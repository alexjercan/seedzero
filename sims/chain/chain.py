#!/usr/bin/env python3
"""Drop a folded chain beside a ball: which lands first?

A uniform chain of length L hangs folded in half from a peg: one end is
held at the top, the free end starts level with it and the fold hangs
L / 2 below them. At t = 0 the free end is released. With the free end
fallen a distance x the held side is a straight hanging length (L + x)
/ 2 and the free side a straight length (L - x) / 2 rising from the
fold to the free end, so the fold sits (L + x) / 2 below the peg and
moves at half the tip speed. In the energy-conserving model (Calkin
and March 1989, the model that experiments confirm) the free end's
speed obeys v^2 = g x (2L - x) / (L - x); differentiating gives the
tip acceleration a = g (1 + x (2L - x) / (2 (L - x)^2)), which is g at
release and grows without bound as x nears L. The fall time to depth x
is the quadrature t = integral dx / v, evaluated with the endpoint
singularities removed (x = s^2 below 0.9 L, u = sqrt(L - x) above it);
x(t) is integrated by RK4 at steps_per_second to 0.9 L and checked
against the closed form to four decimals. The ball is a point mass
dropped from rest at the same instant from the same start line, no
air, y = g t^2 / 2 (drawn with a radius, measured at its centre). Both
are measured to the same finish line L below the start line. The
drawing is capped: once the free side is shorter than one link (x > L
- link) the chain is drawn fully hung with the tip at L; the model's
tip speed runs away in the last centimetres and a real chain whips.
Shown at 1 / slow_factor speed; the drop repeats at the release times
in the manifest (fall, landed hold, fade out, fade in at the start,
hold, release), the hold after each drop clipped to fit the gap to the
next release, and the last drop's cycle wraps around scene_duration to
the first, so the scene is exactly periodic and the last frame equals
the first. Deterministic, no seed.

Measured and printed: the fall time of the chain tip and of the ball
to L, their ratio and the lead, where the ball is when the tip lands,
the RK4 run against the closed form (speed along the way, the times to
0.5 L and 0.9 L), the tip and ball speeds at the same depths, the tip
acceleration halfway, the times to 0.9 L, 0.99 L and L, the drawing
cap and the tip speed there, the schedule in video time, the loop and
periodicity checks and the on-screen text widths.

usage: chain.py [--measure-only] [--frames t1,t2,...]
"""

from __future__ import annotations

import bisect
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
RIM = (96, 108, 126)

# Layout: overlay at y 96..130 (captions.py), title rows at y 200/262/324
# for the first seconds, then the legend rows at y 236 and 290; the labels
# "chain" and "ball" and the clock at y 405; the start line at start_y
# and the finish line 1 m (px_per_m) below it, the scale bar on the left;
# the geometry band y 380..1420 drawn at 2x; the live readouts at y 1250
# (the tip's from the left end of the lines, the ball's to the right end)
# and the fixed lines at y 1300/1336; captions at caption_y 0.75 (y
# 1440..1520); the payoff card from y 1592.
TITLE_Y0, TITLE_PITCH = 200, 62
LEGEND_Y, TAG_Y = 236, 290
LABEL_Y = 405
GEOM_Y0, GEOM_Y1 = 380, 1420
SS = 2
READ_Y = 1250
FIXED_Y0, FIXED_PITCH = 1300, 36
PAYOFF_Y = 1592.0
READ_X = 1020


def blend(col, a: float, base=BG) -> tuple:
    a = max(0.0, min(1.0, a))
    return tuple(int(round(c * a + b * (1 - a))) for c, b in zip(col, base))


# --- measurement --------------------------------------------------------------
def v_closed(x, L: float, g: float):
    """Tip speed at depth x (Calkin and March): v^2 = g x (2L - x) / (L - x)."""
    return np.sqrt(g * x * (2.0 * L - x) / (L - x))


def a_closed(x: float, L: float, g: float) -> float:
    """Tip acceleration at depth x: a = g (1 + x (2L - x) / (2 (L - x)^2))."""
    return g * (1.0 + x * (2.0 * L - x) / (2.0 * (L - x) ** 2))


def simpson(f, a: float, b: float, n: int) -> float:
    xs = np.linspace(a, b, n + 1)
    ys = f(xs)
    return (b - a) / (3.0 * n) * (ys[0] + ys[-1] + 4.0 * ys[1:-1:2].sum() + 2.0 * ys[2:-1:2].sum())


