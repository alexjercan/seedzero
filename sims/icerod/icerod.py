#!/usr/bin/env python3
"""Stick on ice: where does the tip land?

A uniform thin stick of length L = 1 m stands on a floor with its foot at
x = 0, leaning lean_deg (10 degrees) off vertical toward the right, so
theta0 = 80 degrees from the floor, and is let go from rest. Two panels
on the same clock, the same stick and the same lean. Top, ice: the floor
is frictionless, so no horizontal force acts on the stick, its centre of
mass falls straight down along x = (L / 2) cos theta0 and the foot slides
back; with the foot on the floor y_c = (L / 2) sin theta, the energy form
(I_c = m L^2 / 12) is

    theta'^2 = 12 g (sin theta0 - sin theta) / (L (1 + 3 cos^2 theta))

and the equation of motion is

    (1 + 3 cos^2 theta) theta'' = 3 sin theta cos theta theta'^2 - (6 g / L) cos theta.

Bottom, hinged: the foot is pinned in a hinge, theta'' = -(3 g / (2 L))
cos theta and theta'^2 = 3 g (sin theta0 - sin theta) / L. Both are
integrated by RK4 at steps_per_second, the landing (theta = 0) is located
by bisection inside the step, and the run is checked against the energy
forms and against the quadrature of the time to lie flat. The floor's push
on the ice foot, N = m (g + y_c''), is printed to show that the foot never
leaves the floor; the hinge force is printed to show why that foot must be
pinned (no friction could hold it). The drop repeats every cycle_s seconds
of video with a crossfade back to the standing stick; the cycle divides the
scene length, so the scene is exactly periodic and the last frame equals
the first. Shown at 1/slow speed. Deterministic, no seed.

Measured and printed: for each panel the time to lie flat (RK4 and the
quadrature), the energy check, the angular speed and the tip speed at the
floor, the tip's horizontal travel and where it lands, the foot's slide
(ice), the centre's fixed x and its drop (ice), the contact force (the
floor's push on the ice foot; the hinge force and its horizontal to
vertical ratio), the travel ratio and the time ratio between the panels,
the same drop at other leans and for a longer stick (for the description),
a half-step check, the schedule in video time, the loop and periodicity
checks and the on-screen text widths.

usage: icerod.py [--measure-only] [--frames t1,t2,...]
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
GHOST = (64, 74, 90)
ICE = (176, 204, 226)
ICE_HI = (228, 240, 250)
ICE_LO = (136, 166, 194)
NAVY = (24, 44, 74)
DECK_A = (30, 36, 46)
DECK_B = (42, 50, 62)
STEEL = (150, 160, 176)

# Layout: overlay at y 96..130 (captions.py), two title rows at y 190/252 for
# the first seconds, then the legend at y 236 and the shared clock at y 290;
# two panels stacked, ice in the band y 330..880 and the hinge in y 880..1430,
# both drawn at 2x in one geometry layer (nothing is clipped between them);
# each band has its label row 40 px under the band top, its second row at 84
# and its fixed line at 120 (left column from x 40, right column to x 1040),
# the floor surface 480 px under the band top (y 810 and 1360), the slab 32 px
# thick, the "start" label 50 px under the surface; captions at caption_y 0.75
# (y 1440..1530); the seven-line card from y 1572 at a 48 px pitch.
LEGEND_Y, CLOCK_Y = 236, 290
SS = 2
GEOM_Y0, GEOM_Y1 = 330, 1430
PAYOFF_Y, PAYOFF_PITCH = 1572.0, 48
PANELS = ("ice", "hinged")
BAND_Y = {"ice": 330, "hinged": 880}
LABEL_DY, SUB_DY, FIX_DY, FLOOR_DY = 40, 84, 120, 480
SLAB_PX = 32
BAR_R = 8.0
ROW_X0, ROW_X1 = 40, 1040
SLAB_X0, SLAB_X1 = 60, 1020
COLOUR = {"ice": TEAL, "hinged": CORAL}
SLAB_COLOUR = {"ice": ICE, "hinged": DECK_A}
MARK_COLOUR = {"ice": NAVY, "hinged": WHITE}


def blend(col, a: float, base=BG) -> tuple:
    a = max(0.0, min(1.0, a))
    return tuple(int(round(c * a + b * (1 - a))) for c, b in zip(col, base))


# --- measurement --------------------------------------------------------------
def accel(model: str, th: float, w: float, g: float, L: float) -> float:
    """theta'' for the ice stick (foot free to slide) or the hinged stick."""
    c, s = math.cos(th), math.sin(th)
    if model == "ice":
        return (3.0 * s * c * w * w - 6.0 * g / L * c) / (1.0 + 3.0 * c * c)
    return -1.5 * g / L * c


def rk4(model: str, th: float, w: float, h: float, g: float, L: float) -> tuple[float, float]:
    k1t, k1w = w, accel(model, th, w, g, L)
    k2t, k2w = w + 0.5 * h * k1w, accel(model, th + 0.5 * h * k1t, w + 0.5 * h * k1w, g, L)
    k3t, k3w = w + 0.5 * h * k2w, accel(model, th + 0.5 * h * k2t, w + 0.5 * h * k2w, g, L)
    k4t, k4w = w + h * k3w, accel(model, th + h * k3t, w + h * k3w, g, L)
    return (th + h / 6.0 * (k1t + 2.0 * k2t + 2.0 * k3t + k4t),
            w + h / 6.0 * (k1w + 2.0 * k2w + 2.0 * k3w + k4w))


def omega2_closed(model: str, th, th0: float, g: float, L: float):
    """theta'^2 from the energy form (numpy-friendly)."""
    if model == "ice":
        return 12.0 * g * (math.sin(th0) - np.sin(th)) / (L * (1.0 + 3.0 * np.cos(th) ** 2))
    return 3.0 * g * (math.sin(th0) - np.sin(th)) / L


