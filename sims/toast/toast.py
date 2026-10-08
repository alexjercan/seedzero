#!/usr/bin/env python3
"""Toast off the table: does toast always land butter side down?

Two panels on the same clock, the same table drawn the same way at the same
scale, side view: the same slice of toast, a thin uniform plate of length
2a (a rod in side view, I = m a^2 / 3, its mass cancels) leaves a table H
high. The clock starts when the centre of mass passes the table corner
moving horizontally at v with no tilt (v is the chosen setup number; on
the table the toast slides with no loss). Then it slides and tips on the
corner. With s the centre of mass past the corner along the toast and
theta the nose-down tilt, the corner frictionless (Mahajan, AJP 2022):

    s'' = s theta'^2 + g sin theta
    (a^2/3 + s^2) theta'' = g s cos theta - 2 s s' theta'
    N/m = (a^2/3) theta'' / s = (a^2/3)(g cos theta - 2 s' theta') / (a^2/3 + s^2)

integrated by RK4 at steps_per_second; the toast leaves the corner when N
reaches zero or its back end passes the corner (s = a), the event located
inside the step by bisection on the RK4 sub-step and checked by a
half-step rerun; the energy per kilogram is printed until the leave. Then
it flies freely in closed form (the centre of mass on a parabola, turning
at the leave spin) until its lower end touches the floor (the first root
of y_cm - a |sin theta| = -H, scanned at 0.1 ms and bisected); it lands
butter down when cos theta < 0 then. Top panel nudged at 5 cm/s, bottom
panel swiped at 1.5 m/s. After touchdown the drawing lets the slice
settle flat onto the face it shows (a drawing step only, not simulated).
The run repeats every cycle_s seconds of video with a crossfade back to
the start; the cycle divides the scene length, so the scene is exactly
periodic and the last frame equals the first. Shown at 1/slow speed.
Deterministic, no seed.

Measured and printed: both runs (leave time and cause, tilt, spin, fall
time, turned angle, face, distance out, minimum corner force, energy
drift, half-step rerun), the table at table_step_s steps, the landing face
against the speed, the flip speed, the grip variant (Bacon, AJP 2001:
kinetic grip on the corner) and the 12 cm toast for the description, the
brief's checks, the schedule in video time, the on-screen text widths and
the layout clearances.

usage: toast.py [--measure-only] [--frames t1,t2,...]
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
DECK_A = (30, 36, 46)
DECK_B = (42, 50, 62)
RIM = (96, 108, 126)
FLOOR = (36, 42, 52)
CRUST = (124, 76, 38)
CRUMB = (194, 144, 86)
BUTTER = (255, 234, 70)

# Layout: overlay at y 96..130 (captions.py), two title rows at y 190/252 for
# the first seconds, then the legend at y 236; two panels stacked, the nudged
# toast in the band y 330..880 and the swiped one in y 880..1430, each drawn
# at 2x in its own layer; each band has its label row 36 px under the band
# top (left, coloured) with its gold event row right-aligned on the same row,
# then two readout rows at 76 and 110 (left column from x 40: turned, clock;
# right column to x 1040: spin, distance out); the table top 150 px under the
# band top (slab to 174, its edge at edge_x_px, two legs), the floor 525 px
# under the band top; the toast is a 10 px slab centred on the model's line,
# so the line runs 5 px over the drawn table top and floor; captions at
# caption_y 0.75 (y 1440..1530); the six-line card from y 1572 at a 48 px
# pitch.
LEGEND_Y = 236
SS = 2
PAYOFF_Y, PAYOFF_PITCH = 1572.0, 48
PANELS = ("nudged", "swiped")
BAND_Y = {"nudged": 330, "swiped": 880}
BAND_H = 550
LABEL_DY, SUB_DY, FIX_DY = 36, 76, 110
ROW_X0, ROW_X1 = 40, 1040
SLAB_PX, LEG_W = 24, 20
BUTTER_PX = 4.0
COLOUR = {"nudged": CORAL, "swiped": TEAL}
TABLE, CORNER, FLIGHT, DOWN = "table", "corner", "flight", "down"


def blend(col, a: float, base=BG) -> tuple:
    a = max(0.0, min(1.0, a))
    return tuple(int(round(c * a + b * (1 - a))) for c, b in zip(col, base))


# --- measurement --------------------------------------------------------------
def corner_run(v: float, L: float, Ht: float, g: float, dt: float, keep: bool = False, muk: float = 0.0) -> dict:
    """Slide and tip on the corner from s = 0, s' = v, theta = 0, theta' = 0 by RK4 at dt until N reaches
    zero or s reaches a (bisection on the RK4 sub-step inside the last step), then free flight in closed
    form to the floor (the frictionless corner). muk > 0 only replicates the research script's friction
    (-muk N sign(s') with no sticking) to show where the brief's grip numbers come from."""
    a = L / 2.0
    k = a * a / 3.0

    def deriv(s, sd, th, w):
        c, sn = math.cos(th), math.sin(th)
        den = k + s * s
        wd = (g * s * c - 2.0 * s * sd * w) / den
        N = k * (g * c - 2.0 * sd * w) / den
        sdd = s * w * w + g * sn - muk * N * (1.0 if sd >= 0.0 else -1.0)
        return sd, sdd, w, wd, N

    def step(st, h):
        s, sd, th, w = st
        a1 = deriv(s, sd, th, w)
        a2 = deriv(s + 0.5 * h * a1[0], sd + 0.5 * h * a1[1], th + 0.5 * h * a1[2], w + 0.5 * h * a1[3])
        a3 = deriv(s + 0.5 * h * a2[0], sd + 0.5 * h * a2[1], th + 0.5 * h * a2[2], w + 0.5 * h * a2[3])
        a4 = deriv(s + h * a3[0], sd + h * a3[1], th + h * a3[2], w + h * a3[3])
        return tuple(st[i] + h * (a1[i] + 2.0 * a2[i] + 2.0 * a3[i] + a4[i]) / 6.0 for i in range(4))

    def energy(st):
        s, sd, th, w = st
        return 0.5 * (sd * sd + s * s * w * w) + 0.5 * k * w * w - g * s * math.sin(th)

    def event(st) -> float:
        n_ = deriv(*st)[4]
        return min(n_, a - st[0])

    st = (0.0, v, 0.0, 0.0)
    e0 = energy(st)
    n = 0
    min_n = deriv(*st)[4]
    drift = 0.0
    rows = [(0.0, *st, min_n)] if keep else None
    while True:
        nxt = step(st, dt)
        if event(nxt) <= 0.0:
            lo, hi = 0.0, dt
            for _ in range(60):
                mid = 0.5 * (lo + hi)
                if event(step(st, mid)) > 0.0:
                    lo = mid
                else:
                    hi = mid
            st = step(st, hi)
            t_leave = n * dt + hi
            break
        st = nxt
        n += 1
        nn = deriv(*st)[4]
        min_n = min(min_n, nn)
        drift = max(drift, abs(energy(st) - e0))
        if keep:
            rows.append((n * dt, *st, nn))
    n_leave = deriv(*st)[4]
    cause = "N reaches zero" if n_leave <= 1e-9 and st[0] < a - 1e-9 else "the back end passes the corner"
    drift = max(drift, abs(energy(st) - e0))
    if keep:
        rows.append((t_leave, *st, n_leave))
    out = flight(st, a, Ht, g)
    out.update({"v": v, "L": L, "t_leave": t_leave, "cause": cause, "t_touch": t_leave + out["t_fall"],
                "min_n": min(min_n, n_leave), "drift": drift, "steps": n + 1})
    if keep:
        out["rows"] = np.array(rows)
    return out


def flight(st: tuple, a: float, Ht: float, g: float) -> dict:
    """Free flight in closed form from the leave state (s, s', theta, theta') to the first touch of the
    lower end on the floor (scanned at 0.1 ms, then bisected)."""
    s, sd, th, w = st
    x0, y0 = s * math.cos(th), -s * math.sin(th)
    vx = sd * math.cos(th) - s * w * math.sin(th)
    vy = -sd * math.sin(th) - s * w * math.cos(th)

    def low(t: float) -> float:
        return y0 + vy * t - 0.5 * g * t * t - a * abs(math.sin(th + w * t)) + Ht

    t = 0.0
    while low(t + 1e-4) > 0.0:
        t += 1e-4
    lo, hi = t, t + 1e-4
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if low(mid) > 0.0:
            lo = mid
        else:
            hi = mid
    tf = hi
    thT = th + w * tf
    return {"a": a, "H": Ht, "g": g, "s": s, "sd": sd, "th": th, "w": w, "x0": x0, "y0": y0, "vx": vx, "vy": vy,
            "t_fall": tf, "thT": thT, "deg": math.degrees(thT), "down": math.cos(thT) < 0.0, "x_land": x0 + vx * tf}


def grip_run(v: float, L: float, Ht: float, g: float, dt: float, mus: float, muk: float) -> dict:
    """The grip variant: the same slide and tip with friction on the corner, stick-slip. Sliding, the
    friction is -muk N along the toast (s' > 0); when s' reaches zero the toast sticks if the friction
    needed to hold it, s theta'^2 + g sin theta, is at most mus N, and then turns about the corner with s
    fixed until that need passes mus N; it leaves as before. RK4 at dt, every switch located inside the
    step by bisection on the RK4 sub-step."""
    a = L / 2.0
    k = a * a / 3.0

    def deriv(st, stick):
        s, sd, th, w = st
        c, sn = math.cos(th), math.sin(th)
        den = k + s * s
        wd = (g * s * c - 2.0 * s * sd * w) / den
        N = k * (g * c - 2.0 * sd * w) / den
        need = s * w * w + g * sn
        if stick:
            return (0.0, 0.0, w, wd), N, need
        return (sd, need - muk * N, w, wd), N, need

    def step(st, h, stick):
        a1 = deriv(st, stick)[0]
        a2 = deriv(tuple(st[i] + 0.5 * h * a1[i] for i in range(4)), stick)[0]
        a3 = deriv(tuple(st[i] + 0.5 * h * a2[i] for i in range(4)), stick)[0]
        a4 = deriv(tuple(st[i] + h * a3[i] for i in range(4)), stick)[0]
        return tuple(st[i] + h * (a1[i] + 2.0 * a2[i] + 2.0 * a3[i] + a4[i]) / 6.0 for i in range(4))

    def events(st, stick):
        _, N, need = deriv(st, stick)
        if stick:
            return {"slip": mus * N - need, "leave": N}
        return {"stop": st[1], "leave": min(N, a - st[0])}

    st, stick, t = (0.0, v, 0.0, 0.0), v == 0.0, 0.0
    log = []
    while True:
        nxt = step(st, dt, stick)
        ev = events(nxt, stick)
        if min(ev.values()) > 0.0:
            st, t = nxt, t + dt
            continue
        lo, hi = 0.0, dt
        for _ in range(60):
            mid = 0.5 * (lo + hi)
            if min(events(step(st, mid, stick), stick).values()) > 0.0:
                lo = mid
            else:
                hi = mid
        st, t = step(st, hi, stick), t + hi
        ev = events(st, stick)
        which = min(ev, key=ev.get)
        if which == "leave":
            break
        if which == "stop":
            st = (st[0], 0.0, st[2], st[3])
            _, N, need = deriv(st, True)
            assert need <= mus * N, "the toast stops but the static grip cannot hold it"
            stick = True
            log.append(f"sticks at {t * 1000:.1f} ms ({st[0] * 1000:.2f} mm past the corner, tilt {math.degrees(st[2]):.2f} deg)")
        else:
            stick = False
            log.append(f"slips at {t * 1000:.1f} ms (tilt {math.degrees(st[2]):.2f} deg)")
    _, n_leave, _ = deriv(st, stick)
    cause = "N reaches zero" if st[0] < a - 1e-9 else "the back end passes the corner"
    out = flight(st, a, Ht, g)
    out.update({"v": v, "L": L, "t_leave": t, "cause": cause, "t_touch": t + out["t_fall"], "log": log})
    return out


def flip_speed(run, lo: float, hi: float) -> float:
    """The speed at which the landing face turns from butter down to butter up (bisection on v)."""
    assert run(lo)["down"] and not run(hi)["down"]
    for _ in range(24):
        mid = 0.5 * (lo + hi)
        if run(mid)["down"]:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def state_at(run: dict, rt: float, settle_real: float) -> dict:
    """Model state rt real seconds after the centre of mass passes the corner: the centre (x right,
    y up, origin at the corner), the tilt, the spin, the phase; after touchdown the drawn settle."""
    a, g = run["a"], run["g"]
    if rt < 0.0:
        return {"x": run["v"] * rt, "y": 0.0, "th": 0.0, "w": 0.0, "phase": TABLE, "out": run["v"] * rt}
    if rt < run["t_leave"]:
        R = run["rows"]
        s = float(np.interp(rt, R[:, 0], R[:, 1]))
        th = float(np.interp(rt, R[:, 0], R[:, 3]))
        w = float(np.interp(rt, R[:, 0], R[:, 4]))
        x = s * math.cos(th)
        return {"x": x, "y": -s * math.sin(th), "th": th, "w": w, "phase": CORNER, "out": x}
    if rt < run["t_touch"]:
        d = rt - run["t_leave"]
        x = run["x0"] + run["vx"] * d
        return {"x": x, "y": run["y0"] + run["vy"] * d - 0.5 * g * d * d, "th": run["th"] + run["w"] * d, "w": run["w"],
                "phase": FLIGHT, "out": x}
    # Drawing only: the lower end stays on the floor and the slice turns flat onto the face it shows.
    thT = run["thT"]
    u = a if math.sin(thT) > 0.0 else -a
    px = run["x_land"] + u * math.cos(thT)
    py = -run["H"]
    target = round(thT / math.pi) * math.pi
    q = min(1.0, (rt - run["t_touch"]) / settle_real)
    q = q * q * (3.0 - 2.0 * q)
    th = thT + (target - thT) * q
    return {"x": px - u * math.cos(th), "y": py + u * math.sin(th), "th": th, "w": run["w"], "phase": DOWN,
            "out": run["x_land"]}


def toast_corners(st: dict, ppm: float, edge: float, line_y: float, h: float, a: float) -> list[tuple[float, float]]:
    """Band-local corners of the drawn slab (centred on the model line, half thickness h px)."""
    cx, cy = edge + st["x"] * ppm, line_y - st["y"] * ppm
    c, sn = math.cos(st["th"]), math.sin(st["th"])
    ex, ey = c * a * ppm, sn * a * ppm          # along the toast (screen, y down; nose-down tilt positive)
    nx, ny = sn * h, -c * h                     # toward the butter face
    return [(cx - ex - nx, cy - ey - ny), (cx + ex - nx, cy + ey - ny), (cx + ex + nx, cy + ey + ny),
            (cx - ex + nx, cy - ey + ny)]


def measure(man: dict) -> dict:
    g, L, Ht = man["g"], man["toast_m"], man["table_m"]
    a = L / 2.0
    dt = 1.0 / man["steps_per_second"]
    S, P, D, fps, F, ea = man["slow"], man["cycle_s"], man["scene_duration"], man["fps"], man["reset_fade"], man["edge_at"]
    cycles = D / P
    assert abs(cycles - round(cycles)) < 1e-9, "the cycle must divide the scene length"
    for key in ("cycle_s", "edge_at", "first_cycle_at", "reset_fade", "settle_s"):
        assert abs(man[key] * fps - round(man[key] * fps)) < 1e-9, f"{key} must be a whole number of frames"
    ppm = man["px_per_m"]
    top, floor = float(man["table_top_dy"]), float(man["floor_dy"])
    assert abs((floor - top) - Ht * ppm) < 1e-9, "the floor must sit 0.75 m = 375 px under the table top"
    vn, vs = man["speed_ms"]["nudged"], man["speed_ms"]["swiped"]
    print(f"setup: side view, two panels on one clock, the same table drawn the same way at the same scale: the same "
          f"slice of toast, a thin uniform plate {L * 100:g} cm long (2a; a rod in side view, I = m a^2 / 3; its mass "
          f"cancels) leaves a table {Ht * 100:g} cm high; g = {g:g} m/s^2; the clock starts when the centre of mass passes "
          f"the table corner moving horizontally at v with no tilt (v is the chosen setup number; on the table the "
          f"toast slides with no loss); top panel nudged at v = {vn:g} m/s = {vn * 100:g} cm/s, bottom panel swiped at "
          f"v = {vs:g} m/s; then it slides and tips on the corner, frictionless (Mahajan, AJP 2022), with s the centre "
          f"of mass past the corner along the toast and theta the nose-down tilt: s'' = s theta'^2 + g sin theta, "
          f"(a^2/3 + s^2) theta'' = g s cos theta - 2 s s' theta', N/m = (a^2/3) theta'' / s; RK4 at dt = {dt:.0e} s; "
          f"it leaves the corner when N reaches zero or its back end passes the corner (s = a = {a * 100:g} cm), the "
          f"event located inside the step by bisection on the RK4 sub-step; then free flight in closed form, turning "
          f"at the leave spin, until its lower end touches the floor; butter down when cos theta < 0 then; shown at "
          f"1/{S:g} speed on a {P:g} s cycle ({P * fps:.0f} frames), {cycles:.0f} cycles in {D:g} s; drawn at {ppm:g} px "
          f"per metre; deterministic, no seed")
    runs = {}
    for m, v in (("nudged", vn), ("swiped", vs)):
        r = corner_run(v, L, Ht, g, dt, keep=True)
        half = corner_run(v, L, Ht, g, 0.5 * dt)
        r["half"] = half
        runs[m] = r
        print(f"{m} at {v:g} m/s: leaves the corner at {r['t_leave'] * 1000:.4f} ms = {r['t_leave'] * 1000:.1f} ms when "
              f"{r['cause']} (s = {r['s'] * 100:.4f} cm past the corner, s' = {r['sd']:.4f} m/s), tilt "
              f"{math.degrees(r['th']):.4f} deg = {math.degrees(r['th']):.2f} deg, spin {r['w']:.4f} rad/s = {r['w']:.2f} "
              f"rad/s = {r['w'] / (2 * math.pi):.4f} turns a second = {r['w'] / (2 * math.pi):.2f}; centre of mass "
              f"{r['x0'] * 100:.3f} cm out and {-r['y0'] * 100:.3f} cm down, moving ({r['vx']:.4f}, {r['vy']:.4f}) m/s; "
              f"falls {r['t_fall']:.6f} s = {r['t_fall']:.4f} s and touches the floor {r['t_touch']:.6f} s = "
              f"{r['t_touch']:.3f} s after the edge turned {r['deg']:.4f} deg = {r['deg']:.2f} deg: cos theta = "
              f"{math.cos(r['thT']):+.4f}, butter {'DOWN' if r['down'] else 'UP'}; centre of mass "
              f"{r['x_land'] * 100:.3f} cm = {r['x_land'] * 100:.1f} cm out from the edge; minimum N/m {r['min_n']:.6f} "
              f"m/s^2 until the leave; energy per kilogram drift {r['drift']:.1e} J over {r['steps']} steps; half-step "
              f"rerun (dt = {0.5 * dt:.0e} s): leaves at {half['t_leave'] * 1000:.6f} ms ({half['t_leave'] - r['t_leave']:+.1e} "
              f"s), turned {half['deg']:.6f} deg ({half['deg'] - r['deg']:+.1e} deg)")
        assert abs(half["t_leave"] - r["t_leave"]) < 1e-6 and r["drift"] < 1e-12 and r["min_n"] >= -1e-9
        assert half["down"] == r["down"]
        # The table at table_step_s steps.
        R = r["rows"]
        lines = []
        tt = 0.0
        while tt <= r["t_touch"] + 1e-12:
            if tt < r["t_leave"]:
                s = float(np.interp(tt, R[:, 0], R[:, 1]))
                th = float(np.interp(tt, R[:, 0], R[:, 3]))
                w = float(np.interp(tt, R[:, 0], R[:, 4]))
                nn = float(np.interp(tt, R[:, 0], R[:, 5]))
                lines.append(f"  {m} t {tt * 1000:3.0f} ms on the corner: s {s * 100:6.3f} cm, tilt {math.degrees(th):7.2f} deg, "
                             f"spin {w:5.2f} rad/s, N/m {nn:6.3f} m/s^2")
            else:
                st = state_at(r, tt, 1.0)
                lines.append(f"  {m} t {tt * 1000:3.0f} ms in flight: centre {st['x'] * 100:6.2f} cm out, {-st['y'] * 100:6.2f} cm "
                             f"down, tilt {math.degrees(st['th']):7.2f} deg, spin {st['w']:5.2f} rad/s, N 0")
            tt = round(tt + man["table_step_s"], 9)
        lines.append(f"  {m} t {r['t_leave'] * 1000:.1f} ms leaves; touchdown at {r['t_touch'] * 1000:.1f} ms turned "
                     f"{r['deg']:.2f} deg")
        print("\n".join(lines))
    # Free-flight clearance from the table (the slab and its corner): no toast point below the table
    # top on the table side while it flies, sampled every 0.1 ms.
    for m in PANELS:
        r = runs[m]
        worst = math.inf
        tt = r["t_leave"]
        while tt < r["t_touch"]:
            st = state_at(r, tt, 1.0)
            c, sn = math.cos(st["th"]), math.sin(st["th"])
            for u in np.linspace(-a, a, 41):
                px, py = st["x"] + u * c, st["y"] - u * sn
                if px < 0.0:
                    worst = min(worst, py)
            tt += 1e-4
        r["clear"] = worst
        print(f"{m}: in flight the lowest toast point over the table side (x < 0) is "
              f"{'never over the table' if worst == math.inf else f'{worst * 1000:+.3f} mm from the table plane'}")
        assert worst >= -1e-6, "the toast passes through the table"
    # The landing face against the speed, the flip, the grip variant and the 12 cm toast.
    speeds = {}
    descr = []
    for v in sorted(set(man["description_speeds_ms"] + [vn, vs])):
        r = runs["nudged"] if v == vn else runs["swiped"] if v == vs else corner_run(v, L, Ht, g, dt)
        speeds[v] = r
        descr.append(f"{v:g} m/s: leaves at {r['t_leave'] * 1000:.1f} ms ({'N zero' if r['cause'].startswith('N') else 'back end'}), "
                     f"tilt {math.degrees(r['th']):.2f} deg, spin {r['w']:.2f} rad/s, falls {r['t_fall']:.4f} s, turned "
                     f"{r['deg']:.2f} deg, butter {'DOWN' if r['down'] else 'UP'}, {r['x_land'] * 100:.1f} cm out")
        assert r["min_n"] >= -1e-9
    print("landing face against the speed (frictionless corner): " + "; ".join(descr))
    for v, r in speeds.items():
        assert r["down"] == (v < 0.86), "the face against the speed is not one switch"
    v_flip = flip_speed(lambda v: corner_run(v, L, Ht, g, dt), 0.8, 1.0)
    grid = math.ceil(v_flip * 100.0) / 100.0
    assert corner_run(grid, L, Ht, g, dt)["down"] is False and corner_run(grid - 0.01, L, Ht, g, dt)["down"] is True
    muk, mus = man["grip_kinetic"], man["grip_static"]
    bn = grip_run(vn, L, Ht, g, dt, mus, muk)
    bs = grip_run(vs, L, Ht, g, dt, mus, muk)
    v_flip_b = flip_speed(lambda v: grip_run(v, L, Ht, g, dt, mus, muk), 0.8, 1.0)
    grid_b = math.ceil(v_flip_b * 100.0) / 100.0
    L2 = man["long_toast_m"]
    v_flip_12 = flip_speed(lambda v: corner_run(v, L2, Ht, g, dt), 0.8, 1.0)
    v_flip_12b = flip_speed(lambda v: grip_run(v, L2, Ht, g, dt, mus, muk), 0.8, 1.0)
    grid_12, grid_12b = math.ceil(v_flip_12 * 100.0) / 100.0, math.ceil(v_flip_12b * 100.0) / 100.0
    print(f"flip: the face turns from butter down to butter up at {v_flip:.5f} m/s = {v_flip:.3f} m/s = {v_flip:.2f} m/s "
          f"(bisection; {grid - 0.01:.2f} m/s lands down, {grid:.2f} m/s up); every speed up to 0.8 m/s lands butter down")
    print(f"grip variant (Bacon, AJP 2001: static {mus:g}, kinetic {muk:g} on the corner, stick-slip): nudged at "
          f"{vn:g} m/s {'; '.join(bn['log']) or 'never sticks'}; leaves at {bn['t_leave'] * 1000:.1f} ms when {bn['cause']}, "
          f"tilted {math.degrees(bn['th']):.2f} deg at {bn['w']:.2f} rad/s, turns {bn['deg']:.2f} deg, butter "
          f"{'DOWN' if bn['down'] else 'UP'}, {bn['x_land'] * 100:.1f} cm out; swiped at {vs:g} m/s "
          f"{'; '.join(bs['log']) or 'never sticks'}; leaves at {bs['t_leave'] * 1000:.1f} ms at {bs['w']:.2f} rad/s and "
          f"turns {bs['deg']:.2f} deg, butter {'DOWN' if bs['down'] else 'UP'}, {bs['x_land'] * 100:.1f} cm out; the face "
          f"flips at {v_flip_b:.5f} m/s = {v_flip_b:.2f} m/s ({grid_b - 0.01:.2f} lands down, {grid_b:.2f} up)")
    rb = corner_run(vn, L, Ht, g, dt, muk=muk)
    print(f"the research script's friction (-{muk:g} N sign(s'), no sticking: s' chatters about zero while the kinetic "
          f"grip holds) for the nudge: leaves at {rb['t_leave'] * 1000:.1f} ms tilted {math.degrees(rb['th']):.2f} deg at "
          f"{rb['w']:.2f} rad/s, turns {rb['deg']:.2f} deg, butter {'DOWN' if rb['down'] else 'UP'}; the stick-slip model "
          f"above turns {bn['deg']:.2f} deg ({bn['deg'] - rb['deg']:+.2f} deg): the same face")
    print(f"12 cm toast: flips at {v_flip_12:.5f} m/s = {v_flip_12:.2f} m/s frictionless ({grid_12 - 0.01:.2f} down, "
          f"{grid_12:.2f} up), at {v_flip_12b:.5f} m/s = {v_flip_12b:.2f} m/s with the grip ({grid_12b - 0.01:.2f} down, "
          f"{grid_12b:.2f} up)")
    ev = {"runs": runs, "speeds": speeds, "v_flip": v_flip, "v_flip_b": v_flip_b, "bn": bn, "bs": bs, "v_flip_12": v_flip_12}
    # The brief's checks.
    rn, rs = runs["nudged"], runs["swiped"]
    checks: list[tuple[str, float, float, float]] = [
        ("nudged leave (ms)", rn["t_leave"] * 1000, 193.2, 0.06), ("nudged leave tilt (deg)", math.degrees(rn["th"]), 38.81, 6e-3),
        ("nudged spin (rad/s)", rn["w"], 8.89, 6e-3), ("nudged turns a second", rn["w"] / (2 * math.pi), 1.41, 6e-3),
        ("nudged fall (s)", rn["t_fall"], 0.3386, 6e-5), ("nudged turned (deg)", rn["deg"], 211.22, 6e-3),
        ("nudged out (cm)", rn["x_land"] * 100, 8.7, 0.06),
        ("swiped leave (ms)", rs["t_leave"] * 1000, 33.3, 0.06), ("swiped leave tilt (deg)", math.degrees(rs["th"]), 2.46, 6e-3),
        ("swiped spin (rad/s)", rs["w"], 2.45, 6e-3), ("swiped fall (s)", rs["t_fall"], 0.3614, 6e-5),
        ("swiped turned (deg)", rs["deg"], 53.12, 6e-3), ("swiped out (cm)", rs["x_land"] * 100, 59.2, 0.06),
        ("0.80 m/s turned (deg)", speeds[0.8]["deg"], 96.4, 0.06), ("1.00 m/s turned (deg)", speeds[1.0]["deg"], 78.4, 0.06),
        ("2.00 m/s turned (deg)", speeds[2.0]["deg"], 40.16, 6e-3), ("2.00 m/s out (cm)", speeds[2.0]["x_land"] * 100, 78.7, 0.06),
        ("0.20 m/s turned (deg)", speeds[0.2]["deg"], 199.9, 0.06), ("0.50 m/s turned (deg)", speeds[0.5]["deg"], 140.9, 0.06),
        ("flip low (m/s)", v_flip, 0.86, 0.0), ("flip high (m/s)", v_flip, 0.87, 0.0),
        ("grip nudge turned, research friction (deg)", rb["deg"], 178.7, 0.06), ("grip swipe turned (deg)", bs["deg"], 54.1, 0.06),
        ("grip flip, first 0.01 step up (m/s)", grid_b, 0.92, 1e-9), ("12 cm flip, first 0.01 step up (m/s)", grid_12, 0.85, 1e-9),
        ("swiped touchdown = brief 33.3 ms + 0.3614 s (s real)", rs["t_touch"], 0.0333 + 0.3614, 6e-4), ("nudged touchdown (s real)", rn["t_touch"], 0.532, 6e-4),
    ]
    flags = [("nudged leaves when N reaches zero", rn["cause"].startswith("N")),
             ("swiped leaves when its back end passes", rs["cause"].startswith("the back")),
             ("nudged butter DOWN", rn["down"]), ("swiped butter UP", not rs["down"]),
             ("0.80 m/s DOWN", speeds[0.8]["down"]), ("1.00 m/s UP", not speeds[1.0]["down"]),
             ("2.00 m/s UP", not speeds[2.0]["down"]), ("0.20 m/s DOWN", speeds[0.2]["down"]),
             ("0.50 m/s DOWN", speeds[0.5]["down"]), ("grip nudge DOWN", bn["down"]), ("grip swipe UP", not bs["down"]),
             ("N/m at or above zero until the leave (min nudged %.1e, swiped %.4f)" % (rn["min_n"], rs["min_n"]),
              min(rn["min_n"], rs["min_n"]) >= -1e-9),
             ("energy within 1e-12 J/kg (%.1e, %.1e)" % (rn["drift"], rs["drift"]), max(rn["drift"], rs["drift"]) < 1e-12),
             ("half-step rerun within 1e-6 s (%.1e, %.1e)" % (rn["half"]["t_leave"] - rn["t_leave"],
                                                              rs["half"]["t_leave"] - rs["t_leave"]),
              max(abs(rn["half"]["t_leave"] - rn["t_leave"]), abs(rs["half"]["t_leave"] - rs["t_leave"])) < 1e-6)]
    fails = 0
    out = []
    for name, got, want, tol in checks:
        if name == "flip low (m/s)":
            ok = got >= want
            out.append(f"flip at least {want:g}: sim {got:.5f}: {'ok' if ok else 'FAIL'}")
        elif name == "flip high (m/s)":
            ok = got <= want
            out.append(f"flip at most {want:g}: sim {got:.5f}: {'ok' if ok else 'FAIL'}")
        else:
            ok = abs(got - want) <= tol
            out.append(f"{name}: brief {want:g}, sim {got:.6g}, diff {got - want:+.1e}: {'ok' if ok else 'FAIL'}")
        fails += 0 if ok else 1
    for name, ok in flags:
        out.append(f"{name}: {'ok' if ok else 'FAIL'}")
        fails += 0 if ok else 1
    n_checks = len(checks) + len(flags)
    print(f"checks against the brief ({n_checks} checks, {fails} failed): " + "; ".join(out))
    ev["n_checks"], ev["check_fails"] = n_checks, fails
    assert fails == 0, "a check against the brief failed"
    # The schedule in video time.
    t0 = man["first_cycle_at"]
    k0 = math.ceil((0.0 - t0) / P - 1e-9) - 1
    k1 = math.floor((D - t0) / P - 1e-9)
    starts = [t0 + kk * P for kk in range(k0, k1 + 1)]
    ev["cycles"] = int(round(cycles))

    def lst(off_: float) -> str:
        return ", ".join(f"{st + off_:.2f}" for st in starts if 0.0 <= st + off_ < D)

    settle_v = man["settle_s"]
    for m in PANELS:
        assert ea + S * runs[m]["t_touch"] + settle_v < P - F, "the toast is still settling at the reset fade"
    tau0 = (0.0 - t0) % P
    r0 = (tau0 - ea) / S
    print(f"schedule (video time, 1/{S:g} speed): cycles of {P:g} s start at " + ", ".join(f"{st:.2f}" for st in starts)
          + f" s; at the cycle start ({-r0 * 1000:.0f} ms real before the edge) the nudged toast's centre is "
          f"{-vn * r0 * 1000:.1f} mm from the edge and the swiped one's {-vs * r0 * 100:.1f} cm back, both moving; both "
          f"centres pass the edge {ea:g} s into each cycle at {lst(ea)} s; the swiped toast leaves the corner "
          f"{S * rs['t_leave']:.3f} s later and touches the floor {rs['t_touch']:.4f} s real = {S * rs['t_touch']:.3f} s "
          f"after the edge ({ea + S * rs['t_touch']:.3f} s into the cycle) at {lst(ea + S * rs['t_touch'])} s (its event row "
          f"lights); the nudged toast leaves the corner {S * rn['t_leave']:.3f} s after the edge and touches the floor "
          f"{rn['t_touch']:.4f} s real = {S * rn['t_touch']:.3f} s after the edge ({ea + S * rn['t_touch']:.3f} s into the "
          f"cycle) at {lst(ea + S * rn['t_touch'])} s (its event row lights); each settles flat over {settle_v:g} s "
          f"(drawing only); both lie on the floor until the reset crossfade over the last {F:g} s of each cycle (from "
          f"{lst(P - F)} s; the readouts out over its first half and in over its second); title until "
          f"{man['title_until']:g} s; payoff card from {man['payoff_t']:g} s; the title fades back in over the last "
          f"{man['loop_fade']:g} s and the last frame repeats the first (the scene is periodic: {D:g} s holds exactly "
          f"{cycles:.0f} cycles)")
    ev["sched"] = {m: ea + S * runs[m]["t_touch"] for m in PANELS}
    # Text widths.
    font = os.environ["SEED_ZERO_FONT"]
    f28, f34, f40, f56 = (ImageFont.truetype(font, n) for n in (28, 34, 40, 56))
    widths = {"overlay@34": (f34, man["overlay"])}
    for j, line in enumerate(man["title"].split("|")):
        widths[f"title line {j + 1}@56"] = (f56, line)
    widths["legend@40"] = (f40, legend_text(man))
    for m in PANELS:
        widths[f"label {m}@40"] = (f40, label_text(m))
        widths[f"event {m}@40"] = (f40, event_text(m))
    for key, s_ in (("turned@28", turned_text(math.radians(211.2))), ("clock before@28", clock_text(-0.1625, 1.0)),
                    ("clock@28", clock_text(0.5318, 1.0)), ("clock landed@28", clock_text(0.6, 0.5318)),
                    ("spin@28", spin_text(8.89)), ("out@28", out_text(0.592)), ("on the table@28", out_text(-0.1))):
        widths[key] = (f28, s_)
    for j, line in enumerate(payoff_lines(man, ev)):
        widths[f"payoff line {j + 1}@40"] = (f40, line)
    print("text widths (the on-screen strings verbatim): " + ", ".join(f"{kk} {f.getlength(s_):.0f} px '{s_}'"
                                                                    for kk, (f, s_) in widths.items()))
    assert all(f.getlength(s_) < 950 for f, s_ in widths.values()), "a text line is wider than 950 px"
    assert len(payoff_lines(man, ev)) <= 6, "the card has more than six lines"
    # Layout checks (band-local pixels): text boxes against the toast over the whole cycle.
    left_w = max(f40.getlength(label_text(m)) for m in PANELS)
    left_rows = max(f28.getlength(s_) for s_ in (turned_text(math.radians(211.2)), clock_text(-0.1625, 1.0),
                                                 clock_text(0.5318, 1.0), clock_text(0.6, 0.5318)))
    right_rows = max(f28.getlength(s_) for s_ in (spin_text(8.89), out_text(0.592), out_text(-0.1)))
    ev_w = max(f40.getlength(event_text(m)) for m in PANELS)
    # Vertical extents from the font's own boxes (anchor "lm", the drawn anchor), over every string drawn.
    y40 = [f40.getbbox(s_, anchor="lm") for s_ in [label_text(m) for m in PANELS] + [event_text(m) for m in PANELS]]
    y28 = [f28.getbbox(s_, anchor="lm") for s_ in (turned_text(math.radians(211.2)), clock_text(-0.1625, 1.0),
                                                    clock_text(0.5318, 1.0), spin_text(8.89), out_text(0.592))]
    t40, b40 = min(bb[1] for bb in y40), max(bb[3] for bb in y40)
    t28, b28 = min(bb[1] for bb in y28), max(bb[3] for bb in y28)
    boxes = {"label": (ROW_X0, LABEL_DY + t40, ROW_X0 + left_w, LABEL_DY + b40),
             "left rows": (ROW_X0, SUB_DY + t28, ROW_X0 + left_rows, FIX_DY + b28),
             "right rows": (ROW_X1 - right_rows, SUB_DY + t28, ROW_X1, FIX_DY + b28),
             "event": (ROW_X1 - ev_w, LABEL_DY + t40, ROW_X1, LABEL_DY + b40)}
    edge = float(man["edge_x_px"])
    h = man["toast_thick_px"] / 2.0
    line_y = top - h
    settle_real = settle_v / S
    hits = []
    extent = [math.inf, math.inf, -math.inf, -math.inf]
    for m in PANELS:
        r = runs[m]
        for tv in np.arange(-(ea + F), P - ea + 1e-9, 1.0 / 240.0):
            st = state_at(r, tv / S, settle_real)
            pts = toast_corners(st, ppm, edge, line_y, h, a)
            for (px, py) in pts:
                extent = [min(extent[0], px), min(extent[1], py), max(extent[2], px), max(extent[3], py)]
                assert py <= floor + 0.6, f"the {m} toast sinks into the floor"
                for name, (x0b, y0b, x1b, y1b) in boxes.items():
                    if x0b - 4 <= px <= x1b + 4 and y0b - 4 <= py <= y1b + 4:
                        hits.append((m, name, tv))
    names = list(boxes)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            A, B = boxes[names[i]], boxes[names[j]]
            sep = A[2] + 16 <= B[0] or B[2] + 16 <= A[0] or A[3] + 4 <= B[1] or B[3] + 4 <= A[1]
            assert sep, f"{names[i]} meets {names[j]}"
    print(f"row check: label row to x {boxes['label'][2]:.0f} px, event row from x {boxes['event'][0]:.0f} px (widest "
          f"{ev_w:.0f} px), left readouts to x {boxes['left rows'][2]:.0f} px, right readouts from x "
          f"{boxes['right rows'][0]:.0f} px; the label and event rows span {boxes['label'][1]:.0f} to {boxes['label'][3]:.0f} px, the readouts {boxes['left rows'][1]:.0f} to {boxes['left rows'][3]:.0f} px under the band top; the table top {top:.0f} px "
          f"under the band top (slab to {top + SLAB_PX:.0f}), its edge at x {edge:.0f}, the floor at {floor:.0f} "
          f"({floor - top:.0f} px = {Ht:g} m at {ppm:g} px/m); the toast slab ({2 * a * ppm:.0f} by {2 * h:.0f} px) over the "
          f"whole cycle spans x {extent[0]:.0f} to {extent[2]:.0f} and y {extent[1]:.0f} to {extent[3]:.0f} px under the band "
          f"top: {len(hits)} touches with a text box; each band is {BAND_H} px tall (y {BAND_Y['nudged']} to "
          f"{BAND_Y['nudged'] + BAND_H} and {BAND_Y['swiped']} to {BAND_Y['swiped'] + BAND_H}); the caption band starts at "
          f"y {int(man['caption_y'] * H)}")
    assert not hits, f"the toast meets a text box: {hits[:3]}"
    assert extent[0] > 8 and extent[2] < W - 8 and extent[1] > boxes["left rows"][3] + 4 and extent[3] < BAND_H - 4
    assert BAND_Y["swiped"] + BAND_H <= int(man["caption_y"] * H), "the bottom band reaches the caption band"
    assert PAYOFF_Y - 20 > int(man["caption_y"] * H) + 90, "the card meets the caption band"
    return ev


def legend_text(man: dict) -> str:
    return f"same toast, same {man['table_m'] * 100:g} cm table, 1/{man['slow']:g} speed"


def label_text(m: str) -> str:
    return {"nudged": "nudged, 5 cm/s", "swiped": "swiped, 1.5 m/s"}[m]


def event_text(m: str) -> str:
    return {"nudged": "nudged: butter down", "swiped": "swiped: butter up"}[m]


def turned_text(th: float) -> str:
    return f"turned {math.degrees(th):.0f} deg"


def clock_text(r: float, t_touch: float) -> str:
    if r < 0.0:
        return f"edge in {-r * 1000:.0f} ms"
    if r >= t_touch:
        return f"landed at {t_touch * 1000:.0f} ms"
    return f"{r * 1000:.0f} ms past the edge"


def spin_text(w: float) -> str:
    return f"spin {w / (2 * math.pi):.1f} turns a second"


def out_text(x: float) -> str:
    return "on the table" if x < 0.0 else f"{x * 100:.1f} cm out"


def payoff_lines(man: dict, ev: dict) -> list[str]:
    rn, rs = ev["runs"]["nudged"], ev["runs"]["swiped"]
    text = man["payoff_text"].format(deg_n=rn["deg"], deg_s=rs["deg"], w_n=rn["w"], w_s=rs["w"], v_flip=ev["v_flip"],
                                     v_flip_b=ev["v_flip_b"])
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
        self.P = man["cycle_s"]
        self.P_f = int(round(man["cycle_s"] * self.fps))
        self.c0_f = int(round(man["first_cycle_at"] * self.fps))
        self.ea, self.F = man["edge_at"], man["reset_fade"]
        self.runs = ev["runs"]
        self.a = man["toast_m"] / 2.0
        self.edge = float(man["edge_x_px"])
        self.top = float(man["table_top_dy"])
        self.floor = float(man["floor_dy"])
        self.h = man["toast_thick_px"] / 2.0
        self.line_y = self.top - self.h
        self.settle_real = man["settle_s"] / self.S
        # The trail of each centre of mass from the edge to its touchdown, sampled every 0.5 ms real.
        self.trail = {}
        for m in PANELS:
            r = self.runs[m]
            ts = np.arange(0.0, r["t_touch"], 0.0005)
            pts = []
            for t in ts:
                st = state_at(r, float(t), self.settle_real)
                pts.append((self.edge + st["x"] * self.ppm, self.line_y - st["y"] * self.ppm))
            self.trail[m] = (ts, pts)
        self.static = Image.new("RGB", (W * SS, BAND_H * SS), BG)
        self.draw_static(ImageDraw.Draw(self.static))

    def phase(self, f: int) -> tuple[int, float]:
        k, tau_f = divmod(f - self.c0_f, self.P_f)
        return k, tau_f / self.fps

    @staticmethod
    def L_(x: float, y: float) -> tuple[float, float]:
        """Layer (2x) pixel of a band-local point, rounded to 1e-4 px so equal states draw equal pixels."""
        return round(x * SS, 4), round(y * SS, 4)

    def draw_static(self, d: ImageDraw.ImageDraw) -> None:
        man = self.man
        x0, top, edge = float(man["table_x0_px"]), self.top, self.edge
        # The floor: a strip across the band.
        f0, f1 = self.L_(0, self.floor), self.L_(W, self.floor + 10)
        d.rectangle((f0[0], f0[1], f1[0], f1[1]), fill=FLOOR)
        g0, g1 = self.L_(0, self.floor), self.L_(W, self.floor)
        d.line((*g0, *g1), fill=RIM, width=2 * SS)
        # The table: a slab from its left end to the edge, two legs, the edge face lit.
        for lx in (x0 + 30, edge - 60):
            l0, l1 = self.L_(lx, top + SLAB_PX), self.L_(lx + LEG_W, self.floor)
            d.rectangle((l0[0], l0[1], l1[0], l1[1]), fill=DECK_A)
        s0, s1 = self.L_(x0, top), self.L_(edge, top + SLAB_PX)
        d.rectangle((s0[0], s0[1], s1[0], s1[1]), fill=DECK_B)
        t0, t1 = self.L_(x0, top), self.L_(edge, top)
        d.line((*t0, *t1), fill=RIM, width=3 * SS)
        e0, e1 = self.L_(edge - 1, top), self.L_(edge - 1, top + SLAB_PX)
        d.line((*e0, *e1), fill=RIM, width=3 * SS)

    def draw_toast(self, d: ImageDraw.ImageDraw, m: str, st: dict) -> None:
        a, h = self.a, self.h
        pts = toast_corners(st, self.ppm, self.edge, self.line_y, h, a)
        d.polygon([self.L_(*p) for p in pts], fill=CRUST)
        inner = toast_corners(st, self.ppm, self.edge, self.line_y, h - 1.5, a - 1.5 / self.ppm)
        d.polygon([self.L_(*p) for p in inner], fill=CRUMB)
        # The butter: a BUTTER_PX strip along the top face.
        c, sn = math.cos(st["th"]), math.sin(st["th"])
        cx, cy = self.edge + st["x"] * self.ppm, self.line_y - st["y"] * self.ppm
        ex, ey = c * (a * self.ppm - 1.0), sn * (a * self.ppm - 1.0)
        nx, ny = sn, -c
        q = [(cx - ex + nx * (h - BUTTER_PX), cy - ey + ny * (h - BUTTER_PX)), (cx + ex + nx * (h - BUTTER_PX), cy + ey + ny * (h - BUTTER_PX)),
             (cx + ex + nx * h, cy + ey + ny * h), (cx - ex + nx * h, cy - ey + ny * h)]
        d.polygon([self.L_(*p) for p in q], fill=BUTTER)

    def scene(self, m: str, tau: float) -> tuple[Image.Image, dict]:
        layer = self.static.copy()
        d = ImageDraw.Draw(layer)
        r = self.runs[m]
        rt = (tau - self.ea) / self.S
        st = state_at(r, rt, self.settle_real)
        st["rt"] = rt
        if rt > 0.0:
            ts, pts = self.trail[m]
            n = int(np.searchsorted(ts, min(rt, r["t_touch"]), side="right"))
            path = [self.L_(*p) for p in pts[:n]]
            if rt < r["t_touch"]:
                path.append(self.L_(self.edge + st["x"] * self.ppm, self.line_y - st["y"] * self.ppm))
            if len(path) >= 2:
                d.line(path, fill=blend(COLOUR[m], 0.55), width=2 * SS)
        self.draw_toast(d, m, st)
        return layer, st

    def draw_panel(self, m: str, f: int) -> tuple[Image.Image, dict]:
        k, tau = self.phase(f)
        P, F = self.P, self.F
        layer, st = self.scene(m, tau)
        st["alpha"], st["k"] = 1.0, k
        if tau >= P - F:
            a = (tau - (P - F)) / F
            new, st_new = self.scene(m, tau - P)
            layer = Image.blend(layer, new, a)
            st["alpha"] = max(0.0, 1.0 - 2.0 * a)
            st_new["alpha"], st_new["k"] = max(0.0, 2.0 * a - 1.0), k + 1
            if a >= 0.5:
                st = st_new
        return layer, st

    def draw_text(self, d: ImageDraw.ImageDraw, states: dict, hud_alpha: float) -> None:
        man = self.man
        for m, st in states.items():
            y0 = BAND_Y[m]
            r = self.runs[m]
            a = st["alpha"]
            rt = st["rt"]
            landed = rt >= r["t_touch"]
            d.text((ROW_X0, y0 + LABEL_DY), label_text(m), font=self.font, fill=COLOUR[m], anchor="lm")
            th = r["thT"] if landed else st["th"]
            w = r["w"] if rt >= r["t_leave"] else st["w"]
            d.text((ROW_X0, y0 + SUB_DY), turned_text(th), font=self.font_small, fill=blend(GOLD if landed else TEXT, a),
                   anchor="lm")
            d.text((ROW_X0, y0 + FIX_DY), clock_text(rt, r["t_touch"]), font=self.font_small, fill=blend(MUTED, a),
                   anchor="lm")
            d.text((ROW_X1, y0 + SUB_DY), spin_text(w), font=self.font_small, fill=blend(TEXT, a), anchor="rm")
            d.text((ROW_X1, y0 + FIX_DY), out_text(st["out"]), font=self.font_small,
                   fill=blend(GOLD if landed else MUTED, a), anchor="rm")
            if landed:
                d.text((ROW_X1, y0 + LABEL_DY), event_text(m), font=self.font, fill=blend(GOLD, a), anchor="rm")
        if hud_alpha > 0.02:
            d.text((W / 2, LEGEND_Y), legend_text(man), font=self.font, fill=blend(TEXT, hud_alpha), anchor="mm")

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
            # The geometry runs on; the legend and card fade out over the first half of the loop fade
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
        assert int(diff.max()) == 0
        wrap = self.live_frame(total, title_alpha=1.0, hud_alpha=0.0)   # the scene one period on, drawn live
        diff = np.abs(first.astype(int) - wrap.astype(int))
        print(f"periodicity check: the scene drawn live at {self.man['scene_duration']:g} s differs from 0 s in "
              f"{int((diff.max(axis=2) > 24).sum())} px (max channel difference {int(diff.max())})")
        assert int(diff.max()) == 0
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
    man = json.loads((ROOT / "projects/toast/manifest.json").read_text())
    ev = measure(man)
    if "--measure-only" in sys.argv:
        return
    if "--frames" in sys.argv:
        times = [float(v) for v in sys.argv[sys.argv.index("--frames") + 1].split(",")]
        r = Renderer(man, ev)
        (ROOT / "media/toast").mkdir(parents=True, exist_ok=True)
        for tv in times:
            Image.fromarray(r.frame_at(int(round(tv * man["fps"])))).save(ROOT / f"media/toast/smoke-{tv}.png")
        print("smoke frames: " + ", ".join(f"{tv}" for tv in times))
        return
    Renderer(man, ev).render(ROOT / "media/toast/footage.mp4")


if __name__ == "__main__":
    main()
