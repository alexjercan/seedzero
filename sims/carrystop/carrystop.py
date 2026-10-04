#!/usr/bin/env python3
"""Carry a weight on a string, then stop: does it swing?

Two panels on the same clock, the same string and the same speed: a point
weight (the bob) hangs on a light inextensible string of length L from a
hand that moves along a level rail at a steady speed V from t = 0 and
stops dead at t = tau (top panel tau = T / 2, half a swing; bottom panel
tau = T, one full swing). L is chosen from the small-swing period T = 2 pi
sqrt(L / g), so L = g (T / 2 pi)^2. The start and the stop are instant: at
the start the bob keeps its absolute velocity (zero), so in the hand's
frame it moves backwards at V (theta = 0, theta' = -V / L); between the
jumps the hand moves at a steady speed, its frame is inertial and the bob
is a plain pendulum,

    L theta'' = -g sin(theta),

integrated by classical RK4 at steps_per_second with compensated (Kahan)
summation of the state, the energy per unit mass (1/2) L^2 theta'^2 +
g L (1 - cos theta) constant to roundoff between the jumps. At the stop
the bob keeps its absolute velocity again: its tangential speed becomes
L theta' + V cos(theta) and the string's impulse kills the radial part
V sin(theta) (tiny at both stops), so theta' jumps by +V cos(theta) / L.
After the stop the bob swings about the fixed hand with the amplitude
acos(1 - E / (g L)), E the energy per unit mass after the stop. The
string's tension per unit mass is g cos(theta) + L theta'^2 (minus
a sin(theta) while a ramped hand accelerates at a). Linear theory, as a
check: the swing during the move is V / (omega L) and the residual swing
after the stop is 2 (V / (omega L)) |sin(pi tau / T)|: twice the carrying
swing at tau = T / 2, zero at tau = T; the nonlinear period is a little
longer than T, so the stop at T leaves a small residual and the exact zero
sits at the nonlinear period (located by a golden-section search). The
drawing follows the RK4 tables. The run repeats every cycle_s seconds of
video with a crossfade back to the held setup; the cycle divides the scene
length, so the scene is exactly periodic and the last frame equals the
first. Shown at 1/slow speed. Deterministic, no seed.

Measured and printed: L and the periods, the swing during the move
(energy form, linear form, the RK4 peak), each stop (the hand's travel,
the angle and the killed radial speed at the stop, the residual swing
against the linear form, the least tension, the bob's sideways reach),
their ratio, the exact zero of the residual, the energy drift and the
half-step rerun, the tables at table_step_s for both panels, the other
stop times, the faster hand, the ramped hand, the crane cable and the
1 m string for the description, the schedule in video time, the on-screen
text widths and the layout clearances.

usage: carrystop.py [--measure-only] [--frames t1,t2,...]
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
STEEL = (150, 160, 176)
CLAMP = (124, 136, 154)
CLAMP_DARK = (62, 70, 84)

# Layout: overlay at y 96..130 (captions.py), two title rows at y 190/252 for
# the first seconds, then the legend at y 236 and the shared clock at y 290;
# two panels stacked, the half-swing stop in the band y 330..880 and the
# full-swing stop in y 880..1430, each drawn at 2x in its own layer; each
# band has its label row 40 px under the band top, its readout rows at 84
# and 120 (left column from x 40, right column to x 1040), the gold event
# row centred 176 px under the band top; the rail 215 px under the band top
# from x 330 to 660 with ticks at 0, 0.5 and 1 m (300 px per metre); the
# hand block rides on the rail, the string hangs 298 px to the bob (radius
# 14), so the resting bob's centre is 513 px under the band top and its
# bottom 527; captions at caption_y 0.75 (y 1440..1530); the six-line card
# from y 1572 at a 48 px pitch.
LEGEND_Y, CLOCK_Y = 236, 290
TITLE_Y0, TITLE_PITCH = 190, 62
SS = 2
PAYOFF_Y, PAYOFF_PITCH = 1572.0, 48
PANELS = ("half", "full")
BAND_Y = {"half": 330, "full": 880}
BAND_H = 550
LABEL_DY, SUB_DY, FIX_DY = 40, 84, 120
EVENT_DY = 176
ROW_X0, ROW_X1 = 40, 1040
RAIL_DY = 215
RAIL_X0, RAIL_X1 = 330, 660
TICK_LEN = 8
HAND_W, HAND_H = 28, 16
BOB_R = 14
ARC_R, ARC_TICK = 60, 8
ARC_LABEL_DX, ARC_LABEL_DY = 44, 70
RAIL_LABEL_DX, RAIL_LABEL_DY = -12, 24     # labels right-anchored left of their ticks, clear of a stopped string
COLOUR = {"half": TEAL, "full": CORAL}
HELD, CARRY, STOPPED = "held", "carry", "stopped"


def blend(col, a: float, base=BG) -> tuple:
    a = max(0.0, min(1.0, a))
    return tuple(int(round(c * a + b * (1 - a))) for c, b in zip(col, base))


# --- measurement --------------------------------------------------------------
def string_length(g: float, T: float) -> float:
    """L = g (T / 2 pi)^2: the string whose small-swing period is T."""
    return g * (T / (2.0 * math.pi)) ** 2


def energy(g: float, L: float, th: float, om: float) -> float:
    """Energy per unit mass in the hand's frame: (1/2) L^2 theta'^2 + g L (1 - cos theta)."""
    return 0.5 * L * L * om * om + g * L * (1.0 - math.cos(th))


def amplitude(g: float, L: float, E: float) -> float:
    """Swing amplitude (rad) of a pendulum with energy E per unit mass."""
    return math.acos(max(-1.0, min(1.0, 1.0 - E / (g * L))))


def nonlinear_period(g: float, L: float, amp: float) -> float:
    """Exact pendulum period at amplitude amp (rad) by the arithmetic-geometric mean."""
    k = math.sin(0.5 * amp)
    a, b = 1.0, math.sqrt(1.0 - k * k)
    while abs(a - b) > 1e-16:
        a, b = 0.5 * (a + b), math.sqrt(a * b)
    return 2.0 * math.pi * math.sqrt(L / g) / a


def hand_x(V: float, tau: float, ramp: float, t: float) -> float:
    """The hand's travel along the rail at time t (instant jumps when ramp is 0)."""
    if t <= 0.0:
        return 0.0
    if ramp <= 0.0:
        return V * min(t, tau)
    def x_up(s: float) -> float:          # travel during the start ramp
        s = max(0.0, min(ramp, s))
        return 0.5 * V * s * s / ramp
    x = x_up(t) + V * max(0.0, min(t, tau) - ramp)
    if t > tau:
        s = min(ramp, t - tau)
        x += V * s - 0.5 * V * s * s / ramp
    return x


