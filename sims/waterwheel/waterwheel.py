#!/usr/bin/env python3
"""Lorenz water wheel: turn the tap up. Does the wheel spin faster?

A vertical wheel of radius R carries N cups on its rim. A tap at the top
pours Q kg/s into the cups nearest the top (a Gaussian lobe of width
sigma in angle, normalised over the cups so the total inflow is exactly
Q), every cup leaks at rate K per second, and the wheel turns under the
weight of the water against a bearing drag nu. With phi_i the angle of
cup i clockwise from the top and omega the wheel's angular speed:

    dm_i/dt = q(phi_i) - K m_i
    (I0 + R^2 sum m_i) domega/dt = g R sum m_i sin(phi_i) - nu omega
    dphi_i/dt = omega

so the heavy side drops. This is the Malkus wheel; its first Fourier
modes obey the Lorenz equations with b = 1. Two wheels start from the
same state (at rest, cups empty, cup 0 a small angle clockwise of the
top so the symmetry breaks the same way on both), one under a slow tap
and one under a tap pouring tap_ratio times the water. RK4 at a fixed
step. Deterministic, no seed. The video shows window_s seconds of wheel
time in 40 s, at a constant factor.

Measured and printed: the parameters and the Lorenz parameters they
imply; the slow wheel's steady speed, turn period, direction and
reversal count; the fast wheel's reversals in the window (count, times,
runs between them, net turns each way, peak speed) and in the next
window; a sensitivity run with the start angle moved by 1e-6 rad; a
half-step check; the on-screen text widths.

A reversal is counted when the wheel's speed crosses zero and then
reaches reversal_hold_rad_s in the new direction; its time is the zero
crossing. A wobble about zero that does not reach the hold speed in the
new direction does not count.

usage: waterwheel.py [--measure-only] [--frames t1,t2,...]
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
WATER = (96, 176, 240)
CUP = (160, 170, 184)
STRIP = (40, 47, 56)

# Layout: overlay at y 96 (captions.py), title rows at y 190/252/314 for
# the first seconds, two panels of 550 px (slow on top, fast below) each
# with its tap at the top centre and the wheel under it, captions at
# caption_y 0.75 (y 1440..1520), payoff card under them.
PANELS = {"slow": {"top": 336, "colour": TEAL}, "fast": {"top": 886, "colour": CORAL}}
PANEL_H = 550
SS = 2  # supersampling of the geometry layer
GEOM_Y0, GEOM_Y1 = 336, 1436
PAYOFF_Y = 1592.0
WHEEL_CY = 255  # wheel centre below the panel top
STRIP_X0, STRIP_X1, STRIP_Y, STRIP_H = 220, 860, 506, 20


def blend(col, a, base=BG):
    return tuple(int(round(c * a + b * (1 - a))) for c, b in zip(col, base))


def wrap(a):
    return (a + math.pi) % (2.0 * math.pi) - math.pi


def simulate(man: dict, taps: list[float], theta0s: list[float], duration: float, dt: float,
             keep_m: bool = True) -> dict:
    """Batched RK4 of B wheels. Returns per-step theta, omega and (optionally) cup masses."""
    g, R, N = man["g"], man["radius_m"], man["n_cups"]
    K, nu, I0, sig = man["leak_per_s"], man["drag_nu"], man["inertia_i0"], man["lobe_sigma_rad"]
    B = len(taps)
    Q = np.array(taps, dtype=np.float64)[:, None]
    base = 2.0 * math.pi * np.arange(N) / N
    th = np.array(theta0s, dtype=np.float64)
    om = np.zeros(B)
    m = np.zeros((B, N))
    n = int(round(duration / dt))
    TH = np.empty((B, n + 1))
    OM = np.empty((B, n + 1))
    M = np.empty((B, n + 1, N), dtype=np.float32) if keep_m else None

    def deriv(th, om, m):
        phi = th[:, None] + base[None, :]
        d = wrap(phi)
        w = np.exp(-0.5 * (d / sig) ** 2)
        q = Q * w / w.sum(1)[:, None]
        inertia = I0 + R * R * m.sum(1)
        dom = (g * R * (m * np.sin(phi)).sum(1) - nu * om) / inertia
        return om, dom, q - K * m

    for i in range(n + 1):
        TH[:, i] = th
        OM[:, i] = om
        if keep_m:
            M[:, i] = m
        if i == n:
            break
        k1 = deriv(th, om, m)
        k2 = deriv(th + 0.5 * dt * k1[0], om + 0.5 * dt * k1[1], m + 0.5 * dt * k1[2])
        k3 = deriv(th + 0.5 * dt * k2[0], om + 0.5 * dt * k2[1], m + 0.5 * dt * k2[2])
        k4 = deriv(th + dt * k3[0], om + dt * k3[1], m + dt * k3[2])
        th = th + dt / 6.0 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0])
        om = om + dt / 6.0 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1])
        m = m + dt / 6.0 * (k1[2] + 2 * k2[2] + 2 * k3[2] + k4[2])
    return {"theta": TH, "omega": OM, "m": M, "dt": dt, "n": n}


def reversals(om: np.ndarray, dt: float, hold: float) -> tuple[list[float], float | None]:
    """Reversal times (zero crossings, linearly interpolated) under the hold rule,
    and the time the first direction was established (first |omega| >= hold)."""
    big = np.nonzero(np.abs(om) >= hold)[0]
    if len(big) == 0:
        return [], None
    sg = np.where(om[big] > 0, 1, -1)
    change = np.nonzero(sg[1:] != sg[:-1])[0] + 1
    s = np.sign(om)
    cross = np.nonzero((s[1:] != s[:-1]) & (s[:-1] != 0))[0]  # crossing between cross and cross + 1
    times = []
    for c in change:
        i_big = big[c]
        k = np.searchsorted(cross, i_big) - 1
        i = cross[k]
        frac = om[i] / (om[i] - om[i + 1])
        times.append((i + frac) * dt)
    return times, big[0] * dt


def fmt_times(ts: list[float]) -> str:
    return ", ".join(f"{t:.1f}" for t in ts)


def lorenz_params(man: dict, Q: float) -> tuple[float, float, float]:
    """Rayleigh number r, Prandtl-like sigma and the Hopf threshold of the wheel's Lorenz form."""
    g, R, N, K, nu, I0, sig = (man["g"], man["radius_m"], man["n_cups"], man["leak_per_s"],
                               man["drag_nu"], man["inertia_i0"], man["lobe_sigma_rad"])
    base = 2.0 * math.pi * np.arange(N) / N
    c1 = 0.0
    n_ang = 720
    for k in range(n_ang):
        phi = wrap(base + 2.0 * math.pi * k / n_ang)
        w = np.exp(-0.5 * (phi / sig) ** 2)
        c1 += float((w * np.cos(phi)).sum() / w.sum())
    c1 /= n_ang
    r = g * R * Q * c1 / (nu * K * K)
    sigma = nu / (K * (I0 + R * R * Q / K))
    hopf = sigma * (sigma + 4.0) / (sigma - 2.0) if sigma > 2.0 else float("nan")
    return r, sigma, hopf


