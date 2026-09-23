#!/usr/bin/env python3
"""Racing balls: same speed, same finish. Does the dip slow it down?

Two equal solid balls leave the same start line at v0 = 1 m/s toward a
finish line L = 2 m away (horizontal distance). The top track is flat.
The bottom track is flat, dips `dip_depth_m` on two cosine ramps with a
flat floor between them, and comes back up to the same height before
the finish. Each ball rolls without slipping and without losses
(moment of inertia I = k m r^2, k = 2/5 for a solid ball), so along its
track (1 + k) m dv/dt = -m g sin(theta) and the energy closed form is
v(y) = sqrt(v0^2 - 2 g y / (1 + k)), y the height of the ball centre,
which follows the track profile y(x). The ball is integrated in x with
RK4 at a fixed step, x'' = -(g' y' + y' y'' x'^2) / (1 + y'^2) with
g' = g / (1 + k), and its speed is checked against the closed form at
every step. The track force (normal force) N = m (g cos theta + v^2
kappa) is printed in units of the weight and must stay positive at both
ramp crests (no lift-off). The race is played at quarter speed and
repeats every race_period seconds of video, so the video loops on the
race. Deterministic, no seed.

Measured and printed: both arrival times (RK4, the closed forms L / v0
and the quadrature of ds / v(s)), the dip track's length and the extra
length, the dip ball's top speed and where it is reached, its speed at
the finish, the largest lead in metres and when, the lead at its
arrival, the minimum and maximum track force in units of the weight
and the force at both crests, the minimum horizontal speed against the
flat ball, the energy drift, a half-step check, the same race for a
sliding bead (k = 0) for the description, the schedule in video time
and the on-screen text widths.

usage: racingballs.py [--measure-only] [--frames t1,t2,...]
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
TEXT = (216, 222, 230)
MUTED = (138, 148, 163)
WHITE = (236, 240, 244)
WIRE = (70, 80, 94)

# Layout: overlay at y 96..130 (captions.py), title rows at y 190/252 for
# the first seconds, then the race counter at y 236 and the model tag at
# y 290; "start" and "finish" labels at y 480 over dashed lines that span
# both tracks; the flat track's readout row at y 550 (label, speed, clock)
# and its ball level at y 740; the dip track's readout row at y 890, its
# ball level at y 1080 and the dip floor at y 1170; captions at caption_y
# 0.75 (y 1440..1520); the payoff card from y 1592.
COUNTER_Y, TAG_Y = 236, 290
MARK_Y = 480
GEOM_Y0, GEOM_Y1 = 500, 1230
SS = 2
PAYOFF_Y = 1592.0
TRACKS = {
    "flat": {"colour": TEAL, "label": "flat track", "label_y": 550, "base_y": 740.0},
    "dip": {"colour": GOLD, "label": "dip track", "label_y": 890, "base_y": 1080.0},
}
READ_X0, READ_X1 = 100, 980


def blend(col, a: float, base=BG) -> tuple:
    return tuple(int(round(c * a + b * (1 - a))) for c, b in zip(col, base))


def lighten(col, a: float) -> tuple:
    return blend(WHITE, a, col)


def smoothstep(u: float) -> float:
    u = max(0.0, min(1.0, u))
    return u * u * (3 - 2 * u)


# --- the track profile ------------------------------------------------------
class Profile:
    """The height of the ball centre y(x) and its first two derivatives.

    Flat to x0, a cosine ramp down over `ramp`, a flat floor of `floor` at
    -depth, a cosine ramp up over `ramp`, then flat to the finish. With
    depth = 0 the profile is the flat track.
    """

    def __init__(self, depth: float, x0: float, ramp: float, floor: float):
        self.d, self.x0, self.r, self.w = depth, x0, ramp, floor
        self.x1 = x0 + ramp            # start of the floor
        self.x2 = x0 + ramp + floor    # end of the floor
        self.x3 = x0 + 2 * ramp + floor  # back at the top

    def at(self, x: float) -> tuple[float, float, float]:
        d, r = self.d, self.r
        if d == 0.0 or x < self.x0 or x > self.x3:
            return 0.0, 0.0, 0.0
        if x < self.x1:
            u = (x - self.x0) / r
            return (-0.5 * d * (1.0 - math.cos(math.pi * u)),
                    -0.5 * d * math.sin(math.pi * u) * math.pi / r,
                    -0.5 * d * math.cos(math.pi * u) * (math.pi / r) ** 2)
        if x < self.x2:
            return -d, 0.0, 0.0
        u = (x - self.x2) / r
        return (-0.5 * d * (1.0 + math.cos(math.pi * u)),
                0.5 * d * math.sin(math.pi * u) * math.pi / r,
                0.5 * d * math.cos(math.pi * u) * (math.pi / r) ** 2)

    def y(self, x: float) -> float:
        return self.at(x)[0]

    def curvature(self, x: float) -> float:
        _, yp, ypp = self.at(x)
        return ypp / (1.0 + yp * yp) ** 1.5

    def normal_force(self, x: float, v: float, g: float) -> float:
        """The track force on a ball moving at speed v along the track, in units of its weight."""
        _, yp, _ = self.at(x)
        return 1.0 / math.sqrt(1.0 + yp * yp) + v * v * self.curvature(x) / g


def closed_speed(man: dict, k: float, y: float) -> float:
    return math.sqrt(man["launch_speed_m_s"] ** 2 - 2.0 * man["g"] * y / (1.0 + k))


def track_length(prof: Profile, L: float, n: int = 400_000) -> float:
    xs = np.linspace(0.0, L, n + 1)
    mid = 0.5 * (xs[1:] + xs[:-1])
    yp = np.array([prof.at(x)[1] for x in mid])
    return float(np.sum(np.sqrt(1.0 + yp * yp)) * (L / n))


def quadrature_time(man: dict, prof: Profile, k: float, n: int = 400_000) -> float:
    """Independent check: T = integral ds / v(s) = integral sqrt(1 + y'^2) / v(y(x)) dx."""
    L = man["track_length_m"]
    xs = np.linspace(0.0, L, n + 1)
    mid = 0.5 * (xs[1:] + xs[:-1])
    val = np.array([math.sqrt(1.0 + prof.at(x)[1] ** 2) / closed_speed(man, k, prof.at(x)[0]) for x in mid])
    return float(np.sum(val) * (L / n))


# --- RK4 along the track ----------------------------------------------------
def integrate(man: dict, prof: Profile, k: float, dt: float) -> dict:
    """RK4 on (x, x') with x'' = -(g' y' + y' y'' x'^2) / (1 + y'^2), g' = g / (1 + k), from
    x = 0 at speed v0 until x = L; the crossing is interpolated inside the last step.
    Records per step: t, x, y, the speed along the track, the arc length, the track force in
    units of the weight, and the largest difference from the closed-form speed."""
    g, v0, L = man["g"], man["launch_speed_m_s"], man["track_length_m"]
    ge = g / (1.0 + k)

    def deriv(x: float, u: float) -> tuple[float, float]:
        _, yp, ypp = prof.at(x)
        return u, -(ge * yp + yp * ypp * u * u) / (1.0 + yp * yp)

    def speed(x: float, u: float) -> float:
        return u * math.sqrt(1.0 + prof.at(x)[1] ** 2)

    x, u, t, s = 0.0, v0, 0.0, 0.0
    ts, xs, ys, vs, ss, ns, us = [0.0], [0.0], [prof.y(0.0)], [v0], [0.0], [prof.normal_force(0.0, v0, g)], [v0]
    max_dv = 0.0
    while True:
        k1x, k1u = deriv(x, u)
        k2x, k2u = deriv(x + 0.5 * dt * k1x, u + 0.5 * dt * k1u)
        k3x, k3u = deriv(x + 0.5 * dt * k2x, u + 0.5 * dt * k2u)
        k4x, k4u = deriv(x + dt * k3x, u + dt * k3u)
        xn = x + dt / 6.0 * (k1x + 2 * k2x + 2 * k3x + k4x)
        un = u + dt / 6.0 * (k1u + 2 * k2u + 2 * k3u + k4u)
        t += dt
        if xn >= L:
            frac = (L - x) / (xn - x)
            t_arr = t - dt + frac * dt
            u_arr = u + frac * (un - u)
            v_arr = speed(L, u_arr)
            s += 0.5 * (vs[-1] + v_arr) * frac * dt
            ts.append(t_arr); xs.append(L); ys.append(prof.y(L)); vs.append(v_arr); ss.append(s)
            ns.append(prof.normal_force(L, v_arr, g)); us.append(u_arr)
            break
        x, u = xn, un
        v = speed(x, u)
        s += 0.5 * (vs[-1] + v) * dt
        max_dv = max(max_dv, abs(v - closed_speed(man, k, prof.y(x))))
        ts.append(t); xs.append(x); ys.append(prof.y(x)); vs.append(v); ss.append(s)
        ns.append(prof.normal_force(x, v, g)); us.append(u)
    return {"t": np.array(ts), "x": np.array(xs), "y": np.array(ys), "v": np.array(vs), "s": np.array(ss),
            "n": np.array(ns), "u": np.array(us), "t_arr": t_arr, "v_arr": v_arr, "s_arr": s, "max_dv": max_dv, "k": k}


# --- measurement --------------------------------------------------------------
def measure(man: dict) -> dict:
    g, v0, L, d = man["g"], man["launch_speed_m_s"], man["track_length_m"], man["dip_depth_m"]
    k, fps, pb = man["k_inertia"], man["fps"], man["playback"]
    dt = 1.0 / man["steps_per_second"]
    flat = Profile(0.0, man["dip_start_m"], man["ramp_m"], man["dip_floor_m"])
    dip = Profile(d, man["dip_start_m"], man["ramp_m"], man["dip_floor_m"])
    P = man["race_period"]
    print(f"setup: two equal solid balls (I = {k:g} m r^2, radius {man['ball_radius_m'] * 100:g} cm) leave the same "
          f"start line at {v0:g} m/s toward a finish line {L:g} m away; the top track is flat; the bottom track is "
          f"flat to x = {dip.x0:g} m, dips {d * 100:g} cm on a cosine ramp {dip.r:g} m long, runs a flat floor "
          f"{dip.w:g} m long at -{d:g} m, climbs a cosine ramp {dip.r:g} m long back to the top at x = {dip.x3:g} m, "
          f"then runs flat to the finish; the ball centre follows the profile; rolling without slip, no losses, g = "
          f"{g}; RK4 in x at {man['steps_per_second']} steps per second (dt = {dt:.0e} s); played at {pb:g} speed, "
          f"{man['races']} races of {P:g} s; drawn at {man['px_per_m']:g} px per metre ({L * man['px_per_m']:.0f} px "
          f"across, the dip {d * man['px_per_m']:.0f} px deep); deterministic, no seed")
    runs = {"flat": integrate(man, flat, k, dt), "dip": integrate(man, dip, k, dt)}
    F, D = runs["flat"], runs["dip"]
    t_flat_closed = L / v0
    print(f"flat track: arrives at {F['t_arr']:.4f} s (closed form L / v0 = {t_flat_closed:.4f} s, diff "
          f"{abs(F['t_arr'] - t_flat_closed):.1e}), speed at the finish {F['v_arr']:.4f} m/s, track force "
          f"{F['n'].min():.4f} to {F['n'].max():.4f} of the weight, max |v - closed form| {F['max_dv']:.1e} m/s")
    len_dip = track_length(dip, L)
    quad_dip = quadrature_time(man, dip, k)
    v_top_closed = closed_speed(man, k, -d)
    i_top = int(np.argmax(D["v"] > D["v"].max() - 1e-9))
    print(f"dip track: arrives at {D['t_arr']:.4f} s (quadrature of ds / v(s) {quad_dip:.4f} s, diff "
          f"{abs(D['t_arr'] - quad_dip):.1e}); track length {len_dip:.4f} m, {len_dip - L:.4f} m ({100 * (len_dip / L - 1):.1f} "
          f"percent) longer than the flat track; top speed {D['v'].max():.4f} m/s (closed form sqrt(v0^2 + 2 g d / "
          f"(1 + k)) = {v_top_closed:.4f}) first reached at x = {D['x'][i_top]:.4f} m, t = {D['t'][i_top]:.4f} s, held "
          f"along the floor to x = {dip.x2:g} m; speed at the finish {D['v_arr']:.4f} m/s (launch {v0:g}); max |v - "
          f"closed form| over all steps {D['max_dv']:.1e} m/s")
    lead = D["x"] - v0 * D["t"]
    i_lead = int(np.argmax(lead > lead.max() - 1e-9))
    lead_at_arrival = L - v0 * D["t_arr"]
    print(f"lead: the dip ball is ahead of the flat ball by at most {lead.max():.4f} m, first at t = {D['t'][i_lead]:.4f} "
          f"s (x = {D['x'][i_lead]:.4f} m, the top of the exit ramp), and by {lead_at_arrival:.4f} m when it "
          f"arrives (the flat ball is at x = {v0 * D['t_arr']:.4f} m); it wins by {F['t_arr'] - D['t_arr']:.4f} s "
          f"({100 * (1 - D['t_arr'] / F['t_arr']):.1f} percent of the flat time)")
    i_nmin, i_nmax = int(np.argmin(D["n"])), int(np.argmax(D["n"]))
    n_crest0 = dip.normal_force(dip.x0, closed_speed(man, k, 0.0), g)
    n_crest1 = dip.normal_force(dip.x3, closed_speed(man, k, 0.0), g)
    print(f"track force on the dip ball (units of the weight): minimum {D['n'].min():.4f} at x = {D['x'][i_nmin]:.4f} m, "
          f"maximum {D['n'].max():.4f} at x = {D['x'][i_nmax]:.4f} m; at the entry crest (x = {dip.x0:g} m, curvature "
          f"{dip.curvature(dip.x0):.3f} 1/m, radius {1 / abs(dip.curvature(dip.x0)):.3f} m) {n_crest0:.4f}, at the exit "
          f"crest (x = {dip.x3:g} m) {n_crest1:.4f}; positive everywhere, so the ball never lifts off")
    assert D["n"].min() > 0.0, "the dip ball lifts off"
    i_umin = int(np.argmin(D["u"]))
    print(f"horizontal speed of the dip ball: minimum {D['u'].min():.4f} m/s at x = {D['x'][i_umin]:.4f} m (the flat "
          f"ball's {v0:g} m/s), so the dip ball is never behind the flat ball; speed along the track never below "
          f"{D['v'].min():.4f} m/s")
    t_in, t_out = float(np.interp(dip.x0, D["x"], D["t"])), float(np.interp(dip.x3, D["x"], D["t"]))
    print(f"dip crossing: the dip ball enters the dip at t = {t_in:.4f} s and is back at the top at t = {t_out:.4f} s, "
          f"{t_out - t_in:.4f} s for {dip.x3 - dip.x0:g} m of horizontal distance that the flat ball covers in "
          f"{(dip.x3 - dip.x0) / v0:.4f} s")
    half = integrate(man, dip, k, dt / 2)
    print(f"check: at half the time step the dip ball arrives at {half['t_arr']:.6f} s against {D['t_arr']:.6f} s "
          f"(diff {abs(half['t_arr'] - D['t_arr']):.1e} s)")
    bead = integrate(man, dip, 0.0, dt)
    print(f"for the description: a sliding bead (k = 0, no spin) on the same dip arrives at {bead['t_arr']:.4f} s "
          f"(quadrature {quadrature_time(man, dip, 0.0):.4f} s), top speed {bead['v'].max():.4f} m/s (closed form "
          f"{closed_speed(man, 0.0, -d):.4f}), wins by {t_flat_closed - bead['t_arr']:.4f} s, minimum track force "
          f"{bead['n'].min():.4f} of the weight")
    rel, reset, rest = man["release_at"], man["reset_dur"], man["rest_dur"]
    t_dip_v, t_flat_v = D["t_arr"] / pb, F["t_arr"] / pb
    hold = P - reset - rest - rel - t_flat_v
    assert hold > 0.0, "the race period is too short"
    assert rest >= man["loop_fade"], "the loop fade must play over balls at rest"
    assert abs(man["races"] * P - man["scene_duration"]) < 1e-9
    print(f"schedule (video time, {pb:g} speed): each {P:g} s race releases both balls at {rel:g} s, the dip ball "
          f"arrives {t_dip_v:.2f} s after the release and the flat ball {t_flat_v:.2f} s after; clocks frozen for "
          f"{hold:.2f} s, then a {reset:g} s slide back to the start and {rest:g} s at rest; arrivals at "
          + ", ".join(f"{i * P + rel + t_dip_v:.2f}/{i * P + rel + t_flat_v:.2f} s" for i in range(man["races"]))
          + f" (dip/flat); title until {man['title_until']:g} s; payoff card from {man['payoff_t']:g} s; loop fade "
          f"{man['scene_duration'] - man['loop_fade']:.1f} to {man['scene_duration']:g} s")
    ev = {"runs": runs, "profiles": {"flat": flat, "dip": dip}, "len_dip": len_dip, "lead_max": float(lead.max())}
    # Text widths.
    font = os.environ["SEED_ZERO_FONT"]
    f28, f32, f34, f40, f56, f64 = (ImageFont.truetype(font, n) for n in (28, 32, 34, 40, 56, 64))
    widths = {"overlay@34": (f34, man["overlay"])}
    for j, line in enumerate(man["title"].split("|")):
        widths[f"title line {j + 1}@56"] = (f56, line)
    widths["counter@40"] = (f40, f"race {man['races']} of {man['races']}")
    widths["tag@28"] = (f28, model_tag(man))
    for name in TRACKS:
        widths[f"label {name}@32"] = (f32, TRACKS[name]["label"])
    widths["clock@64"] = (f64, "t 1.62 s")
    widths["frozen clock@64"] = (f64, f"{F['t_arr']:.2f} s")
    widths["arrived tag@32"] = (f32, "arrived")
    widths["speed@28"] = (f28, speed_text(D["v"].max()))
    widths["start@28"] = (f28, "start")
    widths["finish@28"] = (f28, "finish")
    widths["depth@28"] = (f28, depth_text(man))
    for j, line in enumerate(payoff_lines(man, ev)):
        widths[f"payoff line {j + 1}@40"] = (f40, line)
    print("text widths: " + ", ".join(f"{k} {f.getlength(s):.0f} px" for k, (f, s) in widths.items()))
    return ev


def model_tag(man: dict) -> str:
    return "solid ball, rolling without slip, no losses"


def speed_text(v: float) -> str:
    return f"speed {v:.2f} m/s"


def depth_text(man: dict) -> str:
    return f"{man['dip_depth_m'] * 100:g} cm"


def payoff_lines(man: dict, ev: dict) -> list[str]:
    text = man["payoff_text"].format(t_dip=ev["runs"]["dip"]["t_arr"], t_flat=ev["runs"]["flat"]["t_arr"])
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
        self.font_label = ImageFont.truetype(font, 32)
        self.font_num = ImageFont.truetype(font, 64)
        self.ppm = float(man["px_per_m"])
        self.r_px = man["ball_radius_m"] * self.ppm
        self.x_origin = W / 2.0 - man["track_length_m"] / 2.0 * self.ppm
        self.first = None
        # Surface polylines (the centre path offset down by the ball radius), in layer pixels.
        self.surfaces = {}
        for name in TRACKS:
            prof = ev["profiles"][name]
            pts = []
            for x in np.linspace(0.0, man["track_length_m"], 900):
                y, yp, _ = prof.at(float(x))
                nrm = math.sqrt(1.0 + yp * yp)
                pts.append(self.L(x + man["ball_radius_m"] * yp / nrm, y - man["ball_radius_m"] / nrm, name))
            self.surfaces[name] = pts

    # --- geometry helpers -------------------------------------------------
    def px(self, x: float, y: float, name: str) -> tuple[float, float]:
        """Frame pixel of a point in metres on track `name` (x along, y up)."""
        return self.x_origin + x * self.ppm, TRACKS[name]["base_y"] - y * self.ppm

    def L(self, x: float, y: float, name: str) -> tuple[float, float]:
        X, Y = self.px(x, y, name)
        return X * SS, (Y - GEOM_Y0) * SS

    def race_state(self, t: float) -> tuple[int, float, float, float]:
        """Video time -> (race index, seconds into the race, physics time, reset fraction)."""
        man = self.man
        P = man["race_period"]
        k = int(t // P)
        tau = t - k * P
        reset_start = P - man["reset_dur"] - man["rest_dur"]
        u = smoothstep((tau - reset_start) / man["reset_dur"]) if tau >= reset_start else 0.0
        tp = max(0.0, tau - man["release_at"]) * man["playback"]
        return k, tau, tp, u

    def ball_state(self, name: str, tp: float, u: float) -> dict:
        run = self.ev["runs"][name]
        arrived = tp >= run["t_arr"]
        if arrived:
            x, v, s, tc = self.man["track_length_m"], run["v_arr"], run["s_arr"], run["t_arr"]
        else:
            x = float(np.interp(tp, run["t"], run["x"]))
            v = float(np.interp(tp, run["t"], run["v"]))
            s = float(np.interp(tp, run["t"], run["s"]))
            tc = tp
        xd, sd = x * (1.0 - u), s * (1.0 - u)
        return {"x": xd, "y": self.ev["profiles"][name].y(xd), "phi": sd / self.man["ball_radius_m"], "v": v,
                "tc": tc, "arrived": arrived, "tp": tp}

    # --- drawing ----------------------------------------------------------
    @staticmethod
    def dashed_line(d: ImageDraw.ImageDraw, p0, p1, fill, width: int, dash: float, gap: float) -> None:
        (x0, y0), (x1, y1) = p0, p1
        seg = math.hypot(x1 - x0, y1 - y0)
        ux, uy = (x1 - x0) / seg, (y1 - y0) / seg
        pos = 0.0
        while pos < seg:
            run = min(dash, seg - pos)
            d.line((x0 + ux * pos, y0 + uy * pos, x0 + ux * (pos + run), y0 + uy * (pos + run)), fill=fill, width=width)
            pos += dash + gap

    def draw_ball(self, d: ImageDraw.ImageDraw, X: float, Y: float, phi: float, col, a: float = 1.0) -> None:
        R = self.r_px * SS
        fill, dark = blend(col, a), blend(blend(col, 0.42), a)
        d.ellipse((X - R, Y - R, X + R, Y + R), fill=fill, outline=dark, width=2 * SS)
        c, s = math.cos(phi), math.sin(phi)
        d.line((X, Y, X + R * 0.86 * c, Y + R * 0.86 * s), fill=dark, width=4 * SS)
        d.ellipse((X - 3 * SS, Y - 3 * SS, X + 3 * SS, Y + 3 * SS), fill=dark)
        hx, hy = X - R * 0.38, Y - R * 0.42
        hr = R * 0.2
        d.ellipse((hx - hr, hy - hr, hx + hr, hy + hr), fill=blend(lighten(col, 0.5), a))

    def draw_geometry(self, d: ImageDraw.ImageDraw, states: dict, tau: float, u: float) -> None:
        man = self.man
        L, r = man["track_length_m"], man["ball_radius_m"]
        dip = self.ev["profiles"]["dip"]
        # Start and finish lines through both tracks.
        top, bot = (MARK_Y + 22 - GEOM_Y0) * SS, (GEOM_Y1 - 12 - GEOM_Y0) * SS
        for x in (0.0, L):
            X = (self.x_origin + x * self.ppm) * SS
            self.dashed_line(d, (X, top), (X, bot), blend(MUTED, 0.7), 2 * SS, 10 * SS, 8 * SS)
        # The dip's reference level (the flat surface continued) and the depth bracket.
        yl = -r
        self.dashed_line(d, self.L(dip.x0, yl, "dip"), self.L(dip.x3, yl, "dip"), blend(GOLD, 0.35), 2 * SS, 8 * SS, 8 * SS)
        xm = 0.5 * (dip.x1 + dip.x2)
        bx0, by0 = self.L(xm, yl, "dip")
        bx1, by1 = self.L(xm, yl - dip.d, "dip")
        d.line((bx0, by0, bx1, by1), fill=blend(GOLD, 0.6), width=2 * SS)
        for yy in (by0, by1):
            d.line((bx0 - 8 * SS, yy, bx0 + 8 * SS, yy), fill=blend(GOLD, 0.6), width=2 * SS)
        # Track surfaces.
        for name in TRACKS:
            d.line(self.surfaces[name], fill=blend(TRACKS[name]["colour"], 0.55), width=8 * SS, joint="curve")
        # Trails, then the balls.
        trail_frames = int(round(man["trail_seconds"] * self.fps))
        for name in TRACKS:
            col, prof, st = TRACKS[name]["colour"], self.ev["profiles"][name], states[name]
            if u > 0.0 or st["arrived"]:
                continue
            for back in range(trail_frames, 0, -1):
                tpb = st["tp"] - back / self.fps * man["playback"]
                if tpb < 0.0:
                    continue
                xb = float(np.interp(tpb, self.ev["runs"][name]["t"], self.ev["runs"][name]["x"]))
                X, Y = self.L(xb, prof.y(xb), name)
                fade = 1.0 - back / (trail_frames + 1)
                rr = self.r_px * SS * (0.35 + 0.45 * fade)
                d.ellipse((X - rr, Y - rr, X + rr, Y + rr), fill=blend(col, 0.3 * fade))
        for name in TRACKS:
            col, st = TRACKS[name]["colour"], states[name]
            X, Y = self.L(st["x"], st["y"], name)
            self.draw_ball(d, X, Y, st["phi"], col)
        # Arrival flash: an expanding ring for 0.6 s of video after each arrival.
        for name in TRACKS:
            col, st = TRACKS[name]["colour"], states[name]
            dtv = (st["tp"] - self.ev["runs"][name]["t_arr"]) / man["playback"]
            if st["arrived"] and 0.0 <= dtv < 0.6 and u == 0.0:
                a = dtv / 0.6
                X, Y = self.L(L, 0.0, name)
                rr = (self.r_px + 6 + 40 * a) * SS
                d.ellipse((X - rr, Y - rr, X + rr, Y + rr), outline=blend(col, 1.0 - a), width=3 * SS)

    def draw_text(self, d: ImageDraw.ImageDraw, states: dict, k: int, u: float, hud_alpha: float) -> None:
        man = self.man
        L = man["track_length_m"]
        for x, label in ((0.0, "start"), (L, "finish")):
            d.text((self.x_origin + x * self.ppm, MARK_Y), label, font=self.font_small, fill=MUTED, anchor="mm")
        dip = self.ev["profiles"]["dip"]
        bx, by = self.px(0.5 * (dip.x1 + dip.x2), -man["ball_radius_m"] - 0.5 * dip.d, "dip")
        d.text((bx + 14, by), depth_text(man), font=self.font_small, fill=blend(GOLD, 0.8), anchor="lm")
        for name in TRACKS:
            col, st, ly = TRACKS[name]["colour"], states[name], TRACKS[name]["label_y"]
            run = self.ev["runs"][name]
            d.text((READ_X0, ly), TRACKS[name]["label"], font=self.font_label, fill=col, anchor="lm")
            if u < 0.5:
                a = 1.0 - 2.0 * u
                sp = speed_text(st["v"])
                if st["arrived"]:
                    clock = f"{run['t_arr']:.2f} s"
                    d.text((READ_X1, ly + 18), clock, font=self.font_num, fill=blend(col, a), anchor="rm")
                    d.text((READ_X1 - self.font_num.getlength(clock) - 18, ly + 24), "arrived", font=self.font_label,
                           fill=blend(col, a), anchor="rm")
                else:
                    d.text((READ_X1, ly + 18), f"t {st['tc']:.2f} s", font=self.font_num, fill=blend(TEXT, a), anchor="rm")
            else:
                a = 2.0 * u - 1.0
                sp = speed_text(man["launch_speed_m_s"])
                d.text((READ_X1, ly + 18), "t 0.00 s", font=self.font_num, fill=blend(TEXT, a), anchor="rm")
            d.text((READ_X0, ly + 42), sp, font=self.font_small, fill=blend(MUTED, a), anchor="lm")
        if hud_alpha > 0.02:
            d.text((W / 2, COUNTER_Y), f"race {k + 1} of {man['races']}", font=self.font, fill=blend(TEXT, hud_alpha), anchor="mm")
            d.text((W / 2, TAG_Y), model_tag(man), font=self.font_small, fill=blend(MUTED, hud_alpha), anchor="mm")

    def live_frame(self, f: int) -> np.ndarray:
        man = self.man
        t = f / self.fps
        k, tau, tp, u = self.race_state(t)
        title_on = t < man["title_until"]
        if title_on:
            title_alpha = 1.0 if t < man["title_until"] - 0.4 else (man["title_until"] - t) / 0.4
            hud_alpha = 0.0
        else:
            title_alpha = 0.0
            hud_alpha = min(1.0, (t - man["title_until"]) / 0.4)
        states = {name: self.ball_state(name, tp, u) for name in TRACKS}
        img = Image.new("RGB", (W, H), BG)
        layer = Image.new("RGB", (W * SS, (GEOM_Y1 - GEOM_Y0) * SS), BG)
        self.draw_geometry(ImageDraw.Draw(layer), states, tau, u)
        img.paste(layer.reduce(SS), (0, GEOM_Y0))
        d = ImageDraw.Draw(img)
        self.draw_text(d, states, k, u, hud_alpha)
        if title_on:
            for j, line in enumerate(man["title"].split("|")):
                d.text((W / 2, 190 + j * 62), line, font=self.font_title, fill=blend(TEXT, title_alpha), anchor="mm")
        if t >= man["payoff_t"]:
            a = min(1.0, (t - man["payoff_t"]) / man["payoff_hold"])
            for j, line in enumerate(payoff_lines(man, self.ev)):
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
    man = json.loads((ROOT / "projects/racingballs/manifest.json").read_text())
    ev = measure(man)
    if "--measure-only" in sys.argv:
        return
    if "--frames" in sys.argv:
        times = [float(v) for v in sys.argv[sys.argv.index("--frames") + 1].split(",")]
        r = Renderer(man, ev)
        (ROOT / "media/racingballs").mkdir(parents=True, exist_ok=True)
        for tv in times:
            Image.fromarray(r.frame_at(int(round(tv * man["fps"])))).save(ROOT / f"media/racingballs/smoke-{tv}.png")
        print("smoke frames: " + ", ".join(f"{tv}" for tv in times))
        return
    Renderer(man, ev).render(ROOT / "media/racingballs/footage.mp4")


if __name__ == "__main__":
    main()
