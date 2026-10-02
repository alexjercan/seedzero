#!/usr/bin/env python3
"""Bat sweet spot: where is the sweet spot on a bat?

Two panels on the same clock, the same ice seen from above, the same stick
and the same ball: a uniform stiff stick of length L and mass M lies at
rest on frictionless ice (no force in the plane before or after the hit,
so after the hit it moves as a free rigid body: its centre at a constant
velocity, a constant spin); a ball of mass m_b at v0 hits it square
(perpendicular to the stick) at a distance d from the handle end in an
instantaneous frictionless hit with restitution e. With r = d - L / 2 and
I = M L^2 / 12 the impulse is

    J = (1 + e) v0 / (1 / m_b + 1 / M + r^2 / I),

the centre moves at J / M along the ball's direction, the spin is J r / I,
the ball keeps v0 - J / m_b, and the handle end's velocity (positive along
the ball's direction) is

    v_handle = J / M - (J r / I)(L / 2) = (J / M)(4 - 6 d / L),

zero at d = 2 L / 3 exactly, for any ball, any speed and any restitution:
the centre of percussion of a uniform rod. Top panel: the hit at d = 2 L /
3. Bottom panel: the hit at the tip, d = L, where the handle end kicks
back at twice the centre's speed. After the hit the free motion is closed
form (no ODE): the centre at J / M, the angle J r t / I; the sweet hit's
handle end stands still at the instant and the spin then sweeps it along
a cycloid cusp; the tip hit's handle end jumps back and the spin brings
it round in a loop. The hit repeats every cycle_s seconds of video with a
crossfade back to the resting stick; the cycle divides the scene length,
so the scene is exactly periodic and the last frame equals the first.
Shown at 1/slow speed. Deterministic, no seed.

Measured and printed: for each hit the impulse, the centre's speed, the
spin, the ball's speed after and both ends' velocities by the impulse
arithmetic and by the closed form (J / M)(4 - 6 d / L), the momentum and
angular momentum balance and the energy lost against (1 - e^2) of the
relative-motion energy; a scan of the hit point in 1 cm steps with the
sign change of the handle end's velocity and the exact root; the other
hits, restitutions, speeds and ball masses for the description; the free
motion after each hit (the handle end's speed and displacement at set
times, the trail's shape, the times the centre and the stick leave the
band); the approach; a second-contact check; the schedule in video time;
the on-screen text widths and the layout clearances.

usage: sweetspot.py [--measure-only] [--frames t1,t2,...]
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
ICE = (16, 27, 39)
ICE_STREAK = (24, 38, 54)
ICE_EDGE = (44, 58, 76)
INK = (30, 36, 46)
BALL_RIM = (150, 160, 176)

# Layout: overlay at y 96..130 (captions.py), two title rows at y 190/252 for
# the first seconds, then the legend at y 236 and the shared clock at y 290;
# two panels stacked, the two-thirds hit in the band y 330..880 and the tip
# hit in y 880..1430, each drawn at 2x in its own ice layer (so a stick that
# leaves its band is clipped at the band); each band has its label row 40 px
# under the band top and its second row at 82 (left column from x 40, the
# ball readout to x 1040); the stick stands vertical at stick_x_px with its
# centre centre_dy under the band top, the handle end at the bottom inside a
# hand ring; the ball comes in from the right edge along the hit point's
# row; the gold event row at EVENT_DY under the band top; captions at
# caption_y 0.75 (y 1440..1530); the six-line card from y 1572 at a 48 px
# pitch.
LEGEND_Y, CLOCK_Y = 236, 290
SS = 2
PAYOFF_Y, PAYOFF_PITCH = 1572.0, 48
PANELS = ("sweet", "tip")
BAND_Y = {"sweet": 330, "tip": 880}
BAND_H = 550
LABEL_DY, SUB_DY = 40, 82
EVENT_DY = 518
ROW_X0, ROW_X1 = 40, 1040
BAR_R = 7.0
COLOUR = {"sweet": TEAL, "tip": CORAL}
BEFORE, AFTER = "before", "after"
STREAKS = ((60, 70, 420, 40), (520, 300, 980, 250), (120, 500, 700, 470), (760, 120, 1040, 100))


def blend(col, a: float, base=BG) -> tuple:
    a = max(0.0, min(1.0, a))
    return tuple(int(round(c * a + b * (1 - a))) for c, b in zip(col, base))


# --- measurement --------------------------------------------------------------
def hit(L: float, M: float, mb: float, v0: float, e: float, d: float) -> dict:
    """The instantaneous frictionless hit of a ball (mb, v0) square on a free uniform stick (L, M)
    at rest, d from the handle end, restitution e: the impulse and every velocity after it."""
    I = M * L * L / 12.0
    r = d - L / 2.0
    mu = 1.0 / (1.0 / mb + 1.0 / M + r * r / I)      # the effective mass at the contact
    J = (1.0 + e) * mu * v0
    Vc = J / M
    om = J * r / I
    vb = v0 - J / mb
    vh = Vc - om * L / 2.0                             # the handle end, positive along the ball's direction
    vt = Vc + om * L / 2.0                             # the tip end
    vh_closed = Vc * (4.0 - 6.0 * d / L)
    e_before = 0.5 * mb * v0 * v0
    e_after = 0.5 * mb * vb * vb + 0.5 * M * Vc * Vc + 0.5 * I * om * om
    return {"d": d, "r": r, "I": I, "mu": mu, "J": J, "Vc": Vc, "om": om, "vb": vb, "vh": vh, "vt": vt,
            "vh_closed": vh_closed, "e": e, "v0": v0, "mb": mb, "L": L, "M": M,
            "p_before": mb * v0, "p_after": mb * vb + M * Vc,
            "l_before": mb * v0 * r, "l_after": mb * vb * r + I * om,
            "e_before": e_before, "e_after": e_after, "lost": e_before - e_after,
            "lost_closed": 0.5 * (1.0 - e * e) * mu * v0 * v0}


def handle_motion(h: dict, t: float) -> tuple[float, float, float]:
    """(dx, dy, speed) of the handle end t s after the hit, in metres: dx positive back toward where
    the ball came from, dy positive toward the tip's side of the start; the free rigid motion."""
    half = h["L"] / 2.0
    phi = h["om"] * t
    dx = -h["Vc"] * t + half * math.sin(phi)
    dy = half * (1.0 - math.cos(phi))
    vx = -h["Vc"] + half * h["om"] * math.cos(phi)
    vy = half * h["om"] * math.sin(phi)
    return dx, dy, math.hypot(vx, vy)


