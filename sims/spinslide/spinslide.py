#!/usr/bin/env python3
"""Does spinning a coaster make it slide farther?

Two bands on the same clock, the same table drawn the same way at the same
scale, seen from above. A uniform disc of radius R (I = m R^2 / 2, a
coaster) rests on a table with grip mu, the same everywhere under it
(chosen). Each coaster gets the same push: its centre leaves at v0 along
the table (chosen). Top band, the PLAIN coaster: no spin. Bottom band, the
SPUN coaster: the same v0 and a spin omega0 about its centre. The
friction is Coulomb friction with uniform pressure integrated over the
contact: on a polar grid of grid_radial by grid_angular cells (area
weights that sum to 1) every cell slips at u = v + omega x r and feels
-mu g times its unit slip direction per unit mass, so

    a = -mu g <u / |u|>,     alpha = -mu g <r x (u / |u|)> / (R^2 / 2),

the area-weighted means over the contact. A cell under a spinning,
sliding disc slips partly sideways, so the slide feels only part of
mu g and the spin only part of the pure-spin torque: the two motions
share the one friction force and, as Farkas et al. (PRL 2003) showed,
v / (R omega) runs to a fixed point near 0.65 and both stop at the same
instant. x, v, the turn theta and omega are integrated by classical RK4
at dt_s (x by the same RK4 stages); a run stops when |v| and R |omega|
are both under stop_speed_m_s. Checked against the closed forms for the
pure slide (t = v0 / (mu g), x = v0^2 / (2 mu g)) and the pure spin
(alpha = 4 mu g / (3 R)), the grid's weights and inertia, the energy
bookkeeping and a half-step rerun. The run repeats every cycle_s seconds
of video with a crossfade back to the resting setup; the cycle divides
the scene length, so the scene is exactly periodic and the last frame
equals the first. Shown at 1/slow speed. Deterministic, no seed.

Measured and printed: the grid checks, the plain run and the spun run
(stop time, distance, the step on which each motion fell under its bound,
the extrapolated zero crossings, v / (R omega) and the friction shares at
the end, the energy), the table of v, R omega and v / (R omega) every
table_every_s for the spun run, the spin and speed variants and the
spin-only run for the description, the brief's checks, the schedule in
video time, the on-screen text widths and the layout clearances.

usage: spinslide.py [--measure-only] [--frames t1,t2,...]
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
DECK_A = (30, 36, 46)
DECK_B = (44, 52, 64)
RIM = (96, 108, 126)
STRIPE = (16, 20, 26)
FINGER = (196, 170, 150)
NAIL = (232, 214, 200)

# Layout: overlay at y 96..130 (captions.py), two title rows at y 190/252 for
# the first seconds, then the legend at y 236; two bands stacked, the plain
# coaster in y 330..880 and the spun coaster in 880..1430, each drawn at 2x in
# its own layer; each band has its label row 40 px under the band top, its
# second row at 84, the speed readout at 120 and the clock at 156 (left column
# from x 40), the "slid" readout at 120 and the spin readout at 156 right-aligned
# at x 1040 (the label rows run long, so the right readouts share the readout rows); the table surface from 182 to 458 under the band top with the
# coasters' centre line at 320 (the 200 px disc from 220 to 420), the start
# line at start_x_px, a cm ruler under the table's lower edge with labels at
# 486; the gold event row at 524, left-aligned at x 40; captions at caption_y
# 0.75 (y 1440..1530); the card from y 1572 at a 48 px pitch. The event rows
# are 28 px (the spun one is 55 characters).
LEGEND_Y = 236
TITLE_YS = {2: (190, 252), 3: (186, 244, 302)}
SS = 2
PAYOFF_Y, PAYOFF_PITCH = 1572.0, 48
PANELS = ("plain", "spun")
BAND_Y = {"plain": 330, "spun": 880}
BAND_H = 550
LABEL_DY, SUB_DY, SPEED_DY, CLOCK_DY = 40, 84, 120, 156
ROW_X0, ROW_X1 = 40, 1040
TABLE_X0, TABLE_X1, TABLE_Y0, TABLE_Y1 = 20, 1060, 182, 458
DISC_CY = 320
RULER_MINOR, RULER_MAJOR, RULER_LABEL_DY = 8, 14, 486
EVENT_DY = 524
FINGER_R = 18.0
FINGER_APPROACH = (-10.0, -40.0)          # the fingertip's offset at the start of its approach (band px)
CONTACT_DEG = {"plain": 180.0, "spun": 220.0}   # where the fingertip meets the rim (screen angle, y down)
COLOUR = {"plain": CORAL, "spun": TEAL}
DEG = math.pi / 180.0


def blend(col, a: float, base=BG) -> tuple:
    a = max(0.0, min(1.0, a))
    return tuple(int(round(c * a + b * (1 - a))) for c, b in zip(col, base))


# --- measurement --------------------------------------------------------------
class Contact:
    """The contact patch: a polar grid of cells with area weights, the Coulomb force and torque per unit mass."""

    def __init__(self, R: float, mu: float, g: float, nr: int, nt: int):
        r = (np.arange(nr) + 0.5) / nr * R
        th = (np.arange(nt) + 0.5) / nt * (2.0 * math.pi)
        rr, tt = np.meshgrid(r, th, indexing="ij")
        self.w = (rr * (R / nr) * (2.0 * math.pi / nt) / (math.pi * R * R)).ravel()
        self.x = (rr * np.cos(tt)).ravel()
        self.y = (rr * np.sin(tt)).ravel()
        self.R, self.mu, self.g, self.nr, self.nt = R, mu, g, nr, nt
        self.I = R * R / 2.0                      # the disc's moment of inertia per unit mass
        self.I_grid = float((self.w * (self.x ** 2 + self.y ** 2)).sum())
        self.w_sum = float(self.w.sum())
        self.mean_r = float((self.w * np.hypot(self.x, self.y)).sum())

    def force(self, v: float, om: float) -> tuple[float, float, float]:
        """(ax, ay, torque) per unit mass: -mu g times the area-weighted mean unit slip direction, and its moment."""
        ux = v - om * self.y
        uy = om * self.x
        n = np.hypot(ux, uy)
        n = np.where(n < 1e-15, 1e-15, n)
        mg = self.mu * self.g
        fx = -mg * float((self.w * ux / n).sum())
        fy = -mg * float((self.w * uy / n).sum())
        tz = -mg * float((self.w * (self.x * uy - self.y * ux) / n).sum())
        return fx, fy, tz

    def deriv(self, s: np.ndarray) -> tuple[np.ndarray, float]:
        """s = (x, v, theta, omega); returns s' and the sideways force (zero by symmetry)."""
        fx, fy, tz = self.force(float(s[1]), float(s[3]))
        return np.array([s[1], fx, s[3], tz / self.I]), fy


