#!/usr/bin/env python3
"""Drop a yo-yo beside a ball: which lands first?

One scene, side view, both objects on one height scale. The yo-yo is a
uniform solid disc of radius R and mass m (the axle's own mass is part
of the disc; m cancels) on an axle of radius r; its string, h = 1 m
long, is wound on the axle and tied to it, and a hand holds the string's
top end still. The yo-yo is let go from rest with the string taut and
vertical. The string does not slip or stretch, so the drop x and the
turn phi obey x = r phi, and the two equations

    m x'' = m g - T,    I phi'' = T r,    I = m R^2 / 2

give the string tension from the constraint, T = m g / (1 + m r^2 / I),
and the drop a = g / (1 + I / (m r^2)) = g / (1 + (R / r)^2 / 2): g / 19
for R / r = 6, with the string holding 18 / 19 of the weight all the way.
Beside it a ball of the same size is dropped from the same height at the
same instant and falls freely at g with no air drag; the floor stops it
(no bounce). Both centres drop exactly h: the ball lands when its centre
has dropped h, and the yo-yo reaches the end of its string when its
centre has dropped h, its rim then level with the floor. At the end of
the string the string is tied to the axle, so the yo-yo's downward speed
reverses while its spin keeps its sense, and the string winds on again on
the other side of the axle: an ideal turnaround with no loss (a real
yo-yo loses some each turn). The climb mirrors the drop and the yo-yo
reaches the hand with zero speed and zero spin at 2 sqrt(2 h / a); the
hand catches it and holds it until the next release. The coupled motion
(x, x', phi, phi') is integrated by classical RK4 at steps_per_second
with the tension from the constraint each step, the end of the string
and the stop at the top located by bisection inside the step, a
half-step rerun as a check, and checked against the closed forms (the
state is accumulated with compensated summation, so the energy and
no-slip residuals stay at roundoff). The drawing follows the RK4 table. Shown at 1/slow speed on a cycle_s cycle
with both let go release_at seconds into the cycle; the ball is reset
into the hand by a crossfade over the last reset_fade seconds of the
cycle (the yo-yo is already at the hand, so it does not jump); the cycle
divides the scene length, so the scene is exactly periodic and the last
frame equals the first. Deterministic, no seed.

Measured and printed: the model constants, the ball's landing by closed
form and by the same RK4 stepping, the yo-yo's drop (the end of the
string, the speed and spin there, the ratio to the ball), its state when
the ball lands, the tension fraction, the energy split and the energy
balance, the no-slip residual, the turnaround and the return, the
half-step agreement, the drop and speed tables at table_step_s for both,
the drops at the sample times, the axle and hollow-ring variants for the
description, the sector fade, the schedule in video time, the on-screen
text widths and the layout clearances.

usage: yoyo.py [--measure-only] [--frames t1,t2,...]
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
STEEL = (150, 160, 176)
CLAMP = (124, 136, 154)
BODY = (224, 104, 92)          # the yo-yo disc
SECTOR = (150, 58, 54)         # its two darker sectors (faded toward BODY as the spin rises)
DISC_RIM = (246, 178, 160)
AXLE = (24, 26, 32)

# Layout: overlay at y 96..130 (captions.py), two title rows at y 190/252 for
# the first seconds, then the legend at y 236 and the shared clock at y 290;
# one scene band y 330..1430 drawn at 2x in its own layer: the live readout
# rows at y 370/404 (left column from x 40 for the yo-yo, right column to x
# 1040 for the ball), the hand line (the release height) at hand_y with two
# small hand marks, the 1 m height scale on the left at scale_x, the yo-yo
# at yoyo_x hanging from its hand on the string, the ball at ball_x, the
# dashed gold finish line 1 m below the hand line, the floor slab one radius
# below it, the gold event rows at y 1286/1334/1382 under the floor;
# captions at caption_y 0.75 (y 1440..1530); the six-line card from y 1572
# at a 48 px pitch.
LEGEND_Y, CLOCK_Y = 236, 290
TITLE_Y0, TITLE_PITCH = 190, 62
SS = 2
PAYOFF_Y, PAYOFF_PITCH = 1572.0, 48
BAND_Y0, BAND_Y1 = 330, 1430
READ_Y = (370, 404)
ROW_X0, ROW_X1 = 40, 1040
EVENT_Y = (1286, 1334, 1382)
HAND_W, HAND_PAD, HAND_STEM = 28, 8, 30
SLAB_PX = 28
TICK_DX0, TICK_DX1, TICK_LABEL_DX = 32, 52, 58
HELD, DOWN, UP, CAUGHT = "held", "down", "up", "caught"


def blend(col, a: float, base=BG) -> tuple:
    a = max(0.0, min(1.0, a))
    return tuple(int(round(c * a + b * (1 - a))) for c, b in zip(col, base))


# --- measurement --------------------------------------------------------------
def inertia_per_mass(R: float, hollow: bool = False) -> float:
    """I / m: R^2 / 2 for a uniform solid disc, R^2 for a hollow ring."""
    return R * R if hollow else 0.5 * R * R


def accel(g: float, R: float, r: float, hollow: bool = False) -> float:
    """a = g / (1 + I / (m r^2))."""
    return g / (1.0 + inertia_per_mass(R, hollow) / (r * r))


def rk4_yoyo(g: float, h: float, R: float, r: float, dt: float, hollow: bool = False, climb: bool = True) -> dict:
    """Integrate (x, v, phi, omega) by classical RK4 at dt: x'' = g - T / m and phi'' = s T r / I with
    the tension from the no-slip constraint, T / m = g / (1 + m r^2 / I), s = +1 while the string
    unwinds (the drop) and -1 while it winds on again (the climb); the state is accumulated with
    compensated (Kahan) summation. The end of the string (x = h) and the stop at the top (v = 0 on
    the climb) are located by bisection inside the step; at the end of the string v flips sign and
    omega keeps its sense. Returns the table and the events."""
    I_m = inertia_per_mass(R, hollow)
    T_m = g / (1.0 + r * r / I_m)              # tension per unit mass from the constraint

    def acc(s: int) -> tuple[float, float]:
        return g - T_m, s * T_m * r / I_m

    def incr(y: tuple, s: int, hh: float) -> tuple:
        """The classical RK4 increment of (x, v, phi, omega) over hh (the accelerations are constant
        inside a leg, so the four stages reduce to the exact quadratic update)."""
        ax, ap = acc(s)
        x, v, p, w = y
        k1 = (v, ax, w, ap)
        k2 = (v + 0.5 * hh * ax, ax, w + 0.5 * hh * ap, ap)
        k3 = (v + 0.5 * hh * ax, ax, w + 0.5 * hh * ap, ap)
        k4 = (v + hh * ax, ax, w + hh * ap, ap)
        return tuple(hh * (k1[i] + 2.0 * k2[i] + 2.0 * k3[i] + k4[i]) / 6.0 for i in range(4))

    def step(y: tuple, s: int, hh: float) -> tuple:
        d = incr(y, s, hh)
        return tuple(y[i] + d[i] for i in range(4))

    def kstep(y: tuple, comp: list, s: int, hh: float) -> tuple:
        """The same step with compensated (Kahan) summation of the state, so the roundoff of
        40,000 additions does not swamp the energy and no-slip residuals."""
        d = incr(y, s, hh)
        out = []
        for i in range(4):
            di = d[i] - comp[i]
            tmp = y[i] + di
            comp[i] = (tmp - y[i]) - di
            out.append(tmp)
        return tuple(out)

    ts, xs, vs, ps, ws = [0.0], [0.0], [0.0], [0.0], [0.0]
    y, s, t, n = (0.0, 0.0, 0.0, 0.0), 1, 0.0, 0
    slip = 0.0
    energy = 0.0
    phi_h = None
    ev: dict = {"T_m": T_m, "I_m": I_m}
    comp = [0.0, 0.0, 0.0, 0.0]
    # The drop.
    while True:
        yn = step(y, s, dt)
        if yn[0] >= h:
            lo, hi = 0.0, dt
            for _ in range(80):
                mid = 0.5 * (lo + hi)
                if step(y, s, mid)[0] < h:
                    lo = mid
                else:
                    hi = mid
            yb = step(y, s, hi)
            t = n * dt + hi
            ev.update(t_bottom=t, v_bottom=yb[1], om_bottom=yb[3], phi_bottom=yb[2], x_bottom=yb[0], steps_down=n + 1)
            phi_h = yb[2]
            y = (yb[0], -yb[1], yb[2], yb[3])     # the turnaround: v reverses, the spin keeps its sense
            s = -1
            comp = [0.0, 0.0, 0.0, 0.0]
            ts.append(t); xs.append(y[0]); vs.append(y[1]); ps.append(y[2]); ws.append(y[3])
            break
        y, n = kstep(y, comp, s, dt), n + 1
        t = n * dt
        slip = max(slip, abs(y[0] - r * y[2]))
        energy = max(energy, abs(g * y[0] - (0.5 * y[1] ** 2 + 0.5 * I_m * y[3] ** 2)))
        ts.append(t); xs.append(y[0]); vs.append(y[1]); ps.append(y[2]); ws.append(y[3])
    ev["slip_down"] = slip
    if climb:
        # The climb, from the bottom until the yo-yo stops rising.
        t0, n = t, 0
        slip_up = 0.0
        while True:
            yn = step(y, s, dt)
            if yn[1] >= 0.0:
                lo, hi = 0.0, dt
                for _ in range(80):
                    mid = 0.5 * (lo + hi)
                    if step(y, s, mid)[1] < 0.0:
                        lo = mid
                    else:
                        hi = mid
                yt = step(y, s, hi)
                t = t0 + n * dt + hi
                ev.update(t_top=t, x_top=yt[0], v_top=yt[1], om_top=yt[3], phi_top=yt[2], steps_up=n + 1)
                ts.append(t); xs.append(yt[0]); vs.append(yt[1]); ps.append(yt[2]); ws.append(yt[3])
                break
            y, n = kstep(y, comp, s, dt), n + 1
            t = t0 + n * dt
            slip_up = max(slip_up, abs((h - y[0]) - r * (y[2] - phi_h)))
            energy = max(energy, abs(g * y[0] - (0.5 * y[1] ** 2 + 0.5 * I_m * y[3] ** 2)))
            ts.append(t); xs.append(y[0]); vs.append(y[1]); ps.append(y[2]); ws.append(y[3])
        ev["slip_up"] = slip_up
    ev["energy_resid"] = energy
    ev["t"], ev["x"], ev["v"], ev["phi"], ev["om"] = (np.array(a) for a in (ts, xs, vs, ps, ws))
    return ev


def rk4_ball(g: float, h: float, dt: float) -> tuple[float, float, int]:
    """The free fall stepped the same way (a = g), the landing by bisection: (t, v, steps)."""
    def step(x: float, v: float, hh: float) -> tuple[float, float]:
        return x + v * hh + 0.5 * g * hh * hh, v + g * hh

    x, v, n = 0.0, 0.0, 0
    while True:
        xn, vn = step(x, v, dt)
        if xn >= h:
            lo, hi = 0.0, dt
            for _ in range(80):
                mid = 0.5 * (lo + hi)
                if step(x, v, mid)[0] < h:
                    lo = mid
                else:
                    hi = mid
            xb, vb = step(x, v, hi)
            return n * dt + hi, vb, n + 1
        x, v, n = xn, vn, n + 1


def yoyo_state(run: dict, rt: float, h: float) -> dict:
    """(x, v, phi, om, phase) of the yo-yo rt real seconds after the release."""
    if rt < 0.0:
        return {"x": 0.0, "v": 0.0, "phi": 0.0, "om": 0.0, "phase": HELD}
    if rt >= run["t_top"]:
        return {"x": 0.0, "v": 0.0, "phi": run["phi_top"], "om": 0.0, "phase": CAUGHT}
    st = {k: float(np.interp(rt, run["t"], run[k])) for k in ("x", "v", "phi", "om")}
    st["phase"] = DOWN if rt < run["t_bottom"] else UP
    if st["phase"] == UP:
        st["x"] = min(h, st["x"])
    return st


def ball_state(g: float, h: float, t_land: float, rt: float) -> dict:
    if rt < 0.0:
        return {"y": 0.0, "v": 0.0, "phase": HELD}
    if rt >= t_land:
        return {"y": h, "v": 0.0, "phase": CAUGHT}   # on the floor, stopped
    return {"y": 0.5 * g * rt * rt, "v": g * rt, "phase": DOWN}


def rpm(om: float) -> float:
    return om * 60.0 / (2.0 * math.pi)


def measure(man: dict) -> dict:
    g, h, R, r, rb = man["g"], man["drop_m"], man["disc_radius_m"], man["axle_radius_m"], man["ball_radius_m"]
    dt = 1.0 / man["steps_per_second"]
    S, P, D, fps, F, pa = man["slow"], man["cycle_s"], man["scene_duration"], man["fps"], man["reset_fade"], man["release_at"]
    cycles = D / P
    assert abs(cycles - round(cycles)) < 1e-9, "the cycle must divide the scene length"
    for key in ("cycle_s", "release_at", "first_cycle_at", "reset_fade"):
        assert abs(man[key] * fps - round(man[key] * fps)) < 1e-9, f"{key} must be a whole number of frames"
    ppm = man["px_per_m"]
    k = inertia_per_mass(R) / (r * r)
    a = accel(g, R, r)
    tension = k / (1.0 + k)
    print(f"setup: one scene, side view, both objects on one height scale: a yo-yo, a uniform solid disc of radius R = "
          f"{R * 100:g} cm ({2 * R * 100:g} cm across; its mass m cancels and the axle's own mass is part of the disc) "
          f"on an axle of radius r = {r * 100:g} cm ({2 * r * 100:g} cm across), R / r = {R / r:g}, I = m R^2 / 2; its "
          f"string, {h:g} m long, is wound on the axle and tied to it, and a hand holds the string's top end still; "
          f"the yo-yo is let go from rest with the string taut and vertical, and the string does not slip or stretch "
          f"(x = r phi); beside it a ball of the same size (radius {rb * 100:g} cm) is dropped from the same height at "
          f"the same instant and falls freely at g = {g:g} m/s^2 with no air drag; the floor stops it, no bounce; both "
          f"centres drop exactly {h:.2f} m: the ball lands when its centre has dropped {h:g} m and the yo-yo reaches the "
          f"end of its string when its centre has dropped {h:g} m, its rim then level with the floor; at the end of the "
          f"string the string is tied to the axle, so the yo-yo's downward speed reverses, its spin keeps its sense and "
          f"the string winds on again on the other side of the axle, an ideal turnaround with no loss (a real yo-yo "
          f"loses some each turn); the coupled motion (x, x', phi, phi') integrated by RK4 at {man['steps_per_second']} "
          f"steps per second (dt = {dt:.0e} s) with the tension from the constraint each step and compensated (Kahan) "
          f"summation of the state, the end of the string and the stop at the top located by bisection inside the step, "
          f"a half-step rerun as a check, against the closed "
          f"forms; shown at 1/{S:g} speed on a {P:g} s cycle ({P * fps:.0f} frames) with both let go {pa:g} s into the "
          f"cycle, {cycles:.0f} cycles in {D:g} s; drawn at {ppm:g} px per metre (the yo-yo and the ball {2 * R * ppm:.0f} "
          f"px across, the axle {2 * r * ppm:.0f} px); deterministic, no seed")
    print(f"model: m x'' = m g - T and I phi'' = T r with x = r phi give T = m g / (1 + m r^2 / I) and a = g / (1 + I / "
          f"(m r^2)) = g / (1 + (R / r)^2 / 2); I / (m r^2) = (R / r)^2 / 2 = {k:g}, so a = g / {1 + k:g} = {a:.4f} m/s^2 "
          f"= {a:.3f} m/s^2 ({a / g:.4f} g) and T = (1 - a / g) m g = {k:g} / {1 + k:g} of the weight = {tension:.4f} = "
          f"{tension * 100:.2f} percent = {tension * 100:.1f} percent, all the way down and up (the same constraint and "
          f"the same tension on the climb, with the torque reversed); a is the same for any mass and any string length")
    # The ball.
    t_ball = math.sqrt(2.0 * h / g)
    v_ball = g * t_ball
    tb_rk, vb_rk, nb = rk4_ball(g, h, dt)
    print(f"ball: falls {h:g} m in sqrt(2 h / g) = {t_ball:.4f} s = {t_ball:.2f} s (under half a second: {t_ball:.4f} < "
          f"0.5) and lands at g t = {v_ball:.3f} m/s = {v_ball:.2f} m/s; stepped at the same dt the ball lands at "
          f"{tb_rk:.6f} s (diff {tb_rk - t_ball:+.1e} s) at {vb_rk:.4f} m/s ({nb} steps); the floor stops it")
    assert abs(tb_rk - t_ball) < 1e-9
    # The yo-yo by RK4 against the closed forms.
    run = rk4_yoyo(g, h, R, r, dt)
    half = rk4_yoyo(g, h, R, r, 0.5 * dt)
    t_c = math.sqrt(2.0 * h / a)
    v_c = math.sqrt(2.0 * a * h)
    om_c = v_c / r
    ratio = run["t_bottom"] / t_ball
    x_at_ball = float(np.interp(t_ball, run["t"], run["x"]))
    v_at_ball = float(np.interp(t_ball, run["t"], run["v"]))
    om_at_ball = float(np.interp(t_ball, run["t"], run["om"]))
    print(f"yo-yo (RK4, {run['steps_down']} steps down): reaches the end of its string at {run['t_bottom']:.4f} s = "
          f"{run['t_bottom']:.2f} s (closed form sqrt(2 h / a) = {t_c:.4f} s, diff {run['t_bottom'] - t_c:+.1e} s; nearly "
          f"two seconds), {run['t_bottom'] - t_ball:.4f} s = {run['t_bottom'] - t_ball:.3f} s after the ball, "
          f"{ratio:.4f} times later = {ratio:.2f} times = {ratio:.1f} times (exactly sqrt({1 + k:g}) = "
          f"{math.sqrt(1 + k):.4f}, diff {ratio - math.sqrt(1 + k):+.1e}), moving at {run['v_bottom']:.4f} m/s = "
          f"{run['v_bottom']:.3f} m/s = {run['v_bottom']:.2f} m/s (closed form sqrt(2 a h) = {v_c:.4f} m/s, diff "
          f"{run['v_bottom'] - v_c:+.1e}) and spinning at {run['om_bottom']:.2f} rad/s = {run['om_bottom']:.1f} rad/s "
          f"(closed form v / r = {om_c:.2f} rad/s, diff {run['om_bottom'] - om_c:+.1e}) = {rpm(run['om_bottom']):.1f} turns "
          f"a minute = {rpm(run['om_bottom']):.0f} turns a minute = {rpm(run['om_bottom']):,.0f} turns a minute "
          f"({rpm(run['om_bottom']) / 60:.1f} turns a second), {run['phi_bottom'] / (2 * math.pi):.2f} turns in all (h / "
          f"(2 pi r) = {h / (2 * math.pi * r):.2f}); when the ball lands at {t_ball:.4f} s the yo-yo has dropped "
          f"{x_at_ball:.4f} m = {x_at_ball * 100:.2f} cm = {x_at_ball * 100:.1f} cm = about {x_at_ball * 100:.0f} cm "
          f"(closed form a t^2 / 2 = {0.5 * a * t_ball ** 2 * 100:.2f} cm) and moves at {v_at_ball:.4f} m/s = "
          f"{v_at_ball:.3f} m/s, spinning {rpm(om_at_ball):.0f} turns a minute, against the ball's {v_ball:.2f} m/s; when "
          f"the yo-yo reaches the bottom the ball has been down for {run['t_bottom'] - t_ball:.4f} s = "
          f"{run['t_bottom'] - t_ball:.3f} s")
    assert abs(run["t_bottom"] - t_c) < 1e-9 and abs(run["v_bottom"] - v_c) < 1e-9 and abs(run["om_bottom"] - om_c) < 1e-6
    # Tension, energy, no-slip, turnaround and return.
    e_fall = 0.5 * run["v_bottom"] ** 2 / (g * h)
    e_spin = 0.5 * run["I_m"] * run["om_bottom"] ** 2 / (g * h)
    print(f"checks: the string holds T / (m g) = {run['T_m'] / g:.6f} of the weight = {run['T_m'] / g * 100:.2f} percent "
          f"({k:g} / {1 + k:g} = {tension:.6f}, diff {run['T_m'] / g - tension:+.1e}), constant down and up; energy at the "
          f"bottom per unit mass: g h = {g * h:.4f} J/kg against v^2 / 2 = {0.5 * run['v_bottom'] ** 2:.4f} J/kg in the "
          f"fall ({e_fall:.4f} = {e_fall * 100:.2f} percent; 1 / {1 + k:g} = {1 / (1 + k):.4f}) plus (I / m) omega^2 / 2 = "
          f"{0.5 * run['I_m'] * run['om_bottom'] ** 2:.4f} J/kg in the spin ({e_spin:.4f} = {e_spin * 100:.2f} percent; "
          f"{k:g} / {1 + k:g} = {k / (1 + k):.4f}); the energy balance m g x = kinetic energy of fall plus spin holds "
          f"within {run['energy_resid']:.1e} J/kg over the drop and the climb; the no-slip residual x - r phi stays "
          f"within {run['slip_down']:.1e} m on the way down and (h - x) - r (phi - phi_h) within {run['slip_up']:.1e} m on "
          f"the way up; turnaround at {run['t_bottom']:.4f} s: {run['v_bottom']:.4f} m/s down becomes "
          f"{run['v_bottom']:.4f} m/s up, the spin stays {run['om_bottom']:.2f} rad/s; the yo-yo stops rising at "
          f"{run['t_top']:.4f} s = {run['t_top']:.3f} s = {run['t_top']:.2f} s (closed form 2 sqrt(2 h / a) = {2 * t_c:.4f} "
          f"s, diff {run['t_top'] - 2 * t_c:+.1e} s; {run['t_top'] / t_ball:.2f} times the ball's fall) at x = "
          f"{run['x_top']:.1e} m from the hand with speed {run['v_top']:.1e} m/s and spin {run['om_top']:.1e} rad/s: "
          f"back at the hand with zero speed, the hand catches it; {run['steps_up']} steps up; half-step rerun (dt = "
          f"{0.5 * dt:.0e} s): the end of the string at {half['t_bottom']:.7f} s ({half['t_bottom'] - run['t_bottom']:+.1e} "
          f"s), the top at {half['t_top']:.7f} s ({half['t_top'] - run['t_top']:+.1e} s), speed at the bottom "
          f"{half['v_bottom']:.7f} m/s ({half['v_bottom'] - run['v_bottom']:+.1e} m/s)")
    assert run["energy_resid"] < 1e-12 and run["slip_down"] < 1e-12 and run["slip_up"] < 1e-12
    assert abs(run["x_top"]) < 1e-9 and abs(run["om_top"]) < 1e-6 and abs(run["t_top"] - 2 * t_c) < 1e-9
    assert abs(half["t_bottom"] - run["t_bottom"]) < 1e-6 and abs(half["t_top"] - run["t_top"]) < 1e-6
    assert abs(e_fall + e_spin - 1.0) < 1e-12
    # Tables at table_step_s for both.
    rows = []
    tt = 0.0
    while tt <= run["t_top"] + 0.5 * man["table_step_s"]:
        ys = yoyo_state(run, tt, h)
        bs = ball_state(g, h, t_ball, tt)
        ball = (f"ball {bs['y'] * 100:.1f} cm, {bs['v']:.2f} m/s" if bs["phase"] == DOWN
                else f"ball on the floor ({h * 100:.0f} cm)")
        rows.append(f"{tt:.2f} s: yo-yo {ys['x'] * 100:.1f} cm down, {abs(ys['v']):.3f} m/s {'up' if ys['v'] < 0 else 'down'}, "
                    f"{rpm(ys['om']):.0f} rpm{' (in the hand)' if ys['phase'] == CAUGHT else ''}; {ball}")
        tt += man["table_step_s"]
    print("tables (RK4 table, real time since the release): " + "; ".join(rows))
    samples = []
    for ts_ in man["sample_times_s"]:
        xs_ = float(np.interp(ts_, run["t"], run["x"]))
        samples.append(f"{ts_:g} s: {xs_ * 100:.1f} cm down (closed form {0.5 * a * ts_ ** 2 * 100:.1f} cm), "
                       f"{float(np.interp(ts_, run['t'], run['v'])):.3f} m/s, {rpm(float(np.interp(ts_, run['t'], run['om']))):.0f} rpm")
    print("drops at the sample times: " + "; ".join(samples))
    # Variants for the description.
    descr = []
    variants = []
    for r2 in man["description_axle_radii_m"]:
        variants.append((f"a {2 * r2 * 100:g} cm axle (R / r = {R / r2:g}, solid disc)", r2, False))
    variants.append((f"a hollow ring yo-yo of the same size on the {2 * r * 100:g} cm axle (I = m R^2)", r, True))
    ev_var = {}
    for name, r2, hollow in variants:
        k2 = inertia_per_mass(R, hollow) / (r2 * r2)
        a2 = accel(g, R, r2, hollow)
        run2 = rk4_yoyo(g, h, R, r2, dt, hollow=hollow, climb=False)
        t2 = math.sqrt(2.0 * h / a2)
        v2 = math.sqrt(2.0 * a2 * h)
        ev_var[name] = run2["t_bottom"]
        descr.append(f"{name}: I / (m r^2) = {k2:g}, a = g / {1 + k2:g} = {a2:.4f} m/s^2, the end of the string at "
                     f"{run2['t_bottom']:.4f} s = {run2['t_bottom']:.3f} s = {run2['t_bottom']:.2f} s (closed form "
                     f"{t2:.4f} s, diff {run2['t_bottom'] - t2:+.1e}), {run2['t_bottom'] / t_ball:.3f} = "
                     f"{run2['t_bottom'] / t_ball:.2f} times the ball, the string holding {k2 / (1 + k2):.4f} = "
                     f"{k2 / (1 + k2) * 100:.1f} percent of the weight, {run2['v_bottom']:.3f} m/s and "
                     f"{run2['om_bottom']:.1f} rad/s = {rpm(run2['om_bottom']):,.0f} rpm at the bottom (closed form "
                     f"{v2:.4f} m/s)")
        assert abs(run2["t_bottom"] - t2) < 1e-9
    print("for the description: " + "; ".join(descr))
    # The sector fade (the spin cannot be drawn honestly at 60 fps once it is fast).
    f0, f1 = man["sector_fade_turns_per_s"]
    om0, om1 = f0 * 2 * math.pi * S, f1 * 2 * math.pi * S
    t0_, t1_ = r * om0 / a, r * om1 / a
    deg_frame = math.degrees(run["om_bottom"] / (S * fps))
    print(f"drawing: the yo-yo's two darker sectors turn with phi and their contrast fades from full at {f0:g} turns per "
          f"video second ({om0:.2f} rad/s real, reached {t0_:.4f} s after the release, {S * t0_:.3f} s of video) to none "
          f"at {f1:g} turns per video second ({om1:.2f} rad/s, {t1_:.4f} s, {S * t1_:.3f} s of video), and back again on "
          f"the climb; at the bottom the spin is {rpm(run['om_bottom']) / 60 / S:.1f} turns per video second, "
          f"{deg_frame:.0f} degrees per frame at {fps} fps, so a mark cannot be drawn honestly there and the disc is a "
          f"plain ring with the spin as a readout; the string is drawn on the axle's left side on the way down and on "
          f"its right side on the way up")
    ev: dict = {"run": run, "t_ball": t_ball, "v_ball": v_ball, "a": a, "k": k, "tension": tension, "ratio": ratio,
                "x_at_ball": x_at_ball, "v_at_ball": v_at_ball, "rpm_bottom": rpm(run["om_bottom"]), "var": ev_var}
    # The schedule in video time.
    t0 = man["first_cycle_at"]
    k0 = math.ceil((0.0 - t0) / P - 1e-9) - 1
    k1 = math.floor((D - t0) / P - 1e-9)
    starts = [t0 + kk * P for kk in range(k0, k1 + 1)]
    ev["cycles"] = int(round(cycles))

    def lst(off_: float) -> str:
        return ", ".join(f"{st + off_:.2f}" for st in starts if 0.0 <= st + off_ < D)

    vt = lambda real: pa + real * S   # noqa: E731  video time after the cycle start
    assert vt(run["t_top"]) < P - F, "the yo-yo is still moving at the reset fade"
    assert vt(t_ball) < P - F
    tau0 = (0.0 - t0) % P
    r0 = (tau0 - pa) / S
    ys0, bs0 = yoyo_state(run, r0, h), ball_state(g, h, t_ball, r0)
    print(f"schedule (video time, 1/{S:g} speed): cycles of {P:g} s start at " + ", ".join(f"{st:.2f}" for st in starts)
          + f" s (the first {-t0:.2f} s before the first frame); both let go {pa:g} s into each cycle at {lst(pa)} s; the "
          f"ball lands {S * t_ball:.3f} s after the release at {lst(vt(t_ball))} s (the first event row lights, the gold "
          f"{x_at_ball * 100:.1f} cm tick appears beside the yo-yo; the ball rests on the floor until the fade); the yo-yo "
          f"reaches the end of its string {S * run['t_bottom']:.3f} s after the release at {lst(vt(run['t_bottom']))} s "
          f"(the second event row lights) and is back in the hand {S * run['t_top']:.3f} s after the release at "
          f"{lst(vt(run['t_top']))} s ({vt(run['t_top']):.2f} s into the cycle; the third event row lights; the hand holds "
          f"it); the yo-yo is {float(np.interp(1.0 / S, run['t'], run['x'])) * 100:.1f} cm down 1 s of video after the "
          f"release and {float(np.interp(2.0 / S, run['t'], run['x'])) * 100:.1f} cm down after 2 s; the sectors fade out {S * t0_:.2f} to {S * t1_:.2f} s after the release and back in "
          f"{S * (run['t_top'] - t1_):.2f} to {S * (run['t_top'] - t0_):.2f} s after it; the reset crossfade runs over the "
          f"last {F:g} s of each cycle (from {lst(P - F)} s; the readouts out over its first half and in over its second; "
          f"the yo-yo is drawn the same in both, so it never jumps); on the first frame the cycle is {tau0:.2f} s in "
          f"({r0:.3f} s real: the yo-yo {ys0['phase']}, the ball {bs0['phase']}); title until {man['title_until']:g} s; "
          f"payoff card from {man['payoff_t']:g} s; the title fades back in over the last {man['loop_fade']:g} s and the "
          f"last frame repeats the first (the scene is periodic: {D:g} s holds exactly {cycles:.0f} cycles)")
    # Text widths.
    font = os.environ["SEED_ZERO_FONT"]
    f24, f28, f34, f40, f56 = (ImageFont.truetype(font, n) for n in (24, 28, 34, 40, 56))
    widths = {"overlay@34": (f34, man["overlay"])}
    for j, line in enumerate(man["title"].split("|")):
        widths[f"title line {j + 1}@56"] = (f56, line)
    widths["legend@40"] = (f40, legend_text(man))
    widths["clock@28"] = (f28, clock_text(3.9368))
    widths["clock held@28"] = (f28, clock_text(-1.0))
    widths["yo-yo readout@28"] = (f28, yoyo_text({"x": h, "phase": DOWN}))
    widths["yo-yo held@28"] = (f28, yoyo_text({"x": 0.0, "phase": HELD}))
    widths["yo-yo caught@28"] = (f28, yoyo_text({"x": 0.0, "phase": CAUGHT}))
    widths["spin@28"] = (f28, spin_text(run["om_bottom"]))
    widths["ball readout@28"] = (f28, ball_text({"y": h, "phase": DOWN}))
    widths["ball held@28"] = (f28, ball_text({"y": 0.0, "phase": HELD}))
    widths["ball speed@28"] = (f28, speed_text({"v": v_ball, "phase": DOWN}))
    widths["ball floor@28"] = (f28, speed_text({"v": 0.0, "phase": CAUGHT}))
    for j in range(3):
        widths[f"event {j + 1}@40"] = (f40, event_text(ev, j))
    widths["scale top@28"] = (f28, "0")
    widths["scale bottom@28"] = (f28, scale_text(h))
    widths["tick@24"] = (f24, tick_text(ev))
    for j, line in enumerate(payoff_lines(man, ev)):
        widths[f"payoff line {j + 1}@40"] = (f40, line)
    print("text widths (the on-screen strings verbatim): " + ", ".join(f"{kk} {f.getlength(s):.0f} px '{s}'"
                                                                           for kk, (f, s) in widths.items()))
    assert all(f.getlength(s) < 950 for f, s in widths.values()), "a text line is wider than 950 px"
    assert len(payoff_lines(man, ev)) <= 6, "the card has more than six lines"
    # Layout checks.
    hy, fy = float(man["hand_y"]), float(man["hand_y"]) + h * ppm
    R_px, r_px, rb_px = R * ppm, r * ppm, rb * ppm
    floor_top = fy + rb_px
    left = ROW_X0 + max(f28.getlength(s) for s in (yoyo_text({"x": h, "phase": DOWN}), yoyo_text({"x": 0.0, "phase": CAUGHT}),
                                                     spin_text(run["om_bottom"])))
    right = ROW_X1 - max(f28.getlength(s) for s in (ball_text({"y": h, "phase": DOWN}), speed_text({"v": v_ball, "phase": DOWN}),
                                                      speed_text({"v": 0.0, "phase": CAUGHT})))
    rows_bottom = READ_Y[1] + 14
    stem_top = hy - HAND_PAD - HAND_STEM
    yx, bx, sx = float(man["yoyo_x"]), float(man["ball_x"]), float(man["scale_x"])
    tick_y = hy + x_at_ball * ppm
    tick_x1 = yx + TICK_LABEL_DX + f24.getlength(tick_text(ev))
    ev_w = max(f40.getlength(event_text(ev, j)) for j in range(3))
    scale_label_x0 = sx - 36 - f28.getlength(scale_text(h))
    print(f"row check: the left column ends at x {left:.0f} px, the right column starts at x {right:.0f} px; both rows end "
          f"at y {rows_bottom:.0f}; the hand marks rise to y {stem_top:.0f} and the hand line is at y {hy:.0f} (x "
          f"{man['line_x0']} to {man['line_x1']}); the yo-yo hangs at x {yx:.0f} (disc x {yx - R_px:.0f} to {yx + R_px:.0f}, "
          f"the string at x {yx - r_px:.1f} down and {yx + r_px:.1f} up) from y {hy - R_px:.0f} at the hand to "
          f"{fy + R_px:.0f} at the bottom; the ball at x {bx:.0f} (x {bx - rb_px:.0f} to {bx + rb_px:.0f}) from y "
          f"{hy - rb_px:.0f} to {fy + rb_px:.0f}; the finish line at y {fy:.0f}, the floor from y {floor_top:.1f} to "
          f"{floor_top + SLAB_PX:.1f}; the scale at x {sx:.0f} with ticks to x {sx - 30:.0f} and labels from x "
          f"{scale_label_x0:.0f}; the gold tick at y {tick_y:.1f} from x {yx + TICK_DX0:.0f} to {yx + TICK_DX1:.0f}, its "
          f"label to x {tick_x1:.0f}; the event rows at y {EVENT_Y[0]}, {EVENT_Y[1]} and {EVENT_Y[2]} (from "
          f"{EVENT_Y[0] - 22} to {EVENT_Y[2] + 22}, widest {ev_w:.0f} px centred on {W // 2}); the band is y {BAND_Y0} to "
          f"{BAND_Y1}; the caption band starts at y {int(man['caption_y'] * H)}; the title rows end at y "
          f"{TITLE_Y0 + TITLE_PITCH + 28} and start at y {TITLE_Y0 - 28}, the overlay band ends at y 130")
    assert right - left > 40, "the columns meet"
    assert rows_bottom < stem_top - 2, "the readout rows meet the hand marks"
    assert stem_top > BAND_Y0 + 10, "the hand marks leave the band"
    assert hy - R_px > rows_bottom and hy - rb_px > rows_bottom, "an object at the hand meets the readout rows"
    assert floor_top + SLAB_PX < EVENT_Y[0] - 22 - 10, "the floor meets the event rows"
    assert EVENT_Y[2] + 22 < BAND_Y1 - 4, "the event rows leave the band"
    assert BAND_Y1 <= int(man["caption_y"] * H), "the band reaches the caption band"
    assert tick_x1 < bx - rb_px - 10, "the gold tick label meets the ball"
    assert yx - R_px > man["line_x0"] + 10 and bx + rb_px < man["line_x1"] - 10, "an object leaves the hand line"
    assert sx < yx - R_px - 60, "the scale meets the yo-yo"
    assert scale_label_x0 > 20, "the scale label leaves the frame"
    assert ev_w < 950 and W // 2 - ev_w / 2 > 40, "the event row leaves the frame"
    assert TITLE_Y0 - 28 > 130 and TITLE_Y0 + TITLE_PITCH + 28 < BAND_Y0, "the title meets the overlay or the band"
    assert PAYOFF_Y - 20 > int(man["caption_y"] * H) + 90, "the card meets the caption band"
    assert PAYOFF_Y + 5 * PAYOFF_PITCH + 20 < H - 40, "the card leaves the frame"
    return ev


def legend_text(man: dict) -> str:
    return f"same height, same instant, 1/{man['slow']:g} speed"


def clock_text(r: float) -> str:
    return "held, at rest" if r < 0.0 else f"{r:.3f} s after the release"


def yoyo_text(st: dict) -> str:
    if st["phase"] == HELD:
        return "yo-yo: in the hand"
    if st["phase"] == CAUGHT:
        return "yo-yo: back in the hand"
    return f"yo-yo: {st['x'] * 100:.1f} cm down"


def spin_text(om: float) -> str:
    return f"spin {rpm(om):.0f} turns a minute"


def ball_text(st: dict) -> str:
    if st["phase"] == HELD:
        return "ball: in the hand"
    return f"ball: {st['y'] * 100:.1f} cm down"


def speed_text(st: dict) -> str:
    if st["phase"] == CAUGHT:
        return "on the floor, stopped"
    return f"speed {st['v']:.2f} m/s"


def scale_text(h: float) -> str:
    return f"{h:g} m"


def tick_text(ev: dict) -> str:
    return f"{ev['x_at_ball'] * 100:.1f} cm"


def event_text(ev: dict, j: int) -> str:
    if j == 0:
        return f"ball lands: {ev['t_ball']:.2f} s, yo-yo {ev['x_at_ball'] * 100:.1f} cm down"
    if j == 1:
        return f"yo-yo at the bottom: {ev['run']['t_bottom']:.2f} s, {ev['ratio']:.2f}x later"
    return f"back at the hand: {ev['run']['t_top']:.2f} s"


def payoff_lines(man: dict, ev: dict) -> list[str]:
    text = man["payoff_text"].format(t_ball=ev["t_ball"], t_yo=ev["run"]["t_bottom"], ratio=ev["ratio"],
                                     x_cm=ev["x_at_ball"] * 100.0, tension_pct=ev["tension"] * 100.0,
                                     rpm=f"{ev['rpm_bottom']:,.0f}", t_back=ev["run"]["t_top"])
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
        self.g, self.h = man["g"], man["drop_m"]
        self.R_px, self.r_px, self.rb_px = (man[k] * self.ppm for k in ("disc_radius_m", "axle_radius_m", "ball_radius_m"))
        self.hy = float(man["hand_y"])
        self.fy = self.hy + self.h * self.ppm
        self.yx, self.bx, self.sx = float(man["yoyo_x"]), float(man["ball_x"]), float(man["scale_x"])
        self.run, self.t_ball = ev["run"], ev["t_ball"]
        self.f0, self.f1 = man["sector_fade_turns_per_s"]

    def phase(self, f: int) -> tuple[int, float]:
        k, tau_f = divmod(f - self.c0_f, self.P_f)
        return k, tau_f / self.fps

    @staticmethod
    def L_(x: float, y: float) -> tuple[float, float]:
        """Layer (2x) pixel of a frame point, rounded to 1e-4 px so equal states draw equal pixels."""
        return round(x * SS, 4), round((y - BAND_Y0) * SS, 4)

    def circle(self, d: ImageDraw.ImageDraw, X: float, Y: float, rr: float, **kw) -> None:
        d.ellipse((X - rr, Y - rr, X + rr, Y + rr), **kw)

    def draw_fixed(self, d: ImageDraw.ImageDraw) -> None:
        man = self.man
        hy, fy = self.hy, self.fy
        # The hand line (the release height) and the two hand marks.
        p0, p1 = self.L_(man["line_x0"], hy), self.L_(man["line_x1"], hy)
        d.line((*p0, *p1), fill=RIM, width=3 * SS)
        for cx in (self.yx, self.bx):
            s0, s1 = self.L_(cx - 5, hy - HAND_PAD - HAND_STEM), self.L_(cx + 5, hy - HAND_PAD)
            d.rectangle((s0[0], s0[1], s1[0], s1[1]), fill=CLAMP)
            q0, q1 = self.L_(cx - HAND_W / 2, hy - HAND_PAD), self.L_(cx + HAND_W / 2, hy)
            d.rounded_rectangle((q0[0], q0[1], q1[0], q1[1]), radius=3 * SS, fill=CLAMP)
        # The height scale on the left: a bar with a tick every 10 cm.
        p0, p1 = self.L_(self.sx, hy), self.L_(self.sx, fy)
        d.line((*p0, *p1), fill=RIM, width=3 * SS)
        for c in range(0, int(round(self.h * 100)) + 1, 10):
            yy = hy + c / 100.0 * self.ppm
            ln = 30 if c % 50 == 0 else 16
            p0, p1 = self.L_(self.sx - ln, yy), self.L_(self.sx, yy)
            d.line((*p0, *p1), fill=RIM, width=(3 if c % 50 == 0 else 2) * SS)
        # The dashed gold finish line (the centres' landing height) across both columns.
        x = float(man["line_x0"])
        while x < man["line_x1"]:
            p0, p1 = self.L_(x, fy), self.L_(min(x + 14.0, float(man["line_x1"])), fy)
            d.line((*p0, *p1), fill=blend(GOLD, 0.8), width=3 * SS)
            x += 24.0
        # The floor slab one radius below it.
        top = fy + self.rb_px
        s0, s1 = self.L_(man["line_x0"], top), self.L_(man["line_x1"], top + SLAB_PX)
        d.rectangle((s0[0], s0[1], s1[0], s1[1]), fill=DECK_B)
        t0, t1 = self.L_(man["line_x0"], top), self.L_(man["line_x1"], top)
        d.line((*t0, *t1), fill=RIM, width=2 * SS)

    def draw_yoyo(self, d: ImageDraw.ImageDraw, st: dict) -> None:
        cx, cy = self.yx, self.hy + st["x"] * self.ppm
        # The string from the hand to the axle's side: left on the way down, right on the way up.
        side = -1.0 if st["phase"] in (HELD, DOWN) else 1.0
        if st["phase"] in (DOWN, UP):
            sx_ = cx + side * self.r_px
            p0, p1 = self.L_(sx_, self.hy), self.L_(sx_, cy)
            d.line((*p0, *p1), fill=STEEL, width=2 * SS)
        X, Y = self.L_(cx, cy)
        rr = self.R_px * SS
        self.circle(d, X, Y, rr, fill=BODY)
        # Two darker sectors turning with phi (clockwise on screen); their contrast fades as the spin
        # rate in video turns per second rises from f0 to f1.
        f_video = abs(st["om"]) / (2.0 * math.pi) / self.S
        c = max(0.0, min(1.0, (self.f1 - f_video) / (self.f1 - self.f0)))
        if c > 0.01:
            col = blend(SECTOR, c, base=BODY)
            a0 = math.degrees(st["phi"]) % 360.0
            for start in (a0, a0 + 180.0):
                d.pieslice((X - rr, Y - rr, X + rr, Y + rr), start, start + 90.0, fill=col)
        self.circle(d, X, Y, rr, outline=DISC_RIM, width=3 * SS)
        self.circle(d, X, Y, self.r_px * SS, fill=AXLE)

    def draw_ball(self, d: ImageDraw.ImageDraw, st: dict) -> None:
        X, Y = self.L_(self.bx, self.hy + st["y"] * self.ppm)
        self.circle(d, X, Y, self.rb_px * SS, fill=TEAL)

    def scene(self, tau: float) -> tuple[Image.Image, dict]:
        """The band layer tau seconds into a cycle (both in the hand before the release)."""
        layer = Image.new("RGB", (W * SS, (BAND_Y1 - BAND_Y0) * SS), BG)
        d = ImageDraw.Draw(layer)
        self.draw_fixed(d)
        tv = tau - self.pa
        rt = tv / self.S
        ys = yoyo_state(self.run, rt, self.h)
        bs = ball_state(self.g, self.h, self.t_ball, rt)
        if bs["phase"] == CAUGHT:
            # The gold tick where the yo-yo was when the ball landed (its label is drawn at 1x).
            ty = self.hy + self.ev["x_at_ball"] * self.ppm
            p0, p1 = self.L_(self.yx + TICK_DX0, ty), self.L_(self.yx + TICK_DX1, ty)
            d.line((*p0, *p1), fill=GOLD, width=3 * SS)
        self.draw_yoyo(d, ys)
        self.draw_ball(d, bs)
        return layer, {"yoyo": ys, "ball": bs, "tv": tv, "rt": rt}

    def draw_scene(self, f: int) -> tuple[Image.Image, dict]:
        k, tau = self.phase(f)
        P, F = self.P, self.F
        layer, st = self.scene(tau)
        st["alpha"], st["k"] = 1.0, k
        if tau >= P - F:
            # Crossfade to the next cycle's held setup (the yo-yo is already in the hand, asserted in
            # measure, and is drawn the same in both; only the ball and the gold tick blend).
            a = (tau - (P - F)) / F
            new, st_new = self.scene(tau - P)
            layer = Image.blend(layer, new, a)
            st["alpha"] = max(0.0, 1.0 - 2.0 * a)
            st_new["alpha"], st_new["k"] = max(0.0, 2.0 * a - 1.0), k + 1
            if a >= 0.5:
                st = st_new
        return layer, st

    def draw_text(self, d: ImageDraw.ImageDraw, st: dict, hud_alpha: float) -> None:
        man, ev = self.man, self.ev
        a = st["alpha"]
        ys, bs = st["yoyo"], st["ball"]
        d.text((ROW_X0, READ_Y[0]), yoyo_text(ys), font=self.font_small, fill=blend(TEXT, a), anchor="lm")
        d.text((ROW_X0, READ_Y[1]), spin_text(ys["om"]), font=self.font_small, fill=blend(MUTED, a), anchor="lm")
        d.text((ROW_X1, READ_Y[0]), ball_text(bs), font=self.font_small, fill=blend(TEXT, a), anchor="rm")
        d.text((ROW_X1, READ_Y[1]), speed_text(bs), font=self.font_small, fill=blend(MUTED, a), anchor="rm")
        d.text((self.sx - 36, self.hy), "0", font=self.font_small, fill=MUTED, anchor="rm")
        d.text((self.sx - 36, self.fy), scale_text(self.h), font=self.font_small, fill=MUTED, anchor="rm")
        if bs["phase"] == CAUGHT:
            d.text((self.yx + TICK_LABEL_DX, self.hy + ev["x_at_ball"] * self.ppm), tick_text(ev), font=self.font_tiny,
                   fill=blend(GOLD, a), anchor="lm")
        rt = st["rt"]
        lit = (bs["phase"] == CAUGHT, rt >= self.run["t_bottom"], ys["phase"] == CAUGHT)
        for j in range(3):
            if lit[j]:
                d.text((W / 2, EVENT_Y[j]), event_text(ev, j), font=self.font, fill=blend(GOLD, a), anchor="mm")
        if hud_alpha > 0.02:
            d.text((W / 2, LEGEND_Y), legend_text(man), font=self.font, fill=blend(TEXT, hud_alpha), anchor="mm")
            d.text((W / 2, CLOCK_Y), clock_text(rt), font=self.font_small, fill=blend(MUTED, hud_alpha), anchor="mm")

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
        layer, st = self.draw_scene(f)
        img.paste(layer.reduce(SS), (0, BAND_Y0))
        d = ImageDraw.Draw(img)
        self.draw_text(d, st, hud_alpha)
        if title_alpha > 0.0:
            for j, line in enumerate(man["title"].split("|")):
                d.text((W / 2, TITLE_Y0 + j * TITLE_PITCH), line, font=self.font_title, fill=blend(TEXT, title_alpha),
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
    man = json.loads((ROOT / "projects/yoyo/manifest.json").read_text())
    ev = measure(man)
    if "--measure-only" in sys.argv:
        return
    if "--frames" in sys.argv:
        times = [float(v) for v in sys.argv[sys.argv.index("--frames") + 1].split(",")]
        r = Renderer(man, ev)
        (ROOT / "media/yoyo").mkdir(parents=True, exist_ok=True)
        for tv in times:
            Image.fromarray(r.frame_at(int(round(tv * man["fps"])))).save(ROOT / f"media/yoyo/smoke-{tv}.png")
        print("smoke frames: " + ", ".join(f"{tv}" for tv in times))
        return
    Renderer(man, ev).render(ROOT / "media/yoyo/footage.mp4")


if __name__ == "__main__":
    main()