def measure(man: dict) -> dict:
    g, R, N = man["g"], man["radius_m"], man["n_cups"]
    K, nu, I0, sig = man["leak_per_s"], man["drag_nu"], man["inertia_i0"], man["lobe_sigma_rad"]
    Qs, ratio = man["tap_slow_kg_s"], man["tap_ratio"]
    Qf = ratio * Qs
    dt, Wd, th0, hold = man["dt_s"], man["window_s"], man["theta0_rad"], man["reversal_hold_rad_s"]
    factor = Wd / man["scene_duration"]
    eps = man["sensitivity_rad"]
    print(f"setup: a vertical wheel of radius {R * 100:g} cm with {N} buckets on its rim, g = {g:g} m/s^2; every bucket "
          f"leaks at {K:g} per second (a bucket loses {100 * (1 - math.exp(-K)):.1f} percent of its water each second); "
          f"the tap pours into the buckets nearest the top (Gaussian lobe of width {sig:g} rad, total inflow exact); "
          f"bearing drag {nu:g} N m s per rad; dry wheel inertia {I0:g} kg m^2 plus R^2 times the water; "
          f"slow tap {Qs * 1000:g} g/s, fast tap {ratio:g} times that = {Qf * 1000:g} g/s; both wheels start at rest "
          f"with empty buckets and bucket 0 {th0:g} rad clockwise of the top; RK4 at dt = {dt:g} s; window {Wd:g} s of "
          f"wheel time shown in {man['scene_duration']:g} s of video ({factor:g}x); deterministic, no seed")
    for name, Q in (("slow", Qs), ("fast", Qf)):
        r, sg, hopf = lorenz_params(man, Q)
        print(f"lorenz form, {name} tap: r = g R Q c1 / (nu K^2) = {r:.2f}, sigma = nu / (K I) = {sg:.2f}, b = 1; "
              f"steady rotation exists for r > 1 and is stable below the Hopf value sigma (sigma + 4) / (sigma - 2) = "
              f"{hopf:.2f}; closed-form steady speed K sqrt(r - 1) = {K * math.sqrt(max(r - 1, 0)):.4f} rad/s")
    print(f"reversal rule: a reversal is counted when omega crosses zero and then reaches {hold:g} rad/s in the "
          f"new direction; its time is the zero crossing; a wobble about zero that does not reach {hold:g} rad/s "
          f"the other way does not count; the first direction is set when |omega| first reaches {hold:g} rad/s")
    runs = simulate(man, [Qs, Qf, Qf], [th0, th0, th0 + eps], 2.0 * Wd, dt)
    nW = int(round(Wd / dt))
    out = {"dt": dt, "nW": nW, "factor": factor, "runs": runs}
    # Slow wheel.
    om_s, th_s = runs["omega"][0], runs["theta"][0]
    rev_s, t_dir_s = reversals(om_s[:nW + 1], dt, hold)
    rev_s2, _ = reversals(om_s, dt, hold)
    tail = om_s[nW - int(30.0 / dt):nW + 1]
    w_ss = float(tail.mean())
    settle = np.nonzero(np.abs(om_s[:nW + 1] - w_ss) > 0.05 * abs(w_ss))[0]
    t_settle = (settle[-1] + 1) * dt if len(settle) else 0.0
    last60 = om_s[nW - int(60.0 / dt):nW + 1]
    turns_s = (th_s[nW] - th_s[0]) / (2.0 * math.pi)
    print(f"slow wheel ({Qs * 1000:g} g/s): starts turning {'clockwise' if om_s[int(t_dir_s / dt)] > 0 else 'counterclockwise'} "
          f"(|omega| reaches {hold:g} rad/s at {t_dir_s:.1f} s); reversals in {Wd:g} s: {len(rev_s)}"
          f"{' (' + fmt_times(rev_s) + ' s)' if rev_s else ''}; in {2 * Wd:g} s: {len(rev_s2)}; steady speed "
          f"{w_ss:.4f} rad/s = {abs(w_ss) * 60 / (2 * math.pi):.2f} turns a minute (mean over the last 30 s of the window, "
          f"{'clockwise' if w_ss > 0 else 'counterclockwise'}), turn period {2 * math.pi / abs(w_ss):.2f} s; within 5 percent "
          f"of it from {t_settle:.1f} s; over the last 60 s the speed stays between {last60.min():.4f} and "
          f"{last60.max():.4f} rad/s (a slow wobble about the steady value, shrinking); peak speed {np.abs(om_s[:nW + 1]).max():.4f} rad/s at "
          f"{int(np.argmax(np.abs(om_s[:nW + 1]))) * dt:.1f} s; {turns_s:.2f} net turns in the window; speed at the end of "
          f"the window {om_s[nW]:.4f} rad/s")
    # Fast wheel.
    om_f, th_f = runs["omega"][1], runs["theta"][1]
    rev_f, t_dir_f = reversals(om_f[:nW + 1], dt, hold)
    rev_f2, _ = reversals(om_f, dt, hold)
    later = [t for t in rev_f2 if t > Wd]
    bounds = [t_dir_f] + rev_f
    runs_len = [b - a for a, b in zip(bounds[:-1], bounds[1:])]
    pos = om_f[:nW + 1].clip(min=0).sum() * dt / (2 * math.pi)
    neg = -om_f[:nW + 1].clip(max=0).sum() * dt / (2 * math.pi)
    i_peak = int(np.argmax(np.abs(om_f[:nW + 1])))
    print(f"fast wheel ({Qf * 1000:g} g/s): starts turning {'clockwise' if om_f[int(t_dir_f / dt)] > 0 else 'counterclockwise'} "
          f"(|omega| reaches {hold:g} rad/s at {t_dir_f:.1f} s); reversals in the {Wd:g} s window: {len(rev_f)}, at "
          f"{fmt_times(rev_f)} s of wheel time = {fmt_times([t / factor for t in rev_f])} s of video; runs one way "
          f"between them {fmt_times(runs_len)} s (first run from the start), longest {max(runs_len):.1f} s, shortest "
          f"{min(runs_len):.1f} s, and the last run from {rev_f[-1]:.1f} s to the end of the window ({Wd - rev_f[-1]:.1f} s, "
          f"still going); {pos:.2f} turns clockwise and {neg:.2f} counterclockwise in the window (net {pos - neg:+.2f}); "
          f"peak speed {abs(om_f[i_peak]):.4f} rad/s at {i_peak * dt:.1f} s = {abs(om_f[i_peak]) * 60 / (2 * math.pi):.2f} "
          f"turns a minute; speed at the end of the window {om_f[nW]:.4f} rad/s")
    print(f"fast wheel, next window ({Wd:g} to {2 * Wd:g} s): {len(later)} reversals at {fmt_times(later)} s; "
          f"{len(rev_f2)} in {2 * Wd:g} s; longest run in the second window "
          f"{max(b - a for a, b in zip([rev_f[-1]] + later, later + [2 * Wd])):.1f} s")
    out["rev_slow"], out["rev_fast"], out["t_dir_slow"], out["t_dir_fast"] = rev_s, rev_f, t_dir_s, t_dir_f
    out["w_slow"] = w_ss
    # Sensitivity: the start angle moved by eps.
    th_e = runs["theta"][2]
    diff = np.abs(th_e - th_f)
    idx = np.nonzero(diff > 0.1)[0]
    t_dep = idx[0] * dt if len(idx) else None
    rev_e, _ = reversals(runs["omega"][2][:nW + 1], dt, hold)
    idx2 = np.nonzero(diff > 1e-3)[0]
    print(f"sensitivity: the fast wheel restarted with the start angle moved by {eps:g} rad differs by 0.001 rad in "
          f"wheel angle from {idx2[0] * dt:.1f} s and by 0.1 rad from {t_dep:.1f} s; it reverses {len(rev_e)} times in "
          f"the window, at {fmt_times(rev_e)} s; the first reversal time that differs by more than 0.5 s: "
          + next((f"number {k + 1} ({a:.1f} against {b:.1f} s)" for k, (a, b) in enumerate(zip(rev_f, rev_e)) if abs(a - b) > 0.5), "none")
          + f"; the difference grows about {math.log(0.1 / eps) / t_dep:.4f} per second (e-folding every {t_dep / math.log(0.1 / eps):.1f} s)"
          + (f"; the slow wheel restarted the same way holds {w_ss:.4f} rad/s" if False else ""))
    # Half step.
    half = simulate(man, [Qs, Qf], [th0, th0], Wd, dt / 2.0, keep_m=False)
    om_hs, om_hf = half["omega"][0], half["omega"][1]
    nWh = half["n"]
    w_ss_h = float(om_hs[nWh - int(30.0 / (dt / 2)):nWh + 1].mean())
    rev_h, _ = reversals(om_hf, dt / 2.0, hold)
    depart = next((f"number {k + 1} ({a:.2f} against {b:.2f} s)" for k, (a, b) in enumerate(zip(rev_f, rev_h)) if abs(a - b) > 0.5), "none")
    print(f"check at half the step (dt = {dt / 2:g} s): slow wheel steady speed {w_ss_h:.4f} rad/s "
          f"({w_ss_h - w_ss:+.6f} against the full step); fast wheel reversals in the window: {len(rev_h)}, at "
          f"{fmt_times(rev_h)} s; largest difference against the full-step times over the window "
          f"{max((abs(a - b) for a, b in zip(rev_f, rev_h)), default=0.0):.3f} s; first reversal differing by more "
          f"than 0.5 s: {depart}")
    m_all = runs["m"][:2, :nW + 1]
    out["m_max"] = float(m_all.max())
    print(f"buckets: fullest bucket in the window {out['m_max'] * 1000:.1f} g (drawn full at {man['cup_full_kg'] * 1000:g} g); "
          f"total water on the slow wheel at the end of the window {runs['m'][0, nW].sum() * 1000:.1f} g "
          f"(Q / K = {Qs / K * 1000:g} g), on the fast wheel {runs['m'][1, nW].sum() * 1000:.1f} g (Q / K = {Qf / K * 1000:g} g)")
    return out


