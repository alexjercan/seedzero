#!/usr/bin/env python3
"""Balloon or dice in a car: which way does the balloon lean?

Side view inside a car that pulls away from rest at a steady a = 100 km/h
per 10 s = 2.7778 m/s^2 after a short throttle ramp. A dice hangs from the
ceiling on a 50 cm string; a helium balloon (30 cm across, 6.4 g with its
gas against 17.0 g of displaced air) is tied to the floor with its centre
50 cm above the anchor. In the car's frame the effective gravity is
g_eff = (-a, -g), backward and down. The dice (theta positive backward):
theta'' = (a cos theta - g sin theta) / L - c theta'. The balloon (phi
positive forward): the cabin air is at rest in the car's frame, so its
pressure gradient lies along g_eff and the buoyancy is -m_air g_eff (up
and forward); with the added mass of half the displaced air and no drag,
(m_b + m_add) L phi'' = (m_air - m_b)(a cos phi - g sin phi) - (m_b +
m_add) L c phi'. Both settle where tan(angle) = a / g, the dice backward
and the balloon forward, whatever the masses. The damping c is a chosen
number; the swing size depends on it, the settled angle does not. The car,
the dice and the balloon are integrated together by RK4 at 10,000 steps a
second, checked against atan(a / g), the closed-form car motion and a
half-step rerun. The launch repeats every cycle_s seconds of video with a
fade to the resting cabin; the cycle divides the scene length, so the
scene is exactly periodic and the last frame equals the first. No slow
motion. Deterministic, no seed.

Measured and printed: the masses and the lift over inertia ratio, the
equilibrium angle against atan(a / g) for both objects, the small-swing
periods, the peaks and the settle times with the chosen damping, the
angles at 4 s, 6 s and the payoff time, the undamped sudden-start peak
against 2 atan(a / g), the peaks at the description damping, the settled
angles at 0.3, 0.5 and 1.0 g, the car's speed and distance at 6 s against
the closed forms, the half-step rerun, the schedule in video time, the
loop and periodicity checks and the on-screen text widths and clearances.

usage: balloon.py [--measure-only] [--frames t1,t2,...]
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
BODY = (58, 66, 80)
BODY_EDGE = (120, 132, 150)
CABIN = (26, 32, 42)
GLASS = (54, 84, 112)
DASHBOARD = (44, 50, 62)
TYRE = (22, 24, 28)
RIM = (150, 158, 170)
ASPHALT = (30, 34, 40)
LANE = (200, 204, 210)
STRING = (222, 226, 232)
PIP = (18, 40, 34)

# Layout: overlay at y 96..130 (captions.py), three title rows at y 186/244/302
# for the first seconds, then the legend at y 236 and the clock at y 290; the
# geometry band y 330..1430 drawn at 2x in one layer: the two header columns
# (label row 40 px under the band top, live readout at 84, settled line at 120),
# the speed row at 210 and 256, the car body from 330 (roof) to 820 (skirt),
# the wheels on the road at 920, the road surface 920..1070; captions at
# caption_y 0.75 (y 1440..1520); the six-line card from y 1572 at a 48 px pitch.
LEGEND_Y, CLOCK_Y = 236, 290
TITLE_Y, TITLE_PITCH = 186, 58
SS = 2
BAND_Y0, BAND_Y1 = 330, 1430
LABEL_DY, LIVE_DY, FIX_DY = 40, 84, 120
SPEED_DY, DIST_DY = 210, 256
ROOF_DY, FLOOR_DY, SKIRT_DY, ROAD_DY, ROAD_BOTTOM_DY = 330, 780, 820, 920, 1070
WHEEL_R, WHEEL_XS = 70, (250, 860)
DICE_ANCHOR_X, BALLOON_ANCHOR_X = 800, 400
ARC_R = 70.0
COL_X0, COL_X1 = 60, 1020
PAYOFF_Y, PAYOFF_PITCH = 1572.0, 48
OBJECTS = ("balloon", "dice")


def blend(col, a: float, base=BG) -> tuple:
    a = max(0.0, min(1.0, a))
    return tuple(int(round(c * a + b * (1 - a))) for c, b in zip(col, base))


def smoothstep(u: float) -> float:
    u = max(0.0, min(1.0, u))
    return u * u * (3.0 - 2.0 * u)


# --- measurement --------------------------------------------------------------
def params(man: dict) -> dict:
    g = man["g"]
    a = man["zero_to_km_h"] / 3.6 / man["zero_to_s"]
    L = man["string_m"]
    R = man["balloon_radius_m"]
    vol = 4.0 / 3.0 * math.pi * R ** 3
    m_air = man["air_density_kg_m3"] * vol
    m_b = man["balloon_mass_g"] / 1000.0
    m_add = man["added_mass_fraction"] * m_air
    k_lift = (m_air - m_b) / (m_b + m_add)
    return {"g": g, "a": a, "L": L, "R": R, "vol": vol, "m_air": m_air, "m_b": m_b, "m_add": m_add, "k_lift": k_lift,
            "eq": math.atan(a / g), "g_eff": math.hypot(a, g)}


def throttle(t: float, a: float, ramp: float) -> float:
    if t <= 0.0:
        return 0.0
    if ramp <= 0.0 or t >= ramp:
        return a
    return a * t / ramp


def deriv(t: float, s: np.ndarray, p: dict, a_max: float, c: float, ramp: float) -> np.ndarray:
    th, w, ph, u, _x, _v = s
    a = throttle(t, a_max, ramp)
    g, L, k = p["g"], p["L"], p["k_lift"]
    return np.array([w, (a * math.cos(th) - g * math.sin(th)) / L - c * w,
                     u, k * (a * math.cos(ph) - g * math.sin(ph)) / L - c * u,
                     _v, a])


def simulate(p: dict, a_max: float, c: float, ramp: float, steps: int, t_end: float) -> dict:
    """RK4 on (theta, theta', phi, phi', x, v) from rest at t = 0 (the throttle) to t_end."""
    dt = 1.0 / steps
    n = int(round(t_end * steps))
    out = np.zeros((n + 1, 6))
    s = np.zeros(6)
    for i in range(1, n + 1):
        t = (i - 1) * dt
        k1 = deriv(t, s, p, a_max, c, ramp)
        k2 = deriv(t + 0.5 * dt, s + 0.5 * dt * k1, p, a_max, c, ramp)
        k3 = deriv(t + 0.5 * dt, s + 0.5 * dt * k2, p, a_max, c, ramp)
        k4 = deriv(t + dt, s + dt * k3, p, a_max, c, ramp)
        s = s + dt * (k1 + 2.0 * k2 + 2.0 * k3 + k4) / 6.0
        out[i] = s
    t = np.arange(n + 1) * dt
    return {"t": t, "theta": out[:, 0], "omega": out[:, 1], "phi": out[:, 2], "phidot": out[:, 3],
            "x": out[:, 4], "v": out[:, 5], "dt": dt, "a": a_max, "c": c, "ramp": ramp}


def extremes(t: np.ndarray, y: np.ndarray, yd: np.ndarray, n_max: int = 4) -> list[tuple[float, float]]:
    """The first turning points (t, y) of y after t = 0, from the sign changes of yd, refined linearly."""
    out = []
    started = False
    for i in range(1, len(t)):
        if not started:
            started = abs(yd[i]) > 1e-9
            continue
        if yd[i - 1] * yd[i] < 0.0:
            f = yd[i - 1] / (yd[i - 1] - yd[i])
            out.append((t[i - 1] + f * (t[i] - t[i - 1]), y[i - 1] + f * (y[i] - y[i - 1])))
            if len(out) >= n_max:
                break
    return out


def settle_time(t: np.ndarray, y: np.ndarray, eq: float, tol: float) -> float:
    """The last time |y - eq| reaches tol (y and eq in radians, tol in radians)."""
    idx = np.nonzero(np.abs(y - eq) >= tol)[0]
    return float(t[idx[-1]]) if len(idx) else 0.0


def at(run: dict, key: str, r: float) -> float:
    return float(np.interp(r, run["t"], run[key]))


def car_closed(a: float, ramp: float, t: float) -> tuple[float, float]:
    """(x, v) of the car t seconds after the throttle with a linear ramp to a over ramp seconds."""
    if t <= ramp:
        return a * t ** 3 / (6.0 * ramp), a * t * t / (2.0 * ramp)
    v_r, x_r = a * ramp / 2.0, a * ramp * ramp / 6.0
    d = t - ramp
    return x_r + v_r * d + 0.5 * a * d * d, v_r + a * d


def measure(man: dict) -> dict:
    p = params(man)
    g, a, L, R = p["g"], p["a"], p["L"], p["R"]
    c, ramp = man["damping_per_s"], man["throttle_ramp_s"]
    steps, T = man["steps_per_second"], man["sim_end_s"]
    P, D, fps, F, go = man["cycle_s"], man["scene_duration"], man["fps"], man["reset_fade"], man["go_at"]
    cycles = D / P
    assert abs(cycles - round(cycles)) < 1e-9, "the cycle must divide the scene length"
    for key in ("cycle_s", "go_at", "first_cycle_at", "reset_fade"):
        assert abs(man[key] * fps - round(man[key] * fps)) < 1e-9, f"{key} must be a whole number of frames"
    eq_deg = math.degrees(p["eq"])
    print(f"setup: side view inside a car that pulls away from rest at a = {man['zero_to_km_h']:g} km/h in "
          f"{man['zero_to_s']:g} s = {a:.4f} m/s^2 ({a / g:.4f} g) after a linear throttle ramp of {ramp:g} s; a dice "
          f"(a point mass, drawn {man['dice_side_m'] * 100:g} cm across) hangs from the ceiling on a {L * 100:g} cm "
          f"string; a helium balloon of radius {R * 100:g} cm ({2 * R * 100:g} cm across, volume {p['vol'] * 1000:.2f} "
          f"litres) is tied to the floor with its centre {L * 100:g} cm above the anchor; balloon plus gas "
          f"{p['m_b'] * 1000:g} g, displaced air {man['air_density_kg_m3']:g} kg/m^3 x volume = {p['m_air'] * 1000:.2f} "
          f"g, added mass {man['added_mass_fraction']:g} of the air = {p['m_add'] * 1000:.2f} g, no drag; in the car's "
          f"frame g_eff = (-a, -g), {p['g_eff']:.4f} m/s^2 tilted {eq_deg:.2f} degrees back from the vertical; dice: "
          f"theta'' = (a cos theta - g sin theta) / L - c theta' (theta positive backward); balloon: (m_b + m_add) L "
          f"phi'' = (m_air - m_b)(a cos phi - g sin phi) - (m_b + m_add) L c phi' (phi positive forward); damping "
          f"c = {c:g} per second, a chosen number; g = {g:g} m/s^2; RK4 on (theta, theta', phi, phi', x, v) at "
          f"{steps} steps per second (dt = {1.0 / steps:.0e} s) for {T:g} s; {P:g} s cycle ({P * fps:.0f} frames) "
          f"with the throttle {go:g} s into the cycle, {cycles:.0f} cycles in {D:g} s, no slow motion; drawn at "
          f"{man['px_per_m']:g} px per metre; deterministic, no seed")
    print(f"lift over inertia: (m_air - m_b) / (m_b + m_add) = ({p['m_air'] * 1000:.2f} - {p['m_b'] * 1000:g}) / "
          f"({p['m_b'] * 1000:g} + {p['m_add'] * 1000:.2f}) = {p['k_lift']:.3f}; the balloon's net lift is "
          f"{(p['m_air'] - p['m_b']) * g * 1000:.1f} mN, {p['m_air'] / p['m_b']:.2f} times its weight in displaced air")
    print(f"equilibrium: both settle where tan(angle) = a / g = {a / g:.5f}: atan(a / g) = {eq_deg:.2f} degrees "
          f"({eq_deg:.4f}), the dice {eq_deg:.2f} degrees back and the balloon {eq_deg:.2f} degrees forward; the angle "
          f"does not depend on the masses, the string length or the damping")
    T0_d = 2.0 * math.pi * math.sqrt(L / g)
    T0_b = 2.0 * math.pi * math.sqrt(L / (p["k_lift"] * g))
    Te_d = 2.0 * math.pi * math.sqrt(L / p["g_eff"])
    Te_b = 2.0 * math.pi * math.sqrt(L / (p["k_lift"] * p["g_eff"]))
    w_d, w_b = math.sqrt(p["g_eff"] / L), math.sqrt(p["k_lift"] * p["g_eff"] / L)
    Td_d = 2.0 * math.pi / math.sqrt(w_d ** 2 - c * c / 4.0)
    Td_b = 2.0 * math.pi / math.sqrt(w_b ** 2 - c * c / 4.0)
    print(f"small-swing periods: at rest 2 pi sqrt(L / g) = {T0_d:.3f} s (dice) and 2 pi sqrt(L / (k g)) = {T0_b:.3f} s "
          f"(balloon, k = {p['k_lift']:.3f}); about the tilted equilibrium (g_eff {p['g_eff']:.4f}) {Te_d:.3f} s and "
          f"{Te_b:.3f} s undamped, {Td_d:.3f} s and {Td_b:.3f} s with c = {c:g} per second (2 pi / sqrt(w0^2 - c^2 / 4))")
    run = simulate(p, a, c, ramp, steps, T)
    ev = {"p": p, "run": run, "eq_deg": eq_deg}
    tol = math.radians(man["settle_deg"])
    payoff_r = man["payoff_t"] - (man["first_cycle_at"] + go) - P * math.floor((man["payoff_t"] - man["first_cycle_at"]) / P)
    for name, key, kd, sgn_word in (("dice", "theta", "omega", "back"), ("balloon", "phi", "phidot", "forward")):
        ext = extremes(run["t"], run[key], run[kd])
        deg = [(t_, math.degrees(y_)) for t_, y_ in ext]
        st = settle_time(run["t"], run[key], p["eq"], tol)
        a4, a6, ap = (math.degrees(at(run, key, r)) for r in (4.0, 6.0, payoff_r))
        final = math.degrees(run[key][-1])
        ev[f"{name}_peaks"] = deg
        ev[f"{name}_settle"] = st
        ev[f"{name}_payoff_deg"] = ap
        print(f"{name}: RK4 with c = {c:g}: swings {sgn_word} to a first peak of {deg[0][1]:.2f} degrees at {deg[0][0]:.3f} s "
              f"after the throttle, back to {deg[1][1]:.2f} at {deg[1][0]:.3f} s, {deg[2][1]:.2f} at {deg[2][0]:.3f} s, "
              f"{deg[3][1]:.2f} at {deg[3][0]:.3f} s (first peak to second peak {deg[2][0] - deg[0][0]:.3f} s); "
              f"{a4:.2f} degrees at 4 s ({a4 - eq_deg:+.2f} from atan(a / g)), {a6:.2f} at 6 s ({a6 - eq_deg:+.2f}), "
              f"{final:.4f} at {T:g} s ({final - eq_deg:+.4f}); last more than {man['settle_deg']:g} degrees from "
              f"{eq_deg:.2f} at {st:.2f} s; at the payoff time ({man['payoff_t']:g} s of video, {payoff_r:.2f} s after "
              f"the throttle) {ap:.2f} degrees {sgn_word}; never crosses the vertical the other way: min "
              f"{math.degrees(run[key].min()):.2f} degrees")
    # The car.
    x6, v6 = at(run, "x", 6.0), at(run, "v", 6.0)
    cx6, cv6 = car_closed(a, ramp, 6.0)
    t100 = ramp / 2.0 + man["zero_to_km_h"] / 3.6 / a
    t60 = ramp / 2.0 + 60.0 / 3.6 / a
    xT, vT = at(run, "x", T), at(run, "v", T)
    print(f"car: RK4: {v6 * 3.6:.2f} km/h ({v6:.4f} m/s) and {x6:.2f} m at 6 s (closed form with the {ramp:g} s ramp "
          f"{cv6 * 3.6:.2f} km/h, {cx6:.2f} m; diffs {abs(v6 - cv6):.1e} m/s, {abs(x6 - cx6):.1e} m; with no ramp "
          f"{a * 6 * 3.6:.2f} km/h and {0.5 * a * 36:.2f} m); it passes 60 km/h at {t60:.2f} s and would reach "
          f"{man['zero_to_km_h']:g} km/h at {t100:.2f} s ({man['zero_to_s']:g} s of steady pull plus half the ramp); "
          f"{vT * 3.6:.1f} km/h and {xT:.1f} m at {T:g} s, the end of the run")
    # Undamped sudden start.
    sud = simulate(p, a, 0.0, 0.0, steps, 3.0)
    pk_d = extremes(sud["t"], sud["theta"], sud["omega"], 1)[0]
    pk_b = extremes(sud["t"], sud["phi"], sud["phidot"], 1)[0]
    ev["sudden"] = (math.degrees(pk_d[1]), math.degrees(pk_b[1]))
    rmp = simulate(p, a, 0.0, ramp, steps, 3.0)
    rd = extremes(rmp["t"], rmp["theta"], rmp["omega"], 1)[0]
    rb = extremes(rmp["t"], rmp["phi"], rmp["phidot"], 1)[0]
    print(f"undamped sudden start (c = 0, no ramp): the dice peaks at {math.degrees(pk_d[1]):.2f} degrees at "
          f"{pk_d[0]:.3f} s and the balloon at {math.degrees(pk_b[1]):.2f} degrees at {pk_b[0]:.3f} s (closed form "
          f"2 atan(a / g) = {2 * eq_deg:.2f}; diffs {math.degrees(pk_d[1]) - 2 * eq_deg:+.1e}, "
          f"{math.degrees(pk_b[1]) - 2 * eq_deg:+.1e} degrees); with the {ramp:g} s ramp and no damping the peaks are "
          f"{math.degrees(rd[1]):.2f} (dice, at {rd[0]:.3f} s) and {math.degrees(rb[1]):.2f} (balloon, at {rb[0]:.3f} s) "
          f"degrees, and neither ever settles")
    # Other damping, for the description.
    c2 = man["description_damping_per_s"]
    r2 = simulate(p, a, c2, ramp, steps, T)
    d2 = extremes(r2["t"], r2["theta"], r2["omega"], 2)
    b2 = extremes(r2["t"], r2["phi"], r2["phidot"], 2)
    ev["c1_peaks"] = (math.degrees(d2[0][1]), math.degrees(b2[0][1]))
    print(f"for the description (damping c = {c2:g} per second, same ramp): the dice peaks at {math.degrees(d2[0][1]):.2f} "
          f"degrees at {d2[0][0]:.3f} s and the balloon at {math.degrees(b2[0][1]):.2f} at {b2[0][0]:.3f} s; "
          f"{math.degrees(at(r2, 'theta', 4.0)):.2f} and {math.degrees(at(r2, 'phi', 4.0)):.2f} degrees at 4 s, "
          f"{math.degrees(at(r2, 'theta', 6.0)):.2f} and {math.degrees(at(r2, 'phi', 6.0)):.2f} at 6 s; last more than "
          f"{man['settle_deg']:g} degrees from {eq_deg:.2f} at {settle_time(r2['t'], r2['theta'], p['eq'], tol):.2f} s "
          f"(dice) and {settle_time(r2['t'], r2['phi'], p['eq'], tol):.2f} s (balloon)")
    # Other accelerations.
    descr = []
    ev["accels"] = {}
    for gs in man["description_accels_g"]:
        ag = gs * g
        rg = simulate(p, ag, c, ramp, steps, 8.0)
        cf = math.degrees(math.atan(gs))
        ev["accels"][gs] = cf
        descr.append(f"{gs:g} g ({ag:.3f} m/s^2): atan = {cf:.2f} degrees, RK4 at 8 s {math.degrees(rg['theta'][-1]):.2f} "
                     f"(dice, back) and {math.degrees(rg['phi'][-1]):.2f} (balloon, forward), peaks "
                     f"{math.degrees(extremes(rg['t'], rg['theta'], rg['omega'], 1)[0][1]):.1f} and "
                     f"{math.degrees(extremes(rg['t'], rg['phi'], rg['phidot'], 1)[0][1]):.1f}")
    print("for the description (other pulls, same strings, same damping): " + "; ".join(descr))
    # Half-step rerun.
    half = simulate(p, a, c, ramp, 2 * steps, T)
    hd = extremes(half["t"], half["theta"], half["omega"], 1)[0]
    hb = extremes(half["t"], half["phi"], half["phidot"], 1)[0]
    print(f"check at half the time step ({2 * steps} steps per second): dice peak {math.degrees(hd[1]):.6f} degrees "
          f"({math.degrees(hd[1]) - ev['dice_peaks'][0][1]:+.1e}) at {hd[0]:.6f} s ({hd[0] - ev['dice_peaks'][0][0]:+.1e}), "
          f"{math.degrees(at(half, 'theta', 6.0)):.6f} at 6 s ({math.degrees(at(half, 'theta', 6.0) - at(run, 'theta', 6.0)):+.1e}); "
          f"balloon peak {math.degrees(hb[1]):.6f} degrees ({math.degrees(hb[1]) - ev['balloon_peaks'][0][1]:+.1e}) at "
          f"{hb[0]:.6f} s ({hb[0] - ev['balloon_peaks'][0][0]:+.1e}), {math.degrees(at(half, 'phi', 6.0)):.6f} at 6 s "
          f"({math.degrees(at(half, 'phi', 6.0) - at(run, 'phi', 6.0)):+.1e}); car at 6 s {at(half, 'x', 6.0):.6f} m "
          f"({at(half, 'x', 6.0) - x6:+.1e})")
    # Schedule.
    t0 = man["first_cycle_at"]
    starts = [t0 + k * P for k in range(int(round(cycles)) + 1)]
    ev["cycles"] = int(round(cycles))

    def lst(off_: float) -> str:
        return ", ".join(f"{s + off_:.2f}" for s in starts if 0.0 <= s + off_ < D)

    print(f"schedule (video time, real speed): cycles of {P:g} s start at " + ", ".join(f"{s:.2f}" for s in starts)
          + f" s; the throttle {go:g} s into each cycle at {lst(go)} s; the dice peaks at {lst(go + ev['dice_peaks'][0][0])} s "
          f"and the balloon at {lst(go + ev['balloon_peaks'][0][0])} s; the settled labels light at "
          f"{lst(go + ev['dice_settle'])} s (dice) and {lst(go + ev['balloon_settle'])} s (balloon); the run fades out "
          f"over {P - F:.2f} to {P - F / 2:.2f} s of each cycle and the resting cabin fades in over {P - F / 2:.2f} to "
          f"{P:.2f} s, the car at {at(run, 'v', P - F - go) * 3.6:.1f} km/h and {at(run, 'x', P - F - go):.1f} m when "
          f"the fade starts; on the first frame the cycle is 0 s in: both at rest, hanging straight, the car still; "
          f"title until {man['title_until']:g} s; payoff card from {man['payoff_t']:g} s; the title fades back in over "
          f"the last {man['loop_fade']:g} s and the last frame repeats the first (the scene is periodic: {D:g} s holds "
          f"exactly {cycles:.0f} cycles)")
    # Text widths.
    font = os.environ["SEED_ZERO_FONT"]
    f28, f34, f40, f48, f56 = (ImageFont.truetype(font, n) for n in (28, 34, 40, 48, 56))
    widths = {"overlay@34": (f34, man["overlay"])}
    for j, line in enumerate(man["title"].split("|")):
        widths[f"title line {j + 1}@56"] = (f56, line)
    widths["legend@40"] = (f40, legend_text(man))
    widths["clock@28"] = (f28, clock_text(1.2345))
    widths["clock rest@28"] = (f28, clock_text(-1.0))
    for name in OBJECTS:
        widths[f"label {name}@40"] = (f40, name)
        widths[f"live {name}@28"] = (f28, live_text(-23.45 if name == "dice" else 23.45, name))
        widths[f"live rest@28"] = (f28, live_text(0.0, name))
        widths[f"settled {name}@28"] = (f28, settled_text(eq_deg, name))
    widths["speed@48"] = (f48, speed_text(120.0))
    widths["distance@28"] = (f28, dist_text(123.4))
    for j, line in enumerate(payoff_lines(man, ev)):
        widths[f"payoff line {j + 1}@40"] = (f40, line)
    print("text widths: " + ", ".join(f"{k} {f.getlength(s):.0f} px" for k, (f, s) in widths.items()))
    assert all(f.getlength(s) < 950 for f, s in widths.values()), "a text line is wider than 950 px"
    # Layout clearances.
    ppm = man["px_per_m"]
    Lpx = L * ppm
    left_end = COL_X0 + max(f28.getlength(live_text(23.45, "balloon")), f28.getlength(settled_text(eq_deg, "balloon")))
    right_start = COL_X1 - max(f28.getlength(live_text(-23.45, "dice")), f28.getlength(settled_text(eq_deg, "dice")))
    peak_b = max(math.degrees(abs(x_)) for x_ in run["phi"])
    peak_d = max(math.degrees(abs(x_)) for x_ in run["theta"])
    top_b = FLOOR_DY - Lpx * math.cos(math.radians(peak_b)) - R * ppm
    bottom_d = ROOF_DY + Lpx * math.cos(math.radians(peak_d)) + man["dice_side_m"] * ppm * 0.71
    fwd_b = BALLOON_ANCHOR_X + Lpx * math.sin(math.radians(peak_b)) + R * ppm
    back_d = DICE_ANCHOR_X - Lpx * math.sin(math.radians(peak_d)) - man["dice_side_m"] * ppm * 0.71
    print(f"layout: the left column ends at x {left_end:.0f} px and the right column starts at {right_start:.0f} px; the "
          f"rows end {FIX_DY + 14} px under the band top, the speed row spans {SPEED_DY - 24} to {DIST_DY + 14} px and the "
          f"roof is at {ROOF_DY} px; the balloon's top at its widest swing ({peak_b:.2f} degrees) is {top_b:.0f} px under "
          f"the band top, {top_b - ROOF_DY:.0f} px under the roof; the dice's lowest point ({peak_d:.2f} degrees) is "
          f"{bottom_d:.0f} px, {FLOOR_DY - bottom_d:.0f} px above the floor; the balloon's front at its widest is x "
          f"{fwd_b:.0f} px and the dice's back x {back_d:.0f} px, {back_d - fwd_b:.0f} px apart; the road ends "
          f"{ROAD_BOTTOM_DY} px under the band top, {BAND_Y1 - BAND_Y0 - ROAD_BOTTOM_DY} px above the band's bottom; "
          f"the third title row ends at y {TITLE_Y + 2 * TITLE_PITCH + 28} px against the band top at {BAND_Y0}")
    assert left_end < right_start - 40, "the header columns collide"
    assert top_b - ROOF_DY > 20 and FLOOR_DY - bottom_d > 20 and back_d - fwd_b > 40, "the objects meet the cabin"
    assert DIST_DY + 14 < ROOF_DY - 20 and FIX_DY + 14 < SPEED_DY - 24 - 10, "the header rows meet the roof"
    return ev


def legend_text(man: dict) -> str:
    return f"0 to {man['zero_to_km_h']:g} km/h in {man['zero_to_s']:g} s, damping {man['damping_per_s']:g}/s"


def clock_text(r: float) -> str:
    return "at rest before the throttle" if r < 0.0 else f"{r:.2f} s after the throttle"


def live_text(deg: float, name: str) -> str:
    """deg is signed the object's own way: positive back for the dice, positive forward for the balloon."""
    if abs(deg) < 0.05:
        return "0.0 degrees, hanging straight"
    own = "back" if name == "dice" else "forward"
    other = "forward" if name == "dice" else "back"
    return f"{abs(deg):.1f} degrees {own if deg > 0 else other}"


