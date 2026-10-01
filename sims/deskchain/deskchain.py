#!/usr/bin/env python3
"""Chain over the desk edge: will the chain slide off the desk?

Two panels on the same clock, the same desk drawn the same way at the same
scale: a uniform chain of length L (mass per length lambda, it cancels)
lies straight on a level desk and hangs straight down over a smooth
rounded edge (no friction and no momentum loss at the corner); x is the
hanging length; friction on the desk part mu, the same at rest and
sliding. A clamp holds each chain until the release. At rest the chain
holds while the hanging weight lambda g x is at most the grip mu lambda g
(L - x), so the threshold is x* = mu L / (1 + mu): one fifth of the chain
at mu = 0.25, whatever L or the chain's weight. Top panel, x0 below x*:
the net force is negative, the chain never moves. Bottom panel, x0 above
x*: lambda L x'' = lambda g x - mu lambda g (L - x), so

    x'' = k^2 (x - x*),  k = sqrt((1 + mu) g / L),  x = x* + (x0 - x*) cosh(k t)

from rest; the chain is all off the desk when x = L, at t = acosh((L -
x*) / (x0 - x*)) / k with the last link moving at k (x0 - x*) sinh(k t);
after that the whole chain falls freely (x'' = g, the same acceleration
as the slide at x = L) and drops out of its panel. The slide is
integrated by RK4 at steps_per_second from rest at x0, the edge crossing
located by bisection inside the step, and checked against the cosh form
and a half-step rerun; the drawing follows the RK4 table. The run
repeats every cycle_s seconds of video with a crossfade back to the
clamped setup; the cycle divides the scene length, so the scene is
exactly periodic and the last frame equals the first. Shown at 1/slow
speed. Deterministic, no seed.

Measured and printed: the threshold and the grip needed in each panel,
the static check for the holding chain, the RK4 slide of the other (the
time off the desk, the last link's speed, the crossing times of the
excess and of the hanging length) against the closed forms and a
half-step rerun, the other hanging lengths, the frictionless case and
the other grips for the description, the schedule in video time, the
on-screen text widths and the layout clearances.

usage: deskchain.py [--measure-only] [--frames t1,t2,...]
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
STEEL = (150, 160, 176)
CLAMP = (124, 136, 154)
CLAMP_DARK = (62, 70, 84)
INK = (150, 158, 170)

# Layout: overlay at y 96..130 (captions.py), two title rows at y 190/252 for
# the first seconds, then the legend at y 236 and the shared clock at y 290;
# two panels stacked, the 18 cm chain in the band y 330..880 and the 22 cm
# chain in y 880..1430, each drawn at 2x in its own geometry layer (so the
# falling chain is clipped at its band); each band has its label row 40 px
# under the band top, its second row at 84 and its third at 120 (left column
# from x 40, right column to x 1040); the desk slab from desk_top_dy under
# the band top (y 480 and 1030), its edge at edge_x_px, two legs under it;
# the chain hangs down the edge face and falls out of the band bottom; the
# gold event row under the desk between the legs at 330; captions at
# caption_y 0.75 (y 1440..1530); the six-line card from y 1572 at a 48 px
# pitch.
LEGEND_Y, CLOCK_Y = 236, 290
SS = 2
PAYOFF_Y, PAYOFF_PITCH = 1572.0, 48
PANELS = ("hold", "slide")
BAND_Y = {"hold": 330, "slide": 880}
BAND_H = 550
LABEL_DY, SUB_DY, FIX_DY = 40, 84, 120
EVENT_DY, EVENT_X = 330, 340
ROW_X0, ROW_X1 = 40, 1040
SLAB_PX, LEG_W, LEG_GAP = 28, 20, 24
LEG_X = (70, 580)
BEAD_R = 4.2
CLAMP_W, CLAMP_PAD, CLAMP_STEM, CLAMP_LIFT = 44, 16, 30, 50
COLOUR = {"hold": TEAL, "slide": CORAL}
HELD, HOLD, SLIDE, OFF = "held", "hold", "slide", "off"


def blend(col, a: float, base=BG) -> tuple:
    a = max(0.0, min(1.0, a))
    return tuple(int(round(c * a + b * (1 - a))) for c, b in zip(col, base))


# --- measurement --------------------------------------------------------------
def threshold(mu: float, L: float) -> float:
    """Hanging length at which the hanging weight equals the grip: x* = mu L / (1 + mu)."""
    return mu * L / (1.0 + mu)


def rate(mu: float, g: float, L: float) -> float:
    """k = sqrt((1 + mu) g / L): the excess over x* grows as cosh(k t)."""
    return math.sqrt((1.0 + mu) * g / L)


def closed_off(x0: float, mu: float, g: float, L: float) -> tuple[float, float]:
    """(time the chain is all off the desk, speed of the last link then) from rest at x0 > x*."""
    xs, k = threshold(mu, L), rate(mu, g, L)
    t = math.acosh((L - xs) / (x0 - xs)) / k
    return t, k * (x0 - xs) * math.sinh(k * t)


def closed_x(t, x0: float, mu: float, g: float, L: float):
    xs, k = threshold(mu, L), rate(mu, g, L)
    return xs + (x0 - xs) * np.cosh(k * t)


def rk4_slide(x0: float, mu: float, g: float, L: float, dt: float) -> dict:
    """Integrate x'' = (g / L)((1 + mu) x - mu L) from rest at x0 by classical RK4 at dt until the
    hanging length reaches L; the crossing is located by bisection on the last step (the
    acceleration is smooth inside the phase, so the RK4 sub-step is as accurate as a full step).
    Returns the table (t, x, v), the end state and the step count."""
    k2 = (1.0 + mu) * g / L
    xs = threshold(mu, L)

    def acc(x: float) -> float:
        return k2 * (x - xs)

    def step(x: float, v: float, h: float) -> tuple[float, float]:
        k1x, k1v = v, acc(x)
        k2x, k2v = v + 0.5 * h * k1v, acc(x + 0.5 * h * k1x)
        k3x, k3v = v + 0.5 * h * k2v, acc(x + 0.5 * h * k2x)
        k4x, k4v = v + h * k3v, acc(x + h * k3x)
        return x + h * (k1x + 2.0 * k2x + 2.0 * k3x + k4x) / 6.0, v + h * (k1v + 2.0 * k2v + 2.0 * k3v + k4v) / 6.0

    assert x0 > xs, "the chain only slides from above the threshold"
    ts, xt, vt = [0.0], [x0], [0.0]
    x, v, n = x0, 0.0, 0
    while True:
        xn, vn = step(x, v, dt)
        if xn >= L:
            lo, hi = 0.0, dt
            for _ in range(80):
                mid = 0.5 * (lo + hi)
                xm, _ = step(x, v, mid)
                if xm < L:
                    lo = mid
                else:
                    hi = mid
            _, vh = step(x, v, hi)
            t_off = n * dt + hi
            ts.append(t_off)
            xt.append(L)
            vt.append(vh)
            n += 1
            break
        n += 1
        x, v = xn, vn
        ts.append(n * dt)
        xt.append(x)
        vt.append(v)
    return {"t": np.array(ts), "x": np.array(xt), "v": np.array(vt), "t_off": t_off, "v_off": vh, "steps": n,
            "x0": x0, "mu": mu, "g": g, "L": L, "static": False}


def static_run(x0: float, mu: float, g: float, L: float) -> dict:
    return {"x0": x0, "mu": mu, "g": g, "L": L, "static": True, "t_off": math.inf, "v_off": 0.0}


def state_at(run: dict, rt: float) -> dict:
    """(x, v, phase) of the chain rt real seconds after the release (the hanging length and the
    speed along the chain; after the edge the whole chain falls freely)."""
    if rt < 0.0:
        return {"x": run["x0"], "v": 0.0, "phase": HELD}
    if run["static"]:
        return {"x": run["x0"], "v": 0.0, "phase": HOLD}
    if rt < run["t_off"]:
        return {"x": float(np.interp(rt, run["t"], run["x"])), "v": float(np.interp(rt, run["t"], run["v"])),
                "phase": SLIDE}
    d = rt - run["t_off"]
    return {"x": run["L"] + run["v_off"] * d + 0.5 * run["g"] * d * d, "v": run["v_off"] + run["g"] * d, "phase": OFF}


def crossing(run: dict, x: float) -> tuple[float, float]:
    """(t, v) when the hanging length first reaches x, interpolated on the RK4 table."""
    return float(np.interp(x, run["x"], run["t"])), float(np.interp(x, run["x"], run["v"]))


def measure(man: dict) -> dict:
    g, L, mu = man["g"], man["chain_m"], man["mu"]
    x_hold, x_slide = man["hang_m"]["hold"], man["hang_m"]["slide"]
    dt = 1.0 / man["steps_per_second"]
    S, P, D, fps, F, pa = man["slow"], man["cycle_s"], man["scene_duration"], man["fps"], man["reset_fade"], man["release_at"]
    cycles = D / P
    assert abs(cycles - round(cycles)) < 1e-9, "the cycle must divide the scene length"
    for key in ("cycle_s", "release_at", "first_cycle_at", "reset_fade"):
        assert abs(man[key] * fps - round(man[key] * fps)) < 1e-9, f"{key} must be a whole number of frames"
    ppm = man["px_per_m"]
    link = man["link_m"]
    n_links = int(round(L / link))
    assert abs(n_links * link - L) < 1e-9, "the link pitch must divide the chain"
    xs, k = threshold(mu, L), rate(mu, g, L)
    print(f"setup: the same desk in both panels: a uniform chain of {L:g} m ({n_links} links of {link * 100:g} cm; its "
          f"mass per length cancels) lies straight on a level desk and hangs straight down over a smooth rounded edge "
          f"(no friction and no momentum loss at the corner); friction on the desk part mu = {mu:g}, the same at rest "
          f"and sliding (a chosen number for a metal chain on a wooden desk); g = {g:g} m/s^2; a clamp holds each chain "
          f"until the release; top panel {x_hold * 100:g} cm over the edge, bottom panel {x_slide * 100:g} cm; the "
          f"slide integrated by RK4 at {man['steps_per_second']} steps per second (dt = {dt:.0e} s) with the edge "
          f"crossing located by bisection inside the step, checked against the closed form x = x* + (x0 - x*) cosh(k t) "
          f"and a half-step rerun; after the edge the whole chain falls freely; shown at 1/{S:g} speed on a {P:g} s "
          f"cycle ({P * fps:.0f} frames) with the release {pa:g} s into the cycle, {cycles:.0f} cycles in {D:g} s; "
          f"drawn at {ppm:g} px per metre; deterministic, no seed")
    print(f"threshold: at rest the chain holds while the hanging weight lambda g x is at most the grip mu lambda g (L - x), "
          f"so the line is x* = mu L / (1 + mu) = {xs:.4f} m = {xs * 100:.2f} cm = {xs / L * 100:.2f} percent of the "
          f"chain, exactly one fifth at mu = {mu:g} (1/5 = {0.2:.4f}); the fraction does not depend on L or on the "
          f"chain's weight; sliding, x'' = k^2 (x - x*) with k = sqrt((1 + mu) g / L) = {k:.4f} per second, so the "
          f"excess over the line grows as cosh(k t): it e-folds every 1/k = {1.0 / k:.4f} s and doubles at "
          f"acosh(2) / k = {math.acosh(2.0) / k:.4f} s")
    # The holding chain: a static check, no integration needed.
    need_h = x_hold / (L - x_hold)
    net_h = x_hold - mu * (L - x_hold)
    print(f"{x_hold * 100:g} cm over the edge (top panel): the hanging weight is {x_hold:.4f} lambda g, the grip available "
          f"mu (L - x0) = {mu * (L - x_hold):.4f} lambda g, net {net_h:+.4f} lambda g: negative, so the chain never moves "
          f"and RK4 is not needed; the grip needed is x0 / (L - x0) = {need_h:.4f} of the weight on the desk, under "
          f"{mu:g}; {x_hold * 100:g} cm is {(xs - x_hold) * 100:.1f} cm under the line: it holds for ever")
    assert net_h < 0.0 and x_hold < xs
    # The sliding chain by RK4 against the closed form.
    need_s = x_slide / (L - x_slide)
    net_s = x_slide - mu * (L - x_slide)
    run = rk4_slide(x_slide, mu, g, L, dt)
    t_c, v_c = closed_off(x_slide, mu, g, L)
    err_x = float(np.max(np.abs(run["x"] - closed_x(run["t"], x_slide, mu, g, L))))
    half = rk4_slide(x_slide, mu, g, L, 0.5 * dt)
    print(f"{x_slide * 100:g} cm over the edge (bottom panel): the hanging weight is {x_slide:.4f} lambda g against a grip "
          f"of {mu * (L - x_slide):.4f} lambda g, net {net_s:+.4f} lambda g: positive, so it slides; the grip needed is "
          f"{need_s:.4f} of the weight on the desk, over {mu:g}; {x_slide * 100:g} cm is {(x_slide - xs) * 100:.1f} cm "
          f"over the line; RK4 from rest: the chain is all off the desk at {run['t_off']:.4f} s (closed form "
          f"acosh((L - x*) / (x0 - x*)) / k = {t_c:.4f} s, diff {run['t_off'] - t_c:+.1e} s) with the last link moving "
          f"at {run['v_off']:.4f} m/s = {run['v_off']:.2f} m/s (closed form k (x0 - x*) sinh(k t) = {v_c:.4f} m/s, diff "
          f"{run['v_off'] - v_c:+.1e} m/s), {run['steps']} steps; the hanging length stays within {err_x:.1e} m of the "
          f"cosh form over the run; half-step rerun (dt = {0.5 * dt:.0e} s): off at {half['t_off']:.7f} s "
          f"({half['t_off'] - run['t_off']:+.1e} s) at {half['v_off']:.7f} m/s ({half['v_off'] - run['v_off']:+.1e} m/s); "
          f"after the edge the whole chain falls freely from {run['v_off']:.2f} m/s")
    assert abs(run["t_off"] - t_c) < 1e-4 and err_x < 1e-6 and abs(half["t_off"] - run["t_off"] ) < 1e-4
    assert net_s > 0.0 and x_slide > xs
    marks = []
    for label, xm in (("the excess doubled to 4 cm", xs + 2.0 * (x_slide - xs)),
                      ("the hanging part at 30 cm", 0.30),
                      ("the excess at 20 cm (hanging 40 cm)", 0.40),
                      ("the hanging part at 50 cm", 0.50),
                      ("the excess at 20 times its start (hanging 60 cm)", xs + 20.0 * (x_slide - xs)),
                      ("the hanging part at 75 cm", 0.75),
                      ("the hanging part at 100 cm", L)):
        tm, vm = crossing(run, xm)
        tc = math.acosh((xm - xs) / (x_slide - xs)) / k
        marks.append(f"{label} at {tm:.4f} s at {vm:.3f} m/s (closed form {tc:.4f} s, diff {tm - tc:+.1e} s)")
    print("crossings (RK4 table, 22 cm chain): " + "; ".join(marks))
    ev: dict = {"xs": xs, "k": k, "runs": {"hold": static_run(x_hold, mu, g, L), "slide": run}, "need": {"hold": need_h,
                "slide": need_s}, "t_c": t_c, "v_c": v_c}
    # Other hanging lengths, the frictionless case and the other grips, for the description.
    descr = []
    ev["others"] = {}
    for x0 in man["description_hangs_m"]:
        r0 = rk4_slide(x0, mu, g, L, dt)
        t0, v0 = closed_off(x0, mu, g, L)
        ev["others"][x0] = r0["t_off"]
        descr.append(f"{x0 * 100:g} cm over the edge (grip needed {x0 / (L - x0):.4f}): all off at {r0['t_off']:.4f} s "
                     f"at {r0['v_off']:.2f} m/s (closed form {t0:.4f} s, diff {r0['t_off'] - t0:+.1e} s)")
    x_f = man["frictionless_hang_m"]
    r_f = rk4_slide(x_f, 0.0, g, L, dt)
    t_f, v_f = closed_off(x_f, 0.0, g, L)
    ev["t_free"] = r_f["t_off"]
    descr.append(f"no friction (mu 0) with {x_f * 100:g} cm over the edge: the line is at 0 cm and k = sqrt(g / L) = "
                 f"{rate(0.0, g, L):.4f} per second; all off at {r_f['t_off']:.4f} s at {r_f['v_off']:.2f} m/s (closed form "
                 f"acosh(L / x0) / k = {t_f:.4f} s, diff {r_f['t_off'] - t_f:+.1e} s)")
    ev["pct"] = {}
    for m2 in man["description_mus"]:
        ev["pct"][m2] = threshold(m2, L) / L * 100.0
        descr.append(f"grip {m2:g} needs {threshold(m2, L) / L * 100.0:.2f} percent over the edge "
                     f"({threshold(m2, L) * 100:.2f} cm of {L:g} m)")
    L2 = man["description_chain_m"]
    descr.append(f"grip {mu:g} with {L2:g} m of chain needs {threshold(mu, L2) * 100:.1f} cm = {threshold(mu, L2) / L2 * 100:.2f} "
                 f"percent, the same fifth; the chain's weight cancels, so a heavy chain and a light one share the line")
    print("for the description: " + "; ".join(descr))
    assert abs(r_f["t_off"] - t_f) < 1e-4
    # The schedule in video time.
    t0 = man["first_cycle_at"]
    k0 = math.ceil((0.0 - t0) / P - 1e-9) - 1
    k1 = math.floor((D - t0) / P - 1e-9)
    starts = [t0 + kk * P for kk in range(k0, k1 + 1)]
    ev["cycles"] = int(round(cycles))

    def lst(off_: float) -> str:
        return ", ".join(f"{st + off_:.2f}" for st in starts if 0.0 <= st + off_ < D)

    top = float(man["desk_top_dy"])
    cy = top - BEAD_R                                   # the chain's corner point (its beads' centre line)
    tip_y_full = cy + L * ppm + BEAD_R                  # the tip's lowest pixel with the chain all over the edge
    assert tip_y_full < BAND_H - 4, "the chain all over the edge leaves the band"
    gone_depth = (BAND_H - cy + BEAD_R) / ppm           # the tail must fall this far past the corner to leave the band
    t_gone = (-run["v_off"] + math.sqrt(run["v_off"] ** 2 + 2.0 * g * gone_depth)) / g
    ev["t_gone"] = t_gone
    gone_v = pa + S * (run["t_off"] + t_gone)
    assert gone_v < P - F, "the fallen chain is still in the band at the reset fade"
    tau0 = (0.0 - t0) % P
    r0 = (tau0 - pa) / S
    st0 = {m: state_at(ev["runs"][m], r0) for m in PANELS}
    vt = lambda real: pa + real * S   # noqa: E731  video time after the cycle start
    cross_v = "; ".join(f"{xm * 100:.0f} cm at {lst(vt(crossing(run, xm)[0]))} s" for xm in (0.30, 0.50, 0.75))
    print(f"schedule (video time, 1/{S:g} speed): cycles of {P:g} s start at " + ", ".join(f"{st:.2f}" for st in starts)
          + f" s (the first {-t0:.2f} s before the first frame); the clamps let go {pa:g} s into each cycle at {lst(pa)} s; "
          f"the 22 cm chain's hanging part passes {cross_v}; it is all off the desk {S * run['t_off']:.2f} s after the "
          f"release at {lst(vt(run['t_off']))} s (the event row lights) and its tail is out of the band {S * t_gone:.2f} s "
          f"later at {lst(gone_v)} s ({gone_v:.2f} s into the cycle, before the fade at {P - F:.2f} s); the 18 cm chain "
          f"never moves and its event row lights {man['hold_event_after_s']:g} s after the release at "
          f"{lst(pa + man['hold_event_after_s'])} s; the clamp lifts over {man['clamp_lift_s']:g} s; the reset crossfade "
          f"runs over the last {F:g} s of each cycle (from {lst(P - F)} s; the readouts out over its first half and in "
          f"over its second); on the first frame the cycle is {tau0:.2f} s in ({r0:.3f} s real after the release: the 18 cm "
          f"chain {st0['hold']['phase']} at {st0['hold']['x'] * 100:.1f} cm, the 22 cm chain {st0['slide']['phase']} at "
          f"{st0['slide']['x'] * 100:.1f} cm); title until {man['title_until']:g} s; payoff card from {man['payoff_t']:g} s; "
          f"the title fades back in over the last {man['loop_fade']:g} s and the last frame repeats the first (the scene "
          f"is periodic: {D:g} s holds exactly {cycles:.0f} cycles)")
    # Text widths.
    font = os.environ["SEED_ZERO_FONT"]
    f24, f28, f34, f40, f56 = (ImageFont.truetype(font, n) for n in (24, 28, 34, 40, 56))
    widths = {"overlay@34": (f34, man["overlay"])}
    for j, line in enumerate(man["title"].split("|")):
        widths[f"title line {j + 1}@56"] = (f56, line)
    widths["legend@40"] = (f40, legend_text(man))
    widths["clock@28"] = (f28, clock_text(1.2515))
    widths["clock held@28"] = (f28, clock_text(-1.0))
    for m in PANELS:
        widths[f"label {m}@40"] = (f40, label_text(man, m))
        widths[f"sublabel {m}@28"] = (f28, sub_text(man, ev, m))
        widths[f"fixed {m}@28"] = (f28, fixed_text(man, ev, m))
        widths[f"event {m}@40"] = (f40, event_text(ev, m))
    widths["hanging@40"] = (f40, hanging_text(L))
    widths["off@40"] = (f40, off_text())
    widths["speed@28"] = (f28, speed_text(2.8))
    widths["last link@28"] = (f28, last_text(ev))
    widths["on the desk@28"] = (f28, desk_text(L))
    widths["tick@24"] = (f24, tick_text(ev))
    for j, line in enumerate(payoff_lines(man, ev)):
        widths[f"payoff line {j + 1}@40"] = (f40, line)
    print("text widths: " + ", ".join(f"{kk} {f.getlength(s):.0f} px" for kk, (f, s) in widths.items()))
    assert all(f.getlength(s) < 950 for f, s in widths.values()), "a text line is wider than 950 px"
    assert len(payoff_lines(man, ev)) <= 6, "the card has more than six lines"
    # Layout checks.
    left = ROW_X0 + max(max(f40.getlength(label_text(man, m)), f28.getlength(sub_text(man, ev, m)),
                            f28.getlength(fixed_text(man, ev, m))) for m in PANELS)
    right = ROW_X1 - max(f40.getlength(hanging_text(L)), f40.getlength(off_text()), f28.getlength(speed_text(2.8)),
                         f28.getlength(last_text(ev)), f28.getlength(desk_text(L)))
    rows_bottom = FIX_DY + 16
    edge = float(man["edge_x_px"])
    clamp_x0, clamp_x1 = edge - 64.0, edge - 64.0 + CLAMP_W
    clamp_top = top - 2.0 * BEAD_R - CLAMP_PAD - CLAMP_STEM - CLAMP_LIFT
    ev_w = max(f40.getlength(event_text(ev, m)) for m in PANELS)
    ev_x0, ev_x1 = EVENT_X - ev_w / 2.0, EVENT_X + ev_w / 2.0
    tick_y = cy + xs * ppm
    tick_x1 = edge + BEAD_R + 38.0 + f24.getlength(tick_text(ev))
    print(f"row check: the left column ends at x {left:.0f} px, the right column starts at x {right:.0f} px; both end "
          f"{rows_bottom} px under the band top; the desk top is {top:.0f} px under the band top (slab to {top + SLAB_PX:.0f}, "
          f"legs at x {LEG_X[0]} and {LEG_X[1]} to {BAND_H - LEG_GAP}); the clamp spans x {clamp_x0:.0f} to {clamp_x1:.0f} "
          f"px between the columns and rises to {clamp_top:.0f} px under the band top when lifted; the event row spans "
          f"{EVENT_DY - 22} to {EVENT_DY + 22} px under the band top and x {ev_x0:.0f} to {ev_x1:.0f} px (widest {ev_w:.0f} "
          f"px, centred on {EVENT_X}) between the legs; the chain hangs at x {edge + BEAD_R:.0f} px from {cy:.0f} px under "
          f"the band top and its tip reaches {tip_y_full:.0f} px with the chain all over the edge; the one fifth tick at "
          f"{tick_y:.0f} px under the band top, its label to x {tick_x1:.0f} px; each band is {BAND_H} px tall (y "
          f"{BAND_Y['hold']} to {BAND_Y['hold'] + BAND_H} and {BAND_Y['slide']} to {BAND_Y['slide'] + BAND_H}); the caption "
          f"band starts at y {int(man['caption_y'] * H)}; the title rows end at y {252 + 28} and the overlay band ends at y 130")
    assert right - left > 40, "the columns meet"
    assert clamp_x0 > left + 10 and clamp_x1 < right - 10, "the clamp meets a text column"
    assert clamp_top > 4, "the lifted clamp leaves the band"
    assert top > rows_bottom + 10, "the desk meets the text rows"
    assert ev_x0 > LEG_X[0] + LEG_W + 16 and ev_x1 < LEG_X[1] - 16, "the event row meets a leg"
    assert EVENT_DY - 22 > top + SLAB_PX + 10 and EVENT_DY + 22 < BAND_H - LEG_GAP, "the event row leaves the desk space"
    assert tick_x1 < W - 40 and tick_y > rows_bottom + 10, "the one fifth tick label does not fit"
    assert BAND_Y["slide"] + BAND_H <= int(man["caption_y"] * H), "the bottom band reaches the caption band"
    assert PAYOFF_Y - 20 > int(man["caption_y"] * H) + 90, "the card meets the caption band"
    return ev


def legend_text(man: dict) -> str:
    return f"same desk, same chain, 1/{man['slow']:g} speed"


def clock_text(r: float) -> str:
    return "held, at rest" if r < 0.0 else f"{r:.3f} s after the release"


def label_text(man: dict, m: str) -> str:
    return f"{man['hang_m'][m] * 100:g} cm over the edge"


def sub_text(man: dict, ev: dict, m: str) -> str:
    return f"grip needed {ev['need'][m]:.2f}, has {man['mu']:g}"


def fixed_text(man: dict, ev: dict, m: str) -> str:
    d = (man["hang_m"][m] - ev["xs"]) * 100.0
    return f"{abs(d):.0f} cm {'over' if d > 0 else 'under'} the line"


def hanging_text(x: float) -> str:
    return f"hanging {x * 100:.0f} cm"


def off_text() -> str:
    return "off the desk"


def speed_text(v: float) -> str:
    return f"speed {v:.2f} m/s"


def last_text(ev: dict) -> str:
    return f"last link at {ev['runs']['slide']['v_off']:.2f} m/s"


def desk_text(x: float) -> str:
    return f"on the desk {x * 100:.0f} cm"


def event_text(ev: dict, m: str) -> str:
    if m == "hold":
        return "holds, for ever"
    return f"slides off at {ev['runs']['slide']['t_off']:.2f} s"


def tick_text(ev: dict) -> str:
    return f"{ev['xs'] * 100:.0f} cm, one fifth"


def payoff_lines(man: dict, ev: dict) -> list[str]:
    o = ev["others"]
    text = man["payoff_text"].format(
        t_off=ev["runs"]["slide"]["t_off"], xs_cm=ev["xs"] * 100.0, t21=o[0.21], t25=o[0.25], t30=o[0.3],
        pct4=ev["pct"][0.4], pct1=ev["pct"][0.1], t_free=ev["t_free"])
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
        self.pa, self.F = man["release_at"], man["reset_fade"]
        self.runs = ev["runs"]
        self.L, self.link = man["chain_m"], man["link_m"]
        self.n_links = int(round(self.L / self.link))
        self.edge = float(man["edge_x_px"])
        self.top = float(man["desk_top_dy"])
        self.cx, self.cy = self.edge + BEAD_R, self.top - BEAD_R    # the chain's corner point

    def phase(self, f: int) -> tuple[int, float]:
        k, tau_f = divmod(f - self.c0_f, self.P_f)
        return k, tau_f / self.fps

    @staticmethod
    def L_(x: float, y: float) -> tuple[float, float]:
        """Layer (2x) pixel of a band-local point, rounded to 1e-4 px so equal states draw equal pixels."""
        return round(x * SS, 4), round(y * SS, 4)

    def bead_pos(self, s: float, x: float) -> tuple[float, float]:
        """Band-local centre of the chain point s metres from the tail with hanging length x: on the
        desk d = (L - x) - s metres before the corner, after the corner d below it."""
        d = (self.L - x) - s
        if d >= 0.0:
            return self.cx - d * self.ppm, self.cy
        return self.cx, self.cy - d * self.ppm

    def draw_desk(self, d: ImageDraw.ImageDraw) -> None:
        man = self.man
        x0, top = float(man["desk_x0_px"]), self.top
        s0, s1 = self.L_(x0, top), self.L_(self.edge, top + SLAB_PX)
        d.rounded_rectangle((s0[0], s0[1], s1[0], s1[1]), radius=6 * SS, fill=DECK_A)
        t0, t1 = self.L_(x0 + 6, top), self.L_(self.edge - 6, top)
        d.line((*t0, *t1), fill=DECK_B, width=3 * SS)
        e0, e1 = self.L_(self.edge - 1, top + 6), self.L_(self.edge - 1, top + SLAB_PX - 6)
        d.line((*e0, *e1), fill=RIM, width=3 * SS)
        for lx in LEG_X:
            l0, l1 = self.L_(lx, top + SLAB_PX), self.L_(lx + LEG_W, BAND_H - LEG_GAP)
            d.rectangle((l0[0], l0[1], l1[0], l1[1]), fill=DECK_A)
        # The one fifth tick on the hanging side (its label is drawn at 1x).
        ty = self.cy + self.ev["xs"] * self.ppm
        k0, k1 = self.L_(self.cx + 10, ty), self.L_(self.cx + 30, ty)
        d.line((*k0, *k1), fill=MUTED, width=3 * SS)

    def draw_chain(self, d: ImageDraw.ImageDraw, m: str, x: float) -> None:
        # The connecting line along the path, then the beads (the tip in gold).
        tail = self.bead_pos(0.0, x)
        tip = self.bead_pos(self.L, x)
        pts = [self.L_(*tail)]
        if x < self.L:
            pts.append(self.L_(self.cx, self.cy))
        pts.append(self.L_(*tip))
        d.line(pts, fill=RIM, width=2 * SS)
        r = BEAD_R * SS
        for j in range(self.n_links):
            s = (j + 0.5) * self.link
            X, Y = self.L_(*self.bead_pos(s, x))
            col = WHITE if j % 2 == 0 else STEEL
            d.ellipse((X - r, Y - r, X + r, Y + r), fill=col)
        X, Y = self.L_(*tip)
        rt = (BEAD_R + 1.5) * SS
        d.ellipse((X - rt, Y - rt, X + rt, Y + rt), fill=GOLD)
        # The start-length marker: a small coloured triangle at the resting tip level, left of the chain.
        yx = self.cy + self.man["hang_m"][m] * self.ppm
        p0, p1, p2 = self.L_(self.cx - 12, yx), self.L_(self.cx - 26, yx - 8), self.L_(self.cx - 26, yx + 8)
        d.polygon([p0, p1, p2], fill=COLOUR[m])

    def draw_clamp(self, d: ImageDraw.ImageDraw, tv: float) -> None:
        lift = 0.0 if tv < 0.0 else min(1.0, tv / self.man["clamp_lift_s"])
        a = 1.0 - 0.7 * lift
        x0 = self.edge - 64.0
        yb = self.top - 2.0 * BEAD_R - 1.0 - CLAMP_LIFT * lift
        p0, p1 = self.L_(x0, yb - CLAMP_PAD), self.L_(x0 + CLAMP_W, yb)
        d.rounded_rectangle((p0[0], p0[1], p1[0], p1[1]), radius=4 * SS, fill=blend(CLAMP, a), outline=blend(CLAMP_DARK, a),
                            width=2 * SS)
        s0, s1 = self.L_(x0 + CLAMP_W / 2.0 - 6, yb - CLAMP_PAD - CLAMP_STEM), self.L_(x0 + CLAMP_W / 2.0 + 6, yb - CLAMP_PAD)
        d.rectangle((s0[0], s0[1], s1[0], s1[1]), fill=blend(CLAMP_DARK, a))

    def scene(self, m: str, tau: float) -> tuple[Image.Image, dict]:
        """The band layer of panel m at tau seconds into a cycle (the clamped setup before the release)."""
        layer = Image.new("RGB", (W * SS, BAND_H * SS), BG)
        d = ImageDraw.Draw(layer)
        self.draw_desk(d)
        tv = tau - self.pa
        rt = tv / self.S
        st = state_at(self.runs[m], rt)
        st["tv"], st["rt"] = tv, rt
        self.draw_chain(d, m, st["x"])
        self.draw_clamp(d, tv)
        return layer, st

    def draw_panel(self, m: str, f: int) -> tuple[Image.Image, dict]:
        k, tau = self.phase(f)
        P, F = self.P, self.F
        layer, st = self.scene(m, tau)
        st["alpha"], st["k"] = 1.0, k
        if tau >= P - F:
            # Crossfade to the next cycle's clamped setup (the fallen chain is out of the band by now,
            # asserted in measure; the holding chain is drawn the same in both, so it never blinks).
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
        L = self.L
        for m, st in states.items():
            y0 = BAND_Y[m]
            a, ph = st["alpha"], st["phase"]
            d.text((ROW_X0, y0 + LABEL_DY), label_text(man, m), font=self.font, fill=COLOUR[m], anchor="lm")
            d.text((ROW_X0, y0 + SUB_DY), sub_text(man, ev, m), font=self.font_small, fill=MUTED, anchor="lm")
            if hud_alpha > 0.02:
                d.text((ROW_X0, y0 + FIX_DY), fixed_text(man, ev, m), font=self.font_small,
                       fill=blend(GOLD, 0.85 * hud_alpha), anchor="lm")
            lit = (m == "hold" and st["tv"] >= man["hold_event_after_s"]) or (m == "slide" and ph == OFF)
            if ph == OFF:
                d.text((ROW_X1, y0 + LABEL_DY), off_text(), font=self.font, fill=blend(MUTED, a), anchor="rm")
                d.text((ROW_X1, y0 + SUB_DY), last_text(ev), font=self.font_small, fill=blend(GOLD, a), anchor="rm")
            else:
                d.text((ROW_X1, y0 + LABEL_DY), hanging_text(st["x"]), font=self.font,
                       fill=blend(GOLD if lit else TEXT, a), anchor="rm")
                d.text((ROW_X1, y0 + SUB_DY), speed_text(st["v"]), font=self.font_small, fill=blend(MUTED, a), anchor="rm")
                d.text((ROW_X1, y0 + FIX_DY), desk_text(L - st["x"]), font=self.font_small, fill=blend(MUTED, a),
                       anchor="rm")
            if lit:
                d.text((EVENT_X, y0 + EVENT_DY), event_text(ev, m), font=self.font, fill=blend(GOLD, a), anchor="mm")
            d.text((self.cx + 38, y0 + self.cy + ev["xs"] * self.ppm), tick_text(ev), font=self.font_tiny, fill=MUTED,
                   anchor="lm")
        if hud_alpha > 0.02:
            d.text((W / 2, LEGEND_Y), legend_text(man), font=self.font, fill=blend(TEXT, hud_alpha), anchor="mm")
            d.text((W / 2, CLOCK_Y), clock_text(states["hold"]["rt"]), font=self.font_small,
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
    man = json.loads((ROOT / "projects/deskchain/manifest.json").read_text())
    ev = measure(man)
    if "--measure-only" in sys.argv:
        return
    if "--frames" in sys.argv:
        times = [float(v) for v in sys.argv[sys.argv.index("--frames") + 1].split(",")]
        r = Renderer(man, ev)
        (ROOT / "media/deskchain").mkdir(parents=True, exist_ok=True)
        for tv in times:
            Image.fromarray(r.frame_at(int(round(tv * man["fps"])))).save(ROOT / f"media/deskchain/smoke-{tv}.png")
        print("smoke frames: " + ", ".join(f"{tv}" for tv in times))
        return
    Renderer(man, ev).render(ROOT / "media/deskchain/footage.mp4")


if __name__ == "__main__":
    main()
