#!/usr/bin/env python3
"""Balance a broom: which is easier to balance, a pencil or a broom?

Two panels on the same clock: a uniform thin stick of length L stands on
a fingertip with its foot held in place (a hinge: the foot neither slips
nor lifts), let go from rest lean_deg (1 degree) off vertical; theta is
measured from vertical. About the foot I = m L^2 / 3 and the torque is
m g (L / 2) sin theta, so

    theta'' = (3 g / (2 L)) sin theta,   theta'^2 = (3 g / L)(cos theta0 - cos theta)

and the mass cancels. In the scaled time tau = t sqrt(3 g / (2 L)) the
equation is theta'' = sin theta for every length, so every time in the
fall scales exactly with sqrt(L): the pencil's fall is the broom's fall
played sqrt(L_broom / L_pencil) times faster. Top panel the broom (1.2
m), bottom panel the pencil (0.15 m, eight times shorter); each band at
its own scale so both sticks are the same length on screen (the frame
shows the same fall at two speeds, which is the physics). The stick lies
flat at theta = 90 degrees (the floor). Both are integrated by RK4 at
steps_per_second with the floor and the 45-degree crossing located by
bisection inside the step, checked against the energy form at every
step, against the quadrature of the energy form for the flat and
45-degree times, against sqrt(8) for the time ratio, and by a half-step
rerun; the foot's push on the stick (vertical and horizontal, in
weights) is printed through the fall. The drop repeats every cycle_s
seconds of video with a crossfade back to the standing stick; the cycle
divides the scene length, so the scene is exactly periodic and the last
frame equals the first. Shown at 1/slow speed. Deterministic, no seed.

Measured and printed: for each panel the time to lie flat and to reach
45 degrees (RK4 and the quadrature), the energy check, the angular speed
and the tip speed at the floor, the foot's push, the small-angle growth
rate and the lean's doublings, the time ratio against sqrt(8), the same
fall at other leans and lengths (for the description), a half-step
check, the schedule in video time, the on-screen text widths and the
layout clearances.

usage: broom.py [--measure-only] [--frames t1,t2,...]
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
ARC = (46, 54, 66)
SKIN = (186, 140, 112)
SKIN_DARK = (132, 94, 72)
NAIL = (222, 190, 170)

# Layout: overlay at y 96..130 (captions.py), two title rows at y 190/252 for
# the first seconds, then the legend at y 236 and the shared clock at y 290;
# two panels stacked, the broom in the band y 330..880 and the pencil in
# y 880..1430, each drawn at 2x in its own geometry layer; each band has its
# label row 40 px under the band top, its second row at 84 and its third at
# 120 (left column from x 40, right column to x 1040); the foot (hinge) on a
# fingertip at foot_x_px, foot_dy under the band top, the stick stick_px long
# on screen in both bands (each band at its own scale), falling to the right
# along a muted arc; the 45-degree tick and its time outside the arc; the gold
# event row in the free space right of the arc; captions at caption_y 0.75
# (y 1440..1530); the six-line card from y 1572 at a 48 px pitch.
LEGEND_Y, CLOCK_Y = 236, 290
SS = 2
PAYOFF_Y, PAYOFF_PITCH = 1572.0, 48
PANELS = ("broom", "pencil")
BAND_Y = {"broom": 330, "pencil": 880}
BAND_H = 550
LABEL_DY, SUB_DY, FIX_DY = 40, 84, 120
EVENT_X, EVENT_DY = 880, 330
TICK_LABEL_GAP = 30.0
ROW_X0, ROW_X1 = 40, 1040
BAR_R = 8.0
FINGER_W = 48
COLOUR = {"broom": TEAL, "pencil": CORAL}


def blend(col, a: float, base=BG) -> tuple:
    a = max(0.0, min(1.0, a))
    return tuple(int(round(c * a + b * (1 - a))) for c, b in zip(col, base))


# --- measurement --------------------------------------------------------------
def accel(th: float, g: float, L: float) -> float:
    """theta'' = (3 g / (2 L)) sin theta, theta from vertical, the foot hinged."""
    return 1.5 * g / L * math.sin(th)


def rk4(th: float, w: float, h: float, g: float, L: float) -> tuple[float, float]:
    k1t, k1w = w, accel(th, g, L)
    k2t, k2w = w + 0.5 * h * k1w, accel(th + 0.5 * h * k1t, g, L)
    k3t, k3w = w + 0.5 * h * k2w, accel(th + 0.5 * h * k2t, g, L)
    k4t, k4w = w + h * k3w, accel(th + h * k3t, g, L)
    return (th + h / 6.0 * (k1t + 2.0 * k2t + 2.0 * k3t + k4t),
            w + h / 6.0 * (k1w + 2.0 * k2w + 2.0 * k3w + k4w))


def omega2_closed(th, th0: float, g: float, L: float):
    """theta'^2 from the energy form (numpy-friendly)."""
    return 3.0 * g * (math.cos(th0) - np.cos(th)) / L


