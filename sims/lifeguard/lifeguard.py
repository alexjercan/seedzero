#!/usr/bin/env python3
"""Lifeguard path: straight to the swimmer, or run farther first?

A straight waterline, sand on one side and water on the other. The
lifeguard chair is d = 20 m up the beach from the waterline; the swimmer
is a = 40 m along the shore and b = 20 m out in the water. The lifeguard
runs at vr = 5 m/s on sand and swims at vs = 1.25 m/s in water, both
constant (no acceleration). Two rescuers leave the chair at the same
instant. One takes the straight line to the swimmer, which crosses the
waterline at x = a d / (d + b) = 20 m along. The other takes the
least-time path: enter the water at the x that minimises
T(x) = sqrt(d^2 + x^2) / vr + sqrt(b^2 + (a - x)^2) / vs, found by a
golden-section search on [0, a] to 1e-9 m and verified against Snell's
law, sin(alpha) / vr = sin(beta) / vs, where alpha and beta are the
angles of the two legs from the shore normal. Both rescuers are points
advanced by exact arc length per frame along their polylines; the
per-frame stepper's water-entry and arrival times are checked against
the closed forms to 1e-9 s. Played in real time, one run per video: both
leave at release_at, the bent path arrives first, the straight line
second, then the picture holds with the payoff card and a short fade
closes the loop. Deterministic, no seed.

Measured and printed: for both paths the entry point, the sand and water
distances and times and the total; the gap; the run-then-swim time
(x = a); T(x) at a table of entry points; the Snell check; the stepper
checks; the schedule in video time; the on-screen text widths.

usage: lifeguard.py [--measure-only] [--frames t1,t2,...]
"""

from __future__ import annotations

import json
import math
import multiprocessing
import os
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent.parent
W, H = 1080, 1920

BG = (11, 14, 18)
TEAL = (92, 200, 165)
GOLD = (240, 176, 84)
CORAL = (232, 96, 88)
TEXT = (216, 222, 230)
MUTED = (138, 148, 163)
WHITE = (236, 240, 244)
SAND = (66, 52, 32)
WATER = (14, 34, 66)
FOAM = (170, 205, 230)

# Layout: overlay at y 96 (captions.py), title rows at y 190/252 for the
# first seconds, one top-down field from y 350 to 1280 (x 40 to 1040) with
# the waterline at y 815, a two-column readout row from y 1296 to 1436,
# captions at caption_y 0.75 (y 1440..1520), payoff card from y 1592.
GEOM_Y0, GEOM_Y1 = 350, 1436
FIELD_X0, FIELD_X1 = 40, 1040
FIELD_Y0, FIELD_Y1 = 350, 1280
SHORE_Y = 815.0
SS = 2
PAYOFF_Y = 1592.0
COL_X = {"straight": 80, "bent": 580}
PATHS = {"straight": {"colour": TEAL, "label": "straight line"}, "bent": {"colour": GOLD, "label": "bent path"}}


def blend(col, a, base=BG):
    return tuple(int(round(c * a + b * (1 - a))) for c, b in zip(col, base))


def smoothstep(u: float) -> float:
    u = max(0.0, min(1.0, u))
    return u * u * (3 - 2 * u)


# --- closed forms -----------------------------------------------------------
def total_time(man: dict, x: float) -> float:
    d, a, b = man["chair_up_beach_m"], man["swimmer_along_m"], man["swimmer_out_m"]
    return math.hypot(d, x) / man["run_speed_m_s"] + math.hypot(b, a - x) / man["swim_speed_m_s"]


def golden_min(f, lo: float, hi: float, tol: float) -> tuple[float, int]:
    """Golden-section search for the minimum of a unimodal f on [lo, hi]; the bracket shrinks to tol."""
    g = (math.sqrt(5.0) - 1.0) / 2.0
    c, d = hi - g * (hi - lo), lo + g * (hi - lo)
    fc, fd = f(c), f(d)
    n = 0
    while hi - lo > tol:
        n += 1
        if fc < fd:
            hi, d, fd = d, c, fc
            c = hi - g * (hi - lo)
            fc = f(c)
        else:
            lo, c, fc = c, d, fd
            d = lo + g * (hi - lo)
            fd = f(d)
    return (lo + hi) / 2.0, n


