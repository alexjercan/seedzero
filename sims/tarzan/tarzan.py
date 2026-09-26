#!/usr/bin/env python3
"""Tarzan release: when do you let go to fly farthest?

A rider (a point mass) hangs on a massless rope of length L from a fixed
pivot. The water surface is h below the low point of the swing. The
rider starts from rest with the rope start_deg from the vertical on the
left and swings down (theta'' = -(g / L) sin theta, integrated by RK4 at
steps_per_second and checked against the energy closed form v^2 = 2 g L
(cos theta - cos start_deg)). At the release angle theta past the bottom
the rider leaves along the tangent, at theta above the horizontal, with
that v, from the point (L sin theta, h + L (1 - cos theta)) measured from
the spot on the water directly below the low point, and then flies as a
parabola with no air until the water (velocity Verlet against the closed
form). The landing distance is the horizontal position at the water,
measured from that spot. Two panels stacked, the same swing in both: the
upper rider lets go at the bottom, the lower rider lower_release_deg past
it. After the splash the rider resets to the start and the swing repeats;
the cycle divides the scene length, so the scene is exactly periodic and
the last frame equals the first. Half speed. Deterministic, no seed.

Measured and printed: the RK4 swing (the time and speed at the bottom
and at the release angle against the closed form, the full period
against the elliptic integral, the energy drift), both releases (speed,
direction, height, flight time, landing distance, apex; Verlet against
the closed form), the whole-degree scan of the release angle and the
fine scan's peak, the far-top drop, the values for the description, the
schedule in video time, the loop and periodicity checks and the
on-screen text widths.

usage: tarzan.py [--measure-only] [--frames t1,t2,...]
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
LEDGE = (30, 36, 46)

# Layout: overlay at y 96..130 (captions.py), three title rows at y 196,
# 254 and 312 (56 px) for the first seconds, then the legend at y 246 and
# the tag at y 298; two panels stacked, each with its label row at the top
# (y top + 16), its pivot 44 px below its top edge and the water line 9 m
# (432 px at 48 px per metre) below the pivot, a 40 px water band under the
# line: the upper panel from y 350 (pivot (372, 394), water at 826, band to
# 866) and the lower panel from y 900 (pivot (372, 944), water at 1376,
# band to 1416); the fixed readouts at the bottom left of each panel above
# the water; the geometry band y 350..1420 drawn at 2x; captions at
# caption_y 0.75 (y 1440..1520); the payoff card from y 1592.
TITLE_Y, TITLE_PITCH = 196, 58
LEGEND_Y, TAG_Y = 246, 298
GEOM_Y0, GEOM_Y1 = 350, 1420
SS = 2
PAYOFF_Y = 1592.0
PIVOT_BELOW_TOP = 44
WATER_BAND = 40
LABEL_X, READ_X = 60, 1020
PANELS = ("upper", "lower")


def blend(col, a: float, base=BG) -> tuple:
    a = max(0.0, min(1.0, a))
    return tuple(int(round(c * a + b * (1 - a))) for c, b in zip(col, base))


# --- measurement --------------------------------------------------------------
def rk4_swing(g: float, L: float, th0: float, dt: float, t_end: float) -> tuple[np.ndarray, np.ndarray]:
    """theta and theta' from rest at th0 (rad) by classical RK4 on theta'' = -(g / L) sin theta."""
    n = int(round(t_end / dt))
    th, w = np.empty(n + 1), np.empty(n + 1)
    k = g / L
    x, v = th0, 0.0
    th[0], w[0] = x, v
    for i in range(n):
        a1 = -k * math.sin(x)
        x2, v2 = x + 0.5 * dt * v, v + 0.5 * dt * a1
        a2 = -k * math.sin(x2)
        x3, v3 = x + 0.5 * dt * v2, v + 0.5 * dt * a2
        a3 = -k * math.sin(x3)
        x4, v4 = x + dt * v3, v + dt * a3
        a4 = -k * math.sin(x4)
        x += dt * (v + 2.0 * v2 + 2.0 * v3 + v4) / 6.0
        v += dt * (a1 + 2.0 * a2 + 2.0 * a3 + a4) / 6.0
        th[i + 1], w[i + 1] = x, v
    return th, w


