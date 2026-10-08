#!/usr/bin/env python3
"""Round pencil or hexagonal pencil: which one rolls off the desk?

Two panels on the same clock, the same desk drawn the same way at the same
scale, seen end-on. Two 7 mm pencils lie on a level desk, their centres
start_to_edge_m from the edge, and each gets the same nudge: its centre
moves off at v0 (chosen). Top panel, the ROUND pencil: a solid cylinder
of radius r rolling without slipping and with no rolling loss (chosen),
so it keeps v0, reaches the edge after d / v0 and leaves the desk as its
centre passes the edge; then it falls freely from a desk desk_height_m
high (t = sqrt(2 H / g), landing v0 t out). Bottom panel, the HEXAGONAL
pencil: a uniform regular hexagonal prism across_flats_m across the
flats, so the corner radius is R = (a / 2) / cos 30 deg (the side length
equals R), I = 5/12 m R^2 about the centre and 17/12 m R^2 about a
corner. The nudge leaves its centre moving at v0 on an arc about the
front corner, omega0 = v0 / R. It rolls one face at a time: pivoting on
the front corner from phi = -30 deg to +30 deg (phi the angle of the
centre from the vertical over the corner),

    phi'' = (12 g / (17 R)) sin phi,

energy conserved over a face (the start and end heights are equal, so
the end spin equals the start spin). At the next corner an inelastic
no-slip impact conserves the angular momentum about the new corner:
(17/12) omega+ = (5/12 + cos 60 deg) omega-, so omega+ = (11/17)
omega-, 121/289 of the energy. It passes the top of a corner only while
the spin at the start of the face exceeds sqrt(24 g (1 - cos 30 deg) /
(17 R)); below that it rocks back onto the same face and lands on the
rear corner with the same impact rule, so each rock keeps 11/17 of the
spin. The corner stays loaded while omega^2 R < g cos phi (worst at the
face ends); the grip needed at the corner is |a_x| / (g + a_y) of the
centre's acceleration; the desk grip is grip (chosen). Every face and
rock is integrated by RK4 at steps_per_second, the face end located by
bisection inside the last step; the pencil counts as stopped when its
spin is under stop_fraction of the corner threshold. The run repeats
every cycle_s seconds of video with a crossfade back to the setup; the
cycle divides the scene length, so the scene is exactly periodic and the
last frame equals the first. Shown at 1/slow speed. Deterministic, no
seed.

Measured and printed: the hexagon's geometry and the impact fraction,
the corner threshold and the hop limit, the RK4 faces and rocks with the
spin after each impact, the grip needed, the round pencil's run and
fall, the speed variants and the tilt limit for the description, the
brief's checks, the schedule in video time, the on-screen text widths and
the layout clearances.

usage: pencil.py [--measure-only] [--frames t1,t2,...]
"""

from __future__ import annotations

import json
import math
import multiprocessing
import os
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction
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
STRIPE = (16, 20, 26)
FINGER = (196, 170, 150)
NAIL = (232, 214, 200)

# Layout: overlay at y 96..130 (captions.py), three title rows at y 186/244/302
# for the first seconds, then the legend at y 236 and the shared clock at y
# 290; two bands stacked, the round pencil in y 330..880 and the hexagonal
# pencil in 880..1430, each drawn at 2x in its own layer (so the falling
# pencil is clipped at its band); each band has its label row 40 px under the
# band top, its second row at 84 and its speed readout at 120 (left column
# from x 40), the "rolled" readout at 40 right-aligned at x 1040, the 10x
# cross-section inset under it in the top right corner; the desk slab from
# desk_top_dy under the band top, its edge at edge_x_px with one leg under
# it; the gold event row under the desk at 462, left-aligned at x 40;
# captions at caption_y 0.75 (y 1440..1530); the card from y 1572 at a 48 px
# pitch.
LEGEND_Y, CLOCK_Y = 236, 290
TITLE_YS = {2: (190, 252), 3: (186, 244, 302)}
SS = 2
PAYOFF_Y, PAYOFF_PITCH = 1572.0, 48
PANELS = ("round", "hex")
BAND_Y = {"round": 330, "hex": 880}
BAND_H = 550
LABEL_DY, SUB_DY, FIX_DY = 40, 84, 120
EVENT_DY = 462
ROW_X0, ROW_X1 = 40, 1040
SLAB_PX, LEG_W, LEG_GAP, LEG_IN = 28, 22, 24, 50
INSET_X0, INSET_Y0, INSET_W, INSET_H = 760, 66, 280, 274
INSET_DESK = 16                     # the inset's desk top this far above the inset bottom
FINGER_L, FINGER_T = 70.0, 16.0     # the finger mark's length and thickness (band px)
COLOUR = {"round": CORAL, "hex": TEAL}
DEG = math.pi / 180.0


def blend(col, a: float, base=BG) -> tuple:
    a = max(0.0, min(1.0, a))
    return tuple(int(round(c * a + b * (1 - a))) for c, b in zip(col, base))


# --- measurement --------------------------------------------------------------
def swing(w0: float, R: float, g: float, dt: float, keep: bool = False) -> dict:
    """One swing of the hexagon about a corner in the local frame: phi from -30 deg with spin w0 > 0.
    Ends at phi = +30 deg (a face: it passed the top of the corner) or back at -30 deg with the spin
    reversed (a rock). RK4 at dt, the end located by bisection on an RK4 sub-step. Also the peak grip
    needed at the corner |a_x| / (g + a_y) and the least corner load (g + a_y) / g."""
    c = 12.0 * g / (17.0 * R)
    A = math.pi / 6.0
    sin, cos = math.sin, math.cos

    def step(p: float, w: float, h: float) -> tuple[float, float]:
        k1p, k1w = w, c * sin(p)
        k2p, k2w = w + 0.5 * h * k1w, c * sin(p + 0.5 * h * k1p)
        k3p, k3w = w + 0.5 * h * k2w, c * sin(p + 0.5 * h * k2p)
        k4p, k4w = w + h * k3w, c * sin(p + h * k3p)
        return p + h * (k1p + 2.0 * k2p + 2.0 * k3p + k4p) / 6.0, w + h * (k1w + 2.0 * k2w + 2.0 * k3w + k4w) / 6.0

    p, w, n = -A, w0, 0
    grip, load = 0.0, math.inf
    ts, ps, ws = [0.0], [p], [w]
    turned = False
    while True:
        pn, wn = step(p, w, dt)
        if wn <= 0.0:
            turned = True
        done_face = pn >= A
        done_rock = turned and pn <= -A
        if done_face or done_rock:
            lo, hi = 0.0, dt
            for _ in range(80):
                mid = 0.5 * (lo + hi)
                pm, _ = step(p, w, mid)
                if (pm < A) if done_face else (pm > -A):
                    lo = mid
                else:
                    hi = mid
            pe, we = step(p, w, hi)
            T = n * dt + hi
            ts.append(T)
            ps.append(A if done_face else -A)
            ws.append(we)
            break
        p, w = pn, wn
        n += 1
        pdd = c * sin(p)
        ax = R * (pdd * cos(p) - w * w * sin(p))
        ay = R * (-pdd * sin(p) - w * w * cos(p))
        nn = g + ay
        load = min(load, nn / g)
        if nn > 0.0:
            grip = max(grip, abs(ax) / nn)
        if keep or n % 1000 == 0:
            ts.append(n * dt)
            ps.append(p)
            ws.append(w)
    out = {"kind": "face" if done_face else "rock", "T": T, "w0": w0, "w_end": we, "grip": grip, "load": load,
           "steps": n + 1}
    if keep:
        out.update(t=np.array(ts), phi=np.array(ps), w=np.array(ws))
    return out


