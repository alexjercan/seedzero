#!/usr/bin/env python3
"""Swim to the flag across a river: aim at the flag, or aim upstream?

Two panels on the same clock, the same river drawn the same way at the
same scale, seen from above: a river w metres wide with a uniform current
u everywhere (the same at the banks and in the middle), flowing down the
screen; two swimmers who both move at v relative to the water, both
starting on the near bank directly across from a flag on the far bank,
both let go at the same instant. x is the distance across, y the
distance downstream (the flag at (w, 0)). The flag swimmer (top panel)
always points straight at the flag: velocity v times the unit vector
toward the flag plus the current (0, u). The upstream swimmer (bottom
panel) holds one fixed heading theta = asin(u / v) upstream of straight
across, so the upstream part of the swimming speed, v sin(theta) = u,
cancels the current and the track is a straight line across at
sqrt(v^2 - u^2). Closed forms: the upstream swimmer lands after
w / sqrt(v^2 - u^2); the flag swimmer follows the pursuit curve
r(phi) = w cos^(k-1)(phi) / (1 + sin phi)^k with k = v / u (r the
distance to the flag, phi the heading upstream of straight across) and
lands after w v / (v^2 - u^2); its furthest downstream point is where
the velocity's downstream part is zero, sin(phi) = u / v. Both swimmers
are integrated by classical RK4 at dt (a half-step rerun as a check);
the flag swimmer stops when it is within stop_m of the flag and the
crossing is located by bisection inside the step; the last millimetre
is covered at the closing speed v - u (the track is tangent to the far
bank there). One run per video, shown at speedup x speed; both stand at
the flag at the end, the title fades back in and the scene crossfades
to its first frame over the last loop_fade seconds, so the last frame
equals the first. Deterministic, no seed.

Measured and printed: both landing times against the closed forms, the
half-step agreement, the upstream swimmer's deviation from the line,
the flag swimmer's furthest downstream point (RK4 against the closed
form), the track against the pursuit curve, where the flag swimmer is
when the upstream swimmer lands, both tracks at 5 s intervals, the flag
swimmer's heading against time, the other currents and the drifter for
the description, the schedule in video time, the on-screen text widths
and the layout clearances.

usage: riverswim.py [--measure-only] [--frames t1,t2,...]
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
WATER = (14, 34, 66)
FOAM = (170, 205, 230)
BANK = (46, 56, 44)
BANK_EDGE = (98, 112, 92)

# Layout: overlay at y 96..130 (captions.py), two title rows at y 190/252 for
# the first seconds, then the legend at y 236 and the shared clock at y 290;
# two bands stacked, the flag swimmer in y 330..880 and the upstream swimmer
# in y 880..1430, each drawn at 2x in its own layer; each band has its label
# row 40 px under the band top, its second row at 84 and its third at 120
# (left column from x 40, right column to x 1040); the river from 150 to 480
# px under the band top: the water x 265..815 (50 m at 11 px/m, flowing down
# the screen) between the near bank (x 40..265) and the far bank (x 815..1040);
# the start on the near bank's edge 250 px under the band top, the flag on
# the far bank's edge directly across; the gold event row at 518 (496..540);
# captions at caption_y 0.75 (y 1440..1530); the six-line card from y 1572
# at a 48 px pitch.
LEGEND_Y, CLOCK_Y = 236, 290
SS = 2
PAYOFF_Y, PAYOFF_PITCH = 1572.0, 48
PANELS = ("flag", "upstream")
BAND_Y = {"flag": 330, "upstream": 880}
BAND_H = 550
LABEL_DY, SUB_DY, FIX_DY = 40, 84, 120
EVENT_DY, EVENT_X = 518, 540
ROW_X0, ROW_X1 = 40, 1040
RIVER_X0, RIVER_X1 = 265, 815
BANK_X0, BANK_X1 = 40, 1040
WATER_DY0, WATER_DY1 = 150, 480
START_DY = 250
DOT_R, TICK_PX, RING_R = 5.0, 26.0, 11.0
CHEV_A, CHEV_B, CHEV_STROKE = 8.0, 6.0, 3.0
FLAG_POLE, FLAG_W, FLAG_H = 36.0, 26.0, 14.0
COLOUR = {"flag": CORAL, "upstream": TEAL}
READY, SWIM, LANDED = "ready", "swim", "landed"


def blend(col, a: float, base=BG) -> tuple:
    a = max(0.0, min(1.0, a))
    return tuple(int(round(c * a + b * (1 - a))) for c, b in zip(col, base))


def fmt1(y: float) -> str:
    """One decimal without a negative zero."""
    return f"{round(y, 1) + 0.0:.1f}"


# --- model -------------------------------------------------------------------
def pursuit_field(w: float, u: float, v: float):
    """Velocity of the swimmer who always points at the flag at (w, 0): v toward the flag plus the current."""
    def f(x: float, y: float) -> tuple[float, float]:
        dx, dy = w - x, -y
        r = math.hypot(dx, dy)
        if r == 0.0:
            return 0.0, u
        return v * dx / r, v * dy / r + u
    return f


def fixed_field(u: float, v: float, theta: float):
    """Velocity of the swimmer who holds the heading theta upstream of straight across."""
    vx, vy = v * math.cos(theta), u - v * math.sin(theta)

    def f(x: float, y: float) -> tuple[float, float]:
        return vx, vy
    return f


def rk4_step(f, x: float, y: float, h: float) -> tuple[float, float]:
    k1x, k1y = f(x, y)
    k2x, k2y = f(x + 0.5 * h * k1x, y + 0.5 * h * k1y)
    k3x, k3y = f(x + 0.5 * h * k2x, y + 0.5 * h * k2y)
    k4x, k4y = f(x + h * k3x, y + h * k3y)
    return x + h * (k1x + 2.0 * k2x + 2.0 * k3x + k4x) / 6.0, y + h * (k1y + 2.0 * k2y + 2.0 * k3y + k4y) / 6.0


def integrate(f, dt: float, stop=None, t_max: float | None = None, keep: int = 1) -> dict:
    """Integrate (x, y) from the start (0, 0) by classical RK4 at dt. stop(x, y) is negative before the end
    event and positive after it; the crossing is located by bisection inside the step. Without a stop the
    run ends at t_max. Every keep-th step is stored (the end point always)."""
    ts, xs, ys, vxs, vys = [0.0], [0.0], [0.0], [], []
    vx0, vy0 = f(0.0, 0.0)
    vxs.append(vx0)
    vys.append(vy0)
    x, y, n = 0.0, 0.0, 0
    t_end = None
    while True:
        xn, yn = rk4_step(f, x, y, dt)
        if stop is not None and stop(xn, yn) >= 0.0:
            lo, hi = 0.0, dt
            for _ in range(80):
                mid = 0.5 * (lo + hi)
                xm, ym = rk4_step(f, x, y, mid)
                if stop(xm, ym) < 0.0:
                    lo = mid
                else:
                    hi = mid
            xn, yn = rk4_step(f, x, y, hi)
            t_end = n * dt + hi
            n += 1
            ts.append(t_end)
            xs.append(xn)
            ys.append(yn)
            vx, vy = f(xn, yn)
            vxs.append(vx)
            vys.append(vy)
            break
        n += 1
        x, y = xn, yn
        if n % keep == 0 or (t_max is not None and n * dt >= t_max - 0.5 * dt):
            ts.append(n * dt)
            xs.append(x)
            ys.append(y)
            vx, vy = f(x, y)
            vxs.append(vx)
            vys.append(vy)
        if t_max is not None and n * dt >= t_max - 0.5 * dt:
            t_end = n * dt
            break
    return {"t": np.array(ts), "x": np.array(xs), "y": np.array(ys), "vx": np.array(vxs), "vy": np.array(vys),
            "t_end": t_end, "x_end": xs[-1], "y_end": ys[-1], "steps": n}


def pursuit_r(w: float, k: float, phi):
    """Closed-form pursuit curve: the distance to the flag at heading phi upstream of straight across."""
    return w * np.cos(phi) ** (k - 1.0) / (1.0 + np.sin(phi)) ** k


def pursuit_time(w: float, u: float, k: float, phi_end: float, n: int = 200000) -> float:
    """Time to reach heading phi_end on the pursuit curve: (w / u) int cos^(k-2) / (1 + sin)^k dphi (Simpson)."""
    phis = np.linspace(0.0, phi_end, n + 1)
    g = np.cos(phis) ** (k - 2.0) / (1.0 + np.sin(phis)) ** k
    h = phi_end / n
    return (w / u) * h / 3.0 * (g[0] + g[-1] + 4.0 * g[1:-1:2].sum() + 2.0 * g[2:-1:2].sum())


def furthest(run: dict) -> tuple[float, float, float]:
    """(t, x, y) where the downstream velocity changes sign on the RK4 table (linear in the step)."""
    vy = run["vy"]
    i = int(np.argmax(vy <= 0.0))
    assert i > 0 and vy[i - 1] > 0.0 >= vy[i]
    t0, t1 = run["t"][i - 1], run["t"][i]
    f = vy[i - 1] / (vy[i - 1] - vy[i])
    t = t0 + f * (t1 - t0)
    return t, float(np.interp(t, run["t"], run["x"])), float(np.interp(t, run["t"], run["y"]))


def heading_deg(w: float, x: float, y: float) -> float:
    return math.degrees(math.atan2(y, w - x))


def at(run: dict, t: float) -> tuple[float, float]:
    return float(np.interp(t, run["t"], run["x"])), float(np.interp(t, run["t"], run["y"]))


def pursuit_run(w: float, u: float, v: float, dt: float, stop_m: float, keep: int = 1) -> dict:
    """The flag swimmer by RK4 until within stop_m of the flag, with the landing time over the last stop_m
    at the closing speed v - u (the track is tangent to the far bank at the flag, so r' -> -(v - u))."""
    run = integrate(pursuit_field(w, u, v), dt, stop=lambda x, y: stop_m - math.hypot(w - x, y), keep=keep)
    run["t_land"] = run["t_end"] + stop_m / (v - u)
    return run


# --- measurement --------------------------------------------------------------
def measure(man: dict) -> dict:
    w, u, v = man["width_m"], man["current_m_s"], man["swim_m_s"]
    dt, stop_m = man["dt_s"], man["stop_m"]
    S, rel, D, fps, F = man["speedup"], man["release_at"], man["scene_duration"], man["fps"], man["loop_fade"]
    ppm = man["px_per_m"]
    for key in ("release_at", "loop_fade", "title_until", "payoff_t"):
        assert abs(man[key] * fps - round(man[key] * fps)) < 1e-9, f"{key} must be a whole number of frames"
    assert abs((RIVER_X1 - RIVER_X0) - w * ppm) < 1e-9, "the water must be w metres wide at px_per_m"
    k = v / u
    theta = math.asin(u / v)
    v_across = math.sqrt(v * v - u * u)
    T_B_cf = w / v_across
    T_A_cf = w * v / (v * v - u * u)
    ratio_cf = T_A_cf / T_B_cf
    print(f"setup: the same river in both panels, seen from above: {w:g} m wide with a uniform current of {u:g} m/s "
          f"everywhere (the same at the banks and in the middle), flowing down the screen; two swimmers who both move "
          f"at {v:g} m/s relative to the water (the current is {u / v:g} of their swimming speed, eight tenths), both "
          f"starting on the near bank directly across from a flag on the far bank, both let go at the same instant; "
          f"top panel the swimmer who always points straight at the flag (velocity {v:g} m/s toward the flag plus the "
          f"current), bottom panel the swimmer who holds one fixed heading asin(u / v) = {math.degrees(theta):.2f} "
          f"degrees upstream of straight across; both integrated by classical RK4 at dt = {dt:g} s (a half-step rerun "
          f"as a check), the flag swimmer stopped within {stop_m * 1000:g} mm of the flag by bisection inside the step; "
          f"shown at {S:g}x speed, one run per video with the start {rel:g} s into the {D:g} s scene; drawn at {ppm:g} "
          f"px per metre ({w * ppm:.0f} px of water); deterministic, no seed")
    # The upstream swimmer: closed form and RK4.
    B = integrate(fixed_field(u, v, theta), dt, stop=lambda x, y: x - w)
    B_half = integrate(fixed_field(u, v, theta), 0.5 * dt, stop=lambda x, y: x - w, keep=2)
    ydev = float(np.max(np.abs(B["y"])))
    print(f"aim upstream (bottom panel): heading theta = asin({u:g} / {v:g}) = {math.degrees(theta):.3f} degrees "
          f"upstream of straight across; the upstream part of the swimming speed v sin(theta) = {v * math.sin(theta):.4f} "
          f"m/s cancels the current {u:g} m/s, the across part v cos(theta) = sqrt(v^2 - u^2) = {v_across:.4f} m/s; "
          f"closed form w / sqrt(v^2 - u^2) = {T_B_cf:.4f} s; RK4: lands at {B['t_end']:.6f} s (diff "
          f"{B['t_end'] - T_B_cf:+.1e} s), {B['steps']} steps, the track stays within {ydev:.1e} m of the straight "
          f"line (|downstream| under 1e-9 m: {'yes' if ydev < 1e-9 else 'NO'}); half-step rerun (dt = {0.5 * dt:g} s): "
          f"lands at {B_half['t_end']:.6f} s ({B_half['t_end'] - B['t_end']:+.1e} s); on screen 'at the flag: "
          f"{B['t_end']:.0f} s' = {B['t_end']:.1f} s = eighty three seconds")
    assert abs(B["t_end"] - T_B_cf) < 1e-6 and ydev < 1e-9 and abs(B_half["t_end"] - B["t_end"]) < 1e-3
    # The flag swimmer: RK4 against the pursuit curve.
    A = pursuit_run(w, u, v, dt, stop_m)
    A_half = pursuit_run(w, u, v, 0.5 * dt, stop_m, keep=2)
    T_A = A["t_land"]
    t_far, x_far, y_far = furthest(A)
    t_far_h, x_far_h, y_far_h = furthest(A_half)
    phi_far = theta                                    # sin(phi) = u / v where the downstream velocity is zero
    r_far_cf = float(pursuit_r(w, k, phi_far))
    y_far_cf, x_far_cf = r_far_cf * math.sin(phi_far), w - r_far_cf * math.cos(phi_far)
    t_far_cf = pursuit_time(w, u, k, phi_far)
    phis = np.arctan2(A["y"], w - A["x"])
    r_tab = np.hypot(w - A["x"], A["y"])
    r_cf_err = np.abs(r_tab - pursuit_r(w, k, phis))
    r_err = float(np.max(r_cf_err[r_tab > 1.0]))          # phi is ill-conditioned in the last metre (w - x at round-off)
    r_err10 = float(np.max(r_cf_err[r_tab > 10.0]))
    ratio = T_A / B["t_end"]
    print(f"aim at the flag (top panel): RK4 from the start: within {stop_m * 1000:g} mm of the flag at {A['t_end']:.6f} s "
          f"({A['steps']} steps; there the heading is {heading_deg(w, A['x_end'], A['y_end']):.6f} degrees upstream and the "
          f"closing speed v - u = {v - u:g} m/s, so the last {stop_m * 1000:g} mm take {stop_m / (v - u):.4f} s); lands at "
          f"{T_A:.6f} s (closed form w v / (v^2 - u^2) = {T_A_cf:.6f} s, diff {T_A - T_A_cf:+.1e} s); "
          f"{ratio:.4f} times the upstream swimmer's {B['t_end']:.4f} s (closed form v / sqrt(v^2 - u^2) = {ratio_cf:.4f}), "
          f"{T_A - B['t_end']:.2f} s longer, nearly twice as long; on screen 'at the flag: {T_A:.0f} s' = {T_A:.1f} s = "
          f"one hundred thirty nine seconds; {ratio:.1f} times longer on the card; furthest downstream {y_far:.4f} m at "
          f"{t_far:.4f} s, {x_far:.4f} m across, heading {heading_deg(w, x_far, y_far):.3f} degrees upstream (the downstream "
          f"velocity -v sin(phi) + u is zero at sin(phi) = u / v, the same angle the upstream swimmer holds; closed form "
          f"r = w cos^(k-1)(phi) / (1 + sin phi)^k = {r_far_cf:.4f} m from the flag, {y_far_cf:.4f} m downstream and "
          f"{x_far_cf:.4f} m across, diffs {y_far - y_far_cf:+.1e} and {x_far - x_far_cf:+.1e} m; the time by quadrature "
          f"{t_far_cf:.4f} s, diff {t_far - t_far_cf:+.1e} s); swept {y_far:.1f} m downstream first = {y_far * ppm:.1f} px; "
          f"the RK4 track stays within {r_err10:.1e} m of the pursuit curve r(phi) while more than 10 m from the flag and within "
          f"{r_err:.1e} m while more than 1 m from it (k = v / u = {k:g}; nearer the flag the heading phi from (w - x, y) is "
          f"ill-conditioned, w - x being at round-off, so the curve is not evaluated there); "
          f"half-step rerun (dt = {0.5 * dt:g} s): lands at {A_half['t_land']:.6f} s ({A_half['t_land'] - T_A:+.1e} s), "
          f"furthest {y_far_h:.6f} m at {t_far_h:.6f} s ({y_far_h - y_far:+.1e} m, {t_far_h - t_far:+.1e} s)")
    assert abs(T_A - T_A_cf) < 1e-4 and abs(A_half["t_land"] - T_A) < 1e-3 and r_err < 1e-6
    assert abs(y_far - y_far_cf) < 1e-6 and abs(t_far - t_far_cf) < 1e-3
    # Where the flag swimmer is when the upstream swimmer lands.
    xb, yb = at(A, B["t_end"])
    rb = math.hypot(w - xb, yb)
    hb = heading_deg(w, xb, yb)
    print(f"when the upstream swimmer lands at {B['t_end']:.2f} s the flag swimmer is {xb:.2f} m across, {yb:.2f} m downstream, "
          f"{rb:.2f} m from the flag, heading {hb:.1f} degrees upstream (almost straight into the current), with "
          f"{T_A - B['t_end']:.2f} s still to swim; its net speed then is {math.hypot(*pursuit_field(w, u, v)(xb, yb)):.4f} m/s")
    # Tracks at table_step_s intervals.
    step = man["table_step_s"]

    def track_line(run: dict, T: float, fixed_heading: float | None) -> str:
        times = [j * step for j in range(int(math.floor(T / step)) + 1)] + [T]
        parts = []
        for tt in times:
            x, y = at(run, tt) if tt < T else (w, 0.0 if fixed_heading is not None else 0.0)
            if tt >= T:
                x, y = w, 0.0
            h = fixed_heading if fixed_heading is not None else (heading_deg(w, x, y) if tt < T else 90.0)
            parts.append(f"{tt:.1f} s: {x:.2f} across, {fmt1(y)} down, {h:.1f} deg")
        return "; ".join(parts)

    print(f"track of the flag swimmer (time: m across, m downstream, heading in degrees upstream): "
          + track_line(A, T_A, None))
    print(f"track of the upstream swimmer (time: m across, m downstream, heading): "
          + track_line(B, B["t_end"], math.degrees(theta)))
    # Heading against time.
    hd = np.degrees(phis)
    marks = []
    for hm in man["heading_marks_deg"]:
        tm = float(np.interp(hm, hd, A["t"]))
        xm, ym = at(A, tm)
        marks.append(f"{hm:g} degrees at {tm:.2f} s ({xm:.2f} m across, {ym:.2f} m downstream)")
    print(f"heading of the flag swimmer against time (degrees upstream of straight across, rising from 0 at the start "
          f"to 90 at the flag, monotone: {'yes' if np.all(np.diff(hd) >= -1e-9) else 'NO'}): " + "; ".join(marks)
          + f"; it is swept downstream while the heading is under {math.degrees(theta):.2f} degrees (until {t_far:.2f} s) and "
          f"crawls back up the far bank after; it reaches {w - 0.1:.1f} m across at {float(np.interp(w - 0.1, A['x'], A['t'])):.2f} s "
          f"and {w - 0.01:.2f} m across at {float(np.interp(w - 0.01, A['x'], A['t'])):.2f} s")
    ev: dict = {"A": A, "B": B, "T_A": T_A, "T_B": B["t_end"], "theta": theta, "ratio": ratio, "t_far": t_far,
                "x_far": x_far, "y_far": y_far, "others": {}}
    # Other currents and the drifter, for the description.
    descr = []
    for u2 in man["description_currents_m_s"]:
        o: dict = {"u": u2}
        if u2 < v:
            th2 = math.asin(u2 / v)
            va2 = math.sqrt(v * v - u2 * u2)
            tb2 = w / va2
            B2 = integrate(fixed_field(u2, v, th2), dt, stop=lambda x, y: x - w, keep=100)
            A2 = pursuit_run(w, u2, v, dt, stop_m, keep=100)
            ta2_cf = w * v / (v * v - u2 * u2)
            tf2, xf2, yf2 = furthest(A2)
            k2 = v / u2
            yf2_cf = float(pursuit_r(w, k2, th2)) * math.sin(th2)
            o.update({"t_b": B2["t_end"], "t_a": A2["t_land"], "y_far": yf2, "theta": math.degrees(th2)})
            descr.append(f"current {u2:g} m/s: aim upstream {math.degrees(th2):.1f} degrees, across at {va2:.4f} m/s, lands "
                         f"at {B2['t_end']:.2f} s (closed form {tb2:.4f} s, diff {B2['t_end'] - tb2:+.1e}); aim at the flag "
                         f"lands at {A2['t_land']:.2f} s (closed form {ta2_cf:.4f} s, diff {A2['t_land'] - ta2_cf:+.1e}), "
                         f"{A2['t_land'] / B2['t_end']:.2f} times longer, swept {yf2:.2f} m downstream at {tf2:.1f} s "
                         f"(closed form {yf2_cf:.4f} m, diff {yf2 - yf2_cf:+.1e})")
        else:
            T_run = man["never_lands_run_s"]
            A2 = integrate(pursuit_field(w, u2, v), dt, t_max=T_run, keep=100)
            r2 = np.hypot(w - A2["x"], A2["y"])
            lim = (w, w / 2.0)
            dlim = np.hypot(lim[0] - A2["x"], lim[1] - A2["y"])
            t_mm = float(A2["t"][int(np.argmax(dlim < 1e-3))])
            sp = math.hypot(*pursuit_field(w, u2, v)(A2["x_end"], A2["y_end"]))
            o.update({"x_end": A2["x_end"], "y_end": A2["y_end"], "r_end": float(r2[-1])})
            descr.append(f"current {u2:g} m/s, equal to the swim speed: aim upstream needs asin({u2:g}) = "
                         f"{math.degrees(math.asin(u2 / v)):.0f} degrees, straight into the current, across at "
                         f"{math.sqrt(max(0.0, v * v - u2 * u2)):.1f} m/s: swimming in place, it never crosses; aim at the "
                         f"flag never lands: after {T_run:g} s it is {A2['x_end']:.4f} m across and {A2['y_end']:.4f} m "
                         f"downstream, {r2[-1]:.4f} m from the flag, moving at {sp:.1e} m/s (the limit point is (w, w / 2) = "
                         f"({lim[0]:g}, {lim[1]:g}) m, half the width downstream: r(phi) = w / (1 + sin phi) at k = 1; it is "
                         f"within 1 mm of the limit from {t_mm:.1f} s and {dlim[-1]:.1e} m from it at {T_run:g} s; the "
                         f"distance to the flag never drops under {float(r2.min()):.4f} m)")
        ev["others"][u2] = o
    Dr = integrate(fixed_field(u, v, 0.0), dt, stop=lambda x, y: x - w, keep=100)
    descr.append(f"the drifter who points straight across and lets the current take it: lands {Dr['y_end']:.1f} m downstream "
                 f"after {Dr['t_end']:.1f} s (closed form w / v = {w / v:.1f} s and u w / v = {u * w / v:.1f} m)")
    ev["drifter"] = Dr
    print("for the description: " + "; ".join(descr))
    # The schedule in video time.
    vt = lambda real: rel + real / S   # noqa: E731
    hold_end = D - F
    per_px = man["chevron_period_m"] * ppm
    drift_px_s = u * ppm * S
    cycles = drift_px_s * D / per_px
    print(f"schedule (video time, {S:g}x speed): both start at {rel:g} s; the flag swimmer is furthest downstream at "
          f"{vt(t_far):.2f} s ({y_far:.1f} m, the gold furthest rows light in both bands); the upstream swimmer lands at "
          f"{vt(B['t_end']):.2f} s (its event row lights) with the flag swimmer {rb:.1f} m from the flag; the flag swimmer "
          f"passes {w - 0.1:.1f} m across at {vt(float(np.interp(w - 0.1, A['x'], A['t']))):.2f} s and lands at {vt(T_A):.2f} s "
          f"(its event row lights); both stand at the flag to {hold_end:.2f} s; the title fades back in and the scene "
          f"crossfades to its first frame over {hold_end:.2f} to {D:.2f} s; title until {man['title_until']:g} s; payoff card "
          f"from {man['payoff_t']:g} s; the current's chevrons drift {drift_px_s:.1f} px per video second ({u * S:g} m/s "
          f"of video) on a {per_px:.0f} px period, {cycles:.0f} periods in {D:g} s (exact: {abs(cycles - round(cycles)) < 1e-9}), "
          f"so the water phase at the last frame equals the first; each chevron is smeared over one frame's travel "
          f"({drift_px_s / fps:.3f} px)")
    assert vt(T_A) < hold_end - 4.0, "the flag swimmer must land well before the fade"
    assert abs(cycles - round(cycles)) < 1e-9, "the chevron drift must be periodic over the scene"
    # Text widths.
    font = os.environ["SEED_ZERO_FONT"]
    f24, f28, f34, f40, f56 = (ImageFont.truetype(font, n) for n in (24, 28, 34, 40, 56))
    widths = {"overlay@34": (f34, man["overlay"])}
    for j, line in enumerate(man["title"].split("|")):
        widths[f"title line {j + 1}@56"] = (f56, line)
    widths["legend@40"] = (f40, legend_text(man))
    widths["clock@28"] = (f28, clock_text(ev, 123.4))
    widths["clock before@28"] = (f28, clock_text(ev, -1.0))
    widths["clock landed@28"] = (f28, clock_text(ev, 200.0))
    for m in PANELS:
        widths[f"label {m}@40"] = (f40, label_text(ev, m))
        widths[f"sublabel {m}@28"] = (f28, sub_text(man))
        widths[f"furthest {m}@28"] = (f28, furthest_text(ev, m))
        widths[f"event {m}@40"] = (f40, event_text(ev, m))
    widths["downstream@28"] = (f28, down_text(y_far))
    widths["to the flag@28"] = (f28, flag_text(w))
    widths["heading@28"] = (f28, heading_text(90.0))
    widths["start@24"] = (f24, "start")
    widths["flag@24"] = (f24, "flag")
    for j, line in enumerate(payoff_lines(man, ev)):
        widths[f"payoff line {j + 1}@40"] = (f40, line)
    print("text widths (the on-screen strings verbatim): " + ", ".join(f"{kk} {f.getlength(s):.0f} px '{s}'"
                                                                     for kk, (f, s) in widths.items()))
    assert all(f.getlength(s) < 950 for f, s in widths.values()), "a text line is wider than 950 px"
    assert len(payoff_lines(man, ev)) <= 6, "the card has more than six lines"
    # Layout checks.
    rows = {
        "label": (max(f40.getlength(label_text(ev, m)) for m in PANELS), f28.getlength(down_text(y_far))),
        "second": (f28.getlength(sub_text(man)), f28.getlength(flag_text(w))),
        "third": (f28.getlength(heading_text(90.0)), max(f28.getlength(furthest_text(ev, m)) for m in PANELS)),
    }
    gaps = {name: (ROW_X1 - rw) - (ROW_X0 + lw) for name, (lw, rw) in rows.items()}
    rows_bottom = FIX_DY + 16
    far_px = START_DY + y_far * ppm
    dot_bottom = far_px + DOT_R + 1.0
    tick_top = START_DY - TICK_PX
    flag_top = START_DY - FLAG_POLE
    ev_w = max(f40.getlength(event_text(ev, m)) for m in PANELS)
    ev_x0, ev_x1 = EVENT_X - ev_w / 2.0, EVENT_X + ev_w / 2.0
    start_x1 = RIVER_X0 - 14
    start_x0 = start_x1 - f24.getlength("start")
    flag_x0 = RIVER_X1 + 19
    flag_x1 = flag_x0 + f24.getlength("flag")
    card_bottom = PAYOFF_Y + (len(payoff_lines(man, ev)) - 1) * PAYOFF_PITCH + 20
    print(f"row check: left and right columns end and start at x {ROW_X0 + rows['label'][0]:.0f} / {ROW_X1 - rows['label'][1]:.0f} "
          f"(label row, gap {gaps['label']:.0f} px), {ROW_X0 + rows['second'][0]:.0f} / {ROW_X1 - rows['second'][1]:.0f} (second "
          f"row, gap {gaps['second']:.0f} px), {ROW_X0 + rows['third'][0]:.0f} / {ROW_X1 - rows['third'][1]:.0f} (third row, gap "
          f"{gaps['third']:.0f} px); the rows end {rows_bottom} px under the band top; the river spans {WATER_DY0} to {WATER_DY1} "
          f"px under the band top, the water x {RIVER_X0} to {RIVER_X1} ({w:g} m at {ppm:g} px/m) between the banks x {BANK_X0} "
          f"to {RIVER_X0} and {RIVER_X1} to {BANK_X1}; the start at x {RIVER_X0}, {START_DY} px under the band top, the flag at x "
          f"{RIVER_X1} with its pole up to {flag_top:.0f} px and its pennant to x {RIVER_X1 + FLAG_W:.0f}; the flag swimmer's track "
          f"bows to {far_px:.1f} px under the band top ({y_far * ppm:.1f} px downstream of the line) and its dot to {dot_bottom:.1f} "
          f"px, above the water's bottom row {WATER_DY1} and the event row (spans {EVENT_DY - 22} to {EVENT_DY + 22} px under the "
          f"band top, x {ev_x0:.0f} to {ev_x1:.0f}, widest {ev_w:.0f} px); the heading tick reaches {tick_top:.0f} px at most "
          f"(straight upstream), under the rows; the dots stay between x {RIVER_X0 - DOT_R:.0f} and {RIVER_X1 + RING_R:.0f}; the "
          f"'start' label spans x {start_x0:.0f} to {start_x1:.0f} on the near bank and 'flag' x {flag_x0:.0f} to {flag_x1:.0f} on "
          f"the far bank; each band is {BAND_H} px tall (y {BAND_Y['flag']} to {BAND_Y['flag'] + BAND_H} and {BAND_Y['upstream']} "
          f"to {BAND_Y['upstream'] + BAND_H}); the caption band starts at y {int(man['caption_y'] * H)}; the card runs from y "
          f"{PAYOFF_Y:.0f} to {card_bottom:.0f}; the title rows end at y {252 + 28} and the overlay band ends at y 130")
    assert all(g > 40 for g in gaps.values()), "the columns meet"
    assert WATER_DY0 > rows_bottom + 10, "the river meets the text rows"
    assert dot_bottom < WATER_DY1 - 10 and dot_bottom < EVENT_DY - 22 - 10, "the track leaves the water or meets the event row"
    assert tick_top > WATER_DY0 + 10 and flag_top > WATER_DY0 + 10, "the tick or the flag leaves the water rows"
    assert EVENT_DY - 22 >= WATER_DY1 + 10 and EVENT_DY + 22 < BAND_H - 6, "the event row meets the river or leaves the band"
    assert start_x0 > BANK_X0 and flag_x1 < BANK_X1 - 10, "a bank label leaves its bank"
    assert RIVER_X1 + RING_R < flag_x0 - 4, "the landed ring meets the flag label"
    assert BAND_Y["upstream"] + BAND_H <= int(man["caption_y"] * H), "the bottom band reaches the caption band"
    assert PAYOFF_Y - 20 > int(man["caption_y"] * H) + 90 and card_bottom < H - 40, "the card meets the caption band or the frame"
    assert 252 + 28 < BAND_Y["flag"], "the title rows reach the first band"
    return ev


def legend_text(man: dict) -> str:
    return f"same river, same swimmers, {man['speedup']:g}x speed"


def clock_text(ev: dict, r: float) -> str:
    if r < 0.0:
        return "before the start"
    if r >= ev["T_A"]:
        return f"{ev['T_A']:.1f} s: both at the flag"
    return f"{r:.1f} s after the start"


def label_text(ev: dict, m: str) -> str:
    if m == "flag":
        return "aims at the flag"
    return f"aims {math.degrees(ev['theta']):.0f} degrees upstream"


def sub_text(man: dict) -> str:
    return f"swims {man['swim_m_s']:.1f} m/s, current {man['current_m_s']:.1f} m/s"


def down_text(y: float) -> str:
    return f"{fmt1(y)} m downstream"


def flag_text(r: float) -> str:
    return f"{r:.0f} m to the flag"


def heading_text(h: float) -> str:
    return f"heading {h:.0f} degrees upstream"


def furthest_text(ev: dict, m: str) -> str:
    y = ev["y_far"] if m == "flag" else 0.0
    return f"furthest: {fmt1(y)} m downstream"


def event_text(ev: dict, m: str) -> str:
    T = ev["T_A"] if m == "flag" else ev["T_B"]
    return f"at the flag: {T:.0f} s"


def payoff_lines(man: dict, ev: dict) -> list[str]:
    o = ev["others"]
    u1, u2 = man["description_currents_m_s"][0], man["description_currents_m_s"][1]
    text = man["payoff_text"].format(
        t_b=ev["T_B"], t_a=ev["T_A"], ratio=ev["ratio"], ymax=ev["y_far"], theta=math.degrees(ev["theta"]),
        sinth=math.sin(ev["theta"]), u1=u1, tb1=o[u1]["t_b"], ta1=o[u1]["t_a"], u2=u2, tb2=o[u2]["t_b"], ta2=o[u2]["t_a"])
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
        self.font_tiny = ImageFont.truetype(font, 24)
        self.ppm = float(man["px_per_m"])
        self.S = man["speedup"]
        self.rel = man["release_at"]
        self.w, self.u, self.v = man["width_m"], man["current_m_s"], man["swim_m_s"]
        self.runs = {"flag": ev["A"], "upstream": ev["B"]}
        self.T = {"flag": ev["T_A"], "upstream": ev["T_B"]}
        self.theta = ev["theta"]
        self.per_px = man["chevron_period_m"] * self.ppm
        self.drift_px_s = self.u * self.ppm * self.S
        self.first: np.ndarray | None = None
        # Trail samples every 0.05 s of real time (the frame step is 1 / fps * speedup real seconds).
        self.trail = {}
        for m, run in self.runs.items():
            ts = np.arange(0.0, self.T[m], 0.05)
            self.trail[m] = (ts, np.interp(ts, run["t"], run["x"]), np.interp(ts, run["t"], run["y"]))

    @staticmethod
    def L_(x: float, y: float) -> tuple[float, float]:
        """Layer (2x) pixel of a band-local point, rounded to 1e-4 px so equal states draw equal pixels."""
        return round(x * SS, 4), round(y * SS, 4)

    def px(self, x: float, y: float) -> tuple[float, float]:
        """Band-local pixel of a point in metres (x across, y downstream)."""
        return RIVER_X0 + x * self.ppm, START_DY + y * self.ppm

    def real_time(self, t: float) -> float:
        return (t - self.rel) * self.S

    def state(self, m: str, r: float) -> dict:
        w = self.w
        run, T = self.runs[m], self.T[m]
        if r <= 0.0:
            x, y, phase = 0.0, 0.0, READY
        elif r >= T:
            x, y, phase = w, 0.0, LANDED
        else:
            x, y = at(run, r)
            phase = SWIM
        if m == "upstream":
            h = math.degrees(self.theta)
        else:
            h = 90.0 if phase == LANDED else heading_deg(w, x, y)
        return {"x": x, "y": y, "phase": phase, "heading": h, "r": r, "to_flag": math.hypot(w - x, y)}

    # --- drawing ----------------------------------------------------------
    @staticmethod
    def dashed(d: ImageDraw.ImageDraw, p0, p1, fill, width: int, dash: float, gap: float) -> None:
        (x0, y0), (x1, y1) = p0, p1
        length = math.hypot(x1 - x0, y1 - y0)
        ux, uy = (x1 - x0) / length, (y1 - y0) / length
        s = 0.0
        while s < length:
            e = min(length, s + dash)
            d.line((x0 + ux * s, y0 + uy * s, x0 + ux * e, y0 + uy * e), fill=fill, width=width)
            s = e + gap

    def water_layer(self, t: float) -> Image.Image:
        """The water with the current's chevrons drifting downstream, each smeared over one frame's travel."""
        wl = Image.new("RGB", ((RIVER_X1 - RIVER_X0) * SS, (WATER_DY1 - WATER_DY0) * SS), WATER)
        d = ImageDraw.Draw(wl)
        per = self.per_px
        travel = self.drift_px_s / self.fps
        drift = (self.drift_px_s * t) % per
        s = CHEV_STROKE + travel
        col = blend(FOAM, 0.26 * CHEV_STROKE / s, WATER)
        hgt = WATER_DY1 - WATER_DY0
        ncol = self.man["chevron_columns"]
        for kcol in range(ncol):
            cx = (kcol + 0.5) * (RIVER_X1 - RIVER_X0) / ncol
            y = (drift + (kcol * 23.0) % per) % per - per
            while y < hgt + per:
                pts = [(cx - CHEV_A, y - CHEV_B), (cx, y), (cx + CHEV_A, y - CHEV_B),
                       (cx + CHEV_A, y - CHEV_B + s), (cx, y + s), (cx - CHEV_A, y - CHEV_B + s)]
                d.polygon([self.L_(px, py) for px, py in pts], fill=col)
                y += per
        return wl

    def scene(self, m: str, t: float) -> tuple[Image.Image, dict]:
        """The band layer of panel m at video time t."""
        layer = Image.new("RGB", (W * SS, BAND_H * SS), BG)
        d = ImageDraw.Draw(layer)
        L = self.L_
        # Banks and water.
        d.rectangle((*L(BANK_X0, WATER_DY0), *L(RIVER_X0, WATER_DY1)), fill=BANK)
        d.rectangle((*L(RIVER_X1, WATER_DY0), *L(BANK_X1, WATER_DY1)), fill=BANK)
        layer.paste(self.water_layer(t), (RIVER_X0 * SS, WATER_DY0 * SS))
        d.line((*L(RIVER_X0, WATER_DY0), *L(RIVER_X0, WATER_DY1)), fill=BANK_EDGE, width=2 * SS)
        d.line((*L(RIVER_X1, WATER_DY0), *L(RIVER_X1, WATER_DY1)), fill=BANK_EDGE, width=2 * SS)
        # The straight reference line from the start to the flag.
        self.dashed(d, L(*self.px(0.0, 0.0)), L(*self.px(self.w, 0.0)), blend(TEXT, 0.38, WATER), 2 * SS, 9 * SS, 8 * SS)
        r = self.real_time(t)
        st = self.state(m, r)
        col = COLOUR[m]
        # The trail up to now.
        ts, xs, ys = self.trail[m]
        if st["phase"] != READY:
            n = int(np.searchsorted(ts, min(r, self.T[m]), side="right"))
            pts = [L(*self.px(float(x), float(y))) for x, y in zip(xs[:n], ys[:n])]
            pts.append(L(*self.px(st["x"], st["y"])))
            if len(pts) >= 2:
                d.line(pts, fill=col, width=4 * SS, joint="curve")
        # The furthest point of the flag swimmer, a gold mark once reached (the rows light with it).
        if m == "flag" and r >= self.ev["t_far"]:
            fx, fy = L(*self.px(self.ev["x_far"], self.ev["y_far"]))
            rr = 4 * SS
            d.ellipse((fx - rr, fy - rr, fx + rr, fy + rr), fill=GOLD)
        # The start ring and the flag.
        sx, sy = L(*self.px(0.0, 0.0))
        rr = 7 * SS
        d.ellipse((sx - rr, sy - rr, sx + rr, sy + rr), outline=WHITE, width=2 * SS)
        fx, fy = self.px(self.w, 0.0)
        d.line((*L(fx, fy), *L(fx, fy - FLAG_POLE)), fill=GOLD, width=3 * SS)
        d.polygon([L(fx, fy - FLAG_POLE), L(fx + FLAG_W, fy - FLAG_POLE + FLAG_H / 2.0), L(fx, fy - FLAG_POLE + FLAG_H)],
                  fill=GOLD)
        # The swimmer: a dot with a heading tick, or a ring once landed.
        X, Y = self.px(st["x"], st["y"])
        if st["phase"] == LANDED:
            cx, cy = L(X, Y)
            rr = RING_R * SS
            d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), outline=col, width=2 * SS)
        else:
            h = math.radians(st["heading"])
            tx, ty = X + TICK_PX * math.cos(h), Y - TICK_PX * math.sin(h)
            d.line((*L(X, Y), *L(tx, ty)), fill=blend(col, 0.85, WATER), width=3 * SS)
        cx, cy = L(X, Y)
        rr = DOT_R * SS
        d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), fill=col, outline=BG, width=SS)
        return layer, st

    def draw_text(self, d: ImageDraw.ImageDraw, states: dict, hud_alpha: float, t: float) -> None:
        man, ev = self.man, self.ev
        r = self.real_time(t)
        for m, st in states.items():
            y0 = BAND_Y[m]
            d.text((ROW_X0, y0 + LABEL_DY), label_text(ev, m), font=self.font, fill=COLOUR[m], anchor="lm")
            d.text((ROW_X0, y0 + SUB_DY), sub_text(man), font=self.font_small, fill=MUTED, anchor="lm")
            d.text((ROW_X0, y0 + FIX_DY), heading_text(st["heading"]), font=self.font_small, fill=MUTED, anchor="lm")
            d.text((ROW_X1, y0 + LABEL_DY), down_text(st["y"]), font=self.font_small, fill=TEXT, anchor="rm")
            d.text((ROW_X1, y0 + SUB_DY), flag_text(st["to_flag"]), font=self.font_small, fill=TEXT, anchor="rm")
            if r >= ev["t_far"]:
                d.text((ROW_X1, y0 + FIX_DY), furthest_text(ev, m), font=self.font_small, fill=GOLD, anchor="rm")
            if st["phase"] == LANDED:
                d.text((EVENT_X, y0 + EVENT_DY), event_text(ev, m), font=self.font, fill=GOLD, anchor="mm")
            d.text((RIVER_X0 - 14, y0 + START_DY), "start", font=self.font_tiny, fill=blend(WHITE, 0.8, BANK), anchor="rm")
            d.text((RIVER_X1 + 19, y0 + START_DY), "flag", font=self.font_tiny, fill=GOLD, anchor="lm")
        if hud_alpha > 0.02:
            d.text((W / 2, LEGEND_Y), legend_text(man), font=self.font, fill=blend(TEXT, hud_alpha), anchor="mm")
            d.text((W / 2, CLOCK_Y), clock_text(ev, r), font=self.font_small, fill=blend(MUTED, hud_alpha), anchor="mm")

    def live_frame(self, f: int) -> np.ndarray:
        man = self.man
        t = f / self.fps
        if t < man["title_until"]:
            title_alpha = 1.0 if t < man["title_until"] - 0.4 else (man["title_until"] - t) / 0.4
            hud_alpha = 0.0
        else:
            title_alpha = 0.0
            hud_alpha = min(1.0, (t - man["title_until"]) / 0.4)
        img = Image.new("RGB", (W, H), BG)
        states = {}
        for m in PANELS:
            layer, states[m] = self.scene(m, t)
            img.paste(layer.reduce(SS), (0, BAND_Y[m]))
        d = ImageDraw.Draw(img)
        self.draw_text(d, states, hud_alpha, t)
        if title_alpha > 0.0:
            for j, line in enumerate(man["title"].split("|")):
                d.text((W / 2, 190 + j * 62), line, font=self.font_title, fill=blend(TEXT, title_alpha), anchor="mm")
        if t >= man["payoff_t"]:
            a = min(1.0, (t - man["payoff_t"]) / man["payoff_hold"])
            for j, line in enumerate(payoff_lines(man, self.ev)):
                d.text((W / 2, PAYOFF_Y + j * PAYOFF_PITCH), line, font=self.font, fill=blend(GOLD, a), anchor="mm")
        return np.asarray(img, dtype=np.float32)

    def frame_at(self, f: int) -> np.ndarray:
        man = self.man
        total = int(round(man["scene_duration"] * self.fps))
        live = self.live_frame(f)
        fade_frames = int(round(man["loop_fade"] * self.fps))
        if f >= total - fade_frames:
            # A single run: the whole frame crossfades to the first frame (title included), so the last
            # frame equals the first exactly.
            if self.first is None:
                self.first = self.live_frame(0)
            a = (f - (total - fade_frames) + 1) / fade_frames
            live = live * (1 - a) + self.first * a
        return live.astype(np.uint8)

    def render(self, out_path: Path) -> None:
        global _RENDERER
        out_path.parent.mkdir(parents=True, exist_ok=True)
        total = int(round(self.man["scene_duration"] * self.fps))
        fade_frames = int(round(self.man["loop_fade"] * self.fps))
        first = self.frame_at(0)
        last = self.frame_at(total - 1)
        diff = np.abs(first.astype(int) - last.astype(int))
        print(f"loop check: last frame differs from the first in {int((diff.max(axis=2) > 24).sum())} px "
              f"(max channel difference {int(diff.max())})")
        pre = self.frame_at(total - fade_frames - 1)
        diff = np.abs(first.astype(int) - pre.astype(int))
        print(f"fade check: the last live frame before the fade ({(total - fade_frames - 1) / self.fps:.3f} s) differs from "
              f"the first in {int((diff.max(axis=2) > 24).sum())} px (max channel difference {int(diff.max())}); the fade "
              f"blends it into the first frame over {fade_frames} frames (a single-run scene)")
        mid = self.frame_at(total - fade_frames // 2)
        diff = np.abs(first.astype(int) - mid.astype(int))
        print(f"fade check: the mid-fade frame differs from the first in {int((diff.max(axis=2) > 24).sum())} px "
              f"(max channel difference {int(diff.max())})")
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
        workers = min(12, os.cpu_count() or 1)
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
    man = json.loads((ROOT / "projects/riverswim/manifest.json").read_text())
    ev = measure(man)
    if "--measure-only" in sys.argv:
        return
    if "--frames" in sys.argv:
        times = [float(v) for v in sys.argv[sys.argv.index("--frames") + 1].split(",")]
        r = Renderer(man, ev)
        (ROOT / "media/riverswim").mkdir(parents=True, exist_ok=True)
        for tv in times:
            Image.fromarray(r.frame_at(int(round(tv * man["fps"])))).save(ROOT / f"media/riverswim/smoke-{tv}.png")
        print("smoke frames: " + ", ".join(f"{tv}" for tv in times))
        return
    Renderer(man, ev).render(ROOT / "media/riverswim/footage.mp4")


if __name__ == "__main__":
    main()
