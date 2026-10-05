#!/usr/bin/env python3
"""Block on a wedge, bolted or free: which block reaches the floor first?

Two panels on the same clock, the same wedge drawn the same way at the same
scale, side view. A block of mass m (a cube of side c, treated as a point
mass at its centre for the motion) rests at the top of a wedge of mass M
whose slope of angle alpha is L = h / sin(alpha) long (h tall, L cos(alpha)
of run); no friction between the block and the wedge. Top panel: the wedge
is bolted to the floor; the block slides down the slope at g sin(alpha),
reaches the floor after sqrt(2 L / a) and presses m g cos(alpha). Bottom
panel: the same wedge sits free on ice (no friction under it either) and
is let go with the block at the same instant; the block presses the slope,
the slope pushes back, and the wedge slides backward at

    A = m g sin(alpha) cos(alpha) / (M + m sin^2(alpha))

while the block speeds down the slope, relative to the wedge, at

    a_rel = (M + m) g sin(alpha) / (M + m sin^2(alpha)),

pressing only N = m M g cos(alpha) / (M + m sin^2(alpha)). With M = m at
30 degrees a_rel is exactly 1.6 g sin(alpha), so the free block is down in
1 / sqrt(1.6) of the bolted time, and the equal masses split the run: the
block goes forward M / (M + m) of L cos(alpha), the wedge back m / (M + m)
of it. Both bands are integrated by classical RK4 at steps_per_second on
the block's and the wedge's Cartesian coordinates with the normal force
solved from the contact constraint at every stage (the block's
acceleration relative to the wedge has no component along the slope's
normal), the floor crossing located by bisection inside the step, and
checked against the closed forms, the contact residual, the horizontal
momentum of the free pair, the energy balance and a half-step rerun.
After the floor the block stops on a floor pad at the foot of the slope
(no bounce) and the free wedge keeps sliding on the ice at its final speed
until a buffer stops it (a plastic stop, buffer_gap_m past its position at
the landing). The drop repeats every cycle_s seconds of video with a
crossfade back to the held setup; the cycle divides the scene length, so
the scene is exactly periodic and the last frame equals the first. Shown
at 1/slow speed. Deterministic, no seed.

Measured and printed: for each band the acceleration along the slope, the
time to the floor, the speeds, the normal force (RK4 against the closed
forms, the contact residual, the momentum, the energy, a half-step rerun),
the wedge's shift and the block's forward travel, the block's lab path
angle, the bolted block's position when the free block lands, the position
tables at table_step_s, the other wedge masses and slope angles for the
description, the brief's checks, the schedule in video time, the on-screen
text widths and the layout clearances.

usage: wedge.py [--measure-only] [--frames t1,t2,...]
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
DECK_A = (30, 36, 46)
DECK_B = (42, 50, 62)
RIM = (96, 108, 126)
INK = (150, 158, 170)
WEDGE_FILL = (54, 62, 76)
WEDGE_EDGE = (120, 132, 150)
BLOCK_FILL = (214, 222, 232)
BLOCK_EDGE = (120, 132, 150)
BLOCK_HI = (240, 244, 248)
ICE = (176, 204, 226)
ICE_HI = (228, 240, 250)
PAD = (84, 94, 110)
BOLT = (200, 150, 70)
BOLT_DARK = (90, 66, 30)
BUFFER = (70, 78, 92)
TRAIL = (122, 132, 148)

# Layout: overlay at y 96..130 (captions.py), three title rows at y 186/244/302
# for the first seconds, then the legend at y 236 and the shared clock at y
# 290; two panels stacked, the bolted wedge in the band y 330..880 and the
# free wedge in y 880..1430, each drawn at 2x in its own geometry layer; each
# band has its label row 40 px under the band top, its second row at 84 and
# its third at 120 (left column from x 40, right column to x 1040); the
# floor surface floor_dy under the band top (y 750 and 1300) with the slab
# under it; the wedge's foot at foot_x_px on the floor and its slope rising
# to the left; the gold event row under the slab at 496; captions at
# caption_y 0.75 (y 1440..1530); the six-line card from y 1572 at a 48 px
# pitch.
LEGEND_Y, CLOCK_Y = 236, 290
TITLE_Y = (186, 244, 302)
SS = 2
PAYOFF_Y, PAYOFF_PITCH = 1572.0, 48
PANELS = ("bolted", "free")
BAND_Y = {"bolted": 330, "free": 880}
BAND_H = 550
LABEL_DY, SUB_DY, FIX_DY = 40, 84, 120
EVENT_DY, EVENT_X = 496, 540
ROW_X0, ROW_X1 = 40, 1040
SLAB_PX, ICE_PX, PAD_PX, PAD_W = 28, 10, 14, 48
BUFFER_W, BUFFER_H = 22, 44
PIN_LEN, PIN_W = 30, 6
COLOUR = {"bolted": CORAL, "free": TEAL}
HELD, SLIDE, DOWN = "held", "sliding", "on the floor"


def blend(col, a: float, base=BG) -> tuple:
    a = max(0.0, min(1.0, a))
    return tuple(int(round(c * a + b * (1 - a))) for c, b in zip(col, base))


# --- measurement --------------------------------------------------------------
def closed_forms(m: float, M: float, a_deg: float, h: float, g: float, bolted: bool) -> dict:
    """The closed forms of the slide: a_rel along the slope, the wedge's acceleration A, the normal force N,
    the time to the floor, the speeds there, the wedge's shift and the block's forward travel."""
    a = math.radians(a_deg)
    sa, ca = math.sin(a), math.cos(a)
    L = h / sa
    if bolted:
        a_rel, A, N = g * sa, 0.0, m * g * ca
    else:
        den = M + m * sa * sa
        a_rel, A, N = (M + m) * g * sa / den, m * g * sa * ca / den, m * M * g * ca / den
    t = math.sqrt(2.0 * L / a_rel)
    v_rel = a_rel * t
    V = A * t
    vx, vy = v_rel * ca - V, v_rel * sa
    back = 0.5 * A * t * t
    return {"L": L, "a_rel": a_rel, "A": A, "N": N, "t": t, "v_rel": v_rel, "V": V, "vx": vx, "vy": vy,
            "v": math.hypot(vx, vy), "back": back, "fwd": L * ca - back, "angle": math.degrees(math.atan2(vy, vx)),
            "E": m * g * h}


def rk4_run(m: float, M: float, a_deg: float, h: float, g: float, dt: float, bolted: bool) -> dict:
    """Classical RK4 at dt on (xb, yb, X, vxb, vyb, VX): the block's lab position from the top of the slope (y
    up) and the wedge's lab shift from its start. At every stage the normal force N is solved from the
    contact constraint, (a_block - a_wedge) . n = 0 with n = (sin a, cos a) the slope's outward normal:
    N (1 / m + sin^2 a / M) = g cos a (M infinite when bolted). The floor crossing (slope distance s = L)
    is located by bisection inside the last step. Returns the table and the end state."""
    a = math.radians(a_deg)
    sa, ca = math.sin(a), math.cos(a)
    L = h / sa

    def normal_force() -> float:
        return g * ca / (1.0 / m + (0.0 if bolted else sa * sa / M))

    def f(y: np.ndarray) -> np.ndarray:
        N = normal_force()
        return np.array([y[3], y[4], y[5], N * sa / m, N * ca / m - g, 0.0 if bolted else -N * sa / M])

    def step(y: np.ndarray, hh: float) -> np.ndarray:
        k1 = f(y)
        k2 = f(y + 0.5 * hh * k1)
        k3 = f(y + 0.5 * hh * k2)
        k4 = f(y + hh * k3)
        return y + hh * (k1 + 2.0 * k2 + 2.0 * k3 + k4) / 6.0

    def s_of(y: np.ndarray) -> float:
        return (y[0] - y[2]) * ca - y[1] * sa

    def res_of(y: np.ndarray) -> float:
        return (y[0] - y[2]) * sa + y[1] * ca

    y = np.zeros(6)
    T, Y = [0.0], [y.copy()]
    n = 0
    while True:
        yn = step(y, dt)
        if s_of(yn) >= L:
            lo, hi = 0.0, dt
            for _ in range(80):
                mid = 0.5 * (lo + hi)
                if s_of(step(y, mid)) < L:
                    lo = mid
                else:
                    hi = mid
            yl = step(y, hi)
            t_land = n * dt + hi
            T.append(t_land)
            Y.append(yl)
            n += 1
            break
        n += 1
        y = yn
        T.append(n * dt)
        Y.append(y.copy())
    tab = np.array(Y)
    t = np.array(T)
    s = (tab[:, 0] - tab[:, 2]) * ca - tab[:, 1] * sa
    res = (tab[:, 0] - tab[:, 2]) * sa + tab[:, 1] * ca
    mom = m * tab[:, 3] + M * tab[:, 5]
    E = 0.5 * m * (tab[:, 3] ** 2 + tab[:, 4] ** 2) + 0.5 * M * tab[:, 5] ** 2 + m * g * tab[:, 1]
    return {"t": t, "xb": tab[:, 0], "yb": tab[:, 1], "X": tab[:, 2], "vxb": tab[:, 3], "vyb": tab[:, 4],
            "VX": tab[:, 5], "s": s, "t_land": t_land, "y_land": yl, "steps": n, "N": normal_force(),
            "res_max": float(np.max(np.abs(res))), "mom_max": float(np.max(np.abs(mom))),
            "E_max": float(np.max(np.abs(E))), "E_land": float(abs(E[-1])),
            "m": m, "M": M, "a": a, "L": L, "h": h, "g": g, "bolted": bolted}


def state_at(run: dict, rt: float, gap: float) -> dict:
    """The lab state rt real seconds after the release: the block's position from the top of the slope (m,
    y up), the wedge's shift X (m, negative backward), the speeds, the slope distance s and the phase;
    after the floor the block rests where it landed and the wedge slides on until the buffer gap past its
    landing shift stops it."""
    if rt < 0.0:
        return {"xb": 0.0, "yb": 0.0, "X": 0.0, "vxb": 0.0, "vyb": 0.0, "VX": 0.0, "s": 0.0, "phase": HELD,
                "wedge_stopped": False}
    if rt < run["t_land"]:
        st = {k: float(np.interp(rt, run["t"], run[k])) for k in ("xb", "yb", "X", "vxb", "vyb", "VX", "s")}
        st["phase"], st["wedge_stopped"] = SLIDE, False
        return st
    yl = run["y_land"]
    d = rt - run["t_land"]
    X = yl[2] + yl[5] * d
    stopped = False
    if yl[5] < 0.0 and X < yl[2] - gap:
        X, stopped = yl[2] - gap, True
    return {"xb": float(yl[0]), "yb": float(yl[1]), "X": float(X), "vxb": 0.0, "vyb": 0.0,
            "VX": 0.0 if stopped or yl[5] == 0.0 else float(yl[5]), "s": run["L"], "phase": DOWN,
            "wedge_stopped": stopped}


def measure(man: dict) -> dict:
    g, m, M = man["g"], man["block_kg"], man["wedge_kg"]
    a_deg, h, c = man["angle_deg"], man["height_m"], man["block_side_m"]
    dt = 1.0 / man["steps_per_second"]
    S, P, D, fps, F, pa = man["slow"], man["cycle_s"], man["scene_duration"], man["fps"], man["reset_fade"], man["release_at"]
    gap = man["buffer_gap_m"]
    cycles = D / P
    assert abs(cycles - round(cycles)) < 1e-9, "the cycle must divide the scene length"
    for key in ("cycle_s", "release_at", "first_cycle_at", "reset_fade", "scene_duration"):
        assert abs(man[key] * fps - round(man[key] * fps)) < 1e-9, f"{key} must be a whole number of frames"
    ppm = man["px_per_m"]
    a = math.radians(a_deg)
    sa, ca = math.sin(a), math.cos(a)
    L = h / sa
    print(f"setup: side view, two panels on one clock, the same wedge drawn the same way at the same scale: a {m:g} kg "
          f"block (a {c * 100:g} cm cube, treated as a point mass at its centre for the motion) rests at the top of a "
          f"{a_deg:g} degree wedge of {M:g} kg whose slope is L = h / sin a = {L:.4f} m = {L * 100:g} cm long ({h * 100:g} cm "
          f"tall, {L * ca * 100:.2f} cm of run); no friction between the block and the wedge; g = {g:g} m/s^2; top panel "
          f"the wedge is bolted to the floor; bottom panel the same wedge sits free on ice (no friction under it "
          f"either) and is let go with the block at the same instant; after the floor the block stops on a floor pad at "
          f"the foot of the slope (no bounce) and a buffer on the ice stops the free wedge "
          f"{'at its landing position, at the instant the block lands' if gap == 0.0 else f'{gap * 100:g} cm past its landing position'} "
          f"(a plastic stop); both bands integrated by "
          f"classical RK4 at {man['steps_per_second']} steps per second (dt = {dt:.0e} s) on the block's and the "
          f"wedge's coordinates with the normal force solved from the contact constraint at every stage, the floor "
          f"crossing located by bisection inside the step, checked against the closed forms and a half-step rerun; "
          f"shown at 1/{S:g} speed on a {P:g} s cycle ({P * fps:.0f} frames) with the release {pa:g} s into the cycle, "
          f"{cycles:.0f} cycles in {D:g} s; drawn at {ppm:g} px per metre (the wedge {L * ca * ppm:.0f} px of run and "
          f"{h * ppm:.0f} px of rise, the block {c * ppm:.0f} px square; the drawn slope runs {c / 2 * 100:g} cm past the "
          f"block's start so the whole block sits on it); deterministic, no seed")
    cf = {"bolted": closed_forms(m, M, a_deg, h, g, True), "free": closed_forms(m, M, a_deg, h, g, False)}
    runs = {"bolted": rk4_run(m, M, a_deg, h, g, dt, True), "free": rk4_run(m, M, a_deg, h, g, dt, False)}
    halves = {"bolted": rk4_run(m, M, a_deg, h, g, 0.5 * dt, True), "free": rk4_run(m, M, a_deg, h, g, 0.5 * dt, False)}
    ev: dict = {"cf": cf, "runs": runs, "halves": halves, "gap": gap}
    checks: list[tuple[str, float, float, float]] = []
    weight = m * g
    for key in PANELS:
        r, c_, hf = runs[key], cf[key], halves[key]
        yl = r["y_land"]
        v_lab = math.hypot(yl[3], yl[4])
        V = -yl[5]
        back, fwd = -yl[2], yl[0]
        E_kin = 0.5 * m * (yl[3] ** 2 + yl[4] ** 2) + 0.5 * M * yl[5] ** 2
        ang = math.degrees(math.atan2(-yl[4], yl[3]))
        a_tab = 2.0 * r["s"][-1] / r["t_land"] ** 2
        name = "bolted down (top panel)" if key == "bolted" else "free on ice (bottom panel)"
        if key == "bolted":
            wedge_phrase = "the wedge does not move (bolted): 0.00 cm"
        else:
            wedge_phrase = (f"the wedge accelerates back at A = m g sin a cos a / (M + m sin^2 a) = {c_['A']:.4f} m/s^2 and "
                            f"slides back {back * 100:.4f} cm = {back * 100:.2f} cm = {back * 100:.0f} cm (closed form "
                            f"{c_['back'] * 100:.4f} cm) at {V:.4f} m/s")
        if key == "bolted":
            mom_phrase = f"the block's horizontal momentum grows to {m * yl[3]:.4f} kg m/s (the bolts and the floor take the push)"
        else:
            mom_phrase = f"horizontal momentum of the pair m vx + M V within {r['mom_max']:.1e} kg m/s"
        line = (f"{name}: a along the slope {'g sin a' if key == 'bolted' else '(M + m) g sin a / (M + m sin^2 a)'} = "
                f"{c_['a_rel']:.4f} m/s^2 = {c_['a_rel']:.2f} m/s^2 (RK4 table 2 s / t^2 = {a_tab:.4f}, diff "
                f"{a_tab - c_['a_rel']:+.1e}); RK4: the block reaches the floor at {r['t_land']:.6f} s = {r['t_land']:.4f} s "
                f"= {r['t_land']:.2f} s (closed form sqrt(2 L / a) = {c_['t']:.6f} s, diff {r['t_land'] - c_['t']:+.1e} s), "
                f"{r['steps']} steps, moving at {v_lab:.4f} m/s = {v_lab:.2f} m/s in the lab (vx {yl[3]:.4f}, vy "
                f"{-yl[4]:.4f} down; closed form {c_['v']:.4f}, diff {v_lab - c_['v']:+.1e}), {r['s'][-1] * 100:.2f} cm "
                f"along the slope; the normal force N = {r['N']:.4f} N = {r['N'] / weight:.4f} of the block's weight "
                f"{weight:.4f} N (closed form {c_['N']:.4f} N, diff {r['N'] - c_['N']:+.1e}); {wedge_phrase}; "
                f"the block moves {fwd * 100:.4f} cm = {fwd * 100:.2f} cm forward in the lab (closed form {c_['fwd'] * 100:.4f} cm) "
                f"and {-yl[1] * 100:.2f} cm down; the sum {(fwd + back) * 100:.2f} cm is the run L cos a = {L * ca * 100:.2f} cm; "
                f"the block's lab path is {ang:.4f} degrees = {ang:.2f} degrees = {ang:.0f} degrees below horizontal (closed form "
                f"{c_['angle']:.4f}); the contact residual (block to slope, normal) stays within {r['res_max']:.1e} m; "
                f"{mom_phrase}; energy: m g h = {c_['E']:.4f} J against "
                f"the kinetic energy of block plus wedge at the floor {E_kin:.4f} J (diff {E_kin - c_['E']:+.1e} J), the balance "
                f"along the run within {r['E_max']:.1e} J; half-step rerun (dt = {0.5 * dt:.0e} s): floor at "
                f"{hf['t_land']:.9f} s ({hf['t_land'] - r['t_land']:+.1e} s)")
        print(line)
        assert abs(r["t_land"] - c_["t"]) < 1e-4 and abs(hf["t_land"] - r["t_land"]) < 1e-9, "RK4 disagrees"
        assert r["res_max"] < 1e-12 and abs(E_kin - c_["E"]) < 1e-12, "a check fails"
        assert key == "bolted" or r["mom_max"] < 1e-13, "the free pair's horizontal momentum drifts"
        ev[key] = {"t": r["t_land"], "v": v_lab, "vx": yl[3], "vy": -yl[4], "V": V, "back": back, "fwd": fwd, "ang": ang,
                   "N": r["N"], "E_kin": E_kin}
    rb, rf = runs["bolted"], runs["free"]
    ratio_a = cf["free"]["a_rel"] / cf["bolted"]["a_rel"]
    ratio_t = rb["t_land"] / rf["t_land"]
    s_b = float(np.interp(rf["t_land"], rb["t"], rb["s"]))
    ev["ratio_a"], ev["ratio_t"], ev["s_bolted_at_free"] = ratio_a, ratio_t, s_b
    print(f"the two panels: the free wedge's block accelerates along the slope {ratio_a:.4f} times as hard as the bolted one "
          f"({cf['free']['a_rel']:.4f} against {cf['bolted']['a_rel']:.4f} m/s^2; exactly (M + m) / (M + m sin^2 a) = "
          f"{(M + m) / (M + m * sa * sa):.4f}, diff {ratio_a - 1.6:+.1e}) and reaches the floor at {rf['t_land']:.4f} s against "
          f"{rb['t_land']:.4f} s, {ratio_t:.4f} times sooner = {ratio_t:.2f} times (exactly sqrt(1.6) = {math.sqrt(1.6):.4f}, diff "
          f"{ratio_t - math.sqrt(1.6):+.1e}), {(rb['t_land'] - rf['t_land']) * 1000:.1f} ms earlier; when the free block lands "
          f"at {rf['t_land']:.4f} s the bolted block is at {s_b:.4f} m = {s_b * 100:.1f} cm of {L:.3f} m along its slope "
          f"(closed form a t^2 / 2 = {0.5 * cf['bolted']['a_rel'] * rf['t_land'] ** 2:.4f} m), {s_b / L * 100:.1f} percent of "
          f"the way; the free block presses {ev['free']['N'] / weight:.4f} of its weight against {ev['bolted']['N'] / weight:.4f} "
          f"on the bolted wedge; the free block's lab path is {ev['free']['ang']:.2f} degrees below horizontal against the "
          f"{a_deg:g} degree slope; at the floor the free block moves at {ev['free']['v']:.4f} m/s in the lab against "
          f"{ev['bolted']['v']:.4f} m/s on the bolted wedge, and the wedge at {ev['free']['V']:.4f} m/s back; the free wedge "
          f"is stopped by the buffer {gap / ev['free']['V']:.4f} s after the landing, {(ev['free']['back'] + gap) * 100:.2f} "
          f"cm from its start")
    # Tables.
    ts = man["table_step_s"]
    for key in PANELS:
        r = runs[key]
        rows = []
        tt = 0.0
        while tt < r["t_land"] - 1e-12:
            rows.append(tt)
            tt += ts
        rows.append(r["t_land"])
        out = []
        for tt in rows:
            st = {k: float(np.interp(tt, r["t"], r[k])) for k in ("xb", "yb", "X", "vxb", "vyb", "s")}
            out.append(f"{tt:.4f} s: slope {st['s'] * 100:.2f} cm, block {max(0.0, -st['yb']) * 100:.2f} cm down and "
                       f"{st['xb'] * 100:.2f} cm forward, wedge {max(0.0, -st['X']) * 100:.2f} cm back, block "
                       f"{math.hypot(st['vxb'], st['vyb']):.3f} m/s")
        print(f"table {key} (RK4 table, real time after the release): " + "; ".join(out))
    # For the description: other wedge masses and other slope angles.
    descr = []
    ev["masses"], ev["angles"] = {}, {}
    for M2 in man["description_wedge_kg"]:
        c2 = closed_forms(m, M2, a_deg, h, g, False)
        r2 = rk4_run(m, M2, a_deg, h, g, dt, False)
        ev["masses"][M2] = {"ratio": c2["a_rel"] / cf["bolted"]["a_rel"], "t": r2["t_land"], "back": -r2["y_land"][2]}
        descr.append(f"wedge {M2:g} kg (block {m:g} kg, {a_deg:g} degrees): a along the slope {c2['a_rel'] / cf['bolted']['a_rel']:.4f} "
                     f"times the bolted case, the floor at {r2['t_land']:.4f} s ({rb['t_land'] / r2['t_land']:.4f} times sooner; "
                     f"closed form {c2['t']:.4f} s, diff {r2['t_land'] - c2['t']:+.1e}), the wedge back {-r2['y_land'][2] * 100:.2f} cm "
                     f"(closed form {c2['back'] * 100:.2f}), the block pressing {c2['N'] / weight:.4f} of its weight")
    for a2 in man["description_angles_deg"]:
        cb2, cf2 = closed_forms(m, M, a2, h, g, True), closed_forms(m, M, a2, h, g, False)
        rb2, rf2 = rk4_run(m, M, a2, h, g, dt, True), rk4_run(m, M, a2, h, g, dt, False)
        ev["angles"][a2] = {"ratio": cf2["a_rel"] / cb2["a_rel"], "t_b": rb2["t_land"], "t_f": rf2["t_land"]}
        descr.append(f"{a2:g} degrees (the same {h * 100:g} cm drop, {cf2['L'] * 100:.2f} cm of slope, equal masses): a ratio "
                     f"{cf2['a_rel'] / cb2['a_rel']:.4f}, bolted floor at {rb2['t_land']:.4f} s, free at {rf2['t_land']:.4f} s "
                     f"({rb2['t_land'] / rf2['t_land']:.4f} times sooner), the wedge back {-rf2['y_land'][2] * 100:.2f} cm, the free "
                     f"block pressing {cf2['N'] / weight:.4f} of its weight (closed forms {cb2['t']:.4f} and {cf2['t']:.4f} s)")
    print("for the description: " + "; ".join(descr))
    # The brief's checks.
    checks += [("bolted a (m/s^2)", cf["bolted"]["a_rel"], 4.9035, 6e-5), ("bolted floor at (s)", rb["t_land"], 0.4947, 6e-5),
               ("bolted speed at the floor (m/s)", ev["bolted"]["v"], 2.4257, 6e-5), ("bolted N (N)", ev["bolted"]["N"], 8.4931, 6e-5),
               ("bolted N / weight", ev["bolted"]["N"] / weight, 0.8660, 6e-5), ("free a_rel (m/s^2)", cf["free"]["a_rel"], 7.8456, 6e-5),
               ("a ratio", ratio_a, 1.6, 1e-12), ("free floor at (s)", rf["t_land"], 0.3911, 6e-5), ("time ratio", ratio_t, 1.2649, 6e-5),
               ("time ratio = sqrt(1.6)", ratio_t, math.sqrt(1.6), 1e-9), ("wedge A (m/s^2)", cf["free"]["A"], 3.3972, 6e-5),
               ("free N (N)", ev["free"]["N"], 6.7945, 6e-5), ("free N / weight", ev["free"]["N"] / weight, 0.6928, 6e-5),
               ("block forward (cm)", ev["free"]["fwd"] * 100, 25.98, 6e-3), ("wedge back (cm)", ev["free"]["back"] * 100, 25.98, 6e-3),
               ("block lab speed (m/s)", ev["free"]["v"], 2.0295, 6e-5), ("block vx (m/s)", ev["free"]["vx"], 1.3286, 6e-5),
               ("block vy (m/s)", ev["free"]["vy"], 1.5342, 6e-5), ("wedge speed (m/s)", ev["free"]["V"], 1.3286, 6e-5),
               ("lab path (deg)", ev["free"]["ang"], 49.11, 6e-3), ("momentum (kg m/s)", rf["mom_max"], 0.0, 1e-13),
               ("energy bolted (J)", ev["bolted"]["E_kin"], 2.9421, 6e-5), ("energy free (J)", ev["free"]["E_kin"], 2.9421, 6e-5),
               ("m g h (J)", cf["free"]["E"], 2.9421, 6e-5), ("bolted block when the free lands (m)", s_b, 0.375, 6e-4)]
    want_m = {2.0: (1.3333, 0.4284, 17.32), 5.0: (1.1429, 0.4627, 8.66), 0.5: (2.0, 0.3498, 34.64), 10.0: (1.0732, 0.4775, 4.72)}
    for M2, (wr, wt, wb) in want_m.items():
        if M2 in ev["masses"]:
            e = ev["masses"][M2]
            checks += [(f"wedge {M2:g} kg ratio", e["ratio"], wr, 6e-5), (f"wedge {M2:g} kg floor at (s)", e["t"], wt, 6e-5),
                       (f"wedge {M2:g} kg back (cm)", e["back"] * 100, wb, 6e-3)]
    want_a = {20.0: (1.7905, 0.7232, 0.5405), 45.0: (1.3333, 0.3498, 0.3029), 60.0: (1.1429, 0.2856, 0.2672)}
    for a2, (wr, wb, wf) in want_a.items():
        if a2 in ev["angles"]:
            e = ev["angles"][a2]
            checks += [(f"{a2:g} deg ratio", e["ratio"], wr, 6e-5), (f"{a2:g} deg bolted floor at (s)", e["t_b"], wb, 6e-5),
                       (f"{a2:g} deg free floor at (s)", e["t_f"], wf, 6e-5)]
    fails = 0
    out = []
    for name, got, want, tol in checks:
        ok = abs(got - want) <= tol
        fails += 0 if ok else 1
        out.append(f"{name}: brief {want:g}, sim {got:.6g}, diff {got - want:+.1e}: {'ok' if ok else 'FAIL'}")
    print(f"checks against the brief ({len(checks)} checks, {fails} failed): " + "; ".join(out))
    ev["check_fails"] = fails
    # The schedule in video time.
    t0 = man["first_cycle_at"]
    k0 = math.ceil((0.0 - t0) / P - 1e-9) - 1
    k1 = math.floor((D - t0) / P - 1e-9)
    starts = [t0 + kk * P for kk in range(k0, k1 + 1)]
    ev["cycles"] = int(round(cycles))

    def lst(off_: float) -> str:
        return ", ".join(f"{st + off_:.2f}" for st in starts if 0.0 <= st + off_ < D)

    t_stop = rf["t_land"] + gap / ev["free"]["V"]
    ev["t_stop"] = t_stop
    tau0 = (0.0 - t0) % P
    r0 = (tau0 - pa) / S
    assert pa + S * t_stop < P - F, "the free wedge is still sliding at the reset fade"
    assert pa + S * rb["t_land"] + man["settle_s"] < P - F, "the bolted block is still settling at the reset fade"
    print(f"schedule (video time, 1/{S:g} speed): cycles of {P:g} s start at " + ", ".join(f"{st:.2f}" for st in starts)
          + f" s (the first {-t0:.2f} s before the first frame); both blocks are let go {pa:g} s into each cycle at {lst(pa)} s "
          f"(the stop pins fade over {man['pin_fade_s']:g} s); the free block reaches the floor {S * rf['t_land']:.2f} s after the "
          f"release at {lst(pa + S * rf['t_land'])} s ({pa + S * rf['t_land']:.2f} s into the cycle; its event row lights, the "
          f"block settles flat on the pad over {man['settle_s']:g} s) and the buffer stops the free wedge {S * (t_stop - rf['t_land']):.2f} "
          f"s after the landing at {lst(pa + S * t_stop)} s; the bolted block reaches the floor {S * rb['t_land']:.2f} s after the release at "
          f"{lst(pa + S * rb['t_land'])} s ({pa + S * rb['t_land']:.2f} s into the cycle; its event row lights); the free block is "
          f"{float(np.interp(1.0 / S, rf['t'], rf['s'])) * 100:.1f} cm down the slope 1 s of video after the release and the bolted "
          f"{float(np.interp(1.0 / S, rb['t'], rb['s'])) * 100:.1f} cm, after 2 s {float(np.interp(2.0 / S, rf['t'], rf['s'])) * 100:.1f} "
          f"and {float(np.interp(2.0 / S, rb['t'], rb['s'])) * 100:.1f} cm; the reset crossfade runs over the last {F:g} s of each cycle "
          f"(from {lst(P - F)} s; the readouts out over its first half and in over its second); on the first frame the cycle is "
          f"{tau0:.2f} s in ({r0:.3f} s real: both blocks held at the top); title until {man['title_until']:g} s; payoff card from "
          f"{man['payoff_t']:g} s; the title fades back in over the last {man['loop_fade']:g} s and the last frame repeats the first "
          f"(the scene is periodic: {D:g} s holds exactly {cycles:.0f} cycles)")
    # Text widths.
    font = os.environ["SEED_ZERO_FONT"]
    f24, f28, f34, f40, f56 = (ImageFont.truetype(font, n) for n in (24, 28, 34, 40, 56))
    widths = {"overlay@34": (f34, man["overlay"])}
    for j, line in enumerate(man["title"].split("|")):
        widths[f"title line {j + 1}@56"] = (f56, line)
    widths["legend@40"] = (f40, legend_text(man))
    widths["clock@28"] = (f28, clock_text(1.125))
    widths["clock held@28"] = (f28, clock_text(-1.0))
    for key in PANELS:
        widths[f"label {key}@40"] = (f40, label_text(key))
        widths[f"slope {key}@40"] = (f40, slope_text(L, L))
        widths[f"block {key}@28"] = (f28, block_text(h))
        widths[f"speed {key}@28"] = (f28, speed_text(ev[key]["v"]))
        widths[f"wedge {key}@28"] = (f28, wedge_text(key, ev["free"]["back"] + gap))
        widths[f"press {key}@28"] = (f28, press_text(ev[key]["N"] / weight))
        widths[f"event {key}@40"] = (f40, event_text(ev, key))
    widths["wedge mass@24"] = (f24, mass_text(M))
    widths["ice@24"] = (f24, ice_text())
    for j, line in enumerate(payoff_lines(man, ev)):
        widths[f"payoff line {j + 1}@40"] = (f40, line)
    print("text widths (the on-screen strings verbatim): " + ", ".join(f"{kk} {f.getlength(s):.0f} px {s!r}" for kk, (f, s) in widths.items()))
    assert all(f.getlength(s) < 950 for f, s in widths.values()), "a text line is wider than 950 px"
    assert len(payoff_lines(man, ev)) <= 6, "the card has more than six lines"
    assert len(man["title"].replace("|", " ")) <= 100 and "<" not in man["title"] and ">" not in man["title"]
    # Layout checks.
    left = ROW_X0 + max(max(f40.getlength(label_text(key)), f28.getlength(block_text(h)), f28.getlength(speed_text(ev[key]["v"])))
                        for key in PANELS)
    right = ROW_X1 - max(max(f40.getlength(slope_text(L, L)), f28.getlength(wedge_text(key, ev["free"]["back"] + gap)),
                             f28.getlength(press_text(ev[key]["N"] / weight))) for key in PANELS)
    rows_bottom = FIX_DY + 14
    floor = float(man["floor_dy"])
    foot = float(man["foot_x_px"])
    apex_x, apex_y = foot - L * ca * ppm, floor - h * ppm
    ext = c / 2.0 * ppm
    top_x, top_y = apex_x - ext * ca, apex_y - ext * sa          # the drawn apex (the slope extended by half a block)
    half = c / 2.0 * ppm
    blk_top = apex_y - half * ca - half * (sa + ca)              # the block's highest corner at the start
    blk_left = apex_x + half * sa - half * (sa + ca)
    back_px = ev["free"]["back"] * ppm
    buf_face = top_x - back_px - gap * ppm
    land_x = {key: apex_x + ev[key]["fwd"] * ppm for key in PANELS}
    pad_x = {key: foot + (ev[key]["fwd"] - L * ca) * ppm for key in PANELS}
    ev_w = max(f40.getlength(event_text(ev, key)) for key in PANELS)
    ev_y0, ev_y1 = EVENT_DY - 20, EVENT_DY + 20
    label_x = top_x + 150.0 - back_px
    print(f"row check: the left column ends at x {left:.0f} px, the right column starts at x {right:.0f} px; both end "
          f"{rows_bottom} px under the band top; the floor surface is {floor:.0f} px under the band top, the slab to "
          f"{floor + SLAB_PX:.0f} px; the event row spans {ev_y0} to {ev_y1} px under the band top and x {EVENT_X - ev_w / 2:.0f} "
          f"to {EVENT_X + ev_w / 2:.0f} px (widest {ev_w:.0f} px, centred on {EVENT_X}); the wedge's foot starts at x {foot:.0f}, "
          f"the block's start (the top of the slope) at x {apex_x:.1f}, {apex_y:.1f} px under the band top, the drawn apex at x "
          f"{top_x:.1f}, {top_y:.1f} px (the slope extended {ext:.0f} px); the block's highest corner at the start is {blk_top:.1f} "
          f"px under the band top and its leftmost corner at x {blk_left:.1f}; the free wedge slides {back_px:.1f} px left to its "
          f"landing position (drawn apex at x {top_x - back_px:.1f}) and {gap * ppm:.0f} px more to the buffer face at x {buf_face:.0f} "
          f"(the buffer from x {buf_face - BUFFER_W:.0f}); the blocks land with their centres at x {land_x['bolted']:.1f} (bolted) and "
          f"{land_x['free']:.1f} (free) px and settle flat on the pads at x {pad_x['bolted']:.0f} to {pad_x['bolted'] + PAD_W:.0f} and "
          f"{pad_x['free']:.0f} to {pad_x['free'] + PAD_W:.0f}; the wedge mass label sits at x {label_x:.0f} at its furthest left; "
          f"each band is {BAND_H} px tall (y {BAND_Y['bolted']} to {BAND_Y['bolted'] + BAND_H} and {BAND_Y['free']} to "
          f"{BAND_Y['free'] + BAND_H}); the caption band starts at y {int(man['caption_y'] * H)}; the title rows end at y "
          f"{TITLE_Y[-1] + 28} and the overlay band ends at y 130")
    assert right - left > 40, "the columns meet"
    assert blk_top > rows_bottom + 16, "the block at the top meets the text rows"
    assert blk_left > 20 and buf_face - BUFFER_W > 20, "the geometry leaves the frame on the left"
    assert land_x["bolted"] + 2 * half + 20 < W - 20, "the bolted block leaves the frame on the right"
    assert ev_y0 > floor + SLAB_PX + 12 and ev_y1 < BAND_H - 8, "the event row leaves the slab space"
    assert EVENT_X - ev_w / 2 > 20 and EVENT_X + ev_w / 2 < W - 20, "the event row leaves the frame"
    assert top_y > rows_bottom + 16, "the wedge apex meets the text rows"
    assert BAND_Y["free"] + BAND_H <= int(man["caption_y"] * H), "the bottom band reaches the caption band"
    assert PAYOFF_Y - 20 > int(man["caption_y"] * H) + 90, "the card meets the caption band"
    assert TITLE_Y[-1] + 28 <= BAND_Y["bolted"], "the title rows reach the first band"
    return ev


def legend_text(man: dict) -> str:
    return f"same block, same wedge, 1/{man['slow']:g} speed"


def clock_text(r: float) -> str:
    return "held, at rest" if r < 0.0 else f"{r:.3f} s after the release"


def label_text(key: str) -> str:
    return "bolted down" if key == "bolted" else "free on ice"


def slope_text(s: float, L: float) -> str:
    return f"slope: {max(0.0, s) * 100:.1f} of {L * 100:.0f} cm"


def block_text(drop: float) -> str:
    return f"block: {max(0.0, drop) * 100:.1f} cm down"


def speed_text(v: float) -> str:
    return f"speed {abs(v):.2f} m/s"


def wedge_text(key: str, back: float) -> str:
    return "wedge: bolted, 0.0 cm" if key == "bolted" else f"wedge: {max(0.0, back) * 100:.1f} cm back"


def press_text(frac: float) -> str:
    return f"presses {frac:.2f} of its weight"


def event_text(ev: dict, key: str) -> str:
    if key == "bolted":
        return f"bolted: floor at {ev['bolted']['t']:.2f} s"
    return f"free: floor at {ev['free']['t']:.2f} s, {ev['ratio_t']:.2f}x sooner"


def mass_text(M: float) -> str:
    return f"{M:g} kg"


def ice_text() -> str:
    return "ice"


def payoff_lines(man: dict, ev: dict) -> list[str]:
    cf = ev["cf"]
    text = man["payoff_text"].format(
        t_free=ev["free"]["t"], t_bolted=ev["bolted"]["t"], ratio_t=ev["ratio_t"], ratio_a=ev["ratio_a"],
        a_free=cf["free"]["a_rel"], a_bolted=cf["bolted"]["a_rel"], back=ev["free"]["back"] * 100, fwd=ev["free"]["fwd"] * 100,
        ang=ev["free"]["ang"], press_free=ev["free"]["N"] / (man["block_kg"] * man["g"]),
        press_bolted=ev["bolted"]["N"] / (man["block_kg"] * man["g"]),
        r2=ev["masses"][2.0]["ratio"], t2=ev["masses"][2.0]["t"], t5=ev["masses"][5.0]["t"])
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
        self.S = man["slow"]
        self.P = man["cycle_s"]
        self.P_f = int(round(man["cycle_s"] * self.fps))
        self.c0_f = int(round(man["first_cycle_at"] * self.fps))
        self.pa, self.F = man["release_at"], man["reset_fade"]
        self.runs = ev["runs"]
        self.gap = ev["gap"]
        self.a = math.radians(man["angle_deg"])
        self.sa, self.ca = math.sin(self.a), math.cos(self.a)
        self.L, self.h = man["height_m"] / self.sa, man["height_m"]
        self.half = man["block_side_m"] / 2.0 * self.ppm
        self.floor = float(man["floor_dy"])
        self.foot = float(man["foot_x_px"])
        self.apex_x = self.foot - self.L * self.ca * self.ppm
        self.apex_y = self.floor - self.h * self.ppm
        ext = self.half
        self.top_x, self.top_y = self.apex_x - ext * self.ca, self.apex_y - ext * self.sa
        self.M = man["wedge_kg"]

    def phase(self, f: int) -> tuple[int, float]:
        k, tau_f = divmod(f - self.c0_f, self.P_f)
        return k, tau_f / self.fps

    @staticmethod
    def L_(x: float, y: float) -> tuple[float, float]:
        """Layer (2x) pixel of a band-local point, rounded to 1e-4 px so equal states draw equal pixels."""
        return round(x * SS, 4), round(y * SS, 4)

    def lab(self, x_m: float, y_m: float) -> tuple[float, float]:
        """Band-local px of a lab point measured from the block's start (y up)."""
        return self.apex_x + x_m * self.ppm, self.apex_y - y_m * self.ppm

    def block_pose(self, key: str, st: dict) -> tuple[float, float, float]:
        """(cx, cy, angle) of the drawn block: on the slope its centre sits half a side off the surface along
        the normal; after the floor it settles flat on the pad over settle_s seconds of video."""
        px, py = self.lab(st["xb"], st["yb"])
        cx, cy = px + self.half * self.sa, py - self.half * self.ca
        ang = self.a
        if st["phase"] == DOWN:
            u = min(1.0, max(0.0, (st["tv"] - self.S * self.runs[key]["t_land"]) / self.man["settle_s"]))
            fx, fy = px + self.half + 4.0, self.floor - self.half
            cx, cy, ang = cx + (fx - cx) * u, cy + (fy - cy) * u, self.a * (1.0 - u)
        return cx, cy, ang

    def draw_ground(self, d: ImageDraw.ImageDraw, key: str) -> None:
        s0, s1 = self.L_(-12.0, self.floor), self.L_(W + 12.0, self.floor + SLAB_PX)
        d.rectangle((s0[0], s0[1], s1[0], s1[1]), fill=DECK_A)
        d.line((*self.L_(-12.0, self.floor), *self.L_(W + 12.0, self.floor)), fill=DECK_B, width=3 * SS)
        if key == "free":
            back_px = self.ev["free"]["back"] * self.ppm
            x0 = self.top_x - back_px - self.gap * self.ppm - BUFFER_W - 6.0
            x1 = self.foot + 24.0
            i0, i1 = self.L_(x0, self.floor), self.L_(x1, self.floor + ICE_PX)
            d.rectangle((i0[0], i0[1], i1[0], i1[1]), fill=ICE)
            d.line((*self.L_(x0, self.floor), *self.L_(x1, self.floor)), fill=ICE_HI, width=2 * SS)
            # The buffer: a short post on the floor at the end of the wedge's run.
            bx = self.top_x - back_px - self.gap * self.ppm
            b0, b1 = self.L_(bx - BUFFER_W, self.floor - BUFFER_H), self.L_(bx, self.floor)
            d.rectangle((b0[0], b0[1], b1[0], b1[1]), fill=BUFFER, outline=RIM, width=2 * SS)
        # The floor pad where the block lands.
        pad_x = self.foot + (self.ev[key]["fwd"] - self.L * self.ca) * self.ppm
        p0, p1 = self.L_(pad_x, self.floor), self.L_(pad_x + PAD_W, self.floor + PAD_PX)
        d.rectangle((p0[0], p0[1], p1[0], p1[1]), fill=PAD)

    def draw_wedge(self, d: ImageDraw.ImageDraw, key: str, X: float) -> None:
        dx = X * self.ppm
        tx, ty = self.top_x + dx, self.top_y
        fx = self.foot + dx
        poly = [self.L_(tx, ty), self.L_(fx, self.floor), self.L_(tx, self.floor)]
        d.polygon(poly, fill=WEDGE_FILL, outline=WEDGE_EDGE, width=2 * SS)
        d.line((*self.L_(tx, ty), *self.L_(fx, self.floor)), fill=TEXT, width=3 * SS)
        if key == "bolted":
            for bx in (tx + 26.0, fx - 46.0):
                by = self.floor - 9.0
                b = self.L_(bx, by)
                r = 6.0 * SS
                d.ellipse((b[0] - r, b[1] - r, b[0] + r, b[1] + r), fill=BOLT, outline=BOLT_DARK, width=SS)
                d.line((b[0] - r * 0.6, b[1] - r * 0.6, b[0] + r * 0.6, b[1] + r * 0.6), fill=BOLT_DARK, width=SS)
                d.line((b[0] - r * 0.6, b[1] + r * 0.6, b[0] + r * 0.6, b[1] - r * 0.6), fill=BOLT_DARK, width=SS)

    def draw_trail(self, d: ImageDraw.ImageDraw, key: str, st: dict) -> None:
        if st["phase"] == HELD:
            return
        px0, py0 = self.lab(0.0, 0.0)
        px1, py1 = self.lab(st["xb"], st["yb"])
        x0, y0 = px0 + self.half * self.sa, py0 - self.half * self.ca
        x1, y1 = px1 + self.half * self.sa, py1 - self.half * self.ca
        length = math.hypot(x1 - x0, y1 - y0)
        if length < 1e-6:
            return
        ux, uy = (x1 - x0) / length, (y1 - y0) / length
        s = 0.0
        while s < length:
            e = min(length, s + 5.0)
            d.line((*self.L_(x0 + ux * s, y0 + uy * s), *self.L_(x0 + ux * e, y0 + uy * e)), fill=TRAIL, width=2 * SS)
            s = e + 7.0

    def draw_pin(self, d: ImageDraw.ImageDraw, tv: float) -> None:
        """A stop pin just downhill of the held block, normal to the slope, fading after the release."""
        a = 1.0 if tv < 0.0 else max(0.0, 1.0 - tv / self.man["pin_fade_s"])
        if a <= 0.0:
            return
        s_px = self.half + PIN_W / 2.0 + 2.0
        bx, by = self.apex_x + s_px * self.ca, self.apex_y + s_px * self.sa
        ex, ey = bx + PIN_LEN * self.sa, by - PIN_LEN * self.ca
        d.line((*self.L_(bx, by), *self.L_(ex, ey)), fill=blend(GOLD, a), width=PIN_W * SS)

    def draw_block(self, d: ImageDraw.ImageDraw, cx: float, cy: float, ang: float) -> None:
        ca, sa = math.cos(ang), math.sin(ang)
        hh = self.half

        def rot(u: float, v: float) -> tuple[float, float]:
            # u along the slope (down-right), v up from the surface; screen y down.
            return self.L_(cx + u * ca + v * sa, cy + u * sa - v * ca)

        body = [rot(-hh, -hh), rot(hh, -hh), rot(hh, hh), rot(-hh, hh)]
        d.polygon(body, fill=BLOCK_FILL, outline=BLOCK_EDGE, width=2 * SS)
        d.line((*rot(-hh + 5, hh - 5), *rot(hh - 5, hh - 5)), fill=BLOCK_HI, width=2 * SS)

    def scene(self, key: str, tau: float) -> tuple[Image.Image, dict]:
        """The band layer of panel key at tau seconds into a cycle (the held setup before the release)."""
        layer = Image.new("RGB", (W * SS, BAND_H * SS), BG)
        d = ImageDraw.Draw(layer)
        tv = tau - self.pa
        rt = tv / self.S
        st = state_at(self.runs[key], rt, self.gap)
        st["tv"], st["rt"] = tv, rt
        self.draw_wedge(d, key, st["X"])
        self.draw_trail(d, key, st)
        self.draw_pin(d, tv)
        cx, cy, ang = self.block_pose(key, st)
        self.draw_block(d, cx, cy, ang)
        self.draw_ground(d, key)   # drawn last: the slab hides the settling block's corner under the floor line
        return layer, st

    def draw_panel(self, key: str, f: int) -> tuple[Image.Image, dict]:
        k, tau = self.phase(f)
        P, F = self.P, self.F
        layer, st = self.scene(key, tau)
        st["alpha"], st["k"] = 1.0, k
        if tau >= P - F:
            # Crossfade to the next cycle's held setup (the free wedge rests at the buffer by now, asserted).
            a = (tau - (P - F)) / F
            new, st_new = self.scene(key, tau - P)
            layer = Image.blend(layer, new, a)
            st["alpha"] = max(0.0, 1.0 - 2.0 * a)
            st_new["alpha"], st_new["k"] = max(0.0, 2.0 * a - 1.0), k + 1
            if a >= 0.5:
                st = st_new
        return layer, st

    def draw_text(self, d: ImageDraw.ImageDraw, states: dict, hud_alpha: float) -> None:
        man, ev = self.man, self.ev
        weight = man["block_kg"] * man["g"]
        for key, st in states.items():
            y0 = BAND_Y[key]
            a, ph = st["alpha"], st["phase"]
            landed = ph == DOWN
            d.text((ROW_X0, y0 + LABEL_DY), label_text(key), font=self.font, fill=COLOUR[key], anchor="lm")
            d.text((ROW_X0, y0 + SUB_DY), block_text(-st["yb"]), font=self.font_small, fill=blend(GOLD if landed else TEXT, a),
                   anchor="lm")
            d.text((ROW_X0, y0 + FIX_DY), speed_text(math.hypot(st["vxb"], st["vyb"])), font=self.font_small,
                   fill=blend(MUTED, a), anchor="lm")
            d.text((ROW_X1, y0 + LABEL_DY), slope_text(st["s"], self.L), font=self.font,
                   fill=blend(GOLD if landed else TEXT, a), anchor="rm")
            wedge_lit = key == "free" and st["wedge_stopped"]
            d.text((ROW_X1, y0 + SUB_DY), wedge_text(key, -st["X"]), font=self.font_small,
                   fill=blend(GOLD if wedge_lit else TEXT, a), anchor="rm")
            d.text((ROW_X1, y0 + FIX_DY), press_text(ev[key]["N"] / weight), font=self.font_small, fill=blend(MUTED, a),
                   anchor="rm")
            if landed:
                d.text((EVENT_X, y0 + EVENT_DY), event_text(ev, key), font=self.font, fill=blend(GOLD, a), anchor="mm")
            # The wedge's mass inside its body (moves with it) and the ice label.
            lx = self.top_x + st["X"] * self.ppm + 150.0
            d.text((lx, y0 + self.floor - 34.0), mass_text(self.M), font=self.font_tiny, fill=INK, anchor="mm")
            if key == "free":
                d.text((self.foot + 60.0, y0 + self.floor + 5.0), ice_text(), font=self.font_tiny, fill=ICE, anchor="lm")
        if hud_alpha > 0.02:
            d.text((W / 2, LEGEND_Y), legend_text(man), font=self.font, fill=blend(TEXT, hud_alpha), anchor="mm")
            d.text((W / 2, CLOCK_Y), clock_text(states["bolted"]["rt"]), font=self.font_small,
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
        for key in PANELS:
            layer, states[key] = self.draw_panel(key, f)
            img.paste(layer.reduce(SS), (0, BAND_Y[key]))
        d = ImageDraw.Draw(img)
        self.draw_text(d, states, hud_alpha)
        if title_alpha > 0.0:
            for j, line in enumerate(man["title"].split("|")):
                d.text((W / 2, TITLE_Y[j]), line, font=self.font_title, fill=blend(TEXT, title_alpha), anchor="mm")
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
            # The geometry runs on; the legend, clock and card fade out over the first half of the loop
            # fade and the title fades in over the second half, so the two never overlap.
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
    man = json.loads((ROOT / "projects/wedge/manifest.json").read_text())
    ev = measure(man)
    if "--measure-only" in sys.argv:
        return
    if "--frames" in sys.argv:
        times = [float(v) for v in sys.argv[sys.argv.index("--frames") + 1].split(",")]
        r = Renderer(man, ev)
        (ROOT / "media/wedge").mkdir(parents=True, exist_ok=True)
        for tv in times:
            Image.fromarray(r.frame_at(int(round(tv * man["fps"])))).save(ROOT / f"media/wedge/smoke-{tv}.png")
        print("smoke frames: " + ", ".join(f"{tv}" for tv in times))
        return
    Renderer(man, ev).render(ROOT / "media/wedge/footage.mp4")


if __name__ == "__main__":
    main()