def t_closed(x: float, L: float, g: float, n: int) -> float:
    """Fall time of the free end to depth x: t = integral dx / v. Below 0.9 L with x = s^2
    (dx / v = 2 sqrt((L - s^2) / (g (2L - s^2))) ds, finite at s = 0); above 0.9 L with
    u = sqrt(L - x) (dx / v = 2 u^2 / sqrt(g (L^2 - u^4)) du, finite at u = 0). Simpson."""
    xa = min(x, 0.9 * L)
    t = simpson(lambda s: 2.0 * np.sqrt((L - s * s) / (g * (2.0 * L - s * s))), 0.0, math.sqrt(xa), n)
    if x > 0.9 * L:
        u0, u1 = math.sqrt(L - 0.9 * L), math.sqrt(max(0.0, L - x))
        t += simpson(lambda u: 2.0 * u * u / np.sqrt(g * (L * L - u ** 4)), u1, u0, n)
    return t


def time_table(L: float, g: float, n: int) -> tuple[np.ndarray, np.ndarray]:
    """Dense (t, x) table of the fall from the same two substitutions by cumulative trapezoid,
    for drawing x(t) by interpolation."""
    s = np.linspace(0.0, math.sqrt(0.9 * L), n + 1)
    f = 2.0 * np.sqrt((L - s * s) / (g * (2.0 * L - s * s)))
    ts = np.concatenate([[0.0], np.cumsum(0.5 * (f[1:] + f[:-1]) * (s[1] - s[0]))])
    u = np.linspace(math.sqrt(0.1 * L), 0.0, n + 1)
    h = 2.0 * u * u / np.sqrt(g * (L * L - u ** 4))
    tu = ts[-1] + np.concatenate([[0.0], np.cumsum(0.5 * (h[1:] + h[:-1]) * (u[0] - u[1]))])
    return np.concatenate([ts, tu[1:]]), np.concatenate([s * s, (L - u * u)[1:]])


def rk4_fall(L: float, g: float, dt: float, x_end: float, marks: list[float]) -> dict:
    """Integrate the tip (x, v) from rest by RK4 at dt until x_end, recording the largest
    difference of v from the closed form along the way and the interpolated crossing times
    of the depths in marks (each ending with x_end itself)."""
    x, v, t = 0.0, 0.0, 0.0
    max_dv, n = 0.0, 0
    cross: dict[float, tuple[float, float]] = {}
    pending = sorted(set(marks + [x_end]))
    while pending:
        k1x, k1v = v, a_closed(x, L, g)
        k2x, k2v = v + 0.5 * dt * k1v, a_closed(x + 0.5 * dt * k1x, L, g)
        k3x, k3v = v + 0.5 * dt * k2v, a_closed(x + 0.5 * dt * k2x, L, g)
        k4x, k4v = v + dt * k3v, a_closed(x + dt * k3x, L, g)
        xn = x + dt / 6.0 * (k1x + 2.0 * k2x + 2.0 * k3x + k4x)
        vn = v + dt / 6.0 * (k1v + 2.0 * k2v + 2.0 * k3v + k4v)
        n += 1
        while pending and xn >= pending[0]:
            f = (pending[0] - x) / (xn - x)
            cross[pending[0]] = (t + f * dt, v + f * (vn - v))
            pending.pop(0)
        x, v, t = xn, vn, t + dt
        if x < x_end:
            max_dv = max(max_dv, abs(v - float(v_closed(x, L, g))))
    return {"cross": cross, "max_dv": max_dv, "steps": n}