def crossing(th: np.ndarray, w: np.ndarray, dt: float, target: float) -> tuple[float, float]:
    """(time, theta') at the first upward crossing of theta = target, interpolated inside the step."""
    i = int(np.nonzero(th >= target)[0][0])
    if i == 0:
        return 0.0, float(w[0])
    frac = (target - th[i - 1]) / (th[i] - th[i - 1])
    return (i - 1 + frac) * dt, float(w[i - 1] + frac * (w[i] - w[i - 1]))


def zero_crossings(w: np.ndarray, dt: float) -> list[float]:
    """Times where theta' changes sign (the turning points of the swing)."""
    s = np.sign(w)
    idx = np.nonzero((s[:-1] != s[1:]) & (s[:-1] != 0))[0]
    out = []
    for i in idx:
        frac = w[i] / (w[i] - w[i + 1])
        out.append((i + frac) * dt)
    return out


def ellip_k(k: float) -> float:
    """Complete elliptic integral of the first kind by the arithmetic-geometric mean."""
    a, b = 1.0, math.sqrt(1.0 - k * k)
    while abs(a - b) > 1e-15:
        a, b = 0.5 * (a + b), math.sqrt(a * b)
    return math.pi / (2.0 * a)


def landing(g: float, L: float, h: float, th_start: float, th: float) -> dict:
    """Closed-form release at th (rad past the bottom) and the parabola to the water."""
    v = math.sqrt(max(0.0, 2.0 * g * L * (math.cos(th) - math.cos(th_start))))
    x0, y0 = L * math.sin(th), h + L * (1.0 - math.cos(th))
    vx, vy = v * math.cos(th), v * math.sin(th)
    t = (vy + math.sqrt(vy * vy + 2.0 * g * y0)) / g
    apex = (x0 + vx * vy / g, y0 + vy * vy / (2.0 * g)) if vy > 0.0 else (x0, y0)
    return {"deg": math.degrees(th), "v": v, "x0": x0, "y0": y0, "vx": vx, "vy": vy, "t": t, "x": x0 + vx * t,
            "apex": apex}


def fly(x0: float, y0: float, vx: float, vy: float, g: float, dt: float) -> tuple[float, float]:
    """Velocity Verlet from the release until the water (y = 0), the crossing interpolated inside the step."""
    x, y, t = x0, y0, 0.0
    while True:
        xn = x + vx * dt
        yn = y + vy * dt - 0.5 * g * dt * dt
        if yn <= 0.0:
            f = y / (y - yn)
            return t + f * dt, x + f * (xn - x)
        x, y, vy, t = xn, yn, vy - g * dt, t + dt