def energy(model: str, th, w, g: float, L: float):
    """Mechanical energy per unit mass, T + V, with V = g y_c."""
    if model == "ice":
        return L * L / 24.0 * w * w * (1.0 + 3.0 * np.cos(th) ** 2) + g * L / 2.0 * np.sin(th)
    return L * L / 6.0 * w * w + g * L / 2.0 * np.sin(th)


def simulate(model: str, th0: float, g: float, L: float, dt: float, t_max: float) -> dict:
    """RK4 from rest at theta0 until the stick lies flat; the landing is found by bisection in the step."""
    n = int(round(t_max / dt))
    theta = [th0]
    omega = [0.0]
    th, w = th0, 0.0
    t_flat = w_flat = None
    for i in range(n):
        th_new, w_new = rk4(model, th, w, dt, g, L)
        if th_new <= 0.0:
            lo, hi = 0.0, dt
            for _ in range(60):
                mid = 0.5 * (lo + hi)
                thm, _ = rk4(model, th, w, mid, g, L)
                if thm > 0.0:
                    lo = mid
                else:
                    hi = mid
            _, w_flat = rk4(model, th, w, hi, g, L)
            t_flat = i * dt + hi
            break
        th, w = th_new, w_new
        theta.append(th)
        omega.append(w)
    assert t_flat is not None, "sim_end_s too short"
    return {"model": model, "th0": th0, "dt": dt, "theta": np.array(theta), "omega": np.array(omega),
            "t_flat": t_flat, "w_flat": w_flat}


def flat_time_quadrature(model: str, th0: float, g: float, L: float, n: int = 400000) -> float:
    """t = int_0^theta0 d theta / theta'(theta); with theta = theta0 - s^2 the integrand is smooth."""
    smax = math.sqrt(th0)
    s = (np.arange(n) + 0.5) * smax / n
    th = th0 - s * s
    f = 2.0 * s / np.sqrt(omega2_closed(model, th, th0, g, L))
    return float(f.sum()) * smax / n


def state_at(run: dict, r: float) -> tuple[float, float, bool]:
    """(theta, theta', landed) r seconds after the release."""
    if r < 0.0:
        return run["th0"], 0.0, False
    if r >= run["t_flat"]:
        return 0.0, run["w_flat"], True
    dt = run["dt"]
    i = int(r / dt)
    fr = r / dt - i
    th, w = run["theta"], run["omega"]
    i1 = min(i + 1, len(th) - 1)
    i = min(i, len(th) - 1)
    return float(th[i] + fr * (th[i1] - th[i])), float(w[i] + fr * (w[i1] - w[i])), False


def contact(run: dict, g: float, L: float) -> dict:
    """The contact force along the run, in weights, sampled at every RK4 step plus the landing."""
    th = np.append(run["theta"], 0.0)
    w = np.append(run["omega"], run["w_flat"])
    c, s = np.cos(th), np.sin(th)
    if run["model"] == "ice":
        thdd = (3.0 * s * c * w * w - 6.0 * g / L * c) / (1.0 + 3.0 * c * c)
        ycdd = L / 2.0 * (c * thdd - s * w * w)
        return {"th": th, "N": 1.0 + ycdd / g}
    thdd = -1.5 * g / L * c
    xcdd = L / 2.0 * (-s * thdd - c * w * w)
    ycdd = L / 2.0 * (c * thdd - s * w * w)
    return {"th": th, "Hx": xcdd / g, "Hy": 1.0 + ycdd / g}


