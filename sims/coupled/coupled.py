#!/usr/bin/env python3
"""Coupled pendulum swap: can a swing pass its motion to its neighbour?

Two identical simple pendulums (point bobs) hang from pivots a fixed
distance apart and are joined at bob level by a light spring whose natural
length equals the pivot spacing, so the spring pulls bob 1 with
k (x2 - x1) where x_i = L sin(theta_i) is each bob's sideways offset from
its own pivot. The left pendulum starts at the manifest angle, the right
one hangs at rest. Below them the same pair swings with no spring. Full
nonlinear equations, no damping:

    theta1'' = -(g / L) sin theta1 + (k / m) (sin theta2 - sin theta1) cos theta1
    theta2'' = -(g / L) sin theta2 - (k / m) (sin theta2 - sin theta1) cos theta2

integrated with RK4 at a fixed step. Deterministic, no seed.

The length puts the in-phase mode at omega1 = pi rad/s and the spring puts
the opposite-phase mode at omega2 = 21 pi / 20, so the two modes beat and
the linear closed forms give the full swap at pi / (omega2 - omega1) =
20.000 s and the return at 40.000 s.

Measured and printed: the peak angle of each pendulum on every swing, the
moment pendulum 1 has the least energy (the swap) and how big its swing is
then, pendulum 2's peak at that moment, the envelope fitted through the
swing peaks and its crossing, the return to pendulum 1, the state at the
end of the scene against the start, the two mode periods measured
separately, an energy check, a half-step check, and the no-spring pair.

usage: coupled.py [--measure-only] [--frames t1,t2,...]
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
BEAM = (120, 130, 145)
STRING = (160, 168, 180)

# Layout: overlay at y 96..130 (compose), title rows at y 190/252/314 for
# the first seconds, two panels stacked (a label row with the readouts 50 px
# above each pivot bar, strings about 400 px, bobs of radius 30), captions
# at caption_y 0.75 (y 1440..1520), payoff card from y 1592. A running
# clock sits at y 250 once the title has faded.
PAYOFF_Y = 1592.0
CLOCK_Y = 250
ROW_ABOVE_PIVOT = 50
PANELS = [
    {"name": "spring", "label": "with a spring", "colour": GOLD, "spring": True},
    {"name": "free", "label": "no spring", "colour": MUTED, "spring": False},
]


def rk4_run(g_over_l: float, k_over_m: float, th1: float, th2: float, steps_per_s: int, t_end: float) -> dict:
    """Integrate both pendulums; return per-step arrays of time, angles, rates and energies."""
    dt = 1.0 / steps_per_s
    n = int(round(t_end * steps_per_s))

    def deriv(s: tuple[float, float, float, float]) -> tuple[float, float, float, float]:
        a1, w1, a2, w2 = s
        s1, s2 = math.sin(a1), math.sin(a2)
        c = k_over_m * (s2 - s1)
        return (w1, -g_over_l * s1 + c * math.cos(a1), w2, -g_over_l * s2 - c * math.cos(a2))

    s = (th1, 0.0, th2, 0.0)
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
    return {"t": t, "th1": out[:, 0], "w1": out[:, 1], "th2": out[:, 2], "w2": out[:, 3], "dt": dt}


def energies(run: dict, g: float, L: float, k_over_m: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Per unit mass: pendulum 1, pendulum 2 and the total including the spring."""
    e1 = 0.5 * L * L * run["w1"] ** 2 + g * L * (1.0 - np.cos(run["th1"]))
    e2 = 0.5 * L * L * run["w2"] ** 2 + g * L * (1.0 - np.cos(run["th2"]))
    spring = 0.5 * k_over_m * (L * np.sin(run["th2"]) - L * np.sin(run["th1"])) ** 2
    return e1, e2, e1 + e2 + spring


def amp_deg(e: float, g: float, L: float) -> float:
    """The swing angle a pendulum with energy e per unit mass would reach."""
    return math.degrees(math.acos(max(-1.0, 1.0 - e / (g * L))))


