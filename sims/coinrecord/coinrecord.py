#!/usr/bin/env python3
"""Coin on a record: does the coin stay on the record?

Two panels on the same clock, the same record drawn the same way at the
same scale, seen from above: a 30 cm record (radius R) turns at a steady
speed, clockwise as seen from above like a real turntable, flush with a
still deck around it (a lazy susan: the deck beyond the rim does not
turn). A coin (a point mass for the physics; its mass cancels) sits r0
from the centre, held down by a fingertip so it moves with the record; at
the release the fingertip lifts and friction alone must hold the coin.
Friction mu between the coin and the record and the same mu on the deck,
the same at rest and sliding. Top panel 45 rpm, bottom panel 78 rpm.

Static test: the coin rides along while the grip it needs, omega^2 r0 / g,
is at most mu; the limit at r0 is omega* = sqrt(mu g / r0) and a speed
omega holds a coin out to mu g / omega^2. Sliding: the coin is integrated
in the inertial (deck) frame by RK4 at dt: its acceleration is mu g
opposite to its velocity relative to the record surface under it (the
surface at (x, y) moves at omega (-y, x)); at the release the relative
velocity is zero and the friction is mu g toward the centre (the direction
of impending slip); after that the relative speed is positive. The rim
crossing (the coin's radius reaching R) is located by bisection inside the
step and checked by a half-step rerun. Past the rim the coin skids on the
still deck under the same mu, decelerating at mu g in a straight line from
its exit velocity: distance v^2 / (2 mu g), time v / (mu g). The run
repeats every cycle_s seconds of video with a crossfade back to the held
setup; the cycle divides the scene length, so the scene is exactly
periodic and the last frame equals the first. Shown at 1/slow speed.
Deterministic, no seed.

Measured and printed: the grip needed in each panel against mu and the
radius each speed holds out to, the limit speed at r0, the RK4 slide of
the 78 rpm coin (the time off the rim, the angle round, the speed, the
speed relative to the record, the record's turn, the lag, the slide table
at 10 ms, the half-step rerun, the early-radius check against the
rotating-frame start), the skid on the deck, the other speeds for the
description, the chosen start angle, the schedule in video time, the
on-screen text widths and the layout clearances.

usage: coinrecord.py [--measure-only] [--frames t1,t2,...]
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
DECK = (40, 47, 58)
DECK_EDGE = (58, 68, 82)
VINYL = (17, 19, 24)
GROOVE = (36, 41, 50)
RIM = (96, 108, 126)
LABEL = (64, 54, 78)
LABEL_MARK = (176, 152, 196)
SPINDLE = (150, 160, 176)
COIN = (222, 206, 160)
COIN_RING = (196, 178, 130)
COIN_EDGE = (124, 108, 68)
FINGER = (124, 136, 154)
FINGER_DARK = (62, 70, 84)
SKID = (170, 92, 84)

# Layout: overlay at y 96..130 (captions.py), two title rows at y 190/252 for
# the first seconds, then the legend at y 236 and the shared clock at y 290;
# two bands stacked, 45 rpm in y 330..880 and 78 rpm in y 880..1430, each
# drawn at 2x in its own geometry layer; each band has its label row 40 px
# under the band top and its second row at 84 (left column from x 40, right
# column to x 1040); the deck slab from SLAB_Y0 to SLAB_Y1 under the band
# top; the record centred at record_centre_px (x, dy under the band top);
# the gold event row at 518 under the band top (496..540); captions at
# caption_y 0.75 (y 1440..1530); the six-line card from y 1572 at a 48 px
# pitch.
LEGEND_Y, CLOCK_Y = 236, 290
SS = 2
PAYOFF_Y, PAYOFF_PITCH = 1572.0, 48
PANELS = ("top", "bottom")
BAND_Y = {"top": 330, "bottom": 880}
BAND_H = 550
LABEL_DY, SUB_DY = 40, 84
EVENT_DY = 518
ROW_X0, ROW_X1 = 40, 1040
SLAB_X0, SLAB_X1, SLAB_Y0, SLAB_Y1 = 24, 1056, 108, 492
COLOUR = {"top": TEAL, "bottom": CORAL}
HELD, RIDE, SLIDE, SKIDS, REST = "held", "ride", "slide", "skid", "rest"
FINGER_SCALE = 1.45
FINGER_DX, FINGER_DY = -6.0, -7.0


def blend(col, a: float, base=BG) -> tuple:
    a = max(0.0, min(1.0, a))
    return tuple(int(round(c * a + b * (1 - a))) for c, b in zip(col, base))


def rot(x: float, y: float, a: float) -> tuple[float, float]:
    c, s = math.cos(a), math.sin(a)
    return c * x - s * y, s * x + c * y


def rpm_to_omega(rpm: float) -> float:
    return rpm * 2.0 * math.pi / 60.0


def omega_to_rpm(omega: float) -> float:
    return omega * 60.0 / (2.0 * math.pi)


# --- measurement --------------------------------------------------------------
def grip_needed(omega: float, r: float, g: float) -> float:
    """omega^2 r / g: the friction coefficient a coin at radius r needs to ride along."""
    return omega * omega * r / g


def holds_out_to(omega: float, mu: float, g: float) -> float:
    """mu g / omega^2: the radius out to which a speed omega holds a coin of grip mu."""
    return mu * g / (omega * omega)


def limit_omega(mu: float, g: float, r: float) -> float:
    """sqrt(mu g / r): the speed at which a coin at radius r starts to slide."""
    return math.sqrt(mu * g / r)


def static_run(omega: float, theta0: float, r0: float, mu: float, g: float, R: float) -> dict:
    return {"static": True, "omega": omega, "theta0": theta0, "r0": r0, "mu": mu, "g": g, "R": R,
            "t_off": math.inf}


def rk4_slide(omega: float, mu: float, g: float, r0: float, R: float, dt: float, theta0: float) -> dict:
    """Integrate the coin in the inertial frame from rest relative to the record at radius r0 and
    angle theta0 by classical RK4 at dt until its radius reaches R; the crossing is located by
    bisection on the last step. The friction is mu g opposite to the velocity relative to the
    record surface, toward the centre when that velocity is zero (the first evaluation only)."""

    def acc(x: float, y: float, vx: float, vy: float) -> tuple[float, float]:
        ux, uy = -omega * y, omega * x
        rx, ry = vx - ux, vy - uy
        s = math.hypot(rx, ry)
        if s < 1e-9:
            rr = math.hypot(x, y)
            return -mu * g * x / rr, -mu * g * y / rr
        return -mu * g * rx / s, -mu * g * ry / s

    def step(x: float, y: float, vx: float, vy: float, h: float) -> tuple[float, float, float, float]:
        ax1, ay1 = acc(x, y, vx, vy)
        x2, y2, vx2, vy2 = x + 0.5 * h * vx, y + 0.5 * h * vy, vx + 0.5 * h * ax1, vy + 0.5 * h * ay1
        ax2, ay2 = acc(x2, y2, vx2, vy2)
        x3, y3, vx3, vy3 = x + 0.5 * h * vx2, y + 0.5 * h * vy2, vx + 0.5 * h * ax2, vy + 0.5 * h * ay2
        ax3, ay3 = acc(x3, y3, vx3, vy3)
        x4, y4, vx4, vy4 = x + h * vx3, y + h * vy3, vx + h * ax3, vy + h * ay3
        ax4, ay4 = acc(x4, y4, vx4, vy4)
        return (x + h * (vx + 2.0 * vx2 + 2.0 * vx3 + vx4) / 6.0, y + h * (vy + 2.0 * vy2 + 2.0 * vy3 + vy4) / 6.0,
                vx + h * (ax1 + 2.0 * ax2 + 2.0 * ax3 + ax4) / 6.0, vy + h * (ay1 + 2.0 * ay2 + 2.0 * ay3 + ay4) / 6.0)

    assert grip_needed(omega, r0, g) > mu, "the coin only slides when it needs more grip than it has"
    x, y = r0 * math.cos(theta0), r0 * math.sin(theta0)
    vx, vy = -omega * y, omega * x
    ts, xs, ys, vxs, vys = [0.0], [x], [y], [vx], [vy]
    n = 0
    rel_min = math.inf
    while True:
        xn, yn, vxn, vyn = step(x, y, vx, vy, dt)
        if math.hypot(xn, yn) >= R:
            lo, hi = 0.0, dt
            for _ in range(80):
                mid = 0.5 * (lo + hi)
                xm, ym, _, _ = step(x, y, vx, vy, mid)
                if math.hypot(xm, ym) < R:
                    lo = mid
                else:
                    hi = mid
            xh, yh, vxh, vyh = step(x, y, vx, vy, hi)
            t_off = n * dt + hi
            ts.append(t_off)
            xs.append(xh)
            ys.append(yh)
            vxs.append(vxh)
            vys.append(vyh)
            n += 1
            break
        n += 1
        x, y, vx, vy = xn, yn, vxn, vyn
        rel_min = min(rel_min, math.hypot(vx + omega * y, vy - omega * x))
        ts.append(n * dt)
        xs.append(x)
        ys.append(y)
        vxs.append(vx)
        vys.append(vy)
    speed = math.hypot(vxh, vyh)
    rel = math.hypot(vxh + omega * yh, vyh - omega * xh)
    # The angle round the centre, unwrapped along the path (a slow coin can go more than half a turn).
    ang_pos = math.degrees(float(np.unwrap(np.arctan2(np.array(ys), np.array(xs)))[-1]) - theta0)
    ang_vel = math.degrees(math.atan2(vyh, vxh))
    ang_vel_rel = (math.degrees(math.atan2(vyh, vxh) - theta0) + 180.0) % 360.0 - 180.0
    turn = math.degrees(omega * t_off)
    skid_d = speed * speed / (2.0 * mu * g)
    skid_t = speed / (mu * g)
    return {"static": False, "t": np.array(ts), "x": np.array(xs), "y": np.array(ys), "vx": np.array(vxs),
            "vy": np.array(vys), "t_off": t_off, "p_off": (xh, yh), "v_off": (vxh, vyh), "speed_off": speed,
            "rel_off": rel, "ang_pos": ang_pos, "ang_vel": ang_vel, "ang_vel_rel": ang_vel_rel, "turn": turn,
            "lag": turn - ang_pos, "skid_d": skid_d, "skid_t": skid_t, "t_rest": t_off + skid_t, "steps": n,
            "rel_min": rel_min, "omega": omega, "theta0": theta0, "r0": r0, "mu": mu, "g": g, "R": R, "dt": dt}


def state_at(run: dict, rt: float) -> dict:
    """Position and velocity (metres, m/s, the physics frame: x right, y up, the record turning
    counterclockwise) and the phase of the coin rt real seconds after the release."""
    r0, om, th0 = run["r0"], run["omega"], run["theta0"]
    if rt < 0.0 or run["static"]:
        a = th0 + om * rt
        return {"p": (r0 * math.cos(a), r0 * math.sin(a)), "v": (-om * r0 * math.sin(a), om * r0 * math.cos(a)),
                "phase": HELD if rt < 0.0 else RIDE}
    if rt < run["t_off"]:
        return {"p": (float(np.interp(rt, run["t"], run["x"])), float(np.interp(rt, run["t"], run["y"]))),
                "v": (float(np.interp(rt, run["t"], run["vx"])), float(np.interp(rt, run["t"], run["vy"]))),
                "phase": SLIDE}
    d = rt - run["t_off"]
    sp = run["speed_off"]
    ux, uy = run["v_off"][0] / sp, run["v_off"][1] / sp
    mug = run["mu"] * run["g"]
    if d < run["skid_t"]:
        s, v = sp * d - 0.5 * mug * d * d, sp - mug * d
        ph = SKIDS
    else:
        s, v = run["skid_d"], 0.0
        ph = REST
    return {"p": (run["p_off"][0] + ux * s, run["p_off"][1] + uy * s), "v": (ux * v, uy * v), "phase": ph}


def trail_points(run: dict, step_s: float) -> np.ndarray:
    """The slide path in the record's frame (fixed at the release): rows (t, x_rec, y_rec)."""
    ts = np.arange(0.0, run["t_off"], step_s)
    ts = np.append(ts, run["t_off"])
    out = np.empty((len(ts), 3))
    for i, t in enumerate(ts):
        x, y = float(np.interp(t, run["t"], run["x"])), float(np.interp(t, run["t"], run["y"]))
        xr, yr = rot(x, y, -run["omega"] * t)
        out[i] = (t, xr, yr)
    return out


