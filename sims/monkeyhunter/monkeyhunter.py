#!/usr/bin/env python3
"""Monkey and hunter: aim straight at it. It drops as you fire. Do you hit?

A launcher at the origin fires a dart straight along the line of sight
at a target hanging H = 10 m up and D = 20 m away. The target is let go
from rest at t = 0, the instant the dart leaves. Two panels: the same
aim at 30 m/s (top) and at 60 m/s (bottom). Gravity only, no air; the
dart and the target are points for every measurement and are drawn
larger than life. Both bodies are integrated together with RK4 at a
fixed step (exact for constant acceleration) and every printed number is
cross-checked against the closed form. Deterministic, no seed.

Measured and printed: the aim angle; for each speed the time the dart
crosses the target's x (closed form D / (v cos theta) and RK4), the drop
of the dart below its aim line and the drop of the target below its
start at that moment, the miss distance at closest approach, the dart
height at the hit, the largest difference between the two drops over
the whole flight; the slowest dart that still hits before the target
reaches the ground (closed form and a bracketing search); the miss of a
dart aimed 1 degree high and 1 degree low; the miss if the target did
not drop; a half-step check; the on-screen text widths.

usage: monkeyhunter.py [--measure-only] [--frames t1,t2,...]
"""

from __future__ import annotations

import json
import math
import os
import subprocess
import sys
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

# Layout: overlay at y 96 (captions.py), title rows at y 190/252/314 for
# the first seconds, two panels (30 m/s on top, 60 m/s below) with the
# launcher at the lower left and the target at the upper right, captions
# at caption_y 0.75 (y 1440..1520), payoff card under them.
PANELS = {
    "slow": {"label_y": 372, "ground_y": 832, "colour": TEAL, "speed": "slow_speed"},
    "fast": {"label_y": 932, "ground_y": 1392, "colour": GOLD, "speed": "fast_speed"},
}
X0 = 80.0  # launcher x in px
SS = 2  # supersampling of the geometry layer
GEOM_Y0, GEOM_Y1 = 336, 1436
PAYOFF_Y = 1592.0
TARGET_R = 16.0
BRACKET_DX = 26.0
HOOK_LEN = 40.0


def blend(col, a, base=BG):
    a = max(0.0, min(1.0, a))
    return tuple(int(round(c * a + b * (1 - a))) for c, b in zip(col, base))


def simulate(man: dict, v: float, aim: float, dt: float, drop: bool = True) -> dict:
    """Dart from the origin at speed v along the angle aim; target from (D, H), let go at t = 0 if drop.

    State: dart x, y, vx, vy, target x, y, vx, vy. RK4 at a fixed step up
    to sim_t_max; bodies keep falling through the ground (the ground
    crossings are measured separately).
    """
    g, D, Hy = man["g"], man["distance_m"], man["height_m"]
    n = int(round(man["sim_t_max"] / dt))
    s = np.array([0.0, 0.0, v * math.cos(aim), v * math.sin(aim), D, Hy, 0.0, 0.0])
    acc = np.array([0.0, 0.0, 0.0, -g, 0.0, 0.0, 0.0, -g if drop else 0.0])

    def deriv(st: np.ndarray) -> np.ndarray:
        return np.array([st[2], st[3], acc[2], acc[3], st[6], st[7], acc[6], acc[7]])

    path = np.empty((n + 1, 8))
    for i in range(n + 1):
        path[i] = s
        if i == n:
            break
        k1 = deriv(s)
        k2 = deriv(s + 0.5 * dt * k1)
        k3 = deriv(s + 0.5 * dt * k2)
        k4 = deriv(s + dt * k3)
        s = s + dt / 6.0 * (k1 + 2 * k2 + 2 * k3 + k4)
    return {"path": path, "dt": dt, "v": v, "aim": aim, "drop": drop}


