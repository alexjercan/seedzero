#!/usr/bin/env python3
"""Spinning glass: which comes first, a dry bottom or a spill?

Two panels on the same clock, the same glass drawn the same way at the same
scale, seen from the side as a cross-section: a straight-sided glass of
inner radius R and height H stands on a turntable platter; the top panel
holds a fill h of 4 cm of water, the bottom panel 6 cm. Both are spun up on
the same ramp: 0 rpm until ramp_start_s of video, then ramp_rpm_per_s each
second up to ramp_max_rpm, held to the end. The water turns with the glass
as one body (rigid rotation, the quasi-steady state after spin-up; real
water lags a glass that is spun up quickly, which is why the ramp is slow),
so its surface is the paraboloid z(r) = z0 + w^2 r^2 / (2 g) with the depth
rim to centre d = w^2 R^2 / (2 g). While the bottom is covered and nothing
has spilled the mean level is the fill: centre z0 = h - d / 2, rim z(R) = h
+ d / 2. The bottom bares when z0 reaches 0, at w = sqrt(4 g h) / R if the
glass has not spilled by then; the rim reaches H at w = sqrt(4 g (H - h)) /
R if the bottom is still covered. Past the dry point the water is a ring
r0 <= r <= R with z = (w^2 / (2 g)) (r^2 - r0^2) and the volume pi w^2 (R^2
- r0^2)^2 / (4 g); past the spill point the rim stays at H and the volume
shrinks to the most the glass can hold at w: pi R^2 (H - d / 2) while d <=
H, then pi g H^2 / w^2 (a ring with its rim at H). The ramp is monotone, so
the water at w is min(fill volume, capacity(w)) and every state is a closed
form of w alone; nothing is integrated. Deterministic, no seed.

Measured and printed: the two fill volumes, the event speeds of both
glasses by bisection on the state against the closed forms, the rim and
centre heights and the dry radius at the events, the spill history of the
6 cm glass (monotone, the millilitres gone by the time its bottom bares),
the no-spill wrong guess for the 6 cm glass, the half-full swap, the
volume under the surface by Simpson quadrature against the closed forms,
the heights table at the table speeds, the wider glass and the low fill
for the description, the Ekman spin-up note, the schedule in video time,
the on-screen text widths and the layout clearances.

usage: spinglass.py [--measure-only] [--frames t1,t2,...]
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
WATER = (36, 78, 128)
SURFACE = (110, 170, 220)
GLASS = (150, 164, 182)
INTERIOR = (18, 22, 28)
DECK_A = (30, 36, 46)
DECK_B = (42, 50, 62)
STEEL = (150, 160, 176)
DIAL = (26, 31, 40)
DIAL_RIM = (96, 108, 126)

# Layout: overlay at y 96..130 (captions.py), three title rows at y 186/244/302
# for the first seconds, then the legend at y 236 and the shared rpm readout at
# y 290; two bands stacked, the 4 cm glass in y 330..880 and the 6 cm glass in
# y 880..1430, each drawn at 2x in its own layer; each band has its label row
# 40 px under the band top (left), two readout rows at 84 and 120 (left column
# from x 40, right column to x 1040); the glass centred on x 540 with its rim
# RIM_DY under the band top and its floor 10 cm below at 36 px per cm, the floor
# plate, the platter and the spindle under it; the top-view dial beside the
# glass on the right; two gold event rows under the platter at 482 and 526;
# captions at caption_y 0.75 (y 1440..1530); the six-line card from y 1572 at
# a 48 px pitch.
LEGEND_Y, CLOCK_Y = 236, 290
TITLE_Y = (186, 244, 302)
SS = 2
PAYOFF_Y, PAYOFF_PITCH = 1572.0, 48
PANELS = ("shallow", "deep")
BAND_Y = {"shallow": 330, "deep": 880}
BAND_H = 550
LABEL_DY, ROW1_DY, ROW2_DY = 40, 84, 120
EVENT_DY = (482, 526)
ROW_X0, ROW_X1 = 40, 1040
GLASS_CX = 540.0
RIM_DY = 62.0
WALL = 8.0
PLATTER_HW, PLATTER_H = 210.0, 16.0
SPINDLE_HW, SPINDLE_H = 8.0, 10.0
DIAL_CX, DIAL_DY, DIAL_R = 930.0, 300.0, 58.0
PUDDLE_MAX = 140.0
COLOUR = {"shallow": TEAL, "deep": CORAL}


def blend(col, a: float, base=BG) -> tuple:
    a = max(0.0, min(1.0, a))
    return tuple(int(round(c * a + b * (1 - a))) for c, b in zip(col, base))


def rpm_to_omega(rpm: float) -> float:
    return rpm * 2.0 * math.pi / 60.0


def omega_to_rpm(w: float) -> float:
    return w * 60.0 / (2.0 * math.pi)


# --- measurement --------------------------------------------------------------
def capacity(w: float, R: float, Hg: float, g: float) -> float:
    """The most water the glass holds at w with its rim wet: the covered paraboloid with its rim at
    H while the depth d = w^2 R^2 / (2 g) is at most H, else the ring with its rim at H."""
    d = w * w * R * R / (2.0 * g)
    if d <= Hg:
        return math.pi * R * R * (Hg - 0.5 * d)
    return math.pi * g * Hg * Hg / (w * w)


def shape(V: float, w: float, R: float, g: float) -> tuple[float, float, float]:
    """(centre z0, rim zR, dry radius r0) of a volume V turning at w in a glass of radius R: the
    bottom is covered while the mean level V / (pi R^2) is at least half the depth d."""
    d = w * w * R * R / (2.0 * g)
    hm = V / (math.pi * R * R)
    if hm >= 0.5 * d:
        return hm - 0.5 * d, hm + 0.5 * d, 0.0
    s = 2.0 / w * math.sqrt(g * V / math.pi)          # R^2 - r0^2 from pi w^2 s^2 / (4 g) = V
    return 0.0, w * w * s / (2.0 * g), math.sqrt(max(0.0, R * R - s))


def state(h: float, w: float, R: float, Hg: float, g: float) -> dict:
    """The water of a fill h at w on a monotone ramp: its volume, what has spilled, the surface."""
    V0 = math.pi * R * R * h
    V = min(V0, capacity(w, R, Hg, g)) if w > 0.0 else V0
    z0, zR, r0 = shape(V, w, R, g)
    assert zR <= Hg + 1e-9, "the surface leaves the glass"
    return {"V": V, "V0": V0, "spilled": V0 - V, "z0": z0, "zR": zR, "r0": r0, "w": w,
            "dry": r0 > 0.0, "spilling": V < V0 - 1e-15}


def surface(st: dict, r: np.ndarray, g: float) -> np.ndarray:
    """z(r) of the surface, 0 on the dry disc."""
    w = st["w"]
    z = st["z0"] + w * w * r * r / (2.0 * g) if st["r0"] == 0.0 else (w * w / (2.0 * g)) * (r * r - st["r0"] ** 2)
    return np.where(r < st["r0"], 0.0, z)


def quadrature(st: dict, R: float, g: float, n: int) -> float:
    """The volume under the surface by Simpson's rule on 2 pi r z(r) over the wet radii."""
    r = np.linspace(st["r0"], R, 2 * n + 1)
    f = 2.0 * math.pi * r * surface(st, r, g)
    hstep = (R - st["r0"]) / (2 * n)
    return float(hstep / 3.0 * (f[0] + f[-1] + 4.0 * f[1:-1:2].sum() + 2.0 * f[2:-1:2].sum()))


