#!/usr/bin/env python3
"""Double slit ripple tank: one slit makes a fan. What do two slits make?

A rectangular ripple tank seen from above. The water height u obeys the
2D scalar wave equation with a damping term in the sponge layers,

    u_tt + 2 sigma u_t = c^2 (u_xx + u_yy),

on a 1 mm grid with a fourth-order Laplacian (five points per axis) and
a leapfrog step (Courant number c dt / dx = 1/3, 60 steps per period);
the five rows around the wall use the second-order stencil with mirrored
(Neumann) values at the wall faces. Wave speed 0.2 m/s at
10 Hz, so the wavelength is 2.0 cm (20 cells). A quadratic sponge 4 cm
wide on all four edges absorbs whatever reaches them. A soft (additive)
plane-wave source on one row just inside the bottom sponge sends
A sin(omega t) up the tank, ramped over two periods; the wave it sends
down dies in the sponge. A wall one cell thick 14 cm up the tank is a
hard reflector (Neumann, no flow through it); its face is an absorbing
beach 3 cm deep, except in the slit columns, so the incoming ripples do
not bounce back and stand in front of it. Two panels, same tank, same
source: on top the wall has one slit 1 cm wide; below it has two slits
1 cm wide, 10 cm apart centre to centre. A screen line 40 cm past the
wall spans +-36 cm (the tank width less the side sponges), so it sees
angles to +-42 degrees. Deterministic, no seed.

Measured and printed: the incident amplitude and the standing-wave
ratio in front of the wall; the time-averaged intensity u^2 along the
screen over the last ten periods; its interior maxima and minima, their
positions and angles from the wall centre (theta = atan(x / 40 cm))
against the closed forms d sin theta = n lambda and (n + 1/2) lambda; the
counts of bright and dark bands; the dark-over-bright ratios; the
single-slit profile (peak at the centre, monotone fall, no minima); the
live counts over time and when they settle; the arrival times of the
wave at the wall and the screen; checks at half the grid step, over a
longer averaging window, at 30 and 35 s against 40 s, and on screens 20
and 30 cm from the wall; and the on-screen text widths.

usage: slits.py [--measure-only] [--frames t1,t2,...]
"""

from __future__ import annotations

import json
import math
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
WIRE = (70, 80, 94)
BEAM = (160, 170, 185)
WATER_LOW = (2, 6, 10)
WATER_FLAT = (16, 36, 44)
WATER_HIGH = (215, 245, 235)

# Layout: overlay at y 96..130 (compose), title rows at y 190/252 for the
# first seconds, two panels: a label row (38 px) then the tank (522 px =
# 58 cm at 9 px/cm) from y 334 (one slit) and 904 (two slits); the tank
# is 720 px wide (80 cm), centred; captions at caption_y 0.75 (y
# 1440..1520) below the second tank (ends at 1426); payoff card from 1592.
PANEL_TOPS = (296, 866)
LABEL_H = 38
TANK_X0 = 180
STRIP_H = 32
PAYOFF_Y = 1592.0
PANELS = [
    {"name": "one", "label": "one slit", "slits": [0.0], "colour": GOLD},
    {"name": "two", "label": "two slits, 10 cm apart", "slits": [-5.0, 5.0], "colour": CORAL},
]


def blend(col, a, base=BG):
    return tuple(int(round(c * a + b * (1 - a))) for c, b in zip(col, base))


def smoothstep(x: float) -> float:
    x = min(1.0, max(0.0, x))
    return x * x * (3.0 - 2.0 * x)


