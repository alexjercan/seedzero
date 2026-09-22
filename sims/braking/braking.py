#!/usr/bin/env python3
"""Braking: twice the speed. How much farther to stop?

Two cars in the two lanes of one road, front bumpers on the same line at
t = 0, both braking at a constant 0.8 g (a = 0.8 x 9.80665 = 7.8453
m/s^2, a dry-road figure) with no reaction time: braking distance only.
Car A in the left lane starts at 50 km/h = 13.8889 m/s, car B in the
right lane at 100 km/h = 27.7778 m/s. Closed forms: x(t) = v0 t - a t^2
/ 2 and v(t) = v0 - a t until v = 0 at t = v0 / a, so the stopping
distance is d = v0^2 / (2 a): 12.2940 m against 49.1761 m, a ratio of
exactly 4 for twice the speed, in 1.7703 s against 3.5407 s. Where car A
stops, car B is still doing sqrt(vB^2 - 2 a dA) = 24.056 m/s = 86.60
km/h (at t = 0.4744 s), and at the instant car A stops car B is doing
exactly 50 km/h with exactly 12.29 m still to go. Both cars are drawn
from the closed forms and checked by an RK4 integration at 6,000 steps
per second. Top-down road running up the screen, the braking line near
the bottom, 19 px per metre. Played at 1/3 speed, three runs of 13.33 s
with a short crossfade reset; the stop marks lit in run 1 stay on the
road for runs 2 and 3, so the viewer sees car B pass car A's stop mark
with its readout in gold. Deterministic, no seed.

Measured and printed: both stopping distances and times and their
ratios; car B's speed and time at car A's stop mark; car B's speed,
position and remaining distance at the instant car A stops; the RK4
checks (max position and speed error, interpolated stop times and
distances, speed at the mark); a table of stopping distances for other
speeds; the run schedule in video time; the on-screen text widths.

usage: braking.py [--measure-only] [--frames t1,t2,...]
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
ASPHALT = (30, 34, 40)
RED = (255, 64, 48)
HEAD = (250, 236, 170)

# Layout: overlay at y 96 (captions.py), title rows at y 190/252 for the
# first seconds, the road from y 350 to 1436 (top down, the cars drive up
# from the braking line at y 1320), a right-aligned readout column for
# car A left of the road and a left-aligned one for car B right of it,
# captions at caption_y 0.75 (y 1440..1520), payoff card from y 1592.
GEOM_Y0, GEOM_Y1 = 350, 1436
ROAD_CX = 540.0
LINE_Y = 1320.0
COL_A_X, COL_B_X = 414, 666
ROW_LABEL, ROW_SPEED, ROW_DIST = 1232, 1324, 1372
NOTE_Y = (378, 408)
CARS = {"a": {"lane": -1, "colour": TEAL, "col_x": COL_A_X, "anchor": "r"},
        "b": {"lane": 1, "colour": CORAL, "col_x": COL_B_X, "anchor": "l"}}
SS = 2
PAYOFF_Y = 1592.0
NOTE = ("no reaction time", "braking distance only")


def blend(col, a, base=BG):
    return tuple(int(round(c * a + b * (1 - a))) for c, b in zip(col, base))


def smoothstep(u: float) -> float:
    u = max(0.0, min(1.0, u))
    return u * u * (3 - 2 * u)


# --- closed forms -----------------------------------------------------------
def decel(man: dict) -> float:
    return man["brake_g"] * man["g_m_s2"]


def speeds(man: dict) -> dict:
    return {"a": man["speed_a_km_h"] / 3.6, "b": man["speed_b_km_h"] / 3.6}


def car_state(v0: float, a: float, t: float) -> dict:
    """Position and speed of a car braking at a from v0, real time t after the line."""
    t_stop = v0 / a
    d = v0 * v0 / (2.0 * a)
    if t >= t_stop:
        return {"x": d, "v": 0.0, "stopped": True, "t": t, "t_stop": t_stop, "d": d}
    return {"x": v0 * t - 0.5 * a * t * t, "v": v0 - a * t, "stopped": False, "t": t, "t_stop": t_stop, "d": d}


def speed_at(v0: float, a: float, x: float) -> float:
    return math.sqrt(max(0.0, v0 * v0 - 2.0 * a * x))


# --- RK4 check ---------------------------------------------------------------
def rk4(acc, state, dt: float):
    x, v = state
    k1 = (v, acc(x, v))
    s2 = (x + 0.5 * dt * k1[0], v + 0.5 * dt * k1[1])
    k2 = (s2[1], acc(*s2))
    s3 = (x + 0.5 * dt * k2[0], v + 0.5 * dt * k2[1])
    k3 = (s3[1], acc(*s3))
    s4 = (x + dt * k3[0], v + dt * k3[1])
    k4 = (s4[1], acc(*s4))
    return (x + dt / 6.0 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0]),
            v + dt / 6.0 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1]))


def check_car(v0: float, a: float, steps: int, marks: list[float]) -> dict:
    """Integrate x'' = -a from (0, v0) until v <= 0; interpolate the stop and the speed at each mark."""
    dt = 1.0 / steps

    def acc(x, v):
        return -a

    st = (0.0, v0)
    t = 0.0
    out = {"max_x_err": 0.0, "max_v_err": 0.0, "marks": {}}
    prev = None
    while True:
        x, v = st
        x_cf = v0 * t - 0.5 * a * t * t
        v_cf = v0 - a * t
        if prev is not None:
            for m in marks:
                if m not in out["marks"] and prev[1] < m <= x:
                    f = (m - prev[1]) / (x - prev[1])
                    out["marks"][m] = {"t": prev[0] + f * dt, "v": prev[2] + f * (v - prev[2])}
            if v <= 0.0:
                f = prev[2] / (prev[2] - v)
                out["stop"] = {"t": prev[0] + f * dt, "x": prev[1] + f * (x - prev[1])}
                break
        out["max_x_err"] = max(out["max_x_err"], abs(x - x_cf))
        out["max_v_err"] = max(out["max_v_err"], abs(v - v_cf))
        prev = (t, x, v)
        st = rk4(acc, st, dt)
        t += dt
    out["steps"] = int(round(t / dt))
    return out


# --- measurement --------------------------------------------------------------
def measure(man: dict) -> dict:
    a = decel(man)
    v = speeds(man)
    steps, slow, ppm = man["steps_per_second"], man["slow_factor"], man["px_per_m"]
    print(f"setup: two cars in the two lanes of one road, front bumpers on the same line at t = 0, both braking at "
          f"a constant {man['brake_g']:g} g = {a:.4f} m/s^2 (g = {man['g_m_s2']:g}, a dry-road figure) with no "
          f"reaction time (braking distance only); car A (left lane) at {man['speed_a_km_h']:g} km/h = {v['a']:.4f} "
          f"m/s, car B (right lane) at {man['speed_b_km_h']:g} km/h = {v['b']:.4f} m/s; {man['car_length_m']:g} x "
          f"{man['car_width_m']:g} m cars in {man['lane_width_m']:g} m lanes at {ppm:g} px per metre; drawn from "
          f"the closed forms x = v0 t - a t^2 / 2, v = v0 - a t and checked by RK4 at {steps} steps per second "
          f"(dt = {1 / steps:.2e} s); played at 1/{slow:g} speed; deterministic, no seed")
    sa = car_state(v["a"], a, v["a"] / a)
    sb = car_state(v["b"], a, v["b"] / a)
    dA, dB, tA, tB = sa["d"], sb["d"], sa["t_stop"], sb["t_stop"]
    print(f"closed forms (d = v0^2 / (2 a), t = v0 / a): car A stops at {dA:.4f} m after {tA:.4f} s; car B stops at "
          f"{dB:.4f} m after {tB:.4f} s; distance ratio {dB / dA:.4f} for a speed ratio of {v['b'] / v['a']:.4f}; "
          f"time ratio {tB / tA:.4f}; difference {dB - dA:.4f} m")
    v_cross = speed_at(v["b"], a, dA)
    t_cross = (v["b"] - v_cross) / a
    a_at_cross = car_state(v["a"], a, t_cross)
    print(f"car B at car A's stop mark ({dA:.4f} m): speed sqrt(vB^2 - 2 a dA) = {v_cross:.4f} m/s = "
          f"{v_cross * 3.6:.2f} km/h at t = {t_cross:.4f} s ({v_cross / v['b'] * 100:.1f} percent of its start "
          f"speed, {v_cross * v_cross / (v['b'] * v['b']) * 100:.1f} percent of its kinetic energy left); car A at "
          f"that instant is at {a_at_cross['x']:.4f} m doing {a_at_cross['v'] * 3.6:.2f} km/h")
    b_at_ta = car_state(v["b"], a, tA)
    print(f"car B at the instant car A stops (t = {tA:.4f} s): {b_at_ta['x']:.4f} m, {b_at_ta['v']:.4f} m/s = "
          f"{b_at_ta['v'] * 3.6:.2f} km/h, {dB - b_at_ta['x']:.4f} m still to go (a car at {b_at_ta['v'] * 3.6:.0f} "
          f"km/h needs {b_at_ta['v'] ** 2 / (2 * a):.4f} m)")
    # Mean speeds: d = mean speed x time, both double.
    print(f"mean braking speed v0 / 2: car A {v['a'] / 2 * 3.6:.2f} km/h over {tA:.4f} s, car B {v['b'] / 2 * 3.6:.2f} "
          f"km/h over {tB:.4f} s: twice the mean speed for twice the time is four times the distance")
    # RK4 checks.
    ca = check_car(v["a"], a, steps, [])
    cb = check_car(v["b"], a, steps, [dA])
    print(f"RK4 check, car A ({ca['steps']} steps to v = 0): max |x - closed form| {ca['max_x_err']:.2e} m, max "
          f"|v - closed form| {ca['max_v_err']:.2e} m/s; interpolated stop t = {ca['stop']['t']:.4f} s (closed form "
          f"{tA:.4f}), x = {ca['stop']['x']:.4f} m (closed form {dA:.4f})")
    mb = cb["marks"][dA]
    print(f"RK4 check, car B ({cb['steps']} steps to v = 0): max |x - closed form| {cb['max_x_err']:.2e} m, max "
          f"|v - closed form| {cb['max_v_err']:.2e} m/s; interpolated stop t = {cb['stop']['t']:.4f} s (closed form "
          f"{tB:.4f}), x = {cb['stop']['x']:.4f} m (closed form {dB:.4f}); at car A's stop mark t = {mb['t']:.4f} s "
          f"(closed form {t_cross:.4f}), speed {mb['v']:.4f} m/s = {mb['v'] * 3.6:.2f} km/h (closed form "
          f"{v_cross * 3.6:.2f}); ratio of the RK4 stop distances {cb['stop']['x'] / ca['stop']['x']:.6f}")
    # Table for the description.
    rows = []
    for kmh in man["table_km_h"]:
        v0 = kmh / 3.6
        rows.append(f"{kmh:g} km/h: {v0 * v0 / (2 * a):.2f} m in {v0 / a:.2f} s")
    print(f"table at {man['brake_g']:g} g, braking distance only: " + "; ".join(rows))
    ev = {"dA": dA, "dB": dB, "tA": tA, "tB": tB, "v_cross": v_cross, "t_cross": t_cross,
          "vA": man["speed_a_km_h"], "vB": man["speed_b_km_h"]}
    # Run schedule in video time.
    period, rel, fps = man["run_period"], man["release_at"], man["fps"]
    n_runs = int(round(man["scene_duration"] / period))
    fpr = int(round(period * fps))
    r_first = int(math.ceil(tA * slow / period))
    ev["r_first"] = r_first
    ev["t_cross_video"] = r_first * period + rel + t_cross * slow
    lines = []
    for r in range(n_runs):
        t0 = r * period + rel
        lines.append(f"run {r + 1}: brakes on {t0:.2f} s; car B at car A's mark {t0 + t_cross * slow:.2f} s"
                     f"{' (mark not yet lit, no flash)' if r < r_first else ' (readout gold, label lit)'}, car A "
                     f"stops {t0 + tA * slow:.2f} s, car B stops {t0 + tB * slow:.2f} s, hold to "
                     f"{r * period + period - man['reset_dur']:.2f} s, reset to {r * period + period:.2f} s")
    print(f"schedule ({n_runs} runs of {period:.4f} s = {fpr} frames at 1/{slow:g} speed, brakes on {rel:g} s into "
          f"each run, crossfade reset over the last {man['reset_dur']:g} s; the stop marks lit in run 1 stay on the "
          f"road for the later runs, so the marks are up from {tA * slow:.2f} s (car A) and {tB * slow:.2f} s "
          f"(car B) to the loop fade, and car B's crossing of car A's mark is flagged from run {r_first + 1} at "
          f"{ev['t_cross_video']:.2f} s): " + "; ".join(lines))
    print(f"title until {man['title_until']:g} s; payoff card from {man['payoff_t']:g} s; loop fade {man['loop_fade']:g} s")
    # Text widths.
    font = os.environ["SEED_ZERO_FONT"]
    f22, f26, f32, f34, f36, f40, f56, f64 = (ImageFont.truetype(font, n) for n in (22, 26, 32, 34, 36, 40, 56, 64))
    widths = {"overlay@34": (f34, man["overlay"])}
    for j, line in enumerate(man["title"].split("|")):
        widths[f"title line {j + 1}@56"] = (f56, line)
    for j, line in enumerate(NOTE):
        widths[f"note line {j + 1}@26"] = (f26, line)
    widths["label a@40"] = (f40, label(man, "a"))
    widths["label b@40"] = (f40, label(man, "b"))
    widths["readout number@64"] = (f64, f"{man['speed_b_km_h']:.1f}")
    widths["readout unit@32"] = (f32, "km/h")
    widths["readout stopped@64"] = (f64, "stopped")
    widths["distance@36"] = (f36, f"{dB:.1f} m")
    widths["mark a@32"] = (f32, f"{dA:.1f} m")
    widths["mark b@32"] = (f32, f"{dB:.1f} m")
    widths["cross label@32"] = (f32, cross_text(ev))
    widths["tick label@22"] = (f22, "50")
    for j, line in enumerate(payoff_lines(man, ev)):
        widths[f"payoff line {j + 1}@40"] = (f40, line)
    print("text widths: " + ", ".join(f"{k} {f.getlength(s):.0f} px" for k, (f, s) in widths.items()))
    return ev


def label(man: dict, name: str) -> str:
    return f"from {man['speed_a_km_h' if name == 'a' else 'speed_b_km_h']:g} km/h"


def cross_text(ev: dict) -> str:
    return f"{ev['v_cross'] * 3.6:.1f} km/h here"


def payoff_lines(man: dict, ev: dict) -> list[str]:
    text = man["payoff_text"].format(vA=ev["vA"], vB=ev["vB"], dA=ev["dA"], dB=ev["dB"])
    return [s.strip() for s in text.split("|")]


# --- rendering ---------------------------------------------------------------
class Renderer:
    def __init__(self, man: dict, ev: dict):
        self.man, self.ev = man, ev
        self.fps = man["fps"]
        font = os.environ["SEED_ZERO_FONT"]
        self.font = ImageFont.truetype(font, 40)
        self.font_title = ImageFont.truetype(font, 56)
        self.font_note = ImageFont.truetype(font, 26)
        self.font_mark = ImageFont.truetype(font, 32)
        self.font_read = ImageFont.truetype(font, 36)
        self.font_num = ImageFont.truetype(font, 64)
        self.font_tick = ImageFont.truetype(font, 22 * SS)
        self.ppm = float(man["px_per_m"])
        self.a = decel(man)
        self.v0 = speeds(man)
        self.slow = float(man["slow_factor"])
        self.period = float(man["run_period"])
        self.fpr = int(round(self.period * self.fps))
        self.n_runs = int(round(man["scene_duration"] / self.period))
        self.lane_w = man["lane_width_m"] * self.ppm
        self.first = None
        self.targets: dict[int, np.ndarray] = {}
        self.unit_w = ImageFont.truetype(font, 32).getlength("km/h")
        self.font_unit = ImageFont.truetype(font, 32)

    # --- geometry helpers -------------------------------------------------
    def lane_cx(self, name: str) -> float:
        return ROAD_CX + CARS[name]["lane"] * self.lane_w / 2.0

    def y_of(self, x_m: float) -> float:
        """Absolute y of a point x_m metres up the road from the braking line."""
        return LINE_Y - x_m * self.ppm

    def L(self, x: float, y: float) -> tuple[float, float]:
        """Layer coordinates (supersampled, y relative to GEOM_Y0) of an absolute frame point."""
        return x * SS, (y - GEOM_Y0) * SS

    def times(self, f: int) -> dict:
        """Video time, run index, run time and real time for frame f."""
        r = f // self.fpr
        tau = (f - r * self.fpr) / self.fps
        tr = max(0.0, tau - self.man["release_at"]) / self.slow
        return {"t": f / self.fps, "r": r, "tau": tau, "tr": tr}

    def state(self, name: str, tr: float) -> dict:
        return car_state(self.v0[name], self.a, tr)

    # --- drawing ----------------------------------------------------------
    def draw_road(self, d: ImageDraw.ImageDraw) -> None:
        x0, x1 = ROAD_CX - self.lane_w, ROAD_CX + self.lane_w
        top, bot = self.L(x0, GEOM_Y0), self.L(x1, GEOM_Y1)
        d.rectangle((top[0], top[1], bot[0], bot[1]), fill=ASPHALT)
        for name, spec in CARS.items():
            lx0 = self.L(self.lane_cx(name) - self.lane_w / 2.0, 0)[0]
            lx1 = self.L(self.lane_cx(name) + self.lane_w / 2.0, 0)[0]
            d.rectangle((lx0, top[1], lx1, bot[1]), fill=blend(spec["colour"], 0.05, ASPHALT))
        for xe in (x0, x1):
            lx, _ = self.L(xe, 0)
            d.line((lx, top[1], lx, bot[1]), fill=WIRE, width=2 * SS)
        # Lane divider: painted dashes.
        cx, _ = self.L(ROAD_CX, 0)
        y = top[1]
        dash = 24 * SS
        while y < bot[1]:
            d.line((cx, y, cx, min(bot[1], y + dash)), fill=blend(MUTED, 0.5, ASPHALT), width=2 * SS)
            y += 2 * dash
        # Distance ticks every 10 m on both edges, labels painted on the divider.
        m = 10
        while self.y_of(m) > GEOM_Y0 + 10:
            ty = self.y_of(m)
            for xe, s in ((x0, -1), (x1, 1)):
                lx, ly = self.L(xe, ty)
                d.line((lx, ly, lx + s * 10 * SS, ly), fill=WIRE, width=2 * SS)
            lab = f"{m}"
            lw = self.font_tick.getlength(lab)
            lx, ly = self.L(ROAD_CX, ty + 30)
            d.rectangle((lx - lw / 2 - 4 * SS, ly - 13 * SS, lx + lw / 2 + 4 * SS, ly + 13 * SS), fill=ASPHALT)
            d.text((lx, ly), lab, font=self.font_tick, fill=blend(MUTED, 0.75, ASPHALT), anchor="mm")
            m += 10
        # The braking line.
        lx0, ly = self.L(x0 - 10, LINE_Y)
        lx1, _ = self.L(x1 + 10, LINE_Y)
        d.line((lx0, ly, lx1, ly), fill=WHITE, width=3 * SS)

    def draw_marks(self, d: ImageDraw.ImageDraw, uA: float, uB: float) -> None:
        """Stop marks: solid across the car's lane, and for car A dashed across car B's lane too."""
        ev = self.ev
        if uA > 0.0:
            y = self.y_of(ev["dA"])
            xa0, xa1 = ROAD_CX - self.lane_w, ROAD_CX
            p0, p1 = self.L(xa0, y), self.L(xa1, y)
            d.line((p0, p1), fill=blend(GOLD, uA, ASPHALT), width=3 * SS)
            x = p1[0]
            xe = self.L(ROAD_CX + self.lane_w, y)[0]
            while x < xe:
                d.line((x, p1[1], min(xe, x + 8 * SS), p1[1]), fill=blend(GOLD, 0.8 * uA, ASPHALT), width=3 * SS)
                x += 14 * SS
        if uB > 0.0:
            y = self.y_of(ev["dB"])
            p0, p1 = self.L(ROAD_CX, y), self.L(ROAD_CX + self.lane_w, y)
            d.line((p0, p1), fill=blend(GOLD, uB, ASPHALT), width=3 * SS)

    def draw_car(self, d: ImageDraw.ImageDraw, name: str, st: dict) -> None:
        man = self.man
        col = CARS[name]["colour"]
        cx = self.lane_cx(name)
        length, width = man["car_length_m"] * self.ppm, man["car_width_m"] * self.ppm
        y_front = self.y_of(st["x"])
        y_rear = y_front + length
        half = width / 2.0
        # Skid marks from the rear axle's start to its position now.
        track = 0.62 * self.ppm
        axle = 3.8 * self.ppm
        for s in (-1, 1):
            p0 = self.L(cx + s * track, LINE_Y + axle)
            p1 = self.L(cx + s * track, y_front + axle)
            d.line((p0, p1), fill=blend(col, 0.4, ASPHALT), width=3 * SS)
        # Brake-light glow behind the car.
        g0, g1 = self.L(cx - half, y_rear - 2), self.L(cx + half, y_rear + 9)
        d.rounded_rectangle((g0[0], g0[1], g1[0], g1[1]), radius=4 * SS, fill=blend(RED, 0.35, ASPHALT))
        # Body, cabin, headlights, brake lights.
        b0, b1 = self.L(cx - half, y_front), self.L(cx + half, y_rear)
        d.rounded_rectangle((b0[0], b0[1], b1[0], b1[1]), radius=7 * SS, fill=col, outline=blend(col, 0.55, (0, 0, 0)), width=SS)
        c0, c1 = self.L(cx - half + 5, y_front + 24), self.L(cx + half - 5, y_front + 58)
        d.rounded_rectangle((c0[0], c0[1], c1[0], c1[1]), radius=4 * SS, fill=blend(col, 0.32, (8, 10, 14)))
        w0, w1 = self.L(cx - half + 6, y_front + 25), self.L(cx + half - 6, y_front + 34)
        d.rectangle((w0[0], w0[1], w1[0], w1[1]), fill=blend(WHITE, 0.55, col))
        for s in (-1, 1):
            h0 = self.L(cx + s * (half - 3), y_front + 2)
            h1 = self.L(cx + s * (half - 11), y_front + 8)
            d.rectangle((min(h0[0], h1[0]), h0[1], max(h0[0], h1[0]), h1[1]), fill=HEAD)
            r0 = self.L(cx + s * (half - 3), y_rear - 9)
            r1 = self.L(cx + s * (half - 12), y_rear - 2)
            d.rectangle((min(r0[0], r1[0]), r0[1], max(r0[0], r1[0]), r1[1]), fill=RED)

    def mark_alphas(self, t: float) -> tuple[float, float, float]:
        ev, slow = self.ev, self.slow
        rel = self.man["release_at"]
        uA = smoothstep((t - (ev["tA"] * slow + rel)) / 0.45)
        uB = smoothstep((t - (ev["tB"] * slow + rel)) / 0.45)
        uC = smoothstep((t - ev["t_cross_video"]) / 0.45)
        return uA, uB, uC

    def draw_state(self, f: int) -> np.ndarray:
        """The full frame for frame f, without title or card."""
        man, ev = self.man, self.ev
        tm = self.times(f)
        states = {name: self.state(name, tm["tr"]) for name in CARS}
        uA, uB, uC = self.mark_alphas(tm["t"])
        img = Image.new("RGB", (W, H), BG)
        layer = Image.new("RGB", (W * SS, (GEOM_Y1 - GEOM_Y0) * SS), BG)
        ld = ImageDraw.Draw(layer)
        self.draw_road(ld)
        self.draw_marks(ld, uA, uB)
        for name in CARS:
            self.draw_car(ld, name, states[name])
        img.paste(layer.reduce(SS), (0, GEOM_Y0))
        d = ImageDraw.Draw(img)
        # Mark labels beside the road.
        x0, x1 = ROAD_CX - self.lane_w, ROAD_CX + self.lane_w
        if uA > 0.0:
            d.text((x0 - 14, self.y_of(ev["dA"])), f"{ev['dA']:.1f} m", font=self.font_mark, fill=blend(GOLD, uA), anchor="rm")
        if uB > 0.0:
            d.text((x1 + 14, self.y_of(ev["dB"])), f"{ev['dB']:.1f} m", font=self.font_mark, fill=blend(GOLD, uB), anchor="lm")
        if uC > 0.0:
            d.text((x1 + 14, self.y_of(ev["dA"])), cross_text(ev), font=self.font_mark, fill=blend(GOLD, uC), anchor="lm")
        for j, line in enumerate(NOTE):
            d.text((COL_A_X, NOTE_Y[j]), line, font=self.font_note, fill=MUTED, anchor="rm")
        # Readout columns.
        flash_b = tm["r"] >= ev["r_first"] and abs(tm["tr"] - ev["t_cross"]) <= 0.3
        for name, st in states.items():
            spec = CARS[name]
            col, x = spec["colour"], spec["col_x"]
            right = spec["anchor"] == "r"
            d.text((x, ROW_LABEL), label(man, name), font=self.font, fill=col, anchor="rm" if right else "lm")
            if st["stopped"]:
                d.text((x, ROW_SPEED), "stopped", font=self.font_num, fill=MUTED, anchor="rs" if right else "ls")
            else:
                num = f"{st['v'] * 3.6:.1f}"
                fill = GOLD if (name == "b" and flash_b) else TEXT
                if right:
                    d.text((x, ROW_SPEED), "km/h", font=self.font_unit, fill=MUTED, anchor="rs")
                    d.text((x - self.unit_w - 10, ROW_SPEED), num, font=self.font_num, fill=fill, anchor="rs")
                else:
                    d.text((x, ROW_SPEED), num, font=self.font_num, fill=fill, anchor="ls")
                    d.text((x + self.font_num.getlength(num) + 10, ROW_SPEED), "km/h", font=self.font_unit, fill=MUTED, anchor="ls")
            d.text((x, ROW_DIST), f"{st['x']:.1f} m", font=self.font_read, fill=GOLD if st["stopped"] else TEXT,
                   anchor="rm" if right else "lm")
        return np.asarray(img, dtype=np.float32)

    def draw_scene(self, f: int) -> Image.Image:
        """Frame f; the last reset_dur of each run crossfades to the start of the next run (or of the video)."""
        man = self.man
        tm = self.times(f)
        reset_start = self.period - man["reset_dur"]
        u = smoothstep((tm["tau"] - reset_start) / man["reset_dur"]) if tm["tau"] >= reset_start else 0.0
        live = self.draw_state(f)
        if u > 0.0:
            nxt = (tm["r"] + 1) * self.fpr if tm["r"] + 1 < self.n_runs else 0
            if nxt not in self.targets:
                self.targets[nxt] = self.draw_state(nxt)
            live = live * (1.0 - u) + self.targets[nxt] * u
        return Image.fromarray(live.astype(np.uint8))

    def live_frame(self, f: int) -> np.ndarray:
        man = self.man
        t = f / self.fps
        img = self.draw_scene(f)
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
    man = json.loads((ROOT / "projects/braking/manifest.json").read_text())
    ev = measure(man)
    if "--measure-only" in sys.argv:
        return
    if "--frames" in sys.argv:
        times = [float(v) for v in sys.argv[sys.argv.index("--frames") + 1].split(",")]
        r = Renderer(man, ev)
        (ROOT / "media/braking").mkdir(parents=True, exist_ok=True)
        for tv in times:
            Image.fromarray(r.frame_at(int(round(tv * man["fps"])))).save(ROOT / f"media/braking/smoke-{tv}.png")
        print("smoke frames: " + ", ".join(f"{tv}" for tv in times))
        return
    Renderer(man, ev).render(ROOT / "media/braking/footage.mp4")


if __name__ == "__main__":
    main()
