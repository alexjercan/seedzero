#!/usr/bin/env python3
"""Tsunami shoaling: a one meter wave at sea. How tall at the shore?

One dimensional linear shallow water on a still-water depth h(x):

    eta_t + (h u)_x = 0,    u_t + g eta_x = 0

on an Arakawa C grid (eta at cell centres, u at faces, closed walls at both
ends) stepped with the staggered leapfrog (u half a step ahead of eta), which
conserves the discrete energy 0.5 g eta_n^2 + 0.5 h u_{n-1/2} u_{n+1/2}
exactly. Linear, no breaking: sqrt(g h) for the speed and Green's law
(crest height proportional to h^(-1/4)) are linear-theory results.

The sea floor is flat at 4,000 m, then a slope where sqrt(h) falls linearly
with x, h(x) = h_deep ((x_apex - x) / L_apex)^2, down to a flat shelf at
10 m. On that profile the local wavelength of any wave shrinks by the same
amount per metre travelled everywhere (d lambda / dx constant, 0.1 here for
the hump sent), so the depth changes slowly against the local wavelength
along the whole slope, which is what Green's law needs; a straight slope
would fail this at the shallow end and reflect. The wave is a single
Gaussian hump of height exactly 1 m, launched as a pure right-going wave
(u = eta sqrt(g / h)) in the deep flat section. A control run sends the
same hump down a flat 4,000 m tank for the same time (measured, not drawn).
Deterministic, no seed.

Measured and printed: the crest height, position, speed (from successive
crest positions against sqrt(g h) at the crest) and width at half height
along the run, at the check depths and on the shelf; the time to reach the
shelf; the reflection left behind the crest (largest |eta| behind the hump
and the largest left-going component); the discrete energy drift; the same
crest numbers at half the grid step with half the time step, and at half the
time step alone; the control run; and the on-screen text widths.

usage: tsunami.py [--measure-only] [--frames t1,t2,...]
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
WATER = (26, 84, 88)
WATER_DEEP = (18, 58, 66)
SURF = (150, 232, 208)
SEABED = (58, 50, 46)
TICK = (96, 84, 76)
MINI_BED = (66, 58, 54)

# Layout: overlay at y 96..130 (compose), title rows at y 190/252 for the
# first seconds, the minimap strip at y 330..440 (whole profile, crest
# marker, visible window), the main panel at y 460..1400 with the still
# water line at y 800 (wave heights at px_per_m_wave above it, the sea floor
# on its own compressed scale below it), readouts top right, the time-lapse
# clock top left, the scale bar bottom right; captions at caption_y 0.75
# (y 1440..1520), payoff card from y 1592.
MINI_Y0, MINI_Y1 = 330, 440
MINI_SWL = 358
MINI_X0, MINI_X1 = 60, 1020
PANEL_Y0, PANEL_Y1 = 460, 1400
SWL_Y = 800
DEPTH_PX_MIN = 60.0
DEPTH_PX_SPAN = 500.0
PAYOFF_Y = 1592.0
SS = 2

_R = None  # renderer shared with forked frame workers


def blend(col, a, base=BG):
    return tuple(int(round(c * a + b * (1 - a))) for c, b in zip(col, base))


def profile_params(man: dict) -> dict:
    h_deep, h_shelf = man["h_deep_m"], man["h_shelf_m"]
    x_slope = man["x_slope_km"] * 1000.0
    L_apex = man["apex_km"] * 1000.0
    x_apex = x_slope + L_apex
    x_shallow = x_apex - L_apex * math.sqrt(h_shelf / h_deep)
    return {"h_deep": h_deep, "h_shelf": h_shelf, "x_slope": x_slope, "L_apex": L_apex,
            "x_apex": x_apex, "x_shallow": x_shallow}


def depth(x: np.ndarray, p: dict) -> np.ndarray:
    """Still-water depth at x (m): flat deep, quadratic slope, flat shelf."""
    s = np.clip((p["x_apex"] - x) / p["L_apex"], 0.0, 1.0)
    h = p["h_deep"] * s * s
    return np.where(x < p["x_slope"], p["h_deep"], np.where(x > p["x_shallow"], p["h_shelf"], h))


def x_of_depth(h: float, p: dict) -> float:
    return p["x_apex"] - p["L_apex"] * math.sqrt(h / p["h_deep"])


def crest_of(eta: np.ndarray, xc: np.ndarray, dx: float) -> tuple[float, float, float]:
    """Sub-grid crest position and height (parabola through three points) and the width at half height."""
    n = eta.shape[0]
    i = int(np.argmax(eta))
    i = min(max(i, 1), n - 2)
    a, b, c = float(eta[i - 1]), float(eta[i]), float(eta[i + 1])
    denom = a - 2.0 * b + c
    delta = 0.5 * (a - c) / denom if denom != 0.0 else 0.0
    x = float(xc[i]) + delta * dx
    peak = b - 0.25 * (a - c) * delta
    half = 0.5 * peak
    left = np.nonzero(eta[:i] <= half)[0]
    right = np.nonzero(eta[i:] <= half)[0]
    if len(left) == 0 or len(right) == 0:
        return x, peak, float("nan")
    jl = int(left[-1])
    jr = i + int(right[0])
    xl = xc[jl] + dx * (half - eta[jl]) / (eta[jl + 1] - eta[jl])
    xr = xc[jr - 1] + dx * (eta[jr - 1] - half) / (eta[jr - 1] - eta[jr])
    return x, peak, float(xr - xl)


def simulate(cfg: dict) -> dict:
    """Step the linear shallow-water equations; sample the crest, energy and reflection every frame."""
    g, dx, dt = cfg["g"], cfg["dx"], cfg["dt"]
    p = cfg["profile"]
    nx = int(round(cfg["x_end"] / dx))
    xc = (np.arange(nx) + 0.5) * dx
    xf = np.arange(nx + 1) * dx
    h_c = depth(xc, p) if not cfg["flat"] else np.full(nx, p["h_deep"])
    h_f = depth(xf, p) if not cfg["flat"] else np.full(nx + 1, p["h_deep"])
    A, sig, x0 = cfg["A"], cfg["sigma"], cfg["x0"]
    c0 = math.sqrt(g * p["h_deep"])
    eta = A * np.exp(-((xc - x0) ** 2) / (2.0 * sig * sig))
    # u half a step behind eta: the right-going hump at t = -dt/2 sits c0 dt/2 to the left.
    u = np.sqrt(g / h_f) * A * np.exp(-((xf + 0.5 * c0 * dt - x0) ** 2) / (2.0 * sig * sig))
    u[0] = 0.0
    u[-1] = 0.0
    spf = cfg["steps_per_frame"]
    n_frames = cfg["n_frames"]
    gl = g * dt / dx
    l = dt / dx
    sq_hg = np.sqrt(h_c / g)
    deep_mask = xc < p["x_slope"]
    crest_x = np.zeros(n_frames)
    crest_h = np.zeros(n_frames)
    fwhm = np.zeros(n_frames)
    energy = np.zeros(n_frames)
    behind = np.zeros(n_frames)
    slope_behind = np.zeros(n_frames)
    trough = np.zeros(n_frames)
    deep_refl = np.zeros(n_frames)
    vol_hump = np.zeros(n_frames)
    vol_total = np.zeros(n_frames)
    field = np.zeros((n_frames, nx), dtype=np.float32) if cfg["store_field"] else None
    for f in range(n_frames):
        for k in range(spf):
            if k == 0:
                u_prev = u.copy()
            u[1:-1] -= gl * (eta[1:] - eta[:-1])
            if k == 0:
                x, pk, wd = crest_of(eta, xc, dx)
                crest_x[f], crest_h[f], fwhm[f] = x, pk, wd
                energy[f] = 0.5 * g * float(np.dot(eta, eta)) * dx + 0.5 * float(np.dot(h_f * u_prev, u)) * dx
                # Exact left-going part in the flat deep section: the wave the slope sends back.
                u_c = 0.25 * (u_prev[:-1] + u_prev[1:] + u[:-1] + u[1:])
                R = 0.5 * (eta - u_c * sq_hg)
                deep_refl[f] = float(np.abs(R[deep_mask]).max())
                mask = xc < x - 3.0 * wd
                if mask.any():
                    behind[f] = float(np.abs(eta[mask]).max())
                    on_slope = mask & ~deep_mask & (xc <= p["x_shallow"])
                    if on_slope.any():
                        slope_behind[f] = float(np.abs(eta[on_slope]).max())
                trough[f] = float(eta[xc < x].min())
                hump = (xc > x - 3.0 * wd) & (xc < x + 3.0 * wd)
                vol_hump[f] = float(eta[hump].sum()) * dx
                vol_total[f] = float(eta.sum()) * dx
                if field is not None:
                    field[f] = eta
            hu = h_f * u
            eta -= l * (hu[1:] - hu[:-1])
    return {"crest_x": crest_x, "crest_h": crest_h, "fwhm": fwhm, "energy": energy, "behind": behind,
            "slope_behind": slope_behind, "trough": trough, "deep_refl": deep_refl, "vol_hump": vol_hump,
            "vol_total": vol_total,
            "field": field, "xc": xc, "h_c": h_c, "cfg": cfg}


def cfg_for(man: dict, dx: float | None = None, dt: float | None = None, flat: bool = False,
            store_field: bool = False) -> dict:
    p = profile_params(man)
    dx = man["dx_m"] if dx is None else dx
    dt = man["dt_s"] if dt is None else dt
    frame_dt = man["time_lapse"] / man["fps"]
    spf = frame_dt / dt
    assert abs(spf - round(spf)) < 1e-9, "the frame interval must be a whole number of steps"
    n_frames = int(round(man["scene_duration"] * man["fps"]))
    return {
        "g": man["g"], "dx": dx, "dt": dt, "profile": p, "flat": flat,
        "x_end": (man["control_x_end_km"] if flat else man["x_end_km"]) * 1000.0,
        "A": man["hump_height_m"], "sigma": man["hump_fwhm_km"] * 1000.0 / (2.0 * math.sqrt(2.0 * math.log(2.0))),
        "x0": man["x_start_km"] * 1000.0, "steps_per_frame": int(round(spf)), "n_frames": n_frames,
        "frame_dt": frame_dt, "store_field": store_field,
    }


def speed_series(crest_x: np.ndarray, frame_dt: float, k: int) -> np.ndarray:
    n = crest_x.shape[0]
    idx = np.arange(n)
    lo = np.clip(idx - k, 0, n - 1)
    hi = np.clip(idx + k, 0, n - 1)
    return (crest_x[hi] - crest_x[lo]) / ((hi - lo) * frame_dt)


def at_x(run: dict, x: float, k: int) -> dict:
    """Crest numbers when the crest passes x (linear in the per-frame series)."""
    cx = run["crest_x"]
    f = int(np.searchsorted(cx, x))
    if f <= 0 or f >= cx.shape[0]:
        return {"f": float("nan"), "t": float("nan"), "h": float("nan"), "v": float("nan"), "w": float("nan"),
                "depth": float("nan")}
    a = (x - cx[f - 1]) / (cx[f] - cx[f - 1])
    fr = f - 1 + a
    v = speed_series(cx, run["cfg"]["frame_dt"], k)

    def lerp(s):
        return float(s[f - 1] * (1 - a) + s[f] * a)

    return {"f": fr, "t": fr * run["cfg"]["frame_dt"], "h": lerp(run["crest_h"]), "v": lerp(v),
            "w": lerp(run["fwhm"]), "depth": float(depth(np.array([x]), run["cfg"]["profile"])[0])}


def fmt_t(seconds: float) -> str:
    return f"{int(seconds // 3600)} h {int((seconds % 3600) // 60):02d} min"


def measure(man: dict) -> dict:
    g = man["g"]
    p = profile_params(man)
    h_deep, h_shelf = p["h_deep"], p["h_shelf"]
    A, fwhm_km = man["hump_height_m"], man["hump_fwhm_km"]
    sigma_km = fwhm_km / (2.0 * math.sqrt(2.0 * math.log(2.0)))
    dx, dt = man["dx_m"], man["dt_s"]
    tl, dur, fps = man["time_lapse"], man["scene_duration"], man["fps"]
    frame_dt = tl / fps
    k = man["speed_window_frames"]
    c_deep = math.sqrt(g * h_deep)
    c_shelf = math.sqrt(g * h_shelf)
    green = (h_deep / h_shelf) ** 0.25
    t_deep = (p["x_slope"] - man["x_start_km"] * 1000.0) / c_deep
    t_slope = p["L_apex"] / c_deep * math.log(p["L_apex"] / (p["x_apex"] - p["x_shallow"]))
    slope_km = (p["x_shallow"] - p["x_slope"]) / 1000.0
    print(f"setup: linear shallow water in one dimension, eta_t + (h u)_x = 0, u_t + g eta_x = 0, g = {g:g} m/s^2, "
          f"on a C grid with dx = {dx:g} m and dt = {dt:g} s (Courant {c_deep * dt / dx:.3f} in the deepest cell), "
          f"staggered leapfrog, closed walls at x = 0 and x = {man['x_end_km']:g} km; sea floor flat at {h_deep:g} m "
          f"to x = {man['x_slope_km']:g} km, then h = {h_deep:g} m ((x_apex - x) / {man['apex_km']:g} km)^2 with "
          f"x_apex = {p['x_apex'] / 1000:g} km, a {slope_km:.0f} km slope down to {h_shelf:g} m at x = "
          f"{p['x_shallow'] / 1000:.0f} km (sea-floor slope {h_deep / p['L_apex'] * 2:.4f} at the top and "
          f"{2 * math.sqrt(h_deep * h_shelf) / p['L_apex']:.5f} at the bottom), then a flat {h_shelf:g} m shelf; "
          f"the wave is a Gaussian hump of height {A:g} m and width {fwhm_km:g} km at half height (sigma "
          f"{sigma_km:.2f} km) centred at x = {man['x_start_km']:g} km at t = 0, launched right-going (u = eta "
          f"sqrt(g / h)); the hump's half-height width shrinks by {fwhm_km * 1000 / p['L_apex']:.2f} m per metre "
          f"travelled on the slope; {dur * tl:g} s of sea time ({fmt_t(dur * tl)}) shown in {dur:g} s at time x{tl}, "
          f"{frame_dt:g} s per frame ({int(round(frame_dt / dt))} steps); control: the same hump in a flat "
          f"{h_deep:g} m tank {man['control_x_end_km']:g} km long for the same time; linear, no breaking; "
          f"deterministic, no seed")
    print(f"closed forms: sqrt(g h) = {c_deep:.2f} m/s at {h_deep:g} m and {c_shelf:.3f} m/s at {h_shelf:g} m; "
          f"Green's law (h_deep / h)^(1/4) = {green:.4f}, so a {A:g} m hump becomes {A * green:.3f} m at "
          f"{h_shelf:g} m; the width at half height scales with sqrt(h), a factor {math.sqrt(h_deep / h_shelf):.1f} "
          f"shorter at {h_shelf:g} m ({fwhm_km / math.sqrt(h_deep / h_shelf):.1f} km); the crest reaches the slope "
          f"after {t_deep:.0f} s ({t_deep / tl:.2f} s of the video), crosses it in {t_slope:.0f} s "
          f"({t_slope / tl:.2f} s of the video) and reaches the shelf at {t_deep + t_slope:.0f} s "
          f"({(t_deep + t_slope) / tl:.2f} s of the video); time on the slope to h: " +
          ", ".join(f"{h:g} m at {(t_deep + p['L_apex'] / c_deep * math.log(p['L_apex'] / (p['x_apex'] - x_of_depth(h, p)))) / tl:.2f} s"
                    for h in man["check_depths_m"]))

    ctx = multiprocessing.get_context("fork")
    jobs = {
        "half": cfg_for(man, dx=dx / 2, dt=dt / 2),
        "halfdt": cfg_for(man, dt=dt / 2),
        "control": cfg_for(man, flat=True),
    }
    with ProcessPoolExecutor(max_workers=len(jobs), mp_context=ctx) as pool:
        futures = {name: pool.submit(simulate, cfg) for name, cfg in jobs.items()}
        main_run = simulate(cfg_for(man, store_field=True))
        runs = {name: fut.result() for name, fut in futures.items()}
    runs["main"] = main_run

    def report(run: dict, label: str) -> dict:
        cx, ch, wd = run["crest_x"], run["crest_h"], run["fwhm"]
        v = speed_series(cx, frame_dt, k)
        out = {}
        print(f"{label}, start: crest {ch[0]:.4f} m at x = {cx[0] / 1000:.1f} km, width at half height "
              f"{wd[0] / 1000:.2f} km, speed over the first {2 * k} frames {v[k] :.2f} m/s against sqrt(g h) "
              f"{c_deep:.2f}")
        # Deep section, halfway to the slope.
        deep = at_x(run, 0.5 * (man["x_start_km"] * 1000.0 + p["x_slope"]), k)
        out["deep"] = deep
        print(f"{label}, in the deep flat section (x = {0.5 * (man['x_start_km'] * 1000.0 + p['x_slope']) / 1000:.0f} km, "
              f"{deep['t'] / tl:.2f} s of the video): crest {deep['h']:.4f} m, speed {deep['v']:.2f} m/s against "
              f"{c_deep:.2f}, width {deep['w'] / 1000:.2f} km")
        lines = []
        for h in man["check_depths_m"]:
            r = at_x(run, x_of_depth(h, p), k)
            out[h] = r
            lines.append(f"{h:g} m (x = {x_of_depth(h, p) / 1000:.1f} km, {r['t']:.0f} s, {r['t'] / tl:.2f} s of the "
                         f"video): crest {r['h']:.4f} m against Green {A * (h_deep / h) ** 0.25:.4f}, speed "
                         f"{r['v']:.2f} m/s against sqrt(g h) {math.sqrt(g * h):.2f}, width {r['w'] / 1000:.2f} km "
                         f"against {fwhm_km * math.sqrt(h / h_deep):.2f}")
        print(f"{label}, crest at the check depths: " + "; ".join(lines))
        x_sh = p["x_shallow"] + man["shelf_check_km"] * 1000.0
        sh = at_x(run, x_sh, k)
        out["shelf"] = sh
        end_f = cx.shape[0] - 1
        print(f"{label}, on the shelf ({man['shelf_check_km']:g} km past the slope's foot, x = {x_sh / 1000:.0f} km, "
              f"{sh['t']:.0f} s, {sh['t'] / tl:.2f} s of the video): crest {sh['h']:.4f} m against Green "
              f"{A * green:.4f} (ratio {sh['h'] / (A * green):.4f}), speed {sh['v']:.3f} m/s against {c_shelf:.3f}, "
              f"width {sh['w'] / 1000:.3f} km against {fwhm_km / math.sqrt(h_deep / h_shelf):.3f} (a factor "
              f"{wd[0] / sh['w']:.2f} shorter than at the start); at the end of the scene ({end_f * frame_dt:.0f} s) "
              f"the crest is {ch[end_f]:.4f} m at x = {cx[end_f] / 1000:.1f} km, {(cx[end_f] - p['x_shallow']) / 1000:.1f} km "
              f"onto the shelf, moving at {v[end_f]:.3f} m/s; largest crest over the run {ch.max():.4f} m at "
              f"{ch.argmax() * frame_dt / tl:.2f} s")
        e = run["energy"]
        print(f"{label}, energy: {e[0]:.6e} J/m at the start, {e[-1]:.6e} at the end, relative drift "
              f"{(e[-1] - e[0]) / e[0]:+.2e}, largest excursion {np.abs(e - e[0]).max() / e[0]:.2e}")
        return out

    res = report(main_run, "main run")
    # Reflection and what is left behind the crest.
    f_sh = int(math.ceil(res["shelf"]["f"]))
    f_foot = int(math.ceil(at_x(main_run, p["x_shallow"], k)["f"]))
    f_top = int(math.ceil(at_x(main_run, p["x_slope"], k)["f"]))
    b, tr, rf, sb = main_run["behind"], main_run["trough"], main_run["deep_refl"], main_run["slope_behind"]
    vh, vt = main_run["vol_hump"], main_run["vol_total"]
    t_wall = t_deep + p["x_slope"] / c_deep
    print(f"main run, reflection: the slope sends a long low wave back into the deep water; its left-going part "
          f"(eta - u sqrt(h / g)) / 2, exact in the flat section, is at most {rf[f_top]:.5f} m when the crest enters "
          f"the slope, {rf[f_foot]:.5f} m ({100 * rf[f_foot] / A:.2f} % of {A:g} m) when the crest reaches the "
          f"foot, {rf[f_sh]:.5f} m on the shelf and {rf[-1]:.5f} m at the end (largest over the run {rf.max():.5f} m at "
          f"{rf.argmax() * frame_dt / tl:.2f} s of the video); the largest |eta| more than three half-height widths "
          f"behind the crest is {b[f_foot]:.5f} m ({100 * b[f_foot] / A:.2f} %) at the foot (at the wall, where a "
          f"left-going wave doubles), {b[f_sh]:.5f} m on the shelf and {b[-1]:.5f} m at the end; on the slope itself "
          f"the largest |eta| behind the crest is {sb[f_foot]:.5f} m ({100 * sb[f_foot] / A:.2f} %) when the crest "
          f"reaches the foot and {sb.max():.5f} m ({100 * sb.max() / A:.2f} %) at most over the run (at "
          f"{sb.argmax() * frame_dt / tl:.2f} s of the video); the water right behind the hump is drawn down to {tr[f_foot]:.4f} m at "
          f"the foot, {tr[f_sh]:.4f} m on the shelf and {tr[-1]:.4f} m at the end; the hump (within three half-height "
          f"widths of the crest) holds {vh[0] / 1e6:.4f} km^2 of water at the start, {vh[f_foot] / 1e6:.4f} km^2 "
          f"({100 * vh[f_foot] / vt[0]:.1f} %) at the foot and {vh[f_sh] / 1e6:.4f} km^2 ({100 * vh[f_sh] / vt[0]:.1f} %) "
          f"on the shelf, the total {vt[0] / 1e6:.4f} km^2 conserved to {abs(vt - vt[0]).max() / vt[0]:.1e}; the "
          f"wave sent back reaches the wall at x = 0 no earlier than {t_wall:.0f} s ({t_wall / tl:.1f} s of the video) "
          f"and its bounce cannot be back at the slope before {t_wall + p['x_slope'] / c_deep:.0f} s, after the "
          f"{dur * tl:.0f} s run")
    half = report(runs["half"], f"check at half the grid step and half the time step (dx = {dx / 2:g} m, dt = {dt / 2:g} s)")
    halfdt = report(runs["halfdt"], f"check at half the time step alone (dt = {dt / 2:g} s)")
    print("check summary, crest on the shelf: main "
          f"{res['shelf']['h']:.4f} m, half grid and time step {half['shelf']['h']:.4f} m, half time step "
          f"{halfdt['shelf']['h']:.4f} m; at the check depths main / half grid: " +
          ", ".join(f"{h:g} m {res[h]['h']:.4f} / {half[h]['h']:.4f}" for h in man["check_depths_m"]))
    ctrl = runs["control"]
    cxc, chc, wdc = ctrl["crest_x"], ctrl["crest_h"], ctrl["fwhm"]
    vc = speed_series(cxc, frame_dt, k)
    f_ctrl = f_sh
    print(f"control (flat {h_deep:g} m tank, same hump, same time): crest {chc[f_ctrl]:.4f} m, speed "
          f"{vc[f_ctrl]:.2f} m/s, width {wdc[f_ctrl] / 1000:.2f} km at {f_ctrl * frame_dt:.0f} s (when the slope "
          f"run is {man['shelf_check_km']:g} km onto the shelf), x = {cxc[f_ctrl] / 1000:.0f} km; at the end "
          f"{chc[-1]:.4f} m, {vc[-1]:.2f} m/s, {wdc[-1] / 1000:.2f} km, x = {cxc[-1] / 1000:.0f} km; crest over the "
          f"run between {chc.min():.4f} and {chc.max():.4f} m; energy drift {(ctrl['energy'][-1] - ctrl['energy'][0]) / ctrl['energy'][0]:+.2e}")
    return {"run": main_run, "res": res, "profile": p, "c_deep": c_deep, "c_shelf": c_shelf, "green": green}


class Renderer:
    def __init__(self, man: dict, meas: dict):
        self.man, self.meas = man, meas
        self.fps = man["fps"]
        font = os.environ["SEED_ZERO_FONT"]
        self.font = ImageFont.truetype(font, 40)
        self.font_title = ImageFont.truetype(font, 56)
        self.font_read = ImageFont.truetype(font, 36)
        self.font_small = ImageFont.truetype(font, 28)
        self.font_tiny = ImageFont.truetype(font, 24)
        self.first = None
        self.p = meas["profile"]
        run = meas["run"]
        self.tl = man["time_lapse"]
        self.frame_dt = self.tl / self.fps
        self.ppm = float(man["px_per_m_wave"])
        self.crest_x = run["crest_x"]
        self.crest_h = run["crest_h"]
        self.speed = speed_series(self.crest_x, self.frame_dt, man["speed_window_frames"])
        self.h_crest = depth(self.crest_x, self.p)
        w_deep = man["window_deep_km"] * 1000.0
        self.win = w_deep * (self.h_crest / self.p["h_deep"]) ** 0.25
        self.xl = self.crest_x - man["crest_frac"] * self.win
        # Surface height per screen column (supersampled) for every frame.
        n = self.crest_x.shape[0]
        cols = (np.arange(W * SS) + 0.5) / (W * SS)
        self.surface = np.zeros((n, W * SS), dtype=np.float32)
        xc = run["xc"]
        for f in range(n):
            xs = self.xl[f] + cols * self.win[f]
            self.surface[f] = np.interp(xs, xc, run["field"][f])
        run["field"] = None
        self.tick = man["tick_km"] * 1000.0
        widths = {"overlay@34": (ImageFont.truetype(font, 34), man["overlay"])}
        for j, line in enumerate(man["title"].split("|")):
            widths[f"title line {j + 1}@56"] = (self.font_title, line)
        widths["depth readout@36"] = (self.font_read, "depth  4,000 m")
        widths["speed readout@36"] = (self.font_read, "speed  198 m/s")
        widths["wave readout@36"] = (self.font_read, "wave  4.5 m")
        widths["time label@28"] = (self.font_small, f"time x{self.tl}")
        widths["clock@36"] = (self.font_read, fmt_t(man["scene_duration"] * self.tl))
        widths["note@28"] = (self.font_small, "wave height and depth not to scale")
        widths["scale@28"] = (self.font_small, f"{man['tick_km']:g} km")
        widths["minimap label@24"] = (self.font_tiny, "ocean floor, the whole run")
        for j, line in enumerate(self.payoff_lines()):
            widths[f"payoff line {j + 1}@40"] = (self.font, line)
        print("text widths: " + ", ".join(f"{k} {f.getlength(s):.0f} px" for k, (f, s) in widths.items()))
        res = meas["res"]
        foot = at_x(run, self.p["x_shallow"], man["speed_window_frames"])
        print(f"video: {man['scene_duration']:g} s at time x{self.tl}; title until {man['title_until']:g} s; the crest "
              f"reaches the slope at {(self.p['x_slope'] - self.crest_x[0]) / meas['c_deep'] / self.tl:.2f} s, "
              f"{man['check_depths_m'][0]:g} m at {res[man['check_depths_m'][0]]['t'] / self.tl:.2f} s, the foot of the "
              f"slope at {foot['t'] / self.tl:.2f} s; payoff card at {man['payoff_t']:g} s; window {self.win[0] / 1000:.0f} km "
              f"wide at the start ({self.win[0] / W / 1000:.3f} km per px, the hump {1000 * man['hump_fwhm_km'] / self.win[0] * W:.0f} px "
              f"wide at half height, {self.ppm * self.crest_h[0]:.0f} px tall) and {self.win[-1] / 1000:.0f} km at the end "
              f"(the hump {run['fwhm'][-1] / self.win[-1] * W:.0f} px wide, {self.ppm * self.crest_h[-1]:.0f} px tall); "
              f"scale bar {self.tick / self.win[0] * W:.0f} px at the start and {self.tick / self.win[-1] * W:.0f} px at the end; "
              f"sea floor under the crest at y {SWL_Y + self.depth_px(self.h_crest[0]):.0f} at the start and "
              f"y {SWL_Y + self.depth_px(self.h_crest[-1]):.0f} at the end")

    def depth_px(self, h):
        p = self.p
        return DEPTH_PX_MIN + DEPTH_PX_SPAN * np.log10(np.maximum(h, p["h_shelf"]) / p["h_shelf"]) / math.log10(p["h_deep"] / p["h_shelf"])

    def payoff_lines(self) -> list[str]:
        res = self.meas["res"]
        text = self.man["payoff_text"].format(deep_h=res["deep"]["h"], deep_v=res["deep"]["v"],
                                              shelf_depth=self.p["h_shelf"], shelf_h=res["shelf"]["h"],
                                              shelf_v=res["shelf"]["v"])
        return [s.strip() for s in text.split("|")]

    @staticmethod
    def fmt_speed(v: float) -> str:
        return f"{v:.0f} m/s" if v >= 100.0 else f"{v:.1f} m/s"

    def draw_panel(self, f: int) -> Image.Image:
        ph = (PANEL_Y1 - PANEL_Y0) * SS
        layer = Image.new("RGB", (W * SS, ph), BG)
        d = ImageDraw.Draw(layer)
        cols = (np.arange(W * SS) + 0.5) / (W * SS)
        xs = self.xl[f] + cols * self.win[f]
        h = depth(xs, self.p)
        y0 = (SWL_Y - PANEL_Y0) * SS
        ys = y0 - self.surface[f] * self.ppm * SS
        yb = y0 + self.depth_px(h) * SS
        px = np.arange(W * SS)
        bed = list(zip(px.tolist(), yb.tolist()))
        d.polygon([(0, ph)] + bed + [(W * SS, ph)], fill=SEABED)
        # Distance ticks on the sea floor, every tick_km, scrolling with the ground.
        k0 = math.ceil(xs[0] / self.tick)
        k1 = math.floor(xs[-1] / self.tick)
        for k in range(k0, k1 + 1):
            xp = (k * self.tick - self.xl[f]) / self.win[f] * W * SS
            j = min(max(int(xp), 0), W * SS - 1)
            d.line((xp, yb[j] + 3 * SS, xp, ph), fill=TICK, width=SS)
        surf = list(zip(px.tolist(), ys.tolist()))
        d.polygon(surf + bed[::-1], fill=WATER)
        d.line(surf, fill=SURF, width=3 * SS)
        return layer.reduce(SS)

    def draw_minimap(self, d: ImageDraw.ImageDraw, f: int) -> None:
        p = self.p
        x_from = self.man["minimap_from_km"] * 1000.0
        x_end = self.man["x_end_km"] * 1000.0
        sc = (MINI_X1 - MINI_X0) / (x_end - x_from)
        xs = np.linspace(x_from, x_end, MINI_X1 - MINI_X0 + 1)
        yb = MINI_SWL + 10 + 60 * (self.depth_px(depth(xs, p)) - DEPTH_PX_MIN) / DEPTH_PX_SPAN
        pts = [(MINI_X0 + sc * (x - x_from), y) for x, y in zip(xs.tolist(), yb.tolist())]
        d.polygon([(MINI_X0, MINI_Y1)] + pts + [(MINI_X1, MINI_Y1)], fill=MINI_BED)
        d.line((MINI_X0, MINI_SWL, MINI_X1, MINI_SWL), fill=blend(SURF, 0.5), width=2)
        # Visible window and the crest marker.
        wl = MINI_X0 + sc * (self.xl[f] - x_from)
        wr = MINI_X0 + sc * (self.xl[f] + self.win[f] - x_from)
        d.rectangle((wl, MINI_SWL - 14, wr, MINI_SWL + 34), outline=blend(TEAL, 0.45), width=2)
        mx = MINI_X0 + sc * (self.crest_x[f] - x_from)
        d.polygon([(mx - 8, MINI_SWL - 20), (mx + 8, MINI_SWL - 20), (mx, MINI_SWL - 4)], fill=GOLD)
        d.text((MINI_X0, MINI_SWL - 24), "ocean floor, the whole run", font=self.font_tiny, fill=MUTED, anchor="lb")
        d.text((MINI_X0 + 10, MINI_Y1 - 22), f"{p['h_deep']:,.0f} m", font=self.font_tiny, fill=blend(TEXT, 0.7), anchor="lm")
        d.text((MINI_X1 - 10, MINI_Y1 - 22), f"{p['h_shelf']:,.0f} m", font=self.font_tiny, fill=blend(TEXT, 0.7), anchor="rm")

    def draw_scene(self, t: float) -> Image.Image:
        man = self.man
        f = min(int(round(t * self.fps)), self.crest_x.shape[0] - 1)
        img = Image.new("RGB", (W, H), BG)
        img.paste(self.draw_panel(f), (0, PANEL_Y0))
        d = ImageDraw.Draw(img)
        self.draw_minimap(d, f)
        # Readouts, top right: label muted, value bright.
        rows = [("depth", f"{self.h_crest[f]:,.0f} m", TEXT), ("speed", self.fmt_speed(self.speed[f]), TEXT),
                ("wave", f"{self.crest_h[f]:.1f} m", GOLD)]
        for j, (label, value, col) in enumerate(rows):
            y = PANEL_Y0 + 30 + j * 50
            d.text((W - 40, y), value, font=self.font_read, fill=col, anchor="rm")
            vw = self.font_read.getlength(value)
            d.text((W - 40 - vw - 14, y), label, font=self.font_read, fill=MUTED, anchor="rm")
        # Time-lapse clock, top left.
        d.text((40, PANEL_Y0 + 30), f"time x{self.tl}", font=self.font_small, fill=MUTED, anchor="lm")
        d.text((40, PANEL_Y0 + 80), fmt_t(f * self.frame_dt), font=self.font_read, fill=TEXT, anchor="lm")
        # Scale bar, bottom right, and the note, bottom left.
        bar = self.tick / self.win[f] * W
        yb = PANEL_Y1 - 48
        d.line((W - 60 - bar, yb, W - 60, yb), fill=TEXT, width=4)
        d.line((W - 60 - bar, yb - 10, W - 60 - bar, yb + 10), fill=TEXT, width=4)
        d.line((W - 60, yb - 10, W - 60, yb + 10), fill=TEXT, width=4)
        d.text((W - 60 - bar / 2, yb - 22), f"{man['tick_km']:g} km", font=self.font_small, fill=TEXT, anchor="mb")
        d.text((40, PANEL_Y1 - 20), "wave height and depth not to scale", font=self.font_small, fill=MUTED, anchor="lm")
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
        global _R
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
        _R = self
        batch = 120
        workers = max(1, min(12, (os.cpu_count() or 2) - 2))
        with ProcessPoolExecutor(max_workers=workers, mp_context=multiprocessing.get_context("fork")) as pool:
            for start in range(0, total, batch):
                stop = min(start + batch, total)
                for data in pool.map(_frame_bytes, range(start, stop)):
                    proc.stdin.write(data)
                print(f"frame {stop}/{total}", file=sys.stderr)
        proc.stdin.close()
        if proc.wait() != 0:
            raise RuntimeError("ffmpeg failed")
        print(f"footage: {out_path} ({total / self.fps:.2f}s at {self.fps} fps)")


def _frame_bytes(f: int) -> bytes:
    return _R.frame_at(f).tobytes()


def main() -> None:
    man = json.loads((ROOT / "projects/tsunami/manifest.json").read_text())
    meas = measure(man)
    if "--measure-only" in sys.argv:
        return
    if "--frames" in sys.argv:
        times = [float(v) for v in sys.argv[sys.argv.index("--frames") + 1].split(",")]
        r = Renderer(man, meas)
        (ROOT / "media/tsunami").mkdir(parents=True, exist_ok=True)
        for tv in times:
            Image.fromarray(r.frame_at(int(round(tv * man["fps"])))).save(ROOT / f"media/tsunami/smoke-{tv}.png")
        print("smoke frames: " + ", ".join(f"{tv}" for tv in times))
        return
    Renderer(man, meas).render(ROOT / "media/tsunami/footage.mp4")


if __name__ == "__main__":
    main()
