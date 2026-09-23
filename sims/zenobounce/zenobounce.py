#!/usr/bin/env python3
"""Zeno bounce: how many bounces before it stops?

A ball is dropped from h0 = 1 m onto a hard floor with no air, once with a
coefficient of restitution e = 0.8 (each bounce keeps 80 percent of the
speed, 64 percent of the height) and once with e = 0.9 (90 percent of the
speed, 81 percent of the height), in two panels side by side, released at
the same instant and drawn at the same scale. Event-driven flights with
closed forms: the drop takes t0 = sqrt(2 h0 / g) and lands at
v0 = sqrt(2 g h0); bounce n leaves the floor at e^n v0, rises to h0 e^(2n)
and flies for 2 t0 e^n; impact n is at t0 + 2 t0 e (1 - e^(n-1)) / (1 - e).
The flight times form a geometric series, so the bounces converge to the
stop time T = t0 (1 + e) / (1 - e) and the path length to
h0 (1 + e^2) / (1 - e^2). The sim counts bounces down to a stated floor
(the first bounce whose height is under count_floor_m, 1 micrometre) and
prints that index, the count of bounces above 1 mm, the index of the first
bounce under 1 mm, the closed-form stop time, the time of the floor bounce,
the path length, and an RK4 free-flight check of the first flights at
steps_per_second with floor-crossing interpolation. The ball is a point for
every number and is drawn larger than life. Played at 1/slow_factor speed,
one run, with a bounce counter and a clock in real seconds per panel; the
counter freezes at the floor bounce, the clock at the stop time; then the
picture holds with the payoff card and a short fade closes the loop.
Deterministic, no seed.

Measured and printed: for both panels the drop time and impact speed, every
bounce down to the floor (launch speed, height, flight time, impact time),
the count above 1 mm, the first bounce under 1 mm, the first bounce under
the floor and its time, the closed-form stop time and path length beside
the partial sums, the RK4 check, the schedule in video time, the on-screen
text widths.

usage: zenobounce.py [--measure-only] [--frames t1,t2,...]
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
WIRE = (104, 116, 132)
WHITE = (236, 240, 244)
SEP = (34, 40, 48)
GROUND = (26, 31, 39)

# Layout: overlay at y 96 (captions.py), title rows at y 190/252 for the
# first seconds, two panels side by side from y 350 to 1436 (x 40..530 and
# 550..1040): the panel label rows at y 380/420, the floor at y 1190 with the
# 1 m release 700 px above it, a height scale at the panel's left edge, the
# ball 285 px in from the panel's left edge, the readouts (bounce counter,
# clock) from y 1240 to 1420, captions at caption_y 0.75 (y 1440..1520),
# the payoff card under them from y 1592.
GEOM_Y0, GEOM_Y1 = 350, 1436
FLOOR_Y = 1190.0
SLAB_PX = 32
SS = 2
PAYOFF_Y = 1592.0
PANELS = {
    "left": {"index": 0, "colour": CORAL, "x0": 40, "x1": 530},
    "right": {"index": 1, "colour": TEAL, "x0": 550, "x1": 1040},
}
BALL_DX = 285.0
SCALE_DX = 70.0
LABEL_Y, SUBLABEL_Y = 380, 420


def blend(col, a, base=BG):
    return tuple(int(round(c * a + b * (1 - a))) for c, b in zip(col, base))


def smoothstep(u: float) -> float:
    u = max(0.0, min(1.0, u))
    return u * u * (3 - 2 * u)


# --- closed forms and the event-driven flights ---------------------------------
def flights(man: dict, e: float) -> list[dict]:
    """The drop and every bounce down to the count floor as exact free-flight segments.

    Segment 0 is the drop from h0 at rest; segment n >= 1 is bounce n, leaving the floor
    at impact n with speed e^n v0. The list ends with the first bounce whose height is
    under count_floor_m (the floor bounce).
    """
    g, h0, floor = float(man["g_m_s2"]), float(man["drop_height_m"]), float(man["count_floor_m"])
    v0, t0 = math.sqrt(2.0 * g * h0), math.sqrt(2.0 * h0 / g)
    segs = [{"n": 0, "t0": 0.0, "y0": h0, "v0": 0.0, "dur": t0, "t1": t0, "apex": h0, "t_apex": 0.0, "v_land": v0}]
    t, n = t0, 0
    while True:
        n += 1
        v = v0 * e ** n
        apex = h0 * e ** (2 * n)
        dur = 2.0 * t0 * e ** n
        segs.append({"n": n, "t0": t, "y0": 0.0, "v0": v, "dur": dur, "t1": t + dur, "apex": apex,
                     "t_apex": t + 0.5 * dur, "v_land": v})
        t += dur
        if apex < floor:
            return segs


def impact_time_closed(t0: float, e: float, n: int) -> float:
    """Closed-form time of impact n: t0 + 2 t0 e (1 - e^(n-1)) / (1 - e)."""
    return t0 * (1.0 + 2.0 * e * (1.0 - e ** (n - 1)) / (1.0 - e))


def stop_time(t0: float, e: float) -> float:
    return t0 * (1.0 + e) / (1.0 - e)


def path_length(h0: float, e: float) -> float:
    return h0 * (1.0 + e * e) / (1.0 - e * e)


def state_at(man: dict, P: dict, t: float) -> dict:
    """The ball at real time t: height of its bottom, velocity, bounce count, flags."""
    g, h0 = float(man["g_m_s2"]), float(man["drop_height_m"])
    segs = P["segs"]
    if t <= 0.0:
        return {"t": 0.0, "y": h0, "v": 0.0, "n": 0, "frozen": False, "stopped": False}
    stopped = t >= P["T"]
    if t >= P["t_floor"]:
        return {"t": min(t, P["T"]), "y": 0.0, "v": 0.0, "n": P["n_floor"], "frozen": True, "stopped": stopped}
    seg = segs[-1]
    for s in segs:
        if t < s["t1"]:
            seg = s
            break
    dt = t - seg["t0"]
    y = seg["y0"] + seg["v0"] * dt - 0.5 * g * dt * dt
    return {"t": t, "y": max(0.0, y), "v": seg["v0"] - g * dt, "n": seg["n"], "frozen": False, "stopped": stopped}


# --- RK4 check ---------------------------------------------------------------
def check_rk4(man: dict, e: float, segs: list[dict]) -> dict:
    """RK4 free flight (y'' = -g) at steps_per_second with floor-crossing interpolation and v -> -e v."""
    g, steps, nfl = float(man["g_m_s2"]), int(man["steps_per_second"]), int(man["rk4_flights"])
    h0 = float(man["drop_height_m"])
    dt = 1.0 / steps

    def step(y, v):
        # RK4 on (y, v) with a = -g; exact for a quadratic, so the only error is the crossing interpolation.
        k1 = (v, -g)
        k2 = (v + 0.5 * dt * k1[1], -g)
        k3 = (v + 0.5 * dt * k2[1], -g)
        k4 = (v + dt * k3[1], -g)
        return (y + dt / 6.0 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0]),
                v + dt / 6.0 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1]))

    y, v, t = h0, 0.0, 0.0
    landings = []
    n_steps = 0
    apex = h0
    apexes = []
    while len(landings) < nfl:
        y2, v2 = step(y, v)
        n_steps += 1
        if y > 0.0 >= y2:
            f = y / (y - y2)
            tc = t + f * dt
            vc = v + f * (v2 - v)
            landings.append({"t": tc, "v": -vc})
            y, v, t = 0.0, -e * vc, tc
            apexes.append(apex)
            apex = 0.0
        else:
            y, v, t = y2, v2, t + dt
            apex = max(apex, y)
    out = {"steps": n_steps, "landings": landings,
           "max_t_err": max(abs(a["t"] - s["t1"]) for a, s in zip(landings, segs)),
           "max_v_err": max(abs(a["v"] - s["v_land"]) for a, s in zip(landings, segs)),
           "max_apex_err": max(abs(a - s["apex"]) for a, s in zip(apexes, segs))}
    return out


# --- measurement --------------------------------------------------------------
def measure(man: dict) -> dict:
    g, h0 = float(man["g_m_s2"]), float(man["drop_height_m"])
    floor, mm = float(man["count_floor_m"]), float(man["mm_floor_m"])
    steps, slow, fps, ppm = int(man["steps_per_second"]), float(man["slow_factor"]), man["fps"], float(man["px_per_m"])
    rel, nfl = float(man["release_at"]), int(man["rk4_flights"])
    v0, t0 = math.sqrt(2.0 * g * h0), math.sqrt(2.0 * h0 / g)
    es = {name: float(man["restitution"][name]) for name in PANELS}
    print(f"setup: a ball dropped from h0 = {h0:g} m onto a hard floor with no air, g = {g:g} m/s^2, once with "
          f"restitution e = {es['left']:g} (left panel: each bounce keeps {es['left'] * 100:.0f} percent of the speed, "
          f"{es['left'] ** 2 * 100:.0f} percent of the height) and once with e = {es['right']:g} (right panel: "
          f"{es['right'] * 100:.0f} percent of the speed, {es['right'] ** 2 * 100:.0f} percent of the height), released "
          f"at the same instant, two panels at the same scale ({ppm:g} px per metre, the drop {h0 * ppm:.0f} px); "
          f"event-driven flights with closed forms (bounce n leaves at e^n v0, rises to h0 e^(2n), flies 2 t0 e^n; "
          f"no time step), counted down to the first bounce under {floor:g} m, checked by an RK4 free flight at "
          f"{steps} steps per second (dt = {1 / steps:.2e} s) with floor-crossing interpolation over the first "
          f"{nfl} flights; the ball is a point for every number; played at 1/{slow:g} speed, one run; "
          f"deterministic, no seed")
    print(f"closed forms: drop time t0 = sqrt(2 h0 / g) = {t0:.6f} s, impact speed v0 = sqrt(2 g h0) = {v0:.4f} m/s; "
          f"bounce n leaves the floor at e^n v0, rises to h0 e^(2n), flies 2 t0 e^n; impact n at "
          f"t0 + 2 t0 e (1 - e^(n-1)) / (1 - e); stop time T = t0 (1 + e) / (1 - e); path h0 (1 + e^2) / (1 - e^2)")
    ev = {"t0": t0, "v0": v0, "panels": {}}
    for name in PANELS:
        e = es[name]
        segs = flights(man, e)
        n_floor = segs[-1]["n"]
        n_mm = next(s["n"] for s in segs if s["n"] >= 1 and s["apex"] < mm)
        T, L = stop_time(t0, e), path_length(h0, e)
        t_floor, t_floor_end = segs[-1]["t0"], segs[-1]["t1"]
        L_floor = h0 + sum(2.0 * s["apex"] for s in segs[1:])
        t_floor_closed = impact_time_closed(t0, e, n_floor)
        t_mm = segs[n_mm]["t0"]
        P = {"e": e, "segs": segs, "n_floor": n_floor, "n_mm": n_mm, "T": T, "L": L, "t_floor": t_floor,
             "t_floor_end": t_floor_end, "L_floor": L_floor, "t_mm": t_mm}
        ev["panels"][name] = P
        print(f"{name} panel (e = {e:g}, keeps {e * 100:.0f} percent of the speed and {e * e * 100:.0f} percent of the "
              f"height per bounce): bounces above {mm * 1000:g} mm: {n_mm - 1} (bounce {n_mm - 1} rises to "
              f"{segs[n_mm - 1]['apex'] * 1000:.4f} mm); first bounce under {mm * 1000:g} mm: bounce {n_mm}, "
              f"{segs[n_mm]['apex'] * 1000:.4f} mm high, {segs[n_mm]['dur'] * 1000:.2f} ms long, leaving the floor at "
              f"{t_mm:.4f} s; first bounce under {floor:g} m (the count floor): bounce {n_floor}, "
              f"{segs[n_floor]['apex']:.3e} m high (bounce {n_floor - 1}: {segs[n_floor - 1]['apex']:.3e} m), "
              f"{segs[n_floor]['dur'] * 1000:.4f} ms long, leaving the floor at {t_floor:.6f} s (closed form "
              f"{t_floor_closed:.6f}, diff {abs(t_floor - t_floor_closed):.1e}) and landing at {t_floor_end:.6f} s; "
              f"closed-form stop time T = t0 (1 + e) / (1 - e) = {T:.6f} s ({t0:.6f} x {(1 + e) / (1 - e):g}), "
              f"{T - t_floor_end:.2e} s after the floor bounce lands; path to the floor bounce {L_floor:.6f} m, "
              f"closed-form path h0 (1 + e^2) / (1 - e^2) = {L:.6f} m (diff {L - L_floor:.1e}); bounce {n_floor + 1} "
              f"would rise to {h0 * e ** (2 * (n_floor + 1)):.2e} m and bounce 100 to {h0 * e ** 200:.2e} m, both "
              f"positive: no bounce height is zero, the counter stops only at the stated floor")
        print(f"{name} bounces (n: leaves at m/s, rises to m, flight s, impact n at s): " + "; ".join(
            f"{s['n']}: {s['v0']:.4f}, {s['apex']:.4e}, {s['dur']:.4e}, {s['t0']:.4f}" for s in segs[1:]))
        chk = check_rk4(man, e, segs)
        print(f"RK4 check, {name} ({chk['steps']} steps over the drop and the first {nfl - 1} bounces): max |landing "
              f"time - event| {chk['max_t_err']:.2e} s, max |landing speed - event| {chk['max_v_err']:.2e} m/s, "
              f"max |apex - h0 e^(2n)| {chk['max_apex_err']:.2e} m (the apex sampled at the step); landings at "
              + ", ".join(f"{a['t']:.6f} s / {a['v']:.4f} m/s" for a in chk["landings"])
              + " against events at " + ", ".join(f"{s['t1']:.6f} s / {s['v_land']:.4f} m/s" for s in segs[:nfl]))
        assert chk["max_t_err"] < 1e-6 and chk["max_v_err"] < 1e-5
    Lp, Rp = ev["panels"]["left"], ev["panels"]["right"]
    print(f"result: the {es['left']:g} ball is under 1 mm from bounce {Lp['n_mm']} and lies at rest at {Lp['T']:.4f} s "
          f"over {Lp['L']:.4f} m of path; the {es['right']:g} ball is under 1 mm from bounce {Rp['n_mm']} and lies at "
          f"rest at {Rp['T']:.4f} s over {Rp['L']:.4f} m; ratio of stop times {Rp['T'] / Lp['T']:.4f}; the counters "
          f"freeze at {Lp['n_floor']} and {Rp['n_floor']} (the first bounces under {floor:g} m)")
    # Schedule in video time.
    hold_end = man["scene_duration"] - man["loop_fade"]
    for name in PANELS:
        P = ev["panels"][name]
        segs = P["segs"]
        marks = [1, 2, 3, 4, 5, 10, P["n_mm"], P["n_floor"]]
        print(f"schedule, {name} (1/{slow:g} speed, release at {rel:g} s): impacts "
              + ", ".join(f"{k} at {rel + slow * segs[k]['t0']:.2f} s" for k in marks)
              + f"; clock frozen at {P['T']:.2f} s from {rel + slow * P['T']:.2f} s; each bounce lasts "
              + ", ".join(f"{slow * segs[k]['dur']:.2f}" for k in (1, 2, 5, 10, P["n_mm"]))
              + f" s of video at bounces 1, 2, 5, 10, {P['n_mm']}")
    print(f"schedule: title until {man['title_until']:g} s; payoff card from {man['payoff_t']:g} s, its last line from "
          f"{man['payoff_t_right']:g} s; hold to {hold_end:.2f} s; loop fade {hold_end:.2f} to {man['scene_duration']:.2f} s")
    # Text widths.
    font = os.environ["SEED_ZERO_FONT"]
    f24, f28, f34, f36, f40, f44, f56, f64 = (ImageFont.truetype(font, n) for n in (24, 28, 34, 36, 40, 44, 56, 64))
    widths = {"overlay@34": (f34, man["overlay"])}
    for j, line in enumerate(man["title"].split("|")):
        widths[f"title line {j + 1}@56"] = (f56, line)
    for name in PANELS:
        widths[f"label {name}@36"] = (f36, label_text(man, name))
        widths[f"sublabel {name}@28"] = (f28, sublabel_text(man, name))
        widths[f"counter {name}@64"] = (f64, str(ev["panels"][name]["n_floor"]))
        widths[f"clock {name}@44"] = (f44, f"t {ev['panels'][name]['T']:.2f} s")
        widths[f"frozen clock {name}@44"] = (f44, f"{ev['panels'][name]['T']:.2f} s")
    widths["counter label@28"] = (f28, "bounces")
    widths["count note@24"] = (f24, count_note(man))
    widths["at rest tag@28"] = (f28, "at rest")
    widths["clock note@24"] = (f24, "real seconds")
    widths["scale 1 m@24"] = (f24, "1 m")
    widths["scale 0.5 m@24"] = (f24, "0.5 m")
    for j, line in enumerate(payoff_lines(man, ev)):
        widths[f"payoff line {j + 1}@40"] = (f40, line)
    print("text widths: " + ", ".join(f"{k} {f.getlength(s):.0f} px" for k, (f, s) in widths.items()))
    panel_w = PANELS["left"]["x1"] - PANELS["left"]["x0"]
    print(f"panel width {panel_w} px; the widest panel text "
          + max((f"{k} {f.getlength(s):.0f} px" for k, (f, s) in widths.items() if "label" in k or "counter" in k
                 or "clock" in k), key=lambda s: float(s.split()[-2])))
    return ev


def label_text(man: dict, name: str) -> str:
    e = float(man["restitution"][name])
    return f"keeps {e * 100:.0f}% of its speed"


def sublabel_text(man: dict, name: str) -> str:
    e = float(man["restitution"][name])
    return f"and {e * e * 100:.0f}% of its height"


def count_note(man: dict) -> str:
    return f"counted to {float(man['count_floor_m']) * 1000:g} mm"


def payoff_lines(man: dict, ev: dict) -> list[str]:
    L, R = ev["panels"]["left"], ev["panels"]["right"]
    text = man["payoff_text"].format(T_left=L["T"], T_right=R["T"], n_left=L["n_floor"], n_right=R["n_floor"],
                                     e_left=L["e"] * 100, e_right=R["e"] * 100)
    return [s.strip() for s in text.split("|")]


# --- rendering ---------------------------------------------------------------
class Renderer:
    def __init__(self, man: dict, ev: dict):
        self.man, self.ev = man, ev
        self.fps = man["fps"]
        font = os.environ["SEED_ZERO_FONT"]
        self.font = ImageFont.truetype(font, 40)
        self.font_title = ImageFont.truetype(font, 56)
        self.font_label = ImageFont.truetype(font, 36)
        self.font_small = ImageFont.truetype(font, 28)
        self.font_clock = ImageFont.truetype(font, 44)
        self.font_num = ImageFont.truetype(font, 64)
        self.font_tiny = ImageFont.truetype(font, 24)
        self.ppm = float(man["px_per_m"])
        self.ball_r = float(man["ball_radius_px"])
        self.slow = float(man["slow_factor"])
        self.first = None

    # --- geometry helpers -------------------------------------------------
    def real_time(self, tau: float) -> float:
        return max(0.0, tau - self.man["release_at"]) / self.slow

    def state(self, name: str, tau: float) -> dict:
        return state_at(self.man, self.ev["panels"][name], self.real_time(tau))

    def ball_x(self, name: str) -> float:
        return PANELS[name]["x0"] + BALL_DX

    def yf(self, y_m: float) -> float:
        """Frame y of a height above the floor in metres."""
        return FLOOR_Y - y_m * self.ppm

    @staticmethod
    def L(x: float, y: float) -> tuple[float, float]:
        """Layer coordinates (supersampled, y relative to GEOM_Y0) of a frame point."""
        return x * SS, (y - GEOM_Y0) * SS

    # --- drawing ----------------------------------------------------------
    def draw_panel_geometry(self, d: ImageDraw.ImageDraw, name: str, st: dict, tau: float) -> None:
        man, P = self.man, self.ev["panels"][name]
        col = PANELS[name]["colour"]
        x0, x1 = float(PANELS[name]["x0"]), float(PANELS[name]["x1"])
        h0 = float(man["drop_height_m"])
        bx = self.ball_x(name)
        # The floor slab and its top line.
        d.rectangle((*self.L(x0, FLOOR_Y), *self.L(x1, FLOOR_Y + SLAB_PX)), fill=GROUND)
        d.line((*self.L(x0, FLOOR_Y), *self.L(x1, FLOOR_Y)), fill=WIRE, width=3 * SS)
        # The height scale: a faint line from the floor to the release height with ticks every 0.25 m.
        sx = x0 + SCALE_DX
        d.line((*self.L(sx, FLOOR_Y), *self.L(sx, self.yf(h0))), fill=blend(MUTED, 0.5), width=SS)
        k = 0
        while k * 0.25 <= h0 + 1e-9:
            yy = self.yf(k * 0.25)
            w = 12.0 if k % 2 == 0 else 7.0
            d.line((*self.L(sx - w, yy), *self.L(sx + w, yy)), fill=blend(MUTED, 0.7), width=SS)
            k += 1
        # Apex marks: a short bar at every bounce height reached so far, beside the ball's path.
        for s in P["segs"][1:]:
            if st["t"] >= s["t_apex"] or st["frozen"]:
                yy = self.yf(s["apex"])
                d.line((*self.L(bx + self.ball_r + 22, yy), *self.L(bx + self.ball_r + 46, yy)),
                       fill=blend(GOLD, 0.55), width=SS)
        # Impact pulses: a ring on the floor for 0.3 s of video after each impact.
        for s in P["segs"][1:]:
            age = (st["t"] - s["t0"]) * self.slow
            if 0.0 <= age < 0.3 and not st["frozen"]:
                u = age / 0.3
                r = (12.0 + 30.0 * u) * SS
                cx, cy = self.L(bx, FLOOR_Y)
                d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=blend(col, 0.9 * (1.0 - u)), width=3 * SS)
        # The ball: its bottom is the point; drawn large.
        cx, cy = self.L(bx, self.yf(st["y"]) - self.ball_r)
        r = self.ball_r * SS
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=GOLD, outline=(120, 84, 30), width=SS)
        hr = r * 0.3
        d.ellipse((cx - r * 0.42 - hr, cy - r * 0.42 - hr, cx - r * 0.42 + hr, cy - r * 0.42 + hr), fill=WHITE)

    def draw_panel_text(self, d: ImageDraw.ImageDraw, name: str, st: dict) -> None:
        man, P = self.man, self.ev["panels"][name]
        col = PANELS[name]["colour"]
        x0, x1 = PANELS[name]["x0"], PANELS[name]["x1"]
        h0 = float(man["drop_height_m"])
        cx = (x0 + x1) / 2.0
        d.text((cx, LABEL_Y), label_text(man, name), font=self.font_label, fill=col, anchor="mm")
        d.text((cx, SUBLABEL_Y), sublabel_text(man, name), font=self.font_small, fill=MUTED, anchor="mm")
        # Scale labels.
        sx = x0 + SCALE_DX
        d.text((sx - 18, self.yf(h0)), f"{h0:g} m", font=self.font_tiny, fill=blend(MUTED, 0.9), anchor="rm")
        d.text((sx - 18, self.yf(h0 / 2)), f"{h0 / 2:g} m", font=self.font_tiny, fill=blend(MUTED, 0.9), anchor="rm")
        # Readouts: the bounce counter, its floor, the clock in real seconds.
        x = x0 + 20
        d.text((x, 1244), "bounces", font=self.font_small, fill=MUTED, anchor="lm")
        num = str(st["n"])
        d.text((x, 1292), num, font=self.font_num, fill=GOLD if st["frozen"] else TEXT, anchor="lm")
        d.text((x + self.font_num.getlength(num) + 16, 1300), count_note(man), font=self.font_tiny,
               fill=blend(GOLD, 0.9) if st["frozen"] else MUTED, anchor="lm")
        if st["stopped"]:
            txt = f"{P['T']:.2f} s"
            d.text((x, 1362), txt, font=self.font_clock, fill=GOLD, anchor="lm")
            d.text((x + self.font_clock.getlength(txt) + 14, 1366), "at rest", font=self.font_small, fill=GOLD, anchor="lm")
        else:
            d.text((x, 1362), f"t {st['t']:.2f} s", font=self.font_clock, fill=TEXT, anchor="lm")
        d.text((x, 1408), "real seconds", font=self.font_tiny, fill=MUTED, anchor="lm")

    def draw_state(self, tau: float) -> Image.Image:
        """The full frame for video time tau, without title or card."""
        img = Image.new("RGB", (W, H), BG)
        layer = Image.new("RGB", (W * SS, (GEOM_Y1 - GEOM_Y0) * SS), BG)
        ld = ImageDraw.Draw(layer)
        sep_x = (PANELS["left"]["x1"] + PANELS["right"]["x0"]) / 2.0 * SS
        ld.line((sep_x, (LABEL_Y - 20 - GEOM_Y0) * SS, sep_x, (GEOM_Y1 - 16 - GEOM_Y0) * SS), fill=SEP, width=2 * SS)
        states = {name: self.state(name, tau) for name in PANELS}
        for name in PANELS:
            self.draw_panel_geometry(ld, name, states[name], tau)
        img.paste(layer.reduce(SS), (0, GEOM_Y0))
        d = ImageDraw.Draw(img)
        for name in PANELS:
            self.draw_panel_text(d, name, states[name])
        return img

    def live_frame(self, f: int) -> np.ndarray:
        man = self.man
        t = f / self.fps
        img = self.draw_state(t)
        d = ImageDraw.Draw(img)
        if t < man["title_until"]:
            a = 1.0 if t < man["title_until"] - 0.4 else (man["title_until"] - t) / 0.4
            for j, line in enumerate(man["title"].split("|")):
                d.text((W / 2, 190 + j * 62), line, font=self.font_title, fill=blend(TEXT, a), anchor="mm")
        lines = payoff_lines(man, self.ev)
        for j, line in enumerate(lines):
            t_on = man["payoff_t_right"] if j == len(lines) - 1 else man["payoff_t"]
            if t >= t_on:
                a = min(1.0, (t - t_on) / man["payoff_hold"])
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
    man = json.loads((ROOT / "projects/zenobounce/manifest.json").read_text())
    ev = measure(man)
    if "--measure-only" in sys.argv:
        return
    if "--frames" in sys.argv:
        times = [float(v) for v in sys.argv[sys.argv.index("--frames") + 1].split(",")]
        r = Renderer(man, ev)
        (ROOT / "media/zenobounce").mkdir(parents=True, exist_ok=True)
        for tv in times:
            Image.fromarray(r.frame_at(int(round(tv * man["fps"])))).save(ROOT / f"media/zenobounce/smoke-{tv}.png")
        print("smoke frames: " + ", ".join(f"{tv}" for tv in times))
        return
    Renderer(man, ev).render(ROOT / "media/zenobounce/footage.mp4")


if __name__ == "__main__":
    main()
