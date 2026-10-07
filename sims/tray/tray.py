#!/usr/bin/env python3
"""Tilting tray: marble or dice, which one goes first?

Two bands on the same clock, the same tray drawn the same way at the same
scale, side view: a tray of length tray_len_m tilts from flat at a steady
rate w about its low edge (the pivot, which stays put). A solid marble of
radius R (I = k m R^2, k = 2/5; the mass cancels; no rolling resistance,
chosen) and a dice (a cube of side dice_side_m modelled as a sliding block
with grip mu, static equal to kinetic; a cube only tips above 45 degrees of
tilt, so it slides first and never tips) rest side by side with their
contact points start_m up the tray from the low edge. Top band, the slow
"no" case: the dice. Bottom band, the fast "yes" case: the marble.

The model, in the tray frame with x the distance up the tray from the pivot
(speed v = dx/dt, negative toward the edge), theta = w t:

    marble (rolls from the first instant; friction can only turn a ball)
        (1 + k) x'' = -g sin(theta) + w^2 x
        closed form without the frame terms: s = g (w t - sin w t) / ((1 + k) w^2)
    dice (sticks while the drive along the tray is within mu N, then slides)
        at rest: holds while g sin(theta) - w^2 x <= mu g cos(theta)
        sliding: x'' = -g sin(theta) + w^2 x + mu N,  N = g cos(theta) + 2 w x'

The + w^2 x term is the centrifugal push away from the pivot and the 2 w x'
term in N is the Coriolis part of the normal force: an object moving toward
the pivot (x' < 0) presses less on the tray (in the inertial frame the
tangential acceleration is 2 x' w, so N = m g cos(theta) + 2 m w x'). Both
bands are integrated by classical RK4 at steps_per_second in the tray frame
(position and speed; the marble's spin from v = omega R), with a stick-slip
start event for the dice (bisection on the time the drive beats the grip; it
never moves uphill), bisection inside the step for the edge arrival, a
half-step rerun, and the marble against its closed form; the drawing follows
the RK4 tables. After the edge each object falls freely in the room frame
(launched at its edge speed along the tray's direction). The run repeats
every cycle_s seconds of video in real time with a crossfade back to the
flat tray; the cycle divides the scene length, so the scene is exactly
periodic and the last frame equals the first. Deterministic, no seed.

Measured and printed: the edge times, tilts and speeds of both, the dice's
slide start against tan(theta) = mu, the margin, the no-slip condition for
the marble, its energy balance at the edge (the tray does work on it), the
table at table_step_s, the description variants (grips, tilt rates, other
rolling shapes, the marble's radius, the frame terms), the checks against
the brief, the schedule in video time, the on-screen text widths and the
layout clearances.

usage: tray.py [--measure-only] [--frames t1,t2,...]
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
RIM = (96, 108, 126)
PLANK = (54, 62, 76)
PLANK_EDGE = (150, 160, 176)
MARBLE = (222, 226, 234)
MARBLE_EDGE = (150, 158, 172)
STRIPE = (58, 66, 82)
DICE_FILL = (236, 240, 244)
DICE_EDGE = (120, 132, 150)
PIP = (40, 44, 52)

# Layout: overlay at y 96..130 (captions.py), three title rows at y 186/244/302
# for the first seconds, then the legend at y 236 and the shared clock at y 290;
# two bands stacked, the dice in y 330..880 and the marble in y 880..1430, each
# drawn at 2x in its own layer (so the falling object is clipped at its band);
# each band has its label row 40 px under the band top, its readout rows at 84
# and 120 (left column from x 40, right column to x 1040); the tray pivots at
# (pivot_x_px, pivot_dy) under the band top and rises on the left as it tilts;
# the gold event row at 490 under the band top, centred on x 400, under the
# raised part of the tray; captions at caption_y 0.75 (y 1440..1530); the
# six-line card from y 1572 at a 48 px pitch.
LEGEND_Y, CLOCK_Y = 236, 290
TITLE_Y = (186, 244, 302)
SS = 2
PAYOFF_Y, PAYOFF_PITCH = 1572.0, 48
PANELS = ("dice", "marble")
BAND_Y = {"dice": 330, "marble": 880}
BAND_H = 550
LABEL_DY, SUB_DY, FIX_DY = 40, 84, 120
ROWS_BOTTOM = FIX_DY + 16
EVENT_DY, EVENT_X = 490, 400
ROW_X0, ROW_X1 = 40, 1040
TRAY_T = 10.0            # the tray slab's thickness under its surface, px
STAND_H = 22.0           # the pivot stand under the low edge
ARC_R = 64.0             # the tilt arc at the pivot
FLAT_REF = 120.0         # the dashed flat reference line left of the pivot
TICK_R0, TICK_R1, TICK_LABEL_R = 40.0, 300.0, 240.0   # the slide-start tick along the 21.8 deg ray
TICK_LABEL_H = -60.0     # the label's offset below the ray
COLOUR = {"dice": CORAL, "marble": TEAL}
HELD, REST, MOVE, OFF = "held", "rest", "move", "off"


def blend(col, a: float, base=BG) -> tuple:
    a = max(0.0, min(1.0, a))
    return tuple(int(round(c * a + b * (1 - a))) for c, b in zip(col, base))


# --- measurement --------------------------------------------------------------
def closed_marble(g: float, w: float, k: float, L: float) -> tuple[float, float, float]:
    """(t, theta, speed) at the edge from s = g (w t - sin w t) / ((1 + k) w^2) = L (no frame terms)."""
    def s_of(t: float) -> float:
        return g * (w * t - math.sin(w * t)) / ((1.0 + k) * w * w)
    lo, hi = 0.0, 60.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if s_of(mid) < L:
            lo = mid
        else:
            hi = mid
    t = 0.5 * (lo + hi)
    return t, w * t, g * (1.0 - math.cos(w * t)) / ((1.0 + k) * w)


def slide_start(g: float, w: float, mu: float, L: float, frame: bool) -> float:
    """The time the drive along the tray first beats the grip with the block at rest at x = L:
    g sin(theta) - w^2 L > mu g cos(theta) (tan(theta) = mu without the centrifugal term)."""
    lo, hi = 0.0, 0.5 * math.pi / w
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if g * math.sin(w * mid) - (w * w * L if frame else 0.0) < mu * g * math.cos(w * mid):
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def integrate(g: float, w: float, L: float, k: float, mu: float | None, dt: float, frame: bool = True,
              cor_sign: float = 1.0) -> dict:
    """RK4 in the tray frame from rest at x = L until the edge (x = 0). mu None: a rolling body with
    inertia k (k = 0 is a frictionless slider). mu given: a sliding block that sticks until the drive
    beats the grip, then slides toward the edge. State (x, v, W) with W the work per kilogram done on
    the body by the tray's normal force, dW/dt = N x w. frame False drops the centrifugal and
    Coriolis terms; cor_sign -1 reverses the Coriolis term on N (the brief's convention, printed as a
    comparison only). The edge crossing is located by bisection inside the step."""
    rolling = mu is None
    cor = cor_sign * 2.0 * w if frame else 0.0
    cen = w * w if frame else 0.0

    def normal(t: float, v: float) -> float:
        return g * math.cos(w * t) + cor * v

    def rhs(t: float, y: tuple) -> tuple:
        x, v, _ = y
        th = w * t
        drive = -g * math.sin(th) + cen * x
        if rolling:
            a = drive / (1.0 + k)
        else:
            a = drive + mu * normal(t, v)      # sliding toward the pivot: friction acts up the tray
        return v, a, (g * math.cos(th) + 2.0 * w * v) * x * w

    def step(t: float, y: tuple, h: float) -> tuple:
        k1 = rhs(t, y)
        k2 = rhs(t + 0.5 * h, tuple(a + 0.5 * h * b for a, b in zip(y, k1)))
        k3 = rhs(t + 0.5 * h, tuple(a + 0.5 * h * b for a, b in zip(y, k2)))
        k4 = rhs(t + h, tuple(a + h * b for a, b in zip(y, k3)))
        return tuple(a + h * (b + 2.0 * c + 2.0 * d + e) / 6.0 for a, b, c, d, e in zip(y, k1, k2, k3, k4))

    t0 = 0.0 if rolling else slide_start(g, w, mu, L, frame)
    t, y, n = t0, (L, 0.0, 0.0), 0
    ts, xs, vs = [t0], [L], [0.0]
    n_min = normal(t0, 0.0) / g
    up_v, up_x, up_t = 0.0, L, 0.0     # a rolling body's uphill excursion: the centrifugal push before g sin(theta) beats it
    assert t0 < 0.5 * math.pi / w, "the block never slides"
    while True:
        yn = step(t, y, dt)
        if yn[0] <= 0.0:
            lo, hi = 0.0, dt
            for _ in range(80):
                mid = 0.5 * (lo + hi)
                if step(t, y, mid)[0] > 0.0:
                    lo = mid
                else:
                    hi = mid
            ye = step(t, y, hi)
            t_off = t + hi
            ts.append(t_off)
            xs.append(0.0)
            vs.append(ye[1])
            n_min = min(n_min, normal(t_off, ye[1]) / g)
            break
        n += 1
        t, y = t0 + n * dt, yn
        if rolling:
            if y[1] > up_v:
                up_v, up_x, up_t = y[1], y[0], t
            assert y[1] < 1e-4, "the body rolls uphill"
        else:
            assert y[1] <= 1e-12, "the block moves uphill"
        n_min = min(n_min, normal(t, y[1]) / g)
        ts.append(t)
        xs.append(y[0])
        vs.append(y[1])
    assert n_min > 0.0, "the body lifts off the tray"
    return {"t": np.array(ts), "x": np.array(xs), "v": np.array(vs), "t_start": t0, "t_off": t_off, "v_off": -ye[1],
            "th_off": w * t_off, "work": ye[2], "n_min": n_min, "steps": n, "g": g, "w": w, "L": L, "k": k, "mu": mu,
            "up_v": up_v, "up_x": up_x - L, "up_t": up_t}


def state_at(run: dict, rt: float) -> dict:
    """(x up the tray, v along it, theta, phase) rt seconds after the tilt began; after the edge the
    body falls freely in the room frame: (dx, dy) metres from the pivot, right and down."""
    w = run["w"]
    if rt < 0.0:
        return {"x": run["L"], "v": 0.0, "th": 0.0, "phase": HELD}
    if rt < run["t_start"]:
        return {"x": run["L"], "v": 0.0, "th": w * rt, "phase": REST}
    if rt < run["t_off"]:
        return {"x": float(np.interp(rt, run["t"], run["x"])), "v": float(np.interp(rt, run["t"], run["v"])),
                "th": w * rt, "phase": MOVE}
    d = rt - run["t_off"]
    th = run["th_off"]                 # the flight direction and the body's frozen orientation
    u = run["v_off"]
    return {"x": 0.0, "v": -u, "th": w * rt, "th_off": th, "phase": OFF, "dx": u * math.cos(th) * d,
            "dy": u * math.sin(th) * d + 0.5 * run["g"] * d * d, "d": d}


def gone_time(run: dict, depth_m: float) -> float:
    """Seconds after the edge until the body has fallen depth_m below the pivot."""
    u = run["v_off"] * math.sin(run["th_off"])
    g = run["g"]
    return (-u + math.sqrt(u * u + 2.0 * g * depth_m)) / g


def measure(man: dict) -> dict:
    g, L, LT, k, R, mu = man["g"], man["start_m"], man["tray_len_m"], man["k_inertia"], man["marble_radius_m"], man["mu"]
    rate = man["rate_deg_s"]
    w = math.radians(rate)
    side = man["dice_side_m"]
    dt = 1.0 / man["steps_per_second"]
    P, D, fps, F, pa = man["cycle_s"], man["scene_duration"], man["fps"], man["reset_fade"], man["release_at"]
    cycles = D / P
    assert abs(cycles - round(cycles)) < 1e-9, "the cycle must divide the scene length"
    for key in ("cycle_s", "release_at", "first_cycle_at", "reset_fade"):
        assert abs(man[key] * fps - round(man[key] * fps)) < 1e-9, f"{key} must be a whole number of frames"
    ppm = float(man["px_per_m"])
    Rd, Dd = float(man["marble_px"]), float(man["dice_px"])
    print(f"setup: side view, two bands on one clock, the same tray drawn the same way at the same scale: a tray {LT:g} m "
          f"long tilts from flat at w = {rate:.2f} deg/s = {w:.6f} rad/s about its low edge (the pivot stays put), in "
          f"real time; a solid marble of radius R = {R * 100:g} cm ({R * 200:g} cm across; I = k m R^2 with k = {k:g}; "
          f"the mass cancels; no rolling resistance, chosen) and a dice (a {side * 100:g} cm cube modelled as a sliding "
          f"block with grip mu = {mu:g}, static equal to kinetic, a chosen number; a cube only tips above 45 degrees of "
          f"tilt (tan 45 = 1 against tan(theta) = {mu:g} for the slide), so it slides first and never tips) rest side by "
          f"side with their contact points {L:g} m up the tray from its low edge; g = {g:g} m/s^2; top band the dice "
          f"(the slow 'no' case), bottom band the marble (the fast 'yes' case); both integrated by classical RK4 at "
          f"{man['steps_per_second']} steps per second (dt = {dt:.0e} s) in the tray frame on the position up the tray "
          f"and the speed (the marble's spin from v = omega R), with the centrifugal term + w^2 x and the Coriolis term "
          f"2 w x' in the normal force (an object moving toward the pivot presses less on the tray: N = m g cos(theta) + "
          f"2 m w x', x' < 0), a stick-slip start event for the dice (bisection on the time the drive beats the grip; "
          f"it never moves uphill), the edge arrival located by bisection inside the step, checked against the closed "
          f"form and a half-step rerun; after the edge each object falls freely in the room frame; shown in real time "
          f"on a {P:g} s cycle ({P * fps:.0f} frames) with the tilt starting {pa:g} s into the cycle, {cycles:.0f} "
          f"cycles in {D:g} s; drawn at {ppm:g} px per metre (tray {LT * ppm:.0f} px, start {L * ppm:.0f} px left of "
          f"the pivot); the objects are drawn larger than life: the dice {Dd:g} px against the model's {side * 100:g} cm "
          f"= {side * ppm:.1f} px, the marble {2 * Rd:g} px across against the model's {R * 200:g} cm = {2 * R * ppm:.1f} "
          f"px, and the drawn marble's stripe rolls without slipping at its drawn size (the physics uses R = {R * 100:g} "
          f"cm); the readouts are the model's; deterministic, no seed")
    # The marble: RK4 with the frame terms, without them, the closed form, a half-step rerun.
    rm = integrate(g, w, L, k, None, dt)
    rm_nf = integrate(g, w, L, k, None, dt, frame=False)
    rm_half = integrate(g, w, L, k, None, 0.5 * dt)
    tc, thc, vc = closed_marble(g, w, k, L)
    need_simple = k / (1.0 + k) * math.tan(rm["th_off"])
    n_edge = math.cos(rm["th_off"]) - 2.0 * w * rm["v_off"] / g
    drive_edge = g * math.sin(rm["th_off"])          # x = 0 at the edge: no centrifugal part
    need_exact = k / (1.0 + k) * drive_edge / (g * n_edge)
    omega = rm["v_off"] / R
    print(f"marble (bottom band): friction can only turn a ball, so it rolls from the first instant (starts moving at "
          f"{rm['t_start']:.3f} s, {math.degrees(w * rm['t_start']):.2f} deg; the tray already turns, so the centrifugal "
          f"push w^2 L = {w * w * L:.5f} m/s^2 rolls it uphill by {rm['up_x'] * 1e9:.1f} nm at up to {rm['up_v'] * 1e6:.2f} "
          f"um/s until g sin(theta) beats it {rm['up_t'] * 1000:.1f} ms in, then it rolls toward the edge); (1 + k) x'' = "
          f"-g sin(theta) + w^2 x; RK4 "
          f"with the frame terms: off the edge at {rm['t_off']:.6f} s = {rm['t_off']:.3f} s, tilt {math.degrees(rm['th_off']):.4f} "
          f"deg = {math.degrees(rm['th_off']):.2f} deg = {math.degrees(rm['th_off']):.1f} deg = {math.degrees(rm['th_off']):.0f} deg "
          f"(rounded), speed {rm['v_off']:.6f} m/s = {rm['v_off']:.3f} m/s, {rm['steps']} steps; without the frame terms "
          f"{rm_nf['t_off']:.6f} s, {math.degrees(rm_nf['th_off']):.4f} deg, {rm_nf['v_off']:.6f} m/s (closed form "
          f"g (w t - sin w t) / ((1 + k) w^2) = L: {tc:.6f} s, {math.degrees(thc):.4f} deg, {vc:.6f} m/s; diffs "
          f"{rm_nf['t_off'] - tc:+.1e} s, {math.degrees(rm_nf['th_off'] - thc):+.1e} deg, {rm_nf['v_off'] - vc:+.1e} m/s); "
          f"the frame terms are worth {rm['t_off'] - rm_nf['t_off']:+.4f} s and {math.degrees(rm['th_off'] - rm_nf['th_off']):+.4f} "
          f"deg; half-step rerun (dt = {0.5 * dt:.0e} s): {rm_half['t_off']:.9f} s ({rm_half['t_off'] - rm['t_off']:+.1e} s) at "
          f"{rm_half['v_off']:.9f} m/s ({rm_half['v_off'] - rm['v_off']:+.1e} m/s); spin at the edge omega = v / R = "
          f"{omega:.1f} rad/s = {omega / (2.0 * math.pi):.1f} turns per second, {L / (2.0 * math.pi * R):.2f} turns over the "
          f"{L * 100:g} cm; no-slip condition: the friction needed is k / (1 + k) of the drive along the tray, so the grip "
          f"needed at the edge is k / (1 + k) tan(theta) = {need_simple:.4f} ({need_exact:.4f} with the Coriolis part of "
          f"N; any grip above that rolls it without slipping, so the chosen {mu:g} holds by a factor "
          f"{mu / need_simple:.0f}); floor push N / W = cos(theta) - 2 w v / g = {n_edge:.4f} of its weight at the edge "
          f"(cos alone {math.cos(rm['th_off']):.4f}; the least over the run {rm['n_min']:.4f})")
    assert abs(rm_nf["t_off"] - tc) < 1e-7 and abs(rm_half["t_off"] - rm["t_off"]) < 1e-9
    # The dice: the slide start against tan(theta) = mu, RK4, the brief's Coriolis convention, half step.
    rd = integrate(g, w, L, k, mu, dt)
    rd_nf = integrate(g, w, L, k, mu, dt, frame=False)
    rd_brief = integrate(g, w, L, k, mu, dt, cor_sign=-1.0)
    rd_half = integrate(g, w, L, k, mu, 0.5 * dt)
    th_s = math.atan(mu)
    print(f"dice (top band): at rest the drive along the tray is g sin(theta) - w^2 x against a grip of mu g cos(theta); "
          f"tan(theta) = mu gives {math.degrees(th_s):.4f} deg = {math.degrees(th_s):.2f} deg at {th_s / w:.4f} s = "
          f"{th_s / w:.3f} s; with the centrifugal term (w^2 L = {w * w * L:.5f} m/s^2) the RK4 start event is at "
          f"{rd['t_start']:.4f} s, {math.degrees(w * rd['t_start']):.4f} deg; then x'' = -g sin(theta) + w^2 x + mu N "
          f"with N = g cos(theta) + 2 w x'; off the edge at {rd['t_off']:.6f} s = {rd['t_off']:.3f} s = {rd['t_off']:.2f} s, "
          f"tilt {math.degrees(rd['th_off']):.4f} deg = {math.degrees(rd['th_off']):.2f} deg = {math.degrees(rd['th_off']):.1f} "
          f"deg = {math.degrees(rd['th_off']):.0f} deg (rounded), speed {rd['v_off']:.6f} m/s = {rd['v_off']:.3f} m/s = "
          f"{rd['v_off']:.2f} m/s, {rd['steps']} steps, {rd['t_off'] - rd['t_start']:.4f} s of sliding; the floor push "
          f"never drops below {rd['n_min']:.4f} of its weight; without the frame terms {rd_nf['t_off']:.6f} s, "
          f"{math.degrees(rd_nf['th_off']):.4f} deg, {rd_nf['v_off']:.6f} m/s; with the Coriolis term on N reversed (the "
          f"orchestrator's closed.py and research/tray.py convention, N = g cos(theta) - 2 w x': a comparison, not the "
          f"model) {rd_brief['t_off']:.6f} s, {math.degrees(rd_brief['th_off']):.4f} deg, {rd_brief['v_off']:.6f} m/s, least "
          f"N / W {rd_brief['n_min']:.4f}; half-step rerun (dt = {0.5 * dt:.0e} s): {rd_half['t_off']:.9f} s "
          f"({rd_half['t_off'] - rd['t_off']:+.1e} s) at {rd_half['v_off']:.9f} m/s ({rd_half['v_off'] - rd['v_off']:+.1e} m/s); "
          f"small-angle slide after the start dt^3 = 6 L / (g sqrt(1 + mu^2) w): "
          f"{(6.0 * L / (g * math.sqrt(1.0 + mu * mu) * w)) ** (1.0 / 3.0):.4f} s")
    assert abs(rd_half["t_off"] - rd["t_off"]) < 1e-9 and abs(rd["t_start"] - th_s / w) < 0.01
    margin_t = rd["t_off"] - rm["t_off"]
    margin_th = math.degrees(rd["th_off"] - rm["th_off"])
    print(f"margin: the dice leaves {margin_t:.4f} s = {margin_t:.2f} s = {margin_t:.1f} s and {margin_th:.4f} deg = "
          f"{margin_th:.2f} deg = {margin_th:.0f} deg after the marble; when the dice starts to slide the marble has been "
          f"gone for {rd['t_start'] - rm['t_off']:.2f} s; the tilt at the edge is {math.degrees(rd['th_off']) / math.degrees(rm['th_off']):.2f} "
          f"times the marble's")
    # Energy per kilogram for the marble at the edge (the tray does work on it).
    ke0 = 0.5 * (L * w) ** 2
    ke_tr = 0.5 * rm["v_off"] ** 2
    ke_sp = 0.5 * k * rm["v_off"] ** 2
    ke = ke_tr + ke_sp
    peak_i = int(np.argmax(rm["x"] * np.sin(w * rm["t"])))
    peak_h = float(rm["x"][peak_i] * math.sin(w * rm["t"][peak_i]))
    resid = ke - ke0 - rm["work"]
    print(f"energy per kg for the marble at the edge: potential drop g (h0 - h_edge) = {0.0:.4f} J/kg (its contact point "
          f"starts on the flat tray at the pivot's height and leaves at the pivot; the tray lifts it to a peak height of "
          f"{peak_h * 100:.2f} cm at {rm['t'][peak_i]:.2f} s on the way); kinetic energy {ke:.4f} J/kg = translation "
          f"{ke_tr:.4f} ({ke_tr / ke:.4f} = 1 / (1 + k) = 5/7) + spin {ke_sp:.4f} ({ke_sp / ke:.4f} = k / (1 + k) = 2/7; the "
          f"spin relative to the tray, 0.5 k v^2); the start kinetic energy with the tray already turning 0.5 (L w)^2 = "
          f"{ke0:.6f} J/kg; work done by the tray's rotation through the normal force, integral of N x w dt = "
          f"{rm['work']:.6f} J/kg; balance KE - KE0 - W = {resid:+.1e} J/kg")
    assert abs(resid) < 1e-8
    assert abs(ke_tr / ke - 1.0 / (1.0 + k)) < 1e-12
    # The table at table_step_s.
    tab_ts = [j * man["table_step_s"] for j in range(0, int(math.floor(rd["t_off"] / man["table_step_s"] + 1e-9)) + 1)]
    tab_ts = sorted(set(tab_ts + [rm["t_off"], rd["t_start"], rd["t_off"]]))
    table = []
    for tt in tab_ts:
        sm, sd = state_at(rm, tt), state_at(rd, tt)
        table.append((tt, sm, sd))
        fm = "off the edge" if sm["phase"] == OFF else f"{sm['x']:.4f} m from the edge (v {-sm['v']:.4f} m/s)"
        fd = "off the edge" if sd["phase"] == OFF else f"{sd['x']:.4f} m from the edge (v {-sd['v']:.4f} m/s, {sd['phase']})"
        print(f"  t {tt:.4f} s, tilt {math.degrees(w * tt):6.3f} deg: dice {fd}; marble {fm}")
    ev: dict = {"runs": {"dice": rd, "marble": rm}, "need": need_simple, "th_s": th_s, "margin_t": margin_t,
                "margin_th": margin_th, "closed": (tc, thc, vc)}
    # For the description: other grips, tilt rates, rolling shapes, the marble's radius.
    descr = []
    ev["grips"] = {}
    for m2 in man["description_mus"]:
        r2 = integrate(g, w, L, k, m2, dt)
        ev["grips"][m2] = r2
        descr.append(f"dice grip {m2:g}: slides from {math.degrees(math.atan(m2)):.2f} deg ({math.atan(m2) / w:.2f} s), off "
                     f"at {math.degrees(r2['th_off']):.2f} deg = {math.degrees(r2['th_off']):.1f} deg ({r2['t_off']:.2f} s) at "
                     f"{r2['v_off']:.3f} m/s")
    ev["rates"] = {}
    for rate2 in man["description_rates_deg_s"]:
        w2 = math.radians(rate2)
        b2, d2 = integrate(g, w2, L, k, None, dt), integrate(g, w2, L, k, mu, dt)
        ev["rates"][rate2] = (b2, d2)
        descr.append(f"tilt rate {rate2:g} deg/s: marble off at {math.degrees(b2['th_off']):.2f} deg = "
                     f"{math.degrees(b2['th_off']):.1f} deg ({b2['t_off']:.2f} s), dice off at {math.degrees(d2['th_off']):.2f} "
                     f"deg = {math.degrees(d2['th_off']):.1f} deg ({d2['t_off']:.2f} s)")
    ev["shapes"] = {}
    for name, k2 in man["description_shapes"].items():
        s2 = integrate(g, w, L, k2, None, dt)
        ev["shapes"][name] = s2
        descr.append(f"{name} (k = {k2:.4g}): off at {math.degrees(s2['th_off']):.2f} deg = {math.degrees(s2['th_off']):.1f} deg "
                     f"({s2['t_off']:.2f} s)")
    for R2 in man["description_radii_m"]:
        b2 = integrate(g, w, L, k, None, dt)   # R does not enter the equation of motion
        assert abs(b2["t_off"] - rm["t_off"]) < 1e-9
        descr.append(f"marble radius {R2 * 1000:g} mm: off at {math.degrees(b2['th_off']):.4f} deg ({b2['t_off']:.6f} s), "
                     f"unchanged (the radius does not enter (1 + k) x'' = -g sin(theta) + w^2 x; spin at the edge "
                     f"{b2['v_off'] / R2 / (2.0 * math.pi):.1f} turns/s)")
    descr.append(f"the frame terms (centrifugal + w^2 x, Coriolis 2 w x' in N) are worth "
                 f"{math.degrees(rm['th_off'] - rm_nf['th_off']):.4f} deg for the marble and "
                 f"{math.degrees(rd['th_off'] - rd_nf['th_off']):.4f} deg for the dice")
    print("for the description: " + "; ".join(descr))
    # The brief's checks (the sim's own numbers; the dice checks under the brief's Coriolis sign are printed too).
    checks: list[tuple[str, float, float, float]] = [
        ("marble off (s)", rm["t_off"], 1.873, 6e-4), ("marble off (deg)", math.degrees(rm["th_off"]), 5.62, 6e-3),
        ("marble off speed (m/s)", rm["v_off"], 0.642, 6e-4),
        ("marble closed form (s)", tc, 1.871, 6e-4), ("marble closed form (deg)", math.degrees(thc), 5.61, 6e-3),
        ("dice slide start (deg)", math.degrees(th_s), 21.80, 6e-3), ("dice slide start (s)", th_s / w, 7.267, 6e-4),
        ("dice off (s)", rd["t_off"], 8.910, 6e-4), ("dice off (deg)", math.degrees(rd["th_off"]), 26.73, 6e-3),
        ("dice off speed (m/s)", rd["v_off"], 0.727, 6e-4),
        ("margin (s)", margin_t, 7.04, 6e-3), ("margin (deg)", margin_th, 21.1, 6e-2),
        ("marble grip needed", need_simple, 0.0281, 6e-5),
        ("frame terms (deg)", math.degrees(rm["th_off"] - rm_nf["th_off"]), 0.006, 6e-4),
        ("dice least N / W", rd["n_min"], 0.901, 6e-4),
    ]
    for m2, want in ((0.2, 16.3), (0.3, 21.7), (0.5, 31.4), (0.6, 35.8)):
        checks.append((f"dice grip {m2:g} off (deg)", math.degrees(ev["grips"][m2]["th_off"]), want, 6e-2))
    for rate2, (wb, wd) in ((1.0, (2.7, 24.2)), (2.0, (4.3, 25.6)), (5.0, (7.9, 28.8))):
        b2, d2 = ev["rates"][rate2]
        checks += [(f"rate {rate2:g} marble off (deg)", math.degrees(b2["th_off"]), wb, 6e-2),
                   (f"rate {rate2:g} dice off (deg)", math.degrees(d2["th_off"]), wd, 6e-2)]
    for name, want in (("ice cube on ice (slides, no grip)", 5.0), ("solid cylinder", 5.7), ("hollow ball", 6.0), ("ring", 6.3)):
        checks.append((f"{name} off (deg)", math.degrees(ev["shapes"][name]["th_off"]), want, 6e-2))
    fails, out = 0, []
    for name, got, want, tol in checks:
        ok = abs(got - want) <= tol
        fails += 0 if ok else 1
        out.append(f"{name}: brief {want:g}, sim {got:.6g}, diff {got - want:+.1e}: {'ok' if ok else 'FAIL'}")
    print(f"checks against the brief ({len(checks)} checks, {fails} failed): " + "; ".join(out))
    brief_checks = [("dice off (s)", rd_brief["t_off"], 8.910, 6e-4), ("dice off (deg)", math.degrees(rd_brief["th_off"]), 26.73, 6e-3),
                    ("dice off speed (m/s)", rd_brief["v_off"], 0.727, 6e-4), ("dice least N / W", rd_brief["n_min"], 0.901, 6e-4),
                    ("margin (s)", rd_brief["t_off"] - rm["t_off"], 7.04, 6e-3),
                    ("margin (deg)", math.degrees(rd_brief["th_off"] - rm["th_off"]), 21.1, 6e-2)]
    for m2, want in ((0.2, 16.3), (0.3, 21.7), (0.5, 31.4), (0.6, 35.8)):
        brief_checks.append((f"dice grip {m2:g} off (deg)", math.degrees(integrate(g, w, L, k, m2, dt, cor_sign=-1.0)["th_off"]), want, 6e-2))
    for rate2, wd in ((1.0, 24.2), (2.0, 25.6), (5.0, 28.8)):
        brief_checks.append((f"rate {rate2:g} dice off (deg)", math.degrees(integrate(g, math.radians(rate2), L, k, mu, dt, cor_sign=-1.0)["th_off"]), wd, 6e-2))
    bf, bout = 0, []
    for name, got, want, tol in brief_checks:
        ok = abs(got - want) <= tol
        bf += 0 if ok else 1
        bout.append(f"{name}: brief {want:g}, sim {got:.6g}, diff {got - want:+.1e}: {'ok' if ok else 'FAIL'}")
    print(f"the same dice checks with the Coriolis term on N reversed, the brief's convention ({len(brief_checks)} checks, "
          f"{bf} failed; a comparison, the model above is the sim's): " + "; ".join(bout))
    ev["check_fails"], ev["brief_sign_fails"] = fails, bf
    # The schedule in video time.
    t0 = man["first_cycle_at"]
    k0 = math.ceil((0.0 - t0) / P - 1e-9) - 1
    k1 = math.floor((D - t0) / P - 1e-9)
    starts = [t0 + kk * P for kk in range(k0, k1 + 1)]
    ev["cycles"] = int(round(cycles))

    def lst(off_: float) -> str:
        return ", ".join(f"{st + off_:.2f}" for st in starts if 0.0 <= st + off_ < D)

    piv_dy = float(man["pivot_dy"])
    depth = (BAND_H - piv_dy) / ppm
    gone = {"dice": gone_time(rd, depth + Dd * 1.5 / ppm), "marble": gone_time(rm, depth + 2.0 * Rd / ppm)}
    gone_v = {m: pa + ev["runs"][m]["t_off"] + gone[m] for m in PANELS}
    ev["gone_v"] = gone_v
    assert max(gone_v.values()) < P - F, "a fallen object is still in the band at the reset fade"
    th_max = w * (P - pa)
    tau0 = (0.0 - t0) % P
    r0 = tau0 - pa
    st0 = {m: state_at(ev["runs"][m], r0) for m in PANELS}
    print(f"schedule (video time, real time): cycles of {P:g} s start at " + ", ".join(f"{st:.2f}" for st in starts)
          + f" s; the tray starts tilting {pa:g} s into each cycle at {lst(pa)} s; the marble leaves the edge "
          f"{rm['t_off']:.3f} s later at {lst(pa + rm['t_off'])} s ({pa + rm['t_off']:.3f} s into the cycle; its event row "
          f"lights) and is out of its band {gone['marble']:.3f} s after that at {lst(gone_v['marble'])} s; the dice starts to "
          f"slide at {lst(pa + rd['t_start'])} s ({pa + rd['t_start']:.3f} s into the cycle; the 'starts to slide' tick "
          f"lights over {man['tick_fade_s']:g} s) and leaves the edge at {lst(pa + rd['t_off'])} s ({pa + rd['t_off']:.3f} s "
          f"into the cycle; its event row lights), out of its band {gone['dice']:.3f} s later at {lst(gone_v['dice'])} s "
          f"({gone_v['dice']:.3f} s into the cycle, before the fade at {P - F:.2f} s); the tray reaches "
          f"{math.degrees(th_max):.2f} deg at the end of the cycle; the reset crossfade back to the flat tray runs over the "
          f"last {F:g} s of each cycle (from {lst(P - F)} s; the readouts out over its first half and in over its second); "
          f"on the first frame the cycle is {tau0:.2f} s in ({r0:.3f} s after the tilt began: the dice {st0['dice']['phase']} "
          f"at {st0['dice']['x'] * 100:.1f} cm, the marble {st0['marble']['phase']} at {st0['marble']['x'] * 100:.1f} cm, "
          f"the tray at {math.degrees(st0['dice']['th']):.1f} deg); title until {man['title_until']:g} s; payoff card from "
          f"{man['payoff_t']:g} s; the title fades back in over the last {man['loop_fade']:g} s and the last frame repeats "
          f"the first (the scene is periodic: {D:g} s holds exactly {cycles:.0f} cycles)")
    # Text widths.
    font = os.environ["SEED_ZERO_FONT"]
    f24, f28, f34, f40, f56 = (ImageFont.truetype(font, n) for n in (24, 28, 34, 40, 56))
    widths = {"overlay@34": (f34, man["overlay"])}
    for j, line in enumerate(man["title"].split("|")):
        widths[f"title line {j + 1}@56"] = (f56, line)
    widths["legend@40"] = (f40, legend_text(man))
    widths["clock@28"] = (f28, clock_text(12.345))
    widths["clock held@28"] = (f28, clock_text(-1.0))
    for m in PANELS:
        widths[f"label {m}@40"] = (f40, label_text(man, m))
        widths[f"fixed {m}@28"] = (f28, fixed_text(ev, m))
        widths[f"event {m}@40"] = (f40, event_text(ev, m))
    widths["tilt@28"] = (f28, tilt_text(26.73))
    widths["from the edge@28"] = (f28, edge_text(0.4))
    widths["off@28"] = (f28, off_text())
    widths["speed@28"] = (f28, speed_text(0.744))
    widths["left at@28"] = (f28, left_text(0.744))
    widths["tick@24"] = (f24, tick_text())
    for j, line in enumerate(payoff_lines(man, ev)):
        widths[f"payoff line {j + 1}@40"] = (f40, line)
    print("text widths (the on-screen strings verbatim): " + ", ".join(f"{kk} {f.getlength(s):.0f} px '{s}'" for kk, (f, s) in widths.items()))
    assert all(f.getlength(s) < 950 for f, s in widths.values()), "a text line is wider than 950 px"
    assert len(payoff_lines(man, ev)) <= 6, "the card has more than six lines"
    # Layout checks.
    left = ROW_X0 + max(max(f40.getlength(label_text(man, m)), f28.getlength(fixed_text(ev, m))) for m in PANELS)
    left = max(left, ROW_X0 + f28.getlength(tilt_text(26.73)))
    right = ROW_X1 - max(f28.getlength(edge_text(0.4)), f28.getlength(off_text()), f28.getlength(speed_text(0.744)),
                         f28.getlength(left_text(0.744)))
    piv_x = float(man["pivot_x_px"])
    LTp = LT * ppm
    far_top = piv_dy - LTp * math.sin(th_max)
    far_x = piv_x - LTp
    dice_top = piv_dy - L * ppm * math.sin(th_s) - Dd * math.cos(th_s) - (L * ppm) * 0.0
    ev_w = max(f40.getlength(event_text(ev, m)) for m in PANELS)
    ev_x0, ev_x1 = EVENT_X - ev_w / 2.0, EVENT_X + ev_w / 2.0
    tick_lx = piv_x - TICK_LABEL_R * math.cos(th_s) + TICK_LABEL_H * math.sin(th_s)
    tick_ly = piv_dy - TICK_LABEL_R * math.sin(th_s) - TICK_LABEL_H * math.cos(th_s)
    tick_w = f24.getlength(tick_text())
    # The ray (and the tray slab at the slide start) is lowest over the label's right end.
    tray_under_label = piv_dy - (piv_x - (tick_lx + tick_w / 2.0)) * math.tan(th_s) + TRAY_T / math.cos(th_s)
    print(f"row check: the left column ends at x {left:.0f} px, the right column starts at x {right:.0f} px; both end "
          f"{ROWS_BOTTOM} px under the band top; the pivot at x {piv_x:.0f}, {piv_dy:.0f} px under the band top "
          f"({BAND_H - piv_dy:.0f} px above the band bottom; the stand to {piv_dy + STAND_H:.0f}); the tray is {LTp:.0f} px "
          f"long, its far end at x {far_x:.0f} when flat and {LTp * math.sin(th_max):.0f} px up at the cycle's last tilt "
          f"({math.degrees(th_max):.2f} deg), its surface there {far_top:.0f} px under the band top; the dice's top corner "
          f"at the slide start {dice_top:.0f} px under the band top; the objects start {L * ppm:.0f} px left of the pivot at "
          f"x {piv_x - L * ppm:.0f}; the slide-start tick runs from radius {TICK_R0:.0f} to {TICK_R1:.0f} px along the "
          f"{math.degrees(th_s):.1f} deg ray and its label is centred at x {tick_lx:.0f}, {tick_ly:.0f} px ({tick_w:.0f} px "
          f"wide; the tray slab's underside over the label's right end is {tray_under_label:.0f} px under the band top at "
          f"the slide start); "
          f"the event row spans {EVENT_DY - 22} to {EVENT_DY + 22} px under the band top and x {ev_x0:.0f} to {ev_x1:.0f} "
          f"px (widest {ev_w:.0f} px, centred on {EVENT_X}); the falling objects pass x {piv_x - Dd:.0f} and beyond; each "
          f"band is {BAND_H} px tall (y {BAND_Y['dice']} to {BAND_Y['dice'] + BAND_H} and {BAND_Y['marble']} to "
          f"{BAND_Y['marble'] + BAND_H}); the caption band starts at y {int(man['caption_y'] * H)}; the title rows end at y "
          f"{TITLE_Y[-1] + 28} and the overlay band ends at y 130")
    assert right - left > 40, "the columns meet"
    assert far_top > ROWS_BOTTOM + 10, "the raised tray reaches the readout rows"
    assert dice_top > ROWS_BOTTOM + 10, "the dice reaches the readout rows"
    assert far_x > ROW_X0, "the tray leaves the band on the left"
    assert ev_x1 < piv_x - Dd - 40 and EVENT_DY + 22 < BAND_H - 4 and EVENT_DY - 22 > piv_dy + STAND_H, "the event row meets the tray or the drop"
    assert tick_ly - 12 > tray_under_label + 4 and tick_ly > ROWS_BOTTOM + 10 and tick_lx - tick_w / 2 > ROW_X0, "the tick label does not fit"
    assert piv_x + ARC_R < W and piv_dy + STAND_H < BAND_H, "the pivot drawing leaves the band"
    assert TITLE_Y[-1] + 28 <= BAND_Y["dice"], "the title reaches the first band"
    assert BAND_Y["marble"] + BAND_H <= int(man["caption_y"] * H), "the bottom band reaches the caption band"
    assert PAYOFF_Y - 20 > int(man["caption_y"] * H) + 90, "the card meets the caption band"
    return ev


def legend_text(man: dict) -> str:
    return f"same tray, {man['rate_deg_s']:g} deg a second, real time"


def clock_text(r: float) -> str:
    return "flat, at rest" if r < 0.0 else f"{r:.2f} s since the tilt began"


def label_text(man: dict, m: str) -> str:
    return f"dice: a block, grip {man['mu']:g}" if m == "dice" else "marble: a ball, it rolls"


def fixed_text(ev: dict, m: str) -> str:
    if m == "dice":
        return f"slides from {math.degrees(ev['th_s']):.1f} deg"
    return f"needs grip {ev['need']:.3f}: rolls at any tilt"


def tilt_text(deg: float) -> str:
    return f"tilt {deg:.1f} deg"


def edge_text(x: float) -> str:
    return f"{x:.2f} m from the edge"


def off_text() -> str:
    return "off the edge"


def speed_text(v: float) -> str:
    return f"speed {max(0.0, v):.2f} m/s"


def left_text(v: float) -> str:
    return f"left at {max(0.0, v):.2f} m/s"


def event_text(ev: dict, m: str) -> str:
    r = ev["runs"][m]
    return f"{m}: off at {math.degrees(r['th_off']):.1f} deg ({r['t_off']:.2f} s)"


def tick_text() -> str:
    return "starts to slide"


def payoff_lines(man: dict, ev: dict) -> list[str]:
    text = man["payoff_text"].format(
        thm=math.degrees(ev["runs"]["marble"]["th_off"]), thd=math.degrees(ev["runs"]["dice"]["th_off"]),
        ths=math.degrees(ev["th_s"]), mu=man["mu"], g02=math.degrees(ev["grips"][0.2]["th_off"]),
        g06=math.degrees(ev["grips"][0.6]["th_off"]), need=ev["need"])
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
        self.P = man["cycle_s"]
        self.P_f = int(round(man["cycle_s"] * self.fps))
        self.c0_f = int(round(man["first_cycle_at"] * self.fps))
        self.pa, self.F = man["release_at"], man["reset_fade"]
        self.runs = ev["runs"]
        self.L, self.LT = man["start_m"], man["tray_len_m"]
        self.px, self.py = float(man["pivot_x_px"]), float(man["pivot_dy"])
        self.Rd, self.Dd = float(man["marble_px"]), float(man["dice_px"])
        self.th_s = ev["th_s"]

    def phase(self, f: int) -> tuple[int, float]:
        k, tau_f = divmod(f - self.c0_f, self.P_f)
        return k, tau_f / self.fps

    @staticmethod
    def L_(x: float, y: float) -> tuple[float, float]:
        """Layer (2x) pixel of a band-local point, rounded to 1e-4 px so equal states draw equal pixels."""
        return round(x * SS, 4), round(y * SS, 4)

    def tray_xy(self, th: float, x_px: float, h_px: float) -> tuple[float, float]:
        """Band-local pixel of the point x_px up the tray from the pivot and h_px above its surface at tilt th."""
        return self.px - x_px * math.cos(th) + h_px * math.sin(th), self.py - x_px * math.sin(th) - h_px * math.cos(th)

    def T_(self, th: float, x_px: float, h_px: float) -> tuple[float, float]:
        return self.L_(*self.tray_xy(th, x_px, h_px))

    @staticmethod
    def dashed(d: ImageDraw.ImageDraw, a: tuple, b: tuple, col, dash: float, gap: float, width: int) -> None:
        ax, ay = a
        bx, by = b
        length = math.hypot(bx - ax, by - ay)
        if length < 1e-6:
            return
        ux, uy = (bx - ax) / length, (by - ay) / length
        s = 0.0
        while s < length:
            e = min(length, s + dash)
            d.line((ax + ux * s, ay + uy * s, ax + ux * e, ay + uy * e), fill=col, width=width)
            s = e + gap

    def draw_tray(self, d: ImageDraw.ImageDraw, m: str, th: float) -> None:
        LTp = self.LT * self.ppm
        # The flat reference (dashed) and the tilt arc at the pivot.
        self.dashed(d, self.L_(self.px - FLAT_REF, self.py), self.L_(self.px - 12, self.py), blend(MUTED, 0.6), 6 * SS, 5 * SS, 2 * SS)
        if th > 1e-6:
            r = ARC_R * SS
            X, Y = self.L_(self.px, self.py)
            d.arc((X - r, Y - r, X + r, Y + r), start=180.0, end=180.0 + math.degrees(th), fill=MUTED, width=2 * SS)
        # The stand under the low edge.
        s0, s1, s2 = self.L_(self.px, self.py + 4), self.L_(self.px - 16, self.py + STAND_H), self.L_(self.px + 16, self.py + STAND_H)
        d.polygon([s0, s1, s2], fill=DECK_A, outline=RIM, width=2 * SS)
        # The tray slab: its surface from the pivot to the far end, TRAY_T thick underneath.
        poly = [self.T_(th, 0.0, 0.0), self.T_(th, LTp, 0.0), self.T_(th, LTp, -TRAY_T), self.T_(th, 0.0, -TRAY_T)]
        d.polygon(poly, fill=PLANK, outline=RIM, width=2 * SS)
        d.line((*self.T_(th, 0.0, 0.0), *self.T_(th, LTp, 0.0)), fill=PLANK_EDGE, width=3 * SS)
        # The start mark: a coloured tick across the slab at the start distance.
        Lp = self.L * self.ppm
        d.line((*self.T_(th, Lp, -1.0), *self.T_(th, Lp, -TRAY_T + 1.0)), fill=COLOUR[m], width=3 * SS)
        # The pivot dot.
        X, Y = self.L_(self.px, self.py)
        r = 5 * SS
        d.ellipse((X - r, Y - r, X + r, Y + r), fill=GOLD)

    def draw_tick(self, d: ImageDraw.ImageDraw, lit: float) -> None:
        """Dice band: a dashed gold ray along the slide-start tilt, dim until the slide starts."""
        col = blend(GOLD, 0.35 + 0.65 * lit)
        self.dashed(d, self.T_(self.th_s, TICK_R0, 0.0), self.T_(self.th_s, TICK_R1, 0.0), col, 7 * SS, 6 * SS, 3 * SS)

    def draw_dice(self, d: ImageDraw.ImageDraw, th: float, x_px: float, off: tuple | None) -> None:
        D = self.Dd
        if off is None:
            P = lambda u, h: self.T_(th, x_px + u, h)   # noqa: E731
        else:
            ox, oy = off
            P = lambda u, h: self.L_(ox - u * math.cos(th) + h * math.sin(th), oy - u * math.sin(th) - h * math.cos(th))   # noqa: E731
        body = [P(-D / 2, 0.0), P(D / 2, 0.0), P(D / 2, D), P(-D / 2, D)]
        d.polygon(body, fill=DICE_FILL, outline=DICE_EDGE, width=2 * SS)
        r = 2.6 * SS
        for du, dh in ((-7.0, D / 2 + 7.0), (0.0, D / 2), (7.0, D / 2 - 7.0)):
            X, Y = P(du, dh)
            d.ellipse((X - r, Y - r, X + r, Y + r), fill=PIP)

    def draw_marble(self, d: ImageDraw.ImageDraw, th: float, x_px: float, off: tuple | None, phi: float) -> None:
        R = self.Rd
        if off is None:
            X, Y = self.T_(th, x_px, R)
        else:
            X, Y = self.L_(off[0] + R * math.sin(th), off[1] - R * math.cos(th))
        Rs = R * SS
        d.ellipse((X - Rs, Y - Rs, X + Rs, Y + Rs), fill=MARBLE, outline=MARBLE_EDGE, width=2 * SS)
        ang = th + phi                     # the stripe turns with the tray and with the roll, both clockwise on screen
        c, sn = math.cos(ang), math.sin(ang)
        d.line((X - Rs * 0.84 * c, Y - Rs * 0.84 * sn, X + Rs * 0.84 * c, Y + Rs * 0.84 * sn), fill=STRIPE, width=4 * SS)
        dr = 2.6 * SS
        px_, py_ = X + Rs * 0.6 * sn, Y - Rs * 0.6 * c
        d.ellipse((px_ - dr, py_ - dr, px_ + dr, py_ + dr), fill=STRIPE)

    def scene(self, m: str, tau: float) -> tuple[Image.Image, dict]:
        """The band layer of panel m at tau seconds into a cycle (the flat tray at rest before the tilt)."""
        layer = Image.new("RGB", (W * SS, BAND_H * SS), BG)
        d = ImageDraw.Draw(layer)
        rt = tau - self.pa
        st = state_at(self.runs[m], rt)
        st["rt"] = rt
        th = st["th"]
        self.draw_tray(d, m, th)
        st["tick"] = 0.0
        if m == "dice" and rt >= 0.0:
            since = rt - self.runs["dice"]["t_start"]
            st["tick"] = 0.0 if since < 0.0 else min(1.0, since / self.man["tick_fade_s"])
            self.draw_tick(d, st["tick"])
        x_px = st["x"] * self.ppm
        off = None
        th_body = th
        if st["phase"] == OFF:
            off = (self.px + st["dx"] * self.ppm, self.py + st["dy"] * self.ppm)
            x_px = 0.0
            th_body = st["th_off"]
        if m == "dice":
            self.draw_dice(d, th_body, x_px, off)
        else:
            rolled = (self.L - st["x"]) * self.ppm
            if st["phase"] == OFF:
                rolled += st["v"] * -1.0 * self.ppm * st["d"]     # keeps spinning at its edge rate
            self.draw_marble(d, th_body, x_px, off, rolled / self.Rd)
        return layer, st

    def draw_panel(self, m: str, f: int) -> tuple[Image.Image, dict]:
        k, tau = self.phase(f)
        P, F = self.P, self.F
        layer, st = self.scene(m, tau)
        st["alpha"], st["k"] = 1.0, k
        if tau >= P - F:
            # Crossfade to the next cycle's flat tray at rest (both objects are out of the band by now, asserted).
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
            off = ph == OFF
            d.text((ROW_X0, y0 + LABEL_DY), label_text(man, m), font=self.font, fill=COLOUR[m], anchor="lm")
            d.text((ROW_X0, y0 + SUB_DY), tilt_text(math.degrees(st["th"])), font=self.font_small, fill=blend(TEXT, a), anchor="lm")
            d.text((ROW_X0, y0 + FIX_DY), fixed_text(ev, m), font=self.font_small, fill=MUTED, anchor="lm")
            if off:
                d.text((ROW_X1, y0 + SUB_DY), off_text(), font=self.font_small, fill=blend(MUTED, a), anchor="rm")
                d.text((ROW_X1, y0 + FIX_DY), left_text(-st["v"]), font=self.font_small, fill=blend(GOLD, a), anchor="rm")
            else:
                d.text((ROW_X1, y0 + SUB_DY), edge_text(st["x"]), font=self.font_small, fill=blend(TEXT, a), anchor="rm")
                d.text((ROW_X1, y0 + FIX_DY), speed_text(-st["v"]), font=self.font_small, fill=blend(MUTED if ph != MOVE else TEXT, a), anchor="rm")
            if off:
                d.text((EVENT_X, y0 + EVENT_DY), event_text(ev, m), font=self.font, fill=blend(GOLD, a), anchor="mm")
            if m == "dice" and st["tick"] > 0.0:
                lx, ly = self.tray_xy(self.th_s, TICK_LABEL_R, TICK_LABEL_H)
                d.text((lx, y0 + ly), tick_text(), font=self.font_tiny, fill=blend(GOLD, a * st["tick"]), anchor="mm")
        if hud_alpha > 0.02:
            d.text((W / 2, LEGEND_Y), legend_text(man), font=self.font, fill=blend(TEXT, hud_alpha), anchor="mm")
            d.text((W / 2, CLOCK_Y), clock_text(states["dice"]["rt"]), font=self.font_small,
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
    man = json.loads((ROOT / "projects/tray/manifest.json").read_text())
    ev = measure(man)
    if "--measure-only" in sys.argv:
        return
    if "--frames" in sys.argv:
        times = [float(v) for v in sys.argv[sys.argv.index("--frames") + 1].split(",")]
        r = Renderer(man, ev)
        (ROOT / "media/tray").mkdir(parents=True, exist_ok=True)
        for tv in times:
            Image.fromarray(r.frame_at(int(round(tv * man["fps"])))).save(ROOT / f"media/tray/smoke-{tv}.png")
        print("smoke frames: " + ", ".join(f"{tv}" for tv in times))
        return
    Renderer(man, ev).render(ROOT / "media/tray/footage.mp4")


if __name__ == "__main__":
    main()
