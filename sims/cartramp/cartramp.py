#!/usr/bin/env python3
"""Cart on a ramp: fired straight up from a rolling cart, does the ball land back in the cup?

Two panels on the same clock, the same ramp drawn the same way at the same
scale, side view. A cart of mass M with light wheels and no friction is let
go from rest at the top of a ramp of angle alpha and length L; it rolls at
g sin(alpha) along the ramp and its normal force M g cos(alpha) stays
positive. A distance d down the ramp it passes a trigger and its spring
launcher fires a ball of mass m at u relative to the cart's velocity at
that instant (the ball's lab velocity is the cart's plus u along the tube;
the cart takes the opposite along-slope impulse; the impulse square to the
ramp is absorbed by the ramp). The ball then flies freely at g with no air
drag. Top panel: the tube points straight up (vertical in the lab). In the
cart's frame, which accelerates down the slope at g sin(alpha), the
along-slope part of gravity is cancelled, so the ball keeps its up-slope
drift u sin(alpha) (plus the cart's recoil m u sin(alpha) / M) while
gravity square to the ramp, g cos(alpha), brings it back to the ramp line
after

    t = 2 u cos(alpha) / (g cos(alpha)) = 2 u / g,

so it lands 2 u^2 sin(alpha) (1 + m / M) / g up the slope behind the cart.
Bottom panel: the tube points square to the ramp; the ball has no
along-slope motion relative to the cart (and the cart no along-slope
recoil), so it flies 2 u / (g cos(alpha)) and drops back into the cup.
Both bands are integrated in the lab frame by classical RK4 at
steps_per_second (the cart along the ramp from rest, the trigger crossing
located by bisection inside the step; then the cart and the ball together,
the landing on the ramp line, the apex and the foot of the ramp located by
bisection) and checked against the closed forms, the ball's energy in
flight, the momentum balance of the launch and a half-step rerun. The
drawing is larger than life: the ball's centre sits in the cup some px
above the ramp surface, so the top band's drawn flight is sheared by a
linear ramp in time (a constant velocity offset, so still a parabola)
from the cup down to the surface and the drawn ball lands on the measured
mark; the readouts are the model's. After the landing the top ball rests
at its landing point and the bottom ball in the cup; both carts roll on to a stop pad at the foot of the
ramp and stop there (no bounce; the stop itself is not modelled). The cart
and the ball are points on the ramp line for every measurement and are
drawn larger than life. The run repeats every cycle_s seconds of video with
a crossfade back to the held setup; the cycle divides the scene length, so
the scene is exactly periodic and the last frame equals the first. Shown at
1/slow speed. Deterministic, no seed.

Measured and printed: the trigger time and speed, the normal force, for
each band the flight time, the apex, the landing point and the miss along
the ramp (RK4 against the closed forms, the energy, the momentum balance,
a half-step rerun), the cart's position and speed at the landing and at
the foot, the position tables at table_step_s, the no-recoil miss, the
other angles, launch speeds and cart masses and the launch from rest for
the description, the brief's checks, the schedule in video time, the
on-screen text widths and the layout clearances.

usage: cartramp.py [--measure-only] [--frames t1,t2,...]
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
INK = (150, 158, 170)
PLANK = (54, 62, 76)
PLANK_EDGE = (150, 160, 176)
CART_FILL = (214, 222, 232)
CART_EDGE = (120, 132, 150)
WHEEL = (70, 78, 92)
WHEEL_RIM = (150, 160, 176)
PAD = (84, 94, 110)
BALL = (236, 240, 244)
BALL_EDGE = (150, 160, 176)

# Layout: overlay at y 96..130 (captions.py), three title rows at y 186/244/302
# for the first seconds, then the legend at y 236 and the shared clock at y
# 290; two panels stacked, the vertical launch in the band y 330..880 and the
# square launch in y 880..1430, each drawn at 2x in its own geometry layer;
# each band has its label row 40 px under the band top, its second row at 84
# and its third at 120 (left column from x 40, right column to x 1040) and
# the gold event row at 172 (right column); the ramp descends left to right
# from ramp_x0_px at ramp_top_dy under the band top, its foot lower right;
# captions at caption_y 0.75 (y 1440..1530); the six-line card from y 1572 at
# a 48 px pitch.
LEGEND_Y, CLOCK_Y = 236, 290
TITLE_Y = (186, 244, 302)
SS = 2
PAYOFF_Y, PAYOFF_PITCH = 1572.0, 48
PANELS = ("vertical", "square")
BAND_Y = {"vertical": 330, "square": 880}
BAND_H = 550
LABEL_DY, SUB_DY, FIX_DY, EVENT_DY = 40, 84, 120, 172
ROW_X0, ROW_X1 = 40, 1040
COLOUR = {"vertical": CORAL, "square": TEAL}
HELD, ROLL, STOP = "held", "rolling", "stopped"
CUP, AIR, DOWN = "cup", "air", "down"
# The cart in plank coordinates (u down the slope, v up from the surface), px at 1x.
WHEEL_R, WHEEL_U = 7.0, 16.0
CHASSIS_U, CHASSIS_V0, CHASSIS_V1 = 26.0, 9.0, 17.0
TUBE_HALF, TUBE_WALL, TUBE_LEN = 10.0, 4.0, 28.0
BALL_R = 8.0
PLANK_T, EXT_TOP, EXT_END = 12.0, 30.0, 34.0
PAD_U0, PAD_W, PAD_H = 30.0, 10.0, 26.0
PIN_LEN, PIN_W = 22, 6
LEG_S = (0.6, 1.4)
DOT_EVERY_S = 0.012


def blend(col, a: float, base=BG) -> tuple:
    a = max(0.0, min(1.0, a))
    return tuple(int(round(c * a + b * (1 - a))) for c, b in zip(col, base))


# --- measurement --------------------------------------------------------------
def tube_dir(mode: str, a: float) -> tuple[float, float]:
    """Lab unit vector of the launcher tube (x along the run, y up)."""
    return (0.0, 1.0) if mode == "vertical" else (math.sin(a), math.cos(a))


def closed_forms(mode: str, M: float, m: float, u: float, a_deg: float, d: float, L: float, g: float,
                 recoil: bool = True, from_rest: bool = False) -> dict:
    a = math.radians(a_deg)
    sa, ca = math.sin(a), math.cos(a)
    ac = g * sa
    t_trig = 0.0 if from_rest else math.sqrt(2.0 * d / ac)
    v_trig = ac * t_trig
    dx, dy = tube_dir(mode, a)
    rel_along = u * (dx * ca - dy * sa)        # the ball's along-slope velocity relative to the cart (down +)
    rel_norm = u * (dx * sa + dy * ca)         # square to the ramp, away from it
    kick = -(m / M) * rel_along if recoil else 0.0
    t_f = 2.0 * rel_norm / (g * ca)
    apex = rel_norm ** 2 / (2.0 * g * ca)
    gap = (kick - rel_along) * t_f             # the ball up-slope of the cart at the landing
    v_cart = v_trig + kick
    s_land = v_cart * t_f + 0.5 * ac * t_f * t_f
    t_foot = (-v_cart + math.sqrt(v_cart * v_cart + 2.0 * ac * (L - d))) / ac
    return {"t_trig": t_trig, "v_trig": v_trig, "ac": ac, "N": M * g * ca, "rel_along": rel_along, "rel_norm": rel_norm,
            "kick": kick, "t_f": t_f, "apex": apex, "gap": gap, "s_land": s_land, "v_land": v_cart + ac * t_f,
            "t_foot": t_foot, "v_foot": v_cart + ac * t_foot, "impulse_norm": m * rel_norm}


def simulate(mode: str, M: float, m: float, u: float, a_deg: float, d: float, L: float, g: float, dt: float,
             recoil: bool = True, from_rest: bool = False, pad: bool = True) -> dict:
    """Classical RK4 at dt in the lab frame. Phase 1: the cart (s along the ramp from the top, v) from rest
    until s = d (bisection inside the step). The launch: the ball leaves with the cart's velocity plus u
    along the tube; the cart takes the opposite along-slope impulse (if recoil). Phase 2: y = (s, v, x, y,
    vx, vy) with the ball's lab position from the launch point (x along the run, y up); the landing is where
    the height above the ramp line h = x sin a + y cos a returns to 0 (bisection), the apex where the normal
    velocity vanishes, the foot where s = L (the cart stops there if pad); the run continues until every event
    is found."""
    a = math.radians(a_deg)
    sa, ca = math.sin(a), math.cos(a)
    ac = g * sa

    def f_cart(y: np.ndarray) -> np.ndarray:
        return np.array([y[1], ac])

    def step(fn, y: np.ndarray, hh: float) -> np.ndarray:
        k1 = fn(y)
        k2 = fn(y + 0.5 * hh * k1)
        k3 = fn(y + 0.5 * hh * k2)
        k4 = fn(y + hh * k3)
        return y + hh * (k1 + 2.0 * k2 + 2.0 * k3 + k4) / 6.0

    def locate(fn, y: np.ndarray, hh: float, cond) -> tuple[float, np.ndarray]:
        """Bisection for the sub-step at which cond(state) first holds (cond false at y, true at y + hh)."""
        lo, hi = 0.0, hh
        for _ in range(80):
            mid = 0.5 * (lo + hi)
            if cond(step(fn, y, mid)):
                hi = mid
            else:
                lo = mid
        return hi, step(fn, y, hi)

    # Phase 1: the cart to the trigger.
    if from_rest:
        t_trig, v_trig, n1 = 0.0, 0.0, 0
    else:
        y = np.array([0.0, 0.0])
        n1 = 0
        while True:
            yn = step(f_cart, y, dt)
            if yn[0] >= d:
                tau, yt = locate(f_cart, y, dt, lambda z: z[0] >= d)
                t_trig, v_trig = n1 * dt + tau, float(yt[1])
                break
            y, n1 = yn, n1 + 1
    dx, dy = tube_dir(mode, a)
    rel_along = u * (dx * ca - dy * sa)
    kick = -(m / M) * rel_along if recoil else 0.0
    v_cart = v_trig + kick
    bvx, bvy = v_trig * ca + u * dx, -v_trig * sa + u * dy
    p_before = (M + m) * v_trig
    p_after = M * v_cart + m * (bvx * ca - bvy * sa)
    # Phase 2: the cart and the ball together.
    stopped = [False]

    def f(y: np.ndarray) -> np.ndarray:
        return np.array([0.0 if stopped[0] else y[1], 0.0 if stopped[0] else ac, y[4], y[5], 0.0, -g])

    def h_of(z: np.ndarray) -> float:
        return z[2] * sa + z[3] * ca

    def vn_of(z: np.ndarray) -> float:
        return z[4] * sa + z[5] * ca

    y = np.array([d, v_cart, 0.0, 0.0, bvx, bvy])
    T, Y = [0.0], [y.copy()]
    ev: dict = {}
    n = 0
    t_max = 4.0
    while True:
        t = n * dt
        yn = step(f, y, dt)
        tn = t + dt
        if "apex" not in ev and vn_of(y) > 0.0 and vn_of(yn) <= 0.0:
            tau, z = locate(f, y, dt, lambda zz: vn_of(zz) <= 0.0)
            ev["apex"] = (t + tau, z.copy())
        if "land" not in ev and t > 0.0 and h_of(yn) <= 0.0:
            tau, z = locate(f, y, dt, lambda zz: h_of(zz) <= 0.0)
            ev["land"] = (t + tau, z.copy())
        if "foot" not in ev and yn[0] >= L:
            tau, z = locate(f, y, dt, lambda zz: zz[0] >= L)
            ev["foot"] = (t + tau, z.copy())
            if pad:
                # The pad stops the cart inside this step: redo the step with the cart frozen at L.
                stopped[0] = True
                yc = z.copy()
                yc[0], yc[1] = L, 0.0
                yn = step(f, yc, dt - tau)
                yn[0], yn[1] = L, 0.0
        n += 1
        y = yn
        T.append(tn)
        Y.append(y.copy())
        done = "land" in ev and ("foot" in ev or not pad)
        if (done and tn >= ev["land"][0] + 0.05) or tn > t_max:
            break
    tab = np.array(Y)
    tt = np.array(T)
    h = tab[:, 2] * sa + tab[:, 3] * ca
    sb = tab[:, 2] * ca - tab[:, 3] * sa
    E = 0.5 * m * (tab[:, 4] ** 2 + tab[:, 5] ** 2) + m * g * tab[:, 3]
    i_land = int(np.searchsorted(tt, ev["land"][0]))
    t_land, zl = ev["land"]
    t_apex, za = ev["apex"]
    out = {"t": tt, "s": tab[:, 0], "v": tab[:, 1], "x": tab[:, 2], "y": tab[:, 3], "vx": tab[:, 4], "vy": tab[:, 5],
           "h": h, "sb": sb, "t_trig": t_trig, "v_trig": v_trig, "kick": kick, "v_cart0": v_cart, "bvx": bvx, "bvy": bvy,
           "t_land": t_land, "sb_land": float(zl[2] * ca - zl[3] * sa), "s_land": float(zl[0]), "v_land": float(zl[1]),
           "gap": float(zl[0] - d - (zl[2] * ca - zl[3] * sa)), "t_apex": t_apex, "apex": float(za[2] * sa + za[3] * ca),
           "E_dev": float(np.max(np.abs(E[:i_land + 1] - E[0]))), "p_before": p_before, "p_after": p_after,
           "steps": n1 + n, "steps1": n1, "mode": mode, "M": M, "m": m, "u": u, "a": a, "d": d, "L": L, "g": g,
           "dt": dt, "from_rest": from_rest, "recoil": recoil}
    if "foot" in ev:
        out["t_foot"], zf = ev["foot"]
        out["v_foot"] = float(zf[1])
    else:
        out["t_foot"], out["v_foot"] = math.inf, 0.0
    return out


def state_at(run: dict, rt: float) -> dict:
    """The lab state rt real seconds after the release: the cart's s (from the top) and v, the ball's lab
    offset from the launch point (x, y), its height h above the ramp line, its along-slope gap behind the
    cart, the time in the air and the phases."""
    d = run["d"]
    if rt < 0.0:
        return {"s": 0.0, "v": 0.0, "x": 0.0, "y": 0.0, "h": 0.0, "gap": 0.0, "t_air": 0.0, "phase": HELD, "ball": CUP}
    if rt < run["t_trig"]:
        ac = run["g"] * math.sin(run["a"])
        return {"s": 0.5 * ac * rt * rt, "v": ac * rt, "x": 0.0, "y": 0.0, "h": 0.0, "gap": 0.0, "t_air": 0.0,
                "phase": ROLL, "ball": CUP}
    t = rt - run["t_trig"]
    st = {k: float(np.interp(t, run["t"], run[k])) for k in ("s", "v", "x", "y", "h", "sb")}
    if t >= run["t_foot"]:
        st["s"], st["v"], phase = run["L"], 0.0, STOP
    else:
        phase = ROLL
    if t < run["t_land"]:
        ball, gap, t_air = AIR, st["s"] - d - st["sb"], t
    else:
        ball, gap, t_air = DOWN, run["gap"], run["t_land"]
        st["x"], st["y"], st["h"], st["sb"] = (float(np.interp(run["t_land"], run["t"], run[k])) for k in ("x", "y", "h", "sb"))
    return {"s": st["s"], "v": st["v"], "x": st["x"], "y": st["y"], "h": st["h"], "gap": gap, "t_air": t_air,
            "phase": phase, "ball": ball, "sb": st["sb"]}


def measure(man: dict) -> dict:
    g, M, m, u = man["g"], man["cart_kg"], man["ball_kg"], man["launch_speed_mps"]
    a_deg, L, d = man["angle_deg"], man["ramp_m"], man["trigger_m"]
    dt = 1.0 / man["steps_per_second"]
    S, P, D, fps, F, pa = man["slow"], man["cycle_s"], man["scene_duration"], man["fps"], man["reset_fade"], man["release_at"]
    cycles = D / P
    assert abs(cycles - round(cycles)) < 1e-9, "the cycle must divide the scene length"
    for key in ("cycle_s", "release_at", "first_cycle_at", "reset_fade", "scene_duration"):
        assert abs(man[key] * fps - round(man[key] * fps)) < 1e-9, f"{key} must be a whole number of frames"
    ppm = man["px_per_m"]
    a = math.radians(a_deg)
    sa, ca = math.sin(a), math.cos(a)
    # The drawn cup: the ball's centre sits CHASSIS_V1 + BALL_R along the tube above the surface; the top
    # band's drawn flight is sheared linearly in time from that height to the surface (see Geometry.ball_xy).
    launch_v = {"vertical": CHASSIS_V1 + BALL_R * ca, "square": CHASSIS_V1 + BALL_R}
    shear_px = launch_v["vertical"] - BALL_R
    print(f"setup: side view, two panels on one clock, the same ramp drawn the same way at the same scale: a {M:g} kg cart "
          f"with light wheels and no friction is let go from rest at the top of a {a_deg:g} degree ramp {L:g} m long "
          f"({L * sa * 100:.0f} cm of drop, {L * ca * 100:.1f} cm of run); it rolls at g sin a = {g * sa:.4f} m/s^2 and its "
          f"normal force M g cos a = {M * g * ca:.3f} N stays positive; {d * 100:g} cm down the ramp it passes a trigger and "
          f"its spring launcher fires a {m * 1000:g} g ball at u = {u:g} m/s relative to the cart's velocity at that instant "
          f"(the ball's lab velocity is the cart's plus u along the tube; the cart takes the opposite along-slope impulse; "
          f"the impulse square to the ramp is absorbed by the ramp); the ball then flies freely at g = {g:g} m/s^2 with no "
          f"air drag; top panel the tube points straight up (vertical in the lab), bottom panel square to the ramp; after "
          f"the landing the top ball rests at its landing point and the bottom ball in the cup; both carts roll "
          f"on to a stop pad at the foot of the ramp ({L:g} m from the top) and stop there (no bounce; the stop itself is "
          f"not modelled); the cart and the ball are points on the ramp line for every measurement and are drawn larger "
          f"than life; both bands integrated by classical RK4 at {man['steps_per_second']} steps per second (dt = {dt:.0e} s) "
          f"in the lab frame, the trigger, the apex, the landing on the ramp line and the foot located by bisection inside "
          f"the step, checked against the closed forms and a half-step rerun; shown at 1/{S:g} speed on a {P:g} s cycle "
          f"({P * fps:.0f} frames) with the release {pa:g} s into the cycle, {cycles:.0f} cycles in {D:g} s; drawn at "
          f"{ppm:g} px per metre (the ramp {L * ca * ppm:.0f} px of run and {L * sa * ppm:.0f} px of rise, the ball "
          f"{2 * BALL_R:.0f} px); deterministic, no seed")
    cf = {k: closed_forms(k, M, m, u, a_deg, d, L, g) for k in PANELS}
    runs = {k: simulate(k, M, m, u, a_deg, d, L, g, dt) for k in PANELS}
    halves = {k: simulate(k, M, m, u, a_deg, d, L, g, 0.5 * dt) for k in PANELS}
    ev: dict = {"cf": cf, "runs": runs, "halves": halves, "launch_v": launch_v}
    r0 = runs["vertical"]
    print(f"trigger: the cart from rest reaches the trigger {d * 100:g} cm down the ramp at {r0['t_trig']:.6f} s = "
          f"{r0['t_trig']:.4f} s moving {r0['v_trig']:.6f} m/s = {r0['v_trig']:.4f} m/s (closed form sqrt(2 d / (g sin a)) = "
          f"{cf['vertical']['t_trig']:.6f} s, g sin a t = {cf['vertical']['v_trig']:.6f} m/s; diffs "
          f"{r0['t_trig'] - cf['vertical']['t_trig']:+.1e} s, {r0['v_trig'] - cf['vertical']['v_trig']:+.1e} m/s), "
          f"{r0['steps1']} steps; the normal force on the cart M g cos a = {M * g * ca:.4f} N = {M * g * ca:.3f} N, positive, "
          f"so the cart stays on the ramp")
    assert abs(r0["t_trig"] - cf["vertical"]["t_trig"]) < 1e-9
    for key in PANELS:
        r, c, hf = runs[key], cf[key], halves[key]
        name = "straight up (top panel)" if key == "vertical" else "square to the ramp (bottom panel)"
        if key == "vertical":
            rel = (f"the ball's velocity relative to the cart has an up-slope part u sin a = {-c['rel_along']:.4f} m/s and a part "
                   f"square to the ramp u cos a = {c['rel_norm']:.4f} m/s; the launch kicks the cart m u sin a / M = {c['kick']:.4f} "
                   f"m/s down the slope (the square part m u cos a = {c['impulse_norm']:.4f} kg m/s goes into the ramp)")
        else:
            rel = (f"the ball's velocity relative to the cart is all square to the ramp, u = {c['rel_norm']:.4f} m/s, with no "
                   f"along-slope part ({c['rel_along']:.1e} m/s), so the cart gets no along-slope kick ({c['kick']:.1e} m/s; the "
                   f"impulse m u = {c['impulse_norm']:.4f} kg m/s presses the cart into the ramp)")
        verdict = (f"the ball lands {r['gap'] * 100:.4f} cm = {r['gap'] * 100:.2f} cm = {r['gap'] * 100:.0f} cm up the slope behind "
                   f"the cart" if key == "vertical" else
                   f"the ball lands {abs(r['gap']) * 100:.2e} cm from the cart along the slope: dead in the cup (miss "
                   f"{abs(r['gap']):.1e} m)")
        print(f"{name}: {rel}; RK4: the ball is in the air {r['t_land']:.6f} s = {r['t_land']:.4f} s (closed form "
              f"{'2 u / g' if key == 'vertical' else '2 u / (g cos a)'} = {c['t_f']:.6f} s, diff {r['t_land'] - c['t_f']:+.1e} s), "
              f"reaches {r['apex'] * 100:.4f} cm = {r['apex'] * 100:.2f} cm above the ramp line at {r['t_apex']:.4f} s (closed form "
              f"{c['apex'] * 100:.4f} cm, diff {(r['apex'] - c['apex']) * 100:+.1e} cm) and comes down on the ramp line "
              f"{r['sb_land'] * 100:.4f} cm past the trigger while the cart is {(r['s_land'] - d):.6f} m = {(r['s_land'] - d):.4f} m "
              f"past the trigger at {r['v_land']:.6f} m/s = {r['v_land']:.3f} m/s (closed form {c['s_land']:.6f} m, "
              f"{c['v_land']:.6f} m/s; diffs {r['s_land'] - d - c['s_land']:+.1e} m, {r['v_land'] - c['v_land']:+.1e} m/s): "
              f"{verdict} (closed form {'2 u^2 sin a (1 + m / M) / g' if key == 'vertical' else '0'} = {c['gap'] * 100:.4f} cm, "
              f"diff {(r['gap'] - c['gap']) * 100:+.1e} cm); the ball's energy in flight (kinetic plus potential) stays within "
              f"{r['E_dev']:.1e} J of its launch value; momentum along the slope at the launch: before (M + m) v = "
              f"{r['p_before']:.6f} kg m/s, after M V + m v_ball = {r['p_after']:.6f} kg m/s (diff {r['p_after'] - r['p_before']:+.1e}); "
              f"the cart reaches the stop pad at the foot {r['t_foot']:.6f} s = {r['t_foot']:.4f} s after the trigger at "
              f"{r['v_foot']:.4f} m/s (closed form {c['t_foot']:.6f} s, {c['v_foot']:.4f} m/s) and stops; {r['steps']} steps; "
              f"half-step rerun (dt = {0.5 * dt:.0e} s): in the air {hf['t_land']:.9f} s ({hf['t_land'] - r['t_land']:+.1e} s), "
              f"lands {hf['gap'] * 100:.9f} cm behind ({(hf['gap'] - r['gap']) * 100:+.1e} cm)"
              + (f"; drawing: the ball's centre is drawn {launch_v[key]:.1f} px above the ramp surface in the cup, so the drawn "
                 f"flight is sheared linearly in time by {shear_px:.1f} px = {shear_px / ppm * 100:.2f} cm square to the ramp "
                 f"(a constant velocity offset of {shear_px / ppm / r['t_land']:.4f} m/s, so the drawn path is still a parabola) "
                 f"and the drawn ball lands on the measured mark with its centre {BALL_R:.0f} px above the surface; the "
                 f"readouts and the mark are the model's" if key == "vertical" else
                 f"; drawing: the ball's centre is drawn {launch_v[key]:.1f} px above the ramp surface in the cup and comes "
                 f"back to the same point, no shear needed"))
        assert abs(r["t_land"] - c["t_f"]) < 1e-9 and abs(r["gap"] - c["gap"]) < 1e-9, "RK4 disagrees with the closed form"
        assert abs(hf["t_land"] - r["t_land"]) < 1e-9 and abs(r["p_after"] - r["p_before"]) < 1e-12, "a check fails"
        assert r["E_dev"] < 1e-12, "the ball's energy drifts"
    # Tables.
    ts = man["table_step_s"]
    tables: dict = {}
    for key in PANELS:
        r = runs[key]
        rows = []
        tt = 0.0
        while tt < r["t_land"] - 1e-12:
            rows.append(tt)
            tt += ts
        rows.append(r["t_land"])
        out = []
        tables[key] = []
        for tt in rows:
            st = {k: float(np.interp(tt, r["t"], r[k])) for k in ("s", "h", "sb")}
            past = st["s"] - d
            gap = past - st["sb"]
            tables[key].append((tt, past, st["h"], gap))
            out.append(f"{tt:.4f} s: cart {past:.4f} m past the trigger, ball {max(0.0, st['h']) * 100:.2f} cm above the ramp "
                       f"line and {gap * 100:.2f} cm up-slope of the cart")
        print(f"table {key} (RK4 table, real time after the trigger): " + "; ".join(out))
    ev["tables"] = tables
    # For the description: no recoil, other angles, speeds, cart masses, and the launch from rest.
    descr = []
    r_nr = simulate("vertical", M, m, u, a_deg, d, L, g, dt, recoil=False)
    c_nr = closed_forms("vertical", M, m, u, a_deg, d, L, g, recoil=False)
    ev["gap_norecoil"] = r_nr["gap"]
    descr.append(f"straight up without the recoil kick (the cart's speed unchanged by the launch): the ball lands "
                 f"{r_nr['gap'] * 100:.2f} cm behind the cart (closed form 2 u^2 sin a / g = {c_nr['gap'] * 100:.2f} cm), the cart "
                 f"{r_nr['s_land'] - d:.4f} m past the trigger at {r_nr['v_land']:.3f} m/s")
    ev["angles"], ev["speeds"], ev["masses"] = {}, {}, {}
    for a2 in man["description_angles_deg"]:
        rv, rs = (simulate(k, M, m, u, a2, d, L, g, dt, pad=False) for k in PANELS)
        cv = closed_forms("vertical", M, m, u, a2, d, L, g)
        ev["angles"][a2] = rv["gap"]
        descr.append(f"{a2:g} degree ramp (the same trigger {d * 100:g} cm down, reached at {rv['t_trig']:.4f} s at {rv['v_trig']:.4f} "
                     f"m/s; the ramp long enough): straight up the ball is in the air {rv['t_land']:.4f} s, {rv['apex'] * 100:.2f} cm "
                     f"high, and lands {rv['gap'] * 100:.2f} cm = {rv['gap'] * 100:.1f} cm behind the cart (closed form "
                     f"{cv['gap'] * 100:.2f} cm); square to the ramp {rs['t_land']:.4f} s, {rs['apex'] * 100:.2f} cm high, miss "
                     f"{abs(rs['gap']) * 100:.1e} cm")
    for u2 in man["description_speeds_mps"]:
        rv, rs = (simulate(k, M, m, u2, a_deg, d, L, g, dt, pad=False) for k in PANELS)
        cv = closed_forms("vertical", M, m, u2, a_deg, d, L, g)
        ev["speeds"][u2] = rv["gap"]
        descr.append(f"ball at {u2:g} m/s ({a_deg:g} degrees, the ramp long enough): straight up in the air {rv['t_land']:.4f} s, "
                     f"{rv['apex'] * 100:.2f} cm high, lands {rv['gap'] * 100:.2f} cm = {rv['gap'] * 100:.1f} cm behind the cart "
                     f"(closed form {cv['gap'] * 100:.2f} cm); square to the ramp {rs['t_land']:.4f} s, {rs['apex'] * 100:.2f} cm "
                     f"high, miss {abs(rs['gap']) * 100:.1e} cm")
    for M2 in man["description_cart_kg"]:
        rv, rs = (simulate(k, M2, m, u, a_deg, d, L, g, dt, pad=False) for k in PANELS)
        cv = closed_forms("vertical", M2, m, u, a_deg, d, L, g)
        ev["masses"][M2] = rv["gap"]
        descr.append(f"a {M2:g} kg cart (the same {m * 1000:g} g ball at {u:g} m/s): the kick drops to {cv['kick']:.4f} m/s and the "
                     f"straight-up ball lands {rv['gap'] * 100:.2f} cm = {rv['gap'] * 100:.1f} cm behind (closed form "
                     f"{cv['gap'] * 100:.2f} cm); square to the ramp miss {abs(rs['gap']) * 100:.1e} cm")
    rv, rs = (simulate(k, M, m, u, a_deg, d, L, g, dt, from_rest=True, pad=False) for k in PANELS)
    ev["gap_rest"], ev["miss_rest"] = rv["gap"], rs["gap"]
    descr.append(f"launched from rest at the trigger (no roll before the launch, the cart at 0 m/s): straight up the ball is "
                 f"in the air {rv['t_land']:.4f} s and still lands {rv['gap'] * 100:.2f} cm = {rv['gap'] * 100:.1f} cm behind the "
                 f"cart (the cart {rv['s_land'] - d:.4f} m past the trigger at {rv['v_land']:.3f} m/s); square to the ramp still "
                 f"dead in the cup (miss {abs(rs['gap']) * 100:.1e} cm): the miss does not depend on the cart's speed")
    print("for the description: " + "; ".join(descr))
    # The brief's checks.
    rv, rs = runs["vertical"], runs["square"]
    checks: list[tuple[str, float, float, float]] = [
        ("trigger at (s)", rv["t_trig"], 0.3498, 6e-5), ("trigger speed (m/s)", rv["v_trig"], 1.7153, 6e-5),
        ("cart a (m/s^2)", cf["vertical"]["ac"], 4.9035, 6e-5), ("normal force (N)", cf["vertical"]["N"], 8.493, 6e-4),
        ("vertical flight (s)", rv["t_land"], 0.4079, 6e-5), ("vertical apex (cm)", rv["apex"] * 100, 17.66, 6e-3),
        ("vertical miss (cm)", rv["gap"] * 100, 42.83, 6e-3), ("vertical miss, no recoil (cm)", r_nr["gap"] * 100, 40.79, 6e-3),
        ("vertical cart past the trigger (m)", rv["s_land"] - d, 1.1279, 6e-5), ("vertical cart speed (m/s)", rv["v_land"], 3.765, 6e-4),
        ("square flight (s)", rs["t_land"], 0.4710, 6e-5), ("square apex (cm)", rs["apex"] * 100, 23.55, 6e-3),
        ("square miss (cm)", rs["gap"] * 100, 0.0, 1e-7), ("square cart past the trigger (m)", rs["s_land"] - d, 1.3517, 6e-5),
        ("square cart speed (m/s)", rs["v_land"], 4.025, 6e-4),
        ("up-slope drift (m/s)", -cf["vertical"]["rel_along"], 1.000, 6e-4), ("square part (m/s)", cf["vertical"]["rel_norm"], 1.732, 6e-4),
        ("recoil kick (m/s)", cf["vertical"]["kick"], 0.050, 6e-4),
    ]
    want_tab = {0.1: (0.201, 0.131), 0.2: (0.451, 0.177), 0.3: (0.750, 0.137), 0.4079: (1.128, 0.000)}
    for tt, past, h, _ in tables["vertical"]:
        for wt, (wp, wh) in want_tab.items():
            if abs(tt - wt) < 6e-5:
                checks += [(f"vertical table {wt:g} s cart (m)", past, wp, 6e-4), (f"vertical table {wt:g} s ball (m)", h, wh, 6e-4)]
    for a2, want in ((20.0, 29.3), (45.0, 60.6)):
        if a2 in ev["angles"]:
            checks.append((f"{a2:g} deg miss (cm)", ev["angles"][a2] * 100, want, 6e-2))
    for u2, want in ((1.5, 24.1), (3.0, 96.4)):
        if u2 in ev["speeds"]:
            checks.append((f"u {u2:g} m/s miss (cm)", ev["speeds"][u2] * 100, want, 6e-2))
    if 5.0 in ev["masses"]:
        checks.append(("5 kg cart miss (cm)", ev["masses"][5.0] * 100, 41.2, 6e-2))
    checks += [("from rest miss (cm)", ev["gap_rest"] * 100, 42.8, 6e-2), ("from rest square miss (cm)", ev["miss_rest"] * 100, 0.0, 1e-7)]
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
    k1 = math.floor((D - t0) / P - 1e-9)
    starts = [t0 + kk * P for kk in range(k0, k1 + 1)]
    ev["cycles"] = int(round(cycles))

    def lst(off_: float) -> str:
        return ", ".join(f"{st + off_:.2f}" for st in starts if 0.0 <= st + off_ < D)

    t_trig = rv["t_trig"]
    land_v = {k: t_trig + runs[k]["t_land"] for k in PANELS}
    foot_v = {k: t_trig + runs[k]["t_foot"] for k in PANELS}
    ev["land_v"], ev["foot_v"] = land_v, foot_v
    tau0 = (0.0 - t0) % P
    r0t = (tau0 - pa) / S
    st0 = {k: state_at(runs[k], r0t) for k in PANELS}
    assert pa + S * max(foot_v.values()) + man["splash_s"] < P - F, "a cart is still rolling at the reset fade"
    print(f"schedule (video time, 1/{S:g} speed): cycles of {P:g} s start at " + ", ".join(f"{st:.2f}" for st in starts)
          + f" s (the first {-t0:.2f} s before the first frame); both carts are let go {pa:g} s into each cycle at {lst(pa)} s "
          f"(the stop pins fade over {man['pin_fade_s']:g} s); both pass the trigger and fire {S * t_trig:.2f} s after the release "
          f"at {lst(pa + S * t_trig)} s; the straight-up ball lands {S * runs['vertical']['t_land']:.2f} s after the launch at "
          f"{lst(pa + S * land_v['vertical'])} s ({pa + S * land_v['vertical']:.2f} s into the cycle; its event row lights "
          f"with a {man['splash_s']:g} s splash); the square ball drops into the cup {S * runs['square']['t_land']:.2f} s after the launch "
          f"at {lst(pa + S * land_v['square'])} s ({pa + S * land_v['square']:.2f} s into the cycle; its event row lights); the "
          f"top cart reaches the stop pad at {lst(pa + S * foot_v['vertical'])} s ({pa + S * foot_v['vertical']:.2f} s into the "
          f"cycle) and the bottom cart at {lst(pa + S * foot_v['square'])} s ({pa + S * foot_v['square']:.2f} s into the cycle); "
          f"the reset crossfade runs over the last {F:g} s of each cycle (from {lst(P - F)} s; the readouts out over its first "
          f"half and in over its second); on the first frame the cycle is {tau0:.2f} s in ({r0t:.3f} s real after the release: "
          f"the carts {st0['vertical']['phase']} at {st0['vertical']['s']:.3f} m, the top ball {st0['vertical']['ball']} at "
          f"{st0['vertical']['h'] * 100:.1f} cm up, {st0['vertical']['gap'] * 100:.1f} cm behind; the bottom ball "
          f"{st0['square']['ball']} at {st0['square']['h'] * 100:.1f} cm up); title until {man['title_until']:g} s; payoff card "
          f"from {man['payoff_t']:g} s; the title fades back in over the last {man['loop_fade']:g} s and the last frame repeats "
          f"the first (the scene is periodic: {D:g} s holds exactly {cycles:.0f} cycles)")
    # Text widths.
    font = os.environ["SEED_ZERO_FONT"]
    f24, f28, f34, f40, f56 = (ImageFont.truetype(font, n) for n in (24, 28, 34, 40, 56))
    widths = {"overlay@34": (f34, man["overlay"])}
    for j, line in enumerate(man["title"].split("|")):
        widths[f"title line {j + 1}@56"] = (f56, line)
    widths["legend@40"] = (f40, legend_text(man))
    widths["clock@28"] = (f28, clock_text(1.125))
    widths["clock held@28"] = (f28, clock_text(-1.0))
    for key in PANELS:
        widths[f"label {key}@40"] = (f40, label_text(key))
        widths[f"cart {key}@28"] = (f28, cart_text(L))
        widths[f"air {key}@28"] = (f28, air_text(AIR, runs[key]["t_land"]))
        widths[f"flight {key}@28"] = (f28, air_text(DOWN, runs[key]["t_land"]))
        widths[f"gap {key}@40"] = (f40, gap_text(runs[key]["gap"]))
        widths[f"height {key}@28"] = (f28, height_text(runs[key]["apex"]))
        widths[f"speed {key}@28"] = (f28, speed_text(runs[key]["v_foot"]))
        widths[f"event {key}@40"] = (f40, event_text(ev, key))
    widths["cup@28"] = (f28, air_text(CUP, 0.0))
    widths["trigger@24"] = (f24, trigger_text())
    widths["gap mark@24"] = (f24, mark_text(ev))
    for j, line in enumerate(payoff_lines(man, ev)):
        widths[f"payoff line {j + 1}@40"] = (f40, line)
    print("text widths (the on-screen strings verbatim): " + ", ".join(f"{kk} {f.getlength(s):.0f} px {s!r}" for kk, (f, s) in widths.items()))
    assert all(f.getlength(s) < 950 for f, s in widths.values()), "a text line is wider than 950 px"
    assert len(payoff_lines(man, ev)) <= 6, "the card has more than six lines"
    assert len(man["title"].replace("|", " ")) <= 100 and "<" not in man["title"] and ">" not in man["title"]
    # Layout checks: the geometry in band-local px.
    geo = Geometry(man)
    left = ROW_X0 + max(max(f40.getlength(label_text(key)), f28.getlength(cart_text(L)), f28.getlength(air_text(AIR, 0.4079)),
                            f28.getlength(air_text(DOWN, 0.4079)), f28.getlength(air_text(CUP, 0.0))) for key in PANELS)
    right = ROW_X1 - max(max(f40.getlength(gap_text(runs[key]["gap"])), f28.getlength(height_text(runs[key]["apex"])),
                             f28.getlength(speed_text(runs[key]["v_foot"]))) for key in PANELS)
    rows_bottom = FIX_DY + 14
    ev_w = {key: f40.getlength(event_text(ev, key)) for key in PANELS}
    ev_x0 = {key: ROW_X1 - ev_w[key] for key in PANELS}
    ev_y0, ev_y1 = EVENT_DY - 20, EVENT_DY + 20
    # The cart at the start: its highest drawn point (the tube's top) in each band.
    top_pt = {}
    for key in PANELS:
        du, dv = geo.tube_dir_plank(key)
        tips = [geo.plank_xy(0.0, (TUBE_HALF + TUBE_WALL) * sgn * (-dv) + du * TUBE_LEN,
                             CHASSIS_V1 + dv * TUBE_LEN + (TUBE_HALF + TUBE_WALL) * sgn * du) for sgn in (-1.0, 1.0)]
        top_pt[key] = min(p[1] for p in tips)
    # The drawn ball paths: the lowest y (highest point) and the extent over the event row's x range.
    path_min_y, path_in_row = {}, {}
    for key in PANELS:
        r = runs[key]
        pts = [geo.ball_xy(key, r["t"][i] / r["t_land"], r["x"][i], r["y"][i]) for i in range(0, len(r["t"]), 10)
               if r["t"][i] <= r["t_land"]]
        path_min_y[key] = min(p[1] for p in pts) - BALL_R
        inside = [p[1] - BALL_R for p in pts if p[0] + BALL_R >= ev_x0[key] - 10]
        path_in_row[key] = min(inside) if inside else math.inf
    foot = geo.plank_xy(L, 0.0, 0.0)
    end_lo = geo.plank_xy(L, EXT_END, -PLANK_T)
    pad_top = geo.plank_xy(L, PAD_U0 + PAD_W, PAD_H)
    land = geo.plank_xy(d + rv["sb_land"], 0.0, 0.0)
    cart_land = geo.plank_xy(rv["s_land"], 0.0, 0.0)
    mark_y = geo.plank_xy(0.5 * (d + rv["sb_land"] + rv["s_land"]), 0.0, geo.mark_v + 30.0)[1]
    legs = [geo.plank_xy(s_leg, 0.0, -PLANK_T) for s_leg in LEG_S]
    trig_lbl = geo.plank_xy(d, 0.0, -PLANK_T - 24.0)
    print(f"row check: the left column ends at x {left:.0f} px, the right column starts at x {right:.0f} px; both end "
          f"{rows_bottom} px under the band top; the event rows span {ev_y0} to {ev_y1} px under the band top, right-aligned "
          f"at x {ROW_X1} from x {ev_x0['vertical']:.0f} (top, {ev_w['vertical']:.0f} px) and {ev_x0['square']:.0f} (bottom, "
          f"{ev_w['square']:.0f} px); the ramp's drawn top at x {geo.x0:.0f}, {geo.y0:.0f} px under the band top, the cart's "
          f"start (s = 0) at x {geo.plank_xy(0, 0, 0)[0]:.1f}, {geo.plank_xy(0, 0, 0)[1]:.1f} px, the foot (s = {L:g} m) at x "
          f"{foot[0]:.1f}, {foot[1]:.1f} px, the plank's lower end corner at x {end_lo[0]:.1f}, {end_lo[1]:.1f} px, the stop "
          f"pad's top corner at x {pad_top[0]:.1f}, {pad_top[1]:.1f} px, the legs' feet at y {legs[0][1]:.0f} and {legs[1][1]:.0f} "
          f"px; the tube's top at the start is {top_pt['vertical']:.1f} px (top band) and {top_pt['square']:.1f} px (bottom "
          f"band) under the band top; the drawn ball paths rise to {path_min_y['vertical']:.1f} px (top) and "
          f"{path_min_y['square']:.1f} px (bottom) under the band top, and over the event rows' x range to "
          f"{path_in_row['vertical']:.1f} and {path_in_row['square']:.1f} px; the landing mark at x {land[0]:.1f}, {land[1]:.1f} "
          f"px and the cart's position at that instant at x {cart_land[0]:.1f}, {cart_land[1]:.1f} px ({(cart_land[0] - land[0]) / ca:.0f} "
          f"px along the slope), the gap label at y {mark_y:.0f} px under the band top; the trigger label at y {trig_lbl[1]:.0f} px; "
          f"each band is {BAND_H} px tall (y {BAND_Y['vertical']} to {BAND_Y['vertical'] + BAND_H} and {BAND_Y['square']} to "
          f"{BAND_Y['square'] + BAND_H}); the caption band starts at y {int(man['caption_y'] * H)}; the title rows end at y "
          f"{TITLE_Y[-1] + 28} and the overlay band ends at y 130")
    assert right - left > 40, "the columns meet"
    assert all(top_pt[key] > rows_bottom + 8 for key in PANELS), "the cart at the start meets the text rows"
    assert all(path_min_y[key] > rows_bottom + 8 for key in PANELS), "a ball path meets the text rows"
    assert all(path_in_row[key] > ev_y1 + 6 for key in PANELS), "a ball path meets an event row"
    assert end_lo[1] < BAND_H - 2 and pad_top[1] < BAND_H - 2 and all(lg[1] < BAND_H - 2 for lg in legs), "the ramp leaves the band"
    assert end_lo[0] < W - 40, "the ramp leaves the frame"
    assert geo.x0 - 4 > 20, "the ramp leaves the frame on the left"
    assert mark_y > ev_y1 + 6, "the gap label meets the event row"
    assert BAND_Y["square"] + BAND_H <= int(man["caption_y"] * H), "the bottom band reaches the caption band"
    assert PAYOFF_Y - 20 > int(man["caption_y"] * H) + 90, "the card meets the caption band"
    assert TITLE_Y[-1] + 28 <= BAND_Y["vertical"], "the title rows reach the first band"
    return ev


def legend_text(man: dict) -> str:
    return f"same cart, same ramp, 1/{man['slow']:g} speed"


def clock_text(r: float) -> str:
    return "held, at rest" if r < 0.0 else f"{r:.3f} s after the release"


def label_text(key: str) -> str:
    return "fired straight up" if key == "vertical" else "fired square to the ramp"


def cart_text(s: float) -> str:
    return f"cart: {max(0.0, s):.2f} m down the ramp"


def air_text(ball: str, t: float) -> str:
    if ball == CUP:
        return "ball in the cup"
    if ball == AIR:
        return f"in the air {t:.3f} s"
    return f"flight {t:.3f} s"


def gap_text(gap: float) -> str:
    return f"gap: {abs(gap) * 100:.1f} cm"


def height_text(h: float) -> str:
    return f"ball: {max(0.0, h) * 100:.1f} cm up"


def speed_text(v: float) -> str:
    return f"cart speed {abs(v):.2f} m/s"


def event_text(ev: dict, key: str) -> str:
    if key == "vertical":
        return f"no: lands {ev['runs']['vertical']['gap'] * 100:.0f} cm behind the cart"
    return "yes: dead in the cup"


def trigger_text() -> str:
    return "trigger"


def mark_text(ev: dict) -> str:
    return f"{ev['runs']['vertical']['gap'] * 100:.0f} cm"


def payoff_lines(man: dict, ev: dict) -> list[str]:
    rv, rs = ev["runs"]["vertical"], ev["runs"]["square"]
    text = man["payoff_text"].format(
        gap=rv["gap"] * 100, gap0=ev["gap_norecoil"] * 100, tf_v=rv["t_land"], tf_s=rs["t_land"], apex_v=rv["apex"] * 100,
        apex_s=rs["apex"] * 100, a45=ev["angles"].get(45.0, 0.0) * 100, a20=ev["angles"].get(20.0, 0.0) * 100,
        u30=ev["speeds"].get(3.0, 0.0) * 100, u15=ev["speeds"].get(1.5, 0.0) * 100, m5=ev["masses"].get(5.0, 0.0) * 100)
    return [s.strip() for s in text.split("|")]


# --- geometry -----------------------------------------------------------------
class Geometry:
    """Band-local pixel geometry (1x): the plank surface point of s metres from the cart's start, plank
    coordinates (u down the slope, v up from the surface, px) and the drawn ball position."""

    def __init__(self, man: dict):
        self.ppm = float(man["px_per_m"])
        self.a = math.radians(man["angle_deg"])
        self.sa, self.ca = math.sin(self.a), math.cos(self.a)
        self.x0, self.y0 = float(man["ramp_x0_px"]), float(man["ramp_top_dy"])   # the drawn top end of the plank
        self.L, self.d = man["ramp_m"], man["trigger_m"]
        self.launch_v = {"vertical": CHASSIS_V1 + BALL_R * self.ca, "square": CHASSIS_V1 + BALL_R}
        self.launch_u = {"vertical": -BALL_R * self.sa, "square": 0.0}
        self.mark_v = 44.0

    def plank_xy(self, s: float, u: float, v: float) -> tuple[float, float]:
        sp = s * self.ppm + EXT_TOP + u
        return self.x0 + sp * self.ca + v * self.sa, self.y0 + sp * self.sa - v * self.ca

    def tube_dir_plank(self, key: str) -> tuple[float, float]:
        """The tube direction in plank coordinates (u, v)."""
        return (-self.sa, self.ca) if key == "vertical" else (0.0, 1.0)

    def launch_xy(self, key: str, s_cart: float) -> tuple[float, float]:
        return self.plank_xy(s_cart, self.launch_u[key], self.launch_v[key])

    def ball_xy(self, key: str, frac: float, x: float, y: float) -> tuple[float, float]:
        """The drawn ball: the launch point of the cart at the trigger plus the lab offset (x along the run, y up);
        in the top band the launch point is sheared from the cup to the surface over the flight (frac = t / t_land,
        clipped to 1 after the landing), so the drawn ball lands on the measured mark."""
        w = max(0.0, min(1.0, frac)) if key == "vertical" else 0.0
        lx, ly = self.plank_xy(self.d, self.launch_u[key] * (1.0 - w), self.launch_v[key] - (self.launch_v[key] - BALL_R) * w)
        return lx + x * self.ppm, ly - y * self.ppm


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
        self.geo = Geometry(man)
        self.S = man["slow"]
        self.P = man["cycle_s"]
        self.P_f = int(round(man["cycle_s"] * self.fps))
        self.c0_f = int(round(man["first_cycle_at"] * self.fps))
        self.pa, self.F = man["release_at"], man["reset_fade"]
        self.runs = ev["runs"]
        self.L, self.d = man["ramp_m"], man["trigger_m"]

    def phase(self, f: int) -> tuple[int, float]:
        k, tau_f = divmod(f - self.c0_f, self.P_f)
        return k, tau_f / self.fps

    @staticmethod
    def L_(x: float, y: float) -> tuple[float, float]:
        """Layer (2x) pixel of a band-local point, rounded to 1e-4 px so equal states draw equal pixels."""
        return round(x * SS, 4), round(y * SS, 4)

    def P_(self, s: float, u: float, v: float) -> tuple[float, float]:
        return self.L_(*self.geo.plank_xy(s, u, v))

    def draw_ramp(self, d: ImageDraw.ImageDraw, key: str) -> None:
        g = self.geo
        L = self.L
        s_end = L + EXT_END / g.ppm
        s_top = -EXT_TOP / g.ppm
        # The legs, then the plank (a slab under the surface line) with a lighter top edge.
        for s_leg in LEG_S:
            a0, a1 = self.P_(s_leg, -8.0, -PLANK_T + 2.0), self.P_(s_leg, 8.0, -PLANK_T + 2.0)
            foot_y = (BAND_H - 6.0) * SS
            d.polygon([a0, a1, (a1[0], foot_y), (a0[0], foot_y)], fill=DECK_A)
        poly = [self.P_(s_top, 0.0, 0.0), self.P_(s_end, 0.0, 0.0), self.P_(s_end, 0.0, -PLANK_T), self.P_(s_top, 0.0, -PLANK_T)]
        d.polygon(poly, fill=PLANK, outline=RIM, width=2 * SS)
        d.line((*self.P_(s_top, 0.0, 0.0), *self.P_(s_end, 0.0, 0.0)), fill=PLANK_EDGE, width=3 * SS)
        # The trigger: a coral tick across the plank.
        d.line((*self.P_(self.d, 0.0, 2.0), *self.P_(self.d, 0.0, -PLANK_T + 2.0)), fill=CORAL, width=3 * SS)
        # The stop pad at the foot.
        pad = [self.P_(L, PAD_U0, 0.0), self.P_(L, PAD_U0 + PAD_W, 0.0), self.P_(L, PAD_U0 + PAD_W, PAD_H), self.P_(L, PAD_U0, PAD_H)]
        d.polygon(pad, fill=PAD, outline=RIM, width=2 * SS)

    def draw_pin(self, d: ImageDraw.ImageDraw, tv: float) -> None:
        """A stop pin just downhill of the held cart, normal to the slope, fading after the release."""
        a = 1.0 if tv < 0.0 else max(0.0, 1.0 - tv / self.man["pin_fade_s"])
        if a <= 0.0:
            return
        u = CHASSIS_U + PIN_W / 2.0 + 3.0
        d.line((*self.P_(0.0, u, 0.0), *self.P_(0.0, u, PIN_LEN)), fill=blend(GOLD, a), width=PIN_W * SS)

    def draw_cart(self, d: ImageDraw.ImageDraw, key: str, s: float) -> None:
        g = self.geo
        du, dv = g.tube_dir_plank(key)
        pu, pv = -dv, du      # across the tube
        body = [self.P_(s, -CHASSIS_U, CHASSIS_V0), self.P_(s, CHASSIS_U, CHASSIS_V0), self.P_(s, CHASSIS_U, CHASSIS_V1),
                self.P_(s, -CHASSIS_U, CHASSIS_V1)]
        d.polygon(body, fill=CART_FILL, outline=CART_EDGE, width=SS)
        for wu in (-WHEEL_U, WHEEL_U):
            cx, cy = self.P_(s, wu, WHEEL_R)
            r = WHEEL_R * SS
            d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=WHEEL, outline=WHEEL_RIM, width=2 * SS)
            d.ellipse((cx - 2 * SS, cy - 2 * SS, cx + 2 * SS, cy + 2 * SS), fill=WHEEL_RIM)
        # The tube: two walls and a base, in the band colour, from the chassis top along the tube direction.
        col = COLOUR[key]
        for sgn in (-1.0, 1.0):
            off = sgn * (TUBE_HALF + TUBE_WALL / 2.0)
            a0 = self.P_(s, pu * off, CHASSIS_V1 + pv * off)
            a1 = self.P_(s, pu * off + du * TUBE_LEN, CHASSIS_V1 + pv * off + dv * TUBE_LEN)
            d.line((*a0, *a1), fill=col, width=int(TUBE_WALL * SS))
        b0 = self.P_(s, -pu * (TUBE_HALF + TUBE_WALL), CHASSIS_V1 - pv * (TUBE_HALF + TUBE_WALL))
        b1 = self.P_(s, pu * (TUBE_HALF + TUBE_WALL), CHASSIS_V1 + pv * (TUBE_HALF + TUBE_WALL))
        d.line((*b0, *b1), fill=col, width=int(TUBE_WALL * SS))

    def draw_dots(self, d: ImageDraw.ImageDraw, key: str, st: dict) -> None:
        """The faint dotted lab path of the ball from the launch to now (held after the landing)."""
        if st["ball"] == CUP:
            return
        run = self.runs[key]
        t_end = min(st["t_air"], run["t_land"]) if st["ball"] == AIR else run["t_land"]
        col = blend(COLOUR[key], 0.5)
        n = int(math.floor(t_end / DOT_EVERY_S + 1e-9))
        r = 2.0 * SS
        for k in range(n + 1):
            tk = k * DOT_EVERY_S
            x, y = (float(np.interp(tk, run["t"], run[c])) for c in ("x", "y"))
            X, Y = self.L_(*self.geo.ball_xy(key, tk / run["t_land"], x, y))
            d.ellipse((X - r, Y - r, X + r, Y + r), fill=col)

    def draw_mark(self, d: ImageDraw.ImageDraw, st: dict) -> None:
        """Top band after the landing: a gold dashed tick at the measured landing point, a dashed gold line
        along the slope to the cart's position at that instant, and end ticks."""
        run = self.runs["vertical"]
        g = self.geo
        s_land, s_cart = self.d + run["sb_land"], run["s_land"]
        v = g.mark_v
        for s_t in (s_land, s_cart):
            a0, a1 = self.P_(s_t, 0.0, 4.0), self.P_(s_t, 0.0, v + 10.0)
            self.dashed(d, a0, a1, GOLD, 6 * SS, 4 * SS, 3 * SS)
        self.dashed(d, self.P_(s_land, 0.0, v), self.P_(s_cart, 0.0, v), GOLD, 8 * SS, 6 * SS, 3 * SS)

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

    def draw_ball(self, d: ImageDraw.ImageDraw, key: str, st: dict) -> None:
        g = self.geo
        if st["ball"] == CUP or (key == "square" and st["ball"] == DOWN):
            X, Y = self.L_(*g.launch_xy(key, st["s"]))
        else:
            X, Y = self.L_(*g.ball_xy(key, st["t_air"] / self.runs[key]["t_land"], st["x"], st["y"]))
        r = BALL_R * SS
        d.ellipse((X - r, Y - r, X + r, Y + r), fill=BALL, outline=BALL_EDGE, width=SS)

    def draw_splash(self, d: ImageDraw.ImageDraw, key: str, st: dict) -> None:
        if key != "vertical" or st["ball"] != DOWN:
            return
        run = self.runs["vertical"]
        u = (st["tv"] - self.S * (run["t_trig"] + run["t_land"])) / self.man["splash_s"]
        if 0.0 <= u < 1.0:
            X, Y = self.L_(*self.geo.ball_xy(key, 1.0, st["x"], st["y"]))
            rr = (10 + 30 * u) * SS
            d.ellipse((X - rr, Y - rr, X + rr, Y + rr), outline=blend(GOLD, 1.0 - u), width=3 * SS)

    def scene(self, key: str, tau: float) -> tuple[Image.Image, dict]:
        """The band layer of panel key at tau seconds into a cycle (the held setup before the release)."""
        layer = Image.new("RGB", (W * SS, BAND_H * SS), BG)
        d = ImageDraw.Draw(layer)
        tv = tau - self.pa
        rt = tv / self.S
        st = state_at(self.runs[key], rt)
        st["tv"], st["rt"] = tv, rt
        self.draw_ramp(d, key)
        self.draw_pin(d, tv)
        if key == "vertical" and st["ball"] == DOWN:
            self.draw_mark(d, st)
        self.draw_dots(d, key, st)
        self.draw_cart(d, key, st["s"])
        self.draw_ball(d, key, st)
        self.draw_splash(d, key, st)
        return layer, st

    def draw_panel(self, key: str, f: int) -> tuple[Image.Image, dict]:
        k, tau = self.phase(f)
        P, F = self.P, self.F
        layer, st = self.scene(key, tau)
        st["alpha"], st["k"] = 1.0, k
        if tau >= P - F:
            # Crossfade to the next cycle's held setup (both carts rest at the pad by now, asserted).
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
        g = self.geo
        for key, st in states.items():
            y0 = BAND_Y[key]
            a, ball = st["alpha"], st["ball"]
            landed = ball == DOWN
            d.text((ROW_X0, y0 + LABEL_DY), label_text(key), font=self.font, fill=COLOUR[key], anchor="lm")
            d.text((ROW_X0, y0 + SUB_DY), cart_text(st["s"]), font=self.font_small, fill=blend(TEXT, a), anchor="lm")
            d.text((ROW_X0, y0 + FIX_DY), air_text(ball, st["t_air"]), font=self.font_small,
                   fill=blend(GOLD if landed else MUTED, a), anchor="lm")
            d.text((ROW_X1, y0 + LABEL_DY), gap_text(st["gap"]), font=self.font, fill=blend(GOLD if landed else TEXT, a), anchor="rm")
            d.text((ROW_X1, y0 + SUB_DY), height_text(st["h"]), font=self.font_small, fill=blend(TEXT, a), anchor="rm")
            d.text((ROW_X1, y0 + FIX_DY), speed_text(st["v"]), font=self.font_small, fill=blend(MUTED, a), anchor="rm")
            if landed and hud_alpha > 0.02:
                d.text((ROW_X1, y0 + EVENT_DY), event_text(ev, key), font=self.font, fill=blend(GOLD, a * hud_alpha), anchor="rm")
            # The trigger label under the plank; the gap label over the dashed line once the top ball is down.
            tx, ty = g.plank_xy(self.d, 0.0, -PLANK_T - 24.0)
            d.text((tx, y0 + ty), trigger_text(), font=self.font_tiny, fill=INK, anchor="mm")
            if key == "vertical" and landed:
                run = self.runs["vertical"]
                mx, my = g.plank_xy(0.5 * (self.d + run["sb_land"] + run["s_land"]), 0.0, g.mark_v + 30.0)
                d.text((mx, y0 + my), mark_text(ev), font=self.font_tiny, fill=blend(GOLD, a), anchor="mm")
        if hud_alpha > 0.02:
            d.text((W / 2, LEGEND_Y), legend_text(man), font=self.font, fill=blend(TEXT, hud_alpha), anchor="mm")
            d.text((W / 2, CLOCK_Y), clock_text(states["vertical"]["rt"]), font=self.font_small,
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
            # The geometry runs on; the legend, clock, event rows and card fade out over the first half of
            # the loop fade and the title fades in over the second half, so the two never overlap.
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
    man = json.loads((ROOT / "projects/cartramp/manifest.json").read_text())
    ev = measure(man)
    if "--measure-only" in sys.argv:
        return
    if "--frames" in sys.argv:
        times = [float(v) for v in sys.argv[sys.argv.index("--frames") + 1].split(",")]
        r = Renderer(man, ev)
        (ROOT / "media/cartramp").mkdir(parents=True, exist_ok=True)
        for tv in times:
            Image.fromarray(r.frame_at(int(round(tv * man["fps"])))).save(ROOT / f"media/cartramp/smoke-{tv}.png")
        print("smoke frames: " + ", ".join(f"{tv}" for tv in times))
        return
    Renderer(man, ev).render(ROOT / "media/cartramp/footage.mp4")


if __name__ == "__main__":
    main()