def rk4_run(g: float, L: float, V: float, tau: float, dt: float, ramp: float = 0.0, t_end: float = 5.0) -> dict:
    """Integrate L theta'' = -g sin(theta) - a cos(theta) in the hand's frame by classical RK4 at dt
    from t = 0 to t_end with compensated (Kahan) summation of the state; a is the hand's
    acceleration (zero between the jumps of an instant hand, +-V / ramp during the ramps of a ramped
    one). An instant hand starts the bob at theta' = -V / L and at t = tau (reached exactly, by a
    partial step when tau is off the grid) the stop adds V cos(theta) / L to theta'. Returns the
    tables and the events."""
    def a_piv(t: float) -> float:
        if ramp <= 0.0:
            return 0.0
        if 0.0 <= t < ramp:
            return V / ramp
        if tau <= t < tau + ramp:
            return -V / ramp
        return 0.0

    def deriv(t: float, th: float, om: float) -> tuple[float, float]:
        return om, -(g / L) * math.sin(th) - (a_piv(t) / L) * math.cos(th)

    def incr(t: float, th: float, om: float, h: float) -> tuple[float, float]:
        k1 = deriv(t, th, om)
        k2 = deriv(t + 0.5 * h, th + 0.5 * h * k1[0], om + 0.5 * h * k1[1])
        k3 = deriv(t + 0.5 * h, th + 0.5 * h * k2[0], om + 0.5 * h * k2[1])
        k4 = deriv(t + h, th + h * k3[0], om + h * k3[1])
        return (h * (k1[0] + 2.0 * k2[0] + 2.0 * k3[0] + k4[0]) / 6.0,
                h * (k1[1] + 2.0 * k2[1] + 2.0 * k3[1] + k4[1]) / 6.0)

    def tension(t: float, th: float, om: float) -> float:
        return g * math.cos(th) + L * om * om - a_piv(t) * math.sin(th)

    th, om = 0.0, (-V / L if ramp <= 0.0 else 0.0)
    comp = [0.0, 0.0]
    ts, ths, oms, tens = [0.0], [th], [om], [tension(0.0, th, om)]
    E0 = energy(g, L, th, om)
    E1 = None
    drift_move = drift_swing = 0.0
    min_T, peak = tens[0], 0.0
    stopped = ramp > 0.0            # a ramped hand has no jump
    ev: dict = {"E0": E0, "steps": 0}
    t, seg_t0, k = 0.0, 0.0, 0
    while t < t_end - 1e-12:
        t_next = seg_t0 + (k + 1) * dt
        if not stopped and t_next >= tau - 1e-9:
            t_next = tau
        t_next = min(t_next, t_end)
        h = t_next - t
        if h > 1e-15:
            d_th, d_om = incr(t, th, om, h)
            for i, (y, d) in enumerate(((th, d_th), (om, d_om))):
                di = d - comp[i]
                tmp = y + di
                comp[i] = (tmp - y) - di
                if i == 0:
                    th = tmp
                else:
                    om = tmp
            ev["steps"] += 1
        t, k = t_next, k + 1
        T_here = tension(t, th, om)
        if not stopped:
            peak = max(peak, abs(th))
            if ramp <= 0.0:
                drift_move = max(drift_move, abs(energy(g, L, th, om) - E0))
        elif E1 is not None:
            drift_swing = max(drift_swing, abs(energy(g, L, th, om) - E1))
        if not stopped and ramp <= 0.0 and t >= tau - 1e-9:
            # The stop: the bob keeps its absolute velocity, the string kills the radial part.
            om_after = om + V * math.cos(th) / L
            ev["stop"] = {"t": t, "th": th, "om_before": om, "om_after": om_after, "radial_killed": V * math.sin(th),
                          "x_hand": hand_x(V, tau, ramp, t)}
            om = om_after
            comp = [0.0, 0.0]
            E1 = energy(g, L, th, om)
            ev["E1"], ev["amp"] = E1, amplitude(g, L, E1)
            T_here = min(T_here, tension(t, th, om))
            stopped, seg_t0, k = True, t, 0
        min_T = min(min_T, T_here)
        ts.append(t)
        ths.append(th)
        oms.append(om)
        tens.append(T_here)
    if ramp > 0.0:
        # The ramped hand: the amplitude from the energy once the hand is at rest.
        assert t_end > tau + ramp, "the ramped run must outlast the stop ramp"
        ev["E1"] = energy(g, L, th, om)
        ev["amp"] = amplitude(g, L, ev["E1"])
    ev.update(peak=peak, min_T=min_T, drift_move=drift_move, drift_swing=drift_swing, V=V, tau=tau, ramp=ramp, L=L,
              g=g, t_end=t_end)
    ev["t"], ev["th"], ev["om"], ev["T"] = (np.array(a) for a in (ts, ths, oms, tens))
    ev["xh"] = np.array([hand_x(V, tau, ramp, tt) for tt in ts])
    if stopped and ramp <= 0.0:
        after = ev["th"][ev["t"] > tau]
        ev["amp_table"] = float(np.max(np.abs(after))) if len(after) else 0.0
    return ev


def residual_at(free: dict, tau: float) -> tuple[float, float, float]:
    """(residual swing, angle, killed radial speed) for a stop at tau on the free run's table: the
    state at the last grid point before tau plus one partial RK4 step (the same step the full run
    takes), then the stop's jump."""
    g, L, V = free["g"], free["L"], free["V"]
    dt = float(free["t"][1] - free["t"][0])
    n = int(math.floor(tau / dt + 1e-9))
    th, om = float(free["th"][n]), float(free["om"][n])
    h = tau - n * dt
    if h > 1e-15:
        def deriv(th_: float, om_: float) -> tuple[float, float]:
            return om_, -(g / L) * math.sin(th_)
        k1 = deriv(th, om)
        k2 = deriv(th + 0.5 * h * k1[0], om + 0.5 * h * k1[1])
        k3 = deriv(th + 0.5 * h * k2[0], om + 0.5 * h * k2[1])
        k4 = deriv(th + h * k3[0], om + h * k3[1])
        th += h * (k1[0] + 2.0 * k2[0] + 2.0 * k3[0] + k4[0]) / 6.0
        om += h * (k1[1] + 2.0 * k2[1] + 2.0 * k3[1] + k4[1]) / 6.0
    om_after = om + V * math.cos(th) / L
    return amplitude(g, L, energy(g, L, th, om_after)), th, V * math.sin(th)


def residual_zero(free: dict, lo: float, hi: float) -> tuple[float, float]:
    """The stop time in [lo, hi] with the least residual swing, by golden-section search."""
    phi = (math.sqrt(5.0) - 1.0) / 2.0
    a, b = lo, hi
    c, d = b - phi * (b - a), a + phi * (b - a)
    fc, fd = residual_at(free, c)[0], residual_at(free, d)[0]
    for _ in range(80):
        if fc < fd:
            b, d, fd = d, c, fc
            c = b - phi * (b - a)
            fc = residual_at(free, c)[0]
        else:
            a, c, fc = c, d, fd
            d = a + phi * (b - a)
            fd = residual_at(free, d)[0]
    tau = 0.5 * (a + b)
    return tau, residual_at(free, tau)[0]