def seg_dist(px: float, py: float, ax: float, ay: float, bx: float, by: float) -> float:
    vx, vy = bx - ax, by - ay
    ln2 = vx * vx + vy * vy
    s = max(0.0, min(1.0, ((px - ax) * vx + (py - ay) * vy) / ln2)) if ln2 > 0.0 else 0.0
    return math.hypot(px - (ax + s * vx), py - (ay + s * vy))


def measure(man: dict) -> dict:
    L, M, mb, v0, e = man["stick_length_m"], man["stick_mass_kg"], man["ball_mass_kg"], man["ball_speed_m_s"], man["restitution"]
    S, P, D, fps, F, ha = man["slow"], man["cycle_s"], man["scene_duration"], man["fps"], man["reset_fade"], man["hit_at"]
    cycles = D / P
    assert abs(cycles - round(cycles)) < 1e-9, "the cycle must divide the scene length"
    for key in ("cycle_s", "hit_at", "first_cycle_at", "reset_fade"):
        assert abs(man[key] * fps - round(man[key] * fps)) < 1e-9, f"{key} must be a whole number of frames"
    ppm = man["px_per_m"]
    xs, yc, br = float(man["stick_x_px"]), float(man["centre_dy"]), float(man["ball_radius_px"])
    half = L / 2.0 * ppm
    x_hit = xs + BAR_R + br
    I = M * L * L / 12.0
    print(f"setup: the same ice in both panels, seen from above: a uniform stiff stick of {L * 100:g} cm and {M:g} kg "
          f"lies at rest on frictionless ice (no force in the plane before or after the hit, so after the hit it "
          f"moves as a free rigid body: its centre at a constant velocity, a constant spin), I = M L^2 / 12 = "
          f"{I:.6f} kg m^2; a ball of {mb * 1000:g} g at {v0:g} m/s hits it square (perpendicular to the stick) at "
          f"a distance d from the handle end in an instantaneous frictionless hit with restitution e = {e:g} (a "
          f"chosen value for a ball on wood; the sweet spot is the same for any e); impulse J = (1 + e) v0 / (1 / "
          f"m_b + 1 / M + r^2 / I) with r = d - L / 2; top panel the hit at d = 2 L / 3 = "
          f"{man['hit_fraction']['sweet'] * L * 100:.2f} cm, bottom panel the hit at the tip, d = L = {L * 100:g} "
          f"cm; the free motion after the hit in closed form (no ODE); shown at 1/{S:g} speed on a {P:g} s cycle "
          f"({P * fps:.0f} frames) with the hit {ha:g} s into the cycle, {cycles:.0f} cycles in {D:g} s; drawn at "
          f"{ppm:g} px per metre (the stick {L * ppm:.0f} px, the ball a {2 * br:.0f} px disc); deterministic, no seed")
    hits = {m: hit(L, M, mb, v0, e, man["hit_fraction"][m] * L) for m in PANELS}
    names = {"sweet": "hit two thirds along (top panel)", "tip": "hit at the tip (bottom panel)"}
    for m in PANELS:
        h = hits[m]
        back = "back toward where the ball came from" if h["vh"] < -1e-9 else ("along the ball's direction" if h["vh"] > 1e-9 else "still")
        ball = f"bounces back at {-h['vb']:.3f} m/s" if h["vb"] < 0 else f"carries on at {h['vb']:.3f} m/s"
        print(f"{names[m]}: d = {h['d'] * 100:.3f} cm, r = d - L / 2 = {h['r'] * 100:.3f} cm, r^2 / I = {h['r'] ** 2 / I:.5f} "
              f"per kg, 1 / m_b + 1 / M + r^2 / I = {1 / mb + 1 / M + h['r'] ** 2 / I:.5f} per kg; impulse J = {h['J']:.4f} "
              f"N s; after the hit the centre moves at J / M = {h['Vc']:.3f} m/s along the ball's direction, the spin is "
              f"J r / I = {h['om']:.2f} rad/s, the ball {ball}; the handle end's velocity J / M - (J r / I)(L / 2) = "
              f"{h['vh']:+.4f} m/s = (J / M)(4 - 6 d / L) = {h['vh_closed']:+.4f} m/s (diff {h['vh'] - h['vh_closed']:+.1e}): "
              f"{abs(h['vh']):.3f} m/s {back}; the tip end {h['vt']:.2f} m/s; momentum before and after the hit "
              f"{h['p_before']:.6f} = {h['p_after']:.6f} kg m/s (diff {h['p_after'] - h['p_before']:+.1e}), angular momentum "
              f"about the stick's centre {h['l_before']:.6f} = {h['l_after']:.6f} kg m^2/s (diff {h['l_after'] - h['l_before']:+.1e}); "
              f"kinetic energy {h['e_before']:.3f} J before, {h['e_after']:.3f} J after: {h['lost']:.3f} J lost = "
              f"{h['lost'] / h['e_before'] * 100:.1f} percent, the closed form (1 - e^2) of the relative-motion energy "
              f"{h['lost_closed']:.3f} J (diff {h['lost'] - h['lost_closed']:+.1e})")
        assert abs(h["vh"] - h["vh_closed"]) < 1e-9 and abs(h["p_after"] - h["p_before"]) < 1e-12
        assert abs(h["l_after"] - h["l_before"]) < 1e-12 and abs(h["lost"] - h["lost_closed"]) < 1e-9
    hs, ht = hits["sweet"], hits["tip"]
    assert abs(hs["vh"]) < 1e-12, "the handle end moves at the two-thirds hit"
    assert abs(ht["vh"] + 2.0 * ht["Vc"]) < 1e-9, "the tip hit's handle end is not at twice the centre's speed"
    # The sweet spot: the root of 4 - 6 d / L and a scan of the hit point.
    root = 2.0 * L / 3.0
    step = man["scan_step_cm"] / 100.0
    n_scan = int(round(L / step))
    scan = [(k * step, hit(L, M, mb, v0, e, k * step)["vh"]) for k in range(n_scan + 1)]
    change = [(scan[k][0], scan[k + 1][0]) for k in range(n_scan) if scan[k][1] > 0.0 >= scan[k + 1][1]]
    assert len(change) == 1, "the handle end's velocity should change sign once along the stick"
    d_lo, d_hi = change[0]
    v_lo, v_hi = hit(L, M, mb, v0, e, d_lo)["vh"], hit(L, M, mb, v0, e, d_hi)["vh"]
    print(f"sweet spot: the handle end's velocity (J / M)(4 - 6 d / L) is zero at d = 2 L / 3 = {root * 100:.3f} cm for "
          f"any ball, any speed and any restitution (the centre of percussion of a uniform rod); the scan of d from 0 "
          f"to {L * 100:g} cm in {man['scan_step_cm']:g} cm steps changes sign once, between {d_lo * 100:.0f} cm "
          f"({v_lo:+.3f} m/s) and {d_hi * 100:.0f} cm ({v_hi:+.3f} m/s); at the root the handle end's velocity is "
          f"{hit(L, M, mb, v0, e, root)['vh']:+.1e} m/s; the handle end moves along the ball at a hit under "
          f"{root * 100:.1f} cm and back at a hit over it")
    # For the description: other hits and restitutions, and the root at other balls.
    descr = []
    others: dict = {}
    for dc in man["description_hits_cm"]:
        h = hit(L, M, mb, v0, e, dc / 100.0)
        others[dc] = h
        where = {0.0: "at the handle end itself", L * 100 / 2: "in the middle"}.get(dc, f"{dc:g} cm from the handle end")
        spin = "no spin" if abs(h["om"]) < 1e-12 else f"spin {h['om']:.2f} rad/s"
        descr.append(f"hit {where} ({dc:g} cm): J {h['J']:.3f} N s, centre {h['Vc']:.3f} m/s, {spin}, handle end "
                     f"{h['vh']:+.3f} m/s, tip end {h['vt']:+.3f} m/s, the ball {h['vb']:+.3f} m/s")
    h3 = hit(L, M, mb, v0, e, L / 3.0)
    others["third"] = h3
    descr.append(f"hit one third along ({L / 3 * 100:.3f} cm, the mirror of the sweet spot): J {h3['J']:.3f} N s, centre "
                 f"{h3['Vc']:.3f} m/s, spin {h3['om']:.2f} rad/s, handle end {h3['vh']:+.3f} m/s, tip end {h3['vt']:+.3f} "
                 f"m/s: the tip end stays still")
    for e2 in man["description_restitutions"]:
        h = hit(L, M, mb, v0, e2, L)
        others[f"e{e2:g}"] = h
        descr.append(f"tip hit with restitution {e2:g}: J {h['J']:.3f} N s, centre {h['Vc']:.3f} m/s, handle end "
                     f"{h['vh']:+.3f} m/s, the ball {h['vb']:+.3f} m/s")
    same = []
    for u in man["description_speeds_m_s"]:
        same.append(f"ball at {u:g} m/s: {hit(L, M, mb, u, e, root)['vh']:+.1e}")
    for m2 in man["description_ball_masses_kg"]:
        same.append(f"a {m2 * 1000:g} g ball: {hit(L, M, m2, v0, e, root)['vh']:+.1e}")
    for e2 in man["description_restitutions"]:
        same.append(f"restitution {e2:g}: {hit(L, M, mb, v0, e2, root)['vh']:+.1e}")
    print("for the description (velocities along the ball's direction, negative = back): " + "; ".join(descr)
          + "; the hit at the handle end is the mirror of the tip hit (the handle end takes the tip end's "
          f"{others[0.0]['vh']:.3f} m/s and the tip end goes back at {-others[0.0]['vt']:.3f} m/s); the handle end's "
          "velocity at the two-thirds hit stays zero with " + ", ".join(same) + " m/s")
    assert abs(others[0.0]["vh"] - ht["vt"]) < 1e-9 and abs(others[0.0]["vt"] - ht["vh"]) < 1e-9, "not the mirror"
    assert abs(h3["vt"]) < 1e-12 and abs(others[L * 100 / 2]["om"]) < 1e-12
    # The free motion after each hit: the handle end's trail.
    t_end = (P - ha) / S
    sp = "; ".join(f"{t * 1000:.0f} ms: {handle_motion(hs, t)[2]:.2f} m/s (2 (J / M) sin(omega t / 2) = "
                   f"{2 * hs['Vc'] * math.sin(hs['om'] * t / 2):.2f}), moved {math.hypot(*handle_motion(hs, t)[:2]) * 100:.1f} cm"
                   for t in man["handle_speed_times_s"])
    jp = "; ".join(f"{t * 1000:.0f} ms: {handle_motion(ht, t)[0] * 100:.1f} cm back, {handle_motion(ht, t)[2]:.2f} m/s"
                   for t in man["handle_jump_times_s"])
    t_turn = {m: 2.0 * math.pi / abs(hits[m]["om"]) for m in PANELS}
    t_cx = {m: xs / (hits[m]["Vc"] * ppm) for m in PANELS}
    t_out = {m: (xs + half + BAR_R) / (hits[m]["Vc"] * ppm) for m in PANELS}
    x_back = -ht["Vc"] * (math.acos(ht["Vc"] / (half / ppm * ht["om"])) / ht["om"]) + half / ppm * math.sin(math.acos(ht["Vc"] / (half / ppm * ht["om"])))
    print(f"free motion after the hit (closed form: the centre at J / M, the angle J r t / I): two-thirds hit: the "
          f"handle end's speed at the instant is 0.00 m/s, the spin then sweeps it ({sp}); its trail is a cycloid with "
          f"a cusp at the hand ring because (L / 2) omega = {half / ppm * hs['om']:.3f} m/s equals the centre's "
          f"{hs['Vc']:.3f} m/s; a full turn takes {t_turn['sweet']:.4f} s real = {t_turn['sweet'] * S:.2f} s of video; "
          f"tip hit: the handle end jumps back at {-ht['vh']:.2f} m/s ({jp}), reaches {x_back * 100:.1f} cm back and the "
          f"spin brings it round in a loop because (L / 2) omega = {half / ppm * ht['om']:.2f} m/s is more than the "
          f"centre's {ht['Vc']:.3f} m/s; a full turn takes {t_turn['tip']:.4f} s real = {t_turn['tip'] * S:.2f} s of video")
    # The approach, the exits and the second-contact check, in video time after the hit.
    t_in = (W + br - x_hit) / (v0 * ppm) * S
    exits = []
    for m in PANELS:
        h = hits[m]
        if h["vb"] < 0:
            t_ball = (W + br - x_hit) / (-h["vb"] * ppm) * S
            ball = f"the ball leaves through the right edge {t_ball:.2f} s after the hit"
        else:
            xb_end = x_hit - h["vb"] * t_end * ppm
            ball = f"the ball drifts left at {h['vb'] * ppm / S:.0f} px/s and is at x {xb_end:.0f} px at the cycle's end"
        reach = xs - h["Vc"] * ((P - F - ha) / S) * ppm + half + BAR_R
        exits.append(f"{m}: the centre crosses the left edge {t_cx[m] * S:.2f} s after the hit (it moves {h['Vc'] * ppm / S:.0f} "
                     f"px/s), the whole stick is out of the band after {t_out[m] * S:.2f} s ({t_out[m] * S + ha:.2f} s "
                     f"into the cycle; at the fade's start its sweep reaches x {reach:.0f} px at most); {ball}")
    # The second-contact check: the ball's centre against the stick segment after the hit (the model has
    # one hit; the drawn ball is larger than life, so the tip hit's handle end grazes its rim on the loop).
    dmin, tmin, graze = {}, {}, {}
    contact = br + BAR_R
    for m in PANELS:
        h = hits[m]
        yb = yc - (h["d"] - L / 2.0) * ppm
        best, t_best, inside = math.inf, 0.0, 0
        for t in np.arange(0.002, t_end, 1.0 / (fps * S)):
            cx = xs - h["Vc"] * t * ppm
            phi = h["om"] * t
            ux, uy = -math.sin(phi), -math.cos(phi)
            xb = x_hit - h["vb"] * t * ppm
            dd = seg_dist(xb, yb, cx + half * ux, yc + half * uy, cx - half * ux, yc - half * uy)
            if dd < best:
                best, t_best = dd, t
            inside += dd < contact
        dmin[m], tmin[m], graze[m] = best, t_best, inside
    print(f"approach and exits (video time, 1/{S:g} speed): the ball enters the band at the right edge {t_in:.2f} s before "
          f"the hit ({ha - t_in:.2f} s into the cycle, after the fade), crosses at {v0 * ppm / S:.0f} px/s and meets the "
          f"stick at x {x_hit:.0f} px; " + "; ".join(exits) + f"; after the hit (one hit in the model) the ball's centre "
          f"comes closest to the stick at {dmin['sweet']:.1f} px = {dmin['sweet'] / ppm * 100:.1f} cm (two thirds, "
          f"{tmin['sweet'] * S:.2f} s after the hit) and {dmin['tip']:.1f} px = {dmin['tip'] / ppm * 100:.1f} cm (tip, "
          f"{tmin['tip'] * S:.2f} s after the hit: the handle end swinging back up through the ball's row); the drawn "
          f"{2 * br:.0f} px ball touches the {2 * BAR_R:.0f} px stick at {contact:.0f} px, so the tip hit's handle end "
          f"cap passes inside the drawn ball's rim by {max(0.0, contact - dmin['tip']):.1f} px on {graze['tip']} of "
          f"{int(round(t_end * fps * S))} frames (the ball is drawn on top); the two-thirds hit clears by "
          f"{dmin['sweet'] - contact:.1f} px")
    assert t_in < ha, "the ball is in the band during the reset fade"
    assert dmin["sweet"] > contact, "the two-thirds stick meets the ball again"
    assert contact - dmin["tip"] < 10.0 and graze["tip"] < 20, "the tip hit's handle end does more than graze the ball"
    ev: dict = {"hits": hits, "others": others, "root": root, "t_turn": t_turn, "x_hit": x_hit}
    # The schedule in video time.
    t0 = man["first_cycle_at"]
    k0 = math.ceil((0.0 - t0) / P - 1e-9) - 1
    k1 = math.floor((D - t0) / P - 1e-9)
    starts = [t0 + kk * P for kk in range(k0, k1 + 1)]
    ev["cycles"] = int(round(cycles))

    def lst(off_: float) -> str:
        return ", ".join(f"{st + off_:.2f}" for st in starts if 0.0 <= st + off_ < D)

    tau0 = (0.0 - t0) % P
    r0 = (tau0 - ha) / S
    xb0 = x_hit - (v0 if r0 < 0 else hs["vb"]) * r0 * ppm
    print(f"schedule (video time, 1/{S:g} speed): cycles of {P:g} s start at " + ", ".join(f"{st:.2f}" for st in starts)
          + f" s (the first {-t0:.2f} s before the first frame); the ball enters at {lst(ha - t_in)} s; the hit {ha:g} s "
          f"into each cycle at {lst(ha)} s (the event rows light); the two-thirds hit's handle end stays inside its "
          f"ring for about {0.02 * S:.1f} s of video ({math.hypot(*handle_motion(hs, 0.02)[:2]) * ppm:.0f} px moved) "
          f"and the tip hit's handle end is {handle_motion(ht, 0.02)[0] * ppm:.0f} px back by then; the two-thirds stick "
          f"is out of its band at {lst(ha + t_out['sweet'] * S)} s and the tip stick at {lst(ha + t_out['tip'] * S)} s; "
          f"the reset crossfade runs over the last {F:g} s of each cycle (from {lst(P - F)} s; the readouts out over "
          f"its first half and in over its second); on the first frame the cycle is {tau0:.2f} s in ({r0:.3f} s real: "
          f"the ball {xb0 - x_hit:.0f} px from the stick); title until {man['title_until']:g} s; payoff card from "
          f"{man['payoff_t']:g} s; the title fades back in over the last {man['loop_fade']:g} s and the last frame "
          f"repeats the first (the scene is periodic: {D:g} s holds exactly {cycles:.0f} cycles)")
    # Text widths.
    font = os.environ["SEED_ZERO_FONT"]
    f24, f28, f34, f40, f56 = (ImageFont.truetype(font, n) for n in (24, 28, 34, 40, 56))
    widths = {"overlay@34": (f34, man["overlay"])}
    for j, line in enumerate(man["title"].split("|")):
        widths[f"title line {j + 1}@56"] = (f56, line)
    widths["legend@40"] = (f40, legend_text(man))
    widths["clock@28"] = (f28, clock_text(0.1234))
    widths["clock before@28"] = (f28, clock_text(-1.0))
    for m in PANELS:
        widths[f"label {m}@40"] = (f40, label_text(man, ev, m))
        widths[f"event {m}@40"] = (f40, event_text(ev, m))
        widths[f"ball after {m}@28"] = (f28, ball_text(ev, m, True))
        widths[f"hit label {m}@24"] = (f24, hit_label(m))
    widths["sublabel@28"] = (f28, sub_text(man))
    widths["ball before@28"] = (f28, ball_text(ev, "sweet", False))
    widths["hand@24"] = (f24, "hand")
    for j, line in enumerate(payoff_lines(man, ev)):
        widths[f"payoff line {j + 1}@40"] = (f40, line)
    print("text widths (the on-screen strings verbatim): "
          + ", ".join(f"{kk} {f.getlength(s):.0f} px '{s}'" for kk, (f, s) in widths.items()))
    assert all(f.getlength(s) < 950 for f, s in widths.values()), "a text line is wider than 950 px"
    assert len(payoff_lines(man, ev)) <= 6, "the card has more than six lines"
    # Layout checks.
    label_end = ROW_X0 + max(f40.getlength(label_text(man, ev, m)) for m in PANELS)
    left = ROW_X0 + f28.getlength(sub_text(man))
    right = ROW_X1 - max(max(f28.getlength(ball_text(ev, m, True)) for m in PANELS), f28.getlength(ball_text(ev, "sweet", False)))
    rows_bottom = SUB_DY + 14
    sweep_top, sweep_bot = yc - half - BAR_R, yc + half + BAR_R
    ring = man["hand_ring_px"] / 2.0
    ring_bot = yc + half + ring
    lanes = {m: (yc - (hits[m]["d"] - L / 2.0) * ppm - br, yc - (hits[m]["d"] - L / 2.0) * ppm + br) for m in PANELS}
    ev_w = max(f40.getlength(event_text(ev, m)) for m in PANELS)
    hit_x0 = xs - BAR_R - 16 - max(f24.getlength(hit_label(m)) for m in PANELS)
    hand_x0 = xs - ring - 12 - f24.getlength("hand")
    print(f"row check: the label row (alone on its row) ends at x {label_end:.0f} px; on the second row the sublabel ends "
          f"at x {left:.0f} px and the ball readout starts at x {right:.0f} px; the rows end "
          f"{rows_bottom} px under the band top; the stick stands at x {xs:.0f} px with its centre {yc:.0f} px under the "
          f"band top and its sweep (any angle, caps included) spans {sweep_top:.0f} to {sweep_bot:.0f} px; the hand ring "
          f"reaches {ring_bot:.0f} px; the ball's lane is {lanes['sweet'][0]:.0f} to {lanes['sweet'][1]:.0f} px (two "
          f"thirds) and {lanes['tip'][0]:.0f} to {lanes['tip'][1]:.0f} px (tip); the event row spans {EVENT_DY - 22} to "
          f"{EVENT_DY + 22} px under the band top and x {W / 2 - ev_w / 2:.0f} to {W / 2 + ev_w / 2:.0f} px (widest "
          f"{ev_w:.0f} px); the hit label starts at x {hit_x0:.0f} px and the hand label at x {hand_x0:.0f} px; each band "
          f"is {BAND_H} px tall (y {BAND_Y['sweet']} to {BAND_Y['sweet'] + BAND_H} and {BAND_Y['tip']} to "
          f"{BAND_Y['tip'] + BAND_H}); the caption band starts at y {int(man['caption_y'] * H)}; the title rows end at y "
          f"{252 + 28} and the overlay band ends at y 130")
    assert right - left > 40 and label_end < W - 40, "the columns meet"
    assert sweep_top > rows_bottom + 4 and sweep_bot < BAND_H - 4, "the stick's ends cross the band's top or bottom rows"
    assert all(lo > rows_bottom + 2 for lo, _ in lanes.values()), "the ball's lane meets the text rows"
    assert ring_bot < EVENT_DY - 22 - 4, "the hand ring meets the event row"
    assert EVENT_DY + 22 < BAND_H - 8, "the event row leaves the band"
    assert hit_x0 > 20 and hand_x0 > 20, "an ice label leaves the frame"
    assert BAND_Y["tip"] + BAND_H <= int(man["caption_y"] * H), "the bottom band reaches the caption band"
    assert PAYOFF_Y - 20 > int(man["caption_y"] * H) + 90, "the card meets the caption band"
    return ev


