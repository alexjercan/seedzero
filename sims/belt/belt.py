#!/usr/bin/env python3
"""Box or ball on a moving belt: which one rides along?

Two panels on the same clock, the same belt drawn the same way at the same
scale: a belt of length L runs at V to the right (its stripes move at V).
At the release a box (top panel) and a solid ball (bottom panel, I = k m
r^2, k = 2/5, a stripe so the spin shows) are set down at rest at the start
line, both with sliding friction mu against the belt. While the bottom of
an object lags the belt, the belt drags it forward with mu m g:

    box:   v' = mu g                          until v = V, then it rides;
    ball:  v' = mu g,  (k r) omega' = mu g    until v + r omega = V,

omega the spin in the sense that moves the bottom point forward. The ball's
slip closes when its bottom point matches the belt, at v = V k / (1 + k)
= 2/7 V over the ground; from then on nothing slips, no friction acts, and
the ball rolls on at that speed, backward on the belt at 5/7 V. The centre
of each object crosses the exit line L on from the start, falls off the
end of the belt and drops out of its panel. No rolling resistance and no
air in the model. The slip is stepped as a Coulomb slip at step_s (Euler
on the speed and the spin, the exact trapezoid on the position, the slip
closure located by linear interpolation inside the step), checked against
the closed forms and a half-step rerun; after the slip the motion is
uniform, so the exit time follows from the stepped end state. The run
repeats every cycle_s seconds of video with a crossfade back to the
resting setup; the cycle divides the scene length and the belt texture is
periodic across it, so the scene is exactly periodic and the last frame
equals the first. Real time. Deterministic, no seed.

Measured and printed: for each panel the slip time, the slip distance and
the settled speed (stepped and closed form), the exit time, the ball's
spin, its speed on the belt and its angular momentum about the belt
surface line through the slip; the other shapes, other grips and the car
footwell for the description; a half-step check; the schedule in video
time; the on-screen text widths and the layout clearances.

usage: belt.py [--measure-only] [--frames t1,t2,...]
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
CARD = (198, 150, 92)
CARD_EDGE = (128, 84, 40)
CARD_TAPE = (226, 202, 158)
BALL_DARK = (140, 52, 48)
BELT = (52, 56, 62)
BELT_EDGE = (110, 116, 124)
BELT_STRIPE = (96, 102, 110)
BELT_AXLE = (26, 28, 32)
INK = (150, 158, 170)

# Layout: overlay at y 96..130 (captions.py), two title rows at y 190/252 for
# the first seconds, then the legend at y 236 and the shared clock at y 290;
# two panels stacked, the box in the band y 330..880 and the ball in y
# 880..1430, each drawn at 2x in its own geometry layer (so a falling object
# is clipped at its band); each band has its label row 40 px under the band
# top, its second row at 84 and its third at 120 (left column from x 40,
# right column to x 1040); the gold event row at 300; the belt surface 380
# px under the band top (y 710 and 1260), the belt body to 416, the marks
# under it at 458; captions at caption_y 0.75 (y 1440..1530); the six-line
# card from y 1572 at a 48 px pitch.
LEGEND_Y, CLOCK_Y = 236, 290
SS = 2
PAYOFF_Y, PAYOFF_PITCH = 1572.0, 48
PANELS = ("box", "ball")
BAND_Y = {"box": 330, "ball": 880}
BAND_H = 550
LABEL_DY, SUB_DY, FIX_DY, EVENT_DY, BELT_DY, BELT_TH, MARK_DY = 40, 84, 120, 300, 380, 36, 458
ROW_X0, ROW_X1 = 40, 1040
COLOUR = {"box": CARD, "ball": CORAL}
HELD, SLIP, RIDE, OFF = "held", "slip", "ride", "off"


def blend(col, a: float, base=BG) -> tuple:
    a = max(0.0, min(1.0, a))
    return tuple(int(round(c * a + b * (1 - a))) for c, b in zip(col, base))


# --- measurement --------------------------------------------------------------
def closed(V: float, mu: float, g: float, k: float | None) -> tuple[float, float, float]:
    """(slip time, settled speed, slip distance) in closed form; k None for the box (no spin)."""
    a = mu * g
    if k is None:
        t, v = V / a, V
    else:
        t, v = V * k / (a * (1.0 + k)), V * k / (1.0 + k)
    return t, v, 0.5 * a * t * t


def stepped(V: float, mu: float, g: float, k: float | None, r: float, dt: float) -> dict:
    """Coulomb slip stepped at dt from rest at the start line: friction mu m g forward while the bottom
    point lags the belt; Euler on v and omega (exact here: the accelerations are constant), the trapezoid
    on x, the slip closure located by linear interpolation inside the step. Also the largest angular
    momentum about the belt surface line seen during the slip, per unit mass (k r^2 omega - r v)."""
    a = mu * g
    alpha = a / (k * r) if k is not None else 0.0
    x = v = w = t = 0.0
    n = 0
    L_max = 0.0

    def contact(v_: float, w_: float) -> float:
        return v_ + (r * w_ if k is not None else 0.0) - V

    while True:
        vc = contact(v, w)
        if vc >= 0.0:
            break
        v_new, w_new = v + a * dt, w + alpha * dt
        vc_new = contact(v_new, w_new)
        if vc_new >= 0.0:
            h = -vc / (vc_new - vc) * dt
            x += v * h + 0.5 * a * h * h
            v, w, t = v + a * h, w + alpha * h, t + h
            n += 1
            break
        x += 0.5 * (v + v_new) * dt
        v, w, t = v_new, w_new, t + dt
        n += 1
        if k is not None:
            L_max = max(L_max, abs(k * r * r * w - r * v))
    return {"t": t, "v": v, "w": w, "x": x, "steps": n, "L_max": L_max, "k": k, "r": r, "V": V}


def run_for(man: dict, k: float | None, mu: float, dt: float) -> dict:
    V, g, L = man["belt_speed_m_s"], man["g"], man["belt_length_m"]
    r = man["ball_radius_m"]
    st = stepped(V, mu, g, k, r, dt)
    st["t_off"] = st["t"] + (L - st["x"]) / st["v"]
    st["theta"] = 0.5 * (mu * g / (k * r) if k is not None else 0.0) * st["t"] * st["t"]
    tc, vc, dc = closed(V, mu, g, k)
    st["closed"] = {"t": tc, "v": vc, "d": dc, "t_off": tc + (L - dc) / vc}
    st["mu"], st["g"], st["L"] = mu, g, L
    return st


def state_at(run: dict, rt: float) -> dict:
    """(x, v, omega, theta, phase, drop) of the object rt seconds after the release."""
    k, r = run["k"], run["r"]
    a = run["mu"] * run["g"]
    alpha = a / (k * r) if k is not None else 0.0
    if rt < 0.0:
        return {"x": 0.0, "v": 0.0, "w": 0.0, "theta": 0.0, "phase": HELD, "drop": 0.0}
    if rt < run["t"]:
        return {"x": 0.5 * a * rt * rt, "v": a * rt, "w": alpha * rt, "theta": 0.5 * alpha * rt * rt,
                "phase": SLIP, "drop": 0.0}
    if rt < run["t_off"]:
        d = rt - run["t"]
        return {"x": run["x"] + run["v"] * d, "v": run["v"], "w": run["w"], "theta": run["theta"] + run["w"] * d,
                "phase": RIDE, "drop": 0.0}
    d = rt - run["t_off"]
    return {"x": run["L"] + run["v"] * d, "v": run["v"], "w": run["w"],
            "theta": run["theta"] + run["w"] * (rt - run["t"]), "phase": OFF, "drop": 0.5 * run["g"] * d * d}


def measure(man: dict) -> dict:
    V, g, L, mu = man["belt_speed_m_s"], man["g"], man["belt_length_m"], man["mu"]
    a_box, r_ball, k_ball = man["box_side_m"], man["ball_radius_m"], man["k_ball"]
    dt = man["step_s"]
    P, D, fps, F, pa = man["cycle_s"], man["scene_duration"], man["fps"], man["reset_fade"], man["place_at"]
    cycles = D / P
    assert abs(cycles - round(cycles)) < 1e-9, "the cycle must divide the scene length"
    for key in ("cycle_s", "place_at", "first_cycle_at", "reset_fade"):
        assert abs(man[key] * fps - round(man[key] * fps)) < 1e-9, f"{key} must be a whole number of frames"
    ppm = man["px_per_m"]
    print(f"setup: the same belt in both panels, {L:g} m from the start line to the exit line, running at V = {V:g} m/s "
          f"to the right (stripes every {man['texture_period_m']:g} m move with it); at the release a box of side "
          f"{a_box * 100:g} cm (top panel, no spin) and a solid ball of radius {r_ball * 100:g} cm (bottom panel, I = "
          f"{k_ball:g} m r^2, a stripe on it) are set down at rest at the start line, both with sliding friction "
          f"coefficient {mu:g} against the belt; while the bottom of an object lags the belt the belt drags it forward "
          f"with mu m g = {mu * g:.4f} m/s^2 on the centre (and mu g / (k r) = {mu * g / (k_ball * r_ball):.2f} rad/s^2 "
          f"on the ball's spin); once the bottom point matches the belt nothing slips and no friction acts; each "
          f"object leaves when its centre crosses the exit line, then falls off the end of the belt (g = {g:g} m/s^2) "
          f"and drops out of its panel; no rolling resistance and no air (a real ball would creep up to the belt "
          f"speed); the slip stepped as a Coulomb slip at dt = {dt:.0e} s, checked against the closed forms and a "
          f"half-step rerun; shown in real time on a {P:g} s cycle ({P * fps:.0f} frames) with the release {pa:g} s "
          f"into the cycle, {cycles:.0f} cycles in {D:g} s; drawn at {ppm:g} px per metre; deterministic, no seed")
    runs = {"box": run_for(man, None, mu, dt), "ball": run_for(man, k_ball, mu, dt)}
    ev: dict = {"runs": runs}
    b = runs["box"]
    c = b["closed"]
    print(f"box: stepped slip: at belt speed after {b['t']:.4f} s (closed form V / (mu g) = {c['t']:.4f} s, diff "
          f"{b['t'] - c['t']:+.1e} s) and {b['x'] * 100:.2f} cm of slip (closed form V^2 / (2 mu g) = {c['d'] * 100:.2f} "
          f"cm, diff {(b['x'] - c['d']) * 100:+.1e} cm), {b['steps']} steps; speed then {b['v']:.6f} m/s = the belt's "
          f"({b['v'] / V:.4f} V), 0 m/s on the belt, so the belt has nothing left to drag and the box rides; its "
          f"centre crosses the exit line {L:g} m on at {b['t_off']:.4f} s (closed form t + (L - d) / V = {c['t_off']:.4f} "
          f"s, diff {b['t_off'] - c['t_off']:+.1e} s), at belt speed")
    s = runs["ball"]
    c = s["closed"]
    bottom = s["v"] + r_ball * s["w"]
    print(f"ball: stepped slip: the slip ends after {s['t']:.4f} s (closed form V k / (mu g (1 + k)) = {c['t']:.4f} s, "
          f"diff {s['t'] - c['t']:+.1e} s) and {s['x'] * 100:.2f} cm (closed form {c['d'] * 100:.2f} cm, diff "
          f"{(s['x'] - c['d']) * 100:+.1e} cm), {s['steps']} steps; speed over the ground then {s['v']:.4f} m/s = "
          f"{s['v'] / V:.4f} of the belt speed (closed form V k / (1 + k) = 2/7 V = {c['v']:.4f} m/s, diff "
          f"{s['v'] - c['v']:+.1e} m/s); spin {s['w']:.2f} rad/s ({s['w'] / (2 * math.pi):.2f} turns a second, bottom "
          f"point moving forward), r omega = {r_ball * s['w']:.4f} m/s, so the bottom point moves at v + r omega = "
          f"{bottom:.6f} m/s = the belt's and the slip is closed; on the belt the centre moves at v - V = "
          f"{s['v'] - V:+.4f} m/s ({(V - s['v']) / V:.4f} V backward, 5/7 = {5 / 7:.4f}): it rolls backward on the "
          f"belt; angular momentum about the belt surface line per unit mass k r^2 omega - r v stays within "
          f"{s['L_max'] / (r_ball * V):.1e} of zero (in m r V) through the slip (the friction acts along that line), "
          f"and m v (1 + k) = {s['v'] * (1 + k_ball):.4f} m = k m V = {k_ball * V:.4f} m; from then on no friction "
          f"acts, v and the spin hold, and its centre crosses the exit line at {s['t_off']:.4f} s (closed form t + "
          f"(L - d) / v = {c['t_off']:.4f} s, diff {s['t_off'] - c['t_off']:+.1e} s), still at {s['v']:.4f} m/s")
    assert abs(bottom - V) < 1e-9 and abs(s["v"] - c["v"]) < 1e-6 and abs(b["v"] - V) < 1e-9
    print(f"the two panels: the box leaves at {b['t_off']:.4f} s at {b['v']:.4f} m/s (belt speed); the ball leaves at "
          f"{s['t_off']:.4f} s at {s['v']:.4f} m/s ({s['v'] / V:.4f} of the belt speed, 2/7 = {2 / 7:.4f}), "
          f"{s['t_off'] / b['t_off']:.2f} times as long on the belt; on the belt the box sits still (0 m/s) and the "
          f"ball rolls backward at {V - s['v']:.4f} m/s; both feel the same drag mu m g, but the ball's drag also spins "
          f"it, and the spin matches the belt after {s['t']:.4f} s, when the centre has only {s['v'] / V:.4f} V")
    ev["shapes"] = {}
    descr = []
    for name, k in man["description_shapes"]:
        rr = run_for(man, k, mu, dt)
        ev["shapes"][name] = rr["v"] / V
        descr.append(f"{name} (k = {k:.4f}): settles at {rr['v']:.4f} m/s = {rr['v'] / V:.4f} V (closed form k / (1 + k) = "
                     f"{k / (1 + k):.4f}) after {rr['t']:.4f} s and {rr['x'] * 100:.2f} cm, off at {rr['t_off']:.3f} s")
    for m2 in man["description_mus"]:
        rr = run_for(man, k_ball, m2, dt)
        descr.append(f"the solid ball with grip {m2:g}: settles at {rr['v'] / V:.4f} V after {rr['t']:.4f} s and "
                     f"{rr['x'] * 100:.2f} cm, off at {rr['t_off']:.3f} s")
    a_car = man["car_g"] * g
    a_ball_car = a_car / (1.0 + k_ball)
    mu_need = man["car_g"] * k_ball / (1.0 + k_ball)
    descr.append(f"the same physics in a car pulling {man['car_g']:g} g (a = {a_car:.4f} m/s^2): a footwell ball rolls "
                 f"back at a / (1 + k) = 5/7 a = {a_ball_car:.4f} m/s^2, 1 m in {math.sqrt(2.0 / a_ball_car):.4f} s, "
                 f"rolling without slipping if the grip is at least a k / (g (1 + k)) = {mu_need:.4f}; a box with grip "
                 f"{mu:g} stays put since {man['car_g']:g} g is under {mu:g} g")
    ev["car"] = {"a": a_ball_car, "t1m": math.sqrt(2.0 / a_ball_car), "mu": mu_need}
    print("for the description (same belt, same grip unless said): " + "; ".join(descr))
    half = {m: run_for(man, None if m == "box" else k_ball, mu, 0.5 * dt) for m in PANELS}
    print(f"check at half the time step ({0.5 * dt:.0e} s): " + "; ".join(
        f"{m} slip {half[m]['t']:.7f} s ({half[m]['t'] - runs[m]['t']:+.1e}), {half[m]['x'] * 100:.7f} cm "
        f"({(half[m]['x'] - runs[m]['x']) * 100:+.1e}), speed {half[m]['v']:.7f} m/s ({half[m]['v'] - runs[m]['v']:+.1e}), "
        f"off at {half[m]['t_off']:.7f} s ({half[m]['t_off'] - runs[m]['t_off']:+.1e})" for m in PANELS))
    # Schedule in video time (real time, no slow motion).
    t0 = man["first_cycle_at"]
    k0 = math.ceil((0.0 - t0) / P - 1e-9) - 1
    k1 = math.floor((D - t0) / P - 1e-9)
    starts = [t0 + k * P for k in range(k0, k1 + 1)]
    ev["cycles"] = int(round(cycles))

    def lst(off_: float) -> str:
        return ", ".join(f"{st + off_:.2f}" for st in starts if 0.0 <= st + off_ < D)

    sx = man["start_x_px"]
    ex = sx + L * ppm
    r_px, half_box = r_ball * ppm, a_box / 2.0 * ppm
    # The box flies off the right frame edge; the ball drops out of the bottom of its band.
    t_box_gone = (W + half_box + 2.0 - ex) / ppm / b["v"]
    drop_ball = (BAND_H - BELT_DY + 2.0 * r_px + 2.0) / ppm
    t_ball_gone = math.sqrt(2.0 * drop_ball / g)
    x_ball_gone = (ex + s["v"] * t_ball_gone * ppm)
    drop_box_at_edge = 0.5 * g * t_box_gone ** 2 * ppm
    ev["gone"] = {"box": b["t_off"] + t_box_gone, "ball": s["t_off"] + t_ball_gone}
    for m in PANELS:
        assert pa + ev["gone"][m] < P - F, f"the {m} is still on the frame at the reset fade"
    assert x_ball_gone + r_px < W, "the ball leaves the frame at the right edge, not the band bottom"
    assert drop_box_at_edge + 2 * half_box < BAND_H - BELT_DY, "the box drops out of its band before the frame edge"
    tau0 = (0.0 - t0) % P
    r0 = tau0 - pa
    st0 = {m: state_at(runs[m], r0) for m in PANELS}
    shift = V * ppm * SS / fps
    period = man["texture_period_m"] * ppm * SS
    assert abs(shift - round(shift)) < 1e-9 and abs(period - round(period)) < 1e-9, "texture shift must be whole layer px"
    total = int(round(D * fps))
    assert (total * int(round(shift))) % int(round(period)) == 0, "the belt texture is not periodic over the scene"
    print(f"schedule (video time, real time): cycles of {P:g} s start at " + ", ".join(f"{st:.2f}" for st in starts)
          + f" s (the first {-t0:.2f} s before the first frame); the objects are set down at rest {pa:g} s into each "
          f"cycle at {lst(pa)} s; the box is at belt speed at {lst(pa + b['t'])} s and crosses the exit line at "
          f"{lst(pa + b['t_off'])} s (off the frame {t_box_gone:.2f} s later, having dropped {drop_box_at_edge / ppm * 100:.1f} "
          f"cm); the ball's slip ends at {lst(pa + s['t'])} s and it crosses the exit line at {lst(pa + s['t_off'])} s "
          f"(out of its band {t_ball_gone:.2f} s later at x {x_ball_gone:.0f} px); the reset crossfade runs over the "
          f"last {F:g} s of each cycle (the readouts out from {lst(P - F)} s, the resting objects in from "
          f"{lst(P - F / 2)} s); on the first frame the cycle is {tau0:.2f} s in ({r0:.2f} s after the release: the box "
          f"at {st0['box']['x'] * 100:.1f} cm and {st0['box']['v']:.2f} m/s, the ball at {st0['ball']['x'] * 100:.1f} cm "
          f"and {st0['ball']['v']:.2f} m/s, {st0['ball']['phase']}); title until {man['title_until']:g} s; payoff card "
          f"from {man['payoff_t']:g} s; the title fades back in over the last {man['loop_fade']:g} s and the last frame "
          f"repeats the first (the scene is periodic: {D:g} s holds exactly {cycles:.0f} cycles); belt texture: "
          f"{shift / SS:g} px per frame, period {period / SS:g} px, {total * shift / period:.0f} periods in {D:g} s (a whole "
          f"number, so the stripes match across the seam)")
    # Text widths.
    font = os.environ["SEED_ZERO_FONT"]
    f24, f28, f34, f40, f56 = (ImageFont.truetype(font, n) for n in (24, 28, 34, 40, 56))
    widths = {"overlay@34": (f34, man["overlay"])}
    for j, line in enumerate(man["title"].split("|")):
        widths[f"title line {j + 1}@56"] = (f56, line)
    widths["legend@40"] = (f40, legend_text(man))
    widths["clock@28"] = (f28, clock_text(7.04))
    widths["clock held@28"] = (f28, clock_text(-1.0))
    for m in PANELS:
        widths[f"label {m}@40"] = (f40, label_text(m))
        widths[f"sublabel {m}@28"] = (f28, sub_text(man, m))
        widths[f"fixed {m}@28"] = (f28, fixed_text(ev, m))
        widths[f"readout {m}@40"] = (f40, ground_text(1.0))
        widths[f"readout off {m}@40"] = (f40, ground_off_text())
        widths[f"on belt {m}@28"] = (f28, belt_text(-1.0))
        widths[f"spin {m}@28"] = (f28, spin_text(m, 2.85))
        for ph in (RIDE, OFF):
            widths[f"event {m} {ph}@40"] = (f40, event_text(ev, m, ph))
    widths["start@24"] = (f24, "start")
    widths["exit@24"] = (f24, exit_text(man))
    widths["belt arrow@24"] = (f24, arrow_text(man))
    for j, line in enumerate(payoff_lines(man, ev)):
        widths[f"payoff line {j + 1}@40"] = (f40, line)
    print("text widths: " + ", ".join(f"{k} {f.getlength(s):.0f} px" for k, (f, s) in widths.items()))
    assert all(f.getlength(s) < 950 for f, s in widths.values()), "a text line is wider than 950 px"
    # Layout checks.
    left = ROW_X0 + max(max(f40.getlength(label_text(m)), f28.getlength(sub_text(man, m)), f28.getlength(fixed_text(ev, m)))
                        for m in PANELS)
    right = ROW_X1 - max(max(f40.getlength(ground_text(1.0)), f28.getlength(belt_text(-1.0)),
                             f28.getlength(spin_text(m, 2.85))) for m in PANELS)
    rows_bottom = FIX_DY + 16
    event_top, event_bottom = EVENT_DY - 22, EVENT_DY + 22
    obj_top = BELT_DY - 2.0 * max(r_px, half_box)
    ev_w = max(f40.getlength(event_text(ev, m, ph)) for m in PANELS for ph in (RIDE, OFF))
    print(f"row check: the left column ends at x {left:.0f} px, the right column starts at x {right:.0f} px; both end "
          f"{rows_bottom} px under the band top; the event row spans {event_top} to {event_bottom} px under the band top "
          f"(widest {ev_w:.0f} px, centred), the objects' tops sit {obj_top:.0f} px under the band top on the belt at "
          f"{BELT_DY}; the marks under the belt at {MARK_DY} px; each band is {BAND_H} px tall (y {BAND_Y['box']} to "
          f"{BAND_Y['box'] + BAND_H} and {BAND_Y['ball']} to {BAND_Y['ball'] + BAND_H}); the caption band starts at y "
          f"{int(man['caption_y'] * H)}; the title rows end at y {252 + 28} and the overlay band ends at y 130")
    assert right - left > 40, "the columns meet"
    assert event_top - rows_bottom > 20 and obj_top - event_bottom > 10, "the event row meets the rows or the objects"
    assert BAND_Y["ball"] + BAND_H <= int(man["caption_y"] * H), "the ball band reaches the caption band"
    assert MARK_DY + 14 < BAND_H, "the marks leave the band"
    return ev


def legend_text(man: dict) -> str:
    return f"same belt at {man['belt_speed_m_s']:g} m/s, real time"


def clock_text(r: float) -> str:
    return "held at the start line" if r < 0.0 else f"{r:.2f} s after the release"


def label_text(m: str) -> str:
    return "box" if m == "box" else "ball"


def sub_text(man: dict, m: str) -> str:
    return f"placed at rest, grip {man['mu']:g}"


def fixed_text(ev: dict, m: str) -> str:
    return f"off the belt at {ev['runs'][m]['t_off']:.2f} s"


def ground_text(v: float) -> str:
    return f"ground speed {v:.2f} m/s"


def ground_off_text() -> str:
    return "off the belt"


def belt_text(rel: float) -> str:
    return f"on the belt {rel:+.2f} m/s"


def spin_text(m: str, turns: float) -> str:
    return "no spin" if m == "box" else f"spin {abs(turns):.1f} turns/s"


def event_text(ev: dict, m: str, ph: str) -> str:
    run = ev["runs"][m]
    if ph not in (RIDE, OFF):
        return ""
    if m == "box":
        return f"at belt speed after {run['t']:.2f} s" if ph == RIDE else f"off at {run['t_off']:.2f} s, at belt speed"
    if ph == RIDE:
        return f"2/7 of the belt speed, {run['v']:.2f} m/s"
    return f"off at {run['t_off']:.2f} s, at 2/7 of the belt speed"


def exit_text(man: dict) -> str:
    return f"exit, {man['belt_length_m']:g} m"


def arrow_text(man: dict) -> str:
    return f"belt {man['belt_speed_m_s']:g} m/s"


def payoff_lines(man: dict, ev: dict) -> list[str]:
    b, s = ev["runs"]["box"], ev["runs"]["ball"]
    text = man["payoff_text"].format(
        t_off_box=b["t_off"], t_off_ball=s["t_off"], v_ball=s["v"], t_box=b["t"], d_box=b["x"] * 100,
        t_ball=s["t"], d_ball=s["x"] * 100)
    return [t.strip() for t in text.split("|")]


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
        self.sx = float(man["start_x_px"])
        self.ex = self.sx + man["belt_length_m"] * self.ppm
        self.lx = self.sx - man["belt_lead_m"] * self.ppm
        self.P = man["cycle_s"]
        self.P_f = int(round(man["cycle_s"] * self.fps))
        self.c0_f = int(round(man["first_cycle_at"] * self.fps))
        self.pa, self.F = man["place_at"], man["reset_fade"]
        self.runs = ev["runs"]
        self.r_ball = man["ball_radius_m"]
        self.a_box = man["box_side_m"]
        self.shift = int(round(man["belt_speed_m_s"] * self.ppm * SS / self.fps))
        self.period = int(round(man["texture_period_m"] * self.ppm * SS))

    def phase(self, f: int) -> tuple[int, float]:
        k, tau_f = divmod(f - self.c0_f, self.P_f)
        return k, tau_f / self.fps

    @staticmethod
    def L(x: float, y: float) -> tuple[float, float]:
        """Layer (2x) pixel of a band-local point, rounded to 1e-4 px so equal states draw equal pixels."""
        return round(x * SS, 4), round(y * SS, 4)

    def draw_belt(self, d: ImageDraw.ImageDraw, f: int) -> None:
        ys, th = float(BELT_DY), float(BELT_TH)
        rad = th / 2.0
        p0, p1 = self.L(self.lx - rad, ys), self.L(self.ex + rad, ys + th)
        d.rounded_rectangle((p0[0], p0[1], p1[0], p1[1]), radius=rad * SS, fill=BELT)
        # Stripes every texture period, moving with the belt (whole layer pixels per frame, so the
        # pattern is exactly periodic over the scene); only on the flat run between the rollers.
        offset = (f * self.shift) % self.period
        x0 = (self.lx + rad) * SS
        x1 = (self.ex - rad) * SS
        j = -1
        while True:
            x = x0 + offset + j * self.period
            if x > x1:
                break
            if x >= x0 and x + 14 * SS <= x1:
                poly = [(x, (ys + 4) * SS), (x + 6 * SS, (ys + 4) * SS), (x + 14 * SS, (ys + th - 4) * SS),
                        (x + 8 * SS, (ys + th - 4) * SS)]
                d.polygon(poly, fill=BELT_STRIPE)
            j += 1
        e0, e1 = self.L(self.lx, ys), self.L(self.ex, ys)
        d.line((*e0, e1[0], e1[1]), fill=BELT_EDGE, width=2 * SS)
        for xa in (self.lx, self.ex):
            c = self.L(xa, ys + rad)
            rr = 4 * SS
            d.ellipse((c[0] - rr, c[1] - rr, c[0] + rr, c[1] + rr), fill=BELT_AXLE)
        # The start and exit marks: gold notches under the belt.
        for xm in (self.sx, self.ex):
            m0, m1, m2 = self.L(xm, ys + th + 3), self.L(xm - 9, ys + th + 18), self.L(xm + 9, ys + th + 18)
            d.polygon([m0, m1, m2], fill=GOLD)
        # The belt direction arrow under the middle of the belt.
        ax0, ax1, ay = W / 2 + 70.0, W / 2 + 150.0, float(MARK_DY)
        q0, q1 = self.L(ax0, ay), self.L(ax1 - 14, ay)
        d.line((*q0, *q1), fill=INK, width=3 * SS)
        tip, b1, b2 = self.L(ax1, ay), self.L(ax1 - 16, ay - 8), self.L(ax1 - 16, ay + 8)
        d.polygon([tip, b1, b2], fill=INK)

    def draw_box(self, d: ImageDraw.ImageDraw, cx: float, drop: float) -> None:
        h = self.a_box / 2.0 * self.ppm
        yb = BELT_DY + drop * self.ppm
        p0, p1 = self.L(cx - h, yb - 2 * h), self.L(cx + h, yb)
        d.rectangle((p0[0], p0[1], p1[0], p1[1]), fill=CARD, outline=CARD_EDGE, width=2 * SS)
        t0, t1 = self.L(cx - 3, yb - 2 * h + 2), self.L(cx + 3, yb - 2)
        d.rectangle((t0[0], t0[1], t1[0], t1[1]), fill=CARD_TAPE)
        l0, l1 = self.L(cx - h + 2, yb - 2 * h + 12), self.L(cx + h - 2, yb - 2 * h + 12)
        d.line((*l0, *l1), fill=CARD_EDGE, width=2 * SS)

    def draw_ball(self, d: ImageDraw.ImageDraw, cx: float, drop: float, theta: float) -> None:
        R = self.r_ball * self.ppm
        cy = BELT_DY - R + drop * self.ppm
        X, Y = self.L(cx, cy)
        Rl = R * SS
        d.ellipse((X - Rl, Y - Rl, X + Rl, Y + Rl), fill=CORAL, outline=BALL_DARK, width=2 * SS)
        phi = -theta            # the spin moves the bottom point forward: counterclockwise on screen
        c, sn = math.cos(phi), math.sin(phi)
        d.line((X - Rl * 0.84 * c, Y - Rl * 0.84 * sn, X + Rl * 0.84 * c, Y + Rl * 0.84 * sn), fill=WHITE, width=4 * SS)
        dr = 3.2 * SS
        px, py = X + Rl * 0.6 * sn, Y - Rl * 0.6 * c
        d.ellipse((px - dr, py - dr, px + dr, py + dr), fill=WHITE)

    def draw_object(self, layer: Image.Image, m: str, st: dict) -> None:
        d = ImageDraw.Draw(layer)
        cx = self.sx + st["x"] * self.ppm
        if m == "box":
            self.draw_box(d, cx, st["drop"])
        else:
            self.draw_ball(d, cx, st["drop"], st["theta"])

    def draw_panel(self, m: str, f: int) -> tuple[Image.Image, dict]:
        layer = Image.new("RGB", (W * SS, BAND_H * SS), BG)
        d = ImageDraw.Draw(layer)
        self.draw_belt(d, f)
        k, tau = self.phase(f)
        F, P = self.F, self.P
        run = self.runs[m]
        a_old = 1.0 if tau <= P - F else max(0.0, (P - F / 2.0 - tau) / (F / 2.0))
        st = state_at(run, tau - self.pa)
        st["r"], st["alpha"], st["k"] = tau - self.pa, a_old, k
        if a_old > 0.0:
            self.draw_object(layer, m, st)           # off the band by the fade (asserted in measure)
        if tau >= P - F / 2.0:
            a_new = (tau - (P - F / 2.0)) / (F / 2.0)
            st_new = state_at(run, tau - P - self.pa)
            st_new["r"], st_new["alpha"], st_new["k"] = tau - P - self.pa, a_new, k + 1
            with_new = layer.copy()
            self.draw_object(with_new, m, st_new)
            layer = Image.blend(layer, with_new, a_new)
            if a_new >= 0.5:
                st = st_new
        return layer, st

    def draw_text(self, d: ImageDraw.ImageDraw, states: dict, hud_alpha: float) -> None:
        man, ev = self.man, self.ev
        V = man["belt_speed_m_s"]
        for m, st in states.items():
            y0 = BAND_Y[m]
            a, ph = st["alpha"], st["phase"]
            d.text((ROW_X0, y0 + LABEL_DY), label_text(m), font=self.font, fill=COLOUR[m], anchor="lm")
            d.text((ROW_X0, y0 + SUB_DY), sub_text(man, m), font=self.font_small, fill=MUTED, anchor="lm")
            if hud_alpha > 0.02:
                d.text((ROW_X0, y0 + FIX_DY), fixed_text(ev, m), font=self.font_small,
                       fill=blend(GOLD, 0.85 * hud_alpha), anchor="lm")
            if ph == OFF:
                d.text((ROW_X1, y0 + LABEL_DY), ground_off_text(), font=self.font, fill=blend(MUTED, a), anchor="rm")
            else:
                settled = ph == RIDE
                d.text((ROW_X1, y0 + LABEL_DY), ground_text(st["v"]), font=self.font,
                       fill=blend(GOLD if settled else TEXT, a), anchor="rm")
                d.text((ROW_X1, y0 + SUB_DY), belt_text(st["v"] - V), font=self.font_small, fill=blend(MUTED, a),
                       anchor="rm")
                turns = st["w"] / (2.0 * math.pi)
                d.text((ROW_X1, y0 + FIX_DY), spin_text(m, turns), font=self.font_small,
                       fill=blend(CORAL if m == "ball" else MUTED, a), anchor="rm")
            txt = event_text(ev, m, ph)
            if txt:
                d.text((W / 2, y0 + EVENT_DY), txt, font=self.font, fill=blend(GOLD, a), anchor="mm")
            ys = y0 + BELT_DY + BELT_TH
            d.text((self.sx, y0 + MARK_DY), "start", font=self.font_tiny, fill=INK, anchor="mm")
            d.text((self.ex, y0 + MARK_DY), exit_text(man), font=self.font_tiny, fill=INK, anchor="mm")
            d.text((W / 2 + 60, y0 + MARK_DY), arrow_text(man), font=self.font_tiny, fill=INK, anchor="rm")
        if hud_alpha > 0.02:
            d.text((W / 2, LEGEND_Y), legend_text(man), font=self.font, fill=blend(TEXT, hud_alpha), anchor="mm")
            d.text((W / 2, CLOCK_Y), clock_text(states["ball"]["r"]), font=self.font_small,
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
    man = json.loads((ROOT / "projects/belt/manifest.json").read_text())
    ev = measure(man)
    if "--measure-only" in sys.argv:
        return
    if "--frames" in sys.argv:
        times = [float(v) for v in sys.argv[sys.argv.index("--frames") + 1].split(",")]
        r = Renderer(man, ev)
        (ROOT / "media/belt").mkdir(parents=True, exist_ok=True)
        for tv in times:
            Image.fromarray(r.frame_at(int(round(tv * man["fps"])))).save(ROOT / f"media/belt/smoke-{tv}.png")
        print("smoke frames: " + ", ".join(f"{tv}" for tv in times))
        return
    Renderer(man, ev).render(ROOT / "media/belt/footage.mp4")


if __name__ == "__main__":
    main()