def hermite(p0: float, m0: float, p1: float, m1: float, dt: float, f: float) -> float:
    """Cubic Hermite value a fraction f into a step of length dt (exact for a parabola)."""
    h00 = 2 * f ** 3 - 3 * f ** 2 + 1
    h10 = f ** 3 - 2 * f ** 2 + f
    h01 = -2 * f ** 3 + 3 * f ** 2
    h11 = f ** 3 - f ** 2
    return h00 * p0 + h10 * dt * m0 + h01 * p1 + h11 * dt * m1


def ground_time(path: np.ndarray, col: int, dt: float) -> float | None:
    """First time the body in column col (y index) goes below y = 0, linear inside the step."""
    y = path[:, col]
    idx = np.nonzero((y[:-1] > 0.0) & (y[1:] <= 0.0))[0]
    if len(idx) == 0:
        return None
    i = int(idx[0])
    f = y[i] / (y[i] - y[i + 1])
    return (i + f) * dt


def analyse(man: dict, run: dict) -> dict:
    """Crossing of the target's x, the drops there, and the closest approach while both are in the air."""
    g, D, Hy = man["g"], man["distance_m"], man["height_m"]
    p, dt = run["path"], run["dt"]
    run["t_ground_target"] = ground_time(p, 5, dt)
    run["t_ground_dart"] = ground_time(p, 1, dt)
    idx = np.nonzero(p[:, 0] >= D)[0]
    if len(idx) == 0:
        run["t_cross"] = None
        return run
    i = int(idx[0])
    f = (D - p[i - 1, 0]) / (p[i, 0] - p[i - 1, 0])  # x is linear in t
    run["t_cross"] = (i - 1 + f) * dt
    run["i_cross"] = i - 1 + f
    yd = hermite(p[i - 1, 1], p[i - 1, 3], p[i, 1], p[i, 3], dt, f)
    yt = hermite(p[i - 1, 5], p[i - 1, 7], p[i, 5], p[i, 7], dt, f)
    run["y_dart_cross"], run["y_target_cross"] = yd, yt
    run["gap_cross"] = yd - yt  # positive: the dart passes above the target
    run["drop_dart"] = D * math.tan(run["aim"]) - yd  # below the aim line at x = D
    run["drop_target"] = Hy - yt
    run["v_cross"] = math.hypot(p[i, 2], hermite(p[i - 1, 3], -g, p[i, 3], -g, dt, f))
    # Closest approach while both bodies are above the ground: the relative
    # motion is uniform when both fall, so the minimum inside a step is the
    # closed-form point on the segment between samples.
    t_air = min(t for t in (run["t_ground_target"], run["t_ground_dart"], man["sim_t_max"]) if t is not None)
    n_air = max(2, int(t_air / dt))
    rel = p[:n_air, 0:2] - p[:n_air, 4:6]
    a, b = rel[:-1], rel[1:] - rel[:-1]
    bb = np.einsum("ij,ij->i", b, b)
    u = np.clip(-np.einsum("ij,ij->i", a, b) / np.where(bb > 0, bb, 1.0), 0.0, 1.0)
    d = np.linalg.norm(a + u[:, None] * b, axis=1)
    k = int(np.argmin(d))
    run["miss"] = float(d[k])
    run["t_miss"] = (k + u[k]) * dt
    # The two drops sampled along the flight up to the crossing.
    m = int(math.floor(run["i_cross"])) + 1
    drop_dart = p[:m, 0] * math.tan(run["aim"]) - p[:m, 1]
    drop_target = Hy - p[:m, 5]
    run["drop_diff_max"] = float(np.max(np.abs(drop_dart - drop_target))) if run["drop"] else None
    return run


def hits_before_ground(man: dict, v: float, aim: float, dt: float) -> bool:
    run = analyse(man, simulate(man, v, aim, dt))
    return run["t_cross"] is not None and run["t_cross"] < run["t_ground_target"]