def measure(man: dict) -> dict:
    g, L, link, rb = man["g_m_s2"], man["chain_m"], man["link_m"], man["ball_radius_m"]
    D, fps, slow = man["scene_duration"], man["fps"], man["slow_factor"]
    dt = 1.0 / man["steps_per_second"]
    nq = man["quadrature_intervals"]
    rels = list(man["releases"])
    drops = len(rels)
    assert rels == sorted(rels) and 0.0 <= rels[0] and rels[-1] < D, "releases must be sorted inside the scene"
    n_links = int(round(L / link))
    print(f"setup: a uniform chain of {L:.2f} m ({n_links} links of {link * 100:g} cm) folded in half from a peg, one "
          f"end held at the top, the free end level with it and the fold {L / 2:g} m below; a ball (radius "
          f"{rb * 100:g} cm, measured at its centre, a point mass) beside it at the same start line; both let go at "
          f"the same instant and measured to the same finish line {L:.2f} m below the start line; no air; g = "
          f"{g:g} m/s^2; the chain tip follows v^2 = g x (2L - x) / (L - x) (Calkin and March, energy conserving), "
          f"a = g (1 + x (2L - x) / (2 (L - x)^2)), integrated by RK4 at {man['steps_per_second']} steps per "
          f"second (dt = {dt:.0e} s) to 0.9 L and checked against the quadrature t = integral dx / v (Simpson, "
          f"{nq} intervals per piece); the ball y = g t^2 / 2; shown at 1/{slow:g} speed, {drops} drops in {D:g} s; "
          f"drawn at {man['px_per_m']:g} px per metre; deterministic, no seed")
    # Closed-form times.
    t_tip = t_closed(L, L, g, nq)
    t_ball = math.sqrt(2.0 * L / g)
    y_ball_at_tip = 0.5 * g * t_tip * t_tip
    gap = L - y_ball_at_tip
    lead = t_ball - t_tip
    T, X = time_table(L, g, nq)
    print(f"fall times: the chain tip reaches {L:.2f} m in {t_tip:.4f} s and the ball in {t_ball:.4f} s "
          f"(sqrt(2 L / g)); the chain takes {100.0 * t_tip / t_ball:.1f} percent of the ball's time, a "
          f"{1000.0 * lead:.1f} ms lead ({1000.0 * lead:.0f} ms); when the tip lands the ball has fallen "
          f"{y_ball_at_tip:.3f} m and is {gap:.3f} m up ({100.0 * gap:.0f} cm to the nearest centimetre, "
          f"{100.0 * gap:.1f} cm); the trapezoid table used for drawing gives {T[-1]:.6f} s to L "
          f"(diff {abs(T[-1] - t_tip):.1e} s from Simpson)")
    # RK4 against the closed form.
    marks = [0.25 * L, 0.5 * L, 0.75 * L]
    rk = rk4_fall(L, g, dt, 0.9 * L, marks)
    t_half_q, t_09_q = t_closed(0.5 * L, L, g, nq), t_closed(0.9 * L, L, g, nq)
    t_half_rk, v_half_rk = rk["cross"][0.5 * L]
    t_09_rk, v_09_rk = rk["cross"][0.9 * L]
    v_half, v_09 = float(v_closed(0.5 * L, L, g)), float(v_closed(0.9 * L, L, g))
    print(f"RK4 check: {rk['steps']} steps of {dt:.0e} s from rest to 0.9 L; the speed along the way stays within "
          f"{rk['max_dv']:.1e} m/s of the closed form; the tip passes 0.5 L at {t_half_rk:.5f} s at {v_half_rk:.5f} "
          f"m/s (quadrature {t_half_q:.5f} s, closed form {v_half:.5f} m/s; diffs {abs(t_half_rk - t_half_q):.1e} s, "
          f"{abs(v_half_rk - v_half):.1e} m/s) and 0.9 L at {t_09_rk:.5f} s at {v_09_rk:.5f} m/s (quadrature "
          f"{t_09_q:.5f} s, closed form {v_09:.5f} m/s; diffs {abs(t_09_rk - t_09_q):.1e} s, "
          f"{abs(v_09_rk - v_09):.1e} m/s): the RK4 run matches the closed form to four decimals")
    assert rk["max_dv"] < 1e-4 and abs(t_09_rk - t_09_q) < 5e-5 and abs(t_half_rk - t_half_q) < 5e-5
    # The ball by the same RK4 (a = g), a trivial check of the stepping.
    xb, vb, tb, n = 0.0, 0.0, 0.0, 0
    while True:
        xn = xb + vb * dt + 0.5 * g * dt * dt
        vn = vb + g * dt
        n += 1
        if xn >= L:
            f = (L - xb) / (xn - xb)
            tb_rk = tb + f * dt
            break
        xb, vb, tb = xn, vn, tb + dt
    print(f"ball check: stepped at the same dt the ball reaches {L:.2f} m at {tb_rk:.5f} s ({n} steps; closed form "
          f"{t_ball:.5f} s, diff {abs(tb_rk - t_ball):.1e} s) at {g * t_ball:.3f} m/s")
    # Speeds at the same depths, the acceleration halfway, the halfway lead.
    rows = []
    for frac in man["description_depths"]:
        x = frac * L
        rows.append(f"{x:.2f} m: tip {float(v_closed(x, L, g)):.2f} m/s at {t_closed(x, L, g, nq):.4f} s, ball "
                    f"{math.sqrt(2.0 * g * x):.2f} m/s at {math.sqrt(2.0 * x / g):.4f} s")
    a_half = a_closed(0.5 * L, L, g)
    y_ball_half = 0.5 * g * t_half_q * t_half_q
    print(f"speeds at the same depth: " + "; ".join(rows) + f"; the tip acceleration at 0.5 L is {a_half:.3f} m/s^2 = "
          f"{a_half / g:.2f} g (g at release, unbounded as x nears L); halfway: the tip passes 0.5 L at "
          f"{t_half_q:.4f} s, when the ball has fallen {y_ball_half:.3f} m, so the tip is {0.5 * L - y_ball_half:.3f} m "
          f"ahead of the ball ({100.0 * (0.5 * L - y_ball_half):.0f} cm) and moving {v_half:.2f} m/s against the "
          f"ball's {g * t_half_q:.2f} m/s at that instant")
    # The tail and the drawing cap.
    t_099 = t_closed(0.99 * L, L, g, nq)
    x_cap = L - link
    t_cap = t_closed(x_cap, L, g, nq)
    v_cap = float(v_closed(x_cap, L, g))
    print(f"tail: time to 0.9 L {t_09_q:.4f} s, to 0.99 L {t_099:.4f} s, to L {t_tip:.4f} s (the last centimetre "
          f"takes {1000.0 * (t_tip - t_099):.2f} ms; v grows like 1 / sqrt(L - x), so the quadrature converges); "
          f"drawing cap: once x > L - one link = {x_cap:.3f} m the chain is drawn fully hung with the tip at L; the "
          f"cap applies from {t_cap:.4f} s ({t_cap * slow:.3f} s of video after the release, {1000.0 * (t_tip - t_cap):.2f} "
          f"ms real / {1000.0 * (t_tip - t_cap) * slow:.1f} ms video before the tip lands, {(t_tip - t_cap) * slow * fps:.2f} "
          f"frames), where the model's tip speed is {v_cap:.1f} m/s ({v_cap / math.sqrt(2.0 * g * x_cap):.1f} times the "
          f"ball's speed at that depth); the cap changes the drawn fall time by under a millisecond of real time")
    # Schedule in video time: each drop's hold after the ball lands is the manifest hold, clipped so
    # that the landed hold, the fade out, the fade in and at least start_hold_min at the start fit the
    # gap to the next release (the last gap wraps around the scene to the first release, so frame 0
    # repeats).
    hold_max, fade, start_min = man["hold_after_ball"], man["reset_fade"], man["start_hold_min"]
    tt_v, tb_v = t_tip * slow, t_ball * slow
    gaps = [rels[k + 1] - rels[k] for k in range(drops - 1)] + [rels[0] + D - rels[-1]]
    holds = [min(hold_max, gp - tb_v - 2.0 * fade - start_min) for gp in gaps]
    assert min(holds) >= 1.0, "every drop needs at least 1 s of landed hold before its fade"
    c0 = rels[0] + D - rels[-1]   # cycle time of the last drop at frame 0 (and at the scene's end)
    print(f"schedule (video time, 1/{slow:g} speed): releases at " + ", ".join(f"{r:.2f}" for r in rels)
          + f" s; the chain tip lands {tt_v:.3f} s after each release (at " + ", ".join(f"{r + tt_v:.2f}" for r in rels)
          + f" s) and the ball {tb_v:.3f} s after (at " + ", ".join(f"{r + tb_v:.2f}" for r in rels)
          + f" s), {lead * slow:.3f} s later; the ball's position at the tip's landing is marked from the tip's landing "
          f"({100.0 * gap:.0f} cm up) until the fade; after the ball lands each pair holds "
          + ", ".join(f"{h:.2f}" for h in holds) + f" s (the manifest hold {hold_max:g} s clipped to the gap, keeping at least {start_min:g} s at the start), fades "
          f"out over {fade:g} s (from " + ", ".join(f"{r + tb_v + h:.2f}" for r, h in zip(rels, holds))
          + f" s), the start state fades in over {fade:g} s and holds "
          + ", ".join(f"{gp - tb_v - h - 2.0 * fade:.2f}" for gp, h in zip(gaps, holds))
          + f" s until the next release; on the first frame both sit at the start line, {rels[0]:.2f} s before the "
          f"first release (the last drop's cycle is {c0:.2f} s old, its start hold began at "
          f"{rels[-1] + tb_v + holds[-1] + 2.0 * fade:.2f} s); title until {man['title_until']:g} s, then the "
          f"legend and the fixed lines; payoff card from {man['payoff_t']:g} s; the HUD fades out and the title "
          f"back in over the last {man['loop_fade']:g} s and the last frame repeats the first (the scene is "
          f"periodic: the state at {D:g} s is the state at 0 s, {drops} drops in {D:g} s)")
    ev = {"t_tip": t_tip, "t_ball": t_ball, "lead_ms": 1000.0 * lead, "gap": gap, "gap_cm": 100.0 * gap,
          "y_ball_at_tip": y_ball_at_tip, "v_half": v_half, "v_ball_half": math.sqrt(g * L), "x_cap": x_cap,
          "table": (T, X), "n_links": n_links, "releases": rels, "holds": holds}
    # Text widths.
    font = os.environ["SEED_ZERO_FONT"]
    f28, f34, f40, f56 = (ImageFont.truetype(font, n) for n in (28, 34, 40, 56))
    widths = {"overlay@34": (f34, man["overlay"])}
    for j, line in enumerate(man["title"].split("|")):
        widths[f"title line {j + 1}@56"] = (f56, line)
    widths["legend@40"] = (f40, legend_text())
    widths["tag@28"] = (f28, tag_text(man))
    widths["label chain@40"] = (f40, "chain")
    widths["label ball@40"] = (f40, "ball")
    widths["clock@40"] = (f40, clock_text(t_ball))
    widths["tip readout@28"] = (f28, tip_text(x_cap, v_cap))
    widths["ball readout@28"] = (f28, ball_text(L, g * t_ball))
    widths["tip landed@28"] = (f28, tip_landed_text(ev))
    widths["ball landed@28"] = (f28, ball_landed_text(ev))
    widths["gap tag@28"] = (f28, gap_text(ev))
    widths["scale@28"] = (f28, f"{L:g} m")
    for j, line in enumerate(fixed_lines(ev)):
        widths[f"fixed line {j + 1}@28"] = (f28, line)
    for j, line in enumerate(payoff_lines(man, ev)):
        widths[f"payoff line {j + 1}@40"] = (f40, line)
    print("text widths: " + ", ".join(f"{k} {f.getlength(s):.0f} px" for k, (f, s) in widths.items()))
    assert all(f.getlength(s) < 950 for f, s in widths.values()), "a text line is wider than 950 px"
    return ev