def hex_run(v0: float, R: float, g: float, dt: float, stop_frac: float, keep: bool = False) -> dict:
    """The hexagonal pencil from the nudge: faces while the spin passes the corner threshold, then rocks
    until the spin after an impact is under stop_frac of the threshold."""
    ratio = 11.0 / 17.0
    wmin = math.sqrt(24.0 * g * (1.0 - math.cos(math.pi / 6.0)) / (17.0 * R))
    whop = math.sqrt(g * math.cos(math.pi / 6.0) / R)
    w = v0 / R
    segs, faces, rocks, t = [], 0, 0, 0.0
    after = []                      # spin after each impact
    if w >= whop:
        return {"hops": True, "w0": w, "faces": 0, "rocks": 0, "segs": [], "after": [], "T_faces": 0.0, "T_stop": 0.0,
                "grip_faces": 0.0, "grip_rocks": 0.0, "load": 0.0, "w_left": w, "energy_err": 0.0}
    sign = 1.0                      # +1 rolling forward, -1 rocking backward
    while True:
        s = swing(abs(w), R, g, dt, keep)
        assert (s["kind"] == "face") == (abs(w) > wmin), "the face/rock outcome disagrees with the threshold"
        s["t0"], s["sign"] = t, sign
        segs.append(s)
        t += s["T"]
        if s["kind"] == "face":
            faces += 1
            w = sign * s["w_end"] * ratio
        else:
            rocks += 1
            sign = -sign
            w = sign * abs(s["w_end"]) * ratio
        after.append(abs(w))
        if s["kind"] == "face" and abs(w) > wmin:
            continue
        if s["kind"] == "face":
            T_faces = t
        if abs(w) < stop_frac * wmin:
            break
    fs = [s for s in segs if s["kind"] == "face"]
    rs = [s for s in segs if s["kind"] == "rock"]
    err = max(abs(abs(s["w_end"]) - s["w0"]) for s in segs)
    return {"hops": False, "w0": v0 / R, "faces": faces, "rocks": rocks, "segs": segs, "after": after,
            "T_faces": sum(s["T"] for s in fs), "T_stop": t, "grip_faces": max((s["grip"] for s in fs), default=0.0),
            "grip_rocks": max((s["grip"] for s in rs), default=0.0), "load": min(s["load"] for s in segs),
            "w_left": after[faces - 1] if faces else v0 / R, "energy_err": err,
            "steps": sum(s["steps"] for s in segs)}