def zero_crossings(run: dict) -> list[float]:
    """Times where theta crosses zero on the table (linear interpolation), after t = 0."""
    t, th = run["t"], run["th"]
    out = []
    for i in range(1, len(t) - 1):
        if th[i] == 0.0 or (th[i] < 0.0) != (th[i + 1] < 0.0):
            if th[i] == th[i + 1]:
                continue
            out.append(float(t[i] + (0.0 - th[i]) * (t[i + 1] - t[i]) / (th[i + 1] - th[i])))
    return out


def linear_residual(g: float, L: float, V: float, tau: float, T: float) -> float:
    return 2.0 * V / math.sqrt(g * L) * abs(math.sin(math.pi * tau / T))


def state_at(run: dict, rt: float) -> dict:
    """(theta, omega, tension, hand travel, phase) rt real seconds after the start."""
    if rt < 0.0:
        return {"th": 0.0, "om": 0.0, "T": run["g"], "xh": 0.0, "phase": HELD}
    st = {k: float(np.interp(rt, run["t"], run[k])) for k in ("th", "om", "T")}
    st["xh"] = hand_x(run["V"], run["tau"], run["ramp"], rt)
    st["phase"] = CARRY if rt < run["tau"] else STOPPED
    return st


def measure(man: dict) -> dict:
    g, V, T = man["g"], man["speed_m_s"], man["period_s"]
    L = string_length(g, T)
    taus = man["stop_s"]
    dt = 1.0 / man["steps_per_second"]
    S, P, D, fps, F, pa = man["slow"], man["cycle_s"], man["scene_duration"], man["fps"], man["reset_fade"], man["start_at"]
    cycles = D / P
    assert abs(cycles - round(cycles)) < 1e-9, "the cycle must divide the scene length"
    for key in ("cycle_s", "start_at", "first_cycle_at", "reset_fade"):
        assert abs(man[key] * fps - round(man[key] * fps)) < 1e-9, f"{key} must be a whole number of frames"
    ppm = man["px_per_m"]
    t_end = man["table_end_s"]
    omega = math.sqrt(g / L)
    print(f"setup: two panels on the same clock, the same string and the same speed, side view: a point weight (the bob) "
          f"hangs on a light inextensible string of length L = g (T / 2 pi)^2 = {L:.6f} m = {L * 100:.1f} cm, chosen so "
          f"the small-swing period is T = 2 pi sqrt(L / g) = {2 * math.pi * math.sqrt(L / g):.4f} s (a string that swings "
          f"once in {T:g} seconds; g = {g:g} m/s^2), from a hand that moves along a level rail at V = {V:g} m/s from t = 0 "
          f"and stops dead at t = tau: top panel tau = {taus['half']:g} s (half a swing), bottom panel tau = "
          f"{taus['full']:g} s (one full swing); the start and the stop are instant (the bob keeps its absolute velocity "
          f"at each jump: theta' = -V / L at the start, theta' + V cos(theta) / L at the stop, the string's impulse "
          f"killing the radial part V sin(theta)); between the jumps the hand's frame is inertial and the bob is a plain "
          f"pendulum L theta'' = -g sin(theta), integrated by RK4 at {man['steps_per_second']} steps per second (dt = "
          f"{dt:.0e} s) with compensated (Kahan) summation, the energy per unit mass (1/2) L^2 theta'^2 + g L (1 - cos "
          f"theta) checked between the jumps, a half-step rerun as a check; after the stop the bob swings about the fixed "
          f"hand with amplitude acos(1 - E / (g L)); the string's tension per unit mass is g cos(theta) + L theta'^2; "
          f"shown at 1/{S:g} speed on a {P:g} s cycle ({P * fps:.0f} frames) with the start {pa:g} s into the cycle, "
          f"{cycles:.0f} cycles in {D:g} s; drawn at {ppm:g} px per metre (the string {L * ppm:.0f} px, the bob "
          f"{2 * BOB_R} px across); deterministic, no seed")
    # The free run: the carrying swing and the nonlinear period.
    free = rk4_run(g, L, V, 1e9, dt, t_end=2.6)
    amp_move = math.acos(1.0 - V * V / (2.0 * g * L))
    amp_lin = V / (omega * L)
    T_nl = nonlinear_period(g, L, amp_move)
    zc = zero_crossings(free)
    print(f"the move: in the hand's frame the bob starts at theta = 0 with theta' = -V / L = {-V / L:.4f} rad/s "
          f"({math.degrees(-V / L):.2f} deg/s): it hangs back, swings forward through the plumb line half a swing later "
          f"and is ahead of the hand for the second half; the swing during the move is acos(1 - V^2 / (2 g L)) = "
          f"{math.degrees(amp_move):.3f} degrees = {math.degrees(amp_move):.1f} degrees (energy form; linear V / (omega L) "
          f"= {math.degrees(amp_lin):.3f} degrees with omega = {omega:.4f} rad/s = pi to {omega - math.pi:+.1e}); the RK4 "
          f"peak during the move is {math.degrees(free['peak']):.3f} degrees ({math.degrees(free['peak']) - math.degrees(amp_move):+.1e} "
          f"degrees from the energy form); the small-swing period is T = {T:.4f} s and the nonlinear period at "
          f"{math.degrees(amp_move):.3f} degrees is {T_nl:.4f} s (AGM), measured on the RK4 table as the second zero "
          f"crossing at {zc[1]:.4f} s (the first at {zc[0]:.4f} s; diff {zc[1] - T_nl:+.1e} s); the bob is "
          f"{L * math.sin(amp_move) * 100:.1f} cm behind the hand at the far point and {L * (1 - math.cos(amp_move)) * 100:.1f} "
          f"cm higher; tension between {free['min_T'] / g:.4f} g and {float(np.max(free['T'])) / g:.4f} g during the move")
    assert abs(T - 2.0 * math.pi * math.sqrt(L / g)) < 1e-12 and abs(zc[1] - T_nl) < 2e-4
    assert abs(math.degrees(free["peak"]) - math.degrees(amp_move)) < 1e-3
    # The two stops.
    runs = {m: rk4_run(g, L, V, taus[m], dt, t_end=t_end) for m in PANELS}
    halves = {m: rk4_run(g, L, V, taus[m], 0.5 * dt, t_end=taus[m] + 0.5) for m in PANELS}
    ev: dict = {"L": L, "T": T, "T_nl": T_nl, "amp_move": amp_move, "runs": runs, "free": free}
    for m, what in (("half", "top panel"), ("full", "bottom panel")):
        r, hf, tau = runs[m], halves[m], taus[m]
        s = r["stop"]
        lin = linear_residual(g, L, V, tau, T)
        reach = L * math.sin(r["amp"])
        print(f"stop at {tau:.1f} s ({what}, {tau / T:g} of a swing): the hand has moved V tau = {s['x_hand']:.3f} m; at "
              f"the stop the bob is at {math.degrees(s['th']):+.3f} degrees from the plumb line moving at theta' = "
              f"{s['om_before']:+.4f} rad/s in the hand's frame (the bob's absolute speed along the rail "
              f"{V + L * s['om_before'] * math.cos(s['th']):+.4f} m/s against the hand's {V:g}); the string's impulse kills "
              f"the radial speed V sin(theta) = {s['radial_killed']:+.5f} m/s (|{abs(s['radial_killed']):.4f}| < 0.001) and "
              f"theta' becomes {s['om_after']:+.4f} rad/s; the residual swing is acos(1 - E / (g L)) = "
              f"{math.degrees(r['amp']):.3f} degrees = {math.degrees(r['amp']):.1f} degrees (the RK4 table peaks at "
              f"{math.degrees(r['amp_table']):.3f} degrees after the stop; linear 2 (V / (omega L)) |sin(pi tau / T)| = "
              f"{math.degrees(lin):.3f} degrees), {math.degrees(r['amp']) / math.degrees(amp_move):.3f} times the carrying "
              f"swing; the least tension over the run is {r['min_T'] / g:.3f} g ({r['min_T']:.4f} m/s^2 per unit mass, "
              f"positive: the string stays taut); the bob's sideways reach after the stop is L sin(amp) = {reach * 100:.1f} "
              f"cm each way ({reach * ppm:.0f} px) and it rises {L * (1 - math.cos(r['amp'])) * 100:.2f} cm; energy drift "
              f"{r['drift_move']:.1e} J/kg during the move and {r['drift_swing']:.1e} J/kg after the stop (E {r['E0']:.6f} "
              f"then {r['E1']:.6f} J/kg); half-step rerun (dt = {0.5 * dt:.0e} s): residual {math.degrees(hf['amp']):.7f} "
              f"degrees ({math.degrees(hf['amp']) - math.degrees(r['amp']):+.1e}), angle at the stop "
              f"{math.degrees(hf['stop']['th']):+.6f} degrees ({math.degrees(hf['stop']['th'] - s['th']):+.1e}); {r['steps']} "
              f"steps")
        assert abs(s["radial_killed"]) < 0.001, "the killed radial speed is not tiny"
        assert r["min_T"] > 0.0, "the string goes slack"
        assert r["drift_move"] < 1e-12 and r["drift_swing"] < 1e-12, "the energy drifts"
        assert abs(math.degrees(hf["amp"]) - math.degrees(r["amp"])) < 1e-6, "the half-step rerun disagrees"
        assert abs(math.degrees(r["amp_table"]) - math.degrees(r["amp"])) < 2e-3
    ratio = runs["half"]["amp"] / runs["full"]["amp"]
    tau0, res0 = residual_zero(free, T - 0.05, T + 0.05)
    print(f"the two stops against each other: {math.degrees(runs['half']['amp']):.3f} / {math.degrees(runs['full']['amp']):.3f} "
          f"= {ratio:.1f} times the swing (about {round(ratio / 10) * 10:.0f}); the stop at {taus['full']:g} s leaves "
          f"{math.degrees(runs['full']['amp']):.3f} degrees because the nonlinear period is {T_nl:.4f} s, not {T:.4f} s: "
          f"the exact zero of the residual is at tau = {tau0:.4f} s ({tau0 - T_nl:+.1e} s from the AGM period) where the "
          f"residual is {math.degrees(res0):.3f} degrees ({math.degrees(res0):.5f}); the residual at tau = {T:g} s on the "
          f"same table is {math.degrees(residual_at(free, T)[0]):.3f} degrees (the full run gave "
          f"{math.degrees(runs['full']['amp']):.3f}); {math.degrees(runs['full']['amp']):.2f} degrees is "
          f"{L * math.sin(runs['full']['amp']) * 100:.2f} cm of sideways motion at the bob: hangs still")
    assert abs(tau0 - T_nl) < 1e-3 and math.degrees(res0) < 0.01
    ev.update(ratio=ratio, tau0=tau0, res0=res0)
    # Tables for both panels.
    for m in PANELS:
        rows = []
        tt = 0.0
        while tt <= t_end + 1e-9:
            st = state_at(runs[m], tt)
            xb = st["xh"] + L * math.sin(st["th"])
            yb = L * math.cos(st["th"])
            rows.append(f"{tt:.1f} s: {math.degrees(st['th']):+.2f} deg, {math.degrees(st['om']):+.1f} deg/s, tension "
                        f"{st['T'] / g:.3f} g, hand {st['xh']:.2f} m, bob {xb:+.3f} m along and {yb:.3f} m down"
                        f"{' (stopped)' if st['phase'] == STOPPED else ''}")
            tt = round(tt + man["table_step_s"], 10)
        print(f"table, stop at {taus[m]:g} s (RK4 table, real time since the start; the angle from the plumb line, positive "
              f"ahead of the hand; the bob's position along the rail from the start and down from the rail): " + "; ".join(rows))
    # Variants for the description.
    descr = []
    ev["descr"] = {}
    for tau in man["description_stops_s"]:
        r = rk4_run(g, L, V, tau, dt, t_end=tau + 2.2)
        descr.append(f"stop at {tau:g} s (moved {r['stop']['x_hand']:.3f} m): residual {math.degrees(r['amp']):.3f} degrees = "
                     f"{math.degrees(r['amp']):.1f} degrees (linear {math.degrees(linear_residual(g, L, V, tau, T)):.3f}), "
                     f"least tension {r['min_T'] / g:.3f} g, reach {L * math.sin(r['amp']) * 100:.1f} cm")
        ev["descr"][f"tau{tau:g}"] = r["amp"]
    V2 = man["description_speed_m_s"]
    free2 = rk4_run(g, L, V2, 1e9, dt, t_end=2.6)
    amp2 = math.acos(1.0 - V2 * V2 / (2.0 * g * L))
    T2 = nonlinear_period(g, L, amp2)
    tau2, res2 = residual_zero(free2, T - 0.05, T + 0.05)
    v1 = {}
    for tau in (taus["half"], taus["full"]):
        r = rk4_run(g, L, V2, tau, dt, t_end=tau + 2.2)
        v1[tau] = r
    descr.append(f"at V = {V2:g} m/s on the same string: the swing during the move is {math.degrees(amp2):.2f} degrees "
                 f"(RK4 peak {math.degrees(free2['peak']):.2f}; nonlinear period {T2:.4f} s), a stop at {taus['half']:g} s "
                 f"leaves {math.degrees(v1[taus['half']]['amp']):.2f} degrees (linear "
                 f"{math.degrees(linear_residual(g, L, V2, taus['half'], T)):.2f}; least tension "
                 f"{v1[taus['half']]['min_T'] / g:.3f} g; reach {L * math.sin(v1[taus['half']]['amp']) * 100:.1f} cm) and a "
                 f"stop at {taus['full']:g} s leaves {math.degrees(v1[taus['full']]['amp']):.2f} degrees "
                 f"({L * math.sin(v1[taus['full']]['amp']) * 100:.1f} cm; its exact zero is at {tau2:.4f} s with "
                 f"{math.degrees(res2):.3f} degrees left)")
    ev["v1_half"], ev["v1_full"] = v1[taus["half"]]["amp"], v1[taus["full"]]["amp"]
    for ramp in man["description_ramps_s"]:
        ra = {tau: rk4_run(g, L, V, tau, dt, ramp=ramp, t_end=tau + ramp + 1.0) for tau in (taus["half"], taus["full"])}
        descr.append(f"a hand that ramps from rest to {V:g} m/s over {ramp:g} s and back to rest over {ramp:g} s (the ramps "
                     f"starting at 0 and at tau; no jumps): the stop at {taus['half']:g} s leaves "
                     f"{math.degrees(ra[taus['half']]['amp']):.2f} degrees and the stop at {taus['full']:g} s leaves "
                     f"{math.degrees(ra[taus['full']]['amp']):.3f} degrees (least tension {ra[taus['half']]['min_T'] / g:.3f} "
                     f"and {ra[taus['full']]['min_T'] / g:.3f} g)")
    Lc, Vc = man["description_crane_m"], man["description_crane_speed_m_s"]
    Tc = 2.0 * math.pi * math.sqrt(Lc / g)
    crane = {}
    for name, tau in (("half", 0.5 * Tc), ("full", Tc)):
        crane[name] = rk4_run(g, Lc, Vc, tau, dt, t_end=tau + 0.5)
    amp_c = math.acos(1.0 - Vc * Vc / (2.0 * g * Lc))
    descr.append(f"a {Lc:g} m crane cable (T = {Tc:.3f} s) carried at {Vc:g} m/s: the load swings {math.degrees(amp_c):.2f} "
                 f"degrees during the move; a stop after half a swing at {0.5 * Tc:.3f} s leaves "
                 f"{math.degrees(crane['half']['amp']):.2f} degrees = {math.degrees(crane['half']['amp']):.1f} degrees "
                 f"({Lc * math.sin(crane['half']['amp']) * 100:.0f} cm each way) and a stop after one swing at {Tc:.3f} s "
                 f"leaves {math.degrees(crane['full']['amp']):.3f} degrees = {math.degrees(crane['full']['amp']):.2f} degrees")
    L1 = man["description_string_m"]
    T1 = 2.0 * math.pi * math.sqrt(L1 / g)
    one = {tau: rk4_run(g, L1, V, tau, dt, t_end=tau + 0.5) for tau in (taus["half"], taus["full"], T1)}
    descr.append(f"a {L1:.2f} m string (T = {T1:.4f} s) at {V:g} m/s: stops at {taus['half']:g} and {taus['full']:g} s leave "
                 f"{math.degrees(one[taus['half']]['amp']):.2f} and {math.degrees(one[taus['full']]['amp']):.2f} degrees; a "
                 f"stop at its own period {T1:.4f} s leaves {math.degrees(one[T1]['amp']):.3f} degrees")
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
    lit_at = {m: taus[m] + man["event_after_swings"][m] * T for m in PANELS}
    ev["lit_at"] = lit_at
    for m in PANELS:
        assert vt(lit_at[m]) < P - F - 1.0, "the event row lights too late in the cycle"
    rt_end = ((P - F) - pa) / S
    tau0_ = (0.0 - t0) % P
    r0 = (tau0_ - pa) / S
    st0 = {m: state_at(runs[m], r0) for m in PANELS}
    print(f"schedule (video time, 1/{S:g} speed): cycles of {P:g} s start at " + ", ".join(f"{st:.2f}" for st in starts)
          + f" s (the first {-t0:.2f} s before the first frame); the hands start {pa:g} s into each cycle at {lst(pa)} s "
          f"(real t = 0); the top hand stops {S * taus['half']:g} s later at {lst(vt(taus['half']))} s ({vt(taus['half']):.2f} s "
          f"into the cycle; the bob has swung back and forward once through the plumb line) and the bottom hand at "
          f"{lst(vt(taus['full']))} s ({vt(taus['full']):.2f} s into the cycle; the bob has swung back, forward and back "
          f"again); the top bob swings on from {vt(taus['half']):.2f} to {P - F:.2f} s of the cycle "
          f"({(P - F) - vt(taus['half']):.1f} s of video, {rt_end - taus['half']:.1f} s real, {(rt_end - taus['half']) / T:.1f} "
          f"swings); the top event row lights {man['event_after_swings']['half']:g} swing after its stop at {lst(vt(lit_at['half']))} s "
          f"and the bottom row {man['event_after_swings']['full']:g} swing after its stop at {lst(vt(lit_at['full']))} s "
          f"({vt(lit_at['full']):.2f} s into the cycle); the gold arc and its label appear at each stop; the trail follows "
          f"the bob over the last {man['trail_s']:g} s of video; the reset crossfade runs over the last {F:g} s of each cycle "
          f"(from {lst(P - F)} s; the hands and bobs blend back to the held start, the readouts out over its first half "
          f"and in over its second); on the first frame the cycle is {tau0_:.2f} s in ({r0:.3f} s real: both hands at "
          f"x {RAIL_X0} px, {st0['half']['phase']}, the bobs hanging still); title until {man['title_until']:g} s; payoff "
          f"card from {man['payoff_t']:g} s; the title fades back in over the last {man['loop_fade']:g} s and the last "
          f"frame repeats the first (the scene is periodic: {D:g} s holds exactly {cycles:.0f} cycles)")
    # Text widths.
    font = os.environ["SEED_ZERO_FONT"]
    f24, f28, f34, f40, f56 = (ImageFont.truetype(font, n) for n in (24, 28, 34, 40, 56))
    widths = {"overlay@34": (f34, man["overlay"])}
    for j, line in enumerate(man["title"].split("|")):
        widths[f"title line {j + 1}@56"] = (f56, line)
    widths["legend@40"] = (f40, legend_text(man))
    widths["clock@28"] = (f28, clock_text(3.0))
    widths["clock held@28"] = (f28, clock_text(-1.0))
    for m in PANELS:
        widths[f"label {m}@40"] = (f40, label_text(man, m))
        widths[f"hand carry {m}@28"] = (f28, hand_text(man, m, {"phase": CARRY, "xh": V * taus[m]}))
        widths[f"hand stopped {m}@28"] = (f28, hand_text(man, m, {"phase": STOPPED, "xh": V * taus[m]}))
        widths[f"event {m}@40"] = (f40, event_text(man, ev, m))
        widths[f"arc label {m}@24"] = (f24, arc_text(runs[m]["amp"]))
    widths["hand held@28"] = (f28, hand_text(man, "half", {"phase": HELD, "xh": 0.0}))
    for ph, th_, amp_ in ((HELD, 0.0, 0.0), (CARRY, -0.1, 0.0), (CARRY, 0.1, 0.0), (STOPPED, 0.0, runs["half"]["amp"]),
                          (STOPPED, 0.0, runs["full"]["amp"])):
        widths[f"state {state_text({'phase': ph, 'th': th_}, amp_)}@28"] = (f28, state_text({"phase": ph, "th": th_}, amp_))
    widths["angle@28"] = (f28, angle_text(-runs["half"]["amp"]))
    widths["tension@28"] = (f28, tension_text(g, g))
    for x in man["rail_ticks_m"]:
        widths[f"rail label {x:g}@24"] = (f24, rail_text(x))
    for j, line in enumerate(payoff_lines(man, ev)):
        widths[f"payoff line {j + 1}@40"] = (f40, line)
    print("text widths (the on-screen strings verbatim): " + ", ".join(f"{kk} {f.getlength(s):.0f} px '{s}'"
                                                                           for kk, (f, s) in widths.items()))
    assert all(f.getlength(s) < 950 for f, s in widths.values()), "a text line is wider than 950 px"
    assert len(payoff_lines(man, ev)) <= 6, "the card has more than six lines"
    # Layout checks.
    left = ROW_X0 + max(max(f40.getlength(label_text(man, m)),
                            f28.getlength(hand_text(man, m, {"phase": CARRY, "xh": V * taus[m]})),
                            f28.getlength(hand_text(man, m, {"phase": STOPPED, "xh": V * taus[m]})),
                            max(f28.getlength(s) for s in state_words(runs))) for m in PANELS)
    right = ROW_X1 - max(f28.getlength(angle_text(-runs["half"]["amp"])), f28.getlength(tension_text(g, g)))
    rows_bottom = FIX_DY + 14
    L_px = L * ppm
    rest_y = RAIL_DY + L_px
    ext = {}
    for m in PANELS:
        r = runs[m]
        sel = (r["t"] >= 0.0) & (r["t"] <= rt_end + 1e-9)
        xb = RAIL_X0 + (r["xh"][sel] + L * np.sin(r["th"][sel])) * ppm
        yb = RAIL_DY + L * np.cos(r["th"][sel]) * ppm
        ext[m] = (float(xb.min()), float(xb.max()), float(yb.min()), float(yb.max()))
    x_lo = min(e[0] for e in ext.values()) - BOB_R
    x_hi = max(e[1] for e in ext.values()) + BOB_R
    y_lo = min(e[2] for e in ext.values()) - BOB_R
    y_hi = max(e[3] for e in ext.values()) + BOB_R
    stop_x = {m: RAIL_X0 + V * taus[m] * ppm for m in PANELS}
    arc_x1 = {m: stop_x[m] + ARC_LABEL_DX + f24.getlength(arc_text(runs[m]["amp"])) for m in PANELS}
    string_dx = max(ARC_LABEL_DY * math.tan(runs[m]["amp"]) for m in PANELS)
    ticks = man["rail_ticks_m"]
    tick_x = [RAIL_X0 + x * ppm for x in ticks]
    label_x0 = [tick_x[i] + RAIL_LABEL_DX - f24.getlength(rail_text(x)) for i, x in enumerate(ticks)]
    label_dx = RAIL_LABEL_DY * math.tan(runs["half"]["amp"])
    ev_w = max(f40.getlength(event_text(man, ev, m)) for m in PANELS)
    print(f"row check: the left column ends at x {left:.0f} px, the right column starts at x {right:.0f} px; both end "
          f"{rows_bottom} px under the band top; the event row is centred {EVENT_DY} px under the band top ({EVENT_DY - 20} "
          f"to {EVENT_DY + 20}; widest {ev_w:.0f} px, x {W / 2 - ev_w / 2:.0f} to {W / 2 + ev_w / 2:.0f}); the rail is "
          f"{RAIL_DY} px under the band top from x {RAIL_X0} to {RAIL_X1} with ticks at x " + ", ".join(f"{x:.0f}" for x in tick_x)
          + f" and labels ending {-RAIL_LABEL_DX} px left of their ticks from x " + ", ".join(f"{x:.0f}" for x in label_x0)
          + f" at {RAIL_DY + RAIL_LABEL_DY} px under the band top (a stopped string is at most {label_dx:.0f} px from its "
          f"tick at that depth); the hand block ({HAND_W} x {HAND_H} px) rides the rail from x "
          f"{RAIL_X0} to {stop_x['half']:.0f} (top) and {stop_x['full']:.0f} (bottom); the string is {L_px:.0f} px, the bob "
          f"({2 * BOB_R} px) rests with its centre {rest_y:.0f} px under the band top and its bottom {rest_y + BOB_R:.0f} px; "
          f"over the drawn run the bob's centre spans x {min(e[0] for e in ext.values()):.0f} to {max(e[1] for e in ext.values()):.0f} "
          f"px and y {min(e[2] for e in ext.values()):.0f} to {max(e[3] for e in ext.values()):.0f} px under the band top "
          f"(top band x {ext['half'][0]:.0f} to {ext['half'][1]:.0f}, bottom band x {ext['full'][0]:.0f} to {ext['full'][1]:.0f}), "
          f"so the bob's disc stays inside x {x_lo:.0f} to {x_hi:.0f} and y {y_lo:.0f} to {y_hi:.0f}; the gold arc has radius "
          f"{ARC_R} px about the stopped hand with its label from x {stop_x['half'] + ARC_LABEL_DX:.0f} to {arc_x1['half']:.0f} "
          f"(top) and {stop_x['full'] + ARC_LABEL_DX:.0f} to {arc_x1['full']:.0f} (bottom) at {RAIL_DY + ARC_LABEL_DY} px under "
          f"the band top, the string at most {string_dx:.0f} px from the plumb line at that depth; each band is {BAND_H} px "
          f"tall (y {BAND_Y['half']} to {BAND_Y['half'] + BAND_H} and {BAND_Y['full']} to {BAND_Y['full'] + BAND_H}); the "
          f"caption band starts at y {int(man['caption_y'] * H)}; the title rows span y {TITLE_Y0 - 28} to "
          f"{TITLE_Y0 + TITLE_PITCH + 28} and the overlay band ends at y 130; the card spans y {PAYOFF_Y - 20:.0f} to "
          f"{PAYOFF_Y + 5 * PAYOFF_PITCH + 20:.0f}")
    assert right - left > 40, "the columns meet"
    assert rows_bottom < EVENT_DY - 20 - 4, "the readout rows meet the event row"
    assert EVENT_DY + 20 < RAIL_DY - HAND_H / 2 - 4, "the event row meets the hand"
    assert W / 2 - ev_w / 2 > 40 and W / 2 + ev_w / 2 < W - 40, "the event row leaves the frame"
    assert RAIL_DY + RAIL_LABEL_DY - 12 > RAIL_DY + HAND_H / 2, "the rail labels meet the hand"
    for i in range(len(ticks)):
        prev = tick_x[i - 1] + 16 if i > 0 else 20
        assert label_x0[i] > prev, "a rail label meets the previous tick"
    assert -RAIL_LABEL_DX > label_dx + 2, "a stopped string meets its rail label"
    assert y_hi < BAND_H - 4, "the bob leaves the band at the bottom"
    assert y_lo > EVENT_DY + 20 + 4 and y_lo > RAIL_DY + RAIL_LABEL_DY + 12, "the bob rises into the rows"
    assert x_lo > 20 and x_hi < W - 20, "the bob leaves the frame"
    assert RAIL_X0 - HAND_W / 2 > 20 and max(stop_x.values()) + HAND_W / 2 <= RAIL_X1, "the hand leaves the rail"
    for m in PANELS:
        assert arc_x1[m] < W - 40, "the arc label leaves the frame"
        assert ARC_LABEL_DX > string_dx + 12, "the arc label meets the string"
        assert RAIL_DY + ARC_LABEL_DY + 12 < y_lo, "the arc label meets the bob"
        assert ARC_R + ARC_TICK < L_px - BOB_R - 10, "the arc meets the bob"
    assert BAND_Y["full"] + BAND_H <= int(man["caption_y"] * H), "the bottom band reaches the caption band"
    assert TITLE_Y0 - 28 > 130 and TITLE_Y0 + TITLE_PITCH + 28 < BAND_Y["half"], "the title meets the overlay or the band"
    assert PAYOFF_Y - 20 > int(man["caption_y"] * H) + 90, "the card meets the caption band"
    assert PAYOFF_Y + 5 * PAYOFF_PITCH + 20 < H - 40, "the card leaves the frame"
    return ev


