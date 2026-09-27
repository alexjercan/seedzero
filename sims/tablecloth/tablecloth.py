#!/usr/bin/env python3
"""Pull the tablecloth: how fast must you pull?

A short glass stands on a tablecloth 0.30 m from the cloth's far edge and
0.40 m from the table edge on the puller's side. At t = 0 the cloth is
pulled toward the table edge at a steady speed V (a jerk to V, then held).
Sliding friction mu_c between glass and cloth drags the glass toward the
puller at mu_c g while the cloth slips under it; the cloth has passed out
from under the glass when the slip V t - mu_c g t^2 / 2 reaches L, which
needs V >= sqrt(2 mu_c g L). Two panels on the same clock, one above the
other, the same cloth and the same glass. Top, V below the threshold: the
glass reaches cloth speed after V^2 / (2 mu_c g) of travel with cloth
still under it, rides with the cloth and goes over the table edge.
Bottom, V above the threshold: the cloth is clear in a tenth of a second
with the glass barely moving; on the bare table (mu_t) it slides a little
further and stops. Both panels are integrated by RK4 at 10,000 steps a
second; the friction switches (zero slip, the cloth's edge, zero speed,
the table edge) are located by bisection inside the step, and the run is
checked against the closed forms. The pull repeats every cycle_s seconds
of video with a crossfade back to the resting setup; the cycle divides
the scene length, so the scene is exactly periodic and the last frame
equals the first. Shown at 1/slow speed. The glass is a short tumbler: a
block tips under friction only if mu exceeds its width over its height,
so it slides on both surfaces and never tips. Deterministic, no seed.

Measured and printed: the tipping check, the threshold speed and how it
scales with the cloth length and the cloth friction, the slow pull by
RK4 (the time and distance to cloth speed, the cloth left under the
glass, the time over the table edge) against the closed forms, the fast
pull by RK4 (the time the cloth is clear, the handover speed, the travel
on the cloth, the slide on the table, the total) against the closed
forms, the RK4 sample error, other pull speeds for the description, the
schedule in video time, the loop and periodicity checks and the on-screen
text widths.

usage: tablecloth.py [--measure-only] [--frames t1,t2,...]
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
CLOTH_A = (190, 70, 64)
CLOTH_B = (236, 214, 176)
GLASS = (150, 176, 200)
GLASS_RIM = (222, 234, 244)
WATER = (72, 134, 206)

# Layout: overlay at y 96..130 (captions.py), two title rows at y 190/252 for
# the first seconds, then the legend at y 236 and the shared clock at y 290;
# two panels stacked, the slow pull in the band y 340..880 and the fast pull
# in y 880..1420, each band drawn at 2x in its own layer (so a glass falling
# off the top table is clipped at the band's bottom), with its label row 40
# px under the band top, its state row at 84 and its fixed line at 120, the
# table surface 350 px under the band top (y 690 and 1230), the slab 40 px
# thick, the legs to 24 px above the band's bottom; captions at caption_y
# 0.75 (y 1440..1520); the five-line card from y 1580 at a 52 px pitch.
LEGEND_Y, CLOCK_Y = 236, 290
SS = 2
PAYOFF_Y, PAYOFF_PITCH = 1580.0, 52
PANELS = ("slow", "fast")
LABEL_DY, STATE_DY, FIX_DY, SURFACE_DY = 40, 84, 120, 350
SLAB_PX, LEG_W = 40, 20
ROW_X0, ROW_X1 = 100, 980
SLIP, RIDE, SLIDE, REST, OFF, WAIT = "slip", "ride", "slide", "rest", "off", "wait"
STATE_WORDS = {WAIT: "at rest on the cloth", SLIP: "sliding on the cloth", RIDE: "riding with the cloth",
               OFF: "over the edge", SLIDE: "sliding on the bare table", REST: "stopped on the table"}


def blend(col, a: float, base=BG) -> tuple:
    a = max(0.0, min(1.0, a))
    return tuple(int(round(c * a + b * (1 - a))) for c, b in zip(col, base))


# --- measurement --------------------------------------------------------------
def rk4_step(x: float, v: float, a: float, h: float) -> tuple[float, float]:
    """One classical RK4 step of x' = v, v' = a over h (a is constant inside a phase)."""
    k1x, k1v = v, a
    k2x, k2v = v + 0.5 * h * k1v, a
    k3x, k3v = v + 0.5 * h * k2v, a
    k4x, k4v = v + h * k3v, a
    return x + h * (k1x + 2.0 * k2x + 2.0 * k3x + k4x) / 6.0, v + h * (k1v + 2.0 * k2v + 2.0 * k3v + k4v) / 6.0


def phase_of(x: float, v: float, t: float, V: float, L: float, x_edge: float) -> str:
    """The friction phase of a glass at (x, v) at time t under a cloth moving at V."""
    if x >= x_edge:
        return OFF
    if V * t - x < L:
        return SLIP if v < V else RIDE
    return SLIDE if v > 0.0 else REST


def simulate(V: float, man: dict) -> dict:
    """RK4 at steps_per_second from the yank until the glass stops or goes over the edge; each
    phase change is located by bisection inside the step, the state snapped to the boundary."""
    g = man["g"]
    ugc, ugt = man["mu_cloth"] * g, man["mu_table"] * g
    L, x_edge = man["cloth_under_glass_m"], man["edge_from_glass_m"]
    dt = 1.0 / man["steps_per_second"]
    n = int(round(man["sim_end_s"] / dt))
    acc = {SLIP: ugc, RIDE: 0.0, SLIDE: -ugt, REST: 0.0, OFF: 0.0}
    t, x, v, phase = 0.0, 0.0, 0.0, SLIP
    ts, xs, vs = [0.0], [0.0], [0.0]
    events: list = []
    pieces: list = []
    p0 = (0.0, 0.0, 0.0)
    for i in range(1, n + 1):
        remaining = dt
        while remaining > 0.0 and phase != OFF:
            a = acc[phase]
            xt, vt = rk4_step(x, v, a, remaining)
            if phase in (REST,) or phase_of(xt, vt, t + remaining, V, L, x_edge) == phase:
                x, v, t = xt, vt, t + remaining
                break
            lo, hi = 0.0, remaining
            for _ in range(80):
                mid = 0.5 * (lo + hi)
                xm, vm = rk4_step(x, v, a, mid)
                if phase_of(xm, vm, t + mid, V, L, x_edge) == phase:
                    lo = mid
                else:
                    hi = mid
            xh, vh = rk4_step(x, v, a, hi)
            new = phase_of(xh, vh, t + hi, V, L, x_edge)
            if phase == SLIP and new == RIDE:
                vh = V
            if phase == SLIDE and new == REST:
                vh = 0.0
            if new == OFF:
                xh = x_edge
            pieces.append((p0[0], t + hi, p0[1], p0[2], a, phase))
            x, v, t = xh, vh, t + hi
            events.append({"t": t, "from": phase, "to": new, "x": x, "v": v, "slip": V * t - x})
            phase = new
            p0 = (t, x, v)
            remaining -= hi
        if phase != OFF:
            t = i * dt
        ts.append(t)
        xs.append(x)
        vs.append(v)
        if phase == OFF:
            break
    pieces.append((p0[0], t if phase == OFF else man["sim_end_s"], p0[1], p0[2], acc[phase], phase))
    return {"V": V, "t": np.array(ts), "x": np.array(xs), "v": np.array(vs), "events": events,
            "pieces": pieces, "final": phase, "t_end": t}


def closed(V: float, man: dict) -> dict:
    g = man["g"]
    ugc, ugt = man["mu_cloth"] * g, man["mu_table"] * g
    L, x_edge = man["cloth_under_glass_m"], man["edge_from_glass_m"]
    vstar = math.sqrt(2.0 * ugc * L)
    out = {"vstar": vstar, "cloth_off_table": (L + x_edge) / V}
    if V < vstar:
        t_ride, x_ride = V / ugc, V * V / (2.0 * ugc)
        out.update({"clears": False, "t_ride": t_ride, "x_ride": x_ride, "left": L - x_ride,
                    "t_edge": t_ride + (x_edge - x_ride) / V if x_ride < x_edge else None})
    else:
        t1 = (V - math.sqrt(V * V - 2.0 * ugc * L)) / ugc
        v1 = ugc * t1
        x1 = 0.5 * ugc * t1 * t1
        d2, t2 = v1 * v1 / (2.0 * ugt), v1 / ugt
        out.update({"clears": True, "t1": t1, "v1": v1, "x1": x1, "d2": d2, "t2": t2, "tot": x1 + d2,
                    "t_stop": t1 + t2, "reaches_edge": x1 + d2 >= x_edge})
    return out


def closed_x(V: float, cf: dict, man: dict, t: np.ndarray) -> np.ndarray:
    ugc, ugt = man["mu_cloth"] * man["g"], man["mu_table"] * man["g"]
    if not cf["clears"]:
        return np.where(t <= cf["t_ride"], 0.5 * ugc * t * t, cf["x_ride"] + V * (t - cf["t_ride"]))
    t1, ts = cf["t1"], cf["t_stop"]
    on_table = cf["x1"] + cf["v1"] * (t - t1) - 0.5 * ugt * (t - t1) ** 2
    return np.where(t <= t1, 0.5 * ugc * t * t, np.where(t <= ts, on_table, cf["tot"]))


def event(run: dict, frm: str, to: str):
    for e in run["events"]:
        if e["from"] == frm and e["to"] == to:
            return e
    return None


def state_at(run: dict, r: float) -> tuple[float, float, str]:
    """(x, v, phase) of the glass r seconds after the yank, from the RK4 pieces (exact between events)."""
    if r < 0.0:
        return 0.0, 0.0, WAIT
    ps = run["pieces"]
    if run["final"] == OFF and r >= run["t_end"]:
        return ps[-1][2], ps[-1][3], OFF     # the last piece starts at the edge crossing
    for t0, t1, x0, v0, a, ph in ps:
        if r < t1:
            break
    d = r - t0
    return x0 + v0 * d + 0.5 * a * d * d, v0 + a * d, ph


def measure(man: dict) -> dict:
    g = man["g"]
    muc, mut = man["mu_cloth"], man["mu_table"]
    L, x_edge = man["cloth_under_glass_m"], man["edge_from_glass_m"]
    gw, gh = man["glass_width_m"], man["glass_height_m"]
    S, P, D, fps, F, pa = man["slow"], man["cycle_s"], man["scene_duration"], man["fps"], man["reset_fade"], man["pull_at"]
    dt = 1.0 / man["steps_per_second"]
    V_slow, V_fast = man["pull_speeds_m_s"]
    cycles = D / P
    assert abs(cycles - round(cycles)) < 1e-9, "the pull cycle must divide the scene length"
    for key in ("cycle_s", "pull_at", "first_cycle_at", "reset_fade"):
        assert abs(man[key] * fps - round(man[key] * fps)) < 1e-9, f"{key} must be a whole number of frames"
    ppm = man["px_per_m"]
    print(f"setup: a short glass ({gw * 100:g} cm wide, {gh * 100:g} cm tall) stands on a tablecloth {L * 100:g} cm "
          f"from the cloth's far edge and {x_edge * 100:g} cm from the table edge on the puller's side; at t = 0 the "
          f"cloth is pulled toward the table edge at a steady speed (a jerk to V, then held); sliding friction mu = "
          f"{muc:g} between glass and cloth (mu g = {muc * g:.4f} m/s^2) and {mut:g} between glass and table ({mut * g:.4f} "
          f"m/s^2), g = {g:g} m/s^2, the cloth thin and massless; top panel V = {V_slow:g} m/s, bottom panel V = "
          f"{V_fast:g} m/s, both integrated by RK4 at {man['steps_per_second']} steps per second (dt = {dt:.0e} s) "
          f"with the friction switches located by bisection inside the step; shown at 1/{S:g} speed on a {P:g} s "
          f"cycle ({P * fps:.0f} frames) with the yank {pa:g} s into the cycle, {cycles:.0f} cycles in {D:g} s; drawn "
          f"at {ppm:g} px per metre; deterministic, no seed")
    ratio = gw / gh
    print(f"tipping check: a block tips under friction only if mu exceeds its width over its height; this glass has "
          f"{gw * 100:g} / {gh * 100:g} = {ratio:.3f}, above both {muc:g} (cloth) and {mut:g} (table), so it slides "
          f"and never tips on either surface (a glass taller than {gw / mut * 100:.1f} cm at {gw * 100:g} cm wide "
          f"would tip on the table)")
    vstar = math.sqrt(2.0 * muc * g * L)
    print(f"threshold: the cloth is clear of the glass only if V^2 / (2 mu g) >= L, i.e. V >= sqrt(2 mu g L) = "
          f"{vstar:.4f} m/s with this cloth (mu {muc:g}, L {L * 100:g} cm); it scales with the square root of the "
          f"cloth length under the glass (" + ", ".join(
              f"{l * 100:g} cm: {math.sqrt(2 * muc * g * l):.3f} m/s" for l in man["description_lengths_m"])
          + ") and of the cloth friction (" + ", ".join(
              f"mu {m:g}: {math.sqrt(2 * m * g * L):.3f} m/s" for m in man["description_mus"])
          + f"); the table friction {mut:g} only sets how far the glass slides afterwards")
    runs = {"slow": simulate(V_slow, man), "fast": simulate(V_fast, man)}
    cfs = {"slow": closed(V_slow, man), "fast": closed(V_fast, man)}
    # The slow pull.
    r, cf = runs["slow"], cfs["slow"]
    ride = event(r, SLIP, RIDE)
    off = event(r, RIDE, OFF)
    assert ride is not None and off is not None and event(r, SLIP, SLIDE) is None, "the slow pull must ride off the edge"
    err_slow = float(np.max(np.abs(r["x"] - closed_x(V_slow, cf, man, r["t"]))))
    print(f"slow pull ({V_slow:g} m/s, below the threshold): RK4: the glass slides on the cloth, gaining {muc * g:.3f} "
          f"m/s^2, and reaches cloth speed {ride['v']:.4f} m/s at {ride['t']:.4f} s after moving {ride['x'] * 100:.2f} "
          f"cm (closed forms V / (mu g) = {cf['t_ride']:.4f} s, V^2 / (2 mu g) = {cf['x_ride'] * 100:.2f} cm; diffs "
          f"{abs(ride['t'] - cf['t_ride']):.1e} s, {abs(ride['x'] - cf['x_ride']) * 100:.1e} cm); by then the cloth "
          f"has moved {V_slow * ride['t'] * 100:.2f} cm, {ride['slip'] * 100:.2f} cm of it out from under the glass, "
          f"so {(L - ride['slip']) * 100:.2f} cm of cloth is still under it (closed form {cf['left'] * 100:.2f} cm) "
          f"and the cloth never clears; the glass rides with the cloth at {V_slow:g} m/s and its centre passes the "
          f"table edge {x_edge * 100:g} cm from its start at {off['t']:.4f} s (closed form {cf['t_edge']:.4f} s, diff "
          f"{abs(off['t'] - cf['t_edge']):.1e} s), the cloth's far edge then {(L - ride['slip']) * 100:.2f} cm behind "
          f"the glass and {(x_edge + L - V_slow * off['t']) * 100:.1f} cm from the table edge; the cloth's far edge "
          f"leaves the table at {cf['cloth_off_table']:.3f} s; RK4 stays within {err_slow:.1e} m of the closed form "
          f"over {len(r['t'])} samples")
    # The fast pull.
    r, cf = runs["fast"], cfs["fast"]
    clear = event(r, SLIP, SLIDE)
    stop = event(r, SLIDE, REST)
    assert clear is not None and stop is not None and r["final"] == REST, "the fast pull must clear and stop"
    err_fast = float(np.max(np.abs(r["x"] - closed_x(V_fast, cf, man, r["t"]))))
    print(f"fast pull ({V_fast:g} m/s, above the threshold): RK4: the cloth is clear of the glass at {clear['t'] * 1000:.1f} "
          f"ms (closed form (V - sqrt(V^2 - 2 mu g L)) / (mu g) = {cf['t1'] * 1000:.1f} ms, diff "
          f"{abs(clear['t'] - cf['t1']) * 1000:.1e} ms) with the glass at {clear['v']:.4f} m/s (closed form "
          f"{cf['v1']:.4f}) having moved {clear['x'] * 100:.3f} cm (closed form {cf['x1'] * 100:.3f}); on the bare "
          f"table it slows at {mut * g:.3f} m/s^2 and stops at {stop['t'] * 1000:.1f} ms after "
          f"{(stop['x'] - clear['x']) * 100:.3f} cm more (closed forms v1^2 / (2 mu g) = {cf['d2'] * 100:.3f} cm in "
          f"{cf['t2'] * 1000:.1f} ms); {stop['x'] * 100:.3f} cm in all (closed form {cf['tot'] * 100:.3f} cm, diff "
          f"{abs(stop['x'] - cf['tot']) * 100:.1e} cm), {stop['x'] * 100:.2f} cm, {(x_edge - stop['x']) * 100:.1f} cm "
          f"short of the table edge; it stays there to the end of the run ({r['t_end']:.2f} s); the cloth's far edge "
          f"leaves the table at {cf['cloth_off_table']:.3f} s; RK4 stays within {err_fast:.1e} m of the closed form "
          f"over {len(r['t'])} samples")
    print(f"the same cloth and glass end opposite ways: at {V_slow:g} m/s the glass goes over the edge, at {V_fast:g} "
          f"m/s it moves {stop['x'] * 100:.2f} cm; {stop['x'] / x_edge * 100:.1f} % of the way to the edge")
    # Other speeds, for the description.
    descr = []
    for u in man["description_speeds_m_s"]:
        ru, cu = simulate(u, man), closed(u, man)
        if cu["clears"]:
            c, s_ = event(ru, SLIP, SLIDE), event(ru, SLIDE, REST)
            descr.append(f"{u:g} m/s: the cloth is clear in {c['t'] * 1000:.1f} ms with the glass at {c['v']:.3f} m/s "
                         f"after {c['x'] * 100:.2f} cm, it slides {(s_['x'] - c['x']) * 100:.2f} cm more and stops after "
                         f"{s_['x'] * 100:.2f} cm at {s_['t'] * 1000:.0f} ms, {(x_edge - s_['x']) * 100:.1f} cm short of "
                         f"the edge (closed form {cu['tot'] * 100:.2f} cm, diff {abs(s_['x'] - cu['tot']) * 100:.1e} cm)")
        else:
            rd, of = event(ru, SLIP, RIDE), event(ru, RIDE, OFF)
            descr.append(f"{u:g} m/s: cloth speed after {rd['x'] * 100:.1f} cm at {rd['t']:.3f} s with "
                         f"{(L - rd['slip']) * 100:.1f} cm of cloth left under the glass, over the edge at {of['t']:.3f} s")
    print("for the description (same cloth, other pull speeds): " + "; ".join(descr))
    # Schedule in video time.
    t0 = man["first_cycle_at"]
    k0 = math.ceil((0.0 - t0) / P - 1e-9) - 1
    k1 = math.floor((D - t0) / P - 1e-9)
    starts = [t0 + k * P for k in range(k0, k1 + 1)]
    ev = {"vstar": vstar, "runs": runs, "cfs": cfs, "ride": event(runs["slow"], SLIP, RIDE),
          "off": event(runs["slow"], RIDE, OFF), "clear": clear, "stop": stop, "cycles": int(round(cycles))}
    drop_px = man["band_y"][1] - (man["band_y"][0] + SURFACE_DY - man["cloth_px"] - gh * ppm)
    t_fall = math.sqrt(2.0 * drop_px / ppm / g)
    ev["t_fall"] = t_fall
    x_far0 = man["table_x0_px"] + man["bare_left_m"] * ppm
    frame_exit = {p: (W - x_far0) / ppm / V for p, V in zip(PANELS, man["pull_speeds_m_s"])}
    vt = lambda real: pa + real * S   # noqa: E731  video time after the cycle start
    def lst(off_: float) -> str:
        return ", ".join(f"{s + off_:.2f}" for s in starts if 0.0 <= s + off_ < D)
    tau0 = (0.0 - t0) % P
    r0 = (tau0 - pa) / S
    st = {p: state_at(runs[p], r0) for p in PANELS}
    print(f"schedule (video time, 1/{S:g} speed): cycles of {P:g} s start at " + ", ".join(f"{s:.2f}" for s in starts)
          + f" s (the first {-t0:.2f} s before the first frame); the yank {pa:g} s into each cycle at {lst(pa)} s; the "
          f"fast cloth is clear {ev['clear']['t'] * S:.2f} s after the yank at {lst(vt(ev['clear']['t']))} s and the fast "
          f"glass stops {ev['stop']['t'] * S:.2f} s after the yank at {lst(vt(ev['stop']['t']))} s; the slow glass "
          f"reaches cloth speed {ev['ride']['t'] * S:.2f} s after the yank at {lst(vt(ev['ride']['t']))} s and goes "
          f"over the edge {ev['off']['t'] * S:.2f} s after the yank at {lst(vt(ev['off']['t']))} s, then falls "
          f"(a {drop_px / ppm:.2f} m drop to the bottom of its panel, {t_fall:.3f} s real, {t_fall * S:.2f} s of video, "
          f"rotation aside); the cloth's far edge leaves the table {vt(cfs['fast']['cloth_off_table']):.2f} s "
          f"(fast) and {vt(cfs['slow']['cloth_off_table']):.2f} s (slow) after the cycle start and leaves the frame "
          f"at {vt(frame_exit['fast']):.2f} s (fast) and {vt(frame_exit['slow']):.2f} s (slow)"
          + f"; each cycle crossfades to the resting setup over its last {F:g} s (out over {P - F:.2f} to "
          f"{P - F / 2:.2f} s, in over {P - F / 2:.2f} to {P:.2f} s after the cycle start); on the first frame the "
          f"cycle is {tau0:.2f} s in ({r0:.3f} s real after the yank): the slow glass is {STATE_WORDS[st['slow'][2]]} "
          f"at {st['slow'][0] * 100:.1f} cm, the fast glass {STATE_WORDS[st['fast'][2]]} at {st['fast'][0] * 100:.2f} "
          f"cm; title until {man['title_until']:g} s; payoff card from {man['payoff_t']:g} s; the title fades back in "
          f"over the last {man['loop_fade']:g} s and the last frame repeats the first (the scene is periodic: {D:g} s "
          f"holds exactly {cycles:.0f} cycles)")
    # Text widths.
    font = os.environ["SEED_ZERO_FONT"]
    f28, f34, f40, f56 = (ImageFont.truetype(font, n) for n in (28, 34, 40, 56))
    widths = {"overlay@34": (f34, man["overlay"])}
    for j, line in enumerate(man["title"].split("|")):
        widths[f"title line {j + 1}@56"] = (f56, line)
    widths["legend@40"] = (f40, legend_text(man))
    widths["clock@28"] = (f28, clock_text(0.1035))
    widths["clock rest@28"] = (f28, clock_text(-1.0))
    for p, V in zip(PANELS, man["pull_speeds_m_s"]):
        widths[f"label {p}@40"] = (f40, label_text(V))
        widths[f"fixed {p}@28"] = (f28, fixed_text(ev, p))
    for ph, word in STATE_WORDS.items():
        widths[f"state {ph}@28"] = (f28, word)
    widths["readout@40"] = (f40, readout_text(x_edge))
    widths["speed@28"] = (f28, speed_text(V_fast))
    widths["mark start@28"] = (f28, "start")
    widths["mark edge@28"] = (f28, "edge")
    for j, line in enumerate(payoff_lines(man, ev)):
        widths[f"payoff line {j + 1}@40"] = (f40, line)
    print("text widths: " + ", ".join(f"{k} {f.getlength(s):.0f} px" for k, (f, s) in widths.items()))
    assert all(f.getlength(s) < 950 for f, s in widths.values()), "a text line is wider than 950 px"
    left = ROW_X0 + max(f40.getlength(label_text(V)) for V in man["pull_speeds_m_s"])
    right = ROW_X1 - f40.getlength(readout_text(x_edge))
    left2 = ROW_X0 + max(f28.getlength(w) for w in STATE_WORDS.values())
    right2 = ROW_X1 - f28.getlength(speed_text(V_fast))
    print(f"row check: the label ends at x {left:.0f} px and the readout starts at {right:.0f} px; the state word "
          f"ends at {left2:.0f} px at most and the speed readout starts at {right2:.0f} px")
    assert left < right - 40 and left2 < right2 - 40, "the row texts collide"
    return ev


def legend_text(man: dict) -> str:
    return f"same cloth, same glass, 1/{man['slow']:g} speed"


def clock_text(r: float) -> str:
    return "at rest before the pull" if r < 0.0 else f"{r:.3f} s after the pull"


def label_text(V: float) -> str:
    return f"pulled at {V:g} m/s"


def readout_text(x: float) -> str:
    return f"moved {x * 100:.1f} cm"


def speed_text(v: float) -> str:
    return f"glass {v:.2f} m/s"


def fixed_text(ev: dict, panel: str) -> str:
    if panel == "slow":
        return f"cloth speed after {ev['ride']['x'] * 100:.1f} cm; over the edge at {ev['off']['t']:.3f} s"
    return f"cloth clear in {ev['clear']['t'] * 1000:.0f} ms; stops after {ev['stop']['x'] * 100:.2f} cm"


def payoff_lines(man: dict, ev: dict) -> list[str]:
    text = man["payoff_text"].format(vstar=ev["vstar"], v_slow=man["pull_speeds_m_s"][0],
                                     v_fast=man["pull_speeds_m_s"][1], tot_cm=ev["stop"]["x"] * 100)
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
        self.ppm = float(man["px_per_m"])
        self.S = man["slow"]
        self.P_f = int(round(man["cycle_s"] * self.fps))
        self.c0_f = int(round(man["first_cycle_at"] * self.fps))
        self.pa, self.F = man["pull_at"], man["reset_fade"]
        self.P = man["cycle_s"]
        self.speeds = dict(zip(PANELS, man["pull_speeds_m_s"]))
        self.runs = ev["runs"]
        self.x_far0 = man["table_x0_px"] + man["bare_left_m"] * self.ppm
        self.x_start = self.x_far0 + man["cloth_under_glass_m"] * self.ppm
        self.x_edge = self.x_start + man["edge_from_glass_m"] * self.ppm
        self.band = {p: (man["band_y"][i], man["band_y"][i + 1]) for i, p in enumerate(PANELS)}

    # --- state helpers ------------------------------------------------------
    def phase(self, f: int) -> tuple[int, float]:
        k, tau_f = divmod(f - self.c0_f, self.P_f)
        return k, tau_f / self.fps

    # --- pixel helpers ------------------------------------------------------
    @staticmethod
    def L(x: float, y: float) -> tuple[float, float]:
        """Layer (2x) pixel of a band-local point, rounded to 1e-4 px so equal states draw equal pixels."""
        return round(x * SS, 4), round(y * SS, 4)

    def draw_glass(self, d: ImageDraw.ImageDraw, cx: float, yb: float, ang: float, a: float) -> None:
        man = self.man
        hw_t = man["glass_width_m"] * self.ppm / 2.0
        hw_b = hw_t - 5.0
        h = man["glass_height_m"] * self.ppm
        cy = yb - h / 2.0
        ca, sa = math.cos(ang), math.sin(ang)

        def rot(px: float, py: float) -> tuple[float, float]:
            dx, dy = px, py - cy
            return self.L(cx + dx * ca - dy * sa, cy + dx * sa + dy * ca)

        body = [rot(-hw_b, yb), rot(hw_b, yb), rot(hw_t, yb - h), rot(-hw_t, yb - h)]
        lvl = 0.55
        hw_w = hw_b + (hw_t - hw_b) * lvl
        water = [rot(-hw_b + 3, yb - 3), rot(hw_b - 3, yb - 3), rot(hw_w - 3, yb - lvl * h), rot(-hw_w + 3, yb - lvl * h)]
        d.polygon(body, fill=blend(GLASS, a))
        d.polygon(water, fill=blend(WATER, a))
        d.polygon(body, outline=blend(GLASS_RIM, a), width=3 * SS)

    def draw_scene(self, d: ImageDraw.ImageDraw, panel: str, tau: float, a: float) -> dict:
        """The cloth, the glass, the mark and the arrow of one panel tau seconds into a cycle, blended by a."""
        man = self.man
        V = self.speeds[panel]
        r = (tau - self.pa) / self.S
        ys = float(SURFACE_DY)
        cl = man["cloth_px"]
        x_far = self.x_far0 + V * max(r, 0.0) * self.ppm
        run = self.runs[panel]
        x, v, ph = state_at(run, r)
        # The cloth: a band on the surface from its far edge to the frame's right edge, a two-colour
        # pattern every pattern_m so the motion reads; beyond the table edge it runs on to the puller.
        pat = man["pattern_m"] * self.ppm
        if x_far < W:
            j = 0
            while x_far + j * pat < W:
                x0, x1 = x_far + j * pat, min(W, x_far + (j + 1) * pat)
                col = CLOTH_A if j % 2 == 0 else CLOTH_B
                p0, p1 = self.L(x0, ys - cl), self.L(x1, ys)
                d.rectangle((p0[0], p0[1], p1[0], p1[1]), fill=blend(col, a))
                j += 1
            e0, e1 = self.L(x_far, ys - cl), self.L(x_far, ys)
            d.line((*e0, *e1), fill=blend(WHITE, 0.8 * a), width=2 * SS)
            if r >= 0.0:
                # The pull arrow beyond the table edge.
                ax0, ax1, ay = self.x_edge + 40.0, W - 30.0, ys - 34.0
                q0, q1 = self.L(ax0, ay), self.L(ax1 - 26, ay)
                d.line((*q0, *q1), fill=blend(CORAL, a), width=6 * SS)
                tip, b1, b2 = self.L(ax1, ay), self.L(ax1 - 30, ay - 16), self.L(ax1 - 30, ay + 16)
                d.polygon([tip, b1, b2], fill=blend(CORAL, a))
        # The start mark and the travel bar inside the slab.
        m0, m1, m2 = self.L(self.x_start, ys + 4), self.L(self.x_start - 9, ys + 20), self.L(self.x_start + 9, ys + 20)
        d.polygon([m0, m1, m2], fill=blend(GOLD, a, DECK_A))
        gx = self.x_start + min(x, man["edge_from_glass_m"]) * self.ppm
        if gx - self.x_start > 2.0:
            b0, b1 = self.L(self.x_start, ys + 29), self.L(gx, ys + 29)
            d.line((*b0, *b1), fill=blend(GOLD, 0.9 * a, DECK_A), width=4 * SS)
        # The glass: on the cloth while the cloth is under it, on the bare table after, tipping and
        # falling once its centre has passed the table edge (a projectile with a fixed spin, visual only).
        if ph == OFF:
            dtf = max(0.0, r - run["t_end"])
            cx = self.x_edge + V * dtf * self.ppm
            yb = ys - cl + 0.5 * man["g"] * dtf * dtf * self.ppm
            ang = man["fall_spin_rad_s"] * dtf
        else:
            cx = self.x_start + x * self.ppm
            yb = ys - cl if ph in (WAIT, SLIP, RIDE) else ys
            ang = 0.0
        self.draw_glass(d, cx, yb, ang, a)
        return {"x": x, "v": v, "phase": ph, "r": r, "alpha": a}

    def draw_panel(self, layer: Image.Image, panel: str, f: int) -> dict:
        man = self.man
        d = ImageDraw.Draw(layer)
        y0, y1 = self.band[panel]
        ys = float(SURFACE_DY)
        # The table: a slab from its left end to the edge, two legs, the edge face lit.
        s0, s1 = self.L(man["table_x0_px"], ys), self.L(self.x_edge, ys + SLAB_PX)
        d.rectangle((s0[0], s0[1], s1[0], s1[1]), fill=DECK_A)
        t0, t1 = self.L(man["table_x0_px"], ys), self.L(self.x_edge, ys)
        d.line((*t0, *t1), fill=DECK_B, width=3 * SS)
        e0, e1 = self.L(self.x_edge - 1, ys), self.L(self.x_edge - 1, ys + SLAB_PX)
        d.line((*e0, *e1), fill=RIM, width=3 * SS)
        for lx in (man["table_x0_px"] + 30, self.x_edge - 100):
            l0, l1 = self.L(lx, ys + SLAB_PX), self.L(lx + LEG_W, y1 - y0 - 24)
            d.rectangle((l0[0], l0[1], l1[0], l1[1]), fill=DECK_A)
        k, tau = self.phase(f)
        F, P = self.F, self.P
        a_old = 1.0 if tau <= P - F else max(0.0, (P - F / 2.0 - tau) / (F / 2.0))
        st = self.draw_scene(d, panel, tau, a_old) if a_old > 0.0 else None
        if tau >= P - F / 2.0:
            a_new = (tau - (P - F / 2.0)) / (F / 2.0)
            st_new = self.draw_scene(d, panel, tau - P, a_new)
            if st is None or a_new >= 0.5:
                st = st_new
        st["k"] = k
        return st

    def draw_text(self, d: ImageDraw.ImageDraw, states: dict, hud_alpha: float) -> None:
        man, ev = self.man, self.ev
        for panel, st in states.items():
            y0 = self.band[panel][0]
            a = st["alpha"]
            ph = st["phase"]
            d.text((ROW_X0, y0 + LABEL_DY), label_text(self.speeds[panel]), font=self.font, fill=TEXT, anchor="lm")
            final = ph in (OFF, REST)
            d.text((ROW_X1, y0 + LABEL_DY), readout_text(min(st["x"], man["edge_from_glass_m"])), font=self.font,
                   fill=blend(GOLD if final else TEXT, a), anchor="rm")
            d.text((ROW_X0, y0 + STATE_DY), STATE_WORDS[ph], font=self.font_small,
                   fill=blend(GOLD if final else MUTED, a), anchor="lm")
            d.text((ROW_X1, y0 + STATE_DY), speed_text(st["v"]), font=self.font_small, fill=blend(MUTED, a), anchor="rm")
            if hud_alpha > 0.02:
                d.text((ROW_X0, y0 + FIX_DY), fixed_text(ev, panel), font=self.font_small,
                       fill=blend(GOLD, 0.85 * hud_alpha), anchor="lm")
            ys = y0 + SURFACE_DY
            d.text((self.x_start, ys + SLAB_PX + 22), "start", font=self.font_small, fill=MUTED, anchor="mm")
            d.text((self.x_edge, ys + SLAB_PX + 22), "edge", font=self.font_small, fill=MUTED, anchor="mm")
        if hud_alpha > 0.02:
            d.text((W / 2, LEGEND_Y), legend_text(man), font=self.font, fill=blend(TEXT, hud_alpha), anchor="mm")
            d.text((W / 2, CLOCK_Y), clock_text(states["slow"]["r"]), font=self.font_small,
                   fill=blend(MUTED, hud_alpha), anchor="mm")

    def live_frame(self, f: int, title_alpha: float | None = None, hud_alpha: float = 0.0) -> np.ndarray:
        """Frame f with the geometry at f / fps; title_alpha and hud_alpha override the title and
        the legend/clock/fixed-line/card blend during the loop fade."""
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
        for panel in PANELS:
            y0, y1 = self.band[panel]
            layer = Image.new("RGB", (W * SS, (y1 - y0) * SS), BG)
            states[panel] = self.draw_panel(layer, panel, f)
            img.paste(layer.reduce(SS), (0, y0))
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
        wrap = self.live_frame(total, title_alpha=1.0, hud_alpha=0.0)   # the geometry one scene on, drawn live
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
    man = json.loads((ROOT / "projects/tablecloth/manifest.json").read_text())
    ev = measure(man)
    if "--measure-only" in sys.argv:
        return
    if "--frames" in sys.argv:
        times = [float(v) for v in sys.argv[sys.argv.index("--frames") + 1].split(",")]
        r = Renderer(man, ev)
        (ROOT / "media/tablecloth").mkdir(parents=True, exist_ok=True)
        for tv in times:
            Image.fromarray(r.frame_at(int(round(tv * man["fps"])))).save(ROOT / f"media/tablecloth/smoke-{tv}.png")
        print("smoke frames: " + ", ".join(f"{tv}" for tv in times))
        return
    Renderer(man, ev).render(ROOT / "media/tablecloth/footage.mp4")


if __name__ == "__main__":
    main()