def energy(th, w, g: float, L: float):
    """Mechanical energy per unit mass, T + V, with V = g y_c = g (L / 2) cos theta."""
    return L * L / 6.0 * w * w + g * L / 2.0 * np.cos(th)


def rate(g: float, L: float) -> float:
    """Small-angle growth rate sqrt(3 g / (2 L)): theta = theta0 cosh(rate t) from rest."""
    return math.sqrt(1.5 * g / L)


def simulate(th0: float, g: float, L: float, dt: float, t_max: float) -> dict:
    """RK4 from rest at theta0 until the stick lies flat (theta = pi/2); the floor and the
    45-degree crossing are located by bisection inside the step."""
    n = int(round(t_max / dt))
    theta = [th0]
    omega = [0.0]
    th, w = th0, 0.0
    t_flat = w_flat = t_45 = w_45 = None

    def cross(th_: float, w_: float, target: float) -> tuple[float, float]:
        lo, hi = 0.0, dt
        for _ in range(60):
            mid = 0.5 * (lo + hi)
            thm, _ = rk4(th_, w_, mid, g, L)
            if thm < target:
                lo = mid
            else:
                hi = mid
        _, wh = rk4(th_, w_, hi, g, L)
        return hi, wh

    for i in range(n):
        th_new, w_new = rk4(th, w, dt, g, L)
        if th_new >= math.pi / 4.0 and t_45 is None:
            h45, w_45 = cross(th, w, math.pi / 4.0)
            t_45 = i * dt + h45
        if th_new >= math.pi / 2.0:
            hf, w_flat = cross(th, w, math.pi / 2.0)
            t_flat = i * dt + hf
            break
        th, w = th_new, w_new
        theta.append(th)
        omega.append(w)
    assert t_flat is not None and t_45 is not None, "sim_end_s too short"
    return {"th0": th0, "L": L, "dt": dt, "theta": np.array(theta), "omega": np.array(omega),
            "t_flat": t_flat, "w_flat": w_flat, "t_45": t_45, "w_45": w_45}


def time_quadrature(th0: float, g: float, L: float, th_end: float, n: int = 400000) -> float:
    """t = int_theta0^theta_end d theta / theta'(theta) with theta' from the energy form; with
    theta = theta0 + s^2 the integrand 2 s / sqrt(cos theta0 - cos theta) is smooth, and
    cos a - cos b = 2 sin((a + b) / 2) sin((b - a) / 2) keeps it accurate near s = 0."""
    smax = math.sqrt(th_end - th0)
    s = (np.arange(n) + 0.5) * smax / n
    diff = 2.0 * np.sin(th0 + s * s / 2.0) * np.sin(s * s / 2.0)
    f = 2.0 * s / np.sqrt(3.0 * g * diff / L)
    return float(f.sum()) * smax / n


def state_at(run: dict, r: float) -> tuple[float, float, bool]:
    """(theta, theta', landed) r seconds after the release."""
    if r < 0.0:
        return run["th0"], 0.0, False
    if r >= run["t_flat"]:
        return math.pi / 2.0, run["w_flat"], True
    dt = run["dt"]
    i = int(r / dt)
    fr = r / dt - i
    th, w = run["theta"], run["omega"]
    i1 = min(i + 1, len(th) - 1)
    i = min(i, len(th) - 1)
    return float(th[i] + fr * (th[i1] - th[i])), float(w[i] + fr * (w[i1] - w[i])), False


def foot_push(run: dict, g: float, L: float) -> dict:
    """The foot's push on the stick along the run, in weights, at every RK4 step plus the floor:
    the centre is at ((L / 2) sin theta, (L / 2) cos theta), so Fx = m x_c'' and Fy = m (g + y_c'')."""
    th = np.append(run["theta"], math.pi / 2.0)
    w = np.append(run["omega"], run["w_flat"])
    c, s = np.cos(th), np.sin(th)
    thdd = 1.5 * g / L * s
    xcdd = L / 2.0 * (c * thdd - s * w * w)
    ycdd = L / 2.0 * (-s * thdd - c * w * w)
    return {"th": th, "Hx": xcdd / g, "Hy": 1.0 + ycdd / g}


def crossing_time(run: dict, th_target: float) -> float:
    """The first time the lean reaches th_target, interpolated on the RK4 table."""
    return float(np.interp(th_target, run["theta"], np.arange(len(run["theta"])) * run["dt"]))