def bisect_w(pred, lo: float, hi: float, n: int = 100) -> float:
    """The smallest w in (lo, hi) where pred(w) turns true (pred is false at lo, true at hi)."""
    assert not pred(lo) and pred(hi)
    for _ in range(n):
        mid = 0.5 * (lo + hi)
        if pred(mid):
            hi = mid
        else:
            lo = mid
    return hi


def closed_events(h: float, R: float, Hg: float, g: float) -> tuple[float, float]:
    """(w at which the bottom bares, w at which the rim reaches H) for a fill h on a monotone ramp."""
    if h <= 0.5 * Hg:
        w_dry = math.sqrt(4.0 * g * h) / R                   # covered, mean level h: z0 = h - d / 2 = 0
        w_spill = (Hg / R) * math.sqrt(g / h)                # the ring's rim w sqrt(V / (pi g)) = H
    else:
        w_spill = math.sqrt(4.0 * g * (Hg - h)) / R          # covered: h + d / 2 = H
        w_dry = math.sqrt(2.0 * g * Hg) / R                  # spilling with its rim at H: z0 = H - d = 0
    return w_dry, w_spill


def rpm_at(t: float, man: dict) -> float:
    t0, k, top = man["ramp_start_s"], man["ramp_rpm_per_s"], man["ramp_max_rpm"]
    if t <= t0:
        return 0.0
    return min(top, k * (t - t0))


def turns_at(t: float, man: dict) -> float:
    """The platter's angle in turns: the integral of the ramp."""
    t0, k, top = man["ramp_start_s"], man["ramp_rpm_per_s"], man["ramp_max_rpm"]
    t1 = t0 + top / k
    if t <= t0:
        return 0.0
    if t <= t1:
        return (k / 60.0) * (t - t0) ** 2 / 2.0
    return (k / 60.0) * (t1 - t0) ** 2 / 2.0 + (top / 60.0) * (t - t1)


def event_time(rpm: float, man: dict) -> float:
    return man["ramp_start_s"] + rpm / man["ramp_rpm_per_s"]