def measure(man: dict) -> dict:
    g, D, Hy = man["g"], man["distance_m"], man["height_m"]
    fps, sub = man["fps"], man["substeps"]
    dt = 1.0 / (fps * sub)
    aim = math.atan2(Hy, D)
    speeds = {"slow": man["slow_speed"], "fast": man["fast_speed"]}
    print(f"setup: a launcher at the origin, a target hanging {Hy:g} m up and {D:g} m away, the dart aimed straight "
          f"at the target's start and fired at {speeds['slow']:g} m/s (top) and {speeds['fast']:g} m/s (bottom); the "
          f"target is let go from rest at t = 0, the instant the dart leaves; g = {g:g} m/s^2, no air; the dart and the "
          f"target are points; RK4 on both bodies at {fps * sub} steps per second (dt = {dt:.2e} s) to "
          f"{man['sim_t_max']:g} s; deterministic, no seed")
    t_g = math.sqrt(2 * Hy / g)
    print(f"aim angle atan({Hy:g} / {D:g}) = {math.degrees(aim):.3f} degrees (cos {math.cos(aim):.5f}, sin "
          f"{math.sin(aim):.5f}); the target's start is {math.hypot(D, Hy):.3f} m from the muzzle along the aim line; "
          f"a target let go from {Hy:g} m reaches the ground at sqrt(2 H / g) = {t_g:.4f} s")
    out = {"aim": aim, "t_ground": t_g}
    for name, v in speeds.items():
        run = analyse(man, simulate(man, v, aim, dt))
        out[name] = run
        t_cf = D / (v * math.cos(aim))
        fall_cf = 0.5 * g * t_cf * t_cf
        print(f"dart at {v:g} m/s: crosses the target's x at {run['t_cross']:.4f} s (closed form D / (v cos theta) = "
              f"{t_cf:.4f} s); at that moment the dart is {run['drop_dart']:.4f} m below its aim line and the target "
              f"{run['drop_target']:.4f} m below its start (closed form g t^2 / 2 = {fall_cf:.4f} m; the two drops differ "
              f"by {(run['drop_dart'] - run['drop_target']) * 1e6:+.3f} micrometres); dart height {run['y_dart_cross']:.4f} m, "
              f"target height {run['y_target_cross']:.4f} m, gap {run['gap_cross']:+.6f} m; miss at closest approach "
              f"{run['miss']:.6f} m at {run['t_miss']:.4f} s; dart speed at the hit {run['v_cross']:.2f} m/s; over the "
              f"whole flight the dart's drop below its aim line and the target's drop differ by at most "
              f"{run['drop_diff_max'] * 1e6:.3f} micrometres; on screen at 1/{man['slow_motion']:g} speed the flight lasts "
              f"{run['t_cross'] * man['slow_motion']:.2f} s")
    v_min_cf = D / (math.cos(aim) * t_g)
    lo, hi = 10.0, 20.0
    assert not hits_before_ground(man, lo, aim, dt) and hits_before_ground(man, hi, aim, dt)
    while hi - lo > 1e-4:
        mid = 0.5 * (lo + hi)
        if hits_before_ground(man, mid, aim, dt):
            hi = mid
        else:
            lo = mid
    v_min = 0.5 * (lo + hi)
    short = analyse(man, simulate(man, man["check_short_speed"], aim, dt))
    i_g = int(short["t_ground_dart"] / dt)
    print(f"slowest dart that still hits before the target reaches the ground: closed form D / (cos theta sqrt(2 H / g)) = "
          f"{v_min_cf:.3f} m/s; bracketing search between {10.0:g} and {20.0:g} m/s to {1e-4:g} m/s gives {v_min:.3f} m/s; at "
          f"{man['check_short_speed']:g} m/s the dart reaches the ground at {short['t_ground_dart']:.4f} s, "
          f"{D - short['path'][i_g, 0]:.2f} m short of the target's x, while the target is still "
          f"{short['path'][i_g, 5]:.2f} m up; the target reaches the ground at {short['t_ground_target']:.4f} s; closest "
          f"approach while both are in the air {short['miss']:.3f} m")
    off = man["check_aim_offset_deg"]
    misses = {}
    for sign, word in ((1, "high"), (-1, "low")):
        a2 = aim + sign * math.radians(off)
        run = analyse(man, simulate(man, speeds["slow"], a2, dt))
        run60 = analyse(man, simulate(man, speeds["fast"], a2, dt))
        gap_cf = D * (math.tan(a2) - math.tan(aim))
        miss_cf = math.hypot(D, Hy) * math.sin(math.radians(off))
        misses[word] = run
        print(f"aimed {off:g} degree {word} at {speeds['slow']:g} m/s: when the dart crosses the target's x at "
              f"{run['t_cross']:.4f} s it passes {abs(run['gap_cross']):.4f} m {'above' if run['gap_cross'] > 0 else 'below'} "
              f"the target (closed form D (tan(theta {'+' if sign > 0 else '-'} {off:g} degree) - tan theta) = "
              f"{abs(gap_cf):.4f} m); miss at closest approach {run['miss']:.4f} m at {run['t_miss']:.4f} s (closed form "
              f"sqrt(D^2 + H^2) sin({off:g} degree) = {miss_cf:.4f} m); the same aim at {speeds['fast']:g} m/s misses by "
              f"{run60['miss']:.4f} m: the miss does not depend on the speed")
    fixed = {}
    for name, v in speeds.items():
        run = analyse(man, simulate(man, v, aim, dt, drop=False))
        fixed[name] = run
    print(f"if the target did not drop: the {speeds['slow']:g} m/s dart crosses the target's x "
          f"{-fixed['slow']['gap_cross']:.3f} m below it (closest approach {fixed['slow']['miss']:.3f} m at "
          f"{fixed['slow']['t_miss']:.4f} s); the {speeds['fast']:g} m/s dart {-fixed['fast']['gap_cross']:.3f} m below "
          f"(closest approach {fixed['fast']['miss']:.3f} m)")
    half = analyse(man, simulate(man, speeds["slow"], aim, dt / 2))
    print(f"check at half the time step ({2 * fps * sub} steps per second): the {speeds['slow']:g} m/s dart crosses at "
          f"{half['t_cross']:.4f} s, both fallen {half['drop_target']:.4f} m, miss {half['miss']:.6f} m "
          f"({half['drop_target'] - out['slow']['drop_target']:+.2e} m and {half['miss'] - out['slow']['miss']:+.2e} m "
          f"against the full step)")
    out["v_min"] = v_min
    out["fall_slow"] = out["slow"]["drop_target"]
    return out