def measure(man: dict) -> dict:
    g, L, h = man["g_m_s2"], man["rope_m"], man["drop_m"]
    D, fps, speed = man["scene_duration"], man["fps"], man["speed"]
    dt = 1.0 / man["steps_per_second"]
    start = math.radians(man["start_deg"])
    rel = {"upper": man["upper_release_deg"], "lower": man["lower_release_deg"]}
    cycle = man["cycle_s"]
    cycles = D / cycle
    assert abs(cycles - round(cycles)) < 1e-9, "the cycle must divide the scene length"
    print(f"setup: a rider as a point mass on a massless rope of {L:g} m from a fixed pivot; the water surface "
          f"{h:g} m below the low point of the swing (the pivot {L + h:g} m above the water); the rider starts from "
          f"rest with the rope {man['start_deg']:g} degrees from the vertical on the left and swings down; "
          f"theta'' = -(g / L) sin theta by RK4 at {man['steps_per_second']} steps per second (dt = {dt:.0e} s) "
          f"against the energy closed form v^2 = 2 g L (cos theta - cos {man['start_deg']:g}); at the release angle "
          f"theta past the bottom the rider leaves along the tangent, at theta above the horizontal, from "
          f"(L sin theta, {h:g} + L (1 - cos theta)) measured from the spot on the water under the low point, then "
          f"a parabola with no air (velocity Verlet at the same dt against the closed form) until the water; the "
          f"landing distance is the horizontal position at the water from that spot; g = {g:g} m/s^2; the upper "
          f"rider lets go {rel['upper']:g} degrees past the bottom (at the bottom), the lower rider "
          f"{rel['lower']:g} degrees past it; drawn at {man['px_per_m']:g} px per metre at {speed:g} x real time "
          f"(the {cycle * speed:g} s cycle of swing, flight, splash and reset takes {cycle:g} s of video, "
          f"{cycles:.0f} cycles in {D:g} s); deterministic, no seed")
    # The RK4 swing from rest at -start.
    th, w = rk4_swing(g, L, -start, dt, 1.4 * 4.0 * math.sqrt(L / g) * ellip_k(math.sin(start / 2.0)))
    energy = 0.5 * (L * w) ** 2 - g * L * np.cos(th)
    e_drift = float(np.max(np.abs(energy - energy[0])))
    turns = zero_crossings(w, dt)
    T_rk4 = turns[1]
    T_closed = 4.0 * math.sqrt(L / g) * ellip_k(math.sin(start / 2.0))
    t_cross, w_cross, v_cross, v_closed = {}, {}, {}, {}
    for name in PANELS:
        t_cross[name], w_cross[name] = crossing(th, w, dt, math.radians(rel[name]))
        v_cross[name] = L * w_cross[name]
        v_closed[name] = math.sqrt(2.0 * g * L * (math.cos(math.radians(rel[name])) - math.cos(start)))
    t_far, w_far = crossing(th, w, dt, start - 1e-9)
    print(f"swing (RK4 from rest at {man['start_deg']:g} degrees): the rider reaches the bottom after "
          f"{t_cross['upper']:.4f} s at {v_cross['upper']:.4f} m/s (closed form {v_closed['upper']:.4f} m/s, diff "
          f"{abs(v_cross['upper'] - v_closed['upper']):.1e} m/s) and {rel['lower']:g} degrees past the bottom after "
          f"{t_cross['lower']:.4f} s at {v_cross['lower']:.4f} m/s (closed form {v_closed['lower']:.4f} m/s, diff "
          f"{abs(v_cross['lower'] - v_closed['lower']):.1e} m/s), {t_cross['lower'] - t_cross['upper']:.4f} s after "
          f"the bottom; the rope reaches the far top ({man['start_deg']:g} degrees) after {turns[0]:.4f} s at "
          f"{abs(L * w_far):.4f} m/s; the full period is {T_rk4:.4f} s (4 sqrt(L / g) K(sin {man['start_deg'] / 2:g} "
          f"degrees) = {T_closed:.4f} s, diff {abs(T_rk4 - T_closed):.1e} s; a small-angle pendulum would take "
          f"{2 * math.pi * math.sqrt(L / g):.4f} s); the energy per unit mass drifts by at most {e_drift:.1e} J/kg "
          f"over {len(th) * dt:.1f} s")
    # The two releases, closed form and Verlet.
    land = {name: landing(g, L, h, start, math.radians(rel[name])) for name in PANELS}
    for name in PANELS:
        ld = land[name]
        t_v, x_v = fly(ld["x0"], ld["y0"], ld["vx"], ld["vy"], g, dt)
        ld["t_verlet"], ld["x_verlet"] = t_v, x_v
        where = "at the bottom" if rel[name] == 0 else f"{rel[name]:g} degrees past the bottom"
        print(f"{name} panel (lets go {where}): speed {ld['v']:.4f} m/s ({ld['v']:.2f}) at {ld['deg']:g} degrees "
              f"above the horizontal (vx {ld['vx']:.4f}, vy {ld['vy']:.4f} m/s) from ({ld['x0']:.4f}, {ld['y0']:.4f}) m, "
              f"i.e. {ld['y0']:.3f} m above the water and {ld['x0']:.3f} m past the spot under the low point"
              + (f"; rises to an apex {ld['apex'][1]:.3f} m above the water at {ld['apex'][0]:.3f} m" if ld["vy"] > 0
                 else "; no rise, the flight starts level")
              + f"; hits the water after {ld['t']:.4f} s of flight ({ld['t']:.3f} s) at {ld['x']:.4f} m "
              f"({ld['x']:.2f} m) from the spot under the low point (Verlet {x_v:.4f} m after {t_v:.4f} s, diffs "
              f"{abs(x_v - ld['x']):.1e} m and {abs(t_v - ld['t']):.1e} s)")
    lu, ll = land["upper"], land["lower"]
    print(f"the two against each other: the lower rider lets go {lu['v'] - ll['v']:.3f} m/s slower ({ll['v'] / lu['v'] * 100:.1f} "
          f"% of the bottom speed) but {ll['y0'] - lu['y0']:.3f} m higher and pointed {ll['deg']:g} degrees up, stays "
          f"in the air {ll['t'] - lu['t']:.3f} s longer ({ll['t'] / lu['t']:.2f} x) and lands {ll['x'] - lu['x']:.3f} m "
          f"farther ({ll['x'] - lu['x']:.2f} m; {ll['x']:.2f} against {lu['x']:.2f} m, {(ll['x'] / lu['x'] - 1) * 100:.1f} "
          f"% farther); the bottom release is the fastest the rider ever goes and the flight is the shortest of the two")
    # The scan of the release angle.
    step = man["scan_deg_step"]
    scan = [landing(g, L, h, start, math.radians(d)) for d in np.arange(0.0, man["start_deg"] + 1e-9, step)]
    best_whole = max(scan, key=lambda s: s["x"])
    fine = [landing(g, L, h, start, math.radians(d))
            for d in np.arange(0.0, man["start_deg"] + 1e-9, man["fine_scan_deg_step"])]
    best = max(fine, key=lambda s: s["x"])
    top = landing(g, L, h, start, start)
    print(f"scan of the release angle ({step:g} degree steps from 0 to {man['start_deg']:g}, landing distance): "
          + ", ".join(f"{s['deg']:g}: {s['x']:.2f} m" for s in scan)
          + f"; the whole-degree best is {best_whole['deg']:g} degrees at {best_whole['x']:.4f} m and "
          f"{man['lower_release_deg']:g} degrees gives {ll['x']:.4f} m ({'the same' if abs(best_whole['x'] - ll['x']) < 0.005 else 'different'} "
          f"to two decimals); the fine scan ({man['fine_scan_deg_step']:g} degree steps) peaks at {best['deg']:.2f} "
          f"degrees ({best['deg']:.1f}) with {best['x']:.4f} m ({best['x']:.2f} m); hanging on to the far top "
          f"({man['start_deg']:g} degrees, speed {top['v']:.3f}) drops the rider straight down from {top['y0']:.3f} m "
          f"above the water, {top['x0']:.3f} m out, {top['t']:.3f} s to the water, landing {top['x']:.2f} m out")
    print("for the description (release angle past the bottom: speed, height above the water, flight time, landing): "
          + "; ".join(f"{s['deg']:g} deg: {s['v']:.2f} m/s, {s['y0']:.2f} m, {s['t']:.3f} s, {s['x']:.2f} m"
                      for s in (landing(g, L, h, start, math.radians(d)) for d in man["description_degs"])))
    # The schedule in video time.
    c0 = man["cycle_start_at"]
    ev_t = {name: {"release": t_cross[name] / speed, "splash": (t_cross[name] + land[name]["t"]) / speed}
            for name in PANELS}
    far_top = turns[0] / speed
    assert ev_t["lower"]["splash"] + 2.0 * man["reset_fade_s"] < cycle, "the lower flight must end well inside the cycle"
    starts = [c0 + k * cycle for k in range(math.floor((0.0 - c0) / cycle + 1e-9), math.floor((D - c0 - 1e-9) / cycle) + 1)]
    inside = lambda ts: ", ".join(f"{v:.2f}" for v in ts if -1e-9 <= v <= D + 1e-9)
    tau0 = (0.0 - c0) % cycle
    first = []
    for name in PANELS:
        e = ev_t[name]
        if tau0 < e["release"]:
            first.append(f"the {name} rider is on the rope {tau0:.2f} s into the swing")
        elif tau0 < e["splash"]:
            first.append(f"the {name} rider is {tau0 - e['release']:.2f} s of video into its flight")
        else:
            first.append(f"the {name} rider has splashed {tau0 - e['splash']:.2f} s ago and the distance is marked")
    print(f"schedule (video time, {speed:g} x real time, cycle {cycle:g} s): the cycles start at "
          + ", ".join(f"{s:.2f}" for s in starts)
          + f" s (rider at rest on the ledge at {man['start_deg']:g} degrees); in each cycle the upper rider lets go "
          f"{ev_t['upper']['release']:.3f} s after the start and splashes at {ev_t['upper']['splash']:.3f} s, the lower "
          f"rider lets go at {ev_t['lower']['release']:.3f} s and splashes at {ev_t['lower']['splash']:.3f} s, the empty "
          f"rope reaches the far top at {far_top:.3f} s, the splash and the distance hold until the reset fade over the "
          f"last {man['reset_fade_s']:g} s of the cycle; upper releases at "
          + inside(s + ev_t["upper"]["release"] for s in starts) + " s, upper splashes at "
          + inside(s + ev_t["upper"]["splash"] for s in starts) + " s, lower releases at "
          + inside(s + ev_t["lower"]["release"] for s in starts) + " s, lower splashes at "
          + inside(s + ev_t["lower"]["splash"] for s in starts) + " s, resets (the fade starts) at "
          + inside(s + cycle - man["reset_fade_s"] for s in starts) + f" s; on the first frame "
          + " and ".join(first) + f"; title until {man['title_until']:g} s, then the legend and the fixed "
          f"readouts; payoff card from {man['payoff_t']:g} s; the title fades back in over the last {man['loop_fade']:g} "
          f"s and the last frame repeats the first (the scene is periodic: {D:g} s holds exactly {cycles:.0f} cycles)")
    ev = {"th": th, "w": w, "dt": dt, "t_cross": t_cross, "t_far": turns[0], "land": land, "best_deg": best["deg"],
          "best_x": best["x"], "x_upper": lu["x"], "x_lower": ll["x"], "ev_t": ev_t, "top": top}
    # Text widths.
    font = os.environ["SEED_ZERO_FONT"]
    f28, f34, f40, f56 = (ImageFont.truetype(font, n) for n in (28, 34, 40, 56))
    widths = {"overlay@34": (f34, man["overlay"])}
    for j, line in enumerate(man["title"].split("|")):
        widths[f"title line {j + 1}@56"] = (f56, line)
    widths["legend@40"] = (f40, legend_text())
    widths["tag@28"] = (f28, tag_text())
    for name in PANELS:
        widths[f"label {name}@40"] = (f40, label_text(man, name))
        for j, line in enumerate(fixed_lines(man, ev, name)):
            widths[f"fixed {name} line {j + 1}@28"] = (f28, line)
        widths[f"distance {name}@28"] = (f28, distance_text(land[name]["x"]))
        widths[f"readout {name}@40"] = (f40, readout_distance(land[name]["x"]))
    widths["readout angle@40"] = (f40, readout_angle(-man["start_deg"]))
    for j, line in enumerate(payoff_lines(man, ev)):
        widths[f"payoff line {j + 1}@40"] = (f40, line)
    print("text widths: " + ", ".join(f"{k} {f.getlength(s):.0f} px" for k, (f, s) in widths.items()))
    assert all(f.getlength(s) < 950 for f, s in widths.values()), "a text line is wider than 950 px"
    return ev