def turning_points(t: np.ndarray, th: np.ndarray, w: np.ndarray) -> list[tuple[float, float]]:
    """(time, |angle| in degrees) where the rate crosses zero, interpolated."""
    out = []
    sign = np.sign(w)
    for i in range(1, len(w)):
        if sign[i - 1] != 0 and sign[i] != sign[i - 1]:
            f = w[i - 1] / (w[i - 1] - w[i])
            tt = t[i - 1] + f * (t[i] - t[i - 1])
            a = th[i - 1] + f * (th[i] - th[i - 1])
            out.append((float(tt), abs(math.degrees(a))))
    return out


def argmin_interp(t: np.ndarray, y: np.ndarray, lo: float, hi: float) -> tuple[float, float]:
    """Time and value of the minimum of y on [lo, hi] with parabolic interpolation."""
    m = (t >= lo) & (t <= hi)
    idx = np.flatnonzero(m)
    i = idx[int(np.argmin(y[idx]))]
    if 0 < i < len(y) - 1:
        y0, y1, y2 = y[i - 1], y[i], y[i + 1]
        denom = y0 - 2 * y1 + y2
        off = 0.5 * (y0 - y2) / denom if denom != 0 else 0.0
        return float(t[i] + off * (t[1] - t[0])), float(y1 - 0.25 * (y0 - y2) * off)
    return float(t[i]), float(y[i])


def sample_at(run: dict, tt: float) -> tuple[float, float, float, float]:
    i = int(round(tt / run["dt"]))
    i = min(max(i, 0), len(run["t"]) - 1)
    return run["th1"][i], run["w1"][i], run["th2"][i], run["w2"][i]


def envelope_fit(peaks: list[tuple[float, float]], t_swap: float, span: float) -> tuple[float, float]:
    """Straight lines through the swing peaks on each side of t_swap; their crossing."""
    before = [(tt, a) for tt, a in peaks if t_swap - span <= tt < t_swap - 0.2]
    after = [(tt, a) for tt, a in peaks if t_swap + 0.2 < tt <= t_swap + span]
    m1, b1 = np.polyfit([p[0] for p in before], [p[1] for p in before], 1)
    m2, b2 = np.polyfit([p[0] for p in after], [p[1] for p in after], 1)
    tx = (b2 - b1) / (m1 - m2)
    return float(tx), float(m1 * tx + b1)


def mode_period(run: dict, which: str) -> float:
    """Mean spacing of same-side turning points of one pendulum over the run."""
    tp = turning_points(run["t"], run[which], run["w" + which[-1]])
    times = [tt for tt, _ in tp]
    same = times[::2]
    return (same[-1] - same[0]) / (len(same) - 1)


