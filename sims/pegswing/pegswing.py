#!/usr/bin/env python3
"""Pendulum and peg: will the ball swing round the peg?

A ball (a point mass) hangs on a massless string of length L from a fixed
pivot and is let go from rest with the string horizontal, the ball level
with the pivot on the left. A thin peg (zero radius in the kinematics) is
fixed on the vertical below the pivot at a distance d. The ball swings
down as a pendulum (theta'' = -(g / L) sin theta by RK4, checked against
v^2 = 2 g L cos theta and the elliptic quarter period). When the string
passes the vertical it catches the peg and the ball goes on round a
circle of radius r = L - d about the peg at the same speed: the velocity
is tangent to both circles at the bottom, so the catch loses nothing. On
the small circle v^2 = 2 g L - 2 g r (1 - cos psi), psi the angle from the
bottom about the peg, and the string pull per unit mass is
T = v^2 / r + g cos psi. The string is still taut at the top only if
v_top^2 >= g r, that is 2 L - 4 r >= r, r <= 2 L / 5, d >= 3 L / 5: the
peg must be at least three fifths of the way down.

Two panels on one clock. Above, the peg halfway down (r = L / 2): the
pull reaches zero at cos psi = -2 (L - r) / (3 r), the string goes slack
and the ball flies as a projectile. Two regimes for the re-catch: while
the ball is on the far side of the vertical through the peg (x > 0) the
string is still round the peg and snaps taut if the ball's distance from
the peg comes back to r; once the ball has crossed to the near side
(x < 0) the string has slipped off the peg and runs straight from the
pivot, so it snaps taut when the ball's distance from the pivot reaches
L. The jerk kills the radial velocity and keeps the tangential part; the
ball then swings as a pendulum again (about the pivot on the near side,
round the peg whenever it crosses the vertical). Below, the peg 70 percent
down (r = 0.3 L): the string stays taut over the top and the ball loops
the peg lap after lap; with a zero-radius peg every lap is the same. Both
panels are integrated by RK4 at steps_per_second with every event (the
catch, the slack, the crossing of the vertical, the re-catch, the top and
the laps) located by bisection inside the step. The release repeats every
cycle_s seconds of video with a crossfade back to the ball at rest; the
cycle divides the scene length, so the scene is periodic and the last
frame equals the first. Shown at 1/slow speed. Deterministic, no seed.

Measured and printed: the swing to the bottom (time and speed against
the elliptic quarter period and sqrt(2 g L)), the catch check (the same
speed on both circles, the velocity horizontal, the pull jump), for the
upper panel the slack (angle from the bottom, short of the top, above the
peg's level, speed, height) against the closed form, the flight (peak,
the crossing of the vertical inside the small circle, the re-catch on the
near side, the radial part killed and the tangential part kept, the
energy kept) and the swing afterwards, for the lower panel the top
(speed, the speed needed, the pull) and the laps against the quadrature,
the threshold d = 3 L / 5 with d just below, at and above it, the RK4
energy check, the schedule in video time, and the on-screen text widths.

usage: pegswing.py [--measure-only] [--frames t1,t2,...]
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
RIM = (96, 108, 126)
STRING = (196, 204, 214)

# Layout: overlay at y 96..130 (captions.py); two title rows at y 190/252
# for the first seconds, then the legend at y 236 and the shared clock at
# y 290; two panels stacked in the band y 340..1420 (540 px each, drawn at
# 2x), each with its pivot 80 px under its top edge at x 540 and the ball
# let go 1 m (400 px) to the left, level with the pivot; the panel label
# top left and the event mark top right (both above the ghost ring and the
# flight), the pull readout bottom left and the state word bottom right
# (both under the bottom of the swing); captions at caption_y 0.75
# (y 1440..1530); the six-line card from y 1580 at a 48 px pitch.
TITLE_Y, TITLE_PITCH = 190, 62
LEGEND_Y, CLOCK_Y = 236, 290
GEOM_Y0, GEOM_Y1 = 340, 1420
SS = 2
PAYOFF_Y, PAYOFF_PITCH = 1580.0, 48
PANELS = ("upper", "lower")
PANEL_COL = {"upper": CORAL, "lower": TEAL}
LABEL_DY, MARK_DY = 30, 30
READ_LABEL_DY, READ_DY, STATE_DY = 470, 516, 516
ROW_X0, ROW_X1 = 60, 1020
BALL_R = 14.0
REST, PIVOT, PEG, FLIGHT = -1, 0, 1, 2
TAUT, FAR, NEAR = 0, 1, 2
ST_REST, ST_SWING, ST_PEG, ST_SLACK, ST_CAUGHT = 0, 1, 2, 3, 4
STATE_WORDS = {ST_REST: "at rest, level with the pivot", ST_SWING: "swinging down", ST_PEG: "round the peg",
               ST_SLACK: "slack, flying free", ST_CAUGHT: "caught by the string, swinging low"}


def blend(col, a: float, base=BG) -> tuple:
    a = max(0.0, min(1.0, a))
    return tuple(int(round(c * a + b * (1 - a))) for c, b in zip(col, base))


def smoothstep(u: float) -> float:
    u = max(0.0, min(1.0, u))
    return u * u * (3 - 2 * u)


# --- measurement --------------------------------------------------------------
def rk4_pend(a: float, w: float, k: float, h: float) -> tuple[float, float]:
    """One classical RK4 step of a'' = -k sin a over h."""
    a1 = -k * math.sin(a)
    x2, w2 = a + 0.5 * h * w, w + 0.5 * h * a1
    a2 = -k * math.sin(x2)
    x3, w3 = a + 0.5 * h * w2, w + 0.5 * h * a2
    a3 = -k * math.sin(x3)
    x4, w4 = a + h * w3, w + h * a3
    a4 = -k * math.sin(x4)
    return a + h * (w + 2.0 * w2 + 2.0 * w3 + w4) / 6.0, w + h * (a1 + 2.0 * a2 + 2.0 * a3 + a4) / 6.0


def ellip_k(k: float) -> float:
    """Complete elliptic integral of the first kind by the arithmetic-geometric mean."""
    a, b = 1.0, math.sqrt(1.0 - k * k)
    while abs(a - b) > 1e-15:
        a, b = 0.5 * (a + b), math.sqrt(a * b)
    return math.pi / (2.0 * a)


def simpson(f, a: float, b: float, n: int = 20000) -> float:
    xs = np.linspace(a, b, n + 1)
    ys = np.array([f(x) for x in xs])
    h = (b - a) / n
    return float(h / 3.0 * (ys[0] + ys[-1] + 4.0 * ys[1:-1:2].sum() + 2.0 * ys[2:-1:2].sum()))


def simulate(d: float, man: dict) -> dict:
    """RK4 from rest at the horizontal until sim_end_s (real seconds); the modes are the pendulum about
    the pivot, the circle about the peg and the free flight; every event is located by bisection
    inside the step and the state snapped to it. x right, y up, the pivot at (0, 0), the peg at (0, -d)."""
    g, L = man["g"], man["string_m"]
    r = L - d
    dt = 1.0 / man["steps_per_second"]
    n = int(round(man["sim_end_s"] / dt))
    tol = man["slack_tol_weights"] * g
    v0 = math.sqrt(2.0 * g * L)
    two_pi = 2.0 * math.pi

    def t_pivot(a: float, w: float) -> float:
        return L * w * w + g * math.cos(a)

    def t_peg(a: float, w: float) -> float:
        return r * w * w + g * math.cos(a)

    mode, a, w, t = PIVOT, -0.5 * math.pi, 0.0, 0.0
    fl: dict | None = None
    laps = 0
    stage = ST_SWING
    events: list = []
    ts, xs, ys, Ts, modes, regs, lapc, stages, angs = ([] for _ in range(9))
    t_min_pivot = math.inf

    def record() -> None:
        if mode == PIVOT:
            x, y, T, reg = L * math.sin(a), -L * math.cos(a), t_pivot(a, w) / g, TAUT
        elif mode == PEG:
            x, y, T, reg = r * math.sin(a), -d - r * math.cos(a), t_peg(a, w) / g, TAUT
        else:
            tau = t - fl["t0"]
            x, y = fl["x0"] + fl["vx0"] * tau, fl["y0"] + fl["vy0"] * tau - 0.5 * g * tau * tau
            T, reg = 0.0, fl["regime"]
        ts.append(t); xs.append(x); ys.append(y); Ts.append(T); modes.append(mode); regs.append(reg)
        lapc.append(laps); stages.append(stage); angs.append(a if mode != FLIGHT else 0.0)

    record()
    for i in range(1, n + 1):
        remaining = dt
        while remaining > 1e-15:
            if mode == PIVOT:
                a1, w1 = rk4_pend(a, w, g / L, remaining)
                t_min_pivot = min(t_min_pivot, t_pivot(a1, w1) / g)
                if a < 0.0 <= a1 and w1 > 0.0:
                    lo, hi = 0.0, remaining
                    for _ in range(80):
                        mid = 0.5 * (lo + hi)
                        am, _ = rk4_pend(a, w, g / L, mid)
                        if am < 0.0:
                            lo = mid
                        else:
                            hi = mid
                    _, wh = rk4_pend(a, w, g / L, hi)
                    t += hi
                    remaining -= hi
                    v = wh * L
                    events.append({"kind": "catch peg", "t": t, "v": v, "T_before": t_pivot(0.0, wh) / g,
                                   "T_after": t_peg(0.0, v / r) / g, "dir_deg": 0.0})
                    mode, a, w = PEG, 0.0, v / r
                    if stage == ST_SWING:
                        stage = ST_PEG
                    continue
                a, w = a1, w1
                t += remaining
                remaining = 0.0
            elif mode == PEG:
                a1, w1 = rk4_pend(a, w, g / r, remaining)
                if t_peg(a1, w1) < -tol:
                    lo, hi = 0.0, remaining
                    for _ in range(80):
                        mid = 0.5 * (lo + hi)
                        am, wm = rk4_pend(a, w, g / r, mid)
                        if t_peg(am, wm) >= 0.0:
                            lo = mid
                        else:
                            hi = mid
                    ah, wh = rk4_pend(a, w, g / r, hi)
                    t += hi
                    remaining -= hi
                    x, y = r * math.sin(ah), -d - r * math.cos(ah)
                    v = wh * r
                    vx, vy = v * math.cos(ah), v * math.sin(ah)
                    events.append({"kind": "slack", "t": t, "psi": ah, "v": v, "x": x, "y": y, "vx": vx, "vy": vy,
                                   "T": t_peg(ah, wh) / g})
                    fl = {"x0": x, "y0": y, "vx0": vx, "vy0": vy, "t0": t, "regime": FAR if x > 0.0 else NEAR,
                          "peak": False}
                    mode = FLIGHT
                    stage = ST_SLACK
                    continue
                if a > 0.0 >= a1:
                    lo, hi = 0.0, remaining
                    for _ in range(80):
                        mid = 0.5 * (lo + hi)
                        am, _ = rk4_pend(a, w, g / r, mid)
                        if am > 0.0:
                            lo = mid
                        else:
                            hi = mid
                    _, wh = rk4_pend(a, w, g / r, hi)
                    t += hi
                    remaining -= hi
                    v = wh * r
                    events.append({"kind": "unwrap", "t": t, "v": v})
                    mode, a, w = PIVOT, 0.0, v / L
                    continue
                k0, k1 = math.floor((a - math.pi) / two_pi), math.floor((a1 - math.pi) / two_pi)
                if k1 > k0:
                    target = math.pi + two_pi * k1
                    f = (target - a) / (a1 - a)
                    wt = w + f * (w1 - w)
                    events.append({"kind": "top", "t": t + f * remaining, "v": abs(wt) * r, "T": t_peg(target, wt) / g,
                                   "n": k1 + 1})
                k0, k1 = math.floor(a / two_pi), math.floor(a1 / two_pi)
                if k1 > k0 and k1 >= 1:
                    target = two_pi * k1
                    f = (target - a) / (a1 - a)
                    wt = w + f * (w1 - w)
                    events.append({"kind": "lap", "t": t + f * remaining, "v": abs(wt) * r, "n": k1})
                    laps = k1
                a, w = a1, w1
                t += remaining
                remaining = 0.0
            else:
                assert fl is not None
                tau0 = t - fl["t0"]
                tau1 = tau0 + remaining

                def pos(tau: float) -> tuple[float, float]:
                    return fl["x0"] + fl["vx0"] * tau, fl["y0"] + fl["vy0"] * tau - 0.5 * g * tau * tau

                tp = fl["vy0"] / g
                if not fl["peak"] and tau0 < tp <= tau1:
                    fl["peak"] = True
                    xp, yp = pos(tp)
                    events.append({"kind": "peak", "t": fl["t0"] + tp, "x": xp, "y": yp})
                xa, ya = pos(tau0)
                xb, yb = pos(tau1)
                if fl["regime"] == FAR:
                    if xa > 0.0 >= xb and fl["vx0"] < 0.0:
                        tauc = -fl["x0"] / fl["vx0"]
                        h = max(0.0, tauc - tau0)
                        xc, yc = pos(tauc)
                        t = fl["t0"] + tauc
                        remaining -= h
                        events.append({"kind": "cross", "t": t, "above_peg": yc + d, "dist_peg": math.hypot(xc, yc + d),
                                       "dist_pivot": math.hypot(xc, yc), "vx": fl["vx0"], "vy": fl["vy0"] - g * tauc})
                        fl["regime"] = NEAR
                        continue
                    fa, fb = math.hypot(xa, ya + d) - r, math.hypot(xb, yb + d) - r
                    if fa < 0.0 <= fb:
                        lo, hi = tau0, tau1
                        for _ in range(80):
                            mid = 0.5 * (lo + hi)
                            xm, ym = pos(mid)
                            if math.hypot(xm, ym + d) - r < 0.0:
                                lo = mid
                            else:
                                hi = mid
                        xc, yc = pos(hi)
                        vx, vy = fl["vx0"], fl["vy0"] - g * hi
                        psi = math.atan2(xc, -(yc + d))
                        v_tan = vx * math.cos(psi) + vy * math.sin(psi)
                        v_rad = vx * math.sin(psi) - vy * math.cos(psi)
                        t = fl["t0"] + hi
                        remaining -= hi - tau0
                        events.append({"kind": "catch peg string", "t": t, "psi": psi, "speed": math.hypot(vx, vy),
                                       "v_rad": v_rad, "v_tan": v_tan, "kept": v_tan * v_tan / (v0 * v0)})
                        mode, a, w = PEG, psi, v_tan / r
                        stage = ST_CAUGHT
                        continue
                else:
                    fa, fb = math.hypot(xa, ya) - L, math.hypot(xb, yb) - L
                    if fa < 0.0 <= fb:
                        lo, hi = tau0, tau1
                        for _ in range(80):
                            mid = 0.5 * (lo + hi)
                            xm, ym = pos(mid)
                            if math.hypot(xm, ym) - L < 0.0:
                                lo = mid
                            else:
                                hi = mid
                        xc, yc = pos(hi)
                        vx, vy = fl["vx0"], fl["vy0"] - g * hi
                        th = math.atan2(xc, -yc)
                        v_tan = vx * math.cos(th) + vy * math.sin(th)
                        v_rad = vx * math.sin(th) - vy * math.cos(th)
                        t = fl["t0"] + hi
                        remaining -= hi - tau0
                        events.append({"kind": "catch string", "t": t, "theta": th, "x": xc, "y": yc,
                                       "speed": math.hypot(vx, vy), "v_rad": v_rad, "v_tan": v_tan,
                                       "kept": v_tan * v_tan / (v0 * v0), "flight": t - fl["t0"],
                                       "dir_deg": math.degrees(math.atan2(-vy, -vx))})
                        mode, a, w = PIVOT, th, v_tan / L
                        stage = ST_CAUGHT
                        continue
                    if xa <= 0.0 < xb:
                        events.append({"kind": "recross", "t": t})
                t += remaining
                remaining = 0.0
        t = i * dt
        record()
    ev = {"kind_index": {}}
    for e in events:
        ev["kind_index"].setdefault(e["kind"], []).append(e)
    return {"d": d, "r": r, "t": np.array(ts), "x": np.array(xs), "y": np.array(ys), "T": np.array(Ts),
            "mode": np.array(modes), "reg": np.array(regs), "laps": np.array(lapc), "stage": np.array(stages),
            "ang": np.array(angs), "events": events, "by_kind": ev["kind_index"], "t_min_pivot": t_min_pivot,
            "v0": v0}


def first(run: dict, kind: str) -> dict | None:
    lst = run["by_kind"].get(kind)
    return lst[0] if lst else None


def closed_forms(d: float, man: dict) -> dict:
    g, L = man["g"], man["string_m"]
    r = L - d
    v0 = math.sqrt(2.0 * g * L)
    out = {"v0": v0, "t_bottom": math.sqrt(L / g) * ellip_k(math.sin(math.pi / 4.0)), "r": r,
           "v_top2": 2.0 * g * L - 4.0 * g * r, "need2": g * r, "T_top": 2.0 * L / r - 5.0}
    c = -2.0 * (L - r) / (3.0 * r)
    speed = lambda psi: math.sqrt(max(0.0, 2.0 * g * L - 2.0 * g * r * (1.0 - math.cos(psi))))  # noqa: E731
    if c >= -1.0:
        psi = math.acos(c)
        out.update({"loops": False, "psi_slack": psi, "v_slack": math.sqrt(2.0 * g * (L - r) / 3.0),
                    "h_slack": -r * c, "t_arc": simpson(lambda p: r / speed(p), 0.0, psi)})
        x0, y0 = r * math.sin(psi), -d - r * math.cos(psi)
        vx, vy = out["v_slack"] * math.cos(psi), out["v_slack"] * math.sin(psi)
        out["peak"] = y0 + vy * vy / (2.0 * g) + d
        if vx < 0.0 < x0:
            tc = -x0 / vx
            yc = y0 + vy * tc - 0.5 * g * tc * tc
            out.update({"t_cross": tc, "cross_above_peg": yc + d})
            lo, hi = tc, tc + 5.0
            f = lambda tau: math.hypot(x0 + vx * tau, y0 + vy * tau - 0.5 * g * tau * tau) - L  # noqa: E731
            if f(lo) < 0.0:
                for _ in range(100):
                    mid = 0.5 * (lo + hi)
                    if f(mid) < 0.0:
                        lo = mid
                    else:
                        hi = mid
                out["t_catch"] = 0.5 * (lo + hi)
    else:
        out.update({"loops": True, "lap": simpson(lambda p: r / speed(p), 0.0, 2.0 * math.pi),
                    "t_half": simpson(lambda p: r / speed(p), 0.0, math.pi)})
    return out


def measure(man: dict) -> dict:
    g, L = man["g"], man["string_m"]
    S, P, D, fps, F = man["slow"], man["cycle_s"], man["scene_duration"], man["fps"], man["reset_fade"]
    rel = man["release_at"]
    steps = man["steps_per_second"]
    cycles = D / P
    assert abs(cycles - round(cycles)) < 1e-9, "the cycle must divide the scene length"
    for key in ("cycle_s", "release_at", "first_cycle_at", "reset_fade"):
        assert abs(man[key] * fps - round(man[key] * fps)) < 1e-9, f"{key} must be a whole number of frames"
    assert P / S <= man["sim_end_s"], "the simulation must cover a whole cycle"
    fr = man["peg_fractions"]
    print(f"setup: a ball (a point mass) on a massless string of L = {L:g} m from a fixed pivot, let go from rest with "
          f"the string horizontal (the ball level with the pivot, on the left); a thin peg (zero radius) fixed on the "
          f"vertical below the pivot at d = {fr[0]:g} L (upper panel, r = L - d = {L - fr[0] * L:.2f} m) and d = {fr[1]:g} L "
          f"(lower panel, r = {L - fr[1] * L:.2f} m); g = {g:g} m/s^2; RK4 at {steps} steps per second (dt = {1 / steps:.0e} s) "
          f"with the catch, the slack, the crossing of the vertical, the re-catch, the top and the laps located by "
          f"bisection inside the step; shown at 1/{S:g} speed on a {P:g} s cycle ({P * fps:.0f} frames) with the release "
          f"{rel:g} s into the cycle, {cycles:.0f} cycles in {D:g} s; drawn at {man['px_per_m']:g} px per metre; "
          f"deterministic, no seed")
    cf0 = closed_forms(fr[0] * L, man)
    print(f"closed forms: bottom speed sqrt(2 g L) = {cf0['v0']:.4f} m/s; time from the horizontal to the bottom "
          f"sqrt(L / g) K(sin 45 deg) = {cf0['t_bottom']:.4f} s; on the small circle v^2 = 2 g L - 2 g r (1 - cos psi) and "
          f"T = v^2 / r + g cos psi; the string is taut at the top only if v_top^2 = 2 g L - 4 g r >= g r, i.e. "
          f"r <= 2 L / 5, d >= 3 L / 5 = {0.6 * L:.2f} m; T at the top = 2 L / r - 5 weights; where the pull reaches zero "
          f"cos psi = -2 (L - r) / (3 r) and v^2 = 2 g (L - r) / 3")
    runs = {p: simulate(f_ * L, man) for p, f_ in zip(PANELS, fr)}
    cfs = {p: closed_forms(f_ * L, man) for p, f_ in zip(PANELS, fr)}
    ev: dict = {"runs": runs, "cfs": cfs}
    for p in PANELS:
        run, cf = runs[p], cfs[p]
        d, r = run["d"], run["r"]
        c = first(run, "catch peg")
        assert c is not None
        # Energy check on the swing down and the small circle before any slack.
        sl = first(run, "slack")
        t_end_check = sl["t"] if sl else c["t"] + 3.0 * cf.get("lap", 1.0)
        m = run["t"] <= t_end_check
        v2_closed = np.where(run["mode"][m] == PIVOT, 2.0 * g * L * np.cos(run["ang"][m]),
                             2.0 * g * L - 2.0 * g * r * (1.0 - np.cos(run["ang"][m])))
        T_closed = np.where(run["mode"][m] == PIVOT, v2_closed / L + g * np.cos(run["ang"][m]),
                            v2_closed / r + g * np.cos(run["ang"][m])) / g
        err_T = float(np.max(np.abs(run["T"][m] - T_closed)))
        print(f"{p} panel (d = {d:g} m, r = {r:g} m): the ball reaches the bottom at {c['t']:.4f} s (closed form "
              f"{cf['t_bottom']:.4f} s, diff {abs(c['t'] - cf['t_bottom']):.1e} s) at {c['v']:.4f} m/s (closed form "
              f"{cf['v0']:.4f}, diff {abs(c['v'] - cf['v0']):.1e}); the string passes the vertical and catches the peg: the "
              f"velocity is {c['dir_deg']:.1f} degrees from horizontal, tangent to both circles, so the speed is "
              f"{c['v']:.4f} m/s on both sides and the catch loses nothing; the pull jumps from {c['T_before']:.4f} weights "
              f"(v^2 / L + g) to {c['T_after']:.4f} weights (v^2 / r + g); RK4 pull stays within {err_T:.1e} weights of "
              f"the energy closed form over {int(m.sum())} samples up to {t_end_check:.3f} s")
        if sl is not None:
            psi = math.degrees(sl["psi"])
            cross, catch, peak = first(run, "cross"), first(run, "catch string"), first(run, "peak")
            assert cross is not None and catch is not None and peak is not None
            assert first(run, "catch peg string") is None, "the upper ball must not be caught on the far side"
            after = run["t"] > catch["t"]
            th_after = run["ang"][after & (run["mode"] == PIVOT)]
            ps_after = run["ang"][after & (run["mode"] == PEG)]
            print(f"{p} panel, slack: the pull reaches 0 at {sl['t']:.4f} s ({sl['t'] - c['t']:.4f} s after the catch; "
                  f"quadrature of r dpsi / v {cf['t_arc']:.4f} s) at psi = {psi:.2f} degrees from the bottom about the peg = "
                  f"{180 - psi:.2f} degrees short of the top = {psi - 90:.2f} degrees above the peg's level (closed form "
                  f"{math.degrees(cf['psi_slack']):.2f}, {180 - math.degrees(cf['psi_slack']):.2f} short, "
                  f"{math.degrees(cf['psi_slack']) - 90:.2f} above), at {sl['v']:.4f} m/s (closed form sqrt(2 g (L - r) / 3) = "
                  f"{cf['v_slack']:.4f}), {sl['y'] + d:.4f} m above the peg (closed form {cf['h_slack']:.4f}) and "
                  f"{sl['x']:.4f} m to the far side; the pull there {sl['T']:.1e} weights; the string goes slack and the "
                  f"ball flies with velocity ({sl['vx']:.4f}, {sl['vy']:.4f}) m/s")
            print(f"{p} panel, flight: the ball peaks {peak['y'] + d:.4f} m above the peg (closed form {cf['peak']:.4f}) at "
                  f"x = {peak['x']:.4f} m, {peak['t'] - sl['t']:.4f} s after the slack; it crosses the vertical "
                  f"{cross['t'] - sl['t']:.4f} s after the slack (closed form {cf['t_cross']:.4f}) at {cross['above_peg']:.4f} m "
                  f"above the peg (closed form {cf['cross_above_peg']:.4f}), {cross['dist_peg']:.4f} m from the peg against "
                  f"r = {r:g} m, so {'inside' if cross['dist_peg'] < r else 'outside'} the small circle: the string round "
                  f"the peg never came taut on the far side; from here the string has slipped off the peg and runs straight "
                  f"from the pivot ({cross['dist_pivot']:.4f} m from it against L = {L:g}); it comes taut {catch['flight']:.4f} s "
                  f"after the slack (closed form {cf['t_catch']:.4f}, diff {abs(catch['flight'] - cf['t_catch']):.1e} s) at "
                  f"{catch['t']:.4f} s, on the near side {abs(math.degrees(catch['theta'])):.2f} degrees from the bottom about "
                  f"the pivot, at ({catch['x']:.4f}, {catch['y']:.4f}) m, moving at {catch['speed']:.4f} m/s "
                  f"{catch['dir_deg']:.1f} degrees below horizontal, almost straight along the string: the jerk kills the "
                  f"radial part {catch['v_rad']:.4f} m/s and keeps the tangential {abs(catch['v_tan']):.4f} m/s, "
                  f"{catch['kept'] * 100:.3f} percent of the bottom kinetic energy ({catch['kept'] * 100:.2f} %); afterwards "
                  f"the ball swings between {abs(math.degrees(th_after.min())) if th_after.size else 0:.1f} degrees left of "
                  f"the bottom about the pivot and {math.degrees(ps_after.max()) if ps_after.size else 0:.1f} degrees right "
                  f"about the peg, until the panel resets")
            ev["slack"], ev["catch"], ev["cross"], ev["peak"] = sl, catch, cross, peak
        else:
            tops = run["by_kind"].get("top", [])
            laps = run["by_kind"].get("lap", [])
            assert len(tops) >= 3 and len(laps) >= 3, "the lower ball must loop"
            lap_t = [laps[0]["t"] - c["t"]] + [laps[i]["t"] - laps[i - 1]["t"] for i in range(1, len(laps))]
            T_min = float(run["T"][(run["t"] > c["t"]) & (run["t"] <= laps[-1]["t"])].min())
            print(f"{p} panel, loop: the ball passes the top at {tops[0]['t']:.4f} s ({tops[0]['t'] - c['t']:.4f} s after the "
                  f"catch; quadrature {cf['t_half']:.4f} s) at {tops[0]['v']:.4f} m/s (closed form sqrt(2 g L - 4 g r) = "
                  f"{math.sqrt(cf['v_top2']):.4f}; it needs sqrt(g r) = {math.sqrt(cf['need2']):.4f}) with the pull "
                  f"{tops[0]['T']:.4f} weights (closed form 2 L / r - 5 = {cf['T_top']:.4f}), the minimum over the laps "
                  f"{T_min:.4f} weights, so the string stays taut and the ball LOOPS THE PEG; laps round the peg take "
                  + ", ".join(f"{x:.4f}" for x in lap_t[:4]) + f" s (spread {max(lap_t) - min(lap_t):.1e} s; quadrature of "
                  f"r dpsi / v over 2 pi {cf['lap']:.4f} s): every lap is the same, the panel is periodic; "
                  f"{len(laps)} laps done by {laps[-1]['t']:.3f} s, {len(run['by_kind']['lap'])} in the {man['sim_end_s']:g} s run")
            ev["top"], ev["laps"], ev["lap_t"] = tops, laps, lap_t
    # The threshold.
    chk = []
    for f_ in man["check_fractions"]:
        run, cf = simulate(f_ * L, man), closed_forms(f_ * L, man)
        sl, tops = first(run, "slack"), run["by_kind"].get("top", [])
        if sl is not None:
            chk.append(f"d = {f_:g} L: does NOT loop, the pull reaches 0 at {math.degrees(sl['psi']):.2f} degrees from the "
                       f"bottom ({180 - math.degrees(sl['psi']):.2f} short of the top; closed form {180 - math.degrees(cf['psi_slack']):.2f}), "
                       f"v_top^2 would be {cf['v_top2']:.4f} against the g r = {cf['need2']:.4f} needed, T at the top would be "
                       f"{cf['T_top']:.4f} weights")
        else:
            chk.append(f"d = {f_:g} L: LOOPS, passes the top at {tops[0]['v']:.4f} m/s (needs {math.sqrt(cf['need2']):.4f}) with "
                       f"the pull {tops[0]['T']:.2e} weights (closed form 2 L / r - 5 = {cf['T_top']:.4f})"
                       + ("; the exact threshold: the string just reaches the top with zero pull" if abs(f_ - 0.6) < 1e-9 else ""))
    print(f"threshold: the peg must be at least 3 L / 5 = {0.6 * L:.2f} m down the string (r <= 2 L / 5 = {0.4 * L:.2f} m); "
          + "; ".join(chk))
    ev["t_min_pivot"] = {p: runs[p]["t_min_pivot"] for p in PANELS}
    # Schedule in video time.
    t0 = man["first_cycle_at"]
    k0 = math.ceil((0.0 - t0) / P - 1e-9) - 1
    k1 = math.floor((D - t0) / P - 1e-9)
    starts = [t0 + k * P for k in range(k0, k1 + 1)]

    def lst(off_: float) -> str:
        return ", ".join(f"{s + off_:.2f}" for s in starts if 0.0 <= s + off_ < D)

    vt = lambda real: rel + real * S  # noqa: E731
    tau0 = (0.0 - t0) % P
    r0 = (tau0 - rel) / S
    up, lo = runs["upper"], runs["lower"]
    c_up = first(up, "catch peg")
    st0 = {p: state_at(runs[p], r0) for p in PANELS}
    top_times = sorted(t for s in starts for e in ev["top"] if 0.0 <= (t := s + vt(e["t"])) < D and (t - s) < P - F / 2)
    print(f"schedule (video time, 1/{S:g} speed): cycles of {P:g} s start at " + ", ".join(f"{s:.2f}" for s in starts)
          + f" s (the first {-t0:.2f} s before the first frame); the release {rel:g} s into each cycle at {lst(rel)} s; both "
          f"balls reach the bottom and catch the peg {c_up['t'] * S:.2f} s after the release at {lst(vt(c_up['t']))} s; the "
          f"upper string goes slack {ev['slack']['t'] * S:.2f} s after the release at {lst(vt(ev['slack']['t']))} s, the "
          f"upper ball peaks at {lst(vt(ev['peak']['t']))} s, crosses the vertical at {lst(vt(ev['cross']['t']))} s and is "
          f"caught by the straight string {ev['catch']['t'] * S:.2f} s after the release at {lst(vt(ev['catch']['t']))} s; "
          f"the lower ball passes the top at " + ", ".join(f"{t:.2f}" for t in top_times) + " s (lap "
          f"{ev['lap_t'][1] * S:.2f} s of video); each cycle crossfades to the ball at rest over its last {F:g} s "
          f"({P - F:.2f} to {P:.2f} s after the cycle start); on the first frame the cycle is {tau0:.2f} s in ({r0:.3f} s real "
          f"after the release): the upper ball is {STATE_WORDS[st0['upper']['stage']]} at ({st0['upper']['x']:.3f}, "
          f"{st0['upper']['y']:.3f}) m, the lower ball {STATE_WORDS[st0['lower']['stage']]} at ({st0['lower']['x']:.3f}, "
          f"{st0['lower']['y']:.3f}) m; title until {man['title_until']:g} s; payoff card from {man['payoff_t']:g} s; the "
          f"title fades back in over the last {man['loop_fade']:g} s and the last frame repeats the first (the scene is "
          f"periodic: {D:g} s holds exactly {cycles:.0f} cycles)")
    # Layout check and text widths.
    ppm = man["px_per_m"]
    px_peak = (540 + ev["peak"]["x"] * ppm, man["pivot_dy"] - ev["peak"]["y"] * ppm)
    font = os.environ["SEED_ZERO_FONT"]
    f28, f32, f34, f40, f48, f56 = (ImageFont.truetype(font, n) for n in (28, 32, 34, 40, 48, 56))
    widths = {"overlay@34": (f34, man["overlay"])}
    for j, line in enumerate(man["title"].split("|")):
        widths[f"title line {j + 1}@56"] = (f56, line)
    widths["legend@40"] = (f40, legend_text(man))
    widths["clock@28"] = (f28, clock_text(1.234, S))
    widths["clock rest@28"] = (f28, clock_text(-1.0, S))
    for p, lab in zip(PANELS, man["panel_labels"]):
        widths[f"label {p}@40"] = (f40, lab)
        widths[f"mark {p}@32"] = (f32, mark_text(ev, p))
    widths["peg label@28"] = (f28, "peg")
    widths["readout label@28"] = (f28, "string pull")
    widths["readout@48"] = (f48, readout_text(first(lo, "catch peg")["T_after"]))
    widths["readout slack@48"] = (f48, readout_text(0.0))
    for st, word in STATE_WORDS.items():
        widths[f"state {st}@28"] = (f28, word)
    widths["state lap@28"] = (f28, state_text(ST_PEG, 12, "lower"))
    for j, line in enumerate(payoff_lines(man, ev)):
        widths[f"payoff line {j + 1}@40"] = (f40, line)
    print("text widths: " + ", ".join(f"{k} {f.getlength(s):.0f} px" for k, (f, s) in widths.items()))
    assert all(f.getlength(s) < 950 for f, s in widths.values()), "a text line is wider than 950 px"
    mark_x0 = ROW_X1 - max(f32.getlength(mark_text(ev, p)) for p in PANELS)
    label_x1 = ROW_X0 + max(f40.getlength(lab) for lab in man["panel_labels"])
    read_x1 = ROW_X0 + f48.getlength(readout_text(9.99))
    state_x0 = ROW_X1 - max(f28.getlength(w) for w in STATE_WORDS.values())
    ring_top = min(man["pivot_dy"] + (runs[p]["d"] - runs[p]["r"]) * ppm for p in PANELS)
    bottom = man["pivot_dy"] + L * ppm
    arc_corner = math.hypot(read_x1 - 540, READ_DY - 24 - man["pivot_dy"])
    print(f"layout (panel px): pivot (540, {man['pivot_dy']}), release point ({540 - L * ppm:.0f}, {man['pivot_dy']}), bottom of "
          f"the swing (540, {bottom:.0f}), the ghost rings' tops at y {ring_top:.0f}, the upper ball's flight peak at "
          f"({px_peak[0]:.0f}, {px_peak[1]:.0f}); the label ends at x {label_x1:.0f} and the mark starts at x {mark_x0:.0f} "
          f"(both in rows {LABEL_DY - 20}..{LABEL_DY + 20}); the readout ends at x {read_x1:.0f} (rows {READ_DY - 24}.."
          f"{READ_DY + 24}) and the state word starts at x {state_x0:.0f} (rows {STATE_DY - 14}..{STATE_DY + 14}); the "
          f"readout's top-right corner is {arc_corner:.0f} px from the pivot against the ball's {L * ppm + BALL_R:.0f}")
    assert label_x1 < mark_x0 - 40, "the label and the mark collide"
    assert MARK_DY + 20 < ring_top - 2 and MARK_DY + 20 < px_peak[1] - BALL_R, "the mark row touches the ring or the flight"
    assert arc_corner > L * ppm + BALL_R, "the swing touches the readout"
    assert STATE_DY - 14 > bottom + BALL_R, "the ball at the bottom touches the state word"
    assert read_x1 + 40 < 540 - BALL_R, "the readout reaches under the bottom of the swing"
    assert read_x1 < state_x0 - 40, "the readout and the state word collide"
    assert STATE_DY + 14 < man["band_y"][1] - man["band_y"][0], "the rows leave the panel"
    return ev


def state_at(run: dict, r: float) -> dict:
    """The recorded sample nearest to r real seconds after the release (the rest state before it)."""
    if r < 0.0:
        L = float(run["r"] + run["d"])
        return {"x": -L, "y": 0.0, "T": 0.0, "mode": REST, "reg": TAUT, "laps": 0, "stage": ST_REST, "i": -1}
    i = min(len(run["t"]) - 1, int(round(r * (len(run["t"]) - 1) / float(run["t"][-1]))))
    return {"x": float(run["x"][i]), "y": float(run["y"][i]), "T": float(run["T"][i]), "mode": int(run["mode"][i]),
            "reg": int(run["reg"][i]), "laps": int(run["laps"][i]), "stage": int(run["stage"][i]), "i": i}


def legend_text(man: dict) -> str:
    return "same ball, same swing, two pegs"


def clock_text(r: float, S: float) -> str:
    return "at rest, level with the pivot" if r < 0.0 else f"{r:.2f} s after release, {S:g}x slow motion"


def readout_text(T: float) -> str:
    return f"{T:.2f} weights"


def state_text(stage: int, laps: int, panel: str) -> str:
    if stage == ST_PEG and panel == "lower":
        return f"round the peg, lap {laps + 1}"
    return STATE_WORDS[stage]


def mark_text(ev: dict, panel: str) -> str:
    if panel == "upper":
        return f"slack {180 - math.degrees(ev['slack']['psi']):.0f}° short of the top"
    return f"over the top at {ev['top'][0]['v']:.1f} m/s"


def payoff_lines(man: dict, ev: dict) -> list[str]:
    text = man["payoff_text"].format(short=180 - math.degrees(ev["slack"]["psi"]), v_slack=ev["slack"]["v"],
                                     v_top=ev["top"][0]["v"], T_top=ev["top"][0]["T"], lap=ev["lap_t"][1])
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
        self.font_mark = ImageFont.truetype(font, 32)
        self.font_num = ImageFont.truetype(font, 48)
        self.ppm = float(man["px_per_m"])
        self.S = man["slow"]
        self.P = man["cycle_s"]
        self.P_f = int(round(self.P * self.fps))
        self.c0_f = int(round(man["first_cycle_at"] * self.fps))
        self.rel, self.F = man["release_at"], man["reset_fade"]
        self.runs = ev["runs"]
        self.L = man["string_m"]
        self.band = {p: (man["band_y"][i], man["band_y"][i + 1]) for i, p in enumerate(PANELS)}
        self.labels = dict(zip(PANELS, man["panel_labels"]))
        self.start_state: np.ndarray | None = None
        self.steps = man["steps_per_second"]
        self.trail_n = 28
        self.trail_stride = max(1, int(round(man["trail_s"] * self.steps / self.trail_n)))

    def phase(self, f: int) -> tuple[int, float]:
        k, tau_f = divmod(f - self.c0_f, self.P_f)
        return k, tau_f / self.fps

    def P_(self, panel: str, x: float, y: float) -> tuple[float, float]:
        """Layer (2x) pixel of a metre point, y up, the pivot of the panel at (540, band top + pivot_dy)."""
        y0 = self.band[panel][0]
        return round((540.0 + x * self.ppm) * SS, 3), round((y0 - GEOM_Y0 + self.man["pivot_dy"] - y * self.ppm) * SS, 3)

    def slack_curve(self, panel: str, ax: float, ay: float, bx: float, by: float, length: float) -> list:
        """A drooping string from the anchor to the ball: a quadratic curve whose control point hangs below
        the chord's midpoint, its droop set by bisection so the sampled polyline has the string's length."""
        cx, cy = bx - ax, by - ay
        c = math.hypot(cx, cy)
        if c >= length - 1e-9 or c < 1e-9:
            return [self.P_(panel, ax, ay), self.P_(panel, bx, by)]
        nx, ny = 0.0, -1.0   # the slack droops straight down
        ts = np.linspace(0.0, 1.0, 25)

        def curve(h: float) -> np.ndarray:
            mx, my = ax + 0.5 * cx + nx * h, ay + 0.5 * cy + ny * h
            px = (1 - ts) ** 2 * ax + 2 * (1 - ts) * ts * mx + ts ** 2 * bx
            py = (1 - ts) ** 2 * ay + 2 * (1 - ts) * ts * my + ts ** 2 * by
            return np.stack([px, py], axis=1)

        lo, hi = 0.0, 2.0 * length
        for _ in range(40):
            mid = 0.5 * (lo + hi)
            pts = curve(mid)
            if float(np.sum(np.hypot(np.diff(pts[:, 0]), np.diff(pts[:, 1])))) < length:
                lo = mid
            else:
                hi = mid
        return [self.P_(panel, float(x), float(y)) for x, y in curve(0.5 * (lo + hi))]

    def draw_panel_geometry(self, d: ImageDraw.ImageDraw, panel: str, st: dict, tr: float) -> None:
        man, run = self.man, self.runs[panel]
        L, r, dpeg = self.L, run["r"], run["d"]
        P = lambda x, y: self.P_(panel, x, y)  # noqa: E731
        col = PANEL_COL[panel]
        # The level line from the release point to the pivot, the mount and the pivot.
        d.line((P(-L, 0.0), P(0.0, 0.0)), fill=blend(MUTED, 0.25), width=2 * SS)
        mx, my = P(0.0, 0.0)
        d.line((mx - 34 * SS, my - 12 * SS, mx + 34 * SS, my - 12 * SS), fill=RIM, width=6 * SS)
        # The ghost ring about the peg.
        cx, cy = P(0.0, -dpeg)
        Rp = r * self.ppm * SS
        d.ellipse((cx - Rp, cy - Rp, cx + Rp, cy + Rp), outline=blend(col, 0.32), width=2 * SS)
        # The dotted leader from the peg to its label.
        lx = cx + Rp + 24 * SS
        x = cx + 14 * SS
        while x < lx - 6 * SS:
            d.line((x, cy, x + 4 * SS, cy), fill=blend(MUTED, 0.6), width=2 * SS)
            x += 10 * SS
        # Event marks: the slack point and the gap to the top (upper), the top ring (lower).
        if panel == "upper" and st["stage"] >= ST_SLACK:
            sl = self.ev["slack"]
            deg = math.degrees(sl["psi"])
            Ra = Rp + 16 * SS
            d.arc((cx - Ra, cy - Ra, cx + Ra, cy + Ra), start=-90, end=90 - deg, fill=GOLD, width=5 * SS)
            sx, sy = P(sl["x"], sl["y"])
            rr = 9 * SS
            d.ellipse((sx - rr, sy - rr, sx + rr, sy + rr), outline=GOLD, width=3 * SS)
            d.line((cx, cy, sx, sy), fill=blend(GOLD, 0.6), width=2 * SS)
            d.line((cx, cy, cx, cy - Rp), fill=blend(GOLD, 0.6), width=2 * SS)
        if panel == "lower" and st["i"] >= 0 and tr >= self.ev["top"][0]["t"]:
            rr = 11 * SS
            d.ellipse((cx - rr, cy - Rp - rr, cx + rr, cy - Rp + rr), outline=GOLD, width=3 * SS)
        # The trail.
        if st["i"] > 0:
            i1 = st["i"]
            idx = list(range(max(0, i1 - self.trail_stride * self.trail_n), i1 + 1, self.trail_stride))
            if idx[-1] != i1:
                idx.append(i1)
            pts = [P(float(run["x"][i]), float(run["y"][i])) for i in idx]
            for j in range(len(pts) - 1):
                a = 0.75 * (j + 1) / len(pts)
                d.line((*pts[j], *pts[j + 1]), fill=blend(TEAL, a), width=3 * SS)
        # The string.
        bx, by = st["x"], st["y"]
        if st["mode"] in (PIVOT, REST):
            d.line((P(0.0, 0.0), P(bx, by)), fill=STRING, width=3 * SS)
        elif st["mode"] == PEG:
            d.line((P(0.0, 0.0), P(0.0, -dpeg)), fill=STRING, width=3 * SS)
            d.line((P(0.0, -dpeg), P(bx, by)), fill=STRING, width=3 * SS)
        else:
            if st["reg"] == FAR:
                d.line((P(0.0, 0.0), P(0.0, -dpeg)), fill=CORAL, width=2 * SS)
                pts = self.slack_curve(panel, 0.0, -dpeg, bx, by, r)
            else:
                pts = self.slack_curve(panel, 0.0, 0.0, bx, by, L)
            d.line(pts, fill=CORAL, width=2 * SS, joint="curve")
        # The peg and the pivot.
        pr = 6 * SS
        d.ellipse((cx - pr, cy - pr, cx + pr, cy + pr), fill=WHITE)
        d.ellipse((mx - pr, my - pr, mx + pr, my + pr), fill=RIM)
        # The ball.
        qx, qy = P(bx, by)
        rb = BALL_R * SS
        d.ellipse((qx - rb, qy - rb, qx + rb, qy + rb), fill=GOLD, outline=(120, 84, 30), width=SS)
        hr = rb * 0.32
        d.ellipse((qx - rb * 0.45 - hr, qy - rb * 0.45 - hr, qx - rb * 0.45 + hr, qy - rb * 0.45 + hr), fill=WHITE)

    def draw_panel_text(self, d: ImageDraw.ImageDraw, panel: str, st: dict, tr: float) -> None:
        run = self.runs[panel]
        y0 = self.band[panel][0]
        col = PANEL_COL[panel]
        d.text((ROW_X0, y0 + LABEL_DY), self.labels[panel], font=self.font, fill=col, anchor="lm")
        show_mark = (panel == "upper" and st["stage"] >= ST_SLACK) or \
                    (panel == "lower" and st["i"] >= 0 and tr >= self.ev["top"][0]["t"])
        if show_mark:
            d.text((ROW_X1, y0 + MARK_DY), mark_text(self.ev, panel), font=self.font_mark, fill=GOLD, anchor="rm")
        # The peg label right of the ring at the peg's height.
        cx, cy = self.P_(panel, 0.0, -run["d"])
        d.text((cx / SS + run["r"] * self.ppm + 24, GEOM_Y0 + cy / SS), "peg", font=self.font_small, fill=MUTED, anchor="lm")
        # The pull readout and the state word.
        d.text((ROW_X0, y0 + READ_LABEL_DY), "string pull", font=self.font_small, fill=MUTED, anchor="lm")
        if st["stage"] == ST_REST:
            ncol = MUTED
        elif st["stage"] == ST_SLACK:
            ncol = CORAL
        else:
            ncol = TEXT
        d.text((ROW_X0, y0 + READ_DY), readout_text(st["T"]), font=self.font_num, fill=ncol, anchor="lm")
        scol = CORAL if st["stage"] == ST_SLACK else (GOLD if st["stage"] == ST_CAUGHT else MUTED)
        d.text((ROW_X1, y0 + STATE_DY), state_text(st["stage"], st["laps"], panel), font=self.font_small, fill=scol,
               anchor="rm")

    def draw_state(self, tau: float) -> np.ndarray:
        """The geometry and the panel texts for tau seconds into a cycle (no title, clock or card)."""
        tr = (tau - self.rel) / self.S
        img = Image.new("RGB", (W, H), BG)
        layer = Image.new("RGB", (W * SS, (GEOM_Y1 - GEOM_Y0) * SS), BG)
        ld = ImageDraw.Draw(layer)
        states = {p: state_at(self.runs[p], tr) for p in PANELS}
        for p in PANELS:
            self.draw_panel_geometry(ld, p, states[p], tr)
        img.paste(layer.reduce(SS), (0, GEOM_Y0))
        d = ImageDraw.Draw(img)
        for p in PANELS:
            self.draw_panel_text(d, p, states[p], tr)
        return np.asarray(img, dtype=np.float32)

    def scene(self, f: int) -> np.ndarray:
        """The state at frame f; the last reset_fade of each cycle crossfades to the ball at rest."""
        _, tau = self.phase(f)
        live = self.draw_state(tau)
        if tau >= self.P - self.F:
            u = smoothstep((tau - (self.P - self.F)) / self.F)
            if self.start_state is None:
                self.start_state = self.draw_state(0.0)
            live = live * (1.0 - u) + self.start_state * u
        return live

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
        img = Image.fromarray(self.scene(f).astype(np.uint8))
        d = ImageDraw.Draw(img)
        if hud_alpha > 0.02:
            d.text((W / 2, LEGEND_Y), legend_text(man), font=self.font, fill=blend(TEXT, hud_alpha), anchor="mm")
            _, tau = self.phase(f)
            d.text((W / 2, CLOCK_Y), clock_text((tau - self.rel) / self.S, self.S), font=self.font_small,
                   fill=blend(MUTED, hud_alpha), anchor="mm")
        if title_alpha > 0.0:
            for j, line in enumerate(man["title"].split("|")):
                d.text((W / 2, TITLE_Y + j * TITLE_PITCH), line, font=self.font_title, fill=blend(TEXT, title_alpha),
                       anchor="mm")
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
            # The geometry runs on; the legend and card fade out over the first half of the loop fade
            # and the title fades in over the second half, so the two never overlap.
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
        wrap = self.live_frame(total, title_alpha=1.0, hud_alpha=0.0)   # the geometry one scene on, drawn live
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
    man = json.loads((ROOT / "projects/pegswing/manifest.json").read_text())
    ev = measure(man)
    if "--measure-only" in sys.argv:
        return
    if "--frames" in sys.argv:
        times = [float(v) for v in sys.argv[sys.argv.index("--frames") + 1].split(",")]
        r = Renderer(man, ev)
        (ROOT / "media/pegswing").mkdir(parents=True, exist_ok=True)
        for tv in times:
            Image.fromarray(r.frame_at(int(round(tv * man["fps"])))).save(ROOT / f"media/pegswing/smoke-{tv}.png")
        print("smoke frames: " + ", ".join(f"{tv}" for tv in times))
        return
    Renderer(man, ev).render(ROOT / "media/pegswing/footage.mp4")


if __name__ == "__main__":
    main()
