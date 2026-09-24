#!/usr/bin/env python3
"""Superball under a table: throw a bouncy ball under a table. So where does it go?

Two balls of radius R are released at the same point (centre release_height_m
above the floor, release_x_m from the hand) with the same velocity (throw_vx
forward, throw_vy down) under a table whose underside is table_height_m above
the floor and spans table_x0_m to table_x1_m. The top ball is rough and
perfectly elastic (Garwin 1969, a solid rubber ball, I = alpha m R^2 with
alpha = 2/5, no air): at every bounce the normal velocity reverses, the
velocity of the contact point along the surface reverses, and the angular
momentum about the contact point is conserved. The map from (vx, R omega)
before the bounce to after it is solved from those two rules as a 2 x 2
linear system in bounce_matrix(); nothing is hard-coded, and the sim asserts
that vx^2 + alpha (R omega)^2 is conserved at every bounce. The bottom ball
is smooth and perfectly elastic: the normal velocity reverses and nothing
else changes. Flights are exact parabolas; the bounce instants are the roots
of quadratics (event driven, no time step). The rough ball's run ends when
it rises back through the release height moving backward (the catch); the
smooth ball's run ends when it leaves the frame on the far side. Played at
playback speed (1/5), the throw repeats every throw_period seconds with a
reset to the hand so the video loops. Deterministic, no seed.

Measured and printed: the bounce map of each surface and its check against
the closed-form fractions, every bounce (time, x, vx, vy, R omega before and
after, spin in turns per second), the horizontal-plus-spin energy and the
total energy after each bounce, the product of the three bounce maps, the
point and velocity where the rough ball crosses the release height on the
way back and its share of the throw speed, the smooth ball's third bounce,
its passage under the far edge of the table and its exit from the frame, the
table length decision, the schedule in video time and the on-screen text
widths.

usage: superball.py [--measure-only] [--frames t1,t2,...]
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
TEXT = (216, 222, 230)
MUTED = (138, 148, 163)
WHITE = (236, 240, 244)
WIRE = (70, 80, 94)
SLAB = (58, 66, 78)
SLAB_TOP = (96, 108, 124)
GROUND = (26, 31, 39)
HAND = (176, 156, 140)

# Layout: overlay at y 96..130 (captions.py), three title rows at y 190/252/314
# for the first seconds, then the throw counter at y 236 and the model tag at
# y 290; two panels at the same scale, each with a label row (label at 32 px,
# the clock at 40 px right-aligned) and a readout row at 28 px above the
# table slab, the table underside 0.70 m above the floor line; the rough
# ball's panel has its floor at y 830 and the smooth ball's at y 1365; bounce
# numbers sit just under each floor line; captions at caption_y 0.75 (y
# 1440..1520); the payoff card from y 1592.
COUNTER_Y, TAG_Y = 236, 290
GEOM_Y0, GEOM_Y1 = 360, 1400
SS = 2
PAYOFF_Y = 1592.0
PANELS = {
    "rough": {"colour": GOLD, "label": "rough ball (grips)", "label_y": 400, "floor_y": 830.0},
    "smooth": {"colour": TEAL, "label": "smooth ball (slides)", "label_y": 935, "floor_y": 1365.0},
}
READ_X0, READ_X1 = 60, 1020
READ_COLS = (60, 330, 650)


def blend(col, a: float, base=BG) -> tuple:
    return tuple(int(round(c * a + b * (1 - a))) for c, b in zip(col, base))


def lighten(col, a: float) -> tuple:
    return blend(WHITE, a, col)


def smoothstep(u: float) -> float:
    u = max(0.0, min(1.0, u))
    return u * u * (3 - 2 * u)


# --- the bounce maps -----------------------------------------------------------
def bounce_matrix(alpha: float, side: int) -> np.ndarray:
    """The rough-ball bounce as a matrix on (vx, R omega), solved from the two rules.

    x forward, y up, omega counterclockwise; side = -1 for a contact below the
    centre (the floor), +1 for a contact above it (the table underside). The
    contact point moves along the surface at u = vx - side R omega; its
    velocity reverses (u' = -u). The angular momentum about the contact point,
    m R (side vx + alpha R omega), is conserved. Two linear equations in the
    two unknowns (vx', R omega'), solved numerically: A [vx'; a'] = B [vx; a].
    """
    A = np.array([[1.0, -side], [side, alpha]])
    B = np.array([[-1.0, side], [side, alpha]])
    return np.linalg.solve(A, B)


def apply_bounce(man: dict, rough: bool, side: int, vx: float, vy: float, a: float) -> tuple[float, float, float]:
    """Velocity after a bounce: the normal velocity reverses; a rough ball also maps (vx, R omega)."""
    if not rough:
        return vx, -vy, a
    M = bounce_matrix(float(man["alpha"]), side)
    vx2, a2 = (M @ np.array([vx, a])).tolist()
    e0, e1 = vx * vx + man["alpha"] * a * a, vx2 * vx2 + man["alpha"] * a2 * a2
    assert abs(e1 - e0) < 1e-9 * max(1.0, e0), f"the bounce map does not conserve energy: {e0} -> {e1}"
    return vx2, -vy, a2


# --- the event-driven flight ----------------------------------------------------
def frame_right_m(man: dict) -> float:
    """The x (metres) of the right edge of the frame at the panel scale."""
    ppm = float(man["px_per_m"])
    margin = (W - (man["view_x1_m"] - man["view_x0_m"]) * ppm) / 2.0
    return man["view_x1_m"] + margin / ppm


def simulate(man: dict, rough: bool) -> dict:
    """Exact parabolas between events; the events are floor, table, catch (rough), exit (frame) or end."""
    g, R, alpha = float(man["g"]), float(man["ball_radius_m"]), float(man["alpha"])
    y_floor, y_table = R, man["table_height_m"] - R
    yr = float(man["release_height_m"])
    x_exit = frame_right_m(man) + R
    x, y = float(man["release_x_m"]), yr
    vx, vy, a, phi, t = float(man["throw_vx_m_s"]), float(man["throw_vy_m_s"]), 0.0, 0.0, 0.0
    segs, events = [], []
    while True:
        cands = []
        # The floor: the positive root of y + vy t - g t^2 / 2 = R.
        disc = vy * vy + 2.0 * g * (y - y_floor)
        tf = (vy + math.sqrt(max(disc, 0.0))) / g
        if tf > 1e-12:
            cands.append((tf, "floor"))
        # The table underside: the first root of y + vy t - g t^2 / 2 = table height - R, if the
        # ball rises that high and is under the table there.
        if vy > 0.0:
            disc = vy * vy - 2.0 * g * (y_table - y)
            if disc >= 0.0:
                tt = (vy - math.sqrt(disc)) / g
                if tt > 1e-12 and man["table_x0_m"] <= x + vx * tt <= man["table_x1_m"]:
                    cands.append((tt, "table"))
        # The catch: the rough ball rising back through the release height while moving backward.
        if rough and vx < 0.0 and vy > 0.0 and y < yr:
            disc = vy * vy - 2.0 * g * (yr - y)
            if disc >= 0.0:
                cands.append(((vy - math.sqrt(disc)) / g, "catch"))
        # The frame edge on the far side.
        if vx > 0.0 and x < x_exit:
            cands.append(((x_exit - x) / vx, "exit"))
        cands.append((man["max_time_s"] - t, "end"))
        dt, kind = min(cands, key=lambda c: c[0])
        x1, y1 = x + vx * dt, y + vy * dt - 0.5 * g * dt * dt
        vy1 = vy - g * dt
        seg = {"t0": t, "x0": x, "y0": y, "vx": vx, "vy0": vy, "a": a, "phi0": phi, "dur": dt, "t1": t + dt,
               "x1": x1, "y1": y1, "vy1": vy1, "end": kind}
        segs.append(seg)
        phi += a / R * dt
        x, y, vy, t = x1, y1, vy1, t + dt
        if kind in ("floor", "table"):
            side = -1 if kind == "floor" else 1
            vx2, vy2, a2 = apply_bounce(man, rough, side, vx, vy, a)
            u_in = vx - side * a
            u_out = vx2 - side * a2
            events.append({"n": len(events) + 1, "kind": kind, "t": t, "x": x, "y": y,
                           "vx_in": vx, "vy_in": vy, "a_in": a, "vx_out": vx2, "vy_out": vy2, "a_out": a2,
                           "u_in": u_in, "u_out": u_out,
                           "E_hs": 0.5 * (vx2 * vx2 + alpha * a2 * a2),
                           "E_tot": 0.5 * (vx2 * vx2 + vy2 * vy2) + 0.5 * alpha * a2 * a2 + g * y,
                           "residual": y - (y_floor if kind == "floor" else y_table)})
            vx, vy, a = vx2, vy2, a2
            continue
        end_state = {"t": t, "x": x, "y": y, "vx": vx, "vy": vy, "a": a, "phi": phi, "kind": kind}
        return {"segs": segs, "events": events, "t_end": t, "end": end_state, "rough": rough}


def state_at(man: dict, run: dict, tp: float) -> dict:
    """The ball at real time tp (held at its end state after the run ends)."""
    g, R = float(man["g"]), float(man["ball_radius_m"])
    if tp >= run["t_end"]:
        e = run["end"]
        st = dict(e)
        st.update({"held": True, "bounces": len(run["events"])})
    else:
        seg = run["segs"][-1]
        for s in run["segs"]:
            if tp < s["t1"]:
                seg = s
                break
        dt = tp - seg["t0"]
        st = {"t": tp, "x": seg["x0"] + seg["vx"] * dt, "y": seg["y0"] + seg["vy0"] * dt - 0.5 * g * dt * dt,
              "vx": seg["vx"], "vy": seg["vy0"] - g * dt, "a": seg["a"], "phi": seg["phi0"] + seg["a"] / R * dt,
              "held": False, "bounces": sum(1 for e in run["events"] if e["t"] <= tp)}
    st["speed"] = math.hypot(st["vx"], st["vy"])
    st["turns_per_s"] = st["a"] / R / (2.0 * math.pi)
    return st


# --- measurement ----------------------------------------------------------------
def measure(man: dict) -> dict:
    g, R, alpha = float(man["g"]), float(man["ball_radius_m"]), float(man["alpha"])
    vx0, vy0, yr = float(man["throw_vx_m_s"]), float(man["throw_vy_m_s"]), float(man["release_height_m"])
    pb, P, fps = float(man["playback"]), float(man["throw_period"]), man["fps"]
    v_throw = math.hypot(vx0, vy0)
    ppm = float(man["px_per_m"])
    print(f"setup: two balls of radius {R * 100:g} cm released at the same point (centre {yr:g} m above the floor, "
          f"x = {man['release_x_m']:g} m at the hand) with the same velocity, {vx0:g} m/s forward and {-vy0:g} m/s "
          f"down ({v_throw:.4f} m/s), under a table whose underside is {man['table_height_m']:g} m above the floor "
          f"({man['table_thickness_m'] * 100:g} cm thick) and spans x = {man['table_x0_m']:g} to {man['table_x1_m']:g} "
          f"m; the top ball is rough and perfectly elastic (Garwin: the normal velocity reverses, the contact-point "
          f"velocity along the surface reverses, the angular momentum about the contact point is conserved, I = alpha "
          f"m R^2 with alpha = {alpha:g}, no air); the bottom ball is smooth and perfectly elastic (no spin change); "
          f"flights are exact parabolas with the bounce instants solved as quadratic roots (event driven, no time "
          f"step); g = {g}; played at 1/{1 / pb:g} speed, {man['throws']} throws of {P:g} s; drawn at {ppm:g} px per "
          f"metre from x = {man['view_x0_m']:g} to {man['view_x1_m']:g} m (frame edge at {frame_right_m(man):.4f} m), "
          f"ball radius {R * ppm:.1f} px; deterministic, no seed")
    Mf, Mt = bounce_matrix(alpha, -1), bounce_matrix(alpha, +1)
    Mf_ref = np.array([[3.0, -4.0], [-10.0, -3.0]]) / 7.0
    Mt_ref = np.array([[3.0, 4.0], [10.0, -3.0]]) / 7.0
    print(f"bounce map (solved from the two rules, alpha = {alpha:g}): floor (contact below) vx' = {Mf[0, 0]:.6f} vx + "
          f"{Mf[0, 1]:.6f} R omega, R omega' = {Mf[1, 0]:.6f} vx + {Mf[1, 1]:.6f} R omega; table underside (contact "
          f"above) vx' = {Mt[0, 0]:.6f} vx + {Mt[0, 1]:.6f} R omega, R omega' = {Mt[1, 0]:.6f} vx + {Mt[1, 1]:.6f} R "
          f"omega; against the closed-form fractions (3, -4; -10, -3) / 7 and (3, 4; 10, -3) / 7 max difference "
          f"{max(np.abs(Mf - Mf_ref).max(), np.abs(Mt - Mt_ref).max()):.1e}; each map conserves vx^2 + alpha (R omega)^2 "
          f"(checked at every bounce below)")
    runs = {"rough": simulate(man, True), "smooth": simulate(man, False)}
    for name in PANELS:
        run = runs[name]
        lines = []
        for e in run["events"]:
            lines.append(f"bounce {e['n']} ({e['kind']}) at t = {e['t']:.4f} s, x = {e['x']:.4f} m (residual "
                         f"{e['residual']:.1e} m): vx {e['vx_in']:.4f} -> {e['vx_out']:.4f} m/s, vy {e['vy_in']:.4f} -> "
                         f"{e['vy_out']:.4f} m/s, R omega {e['a_in']:.4f} -> {e['a_out']:.4f} m/s ({e['a_out'] / R / (2 * math.pi):.2f} "
                         f"turns/s), contact-point speed along the surface {e['u_in']:.4f} -> {e['u_out']:.4f} m/s; "
                         f"energy after: horizontal plus spin (vx^2 + alpha (R omega)^2) / 2 = {e['E_hs']:.4f} J/kg, "
                         f"total {e['E_tot']:.4f} J/kg")
        e = run["end"]
        print(f"{name} ball ({len(run['events'])} bounces, ends by {e['kind']} at t = {e['t']:.4f} s): " + "; ".join(lines))
        E0_hs = 0.5 * vx0 * vx0
        E0 = 0.5 * (vx0 * vx0 + vy0 * vy0) + g * yr
        dev_hs = max(abs(ev["E_hs"] - E0_hs) for ev in run["events"])
        dev = max(abs(ev["E_tot"] - E0) for ev in run["events"])
        print(f"{name} ball energy: horizontal plus spin {E0_hs:.4f} J/kg at the throw, max deviation over the bounces "
              f"{dev_hs:.1e}; total {E0:.4f} J/kg, max deviation {dev:.1e}")
    Rg = runs["rough"]
    kinds = [e["kind"] for e in Rg["events"]]
    assert kinds == ["floor", "table", "floor"], kinds
    assert Rg["end"]["kind"] == "catch", Rg["end"]["kind"]
    prod = Mf @ Mt @ Mf
    v_after = prod @ np.array([vx0, 0.0])
    print(f"product of the three maps (floor, table, floor) on (vx, R omega): [[{prod[0, 0]:.6f}, {prod[0, 1]:.6f}], "
          f"[{prod[1, 0]:.6f}, {prod[1, 1]:.6f}]] = (1/343) [[{prod[0, 0] * 343:.1f}, {prod[0, 1] * 343:.1f}], "
          f"[{prod[1, 0] * 343:.1f}, {prod[1, 1] * 343:.1f}]]; applied to the throw ({vx0:g}, 0): vx {v_after[0]:.4f} m/s, "
          f"R omega {v_after[1]:.4f} m/s (the third bounce above: {Rg['events'][-1]['vx_out']:.4f}, "
          f"{Rg['events'][-1]['a_out']:.4f}); |vx| share {abs(prod[0, 0]) * 100:.2f} percent")
    c = Rg["end"]
    share_vx = abs(c["vx"]) / vx0
    share_v = math.hypot(c["vx"], c["vy"]) / v_throw
    print(f"return: the rough ball rises back through the release height {yr:g} m at t = {c['t']:.4f} s, x = {c['x']:.4f} m "
          f"({-c['x'] * 100:.1f} cm behind the hand), moving backward at {-c['vx']:.4f} m/s and up at {c['vy']:.4f} m/s "
          f"(full speed {math.hypot(c['vx'], c['vy']):.4f} m/s); backward speed {share_vx * 100:.2f} percent of the "
          f"{vx0:g} m/s forward throw speed, full speed {share_v * 100:.2f} percent of the {v_throw:.4f} m/s throw "
          f"speed; spin at the catch {c['a']:.4f} m/s = {c['turns_per_s'] if 'turns_per_s' in c else c['a'] / R / (2 * math.pi):.2f} turns/s; "
          f"it comes back to the hand")
    # What the rough ball would do without the catch.
    e3 = Rg["events"][-1]
    disc = e3["vy_out"] ** 2 - 2.0 * g * (man["table_height_m"] - R - e3["y"])
    tt = (e3["vy_out"] - math.sqrt(disc)) / g
    x_tt = e3["x"] + e3["vx_out"] * tt
    apex = e3["y"] + e3["vy_out"] ** 2 / (2.0 * g)
    print(f"without the catch the rough ball would reach the table underside height at t = {e3['t'] + tt:.4f} s, "
          f"x = {x_tt:.4f} m ({'under' if man['table_x0_m'] <= x_tt <= man['table_x1_m'] else 'outside'} the table, "
          f"near edge at {man['table_x0_m']:g} m), apex {apex:.4f} m; the catch at {c['t']:.4f} s comes first")
    Sm = runs["smooth"]
    assert [e["kind"] for e in Sm["events"]] == ["floor", "table", "floor"]
    s3 = Sm["events"][-1]
    assert s3["x"] > man["table_x1_m"], "the smooth ball's third bounce must be beyond the far edge of the table"
    # Passage under the far edge.
    seg_edge = next(s for s in Sm["segs"] if s["x0"] <= man["table_x1_m"] <= s["x1"])
    dte = (man["table_x1_m"] - seg_edge["x0"]) / seg_edge["vx"]
    y_edge = seg_edge["y0"] + seg_edge["vy0"] * dte - 0.5 * g * dte * dte
    se = Sm["end"]
    disc4 = s3["vy_out"] ** 2 - 2.0 * g * (man["table_height_m"] - R - s3["y"])
    t4 = (s3["vy_out"] - math.sqrt(disc4)) / g
    print(f"smooth ball: keeps vx = {s3['vx_out']:.4f} m/s through every bounce; third bounce at x = {s3['x']:.4f} m, "
          f"t = {s3['t']:.4f} s, {s3['x'] - man['table_x1_m']:.4f} m beyond the far edge of the table; passes under the "
          f"far edge (x = {man['table_x1_m']:g} m) at t = {seg_edge['t0'] + dte:.4f} s at a centre height of {y_edge:.4f} m; "
          f"leaves the frame (x = {se['x']:.4f} m) at t = {se['t']:.4f} s at a height of {se['y']:.4f} m rising at "
          f"{se['vy']:.4f} m/s, speed {math.hypot(se['vx'], se['vy']):.4f} m/s; without the frame edge its next table-height "
          f"crossing would be at x = {s3['x'] + s3['vx_out'] * t4:.4f} m (no table there), apex {s3['y'] + s3['vy_out'] ** 2 / (2 * g):.4f} m")
    print(f"table length: {man['table_x0_m']:g} to {man['table_x1_m']:g} m ({man['table_x1_m'] - man['table_x0_m']:g} m); "
          f"the rough ball's bounces at x = " + ", ".join(f"{e['x']:.4f}" for e in Rg["events"]) + " m and the smooth "
          f"ball's table bounce at x = {Sm['events'][1]['x']:.4f} m are under it; the smooth ball's third bounce at "
          f"{s3['x']:.4f} m is beyond the far edge, so it leaves the far side; the rough ball's would-be next table "
          f"crossing at {x_tt:.4f} m is behind the near edge and after the catch")
    # Schedule.
    rel, reach, reset, rest = man["release_at"], man["reach_dur"], man["reset_dur"], man["rest_dur"]
    t_catch_v, t_exit_v = c["t"] / pb, se["t"] / pb
    hold = P - reset - rest - rel - t_catch_v
    assert hold > 0.0, "the throw period is too short"
    assert rest >= man["loop_fade"], "the loop fade must play over balls at rest"
    assert abs(man["throws"] * P - man["scene_duration"]) < 1e-9
    assert abs(man["scene_duration"] - round(man["scene_duration"])) < 1e-9
    bounces_v = ", ".join(f"{e['t'] / pb:.2f}" for e in Rg["events"])
    print(f"schedule (video time, 1/{1 / pb:g} speed): each {P:g} s throw releases both balls at {rel:g} s; the rough ball "
          f"bounces {bounces_v} s after the release, the hand reaches from {t_catch_v - reach:.2f} s and the ball is "
          f"caught {t_catch_v:.2f} s after the release; the smooth ball bounces "
          + ", ".join(f"{e['t'] / pb:.2f}" for e in Sm["events"]) + f" s after and leaves the frame {t_exit_v:.2f} s after; "
          f"held for {hold:.2f} s, then a {reset:g} s reset to the hand and {rest:g} s at rest; catches at "
          + ", ".join(f"{i * P + rel + t_catch_v:.2f}" for i in range(man["throws"])) + " s; exits at "
          + ", ".join(f"{i * P + rel + t_exit_v:.2f}" for i in range(man["throws"])) + f" s; title until "
          f"{man['title_until']:g} s; payoff card from {man['payoff_t']:g} s; loop fade "
          f"{man['scene_duration'] - man['loop_fade']:.1f} to {man['scene_duration']:g} s")
    ev = {"runs": runs, "share_vx": share_vx, "share_v": share_v, "catch": c, "exit": se}
    # Text widths.
    font = os.environ["SEED_ZERO_FONT"]
    f24, f28, f32, f34, f40, f56 = (ImageFont.truetype(font, n) for n in (24, 28, 32, 34, 40, 56))
    widths = {"overlay@34": (f34, man["overlay"])}
    for j, line in enumerate(man["title"].split("|")):
        widths[f"title line {j + 1}@56"] = (f56, line)
    widths["counter@40"] = (f40, f"throw {man['throws']} of {man['throws']}")
    widths["tag@28"] = (f28, model_tag(man))
    for name in PANELS:
        widths[f"label {name}@32"] = (f32, PANELS[name]["label"])
    widths["clock@40"] = (f40, "t 0.79 s")
    widths["caught tag@32"] = (f32, "caught")
    widths["gone tag@32"] = (f32, "gone")
    widths["x readout@28"] = (f28, x_text(-0.13))
    widths["speed readout@28"] = (f28, speed_text(4.45))
    widths["spin readout@28"] = (f28, spin_text(-18.95))
    widths["readout row@28"] = (f28, x_text(-0.13) + "    " + speed_text(4.45) + "    " + spin_text(-18.95))
    widths["hand@24"] = (f24, "hand")
    widths["table@24"] = (f24, "table")
    widths["floor@24"] = (f24, "floor")
    widths["bounce number@24"] = (f24, "3")
    for j, line in enumerate(catch_lines(c)):
        widths[f"catch tag line {j + 1}@28"] = (f28, line)
    widths["exit tag@28"] = (f28, "out the far side")
    for j, line in enumerate(payoff_lines(man, ev)):
        widths[f"payoff line {j + 1}@40"] = (f40, line)
    print("text widths: " + ", ".join(f"{k} {f.getlength(s):.0f} px" for k, (f, s) in widths.items()))
    assert all(f.getlength(s) < 950 for f, s in widths.values()), "a text line is too wide"
    return ev


def model_tag(man: dict) -> str:
    return "solid rubber ball, perfect bounces, no air"


def x_text(x: float) -> str:
    return f"x {x:.2f} m"


def speed_text(v: float) -> str:
    return f"speed {v:.2f} m/s"


def spin_text(turns: float) -> str:
    return f"spin {abs(turns):.1f} turns/s"


def catch_lines(c: dict) -> list[str]:
    return ["back at the hand", f"{-c['x'] * 100:.0f} cm behind"]


def payoff_lines(man: dict, ev: dict) -> list[str]:
    text = man["payoff_text"].format(share=ev["share_vx"] * 100.0, behind=-ev["catch"]["x"] * 100.0)
    return [s.strip() for s in text.split("|")]


# --- rendering -----------------------------------------------------------------
class Renderer:
    def __init__(self, man: dict, ev: dict):
        self.man, self.ev = man, ev
        self.fps = man["fps"]
        font = os.environ["SEED_ZERO_FONT"]
        self.font = ImageFont.truetype(font, 40)
        self.font_title = ImageFont.truetype(font, 56)
        self.font_small = ImageFont.truetype(font, 28)
        self.font_label = ImageFont.truetype(font, 32)
        self.font_tiny = ImageFont.truetype(font, 24)
        self.ppm = float(man["px_per_m"])
        self.R = float(man["ball_radius_m"])
        self.r_px = self.R * self.ppm
        self.x_origin = W / 2.0 - 0.5 * (man["view_x0_m"] + man["view_x1_m"]) * self.ppm
        self.pb = float(man["playback"])
        self.first = None
        # Path samples per panel: one per video frame plus the exact event points.
        self.paths = {}
        for name in PANELS:
            run = ev["runs"][name]
            n = int(math.ceil(run["t_end"] / self.pb * self.fps)) + 1
            times = [j / self.fps * self.pb for j in range(n)] + [e["t"] for e in run["events"]] + [run["t_end"]]
            times = sorted(t for t in set(times) if t <= run["t_end"])
            pts = []
            for tp in times:
                st = state_at(man, run, tp)
                pts.append((tp, st["x"], st["y"]))
            self.paths[name] = pts

    # --- geometry helpers ----------------------------------------------------
    def px(self, x: float, y: float, name: str) -> tuple[float, float]:
        return self.x_origin + x * self.ppm, PANELS[name]["floor_y"] - y * self.ppm

    def L(self, x: float, y: float, name: str) -> tuple[float, float]:
        X, Y = self.px(x, y, name)
        return X * SS, (Y - GEOM_Y0) * SS

    def throw_state(self, t: float) -> tuple[int, float, float, float]:
        """Video time -> (throw index, seconds into the throw, physics time, reset fraction)."""
        man = self.man
        P = man["throw_period"]
        k = int(t // P)
        tau = t - k * P
        reset_start = P - man["reset_dur"] - man["rest_dur"]
        u = smoothstep((tau - reset_start) / man["reset_dur"]) if tau >= reset_start else 0.0
        tp = max(0.0, tau - man["release_at"]) * self.pb
        return k, tau, tp, u

    def hand_x(self, tau: float, u: float) -> float:
        """The hand: at the release point, reaching to the catch point just before the catch, back on the reset."""
        man = self.man
        c = self.ev["catch"]
        t_catch_v = man["release_at"] + c["t"] / self.pb
        if u > 0.0:
            return c["x"] * (1.0 - u)
        if tau < t_catch_v - man["reach_dur"]:
            return float(man["release_x_m"])
        return c["x"] * smoothstep((tau - (t_catch_v - man["reach_dur"])) / man["reach_dur"])

    # --- drawing -----------------------------------------------------------------
    def draw_ball(self, d: ImageDraw.ImageDraw, X: float, Y: float, phi: float, col, a: float = 1.0) -> None:
        """A two-tone ball: a half disc in a darker shade turned by phi (counterclockwise, y up)."""
        Rp = self.r_px * SS
        fill, dark = blend(col, a), blend(blend(col, 0.5), a)
        rim = blend(blend(col, 0.3), a)
        d.ellipse((X - Rp, Y - Rp, X + Rp, Y + Rp), fill=fill)
        deg = math.degrees(phi)
        d.pieslice((X - Rp, Y - Rp, X + Rp, Y + Rp), -deg - 180.0, -deg, fill=dark)
        d.ellipse((X - Rp, Y - Rp, X + Rp, Y + Rp), outline=rim, width=2 * SS)
        hr = Rp * 0.18
        hx, hy = X - Rp * 0.4, Y - Rp * 0.42
        d.ellipse((hx - hr, hy - hr, hx + hr, hy + hr), fill=blend(lighten(col, 0.6), a))

    def draw_hand(self, d: ImageDraw.ImageDraw, name: str, hx: float, a: float = 1.0) -> None:
        """An open hand behind the ball at the release height: a palm and a thumb over the ball."""
        man = self.man
        yr = man["release_height_m"]
        R = self.R
        col = blend(HAND, a)
        x1 = hx - R - 0.008
        x0 = x1 - 0.036
        p0, p1 = self.L(x0, yr + 0.055, name), self.L(x1, yr - 0.055, name)
        d.rounded_rectangle((p0[0], p0[1], p1[0], p1[1]), radius=6 * SS, fill=col)
        q0, q1 = self.L(x1 - 0.004, yr + 0.055, name), self.L(hx + 0.012, yr + 0.033, name)
        d.rounded_rectangle((q0[0], q0[1], q1[0], q1[1]), radius=5 * SS, fill=col)

    def draw_panel_geometry(self, d: ImageDraw.ImageDraw, name: str, st: dict, tau: float, u: float, hx: float) -> None:
        man, ev = self.man, self.ev
        col = PANELS[name]["colour"]
        run = ev["runs"][name]
        R = self.R
        x_left, x_right = -self.x_origin / self.ppm, (W - self.x_origin) / self.ppm
        # Floor: a line with a ground band under it.
        f0, f1 = self.L(x_left, 0.0, name), self.L(x_right, 0.0, name)
        d.rectangle((f0[0], f0[1], f1[0], f1[1] + 14 * SS), fill=GROUND)
        d.line((f0[0], f0[1], f1[0], f1[1]), fill=WIRE, width=3 * SS)
        # Table: legs behind, then the slab.
        th, tt = man["table_height_m"], man["table_thickness_m"]
        tx0, tx1 = max(man["table_x0_m"], x_left - 0.1), min(man["table_x1_m"], x_right + 0.1)
        for lx in (man["table_x0_m"] + 0.02, man["table_x1_m"] - 0.02):
            if x_left - 0.05 < lx < x_right + 0.05:
                l0, l1 = self.L(lx - 0.02, th, name), self.L(lx + 0.02, 0.0, name)
                d.rectangle((l0[0], l0[1], l1[0], l1[1]), fill=blend(SLAB, 0.55))
        s0, s1 = self.L(tx0, th + tt, name), self.L(tx1, th, name)
        d.rectangle((s0[0], s0[1], s1[0], s1[1]), fill=SLAB)
        d.line((s0[0], s0[1], s1[0], s0[1]), fill=SLAB_TOP, width=3 * SS)
        d.line((s0[0], s1[1], s1[0], s1[1]), fill=SLAB_TOP, width=2 * SS)
        # The path so far and the bounce marks, fading on the reset.
        pa = 1.0 - u
        tp = st["t"]
        pts = [(t_, x_, y_) for (t_, x_, y_) in self.paths[name] if t_ <= tp]
        if not st["held"]:
            pts.append((tp, st["x"], st["y"]))
        if pa > 0.0 and len(pts) > 1:
            for (t0, x0, y0), (t1, x1, y1) in zip(pts, pts[1:]):
                age = (tp - t1) / self.pb
                a = (0.9 if age < man["trail_seconds"] else 0.4) * pa
                d.line((*self.L(x0, y0, name), *self.L(x1, y1, name)), fill=blend(col, a), width=3 * SS)
        for e in run["events"]:
            if e["t"] > tp or pa <= 0.0:
                continue
            X, Y = self.L(e["x"], e["y"] + (-R if e["kind"] == "floor" else R), name)
            rr = 5 * SS
            d.ellipse((X - rr, Y - rr, X + rr, Y + rr), outline=blend(col, 0.9 * pa), width=2 * SS)
            age = (tp - e["t"]) / self.pb
            if u == 0.0 and 0.0 <= age < 0.4:
                q = age / 0.4
                rr = (10.0 + 34.0 * q) * SS
                d.ellipse((X - rr, Y - rr, X + rr, Y + rr), outline=blend(col, 1.0 - q), width=3 * SS)
        # The hand, then the ball.
        self.draw_hand(d, name, hx)
        if name == "rough":
            if st["held"]:
                bx, by = st["x"] * (1.0 - u), st["y"]
            else:
                bx, by = st["x"], st["y"]
            X, Y = self.L(bx, by, name)
            self.draw_ball(d, X, Y, st["phi"], col)
        else:
            if st["held"]:
                if u > 0.0:
                    X, Y = self.L(man["release_x_m"], man["release_height_m"], name)
                    self.draw_ball(d, X, Y, 0.0, col, u)
            else:
                X, Y = self.L(st["x"], st["y"], name)
                self.draw_ball(d, X, Y, st["phi"], col)

    def draw_panel_text(self, d: ImageDraw.ImageDraw, name: str, st: dict, u: float, hx: float) -> None:
        man, ev = self.man, self.ev
        col, ly = PANELS[name]["colour"], PANELS[name]["label_y"]
        run = ev["runs"][name]
        R = self.R
        d.text((READ_X0, ly), PANELS[name]["label"], font=self.font_label, fill=col, anchor="lm")
        # Fixed labels: hand, table, floor.
        hxp, hyp = self.px(hx - R - 0.026, man["release_height_m"] - 0.055, name)
        d.text((hxp, hyp + 20), "hand", font=self.font_tiny, fill=blend(MUTED, 0.9), anchor="mm")
        tx, ty = self.px(man["view_x0_m"] + 0.02, man["table_height_m"] + 0.5 * man["table_thickness_m"], name)
        d.text((tx, ty), "table", font=self.font_tiny, fill=blend(TEXT, 0.75), anchor="lm")
        fx, fy = self.px(man["view_x0_m"] + 0.02, 0.0, name)
        d.text((fx, fy + 20), "floor", font=self.font_tiny, fill=blend(MUTED, 0.9), anchor="lm")
        # Readouts: live, frozen at the end, fading to the throw values on the reset.
        if u < 0.5:
            a = 1.0 - 2.0 * u
            vals = (x_text(st["x"]), speed_text(st["speed"]), spin_text(st["turns_per_s"]))
            clock = f"t {st['t'] if not st['held'] else run['t_end']:.2f} s"
            if st["held"]:
                tag = "caught" if name == "rough" else "gone"
                d.text((READ_X1, ly), clock, font=self.font, fill=blend(col, a), anchor="rm")
                d.text((READ_X1 - self.font.getlength(clock) - 18, ly + 3), tag, font=self.font_label,
                       fill=blend(col, a), anchor="rm")
            else:
                d.text((READ_X1, ly), clock, font=self.font, fill=blend(TEXT, a), anchor="rm")
        else:
            a = 2.0 * u - 1.0
            v0 = math.hypot(man["throw_vx_m_s"], man["throw_vy_m_s"])
            vals = (x_text(0.0), speed_text(v0), spin_text(0.0))
            d.text((READ_X1, ly), "t 0.00 s", font=self.font, fill=blend(TEXT, a), anchor="rm")
        for cx, s in zip(READ_COLS, vals):
            d.text((cx, ly + 40), s, font=self.font_small, fill=blend(MUTED, a), anchor="lm")
        # Bounce numbers under the floor or under the table underside.
        pa = 1.0 - u
        for e in run["events"]:
            if e["t"] > st["t"] or pa <= 0.0:
                continue
            if e["kind"] == "floor":
                X, Y = self.px(e["x"], 0.0, name)
                d.text((X, Y + 20), str(e["n"]), font=self.font_tiny, fill=blend(col, 0.9 * pa), anchor="mm")
            else:
                X, Y = self.px(e["x"], man["table_height_m"], name)
                d.text((X, Y + 18), str(e["n"]), font=self.font_tiny, fill=blend(col, 0.9 * pa), anchor="mm")
        # End tags.
        if st["held"] and pa > 0.0:
            if name == "rough":
                # Above the hand, left of every path (the descent from bounce 2 stays right of x 0.45 m up there).
                for j, line in enumerate(catch_lines(ev["catch"])):
                    X, Y = self.px(man["view_x0_m"] + 0.11, 0.60 - 0.072 * j, name)
                    d.text((X, Y), line, font=self.font_small, fill=blend(col, pa), anchor="lm")
            else:
                X, Y = self.px(man["view_x1_m"], 0.56, name)
                d.text((X, Y), "out the far side", font=self.font_small, fill=blend(col, pa), anchor="rm")

    def live_frame(self, f: int) -> np.ndarray:
        man = self.man
        t = f / self.fps
        k, tau, tp, u = self.throw_state(t)
        title_on = t < man["title_until"]
        if title_on:
            title_alpha = 1.0 if t < man["title_until"] - 0.4 else (man["title_until"] - t) / 0.4
            hud_alpha = 0.0
        else:
            title_alpha = 0.0
            hud_alpha = min(1.0, (t - man["title_until"]) / 0.4)
        states = {name: state_at(man, self.ev["runs"][name], tp) for name in PANELS}
        hx = self.hand_x(tau, u)
        img = Image.new("RGB", (W, H), BG)
        layer = Image.new("RGB", (W * SS, (GEOM_Y1 - GEOM_Y0) * SS), BG)
        ld = ImageDraw.Draw(layer)
        for name in PANELS:
            self.draw_panel_geometry(ld, name, states[name], tau, u, hx if name == "rough" else man["release_x_m"])
        img.paste(layer.reduce(SS), (0, GEOM_Y0))
        d = ImageDraw.Draw(img)
        for name in PANELS:
            self.draw_panel_text(d, name, states[name], u, hx if name == "rough" else man["release_x_m"])
        if hud_alpha > 0.02:
            d.text((W / 2, COUNTER_Y), f"throw {k + 1} of {man['throws']}", font=self.font, fill=blend(TEXT, hud_alpha), anchor="mm")
            d.text((W / 2, TAG_Y), model_tag(man), font=self.font_small, fill=blend(MUTED, hud_alpha), anchor="mm")
        if title_on:
            for j, line in enumerate(man["title"].split("|")):
                d.text((W / 2, 190 + j * 62), line, font=self.font_title, fill=blend(TEXT, title_alpha), anchor="mm")
        if t >= man["payoff_t"]:
            a = min(1.0, (t - man["payoff_t"]) / man["payoff_hold"])
            for j, line in enumerate(payoff_lines(man, self.ev)):
                d.text((W / 2, PAYOFF_Y + j * 56), line, font=self.font, fill=blend(GOLD, a), anchor="mm")
        return np.asarray(img, dtype=np.float32)

    def frame_at(self, f: int) -> np.ndarray:
        man = self.man
        total = int(round(man["scene_duration"] * self.fps))
        live = self.live_frame(f)
        fade_frames = int(round(man["loop_fade"] * self.fps))
        if f >= total - fade_frames:
            if self.first is None:
                self.first = self.live_frame(0)
            a = (f - (total - fade_frames) + 1) / fade_frames
            live = live * (1 - a) + self.first * a
        return live.astype(np.uint8)

    def render(self, out_path: Path) -> None:
        global _RENDERER
        out_path.parent.mkdir(parents=True, exist_ok=True)
        total = int(round(self.man["scene_duration"] * self.fps))
        first = self.frame_at(0)
        last = self.frame_at(total - 1)
        diff = np.abs(first.astype(int) - last.astype(int))
        print(f"loop check: last frame differs from the first in {int((diff.max(axis=2) > 24).sum())} px "
              f"(max channel difference {int(diff.max())})")
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
    man = json.loads((ROOT / "projects/superball/manifest.json").read_text())
    ev = measure(man)
    if "--measure-only" in sys.argv:
        return
    if "--frames" in sys.argv:
        times = [float(v) for v in sys.argv[sys.argv.index("--frames") + 1].split(",")]
        r = Renderer(man, ev)
        (ROOT / "media/superball").mkdir(parents=True, exist_ok=True)
        for tv in times:
            Image.fromarray(r.frame_at(int(round(tv * man["fps"])))).save(ROOT / f"media/superball/smoke-{tv}.png")
        print("smoke frames: " + ", ".join(f"{tv}" for tv in times))
        return
    Renderer(man, ev).render(ROOT / "media/superball/footage.mp4")


if __name__ == "__main__":
    main()