def make_path(man: dict, x_entry: float) -> dict:
    """The polyline chair -> entry -> swimmer with its lengths, times and Snell angles."""
    d, a, b = man["chair_up_beach_m"], man["swimmer_along_m"], man["swimmer_out_m"]
    vr, vs = man["run_speed_m_s"], man["swim_speed_m_s"]
    p0, p1, p2 = (0.0, -d), (x_entry, 0.0), (a, b)
    L_sand, L_water = math.hypot(x_entry, d), math.hypot(a - x_entry, b)
    t_sand, t_water = L_sand / vr, L_water / vs
    sin_a, sin_b = x_entry / L_sand, (a - x_entry) / L_water
    return {"x_entry": x_entry, "p0": p0, "p1": p1, "p2": p2, "L_sand": L_sand, "L_water": L_water,
            "L": L_sand + L_water, "t_sand": t_sand, "t_water": t_water, "T": t_sand + t_water,
            "sin_a": sin_a, "sin_b": sin_b, "alpha_deg": math.degrees(math.asin(sin_a)),
            "beta_deg": math.degrees(math.asin(sin_b)), "snell_a": sin_a / vr, "snell_b": sin_b / vs}


def path_state(man: dict, P: dict, t: float) -> dict:
    """Closed-form state of a rescuer on path P at real time t (metres, y up)."""
    vr, vs = man["run_speed_m_s"], man["swim_speed_m_s"]
    p0, p1, p2 = P["p0"], P["p1"], P["p2"]
    if t <= 0.0:
        return {"x": p0[0], "y": p0[1], "s": 0.0, "phase": "sand", "sand_t": 0.0, "water_t": 0.0, "t": t}
    if t < P["t_sand"]:
        s = vr * t
        f = s / P["L_sand"]
        return {"x": p0[0] + f * (p1[0] - p0[0]), "y": p0[1] + f * (p1[1] - p0[1]), "s": s, "phase": "sand",
                "sand_t": t, "water_t": 0.0, "t": t}
    if t < P["T"]:
        sw = vs * (t - P["t_sand"])
        f = sw / P["L_water"]
        return {"x": p1[0] + f * (p2[0] - p1[0]), "y": p1[1] + f * (p2[1] - p1[1]), "s": P["L_sand"] + sw,
                "phase": "water", "sand_t": P["t_sand"], "water_t": t - P["t_sand"], "t": t}
    return {"x": p2[0], "y": p2[1], "s": P["L"], "phase": "arrived", "sand_t": P["t_sand"], "water_t": P["t_water"], "t": t}


# --- per-frame stepper --------------------------------------------------------
def simulate(man: dict, P: dict, n_frames: int) -> dict:
    """Advance the rescuer by exact arc length per frame from release_at; record the crossing times.

    Frame f is real time t_f = f / fps - release_at. Within a frame the sand and water legs are
    advanced at their own speeds, and the frame that crosses the waterline is split at the exact
    crossing time. Returns the per-frame arc length s[f], the entry and arrival times, and the
    largest difference from the closed form over all frames.
    """
    fps, rel = man["fps"], man["release_at"]
    vr, vs = man["run_speed_m_s"], man["swim_speed_m_s"]
    s = np.zeros(n_frames)
    cur = 0.0
    entry_t = arrival_t = None
    max_err = 0.0
    t_prev = -rel
    for f in range(n_frames):
        t_f = f / fps - rel
        t0 = max(t_prev, 0.0)
        dt = max(0.0, t_f - t0)
        while dt > 0.0 and cur < P["L"]:
            if cur < P["L_sand"]:
                room = (P["L_sand"] - cur) / vr
                if dt >= room:
                    cur = P["L_sand"]
                    entry_t = t0 + room
                    t0 += room
                    dt -= room
                else:
                    cur += vr * dt
                    dt = 0.0
            else:
                room = (P["L"] - cur) / vs
                if dt >= room:
                    cur = P["L"]
                    arrival_t = t0 + room
                    dt = 0.0
                else:
                    cur += vs * dt
                    dt = 0.0
        s[f] = cur
        max_err = max(max_err, abs(cur - path_state(man, P, t_f)["s"]))
        t_prev = t_f
    return {"s": s, "entry_t": entry_t, "arrival_t": arrival_t, "max_err": max_err,
            "entry_err": abs(entry_t - P["t_sand"]), "arrival_err": abs(arrival_t - P["T"])}


