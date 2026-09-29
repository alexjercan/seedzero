#!/usr/bin/env python3
"""Brake or swerve: a wall across the road, 15 m ahead.

Two cars side by side in one wide car park, both at v = 50 km/h with the
same tyre grip, a friction circle of mu g = 0.8 g (g = 9.80665) in any
direction. Each car is a point, the centre of its front bumper, drawn as a
4.5 m by 1.8 m body behind it. A wall spans the whole width 15 m ahead of
both points at t = 0. No reaction time: both act at t = 0.

Left, brake: straight-line deceleration at the full mu g, so the car stops
in v^2 / (2 mu g) after v / (mu g). Right, swerve: the full mu g sideways
and no braking, so the speed stays v and the car follows a circle of
radius R = v^2 / (mu g). To clear a wall across the whole road the car must
turn until it runs along the wall, a quarter turn, which takes R of
forward distance: exactly twice the braking distance. With the wall at
D = 15 m the swerving car hits it after turning asin(D / R), still at v.

Both cars are integrated by RK4 (the swerve as a velocity vector turned
by a perpendicular acceleration of magnitude mu g, the brake as a
deceleration) at steps_per_second, the events located by bisection inside
the step, and checked against the closed forms. The drawing uses the
closed forms. Brake-then-turn strategies (brake to a speed u, then turn
at full grip) are integrated the same way for the scan.

The run repeats at the release times in the manifest (a scene of
scene_duration seconds read as a circle): each run starts preroll seconds
before its release with the cars driving up at v, holds its end state,
and fades out over the first half of reset_fade while the next run fades
in over the second half. The schedule is periodic in the scene length, so
the last frame equals the first. Shown at 1/slow speed. Deterministic, no
seed.

Measured and printed: the braking stop (distance, time, gap to the wall),
the swerve (radius, speed and radius drift along the path, the hit time,
angle, sideways offset, speed and its component square to the wall, the
forward distance of a full quarter turn), the braking car at the moment
of the hit, the body-corner check, the brake-then-turn scan, a narrow
obstacle (a sideways shift) and the same at 70 km/h for the description,
a half-step check, the schedule in video time, the on-screen text widths
and the layout clearances.

usage: swerve.py [--measure-only] [--frames t1,t2,...]
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
ASPHALT = (30, 34, 40)
RED = (255, 64, 48)
HEAD = (250, 236, 170)
CONCRETE = (156, 162, 174)
JOINT = (118, 124, 136)
INK = (34, 38, 46)
HAZARD = (236, 190, 60)

# Layout: overlay at y 96..130 (captions.py), two title rows at y 190/252 for
# the first seconds, then the legend at y 236 and the shared clock at y 290;
# one geometry layer y 320..1430 drawn at 2x: the start line at line_y_px
# (1240), the ground ahead of it at px_per_m (34 px per metre), the wall face
# at 15 m (y 730) with the wall band above it, the dark area beyond the wall
# with the dashed quarter circle and the full-turn line at R (y 404); the
# braking car in its lane at brake_x_px (180), the swerving car starting at
# swerve_x_px (980) and turning left; readout columns left-aligned at x 240
# (brake) and right-aligned at x 920 (swerve) in rows y 1290/1345/1395;
# captions at caption_y 0.75 (y 1440..1530); the six-line card from y 1572 at
# a 48 px pitch.
LEGEND_Y, CLOCK_Y = 236, 290
SS = 2
GEOM_Y0, GEOM_Y1 = 320, 1430
PAYOFF_Y, PAYOFF_PITCH = 1572.0, 48
COL_BRAKE_X, COL_SWERVE_X = 240, 920
ROW_LABEL, ROW_SPEED, ROW_FWD = 1290, 1345, 1395
START_LABEL_Y = 1262
RULER_X = 22
FULL_LABEL_X, FULL_LABEL_DY = 1040, -32
GAP_X = 244
HIT_LABEL_X, HIT_LABEL_Y = 860, 905


def blend(col, a: float, base=BG) -> tuple:
    a = max(0.0, min(1.0, a))
    return tuple(int(round(c * a + b * (1 - a))) for c, b in zip(col, base))


def smoothstep(u: float) -> float:
    u = max(0.0, min(1.0, u))
    return u * u * (3 - 2 * u)


# --- the model ------------------------------------------------------------------
def params(man: dict, kmh: float | None = None) -> dict:
    v = (man["speed_km_h"] if kmh is None else kmh) / 3.6
    a = man["grip_g"] * man["g"]
    return {"v": v, "a": a, "d_b": v * v / (2 * a), "t_b": v / a, "R": v * v / a}


def closed_forms(man: dict) -> dict:
    p = params(man)
    v, a, R, D = p["v"], p["a"], p["R"], man["wall_m"]
    phi = math.asin(D / R)
    p.update({"D": D, "phi": phi, "t_hit": R * phi / v, "side": R * (1 - math.cos(phi)), "gap": D - p["d_b"]})
    return p


def rk4(deriv, s: np.ndarray, h: float) -> np.ndarray:
    k1 = deriv(s)
    k2 = deriv(s + 0.5 * h * k1)
    k3 = deriv(s + 0.5 * h * k2)
    k4 = deriv(s + h * k3)
    return s + h / 6.0 * (k1 + 2.0 * k2 + 2.0 * k3 + k4)


def brake_deriv(a: float):
    """State (x, y, vx, vy): a car braking straight ahead (along +y) at a; the stop is the event vy = 0."""
    def f(s):
        return np.array([s[2], s[3], 0.0, -a])
    return f


def turn_deriv(a: float):
    """State (x, y, vx, vy): acceleration a perpendicular to the velocity, to the left."""
    def f(s):
        sp = math.hypot(s[2], s[3])
        return np.array([s[2], s[3], -a * s[3] / sp, a * s[2] / sp])
    return f


def integrate(deriv, s0: np.ndarray, dt: float, event, t_max: float, t0: float = 0.0, record=None):
    """RK4 from s0 until event(s) turns positive; the crossing is found by 60 bisections of the last step.
    Returns (t, state) at the event; record(t, s) is called at every whole step."""
    s = s0.copy()
    t = t0
    n = int(round(t_max / dt))
    for _ in range(n):
        if record is not None:
            record(t, s)
        s_new = rk4(deriv, s, dt)
        if event(s_new) > 0.0:
            lo, hi = 0.0, dt
            for _ in range(60):
                mid = 0.5 * (lo + hi)
                if event(rk4(deriv, s, mid)) > 0.0:
                    hi = mid
                else:
                    lo = mid
            return t + hi, rk4(deriv, s, hi)
        s, t = s_new, t + dt
    raise RuntimeError("no event before t_max")


def brake_run(p: dict, dt: float) -> dict:
    v, a = p["v"], p["a"]
    err = {"x": 0.0, "v": 0.0, "n": 0}

    def rec(t, s):
        err["x"] = max(err["x"], abs(s[1] - (v * t - 0.5 * a * t * t)))
        err["v"] = max(err["v"], abs(s[3] - (v - a * t)))
        err["n"] += 1

    # The speed crosses zero: stop when vy turns negative.
    t, s = integrate(brake_deriv(a), np.array([0.0, 0.0, 0.0, v]), dt, lambda s: -s[3], 10.0, record=rec)
    return {"t": t, "y": s[1], "x": s[0], "err_x": err["x"], "err_v": err["v"], "steps": err["n"]}


def turn_run(p: dict, dt: float, D: float) -> dict:
    """Pure swerve from (0, 0) at (0, v): the wall hit at y = D, and (ignoring the wall) the quarter turn."""
    v, a, R = p["v"], p["a"], p["R"]

    def recorder():
        drift = {"speed": 0.0, "radius": 0.0, "rmin": 1e9, "rmax": 0.0, "n": 0}

        def rec(t, s):
            sp = math.hypot(s[2], s[3])
            r = math.hypot(s[0] + R, s[1])
            drift["speed"] = max(drift["speed"], abs(sp - v))
            drift["radius"] = max(drift["radius"], abs(r - R))
            drift["rmin"], drift["rmax"] = min(drift["rmin"], r), max(drift["rmax"], r)
            drift["n"] += 1
        return drift, rec

    s0 = np.array([0.0, 0.0, 0.0, v])
    hit_drift, rec = recorder()
    t_hit, s_hit = integrate(turn_deriv(a), s0, dt, lambda s: s[1] - D, 10.0, record=rec)
    drift, rec = recorder()
    t_q, s_q = integrate(turn_deriv(a), s0, dt, lambda s: -s[3], 10.0, record=rec)
    return {"t_hit": t_hit, "s_hit": s_hit, "t_q": t_q, "s_q": s_q, "hit_drift": hit_drift, "drift": drift}


def sidestep_run(p: dict, dt: float, shift: float) -> tuple[float, float]:
    """Pure swerve: the forward distance and the time when the car is shift metres to the side."""
    v, a = p["v"], p["a"]
    t, s = integrate(turn_deriv(a), np.array([0.0, 0.0, 0.0, v]), dt, lambda s: -s[0] - shift, 10.0)
    return s[1], t


def side_at_run(p: dict, dt: float, fwd: float) -> float:
    """Pure swerve: how far to the side the car is when it is fwd metres forward."""
    v, a = p["v"], p["a"]
    _, s = integrate(turn_deriv(a), np.array([0.0, 0.0, 0.0, v]), dt, lambda s: s[1] - fwd, 10.0)
    return -s[0]


def brake_then_turn(p: dict, dt: float, u: float) -> tuple[float, float]:
    """Brake straight at full grip down to speed u, then turn at full grip until the car runs along the wall
    (or stops, for u = 0). Returns the forward distance used and the time."""
    v, a = p["v"], p["a"]
    s = np.array([0.0, 0.0, 0.0, v])
    if u <= 0.0:
        t, s = integrate(brake_deriv(a), s, dt, lambda s: -s[3], 10.0)
        return s[1], t
    t = 0.0
    if u < v:
        t, s = integrate(brake_deriv(a), s, dt, lambda s: u - math.hypot(s[2], s[3]), 10.0)
    t, s = integrate(turn_deriv(a), s, dt, lambda s: -s[3], 10.0, t0=t)
    return s[1], t


def measure(man: dict) -> dict:
    cf = closed_forms(man)
    v, a, R, D = cf["v"], cf["a"], cf["R"], cf["D"]
    dt = 1.0 / man["steps_per_second"]
    S, fps, Dsc, F, pre = man["slow"], man["fps"], man["scene_duration"], man["reset_fade"], man["preroll"]
    for key in ("preroll", "reset_fade", "scene_duration"):
        assert abs(man[key] * fps - round(man[key] * fps)) < 1e-9, f"{key} must be a whole number of frames"
    for r in man["release_times"]:
        assert abs(r * fps - round(r * fps)) < 1e-9, "release times must be whole frames"
    ppm = man["px_per_m"]
    print(f"setup: two cars side by side in one wide car park, both at {man['speed_km_h']:g} km/h = {v:.4f} m/s with the "
          f"same tyre grip, a friction circle of {man['grip_g']:g} g = {a:.4f} m/s^2 in any direction (g = {man['g']:g}); "
          f"each car is a point, the centre of its front bumper, drawn as a {man['car_length_m']:g} x "
          f"{man['car_width_m']:g} m body behind it; a wall spans the whole width {D:g} m ahead of both points at t = 0; "
          f"no reaction time, both act at t = 0; left car brakes straight at the full grip, right car steers left at the "
          f"full grip with no braking; RK4 at {man['steps_per_second']} steps per second (dt = {dt:.2e} s), events by "
          f"bisection inside the step; shown at 1/{S:g} speed, drawn at {ppm:g} px per metre; deterministic, no seed")
    b = brake_run(cf, dt)
    print(f"brake: RK4 stops at {b['y']:.4f} m after {b['t']:.4f} s (closed forms v^2 / (2 mu g) = {cf['d_b']:.4f} m, "
          f"v / (mu g) = {cf['t_b']:.4f} s); it stops {D - b['y']:.4f} m short of the wall; sideways drift "
          f"{abs(b['x']):.1e} m; max |x - closed form| {b['err_x']:.1e} m and |v - closed form| {b['err_v']:.1e} m/s "
          f"over {b['steps']} steps")
    tr = turn_run(cf, dt, D)
    sh, sq = tr["s_hit"], tr["s_q"]
    phi_hit = math.atan2(-sh[2], sh[3])
    sp_hit = math.hypot(sh[2], sh[3])
    hd, qd = tr["hit_drift"], tr["drift"]
    print(f"swerve: the speed stays {v * 3.6:.2f} km/h at every step (max |speed - v| {hd['speed']:.1e} m/s to the wall, "
          f"{qd['speed']:.1e} m/s over the full quarter turn) and the path is a circle of radius {R:.4f} m about the "
          f"point {R:.4f} m to the left of the start (closed form v^2 / (mu g) = {R:.4f} m; the distance to that centre "
          f"stays between {qd['rmin']:.6f} and {qd['rmax']:.6f} m, max |r - R| {qd['radius']:.1e} m over {qd['n']} steps); "
          f"the radius is {R / b['y']:.4f} times the RK4 braking distance")
    print(f"swerve hits the wall: RK4 at {tr['t_hit']:.4f} s (closed form R asin(D / R) / v = {cf['t_hit']:.4f} s), turned "
          f"{math.degrees(phi_hit):.2f} degrees (closed form asin(D / R) = {math.degrees(cf['phi']):.2f}), "
          f"{-sh[0]:.3f} m to the side (closed form R (1 - cos) = {cf['side']:.3f} m), at {sp_hit * 3.6:.2f} km/h, of "
          f"which {sh[3] * 3.6:.2f} km/h is square to the wall and {-sh[2] * 3.6:.2f} km/h along it")
    print(f"a full swerve (a quarter turn, until the car runs along the wall): RK4 {sq[1]:.4f} m forward and "
          f"{-sq[0]:.4f} m to the side after {tr['t_q']:.4f} s (closed forms R = {R:.4f} m, (pi / 2) R / v = "
          f"{math.pi / 2 * R / v:.4f} s); it needs {sq[1] - D:.4f} m more than the {D:g} m to the wall; full swerve "
          f"over braking: {sq[1] / b['y']:.4f}")
    t_h = tr["t_hit"]
    yb, vb = v * t_h - 0.5 * a * t_h * t_h, v - a * t_h
    print(f"at the moment of the hit ({t_h:.4f} s) the braking car is {yb:.3f} m from the line doing {vb * 3.6:.2f} km/h; "
          f"it stops {b['t'] - t_h:.4f} s later")
    hw = man["car_width_m"] / 2.0
    phi_c = math.asin(D / (R + hw))
    print(f"body check: the point model hits when the bumper centre reaches the wall; the outer front corner "
          f"({hw:g} m to the right of the centre) is (R + {hw:g}) sin(angle) ahead, so the body touches first at "
          f"{R * phi_c / v:.4f} s, turned {math.degrees(phi_c):.2f} degrees, with the bumper centre at "
          f"{R * math.sin(phi_c):.3f} m, {t_h - R * phi_c / v:.4f} s earlier (drawn: the car stops at the point-model "
          f"hit with that corner under the wall band)")
    scan = []
    best = None
    for kmh in man["scan_speeds_km_h"]:
        u = kmh / 3.6
        fwd, t_u = brake_then_turn(cf, dt, u)
        cf_fwd = (v * v - u * u) / (2 * a) + u * u / a
        scan.append(f"to {kmh:g} km/h: {fwd:.4f} m in {t_u:.4f} s (closed form {cf_fwd:.4f})")
        if best is None or fwd < best[0]:
            best = (fwd, kmh)
    print("brake then turn (brake straight at full grip to a speed u, then turn at full grip until running along the "
          "wall; forward distance (v^2 - u^2) / (2 mu g) + u^2 / (mu g) = v^2 / (2 mu g) + u^2 / (2 mu g)): "
          + "; ".join(scan) + f"; least at {best[1]:g} km/h, {best[0]:.4f} m: pure braking; any turning adds "
          "u^2 / (2 mu g), and the grip can never slow the car toward the wall faster than mu g, so no path stops the "
          f"forward motion in under {cf['d_b']:.4f} m")
    shift = man["sidestep_m"]
    fwd_s, t_s = sidestep_run(cf, dt, shift)
    side_tie = side_at_run(cf, dt, b["y"])
    p2 = params(man, man["description_speed_km_h"])
    b2 = brake_run(p2, dt)
    tr2 = turn_run(p2, dt, D)
    fwd_s2, _ = sidestep_run(p2, dt, shift)
    side_tie2 = side_at_run(p2, dt, b2["y"])
    print(f"for the description: a narrow obstacle: to move {shift:g} m sideways the swerving car needs {fwd_s:.4f} m "
          f"forward (closed form sqrt(2 R s - s^2) = {math.sqrt(2 * R * shift - shift * shift):.4f} m) after "
          f"{t_s:.4f} s, less than the {b['y']:.4f} m braking distance, so for a narrow obstacle a swerve can win; at "
          f"the braking distance the swerve is {side_tie:.4f} m to the side (closed form R (1 - sqrt(3) / 2) = "
          f"{R * (1 - math.sqrt(3) / 2):.4f} m), so a swerve wins only when less than that much sideways room is "
          f"needed; at {man['description_speed_km_h']:g} km/h: braking {b2['y']:.4f} m in {b2['t']:.4f} s, full "
          f"swerve {tr2['s_q'][1]:.4f} m (radius {p2['R']:.4f} m, ratio {tr2['s_q'][1] / b2['y']:.4f}), a "
          f"{shift:g} m sidestep {fwd_s2:.4f} m, the tie at {side_tie2:.4f} m to the side")
    half = 0.5 * dt
    bh = brake_run(cf, half)
    trh = turn_run(cf, half, D)
    print(f"check at half the time step ({2 * man['steps_per_second']} steps per second): brake stop {bh['y']:.6f} m "
          f"({bh['y'] - b['y']:+.1e}) at {bh['t']:.6f} s ({bh['t'] - b['t']:+.1e}); swerve hit at {trh['t_hit']:.6f} s "
          f"({trh['t_hit'] - t_h:+.1e}), full swerve {trh['s_q'][1]:.6f} m ({trh['s_q'][1] - sq[1]:+.1e})")
    ev = {"cf": cf, "d_b": b["y"], "t_b": b["t"], "gap": D - b["y"], "R": sq[1], "t_hit": t_h,
          "phi": phi_hit, "side": -sh[0], "v_hit": sp_hit * 3.6, "v_norm": sh[3] * 3.6,
          "v2": man["description_speed_km_h"], "d_b2": b2["y"], "R2": tr2["s_q"][1]}
    # Schedule in video time.
    rel = sorted(man["release_times"])
    n = len(rel)
    lines = []
    for k, r in enumerate(rel):
        end = (rel[k + 1] if k + 1 < n else rel[0] + Dsc) - pre
        hit, stop = r + t_h * S, r + b["t"] * S
        hold = end - F - stop
        assert hold > 0.3, "a run fades before the braking car has stopped"
        wrap = "" if stop < Dsc else (f" (past the scene end, so on the circle: swerve hits {hit % Dsc:.2f}, brake "
                                      f"stops {stop % Dsc:.2f}, fades {(end - F) % Dsc:.2f} to {end % Dsc:.2f})")
        lines.append(f"run {k + 1}: drives in from {r - pre:.2f}, release {r:.2f}, swerve hits {hit:.2f}, brake stops "
                     f"{stop:.2f}, holds {hold:.2f} s, fades {end - F:.2f} to {end:.2f}{wrap}")
    r0 = rel[-1] - Dsc
    tau0 = (0.0 - r0) / S
    phi0 = v * tau0 / R
    print(f"schedule (video time, 1/{S:g} speed; the swerve hits {t_h * S:.3f} s and the braking car stops "
          f"{b['t'] * S:.3f} s after each release; each run drives in {pre:g} s before its release and fades over the "
          f"last {F:g} s): " + "; ".join(lines) + f"; the last run is the first run one scene later ({rel[-1]:.2f} - "
          f"{Dsc:g} = {r0:.2f} s), so on the first frame the run is {tau0:.4f} s real after the line: the swerving car "
          f"{R * math.sin(phi0):.2f} m forward, {R * (1 - math.cos(phi0)):.2f} m to the side, turned "
          f"{math.degrees(phi0):.1f} degrees, the braking car {v * tau0 - 0.5 * a * tau0 ** 2:.2f} m forward at "
          f"{(v - a * tau0) * 3.6:.1f} km/h; title until {man['title_until']:g} s; payoff card from {man['payoff_t']:g} s; "
          f"full-swerve label gold from {man['swerve_gold_t']:g} s; the dashed quarter circle beyond the wall "
          f"brightened from {man['arc_hi'][0]:g} to {man['arc_hi'][1]:g} s; the title fades back in over the last "
          f"{man['loop_fade']:g} s and the last frame repeats the first")
    # Text widths.
    font = os.environ["SEED_ZERO_FONT"]
    f22, f26, f28, f32, f34, f36, f40, f48, f56 = (ImageFont.truetype(font, k) for k in (22, 26, 28, 32, 34, 36, 40, 48, 56))
    widths = {"overlay@34": (f34, man["overlay"])}
    for j, line in enumerate(man["title"].split("|")):
        widths[f"title line {j + 1}@56"] = (f56, line)
    widths["legend@40"] = (f40, legend_text(man))
    widths["clock@28"] = (f28, clock_text(1.7703))
    widths["clock rest@28"] = (f28, clock_text(-1.0))
    widths["label brake@40"] = (f40, "brake")
    widths["label swerve@40"] = (f40, "swerve")
    widths["speed@48"] = (f48, speed_text(v))
    widths["stopped@48"] = (f48, "stopped")
    widths["forward@32"] = (f32, fwd_text(D))
    widths["start@28"] = (f28, "start line")
    widths["wall@26"] = (f26, wall_text(man))
    widths["full swerve@32"] = (f32, full_text(ev))
    widths["gap@36"] = (f36, gap_text(ev))
    widths["stop mark@32"] = (f32, stop_text(ev))
    widths["hit@36"] = (f36, hit_text(ev))
    widths["ruler@22"] = (f22, "25 m")
    for j, line in enumerate(payoff_lines(man, ev)):
        widths[f"payoff line {j + 1}@40"] = (f40, line)
    print("text widths: " + ", ".join(f"{k} {f.getlength(s):.0f} px" for k, (f, s) in widths.items()))
    assert all(f.getlength(s) < 950 for f, s in widths.values()), "a text line is wider than 950 px"
    # Layout checks.
    line_y, xb, xs = man["line_y_px"], man["brake_x_px"], man["swerve_x_px"]
    y_wall = line_y - D * ppm
    y_full = line_y - sq[1] * ppm
    brake_right = COL_BRAKE_X + max(f40.getlength("brake"), f48.getlength(speed_text(v)), f48.getlength("stopped"),
                                    f32.getlength(fwd_text(D)))
    swerve_left = COL_SWERVE_X - max(f40.getlength("swerve"), f48.getlength(speed_text(v)), f32.getlength(fwd_text(D)))
    car_hw = man["car_width_m"] / 2 * ppm
    print(f"layout: start line y {line_y}, wall face y {y_wall:.1f} (band from y {y_wall - man['wall_thick_m'] * ppm:.1f}), "
          f"braking stop y {line_y - b['y'] * ppm:.1f}, full-swerve line y {y_full:.1f} (label centre "
          f"y {y_full + FULL_LABEL_DY:.1f}), arc centre x {xs - R * ppm:.1f}, impact x {xs - ev['side'] * ppm:.1f}")
    print(f"row check: the brake column spans x {COL_BRAKE_X} to {brake_right:.0f} px (car to x {xb + car_hw:.0f}), the "
          f"swerve column x {swerve_left:.0f} to {COL_SWERVE_X} px (car from x {xs - car_hw:.0f}); the start label spans "
          f"x {540 - f28.getlength('start line') / 2:.0f} to {540 + f28.getlength('start line') / 2:.0f}")
    assert brake_right < swerve_left - 40, "the readout columns touch"
    assert xb + car_hw < COL_BRAKE_X - 16 and COL_SWERVE_X < xs - car_hw - 16, "a readout column touches its car"
    assert y_full + FULL_LABEL_DY - 20 > CLOCK_Y + 20, "the full-swerve label touches the clock"
    # The hit label sits under the crashed car, left of the swerve's path and below the braking labels.
    body = car_polygon(man, xs - ev["side"] * ppm, y_wall, ev["phi"])
    body_low = max(y for _, y in body)
    hit_w = f36.getlength(hit_text(ev))
    hy0, hy1 = HIT_LABEL_Y - 18, HIT_LABEL_Y + 18
    path_x = min(xs - R * (1 - math.cos(math.asin((line_y - y) / (R * ppm)))) * ppm for y in np.linspace(hy0, hy1, 9))
    stop_low = line_y - b["y"] * ppm + 26 + 16
    print(f"clearance: the hit label (x {HIT_LABEL_X - hit_w:.0f} to {HIT_LABEL_X}, y {hy0:.0f} to {hy1:.0f}) is "
          f"{hy0 - body_low:.0f} px under the crashed body, {path_x - HIT_LABEL_X:.0f} px left of the swerve's path and "
          f"{hy0 - stop_low:.0f} px under the braking stop label")
    assert hy0 - body_low > 8 and path_x - HIT_LABEL_X > 16 and hy0 - stop_low > 8, "the hit label touches something"
    return ev


def car_polygon(man: dict, px: float, py: float, phi: float) -> list[tuple[float, float]]:
    """Screen corners of the body for a bumper centre at (px, py) and heading phi (turned left)."""
    ppm = man["px_per_m"]
    fx, fy = -math.sin(phi), -math.cos(phi)
    rx, ry = math.cos(phi), -math.sin(phi)
    hw, L = man["car_width_m"] / 2, man["car_length_m"]
    return [(px + (u * rx - w * fx) * ppm, py + (u * ry - w * fy) * ppm) for u, w in ((-hw, 0), (hw, 0), (hw, L), (-hw, L))]


def x_at_y(poly: list, y: float) -> float:
    """Leftmost x of a convex polygon on the horizontal line y (inf if it misses)."""
    xs = []
    for (x0, y0), (x1, y1) in zip(poly, poly[1:] + poly[:1]):
        if (y0 - y) * (y1 - y) <= 0 and y0 != y1:
            xs.append(x0 + (y - y0) / (y1 - y0) * (x1 - x0))
    return min(xs) if xs else float("inf")


def legend_text(man: dict) -> str:
    return f"same speed, same grip, 1/{man['slow']:g} speed"


def clock_text(r: float) -> str:
    return "before the line" if r < 0.0 else f"{r:.3f} s after the line"


def speed_text(v: float) -> str:
    return f"{v * 3.6:.1f} km/h"


def fwd_text(y: float) -> str:
    return f"{max(0.0, y):.1f} m forward"


def wall_text(man: dict) -> str:
    return f"wall across the whole road, {man['wall_m']:g} m ahead"


def full_text(ev: dict) -> str:
    return f"a full swerve needs {ev['R']:.1f} m"


def gap_text(ev: dict) -> str:
    return f"{ev['gap']:.1f} m short"


def stop_text(ev: dict) -> str:
    return f"stops in {ev['d_b']:.1f} m"


def hit_text(ev: dict) -> str:
    return f"hits at {ev['v_hit']:.0f} km/h"


def payoff_lines(man: dict, ev: dict) -> list[str]:
    text = man["payoff_text"].format(d_b=ev["d_b"], gap=ev["gap"], R=ev["R"], t_hit=ev["t_hit"], v_hit=ev["v_hit"],
                                     phi_deg=math.degrees(ev["phi"]), side=ev["side"], v2=ev["v2"], d_b2=ev["d_b2"],
                                     R2=ev["R2"])
    return [s.strip() for s in text.split("|")]


# --- rendering ---------------------------------------------------------------
class Renderer:
    def __init__(self, man: dict, ev: dict):
        self.man, self.ev = man, ev
        self.fps = man["fps"]
        font = os.environ["SEED_ZERO_FONT"]
        self.f_title = ImageFont.truetype(font, 56)
        self.f40 = ImageFont.truetype(font, 40)
        self.f48 = ImageFont.truetype(font, 48)
        self.f36 = ImageFont.truetype(font, 36)
        self.f32 = ImageFont.truetype(font, 32)
        self.f28 = ImageFont.truetype(font, 28)
        self.f_wall = ImageFont.truetype(font, 26 * SS)
        self.f_ruler = ImageFont.truetype(font, 22 * SS)
        cf = ev["cf"]
        self.v, self.a, self.R = cf["v"], cf["a"], cf["R"]
        self.t_b, self.d_b, self.t_hit = cf["t_b"], cf["d_b"], cf["t_hit"]
        self.ppm = float(man["px_per_m"])
        self.S = float(man["slow"])
        self.line_y = float(man["line_y_px"])
        self.xb, self.xs = float(man["brake_x_px"]), float(man["swerve_x_px"])
        self.D = man["wall_m"]
        self.y_wall = self.line_y - self.D * self.ppm
        self.y_wall_top = self.y_wall - man["wall_thick_m"] * self.ppm
        self.total = int(round(man["scene_duration"] * self.fps))
        self.pre = int(round(man["preroll"] * self.fps))
        self.F = int(round(man["reset_fade"] * self.fps))
        rel = sorted(int(round(r * self.fps)) for r in man["release_times"])
        self.runs = []
        for k, r in enumerate(rel):
            nxt = rel[k + 1] if k + 1 < len(rel) else rel[0] + self.total
            self.runs.append({"release": r, "start": r - self.pre, "end": nxt - self.pre})
        self.ground = self.draw_ground()
        self.wall = self.draw_wall()
        self.arc_hi = self.draw_arc_highlight()

    # --- helpers ---------------------------------------------------------------
    def Lp(self, x: float, y: float) -> tuple[float, float]:
        return round(x * SS, 4), round((y - GEOM_Y0) * SS, 4)

    def y_of(self, fwd: float) -> float:
        return self.line_y - fwd * self.ppm

    def dashed(self, d, pts: list, col, dash: float, gap: float, width: int) -> None:
        """A dashed polyline through layer points."""
        on, left = True, dash
        for (ax, ay), (bx, by) in zip(pts, pts[1:]):
            seg = math.hypot(bx - ax, by - ay)
            s = 0.0
            while s < seg - 1e-9:
                step = min(left, seg - s)
                if on:
                    u0, u1 = s / seg, (s + step) / seg
                    d.line((ax + (bx - ax) * u0, ay + (by - ay) * u0, ax + (bx - ax) * u1, ay + (by - ay) * u1),
                           fill=col, width=width)
                s += step
                left -= step
                if left <= 1e-9:
                    on = not on
                    left = dash if on else gap

    def arc_point(self, phi: float) -> tuple[float, float]:
        """Screen point of the swerve path at turn angle phi."""
        return (self.xs - self.R * (1 - math.cos(phi)) * self.ppm, self.y_of(self.R * math.sin(phi)))

    # --- static layers -----------------------------------------------------------
    def draw_ground(self) -> Image.Image:
        man = self.man
        img = Image.new("RGB", (W * SS, (GEOM_Y1 - GEOM_Y0) * SS), BG)
        d = ImageDraw.Draw(img)
        a0, a1 = self.Lp(0, self.y_wall), self.Lp(W, GEOM_Y1)
        d.rectangle((a0[0], a0[1], a1[0], a1[1]), fill=ASPHALT)
        lane = man["lane_width_m"] * self.ppm
        for cx, col in ((self.xb, TEAL), (self.xs, CORAL)):
            l0, l1 = self.Lp(cx - lane / 2, self.y_wall), self.Lp(cx + lane / 2, GEOM_Y1)
            d.rectangle((l0[0], l0[1], l1[0], l1[1]), fill=blend(col, 0.05, ASPHALT))
            for xe in (cx - lane / 2, cx + lane / 2):
                self.dashed(d, [self.Lp(xe, GEOM_Y1), self.Lp(xe, self.y_wall)], blend(MUTED, 0.35, ASPHALT),
                            22 * SS, 22 * SS, 2 * SS)
        # The start line across the whole width.
        s0, s1 = self.Lp(0, self.line_y), self.Lp(W, self.line_y)
        d.line((s0, s1), fill=WHITE, width=3 * SS)
        # The ruler on the left edge: ticks every 5 m, the wall's 15 m is under the wall band.
        for m in range(0, 30, 5):
            ty = self.y_of(m)
            base = ASPHALT if ty >= self.y_wall else BG
            t0, t1 = self.Lp(RULER_X - 12, ty), self.Lp(RULER_X + 8, ty)
            d.line((t0, t1), fill=blend(MUTED, 0.7, base), width=2 * SS)
            if m not in (0, 15):   # the start line and the wall carry their own labels
                lab = f"{m} m" if m == 25 else f"{m}"
                p = self.Lp(RULER_X + 14, ty)
                d.text(p, lab, font=self.f_ruler, fill=blend(MUTED, 0.75, base), anchor="lm")
        # The full quarter circle the swerve would need, and the line where it ends (R forward).
        pts = [self.Lp(*self.arc_point(math.pi / 2 * k / 240)) for k in range(241)]
        self.dashed(d, pts, blend(CORAL, 0.7, BG), 16 * SS, 12 * SS, 3 * SS)
        yf = self.y_of(self.ev["R"])
        self.dashed(d, [self.Lp(40, yf), self.Lp(FULL_LABEL_X, yf)], blend(GOLD, 0.55, BG), 10 * SS, 10 * SS, 2 * SS)
        e = self.Lp(*self.arc_point(math.pi / 2))
        r = 6 * SS
        d.ellipse((e[0] - r, e[1] - r, e[0] + r, e[1] + r), outline=blend(CORAL, 0.7, BG), width=2 * SS)
        return img

    def draw_arc_highlight(self) -> Image.Image:
        """The dashed quarter circle again, wider and brighter, only beyond the wall (the part the narration
        points at); pasted with a varying alpha while the narration names it."""
        img = Image.new("RGBA", (W * SS, (GEOM_Y1 - GEOM_Y0) * SS), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        pts = [self.Lp(*self.arc_point(math.pi / 2 * k / 240)) for k in range(241)]
        self.dashed(d, pts, CORAL + (255,), 16 * SS, 12 * SS, 5 * SS)
        e = self.Lp(*self.arc_point(math.pi / 2))
        r = 8 * SS
        d.ellipse((e[0] - r, e[1] - r, e[0] + r, e[1] + r), outline=CORAL + (255,), width=3 * SS)
        cut = int(round((self.y_wall_top - GEOM_Y0) * SS))
        img.paste((0, 0, 0, 0), (0, cut, W * SS, (GEOM_Y1 - GEOM_Y0) * SS))
        return img

    def draw_wall(self) -> Image.Image:
        man = self.man
        img = Image.new("RGBA", (W * SS, (GEOM_Y1 - GEOM_Y0) * SS), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        top, face = self.y_wall_top, self.y_wall
        w0, w1 = self.Lp(0, top), self.Lp(W, face)
        d.rectangle((w0[0], w0[1], w1[0], w1[1]), fill=CONCRETE + (255,))
        # Block joints.
        mid = 0.5 * (top + face - 10)
        for y in (mid,):
            j0, j1 = self.Lp(0, y), self.Lp(W, y)
            d.line((j0, j1), fill=JOINT + (255,), width=SS)
        for row, (ya, yb) in enumerate(((top, mid), (mid, face - 10))):
            x = 30 if row == 0 else 80
            while x < W:
                p0, p1 = self.Lp(x, ya), self.Lp(x, yb)
                d.line((p0, p1), fill=JOINT + (255,), width=SS)
                x += 100
        # A hazard stripe along the face.
        h0, h1 = self.Lp(0, face - 10), self.Lp(W, face)
        d.rectangle((h0[0], h0[1], h1[0], h1[1]), fill=INK + (255,))
        x = -20
        while x < W + 20:
            poly = [self.Lp(x, face), self.Lp(x + 14, face), self.Lp(x + 24, face - 10), self.Lp(x + 10, face - 10)]
            d.polygon(poly, fill=HAZARD + (255,))
            x += 28
        # The label, clear of the swerve's impact point.
        tx, ty = self.Lp(440, 0.5 * (top + face - 10))
        d.rectangle((tx - 300 * SS, ty - 15 * SS, tx + 300 * SS, ty + 15 * SS), fill=CONCRETE + (255,))
        d.text((tx, ty), wall_text(man), font=self.f_wall, fill=INK + (255,), anchor="mm")
        return img

    # --- state -------------------------------------------------------------------
    def locate(self, f: int) -> tuple[dict, int]:
        fm = f % self.total
        for run in self.runs:
            for g in (fm, fm + self.total, fm - self.total):
                if run["start"] <= g < run["end"]:
                    return run, g
        raise RuntimeError("frame outside every run")

    def phase(self, f: int) -> tuple[float, float]:
        """(real time since the release of the shown run, alpha of the shown run) for frame f."""
        run, g = self.locate(f)
        left = run["end"] - g
        half = self.F / 2.0
        if left > self.F:
            return (g - run["release"]) / self.fps / self.S, 1.0
        if left > half:
            return (g - run["release"]) / self.fps / self.S, (left - half) / half
        return (g - run["end"] - self.pre) / self.fps / self.S, 1.0 - left / half

    def brake_state(self, r: float) -> dict:
        v, a = self.v, self.a
        if r < 0.0:
            return {"y": v * r, "v": v, "stopped": False, "braking": False}
        if r >= self.t_b:
            return {"y": self.d_b, "v": 0.0, "stopped": True, "braking": False}
        return {"y": v * r - 0.5 * a * r * r, "v": v - a * r, "stopped": False, "braking": True}

    def swerve_state(self, r: float) -> dict:
        v = self.v
        if r < 0.0:
            return {"x": self.xs, "yf": v * r, "phi": 0.0, "hit": False, "r": r}
        rr = min(r, self.t_hit)
        phi = v * rr / self.R
        return {"x": self.arc_point(phi)[0], "yf": self.R * math.sin(phi), "phi": phi, "hit": r >= self.t_hit, "r": r}

    # --- dynamic drawing ---------------------------------------------------------
    def draw_car(self, d, px: float, py: float, phi: float, col, braking: bool) -> None:
        ppm = self.ppm
        fx, fy = -math.sin(phi), -math.cos(phi)
        rx, ry = math.cos(phi), -math.sin(phi)

        def pt(u, w):
            return self.Lp(px + (u * rx - w * fx) * ppm, py + (u * ry - w * fy) * ppm)

        def poly(pts, fill, outline=None):
            d.polygon([pt(u, w) for u, w in pts], fill=fill, outline=outline)

        L, hw, c = self.man["car_length_m"], self.man["car_width_m"] / 2, 0.28
        if braking:
            poly([(-hw, L - 0.1), (hw, L - 0.1), (hw, L + 0.32), (-hw, L + 0.32)], blend(RED, 0.4, ASPHALT))
        poly([(-hw + c, 0), (hw - c, 0), (hw, c), (hw, L - c), (hw - c, L), (-hw + c, L), (-hw, L - c), (-hw, c)], col,
             outline=blend(col, 0.55, (0, 0, 0)))
        poly([(-0.72, 1.35), (0.72, 1.35), (0.68, 3.35), (-0.68, 3.35)], blend(col, 0.32, (8, 10, 14)))
        poly([(-0.70, 1.38), (0.70, 1.38), (0.66, 1.72), (-0.66, 1.72)], blend(WHITE, 0.55, col))
        poly([(-0.62, 3.02), (0.62, 3.02), (0.60, 3.30), (-0.60, 3.30)], blend(WHITE, 0.3, col))
        for s in (-1, 1):
            poly([(s * 0.50, 0.05), (s * 0.82, 0.05), (s * 0.82, 0.24), (s * 0.50, 0.24)], HEAD)
            poly([(s * 0.46, L - 0.20), (s * 0.84, L - 0.20), (s * 0.84, L - 0.04), (s * 0.46, L - 0.04)],
                 RED if braking else blend(RED, 0.6, col))

    def draw_dynamic(self, d, r: float) -> tuple[dict, dict]:
        man, ppm = self.man, self.ppm
        bs, ss = self.brake_state(r), self.swerve_state(r)
        # Braking car: skid marks from the rear wheels' positions at the line, the stop mark once stopped.
        axle = 3.7
        if r > 0.0:
            for s in (-1, 1):
                p0 = self.Lp(self.xb + s * 0.62 * ppm, self.line_y + axle * ppm)
                p1 = self.Lp(self.xb + s * 0.62 * ppm, self.y_of(bs["y"]) + axle * ppm)
                d.line((p0, p1), fill=blend(TEAL, 0.35, ASPHALT), width=3 * SS)
        lane = man["lane_width_m"] * ppm
        if bs["stopped"]:
            ys = self.y_of(self.d_b)
            m0, m1 = self.Lp(self.xb - lane / 2, ys), self.Lp(self.xb + lane / 2, ys)
            d.line((m0, m1), fill=GOLD, width=3 * SS)
            # The gap bracket from the stop mark to the wall face.
            g0, g1 = self.Lp(GAP_X, ys), self.Lp(GAP_X, self.y_wall)
            d.line((g0, g1), fill=GOLD, width=3 * SS)
            for yy in (ys, self.y_wall):
                t0, t1 = self.Lp(GAP_X - 8, yy), self.Lp(GAP_X + 8, yy)
                d.line((t0, t1), fill=GOLD, width=3 * SS)
        # Swerving car: its path so far, from the line.
        if r > 0.0:
            n = 90
            rr = min(r, self.t_hit)
            pts = [self.Lp(*self.arc_point(self.v * rr * k / n / self.R)) for k in range(n + 1)]
            d.line(pts, fill=blend(CORAL, 0.9, ASPHALT), width=4 * SS, joint="curve")
        self.draw_car(d, self.xb, self.y_of(bs["y"]), 0.0, TEAL, bs["braking"])
        self.draw_car(d, ss["x"], self.y_of(ss["yf"]), ss["phi"], CORAL, False)
        return bs, ss

    def draw_flash(self, d, r: float) -> None:
        u = (r - self.t_hit) * self.S / self.man["hit_flash"]
        if not 0.0 <= u < 1.0:
            return
        cx, cy = self.Lp(self.xs - self.ev["side"] * self.ppm, self.y_wall)
        a = 1.0 - u
        if u < 0.35:
            rc = (26 - 40 * u) * SS
            d.ellipse((cx - rc, cy - rc, cx + rc, cy + rc), fill=blend(WHITE, 1.0 - u / 0.35, CONCRETE))
        rr = (20 + 110 * u) * SS
        d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), outline=blend(WHITE, a, CONCRETE), width=6 * SS)
        for k in range(12):
            ang = 2 * math.pi * k / 12 + 0.3
            r0, r1 = (14 + 50 * u) * SS, (46 + 100 * u) * SS
            d.line((cx + r0 * math.cos(ang), cy + r0 * math.sin(ang), cx + r1 * math.cos(ang), cy + r1 * math.sin(ang)),
                   fill=blend(GOLD, a, CONCRETE), width=5 * SS)

    # --- frames ------------------------------------------------------------------
    def live_frame(self, f: int, title_alpha: float | None = None, hud_alpha: float = 0.0) -> np.ndarray:
        man, ev = self.man, self.ev
        t = f / self.fps
        if title_alpha is None:
            if t < man["title_until"]:
                title_alpha = 1.0 if t < man["title_until"] - 0.4 else (man["title_until"] - t) / 0.4
                hud_alpha = 0.0
            else:
                title_alpha = 0.0
                hud_alpha = min(1.0, (t - man["title_until"]) / 0.4)
        r, a = self.phase(f)
        layer = self.ground.copy()
        ld = ImageDraw.Draw(layer)
        bs, ss = self.draw_dynamic(ld, r)
        if a < 1.0:
            g = np.asarray(self.ground, dtype=np.float32)
            x = np.asarray(layer, dtype=np.float32)
            layer = Image.fromarray(np.round(g + a * (x - g)).astype(np.uint8))
        t0, t1 = man["arc_hi"]
        hi = smoothstep((t - t0) / 0.4) * smoothstep((t1 - t) / 0.4)
        if hi > 0.0:
            mask = self.arc_hi.getchannel("A").point(lambda p: int(round(p * hi)))
            layer.paste(self.arc_hi.convert("RGB"), (0, 0), mask)
        layer.paste(self.wall, (0, 0), self.wall)
        if a >= 1.0:
            self.draw_flash(ImageDraw.Draw(layer), r)
        img = Image.new("RGB", (W, H), BG)
        img.paste(layer.reduce(SS), (0, GEOM_Y0))
        d = ImageDraw.Draw(img)
        # Static labels.
        d.text((540, START_LABEL_Y), "start line", font=self.f28, fill=blend(MUTED, 1.0, ASPHALT), anchor="mm")
        g_full = smoothstep((t - man["swerve_gold_t"]) / 0.4) * hud_alpha
        full_col = tuple(int(round(c0 + (c1 - c0) * g_full)) for c0, c1 in zip(blend(CORAL, 0.8), GOLD))
        d.text((FULL_LABEL_X, self.y_of(ev["R"]) + FULL_LABEL_DY), full_text(ev), font=self.f32, fill=full_col, anchor="rm")
        # Event labels of the shown run.
        if bs["stopped"]:
            ys = self.y_of(self.d_b)
            d.text((GAP_X + 16, 0.5 * (ys + self.y_wall)), gap_text(ev), font=self.f36, fill=blend(GOLD, a, ASPHALT),
                   anchor="lm")
            d.text((GAP_X + 16, ys + 26), stop_text(ev), font=self.f32, fill=blend(GOLD, a, ASPHALT), anchor="lm")
        if ss["hit"]:
            u = smoothstep((ss["r"] - self.t_hit) * self.S / 0.25)
            d.text((HIT_LABEL_X, HIT_LABEL_Y), hit_text(ev), font=self.f36, fill=blend(WHITE, a * u, ASPHALT),
                   anchor="rm")
        # Readout columns.
        d.text((COL_BRAKE_X, ROW_LABEL), "brake", font=self.f40, fill=TEAL, anchor="lm")
        d.text((COL_SWERVE_X, ROW_LABEL), "swerve", font=self.f40, fill=CORAL, anchor="rm")
        if bs["stopped"]:
            d.text((COL_BRAKE_X, ROW_SPEED), "stopped", font=self.f48, fill=blend(GOLD, a, ASPHALT), anchor="lm")
        else:
            d.text((COL_BRAKE_X, ROW_SPEED), speed_text(bs["v"]), font=self.f48, fill=blend(TEXT, a, ASPHALT), anchor="lm")
        d.text((COL_BRAKE_X, ROW_FWD), fwd_text(bs["y"]), font=self.f32,
               fill=blend(GOLD if bs["stopped"] else MUTED, a, ASPHALT), anchor="lm")
        d.text((COL_SWERVE_X, ROW_SPEED), speed_text(self.v), font=self.f48,
               fill=blend(RED if ss["hit"] else TEXT, a, ASPHALT), anchor="rm")
        d.text((COL_SWERVE_X, ROW_FWD), fwd_text(ss["yf"]), font=self.f32,
               fill=blend(GOLD if ss["hit"] else MUTED, a, ASPHALT), anchor="rm")
        if hud_alpha > 0.0:
            d.text((W / 2, LEGEND_Y), legend_text(man), font=self.f40, fill=blend(TEXT, hud_alpha), anchor="mm")
            d.text((W / 2, CLOCK_Y), clock_text(min(r, self.t_b)), font=self.f28, fill=blend(MUTED, hud_alpha),
                   anchor="mm")
        if title_alpha > 0.0:
            for j, line in enumerate(man["title"].split("|")):
                d.text((W / 2, 190 + j * 62), line, font=self.f_title, fill=blend(TEXT, title_alpha), anchor="mm")
        if t >= man["payoff_t"]:
            pa = min(1.0, (t - man["payoff_t"]) / man["payoff_hold"]) * hud_alpha
            for j, line in enumerate(payoff_lines(man, ev)):
                d.text((W / 2, PAYOFF_Y + j * PAYOFF_PITCH), line, font=self.f40, fill=blend(GOLD, pa), anchor="mm")
        return np.asarray(img, dtype=np.uint8)

    def frame_at(self, f: int) -> np.ndarray:
        man = self.man
        total = self.total
        fade_frames = int(round(man["loop_fade"] * self.fps))
        if f == total - 1:
            return self.live_frame(0)   # the scene is periodic: the last frame repeats the first
        if f >= total - fade_frames:
            a = (f - (total - fade_frames) + 1) / fade_frames
            return self.live_frame(f, title_alpha=max(0.0, 2.0 * a - 1.0), hud_alpha=max(0.0, 1.0 - 2.0 * a))
        return self.live_frame(f)

    def render(self, out_path: Path) -> None:
        global _RENDERER
        out_path.parent.mkdir(parents=True, exist_ok=True)
        total = self.total
        first = self.frame_at(0)
        last = self.frame_at(total - 1)
        diff = np.abs(first.astype(int) - last.astype(int))
        print(f"loop check: last frame differs from the first in {int((diff.max(axis=2) > 24).sum())} px "
              f"(max channel difference {int(diff.max())})")
        wrap = self.live_frame(total, title_alpha=1.0, hud_alpha=0.0)
        diff = np.abs(first.astype(int) - wrap.astype(int))
        print(f"periodicity check: the scene drawn live at {self.man['scene_duration']:g} s differs from 0 s in "
              f"{int((diff.max(axis=2) > 24).sum())} px (max channel difference {int(diff.max())})")
        prev = self.frame_at(total - 2)
        diff = np.abs(prev.astype(int) - last.astype(int))
        print(f"loop step: the frame before the last differs from the last in {int((diff.max(axis=2) > 24).sum())} px "
              f"(one frame of motion)")
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
    man = json.loads((ROOT / "projects/swerve/manifest.json").read_text())
    ev = measure(man)
    if "--measure-only" in sys.argv:
        return
    if "--frames" in sys.argv:
        times = [float(v) for v in sys.argv[sys.argv.index("--frames") + 1].split(",")]
        r = Renderer(man, ev)
        (ROOT / "media/swerve").mkdir(parents=True, exist_ok=True)
        for tv in times:
            Image.fromarray(r.frame_at(int(round(tv * man["fps"])))).save(ROOT / f"media/swerve/smoke-{tv}.png")
        print("smoke frames: " + ", ".join(f"{tv}" for tv in times))
        return
    Renderer(man, ev).render(ROOT / "media/swerve/footage.mp4")


if __name__ == "__main__":
    main()
