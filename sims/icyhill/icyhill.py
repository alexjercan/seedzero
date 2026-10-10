#!/usr/bin/env python3
"""Front-wheel drive on an icy hill: nose first, or in reverse?

Two panels on the same clock, the same hill drawn the same way at the same
scale, side view. A front-wheel-drive car of mass m, wheelbase L, with its
centre of mass b ahead of the rear axle and h above the road (a 60 / 40
front-to-rear static split gives b = 0.6 L), stands at rest on an icy hill
of slope theta with grip mu under the tyres (all chosen). The driver floors
it: the driven front wheels spin and push the car uphill with the most the
ice gives, mu N_front; the rear wheels roll free and push nothing. The
pitch of the hill and the acceleration a (uphill positive) move load onto
the downhill axle:

    N_front = m g cos(theta) (b / L)  -/+  m (g sin(theta) + a) (h / L)
    N_rear  = m g cos(theta) - N_front
    a = mu N_front / m - g sin(theta)

with the minus sign NOSE FIRST (the front axle uphill, unloaded) and the
plus sign IN REVERSE (the front axle downhill, loaded). Solved exactly,
x = N_front / (m g) = (b / L) cos(theta) / (1 +/- mu h / L): the sin terms
cancel, so a is constant and the car moves as s = a t^2 / 2 from rest. Top
panel: nose first. Bottom panel: in reverse (the same car turned round,
backing up the same hill). The hill the car can just climb has a = 0:
tan(theta*) = mu b / (L +/- mu h). Both runs are integrated by classical
RK4 at steps_per_second for run_s seconds (the loads computed from the
state at every stage) and checked against the closed form and a half-step
rerun. Real time: the run repeats every cycle_s seconds of video with a
crossfade back to the start; the cycle divides the scene length, so the
scene is exactly periodic and the last frame equals the first.
Deterministic, no seed.

Measured and printed: the axle loads at rest and during the run in both
panels, the acceleration and the distance after run_s seconds against the
closed forms and a half-step rerun, the steepest hill each way, the grip
and drive variants for the description, the brief's checks, the schedule
in video time, the on-screen text widths and the layout clearances.

usage: icyhill.py [--measure-only] [--frames t1,t2,...]
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
SLAB = (30, 34, 40)
ICE = (176, 206, 226)
ICE_DIM = (96, 116, 132)
WHEEL = (38, 42, 48)
RIM = (160, 166, 176)
GLASS = (14, 18, 24)
LAMP = (250, 236, 170)
TAIL = (220, 70, 60)
BAR_BG = (34, 40, 50)
REAR_BAR = (118, 128, 142)

# Layout: overlay at y 96..130 (captions.py), three title rows at y 186/244/302
# for the first seconds, then the legend at y 236 and the shared clock at y
# 290; two bands stacked, nose first in y 330..880 and in reverse in y
# 880..1430, each drawn at 2x in its own layer; each band has its label row
# 40 px under the band top, its second row at 84 and its third at 120 (left
# column from x 40: label, "front-wheel drive, 10 degree ice", speed; right
# column to x 1040: "moved", the front load text, the load bar at 108..124);
# the throttle gauge at the left under the rows; the road rises at the true
# slope through (start_x_px, road_y_px) with the slab under it to the band
# bottom; the car's wheel labels 22 px under the road; the gold event row
# (32 px) right-aligned at x 1040, 512 px under the band top, over the slab;
# captions at caption_y 0.75 (y 1440..1530); the card from y 1572 at a 48 px
# pitch.
LEGEND_Y, CLOCK_Y = 236, 290
TITLE_YS = {2: (190, 252), 3: (186, 244, 302)}
SS = 2
PAYOFF_Y, PAYOFF_PITCH = 1572.0, 48
PANELS = ("nose", "rev")
BAND_Y = {"nose": 330, "rev": 880}
BAND_H = 550
LABEL_DY, SUB_DY, FIX_DY, ROWS_BOTTOM = 40, 84, 120, 136
BAR_Y0, BAR_Y1, BAR_W = 108, 124, 320
EVENT_DY, EVENT_SIZE = 512, 32
ROW_X0, ROW_X1 = 40, 1040
GAUGE_X0, GAUGE_W, GAUGE_Y0, GAUGE_Y1, GAUGE_LABEL_DY = 80, 24, 160, 270, 290
WHEEL_LABEL_DY = 22
SPRAY_N = 7
COLOUR = {"nose": CORAL, "rev": TEAL}
FACING = {"nose": +1.0, "rev": -1.0}        # +1 the nose points uphill
REST, RUN, HOLD = "rest", "run", "hold"
DEG = math.pi / 180.0
# The car's outline in its own frame (u forward, w up, metres) for a 4.0 m car; u is scaled to car_length_m.
BODY = [(-2.0, 0.32), (2.0, 0.32), (2.0, 0.72), (1.35, 0.80), (0.85, 1.28), (-0.95, 1.30), (-1.72, 0.82),
        (-2.0, 0.72)]
GLASS_FRONT = [(0.10, 0.86), (1.22, 0.86), (0.78, 1.20), (0.10, 1.20)]
GLASS_REAR = [(-0.86, 0.86), (-0.02, 0.86), (-0.02, 1.20), (-0.88, 1.22)]


def blend(col, a: float, base=BG) -> tuple:
    a = max(0.0, min(1.0, a))
    return tuple(int(round(c * a + b * (1 - a))) for c, b in zip(col, base))


# --- measurement --------------------------------------------------------------
def front_share(b: float, L: float, h: float, mu: float, theta: float, facing: float) -> float:
    """x = N_front / (m g) with the driven front wheels spinning (closed form): the sin terms cancel.
    facing +1 nose first (front axle uphill), -1 in reverse (front axle downhill)."""
    return (b / L) * math.cos(theta) / (1.0 + facing * mu * h / L)


def front_share_at(b: float, L: float, h: float, g: float, theta: float, a: float, facing: float) -> float:
    """x = N_front / (m g) for a given acceleration a along the slope (uphill positive)."""
    return (b / L) * math.cos(theta) - facing * (math.sin(theta) + a / g) * (h / L)


def accel(mu: float, x: float, g: float, theta: float) -> float:
    return mu * x * g - g * math.sin(theta)


def steepest(b: float, L: float, h: float, mu: float, facing: float) -> float:
    """The hill with a = 0 (degrees): tan theta* = mu b / (L + facing mu h)."""
    return math.degrees(math.atan(mu * b / (L + facing * mu * h)))


def rk4_run(b: float, L: float, h: float, mu: float, g: float, theta: float, facing: float, T: float,
            dt: float) -> dict:
    """Integrate s'' = a(x) with x = N_front / (m g) solved from the load equation at every stage, from rest
    for T seconds by classical RK4 at dt. Returns the table (t, s, v) and the end state."""
    n = int(round(T / dt))
    assert abs(n * dt - T) < 1e-9, "the step must divide the run"

    def acc(_s: float, _v: float) -> float:
        x = front_share(b, L, h, mu, theta, facing)
        return accel(mu, x, g, theta)

    ts, ss, vs = [0.0], [0.0], [0.0]
    s, v = 0.0, 0.0
    for k in range(n):
        k1s, k1v = v, acc(s, v)
        k2s, k2v = v + 0.5 * dt * k1v, acc(s + 0.5 * dt * k1s, v + 0.5 * dt * k1v)
        k3s, k3v = v + 0.5 * dt * k2v, acc(s + 0.5 * dt * k2s, v + 0.5 * dt * k2v)
        k4s, k4v = v + dt * k3v, acc(s + dt * k3s, v + dt * k3v)
        s += dt * (k1s + 2.0 * k2s + 2.0 * k3s + k4s) / 6.0
        v += dt * (k1v + 2.0 * k2v + 2.0 * k3v + k4v) / 6.0
        ts.append((k + 1) * dt)
        ss.append(s)
        vs.append(v)
    x = front_share(b, L, h, mu, theta, facing)
    return {"t": np.array(ts), "s": np.array(ss), "v": np.array(vs), "s_end": s, "v_end": v, "a": accel(mu, x, g, theta),
            "x": x, "xr": math.cos(theta) - x, "x0": front_share_at(b, L, h, g, theta, 0.0, facing),
            "xr0": math.cos(theta) - front_share_at(b, L, h, g, theta, 0.0, facing), "steps": n, "T": T}


def state_at(run: dict, rt: float) -> dict:
    """(s, v, x, xr, phase) rt real seconds after the throttle; before it at rest with the brakes on (static
    loads), after run_s the readouts and the picture hold at the end state."""
    if rt < 0.0:
        return {"s": 0.0, "v": 0.0, "x": run["x0"], "xr": run["xr0"], "phase": REST}
    if rt < run["T"]:
        return {"s": float(np.interp(rt, run["t"], run["s"])), "v": float(np.interp(rt, run["t"], run["v"])),
                "x": run["x"], "xr": run["xr"], "phase": RUN}
    return {"s": run["s_end"], "v": run["v_end"], "x": run["x"], "xr": run["xr"], "phase": HOLD}


def car_points(man: dict, m: str, s_m: float, ev: dict) -> list[tuple[float, float]]:
    """Band-local 1x points of the car body corners and wheel extremes at displacement s_m (uphill +)."""
    th = ev["theta"]
    ppm = float(man["px_per_m"])
    x0, y0 = float(man["start_x_px"]), float(man["road_y_px"])
    px, py = x0 + s_m * ppm * math.cos(th), y0 - s_m * ppm * math.sin(th)
    fx, fy = FACING[m] * math.cos(th), -FACING[m] * math.sin(th)
    nx, ny = -math.sin(th), -math.cos(th)
    k = man["car_length_m"] / 4.0
    pts = []
    for u, w in BODY:
        u *= k
        pts.append((px + (u * fx + w * nx) * ppm, py + (u * fy + w * ny) * ppm))
    rw, hb = man["wheel_radius_m"], man["wheelbase_m"] / 2.0
    for u in (-hb, hb):
        cx, cy = px + (u * fx + rw * nx) * ppm, py + (u * fy + rw * ny) * ppm
        pts += [(cx - rw * ppm, cy - rw * ppm), (cx + rw * ppm, cy + rw * ppm)]
    return pts


def car_shapes(man: dict, m: str, s_m: float, ev: dict) -> list[list[tuple[float, float]]]:
    """Band-local 1x polygons of the car at displacement s_m: the body outline and the two wheel squares."""
    th = ev["theta"]
    ppm = float(man["px_per_m"])
    x0, y0 = float(man["start_x_px"]), float(man["road_y_px"])
    px, py = x0 + s_m * ppm * math.cos(th), y0 - s_m * ppm * math.sin(th)
    fx, fy = FACING[m] * math.cos(th), -FACING[m] * math.sin(th)
    nx, ny = -math.sin(th), -math.cos(th)
    k = man["car_length_m"] / 4.0
    body = [(px + (u * k * fx + w * nx) * ppm, py + (u * k * fy + w * ny) * ppm) for u, w in BODY]
    shapes = [body]
    rw, hb = man["wheel_radius_m"], man["wheelbase_m"] / 2.0
    for u in (-hb, hb):
        cx, cy = px + (u * fx + rw * nx) * ppm, py + (u * fy + rw * ny) * ppm
        r = rw * ppm
        shapes.append([(cx - r, cy - r), (cx + r, cy - r), (cx + r, cy + r), (cx - r, cy + r)])
    return shapes


def point_in_poly(x: float, y: float, poly: list[tuple[float, float]]) -> bool:
    inside = False
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        if (y1 > y) != (y2 > y):
            xi = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
            if xi > x:
                inside = not inside
    return inside


def segments_cross(a, b, c, d) -> bool:
    def orient(p, q, r) -> float:
        return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])
    o1, o2, o3, o4 = orient(a, b, c), orient(a, b, d), orient(c, d, a), orient(c, d, b)
    return (o1 * o2 < 0.0) and (o3 * o4 < 0.0)


def poly_meets_box(poly: list[tuple[float, float]], box: tuple[float, float, float, float]) -> bool:
    """True when the polygon and the box share any point (a vertex inside, a corner inside or crossing edges)."""
    x0, y0, x1, y1 = box
    if any(x0 <= x <= x1 and y0 <= y <= y1 for x, y in poly):
        return True
    corners = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    if any(point_in_poly(x, y, poly) for x, y in corners):
        return True
    n = len(poly)
    for i in range(n):
        for j in range(4):
            if segments_cross(poly[i], poly[(i + 1) % n], corners[j], corners[(j + 1) % 4]):
                return True
    return False


def bbox(pts: list[tuple[float, float]]) -> tuple[float, float, float, float]:
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    return min(xs), min(ys), max(xs), max(ys)


def union(a, b) -> tuple[float, float, float, float]:
    return min(a[0], b[0]), min(a[1], b[1]), max(a[2], b[2]), max(a[3], b[3])


def measure(man: dict) -> dict:
    g, m_kg, L, mu = man["g"], man["mass_kg"], man["wheelbase_m"], man["grip"]
    h, theta_deg = man["cg_height_m"], man["slope_deg"]
    b = man["front_static_share"] * L
    theta = theta_deg * DEG
    T, dt = man["run_s"], 1.0 / man["steps_per_second"]
    P, D, fps, F, ta = man["cycle_s"], man["scene_duration"], man["fps"], man["reset_fade"], man["throttle_at"]
    ppm = man["px_per_m"]
    cycles = D / P
    assert abs(cycles - round(cycles)) < 1e-9, "the cycle must divide the scene length"
    for key in ("cycle_s", "throttle_at", "first_cycle_at", "reset_fade"):
        assert abs(man[key] * fps - round(man[key] * fps)) < 1e-9, f"{key} must be a whole number of frames"
    assert ta + T + 2.0 <= P - F, "the run and the hold must end before the reset fade"
    print(f"setup: the same hill in both panels, side view: a {m_kg:,.0f} kg front-wheel-drive car, wheelbase L = {L:g} m, "
          f"{man['front_static_share'] * 100:g} / {(1 - man['front_static_share']) * 100:g} front-to-rear static split so the "
          f"centre of mass is b = {b:.2f} m ahead of the rear axle and h = {h:g} m up, grip mu = {mu:g} on ice, a theta = "
          f"{theta_deg:g} degree hill (all chosen); g = {g:g} m/s^2; the car starts from rest with the brakes on and the "
          f"driver floors it at the throttle: the driven front wheels spin and push uphill with mu N_front, the rear wheels "
          f"roll free and push nothing; top panel nose first (the front axle uphill), bottom panel in reverse (the same car "
          f"turned round, the front axle downhill, backing up); loads N_front = m g cos theta (b / L) -/+ m (g sin theta + a) "
          f"(h / L) (minus nose first, plus in reverse), N_rear = m g cos theta - N_front, a = mu N_front / m - g sin theta; "
          f"both runs integrated by RK4 at {man['steps_per_second']} steps per second (dt = {dt:.0e} s) for {T:g} s with the "
          f"loads solved from the state at every stage, checked against the closed form x = (b / L) cos theta / (1 +/- mu h / "
          f"L), s = a t^2 / 2 and a half-step rerun; real time on a {P:g} s cycle ({P * fps:.0f} frames) with the throttle "
          f"{ta:g} s into the cycle, the picture and the readouts held from {ta + T:g} s, {cycles:.0f} cycles in {D:g} s; "
          f"drawn at {ppm:g} px per metre; deterministic, no seed")
    runs, half = {}, {}
    names = {"nose": "nose first", "rev": "in reverse"}
    for m in PANELS:
        fc = FACING[m]
        run = rk4_run(b, L, h, mu, g, theta, fc, T, dt)
        hf = rk4_run(b, L, h, mu, g, theta, fc, T, 0.5 * dt)
        runs[m], half[m] = run, hf
        x_c = front_share(b, L, h, mu, theta, fc)
        a_c = accel(mu, x_c, g, theta)
        s_c = 0.5 * a_c * T * T
        err_s = float(np.max(np.abs(run["s"] - 0.5 * a_c * run["t"] ** 2)))
        x_live = front_share_at(b, L, h, g, theta, run["a"], fc)
        print(f"{names[m]} ({'the front axle uphill' if fc > 0 else 'the front axle downhill'}): at rest with the brakes on "
              f"(a = 0) the front axle carries {run['x0']:.4f} of the weight m g and the rear {run['xr0']:.4f} (sum "
              f"{run['x0'] + run['xr0']:.4f} = cos theta {math.cos(theta):.4f}); wheels spinning, the load equation and a = "
              f"mu N_front / m - g sin theta solve to x = N_front / (m g) = (b / L) cos theta / (1 {'+' if fc > 0 else '-'} mu "
              f"h / L) = {x_c:.4f} = {x_c:.3f} ({x_c * 100:.1f} percent, {x_c * m_kg * g:.0f} N), the rear axle "
              f"{run['xr']:.4f} ({run['xr'] * 100:.1f} percent, {run['xr'] * m_kg * g:.0f} N), both positive, sum "
              f"{run['x'] + run['xr']:.4f} = cos theta; the load equation evaluated at the solved a gives back "
              f"{x_live:.6f} (diff {x_live - x_c:+.1e}); the ice gives mu N_front = {mu * x_c * g:.4f} m/s^2 of push against "
              f"g sin theta = {g * math.sin(theta):.4f} m/s^2 of slope, so a = {a_c:+.4f} m/s^2 = {a_c:+.4f} ({'climbs' if a_c > 0 else 'rolls back, the wheels spinning forward'}); "
              f"RK4 from rest: after {T:g} s the car has moved {run['s_end']:+.4f} m = {run['s_end']:+.2f} m at "
              f"{run['v_end']:+.4f} m/s (closed form a t^2 / 2 = {s_c:+.4f} m, diff {run['s_end'] - s_c:+.1e} m; the table "
              f"stays within {err_s:.1e} m of the closed form), {run['steps']} steps; half-step rerun (dt = {0.5 * dt:.0e} s): "
              f"{hf['s_end']:+.7f} m ({hf['s_end'] - run['s_end']:+.1e} m); the rear wheels roll free: no traction from them")
        assert abs(run["s_end"] - s_c) < 1e-9 and err_s < 1e-9 and abs(hf["s_end"] - run["s_end"]) < 1e-9
        assert run["x"] > 0.0 and run["xr"] > 0.0 and abs(run["x"] + run["xr"] - math.cos(theta)) < 1e-12
        assert abs(x_live - x_c) < 1e-12
    lim = {m: steepest(b, L, h, mu, FACING[m]) for m in PANELS}
    window = lim["rev"] - lim["nose"]
    print(f"steepest hill (a = 0): tan theta* = mu b / (L + mu h) nose first = {lim['nose']:.4f} deg = {lim['nose']:.2f} deg, "
          f"mu b / (L - mu h) in reverse = {lim['rev']:.4f} deg = {lim['rev']:.2f} deg; the window between them is "
          f"{window:.4f} deg = {window:.2f} deg wide and the {theta_deg:g} degree hill sits inside it "
          f"({lim['nose']:.2f} < {theta_deg:g} < {lim['rev']:.2f}): the answer depends on the chosen grip, split and height")
    assert lim["nose"] < theta_deg < lim["rev"]
    ev: dict = {"theta": theta, "b": b, "runs": runs, "lim": lim, "window": window}
    # Variants for the description.
    descr = []
    var: dict = {}
    for mu2 in man["description_grips"] + [mu]:
        row = {}
        for m in PANELS:
            x2 = front_share(b, L, h, mu2, theta, FACING[m])
            a2 = accel(mu2, x2, g, theta)
            row[m] = {"x": x2, "a": a2, "s": 0.5 * a2 * T * T, "lim": steepest(b, L, h, mu2, FACING[m])}
        var[mu2] = row
        descr.append(f"grip {mu2:g}: nose first front load {row['nose']['x']:.4f}, a {row['nose']['a']:+.4f} m/s^2, "
                     f"{row['nose']['s']:+.2f} m in {T:g} s, steepest {row['nose']['lim']:.2f} deg; in reverse front load "
                     f"{row['rev']['x']:.4f}, a {row['rev']['a']:+.4f} m/s^2, {row['rev']['s']:+.2f} m in {T:g} s, steepest "
                     f"{row['rev']['lim']:.2f} deg; window {row['rev']['lim'] - row['nose']['lim']:.2f} deg")
    # Rear-wheel drive nose first (the driven rear axle downhill, loaded: the same equation with L - b).
    xr_rwd = ((1.0 - b / L) * math.cos(theta) + math.sin(theta) * h / L) / (1.0 - mu * h / L)
    a_rwd = accel(mu, xr_rwd, g, theta)
    lim_rwd = math.degrees(math.atan(mu * (L - b) / (L - mu * h)))
    # All-wheel drive: every wheel pushes, a = mu g cos theta - g sin theta whatever the split.
    a_awd = mu * g * math.cos(theta) - g * math.sin(theta)
    lim_awd = math.degrees(math.atan(mu))
    descr.append(f"rear-wheel drive nose first at grip {mu:g} (the driven rear axle downhill): rear load {xr_rwd:.4f}, a "
                 f"{a_rwd:+.4f} m/s^2, {0.5 * a_rwd * T * T:+.2f} m in {T:g} s, steepest atan(mu (L - b) / (L - mu h)) = "
                 f"{lim_rwd:.2f} deg (its lighter rear axle gives it less than the front drive even with the pitch helping)")
    descr.append(f"all-wheel drive at grip {mu:g}: a = mu g cos theta - g sin theta = {a_awd:+.4f} m/s^2, "
                 f"{0.5 * a_awd * T * T:+.2f} m in {T:g} s, steepest atan(mu) = {lim_awd:.2f} deg, whatever the split")
    print("for the description: " + "; ".join(descr))
    ev["var"], ev["rwd"] = var, {"x": xr_rwd, "a": a_rwd, "lim": lim_rwd}
    ev["awd"] = {"a": a_awd, "lim": lim_awd}
    # The brief's checks.
    rn, rv = runs["nose"], runs["rev"]
    checks: list[tuple[str, float, float, float]] = [
        ("nose first front load (W)", rn["x"], 0.556, 6e-4), ("nose first front load (4 places)", rn["x"], 0.5556, 6e-5),
        ("nose first a (m/s^2)", rn["a"], -0.0683, 6e-5), ("nose first moved at 5 s (m)", rn["s_end"], -0.85, 6e-3),
        ("in reverse front load (W)", rv["x"], 0.631, 6e-4), ("in reverse front load (4 places)", rv["x"], 0.6309, 6e-5),
        ("in reverse a (m/s^2)", rv["a"], 0.1533, 6e-5), ("in reverse moved at 5 s (m)", rv["s_end"], 1.92, 6e-3),
        ("steepest nose first (deg)", lim["nose"], 9.61, 6e-3), ("steepest in reverse (deg)", lim["rev"], 10.88, 6e-3),
        ("grip 0.2 steepest nose first", var[0.2]["nose"]["lim"], 6.57, 6e-3),
        ("grip 0.2 steepest in reverse", var[0.2]["rev"]["lim"], 7.14, 6e-3),
        ("grip 0.4 steepest nose first", var[0.4]["nose"]["lim"], 12.48, 6e-3),
        ("grip 0.4 steepest in reverse", var[0.4]["rev"]["lim"], 14.69, 6e-3),
        ("rear-wheel drive nose first steepest", lim_rwd, 7.30, 6e-3), ("all-wheel drive steepest", lim_awd, 16.70, 6e-3),
        ("window (deg)", window, 1.27, 6e-3),
        ("nose first loads sum to cos theta", rn["x"] + rn["xr"], math.cos(theta), 1e-12),
        ("in reverse loads sum to cos theta", rv["x"] + rv["xr"], math.cos(theta), 1e-12),
        ("nose first RK4 against the closed form (m)", rn["s_end"] - 0.5 * rn["a"] * T * T, 0.0, 1e-9),
        ("in reverse RK4 against the closed form (m)", rv["s_end"] - 0.5 * rv["a"] * T * T, 0.0, 1e-9),
    ]
    fails = 0
    out = []
    for name, got, want, tol in checks:
        ok = abs(got - want) <= tol
        fails += 0 if ok else 1
        out.append(f"{name}: brief {want:g}, sim {got:.6g}, diff {got - want:+.1e}: {'ok' if ok else 'FAIL'}")
    pos_ok = min(rn["x"], rn["xr"], rv["x"], rv["xr"]) > 0.0
    fails += 0 if pos_ok else 1
    out.append(f"both axle loads positive in both runs: least {min(rn['x'], rn['xr'], rv['x'], rv['xr']):.4f} W: "
               f"{'ok' if pos_ok else 'FAIL'}")
    in_ok = lim["nose"] < theta_deg < lim["rev"]
    fails += 0 if in_ok else 1
    out.append(f"the {theta_deg:g} degree hill inside the window: {'ok' if in_ok else 'FAIL'}")
    print(f"checks against the brief ({len(checks) + 2} checks, {fails} failed): " + "; ".join(out))
    assert fails == 0, "a check against the brief failed"
    ev["check_count"] = len(checks) + 2
    # Geometry on screen.
    x0, y0 = float(man["start_x_px"]), float(man["road_y_px"])
    climb_px, back_px = rv["s_end"] * ppm, -rn["s_end"] * ppm
    boxes_car = {}
    for m in PANELS:
        boxes_car[m] = union(bbox(car_points(man, m, 0.0, ev)), bbox(car_points(man, m, runs[m]["s_end"], ev)))
    road_left, road_right = y0 + x0 * math.tan(theta), y0 - (W - x0) * math.tan(theta)
    print(f"drawing: {ppm:g} px per metre, the slope a true {theta_deg:g} degrees rising to the right; the car "
          f"{man['car_length_m']:g} m = {man['car_length_m'] * ppm:.0f} px long with {man['wheel_radius_m'] * ppm:.0f} px "
          f"wheel radius and its centre of mass {b - L / 2:+.2f} m ahead of the mid-wheelbase, {h:g} m up; both cars start "
          f"with their mid-wheelbase at x {x0:.0f} on the start line, where the road surface is {y0:.0f} px under the band "
          f"top (the road at x 0 is at {road_left:.0f} px, at x {W} at {road_right:.0f} px); the {rv['s_end']:.2f} m climb "
          f"shows as {climb_px:.0f} px along the road ({climb_px * math.cos(theta):.0f} px across, {climb_px * math.sin(theta):.0f} "
          f"px up) and the {-rn['s_end']:.2f} m roll-back as {back_px:.0f} px; the nose first car spans x {boxes_car['nose'][0]:.0f} "
          f"to {boxes_car['nose'][2]:.0f} and y {boxes_car['nose'][1]:.0f} to {boxes_car['nose'][3]:.0f} over its run, the "
          f"in reverse car x {boxes_car['rev'][0]:.0f} to {boxes_car['rev'][2]:.0f} and y {boxes_car['rev'][1]:.0f} to "
          f"{boxes_car['rev'][3]:.0f} (band 0 to {BAND_H}, text rows end at {ROWS_BOTTOM}); the driven wheel's spoke is drawn "
          f"turning at {man['spoke_turns_per_s']:g} turns a second while the wheels spin (drawing only: the spin rate is not "
          f"modelled) and the free wheel's spoke rolls with the car at v / r")
    for m in PANELS:
        bx = boxes_car[m]
        assert bx[0] > 8 and bx[2] < W - 8, f"the {m} car leaves the frame sideways"
        assert bx[1] > ROWS_BOTTOM + 10 and bx[3] < BAND_H - 8, f"the {m} car leaves the band or meets the rows"
    assert road_left < BAND_H - 24 and road_right > ROWS_BOTTOM + 40, "the road leaves the band"
    # The schedule in video time.
    t0 = man["first_cycle_at"]
    k0 = math.ceil((0.0 - t0) / P - 1e-9) - 1
    k1 = math.floor((D - t0) / P - 1e-9)
    starts = [t0 + kk * P for kk in range(k0, k1 + 1)]

    def lst(off_: float) -> str:
        return ", ".join(f"{st + off_:.2f}" for st in starts if 0.0 <= st + off_ < D)

    tau0 = (0.0 - t0) % P
    print(f"schedule (video time, real time): cycles of {P:g} s start at " + ", ".join(f"{st:.2f}" for st in starts)
          + f" s; the throttle gauge rises over the first {ta:g} s of each cycle and the driver floors it {ta:g} s in at "
          f"{lst(ta)} s; the cars move for {T:g} s; the event rows light and the readouts and the picture hold {T:g} s after "
          f"the throttle at {lst(ta + T)} s; the reset crossfade runs over the last {F:g} s of each cycle (from {lst(P - F)} s; "
          f"the readouts out over its first half and in over its second); on the first frame the cycle is {tau0:.2f} s in "
          f"(both cars at rest on the start line, the gauge at zero and rising); title until {man['title_until']:g} s; payoff "
          f"card from {man['payoff_t']:g} s; the title fades back in over the last {man['loop_fade']:g} s and the last frame "
          f"repeats the first (the scene is periodic: {D:g} s holds exactly {cycles:.0f} cycles)")
    # Text widths.
    font = os.environ["SEED_ZERO_FONT"]
    f24, f28, f32, f34, f40, f56 = (ImageFont.truetype(font, n) for n in (24, 28, 32, 34, 40, 56))
    widths = {"overlay@34": (f34, man["overlay"])}
    for j, line in enumerate(man["title"].split("|")):
        widths[f"title line {j + 1}@56"] = (f56, line)
    widths["legend@40"] = (f40, legend_text())
    widths["clock@28"] = (f28, clock_text(1.2515, T))
    widths["clock rest@28"] = (f28, clock_text(-1.0, T))
    for m in PANELS:
        widths[f"label {m}@40"] = (f40, label_text(m))
        widths[f"sublabel {m}@28"] = (f28, sub_text(man))
        widths[f"event {m}@{EVENT_SIZE}"] = (f32, event_text(ev, m, T))
        widths[f"moved {m}@40"] = (f40, moved_text(runs[m]["s_end"]))
        widths[f"load {m}@28"] = (f28, load_text(runs[m]["x"]))
        widths[f"driven label {m}@24"] = (f24, wheel_text(True, runs[m]["x"]))
        widths[f"rear label {m}@24"] = (f24, wheel_text(False, runs[m]["xr"]))
    widths["speed@28"] = (f28, speed_text(-0.3415))
    widths["gauge label@24"] = (f24, gauge_text())
    for j, line in enumerate(payoff_lines(man, ev)):
        widths[f"payoff line {j + 1}@40"] = (f40, line)
    print("text widths (the on-screen strings verbatim): " + ", ".join(f"{kk} {f.getlength(s):.0f} px '{s}'"
                                                                      for kk, (f, s) in widths.items()))
    assert all(f.getlength(s) < 950 for f, s in widths.values()), "a text line is wider than 950 px"
    assert len(payoff_lines(man, ev)) <= 6, "the card has more than six lines"
    assert len(man["title"].split("|")) in TITLE_YS
    # Layout checks (band-local boxes).
    left = ROW_X0 + max(max(f40.getlength(label_text(m)) for m in PANELS), f28.getlength(sub_text(man)),
                        f28.getlength(speed_text(-0.3415)))
    right = ROW_X1 - max(max(f40.getlength(moved_text(runs[m]["s_end"])) for m in PANELS),
                         max(f28.getlength(load_text(runs[m]["x"])) for m in PANELS), BAR_W)
    ev_w = max(f32.getlength(event_text(ev, m, T)) for m in PANELS)
    gl_w = f24.getlength(gauge_text())
    gcx = GAUGE_X0 + GAUGE_W / 2.0
    boxes = {"left column": (ROW_X0 - 8, LABEL_DY - 28, left + 8, ROWS_BOTTOM),
             "right column": (right - 8, LABEL_DY - 28, ROW_X1 + 8, ROWS_BOTTOM),
             "gauge": (min(GAUGE_X0, gcx - gl_w / 2.0) - 6, GAUGE_Y0 - 6, max(GAUGE_X0 + GAUGE_W, gcx + gl_w / 2.0) + 6,
                       GAUGE_LABEL_DY + 14),
             "event row": (ROW_X1 - ev_w - 8, EVENT_DY - 20, ROW_X1 + 8, EVENT_DY + 20)}
    # The wheel labels at the extremes of each run, under the road at each wheel.
    labels = {}
    hb = L / 2.0
    for m in PANELS:
        for s_m, when in ((0.0, "start"), (runs[m]["s_end"], "end")):
            px = x0 + s_m * ppm * math.cos(theta)
            py = y0 - s_m * ppm * math.sin(theta)
            for u, driven in ((hb, True), (-hb, False)):
                cx = px + u * FACING[m] * math.cos(theta) * ppm
                cy = py - u * FACING[m] * math.sin(theta) * ppm
                wtxt = wheel_text(driven, runs[m]["x"] if driven else runs[m]["xr"])
                lw = f24.getlength(wtxt)
                labels[f"{m} {'driven' if driven else 'rear'} label at the {when}"] = (
                    cx - lw / 2.0, cy + WHEEL_LABEL_DY - 13, cx + lw / 2.0, cy + WHEEL_LABEL_DY + 13)
    print(f"row check: the left column spans x {ROW_X0} to {left:.0f} px and the right column x {right:.0f} to {ROW_X1} px, "
          f"both y {LABEL_DY - 20} to {ROWS_BOTTOM} under the band top (the load bar x {ROW_X1 - BAR_W} to {ROW_X1} at y "
          f"{BAR_Y0} to {BAR_Y1}); the throttle gauge x {GAUGE_X0} to {GAUGE_X0 + GAUGE_W}, y {GAUGE_Y0} to {GAUGE_Y1} with its "
          f"label at y {GAUGE_LABEL_DY} ({gl_w:.0f} px wide); the event row x {ROW_X1 - ev_w:.0f} to {ROW_X1} (widest {ev_w:.0f} "
          f"px at {EVENT_SIZE} px) at y {EVENT_DY - 16} to {EVENT_DY + 16}, over the slab (the road surface at x "
          f"{ROW_X1 - ev_w:.0f} is at y {y0 + (x0 - (ROW_X1 - ev_w)) * math.tan(theta):.0f}); the wheel labels {WHEEL_LABEL_DY} "
          f"px under the road at each wheel: " + "; ".join(f"{kk} x {bx[0]:.0f} to {bx[2]:.0f}, y {bx[1]:.0f} to {bx[3]:.0f}"
                                                           for kk, bx in labels.items())
          + f"; each band is {BAND_H} px tall (y {BAND_Y['nose']} to {BAND_Y['nose'] + BAND_H} and {BAND_Y['rev']} to "
          f"{BAND_Y['rev'] + BAND_H}); the caption band starts at y {int(man['caption_y'] * H)}; the title rows end at y "
          f"{TITLE_YS[len(man['title'].split('|'))][-1] + 28}, the band text starts at y {BAND_Y['nose'] + LABEL_DY - 20}; "
          f"the overlay band ends at y 130")
    assert right - left > 40, "the columns meet"
    for a_name, a_box in boxes.items():
        for b_name, b_box in boxes.items():
            if a_name < b_name:
                sep = a_box[2] <= b_box[0] or b_box[2] <= a_box[0] or a_box[3] <= b_box[1] or b_box[3] <= a_box[1]
                assert sep, f"{a_name} meets {b_name}"
    # The cars against the fixed boxes: the body outline and the wheel squares at 61 positions along each run.
    n_pos = 61
    for m in PANELS:
        for s_m in np.linspace(0.0, runs[m]["s_end"], n_pos):
            for shape in car_shapes(man, m, float(s_m), ev):
                for name, bx in boxes.items():
                    assert not poly_meets_box(shape, bx), f"the {m} car meets the {name} at s = {s_m:+.3f} m"
    gauge_box = boxes["gauge"]
    low_pts = [y for m in PANELS for s_m in np.linspace(0.0, runs[m]["s_end"], n_pos)
               for shape in car_shapes(man, m, float(s_m), ev) for x, y in shape if x <= gauge_box[2] + 30]
    print(f"car check: the body outline and both wheel squares of each car, at {n_pos} positions along its run, are clear "
          f"of the left column, the right column, the throttle gauge and the event row (polygon against box); the car "
          f"points within 30 px right of the gauge are never higher than y {min(low_pts):.0f} (the gauge label ends at y "
          f"{gauge_box[3]:.0f})")
    ev_box = boxes["event row"]
    for kk, bx in labels.items():
        sep = bx[2] <= ev_box[0] or ev_box[2] <= bx[0] or bx[3] <= ev_box[1] or ev_box[3] <= bx[1]
        assert sep, f"{kk} meets the event row"
        assert bx[3] < BAND_H - 4 and bx[0] > 4, f"{kk} leaves the band"
        assert bx[1] > ROWS_BOTTOM, f"{kk} meets the text rows"
    assert EVENT_DY + 20 < BAND_H - 8, "the event row leaves the band"
    assert BAND_Y["rev"] + BAND_H <= int(man["caption_y"] * H), "the bottom band reaches the caption band"
    assert PAYOFF_Y - 20 > int(man["caption_y"] * H) + 90, "the card meets the caption band"
    return ev


def legend_text() -> str:
    return "same car, same hill, real time"


def clock_text(r: float, T: float) -> str:
    return "before the throttle" if r < 0.0 else f"{min(r, T):.2f} s after the throttle"


def label_text(m: str) -> str:
    return "nose first" if m == "nose" else "in reverse"


def sub_text(man: dict) -> str:
    return f"front-wheel drive, {man['slope_deg']:g} degree ice"


def speed_text(v: float) -> str:
    return f"speed {v:+.2f} m/s"


def moved_text(s: float) -> str:
    return "moved 0.00 m" if abs(s) < 0.005 else f"moved {s:+.2f} m"


def load_text(x: float) -> str:
    return f"front wheels carry {x * 100:.0f} %"


def wheel_text(driven: bool, x: float) -> str:
    return f"DRIVEN {x * 100:.0f} %" if driven else f"rear {x * 100:.0f} %"


def gauge_text() -> str:
    return "throttle"


def event_text(ev: dict, m: str, T: float) -> str:
    s = ev["runs"][m]["s_end"]
    if m == "nose":
        return f"nose first: rolled back {-s:.2f} m in {T:g} s"
    return f"in reverse: climbed {s:.2f} m in {T:g} s"


def payoff_lines(man: dict, ev: dict) -> list[str]:
    r = ev["runs"]
    text = man["payoff_text"].format(back=-r["nose"]["s_end"], climb=r["rev"]["s_end"], run=man["run_s"],
                                     xf_nose=r["nose"]["x"] * 100, xf_rev=r["rev"]["x"] * 100,
                                     lim_nose=ev["lim"]["nose"], lim_rev=ev["lim"]["rev"])
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
        self.font_event = ImageFont.truetype(font, EVENT_SIZE)
        self.font_layer = ImageFont.truetype(font, 24 * SS)
        self.ppm = float(man["px_per_m"])
        self.P = man["cycle_s"]
        self.P_f = int(round(man["cycle_s"] * self.fps))
        self.c0_f = int(round(man["first_cycle_at"] * self.fps))
        self.ta, self.F, self.T = man["throttle_at"], man["reset_fade"], man["run_s"]
        self.runs = ev["runs"]
        self.th = ev["theta"]
        self.ct, self.st_ = math.cos(self.th), math.sin(self.th)
        self.x0, self.y0 = float(man["start_x_px"]), float(man["road_y_px"])
        self.L, self.h, self.b = man["wheelbase_m"], man["cg_height_m"], ev["b"]
        self.rw = man["wheel_radius_m"]
        self.k = man["car_length_m"] / 4.0

    def phase(self, f: int) -> tuple[int, float]:
        k, tau_f = divmod(f - self.c0_f, self.P_f)
        return k, tau_f / self.fps

    @staticmethod
    def L_(x: float, y: float) -> tuple[float, float]:
        """Layer (2x) pixel of a band-local point, rounded to 1e-4 px so equal states draw equal pixels."""
        return round(x * SS, 4), round(y * SS, 4)

    def road_y(self, x: float) -> float:
        return self.y0 - (x - self.x0) * math.tan(self.th)

    def pivot(self, s_m: float) -> tuple[float, float]:
        """Band-local px of the car's mid-wheelbase road point at displacement s_m (uphill positive)."""
        return self.x0 + s_m * self.ppm * self.ct, self.y0 - s_m * self.ppm * self.st_

    def car_pt(self, m: str, px: float, py: float, u: float, w: float) -> tuple[float, float]:
        """Band-local px of the car-frame point (u forward, w up, metres) with the mid-wheelbase at (px, py)."""
        fc = FACING[m]
        return px + (u * fc * self.ct - w * self.st_) * self.ppm, py + (-u * fc * self.st_ - w * self.ct) * self.ppm

    def draw_road(self, d: ImageDraw.ImageDraw) -> None:
        xa, xb = -12.0, W + 12.0
        ya, yb = self.road_y(xa), self.road_y(xb)
        d.polygon([self.L_(xa, ya), self.L_(xb, yb), self.L_(xb, BAND_H + 12), self.L_(xa, BAND_H + 12)], fill=SLAB)
        d.line((*self.L_(xa, ya), *self.L_(xb, yb)), fill=ICE_DIM, width=7 * SS)
        d.line((*self.L_(xa, ya), *self.L_(xb, yb)), fill=ICE, width=3 * SS)
        # The start line painted across the road at the mid-wheelbase start point, normal to the surface.
        nx, ny = -self.st_, -self.ct
        p0 = self.L_(self.x0 - nx * 14.0, self.y0 - ny * 14.0)
        p1 = self.L_(self.x0 + nx * 10.0, self.y0 + ny * 10.0)
        d.line((*p0, *p1), fill=WHITE, width=3 * SS)

    def draw_trail(self, d: ImageDraw.ImageDraw, m: str, s_m: float) -> None:
        if abs(s_m) < 1e-6:
            return
        u_cm = self.b - self.L / 2.0
        p0 = self.car_pt(m, *self.pivot(0.0), u_cm, self.h)
        p1 = self.car_pt(m, *self.pivot(s_m), u_cm, self.h)
        d.line((*self.L_(*p0), *self.L_(*p1)), fill=blend(WHITE, 0.75, COLOUR[m]), width=2 * SS)
        X, Y = self.L_(*p0)
        d.ellipse((X - 3 * SS, Y - 3 * SS, X + 3 * SS, Y + 3 * SS), fill=blend(WHITE, 0.75, COLOUR[m]))

    def draw_car(self, d: ImageDraw.ImageDraw, m: str, st: dict, tau: float) -> None:
        px, py = self.pivot(st["s"])
        col = COLOUR[m]
        kk = self.k

        def pt(u: float, w: float) -> tuple[float, float]:
            return self.L_(*self.car_pt(m, px, py, u, w))

        body = [pt(u * kk, w) for u, w in BODY]
        d.polygon(body, fill=col, outline=blend(col, 0.55, (0, 0, 0)), width=2 * SS)
        for glass in (GLASS_FRONT, GLASS_REAR):
            d.polygon([pt(u * kk, w) for u, w in glass], fill=GLASS)
        d.polygon([pt(2.0 * kk, 0.50), pt(2.0 * kk, 0.64), pt(1.84 * kk, 0.64), pt(1.84 * kk, 0.50)], fill=LAMP)
        d.polygon([pt(-2.0 * kk, 0.50), pt(-2.0 * kk, 0.66), pt(-1.86 * kk, 0.66), pt(-1.86 * kk, 0.50)], fill=TAIL)
        # The centre of mass: a small ring b ahead of the rear axle, h up.
        cx, cy = pt(self.b - self.L / 2.0, self.h)
        rr = 5.0 * SS
        d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), outline=WHITE, width=2 * SS)
        d.ellipse((cx - rr * 0.35, cy - rr * 0.35, cx + rr * 0.35, cy + rr * 0.35), fill=WHITE)
        # Wheels: the driven front wheel with a teal rim and a fast spoke while the wheels spin, the free rear
        # wheel rolling with the car (its spoke turns v / r).
        hb = self.L / 2.0
        spinning = st["phase"] == RUN
        for u, driven in ((hb, True), (-hb, False)):
            wx, wy = pt(u, self.rw)
            rl = self.rw * self.ppm * SS
            d.ellipse((wx - rl, wy - rl, wx + rl, wy + rl), fill=WHEEL, outline=TEAL if driven else RIM,
                      width=(4 if driven else 2) * SS)
            if driven:
                ang = 2.0 * math.pi * self.man["spoke_turns_per_s"] * max(0.0, min(tau - self.ta, self.T))
            else:
                ang = -FACING[m] * st["s"] / self.rw
            # Screen angle: the wheel turns forward (the car's own forward) when ang grows, as seen from the side.
            for j in range(2):
                a2 = ang + j * math.pi / 2.0
                ex, ey = math.cos(a2) * rl * 0.78, math.sin(a2) * rl * 0.78
                d.line((wx - ex, wy - ey, wx + ex, wy + ey), fill=RIM, width=3 * SS)
            rh = 0.22 * rl
            d.ellipse((wx - rh, wy - rh, wx + rh, wy + rh), fill=TEAL if driven else RIM)
            # The wheel label under the road.
            wbx, wby = self.car_pt(m, px, py, u, 0.0)
            txt = wheel_text(driven, st["x"] if driven else st["xr"])
            d.text(self.L_(wbx, wby + WHEEL_LABEL_DY), txt, font=self.font_layer, fill=TEAL if driven else MUTED, anchor="mm")
            if driven and spinning:
                self.draw_spray(d, m, wbx, wby, tau)

    def draw_spray(self, d: ImageDraw.ImageDraw, m: str, cx: float, cy: float, tau: float) -> None:
        """Ice marks flung downhill from the spinning wheel's contact: SPRAY_N marks on a fixed cycle (drawing only)."""
        tv = tau - self.ta
        for j in range(SPRAY_N):
            u = (tv * 2.2 + j / SPRAY_N) % 1.0
            dist = 14.0 + 110.0 * u
            lift = 34.0 * math.sin(math.pi * u) * (1.0 - 0.3 * u)
            # Downhill is to the left along the road.
            x = cx - dist * self.ct - lift * self.st_
            y = cy + dist * self.st_ - lift * self.ct
            a = 1.0 - u
            r = (4.0 - 2.0 * u) * SS
            X, Y = self.L_(x, y)
            d.ellipse((X - r, Y - r, X + r, Y + r), fill=blend(ICE, 0.9 * a, SLAB if y > self.road_y(x) else BG))

    def draw_gauge(self, d: ImageDraw.ImageDraw, tau: float, st: dict) -> None:
        """The throttle gauge: rises over the throttle_at seconds before the throttle, full during the run, zero at
        the hold and before the cycle starts."""
        if tau < 0.0:
            level = 0.0
        elif tau < self.ta:
            level = tau / self.ta
        elif st["phase"] == RUN:
            level = 1.0
        else:
            level = 0.0
        g0, g1 = self.L_(GAUGE_X0, GAUGE_Y0), self.L_(GAUGE_X0 + GAUGE_W, GAUGE_Y1)
        d.rounded_rectangle((g0[0], g0[1], g1[0], g1[1]), radius=5 * SS, fill=BAR_BG, outline=MUTED, width=SS)
        if level > 0.0:
            top = GAUGE_Y1 - (GAUGE_Y1 - GAUGE_Y0) * level
            f0, f1 = self.L_(GAUGE_X0 + 3, top + 2), self.L_(GAUGE_X0 + GAUGE_W - 3, GAUGE_Y1 - 3)
            if f1[1] > f0[1]:
                d.rounded_rectangle((f0[0], f0[1], f1[0], f1[1]), radius=3 * SS, fill=GOLD)
        d.text(self.L_(GAUGE_X0 + GAUGE_W / 2.0, GAUGE_LABEL_DY), gauge_text(), font=self.font_layer, fill=MUTED, anchor="mm")

    def scene(self, m: str, tau: float) -> tuple[Image.Image, dict]:
        """The band layer of panel m at tau seconds into a cycle (at rest on the start line before the throttle)."""
        layer = Image.new("RGB", (W * SS, BAND_H * SS), BG)
        d = ImageDraw.Draw(layer)
        self.draw_road(d)
        tv = tau - self.ta
        st = state_at(self.runs[m], tv)
        st["tv"], st["rt"] = tv, tv
        self.draw_car(d, m, st, tau)
        self.draw_trail(d, m, st["s"])      # on top: the car moves less than its own length
        self.draw_gauge(d, tau, st)
        return layer, st

    def draw_panel(self, m: str, f: int) -> tuple[Image.Image, dict]:
        k, tau = self.phase(f)
        P, F = self.P, self.F
        layer, st = self.scene(m, tau)
        st["alpha"], st["k"] = 1.0, k
        if tau >= P - F:
            a = (tau - (P - F)) / F
            new, st_new = self.scene(m, tau - P)
            layer = Image.blend(layer, new, a)
            st["alpha"] = max(0.0, 1.0 - 2.0 * a)
            st_new["alpha"], st_new["k"] = max(0.0, 2.0 * a - 1.0), k + 1
            if a >= 0.5:
                st = st_new
        return layer, st

    def draw_bar(self, d: ImageDraw.ImageDraw, y0: int, st: dict, a: float) -> None:
        """The load bar: the front share (teal, from the left) and the rear share (grey) of the weight; the empty
        tail is the share the slope takes (1 - cos theta)."""
        bx0, bx1 = ROW_X1 - BAR_W, ROW_X1
        d.rounded_rectangle((bx0, y0 + BAR_Y0, bx1, y0 + BAR_Y1), radius=4, fill=blend(BAR_BG, a),
                            outline=blend(MUTED, 0.7 * a), width=1)
        xf = bx0 + BAR_W * st["x"]
        xr = xf + BAR_W * st["xr"]
        d.rectangle((bx0 + 1, y0 + BAR_Y0 + 1, xf, y0 + BAR_Y1 - 1), fill=blend(TEAL, a))
        d.rectangle((xf + 1, y0 + BAR_Y0 + 1, xr, y0 + BAR_Y1 - 1), fill=blend(REAR_BAR, a))

    def draw_text(self, d: ImageDraw.ImageDraw, states: dict, hud_alpha: float) -> None:
        man, ev = self.man, self.ev
        for m, st in states.items():
            y0 = BAND_Y[m]
            a = st["alpha"]
            lit = st["phase"] == HOLD
            d.text((ROW_X0, y0 + LABEL_DY), label_text(m), font=self.font, fill=COLOUR[m], anchor="lm")
            d.text((ROW_X0, y0 + SUB_DY), sub_text(man), font=self.font_small, fill=MUTED, anchor="lm")
            d.text((ROW_X0, y0 + FIX_DY), speed_text(st["v"]), font=self.font_small, fill=blend(TEXT, a), anchor="lm")
            d.text((ROW_X1, y0 + LABEL_DY), moved_text(st["s"]), font=self.font, fill=blend(GOLD if lit else TEXT, a),
                   anchor="rm")
            d.text((ROW_X1, y0 + SUB_DY), load_text(st["x"]), font=self.font_small, fill=blend(TEXT, a), anchor="rm")
            self.draw_bar(d, y0, st, a)
            if lit:
                d.text((ROW_X1, y0 + EVENT_DY), event_text(ev, m, self.T), font=self.font_event, fill=blend(GOLD, a),
                       anchor="rm")
        if hud_alpha > 0.02:
            d.text((W / 2, LEGEND_Y), legend_text(), font=self.font, fill=blend(TEXT, hud_alpha), anchor="mm")
            d.text((W / 2, CLOCK_Y), clock_text(states["nose"]["rt"], self.T), font=self.font_small,
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
            for j, line in enumerate(rows):
                d.text((W / 2, TITLE_YS[len(rows)][j]), line, font=self.font_title, fill=blend(TEXT, title_alpha), anchor="mm")
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
    man = json.loads((ROOT / "projects/icyhill/manifest.json").read_text())
    ev = measure(man)
    if "--measure-only" in sys.argv:
        return
    if "--frames" in sys.argv:
        times = [float(v) for v in sys.argv[sys.argv.index("--frames") + 1].split(",")]
        r = Renderer(man, ev)
        (ROOT / "media/icyhill").mkdir(parents=True, exist_ok=True)
        for tv in times:
            Image.fromarray(r.frame_at(int(round(tv * man["fps"])))).save(ROOT / f"media/icyhill/smoke-{tv}.png")
        print("smoke frames: " + ", ".join(f"{tv}" for tv in times))
        return
    Renderer(man, ev).render(ROOT / "media/icyhill/footage.mp4")


if __name__ == "__main__":
    main()
