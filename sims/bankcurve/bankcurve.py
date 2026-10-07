#!/usr/bin/env python3
"""Banked curve on ice: flat road or banked road, which one keeps the car in its lane?

Two panels on the same clock, the same curve drawn the same way at the same
scale, seen from above: a point car at a constant speed v (chosen: held)
enters a curve whose lane centre line has radius R, in a lane w wide (edges
w / 2 either side of the centre line), on ice with grip mu. Holding the curve
needs a sideways acceleration v^2 / R. Top panel, the FLAT road: only the
tyres can push sideways and they give at most mu g, so with full-grip
steering (the swerve model: the lateral acceleration mu g perpendicular to
the velocity, the speed held) the car follows a circle of radius
R2 = v^2 / (mu g) and runs wide, over the outer lane edge, then on off the
road. Bottom panel, the road BANKED at theta (the outer edge higher): the
road's push N tilts toward the centre; in the road frame per kilogram

    N = g cos theta + (v^2 / R) sin theta,
    F = (v^2 / R) cos theta - g sin theta  (down the slope, inward, when positive),

so the grip needed is F / N, far under mu, and the car holds its centre
line. Closed forms: the flat limit sqrt(mu g R), the no-grip design speed
sqrt(g R tan theta), the banked window sqrt(g R (tan theta -+ mu) / (1 +-
mu tan theta)), the bank needed for a speed with and without grip. Both
cars are integrated by classical RK4 at steps_per_second on (x, y, vx, vy)
with the lateral acceleration perpendicular to the velocity (mu g on the
flat, v^2 / R on the bank), the flat car's lane-edge crossing located by
bisection inside the step and checked against the R2 circle and a half-step
rerun; the drawing follows the RK4 tables. The run repeats every cycle_s
seconds of video with a crossfade back to the entry; the cycle divides the
scene length, so the scene is exactly periodic and the last frame equals the
first. Shown at 1/slow speed. Deterministic, no seed.

Measured and printed: the sideways acceleration needed against the grip, the
flat car's circle, its edge crossing (travel, time, angle) against the closed
circle and the half-step rerun, the banked force balance per kilogram, the
table at table_step_s, the other speeds, grips and bank angles for the
description, the brief's checks, the schedule in video time, the on-screen
text widths and the layout clearances.

usage: bankcurve.py [--measure-only] [--frames t1,t2,...]
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
HEAD = (250, 236, 170)
RED = (255, 64, 48)

# Layout: overlay at y 96..130 (captions.py), two title rows at y 190/252 for
# the first seconds, then the legend at y 236 and the shared clock at y 290;
# two bands stacked, the flat road in y 330..880 and the banked road in
# 880..1430, each drawn at 2x in its own layer (so the road and the cars are
# clipped at the band); each band has its label row 40 px under the band top,
# its readouts at 84 and 120 (left column from x 40, right column to x 1040),
# the gold event row at 172 right-aligned at x 1040; the lane enters the band
# at the right edge, its entry point at (entry_x_px, entry_y_px) under the band
# top heading entry_heading_deg (counterclockwise from the right), and curves
# to the left; the cross-section inset in the lower left corner; the gold edge
# mark under the lane in the flat band; captions at caption_y 0.75 (y
# 1440..1530); the six-line card from y 1572 at a 48 px pitch.
LEGEND_Y, CLOCK_Y = 236, 290
SS = 2
PAYOFF_Y, PAYOFF_PITCH = 1572.0, 48
PANELS = ("flat", "banked")
BAND_Y = {"flat": 330, "banked": 880}
BAND_H = 550
LABEL_DY, SUB_DY, FIX_DY = 40, 84, 120
EVENT_DY = 172
ROW_X0, ROW_X1 = 40, 1040
INSET_X0, INSET_Y0, INSET_W, INSET_H = 44, 436, 200, 90
INSET_LABEL_DY = 406
MARK_DY, MARK_DX = 52, -45   # the mark label this far under the lane's inner edge and left of the crossing
COLOUR = {"flat": CORAL, "banked": TEAL}
LANE, OVER = "lane", "over"


def blend(col, a: float, base=BG) -> tuple:
    a = max(0.0, min(1.0, a))
    return tuple(int(round(c * a + b * (1 - a))) for c, b in zip(col, base))


# --- measurement --------------------------------------------------------------
def banked_balance(v: float, R: float, th_deg: float, g: float) -> dict:
    """Force balance per kilogram in the road frame for a car on the centre line at speed v: the
    road's push N (normal) and the friction F along the slope needed (positive down the slope,
    inward: the car would creep up and out without it)."""
    t = math.radians(th_deg)
    ac = v * v / R
    n = g * math.cos(t) + ac * math.sin(t)
    f = ac * math.cos(t) - g * math.sin(t)
    return {"ac": ac, "n": n, "f": f, "need": f / n, "n_w": n / g}


def v_window(R: float, th_deg: float, mu: float, g: float) -> tuple[float, float]:
    """(lowest, highest) speed the bank holds with grip mu (0 when the bank alone holds a stop)."""
    t = math.tan(math.radians(th_deg))
    lo = math.sqrt(g * R * (t - mu) / (1.0 + mu * t)) if t > mu else 0.0
    hi = math.sqrt(g * R * (t + mu) / (1.0 - mu * t)) if mu * t < 1.0 else math.inf
    return lo, hi


def rk4_run(v: float, a_lat: float, R: float, half_w: float, dt: float, t_end: float) -> dict:
    """Integrate (x, y, vx, vy) from the entry (origin, heading +x, the curve centre at (0, R)) by
    classical RK4 at dt with the lateral acceleration a_lat perpendicular to the velocity (to the
    left) until t_end; the first crossing of the outer lane edge (offset half_w from the centre
    line) is located by bisection inside the step. Returns the table and the crossing."""

    def deriv(s: np.ndarray) -> np.ndarray:
        sp = math.hypot(s[2], s[3])
        return np.array([s[2], s[3], -a_lat * s[3] / sp, a_lat * s[2] / sp])

    def step(s: np.ndarray, h: float) -> np.ndarray:
        k1 = deriv(s)
        k2 = deriv(s + 0.5 * h * k1)
        k3 = deriv(s + 0.5 * h * k2)
        k4 = deriv(s + h * k3)
        return s + h * (k1 + 2.0 * k2 + 2.0 * k3 + k4) / 6.0

    def offset(s: np.ndarray) -> float:
        return math.hypot(s[0], s[1] - R) - R

    s = np.array([0.0, 0.0, v, 0.0])
    n_steps = int(round(t_end / dt))
    assert abs(n_steps * dt - t_end) < 1e-9, "the step must divide the run"
    ts, xs, ys, vxs, vys = [0.0], [0.0], [0.0], [v], [0.0]
    t_x = None
    for n in range(n_steps):
        sn = step(s, dt)
        if t_x is None and offset(sn) >= half_w:
            lo, hi = 0.0, dt
            for _ in range(80):
                mid = 0.5 * (lo + hi)
                if offset(step(s, mid)) < half_w:
                    lo = mid
                else:
                    hi = mid
            t_x = n * dt + hi
            s_x = step(s, hi)
        s = sn
        ts.append((n + 1) * dt)
        xs.append(s[0])
        ys.append(s[1])
        vxs.append(s[2])
        vys.append(s[3])
    tab = {k: np.array(a) for k, a in (("t", ts), ("x", xs), ("y", ys), ("vx", vxs), ("vy", vys))}
    tab["off"] = np.hypot(tab["x"], tab["y"] - R) - R
    tab["t_x"] = t_x
    tab["s_x"] = s_x if t_x is not None else None
    tab["steps"] = n_steps
    return tab


def state_at(tab: dict, rt: float, v: float) -> dict:
    """World position, velocity and offset of a car rt real seconds after the entry (before the
    entry it is on the straight at constant speed)."""
    if rt < 0.0:
        return {"x": v * rt, "y": 0.0, "vx": v, "vy": 0.0, "off": 0.0}
    rt = min(rt, float(tab["t"][-1]))
    return {k: float(np.interp(rt, tab["t"], tab[k])) for k in ("x", "y", "vx", "vy", "off")}


def circle_xy(t, v: float, R2: float):
    ph = v * t / R2
    return R2 * np.sin(ph), R2 * (1.0 - np.cos(ph))


def bearing_deg(x: float, y: float, R: float) -> float:
    """The car's angle round the curve as seen from the curve centre (0, R)."""
    return math.degrees(math.atan2(x, R - y))


