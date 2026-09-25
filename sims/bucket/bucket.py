#!/usr/bin/env python3
"""Bucket over your head: how slow before it spills?

A bucket of water hangs on an arm of length r, measured from the pivot
at your shoulder to the water surface; the bucket's open top faces the
pivot and the water fills it from r to r + depth. The arm turns in a
vertical circle at a steady rate omega (a motor, or a steady swing; the
rate never changes). The water is a grid of parcels fixed in the bucket
while the bucket pushes on them. In the frame turning with the arm a
parcel at radius rho feels omega^2 rho outward along the arm and g cos
phi inward at angle phi from the top, so the bucket floor pushes it
with N = m (omega^2 rho - g cos phi) (the same for every parcel across
the bucket's width). A parcel leaves the moment N would go negative,
on the way up at cos phi = omega^2 rho / g, with the bucket's velocity
omega x p, and then flies free under g (no air) until it hits the
floor or you at the pivot. The slowest rate that keeps the surface
water in is omega = sqrt(g / r). Two panels, the same arm and bucket:
the fast rate above (the water never leaves) and the slow rate below
(the water leaves every turn and the bucket is refilled at the bottom
of the swing). Both periods divide the scene length, so the scene is
exactly periodic and the last frame equals the first. Deterministic,
no seed.

Measured and printed: the threshold rate and period against sqrt(g /
r) and the whole-rpm sweep around it, the push at the top of each
panel, the leave angle and speed of every parcel (stepped at
steps_per_second against the closed forms), the flight (velocity
Verlet against the closed form), where and when the parcels land, the
pass height over your head and the clearance to your head and body,
other rates for the description, the schedule in video time, the loop
and periodicity checks and the on-screen text widths.

usage: bucket.py [--measure-only] [--frames t1,t2,...]
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
BUCKET_FILL = (30, 36, 46)

# Layout: overlay at y 96..130 (captions.py), title rows at y 190/252 for
# the first seconds, then the legend rows at y 236 and 290; two panels
# stacked, each with its pivot 244 px below its top edge and the floor
# 300 px below the pivot (1.5 m at 200 px per metre): the fast panel from
# y 320 (pivot at (600, 564), floor at 864) and the slow panel from y 874
# (pivot at (600, 1118), floor at 1418); the panel label at the top left
# and the live push readout at the top right of each panel, the fixed
# readouts at the bottom left; the geometry band y 320..1436 drawn at 2x;
# captions at caption_y 0.75 (y 1440..1520); the payoff card from y 1592.
LEGEND_Y, TAG_Y = 236, 290
GEOM_Y0, GEOM_Y1 = 320, 1436
SS = 2
PAYOFF_Y = 1592.0
PANEL_TOP_ABOVE_PIVOT = 244
LABEL_X, READ_X = 60, 1020
PANELS = ("fast", "slow")


def blend(col, a: float, base=BG) -> tuple:
    a = max(0.0, min(1.0, a))
    return tuple(int(round(c * a + b * (1 - a))) for c, b in zip(col, base))


# --- measurement --------------------------------------------------------------
def leave_by_stepping(omega: float, rho: float, g: float, dt: float) -> tuple[float, float] | None:
    """Step the arm from the bottom through one turn at dt and return (phi before the top in rad,
    time from the bottom) at the first step where N = omega^2 rho - g cos theta goes negative,
    interpolated inside the step; None when the bucket holds the parcel through the turn."""
    n = int(math.ceil(2.0 * math.pi / omega / dt))
    th = math.pi + omega * dt * np.arange(n + 1)
    N = omega * omega * rho - g * np.cos(th)
    neg = np.nonzero(N < 0.0)[0]
    if len(neg) == 0:
        return None
    i = int(neg[0])
    frac = N[i - 1] / (N[i - 1] - N[i])
    t = (i - 1 + frac) * dt
    return 2.0 * math.pi - (math.pi + omega * t), t


def fly(x0: float, y0: float, vx: float, vy: float, g: float, dt: float, floor_y: float, man: dict,
        omega: float, theta_leave: float) -> dict:
    """Free flight by velocity Verlet from the leave state until the floor or you (the head circle
    and the torso box), with the crossing interpolated inside the last step. Tracks the apex, the
    clearance to the head and body, and the closest the parcel comes to the bucket (centre at
    bucket_r on the arm, which keeps turning at omega from theta_leave)."""
    hx, hy = man["head_center_m"]
    hr, tw, sy = man["head_radius_m"], man["torso_half_width_m"], man["shoulder_y_m"]
    rb = 0.5 * (man["bucket_rim_r_m"] + man["bucket_floor_r_m"])
    x, y, t = x0, y0, 0.0
    min_head = math.hypot(x - hx, y - hy) - hr
    min_body = math.hypot(max(abs(x) - tw, 0.0), max(y - sy, 0.0))
    min_bucket, t_bucket, clear = float("inf"), 0.0, False
    apex = (x0 + vx * vy / g, y0 + vy * vy / (2.0 * g)) if vy > 0.0 else (x0, y0)
    while True:
        xn = x + vx * dt
        yn = y + vy * dt - 0.5 * g * dt * dt
        vyn = vy - g * dt
        tn = t + dt
        th = theta_leave + omega * tn
        db = math.hypot(xn - rb * math.sin(th), yn - rb * math.cos(th))
        # The closest approach to the bucket counts once the parcel has separated from it by 0.3 m.
        clear = clear or db > 0.3
        if clear and db < min_bucket:
            min_bucket, t_bucket = db, tn
        if yn <= floor_y:
            f = (floor_y - y) / (yn - y)
            return {"t": t + f * dt, "x": x + f * (xn - x), "y": floor_y, "hit": "floor", "apex": apex,
                    "min_head": min_head, "min_body": min_body, "min_bucket": min_bucket, "t_bucket": t_bucket}
        head = math.hypot(xn - hx, yn - hy) - hr
        body = math.hypot(max(abs(xn) - tw, 0.0), max(yn - sy, 0.0))
        if head <= 0.0 or (abs(xn) <= tw and yn <= sy):
            return {"t": tn, "x": xn, "y": yn, "hit": "head" if head <= 0.0 else "body", "apex": apex,
                    "min_head": min(min_head, head), "min_body": min(min_body, body), "min_bucket": min_bucket,
                    "t_bucket": t_bucket}
        x, y, vy, t = xn, yn, vyn, tn
        min_head, min_body = min(min_head, head), min(min_body, body)


def parcel_grid(man: dict) -> list[tuple[float, float]]:
    r0, depth = man["arm_m"], man["water_depth_m"]
    radii = np.linspace(r0, r0 + depth, man["parcel_rows"])
    spans = np.linspace(-man["parcel_half_span_m"], man["parcel_half_span_m"], man["parcel_columns"])
    return [(float(rho), float(s)) for rho in radii for s in spans]


def leave_state(omega: float, rho: float, s: float, phi: float) -> tuple[float, float, float, float]:
    """Position and velocity of the parcel at (rho, s) in the bucket when the arm is phi before the
    top: p = rho e_r + s e_t, v = omega (rho e_t - s e_r) with e_r = (-sin phi, cos phi), e_t =
    (cos phi, sin phi) (x to the right, y up, the arm turning clockwise on screen)."""
    er = (-math.sin(phi), math.cos(phi))
    et = (math.cos(phi), math.sin(phi))
    return (rho * er[0] + s * et[0], rho * er[1] + s * et[1],
            omega * (rho * et[0] - s * er[0]), omega * (rho * et[1] - s * er[1]))


def measure(man: dict) -> dict:
    g, r0, depth = man["g_m_s2"], man["arm_m"], man["water_depth_m"]
    D, fps, hp = man["scene_duration"], man["fps"], man["pivot_height_m"]
    dt = 1.0 / man["steps_per_second"]
    rpm = {"fast": man["fast_rpm"], "slow": man["slow_rpm"]}
    omega = {k: v * 2.0 * math.pi / 60.0 for k, v in rpm.items()}
    T = {k: 60.0 / v for k, v in rpm.items()}
    turns = {k: D / T[k] for k in rpm}
    for k in rpm:
        assert abs(turns[k] - round(turns[k])) < 1e-9, f"the {k} period must divide the scene length"
    grid = parcel_grid(man)
    print(f"setup: a bucket of water on an arm of {r0:g} m from the pivot at your shoulder to the water surface "
          f"(the open top faces the pivot; the water fills the bucket from {r0:g} to {r0 + depth:g} m, "
          f"{len(grid)} parcels on a {man['parcel_rows']} by {man['parcel_columns']} grid, radii {r0:g} to "
          f"{r0 + depth:g} m, {-man['parcel_half_span_m']:g} to {man['parcel_half_span_m']:g} m across the bucket); "
          f"the arm turns clockwise on screen at a steady rate, {rpm['fast']:g} rpm above (omega = "
          f"{omega['fast']:.4f} rad/s, {T['fast']:.4f} s per turn) and {rpm['slow']:g} rpm below (omega = "
          f"{omega['slow']:.4f} rad/s, {T['slow']:.4f} s per turn); the pivot is {hp:g} m above the floor, so the "
          f"bucket floor at {man['bucket_floor_r_m']:g} m clears the floor by {hp - man['bucket_floor_r_m']:.3f} m at "
          f"the bottom of the swing; you stand at the pivot, seen from the side (head radius {man['head_radius_m']:g} "
          f"m centred {man['head_center_m'][1]:g} m above the pivot, body {2 * man['torso_half_width_m']:g} m deep); "
          f"g = {g:g} m/s^2; a parcel at radius rho on the arm is pushed by the bucket floor with N = m (omega^2 "
          f"rho - g cos phi) at phi from the top and leaves when N would go negative, then flies free under g "
          f"(no air), stepped at {man['steps_per_second']} steps per second (dt = {dt:.0e} s) against the closed "
          f"forms; the slow bucket is refilled at the bottom of each turn; real time, {turns['fast']:.0f} fast "
          f"turns and {turns['slow']:.0f} slow turns in {D:g} s; drawn at {man['px_per_m']:g} px per metre; "
          f"deterministic, no seed")
    # The threshold for the surface water, closed form and the whole-rpm sweep by stepping.
    om_c = math.sqrt(g / r0)
    rpm_c = om_c * 60.0 / (2.0 * math.pi)
    period_c = 2.0 * math.pi / om_c
    rpm_hold, rpm_spill = None, None
    sweep = []
    for k in range(int(rpm_c) - 3, int(rpm_c) + 4):
        om = k * 2.0 * math.pi / 60.0
        lv = leave_by_stepping(om, r0, g, dt)
        top = om * om * r0 / g - 1.0
        sweep.append(f"{k} rpm: " + (f"holds ({top:+.3f} g at the top)" if lv is None
                                     else f"leaves {math.degrees(lv[0]):.1f} degrees before the top ({top:+.3f} g at the top)"))
        if lv is None and rpm_hold is None and k > rpm_c:
            rpm_hold, rpm_spill = k, k - 1
    om_hold = rpm_hold * 2.0 * math.pi / 60.0
    print(f"threshold: the surface water (r = {r0:g} m) stays in when omega^2 r >= g, omega = sqrt(g / r) = "
          f"{om_c:.4f} rad/s = {rpm_c:.2f} rpm, one turn every {period_c:.4f} s ({rpm_c:.1f} rpm, {period_c:.1f} s "
          f"to a tenth; {rpm_c:.0f} rpm to the nearest whole turn); the deeper water at r = {r0 + depth:g} m holds "
          f"down to {math.sqrt(g / (r0 + depth)) * 60 / (2 * math.pi):.2f} rpm, so the surface sets the limit; "
          f"whole-rpm sweep by stepping: " + "; ".join(sweep) + f"; the slowest whole rate that holds is {rpm_hold} "
          f"rpm ({60.0 / rpm_hold:.3f} s per turn, {om_hold * om_hold * r0 / g - 1.0:+.4f} g at the top) and "
          f"{rpm_spill} rpm spills")
    # The fast panel: every parcel through one turn.
    of = omega["fast"]
    fast_min = min(of * of * rho / g - 1.0 for rho, _ in grid)
    fast_leaves = [leave_by_stepping(of, rho, g, dt) for rho, _ in grid]
    assert all(lv is None for lv in fast_leaves), "the fast bucket must hold its water"
    push_top = of * of * r0 / g - 1.0
    print(f"fast panel ({rpm['fast']:g} rpm): omega^2 r = {of * of * r0:.3f} m/s^2 at the surface against g = "
          f"{g:g}; the push on the surface water is {push_top:.3f} g at the top ({push_top:.2f} g), "
          f"{of * of * r0 / g + 1.0:.3f} g at the bottom and {of * of * r0 / g:.3f} g at the sides; the smallest "
          f"push on any parcel through the turn is {fast_min:.3f} g (the surface, at the top), so no parcel leaves; "
          f"stepping every parcel through a full turn finds no leave")
    # The slow panel: every parcel's leave and flight.
    os_ = omega["slow"]
    parcels = []
    for rho, s in grid:
        lv = leave_by_stepping(os_, rho, g, dt)
        assert lv is not None, "the slow bucket must spill"
        phi_closed = math.acos(os_ * os_ * rho / g)
        x0, y0, vx, vy = leave_state(os_, rho, s, phi_closed)
        fl = fly(x0, y0, vx, vy, g, dt, -hp, man, os_, -phi_closed)
        # Closed form of the same flight to the floor (the free flight is a parabola).
        t_floor = (vy + math.sqrt(vy * vy + 2.0 * g * (y0 + hp))) / g
        if fl["hit"] == "floor":
            t_closed, x_closed = t_floor, x0 + vx * t_floor
        else:
            # The hit height is known: solve the parabola for the time to reach it.
            t_closed = (vy + math.sqrt(max(0.0, vy * vy + 2.0 * g * (y0 - fl["y"])))) / g
            x_closed = x0 + vx * t_closed
        parcels.append({"rho": rho, "s": s, "phi": phi_closed, "phi_step": lv[0], "x0": x0, "y0": y0, "vx": vx,
                        "vy": vy, "speed": math.hypot(vx, vy), "t_fl": fl["t"], "x_land": fl["x"], "y_land": fl["y"],
                        "hit": fl["hit"], "apex": fl["apex"], "min_head": fl["min_head"], "min_body": fl["min_body"],
                        "min_bucket": fl["min_bucket"], "t_bucket": fl["t_bucket"], "t_closed": t_closed,
                        "x_closed": x_closed})
    phi0 = parcels[0]["phi"]          # the surface parcels leave first
    for p in parcels:
        p["dtau"] = (phi0 - p["phi"]) / os_
    surf = next(p for p in parcels if abs(p["rho"] - r0) < 1e-12 and abs(p["s"]) < 1e-12)
    x_closed_s = surf["x_closed"]
    print(f"slow panel ({rpm['slow']:g} rpm): omega^2 r = {os_ * os_ * r0:.3f} m/s^2 at the surface, below g, so the "
          f"push on the surface water reaches zero on the way up at cos phi = {os_ * os_ * r0 / g:.4f}, phi = "
          f"{math.degrees(surf['phi']):.2f} degrees before the top (stepped {math.degrees(surf['phi_step']):.2f}, diff "
          f"{abs(math.degrees(surf['phi'] - surf['phi_step'])):.1e} degrees; {math.degrees(surf['phi']):.0f} degrees to "
          f"the nearest degree, {90.0 - math.degrees(surf['phi']):.1f} degrees above the horizontal); at the top the "
          f"bucket would have to pull with {1.0 - os_ * os_ * r0 / g:.3f} g; the surface parcel on the arm leaves at "
          f"({surf['x0']:.3f}, {surf['y0']:.3f}) m from the pivot at omega r = {surf['speed']:.3f} m/s (vx "
          f"{surf['vx']:.3f}, vy {surf['vy']:.3f}), rises to an apex {surf['apex'][1]:.3f} m above the pivot "
          f"({surf['apex'][1] - man['head_center_m'][1] - man['head_radius_m']:.3f} m above the top of your head) at "
          f"{surf['apex'][0]:.3f} m from the pivot line, and comes down on your {surf['hit']} at ({surf['x_land']:.3f}, "
          f"{surf['y_land']:.3f}) m, {hp + surf['y_land']:.2f} m above the floor, after {surf['t_fl']:.3f} s of flight "
          f"(closed form {x_closed_s:.3f} m after {surf['t_closed']:.3f} s, diffs "
          f"{abs(surf['x_land'] - x_closed_s):.1e} m and {abs(surf['t_fl'] - surf['t_closed']):.1e} s); closest "
          f"approach {surf['min_head']:.3f} m to your head; closest approach to the bucket, which keeps turning, "
          f"{surf['min_bucket']:.3f} m at {surf['t_bucket']:.2f} s once it has separated by 0.3 m (it never meets the bucket again)")
    phis = [math.degrees(p["phi"]) for p in parcels]
    hits = [p["hit"] for p in parcels]
    on_you = [p for p in parcels if p["hit"] != "floor"]
    print(f"all {len(parcels)} parcels: they leave between {max(phis):.1f} and {min(phis):.1f} degrees before the "
          f"top (the surface first, the floor water at r = {r0 + depth:g} m last, {max(p['dtau'] for p in parcels):.3f} "
          f"s later), at {min(p['speed'] for p in parcels):.3f} to {max(p['speed'] for p in parcels):.3f} m/s; "
          f"stepped leave angles within {max(abs(math.degrees(p['phi'] - p['phi_step'])) for p in parcels):.1e} "
          f"degrees of the closed form; apexes {min(p['apex'][1] for p in parcels):.3f} to "
          f"{max(p['apex'][1] for p in parcels):.3f} m above the pivot; flights {min(p['t_fl'] for p in parcels):.3f} "
          f"to {max(p['t_fl'] for p in parcels):.3f} s; {hits.count('body')} come down on your body, "
          f"{hits.count('head')} on your head, {hits.count('floor')} on the floor"
          + (f" (the body hits from {hp + max(p['y_land'] for p in on_you):.2f} to "
             f"{hp + min(p['y_land'] for p in on_you):.2f} m above the floor, x from "
             f"{min(p['x_land'] for p in on_you):.3f} to {max(p['x_land'] for p in on_you):.3f} m)" if on_you else "")
          + (f" (the floor landings at x = {min(p['x_land'] for p in parcels if p['hit'] == 'floor'):.3f} to "
             f"{max(p['x_land'] for p in parcels if p['hit'] == 'floor'):.3f} m from the pivot line)"
             if hits.count("floor") else "")
          + f"; closest approach {min(p['min_head'] for p in parcels):.3f} m to your head; closest approach to the "
          f"turning bucket {min(p['min_bucket'] for p in parcels):.3f} m; Verlet hits within "
          f"{max(abs(p['x_land'] - p['x_closed']) for p in parcels):.1e} m and "
          f"{max(abs(p['t_fl'] - p['t_closed']) for p in parcels):.1e} s of the closed form")
    refill_tau = (math.pi + phi0) / os_
    bottom_before = (math.pi - phi0) / os_
    descr = []
    for k in man["description_rpms"]:
        om = k * 2.0 * math.pi / 60.0
        lv = leave_by_stepping(om, r0, g, dt)
        if lv is None:
            descr.append(f"{k:g} rpm: holds, {om * om * r0 / g - 1.0:.3f} g at the top")
        else:
            x0, y0, vx, vy = leave_state(om, r0, 0.0, lv[0])
            fl = fly(x0, y0, vx, vy, g, dt, -hp, man, om, -lv[0])
            where = (f"the floor {fl['x']:.3f} m past the pivot line" if fl["hit"] == "floor"
                     else f"your {fl['hit']} {hp + fl['y']:.2f} m above the floor")
            descr.append(f"{k:g} rpm: leaves {math.degrees(lv[0]):.1f} degrees before the top at {om * r0:.3f} m/s, "
                         f"apex {fl['apex'][1]:.2f} m above the pivot, hits {where} after {fl['t']:.3f} s")
    print("for the description (the surface water on the same arm, other rates): " + "; ".join(descr))
    # Schedule in video time.
    tf0, ts0 = man["fast_top_at"], man["slow_leave_at"]
    ks = range(math.ceil((0.0 - ts0) / T["slow"] - 1e-9), math.floor((D - ts0) / T["slow"] - 1e-9) + 1)
    leaves = [ts0 + k * T["slow"] for k in ks]
    tau0 = (0.0 - ts0) % T["slow"]
    if tau0 >= refill_tau:
        first = f"the slow bucket is {tau0 - refill_tau:.2f} s past the refill at the bottom with its water in"
    elif tau0 < max(p["t_fl"] for p in parcels):
        first = f"the slow water is {tau0:.2f} s into its flight"
    else:
        first = (f"the slow bucket is empty, {tau0:.2f} s after the leave, with the splashes fading on you until "
                 f"the refill at {refill_tau - tau0:.2f} s")
    print(f"schedule (video time, real time): the fast bucket is at the top at {tf0:g} s and every {T['fast']:.4f} s "
          f"after; the slow bucket refills at the bottom {bottom_before:.3f} s before each leave, the surface water "
          f"leaves at {ts0:g} + {T['slow']:g} k s, i.e. at " + ", ".join(f"{t:.2f}" for t in leaves)
          + f" s, the floor water {max(p['dtau'] for p in parcels):.3f} s after, the water lands "
          f"{surf['t_fl']:.3f} to {max(p['t_fl'] for p in parcels):.3f} s after each leave and the puddle fades until "
          f"the refill {refill_tau:.3f} s after the leave; on the first frame {first} and the fast bucket is at the "
          f"top; title until {man['title_until']:g} s, then the legend and the "
          f"fixed readouts; payoff card from {man['payoff_t']:g} s; the title fades back in over the last "
          f"{man['loop_fade']:g} s and the last frame repeats the first (the scene is periodic: {D:g} s holds "
          f"exactly {turns['fast']:.0f} fast turns and {turns['slow']:.0f} slow turns)")
    if hits.count("floor") == 0:
        landing = "all of it comes down on you"
    elif hits.count("floor") == len(hits):
        landing = f"lands {surf['x_land']:.2f} m past you"
    else:
        landing = f"{len(hits) - hits.count('floor')} of {len(hits)} parcels land on you"
    ev = {"omega": omega, "T": T, "turns": {k: int(round(v)) for k, v in turns.items()}, "parcels": parcels,
          "phi0": phi0, "refill_tau": refill_tau, "rpm_c": rpm_c, "period_c": period_c, "rpm_hold": rpm_hold,
          "rpm_spill": rpm_spill, "push_top": push_top, "leave_deg": math.degrees(surf["phi"]),
          "x_land": surf["x_land"], "t_fl": surf["t_fl"], "landing": landing}
    # Text widths.
    font = os.environ["SEED_ZERO_FONT"]
    f28, f34, f40, f56 = (ImageFont.truetype(font, n) for n in (28, 34, 40, 56))
    widths = {"overlay@34": (f34, man["overlay"])}
    for j, line in enumerate(man["title"].split("|")):
        widths[f"title line {j + 1}@56"] = (f56, line)
    widths["legend@40"] = (f40, legend_text())
    widths["tag@28"] = (f28, tag_text())
    for name in PANELS:
        widths[f"label {name}@40"] = (f40, label_text(man, name))
        for j, line in enumerate(fixed_lines(man, ev, name)):
            widths[f"fixed {name} line {j + 1}@28"] = (f28, line)
    widths["push@40"] = (f40, push_text(omega["fast"] ** 2 * r0 / g + 1.0))
    widths["spills@40"] = (f40, "spills")
    widths["you tag@28"] = (f28, "you")
    for j, line in enumerate(payoff_lines(man, ev)):
        widths[f"payoff line {j + 1}@40"] = (f40, line)
    print("text widths: " + ", ".join(f"{k} {f.getlength(s):.0f} px" for k, (f, s) in widths.items()))
    assert all(f.getlength(s) < 950 for f, s in widths.values()), "a text line is wider than 950 px"
    return ev


def legend_text() -> str:
    return "same arm, same bucket, two speeds"


def tag_text() -> str:
    return "side view, refilled at the bottom of each turn"


def label_text(man: dict, name: str) -> str:
    return f"{man[name + '_rpm']:g} turns a minute"


def push_text(push_g: float) -> str:
    return f"push {push_g:.2f} g"


def fixed_lines(man: dict, ev: dict, name: str) -> list[str]:
    if name == "fast":
        return [f"push at top {ev['push_top']:.2f} g", "holds, every turn"]
    return [f"lets go {ev['leave_deg']:.0f} deg before the top", ev["landing"]]


def payoff_lines(man: dict, ev: dict) -> list[str]:
    text = man["payoff_text"].format(rpm_c=ev["rpm_c"], period_c=ev["period_c"], rpm_hold=ev["rpm_hold"],
                                     rpm_spill=ev["rpm_spill"], leave_deg=ev["leave_deg"], x_land=ev["x_land"])
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
        self.g, self.r0, self.depth, self.hp = man["g_m_s2"], man["arm_m"], man["water_depth_m"], man["pivot_height_m"]
        self.panels = {
            "fast": {"omega": ev["omega"]["fast"], "T": ev["T"]["fast"], "pivot": tuple(man["top_pivot"]),
                     "theta0": 0.0, "t0": man["fast_top_at"], "parcels": None},
            "slow": {"omega": ev["omega"]["slow"], "T": ev["T"]["slow"], "pivot": tuple(man["bottom_pivot"]),
                     "theta0": -ev["phi0"], "t0": man["slow_leave_at"], "parcels": ev["parcels"]},
        }

    # --- state helpers ------------------------------------------------------
    def theta(self, name: str, t: float) -> float:
        """Arm angle from the top (rad), increasing clockwise on screen."""
        P = self.panels[name]
        return P["theta0"] + P["omega"] * (t - P["t0"])

    def tau(self, t: float) -> float:
        """Slow-panel cycle time: 0 at the surface water's leave."""
        P = self.panels["slow"]
        return (t - P["t0"]) % P["T"]

    def parcel_state(self, p: dict, tau: float) -> tuple[str, float]:
        """('in', 0) attached, ('free', u) u seconds into the flight, ('down', a) landed with fade a."""
        if tau < p["dtau"] or tau >= self.ev["refill_tau"]:
            return "in", 0.0
        u = tau - p["dtau"]
        if u < p["t_fl"]:
            return "free", u
        land_end = self.ev["refill_tau"]
        return "down", max(0.0, 1.0 - (tau - (p["dtau"] + p["t_fl"])) / (land_end - (p["dtau"] + p["t_fl"])))

    def flight_pos(self, p: dict, u: float) -> tuple[float, float]:
        return p["x0"] + p["vx"] * u, p["y0"] + p["vy"] * u - 0.5 * self.g * u * u

    # --- pixel helpers ------------------------------------------------------
    def px(self, name: str, x: float, y: float) -> tuple[float, float]:
        cx, cy = self.panels[name]["pivot"]
        return cx + x * self.ppm, cy - y * self.ppm

    def L(self, name: str, x: float, y: float) -> tuple[float, float]:
        # Rounded to 1e-4 px so that a coordinate that is an exact integer at one time and off
        # by 1e-11 a whole number of turns later draws the same pixel (the periodicity check).
        X, Y = self.px(name, x, y)
        return round(X * SS, 4), round((Y - GEOM_Y0) * SS, 4)

    def arm_xy(self, theta: float, rho: float, s: float) -> tuple[float, float]:
        """World position of the point at radius rho on the arm and s across it (metres, y up)."""
        return rho * math.sin(theta) + s * math.cos(theta), rho * math.cos(theta) - s * math.sin(theta)

    def circle(self, d: ImageDraw.ImageDraw, X: float, Y: float, rr: float, **kw) -> None:
        d.ellipse((X - rr, Y - rr, X + rr, Y + rr), **kw)

    def arc(self, d: ImageDraw.ImageDraw, name: str, r: float, th0: float, th1: float, fill, width: int) -> None:
        """Arc at radius r from arm angle th0 to th1 (rad from the top, clockwise on screen)."""
        cx, cy = self.L(name, 0.0, 0.0)
        rr = r * self.ppm * SS
        d.arc((cx - rr, cy - rr, cx + rr, cy + rr), math.degrees(th0) - 90.0, math.degrees(th1) - 90.0,
              fill=fill, width=width)

    # --- the scene ----------------------------------------------------------
    def draw_panel(self, d: ImageDraw.ImageDraw, name: str, t: float, hud_alpha: float) -> dict:
        man, P = self.man, self.panels[name]
        r0, depth, g = self.r0, self.depth, self.g
        theta = self.theta(name, t)
        # The floor and the ring the bucket sweeps.
        fx0, fy = self.L(name, -man["floor_half_width_m"], -self.hp)
        fx1, _ = self.L(name, man["floor_half_width_m"], -self.hp)
        d.line((fx0, fy, fx1, fy), fill=RIM, width=3 * SS)
        nd = man["ring_dashes"]
        for j in range(nd):
            a0 = 2.0 * math.pi * j / nd
            self.arc(d, name, r0 + depth / 2.0, a0, a0 + math.pi / nd, blend(RIM, 0.6), 2 * SS)
        # You at the pivot, seen from the side: the body down to the floor, the neck, the head.
        tw, sy = man["torso_half_width_m"], man["shoulder_y_m"]
        hx, hy = man["head_center_m"]
        hr = man["head_radius_m"]
        bx0, by0 = self.L(name, -tw, sy)
        bx1, by1 = self.L(name, tw, -self.hp)
        d.rounded_rectangle((bx0, by0, bx1, by1), radius=tw * self.ppm * SS, fill=blend(WHITE, 0.30))
        nx0, ny0 = self.L(name, -0.04, hy)
        nx1, ny1 = self.L(name, 0.04, sy)
        d.rectangle((nx0, ny0, nx1, ny1), fill=blend(WHITE, 0.45))
        HX, HY = self.L(name, hx, hy)
        self.circle(d, HX, HY, hr * self.ppm * SS, fill=blend(WHITE, 0.85))
        # The slow panel's leave mark: a gold arc from the leave angle to the top with ticks.
        if P["parcels"] is not None and hud_alpha > 0.02:
            self.arc(d, name, 0.84, -self.ev["phi0"], 0.0, blend(GOLD, 0.8 * hud_alpha), 3 * SS)
            for a in (-self.ev["phi0"], 0.0):
                p0 = self.L(name, *self.arm_xy(a, 0.80, 0.0))
                p1 = self.L(name, *self.arm_xy(a, 0.88, 0.0))
                d.line((*p0, *p1), fill=blend(GOLD, 0.8 * hud_alpha), width=3 * SS)
        # The arm and the bucket (open top toward the pivot).
        rim_r, floor_r = man["bucket_rim_r_m"], man["bucket_floor_r_m"]
        rim_w, floor_w = man["bucket_rim_half_width_m"], man["bucket_floor_half_width_m"]
        a0 = self.L(name, 0.0, 0.0)
        a1 = self.L(name, *self.arm_xy(theta, rim_r, 0.0))
        d.line((*a0, *a1), fill=MUTED, width=4 * SS)
        corners = [self.L(name, *self.arm_xy(theta, rr, ss)) for rr, ss in
                   ((rim_r, -rim_w), (floor_r, -floor_w), (floor_r, floor_w), (rim_r, rim_w))]
        d.polygon(corners, fill=BUCKET_FILL)
        # The water: a block while every parcel is in, else parcels, flights and puddles.
        tau = self.tau(t) if P["parcels"] is not None else 0.0
        states = [self.parcel_state(p, tau) for p in P["parcels"]] if P["parcels"] is not None else []
        wb = man["parcel_half_span_m"] + man["parcel_radius_m"]
        pr = man["parcel_radius_m"] * self.ppm * SS
        if all(st == "in" for st, _ in states):
            block = [self.L(name, *self.arm_xy(theta, rr, ss)) for rr, ss in
                     ((r0, -wb), (r0 + depth, -wb), (r0 + depth, wb), (r0, wb))]
            d.polygon(block, fill=TEAL)
        else:
            for p, (st, val) in zip(P["parcels"], states):
                if st == "in":
                    X, Y = self.L(name, *self.arm_xy(theta, p["rho"], p["s"]))
                    self.circle(d, X, Y, pr, fill=TEAL)
                elif st == "free":
                    X, Y = self.L(name, *self.flight_pos(p, val))
                    u0 = max(0.0, val - man["trail_s"])
                    X0, Y0 = self.L(name, *self.flight_pos(p, u0))
                    d.line((X0, Y0, X, Y), fill=blend(TEAL, 0.45), width=2 * SS)
                    self.circle(d, X, Y, pr, fill=TEAL)
                else:
                    X, Y = self.L(name, p["x_land"], p["y_land"])
                    if p["hit"] == "floor":
                        d.ellipse((X - 0.035 * self.ppm * SS, Y - 0.012 * self.ppm * SS,
                                   X + 0.035 * self.ppm * SS, Y + 0.012 * self.ppm * SS), fill=blend(TEAL, 0.8 * val))
                    else:
                        self.circle(d, X, Y, pr * 1.4, fill=blend(TEAL, 0.8 * val))
        for (rr0, ss0), (rr1, ss1) in (((rim_r, -rim_w), (floor_r, -floor_w)), ((floor_r, -floor_w), (floor_r, floor_w)),
                                       ((floor_r, floor_w), (rim_r, rim_w))):
            p0, p1 = self.L(name, *self.arm_xy(theta, rr0, ss0)), self.L(name, *self.arm_xy(theta, rr1, ss1))
            d.line((*p0, *p1), fill=TEXT, width=3 * SS)
        self.circle(d, *a0, 6 * SS, fill=WHITE)
        water_in = all(st == "in" for st, _ in states)
        push = P["omega"] ** 2 * r0 / g - math.cos(theta)
        return {"theta": theta, "water_in": water_in, "push": push}

    def draw_text(self, d: ImageDraw.ImageDraw, states: dict, t: float, hud_alpha: float) -> None:
        man, ev = self.man, self.ev
        for name, st in states.items():
            px_, py = self.panels[name]["pivot"]
            top = py - PANEL_TOP_ABOVE_PIVOT
            floor = py + self.hp * self.ppm
            d.text((LABEL_X, top + 20), label_text(man, name), font=self.font, fill=TEXT, anchor="lm")
            if st["water_in"]:
                d.text((READ_X, top + 20), push_text(st["push"]), font=self.font, fill=TEXT, anchor="rm")
            else:
                d.text((READ_X, top + 20), "spills", font=self.font, fill=CORAL, anchor="rm")
            if hud_alpha > 0.02:
                for j, line in enumerate(fixed_lines(man, ev, name)):
                    col = GOLD if (name == "slow" and j == 0) else MUTED
                    d.text((LABEL_X, floor - 78 + 34 * j), line, font=self.font_small, fill=blend(col, hud_alpha), anchor="lm")
            hx, hy = man["head_center_m"]
            d.text((px_ + (hx - man["head_radius_m"] - 0.04) * self.ppm, py - hy * self.ppm), "you",
                   font=self.font_small, fill=blend(WHITE, 0.8), anchor="rm")
        if hud_alpha > 0.02:
            d.text((W / 2, LEGEND_Y), legend_text(), font=self.font, fill=blend(TEXT, hud_alpha), anchor="mm")
            d.text((W / 2, TAG_Y), tag_text(), font=self.font_small, fill=blend(MUTED, hud_alpha), anchor="mm")

    def live_frame(self, f: int, title_alpha: float | None = None, hud_alpha: float = 0.0) -> np.ndarray:
        """Frame f with the geometry at f / fps; title_alpha and hud_alpha override the title and
        the legend/readout/card blend during the loop fade."""
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
        layer = Image.new("RGB", (W * SS, (GEOM_Y1 - GEOM_Y0) * SS), BG)
        ld = ImageDraw.Draw(layer)
        states = {name: self.draw_panel(ld, name, t, hud_alpha) for name in PANELS}
        img.paste(layer.reduce(SS), (0, GEOM_Y0))
        d = ImageDraw.Draw(img)
        self.draw_text(d, states, t, hud_alpha)
        if title_alpha > 0.0:
            for j, line in enumerate(man["title"].split("|")):
                d.text((W / 2, 190 + j * 62), line, font=self.font_title, fill=blend(TEXT, title_alpha), anchor="mm")
        if t >= man["payoff_t"]:
            a = min(1.0, (t - man["payoff_t"]) / man["payoff_hold"]) * hud_alpha
            for j, line in enumerate(payoff_lines(man, self.ev)):
                d.text((W / 2, PAYOFF_Y + j * 56), line, font=self.font, fill=blend(GOLD, a), anchor="mm")
        return np.asarray(img, dtype=np.uint8)

    def frame_at(self, f: int) -> np.ndarray:
        man = self.man
        total = int(round(man["scene_duration"] * self.fps))
        fade_frames = int(round(man["loop_fade"] * self.fps))
        if f == total - 1:
            return self.live_frame(0)   # the scene is periodic: the last frame repeats the first
        if f >= total - fade_frames:
            # The geometry runs on; the legend, readouts and card fade out over the first half of
            # the loop fade and the title fades in over the second half, so the two never overlap.
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
        wrap = self.live_frame(total, title_alpha=1.0, hud_alpha=0.0)   # the geometry one period on, drawn live
        diff = np.abs(first.astype(int) - wrap.astype(int))
        print(f"periodicity check: the scene drawn live at {self.man['scene_duration']:g} s differs from 0 s in "
              f"{int((diff.max(axis=2) > 24).sum())} px (max channel difference {int(diff.max())})")
        prev = self.frame_at(total - 2)
        diff = np.abs(prev.astype(int) - last.astype(int))
        print(f"loop step: the frame before the last differs from the last in {int((diff.max(axis=2) > 24).sum())} px "
              f"(the fast arm turns {math.degrees(self.panels['fast']['omega'] / self.fps):.2f} degrees per frame, "
              f"the slow arm {math.degrees(self.panels['slow']['omega'] / self.fps):.2f})")
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
    man = json.loads((ROOT / "projects/bucket/manifest.json").read_text())
    ev = measure(man)
    if "--measure-only" in sys.argv:
        return
    if "--frames" in sys.argv:
        times = [float(v) for v in sys.argv[sys.argv.index("--frames") + 1].split(",")]
        r = Renderer(man, ev)
        (ROOT / "media/bucket").mkdir(parents=True, exist_ok=True)
        for tv in times:
            Image.fromarray(r.frame_at(int(round(tv * man["fps"])))).save(ROOT / f"media/bucket/smoke-{tv}.png")
        print("smoke frames: " + ", ".join(f"{tv}" for tv in times))
        return
    Renderer(man, ev).render(ROOT / "media/bucket/footage.mp4")


if __name__ == "__main__":
    main()