class Tank:
    """One ripple tank: the wave field, the sponges, the wall with its slits, and the screen rings."""

    def __init__(self, man: dict, slits_cm: list[float], dx_mm: float, substeps: int):
        self.man = man
        self.dx_mm = dx_mm
        cpc = 10.0 / dx_mm
        self.cpc = cpc
        w, h = man["tank_w_cm"], man["tank_h_cm"]
        nx, ny = int(round(w * cpc)), int(round(h * cpc))
        self.nx, self.ny = nx, ny
        self.frame_real = man["speed"] / man["fps"]
        self.substeps = substeps
        self.dt = self.frame_real / substeps
        c = man["c_m_s"]
        self.courant = c * self.dt / (dx_mm * 1e-3)
        self.C2 = np.float32(self.courant ** 2)
        self.period = 1.0 / man["freq_hz"]
        self.omega = 2.0 * math.pi * man["freq_hz"]
        self.tau0 = man["source_t0"] * man["speed"]
        self.ramp = man["ramp_periods"] * self.period
        self.amp = man["source_amp"]
        self.ref = man["colour_ref"]
        xs = (np.arange(nx) + 0.5) / cpc - w / 2.0
        ys = (np.arange(ny) + 0.5) / cpc
        self.xs, self.ys = xs, ys
        X, Y = np.meshgrid(xs, ys)
        sp = man["sponge_cm"]
        depth = np.maximum.reduce([
            np.clip(sp - (X + w / 2.0), 0.0, None),
            np.clip(sp - (w / 2.0 - X), 0.0, None),
            np.clip(sp - Y, 0.0, None),
            np.clip(sp - (h - Y), 0.0, None),
        ])
        sigma = man["sponge_rate"] * (depth / sp) ** 2
        wy = man["wall_y_cm"]
        wall_rows = np.where((ys >= wy) & (ys < wy + 0.1))[0]
        slit_cols = np.zeros(nx, dtype=bool)
        for xc in slits_cm:
            slit_cols |= np.abs(xs - xc) < man["slit_w_cm"] / 2.0
        self.slit_cols = slit_cols
        self.wall_rows = wall_rows
        b = man["beach_cm"]
        beach = (Y >= wy - b) & (Y < wy) & (~slit_cols)[None, :]
        sig_b = man["beach_rate"] * np.clip((Y - (wy - b)) / b, 0.0, 1.0) ** 2
        sigma = np.where(beach, np.maximum(sigma, sig_b), sigma)
        sdt = sigma * self.dt
        self.a1 = (1.0 / (1.0 + sdt)).astype(np.float32)
        self.a2 = (1.0 - sdt).astype(np.float32)
        self.corr = (~slit_cols).astype(np.float32)
        self.wall_open = slit_cols.astype(np.float32)
        self.j_lo, self.j_hi = int(wall_rows[0]) - 1, int(wall_rows[-1]) + 1
        # Slit cells on the wall row whose side neighbour is a wall cell mirror their own value there.
        side = np.zeros(nx, dtype=np.float32)
        side[1:] += (~slit_cols[:-1]) & slit_cols[1:]
        side[:-1] += (~slit_cols[1:]) & slit_cols[:-1]
        self.side = side
        self.band = slice(int(wall_rows[0]) - 2, int(wall_rows[-1]) + 3)
        self.j_src = int(np.argmin(np.abs(ys - man["source_y_cm"])))
        self.wall_mid = wy + 0.05
        S = man["screen_cm"]
        self.S = S
        self.j_screen = int(np.argmin(np.abs(ys - (self.wall_mid + S))))
        self.j_checks = [int(np.argmin(np.abs(ys - (self.wall_mid + s)))) for s in man["check_screens_cm"]]
        self.j_front = int(np.argmin(np.abs(ys - (wy - b - 0.5))))
        self.span = slice(int(np.searchsorted(xs, -(w / 2.0 - sp))), int(np.searchsorted(xs, w / 2.0 - sp)))
        self.i_centre = int(np.argmin(np.abs(xs)))
        self.i_end = int(np.argmin(np.abs(xs - (w / 2.0 - sp - 1.0))))
        self.env_rows = slice(int(np.searchsorted(ys, 5.0)), int(np.searchsorted(ys, 10.0)))
        self.env_cols = slice(int(np.searchsorted(xs, -30.0)), int(np.searchsorted(xs, -20.0)))
        self.u = np.zeros((ny + 4, nx + 4), dtype=np.float32)
        self.up = np.zeros_like(self.u)
        self.nw = np.zeros_like(self.u)
        self.L = np.zeros((ny, nx), dtype=np.float32)
        self.tmp = np.zeros((ny, nx), dtype=np.float32)
        self.k = 0
        self.live_steps = int(round(man["avg_periods"] * self.period / self.dt))
        self.meas_steps = int(round(man["measure_periods"] * self.period / self.dt))
        self.long_steps = int(round(man["long_periods"] * self.period / self.dt))
        self.period_steps = int(round(self.period / self.dt))
        self.hist = np.zeros((1 + len(self.j_checks), self.long_steps, nx), dtype=np.float32)
        self.live_sum = np.zeros(nx, dtype=np.float64)
        self.env: np.ndarray | None = None
        self.arrive: dict[str, float | None] = {"wall": None, "centre": None, "end": None}

    def source(self, tau: float) -> float:
        if tau < self.tau0:
            return 0.0
        return self.amp * smoothstep((tau - self.tau0) / self.ramp) * math.sin(self.omega * (tau - self.tau0))

    def step(self) -> None:
        u, up, nw = self.u, self.up, self.nw
        c = u[2:-2, 2:-2]
        L, tmp = self.L, self.tmp
        # Fourth-order Laplacian: (16 (N + S + E + W) - (NN + SS + EE + WW) - 60 c) / 12.
        np.add(u[3:-1, 2:-2], u[1:-3, 2:-2], out=L)
        L += u[2:-2, 3:-1]
        L += u[2:-2, 1:-3]
        L *= np.float32(16.0)
        np.add(u[4:, 2:-2], u[:-4, 2:-2], out=tmp)
        tmp += u[2:-2, 4:]
        tmp += u[2:-2, :-4]
        L -= tmp
        np.multiply(c, np.float32(60.0), out=tmp)
        L -= tmp
        L *= np.float32(1.0 / 12.0)
        # The band around the wall: second-order stencil with mirrored (Neumann) values at the wall faces.
        b = self.band
        Lb = u[3:-1, 2:-2][b] + u[1:-3, 2:-2][b] + u[2:-2, 3:-1][b] + u[2:-2, 1:-3][b] - np.float32(4.0) * c[b]
        L[b] = Lb
        L[self.j_lo] += self.corr * c[self.j_lo]
        L[self.j_hi] += self.corr * c[self.j_hi]
        for j in self.wall_rows:
            L[j] += self.side * c[j]
        n = nw[2:-2, 2:-2]
        np.multiply(up[2:-2, 2:-2], self.a2, out=n)
        np.multiply(c, np.float32(2.0), out=tmp)
        np.subtract(tmp, n, out=n)
        np.multiply(L, self.C2, out=tmp)
        n += tmp
        n *= self.a1
        for j in self.wall_rows:
            n[j] *= self.wall_open
        self.k += 1
        tau = self.k * self.dt
        n[self.j_src] += np.float32(self.source(tau))
        self.up, self.u, self.nw = u, nw, up
        # Screen rings and the live running sum.
        k = self.k - 1
        slot = k % self.long_steps
        if k >= self.live_steps:
            self.live_sum -= self.hist[0, (k - self.live_steps) % self.long_steps]
        row = n[self.j_screen]
        np.multiply(row, row, out=self.hist[0, slot])
        self.live_sum += self.hist[0, slot]
        for m, j in enumerate(self.j_checks):
            r = n[j]
            np.multiply(r, r, out=self.hist[m + 1, slot])
        if self.env is not None:
            np.maximum(self.env, np.abs(n[self.env_rows, self.env_cols]), out=self.env)

    def start_envelope(self) -> None:
        self.env = np.zeros((self.env_rows.stop - self.env_rows.start, self.env_cols.stop - self.env_cols.start), dtype=np.float32)

    def field(self) -> np.ndarray:
        return self.u[2:-2, 2:-2]

    def live_profile(self) -> np.ndarray:
        return self.live_sum / max(1, min(self.k, self.live_steps))

    def window_profile(self, ring: int, steps: int) -> np.ndarray:
        steps = min(steps, self.k)
        idx = (np.arange(self.k - steps, self.k)) % self.long_steps
        return self.hist[ring, idx].astype(np.float64).mean(axis=0)

    def check_arrival(self, t_video: float) -> None:
        f = self.field()
        thr = 0.02 * self.ref
        if self.arrive["wall"] is None and np.abs(f[self.j_front]).max() > thr:
            self.arrive["wall"] = t_video
        if self.arrive["centre"] is None and abs(f[self.j_screen, self.i_centre]) > thr:
            self.arrive["centre"] = t_video
        if self.arrive["end"] is None and abs(f[self.j_screen, self.i_end]) > thr:
            self.arrive["end"] = t_video