class Geo:
    """Band-local screen geometry: the entry at (ex, ey) heading psi (counterclockwise from the
    right); world X along the entry heading, world Y toward the curve centre (the visual left)."""

    def __init__(self, man: dict):
        self.ppm = float(man["px_per_m"])
        psi = math.radians(man["entry_heading_deg"])
        self.h = (math.cos(psi), -math.sin(psi))
        self.n = (self.h[1], -self.h[0])
        self.ex, self.ey = float(man["entry_x_px"]), float(man["entry_y_px"])
        self.R = man["radius_m"]

    def scr(self, X: float, Y: float) -> tuple[float, float]:
        return (self.ex + self.ppm * (X * self.h[0] + Y * self.n[0]), self.ey + self.ppm * (X * self.h[1] + Y * self.n[1]))

    def vec(self, X: float, Y: float) -> tuple[float, float]:
        """A world direction on screen (unit in, unit out)."""
        return (X * self.h[0] + Y * self.n[0], X * self.h[1] + Y * self.n[1])

    def lane(self, a: float, off: float) -> tuple[float, float]:
        """Screen point at angle a (rad) round the curve, off metres outward from the centre line."""
        r = self.R + off
        return self.scr(r * math.sin(a), self.R - r * math.cos(a))

    def straight(self, d: float, off: float) -> tuple[float, float]:
        """Screen point d metres before the entry on the straight, off metres outward."""
        return self.scr(-d, -off)


def car_corners(geo: Geo, man: dict, X: float, Y: float, vx: float, vy: float) -> list[tuple[float, float]]:
    """Screen corners of the drawn car body (car_length_m by car_width_m) centred on the model's
    point, turned to its heading."""
    cx, cy = geo.scr(X, Y)
    fx, fy = geo.vec(vx, vy)
    sp = math.hypot(fx, fy)
    fx, fy = fx / sp, fy / sp
    rx, ry = -fy, fx
    hl, hw = man["car_length_m"] / 2.0 * geo.ppm, man["car_width_m"] / 2.0 * geo.ppm
    return [(cx + u * rx + w * fx, cy + u * ry + w * fy) for u, w in ((-hw, -hl), (hw, -hl), (hw, hl), (-hw, hl))]


