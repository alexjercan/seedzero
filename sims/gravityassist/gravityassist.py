#!/usr/bin/env python3
"""Gravity assist: can a planet throw a ship faster, for free?

Two identical ships coast toward an Earth-mass planet on a circular
orbit around the Sun. Both start one million kilometres from the planet
on its sunward side, moving straight away from the Sun at the same speed
relative to the planet. The gold ship is aimed to pass behind the planet
(on its trailing side), the white ship to pass in front, both at the same
closest approach. Everything is integrated in the Sun's inertial frame:
the planet under the Sun's gravity, each ship under the Sun's and the
planet's gravity, with RK4 at a step that scales with the distance from
the planet. The Sun's pull bends an approach that long, so each ship's
starting offset is found by shooting until its closest approach equals
the target. Measured at the start and when each ship is a million
kilometres from the planet again: speed relative to the Sun, speed
relative to the planet, the turning angle. Checks: half the step, the
closed-form hyperbolic deflection, the planet's recoil from momentum
conservation for a 1,000 kg ship. No seed: the run is deterministic.

usage: gravityassist.py [--measure-only] [--frames t1,t2,...]
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
PLANET_IN = (22, 28, 38)
PLANET_OUT = (58, 72, 96)
RIM = (110, 130, 160)

# Layout: readouts under the overlay, the planet-centred view between
# them and the captions (caption_y 0.75, y 1440..1510), a small clock at
# the bottom of the view, payoff under the captions.
LABEL_Y = 236
READ_Y = 290
VALUE_Y = 338
PANEL_X = {"behind": 300.0, "front": 780.0}
VIEW_TOP = 400
VIEW_BOT = 1400
VIEW_CX = 540.0
VIEW_CY = 900.0
CLOCK_Y = 1392
PAYOFF_Y = 1592.0


def run_ship(man: dict, offset_m: float, step_factor: float = 1.0) -> dict:
    """Integrate the planet and one ship from a million km in until a million km out.

    offset_m is the ship's starting offset along the planet's direction of
    motion (negative: trailing side, so it passes behind).
    """
    mus, mup = man["mu_sun"], man["mu_planet"]
    a = man["orbit_radius_m"]
    omega = math.sqrt(mus / a ** 3)
    V = a * omega
    v_inf = man["v_inf_m_per_s"]
    R0 = man["start_distance_km"] * 1000.0
    # Planet at angle 0 at the nominal closest-approach time t = 0; start
    # about R0 / v_inf earlier, when the planet is at angle -omega * T.
    T = R0 / v_inf
    t = -T
    ang = -omega * T
    r_hat = np.array([math.cos(ang), math.sin(ang)])
    t_hat = np.array([-math.sin(ang), math.cos(ang)])
    P = a * r_hat
    PV = V * t_hat
    D = math.sqrt(R0 * R0 - offset_m * offset_m)
    S = P - D * r_hat + offset_m * t_hat
    SV = PV + v_inf * r_hat
    state = np.concatenate([P, PV, S, SV])

    def deriv(s: np.ndarray) -> np.ndarray:
        p, pv, q, qv = s[0:2], s[2:4], s[4:6], s[6:8]
        rp = np.linalg.norm(p)
        rq = np.linalg.norm(q)
        d = q - p
        rd = np.linalg.norm(d)
        pa = -mus * p / rp ** 3
        qa = -mus * q / rq ** 3 - mup * d / rd ** 3
        return np.concatenate([pv, pa, qv, qa])

    ts, states = [t], [state.copy()]
    dmin, dmin_t = math.inf, t
    inbound = True
    while True:
        d = state[4:6] - state[0:2]
        rd = float(np.linalg.norm(d))
        vrel = float(np.linalg.norm(state[6:8] - state[2:4]))
        if rd < dmin:
            dmin, dmin_t = rd, t
        if not inbound and rd >= R0:
            break
        if inbound and rd > dmin * 1.001 and t > -T * 0.5:
            inbound = False
        dt = min(man["dt_max"], max(man["dt_min"], man["dt_scale"] * rd / vrel)) * step_factor
        k1 = deriv(state)
        k2 = deriv(state + 0.5 * dt * k1)
        k3 = deriv(state + 0.5 * dt * k2)
        k4 = deriv(state + dt * k3)
        state = state + dt / 6.0 * (k1 + 2 * k2 + 2 * k3 + k4)
        t += dt
        ts.append(t)
        states.append(state.copy())
        if t > 4 * T:
            raise RuntimeError("ship did not leave")
    ts_a = np.array(ts)
    st = np.array(states)
    # Refine the closest approach with a parabola through the three
    # nearest samples.
    dist = np.linalg.norm(st[:, 4:6] - st[:, 0:2], axis=1)
    i = int(np.argmin(dist))
    if 0 < i < len(dist) - 1:
        y0, y1, y2 = dist[i - 1], dist[i], dist[i + 1]
        denom = y0 - 2 * y1 + y2
        f = 0.5 * (y0 - y2) / denom if denom != 0 else 0.0
        dmin = y1 - 0.25 * (y0 - y2) * f
        dmin_t = ts_a[i] + f * (ts_a[i + 1] - ts_a[i]) if f > 0 else ts_a[i] + f * (ts_a[i] - ts_a[i - 1])
    sun_speed = np.linalg.norm(st[:, 6:8], axis=1)
    rel_v = st[:, 6:8] - st[:, 2:4]
    rel_speed = np.linalg.norm(rel_v, axis=1)
    planet_speed = np.linalg.norm(st[:, 2:4], axis=1)
    sun_dist = np.linalg.norm(st[:, 4:6], axis=1)
    energy = 0.5 * sun_speed ** 2 - mus / sun_dist
    reduced = np.sqrt(2 * (energy + mus / a))  # speed at the planet's distance from the Sun
    turn = math.degrees(math.atan2(rel_v[-1, 0] * rel_v[0, 1] - rel_v[-1, 1] * rel_v[0, 0],
                                   float(np.dot(rel_v[-1], rel_v[0]))))
    return {"t": ts_a, "st": st, "dist": dist, "dmin": dmin, "dmin_t": dmin_t,
            "sun_speed": sun_speed, "rel_speed": rel_speed, "planet_speed": planet_speed,
            "reduced": reduced, "turn": turn, "V": V, "offset": offset_m, "steps": len(ts_a) - 1,
            "rel_v": rel_v}


def aim(man: dict, side: float, step_factor: float = 1.0) -> dict:
    """Find the starting offset (side -1 behind, +1 in front) that gives the target closest approach."""
    target = man["closest_approach_km"] * 1000.0
    mup, v_inf = man["mu_planet"], man["v_inf_m_per_s"]
    # Planet-frame guess: b = rp sqrt(1 + 2 mu / (rp v^2)), then secant on the real run.
    b0 = target * math.sqrt(1 + 2 * mup / (target * v_inf ** 2))
    x0, x1 = side * b0, side * b0 * 1.05
    r0 = run_ship(man, x0, step_factor)
    r1 = run_ship(man, x1, step_factor)
    f0, f1 = r0["dmin"] - target, r1["dmin"] - target
    for _ in range(30):
        if abs(f1) < 0.5:  # half a metre
            break
        x2 = x1 - f1 * (x1 - x0) / (f1 - f0)
        r2 = run_ship(man, x2, step_factor)
        x0, f0, x1, f1, r1 = x1, f1, x2, r2["dmin"] - target, r2
    return r1


def fmt_recoil(v: float) -> str:
    return f"{v:.1e}"


def measure(man: dict) -> dict:
    mus, mup = man["mu_sun"], man["mu_planet"]
    a = man["orbit_radius_m"]
    V = a * math.sqrt(mus / a ** 3)
    v_inf = man["v_inf_m_per_s"]
    rp = man["closest_approach_km"] * 1000.0
    print(f"setup: an Earth-mass planet (mu {mup:.6g} m^3/s^2, radius {man['planet_radius_km']:,.0f} km) on a "
          f"circular orbit of radius {a / 1000:,.0f} km around the Sun (mu {mus:.6g}), moving at {V:,.1f} m/s; "
          f"two ships start {man['start_distance_km']:,.0f} km from the planet on its sunward side, moving "
          f"straight away from the Sun at {v_inf:,.0f} m/s relative to the planet, aimed to pass "
          f"{man['closest_approach_km']:,.0f} km from the planet's centre ({man['closest_approach_km'] - man['planet_radius_km']:,.0f} km "
          f"above the surface), one behind it and one in front; Sun-frame RK4 with steps of "
          f"{man['dt_min']:g} to {man['dt_max']:g} s scaled to the distance from the planet; the starting "
          f"offset of each ship is found by shooting until its closest approach matches; deterministic, no seed")
    runs = {"behind": aim(man, -1.0), "front": aim(man, +1.0)}
    out = {}
    for name, r in runs.items():
        gain = r["sun_speed"][-1] - r["sun_speed"][0]
        print(f"{name}: starting offset {r['offset'] / 1000:+,.1f} km along the planet's motion; closest approach "
              f"{r['dmin'] / 1000:,.1f} km at {r['dmin_t'] / 3600:+.3f} h, {r['rel_speed'][int(np.argmin(r['dist']))]:,.0f} m/s "
              f"relative to the planet there; relative to the planet: {r['rel_speed'][0]:,.1f} m/s in, "
              f"{r['rel_speed'][-1]:,.1f} m/s out, path turned by {abs(r['turn']):.2f} degrees; relative to the Sun: "
              f"{r['sun_speed'][0]:,.1f} m/s in, {r['sun_speed'][-1]:,.1f} m/s out, {gain:+,.1f} m/s "
              f"({gain / 1000:+.2f} km/s); reduced to the planet's distance from the Sun: {r['reduced'][0]:,.1f} in, "
              f"{r['reduced'][-1]:,.1f} out, {r['reduced'][-1] - r['reduced'][0]:+,.1f} m/s; the run covers "
              f"{(r['t'][-1] - r['t'][0]) / 3600:.1f} h in {r['steps']:,} steps; the planet's own speed "
              f"{r['planet_speed'][0]:,.4f} m/s at the start, {r['planet_speed'][-1]:,.4f} at the end")
        out[name] = r
    # Closed form in the planet frame with the planet's velocity fixed.
    e = 1 + rp * v_inf ** 2 / mup
    delta = 2 * math.asin(1 / e)
    v_in = np.array([v_inf, 0.0])
    Vp = np.array([0.0, V])
    for name, sgn in (("behind", +1.0), ("front", -1.0)):
        c, s = math.cos(sgn * delta), math.sin(sgn * delta)
        v_out = np.array([c * v_in[0] - s * v_in[1], s * v_in[0] + c * v_in[1]])
        print(f"check, closed form ({name}): eccentricity {e:.4f}, turn 2 asin(1/e) = {math.degrees(delta):.2f} degrees, "
              f"speed relative to the Sun {np.linalg.norm(Vp + v_in):,.1f} m/s in, {np.linalg.norm(Vp + v_out):,.1f} out, "
              f"{np.linalg.norm(Vp + v_out) - np.linalg.norm(Vp + v_in):+,.1f} m/s")
    fine = aim(man, -1.0, man["check_step_factor"])
    print(f"check, half the step (behind): closest approach {fine['dmin'] / 1000:,.1f} km, relative to the Sun "
          f"{fine['sun_speed'][0]:,.1f} in, {fine['sun_speed'][-1]:,.1f} out, "
          f"{fine['sun_speed'][-1] - fine['sun_speed'][0]:+,.1f} m/s (full step "
          f"{out['behind']['sun_speed'][-1] - out['behind']['sun_speed'][0]:+,.1f})")
    m = man["ship_mass_kg"]
    M = mup / 6.674e-11
    dv_vec = out["behind"]["st"][-1, 6:8] - out["behind"]["st"][0, 6:8]
    dv_planet_vec = out["behind"]["st"][-1, 2:4] - out["behind"]["st"][0, 2:4]
    # The planet's velocity change over the window is the Sun's turning of
    # its orbit; the ship's is that plus the flyby. Recoil from momentum.
    flyby_dv = np.linalg.norm(dv_vec - dv_planet_vec)
    recoil = m * flyby_dv / M
    print(f"check, recoil: the gold ship's velocity changes by {flyby_dv:,.1f} m/s beyond the Sun's turning of the "
          f"planet's orbit; momentum conservation gives the planet ({M:.3e} kg) a recoil of {m:g} kg x "
          f"{flyby_dv:,.1f} m/s / {M:.3e} kg = {recoil:.1e} m/s (about a billionth of a billionth of a metre "
          f"per second); the integration treats the ship as massless, so the planet's speed above is unchanged "
          f"except by rounding")
    gain = (out["behind"]["sun_speed"][-1] - out["behind"]["sun_speed"][0]) / 1000
    loss = (out["front"]["sun_speed"][-1] - out["front"]["sun_speed"][0]) / 1000
    return {"runs": out, "gain": gain, "loss": loss, "recoil": recoil, "V": V,
            "closest_km": out["behind"]["dmin"] / 1000}


def pchip(xk: np.ndarray, yk: np.ndarray, x: float) -> float:
    """Monotone cubic (Fritsch-Carlson) interpolation through the knots."""
    n = len(xk)
    h = np.diff(xk)
    d = np.diff(yk) / h
    m = np.zeros(n)
    m[0], m[-1] = d[0], d[-1]
    for i in range(1, n - 1):
        if d[i - 1] * d[i] <= 0:
            m[i] = 0.0
        else:
            w1, w2 = 2 * h[i] + h[i - 1], h[i] + 2 * h[i - 1]
            m[i] = (w1 + w2) / (w1 / d[i - 1] + w2 / d[i])
    if x <= xk[0]:
        return float(yk[0] + m[0] * (x - xk[0]))
    if x >= xk[-1]:
        return float(yk[-1])
    i = int(np.searchsorted(xk, x) - 1)
    u = (x - xk[i]) / h[i]
    h00 = (1 + 2 * u) * (1 - u) ** 2
    h10 = u * (1 - u) ** 2
    h01 = u * u * (3 - 2 * u)
    h11 = u * u * (u - 1)
    return float(h00 * yk[i] + h10 * h[i] * m[i] + h01 * yk[i + 1] + h11 * h[i] * m[i + 1])


class Renderer:
    def __init__(self, man: dict, meas: dict):
        self.man, self.meas = man, meas
        self.fps = man["fps"]
        font = os.environ["SEED_ZERO_FONT"]
        self.font = ImageFont.truetype(font, 40)
        self.font_small = ImageFont.truetype(font, 32)
        self.font_title = ImageFont.truetype(font, 56)
        self.font_read = ImageFont.truetype(font, 44)
        self.font_label = ImageFont.truetype(font, 34)
        self.font_tag = ImageFont.truetype(font, 28)
        self.first = None
        self.xk = np.array(man["time_knots_video_s"])
        self.yk = np.array(man["time_knots_sim_s"])
        # Knots are hours from the closest pass; the run's own clock has
        # the closest pass a little before zero because the pull speeds
        # the ships up on the way in.
        self.t_ca = meas["runs"]["behind"]["dmin_t"]
        self.labels = {"behind": "gold, passes behind", "front": "white, passes in front"}
        widths = {"overlay@34": (ImageFont.truetype(font, 34), man["overlay"])}
        for j, line in enumerate(man["title"].split("|")):
            widths[f"title line {j + 1}@56"] = (self.font_title, line)
        for name, label in self.labels.items():
            widths[f"label {name}@34"] = (self.font_label, label)
        widths["readout label@32"] = (self.font_small, "speed relative to the Sun")
        widths["readout@44"] = (self.font_read, "34.5 km/s")
        widths["planet tag@28"] = (self.font_tag, "planet, 30 km/s")
        widths["clock@32"] = (self.font_small, "53.5 hours after the closest pass")
        widths["scale@28"] = (self.font_tag, "1,000,000 km")
        for j, line in enumerate(self.payoff_lines()):
            widths[f"payoff line {j + 1}@40"] = (self.font, line)
        print("text widths: " + ", ".join(f"{k} {f.getlength(s):.0f} px" for k, (f, s) in widths.items()))
        knots = ", ".join(f"{v:g} s -> {s / 3600:+.1f} h" for v, s in zip(self.xk, self.yk))
        r = self.meas["runs"]["behind"]
        print(f"time-lapse knots (video -> sim, hours from the closest pass): {knots}; the closest pass is at "
              f"{self.video_time_for(0.0):.2f} s of video, the ships leave the 1,000,000 km window at "
              f"{self.video_time_for(r['t'][-1] - self.t_ca):.2f} s and hold there; payoff card at {man['payoff_t']:g} s")

    def video_time_for(self, rel_t: float) -> float:
        lo, hi = 0.0, self.man["scene_duration"]
        for _ in range(60):
            mid = 0.5 * (lo + hi)
            if pchip(self.xk, self.yk, mid) < rel_t:
                lo = mid
            else:
                hi = mid
        return lo

    def payoff_lines(self) -> list[str]:
        mant, exp = f"{self.meas['recoil']:.0e}".split("e")
        text = self.man["payoff_text"].format(gain=self.meas["gain"], loss=self.meas["loss"],
                                              recoil=f"{mant} x 10^{int(exp)}")
        return [s.strip() for s in text.split("|")]

    def sim_state(self, name: str, sim_t: float):
        """Ship position relative to the planet, in the planet's local frame (x away from the Sun, y along its motion)."""
        r = self.meas["runs"][name]
        t = r["t"]
        sim_t = min(max(sim_t, t[0]), t[-1])
        st = np.array([np.interp(sim_t, t, r["st"][:, k]) for k in range(8)])
        p, pv, q, qv = st[0:2], st[2:4], st[4:6], st[6:8]
        r_hat = p / np.linalg.norm(p)
        t_hat = np.array([-r_hat[1], r_hat[0]])
        d = q - p
        v = qv - pv
        local = np.array([d @ r_hat, d @ t_hat])
        vloc = np.array([v @ r_hat, v @ t_hat])
        speed = float(np.interp(sim_t, t, r["sun_speed"]))
        return local, vloc, speed

    def trail(self, name: str, sim_t: float, every: int = 6) -> list[tuple[float, float]]:
        r = self.meas["runs"][name]
        t = r["t"]
        n = int(np.searchsorted(t, sim_t))
        st = r["st"][:n:every]
        if len(st) < 2:
            return []
        p, q = st[:, 0:2], st[:, 4:6]
        rn = np.linalg.norm(p, axis=1)
        r_hat = p / rn[:, None]
        t_hat = np.stack([-r_hat[:, 1], r_hat[:, 0]], axis=1)
        d = q - p
        return list(zip(np.sum(d * r_hat, axis=1), np.sum(d * t_hat, axis=1)))

    def scale_for(self, sim_t: float) -> float:
        man = self.man
        dmax = 0.0
        for name in ("behind", "front"):
            local, _, _ = self.sim_state(name, sim_t)
            dmax = max(dmax, float(np.linalg.norm(local)))
        half = (VIEW_BOT - VIEW_TOP) / 2
        return min(man["px_per_1000km_max"], man["zoom_fill"] * half / max(dmax / 1e6, 1e-9))

    def to_px(self, local: np.ndarray, s: float) -> tuple[float, float]:
        return VIEW_CX + local[0] / 1e6 * s, VIEW_CY - local[1] / 1e6 * s

    def ship(self, d: ImageDraw.ImageDraw, x: float, y: float, ang: float, col) -> None:
        pts = [(30, 0), (-18, -14), (-10, 0), (-18, 14)]
        c, s = math.cos(ang), math.sin(ang)
        poly = [(x + px * c - py * s, y - (px * s + py * c)) for px, py in pts]
        d.polygon(poly, fill=col)

    def draw_scene(self, t_video: float, title_on: bool) -> Image.Image:
        man, meas = self.man, self.meas
        sim_t = self.t_ca + pchip(self.xk, self.yk, t_video)
        s = self.scale_for(sim_t)
        img = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(img)
        # Planet with a glow, a legend arrow for its motion (up), a
        # pointer to the Sun (left), and a scale bar.
        R = man["planet_radius_km"] * 1000 / 1e6 * s
        Rd = max(R, 6.0)
        for k in range(6, 0, -1):
            a = 0.10 * k / 6
            col = tuple(int(PLANET_OUT[q] * a + BG[q] * (1 - a)) for q in range(3))
            rr = Rd + 16 * (7 - k)
            d.ellipse((VIEW_CX - rr, VIEW_CY - rr, VIEW_CX + rr, VIEW_CY + rr), fill=col)
        d.ellipse((VIEW_CX - Rd, VIEW_CY - Rd, VIEW_CX + Rd, VIEW_CY + Rd), fill=PLANET_OUT, outline=RIM, width=2)
        ax, ay0, ay1 = 120.0, VIEW_TOP + 150, VIEW_TOP + 50
        d.line([(ax, ay0), (ax, ay1)], fill=MUTED, width=4)
        d.polygon([(ax, ay1 - 14), (ax - 12, ay1 + 8), (ax + 12, ay1 + 8)], fill=MUTED)
        d.text((ax + 22, ay0 - 40), f"planet, {meas['V'] / 1000:.0f} km/s", font=self.font_tag, fill=MUTED, anchor="lm")
        d.text((80, VIEW_BOT - 110), "to the Sun", font=self.font_tag, fill=MUTED, anchor="lm")
        d.polygon([(40, VIEW_BOT - 110), (66, VIEW_BOT - 119), (66, VIEW_BOT - 101)], fill=MUTED)
        bar_km = 10_000
        for cand in (10_000, 50_000, 100_000, 500_000, 1_000_000):
            if cand / 1000 * s <= 600:
                bar_km = cand
        bar = bar_km / 1000 * s
        d.line([(80, VIEW_BOT - 30), (80 + bar, VIEW_BOT - 30)], fill=MUTED, width=3)
        for xx in (80, 80 + bar):
            d.line([(xx, VIEW_BOT - 40), (xx, VIEW_BOT - 20)], fill=MUTED, width=3)
        d.text((80 + bar / 2, VIEW_BOT - 58), f"{bar_km:,} km", font=self.font_tag, fill=MUTED, anchor="mm")
        # Trails and ships.
        cols = {"behind": GOLD, "front": WHITE}
        for name in ("behind", "front"):
            tr = self.trail(name, sim_t)
            if len(tr) > 1:
                pts = [self.to_px(np.array(p), s) for p in tr]
                dim = tuple(int(cols[name][q] * 0.55 + BG[q] * 0.45) for q in range(3))
                d.line(pts, fill=dim, width=3)
        for name in ("behind", "front"):
            local, vloc, speed = self.sim_state(name, sim_t)
            x, y = self.to_px(local, s)
            if -60 <= x <= W + 60 and VIEW_TOP - 60 <= y <= VIEW_BOT + 60:
                self.ship(d, x, y, math.atan2(vloc[1], vloc[0]), cols[name])
        d.rectangle((0, 0, W, VIEW_TOP - 1), fill=BG)
        d.rectangle((0, VIEW_BOT + 1, W, H), fill=BG)
        if not title_on:
            for name, cx in PANEL_X.items():
                _, _, speed = self.sim_state(name, sim_t)
                d.text((cx, LABEL_Y), self.labels[name], font=self.font_label, fill=cols[name], anchor="mm")
                d.text((cx, READ_Y), "speed relative to the Sun", font=self.font_small, fill=MUTED, anchor="mm")
                d.text((cx, VALUE_Y), f"{speed / 1000:.1f} km/s", font=self.font_read, fill=TEXT, anchor="mm")
            hrs = (sim_t - self.t_ca) / 3600
            if hrs < -0.05:
                clock = f"closest pass in {-hrs:.1f} hours"
            elif hrs <= 0.05:
                clock = "closest pass"
            else:
                clock = f"{hrs:.1f} hours after the closest pass"
            d.text((W / 2, CLOCK_Y), clock, font=self.font_small, fill=MUTED, anchor="mm")
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
                d.text((W / 2, 200 + j * 62), line, font=self.font_title, fill=shade_col(TEXT, a), anchor="mm")
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
    man = json.loads((ROOT / "projects/gravityassist/manifest.json").read_text())
    meas = measure(man)
    if "--measure-only" in sys.argv:
        return
    if "--frames" in sys.argv:
        times = [float(v) for v in sys.argv[sys.argv.index("--frames") + 1].split(",")]
        r = Renderer(man, meas)
        for tv in times:
            Image.fromarray(r.frame_at(int(round(tv * man["fps"])))).save(ROOT / f"media/gravityassist/smoke-{tv}.png")
        print("smoke frames: " + ", ".join(f"{tv}" for tv in times))
        return
    Renderer(man, meas).render(ROOT / "media/gravityassist/footage.mp4")


if __name__ == "__main__":
    main()