def legend_text() -> str:
    return "same swing, two moments to let go"


def tag_text() -> str:
    return "side view, half speed, no air"


def label_text(man: dict, name: str) -> str:
    deg = man[name + "_release_deg"]
    return "lets go at the bottom" if deg == 0 else f"lets go {deg:g} deg past the bottom"


def readout_angle(deg: float) -> str:
    return f"{int(round(deg))} deg"


def readout_distance(x: float) -> str:
    return f"{x:.2f} m"


def distance_text(x: float) -> str:
    return f"{x:.2f} m"


def fixed_lines(man: dict, ev: dict, name: str) -> list[str]:
    ld = ev["land"][name]
    first = f"{ld['v']:.2f} m/s, level" if ld["deg"] == 0 else f"{ld['v']:.2f} m/s, up at {ld['deg']:g} deg"
    return [first, f"{ld['y0']:.2f} m above the water", f"{ld['t']:.2f} s in the air"]


def payoff_lines(man: dict, ev: dict) -> list[str]:
    text = man["payoff_text"].format(x_upper=ev["x_upper"], x_lower=ev["x_lower"], best_deg=ev["best_deg"],
                                     best_x=ev["best_x"])
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
        self.ppm = float(man["px_per_m"])
        self.g, self.L, self.h = man["g_m_s2"], man["rope_m"], man["drop_m"]
        self.speed, self.cycle, self.c0 = man["speed"], man["cycle_s"], man["cycle_start_at"]
        self.start = math.radians(man["start_deg"])
        self.panels = {name: {"pivot": tuple(man[name + "_pivot"]), "deg": man[name + "_release_deg"],
                              "t_rel": ev["t_cross"][name], "land": ev["land"][name]} for name in PANELS}

    # --- state helpers ------------------------------------------------------
    def tau(self, t: float) -> float:
        """Real (simulation) seconds into the current cycle."""
        return ((t - self.c0) % self.cycle) * self.speed

    def rope_theta(self, tau: float) -> float:
        """Rope angle from the vertical (rad, positive past the bottom) on the RK4 swing."""
        th, dt = self.ev["th"], self.ev["dt"]
        u = tau / dt
        i = min(int(u), len(th) - 2)
        f = u - i
        return float(th[i] + f * (th[i + 1] - th[i]))

    def flight_pos(self, ld: dict, u: float) -> tuple[float, float]:
        return ld["x0"] + ld["vx"] * u, ld["y0"] + ld["vy"] * u - 0.5 * self.g * u * u

    # --- pixel helpers ------------------------------------------------------
    def water_y(self, name: str) -> float:
        return self.panels[name]["pivot"][1] + (self.L + self.h) * self.ppm

    def px(self, name: str, x: float, y: float) -> tuple[float, float]:
        """x from the spot under the low point, y above the water, in metres."""
        cx = self.panels[name]["pivot"][0]
        return cx + x * self.ppm, self.water_y(name) - y * self.ppm

    def L_(self, name: str, x: float, y: float) -> tuple[float, float]:
        # Rounded to 1e-4 px so that a coordinate that is an exact integer at one time and off
        # by 1e-11 a whole number of cycles later draws the same pixel (the periodicity check).
        X, Y = self.px(name, x, y)
        return round(X * SS, 4), round((Y - GEOM_Y0) * SS, 4)

    def rope_xy(self, theta: float, r: float) -> tuple[float, float]:
        """World position (metres, water coordinates) of the point at r along the rope at theta."""
        return r * math.sin(theta), (self.L + self.h) - r * math.cos(theta)

    def circle(self, d: ImageDraw.ImageDraw, X: float, Y: float, rr: float, **kw) -> None:
        d.ellipse((X - rr, Y - rr, X + rr, Y + rr), **kw)

    def arc(self, d: ImageDraw.ImageDraw, name: str, r: float, th0: float, th1: float, fill, width: int) -> None:
        """Arc at radius r about the pivot from rope angle th0 to th1 (rad, positive past the bottom)."""
        cx, cy = self.L_(name, 0.0, self.L + self.h)
        rr = r * self.ppm * SS
        d.arc((cx - rr, cy - rr, cx + rr, cy + rr), 90.0 - math.degrees(th1), 90.0 - math.degrees(th0),
              fill=fill, width=width)

    # --- the scene ----------------------------------------------------------
    def draw_panel(self, d: ImageDraw.ImageDraw, name: str, t: float, hud_alpha: float) -> dict:
        man, P = self.man, self.panels[name]
        L, h, g = self.L, self.h, self.g
        ld = P["land"]
        tau = self.tau(t)
        cycle_real = self.cycle * self.speed
        fade_start = cycle_real - man["reset_fade_s"] * self.speed
        reset = 1.0 if tau < fade_start else max(0.0, (cycle_real - tau) / (cycle_real - fade_start))
        rr = man["rider_radius_m"] * self.ppm * SS
        # The water: a band below the line, the line, the spot under the low point.
        wx0, wy = self.L_(name, (man["ledge_x_px"] - P["pivot"][0]) / self.ppm, 0.0)
        wx1, _ = self.L_(name, (man["water_right_px"] - P["pivot"][0]) / self.ppm, 0.0)
        d.rectangle((wx0, wy, wx1, wy + WATER_BAND * SS), fill=blend(TEAL, 0.10))
        d.line((wx0, wy, wx1, wy), fill=blend(TEAL, 0.6), width=2 * SS)
        sx, sy = self.L_(name, 0.0, 0.0)
        d.line((sx, sy - 8 * SS, sx, sy + 8 * SS), fill=MUTED, width=2 * SS)
        # The swing: a dashed arc of the rider's path from -start to +start, the ledge at the start.
        nd = man["arc_dashes"]
        for j in range(nd):
            a0 = -self.start + 2.0 * self.start * j / nd
            self.arc(d, name, L, a0, a0 + self.start / nd, blend(RIM, 0.6), 2 * SS)
        lx, ly = self.L_(name, *self.rope_xy(-self.start, L))
        ex0, _ = self.L_(name, (man["ledge_x_px"] - P["pivot"][0]) / self.ppm, 0.0)
        d.rectangle((ex0, ly + rr, lx + rr, ly + rr + 4 * SS), fill=RIM)
        # The release mark: a gold tick at the bottom for the upper rider, an arc from the bottom to the release
        # angle with ticks for the lower rider (part of the HUD).
        if hud_alpha > 0.02:
            col = blend(GOLD, 0.8 * hud_alpha)
            rel = math.radians(P["deg"])
            if rel > 0.0:
                self.arc(d, name, L + 0.45, 0.0, rel, col, 3 * SS)
            for a in sorted({0.0, rel}):
                p0 = self.L_(name, *self.rope_xy(a, L + 0.35))
                p1 = self.L_(name, *self.rope_xy(a, L + 0.55))
                d.line((*p0, *p1), fill=col, width=3 * SS)
        # The rider: on the rope, in flight, or splashed.
        piv = self.L_(name, 0.0, L + h)
        if tau < P["t_rel"]:
            theta = self.rope_theta(tau)
            X, Y = self.L_(name, *self.rope_xy(theta, L))
            d.line((*piv, X, Y), fill=MUTED, width=4 * SS)
            self.circle(d, X, Y, rr, fill=TEAL)
            state = {"phase": "rope", "theta": theta, "x": 0.0}
        else:
            u = tau - P["t_rel"]
            # The empty rope swings on and fades until the far top.
            if tau < self.ev["t_far"]:
                a = 0.5 * (1.0 - u / (self.ev["t_far"] - P["t_rel"]))
                theta = self.rope_theta(tau)
                X, Y = self.L_(name, *self.rope_xy(theta, L))
                d.line((*piv, X, Y), fill=blend(MUTED, a * reset), width=4 * SS)
            # The release point.
            RX, RY = self.L_(name, ld["x0"], ld["y0"])
            self.circle(d, RX, RY, 0.5 * rr, outline=blend(WHITE, 0.7 * reset), width=2 * SS)
            # The path so far.
            uf = min(u, ld["t"])
            n = max(2, int(uf / 0.02) + 1)
            pts = [self.L_(name, *self.flight_pos(ld, uf * k / (n - 1))) for k in range(n)]
            if len(pts) > 1:
                d.line(pts, fill=blend(TEAL, 0.45 * reset), width=2 * SS)
            if u < ld["t"]:
                X, Y = self.L_(name, *self.flight_pos(ld, u))
                self.circle(d, X, Y, rr, fill=blend(TEAL, reset))
                state = {"phase": "flight", "theta": 0.0, "x": ld["x0"] + ld["vx"] * u}
            else:
                # The splash: a ring on the water and a crown of drops, fading to a rest level; the distance
                # measured under the water.
                s = u - ld["t"]
                a = reset * max(0.35, 1.0 - s / 0.6)
                X, Y = self.L_(name, ld["x"], 0.0)
                d.ellipse((X - 0.45 * self.ppm * SS, Y - 0.10 * self.ppm * SS, X + 0.45 * self.ppm * SS,
                           Y + 0.10 * self.ppm * SS), outline=blend(TEAL, a), width=2 * SS)
                for k, (dx, dy) in enumerate(((-0.30, 0.45), (-0.12, 0.62), (0.08, 0.65), (0.26, 0.50))):
                    p0 = self.L_(name, ld["x"] + 0.4 * dx, 0.05)
                    p1 = self.L_(name, ld["x"] + dx, dy)
                    d.line((*p0, *p1), fill=blend(TEAL, a), width=2 * SS)
                mx0, my = self.L_(name, 0.0, -8.0 / self.ppm)
                mx1, _ = self.L_(name, ld["x"], -8.0 / self.ppm)
                d.line((mx0, my, mx1, my), fill=blend(GOLD, reset), width=2 * SS)
                for mx in (mx0, mx1):
                    d.line((mx, my - 5 * SS, mx, my + 5 * SS), fill=blend(GOLD, reset), width=2 * SS)
                state = {"phase": "splash", "theta": 0.0, "x": ld["x"]}
        self.circle(d, *piv, 6 * SS, fill=WHITE)
        state["reset"] = reset
        return state

    def draw_text(self, d: ImageDraw.ImageDraw, states: dict, t: float, hud_alpha: float) -> None:
        man, ev = self.man, self.ev
        for name, st in states.items():
            px_, py = self.panels[name]["pivot"]
            top = py - PIVOT_BELOW_TOP
            water = self.water_y(name)
            ld = self.panels[name]["land"]
            d.text((LABEL_X, top + 16), label_text(man, name), font=self.font, fill=TEXT, anchor="lm")
            if st["phase"] == "rope":
                d.text((READ_X, top + 16), readout_angle(math.degrees(st["theta"])), font=self.font, fill=TEXT,
                       anchor="rm")
            elif st["phase"] == "flight":
                d.text((READ_X, top + 16), readout_distance(st["x"]), font=self.font, fill=TEXT, anchor="rm")
            else:
                d.text((READ_X, top + 16), readout_distance(st["x"]), font=self.font,
                       fill=blend(GOLD, st["reset"], TEXT), anchor="rm")
                mx = px_ + 0.5 * ld["x"] * self.ppm
                d.text((mx, water + 24), distance_text(ld["x"]), font=self.font_small,
                       fill=blend(GOLD, st["reset"]), anchor="mm")
            if hud_alpha > 0.02:
                for j, line in enumerate(fixed_lines(man, ev, name)):
                    col = GOLD if j == 0 else MUTED
                    d.text((LABEL_X, water - 96 + 32 * j), line, font=self.font_small, fill=blend(col, hud_alpha),
                           anchor="lm")
        if hud_alpha > 0.02:
            d.text((W / 2, LEGEND_Y), legend_text(), font=self.font, fill=blend(TEXT, hud_alpha), anchor="mm")
            d.text((W / 2, TAG_Y), tag_text(), font=self.font_small, fill=blend(MUTED, hud_alpha), anchor="mm")

    def live_frame(self, f: int, title_alpha: float | None = None, hud_alpha: float = 0.0) -> np.ndarray:
        """Frame f with the geometry at f / fps; title_alpha and hud_alpha override the title and
        the legend/readout/card blend during the loop fade."""
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
        states = {name: self.draw_panel(ld, name, t, hud_alpha) for name in PANELS}
        img.paste(layer.reduce(SS), (0, GEOM_Y0))
        d = ImageDraw.Draw(img)
        self.draw_text(d, states, t, hud_alpha)
        if title_alpha > 0.0:
            for j, line in enumerate(man["title"].split("|")):
                d.text((W / 2, TITLE_Y + j * TITLE_PITCH), line, font=self.font_title, fill=blend(TEXT, title_alpha),
                       anchor="mm")
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
            # The geometry runs on; the legend, readouts and card fade out over the first half of
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
        wrap = self.live_frame(total, title_alpha=1.0, hud_alpha=0.0)   # the geometry one period on, drawn live
        diff = np.abs(first.astype(int) - wrap.astype(int))
        print(f"periodicity check: the scene drawn live at {self.man['scene_duration']:g} s differs from 0 s in "
              f"{int((diff.max(axis=2) > 24).sum())} px (max channel difference {int(diff.max())})")
        prev = self.frame_at(total - 2)
        diff = np.abs(prev.astype(int) - last.astype(int))
        vb = self.ev["land"]["upper"]["v"]
        print(f"loop step: the frame before the last differs from the last in {int((diff.max(axis=2) > 24).sum())} px "
              f"(the rider moves {vb * self.ppm * self.speed / self.fps:.2f} px per frame at the bottom)")
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
    man = json.loads((ROOT / "projects/tarzan/manifest.json").read_text())
    ev = measure(man)
    if "--measure-only" in sys.argv:
        return
    if "--frames" in sys.argv:
        times = [float(v) for v in sys.argv[sys.argv.index("--frames") + 1].split(",")]
        r = Renderer(man, ev)
        (ROOT / "media/tarzan").mkdir(parents=True, exist_ok=True)
        for tv in times:
            Image.fromarray(r.frame_at(int(round(tv * man["fps"])))).save(ROOT / f"media/tarzan/smoke-{tv}.png")
        print("smoke frames: " + ", ".join(f"{tv}" for tv in times))
        return
    Renderer(man, ev).render(ROOT / "media/tarzan/footage.mp4")


if __name__ == "__main__":
    main()
