#!/usr/bin/env python3
"""Bounce down a slope: a ball dropped on a slope. How far apart does it land?

A ball is dropped from h = 0.20 m (vertical, to the first contact point)
onto a slope of angle beta with sin(beta) = 1/4 (14.48 degrees) with
perfectly elastic, frictionless bounces, beside the same ball dropped
0.20 m onto a flat floor. Two panels, the same ball, released at the same
instant and drawn at the same scale. In slope coordinates the normal
velocity reverses at every bounce and the tangential velocity is untouched,
so every hop lasts T = 2 v0 / g = 0.4039 s (v0 = sqrt(2 g h) = 1.9806 m/s)
on the slope and on the flat floor alike, while the speed along the slope
grows by g sin(beta) T per hop: the landing gaps along the slope are
x_n = 8 n h sin(beta) = 0.40 n m, exactly 1 : 2 : 3 : 4, and the flat-floor
ball lands on the same spot every time. The slope run is an event-driven
flight (the time to the plane is the root of a quadratic, the normal
component is reflected, no time step) and is checked by an RK4 free-flight
integration at 6,000 steps per second with plane-crossing interpolation.
sin(beta) = 1/4 is chosen so the first gap is exactly 40 cm and the whole
run is 4.00 m along the slope (1.00 m of drop). The ball is a point for
every number and is drawn larger than life. Played at 1/5 speed, three
runs of 13.33 s with a short crossfade reset. Deterministic, no seed.

Measured and printed: the impact speed, the drop time, the hop time, the
hop height, the landing positions and gaps along the slope beside the
closed form, the gap ratios, the speed along the slope at each landing,
the full speed and the energy at each landing; the same for the flat
floor; the RK4 checks of both runs; the run schedule in video time; the
on-screen text widths.

usage: bounceslope.py [--measure-only] [--frames t1,t2,...]
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
SEP = (34, 40, 48)
GROUND = (26, 31, 39)

# Layout: overlay at y 96 (captions.py), title rows at y 190/252 for the
# first seconds, the slope panel from y 350 to 870 (first contact point at
# x 60, y 528, the slope descending to the right) and the flat-floor panel
# from y 870 to 1436 (floor at y 1190, the ball at x 160), a right-aligned
# readout column at x 1040 in each panel, captions at caption_y 0.75
# (y 1440..1520), payoff card under them from y 1592.
GEOM_Y0, GEOM_Y1 = 350, 1436
PANELS = {
    "slope": {"index": 0, "colour": CORAL, "top": 350, "bottom": 870, "origin": (60.0, 528.0)},
    "floor": {"index": 1, "colour": TEAL, "top": 870, "bottom": 1436, "origin": (160.0, 1190.0)},
}
COL_X = W - 40
SS = 2
PAYOFF_Y = 1592.0
SLAB_PX = 84
TICK_PX = 14
GAP_LABEL_PX = 40
HOP_LABEL_PX = 64


def blend(col, a, base=BG):
    return tuple(int(round(c * a + b * (1 - a))) for c, b in zip(col, base))


def smoothstep(u: float) -> float:
    u = max(0.0, min(1.0, u))
    return u * u * (3 - 2 * u)


# --- closed forms and the event-driven flight ----------------------------------
def basis(man: dict, name: str) -> tuple[float, float, float, float]:
    """(sin beta, cos beta, tangent down the slope, normal up out of the plane) as (sb, cb, t, n)."""
    sb = float(man["slope_sin"]) if name == "slope" else 0.0
    cb = math.sqrt(1.0 - sb * sb)
    return sb, cb


def flight_segments(man: dict, name: str) -> list[dict]:
    """The drop and the hops as exact free-flight segments.

    World coordinates: x to the right, y up, metres, the first contact point at
    the origin; the plane runs along (cos beta, -sin beta) with the unit normal
    (sin beta, cos beta). Each segment is a parabola from (x0, y0) with velocity
    (vx0, vy0) at t0; its end is the exact root of the quadratic for the height
    above the plane, and the next segment starts with the normal component of
    the velocity reversed.
    """
    g, h, hops = float(man["g_m_s2"]), float(man["drop_height_m"]), int(man["hops"])
    sb, cb = basis(man, name)
    nx, ny = sb, cb
    tx, ty = cb, -sb
    x, y, vx, vy = 0.0, h, 0.0, 0.0
    t = 0.0
    segs = []
    for k in range(hops + 1):
        d0 = nx * x + ny * y
        vn = nx * vx + ny * vy
        gn = g * cb
        tf = (vn + math.sqrt(vn * vn + 2.0 * gn * d0)) / gn
        x1, y1 = x + vx * tf, y + vy * tf - 0.5 * g * tf * tf
        vx1, vy1 = vx, vy - g * tf
        vn1 = nx * vx1 + ny * vy1
        vt1 = tx * vx1 + ty * vy1
        seg = {"k": k, "t0": t, "x0": x, "y0": y, "vx0": vx, "vy0": vy, "dur": tf, "t1": t + tf,
               "x1": x1, "y1": y1, "s1": tx * x1 + ty * y1, "residual": nx * x1 + ny * y1,
               "vt": vt1, "vn_in": vn1, "speed_in": math.hypot(vx1, vy1),
               "E": 0.5 * (vx1 * vx1 + vy1 * vy1) + g * y1,
               "apex_d": vn * vn / (2.0 * gn) if k > 0 else d0}
        vx, vy = vx1 - 2.0 * vn1 * nx, vy1 - 2.0 * vn1 * ny
        x, y, t = x1, y1, t + tf
        segs.append(seg)
    return segs


def state_at(man: dict, name: str, segs: list[dict], t: float) -> dict:
    """The ball at real time t (clamped to the last landing): position, velocity, hop index."""
    g = float(man["g_m_s2"])
    sb, cb = basis(man, name)
    t_end = segs[-1]["t1"]
    held = t >= t_end
    t = min(t, t_end)
    seg = segs[-1]
    for s in segs:
        if t < s["t1"]:
            seg = s
            break
    dt = t - seg["t0"]
    x = seg["x0"] + seg["vx0"] * dt
    y = seg["y0"] + seg["vy0"] * dt - 0.5 * g * dt * dt
    vx, vy = seg["vx0"], seg["vy0"] - g * dt
    vt = cb * vx - sb * vy
    return {"t": t, "x": x, "y": y, "vx": vx, "vy": vy, "vt": vt, "speed": math.hypot(vx, vy),
            "k": seg["k"], "dt": dt, "held": held, "landings": seg["k"] + (1 if held else 0)}


# --- RK4 check ---------------------------------------------------------------
def rk4(acc, state, dt: float):
    x, y, vx, vy = state
    a1x, a1y = acc(x, y, vx, vy)
    k1 = (vx, vy, a1x, a1y)
    s2 = (x + 0.5 * dt * k1[0], y + 0.5 * dt * k1[1], vx + 0.5 * dt * k1[2], vy + 0.5 * dt * k1[3])
    a2x, a2y = acc(*s2)
    k2 = (s2[2], s2[3], a2x, a2y)
    s3 = (x + 0.5 * dt * k2[0], y + 0.5 * dt * k2[1], vx + 0.5 * dt * k2[2], vy + 0.5 * dt * k2[3])
    a3x, a3y = acc(*s3)
    k3 = (s3[2], s3[3], a3x, a3y)
    s4 = (x + dt * k3[0], y + dt * k3[1], vx + dt * k3[2], vy + dt * k3[3])
    a4x, a4y = acc(*s4)
    k4 = (s4[2], s4[3], a4x, a4y)
    return tuple(state[i] + dt / 6.0 * (k1[i] + 2 * k2[i] + 2 * k3[i] + k4[i]) for i in range(4))


def check_rk4(man: dict, name: str, segs: list[dict]) -> dict:
    """RK4 free flight at steps_per_second with linear plane-crossing interpolation and reflection."""
    g, hops, steps = float(man["g_m_s2"]), int(man["hops"]), int(man["steps_per_second"])
    h = float(man["drop_height_m"])
    sb, cb = basis(man, name)
    nx, ny, tx, ty = sb, cb, cb, -sb
    dt = 1.0 / steps

    def acc(x, y, vx, vy):
        return 0.0, -g

    st = (0.0, h, 0.0, 0.0)
    t = 0.0
    E0 = g * h
    out = {"landings": [], "max_E_err": 0.0, "steps": 0}
    while len(out["landings"]) <= hops:
        x, y, vx, vy = st
        d_prev = nx * x + ny * y
        st2 = rk4(acc, st, dt)
        x2, y2, vx2, vy2 = st2
        d_new = nx * x2 + ny * y2
        out["steps"] += 1
        if d_prev > 0.0 >= d_new:
            f = d_prev / (d_prev - d_new)
            tc = t + f * dt
            xc, yc = x + f * (x2 - x), y + f * (y2 - y)
            vxc, vyc = vx + f * (vx2 - vx), vy + f * (vy2 - vy)
            vn = nx * vxc + ny * vyc
            out["landings"].append({"t": tc, "s": tx * xc + ty * yc, "vt": tx * vxc + ty * vyc,
                                    "speed": math.hypot(vxc, vyc), "E": 0.5 * (vxc * vxc + vyc * vyc) + g * yc})
            st = (xc, yc, vxc - 2.0 * vn * nx, vyc - 2.0 * vn * ny)
            t = tc
        else:
            st = st2
            t += dt
        x, y, vx, vy = st
        out["max_E_err"] = max(out["max_E_err"], abs(0.5 * (vx * vx + vy * vy) + g * y - E0))
    out["max_t_err"] = max(abs(a["t"] - s["t1"]) for a, s in zip(out["landings"], segs))
    out["max_s_err"] = max(abs(a["s"] - s["s1"]) for a, s in zip(out["landings"], segs))
    out["max_vt_err"] = max(abs(a["vt"] - s["vt"]) for a, s in zip(out["landings"], segs))
    out["max_speed_err"] = max(abs(a["speed"] - s["speed_in"]) for a, s in zip(out["landings"], segs))
    return out


# --- measurement --------------------------------------------------------------
def measure(man: dict) -> dict:
    g, h, hops = float(man["g_m_s2"]), float(man["drop_height_m"]), int(man["hops"])
    sb, cb = basis(man, "slope")
    beta = math.degrees(math.asin(sb))
    steps, slow, fps, ppm = int(man["steps_per_second"]), float(man["slow_factor"]), man["fps"], float(man["px_per_m"])
    v0 = math.sqrt(2.0 * g * h)
    t_d = math.sqrt(2.0 * h / g)
    T = 2.0 * v0 / g
    print(f"setup: a ball dropped from h = {h:g} m (vertical, to the first contact point) onto a slope of angle beta = "
          f"{beta:.4f} degrees (sin beta = {sb:g}, the slope drops 1 m in 4 m) with perfectly elastic, frictionless "
          f"bounces, beside the same ball dropped {h:g} m onto a flat floor, released at the same instant in two panels "
          f"at the same scale ({ppm:g} px per metre, drop {h * ppm:.0f} px, hop height {h * cb * ppm:.0f} px on the "
          f"slope and {h * ppm:.0f} px on the floor); g = {g:g} m/s^2; the slope run is an event-driven flight (the "
          f"time to the plane is the root of a quadratic, the normal velocity is reflected, the tangential velocity is "
          f"untouched, no time step) checked by an RK4 free flight at {steps} steps per second (dt = {1 / steps:.2e} "
          f"s) with plane-crossing interpolation; the ball is a point for every number; played at 1/{slow:g} speed; "
          f"deterministic, no seed")
    print(f"closed forms: impact speed v0 = sqrt(2 g h) = {v0:.4f} m/s, drop time sqrt(2 h / g) = {t_d:.4f} s, hop "
          f"time T = 2 v0 / g = {T:.4f} s on the slope and on the floor alike (the normal speed after the bounce is "
          f"v0 cos beta and the normal gravity g cos beta, the ratio is angle-free), hop height above the slope "
          f"h cos beta = {h * cb:.4f} m (floor: {h:.4f} m), speed along the slope at the first contact v0 sin beta = "
          f"{v0 * sb:.4f} m/s, gaining g sin beta T = {g * sb * T:.4f} m/s per hop, landing gap n: x_n = 8 n h sin "
          f"beta = {8 * h * sb:.4f} n m, total after {hops} hops {8 * h * sb * hops * (hops + 1) / 2:.4f} m along "
          f"the slope ({8 * h * sb * hops * (hops + 1) / 2 * cb:.4f} m across, {8 * h * sb * hops * (hops + 1) / 2 * sb:.4f} "
          f"m down), whole run {t_d + hops * T:.4f} s")
    segs = {name: flight_segments(man, name) for name in PANELS}
    for name in PANELS:
        S = segs[name]
        lines = []
        for k, s in enumerate(S):
            if k == 0:
                lines.append(f"first contact at {s['t1']:.4f} s at s = {s['s1']:.4f} m (residual off the plane "
                             f"{s['residual']:.1e} m), speed {s['speed_in']:.4f} m/s, along the surface {s['vt']:.4f} "
                             f"m/s, energy {s['E']:.4f} J/kg")
            else:
                gap = s["s1"] - S[k - 1]["s1"]
                cf = 8.0 * k * h * (sb if name == "slope" else 0.0)
                lines.append(f"hop {k}: {s['dur']:.4f} s (T = {T:.4f}), lands at {s['t1']:.4f} s at s = {s['s1']:.4f} m, "
                             f"gap {gap:.4f} m (closed form 8 n h sin beta = {cf:.4f}), ratio to gap 1 "
                             f"{gap / (S[1]['s1'] - S[0]['s1']) if name == 'slope' else 0.0:.4f}, hop height "
                             f"{s['apex_d']:.4f} m, along the surface {s['vt']:.4f} m/s, full speed {s['speed_in']:.4f} "
                             f"m/s, energy {s['E']:.4f} J/kg")
        print(f"{name} (event-driven, {hops} hops): " + "; ".join(lines))
        chk = check_rk4(man, name, segs[name])
        print(f"RK4 check, {name} ({chk['steps']} steps to landing {hops}): max |landing time - event| "
              f"{chk['max_t_err']:.2e} s, max |landing position - event| {chk['max_s_err']:.2e} m, max |speed along the "
              f"surface - event| {chk['max_vt_err']:.2e} m/s, max |full speed - event| {chk['max_speed_err']:.2e} m/s, "
              f"max |energy - g h| {chk['max_E_err']:.2e} J/kg (g h = {g * h:.4f}); landings at "
              + ", ".join(f"{a['t']:.4f} s / {a['s']:.4f} m" for a in chk["landings"]))
    S = segs["slope"]
    F = segs["floor"]
    gaps = [S[k]["s1"] - S[k - 1]["s1"] for k in range(1, hops + 1)]
    ratios = [gp / gaps[0] for gp in gaps]
    floor_gaps = [F[k]["s1"] - F[k - 1]["s1"] for k in range(1, hops + 1)]
    gaps_txt = ", ".join(f"{gp:.4f}" for gp in gaps)
    ratios_txt = " : ".join(f"{r:.4f}" for r in ratios)
    floor_txt = ", ".join(f"{gp:.4f}" for gp in floor_gaps)
    e_dev = max(abs(s["E"] - g * h) for s in S + F)
    print(f"result: slope gaps {gaps_txt} m = {ratios_txt}; floor gaps {floor_txt} m; every hop {T:.4f} s in both "
          f"panels; energy conserved at {g * h:.4f} J/kg (max deviation over the landings {e_dev:.1e})")
    ev = {"segs": segs, "gaps": gaps, "ratios": ratios, "T": T, "t_d": t_d, "v0": v0, "beta": beta,
          "t_end": S[-1]["t1"]}
    # Run schedule in video time.
    period, rel = man["run_period"], man["release_at"]
    n_runs = int(round(man["scene_duration"] / period))
    lines = []
    for r in range(n_runs):
        t0 = r * period + rel
        lines.append(f"run {r + 1}: release {t0:.2f} s; first contact {t0 + t_d * slow:.2f} s; landings "
                     + ", ".join(f"{t0 + S[k]['t1'] * slow:.2f}" for k in range(1, hops + 1))
                     + f" s (gaps {', '.join(f'{gp:.2f}' for gp in gaps)} m lit in turn); hold from "
                     f"{t0 + S[-1]['t1'] * slow:.2f} s; reset {r * period + period - man['reset_dur']:.2f} to "
                     f"{r * period + period:.2f} s")
    print(f"schedule ({n_runs} runs of {period:.4g} s at 1/{slow:g} speed, release {rel:g} s into each run, "
          f"each hop {T * slow:.2f} s of video, crossfade reset over the last {man['reset_dur']:g} s): "
          + "; ".join(lines))
    print(f"title until {man['title_until']:g} s; payoff card from {man['payoff_t']:g} s; loop fade {man['loop_fade']:g} s")
    # Text widths.
    font = os.environ["SEED_ZERO_FONT"]
    f24, f28, f30, f34, f36, f40, f56, f64 = (ImageFont.truetype(font, n) for n in (24, 28, 30, 34, 36, 40, 56, 64))
    widths = {"overlay@34": (f34, man["overlay"])}
    for j, line in enumerate(man["title"].split("|")):
        widths[f"title line {j + 1}@56"] = (f56, line)
    for name in PANELS:
        widths[f"label {name}@40"] = (f40, LABELS[name])
        widths[f"sublabel {name}@28"] = (f28, SUBLABELS[name])
        widths[f"speed line {name}@36"] = (f36, speed_line(name, S[-1]["vt"]))
    widths["gap label@28"] = (f28, "last gap")
    widths["big readout@64"] = (f64, f"{gaps[-1]:.2f} m")
    widths["clock line@36"] = (f36, clock_line(man, {"k": hops, "dt": T, "held": True}))
    widths["gap mark@30"] = (f30, f"{gaps[-1]:.2f} m")
    widths["same spot mark@30"] = (f30, "same spot")
    widths["hop mark@24"] = (f24, f"{T:.2f} s")
    widths["drop label@24"] = (f24, f"{h * 100:.0f} cm")
    for j, line in enumerate(payoff_lines(man, ev)):
        widths[f"payoff line {j + 1}@40"] = (f40, line)
    print("text widths: " + ", ".join(f"{k} {f.getlength(s):.0f} px" for k, (f, s) in widths.items()))
    return ev


LABELS = {"slope": "on a 14.5 degree slope", "floor": "on a flat floor"}
SUBLABELS = {"slope": "dropped 20 cm, perfect bounces", "floor": "the same ball, the same drop"}


def speed_line(name: str, vt: float) -> str:
    return f"along the {'slope' if name == 'slope' else 'floor'} {vt:.2f} m/s"


def clock_line(man: dict, st: dict) -> str:
    if st["k"] == 0:
        return f"drop: {st['dt']:.2f} s"
    return f"hop {st['k']} of {man['hops']}: {st['dt']:.2f} s"


def payoff_lines(man: dict, ev: dict) -> list[str]:
    g = ev["gaps"]
    text = man["payoff_text"].format(g1=g[0], g2=g[1], g3=g[2], g4=g[3], T=ev["T"])
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
        self.font_mark = ImageFont.truetype(font, 30)
        self.font_read = ImageFont.truetype(font, 36)
        self.font_num = ImageFont.truetype(font, 64)
        self.font_tiny = ImageFont.truetype(font, 24)
        self.ppm = float(man["px_per_m"])
        self.ball_r = float(man["ball_radius_px"])
        self.first = None
        self.start_state = None
        self.slow = float(man["slow_factor"])

    # --- geometry helpers -------------------------------------------------
    def real_time(self, tau: float) -> float:
        return max(0.0, tau - self.man["release_at"]) / self.slow

    def state(self, name: str, tau: float) -> dict:
        return state_at(self.man, name, self.ev["segs"][name], self.real_time(tau))

    def P(self, name: str, x: float, y: float) -> tuple[float, float]:
        """Frame coordinates of a point in metres (the first contact point at the panel origin)."""
        ox, oy = PANELS[name]["origin"]
        return ox + x * self.ppm, oy - y * self.ppm

    def L(self, name: str, x: float, y: float) -> tuple[float, float]:
        """Layer coordinates (supersampled, y relative to GEOM_Y0) of a point in metres."""
        px, py = self.P(name, x, y)
        return px * SS, (py - GEOM_Y0) * SS

    def plane_point(self, name: str, s: float, depth_px: float = 0.0) -> tuple[float, float]:
        """Frame coordinates of the point s metres along the surface, depth_px below it along the normal."""
        sb, cb = basis(self.man, name)
        px, py = self.P(name, s * cb, -s * sb)
        return px + depth_px * (-sb), py + depth_px * cb

    def centre_offset(self, name: str) -> tuple[float, float]:
        """The drawn ball sits on the surface: its centre is the point plus the radius along the normal (frame px)."""
        sb, cb = basis(self.man, name)
        return self.ball_r * sb, -self.ball_r * cb

    # --- drawing ----------------------------------------------------------
    @staticmethod
    def arrow(d: ImageDraw.ImageDraw, x0: float, y0: float, x1: float, y1: float, fill, width: int) -> None:
        d.line((x0, y0, x1, y1), fill=fill, width=width)
        ang = math.atan2(y1 - y0, x1 - x0)
        h = 7.0 * width
        for s in (-1, 1):
            a = ang + s * math.radians(150)
            d.line((x1, y1, x1 + h * math.cos(a), y1 + h * math.sin(a)), fill=fill, width=width)

    def draw_panel_geometry(self, d: ImageDraw.ImageDraw, name: str, st: dict, tau: float) -> None:
        man, ev = self.man, self.ev
        col = PANELS[name]["colour"]
        segs = ev["segs"][name]
        sb, cb = basis(man, name)
        ox, oy = PANELS[name]["origin"]
        h = float(man["drop_height_m"])
        # The surface: a slab across the panel width, the surface line on top.
        x_left, x_right = 40.0, float(W - 40)
        s_left, s_right = (x_left - ox) / (self.ppm * cb), (x_right - ox) / (self.ppm * cb)
        p0, p1 = self.plane_point(name, s_left), self.plane_point(name, s_right)
        q0, q1 = self.plane_point(name, s_left, SLAB_PX), self.plane_point(name, s_right, SLAB_PX)
        to_layer = lambda p: (p[0] * SS, (p[1] - GEOM_Y0) * SS)
        d.polygon([to_layer(p0), to_layer(p1), to_layer(q1), to_layer(q0)], fill=GROUND)
        d.line((*to_layer(p0), *to_layer(p1)), fill=WIRE, width=3 * SS)
        # The drop height bracket beside the release point.
        bx = (ox - 24.0) * SS
        ytop, ybot = self.L(name, 0.0, h)[1], self.L(name, 0.0, 0.0)[1]
        d.line((bx, ytop, bx, ybot), fill=blend(MUTED, 0.8), width=SS)
        for yy in (ytop, ybot):
            d.line((bx - 5 * SS, yy, bx + 5 * SS, yy), fill=blend(MUTED, 0.8), width=SS)
        # Landing ticks, gap bars and landing pulses.
        offx, offy = self.centre_offset(name)
        for k, seg in enumerate(segs):
            if st["t"] < seg["t1"] - 1e-12 and not (st["held"] and k == len(segs) - 1):
                break
            a, b = self.plane_point(name, seg["s1"]), self.plane_point(name, seg["s1"], TICK_PX)
            d.line((*to_layer(a), *to_layer(b)), fill=GOLD, width=3 * SS)
            if k > 0 and name == "slope":
                c = self.plane_point(name, segs[k - 1]["s1"], TICK_PX)
                d.line((*to_layer(c), *to_layer(b)), fill=blend(GOLD, 0.8), width=2 * SS)
            age = (st["t"] - seg["t1"]) * self.slow  # video seconds since the landing
            if 0.0 <= age < 0.5:
                u = age / 0.5
                r = (10.0 + 30.0 * u) * SS
                cx, cy = self.L(name, seg["x1"], seg["y1"])
                cx, cy = cx + offx * SS, cy + offy * SS
                d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=blend(GOLD, 0.9 * (1.0 - u)), width=3 * SS)
        # The path so far: faint and persistent, bright over the last trail_s of video time.
        n = 300
        t_now = st["t"]
        pts = []
        k_end = int(math.ceil(t_now * n))
        for j in range(0, k_end + 1):
            tk = min(j / n, t_now)
            s = state_at(man, name, segs, tk)
            x, y = self.L(name, s["x"], s["y"])
            pts.append((tk, (x + offx * SS, y + offy * SS)))
        for (t0, p0), (t1, p1) in zip(pts, pts[1:]):
            age = (t_now - t1) * self.slow
            if age < man["trail_s"]:
                alpha = 0.35 + 0.65 * (1.0 - age / man["trail_s"])
            else:
                alpha = 0.3
            d.line((p0, p1), fill=blend(col, alpha), width=3 * SS)
        # Velocity arrow and the ball.
        px, py = self.L(name, st["x"], st["y"])
        px, py = px + offx * SS, py + offy * SS
        speed = st["speed"]
        if speed > 0.0 and not st["held"]:
            ln = min(120.0, 24.0 * speed) * SS
            wx, wy = st["vx"] / speed, -st["vy"] / speed
            x0, y0 = px + wx * (self.ball_r + 2) * SS, py + wy * (self.ball_r + 2) * SS
            self.arrow(d, x0, y0, x0 + wx * ln, y0 + wy * ln, blend(WHITE, 0.85), 2 * SS)
        r = self.ball_r * SS
        d.ellipse((px - r, py - r, px + r, py + r), fill=GOLD, outline=(120, 84, 30), width=SS)
        hr = r * 0.32
        d.ellipse((px - r * 0.45 - hr, py - r * 0.45 - hr, px - r * 0.45 + hr, py - r * 0.45 + hr), fill=WHITE)

    def draw_panel_text(self, d: ImageDraw.ImageDraw, name: str, st: dict) -> None:
        man, ev = self.man, self.ev
        col = PANELS[name]["colour"]
        top = PANELS[name]["top"]
        segs = ev["segs"][name]
        h = float(man["drop_height_m"])
        hops = int(man["hops"])
        # The drop label above the release point.
        rx, ry = self.P(name, 0.0, h)
        offx, offy = self.centre_offset(name)
        d.text((rx + offx, ry + offy - self.ball_r - 22), f"{h * 100:.0f} cm", font=self.font_tiny,
               fill=blend(MUTED, 0.9), anchor="mm")
        # The readout column.
        d.text((COL_X, top + 24), LABELS[name], font=self.font, fill=col, anchor="rm")
        d.text((COL_X, top + 58), SUBLABELS[name], font=self.font_small, fill=MUTED, anchor="rm")
        d.text((COL_X, top + 100), "last gap", font=self.font_small, fill=MUTED, anchor="rm")
        landed = st["landings"]  # completed contacts: 1 after the first contact, 2 after hop 1, ...
        if landed >= 2:
            k = landed - 1
            gap = segs[k]["s1"] - segs[k - 1]["s1"]
            flash = 0.0 <= (st["t"] - segs[k]["t1"]) * self.slow < 0.6
            d.text((COL_X, top + 146), f"{gap:.2f} m", font=self.font_num, fill=GOLD if flash else TEXT, anchor="rm")
        else:
            d.text((COL_X, top + 146), "--", font=self.font_num, fill=MUTED, anchor="rm")
        d.text((COL_X, top + 208), clock_line(man, st), font=self.font_read,
               fill=GOLD if st["held"] else TEXT, anchor="rm")
        d.text((COL_X, top + 246), speed_line(name, st["vt"]), font=self.font_read, fill=TEXT, anchor="rm")
        # Gap marks under the surface: the gap and the hop time, once the hop has landed.
        for k in range(1, hops + 1):
            seg = segs[k]
            if st["t"] < seg["t1"] - 1e-12 and not (st["held"] and k == hops):
                break
            if name == "slope":
                mid = 0.5 * (segs[k - 1]["s1"] + seg["s1"])
                gx, gy = self.plane_point(name, mid, GAP_LABEL_PX)
                hx, hy = self.plane_point(name, mid, HOP_LABEL_PX)
                d.text((gx, gy), f"{seg['s1'] - segs[k - 1]['s1']:.2f} m", font=self.font_mark, fill=GOLD, anchor="mm")
                d.text((hx, hy), f"{seg['dur']:.2f} s", font=self.font_tiny, fill=MUTED, anchor="mm")
            elif k == 1:
                gx, gy = self.plane_point(name, 0.0, GAP_LABEL_PX)
                hx, hy = self.plane_point(name, 0.0, HOP_LABEL_PX)
                d.text((gx, gy), "same spot", font=self.font_mark, fill=GOLD, anchor="mm")
                d.text((hx, hy), f"every hop {seg['dur']:.2f} s", font=self.font_tiny, fill=MUTED, anchor="mm")

    def draw_state(self, tau: float) -> np.ndarray:
        """The full frame for run time tau, without title or card."""
        img = Image.new("RGB", (W, H), BG)
        layer = Image.new("RGB", (W * SS, (GEOM_Y1 - GEOM_Y0) * SS), BG)
        ld = ImageDraw.Draw(layer)
        sep = (PANELS["floor"]["top"] - GEOM_Y0) * SS
        ld.line((40 * SS, sep, (W - 40) * SS, sep), fill=SEP, width=2 * SS)
        states = {name: self.state(name, tau) for name in PANELS}
        for name in PANELS:
            self.draw_panel_geometry(ld, name, states[name], tau)
        img.paste(layer.reduce(SS), (0, GEOM_Y0))
        d = ImageDraw.Draw(img)
        for name in PANELS:
            self.draw_panel_text(d, name, states[name])
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
    man = json.loads((ROOT / "projects/bounceslope/manifest.json").read_text())
    ev = measure(man)
    if "--measure-only" in sys.argv:
        return
    if "--frames" in sys.argv:
        times = [float(v) for v in sys.argv[sys.argv.index("--frames") + 1].split(",")]
        r = Renderer(man, ev)
        (ROOT / "media/bounceslope").mkdir(parents=True, exist_ok=True)
        for tv in times:
            Image.fromarray(r.frame_at(int(round(tv * man["fps"])))).save(ROOT / f"media/bounceslope/smoke-{tv}.png")
        print("smoke frames: " + ", ".join(f"{tv}" for tv in times))
        return
    Renderer(man, ev).render(ROOT / "media/bounceslope/footage.mp4")


if __name__ == "__main__":
    main()