def measure(man: dict) -> dict:
    g = man["g"]
    lean = man["lean_deg"]
    th0 = math.radians(lean)
    dt = 1.0 / man["steps_per_second"]
    S, P, D, fps, F, ra = man["slow"], man["cycle_s"], man["scene_duration"], man["fps"], man["reset_fade"], man["release_at"]
    Pe = P - man["reset_hold"]   # the reset crossfade ends here; the sticks then stand held to the next release
    cycles = D / P
    assert abs(cycles - round(cycles)) < 1e-9, "the drop cycle must divide the scene length"
    for key in ("cycle_s", "release_at", "first_cycle_at", "reset_fade", "reset_hold"):
        assert abs(man[key] * fps - round(man[key] * fps)) < 1e-9, f"{key} must be a whole number of frames"
    Ls = {m: man["sticks"][m]["length_m"] for m in PANELS}
    stick_px = float(man["stick_px"])
    ppm = {m: stick_px / Ls[m] for m in PANELS}
    print(f"setup: a uniform thin stick stands on a fingertip with its foot held in place (a hinge: the foot neither "
          f"slips nor lifts), let go from rest {lean:g} degree off vertical (theta from vertical); about the foot "
          f"I = m L^2 / 3 and the torque is m g (L / 2) sin theta, so theta'' = (3 g / (2 L)) sin theta and the mass "
          f"cancels; top panel the broom, L = {Ls['broom']:g} m ({Ls['broom'] * 100:g} cm); bottom panel the pencil, L = "
          f"{Ls['pencil']:g} m ({Ls['pencil'] * 100:g} cm), "
          f"{Ls['broom'] / Ls['pencil']:g} times shorter (the broom is {Ls['broom'] / Ls['pencil']:g} times as long); "
          f"g = {g:g} m/s^2; the stick lies flat at theta = 90 degrees (the floor); both integrated by RK4 at "
          f"{man['steps_per_second']} steps per second (dt = {dt:.0e} s) with the floor and the 45-degree crossing "
          f"located by bisection inside the step; shown at 1/{S:g} speed on a {P:g} s cycle ({P * fps:.0f} frames) with "
          f"the release {ra:g} s into the cycle, {cycles:.0f} cycles in {D:g} s; each stick drawn to fit, {stick_px:.0f} px "
          f"long on screen (broom {ppm['broom']:.0f} px per metre, pencil {ppm['pencil']:.0f} px per metre, drawn "
          f"{ppm['pencil'] / ppm['broom']:g}x); deterministic, no seed")
    runs = {m: simulate(th0, g, Ls[m], dt, man["sim_end_s"]) for m in PANELS}
    ev: dict = {"runs": runs, "Ls": Ls, "ppm": ppm}
    for m in PANELS:
        r, L = runs[m], Ls[m]
        q_flat = time_quadrature(th0, g, L, math.pi / 2.0)
        q_45 = time_quadrature(th0, g, L, math.pi / 4.0)
        w2 = r["omega"] ** 2
        err_w2 = float(np.max(np.abs(w2 - omega2_closed(r["theta"], th0, g, L))))
        E = energy(r["theta"], r["omega"], g, L)
        drift = float(np.max(np.abs(E - E[0]))) / (g * L / 2.0 * math.cos(th0))
        wf = r["w_flat"]
        wf_closed = math.sqrt(3.0 * g * math.cos(th0) / L)
        w45_closed = math.sqrt(3.0 * g * (math.cos(th0) - math.cos(math.pi / 4.0)) / L)
        k = rate(g, L)
        t2 = crossing_time(r, 2.0 * th0)
        t4 = crossing_time(r, 4.0 * th0)
        t10 = crossing_time(r, math.radians(10.0))
        print(f"{m} ({L:g} m): RK4: the stick lies flat at {r['t_flat']:.4f} s (quadrature of the energy form {q_flat:.4f} s, "
              f"diff {r['t_flat'] - q_flat:+.1e} s) and passes 45 degrees at {r['t_45']:.4f} s (quadrature {q_45:.4f} s, "
              f"diff {r['t_45'] - q_45:+.1e} s); theta'^2 stays within {err_w2:.1e} rad^2/s^2 of the energy form "
              f"(3 g / L)(cos theta0 - cos theta) and the energy drifts by {drift:.1e} of the energy released over "
              f"{len(r['theta'])} steps; at the floor theta' = {wf:.4f} rad/s (energy form sqrt(3 g cos theta0 / L) = "
              f"{wf_closed:.4f}) and the tip comes down at L theta' = {L * wf:.3f} m/s = {L * wf:.2f} m/s; at 45 degrees "
              f"theta' = {r['w_45']:.4f} rad/s (energy form {w45_closed:.4f}); small-angle growth rate sqrt(3 g / (2 L)) = "
              f"{k:.4f} per second (e-fold {1.0 / k:.4f} s; the growing mode doubles every ln 2 / rate = "
              f"{math.log(2.0) / k:.4f} s; from rest the lean follows cosh, first doubling at acosh(2) / rate = "
              f"{math.acosh(2.0) / k:.4f} s): RK4 lean at {2 * lean:g} degrees at {t2:.4f} s, {4 * lean:g} degrees at "
              f"{t4:.4f} s ({t4 - t2:.4f} s later), 10 degrees at {t10:.4f} s")
        assert abs(r["t_flat"] - q_flat) < 1e-6 and abs(r["t_45"] - q_45) < 1e-6, "RK4 disagrees with the quadrature"
        assert err_w2 < 1e-6 and abs(wf - wf_closed) < 1e-6, "RK4 disagrees with the energy form"
        ct = foot_push(r, g, L)
        kmin = int(np.argmin(ct["Hy"]))
        kmax = int(np.argmax(ct["Hx"]))
        over = np.nonzero(np.abs(ct["Hx"]) > ct["Hy"])[0]
        k1 = int(over[0]) if len(over) else -1
        rev = np.nonzero(ct["Hx"] < 0.0)[0]
        krev = int(rev[0]) if len(rev) else -1
        print(f"  {m}: the foot's push on the stick (weights): vertical {ct['Hy'][0]:.4f} and horizontal {ct['Hx'][0]:+.4f} "
              f"(forward, toward the fall) at the release; the forward push peaks at {ct['Hx'][kmax]:+.3f} at "
              f"{math.degrees(ct['th'][kmax]):.1f} degrees and reverses at {math.degrees(ct['th'][krev]):.1f} degrees "
              f"(closed form cos theta = 2/3: {math.degrees(math.acos(2.0 / 3.0)):.1f} degrees); the vertical push falls to "
              f"{ct['Hy'][kmin]:.4f} at {math.degrees(ct['th'][kmin]):.1f} degrees (closed form (3 cos theta - 1)^2 / 4, "
              f"zero at cos theta = 1/3: {math.degrees(math.acos(1.0 / 3.0)):.1f} degrees) and is {ct['Hy'][-1]:.4f} at the "
              f"floor; the sideways pull back toward the foot grows late in the fall to {abs(ct['Hx'][-1]):.4f} weights "
              f"at the floor (closed form (3/2) cos theta0 = {1.5 * math.cos(th0):.4f}); the sideways push exceeds the "
              f"vertical push from {math.degrees(ct['th'][k1]):.1f} degrees on, so a foot on a plain floor would slip: "
              f"it must be held")
        ev[f"push_{m}"] = {"Hy_min": float(ct["Hy"][kmin]), "Hy_min_deg": math.degrees(ct["th"][kmin]),
                           "Hx_floor": float(ct["Hx"][-1]), "Hx_max": float(ct["Hx"][kmax]),
                           "Hx_max_deg": math.degrees(ct["th"][kmax]), "slip_deg": math.degrees(ct["th"][k1])}
    tb, tp = runs["broom"]["t_flat"], runs["pencil"]["t_flat"]
    ratio = tb / tp
    ratio45 = runs["broom"]["t_45"] / runs["pencil"]["t_45"]
    root = math.sqrt(Ls["broom"] / Ls["pencil"])
    ev["ratio"], ev["root"] = ratio, root
    print(f"the two panels: the broom is flat at {tb:.4f} s = {tb:.2f} s (one and a half seconds) against {tp:.4f} s = "
          f"{tp:.2f} s (half a second) for the pencil, {tb - tp:.4f} s apart; the ratio of the flat times is "
          f"{ratio:.5f} = {ratio:.1f} times longer (two point eight times; {ratio:.2f}x) = exactly sqrt({Ls['broom'] / Ls['pencil']:g}) = "
          f"{root:.5f} (diff {ratio - root:+.1e}); the ratio of the 45-degree times is {ratio45:.5f} (diff "
          f"{ratio45 - root:+.1e}); the ratio of the lean doublings is the same: in the scaled time "
          f"tau = t sqrt(3 g / (2 L)) the equation is theta'' = sin theta for every length, so every time in the fall "
          f"scales with sqrt(L): the pencil's fall is the broom's fall played {root:.4f} times faster; the broom is "
          f"{Ls['broom'] / Ls['pencil']:g} times as long, so its fall takes sqrt({Ls['broom'] / Ls['pencil']:g}) = "
          f"{root:.3f} times longer at every angle")
    assert abs(ratio - root) < 1e-5 and abs(ratio45 - root) < 1e-5, "the time ratio is not sqrt(L ratio)"
    # For the description: other leans of the broom and other lengths at the same lean.
    descr = []
    ev["leans"] = {}
    Lb = Ls["broom"]
    for ln in man["description_leans_deg"]:
        r0 = simulate(math.radians(ln), g, Lb, dt, man["sim_end_s"])
        q0 = time_quadrature(math.radians(ln), g, Lb, math.pi / 2.0)
        ev["leans"][ln] = r0["t_flat"]
        descr.append(f"the broom from {ln:g} degrees: 45 degrees at {r0['t_45']:.4f} s, flat at {r0['t_flat']:.4f} s "
                     f"(quadrature {q0:.4f} s)")
        assert abs(r0["t_flat"] - q0) < 1e-6
    ev["lengths"] = {}
    for L2 in man["description_lengths_m"]:
        r2 = simulate(th0, g, L2, dt, man["sim_end_s"])
        ev["lengths"][L2] = r2["t_flat"]
        descr.append(f"a {L2:g} m stick ({L2 * 100:g} cm) from {lean:g} degree: 45 degrees at {r2['t_45']:.4f} s, flat at {r2['t_flat']:.4f} s "
                     f"(sqrt({L2:g} / {Lb:g}) = {math.sqrt(L2 / Lb):.4f} times the broom's {tb:.4f} s = "
                     f"{math.sqrt(L2 / Lb) * tb:.4f} s), {r2['w_flat']:.3f} rad/s and tip {L2 * r2['w_flat']:.2f} m/s at the floor")
    print("for the description (same model): " + "; ".join(descr))
    half = {m: simulate(th0, g, Ls[m], 0.5 * dt, man["sim_end_s"]) for m in PANELS}
    print("check at half the time step (" + f"{2 * man['steps_per_second']} steps per second): " + "; ".join(
        f"{m} flat at {half[m]['t_flat']:.7f} s ({half[m]['t_flat'] - runs[m]['t_flat']:+.1e}), 45 degrees at "
        f"{half[m]['t_45']:.7f} s ({half[m]['t_45'] - runs[m]['t_45']:+.1e}), {half[m]['w_flat']:.6f} rad/s at the floor "
        f"({half[m]['w_flat'] - runs[m]['w_flat']:+.1e})" for m in PANELS)
        + f"; ratio {half['broom']['t_flat'] / half['pencil']['t_flat']:.6f}")
    for m in PANELS:
        assert abs(half[m]["t_flat"] - runs[m]["t_flat"]) < 1e-6
    # Schedule in video time.
    t0 = man["first_cycle_at"]
    k0 = math.floor((0.0 - t0) / P + 1e-9)
    k1 = math.floor((D - t0) / P - 1e-9)
    starts = [t0 + k * P for k in range(k0, k1 + 1)]
    ev["cycles"] = int(round(cycles))

    def lst(off_: float) -> str:
        return ", ".join(f"{s + off_:.2f}" for s in starts if 0.0 <= s + off_ < D)

    tau0 = (0.0 - t0) % P
    r0 = (tau0 - ra) / S
    st0 = {m: state_at(runs[m], r0) for m in PANELS}
    print(f"schedule (video time, 1/{S:g} speed): cycles of {P:g} s start at " + ", ".join(f"{s:.2f}" for s in starts)
          + (f" s (the first {-t0:.2f} s before the first frame)" if t0 < 0.0 else " s (the first on the first frame)")
          + f"; the release {ra:g} s into each cycle at {lst(ra)} s; the "
          f"pencil passes 45 degrees {runs['pencil']['t_45'] * S:.2f} s after the release at {lst(ra + runs['pencil']['t_45'] * S)} s "
          f"and lies flat {tp * S:.2f} s after the release at {lst(ra + tp * S)} s; the broom passes 10 degrees "
          f"{crossing_time(runs['broom'], math.radians(10.0)) * S:.2f} s after the release at "
          f"{lst(ra + crossing_time(runs['broom'], math.radians(10.0)) * S)} s, 45 degrees {runs['broom']['t_45'] * S:.2f} s after "
          f"at {lst(ra + runs['broom']['t_45'] * S)} s and lies flat {tb * S:.2f} s after the release at {lst(ra + tb * S)} s; "
          f"both lie flat with their readouts until the reset fade, which crossfades back to the standing stick over "
          f"{F:g} s ending {man['reset_hold']:g} s before the cycle's end (out over {Pe - F:.2f} to {Pe - F / 2:.2f} s, in "
          f"over {Pe - F / 2:.2f} to {Pe:.2f} s after the cycle start, at {lst(Pe - F)} s), then both stand held from "
          f"{Pe:.2f} s to the next release at {P + ra:.2f} s; on the first frame the cycle is {tau0:.2f} s in ({abs(r0):.3f} s real "
          f"{'after' if r0 >= 0.0 else 'before'} the release): the broom at {math.degrees(st0['broom'][0]):.1f} degrees, the "
          f"pencil at {math.degrees(st0['pencil'][0]):.1f} degrees, {'falling' if r0 >= 0.0 else 'held at rest'}; title "
          f"until {man['title_until']:g} s; payoff card from "
          f"{man['payoff_t']:g} s; the title fades back in over the last {man['loop_fade']:g} s and the last frame "
          f"repeats the first (the scene is periodic: {D:g} s holds exactly {cycles:.0f} cycles)")
    # Text widths.
    font = os.environ["SEED_ZERO_FONT"]
    f24, f28, f34, f40, f56 = (ImageFont.truetype(font, n) for n in (24, 28, 34, 40, 56))
    widths = {"overlay@34": (f34, man["overlay"])}
    for j, line in enumerate(man["title"].split("|")):
        widths[f"title line {j + 1}@56"] = (f56, line)
    widths["legend@40"] = (f40, legend_text(man))
    widths["clock@28"] = (f28, clock_text(1.4985))
    widths["clock rest@28"] = (f28, clock_text(-1.0))
    for m in PANELS:
        widths[f"label {m}@40"] = (f40, label_text(man, m))
        widths[f"sublabel {m}@28"] = (f28, sub_text(man))
        widths[f"fixed {m}@28"] = (f28, fixed_text())
        widths[f"event {m}@40"] = (f40, event_text(ev, m))
        widths[f"tick {m}@24"] = (f24, tick_text(ev, m))
        widths[f"tip {m}@28"] = (f28, tip_text(Ls[m] * runs[m]["w_flat"]))
    widths["angle@40"] = (f40, angle_text(90.0))
    widths["band clock@28"] = (f28, band_clock_text(1.4985))
    for j, line in enumerate(payoff_lines(man, ev)):
        widths[f"payoff line {j + 1}@40"] = (f40, line)
    print("text widths: " + ", ".join(f"{k} {f.getlength(s):.0f} px" for k, (f, s) in widths.items()))
    assert all(f.getlength(s) < 950 for f, s in widths.values()), "a text line is wider than 950 px"
    assert len(payoff_lines(man, ev)) <= 6, "the card has more than six lines"
    # Layout checks: the standing stick's cap clears the text rows, the left column, the right
    # column, the 45-degree label and the event row all sit outside the tip's arc, the finger
    # stays in the band and the card clears the caption band.
    fx, fdy = float(man["foot_x_px"]), float(man["foot_dy"])
    hy = fdy - BAR_R
    R = stick_px
    rows_bottom = FIX_DY + 16
    tip_top = hy - R - BAR_R
    left = ROW_X0 + max(max(f40.getlength(label_text(man, m)), f28.getlength(sub_text(man)), f28.getlength(fixed_text()))
                        for m in PANELS)
    right = ROW_X1 - max(f40.getlength(angle_text(90.0)), f28.getlength(band_clock_text(1.4985)),
                         max(f28.getlength(tip_text(Ls[m] * runs[m]["w_flat"])) for m in PANELS))
    ev_w = max(f40.getlength(event_text(ev, m)) for m in PANELS)
    ev_x0, ev_y0 = EVENT_X - ev_w / 2.0, EVENT_DY - 22
    d_event = math.hypot(ev_x0 - fx, ev_y0 - hy)
    tk_w = max(f24.getlength(tick_text(ev, m)) for m in PANELS)
    u = math.sqrt(0.5)
    tk_x, tk_y = fx + (R + TICK_LABEL_GAP) * u, hy - (R + TICK_LABEL_GAP) * u
    d_tick = math.hypot(tk_x - fx, tk_y + 14 - hy)   # the label's lower-left corner is its nearest point
    d_right = math.hypot(right - fx, rows_bottom - hy)
    finger_top = fdy
    print(f"row check: the left column ends at x {left:.0f} px and the right column starts at x {right:.0f} px; both end "
          f"{rows_bottom} px under the band top and the standing stick (at x {fx:.0f} px) tops out at {tip_top:.0f} px "
          f"under the band top with its cap, {tip_top - rows_bottom:.0f} px under the rows; the hinge is at ({fx:.0f}, {hy:.0f}) and the tip's arc has radius {R:.0f} px "
          f"(plus the {BAR_R:.0f} px cap), so the flat stick reaches x {fx + R + BAR_R:.0f} px; the right column's corner "
          f"is {d_right:.0f} px from the hinge, the event row's corner {d_event:.0f} px and the 45-degree label's corner "
          f"{d_tick:.0f} px (its text to x {tk_x + tk_w:.0f} px); the fingertip spans x {fx - FINGER_W / 2:.0f} to "
          f"{fx + FINGER_W / 2:.0f} px from {finger_top:.0f} px under the band top to the band bottom; each band is "
          f"{BAND_H} px tall (y {BAND_Y['broom']} to {BAND_Y['broom'] + BAND_H} and {BAND_Y['pencil']} to "
          f"{BAND_Y['pencil'] + BAND_H}); the caption band starts at y {int(man['caption_y'] * H)}; the title rows end at "
          f"y {252 + 28} and the overlay band ends at y 130")
    assert tip_top > rows_bottom + 8, "the standing stick reaches the text rows"
    assert d_right > R + BAR_R + 8, "the right column meets the tip's arc"
    assert d_event > R + BAR_R + 8 and EVENT_X + ev_w / 2.0 < W - 30, "the event row meets the arc or the frame edge"
    assert d_tick > R + BAR_R + 8 and tk_x + tk_w < W - 30, "the 45-degree label meets the arc or the frame edge"
    assert fx + R + BAR_R < right - 8 or hy > rows_bottom + 20, "the flat stick meets the right column"
    assert finger_top + 24 < BAND_H, "the fingertip has no room in the band"
    assert BAND_Y["pencil"] + BAND_H <= int(man["caption_y"] * H), "the bottom band reaches the caption band"
    assert PAYOFF_Y - 20 > int(man["caption_y"] * H) + 90, "the card meets the caption band"
    return ev


