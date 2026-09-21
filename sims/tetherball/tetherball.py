#!/usr/bin/env python3
"""Tetherball versus hole: the string gets shorter. Does the puck speed up?

A puck on frictionless ice circles at v0 = 1 m/s on a string of length
L0 = 0.5 m. Two panels, the same puck, released at the same instant and
drawn at the same scale. Top: the string runs through a hole in the ice
and is pulled in at u = 10 cm/s (r = L0 - u t); the pull is central, so
the angular momentum r v_t = L0 v0 is conserved, v_t = L0 v0 / r, and the
speed doubles by r = L0 / 2; the pull stops at r = 5 cm and the puck
keeps circling there. Bottom: the string wraps a fixed pole of radius
a = 2.5 cm (tetherball), so the puck runs on the involute of the pole
circle; the free length l obeys l dl/dt = -a v0 (l^2 = L0^2 - 2 a v0 t),
and the string, always at a right angle to the motion, does no work: the
speed stays v0 until the puck reaches the pole. The hole is on top
because its half-string moment comes first (2.5 s against 3.75 s), so the
narration reads the panels top to bottom and ends on the surprise. Both
runs are drawn from the closed forms and checked against a Cartesian RK4
integration of the puck under the string force (T = m v^2 / l toward the
tangent point for the pole, T = m v_t^2 / r toward the hole). The puck is
a point for every number and is drawn larger than life. Played at 1/3.5
speed, two runs of 20 s with a short crossfade reset. Deterministic, no
seed.

Measured and printed: for the pole the time, turns and speed at half the
string and at the pole, the wrapped turns, the energy and the angular
momentum about the pole; for the hole the time, turns, tangential and
full speed at half the string and at the 5 cm stop, the energy rise and
the angular momentum; the RK4 checks of both closed forms; the run
schedule in video time; the on-screen text widths.

usage: tetherball.py [--measure-only] [--frames t1,t2,...]
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

# Layout: overlay at y 96 (captions.py), title rows at y 190/252 for the
# first seconds, two panels of 543 px from y 350 (top: hole, bottom: pole)
# with the orbit centred at x 372 and a right-aligned readout column at
# x 1040, captions at caption_y 0.75 (y 1440..1520), payoff card under
# them from y 1592.
GEOM_Y0, GEOM_Y1 = 350, 1436
PANEL_H = (GEOM_Y1 - GEOM_Y0) // 2
ORBIT_CX = 372.0
COL_X = W - 40
PANELS = {"hole": {"index": 0, "colour": CORAL}, "pole": {"index": 1, "colour": TEAL}}
SS = 2
PAYOFF_Y = 1592.0
TAU = 2.0 * math.pi


def blend(col, a, base=BG):
    return tuple(int(round(c * a + b * (1 - a))) for c, b in zip(col, base))


def smoothstep(u: float) -> float:
    u = max(0.0, min(1.0, u))
    return u * u * (3 - 2 * u)


# --- closed forms -----------------------------------------------------------
def pole_state(man: dict, t: float) -> dict:
    """Puck on the involute of the pole at real time t (y up, pole centre at the origin)."""
    L0, a, v0 = man["string_length_m"], man["pole_radius_m"], man["start_speed_m_s"]
    l2 = L0 * L0 - 2.0 * a * v0 * t
    hit = l2 <= 0.0
    l = 0.0 if hit else math.sqrt(l2)
    phi = (L0 - l) / a  # angle of the tangent point, also the wrapped angle
    cx, cy = a * math.cos(phi), a * math.sin(phi)
    ux, uy = -math.sin(phi), math.cos(phi)
    x, y = cx + l * ux, cy + l * uy
    if hit:
        vx = vy = 0.0
        speed = 0.0
    else:
        vx, vy = -v0 * math.cos(phi), -v0 * math.sin(phi)
        speed = v0
    turns = (phi + math.atan2(l, a) - math.atan2(L0, a)) / TAU
    return {"x": x, "y": y, "vx": vx, "vy": vy, "l": l, "phi": phi, "cx": cx, "cy": cy, "speed": speed,
            "turns": turns, "wrap_turns": phi / TAU, "Lz": v0 * l, "E": 0.5 * speed * speed, "hit": hit, "t": t}


def hole_state(man: dict, t: float) -> dict:
    """Puck reeled through the hole at real time t (y up, hole at the origin)."""
    L0, u, v0, r_stop = man["string_length_m"], man["reel_rate_m_s"], man["start_speed_m_s"], man["hole_stop_m"]
    Lz = L0 * v0
    t_stop = (L0 - r_stop) / u
    th0 = 0.5 * math.pi
    if t < t_stop:
        r = L0 - u * t
        th = th0 + (Lz / u) * (1.0 / r - 1.0 / L0)
        vr = -u
        stopped = False
    else:
        r = r_stop
        th = th0 + (Lz / u) * (1.0 / r_stop - 1.0 / L0) + (Lz / (r_stop * r_stop)) * (t - t_stop)
        vr = 0.0
        stopped = True
    vt = Lz / r
    c, s = math.cos(th), math.sin(th)
    x, y = r * c, r * s
    vx, vy = vr * c - vt * s, vr * s + vt * c
    speed = math.hypot(vt, vr)
    return {"x": x, "y": y, "vx": vx, "vy": vy, "r": r, "theta": th, "vt": vt, "vr": vr, "speed": speed,
            "turns": (th - th0) / TAU, "Lz": r * vt, "E": 0.5 * speed * speed, "stopped": stopped, "t": t}


# --- RK4 checks -------------------------------------------------------------
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


def check_pole(man: dict, l_end: float) -> dict:
    """Cartesian RK4 of the puck pulled by T = v^2 / l toward the tangent point on the pole."""
    L0, a, v0, steps = man["string_length_m"], man["pole_radius_m"], man["start_speed_m_s"], man["steps_per_second"]
    half = man["half_string_m"]
    dt = 1.0 / steps

    def acc(x, y, vx, vy):
        R = math.hypot(x, y)
        l = math.sqrt(max(R * R - a * a, 1e-18))
        phi = math.atan2(y, x) - math.acos(min(1.0, a / R))
        cx, cy = a * math.cos(phi), a * math.sin(phi)
        T = (vx * vx + vy * vy) / l
        return T * (cx - x) / l, T * (cy - y) / l

    st = (a, L0, -v0, 0.0)
    t = 0.0
    out = {"max_l_err": 0.0, "max_speed_err": 0.0, "max_L_err": 0.0, "half": None}
    prev = None
    while True:
        x, y, vx, vy = st
        R = math.hypot(x, y)
        l = math.sqrt(max(R * R - a * a, 0.0))
        l_cf = math.sqrt(max(L0 * L0 - 2.0 * a * v0 * t, 0.0))
        speed = math.hypot(vx, vy)
        Lz = x * vy - y * vx
        out["max_l_err"] = max(out["max_l_err"], abs(l - l_cf))
        out["max_speed_err"] = max(out["max_speed_err"], abs(speed - v0))
        out["max_L_err"] = max(out["max_L_err"], abs(Lz - v0 * l_cf))
        if prev is not None and out["half"] is None and prev[1] > half >= l:
            f = (prev[1] - half) / (prev[1] - l)
            out["half"] = {"t": prev[0] + f * dt, "speed": prev[2] + f * (speed - prev[2]), "Lz": prev[3] + f * (Lz - prev[3])}
        if l <= l_end:
            out["end"] = {"t": t, "l": l, "speed": speed, "Lz": Lz, "E": 0.5 * speed * speed}
            break
        prev = (t, l, speed, Lz)
        st = rk4(acc, st, dt)
        t += dt
    out["steps"] = int(round(t / dt))
    return out


def check_hole(man: dict) -> dict:
    """Cartesian RK4 of the puck pulled by T = v_t^2 / r toward the hole, until r = hole_stop."""
    L0, u, v0, steps = man["string_length_m"], man["reel_rate_m_s"], man["start_speed_m_s"], man["steps_per_second"]
    r_stop, half = man["hole_stop_m"], man["half_string_m"]
    Lz0 = L0 * v0
    dt = 1.0 / steps

    def acc(x, y, vx, vy):
        r = math.hypot(x, y)
        ex, ey = x / r, y / r
        vt = -vx * ey + vy * ex
        T = vt * vt / r
        return -T * ex, -T * ey

    st = (0.0, L0, -v0, -u)
    t = 0.0
    out = {"max_r_err": 0.0, "max_vr_err": 0.0, "max_L_err": 0.0, "half": None}
    prev = None
    th_prev = 0.5 * math.pi
    th_unwrapped = 0.5 * math.pi
    while True:
        x, y, vx, vy = st
        r = math.hypot(x, y)
        ex, ey = x / r, y / r
        vr = vx * ex + vy * ey
        vt = -vx * ey + vy * ex
        Lz = x * vy - y * vx
        th = math.atan2(y, x)
        d = (th - th_prev + math.pi) % TAU - math.pi
        th_unwrapped += d
        th_prev = th
        r_cf = L0 - u * t
        speed = math.hypot(vx, vy)
        out["max_r_err"] = max(out["max_r_err"], abs(r - r_cf))
        out["max_vr_err"] = max(out["max_vr_err"], abs(vr + u))
        out["max_L_err"] = max(out["max_L_err"], abs(Lz - Lz0))
        rec = (t, r, speed, vt, Lz, th_unwrapped)
        if prev is not None and out["half"] is None and prev[1] > half >= r:
            f = (prev[1] - half) / (prev[1] - r)
            out["half"] = {k: prev[i] + f * (rec[i] - prev[i]) for k, i in
                           (("t", 0), ("speed", 2), ("vt", 3), ("Lz", 4), ("theta", 5))}
        if r <= r_stop:
            out["end"] = {"t": t, "r": r, "speed": speed, "vt": vt, "Lz": Lz, "theta": th_unwrapped, "E": 0.5 * speed * speed}
            break
        prev = rec
        st = rk4(acc, st, dt)
        t += dt
    out["steps"] = int(round(t / dt))
    return out


# --- measurement --------------------------------------------------------------
def measure(man: dict) -> dict:
    L0, a, v0 = man["string_length_m"], man["pole_radius_m"], man["start_speed_m_s"]
    u, r_stop, half = man["reel_rate_m_s"], man["hole_stop_m"], man["half_string_m"]
    steps, slow, fps = man["steps_per_second"], man["slow_factor"], man["fps"]
    ppm = man["px_per_m"]
    print(f"setup: a puck on frictionless ice at v0 = {v0:g} m/s on a string of L0 = {L0:g} m, released at the same "
          f"instant in two panels at the same scale ({ppm:g} px per metre, string {L0 * ppm:.0f} px); top: the string "
          f"runs through a hole and is pulled in at u = {u:g} m/s (r = L0 - u t) until r = {r_stop:g} m, then held; "
          f"bottom: the string wraps a fixed pole of radius a = {a:g} m ({a * ppm:.0f} px), the puck runs on the "
          f"involute of the pole circle, free length l with l dl/dt = -a v0; both drawn from the closed forms and "
          f"checked by a Cartesian RK4 of the puck under the string force at {steps} steps per second "
          f"(dt = {1 / steps:.2e} s); the puck is a point for every number; played at 1/{slow:g} speed; "
          f"deterministic, no seed")
    # Pole closed forms.
    t_half_p = (L0 * L0 - half * half) / (2.0 * a * v0)
    t_hit = L0 * L0 / (2.0 * a * v0)
    ph = pole_state(man, t_half_p)
    pe = pole_state(man, t_hit)
    print(f"pole (closed form, l^2 = L0^2 - 2 a v0 t): the string is at half length l = {half:g} m at "
          f"{t_half_p:.4f} s, speed {ph['speed']:.4f} m/s, {ph['turns']:.4f} turns of the puck about the pole "
          f"({ph['wrap_turns']:.4f} turns of string on the pole, {ph['phi']:.4f} rad); the puck reaches the pole "
          f"(l = 0) at {t_hit:.4f} s after {pe['turns']:.4f} turns ({pe['wrap_turns']:.4f} turns of string, "
          f"{pe['phi']:.4f} rad) at {v0:.4f} m/s all the way; kinetic energy {0.5 * v0 * v0:.4f} J/kg throughout "
          f"(the tension is at a right angle to the velocity, no work); angular momentum about the pole centre "
          f"v0 l: {v0 * L0:.4f} at the start, {ph['Lz']:.4f} at half, 0 at the pole (the tension is tangent to "
          f"the pole, so it has a torque about the centre); the pole holds the puck from {t_hit:.4f} s")
    # Hole closed forms.
    t_half_h = (L0 - half) / u
    t_stop = (L0 - r_stop) / u
    hh = hole_state(man, t_half_h)
    he = hole_state(man, t_stop)
    h0 = hole_state(man, 0.0)
    print(f"hole (closed form, r = L0 - u t, r v_t = L0 v0 = {L0 * v0:.4f} m^2/s): at the start v_t = {v0:.4f} m/s, "
          f"radial {u:g} m/s inward, full speed {h0['speed']:.4f} m/s; the string is at half length r = {half:g} m at "
          f"{t_half_h:.4f} s: tangential speed {hh['vt']:.4f} m/s, full speed {hh['speed']:.4f} m/s "
          f"({hh['speed'] / h0['speed']:.4f} x the start), {hh['turns']:.4f} turns; at r = {r_stop:g} m at "
          f"{t_stop:.4f} s: tangential {he['vt']:.4f} m/s, full {he['speed']:.4f} m/s, {he['turns']:.4f} turns "
          f"({he['theta'] - 0.5 * math.pi:.4f} rad); the pull then stops and the puck circles at {r_stop:g} m at "
          f"{he['vt']:.4f} m/s ({he['vt'] / r_stop / TAU:.2f} turns per second); kinetic energy {h0['E']:.4f} J/kg "
          f"at the start, {hh['E']:.4f} at half ({hh['E'] / h0['E']:.3f} x), {he['E']:.4f} at the stop; work done by "
          f"the string {hh['E'] - h0['E']:.4f} J/kg by half and {he['E'] - h0['E']:.4f} by the stop; angular momentum "
          f"{h0['Lz']:.4f} = {hh['Lz']:.4f} = {he['Lz']:.4f} m^2/s (conserved, the pull is central)")
    # RK4 checks.
    l_end = man["hole_stop_m"]
    cp = check_pole(man, l_end)
    print(f"RK4 check, pole (Cartesian, T = v^2 / l toward the tangent point, {cp['steps']} steps to l = {l_end:g} m): "
          f"max |l - closed form| {cp['max_l_err']:.2e} m, max |speed - v0| {cp['max_speed_err']:.2e} m/s, max "
          f"|angular momentum - v0 l| {cp['max_L_err']:.2e}; at half the string t = {cp['half']['t']:.4f} s "
          f"(closed form {t_half_p:.4f}), speed {cp['half']['speed']:.6f} m/s; at l = {cp['end']['l']:.4f} m t = "
          f"{cp['end']['t']:.4f} s (closed form {(L0 * L0 - l_end * l_end) / (2 * a * v0):.4f}), speed "
          f"{cp['end']['speed']:.6f} m/s, energy {cp['end']['E']:.6f} J/kg")
    ch = check_hole(man)
    th_half_cf = (L0 * v0 / u) * (1.0 / half - 1.0 / L0)
    th_end_cf = (L0 * v0 / u) * (1.0 / r_stop - 1.0 / L0)
    print(f"RK4 check, hole (Cartesian, T = v_t^2 / r toward the hole, {ch['steps']} steps to r = {r_stop:g} m): "
          f"max |r - (L0 - u t)| {ch['max_r_err']:.2e} m, max |radial speed + u| {ch['max_vr_err']:.2e} m/s, max "
          f"|angular momentum - L0 v0| {ch['max_L_err']:.2e}; at half the string t = {ch['half']['t']:.4f} s "
          f"(closed form {t_half_h:.4f}), tangential {ch['half']['vt']:.6f} m/s, full {ch['half']['speed']:.6f} m/s, "
          f"angle {ch['half']['theta'] - 0.5 * math.pi:.6f} rad (closed form {th_half_cf:.6f}); at r = {r_stop:g} m "
          f"t = {ch['end']['t']:.4f} s (closed form {t_stop:.4f}), tangential {ch['end']['vt']:.6f} m/s, full "
          f"{ch['end']['speed']:.6f} m/s, angle {ch['end']['theta'] - 0.5 * math.pi:.6f} rad (closed form "
          f"{th_end_cf:.6f}), energy {ch['end']['E']:.6f} J/kg")
    ev = {"t_half_pole": t_half_p, "t_hit": t_hit, "t_half_hole": t_half_h, "t_stop": t_stop,
          "v_pole_half": ph["speed"], "v_hole_half": hh["speed"], "vt_hole_half": hh["vt"], "v_hole_stop": he["speed"],
          "turns_pole_half": ph["turns"], "turns_pole_hit": pe["turns"], "wrap_hit": pe["wrap_turns"],
          "turns_hole_half": hh["turns"], "turns_hole_stop": he["turns"],
          "pos_half_pole": (ph["x"], ph["y"]), "pos_half_hole": (hh["x"], hh["y"])}
    # Run schedule in video time.
    period, rel = man["run_period"], man["release_at"]
    n_runs = int(round(man["scene_duration"] / period))
    lines = []
    for r in range(n_runs):
        t0 = r * period + rel
        lines.append(f"run {r + 1}: release {t0:.2f} s; hole puck at half string {t0 + t_half_h * slow:.2f} s, pole puck "
                     f"at half string {t0 + t_half_p * slow:.2f} s, hole pull stops {t0 + t_stop * slow:.2f} s, pole puck "
                     f"hits the pole {t0 + t_hit * slow:.2f} s; reset {r * period + period - man['reset_dur']:.2f} to "
                     f"{r * period + period:.2f} s")
    print(f"schedule ({n_runs} runs of {period:g} s at 1/{slow:g} speed, release {rel:g} s into each run, crossfade "
          f"reset over the last {man['reset_dur']:g} s): " + "; ".join(lines))
    print(f"title until {man['title_until']:g} s; payoff card from {man['payoff_t']:g} s; loop fade {man['loop_fade']:g} s")
    # Text widths.
    font = os.environ["SEED_ZERO_FONT"]
    f34, f56, f40, f28, f32, f36, f64, f24 = (ImageFont.truetype(font, n) for n in (34, 56, 40, 28, 32, 36, 64, 24))
    widths = {"overlay@34": (f34, man["overlay"])}
    for j, line in enumerate(man["title"].split("|")):
        widths[f"title line {j + 1}@56"] = (f56, line)
    widths["label pole@40"] = (f40, LABELS["pole"])
    widths["label hole@40"] = (f40, LABELS["hole"])
    widths["sublabel pole@28"] = (f28, sublabel(man, "pole"))
    widths["sublabel hole@28"] = (f28, sublabel(man, "hole"))
    widths["speed label@28"] = (f28, "speed")
    widths["readout@64"] = (f64, f"{he['speed']:.2f} m/s")
    widths["string readout@36"] = (f36, f"string {L0 * 100:.1f} cm")
    widths["turns readout@36"] = (f36, f"turns {he['turns']:.2f}")
    widths["half mark pole@32"] = (f32, half_mark(man, ev, "pole"))
    widths["half mark hole@32"] = (f32, half_mark(man, ev, "hole"))
    widths["end mark pole@32"] = (f32, end_mark(man, ev, "pole"))
    widths["end mark hole@32"] = (f32, end_mark(man, ev, "hole"))
    widths["ring label@24"] = (f24, f"{L0 * 100:.0f} cm")
    for j, line in enumerate(payoff_lines(man, ev)):
        widths[f"payoff line {j + 1}@40"] = (f40, line)
    print("text widths: " + ", ".join(f"{k} {f.getlength(s):.0f} px" for k, (f, s) in widths.items()))
    return ev


LABELS = {"pole": "string wraps a pole", "hole": "string pulled through a hole"}


def sublabel(man: dict, name: str) -> str:
    if name == "pole":
        return f"pole radius {man['pole_radius_m'] * 100:g} cm"
    return f"pulled in at {man['reel_rate_m_s'] * 100:g} cm/s"


def half_mark(man: dict, ev: dict, name: str) -> str:
    v = ev["v_pole_half"] if name == "pole" else ev["v_hole_half"]
    return f"at {man['half_string_m'] * 100:g} cm: {v:.2f} m/s"


def end_mark(man: dict, ev: dict, name: str) -> str:
    if name == "pole":
        return f"hit the pole: {man['start_speed_m_s']:.2f} m/s"
    return f"held at {man['hole_stop_m'] * 100:g} cm: {ev['v_hole_stop']:.2f} m/s"


def payoff_lines(man: dict, ev: dict) -> list[str]:
    text = man["payoff_text"].format(v_pole=ev["v_pole_half"], v_hole=ev["v_hole_half"])
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
        self.font_mark = ImageFont.truetype(font, 32)
        self.font_read = ImageFont.truetype(font, 36)
        self.font_num = ImageFont.truetype(font, 64)
        self.font_ring = ImageFont.truetype(font, 24)
        self.ppm = float(man["px_per_m"])
        self.puck_r = float(man["puck_radius_px"])
        self.first = None
        self.start_state = None
        self.slow = float(man["slow_factor"])

    # --- geometry helpers -------------------------------------------------
    def centre(self, name: str) -> tuple[float, float]:
        return ORBIT_CX, GEOM_Y0 + PANELS[name]["index"] * PANEL_H + PANEL_H / 2.0

    def real_time(self, tau: float) -> float:
        return max(0.0, tau - self.man["release_at"]) / self.slow

    def state(self, name: str, tau: float) -> dict:
        tp = self.real_time(tau)
        return pole_state(self.man, tp) if name == "pole" else hole_state(self.man, tp)

    def L(self, name: str, x: float, y: float) -> tuple[float, float]:
        """Layer coordinates (supersampled, y relative to GEOM_Y0) of a point in metres."""
        cx, cy = self.centre(name)
        return (cx + x * self.ppm) * SS, (cy - GEOM_Y0 - y * self.ppm) * SS

    # --- drawing ----------------------------------------------------------
    @staticmethod
    def dashed_ring(d: ImageDraw.ImageDraw, cx: float, cy: float, r: float, fill, width: int, n: int = 48) -> None:
        step = 360.0 / n
        for k in range(n):
            d.arc((cx - r, cy - r, cx + r, cy + r), start=k * step, end=k * step + step * 0.55, fill=fill, width=width)

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
        L0, a, half = man["string_length_m"], man["pole_radius_m"], man["half_string_m"]
        cx, cy = self.L(name, 0.0, 0.0)
        # Reference rings: the start orbit and the half-string ring.
        for rad, alpha in ((L0, 0.55), (half, 0.4)):
            self.dashed_ring(d, cx, cy, rad * self.ppm * SS, blend(MUTED, alpha), 2 * SS)
        # The half-string mark: a solid gold ring and a dot where the puck was, once the event has happened.
        t_half = ev["t_half_pole"] if name == "pole" else ev["t_half_hole"]
        if st["t"] >= t_half:
            u = smoothstep((st["t"] - t_half) / 0.15)
            r = half * self.ppm * SS
            d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=blend(GOLD, 0.85 * u), width=3 * SS)
            hx, hy = self.L(name, *(ev["pos_half_pole"] if name == "pole" else ev["pos_half_hole"]))
            rr = 7 * SS
            d.ellipse((hx - rr, hy - rr, hx + rr, hy + rr), fill=blend(GOLD, u))
        # Trail: the path over the last trail_s of video time, fading.
        n = 240
        pts = []
        for k in range(n, -1, -1):
            tk = tau - man["trail_s"] * k / n
            if tk < man["release_at"]:
                continue
            s = self.state(name, tk)
            pts.append((k, self.L(name, s["x"], s["y"])))
        for (k0, p0), (k1, p1) in zip(pts, pts[1:]):
            alpha = 0.12 + 0.88 * (1.0 - k1 / n)
            d.line((p0, p1), fill=blend(col, alpha), width=3 * SS)
        # Anchor: the pole with its wrapped string, or the hole.
        px, py = self.L(name, st["x"], st["y"])
        if name == "pole":
            rp = a * self.ppm * SS
            d.ellipse((cx - rp, cy - rp, cx + rp, cy + rp), fill=WIRE, outline=MUTED, width=SS)
            phi = st["phi"]
            n_full = int(phi // TAU)
            rem = phi - n_full * TAU
            for k in range(n_full):
                rr = rp + (3 + 2.5 * k) * SS
                d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), outline=col, width=2 * SS)
            rr = rp + (3 + 2.5 * n_full) * SS
            if rem > 1e-6:
                d.arc((cx - rr, cy - rr, cx + rr, cy + rr), start=-math.degrees(rem), end=0.0, fill=col, width=2 * SS)
            # The free string leaves the outermost wrap at the tangent point.
            ax, ay = cx + rr * math.cos(phi), cy - rr * math.sin(phi)
            if not st["hit"]:
                d.line((ax, ay, px, py), fill=col, width=3 * SS)
        else:
            rh = 7 * SS
            d.line((cx, cy, px, py), fill=col, width=3 * SS)
            d.ellipse((cx - rh, cy - rh, cx + rh, cy + rh), fill=(4, 6, 8), outline=col, width=2 * SS)
        # Velocity arrow and, on the pole, the right angle between the string and the motion.
        speed = st["speed"]
        if speed > 0.0:
            ln = min(120.0, 40.0 * speed) * SS
            wx, wy = st["vx"] / speed, -st["vy"] / speed
            x0, y0 = px + wx * (self.puck_r + 2) * SS, py + wy * (self.puck_r + 2) * SS
            self.arrow(d, x0, y0, x0 + wx * ln, y0 + wy * ln, blend(WHITE, 0.85), 2 * SS)
            if name == "pole":
                sx, sy = ax - px, ay - py
                sl = math.hypot(sx, sy)
                if sl > 1e-9:
                    sx, sy = sx / sl, sy / sl
                    q = 11 * SS
                    o = (self.puck_r + 2) * SS
                    bx, by = px + sx * o, py + sy * o
                    d.line((bx + wx * q, by + wy * q, bx + wx * q + sx * q, by + wy * q + sy * q,
                            bx + sx * q, by + sy * q), fill=blend(WHITE, 0.7), width=2 * SS)
        # Puck.
        r = self.puck_r * SS
        d.ellipse((px - r, py - r, px + r, py + r), fill=GOLD, outline=(120, 84, 30), width=SS)
        hr = r * 0.32
        d.ellipse((px - r * 0.45 - hr, py - r * 0.45 - hr, px - r * 0.45 + hr, py - r * 0.45 + hr), fill=WHITE)

    def draw_panel_text(self, d: ImageDraw.ImageDraw, name: str, st: dict) -> None:
        man, ev = self.man, self.ev
        col = PANELS[name]["colour"]
        top = GEOM_Y0 + PANELS[name]["index"] * PANEL_H
        cx, cy = self.centre(name)
        L0, half = man["string_length_m"], man["half_string_m"]
        d.text((COL_X, top + 24), LABELS[name], font=self.font, fill=col, anchor="rm")
        d.text((COL_X, top + 64), sublabel(man, name), font=self.font_small, fill=MUTED, anchor="rm")
        for rad, gap in ((L0, 30), (half, 28)):
            o = (rad * self.ppm + gap) * math.sqrt(0.5)
            d.text((cx - o, cy + o), f"{rad * 100:.0f} cm", font=self.font_ring, fill=blend(MUTED, 0.8), anchor="mm")
        d.text((COL_X, top + 120), "speed", font=self.font_small, fill=MUTED, anchor="rm")
        t_half = ev["t_half_pole"] if name == "pole" else ev["t_half_hole"]
        flash = abs(st["t"] - t_half) <= 0.35
        if name == "pole" and st["hit"]:
            d.text((COL_X, top + 172), "at the pole", font=self.font_num, fill=MUTED, anchor="rm")
        else:
            d.text((COL_X, top + 172), f"{st['speed']:.2f} m/s", font=self.font_num, fill=GOLD if flash else TEXT, anchor="rm")
        length = st["l"] if name == "pole" else st["r"]
        d.text((COL_X, top + 240), f"string {length * 100:.1f} cm", font=self.font_read, fill=TEXT, anchor="rm")
        d.text((COL_X, top + 284), f"turns {st['turns']:.2f}", font=self.font_read, fill=TEXT, anchor="rm")
        if st["t"] >= t_half:
            d.text((COL_X, top + 344), half_mark(man, ev, name), font=self.font_mark, fill=GOLD, anchor="rm")
        done = st["hit"] if name == "pole" else st["stopped"]
        if done:
            d.text((COL_X, top + 388), end_mark(man, ev, name), font=self.font_mark, fill=GOLD, anchor="rm")

    def draw_state(self, tau: float) -> np.ndarray:
        """The full frame for run time tau, without title or card."""
        img = Image.new("RGB", (W, H), BG)
        layer = Image.new("RGB", (W * SS, (GEOM_Y1 - GEOM_Y0) * SS), BG)
        ld = ImageDraw.Draw(layer)
        ld.line((40 * SS, PANEL_H * SS, (W - 40) * SS, PANEL_H * SS), fill=SEP, width=2 * SS)
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
    man = json.loads((ROOT / "projects/tetherball/manifest.json").read_text())
    ev = measure(man)
    if "--measure-only" in sys.argv:
        return
    if "--frames" in sys.argv:
        times = [float(v) for v in sys.argv[sys.argv.index("--frames") + 1].split(",")]
        r = Renderer(man, ev)
        (ROOT / "media/tetherball").mkdir(parents=True, exist_ok=True)
        for tv in times:
            Image.fromarray(r.frame_at(int(round(tv * man["fps"])))).save(ROOT / f"media/tetherball/smoke-{tv}.png")
        print("smoke frames: " + ", ".join(f"{tv}" for tv in times))
        return
    Renderer(man, ev).render(ROOT / "media/tetherball/footage.mp4")


if __name__ == "__main__":
    main()