class Renderer:
    def __init__(self, man: dict, meas: dict):
        self.man, self.meas = man, meas
        self.fps = man["fps"]
        font = os.environ["SEED_ZERO_FONT"]
        self.font = ImageFont.truetype(font, 40)
        self.font_title = ImageFont.truetype(font, 56)
        self.font_read = ImageFont.truetype(font, 36)
        self.font_clock = ImageFont.truetype(font, 32)
        self.font_small = ImageFont.truetype(font, 28)
        self.first = None
        self.pxm = float(man["px_per_m"])
        self.slow = float(man["slow_motion"])
        total = int(round(man["scene_duration"] * self.fps))
        self.frames_per_cycle = total // man["cycles"]
        assert self.frames_per_cycle * man["cycles"] == total, "cycles must divide the frame count"
        self.cycle = self.frames_per_cycle / self.fps
        self.labels = {name: f"dart at {man[p['speed']]:g} m/s" for name, p in PANELS.items()}
        widths = {"overlay@34": (ImageFont.truetype(font, 34), man["overlay"])}
        for j, line in enumerate(man["title"].split("|")):
            widths[f"title line {j + 1}@56"] = (self.font_title, line)
        for name, label in self.labels.items():
            widths[f"label {name}@40"] = (self.font, label)
        widths["readout@36"] = (self.font_read, "miss: 0.000 m")
        widths["hit@32"] = (self.font_clock, "hit")
        widths["bracket label@28"] = (self.font_small, f"fallen {meas['fall_slow']:.2f} m")
        widths["clock@32"] = (self.font_clock, "0.745 s")
        widths["note@28"] = (self.font_small, f"1/{self.slow:g} speed")
        for j, line in enumerate(self.payoff_lines()):
            widths[f"payoff line {j + 1}@40"] = (self.font, line)
        print("text widths: " + ", ".join(f"{k} {f.getlength(s):.0f} px" for k, (f, s) in widths.items()))
        hold = man["reset_hold"]
        hits = {name: hold + meas[name]["t_cross"] * self.slow for name in PANELS}
        print(f"video: 1/{self.slow:g} speed; {man['cycles']} shots of {self.cycle:.3f} s each, both darts fired "
              f"{hold:g} s into each cycle; the {man['fast_speed']:g} m/s dart hits {hits['fast']:.2f} s into the cycle and "
              f"freezes, the {man['slow_speed']:g} m/s dart hits at {hits['slow']:.2f} s and freezes to the reset at "
              f"{self.cycle:.2f} s; the {man['slow_speed']:g} m/s hits fall at "
              + ", ".join(f"{k * self.cycle + hits['slow']:.2f}" for k in range(man["cycles"]))
              + f" s of video; payoff card at {man['payoff_t']:g} s; loop crossfade over the last {man['loop_fade']:g} s")

    def payoff_lines(self) -> list[str]:
        text = self.man["payoff_text"].format(fall=self.meas["fall_slow"])
        return [s.strip() for s in text.split("|")]

    def cycle_time(self, f: int) -> float:
        return (f % self.frames_per_cycle) / self.fps

    def sim_time(self, f: int) -> float:
        return max(0.0, (self.cycle_time(f) - self.man["reset_hold"]) / self.slow)

    def to_screen(self, p: dict, x: float, y: float) -> tuple[float, float]:
        return X0 + x * self.pxm, p["ground_y"] - y * self.pxm

    def layer_xy(self, sx: float, sy: float) -> tuple[float, float]:
        return sx * SS, (sy - GEOM_Y0) * SS

    def dashed(self, d: ImageDraw.ImageDraw, a: tuple, b: tuple, col, dash: float, gap: float, width: int) -> None:
        ax, ay = a
        bx, by = b
        L = math.hypot(bx - ax, by - ay)
        ux, uy = (bx - ax) / L, (by - ay) / L
        s = 0.0
        while s < L:
            e = min(L, s + dash)
            d.line((ax + ux * s, ay + uy * s, ax + ux * e, ay + uy * e), fill=col, width=width)
            s = e + gap

    def dart(self, d: ImageDraw.ImageDraw, cx: float, cy: float, ux: float, uy: float, col) -> None:
        """A dart 34 px long and 10 px wide (screen px), pointing along (ux, uy) in layer coordinates."""
        L, r = 34.0 * SS, 5.0 * SS
        px, py = -uy, ux
        tail = (cx - ux * L / 2, cy - uy * L / 2)
        neck = (cx + ux * (L / 2 - 12 * SS), cy + uy * (L / 2 - 12 * SS))
        d.line((tail, neck), fill=col, width=int(2 * r))
        d.ellipse((tail[0] - r, tail[1] - r, tail[0] + r, tail[1] + r), fill=col)
        tip = (cx + ux * L / 2, cy + uy * L / 2)
        d.polygon([tip, (neck[0] + px * r * 1.4, neck[1] + py * r * 1.4), (neck[0] - px * r * 1.4, neck[1] - py * r * 1.4)],
                  fill=col)

    def bracket(self, d: ImageDraw.ImageDraw, sx: float, y_top: float, y_bot: float, dx: float, col) -> None:
        """A [ or ] bracket from y_top to y_bot beside x = sx (dx < 0 opens right, dx > 0 opens left)."""
        x1 = sx + dx
        pts = [(sx, y_top), (x1, y_top), (x1, y_bot), (sx, y_bot)]
        d.line([self.layer_xy(*p) for p in pts], fill=col, width=3 * SS, joint="curve")

    def draw_scene(self, f: int, title_on: bool) -> Image.Image:
        man, meas = self.man, self.meas
        D, Hy = man["distance_m"], man["height_m"]
        aim = meas["aim"]
        img = Image.new("RGB", (W, H), BG)
        layer = Image.new("RGB", (W * SS, (GEOM_Y1 - GEOM_Y0) * SS), BG)
        ld = ImageDraw.Draw(layer)
        texts = []
        c = self.cycle_time(f)
        s = self.sim_time(f)
        for name, p in PANELS.items():
            run = meas[name]
            col = p["colour"]
            path, dt = run["path"], run["dt"]
            hit = s >= run["t_cross"]
            s_draw = min(s, run["t_cross"])
            if hit:
                xd, yd = D, run["y_dart_cross"]
                xt, yt = D, run["y_target_cross"]
                i = int(math.floor(run["i_cross"]))
                vx, vy = path[i, 2], path[i, 3]
                i_trail = i
            else:
                q = s_draw / dt
                i = min(int(q), len(path) - 2)
                fr = q - i
                st = path[i] + fr * (path[i + 1] - path[i])
                xd, yd, vx, vy = st[0], st[1], st[2], st[3]
                xt, yt = st[4], st[5]
                i_trail = i
            # Ground, launcher, aim line, hook.
            mx, my = self.to_screen(p, 0.0, 0.0)
            tx0, ty0 = self.to_screen(p, D, Hy)
            ld.rectangle((*self.layer_xy(mx - 44, my), *self.layer_xy(mx + 12, my + 14)), fill=WIRE)
            ld.line((self.layer_xy(mx - 36 * math.cos(aim), my + 36 * math.sin(aim)),
                     self.layer_xy(mx + 22 * math.cos(aim), my - 22 * math.sin(aim))),
                    fill=(150, 160, 176), width=14 * SS)
            ld.line((self.layer_xy(40, p["ground_y"]), self.layer_xy(W - 40, p["ground_y"])), fill=FLOOR, width=4 * SS)
            self.dashed(ld, self.layer_xy(mx, my), self.layer_xy(tx0, ty0), blend(MUTED, 0.55), 14 * SS, 10 * SS, 2 * SS)
            ld.line((self.layer_xy(tx0, ty0 - HOOK_LEN), self.layer_xy(tx0, ty0 - TARGET_R)), fill=WIRE, width=4 * SS)
            ld.line((self.layer_xy(tx0 - 14, ty0 - HOOK_LEN), self.layer_xy(tx0 + 14, ty0 - HOOK_LEN)), fill=WIRE, width=4 * SS)
            # Positions on screen.
            sxd, syd = self.to_screen(p, xd, yd)
            sxt, syt = self.to_screen(p, xt, yt)
            drop = Hy - yt
            if drop > 0.005:
                r = TARGET_R * SS
                lx, ly = self.layer_xy(tx0, ty0)
                ld.ellipse((lx - r, ly - r, lx + r, ly + r), outline=GHOST, width=2 * SS)
            # Brackets: the dart's drop below its aim line and the target's drop below its start.
            drop_dart = xd * math.tan(aim) - yd
            if drop_dart > 0.005:
                sya = p["ground_y"] - xd * math.tan(aim) * self.pxm
                self.bracket(ld, sxd, sya, syd, -BRACKET_DX, blend(col, 0.85))
            if drop_dart > 0.12:  # the label clears the launcher once the dart is well up
                texts.append(((min(max(sxd, 150.0), W - 150.0), syd + 40), f"fallen {drop_dart:.2f} m", self.font_small, col, "mm"))
            if drop > 0.005:
                self.bracket(ld, sxt, ty0, syt, BRACKET_DX, blend(CORAL, 0.85))
                texts.append(((sxt + BRACKET_DX + 12, 0.5 * (ty0 + syt)), f"fallen {drop:.2f} m", self.font_small, CORAL, "lm"))
            # Trail, target, dart.
            n_tr = int(man["trail_s"] / dt)
            pts = []
            for k in range(8, -1, -1):
                j = max(0, i_trail - k * n_tr // 8)
                pts.append(self.layer_xy(*self.to_screen(p, path[j, 0], path[j, 1])))
            for k in range(len(pts) - 1):
                ld.line((pts[k], pts[k + 1]), fill=blend(col, 0.12 + 0.4 * k / (len(pts) - 1)), width=4 * SS)
            r = TARGET_R * SS
            lx, ly = self.layer_xy(sxt, syt)
            ld.ellipse((lx - r, ly - r, lx + r, ly + r), fill=CORAL, outline=(150, 50, 46), width=2 * SS)
            ld.ellipse((lx - r * 0.35, ly - r * 0.35, lx + r * 0.35, ly + r * 0.35), fill=WHITE)
            vn = math.hypot(vx, vy)
            lxd, lyd = self.layer_xy(sxd, syd)
            self.dart(ld, lxd, lyd, vx / vn, -vy / vn, col)
            if hit:
                u = (c - (man["reset_hold"] + run["t_cross"] * self.slow)) / man["hit_flash"]
                if 0.0 <= u < 1.0:
                    rr = (22 + 70 * u) * SS
                    ld.ellipse((lxd - rr, lyd - rr, lxd + rr, lyd + rr), outline=blend(WHITE, 1 - u), width=4 * SS)
                texts.append(((sxd - 44, syd - 30), "hit", self.font_clock, WHITE, "rm"))
                texts.append(((W - 40, p["label_y"]), f"miss: {run['miss']:.3f} m", self.font_read, TEXT, "rm"))
            texts.append(((40, p["label_y"]), self.labels[name], self.font, col, "lm"))
            texts.append(((W - 40, p["ground_y"] - 58), f"{s_draw:.3f} s", self.font_clock, TEXT, "rm"))
            texts.append(((W - 40, p["ground_y"] - 24), f"1/{self.slow:g} speed", self.font_small, MUTED, "rm"))
        img.paste(layer.reduce(SS), (0, GEOM_Y0))
        d = ImageDraw.Draw(img)
        for xy, text, font, fill, anchor in texts:
            d.text(xy, text, font=font, fill=fill, anchor=anchor)
        return img

    def live_frame(self, f: int) -> np.ndarray:
        man = self.man
        t = f / self.fps
        title_on = t < man["title_until"]
        img = self.draw_scene(f, title_on)
        d = ImageDraw.Draw(img)
        if title_on:
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
        for f in range(total):
            proc.stdin.write(self.frame_at(f).tobytes())
            if f % 300 == 0:
                print(f"frame {f}/{total}", file=sys.stderr)
        proc.stdin.close()
        if proc.wait() != 0:
            raise RuntimeError("ffmpeg failed")
        print(f"footage: {out_path} ({total / self.fps:.2f}s at {self.fps} fps)")


def main() -> None:
    man = json.loads((ROOT / "projects/monkeyhunter/manifest.json").read_text())
    meas = measure(man)
    if "--measure-only" in sys.argv:
        return
    if "--frames" in sys.argv:
        times = [float(v) for v in sys.argv[sys.argv.index("--frames") + 1].split(",")]
        r = Renderer(man, meas)
        for tv in times:
            Image.fromarray(r.frame_at(int(round(tv * man["fps"])))).save(ROOT / f"media/monkeyhunter/smoke-{tv}.png")
        print("smoke frames: " + ", ".join(f"{tv}" for tv in times))
        return
    Renderer(man, meas).render(ROOT / "media/monkeyhunter/footage.mp4")


if __name__ == "__main__":
    main()
