#!/usr/bin/env python3
"""Car over a hump: does the car leave the road?

Two panels on the same clock, the same humpback bridge drawn the same way at
the same scale: a cosine hump of height H and length L on a flat road,

    y(x) = (H / 2) (1 + cos(2 pi x / L))   for |x| <= L / 2,   0 elsewhere,

which joins the road with zero slope; its crest radius is R = L^2 / (2 pi^2
H). A car is a point moving along the road at a steady speed v (the engine
holds the speed) with no suspension. While the wheels touch, the road pushes
up per unit mass with

    N = g cos(theta) - v^2 kappa,

theta the road slope and kappa the road's convex curvature (-y'' / (1 +
y'^2)^1.5, positive over the crest). The wheels leave where N reaches zero;
from there the point flies on the parabola from its tangent velocity and
lands where the parabola meets the road again (the root by bisection); the
landing takes the vertical speed and the car continues along the road at its
steady speed. At the crest N = g - v^2 / R, so the limit is v* = sqrt(g R),
independent of the car's mass. The top panel runs at 40 km/h, the bottom one
at 60 km/h. The motion is stepped at step_s (RK4 on dx/dt = v cos theta along
the road, the leave point located by bisection inside the step, the flight
the closed-form parabola with the landing located by bisection), checked
against N = 0 solved by bisection on x and a half-step rerun. Drawing only:
the car body sits on the chord between its two wheel contacts, and in the
air its pitch turns evenly from the take-off chord to the landing chord (the
point model has no attitude). Shown at 1/3
speed; each cycle both cars start start_x_m before the crest; the cycle
divides the scene length and ends with a crossfade back to the start, so the
scene is exactly periodic and the last frame equals the first.
Deterministic, no seed.

Measured and printed: the crest radius, the limit speed, the steepest slope;
for each panel the smallest road push, the leave point, the flight length,
time and largest gap, the landing point and its vertical speed; the 50, 55
and 70 km/h cases and the 1.5 m by 24 m hump for the description; the
bisection and half-step checks; the schedule in real and video seconds; the
on-screen text widths and the layout clearances (the roof never enters the
readout rows).

usage: hump.py [--measure-only] [--frames t1,t2,...]
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
INK = (150, 158, 170)
SLAB = (30, 34, 40)
SURF = (118, 126, 136)
DASH = (196, 202, 210)
SHADOW = (16, 18, 22)
WHEEL = (38, 42, 48)
RIM = (160, 166, 176)
GLASS = (14, 18, 24)
LAMP = (250, 236, 170)
TAIL = (220, 70, 60)
MINI = (84, 92, 104)

# Layout: overlay at y 96..130 (captions.py), two title rows at y 190/252 for
# the first seconds, then the legend at y 236 and the shared clock at y 290;
# two panels stacked, the 40 km/h car in the band y 330..880 and the 60 km/h
# car in y 880..1430, each drawn at 2x in its own layer; each band has its
# label row 40 px under the band top (left: the speed, right: the distance
# from the crest), its second row at 84 (left: the road push; right: the
# minimap strip at x 740..1040, y 68..103) and its gold event row at 120
# (rows end at 136); the flat road 480 px under the band top, the crest 200
# px higher; the car's point at x 480 (the camera follows it); the gap
# readout centred under the car at 516, inside the road slab; captions at
# caption_y 0.75 (y 1440..1530); the six-line card from y 1572 at a 48 px
# pitch.
LEGEND_Y, CLOCK_Y = 236, 290
SS = 2
PAYOFF_Y, PAYOFF_PITCH = 1572.0, 48
PANELS = ("slow", "fast")
BAND_Y = {"slow": 330, "fast": 880}
BAND_H = 550
LABEL_DY, SUB_DY, EVENT_DY, ROWS_BOTTOM = 40, 84, 120, 136
ROW_X0, ROW_X1 = 40, 1040
MINI_X0, MINI_X1, MINI_BASE_DY, MINI_TOP_DY = 740, 1040, 100, 68
ROAD_DY, CAR_X, GAP_TEXT_DY, CREST_TEXT_DY = 480, 480, 516, 34
COLOUR = {"slow": TEAL, "fast": CORAL}
ROAD, AIR = "road", "air"
# The car's outline in its own frame (u forward, w up, metres): a sedan body.
BODY = [(-2.0, 0.32), (2.0, 0.32), (2.0, 0.72), (1.35, 0.80), (0.85, 1.28), (-0.95, 1.30), (-1.72, 0.82),
        (-2.0, 0.72)]
GLASS_FRONT = [(0.10, 0.86), (1.22, 0.86), (0.78, 1.20), (0.10, 1.20)]
GLASS_REAR = [(-0.86, 0.86), (-0.02, 0.86), (-0.02, 1.20), (-0.88, 1.22)]


def blend(col, a: float, base=BG) -> tuple:
    a = max(0.0, min(1.0, a))
    return tuple(int(round(c * a + b * (1 - a))) for c, b in zip(col, base))


# --- the road ------------------------------------------------------------------
class Hump:
    def __init__(self, height: float, length: float):
        self.H, self.L = height, length
        self.k = 2.0 * math.pi / length

    def y(self, x: float) -> float:
        if abs(x) >= self.L / 2.0:
            return 0.0
        return 0.5 * self.H * (1.0 + math.cos(self.k * x))

    def yp(self, x: float) -> float:
        if abs(x) >= self.L / 2.0:
            return 0.0
        return -0.5 * self.H * self.k * math.sin(self.k * x)

    def ypp(self, x: float) -> float:
        if abs(x) >= self.L / 2.0:
            return 0.0
        return -0.5 * self.H * self.k * self.k * math.cos(self.k * x)

    def kappa(self, x: float) -> float:
        """Convex curvature, positive over the crest."""
        p = self.yp(x)
        return -self.ypp(x) / (1.0 + p * p) ** 1.5

    def cos_theta(self, x: float) -> float:
        p = self.yp(x)
        return 1.0 / math.sqrt(1.0 + p * p)

    def N(self, x: float, v: float, g: float) -> float:
        """Road push per unit mass on a point moving along the road at v."""
        return g * self.cos_theta(x) - v * v * self.kappa(x)

    @property
    def R(self) -> float:
        return self.L * self.L / (2.0 * math.pi * math.pi * self.H)


# --- measurement ---------------------------------------------------------------
def rk4_x(h: Hump, x: float, v: float, dt: float) -> float:
    """One RK4 step of dx/dt = v cos theta(x) along the road."""
    f = lambda xx: v * h.cos_theta(xx)   # noqa: E731
    k1 = f(x)
    k2 = f(x + 0.5 * dt * k1)
    k3 = f(x + 0.5 * dt * k2)
    k4 = f(x + dt * k3)
    return x + dt * (k1 + 2 * k2 + 2 * k3 + k4) / 6.0


def march(h: Hump, v: float, g: float, dt: float, T: float, x0: float) -> dict:
    """The point from x0 at the steady speed v for T seconds: RK4 along the road while N >= 0 (the
    leave point located by bisection on the step), the closed-form parabola in the air with the
    landing located by bisection, then along the road again. Samples (t, x, y, phase) at every step
    and at the events; every flight with its leave and landing data; the smallest road push."""
    t, x = 0.0, x0
    ts, xs, ys, ph = [0.0], [x0], [h.y(x0)], [0]
    flights: list[dict] = []
    n_min, x_nmin, t_nmin = h.N(x0, v, g), x0, 0.0
    steps = 0
    while t < T - 1e-12:
        n_here = h.N(x, v, g)
        if n_here < n_min:
            n_min, x_nmin, t_nmin = n_here, x, t
        x_new = rk4_x(h, x, v, dt)
        if h.N(x_new, v, g) >= 0.0:
            t, x = t + dt, x_new
            steps += 1
            ts.append(t), xs.append(x), ys.append(h.y(x)), ph.append(0)
            continue
        # The wheels leave inside this step: bisect the sub-step for N = 0.
        lo, hi = 0.0, dt
        for _ in range(60):
            mid = 0.5 * (lo + hi)
            if h.N(rk4_x(h, x, v, mid), v, g) < 0.0:
                hi = mid
            else:
                lo = mid
        t_leave, x_leave = t + lo, rk4_x(h, x, v, lo)
        y_leave = h.y(x_leave)
        n_min, x_nmin, t_nmin = min(n_min, 0.0), x_leave, t_leave
        theta0 = math.atan(h.yp(x_leave))
        vx, vy = v * math.cos(theta0), v * math.sin(theta0)
        ts.append(t_leave), xs.append(x_leave), ys.append(y_leave), ph.append(1)

        def gap(tf: float) -> float:
            return y_leave + vy * tf - 0.5 * g * tf * tf - h.y(x_leave + vx * tf)

        tf, gmax, t_gmax = 0.0, 0.0, 0.0
        gaps = [(0.0, 0.0)]
        while True:
            tf_new = tf + dt
            gg = gap(tf_new)
            if gg < 0.0 and tf_new > dt:
                break
            tf = tf_new
            gaps.append((tf, gg))
            if gg > gmax:
                gmax, t_gmax = gg, tf
            ts.append(t_leave + tf), xs.append(x_leave + vx * tf)
            ys.append(y_leave + vy * tf - 0.5 * g * tf * tf), ph.append(1)
            steps += 1
            if tf > 60.0:
                raise RuntimeError("no landing")
        lo, hi = tf, tf + dt
        for _ in range(60):
            mid = 0.5 * (lo + hi)
            if gap(mid) < 0.0:
                hi = mid
            else:
                lo = mid
        t_fl = lo
        # Refine the largest gap by golden section between the neighbouring samples.
        a, b = max(0.0, t_gmax - dt), min(t_fl, t_gmax + dt)
        phi = (math.sqrt(5.0) - 1.0) / 2.0
        c, d = b - phi * (b - a), a + phi * (b - a)
        for _ in range(80):
            if gap(c) > gap(d):
                b, d = d, c
                c = b - phi * (b - a)
            else:
                a, c = c, d
                d = a + phi * (b - a)
        t_gmax = 0.5 * (a + b)
        gmax = gap(t_gmax)
        x_land = x_leave + vx * t_fl
        vy_land = vy - g * t_fl
        p_land = h.yp(x_land)
        v_norm = (-vx * p_land + vy_land) / math.sqrt(1.0 + p_land * p_land)   # along the road's up normal
        t_crest = -x_leave / vx if x_leave < 0.0 < x_land else None
        flights.append({
            "t_leave": t_leave, "x_leave": x_leave, "y_leave": y_leave, "theta0": theta0, "vx": vx, "vy": vy,
            "t_flight": t_fl, "t_land": t_leave + t_fl, "x_land": x_land, "y_land": h.y(x_land),
            "length": x_land - x_leave, "gap_max": gmax, "t_gap_max": t_gmax, "x_gap_max": x_leave + vx * t_gmax,
            "vy_land": vy_land, "v_norm_land": v_norm, "apex": y_leave + vy * vy / (2.0 * g),
            "t_crest": t_crest, "gap_crest": gap(t_crest) if t_crest is not None else None,
            "n_before": h.N(x_leave - 1e-6, v, g), "n_after": h.N(x_leave + 1e-6, v, g),
        })
        t, x = t_leave + t_fl, x_land
        ts.append(t), xs.append(x), ys.append(h.y(x)), ph.append(0)
    return {"v": v, "t": np.array(ts), "x": np.array(xs), "y": np.array(ys), "phase": np.array(ph),
            "flights": flights, "n_min": n_min, "x_nmin": x_nmin, "t_nmin": t_nmin, "steps": steps,
            "x_end": x, "T": T}


def crest_time(run: dict) -> float:
    """When the point passes x = 0 (on the road or in the air)."""
    xs, ts = run["x"], run["t"]
    i = int(np.searchsorted(xs, 0.0))
    if i <= 0 or i >= len(xs):
        return float("nan")
    return float(ts[i - 1] + (0.0 - xs[i - 1]) / (xs[i] - xs[i - 1]) * (ts[i] - ts[i - 1]))


def leave_by_bisection(h: Hump, v: float, g: float) -> float | None:
    """N(x) = 0 on the approach, solved by bisection on x in [-L/4, 0] (N > 0 at -L/4, where y'' = 0)."""
    a, b = -h.L / 4.0, 0.0
    if h.N(b, v, g) >= 0.0:
        return None
    assert h.N(a, v, g) > 0.0
    for _ in range(200):
        m = 0.5 * (a + b)
        if h.N(m, v, g) < 0.0:
            b = m
        else:
            a = m
    return 0.5 * (a + b)


def kmh(v: float) -> float:
    return v * 3.6


def ms(v_kmh: float) -> float:
    return v_kmh / 3.6


def run_for(man: dict, h: Hump, v_kmh: float, dt: float, T: float) -> dict:
    """march() for a speed in km/h, with the road, g and the car's wheel geometry attached for state_at
    and the drawing."""
    run = march(h, ms(v_kmh), man["g"], dt, T, man["start_x_m"])
    run["h"], run["g"] = h, man["g"]
    run["wheel_radius"], run["half_wheelbase"] = man["wheel_radius_m"], man["wheelbase_m"] / 2.0
    return run


def flight_text(fl: dict | None, v_kmh: float, h: Hump, g: float, run: dict) -> str:
    if fl is None:
        return (f"{v_kmh:g} km/h ({ms(v_kmh):.4f} m/s): the wheels never leave; the road push bottoms at "
                f"{run['n_min'] / g:.4f} of the weight at x = {run['x_nmin']:+.3f} m (closed form at the crest 1 - "
                f"v^2 / (g R) = {1.0 - ms(v_kmh) ** 2 / (g * h.R):.4f})")
    return (f"{v_kmh:g} km/h ({ms(v_kmh):.4f} m/s): the wheels leave {-fl['x_leave']:.3f} m before the crest (x = "
            f"{fl['x_leave']:+.4f} m, slope {math.degrees(fl['theta0']):.2f} deg, {fl['t_leave']:.4f} s after the start), "
            f"the car is in the air for {fl['length']:.3f} m and {fl['t_flight']:.4f} s, at most {fl['gap_max']:.4f} m "
            f"({fl['gap_max'] * 100:.1f} cm) above the road at x = {fl['x_gap_max']:+.3f} m, "
            + (f"{fl['gap_crest']:.4f} m above the crest as it passes it, " if fl['gap_crest'] is not None else "")
            + f"and lands {fl['x_land']:.3f} m past the crest at {fl['t_land']:.4f} s with {-fl['vy_land']:.3f} m/s of "
            f"downward speed ({-fl['v_norm_land']:.3f} m/s into the road)")


def measure(man: dict) -> dict:
    g = man["g"]
    h = Hump(man["hump_height_m"], man["hump_length_m"])
    slow_kmh, fast_kmh = man["speeds_km_h"]
    dt, slow = man["step_s"], man["slow_motion"]
    P, D, fps, F = man["cycle_s"], man["scene_duration"], man["fps"], man["reset_fade"]
    x0 = man["start_x_m"]
    cycles = D / P
    assert abs(cycles - round(cycles)) < 1e-9, "the cycle must divide the scene length"
    for key in ("cycle_s", "first_cycle_at", "reset_fade"):
        assert abs(man[key] * fps - round(man[key] * fps)) < 1e-9, f"{key} must be a whole number of frames"
    ppm = man["px_per_m"]
    T = P / slow
    v_lim = math.sqrt(g * h.R)
    steep = math.degrees(math.atan(math.pi * h.H / h.L))
    print(f"setup: the same humpback bridge in both panels, a cosine hump H = {h.H:g} m high and L = {h.L:g} m long "
          f"on a flat road, y(x) = (H / 2)(1 + cos(2 pi x / L)) for |x| <= L / 2 (it joins the road with zero slope); "
          f"crest radius R = L^2 / (2 pi^2 H) = {h.R:.4f} m, steepest slope atan(pi H / L) = {steep:.2f} degrees; the "
          f"car is a point moving along the road at a steady speed (the engine holds the speed; no suspension), "
          f"g = {g:g} m/s^2; on the road the push per unit mass is N = g cos(theta) - v^2 kappa, the wheels leave "
          f"where N reaches zero, fly on the parabola from the tangent velocity and land where it meets the road "
          f"(bisection); the landing takes the vertical speed; at the crest N = g - v^2 / R, so the limit is "
          f"v* = sqrt(g R) = {v_lim:.4f} m/s = {kmh(v_lim):.2f} km/h (about {kmh(v_lim):.0f} km/h), whatever the car "
          f"weighs; top panel {slow_kmh:g} km/h, bottom panel {fast_kmh:g} km/h; stepped at dt = {dt:.0e} s (RK4 "
          f"along the road, the leave point by bisection inside the step, the closed-form parabola in the air, the "
          f"landing by bisection), checked against N = 0 solved by bisection on x and a half-step rerun; shown at "
          f"1/{slow:g} speed on a {P:g} s cycle ({P * fps:.0f} frames = {T:.4f} s of real time) with both cars "
          f"starting at x = {x0:g} m ({-x0 - h.L / 2:g} m before the hump) at the cycle start, {cycles:.0f} cycles "
          f"in {D:g} s; drawn at {ppm:g} px per metre; deterministic, no seed")
    runs = {"slow": run_for(man, h, slow_kmh, dt, T), "fast": run_for(man, h, fast_kmh, dt, T)}
    ev: dict = {"runs": runs, "hump": h, "v_lim": v_lim, "steep": steep, "kmh": {"slow": slow_kmh, "fast": fast_kmh}}
    for m in PANELS:
        run = runs[m]
        fl = run["flights"][0] if run["flights"] else None
        run["t_crest"] = crest_time(run)
        print(f"{m} panel, " + flight_text(fl, ev["kmh"][m], h, g, run)
              + f"; passes the crest at {run['t_crest']:.4f} s; {len(run['flights'])} flight(s) in the "
              f"{T:.4f} s run; ends at x = {run['x_end']:+.3f} m ({run['x_end'] - h.L / 2:.2f} m past the hump); "
              f"{run['steps']} steps")
    s, f = runs["slow"], runs["fast"]
    assert not s["flights"] and len(f["flights"]) == 1, "the panels must end differently: slow down, fast in the air"
    fl = f["flights"][0]
    ev["flight"] = fl
    print(f"the two panels: at {slow_kmh:g} km/h the wheels stay on the road, the push never under "
          f"{s['n_min'] / g:.4f} of the weight (at the crest); at {fast_kmh:g} km/h the wheels leave {-fl['x_leave']:.2f} m "
          f"before the crest and the car is in the air for {fl['length']:.2f} m ({fl['length']:.0f} m) and "
          f"{fl['t_flight']:.2f} s, at most {fl['gap_max'] * 100:.0f} cm above the road; the limit between them is "
          f"{kmh(v_lim):.1f} km/h ({kmh(v_lim):.0f} km/h); the parabola's apex is {fl['apex']:.4f} m, "
          f"{fl['apex'] - h.H:+.4f} m against the crest")
    # Checks: the leave point against N = 0 solved by bisection on x; a half-step rerun.
    xb = leave_by_bisection(h, ms(fast_kmh), g)
    assert xb is not None
    print(f"check, leave point: N = 0 solved by bisection on x gives x = {xb:+.6f} m; the march left at "
          f"{fl['x_leave']:+.6f} m (diff {fl['x_leave'] - xb:+.1e} m); N just before the leave {fl['n_before'] / g:+.1e} g, "
          f"just after {fl['n_after'] / g:+.1e} g")
    half = run_for(man, h, fast_kmh, 0.5 * dt, T)
    hf = half["flights"][0]
    print(f"check at half the time step ({0.5 * dt:.0e} s), {fast_kmh:g} km/h: leaves at x = {hf['x_leave']:+.6f} m "
          f"({hf['x_leave'] - fl['x_leave']:+.1e}), {hf['t_leave']:.6f} s ({hf['t_leave'] - fl['t_leave']:+.1e}); in the "
          f"air {hf['length']:.6f} m ({hf['length'] - fl['length']:+.1e}) and {hf['t_flight']:.6f} s "
          f"({hf['t_flight'] - fl['t_flight']:+.1e}); gap {hf['gap_max']:.6f} m ({hf['gap_max'] - fl['gap_max']:+.1e}); "
          f"lands at x = {hf['x_land']:+.6f} m ({hf['x_land'] - fl['x_land']:+.1e}) with {-hf['vy_land']:.6f} m/s down "
          f"({-hf['vy_land'] + fl['vy_land']:+.1e}); the flight is the closed-form parabola x = x0 + vx t, y = y0 + vy t "
          f"- g t^2 / 2 from vx = {fl['vx']:.4f}, vy = {fl['vy']:.4f} m/s, so halving the step only moves the landing root")
    half_s = run_for(man, h, slow_kmh, 0.5 * dt, T)
    print(f"check at half the time step, {slow_kmh:g} km/h: no flight, push bottoms at {half_s['n_min'] / g:.6f} of the "
          f"weight ({(half_s['n_min'] - s['n_min']) / g:+.1e}) at x = {half_s['x_nmin']:+.4f} m; crest at "
          f"{crest_time(half_s):.6f} s ({crest_time(half_s) - s['t_crest']:+.1e})")
    # Description-only cases.
    ev["descr"] = {}
    parts = []
    for v_kmh in man["description_speeds_km_h"]:
        rr = run_for(man, h, v_kmh, dt, 2.0 * T)
        f0 = rr["flights"][0] if rr["flights"] else None
        ev["descr"][v_kmh] = {"run": rr, "flight": f0, "n_crest": h.N(0.0, ms(v_kmh), g) / g}
        parts.append(flight_text(f0, v_kmh, h, g, rr) + f"; N at the crest {h.N(0.0, ms(v_kmh), g) / g:+.4f} g")
    print("for the description, the same hump: " + "; ".join(parts))
    rh, rl = man["research_hump"]
    h2 = Hump(rh, rl)
    v2 = math.sqrt(g * h2.R)
    r2 = run_for(man, h2, fast_kmh, dt, 2.0 * T)
    f2 = r2["flights"][0] if r2["flights"] else None
    ev["research"] = {"hump": h2, "v_lim": v2, "flight": f2}
    print(f"for the description, the research entry's hump {rh:g} m high and {rl:g} m long: crest radius "
          f"{h2.R:.4f} m, limit sqrt(g R) = {v2:.4f} m/s = {kmh(v2):.2f} km/h; " + flight_text(f2, fast_kmh, h2, g, r2))
    # Schedule in video time.
    t0 = man["first_cycle_at"]
    k0 = math.ceil((0.0 - t0) / P - 1e-9) - 1
    k1 = math.floor((D - t0) / P - 1e-9)
    starts = [t0 + k * P for k in range(k0, k1 + 1)]
    ev["cycles"] = int(round(cycles))

    def lst(off_: float) -> str:
        return ", ".join(f"{st + off_:.2f}" for st in starts if 0.0 <= st + off_ < D)

    tau0 = (0.0 - t0) % P
    st0 = {m: state_at(runs[m], tau0 / slow) for m in PANELS}
    print(f"schedule (video time at 1/{slow:g} speed): cycles of {P:g} s start at "
          + ", ".join(f"{st:.2f}" for st in starts)
          + f" s (the first {-t0:.2f} s before the first frame); both cars start at x = {x0:g} m at each cycle start; "
          f"the {fast_kmh:g} km/h car leaves the road {fl['t_leave'] * slow:.2f} s into the cycle "
          f"({fl['t_leave']:.4f} s real) at {lst(fl['t_leave'] * slow)} s, passes the crest {f['t_crest'] * slow:.2f} s in "
          f"at {lst(f['t_crest'] * slow)} s and lands {fl['t_land'] * slow:.2f} s in ({fl['t_land']:.4f} s real) at "
          f"{lst(fl['t_land'] * slow)} s, {fl['t_flight'] * slow:.2f} s of video in the air; the {slow_kmh:g} km/h car "
          f"passes the crest {s['t_crest'] * slow:.2f} s in ({s['t_crest']:.4f} s real) at {lst(s['t_crest'] * slow)} s; "
          f"at the cycle end the {slow_kmh:g} km/h car is at x = {s['x_end']:+.2f} m and the {fast_kmh:g} km/h car at "
          f"x = {f['x_end']:+.2f} m; the reset crossfade runs over the last {F:g} s of each cycle (the readouts out "
          f"from {lst(P - F)} s, the fresh cars in from {lst(P - F / 2)} s); on the first frame the cycle is {tau0:.2f} s "
          f"in ({tau0 / slow:.4f} s real: the {slow_kmh:g} km/h car at x = {st0['slow']['x']:+.2f} m, {st0['slow']['phase']}, "
          f"push {st0['slow']['n']:.3f}; the {fast_kmh:g} km/h car at x = {st0['fast']['x']:+.2f} m, {st0['fast']['phase']}, "
          f"gap {st0['fast']['gap'] * 100:.1f} cm); title until {man['title_until']:g} s; payoff card from "
          f"{man['payoff_t']:g} s; the title fades back in over the last {man['loop_fade']:g} s and the last frame "
          f"repeats the first (the scene is periodic: {D:g} s holds exactly {cycles:.0f} cycles)")
    # Text widths.
    font = os.environ["SEED_ZERO_FONT"]
    f24, f28, f34, f40, f56 = (ImageFont.truetype(font, n) for n in (24, 28, 34, 40, 56))
    widths = {"overlay@34": (f34, man["overlay"])}
    for j, line in enumerate(man["title"].split("|")):
        widths[f"title line {j + 1}@56"] = (f56, line)
    widths["legend@40"] = (f40, legend_text(man))
    widths["clock@28"] = (f28, clock_text(3.3333))
    x_far = max(abs(x0), abs(s["x_end"]), abs(f["x_end"]))
    for m in PANELS:
        widths[f"label {m}@40"] = (f40, label_text(ev, m))
        widths[f"push {m}@28"] = (f28, push_text(ROAD, 0.3534))
        widths[f"push air {m}@28"] = (f28, push_text(AIR, 0.0))
        widths[f"where {m} before@28"] = (f28, where_text(-x_far))
        widths[f"where {m} past@28"] = (f28, where_text(x_far))
        widths[f"event {m}@28"] = (f28, event_text(ev, m))
    widths["gap@28"] = (f28, gap_text(fl["gap_max"]))
    widths["crest@24"] = (f24, "crest")
    for j, line in enumerate(payoff_lines(man, ev)):
        widths[f"payoff line {j + 1}@40"] = (f40, line)
    print("text widths: " + ", ".join(f"{k} {f_.getlength(s_):.0f} px" for k, (f_, s_) in widths.items()))
    assert all(f_.getlength(s_) < 950 for f_, s_ in widths.values()), "a text line is wider than 950 px"
    assert len(payoff_lines(man, ev)) <= 6, "more than six card lines"
    # Layout checks.
    left = ROW_X0 + max(max(f40.getlength(label_text(ev, m)), f28.getlength(push_text(ROAD, 0.3534)),
                            f28.getlength(push_text(AIR, 0.0)), f28.getlength(event_text(ev, m))) for m in PANELS)
    right = ROW_X1 - max(f28.getlength(where_text(-x_far)), f28.getlength(where_text(x_far)))
    gap_w = f28.getlength(gap_text(fl["gap_max"]))
    # The car's highest and lowest drawn points over a whole cycle, frame by frame, both panels.
    roof_min, floor_max, roof_at = 1e9, -1e9, ("", 0.0)
    for m in PANELS:
        for fi in range(int(round(P * fps))):
            st = state_at(runs[m], fi / fps / slow)
            st["run"] = runs[m]
            pts = car_points(st, ppm)
            top = min(p[1] for p in pts)
            if top < roof_min:
                roof_min, roof_at = top, (m, fi / fps)
            floor_max = max(floor_max, max(p[1] for p in pts))
    crest_top = ROAD_DY - h.H * ppm
    print(f"row check: the left column ends at x {left:.0f} px, the right column starts at x {right:.0f} px; the rows "
          f"end {ROWS_BOTTOM} px under the band top; the minimap strip spans x {MINI_X0} to {MINI_X1}, y {MINI_TOP_DY} to "
          f"{MINI_BASE_DY + 6} under the band top; the flat road is {ROAD_DY} px under the band top and the crest "
          f"{crest_top:.0f} px; the car's highest drawn point over a cycle is {roof_min:.1f} px under the band top "
          f"({roof_at[0]} panel, {roof_at[1]:.2f} s into the cycle) and its lowest {floor_max:.1f} px; the gap readout "
          f"is centred at x {CAR_X} ({gap_w:.0f} px wide), {GAP_TEXT_DY} px under the band top inside the slab; each "
          f"band is {BAND_H} px tall (y {BAND_Y['slow']} to {BAND_Y['slow'] + BAND_H} and {BAND_Y['fast']} to "
          f"{BAND_Y['fast'] + BAND_H}); the caption band starts at y {int(man['caption_y'] * H)}; the title rows end at "
          f"y {252 + 28} and the overlay band ends at y 130")
    assert right - left > 40, "the columns meet"
    assert ROW_X0 + f28.getlength(push_text(ROAD, 0.3534)) < MINI_X0 - 40, "the push readout meets the minimap"
    assert roof_min > ROWS_BOTTOM + 6, "the car's roof enters the readout rows"
    assert floor_max < BAND_H - 4, "the car leaves the band at the bottom"
    assert GAP_TEXT_DY - 16 > ROAD_DY + 8 and GAP_TEXT_DY + 16 < BAND_H, "the gap readout leaves the slab"
    assert CAR_X - gap_w / 2 > 20 and CAR_X + gap_w / 2 < W - 20, "the gap readout leaves the frame"
    assert BAND_Y["fast"] + BAND_H <= int(man["caption_y"] * H), "the fast band reaches the caption band"
    assert 252 + 28 < BAND_Y["slow"], "the title rows reach the first band"
    return ev


def state_at(run: dict, r: float) -> dict:
    """(x, y, phase, gap, n, landed, crest) of the car r real seconds after the cycle start."""
    r = max(0.0, min(float(run["t"][-1]), r))
    x = float(np.interp(r, run["t"], run["x"]))
    fl = run["flights"][0] if run["flights"] else None
    if fl is not None and fl["t_leave"] <= r < fl["t_land"]:
        tf = r - fl["t_leave"]
        x = fl["x_leave"] + fl["vx"] * tf
        y = fl["y_leave"] + fl["vy"] * tf - 0.5 * run["g"] * tf * tf
        phase, n, landed = AIR, 0.0, False
    else:
        y = run["h"].y(x)
        phase, landed = ROAD, fl is not None and r >= fl["t_land"]
        n = run["h"].N(x, run["v"], run["g"]) / run["g"]
    return {"x": x, "y": y, "phase": phase, "gap": max(0.0, y - run["h"].y(x)), "n": n, "landed": landed,
            "crest": x >= 0.0, "r": r}


def car_frame(st: dict, run: dict) -> tuple[float, float, float]:
    """The car's drawn pivot (world x, y) and pitch: on the road the chord between the two wheel contacts
    (both wheels sit on the road); in the air the point flies on the parabola and the drawn pitch turns
    evenly from the take-off chord to the landing chord over the flight, so the car leaves and lands on
    its wheels (the point model has no attitude; a car holding its take-off angle would put its rear
    wheel through the road at the landing, where the road is 18 degrees steeper than at the take-off)."""
    h, hb = run["h"], run["half_wheelbase"]
    fl = run["flights"][0] if run["flights"] else None

    def chord(xc: float) -> tuple[float, float, float]:
        xr, xf = xc - hb, xc + hb
        yr, yf = h.y(xr), h.y(xf)
        return 0.5 * (xr + xf), 0.5 * (yr + yf), math.atan2(yf - yr, xf - xr)

    if st["phase"] == ROAD or fl is None:
        return chord(st["x"])
    s = (st["r"] - fl["t_leave"]) / fl["t_flight"]
    _, y0, phi0 = chord(fl["x_leave"])
    _, y1, phi1 = chord(fl["x_land"])
    off = (y0 - fl["y_leave"]) * (1.0 - s) + (y1 - fl["y_land"]) * s
    return st["x"], st["y"] + off, phi0 * (1.0 - s) + phi1 * s


def car_points(st: dict, ppm: float) -> list[tuple[float, float]]:
    """Band-local screen points of the car body corners and wheel extremes (1x px)."""
    run = st["run"]
    px, py, phi = car_frame(st, run)
    c, s = math.cos(phi), math.sin(phi)
    pts = []
    for u, w in BODY:
        pts.append((CAR_X + (px - st["x"] + u * c - w * s) * ppm, ROAD_DY - (py + u * s + w * c) * ppm))
    rw, hb = run["wheel_radius"], run["half_wheelbase"]
    for u in (-hb, hb):
        cx = CAR_X + (px - st["x"] + u * c - rw * s) * ppm
        cy = ROAD_DY - (py + u * s + rw * c) * ppm
        pts += [(cx, cy - rw * ppm), (cx, cy + rw * ppm)]
    return pts


def legend_text(man: dict) -> str:
    a, b = man["speeds_km_h"]
    return f"same hump, {a:g} and {b:g} km/h, 1/{man['slow_motion']:g} speed"


def clock_text(r: float) -> str:
    return f"real time {r:.2f} s, shown at 1/3 speed"


def label_text(ev: dict, m: str) -> str:
    return f"{ev['kmh'][m]:g} km/h"


def push_text(phase: str, n: float) -> str:
    return "road push: none, in the air" if phase == AIR else f"road push {max(0.0, n):.2f} of the car's weight"


def where_text(x: float) -> str:
    return f"{-x:.1f} m before the crest" if x < 0.0 else f"{x:.1f} m past the crest"


def event_text(ev: dict, m: str) -> str:
    if m == "slow":
        return "wheels stay on the road"
    fl = ev["flight"]
    return f"in the air {fl['length']:.1f} m, {fl['t_flight']:.2f} s"


def gap_text(gap: float) -> str:
    return f"wheels {gap * 100:.0f} cm off the road"


def payoff_lines(man: dict, ev: dict) -> list[str]:
    fl, h = ev["flight"], ev["hump"]
    d55 = ev["descr"].get(55)
    f55 = d55["flight"] if d55 else None
    text = man["payoff_text"].format(
        flight=fl["length"], t_flight=fl["t_flight"], gap_cm=fl["gap_max"] * 100, before=-fl["x_leave"],
        v_lim=kmh(ev["v_lim"]), R=h.R, flight55=f55["length"] if f55 else 0.0,
        gap55_cm=f55["gap_max"] * 100 if f55 else 0.0)
    return [t.strip() for t in text.split("|")]


# --- rendering -----------------------------------------------------------------
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
        self.h: Hump = ev["hump"]
        self.slow = man["slow_motion"]
        self.P = man["cycle_s"]
        self.P_f = int(round(man["cycle_s"] * self.fps))
        self.c0_f = int(round(man["first_cycle_at"] * self.fps))
        self.F = man["reset_fade"]
        self.runs = ev["runs"]
        self.x_lo = -self.h.L / 2.0 - 4.5
        self.x_hi = self.h.L / 2.0 + 21.0

    def phase(self, f: int) -> tuple[int, float]:
        k, tau_f = divmod(f - self.c0_f, self.P_f)
        return k, tau_f / self.fps

    @staticmethod
    def L(x: float, y: float) -> tuple[float, float]:
        """Layer (2x) pixel of a band-local point, rounded to 1e-4 px so equal states draw equal pixels."""
        return round(x * SS, 4), round(y * SS, 4)

    def S(self, st: dict, X: float, Y: float) -> tuple[float, float]:
        """Band-local 1x screen point of a world point (the camera follows the car's x)."""
        return CAR_X + (X - st["x"]) * self.ppm, ROAD_DY - Y * self.ppm

    def surface(self, st: dict, xa: float, xb: float, below: float = 0.0, step: float = 0.05) -> list:
        n = max(1, int(math.ceil((xb - xa) / step)))
        pts = []
        for i in range(n + 1):
            X = xa + (xb - xa) * i / n
            sx, sy = self.S(st, X, self.h.y(X))
            pts.append(self.L(sx, sy + below))
        return pts

    def draw_road(self, d: ImageDraw.ImageDraw, st: dict, run: dict) -> None:
        xa = st["x"] - CAR_X / self.ppm - 0.3
        xb = st["x"] + (W - CAR_X) / self.ppm + 0.3
        surf = self.surface(st, xa, xb)
        d.polygon(surf + [self.L(W + 10, BAND_H + 10), self.L(-10, BAND_H + 10)], fill=SLAB)
        # Lane dashes fixed to the road, so they scroll under the car at its speed; each is smeared
        # over one frame's travel (motion blur, no strobing) and dimmed by the same ratio.
        period, dash = self.man["dash_period_m"], self.man["dash_m"]
        travel = st["vx"] / self.slow / self.fps
        col = blend(DASH, dash / (dash + travel) * 0.85, SLAB)
        k = math.floor((xa - dash - travel) / period)
        while k * period < xb + travel:
            da, db = max(xa, k * period - travel), min(xb, k * period + dash)
            if db > da:
                d.line(self.surface(st, da, db, below=7.0), fill=col, width=4 * SS, joint="curve")
            k += 1
        d.line(surf, fill=SURF, width=3 * SS, joint="curve")
        # The crest marker: a gold notch under the surface at x = 0.
        cx, cy = self.S(st, 0.0, self.h.H)
        if -40 < cx < W + 40:
            m0, m1, m2 = self.L(cx, cy + 3), self.L(cx - 9, cy + 18), self.L(cx + 9, cy + 18)
            d.polygon([m0, m1, m2], fill=GOLD)
        # The minimap: the whole hump in a strip at the top right, a dot for the car.
        mx0, mx1 = self.man["minimap_x_range"]
        sx_m = (MINI_X1 - MINI_X0) / (mx1 - mx0)
        sy_m = (MINI_BASE_DY - MINI_TOP_DY - 7) / self.h.H
        pts = []
        n = 120
        for i in range(n + 1):
            X = mx0 + (mx1 - mx0) * i / n
            pts.append(self.L(MINI_X0 + (X - mx0) * sx_m, MINI_BASE_DY - self.h.y(X) * sy_m))
        d.line(pts, fill=MINI, width=2 * SS, joint="curve")
        cxm, cym = self.L(MINI_X0 + (0.0 - mx0) * sx_m, MINI_BASE_DY - self.h.H * sy_m)
        d.line((cxm, cym - 3 * SS, cxm, cym - 9 * SS), fill=GOLD, width=2 * SS)
        X = max(mx0, min(mx1, st["x"]))
        dx, dy = self.L(MINI_X0 + (X - mx0) * sx_m, MINI_BASE_DY - st["y"] * sy_m)
        rr = 5 * SS
        d.ellipse((dx - rr, dy - rr, dx + rr, dy + rr), fill=COLOUR[st["panel"]])

    def draw_car(self, d: ImageDraw.ImageDraw, st: dict, run: dict) -> None:
        px, py, phi = car_frame(st, run)
        c, s = math.cos(phi), math.sin(phi)
        col = COLOUR[st["panel"]]

        def pt(u: float, w: float) -> tuple[float, float]:
            return self.L(*self.S(st, px + u * c - w * s, py + u * s + w * c))

        if st["phase"] == AIR and st["gap"] > 0.005:
            # The shadow on the road under the car, then the dashed gap line at the car's point, straight
            # down from the point to the road (the measured gap).
            d.line(self.surface(st, st["x"] - 2.0, st["x"] + 2.0), fill=SHADOW, width=13 * SS, joint="curve")
            top = self.S(st, st["x"], st["y"])
            bot = self.S(st, st["x"], self.h.y(st["x"]))
            length = bot[1] - top[1]
            y_ = 0.0
            while y_ < length:
                e = min(length, y_ + 7.0)
                a0, a1 = self.L(top[0], top[1] + y_), self.L(top[0], top[1] + e)
                d.line((*a0, *a1), fill=GOLD, width=4 * SS)
                y_ = e + 5.0
            for yy in (top[1], bot[1]):
                t0, t1 = self.L(top[0] - 12, yy), self.L(top[0] + 12, yy)
                d.line((*t0, *t1), fill=GOLD, width=4 * SS)
        body = [pt(u, w) for u, w in BODY]
        d.polygon(body, fill=col, outline=blend(col, 0.55, (0, 0, 0)), width=2 * SS)
        for glass in (GLASS_FRONT, GLASS_REAR):
            d.polygon([pt(u, w) for u, w in glass], fill=GLASS)
        d.polygon([pt(2.0, 0.50), pt(2.0, 0.64), pt(1.84, 0.64), pt(1.84, 0.50)], fill=LAMP)
        d.polygon([pt(-2.0, 0.50), pt(-2.0, 0.66), pt(-1.86, 0.66), pt(-1.86, 0.50)], fill=TAIL)
        rw, hb = run["wheel_radius"], run["half_wheelbase"]
        for u in (-hb, hb):
            cx, cy = pt(u, rw)
            rl = rw * self.ppm * SS
            d.ellipse((cx - rl, cy - rl, cx + rl, cy + rl), fill=WHEEL, outline=RIM, width=2 * SS)
            rh = 0.35 * rl
            d.ellipse((cx - rh, cy - rh, cx + rh, cy + rh), fill=RIM)

    def state(self, m: str, r: float) -> dict:
        run = self.runs[m]
        st = state_at(run, r)
        st["run"], st["panel"] = run, m
        fl = run["flights"][0] if run["flights"] else None
        if st["phase"] == AIR and fl is not None:
            st["vx"] = fl["vx"]
        else:
            st["vx"] = run["v"] * self.h.cos_theta(st["x"])
        return st

    def draw_scene(self, m: str, r: float) -> tuple[Image.Image, dict]:
        layer = Image.new("RGB", (W * SS, BAND_H * SS), BG)
        d = ImageDraw.Draw(layer)
        st = self.state(m, r)
        self.draw_road(d, st, self.runs[m])
        self.draw_car(d, st, self.runs[m])
        return layer, st

    def draw_panel(self, m: str, f: int) -> tuple[Image.Image, dict]:
        k, tau = self.phase(f)
        F, P = self.F, self.P
        layer, st = self.draw_scene(m, tau / self.slow)
        a_old = 1.0 if tau <= P - F else max(0.0, (P - F / 2.0 - tau) / (F / 2.0))
        st["alpha"], st["k"], st["tau"] = a_old, k, tau
        if tau >= P - F / 2.0:
            a_new = (tau - (P - F / 2.0)) / (F / 2.0)
            fresh, st_new = self.draw_scene(m, (tau - P) / self.slow)
            st_new["alpha"], st_new["k"], st_new["tau"] = a_new, k + 1, tau - P
            layer = Image.blend(layer, fresh, a_new)
            if a_new >= 0.5:
                st = st_new
        return layer, st

    def draw_text(self, d: ImageDraw.ImageDraw, states: dict, hud_alpha: float) -> None:
        man, ev = self.man, self.ev
        for m, st in states.items():
            y0 = BAND_Y[m]
            a = st["alpha"]
            run = self.runs[m]
            d.text((ROW_X0, y0 + LABEL_DY), label_text(ev, m), font=self.font, fill=COLOUR[m], anchor="lm")
            d.text((ROW_X1, y0 + LABEL_DY), where_text(st["x"]), font=self.font_small, fill=blend(TEXT, a), anchor="rm")
            at_min = st["phase"] == AIR or (m == "slow" and st["n"] <= run["n_min"] / run["g"] + 0.02)
            d.text((ROW_X0, y0 + SUB_DY), push_text(st["phase"], st["n"]), font=self.font_small,
                   fill=blend(GOLD if at_min else TEXT, a), anchor="lm")
            lit = st["crest"] if m == "slow" else st["landed"]
            if lit:
                d.text((ROW_X0, y0 + EVENT_DY), event_text(ev, m), font=self.font_small, fill=blend(GOLD, a), anchor="lm")
            if st["phase"] == AIR and st["gap"] > 0.005:
                ag = a * min(1.0, st["gap"] / 0.03)
                d.text((CAR_X, y0 + GAP_TEXT_DY), gap_text(st["gap"]), font=self.font_small, fill=blend(GOLD, ag),
                       anchor="mm")
            cx, cy = self.S(st, 0.0, self.h.H)
            if 50 < cx < W - 50:
                d.text((cx, y0 + cy + CREST_TEXT_DY), "crest", font=self.font_tiny, fill=INK, anchor="mm")
        if hud_alpha > 0.02:
            d.text((W / 2, LEGEND_Y), legend_text(man), font=self.font, fill=blend(TEXT, hud_alpha), anchor="mm")
            d.text((W / 2, CLOCK_Y), clock_text(states["fast"]["r"]), font=self.font_small,
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
            # The geometry runs on; the legend, clock, event lines and card fade out over the first
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
    man = json.loads((ROOT / "projects/hump/manifest.json").read_text())
    ev = measure(man)
    if "--measure-only" in sys.argv:
        return
    if "--frames" in sys.argv:
        times = [float(v) for v in sys.argv[sys.argv.index("--frames") + 1].split(",")]
        r = Renderer(man, ev)
        (ROOT / "media/hump").mkdir(parents=True, exist_ok=True)
        for tv in times:
            Image.fromarray(r.frame_at(int(round(tv * man["fps"])))).save(ROOT / f"media/hump/smoke-{tv}.png")
        print("smoke frames: " + ", ".join(f"{tv}" for tv in times))
        return
    Renderer(man, ev).render(ROOT / "media/hump/footage.mp4")


if __name__ == "__main__":
    main()