class Renderer:
    def __init__(self, man: dict, meas: dict):
        self.man, self.meas = man, meas
        self.fps = man["fps"]
        font = os.environ["SEED_ZERO_FONT"]
        self.font = ImageFont.truetype(font, 40)
        self.font_title = ImageFont.truetype(font, 56)
        self.font_read = ImageFont.truetype(font, 36)
        self.font_num = ImageFont.truetype(font, 48)
        self.font_small = ImageFont.truetype(font, 28)
        self.font_status = ImageFont.truetype(font, 32)
        self.first = None
        self.Rpx = float(man["wheel_radius_px"])
        self.factor = meas["factor"]
        self.rev_video = {"slow": [t / self.factor for t in meas["rev_slow"]],
                          "fast": [t / self.factor for t in meas["rev_fast"]]}
        self.taps = {"slow": man["tap_slow_kg_s"], "fast": man["tap_slow_kg_s"] * man["tap_ratio"]}
        self.idx = {"slow": 0, "fast": 1}
        om = meas["runs"]["omega"][:2, :meas["nW"] + 1]
        self.om_scale = float(np.abs(om).max())
        widths = {"overlay@34": (ImageFont.truetype(font, 34), man["overlay"])}
        for j, line in enumerate(man["title"].split("|")):
            widths[f"title line {j + 1}@56"] = (self.font_title, line)
        for name in PANELS:
            widths[f"label {name}@40"] = (self.font, man["labels"][name])
            widths[f"sublabel {name}@28"] = (self.font_small, man["sublabels"][name])
        widths["reversals@28"] = (self.font_small, "reversals")
        widths["counter@48"] = (self.font_num, "12")
        widths["speed@28"] = (self.font_small, "12.3 turns a minute")
        widths["status@32"] = (self.font_status, "turns back")
        widths["factor@28"] = (self.font_small, f"{self.factor:g}x speed")
        widths["clock@36"] = (self.font_read, "4:00")
        for j, line in enumerate(self.payoff_lines()):
            widths[f"payoff line {j + 1}@40"] = (self.font, line)
        print("text widths: " + ", ".join(f"{k} {f.getlength(s):.0f} px" for k, (f, s) in widths.items()))
        rf = self.rev_video["fast"]
        print(f"video: {man['scene_duration']:g} s at {self.fps} fps show {man['window_s']:g} s of wheel time "
              f"({self.factor:g}x); the fast wheel's reversals show at {fmt_times(rf)} s of video, the counter reads "
              f"{len(rf)} from {rf[-1]:.2f} s; the slow wheel's counter stays at {len(self.rev_video['slow'])}; "
              f"peak on-screen spin {self.om_scale * self.factor / (2 * math.pi):.2f} turns per second; "
              f"title to {man['title_until']:g} s; payoff card at {man['payoff_t']:g} s")

    def payoff_lines(self) -> list[str]:
        text = self.man["payoff_text"].format(n=len(self.meas["rev_fast"]), slow=len(self.meas["rev_slow"]))
        return [s.strip() for s in text.split("|")]

    def state(self, name: str, t: float) -> tuple[float, float, np.ndarray]:
        runs = self.meas["runs"]
        i = min(int(round(t * self.factor / runs["dt"])), self.meas["nW"])
        b = self.idx[name]
        return float(runs["theta"][b, i]), float(runs["omega"][b, i]), runs["m"][b, i]

    def draw_wheel(self, d: ImageDraw.ImageDraw, name: str, theta: float, omega: float, m: np.ndarray, t: float) -> None:
        man = self.man
        p = PANELS[name]
        col = p["colour"]
        top = (p["top"] - GEOM_Y0) * SS
        cx, cy = W / 2 * SS, top + WHEEL_CY * SS
        Rp = self.Rpx * SS
        N = man["n_cups"]
        # Tap: pipe and nozzle at the top centre.
        d.rectangle((cx - 7 * SS, top + 4 * SS, cx + 7 * SS, top + 32 * SS), fill=WIRE)
        d.rectangle((cx - 15 * SS, top + 30 * SS, cx + 15 * SS, top + 42 * SS), fill=blend(TEXT, 0.6))
        # Cups: pivot on the rim, body hanging below it, water level inside.
        cups = []
        for i in range(N):
            phi = theta + 2.0 * math.pi * i / N
            px = cx + Rp * math.sin(phi)
            py = cy - Rp * math.cos(phi)
            fill = min(1.0, float(m[i]) / man["cup_full_kg"])
            cups.append((wrap(phi), px, py, fill))
        # Stream: from the nozzle down to the water surface of the cup nearest the top.
        near = min(cups, key=lambda c: abs(c[0]))
        y_land = near[2] + 46 * SS - near[3] * 34 * SS
        half_w = max(2.0, self.taps[name] * man["stream_px_per_kg_s"]) * SS / 2.0
        y_top = top + 42 * SS
        d.rectangle((cx - half_w, y_top, cx + half_w, y_land), fill=blend(WATER, 0.85))
        # Falling texture: darker bands sliding down the stream (a function of video time only).
        period = 26 * SS
        phase = (t * 330.0 * SS) % period
        y = y_top - period + phase
        while y < y_land:
            y0, y1 = max(y_top, y), min(y_land, y + 7 * SS)
            if y1 > y0:
                d.rectangle((cx - half_w, y0, cx + half_w, y1), fill=blend(WATER, 0.55))
            y += period
        # Rim, spokes, hub.
        d.ellipse((cx - Rp, cy - Rp, cx + Rp, cy + Rp), outline=blend(col, 0.8), width=6 * SS)
        for k in range(man["n_spokes"]):
            a = theta + 2.0 * math.pi * k / man["n_spokes"]
            d.line((cx + 18 * SS * math.sin(a), cy - 18 * SS * math.cos(a), cx + Rp * math.sin(a), cy - Rp * math.cos(a)),
                   fill=WIRE, width=4 * SS)
        d.ellipse((cx - 20 * SS, cy - 20 * SS, cx + 20 * SS, cy + 20 * SS), fill=WIRE, outline=blend(col, 0.8), width=3 * SS)
        d.ellipse((cx - 5 * SS, cy - 5 * SS, cx + 5 * SS, cy + 5 * SS), fill=BG)
        for _, px, py, fill in cups:
            y0, y1 = py + 8 * SS, py + 48 * SS
            wt, wb = 24 * SS, 18 * SS
            d.line((px, py, px, y0), fill=CUP, width=2 * SS)
            if fill > 0.005:
                ys = y1 - 2 * SS - fill * 34 * SS
                f = (ys - y0) / (y1 - y0)
                wl = wt + (wb - wt) * f
                d.polygon([(px - wl, ys), (px + wl, ys), (px + wb + 1 * SS, y1 - 2 * SS), (px - wb - 1 * SS, y1 - 2 * SS)],
                          fill=blend(WATER, 0.3 + 0.7 * fill))
                # Leak: a short drip under the cup, longer the fuller the cup.
                d.line((px, y1, px, y1 + (8 + 16 * fill) * SS), fill=blend(WATER, 0.35 + 0.5 * fill), width=2 * SS)
            d.polygon([(px - wt, y0), (px + wt, y0), (px + wb, y1), (px - wb, y1)], outline=CUP, width=2 * SS)
            d.ellipse((px - 5 * SS, py - 5 * SS, px + 5 * SS, py + 5 * SS), fill=blend(col, 0.9))
        # Direction arrow around the hub, fading out as the wheel stops.
        a = min(1.0, abs(omega) / (2.0 * man["reversal_hold_rad_s"]))
        if a > 0.02:
            ra = 54 * SS
            acol = blend(WHITE, a)
            d.arc((cx - ra, cy - ra, cx + ra, cy + ra), 205, 335, fill=acol, width=5 * SS)
            end = math.radians(335 if omega > 0 else 205)
            ex, ey = cx + ra * math.cos(end), cy + ra * math.sin(end)
            # Tangent direction of travel at the arrow tip.
            tx, ty = (-math.sin(end), math.cos(end)) if omega > 0 else (math.sin(end), -math.cos(end))
            nx, ny = -ty, tx
            s = 13 * SS
            d.polygon([(ex + tx * s, ey + ty * s), (ex + nx * s * 0.7, ey + ny * s * 0.7), (ex - nx * s * 0.7, ey - ny * s * 0.7)], fill=acol)

    def draw_strip(self, d: ImageDraw.ImageDraw, name: str, t: float) -> None:
        p = PANELS[name]
        col = p["colour"]
        y0 = p["top"] + STRIP_Y
        d.line((STRIP_X0, y0, STRIP_X1, y0), fill=STRIP, width=2)
        d.line((STRIP_X0, y0 - STRIP_H, STRIP_X0, y0 + STRIP_H), fill=STRIP, width=2)
        runs = self.meas["runs"]
        b = self.idx[name]
        n_pts = int(t * self.fps) + 1
        if n_pts < 2:
            return
        steps = self.factor / self.fps / runs["dt"]
        idx = np.minimum((np.arange(n_pts) * steps).round().astype(int), self.meas["nW"])
        om = runs["omega"][b, idx]
        xs = STRIP_X0 + (STRIP_X1 - STRIP_X0) * np.arange(n_pts) / (self.man["scene_duration"] * self.fps)
        ys = y0 - STRIP_H * om / self.om_scale
        d.line(list(zip(xs.tolist(), ys.tolist())), fill=blend(col, 0.75), width=2)

    def draw_scene(self, t: float) -> Image.Image:
        man = self.man
        img = Image.new("RGB", (W, H), BG)
        layer = Image.new("RGB", (W * SS, (GEOM_Y1 - GEOM_Y0) * SS), BG)
        ld = ImageDraw.Draw(layer)
        states = {}
        for name in PANELS:
            theta, omega, m = self.state(name, t)
            states[name] = (theta, omega)
            self.draw_wheel(ld, name, theta, omega, m, t)
        img.paste(layer.reduce(SS), (0, GEOM_Y0))
        d = ImageDraw.Draw(img)
        tw = t * self.factor
        for name, p in PANELS.items():
            col = p["colour"]
            top = p["top"]
            theta, omega = states[name]
            revs = self.rev_video[name]
            count = sum(1 for r in revs if r <= t)
            since = t - revs[count - 1] if count else None
            d.text((40, top + 20), man["labels"][name], font=self.font, fill=col, anchor="lm")
            d.text((40, top + 64), man["sublabels"][name], font=self.font_small, fill=MUTED, anchor="lm")
            d.text((W - 40, top + 16), "reversals", font=self.font_small, fill=MUTED, anchor="rm")
            flash = since is not None and since < 0.5
            d.text((W - 40, top + 64), f"{count}", font=self.font_num, fill=WHITE if flash else col, anchor="rm")
            rpm = abs(omega) * 60.0 / (2.0 * math.pi)
            d.text((W - 40, top + 108), f"{rpm:.1f} turns a minute", font=self.font_small, fill=MUTED, anchor="rm")
            d.text((40, top + 512), f"{self.factor:g}x speed", font=self.font_small, fill=MUTED, anchor="lm")
            d.text((W - 40, top + 512), f"{int(tw // 60)}:{int(tw % 60):02d}", font=self.font_read, fill=TEXT, anchor="rm")
            word = ""
            if name == "fast" and since is not None and since < man["status_hold"]:
                word, wcol = "turns back", GOLD
            elif name == "slow" and self.meas["t_dir_slow"] is not None and t >= self.meas["t_dir_slow"] / self.factor + 1.0:
                word, wcol = "one way", col
            if word:
                d.text((W / 2 - self.Rpx - 40, top + WHEEL_CY), word, font=self.font_status, fill=wcol, anchor="rm")
            if man.get("trace", True):
                self.draw_strip(d, name, t)
        return img

    def live_frame(self, f: int) -> np.ndarray:
        man = self.man
        t = f / self.fps
        img = self.draw_scene(t)
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
    man = json.loads((ROOT / "projects/waterwheel/manifest.json").read_text())
    meas = measure(man)
    if "--measure-only" in sys.argv:
        return
    if "--frames" in sys.argv:
        times = [float(v) for v in sys.argv[sys.argv.index("--frames") + 1].split(",")]
        r = Renderer(man, meas)
        for tv in times:
            Image.fromarray(r.frame_at(int(round(tv * man["fps"])))).save(ROOT / f"media/waterwheel/smoke-{tv}.png")
        print("smoke frames: " + ", ".join(f"{tv}" for tv in times))
        return
    Renderer(man, meas).render(ROOT / "media/waterwheel/footage.mp4")


if __name__ == "__main__":
    main()