def settled_text(eq_deg: float, name: str) -> str:
    return f"settles {eq_deg:.1f} degrees {'back' if name == 'dice' else 'forward'}"


def speed_text(kmh: float) -> str:
    return f"{kmh:.0f} km/h"


def dist_text(m: float) -> str:
    return f"{m:.0f} m since the start"


def payoff_lines(man: dict, ev: dict) -> list[str]:
    acc = ev["accels"]
    text = man["payoff_text"].format(eq=ev["eq_deg"], m_air=ev["p"]["m_air"] * 1000, a03=acc[0.3], a05=acc[0.5],
                                     a10=acc[1.0], pk_d=ev["dice_peaks"][0][1], pk_b=ev["balloon_peaks"][0][1])
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
        self.font_num = ImageFont.truetype(font, 48)
        self.ppm = float(man["px_per_m"])
        self.P_f = int(round(man["cycle_s"] * self.fps))
        self.c0_f = int(round(man["first_cycle_at"] * self.fps))
        self.go, self.F, self.P = man["go_at"], man["reset_fade"], man["cycle_s"]
        self.run = ev["run"]
        self.eq = ev["p"]["eq"]
        self.Lpx = man["string_m"] * self.ppm
        self.Rpx = man["balloon_radius_m"] * self.ppm
        self.settle = {"dice": ev["dice_settle"], "balloon": ev["balloon_settle"]}

    def phase(self, f: int) -> tuple[int, float]:
        k, tau_f = divmod(f - self.c0_f, self.P_f)
        return k, tau_f / self.fps

    @staticmethod
    def L(x: float, y: float) -> tuple[float, float]:
        """Layer (2x) pixel of a band-local point, rounded to 1e-4 px so equal states draw equal pixels."""
        return round(x * SS, 4), round(y * SS, 4)

    def dashed(self, d, p0, p1, fill, width: int, dash: float, gap: float) -> None:
        (x0, y0), (x1, y1) = self.L(*p0), self.L(*p1)
        length = math.hypot(x1 - x0, y1 - y0)
        if length < 1e-9:
            return
        ux, uy = (x1 - x0) / length, (y1 - y0) / length
        s = 0.0
        while s < length:
            e = min(length, s + dash * SS)
            d.line((x0 + ux * s, y0 + uy * s, x0 + ux * e, y0 + uy * e), fill=fill, width=width * SS)
            s = e + gap * SS

    def state(self, r: float) -> dict:
        if r < 0.0:
            return {"theta": 0.0, "phi": 0.0, "x": 0.0, "v": 0.0, "r": r}
        return {"theta": at(self.run, "theta", r), "phi": at(self.run, "phi", r), "x": at(self.run, "x", r),
                "v": at(self.run, "v", r), "r": r}

    # --- static car -----------------------------------------------------------
    def draw_car(self, d: ImageDraw.ImageDraw) -> None:
        L = self.L
        # Road surface and its edge line.
        d.rectangle((*L(0, ROAD_DY), *L(W, ROAD_BOTTOM_DY)), fill=ASPHALT)
        d.line((*L(0, ROAD_DY), *L(W, ROAD_DY)), fill=blend(LANE, 0.35, ASPHALT), width=2 * SS)
        # Body: a cabin cutaway, the car facing right.
        body = [(60, 700), (60, 600), (130, 560), (240, ROOF_DY + 20), (300, ROOF_DY), (840, ROOF_DY), (900, ROOF_DY + 20),
                (1000, 560), (1040, 600), (1040, 700), (1040, SKIRT_DY), (60, SKIRT_DY)]
        d.polygon([L(x, y) for x, y in body], fill=BODY, outline=BODY_EDGE, width=3 * SS)
        # The cabin interior, open to the viewer, from the rear window to the dashboard.
        cabin = [(150, 580), (250, ROOF_DY + 32), (296, ROOF_DY + 14), (844, ROOF_DY + 14), (890, ROOF_DY + 32),
                 (950, 560), (950, FLOOR_DY), (150, FLOOR_DY)]
        d.polygon([L(x, y) for x, y in cabin], fill=CABIN)
        # Windshield glass at the front, above the dashboard.
        glass = [(900, ROOF_DY + 20), (950, 560), (1000, 560), (1010, 600), (950, 600)]
        d.polygon([L(x, y) for x, y in glass], fill=GLASS)
        # Dashboard block.
        d.rectangle((*L(950, 560), *L(1010, FLOOR_DY)), fill=DASHBOARD)
        d.line((*L(950, 560), *L(1010, 560)), fill=BODY_EDGE, width=2 * SS)
        # Floor line.
        d.line((*L(150, FLOOR_DY), *L(1010, FLOOR_DY)), fill=BODY_EDGE, width=3 * SS)
        # Rear-view mirror on a stalk from the roof, by the windshield.
        d.line((*L(880, ROOF_DY + 14), *L(880, ROOF_DY + 50)), fill=BODY_EDGE, width=3 * SS)
        d.rounded_rectangle((*L(852, ROOF_DY + 50), *L(908, ROOF_DY + 66)), radius=4 * SS, fill=GLASS, outline=BODY_EDGE,
                            width=SS)
        # Wheels.
        for wx in WHEEL_XS:
            cx, cy = L(wx, ROAD_DY - WHEEL_R)
            rr = WHEEL_R * SS
            d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), fill=TYRE, outline=BODY_EDGE, width=2 * SS)
            r2 = 0.55 * rr
            d.ellipse((cx - r2, cy - r2, cx + r2, cy + r2), fill=RIM)
            r3 = 0.12 * rr
            d.ellipse((cx - r3, cy - r3, cx + r3, cy + r3), fill=TYRE)

    # --- dynamic scene --------------------------------------------------------
    def draw_scene(self, d: ImageDraw.ImageDraw, tau: float, a: float) -> dict:
        man = self.man
        r = tau - self.go
        st = self.state(r)
        st["alpha"] = a
        L = self.L
        # Road marks sliding left at the car's speed, smeared over one frame's travel (motion blur, no strobing).
        period, dash = man["dash_period_m"] * self.ppm, man["dash_m"] * self.ppm
        travel = st["v"] * self.ppm / self.fps
        off = (-st["x"] * self.ppm) % period
        col = blend(LANE, a * dash / (dash + travel) * 0.8, ASPHALT)
        xx = off - period
        while xx < W:
            x0, x1 = max(0.0, xx), min(float(W), xx + dash + travel)
            if x1 > x0:
                d.rectangle((*L(x0, ROAD_DY + 68), *L(x1, ROAD_DY + 82)), fill=col)
            xx += period
        # Plumb lines through both anchors.
        mut = blend(MUTED, 0.45 * a, CABIN)
        self.dashed(d, (DICE_ANCHOR_X, ROOF_DY + 14), (DICE_ANCHOR_X, ROOF_DY + 14 + self.Lpx + 50), mut, 2, 10, 8)
        self.dashed(d, (BALLOON_ANCHOR_X, FLOOR_DY), (BALLOON_ANCHOR_X, FLOOR_DY - self.Lpx - self.Rpx - 40), mut, 2, 10, 8)
        # Settled lines: a gold dashed line at the equilibrium tilt once each object has settled.
        lit = {}
        for name in OBJECTS:
            lit[name] = smoothstep((r - self.settle[name]) / 0.3) if r > 0.0 else 0.0
        eq = self.eq
        if lit["dice"] > 0.0:
            gx, gy = DICE_ANCHOR_X - (self.Lpx + 50) * math.sin(eq), ROOF_DY + 14 + (self.Lpx + 50) * math.cos(eq)
            self.dashed(d, (DICE_ANCHOR_X, ROOF_DY + 14), (gx, gy), blend(GOLD, 0.8 * a * lit["dice"], CABIN), 3, 12, 8)
        if lit["balloon"] > 0.0:
            ln = self.Lpx + self.Rpx + 40
            gx, gy = BALLOON_ANCHOR_X + ln * math.sin(eq), FLOOR_DY - ln * math.cos(eq)
            self.dashed(d, (BALLOON_ANCHOR_X, FLOOR_DY), (gx, gy), blend(GOLD, 0.8 * a * lit["balloon"], CABIN), 3, 12, 8)
        # Angle arcs from the plumb line to the string.
        th, ph = st["theta"], st["phi"]
        ax, ay = L(DICE_ANCHOR_X, ROOF_DY + 14)
        Rp = ARC_R * SS
        if abs(th) > 1e-4:
            s0, s1 = sorted((90.0, 90.0 + math.degrees(th)))
            d.arc((ax - Rp, ay - Rp, ax + Rp, ay + Rp), start=s0, end=s1, fill=blend(TEAL, 0.7 * a, CABIN), width=4 * SS)
        bx, by = L(BALLOON_ANCHOR_X, FLOOR_DY)
        if abs(ph) > 1e-4:
            s0, s1 = sorted((270.0, 270.0 + math.degrees(ph)))
            d.arc((bx - Rp, by - Rp, bx + Rp, by + Rp), start=s0, end=s1, fill=blend(CORAL, 0.7 * a, CABIN), width=4 * SS)
        # The dice: string from the ceiling, a cube turned with the string.
        dx, dy = DICE_ANCHOR_X - self.Lpx * math.sin(th), ROOF_DY + 14 + self.Lpx * math.cos(th)
        d.line((*L(DICE_ANCHOR_X, ROOF_DY + 14), *L(dx, dy)), fill=blend(STRING, a, CABIN), width=2 * SS)
        hs = man["dice_side_m"] * self.ppm / 2.0
        ca, sa = math.cos(th), math.sin(th)

        def rot(px: float, py: float) -> tuple[float, float]:
            return L(dx + px * ca + py * sa, dy - px * sa + py * ca)

        d.polygon([rot(-hs, -hs), rot(hs, -hs), rot(hs, hs), rot(-hs, hs)], fill=blend(TEAL, a, CABIN),
                  outline=blend(WHITE, 0.6 * a, CABIN), width=SS)
        pr = 2.6 * SS
        for px, py in ((-hs * 0.5, -hs * 0.5), (hs * 0.5, -hs * 0.5), (0.0, 0.0), (-hs * 0.5, hs * 0.5), (hs * 0.5, hs * 0.5)):
            qx, qy = rot(px, py)
            d.ellipse((qx - pr, qy - pr, qx + pr, qy + pr), fill=blend(PIP, a, CABIN))
        # The balloon: string from the floor, a sphere with a highlight and a knot.
        cx, cy = BALLOON_ANCHOR_X + self.Lpx * math.sin(ph), FLOOR_DY - self.Lpx * math.cos(ph)
        kx, ky = BALLOON_ANCHOR_X + (self.Lpx - self.Rpx) * math.sin(ph), FLOOR_DY - (self.Lpx - self.Rpx) * math.cos(ph)
        d.line((*L(BALLOON_ANCHOR_X, FLOOR_DY), *L(kx, ky)), fill=blend(STRING, a, CABIN), width=2 * SS)
        qx, qy = L(cx, cy)
        rr = self.Rpx * SS
        d.ellipse((qx - rr, qy - rr, qx + rr, qy + rr), fill=blend(CORAL, a, CABIN), outline=blend(CORAL, 0.6 * a, CABIN),
                  width=SS)
        hr = rr * 0.22
        hx, hy = qx - rr * 0.38, qy - rr * 0.42
        d.ellipse((hx - hr, hy - hr * 1.4, hx + hr, hy + hr * 1.4), fill=blend(WHITE, 0.55 * a, blend(CORAL, a, CABIN)))
        kr = 5 * SS
        kx2, ky2 = L(kx, ky)
        d.polygon([(kx2, ky2 - kr), (kx2 - kr, ky2 + kr), (kx2 + kr, ky2 + kr)], fill=blend(CORAL, 0.85 * a, CABIN))
        # Anchor knots.
        for px_, py_ in ((DICE_ANCHOR_X, ROOF_DY + 14), (BALLOON_ANCHOR_X, FLOOR_DY)):
            zx, zy = L(px_, py_)
            d.ellipse((zx - 4 * SS, zy - 4 * SS, zx + 4 * SS, zy + 4 * SS), fill=blend(TEXT, a, CABIN))
        st["lit"] = lit
        return st

    def draw_band(self, layer: Image.Image, f: int) -> dict:
        d = ImageDraw.Draw(layer)
        self.draw_car(d)
        k, tau = self.phase(f)
        F, P = self.F, self.P
        a_old = 1.0 if tau <= P - F else max(0.0, (P - F / 2.0 - tau) / (F / 2.0))
        st = self.draw_scene(d, tau, a_old) if a_old > 0.0 else None
        if tau >= P - F / 2.0:
            a_new = (tau - (P - F / 2.0)) / (F / 2.0)
            st_new = self.draw_scene(d, tau - P, a_new)
            if st is None or a_new >= 0.5:
                st = st_new
        st["k"] = k
        return st

    def draw_text(self, d: ImageDraw.ImageDraw, st: dict, hud_alpha: float) -> None:
        man, ev = self.man, self.ev
        a = st["alpha"]
        y0 = BAND_Y0
        angles = {"dice": math.degrees(st["theta"]), "balloon": math.degrees(st["phi"])}
        cols = {"dice": TEAL, "balloon": CORAL}
        for name, x, anchor in (("balloon", COL_X0, "lm"), ("dice", COL_X1, "rm")):
            lit = st["lit"][name]
            d.text((x, y0 + LABEL_DY), name, font=self.font, fill=cols[name], anchor=anchor)
            d.text((x, y0 + LIVE_DY), live_text(angles[name], name), font=self.font_small,
                   fill=blend(blend(GOLD, lit, TEXT), a), anchor=anchor)
            if hud_alpha > 0.02:
                d.text((x, y0 + FIX_DY), settled_text(ev["eq_deg"], name), font=self.font_small,
                       fill=blend(GOLD, (0.25 + 0.75 * lit * a) * hud_alpha), anchor=anchor)
        d.text((W / 2, y0 + SPEED_DY), speed_text(st["v"] * 3.6), font=self.font_num, fill=blend(TEXT, a), anchor="mm")
        d.text((W / 2, y0 + DIST_DY), dist_text(st["x"]), font=self.font_small, fill=blend(MUTED, a), anchor="mm")
        if hud_alpha > 0.02:
            d.text((W / 2, LEGEND_Y), legend_text(man), font=self.font, fill=blend(TEXT, hud_alpha), anchor="mm")
            d.text((W / 2, CLOCK_Y), clock_text(st["r"]), font=self.font_small, fill=blend(MUTED, hud_alpha), anchor="mm")

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
        layer = Image.new("RGB", (W * SS, (BAND_Y1 - BAND_Y0) * SS), BG)
        st = self.draw_band(layer, f)
        img.paste(layer.reduce(SS), (0, BAND_Y0))
        d = ImageDraw.Draw(img)
        self.draw_text(d, st, hud_alpha)
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
        wrap = self.live_frame(total, title_alpha=1.0, hud_alpha=0.0)
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
    man = json.loads((ROOT / "projects/balloon/manifest.json").read_text())
    ev = measure(man)
    if "--measure-only" in sys.argv:
        return
    if "--frames" in sys.argv:
        times = [float(v) for v in sys.argv[sys.argv.index("--frames") + 1].split(",")]
        r = Renderer(man, ev)
        (ROOT / "media/balloon").mkdir(parents=True, exist_ok=True)
        for tv in times:
            Image.fromarray(r.frame_at(int(round(tv * man["fps"])))).save(ROOT / f"media/balloon/smoke-{tv}.png")
        print("smoke frames: " + ", ".join(f"{tv}" for tv in times))
        return
    Renderer(man, ev).render(ROOT / "media/balloon/footage.mp4")


if __name__ == "__main__":
    main()
