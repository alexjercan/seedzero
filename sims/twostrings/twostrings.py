#!/usr/bin/env python3
"""Inertia ball: pull slowly or jerk it, which string snaps?

Two panels on the same clock, the same ball and the same strings drawn the
same way at the same scale: a ball of mass m hangs from a fixed hook on a
string of stiffness k; an identical string hangs from the ball's underside
down to a hand. Each string is a massless linear spring that carries
tension only (slack when shorter than its free length) and snaps the
instant its tension reaches F (F / k of stretch, chosen numbers for a thin
cord). A small damping c acts on the ball while it hangs from the top
string (it stands for the string's loss); g = 9.80665. At rest the top
string carries m g and the bottom string is just taut at zero tension. x is
the ball's downward displacement from that rest; the hand moves down at a
steady V from t = 0, so the top tension is f1 = m g + k x, the bottom
tension f2 = k (V t - x) (zero if negative), and

    m x'' = f2 - (f1 - m g) - c x' = k V t - 2 k x - c x'.

Top panel, a slow pull: the ball follows the hand at about half its speed
(quasi-static x = V t / 2), both tensions rise together, but the top one
starts m g ahead because it carries the ball, so it reaches F first. Bottom
panel, a jerk: the bottom string stretches F / k before the ball's inertia
lets it move (x = k V t^3 / (6 m) for a still ball), so the bottom string
reaches F first and the top string never gets far past m g. After the top
snaps the ball falls, pulled by gravity and by the bottom string until that
goes slack as the ball outruns the hand, then free fall (no drag); it drops
out of the band. After the bottom snaps the ball wobbles on the top string
(m x'' = -k x - c x', period 2 pi sqrt(m / k), damped) and the hand carries
on down with the broken piece and leaves the band. The pull is integrated
by RK4 at steps_per_second with each snap located by bisection inside the
step and checked against the quasi-static estimate 2 (F - m g) / (k V) for
the slow pull, F / (k V) and the cubic for the jerk, a half-step rerun and
a no-damping rerun; the drawing follows the RK4 tables.

Drawing rule (stretch drawn stretch_draw_x = 20 times): while a string is
intact the ball is drawn at its rest position plus 20 x and the hand at its
string's anchor plus 20 (V t - x) plus the ball's drawn offset, so the hand
is drawn 20 V t under its rest while both strings hold; after a string
snaps the free bodies continue from where they are drawn at true scale (the
ball's fall after the top snaps, the hand's run after the bottom snaps);
the ball still hanging on the top string after the bottom snaps keeps the
20x rule (its wobble). When the bottom string goes slack after the top
snap, the hand opens and steps aside (the slack string no longer acts on
the ball and the model has no collision); the slack string is drawn limp
under the falling ball. The run repeats every cycle_s seconds of video with
a crossfade back to the resting setup; the cycle divides the scene length,
so the scene is exactly periodic and the last frame equals the first. Shown
at 1/slow speed. Deterministic, no seed.

Measured and printed: the rest state and the snap thresholds, the slow pull
(which string, when, the ball's sink, the other tension) against the
quasi-static estimate, the jerk against F / (k V) and the cubic, the
half-step and no-damping reruns, the fall after the top snap (slack time,
peak bottom tension, when the ball leaves the band) and the wobble after
the bottom snap (amplitude, period, the top tension's peak, when the hand
leaves the band), the other speeds and the crossover for the description,
the schedule in video time, the on-screen text widths and the layout
clearances.

usage: twostrings.py [--measure-only] [--frames t1,t2,...]
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
SKY = (110, 170, 230)
GOLD = (240, 176, 84)
CORAL = (232, 96, 88)
TEXT = (216, 222, 230)
MUTED = (138, 148, 163)
WHITE = (236, 240, 244)
DECK_A = (30, 36, 46)
RIM = (96, 108, 126)
STEEL = (150, 160, 176)
BALL = (204, 210, 222)
BALL_RIM = (120, 128, 142)
HAND = (214, 178, 142)
HAND_DARK = (150, 118, 90)

# Layout: overlay at y 96..130 (captions.py), two title rows at y 190/252 for
# the first seconds, then the legend at y 236 and the shared clock at y 290;
# two panels stacked, the slow pull in the band y 330..880 and the jerk in
# y 880..1430, each drawn at 2x in its own geometry layer (so the falling
# ball and the departing hand are clipped at their band); each band has its
# label row 40 px under the band top, its second row at 84 and its third at
# 120 (left column from x 40); the hook, strings, ball and hand on the
# column x string_x_px; the two tension bars at the right (x 856 and 972,
# from 140 to 440 px under the band top, 12 px per newton) with the gold
# break line and the weight tick; the gold event rows at 300 and 346 under
# the band top in the left column; captions at caption_y 0.75 (y
# 1440..1530); the six-line card from y 1572 at a 48 px pitch.
LEGEND_Y, CLOCK_Y = 236, 290
SS = 2
PAYOFF_Y, PAYOFF_PITCH = 1572.0, 48
PANELS = ("slow", "jerk")
BAND_Y = {"slow": 330, "jerk": 880}
BAND_H = 550
LABEL_DY, SUB_DY, FIX_DY = 40, 84, 120
EVENT_DY = (300, 346)
ROW_X0, ROW_X1 = 40, 1040
BAR_X = {"top": 856, "bottom": 972}
BAR_W, BAR_TOP, BAR_BOT, BAR_N = 36, 140, 440, 25.0
BAR_PX_PER_N = (BAR_BOT - BAR_TOP) / BAR_N
HAND_W, HAND_H, HAND_GAP, HAND_ASIDE, STUB = 70, 60, 16, 70, 22
STRING_W = 3
COLOUR = {"slow": TEAL, "jerk": SKY}
HELD, PULL, FALL, WOBBLE = "held", "pull", "fall", "wobble"
TOP, BOTTOM = "top", "bottom"


def blend(col, a: float, base=BG) -> tuple:
    a = max(0.0, min(1.0, a))
    return tuple(int(round(c * a + b * (1 - a))) for c, b in zip(col, base))


def smoother(u: float) -> float:
    u = max(0.0, min(1.0, u))
    return u * u * (3.0 - 2.0 * u)


# --- measurement --------------------------------------------------------------
def rk4_pull(V: float, m: float, k: float, F: float, c: float, g: float, dt: float) -> dict:
    """Integrate m x'' = f2 - k x - c x' with f2 = max(0, k (V t - x)) from rest by classical RK4 at
    dt until a tension reaches F; the snap is located by bisection on the last step. Returns the
    table (t, x, v), the snap state and which string went."""

    def f2_of(t: float, x: float) -> float:
        return max(0.0, k * (V * t - x))

    def acc(t: float, x: float, v: float) -> float:
        return (f2_of(t, x) - k * x - c * v) / m

    def step(t: float, x: float, v: float, h: float) -> tuple[float, float]:
        k1x, k1v = v, acc(t, x, v)
        k2x, k2v = v + 0.5 * h * k1v, acc(t + 0.5 * h, x + 0.5 * h * k1x, v + 0.5 * h * k1v)
        k3x, k3v = v + 0.5 * h * k2v, acc(t + 0.5 * h, x + 0.5 * h * k2x, v + 0.5 * h * k2v)
        k4x, k4v = v + h * k3v, acc(t + h, x + h * k3x, v + h * k3v)
        return x + h * (k1x + 2.0 * k2x + 2.0 * k3x + k4x) / 6.0, v + h * (k1v + 2.0 * k2v + 2.0 * k3v + k4v) / 6.0

    def peak(t: float, x: float) -> float:
        return max(m * g + k * x, f2_of(t, x))

    ts, xt, vt = [0.0], [0.0], [0.0]
    x, v, n = 0.0, 0.0, 0
    while True:
        t = n * dt
        xn, vn = step(t, x, v, dt)
        if peak(t + dt, xn) >= F:
            lo, hi = 0.0, dt
            for _ in range(80):
                mid = 0.5 * (lo + hi)
                xm, _ = step(t, x, v, mid)
                if peak(t + mid, xm) < F:
                    lo = mid
                else:
                    hi = mid
            xs, vs = step(t, x, v, hi)
            t_s = t + hi
            f1, f2 = m * g + k * xs, f2_of(t_s, xs)
            ts.append(t_s)
            xt.append(xs)
            vt.append(vs)
            n += 1
            break
        n += 1
        x, v = xn, vn
        ts.append(n * dt)
        xt.append(x)
        vt.append(v)
        assert n < 10_000_000, "no snap"
    return {"t": np.array(ts), "x": np.array(xt), "v": np.array(vt), "t_snap": t_s, "x_snap": xs, "v_snap": vs,
            "f1_snap": f1, "f2_snap": f2, "which": TOP if f1 >= f2 else BOTTOM, "steps": n, "V": V, "m": m, "k": k,
            "F": F, "c": c, "g": g, "dt": dt}


def rk4_fall(run: dict) -> None:
    """After the top string snaps: m x'' = m g + f2 (no drag) from the snap state until the bottom
    string goes slack (V t - x = 0, located by bisection); then free fall. Adds the table and the
    slack state to the run."""
    V, m, k, g, dt = run["V"], run["m"], run["k"], run["g"], run["dt"]

    def acc(t: float, x: float) -> float:
        return g + max(0.0, k * (V * t - x)) / m

    def step(t: float, x: float, v: float, h: float) -> tuple[float, float]:
        k1x, k1v = v, acc(t, x)
        k2x, k2v = v + 0.5 * h * k1v, acc(t + 0.5 * h, x + 0.5 * h * k1x)
        k3x, k3v = v + 0.5 * h * k2v, acc(t + 0.5 * h, x + 0.5 * h * k2x)
        k4x, k4v = v + h * k3v, acc(t + h, x + h * k3x)
        return x + h * (k1x + 2.0 * k2x + 2.0 * k3x + k4x) / 6.0, v + h * (k1v + 2.0 * k2v + 2.0 * k3v + k4v) / 6.0

    t, x, v = run["t_snap"], run["x_snap"], run["v_snap"]
    ts, xt, vt, f2t = [t], [x], [v], [k * (V * t - x)]
    f2_max = f2t[0]
    while True:
        xn, vn = step(t, x, v, dt)
        if V * (t + dt) - xn <= 0.0:
            lo, hi = 0.0, dt
            for _ in range(80):
                mid = 0.5 * (lo + hi)
                xm, _ = step(t, x, v, mid)
                if V * (t + mid) - xm > 0.0:
                    lo = mid
                else:
                    hi = mid
            xs, vs = step(t, x, v, hi)
            t += hi
            ts.append(t)
            xt.append(xs)
            vt.append(vs)
            f2t.append(0.0)
            break
        t += dt
        x, v = xn, vn
        f2 = k * (V * t - x)
        f2_max = max(f2_max, f2)
        ts.append(t)
        xt.append(x)
        vt.append(v)
        f2t.append(f2)
    run["fall"] = {"t": np.array(ts), "x": np.array(xt), "v": np.array(vt), "f2": np.array(f2t)}
    run["t_slack"], run["x_slack"], run["v_slack"], run["f2_max_after"] = t, xs, vs, f2_max


def rk4_wobble(run: dict, run_s: float) -> None:
    """After the bottom string snaps: m x'' = -k x - c x' on the top string alone from the snap
    state for run_s seconds. Adds the table, the amplitude, the period and the top tension's peak."""
    m, k, c, g, dt = run["m"], run["k"], run["c"], run["g"], run["dt"]

    def acc(x: float, v: float) -> float:
        return (-k * x - c * v) / m

    def step(x: float, v: float, h: float) -> tuple[float, float]:
        k1x, k1v = v, acc(x, v)
        k2x, k2v = v + 0.5 * h * k1v, acc(x + 0.5 * h * k1x, v + 0.5 * h * k1v)
        k3x, k3v = v + 0.5 * h * k2v, acc(x + 0.5 * h * k2x, v + 0.5 * h * k2v)
        k4x, k4v = v + h * k3v, acc(x + h * k3x, v + h * k3v)
        return x + h * (k1x + 2.0 * k2x + 2.0 * k3x + k4x) / 6.0, v + h * (k1v + 2.0 * k2v + 2.0 * k3v + k4v) / 6.0

    n = int(round(run_s / dt))
    t0, x, v = run["t_snap"], run["x_snap"], run["v_snap"]
    xt, vt = [x], [v]
    for _ in range(n):
        x, v = step(x, v, dt)
        xt.append(x)
        vt.append(v)
    xa, va = np.array(xt), np.array(vt)
    ta = t0 + np.arange(n + 1) * dt
    # Maxima of x by parabolic vertex; the period from the first two.
    peaks = []
    for i in range(1, n):
        if xa[i] >= xa[i - 1] and xa[i] > xa[i + 1]:
            a, b, c_ = xa[i - 1], xa[i], xa[i + 1]
            den = a - 2.0 * b + c_
            off = 0.0 if den == 0.0 else 0.5 * (a - c_) / den
            peaks.append((ta[i] + off * dt, b - 0.25 * (a - c_) * off))
            if len(peaks) >= 3:
                break
    run["wobble"] = {"t": ta, "x": xa, "v": va}
    run["amp"] = float(np.max(np.abs(xa)))
    run["x_peak"], run["t_peak"] = peaks[0][1], peaks[0][0]
    run["period"] = peaks[1][0] - peaks[0][0]
    run["f1_peak"] = m * g + k * float(np.max(xa))
    run["f1_max_t"] = float(ta[int(np.argmax(xa))])