def measure(man: dict) -> dict:
    g, a, r, v0 = man["g"], man["across_flats_m"], man["round_radius_m"], man["nudge_speed_m_s"]
    d0, Hd, mu = man["start_to_edge_m"], man["desk_height_m"], man["grip"]
    dt = 1.0 / man["steps_per_second"]
    sf = man["stop_fraction"]
    S, P, D, fps, F, na = man["slow"], man["cycle_s"], man["scene_duration"], man["fps"], man["reset_fade"], man["nudge_at"]
    ppm = man["px_per_m"]
    cycles = D / P
    assert abs(cycles - round(cycles)) < 1e-9, "the cycle must divide the scene length"
    for key in ("cycle_s", "nudge_at", "first_cycle_at", "reset_fade"):
        assert abs(man[key] * fps - round(man[key] * fps)) < 1e-9, f"{key} must be a whole number of frames"
    R = (a / 2.0) / math.cos(math.pi / 6.0)
    ratio_f = (Fraction(5, 12) + Fraction(1, 2)) / Fraction(17, 12)
    ratio = float(ratio_f)
    c = 12.0 * g / (17.0 * R)
    wmin = math.sqrt(24.0 * g * (1.0 - math.cos(math.pi / 6.0)) / (17.0 * R))
    whop = math.sqrt(g * math.cos(math.pi / 6.0) / R)
    imp_x, imp_y = math.cos(math.pi / 6.0) * (ratio - 1.0), 0.5 * (ratio + 1.0)
    imp_grip = abs(imp_x) / imp_y
    tilt = math.degrees(math.atan((R / 2.0) / (a / 2.0)))
    print(f"setup: the same desk in both panels, seen end-on: two 7 mm pencils on a level desk, their centres "
          f"{d0 * 100:g} cm from the edge, each given the same nudge, its centre moving off at v0 = {v0:g} m/s (chosen); "
          f"g = {g:g} m/s^2; top panel the round pencil, a solid cylinder of radius {r * 1000:g} mm rolling without "
          f"slipping and with no rolling loss (chosen), leaving the desk as its centre passes the edge and falling freely "
          f"from a {Hd * 100:g} cm desk; bottom panel the hexagonal pencil, a uniform regular hexagonal prism {a * 1000:g} "
          f"mm across the flats, the nudge leaving its centre moving at v0 on an arc about the front corner (omega0 = v0 / "
          f"R); the desk grip {mu:g} (chosen); each face and rock integrated by RK4 at {man['steps_per_second']} steps "
          f"per second (dt = {dt:.0e} s), the face end located by bisection inside the last step; stopped when the spin "
          f"is under {sf * 100:g} percent of the corner threshold; shown at 1/{S:g} speed on a {P:g} s cycle "
          f"({P * fps:.0f} frames) with the nudge {na:g} s into the cycle, {cycles:.0f} cycles in {D:g} s; drawn at "
          f"{ppm:g} px per metre with a {man['inset_scale']}x cross-section inset; deterministic, no seed")
    print(f"hexagon: corner radius R = (a / 2) / cos 30 deg = {R * 1000:.4f} mm = {R * 1000:.3f} mm (the side length "
          f"equals R; across the corners {2 * R * 1000:.3f} mm); I = 5/12 m R^2 about the centre, 17/12 m R^2 about a "
          f"corner; on a corner phi'' = (12 g / (17 R)) sin phi = {c:.2f} sin phi per s^2; a face is one side = R = "
          f"{R * 1000:.3f} mm of travel and 60 deg of turn; the centre rises R (1 - cos 30 deg) = {R * (1 - math.cos(math.pi / 6)) * 1000:.4f} "
          f"mm over a corner")
    print(f"impact: angular momentum about the new corner, (17/12) omega+ = (5/12 + cos 60 deg) omega-, so omega+ / "
          f"omega- = {ratio_f} = {ratio:.4f} exactly; the energy kept ({ratio_f})^2 = {ratio_f ** 2} = {ratio ** 2:.4f}; "
          f"the spin each corner takes 1 - 11/17 = {1 - ratio_f} = {1 - ratio:.4f}; the impulse the corner gives, per m R "
          f"omega-: {imp_x:+.4f} along the desk, {imp_y:+.4f} up (the desk pushes, no bounce), a grip of {imp_grip:.4f}")
    print(f"corner threshold: over the top of a corner needs (17/24) R^2 omega^2 > g R (1 - cos 30 deg), omega > "
          f"sqrt(24 g (1 - cos 30 deg) / (17 R)) = {wmin:.4f} rad/s (centre speed {wmin * R:.5f} m/s); hop limit: the "
          f"corner stays loaded while omega^2 R < g cos phi, worst at the face ends (cos 30 deg): omega < {whop:.4f} rad/s "
          f"({whop * R:.5f} m/s); tilt: on a desk tilted by beta the centre passes over the downhill corner when tan beta "
          f"> (R / 2) / (a / 2), beta > {tilt:.4f} deg: a hexagonal pencil tips from rest only past {tilt:.0f} deg")
    run = hex_run(v0, R, g, dt, sf, keep=True)
    assert not run["hops"]
    for s in run["segs"]:
        assert abs(abs(s["w_end"]) - s["w0"]) < 1e-9, "a swing's end spin differs from its start spin"
    rows = []
    for j, s in enumerate(run["segs"]):
        what = f"face {j + 1}" if s["kind"] == "face" else f"rock {j + 1 - run['faces']}"
        rows.append(f"{what} ({'forward' if s['sign'] > 0 else 'back'}) {s['t0'] * 1000:.2f} to "
                    f"{(s['t0'] + s['T']) * 1000:.2f} ms: starts {s['w0']:.4f} rad/s, ends {abs(s['w_end']):.4f} "
                    f"(diff {abs(s['w_end']) - s['w0']:+.1e}), after the impact {run['after'][j]:.4f} rad/s")
    print(f"hexagonal pencil at {v0:g} m/s (omega0 = v0 / R = {v0 / R:.4f} rad/s, under the hop limit "
          f"{whop:.2f}): " + "; ".join(rows))
    dist = run["faces"] * R
    print(f"hexagonal result: {run['faces']} faces = {run['faces']} R = {dist * 1000:.4f} mm = {dist * 1000:.1f} mm in "
          f"{run['T_faces'] * 1000:.2f} ms ({run['T_faces']:.4f} s); spin left after the last face's impact "
          f"{run['w_left']:.4f} rad/s, under the {wmin:.4f} rad/s the next corner needs; then {run['rocks']} rocks "
          f"(each keeps 11/17) until the spin is {run['after'][-1]:.4f} rad/s, under {sf * 100:g} percent of the "
          f"threshold ({sf * wmin:.4f}), stopped at {run['T_stop'] * 1000:.2f} ms ({run['T_stop']:.4f} s) after the nudge; "
          f"grip needed at the corner during the faces {run['grip_faces']:.4f}, during the rocks up to "
          f"{run['grip_rocks']:.4f}, at each impact {imp_grip:.4f}, all under the desk's {mu:g}; least corner load "
          f"{run['load']:.4f} of the weight (positive: the corner never lets go); every swing's end spin equals its "
          f"start spin within {run['energy_err']:.1e} rad/s; {run['steps']} RK4 steps")
    assert run["grip_faces"] < mu and run["grip_rocks"] < mu and imp_grip < mu and run["load"] > 0.0
    # The drawn hexagon turns about its pivot: the pivot is always one of its corners.
    worst = 0.0
    for tt in np.linspace(0.0, run["T_stop"] * 1.05, 2001):
        q = hex_state(ev_stub := {"R": R, "hex": run}, man, float(tt))
        if q["pivot"] is not None:
            cxq, cyq = q["x"], q["h"]
            dmin = min(math.hypot(cxq + R * math.sin(a_v * DEG + q["theta"]) - q["pivot"], cyq + R * math.cos(a_v * DEG + q["theta"]))
                       for a_v in (30, 90, 150, 210, 270, 330))
            worst = max(worst, dmin)
    print(f"drawing check: over 2001 times the pivot corner sits on a corner of the turned hexagon within {worst:.1e} m")
    assert worst < 1e-9
    # The first rock's highest point (the closest it comes to the third corner).
    s3 = run["segs"][run["faces"]]
    peak = float(np.max(s3["phi"])) / DEG
    print(f"the first rock climbs from -30 deg to {peak:.2f} deg over the third corner ({peak + 30:.2f} deg of tilt) "
          f"and falls back; the rocks then get smaller by 11/17 in spin each time")
    # Round pencil.
    t_edge = d0 / v0
    t_fall = math.sqrt(2.0 * Hd / g)
    land = v0 * t_fall
    # The drawn circle passes the desk corner during the fall: its deepest overlap with the corner.
    ts = np.linspace(0.0, 0.05, 50001)
    dist_c = np.sqrt((v0 * ts) ** 2 + (r - 0.5 * g * ts ** 2) ** 2)
    pen = float(np.max(np.maximum(0.0, r - dist_c)))
    print(f"round pencil: rolls without loss at {v0:g} m/s (spin {v0 / r:.4f} rad/s); its centre reaches the edge "
          f"{d0 * 100:g} cm on after {t_edge:.4f} s = {t_edge:.3f} s; it falls freely from the {Hd * 100:g} cm desk for "
          f"sqrt(2 H / g) = {t_fall:.4f} s = {t_fall:.3f} s and lands v0 t = {land * 100:.3f} cm = {land * 100:.1f} cm out "
          f"from the edge at {math.hypot(v0, g * t_fall):.3f} m/s; the drawn circle overlaps the desk corner by at most "
          f"{pen * 1000:.4f} mm ({pen * ppm:.2f} px) as it tips off (its centre leaves at the edge, v0^2 / r = "
          f"{v0 * v0 / r:.2f} m/s^2 under g); rolling at a steady speed needs no grip")
    assert pen * ppm < 1.0, "the falling circle cuts the desk corner by a pixel or more"
    ev: dict = {"R": R, "ratio": ratio, "wmin": wmin, "whop": whop, "c": c, "hex": run, "t_edge": t_edge, "t_fall": t_fall,
                "land": land, "dist": dist, "tilt": tilt, "imp_grip": imp_grip, "peak": peak}
    # Variants for the description.
    var = {}
    descr = []
    for vv in man["description_speeds_m_s"] + [v0]:
        rv = run if vv == v0 else hex_run(vv, R, g, dt, sf)
        var[vv] = rv
        if rv["hops"]:
            descr.append(f"{vv:.2f} m/s: omega0 {rv['w0']:.2f} rad/s over the hop limit {whop:.2f}: the corner lets go "
                         f"at once, the model ends (a real pencil hops)")
        else:
            descr.append(f"{vv:.2f} m/s (omega0 {rv['w0']:.2f} rad/s): {rv['faces']} face{'s' if rv['faces'] != 1 else ''} "
                         f"= {rv['faces'] * R * 1000:.1f} mm in {rv['T_faces'] * 1000:.1f} ms, spin left "
                         f"{rv['w_left']:.2f} rad/s, {rv['rocks']} rocks, stopped at {rv['T_stop'] * 1000:.1f} ms, grip "
                         f"needed {rv['grip_faces']:.3f} (rocks {rv['grip_rocks']:.3f}); the round pencil reaches the edge "
                         f"in {d0 / vv:.3f} s and lands {vv * t_fall * 100:.1f} cm out")
    print("for the description (hexagonal pencil at other nudges): " + "; ".join(descr))
    ev["var"] = var
    # The brief's checks.
    v10, v12, v18, v20 = (var[x] for x in (0.10, 0.12, 0.18, 0.20))
    checks: list[tuple[str, float, float, float]] = [
        ("R (mm)", R * 1000, 4.041, 6e-4), ("omega+ / omega- = 11/17", ratio, 11 / 17, 1e-15),
        ("omega+ / omega- (4 places)", ratio, 0.6471, 6e-5), ("energy kept 121/289", ratio ** 2, 121 / 289, 1e-15),
        ("corner threshold (rad/s)", wmin, 21.42, 6e-3), ("corner threshold (m/s)", wmin * R, 0.0866, 6e-5),
        ("hop limit (rad/s)", whop, 45.84, 6e-3), ("hop limit (m/s)", whop * R, 0.1853, 6e-5),
        ("omega0 at 0.15 (rad/s)", v0 / R, 37.12, 6e-3),
        ("face 1 end spin (rad/s)", abs(run["segs"][0]["w_end"]), 37.12, 6e-3),
        ("after impact 1 (rad/s)", run["after"][0], 24.02, 6e-3),
        ("face 2 end spin (rad/s)", abs(run["segs"][1]["w_end"]), 24.02, 6e-3),
        ("after impact 2 (rad/s)", run["after"][1], 15.54, 6e-3),
        ("faces at 0.15", run["faces"], 2, 0), ("distance (mm)", dist * 1000, 8.08, 6e-3),
        ("distance (mm, 1 place)", dist * 1000, 8.1, 6e-2), ("time for 2 faces (ms)", run["T_faces"] * 1000, 102.0, 6e-2),
        ("grip needed at the corner", run["grip_faces"], 0.302, 6e-4),
        ("0.10 m/s faces", v10["faces"], 1, 0), ("0.10 m/s time (ms)", v10["T_faces"] * 1000, 64.2, 6e-2),
        ("0.12 m/s faces", v12["faces"], 1, 0), ("0.12 m/s time (ms)", v12["T_faces"] * 1000, 44.5, 6e-2),
        ("0.18 m/s faces", v18["faces"], 2, 0), ("0.18 m/s time (ms)", v18["T_faces"] * 1000, 72.4, 6e-2),
        ("0.18 m/s grip needed", v18["grip_faces"], 0.89, 6e-3),
        ("0.20 m/s omega0 (rad/s)", v20["w0"], 49.5, 6e-2), ("0.20 m/s hops", 1.0 if v20["hops"] else 0.0, 1.0, 0),
        ("tilt to tip from rest (deg)", tilt, 30.0, 1e-9),
        ("round: time to the edge (s)", t_edge, 1.667, 6e-4), ("round: fall (s)", t_fall, 0.391, 6e-4),
        ("round: lands out (cm)", land * 100, 5.9, 6e-2),
    ]
    fails = 0
    out = []
    for name, got, want, tol in checks:
        ok = abs(got - want) <= tol
        fails += 0 if ok else 1
        out.append(f"{name}: brief {want:g}, sim {got:.6g}, diff {got - want:+.1e}: {'ok' if ok else 'FAIL'}")
    rk_ok = 10 <= run["rocks"] <= 11
    fails += 0 if rk_ok else 1
    out.append(f"rocks before the spin is under 1 percent of the threshold: brief about 10 to 11, sim {run['rocks']}: "
               f"{'ok' if rk_ok else 'FAIL'}")
    print(f"checks against the brief ({len(checks) + 1} checks, {fails} failed): " + "; ".join(out))
    assert fails == 0, "a check against the brief failed"
    ev["check_count"] = len(checks) + 1
    # Geometry on screen.
    x0, edge, top = float(man["start_x_px"]), float(man["edge_x_px"]), float(man["desk_top_dy"])
    assert abs((edge - x0) - d0 * ppm) < 1e-9, "the start is not 25 cm (750 px) from the edge"
    print(f"drawing: {ppm:g} px per metre; the round pencil {2 * r * ppm:.1f} px across, the hexagonal one {a * ppm:.1f} px "
          f"across the flats ({2 * R * ppm:.1f} across the corners); centres start at x {x0:.0f}, the edge at x {edge:.0f}: "
          f"{edge - x0:.0f} px = {(edge - x0) / ppm * 100:g} cm; the hexagonal pencil stops {dist * ppm:.1f} px on; "
          f"inset at {man['inset_scale']}x: {a * ppm * man['inset_scale']:.0f} px across the flats")
    # The schedule in video time.
    t0 = man["first_cycle_at"]
    k0 = math.ceil((0.0 - t0) / P - 1e-9) - 1
    k1 = math.floor((D - t0) / P - 1e-9)
    starts = [t0 + kk * P for kk in range(k0, k1 + 1)]

    def lst(off_: float) -> str:
        return ", ".join(f"{st + off_:.2f}" for st in starts if 0.0 <= st + off_ < D)

    cy = top - r * ppm                                   # the centre line of both pencils (band-local)
    gone_drop = (BAND_H - cy + r * ppm) / ppm             # the round pencil must fall this far to leave the band
    t_gone = math.sqrt(2.0 * gone_drop / g)
    ev["t_gone"] = t_gone
    gone_v = na + S * (t_edge + t_gone)
    assert gone_v < P - F, "the falling round pencil is still in the band at the reset fade"
    stop_v = na + S * run["T_stop"]
    print(f"schedule (video time, 1/{S:g} speed): cycles of {P:g} s start at " + ", ".join(f"{st:.2f}" for st in starts)
          + f" s; the finger mark moves in over the first {man['finger_s']:g} s and taps both pencils {na:g} s into each "
          f"cycle at {lst(na)} s; the hexagonal pencil ends its first face {S * run['segs'][0]['T']:.3f} s later, its "
          f"second {S * run['T_faces']:.3f} s after the nudge at {lst(na + S * run['T_faces'])} s, its first rock peaks "
          f"and falls back by {S * (run['T_faces'] + run['segs'][run['faces']]['T']):.3f} s after the nudge and it "
          f"stops {S * run['T_stop']:.3f} s after the nudge at {lst(stop_v)} s (its event row lights); the round pencil "
          f"reaches the edge {S * t_edge:.3f} s after the nudge at {lst(na + S * t_edge)} s (its event row lights) and is "
          f"out of the band {S * t_gone:.3f} s later at {lst(gone_v)} s ({gone_v:.3f} s into the cycle; it would hit the "
          f"floor at {na + S * (t_edge + t_fall):.3f} s into the cycle); the reset crossfade runs over the last {F:g} s "
          f"of each cycle (from {lst(P - F)} s); title until {man['title_until']:g} s; payoff card from "
          f"{man['payoff_t']:g} s; the title fades back in over the last {man['loop_fade']:g} s and the last frame "
          f"repeats the first (the scene is periodic: {D:g} s holds exactly {cycles:.0f} cycles)")
    ev["stop_v"], ev["gone_v"] = stop_v, gone_v
    # Text widths.
    font = os.environ["SEED_ZERO_FONT"]
    f24, f28, f32, f34, f40, f56 = (ImageFont.truetype(font, n) for n in (24, 28, 32, 34, 40, 56))
    widths = {"overlay@34": (f34, man["overlay"])}
    for j, line in enumerate(man["title"].split("|")):
        widths[f"title line {j + 1}@56"] = (f56, line)
    widths["legend@40"] = (f40, legend_text(man))
    widths["clock@28"] = (f28, clock_text(1.2515))
    widths["clock held@28"] = (f28, clock_text(-1.0))
    for m in PANELS:
        widths[f"label {m}@40"] = (f40, label_text(m))
        widths[f"sublabel {m}@28"] = (f28, sub_text())
        widths[f"event {m}@32"] = (f32, event_text(ev, m))
    widths["speed@28"] = (f28, speed_text(0.155))
    widths["speed floor@28"] = (f28, floor_text())
    widths["rolled mm@28"] = (f28, rolled_text(0.0999))
    widths["rolled cm@28"] = (f28, rolled_text(0.25))
    widths["inset label@24"] = (f24, inset_label(man))
    for j, line in enumerate(payoff_lines(man, ev)):
        widths[f"payoff line {j + 1}@40"] = (f40, line)
    print("text widths (the on-screen strings verbatim): " + ", ".join(f"{kk} {f.getlength(s):.0f} px '{s}'"
                                                                      for kk, (f, s) in widths.items()))
    assert all(f.getlength(s) < 950 for f, s in widths.values()), "a text line is wider than 950 px"
    assert len(payoff_lines(man, ev)) <= 6, "the card has more than six lines"
    assert len(man["title"].split("|")) in TITLE_YS
    # Layout checks (band-local boxes).
    left = ROW_X0 + max(max(f40.getlength(label_text(m)) for m in PANELS), f28.getlength(sub_text()),
                        f28.getlength(speed_text(0.155)), f28.getlength(floor_text()))
    rw = max(f28.getlength(rolled_text(0.0999)), f28.getlength(rolled_text(0.25)))
    ev_w = max(f32.getlength(event_text(ev, m)) for m in PANELS)
    leg_x0 = edge - LEG_IN - LEG_W
    il_w = f24.getlength(inset_label(man))
    boxes = {"left column": (ROW_X0 - 8, LABEL_DY - 28, left + 8, FIX_DY + 22),
             "rolled": (ROW_X1 - rw - 8, LABEL_DY - 22, ROW_X1 + 8, LABEL_DY + 22),
             "inset": (INSET_X0, INSET_Y0, INSET_X0 + INSET_W, INSET_Y0 + INSET_H),
             "desk and pencils": (0, cy - r * ppm - 4, edge + 2, top + SLAB_PX),
             "leg": (leg_x0, top + SLAB_PX, leg_x0 + LEG_W, BAND_H - LEG_GAP),
             "event row": (ROW_X0 - 8, EVENT_DY - 26, ROW_X0 + ev_w + 8, EVENT_DY + 26)}
    hex_top = (INSET_Y0 + INSET_H - INSET_DESK) - 2.0 * R * ppm * man["inset_scale"]
    il_box = (INSET_X0 + 10, INSET_Y0 + 6, INSET_X0 + 10 + il_w, INSET_Y0 + 32)
    ins_cx = INSET_X0 + INSET_W / 2.0
    hex_half = R * ppm * man["inset_scale"]
    print(f"row check: the left column spans x {ROW_X0} to {left:.0f} px and y {LABEL_DY - 20} to {FIX_DY + 14} under "
          f"the band top; the rolled readout x {ROW_X1 - rw:.0f} to {ROW_X1} at y {LABEL_DY}; the inset x {INSET_X0} to "
          f"{INSET_X0 + INSET_W} and y {INSET_Y0} to {INSET_Y0 + INSET_H} (its desk at y {INSET_Y0 + INSET_H - INSET_DESK}, "
          f"the hexagon's highest corner at y {hex_top:.0f}, its body within x {ins_cx - hex_half:.0f} to "
          f"{ins_cx + hex_half:.0f}, the label x {il_box[0]:.0f} to {il_box[2]:.0f} at y {il_box[1]:.0f} to {il_box[3]:.0f}); "
          f"the pencils' centre line at y {cy:.1f}, their tops at {cy - r * ppm:.1f}, the desk top at {top:.0f} (slab to "
          f"{top + SLAB_PX:.0f}); the leg x {leg_x0:.0f} to {leg_x0 + LEG_W:.0f} down to {BAND_H - LEG_GAP}; the event row "
          f"x {ROW_X0} to {ROW_X0 + ev_w:.0f} (widest {ev_w:.0f} px) at y {EVENT_DY - 20} to {EVENT_DY + 20}; the finger "
          f"mark from x {x0 - r * ppm - FINGER_L - 60:.0f}; the round pencil falls past the edge between x {edge:.0f} and "
          f"{edge + v0 * t_gone * ppm + r * ppm:.0f} (clear of the leg at {leg_x0:.0f} to {leg_x0 + LEG_W:.0f}); each band "
          f"is {BAND_H} px tall (y {BAND_Y['round']} to {BAND_Y['round'] + BAND_H} and {BAND_Y['hex']} to "
          f"{BAND_Y['hex'] + BAND_H}); the caption band starts at y {int(man['caption_y'] * H)}; the title rows end at y "
          f"{TITLE_YS[len(man['title'].split('|'))][-1] + 28}, the band text starts at y {BAND_Y['round'] + LABEL_DY - 20}; "
          f"the overlay band ends at y 130")
    for a_name, a_box in boxes.items():
        for b_name, b_box in boxes.items():
            if a_name < b_name:
                sep = a_box[2] <= b_box[0] or b_box[2] <= a_box[0] or a_box[3] <= b_box[1] or b_box[3] <= a_box[1]
                assert sep, f"{a_name} meets {b_name}"
    # The hexagon stays inside the circle of radius R about its centre, and its centre is never higher
    # than R over the inset desk: the circle's half-width at the label's bottom edge bounds the body there.
    c_top = (INSET_Y0 + INSET_H - INSET_DESK) - hex_half
    dy = c_top - il_box[3]
    half_at = math.sqrt(max(0.0, hex_half ** 2 - dy ** 2))
    print(f"inset label check: the label ends at x {il_box[2]:.0f}, y {il_box[3]:.0f}; the hexagon's centre is at least "
          f"y {c_top:.0f} and its body at the label's bottom edge spans at most x {ins_cx - half_at:.0f} to {ins_cx + half_at:.0f}")
    assert il_box[2] + 4 < ins_cx - half_at, "the inset label meets the hexagon"
    assert hex_top > INSET_Y0 + 4, "the hexagon leaves the inset"
    assert ins_cx - hex_half > INSET_X0 + 4 and ins_cx + hex_half < INSET_X0 + INSET_W - 4
    assert edge + v0 * t_gone * ppm + r * ppm < W, "the falling pencil leaves the frame sideways"
    assert x0 - r * ppm - FINGER_L - 60 > 0
    assert BAND_Y["hex"] + BAND_H <= int(man["caption_y"] * H), "the bottom band reaches the caption band"
    assert PAYOFF_Y - 20 > int(man["caption_y"] * H) + 90, "the card meets the caption band"
    return ev