def legend_text(man: dict) -> str:
    return f"same stick, same ball, 1/{man['slow']:g} speed"


def clock_text(r: float) -> str:
    return "before the hit" if r < 0.0 else f"{r:.3f} s after the hit"


def label_text(man: dict, ev: dict, m: str) -> str:
    if m == "sweet":
        return f"hit two thirds along, {ev['hits'][m]['d'] * 100:.1f} cm"
    return f"hit at the tip, {man['stick_length_m'] * 100:g} cm"


def sub_text(man: dict) -> str:
    return f"stiff stick {man['stick_length_m'] * 100:g} cm, ball {man['ball_speed_m_s']:g} m/s"


def ball_text(ev: dict, m: str, after: bool) -> str:
    h = ev["hits"][m]
    if not after:
        return f"ball {h['v0']:g} m/s"
    if h["vb"] < 0:
        return f"ball back at {-h['vb']:.1f} m/s"
    return f"ball on at {h['vb']:.1f} m/s"


def event_text(ev: dict, m: str) -> str:
    h = ev["hits"][m]
    if m == "sweet":
        return f"handle end at the hit: {abs(h['vh']):.2f} m/s"
    return f"handle end at the hit: {-h['vh']:.1f} m/s back"


def hit_label(m: str) -> str:
    return "2/3" if m == "sweet" else "tip"