def state_at(run: dict, rt: float) -> dict:
    """(x, v, f1, f2, hand, phase) of a panel rt real seconds after the pull starts."""
    V, m, k, g = run["V"], run["m"], run["k"], run["g"]
    if rt < 0.0:
        return {"x": 0.0, "v": 0.0, "f1": m * g, "f2": 0.0, "hand": 0.0, "phase": HELD, "slack": False}
    if rt < run["t_snap"]:
        x = float(np.interp(rt, run["t"], run["x"]))
        v = float(np.interp(rt, run["t"], run["v"]))
        return {"x": x, "v": v, "f1": m * g + k * x, "f2": max(0.0, k * (V * rt - x)), "hand": V * rt, "phase": PULL,
                "slack": False}
    if run["which"] == TOP:
        fa = run["fall"]
        if rt < run["t_slack"]:
            x = float(np.interp(rt, fa["t"], fa["x"]))
            v = float(np.interp(rt, fa["t"], fa["v"]))
            return {"x": x, "v": v, "f1": 0.0, "f2": max(0.0, k * (V * rt - x)), "hand": V * rt, "phase": FALL,
                    "slack": False}
        d = rt - run["t_slack"]
        return {"x": run["x_slack"] + run["v_slack"] * d + 0.5 * g * d * d, "v": run["v_slack"] + g * d, "f1": 0.0,
                "f2": 0.0, "hand": V * rt, "phase": FALL, "slack": True}
    wb = run["wobble"]
    assert rt <= wb["t"][-1] + 1e-9, "the wobble table is too short"
    x = float(np.interp(rt, wb["t"], wb["x"]))
    v = float(np.interp(rt, wb["t"], wb["v"]))
    return {"x": x, "v": v, "f1": m * g + k * x, "f2": 0.0, "hand": V * rt, "phase": WOBBLE, "slack": False}


