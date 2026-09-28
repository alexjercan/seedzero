#!/usr/bin/env python3
"""Head-on at 50: is that a wall at 100?

Three crashes on one clock, side view, stacked, the same horizontal scale.
A car is a rigid body of mass m with a crumple zone at its front that acts
as a linear spring of stiffness k while it compresses and locks at maximum
compression (a car does not spring back; the crushed cars stay where they
stop). Lane 1: two identical cars at v head-on, bumpers touching at t = 0;
the two crumple springs act in series between the two bodies, the massless
contact plane sits where the two spring forces balance, and each car's
crush is its own spring's compression. Lane 2: one car at v into a rigid
wall. Lane 3: one car at 2 v into the same wall. All three impacts start
at the same instant (the 2 v car gets twice the run-up). Each lane is
integrated by RK4 at steps_per_second and the lock is located by bisection
inside the step; every number is checked against the closed forms x_max =
v sqrt(m / k), t_max = (pi / 2) sqrt(m / k), a_peak = v sqrt(k / m) and
m v^2 / 2 = k x_max^2 / 2. Shown at 1/slow speed; the crash repeats every
cycle_s seconds of video with a fade back to the run-up; the cycle divides
the scene length, so the scene is exactly periodic and the last frame
equals the first. Deterministic, no seed.

Measured and printed: the closed forms for each lane; the RK4 crush per
car, the time to maximum crush, the peak deceleration in m/s^2 and g, the
energy check and the RK4 error against the closed form for each lane; the
contact plane's largest displacement in the head-on and the momentum
check; the head-on per car against the wall at v, the wall at 2 v against
the wall at v (the 2.00 ratio), and the total head-on crush against the
wall at 2 v; the constant-force crumple for comparison (the 4x); the
crush at other speeds for the description; the run schedule in video
time; the on-screen text widths.

usage: crash.py [--measure-only] [--frames t1,t2,...]
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
WIRE = (70, 80, 94)
GROUND = (52, 60, 72)
WALL = (96, 108, 126)
WALL_DARK = (60, 68, 80)
BODY = (78, 150, 196)
BODY_DARK = (44, 90, 122)
GLASS = (168, 206, 232)
TYRE = (26, 30, 36)
RIM = (150, 158, 170)
CREASE = (140, 44, 40)
BUMPER = (40, 44, 52)

# Layout: overlay at y 96..130 (captions.py), two title rows at y 190/252 for
# the first seconds, then the legend at y 236 and the shared clock at y 290;
# three lanes stacked in the bands lane_y (340..700, 700..1060, 1060..1420),
# each drawn at 2x in its own layer, with its label row 36 px under the band
# top, the speed labels 92 px under, the ground 250 px under (cars 1.35 m =
# 135 px tall stand on it), the crush readouts at 300 and the plane readout
# at 340; the contact plane and the wall face at plane_x_px in every lane;
# captions at caption_y 0.75 (y 1440..1520); the five-line card from y 1580
# at a 52 px pitch.
LEGEND_Y, CLOCK_Y = 236, 290
SS = 2
PAYOFF_Y, PAYOFF_PITCH = 1580.0, 52
LABEL_DY, SPEED_DY, GROUND_DY, READ_DY, PLANE_DY = 36, 92, 250, 300, 340
ROW_X0, ROW_X1 = 90, 990
CAR_H = 1.35
WALL_W_PX = 60
LANES = ("headon", "wall", "wall2")
LANE_TITLE = {"headon": "head-on, {v:g} + {v:g} km/h", "wall": "wall, {v:g} km/h", "wall2": "wall, {v:g} km/h"}


def blend(col, a: float, base=BG) -> tuple:
    a = max(0.0, min(1.0, a))
    return tuple(int(round(c * a + b * (1 - a))) for c, b in zip(col, base))


# --- integration ---------------------------------------------------------------
def rk4(deriv, y: list[float], h: float) -> list[float]:
    k1 = deriv(y)
    k2 = deriv([a + 0.5 * h * b for a, b in zip(y, k1)])
    k3 = deriv([a + 0.5 * h * b for a, b in zip(y, k2)])
    k4 = deriv([a + h * b for a, b in zip(y, k3)])
    return [a + h / 6.0 * (b1 + 2.0 * b2 + 2.0 * b3 + b4) for a, b1, b2, b3, b4 in zip(y, k1, k2, k3, k4)]


def integrate(deriv, y0: list[float], closing, dt: float, t_max: float) -> dict:
    """RK4 from y0 until the closing rate closing(y) reaches zero (the lock), located by bisection
    inside the step; returns the sampled states (the lock state appended) and the lock time."""
    ts, ys = [0.0], [list(y0)]
    t, y = 0.0, list(y0)
    n = int(round(t_max / dt))
    for _ in range(n):
        yn = rk4(deriv, y, dt)
        if closing(yn) <= 0.0:
            lo, hi = 0.0, dt
            for _ in range(60):
                mid = 0.5 * (lo + hi)
                if closing(rk4(deriv, y, mid)) > 0.0:
                    lo = mid
                else:
                    hi = mid
            y = rk4(deriv, y, hi)
            t += hi
            ts.append(t)
            ys.append(y)
            return {"t": np.array(ts), "y": np.array(ys), "t_lock": t, "locked": True}
        y, t = yn, t + dt
        ts.append(t)
        ys.append(y)
    return {"t": np.array(ts), "y": np.array(ys), "t_lock": None, "locked": False}


def crash_wall(m: float, v0: float, dt: float, law, t_max: float = 0.5) -> dict:
    """One car at v0 into a rigid wall: x is the crush (the body's travel past the wall face)."""
    def deriv(y):
        return [y[1], -law(y[0]) / m]
    run = integrate(deriv, [0.0, v0], lambda y: y[1], dt, t_max)
    x, v = run["y"][:, 0], run["y"][:, 1]
    acc = np.array([law(c) / m for c in x])
    run.update({"crush": x, "v": v, "acc": acc, "c_max": float(x[-1]), "a_peak": float(acc.max()),
                "e_spring": None})
    return run


def crash_headon(m: float, v0: float, dt: float, law, inv_law, t_max: float = 0.5) -> dict:
    """Two identical cars at v0 head-on: xA, xB are the body displacements (+x is car A's heading),
    the closure s = xA - xB is shared by the two crumple springs in series so that their forces
    balance (inv_law maps the closure to car A's share; for identical linear springs F(cA) =
    F(cB) gives cA = cB = s / 2), and the contact plane sits at xA - cA."""
    def split(s: float) -> float:
        if s <= 0.0:
            return 0.0
        return inv_law(s)

    def deriv(y):
        s = y[0] - y[2]
        cA = split(s)
        cB = s - cA
        return [y[1], -law(cA) / m, y[3], law(cB) / m]

    run = integrate(deriv, [0.0, v0, 0.0, -v0], lambda y: y[1] - y[3], dt, t_max)
    ya = run["y"]
    s = ya[:, 0] - ya[:, 2]
    cA = np.array([split(si) for si in s])
    cB = s - cA
    p = ya[:, 0] - cA
    accA = np.array([law(c) / m for c in cA])
    accB = np.array([law(c) / m for c in cB])
    run.update({"cA": cA, "cB": cB, "plane": p, "xA": ya[:, 0], "xB": ya[:, 2], "vA": ya[:, 1], "vB": ya[:, 3],
                "accA": accA, "accB": accB, "momentum": m * (ya[:, 1] + ya[:, 3])})
    return run


def spring_law(k: float):
    return (lambda c: k * c), (lambda s: 0.5 * s)


def state_lookup(run: dict, key: str, r: float) -> float:
    """Value of the sampled quantity key at real time r after impact (held after the lock)."""
    if r <= 0.0:
        return float(run[key][0])
    if r >= run["t"][-1]:
        return float(run[key][-1])
    return float(np.interp(r, run["t"], run[key]))


# --- measurement ---------------------------------------------------------------
def closed_forms(m: float, k: float, v: float, g: float) -> dict:
    tau = math.sqrt(m / k)
    return {"x": v * tau, "t": 0.5 * math.pi * tau, "a": v / tau, "g": v / tau / g, "e": 0.5 * m * v * v}


def measure(man: dict) -> dict:
    m, k, g = man["car_mass_kg"], man["crumple_k_n_m"], man["g_m_s2"]
    v1, v2 = man["speed_km_h"] / 3.6, man["fast_speed_km_h"] / 3.6
    dt = 1.0 / man["steps_per_second"]
    S, P, D, fps, F = man["slow"], man["cycle_s"], man["scene_duration"], man["fps"], man["reset_fade"]
    ia, Lz = man["impact_at"], man["crumple_zone_m"]
    cycles = D / P
    assert abs(cycles - round(cycles)) < 1e-9, "the crash cycle must divide the scene length"
    for key in ("cycle_s", "impact_at", "first_cycle_at", "reset_fade"):
        assert abs(man[key] * fps - round(man[key] * fps)) < 1e-9, f"{key} must be a whole number of frames"
    ppm = man["px_per_m"]
    print(f"setup: a car is a rigid body of {m:g} kg with a {Lz:g} m crumple zone at its front that acts as a linear "
          f"spring of k = {k:g} N/m while it compresses and locks at maximum compression (no spring-back); lane 1: two "
          f"identical cars at {man['speed_km_h']:g} km/h = {v1:.4f} m/s head-on, bumpers touching at t = 0, the two "
          f"crumple springs in series between the two bodies with the massless contact plane where their forces "
          f"balance; lane 2: one car at {man['speed_km_h']:g} km/h into a rigid wall; lane 3: one car at "
          f"{man['fast_speed_km_h']:g} km/h = {v2:.4f} m/s into the same wall; all three impacts at the same instant, "
          f"integrated by RK4 at {man['steps_per_second']} steps per second (dt = {dt:.0e} s) with the lock located by "
          f"bisection inside the step; shown at 1/{S:g} speed on a {P:g} s cycle ({P * fps:.0f} frames) with the "
          f"impact {ia:g} s into the cycle ({ia / S * 1000:.1f} ms of run-up, {v1 * ia / S:.3f} m at "
          f"{man['speed_km_h']:g} km/h and {v2 * ia / S:.3f} m at {man['fast_speed_km_h']:g}), {cycles:.0f} cycles in "
          f"{D:g} s; drawn at {ppm:g} px per metre, {man['car_length_m']:g} m cars; deterministic, no seed")
    tau = math.sqrt(m / k)
    cf1, cf2 = closed_forms(m, k, v1, g), closed_forms(m, k, v2, g)
    print(f"closed forms (x_max = v sqrt(m / k), t_max = (pi / 2) sqrt(m / k), a_peak = v sqrt(k / m), g = {g:g}): "
          f"sqrt(m / k) = {tau:.6f} s, sqrt(k / m) = {1 / tau:.4f} 1/s; at {man['speed_km_h']:g} km/h x_max = "
          f"{cf1['x']:.4f} m = {cf1['x'] * 100:.2f} cm, t_max = {cf1['t'] * 1000:.2f} ms, a_peak = {cf1['a']:.1f} "
          f"m/s^2 = {cf1['g']:.2f} g, kinetic energy m v^2 / 2 = {cf1['e'] / 1000:.2f} kJ = k x_max^2 / 2 = "
          f"{0.5 * k * cf1['x'] ** 2 / 1000:.2f} kJ; at {man['fast_speed_km_h']:g} km/h x_max = {cf2['x']:.4f} m = "
          f"{cf2['x'] * 100:.2f} cm, t_max = {cf2['t'] * 1000:.2f} ms (the same), a_peak = {cf2['a']:.1f} m/s^2 = "
          f"{cf2['g']:.2f} g, energy {cf2['e'] / 1000:.2f} kJ = {0.5 * k * cf2['x'] ** 2 / 1000:.2f} kJ; the crush "
          f"is proportional to the speed, ratio {cf2['x'] / cf1['x']:.4f}")
    law, inv = spring_law(k)
    ho = crash_headon(m, v1, dt, law, inv)
    w1 = crash_wall(m, v1, dt, law)
    w2 = crash_wall(m, v2, dt, law)
    assert ho["locked"] and w1["locked"] and w2["locked"], "every lane must reach its lock"
    omega = 1.0 / tau
    # Lane 1.
    tl = ho["t_lock"]
    err1 = float(np.max(np.abs(ho["cA"] - v1 / omega * np.sin(omega * ho["t"]))))
    e_kin = 2 * 0.5 * m * v1 * v1
    e_spr = 0.5 * k * ho["cA"][-1] ** 2 + 0.5 * k * ho["cB"][-1] ** 2
    print(f"lane 1, head-on at {man['speed_km_h']:g} + {man['speed_km_h']:g} km/h (RK4, two bodies, {len(ho['t']) - 1} "
          f"steps): the crumple springs lock at t = {tl * 1000:.2f} ms (closed form {cf1['t'] * 1000:.2f}, diff "
          f"{abs(tl - cf1['t']) * 1000:.1e} ms) with car A crushed {ho['cA'][-1] * 100:.2f} cm and car B crushed "
          f"{ho['cB'][-1] * 100:.2f} cm (closed form {cf1['x'] * 100:.2f} cm each, diff "
          f"{abs(ho['cA'][-1] - cf1['x']) * 100:.1e} cm), {(ho['cA'][-1] + ho['cB'][-1]) * 100:.2f} cm of crush in "
          f"all; the contact plane's largest displacement is {np.max(np.abs(ho['plane'])) * 1000:.4f} mm (it never "
          f"moves: each car meets an immovable plane); both cars stop: speeds at the lock {ho['vA'][-1]:.2e} and "
          f"{ho['vB'][-1]:.2e} m/s; peak deceleration {ho['accA'].max():.1f} m/s^2 = {ho['accA'].max() / g:.2f} g "
          f"(car A) and {ho['accB'].max():.1f} m/s^2 (car B); total momentum stays within "
          f"{np.max(np.abs(ho['momentum'])):.1e} kg m/s of zero; kinetic energy of both cars {e_kin / 1000:.2f} kJ, "
          f"stored in the two springs at the lock {e_spr / 1000:.2f} kJ (diff {abs(e_kin - e_spr):.1e} J); RK4 stays "
          f"within {err1:.1e} m of the closed form x = (v / omega) sin(omega t)")
    # Lanes 2 and 3.
    out = {}
    for name, run, cf, kmh in (("lane 2", w1, cf1, man["speed_km_h"]), ("lane 3", w2, cf2, man["fast_speed_km_h"])):
        v = kmh / 3.6
        err = float(np.max(np.abs(run["crush"] - v / omega * np.sin(omega * run["t"]))))
        e_s = 0.5 * k * run["c_max"] ** 2
        print(f"{name}, one car at {kmh:g} km/h into the wall (RK4, {len(run['t']) - 1} steps): the crumple spring "
              f"locks at t = {run['t_lock'] * 1000:.2f} ms (closed form {cf['t'] * 1000:.2f}, diff "
              f"{abs(run['t_lock'] - cf['t']) * 1000:.1e} ms) with the car crushed {run['c_max'] * 100:.2f} cm (closed "
              f"form {cf['x'] * 100:.2f}, diff {abs(run['c_max'] - cf['x']) * 100:.1e} cm); the car stops: speed at "
              f"the lock {run['v'][-1]:.2e} m/s; peak deceleration {run['a_peak']:.1f} m/s^2 = {run['a_peak'] / g:.2f} "
              f"g (closed form {cf['a']:.1f} m/s^2 = {cf['g']:.2f} g); kinetic energy {0.5 * m * v * v / 1000:.2f} kJ, "
              f"stored in the spring at the lock {e_s / 1000:.2f} kJ (diff {abs(0.5 * m * v * v - e_s):.1e} J); RK4 "
              f"stays within {err:.1e} m of the closed form")
        out[name] = run
    cA, c1, c2 = ho["cA"][-1], w1["c_max"], w2["c_max"]
    print(f"comparison: head-on at {man['speed_km_h']:g} + {man['speed_km_h']:g}, {cA * 100:.2f} cm per car, against "
          f"the wall at {man['speed_km_h']:g}, {c1 * 100:.2f} cm: diff {abs(cA - c1) * 100:.1e} cm, ratio "
          f"{cA / c1:.4f} (the same crash for each car); the wall at {man['fast_speed_km_h']:g}, {c2 * 100:.2f} cm, "
          f"against the wall at {man['speed_km_h']:g}: ratio {c2 / c1:.4f} (twice the speed, twice the crush, in the "
          f"same {w2['t_lock'] * 1000:.1f} ms); the head-on per car against the wall at "
          f"{man['fast_speed_km_h']:g}: ratio {cA / c2:.4f}; the two cars of the head-on together crush "
          f"{(ho['cA'][-1] + ho['cB'][-1]) * 100:.2f} cm, the same as the one car into the wall at "
          f"{man['fast_speed_km_h']:g} ({c2 * 100:.2f} cm, ratio {(ho['cA'][-1] + ho['cB'][-1]) / c2:.4f}): the "
          f"closing speed of {man['speed_km_h'] * 2:g} km/h is shared by two crumple zones; peak deceleration "
          f"{w1['a_peak'] / g:.2f} g in the head-on and the wall at {man['speed_km_h']:g}, {w2['a_peak'] / g:.2f} g "
          f"in the wall at {man['fast_speed_km_h']:g}")
    # Constant-force crumple for comparison.
    F_eq = m * v1 * v1 / (2.0 * c1)
    cf_law = (lambda c: F_eq), None
    cw1 = crash_wall(m, v1, dt, cf_law[0])
    cw2 = crash_wall(m, v2, dt, cf_law[0])
    print(f"constant-force crumple, for comparison (not drawn): a crumple zone that resists with a constant force F "
          f"gives crush m v^2 / (2 F), proportional to the speed squared; with F = {F_eq / 1000:.1f} kN, chosen so "
          f"that {man['speed_km_h']:g} km/h gives the same {cw1['c_max'] * 100:.2f} cm (closed form "
          f"{m * v1 * v1 / (2 * F_eq) * 100:.2f}), {man['fast_speed_km_h']:g} km/h gives {cw2['c_max'] * 100:.2f} cm "
          f"(closed form {m * v2 * v2 / (2 * F_eq) * 100:.2f}), ratio {cw2['c_max'] / cw1['c_max']:.4f}: 4 times, "
          f"not 2, so the 2.00 depends on the spring law, in {cw1['t_lock'] * 1000:.1f} and "
          f"{cw2['t_lock'] * 1000:.1f} ms at a constant {F_eq / m / g:.1f} g; the head-on equality does not depend on "
          f"the law: two identical cars with any crumple law meet at a plane where the two equal forces balance, so "
          f"the plane is fixed by symmetry and each car crushes exactly as it would into a wall at its own speed")
    # Other speeds for the description.
    descr = []
    for kmh in man["description_speeds_km_h"]:
        v = kmh / 3.6
        cf = closed_forms(m, k, v, g)
        r = crash_wall(m, v, dt, law)
        descr.append(f"{kmh:g} km/h: {r['c_max'] * 100:.2f} cm (closed form {cf['x'] * 100:.2f}) in "
                     f"{r['t_lock'] * 1000:.1f} ms, peak {r['a_peak'] / g:.1f} g; a head-on at {kmh:g} + {kmh:g} "
                     f"crushes each car the same {r['c_max'] * 100:.2f} cm")
    print("for the description (same cars, other speeds into the wall): " + "; ".join(descr))
    ev = {"headon": ho, "wall": w1, "wall2": w2, "cf1": cf1, "cf2": cf2, "cycles": int(round(cycles)),
          "c50": c1 * 100, "c100": c2 * 100, "g50": w1["a_peak"] / g, "g100": w2["a_peak"] / g,
          "t_ms": w1["t_lock"] * 1000, "plane_mm": float(np.max(np.abs(ho["plane"])) * 1000), "g": g}
    # Schedule in video time.
    t0 = man["first_cycle_at"]
    k0 = math.ceil((0.0 - t0) / P - 1e-9) - 1
    k1 = math.floor((D - t0) / P - 1e-9)
    starts = [t0 + kk * P for kk in range(k0, k1 + 1)]

    def lst(off_: float) -> str:
        return ", ".join(f"{s + off_:.2f}" for s in starts if 0.0 <= s + off_ < D)
    tau0 = (0.0 - t0) % P
    r0 = (tau0 - ia) / S
    t_lock_v = ia + w1["t_lock"] * S
    print(f"schedule (video time, 1/{S:g} speed): cycles of {P:g} s start at " + ", ".join(f"{s:.2f}" for s in starts)
          + f" s (the first {-t0:.2f} s before the first frame); the bumpers touch {ia:g} s into each cycle at "
          f"{lst(ia)} s; the crush grows for {w1['t_lock'] * S:.2f} s of video and all three lanes lock at "
          f"{lst(t_lock_v)} s (readouts {c1 * 100:.1f}, {c1 * 100:.1f} and {c1 * 100:.1f} cm in lane 1 and 2, "
          f"{c2 * 100:.1f} cm in lane 3, gold from the lock); the crushed cars hold until {lst(P - F)} s, then "
          f"each cycle fades to the run-up of the next over {F:g} s (out over {P - F:.2f} to {P - F / 2:.2f} s, in "
          f"over {P - F / 2:.2f} to {P:.2f} s after the cycle start); on the first frame the cycle is {tau0:.2f} s "
          f"in ({r0 * 1000:.1f} ms real {'before' if r0 < 0 else 'after'} impact): the cars are "
          f"{'in their run-up' if r0 < 0 else 'crushing'}; title until {man['title_until']:g} s, then the legend and "
          f"the clock; payoff card from {man['payoff_t']:g} s; the title fades back in over the last "
          f"{man['loop_fade']:g} s and the last frame repeats the first (the scene is periodic: {D:g} s holds exactly "
          f"{cycles:.0f} cycles)")
    # Text widths.
    font = os.environ["SEED_ZERO_FONT"]
    f28, f34, f40, f56 = (ImageFont.truetype(font, n) for n in (28, 34, 40, 56))
    widths = {"overlay@34": (f34, man["overlay"])}
    for j, line in enumerate(man["title"].split("|")):
        widths[f"title line {j + 1}@56"] = (f56, line)
    widths["legend@40"] = (f40, legend_text(man))
    widths["clock before@28"] = (f28, clock_text(-0.0325))
    widths["clock after@28"] = (f28, clock_text(0.0497))
    for lane in LANES:
        widths[f"label {lane}@40"] = (f40, label_text(man, lane))
        widths[f"facts {lane}@28"] = (f28, facts_text(ev, lane))
    widths["speed@28"] = (f28, speed_text(man["fast_speed_km_h"]))
    widths["readout@40"] = (f40, readout_text(c2))
    widths["plane@28"] = (f28, plane_text(0.0))
    for j, line in enumerate(payoff_lines(man, ev)):
        widths[f"payoff line {j + 1}@40"] = (f40, line)
    print("text widths: " + ", ".join(f"{kk} {f.getlength(s):.0f} px" for kk, (f, s) in widths.items()))
    assert all(f.getlength(s) < 950 for f, s in widths.values()), "a text line is wider than 950 px"
    left = ROW_X0 + max(f40.getlength(label_text(man, lane)) for lane in LANES)
    right = ROW_X1 - max(f28.getlength(facts_text(ev, lane)) for lane in LANES)
    rw = f40.getlength(readout_text(c2))
    rx = Renderer.READ_X["headon"]
    read_gap = (rx["b"] - rw / 2) - (rx["a"] + rw / 2)
    print(f"row check: the lane label ends at x {left:.0f} px and the facts line starts at {right:.0f} px; the two "
          f"head-on readouts are {read_gap:.0f} px apart")
    assert left < right - 40 and read_gap > 40, "the row texts collide"
    return ev


def legend_text(man: dict) -> str:
    return f"same cars, one clock, slow motion 1/{man['slow']:g}"


def clock_text(r: float) -> str:
    return f"{abs(r) * 1000:.1f} ms {'before' if r < 0.0 else 'after'} impact"


def label_text(man: dict, lane: str) -> str:
    v = man["fast_speed_km_h"] if lane == "wall2" else man["speed_km_h"]
    return LANE_TITLE[lane].format(v=v)


def facts_text(ev: dict, lane: str) -> str:
    run = ev[lane]
    peak = (run["accA"] if lane == "headon" else run["acc"]).max() / ev["g"]
    return f"peak {peak:.1f} g, {run['t_lock'] * 1000:.1f} ms"


def speed_text(kmh: float) -> str:
    return f"{kmh:g} km/h"


def readout_text(c: float) -> str:
    return f"crush {c * 100:.1f} cm"


def plane_text(p_mm: float) -> str:
    return f"contact plane moved {p_mm:.2f} mm"


def payoff_lines(man: dict, ev: dict) -> list[str]:
    text = man["payoff_text"].format(c50=ev["c50"], c100=ev["c100"], g50=ev["g50"], g100=ev["g100"], t_ms=ev["t_ms"])
    return [s.strip() for s in text.split("|")]


# --- rendering ---------------------------------------------------------------
class Renderer:
    READ_X = {"headon": {"a": 310.0, "b": 770.0}, "wall": {"a": 372.0}, "wall2": {"a": 372.0}}

    def __init__(self, man: dict, ev: dict):
        self.man, self.ev = man, ev
        self.fps = man["fps"]
        font = os.environ["SEED_ZERO_FONT"]
        self.font = ImageFont.truetype(font, 40)
        self.font_title = ImageFont.truetype(font, 56)
        self.font_small = ImageFont.truetype(font, 28)
        self.ppm = float(man["px_per_m"])
        self.S = man["slow"]
        self.P_f = int(round(man["cycle_s"] * self.fps))
        self.c0_f = int(round(man["first_cycle_at"] * self.fps))
        self.ia, self.F = man["impact_at"], man["reset_fade"]
        self.P = man["cycle_s"]
        self.px = float(man["plane_x_px"])
        self.Lz = man["crumple_zone_m"]
        self.Lb = man["car_length_m"] - self.Lz
        self.v1, self.v2 = man["speed_km_h"] / 3.6, man["fast_speed_km_h"] / 3.6
        self.band = {lane: (man["lane_y"][i], man["lane_y"][i + 1]) for i, lane in enumerate(LANES)}
        # Cars per lane: (key, heading d, speed, run and the sampled keys for displacement and crush).
        self.cars = {
            "headon": [("a", 1, self.v1, ev["headon"], "xA", "cA"), ("b", -1, self.v1, ev["headon"], "xB", "cB")],
            "wall": [("a", 1, self.v1, ev["wall"], "crush", "crush")],
            "wall2": [("a", 1, self.v2, ev["wall2"], "crush", "crush")],
        }
        self.kmh = {"headon": man["speed_km_h"], "wall": man["speed_km_h"], "wall2": man["fast_speed_km_h"]}

    # --- state helpers ------------------------------------------------------
    def phase(self, f: int) -> tuple[int, float]:
        k, tau_f = divmod(f - self.c0_f, self.P_f)
        return k, tau_f / self.fps

    def car_state(self, d: int, v: float, run: dict, xkey: str, ckey: str, r: float) -> dict:
        """Body displacement x (m, +x is car A's heading), crush c and lock flag at real time r."""
        if r < 0.0:
            return {"x": d * v * r, "c": 0.0, "locked": False}
        return {"x": state_lookup(run, xkey, r), "c": state_lookup(run, ckey, r), "locked": r >= run["t_lock"]}

    # --- pixel helpers ------------------------------------------------------
    def X(self, xm: float) -> float:
        return self.px + xm * self.ppm

    @staticmethod
    def L(x: float, y: float) -> tuple[float, float]:
        """Layer (2x) pixel of a lane-local point, rounded so equal states draw equal pixels."""
        return round(x * SS, 4), round(y * SS, 4)

    def rect(self, d: ImageDraw.ImageDraw, x0: float, y0: float, x1: float, y1: float, fill, outline=None, width=1) -> None:
        p0, p1 = self.L(min(x0, x1), min(y0, y1)), self.L(max(x0, x1), max(y0, y1))
        d.rectangle((p0[0], p0[1], p1[0], p1[1]), fill=fill, outline=outline, width=width * SS if outline else 0)

    def draw_car(self, d: ImageDraw.ImageDraw, dd: int, st: dict, a: float) -> None:
        """A side-view car heading dd (+1 right, -1 left) with its rigid front at g and the crumple
        zone from g to the front face, shortened by the crush."""
        ppm, Lz, Lb = self.ppm, self.Lz, self.Lb
        gy = float(GROUND_DY)
        g = -dd * Lz + st["x"]            # rigid front (m), so the uncrushed bumper is at -dd Lz + dd Lz + x
        face = g + dd * (Lz - st["c"])
        rear = g - dd * Lb
        X = self.X
        # Wheels on the rigid part.
        for wx in (rear + dd * 0.65, g - dd * 0.55):
            cx, cy, rr = X(wx), gy - 0.32 * ppm, 0.32 * ppm
            p0, p1 = self.L(cx - rr, cy - rr), self.L(cx + rr, cy + rr)
            d.ellipse((p0[0], p0[1], p1[0], p1[1]), fill=blend(TYRE, a), outline=blend(RIM, a), width=3 * SS)
            h0, h1 = self.L(cx - rr * 0.35, cy - rr * 0.35), self.L(cx + rr * 0.35, cy + rr * 0.35)
            d.ellipse((h0[0], h0[1], h1[0], h1[1]), fill=blend(RIM, 0.7 * a))
        # Body slab over the rigid part.
        self.rect(d, X(rear), gy - 0.86 * ppm, X(g), gy - 0.30 * ppm, fill=blend(BODY, a))
        # Cabin with slanted windows.
        c0, c1 = rear + dd * 0.85, rear + dd * 2.45
        top = gy - CAR_H * ppm
        cab = [self.L(X(c0), gy - 0.86 * ppm), self.L(X(c0 + dd * 0.22), top), self.L(X(c1 - dd * 0.32), top),
               self.L(X(c1), gy - 0.86 * ppm)]
        d.polygon(cab, fill=blend(BODY_DARK, a))
        win_h = gy - 0.92 * ppm
        win_t = top + 0.06 * ppm
        d.polygon([self.L(X(c0 + dd * 0.08), win_h), self.L(X(c0 + dd * 0.27), win_t), self.L(X(c0 + dd * 0.72), win_t),
                   self.L(X(c0 + dd * 0.72), win_h)], fill=blend(GLASS, a))
        d.polygon([self.L(X(c0 + dd * 0.82), win_h), self.L(X(c0 + dd * 0.82), win_t), self.L(X(c1 - dd * 0.38), win_t),
                   self.L(X(c1 - dd * 0.08), win_h)], fill=blend(GLASS, a))
        # Wheel arches cut into the slab (drawn as ground-coloured discs would hide the wheels; skip).
        # Crumple zone: the front section, shortened by the crush, with creases that bunch up.
        zone_len = Lz - st["c"]
        self.rect(d, X(g), gy - 0.80 * ppm, X(face), gy - 0.30 * ppm, fill=blend(CORAL, a))
        for j in range(1, 5):
            cx = X(g + dd * zone_len * j / 5.0)
            q0, q1 = self.L(cx, gy - 0.78 * ppm), self.L(cx, gy - 0.32 * ppm)
            d.line((*q0, *q1), fill=blend(CREASE, a), width=2 * SS)
        # Bumper at the face.
        self.rect(d, X(face), gy - 0.74 * ppm, X(face - dd * 0.06), gy - 0.30 * ppm, fill=blend(BUMPER, a))
        # Headlight at the top of the face.
        self.rect(d, X(face - dd * 0.06), gy - 0.80 * ppm, X(face - dd * 0.20), gy - 0.72 * ppm, fill=blend(WHITE, 0.9 * a))

    def draw_scene(self, d: ImageDraw.ImageDraw, lane: str, tau: float, a: float) -> dict:
        """The cars of one lane tau seconds into a cycle, blended by a; returns the states for the text."""
        r = (tau - self.ia) / self.S
        states = {}
        for key, dd, v, run, xkey, ckey in self.cars[lane]:
            st = self.car_state(dd, v, run, xkey, ckey, r)
            st["d"] = dd
            self.draw_car(d, dd, st, a)
            states[key] = st
        out = {"cars": states, "r": r, "alpha": a}
        if lane == "headon":
            out["plane_mm"] = abs(state_lookup(self.ev["headon"], "plane", r)) * 1000.0 if r > 0.0 else 0.0
        return out

    def draw_lane(self, layer: Image.Image, lane: str, f: int) -> dict:
        d = ImageDraw.Draw(layer)
        y0, y1 = self.band[lane]
        gy = float(GROUND_DY)
        # The ground.
        g0, g1 = self.L(40, gy), self.L(W - 40, gy)
        d.line((*g0, *g1), fill=GROUND, width=3 * SS)
        if lane != "headon":
            # The wall: a hatched block whose face is the plane.
            x0, x1 = self.px, self.px + WALL_W_PX
            self.rect(d, x0, 70, x1, gy, fill=WALL_DARK, outline=WALL, width=2)
            y = 70.0
            while y < gy - 4:
                p0, p1 = self.L(x0 + 2, min(gy, y + 24)), self.L(min(x1 - 2, x0 + 2 + (min(gy, y + 24) - y)), y)
                d.line((*p0, *p1), fill=WALL, width=2 * SS)
                y += 24.0
        k, tau = self.phase(f)
        F, P = self.F, self.P
        a_old = 1.0 if tau <= P - F else max(0.0, (P - F / 2.0 - tau) / (F / 2.0))
        st = self.draw_scene(d, lane, tau, a_old) if a_old > 0.0 else None
        if tau >= P - F / 2.0:
            a_new = (tau - (P - F / 2.0)) / (F / 2.0)
            st_new = self.draw_scene(d, lane, tau - P, a_new)
            if st is None or a_new >= 0.5:
                st = st_new
        if lane == "headon":
            # The contact plane: a thin fixed line drawn over the cars.
            p0, p1 = self.L(self.px, 70), self.L(self.px, gy + 12)
            d.line((*p0, *p1), fill=WHITE, width=2 * SS)
        st["k"] = k
        return st

    def draw_text(self, d: ImageDraw.ImageDraw, states: dict, hud_alpha: float) -> None:
        man, ev = self.man, self.ev
        for lane, st in states.items():
            y0 = self.band[lane][0]
            a = st["alpha"]
            d.text((ROW_X0, y0 + LABEL_DY), label_text(man, lane), font=self.font, fill=TEXT, anchor="lm")
            locked = all(c["locked"] for c in st["cars"].values())
            if locked and hud_alpha > 0.02:
                d.text((ROW_X1, y0 + LABEL_DY), facts_text(ev, lane), font=self.font_small,
                       fill=blend(GOLD, 0.85 * a * hud_alpha), anchor="rm")
            for key, c in st["cars"].items():
                # Speed label over the rigid body, moving with it.
                g = -c["d"] * self.Lz + c["x"]
                cx = self.X(g - c["d"] * self.Lb / 2.0)
                d.text((cx, y0 + SPEED_DY), speed_text(self.kmh[lane]), font=self.font_small, fill=blend(MUTED, a), anchor="mm")
                d.text((self.READ_X[lane][key], y0 + READ_DY), readout_text(c["c"]), font=self.font,
                       fill=blend(GOLD if c["locked"] else TEXT, a), anchor="mm")
            if lane == "headon":
                d.text((self.px, y0 + PLANE_DY), plane_text(st["plane_mm"]), font=self.font_small,
                       fill=blend(TEAL, a), anchor="mm")
        if hud_alpha > 0.02:
            d.text((W / 2, LEGEND_Y), legend_text(man), font=self.font, fill=blend(TEXT, hud_alpha), anchor="mm")
            d.text((W / 2, CLOCK_Y), clock_text(states["wall"]["r"]), font=self.font_small,
                   fill=blend(MUTED, hud_alpha), anchor="mm")

    def live_frame(self, f: int, title_alpha: float | None = None, hud_alpha: float = 0.0) -> np.ndarray:
        """Frame f with the geometry at f / fps; title_alpha and hud_alpha override the title and
        the legend/clock/facts/card blend during the loop fade."""
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
        for lane in LANES:
            y0, y1 = self.band[lane]
            layer = Image.new("RGB", (W * SS, (y1 - y0) * SS), BG)
            states[lane] = self.draw_lane(layer, lane, f)
            img.paste(layer.reduce(SS), (0, y0))
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
            # The geometry runs on; the legend, clock, facts and card fade out over the first half of
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
    man = json.loads((ROOT / "projects/crash/manifest.json").read_text())
    ev = measure(man)
    if "--measure-only" in sys.argv:
        return
    if "--frames" in sys.argv:
        times = [float(v) for v in sys.argv[sys.argv.index("--frames") + 1].split(",")]
        r = Renderer(man, ev)
        (ROOT / "media/crash").mkdir(parents=True, exist_ok=True)
        for tv in times:
            Image.fromarray(r.frame_at(int(round(tv * man["fps"])))).save(ROOT / f"media/crash/smoke-{tv}.png")
        print("smoke frames: " + ", ".join(f"{tv}" for tv in times))
        return
    Renderer(man, ev).render(ROOT / "media/crash/footage.mp4")


if __name__ == "__main__":
    main()
