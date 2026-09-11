#!/usr/bin/env python3
"""Gyroscope top: spin a top three times faster, does it circle faster?

Two identical tops on a table at the same lean, each started in steady
precession. The top one spins thirty times a second, the bottom one ninety.
Lagrange's equations of the heavy symmetric top with theta the lean from the
vertical, phi the azimuth of the axis (the circling) and psi the spin angle,
and the two conserved momenta p_phi and p_psi:

    I1 theta'' = I1 phi'^2 sin(theta) cos(theta) - p_psi phi' sin(theta) + m g r sin(theta)
    phi'       = (p_phi - p_psi cos(theta)) / (I1 sin(theta)^2)
    psi'       = p_psi / I3 - phi' cos(theta)

integrated with RK4 at a fixed step. The mass cancels. The top is a solid
disc of radius R and thickness h on a massless stem with its centre r above
the tip, so I3 = R^2 / 2 and I1 = (3 R^2 + h^2) / 12 + r^2 per unit mass.

Measured and printed: the moments of inertia, the steady precession rate from
the quadratic I1 cos(theta) W^2 - I3 w3 W + m g r = 0 against the fast-top
approximation m g r / (I3 w3), every lap time of each top, the lean and
energy drift, the laps inside the short, the ratio of the lap times, a
cross-check with a full rigid-body quaternion integration, a step-halving
check, the same tops released from rest, tops spun below the critical rate
falling past horizontal, and the on-screen text widths.

usage: gyrotop.py [--measure-only] [--frames t1,t2,...]
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
TABLE = (24, 30, 38)
TABLE_RIM = (52, 60, 72)
STEM = (170, 178, 190)

# Layout: two panels, captions between them at caption_y 0.49 (y 941..1021).
PANELS = {"slow": {"label_y": 214, "pivot": (540.0, 810.0)}, "fast": {"label_y": 1104, "pivot": (540.0, 1660.0)}}
COLOURS = {"slow": GOLD, "fast": TEAL}
PX_PER_M = 10000.0
PAYOFF_Y = 1836.0
RIM_N = 72


def inertia(man: dict) -> tuple[float, float]:
    """I1 (transverse, about the tip) and I3 (axial) per unit mass."""
    R, h, r = man["disc_radius"], man["disc_thickness"], man["com_height"]
    return (3 * R * R + h * h) / 12 + r * r, 0.5 * R * R


def steady_rate(I1: float, I3: float, mgr: float, w3: float, theta: float) -> float | None:
    """Slow root of I1 cos(theta) W^2 - I3 w3 W + m g r = 0, or None below the threshold."""
    s = I3 * w3
    disc = s * s - 4 * I1 * mgr * math.cos(theta)
    if disc < 0:
        return None
    return (s - math.sqrt(disc)) / (2 * I1 * math.cos(theta))


def lap_times(phi: np.ndarray, dt: float) -> np.ndarray:
    """Times at which the azimuth passes each whole turn, linearly interpolated."""
    turns = np.floor(phi / (2 * math.pi))
    idx = np.nonzero(turns[1:] > turns[:-1])[0]
    out = []
    for i in idx:
        target = 2 * math.pi * turns[i + 1]
        out.append((i + (target - phi[i]) / (phi[i + 1] - phi[i])) * dt)
    return np.array(out)


def simulate(man: dict, spin_hz: float, duration: float, steps_per_s: int,
             from_rest: bool = False) -> dict:
    """Reduced heavy-top equations. Returns per-step theta, phi, psi and checks."""
    I1, I3 = inertia(man)
    mgr = man["g"] * man["com_height"]
    th0 = math.radians(man["tilt_deg"])
    w3 = 2 * math.pi * spin_hz
    p_psi = I3 * w3
    W0 = 0.0 if from_rest else steady_rate(I1, I3, mgr, w3, th0)
    if W0 is None:
        W0 = 0.0
    p_phi = I1 * W0 * math.sin(th0) ** 2 + p_psi * math.cos(th0)

    def deriv(y: np.ndarray) -> np.ndarray:
        th, thd = y[0], y[1]
        s, c = math.sin(th), math.cos(th)
        phd = (p_phi - p_psi * c) / (I1 * s * s)
        psd = p_psi / I3 - phd * c
        thdd = (I1 * phd * phd * s * c - p_psi * phd * s + mgr * s) / I1
        return np.array([thd, thdd, phd, psd])

    def energy(y: np.ndarray) -> float:
        th, thd = y[0], y[1]
        s, c = math.sin(th), math.cos(th)
        phd = (p_phi - p_psi * c) / (I1 * s * s)
        return 0.5 * I1 * (thd * thd + phd * phd * s * s) + 0.5 * p_psi * p_psi / I3 + mgr * c

    dt = 1.0 / steps_per_s
    n = int(round(duration * steps_per_s))
    y = np.array([th0, 0.0, 0.0, 0.0])
    theta = np.empty(n + 1)
    phi = np.empty(n + 1)
    psi = np.empty(n + 1)
    E0 = energy(y)
    max_dE = 0.0
    fall_t = None
    for i in range(n + 1):
        theta[i], phi[i], psi[i] = y[0], y[2], y[3]
        if i == n:
            break
        k1 = deriv(y)
        k2 = deriv(y + 0.5 * dt * k1)
        k3 = deriv(y + 0.5 * dt * k2)
        k4 = deriv(y + dt * k3)
        y_new = y + dt / 6.0 * (k1 + 2 * k2 + 2 * k3 + k4)
        if fall_t is None and y[0] < math.pi / 2 <= y_new[0]:
            fall_t = (i + (math.pi / 2 - y[0]) / (y_new[0] - y[0])) * dt
        y = y_new
        if i % 100 == 0:
            max_dE = max(max_dE, abs(energy(y) - E0) / abs(E0))
    laps = lap_times(phi, dt)
    return {"theta": theta, "phi": phi, "psi": psi, "dt": dt, "W0": W0, "p_psi": p_psi, "p_phi": p_phi,
            "laps": laps, "periods": np.diff(laps) if len(laps) > 1 else np.array([]),
            "first_lap": float(laps[0]) if len(laps) else None,
            "lean_min": float(np.degrees(theta.min())), "lean_max": float(np.degrees(theta.max())),
            "dE": max_dE, "fall_t": fall_t, "spin_hz": spin_hz}


# Full rigid-body cross-check: Euler's equations in the body frame with the
# gravity torque about the tip, orientation as a unit quaternion.
def quat_mul(p: np.ndarray, q: np.ndarray) -> np.ndarray:
    w1, x1, y1, z1 = p
    w2, x2, y2, z2 = q
    return np.array([
        w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2,
        w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2,
        w1 * y2 - x1 * z2 + y1 * w2 + z1 * x2,
        w1 * z2 + x1 * y2 - y1 * x2 + z1 * w2,
    ])


def quat_to_matrix(q: np.ndarray) -> np.ndarray:
    w, x, y, z = q
    return np.array([
        [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
        [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
        [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)],
    ])


def simulate_rigid(man: dict, spin_hz: float, duration: float, steps_per_s: int) -> dict:
    I1, I3 = inertia(man)
    inert = np.array([I1, I1, I3])
    g, r = man["g"], man["com_height"]
    th0 = math.radians(man["tilt_deg"])
    w3 = 2 * math.pi * spin_hz
    W0 = steady_rate(I1, I3, g * r, w3, th0)
    q = np.array([math.cos(th0 / 2), 0.0, math.sin(th0 / 2), 0.0])  # body z -> (sin th0, 0, cos th0)
    Rm = quat_to_matrix(q)
    n0 = Rm[:, 2]
    w_space = W0 * np.array([0.0, 0.0, 1.0]) + (w3 - W0 * math.cos(th0)) * n0
    w_body = Rm.T @ w_space
    state = np.concatenate([w_body, q])
    zhat = np.array([0.0, 0.0, 1.0])

    def deriv(s: np.ndarray) -> np.ndarray:
        w, qq = s[:3], s[3:]
        Rq = quat_to_matrix(qq)
        n = Rq[:, 2]
        tau_space = -g * r * np.cross(n, zhat)
        tau_body = Rq.T @ tau_space
        dw = (tau_body + np.cross(inert * w, w)) / inert
        dq = 0.5 * quat_mul(qq, np.array([0.0, w[0], w[1], w[2]]))
        return np.concatenate([dw, dq])

    dt = 1.0 / steps_per_s
    n = int(round(duration * steps_per_s))
    phi = np.empty(n + 1)
    theta = np.empty(n + 1)
    Lz0 = None
    max_dLz = 0.0
    prev = 0.0
    unwrapped = 0.0
    for i in range(n + 1):
        Rq = quat_to_matrix(state[3:])
        nvec = Rq[:, 2]
        a = math.atan2(nvec[1], nvec[0])
        d = a - prev
        d -= 2 * math.pi * round(d / (2 * math.pi))
        unwrapped += d
        prev = a
        phi[i] = unwrapped
        theta[i] = math.acos(max(-1.0, min(1.0, nvec[2])))
        Lz = float((Rq @ (inert * state[:3]))[2])
        if Lz0 is None:
            Lz0 = Lz
        max_dLz = max(max_dLz, abs(Lz - Lz0) / abs(Lz0))
        if i == n:
            break
        k1 = deriv(state)
        k2 = deriv(state + 0.5 * dt * k1)
        k3 = deriv(state + 0.5 * dt * k2)
        k4 = deriv(state + dt * k3)
        state = state + dt / 6.0 * (k1 + 2 * k2 + 2 * k3 + k4)
        state[3:] /= np.linalg.norm(state[3:])
    laps = lap_times(phi, dt)
    return {"laps": laps, "lean_min": float(np.degrees(theta.min())), "lean_max": float(np.degrees(theta.max())),
            "dLz": max_dLz}


def measure(man: dict) -> dict:
    I1, I3 = inertia(man)
    R, h, r = man["disc_radius"], man["disc_thickness"], man["com_height"]
    g = man["g"]
    mgr = g * r
    th0 = math.radians(man["tilt_deg"])
    steps = man["fps"] * man["substeps"]
    dur = man["scene_duration"]
    print(f"top: disc radius {R * 100:.1f} cm, thickness {h * 100:.1f} cm, centre {r * 100:.1f} cm above the tip, "
          f"lean {man['tilt_deg']:g} deg from the vertical; per unit mass I1 {I1:.4e}, I3 {I3:.4e} m^2, "
          f"g r {mgr:.5f} m^2/s^2; RK4 at {steps} steps per second, deterministic, no seed")
    w_sleep = math.sqrt(4 * I1 * mgr) / I3
    w_fall = math.sqrt(2 * I1 * mgr / math.cos(th0)) / I3
    print(f"thresholds: a top standing straight up is stable above {w_sleep / (2 * math.pi):.2f} turns a second; "
          f"released from rest at {man['tilt_deg']:g} deg it swings past horizontal below {w_fall / (2 * math.pi):.2f} turns a second")
    runs: dict[str, dict] = {}
    exact: dict[str, float] = {}
    for name, hz in man["spins_per_second"].items():
        w3 = 2 * math.pi * hz
        s = I3 * w3
        c = 4 * I1 * mgr * math.cos(th0)
        Wex = steady_rate(I1, I3, mgr, w3, th0)
        Wap = mgr / s
        exact[name] = 2 * math.pi / Wex
        print(f"{name} top: {hz:g} turns a second ({hz * 60:.0f} rpm); I3 w3 over the threshold {s / math.sqrt(c):.2f}x; "
              f"steady precession {Wex:.4f} rad/s, period {2 * math.pi / Wex:.4f} s "
              f"(fast-top approximation m g r / (I3 w3): {Wap:.4f} rad/s, {2 * math.pi / Wap:.4f} s)")
        run = simulate(man, hz, dur, steps)
        runs[name] = run
        per = run["periods"]
        print(f"  measured: {len(run['laps'])} laps in {dur:g} s, first lap at {run['first_lap']:.4f} s, "
              f"lap time mean {per.mean():.4f} s (min {per.min():.4f}, max {per.max():.4f}); "
              f"lean stays between {run['lean_min']:.4f} and {run['lean_max']:.4f} deg; energy drift {run['dE']:.1e}; "
              f"turns in {dur:g} s: {hz * dur:.0f}")
    ratio = runs["fast"]["periods"].mean() / runs["slow"]["periods"].mean()
    print(f"ratio of lap times fast/slow: {ratio:.4f} (exact steady roots {exact['fast'] / exact['slow']:.4f}; "
          f"the fast-top approximation gives exactly 3)")
    # Checks.
    for name, hz in man["spins_per_second"].items():
        fine = simulate(man, hz, min(dur, 12.0), man["check_steps_per_second"])
        rigid = simulate_rigid(man, hz, man["check_rigid_duration"], 3 * man["check_steps_per_second"])
        print(f"check {name}: {man['check_steps_per_second']} steps per second first lap {fine['first_lap']:.4f} s; "
              f"full rigid-body quaternion run at {3 * man['check_steps_per_second']} steps per second first lap "
              f"{rigid['laps'][0]:.4f} s, lean {rigid['lean_min']:.3f} to {rigid['lean_max']:.3f} deg, "
              f"vertical angular momentum drift {rigid['dLz']:.1e}")
        rest = simulate(man, hz, man["check_rest_duration"], steps, from_rest=True)
        n_laps = len(rest["laps"])
        print(f"check {name} released from rest at the same lean: {n_laps} laps in {man['check_rest_duration']:g} s, "
              f"average lap {rest['laps'][-1] / n_laps:.4f} s, lean wobbles between {rest['lean_min']:.2f} and "
              f"{rest['lean_max']:.2f} deg")
    for hz in man["check_fall_spins"]:
        fall = simulate(man, hz, 6.0, steps, from_rest=True)
        if fall["fall_t"] is not None:
            print(f"check: spun {hz:g} turns a second and released from rest at the same lean, the top passes "
                  f"horizontal at {fall['fall_t']:.3f} s (lean reaches {fall['lean_max']:.1f} deg)")
        else:
            print(f"check: spun {hz:g} turns a second and released from rest at the same lean, the top stays up "
                  f"(lean wobbles between {fall['lean_min']:.1f} and {fall['lean_max']:.1f} deg over 6 s)")
    return {"runs": runs, "ratio": ratio,
            "period": {k: float(v["periods"].mean()) for k, v in runs.items()},
            "laps": {k: int(len(v["laps"])) for k, v in runs.items()}}


class Renderer:
    def __init__(self, man: dict, meas: dict):
        self.man, self.meas = man, meas
        self.fps = man["fps"]
        font = os.environ["SEED_ZERO_FONT"]
        self.font = ImageFont.truetype(font, 40)
        self.font_small = ImageFont.truetype(font, 32)
        self.font_big = ImageFont.truetype(font, 56)
        self.font_title = ImageFont.truetype(font, 56)
        self.font_read = ImageFont.truetype(font, 48)
        a = math.radians(man["camera_elevation_deg"])
        self.sa, self.ca = math.sin(a), math.cos(a)
        self.view = np.array([0.0, -self.ca, self.sa])  # towards the camera
        self.light = np.array([-0.4, -0.5, 0.75])
        self.light /= np.linalg.norm(self.light)
        self.steps = man["fps"] * man["substeps"]
        self.first = None
        widths = {"overlay@34": (ImageFont.truetype(font, 34), man["overlay"])}
        for j, line in enumerate(man["title"].split("|")):
            widths[f"title line {j + 1}@56"] = (self.font_title, line)
        for name, hz in man["spins_per_second"].items():
            widths[f"label {name}@40"] = (self.font, f"spins {hz:g} times a second")
            widths[f"turns {name}@48"] = (self.font_read, f"turns: {int(hz * man['scene_duration']):,}")
            widths[f"lap readout {name}@48"] = (self.font_read, f"{meas['period'][name]:.1f} s a lap")
            widths[f"laps {name}@56"] = (self.font_big, f"laps: {meas['laps'][name]}")
        for j, line in enumerate(self.payoff_lines()):
            widths[f"payoff line {j + 1}@40"] = (self.font, line)
        print("text widths: " + ", ".join(f"{k} {f.getlength(s):.0f} px" for k, (f, s) in widths.items()))

    def payoff_lines(self) -> list[str]:
        p = self.meas["period"]
        text = self.man["payoff_text"].format(slow=p["slow"], fast=p["fast"], ratio=self.meas["ratio"])
        return [s.strip() for s in text.split("|")]

    def project(self, p: np.ndarray, pivot: tuple) -> tuple[float, float]:
        return (pivot[0] + p[0] * PX_PER_M, pivot[1] - (p[1] * self.sa + p[2] * self.ca) * PX_PER_M)

    def shade(self, col: tuple, k: float) -> tuple:
        return tuple(int(max(0, min(255, c * k))) for c in col)

    def draw_top(self, d: ImageDraw.ImageDraw, theta: float, phi: float, pivot: tuple, colour: tuple,
                 trace_theta: float) -> dict:
        man = self.man
        R, h, r, Lh = man["disc_radius"], man["disc_thickness"], man["com_height"], man["handle_length"]
        n = np.array([math.sin(theta) * math.cos(phi), math.sin(theta) * math.sin(phi), math.cos(theta)])
        e1 = np.array([-math.sin(phi), math.cos(phi), 0.0])
        e2 = np.cross(n, e1)
        c_b, c_t = (r - h / 2) * n, (r + h / 2) * n
        tip_h = (r + h / 2 + Lh) * n
        nv = float(n @ self.view)
        ang = np.linspace(0, 2 * math.pi, RIM_N, endpoint=False)
        rim_b = [self.project(c_b + R * (math.cos(a) * e1 + math.sin(a) * e2), pivot) for a in ang]
        rim_t = [self.project(c_t + R * (math.cos(a) * e1 + math.sin(a) * e2), pivot) for a in ang]
        # Trace ring of the handle tip at the nominal lean: far half before the top, near half after.
        L_tip = r + h / 2 + Lh
        rho, z = L_tip * math.sin(trace_theta), L_tip * math.cos(trace_theta)
        ring = [(a, self.project(np.array([rho * math.cos(a), rho * math.sin(a), z]), pivot)) for a in np.linspace(0, 2 * math.pi, 96, endpoint=False)]

        def ring_dots(near: bool) -> None:
            for a, (x, y) in ring:
                if (math.sin(a) < 0) == near:
                    d.ellipse((x - 2.5, y - 2.5, x + 2.5, y + 2.5), fill=WIRE)

        def axis_quad(p0: np.ndarray, p1: np.ndarray, w0: float, w1: float) -> list:
            s0, s1 = self.project(p0, pivot), self.project(p1, pivot)
            dx, dy = s1[0] - s0[0], s1[1] - s0[1]
            L = math.hypot(dx, dy) or 1.0
            px, py = -dy / L, dx / L
            return [(s0[0] + px * w0, s0[1] + py * w0), (s1[0] + px * w1, s1[1] + py * w1),
                    (s1[0] - px * w1, s1[1] - py * w1), (s0[0] - px * w0, s0[1] - py * w0)]

        def draw_stem() -> None:
            d.polygon(axis_quad(np.zeros(3), c_b, 1.5, 0.0018 * PX_PER_M), fill=STEM)

        def draw_handle() -> None:
            d.polygon(axis_quad(c_t, tip_h, 0.0012 * PX_PER_M, 0.0012 * PX_PER_M), fill=STEM)
            x, y = self.project(tip_h, pivot)
            k = 0.0028 * PX_PER_M
            d.ellipse((x - k, y - k, x + k, y + k), fill=TEXT)

        def draw_side() -> None:
            for j in range(RIM_N):
                am = ang[j] + math.pi / RIM_N
                m = math.cos(am) * e1 + math.sin(am) * e2
                if float(m @ self.view) <= 0:
                    continue
                k = 0.40 + 0.45 * max(0.0, float(m @ self.light))
                col = self.shade(colour, k)
                j2 = (j + 1) % RIM_N
                d.polygon([rim_b[j], rim_b[j2], rim_t[j2], rim_t[j]], fill=col, outline=col)

        def draw_face(top: bool) -> None:
            rim = rim_t if top else rim_b
            normal = n if top else -n
            centre = c_t if top else c_b
            k = 0.62 + 0.38 * max(0.0, float(normal @ self.light))
            col = self.shade(colour, k)
            d.polygon(rim, fill=col, outline=col)
            if top:
                for frac, kk in ((0.70, 0.86), (0.62, 1.0)):
                    pts = [self.project(centre + frac * R * (math.cos(a) * e1 + math.sin(a) * e2), pivot) for a in ang]
                    d.polygon(pts, fill=self.shade(col, kk), outline=self.shade(col, kk))
            hub = [self.project(centre + 0.14 * R * (math.cos(a) * e1 + math.sin(a) * e2), pivot) for a in ang]
            d.polygon(hub, fill=STEM, outline=STEM)

        ring_dots(False)
        if nv >= 0:
            draw_stem()
            draw_side()
            draw_face(True)
            draw_handle()
        else:
            draw_handle()
            draw_side()
            draw_face(False)
            draw_stem()
        ring_dots(True)
        # Lap start mark on the ring.
        x, y = ring[0][1]
        d.ellipse((x - 7, y - 7, x + 7, y + 7), fill=TEXT)
        return {"disc": self.project(r * n, pivot), "tip": self.project(tip_h, pivot), "n": n,
                "tangent": np.array([-math.sin(phi), math.cos(phi), 0.0])}

    def draw_arrow(self, d: ImageDraw.ImageDraw, p0: tuple, p1: tuple, col: tuple, width: int = 8) -> None:
        d.line([p0, p1], fill=col, width=width)
        dx, dy = p1[0] - p0[0], p1[1] - p0[1]
        L = math.hypot(dx, dy) or 1.0
        ux, uy = dx / L, dy / L
        px, py = -uy, ux
        head = 22
        d.polygon([(p1[0] + ux * 10, p1[1] + uy * 10), (p1[0] - ux * head + px * 14, p1[1] - uy * head + py * 14),
                   (p1[0] - ux * head - px * 14, p1[1] - uy * head - py * 14)], fill=col)

    def live_frame(self, f: int) -> Image.Image:
        man, m = self.man, self.meas
        t = f / self.fps
        img = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(img)
        title_on = t < man["title_until"]
        th_nom = math.radians(man["tilt_deg"])

        def shade_col(col, alpha):
            return tuple(int(c * alpha + BG[j] * (1 - alpha)) for j, c in enumerate(col))

        for name, p in PANELS.items():
            run = m["runs"][name]
            hz = man["spins_per_second"][name]
            i = min(int(round(t * self.steps)), len(run["theta"]) - 1)
            px, py = p["pivot"]
            # Table.
            rt = man["table_radius"] * PX_PER_M
            d.ellipse((px - rt, py - rt * self.sa, px + rt, py + rt * self.sa), fill=TABLE, outline=TABLE_RIM, width=3)
            geo = self.draw_top(d, float(run["theta"][i]), float(run["phi"][i]), p["pivot"], COLOURS[name], th_nom)
            d.ellipse((px - 4, py - 4, px + 4, py + 4), fill=TEXT)
            # Mechanism arrows: gravity down at the disc, then the sideways motion at the handle tip.
            if man["mech_t"] <= t < man["mech_until"]:
                a1 = min(1.0, (t - man["mech_t"]) / 0.3, (man["mech_until"] - t) / 0.3)
                gx, gy = geo["disc"]
                col = shade_col(CORAL, a1)
                self.draw_arrow(d, (gx, gy + 24), (gx, gy + 120), col)
                d.text((gx + 22, gy + 78), "gravity", font=self.font_small, fill=col, anchor="lm", stroke_width=3, stroke_fill=BG)
                if t >= man["mech_arrow2_t"]:
                    a2 = min(1.0, (t - man["mech_arrow2_t"]) / 0.3, (man["mech_until"] - t) / 0.3)
                    tx, ty = geo["tip"]
                    tg = geo["tangent"]
                    sx, sy = tg[0], -(tg[1] * self.sa)
                    L = math.hypot(sx, sy) or 1.0
                    sx, sy = sx / L * 96, sy / L * 96
                    self.draw_arrow(d, (tx + sx * 0.25, ty + sy * 0.25), (tx + sx, ty + sy), shade_col(TEXT, a2))
            # Labels and readouts.
            if name == "slow" and title_on:
                alpha = 1.0 if t < man["title_until"] - 0.4 else (man["title_until"] - t) / 0.4
                shade = shade_col(TEXT, alpha)
                for j, line in enumerate(man["title"].split("|")):
                    d.text((W / 2, 186 + j * 62), line, font=self.font_title, fill=shade, anchor="mm")
                continue
            d.text((60, p["label_y"]), f"spins {hz:g} times a second", font=self.font, fill=COLOURS[name], anchor="lm")
            turns = int(hz * t)
            d.text((60, p["label_y"] + 54), f"turns: {turns:,}", font=self.font_read, fill=MUTED, anchor="lm")
            laps = int(np.searchsorted(run["laps"], t, side="right"))
            d.text((W - 60, p["label_y"]), f"laps: {laps}", font=self.font_big, fill=TEXT, anchor="rm")
            if laps >= 1:
                d.text((W - 60, p["label_y"] + 54), f"{m['period'][name]:.1f} s a lap", font=self.font_read,
                       fill=COLOURS[name], anchor="rm")
        if t >= man["payoff_t"]:
            alpha = min(1.0, (t - man["payoff_t"]) / man["payoff_hold"])
            shade = shade_col(GOLD, alpha)
            for j, line in enumerate(self.payoff_lines()):
                d.text((W / 2, PAYOFF_Y - 32 + j * 64), line, font=self.font, fill=shade, anchor="mm")
        return img

    def frame_at(self, f: int) -> np.ndarray:
        man = self.man
        total = int(round(man["scene_duration"] * self.fps))
        live = np.asarray(self.live_frame(f), dtype=np.float32)
        fade_frames = int(round(man["loop_fade"] * self.fps))
        if f >= total - fade_frames:
            if self.first is None:
                self.first = np.asarray(self.live_frame(0), dtype=np.float32)
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
    man = json.loads((ROOT / "projects/gyrotop/manifest.json").read_text())
    meas = measure(man)
    if "--measure-only" in sys.argv:
        return
    if "--frames" in sys.argv:
        times = [float(v) for v in sys.argv[sys.argv.index("--frames") + 1].split(",")]
        r = Renderer(man, meas)
        for tv in times:
            Image.fromarray(r.frame_at(int(round(tv * man["fps"])))).save(ROOT / f"media/gyrotop/smoke-{tv}.png")
        print("smoke frames: " + ", ".join(f"{tv}" for tv in times))
        return
    Renderer(man, meas).render(ROOT / "media/gyrotop/footage.mp4")


if __name__ == "__main__":
    main()