def measure(man: dict) -> dict:
    g, L = man["g"], man["stick_length_m"]
    lean = man["lean_deg"]
    th0 = math.radians(90.0 - lean)
    dt = 1.0 / man["steps_per_second"]
    S, P, D, fps, F, ra = man["slow"], man["cycle_s"], man["scene_duration"], man["fps"], man["reset_fade"], man["release_at"]
    cycles = D / P
    assert abs(cycles - round(cycles)) < 1e-9, "the drop cycle must divide the scene length"
    for key in ("cycle_s", "release_at", "first_cycle_at", "reset_fade"):
        assert abs(man[key] * fps - round(man[key] * fps)) < 1e-9, f"{key} must be a whole number of frames"
    ppm = man["px_per_m"]
    print(f"setup: a uniform stick of length {L:g} m stands with its foot at x = 0, leaning {lean:g} degrees off vertical "
          f"toward the right (theta0 = {90 - lean:g} degrees from the floor), and is let go from rest; top panel the floor "
          f"is ice (frictionless, the foot free to slide), bottom panel the same stick with its foot pinned in a hinge; "
          f"g = {g:g} m/s^2; both integrated by RK4 at {man['steps_per_second']} steps per second (dt = {dt:.2e} s) with "
          f"the landing located by bisection inside the step; shown at 1/{S:g} speed on a {P:g} s cycle ({P * fps:.0f} "
          f"frames) with the release {ra:g} s into the cycle, {cycles:.0f} cycles in {D:g} s; drawn at {ppm:g} px per "
          f"metre; deterministic, no seed")
    runs = {m: simulate(m, th0, g, L, dt, man["sim_end_s"]) for m in PANELS}
    quad = {m: flat_time_quadrature(m, th0, g, L) for m in PANELS}
    ev: dict = {"runs": runs, "quad": quad}
    xc = L / 2.0 * math.cos(th0)
    w_floor_closed = math.sqrt(3.0 * g * math.sin(th0) / L)
    travel = {"ice": L / 2.0 * (1.0 - math.cos(th0)), "hinged": L * (1.0 - math.cos(th0))}
    ev["travel"] = travel
    ev["xc"] = xc
    for m in PANELS:
        r = runs[m]
        w2 = r["omega"] ** 2
        err_w2 = float(np.max(np.abs(w2 - omega2_closed(m, r["theta"], th0, g, L))))
        E = energy(m, r["theta"], r["omega"], g, L)
        drift = float(np.max(np.abs(E - E[0]))) / (g * L / 2.0 * math.sin(th0))
        wf = abs(r["w_flat"])
        common = (f"{m}: RK4: the stick lies flat at {r['t_flat']:.4f} s (quadrature of the energy form {quad[m]:.4f} s, "
                  f"diff {r['t_flat'] - quad[m]:+.1e} s); theta'^2 stays within {err_w2:.1e} rad^2/s^2 of the energy form "
                  f"and the energy drifts by {drift:.1e} of the energy released over {len(r['theta'])} steps; at the floor "
                  f"theta' = {wf:.4f} rad/s (closed form sqrt(3 g sin theta0 / L) = {w_floor_closed:.4f}), the tip comes "
                  f"down at L theta' = {L * wf:.3f} m/s and the centre at (L / 2) theta' = {L / 2 * wf:.3f} m/s")
        if m == "ice":
            ct = contact(r, g, L)
            k = int(np.argmin(ct["N"]))
            foot_v = L / 2.0 * np.sin(r["theta"]) * np.abs(r["omega"])
            kv = int(np.argmax(foot_v))
            print(common + f"; the tip's horizontal travel is (L / 2)(1 - cos theta0) = {travel['ice'] * 100:.2f} cm, so it "
                  f"lands {(L / 2 * (1 + math.cos(th0))) * 100:.2f} cm from the foot's start, and the foot slides back the "
                  f"same {travel['ice'] * 100:.2f} cm; the centre stays at x = (L / 2) cos theta0 = {xc * 100:.2f} cm "
                  f"(no horizontal force) and drops (L / 2) sin theta0 = {L / 2 * math.sin(th0) * 100:.2f} cm straight "
                  f"down; the foot slides fastest at {foot_v[kv]:.3f} m/s at {math.degrees(r['theta'][kv]):.1f} degrees "
                  f"and its speed (L / 2) sin theta theta' is {L / 2 * math.sin(0.0) * wf:.3f} m/s at the floor: it "
                  f"stops as the tip lands; the floor's push on the foot N = m (g + y_c'') is {ct['N'][0]:.3f} weights "
                  f"at the release, at least {ct['N'][k]:.3f} weights (at {math.degrees(ct['th'][k]):.1f} degrees) and "
                  f"{ct['N'][-1]:.3f} weights at the floor, never zero, so the foot never leaves the floor")
            ev["N_min"], ev["N_min_deg"] = float(ct["N"][k]), math.degrees(ct["th"][k])
        else:
            ct = contact(r, g, L)
            k = int(np.argmin(ct["Hy"]))
            ratio = np.abs(ct["Hx"]) / ct["Hy"]
            kr = int(np.argmax(ratio))
            print(common + f"; the tip's horizontal travel is L (1 - cos theta0) = {travel['hinged'] * 100:.2f} cm, so "
                  f"it lands L = {L * 100:.2f} cm from the foot; the hinge force (weights): vertical {ct['Hy'][0]:.3f} at "
                  f"the release, at least {ct['Hy'][k]:.4f} (at {math.degrees(ct['th'][k]):.1f} degrees) and "
                  f"{ct['Hy'][-1]:.3f} at the floor; horizontal (toward the foot, pulling the stick back) "
                  f"{abs(ct['Hx'][k]):.3f} at that angle and {abs(ct['Hx'][-1]):.3f} at the floor; the horizontal to "
                  f"vertical ratio reaches {ratio[kr]:.1f} at {math.degrees(ct['th'][kr]):.1f} degrees (a rough floor "
                  f"would need a friction coefficient of {ratio[kr]:.1f}), so no friction could hold this foot: it must "
                  f"be pinned")
            ev["Hy_min"], ev["Hy_min_deg"] = float(ct["Hy"][k]), math.degrees(ct["th"][k])
            ev["ratio_max"], ev["ratio_max_deg"] = float(ratio[kr]), math.degrees(ct["th"][kr])
    ti, th_ = runs["ice"]["t_flat"], runs["hinged"]["t_flat"]
    print(f"the two panels: the tip travels {travel['ice'] * 100:.2f} cm on ice against {travel['hinged'] * 100:.2f} cm "
          f"hinged, a ratio of {travel['hinged'] / travel['ice']:.4f} (exactly 2 at any lean: on ice the centre does not "
          f"move sideways, so the tip's travel is half the stick's foreshortening L (1 - cos theta0) instead of all of "
          f"it); the ice stick is flat at {ti:.4f} s against {th_:.4f} s hinged, {th_ / ti:.3f} times longer, "
          f"{th_ - ti:.4f} s apart; both reach the floor at {abs(runs['ice']['w_flat']):.4f} and "
          f"{abs(runs['hinged']['w_flat']):.4f} rad/s (the same energy ends in the same rotation: at theta = 0 both "
          f"kinetic energies are m L^2 theta'^2 / 6)")
    # For the description.
    descr = []
    for ln in man["description_leans_deg"]:
        t0 = math.radians(90.0 - ln)
        ri = simulate("ice", t0, g, L, dt, man["sim_end_s"])
        rh = simulate("hinged", t0, g, L, dt, man["sim_end_s"])
        descr.append(f"{ln:g} degree off vertical: ice flat at {ri['t_flat']:.3f} s (quadrature "
                     f"{flat_time_quadrature('ice', t0, g, L):.3f}), hinged {rh['t_flat']:.3f} s (quadrature "
                     f"{flat_time_quadrature('hinged', t0, g, L):.3f}), {rh['t_flat'] / ri['t_flat']:.3f} times longer; tip "
                     f"travel {L / 2 * (1 - math.cos(t0)) * 100:.2f} cm against {L * (1 - math.cos(t0)) * 100:.2f} cm, ratio "
                     f"{L * (1 - math.cos(t0)) / (L / 2 * (1 - math.cos(t0))):.4f}; both at "
                     f"{abs(ri['w_flat']):.3f} and {abs(rh['w_flat']):.3f} rad/s at the floor")
    L2 = man["description_length_m"]
    ri2 = simulate("ice", th0, g, L2, dt, man["sim_end_s"])
    rh2 = simulate("hinged", th0, g, L2, dt, man["sim_end_s"])
    descr.append(f"a {L2:g} m stick at {lean:g} degrees: ice flat at {ri2['t_flat']:.3f} s, hinged {rh2['t_flat']:.3f} s "
                 f"(sqrt({L2:g} / {L:g}) = {math.sqrt(L2 / L):.4f} times the {L:g} m times, {math.sqrt(L2 / L) * ti:.3f} "
                 f"and {math.sqrt(L2 / L) * th_:.3f} s); tip travel {L2 / 2 * (1 - math.cos(th0)) * 100:.2f} cm against "
                 f"{L2 * (1 - math.cos(th0)) * 100:.2f} cm, ratio {2.0:.4f}")
    print("for the description (same release, other leans and a longer stick): " + "; ".join(descr))
    half = {m: simulate(m, th0, g, L, 0.5 * dt, man["sim_end_s"]) for m in PANELS}
    print("check at half the time step (" + f"{2 * man['steps_per_second']} steps per second): " + "; ".join(
        f"{m} flat at {half[m]['t_flat']:.6f} s ({half[m]['t_flat'] - runs[m]['t_flat']:+.1e}), "
        f"{abs(half[m]['w_flat']):.6f} rad/s at the floor ({abs(half[m]['w_flat']) - abs(runs[m]['w_flat']):+.1e})"
        for m in PANELS))
    # Schedule in video time.
    t0 = man["first_cycle_at"]
    k0 = math.ceil((0.0 - t0) / P - 1e-9) - 1
    k1 = math.floor((D - t0) / P - 1e-9)
    starts = [t0 + k * P for k in range(k0, k1 + 1)]
    ev["cycles"] = int(round(cycles))

    def lst(off_: float) -> str:
        return ", ".join(f"{s + off_:.2f}" for s in starts if 0.0 <= s + off_ < D)

    tau0 = (0.0 - t0) % P
    r0 = (tau0 - ra) / S
    st0 = {m: state_at(runs[m], r0) for m in PANELS}
    print(f"schedule (video time, 1/{S:g} speed): cycles of {P:g} s start at " + ", ".join(f"{s:.2f}" for s in starts)
          + f" s (the first {-t0:.2f} s before the first frame); the release {ra:g} s into each cycle at {lst(ra)} s; the "
          f"ice stick lies flat {ti * S:.2f} s after the release at {lst(ra + ti * S)} s and the hinged stick "
          f"{th_ * S:.2f} s after the release at {lst(ra + th_ * S)} s; both lie flat with their readouts until the "
          f"reset fade, which crossfades back to the standing stick over the last {F:g} s of each cycle (out over "
          f"{P - F:.2f} to {P - F / 2:.2f} s, in over {P - F / 2:.2f} to {P:.2f} s after the cycle start, at "
          f"{lst(P - F)} s); on the first frame the cycle is {tau0:.2f} s in ({r0:.3f} s real after the release): the "
          f"ice stick is at {math.degrees(st0['ice'][0]):.1f} degrees with its tip "
          f"{(L / 2 * (math.cos(st0['ice'][0]) - math.cos(th0))) * 100:.1f} cm along, the hinged stick at "
          f"{math.degrees(st0['hinged'][0]):.1f} degrees with its tip "
          f"{(L * (math.cos(st0['hinged'][0]) - math.cos(th0))) * 100:.1f} cm along; title until {man['title_until']:g} "
          f"s; payoff card from {man['payoff_t']:g} s; the title fades back in over the last {man['loop_fade']:g} s and "
          f"the last frame repeats the first (the scene is periodic: {D:g} s holds exactly {cycles:.0f} cycles)")
    # Text widths.
    font = os.environ["SEED_ZERO_FONT"]
    f28, f34, f40, f56 = (ImageFont.truetype(font, n) for n in (28, 34, 40, 56))
    widths = {"overlay@34": (f34, man["overlay"])}
    for j, line in enumerate(man["title"].split("|")):
        widths[f"title line {j + 1}@56"] = (f56, line)
    widths["legend@40"] = (f40, legend_text(man))
    widths["clock@28"] = (f28, clock_text(0.7683))
    widths["clock rest@28"] = (f28, clock_text(-1.0))
    for m in PANELS:
        widths[f"label {m}@40"] = (f40, label_text(m))
        widths[f"sublabel {m}@28"] = (f28, sub_text(m))
        widths[f"fixed {m}@28"] = (f28, fixed_text(ev, m))
        widths[f"readout {m}@40"] = (f40, readout_text(travel[m]))
        widths[f"readout2 {m}@28"] = (f28, readout2_text(m, travel["ice"]))
    widths["mark start@28"] = (f28, "start")
    for j, line in enumerate(payoff_lines(man, ev)):
        widths[f"payoff line {j + 1}@40"] = (f40, line)
    print("text widths: " + ", ".join(f"{k} {f.getlength(s):.0f} px" for k, (f, s) in widths.items()))
    assert all(f.getlength(s) < 950 for f, s in widths.values()), "a text line is wider than 950 px"
    # Row checks: the left column must end before the standing stick, and the right column must clear
    # the hinged tip's path (the ice tip never reaches the right column).
    fx = man["foot_x_px"]
    left = ROW_X0 + max(max(f40.getlength(label_text(m)), f28.getlength(sub_text(m)), f28.getlength(fixed_text(ev, m)))
                        for m in PANELS)
    right1 = ROW_X1 - max(f40.getlength(readout_text(travel[m])) for m in PANELS)
    right2 = ROW_X1 - max(f28.getlength(readout2_text(m, travel["ice"])) for m in PANELS)
    print(f"row check: the left column ends at x {left:.0f} px and the standing stick starts at x {fx:.0f} px; the "
          f"readout row starts at x {right1:.0f} px and the second row at x {right2:.0f} px")
    assert left < fx - 20, "the left column reaches the stick"
    r = runs["hinged"]
    tip_x = fx + L * np.cos(r["theta"]) * ppm
    tip_y = BAND_Y["hinged"] + FLOOR_DY - BAR_R - L * np.sin(r["theta"]) * ppm - BAND_Y["hinged"]   # band-relative
    cap = BAR_R + 3.0
    boxes = {"readout row": (right1, LABEL_DY - 20, ROW_X1, LABEL_DY + 20),
             "second row": (right2, SUB_DY - 14, ROW_X1, SUB_DY + 14)}
    clear = {}
    for name, (x0, y0, x1, y1) in boxes.items():
        dx = x0 - (tip_x + cap)
        dy = (tip_y - cap) - y1
        clear[name] = float(np.min(np.maximum(dx, dy)))
    ice_tip_max = fx + (xc + L / 2.0) * ppm
    print("clearance: the hinged tip passes " + ", ".join(f"{v:.0f} px from the {k}" for k, v in clear.items())
          + f" at the closest; the ice tip never goes right of x {ice_tip_max:.0f} px")
    assert all(v > 8.0 for v in clear.values()), "the hinged tip crosses a readout row"
    return ev


