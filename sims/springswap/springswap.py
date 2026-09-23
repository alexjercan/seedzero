#!/usr/bin/env python3
"""Spring pendulum swap: bounce it up and down. Does it start to swing?

A point bob of mass m hangs on a light spring of stiffness k and natural
length l0 from a fixed pivot. Under the bob's weight the spring stretches
to the equilibrium length l = l0 + m g / k (1 m here). The bob is pulled
down by the bounce amplitude A (10 cm) with a small tilt from vertical
(0.1 degree) and released at rest. Two panels share every input; only the
spring differs. The left spring is tuned to two bounces per swing,
k / m = 4 g / l (the 2:1 autoparametric resonance), the right spring to
1.5 bounces per swing, k / m = 2.25 g / l. Full two-degree-of-freedom
equations in polar coordinates (r from the pivot, theta from straight
down), no small-angle approximation, no damping:

    r''     = r theta'^2 + g cos theta - (k / m) (r - l0)
    theta'' = -(2 r' theta' + g sin theta) / r

integrated with RK4 at a fixed step (1200 steps per second, 0.83 ms; the
half-step check runs at 2400). Deterministic, no seed.

Measured and printed: for each panel the swing and bounce periods (from
the zero crossings of theta and r' over the first ten seconds, beside the
closed forms 2 pi sqrt(l / g) and 2 pi sqrt(m / k)), the time the swing
angle first passes 1 and 5 degrees, the peak swing angle and its time
within 40 s and within 60 s, the bounce amplitude (radial and vertical
excursion of the bob) over one bounce period at the swing peak, the
readouts at the end of the scene, the energy drift, the half-step check,
the lowest bob position in the frame, the schedule and the text widths.

usage: springswap.py [--measure-only] [--frames t1,t2,...]
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
WIRE = (70, 80, 94)
WHITE = (236, 240, 244)
BEAM = (120, 130, 145)
SPRING = (176, 184, 196)

# Layout: overlay at y 96..130 (captions.py), title rows at y 190/252 for
# the first seconds, a muted clock at y 250 after the title, panel labels
# at y 345, the top bar at y 400, springs of 700 px at equilibrium (1 m),
# bobs of radius 30 bouncing 70 px either way, a readout row per panel at
# y 1310 (swing) and 1362 (bounce), captions at caption_y 0.75 (y
# 1440..1520), payoff card from y 1592. The geometry is drawn at 2x on a
# layer from y 300 to 1280 and reduced.
GEOM_Y0, GEOM_Y1 = 300, 1280
SS = 2
PAYOFF_Y = 1592.0
CLOCK_Y = 250
LABEL_Y = 345
READ_Y = (1310, 1362)
COLOURS = {"tuned": GOLD, "detuned": TEAL}


def blend(col, a, base=BG):
    return tuple(int(round(c * a + b * (1 - a))) for c, b in zip(col, base))


# --- simulation --------------------------------------------------------------
def panel_params(man: dict, panel: dict) -> dict:
    g, l = man["g"], man["length_m"]
    n = panel["bounces_per_swing"]
    k_over_m = n * n * g / l
    l0 = l - g / k_over_m
    return {"name": panel["name"], "label": panel["label"], "n": n, "k_over_m": k_over_m, "l0": l0, "l": l, "g": g}


def rk4_run(p: dict, r0: float, th0: float, steps_per_s: int, t_end: float) -> dict:
    """Integrate the spring pendulum from rest at (r0, th0); per-step arrays of time and state."""
    g, km, l0 = p["g"], p["k_over_m"], p["l0"]
    dt = 1.0 / steps_per_s
    n = int(round(t_end * steps_per_s))

    def deriv(s):
        r, rd, th, thd = s
        return (rd, r * thd * thd + g * math.cos(th) - km * (r - l0), thd, -(2.0 * rd * thd + g * math.sin(th)) / r)

    s = (r0, 0.0, th0, 0.0)
    out = np.empty((n + 1, 4))
    out[0] = s
    for i in range(1, n + 1):
        k1 = deriv(s)
        k2 = deriv(tuple(s[j] + 0.5 * dt * k1[j] for j in range(4)))
        k3 = deriv(tuple(s[j] + 0.5 * dt * k2[j] for j in range(4)))
        k4 = deriv(tuple(s[j] + dt * k3[j] for j in range(4)))
        s = tuple(s[j] + dt / 6.0 * (k1[j] + 2 * k2[j] + 2 * k3[j] + k4[j]) for j in range(4))
        out[i] = s
    t = np.arange(n + 1) * dt
    return {"t": t, "r": out[:, 0], "rd": out[:, 1], "th": out[:, 2], "thd": out[:, 3], "dt": dt, "steps_per_s": steps_per_s}


def energy(p: dict, run: dict) -> np.ndarray:
    """Total energy per unit mass: kinetic, gravity (zero at the pivot), spring."""
    r, rd, th, thd = run["r"], run["rd"], run["th"], run["thd"]
    return 0.5 * (rd * rd + r * r * thd * thd) - p["g"] * r * np.cos(th) + 0.5 * p["k_over_m"] * (r - p["l0"]) ** 2


def zero_crossings(t: np.ndarray, y: np.ndarray, t_max: float) -> list[float]:
    """Interpolated times where y changes sign, up to t_max."""
    out = []
    m = int(np.searchsorted(t, t_max))
    s = np.sign(y[:m])
    for i in range(1, m):
        if s[i - 1] != 0 and s[i] != s[i - 1]:
            f = y[i - 1] / (y[i - 1] - y[i])
            out.append(float(t[i - 1] + f * (t[i] - t[i - 1])))
    return out


def period_from_crossings(t: np.ndarray, y: np.ndarray, t_max: float) -> tuple[float, int]:
    z = zero_crossings(t, y, t_max)
    return 2.0 * (z[-1] - z[0]) / (len(z) - 1), len(z) - 1


def first_pass(t: np.ndarray, y: np.ndarray, level: float) -> float | None:
    """Interpolated time |y| first exceeds level."""
    a = np.abs(y)
    idx = np.flatnonzero(a >= level)
    if len(idx) == 0:
        return None
    i = int(idx[0])
    if i == 0:
        return 0.0
    f = (level - a[i - 1]) / (a[i] - a[i - 1])
    return float(t[i - 1] + f * (t[i] - t[i - 1]))


def peak_within(t: np.ndarray, y: np.ndarray, t_max: float) -> tuple[float, float]:
    """Largest |y| up to t_max with parabolic interpolation; returns (time, value)."""
    m = int(np.searchsorted(t, t_max, side="right"))
    a = np.abs(y[:m])
    i = int(np.argmax(a))
    if 0 < i < m - 1:
        y0, y1, y2 = a[i - 1], a[i], a[i + 1]
        denom = y0 - 2 * y1 + y2
        off = 0.5 * (y0 - y2) / denom if denom != 0 else 0.0
        return float(t[i] + off * (t[1] - t[0])), float(y1 - 0.25 * (y0 - y2) * off)
    return float(t[i]), float(a[i])


def window_amp(t: np.ndarray, y: np.ndarray, lo: float, hi: float) -> float:
    """Half the range of y on [lo, hi]."""
    m = (t >= lo) & (t <= hi)
    return float((y[m].max() - y[m].min()) / 2.0)


def trailing_readouts(run: dict, t_swing: float, t_bounce: float, fps: int, n_frames: int) -> tuple[np.ndarray, np.ndarray]:
    """Per-frame readouts: the largest |theta| over the last swing period (degrees) and half the vertical
    range of the bob over the last bounce period (metres)."""
    t, th = run["t"], run["th"]
    y = run["r"] * np.cos(th)
    swing = np.zeros(n_frames)
    bounce = np.zeros(n_frames)
    for f in range(n_frames):
        tf = f / fps
        # Inside the first period the window looks ahead to [0, period] so the first frame reads the
        # release amplitude, not an empty window.
        i0, i1 = np.searchsorted(t, (max(0.0, tf - t_swing), max(tf, t_swing)), side="right")
        swing[f] = math.degrees(np.abs(th[max(0, i0 - 1):i1]).max())
        j0, j1 = np.searchsorted(t, (max(0.0, tf - t_bounce), max(tf, t_bounce)), side="right")
        seg = y[max(0, j0 - 1):j1]
        bounce[f] = (seg.max() - seg.min()) / 2.0
    return swing, bounce


# --- measurement --------------------------------------------------------------
def measure(man: dict) -> dict:
    g, l, A = man["g"], man["length_m"], man["bounce_m"]
    tilt = math.radians(man["tilt_deg"])
    sps, csps = man["steps_per_s"], man["check_steps_per_s"]
    tm, ts, fps = man["measure_duration"], man["scene_duration"], man["fps"]
    n_frames = int(round(ts * fps))
    ppm = man["px_per_m"]
    print(f"setup: a point bob on a light spring from a fixed pivot; stretched equilibrium length {l:g} m; the bob "
          f"pulled down {A * 100:g} cm below the equilibrium with a {man['tilt_deg']:g} degree tilt from vertical and "
          f"released at rest; two panels share every input, only the spring differs: "
          + "; ".join(f"{q['label']} (k/m = {q['bounces_per_swing'] ** 2:g} g/l)" for q in man["panels"])
          + f"; full two-degree-of-freedom polar equations, no small-angle approximation, no damping; RK4 at {sps} "
          f"steps/s ({1000 / sps:.2f} ms), half-step check at {csps}; measured over {tm:g} s, scene {ts:g} s at {fps} "
          f"fps ({n_frames} frames), real time; drawn at {ppm:g} px per metre; deterministic, no seed")
    ev = {"panels": [], "runs": {}, "reads": {}}
    for panel in man["panels"]:
        p = panel_params(man, panel)
        run = rk4_run(p, l + A, tilt, sps, tm)
        t, th, r, rd = run["t"], run["th"], run["r"], run["rd"]
        T_swing_cf = 2 * math.pi * math.sqrt(l / g)
        T_bounce_cf = 2 * math.pi / math.sqrt(p["k_over_m"])
        T_swing, n_sw = period_from_crossings(t, th, 10.0)
        T_bounce, n_bo = period_from_crossings(t, rd, 10.0)
        T_swing_late, n_late = period_from_crossings(t, th, 20.0)
        T_swing_late = 2.0 * (T_swing_late * n_late / 2.0 - T_swing * n_sw / 2.0) / (n_late - n_sw)
        print(f"{p['name']} ({p['label']}): k/m = {p['k_over_m']:.4f} s^-2, natural length {p['l0']:.4f} m, "
              f"stretched to {l:g} m; swing period {T_swing:.4f} s from {n_sw} zero-crossing intervals of theta in the "
              f"first 10 s and {T_swing_late:.4f} s from the {n_late - n_sw} intervals between 10 and 20 s (closed form "
              f"2 pi sqrt(l/g) = {T_swing_cf:.4f} s); bounce period {T_bounce:.4f} s from {n_bo} zero-crossing intervals "
              f"of r' in the first 10 s (closed form 2 pi sqrt(m/k) = {T_bounce_cf:.4f} s); ratio "
              f"{T_swing_cf / T_bounce_cf:.4f} bounces per swing by the closed forms")
        t1, t5 = first_pass(t, th, math.radians(1.0)), first_pass(t, th, math.radians(5.0))
        tp40, pk40 = peak_within(t, th, ts)
        tp60, pk60 = peak_within(t, th, tm)
        y = r * np.cos(th)
        rad40 = window_amp(t, r, tp40 - T_bounce / 2, tp40 + T_bounce / 2)
        ver40 = window_amp(t, y, tp40 - T_bounce / 2, tp40 + T_bounce / 2)
        rad60 = window_amp(t, r, tp60 - T_bounce / 2, tp60 + T_bounce / 2)
        ver60 = window_amp(t, y, tp60 - T_bounce / 2, tp60 + T_bounce / 2)
        print(f"{p['name']}: swing angle first passes 1 degree at "
              + (f"{t1:.2f} s" if t1 is not None else f"never in {tm:g} s")
              + " and 5 degrees at " + (f"{t5:.2f} s" if t5 is not None else f"never in {tm:g} s")
              + f"; peak swing within {ts:g} s: {math.degrees(pk40):.2f} degrees at {tp40:.2f} s, bounce there "
              f"{rad40 * 100:.2f} cm radial and {ver40 * 100:.2f} cm vertical (half the range over one bounce period); "
              f"peak swing within {tm:g} s: {math.degrees(pk60):.2f} degrees at {tp60:.2f} s, bounce there "
              f"{rad60 * 100:.2f} cm radial and {ver60 * 100:.2f} cm vertical; largest angle over {tm:g} s "
              f"{math.degrees(pk60):.3f} degrees")
        swing_read, bounce_read = trailing_readouts(run, T_swing, T_bounce, fps, n_frames)
        i_end = n_frames - 1
        print(f"{p['name']}: readouts (largest |theta| over the last swing period, half the vertical range over the "
              f"last bounce period) at the scene end {i_end / fps:.2f} s: swing {swing_read[i_end]:.2f} deg, bounce "
              f"{bounce_read[i_end] * 100:.2f} cm; readout peak swing {swing_read.max():.2f} deg at frame "
              f"{int(swing_read.argmax())} ({swing_read.argmax() / fps:.2f} s), the bounce readout there "
              f"{bounce_read[int(swing_read.argmax())] * 100:.2f} cm; the smallest bounce readout {bounce_read.min() * 100:.2f} "
              f"cm at {bounce_read.argmin() / fps:.2f} s")
        e = energy(p, run)
        e_bounce = 0.5 * p["k_over_m"] * A * A
        drift = float(np.abs(e - e[0]).max())
        print(f"{p['name']}: energy drift over {tm:g} s: max |E - E0| = {drift:.2e} J/kg, {drift / e_bounce * 100:.2e} "
              f"percent of the bounce energy {e_bounce:.4f} J/kg (E0 = {e[0]:.6f} J/kg)")
        # Half-step check.
        chk = rk4_run(p, l + A, tilt, csps, tm)
        c5 = first_pass(chk["t"], chk["th"], math.radians(5.0))
        ctp, cpk = peak_within(chk["t"], chk["th"], tm)
        print(f"{p['name']}: half-step check at {csps} steps/s: 5 degrees at "
              + (f"{c5:.4f} s" if c5 is not None else "never")
              + (f" (diff {abs(c5 - t5):.1e} s)" if c5 is not None and t5 is not None else "")
              + f"; peak {math.degrees(cpk):.4f} degrees at {ctp:.4f} s against {math.degrees(pk60):.4f} at {tp60:.4f} "
              f"(diffs {abs(math.degrees(cpk) - math.degrees(pk60)):.1e} degrees, {abs(ctp - tp60):.1e} s)")
        # Geometry check: the lowest bob edge in the frame over the scene.
        m = t <= ts
        depth_px = man["pivot_y_px"] + ppm * (r[m] * np.cos(th[m])).max() + man["bob_radius_px"]
        side_px = ppm * np.abs(r[m] * np.sin(th[m])).max()
        print(f"{p['name']}: lowest bob edge y = {depth_px:.0f} px (readout row from {READ_Y[0] - 20} px); largest "
              f"sideways reach {side_px:.0f} px of the {W / 2 / 2:.0f} px panel half-width; r ranges {r[m].min():.4f} "
              f"to {r[m].max():.4f} m in the scene")
        ev["panels"].append({**p, "T_swing": T_swing, "T_bounce": T_bounce, "t1": t1, "t5": t5, "tp40": tp40,
                             "pk40_deg": math.degrees(pk40), "tp60": tp60, "pk60_deg": math.degrees(pk60),
                             "rad40": rad40, "ver40": ver40, "drift": drift})
        ev["runs"][p["name"]] = run
        ev["reads"][p["name"]] = (swing_read, bounce_read)
    # Schedule.
    hold_end = ts - man["loop_fade"]
    tuned = ev["panels"][0]
    print(f"schedule (real time, one run from release at 0 s): tuned swing passes 1 degree at {tuned['t1']:.2f} s and "
          f"5 degrees at {tuned['t5']:.2f} s, peaks at {tuned['tp40']:.2f} s; loop fade {hold_end:.2f} to {ts:.2f} s; "
          f"title until {man['title_until']:g} s; payoff card from {man['payoff_t']:g} s")
    # Text widths.
    font = os.environ["SEED_ZERO_FONT"]
    f32, f34, f36, f40, f56 = (ImageFont.truetype(font, n) for n in (32, 34, 36, 40, 56))
    widths = {"overlay@34": (f34, man["overlay"])}
    for j, line in enumerate(man["title"].split("|")):
        widths[f"title line {j + 1}@56"] = (f56, line)
    for p in ev["panels"]:
        widths[f"label {p['name']}@36"] = (f36, p["label"])
    widths["swing readout@40"] = (f40, "swing 11.4 deg")
    widths["bounce readout@36"] = (f36, "bounce 10.0 cm")
    widths["clock@32"] = (f32, "40.0 s")
    for j, line in enumerate(payoff_lines(man, ev)):
        widths[f"payoff line {j + 1}@40"] = (f40, line)
    print("text widths: " + ", ".join(f"{k} {f.getlength(s):.0f} px" for k, (f, s) in widths.items()))
    return ev


def payoff_lines(man: dict, ev: dict) -> list[str]:
    tuned, detuned = ev["panels"]
    text = man["payoff_text"].format(peak_tuned=tuned["pk40_deg"], bounce_tuned=tuned["ver40"] * 100,
                                     peak_detuned=detuned["pk60_deg"])
    return [s.strip() for s in text.split("|")]


# --- rendering ---------------------------------------------------------------
class Renderer:
    def __init__(self, man: dict, ev: dict):
        self.man, self.ev = man, ev
        self.fps = man["fps"]
        font = os.environ["SEED_ZERO_FONT"]
        self.font = ImageFont.truetype(font, 40)
        self.font_title = ImageFont.truetype(font, 56)
        self.font_label = ImageFont.truetype(font, 36)
        self.font_clock = ImageFont.truetype(font, 32)
        self.ppm = float(man["px_per_m"])
        self.r_bob = float(man["bob_radius_px"])
        self.py = float(man["pivot_y_px"])
        self.steps_per_frame = man["steps_per_s"] / self.fps
        self.first = None

    def state(self, name: str, f: int) -> tuple[float, float]:
        run = self.ev["runs"][name]
        i = min(int(round(f * self.steps_per_frame)), len(run["t"]) - 1)
        return float(run["r"][i]), float(run["th"][i])

    def L(self, x: float, y: float) -> tuple[float, float]:
        return x * SS, (y - GEOM_Y0) * SS

    def draw_spring(self, d: ImageDraw.ImageDraw, a: tuple[float, float], b: tuple[float, float]) -> None:
        dx, dy = b[0] - a[0], b[1] - a[1]
        length = math.hypot(dx, dy)
        ux, uy = dx / length, dy / length
        nx, ny = -uy, ux
        lead = 22.0 * SS
        coils = 14
        amp = 16.0 * SS
        pts = [a, (a[0] + ux * lead, a[1] + uy * lead)]
        inner = length - 2 * lead
        for i in range(1, 2 * coils):
            s = lead + inner * i / (2 * coils)
            off = amp if i % 2 else -amp
            pts.append((a[0] + ux * s + nx * off, a[1] + uy * s + ny * off))
        pts.append((b[0] - ux * lead, b[1] - uy * lead))
        pts.append(b)
        d.line(pts, fill=SPRING, width=3 * SS, joint="curve")

    def draw_geometry(self, d: ImageDraw.ImageDraw, f: int) -> None:
        man = self.man
        Lpx = man["length_m"] * self.ppm
        for k, p in enumerate(self.ev["panels"]):
            px, col = float(man["panel_x_px"][k]), COLOURS[p["name"]]
            r, th = self.state(p["name"], f)
            swing_deg = float(self.ev["reads"][p["name"]][0][min(f, len(self.ev["reads"][p["name"]][0]) - 1)])
            # Straight-down reference and the faint arc of the latest swing.
            X0, Y0 = self.L(px, self.py)
            d.line((X0, Y0, X0, Y0 + Lpx * SS), fill=WIRE, width=2 * SS)
            if swing_deg > 0.3:
                rr = Lpx * SS
                d.arc((X0 - rr, Y0 - rr, X0 + rr, Y0 + rr), start=90 - swing_deg, end=90 + swing_deg,
                      fill=blend(col, 0.45), width=3 * SS)
            # Top bar and pivot.
            d.line((X0 - 150 * SS, Y0, X0 + 150 * SS, Y0), fill=BEAM, width=8 * SS)
            # Spring and bob.
            bx, by = px + r * self.ppm * math.sin(th), self.py + r * self.ppm * math.cos(th)
            BX, BY = self.L(bx, by)
            ux, uy = (BX - X0), (BY - Y0)
            n = math.hypot(ux, uy)
            ux, uy = ux / n, uy / n
            rb = self.r_bob * SS
            self.draw_spring(d, (X0, Y0), (BX - ux * rb, BY - uy * rb))
            d.ellipse((X0 - 8 * SS, Y0 - 8 * SS, X0 + 8 * SS, Y0 + 8 * SS), fill=BEAM)
            d.ellipse((BX - rb, BY - rb, BX + rb, BY + rb), fill=col)
            d.ellipse((BX - 7 * SS, BY - 7 * SS, BX + 7 * SS, BY + 7 * SS), fill=BG)

    def draw_text(self, d: ImageDraw.ImageDraw, f: int, title_on: bool) -> None:
        man = self.man
        for k, p in enumerate(self.ev["panels"]):
            px, col = man["panel_x_px"][k], COLOURS[p["name"]]
            swing, bounce = self.ev["reads"][p["name"]]
            i = min(f, len(swing) - 1)
            d.text((px, LABEL_Y), p["label"], font=self.font_label, fill=col, anchor="mm")
            d.text((px, READ_Y[0]), f"swing {swing[i]:.1f} deg", font=self.font, fill=col, anchor="mm")
            d.text((px, READ_Y[1]), f"bounce {bounce[i] * 100:.1f} cm", font=self.font_label, fill=MUTED, anchor="mm")
        # The clock sits on the title's second row, so it is hidden while the title shows and during the
        # loop fade, when the title frame is blended back in.
        if not title_on and f / self.fps < man["scene_duration"] - man["loop_fade"]:
            d.text((W / 2, CLOCK_Y), f"{f / self.fps:.1f} s", font=self.font_clock, fill=MUTED, anchor="mm")

    def live_frame(self, f: int) -> np.ndarray:
        man = self.man
        t = f / self.fps
        title_on = t < man["title_until"]
        img = Image.new("RGB", (W, H), BG)
        layer = Image.new("RGB", (W * SS, (GEOM_Y1 - GEOM_Y0) * SS), BG)
        self.draw_geometry(ImageDraw.Draw(layer), f)
        img.paste(layer.reduce(SS), (0, GEOM_Y0))
        d = ImageDraw.Draw(img)
        self.draw_text(d, f, title_on)
        if title_on:
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
    man = json.loads((ROOT / "projects/springswap/manifest.json").read_text())
    ev = measure(man)
    if "--measure-only" in sys.argv:
        return
    if "--frames" in sys.argv:
        times = [float(v) for v in sys.argv[sys.argv.index("--frames") + 1].split(",")]
        r = Renderer(man, ev)
        (ROOT / "media/springswap").mkdir(parents=True, exist_ok=True)
        for tv in times:
            Image.fromarray(r.frame_at(int(round(tv * man["fps"])))).save(ROOT / f"media/springswap/smoke-{tv}.png")
        print("smoke frames: " + ", ".join(f"{tv}" for tv in times))
        return
    Renderer(man, ev).render(ROOT / "media/springswap/footage.mp4")


if __name__ == "__main__":
    main()
