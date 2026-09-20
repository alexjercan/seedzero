#!/usr/bin/env python3
"""Loop the loop: start level with the top of the loop. Does the puck make it round?

A frictionless puck slides on one track: a straight ramp at 45 degrees
into a 1.2 m dip arc, then a vertical loop of radius R = 1 m, then a flat
exit. Two panels, the same track, two release heights: the top puck is
released from rest level with the top of the loop (h = 2R), the bottom
puck from h = 2.5R. The puck is a point constrained to the track: RK4 on
(s, v) with s'' = -g dy/ds along the arc length, the speed for the track
force taken from energy (v^2 = 2 g (h - y)) so the normal force

    N = m (v^2 kappa + g n_y)

(kappa the curvature toward the puck's side of the track, n the unit
normal on that side) is exact in s. The puck leaves where N < 0 (found by
bisection on s), then flies as a projectile (closed form) until it meets
the loop again; the run ends at the landing. Played at one third speed,
four runs of 10 s with a short crossfade reset. Deterministic, no seed.

Measured and printed: the closed forms sin theta = 2 (h/R - 1) / 3 and
the 2.5R threshold; for each panel the bottom speed, the departure (time,
angle above the centre, angle short of the top, height, speed, the
minimum track force) or the top crossing (time, speed, N at the top),
the landing point and time, the exit time, an energy check; the 2.25R,
2.49R, 2.51R and rolling-ball checks; the run schedule in video time; the
on-screen text widths.

usage: looptrack.py [--measure-only] [--frames t1,t2,...]
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
WIRE = (104, 116, 132)
WHITE = (236, 240, 244)

# Layout: overlay at y 96 (captions.py), title rows at y 190/252/314 for
# the first seconds, two panels of 543 px from y 350 (top: level with the
# top, bottom: 2.5R), the loop centred at x 660, captions at caption_y
# 0.75 (y 1440..1520), payoff card under them from y 1592. Loop centre at
# x 660 so the marks right-aligned at x 1040 clear the loop's top.
GEOM_Y0, GEOM_Y1 = 350, 1436
PANEL_H = (GEOM_Y1 - GEOM_Y0) // 2
LOOP_CX = 660.0
BASE_PAD = 18  # loop bottom above the panel's lower edge
PANELS = {"top": {"index": 0, "colour": TEAL}, "bottom": {"index": 1, "colour": CORAL}}
SS = 2
PAYOFF_Y = 1592.0
PUCK_R = 14.0


def blend(col, a, base=BG):
    return tuple(int(round(c * a + b * (1 - a))) for c, b in zip(col, base))


def smoothstep(u: float) -> float:
    u = max(0.0, min(1.0, u))
    return u * u * (3 - 2 * u)


class Track:
    """Ramp, dip arc, loop, flat exit; x right, y up, loop bottom at (0, 0)."""

    def __init__(self, R: float, alpha_deg: float, r_d: float, h_top: float, exit_len: float):
        self.R, self.r_d, self.h_top = R, r_d, h_top
        self.alpha = math.radians(alpha_deg)
        sa, ca = math.sin(self.alpha), math.cos(self.alpha)
        self.dip_start = (-r_d * sa, r_d * (1.0 - ca))
        self.L_ramp = (h_top - self.dip_start[1]) / sa
        self.ramp_top = (self.dip_start[0] - self.L_ramp * ca, h_top)
        self.s_ramp = self.L_ramp
        self.s_dip = self.s_ramp + r_d * self.alpha
        self.s_loop = self.s_dip + 2.0 * math.pi * R
        self.s_top = self.s_dip + math.pi * R
        self.s_end = self.s_loop + exit_len
        self.loop_c = (0.0, R)

    def s_at_height(self, h: float) -> float:
        """Arc length of the point on the ramp at height h."""
        return (self.h_top - h) / math.sin(self.alpha)

    def point(self, s: float):
        """(x, y, tx, ty, nx, ny, kappa) at arc length s."""
        sa, ca = math.sin(self.alpha), math.cos(self.alpha)
        if s < self.s_ramp:
            x = self.ramp_top[0] + s * ca
            y = self.ramp_top[1] - s * sa
            return x, y, ca, -sa, sa, ca, 0.0
        if s < self.s_dip:
            b = (s - self.s_ramp) / self.r_d - self.alpha
            x = self.r_d * math.sin(b)
            y = self.r_d * (1.0 - math.cos(b))
            return x, y, math.cos(b), math.sin(b), -math.sin(b), math.cos(b), 1.0 / self.r_d
        if s < self.s_loop:
            phi = (s - self.s_dip) / self.R
            x = self.R * math.sin(phi)
            y = self.R * (1.0 - math.cos(phi))
            return x, y, math.cos(phi), math.sin(phi), -math.sin(phi), math.cos(phi), 1.0 / self.R
        return s - self.s_loop, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0

    def loop_phi(self, s: float) -> float:
        return (s - self.s_dip) / self.R


def n_over_mg(track: Track, g: float, h: float, k: float, s: float) -> float:
    """Track force in units of the weight at arc length s, speed from energy."""
    _, y, _, _, _, ny, kappa = track.point(s)
    v2 = 2.0 * g * (h - y) / (1.0 + k)
    return v2 * kappa / g + ny


def simulate(track: Track, g: float, h: float, k: float, steps: int, tol: float, t_max: float = 6.0) -> dict:
    """Slide from rest at height h on the ramp. Returns per-step arrays and events."""
    dt = 1.0 / steps
    s, v = track.s_at_height(h), 0.0
    ts, ss, vs, ns = [0.0], [s], [v], [n_over_mg(track, g, h, k, s)]
    out = {"h": h, "k": k, "dt": dt, "depart": None, "top": None, "entry": None, "loop_exit": None,
           "gone": None, "drift": 0.0}
    e0 = g * h

    def acc(x: float) -> float:
        return -g * track.point(min(x, track.s_end))[3] / (1.0 + k)

    n = int(round(t_max * steps))
    for i in range(n):
        t = i * dt
        k1v, k1s = acc(s), v
        k2v, k2s = acc(s + 0.5 * dt * k1s), v + 0.5 * dt * k1v
        k3v, k3s = acc(s + 0.5 * dt * k2s), v + 0.5 * dt * k2v
        k4v, k4s = acc(s + dt * k3s), v + dt * k3v
        s_new = s + dt / 6.0 * (k1s + 2 * k2s + 2 * k3s + k4s)
        v_new = v + dt / 6.0 * (k1v + 2 * k2v + 2 * k3v + k4v)
        t_new = t + dt
        for name, s_mark in (("entry", track.s_dip), ("top", track.s_top), ("loop_exit", track.s_loop), ("gone", track.s_end)):
            if out[name] is None and s < s_mark <= s_new:
                f = (s_mark - s) / (s_new - s)
                out[name] = {"t": t + f * dt, "v": v + f * (v_new - v)}
        if s_new >= track.s_end:
            ts.append(t_new); ss.append(track.s_end); vs.append(v_new); ns.append(1.0)
            break
        nm = n_over_mg(track, g, h, k, s_new)
        y_new = track.point(s_new)[1]
        e = 0.5 * (1.0 + k) * v_new * v_new + g * y_new
        out["drift"] = max(out["drift"], abs(e - e0) / e0)
        if nm < -tol:
            lo, hi = s, s_new  # N(lo) >= -tol > N(hi)
            for _ in range(80):
                mid = 0.5 * (lo + hi)
                if n_over_mg(track, g, h, k, mid) >= 0.0:
                    lo = mid
                else:
                    hi = mid
            s_star = 0.5 * (lo + hi)
            f = (s_star - s) / (s_new - s)
            t_star = t + f * dt
            x, y, tx, ty, nx, ny, _ = track.point(s_star)
            v_star = math.sqrt(max(0.0, 2.0 * g * (h - y) / (1.0 + k)))
            out["depart"] = {"t": t_star, "s": s_star, "x": x, "y": y, "v": v_star, "vx": v_star * tx, "vy": v_star * ty,
                             "nx": nx, "ny": ny, "phi": track.loop_phi(s_star), "v_rk4": v + f * (v_new - v)}
            ts.append(t_star); ss.append(s_star); vs.append(v_star); ns.append(0.0)
            break
        s, v = s_new, v_new
        ts.append(t_new); ss.append(s); vs.append(v); ns.append(nm)
    out["t"], out["s"], out["v"], out["n"] = (np.array(a) for a in (ts, ss, vs, ns))
    if out["depart"] is not None:
        out["flight"] = flight(track, g, out["depart"])
    return out


def flight(track: Track, g: float, dep: dict) -> dict:
    """Closed-form projectile from the departure point to the loop wall."""
    cx, cy = track.loop_c
    R = track.R

    def pos(t: float) -> tuple[float, float]:
        return dep["x"] + dep["vx"] * t, dep["y"] + dep["vy"] * t - 0.5 * g * t * t

    def outside(t: float) -> float:
        x, y = pos(t)
        return math.hypot(x - cx, y - cy) - R

    t_lo, t_hi = 2e-3, None
    t = t_lo
    while t < 5.0:
        if outside(t) > 0.0:
            t_hi = t
            break
        t_lo = t
        t += 1e-4
    if t_hi is None:
        raise RuntimeError("no landing found")
    for _ in range(80):
        mid = 0.5 * (t_lo + t_hi)
        if outside(mid) > 0.0:
            t_hi = mid
        else:
            t_lo = mid
    tl = 0.5 * (t_lo + t_hi)
    x, y = pos(tl)
    vx, vy = dep["vx"], dep["vy"] - g * tl
    phi = math.atan2(x - cx, -(y - cy)) % (2.0 * math.pi)  # from the bottom, counter-clockwise
    tang = (math.cos(phi), math.sin(phi))
    normal = (-math.sin(phi), math.cos(phi))
    t_peak = dep["vy"] / g
    xp, yp = pos(t_peak)
    return {"dt": tl, "x": x, "y": y, "phi": phi, "speed": math.hypot(vx, vy),
            "v_tan": vx * tang[0] + vy * tang[1], "v_norm": vx * normal[0] + vy * normal[1],
            "t_peak": t_peak, "x_peak": xp, "y_peak": yp, "pos": pos, "nx": normal[0], "ny": normal[1]}


def closed_form_theta(h_over_R: float, k: float = 0.0) -> float | None:
    """Departure angle above the centre, degrees, for release height h (no departure -> None)."""
    sin_th = 2.0 * (h_over_R - 1.0) / (3.0 + k)
    return None if sin_th >= 1.0 else math.degrees(math.asin(sin_th))


def measure(man: dict) -> dict:
    g, R = man["g"], man["loop_radius_m"]
    fps, steps, slow = man["fps"], man["steps_per_second"], man["slow_factor"]
    tol = man["leave_tol_mg"]
    track = Track(R, man["ramp_angle_deg"], man["dip_radius_m"], man["ramp_top_m"], man["exit_length_m"])
    print(f"setup: a frictionless point puck on one track: a straight ramp at {man['ramp_angle_deg']:g} degrees "
          f"from ({track.ramp_top[0]:.4f}, {track.ramp_top[1]:.2f}) m into a dip arc of radius {man['dip_radius_m']:g} m "
          f"(tangent point ({track.dip_start[0]:.4f}, {track.dip_start[1]:.4f}) m), then a vertical loop of radius "
          f"R = {R:g} m (bottom at (0, 0), top at (0, {2 * R:g})), then a flat exit of {man['exit_length_m']:g} m; "
          f"g = {g:g} m/s^2; ramp {track.L_ramp:.4f} m, dip {track.s_dip - track.s_ramp:.4f} m, loop {2 * math.pi * R:.4f} m; "
          f"two panels, the same track, released from rest at h = {man['release_heights_R']['top']:g} R (top panel, level "
          f"with the top of the loop) and h = {man['release_heights_R']['bottom']:g} R (bottom panel); RK4 on (s, v) at "
          f"{steps} steps per second (dt = {1 / steps:.2e} s), track force N = m (v^2 kappa + g n_y) with v from energy, "
          f"departure where N < -{tol:g} m g (bisection on s), then a closed-form projectile to the loop wall; played at "
          f"1/{slow} speed; deterministic, no seed")
    print(f"closed forms: the puck leaves where sin theta = 2 (h/R - 1) / 3 (theta above the loop centre): "
          f"h = 2 R -> theta = {closed_form_theta(2.0):.2f} degrees ({180 - 90 - closed_form_theta(2.0):.2f} short of the top, "
          f"height {R * (1 + 2 / 3):.4f} m = {1 + 2 / 3:.4f} R); h = 2.25 R -> {closed_form_theta(2.25):.2f} degrees; "
          f"h = 2.49 R -> {closed_form_theta(2.49):.2f} degrees; threshold h = 2.5 R (sin theta = 1, N = 0 exactly at the top); "
          f"speed at the top from 2.5 R sqrt(g R) = {math.sqrt(g * R):.4f} m/s; bottom speeds sqrt(2 g h): "
          f"{math.sqrt(2 * g * 2 * R):.4f} m/s from 2 R, {math.sqrt(2 * g * 2.5 * R):.4f} m/s from 2.5 R; track force at the "
          f"bottom of the loop (2 h / R + 1) m g: {2 * 2 + 1:g} weights from 2 R, {2 * 2.5 + 1:g} weights from 2.5 R; "
          f"rolling solid ball (k = {man['rolling_k']:g}, v^2 = 2 g (h - y) / (1 + k)): needs h = 2 R + 0.7 R = 2.7 R, "
          f"from 2 R it leaves at sin theta = 10 (h/R - 1) / 17 -> {closed_form_theta(2.0, man['rolling_k']):.2f} degrees")
    runs = {}
    for name, hR in man["release_heights_R"].items():
        run = simulate(track, g, hR * R, 0.0, steps, tol)
        run["hR"] = hR
        runs[name] = run
        head = (f"{name} panel, released from rest at h = {hR:g} R = {hR * R:g} m (ramp point ({track.point(run['s'][0])[0]:.4f}, "
                f"{hR * R:g}) m, s = {run['s'][0]:.4f} m): reaches the loop bottom at {run['entry']['t']:.4f} s at "
                f"{run['entry']['v']:.4f} m/s (closed form {math.sqrt(2 * g * hR * R):.4f}), track force there "
                f"{n_over_mg(track, g, hR * R, 0.0, track.s_dip + 1e-12):.4f} weights")
        dep = run["depart"]
        if dep is not None:
            fl = run["flight"]
            theta = math.degrees(dep["phi"]) - 90.0
            print(head + f"; LEAVES the track at {dep['t']:.4f} s ({dep['t'] - run['entry']['t']:.4f} s after entering the loop): "
                  f"{math.degrees(dep['phi']):.3f} degrees round from the bottom = {theta:.3f} degrees above the centre = "
                  f"{180 - math.degrees(dep['phi']):.3f} degrees short of the top (closed form {closed_form_theta(hR):.3f} above "
                  f"the centre, {90 - closed_form_theta(hR):.3f} short); height {dep['y']:.4f} m = {dep['y'] / R:.4f} R at "
                  f"x = {dep['x']:.4f} m; speed {dep['v']:.4f} m/s (RK4 speed {dep['v_rk4']:.4f}), velocity ({dep['vx']:.4f}, "
                  f"{dep['vy']:.4f}) m/s, {math.degrees(math.atan2(dep['vy'], -dep['vx'])):.1f} degrees above horizontal "
                  f"heading left; track force at departure {n_over_mg(track, g, hR * R, 0.0, dep['s']):.2e} weights, minimum "
                  f"before it {run['n'][:-1].min():.6f}; flight: peak {fl['y_peak']:.4f} m at x = {fl['x_peak']:.4f} m after "
                  f"{fl['t_peak']:.4f} s, meets the loop wall after {fl['dt']:.4f} s of flight at ({fl['x']:.4f}, {fl['y']:.4f}) m, "
                  f"{math.degrees(fl['phi']):.2f} degrees round from the bottom ({360 - math.degrees(fl['phi']):.2f} degrees up "
                  f"the left side), at {dep['t'] + fl['dt']:.4f} s after release, speed {fl['speed']:.4f} m/s ({fl['v_tan']:.4f} "
                  f"along the track, {fl['v_norm']:.4f} into it); the run ends at the landing (the impact is not modelled); "
                  f"energy drift before departure {run['drift']:.1e}")
        else:
            top = run["top"]
            n_top = 2.0 * (hR - 2.0) - 1.0 + 0.0  # (v^2 / R - g) / g with v^2 = 2 g (h - 2R)
            i_loop = (run["s"] > track.s_dip) & (run["s"] < track.s_loop)
            n_min_i = int(np.argmin(np.where(i_loop, run["n"], np.inf)))
            print(head + f"; passes the top at {top['t']:.4f} s ({top['t'] - run['entry']['t']:.4f} s after entering the loop) "
                  f"at {top['v']:.4f} m/s (closed form sqrt(g R) = {math.sqrt(g * R):.4f}); track force at the top "
                  f"{n_top:.6f} weights (closed form 2 (h/R - 2) - 1 = {2 * (hR - 2) - 1:g}), minimum sampled in the loop "
                  f"{run['n'][n_min_i]:.3e} weights at {run['t'][n_min_i]:.4f} s, {math.degrees(track.loop_phi(run['s'][n_min_i])):.3f} "
                  f"degrees round; MAKES IT ROUND: leaves the loop at {run['loop_exit']['t']:.4f} s at "
                  f"{run['loop_exit']['v']:.4f} m/s and reaches the end of the exit at {run['gone']['t']:.4f} s; "
                  f"energy drift {run['drift']:.1e}")
    for hR in man["check_heights_R"]:
        run = simulate(track, g, hR * R, 0.0, steps, tol)
        if run["depart"] is not None:
            d = run["depart"]
            print(f"check h = {hR:g} R (not drawn): leaves at {math.degrees(d['phi']) - 90:.2f} degrees above the centre, "
                  f"{180 - math.degrees(d['phi']):.2f} short of the top (closed form {closed_form_theta(hR):.2f} above), height "
                  f"{d['y'] / R:.4f} R, at {d['t']:.4f} s; lands after {run['flight']['dt']:.4f} s at {math.degrees(run['flight']['phi']):.1f} degrees round")
        else:
            print(f"check h = {hR:g} R (not drawn): makes it round; track force at the top {2 * (hR - 2) - 1:.4f} weights, "
                  f"top at {run['top']['t']:.4f} s at {run['top']['v']:.4f} m/s")
    for hR in man["rolling_heights_R"]:
        run = simulate(track, g, hR * R, man["rolling_k"], steps, tol)
        if run["depart"] is not None:
            d = run["depart"]
            print(f"check rolling solid ball from h = {hR:g} R (not drawn): leaves at {math.degrees(d['phi']) - 90:.2f} degrees "
                  f"above the centre, {180 - math.degrees(d['phi']):.2f} short of the top (closed form "
                  f"{closed_form_theta(hR, man['rolling_k']):.2f} above), at {d['t']:.4f} s, speed {d['v']:.4f} m/s")
        else:
            k = man["rolling_k"]
            print(f"check rolling solid ball from h = {hR:g} R (not drawn): makes it round; track force at the top "
                  f"{2 * (hR - 2) / (1 + k) - 1:.6f} weights, top speed {run['top']['v']:.4f} m/s at {run['top']['t']:.4f} s")
    # Run schedule in video time.
    period, rel = man["run_period"], man["release_at"]
    n_runs = int(round(man["scene_duration"] / period))
    lines = []
    for r in range(n_runs):
        t0 = r * period + rel
        top, bot = runs["top"], runs["bottom"]
        lines.append(f"run {r + 1}: release {t0:.2f} s; top puck enters the loop {t0 + top['entry']['t'] * slow:.2f} s, "
                     f"leaves the track {t0 + top['depart']['t'] * slow:.2f} s, lands {t0 + (top['depart']['t'] + top['flight']['dt']) * slow:.2f} s; "
                     f"bottom puck enters {t0 + bot['entry']['t'] * slow:.2f} s, passes the top {t0 + bot['top']['t'] * slow:.2f} s, "
                     f"leaves the loop {t0 + bot['loop_exit']['t'] * slow:.2f} s, off the end {t0 + bot['gone']['t'] * slow:.2f} s; "
                     f"reset {r * period + period - man['reset_dur']:.2f} to {r * period + period:.2f} s")
    print(f"schedule ({n_runs} runs of {period:g} s at 1/{slow} speed, release {rel:g} s into each run, crossfade reset over "
          f"the last {man['reset_dur']:g} s): " + "; ".join(lines))
    print(f"title until {man['title_until']:g} s; payoff card from {man['payoff_t']:g} s; loop fade {man['loop_fade']:g} s")
    # Text widths.
    font = os.environ["SEED_ZERO_FONT"]
    f34, f56, f40, f28, f32, f48 = (ImageFont.truetype(font, n) for n in (34, 56, 40, 28, 32, 48))
    short = 180.0 - math.degrees(runs["top"]["depart"]["phi"])
    widths = {"overlay@34": (f34, man["overlay"])}
    for j, line in enumerate(man["title"].split("|")):
        widths[f"title line {j + 1}@56"] = (f56, line)
    widths["label top@40"] = (f40, "level with the top")
    widths["label bottom@40"] = (f40, "half a radius higher")
    widths["sublabel@28"] = (f28, "released from rest 2.5 m up")
    widths["level label@28"] = (f28, "level with the top")
    widths["readout label@28"] = (f28, "push from the track")
    widths["readout@48"] = (f48, "6.0 x weight")
    widths["depart label@32"] = (f32, f"{short:.0f} deg short")
    widths["top label@32"] = (f32, "push 0 at the top")
    widths["round label@32"] = (f32, "all the way round")
    for j, line in enumerate(payoff_lines(man, runs)):
        widths[f"payoff line {j + 1}@40"] = (f40, line)
    print("text widths: " + ", ".join(f"{k} {f.getlength(s):.0f} px" for k, (f, s) in widths.items()))
    return {"track": track, "runs": runs}


def payoff_lines(man: dict, runs: dict) -> list[str]:
    short = 180.0 - math.degrees(runs["top"]["depart"]["phi"])
    text = man["payoff_text"].format(short=short, ratio=runs["bottom"]["hR"])
    return [s.strip() for s in text.split("|")]


class Renderer:
    def __init__(self, man: dict, meas: dict):
        self.man, self.meas = man, meas
        self.fps = man["fps"]
        self.track: Track = meas["track"]
        self.runs = meas["runs"]
        font = os.environ["SEED_ZERO_FONT"]
        self.font = ImageFont.truetype(font, 40)
        self.font_title = ImageFont.truetype(font, 56)
        self.font_small = ImageFont.truetype(font, 28)
        self.font_mark = ImageFont.truetype(font, 32)
        self.font_num = ImageFont.truetype(font, 48)
        self.ppm = float(man["px_per_m"])
        self.first = None
        self.start_state = None
        self.run_frames = int(round(man["run_period"] * self.fps))
        self.short = 180.0 - math.degrees(self.runs["top"]["depart"]["phi"])
        self.track_pts = [self.track.point(s)[:2] for s in np.linspace(0.0, self.track.s_dip, 160)]
        self.exit_len = man["exit_length_m"]

    # --- geometry helpers -------------------------------------------------
    def base_y(self, name: str) -> float:
        return GEOM_Y0 + PANELS[name]["index"] * PANEL_H + PANEL_H - BASE_PAD

    def px(self, name: str, x: float, y: float, ss: int = 1) -> tuple[float, float]:
        return (LOOP_CX + x * self.ppm) * ss, (self.base_y(name) - y * self.ppm) * ss

    def state(self, name: str, tau: float) -> dict:
        """Puck state at run time tau (video seconds since the run start)."""
        man, run = self.man, self.runs[name]
        tp = max(0.0, tau - man["release_at"]) / man["slow_factor"]
        dep = run["depart"]
        if dep is not None and tp >= dep["t"]:
            fl = run["flight"]
            if tp - dep["t"] >= fl["dt"]:
                return {"mode": "landed", "x": fl["x"], "y": fl["y"], "nx": fl["nx"], "ny": fl["ny"], "n": 0.0, "tp": tp}
            x, y = fl["pos"](tp - dep["t"])
            return {"mode": "flight", "x": x, "y": y, "nx": dep["nx"], "ny": dep["ny"], "n": 0.0, "tp": tp}
        if run["gone"] is not None and tp >= run["gone"]["t"]:
            return {"mode": "gone", "x": 0.0, "y": 0.0, "nx": 0.0, "ny": 1.0, "n": 1.0, "tp": tp}
        s = float(np.interp(tp, run["t"], run["s"]))
        nm = float(np.interp(tp, run["t"], run["n"]))
        x, y, _, _, nx, ny, _ = self.track.point(s)
        return {"mode": "track", "x": x, "y": y, "nx": nx, "ny": ny, "n": nm, "tp": tp, "s": s}

    # --- drawing ----------------------------------------------------------
    def dashed(self, d: ImageDraw.ImageDraw, p0, p1, fill, width: int, dash: float, gap: float) -> None:
        x0, y0 = p0
        x1, y1 = p1
        L = math.hypot(x1 - x0, y1 - y0)
        if L < 1e-9:
            return
        ux, uy = (x1 - x0) / L, (y1 - y0) / L
        a = 0.0
        while a < L:
            b = min(L, a + dash)
            d.line((x0 + ux * a, y0 + uy * a, x0 + ux * b, y0 + uy * b), fill=fill, width=width)
            a = b + gap

    def draw_panel_geometry(self, d: ImageDraw.ImageDraw, name: str, st: dict, tau: float, alpha: float) -> None:
        """Track, marks and the puck on the supersampled layer (y relative to GEOM_Y0)."""
        man, run, track = self.man, self.runs[name], self.track
        col = PANELS[name]["colour"]
        R = track.R

        def P(x: float, y: float) -> tuple[float, float]:
            px, py = self.px(name, x, y, SS)
            return px, py - GEOM_Y0 * SS

        # Track: ramp and dip, loop, exit.
        d.line([P(x, y) for x, y in self.track_pts], fill=WIRE, width=6 * SS, joint="curve")
        d.line((P(0.0, 0.0), P(self.exit_len + 0.5, 0.0)), fill=WIRE, width=6 * SS)
        cx, cy = P(0.0, R)
        Rp = R * self.ppm * SS
        d.ellipse((cx - Rp, cy - Rp, cx + Rp, cy + Rp), outline=blend(col, 0.7), width=6 * SS)
        # Level line at the height of the top of the loop, from the ramp to the top.
        x_ramp = track.point(track.s_at_height(2.0 * R))[0]
        d_level = blend(col, 0.75) if name == "top" else blend(MUTED, 0.7)
        self.dashed(d, P(x_ramp, 2.0 * R), P(0.0, 2.0 * R), d_level, 3 * SS, 14 * SS, 10 * SS)
        tx, ty = P(0.0, 2.0 * R)
        d.line((tx, ty - 16 * SS, tx, ty + 16 * SS), fill=blend(col, 0.9), width=4 * SS)
        # Start mark on the ramp (a short tick across the track at the release point).
        s0 = track.s_at_height(run["hR"] * R)
        x0, y0, _, _, nx0, ny0, _ = track.point(s0)
        d.line((P(x0 - nx0 * 0.09, y0 - ny0 * 0.09), P(x0 + nx0 * 0.09, y0 + ny0 * 0.09)), fill=blend(col, 0.9), width=4 * SS)
        # Departure marks after the event.
        dep = run["depart"]
        if dep is not None and st["mode"] in ("flight", "landed"):
            fl = run["flight"]
            gold = blend(GOLD, alpha)
            d.line((P(0.0, R), P(dep["x"], dep["y"])), fill=gold, width=4 * SS)
            d.line((P(0.0, R), P(0.0, 2.0 * R)), fill=blend(MUTED, 0.8 * alpha), width=3 * SS)
            Ra = Rp + 30 * SS
            d.arc((cx - Ra, cy - Ra, cx + Ra, cy + Ra), start=-90, end=90 - math.degrees(dep["phi"]), fill=gold, width=6 * SS)
            # Flight trail: dots along the path flown so far.
            t_fl = min(st["tp"] - dep["t"], fl["dt"])
            n_dots = int(t_fl / (0.02 / 1.0)) + 1
            for i in range(n_dots):
                x, y = fl["pos"](i * 0.02)
                qx, qy = P(x + dep["nx"] * PUCK_R / self.ppm, y + dep["ny"] * PUCK_R / self.ppm)
                r = 3 * SS
                d.ellipse((qx - r, qy - r, qx + r, qy + r), fill=blend(GOLD, 0.45 * alpha))
        top = run["top"]
        if dep is None and top is not None and st["tp"] >= top["t"]:
            tx, ty = P(0.0, 2.0 * R)
            r = 11 * SS
            d.ellipse((tx - r, ty - r, tx + r, ty + r), outline=blend(GOLD, alpha), width=3 * SS)
        # Puck.
        if st["mode"] != "gone":
            qx, qy = P(st["x"] + st["nx"] * PUCK_R / self.ppm, st["y"] + st["ny"] * PUCK_R / self.ppm)
            r = PUCK_R * SS
            d.ellipse((qx - r, qy - r, qx + r, qy + r), fill=blend(GOLD, alpha), outline=blend((120, 84, 30), alpha), width=SS)
            hr = r * 0.32
            d.ellipse((qx - r * 0.45 - hr, qy - r * 0.45 - hr, qx - r * 0.45 + hr, qy - r * 0.45 + hr), fill=blend(WHITE, alpha))

    def draw_panel_text(self, d: ImageDraw.ImageDraw, name: str, st: dict, alpha: float) -> None:
        man, run, track = self.man, self.runs[name], self.track
        col = PANELS[name]["colour"]
        top_y = GEOM_Y0 + PANELS[name]["index"] * PANEL_H
        base = self.base_y(name)
        label = "level with the top" if name == "top" else "half a radius higher"
        d.text((W - 40, top_y + 24), label, font=self.font, fill=col, anchor="rm")
        d.text((W - 40, top_y + 66), f"released from rest {run['hR'] * track.R:.1f} m up", font=self.font_small, fill=MUTED, anchor="rm")
        if name == "top":
            lx, ly = self.px(name, 0.0 - 0.9, 2.0 * track.R)
            d.text((lx, ly - 22), "level with the top", font=self.font_small, fill=blend(col, 0.9), anchor="mm")
        d.text((60, base - 88), "push from the track", font=self.font_small, fill=MUTED, anchor="lm")
        if st["mode"] == "track":
            num = f"{st['n']:.1f} x weight"
            ncol = GOLD if st["n"] < 0.05 else TEXT
        elif st["mode"] in ("flight", "landed"):
            num = "0.0 x weight"
            ncol = GOLD
        else:
            num = "off the end"
            ncol = MUTED
        d.text((60, base - 40), num, font=self.font_num, fill=blend(ncol, alpha), anchor="lm")
        mx, my = W - 40, top_y + 106
        if run["depart"] is not None and st["mode"] in ("flight", "landed"):
            d.text((mx, my), f"{self.short:.0f} deg short", font=self.font_mark, fill=blend(GOLD, alpha), anchor="rm")
        if run["depart"] is None and run["top"] is not None and st["tp"] >= run["top"]["t"]:
            word = "all the way round" if st["tp"] >= run["loop_exit"]["t"] else "push 0 at the top"
            d.text((mx, my), word, font=self.font_mark, fill=blend(GOLD, alpha), anchor="rm")

    def draw_state(self, tau: float) -> np.ndarray:
        """The full frame for run time tau, without title or card."""
        img = Image.new("RGB", (W, H), BG)
        layer = Image.new("RGB", (W * SS, (GEOM_Y1 - GEOM_Y0) * SS), BG)
        ld = ImageDraw.Draw(layer)
        states = {name: self.state(name, tau) for name in PANELS}
        for name in PANELS:
            self.draw_panel_geometry(ld, name, states[name], tau, 1.0)
        img.paste(layer.reduce(SS), (0, GEOM_Y0))
        d = ImageDraw.Draw(img)
        for name in PANELS:
            self.draw_panel_text(d, name, states[name], 1.0)
        return np.asarray(img, dtype=np.float32)

    def draw_scene(self, t: float) -> Image.Image:
        """Run time from video time; the last reset_dur of each run crossfades to the start state."""
        man = self.man
        period = man["run_period"]
        tau = t - int(t // period) * period
        reset_start = period - man["reset_dur"]
        u = smoothstep((tau - reset_start) / man["reset_dur"]) if tau >= reset_start else 0.0
        live = self.draw_state(tau)
        if u > 0.0:
            if self.start_state is None:
                self.start_state = self.draw_state(0.0)
            live = live * (1.0 - u) + self.start_state * u
        return Image.fromarray(live.astype(np.uint8))

    def live_frame(self, f: int) -> np.ndarray:
        man = self.man
        t = f / self.fps
        img = self.draw_scene(t)
        d = ImageDraw.Draw(img)
        if t < man["title_until"]:
            a = 1.0 if t < man["title_until"] - 0.4 else (man["title_until"] - t) / 0.4
            for j, line in enumerate(man["title"].split("|")):
                d.text((W / 2, 190 + j * 62), line, font=self.font_title, fill=blend(TEXT, a), anchor="mm")
        if t >= man["payoff_t"]:
            a = min(1.0, (t - man["payoff_t"]) / man["payoff_hold"])
            for j, line in enumerate(payoff_lines(man, self.runs)):
                d.text((W / 2, PAYOFF_Y + j * 56), line, font=self.font, fill=blend(GOLD, a), anchor="mm")
        return np.asarray(img, dtype=np.float32)

    def frame_at(self, f: int) -> np.ndarray:
        man = self.man
        total = int(round(man["scene_duration"] * self.fps))
        live = self.live_frame(f)
        fade_frames = int(round(man["loop_fade"] * self.fps))
        if f >= total - fade_frames:
            if self.first is None:
                self.first = self.live_frame(0)
            a = (f - (total - fade_frames) + 1) / fade_frames
            live = live * (1 - a) + self.first * a
        return live.astype(np.uint8)

    def render(self, out_path: Path) -> None:
        global _RENDERER
        out_path.parent.mkdir(parents=True, exist_ok=True)
        total = int(round(self.man["scene_duration"] * self.fps))
        first = self.frame_at(0)
        last = self.frame_at(total - 1)
        diff = np.abs(first.astype(int) - last.astype(int))
        print(f"loop check: last frame differs from the first in {int((diff.max(axis=2) > 24).sum())} px "
              f"(max channel difference {int(diff.max())})")
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
    man = json.loads((ROOT / "projects/looptrack/manifest.json").read_text())
    meas = measure(man)
    if "--measure-only" in sys.argv:
        return
    if "--frames" in sys.argv:
        times = [float(v) for v in sys.argv[sys.argv.index("--frames") + 1].split(",")]
        r = Renderer(man, meas)
        (ROOT / "media/looptrack").mkdir(parents=True, exist_ok=True)
        for tv in times:
            Image.fromarray(r.frame_at(int(round(tv * man["fps"])))).save(ROOT / f"media/looptrack/smoke-{tv}.png")
        print("smoke frames: " + ", ".join(f"{tv}" for tv in times))
        return
    Renderer(man, meas).render(ROOT / "media/looptrack/footage.mp4")


if __name__ == "__main__":
    main()