def legend_text(man: dict) -> str:
    return f"same string, same speed, 1/{man['slow']:g} speed"


def clock_text(r: float) -> str:
    return "held, at rest" if r < 0.0 else f"{r:.3f} s after the start"


def label_text(man: dict, m: str) -> str:
    return f"stop after {man['stop_s'][m]:g} s: {'half a swing' if m == 'half' else 'one full swing'}"


def hand_text(man: dict, m: str, st: dict) -> str:
    if st["phase"] == HELD:
        return "hand: held"
    if st["phase"] == CARRY:
        return f"hand: {man['speed_m_s']:.2f} m/s, {st['xh']:.2f} m"
    return f"hand: stopped at {man['stop_s'][m]:.1f} s"


def state_text(st: dict, amp: float) -> str:
    if st["phase"] == HELD:
        return "weight at rest"
    if st["phase"] == CARRY:
        return "weight hangs back" if st["th"] < 0.0 else "weight swings ahead"
    return "weight swings on" if math.degrees(amp) >= 1.0 else "weight hangs still"


def state_words(runs: dict) -> list[str]:
    return [state_text({"phase": HELD, "th": 0.0}, 0.0), state_text({"phase": CARRY, "th": -0.1}, 0.0),
            state_text({"phase": CARRY, "th": 0.1}, 0.0), state_text({"phase": STOPPED, "th": 0.0}, runs["half"]["amp"]),
            state_text({"phase": STOPPED, "th": 0.0}, runs["full"]["amp"])]


