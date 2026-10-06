#!/usr/bin/env python3
"""Fingers under a ruler: slide two fingers together under a stick. Where do they meet?

Two panels on the same clock, side view, the same scale: a stick of
length L rests level on two finger pads of width w (their centres at
`left` and `right` from the stick's left end, asymmetric on purpose so
there is no tie). The pads' distances from the stick's balance point are
x_left and x_right; the loads are N_left = W x_right / (x_left + x_right)
and N_right = W x_left / (x_left + x_right) (the finger nearer the
balance point carries more; the weight W cancels). Grip between a pad and
the stick: static mu_s, sliding mu_k (chosen). Exactly one finger slips
at a time: the finger carrying less weight (the one farther from the
balance point) slides under the stick at v while the other holds; the
stick stays still (in your hands the stick drifts along with the gripping
finger instead; the meeting point is the same). The slider's friction
mu_k N_slip is balanced by the holder's static friction, which can reach
mu_s N_hold; the slide ends when mu_k N_slip = mu_s N_hold, that is when
the slider's distance from the balance point is mu_k / mu_s of the
holder's; then they swap. The fingers have met when the pad centres are w
apart (the pads touch); the balance point then lies between them. Because
exactly one finger moves at any instant, the total time is (right - left
- w) / v in every case. Top panel: a uniform ruler, balance point at L /
2. Bottom panel: a hammer-like stick, its heavy head on the left, balance
point 20 cm from the head end. The slip sequence is simulated as an
event-driven Coulomb model: the slider moves at v in steps of dt, the
swap and meeting conditions are tested at each step and the event is
located exactly by bisection inside the step (both conditions are linear
in the slider's travel) and checked against the closed form. The run
repeats every cycle_s seconds of video with a crossfade back to the
resting setup; the cycle divides the scene length, so the scene is
exactly periodic and the last frame equals the first. Shown at real
speed. Deterministic, no seed.

Measured and printed: the start loads, every slip (which finger, how
far, until when, both positions, both loads, the force balance at the
swap), the meeting positions and centre, the slip count, the total time,
the drawn hammer's balance point, the description variants (other grips,
a slower slide, another balance point), the checks against the brief,
the schedule in video time, the on-screen text widths and the layout
clearances.

usage: fingers.py [--measure-only] [--frames t1,t2,...]
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
WOOD = (214, 188, 138)
WOOD_DARK = (150, 124, 78)
INK = (58, 46, 30)
STEEL = (150, 160, 176)
STEEL_DARK = (84, 92, 106)

# Layout: overlay at y 96..130 (captions.py), two title rows at y 190/252 for
# the first seconds, then the legend at y 236 and the shared clock at y 290;
# two panels stacked, the ruler in the band y 330..880 and the hammer in
# y 880..1430, each drawn at 2x in its own geometry layer; each band has its
# label row 40 px under the band top, its second row at 84 and its third at
# 120 (left column from x 40, right column to x 1040); the stick lies level
# with its underside STICK_DY under the band top from x 140 to 940 (800 px
# per metre), the ruler RULER_H tall, the hammer's handle HANDLE_H tall and
# its head HEAD_H tall rising above the handle; the gold balance mark and its
# label above the stick; the finger pads hang PAD_H under the stick, the
# load bars under them, their labels under the bars, the hammer band's
# dashed first-swap mark and its label under those, the gold event row at
# EVENT_DY; captions at caption_y 0.75 (y 1440..1530); the six-line card
# from y 1572 at a 48 px pitch.
LEGEND_Y, CLOCK_Y = 236, 290
SS = 2
PAYOFF_Y, PAYOFF_PITCH = 1572.0, 48
PANELS = ("ruler", "hammer")
BAND_Y = {"ruler": 330, "hammer": 880}
BAND_H = 550
LABEL_DY, SUB_DY, FIX_DY = 40, 84, 120
ROW_X0, ROW_X1 = 40, 1040
STICK_DY = 256            # the stick's underside (the pads touch it here)
RULER_H, HANDLE_H, HEAD_H = 40, 16, 56
PAD_H = 80
BAR_DY, BAR_H, BAR_FULL = 352, 16, 160   # the load bars: 160 px for the whole weight
LOAD_DY = 386             # the load labels' centre line (24 px)
SWAP_LABEL_DY = 274       # the hammer band's "first swap" label (24 px), right of the dashed mark
SWAP_LINE_END = 346       # the dashed mark ends under the pads, above the load bars
EVENT_DY = 480
TICK_LEN, TICK_LEN_20 = 10, 16
COLOUR = {"left": TEAL, "right": CORAL}
BAND_COLOUR = {"ruler": TEAL, "hammer": CORAL}
REST, SLIDE, MET = "rest", "slide", "met"


def blend(col, a: float, base=BG) -> tuple:
    a = max(0.0, min(1.0, a))
    return tuple(int(round(c * a + b * (1 - a))) for c, b in zip(col, base))


# --- measurement --------------------------------------------------------------
def loads(xa: float, xb: float) -> tuple[float, float]:
    """(N_left, N_right) in units of the weight W for pads xa and xb from the balance point."""
    return xb / (xa + xb), xa / (xa + xb)


def simulate(com: float, mu_s: float, mu_k: float, left: float, right: float, v: float, width: float,
             dt: float) -> dict:
    """Event-driven Coulomb slips: the finger farther from the balance point (less load) slides at v
    while the other holds; at each step of dt the swap condition x_slip <= (mu_k / mu_s) x_hold and the
    meeting condition xa + xb <= width are tested; the first event inside a step is located by bisection
    (both are linear in the slider's travel) and compared with the closed form. Returns every slip,
    the piecewise-linear position table and the end state."""
    r = mu_k / mu_s
    xa, xb = com - left, right - com          # the pads' distances from the balance point
    assert xa > 0.0 and xb > 0.0, "both pads must be outside the balance point"
    slider = "left" if xa > xb else "right"
    t, n_steps, max_dev = 0.0, 0, 0.0
    slips: list[dict] = []
    table_t, table_l, table_r = [0.0], [left], [right]
    while xa + xb > width + 1e-12:
        xs, xh = (xa, xb) if slider == "left" else (xb, xa)
        d_swap = xs - r * xh                   # travel until mu_k N_slip = mu_s N_hold
        d_meet = xa + xb - width               # travel until the pads touch
        d_closed = min(d_swap, d_meet)
        assert d_closed > 0.0

        def event(s: float) -> float:          # min of both margins after a travel s; negative past the event
            return min(xs - s - r * xh, xa + xb - s - width)

        # Step at dt until the event is inside a step, then bisect inside the step.
        s0 = 0.0
        while event(s0 + v * dt) > 0.0:
            s0 += v * dt
            n_steps += 1
        lo, hi = s0, s0 + v * dt
        for _ in range(80):
            mid = 0.5 * (lo + hi)
            if event(mid) > 0.0:
                lo = mid
            else:
                hi = mid
        n_steps += 1
        d = 0.5 * (lo + hi)
        max_dev = max(max_dev, abs(d - d_closed))
        t += d / v
        if slider == "left":
            xa -= d
        else:
            xb -= d
        nl, nr = loads(xa, xb)
        n_slip, n_hold = (nl, nr) if slider == "left" else (nr, nl)
        slips.append({"finger": slider, "d": d, "d_closed": d_closed, "t": t, "left": com - xa, "right": com + xb,
                      "N_left": nl, "N_right": nr, "f_slip": mu_k * n_slip, "f_hold": mu_s * n_hold,
                      "ratio": (xa / xb if slider == "left" else xb / xa), "met": d_meet <= d_swap + 1e-15})
        table_t.append(t)
        table_l.append(com - xa)
        table_r.append(com + xb)
        slider = "right" if slider == "left" else "left"
    return {"slips": slips, "t_total": t, "left": com - xa, "right": com + xb, "centre": com + 0.5 * (xb - xa),
            "com": com, "mu_s": mu_s, "mu_k": mu_k, "v": v, "width": width, "left0": left, "right0": right,
            "table": (np.array(table_t), np.array(table_l), np.array(table_r)), "steps": n_steps, "max_dev": max_dev}


def state_at(run: dict, rt: float) -> dict:
    """Pad centres, the slider, the completed slips, the loads and the slip's start position rt real
    seconds after the fingers started (at rest before, met after)."""
    tt, tl, tr = run["table"]
    com = run["com"]
    if rt <= 0.0:
        xa, xb = com - run["left0"], run["right0"] - com
        nl, nr = loads(xa, xb)
        return {"left": run["left0"], "right": run["right0"], "phase": REST, "slider": None, "slips": 0,
                "N_left": nl, "N_right": nr, "trail_from": None}
    if rt >= run["t_total"]:
        nl, nr = loads(com - run["left"], run["right"] - com)
        return {"left": run["left"], "right": run["right"], "phase": MET, "slider": None, "slips": len(run["slips"]),
                "N_left": nl, "N_right": nr, "trail_from": None}
    k = int(np.searchsorted(tt, rt, side="right")) - 1       # the slip in progress is slips[k]
    left = float(np.interp(rt, tt, tl))
    right = float(np.interp(rt, tt, tr))
    nl, nr = loads(com - left, right - com)
    slip = run["slips"][k]
    return {"left": left, "right": right, "phase": SLIDE, "slider": slip["finger"], "slips": k,
            "N_left": nl, "N_right": nr, "trail_from": (tl[k] if slip["finger"] == "left" else tr[k])}


def hammer_shape(man: dict) -> dict:
    """The drawn hammer: a head (head_m long, head_h_m tall, density_ratio times the handle's) at the left
    end and a handle (handle_h_m tall) to the right end; the balance point from the closed form and from
    the 2x pixel mask it is drawn from."""
    L, hm, hh, th, rho = man["stick_m"], man["head_m"], man["head_h_m"], man["handle_h_m"], man["head_density_ratio"]
    a_head, a_handle = hm * hh, (L - hm) * th
    com = (rho * a_head * hm / 2.0 + a_handle * (hm + (L - hm) / 2.0)) / (rho * a_head + a_handle)
    ppm = float(man["px_per_m"])
    x0 = float(man["stick_x0_px"])
    layer = Image.new("L", (W * SS, BAND_H * SS), 0)
    d = ImageDraw.Draw(layer)
    hx0, hx1 = x0 * SS, (x0 + hm * ppm) * SS
    d.rectangle((hx1, (STICK_DY - HANDLE_H) * SS, (x0 + L * ppm) * SS - 1, STICK_DY * SS - 1), fill=1)
    d.rectangle((hx0, (STICK_DY - HEAD_H) * SS, hx1 - 1, STICK_DY * SS - 1), fill=2)
    m = np.asarray(layer)
    xs = np.arange(m.shape[1]) + 0.5
    wgt = np.where(m == 2, rho, 0.0) + np.where(m == 1, 1.0, 0.0)
    cx = float((wgt * xs[None, :]).sum() / wgt.sum())
    com_px = (cx / SS - x0) / ppm
    return {"com": com, "com_px": com_px, "a_head": a_head, "a_handle": a_handle, "head_px": hm * ppm}


def measure(man: dict) -> dict:
    L, w, v = man["stick_m"], man["pad_m"], man["speed_m_s"]
    left, right = man["left_m"], man["right_m"]
    mu_s, mu_k = man["mu_s"], man["mu_k"]
    dt = 1.0 / man["steps_per_second"]
    P, D, fps, F, sa = man["cycle_s"], man["scene_duration"], man["fps"], man["reset_fade"], man["start_at"]
    cycles = D / P
    assert abs(cycles - round(cycles)) < 1e-9, "the cycle must divide the scene length"
    for key in ("cycle_s", "start_at", "first_cycle_at", "reset_fade"):
        assert abs(man[key] * fps - round(man[key] * fps)) < 1e-9, f"{key} must be a whole number of frames"
    ppm = float(man["px_per_m"])
    com = man["balance_m"]
    r = mu_k / mu_s
    t_total = (right - left - w) / v
    print(f"setup: side view, two panels on one clock at the same scale: a stick of {L:g} m rests level on two finger pads "
          f"{w * 100:g} cm wide, the left pad's centre at {left * 100:g} cm and the right pad's centre at {right * 100:g} cm "
          f"from the left end (asymmetric on purpose, so there is no tie); grip between the pads and the stick: static "
          f"{mu_s:g}, sliding {mu_k:g} (chosen); with x_left and x_right the pads' distances from the balance point the loads "
          f"are N_left = W x_right / (x_left + x_right) and N_right = W x_left / (x_left + x_right) (the finger nearer the "
          f"balance point carries more; the weight W cancels, g = {man['g']:g} m/s^2 never enters); exactly one finger slips "
          f"at a time: the finger carrying less weight slides under the stick at {v * 100:g} cm/s while the other holds and "
          f"the stick stays still (in your hands the stick drifts along with the gripping finger instead; the meeting point "
          f"is the same); the slide ends when {mu_k:g} N_slip = {mu_s:g} N_hold, that is when the slider's distance from the "
          f"balance point is {mu_k:g} / {mu_s:g} = {r:.4f} of the holder's; then they swap; the fingers have met when the "
          f"pad centres are {w * 100:g} cm apart; top panel a uniform ruler with its balance point at {com['ruler'] * 100:g} "
          f"cm, bottom panel a hammer-like stick with its balance point {com['hammer'] * 100:g} cm from the head end (the "
          f"head on the left); event-driven Coulomb model stepped at {man['steps_per_second']} steps per second (dt = "
          f"{dt:.0e} s), each swap located by bisection inside its step and checked against the closed form; total time "
          f"({right * 100:g} - {left * 100:g} - {w * 100:g}) cm / {v * 100:g} cm/s = {t_total:.3f} s in every case because "
          f"exactly one finger moves at any instant; shown at real speed on a {P:g} s cycle ({P * fps:.0f} frames) with the "
          f"fingers starting {sa:g} s into the cycle, {cycles:.0f} cycles in {D:g} s; drawn at {ppm:g} px per metre; "
          f"deterministic, no seed")
    starts = {}
    for m in PANELS:
        xa, xb = com[m] - left, right - com[m]
        nl, nr = loads(xa, xb)
        starts[m] = (nl, nr, "left" if xa > xb else "right")
    print(f"start loads: ruler left ({(com['ruler'] - left) * 100:g} cm from the middle) {starts['ruler'][0]:.4f} W, right "
          f"({(right - com['ruler']) * 100:g} cm) {starts['ruler'][1]:.4f} W: the {starts['ruler'][2]} finger slips first; "
          f"hammer left ({(com['hammer'] - left) * 100:g} cm from the balance point) {starts['hammer'][0]:.4f} W, right "
          f"({(right - com['hammer']) * 100:g} cm) {starts['hammer'][1]:.4f} W: the {starts['hammer'][2]} finger slips first")
    ev: dict = {"runs": {}, "starts": starts, "t_total": t_total, "ratio": r}
    max_bal = 0.0
    for m in PANELS:
        run = simulate(com[m], mu_s, mu_k, left, right, v, w, dt)
        ev["runs"][m] = run
        name = "ruler, balance point 50 cm (top panel)" if m == "ruler" else "hammer stick, balance point 20 cm from the head end (bottom panel)"
        print(f"{name}: fingers meet at {run['left'] * 100:.2f} / {run['right'] * 100:.2f} cm (centre {run['centre'] * 100:.2f} cm, "
              f"{abs(run['centre'] - com[m]) * 100:.2f} cm from the balance point, inside the {w * 100:g} cm gap) after "
              f"{len(run['slips'])} slips and {run['t_total']:.3f} s at {v * 100:g} cm/s, final gap "
              f"{(run['right'] - run['left']) * 100:.1f} cm; {run['steps']} steps, every event within {run['max_dev']:.1e} m of "
              f"its closed form")
        for j, s in enumerate(run["slips"]):
            bal = abs(s["f_slip"] - s["f_hold"])
            if not s["met"]:
                max_bal = max(max_bal, bal)
            tail = (f"the pads touch" if s["met"] else
                    f"swap: {mu_k:g} x {s['N_left' if s['finger'] == 'left' else 'N_right']:.4f} = {s['f_slip']:.4f} W = "
                    f"{mu_s:g} x {s['N_right' if s['finger'] == 'left' else 'N_left']:.4f} = {s['f_hold']:.4f} W (diff "
                    f"{s['f_slip'] - s['f_hold']:+.1e}), the slider's distance {s['ratio']:.4f} of the holder's")
            print(f"   slip {j + 1}: {s['finger']} finger slid {s['d'] * 100:.2f} cm until t {s['t']:.3f} s: fingers at "
                  f"{s['left'] * 100:.2f} and {s['right'] * 100:.2f} cm; loads left {s['N_left']:.4f} W, right {s['N_right']:.4f} W; {tail}")
        assert abs(run["t_total"] - t_total) < 1e-9, "the total time must be the gap over the speed"
        assert abs(run["centre"] - com[m]) < w / 2.0, "the fingers must meet at the balance point"
    assert max_bal < 1e-9, "the force balance at a swap failed"
    hs = hammer_shape(man)
    ev["hammer_shape"] = hs
    print(f"hammer shape: a head {man['head_m'] * 100:g} cm long and {man['head_h_m'] * 100:g} cm tall at the left end "
          f"({hs['head_px']:.0f} px) with {man['head_density_ratio']:g} times the handle's density, a handle "
          f"{man['handle_h_m'] * 100:g} cm tall to the right end; areas {hs['a_head'] * 1e4:.0f} and {hs['a_handle'] * 1e4:.0f} "
          f"cm^2; balance point of the drawn shape {hs['com'] * 100:.2f} cm from the head end (closed form), "
          f"{hs['com_px'] * 100:.2f} cm from the 2x pixel mask it is drawn from (diff {(hs['com_px'] - hs['com']) * 100:+.1e} cm); "
          f"the model's {com['hammer'] * 100:g} cm")
    assert abs(hs["com"] - com["hammer"]) < 1e-9 and abs(hs["com_px"] - com["hammer"]) < 2e-4
    # Variants for the description.
    descr = []
    ev["variants"] = {}
    for ms, mk in man["description_grips"]:
        for m in PANELS:
            rv = simulate(com[m], ms, mk, left, right, v, w, dt)
            ev["variants"][(m, ms, mk)] = rv
            s0 = rv["slips"][0]
            descr.append(f"{m}, grips {ms:g} / {mk:g}: {len(rv['slips'])} slips, the {s0['finger']} finger slides {s0['d'] * 100:.2f} "
                         f"cm first to {(s0['left'] if s0['finger'] == 'left' else s0['right']) * 100:.1f} cm ({s0['t']:.3f} s), "
                         f"meeting at {rv['left'] * 100:.2f} / {rv['right'] * 100:.2f} cm (centre {rv['centre'] * 100:.2f} cm) at "
                         f"{rv['t_total']:.3f} s")
    for v2 in man["description_speeds_m_s"]:
        rv = simulate(com["ruler"], mu_s, mu_k, left, right, v2, w, dt)
        ev["variants"][("ruler", "v", v2)] = rv
        same = all(abs(a["left"] - b["left"]) < 1e-9 and abs(a["right"] - b["right"]) < 1e-9
                   for a, b in zip(rv["slips"], ev["runs"]["ruler"]["slips"])) and len(rv["slips"]) == len(ev["runs"]["ruler"]["slips"])
        descr.append(f"ruler at {v2 * 100:g} cm/s: {len(rv['slips'])} slips, the same positions ({'yes' if same else 'NO'}), "
                     f"meeting at {rv['left'] * 100:.2f} / {rv['right'] * 100:.2f} cm at {rv['t_total']:.3f} s")
    for c2 in man["description_balances_m"]:
        rv = simulate(c2, mu_s, mu_k, left, right, v, w, dt)
        ev["variants"][("com", c2)] = rv
        s0 = rv["slips"][0]
        descr.append(f"a stick with its balance point at {c2 * 100:g} cm: {len(rv['slips'])} slips, the {s0['finger']} finger slides "
                     f"{s0['d'] * 100:.2f} cm first, meeting at {rv['left'] * 100:.2f} / {rv['right'] * 100:.2f} cm (centre "
                     f"{rv['centre'] * 100:.2f} cm) at {rv['t_total']:.3f} s")
    all_bal = all(abs(rv["centre"] - rv["com"]) < w / 2.0 for rv in ev["variants"].values())
    descr.append(f"in every case the fingers meet at the balance point (the gap's centre within {w * 50:g} cm of it: "
                 f"{'yes' if all_bal else 'NO'})")
    print("for the description: " + "; ".join(descr))
    assert all_bal
    # The brief's checks.
    rr, rh = ev["runs"]["ruler"], ev["runs"]["hammer"]
    checks: list[tuple[str, float, float, float]] = [
        ("ruler slips", len(rr["slips"]), 15, 0), ("ruler meet left (cm)", rr["left"] * 100, 49.21, 6e-3),
        ("ruler meet right (cm)", rr["right"] * 100, 50.71, 6e-3), ("ruler meet centre (cm)", rr["centre"] * 100, 49.96, 6e-3),
        ("ruler total time (s)", rr["t_total"], 8.350, 6e-4),
        ("hammer slips", len(rh["slips"]), 11, 0), ("hammer meet left (cm)", rh["left"] * 100, 19.16, 6e-3),
        ("hammer meet right (cm)", rh["right"] * 100, 20.66, 6e-3), ("hammer meet centre (cm)", rh["centre"] * 100, 19.91, 6e-3),
        ("hammer total time (s)", rh["t_total"], 8.350, 6e-4),
        ("ruler start load left (W)", starts["ruler"][0], 0.4706, 6e-5), ("ruler start load right (W)", starts["ruler"][1], 0.5294, 6e-5),
        ("hammer start load left (W)", starts["hammer"][0], 0.8235, 6e-5), ("hammer start load right (W)", starts["hammer"][1], 0.1765, 6e-5),
        ("slider stops at (of the holder's distance)", r, 0.75, 1e-12),
    ]
    for j, (pos, tt) in enumerate(((20.0, 1.500), (72.5, 3.250), (33.13, 4.563), (62.66, 5.547))):
        s = rr["slips"][j]
        checks += [(f"ruler swap {j + 1} position (cm)", (s["left"] if s["finger"] == "left" else s["right"]) * 100, pos, 6e-3),
                   (f"ruler swap {j + 1} time (s)", s["t"], tt, 6e-4)]
    checks += [("hammer first slide (cm)", rh["slips"][0]["d"] * 100, 58.75, 6e-3), ("hammer first slide finger is right", 1.0 if rh["slips"][0]["finger"] == "right" else 0.0, 1.0, 0)]
    for j, (pos, tt) in enumerate(((31.25, 5.875), (11.56, 6.531), (26.33, 7.023), (15.25, 7.393))):
        s = rh["slips"][j]
        checks += [(f"hammer swap {j + 1} position (cm)", (s["left"] if s["finger"] == "left" else s["right"]) * 100, pos, 6e-3),
                   (f"hammer swap {j + 1} time (s)", s["t"], tt, 6e-4)]
    s = rr["slips"][0]
    checks += [("holder load at a swap (W)", s["N_left"], 0.5714, 6e-5), ("slider load at a swap (W)", s["N_right"], 0.4286, 6e-5)]
    va = ev["variants"][("ruler", 0.5, 0.45)]
    checks += [("ruler grips 0.5 / 0.45 slips", len(va["slips"]), 39, 0), ("ruler grips 0.5 / 0.45 first swap (cm)", va["slips"][0]["left"] * 100, 14.0, 6e-2),
               ("ruler grips 0.5 / 0.45 first swap (s)", va["slips"][0]["t"], 0.900, 6e-4)]
    vb = ev["variants"][("ruler", 0.6, 0.3)]
    checks += [("ruler grips 0.6 / 0.3 slips", len(vb["slips"]), 7, 0), ("ruler grips 0.6 / 0.3 first swap (cm)", vb["slips"][0]["left"] * 100, 30.0, 6e-2),
               ("ruler grips 0.6 / 0.3 first swap (s)", vb["slips"][0]["t"], 2.500, 6e-4)]
    vc = ev["variants"][("hammer", 0.6, 0.3)]
    checks += [("hammer grips 0.6 / 0.3 slips", len(vc["slips"]), 5, 0), ("hammer grips 0.6 / 0.3 first slide (cm)", vc["slips"][0]["d"] * 100, 62.50, 6e-3)]
    vd = ev["variants"][("ruler", "v", 0.05)]
    checks += [("ruler at 5 cm/s total time (s)", vd["t_total"], 16.700, 6e-4), ("ruler at 5 cm/s meet left (cm)", vd["left"] * 100, 49.21, 6e-3)]
    ve = ev["variants"][("com", 0.3)]
    checks += [("balance 30 cm slips", len(ve["slips"]), 13, 0), ("balance 30 cm meet left (cm)", ve["left"] * 100, 29.21, 6e-3),
               ("balance 30 cm meet right (cm)", ve["right"] * 100, 30.71, 6e-3)]
    checks.append(("drawn hammer balance point (cm)", hs["com_px"] * 100, 20.0, 2e-2))
    fails, out = 0, []
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
    cyc = [t0 + kk * P for kk in range(k0, k1 + 1)]
    ev["cycles"] = int(round(cycles))

    def lst(off_: float) -> str:
        return ", ".join(f"{st + off_:.3f}" for st in cyc if 0.0 <= st + off_ < D)

    hold = P - F - (sa + t_total)
    assert hold > 0.3, "the met state holds too briefly before the fade"
    tau0 = (0.0 - t0) % P
    st0 = {m: state_at(ev["runs"][m], tau0 - sa) for m in PANELS}
    print(f"schedule (video time, real speed): cycles of {P:g} s start at " + ", ".join(f"{st:.2f}" for st in cyc)
          + f" s (the first {abs(t0):.2f} s before the first frame); the fingers start {sa:g} s into each cycle at {lst(sa)} s; the "
          f"ruler's first swap at {lst(sa + rr['slips'][0]['t'])} s, its second at {lst(sa + rr['slips'][1]['t'])} s, its third at "
          f"{lst(sa + rr['slips'][2]['t'])} s; the hammer's first swap at {lst(sa + rh['slips'][0]['t'])} s, its second at "
          f"{lst(sa + rh['slips'][1]['t'])} s; both meetings {t_total:.3f} s after the start at {lst(sa + t_total)} s (the gold "
          f"balance marks and both event rows light); the met state holds {hold:.3f} s; the reset crossfade runs over the last "
          f"{F:g} s of each cycle (from {lst(P - F)} s; the readouts out over its first half and in over its second); on the first "
          f"frame the cycle is {tau0:.2f} s in ({tau0 - sa:+.3f} s after the start: the ruler's fingers {st0['ruler']['phase']} at "
          f"{st0['ruler']['left'] * 100:.1f} and {st0['ruler']['right'] * 100:.1f} cm, the hammer's {st0['hammer']['phase']} at "
          f"{st0['hammer']['left'] * 100:.1f} and {st0['hammer']['right'] * 100:.1f} cm); title until {man['title_until']:g} s; "
          f"payoff card from {man['payoff_t']:g} s; the title fades back in over the last {man['loop_fade']:g} s and the last "
          f"frame repeats the first (the scene is periodic: {D:g} s holds exactly {cycles:.0f} cycles)")
    # Text widths.
    font = os.environ["SEED_ZERO_FONT"]
    f24, f28, f34, f40, f56 = (ImageFont.truetype(font, n) for n in (24, 28, 34, 40, 56))
    widths = {"overlay@34": (f34, man["overlay"])}
    for j, line in enumerate(man["title"].split("|")):
        widths[f"title line {j + 1}@56"] = (f56, line)
    widths["legend@40"] = (f40, legend_text())
    widths["clock@28"] = (f28, clock_text(8.35))
    widths["clock rest@28"] = (f28, clock_text(-1.0))
    for m in PANELS:
        widths[f"label {m}@40"] = (f40, label_text(man, m))
        widths[f"event {m}@40"] = (f40, event_text(ev, m))
    widths["left finger@28"] = (f28, finger_text("left", 0.4921))
    widths["right finger@28"] = (f28, finger_text("right", 0.90))
    for ph, sl in ((REST, None), (SLIDE, "right"), (SLIDE, "left"), (MET, None)):
        widths[f"state {ph}{' ' + sl if sl else ''}@28"] = (f28, state_text(ph, sl))
    widths["slips@28"] = (f28, slips_text(15))
    widths["load@24"] = (f24, load_text(0.8235))
    widths["load full@24"] = (f24, load_text(1.0))
    for n in man["ruler_numbers_cm"]:
        widths[f"ruler number {n}@24"] = (f24, str(n))
    widths["balance@24"] = (f24, balance_text())
    widths["first swap@24"] = (f24, swap_text())
    for j, line in enumerate(payoff_lines(man, ev)):
        widths[f"payoff line {j + 1}@40"] = (f40, line)
    print("text widths (the on-screen strings verbatim): " + ", ".join(f"{kk} {f.getlength(s):.0f} px '{s}'" for kk, (f, s) in widths.items()))
    assert all(f.getlength(s) < 950 for f, s in widths.values()), "a text line is wider than 950 px"
    assert len(payoff_lines(man, ev)) <= 6, "the card has more than six lines"
    # Layout checks.
    left_w = max(max(f40.getlength(label_text(man, m)) for m in PANELS), f28.getlength(finger_text("left", 0.4921)),
                 max(f28.getlength(state_text(ph, sl)) for ph, sl in ((REST, None), (SLIDE, "right"), (SLIDE, "left"), (MET, None))))
    right_w = max(f28.getlength(finger_text("right", 0.90)), f28.getlength(slips_text(15)))
    col_l, col_r = ROW_X0 + left_w, ROW_X1 - right_w
    rows_bottom = FIX_DY + 16
    x0 = float(man["stick_x0_px"])
    x1 = x0 + L * ppm
    head_top = STICK_DY - HEAD_H
    ruler_top = STICK_DY - RULER_H
    bal_label_top = {"ruler": ruler_top - 15 - 12, "hammer": STICK_DY - HANDLE_H - 15 - 12}
    load_w = f24.getlength(load_text(1.0))
    # The load bars and labels at their extreme positions over both runs.
    bar_min, bar_max, lab_min, lab_max = 1e9, -1e9, 1e9, -1e9
    for m in PANELS:
        run = ev["runs"][m]
        tt = run["table"][0]
        for rt in np.concatenate((tt, np.linspace(0.0, run["t_total"], 2000))):
            st = state_at(run, rt)
            xl, xr = x0 + st["left"] * ppm, x0 + st["right"] * ppm
            bar_min = min(bar_min, xl - BAR_FULL * st["N_left"])
            bar_max = max(bar_max, xr + BAR_FULL * st["N_right"])
            l_end = max(xl, ROW_X0 + f24.getlength(load_text(st["N_left"])))
            r_start = min(xr, ROW_X1 - f24.getlength(load_text(st["N_right"])))
            lab_min = min(lab_min, l_end - f24.getlength(load_text(st["N_left"])))
            lab_max = max(lab_max, r_start + f24.getlength(load_text(st["N_right"])))
            assert r_start - l_end >= 8.0, "the two load labels meet"
    pad_l0, pad_r1 = x0 + left * ppm - 6, x0 + right * ppm + 6
    swap_x = x0 + rh["slips"][0]["right"] * ppm
    swap_label_x1 = swap_x + 12 + f24.getlength(swap_text())
    bal_x = {m: x0 + com[m] * ppm for m in PANELS}
    bal_label_x1 = {m: bal_x[m] + 14 + f24.getlength(balance_text()) for m in PANELS}
    ev_w = max(f40.getlength(event_text(ev, m)) for m in PANELS)
    print(f"row check: the left column ends at x {col_l:.0f} px, the right column starts at x {col_r:.0f} px; both end {rows_bottom} "
          f"px under the band top; the stick spans x {x0:.0f} to {x1:.0f} px with its underside {STICK_DY} px under the band top "
          f"(the ruler from {ruler_top} px, the hammer's handle from {STICK_DY - HANDLE_H} px, its head from {head_top} px over x "
          f"{x0:.0f} to {x0 + hs['head_px']:.0f} px); the gold balance marks at x {bal_x['ruler']:.0f} (ruler) and {bal_x['hammer']:.0f} "
          f"px (hammer) with their labels from {bal_label_top['ruler']:.0f} and {bal_label_top['hammer']:.0f} px under the band top to "
          f"x {bal_label_x1['ruler']:.0f} and {bal_label_x1['hammer']:.0f} px; the pads hang from {STICK_DY} to {STICK_DY + PAD_H} px "
          f"between x {pad_l0:.0f} and {pad_r1:.0f} px; the load bars at {BAR_DY} to {BAR_DY + BAR_H} px span x {bar_min:.0f} to "
          f"{bar_max:.0f} px at their widest; the load labels at {LOAD_DY - 12} to {LOAD_DY + 12} px span x {lab_min:.0f} to "
          f"{lab_max:.0f} px at their widest (each at most {load_w:.0f} px wide); the hammer's dashed first-swap mark at x "
          f"{swap_x:.0f} px from {STICK_DY + 6} to {SWAP_LINE_END} px with its label right of it to x {swap_label_x1:.0f} px at "
          f"{SWAP_LABEL_DY - 12} to {SWAP_LABEL_DY + 12} px (inside the pad zone, crossed only by the right finger's first "
          f"trail); the event row centred {EVENT_DY} px under the band top ({EVENT_DY - 20} to {EVENT_DY + 20}), widest {ev_w:.0f} px; each "
          f"band is {BAND_H} px tall (y {BAND_Y['ruler']} to {BAND_Y['ruler'] + BAND_H} and {BAND_Y['hammer']} to "
          f"{BAND_Y['hammer'] + BAND_H}); the caption band starts at y {int(man['caption_y'] * H)}; the title rows end at y "
          f"{252 + 28} and the overlay band ends at y 130")
    assert col_r - col_l > 40, "the columns meet"
    assert head_top > rows_bottom + 10 and bal_label_top["ruler"] > rows_bottom + 10, "the stick or the balance label meets the text rows"
    assert bal_label_x1["hammer"] > x0 + hs["head_px"] + 4 or bal_label_top["hammer"] > head_top, "the hammer's balance label meets the head"
    assert bal_x["hammer"] - 10 > x0 + hs["head_px"], "the hammer's balance mark meets the head"
    assert bar_min > ROW_X0 and bar_max < ROW_X1, "a load bar leaves the frame"
    assert lab_min >= ROW_X0 - 0.5 and lab_max <= ROW_X1 + 0.5, "a load label leaves the frame"
    assert STICK_DY + PAD_H < BAR_DY and BAR_DY + BAR_H < LOAD_DY - 12, "the pads, bars and labels overlap"
    assert SWAP_LINE_END < BAR_DY and SWAP_LABEL_DY + 12 < STICK_DY + PAD_H and swap_label_x1 < ROW_X1, "the first-swap mark misfits"
    assert LOAD_DY + 12 < EVENT_DY - 20, "the load labels meet the event row"
    assert EVENT_DY + 20 < BAND_H - 10, "the event row leaves the band"
    assert W / 2 - ev_w / 2 > 40 and W / 2 + ev_w / 2 < W - 40, "the event row leaves the frame"
    assert BAND_Y["hammer"] + BAND_H <= int(man["caption_y"] * H), "the bottom band reaches the caption band"
    assert PAYOFF_Y - 20 > int(man["caption_y"] * H) + 90, "the card meets the caption band"
    return ev


def legend_text() -> str:
    return "same fingers, same grip, real time"


def clock_text(r: float) -> str:
    return "fingers at rest" if r < 0.0 else f"{r:.3f} s since the fingers started"


def label_text(man: dict, m: str) -> str:
    return f"a {man['stick_m']:g} m ruler" if m == "ruler" else "a hammer, heavy end left"


def finger_text(side: str, x: float) -> str:
    return f"{side} finger: {x * 100:.1f} cm"


def state_text(ph: str, slider: str | None) -> str:
    if ph == REST:
        return "both at rest"
    if ph == MET:
        return "fingers together"
    return f"sliding: {slider} finger"


def slips_text(n: int) -> str:
    return f"slips: {n}"


def load_text(n: float) -> str:
    return f"{n * 100:.0f}% of the weight"


def balance_text() -> str:
    return "balance point"


def swap_text() -> str:
    return "first swap"


def event_text(ev: dict, m: str) -> str:
    c = ev["runs"][m]["centre"] * 100.0
    return f"ruler: they meet at {c:.0f} cm, the middle" if m == "ruler" else f"hammer: they meet {c:.0f} cm from the head"


def payoff_lines(man: dict, ev: dict) -> list[str]:
    rr, rh = ev["runs"]["ruler"], ev["runs"]["hammer"]
    text = man["payoff_text"].format(
        meet_r=rr["centre"] * 100.0, meet_h=rh["centre"] * 100.0, n_r=len(rr["slips"]), n_h=len(rh["slips"]),
        t_total=ev["t_total"], first_h=rh["slips"][0]["d"] * 100.0,
        n_r63=len(ev["variants"][("ruler", 0.6, 0.3)]["slips"]), n_h63=len(ev["variants"][("hammer", 0.6, 0.3)]["slips"]))
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
        self.font_tiny2x = ImageFont.truetype(font, 24 * SS)
        self.ppm = float(man["px_per_m"])
        self.P = man["cycle_s"]
        self.P_f = int(round(man["cycle_s"] * self.fps))
        self.c0_f = int(round(man["first_cycle_at"] * self.fps))
        self.sa, self.F = man["start_at"], man["reset_fade"]
        self.runs = ev["runs"]
        self.L = man["stick_m"]
        self.x0 = float(man["stick_x0_px"])
        self.x1 = self.x0 + self.L * self.ppm
        self.head_px = ev["hammer_shape"]["head_px"]
        self.swap_x = self.x0 + self.runs["hammer"]["slips"][0]["right"] * self.ppm
        self.bal_x = {m: self.x0 + man["balance_m"][m] * self.ppm for m in PANELS}

    def phase(self, f: int) -> tuple[int, float]:
        k, tau_f = divmod(f - self.c0_f, self.P_f)
        return k, tau_f / self.fps

    @staticmethod
    def L_(x: float, y: float) -> tuple[float, float]:
        """Layer (2x) pixel of a band-local point, rounded to 1e-4 px so equal states draw equal pixels."""
        return round(x * SS, 4), round(y * SS, 4)

    def px(self, x_m: float) -> float:
        return self.x0 + x_m * self.ppm

    def dashed(self, d: ImageDraw.ImageDraw, x: float, y0: float, y1: float, col, dash: float = 8.0, gap: float = 6.0,
               width: int = 2) -> None:
        s = y0
        while s < y1:
            e = min(y1, s + dash)
            a, b = self.L_(x, s), self.L_(x, e)
            d.line((*a, *b), fill=col, width=width * SS)
            s += dash + gap

    def draw_stick(self, d: ImageDraw.ImageDraw, m: str) -> None:
        x0, x1 = self.x0, self.x1
        if m == "ruler":
            top = STICK_DY - RULER_H
            p0, p1 = self.L_(x0, top), self.L_(x1, STICK_DY)
            d.rectangle((p0[0], p0[1], p1[0] - 1, p1[1] - 1), fill=WOOD, outline=WOOD_DARK, width=2 * SS)
            for k in range(0, 101, 10):
                tx = self.px(k / 100.0)
                tl = TICK_LEN_20 if k % 20 == 0 else TICK_LEN
                t0, t1 = self.L_(tx, top), self.L_(tx, top + tl)
                d.line((*t0, *t1), fill=INK, width=2 * SS)
            for n in self.man["ruler_numbers_cm"]:
                tx = self.px(n / 100.0)
                anchor, X = "mm", tx
                if n == 0:
                    anchor, X = "lm", x0 + 6
                elif n == 100:
                    anchor, X = "rm", x1 - 6
                d.text(self.L_(X, STICK_DY - 13), str(n), font=self.font_tiny2x, fill=INK, anchor=anchor)
        else:
            hx1 = x0 + self.head_px
            p0, p1 = self.L_(hx1, STICK_DY - HANDLE_H), self.L_(x1, STICK_DY)
            d.rectangle((p0[0], p0[1], p1[0] - 1, p1[1] - 1), fill=WOOD, outline=WOOD_DARK, width=2 * SS)
            q0, q1 = self.L_(x0, STICK_DY - HEAD_H), self.L_(hx1, STICK_DY)
            d.rectangle((q0[0], q0[1], q1[0] - 1, q1[1] - 1), fill=STEEL, outline=STEEL_DARK, width=2 * SS)
            # The dashed first-swap mark (the right finger stops here first).
            self.dashed(d, self.swap_x, STICK_DY + 6, SWAP_LINE_END, blend(GOLD, 0.6))

    def draw_balance(self, d: ImageDraw.ImageDraw, m: str, a: float) -> None:
        if a <= 0.0:
            return
        top = STICK_DY - (RULER_H if m == "ruler" else HANDLE_H)
        bx = self.bal_x[m]
        col = blend(GOLD, a)
        p0, p1, p2 = self.L_(bx, top - 2), self.L_(bx - 9, top - 21), self.L_(bx + 9, top - 21)
        d.polygon([p0, p1, p2], fill=col)

    def draw_fingers(self, d: ImageDraw.ImageDraw, st: dict) -> None:
        xl, xr = self.px(st["left"]), self.px(st["right"])
        # The slider's trail: a translucent streak from the slip's start to the pad.
        if st["slider"] is not None and st["trail_from"] is not None:
            xs = self.px(st["trail_from"])
            xc = xl if st["slider"] == "left" else xr
            col = blend(COLOUR[st["slider"]], 0.22)
            a, b = self.L_(min(xs, xc), STICK_DY + 8), self.L_(max(xs, xc), STICK_DY + PAD_H - 10)
            if b[0] - a[0] > 1:
                d.rectangle((a[0], a[1], b[0], b[1]), fill=col)
        for side, x in (("left", xl), ("right", xr)):
            col = COLOUR[side]
            if st["phase"] == SLIDE:
                bright = st["slider"] == side
                fill = col if bright else blend(col, 0.45)
            else:
                bright = False
                fill = col if st["phase"] == MET else blend(col, 0.75)
            p0, p1 = self.L_(x - 6, STICK_DY), self.L_(x + 6, STICK_DY + PAD_H)
            d.rounded_rectangle((p0[0], p0[1], p1[0] - 1, p1[1] - 1), radius=6 * SS, fill=fill,
                                outline=WHITE if bright else None, width=2 * SS if bright else 0)
        # The load bars: the left finger's grows leftward from its pad, the right finger's rightward.
        for side, x, n, sgn in (("left", xl, st["N_left"], -1), ("right", xr, st["N_right"], 1)):
            e = x + sgn * BAR_FULL * n
            a, b = self.L_(min(x, e), BAR_DY), self.L_(max(x, e), BAR_DY + BAR_H)
            dim = st["phase"] == SLIDE and st["slider"] != side
            d.rectangle((a[0], a[1], b[0], b[1]), fill=blend(COLOUR[side], 0.5 if dim else 0.9))

    def scene(self, m: str, tau: float) -> tuple[Image.Image, dict]:
        """The band layer of panel m at tau seconds into a cycle (the resting setup before the start)."""
        layer = Image.new("RGB", (W * SS, BAND_H * SS), BG)
        d = ImageDraw.Draw(layer)
        rt = tau - self.sa
        st = state_at(self.runs[m], rt)
        st["tv"], st["rt"] = rt, rt
        self.draw_stick(d, m)
        st["bal_alpha"] = 0.0 if st["phase"] != MET else min(1.0, (rt - self.runs[m]["t_total"]) / 0.3)
        self.draw_balance(d, m, st["bal_alpha"])
        self.draw_fingers(d, st)
        return layer, st

    def draw_panel(self, m: str, f: int) -> tuple[Image.Image, dict]:
        k, tau = self.phase(f)
        P, F = self.P, self.F
        layer, st = self.scene(m, tau)
        st["alpha"], st["k"] = 1.0, k
        if tau >= P - F:
            # Crossfade to the next cycle's resting setup (the sticks are drawn the same in both, so they never blink).
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
        f24 = self.font_tiny
        for m, st in states.items():
            y0 = BAND_Y[m]
            a = st["alpha"]
            d.text((ROW_X0, y0 + LABEL_DY), label_text(man, m), font=self.font, fill=BAND_COLOUR[m], anchor="lm")
            d.text((ROW_X0, y0 + SUB_DY), finger_text("left", st["left"]), font=self.font_small, fill=blend(TEAL, a), anchor="lm")
            d.text((ROW_X0, y0 + FIX_DY), state_text(st["phase"], st["slider"]), font=self.font_small,
                   fill=blend(GOLD if st["phase"] == MET else MUTED, a), anchor="lm")
            d.text((ROW_X1, y0 + SUB_DY), finger_text("right", st["right"]), font=self.font_small, fill=blend(CORAL, a), anchor="rm")
            d.text((ROW_X1, y0 + FIX_DY), slips_text(st["slips"]), font=self.font_small, fill=blend(MUTED, a), anchor="rm")
            # The load labels under the bars, clamped inside the frame.
            xl, xr = self.px(st["left"]), self.px(st["right"])
            tl, tr = load_text(st["N_left"]), load_text(st["N_right"])
            l_end = max(xl, ROW_X0 + f24.getlength(tl))
            r_start = min(xr, ROW_X1 - f24.getlength(tr))
            dim_l = st["phase"] == SLIDE and st["slider"] != "left"
            dim_r = st["phase"] == SLIDE and st["slider"] != "right"
            d.text((l_end, y0 + LOAD_DY), tl, font=f24, fill=blend(TEAL, a * (0.55 if dim_l else 1.0)), anchor="rm")
            d.text((r_start, y0 + LOAD_DY), tr, font=f24, fill=blend(CORAL, a * (0.55 if dim_r else 1.0)), anchor="lm")
            if m == "hammer":
                d.text((self.swap_x + 12, y0 + SWAP_LABEL_DY), swap_text(), font=f24, fill=blend(GOLD, 0.6), anchor="lm")
            if st["bal_alpha"] > 0.0:
                top = STICK_DY - (RULER_H if m == "ruler" else HANDLE_H)
                d.text((self.bal_x[m] + 14, y0 + top - 15), balance_text(), font=f24, fill=blend(GOLD, st["bal_alpha"] * a), anchor="lm")
            if st["phase"] == MET:
                d.text((W / 2, y0 + EVENT_DY), event_text(ev, m), font=self.font, fill=blend(GOLD, a), anchor="mm")
        if hud_alpha > 0.02:
            d.text((W / 2, LEGEND_Y), legend_text(), font=self.font, fill=blend(TEXT, hud_alpha), anchor="mm")
            rt = states["ruler"]["rt"]
            d.text((W / 2, CLOCK_Y), clock_text(min(rt, self.ev["t_total"])), font=self.font_small,
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
            # The geometry runs on; the legend, clock and card fade out over the first half of the loop
            # fade and the title fades in over the second half, so the two never overlap.
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
    man = json.loads((ROOT / "projects/fingers/manifest.json").read_text())
    ev = measure(man)
    if "--measure-only" in sys.argv:
        return
    if "--frames" in sys.argv:
        times = [float(v) for v in sys.argv[sys.argv.index("--frames") + 1].split(",")]
        r = Renderer(man, ev)
        (ROOT / "media/fingers").mkdir(parents=True, exist_ok=True)
        for tv in times:
            Image.fromarray(r.frame_at(int(round(tv * man["fps"])))).save(ROOT / f"media/fingers/smoke-{tv}.png")
        print("smoke frames: " + ", ".join(f"{tv}" for tv in times))
        return
    Renderer(man, ev).render(ROOT / "media/fingers/footage.mp4")


if __name__ == "__main__":
    main()