def measure(man: dict) -> dict:
    g, R, Hg = man["g"], man["glass_radius_m"], man["glass_height_m"]
    fills = man["fill_m"]
    D, fps = man["scene_duration"], man["fps"]
    t0, k, top = man["ramp_start_s"], man["ramp_rpm_per_s"], man["ramp_max_rpm"]
    t1 = t0 + top / k
    w_top = rpm_to_omega(top)
    ppc = man["px_per_cm"]
    for key in ("ramp_start_s", "scene_duration", "loop_fade"):
        assert abs(man[key] * fps - round(man[key] * fps)) < 1e-9, f"{key} must be a whole number of frames"
    assert t1 < D, "the ramp must end inside the scene"
    V0 = {m: math.pi * R * R * fills[m] for m in PANELS}
    print(f"setup: the same glass in both panels, seen from the side as a cross-section: a straight-sided glass of inner "
          f"radius R = {R * 100:g} cm ({2 * R * 100:g} cm across) and height H = {Hg * 100:g} cm on a turntable platter; "
          f"top panel {fills['shallow'] * 100:g} cm of water ({V0['shallow'] * 1e6:.1f} mL), bottom panel "
          f"{fills['deep'] * 100:g} cm ({V0['deep'] * 1e6:.1f} mL); both spun up on the same ramp: 0 rpm until {t0:g} s of "
          f"video, then {k:g} rpm per second to {top:g} rpm at {t1:g} s ({w_top:.3f} rad/s), held to the end at {D:g} s; the "
          f"water turns with the glass as one body (rigid rotation, the quasi-steady state after spin-up; real water lags a "
          f"glass that is spun up quickly, which is why the ramp is slow); its surface is the paraboloid z = z0 + w^2 r^2 / "
          f"(2 g) with the depth rim to centre d = w^2 R^2 / (2 g); while the bottom is covered and nothing has spilled "
          f"the mean level is the fill: centre z0 = h - w^2 R^2 / (4 g), rim h + w^2 R^2 / (4 g); past the dry point the "
          f"water is a ring r0 to R with z = (w^2 / (2 g)) (r^2 - r0^2) and volume pi w^2 (R^2 - r0^2)^2 / (4 g); past the "
          f"spill point the rim stays at H and the volume shrinks to the capacity pi R^2 (H - d / 2) while d <= H, then "
          f"pi g H^2 / w^2; the ramp is monotone, so the water at w is min(fill, capacity(w)) and every state is a closed "
          f"form of w alone, nothing integrated; g = {g:g} m/s^2; drawn at {ppc:g} px per cm (the glass {2 * R * 100 * ppc:.0f} "
          f"px wide inside and {Hg * 100 * ppc:.0f} px tall); deterministic, no seed")
    ev: dict = {"V0": V0, "fills": fills, "events": {}, "closed": {}}
    lines = []
    for m in PANELS:
        h = fills[m]
        wd_c, ws_c = closed_events(h, R, Hg, g)
        w_dry = bisect_w(lambda w: state(h, w, R, Hg, g)["z0"] <= 0.0, 0.0, w_top)
        w_spill = bisect_w(lambda w: state(h, w, R, Hg, g)["spilling"], 0.0, w_top)
        sd, ss_ = state(h, w_dry, R, Hg, g), state(h, w_spill, R, Hg, g)
        first = "the bottom shows first" if w_dry < w_spill else "it spills first"
        ev["events"][m] = {"w_dry": w_dry, "w_spill": w_spill, "rpm_dry": omega_to_rpm(w_dry),
                           "rpm_spill": omega_to_rpm(w_spill), "st_dry": sd, "st_spill": ss_, "first": first}
        ev["closed"][m] = {"w_dry": wd_c, "w_spill": ws_c}
        if w_dry < w_spill:
            lines.append(f"{h * 100:g} cm of water ({'top' if m == 'shallow' else 'bottom'} panel, {V0[m] * 1e6:.1f} mL): "
                         f"{first}: the centre reaches 0 at w = {w_dry:.3f} rad/s = {omega_to_rpm(w_dry):.1f} rpm = "
                         f"{omega_to_rpm(w_dry):.0f} rpm (closed form sqrt(4 g h) / R = {wd_c:.3f} rad/s = "
                         f"{omega_to_rpm(wd_c):.1f} rpm, diff {w_dry - wd_c:+.1e}), the rim then at {sd['zR'] * 100:.1f} cm "
                         f"= {sd['zR'] * 100:.0f} cm (2 h; the dip of {h * 100:.1f} cm equals the climb of "
                         f"{(sd['zR'] - h) * 100:.1f} cm), water {sd['V'] * 1e6:.1f} mL, nothing spilled; from then the "
                         f"water is a ring and the dry disc grows; the rim reaches H only at w = {w_spill:.3f} rad/s = "
                         f"{omega_to_rpm(w_spill):.1f} rpm = {omega_to_rpm(w_spill):.0f} rpm (closed form (H / R) "
                         f"sqrt(g / h) = {ws_c:.3f} rad/s = {omega_to_rpm(ws_c):.1f} rpm, diff {w_spill - ws_c:+.1e}) with "
                         f"the dry radius {ss_['r0'] * 100:.2f} cm = {ss_['r0'] * 100:.1f} cm of {R * 100:g} (dry disc "
                         f"{2 * ss_['r0'] * 100:.1f} cm across), the water still {ss_['V'] * 1e6:.1f} mL; at {top:g} rpm "
                         f"{state(h, w_top, R, Hg, g)['V'] * 1e6:.1f} mL remain, {state(h, w_top, R, Hg, g)['spilled'] * 1e6:.1f} "
                         f"mL spilled, dry radius {state(h, w_top, R, Hg, g)['r0'] * 100:.2f} cm")
        else:
            lines.append(f"{h * 100:g} cm of water ({'top' if m == 'shallow' else 'bottom'} panel, {V0[m] * 1e6:.1f} mL): "
                         f"{first}: the rim reaches H at w = {w_spill:.3f} rad/s = {omega_to_rpm(w_spill):.1f} rpm = "
                         f"{omega_to_rpm(w_spill):.0f} rpm (closed form sqrt(4 g (H - h)) / R = {ws_c:.3f} rad/s = "
                         f"{omega_to_rpm(ws_c):.1f} rpm, diff {w_spill - ws_c:+.1e}), the centre then at "
                         f"{ss_['z0'] * 100:.1f} cm = {ss_['z0'] * 100:.0f} cm (2 h - H; the climb of {(Hg - h) * 100:.1f} cm "
                         f"equals the dip of {(h - ss_['z0']) * 100:.1f} cm), water {ss_['V'] * 1e6:.1f} mL; from then the "
                         f"rim stays at H and the water leaves; the bottom shows at w = {w_dry:.3f} rad/s = "
                         f"{omega_to_rpm(w_dry):.1f} rpm = {omega_to_rpm(w_dry):.0f} rpm (closed form sqrt(2 g H) / R = "
                         f"{wd_c:.3f} rad/s = {omega_to_rpm(wd_c):.1f} rpm, diff {w_dry - wd_c:+.1e}), when "
                         f"{sd['V'] * 1e6:.1f} mL of {V0[m] * 1e6:.1f} mL remain (exactly half the glass, pi R^2 H / 2 = "
                         f"{math.pi * R * R * Hg / 2 * 1e6:.1f} mL) and {sd['spilled'] * 1e6:.1f} mL = "
                         f"{sd['spilled'] * 1e6:.0f} mL have spilled; at {top:g} rpm "
                         f"{state(h, w_top, R, Hg, g)['V'] * 1e6:.1f} mL remain, {state(h, w_top, R, Hg, g)['spilled'] * 1e6:.1f} "
                         f"mL spilled, dry radius {state(h, w_top, R, Hg, g)['r0'] * 100:.2f} cm")
        assert abs(w_dry - wd_c) < 1e-9 and abs(w_spill - ws_c) < 1e-9, "an event disagrees with its closed form"
    for ln in lines:
        print(ln)
    e4, e6 = ev["events"]["shallow"], ev["events"]["deep"]
    assert e4["w_dry"] < e4["w_spill"] and e6["w_spill"] < e6["w_dry"], "the panels must end differently"
    assert abs(e4["w_dry"] - e6["w_spill"]) < 1e-9, "the two first events must share one speed"
    # The wrong guess, the half-full swap.
    w_wrong = math.sqrt(4.0 * g * fills["deep"]) / R
    ev["rpm_wrong"] = omega_to_rpm(w_wrong)
    st_w = state(fills["deep"], w_wrong, R, Hg, g)
    print(f"wrong guess: sqrt(4 g h) / R with h = {fills['deep'] * 100:g} cm gives {w_wrong:.3f} rad/s = {ev['rpm_wrong']:.1f} "
          f"rpm for the bottom to show, the figure in the research entry; it ignores the spilled water (it would put the "
          f"rim at {2 * fills['deep'] * 100:.1f} cm, above the {Hg * 100:g} cm glass); with the spill the 6 cm glass has "
          f"only {st_w['V'] * 1e6:.1f} mL left at {ev['rpm_wrong']:.1f} rpm and its bottom has been dry since "
          f"{e6['rpm_dry']:.1f} rpm, so {e6['rpm_dry']:.1f} rpm is right and {ev['rpm_wrong']:.1f} rpm is wrong")
    hh = man["half_fill_m"]
    wdh, wsh = closed_events(hh, R, Hg, g)
    wdh_b = bisect_w(lambda w: state(hh, w, R, Hg, g)["z0"] <= 0.0, 0.0, w_top)
    wsh_b = bisect_w(lambda w: state(hh, w, R, Hg, g)["spilling"], 0.0, w_top)
    ev["rpm_half"] = omega_to_rpm(wdh_b)
    print(f"half full ({hh * 100:g} cm, {math.pi * R * R * hh * 1e6:.1f} mL): the swap; the bottom shows at {wdh_b:.3f} rad/s "
          f"= {omega_to_rpm(wdh_b):.1f} rpm and the rim reaches H at {wsh_b:.3f} rad/s = {omega_to_rpm(wsh_b):.1f} rpm, both "
          f"at once (closed forms {wdh:.3f} and {wsh:.3f} rad/s, diffs {wdh_b - wdh:+.1e} and {wsh_b - wsh:+.1e}; the "
          f"paraboloid depth w^2 R^2 / (2 g) = H = {Hg * 100:g} cm exactly); under half full the bottom shows first, over "
          f"half full it spills first")
    assert abs(wdh_b - wsh_b) < 1e-9 and abs(wdh_b - e6["w_dry"]) < 1e-9
    # The spill history of the deep glass and the shallow glass (monotone).
    rpms = np.arange(0.0, top + 1e-9, 0.1)
    hist = {m: np.array([state(fills[m], rpm_to_omega(r), R, Hg, g)["V"] for r in rpms]) for m in PANELS}
    for m in PANELS:
        assert np.all(np.diff(hist[m]) <= 1e-15), "the water must never increase"
    marks = []
    for r in (300.0, 341.8, 350.0, 360.0, 370.0, 382.1, 400.0, 418.6, 427.2, 450.0):
        s6 = state(fills["deep"], rpm_to_omega(r), R, Hg, g)
        s4 = state(fills["shallow"], rpm_to_omega(r), R, Hg, g)
        marks.append(f"{r:g} rpm: 6 cm {s6['V'] * 1e6:.1f} mL ({s6['spilled'] * 1e6:.1f} gone), 4 cm {s4['V'] * 1e6:.1f} mL "
                     f"({s4['spilled'] * 1e6:.1f} gone)")
    print(f"spill history (the water at each speed, {len(rpms)} samples at 0.1 rpm from 0 to {top:g} rpm, monotone "
          f"non-increasing in both glasses): " + "; ".join(marks) + f"; the 6 cm glass has lost {e6['st_dry']['spilled'] * 1e6:.1f} "
          f"mL by {e6['rpm_dry']:.1f} rpm; above {e4['rpm_spill']:.1f} rpm both glasses hold the same water, pi g H^2 / w^2, "
          f"{state(fills['deep'], w_top, R, Hg, g)['V'] * 1e6:.1f} mL each at {top:g} rpm")
    # Quadrature of the volume under the surface against the closed forms.
    n = man["quadrature_intervals"]
    worst = 0.0
    qlines = []
    for r in man["quadrature_rpm"]:
        for m in PANELS:
            st = state(fills[m], rpm_to_omega(r), R, Hg, g)
            q = quadrature(st, R, g, n)
            worst = max(worst, abs(q - st["V"]))
            qlines.append(f"{m} {r:g} rpm {q * 1e6:.6f} mL vs {st['V'] * 1e6:.6f} ({(q - st['V']) * 1e6:+.1e})")
    print(f"quadrature: Simpson's rule with {n} intervals on 2 pi r z(r) over the wet radii against the closed-form volume "
          f"(the fill before any spill, the ring formula past the dry point, the capacity past the spill point): worst "
          f"{worst * 1e6:.2e} mL = {worst * 1e3:.2e} L, within 1e-6 L; " + "; ".join(qlines))
    assert worst < 1e-9, "the quadrature disagrees with the closed-form volume"
    # The heights table.
    rows = []
    for r in man["table_rpm"]:
        w = rpm_to_omega(r)
        parts = []
        for m in PANELS:
            st = state(fills[m], w, R, Hg, g)
            parts.append(f"{fills[m] * 100:g} cm: centre {st['z0'] * 100:.1f} cm, rim {st['zR'] * 100:.1f} cm"
                         + (f", dry radius {st['r0'] * 100:.2f} cm" if st["dry"] else "")
                         + f", water {st['V'] * 1e6:.1f} mL")
        rows.append(f"{r:g} rpm ({w:.3f} rad/s, depth {w * w * R * R / (2 * g) * 100:.1f} cm): " + "; ".join(parts))
    print("table (rim and centre heights): " + " | ".join(rows))
    # For the description: the wider glass and the low fill, and the spin-up note.
    R2 = man["description_wide_radius_m"]
    wd2, ws2 = closed_events(fills["shallow"], R2, Hg, g)
    h3 = man["description_low_fill_m"]
    wd3, ws3 = closed_events(h3, R, Hg, g)
    ev["rpm_wide"], ev["rpm_low_dry"], ev["rpm_low_spill"] = omega_to_rpm(wd2), omega_to_rpm(wd3), omega_to_rpm(ws3)
    nu = man["water_viscosity_m2_s"]
    ek = {m: fills[m] / math.sqrt(nu * e4["w_dry"]) for m in PANELS}
    print(f"for the description: a wider glass, R = {R2 * 100:g} cm ({2 * R2 * 100:g} cm across), with {fills['shallow'] * 100:g} "
          f"cm: bottom dry at {wd2:.3f} rad/s = {omega_to_rpm(wd2):.1f} rpm (rim then {2 * fills['shallow'] * 100:.1f} cm), "
          f"spills at {omega_to_rpm(ws2):.1f} rpm; the {R * 100:g} cm glass with {h3 * 100:g} cm ({math.pi * R * R * h3 * 1e6:.1f} "
          f"mL): dry at {wd3:.3f} rad/s = {omega_to_rpm(wd3):.1f} rpm (rim then {2 * h3 * 100:.1f} cm), spills at {ws3:.3f} "
          f"rad/s = {omega_to_rpm(ws3):.1f} rpm; the dry speed scales as sqrt(h) / R and the spill speed of an under-half "
          f"fill as 1 / (R sqrt(h)); spin-up note (not drawn): water spun up suddenly takes about h / sqrt(nu w) to catch up "
          f"with the glass (Ekman spin-up, nu = {nu:g} m^2/s): {ek['shallow']:.1f} s for {fills['shallow'] * 100:g} cm and "
          f"{ek['deep']:.1f} s for {fills['deep'] * 100:g} cm at {e4['rpm_dry']:.1f} rpm, so the ramp of {t1 - t0:g} s at "
          f"{k:g} rpm per second is slow against it and the rigid-rotation surface is the quasi-steady state")
    # Brief checks.
    checks = [
        ("4 cm bottom dry (rpm)", 341.8, e4["rpm_dry"], 1), ("4 cm bottom dry (rad/s)", 35.790, e4["w_dry"], 3),
        ("4 cm rim then (cm)", 8.0, e4["st_dry"]["zR"] * 100, 1), ("4 cm spill (rpm)", 427.2, e4["rpm_spill"], 1),
        ("4 cm dry radius at the spill (cm)", 1.57, e4["st_spill"]["r0"] * 100, 2),
        ("6 cm spill (rpm)", 341.8, e6["rpm_spill"], 1), ("6 cm centre then (cm)", 2.0, e6["st_spill"]["z0"] * 100, 1),
        ("6 cm bottom dry (rpm)", 382.1, e6["rpm_dry"], 1), ("6 cm bottom dry (rad/s)", 40.014, e6["w_dry"], 3),
        ("6 cm left then (mL)", 192.4, e6["st_dry"]["V"] * 1e6, 1), ("6 cm spilled then (mL)", 38.5, e6["st_dry"]["spilled"] * 1e6, 1),
        ("5 cm both (rpm)", 382.1, ev["rpm_half"], 1), ("6 cm no-spill wrong guess (rpm)", 418.6, ev["rpm_wrong"], 1),
        ("4 cm volume (mL)", 153.9, V0["shallow"] * 1e6, 1), ("6 cm volume (mL)", 230.9, V0["deep"] * 1e6, 1),
        ("9 cm glass, 4 cm: dry (rpm)", 265.8, ev["rpm_wide"], 1), ("2 cm fill: dry (rpm)", 241.7, ev["rpm_low_dry"], 1),
        ("2 cm fill: spill (rpm)", 604.1, ev["rpm_low_spill"], 1),
        ("341.8 rpm at (s)", 25.79, event_time(e4["rpm_dry"], man), 2),
        ("382.1 rpm at (s)", 28.47, event_time(e6["rpm_dry"], man), 2),
        ("427.2 rpm at (s)", 31.48, event_time(e4["rpm_spill"], man), 2),
    ]
    # Agreement at the brief's precision, or within one unit of its last digit where the brief rounded a
    # rounded figure (341.8 / 15 against the exact 341.76 / 15; 604.1 against the exact 604.18).
    grades = []
    for _, b, v, p in checks:
        err = abs(v - b)
        grades.append("ok" if err < 0.5 * 10 ** -p + 1e-12 else "ok within one unit of the brief's last digit"
                      if err < 1.1 * 10 ** -p else "DIFFERS")
    exact = sum(gr == "ok" for gr in grades)
    print(f"brief checks ({exact} of {len(checks)} agree at the brief's precision, "
          f"{sum(gr != 'DIFFERS' for gr in grades)} of {len(checks)} within one unit of its last digit): "
          + "; ".join(f"{name}: brief {b:g}, sim {v:.{p + 1}f} ({gr})" for (name, b, v, p), gr in zip(checks, grades)))
    assert all(gr != "DIFFERS" for gr in grades), "a brief check differs"
    # The schedule in video time.
    ev["t"] = {"dry4": event_time(e4["rpm_dry"], man), "spill4": event_time(e4["rpm_spill"], man),
               "spill6": event_time(e6["rpm_spill"], man), "dry6": event_time(e6["rpm_dry"], man), "ramp_end": t1}
    b0, b1 = man["blur_rpm"]
    print(f"schedule (video time, real time): both glasses at rest until {t0:g} s, then {k:g} rpm per second; "
          f"{b0:g} rpm at {event_time(b0, man):.2f} s and {b1:g} rpm at {event_time(b1, man):.2f} s (the dial's mark blurs "
          f"to a ring between them, {b0 / 60:.2f} to {b1 / 60:.2f} turns per second of video); the 4 cm glass bares its bottom "
          f"and the 6 cm glass reaches its rim at {e4['rpm_dry']:.1f} rpm at {ev['t']['dry4']:.2f} s (both first event rows "
          f"light); the 6 cm glass bares its bottom at {e6['rpm_dry']:.1f} rpm at {ev['t']['dry6']:.2f} s (its second row "
          f"lights); the 4 cm glass reaches its rim at {e4['rpm_spill']:.1f} rpm at {ev['t']['spill4']:.2f} s (its second "
          f"row lights); the ramp reaches {top:g} rpm at {t1:g} s and holds (the streaks stop, the puddles stay); the platter "
          f"turns {turns_at(D, man):.2f} turns in all ({turns_at(t1, man):.2f} on the ramp); on the first frame both glasses "
          f"are at rest with their still levels; title until {man['title_until']:g} s; payoff card from {man['payoff_t']:g} s; "
          f"single run: over the last {man['loop_fade']:g} s the scene crossfades back to the first frame (the readouts "
          f"and the card out over its first half, the title in over its second) and the last frame repeats the first")
    # Text widths.
    font = os.environ["SEED_ZERO_FONT"]
    f24, f28, f34, f40, f56 = (ImageFont.truetype(font, n) for n in (24, 28, 34, 40, 56))
    widths = {"overlay@34": (f34, man["overlay"])}
    for j, line in enumerate(man["title"].split("|")):
        widths[f"title line {j + 1}@56"] = (f56, line)
    widths["legend@40"] = (f40, legend_text(man))
    widths["clock rest@28"] = (f28, clock_text(0.0, man))
    widths["clock ramp@28"] = (f28, clock_text(20.0, man))
    widths["clock held@28"] = (f28, clock_text(35.0, man))
    for m in PANELS:
        widths[f"label {m}@40"] = (f40, label_text(man, m))
        for j, line in enumerate(event_texts(ev, m)):
            widths[f"event {m} row {j + 1}@40"] = (f40, line)
    st_ex = state(fills["deep"], rpm_to_omega(300.0), R, Hg, g)
    widths["rpm row@28"] = (f28, rpm_text(450.0))
    widths["centre row@28"] = (f28, centre_text(st_ex))
    widths["centre dry row@28"] = (f28, centre_text(e4["st_spill"]))
    widths["rim row@28"] = (f28, rim_text(st_ex))
    widths["water row@28"] = (f28, water_text(state(fills["deep"], 0.0, R, Hg, g)))
    widths["dial tag@24"] = (f24, dial_text())
    widths["rim tag@24"] = (f24, rim_tag(man))
    widths["fill tag shallow@24"] = (f24, fill_tag(man, "shallow"))
    widths["fill tag deep@24"] = (f24, fill_tag(man, "deep"))
    for j, line in enumerate(payoff_lines(man, ev)):
        widths[f"payoff line {j + 1}@40"] = (f40, line)
    print("text widths (the on-screen strings verbatim): " + ", ".join(f"{kk} {f.getlength(s):.0f} px '{s}'"
                                                                       for kk, (f, s) in widths.items()))
    assert all(f.getlength(s) < 950 for f, s in widths.values()), "a text line is wider than 950 px"
    assert len(payoff_lines(man, ev)) <= 6, "the card has more than six lines"
    assert len(man["title"].split("|")) <= 3, "the title has more than three rows"
    # Layout checks.
    Rpx = R * 100 * ppc
    gx0, gx1 = GLASS_CX - Rpx - WALL, GLASS_CX + Rpx + WALL
    floor = RIM_DY + Hg * 100 * ppc
    plate = floor + WALL
    platter_y1 = plate + PLATTER_H
    spindle_y1 = platter_y1 + SPINDLE_H
    left = ROW_X0 + max(f40.getlength(label_text(man, m)) for m in PANELS)
    left = max(left, ROW_X0 + f28.getlength(rpm_text(450.0)), ROW_X0 + f28.getlength(centre_text(e4["st_spill"])),
               ROW_X0 + f28.getlength(centre_text(st_ex)))
    right = ROW_X1 - max(f28.getlength(rim_text(st_ex)), f28.getlength(water_text(state(fills["deep"], 0.0, R, Hg, g))))
    rows_bottom = ROW2_DY + 14
    ev_w = max(f40.getlength(s) for m in PANELS for s in event_texts(ev, m))
    ev_x0, ev_x1 = W / 2.0 - ev_w / 2.0, W / 2.0 + ev_w / 2.0
    tag_x1 = gx1 + 10 + max(f24.getlength(rim_tag(man)), f24.getlength(fill_tag(man, "deep")))
    puddle_x1 = gx1 + PUDDLE_MAX
    print(f"row check: the left column ends at x {left:.0f} px and the right column starts at x {right:.0f} px; the rows end "
          f"{rows_bottom} px under the band top; the glass spans x {gx0:.0f} to {gx1:.0f} px (inner {GLASS_CX - Rpx:.0f} to "
          f"{GLASS_CX + Rpx:.0f}) from its rim at {RIM_DY:.0f} px under the band top to its floor at {floor:.0f}, the floor "
          f"plate to {plate:.0f}, the platter (x {GLASS_CX - PLATTER_HW:.0f} to {GLASS_CX + PLATTER_HW:.0f}) to "
          f"{platter_y1:.0f} and the spindle to {spindle_y1:.0f}; the puddles reach x {gx0 - PUDDLE_MAX:.0f} and "
          f"{puddle_x1:.0f} at most on the platter top; the rim and fill tags sit right of the glass to x {tag_x1:.0f}; the "
          f"dial is centred at x {DIAL_CX:.0f}, {DIAL_DY:.0f} px under the band top with radius {DIAL_R:.0f} (y "
          f"{DIAL_DY - DIAL_R:.0f} to {DIAL_DY + DIAL_R + 30:.0f} with its tag, x {DIAL_CX - DIAL_R:.0f} to "
          f"{DIAL_CX + DIAL_R:.0f}); the event rows are centred {EVENT_DY[0]} and {EVENT_DY[1]} px under the band top (from "
          f"{EVENT_DY[0] - 22} to {EVENT_DY[1] + 22}) and span x {ev_x0:.0f} to {ev_x1:.0f} px (widest {ev_w:.0f} px); the "
          f"surface never rises above the rim (asserted in every state); each band is {BAND_H} px tall (y {BAND_Y['shallow']} "
          f"to {BAND_Y['shallow'] + BAND_H} and {BAND_Y['deep']} to {BAND_Y['deep'] + BAND_H}); the caption band starts at y "
          f"{int(man['caption_y'] * H)}; the title rows end at y {TITLE_Y[-1] + 28} and the overlay band ends at y 130")
    assert left < gx0 - 16, "the left column meets the glass"
    assert right > gx1 + 16, "the right column meets the glass"
    assert right - left > 40, "the columns meet"
    assert RIM_DY >= LABEL_DY + 20, "the rim meets the label row"
    assert spindle_y1 < EVENT_DY[0] - 22 - 2, "the spindle meets the event rows"
    assert EVENT_DY[1] + 22 < BAND_H, "the second event row leaves the band"
    assert EVENT_DY[1] - EVENT_DY[0] >= 44, "the event rows overlap"
    assert DIAL_DY - DIAL_R > rows_bottom + 10, "the dial meets the readout rows"
    assert DIAL_CX - DIAL_R > tag_x1 + 10, "the dial meets the tags"
    assert DIAL_DY + DIAL_R + 30 < plate - 4, "the dial tag reaches the platter line"
    assert puddle_x1 < W - 8 and gx0 - PUDDLE_MAX > 8, "a puddle leaves the band sideways"
    assert TITLE_Y[-1] + 28 <= BAND_Y["shallow"], "the title rows reach the first band"
    assert BAND_Y["deep"] + BAND_H <= int(man["caption_y"] * H), "the bottom band reaches the caption band"
    assert PAYOFF_Y - 20 > int(man["caption_y"] * H) + 90, "the card meets the caption band"
    return ev