def run(c: Contact, v0: float, om0: float, dt: float, stop: float) -> dict:
    """RK4 from the push until |v| < stop and R |omega| < stop. Returns the table and the end state."""
    s = np.array([0.0, v0, 0.0, om0])
    rows = [(0.0, 0.0, v0, 0.0, om0)]
    k_v = 0 if abs(v0) < stop else None
    k_w = 0 if c.R * abs(om0) < stop else None
    fy_max = 0.0
    n = 0
    while k_v is None or k_w is None:
        k1, f1 = c.deriv(s)
        k2, f2 = c.deriv(s + 0.5 * dt * k1)
        k3, f3 = c.deriv(s + 0.5 * dt * k2)
        k4, f4 = c.deriv(s + dt * k3)
        fy_max = max(fy_max, abs(f1), abs(f2), abs(f3), abs(f4))
        s = s + dt / 6.0 * (k1 + 2.0 * k2 + 2.0 * k3 + k4)
        n += 1
        rows.append((n * dt, float(s[0]), float(s[1]), float(s[2]), float(s[3])))
        if k_v is None and abs(s[1]) < stop:
            k_v = n
        if k_w is None and c.R * abs(s[3]) < stop:
            k_w = n
        assert n < 200000, "the run does not stop"
    arr = np.array(rows)
    out = {"t": arr[:, 0], "x": arr[:, 1], "v": arr[:, 2], "theta": arr[:, 3], "om": arr[:, 4], "steps": n,
           "t_stop": n * dt, "x_stop": float(s[0]), "v_end": float(s[1]), "om_end": float(s[3]),
           "theta_end": float(s[2]), "k_v": k_v, "k_w": k_w, "fy_max": fy_max, "v0": v0, "om0": om0, "dt": dt}
    # Zero crossings of v and of omega extrapolated linearly from the last two rows.
    if n >= 2:
        t1, t2 = arr[-2, 0], arr[-1, 0]
        v1, v2 = arr[-2, 2], arr[-1, 2]
        w1, w2 = arr[-2, 4], arr[-1, 4]
        out["t_v0"] = t2 + v2 * (t2 - t1) / (v1 - v2) if v1 != v2 else math.nan
        out["t_w0"] = t2 + w2 * (t2 - t1) / (w1 - w2) if w1 != w2 else math.nan
    fx, _, tz = c.force(float(s[1]), float(s[3])) if abs(om0) > 0 else (-c.mu * c.g, 0.0, 0.0)
    out["share_slide"] = abs(fx) / (c.mu * c.g)
    out["share_spin"] = abs(tz) / (c.mu * c.g * c.mean_r)
    out["eps_end"] = float(s[1]) / (c.R * float(s[3])) if abs(s[3]) > 1e-12 else math.nan
    out["E0"] = 0.5 * v0 * v0 + 0.5 * c.I * om0 * om0
    out["E_end"] = 0.5 * float(s[1]) ** 2 + 0.5 * c.I * float(s[3]) ** 2
    return out


def state_at(r: dict, rt: float) -> dict:
    """(x, v, theta, omega, stopped) rt real seconds after the push; at rest before it, held after the stop."""
    if rt < 0.0:
        return {"x": 0.0, "v": 0.0, "theta": 0.0, "om": 0.0, "stopped": False}
    if rt >= r["t_stop"]:
        return {"x": r["x_stop"], "v": 0.0, "theta": r["theta_end"], "om": 0.0, "stopped": True}
    return {"x": float(np.interp(rt, r["t"], r["x"])), "v": float(np.interp(rt, r["t"], r["v"])),
            "theta": float(np.interp(rt, r["t"], r["theta"])), "om": float(np.interp(rt, r["t"], r["om"])),
            "stopped": False}