def extrema(P: np.ndarray, thr: float) -> tuple[list[tuple[int, int]], float]:
    """Interior maxima (+1) and minima (-1) of P with persistence at least thr; leading and trailing minima dropped."""
    n = len(P)
    if n < 3:
        return [], 0.0
    left, right = P[:-2], P[2:]
    mid = P[1:-1]
    is_max = (mid > left) & (mid >= right)
    is_min = (mid < left) & (mid <= right)
    idx = np.where(is_max | is_min)[0] + 1
    ext: list[list[int]] = []
    for i in idx:
        kind = 1 if is_max[i - 1] else -1
        if ext and ext[-1][1] == kind:
            if (kind == 1 and P[i] > P[ext[-1][0]]) or (kind == -1 and P[i] < P[ext[-1][0]]):
                ext[-1] = [int(i), kind]
        else:
            ext.append([int(i), kind])
    pruned = 0.0
    while len(ext) >= 2:
        diffs = [abs(P[ext[m][0]] - P[ext[m + 1][0]]) for m in range(len(ext) - 1)]
        m = int(np.argmin(diffs))
        if diffs[m] >= thr:
            break
        pruned = max(pruned, float(diffs[m]))
        del ext[m:m + 2]
    while ext and ext[0][1] == -1:
        ext.pop(0)
    while ext and ext[-1][1] == -1:
        ext.pop()
    return [(i, k) for i, k in ext], pruned


def refine(P: np.ndarray, i: int) -> float:
    if 0 < i < len(P) - 1:
        den = P[i - 1] - 2.0 * P[i] + P[i + 1]
        if den != 0.0:
            return i + 0.5 * (P[i - 1] - P[i + 1]) / den
    return float(i)


def profile_stats(P_full: np.ndarray, tank: Tank, dist_cm: float, man: dict) -> dict:
    """Extrema of the smoothed screen profile over the screen span, in cm and degrees from the wall centre."""
    xs = tank.xs[tank.span]
    P = P_full[tank.span]
    k = max(1, int(round(man["smooth_mm"] / tank.dx_mm)))
    if k % 2 == 0:
        k += 1
    Ps = np.convolve(P, np.ones(k) / k, mode="same")
    pmax = float(Ps.max())
    floor = man["count_floor"] * tank.ref ** 2
    if pmax <= floor:
        return {"bright": 0, "dark": 0, "maxima": [], "minima": [], "ripple": 0.0, "pmax": pmax, "smooth": Ps}
    ext, pruned = extrema(Ps, man["band_threshold"] * pmax)
    dxc = 1.0 / tank.cpc
    out_max, out_min = [], []
    for j, (i, kind) in enumerate(ext):
        pos = refine(Ps, i)
        x = xs[0] + pos * dxc
        ang = math.degrees(math.atan2(x, dist_cm))
        val = float(Ps[i])
        if kind == 1:
            out_max.append({"x": x, "deg": ang, "val": val})
        else:
            lo = min(Ps[ext[j - 1][0]], Ps[ext[j + 1][0]])
            out_min.append({"x": x, "deg": ang, "val": val, "ratio": val / lo if lo > 0 else float("nan")})
    return {"bright": len(out_max), "dark": len(out_min), "maxima": out_max, "minima": out_min,
            "ripple": pruned / pmax, "pmax": pmax, "smooth": Ps}