def legend_text(man: dict) -> str:
    return f"same desk, same nudge, 1/{man['slow']:g} speed"


def clock_text(r: float) -> str:
    return "before the nudge" if r < 0.0 else f"{r:.3f} s after the nudge"


def label_text(m: str) -> str:
    return "round pencil" if m == "round" else "hexagonal pencil"


def sub_text() -> str:
    return "7 mm, same nudge"


def speed_text(v: float) -> str:
    return f"speed {v:.2f} m/s"


def floor_text() -> str:
    return "on the floor"


def rolled_text(x: float) -> str:
    return f"rolled {x * 100:.1f} cm" if x >= 0.1 else f"rolled {x * 1000:.1f} mm"


def event_text(ev: dict, m: str) -> str:
    if m == "round":
        return f"round: off the desk at {ev['t_edge']:.2f} s"
    return f"hexagonal: stopped after {ev['hex']['faces']} faces, {ev['dist'] * 1000:.0f} mm"


def inset_label(man: dict) -> str:
    return f"{man['inset_scale']}x"


def payoff_lines(man: dict, ev: dict) -> list[str]:
    h = ev["hex"]
    text = man["payoff_text"].format(t_edge=ev["t_edge"], land_cm=ev["land"] * 100, faces=h["faces"],
                                     dist_mm=ev["dist"] * 1000, t_faces=h["T_faces"], wmin=ev["wmin"],
                                     w_left=h["w_left"])
    return [s.strip() for s in text.split("|")]