def legend_text(man: dict) -> str:
    return f"each stick drawn to fit, 1/{man['slow']:g} speed"


def clock_text(r: float) -> str:
    return "held, at rest" if r < 0.0 else f"{r:.3f} s after the release"


def label_text(man: dict, m: str) -> str:
    return man["sticks"][m]["label"]


def sub_text(man: dict) -> str:
    return f"{man['lean_deg']:g} degree off vertical"


def fixed_text() -> str:
    return "the foot stays on the finger"


def angle_text(deg: float) -> str:
    return f"{deg:.1f} degrees"


def band_clock_text(r: float) -> str:
    return f"{max(0.0, r):.3f} s"


def tip_text(v: float) -> str:
    return f"tip {v:.2f} m/s"


def event_text(ev: dict, m: str) -> str:
    return f"flat at {ev['runs'][m]['t_flat']:.3f} s"


def tick_text(ev: dict, m: str) -> str:
    return f"45 degrees at {ev['runs'][m]['t_45']:.3f} s"


def payoff_lines(man: dict, ev: dict) -> list[str]:
    text = man["payoff_text"].format(
        t_broom=ev["runs"]["broom"]["t_flat"], t_pencil=ev["runs"]["pencil"]["t_flat"], ratio=ev["ratio"],
        t45_broom=ev["runs"]["broom"]["t_45"], t45_pencil=ev["runs"]["pencil"]["t_45"],
        t_ruler=ev["lengths"][0.3], t_pole=ev["lengths"][4.8])
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
        self.th0 = math.radians(man["lean_deg"])
        self.S = man["slow"]
        self.P = man["cycle_s"]
        self.P_f = int(round(man["cycle_s"] * self.fps))
        self.c0_f = int(round(man["first_cycle_at"] * self.fps))
        self.ra, self.F = man["release_at"], man["reset_fade"]
        self.Pe = man["cycle_s"] - man["reset_hold"]   # the reset crossfade ends here
        self.runs = ev["runs"]
        self.Ls = ev["Ls"]
        self.R = float(man["stick_px"])
        self.fx = float(man["foot_x_px"])
        self.fdy = float(man["foot_dy"])
        self.hy = self.fdy - BAR_R   # the hinge (the stick's axis at the foot), band-local

    def phase(self, f: int) -> tuple[int, float]:
        k, tau_f = divmod(f - self.c0_f, self.P_f)
        return k, tau_f / self.fps

    @staticmethod
    def L_(x: float, y: float) -> tuple[float, float]:
        """Layer (2x) pixel of a band-local point, rounded to 1e-4 px so equal states draw equal pixels."""
        return round(x * SS, 4), round(y * SS, 4)

    def tip(self, th: float) -> tuple[float, float]:
        return self.fx + self.R * math.sin(th), self.hy - self.R * math.cos(th)

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

    def draw_static(self, d: ImageDraw.ImageDraw) -> None:
        """The fingertip, the vertical ghost, the flat guide, the tip's arc and the 45-degree tick."""
        fx, hy, R = self.fx, self.hy, self.R
        # The tip's path and the flat guide.
        c0, c1 = self.L_(fx - R, hy - R), self.L_(fx + R, hy + R)
        d.arc((c0[0], c0[1], c1[0], c1[1]), 270.0, 360.0, fill=ARC, width=2 * SS)
        self.dashed(d, self.L_(fx + 2 * BAR_R, hy), self.L_(fx + R, hy), ARC, 10 * SS, 8 * SS, 2 * SS)
        # The ghost of the vertical start.
        g0, g1 = self.L_(fx, hy), self.L_(fx, hy - R)
        self.dashed(d, g0, g1, GHOST, 14 * SS, 9 * SS, 3 * SS)
        r = BAR_R * SS
        d.ellipse((g1[0] - r, g1[1] - r, g1[0] + r, g1[1] + r), outline=GHOST, width=2 * SS)
        # The 45-degree tick across the arc.
        u = math.sqrt(0.5)
        t0, t1 = self.L_(fx + (R - 12) * u, hy - (R - 12) * u), self.L_(fx + (R + 12) * u, hy - (R + 12) * u)
        d.line((*t0, *t1), fill=MUTED, width=3 * SS)
        # The fingertip under the foot: a rounded finger rising from the band bottom, with a nail.
        x0, x1 = fx - FINGER_W / 2.0, fx + FINGER_W / 2.0
        p0, p1 = self.L_(x0, self.fdy), self.L_(x1, BAND_H + 40)
        d.rounded_rectangle((p0[0], p0[1], p1[0], p1[1]), radius=int(FINGER_W / 2 * SS), fill=SKIN, outline=SKIN_DARK,
                            width=2 * SS)
        n0, n1 = self.L_(fx - 11, self.fdy + 8), self.L_(fx + 11, self.fdy + 26)
        d.ellipse((n0[0], n0[1], n1[0], n1[1]), fill=NAIL)

    def draw_stick(self, d: ImageDraw.ImageDraw, m: str, th: float, a: float) -> None:
        col = blend(COLOUR[m], a)
        p_f = self.L_(self.fx, self.hy)
        p_t = self.L_(*self.tip(th))
        r = BAR_R * SS
        d.line((*p_f, *p_t), fill=col, width=int(2 * r))
        d.ellipse((p_f[0] - r, p_f[1] - r, p_f[0] + r, p_f[1] + r), fill=col)
        d.ellipse((p_t[0] - r, p_t[1] - r, p_t[0] + r, p_t[1] + r), fill=col)
        rt = (BAR_R + 3) * SS
        d.ellipse((p_t[0] - rt, p_t[1] - rt, p_t[0] + rt, p_t[1] + rt), fill=blend(GOLD, a))
        pr = 5 * SS
        d.ellipse((p_f[0] - pr, p_f[1] - pr, p_f[0] + pr, p_f[1] + pr), fill=BG, outline=blend(WHITE, a), width=2 * SS)

    def draw_scene(self, d: ImageDraw.ImageDraw, m: str, tau: float, a: float) -> dict:
        """The moving parts of one panel tau seconds into a cycle, blended by a."""
        man = self.man
        r = (tau - self.ra) / self.S
        run = self.runs[m]
        th, w, landed = state_at(run, r)
        self.draw_stick(d, m, th, a)
        if landed:
            u = (tau - (self.ra + run["t_flat"] * self.S)) / man["land_flash"]
            if 0.0 <= u < 1.0:
                p_t = self.L_(*self.tip(math.pi / 2.0))
                rr = (22 + 70 * u) * SS
                d.ellipse((p_t[0] - rr, p_t[1] - rr, p_t[0] + rr, p_t[1] + rr), outline=blend(WHITE, (1 - u) * a),
                          width=4 * SS)
        return {"theta": th, "omega": w, "landed": landed, "r": r, "alpha": a}

    def draw_panel(self, m: str, f: int) -> tuple[Image.Image, dict]:
        layer = Image.new("RGB", (W * SS, BAND_H * SS), BG)
        d = ImageDraw.Draw(layer)
        self.draw_static(d)
        k, tau = self.phase(f)
        F, P, Pe = self.F, self.P, self.Pe
        a_old = 1.0 if tau <= Pe - F else max(0.0, (Pe - F / 2.0 - tau) / (F / 2.0))
        st = self.draw_scene(d, m, tau, a_old) if a_old > 0.0 else None
        if tau >= Pe - F / 2.0:
            a_new = min(1.0, (tau - (Pe - F / 2.0)) / (F / 2.0))
            st_new = self.draw_scene(d, m, tau - P, a_new)
            if st is None or a_new >= 0.5:
                st = st_new
        st["k"] = k
        return layer, st

    def draw_text(self, d: ImageDraw.ImageDraw, states: dict, hud_alpha: float) -> None:
        man, ev = self.man, self.ev
        u = math.sqrt(0.5)
        for m, st in states.items():
            y0 = BAND_Y[m]
            a = st["alpha"]
            L = self.Ls[m]
            d.text((ROW_X0, y0 + LABEL_DY), label_text(man, m), font=self.font, fill=COLOUR[m], anchor="lm")
            d.text((ROW_X0, y0 + SUB_DY), sub_text(man), font=self.font_small, fill=MUTED, anchor="lm")
            d.text((ROW_X0, y0 + FIX_DY), fixed_text(), font=self.font_small, fill=MUTED, anchor="lm")
            landed = st["landed"]
            r_show = min(max(st["r"], 0.0), self.runs[m]["t_flat"])
            d.text((ROW_X1, y0 + LABEL_DY), angle_text(math.degrees(st["theta"])), font=self.font,
                   fill=blend(GOLD if landed else TEXT, a), anchor="rm")
            d.text((ROW_X1, y0 + SUB_DY), band_clock_text(r_show), font=self.font_small,
                   fill=blend(GOLD if landed else TEXT, a), anchor="rm")
            d.text((ROW_X1, y0 + FIX_DY), tip_text(L * st["omega"]), font=self.font_small, fill=blend(MUTED, a), anchor="rm")
            if landed:
                d.text((EVENT_X, y0 + EVENT_DY), event_text(ev, m), font=self.font, fill=blend(GOLD, a), anchor="mm")
            tx, ty = self.fx + (self.R + TICK_LABEL_GAP) * u, self.hy - (self.R + TICK_LABEL_GAP) * u
            d.text((tx, y0 + ty), tick_text(ev, m), font=self.font_tiny, fill=MUTED, anchor="lm")
        if hud_alpha > 0.02:
            d.text((W / 2, LEGEND_Y), legend_text(man), font=self.font, fill=blend(TEXT, hud_alpha), anchor="mm")
            d.text((W / 2, CLOCK_Y), clock_text(states["broom"]["r"]), font=self.font_small,
                   fill=blend(MUTED, hud_alpha), anchor="mm")

    def live_frame(self, f: int, title_alpha: float | None = None, hud_alpha: float = 0.0) -> np.ndarray:
        """Frame f with the geometry at f / fps; title_alpha and hud_alpha override the title and the
        legend/clock/card blend during the loop fade."""
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
    man = json.loads((ROOT / "projects/broom/manifest.json").read_text())
    ev = measure(man)
    if "--measure-only" in sys.argv:
        return
    if "--frames" in sys.argv:
        times = [float(v) for v in sys.argv[sys.argv.index("--frames") + 1].split(",")]
        r = Renderer(man, ev)
        (ROOT / "media/broom").mkdir(parents=True, exist_ok=True)
        for tv in times:
            Image.fromarray(r.frame_at(int(round(tv * man["fps"])))).save(ROOT / f"media/broom/smoke-{tv}.png")
        print("smoke frames: " + ", ".join(f"{tv}" for tv in times))
        return
    Renderer(man, ev).render(ROOT / "media/broom/footage.mp4")


if __name__ == "__main__":
    main()