def geometry(man: dict) -> dict:
    """Band-local drawing constants (px)."""
    r = float(man["ball_r_px"])
    ball0 = man["hook_dy"] + man["top_string_px"] + r
    grip0 = ball0 + r + man["bottom_string_px"]
    return {"cx": float(man["string_x_px"]), "r": r, "hook": float(man["hook_dy"]), "ball0": ball0, "grip0": grip0,
            "ppm": float(man["px_per_m"]), "exp": float(man["stretch_draw_x"]) * float(man["px_per_m"])}


def ball_dy(run: dict, st: dict, geo: dict) -> float:
    """The ball's drawn centre under the band top: rest + 20 x while the top string holds, true
    scale from the drawn snap position after it snaps."""
    if st["phase"] == FALL:
        return geo["ball0"] + geo["exp"] * run["x_snap"] + geo["ppm"] * (st["x"] - run["x_snap"])
    return geo["ball0"] + geo["exp"] * st["x"]


def grip_dy(run: dict, st: dict, geo: dict) -> float:
    """The hand's pinch point under the band top: 20 V t under its rest while both strings hold,
    true scale from the drawn snap position after a snap."""
    if st["phase"] in (HELD, PULL):
        return geo["grip0"] + geo["exp"] * st["hand"]
    return geo["grip0"] + geo["exp"] * run["V"] * run["t_snap"] + geo["ppm"] * (st["hand"] - run["V"] * run["t_snap"])


