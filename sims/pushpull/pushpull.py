#!/usr/bin/env python3
"""Push down on a crate, or pull up on it: which one moves it?

Two bands on the same clock, the same floor drawn the same way at the same
scale, side view: a crate of mass m (a cube of side w) rests on a level
floor with grip (friction coefficient) mu, the same at rest and sliding (a
chosen number). The same force F acts on the crate at angle a to the floor,
applied at mid-height (w / 2 up) so the crate slides and never tips (the
tipping check is printed). Top band, PUSH: a rod on the rear (left) face
presses forward and down at a below the horizontal. Bottom band, PULL: a
rope on the front (right) face pulls forward and up at a above the
horizontal. The horizontal drive is F cos a in both; the vertical part
F sin a presses the crate into the floor (push) or lifts part of its
weight (pull), so the floor push is

    N = m g + F sin a  (push),   N = m g - F sin a  (pull),

the grip limit is mu N, and the crate moves only while the drive exceeds
it: a = (F cos a - mu N) / m, else 0. The force acts for window_s seconds
(the measurement window); then the tool lets go and a moving crate skids
to a stop under sliding friction mu m g. Both bands are integrated by RK4
at steps_per_second with the stick-slip rule each step (static while
|drive| is at most mu N and v = 0; sliding friction mu N against the
motion otherwise; the crate stops when v crosses zero, located by
bisection inside the step), the forces held over each step (the step
boundaries fall on the release, so the piecewise-constant forces are
exact), checked against the closed forms and a half-step rerun; the
drawing follows the RK4 table. The run repeats every cycle_s seconds of
video with a crossfade back to the resting setup; the cycle divides the
scene length, so the scene is exactly periodic and the last frame equals
the first. Shown at 1/slow speed. Deterministic, no seed.

Measured and printed: the forces in both bands (weight, press or lift,
floor push, grip limit, drive, net), the accelerations, the position and
speed table at table_step_s to the release, the skid, the tipping check,
the energy at the release on the pull, the threshold forces, the lock
angle and the best pull angle, the force, grip and angle variants for the
description, the checks against the brief, the schedule in video time,
the on-screen text widths and the layout clearances.

usage: pushpull.py [--measure-only] [--frames t1,t2,...]
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
STEEL = (170, 180, 196)
CARD = (198, 150, 92)
CARD_EDGE = (128, 84, 40)
CARD_TAPE = (226, 202, 158)
ROD = (124, 136, 154)
ROD_DARK = (62, 70, 84)
ROPE = (214, 190, 140)
INK = (150, 158, 170)

# Layout: overlay at y 96..130 (captions.py), three title rows at y 186/244/302
# for the first seconds, then the legend at y 236 and the shared clock at y 290;
# two bands stacked, the push in y 330..880 and the pull in y 880..1430, each
# drawn at 2x in its own layer (so nothing leaves its band); each band has its
# label row 40 px under the band top, its second row at 84 and its third at
# 120 (left column from x 40, right column to x 1040); the grip meter rows at
# 156 and 182 on the right (x 560..1040); the floor line at floor_dy under the
# band top with a 24 px plank under it; the crate (w metres, 110 px) sits on
# the floor with its rear face at start_x_px at the start; the force arrows at
# 2 px per newton: the drive (teal, 100 px) along the rod or rope, the floor
# push (up from the floor, through the crate) and the weight (down from the
# centre) 14 px either side of the crate's centre line, the friction (coral)
# inside the plank; the gold event row in the ground region at 470; captions
# at caption_y 0.75 (y 1440..1530); the six-line card from y 1572 at a 48 px
# pitch.
LEGEND_Y, CLOCK_Y = 236, 290
TITLE_Y = (186, 244, 302)
SS = 2
PAYOFF_Y, PAYOFF_PITCH = 1572.0, 48
PANELS = ("push", "pull")
SIGN = {"push": -1.0, "pull": 1.0}       # the vertical part: -1 presses, +1 lifts
BAND_Y = {"push": 330, "pull": 880}
BAND_H = 550
LABEL_DY, SUB_DY, FIX_DY = 40, 84, 120
METER_DY = (156, 182)
METER_LABEL_X, METER_BAR_X, METER_VAL_X, METER_END_X = 640, 652, 764, 1040
EVENT_DY, EVENT_X = 470, 520
ROW_X0, ROW_X1 = 40, 1040
PLANK_PX = 24
PX_PER_N = 2.0
ARROW_HEAD = 16.0
ARROW_DX = 14.0
TOOL_LEN = 180.0
COLOUR = {"push": CORAL, "pull": TEAL}
REST, FORCE, SKID, STOP = "rest", "force", "skid", "stop"


def blend(col, a: float, base=BG) -> tuple:
    a = max(0.0, min(1.0, a))
    return tuple(int(round(c * a + b * (1 - a))) for c, b in zip(col, base))


# --- measurement --------------------------------------------------------------
def forces(m: float, g: float, mu: float, F: float, a_deg: float, sign: float) -> dict:
    """The static force balance: weight, vertical part, floor push N, grip limit mu N, drive, net
    and the acceleration a = max(0, (drive - mu N) / m) for a force F at a_deg; sign +1 lifts (pull),
    -1 presses (push)."""
    th = math.radians(a_deg)
    weight = m * g
    vert = F * math.sin(th)
    N = weight - sign * vert
    drive = F * math.cos(th)
    grip = mu * N
    net = drive - grip
    return {"weight": weight, "vert": vert, "N": N, "drive": drive, "grip": grip, "net": net,
            "a": max(0.0, net / m), "moves": net > 0.0}


def threshold_force(m: float, g: float, mu: float, a_deg: float, sign: float) -> float:
    """The force at a_deg that just balances the grip: mu m g / (cos a + sign mu sin a); infinite
    (no push works) when the denominator is not positive."""
    th = math.radians(a_deg)
    den = math.cos(th) + sign * mu * math.sin(th)
    return mu * m * g / den if den > 1e-12 else math.inf


def rk4_run(m: float, g: float, mu: float, F: float, a_deg: float, sign: float, t_rel: float, dt_n: int,
            t_end: float) -> dict:
    """Integrate the crate from rest by classical RK4 at dt = 1 / dt_n with the stick-slip rule each step:
    the force acts until t_rel (held over each step; the step boundaries fall on t_rel), then the
    tool lets go and the crate skids under mu m g until v crosses zero (bisection inside the step).
    Returns the table (t, x, v), the release and stop states and the step count."""
    dt = 1.0 / dt_n
    fo = forces(m, g, mu, F, a_deg, sign)
    n_rel = int(round(t_rel * dt_n))
    assert abs(n_rel / dt_n - t_rel) < 1e-12, "the release must fall on a step boundary"

    def acc(n: int, v: float) -> float:
        """The stick-slip rule, decided once per step from the state at the step start: static (a = 0)
        while v = 0 and |drive| is at most mu N; else sliding friction mu N against the motion (or
        against the drive when starting from rest)."""
        D, N = (fo["drive"], fo["N"]) if n < n_rel else (0.0, m * g)
        if abs(v) < 1e-15:
            return 0.0 if abs(D) <= mu * N else (D - math.copysign(mu * N, D)) / m
        return (D - math.copysign(mu * N, v)) / m

    def step(n: int, x: float, v: float, h: float) -> tuple[float, float]:
        a = acc(n, v)      # held over the step: the forces are piecewise constant, so RK4 is exact here
        k1x, k1v = v, a
        k2x, k2v = v + 0.5 * h * k1v, a
        k3x, k3v = v + 0.5 * h * k2v, a
        k4x, k4v = v + h * k3v, a
        return x + h * (k1x + 2.0 * k2x + 2.0 * k3x + k4x) / 6.0, v + h * (k1v + 2.0 * k2v + 2.0 * k3v + k4v) / 6.0

    ts, xt, vt = [0.0], [0.0], [0.0]
    x, v, n = 0.0, 0.0, 0
    n_end = int(round(t_end * dt_n))
    t_stop, x_stop, x_rel, v_rel = math.inf, math.nan, math.nan, math.nan
    while n < n_end:
        if n == n_rel:
            x_rel, v_rel = x, v
        xn, vn = step(n, x, v, dt)
        if v > 0.0 and vn <= 0.0:
            lo, hi = 0.0, dt
            for _ in range(80):
                mid = 0.5 * (lo + hi)
                _, vm = step(n, x, v, mid)
                if vm > 0.0:
                    lo = mid
                else:
                    hi = mid
            xh, _ = step(n, x, v, hi)
            t_stop, x_stop = n / dt_n + hi, xh
            xn, vn = xh, 0.0
            n += 1
            ts.append(t_stop)
            xt.append(xn)
            vt.append(0.0)
            x, v = xn, vn
            # From rest with no drive the crate stays: fill the table to t_end at rest.
            while n < n_end:
                n += 1
                ts.append(n / dt_n)
                xt.append(x)
                vt.append(0.0)
            break
        n += 1
        x, v = xn, vn
        ts.append(n / dt_n)
        xt.append(x)
        vt.append(v)
    if math.isnan(x_rel):
        x_rel, v_rel = float(np.interp(t_rel, ts, xt)), float(np.interp(t_rel, ts, vt))
    if math.isinf(t_stop):
        t_stop, x_stop = t_rel, x_rel          # never moved: at rest from the release on
    return {"t": np.array(ts), "x": np.array(xt), "v": np.array(vt), "x_rel": x_rel, "v_rel": v_rel,
            "t_stop": t_stop, "x_stop": x_stop, "steps": n, "t_rel": t_rel, "forces": fo, "mu": mu, "m": m,
            "g": g}


def state_at(run: dict, rt: float) -> dict:
    """(x, v, N, friction, drive, phase) of the crate rt real seconds after the force came on."""
    fo, mu, m, g = run["forces"], run["mu"], run["m"], run["g"]
    if rt < 0.0:
        return {"x": 0.0, "v": 0.0, "N": m * g, "fric": 0.0, "grip": mu * m * g, "drive": 0.0, "phase": REST}
    x = float(np.interp(rt, run["t"], run["x"]))
    v = float(np.interp(rt, run["t"], run["v"]))
    if rt < run["t_rel"]:
        fric = fo["drive"] if not fo["moves"] else fo["grip"]
        return {"x": x, "v": v, "N": fo["N"], "fric": fric, "grip": fo["grip"], "drive": fo["drive"], "phase": FORCE}
    if rt < run["t_stop"]:
        return {"x": x, "v": v, "N": m * g, "fric": mu * m * g, "grip": mu * m * g, "drive": 0.0, "phase": SKID}
    return {"x": run["x_stop"], "v": 0.0, "N": m * g, "fric": 0.0, "grip": mu * m * g, "drive": 0.0, "phase": STOP}


def measure(man: dict) -> dict:
    g, m, mu, F, a_deg = man["g"], man["crate_kg"], man["mu"], man["force_n"], man["angle_deg"]
    w, hap, T = man["crate_m"], man["apply_height_m"], man["window_s"]
    dt_n = man["steps_per_second"]
    dt = 1.0 / dt_n
    S, P, D, fps, Fd, fa = man["slow"], man["cycle_s"], man["scene_duration"], man["fps"], man["reset_fade"], man["force_at"]
    cycles = D / P
    assert abs(cycles - round(cycles)) < 1e-9, "the cycle must divide the scene length"
    for key in ("cycle_s", "force_at", "first_cycle_at", "reset_fade", "tool_fade_s"):
        assert abs(man[key] * fps - round(man[key] * fps)) < 1e-9, f"{key} must be a whole number of frames"
    ppm = man["px_per_m"]
    th = math.radians(a_deg)
    print(f"setup: side view, two bands on one clock, the same floor drawn the same way at the same scale: a {m:g} kg "
          f"crate ({w * 100:g} cm cube, weight m g = {m * g:.2f} N) rests on a level floor with grip (friction "
          f"coefficient) mu = {mu:g}, the same at rest and sliding (a chosen number); g = {g:g} m/s^2; the same force "
          f"F = {F:g} N acts at {a_deg:g} degrees to the floor, applied at mid-height ({hap * 100:g} cm up) so the crate "
          f"slides and never tips; top band PUSH: a rod on the rear face presses forward and down; bottom band PULL: "
          f"a rope on the front face pulls forward and up; the force acts for {T:g} s (the measurement window), then "
          f"the tool lets go and a moving crate skids to a stop under sliding friction mu m g; RK4 at {dt_n} steps "
          f"per second (dt = {dt:.0e} s) with the stick-slip rule each step, the forces held over each step, the stop "
          f"located by bisection, checked against the closed forms and a half-step rerun; shown at 1/{S:g} speed on a "
          f"{P:g} s cycle ({P * fps:.0f} frames) with the force coming on {fa:g} s into the cycle, {cycles:.0f} cycles "
          f"in {D:g} s; drawn at {ppm:g} px per metre; deterministic, no seed")
    print(f"the same in both bands: horizontal drive F cos a = {F * math.cos(th):.2f} N = {F * math.cos(th):.4f} N, "
          f"vertical part F sin a = {F * math.sin(th):.2f} N; weight {m * g:.2f} N; a crate at rest moves only when the "
          f"drive exceeds the grip limit mu N")
    ev: dict = {"runs": {}, "fo": {}, "half": {}}
    checks: list[tuple[str, float, float, float]] = []
    for key in PANELS:
        sign = SIGN[key]
        fo = forces(m, g, mu, F, a_deg, sign)
        run = rk4_run(m, g, mu, F, a_deg, sign, T, dt_n, 4.0)
        half = rk4_run(m, g, mu, F, a_deg, sign, T, 2 * dt_n, 4.0)
        ev["runs"][key], ev["fo"][key], ev["half"][key] = run, fo, half
        word = "press" if key == "push" else "lift"
        verdict = "slides" if fo["moves"] else "stays still"
        a_c = fo["a"]
        table = []
        for k in range(int(round(T / man["table_step_s"])) + 1):
            tq = k * man["table_step_s"]
            xq = float(np.interp(tq, run["t"], run["x"]))
            vq = float(np.interp(tq, run["t"], run["v"]))
            xc = 0.5 * a_c * tq * tq
            table.append(f"{tq:.1f} s: {xq:.4f} m at {vq:.4f} m/s (closed {xc:.4f} m, diff {xq - xc:+.1e} m)")
        err_x = float(np.max(np.abs(run["x"][run["t"] <= T] - 0.5 * a_c * run["t"][run["t"] <= T] ** 2)))
        print(f"{key} {'down' if key == 'push' else 'up'} at {a_deg:g} deg ({'top' if key == 'push' else 'bottom'} band): "
              f"weight {fo['weight']:.2f} N, {word} F sin a = {fo['vert']:.2f} N, floor push N = {fo['N']:.2f} N "
              f"({fo['N']:.4f} N), grip limit mu N = {fo['grip']:.2f} N ({fo['grip']:.4f} N), drive {fo['drive']:.2f} N, "
              f"net {fo['net']:+.2f} N: the crate {verdict}; a = {a_c:.4f} m/s^2 ({a_c:.6f}); RK4 table (real time after "
              f"the force came on): " + "; ".join(table) + f"; at the release ({T:g} s) {run['x_rel']:.4f} m = "
              f"{run['x_rel']:.3f} m moving {run['v_rel']:.4f} m/s = {run['v_rel']:.3f} m/s (closed form a T^2 / 2 = "
              f"{0.5 * a_c * T * T:.4f} m, a T = {a_c * T:.4f} m/s; diffs {run['x_rel'] - 0.5 * a_c * T * T:+.1e} m, "
              f"{run['v_rel'] - a_c * T:+.1e} m/s); the position stays within {err_x:.1e} m of the closed form over "
              f"the window; {run['steps']} steps; half-step rerun (dt = {0.5 * dt:.0e} s): {half['x_rel']:.9f} m "
              f"({half['x_rel'] - run['x_rel']:+.1e} m) at {half['v_rel']:.9f} m/s; 1 s {0.5 * a_c:.3f} m, 3 s without "
              f"the release would be {4.5 * a_c:.3f} m")
        assert abs(half["x_rel"] - run["x_rel"]) < 1e-9 and err_x < 1e-9
        if fo["moves"]:
            skid_d = run["x_stop"] - run["x_rel"]
            skid_t = run["t_stop"] - run["t_rel"]
            dec = mu * g
            d_c, t_c = run["v_rel"] ** 2 / (2.0 * dec), run["v_rel"] / dec
            print(f"{key} skid: at {T:g} s the rope lets go and the crate skids under sliding friction mu m g = "
                  f"{mu * m * g:.2f} N (deceleration mu g = {dec:.4f} m/s^2): skid {skid_d:.4f} m = {skid_d:.3f} m in "
                  f"{skid_t:.4f} s (closed form v^2 / (2 mu g) = {d_c:.4f} m, v / (mu g) = {t_c:.4f} s; diffs "
                  f"{skid_d - d_c:+.1e} m, {skid_t - t_c:+.1e} s), at rest {run['x_stop']:.4f} m = {run['x_stop']:.3f} m "
                  f"from the start at {run['t_stop']:.4f} s; half-step rerun stops at {half['x_stop']:.9f} m "
                  f"({half['x_stop'] - run['x_stop']:+.1e} m) at {half['t_stop']:.9f} s ({half['t_stop'] - run['t_stop']:+.1e} s)")
            assert abs(skid_d - d_c) < 1e-9 and abs(half["x_stop"] - run["x_stop"]) < 1e-9
            work = fo["drive"] * run["x_rel"]
            heat = fo["grip"] * run["x_rel"]
            kin = 0.5 * m * run["v_rel"] ** 2
            print(f"{key} energy at {T:g} s: drive work F cos a x = {work:.2f} J = friction heat mu N x = {heat:.2f} J + "
                  f"kinetic m v^2 / 2 = {kin:.2f} J (sum {heat + kin:.2f} J, diff {work - heat - kin:+.1e} J); the skid "
                  f"turns the {kin:.2f} J into heat over {skid_d:.3f} m ({mu * m * g * skid_d:.2f} J)")
            assert abs(work - heat - kin) < 1e-9
            ev["work"], ev["heat"], ev["kin"] = work, heat, kin
            checks += [("pull floor push N (N)", fo["N"], 73.07, 6e-3), ("pull grip limit (N)", fo["grip"], 29.23, 6e-3),
                       ("pull a (m/s^2)", a_c, 1.4073, 6e-5), ("pull 1 s (m)", 0.5 * a_c, 0.704, 6e-4),
                       ("pull 2 s (m)", run["x_rel"], 2.815, 6e-4), ("pull 2 s speed (m/s)", run["v_rel"], 2.815, 6e-4),
                       ("pull 3 s without release (m)", 4.5 * a_c, 6.333, 6e-4), ("skid (m)", skid_d, 1.010, 6e-4),
                       ("skid time (s)", skid_t, 0.7175, 6e-5), ("at rest (m)", run["x_stop"], 3.825, 1.5e-3),
                       ("at rest at (s)", run["t_stop"], 2.7175, 6e-5), ("drive work (J)", work, 121.88, 6e-3),
                       ("friction heat (J)", heat, 82.27, 6e-3), ("kinetic (J)", kin, 39.61, 6e-3)]
        else:
            assert run["x_stop"] == 0.0 and float(np.max(np.abs(run["x"]))) == 0.0
            print(f"{key}: the rod keeps pressing for the {T:g} s, then lifts off; the crate never moved (RK4 max |x| "
                  f"{float(np.max(np.abs(run['x']))):.1e} m); the static friction equals the drive {fo['drive']:.2f} N, "
                  f"{fo['grip'] - fo['drive']:.2f} N under the grip limit")
            checks += [("push floor push N (N)", fo["N"], 123.07, 6e-3), ("push grip limit (N)", fo["grip"], 49.23, 6e-3),
                       ("push a (m/s^2)", a_c, 0.0, 1e-12), ("push 2 s (m)", run["x_rel"], 0.0, 1e-12)]
    checks += [("drive F cos a (N)", F * math.cos(th), 43.30, 6e-3), ("vertical F sin a (N)", F * math.sin(th), 25.00, 6e-3),
               ("weight (N)", m * g, 98.07, 6e-3)]
    # Tipping check at mid-height.
    Fx, Fy = F * math.cos(th), F * math.sin(th)
    restore = m * g * w / 2.0
    tip_rear = Fx * hap
    lift_front = Fy * w
    print(f"tipping check (force at {hap * 100:g} cm up on a {w * 100:g} cm cube): pull: lifting the rear about the front "
          f"bottom edge F cos a h = {tip_rear:.2f} N m against m g w / 2 = {restore:.2f} N m: "
          f"{'no tip' if tip_rear < restore else 'TIPS'}; lifting the front about the rear bottom edge F sin a w = "
          f"{lift_front:.2f} N m against {restore:.2f} + {tip_rear:.2f} = {restore + tip_rear:.2f} N m: "
          f"{'no tip' if lift_front < restore + tip_rear else 'TIPS'}; push: lifting the rear about the front bottom edge "
          f"{tip_rear:.2f} N m against m g w / 2 + F sin a w = {restore + lift_front:.2f} N m: "
          f"{'no tip' if tip_rear < restore + lift_front else 'TIPS'}; the crate slides and never tips")
    assert tip_rear < restore and lift_front < restore + tip_rear
    checks += [("tip F cos a h (N m)", tip_rear, 10.83, 6e-3), ("restoring m g w / 2 (N m)", restore, 24.52, 6e-3),
               ("lift F sin a w (N m)", lift_front, 12.50, 6e-3)]
    # Thresholds and angles.
    f_pull = threshold_force(m, g, mu, a_deg, 1.0)
    f_push = threshold_force(m, g, mu, a_deg, -1.0)
    f_flat = mu * m * g
    lock = math.degrees(math.atan(1.0 / mu))
    best = math.degrees(math.atan(mu))
    f_best = mu * m * g / math.sqrt(1.0 + mu * mu)
    pct = 100.0 * (1.0 - 1.0 / math.sqrt(1.0 + mu * mu))
    print(f"thresholds: the force that just moves the crate at {a_deg:g} deg is mu m g / (cos a + mu sin a) = {f_pull:.2f} N "
          f"pulling against mu m g / (cos a - mu sin a) = {f_push:.2f} N pushing (ratio {f_push / f_pull:.4f}); flat "
          f"(0 deg) mu m g = {f_flat:.2f} N; push lock angle acot(mu) = {lock:.2f} deg (at or above it no push, however "
          f"hard, moves the crate: the extra press adds more grip than drive); best pull angle atan(mu) = {best:.2f} deg "
          f"needing mu m g / sqrt(1 + mu^2) = {f_best:.2f} N ({pct:.1f} percent less than flat)")
    checks += [("pull threshold (N)", f_pull, 36.80, 6e-3), ("push threshold (N)", f_push, 58.90, 6e-3),
               ("threshold ratio", f_push / f_pull, 1.6006, 6e-5), ("flat threshold (N)", f_flat, 39.23, 6e-3),
               ("lock angle (deg)", lock, 68.20, 6e-3), ("best pull angle (deg)", best, 21.80, 6e-3),
               ("best pull force (N)", f_best, 36.42, 6e-3), ("best pull saving (percent)", pct, 7.2, 6e-2)]
    ev.update({"f_pull": f_pull, "f_push": f_push, "f_flat": f_flat, "lock": lock, "best": best, "f_best": f_best, "pct": pct})
    # Variants for the description (closed forms, RK4 cross-checked at the window).
    descr = []
    want = {("F", 40.0): (0.683, 0.0), ("F", 60.0): (4.947, 0.147), ("F", 70.0): (7.079, 1.479),
            ("mu", 0.3): (4.276, 1.276), ("mu", 0.5): (1.353, 0.0), ("deg", 0.0): (2.154, 2.154),
            ("deg", 15.0): (2.849, 0.778), ("deg", 45.0): (2.054, 0.0), ("deg", 60.0): (0.619, 0.0)}
    ev["variants"] = {}
    for kind, vals in (("F", man["description_forces_n"]), ("mu", man["description_mus"]), ("deg", man["description_angles_deg"])):
        for val in vals:
            F2, mu2, d2 = (val if kind == "F" else F), (val if kind == "mu" else mu), (val if kind == "deg" else a_deg)
            out = {}
            for key in PANELS:
                fo2 = forces(m, g, mu2, F2, d2, SIGN[key])
                r2 = rk4_run(m, g, mu2, F2, d2, SIGN[key], T, dt_n, T)
                assert abs(r2["x_rel"] - 0.5 * fo2["a"] * T * T) < 1e-9
                out[key] = (fo2["a"], r2["x_rel"], fo2["N"], fo2["grip"], fo2["drive"])
            ev["variants"][(kind, val)] = out
            label = {"F": f"F {val:g} N at {a_deg:g} deg", "mu": f"grip {val:g}, {F:g} N at {a_deg:g} deg",
                     "deg": f"{F:g} N at {val:g} deg"}[kind]
            descr.append(f"{label}: pull N {out['pull'][2]:.2f} N, grip {out['pull'][3]:.2f} N, a {out['pull'][0]:.3f} m/s^2; "
                         f"push N {out['push'][2]:.2f} N, grip {out['push'][3]:.2f} N, a {out['push'][0]:.3f} m/s^2; drive "
                         f"{out['pull'][4]:.2f} N; at {T:g} s {out['pull'][1]:.3f} against {out['push'][1]:.3f} m")
            wp, ws = want[(kind, val)]
            checks += [(f"{label} pull 2 s (m)", out["pull"][1], wp, 6e-4), (f"{label} push 2 s (m)", out["push"][1], ws, 6e-4)]
    print("for the description: " + "; ".join(descr))
    fails = 0
    out = []
    for name, got, wnt, tol in checks:
        ok = abs(got - wnt) <= tol
        fails += 0 if ok else 1
        out.append(f"{name}: brief {wnt:g}, sim {got:.6g}, diff {got - wnt:+.1e}: {'ok' if ok else 'FAIL'}")
    print(f"checks against the brief ({len(checks)} checks, {fails} failed): " + "; ".join(out))
    ev["checks"], ev["fails"] = len(checks), fails
    # The schedule in video time.
    t0 = man["first_cycle_at"]
    k0 = math.ceil((0.0 - t0) / P - 1e-9) - 1
    k1 = math.floor((D - t0) / P - 1e-9)
    starts = [t0 + kk * P for kk in range(k0, k1 + 1)]
    ev["cycles"] = int(round(cycles))

    def lst(off_: float) -> str:
        return ", ".join(f"{st + off_:.2f}" for st in starts if 0.0 <= st + off_ < D)

    run_pull = ev["runs"]["pull"]
    vt = lambda real: fa + real * S   # noqa: E731  video time after the cycle start
    rest_v = vt(run_pull["t_stop"])
    assert rest_v < P - Fd, "the pull crate is still skidding at the reset fade"
    tau0 = (0.0 - t0) % P
    r0 = (tau0 - fa) / S
    st0 = {key: state_at(ev["runs"][key], r0) for key in PANELS}
    ev["rest_v"] = rest_v
    print(f"schedule (video time, 1/{S:g} speed): cycles of {P:g} s start at " + ", ".join(f"{st:.2f}" for st in starts)
          + f" s (the first {-t0:.2f} s before the first frame); the force comes on {fa:g} s into each cycle at {lst(fa)} s; "
          f"the {T:g} s mark (the rope and the rod let go, both event rows light) is {vt(T):.2f} s into the cycle at "
          f"{lst(vt(T))} s; the pull crate is at rest {rest_v:.3f} s into the cycle ({S * run_pull['t_stop']:.3f} s after "
          f"the force) at {lst(rest_v)} s, before the fade at {P - Fd:.2f} s; the tools fade over {man['tool_fade_s']:g} s "
          f"after the release; the reset crossfade runs over the last {Fd:g} s of each cycle (from {lst(P - Fd)} s; the "
          f"readouts out over its first half and in over its second); on the first frame the cycle is {tau0:.2f} s in "
          f"({r0:.3f} s real after the force came on: the push crate {st0['push']['phase']} at {st0['push']['x']:.3f} m, the "
          f"pull crate {st0['pull']['phase']} at {st0['pull']['x']:.3f} m moving {st0['pull']['v']:.3f} m/s); title until "
          f"{man['title_until']:g} s; payoff card from {man['payoff_t']:g} s; the title fades back in over the last "
          f"{man['loop_fade']:g} s and the last frame repeats the first (the scene is periodic: {D:g} s holds exactly "
          f"{cycles:.0f} cycles)")
    # Text widths.
    font = os.environ["SEED_ZERO_FONT"]
    f24, f28, f34, f40, f56 = (ImageFont.truetype(font, n) for n in (24, 28, 34, 40, 56))
    widths = {"overlay@34": (f34, man["overlay"])}
    for j, line in enumerate(man["title"].split("|")):
        widths[f"title line {j + 1}@56"] = (f56, line)
    assert len(man["title"].split("|")) <= len(TITLE_Y), "too many title rows"
    widths["legend@40"] = (f40, legend_text(man))
    widths["clock@28"] = (f28, clock_text(1.2515))
    widths["clock held@28"] = (f28, clock_text(-1.0))
    for key in PANELS:
        fo = ev["fo"][key]
        widths[f"label {key}@40"] = (f40, label_text(man, key))
        widths[f"floor push {key}@28"] = (f28, floor_text(fo["N"]))
        widths[f"fixed {key}@28"] = (f28, fixed_text(key, fo))
        widths[f"grip {key}@28"] = (f28, grip_text(fo["grip"]))
        widths[f"event {key}@40"] = (f40, event_text(ev, key))
    widths["moved@40"] = (f40, moved_text(run_pull["x_stop"]))
    widths["speed@28"] = (f28, speed_text(2.8146))
    widths["meter label@24"] = (f24, "grip limit")
    widths["meter value@24"] = (f24, meter_value(123.07))
    widths["verdict@24"] = (f24, "slides")
    widths["mark@24"] = (f24, mark_text(T))
    widths["start@24"] = (f24, "start")
    for j, line in enumerate(payoff_lines(man, ev)):
        widths[f"payoff line {j + 1}@40"] = (f40, line)
    print("text widths (the on-screen strings verbatim): " + ", ".join(f"{kk} {f.getlength(s):.0f} px '{s}'"
                                                                       for kk, (f, s) in widths.items()))
    assert all(f.getlength(s) < 950 for f, s in widths.values()), "a text line is wider than 950 px"
    assert len(payoff_lines(man, ev)) <= 6, "the card has more than six lines"
    # Layout checks.
    left = ROW_X0 + max(max(f40.getlength(label_text(man, key)), f28.getlength(floor_text(ev["fo"][key]["N"])),
                            f28.getlength(fixed_text(key, ev["fo"][key]))) for key in PANELS)
    right = ROW_X1 - max(f40.getlength(moved_text(run_pull["x_stop"])), f28.getlength(grip_text(49.23)),
                         f28.getlength(speed_text(2.8146)))
    rows_bottom = FIX_DY + 16
    sx, floor = float(man["start_x_px"]), float(man["floor_dy"])
    side = w * ppm
    cy = floor - side / 2.0
    far_front = sx + run_pull["x_stop"] * ppm + side
    far_rope = sx + run_pull["x_rel"] * ppm + side + TOOL_LEN * math.cos(th)
    rope_top = cy - TOOL_LEN * math.sin(th)
    drive_len = F * PX_PER_N
    rod_tail_x = sx - drive_len * math.cos(th)
    n_top = {key: floor - ev["fo"][key]["N"] * PX_PER_N for key in PANELS}
    n_top_skid = floor - m * g * PX_PER_N
    w_tip = cy + m * g * PX_PER_N
    meter_top, meter_bottom = METER_DY[0] - 13, METER_DY[1] + 13
    meter_x0 = METER_LABEL_X - f24.getlength("grip limit")
    ev_w = {key: f40.getlength(event_text(ev, key)) for key in PANELS}
    ev_x0, ev_x1 = {key: EVENT_X - ev_w[key] / 2.0 for key in PANELS}, {key: EVENT_X + ev_w[key] / 2.0 for key in PANELS}
    push_w_x = sx + side / 2.0 + ARROW_DX
    pull_w_x_lit = sx + run_pull["x_rel"] * ppm + side / 2.0 + ARROW_DX
    mark_x = sx + run_pull["x_rel"] * ppm
    grip_len = max(ev["fo"]["push"]["grip"], mu * m * g) * PX_PER_N
    fric_x0 = sx + side / 2.0 - grip_len
    print(f"row check: the left column ends at x {left:.0f} px, the right column starts at x {right:.0f} px; both end "
          f"{rows_bottom} px under the band top; the grip meter spans {meter_top} to {meter_bottom} px under the band top "
          f"and x {meter_x0:.0f} to {METER_END_X}; the floor line is {floor:.0f} px under the band top (plank to "
          f"{floor + PLANK_PX:.0f}), the crate {side:.0f} px square from {cy - side / 2.0:.0f} px with its rear face at "
          f"x {sx:.0f} at the start; the pull crate's rear face reaches x {sx + run_pull['x_rel'] * ppm:.0f} at the "
          f"{T:g} s mark and its front face x {far_front:.1f} at rest ({run_pull['x_stop']:.3f} m), the rope's far end "
          f"x {far_rope:.0f} and {rope_top:.0f} px under the band top; the push arrow's tail at x {rod_tail_x:.1f}; the "
          f"floor push arrow tops {n_top['push']:.0f} (push), {n_top['pull']:.0f} (pull) and {n_top_skid:.0f} (skid, N = m g) "
          f"px under the band top; the weight arrow's tip at {w_tip:.0f} px; the friction arrow reaches x {fric_x0:.0f} "
          f"inside the plank; the event row spans {EVENT_DY - 22} to {EVENT_DY + 22} px under the band top and x "
          f"{ev_x0['push']:.0f} to {ev_x1['push']:.0f} (push, {ev_w['push']:.0f} px) and {ev_x0['pull']:.0f} to "
          f"{ev_x1['pull']:.0f} (pull, {ev_w['pull']:.0f} px), centred on {EVENT_X}; the push weight arrow stands at x "
          f"{push_w_x:.0f}, the pull one at x {pull_w_x_lit:.0f} when its event row lights; the {T:g} s mark at x "
          f"{mark_x:.1f}; each band is {BAND_H} px tall (y {BAND_Y['push']} to {BAND_Y['push'] + BAND_H} and {BAND_Y['pull']} "
          f"to {BAND_Y['pull'] + BAND_H}); the caption band starts at y {int(man['caption_y'] * H)}; the title rows end at "
          f"y {TITLE_Y[len(man['title'].split('|')) - 1] + 28} and the overlay band ends at y 130")
    assert right - left > 40, "the columns meet"
    assert far_front < W - 12, "the pull crate leaves the frame at rest"
    assert far_rope < W - 8 and rope_top > meter_bottom + 10, "the rope leaves the band or meets the meter"
    assert rod_tail_x > 8, "the push arrow's tail leaves the frame"
    assert min(n_top.values()) > rows_bottom + 10, "the floor push arrow meets the text rows"
    assert n_top_skid > meter_bottom + 4 and n_top["pull"] > meter_bottom + 4, "the pull floor push arrow meets the meter"
    assert w_tip < BAND_H - 6, "the weight arrow leaves the band"
    assert fric_x0 > 20, "the friction arrow leaves the frame"
    assert cy - side / 2.0 > rows_bottom + 10, "the crate meets the text rows"
    assert EVENT_DY - 22 > floor + PLANK_PX + 10 and EVENT_DY + 22 < BAND_H - 8, "the event row leaves the ground region"
    assert ev_x0["push"] > push_w_x + 30, "the push event row meets the push weight arrow"
    assert ev_x1["pull"] < pull_w_x_lit - 30, "the pull event row meets the pull weight arrow when it lights"
    assert meter_x0 > push_w_x + 30, "the meter meets the push floor push arrow"
    assert BAND_Y["pull"] + BAND_H <= int(man["caption_y"] * H), "the bottom band reaches the caption band"
    assert PAYOFF_Y - 20 > int(man["caption_y"] * H) + 90, "the card meets the caption band"
    assert TITLE_Y[len(man["title"].split("|")) - 1] + 28 <= BAND_Y["push"], "the title rows reach the first band"
    return ev


def legend_text(man: dict) -> str:
    return f"same crate, same {man['force_n']:g} N, 1/{man['slow']:g} speed"


def clock_text(r: float) -> str:
    return "at rest, no force yet" if r < 0.0 else f"{r:.3f} s after the force came on"


def label_text(man: dict, key: str) -> str:
    return f"{'push down' if key == 'push' else 'pull up'} at {man['angle_deg']:g} deg"


def floor_text(N: float) -> str:
    return f"floor push: {N:.1f} N"


def fixed_text(key: str, fo: dict) -> str:
    return f"weight {fo['weight']:.1f} N, {'press' if key == 'push' else 'lift'} {fo['vert']:.1f} N"


def grip_text(grip: float) -> str:
    return f"grip limit: {grip:.1f} N"


def moved_text(x: float) -> str:
    return f"moved: {x:.2f} m"


def speed_text(v: float) -> str:
    return f"speed {v:.2f} m/s"


def meter_value(n: float) -> str:
    return f"{n:.1f} N"


def mark_text(T: float) -> str:
    return f"{T:g} s"


def event_text(ev: dict, key: str) -> str:
    if key == "push":
        return "push down: it never moves"
    return f"pull up: {ev['runs']['pull']['x_rel']:.1f} m in {ev['runs']['pull']['t_rel']:g} s"


def payoff_lines(man: dict, ev: dict) -> list[str]:
    fo = ev["fo"]
    text = man["payoff_text"].format(
        x2=ev["runs"]["pull"]["x_rel"], n_pull=fo["pull"]["N"], n_push=fo["push"]["N"], g_pull=fo["pull"]["grip"],
        g_push=fo["push"]["grip"], drive=fo["pull"]["drive"], f_pull=ev["f_pull"], f_push=ev["f_push"], lock=ev["lock"])
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
        self.font_layer = ImageFont.truetype(font, 24 * SS)
        self.ppm = float(man["px_per_m"])
        self.S = man["slow"]
        self.P = man["cycle_s"]
        self.P_f = int(round(man["cycle_s"] * self.fps))
        self.c0_f = int(round(man["first_cycle_at"] * self.fps))
        self.fa, self.F = man["force_at"], man["reset_fade"]
        self.runs = ev["runs"]
        self.sx = float(man["start_x_px"])
        self.floor = float(man["floor_dy"])
        self.side = man["crate_m"] * self.ppm
        self.cy = self.floor - self.side / 2.0
        self.th = math.radians(man["angle_deg"])
        self.T = man["window_s"]
        self.mark_x = self.sx + self.runs["pull"]["x_rel"] * self.ppm

    def phase(self, f: int) -> tuple[int, float]:
        k, tau_f = divmod(f - self.c0_f, self.P_f)
        return k, tau_f / self.fps

    @staticmethod
    def L_(x: float, y: float) -> tuple[float, float]:
        """Layer (2x) pixel of a band-local point, rounded to 1e-4 px so equal states draw equal pixels."""
        return round(x * SS, 4), round(y * SS, 4)

    def arrow(self, d: ImageDraw.ImageDraw, x0: float, y0: float, x1: float, y1: float, col, width: float) -> None:
        """A straight arrow in the layer from (x0, y0) with its tip at (x1, y1), band-local 1x units."""
        length = math.hypot(x1 - x0, y1 - y0)
        if length < 1.0:
            return
        ux, uy = (x1 - x0) / length, (y1 - y0) / length
        head = min(ARROW_HEAD, length)
        bx, by = x1 - ux * head, y1 - uy * head
        if length > head:
            d.line((*self.L_(x0, y0), *self.L_(bx, by)), fill=col, width=int(round(width * SS)))
        hw = head * 0.5
        d.polygon([self.L_(x1, y1), self.L_(bx - uy * hw, by + ux * hw), self.L_(bx + uy * hw, by - ux * hw)], fill=col)

    def draw_floor(self, d: ImageDraw.ImageDraw, key: str, st: dict) -> None:
        f = self.floor
        p0, p1 = self.L_(-12.0, f), self.L_(W + 12.0, f + PLANK_PX)
        d.rectangle((p0[0], p0[1], p1[0], p1[1]), fill=DECK_A)
        d.line((*self.L_(-12.0, f), *self.L_(W + 12.0, f)), fill=DECK_B, width=3 * SS)
        # The start mark: a gold notch under the plank with its label.
        m0, m1, m2 = self.L_(self.sx, f + PLANK_PX + 2), self.L_(self.sx - 9, f + PLANK_PX + 16), self.L_(self.sx + 9, f + PLANK_PX + 16)
        d.polygon([m0, m1, m2], fill=GOLD)
        d.text(self.L_(self.sx, f + PLANK_PX + 32), "start", font=self.font_layer, fill=INK, anchor="mm")
        if key == "pull":
            # The dashed 2 s mark on the floor, lit gold when the clock reaches the window.
            lit = st["phase"] in (SKID, STOP)
            col = GOLD if lit else blend(GOLD, 0.35)
            x = self.mark_x
            y = f - 60.0
            while y < f + PLANK_PX - 4:
                d.line((*self.L_(x, y), *self.L_(x, min(y + 8.0, f + PLANK_PX - 4))), fill=col, width=3 * SS)
                y += 14.0
            d.text(self.L_(x - 10.0, f - 22.0), mark_text(self.T), font=self.font_layer, fill=col, anchor="rm")

    def draw_crate(self, d: ImageDraw.ImageDraw, cx: float) -> None:
        h = self.side / 2.0
        p0, p1 = self.L_(cx - h, self.cy - h), self.L_(cx + h, self.cy + h)
        d.rectangle((p0[0], p0[1], p1[0], p1[1]), fill=CARD, outline=CARD_EDGE, width=2 * SS)
        t0, t1 = self.L_(cx - 4, self.cy - h + 2), self.L_(cx + 4, self.cy + h - 2)
        d.rectangle((t0[0], t0[1], t1[0], t1[1]), fill=CARD_TAPE)
        for dy in (-h + 16, h - 16):
            l0, l1 = self.L_(cx - h + 3, self.cy + dy), self.L_(cx + h - 3, self.cy + dy)
            d.line((*l0, *l1), fill=CARD_EDGE, width=2 * SS)

    def draw_tool(self, d: ImageDraw.ImageDraw, key: str, cx: float, st: dict) -> None:
        """The rod (push, from the upper left on to the rear face) or the rope (pull, from the front face to
        the upper right); after the release the rod backs off along its axis and both fade."""
        tv = st["tv"]
        fade = self.man["tool_fade_s"]
        a = 1.0 if tv < self.S * self.T else max(0.0, 1.0 - (tv - self.S * self.T) / fade)
        if a <= 0.0:
            return
        h = self.side / 2.0
        c, s = math.cos(self.th), math.sin(self.th)
        if key == "push":
            back = 40.0 * (1.0 - a)
            px, py = cx - h - back * c, self.cy - back * s           # the pad's contact point
            ex, ey = px - TOOL_LEN * c, py - TOOL_LEN * s
            d.line((*self.L_(px, py), *self.L_(ex, ey)), fill=blend(ROD, a), width=14 * SS)
            d.line((*self.L_(px - 2 * c, py - 2 * s), *self.L_(ex, ey)), fill=blend(ROD_DARK, a), width=3 * SS)
            q0, q1 = self.L_(px - 4.0, py - 22.0), self.L_(px, py + 22.0)
            d.rectangle((q0[0], q0[1], q1[0], q1[1]), fill=blend(ROD, a), outline=blend(ROD_DARK, a), width=SS)
        else:
            px, py = cx + h, self.cy
            ex, ey = px + TOOL_LEN * c, py - TOOL_LEN * s
            d.line((*self.L_(px, py), *self.L_(ex, ey)), fill=blend(ROPE, a), width=4 * SS)
            r = 6.0 * SS
            k = self.L_(px + 2.0, py)
            d.ellipse((k[0] - r, k[1] - r, k[0] + r, k[1] + r), fill=blend(ROPE, a), outline=blend(CARD_EDGE, a), width=SS)

    def draw_forces(self, d: ImageDraw.ImageDraw, key: str, cx: float, st: dict) -> None:
        h = self.side / 2.0
        c, s = math.cos(self.th), math.sin(self.th)
        # The grip limit as a dim coral line inside the plank, then the friction acting as a solid arrow.
        y_f = self.floor + PLANK_PX / 2.0
        if st["grip"] > 0.0:
            d.line((*self.L_(cx, y_f), *self.L_(cx - st["grip"] * PX_PER_N, y_f)), fill=blend(CORAL, 0.35), width=4 * SS)
        if st["fric"] > 0.0:
            self.arrow(d, cx, y_f, cx - st["fric"] * PX_PER_N, y_f, CORAL, 6.0)
        # The floor push up from the floor through the crate, the weight down from the centre.
        self.arrow(d, cx - ARROW_DX, self.floor, cx - ARROW_DX, self.floor - st["N"] * PX_PER_N, STEEL, 6.0)
        self.arrow(d, cx + ARROW_DX, self.cy, cx + ARROW_DX, self.cy + self.man["crate_kg"] * self.man["g"] * PX_PER_N,
                   MUTED, 6.0)
        # The drive: F at the angle, into the rear face (push) or away from the front face (pull).
        if st["phase"] == FORCE:
            L = self.man["force_n"] * PX_PER_N
            if key == "push":
                self.arrow(d, cx - h - L * c, self.cy - L * s, cx - h, self.cy, TEAL, 6.0)
            else:
                self.arrow(d, cx + h, self.cy, cx + h + L * c, self.cy - L * s, TEAL, 6.0)

    def scene(self, key: str, tau: float) -> tuple[Image.Image, dict]:
        """The band layer of panel key at tau seconds into a cycle (the resting setup before the force)."""
        layer = Image.new("RGB", (W * SS, BAND_H * SS), BG)
        d = ImageDraw.Draw(layer)
        tv = tau - self.fa
        rt = tv / self.S
        st = state_at(self.runs[key], rt)
        st["tv"], st["rt"] = tv, rt
        self.draw_floor(d, key, st)
        cx = self.sx + st["x"] * self.ppm + self.side / 2.0
        self.draw_tool(d, key, cx, st)
        self.draw_crate(d, cx)
        self.draw_forces(d, key, cx, st)
        return layer, st

    def draw_panel(self, key: str, f: int) -> tuple[Image.Image, dict]:
        k, tau = self.phase(f)
        P, F = self.P, self.F
        layer, st = self.scene(key, tau)
        st["alpha"], st["k"] = 1.0, k
        if tau >= P - F:
            # Crossfade to the next cycle's resting setup (the pull crate is at rest by now, asserted in measure).
            a = (tau - (P - F)) / F
            new, st_new = self.scene(key, tau - P)
            layer = Image.blend(layer, new, a)
            st["alpha"] = max(0.0, 1.0 - 2.0 * a)
            st_new["alpha"], st_new["k"] = max(0.0, 2.0 * a - 1.0), k + 1
            if a >= 0.5:
                st = st_new
        return layer, st

    def draw_meter(self, d: ImageDraw.ImageDraw, y0: int, st: dict, a: float) -> None:
        rows = (("drive", st["drive"], TEAL), ("grip limit", st["grip"], CORAL))
        winner = None
        if st["drive"] > 0.0:
            winner = 0 if st["drive"] > st["grip"] else 1
        for j, (name, val, col) in enumerate(rows):
            y = y0 + METER_DY[j]
            d.text((METER_LABEL_X, y), name, font=self.font_tiny, fill=blend(TEXT, a), anchor="rm")
            if val > 0.0:
                d.rectangle((METER_BAR_X, y - 5, METER_BAR_X + val * PX_PER_N, y + 5), fill=blend(col, a))
            d.text((METER_VAL_X, y), meter_value(val), font=self.font_tiny, fill=blend(TEXT, a), anchor="lm")
            if winner == j:
                d.text((METER_END_X, y), "slides" if j == 0 else "holds", font=self.font_tiny, fill=blend(GOLD, a), anchor="rm")

    def draw_text(self, d: ImageDraw.ImageDraw, states: dict, hud_alpha: float) -> None:
        man, ev = self.man, self.ev
        for key, st in states.items():
            y0 = BAND_Y[key]
            a, ph = st["alpha"], st["phase"]
            fo = ev["fo"][key]
            lit = ph in (SKID, STOP)
            d.text((ROW_X0, y0 + LABEL_DY), label_text(man, key), font=self.font, fill=COLOUR[key], anchor="lm")
            d.text((ROW_X0, y0 + SUB_DY), floor_text(st["N"]), font=self.font_small, fill=blend(TEXT, a), anchor="lm")
            d.text((ROW_X0, y0 + FIX_DY), fixed_text(key, fo), font=self.font_small, fill=MUTED, anchor="lm")
            d.text((ROW_X1, y0 + LABEL_DY), moved_text(st["x"]), font=self.font, fill=blend(GOLD if lit else TEXT, a),
                   anchor="rm")
            d.text((ROW_X1, y0 + SUB_DY), grip_text(st["grip"]), font=self.font_small, fill=blend(TEXT, a), anchor="rm")
            d.text((ROW_X1, y0 + FIX_DY), speed_text(st["v"]), font=self.font_small, fill=blend(MUTED, a), anchor="rm")
            self.draw_meter(d, y0, st, a)
            if lit:
                d.text((EVENT_X, y0 + EVENT_DY), event_text(ev, key), font=self.font, fill=blend(GOLD, a), anchor="mm")
        if hud_alpha > 0.02:
            d.text((W / 2, LEGEND_Y), legend_text(man), font=self.font, fill=blend(TEXT, hud_alpha), anchor="mm")
            d.text((W / 2, CLOCK_Y), clock_text(states["push"]["rt"]), font=self.font_small,
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
    man = json.loads((ROOT / "projects/pushpull/manifest.json").read_text())
    ev = measure(man)
    if "--measure-only" in sys.argv:
        return
    if "--frames" in sys.argv:
        times = [float(v) for v in sys.argv[sys.argv.index("--frames") + 1].split(",")]
        r = Renderer(man, ev)
        (ROOT / "media/pushpull").mkdir(parents=True, exist_ok=True)
        for tv in times:
            Image.fromarray(r.frame_at(int(round(tv * man["fps"])))).save(ROOT / f"media/pushpull/smoke-{tv}.png")
        print("smoke frames: " + ", ".join(f"{tv}" for tv in times))
        return
    Renderer(man, ev).render(ROOT / "media/pushpull/footage.mp4")


if __name__ == "__main__":
    main()
