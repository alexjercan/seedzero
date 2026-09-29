#!/usr/bin/env python3
"""Ice cube or ball: which climbs higher?

Two panels on the same clock, the same ramp drawn the same way at the same
scale. The ramp is a flat run-in, a circular fillet of radius Rf into a
straight slope at theta = 20 degrees that runs off the frame (no end in
reach). Top, an ice cube of side a slides with no friction. Bottom, a solid
ball of radius r (I = k m r^2, k = 2/5) rolls without slipping on a grippy
ramp. With a = 2 r both centres ride the same offset curve, c = a / 2 = r
above the surface, so the paths are identical and only k differs. Both
centres cross the same start mark on the flat at v0 = 3 m/s, the ball
already rolling (omega = v0 / r). Along the centre path (arc length s)

    (1 + k) s'' = -g sin alpha(s),

alpha the path's slope (0 on the flat, (s - s1) / (Rf - c) on the fillet,
theta on the slope), k = 0 for the cube. Both are integrated by RK4 at
steps_per_second, the top (s' = 0) and the return to the mark are located
by bisection inside the step, and the run is checked against the energy
(1 / 2)(1 + k) v^2 + g y_c and a half-step rerun. The friction the ball
needs, f = m g sin alpha k / (1 + k), is printed against the normal force
N = m (g cos alpha + v^2 kappa) along the whole path (kappa the path
curvature, 1 / (Rf - c) on the fillet). Each object climbs, stops, runs
back down and off the flat; the run repeats every cycle_s seconds of video
(the objects are off the frame at the cycle seam and the peak marks fade
there), the cycle divides the scene length, so the scene is exactly
periodic and the last frame equals the first. Shown at 1/slow speed.
Deterministic, no seed.

Measured and printed: for each panel the rise of the centre of mass (RK4
and the closed form (1 + k) v0^2 / 2 g), the time of the top after the
mark, the foot and the slope start (and the plain-slope closed form), the
path length, the return to the mark, the energy check, the normal force
and (ball) the friction it needs and its spin; the ratio of the rises;
other shapes and a rolling ball on an ice slope (for the description); a
half-step check; the schedule in video time; the on-screen text widths
and the layout clearances.

usage: uphill.py [--measure-only] [--frames t1,t2,...]
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
ICE = (176, 204, 226)
ICE_HI = (228, 240, 250)
ICE_LO = (140, 170, 198)
ICE_INK = (40, 66, 98)
CUBE = (150, 214, 240)
CUBE_FILL = (214, 238, 250)
CUBE_EDGE = (70, 128, 176)
GRIP = (46, 42, 40)
GRIP_TOP = (92, 84, 76)
GRIP_DOT = (70, 64, 60)
BALL_DARK = (140, 52, 48)

# Layout: overlay at y 96..130 (captions.py), two title rows at y 190/252 for
# the first seconds, then the legend at y 236 and the shared clock at y 290;
# two panels stacked, the cube in the band y 330..880 and the ball in y
# 880..1430, both drawn at 2x in one geometry layer; each band has its label
# row 40 px under the band top, its second row at 84 and its third at 120
# (left column from x 40, right column to x 1040); the flat's surface 500 px
# under the band top (y 830 and 1380) and the ramp body down to 548 (y 878
# and 1428); captions at caption_y 0.75 (y 1440..1530); the six-line card
# from y 1572 at a 48 px pitch.
LEGEND_Y, CLOCK_Y = 236, 290
SS = 2
GEOM_Y0, GEOM_Y1 = 330, 1430
PAYOFF_Y, PAYOFF_PITCH = 1572.0, 48
PANELS = ("cube", "ball")
BAND_Y = {"cube": 330, "ball": 880}
LABEL_DY, SUB_DY, FIX_DY, FLOOR_DY, BODY_DY = 40, 84, 120, 500, 548
ROW_X0, ROW_X1 = 40, 1040
COLOUR = {"cube": CUBE, "ball": CORAL}
BODY = {"cube": ICE, "ball": GRIP}
INK = {"cube": ICE_INK, "ball": MUTED}
PEAK_LINE_PX = 230
TICKS_CM = (10, 20, 30, 40, 50, 60, 70)


def blend(col, a: float, base=BG) -> tuple:
    a = max(0.0, min(1.0, a))
    return tuple(int(round(c * a + b * (1 - a))) for c, b in zip(col, base))


# --- the track ------------------------------------------------------------------
class Track:
    """The centre path c above the ramp surface, by its arc length s from the start mark.

    The surface: flat y = 0 up to x_f, a circular fillet of radius Rf (centre (x_f, Rf)) turning up
    to theta, then a straight slope. The centre path is the surface offset by c along the normal:
    flat at y = c up to s1 = x_f, an arc of radius rho = Rf - c up to s2 = s1 + rho theta, a line.
    """

    def __init__(self, man: dict, c: float):
        self.th = math.radians(man["slope_deg"])
        self.Rf = man["fillet_radius_m"]
        self.xf = man["flat_to_foot_m"]
        self.c = c
        self.rho = self.Rf - c
        assert self.rho > 0.0
        self.s1 = self.xf
        self.s2 = self.s1 + self.rho * self.th
        self.x2 = self.xf + self.rho * math.sin(self.th)
        self.y2 = self.Rf - self.rho * math.cos(self.th)

    def sin_alpha(self, s: float) -> float:
        if s <= self.s1:
            return 0.0
        if s < self.s2:
            return math.sin((s - self.s1) / self.rho)
        return math.sin(self.th)

    def point(self, s: float) -> tuple[float, float, float]:
        """(x, y, alpha) of the centre."""
        if s <= self.s1:
            return s, self.c, 0.0
        if s < self.s2:
            ph = (s - self.s1) / self.rho
            return self.xf + self.rho * math.sin(ph), self.Rf - self.rho * math.cos(ph), ph
        d = s - self.s2
        return self.x2 + d * math.cos(self.th), self.y2 + d * math.sin(self.th), self.th

    def y_arr(self, s: np.ndarray) -> np.ndarray:
        ph = np.clip((s - self.s1) / self.rho, 0.0, self.th)
        y = self.Rf - self.rho * np.cos(ph)
        return np.where(s <= self.s1, self.c, np.where(s < self.s2, y, self.y2 + (s - self.s2) * math.sin(self.th)))

    def alpha_arr(self, s: np.ndarray) -> np.ndarray:
        return np.clip((s - self.s1) / self.rho, 0.0, self.th)

    def kappa_arr(self, s: np.ndarray) -> np.ndarray:
        return np.where((s > self.s1) & (s < self.s2), 1.0 / self.rho, 0.0)

    def s_of_rise(self, h: float) -> float:
        """Arc length where the centre has risen h above its level on the flat."""
        y = self.c + h
        if y <= self.y2:
            return self.s1 + self.rho * math.acos((self.Rf - y) / self.rho)
        return self.s2 + (y - self.y2) / math.sin(self.th)

    def contact(self, s: float) -> tuple[float, float, float]:
        """The contact point on the surface under the centre at s, and the slope there."""
        x, y, a = self.point(s)
        return x + self.c * math.sin(a), y - self.c * math.cos(a), a

    def surface_y(self, x: float) -> float:
        if x <= self.xf:
            return 0.0
        xe = self.xf + self.Rf * math.sin(self.th)
        if x < xe:
            return self.Rf - math.sqrt(self.Rf * self.Rf - (x - self.xf) ** 2)
        return self.Rf * (1.0 - math.cos(self.th)) + (x - xe) * math.tan(self.th)


# --- measurement --------------------------------------------------------------
def rk4(tr: Track, k: float, g: float, s: float, v: float, h: float) -> tuple[float, float]:
    def acc(s_: float) -> float:
        return -g * tr.sin_alpha(s_) / (1.0 + k)
    k1s, k1v = v, acc(s)
    k2s, k2v = v + 0.5 * h * k1v, acc(s + 0.5 * h * k1s)
    k3s, k3v = v + 0.5 * h * k2v, acc(s + 0.5 * h * k2s)
    k4s, k4v = v + h * k3v, acc(s + h * k3s)
    return (s + h / 6.0 * (k1s + 2.0 * k2s + 2.0 * k3s + k4s),
            v + h / 6.0 * (k1v + 2.0 * k2v + 2.0 * k3v + k4v))


def bisect(tr: Track, k: float, g: float, s: float, v: float, dt: float, fn) -> tuple[float, float, float]:
    """The sub-step h in (0, dt] where fn(s, v) first turns true, by 60 bisections; returns (h, s, v)."""
    lo, hi = 0.0, dt
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if fn(*rk4(tr, k, g, s, v, mid)):
            hi = mid
        else:
            lo = mid
    sh, vh = rk4(tr, k, g, s, v, hi)
    return hi, sh, vh


def step(tr: Track, k: float, g: float, s: float, v: float, h: float) -> tuple[float, float]:
    """One RK4 step of length h, split at the curvature jumps (the ends of the fillet) so no RK4 stage
    straddles one: the step lands on the jump (found by bisection) and goes on from there."""
    s_new, v_new = rk4(tr, k, g, s, v, h)
    for sk in (tr.s1, tr.s2):
        if (s - sk) * (s_new - sk) < 0.0:
            up = s_new > s
            hk, sh, vh = bisect(tr, k, g, s, v, h, lambda s_, v_, sk=sk, up=up: (s_ >= sk) if up else (s_ <= sk))
            if 0.0 < hk < h:
                return step(tr, k, g, sh, vh, h - hk)
    return s_new, v_new


def simulate(tr: Track, k: float, g: float, v0: float, dt: float, t_max: float) -> dict:
    """RK4 from the start mark (s = 0, s' = v0) up the ramp, over the top and back to the mark."""
    n = int(round(t_max / dt))
    S, V = [0.0], [v0]
    s, v = 0.0, v0
    ev: dict = {"k": k, "dt": dt, "track": tr, "v0": v0}
    marks = {"t_s1": tr.s1, "t_s2": tr.s2}
    for i in range(n):
        s_new, v_new = step(tr, k, g, s, v, dt)
        for key, sm in list(marks.items()):
            if v > 0.0 and s < sm <= s_new:
                h, _, _ = bisect(tr, k, g, s, v, dt, lambda s_, v_, sm=sm: s_ >= sm)
                ev[key] = i * dt + h
                del marks[key]
        if "t_top" not in ev and v_new <= 0.0:
            h, sh, vh = bisect(tr, k, g, s, v, dt, lambda s_, v_: v_ <= 0.0)
            ev["t_top"], ev["s_top"] = i * dt + h, sh
        if "t_top" in ev and s_new <= 0.0:
            h, sh, vh = bisect(tr, k, g, s, v, dt, lambda s_, v_: s_ <= 0.0)
            ev["t_back"], ev["v_back"] = i * dt + h, vh
            break
        s, v = s_new, v_new
        S.append(s)
        V.append(v)
    assert "t_back" in ev, "sim_end_s too short"
    ev["s"], ev["v"] = np.array(S), np.array(V)
    ev["rise"] = tr.point(ev["s_top"])[1] - tr.c
    return ev


def energy(run: dict, g: float) -> np.ndarray:
    tr = run["track"]
    return 0.5 * (1.0 + run["k"]) * run["v"] ** 2 + g * tr.y_arr(run["s"])


def state_at(run: dict, r: float) -> tuple[float, float]:
    """(s, s') of the centre r seconds after the mark; constant speed on the flat before and after."""
    if r <= 0.0:
        return run["v0"] * r, run["v0"]
    if r >= run["t_back"]:
        return run["v_back"] * (r - run["t_back"]), run["v_back"]
    dt = run["dt"]
    i = int(r / dt)
    fr = r / dt - i
    s, v = run["s"], run["v"]
    i1 = min(i + 1, len(s) - 1)
    i = min(i, len(s) - 1)
    return float(s[i] + fr * (s[i1] - s[i])), float(v[i] + fr * (v[i1] - v[i]))


def forces(run: dict, g: float) -> dict:
    """Normal force and the friction the rolling constraint needs, in weights, at every RK4 step."""
    tr, k = run["track"], run["k"]
    s, v = run["s"], run["v"]
    a = tr.alpha_arr(s)
    N = np.cos(a) + v * v * tr.kappa_arr(s) / g
    f = np.sin(a) * k / (1.0 + k)
    return {"s": s, "N": N, "f": f, "ratio": f / N}


def measure(man: dict) -> dict:
    g, v0 = man["g"], man["v0_m_s"]
    th = math.radians(man["slope_deg"])
    a_cube, r_ball, k_ball = man["cube_side_m"], man["ball_radius_m"], man["k_ball"]
    dt = 1.0 / man["steps_per_second"]
    S, P, D, fps, F, ca = man["slow"], man["cycle_s"], man["scene_duration"], man["fps"], man["reset_fade"], man["cross_at"]
    cycles = D / P
    assert abs(cycles - round(cycles)) < 1e-9, "the cycle must divide the scene length"
    for key in ("cycle_s", "cross_at", "first_cycle_at", "reset_fade"):
        assert abs(man[key] * fps - round(man[key] * fps)) < 1e-9, f"{key} must be a whole number of frames"
    ppm = man["px_per_m"]
    tracks = {"cube": Track(man, a_cube / 2.0), "ball": Track(man, r_ball)}
    ks = {"cube": 0.0, "ball": k_ball}
    tr = tracks["ball"]
    print(f"setup: the same ramp in both panels, a flat run-in, a circular fillet of radius {man['fillet_radius_m']:g} m "
          f"starting {man['flat_to_foot_m']:g} m past the start mark and a straight {man['slope_deg']:g} degree slope that "
          f"runs off the frame; top panel an ice cube of side {a_cube * 100:g} cm that slides with no friction (k = 0, its "
          f"centre {a_cube / 2 * 100:g} cm above the surface), bottom panel a solid ball of radius {r_ball * 100:g} cm (I = "
          f"{k_ball:g} m r^2) that rolls without slipping on a grippy ramp (friction coefficient {man['mu_grip']:g}); both "
          f"centres ride the same offset curve (fillet radius {tr.rho:g} m); both cross the start mark at {v0:g} m/s, the "
          f"ball spinning at v0 / r = {v0 / r_ball:.1f} rad/s ({v0 / r_ball / (2 * math.pi):.2f} turns a second); "
          f"(1 + k) s'' = -g sin alpha(s) along the centre path, g = {g:g} m/s^2; RK4 at {man['steps_per_second']} steps "
          f"per second (dt = {dt:.2e} s) with the top and the return located by bisection inside the step; shown at "
          f"1/{S:g} speed on a {P:g} s cycle ({P * fps:.0f} frames) with the mark crossed {ca:g} s into the cycle, "
          f"{cycles:.0f} cycles in {D:g} s; drawn at {ppm:g} px per metre; deterministic, no seed")
    runs = {m: simulate(tracks[m], ks[m], g, v0, dt, man["sim_end_s"]) for m in PANELS}
    ev: dict = {"runs": runs, "tracks": tracks}
    t_foot = man["flat_to_foot_m"] / v0
    for m in PANELS:
        r, trm, k = runs[m], tracks[m], ks[m]
        E = energy(r, g)
        E0 = 0.5 * (1.0 + k) * v0 * v0
        drift = float(np.max(np.abs(E - E[0]))) / E0
        h_closed = (1.0 + k) * v0 * v0 / (2.0 * g)
        t_plain = (1.0 + k) * v0 / (g * math.sin(th))
        path = r["s_top"] - trm.s1
        fc = forces(r, g)
        on_fil = (fc["s"] > trm.s1) & (fc["s"] < trm.s2)
        name = "ice cube" if m == "cube" else "ball"
        line = (f"{m}: RK4: the {name}'s centre rises {r['rise'] * 100:.2f} cm (closed form (1 + k) v0^2 / 2 g = "
                f"{h_closed * 100:.2f} cm, diff {(r['rise'] - h_closed) * 100:+.1e} cm); the top comes {r['t_top']:.4f} s "
                f"after the mark, {r['t_top'] - t_foot:.4f} s after the foot of the fillet ({t_foot:.4f} s after the mark) "
                f"and {r['t_top'] - r['t_s2']:.4f} s after the start of the straight slope (reached at {r['t_s2']:.4f} s); "
                f"on a plain slope with no fillet the top would come {t_plain:.4f} s after the foot, {h_closed / math.sin(th) * 100:.2f} "
                f"cm along the slope; here the centre travels {path * 100:.2f} cm along its path from the foot "
                f"({(r['s_top'] - trm.s2) * 100:.2f} cm of it along the straight slope); back at the mark at "
                f"{r['t_back']:.4f} s at {abs(r['v_back']):.6f} m/s; the energy (1 / 2)(1 + k) v^2 + g y_c drifts by "
                f"{drift:.1e} of the starting kinetic energy over {len(r['s'])} steps; the normal force is "
                f"{fc['N'].min():.3f} to {fc['N'].max():.3f} weights (at least {fc['N'][on_fil].min():.3f} and at most "
                f"{fc['N'][on_fil].max():.3f} on the fillet, {math.cos(th):.3f} on the slope), never zero")
        if m == "ball":
            kk = int(np.argmax(fc["ratio"]))
            line += (f"; to roll without slipping it needs a friction force f = m g sin alpha k / (1 + k) of up to "
                     f"{fc['f'].max():.4f} weights, at most {fc['ratio'][kk]:.4f} of the normal force (on the straight "
                     f"slope, (k / (1 + k)) tan theta = {k / (1 + k) * math.tan(th):.4f}; at most "
                     f"{fc['ratio'][on_fil].max():.4f} on the fillet), under the ramp's {man['mu_grip']:g} everywhere; "
                     f"its spin v / r falls from {v0 / r_ball:.1f} rad/s at the mark to {abs(state_at(r, r['t_top'])[1]) / r_ball:.1f} "
                     f"at the top; at the mark {k / (1 + k):.4f} of its energy (2/7) is spin")
            assert fc["ratio"].max() < man["mu_grip"], "the ball would slip"
            ev["mu_need"] = float(fc["ratio"].max())
        assert fc["N"].min() > 0.0
        print(line)
    rc, rb = runs["cube"], runs["ball"]
    ev["ratio"] = rb["rise"] / rc["rise"]
    print(f"the two panels: the ball's centre rises {rb['rise'] * 100:.2f} cm against the cube's {rc['rise'] * 100:.2f} cm, "
          f"{ev['ratio']:.4f} times as high ((1 + k) = {1 + k_ball:.4f}), {(rb['rise'] - rc['rise']) * 100:.2f} cm higher; "
          f"the ball tops out {rb['t_top']:.4f} s after the mark against {rc['t_top']:.4f} s, and is back at the mark at "
          f"{rb['t_back']:.4f} s against {rc['t_back']:.4f} s; same speed at the mark, but the ball carries an extra 2/5 of "
          f"its motion energy in its spin, and the grip turns that spin into height as it climbs")
    # For the description: other shapes and a rolling ball that meets an ice slope.
    descr = []
    ev["shapes"] = {}
    for name, k in man["description_shapes"]:
        rr = simulate(tracks["ball"], k, g, v0, dt, man["sim_end_s"])
        ev["shapes"][name] = rr["rise"] / rc["rise"]
        descr.append(f"{name} (k = {k:.4f}): rises {rr['rise'] * 100:.2f} cm (closed form "
                     f"{(1 + k) * v0 * v0 / (2 * g) * 100:.2f}), {rr['rise'] / rc['rise']:.4f} times the cube, tops out "
                     f"{rr['t_top']:.4f} s after the mark, needs friction {k / (1 + k) * math.tan(th):.4f} of the normal "
                     f"force")
    ri = simulate(tracks["ball"], 0.0, g, v0, dt, man["sim_end_s"])
    descr.append(f"the same rolling ball meeting an ice slope (no friction from the foot on, no torque about its "
                 f"centre): its centre rises {ri['rise'] * 100:.2f} cm, like the cube, tops out {ri['t_top']:.4f} s "
                 f"after the mark and is still spinning at {v0 / r_ball:.1f} rad/s ({v0 / r_ball / (2 * math.pi):.2f} "
                 f"turns a second) at the top: its 2/7 of spin energy stays in the spin")
    ev["ice_ball_rise"] = ri["rise"]
    print("for the description (same ramp, same 3 m/s at the mark): " + "; ".join(descr))
    half = {m: simulate(tracks[m], ks[m], g, v0, 0.5 * dt, man["sim_end_s"]) for m in PANELS}
    print(f"check at half the time step ({2 * man['steps_per_second']} steps per second): " + "; ".join(
        f"{m} rises {half[m]['rise'] * 100:.6f} cm ({(half[m]['rise'] - runs[m]['rise']) * 100:+.1e}), top at "
        f"{half[m]['t_top']:.6f} s ({half[m]['t_top'] - runs[m]['t_top']:+.1e}), back at {half[m]['t_back']:.6f} s "
        f"({half[m]['t_back'] - runs[m]['t_back']:+.1e})" for m in PANELS))
    # Schedule in video time.
    t0 = man["first_cycle_at"]
    k0 = math.ceil((0.0 - t0) / P - 1e-9) - 1
    k1 = math.floor((D - t0) / P - 1e-9)
    starts = [t0 + k * P for k in range(k0, k1 + 1)]
    ev["cycles"] = int(round(cycles))

    def lst(off_: float) -> str:
        return ", ".join(f"{s + off_:.2f}" for s in starts if 0.0 <= s + off_ < D)

    mx = man["mark_x_px"]
    half_px = {"cube": a_cube / 2.0 * math.sqrt(2.0) * ppm, "ball": r_ball * ppm}
    enter = {m: (-(mx + half_px[m] + 2.0) / ppm) / v0 for m in PANELS}     # real time the object clears the left edge
    leave = {m: runs[m]["t_back"] + (mx + half_px[m] + 2.0) / ppm / abs(runs[m]["v_back"]) for m in PANELS}
    for m in PANELS:
        assert ca + enter[m] * S > 0.0, f"the {m} is on the frame at the cycle start"
        assert ca + leave[m] * S < P - F, f"the {m} is still on the frame at the reset fade"
    tau0 = (0.0 - t0) % P
    r0 = (tau0 - ca) / S
    print(f"schedule (video time, 1/{S:g} speed): cycles of {P:g} s start at " + ", ".join(f"{s:.2f}" for s in starts)
          + f" s (the first {-t0:.2f} s before the first frame); both objects come in from the left edge "
          f"{-enter['cube'] * S:.2f} and {-enter['ball'] * S:.2f} s before they cross the mark, {ca:g} s into each cycle "
          f"at {lst(ca)} s; the cube tops out at {lst(ca + rc['t_top'] * S)} s and the ball at "
          f"{lst(ca + rb['t_top'] * S)} s; the cube is back at the mark at {lst(ca + rc['t_back'] * S)} s and off the "
          f"frame at {lst(ca + leave['cube'] * S)} s, the ball back at the mark at {lst(ca + rb['t_back'] * S)} s and off "
          f"at {lst(ca + leave['ball'] * S)} s; the peak marks fade over the last {F:g} s of each cycle (from "
          f"{lst(P - F)} s); on the first frame the cycle is {tau0:.2f} s in ({r0:.3f} s real after the mark: both "
          f"centres {-r0 * v0 * 100:.1f} cm before the mark); title until {man['title_until']:g} s; payoff card from "
          f"{man['payoff_t']:g} s; the title fades back in over the last {man['loop_fade']:g} s and the last frame "
          f"repeats the first (the scene is periodic: {D:g} s holds exactly {cycles:.0f} cycles)")
    ev["enter"], ev["leave"] = enter, leave
    # Text widths.
    font = os.environ["SEED_ZERO_FONT"]
    f24, f28, f34, f40, f56 = (ImageFont.truetype(font, n) for n in (24, 28, 34, 40, 56))
    widths = {"overlay@34": (f34, man["overlay"])}
    for j, line in enumerate(man["title"].split("|")):
        widths[f"title line {j + 1}@56"] = (f56, line)
    widths["legend@40"] = (f40, legend_text(man))
    widths["clock@28"] = (f28, clock_text(2.6873))
    widths["clock rest@28"] = (f28, clock_text(-1.0))
    for m in PANELS:
        widths[f"label {m}@40"] = (f40, label_text(m))
        widths[f"sublabel {m}@28"] = (f28, sub_text(m))
        widths[f"fixed {m}@28"] = (f28, fixed_text(ev, m))
        widths[f"readout {m}@40"] = (f40, height_text(0.6424))
        widths[f"speed {m}@28"] = (f28, speed_text(3.0))
        widths[f"spin {m}@28"] = (f28, spin_text(m, 9.55))
        widths[f"peak {m}@40"] = (f40, peak_text(runs[m]["rise"]))
    widths["cross mark@28"] = (f28, cross_text(rc["rise"]))
    widths["mark@24"] = (f24, mark_text(man))
    for j, line in enumerate(payoff_lines(man, ev)):
        widths[f"payoff line {j + 1}@40"] = (f40, line)
    print("text widths: " + ", ".join(f"{k} {f.getlength(s):.0f} px" for k, (f, s) in widths.items()))
    assert all(f.getlength(s) < 950 for f, s in widths.values()), "a text line is wider than 950 px"
    # Layout checks: the columns against the ramp and the objects, the peak labels against the ramp.
    left = ROW_X0 + max(max(f40.getlength(label_text(m)), f28.getlength(sub_text(m)), f28.getlength(fixed_text(ev, m)))
                        for m in PANELS)
    right = ROW_X1 - max(max(f40.getlength(height_text(0.6424)), f28.getlength(speed_text(3.0)),
                             f28.getlength(spin_text(m, 9.55))) for m in PANELS)
    rows_bottom = FIX_DY + 16
    top_obj = FLOOR_DY - (rb["rise"] + 2.0 * r_ball) * ppm                  # the ball's top edge at its peak
    right_ramp = FLOOR_DY - tr.surface_y((ROW_X1 - mx) / ppm) * ppm          # the ramp surface under the right column
    print(f"row check: the left column ends at x {left:.0f} px, the right column starts at x {right:.0f} px; both end "
          f"{rows_bottom} px under the band top; the ramp surface at x {ROW_X1} px is {right_ramp:.0f} px under the band "
          f"top and the ball's top edge at its peak {top_obj:.0f} px")
    assert right_ramp - rows_bottom > 40 and top_obj - rows_bottom > 40, "the right column meets the ramp or the ball"
    def surf(trm: Track, x_px: float) -> float:
        return FLOOR_DY - trm.surface_y((x_px - mx) / ppm) * ppm

    clear = []
    rc_top = tracks["ball"].point(tracks["ball"].s_of_rise(rc["rise"]))
    marks = [("cube peak", tracks["cube"], tracks["cube"].point(rc["s_top"]), half_px["cube"] + 8.0, f40,
              peak_text(rc["rise"])),
             ("ball peak", tracks["ball"], tracks["ball"].point(rb["s_top"]), half_px["ball"] + 8.0, f40,
              peak_text(rb["rise"])),
             ("cube level in the ball panel", tracks["ball"], rc_top, 30.0, f28, cross_text(rc["rise"]))]
    for name, trm, (xc, yc, _), off, fnt, txt in marks:
        lx1 = mx + xc * ppm - off
        lx0 = lx1 - PEAK_LINE_PX
        ly = FLOOR_DY - yc * ppm
        tx1 = lx0 - 12.0
        tx0 = tx1 - fnt.getlength(txt)
        line_gap = surf(trm, lx1) - ly
        label_gap = surf(trm, tx1) - (ly + 20.0)
        clear.append(f"{name} line from x {lx0:.0f} to {lx1:.0f} px at {ly:.0f} px under the band top ({line_gap:.0f} px "
                     f"above the ramp at its right end), label x {tx0:.0f} to {tx1:.0f} px ({label_gap:.0f} px above the ramp)")
        assert tx0 > 20 and (tx0 > left + 10 or ly - 20 > rows_bottom + 20), "a peak label meets the left column"
        assert line_gap > 10.0 and label_gap > 10.0, "a peak label or line meets the ramp"
    print("peak marks: " + "; ".join(clear))
    return ev


def legend_text(man: dict) -> str:
    return f"same speed, same slope, 1/{man['slow']:g} speed"


def clock_text(r: float) -> str:
    return "before the start mark" if r < 0.0 else f"{r:.3f} s after the start mark"


def label_text(m: str) -> str:
    return "ice cube" if m == "cube" else "ball"


def sub_text(m: str) -> str:
    return "slides on ice, no friction" if m == "cube" else "rolls on a grippy ramp"


def fixed_text(ev: dict, m: str) -> str:
    return f"top {ev['runs'][m]['t_top']:.2f} s after the mark"


def height_text(h: float) -> str:
    return f"height {max(0.0, h) * 100:.0f} cm"


def speed_text(v: float) -> str:
    return f"speed {abs(v):.2f} m/s"


def spin_text(m: str, turns: float) -> str:
    return "no spin" if m == "cube" else f"spin {abs(turns):.1f} turns/s"


def peak_text(h: float) -> str:
    return f"{h * 100:.0f} cm"


def cross_text(h: float) -> str:
    return f"ice cube {h * 100:.0f} cm"


def mark_text(man: dict) -> str:
    return f"{man['v0_m_s']:g} m/s"


def payoff_lines(man: dict, ev: dict) -> list[str]:
    rc, rb = ev["runs"]["cube"], ev["runs"]["ball"]
    sh = ev["shapes"]
    text = man["payoff_text"].format(
        h_ball=rb["rise"] * 100, h_cube=rc["rise"] * 100, ratio=ev["ratio"], t_ball=rb["t_top"], t_cube=rc["t_top"],
        mu_need=ev["mu_need"], r_cyl=sh["solid cylinder"], r_hollow=sh["hollow ball"], r_hoop=sh["hoop"])
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
        self.mx = float(man["mark_x_px"])
        self.S = man["slow"]
        self.P = man["cycle_s"]
        self.P_f = int(round(man["cycle_s"] * self.fps))
        self.c0_f = int(round(man["first_cycle_at"] * self.fps))
        self.ca, self.F = man["cross_at"], man["reset_fade"]
        self.runs, self.tracks = ev["runs"], ev["tracks"]
        self.r_ball = man["ball_radius_m"]
        self.a_cube = man["cube_side_m"]
        self.surface = {m: self.surface_px(m) for m in PANELS}

    def phase(self, f: int) -> tuple[int, float]:
        k, tau_f = divmod(f - self.c0_f, self.P_f)
        return k, tau_f / self.fps

    def scr(self, m: str, x_m: float, y_m: float) -> tuple[float, float]:
        return self.mx + x_m * self.ppm, BAND_Y[m] + FLOOR_DY - y_m * self.ppm

    @staticmethod
    def Lp(x: float, y: float) -> tuple[float, float]:
        """Layer (2x) pixel of a screen point, rounded to 1e-4 px so equal states draw equal pixels."""
        return round(x * SS, 4), round((y - GEOM_Y0) * SS, 4)

    def surface_px(self, m: str) -> list[tuple[float, float]]:
        tr = self.tracks[m]
        pts = [self.scr(m, (-12.0 - self.mx) / self.ppm, 0.0), self.scr(m, tr.xf, 0.0)]
        for j in range(1, 41):
            ph = tr.th * j / 40
            pts.append(self.scr(m, tr.xf + tr.Rf * math.sin(ph), tr.Rf * (1.0 - math.cos(ph))))
        x_end = (W + 12.0 - self.mx) / self.ppm
        pts.append(self.scr(m, x_end, tr.surface_y(x_end)))
        return pts

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

    def tick(self, d: ImageDraw.ImageDraw, m: str, s: float, depth: float, col, width: int) -> tuple:
        """A tick into the ramp body, normal to the surface at the contact point under the centre at s."""
        cx, cy, a = self.tracks[m].contact(s)
        px, py = self.scr(m, cx, cy)
        nx, ny = math.sin(a), math.cos(a)            # into the body, screen coordinates (y down)
        d.line((*self.Lp(px, py), *self.Lp(px + nx * depth, py + ny * depth)), fill=col, width=width)
        return px, py, nx, ny

    def draw_ramp(self, d: ImageDraw.ImageDraw, m: str) -> None:
        pts = self.surface[m]
        yb = BAND_Y[m] + BODY_DY
        poly = [self.Lp(x, y) for x, y in pts] + [self.Lp(W + 12.0, yb), self.Lp(-12.0, yb)]
        d.polygon(poly, fill=BODY[m])
        line = [self.Lp(x, y) for x, y in pts]
        if m == "cube":
            # Ice: a bright top edge, a darker foot and a few highlights along the slope.
            lower = [self.Lp(-12.0, yb - 5), self.Lp(W + 12.0, yb - 5), self.Lp(W + 12.0, yb), self.Lp(-12.0, yb)]
            d.polygon(lower, fill=ICE_LO)
            d.line(line, fill=ICE_HI, width=3 * SS)
            tr = self.tracks[m]
            for xm in (0.05, 0.55, 0.95, 1.35, 1.75, 2.15):
                ys = tr.surface_y(xm)
                x0, y0 = self.scr(m, xm, ys)
                dx = 46.0
                d.line((*self.Lp(x0, y0 + 16), *self.Lp(x0 + dx, y0 + 16 - dx * math.tan(tr.th) * (xm > 0.4))),
                       fill=ICE_HI, width=2 * SS)
        else:
            # Grip: a rough top band and a fixed speckle (no randomness: a fixed integer pattern).
            d.line(line, fill=GRIP_TOP, width=6 * SS)
            tr = self.tracks[m]
            for j in range(0, 150):
                xm = -0.3 + j * 0.0187
                depth = 10.0 + ((j * 37) % 11) * 2.6
                ys = tr.surface_y(xm)
                x0, y0 = self.scr(m, xm, ys)
                y0 += depth
                if y0 < yb - 4 and -4 < x0 < W + 4:
                    r = 1.6 * SS
                    p = self.Lp(x0, y0)
                    d.ellipse((p[0] - r, p[1] - r, p[0] + r, p[1] + r), fill=GRIP_DOT)
        # Height ticks every 10 cm of the centre's rise.
        tr = self.tracks[m]
        for h in TICKS_CM:
            s = tr.s_of_rise(h / 100.0)
            px, py, nx, ny = self.tick(d, m, s, 14.0, INK[m], 2 * SS)
        # The start mark: a gold notch in the flat.
        ys = BAND_Y[m] + FLOOR_DY
        p0, p1, p2 = self.Lp(self.mx, ys + 3), self.Lp(self.mx - 9, ys + 18), self.Lp(self.mx + 9, ys + 18)
        d.polygon([p0, p1, p2], fill=GOLD)

    def draw_cube(self, d: ImageDraw.ImageDraw, m: str, s: float) -> None:
        tr = self.tracks[m]
        x, y, a = tr.point(s)
        cx, cy = self.scr(m, x, y)
        h = self.a_cube / 2.0 * self.ppm
        ca, sa = math.cos(a), math.sin(a)

        def rot(u: float, v: float) -> tuple[float, float]:
            # u along the slope, v up from the surface; screen y down.
            return self.Lp(cx + u * ca - v * sa, cy - (u * sa + v * ca))

        body = [rot(-h, -h), rot(h, -h), rot(h, h), rot(-h, h)]
        d.polygon(body, fill=CUBE_FILL, outline=CUBE_EDGE, width=2 * SS)
        inner = [rot(-h + 6, h - 6), rot(h - 14, h - 6), rot(-h + 6, -h + 14)]
        d.polygon(inner, fill=(236, 248, 253))
        d.line((*rot(-h + 5, -h + 5), *rot(h - 5, -h + 5)), fill=(176, 214, 236), width=2 * SS)

    def draw_ball(self, d: ImageDraw.ImageDraw, m: str, s: float) -> None:
        tr = self.tracks[m]
        x, y, a = tr.point(s)
        cx, cy = self.scr(m, x, y)
        X, Y = self.Lp(cx, cy)
        R = self.r_ball * self.ppm * SS
        d.ellipse((X - R, Y - R, X + R, Y + R), fill=CORAL, outline=BALL_DARK, width=2 * SS)
        phi = s / self.r_ball            # rolled angle, clockwise on screen while it moves right
        c, sn = math.cos(phi), math.sin(phi)
        d.line((X - R * 0.84 * c, Y - R * 0.84 * sn, X + R * 0.84 * c, Y + R * 0.84 * sn), fill=WHITE, width=5 * SS)
        dr = 3.6 * SS
        px, py = X + R * 0.62 * sn, Y - R * 0.62 * c
        d.ellipse((px - dr, py - dr, px + dr, py + dr), fill=WHITE)

    def draw_panel(self, d: ImageDraw.ImageDraw, m: str, f: int) -> dict:
        self.draw_ramp(d, m)
        k, tau = self.phase(f)
        r = (tau - self.ca) / self.S
        run = self.runs[m]
        s, v = state_at(run, r)
        tr = self.tracks[m]
        mark_a = 1.0 if tau < self.P - self.F else max(0.0, (self.P - tau) / self.F)
        peaked = r >= run["t_top"]
        base = BG
        # The cube's top carried across to the ball's panel.
        if m == "ball" and r >= self.runs["cube"]["t_top"]:
            rc = self.runs["cube"]
            xc, yc, _ = self.tracks["cube"].point(rc["s_top"])
            s_b = tr.s_of_rise(rc["rise"])
            xb, yb_, _ = tr.point(s_b)
            px1, py = self.scr(m, xb, yb_)
            self.dashed(d, self.Lp(px1 - 30 - PEAK_LINE_PX, py), self.Lp(px1 - 30, py), blend(CUBE, 0.75 * mark_a),
                        12 * SS, 8 * SS, 2 * SS)
        if peaked:
            xc, yc, _ = tr.point(run["s_top"])
            px, py = self.scr(m, xc, yc)
            half = (self.a_cube / 2.0 * math.sqrt(2.0) if m == "cube" else self.r_ball) * self.ppm
            x1 = px - half - 8.0
            self.dashed(d, self.Lp(x1 - PEAK_LINE_PX, py), self.Lp(x1, py), blend(GOLD, mark_a), 14 * SS, 8 * SS, 3 * SS)
            self.tick(d, m, run["s_top"], 22.0, blend(GOLD, mark_a, BODY[m]), 4 * SS)
        if m == "cube":
            self.draw_cube(d, m, s)
        else:
            self.draw_ball(d, m, s)
        x, y, _ = tr.point(s)
        return {"k": k, "tau": tau, "r": r, "s": s, "v": v, "rise": y - tr.c, "peaked": peaked, "mark_a": mark_a}

    def draw_text(self, d: ImageDraw.ImageDraw, states: dict, hud_alpha: float) -> None:
        man, ev = self.man, self.ev
        for m, st in states.items():
            y0 = BAND_Y[m]
            run, tr = self.runs[m], self.tracks[m]
            d.text((ROW_X0, y0 + LABEL_DY), label_text(m), font=self.font, fill=COLOUR[m], anchor="lm")
            d.text((ROW_X0, y0 + SUB_DY), sub_text(m), font=self.font_small, fill=MUTED, anchor="lm")
            if hud_alpha > 0.02:
                d.text((ROW_X0, y0 + FIX_DY), fixed_text(ev, m), font=self.font_small,
                       fill=blend(GOLD, 0.85 * hud_alpha), anchor="lm")
            at_top = st["peaked"] and st["rise"] > run["rise"] - 0.005
            d.text((ROW_X1, y0 + LABEL_DY), height_text(st["rise"]), font=self.font,
                   fill=GOLD if at_top else TEXT, anchor="rm")
            d.text((ROW_X1, y0 + SUB_DY), speed_text(st["v"]), font=self.font_small, fill=MUTED, anchor="rm")
            turns = st["v"] / self.r_ball / (2.0 * math.pi)
            d.text((ROW_X1, y0 + FIX_DY), spin_text(m, turns), font=self.font_small,
                   fill=CORAL if m == "ball" else MUTED, anchor="rm")
            ys = y0 + FLOOR_DY
            d.text((self.mx, ys + 33), mark_text(man), font=self.font_tiny, fill=INK[m], anchor="mm")
            for h in TICKS_CM:
                cx, cy, a = tr.contact(tr.s_of_rise(h / 100.0))
                px, py = self.scr(m, cx, cy)
                d.text((px + math.sin(a) * 30.0, py + math.cos(a) * 30.0), f"{h}", font=self.font_tiny, fill=INK[m],
                       anchor="mm")
            if st["peaked"] and st["mark_a"] > 0.0:
                xc, yc, _ = tr.point(run["s_top"])
                px, py = self.scr(m, xc, yc)
                half = (self.a_cube / 2.0 * math.sqrt(2.0) if m == "cube" else self.r_ball) * self.ppm
                x0 = px - half - 8.0 - PEAK_LINE_PX - 12.0
                d.text((x0, py), peak_text(run["rise"]), font=self.font, fill=blend(GOLD, st["mark_a"]), anchor="rm")
            if m == "ball" and st["r"] >= self.runs["cube"]["t_top"] and st["mark_a"] > 0.0:
                rc = self.runs["cube"]
                xb, yb_, _ = tr.point(tr.s_of_rise(rc["rise"]))
                px1, py = self.scr(m, xb, yb_)
                d.text((px1 - 30 - PEAK_LINE_PX - 12.0, py), cross_text(rc["rise"]), font=self.font_small,
                       fill=blend(CUBE, 0.85 * st["mark_a"]), anchor="rm")
        if hud_alpha > 0.02:
            d.text((W / 2, LEGEND_Y), legend_text(man), font=self.font, fill=blend(TEXT, hud_alpha), anchor="mm")
            r_clock = min(states["ball"]["r"], self.runs["ball"]["t_back"])
            d.text((W / 2, CLOCK_Y), clock_text(r_clock), font=self.font_small, fill=blend(MUTED, hud_alpha), anchor="mm")

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
        wrap = self.live_frame(total, title_alpha=1.0, hud_alpha=0.0)
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
    man = json.loads((ROOT / "projects/uphill/manifest.json").read_text())
    ev = measure(man)
    if "--measure-only" in sys.argv:
        return
    if "--frames" in sys.argv:
        times = [float(v) for v in sys.argv[sys.argv.index("--frames") + 1].split(",")]
        r = Renderer(man, ev)
        (ROOT / "media/uphill").mkdir(parents=True, exist_ok=True)
        for tv in times:
            Image.fromarray(r.frame_at(int(round(tv * man["fps"])))).save(ROOT / f"media/uphill/smoke-{tv}.png")
        print("smoke frames: " + ", ".join(f"{tv}" for tv in times))
        return
    Renderer(man, ev).render(ROOT / "media/uphill/footage.mp4")


if __name__ == "__main__":
    main()
