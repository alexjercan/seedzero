#!/usr/bin/env python3
"""Roll a coin around a coin. How many times does it turn?

A coin of radius r rolls without slipping around a fixed coin of the
same radius R = r (top panel), and the same coin rolls along a flat
strip exactly as long as the fixed coin's rim, 2 pi R, drawn as that rim
unrolled (bottom panel). The contact point advances along the fixed rim
(or the strip) at a set speed v, the same on both panels, so both rolls
finish at the same instant. The centre of the rolling coin moves on a
circle of radius R + r. No slip means the point of the rolling coin that
touches the rim is at rest, so the coin spins at |v_c| / r with v_c =
(R + r) v / R its centre's speed, and the arrow on its face turns
phi = s / r + s / R = theta (1 + R / r) in the lab, theta = s / R being
the angle of the line of centres. One lap (s = 2 pi R) gives phi =
2 pi (R / r + 1) = 4 pi for R = r, exactly 2 turns, and the arrow is
upright again halfway around, at theta = pi. Along the strip the same
coin turns phi = s / r = 2 pi, exactly 1 turn. The extra turn around the
coin is the lap of the line of centres itself: the centre's path,
2 pi (R + r), is twice the coin's own circumference.

Each lap rolls for roll_s seconds and then holds at the end with the
counters lit; at the lap boundary the strip coin jumps back to the start
and the counters reset. The lap is a whole number of frames and divides
the scene, so the scene is exactly periodic and the last frame equals
the first. Kinematics only, deterministic, no seed.

Measured and printed from the sampled positions: the arrow's lab angle
over a lap on both panels against the closed form, the count of returns
to upright per lap, where the arrow is first upright again, the no-slip
checks (the arc rolled on the moving coin's rim against the arc covered
on the fixed rim or the strip, and the speed of the material point at
the contact), the centre's path length against the coin's circumference,
the same counts around a coin of twice and three times the radius for
the description, the schedule in video time, the loop check and the
on-screen text widths.

usage: coinroll.py [--measure-only] [--frames t1,t2,...]
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
RIM = (96, 108, 126)
FACE = (34, 40, 50)
COIN = (240, 176, 84)
COIN_EDGE = (168, 112, 36)
ARROW = (20, 18, 16)

# Layout: overlay at y 96..130 (captions.py), three title rows at y 172/234/296
# for the first seconds, then the legend at y 236 and the tag at y 290; the
# top panel's label at y 360 (left-aligned at x 40), the fixed coin centred at
# fixed_centre_px with the rolling coin going around it (radius 3 r from the
# centre, y 400..1000 for r = 100 px), the turns counter on the fixed coin's
# face; the bottom panel's label at y 1086, the strip's top surface at strip_y
# (1331) with the coin rolling on it (top at 1131), the ticks under the strip
# to 1357 and the strip's turns counter at y 1392; the geometry band y
# 330..1420 drawn at 2x and reduced; captions at caption_y 0.75 (y
# 1440..1520); the card from y 1592.
LEGEND_Y, TAG_Y = 236, 290
LABEL_A_Y, LABEL_B_Y = 360, 1086
GEOM_Y0, GEOM_Y1 = 330, 1420
SS = 2
PAYOFF_Y = 1592.0
COUNTER_B_Y = 1392
PANELS = ("around", "along")
TWO_PI = 2.0 * math.pi


def blend(col, a: float, base=BG) -> tuple:
    a = max(0.0, min(1.0, a))
    return tuple(int(round(c * a + b * (1 - a))) for c, b in zip(col, base))


def direction(a) -> tuple:
    """Unit vector at angle a measured clockwise from up, in x-right y-up coordinates."""
    return np.sin(a), np.cos(a)


# --- measurement --------------------------------------------------------------
def roll(R: float, r: float, v: float, duration: float, n: int, strip: bool) -> dict:
    """Sample one roll at n steps. The contact point advances at speed v along the fixed
    rim (around) or along the strip (along); the rolling coin's spin follows from no slip
    (its contact point is at rest, omega = |v_c| / r). Every check is computed from the
    sampled positions."""
    dt = duration / n
    t = np.arange(n + 1) * dt
    s = v * t                                    # arc covered on the fixed rim or the strip
    if strip:
        theta = np.zeros_like(s)
        cx, cy = s.copy(), np.full_like(s, r)
        v_c = v
    else:
        theta = s / R                            # the line of centres
        ux, uy = direction(theta)
        cx, cy = (R + r) * ux, (R + r) * uy
        v_c = (R + r) * v / R                    # the centre's speed
    omega = np.full_like(s, v_c / r)
    phi = np.concatenate([[0.0], np.cumsum(0.5 * (omega[1:] + omega[:-1]) * dt)])   # the arrow's lab angle
    # Returns to upright: phi reaches 2 pi k, k >= 1, interpolated between samples.
    ks = [k for k in range(1, 64) if TWO_PI * k <= phi[-1] + 1e-9]
    ups = [{"k": k, "t": float(np.interp(TWO_PI * k, phi, t)), "s": float(np.interp(TWO_PI * k, phi, s)),
            "theta": float(np.interp(TWO_PI * k, phi, theta))} for k in ks]
    # The centre's path from the chords between samples.
    path = float(np.sum(np.hypot(np.diff(cx), np.diff(cy))))
    # No slip, check 1: the arc of the rolling rim that has touched, r (phi - theta), against the
    # arc covered on the fixed rim R theta (or the strip, s).
    arc_err = float(np.max(np.abs(r * (phi - theta) - s)))
    # No slip, check 2: the material point of the rolling coin at the contact, followed over one
    # sample either side, moves at (q(t + dt) - q(t - dt)) / 2 dt; it should be at rest.
    beta = theta + math.pi - phi                 # body angle of the contact point (from the arrow)
    res = 0.0
    for i in range(1, len(s) - 1, max(1, len(s) // 4000)):
        b = beta[i]
        ax, ay = cx[i - 1] + r * math.sin(phi[i - 1] + b), cy[i - 1] + r * math.cos(phi[i - 1] + b)
        bx, by = cx[i + 1] + r * math.sin(phi[i + 1] + b), cy[i + 1] + r * math.cos(phi[i + 1] + b)
        res = max(res, math.hypot(bx - ax, by - ay) / (2.0 * dt))
    return {"t": t, "s": s, "theta": theta, "phi": phi, "ups": ups, "path": path, "arc_err": arc_err,
            "slip": res / v, "dt": dt, "v_c": v_c, "phi_end": float(phi[-1])}


def measure(man: dict) -> dict:
    fps, D = man["fps"], man["scene_duration"]
    r = 1.0                                       # the rolling coin's radius, the unit of length
    R = man["fixed_radius_ratio"] * r
    lap, roll_s, laps = man["lap_s"], man["roll_s"], man["laps"]
    hold = lap - roll_s
    assert abs(laps * lap - D) < 1e-9, "the laps must fill the scene"
    for key in ("lap_s", "roll_s", "lap_at"):
        assert abs(man[key] * fps - round(man[key] * fps)) < 1e-9, f"{key} must be a whole number of frames"
    n = int(round(roll_s * fps * man["substeps"]))
    v = TWO_PI * R / roll_s                       # contact speed, the same on both panels
    print(f"setup: a coin of radius r rolls without slipping around a fixed coin of radius R = {R:g} r (the "
          f"same size), and the same coin rolls along a flat strip of length 2 pi R = {TWO_PI * R:.4f} r, the "
          f"fixed rim unrolled; the contact point advances at v = {v:.4f} r/s on both panels, so a lap of the "
          f"rim and the strip both take {roll_s:g} s ({roll_s * fps:.0f} frames), then both hold {hold:g} s at "
          f"the end; {laps} laps of {lap:g} s in {D:g} s; sampled at {man['substeps']} steps per frame "
          f"(dt = {roll_s / n:.2e} s); drawn at {man['coin_radius_px']:g} px per r; kinematics only, "
          f"deterministic, no seed")
    ar = roll(R, r, v, roll_s, n, strip=False)
    al = roll(R, r, v, roll_s, n, strip=True)
    u1 = ar["ups"][0]
    print(f"around: over one lap (s = 2 pi R = {ar['s'][-1]:.4f} r) the arrow's lab angle grows to "
          f"{ar['phi_end']:.4f} rad = {ar['phi_end'] / math.pi:.4f} pi = {ar['phi_end'] / TWO_PI:.4f} turns "
          f"(closed form 2 pi (R / r + 1) = {TWO_PI * (R / r + 1) / math.pi:.4f} pi); the arrow is upright again "
          f"{len(ar['ups'])} times per lap: first at s = {u1['s']:.4f} r = {u1['s'] / ar['s'][-1]:.4f} of the "
          f"rim, theta = {math.degrees(u1['theta']):.2f} degrees, {u1['t']:.3f} s into the roll (halfway, on the "
          f"far side; closed form s = 2 pi R r / (R + r) = {TWO_PI * R * r / (R + r):.4f} r)"
          + "".join(f", then at s = {u['s']:.4f} r, theta = {math.degrees(u['theta']):.2f} degrees, {u['t']:.3f} s"
                    for u in ar["ups"][1:])
          + f" (back at the start); relative to the line of centres the coin turns s / r = "
          f"{(ar['phi_end'] - ar['theta'][-1]) / TWO_PI:.4f} turn per lap and the line of centres itself turns "
          f"{ar['theta'][-1] / TWO_PI:.4f} turn: {ar['phi_end'] / TWO_PI:.4f} in all")
    print(f"along: the same coin rolls the strip (s = 2 pi R = {al['s'][-1]:.4f} r) at the same contact speed in "
          f"{roll_s:g} s; the arrow's lab angle grows to {al['phi_end']:.4f} rad = {al['phi_end'] / math.pi:.4f} "
          f"pi = {al['phi_end'] / TWO_PI:.4f} turn (closed form s / r = 2 pi); upright again {len(al['ups'])} "
          f"time per strip, at s = {al['ups'][0]['s']:.4f} r, the end of the strip, {al['ups'][0]['t']:.3f} s")
    print(f"no slip: the arc of the rolling coin's rim that has touched, r (phi - theta), matches the arc covered "
          f"on the fixed rim, R theta, within {ar['arc_err']:.1e} r at every sample around, and r phi matches s "
          f"within {al['arc_err']:.1e} r along; the material point of the rolling coin at the contact moves at "
          f"most {ar['slip']:.1e} v around and {al['slip']:.1e} v along (central differences over "
          f"{2 * ar['dt']:.1e} s): it rests on the rim, it rolls, it does not slide; at the end of a lap the "
          f"whole rim of the rolling coin, 2 pi r = {TWO_PI * r:.4f} r, has touched, {ar['s'][-1] / (TWO_PI * r):.4f} "
          f"times its own rim, so the painted arcs close together")
    print(f"centre: the rolling coin's centre travels {ar['path']:.4f} r per lap around the coin (closed form "
          f"2 pi (R + r) = {TWO_PI * (R + r):.4f} r), {ar['path'] / (TWO_PI * r):.4f} times the coin's own "
          f"circumference 2 pi r = {TWO_PI * r:.4f} r, at {ar['v_c']:.4f} r/s; along the strip it travels "
          f"{al['path']:.4f} r, {al['path'] / (TWO_PI * r):.4f} times, at {al['v_c']:.4f} r/s; the extra turn "
          f"around the coin is the lap of the line of centres")
    descr = []
    for q in man["description_ratios"]:
        Rq = q * r
        vq = TWO_PI * Rq / roll_s
        dq = roll(Rq, r, vq, roll_s, n, strip=False)
        sq = roll(Rq, r, vq, roll_s, n, strip=True)
        descr.append(f"around a coin of {q:g} times the radius the arrow turns {dq['phi_end'] / TWO_PI:.4f} turns "
                     f"per lap (upright again {len(dq['ups'])} times, first at theta = "
                     f"{math.degrees(dq['ups'][0]['theta']):.2f} degrees) against {sq['phi_end'] / TWO_PI:.4f} "
                     f"along a strip as long as that rim (upright {len(sq['ups'])} times); R / r + 1 = {q + 1:g}")
    print("for the description: " + "; ".join(descr) + " (the 1982 SAT keyed 3 for the coin of 3 times the radius)")
    # Schedule in video time.
    la = man["lap_at"]
    bounds = [la + j * lap for j in range(-1, laps + 1) if 0.0 <= la + j * lap < D]
    halfs = [b + u1["t"] for b in bounds if b + u1["t"] < D]
    ends = sorted(t for t in [b + roll_s for b in bounds] + [la - hold] if 0.0 <= t < D)
    p0 = (0.0 - la) % lap
    if p0 < roll_s:
        u0 = p0 / roll_s
        state0 = (f"the coin is {p0:.2f} s into a roll, {100 * u0:.1f} % of the way around (theta = "
                  f"{360 * u0:.0f} degrees), the counters read {u0 * ar['phi_end'] / TWO_PI:.2f} and "
                  f"{u0 * al['phi_end'] / TWO_PI:.2f} turns")
    else:
        state0 = (f"the coin holds at the end of a lap, {p0 - roll_s:.2f} s into the hold, the counters read "
                  f"{ar['phi_end'] / TWO_PI:.2f} and {al['phi_end'] / TWO_PI:.2f} turns")
    print(f"schedule (video time): {laps} laps of {lap:g} s ({lap * fps:.0f} frames), each rolling {roll_s:g} s "
          f"({roll_s * fps:.0f} frames) and holding {hold:g} s at the end; lap boundaries (the strip coin jumps "
          f"back to the start, the counters reset, the painted rims clear) at "
          + ", ".join(f"{t:.1f}" for t in bounds) + " s; the arrow is upright again halfway around at "
          + ", ".join(f"{t:.1f}" for t in halfs) + " s; back at the start with the counters at "
          f"{ar['phi_end'] / TWO_PI:.2f} and {al['phi_end'] / TWO_PI:.2f} (the strip coin at the end of the strip) "
          "at " + ", ".join(f"{t:.1f}" for t in ends) + f" s, holding until the next boundary; on the first frame "
          f"{state0}; title until {man['title_until']:g} s, then the legend and the tag, the counters from "
          f"{man['counters_from']:g} s; payoff "
          f"card from {man['payoff_t']:g} s; the title fades back in over the last {man['loop_fade']:g} s and the "
          f"last frame repeats the first (the scene is periodic: {D:g} s holds exactly {laps} laps)")
    ev = {"R": R, "r": r, "v": v, "around_turns": ar["phi_end"] / TWO_PI, "along_turns": al["phi_end"] / TWO_PI,
          "ups_around": ar["ups"], "ups_along": al["ups"], "half_t": u1["t"]}
    # Text widths.
    font = os.environ["SEED_ZERO_FONT"]
    f28, f34, f40, f56 = (ImageFont.truetype(font, k) for k in (28, 34, 40, 56))
    widths = {"overlay@34": (f34, man["overlay"])}
    for j, line in enumerate(man["title"].split("|")):
        widths[f"title line {j + 1}@56"] = (f56, line)
    widths["legend@40"] = (f40, legend_text())
    widths["tag@28"] = (f28, tag_text())
    for name in PANELS:
        widths[f"label {name}@40"] = (f40, label_text(name))
    widths["counter word@28"] = (f28, "turns")
    widths["counter around@40"] = (f40, counter_text("around", ev["around_turns"]))
    widths["counter along@40"] = (f40, counter_text("along", ev["along_turns"]))
    for j, line in enumerate(payoff_lines(man, ev)):
        widths[f"payoff line {j + 1}@40"] = (f40, line)
    print("text widths: " + ", ".join(f"{k_} {f.getlength(s):.0f} px" for k_, (f, s) in widths.items()))
    assert all(f.getlength(s) < 950 for f, s in widths.values()), "a text line is wider than 950 px"
    coin_keys = ("counter word@28", "counter around@40")
    assert all(widths[k_][0].getlength(widths[k_][1]) < 1.6 * man["coin_radius_px"] for k_ in coin_keys), \
        "the counter does not fit on the fixed coin's face"
    return ev


def legend_text() -> str:
    return "same coin, same size, no slipping"


def tag_text() -> str:
    return "the arrow counts the turns; red is the rim already rolled"


def label_text(name: str) -> str:
    return "around a coin the same size" if name == "around" else "along a flat strip as long as that rim"


def counter_text(name: str, turns: float) -> str:
    return f"{turns:.2f}" if name == "around" else f"turns {turns:.2f}"


def payoff_lines(man: dict, ev: dict) -> list[str]:
    text = man["payoff_text"].format(around=ev["around_turns"], along=ev["along_turns"])
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
        self.ppu = float(man["coin_radius_px"])
        self.R, self.r = ev["R"], ev["r"]
        self.fc = (float(man["fixed_centre_px"][0]), float(man["fixed_centre_px"][1]))
        self.strip_y = float(man["strip_y"])
        self.strip_x0 = W / 2.0 - math.pi * self.R * self.ppu
        self.lap_f = int(round(man["lap_s"] * self.fps))
        self.roll_f = int(round(man["roll_s"] * self.fps))
        self.lap_at_f = int(round(man["lap_at"] * self.fps))

    # --- state helpers ------------------------------------------------------
    def phase(self, f: int) -> tuple[float, bool]:
        """Fraction of the rim covered in the current lap and whether the lap is holding."""
        p = (f - self.lap_at_f) % self.lap_f
        if p < self.roll_f:
            return p / self.roll_f, False
        return 1.0, True

    # --- pixel helpers ------------------------------------------------------
    def L(self, x: float, y: float) -> tuple[float, float]:
        # Rounded to 1e-4 px so equal states draw equal pixels (the periodicity check).
        return round(x * SS, 4), round((y - GEOM_Y0) * SS, 4)

    def bbox(self, cx: float, cy: float, rad: float) -> tuple:
        return self.L(cx - rad, cy - rad) + self.L(cx + rad, cy + rad)

    def arc(self, d: ImageDraw.ImageDraw, cx: float, cy: float, rad: float, a0: float, a1: float, col, width: int) -> None:
        """Arc of a circle from screen direction a0 to a1 clockwise (radians, clockwise from up)."""
        if a1 - a0 >= TWO_PI - 1e-9:
            d.ellipse(self.bbox(cx, cy, rad), outline=col, width=width * SS)
        elif a1 - a0 > 1e-9:
            d.arc(self.bbox(cx, cy, rad), math.degrees(a0) - 90.0, math.degrees(a1) - 90.0, fill=col, width=width * SS)

    def draw_coin(self, d: ImageDraw.ImageDraw, cx: float, cy: float, phi: float, painted: float) -> None:
        """The rolling coin at pixel centre (cx, cy), its arrow at phi (clockwise from up), and the
        arc of its rim that has touched, of angle painted, ending at the contact point phi + pi."""
        rp = self.ppu
        d.ellipse(self.bbox(cx, cy, rp), fill=COIN, outline=COIN_EDGE, width=3 * SS)
        self.arc(d, cx, cy, rp - 8, phi + math.pi - painted, phi + math.pi, CORAL, 8)
        ux, uy = math.sin(phi), math.cos(phi)          # y-up
        tail = (cx - 0.50 * rp * ux, cy + 0.50 * rp * uy)
        neck = (cx + 0.38 * rp * ux, cy - 0.38 * rp * uy)
        tip = (cx + 0.82 * rp * ux, cy - 0.82 * rp * uy)
        d.line([self.L(*tail), self.L(*neck)], fill=ARROW, width=int(0.16 * rp) * SS)
        wd = 0.32 * rp
        b1 = (neck[0] + wd * uy, neck[1] + wd * ux)
        b2 = (neck[0] - wd * uy, neck[1] - wd * ux)
        d.polygon([self.L(*tip), self.L(*b1), self.L(*b2)], fill=ARROW)
        d.ellipse(self.bbox(cx, cy, 0.07 * rp), fill=COIN_EDGE)

    def draw_ghost(self, d: ImageDraw.ImageDraw, cx: float, cy: float) -> None:
        """A faint outline of the coin with its arrow up: where the arrow was upright again."""
        rp = self.ppu
        col = blend(GOLD, 0.55)
        d.ellipse(self.bbox(cx, cy, rp), outline=col, width=3 * SS)
        d.line([self.L(cx, cy + 0.45 * rp), self.L(cx, cy - 0.45 * rp)], fill=col, width=6 * SS)
        d.polygon([self.L(cx, cy - 0.82 * rp), self.L(cx + 0.28 * rp, cy - 0.40 * rp),
                   self.L(cx - 0.28 * rp, cy - 0.40 * rp)], fill=col)

    def draw_around(self, d: ImageDraw.ImageDraw, u: float) -> dict:
        R, r, ppu = self.R, self.r, self.ppu
        fx, fy = self.fc
        s = u * TWO_PI * R
        theta = s / R
        phi = s / r + s / R
        # The centre's path (faint) and the trail so far (teal).
        d.ellipse(self.bbox(fx, fy, (R + r) * ppu), outline=blend(RIM, 0.45), width=2 * SS)
        self.arc(d, fx, fy, (R + r) * ppu, 0.0, theta, TEAL, 4)
        # The fixed coin: face, rim, ticks, the painted arc, the start notch.
        d.ellipse(self.bbox(fx, fy, R * ppu), fill=FACE, outline=RIM, width=3 * SS)
        for k in range(self.man["rim_ticks"]):
            a = TWO_PI * k / self.man["rim_ticks"]
            ux, uy = math.sin(a), math.cos(a)
            p0 = self.L(fx + (R * ppu - 18) * ux, fy - (R * ppu - 18) * uy)
            p1 = self.L(fx + (R * ppu - 4) * ux, fy - (R * ppu - 4) * uy)
            d.line([p0, p1], fill=RIM, width=3 * SS)
        self.arc(d, fx, fy, R * ppu - 8, 0.0, theta, CORAL, 8)
        d.line([self.L(fx, fy - R * ppu - 10), self.L(fx, fy - R * ppu + 22)], fill=GOLD, width=4 * SS)
        # Ghosts where the arrow was upright again, then the coin.
        for up in self.ev["ups_around"]:
            if s >= up["s"] - 1e-9:
                ux, uy = math.sin(up["theta"]), math.cos(up["theta"])
                self.draw_ghost(d, fx + (R + r) * ppu * ux, fy - (R + r) * ppu * uy)
        ux, uy = math.sin(theta), math.cos(theta)
        cx, cy = fx + (R + r) * ppu * ux, fy - (R + r) * ppu * uy
        self.draw_coin(d, cx, cy, phi, s / r)
        return {"turns": phi / TWO_PI}

    def draw_along(self, d: ImageDraw.ImageDraw, u: float) -> dict:
        R, r, ppu = self.R, self.r, self.ppu
        x0, y0 = self.strip_x0, self.strip_y
        s = u * TWO_PI * R
        phi = s / r
        length = TWO_PI * R * ppu
        # The strip: the fixed rim unrolled, with the same ticks, the painted part and the start notch.
        d.rectangle(self.L(x0, y0) + self.L(x0 + length, y0 + 8), fill=RIM)
        if s > 1e-9:
            d.rectangle(self.L(x0, y0) + self.L(x0 + s * ppu, y0 + 8), fill=CORAL)
        for k in range(self.man["rim_ticks"] + 1):
            x = x0 + length * k / self.man["rim_ticks"]
            d.line([self.L(x, y0 + 8), self.L(x, y0 + (26 if k in (0, self.man["rim_ticks"]) else 20))],
                   fill=RIM, width=3 * SS)
        d.line([self.L(x0, y0 - 10), self.L(x0, y0 + 26)], fill=GOLD, width=4 * SS)
        # The centre's path (faint) and the trail so far.
        d.line([self.L(x0, y0 - r * ppu), self.L(x0 + length, y0 - r * ppu)], fill=blend(RIM, 0.45), width=2 * SS)
        if s > 1e-9:
            d.line([self.L(x0, y0 - r * ppu), self.L(x0 + s * ppu, y0 - r * ppu)], fill=TEAL, width=4 * SS)
        for up in self.ev["ups_along"]:
            if s >= up["s"] - 1e-9:
                self.draw_ghost(d, x0 + up["s"] * ppu, y0 - r * ppu)
        self.draw_coin(d, x0 + s * ppu, y0 - r * ppu, phi, s / r)
        return {"turns": phi / TWO_PI}

    def draw_text(self, d: ImageDraw.ImageDraw, states: dict, hud_alpha: float, counter_alpha: float) -> None:
        fx, fy = self.fc
        d.text((40, LABEL_A_Y), label_text("around"), font=self.font, fill=TEXT, anchor="lm")
        d.text((40, LABEL_B_Y), label_text("along"), font=self.font, fill=TEXT, anchor="lm")
        if hud_alpha > 0.02:
            d.text((W / 2, LEGEND_Y), legend_text(), font=self.font, fill=blend(TEXT, hud_alpha), anchor="mm")
            d.text((W / 2, TAG_Y), tag_text(), font=self.font_small, fill=blend(MUTED, hud_alpha), anchor="mm")
        if counter_alpha > 0.02:
            d.text((fx, fy - 26), "turns", font=self.font_small, fill=blend(MUTED, counter_alpha, FACE), anchor="mm")
            d.text((fx, fy + 16), counter_text("around", states["around"]["turns"]), font=self.font,
                   fill=blend(TEXT, counter_alpha, FACE), anchor="mm")
            d.text((W / 2, COUNTER_B_Y), counter_text("along", states["along"]["turns"]), font=self.font,
                   fill=blend(TEXT, counter_alpha), anchor="mm")

    def live_frame(self, f: int, title_alpha: float | None = None, hud_alpha: float = 0.0) -> np.ndarray:
        """Frame f with the geometry at f / fps; title_alpha and hud_alpha override the title and
        the legend/counter/card blend during the loop fade."""
        man = self.man
        t = f / self.fps
        if title_alpha is None:
            if t < man["title_until"]:
                title_alpha = 1.0 if t < man["title_until"] - 0.4 else (man["title_until"] - t) / 0.4
                hud_alpha = 0.0
            else:
                title_alpha = 0.0
                hud_alpha = min(1.0, (t - man["title_until"]) / 0.4)
        u, _holding = self.phase(f)
        img = Image.new("RGB", (W, H), BG)
        layer = Image.new("RGB", (W * SS, (GEOM_Y1 - GEOM_Y0) * SS), BG)
        ld = ImageDraw.Draw(layer)
        states = {"around": self.draw_around(ld, u), "along": self.draw_along(ld, u)}
        img.paste(layer.reduce(SS), (0, GEOM_Y0))
        d = ImageDraw.Draw(img)
        # The counters appear with the first roll (counters_from), so the opening hold does not
        # show the answer before the question is asked; they fade with the HUD at the loop.
        counter_alpha = hud_alpha * min(1.0, max(0.0, (t - man["counters_from"]) / 0.4))
        self.draw_text(d, states, hud_alpha, counter_alpha)
        if title_alpha > 0.0:
            for j, line in enumerate(man["title"].split("|")):
                d.text((W / 2, 172 + j * 62), line, font=self.font_title, fill=blend(TEXT, title_alpha), anchor="mm")
        if t >= man["payoff_t"]:
            a = min(1.0, (t - man["payoff_t"]) / man["payoff_hold"]) * hud_alpha
            for j, line in enumerate(payoff_lines(man, self.ev)):
                d.text((W / 2, PAYOFF_Y + j * 56), line, font=self.font, fill=blend(GOLD, a), anchor="mm")
        return np.asarray(img, dtype=np.uint8)

    def frame_at(self, f: int) -> np.ndarray:
        man = self.man
        total = int(round(man["scene_duration"] * self.fps))
        fade_frames = int(round(man["loop_fade"] * self.fps))
        if f == total - 1:
            return self.live_frame(0)   # the scene is periodic: the last frame repeats the first
        if f >= total - fade_frames:
            # The geometry runs on; the legend, counters and card fade out over the first half of
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
        wrap = self.live_frame(total, title_alpha=1.0, hud_alpha=0.0)   # the geometry one scene on, drawn live
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
    man = json.loads((ROOT / "projects/coinroll/manifest.json").read_text())
    ev = measure(man)
    if "--measure-only" in sys.argv:
        return
    if "--frames" in sys.argv:
        times = [float(v) for v in sys.argv[sys.argv.index("--frames") + 1].split(",")]
        r = Renderer(man, ev)
        (ROOT / "media/coinroll").mkdir(parents=True, exist_ok=True)
        for tv in times:
            Image.fromarray(r.frame_at(int(round(tv * man["fps"])))).save(ROOT / f"media/coinroll/smoke-{tv}.png")
        print("smoke frames: " + ", ".join(f"{tv}" for tv in times))
        return
    Renderer(man, ev).render(ROOT / "media/coinroll/footage.mp4")


if __name__ == "__main__":
    main()