def measure(man: dict) -> dict:
    g, L, m, k = man["g"], man["length_m"], man["mass_kg"], man["spring_k_n_per_m"]
    gL, km = g / L, k / m
    a0, b0 = math.radians(man["start_deg"]), math.radians(man["start_deg_2"])
    sps = man["steps_per_s"]
    dur, tm = man["scene_duration"], man["measure_duration"]
    w1_lin, w2_lin = math.sqrt(gL), math.sqrt(gL + 2 * km)
    t_swap_lin = math.pi / (w2_lin - w1_lin)
    print(f"setup: two identical pendulums of length {L:.5f} m (g / pi^2, small-swing period "
          f"{2 * math.pi / w1_lin:.4f} s), point bobs of {m * 1000:g} g, pivots {man['pivot_gap_m']:g} m apart, "
          f"joined at bob level by a spring of k = {k:.6f} N/m (k / m = {km:.5f} s^-2) with natural length equal "
          f"to the pivot spacing; the left pendulum starts at {man['start_deg']:g} degrees, the right at "
          f"{man['start_deg_2']:g} degrees, both at rest; the same pair with no spring below; RK4 at {sps} steps "
          f"per second (dt = {1 / sps:.2e} s) for {tm:g} s, {dur:g} s shown; deterministic, no seed")
    print(f"linear closed forms: in-phase mode omega1 = sqrt(g / L) = {w1_lin:.5f} rad/s (period "
          f"{2 * math.pi / w1_lin:.4f} s, {dur * w1_lin / (2 * math.pi):.2f} swings in {dur:g} s), opposite mode "
          f"omega2 = sqrt(g / L + 2 k / m) = {w2_lin:.5f} rad/s (period {2 * math.pi / w2_lin:.4f} s, "
          f"{dur * w2_lin / (2 * math.pi):.2f} swings), difference {w2_lin - w1_lin:.5f} rad/s = pi / 20; full swap "
          f"at pi / (omega2 - omega1) = {t_swap_lin:.3f} s, back at {2 * t_swap_lin:.3f} s")

    run = rk4_run(gL, km, a0, b0, sps, tm)
    e1, e2, et = energies(run, g, L, km)
    t = run["t"]
    p1 = turning_points(t, run["th1"], run["w1"])
    p2 = turning_points(t, run["th2"], run["w2"])

    # Mechanism table: pendulum 1's swings (pairs of turning points) and the
    # largest angle each pendulum reaches in each.
    rows = []
    bounds = [0.0] + [tt for tt, _ in p1]
    for n in range(0, len(bounds) - 2, 2):
        lo, hi = bounds[n], bounds[n + 2]
        if hi > dur + 0.5:
            break
        mask = (t >= lo) & (t <= hi)
        rows.append((n // 2 + 1, hi, math.degrees(np.abs(run["th1"][mask]).max()),
                     math.degrees(np.abs(run["th2"][mask]).max())))
    print("swings of the left pendulum (swing, end time, left peak, right peak in degrees): " +
          "; ".join(f"{n} {hi:.2f} s {a:.2f} {b:.2f}" for n, hi, a, b in rows))

    # The swap: the moment the left pendulum has the least energy.
    t_swap, e_swap = argmin_interp(t, e1, 0.25 * tm, 0.75 * tm)
    th1_s, w1_s, th2_s, w2_s = sample_at(run, t_swap)
    p2_near = min(p2, key=lambda p: abs(p[0] - t_swap))
    p1_min = min((p for p in p1 if abs(p[0] - t_swap) < 3.0), key=lambda p: p[1])
    p1_small = sorted((p for p in p1 if 0.3 < abs(p[0] - t_swap) < 1.0), key=lambda p: p[0])
    t_env, a_env = envelope_fit([p for p in p1 if p[1] > 0.05], t_swap, 4.0)
    print(f"swap: the left pendulum has its least energy at {t_swap:.3f} s, a swing of {amp_deg(e_swap, g, L):.4f} "
          f"degrees (angle {math.degrees(th1_s):.4f} degrees, rate {math.degrees(w1_s):.4f} degrees/s); the "
          f"right pendulum is then at {math.degrees(th2_s):.3f} degrees moving at {math.degrees(w2_s):.3f} "
          f"degrees/s, its nearest swing peak {p2_near[1]:.3f} degrees at {p2_near[0]:.3f} s; the left pendulum's "
          f"smallest turning point is {p1_min[1]:.4f} degrees at {p1_min[0]:.3f} s and its neighbouring swing "
          f"peaks are " + ", ".join(f"{a:.3f} degrees at {tt:.3f} s" for tt, a in p1_small) +
          f"; straight lines through the swing peaks over 4 s on each side cross at {t_env:.3f} s at "
          f"{a_env:.3f} degrees; linear closed form {t_swap_lin:.3f} s")

    # The return: the right pendulum has the least energy near twice the swap.
    t_back, e_back = argmin_interp(t, e2, 0.75 * tm, tm)
    th1_b, w1_b, th2_b, w2_b = sample_at(run, t_back)
    print(f"back: the right pendulum has its least energy at {t_back:.3f} s, a swing of {amp_deg(e_back, g, L):.4f} "
          f"degrees; the left pendulum is then at {math.degrees(th1_b):.3f} degrees moving at "
          f"{math.degrees(w1_b):.3f} degrees/s; linear closed form {2 * t_swap_lin:.3f} s; {t_swap:.3f} s to "
          f"the swap and {t_back - t_swap:.3f} s back")

    # Loop closure at the end of the scene.
    th1_e, w1_e, th2_e, w2_e = sample_at(run, dur)
    ppm = man["px_per_m"]
    dx1 = (math.sin(th1_e) - math.sin(a0)) * L * ppm
    dx2 = (math.sin(th2_e) - math.sin(b0)) * L * ppm
    print(f"loop: at {dur:g} s the left pendulum is at {math.degrees(th1_e):.3f} degrees moving at "
          f"{math.degrees(w1_e):.3f} degrees/s and the right at {math.degrees(th2_e):.3f} degrees moving at "
          f"{math.degrees(w2_e):.3f} degrees/s, against {man['start_deg']:g} and {man['start_deg_2']:g} degrees at "
          f"rest at the start: the bobs are {abs(dx1):.1f} px and {abs(dx2):.1f} px from their first-frame "
          f"positions; the {man['loop_fade']:g} s loop fade covers the difference")

    # Carrier: the left pendulum's own swing period over its first seven swings
    # (the turning points near the swap shift with the envelope).
    same = [tt for tt, _ in p1][1::2][:8]
    carrier = (same[-1] - same[0]) / (len(same) - 1)
    print(f"carrier: the left pendulum swings every {carrier:.4f} s over its first seven swings "
          f"({t_swap / carrier:.2f} swings to the swap); linear mean of the two modes "
          f"{2 * math.pi / (0.5 * (w1_lin + w2_lin)):.4f} s")

    # Modes measured on their own: both started together, and opposite, at the
    # start angle and at a small angle where the linear closed forms apply;
    # and a small-angle swap.
    small = math.radians(man["small_deg"])
    lines = []
    for ang in (a0, small):
        inph = rk4_run(gL, km, ang, ang, sps, 20.0)
        anti = rk4_run(gL, km, ang, -ang, sps, 20.0)
        lines.append(f"started together at {math.degrees(ang):g} degrees they swing every "
                     f"{mode_period(inph, 'th1'):.4f} s and started opposite every {mode_period(anti, 'th1'):.4f} s")
    srun = rk4_run(gL, km, small, 0.0, sps, tm)
    se1, _, _ = energies(srun, g, L, km)
    t_swap_small, e_swap_small = argmin_interp(srun["t"], se1, 0.25 * tm, 0.75 * tm)
    print(f"modes: {'; '.join(lines)} (linear {2 * math.pi / w1_lin:.4f} s and {2 * math.pi / w2_lin:.4f} s); "
          f"a {man['small_deg']:g} degree start swaps at {t_swap_small:.3f} s with a swing of "
          f"{amp_deg(e_swap_small, g, L):.4f} degrees (linear {t_swap_lin:.3f} s); the {man['start_deg']:g} degree "
          f"start swaps at {t_swap:.3f} s, {100 * (t_swap / t_swap_lin - 1):.2f} percent later")

    # Energy, half-step and no-spring checks.
    drift = float(np.abs(et - et[0]).max() / et[0])
    half = rk4_run(gL, km, a0, b0, man["check_steps_per_s"], tm)
    he1, _, _ = energies(half, g, L, km)
    t_swap_h, e_swap_h = argmin_interp(half["t"], he1, 0.25 * tm, 0.75 * tm)
    free = rk4_run(gL, 0.0, a0, b0, sps, tm)
    free_peak2 = math.degrees(np.abs(free["th2"]).max())
    T_free = mode_period(free, "th1")
    print(f"checks: total energy drifts by at most {drift:.1e} relative over {tm:g} s; at {man['check_steps_per_s']} "
          f"steps per second the swap is at {t_swap_h:.3f} s with a swing of {amp_deg(e_swap_h, g, L):.4f} "
          f"degrees; no spring: the right pendulum's largest angle over {tm:g} s is {free_peak2:.3f} degrees and "
          f"the left one swings every {T_free:.4f} s (its {man['start_deg']:g} degree swing lengthens the "
          f"{2 * math.pi / w1_lin:.4f} s small-swing period by {100 * (T_free / (2 * math.pi / w1_lin) - 1):.2f} "
          f"percent)")
    return {"run": run, "free": free, "p1": p1, "p2": p2, "t_swap": t_swap, "t_back": t_back, "rows": rows,
            "free_peak2": free_peak2, "amp_swap": amp_deg(e_swap, g, L), "peak2_swap": p2_near[1]}