def angle_text(th: float) -> str:
    return f"angle {math.degrees(th):+.1f} deg"


def tension_text(T: float, g: float) -> str:
    return f"tension {T / g:.3f} g"


def rail_text(x: float) -> str:
    return "0" if x == 0.0 else f"{x:g} m"


def arc_text(amp: float) -> str:
    return f"{math.degrees(amp):.1f} deg"


def event_text(man: dict, ev: dict, m: str) -> str:
    amp = math.degrees(ev["runs"][m]["amp"])
    if m == "half":
        return f"stopped at {man['stop_s'][m]:g} s: swings {amp:.1f} degrees"
    return f"stopped at {man['stop_s'][m]:g} s: hangs still, {amp:.1f} degrees"


def payoff_lines(man: dict, ev: dict) -> list[str]:
    text = man["payoff_text"].format(
        amp_half=math.degrees(ev["runs"]["half"]["amp"]), amp_full=math.degrees(ev["runs"]["full"]["amp"]),
        T0=ev["T"], L_cm=ev["L"] * 100.0, amp1_v1=math.degrees(ev["v1_half"]), amp2_v1=math.degrees(ev["v1_full"]))
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
        self.pa, self.F = man["start_at"], man["reset_fade"]
        self.runs = ev["runs"]
        self.L, self.g = ev["L"], man["g"]
        self.trail_f = int(round(man["trail_s"] * self.fps))

    def phase(self, f: int) -> tuple[int, float]:
        k, tau_f = divmod(f - self.c0_f, self.P_f)
        return k, tau_f / self.fps

    @staticmethod
    def L_(x: float, y: float) -> tuple[float, float]:
        """Layer (2x) pixel of a band-local point, rounded to 1e-4 px so equal states draw equal pixels."""
        return round(x * SS, 4), round(y * SS, 4)

    def bob_pos(self, st: dict) -> tuple[float, float]:
        hx = RAIL_X0 + st["xh"] * self.ppm
        return hx + self.L * self.ppm * math.sin(st["th"]), RAIL_DY + self.L * self.ppm * math.cos(st["th"])

    def draw_rail(self, d: ImageDraw.ImageDraw) -> None:
        p0, p1 = self.L_(RAIL_X0, RAIL_DY), self.L_(RAIL_X1, RAIL_DY)
        d.line((*p0, *p1), fill=RIM, width=3 * SS)
        for x in self.man["rail_ticks_m"]:
            tx = RAIL_X0 + x * self.ppm
            t0, t1 = self.L_(tx, RAIL_DY), self.L_(tx, RAIL_DY + TICK_LEN)
            d.line((*t0, *t1), fill=RIM, width=3 * SS)

    def draw_dashed(self, d: ImageDraw.ImageDraw, x0: float, y0: float, x1: float, y1: float, col, dash: float = 6.0,
                    gap: float = 6.0, width: int = 2) -> None:
        length = math.hypot(x1 - x0, y1 - y0)
        if length < 1e-9:
            return
        ux, uy = (x1 - x0) / length, (y1 - y0) / length
        s = 0.0
        while s < length:
            e = min(length, s + dash)
            a, b = self.L_(x0 + ux * s, y0 + uy * s), self.L_(x0 + ux * e, y0 + uy * e)
            d.line((*a, *b), fill=col, width=width * SS)
            s += dash + gap

    def scene(self, m: str, tau: float) -> tuple[Image.Image, dict]:
        """The band layer of panel m at tau seconds into a cycle (the held setup before the start)."""
        layer = Image.new("RGB", (W * SS, BAND_H * SS), BG)
        d = ImageDraw.Draw(layer)
        self.draw_rail(d)
        run = self.runs[m]
        tv = tau - self.pa
        rt = tv / self.S
        st = state_at(run, rt)
        st["tv"], st["rt"], st["amp"] = tv, rt, run["amp"]
        hx = RAIL_X0 + st["xh"] * self.ppm
        bx, by = self.bob_pos(st)
        # The plumb line straight down from the hand.
        self.draw_dashed(d, hx, RAIL_DY + HAND_H / 2 + 6, hx, RAIL_DY + self.L * self.ppm + 8, blend(MUTED, 0.55))
        # The trail of the bob's centre over the last trail_s seconds of video (only after the start).
        if rt > 0.0:
            pts = []
            for j in range(0, self.trail_f + 1):
                rtj = rt - j / self.fps / self.S
                if rtj < 0.0:
                    break
                pts.append(self.bob_pos(state_at(run, rtj)))
            for j in range(len(pts) - 1):
                if j % 4 < 2:
                    a, b = self.L_(*pts[j]), self.L_(*pts[j + 1])
                    d.line((*a, *b), fill=blend(COLOUR[m], 0.6), width=2 * SS)
        # The swing arc about the stopped hand, with ticks at its ends.
        if st["phase"] == STOPPED:
            amp = math.degrees(run["amp"])
            cx, cy = self.L_(hx, RAIL_DY)
            Ra = ARC_R * SS
            if amp >= 0.5:
                d.arc((cx - Ra, cy - Ra, cx + Ra, cy + Ra), start=90.0 - amp, end=90.0 + amp, fill=GOLD, width=4 * SS)
            for sgn in (-1.0, 1.0):
                ang = math.radians(90.0 + sgn * amp)
                a = self.L_(hx + (ARC_R - ARC_TICK) * math.cos(ang), RAIL_DY + (ARC_R - ARC_TICK) * math.sin(ang))
                b = self.L_(hx + (ARC_R + ARC_TICK) * math.cos(ang), RAIL_DY + (ARC_R + ARC_TICK) * math.sin(ang))
                d.line((*a, *b), fill=GOLD, width=4 * SS)
        # The string, the hand and the bob.
        s0, s1 = self.L_(hx, RAIL_DY), self.L_(bx, by)
        d.line((*s0, *s1), fill=STEEL, width=2 * SS)
        h0, h1 = self.L_(hx - HAND_W / 2, RAIL_DY - HAND_H / 2), self.L_(hx + HAND_W / 2, RAIL_DY + HAND_H / 2)
        d.rounded_rectangle((h0[0], h0[1], h1[0], h1[1]), radius=3 * SS, fill=CLAMP, outline=CLAMP_DARK, width=2 * SS)
        X, Y = self.L_(bx, by)
        r = BOB_R * SS
        d.ellipse((X - r, Y - r, X + r, Y + r), fill=WHITE, outline=COLOUR[m], width=3 * SS)
        st["hx"], st["bx"], st["by"] = hx, bx, by
        return layer, st

    def draw_panel(self, m: str, f: int) -> tuple[Image.Image, dict]:
        k, tau = self.phase(f)
        P, F = self.P, self.F
        layer, st = self.scene(m, tau)
        st["alpha"], st["k"] = 1.0, k
        if tau >= P - F:
            # Crossfade to the next cycle's held setup (the hands and bobs blend back to the start).
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
            a = st["alpha"]
            run = self.runs[m]
            d.text((ROW_X0, y0 + LABEL_DY), label_text(man, m), font=self.font, fill=COLOUR[m], anchor="lm")
            d.text((ROW_X0, y0 + SUB_DY), hand_text(man, m, st), font=self.font_small, fill=blend(TEXT, a), anchor="lm")
            d.text((ROW_X0, y0 + FIX_DY), state_text(st, run["amp"]), font=self.font_small, fill=blend(MUTED, a), anchor="lm")
            lit = st["rt"] >= ev["lit_at"][m]
            d.text((ROW_X1, y0 + SUB_DY), angle_text(st["th"]), font=self.font_small, fill=blend(GOLD if lit else TEXT, a),
                   anchor="rm")
            d.text((ROW_X1, y0 + FIX_DY), tension_text(st["T"], self.g), font=self.font_small, fill=blend(MUTED, a),
                   anchor="rm")
            for x in man["rail_ticks_m"]:
                d.text((RAIL_X0 + x * self.ppm + RAIL_LABEL_DX, y0 + RAIL_DY + RAIL_LABEL_DY), rail_text(x),
                       font=self.font_tiny, fill=MUTED, anchor="rm")
            if st["phase"] == STOPPED:
                d.text((st["hx"] + ARC_LABEL_DX, y0 + RAIL_DY + ARC_LABEL_DY), arc_text(run["amp"]), font=self.font_tiny,
                       fill=blend(GOLD, a), anchor="lm")
            if lit:
                d.text((W / 2, y0 + EVENT_DY), event_text(man, ev, m), font=self.font, fill=blend(GOLD, a), anchor="mm")
        if hud_alpha > 0.02:
            d.text((W / 2, LEGEND_Y), legend_text(man), font=self.font, fill=blend(TEXT, hud_alpha), anchor="mm")
            d.text((W / 2, CLOCK_Y), clock_text(states["half"]["rt"]), font=self.font_small,
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
    man = json.loads((ROOT / "projects/carrystop/manifest.json").read_text())
    ev = measure(man)
    if "--measure-only" in sys.argv:
        return
    if "--frames" in sys.argv:
        times = [float(v) for v in sys.argv[sys.argv.index("--frames") + 1].split(",")]
        r = Renderer(man, ev)
        (ROOT / "media/carrystop").mkdir(parents=True, exist_ok=True)
        for tv in times:
            Image.fromarray(r.frame_at(int(round(tv * man["fps"])))).save(ROOT / f"media/carrystop/smoke-{tv}.png")
        print("smoke frames: " + ", ".join(f"{tv}" for tv in times))
        return
    Renderer(man, ev).render(ROOT / "media/carrystop/footage.mp4")


if __name__ == "__main__":
    main()