def measure(man: dict) -> dict:
    g, m, k, F, c = man["g"], man["mass_kg"], man["stiffness_n_m"], man["break_n"], man["damping_n_s_m"]
    V_s, V_j = man["speed_m_s"]["slow"], man["speed_m_s"]["jerk"]
    dt = 1.0 / man["steps_per_second"]
    S, P, D, fps, Fd, pa = man["slow"], man["cycle_s"], man["scene_duration"], man["fps"], man["reset_fade"], man["release_at"]
    cycles = D / P
    assert abs(cycles - round(cycles)) < 1e-9, "the cycle must divide the scene length"
    for key in ("cycle_s", "release_at", "first_cycle_at", "reset_fade"):
        assert abs(man[key] * fps - round(man[key] * fps)) < 1e-9, f"{key} must be a whole number of frames"
    geo = geometry(man)
    print(f"setup: the same ball and the same strings in both panels: a ball of m = {m:g} kg hangs from a fixed hook on a "
          f"string of stiffness k = {k:g} N/m; an identical string hangs from the ball's underside down to a hand; each "
          f"string is a massless linear spring that carries tension only (slack when shorter than its free length) and "
          f"snaps the instant its tension reaches F = {F:g} N ({F / k * 1000:g} mm of stretch; chosen numbers for a thin "
          f"cord), {F / (m * g):.2f} times the ball's weight; a small damping c = {c:g} N s/m on the ball while it hangs "
          f"from the top string (chosen); g = {g:g} m/s^2; x is the ball's downward displacement from rest and the hand "
          f"moves down at a steady V from t = 0: f1 = m g + k x, f2 = k (V t - x), m x'' = k V t - 2 k x - c x'; top "
          f"panel pulled at V = {V_s:g} m/s, bottom panel jerked at V = {V_j:g} m/s; integrated by RK4 at "
          f"{man['steps_per_second']} steps per second (dt = {dt:.0e} s) with the snap located by bisection inside the "
          f"step, checked against the quasi-static estimate 2 (F - m g) / (k V), the jerk's F / (k V) and the cubic "
          f"k V t^3 / (6 m), a half-step rerun and a no-damping rerun; after the top snaps the ball falls with the bottom "
          f"string's pull until it goes slack, then freely (no drag); after the bottom snaps the ball wobbles on the top "
          f"string (m x'' = -k x - c x'); shown at 1/{S:g} speed on a {P:g} s cycle ({P * fps:.0f} frames) with the pull "
          f"starting {pa:g} s into the cycle, {cycles:.0f} cycles in {D:g} s; drawn at {geo['ppm']:g} px per metre with "
          f"the stretch drawn {man['stretch_draw_x']:g}x; deterministic, no seed")
    x_rest = m * g / k
    x_top = (F - m * g) / k
    s_bot = F / k
    T_both = 2.0 * math.pi * math.sqrt(m / (2.0 * k))
    T_top = 2.0 * math.pi * math.sqrt(m / k)
    print(f"rest: the top string carries m g = {m * g:.3f} N, stretched m g / k = {x_rest * 1000:.3f} mm; the bottom string "
          f"is just taut at 0 N; the top string snaps when x = (F - m g) / k = {x_top * 1000:.4f} mm, the bottom when "
          f"V t - x = F / k = {s_bot * 1000:.3f} mm; the ball's natural period on both strings 2 pi sqrt(m / 2 k) = "
          f"{T_both * 1000:.2f} ms, on the top string alone 2 pi sqrt(m / k) = {T_top * 1000:.2f} ms; damping rate "
          f"c / (2 m) = {c / (2.0 * m):g} per second")
    # The slow pull.
    slow = rk4_pull(V_s, m, k, F, c, g, dt)
    assert slow["which"] == TOP, "the slow pull did not snap the top string"
    rk4_fall(slow)
    half_s = rk4_pull(V_s, m, k, F, c, g, 0.5 * dt)
    nod_s = rk4_pull(V_s, m, k, F, 0.0, g, dt)
    t_qs = 2.0 * (F - m * g) / (k * V_s)
    lag = V_s * slow["t_snap"] / 2.0 - slow["x_snap"]
    ball_gone_dy = BAND_H + 2.0 + geo["r"] + STUB          # the ball's top and its string stub past the band bottom
    x_gone = slow["x_snap"] + (ball_gone_dy - geo["ball0"] - geo["exp"] * slow["x_snap"]) / geo["ppm"]
    if x_gone <= slow["x_slack"]:
        t_gone = float(np.interp(x_gone, slow["fall"]["x"], slow["fall"]["t"]))
    else:
        vs = slow["v_slack"]
        t_gone = slow["t_slack"] + (-vs + math.sqrt(vs * vs + 2.0 * g * (x_gone - slow["x_slack"]))) / g
    slow["t_gone"] = t_gone
    print(f"slow pull (top panel, V = {V_s:g} m/s = {V_s * 100:g} cm/s): the top string snaps at {slow['t_snap'] * 1000:.3f} ms "
          f"= {slow['t_snap']:.4f} s with the ball {slow['x_snap'] * 1000:.4f} mm down (moving at {slow['v_snap'] * 1000:.2f} "
          f"mm/s) and the hand {V_s * slow['t_snap'] * 1000:.3f} mm down; the top string at {slow['f1_snap']:.3f} N, the "
          f"bottom string at {slow['f2_snap']:.3f} N; quasi-static estimate 2 (F - m g) / (k V) = {t_qs * 1000:.3f} ms "
          f"(x = V t / 2; the ball lags V t / 2 by {lag * 1000:.3f} mm at the snap, which is the "
          f"{(slow['t_snap'] - t_qs) * 1000:.3f} ms gap); {slow['steps']} steps; half-step rerun (dt = {0.5 * dt:.0e} s): "
          f"{half_s['t_snap'] * 1000:.4f} ms ({(half_s['t_snap'] - slow['t_snap']) * 1000:+.1e} ms), ball "
          f"{half_s['x_snap'] * 1000:.4f} mm; no damping: top at {nod_s['t_snap'] * 1000:.3f} ms, ball "
          f"{nod_s['x_snap'] * 1000:.4f} mm, bottom {nod_s['f2_snap']:.3f} N; after the snap the bottom string pulls the "
          f"falling ball (its tension peaks at {slow['f2_max_after']:.3f} N, under {F:g} N, so it never snaps) until it goes "
          f"slack {(slow['t_slack'] - slow['t_snap']) * 1000:.2f} ms later at {slow['t_slack'] * 1000:.3f} ms with the ball "
          f"{slow['x_slack'] * 1000:.3f} mm down at {slow['v_slack']:.3f} m/s; then free fall: the ball's drawn top is out "
          f"of the band at {t_gone:.4f} s real = {S * t_gone:.2f} s video after the pull starts")
    assert abs(slow["t_snap"] - half_s["t_snap"]) < 1e-6 and abs(slow["x_snap"] - x_top) < 1e-9
    assert slow["f2_max_after"] < F
    # The jerk.
    jerk = rk4_pull(V_j, m, k, F, c, g, dt)
    assert jerk["which"] == BOTTOM, "the jerk did not snap the bottom string"
    rk4_wobble(jerk, man["wobble_run_s"])
    half_j = rk4_pull(V_j, m, k, F, c, g, 0.5 * dt)
    nod_j = rk4_pull(V_j, m, k, F, 0.0, g, dt)
    t_cf = F / (k * V_j)
    cubic = lambda t: k * V_j * t ** 3 / (6.0 * m)   # noqa: E731
    omega = math.sqrt(k / m)
    amp_est = math.sqrt(jerk["x_snap"] ** 2 + (jerk["v_snap"] / omega) ** 2)
    hand_gone_dy = BAND_H + 2.0 + STUB                      # the stub on the hand past the band bottom
    grip_snap = geo["grip0"] + geo["exp"] * V_j * jerk["t_snap"]
    t_hand_gone = jerk["t_snap"] + (hand_gone_dy - grip_snap) / geo["ppm"] / V_j
    jerk["t_gone"] = t_hand_gone
    print(f"jerk (bottom panel, V = {V_j:g} m/s): the bottom string snaps at {jerk['t_snap'] * 1000:.3f} ms = "
          f"{jerk['t_snap']:.4f} s with the ball {jerk['x_snap'] * 1000:.4f} mm down (moving at {jerk['v_snap'] * 1000:.1f} "
          f"mm/s) and the hand {V_j * jerk['t_snap'] * 1000:.3f} mm down; the bottom string at {jerk['f2_snap']:.3f} N, the "
          f"top string at {jerk['f1_snap']:.3f} N; closed form with the ball still F / (k V) = {t_cf * 1000:.3f} ms; the "
          f"cubic k V t^3 / (6 m) gives {cubic(t_cf) * 1000:.4f} mm at {t_cf * 1000:.3f} ms and {cubic(jerk['t_snap']) * 1000:.4f} "
          f"mm at {jerk['t_snap'] * 1000:.3f} ms; {jerk['steps']} steps ({S * jerk['t_snap'] * fps:.2f} frames of video); "
          f"half-step rerun: {half_j['t_snap'] * 1000:.4f} ms ({(half_j['t_snap'] - jerk['t_snap']) * 1000:+.1e} ms), ball "
          f"{half_j['x_snap'] * 1000:.4f} mm; no damping: bottom at {nod_j['t_snap'] * 1000:.3f} ms, ball "
          f"{nod_j['x_snap'] * 1000:.4f} mm, top {nod_j['f1_snap']:.3f} N; after the snap the ball wobbles on the top string: "
          f"amplitude {jerk['amp'] * 1000:.3f} mm (the ball's speed at the snap over omega = sqrt(k / m) = {omega:.2f} per "
          f"second gives sqrt(x^2 + (v / omega)^2) = {amp_est * 1000:.3f} mm), first peak {jerk['x_peak'] * 1000:.3f} mm at "
          f"{jerk['t_peak'] * 1000:.2f} ms, period {jerk['period'] * 1000:.2f} ms (closed form {T_top * 1000:.2f} ms), the "
          f"top tension peaks at {jerk['f1_peak']:.3f} N (never {F:g} N); the hand carries on at {V_j:g} m/s with the broken "
          f"piece and is out of the band at {t_hand_gone:.4f} s real = {S * t_hand_gone:.2f} s video after the pull starts")
    assert abs(jerk["t_snap"] - half_j["t_snap"]) < 1e-6 and abs(jerk["t_snap"] - t_cf) < 1e-4
    assert abs(jerk["period"] - T_top) < 1e-3 and jerk["f1_peak"] < F
    ev: dict = {"runs": {"slow": slow, "jerk": jerk}, "x_top": x_top, "s_bot": s_bot}
    # Other speeds and the crossover, for the description.
    descr = []
    for V in man["description_speeds_m_s"]:
        r0 = rk4_pull(V, m, k, F, c, g, dt)
        other = r0["f2_snap"] if r0["which"] == TOP else r0["f1_snap"]
        descr.append(f"{V:g} m/s: the {r0['which']} string at {r0['t_snap'] * 1000:.3f} ms, ball {r0['x_snap'] * 1000:.4f} mm, "
                     f"the other string at {other:.3f} N")
    lo, hi = man["crossover_bracket_m_s"]
    assert rk4_pull(lo, m, k, F, c, g, dt)["which"] == TOP and rk4_pull(hi, m, k, F, c, g, dt)["which"] == BOTTOM
    ev["v_lo"], ev["v_hi"] = lo, hi
    for _ in range(24):
        mid = 0.5 * (lo + hi)
        if rk4_pull(mid, m, k, F, c, g, dt)["which"] == TOP:
            lo = mid
        else:
            hi = mid
    ev["v_cross"] = 0.5 * (lo + hi)
    nod_lo, nod_hi = ev["v_lo"], ev["v_hi"]
    for _ in range(24):
        mid = 0.5 * (nod_lo + nod_hi)
        if rk4_pull(mid, m, k, F, 0.0, g, dt)["which"] == TOP:
            nod_lo = mid
        else:
            nod_hi = mid
    print("for the description: " + "; ".join(descr) + f"; the crossover (top below, bottom above) sits between "
          f"{ev['v_lo']:g} and {ev['v_hi']:g} m/s, bisected to {ev['v_cross']:.4f} m/s with c = {c:g} ({0.5 * (nod_lo + nod_hi):.4f} "
          f"m/s with no damping); it depends on k, F and c")
    # The schedule in video time.
    t0 = man["first_cycle_at"]
    k0 = math.ceil((0.0 - t0) / P - 1e-9) - 1
    k1 = math.floor((D - t0) / P - 1e-9)
    starts = [t0 + kk * P for kk in range(k0, k1 + 1)]
    ev["cycles"] = int(round(cycles))

    def lst(off_: float) -> str:
        return ", ".join(f"{st + off_:.2f}" for st in starts if 0.0 <= st + off_ < D)

    vt = lambda real: pa + real * S   # noqa: E731  video time after the cycle start
    gone_s, gone_j = vt(slow["t_gone"]), vt(jerk["t_gone"])
    assert gone_s < P - Fd, "the fallen ball is still in the band at the reset fade"
    assert gone_j < P - Fd, "the departing hand is still in the band at the reset fade"
    assert (P - pa) / S <= jerk["t_snap"] + man["wobble_run_s"], "the wobble table does not cover the cycle"
    tau0 = (0.0 - t0) % P
    r0 = (tau0 - pa) / S
    st0 = {p: state_at(ev["runs"][p], r0) for p in PANELS}
    print(f"schedule (video time, 1/{S:g} speed): cycles of {P:g} s start at " + ", ".join(f"{st:.2f}" for st in starts)
          + f" s (the first {-t0:.2f} s before the first frame); the pull starts {pa:g} s into each cycle at {lst(pa)} s; "
          f"the slow pull's top string snaps {S * slow['t_snap']:.2f} s after the pull at {lst(vt(slow['t_snap']))} s (the "
          f"event row lights, the ball falls at true scale), its bottom string goes slack at {lst(vt(slow['t_slack']))} s "
          f"(the hand opens and steps aside over {man['hand_aside_s']:g} s) and the ball is out of the band "
          f"{S * (slow['t_gone'] - slow['t_snap']):.2f} s after the snap at {lst(gone_s)} s ({gone_s:.2f} s into the cycle, "
          f"before the fade at {P - Fd:.2f} s); the jerk's bottom string snaps {S * jerk['t_snap']:.3f} s = "
          f"{S * jerk['t_snap'] * fps:.1f} frames after the pull at {lst(vt(jerk['t_snap']))} s (the event row lights, the "
          f"broken ends recoil over {man['recoil_s']:g} s, the flash lasts {man['flash_s']:g} s) and the hand is out of the "
          f"band at {lst(gone_j)} s ({gone_j:.2f} s into the cycle); the ball's wobble period is {S * jerk['period']:.2f} s "
          f"of video; the reset crossfade runs over the last {Fd:g} s of each cycle (from {lst(P - Fd)} s; the readouts "
          f"out over its first half and in over its second); on the first frame the cycle is {tau0:.2f} s in ({r0:.3f} s "
          f"real after the pull starts: the slow panel {st0['slow']['phase']} at {st0['slow']['x'] * 1000:.3f} mm, the "
          f"jerk panel {st0['jerk']['phase']} at {st0['jerk']['x'] * 1000:.3f} mm); title until {man['title_until']:g} s; "
          f"payoff card from {man['payoff_t']:g} s; the title fades back in over the last {man['loop_fade']:g} s and the "
          f"last frame repeats the first (the scene is periodic: {D:g} s holds exactly {cycles:.0f} cycles)")
    # The on-screen texts that quote the measurements.
    print("on screen: the event rows read " + " / ".join("'" + " ".join(event_lines(ev, p)) + "'" for p in PANELS)
          + "; the readouts freeze at " + " / ".join(f"'{ball_text(ev['runs'][p]['x_snap'])}, "
          f"{hand_text(ev['runs'][p]['V'] * ev['runs'][p]['t_snap'])}'" for p in PANELS)
          + "; the card reads: " + " | ".join(payoff_lines(man, ev)))
    # Text widths.
    font = os.environ["SEED_ZERO_FONT"]
    f24, f28, f34, f40, f56 = (ImageFont.truetype(font, n) for n in (24, 28, 34, 40, 56))
    widths = {"overlay@34": (f34, man["overlay"])}
    for j, line in enumerate(man["title"].split("|")):
        widths[f"title line {j + 1}@56"] = (f56, line)
    widths["legend@40"] = (f40, legend_text(man))
    widths["clock@28"] = (f28, clock_text(slow["t_snap"]))
    widths["clock held@28"] = (f28, clock_text(-1.0))
    for p in PANELS:
        widths[f"label {p}@40"] = (f40, label_text(man, p))
        widths[f"ball moved {p}@28"] = (f28, ball_text(ev["runs"][p]["x_snap"]))
        widths[f"hand moved {p}@28"] = (f28, hand_text(ev["runs"][p]["V"] * ev["runs"][p]["t_snap"]))
        for j, line in enumerate(event_lines(ev, p)):
            widths[f"event {p} line {j + 1}@40"] = (f40, line)
    widths["break@24"] = (f24, break_text(man))
    widths["weight@24"] = (f24, weight_text(man))
    widths["bar value@24"] = (f24, bar_value_text(20.0))
    widths["snapped@24"] = (f24, "snapped")
    widths["bar top@24"] = (f24, "top")
    widths["bar bottom@24"] = (f24, "bottom")
    for j, line in enumerate(payoff_lines(man, ev)):
        widths[f"payoff line {j + 1}@40"] = (f40, line)
    print("text widths: " + ", ".join(f"{kk} {f.getlength(s):.0f} px" for kk, (f, s) in widths.items()))
    assert all(f.getlength(s) < 950 for f, s in widths.values()), "a text line is wider than 950 px"
    assert len(payoff_lines(man, ev)) <= 6, "the card has more than six lines"
    # Layout checks.
    left = ROW_X0 + max(max(f40.getlength(label_text(man, p)), f28.getlength(ball_text(0.0)), f28.getlength(hand_text(0.0)),
                            max(f40.getlength(s) for s in event_lines(ev, p))) for p in PANELS)
    cx, r = geo["cx"], geo["r"]
    hand_x1 = cx + HAND_GAP + HAND_W + HAND_ASIDE
    weight_x0 = BAR_X["top"] - 24.0 - f24.getlength(weight_text(man))
    grip_slow = geo["grip0"] + geo["exp"] * V_s * slow["t_snap"]
    grip_jerk = geo["grip0"] + geo["exp"] * V_j * jerk["t_snap"]
    ball_slow = geo["ball0"] + geo["exp"] * slow["x_snap"]
    wobble_px = geo["exp"] * jerk["amp"]
    bar_x1 = BAR_X["bottom"] + BAR_W
    print(f"row check: the left column ends at x {left:.0f} px; the ball column spans x {cx - r:.0f} to {cx + r:.0f} px and "
          f"the hand x {cx:.0f} to {cx + HAND_GAP + HAND_W:.0f} px ({hand_x1:.0f} px when it steps aside); the weight label "
          f"starts at x {weight_x0:.0f} px and the bars span x {BAR_X['top']} to {bar_x1} px from {BAR_TOP} to {BAR_BOT} px "
          f"under the band top ({BAR_PX_PER_N:g} px per newton; the break line {BAR_BOT - F * BAR_PX_PER_N:.0f} px under "
          f"the band top, the weight tick {BAR_BOT - m * g * BAR_PX_PER_N:.0f} px); the hook at {geo['hook']:.0f} px, the "
          f"ball's centre at rest {geo['ball0']:.0f} px and the pinch point {geo['grip0']:.0f} px under the band top; at "
          f"the slow snap the ball's centre is drawn {ball_slow:.1f} px and the pinch point {grip_slow:.1f} px under the "
          f"band top (the hand's lowest pixel {grip_slow + HAND_H - 12:.0f} px); at the jerk's snap the pinch point is "
          f"{grip_jerk:.1f} px under the band top and the ball's drawn wobble is {wobble_px:.1f} px; the event rows at "
          f"{EVENT_DY[0]} and {EVENT_DY[1]} px under the band top; each band is {BAND_H} px tall (y {BAND_Y['slow']} to "
          f"{BAND_Y['slow'] + BAND_H} and {BAND_Y['jerk']} to {BAND_Y['jerk'] + BAND_H}); the caption band starts at y "
          f"{int(man['caption_y'] * H)}; the title rows end at y {252 + 28} and the overlay band ends at y 130")
    pair = 0.5 * (f24.getlength("snapped") + f24.getlength(bar_value_text(20.0)))
    assert pair < BAR_X[BOTTOM] - BAR_X[TOP] - 8, "the bar value labels meet"
    assert cx - r > left + 20, "the ball column meets the left column"
    assert hand_x1 < weight_x0 - 8, "the hand meets the weight label"
    assert grip_slow + HAND_H - 12 < BAND_H - 4, "the slow pull's hand leaves the band"
    assert grip_jerk + HAND_H - 12 < BAND_H - 4, "the jerk's hand leaves the band before the snap"
    assert geo["hook"] > 8 and ball_slow + r < geo["grip0"] + 20, "the ball meets the hand at rest"
    assert EVENT_DY[1] + 22 < BAND_H - 10 and EVENT_DY[0] - 22 > FIX_DY + 16, "the event rows do not fit"
    assert BAND_Y["jerk"] + BAND_H <= int(man["caption_y"] * H), "the bottom band reaches the caption band"
    assert PAYOFF_Y - 20 > int(man["caption_y"] * H) + 90, "the card meets the caption band"
    return ev