def legend_text(man: dict) -> str:
    return f"same glass, same ramp, {man['ramp_rpm_per_s']:g} rpm a second"


def clock_text(t: float, man: dict) -> str:
    rpm = rpm_at(t, man)
    if t <= man["ramp_start_s"]:
        return "at rest"
    if rpm >= man["ramp_max_rpm"]:
        return f"held at {rpm:.0f} turns a minute"
    return f"spinning up, {rpm:.0f} turns a minute"


def label_text(man: dict, m: str) -> str:
    return f"{man['fill_m'][m] * 100:g} cm of water"


def rpm_text(rpm: float) -> str:
    return f"{rpm:.0f} turns a minute"


def centre_text(st: dict) -> str:
    return "center dry" if st["dry"] else f"center {st['z0'] * 100:.1f} cm"


def rim_text(st: dict) -> str:
    return f"rim {st['zR'] * 100:.1f} cm"


def water_text(st: dict) -> str:
    return f"water {st['V'] * 1e6:.0f} mL"


def dial_text() -> str:
    return "top view"


def rim_tag(man: dict) -> str:
    return f"rim {man['glass_height_m'] * 100:g} cm"


def fill_tag(man: dict, m: str) -> str:
    return f"still {man['fill_m'][m] * 100:g} cm"