# --- state over time ----------------------------------------------------------
def hex_state(ev: dict, man: dict, rt: float) -> dict:
    """The hexagonal pencil rt real seconds after the nudge: centre (metres from its start, height of
    the centre above the desk), body turn theta (clockwise, rad), spin, the pivot corner (desk x) or None."""
    R = ev["R"]
    A = math.pi / 6.0
    run = ev["hex"]
    if rt < 0.0:
        return {"x": 0.0, "h": R * math.cos(A), "theta": 0.0, "w": 0.0, "pivot": None, "pv": None, "stopped": False}
    # Walk the segments: pivot positions and the turn at the start of each.
    pivot = R / 2.0
    theta = 0.0
    for j, s in enumerate(run["segs"]):
        sg = s["sign"]
        if rt < s["t0"] + s["T"]:
            u = rt - s["t0"]
            pl = float(np.interp(u, s["t"], s["phi"]))
            wl = float(np.interp(u, s["t"], s["w"]))
            pw = sg * pl                           # the world angle of the centre from the vertical over the pivot
            th = theta + (pw - sg * (-A))
            # the pivot vertex: a = pw + 180 deg = a_v + th, a_v the vertex's angle in the body
            return {"x": pivot + R * math.sin(pw) - 0.0, "h": R * math.cos(pw), "theta": th, "w": sg * wl,
                    "pivot": pivot, "pv": pw, "stopped": False}
        pe = sg * (A if s["kind"] == "face" else -A)
        theta += pe - sg * (-A)
        # The next pivot: after a face the next corner forward; after a rock the corner at the other end.
        if s["kind"] == "face":
            pivot = pivot + sg * R
        else:
            pivot = pivot - sg * R
    centre = run["faces"] * R
    return {"x": centre, "h": R * math.cos(A), "theta": theta, "w": 0.0, "pivot": None, "pv": None, "stopped": True}


