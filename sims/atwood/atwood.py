#!/usr/bin/env python3
"""Drop 1.1 kg beside the same 1.1 kg on a pulley against 1.0 kg: which lands first?

One scene, side view, both weights on one height scale. On the left a
weight of mass m1 is held h = 1 m above a floor pad and dropped; it falls
freely at g with no air drag and the pad stops it (no bounce). On the
right the same mass m1 hangs on a string over a pulley against a lighter
weight m2; the heavy weight starts level with the dropped one, h above
its own pad, and the light weight starts on its pad on the floor; both
are held and let go at the same instant as the drop. The string is
massless and inextensible and the pulley massless and frictionless, so
the two weights share one speed and the pair obeys

    (m1 + m2) a = (m1 - m2) g,    T = m2 (g + a) = m1 (g - a) = 2 m1 m2 g / (m1 + m2)

a = g / 21 for 1.1 kg against 1.0 kg: the 0.1 kg of net weight must move
all 2.1 kg, so the pair speeds up 21 times more slowly than a free fall
and lands sqrt(21) times later. The heavy weight reaches its pad after
sqrt(2 h / a) at sqrt(2 a h) and the pad stops it; the light weight is
then h up, level with the release line, the string goes slack and both
rest until the reset. The free weight lands at sqrt(2 h / g). Both drops
are integrated by classical RK4 at steps_per_second (the accelerations
are constant, so the four stages reduce to the exact quadratic update)
with compensated (Kahan) summation of the state, the landing located by
bisection inside the step, a half-step rerun as a check, against the
closed forms; the energy balance of the pair, (m1 - m2) g x against
(m1 + m2) v^2 / 2, is tracked every step. The drawing follows the RK4
tables. Shown at 1/slow speed on a cycle_s cycle with both let go
release_at seconds into the cycle; the weights are reset by a crossfade
over the last reset_fade seconds of the cycle; the cycle divides the
scene length, so the scene is exactly periodic and the last frame
equals the first. Deterministic, no seed.

Measured and printed: the model constants, the acceleration and g / a,
the tension three ways, the free drop and the Atwood drop by closed form
and by RK4 (landing times, speeds, the ratio against sqrt(21), the
energy residuals, the half-step agreement), the heavy weight's drop when
the free weight lands, the wrong guess g / 11, every check in the brief
with the sim's value beside it, the position and speed tables at
table_step_s for both, the pulley-disc and mass-ratio variants for the
description, the pulley drawing numbers, the schedule in video time, the
on-screen text widths and the layout clearances.

usage: atwood.py [--measure-only] [--frames t1,t2,...]
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
AXLE = (24, 26, 32)
TEAL_RIM = (150, 226, 200)
CORAL_RIM = (246, 160, 150)
STEEL_RIM = (200, 208, 220)

# Layout: overlay at y 96..130 (captions.py), two title rows at y 190/252 for
# the first seconds, then the legend at y 236 and the shared clock at y 290;
# one scene band y 330..1430 drawn at 2x in its own layer: two readout rows
# at y 370/404 from x 40 (the dropped weight, then the pulley pair; they end
# left of the pulley), the pulley on a short ceiling bracket at the top
# centre-right with its two vertical string legs at heavy_x and light_x,
# the release line at release_y across both columns with a small hand mark
# on each 1.1 kg block, the 1 m height scale on the left at scale_x, the
# free block at free_x, the Atwood blocks at heavy_x and light_x, the floor
# pads 1 m below the release line on the floor slab, a gold tick beside the
# heavy block at its depth when the free weight lands, the gold event rows
# at y 1326/1374 under the floor; captions at caption_y 0.75 (y 1440..1530);
# the six-line card from y 1572 at a 48 px pitch.
LEGEND_Y, CLOCK_Y = 236, 290
TITLE_Y0, TITLE_PITCH = 190, 62
SS = 2
PAYOFF_Y, PAYOFF_PITCH = 1572.0, 48
BAND_Y0, BAND_Y1 = 330, 1430
READ_Y = (370, 404)
ROW_X0 = 40
EVENT_Y = (1326, 1374)
HAND_W, HAND_PAD, HAND_STEM, HAND_DX = 28, 8, 30, -30
PAD_EXTRA = 24          # the pad is this much wider than the block
FLOOR_PX = 24
BRACKET_W, BRACKET_H, STEM_W = 90, 8, 10
HUB_R = 10
TICK_DX0, TICK_DX1, TICK_LABEL_DX = -90, -70, -96   # the gold tick sits left of the heavy block
HELD, MOVING, LANDED = "held", "moving", "landed"

# The brief's numbers, as checks the sim must print beside its own values.
BRIEF = {
    "a (m/s^2)": (0.4670, 4), "g / a": (21.00, 2), "t heavy (s)": (2.0695, 4), "t free (s)": (0.4516, 4),
    "ratio": (4.5826, 4), "sqrt(21)": (4.5826, 4), "naive a = g / 11 (m/s^2)": (0.8915, 4), "naive t (s)": (1.4978, 4),
    "heavy down when the free lands (cm)": (4.76, 2), "v heavy at the pad (m/s)": (0.9664, 4),
    "v free at the pad (m/s)": (4.4288, 4), "tension (N)": (10.274, 3), "T / heavy weight": (0.9524, 4),
    "T / light weight": (1.0476, 4), "heavy weight (N)": (10.788, 3), "light weight (N)": (9.807, 3),
    "0.2 kg disc a (m/s^2)": (0.4458, 4), "0.2 kg disc t (s)": (2.1182, 4), "0.5 kg disc a (m/s^2)": (0.4173, 4),
    "0.5 kg disc t (s)": (2.1892, 4), "1.2 kg: g / a": (11.0, 1), "1.2 kg t (s)": (1.4978, 4), "1.5 kg: g / a": (5.0, 1),
    "1.5 kg t (s)": (1.0098, 4), "2.0 kg: g / a": (3.0, 1), "2.0 kg t (s)": (0.7822, 4),
}


def blend(col, a: float, base=BG) -> tuple:
    a = max(0.0, min(1.0, a))
    return tuple(int(round(c * a + b * (1 - a))) for c, b in zip(col, base))


# --- measurement --------------------------------------------------------------
def atwood_accel(g: float, m1: float, m2: float, disc_kg: float = 0.0) -> float:
    """a = (m1 - m2) g / (m1 + m2 + I / r^2); I / r^2 = disc_kg / 2 for a uniform disc pulley (0 when massless)."""
    return (m1 - m2) * g / (m1 + m2 + 0.5 * disc_kg)


def tension(g: float, m1: float, m2: float) -> float:
    return 2.0 * m1 * m2 * g / (m1 + m2)


def rk4_drop(a: float, h: float, dt: float, energy=None) -> dict:
    """Integrate x'' = a from rest by classical RK4 at dt (the acceleration is constant, so the four
    stages reduce to the exact quadratic update x += v dt + a dt^2 / 2, v += a dt) with compensated
    (Kahan) summation of the state; the landing x = h is located by bisection inside the step.
    energy(x, v) is the energy residual, tracked every step. Returns the table and the landing."""
    def incr(v: float, hh: float) -> tuple[float, float]:
        k1x, k1v = v, a
        k2x, k2v = v + 0.5 * hh * a, a
        k3x, k3v = v + 0.5 * hh * a, a
        k4x, k4v = v + hh * a, a
        return hh * (k1x + 2.0 * k2x + 2.0 * k3x + k4x) / 6.0, hh * (k1v + 2.0 * k2v + 2.0 * k3v + k4v) / 6.0

    def step(x: float, v: float, hh: float) -> tuple[float, float]:
        dx, dv = incr(v, hh)
        return x + dx, v + dv

    ts, xs, vs = [0.0], [0.0], [0.0]
    x, v, n = 0.0, 0.0, 0
    cx = cv = 0.0
    resid = 0.0
    while True:
        xn, _ = step(x, v, dt)
        if xn >= h:
            lo, hi = 0.0, dt
            for _ in range(80):
                mid = 0.5 * (lo + hi)
                if step(x, v, mid)[0] < h:
                    lo = mid
                else:
                    hi = mid
            xb, vb = step(x, v, hi)
            t_land = n * dt + hi
            ts.append(t_land); xs.append(xb); vs.append(vb)
            if energy is not None:
                resid = max(resid, abs(energy(xb, vb)))
            break
        dx, dv = incr(v, dt)
        y = dx - cx; tmp = x + y; cx = (tmp - x) - y; x = tmp
        y = dv - cv; tmp = v + y; cv = (tmp - v) - y; v = tmp
        n += 1
        ts.append(n * dt); xs.append(x); vs.append(v)
        if energy is not None:
            resid = max(resid, abs(energy(x, v)))
    return {"t": np.array(ts), "x": np.array(xs), "v": np.array(vs), "t_land": t_land, "v_land": vb, "x_land": xb,
            "steps": n + 1, "energy_resid": resid}


def drop_state(run: dict, rt: float, h: float) -> dict:
    """(x, v, phase) of a weight rt real seconds after the release: x is its drop below the release line."""
    if rt < 0.0:
        return {"x": 0.0, "v": 0.0, "phase": HELD}
    if rt >= run["t_land"]:
        return {"x": h, "v": 0.0, "phase": LANDED}
    return {"x": float(np.interp(rt, run["t"], run["x"])), "v": float(np.interp(rt, run["t"], run["v"])), "phase": MOVING}


def measure(man: dict) -> dict:
    g, h, m1, m2 = man["g"], man["drop_m"], man["heavy_kg"], man["light_kg"]
    dt = 1.0 / man["steps_per_second"]
    S, P, D, fps, F, pa = man["slow"], man["cycle_s"], man["scene_duration"], man["fps"], man["reset_fade"], man["release_at"]
    cycles = D / P
    assert abs(cycles - round(cycles)) < 1e-9, "the cycle must divide the scene length"
    for key in ("cycle_s", "release_at", "first_cycle_at", "reset_fade"):
        assert abs(man[key] * fps - round(man[key] * fps)) < 1e-9, f"{key} must be a whole number of frames"
    ppm = man["px_per_m"]
    bw, bh = man["block_w_px"], man["block_h_px"]
    r_pul_px = (man["light_x"] - man["heavy_x"]) / 2.0
    r_pul = r_pul_px / ppm
    a = atwood_accel(g, m1, m2)
    T = tension(g, m1, m2)
    W1, W2 = m1 * g, m2 * g
    k = (m1 + m2) / (m1 - m2)
    print(f"setup: one scene, side view, both weights on one height scale: on the left a {m1:g} kg weight is held {h:g} m "
          f"above a floor pad and dropped; it falls freely at g = {g:g} m/s^2 with no air drag and the pad stops it, no "
          f"bounce; on the right the same {m1:g} kg hangs on a string over a pulley against {m2:g} kg; the heavy weight "
          f"starts level with the dropped one, {h:.2f} m above its own pad, and the light weight starts on its pad on the "
          f"floor; both are held and let go at the same instant as the drop; the string is massless and inextensible and "
          f"the pulley massless and frictionless (a pulley with mass is a description-only variant), so the two weights "
          f"share one speed; the pad stops the heavy weight, the light weight is then {h:g} m up, level with the release "
          f"line, the string goes slack and both rest until the reset; both drops integrated by RK4 at "
          f"{man['steps_per_second']} steps per second (dt = {dt:.0e} s) with compensated (Kahan) summation of the state, "
          f"the landing located by bisection inside the step, a half-step rerun as a check, against the closed forms; "
          f"shown at 1/{S:g} speed on a {P:g} s cycle ({P * fps:.0f} frames) with both let go {pa:g} s into the cycle, "
          f"{cycles:.0f} cycles in {D:g} s; drawn at {ppm:g} px per metre (the blocks {bw} x {bh} px, the pulley {r_pul_px:.0f} "
          f"px in radius = {r_pul * 100:.2f} cm at this scale, its size does not enter the motion); deterministic, no seed")
    print(f"model: (m1 + m2) a = (m1 - m2) g gives a = {m1 - m2:.4f} kg x g / {m1 + m2:.4f} kg = {a:.5f} m/s^2 = {a:.4f} m/s^2 = "
          f"{a:.3f} m/s^2 = g / {g / a:.4f} = g / {g / a:.2f} (exactly g / 21: (m1 + m2) / (m1 - m2) = {k:.4f}, diff "
          f"{k - 21:+.1e}); the tension T = m2 (g + a) = {m2 * (g + a):.4f} N = m1 (g - a) = {m1 * (g - a):.4f} N = "
          f"2 m1 m2 g / (m1 + m2) = {T:.4f} N = {T:.3f} N = {T:.1f} N, {T / W1:.4f} of the heavy weight's {W1:.3f} N = "
          f"{W1:.1f} N and {T / W2:.4f} of the light weight's {W2:.3f} N; the net weight on the pair is (m1 - m2) g = "
          f"{(m1 - m2) * g:.4f} N moving {m1 + m2:.1f} kg; a is the same for any height")
    # The free weight.
    t_free_c = math.sqrt(2.0 * h / g)
    v_free_c = g * t_free_c
    free = rk4_drop(g, h, dt, energy=lambda x, v: m1 * g * x - 0.5 * m1 * v * v)
    free_half = rk4_drop(g, h, 0.5 * dt, energy=lambda x, v: m1 * g * x - 0.5 * m1 * v * v)
    print(f"dropped weight (RK4, {free['steps']} steps): lands at {free['t_land']:.6f} s = {free['t_land']:.4f} s = "
          f"{free['t_land']:.2f} s (closed form sqrt(2 h / g) = {t_free_c:.6f} s, diff {free['t_land'] - t_free_c:+.1e} s; "
          f"under half a second: {free['t_land']:.4f} < 0.5) at {free['v_land']:.4f} m/s = {free['v_land']:.2f} m/s "
          f"(closed form g t = {v_free_c:.4f} m/s, diff {free['v_land'] - v_free_c:+.1e}); energy balance m g x against "
          f"m v^2 / 2 within {free['energy_resid']:.1e} J; half-step rerun (dt = {0.5 * dt:.0e} s): {free_half['t_land']:.9f} s "
          f"({free_half['t_land'] - free['t_land']:+.1e} s); the pad stops it")
    assert abs(free["t_land"] - t_free_c) < 1e-9 and abs(free["v_land"] - v_free_c) < 1e-9
    assert abs(free_half["t_land"] - free["t_land"]) < 1e-9 and free["energy_resid"] < 1e-12
    # The Atwood pair.
    t_atw_c = math.sqrt(2.0 * h / a)
    v_atw_c = math.sqrt(2.0 * a * h)
    pair_energy = lambda x, v: (m1 - m2) * g * x - 0.5 * (m1 + m2) * v * v   # noqa: E731
    atw = rk4_drop(a, h, dt, energy=pair_energy)
    atw_half = rk4_drop(a, h, 0.5 * dt, energy=pair_energy)
    ratio = atw["t_land"] / free["t_land"]
    x_at_free = float(np.interp(free["t_land"], atw["t"], atw["x"]))
    v_at_free = float(np.interp(free["t_land"], atw["t"], atw["v"]))
    print(f"on the pulley (RK4, {atw['steps']} steps): the heavy weight lands at {atw['t_land']:.6f} s = {atw['t_land']:.4f} s = "
          f"{atw['t_land']:.3f} s = {atw['t_land']:.2f} s (closed form sqrt(2 h / a) = {t_atw_c:.6f} s, diff "
          f"{atw['t_land'] - t_atw_c:+.1e} s; about two seconds), {atw['t_land'] - free['t_land']:.4f} s after the dropped "
          f"weight, {ratio:.4f} times later = {ratio:.2f} times = {ratio:.1f} times (exactly sqrt(21) = {math.sqrt(21):.4f}, "
          f"diff {ratio - math.sqrt(21):+.1e}), moving at {atw['v_land']:.4f} m/s = {atw['v_land']:.3f} m/s = "
          f"{atw['v_land']:.2f} m/s (closed form sqrt(2 a h) = {v_atw_c:.4f} m/s, diff {atw['v_land'] - v_atw_c:+.1e}) "
          f"against the dropped weight's {free['v_land']:.4f} m/s; when the dropped weight lands at {free['t_land']:.4f} s "
          f"the heavy weight has dropped {x_at_free:.5f} m = {x_at_free * 100:.3f} cm = {x_at_free * 100:.2f} cm = "
          f"{x_at_free * 100:.1f} cm (closed form a t^2 / 2 = h / 21 = {h / 21 * 100:.3f} cm, diff "
          f"{x_at_free - h / 21:+.1e} m) at {v_at_free:.4f} m/s = {v_at_free:.2f} m/s, and the light weight has risen the "
          f"same {x_at_free * 100:.1f} cm; when the heavy weight lands the dropped one has been down for "
          f"{atw['t_land'] - free['t_land']:.4f} s = {atw['t_land'] - free['t_land']:.2f} s; the light weight is then "
          f"{h:g} m up, level with the release line, with zero speed, and the string goes slack (tension 0); energy balance "
          f"(m1 - m2) g x against (m1 + m2) v^2 / 2 within {atw['energy_resid']:.1e} J over the drop; half-step rerun "
          f"(dt = {0.5 * dt:.0e} s): lands at {atw_half['t_land']:.9f} s ({atw_half['t_land'] - atw['t_land']:+.1e} s) at "
          f"{atw_half['v_land']:.9f} m/s ({atw_half['v_land'] - atw['v_land']:+.1e} m/s)")
    assert abs(atw["t_land"] - t_atw_c) < 1e-9 and abs(atw["v_land"] - v_atw_c) < 1e-9
    assert abs(atw_half["t_land"] - atw["t_land"]) < 1e-9 and atw["energy_resid"] < 1e-12
    assert abs(ratio - math.sqrt(21)) < 1e-9 and abs(k - 21) < 1e-9
    # The wrong guess.
    nd = man["naive_divisor"]
    a_naive = g / nd
    t_naive = math.sqrt(2.0 * h / a_naive)
    print(f"wrong guess: the weight difference alone, {m1 - m2:.1f} kg of {m1:g} kg, suggests a = g / {nd:g} = {a_naive:.4f} m/s^2, "
          f"which would land the heavy weight at {t_naive:.4f} s = {t_naive:.2f} s, {t_naive / free['t_land']:.2f} times the "
          f"free drop; the true a = g / 21 because the {m1 - m2:.1f} kg of net weight must get all {m1 + m2:.1f} kg moving, "
          f"{(m1 + m2) / (m1 - m2) / nd:.4f} times more mass than the difference alone counts")
    # Tables.
    rows = []
    tt = 0.0
    while tt <= atw["t_land"] + man["table_step_s"] + 1e-9:
        fs, hs = drop_state(free, tt, h), drop_state(atw, tt, h)
        f_txt = (f"dropped {fs['x'] * 100:.1f} cm, {fs['v']:.2f} m/s" if fs["phase"] == MOVING
                 else f"dropped on the pad ({h * 100:.0f} cm)")
        h_txt = (f"pulley side {hs['x'] * 100:.1f} cm down, {hs['v']:.3f} m/s, light weight {hs['x'] * 100:.1f} cm up"
                 if hs["phase"] == MOVING else f"pulley side on the pad ({h * 100:.0f} cm), light weight {h * 100:.0f} cm up")
        rows.append(f"{tt:.2f} s: {f_txt}; {h_txt}")
        tt += man["table_step_s"]
    print("tables (RK4 tables, real time since the release): " + "; ".join(rows))
    # Variants for the description.
    descr = []
    var: dict = {}
    for disc in man["description_pulley_disc_kg"]:
        a2 = atwood_accel(g, m1, m2, disc)
        r2 = rk4_drop(a2, h, dt)
        t2 = math.sqrt(2.0 * h / a2)
        var[f"disc {disc:g}"] = (a2, r2["t_land"])
        descr.append(f"a {disc:g} kg uniform pulley disc (I / r^2 = {0.5 * disc:g} kg) with the same weights: a = "
                     f"{(m1 - m2) * g:.4f} N / {m1 + m2 + 0.5 * disc:.2f} kg = {a2:.4f} m/s^2 = g / {g / a2:.2f}, lands at "
                     f"{r2['t_land']:.4f} s = {r2['t_land']:.2f} s (closed form {t2:.4f} s, diff {r2['t_land'] - t2:+.1e} s), "
                     f"{r2['t_land'] / free['t_land']:.2f} times the free drop")
        assert abs(r2["t_land"] - t2) < 1e-9
    for mb in man["description_heavy_kg"]:
        a3 = atwood_accel(g, mb, m2)
        r3 = rk4_drop(a3, h, dt)
        t3 = math.sqrt(2.0 * h / a3)
        var[f"heavy {mb:g}"] = (a3, r3["t_land"])
        descr.append(f"{mb:g} kg against {m2:g} kg (massless pulley): a = g / {g / a3:.2f} = {a3:.4f} m/s^2, lands at "
                     f"{r3['t_land']:.4f} s = {r3['t_land']:.2f} s (closed form {t3:.4f} s, diff {r3['t_land'] - t3:+.1e} s), "
                     f"{r3['t_land'] / free['t_land']:.2f} times the free drop, the string holding {tension(g, mb, m2):.3f} N")
        assert abs(r3["t_land"] - t3) < 1e-9
    print("for the description: " + "; ".join(descr))
    # The brief's checks beside the sim's values.
    sim = {
        "a (m/s^2)": a, "g / a": g / a, "t heavy (s)": atw["t_land"], "t free (s)": free["t_land"], "ratio": ratio,
        "sqrt(21)": math.sqrt(21), "naive a = g / 11 (m/s^2)": a_naive, "naive t (s)": t_naive,
        "heavy down when the free lands (cm)": x_at_free * 100, "v heavy at the pad (m/s)": atw["v_land"],
        "v free at the pad (m/s)": free["v_land"], "tension (N)": T, "T / heavy weight": T / W1, "T / light weight": T / W2,
        "heavy weight (N)": W1, "light weight (N)": W2,
        "0.2 kg disc a (m/s^2)": var["disc 0.2"][0], "0.2 kg disc t (s)": var["disc 0.2"][1],
        "0.5 kg disc a (m/s^2)": var["disc 0.5"][0], "0.5 kg disc t (s)": var["disc 0.5"][1],
        "1.2 kg: g / a": g / var["heavy 1.2"][0], "1.2 kg t (s)": var["heavy 1.2"][1],
        "1.5 kg: g / a": g / var["heavy 1.5"][0], "1.5 kg t (s)": var["heavy 1.5"][1],
        "2.0 kg: g / a": g / var["heavy 2"][0], "2.0 kg t (s)": var["heavy 2"][1],
    }
    checks = []
    n_fail = 0
    for name, (want, dec) in BRIEF.items():
        got = sim[name]
        ok = f"{got:.{dec}f}" == f"{want:.{dec}f}"
        n_fail += 0 if ok else 1
        checks.append(f"{name}: brief {want:.{dec}f}, sim {got:.{dec}f} ({'ok' if ok else 'DIFFERS'})")
    print(f"brief checks ({len(BRIEF) - n_fail} of {len(BRIEF)} agree at the brief's precision): " + "; ".join(checks))
    ev: dict = {"free": free, "atw": atw, "a": a, "T": T, "W1": W1, "W2": W2, "ratio": ratio, "x_at_free": x_at_free,
                "v_at_free": v_at_free, "t_naive": t_naive, "a_naive": a_naive, "var": var, "r_pul": r_pul,
                "r_pul_px": r_pul_px, "net_kg": m1 - m2, "tot_kg": m1 + m2}
    # The pulley drawing.
    turns = h / (2.0 * math.pi * r_pul)
    print(f"drawing: the string turns the pulley x / r = {h / r_pul:.3f} rad = {turns:.3f} turns over the {h:g} m drop "
          f"({turns / (S * atw['t_land']):.3f} turns per video second on average, {math.degrees(atw['v_land'] / r_pul / (S * fps)):.2f} "
          f"degrees per frame at the end), counterclockwise as the heavy side goes down; a spoke mark on the disc shows it; "
          f"the string is drawn as the two vertical legs and the arc over the top of the disc; the gold "
          f"{x_at_free * 100:.1f} cm tick appears left of the heavy block at its depth when the dropped weight lands")
    # The schedule in video time.
    t0 = man["first_cycle_at"]
    k0 = math.ceil((0.0 - t0) / P - 1e-9) - 1
    k1 = math.floor((D - t0) / P - 1e-9)
    starts = [t0 + kk * P for kk in range(k0, k1 + 1)]
    ev["cycles"] = int(round(cycles))

    def lst(off_: float) -> str:
        return ", ".join(f"{st + off_:.2f}" for st in starts if 0.0 <= st + off_ < D)

    vt = lambda real: pa + real * S   # noqa: E731  video time after the cycle start
    assert vt(atw["t_land"]) < P - F - 1.0, "the heavy weight must land at least 1 s before the reset fade"
    tau0 = (0.0 - t0) % P
    r0 = (tau0 - pa) / S
    fs0, hs0 = drop_state(free, r0, h), drop_state(atw, r0, h)
    print(f"schedule (video time, 1/{S:g} speed): cycles of {P:g} s start at " + ", ".join(f"{st:.2f}" for st in starts)
          + f" s (the first {-t0:.2f} s before the first frame); both let go {pa:g} s into each cycle at {lst(pa)} s; the "
          f"dropped weight lands {S * free['t_land']:.3f} s after the release at {lst(vt(free['t_land']))} s (the first "
          f"event row lights, the gold {x_at_free * 100:.1f} cm tick appears beside the heavy block; it rests on its pad "
          f"until the fade); the heavy weight on the pulley lands {S * atw['t_land']:.3f} s after the release at "
          f"{lst(vt(atw['t_land']))} s ({vt(atw['t_land']):.2f} s into the cycle; the second event row lights; the light "
          f"weight is then level with the release line and both rest); the heavy weight is "
          f"{float(np.interp(1.0 / S, atw['t'], atw['x'])) * 100:.1f} cm down 1 s of video after the release, "
          f"{float(np.interp(2.0 / S, atw['t'], atw['x'])) * 100:.1f} cm after 2 s and "
          f"{float(np.interp(4.0 / S, atw['t'], atw['x'])) * 100:.1f} cm after 4 s; the reset crossfade runs over the last "
          f"{F:g} s of each cycle (from {lst(P - F)} s; the readouts out over its first half and in over its second; the "
          f"blocks blend back to the release line and the light weight to its pad); on the first frame the cycle is "
          f"{tau0:.2f} s in ({r0:.3f} s real: the dropped weight {fs0['phase']}, the pulley pair {hs0['phase']}); title until "
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
    widths["clock@28"] = (f28, clock_text(2.0695))
    widths["clock held@28"] = (f28, clock_text(-1.0))
    row_cases = {"held": {"x": 0.0, "v": 0.0, "phase": HELD}, "moving": {"x": h, "v": 4.4288, "phase": MOVING},
                 "landed": {"x": h, "v": 0.0, "phase": LANDED}}
    for which in ("free", "atw"):
        for case, st in row_cases.items():
            widths[f"row {which} {case}@28"] = (f28, "".join(row_text(which, st)))
    widths["block heavy@28"] = (f28, block_label(m1))
    widths["block light@28"] = (f28, block_label(m2))
    widths["scale top@28"] = (f28, "0")
    widths["scale bottom@28"] = (f28, scale_text(h))
    widths["tick@24"] = (f24, tick_text(ev))
    for j in range(2):
        widths[f"event {j + 1}@40"] = (f40, event_text(ev, j))
    for j, line in enumerate(payoff_lines(man, ev)):
        widths[f"payoff line {j + 1}@40"] = (f40, line)
    print("text widths (the on-screen strings verbatim): " + ", ".join(f"{kk} {f.getlength(s):.0f} px '{s}'"
                                                                           for kk, (f, s) in widths.items()))
    assert all(f.getlength(s) < 950 for f, s in widths.values()), "a text line is wider than 950 px"
    assert len(payoff_lines(man, ev)) <= 6, "the card has more than six lines"
    assert f28.getlength(block_label(m1)) < bw - 16, "the block label does not fit in the block"
    # Layout checks.
    ry = float(man["release_y"])
    pad_y = ry + h * ppm
    fx, hx, lx, sx = (float(man[kk]) for kk in ("free_x", "heavy_x", "light_x", "scale_x"))
    py = float(man["pulley_y"])
    rows_right = ROW_X0 + max(f28.getlength(s) for f, s in widths.values() if f is f28 and s.startswith(("dropped", "on the")))
    rows_bottom = READ_Y[1] + 14
    block_top = ry - bh
    stem_top = block_top - HAND_PAD - HAND_STEM
    disc_top, disc_bottom = py - r_pul_px, py + r_pul_px
    inner = r_pul_px - bw / 2.0                                   # the blocks' inner edges are this far inside the legs
    disc_low_at_block = py + math.sqrt(r_pul_px ** 2 - inner ** 2)   # the disc's lowest point over a block's inner edge
    bracket_bottom = BAND_Y0 + 2 + BRACKET_H
    floor_bottom = pad_y + man["pad_h_px"] + FLOOR_PX
    tick_y = ry + x_at_free * ppm
    tick_x0 = hx + TICK_LABEL_DX - f24.getlength(tick_text(ev))
    ev_w = max(f40.getlength(event_text(ev, j)) for j in range(2))
    scale_label_x0 = sx - 36 - f28.getlength(scale_text(h))
    pad_half = bw / 2.0 + PAD_EXTRA / 2.0
    print(f"row check: the readout rows end at x {rows_right:.0f} px (the pulley's left edge is at x {hx - 0:.0f}); both rows end "
          f"at y {rows_bottom:.0f}; the hand marks rise to y {stem_top:.0f} over the block tops at y {block_top:.0f}; the release "
          f"line is at y {ry:.0f} (x {man['line_x0']} to {man['line_x1']}); the pulley is centred at ({hx + r_pul_px:.0f}, "
          f"{py:.0f}) with radius {r_pul_px:.0f} px (y {disc_top:.0f} to {disc_bottom:.0f}; its lowest point over a block's "
          f"inner edge is at y {disc_low_at_block:.1f}), hanging from a bracket ending at y {bracket_bottom:.0f}; the string "
          f"legs are at x {hx:.0f} and {lx:.0f} from y {py:.0f}; the free block spans x {fx - bw / 2:.0f} to {fx + bw / 2:.0f} "
          f"and drops from y {block_top:.0f}..{ry:.0f} to {pad_y - bh:.0f}..{pad_y:.0f}; the heavy block x {hx - bw / 2:.0f} "
          f"to {hx + bw / 2:.0f} the same way; the light block x {lx - bw / 2:.0f} to {lx + bw / 2:.0f} rises from y "
          f"{pad_y - bh:.0f}..{pad_y:.0f} to {block_top:.0f}..{ry:.0f}; the pads from y {pad_y:.0f} to "
          f"{pad_y + man['pad_h_px']:.0f} (x {fx - pad_half:.0f}..{fx + pad_half:.0f}, {hx - pad_half:.0f}..{hx + pad_half:.0f}, "
          f"{lx - pad_half:.0f}..{lx + pad_half:.0f}), the floor to y {floor_bottom:.0f}; the scale at x {sx:.0f} with ticks to "
          f"x {sx - 30:.0f} and labels from x {scale_label_x0:.0f}; the gold tick at y {tick_y:.1f} from x {hx + TICK_DX0:.0f} "
          f"to {hx + TICK_DX1:.0f}, its label from x {tick_x0:.0f}; the event rows at y {EVENT_Y[0]} and {EVENT_Y[1]} (from "
          f"{EVENT_Y[0] - 22} to {EVENT_Y[1] + 22}, widest {ev_w:.0f} px centred on {W // 2}); the band is y {BAND_Y0} to "
          f"{BAND_Y1}; the caption band starts at y {int(man['caption_y'] * H)}; the title rows span y {TITLE_Y0 - 28} to "
          f"{TITLE_Y0 + TITLE_PITCH + 28}, the overlay band ends at y 130")
    assert rows_right < hx - 10, "the readout rows meet the pulley"
    assert rows_bottom < stem_top - 2, "the readout rows meet the hand marks"
    assert stem_top > BAND_Y0 + 10, "the hand marks leave the band"
    assert disc_top > bracket_bottom and bracket_bottom > BAND_Y0, "the pulley meets its bracket or the band top"
    assert block_top > disc_low_at_block + 10, "a block at the release line meets the pulley"
    assert floor_bottom < EVENT_Y[0] - 22 - 10, "the floor meets the event rows"
    assert EVENT_Y[1] + 22 < BAND_Y1 - 4, "the event rows leave the band"
    assert BAND_Y1 <= int(man["caption_y"] * H), "the band reaches the caption band"
    assert tick_x0 > fx + bw / 2.0 + 10, "the gold tick label meets the free block"
    assert fx - pad_half > man["line_x0"] and lx + pad_half < man["line_x1"], "a pad leaves the release line's span"
    assert sx < fx - bw / 2.0 - 16, "the scale meets the free block"
    assert scale_label_x0 > 20, "the scale label leaves the frame"
    assert hx + HAND_DX + HAND_W / 2.0 < hx - 6, "the heavy block's hand mark meets the string"
    assert fx + bw / 2.0 < hx - bw / 2.0 - 40, "the free block meets the heavy block"
    assert lx + pad_half < W - 40, "the light pad leaves the frame"
    assert ev_w < 950 and W // 2 - ev_w / 2 > 40, "the event row leaves the frame"
    assert TITLE_Y0 - 28 > 130 and TITLE_Y0 + TITLE_PITCH + 28 < BAND_Y0, "the title meets the overlay or the band"
    assert PAYOFF_Y - 20 > int(man["caption_y"] * H) + 90, "the card meets the caption band"
    assert PAYOFF_Y + 5 * PAYOFF_PITCH + 20 < H - 40, "the card leaves the frame"
    return ev


def legend_text(man: dict) -> str:
    return f"same weight, same height, 1/{man['slow']:g} speed"


def clock_text(r: float) -> str:
    return "held, at rest" if r < 0.0 else f"{r:.3f} s after the release"


def row_text(which: str, st: dict) -> tuple[str, str]:
    """(coloured label, the rest) of a readout row."""
    label = "dropped:" if which == "free" else "on the pulley:"
    if st["phase"] == HELD:
        return label, " in the hand"
    if st["phase"] == LANDED:
        return label, f" {st['x'] * 100:.1f} cm down, stopped"
    return label, f" {st['x'] * 100:.1f} cm down, {st['v']:.2f} m/s"


def block_label(m: float) -> str:
    return f"{m:.1f} kg"


def scale_text(h: float) -> str:
    return f"{h:g} m"


def tick_text(ev: dict) -> str:
    return f"{ev['x_at_free'] * 100:.1f} cm"


def event_text(ev: dict, j: int) -> str:
    if j == 0:
        return f"dropped: {ev['free']['t_land']:.2f} s, pulley side {ev['x_at_free'] * 100:.1f} cm down"
    return f"on the pulley: lands at {ev['atw']['t_land']:.2f} s, {ev['ratio']:.1f}x later"


def payoff_lines(man: dict, ev: dict) -> list[str]:
    disc = man["description_pulley_disc_kg"][-1]
    text = man["payoff_text"].format(t_free=ev["free"]["t_land"], t_atw=ev["atw"]["t_land"], ratio=ev["ratio"],
                                     net_kg=ev["net_kg"], tot_kg=ev["tot_kg"], naive=man["naive_divisor"],
                                     t_naive=ev["t_naive"], tension=ev["T"], disc_kg=disc,
                                     t_disc=ev["var"][f"disc {disc:g}"][1])
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
        self.font_block = ImageFont.truetype(font, 28 * SS)   # the block labels are drawn in the 2x layer
        self.ppm = float(man["px_per_m"])
        self.S = man["slow"]
        self.P = man["cycle_s"]
        self.P_f = int(round(man["cycle_s"] * self.fps))
        self.c0_f = int(round(man["first_cycle_at"] * self.fps))
        self.pa, self.F = man["release_at"], man["reset_fade"]
        self.g, self.h = man["g"], man["drop_m"]
        self.m1, self.m2 = man["heavy_kg"], man["light_kg"]
        self.ry = float(man["release_y"])
        self.pad_y = self.ry + self.h * self.ppm
        self.fx, self.hx, self.lx, self.sx = (float(man[k]) for k in ("free_x", "heavy_x", "light_x", "scale_x"))
        self.py = float(man["pulley_y"])
        self.bw, self.bh, self.pad_h = man["block_w_px"], man["block_h_px"], man["pad_h_px"]
        self.r_pul_px, self.r_pul = ev["r_pul_px"], ev["r_pul"]
        self.cx = self.hx + self.r_pul_px
        self.free, self.atw = ev["free"], ev["atw"]

    def phase(self, f: int) -> tuple[int, float]:
        k, tau_f = divmod(f - self.c0_f, self.P_f)
        return k, tau_f / self.fps

    @staticmethod
    def L_(x: float, y: float) -> tuple[float, float]:
        """Layer (2x) pixel of a frame point, rounded to 1e-4 px so equal states draw equal pixels."""
        return round(x * SS, 4), round((y - BAND_Y0) * SS, 4)

    def circle(self, d: ImageDraw.ImageDraw, X: float, Y: float, rr: float, **kw) -> None:
        d.ellipse((X - rr, Y - rr, X + rr, Y + rr), **kw)

    def rect(self, d: ImageDraw.ImageDraw, x0: float, y0: float, x1: float, y1: float, **kw) -> None:
        p0, p1 = self.L_(x0, y0), self.L_(x1, y1)
        d.rectangle((p0[0], p0[1], p1[0], p1[1]), **kw)

    def line(self, d: ImageDraw.ImageDraw, x0: float, y0: float, x1: float, y1: float, fill, width: int) -> None:
        p0, p1 = self.L_(x0, y0), self.L_(x1, y1)
        d.line((*p0, *p1), fill=fill, width=width * SS)

    def draw_fixed(self, d: ImageDraw.ImageDraw) -> None:
        man = self.man
        ry, pad_y = self.ry, self.pad_y
        # The ceiling bracket and the pulley's stem (the disc is drawn over it).
        self.rect(d, self.cx - BRACKET_W / 2, BAND_Y0 + 2, self.cx + BRACKET_W / 2, BAND_Y0 + 2 + BRACKET_H, fill=RIM)
        self.rect(d, self.cx - STEM_W / 2, BAND_Y0 + 2 + BRACKET_H, self.cx + STEM_W / 2, self.py, fill=RIM)
        # The release line (the start height of the two 1.1 kg blocks' bottoms) across both columns.
        self.line(d, man["line_x0"], ry, man["line_x1"], ry, RIM, 3)
        # The hand marks on the two 1.1 kg blocks' tops (they stay where the hands let go).
        top = ry - self.bh
        for cx in (self.fx, self.hx):
            hx_ = cx + HAND_DX
            self.rect(d, hx_ - 5, top - HAND_PAD - HAND_STEM, hx_ + 5, top - HAND_PAD, fill=CLAMP)
            q0, q1 = self.L_(hx_ - HAND_W / 2, top - HAND_PAD), self.L_(hx_ + HAND_W / 2, top)
            d.rounded_rectangle((q0[0], q0[1], q1[0], q1[1]), radius=3 * SS, fill=CLAMP)
        # The height scale on the left: a bar with a tick every 10 cm.
        self.line(d, self.sx, ry, self.sx, pad_y, RIM, 3)
        for c in range(0, int(round(self.h * 100)) + 1, 10):
            yy = ry + c / 100.0 * self.ppm
            ln = 30 if c % 50 == 0 else 16
            self.line(d, self.sx - ln, yy, self.sx, yy, RIM, 3 if c % 50 == 0 else 2)
        # The floor slab and the three pads on it.
        self.rect(d, man["line_x0"], pad_y + self.pad_h, man["line_x1"], pad_y + self.pad_h + FLOOR_PX, fill=DECK_A)
        half = self.bw / 2.0 + PAD_EXTRA / 2.0
        for cx in (self.fx, self.hx, self.lx):
            self.rect(d, cx - half, pad_y, cx + half, pad_y + self.pad_h, fill=DECK_B)
            self.line(d, cx - half, pad_y, cx + half, pad_y, RIM, 2)

    def draw_block(self, d: ImageDraw.ImageDraw, cx: float, bottom: float, fill, rim, label: str) -> None:
        p0, p1 = self.L_(cx - self.bw / 2, bottom - self.bh), self.L_(cx + self.bw / 2, bottom)
        d.rounded_rectangle((p0[0], p0[1], p1[0], p1[1]), radius=8 * SS, fill=fill, outline=rim, width=2 * SS)
        X, Y = self.L_(cx, bottom - self.bh / 2)
        d.text((X, Y), label, font=self.font_block, fill=BG, anchor="mm")

    def draw_pulley(self, d: ImageDraw.ImageDraw, x_atw: float, heavy_top: float, light_top: float) -> None:
        cx, cy, r = self.cx, self.py, self.r_pul_px
        X, Y = self.L_(cx, cy)
        R = r * SS
        self.circle(d, X, Y, R, fill=DECK_B, outline=RIM, width=3 * SS)
        # The spoke mark turns with the string: counterclockwise as the heavy side goes down.
        th = x_atw / self.r_pul
        ex, ey = cx - (r - 8) * math.sin(th), cy - (r - 8) * math.cos(th)
        self.line(d, cx, cy, ex, ey, STEEL, 5)
        self.circle(d, X, Y, HUB_R * SS, fill=AXLE, outline=RIM, width=2 * SS)
        # The string: the arc over the top of the disc and the two vertical legs.
        d.arc((X - R, Y - R, X + R, Y + R), 180, 360, fill=STEEL, width=2 * SS)
        self.line(d, self.hx, cy, self.hx, heavy_top, STEEL, 2)
        self.line(d, self.lx, cy, self.lx, light_top, STEEL, 2)

    def scene(self, tau: float) -> tuple[Image.Image, dict]:
        """The band layer tau seconds into a cycle (all held before the release)."""
        layer = Image.new("RGB", (W * SS, (BAND_Y1 - BAND_Y0) * SS), BG)
        d = ImageDraw.Draw(layer)
        self.draw_fixed(d)
        tv = tau - self.pa
        rt = tv / self.S
        fs = drop_state(self.free, rt, self.h)
        hs = drop_state(self.atw, rt, self.h)
        free_bottom = self.ry + fs["x"] * self.ppm
        heavy_bottom = self.ry + hs["x"] * self.ppm
        light_bottom = self.pad_y - hs["x"] * self.ppm
        if fs["phase"] == LANDED:
            # The gold tick where the heavy block's bottom was when the dropped weight landed (label at 1x).
            ty = self.ry + self.ev["x_at_free"] * self.ppm
            self.line(d, self.hx + TICK_DX0, ty, self.hx + TICK_DX1, ty, GOLD, 3)
        self.draw_pulley(d, hs["x"], heavy_bottom - self.bh, light_bottom - self.bh)
        self.draw_block(d, self.fx, free_bottom, TEAL, TEAL_RIM, block_label(self.m1))
        self.draw_block(d, self.hx, heavy_bottom, CORAL, CORAL_RIM, block_label(self.m1))
        self.draw_block(d, self.lx, light_bottom, STEEL, STEEL_RIM, block_label(self.m2))
        return layer, {"free": fs, "atw": hs, "tv": tv, "rt": rt}

    def draw_scene(self, f: int) -> tuple[Image.Image, dict]:
        k, tau = self.phase(f)
        P, F = self.P, self.F
        layer, st = self.scene(tau)
        st["alpha"], st["k"] = 1.0, k
        if tau >= P - F:
            # Crossfade to the next cycle's held setup: the blocks blend back to the release line and
            # the light weight to its pad; the readouts fade out over the first half and in over the second.
            a = (tau - (P - F)) / F
            new, st_new = self.scene(tau - P)
            layer = Image.blend(layer, new, a)
            st["alpha"] = max(0.0, 1.0 - 2.0 * a)
            st_new["alpha"], st_new["k"] = max(0.0, 2.0 * a - 1.0), k + 1
            if a >= 0.5:
                st = st_new
        return layer, st

    def draw_text(self, d: ImageDraw.ImageDraw, st: dict, hud_alpha: float) -> None:
        man, ev = self.man, self.ev
        a = st["alpha"]
        fs, hs = st["free"], st["atw"]
        for j, (which, col, s) in enumerate((("free", TEAL, fs), ("atw", CORAL, hs))):
            label, rest = row_text(which, s)
            d.text((ROW_X0, READ_Y[j]), label, font=self.font_small, fill=blend(col, a), anchor="lm")
            d.text((ROW_X0 + self.font_small.getlength(label), READ_Y[j]), rest, font=self.font_small,
                   fill=blend(TEXT, a), anchor="lm")
        d.text((self.sx - 36, self.ry), "0", font=self.font_small, fill=MUTED, anchor="rm")
        d.text((self.sx - 36, self.pad_y), scale_text(self.h), font=self.font_small, fill=MUTED, anchor="rm")
        if fs["phase"] == LANDED:
            d.text((self.hx + TICK_LABEL_DX, self.ry + ev["x_at_free"] * self.ppm), tick_text(ev), font=self.font_tiny,
                   fill=blend(GOLD, a), anchor="rm")
        lit = (fs["phase"] == LANDED, hs["phase"] == LANDED)
        for j in range(2):
            if lit[j]:
                d.text((W / 2, EVENT_Y[j]), event_text(ev, j), font=self.font, fill=blend(GOLD, a), anchor="mm")
        if hud_alpha > 0.02:
            d.text((W / 2, LEGEND_Y), legend_text(man), font=self.font, fill=blend(TEXT, hud_alpha), anchor="mm")
            d.text((W / 2, CLOCK_Y), clock_text(st["rt"]), font=self.font_small, fill=blend(MUTED, hud_alpha), anchor="mm")

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
        layer, st = self.draw_scene(f)
        img.paste(layer.reduce(SS), (0, BAND_Y0))
        d = ImageDraw.Draw(img)
        self.draw_text(d, st, hud_alpha)
        if title_alpha > 0.0:
            for j, line in enumerate(man["title"].split("|")):
                d.text((W / 2, TITLE_Y0 + j * TITLE_PITCH), line, font=self.font_title, fill=blend(TEXT, title_alpha),
                       anchor="mm")
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
    man = json.loads((ROOT / "projects/atwood/manifest.json").read_text())
    ev = measure(man)
    if "--measure-only" in sys.argv:
        return
    if "--frames" in sys.argv:
        times = [float(v) for v in sys.argv[sys.argv.index("--frames") + 1].split(",")]
        r = Renderer(man, ev)
        (ROOT / "media/atwood").mkdir(parents=True, exist_ok=True)
        for tv in times:
            Image.fromarray(r.frame_at(int(round(tv * man["fps"])))).save(ROOT / f"media/atwood/smoke-{tv}.png")
        print("smoke frames: " + ", ".join(f"{tv}" for tv in times))
        return
    Renderer(man, ev).render(ROOT / "media/atwood/footage.mp4")


if __name__ == "__main__":
    main()
