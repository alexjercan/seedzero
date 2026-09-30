#!/usr/bin/env python3
"""Ball or ring into a wall: which one comes back?

Two panels on the same clock, the same table drawn the same way at the same
scale. Top, a solid ball (I = k m r^2, k = 2/5). Bottom, a thin ring (k = 1)
of the same radius r. Both roll without slipping at v0 toward a smooth
vertical wall wall_m from the start line; at t = 0 each body's leading edge
is on the start line (its centre r behind it), so the centre travels wall_m
to the hit at exactly wall_m / v0. The wall is smooth (no tangential
impulse) with restitution e: at the hit the centre's velocity reverses to
-e v0 and the spin is unchanged, so the contact point on the table slides
at (1 + e) v0 away from the wall. Sliding friction mu m g acts toward the
wall (opposing the slip), slows the centre at mu g and unwinds the spin at
mu g / (k r); the slip closes when the contact is at rest and the body
rolls again. The slip is integrated by a stepped Coulomb model at dt_s
(the friction sign re-evaluated every step, the closure located by linear
interpolation inside the step) and checked against the closed forms

    t_slip = (1 + e) v0 k / ((1 + k) mu g),
    v_back = v0 (k - e) / (1 + k)            (negative: away from the wall),
    d_wall = e v0 t_slip - mu g t_slip^2 / 2,

the angular momentum about the table contact line (v + k r omega, which
friction cannot change) and a half-step rerun. The free rolls before the
hit and after the slip are constant speed (no force acts). The run repeats
every cycle_s seconds of video with the marks and the parked ring fading
over the last reset_fade seconds; the cycle divides the scene length, so
the scene is exactly periodic and the last frame equals the first. Shown
at 1/slow speed. Deterministic, no seed.

Measured and printed: for each panel the hit time, the slip time, the
distance from the wall when the slip ends, the speed it rolls back at, the
energy kept and the angular momentum before and after (stepped model and
closed form); other shapes, a spinless puck on ice, a bounce of e = 0.8,
other mu, two balls head on and a grippy wall (for the description); a
half-step check; the schedule in video time; the on-screen text widths and
the layout clearances.

usage: wallbounce.py [--measure-only] [--frames t1,t2,...]
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
RING = (150, 214, 240)
RING_DARK = (70, 128, 176)
BALL_DARK = (140, 52, 48)
TABLE = (46, 42, 40)
TABLE_TOP = (92, 84, 76)
TABLE_INK = (150, 140, 128)
WALL = (128, 136, 148)
WALL_FACE = (200, 206, 214)
WALL_INK = (36, 40, 48)

# Layout: overlay at y 96..130 (captions.py), two title rows at y 190/252 for
# the first seconds, then the legend at y 236 and the shared clock at y 290;
# two panels stacked, the ball in the band y 330..880 and the ring in y
# 880..1430, both drawn at 2x in one geometry layer; each band has its label
# row 40 px under the band top, its second row at 84 and its third at 120
# (left column from x 40, right column to x 1040); the payoff label row at
# 200; the wall from 262 down to the table surface at 470 (y 800 and 1350);
# the bracket at 400 with its text at 372; the table slab down to 520; tick
# labels at 503; captions at caption_y 0.75 (y 1440..1530); the six-line
# card from y 1572 at a 48 px pitch.
LEGEND_Y, CLOCK_Y = 236, 290
SS = 2
GEOM_Y0, GEOM_Y1 = 330, 1430
PAYOFF_Y, PAYOFF_PITCH = 1572.0, 48
PANELS = ("ball", "ring")
BAND_Y = {"ball": 330, "ring": 880}
LABEL_DY, SUB_DY, FIX_DY = 40, 84, 120
PAY_DY, WALL_TOP_DY, WALL_LABEL_DY, WALL_HATCH_DY = 200, 262, 292, 344
BRACKET_TEXT_DY, BRACKET_DY, FLOOR_DY, SLAB_DY, TICK_LABEL_DY = 372, 400, 470, 520, 503
ROW_X0, ROW_X1 = 40, 1040
WALL_X1 = W + 12          # the wall runs off the right edge of the frame
COLOUR = {"ball": CORAL, "ring": RING}
EDGE = {"ball": BALL_DARK, "ring": RING_DARK}


def blend(col, a: float, base=BG) -> tuple:
    a = max(0.0, min(1.0, a))
    return tuple(int(round(c * a + b * (1 - a))) for c, b in zip(col, base))


# --- measurement --------------------------------------------------------------
def slip(v: float, om: float, r: float, k: float, mu: float, g: float, dt: float) -> dict:
    """Stepped Coulomb model of the slip from the state just after the hit (centre speed v, spin om,
    rolling is v = r om) until the contact point is at rest. Every step re-evaluates the friction
    sign from the slip v - r om; the closure is located by linear interpolation inside the step.
    Returns the arrays and the end state (t from the hit, x from the hit position)."""
    T, X, V, OM, TH = [0.0], [0.0], [v], [om], [0.0]
    t, x, th = 0.0, 0.0, 0.0
    s = v - r * om
    a = 0.0
    while abs(s) > 0.0:
        sg = 1.0 if s > 0.0 else -1.0
        a = -mu * g * sg
        al = mu * g * sg / (k * r)
        v_new, om_new = v + a * dt, om + al * dt
        s_new = v_new - r * om_new
        if s_new * s <= 0.0:
            h = dt * s / (s - s_new)
            v, om = v + a * h, om + al * h
            x += V[-1] * h + 0.5 * a * h * h
            th += OM[-1] * h + 0.5 * al * h * h
            t += h
            om = v / r                       # snap out the rounding: the body rolls
            T.append(t), X.append(x), V.append(v), OM.append(om), TH.append(th)
            s = 0.0
            break
        x += v * dt + 0.5 * a * dt * dt
        th += om * dt + 0.5 * al * dt * dt
        v, om, s = v_new, om_new, s_new
        t += dt
        T.append(t), X.append(x), V.append(v), OM.append(om), TH.append(th)
    return {"t": np.array(T), "x": np.array(X), "v": np.array(V), "om": np.array(OM), "th": np.array(TH),
            "t_end": t, "x_end": x, "v_end": v, "om_end": om, "th_end": th, "dt": dt, "steps": len(T) - 1}


def simulate(man: dict, k: float, mu: float, e: float, dt: float, spin: bool = True) -> dict:
    """One body from the start line into the wall and back: the free roll (constant speed, the
    centre from -r), the hit at the wall, the stepped slip, the free roll after."""
    g, v0, r, L = man["g"], man["v0_m_s"], man["radius_m"], man["wall_m"]
    om0 = v0 / r if spin else 0.0
    run: dict = {"k": k, "mu": mu, "e": e, "r": r, "v0": v0, "om0": om0, "dt": dt}
    run["t_hit"] = L / v0                        # the centre travels L at v0 (no force acts)
    run["x_hit"] = L - r
    run["th_hit"] = om0 * run["t_hit"]
    v_hit = -e * v0
    run["v_hit"] = v_hit
    if mu <= 0.0 or (abs(v_hit - r * om0) < 1e-15):
        # No friction (or no slip): the body keeps the post-hit state.
        run.update({"t_end": run["t_hit"], "x_end": run["x_hit"], "v_end": v_hit, "om_end": om0,
                    "th_end": run["th_hit"], "slip": None, "d_wall": 0.0, "t_slip": 0.0, "steps": 0})
    else:
        sl = slip(v_hit, om0, r, k, mu, g, dt)
        run["slip"] = sl
        run["t_slip"] = sl["t_end"]
        run["t_end"] = run["t_hit"] + sl["t_end"]
        run["x_end"] = run["x_hit"] + sl["x_end"]
        run["v_end"], run["om_end"] = sl["v_end"], sl["om_end"]
        run["th_end"] = run["th_hit"] + sl["th_end"]
        run["d_wall"] = -sl["x_end"]             # the centre's travel away from the wall = the gap
        run["steps"] = sl["steps"]
    if run["v_end"] < -1e-9:
        run["t_back"] = run["t_end"] + (run["x_end"] + r) / (-run["v_end"])   # the leading edge back on the line
    else:
        run["t_back"] = None                     # stopped (|v| under 1e-9 m/s) or moving toward the wall
    # Closed forms.
    if mu > 0.0 and spin:
        ts = (1.0 + e) * v0 * k / ((1.0 + k) * mu * g)
        run["closed"] = {"t_slip": ts, "v_end": v0 * (k - e) / (1.0 + k), "d_wall": e * v0 * ts - 0.5 * mu * g * ts * ts,
                         "energy": ((k - e) / (1.0 + k)) ** 2}
    else:
        run["closed"] = {"t_slip": 0.0, "v_end": v_hit, "d_wall": 0.0, "energy": e * e}
    run["energy"] = (run["v_end"] / v0) ** 2      # (1 + k) v^2 / 2 over (1 + k) v0^2 / 2
    # Angular momentum about the table contact line, (v + k r omega) / v0.
    run["ell_before"] = (v0 + k * r * om0) / v0
    run["ell_hit"] = (v_hit + k * r * om0) / v0
    run["ell_end"] = (run["v_end"] + k * r * run["om_end"]) / v0
    if run["slip"] is not None:
        ell = (run["slip"]["v"] + k * r * run["slip"]["om"]) / v0
        run["ell_drift"] = float(np.max(np.abs(ell - run["ell_hit"])))
    else:
        run["ell_drift"] = 0.0
    return run


def state_at(run: dict, t: float) -> dict:
    """Centre x (from the start line), speed v, spin om, stripe angle th and the contact slip at real time t."""
    r, v0, om0 = run["r"], run["v0"], run["om0"]
    if t < run["t_hit"]:
        x, v, om, th = -r + v0 * t, v0, om0, om0 * t
        phase = "in"
    elif run["slip"] is not None and t < run["t_end"]:
        sl = run["slip"]
        u = t - run["t_hit"]
        i = min(int(u / sl["dt"]), len(sl["t"]) - 2)
        f = (u - sl["t"][i]) / (sl["t"][i + 1] - sl["t"][i])
        x = run["x_hit"] + sl["x"][i] + f * (sl["x"][i + 1] - sl["x"][i])
        v = sl["v"][i] + f * (sl["v"][i + 1] - sl["v"][i])
        om = sl["om"][i] + f * (sl["om"][i + 1] - sl["om"][i])
        th = run["th_hit"] + sl["th"][i] + f * (sl["th"][i + 1] - sl["th"][i])
        phase = "slip"
    else:
        u = t - run["t_end"]
        x, v, om = run["x_end"] + run["v_end"] * u, run["v_end"], run["om_end"]
        th = run["th_end"] + run["om_end"] * u
        phase = "out"
    return {"x": float(x), "v": float(v), "om": float(om), "th": float(th), "slip": float(v - r * om), "phase": phase}


def measure(man: dict) -> dict:
    g, v0, r, L, mu, e = man["g"], man["v0_m_s"], man["radius_m"], man["wall_m"], man["mu"], man["e"]
    dt = man["dt_s"]
    S, P, D, fps, F, ca = man["slow"], man["cycle_s"], man["scene_duration"], man["fps"], man["reset_fade"], man["cross_at"]
    cycles = D / P
    assert abs(cycles - round(cycles)) < 1e-9, "the cycle must divide the scene length"
    for key in ("cycle_s", "cross_at", "first_cycle_at", "reset_fade", "scene_duration"):
        assert abs(man[key] * fps - round(man[key] * fps)) < 1e-9, f"{key} must be a whole number of frames"
    ppm = man["px_per_m"]
    ks = {"ball": man["k_ball"], "ring": man["k_ring"]}
    print(f"setup: side view, two panels on one clock, the same table (sliding friction mu = {mu:g}) and the same smooth "
          f"vertical wall (restitution e = {e:g}, no tangential impulse) {L:g} m from the start line; top panel a solid "
          f"ball of radius {r * 100:g} cm (I = {ks['ball']:g} m r^2), bottom panel a thin ring of the same radius (I = "
          f"{ks['ring']:g} m r^2); convention: at t = 0 each body's leading edge is on the start line (its centre {r * 100:g} "
          f"cm behind it) and rolls without slipping at v0 = {v0:g} m/s, spinning at v0 / r = {v0 / r:.2f} rad/s "
          f"({v0 / r / (2 * math.pi):.2f} turns a second), so the centre travels {L:g} m and the hit comes at exactly "
          f"{L / v0:.3f} s; 'distance from the wall' is the gap between the wall face and the body's near edge (the "
          f"centre's travel since the hit); 'back at the start line' is the same edge crossing the line on the way back; "
          f"g = {g:g} m/s^2; at the hit the centre's velocity reverses (to -e v0) and the spin is unchanged, then the "
          f"contact slides and friction mu m g acts toward the wall until the slip closes: stepped Coulomb model at dt = "
          f"{dt:.0e} s with the closure located by linear interpolation inside the step, the free rolls before the hit and "
          f"after the slip at constant speed (no force acts); shown at 1/{S:g} speed on a {P:g} s cycle ({P * fps:.0f} "
          f"frames) with the start line crossed {ca:g} s into the cycle, {cycles:.0f} cycles in {D:g} s; drawn at {ppm:g} "
          f"px per metre, the stripe on each body is a massless mark; deterministic, no seed")
    runs = {m: simulate(man, ks[m], mu, e, dt) for m in PANELS}
    ev: dict = {"runs": runs}
    half_px = r * ppm
    lx = man["line_x_px"]
    enter_t = (-(lx + half_px + 2.0) / ppm + r) / v0   # real time (from t = 0) when the body clears the left edge
    ev["enter_t"] = enter_t
    for m in PANELS:
        rn, k = runs[m], ks[m]
        cf = rn["closed"]
        name = "ball" if m == "ball" else "ring"
        sl = rn["slip"]
        back = "away from the wall" if rn["v_end"] < -1e-9 else ("toward the wall" if rn["v_end"] > 1e-9 else "stopped")
        line = (f"{m}: stepped model: the hit comes at {rn['t_hit']:.6f} s with the centre {rn['x_hit'] + r:.3f} m past the "
                f"start line (the leading edge on the wall); after the hit the centre moves at {abs(rn['v_hit']):.4f} m/s "
                f"away from the wall with the spin unchanged at {rn['om0']:.2f} rad/s the old way, so the contact slides at "
                f"{abs(rn['v_hit'] - r * rn['om0']):.4f} m/s; the slip closes {rn['t_slip']:.6f} s after the hit (closed form "
                f"(1 + e) v0 k / ((1 + k) mu g) = {cf['t_slip']:.6f} s, diff {rn['t_slip'] - cf['t_slip']:+.1e} s) over "
                f"{rn['steps']} steps, {rn['d_wall'] * 100:.3f} cm from the wall (closed form e v0 t - mu g t^2 / 2 = "
                f"{cf['d_wall'] * 100:.3f} cm, diff {(rn['d_wall'] - cf['d_wall']) * 100:+.1e} cm), and the {name} then "
                f"rolls at {abs(rn['v_end']):.6f} m/s {back} (closed form v0 (k - e) / (1 + k) = {abs(cf['v_end']):.6f} m/s = "
                f"{fraction(k, e)}, diff {rn['v_end'] - cf['v_end']:+.1e} m/s), spinning at {abs(rn['om_end']):.2f} rad/s "
                f"({abs(rn['om_end']) / (2 * math.pi):.2f} turns a second); energy kept {rn['energy']:.4f} of the start "
                f"(closed form ((k - e) / (1 + k))^2 = {cf['energy']:.4f}); angular momentum about the table contact line "
                f"(v + k r omega) / v0: {rn['ell_before']:.4f} before the hit, {rn['ell_hit']:.4f} after the hit, "
                f"{tidy(rn['ell_end']):.4f} after the slip (drift {rn['ell_drift']:.1e} through the slip: friction acts on that "
                f"line and cannot change it); the slip covers {sl['x_end'] * -100:.3f} cm of the centre's path with the "
                f"spin falling from {sl['om'][0]:.2f} to {tidy(sl['om_end']):.2f} rad/s")
        if rn["t_back"] is not None:
            leave = rn["t_back"] + ((lx + half_px + 2.0) / ppm - r) / abs(rn["v_end"])
            rn["t_leave"] = leave
            line += (f"; timeline: hit {rn['t_hit']:.3f} s, rolls again {rn['t_end']:.3f} s, leading edge back on the "
                     f"start line {rn['t_back']:.3f} s, off the left edge of the frame {leave:.3f} s")
        else:
            rn["t_leave"] = None
            line += (f"; timeline: hit {rn['t_hit']:.3f} s, stops {rn['t_end']:.3f} s and stays {rn['d_wall'] * 100:.2f} "
                     f"cm from the wall")
        print(line)
    rb, rr = runs["ball"], runs["ring"]
    print(f"the two panels: the ball rolls back at {abs(rb['v_end']):.4f} m/s, {abs(rb['v_end']) / v0:.4f} of its speed "
          f"(3/7 = {3 / 7:.4f}), after sliding {rb['t_slip']:.4f} s and coming to rest as a roller {rb['d_wall'] * 100:.2f} "
          f"cm from the wall; the ring rolls back at {abs(rr['v_end']):.4f} m/s: it stops dead after sliding "
          f"{rr['t_slip']:.4f} s, {rr['d_wall'] * 100:.2f} cm from the wall; the ball keeps {rb['energy']:.4f} of its "
          f"energy, the ring {rr['energy']:.4f}; same speed, same wall, same table: the bounce flips the motion and not "
          f"the spin, the spin fights the return, and the ring's spin (k = 1) holds exactly as much as its motion")
    # For the description.
    descr = []
    ev["shapes"] = {}
    for name, k in man["description_shapes"]:
        rs = simulate(man, k, mu, e, dt)
        ev["shapes"][name] = abs(rs["v_end"]) / v0
        descr.append(f"{name} (k = {k:.4f}): rolls back at {abs(rs['v_end']):.4f} m/s ({abs(rs['v_end']) / v0:.4f} v0, "
                     f"closed form {fraction(k, e)}), slip {rs['t_slip']:.4f} s, {rs['d_wall'] * 100:.2f} cm from the wall, "
                     f"energy kept {rs['energy']:.4f}")
    rp = simulate(man, ks["ball"], 0.0, e, dt, spin=False)
    ev["puck"] = abs(rp["v_end"]) / v0
    descr.append(f"a spinless puck on ice (no spin, no friction): comes back at {abs(rp['v_end']):.4f} m/s "
                 f"({abs(rp['v_end']) / v0:.4f} v0), no slip to close, energy kept {rp['energy']:.4f}")
    e2 = man["description_e"]
    for m in PANELS:
        rs = simulate(man, ks[m], mu, e2, dt)
        way = "away from the wall" if rs["v_end"] < -1e-9 else "toward the wall (it creeps back to the wall)"
        descr.append(f"bounce e = {e2:g}, {m}: leaves the wall at {abs(rs['v_hit']):.2f} m/s, slip {rs['t_slip']:.4f} s, "
                     f"{rs['d_wall'] * 100:.2f} cm from the wall, then rolls at {abs(rs['v_end']):.4f} m/s "
                     f"({abs(rs['v_end']) / v0:.4f} v0, closed form {fraction(ks[m], e2)}) {way}")
        ev[f"e2_{m}"] = rs["v_end"] / v0
    for mu2 in man["description_mus"]:
        rs = simulate(man, ks["ball"], mu2, e, dt)
        descr.append(f"mu {mu2:g}, ball: rolls back at {abs(rs['v_end']):.4f} m/s (the same 3/7), slip {rs['t_slip']:.4f} s, "
                     f"{rs['d_wall'] * 100:.2f} cm from the wall (mu sets only the slip time and distance)")
        ev[f"mu_{mu2:g}"] = rs["d_wall"]
    # Two rolling balls head on: equal masses and a frictionless contact swap the centre velocities and
    # leave both spins, so each ball is in the wall state with e = 1 and slips the same way.
    rt = simulate(man, ks["ball"], mu, 1.0, dt)
    descr.append(f"two rolling balls meeting head on (equal masses, frictionless contact: the centre velocities swap, "
                 f"the spins stay): each is in the e = 1 wall state and rolls back at {abs(rt['v_end']):.4f} m/s "
                 f"({abs(rt['v_end']) / v0:.4f} v0) after sliding {rt['t_slip']:.4f} s")
    kick = {m: v0 * ks[m] / (1.0 + ks[m]) for m in PANELS}
    ev["kick"] = kick
    descr.append(f"a grippy wall (not modelled in the panels): the wall contact moves down at v0 during the hit, so wall "
                 f"friction that stops that slide gives an upward kick v0 k / (1 + k) = {kick['ball']:.4f} m/s (ball, 2/7 v0) "
                 f"and {kick['ring']:.4f} m/s (ring, 1/2 v0) and takes spin away, so the claim needs a smooth wall")
    print("for the description (same table, same 1 m/s): " + "; ".join(descr))
    half = {m: simulate(man, ks[m], mu, e, 0.5 * dt) for m in PANELS}
    print(f"check at half the time step (dt = {0.5 * dt:.0e} s): " + "; ".join(
        f"{m} slip {half[m]['t_slip']:.9f} s ({half[m]['t_slip'] - runs[m]['t_slip']:+.1e}), {half[m]['d_wall'] * 100:.7f} cm "
        f"({(half[m]['d_wall'] - runs[m]['d_wall']) * 100:+.1e}), rolls back at {abs(half[m]['v_end']):.9f} m/s "
        f"({half[m]['v_end'] - runs[m]['v_end']:+.1e}), {half[m]['steps']} steps" for m in PANELS))
    # Schedule in video time.
    t0 = man["first_cycle_at"]
    k0 = math.ceil((0.0 - t0) / P - 1e-9) - 1
    k1 = math.floor((D - t0) / P - 1e-9)
    starts = [t0 + k * P for k in range(k0, k1 + 1)]
    ev["cycles"] = int(round(cycles))

    def lst(off_: float) -> str:
        return ", ".join(f"{s + off_:.2f}" for s in starts if 0.0 <= s + off_ < D)

    assert ca + enter_t * S > 0.0, "the bodies are on the frame at the cycle start"
    assert ca + rb["t_leave"] * S < P - F, "the ball is still on the frame at the reset fade"
    tau0 = (0.0 - t0) % P
    r0 = (tau0 - ca) / S
    st0 = state_at(rb, r0)
    print(f"schedule (video time, 1/{S:g} speed): cycles of {P:g} s start at " + ", ".join(f"{s:.2f}" for s in starts)
          + f" s (the first {-t0:.2f} s before the first frame); both bodies come in from the left edge {-enter_t * S:.2f} s "
          f"before their leading edge crosses the start line, {ca:g} s into each cycle at {lst(ca)} s; both hit the wall "
          f"at {lst(ca + rb['t_hit'] * S)} s; the ball rolls again (label lit) at {lst(ca + rb['t_end'] * S)} s and the "
          f"ring stops (label lit) at {lst(ca + rr['t_end'] * S)} s; the ball is back at the start line at "
          f"{lst(ca + rb['t_back'] * S)} s and off the frame at {lst(ca + rb['t_leave'] * S)} s; the marks and the parked "
          f"ring fade over the last {F:g} s of each cycle (from {lst(P - F)} s); on the first frame the cycle is "
          f"{tau0:.2f} s in ({r0:.3f} s real: both centres {-st0['x'] * 100:.1f} cm before the start line, rolling in); "
          f"title until {man['title_until']:g} s; payoff card from {man['payoff_t']:g} s; the title fades back in over the "
          f"last {man['loop_fade']:g} s and the last frame repeats the first (the scene is periodic: {D:g} s holds exactly "
          f"{cycles:.0f} cycles)")
    # Text widths.
    font = os.environ["SEED_ZERO_FONT"]
    f24, f28, f34, f40, f56 = (ImageFont.truetype(font, n) for n in (24, 28, 34, 40, 56))
    widths = {"overlay@34": (f34, man["overlay"])}
    for j, line in enumerate(man["title"].split("|")):
        widths[f"title line {j + 1}@56"] = (f56, line)
    widths["legend@40"] = (f40, legend_text(man))
    widths["clock@28"] = (f28, clock_text(2.6873))
    widths["clock rest@28"] = (f28, clock_text(-1.0))
    for m in PANELS:
        widths[f"label {m}@40"] = (f40, label_text(m))
        widths[f"sublabel {m}@28"] = (f28, sub_text(m, man))
        widths[f"fixed {m}@28"] = (f28, fixed_text(ev, m))
        widths[f"payoff label {m}@40"] = (f40, pay_text(ev, m))
        widths[f"bracket {m}@28"] = (f28, bracket_text(runs[m]))
    widths["speed in@40"] = (f40, speed_text(1.0, "in", 0.0))
    widths["speed out@40"] = (f40, speed_text(-1.0, "slip", 0.0))
    widths["speed back@40"] = (f40, speed_text(-0.4286, "out", 0.0))
    widths["speed stopped@40"] = (f40, speed_text(0.0, "out", 0.0))
    widths["spin@28"] = (f28, spin_text(33.33))
    widths["contact slides@28"] = (f28, contact_text(-2.0))
    widths["contact rest@28"] = (f28, contact_text(0.0))
    widths["contact stopped@28"] = (f28, contact_text(0.0, 0.0))
    for j, word in enumerate(WALL_LABEL.split()):
        widths[f"wall word {j + 1}@24"] = (f24, word)
    widths["start@24"] = (f24, START_LABEL)
    for j, line in enumerate(payoff_lines(man, ev)):
        widths[f"payoff line {j + 1}@40"] = (f40, line)
    print("text widths: " + ", ".join(f"{k} {f.getlength(s):.0f} px" for k, (f, s) in widths.items()))
    assert all(f.getlength(s) < 950 for f, s in widths.values()), "a text line is wider than 950 px"
    # Layout checks.
    wall_x = lx + L * ppm
    gaps = []
    for m in PANELS:
        gaps.append((ROW_X1 - f40.getlength(speed_text(-1.0, "slip", 0.0))) - (ROW_X0 + f40.getlength(label_text(m))))
        gaps.append((ROW_X1 - f28.getlength(spin_text(33.33)) - 40) - (ROW_X0 + f28.getlength(sub_text(m, man))))
        gaps.append((ROW_X1 - f28.getlength(contact_text(-2.0))) - (ROW_X0 + f28.getlength(fixed_text(ev, m))))
    left = ROW_X0 + max(max(f40.getlength(label_text(m)), f28.getlength(sub_text(m, man)), f28.getlength(fixed_text(ev, m)))
                        for m in PANELS)
    right = ROW_X1 - max(f40.getlength(speed_text(-1.0, "slip", 0.0)), f28.getlength(spin_text(33.33)) + 40,
                         f28.getlength(contact_text(-2.0)))
    rows_bottom = FIX_DY + 16
    pay_x1 = wall_x - 40.0
    pay_x0 = min(pay_x1 - f40.getlength(pay_text(ev, m)) for m in PANELS)
    wl_w = max(f24.getlength(w) for w in WALL_LABEL.split())
    wl_x0, wl_x1 = (wall_x + W) / 2 - wl_w / 2, (wall_x + W) / 2 + wl_w / 2
    body_top = FLOOR_DY - 2.0 * r * ppm
    brk = []
    for m in PANELS:
        xe = lx + (runs[m]["x_end"] + r) * ppm
        bw = f28.getlength(bracket_text(runs[m]))
        bx = bracket_text_x(xe, wall_x, bw)
        brk.append((m, xe, bx - bw / 2, bx + bw / 2))
        assert bx + bw / 2 <= wall_x - 8.0, "the bracket text meets the wall"
    print(f"layout: the left column ends at x {left:.0f} px, the right column starts at x {right:.0f} px, both end "
          f"{rows_bottom} px under the band top, and on each of the three rows the gap between the left text and the "
          f"right text is at least {min(gaps):.0f} px; the wall face is at x {wall_x:.0f} px, the wall from {WALL_TOP_DY} to "
          f"{FLOOR_DY} px under the band top; the payoff label row at {PAY_DY} px spans x {pay_x0:.0f} to {pay_x1:.0f} px "
          f"(its bottom {PAY_DY + 20} px, above the wall top); the wall label (two words inside the wall) at {WALL_LABEL_DY} "
          f"and {WALL_LABEL_DY + 28} px, x {wl_x0:.0f} to {wl_x1:.0f} px (the wall face at {wall_x:.0f}, the frame edge at "
          f"{W}), the hatch from {WALL_HATCH_DY} px; the bracket text at {BRACKET_TEXT_DY} px (bottom {BRACKET_TEXT_DY + 14}) and the bracket at "
          f"{BRACKET_DY} px sit above the body top at {body_top:.0f} px (brackets from x "
          + ", ".join(f"{xe:.0f} px to the wall with the text x {x0:.0f} to {x1:.0f} px ({m})" for m, xe, x0, x1 in brk)
          + f"); the bodies are {2 * r * ppm:.0f} px across; the "
          f"slip streaks run {rb['d_wall'] * ppm:.0f} px (ball) and {rr['d_wall'] * ppm:.0f} px (ring) back from the "
          f"contact at the hit (x {lx + rb['x_hit'] * ppm:.0f} px); the geometry layer is y {GEOM_Y0} to {GEOM_Y1}, the card "
          f"from y {PAYOFF_Y - 20:.0f} to {PAYOFF_Y + 5 * PAYOFF_PITCH + 20:.0f}; the overlay band y 96 to 130 and the "
          f"caption band y {man['caption_y'] * H:.0f} to {man['caption_y'] * H + 90:.0f} hold no sim drawing")
    assert min(gaps) > 40, "the columns meet on a row"
    assert pay_x0 > 20 and PAY_DY + 20 < WALL_TOP_DY and PAY_DY - 20 > rows_bottom, "the payoff label row collides"
    assert wl_x0 > wall_x + 8 and wl_x1 < W - 8 and WALL_LABEL_DY - 12 > WALL_TOP_DY + 8, "the wall label collides"
    assert WALL_LABEL_DY + 28 + 12 < WALL_HATCH_DY, "the hatch meets the wall label"
    assert BRACKET_DY + 6 < body_top and BRACKET_TEXT_DY + 14 < BRACKET_DY - 6, "the bracket meets the body"
    assert GEOM_Y1 <= man["caption_y"] * H and PAYOFF_Y - 20 > man["caption_y"] * H + 90, "the caption band is not free"
    return ev


def tidy(x: float, eps: float = 1e-9) -> float:
    """Zero for printing when |x| is under eps (the sign of a 1e-12 residue is noise)."""
    return 0.0 if abs(x) < eps else x


def fraction(k: float, e: float) -> str:
    """The closed form v0 (k - e) / (1 + k) as a small fraction when it is one."""
    val = abs(k - e) / (1.0 + k)
    for den in range(1, 50):
        num = round(val * den)
        if abs(num / den - val) < 1e-9:
            return f"{num}/{den}" if num else "0"
    return f"{val:.4f}"


WALL_LABEL = "smooth wall"
START_LABEL = "start line"


def legend_text(man: dict) -> str:
    return f"same speed, same wall, 1/{man['slow']:g} speed"


def clock_text(r: float) -> str:
    return "before the start line" if r < 0.0 else f"{r:.3f} s after the start line"


def label_text(m: str) -> str:
    return "solid ball" if m == "ball" else "thin ring"


def sub_text(m: str, man: dict) -> str:
    return "mass through the middle" if m == "ball" else "all its mass on the rim"


def fixed_text(ev: dict, m: str) -> str:
    return f"slides {ev['runs'][m]['t_slip']:.2f} s after the bounce"


def pay_text(ev: dict, m: str) -> str:
    rn = ev["runs"][m]
    if m == "ball":
        return f"rolls back at {abs(rn['v_end']):.2f} m/s, 3/7"
    return f"stops dead, {rn['d_wall'] * 100:.0f} cm from the wall"


def bracket_text(rn: dict) -> str:
    return f"{rn['d_wall'] * 100:.1f} cm"


def speed_text(v: float, phase: str, v_end: float) -> str:
    if abs(v) < 5e-3:
        return "0.00 m/s, stopped"
    return f"{abs(v):.2f} m/s " + ("toward the wall" if v > 0.0 else "away from the wall")


def spin_text(om: float) -> str:
    return f"spin {abs(om) / (2.0 * math.pi):.1f} turns/s"


def contact_text(s: float, v: float = 1.0) -> str:
    if abs(s) >= 5e-3:
        return f"contact slides {abs(s):.2f} m/s"
    return "contact at rest, rolling" if abs(v) >= 5e-3 else "contact at rest, stopped"


def bracket_text_x(xe: float, wall_x: float, width: float) -> float:
    """Centre of the bracket text: over the bracket, but kept 8 px clear of the wall face."""
    return min((xe + wall_x) / 2.0, wall_x - 8.0 - width / 2.0)


def payoff_lines(man: dict, ev: dict) -> list[str]:
    rb, rr = ev["runs"]["ball"], ev["runs"]["ring"]
    text = man["payoff_text"].format(v_ball=abs(rb["v_end"]), d_ring=rr["d_wall"] * 100, t_ball=rb["t_slip"],
                                     t_ring=rr["t_slip"], d_ball=rb["d_wall"] * 100)
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
        self.lx = float(man["line_x_px"])
        self.S = man["slow"]
        self.P = man["cycle_s"]
        self.P_f = int(round(man["cycle_s"] * self.fps))
        self.c0_f = int(round(man["first_cycle_at"] * self.fps))
        self.ca, self.F = man["cross_at"], man["reset_fade"]
        self.runs = ev["runs"]
        self.r = man["radius_m"]
        self.L = man["wall_m"]
        self.wall_x = self.lx + self.L * self.ppm

    def phase(self, f: int) -> tuple[int, float]:
        k, tau_f = divmod(f - self.c0_f, self.P_f)
        return k, tau_f / self.fps

    def sx(self, x_m: float) -> float:
        return self.lx + x_m * self.ppm

    @staticmethod
    def Lp(x: float, y: float) -> tuple[float, float]:
        """Layer (2x) pixel of a screen point, rounded to 1e-4 px so equal states draw equal pixels."""
        return round(x * SS, 4), round((y - GEOM_Y0) * SS, 4)

    def draw_table(self, d: ImageDraw.ImageDraw, m: str) -> None:
        y0 = BAND_Y[m]
        ys, yb = y0 + FLOOR_DY, y0 + SLAB_DY
        s0, s1 = self.Lp(-12.0, ys), self.Lp(W + 12.0, yb)
        d.rectangle((s0[0], s0[1], s1[0], s1[1]), fill=TABLE)
        t0, t1 = self.Lp(-12.0, ys), self.Lp(W + 12.0, ys)
        d.line((*t0, *t1), fill=TABLE_TOP, width=3 * SS)
        # Distance ticks every 10 cm from the start line to the wall.
        for j in range(0, 11):
            x = self.sx(j * 0.1)
            depth = 14.0 if j % 5 == 0 else 8.0
            d.line((*self.Lp(x, ys + 3), *self.Lp(x, ys + 3 + depth)), fill=TABLE_INK, width=2 * SS)
        # The start line: a gold notch in the surface.
        p0, p1, p2 = self.Lp(self.lx, ys + 3), self.Lp(self.lx - 9, ys + 18), self.Lp(self.lx + 9, ys + 18)
        d.polygon([p0, p1, p2], fill=GOLD)
        # The wall: a block on the table at the right, its face lit.
        w0, w1 = self.Lp(self.wall_x, y0 + WALL_TOP_DY), self.Lp(WALL_X1, ys)
        d.rectangle((w0[0], w0[1], w1[0], w1[1]), fill=WALL)
        f0, f1 = self.Lp(self.wall_x + 1.5, y0 + WALL_TOP_DY), self.Lp(self.wall_x + 1.5, ys)
        d.line((*f0, *f1), fill=WALL_FACE, width=3 * SS)
        for j in range(0, 5):
            yy = y0 + WALL_HATCH_DY + j * 26.0
            d.line((*self.Lp(self.wall_x + 14, yy), *self.Lp(W - 10, yy)), fill=WALL_INK, width=1 * SS)

    def draw_body(self, d: ImageDraw.ImageDraw, m: str, x: float, th: float, a: float) -> None:
        y0 = BAND_Y[m]
        cx, cy = self.sx(x), y0 + FLOOR_DY - self.r * self.ppm
        X, Y = self.Lp(cx, cy)
        R = self.r * self.ppm * SS
        c, sn = math.cos(th), math.sin(th)       # th grows clockwise on screen while the body rolls right
        if m == "ball":
            d.ellipse((X - R, Y - R, X + R, Y + R), fill=blend(CORAL, a), outline=blend(BALL_DARK, a), width=2 * SS)
            d.line((X - R * 0.84 * c, Y - R * 0.84 * sn, X + R * 0.84 * c, Y + R * 0.84 * sn), fill=blend(WHITE, a),
                   width=5 * SS)
            dr = 3.6 * SS
            px, py = X + R * 0.62 * sn, Y - R * 0.62 * c
            d.ellipse((px - dr, py - dr, px + dr, py + dr), fill=blend(WHITE, a))
        else:
            wr = 6 * SS
            d.ellipse((X - R, Y - R, X + R, Y + R), outline=blend(RING, a), width=wr)
            d.ellipse((X - R, Y - R, X + R, Y + R), outline=blend(RING_DARK, a), width=1 * SS)
            Ri = R - wr + 1
            d.line((X - Ri * c, Y - Ri * sn, X + Ri * c, Y + Ri * sn), fill=blend(WHITE, a), width=4 * SS)
            dr = 4.0 * SS
            px, py = X + (R - wr / 2) * sn, Y - (R - wr / 2) * c
            d.ellipse((px - dr, py - dr, px + dr, py + dr), fill=blend(WHITE, a))

    def draw_panel(self, d: ImageDraw.ImageDraw, m: str, f: int) -> dict:
        self.draw_table(d, m)
        k, tau = self.phase(f)
        r = (tau - self.ca) / self.S
        run = self.runs[m]
        st = state_at(run, r)
        y0 = BAND_Y[m]
        ys = y0 + FLOOR_DY
        mark_a = 1.0 if tau < self.P - self.F else max(0.0, (self.P - tau) / self.F)
        on_frame = self.sx(st["x"]) + self.r * self.ppm > -4.0
        # The slip streak: the table under the contact since the hit, in the body's colour.
        if r >= run["t_hit"]:
            x_hit = self.sx(run["x_hit"])
            x_now = self.sx(max(st["x"], run["x_end"]))
            if x_hit - x_now > 0.5:
                s0, s1 = self.Lp(x_now, ys + 3), self.Lp(x_hit, ys + 9)
                d.rectangle((s0[0], s0[1], s1[0], s1[1]), fill=blend(COLOUR[m], 0.8 * mark_a, TABLE))
        # The distance bracket from the near edge at the end of the slip to the wall face.
        ended = r >= run["t_end"]
        if ended and mark_a > 0.0:
            xe = self.sx(run["x_end"] + self.r)
            yb = y0 + BRACKET_DY
            col = blend(GOLD, mark_a)
            d.line((*self.Lp(xe, yb), *self.Lp(self.wall_x, yb)), fill=col, width=2 * SS)
            d.line((*self.Lp(xe, yb - 8), *self.Lp(xe, yb + 8)), fill=col, width=2 * SS)
            d.line((*self.Lp(self.wall_x - 1, yb - 8), *self.Lp(self.wall_x - 1, yb + 8)), fill=col, width=2 * SS)
        if on_frame:
            a = mark_a if (m == "ring" and ended) else 1.0
            if a > 0.0:
                self.draw_body(d, m, st["x"], st["th"], a)
        st.update({"k": k, "tau": tau, "r": r, "ended": ended, "mark_a": mark_a})
        return st

    def spin_icon(self, d: ImageDraw.ImageDraw, cx: float, cy: float, om: float, col) -> None:
        """A small arc with an arrowhead: clockwise for om > 0 (rolling toward the wall), else counterclockwise."""
        rr = 11.0
        box = (cx - rr, cy - rr, cx + rr, cy + rr)
        if om > 0.0:
            d.arc(box, 30, 300, fill=col, width=3)
            ang = math.radians(300)
            tip = (cx + rr * math.cos(ang), cy + rr * math.sin(ang))
            tx, ty = -math.sin(ang), math.cos(ang)       # clockwise tangent on screen
        else:
            d.arc(box, 60, 330, fill=col, width=3)
            ang = math.radians(60)
            tip = (cx + rr * math.cos(ang), cy + rr * math.sin(ang))
            tx, ty = math.sin(ang), -math.cos(ang)       # counterclockwise tangent
        nx, ny = -ty, tx
        head = [(tip[0] + tx * 7, tip[1] + ty * 7), (tip[0] + nx * 5 - tx * 2, tip[1] + ny * 5 - ty * 2),
                (tip[0] - nx * 5 - tx * 2, tip[1] - ny * 5 - ty * 2)]
        d.polygon(head, fill=col)

    def draw_text(self, d: ImageDraw.ImageDraw, states: dict, hud_alpha: float) -> None:
        man, ev = self.man, self.ev
        for m, st in states.items():
            y0 = BAND_Y[m]
            run = self.runs[m]
            d.text((ROW_X0, y0 + LABEL_DY), label_text(m), font=self.font, fill=COLOUR[m], anchor="lm")
            d.text((ROW_X0, y0 + SUB_DY), sub_text(m, man), font=self.font_small, fill=MUTED, anchor="lm")
            if hud_alpha > 0.02:
                d.text((ROW_X0, y0 + FIX_DY), fixed_text(ev, m), font=self.font_small,
                       fill=blend(GOLD, 0.85 * hud_alpha), anchor="lm")
            d.text((ROW_X1, y0 + LABEL_DY), speed_text(st["v"], st["phase"], run["v_end"]), font=self.font,
                   fill=GOLD if st["ended"] else TEXT, anchor="rm")
            spin = spin_text(st["om"])
            d.text((ROW_X1, y0 + SUB_DY), spin, font=self.font_small, fill=COLOUR[m], anchor="rm")
            if abs(st["om"]) > 0.3:
                self.spin_icon(d, ROW_X1 - self.font_small.getlength(spin) - 24, y0 + SUB_DY, st["om"], COLOUR[m])
            sliding = st["phase"] == "slip"
            d.text((ROW_X1, y0 + FIX_DY), contact_text(st["slip"], st["v"]), font=self.font_small,
                   fill=COLOUR[m] if sliding else MUTED, anchor="rm")
            # The wall and the start line labels, the tick labels.
            ys = y0 + FLOOR_DY
            for j, word in enumerate(WALL_LABEL.split()):
                d.text(((self.wall_x + W) / 2, y0 + WALL_LABEL_DY + j * 28), word, font=self.font_tiny, fill=WALL_INK,
                       anchor="mm")
            d.text((self.lx, y0 + TICK_LABEL_DY), START_LABEL, font=self.font_tiny, fill=TABLE_INK, anchor="mm")
            d.text((self.sx(0.5), y0 + TICK_LABEL_DY), "50 cm", font=self.font_tiny, fill=TABLE_INK, anchor="mm")
            d.text((self.sx(1.0), y0 + TICK_LABEL_DY), "1 m", font=self.font_tiny, fill=TABLE_INK, anchor="mm")
            if st["ended"] and st["mark_a"] > 0.0:
                d.text((self.wall_x - 40.0, y0 + PAY_DY), pay_text(ev, m), font=self.font, fill=blend(GOLD, st["mark_a"]),
                       anchor="rm")
                xe = self.sx(run["x_end"] + self.r)
                bw = self.font_small.getlength(bracket_text(run))
                d.text((bracket_text_x(xe, self.wall_x, bw), y0 + BRACKET_TEXT_DY), bracket_text(run),
                       font=self.font_small, fill=blend(GOLD, st["mark_a"]), anchor="mm")
        if hud_alpha > 0.02:
            d.text((W / 2, LEGEND_Y), legend_text(man), font=self.font, fill=blend(TEXT, hud_alpha), anchor="mm")
            d.text((W / 2, CLOCK_Y), clock_text(states["ball"]["r"]), font=self.font_small, fill=blend(MUTED, hud_alpha),
                   anchor="mm")

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
        layer = Image.new("RGB", (W * SS, (GEOM_Y1 - GEOM_Y0) * SS), BG)
        ld = ImageDraw.Draw(layer)
        states = {m: self.draw_panel(ld, m, f) for m in PANELS}
        img.paste(layer.reduce(SS), (0, GEOM_Y0))
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
    man = json.loads((ROOT / "projects/wallbounce/manifest.json").read_text())
    ev = measure(man)
    if "--measure-only" in sys.argv:
        return
    if "--frames" in sys.argv:
        times = [float(v) for v in sys.argv[sys.argv.index("--frames") + 1].split(",")]
        r = Renderer(man, ev)
        (ROOT / "media/wallbounce").mkdir(parents=True, exist_ok=True)
        for tv in times:
            Image.fromarray(r.frame_at(int(round(tv * man["fps"])))).save(ROOT / f"media/wallbounce/smoke-{tv}.png")
        print("smoke frames: " + ", ".join(f"{tv}" for tv in times))
        return
    Renderer(man, ev).render(ROOT / "media/wallbounce/footage.mp4")


if __name__ == "__main__":
    main()