def measure(man: dict) -> dict:
    g, R, mu, v0, om0 = man["g"], man["radius_m"], man["grip"], man["push_speed_m_s"], man["spin_rad_s"]
    dt, nr, nt, stop = man["dt_s"], man["grid_radial"], man["grid_angular"], man["stop_speed_m_s"]
    S, P, D, fps, F, na = man["slow"], man["cycle_s"], man["scene_duration"], man["fps"], man["reset_fade"], man["push_at"]
    ppm = man["px_per_m"]
    cycles = D / P
    assert abs(cycles - round(cycles)) < 1e-9, "the cycle must divide the scene length"
    for key in ("cycle_s", "push_at", "first_cycle_at", "reset_fade", "finger_s"):
        assert abs(man[key] * fps - round(man[key] * fps)) < 1e-9, f"{key} must be a whole number of frames"
    mg = mu * g
    c = Contact(R, mu, g, nr, nt)
    turns = om0 / (2.0 * math.pi)
    print(f"setup: the same table in both bands, seen from above: a uniform disc of radius {R * 100:g} cm ({R * 200:g} cm "
          f"coaster, I = m R^2 / 2) on a table with grip mu = {mu:g}, the same everywhere under it (chosen); g = {g:g} "
          f"m/s^2; each coaster gets the same push, its centre leaving at v0 = {v0:g} m/s (chosen); top band the plain "
          f"coaster, no spin; bottom band the spun coaster, the same {v0:g} m/s and omega0 = {om0:g} rad/s = {turns:.2f} "
          f"turns a second (rim speed R omega0 = {R * om0:.2f} m/s = {R * om0:.3f} m/s); Coulomb friction with uniform "
          f"pressure integrated over the contact on a polar grid of {nr} radial by {nt} angular cells ({nr * nt} cells): "
          f"the force per unit mass is -mu g times the area-weighted mean unit slip direction, the torque per unit mass "
          f"about the centre likewise; x, v, theta and omega by classical RK4 at dt = {dt:g} s = {dt:.0e} s (x by the "
          f"same RK4 stages); a run stops when |v| < {stop:g} m/s and R |omega| < {stop:g} m/s; shown at 1/{S:g} speed "
          f"on a {P:g} s cycle ({P * fps:.0f} frames) with the push {na:g} s into the cycle, {cycles:.0f} cycles in "
          f"{D:g} s; drawn at {ppm:g} px per metre; deterministic, no seed")
    # Grid checks and the pure cases.
    fx_slide, fy_slide, tz_slide = c.force(v0, 0.0)
    fx_spin, fy_spin, tz_spin = c.force(0.0, om0)
    alpha_spin = -tz_spin / c.I
    alpha_closed = 4.0 * mg / (3.0 * R)
    print(f"grid: the {nr} x {nt} area weights sum to {c.w_sum:.12f} (1 - sum {1.0 - c.w_sum:+.1e}); the grid's "
          f"I_c = <r^2> = {c.I_grid:.9e} m^2 against R^2 / 2 = {c.I:.9e} m^2 (diff {c.I_grid - c.I:+.2e} m^2, "
          f"{(c.I_grid - c.I) / c.I:+.1e} relative); <r> = {c.mean_r:.6f} m against 2 R / 3 = {2 * R / 3:.6f} m "
          f"(diff {c.mean_r - 2 * R / 3:+.1e} m); pure slide (omega = 0) at {v0:g} m/s: the quadrature gives "
          f"{fx_slide:.9f} m/s^2 against -mu g = {-mg:.9f} m/s^2 (diff {fx_slide + mg:+.1e}), sideways {fy_slide:+.1e}, "
          f"torque {tz_slide:+.1e}; pure spin (v = 0) at {om0:g} rad/s: force {fx_spin:+.1e}, {fy_spin:+.1e} m/s^2, "
          f"torque {tz_spin:.6e} m^2/s^2 = -mu g <r> ({-mg * c.mean_r:.6e}), so alpha = {alpha_spin:.4f} rad/s^2 "
          f"against the closed form 4 mu g / (3 R) = {alpha_closed:.4f} rad/s^2 (diff {alpha_spin - alpha_closed:+.1e}): "
          f"a spin-only coaster would stop after omega0 / alpha = {om0 / alpha_closed:.4f} s")
    assert abs(c.w_sum - 1.0) < 1e-12 and abs(c.I_grid - c.I) < 1e-5
    assert abs(fx_slide + mg) < 1e-9 and abs(fy_slide) < 1e-9 and abs(tz_slide) < 1e-9
    # The plain run.
    plain = run(c, v0, 0.0, dt, stop)
    t_pc, x_pc = v0 / mg, v0 * v0 / (2.0 * mg)
    print(f"plain coaster ({v0:g} m/s, no spin): the friction is the full mu g = {mg:.4f} m/s^2 against the slide, so v "
          f"falls at a steady {mg:.4f} m/s^2; it stops (|v| under {stop:g} m/s) at {plain['t_stop']:.4f} s on step "
          f"{plain['steps']} after {plain['x_stop'] * 100:.4f} cm = {plain['x_stop'] * 100:.2f} cm = "
          f"{plain['x_stop'] * 100:.0f} cm (closed form v0 / (mu g) = {t_pc:.4f} s to v = 0, v0^2 / (2 mu g) = "
          f"{x_pc * 100:.4f} cm = {x_pc * 100:.2f} cm; the quadrature stop comes {t_pc - plain['t_stop']:.1e} s before "
          f"v would reach zero, {(x_pc - plain['x_stop']) * 100:.1e} cm short of the closed distance); v left "
          f"{plain['v_end']:.2e} m/s; sideways force at most {plain['fy_max']:.1e} m/s^2; energy per unit mass "
          f"{plain['E0']:.4f} J/kg at the push, {plain['E_end']:.1e} J/kg at the stop")
    assert abs(plain["x_stop"] - x_pc) < 1e-4 and abs(plain["t_stop"] - t_pc) < 1e-3
    # The spun run.
    spun = run(c, v0, om0, dt, stop)
    ratio = spun["x_stop"] / plain["x_stop"]
    gap = abs(spun["k_v"] - spun["k_w"])
    print(f"spun coaster ({v0:g} m/s and {om0:g} rad/s): it stops at {spun['t_stop']:.4f} s on step {spun['steps']} after "
          f"{spun['x_stop'] * 100:.4f} cm = {spun['x_stop'] * 100:.2f} cm = {spun['x_stop'] * 100:.0f} cm, "
          f"{ratio:.4f} = {ratio:.3f} times the plain coaster's {plain['x_stop'] * 100:.2f} cm; |v| fell under "
          f"{stop:g} m/s on step {spun['k_v']} ({spun['k_v'] * dt:.4f} s) and R |omega| on step {spun['k_w']} "
          f"({spun['k_w'] * dt:.4f} s): {gap} step{'s' if gap != 1 else ''} = {gap * dt * 1000:.1f} ms apart; the zero "
          f"crossings extrapolated from the last two steps: v at {spun['t_v0']:.5f} s, omega at {spun['t_w0']:.5f} s, "
          f"{abs(spun['t_v0'] - spun['t_w0']) * 1000:.3f} ms apart (the slide and the spin end at the same instant); at "
          f"the stop v = {spun['v_end']:.2e} m/s, R omega = {R * spun['om_end']:.2e} m/s, v / (R omega) = "
          f"{spun['eps_end']:.3f} (Farkas et al. PRL 2003: 0.653); at the end the slide feels {spun['share_slide']:.4f} "
          f"= {spun['share_slide']:.3f} of mu g = {spun['share_slide'] * 100:.0f} percent of the friction and the spin "
          f"feels {spun['share_spin']:.3f} of the pure-spin torque; it turned {spun['theta_end'] / (2 * math.pi):.3f} "
          f"turns; sideways force at most {spun['fy_max']:.1e} m/s^2; energy per unit mass 0.5 v0^2 + 0.25 R^2 omega0^2 = "
          f"{spun['E0']:.4f} J/kg at the push, {spun['E_end']:.1e} J/kg at the stop")
    assert spun["k_v"] is not None and spun["k_w"] is not None
    assert abs(spun["t_v0"] - spun["t_w0"]) < 1e-3, "the slide and the spin do not end together"
    # The table every table_every_s.
    rows = []
    every = man["table_every_s"]
    for k in range(int(math.floor(spun["t_stop"] / every + 1e-9)) + 1):
        tt = k * every
        st = state_at(spun, tt)
        eps = st["v"] / (R * st["om"]) if abs(st["om"]) > 1e-12 else math.nan
        rows.append(f"{tt:.2f} s: v {st['v']:.4f} m/s, R omega {R * st['om']:.4f} m/s ({st['om'] / (2 * math.pi):.2f} "
                    f"turns/s), v / (R omega) {eps:.3f}")
    rows.append(f"{spun['t_stop']:.4f} s (stop): v {spun['v_end']:.4f} m/s, R omega {R * spun['om_end']:.4f} m/s, "
                f"v / (R omega) {spun['eps_end']:.3f}")
    print("spun coaster table: " + "; ".join(rows))
    # Half step.
    half = run(c, v0, om0, 0.5 * dt, stop)
    print(f"half-step rerun (dt = {0.5 * dt:g} s): the spun coaster stops at {half['t_stop']:.5f} s after "
          f"{half['x_stop'] * 100:.5f} cm ({(half['x_stop'] - spun['x_stop']) * 1000:+.2e} mm, "
          f"{half['t_stop'] - spun['t_stop']:+.1e} s against the full step), v / (R omega) {half['eps_end']:.3f}")
    assert abs(half["x_stop"] - spun["x_stop"]) < 1e-4
    ev: dict = {"c": c, "plain": plain, "spun": spun, "ratio": ratio, "half": half, "turns": turns}
    # Variants for the description.
    descr = []
    var = {}
    for om in man["description_spins_rad_s"]:
        rv = run(c, v0, om, dt, stop)
        var[("spin", om)] = rv
        descr.append(f"{v0:g} m/s with {om:g} rad/s ({om / (2 * math.pi):.2f} turns/s, rim {R * om:.2f} m/s): stops at "
                     f"{rv['t_stop']:.4f} s after {rv['x_stop'] * 100:.2f} cm, {rv['x_stop'] / plain['x_stop']:.3f} times "
                     f"the plain {plain['x_stop'] * 100:.2f} cm, v / (R omega) at the end {rv['eps_end']:.3f}, energy at "
                     f"the push {rv['E0']:.4f} J/kg")
    for vv in man["description_speeds_m_s"]:
        rp = run(c, vv, 0.0, dt, stop)
        rv = run(c, vv, om0, dt, stop)
        var[("speed", vv)] = (rp, rv)
        descr.append(f"{vv:g} m/s: plain stops at {rp['t_stop']:.4f} s after {rp['x_stop'] * 100:.2f} cm (closed form "
                     f"{vv * vv / (2 * mg) * 100:.2f} cm); with {om0:g} rad/s it stops at {rv['t_stop']:.4f} s after "
                     f"{rv['x_stop'] * 100:.2f} cm, {rv['x_stop'] / rp['x_stop']:.3f} times as far")
    spin_only = {}
    for om in (om0, 40.0):
        rs = run(c, 0.0, om, dt, stop)
        spin_only[om] = rs
        descr.append(f"spin only, {om:g} rad/s and no push: moves {abs(rs['x_stop']) * 100:.3f} cm and stops at "
                     f"{rs['t_stop']:.4f} s (closed form 3 R omega0 / (4 mu g) = {3 * R * om / (4 * mg):.4f} s)")
    print("for the description: " + "; ".join(descr))
    ev["var"], ev["spin_only"] = var, spin_only
    # The brief's checks.
    v40 = var[("spin", 40.0)]
    checks: list[tuple[str, float, float, float]] = [
        ("plain stop, closed form v0 / (mu g) (s)", t_pc, 0.3399, 6e-5),
        ("plain distance, closed form v0^2 / (2 mu g) (cm)", x_pc * 100, 16.99, 6e-3),
        ("plain stop, quadrature (s)", plain["t_stop"], 0.3394, 6e-5),
        ("plain distance, quadrature (cm)", plain["x_stop"] * 100, 16.99, 6e-3),
        ("spun distance (cm)", spun["x_stop"] * 100, 33.99, 6e-3),
        ("spun stop (s)", spun["t_stop"], 0.6554, 6e-5),
        ("ratio spun / plain", ratio, 2.000, 6e-4),
        ("40.0 rad/s distance (cm)", v40["x_stop"] * 100, 33.43, 6e-3),
        ("40.0 rad/s stop (s)", v40["t_stop"], 0.6462, 6e-5),
        ("40.0 rad/s ratio", v40["x_stop"] / plain["x_stop"], 1.967, 6e-4),
        ("v / (R omega) at the stop, in 0.64 to 0.66", spun["eps_end"], 0.65, 0.01),
        ("slide friction at the fixed point (of mu g)", spun["share_slide"], 0.616, 0.01),
        ("spin only at 40.0 rad/s stops (s)", spin_only[40.0]["t_stop"], 0.5098, 1e-3),
        ("spin only at 40.87 rad/s stops, closed form 3 R omega0 / (4 mu g) (s)", spin_only[om0]["t_stop"],
         3 * R * om0 / (4 * mg), 1e-3),
        ("spin only moves (cm)", spin_only[om0]["x_stop"] * 100, 0.0, 1e-6),
        ("pure slide quadrature (of mu g)", -fx_slide / mg, 1.0, 1e-12),
        ("grid weights sum", c.w_sum, 1.0, 1e-12),
        ("grid I_c against R^2 / 2 (m^2)", c.I_grid, c.I, 1e-5),
        ("energy at the push with 40.0 rad/s (J/kg)", v40["E0"], 1.5, 1e-9),
        ("energy at the push with 40.87 rad/s, 0.5 v0^2 + 0.25 R^2 omega0^2 (J/kg)", spun["E0"],
         0.5 * v0 * v0 + 0.25 * R * R * om0 * om0, 1e-12),
        ("energy at the stop (J/kg)", spun["E_end"], 0.0, 1e-5),
        ("half step changes the stop distance (m)", half["x_stop"] - spun["x_stop"], 0.0, 1e-4),
        ("zero crossings of v and omega apart (ms)", (spun["t_v0"] - spun["t_w0"]) * 1000, 0.0, 1.0),
    ]
    fails = 0
    out = []
    for name, got, want, tol in checks:
        ok = abs(got - want) <= tol
        fails += 0 if ok else 1
        out.append(f"{name}: brief {want:.6g}, sim {got:.6g}, diff {got - want:+.1e}: {'ok' if ok else 'FAIL'}")
    same = gap <= 3
    fails += 0 if same else 1
    out.append(f"|v| and R |omega| fall under {stop:g} m/s on the same step: brief 0 steps apart, sim {gap} steps "
               f"({gap * dt * 1000:.1f} ms) apart, within 3 steps: {'ok' if same else 'FAIL'}")
    print(f"checks against the brief ({len(checks) + 1} checks, {fails} failed): " + "; ".join(out))
    assert fails == 0, "a check against the brief failed"
    ev["check_count"] = len(checks) + 1
    # Geometry on screen.
    x0 = float(man["start_x_px"])
    disc_px = R * ppm
    stop_px = {m: x0 + ev[m]["x_stop"] * ppm for m in PANELS}
    print(f"drawing: {ppm:g} px per metre; each coaster {2 * disc_px:.0f} px across; the start line at x {x0:.0f}; the "
          f"plain coaster stops with its centre at x {stop_px['plain']:.1f} px (brief 490), the spun one at x "
          f"{stop_px['spun']:.1f} px (brief 830); the discs span x {x0 - disc_px:.0f} to {stop_px['spun'] + disc_px:.0f} "
          f"px on a table from x {TABLE_X0} to {TABLE_X1} ({TABLE_X1 - stop_px['spun'] - disc_px:.0f} px of margin on "
          f"the right); the spun coaster turns {spun['theta_end'] / (2 * math.pi):.2f} turns, "
          f"{om0 / (2 * math.pi) / S / fps * 360:.1f} deg per frame at the push")
    assert abs(stop_px["plain"] - 490) < 3 and abs(stop_px["spun"] - 830) < 3
    assert x0 - disc_px > TABLE_X0 + 10 and stop_px["spun"] + disc_px < TABLE_X1 - 60, "a disc leaves the table"
    assert DISC_CY - disc_px > TABLE_Y0 + 10 and DISC_CY + disc_px < TABLE_Y1 - 10, "a disc leaves the table vertically"
    # The schedule in video time.
    t0 = man["first_cycle_at"]
    k0 = math.ceil((0.0 - t0) / P - 1e-9) - 1
    k1 = math.floor((D - t0) / P - 1e-9)
    starts = [t0 + kk * P for kk in range(k0, k1 + 1)]

    def lst(off_: float) -> str:
        return ", ".join(f"{st + off_:.2f}" for st in starts if 0.0 <= st + off_ < D)

    stop_v = {m: na + S * ev[m]["t_stop"] for m in PANELS}
    ev["stop_v"] = stop_v
    assert stop_v["spun"] + 0.5 < P - F, "the spun coaster is still moving at the reset fade"
    print(f"schedule (video time, 1/{S:g} speed): cycles of {P:g} s start at " + ", ".join(f"{st:.2f}" for st in starts)
          + f" s; the fingertips move in over the first {man['finger_s']:g} s and push both coasters {na:g} s into each "
          f"cycle at {lst(na)} s; the plain coaster stops {S * plain['t_stop']:.3f} s after the push at "
          f"{lst(stop_v['plain'])} s (its event row lights); the spun coaster stops {S * spun['t_stop']:.3f} s after the "
          f"push at {lst(stop_v['spun'])} s (its event row lights), {stop_v['spun'] - stop_v['plain']:.2f} s after the "
          f"plain one; both hold until the reset crossfade over the last {F:g} s of each cycle (from {lst(P - F)} s); "
          f"title until {man['title_until']:g} s; payoff card from {man['payoff_t']:g} s; the title fades back in over "
          f"the last {man['loop_fade']:g} s and the last frame repeats the first (the scene is periodic: {D:g} s holds "
          f"exactly {cycles:.0f} cycles)")
    # Text widths.
    font = os.environ["SEED_ZERO_FONT"]
    f24, f28, f34, f40, f56 = (ImageFont.truetype(font, n) for n in (24, 28, 34, 40, 56))
    widths = {"overlay@34": (f34, man["overlay"])}
    for j, line in enumerate(man["title"].split("|")):
        widths[f"title line {j + 1}@56"] = (f56, line)
    widths["legend@40"] = (f40, legend_text(man))
    for m in PANELS:
        widths[f"label {m}@40"] = (f40, label_text(man, ev, m))
        widths[f"sublabel {m}@28"] = (f28, sub_text(man))
        widths[f"event {m}@28"] = (f28, event_text(ev, m))
    widths["speed@28"] = (f28, speed_text(v0))
    widths["clock@28"] = (f28, clock_text(0.6554))
    widths["clock held@28"] = (f28, clock_text(-1.0))
    widths["slid@28"] = (f28, slid_text(spun["x_stop"]))
    widths["spin@28"] = (f28, spin_text(om0))
    widths["no spin@28"] = (f28, nospin_text())
    for j, lab in enumerate(ruler_labels()):
        widths[f"ruler label {j + 1}@24"] = (f24, lab)
    for j, line in enumerate(payoff_lines(man, ev)):
        widths[f"payoff line {j + 1}@40"] = (f40, line)
    print("text widths (the on-screen strings verbatim): " + ", ".join(f"{kk} {f.getlength(s):.0f} px '{s}'"
                                                                      for kk, (f, s) in widths.items()))
    assert all(f.getlength(s) < 950 for f, s in widths.values()), "a text line is wider than 950 px"
    assert len(payoff_lines(man, ev)) <= 6, "the card has more than six lines"
    assert len(man["title"].split("|")) in TITLE_YS
    # Layout checks (band-local boxes).
    rw = max(f28.getlength(slid_text(spun["x_stop"])), f28.getlength(spin_text(om0)), f28.getlength(nospin_text()))
    right = ROW_X1 - rw
    ev_w = max(f28.getlength(event_text(ev, m)) for m in PANELS)
    rl = ruler_labels()
    rl_x0 = x0 - f24.getlength(rl[0]) / 2.0
    rl_x1 = x0 + (len(rl) - 1) * 200.0 + f24.getlength(rl[-1]) / 2.0
    # The fingertip's reach: its approach start for each band.
    finger_top = math.inf
    finger_left = math.inf
    for m in PANELS:
        a = CONTACT_DEG[m] * DEG
        fx_ = x0 + (disc_px + FINGER_R + 2.0) * math.cos(a) + FINGER_APPROACH[0]
        fy_ = DISC_CY + (disc_px + FINGER_R + 2.0) * math.sin(a) + FINGER_APPROACH[1]
        finger_top = min(finger_top, fy_ - FINGER_R)
        finger_left = min(finger_left, fx_ - FINGER_R)
    left_lab = ROW_X0 + max(max(f40.getlength(label_text(man, ev, m)) for m in PANELS), f28.getlength(sub_text(man)))
    left_rd = ROW_X0 + max(f28.getlength(speed_text(v0)), f28.getlength(clock_text(0.6554)), f28.getlength(clock_text(-1.0)))
    boxes = {"left labels": (ROW_X0 - 8, LABEL_DY - 28, left_lab + 8, SUB_DY + 16),
             "left readouts": (ROW_X0 - 8, SPEED_DY - 16, left_rd + 8, CLOCK_DY + 16),
             "right readouts": (right - 8, SPEED_DY - 16, ROW_X1 + 8, CLOCK_DY + 16),
             "table": (TABLE_X0, TABLE_Y0, TABLE_X1, TABLE_Y1 + RULER_MAJOR),
             "ruler labels": (rl_x0 - 4, RULER_LABEL_DY - 13, rl_x1 + 4, RULER_LABEL_DY + 13),
             "event row": (ROW_X0 - 8, EVENT_DY - 20, ROW_X0 + ev_w + 8, EVENT_DY + 20)}
    print(f"row check: the left label rows span x {ROW_X0} to {left_lab:.0f} px and y {LABEL_DY - 20} to {SUB_DY + 14} under "
          f"the band top, the left readouts x {ROW_X0} to {left_rd:.0f} and y {SPEED_DY - 14} to {CLOCK_DY + 14}; the right "
          f"readouts x {right:.0f} to {ROW_X1} and y {SPEED_DY - 14} to {CLOCK_DY + 14}; the table x "
          f"{TABLE_X0} to {TABLE_X1}, y {TABLE_Y0} to {TABLE_Y1} with its ruler ticks to {TABLE_Y1 + RULER_MAJOR} and the "
          f"ruler labels x {rl_x0:.0f} to {rl_x1:.0f} at y {RULER_LABEL_DY - 12} to {RULER_LABEL_DY + 12}; the coasters' "
          f"centre line at y {DISC_CY}, the discs from y {DISC_CY - disc_px:.0f} to {DISC_CY + disc_px:.0f}; the "
          f"fingertips reach up to y {finger_top:.0f} and left to x {finger_left:.0f}; the event row x {ROW_X0} to "
          f"{ROW_X0 + ev_w:.0f} (widest {ev_w:.0f} px) at y {EVENT_DY - 16} to {EVENT_DY + 16}; each band is {BAND_H} px "
          f"tall (y {BAND_Y['plain']} to {BAND_Y['plain'] + BAND_H} and {BAND_Y['spun']} to {BAND_Y['spun'] + BAND_H}); "
          f"the caption band starts at y {int(man['caption_y'] * H)}; the title rows end at y "
          f"{TITLE_YS[len(man['title'].split('|'))][-1] + 28}, the band text starts at y {BAND_Y['plain'] + LABEL_DY - 20}; "
          f"the legend at y {LEGEND_Y}; the overlay band ends at y 130; the card from y {PAYOFF_Y:.0f} to "
          f"{PAYOFF_Y + (len(payoff_lines(man, ev)) - 1) * PAYOFF_PITCH + 20:.0f}")
    for a_name, a_box in boxes.items():
        for b_name, b_box in boxes.items():
            if a_name < b_name:
                sep = a_box[2] <= b_box[0] or b_box[2] <= a_box[0] or a_box[3] <= b_box[1] or b_box[3] <= a_box[1]
                assert sep, f"{a_name} meets {b_name}"
    assert right - left_rd > 40, "the readout columns meet"
    assert left_lab < ROW_X1 - 40, "a label row reaches the right margin"
    assert finger_top > CLOCK_DY + 14 + 2, "a fingertip meets the clock row"
    assert finger_left >= 0.0, "a fingertip leaves the frame"
    assert EVENT_DY + 20 <= BAND_H, "the event row leaves the band"
    assert rl_x1 < W - 20
    assert BAND_Y["spun"] + BAND_H <= int(man["caption_y"] * H), "the bottom band reaches the caption band"
    assert PAYOFF_Y - 20 > int(man["caption_y"] * H) + 90, "the card meets the caption band"
    assert PAYOFF_Y + (len(payoff_lines(man, ev)) - 1) * PAYOFF_PITCH + 20 < H - 40, "the card leaves the frame"
    assert TITLE_YS[len(man["title"].split("|"))][-1] + 28 <= BAND_Y["plain"] + LABEL_DY - 20, "the title meets the bands"
    return ev


