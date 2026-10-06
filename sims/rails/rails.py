#!/usr/bin/env python3
"""Marble on rails: flat board or two rails, which one gets down first?

Two panels on the same clock, the same slope drawn the same way at the same
scale: a solid marble of radius R (I = k m R^2, k = 2/5; the mass cancels)
rolls without slipping from rest L = 1 m (measured along the slope) down a
slope at alpha = 20 degrees; no air drag, no rolling resistance (chosen).
Top panel: two thin rails whose contact lines are 1.6 R apart, so the
marble touches each rail at the contact radius r = sqrt(R^2 - (0.8 R)^2) =
0.6 R and its centre sits R - r = 0.4 R lower than on a board; rolling
without slipping on the rails means v = omega r, so

    a = g sin alpha / (1 + k R^2 / r^2)

Bottom panel: a flat board, contact radius R, a = g sin alpha / (1 + k).
Both marbles stop on a stop pad at the foot (no bounce; the stop itself is
not modelled). Both runs are integrated by RK4 at steps_per_second on
(position along the slope, spin angle, speed), the arrival at the foot
located by bisection inside the step and checked against the closed forms
and a half-step rerun; the drawing follows the RK4 table. The run repeats
every cycle_s seconds of video with a crossfade back to the held setup;
the cycle divides the scene length, so the scene is exactly periodic and
the last frame equals the first. Shown at 1/slow speed. Deterministic, no
seed.

Measured and printed: the contact radius and the sinking, the acceleration,
time, speed, spin, turns, spin share of the energy and grip needed in each
panel against the closed forms and a half-step rerun, the ratios, where the
rail marble is when the flat marble lands, the table at table_step_s, the
energy balance per kilogram, the description variants (other rail gaps,
other slopes, other marble sizes, a sliding ice cube, Galileo's groove),
the brief's checks, the schedule in video time, the on-screen text widths
and the layout clearances.

usage: rails.py [--measure-only] [--frames t1,t2,...]
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
PLANK = (34, 40, 50)
PLANK_EDGE = (120, 132, 150)
RIM = (96, 108, 126)
STEEL = (170, 180, 196)
RAIL = (62, 70, 84)
PAD = (58, 66, 80)
MARBLE = (222, 226, 234)
MARBLE_EDGE = (150, 158, 172)
STRIPE = (58, 66, 82)

# Layout: overlay at y 96..130 (captions.py), two title rows at y 190/252 for
# the first seconds, then the legend at y 236 and the shared clock at y 290;
# two panels stacked, the rails in the band y 330..880 and the flat board in
# y 880..1430, each drawn at 2x in its own geometry layer; each band has its
# label row 40 px under the band top, its second row at 84 and its third at
# 120 (left column from x 40, right column to x 1040) and the gold event row
# at 172 (right column); the slope descends left to right from slope_x0_px
# at slope_top_dy under the band top to its foot lower right with a stop pad;
# an end-view inset on the right under the event row; captions at caption_y
# 0.75 (y 1440..1530); the six-line card from y 1572 at a 48 px pitch.
LEGEND_Y, CLOCK_Y = 236, 290
TITLE_Y = (190, 252)
SS = 2
PAYOFF_Y, PAYOFF_PITCH = 1572.0, 48
PANELS = ("rails", "flat")
BAND_Y = {"rails": 330, "flat": 880}
BAND_H = 550
LABEL_DY, SUB_DY, FIX_DY, EVENT_DY = 40, 84, 120, 172
ROW_X0, ROW_X1 = 40, 1040
COLOUR = {"rails": CORAL, "flat": TEAL}
HELD, ROLL, DOWN = "held", "rolling", "down"
# Slope coordinates (u down the slope, v up from the surface), px at 1x.
PLANK_T, BASE_T, EXT_TOP, EXT_END = 14.0, 6.0, 30.0, 64.0
RAIL_H, FAR_RAIL_V = 5.0, 9.0
PAD_GAP, PAD_W, PAD_H = 3.0, 12.0, 44.0
PIN_LEN, PIN_W = 24, 6
MARK_V, MARK_V0, MARK_LABEL_V = 64.0, 8.0, 122.0
# The end-view inset (band-local, 1x): the surface level and the drawn radius.
INSET_X, INSET_YS, INSET_R, INSET_HALF = 860.0, 300.0, 44.0, 64.0
INSET_LABEL_DY = 32.0


def blend(col, a: float, base=BG) -> tuple:
    a = max(0.0, min(1.0, a))
    return tuple(int(round(c * a + b * (1 - a))) for c, b in zip(col, base))


# --- measurement --------------------------------------------------------------
def contact_ratio(gap_radii: float) -> float:
    """r / R for rails whose contact lines are gap_radii marble radii apart (1 for a flat board)."""
    h = 0.5 * gap_radii
    assert 0.0 <= h < 1.0, "the rails must be closer than the marble's width"
    return math.sqrt(1.0 - h * h)


def accel(g: float, alpha: float, k: float, rho: float) -> float:
    """a = g sin alpha / (1 + k R^2 / r^2) with rho = r / R."""
    return g * math.sin(alpha) / (1.0 + k / (rho * rho))


def closed_time(L: float, a: float) -> float:
    return math.sqrt(2.0 * L / a)


def rk4_roll(L: float, a: float, r: float, dt: float) -> dict:
    """Integrate s' = v, phi' = v / r, v' = a from rest by classical RK4 at dt until s reaches L; the
    crossing is located by bisection inside the last step. Returns the table (t, s, v, phi) and the
    arrival state."""

    def step(s: float, phi: float, v: float, h: float) -> tuple[float, float, float]:
        k1s, k1p, k1v = v, v / r, a
        v2 = v + 0.5 * h * k1v
        k2s, k2p, k2v = v2, v2 / r, a
        v3 = v + 0.5 * h * k2v
        k3s, k3p, k3v = v3, v3 / r, a
        v4 = v + h * k3v
        k4s, k4p, k4v = v4, v4 / r, a
        return (s + h * (k1s + 2.0 * k2s + 2.0 * k3s + k4s) / 6.0,
                phi + h * (k1p + 2.0 * k2p + 2.0 * k3p + k4p) / 6.0,
                v + h * (k1v + 2.0 * k2v + 2.0 * k3v + k4v) / 6.0)

    ts, st, vt, pt = [0.0], [0.0], [0.0], [0.0]
    s = phi = v = 0.0
    n = 0
    while True:
        sn, pn, vn = step(s, phi, v, dt)
        if sn >= L:
            lo, hi = 0.0, dt
            for _ in range(80):
                mid = 0.5 * (lo + hi)
                sm, _, _ = step(s, phi, v, mid)
                if sm < L:
                    lo = mid
                else:
                    hi = mid
            _, ph, vh = step(s, phi, v, hi)
            t_arr = n * dt + hi
            ts.append(t_arr)
            st.append(L)
            vt.append(vh)
            pt.append(ph)
            n += 1
            break
        n += 1
        s, phi, v = sn, pn, vn
        ts.append(n * dt)
        st.append(s)
        vt.append(v)
        pt.append(phi)
    return {"t": np.array(ts), "s": np.array(st), "v": np.array(vt), "phi": np.array(pt), "t_arr": t_arr,
            "v_arr": vh, "phi_arr": ph, "steps": n, "a": a, "r": r, "L": L}


def state_at(run: dict, rt: float) -> dict:
    """(s, v, phi, phase) rt real seconds after the release; after the arrival the marble rests at the
    foot and the readouts hold the values at the foot (the stop itself is not modelled)."""
    if rt < 0.0:
        return {"s": 0.0, "v": 0.0, "phi": 0.0, "phase": HELD, "t_down": 0.0}
    if rt < run["t_arr"]:
        return {"s": float(np.interp(rt, run["t"], run["s"])), "v": float(np.interp(rt, run["t"], run["v"])),
                "phi": float(np.interp(rt, run["t"], run["phi"])), "phase": ROLL, "t_down": 0.0}
    return {"s": run["L"], "v": run["v_arr"], "phi": run["phi_arr"], "phase": DOWN, "t_down": rt - run["t_arr"]}


def panel_numbers(g: float, alpha: float, k: float, R: float, L: float, gap: float) -> dict:
    rho = contact_ratio(gap)
    r = rho * R
    a = accel(g, alpha, k, rho)
    t = closed_time(L, a)
    v = a * t
    omega = v / r
    return {"gap": gap, "rho": rho, "r": r, "sunk": R - r, "a": a, "t": t, "v": v, "omega": omega,
            "turns_s": omega / (2.0 * math.pi), "turns": L / (2.0 * math.pi * r),
            "grip": k * a / (rho * g * math.cos(alpha)), "spin_share": (k / (rho * rho)) / (1.0 + k / (rho * rho)),
            "e_trans": 0.5 * v * v, "e_spin": 0.5 * k * (omega * R) ** 2}


def measure(man: dict) -> dict:
    g, R, k, L = man["g"], man["marble_radius_m"], man["k_inertia"], man["slope_m"]
    alpha = math.radians(man["slope_deg"])
    gap = man["rail_gap_radii"]
    dt = 1.0 / man["steps_per_second"]
    S, P, D, fps, F, pa = man["slow"], man["cycle_s"], man["scene_duration"], man["fps"], man["reset_fade"], man["release_at"]
    cycles = D / P
    assert abs(cycles - round(cycles)) < 1e-9, "the cycle must divide the scene length"
    for key in ("cycle_s", "release_at", "first_cycle_at", "reset_fade"):
        assert abs(man[key] * fps - round(man[key] * fps)) < 1e-9, f"{key} must be a whole number of frames"
    ppm = float(man["px_per_m"])
    Rd = float(man["marble_px"])
    gaps = {"rails": gap, "flat": 0.0}
    cf = {m: panel_numbers(g, alpha, k, R, L, gaps[m]) for m in PANELS}
    print(f"setup: side view, two panels on one clock, the same slope drawn the same way at the same scale: a solid "
          f"marble of radius R = {R * 100:g} cm ({R * 200:g} cm across; I = k m R^2 with k = {k:g}; the mass cancels) rolls "
          f"without slipping from rest {L:g} m (measured along the slope) down a slope at {man['slope_deg']:g} degrees; "
          f"no air drag and no rolling resistance (chosen); g = {g:g} m/s^2; top panel two thin rails whose contact lines "
          f"are {gap:g} R = {gap * R * 100:g} cm apart, bottom panel a flat board; both marbles stop on a stop pad at the "
          f"foot (no bounce; the stop itself is not modelled); both panels integrated by classical RK4 at "
          f"{man['steps_per_second']} steps per second (dt = {dt:.0e} s) on the position along the slope, the spin angle "
          f"and the speed, the arrival at the foot located by bisection inside the step, checked against the closed forms "
          f"and a half-step rerun; shown at 1/{S:g} speed on a {P:g} s cycle ({P * fps:.0f} frames) with the release "
          f"{pa:g} s into the cycle, {cycles:.0f} cycles in {D:g} s; drawn at {ppm:g} px per metre along the slope "
          f"({ppm * math.cos(alpha):.0f} px of run, {ppm * math.sin(alpha):.0f} px of rise); the marble is drawn larger "
          f"than life, a drawn radius of {Rd:g} px against the model's {R * 100:g} cm = {R * ppm:.1f} px, and the drawn "
          f"marble rolls without slipping at its drawn size (its stripe turns {1.0 / cf['rails']['rho']:.3f} times faster "
          f"on the rails, as the model's spin does); the readouts are the model's; deterministic, no seed")
    runs, half = {}, {}
    for m in PANELS:
        c = cf[m]
        runs[m] = rk4_roll(L, c["a"], c["r"], dt)
        half[m] = rk4_roll(L, c["a"], c["r"], 0.5 * dt)
    for m, name in (("rails", "rails (top panel)"), ("flat", "flat board (bottom panel)")):
        c, r_, h_ = cf[m], runs[m], half[m]
        kk = k / (c["rho"] ** 2)
        print(f"{name}: contact lines {c['gap']:g} R apart, so the marble touches at the contact radius r = sqrt(R^2 - "
              f"({0.5 * c['gap']:g} R)^2) = {c['rho']:.4f} R = {c['r'] * 1000:.1f} mm and its centre sits {c['sunk'] * 1000:.2f} mm "
              f"lower than on a board; rolling without slipping means v = omega r, so a = g sin a / (1 + k R^2 / r^2) = "
              f"g sin a / (1 + {kk:.4f}) = {c['a']:.4f} m/s^2; RK4 from rest: {L:g} m in {r_['t_arr']:.6f} s = {r_['t_arr']:.4f} s "
              f"at {r_['v_arr']:.6f} m/s = {r_['v_arr']:.4f} m/s (closed form sqrt(2 L / a) = {c['t']:.6f} s, a t = {c['v']:.6f} "
              f"m/s; diffs {r_['t_arr'] - c['t']:+.1e} s, {r_['v_arr'] - c['v']:+.1e} m/s), {r_['steps']} steps; the position "
              f"stays within {float(np.max(np.abs(r_['s'] - 0.5 * c['a'] * r_['t'] ** 2))):.1e} m of a t^2 / 2 over the run; "
              f"half-step rerun (dt = {0.5 * dt:.0e} s): {h_['t_arr']:.9f} s ({h_['t_arr'] - r_['t_arr']:+.1e} s) at "
              f"{h_['v_arr']:.9f} m/s ({h_['v_arr'] - r_['v_arr']:+.1e} m/s); spin at the bottom omega = v / r = "
              f"{c['omega']:.1f} rad/s = {c['turns_s']:.1f} turns per second (RK4 spin angle {r_['phi_arr']:.4f} rad = "
              f"{r_['phi_arr'] / (2.0 * math.pi):.2f} turns over the metre; closed L / (2 pi r) = {c['turns']:.2f}), the spin "
              f"share of the energy k R^2 / r^2 / (1 + k R^2 / r^2) = {c['spin_share']:.4f}, grip needed (friction over the "
              f"contact normal forces, k (R / r) a / (g cos a)) {c['grip']:.4f}")
        assert abs(r_["t_arr"] - c["t"]) < 1e-7 and abs(h_["t_arr"] - r_["t_arr"]) < 1e-9
    rr, rf = runs["rails"], runs["flat"]
    cr, cfl = cf["rails"], cf["flat"]
    a_ratio = cfl["a"] / cr["a"]
    t_ratio = rr["t_arr"] / rf["t_arr"]
    closed_ratio = (1.0 + k / cr["rho"] ** 2) / (1.0 + k)
    margin = rr["t_arr"] - rf["t_arr"]
    s_mark = float(np.interp(rf["t_arr"], rr["t"], rr["s"]))
    v_mark = float(np.interp(rf["t_arr"], rr["t"], rr["v"]))
    short = L - s_mark
    print(f"flat against rails: a ratio {a_ratio:.4f}, time ratio {t_ratio:.4f} (closed (1 + k / {cr['rho'] ** 2:.2f}) / (1 + k) = "
          f"{closed_ratio:.4f}, sqrt {math.sqrt(closed_ratio):.4f}); margin {margin:.4f} s; speed at the bottom {rf['v_arr']:.4f} "
          f"against {rr['v_arr']:.4f} m/s; the rail marble must spin {1.0 / cr['rho']:.4f} times faster for the same speed")
    print(f"rail marble when the flat marble reaches the bottom (t {rf['t_arr']:.4f} s): {s_mark:.4f} m down at {v_mark:.4f} "
          f"m/s, {short * 100:.1f} cm short = {short * 100:.0f} cm short (closed a_r t_f^2 / 2 = {0.5 * cr['a'] * rf['t_arr'] ** 2:.4f} m)")
    t_half = float(np.interp(0.5 * L, rr["s"], rr["t"]))
    print(f"flat marble when the rail marble is halfway: t {t_half:.4f} s, flat at {float(np.interp(t_half, rf['t'], rf['s'])):.4f} m")
    # The table at table_step_s plus the two arrivals.
    tab_ts = [j * man["table_step_s"] for j in range(1, int(math.floor(rr["t_arr"] / man["table_step_s"] + 1e-9)) + 1)]
    tab_ts = sorted(set(tab_ts + [rf["t_arr"], 1.0, rr["t_arr"]]))
    table = []
    for tt in tab_ts:
        sf, sr = state_at(rf, tt), state_at(rr, tt)
        table.append((tt, sf["s"], sf["v"], sr["s"], sr["v"]))
        print(f"  t {tt:.4f} s: flat {sf['s']:.4f} m (v {sf['v']:.4f}), rails {sr['s']:.4f} m (v {sr['v']:.4f})")
    # Energy per kilogram.
    drop = g * L * math.sin(alpha)
    print(f"energy per kg at the bottom: potential drop g L sin a = {drop:.4f} J/kg; flat: translation {cfl['e_trans']:.4f} + "
          f"spin {cfl['e_spin']:.4f} = {cfl['e_trans'] + cfl['e_spin']:.4f}; rails: translation {cr['e_trans']:.4f} + spin "
          f"{cr['e_spin']:.4f} = {cr['e_trans'] + cr['e_spin']:.4f}; spin share {cfl['spin_share'] * 100:.1f} percent flat against "
          f"{cr['spin_share'] * 100:.1f} percent on the rails; the RK4 speeds give {0.5 * rf['v_arr'] ** 2 * (1.0 + k):.4f} and "
          f"{0.5 * rr['v_arr'] ** 2 * (1.0 + k / cr['rho'] ** 2):.4f} J/kg")
    assert abs(cfl["e_trans"] + cfl["e_spin"] - drop) < 1e-9 and abs(cr["e_trans"] + cr["e_spin"] - drop) < 1e-9
    print(f"no-slip condition: the friction needed is k (R / r) m a and the contact normal forces add to m g cos a (R / r), "
          f"so the grip needed is {cfl['grip']:.4f} on the board and {cr['grip']:.4f} on the rails (a chosen grip of 0.3 or "
          f"more holds both)")
    ev: dict = {"cf": cf, "runs": runs, "a_ratio": a_ratio, "t_ratio": t_ratio, "margin": margin, "s_mark": s_mark,
                "short": short, "table": table, "drop": drop}
    # For the description.
    descr = []
    ev["gaps"] = {}
    for g2 in man["description_gaps_radii"]:
        c2 = panel_numbers(g, alpha, k, R, L, g2)
        r2 = rk4_roll(L, c2["a"], c2["r"], dt)
        ev["gaps"][g2] = r2["t_arr"]
        descr.append(f"rails {g2:g} R apart (contact radius {c2['rho']:.3f} R = {c2['r'] * 1000:.1f} mm, centre sunk "
                     f"{c2['sunk'] * 1000:.2f} mm): a {c2['a']:.4f} m/s^2, {L:g} m in {r2['t_arr']:.4f} s (closed {c2['t']:.4f} s) at "
                     f"{r2['v_arr']:.4f} m/s, spin {c2['turns_s']:.1f} turns/s ({c2['turns']:.1f} turns over the metre), grip needed "
                     f"{c2['grip']:.4f}, spin share {c2['spin_share']:.4f}")
    ev["slopes"] = {}
    for deg in man["description_slopes_deg"]:
        al2 = math.radians(deg)
        tf2 = rk4_roll(L, accel(g, al2, k, 1.0), R, dt)["t_arr"]
        tr2 = rk4_roll(L, accel(g, al2, k, cr["rho"]), cr["r"], dt)["t_arr"]
        ev["slopes"][deg] = (tf2, tr2)
        descr.append(f"{deg:g} degree slope: flat {tf2:.4f} s, rails {tr2:.4f} s (ratio {tr2 / tf2:.4f}, the same)")
    for R2 in man["description_radii_m"]:
        c_f = panel_numbers(g, alpha, k, R2, L, 0.0)
        c_r = panel_numbers(g, alpha, k, R2, L, gap)
        tf2 = rk4_roll(L, c_f["a"], c_f["r"], dt)["t_arr"]
        tr2 = rk4_roll(L, c_r["a"], c_r["r"], dt)["t_arr"]
        assert abs(tf2 - rf["t_arr"]) < 1e-9 and abs(tr2 - rr["t_arr"]) < 1e-9, "the times depend on the radius"
        descr.append(f"marble radius {R2 * 1000:g} mm, rails {gap:g} R apart ({gap * R2 * 1000:g} mm): times unchanged "
                     f"({tf2:.4f} and {tr2:.4f} s; the ratio depends only on the gap in radii; spin {c_f['turns_s']:.1f} "
                     f"against {c_r['turns_s']:.1f} turns/s)")
    a_ice = g * math.sin(alpha)
    t_ice = rk4_roll(L, a_ice, 1.0, dt)["t_arr"]
    ev["t_ice"] = t_ice
    descr.append(f"a sliding ice cube (no spin, no friction) for reference: a = g sin a = {a_ice:.4f} m/s^2, {L:g} m in "
                 f"{t_ice:.4f} s (closed {closed_time(L, a_ice):.4f} s)")
    gw, gr = man["galileo_groove_punti"], man["galileo_ball_radius_punti"]
    rho_g = contact_ratio(gw / gr)
    fac_g = (1.0 + k) / (1.0 + k / rho_g ** 2)
    ev["galileo_pct"] = (1.0 - fac_g) * 100.0
    ev["rho_g"] = rho_g
    descr.append(f"Galileo's groove {gw:g} punti wide for a ball of radius {gr:g} punti: contact radius {rho_g:.4f} R, acceleration "
                 f"x {fac_g:.4f} ({(1.0 - fac_g) * 100:.2f} percent less than on a flat board; TPT 2024 says 5.75), "
                 f"time x {1.0 / math.sqrt(fac_g):.4f}")
    print("for the description: " + "; ".join(descr))
    # The brief's checks.
    checks: list[tuple[str, float, float, float]] = [
        ("flat time (s)", rf["t_arr"], 0.9137, 6e-5), ("flat speed (m/s)", rf["v_arr"], 2.1890, 6e-5),
        ("flat a (m/s^2)", cfl["a"], 2.3959, 6e-5),
        ("rails time (s)", rr["t_arr"], 1.1220, 6e-5), ("rails speed (m/s)", rr["v_arr"], 1.7826, 6e-5),
        ("rails a (m/s^2)", cr["a"], 1.5888, 6e-5),
        ("a ratio", a_ratio, 1.5079, 6e-5), ("time ratio", t_ratio, 1.2280, 6e-5),
        ("rail marble at the flat landing (m)", s_mark, 0.6632, 6e-5), ("short (cm)", short * 100, 33.7, 6e-2),
        ("flat spin (rad/s)", cfl["omega"], 218.9, 6e-2), ("rails spin (rad/s)", cr["omega"], 297.1, 6e-2),
        ("flat turns/s", cfl["turns_s"], 34.8, 6e-2), ("rails turns/s", cr["turns_s"], 47.3, 6e-2),
        ("flat turns over the metre", cfl["turns"], 15.9, 6e-2), ("rails turns over the metre", cr["turns"], 26.5, 6e-2),
        ("flat spin share", cfl["spin_share"], 0.2857, 6e-5), ("rails spin share", cr["spin_share"], 0.5263, 6e-5),
        ("flat grip needed", cfl["grip"], 0.1040, 6e-5), ("rails grip needed", cr["grip"], 0.1149, 6e-5),
        ("contact radius (R)", cr["rho"], 0.6, 1e-9), ("centre sunk (mm)", cr["sunk"] * 1000, 4.0, 1e-9),
        ("potential drop (J/kg)", drop, 3.3542, 6e-5), ("flat translation (J/kg)", cfl["e_trans"], 2.3959, 6e-5),
        ("flat spin energy (J/kg)", cfl["e_spin"], 0.9583, 6e-5), ("rails translation (J/kg)", cr["e_trans"], 1.5888, 6e-5),
        ("rails spin energy (J/kg)", cr["e_spin"], 1.7654, 6e-5),
        ("ice cube (s)", t_ice, 0.7722, 6e-5), ("Galileo contact (R)", rho_g, 0.9052, 6e-5),
        ("Galileo percent less", ev["galileo_pct"], 5.93, 6e-3),
    ]
    want_tab = {0.2: (0.0479, 0.0318), 0.4: (0.1917, 0.1271), 0.6: (0.4313, 0.2860), 0.8: (0.7667, 0.5084)}
    for tt, sf, _, sr, _ in table:
        for wt, (wf, wr) in want_tab.items():
            if abs(tt - wt) < 1e-9:
                checks += [(f"table {wt:g} s flat (m)", sf, wf, 6e-5), (f"table {wt:g} s rails (m)", sr, wr, 6e-5)]
    for g2, want in ((1.2, 0.9843), (1.8, 1.3607)):
        if g2 in ev["gaps"]:
            checks.append((f"rails {g2:g} R apart (s)", ev["gaps"][g2], want, 6e-5))
    for deg, (wf, wr) in ((10.0, (1.2823, 1.5746)), (30.0, (0.7557, 0.9279))):
        if deg in ev["slopes"]:
            checks += [(f"{deg:g} deg flat (s)", ev["slopes"][deg][0], wf, 6e-5), (f"{deg:g} deg rails (s)", ev["slopes"][deg][1], wr, 6e-5)]
    fails = 0
    out = []
    for name, got, want, tol in checks:
        ok = abs(got - want) <= tol
        fails += 0 if ok else 1
        out.append(f"{name}: brief {want:g}, sim {got:.6g}, diff {got - want:+.1e}: {'ok' if ok else 'FAIL'}")
    print(f"checks against the brief ({len(checks)} checks, {fails} failed): " + "; ".join(out))
    ev["check_fails"] = fails
    # The schedule in video time.
    t0 = man["first_cycle_at"]
    k0 = math.ceil((0.0 - t0) / P - 1e-9) - 1
    k1 = math.floor((D - t0) / P - 1e-9)
    starts = [t0 + kk * P for kk in range(k0, k1 + 1)]
    ev["cycles"] = int(round(cycles))

    def lst(off_: float) -> str:
        return ", ".join(f"{st + off_:.2f}" for st in starts if 0.0 <= st + off_ < D)

    vt = lambda real: pa + real * S   # noqa: E731  video time after the cycle start
    assert vt(rr["t_arr"]) + man["mark_fade_s"] < P - F, "the rail marble is still rolling at the reset fade"
    tau0 = (0.0 - t0) % P
    r0 = (tau0 - pa) / S
    st0 = {m: state_at(runs[m], r0) for m in PANELS}
    print(f"schedule (video time, 1/{S:g} speed): cycles of {P:g} s start at " + ", ".join(f"{st:.2f}" for st in starts)
          + f" s (the first {-t0:.2f} s before the first frame); both marbles are let go {pa:g} s into each cycle at {lst(pa)} s "
          f"(the stop pins fade over {man['pin_fade_s']:g} s); the flat marble reaches the foot {S * rf['t_arr']:.2f} s after the "
          f"release at {lst(vt(rf['t_arr']))} s ({vt(rf['t_arr']):.3f} s into the cycle; its event row lights and the gold "
          f"'{short * 100:.0f} cm short' mark fades in over {man['mark_fade_s']:g} s in the rails band); the rail marble reaches "
          f"the foot {S * rr['t_arr']:.2f} s after the release at {lst(vt(rr['t_arr']))} s ({vt(rr['t_arr']):.3f} s into the cycle; "
          f"its event row lights), {S * margin:.2f} s of video after the flat one; the reset crossfade runs over the last {F:g} s "
          f"of each cycle (from {lst(P - F)} s; the readouts out over its first half and in over its second); on the first frame "
          f"the cycle is {tau0:.2f} s in ({r0:.3f} s real after the release: the rail marble {st0['rails']['phase']} at "
          f"{st0['rails']['s'] * 100:.1f} cm, the flat marble {st0['flat']['phase']} at {st0['flat']['s'] * 100:.1f} cm); title until "
          f"{man['title_until']:g} s; payoff card from {man['payoff_t']:g} s; the title fades back in over the last "
          f"{man['loop_fade']:g} s and the last frame repeats the first (the scene is periodic: {D:g} s holds exactly "
          f"{cycles:.0f} cycles)")
    # Text widths.
    font = os.environ["SEED_ZERO_FONT"]
    f24, f28, f34, f40, f56 = (ImageFont.truetype(font, n) for n in (24, 28, 34, 40, 56))
    widths = {"overlay@34": (f34, man["overlay"])}
    for j, line in enumerate(man["title"].split("|")):
        widths[f"title line {j + 1}@56"] = (f56, line)
    widths["legend@40"] = (f40, legend_text(man))
    widths["clock@28"] = (f28, clock_text(rr["t_arr"]))
    widths["clock held@28"] = (f28, clock_text(-1.0))
    for m in PANELS:
        widths[f"label {m}@40"] = (f40, label_text(m))
        widths[f"down {m}@28"] = (f28, down_text(L))
        widths[f"contact {m}@28"] = (f28, contact_text(cf[m], R))
        widths[f"speed {m}@28"] = (f28, speed_text(runs[m]["v_arr"]))
        widths[f"spin {m}@28"] = (f28, spin_text(cf[m]["turns_s"]))
        widths[f"event {m}@40"] = (f40, event_text(ev, m))
        widths[f"inset r {m}@24"] = (f24, inset_r_text(m, cf[m]))
    widths["inset label@24"] = (f24, inset_label_text())
    widths["mark@24"] = (f24, mark_text(ev))
    for j, line in enumerate(payoff_lines(man, ev)):
        widths[f"payoff line {j + 1}@40"] = (f40, line)
    print("text widths (the on-screen strings verbatim): " + ", ".join(f"{kk} {f.getlength(s):.0f} px '{s}'" for kk, (f, s) in widths.items()))
    assert all(f.getlength(s) < 950 for f, s in widths.values()), "a text line is wider than 950 px"
    assert len(payoff_lines(man, ev)) <= 6, "the card has more than six lines"
    assert len(man["title"].split("|")) <= len(TITLE_Y), "too many title rows"
    # Layout checks.
    geo = Geometry(man)
    left = ROW_X0 + max(max(f40.getlength(label_text(m)), f28.getlength(down_text(L)), f28.getlength(contact_text(cf[m], R)))
                        for m in PANELS)
    right = ROW_X1 - max(max(f28.getlength(speed_text(runs[m]["v_arr"])), f28.getlength(spin_text(cf[m]["turns_s"]))) for m in PANELS)
    rows_bottom = FIX_DY + 16
    ev_w = {m: f40.getlength(event_text(ev, m)) for m in PANELS}
    ev_x0 = ROW_X1 - max(ev_w.values())
    top_pt = geo.slope_xy(0.0, 0.0, 0.0)
    foot = geo.slope_xy(L, 0.0, 0.0)
    end_lo = geo.slope_xy(L, EXT_END, -PLANK_T)
    pad_hi = geo.slope_xy(L, Rd + PAD_GAP + PAD_W, PAD_H)
    pad_lo = geo.slope_xy(L, Rd + PAD_GAP + PAD_W, 0.0)
    m_top = {m: geo.slope_xy(0.0, 0.0, geo.centre_v[m] + Rd) for m in PANELS}        # the marble's highest pixel at the start
    m_far = {m: geo.slope_xy(L, Rd, geo.centre_v[m]) for m in PANELS}                  # its downhill extreme at the foot
    pin_top = geo.slope_xy(0.0, Rd + PAD_GAP + PIN_W / 2.0, PIN_LEN)
    mark_lbl = geo.slope_xy(0.5 * (s_mark + L), 0.0, MARK_LABEL_V)
    mark_top = geo.slope_xy(s_mark, 0.0, MARK_V + 6.0)
    mark_w = f24.getlength(mark_text(ev))
    ins_top = min(INSET_YS - geo.inset_centre_dy(m) - INSET_R for m in PANELS)
    ins_bottom = INSET_YS + INSET_LABEL_DY + 14
    ins_r_x1 = INSET_X + INSET_R + 14 + max(f24.getlength(inset_r_text(m, cf[m])) for m in PANELS)
    print(f"row check: the left column ends at x {left:.0f} px, the right column starts at x {right:.0f} px; both end "
          f"{rows_bottom} px under the band top; the event rows span {EVENT_DY - 20} to {EVENT_DY + 20} px under the band top, "
          f"right-aligned at x {ROW_X1} from x {ev_x0:.0f} (widest {max(ev_w.values()):.0f} px); the slope's start contact at x "
          f"{top_pt[0]:.1f}, {top_pt[1]:.1f} px under the band top, the foot (s = {L:g} m) at x {foot[0]:.1f}, {foot[1]:.1f} px, the "
          f"plank's lower end corner at x {end_lo[0]:.1f}, {end_lo[1]:.1f} px, the stop pad's far corners at x {pad_hi[0]:.1f}, "
          f"{pad_hi[1]:.1f} and {pad_lo[0]:.1f}, {pad_lo[1]:.1f} px; the marble's highest pixel at the start {m_top['rails'][1]:.1f} "
          f"(rails) and {m_top['flat'][1]:.1f} (flat) px under the band top, its downhill extreme at the foot x {m_far['rails'][0]:.1f} "
          f"and {m_far['flat'][0]:.1f} px; the stop pin's top at {pin_top[1]:.1f} px; the gold mark's dashed line rises to "
          f"{mark_top[1]:.1f} px and its label is centred at x {mark_lbl[0]:.0f}, {mark_lbl[1]:.0f} px ({mark_w:.0f} px wide); the "
          f"end-view inset spans {ins_top:.1f} to {ins_bottom:.1f} px under the band top and x {INSET_X - INSET_HALF:.0f} to "
          f"{ins_r_x1:.0f} px; each band is {BAND_H} px tall (y {BAND_Y['rails']} to {BAND_Y['rails'] + BAND_H} and {BAND_Y['flat']} "
          f"to {BAND_Y['flat'] + BAND_H}); the caption band starts at y {int(man['caption_y'] * H)}; the title rows end at y "
          f"{TITLE_Y[len(man['title'].split('|')) - 1] + 28} and the overlay band ends at y 130")
    assert right - left > 40, "the columns meet"
    assert all(m_top[m][1] > rows_bottom + 10 for m in PANELS), "the marble meets the text rows"
    assert pin_top[1] > rows_bottom + 10, "the stop pin meets the text rows"
    assert end_lo[1] < BAND_H - 2 and pad_lo[1] < BAND_H - 2 and foot[1] + PLANK_T < BAND_H - 2, "the slope leaves the band"
    assert pad_hi[0] < INSET_X - INSET_HALF - 20, "the stop pad meets the inset"
    assert mark_lbl[0] + mark_w / 2.0 < INSET_X - INSET_HALF - 20 and mark_lbl[1] - 14 > rows_bottom + 10, "the mark label does not fit"
    assert mark_lbl[0] + mark_w / 2.0 < ev_x0 - 10 or mark_lbl[1] - 14 > EVENT_DY + 30, "the mark label meets the event row"
    assert ins_top > EVENT_DY + 30 and ins_bottom < BAND_H - 10 and ins_r_x1 < W - 20, "the inset does not fit"
    assert TITLE_Y[len(man["title"].split("|")) - 1] + 28 <= BAND_Y["rails"], "the title reaches the top band"
    assert BAND_Y["flat"] + BAND_H <= int(man["caption_y"] * H), "the bottom band reaches the caption band"
    assert PAYOFF_Y - 20 > int(man["caption_y"] * H) + 90, "the card meets the caption band"
    return ev


def legend_text(man: dict) -> str:
    return f"same marble, same slope, 1/{man['slow']:g} speed"


def clock_text(r: float) -> str:
    return "held, at rest" if r < 0.0 else f"{r:.3f} s after the release"


def label_text(m: str) -> str:
    return "on two rails" if m == "rails" else "on a flat board"


def down_text(s: float) -> str:
    return f"{s:.2f} m down the slope"


def contact_text(c: dict, R: float) -> str:
    if c["gap"] == 0.0:
        return f"touches at R = {R * 1000:.0f} mm"
    return f"touches at {c['rho']:.1f} R = {c['r'] * 1000:.0f} mm"


def speed_text(v: float) -> str:
    return f"speed {v:.2f} m/s"


def spin_text(turns_s: float) -> str:
    return f"spin {turns_s:.1f} turns/s"


def event_text(ev: dict, m: str) -> str:
    t = ev["runs"][m]["t_arr"]
    return f"rails: down in {t:.3f} s" if m == "rails" else f"flat board: down in {t:.3f} s"


def mark_text(ev: dict) -> str:
    return f"{ev['short'] * 100:.0f} cm short"


def inset_r_text(m: str, c: dict) -> str:
    return "r = R" if m == "flat" else f"r = {c['rho']:.1f} R"


def inset_label_text() -> str:
    return "end view"


def payoff_lines(man: dict, ev: dict) -> list[str]:
    cf, runs = ev["cf"], ev["runs"]
    text = man["payoff_text"].format(
        tf=runs["flat"]["t_arr"], tr=runs["rails"]["t_arr"], short=ev["short"] * 100.0,
        sf=cf["flat"]["spin_share"] * 100.0, sr=cf["rails"]["spin_share"] * 100.0,
        t12=ev["gaps"][1.2], t18=ev["gaps"][1.8], ratio=ev["t_ratio"])
    return [s.strip() for s in text.split("|")]


# --- geometry -----------------------------------------------------------------
class Geometry:
    """Band-local pixel geometry (1x): the slope surface point s metres from the start, slope coordinates
    (u down the slope, v up from the surface, px) and the drawn marble's centre height in each panel."""

    def __init__(self, man: dict):
        self.ppm = float(man["px_per_m"])
        self.a = math.radians(man["slope_deg"])
        self.sa, self.ca = math.sin(self.a), math.cos(self.a)
        self.x0, self.y0 = float(man["slope_x0_px"]), float(man["slope_top_dy"])   # the start contact point (s = 0)
        self.L = man["slope_m"]
        self.Rd = float(man["marble_px"])
        self.rho = contact_ratio(man["rail_gap_radii"])
        # The drawn centre height over the surface line: on the board Rd; on the rails the rail top plus
        # the drawn contact radius (the marble sinks by (1 - rho) Rd between the rails).
        self.centre_v = {"flat": self.Rd, "rails": RAIL_H + self.rho * self.Rd}
        self.draw_r = {"flat": self.Rd, "rails": self.rho * self.Rd}   # the drawn rolling radius

    def slope_xy(self, s: float, u: float, v: float) -> tuple[float, float]:
        sp = s * self.ppm + u
        return self.x0 + sp * self.ca + v * self.sa, self.y0 + sp * self.sa - v * self.ca

    def inset_centre_dy(self, m: str) -> float:
        """The inset marble's centre height over the inset surface level."""
        return INSET_R if m == "flat" else RAIL_H + self.rho * INSET_R


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
        self.geo = Geometry(man)
        self.S = man["slow"]
        self.P = man["cycle_s"]
        self.P_f = int(round(man["cycle_s"] * self.fps))
        self.c0_f = int(round(man["first_cycle_at"] * self.fps))
        self.pa, self.F = man["release_at"], man["reset_fade"]
        self.runs = ev["runs"]
        self.L = man["slope_m"]
        self.R = man["marble_radius_m"]

    def phase(self, f: int) -> tuple[int, float]:
        k, tau_f = divmod(f - self.c0_f, self.P_f)
        return k, tau_f / self.fps

    @staticmethod
    def L_(x: float, y: float) -> tuple[float, float]:
        """Layer (2x) pixel of a band-local point, rounded to 1e-4 px so equal states draw equal pixels."""
        return round(x * SS, 4), round(y * SS, 4)

    def P_(self, s: float, u: float, v: float) -> tuple[float, float]:
        return self.L_(*self.geo.slope_xy(s, u, v))

    @staticmethod
    def dashed(d: ImageDraw.ImageDraw, a: tuple, b: tuple, col, dash: float, gap: float, width: int) -> None:
        ax, ay = a
        bx, by = b
        length = math.hypot(bx - ax, by - ay)
        if length < 1e-6:
            return
        ux, uy = (bx - ax) / length, (by - ay) / length
        s = 0.0
        while s < length:
            e = min(length, s + dash)
            d.line((ax + ux * s, ay + uy * s, ax + ux * e, ay + uy * e), fill=col, width=width)
            s = e + gap

    def draw_slope(self, d: ImageDraw.ImageDraw, m: str) -> None:
        L = self.L
        s_top = -EXT_TOP / self.geo.ppm
        s_end = L + EXT_END / self.geo.ppm
        th = PLANK_T if m == "flat" else BASE_T     # the board, or the thin base the rails stand on
        poly = [self.P_(s_top, 0.0, 0.0), self.P_(s_end, 0.0, 0.0), self.P_(s_end, 0.0, -th), self.P_(s_top, 0.0, -th)]
        d.polygon(poly, fill=PLANK, outline=RIM, width=2 * SS)
        if m == "flat":
            d.line((*self.P_(s_top, 0.0, 0.0), *self.P_(s_end, 0.0, 0.0)), fill=PLANK_EDGE, width=3 * SS)
        else:
            # The far rail, seen behind the marble: a thin bright line a little above the near rail's top.
            d.line((*self.P_(s_top, 0.0, FAR_RAIL_V), *self.P_(s_end, 0.0, FAR_RAIL_V)), fill=STEEL, width=2 * SS)
        # The stop pad at the foot, just downhill of the marble's resting place.
        u0 = self.geo.Rd + PAD_GAP
        pad = [self.P_(L, u0, 0.0), self.P_(L, u0 + PAD_W, 0.0), self.P_(L, u0 + PAD_W, PAD_H), self.P_(L, u0, PAD_H)]
        d.polygon(pad, fill=PAD, outline=RIM, width=2 * SS)

    def draw_rails(self, d: ImageDraw.ImageDraw) -> None:
        """The near rail as a thin double line over the marble: a dark foot band and a bright top edge."""
        s_top = -EXT_TOP / self.geo.ppm
        s_end = self.L + EXT_END / self.geo.ppm
        band = [self.P_(s_top, 0.0, RAIL_H), self.P_(s_end, 0.0, RAIL_H), self.P_(s_end, 0.0, 0.0), self.P_(s_top, 0.0, 0.0)]
        d.polygon(band, fill=RAIL)
        d.line((*self.P_(s_top, 0.0, RAIL_H), *self.P_(s_end, 0.0, RAIL_H)), fill=STEEL, width=2 * SS)
        d.line((*self.P_(s_top, 0.0, 0.5), *self.P_(s_end, 0.0, 0.5)), fill=RIM, width=1 * SS)

    def draw_pin(self, d: ImageDraw.ImageDraw, tv: float) -> None:
        """A stop pin just downhill of the held marble, normal to the slope, fading after the release."""
        a = 1.0 if tv < 0.0 else max(0.0, 1.0 - tv / self.man["pin_fade_s"])
        if a <= 0.0:
            return
        u = self.geo.Rd + PAD_GAP + PIN_W / 2.0
        d.line((*self.P_(0.0, u, 0.0), *self.P_(0.0, u, PIN_LEN)), fill=blend(GOLD, a), width=PIN_W * SS)

    def draw_mark(self, d: ImageDraw.ImageDraw, a: float) -> None:
        """Rails band after the flat landing: a dashed gold tick where the rail marble was at that instant,
        one at the foot, and a dashed gold line along the slope between them (the label is drawn at 1x)."""
        s_mark, L = self.ev["s_mark"], self.L
        col = blend(GOLD, a)
        for s_t in (s_mark, L):
            self.dashed(d, self.P_(s_t, 0.0, MARK_V0), self.P_(s_t, 0.0, MARK_V + 6.0), col, 6 * SS, 4 * SS, 3 * SS)
        self.dashed(d, self.P_(s_mark, 0.0, MARK_V), self.P_(L, 0.0, MARK_V), col, 8 * SS, 6 * SS, 3 * SS)

    def draw_marble(self, d: ImageDraw.ImageDraw, m: str, s: float) -> None:
        g = self.geo
        X, Y = self.P_(s, 0.0, g.centre_v[m])
        R = g.Rd * SS
        d.ellipse((X - R, Y - R, X + R, Y + R), fill=MARBLE, outline=MARBLE_EDGE, width=2 * SS)
        phi = s * g.ppm / g.draw_r[m]            # the drawn marble rolls without slipping at its drawn size
        c, sn = math.cos(phi), math.sin(phi)
        d.line((X - R * 0.84 * c, Y - R * 0.84 * sn, X + R * 0.84 * c, Y + R * 0.84 * sn), fill=STRIPE, width=5 * SS)
        dr = 3.6 * SS
        px, py = X + R * 0.6 * sn, Y - R * 0.6 * c
        d.ellipse((px - dr, py - dr, px + dr, py + dr), fill=STRIPE)

    def draw_inset(self, d: ImageDraw.ImageDraw, m: str) -> None:
        """The end view: the marble seen along the slope, on a flat line or resting on two rail dots."""
        g = self.geo
        xs, ys, Ri = INSET_X, INSET_YS, INSET_R
        cy = ys - g.inset_centre_dy(m)
        x0, x1 = xs - INSET_HALF, xs + INSET_HALF
        # The board slab.
        d.rectangle((*self.L_(x0, ys), *self.L_(x1, ys + 10)), fill=PLANK, outline=RIM, width=1 * SS)
        if m == "flat":
            d.line((*self.L_(x0, ys), *self.L_(x1, ys)), fill=PLANK_EDGE, width=3 * SS)
        else:
            for sgn in (-1.0, 1.0):
                rx = xs + sgn * 0.5 * self.man["rail_gap_radii"] * Ri
                d.rectangle((*self.L_(rx - 4, ys - RAIL_H), *self.L_(rx + 4, ys)), fill=RAIL, outline=STEEL, width=1 * SS)
        X, Y = self.L_(xs, cy)
        R = Ri * SS
        d.ellipse((X - R, Y - R, X + R, Y + R), fill=MARBLE, outline=MARBLE_EDGE, width=2 * SS)
        # The spin axis (a dashed horizontal line through the centre) and the contact radius in gold:
        # the perpendicular distance from the axis to the contact points.
        self.dashed(d, self.L_(x0 - 8, cy), self.L_(x1 + 8, cy), MUTED, 6 * SS, 5 * SS, 2 * SS)
        if m == "flat":
            d.line((*self.L_(xs, cy), *self.L_(xs, ys)), fill=GOLD, width=3 * SS)
            d.line((*self.L_(xs - 7, ys - 1), *self.L_(xs + 7, ys - 1)), fill=GOLD, width=2 * SS)
        else:
            for sgn in (-1.0, 1.0):
                rx = xs + sgn * 0.5 * self.man["rail_gap_radii"] * Ri
                d.line((*self.L_(xs, cy), *self.L_(rx, ys - RAIL_H)), fill=MARBLE_EDGE, width=2 * SS)
            d.line((*self.L_(xs, cy), *self.L_(xs, ys - RAIL_H)), fill=GOLD, width=3 * SS)
            d.line((*self.L_(xs - 7, ys - RAIL_H), *self.L_(xs + 7, ys - RAIL_H)), fill=GOLD, width=2 * SS)
        d.ellipse((X - 4 * SS, Y - 4 * SS, X + 4 * SS, Y + 4 * SS), fill=STRIPE)

    def scene(self, m: str, tau: float) -> tuple[Image.Image, dict]:
        """The band layer of panel m at tau seconds into a cycle (the held setup before the release)."""
        layer = Image.new("RGB", (W * SS, BAND_H * SS), BG)
        d = ImageDraw.Draw(layer)
        tv = tau - self.pa
        rt = tv / self.S
        st = state_at(self.runs[m], rt)
        st["tv"], st["rt"] = tv, rt
        st["mark"] = 0.0
        self.draw_slope(d, m)
        self.draw_pin(d, tv)
        if m == "rails":
            flat_down = rt - self.runs["flat"]["t_arr"]
            if flat_down >= 0.0:
                st["mark"] = min(1.0, flat_down * self.S / self.man["mark_fade_s"])
                self.draw_mark(d, st["mark"])
        self.draw_marble(d, m, st["s"])
        if m == "rails":
            self.draw_rails(d)
        self.draw_inset(d, m)
        return layer, st

    def draw_panel(self, m: str, f: int) -> tuple[Image.Image, dict]:
        k, tau = self.phase(f)
        P, F = self.P, self.F
        layer, st = self.scene(m, tau)
        st["alpha"], st["k"] = 1.0, k
        if tau >= P - F:
            # Crossfade to the next cycle's held setup (both marbles rest at the foot by now, asserted).
            a = (tau - (P - F)) / F
            new, st_new = self.scene(m, tau - P)
            layer = Image.blend(layer, new, a)
            st["alpha"] = max(0.0, 1.0 - 2.0 * a)
            st_new["alpha"], st_new["k"] = max(0.0, 2.0 * a - 1.0), k + 1
            if a >= 0.5:
                st = st_new
        return layer, st

    def draw_text(self, d: ImageDraw.ImageDraw, states: dict, hud_alpha: float) -> None:
        man, ev, g = self.man, self.ev, self.geo
        cf = ev["cf"]
        for m, st in states.items():
            y0 = BAND_Y[m]
            a, ph = st["alpha"], st["phase"]
            down = ph == DOWN
            c = cf[m]
            turns_s = st["v"] / c["r"] / (2.0 * math.pi)
            d.text((ROW_X0, y0 + LABEL_DY), label_text(m), font=self.font, fill=COLOUR[m], anchor="lm")
            d.text((ROW_X0, y0 + SUB_DY), down_text(st["s"]), font=self.font_small, fill=blend(GOLD if down else TEXT, a), anchor="lm")
            d.text((ROW_X0, y0 + FIX_DY), contact_text(c, self.R), font=self.font_small, fill=MUTED, anchor="lm")
            d.text((ROW_X1, y0 + SUB_DY), speed_text(st["v"]), font=self.font_small, fill=blend(GOLD if down else TEXT, a), anchor="rm")
            d.text((ROW_X1, y0 + FIX_DY), spin_text(turns_s), font=self.font_small, fill=blend(GOLD if down else MUTED, a), anchor="rm")
            if down and hud_alpha > 0.02:
                d.text((ROW_X1, y0 + EVENT_DY), event_text(ev, m), font=self.font, fill=blend(GOLD, a * hud_alpha), anchor="rm")
            if m == "rails" and st["mark"] > 0.0:
                mx, my = g.slope_xy(0.5 * (ev["s_mark"] + self.L), 0.0, MARK_LABEL_V)
                d.text((mx, y0 + my), mark_text(ev), font=self.font_tiny, fill=blend(GOLD, a * st["mark"]), anchor="mm")
            # The inset labels.
            cy = INSET_YS - g.inset_centre_dy(m)
            contact_y = INSET_YS if m == "flat" else INSET_YS - RAIL_H
            d.text((INSET_X + INSET_R + 14, y0 + 0.5 * (cy + contact_y)), inset_r_text(m, c), font=self.font_tiny, fill=GOLD, anchor="lm")
            d.text((INSET_X, y0 + INSET_YS + INSET_LABEL_DY), inset_label_text(), font=self.font_tiny, fill=MUTED, anchor="mm")
        if hud_alpha > 0.02:
            d.text((W / 2, LEGEND_Y), legend_text(man), font=self.font, fill=blend(TEXT, hud_alpha), anchor="mm")
            d.text((W / 2, CLOCK_Y), clock_text(states["rails"]["rt"]), font=self.font_small,
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
                d.text((W / 2, TITLE_Y[j]), line, font=self.font_title, fill=blend(TEXT, title_alpha), anchor="mm")
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
            # The geometry runs on; the legend, clock, event rows and card fade out over the first half of
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
    man = json.loads((ROOT / "projects/rails/manifest.json").read_text())
    ev = measure(man)
    if "--measure-only" in sys.argv:
        return
    if "--frames" in sys.argv:
        times = [float(v) for v in sys.argv[sys.argv.index("--frames") + 1].split(",")]
        r = Renderer(man, ev)
        (ROOT / "media/rails").mkdir(parents=True, exist_ok=True)
        for tv in times:
            Image.fromarray(r.frame_at(int(round(tv * man["fps"])))).save(ROOT / f"media/rails/smoke-{tv}.png")
        print("smoke frames: " + ", ".join(f"{tv}" for tv in times))
        return
    Renderer(man, ev).render(ROOT / "media/rails/footage.mp4")


if __name__ == "__main__":
    main()
