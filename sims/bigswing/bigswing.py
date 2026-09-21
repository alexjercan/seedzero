#!/usr/bin/env python3
"""Big swing versus small swing: same pendulum, bigger swing. Does it take longer?

One simple pendulum (a point bob on a massless rod of length L, g =
9.80665 m/s^2, theta'' = -(g / L) sin theta) drawn twice at the same
scale: the top panel is released from rest at 10 degrees, the bottom
panel from rest at the big angle, both at t = 0. The length is chosen so
that the 10 degree swing takes exactly 2.000 s out and back, and the big
release angle is solved so that its swing takes exactly 2.500 s, from
the closed form

    T = 4 sqrt(L / g) K(k),  k = sin(theta0 / 2),

with K the complete elliptic integral of the first kind (AGM). Both are
integrated with RK4 at 3,600 steps per second for the 40 s scene; the
turnarounds and the bottom crossings are found in the step arrays. In
40.000 s the small swing makes 20 swings and the big one 16, both back
at the release side, so the scene loops. Played at real speed.
Deterministic, no seed.

Measured and printed: the solved length and big angle with the K(k)
check, the small-angle period 2 pi sqrt(L / g), T / T0 for a table of
angles, and for each panel the RK4 period of every swing (first, mean,
spread) against the closed form, the swing count at 40.000 s and the
time of the last turnaround, the bottom crossings, the bottom speed
against sqrt(2 g L (1 - cos theta0)), the time above horizontal and
near the turnarounds, the energy drift, a half-step check, the
coincidences of the two swings, the counter schedule in video time and
the on-screen text widths.

usage: bigswing.py [--measure-only] [--frames t1,t2,...]
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

# Layout: overlay at y 96 (captions.py), title rows at y 190/252/314 for
# the first seconds, two panels of 543 px from y 350 (top: 10 degrees,
# bottom: the big angle). In each panel the pivot sits at x 700, 100 px
# under the panel top, with a 300 px rod, so the bob sweeps x 384..1016
# and the big bob rises 70 px above the pivot; the readouts live in the
# left column x 40..370, which the bob never reaches. A shared time strip
# at y 845 between the panels (x 400..1016) carries a tick at the start
# of every swing (small ticks up, big ticks down) and the elapsed clock
# at its left. Captions at caption_y 0.75 (y 1440..1520), payoff card
# under them from y 1592.
GEOM_Y0, GEOM_Y1 = 350, 1436
PANEL_H = (GEOM_Y1 - GEOM_Y0) // 2
PIVOT_X = 700.0
PIVOT_DY = 100.0
COL_X = 40
STRIP_X0, STRIP_X1 = 400.0, 1016.0
STRIP_Y = GEOM_Y0 + PANEL_H - 48
PANELS = {"small": {"index": 0, "colour": TEAL}, "big": {"index": 1, "colour": CORAL}}
SS = 2
PAYOFF_Y = 1592.0
BOB_R = 16.0
TICK_DY = 28.0  # bottom marker under the arc


def blend(col, a, base=BG):
    a = max(0.0, min(1.0, a))
    return tuple(int(round(c * a + b * (1 - a))) for c, b in zip(col, base))


def smoothstep(u: float) -> float:
    u = max(0.0, min(1.0, u))
    return u * u * (3 - 2 * u)


def ellipk(k: float) -> float:
    """Complete elliptic integral of the first kind K(k) by the arithmetic-geometric mean."""
    a, b = 1.0, math.sqrt(1.0 - k * k)
    for _ in range(60):
        if abs(a - b) < 1e-17:
            break
        a, b = 0.5 * (a + b), math.sqrt(a * b)
    return math.pi / (2.0 * a)


def period_exact(g: float, L: float, angle_deg: float) -> float:
    return 4.0 * math.sqrt(L / g) * ellipk(math.sin(math.radians(angle_deg) / 2.0))


def solve_angle(g: float, L: float, T: float, lo: float = 1.0, hi: float = 179.99) -> float:
    """Release angle (degrees) whose period is T; the period grows with the angle."""
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if period_exact(g, L, mid) < T:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def simulate(g: float, L: float, angle_deg: float, steps: int, t_max: float) -> dict:
    """RK4 on (theta, omega) from rest at +angle_deg; events by linear interpolation in the step."""
    dt = 1.0 / steps
    n = int(round(t_max * steps))
    theta = np.empty(n + 1)
    omega = np.empty(n + 1)
    k = g / L
    th, w = math.radians(angle_deg), 0.0
    sin = math.sin
    for i in range(n + 1):
        theta[i], omega[i] = th, w
        if i == n:
            break
        k1t, k1w = w, -k * sin(th)
        k2t, k2w = w + 0.5 * dt * k1w, -k * sin(th + 0.5 * dt * k1t)
        k3t, k3w = w + 0.5 * dt * k2w, -k * sin(th + 0.5 * dt * k2t)
        k4t, k4w = w + dt * k3w, -k * sin(th + dt * k3t)
        th += dt / 6.0 * (k1t + 2 * k2t + 2 * k3t + k4t)
        w += dt / 6.0 * (k1w + 2 * k2w + 2 * k3w + k4w)
    t = np.arange(n + 1) * dt
    # Turnarounds on the release side (omega + -> -), on the far side (- -> +), bottom crossings.
    i_ret = np.nonzero((omega[:-1] > 0.0) & (omega[1:] <= 0.0))[0]
    t_ret = t[i_ret] + dt * omega[i_ret] / (omega[i_ret] - omega[i_ret + 1])
    i_far = np.nonzero((omega[:-1] < 0.0) & (omega[1:] >= 0.0))[0]
    t_far = t[i_far] + dt * omega[i_far] / (omega[i_far] - omega[i_far + 1])
    i_bot = np.nonzero(theta[:-1] * theta[1:] < 0.0)[0]
    t_bot = t[i_bot] + dt * theta[i_bot] / (theta[i_bot] - theta[i_bot + 1])
    th0 = math.radians(angle_deg)
    e = 0.5 * L * L * omega * omega - g * L * np.cos(theta)
    e0 = -g * L * math.cos(th0)
    drift = float(np.abs(e - e0).max() / (g * L * (1.0 - math.cos(th0))))
    return {"angle": angle_deg, "dt": dt, "t": t, "theta": theta, "omega": omega, "t_ret": t_ret, "t_far": t_far,
            "t_bot": t_bot, "drift": drift, "v_max": float(L * np.abs(omega).max())}


def measure(man: dict) -> dict:
    g = man["g"]
    steps, fps = man["steps_per_second"], man["fps"]
    a_small, T_small, T_big = man["small_angle_deg"], man["small_period_s"], man["big_period_s"]
    dur = man["scene_duration"]
    k_small = math.sin(math.radians(a_small) / 2.0)
    K_small = ellipk(k_small)
    L = g * (T_small / (4.0 * K_small)) ** 2
    T0 = 2.0 * math.pi * math.sqrt(L / g)
    a_big = solve_angle(g, L, T_big)
    k_big = math.sin(math.radians(a_big) / 2.0)
    K_big = ellipk(k_big)
    sol = man.get("solved")
    if sol is not None:
        assert abs(sol["length_m"] - L) < 1e-9 and abs(sol["big_angle_deg"] - a_big) < 1e-8, \
            f"manifest solved values differ: L {L:.10f}, angle {a_big:.9f}"
    print(f"setup: one simple pendulum (point bob on a massless rod of length L, g = {g:g} m/s^2, theta'' = -(g / L) "
          f"sin theta) drawn twice at the same scale; top panel released from rest at {a_small:g} degrees, bottom panel "
          f"from rest at the big angle, both at t = 0; L chosen so that the {a_small:g} degree swing takes exactly "
          f"{T_small:.3f} s out and back and the big angle solved so that its swing takes exactly {T_big:.3f} s, from "
          f"T = 4 sqrt(L / g) K(sin(theta0 / 2)) with K by the AGM; RK4 on (theta, omega) at {steps} steps per second "
          f"(dt = {1 / steps:.2e} s) for {man['sim_t_max']:g} s; played at real speed; deterministic, no seed")
    print(f"closed forms: K(sin {a_small / 2:g} deg) = K({k_small:.6f}) = {K_small:.9f}; L = g (T / 4 K)^2 = {L:.6f} m "
          f"({L * 100:.2f} cm); small-angle period T0 = 2 pi sqrt(L / g) = {T0:.6f} s, so the {a_small:g} degree swing runs "
          f"{(T_small / T0 - 1) * 100:.2f} percent slow; big angle solved by bisection: theta0 = {a_big:.3f} degrees "
          f"({a_big:.6f}; {a_big - 90:.3f} degrees above horizontal, the bob rises {-math.cos(math.radians(a_big)):.4f} L = "
          f"{-L * math.cos(math.radians(a_big)) * 100:.2f} cm above the pivot at the turnaround); check: k = sin({a_big / 2:.4f} deg) = "
          f"{k_big:.6f}, K(k) = {K_big:.9f}, 4 sqrt(L / g) K = {4 * math.sqrt(L / g) * K_big:.9f} s, ratio to T0 "
          f"{T_big / T0:.6f} = (2 / pi) K = {2 / math.pi * K_big:.6f}; T({a_big:.3f}) / T({a_small:g}) = {T_big / T_small:.4f}")
    table = ", ".join(f"{a:g} deg {period_exact(g, L, a) / T0:.4f} ({(period_exact(g, L, a) / T0 - 1) * 100:.1f} percent slow, "
                      f"{period_exact(g, L, a):.3f} s)" for a in man["table_angles_deg"])
    print(f"T / T0 = (2 / pi) K(sin(theta0 / 2)) for this pendulum: {table}")
    runs = {}
    for name, angle, T_target in (("small", a_small, T_small), ("big", a_big, T_big)):
        run = simulate(g, L, angle, steps, man["sim_t_max"])
        run["T_target"] = T_target
        run["T_exact"] = period_exact(g, L, angle)
        ret = run["t_ret"]
        periods = np.diff(np.concatenate(([0.0], ret)))
        in_scene = ret <= dur + 1e-6
        n_done = int(in_scene.sum())
        run["n_done"] = n_done
        run["t_last"] = float(ret[n_done - 1])
        run["periods"] = periods
        run["T_rk4"] = float(periods[:n_done].mean())
        th0 = math.radians(angle)
        v_bot = math.sqrt(2.0 * g * L * (1.0 - math.cos(th0)))
        halves = np.diff(run["t_bot"])
        i_first = int(np.searchsorted(run["t"], ret[0]))
        th_first = run["theta"][: i_first + 1]
        above = float((np.abs(th_first) > 0.5 * math.pi).sum() * run["dt"])
        near = float((np.abs(th_first) > th0 - math.radians(10.0)).sum() * run["dt"])
        run["above"] = above
        runs[name] = run
        print(f"{name} panel, released from rest at {angle:.3f} degrees: RK4 swing (out and back, turnaround to turnaround on "
              f"the release side) first {periods[0]:.6f} s, mean of the {n_done} swings in {dur:g} s {run['T_rk4']:.6f} s, "
              f"min {periods[:n_done].min():.6f}, max {periods[:n_done].max():.6f} (closed form {run['T_exact']:.6f} s, "
              f"{periods[0] - run['T_exact']:+.1e}); swings done at {dur:.3f} s: {n_done}, the last turnaround at "
              f"{run['t_last']:.6f} s" + (f", the next at {ret[n_done]:.4f} s" if len(ret) > n_done else "")
              + f"; bottom crossings at {run['t_bot'][0]:.6f}, "
              f"{run['t_bot'][1]:.6f}, {run['t_bot'][2]:.6f} s ... ({int((run['t_bot'] <= dur + 1e-6).sum())} in {dur:g} s), "
              f"half swing mean {halves[: 2 * n_done - 1].mean():.6f} s (spread {halves[: 2 * n_done - 1].max() - halves[: 2 * n_done - 1].min():.1e}); "
              f"speed at the bottom {run['v_max']:.4f} m/s (closed form sqrt(2 g L (1 - cos theta0)) = {v_bot:.4f}); per swing "
              f"{above:.4f} s above horizontal"
              + (f" and {near:.4f} s within 10 degrees of a turnaround ({near / periods[0] * 100:.1f} percent of the swing, "
                 f"{20.0 / angle * 100:.1f} percent of the arc)" if angle > 20.0 else "")
              + f"; energy drift {run['drift']:.1e}")
    for name in PANELS:
        run = runs[name]
        run_h = simulate(g, L, run["angle"], 2 * steps, man["sim_t_max"])
        p_h = np.diff(np.concatenate(([0.0], run_h["t_ret"])))
        print(f"check at half the time step ({2 * steps} steps per second), {run['angle']:.3f} degrees: first swing "
              f"{p_h[0]:.6f} s ({p_h[0] - run['periods'][0]:+.1e}), swings done at {dur:g} s {int((run_h['t_ret'] <= dur + 1e-6).sum())}, "
              f"last turnaround {run_h['t_ret'][int((run_h['t_ret'] <= dur + 1e-6).sum()) - 1]:.6f} s, energy drift {run_h['drift']:.1e}")
    # Coincidences: both bobs at a turnaround within 1 ms.
    s_turn = np.sort(np.concatenate((runs["small"]["t_ret"], runs["small"]["t_far"])))
    b_turn = np.sort(np.concatenate((runs["big"]["t_ret"], runs["big"]["t_far"])))
    coinc = []
    for tb in b_turn:
        if tb > dur + 1e-6:
            break
        j = int(np.argmin(np.abs(s_turn - tb)))
        if abs(s_turn[j] - tb) < 1e-3:
            side_s = "release side" if np.any(np.abs(runs["small"]["t_ret"] - s_turn[j]) < 1e-6) else "far side"
            side_b = "release side" if np.any(np.abs(runs["big"]["t_ret"] - tb) < 1e-6) else "far side"
            coinc.append(f"{tb:.3f} s (small {side_s}, big {side_b})")
    print(f"drift: the small swing gains {T_big - T_small:.3f} s a swing, a quarter swing every big swing, so both bobs are at a "
          f"turnaround together at " + ", ".join(coinc) + f"; in between the counters differ by up to "
          f"{int(math.floor(dur / T_small)) - int(math.floor(dur / T_big))} swings")
    # Counter schedule in video time.
    reads = []
    for tv in (0.0, 2.0, 2.5, 5.0, 10.0, 15.0, 20.0, 25.0, 30.0, 35.0, dur - 1.0 / fps):
        ns = 1 + int((runs["small"]["t_ret"] <= tv + 1e-9).sum())
        nb = 1 + int((runs["big"]["t_ret"] <= tv + 1e-9).sum())
        reads.append(f"{tv:.2f} s: swing {ns} / swing {nb}")
    print(f"video schedule (real speed, both released at 0 s, the counter shows the swing in progress, 1 at the release): "
          + "; ".join(reads) + f"; the small counter ticks at " + ", ".join(f"{v:.1f}" for v in runs["small"]["t_ret"][:4])
          + f" ... s and the big one at " + ", ".join(f"{v:.2f}" for v in runs["big"]["t_ret"][:4])
          + f" ... s; the period readouts appear at {runs['small']['t_ret'][0]:.3f} s (small) and {runs['big']['t_ret'][0]:.3f} s "
          f"(big); the strip ticks at every swing start, {runs['small']['n_done']} small and {runs['big']['n_done']} big by the end; "
          f"title until {man['title_until']:g} s; slow-part mark from {man['slow_mark_t']:g} s; payoff card from {man['payoff_t']:g} s; "
          f"loop: counters, strip and card crossfade over the last {man['loop_fade']:g} s, the pendulums over the last "
          f"{man['motion_fade_frames']} frames")
    # Text widths.
    font = os.environ["SEED_ZERO_FONT"]
    f34, f56, f40, f28, f48, f88 = (ImageFont.truetype(font, n) for n in (34, 56, 40, 28, 48, 88))
    widths = {"overlay@34": (f34, man["overlay"])}
    for j, line in enumerate(man["title"].split("|")):
        widths[f"title line {j + 1}@56"] = (f56, line)
    widths["label small@40"] = (f40, panel_label("small"))
    widths["label big@40"] = (f40, panel_label("big"))
    widths["sublabel small@28"] = (f28, panel_sublabel(a_small))
    widths["sublabel big@28"] = (f28, panel_sublabel(a_big))
    widths["swing label@28"] = (f28, "swing")
    widths["counter@88"] = (f88, f"{runs['small']['n_done']}")
    widths["stopwatch@28"] = (f28, "this swing 1.23 s")
    widths["period label@28"] = (f28, "out and back")
    widths["period@48"] = (f48, f"{T_big:.3f} s")
    widths["timing@28"] = (f28, "timing")
    widths["clock@40"] = (f40, f"{dur - 1 / fps:.2f} s")
    for j, line in enumerate(payoff_lines(man, runs)):
        widths[f"payoff line {j + 1}@40"] = (f40, line)
    print("text widths: " + ", ".join(f"{k} {f.getlength(s):.0f} px" for k, (f, s) in widths.items())
          + f"; left column budget {int(PIVOT_X - man['rod_px'] * math.sin(math.radians(a_big)) - BOB_R - 20 - COL_X)} px")
    return {"L": L, "T0": T0, "a_big": a_big, "runs": runs}


def panel_label(name: str) -> str:
    return "small swing" if name == "small" else "big swing"


def panel_sublabel(angle: float) -> str:
    return f"let go at {angle:.1f} deg" if angle != int(angle) else f"let go at {angle:.0f} degrees"


def payoff_lines(man: dict, runs: dict) -> list[str]:
    text = man["payoff_text"].format(t_small=runs["small"]["T_rk4"], t_big=runs["big"]["T_rk4"],
                                     n_small=runs["small"]["n_done"], n_big=runs["big"]["n_done"],
                                     dur=man["scene_duration"])
    return [s.strip() for s in text.split("|")]


class Renderer:
    def __init__(self, man: dict, meas: dict):
        self.man, self.meas = man, meas
        self.fps = man["fps"]
        self.runs = meas["runs"]
        font = os.environ["SEED_ZERO_FONT"]
        self.font = ImageFont.truetype(font, 40)
        self.font_title = ImageFont.truetype(font, 56)
        self.font_small = ImageFont.truetype(font, 28)
        self.font_num = ImageFont.truetype(font, 48)
        self.font_count = ImageFont.truetype(font, 88)
        self.rod = float(man["rod_px"])
        self.total = int(round(man["scene_duration"] * self.fps))
        self.first = None

    # --- state ------------------------------------------------------------
    def pivot(self, name: str) -> tuple[float, float]:
        return PIVOT_X, GEOM_Y0 + PANELS[name]["index"] * PANEL_H + PIVOT_DY

    def state(self, name: str, t: float) -> dict:
        run = self.runs[name]
        theta = float(np.interp(t, run["t"], run["theta"]))
        n_ret = int(np.searchsorted(run["t_ret"], t + 1e-9, side="right"))
        start = float(run["t_ret"][n_ret - 1]) if n_ret > 0 else 0.0
        last_T = float(run["periods"][n_ret - 1]) if n_ret > 0 else None
        n_bot = int(np.searchsorted(run["t_bot"], t + 1e-9, side="right"))
        since_bot = t - float(run["t_bot"][n_bot - 1]) if n_bot > 0 else None
        return {"theta": theta, "swing": n_ret + 1, "start": start, "last_T": last_T, "since_bot": since_bot}

    # --- drawing ----------------------------------------------------------
    def dashed(self, d: ImageDraw.ImageDraw, p0, p1, fill, width: int, dash: float, gap: float) -> None:
        x0, y0 = p0
        x1, y1 = p1
        L = math.hypot(x1 - x0, y1 - y0)
        if L < 1e-9:
            return
        ux, uy = (x1 - x0) / L, (y1 - y0) / L
        a = 0.0
        while a < L:
            b = min(L, a + dash)
            d.line((x0 + ux * a, y0 + uy * a, x0 + ux * b, y0 + uy * b), fill=fill, width=width)
            a = b + gap

    def draw_panel_geometry(self, d: ImageDraw.ImageDraw, name: str, st: dict, t: float) -> None:
        man, run = self.man, self.runs[name]
        col = PANELS[name]["colour"]
        px, py = self.pivot(name)
        R = self.rod
        th0 = math.radians(run["angle"])

        def P(x: float, y: float) -> tuple[float, float]:
            return x * SS, (y - GEOM_Y0) * SS

        # Horizontal through the pivot and the plumb line to the bottom of the arc.
        self.dashed(d, P(px - R - 20, py), P(px + R + 20, py), blend(MUTED, 0.45), 2 * SS, 12 * SS, 10 * SS)
        self.dashed(d, P(px, py), P(px, py + R), blend(MUTED, 0.45), 2 * SS, 12 * SS, 10 * SS)
        # The swing arc with a tick at each end.
        cx, cy = P(px, py)
        Rp = R * SS
        a0 = math.degrees(th0)
        d.arc((cx - Rp, cy - Rp, cx + Rp, cy + Rp), start=90 - a0, end=90 + a0, fill=blend(col, 0.4), width=3 * SS)
        for sgn in (-1.0, 1.0):
            ex, ey = px + R * math.sin(sgn * th0), py + R * math.cos(sgn * th0)
            ux, uy = math.sin(sgn * th0), math.cos(sgn * th0)
            d.line((P(ex - ux * 12, ey - uy * 12), P(ex + ux * 12, ey + uy * 12)), fill=blend(col, 0.8), width=3 * SS)
        # The slow part: the arc above horizontal, gold, from slow_mark_t (big panel only).
        if run["angle"] > 90.0 and t >= man["slow_mark_t"]:
            a = smoothstep((t - man["slow_mark_t"]) / 0.5)
            gold = blend(GOLD, a)
            d.arc((cx - Rp, cy - Rp, cx + Rp, cy + Rp), start=90 - a0, end=0, fill=gold, width=7 * SS)
            d.arc((cx - Rp, cy - Rp, cx + Rp, cy + Rp), start=180, end=90 + a0, fill=gold, width=7 * SS)
        # Bottom marker: a tick under the arc that flashes at every bottom crossing.
        flash = 0.0 if st["since_bot"] is None else math.exp(-st["since_bot"] / man["flash_decay"])
        mx, my = px, py + R + TICK_DY
        d.line((P(mx, my - 10), P(mx, my + 10)), fill=blend(WHITE, 0.3 + 0.7 * flash), width=int((3 + 3 * flash) * SS))
        if flash > 0.02:
            r = (10 + 26 * (1 - flash)) * SS
            fx, fy = P(px, py + R)
            d.ellipse((fx - r, fy - r, fx + r, fy + r), outline=blend(WHITE, 0.6 * flash), width=2 * SS)
        # Rod, pivot, bob.
        bx, by = px + R * math.sin(st["theta"]), py + R * math.cos(st["theta"])
        d.line((P(px, py), P(bx, by)), fill=WIRE, width=5 * SS)
        pr = 7 * SS
        d.ellipse((cx - pr, cy - pr, cx + pr, cy + pr), fill=BG, outline=TEXT, width=3 * SS)
        bob_col = col
        if run["angle"] > 90.0 and t >= man["slow_mark_t"] and abs(st["theta"]) > 0.5 * math.pi:
            bob_col = blend(GOLD, smoothstep((t - man["slow_mark_t"]) / 0.5), col)
        qx, qy = P(bx, by)
        r = BOB_R * SS
        d.ellipse((qx - r, qy - r, qx + r, qy + r), fill=bob_col, outline=blend(bob_col, 0.55), width=SS)
        hr = r * 0.32
        d.ellipse((qx - r * 0.45 - hr, qy - r * 0.45 - hr, qx - r * 0.45 + hr, qy - r * 0.45 + hr), fill=WHITE)

    def draw_geometry(self, t: float) -> Image.Image:
        img = Image.new("RGB", (W, H), BG)
        layer = Image.new("RGB", (W * SS, (GEOM_Y1 - GEOM_Y0) * SS), BG)
        ld = ImageDraw.Draw(layer)
        for name in PANELS:
            self.draw_panel_geometry(ld, name, self.state(name, t), t)
        img.paste(layer.reduce(SS), (0, GEOM_Y0))
        return img

    def draw_hud(self, img: Image.Image, t: float) -> np.ndarray:
        """Readouts, strip, clock, title and card for time t over an already drawn geometry."""
        man, runs = self.man, self.runs
        d = ImageDraw.Draw(img)
        for name, p in PANELS.items():
            run, col = runs[name], p["colour"]
            st = self.state(name, t)
            top = GEOM_Y0 + p["index"] * PANEL_H
            d.text((COL_X, top + 34), panel_label(name), font=self.font, fill=col, anchor="lm")
            d.text((COL_X, top + 76), panel_sublabel(run["angle"]), font=self.font_small, fill=MUTED, anchor="lm")
            d.text((COL_X, top + 150), "swing", font=self.font_small, fill=MUTED, anchor="lm")
            d.text((COL_X - 4, top + 214), f"{st['swing']}", font=self.font_count, fill=col, anchor="lm")
            d.text((COL_X, top + 290), f"this swing {max(0.0, t - st['start']):.2f} s", font=self.font_small, fill=MUTED,
                   anchor="lm")
            d.text((COL_X, top + 356), "out and back", font=self.font_small, fill=MUTED, anchor="lm")
            if st["last_T"] is None:
                d.text((COL_X, top + 402), "timing", font=self.font_small, fill=MUTED, anchor="lm")
            else:
                d.text((COL_X, top + 402), f"{st['last_T']:.3f} s", font=self.font_num, fill=col, anchor="lm")
        # Shared strip: swing starts, small ticks up and big ticks down, cursor at t.
        d.line((STRIP_X0, STRIP_Y, STRIP_X1, STRIP_Y), fill=WIRE, width=2)
        span = STRIP_X1 - STRIP_X0
        for name, p in PANELS.items():
            col = p["colour"]
            sgn = -1.0 if name == "small" else 1.0
            starts = np.concatenate(([0.0], runs[name]["t_ret"]))
            for ts in starts[starts <= t + 1e-9]:
                x = STRIP_X0 + span * ts / man["scene_duration"]
                d.line((x, STRIP_Y, x, STRIP_Y + sgn * 16), fill=col, width=3)
        xc = STRIP_X0 + span * t / man["scene_duration"]
        d.line((xc, STRIP_Y - 24, xc, STRIP_Y + 24), fill=WHITE, width=2)
        d.text((COL_X + 330, STRIP_Y), f"{t:.2f} s", font=self.font, fill=TEXT, anchor="rm")
        if t < man["title_until"]:
            a = 1.0 if t < man["title_until"] - 0.4 else (man["title_until"] - t) / 0.4
            for j, line in enumerate(man["title"].split("|")):
                d.text((W / 2, 190 + j * 62), line, font=self.font_title, fill=blend(TEXT, a), anchor="mm")
        if t >= man["payoff_t"]:
            a = min(1.0, (t - man["payoff_t"]) / man["payoff_hold"])
            for j, line in enumerate(payoff_lines(man, runs)):
                d.text((W / 2, PAYOFF_Y + j * 56), line, font=self.font, fill=blend(GOLD, a), anchor="mm")
        return np.asarray(img, dtype=np.float32)

    def frame_at(self, f: int) -> np.ndarray:
        man = self.man
        t = f / self.fps
        geo = self.draw_geometry(t)
        live = self.draw_hud(geo.copy(), t)
        fade_frames = int(round(man["loop_fade"] * self.fps))
        if f >= self.total - fade_frames:
            a = (f - (self.total - fade_frames) + 1) / fade_frames
            live = live * (1 - a) + self.draw_hud(geo.copy(), 0.0) * a
        mf = man["motion_fade_frames"]
        if f >= self.total - mf:
            if self.first is None:
                self.first = self.draw_hud(self.draw_geometry(0.0), 0.0)
            b = (f - (self.total - mf) + 1) / mf
            live = live * (1 - b) + self.first * b
        return live.astype(np.uint8)

    def render(self, out_path: Path) -> None:
        global _RENDERER
        out_path.parent.mkdir(parents=True, exist_ok=True)
        total = self.total
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
    man = json.loads((ROOT / "projects/bigswing/manifest.json").read_text())
    meas = measure(man)
    if "--measure-only" in sys.argv:
        return
    if "--frames" in sys.argv:
        times = [float(v) for v in sys.argv[sys.argv.index("--frames") + 1].split(",")]
        r = Renderer(man, meas)
        (ROOT / "media/bigswing").mkdir(parents=True, exist_ok=True)
        for tv in times:
            Image.fromarray(r.frame_at(int(round(tv * man["fps"])))).save(ROOT / f"media/bigswing/smoke-{tv}.png")
        print("smoke frames: " + ", ".join(f"{tv}" for tv in times))
        return
    Renderer(man, meas).render(ROOT / "media/bigswing/footage.mp4")


if __name__ == "__main__":
    main()