def run_tank(man: dict, slits: list[float], dx_mm: float, substeps: int, t_end: float, keep: bool = False) -> dict:
    """Step one tank through the video frames up to t_end and collect the measurements (the pool entry point)."""
    tank = Tank(man, slits, dx_mm, substeps)
    fps = man["fps"]
    total = int(round(t_end * fps))
    counts: list[tuple[int, int]] = []
    snaps: dict[float, dict] = {}
    checks = {int(round(t * fps)): t for t in man["steady_checks"]}
    total_steps = total * substeps
    for f in range(total + 1):
        if f > 0:
            if tank.k == total_steps - tank.period_steps:
                tank.start_envelope()
            for _ in range(substeps):
                if tank.k == total_steps - tank.period_steps:
                    tank.start_envelope()
                tank.step()
        tank.check_arrival(f / fps)
        st = profile_stats(tank.live_profile(), tank, tank.S, man)
        counts.append((st["bright"], st["dark"]))
        if f in checks:
            snaps[checks[f]] = profile_stats(tank.window_profile(0, tank.meas_steps), tank, tank.S, man)
    P10 = tank.window_profile(0, tank.meas_steps)
    P20 = tank.window_profile(0, tank.long_steps)
    res = {
        "counts": counts,
        "snaps": snaps,
        "final": profile_stats(P10, tank, tank.S, man),
        "long": profile_stats(P20, tank, tank.S, man),
        "checks": {s: profile_stats(tank.window_profile(m + 1, tank.meas_steps), tank, s, man)
                   for m, s in enumerate(man["check_screens_cm"])},
        "P10": P10,
        "xs": tank.xs,
        "span": (tank.span.start, tank.span.stop),
        "arrive": tank.arrive,
        "env": tank.env.max(axis=1) if tank.env is not None else None,
        "centre": float(P10[tank.i_centre]),
        "dx_mm": dx_mm, "dt": tank.dt, "courant": tank.courant, "nx": tank.nx, "ny": tank.ny,
        "steps": tank.k, "live_steps": tank.live_steps, "meas_steps": tank.meas_steps, "long_steps": tank.long_steps,
    }
    if keep:
        res["tank"] = tank
    return res


def fmt_ext(items: list[dict], nd: int = 2) -> str:
    return ", ".join(f"{e['x']:+.{nd}f} cm ({e['deg']:+.2f} deg)" for e in items)


def settle_time(counts: list[tuple[int, int]], fps: int) -> tuple[float, tuple[int, int], list[tuple[float, int, int]]]:
    final = counts[-1]
    f_settle = len(counts) - 1
    while f_settle > 0 and counts[f_settle - 1] == final:
        f_settle -= 1
    changes = []
    last = None
    for f, cnt in enumerate(counts):
        if cnt != last:
            changes.append((f / fps, cnt[0], cnt[1]))
            last = cnt
    return f_settle / fps, final, changes