def pos_at_s(P: dict, s: float) -> tuple[float, float]:
    p0, p1, p2 = P["p0"], P["p1"], P["p2"]
    if s <= P["L_sand"]:
        f = s / P["L_sand"]
        return p0[0] + f * (p1[0] - p0[0]), p0[1] + f * (p1[1] - p0[1])
    f = min(1.0, (s - P["L_sand"]) / P["L_water"])
    return p1[0] + f * (p2[0] - p1[0]), p1[1] + f * (p2[1] - p1[1])


# --- measurement --------------------------------------------------------------
def measure(man: dict) -> dict:
    d, a, b = man["chair_up_beach_m"], man["swimmer_along_m"], man["swimmer_out_m"]
    vr, vs = man["run_speed_m_s"], man["swim_speed_m_s"]
    fps, rel = man["fps"], man["release_at"]
    ppm = man["px_per_m"]
    n_frames = int(round(man["scene_duration"] * fps))
    print(f"setup: a straight waterline, sand on one side and water on the other; the lifeguard chair is {d:g} m up "
          f"the beach from the waterline and the swimmer {a:g} m along the shore and {b:g} m out in the water; running "
          f"speed {vr:g} m/s on sand, swimming speed {vs:g} m/s in water ({vr / vs:g} x slower), both constant; two "
          f"rescuers leave the chair at the same instant, one on the straight line and one on the least-time path; "
          f"points advanced by exact arc length per frame at {fps} fps; drawn at {ppm:g} px per metre ({a * ppm:.0f} "
          f"px along the shore, {(d + b) * ppm:.0f} px across); played in real time; deterministic, no seed")
    # The straight line crosses the waterline at x = a d / (d + b).
    x_str = a * d / (d + b)
    S = make_path(man, x_str)
    print(f"straight line (chair to swimmer, crosses the waterline at x = a d / (d + b) = {x_str:.4f} m along): "
          f"{S['L_sand']:.4f} m of sand in {S['t_sand']:.4f} s plus {S['L_water']:.4f} m of water in {S['t_water']:.4f} "
          f"s = {S['T']:.4f} s over {S['L']:.4f} m; angles from the shore normal {S['alpha_deg']:.2f} deg on sand and "
          f"{S['beta_deg']:.2f} deg in water; sin(alpha)/vr = {S['snell_a']:.5f}, sin(beta)/vs = {S['snell_b']:.5f} "
          f"(not equal, so not the least-time path)")
    # The least-time path by golden-section search.
    x_opt, n_iter = golden_min(lambda x: total_time(man, x), 0.0, a, man["search_tol_m"])
    B = make_path(man, x_opt)
    dT = x_opt / (vr * B["L_sand"]) - (a - x_opt) / (vs * B["L_water"])
    print(f"least-time path (golden-section search on [0, {a:g}] m, {n_iter} iterations, bracket {man['search_tol_m']:g} "
          f"m): enter the water at x* = {x_opt:.4f} m along ({a - x_opt:.4f} m short of the swimmer); "
          f"{B['L_sand']:.4f} m of sand in {B['t_sand']:.4f} s plus {B['L_water']:.4f} m of water in {B['t_water']:.4f} s "
          f"= {B['T']:.4f} s over {B['L']:.4f} m ({B['L'] - S['L']:.4f} m longer than the straight line); dT/dx at x* "
          f"= {dT:.2e} s/m; Snell check: sin(alpha)/vr = {B['snell_a']:.5f}, sin(beta)/vs = {B['snell_b']:.5f}, "
          f"difference {abs(B['snell_a'] - B['snell_b']):.2e}; alpha = {B['alpha_deg']:.2f} deg, beta = "
          f"{B['beta_deg']:.2f} deg; sin(alpha)/sin(beta) = {B['sin_a'] / B['sin_b']:.4f} = vr/vs = {vr / vs:g}")
    gap = S["T"] - B["T"]
    print(f"gap: the bent path wins by {gap:.4f} s ({gap / S['T'] * 100:.2f} percent of the straight time); the bent "
          f"rescuer spends {S['t_sand'] - B['t_sand']:+.4f} s on sand and {S['t_water'] - B['t_water']:+.4f} s in water "
          f"relative to the straight line, i.e. {B['t_sand'] - S['t_sand']:.4f} s more running buys "
          f"{S['t_water'] - B['t_water']:.4f} s less swimming")
    R = make_path(man, a)
    print(f"run-then-swim (x = {a:g} m, run along the beach to level with the swimmer, then swim straight out): "
          f"{R['L_sand']:.4f} m of sand in {R['t_sand']:.4f} s plus {R['L_water']:.4f} m of water in {R['t_water']:.4f} "
          f"s = {R['T']:.4f} s ({R['T'] - B['T']:.4f} s slower than the least-time path)")
    print("table T(x) at entry x along the shore: " + "; ".join(
        f"x = {x:g} m: {total_time(man, x):.3f} s (sand {math.hypot(d, x):.2f} m, water {math.hypot(b, a - x):.2f} m)"
        for x in man["table_x_m"]))
    # Per-frame stepper checks.
    sims = {}
    for name, P in (("straight", S), ("bent", B)):
        sims[name] = simulate(man, P, n_frames)
        r = sims[name]
        print(f"stepper check, {name} ({n_frames} frames at {fps} fps, exact arc length per frame from release_at "
              f"{rel:g} s): enters the water at {r['entry_t']:.9f} s (closed form {P['t_sand']:.9f}, diff "
              f"{r['entry_err']:.1e}), arrives at {r['arrival_t']:.9f} s (closed form {P['T']:.9f}, diff "
              f"{r['arrival_err']:.1e}), max |s - closed form| over all frames {r['max_err']:.1e} m")
        assert r["entry_err"] < 1e-9 and r["arrival_err"] < 1e-9 and r["max_err"] < 1e-9
    # Schedule in video time.
    hold_end = man["scene_duration"] - man["loop_fade"]
    print(f"schedule (real time, one run, release at {rel:g} s): straight rescuer enters the water at "
          f"{rel + S['t_sand']:.2f} s, bent rescuer enters the water at {rel + B['t_sand']:.2f} s, bent rescuer arrives "
          f"at {rel + B['T']:.2f} s, straight rescuer arrives at {rel + S['T']:.2f} s, hold to {hold_end:.2f} s, loop "
          f"fade {hold_end:.2f} to {man['scene_duration']:.2f} s; title until {man['title_until']:g} s; payoff card "
          f"from {man['payoff_t']:g} s")
    ev = {"S": S, "B": B, "R": R, "x_opt": x_opt, "gap": gap, "sims": sims}
    # Text widths.
    font = os.environ["SEED_ZERO_FONT"]
    f24, f26, f28, f32, f34, f40, f56, f64 = (ImageFont.truetype(font, n) for n in (24, 26, 28, 32, 34, 40, 56, 64))
    widths = {"overlay@34": (f34, man["overlay"])}
    for j, line in enumerate(man["title"].split("|")):
        widths[f"title line {j + 1}@56"] = (f56, line)
    for name in PATHS:
        widths[f"label {name}@32"] = (f32, PATHS[name]["label"])
    widths["clock@64"] = (f64, "t 28.3 s")
    widths["frozen clock@64"] = (f64, f"{S['T']:.1f} s")
    widths["arrived tag@32"] = (f32, "arrived")
    widths["sub straight@28"] = (f28, sub_text(S, path_state(man, S, S["T"])))
    widths["sub bent@28"] = (f28, sub_text(B, path_state(man, B, B["T"])))
    widths["entry straight@28"] = (f28, entry_label(S))
    widths["entry bent@28"] = (f28, entry_label(B))
    widths["swimmer@28"] = (f28, "swimmer")
    widths["chair@26"] = (f26, "chair")
    widths["water@28"] = (f28, "water")
    widths["sand@28"] = (f28, "sand")
    widths["scale@24"] = (f24, "10 m")
    for j, line in enumerate(payoff_lines(man, ev)):
        widths[f"payoff line {j + 1}@40"] = (f40, line)
    print("text widths: " + ", ".join(f"{k} {f.getlength(s):.0f} px" for k, (f, s) in widths.items()))
    return ev


