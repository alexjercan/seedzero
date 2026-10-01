#!/usr/bin/env python3
"""Rope round a post: can two kilos hold twenty kilos?

Two panels on the same clock, the same post and the same rope drawn the
same way at the same scale. A massless, unstretchable rope is wrapped
round a fixed horizontal round post, one full turn (top panel, theta = 2
pi) or two full turns (bottom panel, theta = 4 pi). On one side hangs a
big weight M = 20 kg, on the other a small weight m = 2 kg. The friction
coefficient between rope and post is mu, the same at rest and sliding (a
chosen number for a rope on a wooden post). Capstan (Euler-Eytelwein): the
rope holds while the big tension is at most e^(mu theta) times the small
one, T_big <= e^(mu theta) T_small. The post's radius does not enter the
factor, so the post is drawn larger than scale. Until the release a latch
under the big weight carries it; then the latch slides away.

    holds:  M g <= e^(mu theta) m g            nothing moves;
    slips:  both weights move with the rope, T_big = e^(mu theta) T_small,
            m (g + a) = T_small,  M g - T_big = M a,
            a = g (M - m e^(mu theta)) / (M + m e^(mu theta)),

the big weight falling and the small one rising at the same speed while
the rope slides round the post. The fall of L = 1 m is integrated by RK4
at steps_per_second and checked against the closed forms sqrt(2 L / a) and
a t, and against a half-step rerun; the run ends at the landing (what the
small weight does after that is not modelled). The run repeats every
cycle_s seconds of video with a crossfade back to the latched setup; the
cycle divides the scene length, so the scene is exactly periodic and the
last frame equals the first. Shown at 1/slow speed. Deterministic, no seed.

Measured and printed: the capstan factors for one, two and three turns,
the capacity of the 2 kg side with each, whether the 20 kg holds, the
spare, the turns needed for exactly 20 kg, the sliding acceleration and
the tensions, the 1 m fall by RK4 against the closed forms and the
half-step rerun, load scans for one and two turns, the factors with other
grips, the hand variant for the description, the schedule in video time,
the on-screen text widths and the layout clearances.

usage: capstan.py [--measure-only] [--frames t1,t2,...]
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
POST = (126, 92, 60)
POST_EDGE = (82, 58, 36)
POST_LIGHT = (164, 126, 86)
ROPE = (214, 178, 124)
ROPE_DARK = (108, 80, 46)
BLOCK = (168, 176, 188)
BLOCK_EDGE = (92, 100, 114)
BLOCK_TEXT = (28, 32, 38)
FLOOR = (118, 126, 138)
LATCH = (156, 164, 176)
WALL = (72, 78, 90)
INK = (150, 158, 170)

# Layout: overlay at y 96..130 (captions.py), two title rows at y 190/252 for
# the first seconds, then the legend at y 236 and the shared clock at y 290;
# two panels stacked, one turn in the band y 330..880 and two turns in y
# 880..1430, each drawn at 2x in its own geometry layer; in each band the
# label row 40 px under the band top holds the panel label (left), the gold
# event text (centred) and the live state (right), the second row at 84 and
# the third at 120 hold the capacity and the factor (left) and the speed and
# the fall (right); the post is centred under them (its axis horizontal,
# centre 110 px under the band top, drawn radius 40 px), the rope hangs from
# its bottom edge at x 480 (20 kg) and 600 (2 kg), the floor is 524 px under
# the band top; captions at caption_y 0.75 (y 1440..1530); the six-line
# card from y 1572 at a 48 px pitch.
LEGEND_Y, CLOCK_Y = 236, 290
SS = 2
PAYOFF_Y, PAYOFF_PITCH = 1572.0, 48
PANELS = ("one", "two")
BAND_Y = {"one": 330, "two": 880}
BAND_H = 550
LABEL_DY, SUB_DY, FIX_DY = 40, 84, 120
ROW_X0, ROW_X1 = 40, 1040
COLOUR = {"one": CORAL, "two": TEAL}
HELD, FALL, DOWN, HOLD = "held", "falling", "down", "holding"
CX = 540.0                       # the post's centre x
POST_CY, POST_HALF_LEN = 110.0, 110.0
STRAND_DX = 60.0                 # the strands hang at CX - 60 (20 kg) and CX + 60 (2 kg)
ROPE_W = 8.0
STRAND_A0 = 22.0                 # rope from the post's bottom edge to the 20 kg block's top at the start
BIG_W, BIG_H = 96.0, 72.0
SMALL_W, SMALL_H = 58.0, 46.0
FLOOR_Y = 524.0
FLOOR_X0, FLOOR_X1 = CX - 150.0, CX + 170.0
DIM_X = CX + 150.0               # the 1 m dimension line
TICK_SPACING, TICK_PHASE = 28.0, 14.0
WALL_X = 300.0
LATCH_TH = 10.0
LATCH_IN, LATCH_OUT = 40.0, -64.0   # the latch tip relative to the 20 kg strand, in and retracted


def blend(col, a: float, base=BG) -> tuple:
    a = max(0.0, min(1.0, a))
    return tuple(int(round(c * a + b * (1 - a))) for c, b in zip(col, base))


def smoother(u: float) -> float:
    u = max(0.0, min(1.0, u))
    return u * u * u * (u * (6.0 * u - 15.0) + 10.0)


# --- measurement --------------------------------------------------------------
def factor(mu: float, turns: float) -> float:
    return math.exp(mu * 2.0 * math.pi * turns)


def slide_accel(M: float, m: float, K: float, g: float) -> float:
    return g * (M - m * K) / (M + m * K)


def rk4_fall(a: float, L: float, dt: float) -> dict:
    """y'' = a from rest until y reaches L; RK4 on (y, v), the landing located by linear interpolation
    inside the step."""
    y = v = t = 0.0
    n = 0
    while True:
        k1y, k1v = v, a
        k2y, k2v = v + 0.5 * dt * k1v, a
        k3y, k3v = v + 0.5 * dt * k2v, a
        k4y, k4v = v + dt * k3v, a
        y_new = y + dt / 6.0 * (k1y + 2.0 * k2y + 2.0 * k3y + k4y)
        v_new = v + dt / 6.0 * (k1v + 2.0 * k2v + 2.0 * k3v + k4v)
        n += 1
        if y_new >= L:
            h = (L - y) / (y_new - y) * dt
            return {"t": t + h, "v": v + (v_new - v) * h / dt, "steps": n}
        y, v, t = y_new, v_new, t + dt


def capacity(man: dict, turns: float) -> dict:
    g, M, m, mu = man["g"], man["big_kg"], man["small_kg"], man["mu"]
    K = factor(mu, turns)
    T_max = K * m * g
    holds = M * g <= T_max
    out = {"K": K, "T_max": T_max, "M_max": K * m, "holds": holds, "spare_N": T_max - M * g, "ratio": M * g / T_max}
    if not holds:
        out["a"] = slide_accel(M, m, K, g)
    return out


def measure(man: dict) -> dict:
    g, M, m, mu, L = man["g"], man["big_kg"], man["small_kg"], man["mu"], man["fall_m"]
    S, P, D, fps, F, pa = man["slow"], man["cycle_s"], man["scene_duration"], man["fps"], man["reset_fade"], man["release_at"]
    dt = 1.0 / man["steps_per_second"]
    turns = dict(zip(PANELS, man["turns_per_panel"]))
    cycles = D / P
    assert abs(cycles - round(cycles)) < 1e-9, "the cycle must divide the scene length"
    for key in ("cycle_s", "release_at", "first_cycle_at", "reset_fade", "latch_slide_s", "hold_event_after_s"):
        assert abs(man[key] * fps - round(man[key] * fps)) < 1e-9, f"{key} must be a whole number of frames"
    ppm = man["px_per_m"]
    R_px = man["post_draw_radius_px"]
    print(f"setup: a massless, unstretchable rope round a fixed horizontal round post of radius {man['post_radius_m'] * 100:g} "
          f"cm (drawn at {R_px:g} px = {R_px / ppm * 100:.1f} cm, larger than scale: the radius does not enter the capstan "
          f"factor e^(mu theta), the same factors hold with any radius), {turns['one']:g} full turn in the top panel "
          f"(theta = {turns['one'] * 2:g} pi) and {turns['two']:g} full turns in the bottom panel (theta = {turns['two'] * 2:g} "
          f"pi); friction coefficient mu = {mu:g} between rope and post, the same at rest and sliding (a chosen number for a "
          f"rope on a wooden post); on the left hangs M = {M:g} kg ({M * g:.2f} N), on the right m = {m:g} kg ({m * g:.3f} N), "
          f"g = {g:g} m/s^2; the rope holds while T_big <= e^(mu theta) T_small; the floor is {L:g} m under the big weight; "
          f"a latch carries the big weight until the release, then slides away; the fall integrated by RK4 at "
          f"{man['steps_per_second']} steps per second (dt = {dt:.0e} s) and checked against the closed forms and a "
          f"half-step rerun; shown at 1/{S:g} speed on a {P:g} s cycle ({P * fps:.0f} frames) with the release {pa:g} s "
          f"into the cycle, {cycles:.0f} cycles in {D:g} s; drawn at {ppm:g} px per metre; deterministic, no seed")
    caps = {p: capacity(man, turns[p]) for p in PANELS}
    ev: dict = {"caps": caps, "turns": turns}
    c1, c2 = caps["one"], caps["two"]
    print(f"one turn: e^({mu:g} x {turns['one'] * 2:g} pi) = {c1['K']:.4f}, so the {m:g} kg side ({m * g:.3f} N) holds at most "
          f"{c1['T_max']:.2f} N = {c1['M_max']:.3f} kg; the {M:g} kg ({M * g:.2f} N) is {c1['ratio']:.3f} times that "
          f"({-c1['spare_N']:.2f} N short): the rope slips")
    print(f"two turns: e^({mu:g} x {turns['two'] * 2:g} pi) = {c2['K']:.4f}, so the {m:g} kg side holds at most "
          f"{c2['T_max']:.2f} N = {c2['M_max']:.3f} kg; the {M:g} kg is {c2['ratio']:.4f} of that ({1 / c2['ratio']:.3f} "
          f"times to spare, {c2['spare_N']:.2f} N spare): the rope holds, nothing moves; the other way round the "
          f"{m:g} kg side would need {m * g:.3f} N > {c2['K']:.4f} x {M * g:.2f} N to pull the {M:g} kg up, so it holds that "
          f"way as well")
    assert (not c1["holds"]) and c2["holds"], "the brief's outcome does not hold"
    # The slide with one turn.
    a = c1["a"]
    T_small = m * (g + a)
    T_big = c1["K"] * T_small
    rk = rk4_fall(a, L, dt)
    half = rk4_fall(a, L, 0.5 * dt)
    t_c, v_c = math.sqrt(2.0 * L / a), a * math.sqrt(2.0 * L / a)
    ev["fall"] = {"a": a, "t": rk["t"], "v": rk["v"], "t_closed": t_c, "v_closed": v_c}
    print(f"one turn, sliding: both weights move with the rope; T_small = m (g + a) = {T_small:.3f} N, T_big = "
          f"{c1['K']:.4f} T_small = {T_big:.2f} N, M g - T_big = {M * g - T_big:.3f} N = M a; a = g (M - m K) / (M + m K) = "
          f"{a:.4f} m/s^2 ({a / g:.4f} g); RK4 at {man['steps_per_second']} steps/s: the {M:g} kg reaches the floor {L:g} m "
          f"down after {rk['t']:.5f} s (closed form sqrt(2 L / a) = {t_c:.5f} s, diff {rk['t'] - t_c:+.1e} s) at "
          f"{rk['v']:.4f} m/s (closed form a t = {v_c:.4f} m/s, diff {rk['v'] - v_c:+.1e} m/s), {rk['steps']} steps; "
          f"half-step rerun (dt = {0.5 * dt:.0e} s): {half['t']:.7f} s ({half['t'] - rk['t']:+.1e} s), {half['v']:.7f} "
          f"m/s ({half['v'] - rk['v']:+.1e} m/s); the rope slides round the post at the same speed and the {m:g} kg "
          f"rises {L:g} m in the same {rk['t']:.3f} s; the run ends at the landing")
    assert abs(rk["t"] - t_c) < 1e-6 and abs(half["t"] - rk["t"]) < 1e-6, "RK4 disagrees with the closed form"
    n_star = math.log(M / m) / (2.0 * math.pi * mu)
    c3 = capacity(man, 3.0)
    ev["n_star"], ev["c3"] = n_star, c3
    print(f"the limit: exactly {M:g} kg needs ln(M / m) / (2 pi mu) = {n_star:.4f} turns ({n_star * 360:.1f} degrees); each "
          f"full turn multiplies the holding power by e^(2 pi mu) = {c1['K']:.4f}; three turns: factor {c3['K']:.2f}, holds up "
          f"to {c3['T_max']:.1f} N = {c3['M_max']:.1f} kg")
    scans = []
    for p in PANELS:
        parts = []
        for load in man["scan_loads_kg"][p]:
            K = caps[p]["K"]
            if load * g <= K * m * g:
                parts.append(f"{load:g} kg holds")
            else:
                parts.append(f"{load:g} kg slips (a = {slide_accel(load, m, K, g):.4f} m/s^2)")
        scans.append(f"{label_text(p)}: " + ", ".join(parts) + f" (limit {caps[p]['M_max']:.2f} kg)")
    print("load scan with the 2 kg side: " + "; ".join(scans))
    ev["scan"] = scans
    grips = []
    for mu2 in man["description_mus"]:
        grips.append(f"grip {mu2:g}: " + ", ".join(
            f"{factor(mu2, turns[p]):.3f} with {label_text(p)}" for p in PANELS))
    ev["grips"] = {mu2: {p: factor(mu2, turns[p]) for p in PANELS} for mu2 in man["description_mus"]}
    hand = man["hand_N"]
    a_hand = (M * g - c1["K"] * hand) / M
    t_hand = math.sqrt(2.0 * L / a_hand)
    ev["hand"] = {"a": a_hand, "t": t_hand}
    print("for the description: the factor depends on the grip: " + "; ".join(grips)
          + f"; a hand holding a steady {hand:g} N instead of the {m:g} kg weight: one turn holds up to "
          f"{c1['K'] * hand:.1f} N = {c1['K'] * hand / g:.2f} kg, the {M:g} kg falls at (M g - K x {hand:g} N) / M = "
          f"{a_hand:.4f} m/s^2, {L:g} m in {t_hand:.4f} s")
    # Schedule in video time.
    t0 = man["first_cycle_at"]
    k0 = math.ceil((0.0 - t0) / P - 1e-9) - 1
    k1 = math.floor((D - t0) / P - 1e-9)
    starts = [t0 + k * P for k in range(k0, k1 + 1)]
    ev["cycles"] = int(round(cycles))
    vt = lambda real: pa + real * S   # noqa: E731  video time after the cycle start

    def lst(off_: float) -> str:
        return ", ".join(f"{st + off_:.2f}" for st in starts if 0.0 <= st + off_ < D)

    t_land = vt(rk["t"])
    assert t_land < P - F - 0.5, "the landing runs into the reset fade"
    tau0 = (0.0 - t0) % P
    r0 = (tau0 - pa) / S
    st0 = {p: state_at(ev, man, p, r0) for p in PANELS}
    print(f"schedule (video time, 1/{S:g} speed): cycles of {P:g} s start at " + ", ".join(f"{st:.2f}" for st in starts)
          + f" s; the release {pa:g} s into each cycle at {lst(pa)} s (the latch slides away over the next "
          f"{man['latch_slide_s']:g} s); with one turn the {M:g} kg reaches the floor {rk['t'] * S:.2f} s of video after "
          f"the release at {lst(t_land)} s and the top event text lights there; with two turns nothing moves and the "
          f"bottom event text lights {man['hold_event_after_s']:g} s of video ({man['hold_event_after_s'] / S:.2f} s real) "
          f"after the release at {lst(pa + man['hold_event_after_s'])} s; each cycle crossfades to the latched setup over "
          f"its last {F:g} s (from {lst(P - F)} s); on the first frame the cycle is {tau0:.2f} s in ({r0:.3f} s real "
          f"after the release): the top {M:g} kg is {st0['one']['phase']} at {st0['one']['d'] * 100:.1f} cm down, the "
          f"bottom {M:g} kg is {st0['two']['phase']}; title until {man['title_until']:g} s; payoff card from "
          f"{man['payoff_t']:g} s; the title fades back in over the last {man['loop_fade']:g} s and the last frame repeats "
          f"the first (the scene is periodic: {D:g} s holds exactly {cycles:.0f} cycles)")
    # Text widths.
    font = os.environ["SEED_ZERO_FONT"]
    f20, f24, f28, f34, f40, f56 = (ImageFont.truetype(font, n) for n in (20, 24, 28, 34, 40, 56))
    widths = {"overlay@34": (f34, man["overlay"])}
    for j, line in enumerate(man["title"].split("|")):
        widths[f"title line {j + 1}@56"] = (f56, line)
    widths["legend@40"] = (f40, legend_text(man))
    widths["clock@28"] = (f28, clock_text(0.9954))
    widths["clock held@28"] = (f28, clock_text(-1.0))
    for p in PANELS:
        widths[f"label {p}@40"] = (f40, label_text(p))
        widths[f"capacity {p}@28"] = (f28, cap_text(ev, p))
        widths[f"factor {p}@28"] = (f28, times_text(man, ev, p))
        for ph in (HELD, FALL, DOWN, HOLD):
            widths[f"state {ph}@40"] = (f40, state_text(ph))
        widths[f"event {p}@40"] = (f40, event_text(ev, p, DOWN if p == "one" else HOLD, True))
    widths["speed@28"] = (f28, speed_text(rk["v"]))
    widths["fallen@28"] = (f28, fallen_text(L))
    widths["holding for@28"] = (f28, holding_text(rk["t"]))
    widths["big label@24"] = (f24, block_text(M))
    widths["small label@20"] = (f20, block_text(m))
    widths["dimension@24"] = (f24, dim_text(L))
    for j, line in enumerate(payoff_lines(man, ev)):
        widths[f"payoff line {j + 1}@40"] = (f40, line)
    print("text widths: " + ", ".join(f"{k} {f.getlength(s):.0f} px" for k, (f, s) in widths.items()))
    assert all(f.getlength(s) < 950 for f, s in widths.values()), "a text line is wider than 950 px"
    assert len(payoff_lines(man, ev)) <= 6, "more than six card lines"
    # Layout checks (band-local px).
    left = ROW_X0 + max(max(f40.getlength(label_text(p)), f28.getlength(cap_text(ev, p)), f28.getlength(times_text(man, ev, p)))
                        for p in PANELS)
    right = ROW_X1 - max(max(f40.getlength(state_text(ph)) for ph in (HELD, FALL, DOWN, HOLD)),
                         f28.getlength(speed_text(rk["v"])), f28.getlength(fallen_text(L)), f28.getlength(holding_text(rk["t"])))
    ev_w = max(f40.getlength(event_text(ev, p, DOWN if p == "one" else HOLD, True)) for p in PANELS)
    label_end = ROW_X0 + max(f40.getlength(label_text(p)) for p in PANELS)
    state_start = ROW_X1 - max(f40.getlength(state_text(ph)) for ph in (HELD, FALL, DOWN, HOLD))
    post_x0, post_x1 = CX - POST_HALF_LEN, CX + POST_HALF_LEN
    post_top, post_bottom = POST_CY - R_px, POST_CY + R_px
    xa, xb = CX - STRAND_DX, CX + STRAND_DX
    big_top0 = post_bottom + STRAND_A0
    big_bottom0 = big_top0 + BIG_H
    strand_b0 = STRAND_A0 + L * ppm
    small_top0 = post_bottom + strand_b0
    small_bottom0 = small_top0 + SMALL_H
    small_top_end = small_top0 - L * ppm
    floor_bottom = FLOOR_Y + 3 + 14
    print(f"row check: the left column ends at x {left:.0f} px and the right column starts at x {right:.0f} px, the post "
          f"spans x {post_x0:.0f} to {post_x1:.0f} px and y {post_top:.0f} to {post_bottom:.0f} px under the band top; the "
          f"event text (widest {ev_w:.0f} px, centred) spans x {W / 2 - ev_w / 2:.0f} to {W / 2 + ev_w / 2:.0f} px between "
          f"the label (ends at {label_end:.0f}) and the state (starts at {state_start:.0f}); the rows end {FIX_DY + 16} px "
          f"under the band top; the {M:g} kg block hangs at x {xa - BIG_W / 2:.0f} to {xa + BIG_W / 2:.0f} from y "
          f"{big_top0:.0f} to {big_bottom0:.0f} and lands with its bottom on the floor at {FLOOR_Y:.0f} ({L:g} m = "
          f"{L * ppm:.0f} px); the {m:g} kg block hangs at x {xb - SMALL_W / 2:.0f} to {xb + SMALL_W / 2:.0f} from y "
          f"{small_top0:.0f} to {small_bottom0:.0f} ({FLOOR_Y - small_bottom0:.0f} px above the floor) and rises to "
          f"{small_top_end:.0f}, {small_top_end - post_bottom:.0f} px under the post; the latch tip retracts from x "
          f"{xa + LATCH_IN:.0f} to {xa + LATCH_OUT:.0f} ({xa - BIG_W / 2 - (xa + LATCH_OUT):.0f} px clear of the block); "
          f"the floor hatch ends {floor_bottom:.0f} px under the band top; each band is {BAND_H} px tall (y "
          f"{BAND_Y['one']} to {BAND_Y['one'] + BAND_H} and {BAND_Y['two']} to {BAND_Y['two'] + BAND_H}); the caption band "
          f"starts at y {int(man['caption_y'] * H)}; the title rows end at y {252 + 28} and the overlay band ends at y 130")
    assert left < post_x0 - 20 and right > post_x1 + 20, "a column meets the post"
    assert W / 2 - ev_w / 2 > label_end + 30 and W / 2 + ev_w / 2 < state_start - 30, "the event text meets a side text"
    assert post_top >= LABEL_DY + 24, "the post meets the label row"
    assert abs(big_bottom0 + L * ppm - FLOOR_Y) < 1e-9, "the fall does not end on the floor"
    assert small_bottom0 < FLOOR_Y - 8, "the small block starts on the floor"
    assert small_top_end >= post_bottom + 4, "the small block rises into the post"
    assert xa + BIG_W / 2 < xb - SMALL_W / 2 - 8, "the blocks overlap"
    assert xa + LATCH_OUT < xa - BIG_W / 2 - 8, "the latch stays under the block"
    assert WALL_X + 8 < xa + LATCH_OUT, "the latch retracts into the wall"
    assert floor_bottom < BAND_H - 8, "the floor leaves the band"
    assert f24.getlength(block_text(M)) < BIG_W - 10 and f20.getlength(block_text(m)) < SMALL_W - 8, "a block label overflows"
    assert xb + SMALL_W / 2 + 20 < DIM_X < FLOOR_X1 and DIM_X + 8 + f24.getlength(dim_text(L)) < W - 20, "the dimension line"
    assert BAND_Y["two"] + BAND_H <= int(man["caption_y"] * H), "the lower band reaches the caption band"
    return ev


def state_at(ev: dict, man: dict, panel: str, r: float) -> dict:
    """The panel's state r real seconds after the release: phase, fall d (m), speed v (m/s), lit."""
    if r < 0.0:
        return {"phase": HELD, "d": 0.0, "v": 0.0, "lit": False}
    if panel == "one":
        fl = ev["fall"]
        if r < fl["t_closed"]:
            return {"phase": FALL, "d": 0.5 * fl["a"] * r * r, "v": fl["a"] * r, "lit": False}
        return {"phase": DOWN, "d": man["fall_m"], "v": 0.0, "lit": True}
    return {"phase": HOLD, "d": 0.0, "v": 0.0, "lit": r >= man["hold_event_after_s"] / man["slow"]}