def measure(man: dict) -> dict:
    g, mu, r0, R = man["g"], man["mu"], man["coin_radius_m"], man["record_radius_m"]
    dt = man["dt_s"]
    S, P, D, fps, F, pa = man["slow"], man["cycle_s"], man["scene_duration"], man["fps"], man["reset_fade"], man["release_at"]
    cycles = D / P
    assert abs(cycles - round(cycles)) < 1e-9, "the cycle must divide the scene length"
    for key in ("cycle_s", "release_at", "first_cycle_at", "reset_fade"):
        assert abs(man[key] * fps - round(man[key] * fps)) < 1e-9, f"{key} must be a whole number of frames"
    ppm = man["px_per_m"]
    rpm = man["rpm"]
    om = {m: rpm_to_omega(rpm[m]) for m in PANELS}
    coin_px = man["coin_diameter_m"] * ppm
    print(f"setup: the same record in both panels, seen from above: a {2 * R * 100:g} cm record (radius {R * 100:g} cm) "
          f"turns at a steady speed, clockwise as seen from above, flush with a still deck around it (a lazy susan: the "
          f"deck beyond the rim does not turn); a coin (a point mass for the physics, drawn {man['coin_diameter_m'] * 100:g} "
          f"cm across; its mass cancels) sits {r0 * 100:g} cm from the centre, held down by a fingertip so it moves with "
          f"the record; at the release the fingertip lifts and friction alone must hold the coin; friction mu = {mu:g} "
          f"between the coin and the record and the same on the deck, the same at rest and sliding (a chosen value for a "
          f"coin on vinyl; the limit scales with sqrt(mu)); g = {g:g} m/s^2; top panel {rpm['top']:g} rpm (omega = "
          f"{om['top']:.4f} rad/s), bottom panel {rpm['bottom']:g} rpm (omega = {om['bottom']:.4f} rad/s); the slide "
          f"integrated in the deck frame by RK4 at dt = {dt:.0e} s (friction mu g opposite to the coin's velocity relative "
          f"to the record surface under it, toward the centre at the release when that velocity is zero) with the rim "
          f"crossing located by bisection inside the step and checked by a half-step rerun; past the rim a straight skid "
          f"on the still deck at mu g; shown at 1/{S:g} speed on a {P:g} s cycle ({P * fps:.0f} frames) with the release "
          f"{pa:g} s into the cycle, {cycles:.0f} cycles in {D:g} s; drawn at {ppm:g} px per metre (the record "
          f"{2 * R * ppm:.0f} px across, the coin {coin_px:.1f} px); deterministic, no seed")
    om_star = limit_omega(mu, g, r0)
    print(f"limit: the coin rides along while the grip it needs, omega^2 r / g, is at most mu = {mu:g}; at r = {r0 * 100:g} "
          f"cm the limit is omega* = sqrt(mu g / r) = {om_star:.4f} rad/s = {omega_to_rpm(om_star):.2f} rpm; a speed omega "
          f"holds a coin out to r = mu g / omega^2")
    need = {m: grip_needed(om[m], r0, g) for m in PANELS}
    hold_r = {m: holds_out_to(om[m], mu, g) for m in PANELS}
    # Top panel: the static test.
    m = "top"
    print(f"{rpm[m]:g} rpm (top panel): omega = {om[m]:.4f} rad/s, the coin needs omega^2 r / g = {need[m]:.4f} of grip "
          f"against {mu:.2f} available, margin {mu - need[m]:.4f}: it stays and rides round with the record (its velocity "
          f"relative to the record stays zero; no integration needed); {rpm[m]:g} rpm holds a coin out to mu g / omega^2 = "
          f"{hold_r[m] * 100:.2f} cm; it needs {omega_to_rpm(om_star):.2f} rpm to move a coin at {r0 * 100:g} cm, "
          f"{omega_to_rpm(om_star) - rpm[m]:.2f} rpm more")
    assert need[m] <= mu and hold_r[m] > r0
    # Bottom panel: the slide, from angle 0 for the reference and from the drawn start angle.
    m = "bottom"
    ref = rk4_slide(om[m], mu, g, r0, R, dt, 0.0)
    theta0 = -math.radians(ref["ang_vel"])
    run = rk4_slide(om[m], mu, g, r0, R, dt, theta0)
    half = rk4_slide(om[m], mu, g, r0, R, 0.5 * dt, theta0)
    a0 = om[m] ** 2 * r0 - mu * g
    t10 = man["table_step_s"]
    r10 = math.hypot(float(np.interp(t10, run["t"], run["x"])), float(np.interp(t10, run["t"], run["y"])))
    print(f"{rpm[m]:g} rpm (bottom panel): omega = {om[m]:.4f} rad/s, the coin needs omega^2 r / g = {need[m]:.4f} of grip "
          f"against {mu:.2f} available, {need[m] / mu:.2f} times what it has: it slides; {rpm[m]:g} rpm would hold a coin "
          f"only out to mu g / omega^2 = {hold_r[m] * 100:.2f} cm (inside the label); RK4 from the release: the coin's "
          f"radius reaches the rim R = {R * 100:g} cm at {run['t_off']:.4f} s, {run['ang_pos']:.1f} degrees round the "
          f"centre in the deck frame from where it started, moving at {run['speed_off']:.4f} m/s = {run['speed_off']:.2f} "
          f"m/s ({run['rel_off']:.3f} m/s relative to the record surface) while the record turned omega t = "
          f"{run['turn']:.1f} degrees, so the coin lags the record by {run['lag']:.1f} degrees at the rim; its velocity "
          f"points {run['ang_vel_rel']:.1f} degrees from its starting radius (counterclockwise in the frame where the "
          f"record turns counterclockwise) and {run['ang_vel_rel'] - run['ang_pos']:.1f} degrees outward of the tangent "
          f"direction's radius; that is under one fifth of a second ({run['t_off']:.4f} < 0.2000 s); {run['steps']} "
          f"steps; the relative speed after the first step stays above {run['rel_min']:.2e} m/s (the friction direction "
          f"is defined); half-step rerun (dt = {0.5 * dt:.0e} s): off at {half['t_off']:.7f} s ({half['t_off'] - run['t_off']:+.1e} "
          f"s), {half['ang_pos']:.4f} degrees round, {half['speed_off']:.6f} m/s ({half['speed_off'] - run['speed_off']:+.1e} "
          f"m/s); reference run from angle 0: off at {ref['t_off']:.7f} s ({ref['t_off'] - run['t_off']:+.1e} s), "
          f"{ref['ang_pos']:.4f} degrees round; start check: in the record's frame the coin starts outward at omega^2 r "
          f"- mu g = {a0:.4f} m/s^2, so after {t10 * 1000:.0f} ms it is {0.5 * a0 * t10 * t10 * 100:.4f} cm out; RK4 gives "
          f"{(r10 - r0) * 100:.4f} cm")
    assert need[m] > mu and hold_r[m] < r0
    assert abs(half["t_off"] - run["t_off"]) < 1e-4, "the half-step rerun disagrees on the exit time"
    assert abs(ref["t_off"] - run["t_off"]) < 1e-9 and abs(ref["ang_pos"] - run["ang_pos"]) < 1e-6
    assert run["t_off"] < 0.2
    rows = []
    t = 0.0
    while t < run["t_off"] - 1e-9:
        x, y = float(np.interp(t, run["t"], run["x"])), float(np.interp(t, run["t"], run["y"]))
        vx, vy = float(np.interp(t, run["t"], run["vx"])), float(np.interp(t, run["t"], run["vy"]))
        ang = (math.degrees(math.atan2(y, x) - theta0) + 180.0) % 360.0 - 180.0
        rows.append(f"{t * 1000:.0f} ms r {math.hypot(x, y) * 100:.2f} cm, {ang:.1f} deg, {math.hypot(vx, vy):.3f} m/s")
        t += t10
    rows.append(f"{run['t_off'] * 1000:.1f} ms r {R * 100:.2f} cm, {run['ang_pos']:.1f} deg, {run['speed_off']:.3f} m/s")
    print(f"slide table ({rpm[m]:g} rpm, time after the release, radius, angle round the centre in the deck frame from the "
          f"start, speed in the deck frame): " + "; ".join(rows))
    print(f"skid ({rpm[m]:g} rpm): past the rim the coin skids straight on the still deck from {run['speed_off']:.4f} m/s "
          f"at mu g = {mu * g:.3f} m/s^2: v^2 / (2 mu g) = {run['skid_d'] * 100:.1f} cm = {run['skid_d'] * 100:.2f} cm in "
          f"v / (mu g) = {run['skid_t']:.3f} s; the coin is at rest {run['t_rest']:.3f} s after the release, "
          f"{run['skid_d'] * 100 + R * 100:.1f} cm from the record's centre")
    # The drawn start angle: the exit velocity along +x (to the right on screen).
    print(f"start angle: the drawn coin starts at {math.degrees(theta0):.1f} degrees (the physics frame, counterclockwise "
          f"from +x; the screen mirrors y so the record turns clockwise), so its exit velocity points {run['ang_vel']:.6f} "
          f"degrees from +x (to the right) and the skid runs straight right from the rim point at {math.degrees(math.atan2(run['p_off'][1], run['p_off'][0])):.1f} "
          f"degrees; the top coin starts at the same angle and rides round")
    assert abs(run["ang_vel"]) < 1e-6
    ev: dict = {"om": om, "need": need, "hold_r": hold_r, "om_star": om_star, "rpm_star": omega_to_rpm(om_star),
                "runs": {"top": static_run(om["top"], theta0, r0, mu, g, R), "bottom": run}, "theta0": theta0}
    # For the description: other speeds.
    descr = []
    ev["others"] = {}
    for rpm_s in man["description_rpm_static"]:
        w = rpm_to_omega(rpm_s)
        ev["others"][rpm_s] = {"need": grip_needed(w, r0, g), "hold_r": holds_out_to(w, mu, g)}
        label = "33 1/3" if abs(rpm_s - 100.0 / 3.0) < 1e-6 else f"{rpm_s:g}"
        descr.append(f"{label} rpm ({rpm_s:.4f}; omega {w:.4f} rad/s) needs {grip_needed(w, r0, g):.4f} of grip and holds "
                     f"a coin out to {holds_out_to(w, mu, g) * 100:.2f} cm")
    for rpm_s in man["description_rpm_slide"]:
        w = rpm_to_omega(rpm_s)
        r_s = rk4_slide(w, mu, g, r0, R, dt, 0.0)
        ev["others"][rpm_s] = {"need": grip_needed(w, r0, g), "run": r_s}
        descr.append(f"{rpm_s:g} rpm (omega {w:.4f} rad/s) needs {grip_needed(w, r0, g):.4f}: off the rim at {r_s['t_off']:.4f} s, "
                     f"{r_s['ang_pos']:.1f} degrees round, at {r_s['speed_off']:.4f} m/s while the record turned "
                     f"{r_s['turn']:.1f} degrees; skid {r_s['skid_d'] * 100:.1f} cm in {r_s['skid_t']:.3f} s, at rest "
                     f"{r_s['t_rest']:.3f} s after the release")
    om_hold = limit_omega(mu, g, R)
    descr.append(f"a coin at the rim itself ({R * 100:g} cm) slides above sqrt(mu g / R) = {omega_to_rpm(om_hold):.2f} rpm")
    for mu2 in man["description_mus"]:
        w2 = limit_omega(mu2, g, r0)
        descr.append(f"grip {mu2:g} at {r0 * 100:g} cm: the limit is {omega_to_rpm(w2):.2f} rpm ({rpm['top']:g} rpm "
                     f"{'holds' if grip_needed(om['top'], r0, g) <= mu2 else 'slides'}, {rpm['bottom']:g} rpm "
                     f"{'holds' if grip_needed(om['bottom'], r0, g) <= mu2 else 'slides'})")
    print("for the description: " + "; ".join(descr))
    # The schedule in video time.
    t0 = man["first_cycle_at"]
    k0 = math.ceil((0.0 - t0) / P - 1e-9) - 1
    k1 = math.floor((D - t0) / P - 1e-9)
    starts = [t0 + kk * P for kk in range(k0, k1 + 1)]
    ev["cycles"] = int(round(cycles))

    def lst(off_: float) -> str:
        return ", ".join(f"{st + off_:.2f}" for st in starts if 0.0 <= st + off_ < D)

    vt = lambda real: pa + real * S   # noqa: E731  video time after the cycle start
    rest_v = vt(run["t_rest"])
    assert rest_v < P - F, "the skidding coin is still moving at the reset fade"
    tau0 = (0.0 - t0) % P
    rt0 = (tau0 - pa) / S
    turn_cycle = {m: om[m] * P / S for m in PANELS}
    print(f"schedule (video time, 1/{S:g} speed): cycles of {P:g} s start at " + ", ".join(f"{st:.2f}" for st in starts)
          + f" s (the first {-t0:.2f} s before the first frame); the fingertip lifts {pa:g} s into each cycle at {lst(pa)} s "
          f"(over {man['finger_lift_s']:g} s); the {rpm['bottom']:g} rpm coin crosses the rim {S * run['t_off']:.2f} s after "
          f"the release at {lst(vt(run['t_off']))} s ({vt(run['t_off']):.2f} s into the cycle; the event row lights) and is "
          f"at rest on the deck at {lst(rest_v)} s ({rest_v:.2f} s into the cycle, before the fade at {P - F:.2f} s); the "
          f"{rpm['top']:g} rpm coin rides round and its event row lights {man['hold_event_after_s']:g} s after the release "
          f"at {lst(pa + man['hold_event_after_s'])} s; the record turns {math.degrees(om['top']) / S:.1f} "
          f"and {math.degrees(om['bottom']) / S:.1f} degrees per second of video ({omega_to_rpm(om['top']) / S:.2f} and "
          f"{omega_to_rpm(om['bottom']) / S:.2f} turns a minute on screen) and {math.degrees(turn_cycle['top']):.0f} and "
          f"{math.degrees(turn_cycle['bottom']):.0f} degrees per cycle, so the label marker jumps under the crossfade (the "
          f"grooves are symmetric and do not); the reset crossfade runs over the last {F:g} s of each cycle (from "
          f"{lst(P - F)} s; the readouts out over its first half and in over its second); on the first frame the cycle is "
          f"{tau0:.2f} s in ({rt0:.3f} s real: both coins held); title until {man['title_until']:g} s; payoff card from "
          f"{man['payoff_t']:g} s; the title fades back in over the last {man['loop_fade']:g} s and the last frame repeats "
          f"the first (the scene is periodic: {D:g} s holds exactly {cycles:.0f} cycles)")
    # Text widths.
    font = os.environ["SEED_ZERO_FONT"]
    f28, f34, f40, f56 = (ImageFont.truetype(font, n) for n in (28, 34, 40, 56))
    widths = {"overlay@34": (f34, man["overlay"])}
    for j, line in enumerate(man["title"].split("|")):
        widths[f"title line {j + 1}@56"] = (f56, line)
    widths["legend@40"] = (f40, legend_text(man))
    widths["clock@28"] = (f28, clock_text(run["t_off"]))
    widths["clock held@28"] = (f28, clock_text(-1.0))
    for m in PANELS:
        widths[f"label {m}@40"] = (f40, label_text(man, m))
        widths[f"sublabel {m}@28"] = (f28, sub_text(man))
        widths[f"readout {m}@28"] = (f28, need_text(ev, m))
        widths[f"event {m}@40"] = (f40, event_text(ev, m))
    for ph in (HELD, RIDE, SLIDE, SKIDS, REST):
        widths[f"state {ph}@28"] = (f28, state_text(ph))
    for j, line in enumerate(payoff_lines(man, ev)):
        widths[f"payoff line {j + 1}@40"] = (f40, line)
    print("text widths (the on-screen strings verbatim): " + ", ".join(f"{kk} {f.getlength(s):.0f} px '{s}'"
                                                                       for kk, (f, s) in widths.items()))
    assert all(f.getlength(s) < 950 for f, s in widths.values()), "a text line is wider than 950 px"
    assert len(payoff_lines(man, ev)) <= 6, "the card has more than six lines"
    # Layout checks: the record inside the slab, the coins and the skid clear of every text row.
    cx, cy = man["record_centre_px"]
    Rpx, r0px, cr = R * ppm, r0 * ppm, 0.5 * coin_px
    left = ROW_X0 + max(f40.getlength(label_text(man, m)) for m in PANELS)
    left2 = ROW_X0 + f28.getlength(sub_text(man))
    right = ROW_X1 - max(f28.getlength(state_text(ph)) for ph in (HELD, RIDE, SLIDE, SKIDS, REST))
    right2 = ROW_X1 - max(f28.getlength(need_text(ev, m)) for m in PANELS)
    rows_bottom = SUB_DY + 14
    ev_w = max(f40.getlength(event_text(ev, m)) for m in PANELS)
    ev_x0, ev_x1 = W / 2.0 - ev_w / 2.0, W / 2.0 + ev_w / 2.0
    # The bottom coin's path on screen (band-local px): the slide table, the skid and the rest.
    pts = []
    for t in np.append(run["t"][:: max(1, len(run["t"]) // 2000)], run["t_off"]):
        st = state_at(run, float(t))
        pts.append((cx + st["p"][0] * ppm, cy + st["p"][1] * ppm))
    for t in np.linspace(run["t_off"], run["t_rest"], 200):
        st = state_at(run, float(t))
        pts.append((cx + st["p"][0] * ppm, cy + st["p"][1] * ppm))
    xs_ = [p[0] for p in pts]
    ys_ = [p[1] for p in pts]
    path_x0, path_x1 = min(xs_) - cr, max(xs_) + cr
    path_y0, path_y1 = min(ys_) - cr, max(ys_) + cr
    rest = state_at(run, run["t_rest"])
    rest_px = (cx + rest["p"][0] * ppm, cy + rest["p"][1] * ppm)
    off_px = (cx + run["p_off"][0] * ppm, cy + run["p_off"][1] * ppm)
    pad = cr * FINGER_SCALE * 1.25 * 1.12 + math.hypot(FINGER_DX, FINGER_DY)   # the lifted pad's farthest reach
    ride_y0, ride_y1 = cy - r0px - pad, cy + r0px + pad
    print(f"row check: the label row ends at x {left:.0f} px and the state word starts at x {right:.0f} px; the second row's "
          f"sublabel ends at x {left2:.0f} px and the grip readout starts at x {right2:.0f} px; the rows end {rows_bottom} px "
          f"under the band top; the deck slab spans x {SLAB_X0} to {SLAB_X1} and {SLAB_Y0} to {SLAB_Y1} px under the band "
          f"top; the record ({2 * Rpx:.0f} px) is centred at x {cx} and {cy} px under the band top, so it spans "
          f"{cy - Rpx:.0f} to {cy + Rpx:.0f} px and x {cx - Rpx:.0f} to {cx + Rpx:.0f}; the riding coin (fingertip pad "
          f"included) stays between {ride_y0:.0f} and {ride_y1:.0f} px; the {rpm['bottom']:g} rpm coin leaves the rim at "
          f"x {off_px[0]:.0f}, {off_px[1]:.0f} px under the band top, skids right and rests at x {rest_px[0]:.0f}; its whole "
          f"path (coin radius {cr:.1f} px included) spans x {path_x0:.0f} to {path_x1:.0f} and {path_y0:.0f} to "
          f"{path_y1:.0f} px under the band top; the event row spans {EVENT_DY - 22} to {EVENT_DY + 22} px under the band "
          f"top and x {ev_x0:.0f} to {ev_x1:.0f} px (widest {ev_w:.0f} px, centred on {W // 2}); each band is {BAND_H} px "
          f"tall (y {BAND_Y['top']} to {BAND_Y['top'] + BAND_H} and {BAND_Y['bottom']} to {BAND_Y['bottom'] + BAND_H}); the "
          f"caption band starts at y {int(man['caption_y'] * H)}; the title rows end at y {252 + 28} and the overlay band "
          f"ends at y 130")
    assert right - left > 40 and right2 - left2 > 40, "the columns meet"
    assert cy - Rpx > SLAB_Y0 + 4 and cy + Rpx < SLAB_Y1 - 4, "the record leaves the slab"
    assert SLAB_Y0 > rows_bottom + 6, "the slab meets the text rows"
    assert SLAB_Y1 < EVENT_DY - 22 - 2, "the slab meets the event row"
    assert ride_y0 > rows_bottom + 10 and ride_y1 < EVENT_DY - 22 - 10, "the riding coin meets a text row"
    assert path_y0 > rows_bottom + 10 and path_y1 < EVENT_DY - 22 - 10, "the sliding coin meets a text row"
    assert path_x0 > 8 and path_x1 < W - 8, "the coin leaves the band sideways"
    assert BAND_Y["bottom"] + BAND_H <= int(man["caption_y"] * H), "the bottom band reaches the caption band"
    assert PAYOFF_Y - 20 > int(man["caption_y"] * H) + 90, "the card meets the caption band"
    return ev


def legend_text(man: dict) -> str:
    return f"same coin, same grip, 1/{man['slow']:g} speed"


def clock_text(r: float) -> str:
    return "held" if r < 0.0 else f"{r:.3f} s after the release"


def label_text(man: dict, m: str) -> str:
    return f"{man['rpm'][m]:g} turns a minute"


def sub_text(man: dict) -> str:
    return f"coin {man['coin_radius_m'] * 100:g} cm from the centre, grip {man['mu']:.2f}"


def need_text(ev: dict, m: str) -> str:
    return f"needs {ev['need'][m]:.2f} of grip"


def state_text(ph: str) -> str:
    return {HELD: "held", RIDE: "rides round", SLIDE: "sliding", SKIDS: "off the record, skidding",
            REST: "at rest on the deck"}[ph]


def event_text(ev: dict, m: str) -> str:
    if m == "top":
        return f"stays on: needs {ev['need'][m]:.2f}, has {ev['runs'][m]['mu']:.2f}"
    return f"off the record in {ev['runs'][m]['t_off']:.2f} s"


def payoff_lines(man: dict, ev: dict) -> list[str]:
    o = ev["others"]
    third = [k for k in o if abs(k - 100.0 / 3.0) < 1e-6][0]
    text = man["payoff_text"].format(
        need45=ev["need"]["top"], need78=ev["need"]["bottom"], mu=man["mu"], t_off=ev["runs"]["bottom"]["t_off"],
        rpm_star=ev["rpm_star"], r45=ev["hold_r"]["top"] * 100.0, r78=ev["hold_r"]["bottom"] * 100.0,
        r33=o[third]["hold_r"] * 100.0)
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
        self.S = man["slow"]
        self.P = man["cycle_s"]
        self.P_f = int(round(man["cycle_s"] * self.fps))
        self.c0_f = int(round(man["first_cycle_at"] * self.fps))
        self.pa, self.F = man["release_at"], man["reset_fade"]
        self.runs = ev["runs"]
        self.cx, self.cy = (float(v) for v in man["record_centre_px"])
        self.R = man["record_radius_m"] * self.ppm
        self.cr = 0.5 * man["coin_diameter_m"] * self.ppm
        self.trail = trail_points(self.runs["bottom"], man["trail_step_s"])

    def phase(self, f: int) -> tuple[int, float]:
        k, tau_f = divmod(f - self.c0_f, self.P_f)
        return k, tau_f / self.fps

    @staticmethod
    def L_(x: float, y: float) -> tuple[float, float]:
        """Layer (2x) pixel of a band-local point, rounded to 1e-4 px so equal states draw equal pixels."""
        return round(x * SS, 4), round(y * SS, 4)

    def px(self, x: float, y: float) -> tuple[float, float]:
        """Band-local pixel of a physics point (metres): y mirrored, so the record turns clockwise."""
        return self.cx + x * self.ppm, self.cy + y * self.ppm

    def draw_deck(self, d: ImageDraw.ImageDraw) -> None:
        s0, s1 = self.L_(SLAB_X0, SLAB_Y0), self.L_(SLAB_X1, SLAB_Y1)
        d.rounded_rectangle((s0[0], s0[1], s1[0], s1[1]), radius=10 * SS, fill=DECK, outline=DECK_EDGE, width=2 * SS)

    def draw_record(self, d: ImageDraw.ImageDraw, phi: float) -> None:
        """The vinyl with symmetric grooves, the rim, the label with one marker at angle phi, the spindle."""
        cx, cy, R = self.cx, self.cy, self.R
        p0, p1 = self.L_(cx - R, cy - R), self.L_(cx + R, cy + R)
        d.ellipse((p0[0], p0[1], p1[0], p1[1]), fill=VINYL, outline=RIM, width=3 * SS)
        for gfrac in np.linspace(0.42, 0.965, 16):
            rr = R * gfrac
            q0, q1 = self.L_(cx - rr, cy - rr), self.L_(cx + rr, cy + rr)
            d.ellipse((q0[0], q0[1], q1[0], q1[1]), outline=GROOVE, width=1 * SS)

    def draw_label(self, d: ImageDraw.ImageDraw, phi: float) -> None:
        cx, cy, R = self.cx, self.cy, self.R
        rl = R * 0.33
        q0, q1 = self.L_(cx - rl, cy - rl), self.L_(cx + rl, cy + rl)
        d.ellipse((q0[0], q0[1], q1[0], q1[1]), fill=LABEL)
        mx, my = cx + rl * 0.66 * math.cos(phi), cy + rl * 0.66 * math.sin(phi)
        m0, m1 = self.L_(mx - 9, my - 9), self.L_(mx + 9, my + 9)
        d.ellipse((m0[0], m0[1], m1[0], m1[1]), fill=LABEL_MARK)
        l0 = self.L_(cx + rl * 0.22 * math.cos(phi), cy + rl * 0.22 * math.sin(phi))
        l1 = self.L_(cx + rl * 0.5 * math.cos(phi), cy + rl * 0.5 * math.sin(phi))
        d.line((*l0, *l1), fill=LABEL_MARK, width=3 * SS)
        s0, s1 = self.L_(cx - 6, cy - 6), self.L_(cx + 6, cy + 6)
        d.ellipse((s0[0], s0[1], s1[0], s1[1]), fill=SPINDLE)

    def draw_trail(self, d: ImageDraw.ImageDraw, rt: float) -> None:
        """The slip path on the vinyl, turning with the record, up to the coin or the rim point."""
        run = self.runs["bottom"]
        if rt <= 0.0:
            return
        tr = self.trail[self.trail[:, 0] <= min(rt, run["t_off"]) + 1e-12]
        a = run["omega"] * rt
        pts = [self.L_(*self.px(*rot(x, y, a))) for _, x, y in tr]
        if rt < run["t_off"]:
            pts.append(self.L_(*self.px(*state_at(run, rt)["p"])))
        if len(pts) >= 2:
            d.line(pts, fill=blend(CORAL, 0.85, VINYL), width=4 * SS, joint="curve")

    def draw_skid(self, d: ImageDraw.ImageDraw, rt: float) -> None:
        run = self.runs["bottom"]
        if rt <= run["t_off"]:
            return
        p0 = self.L_(*self.px(*run["p_off"]))
        p1 = self.L_(*self.px(*state_at(run, rt)["p"]))
        d.line((*p0, *p1), fill=blend(SKID, 0.8, DECK), width=3 * SS)

    def draw_coin(self, d: ImageDraw.ImageDraw, X: float, Y: float) -> None:
        r = self.cr
        c0, c1 = self.L_(X - r, Y - r), self.L_(X + r, Y + r)
        d.ellipse((c0[0], c0[1], c1[0], c1[1]), fill=COIN, outline=COIN_EDGE, width=2 * SS)
        ri = r * 0.68
        i0, i1 = self.L_(X - ri, Y - ri), self.L_(X + ri, Y + ri)
        d.ellipse((i0[0], i0[1], i1[0], i1[1]), outline=COIN_RING, width=1 * SS)

    def draw_finger(self, d: ImageDraw.ImageDraw, X: float, Y: float, tv: float) -> None:
        """The fingertip pad over the coin; from the release it lifts: grows a little and fades out."""
        lift = 0.0 if tv < 0.0 else min(1.0, tv / self.man["finger_lift_s"])
        if lift >= 1.0:
            return
        a = 1.0 - lift
        r = self.cr * FINGER_SCALE * (1.0 + 0.25 * lift)
        # The pad sits a little up and left of the coin's centre, so a sliver of the coin shows.
        X, Y = X + FINGER_DX, Y + FINGER_DY
        f0, f1 = self.L_(X - r, Y - r * 1.12), self.L_(X + r, Y + r * 1.12)
        d.ellipse((f0[0], f0[1], f1[0], f1[1]), fill=blend(FINGER, a, VINYL),
                  outline=blend(FINGER_DARK, a, VINYL), width=2 * SS)
        ri = r * 0.55
        h0, h1 = self.L_(X - ri, Y - ri * 0.8 - r * 0.2), self.L_(X + ri, Y + ri * 0.8 - r * 0.2)
        d.ellipse((h0[0], h0[1], h1[0], h1[1]), outline=blend(FINGER_DARK, 0.7 * a, FINGER), width=1 * SS)

    def scene(self, m: str, tau: float) -> tuple[Image.Image, dict]:
        """The band layer of panel m at tau seconds into a cycle (the held setup before the release)."""
        layer = Image.new("RGB", (W * SS, BAND_H * SS), BG)
        d = ImageDraw.Draw(layer)
        run = self.runs[m]
        tv = tau - self.pa
        rt = tv / self.S
        phi = run["omega"] * tau / self.S          # the record's angle, from the cycle time
        self.draw_deck(d)
        if m == "bottom":
            self.draw_skid(d, rt)
        self.draw_record(d, phi)
        if m == "bottom":
            self.draw_trail(d, rt)
        self.draw_label(d, phi)
        st = state_at(run, rt)
        X, Y = self.px(*st["p"])
        self.draw_coin(d, X, Y)
        if tv < self.man["finger_lift_s"]:
            rel = state_at(run, 0.0) if tv >= 0.0 else st
            self.draw_finger(d, *self.px(*rel["p"]), tv)
        st["tv"], st["rt"] = tv, rt
        return layer, st

    def draw_panel(self, m: str, f: int) -> tuple[Image.Image, dict]:
        k, tau = self.phase(f)
        P, F = self.P, self.F
        layer, st = self.scene(m, tau)
        st["alpha"], st["k"] = 1.0, k
        if tau >= P - F:
            # Crossfade to the next cycle's held setup (the skidding coin is at rest by now, asserted
            # in measure; the record's marker and the riding coin jump with the cycle time).
            a = (tau - (P - F)) / F
            new, st_new = self.scene(m, tau - P)
            layer = Image.blend(layer, new, a)
            st["alpha"] = max(0.0, 1.0 - 2.0 * a)
            st_new["alpha"], st_new["k"] = max(0.0, 2.0 * a - 1.0), k + 1
            if a >= 0.5:
                st = st_new
        return layer, st

    def draw_text(self, d: ImageDraw.ImageDraw, states: dict, hud_alpha: float) -> None:
        man, ev = self.man, self.ev
        for m, st in states.items():
            y0 = BAND_Y[m]
            a, ph = st["alpha"], st["phase"]
            released = st["tv"] >= 0.0
            d.text((ROW_X0, y0 + LABEL_DY), label_text(man, m), font=self.font, fill=COLOUR[m], anchor="lm")
            d.text((ROW_X0, y0 + SUB_DY), sub_text(man), font=self.font_small, fill=MUTED, anchor="lm")
            lit = (m == "top" and st["tv"] >= man["hold_event_after_s"]) or (m == "bottom" and ph in (SKIDS, REST))
            d.text((ROW_X1, y0 + LABEL_DY + 2), state_text(ph), font=self.font_small,
                   fill=blend(GOLD if lit else MUTED, a), anchor="rm")
            d.text((ROW_X1, y0 + SUB_DY), need_text(ev, m), font=self.font_small,
                   fill=blend(GOLD if released else TEXT, a), anchor="rm")
            if lit:
                d.text((W / 2, y0 + EVENT_DY), event_text(ev, m), font=self.font, fill=blend(GOLD, a), anchor="mm")
        if hud_alpha > 0.02:
            d.text((W / 2, LEGEND_Y), legend_text(man), font=self.font, fill=blend(TEXT, hud_alpha), anchor="mm")
            d.text((W / 2, CLOCK_Y), clock_text(states["top"]["rt"]), font=self.font_small,
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
        for m in PANELS:
            layer, states[m] = self.draw_panel(m, f)
            img.paste(layer.reduce(SS), (0, BAND_Y[m]))
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
    man = json.loads((ROOT / "projects/coinrecord/manifest.json").read_text())
    ev = measure(man)
    if "--measure-only" in sys.argv:
        return
    if "--frames" in sys.argv:
        times = [float(v) for v in sys.argv[sys.argv.index("--frames") + 1].split(",")]
        r = Renderer(man, ev)
        (ROOT / "media/coinrecord").mkdir(parents=True, exist_ok=True)
        for tv in times:
            Image.fromarray(r.frame_at(int(round(tv * man["fps"])))).save(ROOT / f"media/coinrecord/smoke-{tv}.png")
        print("smoke frames: " + ", ".join(f"{tv}" for tv in times))
        return
    Renderer(man, ev).render(ROOT / "media/coinrecord/footage.mp4")


if __name__ == "__main__":
    main()