def measure(man: dict) -> dict:
    c, f0, lam = man["c_m_s"], man["freq_hz"], man["c_m_s"] / man["freq_hz"] * 100.0
    d, a, S = man["slit_sep_cm"], man["slit_w_cm"], man["screen_cm"]
    w, h, sp = man["tank_w_cm"], man["tank_h_cm"], man["sponge_cm"]
    fps, speed = man["fps"], man["speed"]
    probe = Tank(man, [0.0], man["dx_mm"], man["substeps"])
    span_cm = w / 2.0 - sp
    span_deg = math.degrees(math.atan2(span_cm, S))
    print(f"setup: ripple tank {w:g} x {h:g} cm seen from above, 2D wave equation u_tt + 2 sigma u_t = c^2 (u_xx + u_yy) "
          f"at c = {c:g} m/s and {f0:g} Hz (wavelength {lam:g} cm), grid {man['dx_mm']:g} mm ({probe.nx} x {probe.ny} cells, "
          f"{lam * probe.cpc:.0f} per wavelength), fourth-order Laplacian (second order with mirrored values in the five rows "
          f"around the wall), leapfrog at dt = {probe.dt * 1000:.4f} ms (Courant "
          f"{probe.courant:.4f}, {probe.period_steps} steps per period, {man['substeps']} steps per video frame); a quadratic "
          f"sponge {sp:g} cm wide on all four edges (rate {man['sponge_rate']:g}/s); a soft plane-wave source on the row at "
          f"y = {man['source_y_cm']:g} cm ramped over {man['ramp_periods']} periods from {man['source_t0']:g} s of the "
          f"video; a hard (Neumann) wall 1 mm thick at y = {man['wall_y_cm']:g} cm with an absorbing beach {man['beach_cm']:g} cm "
          f"deep on its face (rate {man['beach_rate']:g}/s) except in the slit columns; top panel one slit {a:g} cm wide at "
          f"the centre, bottom panel two slits {a:g} cm wide {d:g} cm apart; screen line {S:g} cm past the wall spanning "
          f"+-{span_cm:g} cm (+-{span_deg:.1f} degrees); time-lapse at {1 / speed:g}x slow motion ({speed:g} s of wave per "
          f"video second, {speed * man['scene_duration']:g} s of wave in the {man['scene_duration']:g} s scene); "
          f"deterministic, no seed")
    bright_cf = [math.degrees(math.asin(n * lam / d)) for n in range(1, 4) if n * lam / d < 1.0]
    dark_cf = [math.degrees(math.asin((n + 0.5) * lam / d)) for n in range(0, 5) if (n + 0.5) * lam / d < 1.0]
    n_b = 1 + 2 * sum(1 for t in bright_cf if t < span_deg)
    n_d = 2 * sum(1 for t in dark_cf if t < span_deg)
    print(f"closed forms: two slits {d:g} cm apart at wavelength {lam:g} cm: bright where d sin theta = n lambda, "
          + ", ".join(f"{t:.2f}" for t in bright_cf) + " degrees (positions on the screen "
          + ", ".join(f"{S * math.tan(math.radians(t)):.2f}" for t in bright_cf) + " cm); dark where d sin theta = "
          f"(n + 1/2) lambda, " + ", ".join(f"{t:.2f}" for t in dark_cf) + " degrees (positions "
          + ", ".join(f"{S * math.tan(math.radians(t)):.2f}" for t in dark_cf) + f" cm); on a screen spanning "
          f"+-{span_deg:.1f} degrees that is {n_b} bright bands (the centre plus {(n_b - 1) // 2} each side) and {n_d} dark "
          f"bands between them; one slit {a:g} cm wide: the first dark direction needs sin theta = lambda / a = "
          f"{lam / a:g}, over one, so no dark band anywhere: one smooth fan; the wave crosses the {man['wall_y_cm'] - man['source_y_cm']:g} cm "
          f"from the source to the wall in {(man['wall_y_cm'] - man['source_y_cm']) / (100 * c) / speed:.1f} s of video and "
          f"the {S:g} cm from the wall to the screen centre in {S / (100 * c) / speed:.1f} s more")
    jobs = {
        "one": (man, PANELS[0]["slits"], man["dx_mm"], man["substeps"], man["scene_duration"]),
        "two": (man, PANELS[1]["slits"], man["dx_mm"], man["substeps"], man["scene_duration"]),
        "two_half": (man, PANELS[1]["slits"], man["dx_mm"] / 2.0, 2 * man["substeps"], man["check_until"]),
    }
    with ProcessPoolExecutor(max_workers=len(jobs)) as pool:
        futures = {name: pool.submit(run_tank, *args) for name, args in jobs.items()}
        runs = {name: fut.result() for name, fut in futures.items()}
    out = {"runs": runs}
    one, two = runs["one"], runs["two"]
    for name, run in (("one", one), ("two", two)):
        env = run["env"]
        swr = float(env.max() / env.min())
        r = (swr - 1.0) / (swr + 1.0)
        arr = run["arrive"]
        print(f"{name}: incident wave amplitude {env.max():.4f} (source amplitude {man['source_amp']:g}) measured 5 to 10 cm "
              f"up the tank over the last period; envelope min {env.min():.4f}, standing-wave ratio {swr:.3f}, so the beach "
              f"sends back {100 * r:.1f}% of the amplitude; the wave reaches the wall at {arr['wall']:.2f} s of the video, "
              f"the screen centre at {arr['centre']:.2f} s and the screen end (35 cm off axis) at {arr['end']:.2f} s")
    st = two["final"]
    print(f"two slits, screen at {S:g} cm, intensity u^2 averaged over the last {man['measure_periods']} periods at "
          f"{man['scene_duration']:g} s: {st['bright']} bright bands at " + fmt_ext(st["maxima"]) +
          f"; {st['dark']} dark bands at " + fmt_ext(st["minima"]) + "; dark over bright " +
          ", ".join(f"{m['ratio']:.4f}" for m in st["minima"]) + f" (largest {max(m['ratio'] for m in st['minima']):.4f}); "
          f"band heights as a fraction of the centre " + ", ".join(f"{m['val'] / st['pmax']:.3f}" for m in st["maxima"]) +
          f"; the largest pruned ripple {100 * st['ripple']:.2f}% of the peak")
    pos = sorted(st["maxima"], key=lambda e: e["deg"])
    cen = (len(pos) - 1) // 2
    meas_b = [abs(pos[cen + n]["deg"]) for n in range(1, cen + 1)]
    meas_b_l = [abs(pos[cen - n]["deg"]) for n in range(1, cen + 1)]
    mins = sorted(st["minima"], key=lambda e: e["deg"])
    half = len(mins) // 2
    meas_d = [abs(mins[half + n]["deg"]) for n in range(0, half)]
    meas_d_l = [abs(mins[half - 1 - n]["deg"]) for n in range(0, half)]
    print("two slits against the closed forms: bright right " + ", ".join(f"{m:.2f}" for m in meas_b) + " and left " +
          ", ".join(f"{m:.2f}" for m in meas_b_l) + " degrees against " + ", ".join(f"{t:.2f}" for t in bright_cf[:cen]) +
          " (largest difference " + f"{max(abs(m - t) for m, t in zip(meas_b + meas_b_l, bright_cf[:cen] * 2)):.2f} degrees); "
          "dark right " + ", ".join(f"{m:.2f}" for m in meas_d) + " and left " + ", ".join(f"{m:.2f}" for m in meas_d_l) +
          " degrees against " + ", ".join(f"{t:.2f}" for t in dark_cf[:half]) + " (largest difference "
          f"{max(abs(m - t) for m, t in zip(meas_d + meas_d_l, dark_cf[:half] * 2)):.2f} degrees); the first dark band "
          f"{meas_d[0]:.2f} degrees off centre, {mins[half]['x']:.2f} cm along the screen")
    so = one["final"]
    P1 = so["smooth"]
    xs1 = one["xs"][one["span"][0]:one["span"][1]]
    peak_i = int(np.argmax(P1))
    right = P1[peak_i:]
    left = P1[:peak_i + 1][::-1]
    mono_r = bool(np.all(np.diff(right) <= 0.0))
    mono_l = bool(np.all(np.diff(left) <= 0.0))
    rise_r = float(np.max(np.diff(right)) / P1.max()) if len(right) > 1 else 0.0
    rise_l = float(np.max(np.diff(left)) / P1.max()) if len(left) > 1 else 0.0
    top = xs1[P1 >= 0.99 * P1.max()]
    samples = [0.0, 10.0, 20.0, 30.0, 35.0]
    vals = [float(np.interp(x, xs1, P1) / P1.max()) for x in samples]
    valsl = [float(np.interp(-x, xs1, P1) / P1.max()) for x in samples]
    print(f"one slit, screen at {S:g} cm, same average: {so['bright']} bright band, a flat top within 1% of the peak from "
          f"{top.min():+.1f} to {top.max():+.1f} cm ({math.degrees(math.atan2(top.min(), S)):+.1f} to "
          f"{math.degrees(math.atan2(top.max(), S)):+.1f} degrees); {so['dark']} dark bands; the profile "
          f"falls from the peak to the screen ends {'without a single rise' if mono_r and mono_l else 'with rises of at most ' + f'{100 * max(rise_r, rise_l):.3f}% of the peak per mm'}; "
          f"the largest pruned ripple {100 * so['ripple']:.2f}% of the peak; intensity as a fraction of the peak at "
          + ", ".join(f"{x:g} cm {v:.3f}" for x, v in zip(samples, vals)) + " to the right and "
          + ", ".join(f"{v:.3f}" for v in valsl) + " to the left")
    tot1 = float(one["P10"][one["span"][0]:one["span"][1]].sum())
    tot2 = float(two["P10"][two["span"][0]:two["span"][1]].sum())
    print(f"totals along the screen: two slits let through {tot2 / tot1:.3f} times the summed intensity of one slit, and the "
          f"centre of the screen is {two['centre'] / one['centre']:.3f} times as bright (two waves in step: amplitude twice, "
          f"intensity four times); transmitted amplitude at the screen centre {math.sqrt(2 * two['centre']):.4f} (two slits) "
          f"and {math.sqrt(2 * one['centre']):.4f} (one slit) against the incident {two['env'].max():.4f}")
    for name, run in (("one", one), ("two", two)):
        t_set, final, changes = settle_time(run["counts"], fps)
        print(f"{name}: live counts (bright, dark) from the {man['avg_periods']}-period running average: " +
              "; ".join(f"{t:.2f} s -> {b}, {dk}" for t, b, dk in changes[:14]) +
              (f"; ... {len(changes)} changes" if len(changes) > 14 else "") +
              f"; final {final[0]}, {final[1]} from {t_set:.2f} s to the end")
        out[name + "_settle"] = t_set
        out[name + "_final"] = final
    # Steadiness: the extrema at the check times against the end.
    for t_chk, snap in sorted(two["snaps"].items()):
        ends = two["final"]
        if snap["bright"] == ends["bright"] and snap["dark"] == ends["dark"]:
            dmax = max(abs(a["deg"] - b["deg"]) for a, b in zip(sorted(snap["maxima"], key=lambda e: e["deg"]), sorted(ends["maxima"], key=lambda e: e["deg"])))
            dmin = max(abs(a["deg"] - b["deg"]) for a, b in zip(sorted(snap["minima"], key=lambda e: e["deg"]), sorted(ends["minima"], key=lambda e: e["deg"])))
            print(f"check at {t_chk:g} s of the video (two slits, {man['measure_periods']}-period average): the same "
                  f"{snap['bright']} bright and {snap['dark']} dark bands, angles within {dmax:.2f} (bright) and {dmin:.2f} "
                  f"(dark) degrees of the {man['scene_duration']:g} s values")
        else:
            print(f"check at {t_chk:g} s of the video (two slits): {snap['bright']} bright and {snap['dark']} dark bands "
                  f"against {ends['bright']} and {ends['dark']} at the end")
    lg = two["long"]
    dmax = max(abs(a["deg"] - b["deg"]) for a, b in zip(sorted(lg["maxima"], key=lambda e: e["deg"]), sorted(st["maxima"], key=lambda e: e["deg"])))
    dmin = max(abs(a["deg"] - b["deg"]) for a, b in zip(sorted(lg["minima"], key=lambda e: e["deg"]), sorted(st["minima"], key=lambda e: e["deg"])))
    print(f"check over a longer window ({man['long_periods']} periods): {lg['bright']} bright and {lg['dark']} dark bands, "
          f"angles within {dmax:.2f} and {dmin:.2f} degrees of the {man['measure_periods']}-period values; dark over bright "
          f"largest {max(m['ratio'] for m in lg['minima']):.4f}")
    hf = runs["two_half"]["final"]
    dmax = max(abs(a["deg"] - b["deg"]) for a, b in zip(sorted(hf["maxima"], key=lambda e: e["deg"]), sorted(st["maxima"], key=lambda e: e["deg"])))
    dmin = max(abs(a["deg"] - b["deg"]) for a, b in zip(sorted(hf["minima"], key=lambda e: e["deg"]), sorted(st["minima"], key=lambda e: e["deg"])))
    print(f"check at half the grid step ({hf and runs['two_half']['dx_mm']:g} mm, dt {runs['two_half']['dt'] * 1000:.4f} ms, "
          f"{runs['two_half']['nx']} x {runs['two_half']['ny']} cells, run to {man['check_until']:g} s of the video): "
          f"{hf['bright']} bright bands at " + fmt_ext(hf["maxima"]) + f"; {hf['dark']} dark bands at " + fmt_ext(hf["minima"]) +
          f"; angles within {dmax:.2f} (bright) and {dmin:.2f} (dark) degrees of the full-step run; dark over bright largest "
          f"{max(m['ratio'] for m in hf['minima']):.4f}")
    def by_order(items: list[dict]) -> dict[int, dict]:
        """Bands keyed by their order from the centre (negative on the left)."""
        pos = sorted(items, key=lambda e: e["deg"])
        cen = min(range(len(pos)), key=lambda m: abs(pos[m]["deg"]))
        return {m - cen: e for m, e in enumerate(pos)}

    ref_max = by_order(st["maxima"])
    for s_chk, ck in sorted(two["checks"].items()):
        chk_max = by_order(ck["maxima"])
        ratios = [(n, chk_max[n]["x"] / ref_max[n]["x"]) for n in sorted(chk_max) if n in ref_max and n != 0]
        print(f"check on a screen {s_chk:g} cm from the wall (two slits, a wider view: +-{math.degrees(math.atan2(span_cm, s_chk)):.0f} "
              f"degrees): {ck['bright']} bright bands at " + fmt_ext(ck["maxima"]) + f"; {ck['dark']} dark bands at " +
              fmt_ext(ck["minima"]) + "; the bands of orders " + ", ".join(f"{n:+d}" for n, _ in ratios) + " sit at " +
              ", ".join(f"{r:.3f}" for _, r in ratios) + f" of their {S:g} cm positions (a straight line from the wall centre "
              f"gives {s_chk / S:.3f})")
        ck1 = one["checks"][s_chk]
        print(f"check on a screen {s_chk:g} cm from the wall (one slit): {ck1['bright']} bright band, {ck1['dark']} dark bands, "
              f"largest pruned ripple {100 * ck1['ripple']:.2f}% of the peak")
    out["bright"] = st["bright"]
    out["dark"] = st["dark"]
    out["first_dark_deg"] = meas_d[0]
    out["first_dark_x"] = mins[half]["x"]
    out["bright_deg"] = meas_b
    out["dark_deg"] = meas_d
    return out