def measure(man: dict) -> dict:
    g, R, mu, th = man["g"], man["radius_m"], man["mu"], man["bank_deg"]
    v_kmh = man["speed_kmh"]
    v = v_kmh / 3.6
    half_w = man["lane_width_m"] / 2.0
    dt = 1.0 / man["steps_per_second"]
    S, P, D, fps, F, pa = man["slow"], man["cycle_s"], man["scene_duration"], man["fps"], man["reset_fade"], man["entry_at"]
    t_end = man["run_end_s"]
    cycles = D / P
    assert abs(cycles - round(cycles)) < 1e-9, "the cycle must divide the scene length"
    for key in ("cycle_s", "entry_at", "first_cycle_at", "reset_fade"):
        assert abs(man[key] * fps - round(man[key] * fps)) < 1e-9, f"{key} must be a whole number of frames"
    assert pa + S * t_end < P - F, "the run must end before the reset fade"
    ppm = man["px_per_m"]
    ac = v * v / R
    R2 = v * v / (mu * g)
    v_flat = math.sqrt(mu * g * R)
    v_design = math.sqrt(g * R * math.tan(math.radians(th)))
    v_lo, v_hi = v_window(R, th, mu, g)
    print(f"setup: top-down view, two panels on one clock, the same curve drawn the same way at the same scale: a point "
          f"car at {v_kmh:g} km/h = {v:.4f} m/s (the speed held constant: chosen) enters a curve whose lane centre line "
          f"has radius R = {R:g} m, in a lane {man['lane_width_m']:g} m wide (edges {half_w:g} m either side of the "
          f"centre line), on ice with grip mu = {mu:g} (a chosen number for tyres on ice); g = {g:g} m/s^2; top panel "
          f"the flat road, bottom panel the road banked at theta = {th:g} degrees with the outer edge higher; the flat "
          f"car steers with full grip (the swerve model: the lateral acceleration mu g perpendicular to its velocity, "
          f"the speed held), the banked car follows its centre line; both integrated by classical RK4 at "
          f"{man['steps_per_second']} steps per second (dt = {dt:.0e} s) on (x, y, vx, vy) to {t_end:g} s after the "
          f"entry, the flat car's lane-edge crossing located by bisection inside the step and checked against the "
          f"circle v^2 / (mu g) and a half-step rerun; after the edge the flat car keeps its full-grip steer off the "
          f"road (chosen); shown at 1/{S:g} speed on a {P:g} s cycle ({P * fps:.0f} frames) with the entry {pa:g} s into "
          f"the cycle, {cycles:.0f} cycles in {D:g} s; drawn at {ppm:g} px per metre (the lane {man['lane_width_m'] * ppm:.0f} "
          f"px wide, the curve radius {R * ppm:.0f} px; the model's point car drawn as a {man['car_length_m']:g} by "
          f"{man['car_width_m']:g} m body, {man['car_length_m'] * ppm:.0f} by {man['car_width_m'] * ppm:.0f} px); "
          f"deterministic, no seed")
    print(f"needed: holding the curve needs v^2 / R = {ac:.4f} m/s^2 = {ac / g:.4f} g sideways; the tyres on ice can give "
          f"at most mu g = {mu * g:.4f} m/s^2 = {mu:g} g on the flat, {ac / g / mu:.2f} times less than needed; the flat "
          f"road holds this curve up to sqrt(mu g R) = {v_flat:.4f} m/s = {v_flat * 3.6:.2f} km/h")
    # The flat car by RK4 against the circle.
    flat = rk4_run(v, mu * g, R, half_w, dt, t_end)
    assert flat["t_x"] is not None, "the flat car never reaches the lane edge"
    t_x, s_x = flat["t_x"], flat["s_x"]
    cx_, cy_ = circle_xy(flat["t"], v, R2)
    err_c = float(np.max(np.hypot(flat["x"] - cx_, flat["y"] - cy_)))
    half = rk4_run(v, mu * g, R, half_w, 0.5 * dt, t_end)
    # Closed crossing on the circle by bisection on the arc length.
    def off_circle(s_arc: float) -> float:
        ph = s_arc / R2
        return math.hypot(R2 * math.sin(ph), R2 * (1.0 - math.cos(ph)) - R) - R
    lo, hi = 0.0, 0.5 * math.pi * R2
    for _ in range(100):
        mid = 0.5 * (lo + hi)
        if off_circle(mid) < half_w:
            lo = mid
        else:
            hi = mid
    s_closed = hi
    t_closed = s_closed / v
    s_small = math.sqrt(2.0 * half_w / (1.0 / R - 1.0 / R2))
    travel = v * t_x
    ang_arc = math.degrees(travel / R)
    bear_x = bearing_deg(float(s_x[0]), float(s_x[1]), R)
    end = state_at(flat, t_end, v)
    speed_end = math.hypot(end["vx"], end["vy"])
    print(f"flat road (top panel): with {mu:g} g of grip the car follows a circle of radius v^2 / (mu g) = {R2:.4f} m = "
          f"{R2:.2f} m instead of {R:g} m; RK4 from the entry: it crosses the outer lane edge {half_w:g} m out after "
          f"{travel:.4f} m of travel = {travel:.2f} m, {t_x:.6f} s = {t_x:.4f} s after the entry, {ang_arc:.2f} degrees "
          f"of arc at the lane's radius = {ang_arc:.1f} deg (its bearing from the curve centre {bear_x:.2f} deg); closed "
          f"form on the {R2:.2f} m circle: {s_closed:.4f} m, {t_closed:.6f} s (diff {t_x - t_closed:+.1e} s); small-arc "
          f"check sqrt(2 w / (1 / R - 1 / R2)) = {s_small:.3f} m; the RK4 position stays within {err_c:.1e} m of the "
          f"circle over the {t_end:g} s run ({flat['steps']} steps); half-step rerun (dt = {0.5 * dt:.0e} s): over the "
          f"edge at {half['t_x']:.9f} s ({half['t_x'] - t_x:+.1e} s); at {t_end:g} s the car is {end['off']:.4f} m = "
          f"{end['off']:.1f} m outside the lane centre line ({end['off'] - half_w:.1f} m past the edge), bearing "
          f"{bearing_deg(end['x'], end['y'], R):.1f} deg, speed kept {speed_end * 3.6:.2f} km/h")
    assert abs(t_x - t_closed) < 1e-6 and err_c < 1e-6 and abs(half["t_x"] - t_x) < 1e-9
    assert abs(speed_end - v) < 1e-9
    # The banked car: the force balance and the lane-following integration.
    bb = banked_balance(v, R, th, g)
    banked = rk4_run(v, ac, R, half_w, dt, t_end)
    max_off_b = float(np.max(np.abs(banked["off"])))
    avail = mu * bb["n"]
    print(f"banked {th:g} degrees (bottom panel): the force balance per kilogram in the road frame: the road's push "
          f"N = g cos theta + (v^2 / R) sin theta = {g * math.cos(math.radians(th)):.4f} + {ac * math.sin(math.radians(th)):.4f} = "
          f"{bb['n']:.4f} m/s^2 = {bb['n_w']:.4f} weights (its tilt toward the centre gives {bb['n'] * math.sin(math.radians(th)):.4f} "
          f"m/s^2 of the {ac:.4f} needed); along the slope, the needed (v^2 / R) cos theta = {ac * math.cos(math.radians(th)):.4f} "
          f"against gravity's g sin theta = {g * math.sin(math.radians(th)):.4f}, so the friction needed is {bb['f']:.4f} m/s^2 "
          f"down the slope (inward: without it the car would creep up and out, the speed being above the design speed), "
          f"grip needed F / N = {bb['need']:.4f} against {mu:g} available ({avail:.4f} m/s^2 along the slope, "
          f"{mu - bb['need']:.4f} of grip to spare), so the car holds its lane; RK4 of the lane-following motion "
          f"(lateral acceleration v^2 / R): the offset from the centre line stays within {max_off_b:.1e} m over {t_end:g} s "
          f"and it never reaches the edge; no grip at all holds sqrt(g R tan theta) = {v_design:.4f} m/s = "
          f"{v_design * 3.6:.2f} km/h on this bank (the design speed); with grip {mu:g} the bank holds "
          f"{v_lo * 3.6:.2f} to {v_hi * 3.6:.2f} km/h (below it the car slides down the bank, above it up and out)")
    assert abs(bb["need"]) < mu and banked["t_x"] is None and max_off_b < 1e-9
    # The table.
    rows = []
    n_tab = int(round(t_end / man["table_step_s"]))
    for i in range(n_tab + 1):
        tt = i * man["table_step_s"]
        sf, sb = state_at(flat, tt, v), state_at(banked, tt, v)
        rows.append((tt, sf["off"], bearing_deg(sf["x"], sf["y"], R), sb["off"], bearing_deg(sb["x"], sb["y"], R)))
        print(f"  t {tt:.2f} s: flat {sf['off']:+.4f} m off the lane centre ({'over the edge' if sf['off'] > half_w else 'in the lane'}), "
              f"{bearing_deg(sf['x'], sf['y'], R):.2f} deg round the curve; banked {sb['off']:+.1e} m off, "
              f"{bearing_deg(sb['x'], sb['y'], R):.2f} deg round the curve")
    ev: dict = {"v": v, "ac": ac, "ac_g": ac / g, "R2": R2, "flat": flat, "banked": banked, "t_x": t_x, "travel": travel,
                "bb": bb, "v_flat": v_flat, "v_design": v_design, "v_lo": v_lo, "v_hi": v_hi, "end_off": end["off"]}
    # Other speeds, grips and bank angles for the description.
    descr = []
    ev["speeds"] = {}
    for kmh in man["description_speeds_kmh"]:
        vv = kmh / 3.6
        need_f = vv * vv / R / g
        b2 = banked_balance(vv, R, th, g)
        ev["speeds"][kmh] = (need_f, b2["need"])
        if abs(b2["need"]) <= mu:
            outcome = "holds its lane"
        elif b2["need"] > 0.0:
            outcome = "slides up and out"
        else:
            outcome = "slides down the bank"
        descr.append(f"{kmh:g} km/h: the flat road needs grip {need_f:.4f} ({'holds' if need_f <= mu else 'slides out'}); "
                     f"the bank needs grip {abs(b2['need']):.4f} {'down the slope' if b2['need'] > 0 else 'up the slope'} "
                     f"({outcome}; N {b2['n_w']:.4f} weights)")
    ev["mus"] = {}
    for m2 in man["description_mus"]:
        lo2, hi2 = v_window(R, th, m2, g)
        vf2 = math.sqrt(m2 * g * R)
        ev["mus"][m2] = (vf2 * 3.6, lo2 * 3.6, hi2 * 3.6)
        descr.append(f"grip {m2:g}: the flat road holds up to {vf2 * 3.6:.1f} km/h, the {th:g} degree bank "
                     f"{lo2 * 3.6:.1f} to {hi2 * 3.6:.1f} km/h")
    bank_mu = math.degrees(math.atan((ac / g - mu) / (1.0 + mu * ac / g)))
    bank_0 = math.degrees(math.atan(ac / g))
    ev["bank_mu"], ev["bank_0"] = bank_mu, bank_0
    descr.append(f"the bank that holds {v_kmh:g} km/h on this curve with grip {mu:g}: tan theta = (v^2 / (g R) - mu) / "
                 f"(1 + mu v^2 / (g R)) gives {bank_mu:.2f} degrees; with no grip at all tan theta = v^2 / (g R) gives "
                 f"{bank_0:.2f} degrees")
    print("for the description: " + "; ".join(descr))
    # The brief's checks.
    checks: list[tuple[str, float, float, float]] = [
        ("needed (m/s^2)", ac, 3.858, 6e-4), ("needed (g)", ac / g, 0.3934, 6e-5),
        ("flat radius (m)", R2, 196.70, 6e-3), ("flat travel to the edge (m)", travel, 22.05, 6e-3),
        ("flat time to the edge (s)", t_x, 1.5876, 6e-5), ("flat angle to the edge (deg)", ang_arc, 25.3, 6e-2),
        ("banked grip needed", bb["need"], 0.0257, 6e-5), ("banked N (weights)", bb["n_w"], 1.0742, 6e-5),
        ("flat limit (km/h)", v_flat * 3.6, 25.21, 6e-3), ("design speed (km/h)", v_design * 3.6, 48.09, 6e-3),
        ("banked window low (km/h)", v_lo * 3.6, 40.23, 6e-3), ("banked window high (km/h)", v_hi * 3.6, 55.32, 6e-3),
        ("bank needed with grip 0.1 (deg)", bank_mu, 15.76, 6e-3), ("bank needed with no grip (deg)", bank_0, 21.47, 6e-3),
        ("small-arc travel (m)", s_small, 21.663, 6e-4),
    ]
    for kmh, want in ((30.0, -0.2114), (40.0, -0.1028), (60.0, 0.1679), (70.0, 0.3179)):
        if kmh in ev["speeds"]:
            checks.append((f"{kmh:g} km/h banked grip needed", ev["speeds"][kmh][1], want, 6e-5))
    for m2, want in ((0.3, 43.7), (0.5, 56.4), (0.8, 71.3)):
        if m2 in ev["mus"]:
            checks.append((f"grip {m2:g} flat limit (km/h)", ev["mus"][m2][0], want, 6e-2))
    fails = 0
    out = []
    for name, got, want, tol in checks:
        ok = abs(got - want) <= tol
        fails += 0 if ok else 1
        out.append(f"{name}: brief {want:g}, sim {got:.6g}, diff {got - want:+.1e}: {'ok' if ok else 'FAIL'}")
    print(f"checks against the brief ({len(checks)} checks, {fails} failed): " + "; ".join(out))
    ev["check_fails"] = fails
    assert fails == 0, "a check against the brief failed"
    # The schedule in video time.
    t0 = man["first_cycle_at"]
    k0 = math.ceil((0.0 - t0) / P - 1e-9) - 1
    k1 = math.floor((D - t0) / P - 1e-9)
    starts = [t0 + kk * P for kk in range(k0, k1 + 1)]
    ev["cycles"] = int(round(cycles))

    def lst(off_: float) -> str:
        return ", ".join(f"{st + off_:.2f}" for st in starts if 0.0 <= st + off_ < D)

    tau0 = (0.0 - t0) % P
    r0 = (tau0 - pa) / S
    st0 = {m: state_at(ev[m], r0, v) for m in PANELS}
    vt = lambda real: pa + real * S   # noqa: E731  video time after the cycle start
    print(f"schedule (video time, 1/{S:g} speed): cycles of {P:g} s start at " + ", ".join(f"{st:.2f}" for st in starts)
          + f" s (the first {-t0:.2f} s before the first frame); both cars pass the entry {pa:g} s into each cycle at "
          f"{lst(pa)} s; the flat car is over the outer edge {S * t_x:.3f} s after the entry at {lst(vt(t_x))} s "
          f"({vt(t_x):.3f} s into the cycle; both event rows light and the gold edge mark fades in over "
          f"{man['mark_fade_s']:g} s); the run ends {S * t_end:g} s after the entry at {lst(vt(t_end))} s ({vt(t_end):g} s "
          f"into the cycle: the flat car {end['off']:.1f} m outside the lane centre line, the banked car on it) and both "
          f"cars hold there until the reset crossfade over the last {F:g} s of each cycle (from {lst(P - F)} s; the "
          f"readouts out over its first half and in over its second); on the first frame the cycle is {tau0:.2f} s in "
          f"({r0:.3f} s real after the entry: the flat car {st0['flat']['off']:.2f} m off the centre line, the banked car "
          f"{st0['banked']['off']:.1e} m); title until {man['title_until']:g} s; payoff card from {man['payoff_t']:g} s; "
          f"the title fades back in over the last {man['loop_fade']:g} s and the last frame repeats the first (the scene "
          f"is periodic: {D:g} s holds exactly {cycles:.0f} cycles)")
    # Text widths.
    font = os.environ["SEED_ZERO_FONT"]
    f24, f28, f34, f40, f56 = (ImageFont.truetype(font, n) for n in (24, 28, 34, 40, 56))
    widths = {"overlay@34": (f34, man["overlay"])}
    for j, line in enumerate(man["title"].split("|")):
        widths[f"title line {j + 1}@56"] = (f56, line)
    widths["legend@40"] = (f40, legend_text(man))
    widths["clock@28"] = (f28, clock_text(1.5876))
    widths["clock before@28"] = (f28, clock_text(-1.0))
    for m in PANELS:
        widths[f"label {m}@40"] = (f40, label_text(man, m))
        widths[f"sub {m}@28"] = (f28, sub_text(ev, m))
        widths[f"fixed {m}@28"] = (f28, fixed_text(man, ev, m))
        widths[f"event {m}@40"] = (f40, event_text(ev, m))
    widths["offset@28"] = (f28, offset_text(end["off"]))
    widths["speed@28"] = (f28, speed_text(man))
    widths["mark@24"] = (f24, mark_text(ev))
    widths["inset label@24"] = (f24, inset_label())
    for j, line in enumerate(payoff_lines(man, ev)):
        widths[f"payoff line {j + 1}@40"] = (f40, line)
    print("text widths (the on-screen strings verbatim): " + ", ".join(f"{kk} {f.getlength(s):.0f} px '{s}'"
                                                                      for kk, (f, s) in widths.items()))
    assert all(f.getlength(s) < 950 for f, s in widths.values()), "a text line is wider than 950 px"
    assert len(payoff_lines(man, ev)) <= 6, "the card has more than six lines"
    assert all(len(line) > 0 for line in man["title"].split("|")) and len(man["title"].split("|")) <= 3
    # Layout checks (band-local pixels).
    geo = Geo(man)
    left = ROW_X0 + max(max(f40.getlength(label_text(man, m)), f28.getlength(sub_text(ev, m)),
                            f28.getlength(fixed_text(man, ev, m))) for m in PANELS)
    right = ROW_X1 - max(f28.getlength(offset_text(end["off"])), f28.getlength(speed_text(man)))
    rows_bottom = FIX_DY + 16
    ev_w = max(f40.getlength(event_text(ev, m)) for m in PANELS)
    boxes = {"left column": (ROW_X0 - 8, LABEL_DY - 28, left + 8, rows_bottom + 8),
             "right column": (right - 8, SUB_DY - 22, ROW_X1 + 8, rows_bottom + 8),
             "event row": (ROW_X1 - ev_w - 8, EVENT_DY - 28, ROW_X1 + 8, EVENT_DY + 28),
             "inset": (INSET_X0 - 8, INSET_Y0 - 8, INSET_X0 + INSET_W + 8, INSET_Y0 + INSET_H + 8),
             "inset label": (INSET_X0 + INSET_W / 2 - f24.getlength(inset_label()) / 2 - 8, INSET_LABEL_DY - 20,
                             INSET_X0 + INSET_W / 2 + f24.getlength(inset_label()) / 2 + 8, INSET_LABEL_DY + 20)}
    # The mark label under the lane's inner edge below the crossing point.
    mx, my = geo.scr(float(s_x[0]), float(s_x[1]))
    inner_y = inner_edge_y_at(geo, man, mx)
    mark_y, lx = inner_y + MARK_DY, mx + MARK_DX
    mw = f24.getlength(mark_text(ev))
    boxes["mark label"] = (lx - mw / 2 - 8, mark_y - 20, lx + mw / 2 + 8, mark_y + 20)
    ev["mark"] = (mx, my, lx, mark_y)
    a_draw = v * t_end / R + math.radians(man["lane_extra_deg"])
    lane_pts = []
    for off in (-half_w, 0.0, half_w):
        for k in range(301):
            lane_pts.append(geo.lane(a_draw * k / 300, off))
    circle_pts = [geo.scr(*circle_xy(k * man["circle_draw_m"] / 200 / v, v, R2)) for k in range(201)]
    car_pts = {m: [] for m in PANELS}
    for m in PANELS:
        tab = ev[m]
        for i in range(0, len(tab["t"]), max(1, len(tab["t"]) // 400)):
            car_pts[m] += car_corners(geo, man, float(tab["x"][i]), float(tab["y"][i]), float(tab["vx"][i]), float(tab["vy"][i]))
        e = state_at(tab, t_end, v)
        car_pts[m] += car_corners(geo, man, e["x"], e["y"], e["vx"], e["vy"])

    def inside(p, box) -> bool:
        return box[0] <= p[0] <= box[2] and box[1] <= p[1] <= box[3]

    def hits(pts, name) -> list[str]:
        return [bname for bname, box in boxes.items() if any(inside(p, box) for p in pts)]

    content = (16.0, rows_bottom + 10.0, W - 16.0, BAND_H - 6.0)
    extremes = {m: (min(p[0] for p in car_pts[m]), min(p[1] for p in car_pts[m]), max(p[0] for p in car_pts[m]),
                    max(p[1] for p in car_pts[m])) for m in PANELS}
    lane_box = (min(p[0] for p in lane_pts), min(p[1] for p in lane_pts), max(p[0] for p in lane_pts), max(p[1] for p in lane_pts))
    circ_box = (min(p[0] for p in circle_pts), min(p[1] for p in circle_pts), max(p[0] for p in circle_pts), max(p[1] for p in circle_pts))
    end_pts = {m: geo.scr(state_at(ev[m], t_end, v)["x"], state_at(ev[m], t_end, v)["y"]) for m in PANELS}
    d_straight = (W - geo.ex) / (-geo.h[0]) / ppm
    print(f"row check: the left column ends at x {left:.0f} px, the right column starts at x {right:.0f} px; both end "
          f"{rows_bottom} px under the band top; the event rows span {EVENT_DY - 20} to {EVENT_DY + 20} px under the band top, "
          f"right-aligned at x {ROW_X1} from x {ROW_X1 - ev_w:.0f} (widest {ev_w:.0f} px); the lane enters at the band's "
          f"right edge {d_straight:.1f} m before the entry point ({geo.ex:.0f}, {geo.ey:.0f}) heading "
          f"{man['entry_heading_deg']:g} deg and is drawn to {math.degrees(a_draw):.1f} deg round the curve, its edges "
          f"and centre line within x {lane_box[0]:.0f} to {lane_box[2]:.0f} and y {lane_box[1]:.0f} to {lane_box[3]:.0f} "
          f"px under the band top; the flat car's dashed circle is drawn {man['circle_draw_m']:g} m from the entry, within "
          f"x {circ_box[0]:.0f} to {circ_box[2]:.0f} and y {circ_box[1]:.0f} to {circ_box[3]:.0f}; the flat car's body "
          f"over the run spans x {extremes['flat'][0]:.0f} to {extremes['flat'][2]:.0f} and y {extremes['flat'][1]:.0f} "
          f"to {extremes['flat'][3]:.0f} (its point at the run end ({end_pts['flat'][0]:.0f}, {end_pts['flat'][1]:.0f})); "
          f"the banked car's body spans x {extremes['banked'][0]:.0f} to {extremes['banked'][2]:.0f} and y "
          f"{extremes['banked'][1]:.0f} to {extremes['banked'][3]:.0f} (its point at the run end ({end_pts['banked'][0]:.0f}, "
          f"{end_pts['banked'][1]:.0f})); the crossing point at ({mx:.0f}, {my:.0f}) with the lane's inner edge at y "
          f"{inner_y:.0f} under it and the mark label centred at ({lx:.0f}, {mark_y:.0f}), {mw:.0f} px wide; the "
          f"cross-section inset spans x {INSET_X0} to {INSET_X0 + INSET_W} and y {INSET_Y0} to {INSET_Y0 + INSET_H} px "
          f"under the band top with its label at y {INSET_LABEL_DY}; each band is {BAND_H} px tall (y {BAND_Y['flat']} to "
          f"{BAND_Y['flat'] + BAND_H} and {BAND_Y['banked']} to {BAND_Y['banked'] + BAND_H}); the caption band starts at y "
          f"{int(man['caption_y'] * H)}; the title rows end at y {302 + 28 if len(man["title"].split("|")) == 3 else 252 + 28} and the overlay band ends at y 130")
    assert right - left > 40, "the columns meet"
    assert all(content[0] <= p[0] <= content[2] and content[1] <= p[1] <= content[3] for p in lane_pts), "the drawn arcs leave the band's content area"
    assert all(content[0] <= p[0] <= content[2] and content[1] <= p[1] <= content[3] for p in circle_pts), "the dashed circle leaves the content area"
    for m in PANELS:
        inb = [p for p in car_pts[m] if p[0] <= W]  # the cars drive in from the right edge; inside they stay in the band
        assert all(content[1] <= p[1] <= content[3] and p[0] >= content[0] for p in inb), f"the {m} car leaves its band"
        for pts, what in ((car_pts[m], f"{m} car"),):
            h_ = hits(pts, what)
            assert not h_, f"the {what} meets {h_}"
    assert not hits(lane_pts, "lane"), f"the lane meets {hits(lane_pts, 'lane')}"
    assert not hits(circle_pts, "circle"), f"the dashed circle meets {hits(circle_pts, 'circle')}"
    for a_name, a_box in boxes.items():
        for b_name, b_box in boxes.items():
            if a_name < b_name:
                sep = a_box[2] <= b_box[0] or b_box[2] <= a_box[0] or a_box[3] <= b_box[1] or b_box[3] <= a_box[1]
                assert sep, f"{a_name} meets {b_name}"
    assert boxes["mark label"][3] < BAND_H - 6 and boxes["mark label"][0] > 16 and boxes["mark label"][2] < W - 16
    assert BAND_Y["banked"] + BAND_H <= int(man["caption_y"] * H), "the bottom band reaches the caption band"
    assert PAYOFF_Y - 20 > int(man["caption_y"] * H) + 90, "the card meets the caption band"
    return ev


def inner_edge_y_at(geo: Geo, man: dict, x: float) -> float:
    """The lane's inner edge (toward the centre) y under screen x, by bisection on the angle."""
    half_w = man["lane_width_m"] / 2.0
    lo, hi = 0.0, math.pi / 2
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if geo.lane(mid, -half_w)[0] > x:
            lo = mid
        else:
            hi = mid
    return geo.lane(hi, -half_w)[1]


def legend_text(man: dict) -> str:
    return f"same car, same icy curve, 1/{man['slow']:g} speed"


def clock_text(r: float) -> str:
    return "before the entry" if r < 0.0 else f"{r:.3f} s after the entry"


def label_text(man: dict, m: str) -> str:
    if m == "flat":
        return f"flat road, grip {man['mu']:g}"
    return f"banked {man['bank_deg']:g} deg, grip {man['mu']:g}"


def sub_text(ev: dict, m: str) -> str:
    if m == "flat":
        return f"needs {ev['ac_g']:.2f} g sideways"
    return f"road push {ev['bb']['n_w']:.2f} g, tilted inward"


def fixed_text(man: dict, ev: dict, m: str) -> str:
    need = ev["ac_g"] if m == "flat" else ev["bb"]["need"]
    return f"grip needed {need:.2f}, ice gives {man['mu']:g}" if m == "flat" else f"grip needed {need:.3f}, ice gives {man['mu']:g}"


def offset_text(off: float) -> str:
    return f"{off:.1f} m off the lane centre"


def speed_text(man: dict) -> str:
    return f"speed {man['speed_kmh']:g} km/h"


def event_text(ev: dict, m: str) -> str:
    if m == "flat":
        return f"flat: over the edge at {ev['t_x']:.2f} s"
    return "banked: holds its lane"


def mark_text(ev: dict) -> str:
    return f"over the edge at {ev['t_x']:.2f} s"


def inset_label() -> str:
    return "cross-section"


def payoff_lines(man: dict, ev: dict) -> list[str]:
    text = man["payoff_text"].format(
        t_x=ev["t_x"], ac_g=ev["ac_g"], mu=man["mu"], n_w=ev["bb"]["n_w"], need=ev["bb"]["need"],
        v_flat=ev["v_flat"] * 3.6, v_lo=ev["v_lo"] * 3.6, v_hi=ev["v_hi"] * 3.6, v_design=ev["v_design"] * 3.6)
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
        self.geo = Geo(man)
        self.ppm = float(man["px_per_m"])
        self.S = man["slow"]
        self.P = man["cycle_s"]
        self.P_f = int(round(man["cycle_s"] * self.fps))
        self.c0_f = int(round(man["first_cycle_at"] * self.fps))
        self.pa, self.F = man["entry_at"], man["reset_fade"]
        self.v, self.R, self.R2 = ev["v"], man["radius_m"], ev["R2"]
        self.half_w = man["lane_width_m"] / 2.0
        self.t_end = man["run_end_s"]
        self.a_draw = self.v * self.t_end / self.R + math.radians(man["lane_extra_deg"])
        self.statics = {m: self.draw_static(m) for m in PANELS}

    def phase(self, f: int) -> tuple[int, float]:
        k, tau_f = divmod(f - self.c0_f, self.P_f)
        return k, tau_f / self.fps

    @staticmethod
    def L_(x: float, y: float) -> tuple[float, float]:
        """Layer (2x) pixel of a band-local point, rounded to 1e-4 px so equal states draw equal pixels."""
        return round(x * SS, 4), round(y * SS, 4)

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

    def lane_pt(self, u: float, off: float) -> tuple[float, float]:
        """Band-local point of the lane at path parameter u (metres along the centre line, negative
        on the straight before the entry), off metres outward."""
        if u < 0.0:
            return self.geo.straight(-u, off)
        return self.geo.lane(u / self.R, off)

    def draw_static(self, m: str) -> Image.Image:
        """The band's road (and the flat car's dashed circle) and the cross-section inset, at 2x."""
        man, geo = self.man, self.geo
        layer = Image.new("RGB", (W * SS, BAND_H * SS), BG)
        d = ImageDraw.Draw(layer)
        tint = blend(COLOUR[m], 0.06, ASPHALT)
        u0, u1 = -man["straight_m"], self.a_draw * self.R
        fade = man["lane_fade_m"]
        n_seg = 220
        strips = 5 if m == "banked" else 1
        for k in range(n_seg):
            ua, ub = u0 + (u1 - u0) * k / n_seg, u0 + (u1 - u0) * (k + 1) / n_seg
            a = min(1.0, (u1 - ua) / fade)
            for j in range(strips):
                oa, ob = -self.half_w + self.half_w * 2 * j / strips, -self.half_w + self.half_w * 2 * (j + 1) / strips
                # The banked lane is shaded lighter toward its raised outer edge (off < 0 is inward).
                shade = blend(WHITE, 0.10 * (strips - 1 - j) / max(1, strips - 1), tint) if strips > 1 else tint
                poly = [self.L_(*self.lane_pt(ua, ob)), self.L_(*self.lane_pt(ub, ob)),
                        self.L_(*self.lane_pt(ub + 0.02, oa)), self.L_(*self.lane_pt(ua, oa))]
                d.polygon(poly, fill=blend(shade, a))
        for off in (-self.half_w, self.half_w):
            for k in range(n_seg):
                ua, ub = u0 + (u1 - u0) * k / n_seg, u0 + (u1 - u0) * (k + 1) / n_seg
                a = min(1.0, (u1 - ua) / fade)
                d.line((*self.L_(*self.lane_pt(ua, off)), *self.L_(*self.lane_pt(ub, off))), fill=blend(TEXT, 0.55 * a),
                       width=2 * SS)
        pts = [self.L_(*self.lane_pt(u0 + (u1 - u0 - fade) * k / n_seg, 0.0)) for k in range(n_seg + 1)]
        self.dashed(d, pts, blend(MUTED, 0.35, ASPHALT), 14 * SS, 14 * SS, 2 * SS)
        if m == "flat":
            n = 200
            pts = [self.L_(*geo.scr(*circle_xy(k * man["circle_draw_m"] / n / self.v, self.v, self.R2))) for k in range(n + 1)]
            self.dashed(d, pts, blend(CORAL, 0.5), 12 * SS, 10 * SS, 2 * SS)
        self.draw_inset(d, m)
        return layer

    def draw_inset(self, d: ImageDraw.ImageDraw, m: str) -> None:
        """The cross-section: the road seen along its direction (the curve centre on the left), the
        car on it and the sideways push: a dashed coral arrow for the push the flat road cannot give,
        a solid gold arrow for the banked road's tilted push."""
        th = math.radians(self.man["bank_deg"]) if m == "banked" else 0.0
        cx, cy = INSET_X0 + INSET_W / 2.0 + 6, INSET_Y0 + INSET_H - 30.0
        bx = (INSET_X0, INSET_Y0, INSET_X0 + INSET_W, INSET_Y0 + INSET_H)
        d.rounded_rectangle((*self.L_(bx[0], bx[1]), *self.L_(bx[2], bx[3])), radius=6 * SS, fill=blend(WHITE, 0.03),
                            outline=blend(MUTED, 0.35), width=SS)
        # The road: a thick line through (cx, cy) rising to the right by th (the outer edge higher).
        ex, ey = math.cos(th), -math.sin(th)       # along the road section, outward (to the right)
        nx, ny = -math.sin(th), -math.cos(th)      # the road's normal: up, tilted toward the centre (left)
        half = 70.0
        r0, r1 = (cx - half * ex, cy - half * ey), (cx + half * ex, cy + half * ey)
        d.line((*self.L_(*r0), *self.L_(*r1)), fill=blend(TEXT, 0.7), width=4 * SS)
        if m == "banked":
            # The level reference under the raised edge.
            self.dashed(d, [self.L_(cx - half, cy), self.L_(cx + half, cy)], blend(MUTED, 0.4), 6 * SS, 6 * SS, SS)
        # The car seen from behind: a body on two wheels, standing on the road.
        bw, bh, wh = 34.0, 15.0, 5.0

        def pt(u: float, w: float) -> tuple[float, float]:
            return self.L_(cx + u * ex + w * nx, cy + u * ey + w * ny)

        d.polygon([pt(-bw / 2, wh), pt(bw / 2, wh), pt(bw / 2, wh + bh), pt(-bw / 2, wh + bh)], fill=COLOUR[m])
        d.polygon([pt(-bw / 2 + 7, wh + bh), pt(bw / 2 - 7, wh + bh), pt(bw / 2 - 10, wh + bh + 8), pt(-bw / 2 + 10, wh + bh + 8)],
                  fill=blend(COLOUR[m], 0.6, (8, 10, 14)))
        for s in (-1, 1):
            d.polygon([pt(s * bw / 2 - 4, 0), pt(s * bw / 2 + 4, 0), pt(s * bw / 2 + 4, wh + 1), pt(s * bw / 2 - 4, wh + 1)],
                      fill=blend(TEXT, 0.5))
        # The sideways push arrow from the car's centre.
        ccx, ccy = cx + (wh + bh / 2) * nx, cy + (wh + bh / 2) * ny
        if m == "flat":
            ax, ay = -1.0, 0.0
            length = 50.0
            tip = (ccx - bw / 2 - 4 + ax * length, ccy)
            base = (ccx - bw / 2 - 4, ccy)
            self.dashed(d, [self.L_(*base), self.L_(*tip)], CORAL, 5 * SS, 4 * SS, 3 * SS)
            col = CORAL
        else:
            ax, ay = nx, ny
            length = 44.0
            base = (ccx, ccy)
            tip = (ccx + ax * length, ccy + ay * length)
            d.line((*self.L_(*base), *self.L_(*tip)), fill=GOLD, width=4 * SS)
            col = GOLD
        hx, hy = tip
        px, py = -ay, ax
        d.polygon([self.L_(hx + ax * 9, hy + ay * 9), self.L_(hx + px * 6, hy + py * 6), self.L_(hx - px * 6, hy - py * 6)],
                  fill=col)

    def draw_car(self, d: ImageDraw.ImageDraw, X: float, Y: float, vx: float, vy: float, col) -> None:
        geo, man = self.geo, self.man
        cx, cy = geo.scr(X, Y)
        fx, fy = geo.vec(vx, vy)
        sp = math.hypot(fx, fy)
        fx, fy = fx / sp, fy / sp
        rx, ry = -fy, fx
        hl, hw = man["car_length_m"] / 2.0 * self.ppm, man["car_width_m"] / 2.0 * self.ppm
        c = 3.0

        def pt(u: float, w: float) -> tuple[float, float]:
            return self.L_(cx + u * rx + w * fx, cy + u * ry + w * fy)

        body = [(-hw + c, -hl), (hw - c, -hl), (hw, -hl + c), (hw, hl - c), (hw - c, hl), (-hw + c, hl), (-hw, hl - c),
                (-hw, -hl + c)]
        d.polygon([pt(u, w) for u, w in body], fill=col, outline=blend(col, 0.5, (0, 0, 0)))
        d.polygon([pt(u, w) for u, w in ((-hw + 3, 2), (hw - 3, 2), (hw - 4, 8), (-hw + 4, 8))],
                  fill=blend(WHITE, 0.55, col))
        d.polygon([pt(u, w) for u, w in ((-hw + 3, -16), (hw - 3, -16), (hw - 3, -10), (-hw + 3, -10))],
                  fill=blend(col, 0.5, (8, 10, 14)))
        for s in (-1, 1):
            d.polygon([pt(u, w) for u, w in ((s * (hw - 1), hl - 1), (s * (hw - 6), hl - 1), (s * (hw - 6), hl - 4), (s * (hw - 1), hl - 4))],
                      fill=HEAD)

    def scene(self, m: str, tau: float) -> tuple[Image.Image, dict]:
        """The band layer of panel m at tau seconds into a cycle."""
        layer = self.statics[m].copy()
        d = ImageDraw.Draw(layer)
        tv = tau - self.pa
        rt = tv / self.S
        tab = self.ev[m]
        st = state_at(tab, rt, self.v)
        st["tv"], st["rt"] = tv, rt
        st["phase"] = OVER if (m == "flat" and rt >= self.ev["t_x"]) else LANE
        # The trail from the straight to the car.
        rr = min(max(rt, -1.0), self.t_end)
        n = max(2, int(60 * (rr + 1.0)))
        pts = []
        for k in range(n + 1):
            r_ = -1.0 + (rr + 1.0) * k / n
            s_ = state_at(tab, r_, self.v)
            pts.append(self.L_(*self.geo.scr(s_["x"], s_["y"])))
        d.line(pts, fill=blend(COLOUR[m], 0.75, ASPHALT), width=3 * SS, joint="curve")
        if m == "flat":
            # The gold edge mark: a dot at the crossing point and a tick down to its label.
            a = 0.0 if rt < self.ev["t_x"] else min(1.0, (rt - self.ev["t_x"]) * self.S / self.man["mark_fade_s"])
            if a > 0.0:
                mx, my, lx, mark_y = self.ev["mark"]
                r = 7 * SS
                X, Y = self.L_(mx, my)
                d.ellipse((X - r, Y - r, X + r, Y + r), fill=blend(GOLD, a, ASPHALT))
                self.dashed(d, [self.L_(mx, my + 10), self.L_(lx, mark_y - 16)], blend(GOLD, 0.8 * a, ASPHALT), 6 * SS, 6 * SS, 2 * SS)
            st["mark_alpha"] = a
        self.draw_car(d, st["x"], st["y"], st["vx"], st["vy"], COLOUR[m])
        return layer, st

    def draw_panel(self, m: str, f: int) -> tuple[Image.Image, dict]:
        k, tau = self.phase(f)
        P, F = self.P, self.F
        layer, st = self.scene(m, tau)
        st["alpha"], st["k"] = 1.0, k
        if tau >= P - F:
            # Crossfade to the next cycle's entry (the cars held at the run end fade into the cars
            # driving in on the straight).
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
        lit_all = states["flat"]["rt"] >= ev["t_x"]
        for m, st in states.items():
            y0 = BAND_Y[m]
            a = st["alpha"]
            over = st["phase"] == OVER
            d.text((ROW_X0, y0 + LABEL_DY), label_text(man, m), font=self.font, fill=COLOUR[m], anchor="lm")
            d.text((ROW_X0, y0 + SUB_DY), sub_text(ev, m), font=self.font_small, fill=MUTED, anchor="lm")
            if hud_alpha > 0.02:
                d.text((ROW_X0, y0 + FIX_DY), fixed_text(man, ev, m), font=self.font_small,
                       fill=blend(GOLD, 0.85 * hud_alpha), anchor="lm")
            d.text((ROW_X1, y0 + SUB_DY), offset_text(abs(st["off"]) if abs(st["off"]) > 0.05 else 0.0), font=self.font_small,
                   fill=blend(GOLD if over else TEXT, a), anchor="rm")
            d.text((ROW_X1, y0 + FIX_DY), speed_text(man), font=self.font_small, fill=blend(MUTED, a), anchor="rm")
            if lit_all and st["rt"] >= ev["t_x"]:
                d.text((ROW_X1, y0 + EVENT_DY), event_text(ev, m), font=self.font, fill=blend(GOLD, a), anchor="rm")
            if m == "flat" and st.get("mark_alpha", 0.0) > 0.0:
                mx, my, lx, mark_y = ev["mark"]
                d.text((lx, y0 + mark_y), mark_text(ev), font=self.font_tiny, fill=blend(GOLD, st["mark_alpha"] * a), anchor="mm")
            d.text((INSET_X0 + INSET_W / 2.0, y0 + INSET_LABEL_DY), inset_label(), font=self.font_tiny, fill=MUTED, anchor="mm")
        if hud_alpha > 0.02:
            d.text((W / 2, LEGEND_Y), legend_text(man), font=self.font, fill=blend(TEXT, hud_alpha), anchor="mm")
            d.text((W / 2, CLOCK_Y), clock_text(min(states["flat"]["rt"], self.t_end)), font=self.font_small,
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
            rows = man["title"].split("|")
            ys = (190, 252) if len(rows) == 2 else (186, 244, 302)
            for j, line in enumerate(rows):
                d.text((W / 2, ys[j]), line, font=self.font_title, fill=blend(TEXT, title_alpha), anchor="mm")
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
            # The geometry runs on; the legend, clock, fixed lines and card fade out over the first
            # half of the loop fade and the title fades in over the second half, so the two never overlap.
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
    man = json.loads((ROOT / "projects/bankcurve/manifest.json").read_text())
    ev = measure(man)
    if "--measure-only" in sys.argv:
        return
    if "--frames" in sys.argv:
        times = [float(v) for v in sys.argv[sys.argv.index("--frames") + 1].split(",")]
        r = Renderer(man, ev)
        (ROOT / "media/bankcurve").mkdir(parents=True, exist_ok=True)
        for tv in times:
            Image.fromarray(r.frame_at(int(round(tv * man["fps"])))).save(ROOT / f"media/bankcurve/smoke-{tv}.png")
        print("smoke frames: " + ", ".join(f"{tv}" for tv in times))
        return
    Renderer(man, ev).render(ROOT / "media/bankcurve/footage.mp4")


if __name__ == "__main__":
    main()