def legend_text(man: dict) -> str:
    return f"same strings, stretch drawn {man['stretch_draw_x']:g}x"


def clock_text(r: float) -> str:
    return "held, at rest" if r < 0.0 else f"{r:.3f} s after the pull starts"


def label_text(man: dict, p: str) -> str:
    V = man["speed_m_s"][p]
    return f"pulled at {V * 100:g} cm/s" if p == "slow" else f"jerked at {V:g} m/s"


def ball_text(x: float) -> str:
    return f"ball moved {x * 1000:.3f} mm"


def hand_text(h: float) -> str:
    return f"hand moved {h * 1000:.2f} mm"


def event_lines(ev: dict, p: str) -> list[str]:
    run = ev["runs"][p]
    return [f"{run['which']} string snaps", f"at {run['t_snap']:.3f} s"]


def break_text(man: dict) -> str:
    return f"snaps at {man['break_n']:g} N"


def weight_text(man: dict) -> str:
    return f"{man['mass_kg'] * man['g']:.1f} N"


def bar_value_text(f: float) -> str:
    return f"{f:.1f} N"


def payoff_lines(man: dict, ev: dict) -> list[str]:
    s, j = ev["runs"]["slow"], ev["runs"]["jerk"]
    text = man["payoff_text"].format(t_top=s["t_snap"], t_bot=j["t_snap"], x_top_mm=s["x_snap"] * 1000.0,
                                     x_bot_mm=j["x_snap"] * 1000.0, v_lo=ev["v_lo"], v_hi=ev["v_hi"])
    return [t.strip() for t in text.split("|")]


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
        self.geo = geometry(man)
        self.S = man["slow"]
        self.P = man["cycle_s"]
        self.P_f = int(round(man["cycle_s"] * self.fps))
        self.c0_f = int(round(man["first_cycle_at"] * self.fps))
        self.pa, self.F = man["release_at"], man["reset_fade"]
        self.runs = ev["runs"]
        self.Fn = man["break_n"]

    def phase(self, f: int) -> tuple[int, float]:
        k, tau_f = divmod(f - self.c0_f, self.P_f)
        return k, tau_f / self.fps

    @staticmethod
    def L_(x: float, y: float) -> tuple[float, float]:
        """Layer (2x) pixel of a band-local point, rounded to 1e-4 px so equal states draw equal pixels."""
        return round(x * SS, 4), round(y * SS, 4)

    def warm(self, p: str, f: float) -> tuple:
        """The string colour: the panel colour warming toward coral as the tension nears the break."""
        return blend(CORAL, max(0.0, min(1.0, f / self.Fn)), COLOUR[p])

    def draw_hook(self, d: ImageDraw.ImageDraw) -> None:
        cx, hook = self.geo["cx"], self.geo["hook"]
        b0, b1 = self.L_(cx - 60, 6), self.L_(cx + 60, hook - 6)
        d.rounded_rectangle((b0[0], b0[1], b1[0], b1[1]), radius=4 * SS, fill=DECK_A, outline=RIM, width=2 * SS)
        for j in range(-5, 6):
            p0, p1 = self.L_(cx + j * 11, 6), self.L_(cx + j * 11 - 6, hook - 6)
            d.line((*p0, *p1), fill=blend(RIM, 0.6, DECK_A), width=2 * SS)
        X, Y = self.L_(cx, hook)
        rr = 6 * SS
        d.ellipse((X - rr, Y - rr, X + rr, Y + rr), outline=STEEL, width=2 * SS)

    def draw_string(self, d: ImageDraw.ImageDraw, y0: float, y1: float, col: tuple) -> None:
        cx = self.geo["cx"]
        p0, p1 = self.L_(cx, y0), self.L_(cx, y1)
        d.line((*p0, *p1), fill=col, width=STRING_W * SS)

    def draw_stub(self, d: ImageDraw.ImageDraw, y_end: float, half: float, down: bool, u: float, col: tuple) -> None:
        """A broken end recoiling from the break point toward its anchor at y_end: its length shrinks
        from half the string to STUB over the recoil and its tip curls sideways."""
        cx = self.geo["cx"]
        ln = max(STUB, half * (1.0 - u) + STUB * u)
        sgn = 1.0 if down else -1.0
        tip_y = y_end + sgn * ln
        curl = 12.0 * u
        pts = [self.L_(cx, y_end), self.L_(cx, tip_y - sgn * curl), self.L_(cx + curl, tip_y)]
        d.line(pts, fill=col, width=STRING_W * SS, joint="curve")

    def draw_slack(self, d: ImageDraw.ImageDraw, y0: float, length: float, col: tuple) -> None:
        """The slack bottom string hanging limp under the ball: a wave over its drawn rest length."""
        cx = self.geo["cx"]
        pts = []
        n = 24
        for j in range(n + 1):
            u = j / n
            pts.append(self.L_(cx + 9.0 * math.sin(u * 3.0 * math.pi) * (0.3 + 0.7 * u), y0 + length * u))
        d.line(pts, fill=col, width=STRING_W * SS, joint="curve")

    def draw_flash(self, d: ImageDraw.ImageDraw, y: float, u: float) -> None:
        cx = self.geo["cx"]
        rr = (12.0 + 60.0 * u) * SS
        X, Y = self.L_(cx, y)
        d.ellipse((X - rr, Y - rr, X + rr, Y + rr), outline=blend(GOLD, 1.0 - u), width=3 * SS)

    def draw_ball(self, d: ImageDraw.ImageDraw, y: float) -> None:
        cx, r = self.geo["cx"], self.geo["r"]
        X, Y = self.L_(cx, y)
        rr = r * SS
        d.ellipse((X - rr, Y - rr, X + rr, Y + rr), fill=BALL, outline=BALL_RIM, width=2 * SS)
        hx, hy = self.L_(cx - r * 0.35, y - r * 0.35)
        hr = r * 0.22 * SS
        d.ellipse((hx - hr, hy - hr, hx + hr, hy + hr), fill=WHITE)

    def draw_hand(self, d: ImageDraw.ImageDraw, grip: float, aside: float, open_: float) -> None:
        """A hand pinching the string's end from the right: a palm and two fingers meeting at the
        pinch point; shifted right by aside px and opened (fingers spread) by open_ in 0..1."""
        cx = self.geo["cx"]
        x0 = cx + HAND_GAP + aside
        p0, p1 = self.L_(x0, grip - 12), self.L_(x0 + HAND_W, grip - 12 + HAND_H)
        d.rounded_rectangle((p0[0], p0[1], p1[0], p1[1]), radius=14 * SS, fill=HAND, outline=HAND_DARK, width=2 * SS)
        spread = 16.0 * open_
        for sgn, base in ((-1.0, grip - 4), (1.0, grip + 8)):
            a0 = self.L_(x0 + 6, base)
            a1 = self.L_(cx + aside, grip + sgn * (3.0 + spread))
            d.line((*a0, *a1), fill=HAND, width=12 * SS)
            d.line((*a0, *a1), fill=HAND_DARK, width=2 * SS)

    def draw_bars(self, d: ImageDraw.ImageDraw, p: str, f1: float, f2: float, snapped: str | None) -> None:
        for name, f in ((TOP, f1), (BOTTOM, f2)):
            x = BAR_X[name]
            b0, b1 = self.L_(x, BAR_TOP), self.L_(x + BAR_W, BAR_BOT)
            d.rectangle((b0[0], b0[1], b1[0], b1[1]), fill=DECK_A, outline=RIM, width=2 * SS)
            if name != snapped and f > 0.0:
                top = BAR_BOT - min(BAR_N, f) * BAR_PX_PER_N
                f0, f1_ = self.L_(x + 3, top), self.L_(x + BAR_W - 3, BAR_BOT - 3)
                if f1_[1] > f0[1]:
                    d.rectangle((f0[0], f0[1], f1_[0], f1_[1]), fill=self.warm(p, f))
        yb = BAR_BOT - self.Fn * BAR_PX_PER_N
        g0, g1 = self.L_(BAR_X[TOP] - 24, yb), self.L_(BAR_X[BOTTOM] + BAR_W + 12, yb)
        d.line((*g0, *g1), fill=GOLD, width=3 * SS)
        yw = BAR_BOT - self.man["mass_kg"] * self.man["g"] * BAR_PX_PER_N
        w0, w1 = self.L_(BAR_X[TOP] - 18, yw), self.L_(BAR_X[TOP] - 4, yw)
        d.line((*w0, *w1), fill=MUTED, width=3 * SS)

    def scene(self, p: str, tau: float) -> tuple[Image.Image, dict]:
        """The band layer of panel p at tau seconds into a cycle (the resting setup before the pull)."""
        man, geo = self.man, self.geo
        run = self.runs[p]
        layer = Image.new("RGB", (W * SS, BAND_H * SS), BG)
        d = ImageDraw.Draw(layer)
        tv = tau - self.pa
        rt = tv / self.S
        st = state_at(run, rt)
        st["tv"], st["rt"] = tv, rt
        cx, r = geo["cx"], geo["r"]
        by = ball_dy(run, st, geo)
        grip = grip_dy(run, st, geo)
        snapped = run["which"] if st["phase"] in (FALL, WOBBLE) else None
        since = (rt - run["t_snap"]) * self.S if snapped else -1.0      # video seconds since the snap
        u_recoil = smoother(since / man["recoil_s"]) if snapped else 0.0
        self.draw_hook(d)
        self.draw_bars(d, p, st["f1"], st["f2"], snapped)
        # The top string: intact, or two recoiling stubs from the hook and from the ball's top.
        y_top0, y_top1 = geo["hook"], by - r
        if snapped == TOP:
            by_s = geo["ball0"] + geo["exp"] * run["x_snap"]
            half = 0.5 * (by_s - r - geo["hook"])
            self.draw_stub(d, geo["hook"], half, True, u_recoil, COLOUR[p])
            self.draw_stub(d, by - r, half, False, u_recoil, COLOUR[p])
        else:
            self.draw_string(d, y_top0, y_top1, self.warm(p, st["f1"]))
        # The bottom string: intact (taut), limp after the slack, or two stubs after its snap.
        aside, open_ = 0.0, 0.0
        if snapped == BOTTOM:
            grip_s = geo["grip0"] + geo["exp"] * run["V"] * run["t_snap"]
            by_s = geo["ball0"] + geo["exp"] * run["x_snap"]
            half = 0.5 * (grip_s - by_s - r)
            self.draw_stub(d, by + r, half, True, u_recoil, COLOUR[p])
            self.draw_stub(d, grip, half, False, u_recoil, COLOUR[p])
        elif st["slack"]:
            w = smoother((rt - run["t_slack"]) * self.S / man["hand_aside_s"])
            aside, open_ = HAND_ASIDE * w, w
            self.draw_slack(d, by + r, float(man["bottom_string_px"]), blend(COLOUR[p], 0.7))
        else:
            self.draw_string(d, by + r, grip, self.warm(p, st["f2"]))
        self.draw_ball(d, by)
        self.draw_hand(d, grip, aside, open_)
        if snapped and since < man["flash_s"]:
            if snapped == TOP:
                y_flash = geo["hook"] + 0.5 * (geo["ball0"] + geo["exp"] * run["x_snap"] - r - geo["hook"])
            else:
                y_flash = 0.5 * (geo["ball0"] + geo["exp"] * run["x_snap"] + r + geo["grip0"]
                                 + geo["exp"] * run["V"] * run["t_snap"])
            self.draw_flash(d, y_flash, since / man["flash_s"])
        st["snapped"] = snapped
        return layer, st

    def draw_panel(self, p: str, f: int) -> tuple[Image.Image, dict]:
        k, tau = self.phase(f)
        P, F = self.P, self.F
        layer, st = self.scene(p, tau)
        st["alpha"], st["k"] = 1.0, k
        if tau >= P - F:
            # Crossfade to the next cycle's resting setup (the fallen ball and the departing hand are
            # out of the band by now, asserted in measure).
            a = (tau - (P - F)) / F
            new, st_new = self.scene(p, tau - P)
            layer = Image.blend(layer, new, a)
            st["alpha"] = max(0.0, 1.0 - 2.0 * a)
            st_new["alpha"], st_new["k"] = max(0.0, 2.0 * a - 1.0), k + 1
            if a >= 0.5:
                st = st_new
        return layer, st

    def draw_text(self, d: ImageDraw.ImageDraw, states: dict, hud_alpha: float) -> None:
        man, ev = self.man, self.ev
        for p, st in states.items():
            run = self.runs[p]
            y0 = BAND_Y[p]
            a = st["alpha"]
            snapped = st.get("snapped")
            d.text((ROW_X0, y0 + LABEL_DY), label_text(man, p), font=self.font, fill=COLOUR[p], anchor="lm")
            if snapped:
                d.text((ROW_X0, y0 + SUB_DY), ball_text(run["x_snap"]), font=self.font_small, fill=blend(GOLD, a), anchor="lm")
                d.text((ROW_X0, y0 + FIX_DY), hand_text(run["V"] * run["t_snap"]), font=self.font_small,
                       fill=blend(MUTED, a), anchor="lm")
                for j, line in enumerate(event_lines(ev, p)):
                    d.text((ROW_X0, y0 + EVENT_DY[j]), line, font=self.font, fill=blend(GOLD, a), anchor="lm")
            else:
                d.text((ROW_X0, y0 + SUB_DY), ball_text(st["x"]), font=self.font_small, fill=blend(TEXT, a), anchor="lm")
                d.text((ROW_X0, y0 + FIX_DY), hand_text(st["hand"]), font=self.font_small, fill=blend(MUTED, a), anchor="lm")
            # The bar labels and live values.
            for name, f in ((TOP, st["f1"]), (BOTTOM, st["f2"])):
                xm = BAR_X[name] + BAR_W / 2.0
                d.text((xm, y0 + BAR_BOT + 22), name, font=self.font_tiny, fill=MUTED, anchor="mm")
                if name == snapped:
                    d.text((xm, y0 + BAR_TOP - 18), "snapped", font=self.font_tiny, fill=blend(GOLD, a), anchor="mm")
                else:
                    d.text((xm, y0 + BAR_TOP - 18), bar_value_text(f), font=self.font_tiny,
                           fill=blend(self.warm(p, f), a), anchor="mm")
            yb = y0 + BAR_BOT - self.Fn * BAR_PX_PER_N
            d.text((BAR_X[BOTTOM] + BAR_W + 12, yb - 20), break_text(man), font=self.font_tiny, fill=GOLD, anchor="rm")
            yw = y0 + BAR_BOT - man["mass_kg"] * man["g"] * BAR_PX_PER_N
            d.text((BAR_X[TOP] - 24, yw), weight_text(man), font=self.font_tiny, fill=MUTED, anchor="rm")
        if hud_alpha > 0.02:
            d.text((W / 2, LEGEND_Y), legend_text(man), font=self.font, fill=blend(TEXT, hud_alpha), anchor="mm")
            d.text((W / 2, CLOCK_Y), clock_text(states["slow"]["rt"]), font=self.font_small,
                   fill=blend(MUTED, hud_alpha), anchor="mm")

    def live_frame(self, f: int, title_alpha: float | None = None, hud_alpha: float = 0.0) -> np.ndarray:
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
        states = {}
        for p in PANELS:
            layer, states[p] = self.draw_panel(p, f)
            img.paste(layer.reduce(SS), (0, BAND_Y[p]))
        d = ImageDraw.Draw(img)
        self.draw_text(d, states, hud_alpha)
        if title_alpha > 0.0:
            for j, line in enumerate(man["title"].split("|")):
                d.text((W / 2, 190 + j * 62), line, font=self.font_title, fill=blend(TEXT, title_alpha), anchor="mm")
        if t >= man["payoff_t"]:
            a = min(1.0, (t - man["payoff_t"]) / man["payoff_hold"]) * hud_alpha
            for j, line in enumerate(payoff_lines(man, self.ev)):
                d.text((W / 2, PAYOFF_Y + j * PAYOFF_PITCH), line, font=self.font, fill=blend(GOLD, a), anchor="mm")
        return np.asarray(img, dtype=np.uint8)

    def frame_at(self, f: int) -> np.ndarray:
        man = self.man
        total = int(round(man["scene_duration"] * self.fps))
        fade_frames = int(round(man["loop_fade"] * self.fps))
        if f == total - 1:
            return self.live_frame(0)   # the scene is periodic: the last frame repeats the first
        if f >= total - fade_frames:
            # The geometry runs on; the legend, clock and card fade out over the first half of the
            # loop fade and the title fades in over the second half, so the two never overlap.
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
        wrap = self.live_frame(total, title_alpha=1.0, hud_alpha=0.0)   # the scene one period on, drawn live
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
    man = json.loads((ROOT / "projects/twostrings/manifest.json").read_text())
    ev = measure(man)
    if "--measure-only" in sys.argv:
        return
    if "--frames" in sys.argv:
        times = [float(v) for v in sys.argv[sys.argv.index("--frames") + 1].split(",")]
        r = Renderer(man, ev)
        (ROOT / "media/twostrings").mkdir(parents=True, exist_ok=True)
        for tv in times:
            Image.fromarray(r.frame_at(int(round(tv * man["fps"])))).save(ROOT / f"media/twostrings/smoke-{tv}.png")
        print("smoke frames: " + ", ".join(f"{tv}" for tv in times))
        return
    Renderer(man, ev).render(ROOT / "media/twostrings/footage.mp4")


if __name__ == "__main__":
    main()