def legend_text() -> str:
    return "both fall 1 m, let go together"


def tag_text(man: dict) -> str:
    return f"1/{man['slow_factor']:g} speed, no air, ball measured at its center"


def clock_text(tau: float) -> str:
    return f"{tau:.3f} s"


def tip_text(x: float, v: float) -> str:
    return f"tip {x:.2f} m, {v:.1f} m/s"


def ball_text(y: float, v: float) -> str:
    return f"ball {y:.2f} m, {v:.1f} m/s"


def tip_landed_text(ev: dict) -> str:
    return f"tip lands at {ev['t_tip']:.3f} s"


def ball_landed_text(ev: dict) -> str:
    return f"ball lands at {ev['t_ball']:.3f} s"


def gap_text(ev: dict) -> str:
    return f"{ev['gap_cm']:.0f} cm up"


def fixed_lines(ev: dict) -> list[str]:
    return [f"halfway down: tip {ev['v_half']:.2f} m/s, ball {ev['v_ball_half']:.2f} m/s",
            f"chain tip {ev['t_tip']:.3f} s, ball {ev['t_ball']:.3f} s: a {ev['lead_ms']:.0f} ms lead"]


def payoff_lines(man: dict, ev: dict) -> list[str]:
    text = man["payoff_text"].format(t_tip=ev["t_tip"], t_ball=ev["t_ball"], lead_ms=ev["lead_ms"],
                                     gap_cm=ev["gap_cm"])
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
        self.ppm = float(man["px_per_m"])
        self.g, self.L, self.link, self.rb = man["g_m_s2"], man["chain_m"], man["link_m"], man["ball_radius_m"]
        self.slow, self.D = man["slow_factor"], man["scene_duration"]
        self.releases, self.holds, self.fade = ev["releases"], ev["holds"], man["reset_fade"]
        self.T, self.X = ev["table"]
        self.t_tip, self.t_ball = ev["t_tip"], ev["t_ball"]
        self.y0 = float(man["start_y"])
        self.y1 = self.y0 + self.L * self.ppm
        self.gap_px = man["strand_gap_m"] * self.ppm
        self.fixed_x = man["chain_x"] - 0.5 * self.gap_px
        self.free_x = man["chain_x"] + 0.5 * self.gap_px

    # --- state helpers ------------------------------------------------------
    def phase(self, t: float) -> tuple[float, float]:
        """(tau, alpha): real seconds since the latest release (0 at the start line) and the blend of
        the moving pair; tau runs on through the landed hold and the fade-out. Before the first
        release the last drop's cycle, wrapped around the scene, is in progress."""
        k = bisect.bisect_right(self.releases, t) - 1
        if k < 0:
            k, r = len(self.releases) - 1, self.releases[-1] - self.D
        else:
            r = self.releases[k]
        c, hold = t - r, self.holds[k]
        tb = self.t_ball * self.slow
        if c < tb + hold:
            return c / self.slow, 1.0
        if c < tb + hold + self.fade:
            return (tb + hold) / self.slow, 1.0 - (c - tb - hold) / self.fade
        if c < tb + hold + 2.0 * self.fade:
            return 0.0, (c - tb - hold - self.fade) / self.fade
        return 0.0, 1.0

    def tip_depth(self, tau: float) -> float:
        if tau >= self.t_tip:
            return self.L
        return float(np.interp(tau, self.T, self.X))

    def ball_depth(self, tau: float) -> float:
        return min(self.L, 0.5 * self.g * tau * tau)

    # --- pixel helpers ------------------------------------------------------
    def L_(self, X: float, Y: float) -> tuple[float, float]:
        # Rounded to 1e-4 px so that equal states draw the same pixels (the periodicity check).
        return round(X * SS, 4), round((Y - GEOM_Y0) * SS, 4)

    def circle(self, d: ImageDraw.ImageDraw, X: float, Y: float, rr: float, **kw) -> None:
        d.ellipse((X - rr, Y - rr, X + rr, Y + rr), **kw)

    # --- the scene ----------------------------------------------------------
    def draw_scene(self, d: ImageDraw.ImageDraw, tau: float, alpha: float) -> dict:
        man = self.man
        L, link, ppm = self.L, self.link, self.ppm
        x = self.tip_depth(tau)
        yb = self.ball_depth(tau)
        capped = x > L - link
        # The start and finish lines and the scale bar.
        for yy in (self.y0, self.y1):
            p0, p1 = self.L_(man["line_x0"], yy), self.L_(man["line_x1"], yy)
            d.line((*p0, *p1), fill=RIM, width=3 * SS)
        sx = man["scale_x"]
        mid = 0.5 * (self.y0 + self.y1)
        for ya, yb_ in ((self.y0, mid - 26), (mid + 26, self.y1)):
            p0, p1 = self.L_(sx, ya), self.L_(sx, yb_)
            d.line((*p0, *p1), fill=RIM, width=3 * SS)
        for yy in (self.y0, self.y1):
            p0, p1 = self.L_(sx - 12, yy), self.L_(sx + 12, yy)
            d.line((*p0, *p1), fill=RIM, width=3 * SS)
        # The peg that holds the chain's fixed end.
        p0, p1 = self.L_(self.fixed_x - 9, self.y0 - 24), self.L_(self.fixed_x + 9, self.y0)
        d.rounded_rectangle((*p0, *p1), radius=4 * SS, fill=RIM)
        # The chain: the held side hangs straight from the peg to the fold (L + x) / 2 below it, the
        # free side rises from the fold to the free end x below the start line; a half circle at the
        # fold; links of pitch link_m along both sides (the ones in transit over the fold are the arc).
        yf = L if capped else 0.5 * (L + x)
        xt = L if capped else x
        rope = blend(RIM, 0.9 * alpha)
        p0, p1 = self.L_(self.fixed_x, self.y0), self.L_(self.fixed_x, self.y0 + yf * ppm)
        d.line((*p0, *p1), fill=rope, width=2 * SS)
        if not capped:
            p0, p1 = self.L_(self.free_x, self.y0 + yf * ppm), self.L_(self.free_x, self.y0 + xt * ppm)
            d.line((*p0, *p1), fill=rope, width=2 * SS)
            cx, cy = self.L_(man["chain_x"], self.y0 + yf * ppm)
            rr = 0.5 * self.gap_px * SS
            d.arc((cx - rr, cy - rr, cx + rr, cy + rr), 0, 180, fill=blend(WHITE, 0.85 * alpha), width=5 * SS)
        half = 0.5 * link
        w_flat, w_edge, ln = 0.016 * ppm, 0.007 * ppm, 0.021 * ppm
        for k in range(self.ev["n_links"]):
            a = (k + 0.5) * link
            if a + half <= yf + 1e-12:
                cx, cy = self.fixed_x, self.y0 + a * ppm
            elif not capped and a - half >= yf - 1e-12:
                cx, cy = self.free_x, self.y0 + xt * ppm + (L - a) * ppm
            else:
                continue
            w = w_flat if k % 2 == 0 else w_edge
            col = blend(WHITE, 0.85 * alpha) if k % 2 == 0 else blend(TEXT, 0.6 * alpha)
            X0, Y0 = self.L_(cx - 0.5 * w, cy - 0.5 * ln)
            X1, Y1 = self.L_(cx + 0.5 * w, cy + 0.5 * ln)
            d.ellipse((X0, Y0, X1, Y1), outline=col, width=3 * SS)
        # The tip dot, and the landing tick once the tip is down.
        tip_x = self.fixed_x if capped else self.free_x
        TX, TY = self.L_(tip_x, self.y0 + xt * ppm)
        self.circle(d, TX, TY, 6 * SS, fill=blend(GOLD, alpha))
        if tau >= self.t_tip:
            p0, p1 = self.L_(man["chain_x"] - 40, self.y1), self.L_(man["chain_x"] + 40, self.y1)
            d.line((*p0, *p1), fill=blend(GOLD, alpha), width=5 * SS)
        # The ball, its landing tick, and the ghost where it was when the tip landed.
        bx = man["ball_x"]
        if tau >= self.t_tip:
            gy = self.y0 + self.ev["y_ball_at_tip"] * ppm
            GX, GY = self.L_(bx, gy)
            rr = self.rb * ppm * SS
            for j in range(12):
                d.arc((GX - rr, GY - rr, GX + rr, GY + rr), 30 * j, 30 * j + 16, fill=blend(GOLD, alpha), width=3 * SS)
            p0, p1 = self.L_(bx + 50, gy), self.L_(bx + 50, self.y1)
            d.line((*p0, *p1), fill=blend(GOLD, alpha), width=3 * SS)
            for yy in (gy, self.y1):
                p0, p1 = self.L_(bx + 42, yy), self.L_(bx + 58, yy)
                d.line((*p0, *p1), fill=blend(GOLD, alpha), width=3 * SS)
        if tau >= self.t_ball:
            p0, p1 = self.L_(bx - 40, self.y1), self.L_(bx + 40, self.y1)
            d.line((*p0, *p1), fill=blend(TEAL, alpha), width=5 * SS)
        BX, BY = self.L_(bx, self.y0 + yb * ppm)
        self.circle(d, BX, BY, self.rb * ppm * SS, fill=blend(TEAL, alpha))
        return {"x": x, "yb": yb, "capped": capped, "tau": tau, "alpha": alpha}

    def draw_text(self, d: ImageDraw.ImageDraw, st: dict, hud_alpha: float) -> None:
        man, ev = self.man, self.ev
        tau, alpha = st["tau"], st["alpha"]
        d.text((man["chain_x"], LABEL_Y), "chain", font=self.font, fill=TEXT, anchor="mm")
        d.text((man["ball_x"], LABEL_Y), "ball", font=self.font, fill=TEXT, anchor="mm")
        d.text((READ_X, LABEL_Y), clock_text(min(tau, self.t_ball)), font=self.font, fill=blend(TEXT, alpha), anchor="rm")
        d.text((man["scale_x"], 0.5 * (self.y0 + self.y1)), f"{self.L:g} m", font=self.font_small, fill=MUTED, anchor="mm")
        # The live readouts sit under the finish line, the tip's from its left end and the ball's
        # to its right end, so the two never meet.
        if tau >= self.t_tip:
            d.text((man["line_x0"], READ_Y), tip_landed_text(ev), font=self.font_small, fill=blend(GOLD, alpha), anchor="lm")
        else:
            v = float(v_closed(st["x"], self.L, self.g)) if st["x"] > 0.0 else 0.0
            d.text((man["line_x0"], READ_Y), tip_text(st["x"], v), font=self.font_small, fill=blend(TEXT, alpha), anchor="lm")
        if tau >= self.t_ball:
            d.text((man["line_x1"], READ_Y), ball_landed_text(ev), font=self.font_small, fill=blend(TEAL, alpha), anchor="rm")
        else:
            d.text((man["line_x1"], READ_Y), ball_text(st["yb"], self.g * tau), font=self.font_small,
                   fill=blend(TEXT, alpha), anchor="rm")
        if tau >= self.t_tip:
            gy = self.y0 + ev["y_ball_at_tip"] * self.ppm
            d.text((man["ball_x"] + 66, 0.5 * (gy + self.y1)), gap_text(ev), font=self.font_small,
                   fill=blend(GOLD, alpha), anchor="lm")
        if hud_alpha > 0.02:
            d.text((W / 2, LEGEND_Y), legend_text(), font=self.font, fill=blend(TEXT, hud_alpha), anchor="mm")
            d.text((W / 2, TAG_Y), tag_text(man), font=self.font_small, fill=blend(MUTED, hud_alpha), anchor="mm")
            for j, line in enumerate(fixed_lines(ev)):
                d.text((W / 2, FIXED_Y0 + j * FIXED_PITCH), line, font=self.font_small, fill=blend(MUTED, hud_alpha),
                       anchor="mm")

    def live_frame(self, f: int, title_alpha: float | None = None, hud_alpha: float = 0.0) -> np.ndarray:
        """Frame f with the geometry at f / fps; title_alpha and hud_alpha override the title and
        the legend/readout/card blend during the loop fade."""
        man = self.man
        t = f / self.fps
        if title_alpha is None:
            if t < man["title_until"]:
                title_alpha = 1.0 if t < man["title_until"] - 0.4 else (man["title_until"] - t) / 0.4
                hud_alpha = 0.0
            else:
                title_alpha = 0.0
                hud_alpha = min(1.0, (t - man["title_until"]) / 0.4)
        img = Image.new("RGB", (W, H), BG)
        layer = Image.new("RGB", (W * SS, (GEOM_Y1 - GEOM_Y0) * SS), BG)
        ld = ImageDraw.Draw(layer)
        tau, alpha = self.phase(t)
        st = self.draw_scene(ld, tau, alpha)
        img.paste(layer.reduce(SS), (0, GEOM_Y0))
        d = ImageDraw.Draw(img)
        self.draw_text(d, st, hud_alpha)
        if title_alpha > 0.0:
            for j, line in enumerate(man["title"].split("|")):
                d.text((W / 2, TITLE_Y0 + j * TITLE_PITCH), line, font=self.font_title, fill=blend(TEXT, title_alpha),
                       anchor="mm")
        if t >= man["payoff_t"]:
            a = min(1.0, (t - man["payoff_t"]) / man["payoff_hold"]) * hud_alpha
            for j, line in enumerate(payoff_lines(man, self.ev)):
                d.text((W / 2, PAYOFF_Y + j * 56), line, font=self.font, fill=blend(GOLD, a), anchor="mm")
        return np.asarray(img, dtype=np.uint8)

    def frame_at(self, f: int) -> np.ndarray:
        man = self.man
        total = int(round(man["scene_duration"] * self.fps))
        fade_frames = int(round(man["loop_fade"] * self.fps))
        if f == total - 1:
            return self.live_frame(0)   # the scene is periodic: the last frame repeats the first
        if f >= total - fade_frames:
            # The geometry runs on; the legend, readouts and card fade out over the first half of
            # the loop fade and the title fades in over the second half, so the two never overlap.
            a = (f - (total - fade_frames) + 1) / fade_frames
            return self.live_frame(f, title_alpha=max(0.0, 2.0 * a - 1.0), hud_alpha=max(0.0, 1.0 - 2.0 * a))
        return self.live_frame(f)

    def render(self, out_path: Path) -> None:
        global _RENDERER
        out_path.parent.mkdir(parents=True, exist_ok=True)
        total = int(round(self.man["scene_duration"] * self.fps))
        first = self.frame_at(0)
        last = self.frame_at(total - 1)
        diff = np.abs(first.astype(int) - last.astype(int))
        print(f"loop check: last frame differs from the first in {int((diff.max(axis=2) > 24).sum())} px "
              f"(max channel difference {int(diff.max())})")
        wrap = self.live_frame(total, title_alpha=1.0, hud_alpha=0.0)   # the geometry one period on, drawn live
        diff = np.abs(first.astype(int) - wrap.astype(int))
        print(f"periodicity check: the scene drawn live at {self.man['scene_duration']:g} s differs from 0 s in "
              f"{int((diff.max(axis=2) > 24).sum())} px (max channel difference {int(diff.max())})")
        prev = self.frame_at(total - 2)
        diff = np.abs(prev.astype(int) - last.astype(int))
        print(f"loop step: the frame before the last differs from the last in {int((diff.max(axis=2) > 24).sum())} px")
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
    man = json.loads((ROOT / "projects/chain/manifest.json").read_text())
    ev = measure(man)
    if "--measure-only" in sys.argv:
        return
    if "--frames" in sys.argv:
        times = [float(v) for v in sys.argv[sys.argv.index("--frames") + 1].split(",")]
        r = Renderer(man, ev)
        (ROOT / "media/chain").mkdir(parents=True, exist_ok=True)
        for tv in times:
            Image.fromarray(r.frame_at(int(round(tv * man["fps"])))).save(ROOT / f"media/chain/smoke-{tv}.png")
        print("smoke frames: " + ", ".join(f"{tv}" for tv in times))
        return
    Renderer(man, ev).render(ROOT / "media/chain/footage.mp4")


if __name__ == "__main__":
    main()