def event_texts(ev: dict, m: str) -> list[str]:
    e = ev["events"][m]
    if m == "shallow":
        return [f"bottom shows at {e['rpm_dry']:.0f} rpm, rim at {e['st_dry']['zR'] * 100:.0f} cm",
                f"spills at {e['rpm_spill']:.0f} rpm"]
    return [f"spills at {e['rpm_spill']:.0f} rpm, center {e['st_spill']['z0'] * 100:.0f} cm",
            f"bottom shows at {e['rpm_dry']:.0f} rpm, {e['st_dry']['spilled'] * 1e6:.0f} mL gone"]


def payoff_lines(man: dict, ev: dict) -> list[str]:
    e4, e6 = ev["events"]["shallow"], ev["events"]["deep"]
    text = man["payoff_text"].format(
        rpm_dry4=e4["rpm_dry"], rim4=e4["st_dry"]["zR"] * 100, rpm_spill6=e6["rpm_spill"], z06=e6["st_spill"]["z0"] * 100,
        rpm_spill4=e4["rpm_spill"], rpm_dry6=e6["rpm_dry"], gone6=e6["st_dry"]["spilled"] * 1e6, rpm_half=ev["rpm_half"])
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
        self.g, self.R, self.Hg = man["g"], man["glass_radius_m"], man["glass_height_m"]
        self.ppc = float(man["px_per_cm"])
        self.Rpx = self.R * 100 * self.ppc
        self.floor = RIM_DY + self.Hg * 100 * self.ppc
        self.plate = self.floor + WALL
        self.platter_y1 = self.plate + PLATTER_H
        self.t_end = man["ramp_start_s"] + man["ramp_max_rpm"] / man["ramp_rpm_per_s"]
        # The 2x column grid across the inner glass, in metres from the axis.
        self.cols = np.arange(-int(self.Rpx * SS), int(self.Rpx * SS) + 1)
        self.r_cols = np.abs(self.cols) / (SS * self.ppc * 100.0)

    @staticmethod
    def L_(x: float, y: float) -> tuple[float, float]:
        """Layer (2x) pixel of a band-local point, rounded to 1e-4 px so equal states draw equal pixels."""
        return round(x * SS, 4), round(y * SS, 4)

    def zy(self, z: float) -> float:
        """Band-local y of a height z (metres) above the glass floor."""
        return self.floor - z * 100.0 * self.ppc

    def dashed(self, d: ImageDraw.ImageDraw, x0: float, x1: float, y: float, col, dash: float = 10.0, width: int = 2) -> None:
        x = x0
        while x < x1:
            p0, p1 = self.L_(x, y), self.L_(min(x + dash, x1), y)
            d.line((*p0, *p1), fill=col, width=width * SS)
            x += 2.0 * dash

    def draw_platter(self, d: ImageDraw.ImageDraw) -> None:
        cx = GLASS_CX
        p0, p1 = self.L_(cx - PLATTER_HW, self.plate), self.L_(cx + PLATTER_HW, self.platter_y1)
        d.rounded_rectangle((p0[0], p0[1], p1[0], p1[1]), radius=5 * SS, fill=DECK_A)
        t0, t1 = self.L_(cx - PLATTER_HW + 6, self.plate + 1), self.L_(cx + PLATTER_HW - 6, self.plate + 1)
        d.line((*t0, *t1), fill=DECK_B, width=3 * SS)
        s0, s1 = self.L_(cx - SPINDLE_HW, self.platter_y1), self.L_(cx + SPINDLE_HW, self.platter_y1 + SPINDLE_H)
        d.rectangle((s0[0], s0[1], s1[0], s1[1]), fill=STEEL)

    def draw_glass(self, d: ImageDraw.ImageDraw, st: dict, m: str, spill_a: float, f: int) -> None:
        cx, Rpx = GLASS_CX, self.Rpx
        g = self.g
        # The interior, then the water as the filled region between the floor (or the dry disc) and the surface.
        i0, i1 = self.L_(cx - Rpx, RIM_DY), self.L_(cx + Rpx, self.floor)
        d.rectangle((i0[0], i0[1], i1[0], i1[1]), fill=INTERIOR)
        z = surface(st, self.r_cols, g)
        xs = cx * SS + self.cols                    # 2x layer x of each column
        ys = (self.floor - z * 100.0 * self.ppc) * SS
        wet = self.r_cols >= st["r0"] if st["dry"] else np.ones_like(self.r_cols, dtype=bool)
        # Split the wet columns into runs (one run when covered, two lobes when the bottom is dry).
        idx = np.nonzero(wet)[0]
        if len(idx):
            breaks = np.nonzero(np.diff(idx) > 1)[0]
            runs = np.split(idx, breaks + 1)
            fl = self.floor * SS
            for run in runs:
                if len(run) < 2:
                    continue
                pts = [(float(xs[run[0]]), fl)] + [(float(xs[i]), float(ys[i])) for i in run] + [(float(xs[run[-1]]), fl)]
                d.polygon(pts, fill=WATER)
                d.line([(float(xs[i]), float(ys[i])) for i in run], fill=SURFACE, width=2 * SS)
        # The still level (muted dashes) and the rim height (gold dashes) across the interior.
        self.dashed(d, cx - Rpx + 4, cx + Rpx - 4, self.zy(self.man["fill_m"][m]), blend(MUTED, 0.7), 8.0, 1)
        self.dashed(d, cx - Rpx + 4, cx + Rpx - 4, RIM_DY + 1.5, blend(GOLD, 0.85), 8.0, 1)
        # The walls and the floor plate.
        for x0, x1 in ((cx - Rpx - WALL, cx - Rpx), (cx + Rpx, cx + Rpx + WALL)):
            w0, w1 = self.L_(x0, RIM_DY - 2), self.L_(x1, self.plate)
            d.rectangle((w0[0], w0[1], w1[0], w1[1]), fill=GLASS)
        f0, f1 = self.L_(cx - Rpx - WALL, self.floor), self.L_(cx + Rpx + WALL, self.plate)
        d.rectangle((f0[0], f0[1], f1[0], f1[1]), fill=GLASS)
        # Spill: thin streaks down the outside of both walls while the water is leaving, a puddle that grows.
        if st["spilled"] > 0.0:
            pw = min(PUDDLE_MAX, 12.0 + st["spilled"] * 1e6 * 1.4)
            for sgn in (-1.0, 1.0):
                xa = cx + sgn * (Rpx + WALL)
                xb = xa + sgn * pw
                q0, q1 = self.L_(min(xa, xb), self.plate - 5), self.L_(max(xa, xb), self.plate + 1)
                d.ellipse((q0[0], q0[1] - 0, q1[0], q1[1]), fill=blend(TEAL, 0.9))
        if spill_a > 0.0:
            col = blend(TEAL, 0.75 * spill_a)
            for sgn in (-1.0, 1.0):
                x = cx + sgn * (Rpx + WALL + 2.0)
                l0, l1 = self.L_(x, RIM_DY), self.L_(x, self.plate - 4)
                d.line((*l0, *l1), fill=col, width=2 * SS)
                span = self.plate - 4 - RIM_DY
                for kk in range(4):
                    yd = RIM_DY + ((f * 7.0 + kk * 90.0) % span)
                    d0, d1 = self.L_(x, yd), self.L_(x, min(yd + 14.0, self.plate - 4))
                    d.line((*d0, *d1), fill=blend(SURFACE, 0.95 * spill_a), width=3 * SS)

    def draw_dial(self, d: ImageDraw.ImageDraw, turns: float, rpm: float) -> None:
        """The platter seen from above: a disc with one mark whose angle is the integrated spin; the mark
        blurs to a ring between the blur speeds."""
        cx, cy, r = DIAL_CX, DIAL_DY, DIAL_R
        c0, c1 = self.L_(cx - r, cy - r), self.L_(cx + r, cy + r)
        d.ellipse((c0[0], c0[1], c1[0], c1[1]), fill=DIAL, outline=DIAL_RIM, width=2 * SS)
        b0, b1 = self.man["blur_rpm"]
        ring = max(0.0, min(1.0, (rpm - b0) / (b1 - b0)))
        a = 2.0 * math.pi * (turns % 1.0)          # clockwise on screen
        ri, ro = 0.30 * r, 0.88 * r
        if ring < 1.0:
            ma = 1.0 - ring
            p0 = self.L_(cx + ri * math.sin(a), cy - ri * math.cos(a))
            p1 = self.L_(cx + ro * math.sin(a), cy - ro * math.cos(a))
            d.line((*p0, *p1), fill=blend(GOLD, ma, DIAL), width=4 * SS)
            px, py = cx + ro * math.sin(a), cy - ro * math.cos(a)
            e0, e1 = self.L_(px - 5, py - 5), self.L_(px + 5, py + 5)
            d.ellipse((e0[0], e0[1], e1[0], e1[1]), fill=blend(GOLD, ma, DIAL))
        if ring > 0.0:
            rm = 0.5 * (ri + ro)
            q0, q1 = self.L_(cx - rm, cy - rm), self.L_(cx + rm, cy + rm)
            d.ellipse((q0[0], q0[1], q1[0], q1[1]), outline=blend(GOLD, 0.55 * ring, DIAL), width=int((ro - ri) * SS))
        h0, h1 = self.L_(cx - 4, cy - 4), self.L_(cx + 4, cy + 4)
        d.ellipse((h0[0], h0[1], h1[0], h1[1]), fill=STEEL)

    def scene(self, m: str, t: float, f: int) -> tuple[Image.Image, dict]:
        """The band layer of panel m at video time t."""
        layer = Image.new("RGB", (W * SS, BAND_H * SS), BG)
        d = ImageDraw.Draw(layer)
        rpm = rpm_at(t, self.man)
        st = state(self.man["fill_m"][m], rpm_to_omega(rpm), self.R, self.Hg, self.g)
        st["t"], st["rpm"] = t, rpm
        # Streaks while the water is leaving: from the spill speed until the ramp ends, fading out after.
        e = self.ev["events"][m]
        t_sp = event_time(e["rpm_spill"], self.man)
        if st["spilled"] > 0.0 and t <= self.t_end:
            spill_a = min(1.0, (t - t_sp) / 0.25)
        elif st["spilled"] > 0.0:
            spill_a = max(0.0, 1.0 - (t - self.t_end) / 0.4)
        else:
            spill_a = 0.0
        self.draw_platter(d)
        self.draw_glass(d, st, m, spill_a, f)
        self.draw_dial(d, turns_at(t, self.man), rpm)
        return layer, st

    def draw_text(self, d: ImageDraw.ImageDraw, states: dict, hud_alpha: float) -> None:
        man, ev = self.man, self.ev
        for m, st in states.items():
            y0 = BAND_Y[m]
            a = st["alpha"]
            d.text((ROW_X0, y0 + LABEL_DY), label_text(man, m), font=self.font, fill=COLOUR[m], anchor="lm")
            d.text((ROW_X0, y0 + ROW1_DY), rpm_text(st["rpm"]), font=self.font_small, fill=blend(TEXT, a), anchor="lm")
            d.text((ROW_X0, y0 + ROW2_DY), centre_text(st), font=self.font_small,
                   fill=blend(GOLD if st["dry"] else MUTED, a), anchor="lm")
            d.text((ROW_X1, y0 + ROW1_DY), rim_text(st), font=self.font_small,
                   fill=blend(GOLD if st["spilled"] > 0.0 else MUTED, a), anchor="rm")
            d.text((ROW_X1, y0 + ROW2_DY), water_text(st), font=self.font_small,
                   fill=blend(GOLD if st["spilled"] > 0.0 else MUTED, a), anchor="rm")
            # The rim and still-level tags right of the glass, the dial tag under the dial.
            gx1 = GLASS_CX + self.Rpx + WALL
            d.text((gx1 + 10, y0 + RIM_DY + 1), rim_tag(man), font=self.font_tiny, fill=blend(GOLD, 0.85), anchor="lm")
            d.text((gx1 + 10, y0 + self.zy(man["fill_m"][m])), fill_tag(man, m), font=self.font_tiny, fill=MUTED, anchor="lm")
            d.text((DIAL_CX, y0 + DIAL_DY + DIAL_R + 18), dial_text(), font=self.font_tiny, fill=MUTED, anchor="mm")
            e = ev["events"][m]
            t_first = event_time(min(e["rpm_dry"], e["rpm_spill"]), man)
            t_second = event_time(max(e["rpm_dry"], e["rpm_spill"]), man)
            for j, (tt, line) in enumerate(zip((t_first, t_second), event_texts(ev, m))):
                if st["t"] >= tt:
                    d.text((W / 2, y0 + EVENT_DY[j]), line, font=self.font, fill=blend(GOLD, a), anchor="mm")
        if hud_alpha > 0.02:
            d.text((W / 2, LEGEND_Y), legend_text(man), font=self.font, fill=blend(TEXT, hud_alpha), anchor="mm")
            d.text((W / 2, CLOCK_Y), clock_text(states["shallow"]["t"], man), font=self.font_small,
                   fill=blend(MUTED, hud_alpha), anchor="mm")

    def live_frame(self, f: int, title_alpha: float | None = None, hud_alpha: float = 0.0, back: float = 0.0) -> np.ndarray:
        """Frame f with the geometry at f / fps; title_alpha and hud_alpha override the title and the
        legend/readout/card blend during the loop fade, and back blends the scene toward the first frame."""
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
            layer, st = self.scene(m, t, f)
            st["alpha"] = 1.0
            if back > 0.0:
                first, st0 = self.scene(m, 0.0, 0)
                layer = Image.blend(layer, first, back)
                st["alpha"] = max(0.0, 1.0 - 2.0 * back)
                st0["alpha"] = max(0.0, 2.0 * back - 1.0)
                if back >= 0.5:
                    st = st0
            states[m] = st
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
            return self.live_frame(0)   # the last frame repeats the first
        if f >= total - fade_frames:
            # Single run: the scene crossfades back to the first frame; the legend, readouts and card
            # fade out over the first half of the loop fade and the title fades in over the second half.
            a = (f - (total - fade_frames) + 1) / fade_frames
            return self.live_frame(f, title_alpha=max(0.0, 2.0 * a - 1.0), hud_alpha=max(0.0, 1.0 - 2.0 * a), back=a)
        return self.live_frame(f)

    def render(self, out_path: Path) -> None:
        global _RENDERER
        out_path.parent.mkdir(parents=True, exist_ok=True)
        total = int(round(self.man["scene_duration"] * self.fps))
        fade_frames = int(round(self.man["loop_fade"] * self.fps))
        first = self.frame_at(0)
        last = self.frame_at(total - 1)
        diff = np.abs(first.astype(int) - last.astype(int))
        print(f"loop check: last frame differs from the first in {int((diff.max(axis=2) > 24).sum())} px "
              f"(max channel difference {int(diff.max())})")
        for back in (total - fade_frames, total - fade_frames // 2, total - 2):
            fr = self.frame_at(back)
            diff = np.abs(first.astype(int) - fr.astype(int))
            print(f"fade check: frame {back} ({back / self.fps:.3f} s) differs from the first in "
                  f"{int((diff.max(axis=2) > 24).sum())} px (max channel difference {int(diff.max())})")
        prev = self.frame_at(total - 2)
        diff = np.abs(prev.astype(int) - last.astype(int))
        print(f"loop step: the frame before the last differs from the last in {int((diff.max(axis=2) > 24).sum())} px "
              f"(single run: the scene fades back to the first frame over the last {fade_frames} frames)")
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
    man = json.loads((ROOT / "projects/spinglass/manifest.json").read_text())
    ev = measure(man)
    if "--measure-only" in sys.argv:
        return
    if "--frames" in sys.argv:
        times = [float(v) for v in sys.argv[sys.argv.index("--frames") + 1].split(",")]
        r = Renderer(man, ev)
        (ROOT / "media/spinglass").mkdir(parents=True, exist_ok=True)
        for tv in times:
            Image.fromarray(r.frame_at(int(round(tv * man["fps"])))).save(ROOT / f"media/spinglass/smoke-{tv}.png")
        print("smoke frames: " + ", ".join(f"{tv}" for tv in times))
        return
    Renderer(man, ev).render(ROOT / "media/spinglass/footage.mp4")


if __name__ == "__main__":
    main()