def legend_text(man: dict) -> str:
    return f"same rope, same post, 1/{man['slow']:g} speed"


def clock_text(r: float) -> str:
    return "held on the latch" if r < 0.0 else f"{r:.2f} s after the release"


def label_text(p: str) -> str:
    return "one turn" if p == "one" else "two turns"


def cap_text(ev: dict, p: str) -> str:
    return f"holds up to {ev['caps'][p]['M_max']:.1f} kg"


def times_text(man: dict, ev: dict, p: str) -> str:
    return f"{man['small_kg']:g} kg times {ev['caps'][p]['K']:.1f}"


def state_text(ph: str) -> str:
    return ph


def speed_text(v: float) -> str:
    return f"speed {v:.2f} m/s"


def fallen_text(d: float) -> str:
    return f"fallen {d:.2f} m"


def holding_text(r: float) -> str:
    return f"holding for {r:.2f} s"


def block_text(kg: float) -> str:
    return f"{kg:g} kg"


def dim_text(L: float) -> str:
    return f"{L:g} m"


def event_text(ev: dict, p: str, ph: str, lit: bool) -> str:
    if not lit:
        return ""
    if p == "one" and ph == DOWN:
        return f"on the floor at {ev['fall']['t']:.2f} s"
    if p == "two" and ph == HOLD:
        return "holds, nothing moves"
    return ""