def legend_text(man: dict) -> str:
    return f"same table, same push, 1/{man['slow']:g} speed"


def clock_text(r: float) -> str:
    return "before the push" if r < 0.0 else f"{r:.3f} s after the push"


def label_text(man: dict, ev: dict, m: str) -> str:
    return "plain coaster" if m == "plain" else f"spun coaster, {ev['turns']:.1f} turns a second"


def sub_text(man: dict) -> str:
    return f"same push, {man['push_speed_m_s']:g} m/s"


def speed_text(v: float) -> str:
    return f"speed {v:.2f} m/s"


def slid_text(x: float) -> str:
    return f"slid {x * 100:.1f} cm"


def spin_text(om: float) -> str:
    return f"spin {om / (2 * math.pi):.1f} turns/s"


def nospin_text() -> str:
    return "no spin"


def event_text(ev: dict, m: str) -> str:
    r = ev[m]
    if m == "plain":
        return f"plain: stopped at {r['t_stop']:.2f} s, {r['x_stop'] * 100:.0f} cm"
    return f"spun: stopped at {r['t_stop']:.2f} s, {r['x_stop'] * 100:.0f} cm, spin and slide together"


def ruler_labels() -> list[str]:
    return ["0", "10", "20", "30", "40 cm"]


def payoff_lines(man: dict, ev: dict) -> list[str]:
    text = man["payoff_text"].format(d_plain_cm=ev["plain"]["x_stop"] * 100, t_plain=ev["plain"]["t_stop"],
                                     d_spun_cm=ev["spun"]["x_stop"] * 100, t_spun=ev["spun"]["t_stop"],
                                     ratio=ev["ratio"], share_pct=ev["spun"]["share_slide"] * 100)
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
        self.font_tiny = ImageFont.truetype(font, 24)
        self.font_event = ImageFont.truetype(font, 28)
        self.ppm = float(man["px_per_m"])
        self.S = man["slow"]
        self.P = man["cycle_s"]
        self.P_f = int(round(man["cycle_s"] * self.fps))
        self.c0_f = int(round(man["first_cycle_at"] * self.fps))
        self.na, self.F = man["push_at"], man["reset_fade"]
        self.x0 = float(man["start_x_px"])
        self.disc = man["radius_m"] * self.ppm

    def phase(self, f: int) -> tuple[int, float]:
        k, tau_f = divmod(f - self.c0_f, self.P_f)
        return k, tau_f / self.fps

    @staticmethod
    def L_(x: float, y: float) -> tuple[float, float]:
        """Layer (2x) pixel of a band-local point, rounded to 1e-4 px so equal states draw equal pixels."""
        return round(x * SS, 4), round(y * SS, 4)

    def draw_table(self, d: ImageDraw.ImageDraw, m: str, st: dict) -> None:
        L_ = self.L_
        s0, s1 = L_(TABLE_X0, TABLE_Y0), L_(TABLE_X1, TABLE_Y1)
        d.rounded_rectangle((s0[0], s0[1], s1[0], s1[1]), radius=8 * SS, fill=DECK_A, outline=DECK_B, width=2 * SS)
        # The start line.
        a0, a1 = L_(self.x0, TABLE_Y0 + 10), L_(self.x0, TABLE_Y1 - 10)
        d.line((*a0, *a1), fill=blend(RIM, 0.7, DECK_A), width=2 * SS)
        # The cm ruler under the table's lower edge (its labels are drawn at 1x).
        for k in range(0, 46):
            xx = self.x0 + k * self.ppm / 100.0
            if xx > TABLE_X1:
                break
            h = RULER_MAJOR if k % 5 == 0 else RULER_MINOR
            t0, t1 = L_(xx, TABLE_Y1), L_(xx, TABLE_Y1 + h)
            d.line((*t0, *t1), fill=RIM, width=(2 if k % 5 == 0 else 1) * SS)
        if st["stopped"]:
            xs = self.x0 + st["x"] * self.ppm
            t0, t1 = L_(xs, TABLE_Y1), L_(xs, TABLE_Y1 + RULER_MAJOR)
            d.line((*t0, *t1), fill=GOLD, width=3 * SS)

    def draw_coaster(self, d: ImageDraw.ImageDraw, m: str, cx: float, cy: float, theta: float) -> None:
        """A coaster from above: the disc in the band colour, a dark stripe from the centre to the rim at the
        body turn theta (counterclockwise on screen) and a centre dot."""
        col = COLOUR[m]
        r = self.disc
        p0, p1 = self.L_(cx - r, cy - r), self.L_(cx + r, cy + r)
        d.ellipse((p0[0], p0[1], p1[0], p1[1]), fill=col, outline=blend(col, 0.55, STRIPE), width=3 * SS)
        tip = (cx + (r - 6.0) * math.cos(theta), cy - (r - 6.0) * math.sin(theta))
        d.line((*self.L_(cx, cy), *self.L_(*tip)), fill=STRIPE, width=14 * SS)
        c0, c1 = self.L_(cx - 7.0, cy - 7.0), self.L_(cx + 7.0, cy + 7.0)
        d.ellipse((c0[0], c0[1], c1[0], c1[1]), fill=STRIPE)

    def draw_finger(self, d: ImageDraw.ImageDraw, m: str, tau: float) -> None:
        """The fingertip seen from above: it moves in to the rim over finger_s, pushes at push_at, and pulls back."""
        na, fs = self.na, self.man["finger_s"]
        a = CONTACT_DEG[m] * DEG
        rim = (self.x0 + self.disc * math.cos(a), DISC_CY + self.disc * math.sin(a))
        touch = (self.x0 + (self.disc + FINGER_R + 2.0) * math.cos(a), DISC_CY + (self.disc + FINGER_R + 2.0) * math.sin(a))
        if tau < na:
            u = max(0.0, (tau - (na - fs)) / fs)
            k = 1.0 - u * u
            alpha = 1.0
        else:
            u = (tau - na) / 0.6
            if u >= 1.0:
                return
            k = u
            alpha = 1.0 - u
        cx = touch[0] + FINGER_APPROACH[0] * k
        cy = touch[1] + FINGER_APPROACH[1] * k
        p0, p1 = self.L_(cx - FINGER_R, cy - FINGER_R), self.L_(cx + FINGER_R, cy + FINGER_R)
        d.ellipse((p0[0], p0[1], p1[0], p1[1]), fill=blend(FINGER, alpha))
        nx, ny = cx + 5.0 * math.cos(a), cy + 5.0 * math.sin(a)
        n0, n1 = self.L_(nx - 8.0, ny - 8.0), self.L_(nx + 8.0, ny + 8.0)
        d.ellipse((n0[0], n0[1], n1[0], n1[1]), fill=blend(NAIL, alpha))
        if 0.0 <= tau - na < 0.3:
            b = 1.0 - (tau - na) / 0.3
            for ang in (-40.0, 0.0, 40.0):
                dx, dy = math.cos(a + math.pi + ang * DEG), math.sin(a + math.pi + ang * DEG)
                q0 = self.L_(rim[0] + 8.0 * dx, rim[1] + 8.0 * dy)
                q1 = self.L_(rim[0] + 20.0 * dx, rim[1] + 20.0 * dy)
                d.line((*q0, *q1), fill=blend(GOLD, b), width=2 * SS)

    def scene(self, m: str, tau: float) -> tuple[Image.Image, dict]:
        """The band layer of coaster m at tau seconds into a cycle (the resting setup before the push)."""
        layer = Image.new("RGB", (W * SS, BAND_H * SS), BG)
        d = ImageDraw.Draw(layer)
        tv = tau - self.na
        rt = tv / self.S
        st = state_at(self.ev[m], rt)
        self.draw_table(d, m, st)
        cx = self.x0 + st["x"] * self.ppm
        if rt > 0.0:
            d.line((*self.L_(self.x0, DISC_CY), *self.L_(cx, DISC_CY)), fill=blend(COLOUR[m], 0.45, DECK_A), width=2 * SS)
        self.draw_coaster(d, m, cx, DISC_CY, st["theta"])
        self.draw_finger(d, m, tau)
        st["tv"], st["rt"] = tv, rt
        return layer, st

    def draw_panel(self, m: str, f: int) -> tuple[Image.Image, dict]:
        k, tau = self.phase(f)
        P, F = self.P, self.F
        layer, st = self.scene(m, tau)
        st["alpha"], st["k"] = 1.0, k
        if tau >= P - F:
            a = (tau - (P - F)) / F
            new, st_new = self.scene(m, tau - P)
            layer = Image.blend(layer, new, a)
            st["alpha"] = max(0.0, 1.0 - 2.0 * a)
            st_new["alpha"], st_new["k"] = max(0.0, 2.0 * a - 1.0), k + 1
            if a >= 0.5:
                st = st_new
        return layer, st

    def draw_text(self, d: ImageDraw.ImageDraw, states: dict, hud_alpha: float) -> None:
        man, ev = self.man, self.ev
        for m, st in states.items():
            y0 = BAND_Y[m]
            a = st["alpha"]
            lit = st["stopped"]
            d.text((ROW_X0, y0 + LABEL_DY), label_text(man, ev, m), font=self.font, fill=COLOUR[m], anchor="lm")
            d.text((ROW_X0, y0 + SUB_DY), sub_text(man), font=self.font_small, fill=MUTED, anchor="lm")
            d.text((ROW_X0, y0 + SPEED_DY), speed_text(st["v"]), font=self.font_small, fill=blend(TEXT, a), anchor="lm")
            d.text((ROW_X0, y0 + CLOCK_DY), clock_text(st["rt"]), font=self.font_small, fill=blend(MUTED, a), anchor="lm")
            d.text((ROW_X1, y0 + SPEED_DY), slid_text(st["x"]), font=self.font_small, fill=blend(GOLD if lit else TEXT, a),
                   anchor="rm")
            if m == "spun":
                d.text((ROW_X1, y0 + CLOCK_DY), spin_text(st["om"]), font=self.font_small,
                       fill=blend(GOLD if lit else TEXT, a), anchor="rm")
            else:
                d.text((ROW_X1, y0 + CLOCK_DY), nospin_text(), font=self.font_small, fill=MUTED, anchor="rm")
            for j, lab in enumerate(ruler_labels()):
                d.text((self.x0 + j * 200.0, y0 + RULER_LABEL_DY), lab, font=self.font_tiny, fill=MUTED, anchor="mm")
            if lit:
                d.text((ROW_X0, y0 + EVENT_DY), event_text(ev, m), font=self.font_event, fill=blend(GOLD, a), anchor="lm")
        if hud_alpha > 0.02:
            d.text((W / 2, LEGEND_Y), legend_text(man), font=self.font, fill=blend(TEXT, hud_alpha), anchor="mm")

    def live_frame(self, f: int, title_alpha: float | None = None, hud_alpha: float = 0.0) -> np.ndarray:
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
        states = {}
        for m in PANELS:
            layer, states[m] = self.draw_panel(m, f)
            img.paste(layer.reduce(SS), (0, BAND_Y[m]))
        d = ImageDraw.Draw(img)
        self.draw_text(d, states, hud_alpha)
        if title_alpha > 0.0:
            rows = man["title"].split("|")
            for j, line in enumerate(rows):
                d.text((W / 2, TITLE_YS[len(rows)][j]), line, font=self.font_title, fill=blend(TEXT, title_alpha), anchor="mm")
        if t >= man["payoff_t"]:
            a = min(1.0, (t - man["payoff_t"]) / man["payoff_hold"]) * hud_alpha
            for j, line in enumerate(payoff_lines(man, self.ev)):
                d.text((W / 2, PAYOFF_Y + j * PAYOFF_PITCH), line, font=self.font, fill=blend(GOLD, a), anchor="mm")
        return np.asarray(img, dtype=np.uint8)

    def frame_at(self, f: int) -> np.ndarray:
        man = self.man
        total = int(round(man["scene_duration"] * self.fps))
        fade_frames = int(round(man["loop_fade"] * self.fps))
        if f == total - 1:
            return self.live_frame(0)   # the scene is periodic: the last frame repeats the first
        if f >= total - fade_frames:
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
        wrap = self.live_frame(total, title_alpha=1.0, hud_alpha=0.0)
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
        workers = min(12, os.cpu_count() or 1)
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
    man = json.loads((ROOT / "projects/spinslide/manifest.json").read_text())
    ev = measure(man)
    if "--measure-only" in sys.argv:
        return
    if "--frames" in sys.argv:
        times = [float(v) for v in sys.argv[sys.argv.index("--frames") + 1].split(",")]
        r = Renderer(man, ev)
        (ROOT / "media/spinslide").mkdir(parents=True, exist_ok=True)
        for tv in times:
            Image.fromarray(r.frame_at(int(round(tv * man["fps"])))).save(ROOT / f"media/spinslide/smoke-{tv}.png")
        print("smoke frames: " + ", ".join(f"{tv}" for tv in times))
        return
    Renderer(man, ev).render(ROOT / "media/spinslide/footage.mp4")


if __name__ == "__main__":
    main()