class Renderer:
    def __init__(self, man: dict, meas: dict):
        self.man, self.meas = man, meas
        self.fps = man["fps"]
        font = os.environ["SEED_ZERO_FONT"]
        self.font = ImageFont.truetype(font, 40)
        self.font_title = ImageFont.truetype(font, 56)
        self.font_label = ImageFont.truetype(font, 36)
        self.font_read = ImageFont.truetype(font, 28)
        self.font_small = ImageFont.truetype(font, 24)
        self.first: np.ndarray | None = None
        self.ppc = man["px_per_cm"]
        self.tank_w = int(round(man["tank_w_cm"] * self.ppc))
        self.tank_h = int(round(man["tank_h_cm"] * self.ppc))
        self.tanks = [Tank(man, p["slits"], man["dx_mm"], man["substeps"]) for p in PANELS]
        self.frame_done = 0
        self.gamma = man["gamma"]
        levels = np.linspace(-1.0, 1.0, 2049)
        lut = np.zeros((2049, 3), dtype=np.uint8)
        for ch in range(3):
            lo, fl, hi = WATER_LOW[ch], WATER_FLAT[ch], WATER_HIGH[ch]
            lut[:, ch] = np.where(levels < 0, fl + (lo - fl) * (-levels), fl + (hi - fl) * levels).round().astype(np.uint8)
        self.lut = lut
        t0 = self.tanks[0]
        self.wall_px = int(round((man["tank_h_cm"] - t0.wall_mid) * self.ppc))
        self.screen_px = int(round((man["tank_h_cm"] - t0.ys[t0.j_screen]) * self.ppc))
        self.slit_px = []
        for tk in self.tanks:
            cols = np.where(tk.slit_cols)[0]
            runs = np.split(cols, np.where(np.diff(cols) > 1)[0] + 1)
            self.slit_px.append([(int(r[0] * self.ppc / tk.cpc + 0.5), int((r[-1] + 1) * self.ppc / tk.cpc + 0.5)) for r in runs])
        self.span_px = (int(t0.span.start * self.ppc / t0.cpc + 0.5), int(t0.span.stop * self.ppc / t0.cpc + 0.5))
        self.px_x = (np.arange(self.tank_w) + 0.5) / self.ppc - man["tank_w_cm"] / 2.0
        self.counts_seen: list[list[tuple[int, int]]] = [[], []]
        widths = {"overlay@34": (ImageFont.truetype(font, 34), man["overlay"])}
        for j, line in enumerate(man["title"].split("|")):
            widths[f"title line {j + 1}@56"] = (self.font_title, line)
        for p in PANELS:
            widths[f"label {p['name']}@36"] = (self.font_label, p["label"])
        widths["readout@28"] = (self.font_read, self.readout_text(7, 6))
        widths["angle label@24"] = (self.font_small, self.angle_text())
        for j, line in enumerate(self.payoff_lines()):
            widths[f"payoff line {j + 1}@40"] = (self.font, line)
        print("text widths: " + ", ".join(f"{k} {f.getlength(s):.0f} px" for k, (f, s) in widths.items()))
        print(f"video: {1 / man['speed']:g}x slow motion, {man['scene_duration']:g} s; tank {self.tank_w} x {self.tank_h} px at "
              f"{self.ppc:g} px/cm (wavelength {man['c_m_s'] / man['freq_hz'] * 100 * self.ppc:.0f} px, crests move "
              f"{100 * man['c_m_s'] * man['speed']:g} cm per video second); wall {self.wall_px} px and screen {self.screen_px} px "
              f"below the tank top; strip {STRIP_H} px above the screen; counts settle at {meas['one_settle']:.2f} s (one slit) and "
              f"{meas['two_settle']:.2f} s (two slits); angle label from {meas['two_settle']:.2f} s; payoff card at {man['payoff_t']:g} s")

    def payoff_lines(self) -> list[str]:
        text = self.man["payoff_text"].format(bright=self.meas["bright"], dark=self.meas["dark"])
        return [s.strip() for s in text.split("|")]

    def readout_text(self, bright: int, dark: int) -> str:
        return f"bright bands: {bright}   dark bands: {dark}"

    def angle_text(self) -> str:
        return f"dark at {self.meas['first_dark_deg']:.1f}°"

    def advance_to(self, f: int) -> None:
        while self.frame_done < f:
            for tk in self.tanks:
                for _ in range(tk.substeps):
                    tk.step()
            self.frame_done += 1
            for m, tk in enumerate(self.tanks):
                st = profile_stats(tk.live_profile(), tk, tk.S, self.man)
                self.counts_seen[m].append((st["bright"], st["dark"]))

    def water(self, tk: Tank, P4: np.ndarray, st: dict) -> np.ndarray:
        """The tank as an RGB array: the height map, the gold strip, the screen line and the wall."""
        fld = tk.field()[::-1]
        img = Image.fromarray(np.ascontiguousarray(fld)).resize((self.tank_w, self.tank_h), Image.BILINEAR)
        v = np.asarray(img, dtype=np.float32) / np.float32(tk.ref)
        np.clip(v, -1.0, 1.0, out=v)
        g = np.sign(v) * np.abs(v) ** np.float32(self.gamma) if self.gamma != 0.5 else np.sign(v) * np.sqrt(np.abs(v))
        idx = np.clip(((g + 1.0) * 1024.0).round().astype(np.int32), 0, 2048)
        rgb = self.lut[idx]
        # Strip: the running average, normalised to its own peak, as gold bar heights.
        if st["pmax"] > self.man["count_floor"] * tk.ref ** 2:
            prof = np.interp(self.px_x, tk.xs, P4)
            hgt = np.clip(prof / prof[self.span_px[0]:self.span_px[1]].max(), 0.0, 1.0) * STRIP_H
            rows = np.arange(STRIP_H)[:, None]
            mask = rows >= (STRIP_H - hgt[None, :]).round()
            mask[:, :self.span_px[0]] = False
            mask[:, self.span_px[1]:] = False
            y0 = self.screen_px - STRIP_H
            region = rgb[y0:self.screen_px]
            region[mask] = GOLD
        rgb[self.screen_px:self.screen_px + 2, self.span_px[0]:self.span_px[1]] = MUTED
        rgb[self.wall_px - 3:self.wall_px + 3, :] = BEAM
        return rgb

    def draw_scene(self, t: float) -> Image.Image:
        man = self.man
        img = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(img)
        for m, (p, tk) in enumerate(zip(PANELS, self.tanks)):
            top = PANEL_TOPS[m]
            P4 = tk.live_profile()
            st = profile_stats(P4, tk, tk.S, man)
            rgb = self.water(tk, P4, st)
            for a, b in self.slit_px[m]:
                rgb[self.wall_px - 3:self.wall_px + 3, a:b] = rgb[self.wall_px + 4:self.wall_px + 10, a:b]
            tank_top = top + LABEL_H
            img.paste(Image.fromarray(rgb), (TANK_X0, tank_top))
            d.rectangle((TANK_X0 - 1, tank_top - 1, TANK_X0 + self.tank_w, tank_top + self.tank_h), outline=WIRE, width=1)
            d.text((40, top + LABEL_H // 2), p["label"], font=self.font_label, fill=p["colour"], anchor="lm")
            d.text((W - 40, top + LABEL_H // 2), self.readout_text(st["bright"], st["dark"]), font=self.font_read,
                   fill=TEXT if st["bright"] > 0 else MUTED, anchor="rm")
            if m == 1 and t >= self.meas["two_settle"] and st["bright"] == self.meas["bright"]:
                x = TANK_X0 + (self.meas["first_dark_x"] + man["tank_w_cm"] / 2.0) * self.ppc
                y = tank_top + self.screen_px + 2
                d.line((x, y, x, y + 16), fill=MUTED, width=2)
                d.text((x, y + 20), self.angle_text(), font=self.font_small, fill=MUTED, anchor="ma")
        return img

    def live_frame(self, f: int) -> np.ndarray:
        man = self.man
        t = f / self.fps
        self.advance_to(f)
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
        if self.first is None:
            self.first = self.live_frame(0)
        live = self.live_frame(f) if f > 0 else self.first
        fade_frames = int(round(man["loop_fade"] * self.fps))
        if f >= total - fade_frames:
            a = (f - (total - fade_frames) + 1) / fade_frames
            live = live * (1 - a) + self.first * a
        return live.astype(np.uint8)

    def check_counts(self) -> None:
        for m, p in enumerate(PANELS):
            seen = self.counts_seen[m]
            ref = self.meas["runs"][p["name"]]["counts"][1:1 + len(seen)]
            same = seen == ref
            print(f"render {p['name']}: live counts over {len(seen)} frames {'match' if same else 'DIFFER FROM'} the measure run; "
                  f"final {seen[-1][0]} bright, {seen[-1][1]} dark")

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
        self.check_counts()
        print(f"footage: {out_path} ({total / self.fps:.2f}s at {self.fps} fps)")


def main() -> None:
    man = json.loads((ROOT / "projects/slits/manifest.json").read_text())
    meas = measure(man)
    if "--measure-only" in sys.argv:
        return
    if "--frames" in sys.argv:
        times = sorted(float(v) for v in sys.argv[sys.argv.index("--frames") + 1].split(","))
        r = Renderer(man, meas)
        for tv in times:
            Image.fromarray(r.frame_at(int(round(tv * man["fps"])))).save(ROOT / f"media/slits/smoke-{tv:g}.png")
        r.check_counts()
        print("smoke frames: " + ", ".join(f"{tv:g}" for tv in times))
        return
    Renderer(man, meas).render(ROOT / "media/slits/footage.mp4")


if __name__ == "__main__":
    main()