def payoff_lines(man: dict, ev: dict) -> list[str]:
    c1, c2, c3 = ev["caps"]["one"], ev["caps"]["two"], ev["c3"]
    mus = man["description_mus"]
    text = man["payoff_text"].format(
        M_one=c1["M_max"], M_two=c2["M_max"], K1=c1["K"], K2=c2["K"], n_star=ev["n_star"], M_three=c3["M_max"],
        K2_lo=ev["grips"][mus[0]]["two"], K2_hi=ev["grips"][mus[1]]["two"], mu_lo=mus[0], mu_hi=mus[1])
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
        self.font_big2x = ImageFont.truetype(font, 24 * SS)
        self.font_small2x = ImageFont.truetype(font, 20 * SS)
        self.ppm = float(man["px_per_m"])
        self.R = float(man["post_draw_radius_px"])
        self.S = man["slow"]
        self.P = man["cycle_s"]
        self.P_f = int(round(man["cycle_s"] * self.fps))
        self.c0_f = int(round(man["first_cycle_at"] * self.fps))
        self.pa, self.F = man["release_at"], man["reset_fade"]
        self.turns = ev["turns"]
        self.L = man["fall_m"]
        self.xa, self.xb = CX - STRAND_DX, CX + STRAND_DX
        self.post_bottom = POST_CY + self.R
        self.strand_b0 = STRAND_A0 + self.L * self.ppm
        # The front half of a turn (phi 0..pi from the bottom edge over the front to the top edge),
        # as offsets from the turn's start x, with its cumulative arc length, per panel.
        self.front = {}
        for p in PANELS:
            n = self.turns[p]
            pitch = 2.0 * STRAND_DX / n
            phi = np.linspace(0.0, math.pi, 49)
            xs = 0.5 * pitch * phi / math.pi
            ys = POST_CY + self.R * np.cos(phi)
            seg = np.hypot(np.diff(xs), np.diff(ys))
            cum = np.concatenate([[0.0], np.cumsum(seg)])
            self.front[p] = {"n": n, "pitch": pitch, "xs": xs, "ys": ys, "cum": cum, "len": float(cum[-1])}
        self.static = self.draw_static()

    def phase(self, f: int) -> tuple[int, float]:
        k, tau_f = divmod(f - self.c0_f, self.P_f)
        return k, tau_f / self.fps

    @staticmethod
    def L_(x: float, y: float) -> tuple[float, float]:
        """Layer (2x) pixel of a band-local point, rounded to 1e-4 px so equal states draw equal pixels."""
        return round(x * SS, 4), round(y * SS, 4)

    def draw_static(self) -> Image.Image:
        """The post, the floor, the wall and the 1 m dimension line: the same in every frame."""
        layer = Image.new("RGB", (W * SS, BAND_H * SS), BG)
        d = ImageDraw.Draw(layer)
        R = self.R
        # The floor with a hatch under it.
        f0, f1 = self.L_(FLOOR_X0, FLOOR_Y), self.L_(FLOOR_X1, FLOOR_Y + 3)
        d.rectangle((f0[0], f0[1], f1[0], f1[1]), fill=FLOOR)
        x = FLOOR_X0 + 6.0
        while x + 12.0 <= FLOOR_X1:
            h0, h1 = self.L_(x + 12.0, FLOOR_Y + 4), self.L_(x, FLOOR_Y + 16)
            d.line((*h0, *h1), fill=blend(FLOOR, 0.6), width=2 * SS)
            x += 16.0
        # The 1 m dimension line to the right of the small weight.
        y0, y1 = self.post_bottom + STRAND_A0 + BIG_H, FLOOR_Y
        p0, p1 = self.L_(DIM_X, y0), self.L_(DIM_X, y1)
        d.line((*p0, *p1), fill=INK, width=2 * SS)
        for yy in (y0, y1):
            q0, q1 = self.L_(DIM_X - 8, yy), self.L_(DIM_X + 8, yy)
            d.line((*q0, *q1), fill=INK, width=2 * SS)
        d.text(self.L_(DIM_X + 10, 0.5 * (y0 + y1)), dim_text(self.L), font=self.font_big2x, fill=INK, anchor="lm")
        # The wall the latch retracts into.
        w0, w1 = self.L_(WALL_X, self.post_bottom + STRAND_A0 + BIG_H - 30), self.L_(WALL_X + 8, self.post_bottom + STRAND_A0 + BIG_H + 40)
        d.rectangle((w0[0], w0[1], w1[0], w1[1]), fill=WALL)
        # The post: a horizontal rounded bar with a light stripe along its upper part.
        p0, p1 = self.L_(CX - POST_HALF_LEN, POST_CY - R), self.L_(CX + POST_HALF_LEN, POST_CY + R)
        d.rounded_rectangle((p0[0], p0[1], p1[0], p1[1]), radius=R * SS, fill=POST, outline=POST_EDGE, width=2 * SS)
        s0, s1 = self.L_(CX - POST_HALF_LEN + R * 0.4, POST_CY - R * 0.72), self.L_(CX + POST_HALF_LEN - R * 0.4, POST_CY - R * 0.42)
        d.rounded_rectangle((s0[0], s0[1], s1[0], s1[1]), radius=R * 0.15 * SS, fill=POST_LIGHT)
        return layer

    def rope_point(self, p: str, s: float, LA: float, LB: float):
        """(x, y, kind) of the rope point s px along the rope from the big block's top, or None past the
        small block; kind 'strand', 'front' or 'hidden'."""
        fr = self.front[p]
        if s < LA:
            return self.xa, self.post_bottom + LA - s, "strand"
        s -= LA
        for i in range(fr["n"]):
            if s < fr["len"]:
                x = self.xa + i * fr["pitch"] + float(np.interp(s, fr["cum"], fr["xs"]))
                y = float(np.interp(s, fr["cum"], fr["ys"]))
                return x, y, "front"
            s -= fr["len"]
            if s < fr["len"]:
                return None, None, "hidden"
            s -= fr["len"]
        if s < LB:
            return self.xb, self.post_bottom + s, "strand"
        return None

    def draw_dynamic(self, layer: Image.Image, p: str, tau: float) -> dict:
        """The rope, the weights and the latch tau seconds into a cycle, drawn over the static layer."""
        man = self.man
        d = ImageDraw.Draw(layer)
        r = (tau - self.pa) / self.S
        st = state_at(self.ev, man, p, r)
        d_px = st["d"] * self.ppm
        LA = STRAND_A0 + d_px
        LB = self.strand_b0 - d_px
        big_top = self.post_bottom + LA
        small_top = self.post_bottom + LB
        fr = self.front[p]
        # The latch: in under the big weight until the release, then retracting into the wall.
        u = smoother((tau - self.pa) / man["latch_slide_s"]) if tau >= self.pa else 0.0
        tip = self.xa + LATCH_IN + (LATCH_OUT - LATCH_IN) * u
        ly = self.post_bottom + STRAND_A0 + BIG_H
        l0, l1 = self.L_(WALL_X + 8, ly), self.L_(tip, ly + LATCH_TH)
        d.rectangle((l0[0], l0[1], l1[0], l1[1]), fill=LATCH)
        # The strands from the post's bottom edge down to the weights.
        wd = int(round(ROPE_W * SS))
        a0, a1 = self.L_(self.xa, self.post_bottom), self.L_(self.xa, big_top)
        d.line((*a0, *a1), fill=ROPE, width=wd)
        b0, b1 = self.L_(self.xb, self.post_bottom), self.L_(self.xb, small_top)
        d.line((*b0, *b1), fill=ROPE, width=wd)
        # The front half of each turn over the post (the back half is hidden behind it).
        for i in range(fr["n"]):
            x0 = self.xa + i * fr["pitch"]
            pts = [self.L_(x0 + float(dx), float(y)) for dx, y in zip(fr["xs"], fr["ys"])]
            d.line(pts, fill=ROPE, width=wd, joint="curve")
        # Dash marks every TICK_SPACING px of rope, moving with the rope.
        k = 0
        while True:
            pt = self.rope_point(p, TICK_PHASE + k * TICK_SPACING, LA, LB)
            if pt is None:
                break
            x, y, kind = pt
            if kind == "strand":
                t0, t1 = self.L_(x - ROPE_W / 2, y - 2), self.L_(x + ROPE_W / 2, y + 2)
                d.rectangle((t0[0], t0[1], t1[0], t1[1]), fill=ROPE_DARK)
            elif kind == "front":
                X, Y = self.L_(x, y)
                rr = (ROPE_W / 2 - 1) * SS
                d.ellipse((X - rr, Y - rr, X + rr, Y + rr), fill=ROPE_DARK)
            k += 1
        # The weights.
        for cx, top, w, h, kg, fnt in ((self.xa, big_top, BIG_W, BIG_H, man["big_kg"], self.font_big2x),
                                       (self.xb, small_top, SMALL_W, SMALL_H, man["small_kg"], self.font_small2x)):
            q0, q1 = self.L_(cx - w / 2, top), self.L_(cx + w / 2, top + h)
            d.rectangle((q0[0], q0[1], q1[0], q1[1]), fill=BLOCK, outline=BLOCK_EDGE, width=2 * SS)
            d.text(self.L_(cx, top + h / 2), block_text(kg), font=fnt, fill=BLOCK_TEXT, anchor="mm")
        st["r"] = r
        return st

    def draw_panel(self, p: str, f: int) -> tuple[Image.Image, dict]:
        k, tau = self.phase(f)
        F, P = self.F, self.P
        old = self.static.copy()
        st = self.draw_dynamic(old, p, tau)
        st["alpha"], st["k"] = 1.0, k
        if tau <= P - F:
            return old, st
        a = (tau - (P - F)) / F
        new = self.static.copy()
        st_new = self.draw_dynamic(new, p, tau - P)
        st_new["k"] = k + 1
        layer = Image.blend(old, new, a)
        if a < 0.5:
            st["alpha"] = 1.0 - 2.0 * a
            return layer, st
        st_new["alpha"] = 2.0 * a - 1.0
        return layer, st_new

    def draw_text(self, d: ImageDraw.ImageDraw, states: dict, hud_alpha: float) -> None:
        man, ev = self.man, self.ev
        for p, st in states.items():
            y0 = BAND_Y[p]
            a, ph = st["alpha"], st["phase"]
            d.text((ROW_X0, y0 + LABEL_DY), label_text(p), font=self.font, fill=COLOUR[p], anchor="lm")
            if hud_alpha > 0.02:
                d.text((ROW_X0, y0 + SUB_DY), cap_text(ev, p), font=self.font_small, fill=blend(GOLD, 0.9 * hud_alpha), anchor="lm")
                d.text((ROW_X0, y0 + FIX_DY), times_text(man, ev, p), font=self.font_small, fill=blend(MUTED, hud_alpha), anchor="lm")
            settled = (p == "one" and ph == DOWN) or (p == "two" and st["lit"])
            col = MUTED if ph in (HELD, DOWN) else (GOLD if settled else TEXT)
            d.text((ROW_X1, y0 + LABEL_DY), state_text(ph), font=self.font, fill=blend(col, a), anchor="rm")
            d.text((ROW_X1, y0 + SUB_DY), speed_text(st["v"]), font=self.font_small, fill=blend(TEXT if ph == FALL else MUTED, a),
                   anchor="rm")
            third = fallen_text(st["d"]) if p == "one" else holding_text(max(0.0, st["r"]))
            d.text((ROW_X1, y0 + FIX_DY), third, font=self.font_small, fill=blend(MUTED, a), anchor="rm")
            txt = event_text(ev, p, ph, st["lit"])
            if txt:
                d.text((W / 2, y0 + LABEL_DY), txt, font=self.font, fill=blend(GOLD, a), anchor="mm")
        if hud_alpha > 0.02:
            d.text((W / 2, LEGEND_Y), legend_text(man), font=self.font, fill=blend(TEXT, hud_alpha), anchor="mm")
            d.text((W / 2, CLOCK_Y), clock_text(states["one"]["r"]), font=self.font_small, fill=blend(MUTED, hud_alpha), anchor="mm")

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
        for p in PANELS:
            layer, states[p] = self.draw_panel(p, f)
            img.paste(layer.reduce(SS), (0, BAND_Y[p]))
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
    man = json.loads((ROOT / "projects/capstan/manifest.json").read_text())
    ev = measure(man)
    if "--measure-only" in sys.argv:
        return
    if "--frames" in sys.argv:
        times = [float(v) for v in sys.argv[sys.argv.index("--frames") + 1].split(",")]
        r = Renderer(man, ev)
        (ROOT / "media/capstan").mkdir(parents=True, exist_ok=True)
        for tv in times:
            Image.fromarray(r.frame_at(int(round(tv * man["fps"])))).save(ROOT / f"media/capstan/smoke-{tv}.png")
        print("smoke frames: " + ", ".join(f"{tv}" for tv in times))
        return
    Renderer(man, ev).render(ROOT / "media/capstan/footage.mp4")


if __name__ == "__main__":
    main()
