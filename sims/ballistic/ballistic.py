#!/usr/bin/env python3
"""Ballistic pendulum: sticky ball or bouncy ball, which block swings higher?

A ball of mass m at speed u hits a block of mass M that hangs at rest at
the bottom of a light string of length L. The hit is horizontal through
the block's centre and instantaneous (momentum conserved across it). Two
panels with the same masses, the same speed and the same string; only
the ball differs. Top: a sticky ball (perfectly inelastic hit) stays in
the block and the pair swings up together at v = m u / (M + m). Bottom:
a bouncy ball (perfectly elastic hit) comes back at (m - M) u / (M + m)
and the block swings up alone at v = 2 m u / (M + m). After the hit the
swinging mass is a point mass on a taut string,

    theta'' = -(g / L) sin theta,   theta(0) = 0,  omega(0) = v / L,

integrated with RK4 at a fixed step; the peak (omega = 0) and the return
to the bottom (theta = 0) are interpolated inside the step. No air, no
losses. The peak height is checked against h = v^2 / 2 g and the peak
angle against cos theta = 1 - h / L; the string tension g cos theta +
L omega^2 (in units of the swinging weight) is printed and must stay
positive, which holds while the block stays under 90 degrees. Played at
quarter speed; each shot fires the ball, the block rises, falls back, is
caught at the bottom, held, and reset just before the next fire, so the
video loops on the shot rather than on the swing (the two swing periods
differ). The first shot fires at fire_at_first (motion in the first
second); later shots fire at fire_at into their period so that a peak
lands on the words that name it. Deterministic, no seed.

Measured and printed: the block speed after each hit and the ball's
speed after the bounce (momentum and energy before and after), the
energy kept by each block, the RK4 peak height, peak angle and peak
time against the closed forms and the elliptic quarter period, the
return time, the height ratio, the tension at the bottom and its
minimum over the swing, the energy drift, a half-step check, the same
ratio at two other mass ratios for the description, the schedule in
video time and the on-screen text widths.

usage: ballistic.py [--measure-only] [--frames t1,t2,...]
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
WHITE = (236, 240, 244)
WIRE = (104, 116, 132)
WOOD = (178, 150, 116)
WOOD_DARK = (110, 90, 68)

# Layout: overlay at y 96..130 (captions.py), title rows at y 190/252 for
# the first seconds, then the shot counter at y 236 and the model tag at
# y 290; two panels of 543 px from y 350 (top: the sticky ball, bottom:
# the bouncy ball). In each panel the pivot sits at x 500, 70 px under
# the panel top, with a 400 px string (1 m at 400 px per metre), so the
# block hangs at rest 470 px under the panel top and swings to the right,
# up to x 878 and 270 px above its rest level; the ball flies in from a
# launcher at the left edge along the rest level; the readouts live in
# the left column x 40..340 above the ball's path; the height marks (0,
# the two measured peaks) are dashed lines from x 540 to 930 with their
# labels from x 946. Captions at caption_y 0.75 (y 1440..1520), the
# payoff card under them from y 1592.
COUNTER_Y, TAG_Y = 236, 290
GEOM_Y0, GEOM_Y1 = 350, 1436
PANEL_H = (GEOM_Y1 - GEOM_Y0) // 2
PIVOT_X = 500.0
PIVOT_DY = 70.0
COL_X = 40
MARK_X0, MARK_X1 = 540.0, 930.0
MARK_LABEL_X = 946
SS = 2
PAYOFF_Y = 1592.0
BLOCK_W, BLOCK_H = 56.0, 48.0   # drawn size, tangential x radial (not to scale)
BALL_R = 11.0                   # drawn radius (not to scale)
LAUNCHER_W, LAUNCHER_H = 84.0, 36.0
PANELS = {
    "stick": {"index": 0, "colour": TEAL, "label": "sticky ball", "sub": "sticks in the block"},
    "bounce": {"index": 1, "colour": GOLD, "label": "bouncy ball", "sub": "bounces off the block"},
}


def blend(col, a: float, base=BG) -> tuple:
    a = max(0.0, min(1.0, a))
    return tuple(int(round(c * a + b * (1 - a))) for c, b in zip(col, base))


def smoothstep(u: float) -> float:
    u = max(0.0, min(1.0, u))
    return u * u * (3 - 2 * u)


def ellipk(k: float) -> float:
    """Complete elliptic integral of the first kind K(k) by the arithmetic-geometric mean."""
    a, b = 1.0, math.sqrt(1.0 - k * k)
    for _ in range(60):
        if abs(a - b) < 1e-17:
            break
        a, b = 0.5 * (a + b), math.sqrt(a * b)
    return math.pi / (2.0 * a)


# --- the hit ------------------------------------------------------------------
def hit(m: float, u: float, M: float, kind: str) -> dict:
    """Block speed, ball speed and swinging mass after an instantaneous horizontal hit on a block at rest."""
    if kind == "stick":
        v = m * u / (M + m)
        return {"v": v, "ball": v, "mass": M + m}
    v = 2.0 * m * u / (M + m)
    return {"v": v, "ball": (m - M) * u / (M + m), "mass": M}


# --- the swing ----------------------------------------------------------------
def swing(g: float, L: float, v0: float, dt: float, t_max: float) -> dict:
    """RK4 on (theta, omega) from theta = 0, omega = v0 / L; the peak and the return interpolated in the step."""
    n = int(round(t_max / dt))
    theta = np.empty(n + 1)
    omega = np.empty(n + 1)
    k = g / L
    th, w = 0.0, v0 / L
    sin = math.sin
    for i in range(n + 1):
        theta[i], omega[i] = th, w
        if i == n:
            break
        k1t, k1w = w, -k * sin(th)
        k2t, k2w = w + 0.5 * dt * k1w, -k * sin(th + 0.5 * dt * k1t)
        k3t, k3w = w + 0.5 * dt * k2w, -k * sin(th + 0.5 * dt * k2t)
        k4t, k4w = w + dt * k3w, -k * sin(th + dt * k3t)
        th += dt / 6.0 * (k1t + 2 * k2t + 2 * k3t + k4t)
        w += dt / 6.0 * (k1w + 2 * k2w + 2 * k3w + k4w)
    t = np.arange(n + 1) * dt
    i_pk = int(np.nonzero((omega[:-1] > 0.0) & (omega[1:] <= 0.0))[0][0])
    f = omega[i_pk] / (omega[i_pk] - omega[i_pk + 1])
    t_peak = t[i_pk] + f * dt
    th_peak = theta[i_pk] + f * (theta[i_pk + 1] - theta[i_pk])
    i_rt = np.nonzero((theta[:-1] > 0.0) & (theta[1:] <= 0.0))[0]
    i_rt = int(i_rt[i_rt > i_pk][0])
    f = theta[i_rt] / (theta[i_rt] - theta[i_rt + 1])
    t_ret = t[i_rt] + f * dt
    v_ret = L * (omega[i_rt] + f * (omega[i_rt + 1] - omega[i_rt]))
    e = 0.5 * L * L * omega * omega - g * L * np.cos(theta)
    e0 = 0.5 * v0 * v0 - g * L
    drift = float(np.abs(e - e0).max() / (0.5 * v0 * v0))
    tension = np.cos(theta[: i_rt + 1]) + L * omega[: i_rt + 1] ** 2 / g
    return {"t": t, "theta": theta, "omega": omega, "dt": dt, "t_peak": t_peak, "th_peak": th_peak,
            "h_peak": L * (1.0 - math.cos(th_peak)), "th_max_grid": float(theta.max()), "t_ret": t_ret,
            "v_ret": v_ret, "drift": drift, "tension_min": float(tension.min()), "tension_bottom": float(tension[0])}


# --- measurement --------------------------------------------------------------
def measure(man: dict) -> dict:
    g, L = man["g"], man["string_length_m"]
    m, u, M = man["ball_mass_kg"], man["ball_speed_m_s"], man["block_mass_kg"]
    steps, pb, fps, P = man["steps_per_second"], man["playback"], man["fps"], man["shot_period"]
    dt = 1.0 / steps
    ppm = man["px_per_m"]
    print(f"setup: a {m * 1000:g} g ball at {u:g} m/s hits a {M * 1000:g} g block hanging at rest at the bottom of a "
          f"{L:g} m light string, horizontally through the block's centre, in an instant (momentum conserved across the "
          f"hit); top panel: a sticky ball (perfectly inelastic hit) stays in the block and the pair swings together; "
          f"bottom panel: a bouncy ball (perfectly elastic hit) comes back and the block swings alone; after the hit the "
          f"swinging mass is a point mass on a taut string, theta'' = -(g / L) sin theta, g = {g}, RK4 at {steps} steps "
          f"per second (dt = {dt:.0e} s) from theta = 0, omega = v / L; no air, no losses; played at {pb:g} speed, "
          f"{man['shots']} shots of {P:g} s; the string drawn at {ppm:g} px per metre ({L * ppm:.0f} px), the ball and "
          f"the block drawn larger than scale; deterministic, no seed")
    p0, e0 = m * u, 0.5 * m * u * u
    runs = {}
    for kind in PANELS:
        hk = hit(m, u, M, kind)
        run = swing(g, L, hk["v"], dt, man["sim_t_max_s"])
        run.update(hk)
        run["p_after"] = M * hk["v"] + m * hk["ball"] if kind == "bounce" else (M + m) * hk["v"]
        run["e_block"] = 0.5 * hk["mass"] * hk["v"] ** 2
        run["e_ball"] = 0.5 * m * hk["ball"] ** 2 if kind == "bounce" else 0.0
        run["h_closed"] = hk["v"] ** 2 / (2.0 * g)
        run["th_closed"] = math.acos(1.0 - run["h_closed"] / L)
        kk = math.sin(0.5 * run["th_closed"])
        run["T_closed"] = 4.0 * math.sqrt(L / g) * ellipk(kk)
        runs[kind] = run
    S, B = runs["stick"], runs["bounce"]
    print(f"the hit: momentum before {p0:.4f} kg m/s, energy before {e0:.4f} J; sticky ball: the pair "
          f"({(M + m) * 1000:g} g) leaves at v = m u / (M + m) = {S['v']:.4f} m/s (momentum after {S['p_after']:.4f}), "
          f"energy after {S['e_block']:.4f} J, {100 * S['e_block'] / e0:.2f} percent kept; bouncy ball: the block leaves "
          f"at v = 2 m u / (M + m) = {B['v']:.4f} m/s and the ball comes back at (m - M) u / (M + m) = {B['ball']:.4f} "
          f"m/s (momentum after {B['p_after']:.4f}), the block carries {B['e_block']:.4f} J ({100 * B['e_block'] / e0:.2f} "
          f"percent) and the ball keeps {B['e_ball']:.4f} J ({100 * B['e_ball'] / e0:.2f} percent), total "
          f"{B['e_block'] + B['e_ball']:.4f} J; the bounce gives the block {B['v'] / S['v']:.4f} times the speed of the "
          f"stuck pair; impulse on the block {M * B['v']:.4f} N s against {M * S['v']:.4f} N s for the block inside the "
          f"pair ({S['p_after']:.4f} N s for the pair)")
    for kind, run in runs.items():
        print(f"{kind}: RK4 swing from {run['v']:.4f} m/s peaks at h = {run['h_peak'] * 100:.4f} cm (closed form v^2 / 2 g "
              f"= {run['h_closed'] * 100:.4f} cm, diff {abs(run['h_peak'] - run['h_closed']) * 100:.1e} cm; shown as "
              f"{run['h_peak'] * 100:.0f} cm), {math.degrees(run['th_peak']):.4f} degrees (closed form acos(1 - h / L) = "
              f"{math.degrees(run['th_closed']):.4f}; the largest grid angle {math.degrees(run['th_max_grid']):.4f}), at "
              f"t = {run['t_peak']:.4f} s after the hit (elliptic quarter period sqrt(L / g) K(sin(theta / 2)) = "
              f"{run['T_closed'] / 4:.4f} s, full period {run['T_closed']:.4f} s); back at the bottom at {run['t_ret']:.4f} s "
              f"(half period {run['T_closed'] / 2:.4f}) at {run['v_ret']:.4f} m/s; string tension at the bottom "
              f"{run['tension_bottom']:.4f} of the swinging weight = {run['mass'] * g * run['tension_bottom']:.4f} N, "
              f"minimum over the swing {run['tension_min']:.4f} of the weight (at the peak, cos theta = "
              f"{math.cos(run['th_peak']):.4f}), so the string stays taut; energy drift {run['drift']:.1e}")
        assert run["th_peak"] < 0.5 * math.pi and run["tension_min"] > 0.0, "the string goes slack"
    ratio = B["h_peak"] / S["h_peak"]
    print(f"ratio: the bouncy block rises {ratio:.4f} times as high as the stuck pair ({B['h_peak'] * 100:.4f} / "
          f"{S['h_peak'] * 100:.4f} cm; closed form (2 m / (M + m))^2 / (m / (M + m))^2 = 4 at every mass ratio); the "
          f"angles are not in that ratio ({math.degrees(B['th_peak']):.2f} against {math.degrees(S['th_peak']):.2f} "
          f"degrees, {math.degrees(B['th_peak']) / math.degrees(S['th_peak']):.3f} times)")
    for kind, run in runs.items():
        half = swing(g, L, run["v"], dt / 2, man["sim_t_max_s"])
        print(f"check at half the time step ({2 * steps} steps per second), {kind}: peak {half['h_peak'] * 100:.6f} cm "
              f"({(half['h_peak'] - run['h_peak']) * 100:+.1e}), {math.degrees(half['th_peak']):.6f} degrees at "
              f"{half['t_peak']:.6f} s ({half['t_peak'] - run['t_peak']:+.1e}), return at {half['t_ret']:.6f} s "
              f"({half['t_ret'] - run['t_ret']:+.1e}), energy drift {half['drift']:.1e}")
    others = []
    for m2, u2, M2 in man["other_cases"]:
        hs, hb = hit(m2, u2, M2, "stick"), hit(m2, u2, M2, "bounce")
        h1, h2 = hs["v"] ** 2 / (2 * g), hb["v"] ** 2 / (2 * g)
        others.append(f"{m2 * 1000:g} g at {u2:g} m/s into {M2 * 1000:g} g: {h1 * 100:.2f} against {h2 * 100:.2f} cm "
                      f"({math.degrees(math.acos(1 - h1 / L)):.1f} against {math.degrees(math.acos(1 - h2 / L)):.1f} "
                      f"degrees on a {L:g} m string), ratio {h2 / h1:.4f}")
    print("for the description, the same two hits at other mass ratios (closed form): " + "; ".join(others))
    # Schedule in video time.
    x_start_m = (man["ball_start_px"] - PIVOT_X) / ppm
    x_contact_m = -(BLOCK_W / 2 + BALL_R) / ppm
    approach = (x_contact_m - x_start_m) / u / pb
    n = man["shots"]
    fires = [man["fire_at_first"]] + [k * P + man["fire_at"] for k in range(1, n)]
    ends = fires[1:] + [n * P]
    assert man["rest_dur"] >= man["loop_fade"], "the loop fade must play over a scene at rest"
    assert abs(n * P - man["scene_duration"]) < 1e-9
    gone = (x_contact_m * ppm + PIVOT_X + BALL_R) / (-B["ball"] * pb * ppm)
    print(f"schedule (video time, {pb:g} speed, {n} shots of {P:g} s): the first shot fires the ball at "
          f"{man['fire_at_first']:g} s and the later shots at {man['fire_at']:g} s into their period, from x = "
          f"{x_start_m:.4f} m ({man['ball_start_px']:g} px, inside the launcher), {x_contact_m - x_start_m:.4f} m of approach "
          f"in {approach:.4f} s; after each hit the stuck pair peaks {S['t_peak'] / pb:.4f} s later and is caught at the "
          f"bottom {S['t_ret'] / pb:.4f} s later, the bouncy block peaks {B['t_peak'] / pb:.4f} s later and is caught "
          f"{B['t_ret'] / pb:.4f} s later, the bouncy ball leaves the frame {gone:.2f} s later; the readouts and the "
          f"trace hold until {man['reset_dur'] + man['rest_dur']:g} s before the next fire (a {man['reset_dur']:g} s reset, "
          f"then {man['rest_dur']:g} s at rest); title until {man['title_until']:g} s; payoff card from "
          f"{man['payoff_t']:g} s; loop fade {man['scene_duration'] - man['loop_fade']:.1f} to {man['scene_duration']:g} s")
    rows = []
    for k, (f0, f1) in enumerate(zip(fires, ends)):
        hit_at = f0 + approach
        reset_start = f1 - man["reset_dur"] - man["rest_dur"]
        hold = reset_start - (hit_at + B["t_ret"] / pb)
        assert hold > 0.0, f"shot {k + 1}: the reset starts before the bouncy block is caught"
        rows.append(f"shot {k + 1}: fire {f0:.2f}, hit {hit_at:.2f}, peaks {hit_at + S['t_peak'] / pb:.2f}/"
                    f"{hit_at + B['t_peak'] / pb:.2f}, catches {hit_at + S['t_ret'] / pb:.2f}/{hit_at + B['t_ret'] / pb:.2f}, "
                    f"hold {hold:.2f} s, reset {reset_start:.2f}, rest {f1 - man['rest_dur']:.2f} to {f1:.2f} s")
    print("shots (video time, stick/bounce): " + "; ".join(rows))
    ev = {"runs": runs, "ratio": ratio, "approach": approach, "fires": fires, "ends": ends,
          "x_start_m": x_start_m, "x_contact_m": x_contact_m}
    # Text widths.
    font = os.environ["SEED_ZERO_FONT"]
    f28, f34, f40, f56, f64 = (ImageFont.truetype(font, n) for n in (28, 34, 40, 56, 64))
    widths = {"overlay@34": (f34, man["overlay"])}
    for j, line in enumerate(man["title"].split("|")):
        widths[f"title line {j + 1}@56"] = (f56, line)
    widths["counter@40"] = (f40, f"shot {man['shots']} of {man['shots']}")
    widths["tag@28"] = (f28, model_tag(man))
    for kind, p in PANELS.items():
        widths[f"label {kind}@40"] = (f40, p["label"])
        widths[f"sublabel {kind}@28"] = (f28, p["sub"])
    widths["speed label@28"] = (f28, "speed after the hit")
    widths["speed@40"] = (f40, speed_text(B["v"]))
    widths["rise label@28"] = (f28, "rise")
    widths["peak label@28"] = (f28, "peak")
    widths["rise@64"] = (f64, rise_text(B["h_peak"]))
    widths["mark 0@28"] = (f28, "0")
    for kind in PANELS:
        widths[f"mark {kind}@28"] = (f28, rise_text(runs[kind]["h_peak"]))
    for j, line in enumerate(payoff_lines(man, ev)):
        widths[f"payoff line {j + 1}@40"] = (f40, line)
    print("text widths: " + ", ".join(f"{k} {f.getlength(s):.0f} px" for k, (f, s) in widths.items())
          + f"; left column budget {int(PIVOT_X - BLOCK_W / 2 - BALL_R - 20 - COL_X)} px")
    return ev


def model_tag(man: dict) -> str:
    return f"point mass on a {man['string_length_m']:g} m string, instant hit, no losses"


def speed_text(v: float) -> str:
    return f"{v:.2f} m/s"


def rise_text(h: float) -> str:
    return f"{h * 100:.0f} cm"


def payoff_lines(man: dict, ev: dict) -> list[str]:
    text = man["payoff_text"].format(h_stick=ev["runs"]["stick"]["h_peak"] * 100,
                                     h_bounce=ev["runs"]["bounce"]["h_peak"] * 100, ratio=ev["ratio"])
    return [s.strip() for s in text.split("|")]


# --- rendering ---------------------------------------------------------------
class Renderer:
    def __init__(self, man: dict, ev: dict):
        self.man, self.ev = man, ev
        self.runs = ev["runs"]
        self.fps = man["fps"]
        font = os.environ["SEED_ZERO_FONT"]
        self.font = ImageFont.truetype(font, 40)
        self.font_title = ImageFont.truetype(font, 56)
        self.font_small = ImageFont.truetype(font, 28)
        self.font_num = ImageFont.truetype(font, 64)
        self.ppm = float(man["px_per_m"])
        self.R = man["string_length_m"] * self.ppm
        self.total = int(round(man["scene_duration"] * self.fps))
        self.first = None

    # --- state --------------------------------------------------------------
    def pivot(self, name: str) -> tuple[float, float]:
        return PIVOT_X, GEOM_Y0 + PANELS[name]["index"] * PANEL_H + PIVOT_DY

    def shot_state(self, t: float) -> tuple[int, float, float, float]:
        """Video time -> (shot index, that shot's fire time, physics time since its hit, reset fraction)."""
        man, fires = self.man, self.ev["fires"]
        k = max(0, sum(1 for f in fires if f <= t) - 1)
        fire = fires[k]
        rs = self.ev["ends"][k] - man["reset_dur"] - man["rest_dur"]
        u = smoothstep((t - rs) / man["reset_dur"]) if t >= rs else 0.0
        tp = (t - fire - self.ev["approach"]) * man["playback"]
        return k, fire, tp, u

    def panel_state(self, name: str, t: float, fire: float, tp: float) -> dict:
        man, run = self.man, self.runs[name]
        if tp < 0.0:
            theta, phase = 0.0, "before"
        elif tp < run["t_ret"]:
            theta, phase = float(np.interp(tp, run["t"], run["theta"])), "swing"
        else:
            theta, phase = 0.0, "caught"
        if tp < 0.0:
            trace, h, frozen = None, 0.0, False
        elif tp < run["t_peak"]:
            trace, h, frozen = theta, man["string_length_m"] * (1.0 - math.cos(theta)), False
        else:
            trace, h, frozen = run["th_peak"], run["h_peak"], True
        # The ball: in the launcher, flying in, stuck, flying back, or gone.
        if t < fire:
            ball = ("launcher", self.ev["x_start_m"])
        elif tp < 0.0:
            ball = ("in", self.ev["x_start_m"] + man["ball_speed_m_s"] * (t - fire) * man["playback"])
        elif name == "stick":
            ball = ("stuck", 0.0)
        else:
            x = self.ev["x_contact_m"] + run["ball"] * tp
            ball = ("out", x) if x * self.ppm + PIVOT_X > -BALL_R - 400 else ("gone", x)
        return {"theta": theta, "phase": phase, "trace": trace, "h": h, "frozen": frozen, "ball": ball, "tp": tp}

    # --- drawing ------------------------------------------------------------
    @staticmethod
    def dashed(d: ImageDraw.ImageDraw, p0, p1, fill, width: int, dash: float, gap: float) -> None:
        (x0, y0), (x1, y1) = p0, p1
        seg = math.hypot(x1 - x0, y1 - y0)
        if seg < 1e-9:
            return
        ux, uy = (x1 - x0) / seg, (y1 - y0) / seg
        pos = 0.0
        while pos < seg:
            run = min(dash, seg - pos)
            d.line((x0 + ux * pos, y0 + uy * pos, x0 + ux * (pos + run), y0 + uy * (pos + run)), fill=fill, width=width)
            pos += dash + gap

    def draw_ball(self, d: ImageDraw.ImageDraw, X: float, Y: float, col, a: float = 1.0, scale: float = 1.0) -> None:
        r = BALL_R * SS * scale
        d.ellipse((X - r, Y - r, X + r, Y + r), fill=blend(col, a), outline=blend(blend(col, 0.5), a), width=SS)
        hr = r * 0.3
        d.ellipse((X - r * 0.4 - hr, Y - r * 0.4 - hr, X - r * 0.4 + hr, Y - r * 0.4 + hr), fill=blend(WHITE, a * 0.9))

    def draw_panel(self, d: ImageDraw.ImageDraw, name: str, st: dict, t: float, fire: float, u: float) -> None:
        man, run = self.man, self.runs[name]
        col = PANELS[name]["colour"]
        px, py = self.pivot(name)
        R = self.R
        y_rest = py + R

        def P(x: float, y: float) -> tuple[float, float]:
            return x * SS, (y - GEOM_Y0) * SS

        # Plumb line and the height marks: the rest level and both measured peaks.
        self.dashed(d, P(px, py), P(px, y_rest - BLOCK_H / 2 - 4), blend(MUTED, 0.35), 2 * SS, 10 * SS, 10 * SS)
        for h in (0.0, self.runs["stick"]["h_peak"], self.runs["bounce"]["h_peak"]):
            yy = y_rest - h * self.ppm
            self.dashed(d, P(MARK_X0, yy), P(MARK_X1, yy), blend(MUTED, 0.5), 2 * SS, 10 * SS, 8 * SS)
        # Launcher at the left edge on the rest level.
        lx0, ly0 = P(0.0, y_rest - LAUNCHER_H / 2)
        lx1, ly1 = P(LAUNCHER_W, y_rest + LAUNCHER_H / 2)
        d.rounded_rectangle((lx0 - 10 * SS, ly0, lx1, ly1), radius=8 * SS, fill=blend(WIRE, 0.35), outline=WIRE, width=2 * SS)
        # Trace arc from the bottom up to the highest angle reached in this shot, with a tick at the peak.
        a_tr = 1.0 - u
        if st["trace"] is not None and a_tr > 0.0:
            cx, cy = P(px, py)
            Rp = R * SS
            deg = math.degrees(st["trace"])
            if deg > 0.05:
                d.arc((cx - Rp, cy - Rp, cx + Rp, cy + Rp), start=90 - deg, end=90, fill=blend(col, 0.55 * a_tr), width=4 * SS)
            if st["frozen"]:
                th = run["th_peak"]
                ex, ey = px + R * math.sin(th), py + R * math.cos(th)
                ux, uy = math.sin(th), math.cos(th)
                d.line((P(ex - ux * 34, ey - uy * 34), P(ex + ux * 34, ey + uy * 34)), fill=blend(col, 0.9 * a_tr), width=4 * SS)
        # String, pivot mount, block (with the stuck ball).
        th = st["theta"]
        bx, by = px + R * math.sin(th), py + R * math.cos(th)
        tx, ty = math.cos(th), -math.sin(th)      # tangent, to the right at rest
        rx, ry = math.sin(th), math.cos(th)       # down the string
        top_c = (bx - rx * BLOCK_H / 2, by - ry * BLOCK_H / 2)
        d.line((P(px, py), P(*top_c)), fill=WIRE, width=3 * SS)
        d.line((P(px - 30, py - 9), P(px + 30, py - 9)), fill=WIRE, width=5 * SS)
        cx, cy = P(px, py)
        pr = 6 * SS
        d.ellipse((cx - pr, cy - pr, cx + pr, cy + pr), fill=BG, outline=TEXT, width=2 * SS)
        corners = []
        for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            corners.append(P(bx + tx * sx * BLOCK_W / 2 + rx * sy * BLOCK_H / 2, by + ty * sx * BLOCK_W / 2 + ry * sy * BLOCK_H / 2))
        d.polygon(corners, fill=WOOD, outline=WOOD_DARK, width=2 * SS)
        # Clamp when caught (fades in after the catch, out over the reset).
        if st["phase"] == "caught":
            a_cl = min(1.0, (st["tp"] - run["t_ret"]) / man["playback"] / 0.15) * (1.0 - u)
            if a_cl > 0.02:
                for sx in (-1.0, 1.0):
                    xx = px + sx * (BLOCK_W / 2 + 10)
                    d.line((P(xx, y_rest - 30), P(xx, y_rest + 30)), fill=blend(MUTED, a_cl), width=5 * SS)
                    d.line((P(xx, y_rest - 30), P(xx - sx * 10, y_rest - 30)), fill=blend(MUTED, a_cl), width=5 * SS)
                    d.line((P(xx, y_rest + 30), P(xx - sx * 10, y_rest + 30)), fill=blend(MUTED, a_cl), width=5 * SS)
        # The ball.
        kind, x = st["ball"]
        trail = int(round(man["trail_seconds"] * self.fps))
        if kind == "launcher":
            self.draw_ball(d, *P(man["ball_start_px"], y_rest), col)
        elif kind == "in":
            for back in range(trail, 0, -1):
                tb = t - back / self.fps
                if tb < fire:
                    continue
                xb = self.ev["x_start_m"] + man["ball_speed_m_s"] * (tb - fire) * man["playback"]
                fade = 1.0 - back / (trail + 1)
                self.draw_ball(d, *P(PIVOT_X + xb * self.ppm, y_rest), col, 0.35 * fade, 0.5 + 0.5 * fade)
            self.draw_ball(d, *P(PIVOT_X + x * self.ppm, y_rest), col)
        elif kind == "stuck":
            a_b = 1.0 - u
            if a_b > 0.02:
                sx, sy = bx - tx * (BLOCK_W / 2 + BALL_R * 0.45), by - ty * (BLOCK_W / 2 + BALL_R * 0.45)
                self.draw_ball(d, *P(sx, sy), col, a_b)
        elif kind == "out":
            for back in range(trail, 0, -1):
                tpb = st["tp"] - back / self.fps * man["playback"]
                if tpb < 0.0:
                    continue
                xb = self.ev["x_contact_m"] + run["ball"] * tpb
                fade = 1.0 - back / (trail + 1)
                self.draw_ball(d, *P(PIVOT_X + xb * self.ppm, y_rest), col, 0.35 * fade, 0.5 + 0.5 * fade)
            self.draw_ball(d, *P(PIVOT_X + x * self.ppm, y_rest), col)
        if u > 0.0 and kind != "launcher":
            self.draw_ball(d, *P(man["ball_start_px"], y_rest), col, u)
        # Flashes: the muzzle at the fire, the hit at the contact point, the catch at the bottom.
        dtf = t - fire
        if 0.0 <= dtf < 0.2:
            a = dtf / 0.2
            fx, fy = P(LAUNCHER_W, y_rest)
            rr = (8 + 30 * a) * SS
            d.ellipse((fx - rr, fy - rr, fx + rr, fy + rr), outline=blend(WHITE, 0.8 * (1 - a)), width=3 * SS)
        dth = t - fire - self.ev["approach"]
        if 0.0 <= dth < 0.35:
            a = dth / 0.35
            fx, fy = P(PIVOT_X + self.ev["x_contact_m"] * self.ppm, y_rest)
            rr = (BALL_R + 4 + 60 * a) * SS
            d.ellipse((fx - rr, fy - rr, fx + rr, fy + rr), outline=blend(WHITE, 1.0 - a), width=4 * SS)
        dtc = (st["tp"] - run["t_ret"]) / man["playback"]
        if st["phase"] == "caught" and 0.0 <= dtc < 0.4:
            a = dtc / 0.4
            fx, fy = P(px, y_rest)
            rr = (BLOCK_W / 2 + 6 + 40 * a) * SS
            d.ellipse((fx - rr, fy - rr, fx + rr, fy + rr), outline=blend(WHITE, 0.7 * (1 - a)), width=3 * SS)

    def draw_geometry(self, t: float) -> tuple[Image.Image, dict]:
        k, fire, tp, u = self.shot_state(t)
        states = {name: self.panel_state(name, t, fire, tp) for name in PANELS}
        img = Image.new("RGB", (W, H), BG)
        layer = Image.new("RGB", (W * SS, (GEOM_Y1 - GEOM_Y0) * SS), BG)
        ld = ImageDraw.Draw(layer)
        for name in PANELS:
            self.draw_panel(ld, name, states[name], t, fire, u)
        img.paste(layer.reduce(SS), (0, GEOM_Y0))
        return img, {"k": k, "fire": fire, "tp": tp, "u": u, "states": states}

    def draw_hud(self, img: Image.Image, t: float, info: dict, hud_alpha: float, title_alpha: float) -> np.ndarray:
        man = self.man
        d = ImageDraw.Draw(img)
        u = info["u"]
        for name, p in PANELS.items():
            run, col, st = self.runs[name], p["colour"], info["states"][name]
            top = GEOM_Y0 + p["index"] * PANEL_H
            py = top + PIVOT_DY
            y_rest = py + self.R
            d.text((COL_X, top + 34), p["label"], font=self.font, fill=col, anchor="lm")
            d.text((COL_X, top + 74), p["sub"], font=self.font_small, fill=MUTED, anchor="lm")
            d.text((COL_X, top + 140), "speed after the hit", font=self.font_small, fill=MUTED, anchor="lm")
            # Readouts: the live values fade out over the first half of the reset, the rest values fade in over the second.
            if u < 0.5:
                a = 1.0 - 2.0 * u
                hit_done = st["tp"] >= 0.0
                d.text((COL_X, top + 186), speed_text(run["v"] if hit_done else 0.0), font=self.font,
                       fill=blend(col if hit_done else TEXT, a), anchor="lm")
                d.text((COL_X, top + 254), "peak" if st["frozen"] else "rise", font=self.font_small,
                       fill=blend(col if st["frozen"] else MUTED, a), anchor="lm")
                d.text((COL_X, top + 306), rise_text(st["h"]), font=self.font_num,
                       fill=blend(col if st["frozen"] else TEXT, a), anchor="lm")
            else:
                a = 2.0 * u - 1.0
                d.text((COL_X, top + 186), speed_text(0.0), font=self.font, fill=blend(TEXT, a), anchor="lm")
                d.text((COL_X, top + 254), "rise", font=self.font_small, fill=blend(MUTED, a), anchor="lm")
                d.text((COL_X, top + 306), rise_text(0.0), font=self.font_num, fill=blend(TEXT, a), anchor="lm")
            for h, label in ((0.0, "0"), (self.runs["stick"]["h_peak"], None), (self.runs["bounce"]["h_peak"], None)):
                d.text((MARK_LABEL_X, y_rest - h * self.ppm), label or rise_text(h), font=self.font_small, fill=MUTED, anchor="lm")
        if hud_alpha > 0.02:
            d.text((W / 2, COUNTER_Y), f"shot {info['k'] + 1} of {man['shots']}", font=self.font, fill=blend(TEXT, hud_alpha), anchor="mm")
            d.text((W / 2, TAG_Y), model_tag(man), font=self.font_small, fill=blend(MUTED, hud_alpha), anchor="mm")
        if title_alpha > 0.0:
            for j, line in enumerate(man["title"].split("|")):
                d.text((W / 2, 190 + j * 62), line, font=self.font_title, fill=blend(TEXT, title_alpha), anchor="mm")
        if t >= man["payoff_t"]:
            a = min(1.0, (t - man["payoff_t"]) / man["payoff_hold"])
            for j, line in enumerate(payoff_lines(man, self.ev)):
                d.text((W / 2, PAYOFF_Y + j * 56), line, font=self.font, fill=blend(GOLD, a), anchor="mm")
        return np.asarray(img, dtype=np.float32)

    def live_frame(self, f: int) -> np.ndarray:
        man = self.man
        t = f / self.fps
        if t < man["title_until"]:
            title_alpha = 1.0 if t < man["title_until"] - 0.4 else (man["title_until"] - t) / 0.4
            hud_alpha = 0.0
        else:
            title_alpha = 0.0
            hud_alpha = min(1.0, (t - man["title_until"]) / 0.4)
        img, info = self.draw_geometry(t)
        return self.draw_hud(img, t, info, hud_alpha, title_alpha)

    def frame_at(self, f: int) -> np.ndarray:
        man = self.man
        live = self.live_frame(f)
        fade_frames = int(round(man["loop_fade"] * self.fps))
        if f >= self.total - fade_frames:
            if self.first is None:
                self.first = self.live_frame(0)
            a = (f - (self.total - fade_frames) + 1) / fade_frames
            live = live * (1 - a) + self.first * a
        return live.astype(np.uint8)

    def render(self, out_path: Path) -> None:
        global _RENDERER
        out_path.parent.mkdir(parents=True, exist_ok=True)
        total = self.total
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
    man = json.loads((ROOT / "projects/ballistic/manifest.json").read_text())
    ev = measure(man)
    if "--measure-only" in sys.argv:
        return
    if "--frames" in sys.argv:
        times = [float(v) for v in sys.argv[sys.argv.index("--frames") + 1].split(",")]
        r = Renderer(man, ev)
        (ROOT / "media/ballistic").mkdir(parents=True, exist_ok=True)
        for tv in times:
            Image.fromarray(r.frame_at(int(round(tv * man["fps"])))).save(ROOT / f"media/ballistic/smoke-{tv}.png")
        print("smoke frames: " + ", ".join(f"{tv}" for tv in times))
        return
    Renderer(man, ev).render(ROOT / "media/ballistic/footage.mp4")


if __name__ == "__main__":
    main()
