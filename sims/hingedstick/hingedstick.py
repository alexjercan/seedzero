#!/usr/bin/env python3
"""Hinged stick and free ball: let go of both together. Which hits the table first?

A uniform stick of length L = 1 m is hinged at its left end on a table
and propped at an angle theta0. A free ball is held at rest level with
the stick's tip and just past the tip's reach (its centre is L from the
hinge, so the tip, which sweeps outward as the stick falls, never
touches it). Both are let go at t = 0. The stick alone obeys

    theta'' = -(3 g / (2 L)) cos theta

(a uniform rod about its end, I = m L^2 / 3) and stops when it lies
flat; the ball falls freely from height L sin theta0 and stops on the
table. Two panels: 30 degrees on top, 60 degrees below. Both bodies are
integrated with RK4 at a fixed step; the stick is checked against the
exact energy integral t = sqrt(L / 3 g) int d theta / sqrt(sin theta0 -
sin theta) and the ball against sqrt(2 h / g). The ball is a point for
every number and is drawn larger than life. Deterministic, no seed.

Measured and printed: for each angle the tip height, the tip's initial
vertical acceleration in g, the time the stick lies flat (RK4 and the
energy integral), the ball's landing time (RK4 and the closed form),
the ball's height when the stick is flat or the stick's angle and tip
height when the ball lands, the tip speed on landing (RK4 and sqrt(3 g
L sin theta0)), the classic cup-on-the-tip variant, the 45 degree case,
the angle at which the tip starts at exactly g (cos^2 theta0 = 2 / 3),
the crossover angle at which both land together, a half-step check,
the video schedule and the on-screen text widths.

usage: hingedstick.py [--measure-only] [--frames t1,t2,...]
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
WIRE = (70, 80, 94)
WHITE = (236, 240, 244)
GHOST = (44, 52, 62)
FLOOR = (120, 132, 150)
SLAB = (48, 56, 68)

# Layout: overlay at y 96 (captions.py), title rows at y 190/252/314 for
# the first seconds, two panels (30 degrees on top, 60 degrees below)
# with the hinge at the lower left, the ball level with the tip at x = L
# from the hinge, the clock top right and the readouts on the right,
# captions at caption_y 0.75 (y 1440..1520), payoff card under them.
PANELS = {
    "top": {"label_y": 372, "ground_y": 836, "colour": TEAL, "angle": "top_angle_deg"},
    "bottom": {"label_y": 922, "ground_y": 1386, "colour": CORAL, "angle": "bottom_angle_deg"},
}
HINGE_X = 100.0
SS = 2  # supersampling of the geometry layer
GEOM_Y0, GEOM_Y1 = 336, 1436
PAYOFF_Y = 1592.0
BAR_R = 7.0  # half thickness of the stick in screen px
BALL_R = 14.0
BALL_GAP = 12.0


def blend(col, a, base=BG):
    a = max(0.0, min(1.0, a))
    return tuple(int(round(c * a + b * (1 - a))) for c, b in zip(col, base))


def simulate(man: dict, angle_deg: float, dt: float) -> dict:
    """Stick from angle_deg and a free ball from the tip's height, both from rest at t = 0.

    State: theta, theta' for the stick; y, y' for the ball. RK4 at a fixed
    step up to sim_t_max; each body stops where it lands (theta = 0, y =
    0) and the landing times are interpolated inside the step that
    crosses.
    """
    g, L = man["g"], man["stick_length_m"]
    k = 3.0 * g / (2.0 * L)
    th0 = math.radians(angle_deg)
    h = L * math.sin(th0)
    n = int(round(man["sim_t_max"] / dt))
    theta = np.zeros(n + 1)
    omega = np.zeros(n + 1)
    yb = np.zeros(n + 1)
    th, w, y, vy = th0, 0.0, h, 0.0
    t_flat = w_flat = t_ball = None
    for i in range(n + 1):
        theta[i], omega[i], yb[i] = max(th, 0.0), (w if th > 0.0 else 0.0), max(y, 0.0)
        if i == n:
            break
        if th > 0.0:
            k1 = (w, -k * math.cos(th))
            k2 = (w + 0.5 * dt * k1[1], -k * math.cos(th + 0.5 * dt * k1[0]))
            k3 = (w + 0.5 * dt * k2[1], -k * math.cos(th + 0.5 * dt * k2[0]))
            k4 = (w + dt * k3[1], -k * math.cos(th + dt * k3[0]))
            th_new = th + dt / 6.0 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0])
            w_new = w + dt / 6.0 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1])
            if th_new <= 0.0 and t_flat is None:
                frac = th / (th - th_new)
                t_flat = (i + frac) * dt
                w_flat = w + frac * (w_new - w)
            th, w = th_new, w_new
        if y > 0.0:
            # RK4 on y'' = -g is exact for constant acceleration.
            y_new = y + vy * dt - 0.5 * g * dt * dt
            vy_new = vy - g * dt
            if y_new <= 0.0 and t_ball is None:
                frac = y / (y - y_new)
                t_ball = (i + frac) * dt
            y, vy = y_new, vy_new
    assert t_flat is not None and t_ball is not None, "sim_t_max too short"
    i_flat, i_ball = int(math.ceil(t_flat / dt)), int(math.ceil(t_ball / dt))
    # Height of the loser at the winner's landing, read from the closed
    # forms for the ball (exact) and from the RK4 sample nearest the
    # stick's state for the stick.
    y_ball_at_flat = max(0.0, h - 0.5 * g * t_flat * t_flat)
    j = min(n - 1, int(t_ball / dt))
    fr = t_ball / dt - j
    theta_at_ball = float(theta[j] + fr * (theta[j + 1] - theta[j]))
    return {
        "angle": angle_deg, "h": h, "dt": dt, "theta": theta, "omega": omega, "y": yb,
        "t_flat": t_flat, "t_ball": t_ball, "tip_speed": L * abs(w_flat),
        "y_ball_at_flat": y_ball_at_flat, "theta_at_ball": theta_at_ball,
        "tip_at_ball": L * math.sin(theta_at_ball), "i_flat": i_flat, "i_ball": i_ball,
        "winner": "stick" if t_flat < t_ball else "ball",
    }


def flat_time_exact(g: float, L: float, angle_deg: float, n: int = 200000) -> float:
    """Energy integral sqrt(L / 3 g) int_0^theta0 d theta / sqrt(sin theta0 - sin theta).

    With theta = theta0 - s^2 the integrand is smooth (2 / sqrt(cos theta0)
    at s = 0); midpoint rule in s.
    """
    th0 = math.radians(angle_deg)
    smax = math.sqrt(th0)
    s = (np.arange(n) + 0.5) * smax / n
    f = 2.0 * s / np.sqrt(math.sin(th0) - np.sin(th0 - s * s))
    return math.sqrt(L / (3.0 * g)) * float(f.sum()) * smax / n


def ball_time_exact(g: float, L: float, angle_deg: float) -> float:
    return math.sqrt(2.0 * L * math.sin(math.radians(angle_deg)) / g)


def cup_variant(man: dict, run: dict) -> tuple[float, float]:
    """Ball starting on the tip: first time it meets the stick's line, and the stick's angle then."""
    g, L = man["g"], man["stick_length_m"]
    th0 = math.radians(run["angle"])
    x = L * math.cos(th0)
    dt = run["dt"]
    t = np.arange(len(run["theta"])) * dt
    y_ball = L * math.sin(th0) - 0.5 * g * t * t
    y_stick = x * np.tan(run["theta"])
    idx = np.nonzero(y_ball[1:] <= y_stick[1:])[0]
    i = int(idx[0]) + 1
    d0, d1 = y_ball[i - 1] - y_stick[i - 1], y_ball[i] - y_stick[i]
    frac = d0 / (d0 - d1)
    return (i - 1 + frac) * dt, math.degrees(run["theta"][i - 1] + frac * (run["theta"][i] - run["theta"][i - 1]))


def measure(man: dict) -> dict:
    g, L = man["g"], man["stick_length_m"]
    fps, sub = man["fps"], man["substeps"]
    steps = fps * sub
    dt = 1.0 / steps
    top, bot = man["top_angle_deg"], man["bottom_angle_deg"]
    print(f"setup: a uniform stick of length {L:g} m hinged at its left end on a table and propped at {top:g} degrees "
          f"(top) and {bot:g} degrees (bottom); a free ball held at rest level with the tip, its centre {L:g} m from the "
          f"hinge (just past the tip's reach); both let go at t = 0; g = {g:g} m/s^2; the stick obeys "
          f"theta'' = -(3 g / 2 L) cos theta and stops flat, the ball falls freely and stops on the table; RK4 at "
          f"{steps} steps per second (dt = {dt:.2e} s) for {man['sim_t_max']:g} s; the ball is a point for every "
          f"number; deterministic, no seed")
    th_g = math.degrees(math.acos(math.sqrt(2.0 / 3.0)))
    print(f"tip's initial vertical acceleration (3 / 2) g cos^2 theta0 equals g at theta0 = {th_g:.2f} degrees "
          f"(cos^2 theta0 = 2 / 3): below it the tip starts down faster than a free ball, above it slower")
    out: dict = {}
    for name, angle in (("top", top), ("bottom", bot)):
        run = simulate(man, angle, dt)
        out[name] = run
        th0 = math.radians(angle)
        a_tip = 1.5 * math.cos(th0) ** 2
        t_ex = flat_time_exact(g, L, angle)
        t_bx = ball_time_exact(g, L, angle)
        v_ex = math.sqrt(3.0 * g * L * math.sin(th0))
        first, second = ("stick", "ball") if run["winner"] == "stick" else ("ball", "stick")
        print(f"{name} panel, {angle:g} degrees: tip height L sin theta0 = {run['h']:.4f} m; the tip starts down at "
              f"{a_tip:.3f} g; the stick lies flat at {run['t_flat']:.4f} s (energy integral {t_ex:.4f} s, "
              f"{run['t_flat'] - t_ex:+.2e}); the ball lands at {run['t_ball']:.4f} s (sqrt(2 h / g) = {t_bx:.4f} s, "
              f"{run['t_ball'] - t_bx:+.2e}); the {first} lands first, {abs(run['t_flat'] - run['t_ball']):.4f} s "
              f"before the {second}; when the stick is flat the ball is {run['y_ball_at_flat'] * 100:.2f} cm up; "
              f"when the ball lands the stick is at {math.degrees(run['theta_at_ball']):.2f} degrees with its tip "
              f"{run['tip_at_ball'] * 100:.2f} cm up; tip speed on landing {run['tip_speed']:.3f} m/s (closed form "
              f"sqrt(3 g L sin theta0) = {v_ex:.3f} m/s)")
        t_cup, th_cup = cup_variant(man, run)
        print(f"  classic cup-on-the-tip variant at {angle:g} degrees (not drawn): the ball starts on the tip, "
              f"{L * math.cos(th0):.3f} m from the hinge; it meets the stick's line at {t_cup:.4f} s with the stick at "
              f"{th_cup:.2f} degrees"
              + (" (the stick fell away from under it and lies flat; the ball lands on the stick)" if th_cup < 1e-6
                 else " (the ball drops onto the moving stick and rides it down; the loaded stick is not simulated)"))
    chk = man["check_angle_deg"]
    run_c = simulate(man, chk, dt)
    print(f"check at {chk:g} degrees (not drawn): stick flat at {run_c['t_flat']:.4f} s (energy integral "
          f"{flat_time_exact(g, L, chk):.4f} s), ball lands at {run_c['t_ball']:.4f} s "
          f"(closed form {ball_time_exact(g, L, chk):.4f} s); the {run_c['winner']} lands first, by "
          f"{abs(run_c['t_flat'] - run_c['t_ball']):.4f} s; tip starts at {1.5 * math.cos(math.radians(chk)) ** 2:.3f} g")
    lo, hi = top, bot
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if flat_time_exact(g, L, mid) - ball_time_exact(g, L, mid) < 0.0:
            lo = mid
        else:
            hi = mid
    cross = 0.5 * (lo + hi)
    run_x = simulate(man, cross, dt)
    print(f"crossover angle (stick flat and ball landing at the same time, bisection on the closed forms between "
          f"{top:g} and {bot:g} degrees): {cross:.3f} degrees, both at {ball_time_exact(g, L, cross):.4f} s; RK4 at "
          f"that angle: stick flat at {run_x['t_flat']:.4f} s, ball at {run_x['t_ball']:.4f} s; below it the stick "
          f"wins, above it the ball")
    out["crossover"] = cross
    half: dict = {}
    for name, angle in (("top", top), ("bottom", bot)):
        run_h = simulate(man, angle, 0.5 * dt)
        half[name] = run_h
        run = out[name]
        print(f"check at half the time step ({2 * steps} steps per second), {angle:g} degrees: stick flat at "
              f"{run_h['t_flat']:.6f} s ({run_h['t_flat'] - run['t_flat']:+.1e}), ball at {run_h['t_ball']:.6f} s "
              f"({run_h['t_ball'] - run['t_ball']:+.1e}), ball {run_h['y_ball_at_flat'] * 100:.3f} cm up at the flat, "
              f"tip {run_h['tip_at_ball'] * 100:.3f} cm up at the ball's landing")
    return out


class Renderer:
    def __init__(self, man: dict, meas: dict):
        self.man, self.meas = man, meas
        self.fps = man["fps"]
        font = os.environ["SEED_ZERO_FONT"]
        self.font = ImageFont.truetype(font, 40)
        self.font_title = ImageFont.truetype(font, 56)
        self.font_read = ImageFont.truetype(font, 36)
        self.font_clock = ImageFont.truetype(font, 48)
        self.font_flag = ImageFont.truetype(font, 32)
        self.font_small = ImageFont.truetype(font, 28)
        self.first = None
        self.pxm = float(man["px_per_m"])
        self.slow = float(man["slow_motion"])
        self.L = float(man["stick_length_m"])
        total = int(round(man["scene_duration"] * self.fps))
        self.frames_per_cycle = total // man["cycles"]
        assert self.frames_per_cycle * man["cycles"] == total, "cycles must divide the frame count"
        self.cycle = self.frames_per_cycle / self.fps
        self.labels = {name: f"stick at {man[p['angle']]:g} degrees" for name, p in PANELS.items()}
        self.sub = "hinged at the left end, ball level with the tip"
        widths = {"overlay@34": (ImageFont.truetype(font, 34), man["overlay"])}
        for j, line in enumerate(man["title"].split("|")):
            widths[f"title line {j + 1}@56"] = (self.font_title, line)
        for name, label in self.labels.items():
            widths[f"label {name}@40"] = (self.font, label)
        widths["sublabel@28"] = (self.font_small, self.sub)
        widths["clock@48"] = (self.font_clock, "0.481 s")
        widths["note@28"] = (self.font_small, f"1/{self.slow:g} speed")
        for name in PANELS:
            run = meas[name]
            widths[f"tip readout {name}@36"] = (self.font_read, f"tip {run['h'] * 100:.0f} cm up")
            widths[f"ball readout {name}@36"] = (self.font_read, f"ball {run['h'] * 100:.0f} cm up")
            widths[f"stick landed {name}@36"] = (self.font_read, f"stick flat {run['t_flat']:.3f} s")
            widths[f"ball landed {name}@36"] = (self.font_read, f"ball lands {run['t_ball']:.3f} s")
            widths[f"ghost label {name}@32"] = (self.font_flag, self.ghost_label(name))
        widths["flag@32"] = (self.font_flag, "first")
        for j, line in enumerate(self.payoff_lines()):
            widths[f"payoff line {j + 1}@40"] = (self.font, line)
        print("text widths: " + ", ".join(f"{k} {f.getlength(s):.0f} px" for k, (f, s) in widths.items()))
        hold = man["reset_hold"]
        sched = []
        for name in PANELS:
            run = meas[name]
            sched.append(f"{man[PANELS[name]['angle']]:g} degrees: stick flat {hold + run['t_flat'] * self.slow:.2f} s and "
                         f"ball down {hold + run['t_ball'] * self.slow:.2f} s into the cycle (the {run['winner']} first)")
        last = hold + max(max(r["t_flat"], r["t_ball"]) for r in (meas["top"], meas["bottom"])) * self.slow
        print(f"video: 1/{self.slow:g} speed; {man['cycles']} drops of {self.cycle:.3f} s each, both let go {hold:g} s "
              f"into each cycle; " + "; ".join(sched) + f"; everything is down by {last:.2f} s and holds to the reset at "
              f"{self.cycle:.2f} s; releases at "
              + ", ".join(f"{k * self.cycle + hold:.2f}" for k in range(man["cycles"]))
              + f" s of video; the {man['top_angle_deg']:g} degree stick lands at "
              + ", ".join(f"{k * self.cycle + hold + meas['top']['t_flat'] * self.slow:.2f}" for k in range(man["cycles"]))
              + f" s and the {man['bottom_angle_deg']:g} degree ball at "
              + ", ".join(f"{k * self.cycle + hold + meas['bottom']['t_ball'] * self.slow:.2f}" for k in range(man["cycles"]))
              + f" s; title until {man['title_until']:g} s; payoff card at {man['payoff_t']:g} s; loop crossfade over "
              f"the last {man['loop_fade']:g} s")

    def ghost_label(self, name: str) -> str:
        run = self.meas[name]
        if run["winner"] == "stick":
            return f"still {run['y_ball_at_flat'] * 100:.0f} cm up"
        return f"tip still {run['tip_at_ball'] * 100:.0f} cm up"

    def payoff_lines(self) -> list[str]:
        m = self.meas
        text = self.man["payoff_text"].format(
            t_flat_top=m["top"]["t_flat"], h_ball_top=m["top"]["y_ball_at_flat"] * 100,
            t_ball_bottom=m["bottom"]["t_ball"], h_tip_bottom=m["bottom"]["tip_at_ball"] * 100,
            t_ball_top=m["top"]["t_ball"], t_flat_bottom=m["bottom"]["t_flat"])
        return [s.strip() for s in text.split("|")]

    def cycle_time(self, f: int) -> float:
        return (f % self.frames_per_cycle) / self.fps

    def sim_time(self, f: int) -> float:
        return max(0.0, (self.cycle_time(f) - self.man["reset_hold"]) / self.slow)

    def to_screen(self, p: dict, x: float, y: float) -> tuple[float, float]:
        return HINGE_X + x * self.pxm, p["ground_y"] - y * self.pxm

    @staticmethod
    def layer_xy(sx: float, sy: float) -> tuple[float, float]:
        return sx * SS, (sy - GEOM_Y0) * SS

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

    def stick(self, d: ImageDraw.ImageDraw, hx: float, hy: float, tx: float, ty: float, col, ghost: bool = False) -> None:
        """The bar from the hinge (hx, hy) to the tip (tx, ty) in layer coordinates."""
        r = BAR_R * SS
        if ghost:
            self.dashed(d, (hx, hy), (tx, ty), col, 14 * SS, 9 * SS, 3 * SS)
            d.ellipse((tx - r, ty - r, tx + r, ty + r), outline=col, width=2 * SS)
            return
        d.line((hx, hy, tx, ty), fill=col, width=int(2 * r))
        d.ellipse((hx - r, hy - r, hx + r, hy + r), fill=col)
        d.ellipse((tx - r, ty - r, tx + r, ty + r), fill=col)
        cap = r * 0.55
        d.ellipse((tx - cap, ty - cap, tx + cap, ty + cap), fill=blend(WHITE, 0.8, col))

    def ball(self, d: ImageDraw.ImageDraw, cx: float, cy: float, col, ghost: bool = False) -> None:
        r = BALL_R * SS
        if ghost:
            d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=col, width=2 * SS)
            return
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=col, outline=(120, 84, 30), width=SS)
        hr = r * 0.32
        d.ellipse((cx - r * 0.45 - hr, cy - r * 0.45 - hr, cx - r * 0.45 + hr, cy - r * 0.45 + hr), fill=WHITE)

    def bracket(self, d: ImageDraw.ImageDraw, sx: float, y_top: float, y_bot: float, col) -> None:
        """A ] bracket from y_top to y_bot at x = sx, ticks opening left (layer coordinates)."""
        t = 10 * SS
        d.line((sx, y_top, sx, y_bot), fill=col, width=2 * SS)
        d.line((sx - t, y_top, sx, y_top), fill=col, width=2 * SS)
        d.line((sx - t, y_bot, sx, y_bot), fill=col, width=2 * SS)

    def draw_scene(self, f: int) -> Image.Image:
        man, meas = self.man, self.meas
        img = Image.new("RGB", (W, H), BG)
        layer = Image.new("RGB", (W * SS, (GEOM_Y1 - GEOM_Y0) * SS), BG)
        ld = ImageDraw.Draw(layer)
        c = self.cycle_time(f)
        s = self.sim_time(f)
        texts = []
        Lpx = self.L * self.pxm
        for name, p in PANELS.items():
            run = meas[name]
            col = p["colour"]
            dt = run["dt"]
            i = min(int(round(s / dt)), len(run["theta"]) - 1)
            theta, y_ball = float(run["theta"][i]), float(run["y"][i])
            stick_down, ball_down = s >= run["t_flat"], s >= run["t_ball"]
            gy = p["ground_y"]
            hx, hy = self.layer_xy(HINGE_X, gy)
            # Table slab, its top BAR_R below the hinge line so the flat bar rests on it.
            top_y = (gy + BAR_R - GEOM_Y0) * SS
            ld.rectangle((60 * SS, top_y, (W - 60) * SS, top_y + 12 * SS), fill=SLAB)
            ld.line((60 * SS, top_y, (W - 60) * SS, top_y), fill=FLOOR, width=3 * SS)
            # The tip's path and the release level.
            th0 = math.radians(run["angle"])
            ld.arc((hx - Lpx * SS, hy - Lpx * SS, hx + Lpx * SS, hy + Lpx * SS), -math.degrees(th0), 0.0,
                   fill=GHOST, width=2 * SS)
            ball_sx = HINGE_X + Lpx + BAR_R + BALL_GAP + BALL_R
            level_y = gy - run["h"] * self.pxm
            lx0, ly0 = self.layer_xy(HINGE_X, level_y)
            lx1, _ = self.layer_xy(ball_sx + 40, level_y)
            self.dashed(ld, (lx0, ly0), (lx1, ly0), blend(MUTED, 0.6), 12 * SS, 8 * SS, 2 * SS)
            # Ghost of the loser at the winner's landing.
            if run["winner"] == "stick" and stick_down:
                gx, gyy = self.layer_xy(ball_sx, gy - run["y_ball_at_flat"] * self.pxm + BAR_R - BALL_R)
                self.ball(ld, gx, gyy, blend(WHITE, 0.7), ghost=True)
                bx = gx + (BALL_R + 12) * SS
                self.bracket(ld, bx, gyy + BALL_R * SS, top_y, blend(WHITE, 0.7))
                texts.append(((ball_sx + BALL_R + 22, gy - run["y_ball_at_flat"] * self.pxm * 0.5), self.ghost_label(name),
                              self.font_flag, WHITE, "lm"))
            if run["winner"] == "ball" and ball_down:
                thg = run["theta_at_ball"]
                gtx, gty = self.layer_xy(*self.to_screen(p, self.L * math.cos(thg), self.L * math.sin(thg)))
                self.stick(ld, hx, hy, gtx, gty, blend(WHITE, 0.7), ghost=True)
                bx = gtx + 28 * SS
                self.bracket(ld, bx, gty, top_y, blend(WHITE, 0.7))
                texts.append(((HINGE_X + self.L * math.cos(thg) * self.pxm + 40, gy - run["tip_at_ball"] * self.pxm * 0.5),
                              self.ghost_label(name), self.font_flag, WHITE, "lm"))
            # Hinge pin, stick, ball.
            tx, ty = self.layer_xy(*self.to_screen(p, self.L * math.cos(theta), self.L * math.sin(theta)))
            self.stick(ld, hx, hy, tx, ty, col)
            pr = 5 * SS
            ld.ellipse((hx - pr, hy - pr, hx + pr, hy + pr), fill=BG, outline=WIRE, width=2 * SS)
            bx_, by_ = self.layer_xy(ball_sx, gy - y_ball * self.pxm + BAR_R - BALL_R)
            self.ball(ld, bx_, by_, GOLD)
            # Landing flashes and the winner's flag.
            for body, landed, t_land, (fx, fy) in (("stick", stick_down, run["t_flat"], (tx, ty)),
                                                  ("ball", ball_down, run["t_ball"], (bx_, by_))):
                if not landed:
                    continue
                u = (c - (man["reset_hold"] + t_land * self.slow)) / man["land_flash"]
                if 0.0 <= u < 1.0:
                    rr = (22 + 70 * u) * SS
                    ld.ellipse((fx - rr, fy - rr, fx + rr, fy + rr), outline=blend(WHITE, 1 - u), width=4 * SS)
                if body == run["winner"]:
                    if body == "stick":
                        texts.append(((HINGE_X + Lpx - 60, gy - 40), "first", self.font_flag, WHITE, "mm"))
                    else:
                        texts.append(((ball_sx + BALL_R + 16, gy - 12), "first", self.font_flag, WHITE, "lm"))
            # Labels, clock, readouts.
            texts.append(((40, p["label_y"]), self.labels[name], self.font, col, "lm"))
            texts.append(((40, p["label_y"] + 40), self.sub, self.font_small, MUTED, "lm"))
            s_draw = min(s, max(run["t_flat"], run["t_ball"]))
            texts.append(((W - 40, p["label_y"] + 10), f"{s_draw:.3f} s", self.font_clock, TEXT, "rm"))
            texts.append(((W - 40, p["label_y"] + 58), f"1/{self.slow:g} speed", self.font_small, MUTED, "rm"))
            tip_h = self.L * math.sin(theta)
            if stick_down:
                texts.append(((W - 40, gy - 170), f"stick flat {run['t_flat']:.3f} s", self.font_read,
                              WHITE if run["winner"] == "stick" else col, "rm"))
            else:
                texts.append(((W - 40, gy - 170), f"tip {tip_h * 100:.0f} cm up", self.font_read, col, "rm"))
            if ball_down:
                texts.append(((W - 40, gy - 120), f"ball lands {run['t_ball']:.3f} s", self.font_read,
                              WHITE if run["winner"] == "ball" else GOLD, "rm"))
            else:
                texts.append(((W - 40, gy - 120), f"ball {y_ball * 100:.0f} cm up", self.font_read, GOLD, "rm"))
        img.paste(layer.reduce(SS), (0, GEOM_Y0))
        d = ImageDraw.Draw(img)
        for xy, text, font, fill, anchor in texts:
            d.text(xy, text, font=font, fill=fill, anchor=anchor)
        return img

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
            for j, line in enumerate(self.payoff_lines()):
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
    man = json.loads((ROOT / "projects/hingedstick/manifest.json").read_text())
    meas = measure(man)
    if "--measure-only" in sys.argv:
        return
    if "--frames" in sys.argv:
        times = [float(v) for v in sys.argv[sys.argv.index("--frames") + 1].split(",")]
        r = Renderer(man, meas)
        (ROOT / "media/hingedstick").mkdir(parents=True, exist_ok=True)
        for tv in times:
            Image.fromarray(r.frame_at(int(round(tv * man["fps"])))).save(ROOT / f"media/hingedstick/smoke-{tv}.png")
        print("smoke frames: " + ", ".join(f"{tv}" for tv in times))
        return
    Renderer(man, meas).render(ROOT / "media/hingedstick/footage.mp4")


if __name__ == "__main__":
    main()