def round_state(ev: dict, man: dict, rt: float) -> dict:
    v0, r, g, d0 = man["nudge_speed_m_s"], man["round_radius_m"], man["g"], man["start_to_edge_m"]
    if rt < 0.0:
        return {"x": 0.0, "drop": 0.0, "theta": 0.0, "v": 0.0, "off": False, "floor": False}
    x = v0 * rt
    th = x / r
    if rt < ev["t_edge"]:
        return {"x": x, "drop": 0.0, "theta": th, "v": v0, "off": False, "floor": False}
    u = rt - ev["t_edge"]
    floor = u >= ev["t_fall"]
    return {"x": x, "drop": 0.5 * g * u * u, "theta": th, "v": math.hypot(v0, g * u), "off": True, "floor": floor}


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
        self.font_inset = ImageFont.truetype(font, 24 * SS)
        self.font_event = ImageFont.truetype(font, 32)
        self.ppm = float(man["px_per_m"])
        self.S = man["slow"]
        self.P = man["cycle_s"]
        self.P_f = int(round(man["cycle_s"] * self.fps))
        self.c0_f = int(round(man["first_cycle_at"] * self.fps))
        self.na, self.F = man["nudge_at"], man["reset_fade"]
        self.r = man["round_radius_m"]
        self.R = ev["R"]
        self.x0 = float(man["start_x_px"])
        self.edge = float(man["edge_x_px"])
        self.top = float(man["desk_top_dy"])
        self.cy = self.top - self.r * self.ppm
        self.k = self.ppm * man["inset_scale"]
        # The hexagon's centre path, sampled densely, for its trail.
        ts = np.linspace(0.0, ev["hex"]["T_stop"], 400)
        self.hex_path = [(t, hex_state(ev, man, float(t))) for t in ts]

    def phase(self, f: int) -> tuple[int, float]:
        k, tau_f = divmod(f - self.c0_f, self.P_f)
        return k, tau_f / self.fps

    @staticmethod
    def L_(x: float, y: float) -> tuple[float, float]:
        """Layer (2x) pixel of a band-local point, rounded to 1e-4 px so equal states draw equal pixels."""
        return round(x * SS, 4), round(y * SS, 4)

    def draw_desk(self, d: ImageDraw.ImageDraw) -> None:
        top, edge = self.top, self.edge
        s0, s1 = self.L_(-20, top), self.L_(edge, top + SLAB_PX)
        d.rounded_rectangle((s0[0], s0[1], s1[0], s1[1]), radius=6 * SS, fill=DECK_A)
        t0, t1 = self.L_(0, top), self.L_(edge - 6, top)
        d.line((*t0, *t1), fill=DECK_B, width=3 * SS)
        e0, e1 = self.L_(edge - 1, top + 6), self.L_(edge - 1, top + SLAB_PX - 6)
        d.line((*e0, *e1), fill=RIM, width=3 * SS)
        lx = edge - LEG_IN - LEG_W
        l0, l1 = self.L_(lx, top + SLAB_PX), self.L_(lx + LEG_W, BAND_H - LEG_GAP)
        d.rectangle((l0[0], l0[1], l1[0], l1[1]), fill=DECK_A)
        # The start mark under the pencils and the 25 cm tick at the edge.
        for xx in (self.x0,):
            a0, a1 = self.L_(xx, top + 4), self.L_(xx, top + 14)
            d.line((*a0, *a1), fill=RIM, width=2 * SS)

    def hex_pts(self, cx: float, cy: float, rad: float, theta: float) -> list[tuple[float, float]]:
        return [(cx + rad * math.sin(a * DEG + theta), cy - rad * math.cos(a * DEG + theta)) for a in (30, 90, 150, 210, 270, 330)]

    def draw_pencil(self, d: ImageDraw.ImageDraw, m: str, cx: float, cy: float, scale: float, theta: float,
                    pivot_xy=None, lw: float = 1.0) -> None:
        """A pencil end-on at band point (cx, cy), scale px per metre: the body and a dark stripe from the
        centre to the rim (to the top at theta 0), the hexagon's pivot corner in gold."""
        col = COLOUR[m]
        if m == "round":
            rad = self.r * scale
            p0, p1 = self.L_(cx - rad, cy - rad), self.L_(cx + rad, cy + rad)
            d.ellipse((p0[0], p0[1], p1[0], p1[1]), fill=col, outline=blend(col, 0.55, STRIPE), width=max(1, int(round(lw * SS))))
            tip = (cx + rad * math.sin(theta), cy - rad * math.cos(theta))
        else:
            rad = self.R * scale
            pts = self.hex_pts(cx, cy, rad, theta)
            d.polygon([self.L_(*p) for p in pts], fill=col, outline=blend(col, 0.55, STRIPE), width=max(1, int(round(lw * SS))))
            # The stripe to the middle of a face (the face on top at theta 0).
            tip = (cx + rad * math.cos(math.pi / 6) * math.sin(theta), cy - rad * math.cos(math.pi / 6) * math.cos(theta))
        d.line((*self.L_(cx, cy), *self.L_(*tip)), fill=STRIPE, width=max(2, int(round(2.2 * lw * SS))))
        c0, c1 = self.L_(cx - 1.6 * lw, cy - 1.6 * lw), self.L_(cx + 1.6 * lw, cy + 1.6 * lw)
        d.ellipse((c0[0], c0[1], c1[0], c1[1]), fill=STRIPE)
        if pivot_xy is not None:
            pr = 2.2 * lw + 1.0
            q0, q1 = self.L_(pivot_xy[0] - pr, pivot_xy[1] - pr), self.L_(pivot_xy[0] + pr, pivot_xy[1] + pr)
            d.ellipse((q0[0], q0[1], q1[0], q1[1]), fill=GOLD)

    def draw_finger(self, d: ImageDraw.ImageDraw, tau: float) -> None:
        """The finger-tap mark: it slides in from the left, taps the pencil at the nudge, and pulls back."""
        na, fs = self.na, self.man["finger_s"]
        left = self.x0 - self.r * self.ppm               # the pencils' left side
        if tau < na:
            u = max(0.0, (tau - (na - fs)) / fs)
            gap = 60.0 * (1.0 - u * u)
            a = 1.0
        else:
            u = (tau - na) / 0.6
            if u >= 1.0:
                return
            gap = 60.0 * u
            a = 1.0 - u
        x1 = left - gap
        x0 = x1 - FINGER_L
        y0, y1 = self.cy - FINGER_T / 2.0, self.cy + FINGER_T / 2.0
        p0, p1 = self.L_(x0, y0), self.L_(x1, y1)
        d.rounded_rectangle((p0[0], p0[1], p1[0], p1[1]), radius=FINGER_T / 2.0 * SS, fill=blend(FINGER, a))
        n0, n1 = self.L_(x1 - 14, y0 + 3), self.L_(x1 - 3, y1 - 3)
        d.rounded_rectangle((n0[0], n0[1], n1[0], n1[1]), radius=3 * SS, fill=blend(NAIL, a))
        if 0.0 <= tau - na < 0.3:
            b = 1.0 - (tau - na) / 0.3
            for ang in (-40, 0, 40):
                sx, cx_ = math.sin(ang * DEG), math.cos(ang * DEG)
                q0 = self.L_(left + 4 + 10 * sx, self.cy - 16 - 4 * cx_)
                q1 = self.L_(left + 4 + 20 * sx, self.cy - 16 - 14 * cx_)
                d.line((*q0, *q1), fill=blend(GOLD, b), width=2 * SS)

    def draw_inset(self, layer: Image.Image, m: str, st: dict) -> None:
        """The 10x cross-section: the camera follows the pencil's centre along the desk; desk ticks
        every millimetre scroll past; the hexagon's pivot corner in gold."""
        k = self.k
        sub = Image.new("RGB", (INSET_W * SS, INSET_H * SS), blend(WHITE, 0.03))
        d = ImageDraw.Draw(sub)
        desk_y = INSET_H - INSET_DESK
        cxw = st["x_m"]                                   # world x (m from the pencil's start) at the inset centre
        ccx = INSET_W / 2.0

        def X(xm: float) -> float:
            return ccx + (xm - cxw) * k

        L_ = self.L_
        edge_m = self.man["start_to_edge_m"]
        ex = X(edge_m) if m == "round" else 10_000.0
        if ex > -5:
            d.rectangle((*L_(-5, desk_y), *L_(min(ex, INSET_W + 5), INSET_H + 5)), fill=DECK_A)
            d.line((*L_(-5, desk_y), *L_(min(ex, INSET_W + 5), desk_y)), fill=DECK_B, width=3 * SS)
        j0 = math.floor((cxw - INSET_W / 2.0 / k) * 1000) - 1
        for j in range(j0, j0 + int(INSET_W / k * 1000) + 3):
            xx = X(j / 1000.0)
            if xx < ex - 2:
                d.line((*L_(xx, desk_y + 3), *L_(xx, desk_y + (10 if j % 5 == 0 else 6))), fill=RIM, width=SS)
        if -5 < ex < INSET_W + 5:
            d.line((*L_(ex - 1, desk_y + 2), *L_(ex - 1, INSET_H + 5)), fill=RIM, width=2 * SS)
        if m == "round":
            cyy = desk_y - (self.r - st["drop_m"]) * k
            self.draw_pencil(d, m, ccx, cyy, k, st["theta"], lw=3.0)
        else:
            cyy = desk_y - st["h_m"] * k
            pv = None
            if st["pivot_m"] is not None:
                pv = (X(st["pivot_m"]), desk_y)
            self.draw_pencil(d, m, ccx, cyy, k, st["theta"], pivot_xy=pv, lw=3.0)
        d.text(L_(10, 8), inset_label(self.man), font=self.font_inset,
               fill=MUTED, anchor="la")
        mask = Image.new("L", sub.size, 0)
        ImageDraw.Draw(mask).rounded_rectangle((0, 0, sub.size[0] - 1, sub.size[1] - 1), radius=8 * SS, fill=255)
        layer.paste(sub, (INSET_X0 * SS, INSET_Y0 * SS), mask)
        ImageDraw.Draw(layer).rounded_rectangle((INSET_X0 * SS, INSET_Y0 * SS, (INSET_X0 + INSET_W) * SS - 1,
                                                 (INSET_Y0 + INSET_H) * SS - 1), radius=8 * SS,
                                                outline=blend(MUTED, 0.35), width=SS)

    def scene(self, m: str, tau: float) -> tuple[Image.Image, dict]:
        layer = Image.new("RGB", (W * SS, BAND_H * SS), BG)
        d = ImageDraw.Draw(layer)
        self.draw_desk(d)
        tv = tau - self.na
        rt = tv / self.S
        ppm = self.ppm
        if m == "round":
            s = round_state(self.ev, self.man, rt)
            cx, cy = self.x0 + s["x"] * ppm, self.cy + s["drop"] * ppm
            # Trail of the centre.
            if rt > 0.0:
                xe = min(cx, self.edge)
                d.line((*self.L_(self.x0, self.cy), *self.L_(xe, self.cy)), fill=blend(CORAL, 0.35), width=SS)
                if s["off"]:
                    pts = []
                    u_end = rt - self.ev["t_edge"]
                    for i in range(41):
                        u = u_end * i / 40
                        pts.append(self.L_(self.edge + self.man["nudge_speed_m_s"] * u * ppm,
                                           self.cy + 0.5 * self.man["g"] * u * u * ppm))
                    d.line(pts, fill=blend(CORAL, 0.35), width=SS)
            self.draw_pencil(d, m, cx, cy, ppm, s["theta"])
            st = {"x_m": s["x"], "drop_m": s["drop"], "theta": s["theta"], "v": s["v"], "off": s["off"],
                  "floor": s["floor"], "rolled": min(s["x"], self.man["start_to_edge_m"])}
        else:
            s = hex_state(self.ev, self.man, rt)
            cx = self.x0 + s["x"] * ppm
            cy = self.top - s["h"] * ppm
            if rt > 0.0:
                pts = [self.L_(self.x0 + q["x"] * ppm, self.top - q["h"] * ppm) for t, q in self.hex_path if t <= rt]
                pts.append(self.L_(cx, cy))
                if len(pts) >= 2:
                    d.line(pts, fill=blend(TEAL, 0.45), width=SS)
            self.draw_pencil(d, m, cx, cy, ppm, s["theta"])
            st = {"x_m": s["x"], "h_m": s["h"], "theta": s["theta"], "v": abs(s["w"]) * self.R, "pivot_m": s["pivot"],
                  "stopped": s["stopped"], "rolled": s["x"]}
        self.draw_finger(d, tau)
        self.draw_inset(layer, m, st)
        st["tv"], st["rt"] = tv, rt
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

    def draw_text(self, d: ImageDraw.ImageDraw, states: dict, hud_alpha: float) -> None:
        man, ev = self.man, self.ev
        for m, st in states.items():
            y0 = BAND_Y[m]
            a = st["alpha"]
            d.text((ROW_X0, y0 + LABEL_DY), label_text(m), font=self.font, fill=COLOUR[m], anchor="lm")
            d.text((ROW_X0, y0 + SUB_DY), sub_text(), font=self.font_small, fill=MUTED, anchor="lm")
            if m == "round" and st["floor"]:
                d.text((ROW_X0, y0 + FIX_DY), floor_text(), font=self.font_small, fill=blend(TEXT, a), anchor="lm")
            else:
                d.text((ROW_X0, y0 + FIX_DY), speed_text(st["v"]), font=self.font_small, fill=blend(TEXT, a), anchor="lm")
            lit = st["off"] if m == "round" else st["stopped"]
            d.text((ROW_X1, y0 + LABEL_DY), rolled_text(st["rolled"]), font=self.font_small,
                   fill=blend(GOLD if lit else TEXT, a), anchor="rm")
            if lit:
                d.text((ROW_X0, y0 + EVENT_DY), event_text(ev, m), font=self.font_event, fill=blend(GOLD, a), anchor="lm")
        if hud_alpha > 0.02:
            d.text((W / 2, LEGEND_Y), legend_text(man), font=self.font, fill=blend(TEXT, hud_alpha), anchor="mm")
            d.text((W / 2, CLOCK_Y), clock_text(states["round"]["rt"]), font=self.font_small,
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
    man = json.loads((ROOT / "projects/pencil/manifest.json").read_text())
    ev = measure(man)
    if "--measure-only" in sys.argv:
        return
    if "--frames" in sys.argv:
        times = [float(v) for v in sys.argv[sys.argv.index("--frames") + 1].split(",")]
        r = Renderer(man, ev)
        (ROOT / "media/pencil").mkdir(parents=True, exist_ok=True)
        for tv in times:
            Image.fromarray(r.frame_at(int(round(tv * man["fps"])))).save(ROOT / f"media/pencil/smoke-{tv}.png")
        print("smoke frames: " + ", ".join(f"{tv}" for tv in times))
        return
    Renderer(man, ev).render(ROOT / "media/pencil/footage.mp4")


if __name__ == "__main__":
    main()