def last_peaks(t: np.ndarray, peaks: list[tuple[float, float]], start_deg: float) -> np.ndarray:
    """For every step, the |angle| at the pendulum's latest turning point (the start until the first)."""
    out = np.full(len(t), abs(start_deg))
    times = np.array([tt for tt, _ in peaks])
    vals = np.array([a for _, a in peaks])
    if len(times):
        idx = np.searchsorted(times, t, side="right") - 1
        has = idx >= 0
        out[has] = vals[idx[has]]
    return out


class Renderer:
    def __init__(self, man: dict, meas: dict):
        self.man, self.meas = man, meas
        self.fps = man["fps"]
        font = os.environ["SEED_ZERO_FONT"]
        self.font = ImageFont.truetype(font, 40)
        self.font_read = ImageFont.truetype(font, 36)
        self.font_title = ImageFont.truetype(font, 56)
        self.first = None
        self.ppm = man["px_per_m"]
        self.L = man["length_m"] * self.ppm
        self.r = man["bob_radius_px"]
        run, free = meas["run"], meas["free"]
        t = run["t"]
        self.angles = {
            "spring": (run["th1"], run["th2"]),
            "free": (free["th1"], free["th2"]),
        }
        fp1 = turning_points(free["t"], free["th1"], free["w1"])
        self.reads = {
            "spring": (last_peaks(t, meas["p1"], man["start_deg"]), last_peaks(t, meas["p2"], man["start_deg_2"])),
            "free": (last_peaks(t, fp1, man["start_deg"]), np.zeros(len(t))),
        }
        self.steps_per_frame = man["steps_per_s"] // self.fps
        widths = {"overlay@34": (ImageFont.truetype(font, 34), man["overlay"])}
        for j, line in enumerate(man["title"].split("|")):
            widths[f"title line {j + 1}@56"] = (self.font_title, line)
        for p in PANELS:
            widths[f"label {p['name']}@40"] = (self.font, p["label"])
        widths["readout@36"] = (self.font_read, "10.0 deg")
        widths["clock@40"] = (self.font, "40.0 s")
        for j, line in enumerate(self.payoff_lines()):
            widths[f"payoff line {j + 1}@40"] = (self.font, line)
        print("text widths: " + ", ".join(f"{k} {f.getlength(s):.0f} px" for k, (f, s) in widths.items()))
        print(f"video: real time, {man['scene_duration']:g} s; the swap is at {meas['t_swap']:.3f} s and the "
              f"return at {meas['t_back']:.3f} s; payoff card at {man['payoff_t']:g} s; strings {self.L:.0f} px, "
              f"bobs {self.r} px, pivots {man['pivot_x_px'][1] - man['pivot_x_px'][0]} px apart")

    def payoff_lines(self) -> list[str]:
        text = self.man["payoff_text"].format(swap=self.meas["t_swap"], back=self.meas["t_back"])
        return [s.strip() for s in text.split("|")]

    def draw_spring(self, d: ImageDraw.ImageDraw, a: tuple[float, float], b: tuple[float, float]) -> None:
        dx, dy = b[0] - a[0], b[1] - a[1]
        length = math.hypot(dx, dy)
        ux, uy = dx / length, dy / length
        nx, ny = -uy, ux
        lead = 18.0
        coils = 12
        amp = 12.0
        pts = [a, (a[0] + ux * lead, a[1] + uy * lead)]
        inner = length - 2 * lead
        for i in range(1, 2 * coils):
            s = lead + inner * i / (2 * coils)
            off = amp if i % 2 else -amp
            pts.append((a[0] + ux * s + nx * off, a[1] + uy * s + ny * off))
        pts.append((b[0] - ux * lead, b[1] - uy * lead))
        pts.append(b)
        d.line(pts, fill=GOLD, width=3, joint="curve")

    def draw_scene(self, t: float, title_on: bool) -> Image.Image:
        man = self.man
        img = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(img)
        i = min(int(round(t * man["steps_per_s"])), len(self.meas["run"]["t"]) - 1)
        L, r = self.L, self.r
        xs = man["pivot_x_px"]
        for p, py in zip(PANELS, man["pivot_y_px"]):
            th = [self.angles[p["name"]][q][i] for q in range(2)]
            reads = [self.reads[p["name"]][q][i] for q in range(2)]
            # Beam and pivots.
            d.line([(xs[0] - 70, py), (xs[1] + 70, py)], fill=BEAM, width=8)
            bobs = []
            for q, (px, col) in enumerate(zip(xs, (CORAL, TEAL))):
                # Faint arc of the latest swing peak.
                rr = L + 26
                if reads[q] > 0.02:
                    d.arc((px - rr, py - rr, px + rr, py + rr), start=90 - reads[q], end=90 + reads[q],
                          fill=WIRE, width=3)
                bx, by = px + L * math.sin(th[q]), py + L * math.cos(th[q])
                bobs.append((bx, by))
            if p["spring"]:
                (x1, y1), (x2, y2) = bobs
                ux, uy = x2 - x1, y2 - y1
                n = math.hypot(ux, uy)
                ux, uy = ux / n, uy / n
                self.draw_spring(d, (x1 + ux * (r + 2), y1 + uy * (r + 2)), (x2 - ux * (r + 2), y2 - uy * (r + 2)))
            for q, (px, col) in enumerate(zip(xs, (CORAL, TEAL))):
                bx, by = bobs[q]
                d.line([(px, py), (bx, by)], fill=STRING, width=3)
                d.ellipse((px - 8, py - 8, px + 8, py + 8), fill=BEAM)
                d.ellipse((bx - r, by - r, bx + r, by + r), fill=col)
                d.ellipse((bx - 7, by - 7, bx + 7, by + 7), fill=BG)
            if not title_on:
                ry = py - ROW_ABOVE_PIVOT
                d.text((W / 2, ry), p["label"], font=self.font, fill=p["colour"], anchor="mm")
                d.text((110, ry), f"{reads[0]:.1f} deg", font=self.font_read, fill=CORAL, anchor="lm")
                d.text((970, ry), f"{reads[1]:.1f} deg", font=self.font_read, fill=TEAL, anchor="rm")
        if not title_on:
            d.text((W / 2, CLOCK_Y), f"{t:.1f} s", font=self.font, fill=TEXT, anchor="mm")
        return img

    def live_frame(self, f: int) -> np.ndarray:
        man = self.man
        t = f / self.fps
        title_on = t < man["title_until"]
        img = self.draw_scene(t, title_on)
        d = ImageDraw.Draw(img)

        def shade_col(col, a):
            return tuple(int(c * a + BG[j] * (1 - a)) for j, c in enumerate(col))

        if title_on:
            a = 1.0 if t < man["title_until"] - 0.4 else (man["title_until"] - t) / 0.4
            for j, line in enumerate(man["title"].split("|")):
                d.text((W / 2, 190 + j * 62), line, font=self.font_title, fill=shade_col(TEXT, a), anchor="mm")
        if t >= man["payoff_t"]:
            a = min(1.0, (t - man["payoff_t"]) / man["payoff_hold"])
            for j, line in enumerate(self.payoff_lines()):
                d.text((W / 2, PAYOFF_Y + j * 56), line, font=self.font, fill=shade_col(GOLD, a), anchor="mm")
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
    man = json.loads((ROOT / "projects/coupled/manifest.json").read_text())
    meas = measure(man)
    if "--measure-only" in sys.argv:
        return
    if "--frames" in sys.argv:
        times = [float(v) for v in sys.argv[sys.argv.index("--frames") + 1].split(",")]
        r = Renderer(man, meas)
        for tv in times:
            Image.fromarray(r.frame_at(int(round(tv * man["fps"])))).save(ROOT / f"media/coupled/smoke-{tv}.png")
        print("smoke frames: " + ", ".join(f"{tv}" for tv in times))
        return
    Renderer(man, meas).render(ROOT / "media/coupled/footage.mp4")


if __name__ == "__main__":
    main()