def sub_text(P: dict, st: dict) -> str:
    if st["phase"] == "sand":
        return f"sand {st['sand_t']:.1f} s"
    return f"sand {st['sand_t']:.1f} s / water {st['water_t']:.1f} s"


def entry_label(P: dict) -> str:
    x = P["x_entry"]
    return f"{x:.0f} m" if abs(x - round(x)) < 1e-6 else f"{x:.1f} m"


def payoff_lines(man: dict, ev: dict) -> list[str]:
    text = man["payoff_text"].format(t_bent=ev["B"]["T"], t_straight=ev["S"]["T"])
    return [s.strip() for s in text.split("|")]


# --- rendering ---------------------------------------------------------------
class Renderer:
    def __init__(self, man: dict, ev: dict):
        self.man, self.ev = man, ev
        self.fps = man["fps"]
        font = os.environ["SEED_ZERO_FONT"]
        self.font = ImageFont.truetype(font, 40)
        self.font_title = ImageFont.truetype(font, 56)
        self.font_small = ImageFont.truetype(font, 28)
        self.font_chair = ImageFont.truetype(font, 26)
        self.font_label = ImageFont.truetype(font, 32)
        self.font_num = ImageFont.truetype(font, 64)
        self.font_scale = ImageFont.truetype(font, 24)
        self.ppm = float(man["px_per_m"])
        self.dot_r = float(man["dot_radius_px"])
        self.origin_x = W / 2.0 - man["swimmer_along_m"] / 2.0 * self.ppm
        self.first = None
        self.paths = {"straight": ev["S"], "bent": ev["B"]}
        self.winner = "bent" if ev["B"]["T"] < ev["S"]["T"] else "straight"

    # --- geometry helpers -------------------------------------------------
    def px(self, x: float, y: float) -> tuple[float, float]:
        """Frame pixel of a point in metres (x along the shore, y out to sea)."""
        return self.origin_x + x * self.ppm, SHORE_Y - y * self.ppm

    def L(self, x: float, y: float) -> tuple[float, float]:
        """Layer coordinates (supersampled, y relative to GEOM_Y0) of a point in metres."""
        X, Y = self.px(x, y)
        return X * SS, (Y - GEOM_Y0) * SS

    def real_time(self, t: float) -> float:
        return t - self.man["release_at"]

    def state(self, name: str, f: int) -> dict:
        """Rescuer state at video frame f from the per-frame stepper (position by arc length)."""
        P = self.paths[name]
        tr = self.real_time(f / self.fps)
        s = float(self.ev["sims"][name]["s"][min(max(f, 0), len(self.ev["sims"][name]["s"]) - 1)])
        st = path_state(self.man, P, tr)
        x, y = pos_at_s(P, s)
        st.update({"x": x, "y": y, "s": s})
        return st

    # --- drawing ----------------------------------------------------------
    @staticmethod
    def dashed_polyline(d: ImageDraw.ImageDraw, pts, fill, width: int, dash: float, gap: float) -> None:
        phase = 0.0
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            seg = math.hypot(x1 - x0, y1 - y0)
            if seg < 1e-9:
                continue
            ux, uy = (x1 - x0) / seg, (y1 - y0) / seg
            pos = 0.0
            while pos < seg:
                on = phase < dash
                run = (dash - phase) if on else (dash + gap - phase)
                run = min(run, seg - pos)
                if on:
                    d.line((x0 + ux * pos, y0 + uy * pos, x0 + ux * (pos + run), y0 + uy * (pos + run)), fill=fill, width=width)
                pos += run
                phase = (phase + run) % (dash + gap)

    def draw_field(self, d: ImageDraw.ImageDraw) -> None:
        """Water, sand, the waterline, a few ripple marks, the scale bar."""
        x0, x1 = FIELD_X0 * SS, FIELD_X1 * SS
        y0, ys, y1 = (FIELD_Y0 - GEOM_Y0) * SS, (SHORE_Y - GEOM_Y0) * SS, (FIELD_Y1 - GEOM_Y0) * SS
        d.rectangle((x0, y0, x1, ys), fill=WATER)
        d.rectangle((x0, ys, x1, y1), fill=SAND)
        # Ripples: short dashes on fixed rows, offset row by row (deterministic).
        rip = blend(FOAM, 0.16, WATER)
        for k, ym in enumerate((3.0, 7.0, 11.0, 15.0, 19.0)):
            yy = (SHORE_Y - ym * self.ppm - GEOM_Y0) * SS
            off = (k * 37) % 90
            xx = x0 + 30 * SS + off * SS
            while xx < x1 - 30 * SS:
                d.line((xx, yy, xx + 26 * SS, yy), fill=rip, width=2 * SS)
                xx += 90 * SS
        # The waterline: a foam line and a fainter wet-sand line.
        d.line((x0, ys, x1, ys), fill=FOAM, width=3 * SS)
        d.line((x0, ys + 7 * SS, x1, ys + 7 * SS), fill=blend(FOAM, 0.25, SAND), width=2 * SS)
        # Distance ticks every 10 m along the shore.
        a = self.man["swimmer_along_m"]
        for xm in range(0, int(a) + 1, 10):
            X, _ = self.L(float(xm), 0.0)
            d.line((X, ys - 6 * SS, X, ys + 6 * SS), fill=blend(FOAM, 0.7, WATER), width=2 * SS)
        # Scale bar in the water, top left.
        bx, by = (FIELD_X0 + 30) * SS, (FIELD_Y0 + 70 - GEOM_Y0) * SS
        d.line((bx, by, bx + 10 * self.ppm * SS, by), fill=blend(FOAM, 0.8, WATER), width=2 * SS)
        for xx in (bx, bx + 10 * self.ppm * SS):
            d.line((xx, by - 5 * SS, xx, by + 5 * SS), fill=blend(FOAM, 0.8, WATER), width=2 * SS)

    def draw_geometry(self, d: ImageDraw.ImageDraw, states: dict, t: float) -> None:
        man = self.man
        # Full routes, thin and dashed, then the covered part solid.
        for name in PATHS:
            P, col = self.paths[name], PATHS[name]["colour"]
            pts = [self.L(*P["p0"]), self.L(*P["p1"]), self.L(*P["p2"])]
            self.dashed_polyline(d, pts, blend(col, 0.6), 2 * SS, 9 * SS, 8 * SS)
        for name in PATHS:
            P, col, st = self.paths[name], PATHS[name]["colour"], states[name]
            if st["s"] > 0.0:
                pts = [self.L(*P["p0"])]
                if st["s"] >= P["L_sand"]:
                    pts.append(self.L(*P["p1"]))
                pts.append(self.L(st["x"], st["y"]))
                d.line(pts, fill=col, width=4 * SS, joint="curve")
        # Entry ticks on the waterline.
        for name in PATHS:
            P, col = self.paths[name], PATHS[name]["colour"]
            X, Y = self.L(*P["p1"])
            d.line((X, Y - 12 * SS, X, Y + 12 * SS), fill=col, width=3 * SS)
        # The chair and the swimmer.
        cx, cy = self.L(*self.paths["straight"]["p0"])
        r = 12 * SS
        d.rectangle((cx - r, cy - r, cx + r, cy + r), outline=WHITE, width=2 * SS)
        d.rectangle((cx - r * 0.45, cy - r * 0.45, cx + r * 0.45, cy + r * 0.45), fill=WHITE)
        # The swimmer: a dot inside a ring wide enough to stay visible round the arrived rescuers.
        sx, sy = self.L(*self.paths["straight"]["p2"])
        rs = 24 * SS
        d.ellipse((sx - rs, sy - rs, sx + rs, sy + rs), outline=CORAL, width=2 * SS)
        rs = 8 * SS
        d.ellipse((sx - rs, sy - rs, sx + rs, sy + rs), fill=CORAL)
        # Arrival flash: an expanding ring for 0.6 s after each arrival.
        for name in PATHS:
            P, col, st = self.paths[name], PATHS[name]["colour"], states[name]
            dt = st["t"] - P["T"]
            if 0.0 <= dt < 0.6:
                u = dt / 0.6
                rr = (16 + 34 * u) * SS
                d.ellipse((sx - rr, sy - rr, sx + rr, sy + rr), outline=blend(col, 1.0 - u), width=3 * SS)
        # The rescuers: a dot with a ring; the straight first, with the wider ring, so both rings
        # show when the two coincide at the chair and at the swimmer.
        for name, ring in (("straight", 11), ("bent", 6)):
            col, st = PATHS[name]["colour"], states[name]
            X, Y = self.L(st["x"], st["y"])
            rr = (self.dot_r + ring) * SS
            d.ellipse((X - rr, Y - rr, X + rr, Y + rr), outline=col, width=2 * SS)
            rr = self.dot_r * SS
            d.ellipse((X - rr, Y - rr, X + rr, Y + rr), fill=col, outline=BG, width=SS)
            rr = self.dot_r * 0.3 * SS
            d.ellipse((X - rr, Y - rr, X + rr, Y + rr), fill=WHITE)

    def draw_text(self, d: ImageDraw.ImageDraw, states: dict) -> None:
        man = self.man
        # Field labels.
        d.text((FIELD_X0 + 30, FIELD_Y0 + 36), "water", font=self.font_small, fill=blend(FOAM, 0.85, WATER), anchor="lm")
        d.text((FIELD_X0 + 30 + 10 * self.ppm + 12, FIELD_Y0 + 70), "10 m", font=self.font_scale,
               fill=blend(FOAM, 0.8, WATER), anchor="lm")
        d.text((FIELD_X1 - 30, FIELD_Y1 - 28), "sand", font=self.font_small, fill=blend(FOAM, 0.7, SAND), anchor="rm")
        cx, cy = self.px(*self.paths["straight"]["p0"])
        d.text((cx, cy + 31), "chair", font=self.font_chair, fill=blend(WHITE, 0.85, SAND), anchor="mm")
        sx, sy = self.px(*self.paths["straight"]["p2"])
        d.text((sx - 34, sy), "swimmer", font=self.font_small, fill=CORAL, anchor="rm")
        for name in PATHS:
            P, col = self.paths[name], PATHS[name]["colour"]
            X, Y = self.px(*P["p1"])
            d.text((X + 9, Y + 27), entry_label(P), font=self.font_small, fill=col, anchor="lm")
        # Readout row: label, clock, sand / water split.
        for name in PATHS:
            P, col, st, x = self.paths[name], PATHS[name]["colour"], states[name], COL_X[name]
            d.text((x, 1308), PATHS[name]["label"], font=self.font_label, fill=col, anchor="lm")
            if st["phase"] == "arrived":
                cc = GOLD if name == self.winner else TEXT
                txt = f"{P['T']:.1f} s"
                d.text((x, 1362), txt, font=self.font_num, fill=cc, anchor="lm")
                d.text((x + self.font_num.getlength(txt) + 18, 1368), "arrived", font=self.font_label,
                       fill=cc if name == self.winner else MUTED, anchor="lm")
            else:
                d.text((x, 1362), f"t {max(0.0, st['t']):.1f} s", font=self.font_num, fill=TEXT, anchor="lm")
            d.text((x, 1418), sub_text(P, st), font=self.font_small, fill=MUTED, anchor="lm")

    def draw_state(self, f: int) -> Image.Image:
        """The full frame for video frame f, without title or card."""
        img = Image.new("RGB", (W, H), BG)
        layer = Image.new("RGB", (W * SS, (GEOM_Y1 - GEOM_Y0) * SS), BG)
        ld = ImageDraw.Draw(layer)
        states = {name: self.state(name, f) for name in PATHS}
        self.draw_field(ld)
        self.draw_geometry(ld, states, f / self.fps)
        img.paste(layer.reduce(SS), (0, GEOM_Y0))
        d = ImageDraw.Draw(img)
        self.draw_text(d, states)
        return img

    def live_frame(self, f: int) -> np.ndarray:
        man = self.man
        t = f / self.fps
        img = self.draw_state(f)
        d = ImageDraw.Draw(img)
        if t < man["title_until"]:
            a = 1.0 if t < man["title_until"] - 0.4 else (man["title_until"] - t) / 0.4
            for j, line in enumerate(man["title"].split("|")):
                d.text((W / 2, 190 + j * 62), line, font=self.font_title, fill=blend(TEXT, a), anchor="mm")
        if t >= man["payoff_t"]:
            a = min(1.0, (t - man["payoff_t"]) / man["payoff_hold"])
            for j, line in enumerate(payoff_lines(man, self.ev)):
                d.text((W / 2, PAYOFF_Y + j * 56), line, font=self.font, fill=blend(GOLD, a), anchor="mm")
        return np.asarray(img, dtype=np.float32)

    def frame_at(self, f: int) -> np.ndarray:
        man = self.man
        total = int(round(man["scene_duration"] * self.fps))
        live = self.live_frame(f)
        fade_frames = int(round(man["loop_fade"] * self.fps))
        if f >= total - fade_frames:
            if self.first is None:
                self.first = self.live_frame(0)
            a = (f - (total - fade_frames) + 1) / fade_frames
            live = live * (1 - a) + self.first * a
        return live.astype(np.uint8)

    def render(self, out_path: Path) -> None:
        global _RENDERER
        out_path.parent.mkdir(parents=True, exist_ok=True)
        total = int(round(self.man["scene_duration"] * self.fps))
        first = self.frame_at(0)
        last = self.frame_at(total - 1)
        diff = np.abs(first.astype(int) - last.astype(int))
        print(f"loop check: last frame differs from the first in {int((diff.max(axis=2) > 24).sum())} px "
              f"(max channel difference {int(diff.max())})")
        proc = subprocess.Popen(
            ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
             "-s", f"{W}x{H}", "-r", str(self.fps), "-i", "-",
             "-c:v", "libx264", "-crf", "16", "-preset", "medium",
             "-pix_fmt", "yuv420p", str(out_path)],
            stdin=subprocess.PIPE,
        )
        assert proc.stdin is not None
        _RENDERER = self
        workers = min(8, os.cpu_count() or 1)
        with ProcessPoolExecutor(max_workers=workers, mp_context=multiprocessing.get_context("fork")) as pool:
            for f, frame in enumerate(pool.map(_frame_bytes, range(total), chunksize=8)):
                proc.stdin.write(frame)
                if f % 300 == 0:
                    print(f"frame {f}/{total}", file=sys.stderr)
        proc.stdin.close()
        if proc.wait() != 0:
            raise RuntimeError("ffmpeg failed")
        print(f"footage: {out_path} ({total / self.fps:.2f}s at {self.fps} fps)")


_RENDERER: Renderer | None = None


def _frame_bytes(f: int) -> bytes:
    assert _RENDERER is not None
    return _RENDERER.frame_at(f).tobytes()


def main() -> None:
    man = json.loads((ROOT / "projects/lifeguard/manifest.json").read_text())
    ev = measure(man)
    if "--measure-only" in sys.argv:
        return
    if "--frames" in sys.argv:
        times = [float(v) for v in sys.argv[sys.argv.index("--frames") + 1].split(",")]
        r = Renderer(man, ev)
        (ROOT / "media/lifeguard").mkdir(parents=True, exist_ok=True)
        for tv in times:
            Image.fromarray(r.frame_at(int(round(tv * man["fps"])))).save(ROOT / f"media/lifeguard/smoke-{tv}.png")
        print("smoke frames: " + ", ".join(f"{tv}" for tv in times))
        return
    Renderer(man, ev).render(ROOT / "media/lifeguard/footage.mp4")


if __name__ == "__main__":
    main()
