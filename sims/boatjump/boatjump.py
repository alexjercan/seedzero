#!/usr/bin/env python3
"""Jump from a boat to the dock: does it matter if the boat is tied?

Two panels on the same clock, the same boat drawn the same way at the same
scale, side view: a jumper of mass m (a point mass) stands at the bow of a
light boat of mass M on still water; the dock edge is D metres from the bow
at the boat's floor height. The legs give the jumper a takeoff of u at an
angle alpha relative to the boat (the textbook form: the push is defined
by the relative speed). During the push the horizontal momentum of jumper
plus boat is conserved; the vertical impulse m u sin(alpha) goes into the
water through the hull, so the boat does not move vertically. No water
drag on the boat and no air drag in the flight (chosen). Top panel, the
FREE boat: the jumper leaves at v_j = u_x M / (M + m) over the ground and
the boat recoils at v_b = -u_x m / (M + m). Bottom panel, the TIED boat (a
taut rope to the dock takes the recoil): the jumper leaves at u_x. Both
flights last T = 2 u_y / g, reach the apex u_y^2 / (2 g) and land at v T;
the ratio of the two landing distances is exactly (M + m) / M. Both
flights are integrated by RK4 at steps_per_second (x, y of the jumper; x
of the boat), the landing at the floor level located by bisection inside
the step, checked against the closed forms and a half-step rerun; the
drawing follows the RK4 table. The run repeats every cycle_s seconds of
video with a crossfade back to the standing setup; the cycle divides the
scene length, so the scene is exactly periodic and the last frame equals
the first. Shown at 1/slow speed. Deterministic, no seed.

Measured and printed: the takeoff speeds over the ground, the flight time
and apex, the landing distances against the dock (short or past), the
boat's recoil, the ratio, the momentum balance and the vertical impulse,
the kinetic energy after the push, the table at 0.1 s steps, the boat-mass
and takeoff variants for the description, the checks against the brief,
the schedule in video time, the on-screen text widths and the layout
clearances.

usage: boatjump.py [--measure-only] [--frames t1,t2,...]
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
HULL = (54, 62, 76)
HULL_EDGE = (150, 160, 176)
WATER = (14, 34, 66)
FOAM = (170, 205, 230)
ROPE = (214, 190, 140)
INK = (150, 158, 170)

# Layout: overlay at y 96..130 (captions.py), three title rows at y 186/244/302
# for the first seconds, then the legend at y 236 and the shared clock at y
# 290; two bands stacked, the free boat in y 330..880 and the tied boat in y
# 880..1430, each drawn at 2x in its own layer (so nothing leaves its band);
# each band has its label row 40 px under the band top, its second row at 84
# and its third at 120 (left column from x 40, right column to x 1040); the
# floor level (the boat's floor and the dock top) at floor_dy under the band
# top, the water line water_dy under it, the water down to the band bottom;
# the hull block ends at the bow at bow_x_px, the dock block starts a gap
# (gap_m * px_per_m) right of the bow; the gold mark label at MARK_LABEL_DY
# over the dashed gap line at MARK_DY (above the arc's apex); the gold event
# row in the water at 480; captions at caption_y 0.75 (y 1440..1530); the
# six-line card from y 1572 at a 48 px pitch.
LEGEND_Y, CLOCK_Y = 236, 290
TITLE_Y = (186, 244, 302)
SS = 2
PAYOFF_Y, PAYOFF_PITCH = 1572.0, 48
PANELS = ("free", "tied")
BAND_Y = {"free": 330, "tied": 880}
BAND_H = 550
LABEL_DY, SUB_DY, FIX_DY = 40, 84, 120
EVENT_DY, EVENT_X = 480, 440
MARK_DY, MARK_LABEL_DY = 206, 180
ROW_X0, ROW_X1 = 40, 1040
HEAD_R, FIG_H, FIG_LEG, FIG_ARM = 4.5, 22.0, 7.0, 7.0
TRAIL_EVERY_S = 0.004
HULL_TAPER = 18.0
COLOUR = {"free": CORAL, "tied": TEAL}
HELD, AIR, DOWN = "held", "air", "down"


def blend(col, a: float, base=BG) -> tuple:
    a = max(0.0, min(1.0, a))
    return tuple(int(round(c * a + b * (1 - a))) for c, b in zip(col, base))


# --- measurement --------------------------------------------------------------
def closed(m: float, M: float, u: float, a_deg: float, g: float, free: bool) -> dict:
    """The closed forms: takeoff speeds over the ground, flight time, apex, landing distance, recoil."""
    a = math.radians(a_deg)
    ux, uy = u * math.cos(a), u * math.sin(a)
    if free:
        vj, vb = ux * M / (M + m), -ux * m / (M + m)
    else:
        vj, vb = ux, 0.0
    T = 2.0 * uy / g
    return {"ux": ux, "uy": uy, "vj": vj, "vb": vb, "T": T, "apex": uy * uy / (2.0 * g), "x_land": vj * T, "xb_land": vb * T}


def rk4_flight(vj: float, uy: float, vb: float, g: float, dt: float) -> dict:
    """Integrate the jumper (x, y, vx, vy) and the boat (xb) from the takeoff by classical RK4 at dt until the
    jumper is back at the floor level y = 0; the landing is located by bisection on the last step. Returns the
    table (t, x, y, xb), the landing and the step count."""

    def f(s: np.ndarray) -> np.ndarray:
        return np.array([s[2], s[3], 0.0, -g, vb])

    def step(s: np.ndarray, h: float) -> np.ndarray:
        k1 = f(s)
        k2 = f(s + 0.5 * h * k1)
        k3 = f(s + 0.5 * h * k2)
        k4 = f(s + h * k3)
        return s + h * (k1 + 2.0 * k2 + 2.0 * k3 + k4) / 6.0

    s = np.array([0.0, 0.0, vj, uy, 0.0])
    ts, xs, ys, xbs = [0.0], [0.0], [0.0], [0.0]
    n = 0
    while True:
        sn = step(s, dt)
        if sn[1] < 0.0 and n > 0:
            lo, hi = 0.0, dt
            for _ in range(80):
                mid = 0.5 * (lo + hi)
                if step(s, mid)[1] > 0.0:
                    lo = mid
                else:
                    hi = mid
            sl = step(s, hi)
            t_land = n * dt + hi
            ts.append(t_land)
            xs.append(float(sl[0]))
            ys.append(0.0)
            xbs.append(float(sl[4]))
            n += 1
            break
        n += 1
        s = sn
        ts.append(n * dt)
        xs.append(float(s[0]))
        ys.append(float(s[1]))
        xbs.append(float(s[4]))
    return {"t": np.array(ts), "x": np.array(xs), "y": np.array(ys), "xb": np.array(xbs), "t_land": t_land,
            "x_land": float(sl[0]), "xb_land": float(sl[4]), "vy_land": float(sl[3]), "steps": n}


def state_at(run: dict, rt: float) -> dict:
    """(x, y, xb, phase, t_air) rt real seconds after the takeoff; the run holds at the landing."""
    if rt < 0.0:
        return {"x": 0.0, "y": 0.0, "xb": 0.0, "phase": HELD, "t_air": 0.0}
    if rt < run["t_land"]:
        return {"x": float(np.interp(rt, run["t"], run["x"])), "y": float(np.interp(rt, run["t"], run["y"])),
                "xb": float(np.interp(rt, run["t"], run["xb"])), "phase": AIR, "t_air": rt}
    return {"x": run["x_land"], "y": 0.0, "xb": run["xb_land"], "phase": DOWN, "t_air": run["t_land"]}


def measure(man: dict) -> dict:
    g, m, M, u, a_deg, D = man["g"], man["jumper_kg"], man["boat_kg"], man["takeoff_m_s"], man["angle_deg"], man["gap_m"]
    dt = 1.0 / man["steps_per_second"]
    S, P, Dur, fps, F, pa = man["slow"], man["cycle_s"], man["scene_duration"], man["fps"], man["reset_fade"], man["takeoff_at"]
    cycles = Dur / P
    assert abs(cycles - round(cycles)) < 1e-9, "the cycle must divide the scene length"
    for key in ("cycle_s", "takeoff_at", "first_cycle_at", "reset_fade", "splash_s", "sink_s"):
        assert abs(man[key] * fps - round(man[key] * fps)) < 1e-9, f"{key} must be a whole number of frames"
    ppm = man["px_per_m"]
    print(f"setup: side view, two panels on one clock, the same boat drawn the same way at the same scale: a jumper of "
          f"{m:g} kg (a point mass) stands at the bow of a light dinghy of {M:g} kg on still water; the dock edge is "
          f"{D:g} m from the bow at the boat's floor height; the legs give a takeoff of {u:g} m/s at {a_deg:g} degrees "
          f"relative to the boat (the textbook form: the push is defined by the relative speed); the horizontal momentum "
          f"of jumper plus boat is conserved during the push; the vertical impulse goes into the water through the hull, "
          f"so the boat does not move vertically; no water drag on the boat and no air drag in the flight (chosen); "
          f"g = {g:g} m/s^2; top panel the boat is free, bottom panel a taut rope to the dock takes the recoil; both "
          f"flights integrated by classical RK4 at {man['steps_per_second']} steps per second (dt = {dt:.0e} s) on the "
          f"jumper's x, y and the boat's x, the landing at the floor level located by bisection inside the step, checked "
          f"against the closed forms and a half-step rerun; the run holds at the landing; shown at 1/{S:g} speed on a "
          f"{P:g} s cycle ({P * fps:.0f} frames) with the takeoff {pa:g} s into the cycle, {cycles:.0f} cycles in "
          f"{Dur:g} s; drawn at {ppm:g} px per metre with a {man['hull_m']:g} m hull; deterministic, no seed")
    cf = closed(m, M, u, a_deg, g, free=False)
    print(f"takeoff: u_x = u cos a = {cf['ux']:.4f} m/s, u_y = u sin a = {cf['uy']:.4f} m/s; flight T = 2 u_y / g = "
          f"{cf['T']:.4f} s, apex u_y^2 / 2g = {cf['apex']:.4f} m; vertical impulse m u_y = {m * cf['uy']:.1f} N s into "
          f"the water through the hull")
    ev: dict = {"runs": {}, "closed": {}}
    for key in PANELS:
        free = key == "free"
        c = closed(m, M, u, a_deg, g, free)
        run = rk4_flight(c["vj"], c["uy"], c["vb"], g, dt)
        half = rk4_flight(c["vj"], c["uy"], c["vb"], g, 0.5 * dt)
        err_x = float(np.max(np.abs(run["x"] - c["vj"] * run["t"])))
        err_y = float(np.max(np.abs(run["y"] - (c["uy"] * run["t"] - 0.5 * g * run["t"] ** 2))))
        ev["runs"][key], ev["closed"][key] = run, c
        if free:
            how = f"the jumper leaves at u_x M / (M + m) = {c['vj']:.4f} m/s over the ground, the boat recoils at u_x m / (M + m) = {-c['vb']:.4f} m/s"
            where = f"{(D - run['x_land']) * 100:.1f} cm short of the dock, in the water; the boat is {-run['xb_land']:.4f} m back by then"
        else:
            how = f"the rope takes the recoil, so the jumper leaves at u_x = {c['vj']:.4f} m/s over the ground and the boat stays at 0 m/s"
            where = f"{(run['x_land'] - D) * 100:.1f} cm past the edge, on the dock; the boat has moved {run['xb_land']:.4f} m"
        print(f"{key} boat ({'top' if free else 'bottom'} panel): {how}; RK4 from the takeoff: lands {run['t_land']:.6f} s "
              f"= {run['t_land']:.4f} s later at x {run['x_land']:.6f} m = {run['x_land']:.4f} m out (closed form "
              f"2 u_y / g = {c['T']:.4f} s, v T = {c['x_land']:.4f} m; diffs {run['t_land'] - c['T']:+.1e} s, "
              f"{run['x_land'] - c['x_land']:+.1e} m), {run['steps']} steps; the table stays within {err_x:.1e} m of v t "
              f"and {err_y:.1e} m of u_y t - g t^2 / 2; half-step rerun (dt = {0.5 * dt:.0e} s): {half['t_land']:.9f} s "
              f"({half['t_land'] - run['t_land']:+.1e} s) at {half['x_land']:.9f} m ({half['x_land'] - run['x_land']:+.1e} m); "
              f"{where}; vertical speed at the landing {run['vy_land']:.4f} m/s")
        assert abs(run["t_land"] - c["T"]) < 1e-9 and abs(run["x_land"] - c["x_land"]) < 1e-9
        assert abs(half["t_land"] - run["t_land"]) < 1e-9 and err_x < 1e-9 and err_y < 1e-9
    rf, rt_ = ev["runs"]["free"], ev["runs"]["tied"]
    cfr, ct = ev["closed"]["free"], ev["closed"]["tied"]
    assert rf["x_land"] < D < rt_["x_land"], "the free jump must fall short and the tied jump must reach the dock"
    ratio = rt_["x_land"] / rf["x_land"]
    ev["ratio"], ev["short"], ev["past"] = ratio, D - rf["x_land"], rt_["x_land"] - D
    p_h = m * cfr["vj"] + M * cfr["vb"]
    ke_t = 0.5 * m * u * u
    ke_fj = 0.5 * m * (cfr["vj"] ** 2 + cfr["uy"] ** 2)
    ke_fb = 0.5 * M * cfr["vb"] ** 2
    ev["ke"] = {"tied": ke_t, "free": ke_fj + ke_fb, "free_jumper": ke_fj, "free_boat": ke_fb}
    print(f"ratio of the landing distances tied / free = {ratio:.4f} = (M + m) / M = {(M + m) / M:.4f}; horizontal momentum "
          f"of jumper plus free boat after the push m v_j + M v_b = {p_h:.2e} kg m/s (zero: it was zero before); vertical "
          f"impulse {m * cfr['uy']:.1f} N s; kinetic energy after the push: tied m u^2 / 2 = {ke_t:.1f} J; free "
          f"{ke_fj + ke_fb:.1f} J ({ke_fj:.1f} in the jumper and {ke_fb:.1f} in the boat; less: the legs push against a "
          f"boat that is moving away)")
    assert abs(ratio - (M + m) / M) < 1e-9 and abs(p_h) < 1e-9
    table = []
    tt = 0.0
    while tt < rf["t_land"] - 1e-9:
        sf, st = state_at(rf, tt), state_at(rt_, tt)
        table.append((tt, sf, st))
        print(f"  t {tt:.1f} s: free jumper x {sf['x']:.4f} m, y {sf['y']:.4f} m, boat x {sf['xb']:.4f} m; tied jumper "
              f"x {st['x']:.4f} m, y {st['y']:.4f} m, boat x {st['xb']:.4f} m")
        tt = round(tt + 0.1, 6)
    sf, st = state_at(rf, rf["t_land"]), state_at(rt_, rt_["t_land"])
    print(f"  t {rf['t_land']:.4f} s (landing): free jumper x {sf['x']:.4f} m, y {sf['y']:.4f} m, boat x {sf['xb']:.4f} m; "
          f"tied jumper x {st['x']:.4f} m, y {st['y']:.4f} m, boat x {st['xb']:.4f} m")
    ev["table"] = table
    # Description variants.
    descr = []
    ev["boats"] = {}
    for Mb in man["description_boats_kg"]:
        cb = closed(m, Mb, u, a_deg, g, free=True)
        rb = rk4_flight(cb["vj"], cb["uy"], cb["vb"], g, dt)
        ev["boats"][Mb] = rb["x_land"]
        descr.append(f"a {Mb:g} kg boat, free: the jumper at {cb['vj']:.4f} m/s lands {rb['x_land']:.4f} m = {rb['x_land']:.2f} m out "
                     f"({'on the dock' if rb['x_land'] >= D else 'short'}), the boat {-rb['xb_land']:.4f} m back (closed {cb['x_land']:.4f} m)")
    m_need = m * D / (ct["x_land"] - D)
    c_need = closed(m, m_need, u, a_deg, g, free=True)
    ev["m_need"] = m_need
    descr.append(f"the free jump clears {D:g} m only from a boat of at least M = m D / (u_x T - D) = {m_need:.1f} kg "
                 f"(check: a {m_need:.1f} kg boat lands {c_need['x_land']:.4f} m)")
    u_need = math.sqrt(g * D * (M + m) / M / math.sin(2.0 * math.radians(a_deg)))
    c_u = closed(m, M, u_need, a_deg, g, free=True)
    ev["u_need"] = u_need
    descr.append(f"from the {M:g} kg boat the free jump needs a takeoff of u = sqrt(g D (M + m) / (M sin 2a)) = {u_need:.4f} m/s "
                 f"= {u_need:.2f} m/s relative to the boat (check: lands {c_u['x_land']:.4f} m; the landing distance grows as u^2); "
                 f"the research log's {u * D / rf['x_land']:.4f} m/s scaled the speed linearly with the distance, which is not "
                 f"this definition")
    for ad in man["description_angles_deg"]:
        ca, cb = closed(m, M, u, ad, g, free=False), closed(m, M, u, ad, g, free=True)
        descr.append(f"takeoff at {ad:g} degrees: tied {ca['x_land']:.4f} m, free {cb['x_land']:.4f} m (flight {ca['T']:.4f} s)")
    for uu in man["description_takeoffs_m_s"]:
        ca, cb = closed(m, M, uu, a_deg, g, free=False), closed(m, M, uu, a_deg, g, free=True)
        descr.append(f"takeoff {uu:g} m/s: tied {ca['x_land']:.4f} m, free {cb['x_land']:.4f} m")
    v_alt = cfr["ux"] * math.sqrt(M / (M + m))
    descr.append(f"an alternative model with the same push energy instead of the same relative speed (v_j = u_x sqrt(M / (M + m)) = "
                 f"{v_alt:.4f} m/s) lands {v_alt * cfr['T']:.4f} m, still short of {D:g} m; not used")
    print("for the description: " + "; ".join(descr))
    # The brief's checks.
    checks: list[tuple[str, float, float, float]] = [
        ("flight (s)", rf["t_land"], 0.5047, 6e-5), ("apex (m)", ct["apex"], 0.3123, 6e-5),
        ("tied lands (m)", rt_["x_land"], 1.2491, 6e-5), ("tied jumper (m/s)", ct["vj"], 2.4749, 6e-5),
        ("free lands (m)", rf["x_land"], 0.5205, 6e-5), ("free jumper (m/s)", cfr["vj"], 1.0312, 6e-5),
        ("free short (m)", ev["short"], 0.4795, 6e-5), ("boat back (m)", -rf["xb_land"], 0.7286, 6e-5),
        ("boat speed (m/s)", -cfr["vb"], 1.4437, 6e-5), ("ratio", ratio, 2.4000, 6e-5),
        ("vertical impulse (N s)", m * cfr["uy"], 173.2, 6e-2), ("mass to clear 1 m (kg)", m_need, 281.0, 6e-2),
        ("takeoff to clear 1 m (m/s)", u_need, 4.85, 6e-3),
        ("kinetic energy tied (J)", ke_t, 428.8, 6e-2), ("kinetic energy free (J)", ke_fj + ke_fb, 303.7, 6e-2),
        ("free jumper energy (J)", ke_fj, 251.6, 6e-2), ("free boat energy (J)", ke_fb, 52.1, 6e-2),
    ]
    for Mb, want in ((30.0, 0.37), (100.0, 0.73), (200.0, 0.93), (400.0, 1.06)):
        if Mb in ev["boats"]:
            checks.append((f"{Mb:g} kg boat lands (m)", ev["boats"][Mb], want, 6e-3))
    fails = 0
    out = []
    for name, got, want, tol in checks:
        ok = abs(got - want) <= tol
        fails += 0 if ok else 1
        out.append(f"{name}: brief {want:g}, sim {got:.6g}, diff {got - want:+.1e}: {'ok' if ok else 'FAIL'}")
    print(f"checks against the brief ({len(checks)} checks, {fails} failed): " + "; ".join(out))
    ev["check_fails"] = fails
    # The schedule in video time.
    t0 = man["first_cycle_at"]
    k0 = math.ceil((0.0 - t0) / P - 1e-9) - 1
    k1 = math.floor((Dur - t0) / P - 1e-9)
    starts = [t0 + kk * P for kk in range(k0, k1 + 1)]
    ev["cycles"] = int(round(cycles))

    def lst(off_: float) -> str:
        return ", ".join(f"{st + off_:.2f}" for st in starts if 0.0 <= st + off_ < Dur)

    water_m = man["water_dy"] / ppm
    # The free jumper's dot runs on past the floor level to the water line (a drawing detail, closed form).
    vy = rf["vy_land"]
    t_water = (-(-vy) + math.sqrt(vy * vy + 2.0 * g * water_m)) / g
    ev["t_water"] = t_water
    land_v = pa + S * rf["t_land"]
    splash_end = land_v + S * t_water + man["splash_s"]
    sink_end = land_v + S * t_water + man["sink_s"]
    assert max(splash_end, sink_end) < P - F, "the splash is still running at the reset fade"
    tau0 = (0.0 - t0) % P
    r0 = (tau0 - pa) / S
    st0 = {key: state_at(ev["runs"][key], r0) for key in PANELS}
    print(f"schedule (video time, 1/{S:g} speed): cycles of {P:g} s start at " + ", ".join(f"{st:.2f}" for st in starts)
          + f" s (the first {-t0:.2f} s before the first frame); both jumpers take off {pa:g} s into each cycle at {lst(pa)} s; "
          f"the apex {S * rf['t_land'] / 2:.2f} s after the takeoff at {lst(pa + S * rf['t_land'] / 2)} s; both land "
          f"{S * rf['t_land']:.3f} s after the takeoff at {lst(land_v)} s ({land_v:.3f} s into the cycle; both event rows and "
          f"the gold marks light); the free jumper's dot runs on to the water line {water_m * 100:.1f} cm under the floor "
          f"level {S * t_water:.3f} s later at {lst(land_v + S * t_water)} s (the splash ring runs {man['splash_s']:g} s and "
          f"the dot sinks {man['sink_px']:g} px over {man['sink_s']:g} s, drawing details); the run holds at the landing; "
          f"the reset crossfade runs over the last {F:g} s of each cycle (from {lst(P - F)} s; the readouts out over its "
          f"first half and in over its second); on the first frame the cycle is {tau0:.2f} s in ({r0:.3f} s real after the "
          f"takeoff: the free jumper {st0['free']['phase']} at x {st0['free']['x']:.2f} m, y {st0['free']['y']:.2f} m, the "
          f"tied jumper at x {st0['tied']['x']:.2f} m); title until {man['title_until']:g} s; payoff card from "
          f"{man['payoff_t']:g} s; the title fades back in over the last {man['loop_fade']:g} s and the last frame repeats "
          f"the first (the scene is periodic: {Dur:g} s holds exactly {cycles:.0f} cycles)")
    # Text widths.
    font = os.environ["SEED_ZERO_FONT"]
    f24, f28, f34, f40, f56 = (ImageFont.truetype(font, n) for n in (24, 28, 34, 40, 56))
    widths = {"overlay@34": (f34, man["overlay"])}
    for j, line in enumerate(man["title"].split("|")):
        widths[f"title line {j + 1}@56"] = (f56, line)
    widths["legend@40"] = (f40, legend_text(man))
    widths["clock@28"] = (f28, clock_text(rf["t_land"]))
    widths["clock held@28"] = (f28, clock_text(-1.0))
    for key in PANELS:
        widths[f"label {key}@40"] = (f40, label_text(key))
        widths[f"out {key}@28"] = (f28, out_text(ev["runs"][key]["x_land"]))
        widths[f"air {key}@28"] = (f28, air_text(DOWN, rf["t_land"]))
        widths[f"boat {key}@28"] = (f28, boat_text(key, ev["runs"][key]["xb_land"]))
        widths[f"height {key}@28"] = (f28, height_text(ct["apex"]))
        widths[f"event {key}@40"] = (f40, event_text(ev, key))
        widths[f"mark {key}@24"] = (f24, mark_text(ev, key))
    widths["on the bow@28"] = (f28, air_text(HELD, 0.0))
    for j, line in enumerate(payoff_lines(man, ev)):
        widths[f"payoff line {j + 1}@40"] = (f40, line)
    print("text widths (the on-screen strings verbatim): " + ", ".join(f"{kk} {f.getlength(s):.0f} px '{s}'" for kk, (f, s) in widths.items()))
    assert all(f.getlength(s) < 950 for f, s in widths.values()), "a text line is wider than 950 px"
    assert len(payoff_lines(man, ev)) <= 6, "the card has more than six lines"
    # Layout checks.
    left = ROW_X0 + max(max(f40.getlength(label_text(key)), f28.getlength(out_text(ev["runs"][key]["x_land"])),
                            f28.getlength(air_text(DOWN, rf["t_land"]))) for key in PANELS)
    right = ROW_X1 - max(max(f28.getlength(boat_text(key, ev["runs"][key]["xb_land"])), f28.getlength(height_text(ct["apex"])))
                         for key in PANELS)
    rows_bottom = FIX_DY + 16
    floor = float(man["floor_dy"])
    bow = float(man["bow_x_px"])
    hull_px = man["hull_m"] * ppm
    dock_x = bow + D * ppm
    recoil_px = -rf["xb_land"] * ppm
    stern_land = bow - hull_px - recoil_px
    apex_top = floor - ct["apex"] * ppm - FIG_H - HEAD_R
    x_land = {key: bow + ev["runs"][key]["x_land"] * ppm for key in PANELS}
    mark_w = {key: f24.getlength(mark_text(ev, key)) for key in PANELS}
    mark_c = {"free": 0.5 * (x_land["free"] + dock_x), "tied": 0.5 * (dock_x + x_land["tied"])}
    mark_x0 = {key: mark_c[key] - mark_w[key] / 2.0 for key in PANELS}
    mark_x1 = {key: mark_c[key] + mark_w[key] / 2.0 for key in PANELS}
    ev_w = max(f40.getlength(event_text(ev, key)) for key in PANELS)
    ev_x0, ev_x1 = EVENT_X - ev_w / 2.0, EVENT_X + ev_w / 2.0
    water_top = floor + man["water_dy"]
    hull_bottom = floor + man["hull_depth_px"]
    sink_bottom = water_top + man["sink_px"] + HEAD_R    # the sunk figure's feet point plus the head radius (the head is above)
    print(f"row check: the left column ends at x {left:.0f} px, the right column starts at x {right:.0f} px; both end "
          f"{rows_bottom} px under the band top; the floor level (the boat's floor and the dock top) is {floor:.0f} px under "
          f"the band top, the water line {water_top:.0f} px, the hull bottom {hull_bottom:.0f} px; the hull spans x "
          f"{bow - hull_px:.0f} to {bow:.0f} px at the start and x {stern_land:.0f} to {bow - recoil_px:.0f} px when the free "
          f"jumper lands (recoil {recoil_px:.0f} px); the dock starts at x {dock_x:.0f} px (gap {D * ppm:.0f} px); the jumpers "
          f"land at x {x_land['free']:.0f} px (free, over the water) and {x_land['tied']:.0f} px (tied, on the dock); the "
          f"figure's highest pixel at the apex is {apex_top:.0f} px under the band top ({ct['apex'] * ppm:.0f} px of rise); "
          f"the gold mark labels are centred at x {mark_c['free']:.0f} and {mark_c['tied']:.0f} px ({mark_x0['free']:.0f} to "
          f"{mark_x1['free']:.0f} and {mark_x0['tied']:.0f} to {mark_x1['tied']:.0f} px) {MARK_LABEL_DY} px under the band "
          f"top over the dashed gap line at {MARK_DY} px; the event rows span {EVENT_DY - 22} to {EVENT_DY + 22} px under the "
          f"band top and x {ev_x0:.0f} to {ev_x1:.0f} px (widest {ev_w:.0f} px, centred on {EVENT_X}) in the water left of "
          f"the dock; the sunk figure reaches {sink_bottom:.0f} px under the band top; each band is {BAND_H} px tall (y "
          f"{BAND_Y['free']} to {BAND_Y['free'] + BAND_H} and {BAND_Y['tied']} to {BAND_Y['tied'] + BAND_H}); the caption "
          f"band starts at y {int(man['caption_y'] * H)}; the title rows end at y {TITLE_Y[-1] + 28} and the overlay band "
          f"ends at y 130")
    assert right - left > 40, "the columns meet"
    assert stern_land > 16, "the free boat's stern leaves the band when the jumper lands"
    assert apex_top > rows_bottom + 10, "the figure at the apex meets the text rows"
    assert MARK_LABEL_DY - 12 > rows_bottom + 10 and MARK_DY + 6 < apex_top, "the mark label meets the rows or the arc"
    assert all(mark_x0[key] > 16 and mark_x1[key] < W - 16 for key in PANELS), "a mark label leaves the frame"
    assert x_land["tied"] + 12 < W - 16, "the tied landing leaves the frame"
    assert ev_x0 > 16 and ev_x1 < dock_x - 16, "the event row meets the dock or the frame edge"
    assert EVENT_DY - 22 > hull_bottom + 10 and EVENT_DY + 22 < BAND_H - 10, "the event row leaves the water"
    assert sink_bottom < EVENT_DY - 22 - 10, "the sunk figure meets the event row"
    assert floor > rows_bottom + 10 and TITLE_Y[-1] + 28 <= BAND_Y["free"], "the floor or the title meets the rows"
    assert BAND_Y["tied"] + BAND_H <= int(man["caption_y"] * H), "the bottom band reaches the caption band"
    assert PAYOFF_Y - 20 > int(man["caption_y"] * H) + 90, "the card meets the caption band"
    return ev


def legend_text(man: dict) -> str:
    return f"same jump, same boat, 1/{man['slow']:g} speed"


def clock_text(r: float) -> str:
    return "on the bow, at rest" if r < 0.0 else f"{r:.3f} s after the takeoff"


def label_text(key: str) -> str:
    return "free boat (not tied)" if key == "free" else "tied boat (rope to the dock)"


def out_text(x: float) -> str:
    return f"jumper {max(0.0, x):.2f} m out"


def air_text(phase: str, t: float) -> str:
    if phase == HELD:
        return "on the bow"
    if phase == AIR:
        return f"in the air {t:.3f} s"
    return f"flight {t:.3f} s"


def boat_text(key: str, xb: float) -> str:
    if key == "tied":
        return f"boat tied: {abs(xb):.2f} m"
    return f"boat {abs(xb):.2f} m back"


def height_text(y: float) -> str:
    return f"height {max(0.0, y):.2f} m"


def event_text(ev: dict, key: str) -> str:
    if key == "free":
        return f"free boat: {ev['runs']['free']['x_land']:.2f} m, in the water"
    return f"tied boat: {ev['runs']['tied']['x_land']:.2f} m, on the dock"


def mark_text(ev: dict, key: str) -> str:
    if key == "free":
        return f"{ev['short'] * 100:.0f} cm short"
    return f"{ev['past'] * 100:.0f} cm past the edge"


def payoff_lines(man: dict, ev: dict) -> list[str]:
    text = man["payoff_text"].format(
        x_tied=ev["runs"]["tied"]["x_land"], x_free=ev["runs"]["free"]["x_land"], short_cm=ev["short"] * 100.0,
        back=-ev["runs"]["free"]["xb_land"], ratio=ev["ratio"], m100=100.0, x100=ev["boats"].get(100.0, 0.0),
        m_need=ev["m_need"], u_need=ev["u_need"])
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
        self.pa, self.F = man["takeoff_at"], man["reset_fade"]
        self.runs = ev["runs"]
        self.g = man["g"]
        self.bow = float(man["bow_x_px"])
        self.floor = float(man["floor_dy"])
        self.hull_px = man["hull_m"] * self.ppm
        self.dock_x = self.bow + man["gap_m"] * self.ppm
        self.water_top = self.floor + man["water_dy"]
        self.water_m = man["water_dy"] / self.ppm
        self.t_water = ev["t_water"]

    def phase(self, f: int) -> tuple[int, float]:
        k, tau_f = divmod(f - self.c0_f, self.P_f)
        return k, tau_f / self.fps

    @staticmethod
    def L_(x: float, y: float) -> tuple[float, float]:
        """Layer (2x) pixel of a band-local point, rounded to 1e-4 px so equal states draw equal pixels."""
        return round(x * SS, 4), round(y * SS, 4)

    def px(self, x: float, y: float) -> tuple[float, float]:
        """Band-local 1x pixel of a lab point (x metres right of the bow's start, y metres above the floor)."""
        return self.bow + x * self.ppm, self.floor - y * self.ppm

    @staticmethod
    def dashed(d: ImageDraw.ImageDraw, a: tuple, b: tuple, col, dash: float, gap: float, width: int) -> None:
        ax, ay = a
        bx, by = b
        length = math.hypot(bx - ax, by - ay)
        if length < 1e-6:
            return
        ux, uy = (bx - ax) / length, (by - ay) / length
        s = 0.0
        while s < length:
            e = min(length, s + dash)
            d.line((ax + ux * s, ay + uy * s, ax + ux * e, ay + uy * e), fill=col, width=width)
            s = e + gap

    def draw_water_and_dock(self, d: ImageDraw.ImageDraw) -> None:
        L = self.L_
        d.rectangle((*L(-12.0, self.water_top), *L(W + 12.0, BAND_H + 12.0)), fill=WATER)
        d.line((*L(-12.0, self.water_top), *L(W + 12.0, self.water_top)), fill=blend(FOAM, 0.35, WATER), width=2 * SS)
        # The dock: a block from the edge to the frame's right, its top at the floor level, on two pilings.
        d.rectangle((*L(self.dock_x, self.floor), *L(W + 12.0, self.floor + 30.0)), fill=DECK_A, outline=RIM, width=2 * SS)
        d.line((*L(self.dock_x + 4.0, self.floor), *L(W + 12.0, self.floor)), fill=DECK_B, width=3 * SS)
        for px_ in (self.dock_x + 26.0, W - 60.0):
            d.rectangle((*L(px_ - 9.0, self.floor + 30.0), *L(px_ + 9.0, BAND_H + 12.0)), fill=DECK_A, outline=RIM, width=SS)

    def draw_boat(self, d: ImageDraw.ImageDraw, key: str, xb: float) -> None:
        bow = self.bow + xb * self.ppm
        top, bottom = self.floor, self.floor + self.man["hull_depth_px"]
        poly = [self.L_(bow - self.hull_px, top), self.L_(bow, top), self.L_(bow - HULL_TAPER, bottom),
                self.L_(bow - self.hull_px + HULL_TAPER, bottom)]
        d.polygon(poly, fill=HULL, outline=HULL_EDGE, width=2 * SS)
        d.line((*self.L_(bow - self.hull_px + 4.0, top), *self.L_(bow - 4.0, top)), fill=DECK_B, width=3 * SS)
        if key == "tied":
            # A taut rope from the bow to the dock face, a cleat at each end.
            y = top + 9.0
            d.line((*self.L_(bow, y), *self.L_(self.dock_x, y)), fill=ROPE, width=2 * SS)
            for cx in (bow - 6.0, self.dock_x + 6.0):
                r = 3.0 * SS
                X, Y = self.L_(cx, y)
                d.ellipse((X - r, Y - r, X + r, Y + r), fill=ROPE)

    def jumper_xy(self, key: str, st: dict) -> tuple[float, float, float]:
        """The figure's feet point (lab metres) and its sink in px: in the water the free jumper runs on past the
        floor level to the water line, then sinks a little (drawing details, video time)."""
        if key != "free" or st["phase"] != DOWN:
            return st["x"], st["y"], 0.0
        run = self.runs["free"]
        c = self.ev["closed"]["free"]
        d_v = st["tv"] - self.S * run["t_land"]            # video seconds since the landing
        tau = min(self.t_water, max(0.0, d_v / self.S))     # real seconds past the floor level, to the water line
        x = run["x_land"] + c["vj"] * tau
        y = run["vy_land"] * tau - 0.5 * self.g * tau * tau
        after = max(0.0, d_v - self.S * self.t_water)
        u = min(1.0, after / self.man["sink_s"])
        sink = self.man["sink_px"] * (1.0 - (1.0 - u) ** 2)
        return x, y, sink

    def draw_trail(self, d: ImageDraw.ImageDraw, key: str, st: dict) -> None:
        if st["phase"] == HELD:
            return
        run = self.runs[key]
        t_end = min(st["t_air"], run["t_land"])
        n = int(math.floor(t_end / TRAIL_EVERY_S + 1e-9))
        pts = []
        for k in range(n + 1):
            tk = k * TRAIL_EVERY_S
            pts.append(self.L_(*self.px(float(np.interp(tk, run["t"], run["x"])), float(np.interp(tk, run["t"], run["y"])))))
        x, y, _ = self.jumper_xy(key, st)
        pts.append(self.L_(*self.px(x, y)))
        if len(pts) >= 2:
            d.line(pts, fill=blend(COLOUR[key], 0.55), width=3, joint="curve")

    def draw_figure(self, d: ImageDraw.ImageDraw, key: str, st: dict) -> None:
        x, y, sink = self.jumper_xy(key, st)
        fx, fy = self.px(x, y)
        fy += sink
        col = COLOUR[key]
        L = self.L_
        hip = fy - FIG_LEG
        neck = fy - FIG_H + 2.0 * HEAD_R
        d.line((*L(fx, hip), *L(fx - 4.0, fy)), fill=col, width=3 * SS)
        d.line((*L(fx, hip), *L(fx + 4.0, fy)), fill=col, width=3 * SS)
        d.line((*L(fx, hip), *L(fx, neck)), fill=col, width=3 * SS)
        d.line((*L(fx - FIG_ARM, neck + 7.0), *L(fx, neck + 1.0), *L(fx + FIG_ARM, neck - 3.0)), fill=col, width=3 * SS)
        X, Y = L(fx, fy - FIG_H + HEAD_R)
        r = HEAD_R * SS
        d.ellipse((X - r, Y - r, X + r, Y + r), fill=WHITE, outline=col, width=SS)

    def draw_mark(self, d: ImageDraw.ImageDraw, key: str) -> None:
        """After the landing: gold dashed ticks at the landing point and the dock edge up to a dashed gap line."""
        run = self.runs[key]
        x_land = self.bow + run["x_land"] * self.ppm
        for xt in (x_land, self.dock_x):
            self.dashed(d, self.L_(xt, self.floor - 4.0), self.L_(xt, MARK_DY + 8.0), GOLD, 6 * SS, 4 * SS, 3 * SS)
        self.dashed(d, self.L_(x_land, MARK_DY), self.L_(self.dock_x, MARK_DY), GOLD, 8 * SS, 6 * SS, 3 * SS)
        r = 5.0 * SS
        X, Y = self.L_(x_land, self.floor)
        d.ellipse((X - r, Y - r, X + r, Y + r), fill=GOLD)

    def draw_splash(self, d: ImageDraw.ImageDraw, key: str, st: dict) -> None:
        if key != "free" or st["phase"] != DOWN:
            return
        run = self.runs["free"]
        u = (st["tv"] - self.S * (run["t_land"] + self.t_water)) / self.man["splash_s"]
        if 0.0 <= u < 1.0:
            c = self.ev["closed"]["free"]
            X, Y = self.L_(*self.px(run["x_land"] + c["vj"] * self.t_water, -self.water_m))
            rr = (8 + 32 * u) * SS
            d.ellipse((X - rr, Y - rr * 0.45, X + rr, Y + rr * 0.45), outline=blend(FOAM, 1.0 - u, WATER), width=3 * SS)

    def scene(self, key: str, tau: float) -> tuple[Image.Image, dict]:
        """The band layer of panel key at tau seconds into a cycle (the standing setup before the takeoff)."""
        layer = Image.new("RGB", (W * SS, BAND_H * SS), BG)
        d = ImageDraw.Draw(layer)
        tv = tau - self.pa
        rt = tv / self.S
        st = state_at(self.runs[key], rt)
        st["tv"], st["rt"] = tv, rt
        self.draw_water_and_dock(d)
        self.draw_boat(d, key, st["xb"])
        if st["phase"] == DOWN:
            self.draw_mark(d, key)
        self.draw_trail(d, key, st)
        self.draw_splash(d, key, st)
        self.draw_figure(d, key, st)
        return layer, st

    def draw_panel(self, key: str, f: int) -> tuple[Image.Image, dict]:
        k, tau = self.phase(f)
        P, F = self.P, self.F
        layer, st = self.scene(key, tau)
        st["alpha"], st["k"] = 1.0, k
        if tau >= P - F:
            # Crossfade to the next cycle's standing setup (both runs hold at the landing by now, asserted).
            a = (tau - (P - F)) / F
            new, st_new = self.scene(key, tau - P)
            layer = Image.blend(layer, new, a)
            st["alpha"] = max(0.0, 1.0 - 2.0 * a)
            st_new["alpha"], st_new["k"] = max(0.0, 2.0 * a - 1.0), k + 1
            if a >= 0.5:
                st = st_new
        return layer, st

    def draw_text(self, d: ImageDraw.ImageDraw, states: dict, hud_alpha: float) -> None:
        man, ev = self.man, self.ev
        for key, st in states.items():
            y0 = BAND_Y[key]
            a, ph = st["alpha"], st["phase"]
            landed = ph == DOWN
            d.text((ROW_X0, y0 + LABEL_DY), label_text(key), font=self.font, fill=COLOUR[key], anchor="lm")
            d.text((ROW_X0, y0 + SUB_DY), out_text(st["x"]), font=self.font_small, fill=blend(GOLD if landed else TEXT, a), anchor="lm")
            d.text((ROW_X0, y0 + FIX_DY), air_text(ph, st["t_air"]), font=self.font_small, fill=blend(MUTED, a), anchor="lm")
            d.text((ROW_X1, y0 + SUB_DY), boat_text(key, st["xb"]), font=self.font_small,
                   fill=blend(GOLD if (landed and key == "free") else TEXT, a), anchor="rm")
            d.text((ROW_X1, y0 + FIX_DY), height_text(st["y"]), font=self.font_small, fill=blend(MUTED, a), anchor="rm")
            if landed:
                d.text((EVENT_X, y0 + EVENT_DY), event_text(ev, key), font=self.font, fill=blend(GOLD, a), anchor="mm")
                x_land = self.bow + self.runs[key]["x_land"] * self.ppm
                mx = 0.5 * (x_land + self.dock_x)
                d.text((mx, y0 + MARK_LABEL_DY), mark_text(ev, key), font=self.font_tiny, fill=blend(GOLD, a), anchor="mm")
        if hud_alpha > 0.02:
            d.text((W / 2, LEGEND_Y), legend_text(man), font=self.font, fill=blend(TEXT, hud_alpha), anchor="mm")
            d.text((W / 2, CLOCK_Y), clock_text(min(states["free"]["rt"], self.runs["free"]["t_land"])), font=self.font_small,
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
        for key in PANELS:
            layer, states[key] = self.draw_panel(key, f)
            img.paste(layer.reduce(SS), (0, BAND_Y[key]))
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
            return self.live_frame(0)   # the scene is periodic: the last frame repeats the first
        if f >= total - fade_frames:
            # The geometry runs on; the legend, clock and card fade out over the first half of the loop fade
            # and the title fades in over the second half, so the two never overlap.
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
    man = json.loads((ROOT / "projects/boatjump/manifest.json").read_text())
    ev = measure(man)
    if "--measure-only" in sys.argv:
        return
    if "--frames" in sys.argv:
        times = [float(v) for v in sys.argv[sys.argv.index("--frames") + 1].split(",")]
        r = Renderer(man, ev)
        (ROOT / "media/boatjump").mkdir(parents=True, exist_ok=True)
        for tv in times:
            Image.fromarray(r.frame_at(int(round(tv * man["fps"])))).save(ROOT / f"media/boatjump/smoke-{tv}.png")
        print("smoke frames: " + ", ".join(f"{tv}" for tv in times))
        return
    Renderer(man, ev).render(ROOT / "media/boatjump/footage.mp4")


if __name__ == "__main__":
    main()
