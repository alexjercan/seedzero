#!/usr/bin/env python3
"""Ball at a step: roll a ball at a step, does it get up?

Two panels on the same clock, the same floor and the same step drawn the
same way at the same scale. A level floor meets a step (a low kerb) of
height h with a sharp edge; the top of the step is level and continues to
the right. A solid ball of radius R (I = k m R^2, k = 2/5; m cancels)
rolls without slipping on the floor at v0 toward the step, its spin
omega0 = v0 / R: top panel the slow ball, bottom panel the fast ball. The
ball's surface at the height of the edge is d0 = sqrt(R^2 - (R - h)^2)
ahead of its centre and lower parts of the ball are nearer the centre
line, so the first contact is the edge itself; the centre is then at
phi0 = acos((R - h) / R) from the vertical over the edge. Grab: the ball
catches the edge and from that instant rolls about it without slipping
(the material point at the edge is at rest), so angular momentum about
the edge is conserved through the grab,

    m v0 (R - h) + k m R^2 omega0 = (1 + k) m R^2 omega1,
    omega1 = (v0 / R) (1 - h / ((1 + k) R)),

the edge keeping 1 - h / ((1 + k) R) of the spin. Pivot: a rigid body
about the fixed edge, (1 + k) m R^2 phi'' = m g R sin(phi), phi measured
from the vertical over the edge toward the floor side; the ball climbs
while phi falls toward 0; integrated by RK4 at dt_s with compensated
summation, the events located by bisection inside the step, the energy
(1/2)(1 + k) R^2 phi'^2 + g R cos(phi) checked per unit mass, the normal
force N / (m g) = cos(phi) - R phi'^2 / g (positive while the edge pushes)
and the grip the edge must give, (k / (1 + k)) sin(phi) / (N / m g),
printed along the pivot. Over the top: when phi reaches 0 the centre is
over the edge, the ball's lowest point touches the top of the step at the
edge and the pivot speed R phi' equals the rolling speed, so the ball
rolls on along the top without slipping at v_top = R |phi'| =
sqrt((omega1 R)^2 - 2 g h / (1 + k)) with no further loss. Fall back: if
phi' reaches 0 before phi reaches 0 the ball rises (1 + k)(omega1 R)^2 /
(2 g) above the floor at its highest, pivots back down and returns to the
floor at the start geometry with phi' = +omega1 (energy conserved on the
pivot); its centre then moves back at omega1 (R - h) and down at omega1
d0; the floor landing is plastic (the floor kills the downward speed) and
the ball leaves the edge; angular momentum about the floor contact is
conserved through the landing, m R omega1 (R - h) + k m R^2 omega1 =
(1 + k) m R v_back, so v_back = omega1 ((R - h) + k R) / (1 + k) and the
ball rolls back without slipping. Threshold: v* = sqrt(2 g h / (1 + k)) /
(1 - h / ((1 + k) R)), at which the ball just reaches the top with zero
speed. Edge-force limit: N = 0 at the first touch when omega1 = sqrt(g
(R - h)) / R; above that speed the model ends (a real ball bounces off).
The run repeats every cycle_s seconds of video with a crossfade back to
the rolling start; the cycle divides the scene length, so the scene is
exactly periodic and the last frame equals the first. Shown at 1/slow
speed. Deterministic, no seed.

Measured and printed: the touch geometry, the spin kept at the grab, the
threshold and the edge-force limit, for each panel the RK4 pivot (over
the top or the highest point and the fall back, the times, the speeds,
the minimum edge force, the grip the edge and the floor must give, the
grab's impulse ratio, the energy residual, a half-step rerun) against the
closed forms, the brief's checks, the tables at 20 ms, the description
variants, the schedule in video time, the on-screen text widths and the
layout clearances.

usage: kerbhop.py [--measure-only] [--frames t1,t2,...]
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
DECK_A = (30, 36, 46)
DECK_B = (42, 50, 62)
RIM = (96, 108, 126)
INK = (150, 158, 170)
BALL_FILL = (172, 182, 198)
BALL_EDGE = (104, 116, 134)
SPOKE = (34, 40, 50)
TRAIL = (104, 114, 130)

# Layout: overlay at y 96..130 (captions.py), two title rows at y 190/252 for
# the first seconds, then the legend at y 236 and the shared clock at y 290;
# two panels stacked, the slow ball in the band y 330..880 and the fast ball
# in y 880..1430, each drawn at 2x in its own geometry layer; each band has
# its label row 40 px under the band top, its second row at 84 and its third
# at 120 (left column from x 40, right column to x 1040); the gold event row
# at 176; the floor surface floor_dy under the band top (y 800 and 1350),
# the step top h above it (440), the slab down to slab_dy (520), the edge at
# edge_x_px; the height scale on the step's side at x 910; captions at
# caption_y 0.75 (y 1440..1530); the six-line card from y 1572 at a 48 px
# pitch.
LEGEND_Y, CLOCK_Y = 236, 290
SS = 2
PAYOFF_Y, PAYOFF_PITCH = 1572.0, 48
PANELS = ("slow", "fast")
BAND_Y = {"slow": 330, "fast": 880}
BAND_H = 550
LABEL_DY, SUB_DY, FIX_DY = 40, 84, 120
EVENT_DY, EVENT_X = 176, 540
ROW_X0, ROW_X1 = 40, 1040
SCALE_X, SCALE_TICK, SCALE_LABEL_X = 910, 12, 934
PEAK_LABEL_X, PEAK_LINE_END = 874, 772
EDGE_MARK, EDGE_RING = 5, 16
COLOUR = {"slow": TEAL, "fast": CORAL}
ROLL_IN, CLIMB, FALL, OVER, BACK = "rolling", "on the edge", "falling back", "over the top", "rolling back"


def blend(col, a: float, base=BG) -> tuple:
    a = max(0.0, min(1.0, a))
    return tuple(int(round(c * a + b * (1 - a))) for c, b in zip(col, base))


# --- measurement --------------------------------------------------------------
def geometry(R: float, h: float, k: float, g: float) -> dict:
    """The touch geometry and the closed forms that do not depend on v0."""
    phi0 = math.acos((R - h) / R)
    d0 = math.sqrt(R * R - (R - h) ** 2)
    keep = 1.0 - h / ((1.0 + k) * R)
    vstar = math.sqrt(2.0 * g * h / (1.0 + k)) / keep
    w_zero = math.sqrt(g * (R - h)) / R              # omega1 at which N = 0 at the first touch
    v_zero = w_zero * R / keep
    j_ratio = (h / R) * (k / (1.0 + k)) / math.sin(phi0)   # tangential over normal impulse at the grab
    f_grip = k * h / ((1.0 + k) * d0)                # horizontal over vertical impulse at the floor landing
    return {"phi0": phi0, "d0": d0, "keep": keep, "vstar": vstar, "w_zero": w_zero, "v_zero": v_zero,
            "j_ratio": j_ratio, "f_grip": f_grip}


def pivot(v0: float, R: float, h: float, k: float, g: float, dt: float) -> dict:
    """RK4 of the pivot about the edge from the grab at v0: (phi, phi') from (phi0, -omega1) until phi
    reaches 0 (over the top) or phi' turns and phi is back at phi0 (fall back). Compensated (Kahan)
    summation of the state; the events are located by bisection on the last step. Returns the table and
    the end state."""
    geo = geometry(R, h, k, g)
    phi0, d0, w1 = geo["phi0"], geo["d0"], geo["keep"] * v0 / R
    c = g / ((1.0 + k) * R)

    def acc(p: float) -> float:
        return c * math.sin(p)

    def rk4(p: float, w: float, hh: float) -> tuple[float, float]:
        k1p, k1w = w, acc(p)
        k2p, k2w = w + 0.5 * hh * k1w, acc(p + 0.5 * hh * k1p)
        k3p, k3w = w + 0.5 * hh * k2w, acc(p + 0.5 * hh * k2p)
        k4p, k4w = w + hh * k3w, acc(p + hh * k3p)
        return hh * (k1p + 2.0 * k2p + 2.0 * k3p + k4p) / 6.0, hh * (k1w + 2.0 * k2w + 2.0 * k3w + k4w) / 6.0

    def bisect(p: float, w: float, fn) -> tuple[float, float, float]:
        lo, hi = 0.0, dt
        for _ in range(80):
            mid = 0.5 * (lo + hi)
            dp, dw = rk4(p, w, mid)
            if fn(p + dp, w + dw):
                hi = mid
            else:
                lo = mid
        dp, dw = rk4(p, w, hi)
        return hi, p + dp, w + dw

    run: dict = {"v0": v0, "R": R, "h": h, "k": k, "g": g, "dt": dt, "om0": v0 / R, "om1": w1, "phi0": phi0,
                 "d0": d0, "t_peak": None, "N_touch": math.cos(phi0) - R * w1 * w1 / g}
    T, PH, WW = [0.0], [phi0], [-w1]
    p, w = phi0, -w1
    cp = cw = 0.0
    n = 0
    while True:
        dp, dw = rk4(p, w, dt)
        yp = dp - cp
        tp = p + yp
        cp = (tp - p) - yp
        yw = dw - cw
        tw = w + yw
        cw = (tw - w) - yw
        pn, wn = tp, tw
        if pn <= 0.0:
            hh, _, wh = bisect(p, w, lambda P_, W_: P_ <= 0.0)
            t = n * dt + hh
            T.append(t), PH.append(0.0), WW.append(wh)
            run.update({"over": True, "t_end": t, "w_end": wh, "v_top": abs(wh) * R})
            break
        if run["t_peak"] is None and wn >= 0.0:
            hh, ph, _ = bisect(p, w, lambda P_, W_: W_ >= 0.0)
            run["t_peak"], run["phi_peak"] = n * dt + hh, ph
            run["rise"] = R * math.cos(ph) - (R - h)        # the centre's rise above its floor level
        if run["t_peak"] is not None and pn >= phi0:
            hh, _, wh = bisect(p, w, lambda P_, W_: P_ >= phi0)
            t = n * dt + hh
            T.append(t), PH.append(phi0), WW.append(wh)
            run.update({"over": False, "t_end": t, "w_end": wh})
            break
        p, w = pn, wn
        n += 1
        T.append(n * dt), PH.append(p), WW.append(w)
    run["steps"] = n + 1
    run["t"], run["phi"], run["w"] = np.array(T), np.array(PH), np.array(WW)
    E = 0.5 * (1.0 + k) * R * R * run["w"] ** 2 + g * R * np.cos(run["phi"])
    run["E0"], run["E_res"] = float(E[0]), float(np.max(np.abs(E - E[0])))
    run["N"] = np.cos(run["phi"]) - R * run["w"] ** 2 / g
    run["grip"] = (k / (1.0 + k)) * np.sin(run["phi"]) / run["N"]
    run["N_min"], run["i_Nmin"] = float(run["N"].min()), int(np.argmin(run["N"]))
    run["grip_max"], run["i_gmax"] = float(run["grip"].max()), int(np.argmax(run["grip"]))
    run["grip_touch"] = float(run["grip"][0])
    if run["over"]:
        run["v_top_closed"] = math.sqrt(max(0.0, (w1 * R) ** 2 - 2.0 * g * h / (1.0 + k)))
    else:
        we = run["w_end"]
        run["rise_closed"] = (1.0 + k) * (w1 * R) ** 2 / (2.0 * g)
        run["vx_land"], run["vy_land"] = we * (R - h), we * d0
        run["v_back"] = we * ((R - h) + k * R) / (1.0 + k)
        run["f_grip"] = (run["v_back"] - we * (R - h)) / (we * d0)
    return run


def state_at(run: dict, t: float) -> dict:
    """Centre x (m from the edge, positive to the right), height y (m above the floor), the spoke angle
    (clockwise on screen), the centre speed, the spin rate (clockwise positive), the rise and the phase, t
    real seconds after the touch."""
    R, h, v0, om0, phi0, d0 = run["R"], run["h"], run["v0"], run["om0"], run["phi0"], run["d0"]
    if t < 0.0:
        return {"x": -d0 + v0 * t, "y": R, "th": om0 * t, "v": v0, "spin": om0, "phase": ROLL_IN, "on_edge": False}
    if t < run["t_end"]:
        phi = float(np.interp(t, run["t"], run["phi"]))
        w = float(np.interp(t, run["t"], run["w"]))
        return {"x": -R * math.sin(phi), "y": h + R * math.cos(phi), "th": phi0 - phi, "v": R * abs(w), "spin": -w,
                "phase": CLIMB if w < 0.0 else FALL, "on_edge": True, "phi": phi, "w": w}
    u = t - run["t_end"]
    if run["over"]:
        v = run["v_top"]
        return {"x": v * u, "y": R + h, "th": phi0 + v / R * u, "v": v, "spin": v / R, "phase": OVER, "on_edge": False}
    v = run["v_back"]
    return {"x": -d0 - v * u, "y": R, "th": -v / R * u, "v": v, "spin": -v / R, "phase": BACK, "on_edge": False}


def measure(man: dict) -> dict:
    g, R, h, k = man["g"], man["radius_m"], man["step_m"], man["k"]
    v0s = man["v0_m_s"]
    dt = man["dt_s"]
    S, P, D, fps, F, ta = man["slow"], man["cycle_s"], man["scene_duration"], man["fps"], man["reset_fade"], man["touch_at"]
    cycles = D / P
    assert abs(cycles - round(cycles)) < 1e-9, "the cycle must divide the scene length"
    for key in ("cycle_s", "touch_at", "first_cycle_at", "reset_fade", "scene_duration"):
        assert abs(man[key] * fps - round(man[key] * fps)) < 1e-9, f"{key} must be a whole number of frames"
    ppm = man["px_per_m"]
    geo = geometry(R, h, k, g)
    phi0, d0, keep, vstar = geo["phi0"], geo["d0"], geo["keep"], geo["vstar"]
    print(f"setup: side view, two panels on one clock, the same level floor and the same step of h = {h * 100:g} cm with "
          f"a sharp edge (the top level and continuing to the right); a solid ball of radius R = {R * 100:g} cm "
          f"({2 * R * 100:g} cm across, I = {k:g} m R^2, m cancels) rolls without slipping on the floor at v0 toward the "
          f"step, spinning at omega0 = v0 / R; top panel v0 = {v0s['slow']:g} m/s, bottom panel {v0s['fast']:g} m/s; "
          f"g = {g:g} m/s^2; the ball grips the edge and never slips there (the grip it needs is printed); the pivot "
          f"about the edge integrated by RK4 at dt = {dt:.0e} s with compensated summation, the events located by "
          f"bisection inside the step, checked against the energy, the closed forms and a half-step rerun; the floor "
          f"landing is plastic (the floor kills the downward speed) and conserves angular momentum about the floor "
          f"contact; shown at 1/{S:g} speed on a {P:g} s cycle ({P * fps:.0f} frames) with the touch {ta:g} s into the "
          f"cycle, {cycles:.0f} cycles in {D:g} s; drawn at {ppm:g} px per metre (the ball {2 * R * ppm:.0f} px across, "
          f"the step {h * ppm:.0f} px tall); deterministic, no seed")
    # The ball meets the edge first: at every height y under h the half-chord is under d0.
    ys = np.linspace(0.0, h, 301)
    chords = np.sqrt(R * R - (R - ys) ** 2)
    assert np.all(chords[:-1] < d0 + 1e-15), "a lower part of the ball would meet the step face first"
    print(f"geometry: the ball's surface at the height of the edge is d0 = sqrt(R^2 - (R - h)^2) = {d0 * 100:.4f} cm = "
          f"{d0 * 100:.2f} cm ahead of its centre, and at every lower height the half-chord is smaller (at most "
          f"{chords[:-1].max() * 100:.4f} cm under the edge height), so the first contact is the edge itself; the centre "
          f"is then phi0 = acos((R - h) / R) = {math.degrees(phi0):.4f} degrees = {math.degrees(phi0):.2f} degrees from "
          f"the vertical over the edge; the grab keeps omega1 / omega0 = 1 - h / ((1 + k) R) = {keep:.4f} of the spin "
          f"and loses {1.0 - keep:.4f}, about one fifth (1/5 = {0.2:.4f}); the energy kept through the grab is "
          f"keep^2 = {keep * keep:.4f}; the grab's impulse ratio, tangential over normal, is (h / R)(k / (1 + k)) / "
          f"sin(phi0) = {geo['j_ratio']:.4f} for any v0; the floor landing needs a grip (horizontal over vertical "
          f"impulse) of k h / ((1 + k) d0) = {geo['f_grip']:.4f} for any v0; threshold v* = sqrt(2 g h / (1 + k)) / "
          f"(1 - h / ((1 + k) R)) = {vstar:.4f} m/s = {vstar:.2f} m/s = {vstar:.1f} m/s (the ball just reaches the top "
          f"with zero speed); edge-force limit: N = 0 at the first touch when omega1 = sqrt(g (R - h)) / R = "
          f"{geo['w_zero']:.4f} rad/s, v0 = {geo['v_zero']:.4f} m/s = {geo['v_zero']:.2f} m/s; above it the edge "
          f"force is negative at the touch and the model ends (a real ball bounces off)")
    runs = {m: pivot(v0s[m], R, h, k, g, dt) for m in PANELS}
    halves = {m: pivot(v0s[m], R, h, k, g, 0.5 * dt) for m in PANELS}
    ev: dict = {"geo": geo, "runs": runs, "halves": halves}
    checks: list[tuple[str, float, float, float]] = []
    checks += [("phi0 (degrees)", math.degrees(phi0), 43.34, 0.006), ("edge ahead of the centre (cm)", d0 * 100, 7.55, 0.006),
               ("omega1 / omega0", keep, 0.8052, 6e-5), ("threshold v* (m/s)", vstar, 0.8052, 6e-5),
               ("grab impulse ratio", geo["j_ratio"], 0.11, 0.006), ("floor grip", geo["f_grip"], 0.11, 0.006)]
    for m in PANELS:
        rn, hf, v0 = runs[m], halves[m], v0s[m]
        name = "top panel" if m == "slow" else "bottom panel"
        assert rn["E_res"] < 1e-12, "the pivot energy drifts"
        assert rn["N_touch"] > 0.0 and rn["N_min"] > 0.0, "the edge force goes negative"
        assert abs(hf["t_end"] - rn["t_end"]) < 1e-6, "the half-step rerun disagrees"
        head = (f"{v0:g} m/s ({name}): omega0 = {rn['om0']:.4f} rad/s = {rn['om0'] / (2 * math.pi):.3f} turns/s, omega1 = "
                f"{rn['om1']:.4f} rad/s = {rn['om1'] / (2 * math.pi):.3f} turns/s after the grab; {'over' if v0 > vstar else 'under'} "
                f"the threshold by {abs(v0 - vstar):.4f} m/s; at the touch the edge force is {rn['N_touch']:.4f} weights and the "
                f"grip needed {rn['grip_touch']:.4f}; ")
        if rn["over"]:
            line = head + (f"RK4: over the edge (phi = 0) at {rn['t_end']:.4f} s after the touch, rolling on along the top at "
                           f"{rn['v_top']:.4f} m/s = {rn['v_top']:.2f} m/s (closed form sqrt((omega1 R)^2 - 2 g h / (1 + k)) = "
                           f"{rn['v_top_closed']:.4f} m/s, diff {rn['v_top'] - rn['v_top_closed']:+.1e} m/s) with no further loss, "
                           f"spinning at {rn['v_top'] / R:.4f} rad/s; the rise is the full {h * 100:g} cm")
            checks += [(f"{v0:g} m/s omega0 (rad/s)", rn["om0"], 8.182, 6e-4), (f"{v0:g} m/s omega1 (rad/s)", rn["om1"], 6.588, 6e-4),
                       (f"{v0:g} m/s over the edge at (s)", rn["t_end"], 0.1845, 6e-5), (f"{v0:g} m/s rolls on at (m/s)", rn["v_top"], 0.3238, 6e-5),
                       (f"{v0:g} m/s minimum edge force (weights)", rn["N_min"], 0.241, 6e-4), (f"{v0:g} m/s needed edge grip at the touch", rn["grip_touch"], 0.82, 0.006)]
            half = (f"half-step rerun (dt = {0.5 * dt:.0e} s): over at {hf['t_end']:.7f} s ({hf['t_end'] - rn['t_end']:+.1e} s) at "
                    f"{hf['v_top']:.7f} m/s ({hf['v_top'] - rn['v_top']:+.1e} m/s)")
        else:
            assert abs(rn["t_end"] - 2.0 * rn["t_peak"]) < 1e-6, "the pivot is not symmetric"
            line = head + (f"RK4: the energy (1/2)(1 + k)(omega1 R)^2 = {0.5 * (1 + k) * (rn['om1'] * R) ** 2:.4f} J/kg is under "
                           f"g h = {g * h:.4f} J/kg, so it falls back: highest at {rn['t_peak']:.4f} s after the touch with the centre "
                           f"{rn['rise'] * 100:.4f} cm = {rn['rise'] * 100:.3f} cm = {rn['rise'] * 100:.1f} cm above its floor level, "
                           f"about {rn['rise'] * 100:.0f} of the {h * 100:g} cm (closed form (1 + k)(omega1 R)^2 / (2 g) = "
                           f"{rn['rise_closed'] * 100:.4f} cm, diff {(rn['rise'] - rn['rise_closed']) * 100:+.1e} cm; phi at the top "
                           f"{math.degrees(rn['phi_peak']):.2f} degrees), {(h - rn['rise']) * 100:.2f} cm short of the top; back on the "
                           f"floor at {rn['t_end']:.4f} s = {rn['t_end']:.2f} s after the touch (2 x the time to the top) with phi' = "
                           f"{rn['w_end']:.4f} rad/s (omega1 {rn['om1']:.4f}), the centre moving back at omega1 (R - h) = "
                           f"{rn['vx_land']:.4f} m/s and down at omega1 d0 = {rn['vy_land']:.4f} m/s; the floor kills the downward "
                           f"speed and the ball rolls back at v_back = omega1 ((R - h) + k R) / (1 + k) = {rn['v_back']:.4f} m/s = "
                           f"{rn['v_back']:.2f} m/s, spinning at {rn['v_back'] / R:.4f} rad/s (the floor grip needed "
                           f"{rn['f_grip']:.4f})")
            checks += [(f"{v0:g} m/s omega0 (rad/s)", rn["om0"], 6.364, 6e-4), (f"{v0:g} m/s omega1 (rad/s)", rn["om1"], 5.124, 6e-4),
                       (f"{v0:g} m/s rise (cm)", rn["rise"] * 100, 2.268, 6e-4), (f"{v0:g} m/s highest at (s)", rn["t_peak"], 0.172, 6e-4),
                       (f"{v0:g} m/s back on the floor at (s)", rn["t_end"], 0.3443, 6e-5), (f"{v0:g} m/s moving back (m/s)", rn["vx_land"], 0.410, 6e-4),
                       (f"{v0:g} m/s moving down (m/s)", rn["vy_land"], 0.387, 6e-4), (f"{v0:g} m/s rolls back at (m/s)", rn["v_back"], 0.4538, 6e-5),
                       (f"{v0:g} m/s minimum edge force (weights)", rn["N_min"], 0.433, 6e-4), (f"{v0:g} m/s needed edge grip at the touch", rn["grip_touch"], 0.453, 6e-4),
                       (f"{v0:g} m/s needed floor grip", rn["f_grip"], 0.11, 0.006)]
            half = (f"half-step rerun (dt = {0.5 * dt:.0e} s): highest at {hf['t_peak']:.7f} s ({hf['t_peak'] - rn['t_peak']:+.1e} s), "
                    f"back at {hf['t_end']:.7f} s ({hf['t_end'] - rn['t_end']:+.1e} s), rise {hf['rise'] * 100:.7f} cm "
                    f"({(hf['rise'] - rn['rise']) * 100:+.1e} cm), rolls back at {hf['v_back']:.7f} m/s ({hf['v_back'] - rn['v_back']:+.1e} m/s)")
        line += (f"; the edge force N / (m g) is at least {rn['N_min']:.4f} weights (at {rn['t'][rn['i_Nmin']]:.4f} s) and the grip "
                 f"the edge must give is at most {rn['grip_max']:.4f} (at {rn['t'][rn['i_gmax']]:.4f} s, the touch); the grab's "
                 f"impulse ratio is {geo['j_ratio']:.4f}; the energy stays within {rn['E_res']:.1e} J/kg of {rn['E0']:.6f} J/kg "
                 f"over {rn['steps']} steps; {half}")
        print(line)
    rs, rf = runs["slow"], runs["fast"]
    assert (not rs["over"]) and rf["over"], "the panels do not split at the threshold"
    print(f"the two panels: at {v0s['slow']:g} m/s the ball catches the edge, swings up {rs['rise'] * 100:.1f} of the {h * 100:g} cm "
          f"and falls back onto the floor {rs['t_end']:.2f} s after the touch, rolling back at {rs['v_back']:.2f} m/s; at "
          f"{v0s['fast']:g} m/s it is over the top {rf['t_end']:.2f} s after the touch and rolls on along the step at "
          f"{rf['v_top']:.2f} m/s; the limit is {vstar:.4f} m/s = {vstar:.2f} m/s = {vstar:.1f} m/s; the catch keeps {keep:.4f} = "
          f"{keep:.2f} of the spin and costs {1 - keep:.4f}, about one fifth; the rest must lift the centre {h * 100:g} cm")
    # Tables at 20 ms.
    ts = man["table_step_s"]
    for m in PANELS:
        rn = runs[m]
        rows = []
        tt = 0.0
        while tt < rn["t_end"] - 1e-12:
            rows.append(tt)
            tt += ts
        rows.append(rn["t_end"])
        out = []
        for tt in rows:
            st = state_at(rn, min(tt, rn["t_end"] - 1e-12))
            phi, w = st["phi"], st["w"]
            N = math.cos(phi) - R * w * w / g
            out.append(f"{tt:.4f} s: x {st['x'] * 100:+.2f} cm, y {st['y'] * 100:.2f} cm, phi {math.degrees(phi):.2f} deg, "
                       f"phi' {w:+.3f} rad/s, N {N:.3f}, grip {(k / (1 + k)) * math.sin(phi) / N:.3f}")
        print(f"table {v0s[m]:g} m/s (RK4 table, real time after the touch; x from the edge, y the centre's height above the "
              f"floor; N in weights): " + "; ".join(out))
    # For the description.
    descr = []
    ev["others"] = {}
    for v0 in man["description_speeds_m_s"]:
        N_touch = math.cos(phi0) - R * (keep * v0 / R) ** 2 / g
        if N_touch < 0.0:
            descr.append(f"{v0:g} m/s: the edge force at the touch would be {N_touch:.4f} weights, negative: the model ends "
                         f"(a real ball bounces off the edge)")
            continue
        ro = pivot(v0, R, h, k, g, dt)
        ev["others"][v0] = ro
        if ro["over"]:
            descr.append(f"{v0:g} m/s: over at {ro['t_end']:.4f} s, rolling on at {ro['v_top']:.4f} m/s; edge force at the touch "
                         f"{ro['N_touch']:.4f} weights (its minimum {ro['N_min']:.4f}), grip needed at the touch {ro['grip_touch']:.3f} "
                         f"(its maximum {ro['grip_max']:.3f})")
            if abs(v0 - 1.0) < 1e-9:
                checks += [("1.0 m/s over at (s)", ro["t_end"], 0.1424, 6e-5), ("1.0 m/s rolls on at (m/s)", ro["v_top"], 0.4775, 6e-5),
                           ("1.0 m/s needed grip at the touch", ro["grip_touch"], 1.55, 0.006), ("1.0 m/s edge force at the touch", ro["N_touch"], 0.126, 6e-4)]
            if abs(v0 - 1.1) < 1e-9:
                checks += [("1.1 m/s edge force at the touch", ro["N_touch"], 0.0, 6e-4), ("1.1 m/s over at (s)", ro["t_end"], 0.1194, 6e-5),
                           ("1.1 m/s rolls on at (m/s)", ro["v_top"], 0.6035, 6e-5)]
        else:
            descr.append(f"{v0:g} m/s: rises {ro['rise'] * 100:.4f} cm (closed form {ro['rise_closed'] * 100:.4f}), highest at "
                         f"{ro['t_peak']:.4f} s, back on the floor at {ro['t_end']:.4f} s, rolls back at {ro['v_back']:.4f} m/s; "
                         f"edge force at the touch {ro['N_touch']:.4f} weights, grip needed {ro['grip_touch']:.3f}")
            if abs(v0 - 0.8) < 1e-9:
                checks += [("0.8 m/s rise (cm)", ro["rise"] * 100, 2.962, 6e-4), ("0.8 m/s back on the floor at (s)", ro["t_end"], 0.7287, 6e-5),
                           ("0.8 m/s rolls back at (m/s)", ro["v_back"], 0.5187, 6e-5)]
    kh = man["hollow_k"]
    gh = geometry(R, h, kh, g)
    descr.append(f"a hollow ball (thin shell, k = {kh:.4f}) of the same size: threshold {gh['vstar']:.4f} m/s (keeps {gh['keep']:.4f} "
                 f"of the spin), edge-force limit {gh['v_zero']:.4f} m/s")
    checks.append(("hollow ball threshold (m/s)", gh["vstar"], 0.7104, 6e-5))
    h2 = man["description_step_m"]
    g2 = geometry(R, h2, k, g)
    descr.append(f"a {h2 * 100:g} cm step for this ball: threshold {g2['vstar']:.4f} m/s but the edge force is negative at the touch "
                 f"above {g2['v_zero']:.4f} m/s, so no speed takes it (the ball bounces off before it can climb)")
    checks += [("5 cm step threshold (m/s)", g2["vstar"], 1.2393, 6e-5), ("5 cm step edge-force limit (m/s)", g2["v_zero"], 1.1359, 6e-5)]
    rg = man["ring"]
    g3 = geometry(rg["radius_m"], rg["step_m"], rg["k"], g)
    descr.append(f"a bike-wheel ring (R = {rg['radius_m'] * 100:g} cm, k = {rg['k']:g}) at a {rg['step_m'] * 100:g} cm kerb: threshold "
                 f"{g3['vstar']:.4f} m/s, edge-force limit {g3['v_zero']:.4f} m/s (it keeps {g3['keep']:.4f} of the spin)")
    checks.append(("bike-wheel ring threshold (m/s)", g3["vstar"], 1.1671, 6e-5))
    ev["hollow"], ev["step2"], ev["ring"] = gh, g2, g3
    print(f"for the description (same ball, same {h * 100:g} cm step unless said): " + "; ".join(descr))
    # The brief's checks.
    fails = 0
    out = []
    for name, got, want, tol in checks:
        ok = abs(got - want) <= tol
        fails += 0 if ok else 1
        out.append(f"{name}: brief {want:g}, sim {got:.5g}, diff {got - want:+.1e}: {'ok' if ok else 'FAIL'}")
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

    r_end = (P - ta) / S                     # real time after the touch at the end of the cycle
    r_fade = (P - F - ta) / S
    tau0 = (0.0 - t0) % P
    r0 = (tau0 - ta) / S
    st0 = {m: state_at(runs[m], r0) for m in PANELS}
    st_end = {m: state_at(runs[m], r_end) for m in PANELS}
    ev["r_end"] = r_end
    print(f"schedule (video time, 1/{S:g} speed): cycles of {P:g} s start at " + ", ".join(f"{st:.2f}" for st in starts)
          + f" s (the first {-t0:.2f} s before the first frame); both balls roll in from {ta:g} s before the touch, the "
          f"{v0s['slow']:g} m/s ball's centre {-st0['slow']['x'] * 100:.2f} cm and the {v0s['fast']:g} m/s ball's {-st0['fast']['x'] * 100:.2f} "
          f"cm left of the edge at the cycle start; both touch the edge {ta:g} s into each cycle at {lst(ta)} s; the "
          f"{v0s['fast']:g} m/s ball is over the top {S * rf['t_end']:.2f} s later at {lst(ta + S * rf['t_end'])} s (its event row "
          f"lights) and rolls on at {rf['v_top']:.4f} m/s, its centre {st_end['fast']['x'] * 100:.1f} cm right of the edge at the end "
          f"of the cycle; the {v0s['slow']:g} m/s ball is highest {S * rs['t_peak']:.2f} s after the touch at "
          f"{lst(ta + S * rs['t_peak'])} s (the gold rise mark appears), back on the floor {S * rs['t_end']:.2f} s after the touch at "
          f"{lst(ta + S * rs['t_end'])} s (its event row lights) and rolls back at {rs['v_back']:.4f} m/s, its centre "
          f"{-st_end['slow']['x'] * 100:.1f} cm left of the edge at the end of the cycle; the reset crossfade runs over the last "
          f"{F:g} s of each cycle (from {lst(P - F)} s; the readouts out over its first half and in over its second); on the "
          f"first frame the cycle is {tau0:.2f} s in ({r0:.3f} s real: both balls rolling in); title until {man['title_until']:g} s; "
          f"payoff card from {man['payoff_t']:g} s; the title fades back in over the last {man['loop_fade']:g} s and the last frame "
          f"repeats the first (the scene is periodic: {D:g} s holds exactly {cycles:.0f} cycles)")
    # Text widths.
    font = os.environ["SEED_ZERO_FONT"]
    f24, f28, f34, f40, f56 = (ImageFont.truetype(font, n) for n in (24, 28, 34, 40, 56))
    widths = {"overlay@34": (f34, man["overlay"])}
    for j, line in enumerate(man["title"].split("|")):
        widths[f"title line {j + 1}@56"] = (f56, line)
    widths["legend@40"] = (f40, legend_text(man))
    widths["clock@28"] = (f28, clock_text(0.3443))
    widths["clock before@28"] = (f28, clock_text(-1.0))
    for m in PANELS:
        widths[f"label {m}@40"] = (f40, label_text(man, m))
        widths[f"fixed {m}@28"] = (f28, fixed_text(man, ev, m))
        widths[f"event {m}@40"] = (f40, event_text(ev, m))
    widths["speed@28"] = (f28, speed_text(0.9))
    for ph in (ROLL_IN, CLIMB, FALL, OVER, BACK):
        widths[f"state {ph}@28"] = (f28, state_text(ph))
    widths["rise@40"] = (f40, rise_text(0.03))
    widths["spin@28"] = (f28, spin_text(8.182))
    widths["scale top@24"] = (f24, scale_top_text(h))
    widths["scale bottom@24"] = (f24, scale_bottom_text())
    widths["peak@24"] = (f24, peak_text(rs["rise"]))
    for j, line in enumerate(payoff_lines(man, ev)):
        widths[f"payoff line {j + 1}@40"] = (f40, line)
    print("text widths (the on-screen strings verbatim): " + ", ".join(f"{kk} {f.getlength(s):.0f} px {s!r}" for kk, (f, s) in widths.items()))
    assert all(f.getlength(s) < 950 for f, s in widths.values()), "a text line is wider than 950 px"
    assert len(payoff_lines(man, ev)) <= 6, "the card has more than six lines"
    assert len(man["title"].replace("|", " ")) <= 100 and "<" not in man["title"] and ">" not in man["title"]
    # Layout checks.
    left = ROW_X0 + max(max(f40.getlength(label_text(man, m)), f28.getlength(speed_text(0.9)),
                            max(f28.getlength(state_text(ph)) for ph in (ROLL_IN, CLIMB, FALL, OVER, BACK))) for m in PANELS)
    right = ROW_X1 - max(max(f40.getlength(rise_text(0.03)), f28.getlength(spin_text(8.182)), f28.getlength(fixed_text(man, ev, m)))
                         for m in PANELS)
    rows_bottom = FIX_DY + 14
    floor = float(man["floor_dy"])
    step_top = floor - h * ppm
    slab = float(man["slab_dy"])
    edge = float(man["edge_x_px"])
    Rpx = R * ppm
    ball_top_step = step_top - 2.0 * Rpx
    ev_w = max(f40.getlength(event_text(ev, m)) for m in PANELS)
    ev_y0, ev_y1 = EVENT_DY - 20, EVENT_DY + 20
    x_start = {m: edge + st0[m]["x"] * ppm for m in PANELS}
    x_pre = {m: edge + state_at(runs[m], (0.0 - F - ta) / S)["x"] * ppm for m in PANELS}   # the incoming ball at the fade start
    x_end = {m: edge + st_end[m]["x"] * ppm for m in PANELS}
    x_peak = edge - R * math.sin(rs["phi_peak"]) * ppm
    y_peak = floor - rs["rise"] * ppm
    sc_top = f24.getlength(scale_top_text(h))
    pk_w = f24.getlength(peak_text(rs["rise"]))
    print(f"row check: the left column ends at x {left:.0f} px, the right column starts at x {right:.0f} px; both end "
          f"{rows_bottom} px under the band top; the event row spans {ev_y0} to {ev_y1} px under the band top and x "
          f"{EVENT_X - ev_w / 2:.0f} to {EVENT_X + ev_w / 2:.0f} px (widest {ev_w:.0f} px, centred on {EVENT_X}); the floor surface "
          f"is {floor:.0f} px under the band top, the step top {step_top:.0f} px, the slab to {slab:.0f} px, the edge at x "
          f"{edge:.0f}; the ball is {2 * Rpx:.0f} px across, its top {floor - 2 * Rpx:.0f} px under the band top on the floor and "
          f"{ball_top_step:.0f} px on the step; centres at the cycle start x {x_start['slow']:.1f} ({v0s['slow']:g}) and "
          f"{x_start['fast']:.1f} ({v0s['fast']:g}) px, at the fade start of the incoming cycle {x_pre['slow']:.1f} and "
          f"{x_pre['fast']:.1f} px, at the cycle end {x_end['slow']:.1f} ({v0s['slow']:g}, rolling back) and {x_end['fast']:.1f} "
          f"({v0s['fast']:g}, on the step) px; the slow ball's centre at its peak x {x_peak:.1f} px, its bottom {y_peak:.1f} px "
          f"under the band top (the step top at {step_top:.0f}); the height scale on the step's side at x {SCALE_X} "
          f"({SCALE_X - SCALE_TICK} to {SCALE_X + SCALE_TICK}) from {step_top:.0f} to {floor:.0f} px, its labels from x "
          f"{SCALE_LABEL_X} to {SCALE_LABEL_X + sc_top:.0f} px; the gold rise mark runs from the ball's bottom to x "
          f"{PEAK_LINE_END} px with its label x {PEAK_LABEL_X - pk_w:.0f} to {PEAK_LABEL_X} px at {y_peak:.1f} px; each band is "
          f"{BAND_H} px tall (y {BAND_Y['slow']} to {BAND_Y['slow'] + BAND_H} and {BAND_Y['fast']} to {BAND_Y['fast'] + BAND_H}); the "
          f"caption band starts at y {int(man['caption_y'] * H)}; the title rows end at y {252 + 28} and the overlay band ends at y 130")
    assert right - left > 40, "the columns meet"
    assert ev_y0 > rows_bottom + 16, "the event row meets the text rows"
    assert ev_y1 < ball_top_step - 16, "the event row meets the ball on the step"
    assert EVENT_X - ev_w / 2 > 20 and EVENT_X + ev_w / 2 < W - 20, "the event row leaves the frame"
    for m in PANELS:
        assert x_start[m] - Rpx > 4 and x_pre[m] - Rpx > 4, f"the {m} ball starts off the frame"
        assert x_end[m] - Rpx > 4 and x_end[m] + Rpx < W - 4, f"the {m} ball leaves the frame"
    assert x_peak + Rpx + 8 < PEAK_LINE_END, "the rise mark meets the ball"
    assert PEAK_LABEL_X < SCALE_X - SCALE_TICK - 8 and SCALE_LABEL_X + sc_top < ROW_X1, "the scale labels do not fit"
    assert SCALE_X - SCALE_TICK > edge + 8, "the scale is not on the step"
    assert x_end["fast"] + Rpx < SCALE_LABEL_X - 8, "the fast ball reaches the scale labels"
    assert step_top - 2.0 * Rpx > ev_y1 + 16 and slab < BAND_H - 4, "the geometry leaves its band"
    assert BAND_Y["fast"] + BAND_H <= int(man["caption_y"] * H), "the bottom band reaches the caption band"
    assert PAYOFF_Y - 20 > int(man["caption_y"] * H) + 90, "the card meets the caption band"
    return ev


def legend_text(man: dict) -> str:
    return f"same ball, same step, 1/{man['slow']:g} speed"


def clock_text(t: float) -> str:
    return "before the touch" if t < 0.0 else f"{t:.3f} s after the touch"


def label_text(man: dict, m: str) -> str:
    return f"ball at {man['v0_m_s'][m]:g} m/s"


def speed_text(v: float) -> str:
    return f"speed {abs(v):.2f} m/s"


def state_text(phase: str) -> str:
    return phase


def rise_text(rise: float) -> str:
    return f"rise {max(0.0, rise) * 100:.1f} cm"


def spin_text(om: float) -> str:
    return f"spin {abs(om) / (2.0 * math.pi):.2f} turns/s"


def fixed_text(man: dict, ev: dict, m: str) -> str:
    v0, vstar = man["v0_m_s"][m], ev["geo"]["vstar"]
    return f"limit {vstar:.2f} m/s, {abs(v0 - vstar):.2f} {'over' if v0 > vstar else 'under'}"


def event_text(ev: dict, m: str) -> str:
    rn = ev["runs"][m]
    if rn["over"]:
        return f"over at {rn['t_end']:.2f} s, rolls on at {rn['v_top']:.2f} m/s"
    return f"falls back at {rn['t_end']:.2f} s, rose {rn['rise'] * 100:.1f} of {rn['h'] * 100:g} cm"


def scale_top_text(h: float) -> str:
    return f"{h * 100:g} cm"


def scale_bottom_text() -> str:
    return "0"


def peak_text(rise: float) -> str:
    return f"{rise * 100:.1f} cm"


def payoff_lines(man: dict, ev: dict) -> list[str]:
    rs, rf, geo = ev["runs"]["slow"], ev["runs"]["fast"], ev["geo"]
    text = man["payoff_text"].format(vstar=geo["vstar"], rise=rs["rise"] * 100, t_back=rs["t_end"], v_back=rs["v_back"],
                                     t_over=rf["t_end"], v_top=rf["v_top"], keep=geo["keep"], v_zero=geo["v_zero"])
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
        self.S = man["slow"]
        self.P = man["cycle_s"]
        self.P_f = int(round(man["cycle_s"] * self.fps))
        self.c0_f = int(round(man["first_cycle_at"] * self.fps))
        self.ta, self.F = man["touch_at"], man["reset_fade"]
        self.runs = ev["runs"]
        self.R, self.h = man["radius_m"], man["step_m"]
        self.edge = float(man["edge_x_px"])
        self.floor = float(man["floor_dy"])
        self.slab = float(man["slab_dy"])
        self.step_top = self.floor - self.h * self.ppm
        self.t_start = (0.0 - self.ta) / self.S          # real time at the cycle start

    def phase(self, f: int) -> tuple[int, float]:
        k, tau_f = divmod(f - self.c0_f, self.P_f)
        return k, tau_f / self.fps

    @staticmethod
    def L_(x: float, y: float) -> tuple[float, float]:
        """Layer (2x) pixel of a band-local point, rounded to 1e-4 px so equal states draw equal pixels."""
        return round(x * SS, 4), round(y * SS, 4)

    def pos(self, st: dict) -> tuple[float, float]:
        """Band-local centre of the ball."""
        return self.edge + st["x"] * self.ppm, self.floor - st["y"] * self.ppm

    def draw_floor(self, d: ImageDraw.ImageDraw, on_edge: bool) -> None:
        # The floor slab across the band, the step slab from the edge to the right, lighter top lines.
        s0, s1 = self.L_(-12.0, self.floor), self.L_(W + 12.0, self.slab)
        d.rectangle((s0[0], s0[1], s1[0], s1[1]), fill=DECK_A)
        p0, p1 = self.L_(self.edge, self.step_top), self.L_(W + 12.0, self.slab)
        d.rectangle((p0[0], p0[1], p1[0], p1[1]), fill=DECK_A)
        d.line((*self.L_(-12.0, self.floor), *self.L_(self.edge, self.floor)), fill=DECK_B, width=3 * SS)
        d.line((*self.L_(self.edge, self.step_top), *self.L_(W + 12.0, self.step_top)), fill=DECK_B, width=3 * SS)
        d.line((*self.L_(self.edge, self.step_top), *self.L_(self.edge, self.floor)), fill=RIM, width=3 * SS)
        # The height scale on the step's side: a spine with a tick every centimetre.
        for j in range(int(round(self.h * 100)) + 1):
            y = self.floor - j * 0.01 * self.ppm
            d.line((*self.L_(SCALE_X - SCALE_TICK, y), *self.L_(SCALE_X + SCALE_TICK, y)), fill=INK, width=2 * SS)
        d.line((*self.L_(SCALE_X, self.step_top), *self.L_(SCALE_X, self.floor)), fill=INK, width=2 * SS)
        # The edge: a small bright corner mark, gold with a ring while the ball pivots on it.
        col = GOLD if on_edge else WHITE
        e = self.L_(self.edge, self.step_top)
        r = EDGE_MARK * SS
        d.rectangle((e[0] - r, e[1] - r, e[0] + r, e[1] + r), fill=col)
        if on_edge:
            rr = EDGE_RING * SS
            d.ellipse((e[0] - rr, e[1] - rr, e[0] + rr, e[1] + rr), outline=GOLD, width=2 * SS)

    def dashed_path(self, d: ImageDraw.ImageDraw, pts: list[tuple[float, float]], col, dash: float, gap: float,
                    width: int) -> None:
        """Dashes along a polyline (layer px) by arc length."""
        if len(pts) < 2:
            return
        seg = []
        total = 0.0
        for (ax, ay), (bx, by) in zip(pts[:-1], pts[1:]):
            ln = math.hypot(bx - ax, by - ay)
            seg.append((ax, ay, bx, by, ln, total))
            total += ln
        if total <= 0.0:
            return

        def at(s: float) -> tuple[float, float]:
            for ax, ay, bx, by, ln, s0 in seg:
                if s <= s0 + ln or (ax, ay, bx, by, ln, s0) is seg[-1]:
                    u = 0.0 if ln <= 0.0 else min(1.0, max(0.0, (s - s0) / ln))
                    return ax + (bx - ax) * u, ay + (by - ay) * u
            return seg[-1][2], seg[-1][3]

        s = 0.0
        while s < total:
            e = min(total, s + dash)
            d.line((*at(s), *at(e)), fill=col, width=width)
            s = e + gap

    def draw_trail(self, d: ImageDraw.ImageDraw, m: str, t: float) -> None:
        if t <= self.t_start:
            return
        n = int(math.floor((t - self.t_start) / 0.001))
        times = [self.t_start + j * 0.001 for j in range(n + 1)] + [t]
        pts = [self.L_(*self.pos(state_at(self.runs[m], tt))) for tt in times]
        self.dashed_path(d, pts, TRAIL, 8 * SS, 6 * SS, 2 * SS)

    def draw_ball(self, d: ImageDraw.ImageDraw, st: dict) -> None:
        cx, cy = self.pos(st)
        X, Y = self.L_(cx, cy)
        Rl = self.R * self.ppm * SS
        d.ellipse((X - Rl, Y - Rl, X + Rl, Y + Rl), fill=BALL_FILL, outline=BALL_EDGE, width=2 * SS)
        c, sn = math.cos(st["th"]), math.sin(st["th"])    # th grows clockwise on screen while the ball rolls right
        d.line((X, Y, X + Rl * 0.80 * c, Y + Rl * 0.80 * sn), fill=SPOKE, width=5 * SS)
        dr = 7.0 * SS
        px, py = X + Rl * 0.80 * c, Y + Rl * 0.80 * sn
        d.ellipse((px - dr, py - dr, px + dr, py + dr), fill=SPOKE)
        dc = 4.0 * SS
        d.ellipse((X - dc, Y - dc, X + dc, Y + dc), fill=SPOKE)

    def scene(self, m: str, tau: float) -> tuple[Image.Image, dict]:
        """The band layer of panel m at tau seconds into a cycle."""
        layer = Image.new("RGB", (W * SS, BAND_H * SS), BG)
        d = ImageDraw.Draw(layer)
        t = (tau - self.ta) / self.S
        run = self.runs[m]
        st = state_at(run, t)
        st["t"], st["tau"] = t, tau
        self.draw_floor(d, st["on_edge"])
        self.draw_trail(d, m, t)
        # The rise marks: the slow ball's peak (a gold dashed line from its bottom to the scale and a gold tick), the
        # fast ball's full step (the top tick gold) once it is over.
        if (not run["over"]) and t >= run["t_peak"]:
            yp = self.floor - run["rise"] * self.ppm
            xp = self.edge - self.R * math.sin(run["phi_peak"]) * self.ppm
            self.dashed_path(d, [self.L_(xp, yp), self.L_(PEAK_LINE_END, yp)], GOLD, 10 * SS, 6 * SS, 3 * SS)
            d.line((*self.L_(SCALE_X - SCALE_TICK - 6, yp), *self.L_(SCALE_X + SCALE_TICK, yp)), fill=GOLD, width=3 * SS)
        if run["over"] and t >= run["t_end"]:
            d.line((*self.L_(SCALE_X - SCALE_TICK - 6, self.step_top), *self.L_(SCALE_X + SCALE_TICK, self.step_top)),
                   fill=GOLD, width=3 * SS)
        self.draw_ball(d, st)
        return layer, st

    def draw_panel(self, m: str, f: int) -> tuple[Image.Image, dict]:
        k, tau = self.phase(f)
        P, F = self.P, self.F
        layer, st = self.scene(m, tau)
        st["alpha"], st["k"] = 1.0, k
        if tau >= P - F:
            # Crossfade to the next cycle's rolling start (the balls are inside the band in both, asserted in measure).
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
            run = self.runs[m]
            a, ph, t = st["alpha"], st["phase"], st["t"]
            d.text((ROW_X0, y0 + LABEL_DY), label_text(man, m), font=self.font, fill=COLOUR[m], anchor="lm")
            d.text((ROW_X0, y0 + SUB_DY), speed_text(st["v"]), font=self.font_small, fill=blend(MUTED, a), anchor="lm")
            d.text((ROW_X0, y0 + FIX_DY), state_text(ph), font=self.font_small,
                   fill=blend(GOLD if st["on_edge"] else TEXT, a), anchor="lm")
            rise = st["y"] - self.R
            if run["over"]:
                at_top = ph == OVER
            else:
                at_top = st["on_edge"] and abs(rise - run["rise"]) < 5e-4
            d.text((ROW_X1, y0 + LABEL_DY), rise_text(rise), font=self.font, fill=blend(GOLD if at_top else TEXT, a), anchor="rm")
            d.text((ROW_X1, y0 + SUB_DY), spin_text(st["spin"]), font=self.font_small, fill=blend(MUTED, a), anchor="rm")
            if hud_alpha > 0.02:
                d.text((ROW_X1, y0 + FIX_DY), fixed_text(man, ev, m), font=self.font_small,
                       fill=blend(GOLD, 0.85 * hud_alpha), anchor="rm")
            lit = t >= run["t_end"]
            if lit:
                d.text((EVENT_X, y0 + EVENT_DY), event_text(ev, m), font=self.font, fill=blend(GOLD, a), anchor="mm")
            # The scale labels on the step's side; the peak label of the slow ball. These sit over the slab, so they
            # fade by alpha compositing (the draw context is RGBA), not by blending towards the background colour.
            d.text((SCALE_LABEL_X, y0 + self.step_top), scale_top_text(self.h), font=self.font_tiny, fill=INK, anchor="lm")
            if run["over"] and lit:
                d.text((SCALE_LABEL_X, y0 + self.step_top), scale_top_text(self.h), font=self.font_tiny,
                       fill=GOLD + (int(round(255 * a)),), anchor="lm")
            d.text((SCALE_LABEL_X, y0 + self.floor), scale_bottom_text(), font=self.font_tiny, fill=INK, anchor="lm")
            if (not run["over"]) and t >= run["t_peak"]:
                d.text((PEAK_LABEL_X, y0 + self.floor - run["rise"] * self.ppm), peak_text(run["rise"]), font=self.font_tiny,
                       fill=GOLD + (int(round(255 * a)),), anchor="rm")
        if hud_alpha > 0.02:
            d.text((W / 2, LEGEND_Y), legend_text(man), font=self.font, fill=blend(TEXT, hud_alpha), anchor="mm")
            d.text((W / 2, CLOCK_Y), clock_text(states["slow"]["t"]), font=self.font_small, fill=blend(MUTED, hud_alpha),
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
        states = {}
        for m in PANELS:
            layer, states[m] = self.draw_panel(m, f)
            img.paste(layer.reduce(SS), (0, BAND_Y[m]))
        d = ImageDraw.Draw(img, "RGBA")
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
            # The geometry runs on; the legend, clock, fixed lines and card fade out over the first half of the
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
    man = json.loads((ROOT / "projects/kerbhop/manifest.json").read_text())
    ev = measure(man)
    if "--measure-only" in sys.argv:
        return
    if "--frames" in sys.argv:
        times = [float(v) for v in sys.argv[sys.argv.index("--frames") + 1].split(",")]
        r = Renderer(man, ev)
        (ROOT / "media/kerbhop").mkdir(parents=True, exist_ok=True)
        for tv in times:
            Image.fromarray(r.frame_at(int(round(tv * man["fps"])))).save(ROOT / f"media/kerbhop/smoke-{tv}.png")
        print("smoke frames: " + ", ".join(f"{tv}" for tv in times))
        return
    Renderer(man, ev).render(ROOT / "media/kerbhop/footage.mp4")


if __name__ == "__main__":
    main()
