#!/usr/bin/env python3
"""Lowered or dropped: how far does the spring squash?

A 1 kg weight on a vertical massless spring with no friction and no
damping. The spring's stiffness is chosen so that it sags exactly 5 cm
under the weight at rest (k = m g / 0.05 m = 196.2 N/m). Two panels,
the same weight and the same spring. Left, lowered: a hand lowers the
weight from the spring's free top over 2.5 s along a smooth profile
(smootherstep, 2 cm/s on average) that eases to a stop at the sag; the
spring takes the load as k x and the hand carries the rest, m g - k x -
m x'', which reaches zero at x = 5 cm, where the weight rests; the hand
stays a moment carrying nothing, then moves away. The hand comes back, lifts the weight to the free top
and lowers it again, a 10 s cycle in real time. Right, dropped: the
same weight is let go from rest touching the free top. With nothing
carrying it, it passes the 5 cm resting point at speed and goes on to
x_max = 2 m g / k = 10 cm (m g x = k x^2 / 2), stops for an instant,
comes back to the top and bounces between 0 and 10 cm every
2 pi sqrt(m / k) = 0.449 s for ever, x(t) = (m g / k) (1 - cos omega t).
The dropped panel is in slow motion so that one bounce fills a whole
number of frames; both cycles divide the scene length, so the scene is
exactly periodic and the last frame equals the first. Deterministic,
no seed.

Measured and printed: the stiffness and the static sag, the hand's
share of the load through the lowering (never negative, zero at the
sag) and the residual wobble after the hand lets go (by RK4, zero; and
the wobble a hand still moving at 2 cm/s would leave), the dropped
weight by RK4 at 10,000 steps a second against the closed form (the
deepest squash, the time to reach it, the period, the speed through
the 5 cm mark, the ratio to the static sag), the energy check, the
squash from 5 and 10 cm above the spring and the sag under 2 kg for
the description, the schedule in video time, the loop and periodicity
checks and the on-screen text widths.

usage: springdrop.py [--measure-only] [--frames t1,t2,...]
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
BLOCK = (204, 210, 220)

# Layout: overlay at y 96..130 (captions.py), three title rows at y 172/234/296
# for the first seconds, then the legend at y 236 and the tag at y 290; two
# panels side by side (spring centres at x 225 and 765), each with its label
# at y 380, its time-base tag at y 420, its live readout at y 460 and its two
# fixed lines at y 502/536 (left-aligned 185 px left of the spring centre);
# the spring base at y 1380, the free top at 1380 - 0.25 m * 2000 px/m = 880,
# the block (0.10 m tall) above it, the hand bracket above the block, the
# centimetre scale 158 px right of the spring; the geometry band y 320..1420
# drawn at 2x; captions at caption_y 0.75 (y 1440..1520); the card from 1592.
LEGEND_Y, TAG_Y = 236, 290
GEOM_Y0, GEOM_Y1 = 320, 1420
SS = 2
PAYOFF_Y = 1592.0
LABEL_Y, PTAG_Y, LIVE_Y, FIX_Y = 380, 420, 460, 502
PANELS = ("lowered", "dropped")


def blend(col, a: float, base=BG) -> tuple:
    a = max(0.0, min(1.0, a))
    return tuple(int(round(c * a + b * (1 - a))) for c, b in zip(col, base))


def smoother(u: float) -> float:
    """Smootherstep 6u^5 - 15u^4 + 10u^3: zero speed and zero acceleration at both ends."""
    u = max(0.0, min(1.0, u))
    return u * u * u * (u * (6.0 * u - 15.0) + 10.0)


def smoother_dd(u: float) -> float:
    u = max(0.0, min(1.0, u))
    return 60.0 * u * (2.0 * u - 1.0) * (u - 1.0)


# --- measurement --------------------------------------------------------------
def rk4(x0: float, v0: float, g: float, k_m: float, dt: float, n: int, contact_only: bool = False) -> tuple[np.ndarray, np.ndarray]:
    """Integrate x'' = g - (k/m) x (compression x positive downward) by classical RK4 for n steps.
    With contact_only the spring pushes only while x > 0 (a weight dropped from above the free top)."""
    def acc(x: float) -> float:
        return g - k_m * (x if (x > 0.0 or not contact_only) else 0.0)
    xs, vs = np.empty(n + 1), np.empty(n + 1)
    x, v = x0, v0
    xs[0], vs[0] = x, v
    for i in range(1, n + 1):
        k1x, k1v = v, acc(x)
        k2x, k2v = v + 0.5 * dt * k1v, acc(x + 0.5 * dt * k1x)
        k3x, k3v = v + 0.5 * dt * k2v, acc(x + 0.5 * dt * k2x)
        k4x, k4v = v + dt * k3v, acc(x + dt * k3x)
        x += dt * (k1x + 2.0 * k2x + 2.0 * k3x + k4x) / 6.0
        v += dt * (k1v + 2.0 * k2v + 2.0 * k3v + k4v) / 6.0
        xs[i], vs[i] = x, v
    return xs, vs


def vertex(xs: np.ndarray, i: int, dt: float) -> tuple[float, float]:
    """Parabola through samples i-1, i, i+1: the refined extremum (time, value)."""
    a, b, c = xs[i - 1], xs[i], xs[i + 1]
    den = a - 2.0 * b + c
    off = 0.0 if den == 0.0 else 0.5 * (a - c) / den
    return (i + off) * dt, b - 0.25 * (a - c) * off


def measure(man: dict) -> dict:
    g, m, sag = man["g_m_s2"], man["mass_kg"], man["static_sag_m"]
    D, fps = man["scene_duration"], man["fps"]
    dt = 1.0 / man["steps_per_second"]
    k = m * g / sag
    omega = math.sqrt(k / m)
    T = 2.0 * math.pi / omega
    P_video = D / man["bounces"]
    slow = P_video / T
    cycle = man["lower_s"] + man["rest_s"] + man["lift_s"] + man["top_s"]
    cycles = D / cycle
    assert abs(cycles - round(cycles)) < 1e-9, "the lowering cycle must divide the scene length"
    assert abs(P_video * fps - round(P_video * fps)) < 1e-9, "a bounce must be a whole number of frames"
    assert abs(cycle * fps - round(cycle * fps)) < 1e-9, "the lowering cycle must be a whole number of frames"
    for key in ("lower_at", "bottom_at"):
        assert abs(man[key] * fps - round(man[key] * fps)) < 1e-9, f"{key} must be a whole number of frames"
    print(f"setup: a {m:g} kg weight on a vertical massless spring, no friction, no damping; the stiffness is set so "
          f"the spring sags exactly {sag * 100:g} cm under the weight at rest, k = m g / {sag:g} m = {k:.1f} N/m; "
          f"g = {g:g} m/s^2; omega = sqrt(k / m) = {omega:.4f} rad/s, one bounce every 2 pi / omega = {T:.4f} s; "
          f"left panel: a hand lowers the weight from the spring's free top over {man['lower_s']:g} s along a "
          f"smootherstep profile ({sag / man['lower_s'] * 100:.2f} cm/s on average, "
          f"{1.875 * sag / man['lower_s'] * 100:.2f} cm/s at most, easing to a stop at the sag), stays on it for "
          f"{man['linger_s']:g} s carrying nothing, moves away, comes back {man['rest_s']:g} s after the release, "
          f"lifts it back over {man['lift_s']:g} s and holds it at the top for {man['top_s']:g} "
          f"s, a {cycle:g} s cycle in real time; right panel: the same weight let go from rest touching the free top, "
          f"integrated by RK4 at {man['steps_per_second']} steps per second (dt = {dt:.0e} s) against the closed "
          f"form x(t) = (m g / k) (1 - cos omega t), shown {slow:.4f}x slow so one bounce fills {P_video:g} s "
          f"({P_video * fps:.0f} frames); {cycles:.0f} lowering cycles and {man['bounces']} bounces in {D:g} s; "
          f"drawn at {man['px_per_m']:g} px per metre; deterministic, no seed")
    # Static sags.
    sag2 = 2.0 * m * g / k
    print(f"static: the spring force k x balances the weight m g = {m * g:.2f} N at x = m g / k = {sag * 100:.2f} cm "
          f"(the setup number); under {2 * m:g} kg the sag is {sag2 * 100:.2f} cm; the spring pushes with "
          f"{k * sag:.2f} N at {sag * 100:g} cm (the weight) and {k * 2 * sag:.2f} N at {2 * sag * 100:g} cm "
          f"(twice the weight)")
    # The lowered panel: the hand's share of the load through the descent and the lift.
    n_low = int(round(man["lower_s"] / dt))
    us = np.arange(n_low + 1) / n_low
    S = np.array([smoother(u) for u in us])
    Sdd = np.array([smoother_dd(u) for u in us])
    x_h = sag * S
    xdd_h = sag * Sdd / man["lower_s"] ** 2
    F = m * g - k * x_h - m * xdd_h
    frac = F / (m * g)
    inertial = np.abs(m * xdd_h) / (m * g)
    n_lift = int(round(man["lift_s"] / dt))
    ul = np.arange(n_lift + 1) / n_lift
    x_l = sag * (1.0 - np.array([smoother(u) for u in ul]))
    F_l = m * g - k * x_l + m * sag * np.array([smoother_dd(u) for u in ul]) / man["lift_s"] ** 2
    table = ", ".join(f"{c} cm {100 * (1 - c / 100 / sag):.0f} %" for c in range(0, int(round(sag * 100)) + 1))
    # After the release: RK4 from the rest state, and from a hand still moving at the steady speed.
    n_rest = int(round(man["rest_s"] / dt))
    xr, vr = rk4(sag, 0.0, g, k / m, dt, n_rest)
    resid = float(np.max(np.abs(xr - sag)))
    u0 = man["hand_steady_speed_m_s"]
    xs_, vs_ = rk4(sag, u0, g, k / m, dt, n_rest)
    wob = float(np.max(np.abs(xs_ - sag)))
    print(f"lowered: the hand's share of the load is m g - k x - m x'' (the last term is the inertia of the smooth "
          f"profile, at most {100 * inertial.max():.2f} % of the weight); it falls from {100 * frac[0]:.1f} % "
          f"({F[0]:.2f} N) at the free top to {100 * frac[-1]:.1f} % ({F[-1]:.1e} N) at x = {x_h[-1] * 100:.2f} cm "
          f"and never goes negative (minimum {100 * frac.min():.2f} %, so the hand only ever carries, never holds "
          f"down); quasi-static shares {table}; the lift back needs {100 * F_l.min() / (m * g):.1f} to "
          f"{100 * F_l.max() / (m * g):.1f} % of the weight; after the hand lets go at x = {sag * 100:.2f} cm "
          f"with zero speed, RK4 over {man['rest_s']:g} s moves the weight at most {resid * 1000:.1e} mm from the "
          f"sag (no wobble; the sag is the equilibrium); a hand that let go while still moving at {u0 * 100:g} "
          f"cm/s would leave a wobble of u / omega = {u0 / omega * 1000:.2f} mm (RK4 {wob * 1000:.2f} mm)")
    # The dropped panel: RK4 through the scene's worth of bounces against the closed form.
    n_drop = int(round(man["bounces"] * T / dt)) + 1
    xd, vd = rk4(0.0, 0.0, g, k / m, dt, n_drop)
    td = np.arange(n_drop + 1) * dt
    x_closed = sag * (1.0 - np.cos(omega * td))
    v_closed = sag * omega * np.sin(omega * td)
    err_x = float(np.max(np.abs(xd - x_closed)))
    err_v = float(np.max(np.abs(vd - v_closed)))
    first = int(np.argmax(xd[: int(T / dt)]))
    t_bot, x_bot = vertex(xd, first, dt)
    lo = first + int(0.25 * T / dt)
    i_top = lo + int(np.argmin(xd[lo: lo + int(0.5 * T / dt)]))
    t_top, x_top = vertex(xd, i_top, dt)
    cross = int(np.argmax(xd >= sag))
    f_c = (sag - xd[cross - 1]) / (xd[cross] - xd[cross - 1])
    v_cross = vd[cross - 1] + f_c * (vd[cross] - vd[cross - 1])
    t_cross = (cross - 1 + f_c) * dt
    x_max = 2.0 * m * g / k
    bottoms = [vertex(xd, i, dt)[1] for i in range(1, n_drop) if xd[i] >= xd[i - 1] and xd[i] > xd[i + 1]]
    print(f"dropped: let go from rest at the free top; RK4 reaches its deepest squash {x_bot * 100:.4f} cm at "
          f"{t_bot:.4f} s (closed form 2 m g / k = {x_max * 100:.4f} cm at a half period {T / 2:.4f} s; "
          f"{x_bot * 100:.2f} cm, {x_bot / sag:.4f} times the static sag, exactly double), comes back up to "
          f"{x_top * 100:.1e} cm at {t_top:.4f} s (closed form {T:.4f} s; one bounce every {T:.3f} s), passes the "
          f"{sag * 100:g} cm resting point on the way down at {v_cross:.4f} m/s at {t_cross:.4f} s (closed form "
          f"omega x = {omega * sag:.4f} m/s at a quarter period {T / 4:.4f} s); over {man['bounces']} bounces "
          f"({n_drop * dt:.2f} s) RK4 stays within {err_x:.1e} m and {err_v:.1e} m/s of the closed form and the "
          f"{len(bottoms)} bottoms lie between {min(bottoms) * 100:.4f} and {max(bottoms) * 100:.4f} cm; energy: "
          f"m g x_max = {m * g * x_max:.4f} J against k x_max^2 / 2 = {0.5 * k * x_max ** 2:.4f} J; no damping, "
          f"so it bounces between 0 and {x_max * 100:.0f} cm for ever")
    # Drops from above the free top, for the description.
    descr = []
    for h in man["description_drops_m"]:
        x_cf = sag * (1.0 + math.sqrt(1.0 + 2.0 * h / sag))
        n_h = int(round(2.0 / dt))
        xh, vh = rk4(-h, 0.0, g, k / m, dt, n_h, contact_only=True)
        i = int(np.argmax(vh[1:] < 0.0)) + 1          # the first bottom: where the speed first turns upward
        t_h, x_h_max = vertex(xh, i, dt)
        descr.append(f"from {h * 100:g} cm above the spring: deepest {x_h_max * 100:.2f} cm at {t_h:.3f} s "
                     f"(closed form m g (h + x) = k x^2 / 2, x = {x_cf * 100:.2f} cm, diff {abs(x_h_max - x_cf) * 100:.1e} cm)")
    print("for the description (RK4 with the spring pushing only while the weight is on it): " + "; ".join(descr))
    # Schedule in video time.
    la, ba = man["lower_at"], man["bottom_at"]
    c0 = (0.0 - la) % cycle
    lows = [la + j * cycle for j in range(-1, int(cycles) + 1) if 0.0 <= la + j * cycle < D]
    lets = [t + man["lower_s"] for t in lows]
    aways = [t + man["lower_s"] + man["linger_s"] for t in lows]
    lifts = [t + man["lower_s"] + man["rest_s"] for t in lows]
    bots = [ba + j * P_video for j in range(-1, man["bounces"] + 1) if 0.0 <= ba + j * P_video < D]
    if c0 < man["lower_s"]:
        state0 = f"the hand is {c0:.2f} s into a lowering"
    elif c0 < man["lower_s"] + man["linger_s"]:
        state0 = f"the lowered weight rests at {sag * 100:g} cm with the hand still on it carrying nothing"
    elif c0 < man["lower_s"] + man["rest_s"]:
        state0 = (f"the lowered weight rests at {sag * 100:g} cm, {c0 - man['lower_s'] - man['linger_s']:.2f} s "
                  f"after the hand moved away")
    elif c0 < man["lower_s"] + man["rest_s"] + man["lift_s"]:
        state0 = f"the hand is {c0 - man['lower_s'] - man['rest_s']:.2f} s into the lift"
    else:
        state0 = "the hand holds the weight at the top"
    b0 = (0.0 - ba) % P_video
    print(f"schedule (video time): the lowered panel runs in real time on a {cycle:g} s cycle ({cycle * fps:.0f} "
          f"frames): lowering starts at " + ", ".join(f"{t:.1f}" for t in lows) + " s, the hand lets go "
          f"{man['lower_s']:g} s later at " + ", ".join(f"{t:.1f}" for t in lets) + f" s (the weight rests at the "
          f"sag from then on), stays on it carrying nothing for {man['linger_s']:g} s and moves away over "
          f"{man['hand_away_s']:g} s from " + ", ".join(f"{t:.1f}" for t in aways) + f" s, comes back over "
          f"{man['hand_away_s']:g} s and lifts from " + ", ".join(f"{t:.1f}" for t in lifts)
          + f" s, holds at the top for the last {man['top_s']:g} s of the cycle; the dropped panel runs "
          f"{slow:.4f}x slow on a {P_video:g} s cycle ({P_video * fps:.0f} frames): at the top at "
          f"{(ba + P_video / 2) % P_video:g} + {P_video:g} k s, at its deepest at {ba:g} + {P_video:g} k s, i.e. "
          + ", ".join(f"{t:.0f}" for t in bots[:6]) + f", ... s; on the first frame {state0} and the dropped weight is "
          f"{b0:.2f} s of video ({b0 / slow:.3f} s real) past its deepest point; title until {man['title_until']:g} s, "
          f"then the legend, the tags, the live readouts and the fixed lines; payoff card from {man['payoff_t']:g} s; "
          f"the title fades back in over the last {man['loop_fade']:g} s and the last frame repeats the first (the "
          f"scene is periodic: {D:g} s holds exactly {cycles:.0f} lowering cycles and {man['bounces']} bounces)")
    ev = {"k": k, "omega": omega, "T": T, "P_video": P_video, "slow": slow, "cycle": cycle, "sag": sag,
          "x_max": x_max, "x_bot": x_bot, "t_bot": t_bot, "v_cross": v_cross, "table_x": xd[: int(2 * T / dt) + 2],
          "table_v": vd[: int(2 * T / dt) + 2], "dt": dt, "sag2": sag2}
    # Text widths.
    font = os.environ["SEED_ZERO_FONT"]
    f28, f34, f40, f56 = (ImageFont.truetype(font, n) for n in (28, 34, 40, 56))
    widths = {"overlay@34": (f34, man["overlay"])}
    for j, line in enumerate(man["title"].split("|")):
        widths[f"title line {j + 1}@56"] = (f56, line)
    widths["legend@40"] = (f40, legend_text())
    widths["tag@28"] = (f28, tag_text())
    for name in PANELS:
        widths[f"label {name}@40"] = (f40, label_text(name))
        widths[f"tag {name}@28"] = (f28, panel_tag(ev, name))
        for j, line in enumerate(fixed_lines(ev, name)):
            widths[f"fixed {name} line {j + 1}@28"] = (f28, line)
    widths["live hand@28"] = (f28, live_text("lowered", 1.0))
    widths["live speed@28"] = (f28, live_text("dropped", ev["v_cross"]))
    widths["scale@28"] = (f28, "10 cm")
    widths["block@28"] = (f28, block_text(man))
    for j, line in enumerate(payoff_lines(man, ev)):
        widths[f"payoff line {j + 1}@40"] = (f40, line)
    print("text widths: " + ", ".join(f"{k_} {f.getlength(s):.0f} px" for k_, (f, s) in widths.items()))
    assert all(f.getlength(s) < 950 for f, s in widths.values()), "a text line is wider than 950 px"
    panel_keys = [k_ for k_ in widths if k_.split(" ")[0] in ("label", "fixed", "live") or k_.startswith("tag ")]
    assert all(widths[k_][0].getlength(widths[k_][1]) < 470 for k_ in panel_keys), "a panel line is wider than its column"
    return ev


def legend_text() -> str:
    return "same weight, same spring"


def tag_text() -> str:
    return "no friction, no damping, no air"


def label_text(name: str) -> str:
    return "lowered by hand" if name == "lowered" else "let go at the top"


def panel_tag(ev: dict, name: str) -> str:
    return "real time" if name == "lowered" else f"slow motion, {ev['slow']:.2f}x"


def live_text(name: str, value: float) -> str:
    if name == "lowered":
        return f"hand carries {max(0.0, 100.0 * value):.0f} %"
    return f"speed {abs(value):.2f} m/s"


def block_text(man: dict) -> str:
    return f"{man['mass_kg']:g} kg"


def fixed_lines(ev: dict, name: str) -> list[str]:
    if name == "lowered":
        return [f"deepest {ev['sag'] * 100:.2f} cm", "the hand carries 0 % there"]
    return [f"deepest {ev['x_bot'] * 100:.2f} cm", f"exactly double, every {ev['T']:.3f} s"]


def payoff_lines(man: dict, ev: dict) -> list[str]:
    text = man["payoff_text"].format(sag_cm=ev["sag"] * 100, deep_cm=ev["x_bot"] * 100, period=ev["T"])
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
        self.g, self.m, self.sag = man["g_m_s2"], man["mass_kg"], man["static_sag_m"]
        self.k = ev["k"]
        self.cycle_f = int(round(ev["cycle"] * self.fps))
        self.period_f = int(round(ev["P_video"] * self.fps))
        self.lower_at_f = int(round(man["lower_at"] * self.fps))
        self.bottom_at_f = int(round(man["bottom_at"] * self.fps))
        self.top_y = man["base_y"] - man["spring_free_length_m"] * self.ppm
        n = len(ev["table_x"])
        self.table_t = np.arange(n) * ev["dt"]

    # --- state helpers ------------------------------------------------------
    def lowered_state(self, f: int) -> dict:
        """Compression x (m), the hand's share of the load, the hand's lift (px) and alpha at frame f."""
        man, sag = self.man, self.sag
        c = ((f - self.lower_at_f) % self.cycle_f) / self.fps
        ls, rs, fs, aw = man["lower_s"], man["rest_s"], man["lift_s"], man["hand_away_s"]
        if c < ls:
            u = c / ls
            x = sag * smoother(u)
            frac = 1.0 - smoother(u) - sag * smoother_dd(u) / (ls * ls * self.g)
            return {"x": x, "frac": frac, "lift": 0.0, "alpha": 1.0}
        if c < ls + rs:
            u = c - ls
            lg = man["linger_s"]
            if u < lg:
                w = 0.0
            elif u < lg + aw:
                w = (u - lg) / aw
            elif u > rs - aw:
                w = (rs - u) / aw
            else:
                w = 1.0
            return {"x": sag, "frac": 0.0, "lift": man["hand_lift_px"] * smoother(w), "alpha": 1.0 - w}
        if c < ls + rs + fs:
            u = (c - ls - rs) / fs
            x = sag * (1.0 - smoother(u))
            frac = smoother(u) + sag * smoother_dd(u) / (fs * fs * self.g)
            return {"x": x, "frac": frac, "lift": 0.0, "alpha": 1.0}
        return {"x": 0.0, "frac": 1.0, "lift": 0.0, "alpha": 1.0}

    def dropped_state(self, f: int) -> dict:
        """Compression x (m) and speed (m/s) from the RK4 table at frame f (real time, the panel runs slow)."""
        ev = self.ev
        tau = (((f - self.bottom_at_f) % self.period_f) / self.fps) / ev["slow"] + ev["T"] / 2.0
        tau = tau % ev["T"]
        x = float(np.interp(tau, self.table_t, ev["table_x"]))
        v = float(np.interp(tau, self.table_t, ev["table_v"]))
        return {"x": x, "v": v}

    # --- pixel helpers ------------------------------------------------------
    def L(self, x: float, y: float) -> tuple[float, float]:
        # Rounded to 1e-4 px so that a coordinate that is an exact integer at one time and off
        # by 1e-11 a whole number of cycles later draws the same pixel (the periodicity check).
        return round(x * SS, 4), round((y - GEOM_Y0) * SS, 4)

    def draw_spring(self, d: ImageDraw.ImageDraw, cx: float, y0: float, y1: float) -> None:
        """Zigzag coil from the base (y0) up to the block bottom (y1), a fixed number of coils."""
        man = self.man
        lead, amp, coils = 14.0, float(man["coil_half_width_px"]), int(man["coils"])
        pts = [self.L(cx, y0), self.L(cx, y0 - lead)]
        inner = (y0 - lead) - (y1 + lead)
        for i in range(1, 2 * coils):
            s = (y0 - lead) - inner * i / (2 * coils)
            off = amp if i % 2 else -amp
            pts.append(self.L(cx + off, s))
        pts.append(self.L(cx, y1 + lead))
        pts.append(self.L(cx, y1))
        d.line(pts, fill=TEAL, width=5 * SS, joint="curve")

    def draw_panel(self, d: ImageDraw.ImageDraw, name: str, f: int, hud_alpha: float) -> dict:
        man = self.man
        cx = float(man["panel_x"][PANELS.index(name)])
        base = float(man["base_y"])
        bw, bh = man["block_width_m"] * self.ppm / 2.0, man["block_height_m"] * self.ppm
        st = self.lowered_state(f) if name == "lowered" else self.dropped_state(f)
        yb = self.top_y + st["x"] * self.ppm          # block bottom = spring top
        # The base plate and its hatching.
        x0, y0 = self.L(cx - 150, base)
        x1, _ = self.L(cx + 150, base)
        d.line((x0, y0, x1, y0), fill=RIM, width=5 * SS)
        for j in range(9):
            hx = cx - 140 + 35 * j
            p0, p1 = self.L(hx, base + 3), self.L(hx - 14, base + 17)
            d.line((*p0, *p1), fill=blend(RIM, 0.7), width=2 * SS)
        # The centimetre scale right of the spring, with the deepest-point marker.
        sx = cx + 158
        s0, s1 = self.L(sx, self.top_y - 12), self.L(sx, self.top_y + 0.12 * self.ppm)
        d.line((*s0, *s1), fill=RIM, width=2 * SS)
        for c in range(13):
            yy = self.top_y + c / 100.0 * self.ppm
            ln = 16 if c % 5 == 0 else 8
            p0, p1 = self.L(sx, yy), self.L(sx + ln, yy)
            d.line((*p0, *p1), fill=RIM, width=(3 if c % 5 == 0 else 2) * SS)
        deep = self.sag if name == "lowered" else self.ev["x_bot"]
        yd = self.top_y + deep * self.ppm
        if hud_alpha > 0.02:
            col = blend(GOLD, 0.9 * hud_alpha)
            tip = self.L(sx - 3, yd)
            a1, a2 = self.L(sx - 21, yd - 11), self.L(sx - 21, yd + 11)
            d.polygon([tip, a1, a2], fill=col)
            for j in range(0, 260, 20):
                p0, p1 = self.L(cx - 130 + j, yd), self.L(cx - 130 + j + 10, yd)
                d.line((*p0, *p1), fill=blend(GOLD, 0.6 * hud_alpha), width=2 * SS)
        # The spring and the block.
        self.draw_spring(d, cx, base, yb)
        bx0, by0 = self.L(cx - bw, yb - bh)
        bx1, by1 = self.L(cx + bw, yb)
        d.rounded_rectangle((bx0, by0, bx1, by1), radius=8 * SS, fill=BLOCK)
        # The hand: a bracket over the block with a stem, lifted and faded while it is away.
        if name == "lowered" and st["alpha"] > 0.02:
            col = blend(CORAL, st["alpha"])
            yt = yb - bh - st["lift"]
            hx0, hy0 = self.L(cx - bw - 10, yt - 34)
            hx1, hy1 = self.L(cx + bw + 10, yt - 14)
            d.rectangle((hx0, hy0, hx1, hy1), fill=col)
            for sgn in (-1, 1):
                fx0, fy0 = self.L(cx + sgn * (bw + 10) - (10 if sgn > 0 else 8), yt - 14)
                fx1, fy1 = self.L(cx + sgn * (bw + 10) + (8 if sgn > 0 else 10), yt + 60)
                d.rectangle((min(fx0, fx1), fy0, max(fx0, fx1), fy1), fill=col)
            sx0, sy0 = self.L(cx - 10, yt - 90)
            sx1, sy1 = self.L(cx + 10, yt - 34)
            d.rectangle((sx0, sy0, sx1, sy1), fill=col)
        return {"x": st["x"], "yb": yb, "cx": cx, "live": st["frac"] if name == "lowered" else st["v"]}

    def draw_text(self, d: ImageDraw.ImageDraw, states: dict, hud_alpha: float) -> None:
        man, ev = self.man, self.ev
        for name, st in states.items():
            cx = st["cx"]
            lx = cx - 185
            d.text((lx, LABEL_Y), label_text(name), font=self.font, fill=TEXT, anchor="lm")
            d.text((cx, st["yb"] - man["block_height_m"] * self.ppm / 2.0), block_text(man), font=self.font_small,
                   fill=BG, anchor="mm")
            for c, s in ((0, "0"), (5, "5"), (10, "10 cm")):
                d.text((cx + 158 + 24, self.top_y + c / 100.0 * self.ppm), s, font=self.font_small, fill=MUTED, anchor="lm")
            if hud_alpha > 0.02:
                d.text((lx, PTAG_Y), panel_tag(ev, name), font=self.font_small, fill=blend(MUTED, hud_alpha), anchor="lm")
                d.text((lx, LIVE_Y), live_text(name, st["live"]), font=self.font_small, fill=blend(TEXT, hud_alpha), anchor="lm")
                for j, line in enumerate(fixed_lines(ev, name)):
                    col = GOLD if j == 0 else MUTED
                    d.text((lx, FIX_Y + 34 * j), line, font=self.font_small, fill=blend(col, hud_alpha), anchor="lm")
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
        states = {name: self.draw_panel(ld, name, f, hud_alpha) for name in PANELS}
        img.paste(layer.reduce(SS), (0, GEOM_Y0))
        d = ImageDraw.Draw(img)
        self.draw_text(d, states, hud_alpha)
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
    man = json.loads((ROOT / "projects/springdrop/manifest.json").read_text())
    ev = measure(man)
    if "--measure-only" in sys.argv:
        return
    if "--frames" in sys.argv:
        times = [float(v) for v in sys.argv[sys.argv.index("--frames") + 1].split(",")]
        r = Renderer(man, ev)
        (ROOT / "media/springdrop").mkdir(parents=True, exist_ok=True)
        for tv in times:
            Image.fromarray(r.frame_at(int(round(tv * man["fps"])))).save(ROOT / f"media/springdrop/smoke-{tv}.png")
        print("smoke frames: " + ", ".join(f"{tv}" for tv in times))
        return
    Renderer(man, ev).render(ROOT / "media/springdrop/footage.mp4")


if __name__ == "__main__":
    main()