def payoff_lines(man: dict, ev: dict) -> list[str]:
    L = man["stick_length_m"]
    text = man["payoff_text"].format(
        vh_sweet=abs(ev["hits"]["sweet"]["vh"]), vh_tip=-ev["hits"]["tip"]["vh"],
        vc_mid=ev["others"][L * 100 / 2]["Vc"], vh_e1=-ev["others"]["e1"]["vh"])
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
        self.font_ice = ImageFont.truetype(font, 24 * SS)
        self.ppm = float(man["px_per_m"])
        self.S = man["slow"]
        self.P = man["cycle_s"]
        self.P_f = int(round(man["cycle_s"] * self.fps))
        self.c0_f = int(round(man["first_cycle_at"] * self.fps))
        self.ha, self.F = man["hit_at"], man["reset_fade"]
        self.hits = ev["hits"]
        self.L = man["stick_length_m"]
        self.half = self.L / 2.0 * self.ppm
        self.xs, self.yc = float(man["stick_x_px"]), float(man["centre_dy"])
        self.br = float(man["ball_radius_px"])
        self.ring = man["hand_ring_px"] / 2.0
        self.x_hit = self.xs + BAR_R + self.br

    def phase(self, f: int) -> tuple[int, float]:
        k, tau_f = divmod(f - self.c0_f, self.P_f)
        return k, tau_f / self.fps

    @staticmethod
    def L_(x: float, y: float) -> tuple[float, float]:
        """Layer (2x) pixel of a band-local point, rounded to 1e-4 px so equal states draw equal pixels."""
        return round(x * SS, 4), round(y * SS, 4)

    def geometry(self, m: str, rt: float) -> tuple:
        """(centre x, angle, tip direction, tip, handle) in band-local px rt real seconds after the hit."""
        h = self.hits[m]
        if rt < 0.0:
            cx, phi = self.xs, 0.0
        else:
            cx, phi = self.xs - h["Vc"] * rt * self.ppm, h["om"] * rt
        ux, uy = -math.sin(phi), -math.cos(phi)
        tip = (cx + self.half * ux, self.yc + self.half * uy)
        handle = (cx - self.half * ux, self.yc - self.half * uy)
        return cx, phi, (ux, uy), tip, handle

    def ball_at(self, m: str, rt: float) -> tuple[float, float]:
        h = self.hits[m]
        yb = self.yc - (h["d"] - self.L / 2.0) * self.ppm
        xb = self.x_hit - (h["v0"] if rt < 0.0 else h["vb"]) * rt * self.ppm
        return xb, yb

    def draw_ice(self, d: ImageDraw.ImageDraw, m: str) -> None:
        for x0, y0, x1, y1 in STREAKS:
            d.line((*self.L_(x0, y0), *self.L_(x1, y1)), fill=ICE_STREAK, width=2 * SS)
        d.line((*self.L_(0, 1), *self.L_(W, 1)), fill=ICE_EDGE, width=2 * SS)
        # The hit point's label on the ice, the hand label and the hand ring where the handle end rests.
        _, yb = self.ball_at(m, -1.0)
        d.text(self.L_(self.xs - BAR_R - 16, yb), hit_label(m), font=self.font_ice, fill=MUTED, anchor="rm")
        hx, hy = self.xs, self.yc + self.half
        d.text(self.L_(hx - self.ring - 12, hy), "hand", font=self.font_ice, fill=MUTED, anchor="rm")
        r = self.ring * SS
        X, Y = self.L_(hx, hy)
        d.ellipse((X - r, Y - r, X + r, Y + r), outline=COLOUR[m], width=3 * SS)

    def draw_trail(self, d: ImageDraw.ImageDraw, m: str, rt: float) -> None:
        if rt <= 0.0:
            return
        step = 1.0 / (self.fps * self.S)
        n = int(rt / step)
        pts = [self.L_(*self.geometry(m, k * step)[4]) for k in range(n + 1)] + [self.L_(*self.geometry(m, rt)[4])]
        if len(pts) > 1:
            d.line(pts, fill=blend(GOLD, 0.85, ICE), width=3 * SS, joint="curve")

    def draw_stick(self, d: ImageDraw.ImageDraw, m: str, rt: float) -> None:
        h = self.hits[m]
        _, _, (ux, uy), tip, handle = self.geometry(m, rt)
        col = COLOUR[m]
        p_t, p_h = self.L_(*tip), self.L_(*handle)
        r = BAR_R * SS
        d.line((*p_h, *p_t), fill=col, width=int(2 * r))
        d.ellipse((p_t[0] - r, p_t[1] - r, p_t[0] + r, p_t[1] + r), fill=col)
        d.ellipse((p_h[0] - r, p_h[1] - r, p_h[0] + r, p_h[1] + r), fill=col)
        # The tick across the stick at the hit point, riding with the stick.
        px, py = handle[0] + h["d"] * self.ppm * ux, handle[1] + h["d"] * self.ppm * uy
        nx, ny = -uy, ux
        tl = BAR_R + 3.0
        d.line((*self.L_(px - nx * tl, py - ny * tl), *self.L_(px + nx * tl, py + ny * tl)), fill=INK, width=3 * SS)
        # The handle end marker.
        rh = (BAR_R - 1.5) * SS
        d.ellipse((p_h[0] - rh, p_h[1] - rh, p_h[0] + rh, p_h[1] + rh), fill=WHITE)

    def draw_ball(self, d: ImageDraw.ImageDraw, m: str, rt: float) -> None:
        xb, yb = self.ball_at(m, rt)
        if xb < -self.br - 4.0 or xb > W + self.br + 4.0:
            return
        r = self.br * SS
        X, Y = self.L_(xb, yb)
        d.ellipse((X - r, Y - r, X + r, Y + r), fill=WHITE, outline=BALL_RIM, width=2 * SS)

    def scene(self, m: str, tau: float) -> tuple[Image.Image, dict]:
        """The band layer of panel m at tau seconds into a cycle (the resting stick before the hit)."""
        layer = Image.new("RGB", (W * SS, BAND_H * SS), ICE)
        d = ImageDraw.Draw(layer)
        self.draw_ice(d, m)
        tv = tau - self.ha
        rt = tv / self.S
        self.draw_trail(d, m, rt)
        self.draw_stick(d, m, rt)
        self.draw_ball(d, m, rt)
        return layer, {"tv": tv, "rt": rt, "phase": AFTER if rt >= 0.0 else BEFORE}

    def draw_panel(self, m: str, f: int) -> tuple[Image.Image, dict]:
        k, tau = self.phase(f)
        P, F = self.P, self.F
        layer, st = self.scene(m, tau)
        st["alpha"], st["k"] = 1.0, k
        if tau >= P - F:
            # Crossfade to the next cycle's resting stick (the ball of the next cycle enters after the
            # fade, asserted in measure; the ice is drawn the same in both, so it never blinks).
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
            a, after = st["alpha"], st["phase"] == AFTER
            d.text((ROW_X0, y0 + LABEL_DY), label_text(man, ev, m), font=self.font, fill=COLOUR[m], anchor="lm")
            d.text((ROW_X0, y0 + SUB_DY), sub_text(man), font=self.font_small, fill=MUTED, anchor="lm")
            d.text((ROW_X1, y0 + SUB_DY), ball_text(ev, m, after), font=self.font_small,
                   fill=blend(GOLD if after else TEXT, a), anchor="rm")
            if after:
                d.text((W / 2, y0 + EVENT_DY), event_text(ev, m), font=self.font, fill=blend(GOLD, a), anchor="mm")
        if hud_alpha > 0.02:
            d.text((W / 2, LEGEND_Y), legend_text(man), font=self.font, fill=blend(TEXT, hud_alpha), anchor="mm")
            d.text((W / 2, CLOCK_Y), clock_text(states["sweet"]["rt"]), font=self.font_small,
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
        print(f"loop step: the frame before the last differs from the last in {int((diff.max(axis=2) > 24).sum())} px "
              f"(the approaching ball moves one frame on)")
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
    man = json.loads((ROOT / "projects/sweetspot/manifest.json").read_text())
    ev = measure(man)
    if "--measure-only" in sys.argv:
        return
    if "--frames" in sys.argv:
        times = [float(v) for v in sys.argv[sys.argv.index("--frames") + 1].split(",")]
        r = Renderer(man, ev)
        (ROOT / "media/sweetspot").mkdir(parents=True, exist_ok=True)
        for tv in times:
            Image.fromarray(r.frame_at(int(round(tv * man["fps"])))).save(ROOT / f"media/sweetspot/smoke-{tv}.png")
        print("smoke frames: " + ", ".join(f"{tv}" for tv in times))
        return
    Renderer(man, ev).render(ROOT / "media/sweetspot/footage.mp4")


if __name__ == "__main__":
    main()