def legend_text(man: dict) -> str:
    return f"same stick, same lean, 1/{man['slow']:g} speed"


def clock_text(r: float) -> str:
    return "at rest before the release" if r < 0.0 else f"{r:.3f} s after the release"


def label_text(m: str) -> str:
    return "on ice" if m == "ice" else "pinned in a hinge"


def sub_text(m: str) -> str:
    return "no grip: the foot slides" if m == "ice" else "the foot cannot move"


def fixed_text(ev: dict, m: str) -> str:
    return f"lies flat at {ev['runs'][m]['t_flat']:.3f} s"


def readout_text(travel_m: float) -> str:
    return f"tip {travel_m * 100:.0f} cm along"


def readout2_text(m: str, slide_m: float) -> str:
    return f"foot {max(0.0, slide_m) * 100:.0f} cm back" if m == "ice" else "foot held by the pin"


def payoff_lines(man: dict, ev: dict) -> list[str]:
    text = man["payoff_text"].format(
        tip_ice=ev["travel"]["ice"] * 100, tip_hinged=ev["travel"]["hinged"] * 100,
        t_ice=ev["runs"]["ice"]["t_flat"], t_hinged=ev["runs"]["hinged"]["t_flat"],
        w_floor=abs(ev["runs"]["ice"]["w_flat"]), n_min=ev["N_min"])
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
        self.L = float(man["stick_length_m"])
        self.th0 = math.radians(90.0 - man["lean_deg"])
        self.S = man["slow"]
        self.P = man["cycle_s"]
        self.P_f = int(round(man["cycle_s"] * self.fps))
        self.c0_f = int(round(man["first_cycle_at"] * self.fps))
        self.ra, self.F = man["release_at"], man["reset_fade"]
        self.runs = ev["runs"]
        self.fx = float(man["foot_x_px"])
        self.xc = ev["xc"]

    # --- state helpers ------------------------------------------------------
    def phase(self, f: int) -> tuple[int, float]:
        k, tau_f = divmod(f - self.c0_f, self.P_f)
        return k, tau_f / self.fps

    def ends(self, m: str, th: float) -> tuple[float, float, float, float]:
        """Foot and tip of the stick in metres (x right, y up) for angle th."""
        L = self.L
        if m == "ice":
            return self.xc - L / 2.0 * math.cos(th), 0.0, self.xc + L / 2.0 * math.cos(th), L * math.sin(th)
        return 0.0, 0.0, L * math.cos(th), L * math.sin(th)

    # --- pixel helpers ------------------------------------------------------
    def Lp(self, x: float, y: float) -> tuple[float, float]:
        """Layer (2x) pixel of a screen point, rounded to 1e-4 px so equal states draw equal pixels."""
        return round(x * SS, 4), round((y - GEOM_Y0) * SS, 4)

    def scr(self, m: str, x_m: float, y_m: float) -> tuple[float, float]:
        """Screen point of a stick-axis point (metres from the foot's start, height above the floor)."""
        axis_y = BAND_Y[m] + FLOOR_DY - BAR_R
        return self.fx + x_m * self.ppm, axis_y - y_m * self.ppm

    def dashed(self, d: ImageDraw.ImageDraw, a: tuple, b: tuple, col, dash: float, gap: float, width: int) -> None:
        ax, ay = a
        bx, by = b
        length = math.hypot(bx - ax, by - ay)
        if length < 1e-9:
            return
        ux, uy = (bx - ax) / length, (by - ay) / length
        s = 0.0
        while s < length:
            e = min(length, s + dash)
            d.line((ax + ux * s, ay + uy * s, ax + ux * e, ay + uy * e), fill=col, width=width)
            s = e + gap

    def notch(self, d: ImageDraw.ImageDraw, x: float, ys: float, col) -> None:
        """A small triangle in the slab, its apex at the surface."""
        p0, p1, p2 = self.Lp(x, ys + 4), self.Lp(x - 9, ys + 20), self.Lp(x + 9, ys + 20)
        d.polygon([p0, p1, p2], fill=col)

    def draw_floor(self, d: ImageDraw.ImageDraw, m: str) -> None:
        ys = BAND_Y[m] + FLOOR_DY
        s0, s1 = self.Lp(SLAB_X0, ys), self.Lp(SLAB_X1, ys + SLAB_PX)
        d.rectangle((s0[0], s0[1], s1[0], s1[1]), fill=SLAB_COLOUR[m])
        if m == "ice":
            t0, t1 = self.Lp(SLAB_X0, ys), self.Lp(SLAB_X1, ys)
            d.line((*t0, *t1), fill=ICE_HI, width=2 * SS)
            b0, b1 = self.Lp(SLAB_X0, ys + SLAB_PX - 4), self.Lp(SLAB_X1, ys + SLAB_PX)
            d.rectangle((b0[0], b0[1], b1[0], b1[1]), fill=ICE_LO)
            for hx in (150, 330, 590, 790, 950):
                h0, h1 = self.Lp(hx, ys + 8), self.Lp(hx + 44, ys + 24)
                d.line((*h0, *h1), fill=ICE_HI, width=2 * SS)
        else:
            t0, t1 = self.Lp(SLAB_X0, ys), self.Lp(SLAB_X1, ys)
            d.line((*t0, *t1), fill=DECK_B, width=3 * SS)
            # The hinge bracket: a trapezoid from the surface up to the pin on the stick's axis.
            ax_y = ys - BAR_R
            poly = [self.Lp(self.fx - 24, ys + 2), self.Lp(self.fx + 24, ys + 2), self.Lp(self.fx + 9, ax_y),
                    self.Lp(self.fx - 9, ax_y)]
            d.polygon(poly, fill=STEEL)
        # The start mark at the foot's start.
        self.notch(d, self.fx, ys, blend(GOLD, 1.0, SLAB_COLOUR[m]))
        # The ghost of the start pose: a dashed stick from the foot to the tip's start.
        fx0, fy0, tx0, ty0 = self.ends(m, self.th0)
        a = self.Lp(*self.scr(m, fx0, fy0))
        b = self.Lp(*self.scr(m, tx0, ty0))
        self.dashed(d, a, b, GHOST, 14 * SS, 9 * SS, 3 * SS)
        r = BAR_R * SS
        d.ellipse((b[0] - r, b[1] - r, b[0] + r, b[1] + r), outline=GHOST, width=2 * SS)
        if m == "ice":
            # The guide through the centre of mass: it falls straight down this line.
            cx, cy_top = self.scr(m, self.xc, self.L / 2.0 * math.sin(self.th0))
            g0, g1 = self.Lp(cx, ys - 2), self.Lp(cx, cy_top - 36)
            self.dashed(d, g0, g1, blend(TEAL, 0.5), 10 * SS, 8 * SS, 2 * SS)

    def draw_stick(self, d: ImageDraw.ImageDraw, m: str, th: float, a: float) -> None:
        col = blend(COLOUR[m], a)
        fx_m, fy_m, tx_m, ty_m = self.ends(m, th)
        p_f = self.Lp(*self.scr(m, fx_m, fy_m))
        p_t = self.Lp(*self.scr(m, tx_m, ty_m))
        r = BAR_R * SS
        d.line((*p_f, *p_t), fill=col, width=int(2 * r))
        d.ellipse((p_f[0] - r, p_f[1] - r, p_f[0] + r, p_f[1] + r), fill=col)
        d.ellipse((p_t[0] - r, p_t[1] - r, p_t[0] + r, p_t[1] + r), fill=col)
        # The marked middle and the coloured tip.
        mx, my = 0.5 * (p_f[0] + p_t[0]), 0.5 * (p_f[1] + p_t[1])
        rr = 7 * SS
        d.ellipse((mx - rr, my - rr, mx + rr, my + rr), fill=blend(BG, a), outline=blend(WHITE, a), width=2 * SS)
        rt = (BAR_R + 3) * SS
        d.ellipse((p_t[0] - rt, p_t[1] - rt, p_t[0] + rt, p_t[1] + rt), fill=blend(GOLD, a))
        if m == "hinged":
            pr = 5 * SS
            d.ellipse((p_f[0] - pr, p_f[1] - pr, p_f[0] + pr, p_f[1] + pr), fill=BG, outline=blend(WHITE, a), width=2 * SS)

    def draw_scene(self, d: ImageDraw.ImageDraw, m: str, tau: float, a: float) -> dict:
        """The moving parts of one panel tau seconds into a cycle, blended by a."""
        man = self.man
        r = (tau - self.ra) / self.S
        run = self.runs[m]
        th, w, landed = state_at(run, r)
        ys = BAND_Y[m] + FLOOR_DY
        base = SLAB_COLOUR[m]
        fx_m, _, tx_m, _ = self.ends(m, th)
        _, _, tx0_m, _ = self.ends(m, self.th0)
        travel = tx_m - tx0_m
        slide = -fx_m
        # The travel bars in the slab: the tip's (gold) and, on ice, the foot's (teal).
        x_t0, x_t = self.fx + tx0_m * self.ppm, self.fx + tx_m * self.ppm
        if x_t - x_t0 > 2.0:
            b0, b1 = self.Lp(x_t0, ys + 11), self.Lp(x_t, ys + 11)
            d.line((*b0, *b1), fill=blend(GOLD, 0.9 * a, base), width=4 * SS)
        if m == "ice":
            x_f = self.fx + fx_m * self.ppm
            if self.fx - x_f > 2.0:
                b0, b1 = self.Lp(x_f, ys + 24), self.Lp(self.fx, ys + 24)
                d.line((*b0, *b1), fill=blend(TEAL, 0.9 * a, base), width=4 * SS)
        if landed:
            self.notch(d, x_t, ys, blend(MARK_COLOUR[m], a, base))
        self.draw_stick(d, m, th, a)
        if landed:
            u = (tau - (self.ra + run["t_flat"] * self.S)) / man["land_flash"]
            if 0.0 <= u < 1.0:
                p_t = self.Lp(*self.scr(m, tx_m, 0.0))
                rr = (22 + 70 * u) * SS
                d.ellipse((p_t[0] - rr, p_t[1] - rr, p_t[0] + rr, p_t[1] + rr), outline=blend(WHITE, (1 - u) * a),
                          width=4 * SS)
        return {"theta": th, "travel": travel, "slide": slide, "landed": landed, "r": r, "alpha": a}

    def draw_panel(self, d: ImageDraw.ImageDraw, m: str, f: int) -> dict:
        self.draw_floor(d, m)
        k, tau = self.phase(f)
        F, P = self.F, self.P
        a_old = 1.0 if tau <= P - F else max(0.0, (P - F / 2.0 - tau) / (F / 2.0))
        st = self.draw_scene(d, m, tau, a_old) if a_old > 0.0 else None
        if tau >= P - F / 2.0:
            a_new = (tau - (P - F / 2.0)) / (F / 2.0)
            st_new = self.draw_scene(d, m, tau - P, a_new)
            if st is None or a_new >= 0.5:
                st = st_new
        st["k"] = k
        return st

    def draw_text(self, d: ImageDraw.ImageDraw, states: dict, hud_alpha: float) -> None:
        man, ev = self.man, self.ev
        for m, st in states.items():
            y0 = BAND_Y[m]
            a = st["alpha"]
            col = COLOUR[m]
            d.text((ROW_X0, y0 + LABEL_DY), label_text(m), font=self.font, fill=col, anchor="lm")
            d.text((ROW_X0, y0 + SUB_DY), sub_text(m), font=self.font_small, fill=MUTED, anchor="lm")
            if hud_alpha > 0.02:
                d.text((ROW_X0, y0 + FIX_DY), fixed_text(ev, m), font=self.font_small,
                       fill=blend(GOLD, 0.85 * hud_alpha), anchor="lm")
            d.text((ROW_X1, y0 + LABEL_DY), readout_text(st["travel"]), font=self.font,
                   fill=blend(GOLD if st["landed"] else TEXT, a), anchor="rm")
            d.text((ROW_X1, y0 + SUB_DY), readout2_text(m, st["slide"]), font=self.font_small,
                   fill=blend(GOLD if (st["landed"] and m == "ice") else MUTED, a), anchor="rm")
            ys = y0 + FLOOR_DY
            d.text((self.fx, ys + SLAB_PX + 18), "start", font=self.font_small, fill=MUTED, anchor="mm")
        if hud_alpha > 0.02:
            d.text((W / 2, LEGEND_Y), legend_text(man), font=self.font, fill=blend(TEXT, hud_alpha), anchor="mm")
            r_clock = min(states["ice"]["r"], self.runs["hinged"]["t_flat"])
            d.text((W / 2, CLOCK_Y), clock_text(r_clock), font=self.font_small, fill=blend(MUTED, hud_alpha), anchor="mm")

    def live_frame(self, f: int, title_alpha: float | None = None, hud_alpha: float = 0.0) -> np.ndarray:
        """Frame f with the geometry at f / fps; title_alpha and hud_alpha override the title and the
        legend/clock/fixed-line/card blend during the loop fade."""
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
    man = json.loads((ROOT / "projects/icerod/manifest.json").read_text())
    ev = measure(man)
    if "--measure-only" in sys.argv:
        return
    if "--frames" in sys.argv:
        times = [float(v) for v in sys.argv[sys.argv.index("--frames") + 1].split(",")]
        r = Renderer(man, ev)
        (ROOT / "media/icerod").mkdir(parents=True, exist_ok=True)
        for tv in times:
            Image.fromarray(r.frame_at(int(round(tv * man["fps"])))).save(ROOT / f"media/icerod/smoke-{tv}.png")
        print("smoke frames: " + ", ".join(f"{tv}" for tv in times))
        return
    Renderer(man, ev).render(ROOT / "media/icerod/footage.mp4")


if __name__ == "__main__":
    main()
