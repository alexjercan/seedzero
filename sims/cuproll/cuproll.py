#!/usr/bin/env python3
"""Paper cup or straight can: nudge both the same, which one rolls off the desk?

One top-down desk scene, real time. A thin-walled paper cup (top diameter
2 Rt, bottom diameter 2 rb, height h: the wall plus a bottom disc of the
same sheet) lies on its side and a straight can of diameter 2 r lies next
to it, both with their axes parallel to the desk edge, both d from the
edge, on a level desk with grip mu (chosen). Each gets the same nudge: its
centre moves off toward the edge at v (chosen). The CAN is a cylinder: it
rolls straight without loss (chosen), reaches the edge after d / v, leaves
the desk as its centre passes the edge and falls freely from a desk H
high (t = sqrt(2 H / g), landing v t out). The CUP is a slice of a cone of
slant length sqrt(h^2 + (Rt - rb)^2) and half-angle alpha, sin alpha =
(Rt - rb) / slant. Rolling without slipping it pivots about the apex of
that cone, which lies l1 = rb / sin alpha beyond the small rim and l2 =
Rt / sin alpha from the large rim along the contact line (the generator
on the desk). Its angular velocity lies along the contact line, omega_g =
-Omega cot alpha, and in the frame turning with the axis the cup spins
about its own axis at omega_s = Omega / sin alpha, where Omega is the rate
at which the axis (and the contact line) turns about the vertical through
the apex: Omega = v / rho with rho = d_cm cos alpha the radius of the
centre of mass's circle (d_cm its distance from the apex along the axis).
Both rims run on circles of radii l1 and l2 about the apex, so the cup
turns l1 / rb = l2 / Rt = 1 / sin alpha times per lap, its centre of mass
rides at the constant height d_cm sin alpha (energy kept), and it is back
at its start after 2 pi rho / v. The dynamics are a closed form: N = m g
(the height is constant), the friction needed is v^2 / (g rho) toward the
apex along the contact line (zero torque about the apex), and the normal
resultant sits where the torque of N and gravity about the apex equals
dL/dt = Omega z x L, L = I_apex omega. The kinematics are integrated by
RK4 on the cup's rotation matrix (angular velocity along the contact line
read from the state) and checked: axis height, orthonormality, the lap
against the closed form, no slip on both rims (arc rolled on the rim
against arc covered on the desk), the centre's speed, dL/dt by finite
differences against the closed form. The drawing follows the integration.
The run repeats every cycle_s seconds of video with a crossfade back to
the setup; the cycle divides the scene length, so the scene is exactly
periodic and the last frame equals the first. Deterministic, no seed.

Measured and printed: the cone geometry, the mass split and the centre
of mass, the inertia tensor about the apex (closed form against a
quadrature), the lap, the turns per lap, the friction needed, the normal
resultant, the cup's nearest approach to the edge, the can's exit and
landing, the cup-size and nudge variants for the description, the
brief's checks, the schedule in video time, the on-screen text widths and
the layout clearances.

usage: cuproll.py [--measure-only] [--frames t1,t2,...]
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
DECK_B = (42, 50, 62)
RIM = (96, 108, 126)
STRIPE = (16, 20, 26)
CUP_DARK = (120, 40, 34)
CUP_MOUTH = (40, 18, 16)
CAN_DARK = (34, 110, 88)
FINGER = (196, 170, 150)
NAIL = (232, 214, 200)

# Layout (one scene, 1080x1920): overlay at y 96..130 (captions.py); the
# floor beyond the desk edge is the dark background above y 330 (the title
# rows at y 186/244/302 for the first seconds, then the legend at y 236 and
# the clock at y 290, all left-aligned at x 40 so the can's drop lane on
# the right stays clear); the desk fills the frame from the edge at y 330
# to y 1290 (90 by 80 cm at 1200 px per metre); the label rows at y 372
# (cup left at x 40, can right-aligned at x 860), the shared sub row at y
# 414, the can's readout at y 450; both objects start on the start line at
# y 810 (40 cm = 480 px below the edge); the cup's live counters sit inside
# the empty disc about the cone tip, above the tip, the "cone tip" tag
# under it; the gold event rows at y 1200 and 1248 under the cup's circle;
# the geometry (y 136..1290) drawn at 2x and reduced; captions at caption_y
# 0.75 (y 1440..1530); the six-line card from y 1572 at a 48 px pitch.
LEGEND_Y, CLOCK_Y = 236, 290
TITLE_Y = (186, 244, 302)
TEXT_X0 = 40
SS = 2
LAYER_Y0, LAYER_Y1 = 136, 1290
PAYOFF_Y, PAYOFF_PITCH = 1572.0, 48
LABEL_Y, SUB_Y, READ_Y = 372, 414, 450
ROW_X0, ROW_X1 = 40, 860
EVENT_Y = (1200, 1248)
COUNTER_DY = (-90, -54)       # the cup's counters above the cone tip
TIP_DY = 24                   # the "cone tip" tag under the tip
START_Y = 810
FINGER_L, FINGER_T = 70.0, 16.0
COLOUR = {"cup": CORAL, "can": TEAL}
TWO_PI = 2.0 * math.pi


def blend(col, a: float, base=BG) -> tuple:
    a = max(0.0, min(1.0, a))
    return tuple(int(round(c * a + b * (1 - a))) for c, b in zip(col, base))


# --- measurement --------------------------------------------------------------
def cone_geometry(Rt: float, rb: float, h: float) -> dict:
    """The cone the cup is a slice of: slant, half-angle, apex distances along the generator."""
    slant = math.hypot(h, Rt - rb)
    sa = (Rt - rb) / slant
    alpha = math.asin(sa)
    return {"Rt": Rt, "rb": rb, "h": h, "slant": slant, "sin_a": sa, "cos_a": math.cos(alpha), "alpha": alpha,
            "l1": rb / sa, "l2": Rt / sa}


def cup_mass(geo: dict) -> dict:
    """Thin sheet of unit surface density: the frustum wall from slant l1 to l2 plus the bottom disc.
    Mass, the centre of mass along the axis from the apex, and the inertia tensor about the apex
    (I1 about any line through the apex perpendicular to the axis, I3 about the axis)."""
    sa, ca, l1, l2, rb = geo["sin_a"], geo["cos_a"], geo["l1"], geo["l2"], geo["rb"]
    m_w = math.pi * sa * (l2 ** 2 - l1 ** 2)                 # = pi (Rt + rb) (l2 - l1)
    m_b = math.pi * rb ** 2
    s_w = (2.0 / 3.0) * (l2 ** 3 - l1 ** 3) / (l2 ** 2 - l1 ** 2)   # wall CM along the slant
    z_w, z_b = s_w * ca, l1 * ca                               # axial positions from the apex
    q4 = (l2 ** 4 - l1 ** 4) / 4.0
    I3 = 2.0 * math.pi * sa ** 3 * q4 + 0.5 * m_b * rb ** 2
    I1 = 2.0 * math.pi * sa * (ca ** 2 + 0.5 * sa ** 2) * q4 + m_b * (0.25 * rb ** 2 + z_b ** 2)
    m = m_w + m_b
    return {"m_w": m_w, "m_b": m_b, "m": m, "share_w": m_w / m, "d_cm": (m_w * z_w + m_b * z_b) / m,
            "I1": I1, "I3": I3}


def cup_mass_quadrature(geo: dict, ns: int = 4000, nphi: int = 720) -> dict:
    """The same mass, centre and inertia tensor by midpoint quadrature over the sheet (a check)."""
    sa, ca, l1, l2, rb = geo["sin_a"], geo["cos_a"], geo["l1"], geo["l2"], geo["rb"]
    s = l1 + (np.arange(ns) + 0.5) * (l2 - l1) / ns
    phi = (np.arange(nphi) + 0.5) * TWO_PI / nphi
    S, P = np.meshgrid(s, phi, indexing="ij")
    dA = S * sa * ((l2 - l1) / ns) * (TWO_PI / nphi)
    z, x, y = S * ca, S * sa * np.cos(P), S * sa * np.sin(P)
    r = (np.arange(400) + 0.5) * rb / 400
    Rr, Pb = np.meshgrid(r, phi, indexing="ij")
    dAb = Rr * (rb / 400) * (TWO_PI / nphi)
    zb, xb, yb = np.full_like(Rr, l1 * ca), Rr * np.cos(Pb), Rr * np.sin(Pb)
    m = float(dA.sum() + dAb.sum())
    d_cm = float((z * dA).sum() + (zb * dAb).sum()) / m
    I3 = float(((x ** 2 + y ** 2) * dA).sum() + ((xb ** 2 + yb ** 2) * dAb).sum())
    I1 = float(((y ** 2 + z ** 2) * dA).sum() + ((yb ** 2 + zb ** 2) * dAb).sum())
    return {"m": m, "d_cm": d_cm, "I1": I1, "I3": I3}


def skew(w: np.ndarray) -> np.ndarray:
    return np.array([[0.0, -w[2], w[1]], [w[2], 0.0, -w[0]], [-w[1], w[0], 0.0]])


def rolling_cone(geo: dict, mass: dict, v: float, fps: int, substeps: int, t_end: float, g: float,
                 psi0: float = math.pi) -> dict:
    """RK4 on the cup's rotation matrix R (body to desk; column 3 the axis, column 1 the body line
    that starts at the contact). The angular velocity is omega_g along the contact line, read from
    the state as the horizontal direction of the axis; omega_g = -Omega cot alpha gives the centre
    of mass the speed v toward the edge at the start. Desk coordinates: x along the axis at the
    start, y toward the edge, z up, origin at the apex."""
    sa, ca = geo["sin_a"], geo["cos_a"]
    rho = mass["d_cm"] * ca
    Omega = v / rho
    wg = -Omega * ca / sa
    dt = 1.0 / (fps * substeps)
    n = int(round(t_end * fps * substeps))
    R = np.column_stack([np.array([sa, 0.0, -ca]), np.array([0.0, 1.0, 0.0]), np.array([ca, 0.0, sa])])
    marker = np.array([math.cos(psi0), math.sin(psi0), 0.0])   # the stripe, a body-fixed generator

    def omega_of(Rm: np.ndarray) -> np.ndarray:
        ax, ay = Rm[0, 2], Rm[1, 2]
        hh = math.hypot(ax, ay)
        return np.array([wg * ax / hh, wg * ay / hh, 0.0])

    def deriv(Rm: np.ndarray) -> np.ndarray:
        return skew(omega_of(Rm)) @ Rm

    t = np.arange(n + 1) * dt
    theta_raw = np.empty(n + 1)
    psi_raw = np.empty(n + 1)
    az = np.empty(n + 1)
    cm = np.empty((n + 1, 2))
    Rs = {}
    ortho = 0.0

    def record(k: int, Rm: np.ndarray) -> None:
        ax, ay = Rm[0, 2], Rm[1, 2]
        th = math.atan2(ay, ax)
        gx, gy = math.cos(th), math.sin(th)
        nvec = np.array([sa * gx, sa * gy, -ca])           # the current contact direction from the axis
        yvec = np.array([-gy, gx, 0.0])                     # z x g, the direction of the centre's motion
        mk = Rm @ marker
        theta_raw[k] = th
        psi_raw[k] = math.atan2(float(mk @ yvec), float(mk @ nvec))
        az[k] = Rm[2, 2]
        cm[k] = mass["d_cm"] * ax, mass["d_cm"] * ay

    record(0, R)
    for k in range(1, n + 1):
        k1 = deriv(R)
        k2 = deriv(R + 0.5 * dt * k1)
        k3 = deriv(R + 0.5 * dt * k2)
        k4 = deriv(R + dt * k3)
        R = R + dt / 6.0 * (k1 + 2.0 * k2 + 2.0 * k3 + k4)
        record(k, R)
        if k % substeps == 0:
            Rs[k // substeps] = R.copy()
            ortho = max(ortho, float(np.abs(R.T @ R - np.eye(3)).max()))
    theta = np.unwrap(theta_raw)
    psi = np.unwrap(psi_raw) - psi0
    # The lap: the contact line back through its start direction; the centre back at its start.
    T_lap = float(np.interp(TWO_PI, theta, t))
    dist = np.hypot(cm[:, 0] - cm[0, 0], cm[:, 1] - cm[0, 1])
    half = int(np.argmax(dist > 0.5 * dist.max()))
    i = half + int(np.argmin(dist[half:]))
    y0, y1, y2 = dist[i - 1], dist[i], dist[i + 1]
    off = 0.5 * (y0 - y2) / (y0 - 2 * y1 + y2)
    T_ret = float(t[i] + off * dt)
    d_ret = float(y1 - 0.25 * (y0 - y2) * off)
    speed = np.hypot(np.diff(cm[:, 0]), np.diff(cm[:, 1])) / dt
    # No slip: the arc of each rim that has touched, radius x |body turn|, against the arc of its
    # circle on the desk, apex distance x the contact line's turn.
    turn = np.abs(psi)
    slip_large = float(np.max(np.abs(geo["Rt"] * turn - geo["l2"] * theta)))
    slip_small = float(np.max(np.abs(geo["rb"] * turn - geo["l1"] * theta)))
    turns_lap = float(np.interp(T_lap, t, turn)) / TWO_PI
    # dL/dt by central differences from the stored frames against Omega z x L, and the normal
    # resultant it puts on the contact line.
    Ib = np.diag([mass["I1"], mass["I1"], mass["I3"]])
    xn = []
    dLz = 0.0
    for f in range(2, len(Rs) - 2, max(1, len(Rs) // 25)):
        Ls = []
        for ff in (f - 1, f + 1):
            Rm = Rs[ff]
            Ls.append(Rm @ Ib @ Rm.T @ omega_of(Rm))
        dL = (Ls[1] - Ls[0]) / (2.0 / fps)
        Rm = Rs[f]
        th = math.atan2(Rm[1, 2], Rm[0, 2])
        yvec = np.array([-math.sin(th), math.cos(th), 0.0])
        xn.append(rho - float(dL @ yvec) / (mass["m"] * g))
        dLz = max(dLz, abs(float(dL[2])))
    return {"t": t, "theta": theta, "psi": psi, "az": az, "cm": cm, "rho": rho, "Omega": Omega, "wg": wg,
            "ws": Omega / sa, "T_lap": T_lap, "T_ret": T_ret, "d_ret": d_ret, "turns_lap": turns_lap,
            "slip_large": slip_large, "slip_small": slip_small, "ortho": ortho, "dt": dt, "steps": n,
            "az_dev": float(np.max(np.abs(az - sa))), "speed_dev": float(np.max(np.abs(speed - v))),
            "xn_num": (float(np.mean(xn)), float(np.max(xn) - np.min(xn))), "dLz": dLz}


def closed_forms(geo: dict, mass: dict, v: float, g: float) -> dict:
    sa, ca = geo["sin_a"], geo["cos_a"]
    rho = mass["d_cm"] * ca
    Omega = v / rho
    xn = rho + Omega ** 2 * (ca / sa) * (mass["I1"] * sa ** 2 + mass["I3"] * ca ** 2) / (mass["m"] * g)
    return {"rho": rho, "h_cm": mass["d_cm"] * sa, "Omega": Omega, "T_lap": TWO_PI * rho / v, "mu": v * v / (g * rho),
            "xn": xn, "turns": 1.0 / sa, "wg": Omega * ca / sa, "ws": Omega / sa}


def measure(man: dict) -> dict:
    g, v, d, Hd, mu = man["g"], man["nudge_speed_m_s"], man["start_to_edge_m"], man["desk_height_m"], man["grip"]
    Rt, rb, h = man["cup_top_diameter_m"] / 2.0, man["cup_bottom_diameter_m"] / 2.0, man["cup_height_m"]
    r_can, L_can = man["can_diameter_m"] / 2.0, man["can_length_m"]
    fps, sub = man["fps"], man["substeps"]
    P, D, F, na = man["cycle_s"], man["scene_duration"], man["reset_fade"], man["nudge_at"]
    ppm = float(man["px_per_m"])
    cycles = D / P
    assert abs(cycles - round(cycles)) < 1e-9, "the cycle must divide the scene length"
    for key in ("cycle_s", "nudge_at", "first_cycle_at", "reset_fade", "finger_s"):
        assert abs(man[key] * fps - round(man[key] * fps)) < 1e-9, f"{key} must be a whole number of frames"
    geo = cone_geometry(Rt, rb, h)
    mass = cup_mass(geo)
    quad = cup_mass_quadrature(geo)
    cf = closed_forms(geo, mass, v, g)
    print(f"setup: one desk seen from above, real time: a thin-walled 8 oz paper cup (top diameter {2 * Rt * 100:g} cm, "
          f"bottom diameter {2 * rb * 100:g} cm, height {h * 100:g} cm; the wall plus a bottom disc of the same sheet) lying "
          f"on its side and a straight can {2 * r_can * 100:g} cm in diameter and {L_can * 100:g} cm long, both with their "
          f"axes parallel to the desk edge, both {d * 100:g} cm from the edge, on a level desk with grip {mu:g} (chosen); "
          f"each gets the same nudge: its centre moves off toward the edge at v = {v:g} m/s (chosen); g = {g:g} m/s^2; the "
          f"can rolls straight without loss (chosen), leaves the desk as its centre passes the edge and falls freely from a "
          f"{Hd * 100:g} cm desk; the cup rolls without slipping as a slice of a cone, pivoting about the cone's apex; its "
          f"rotation matrix integrated by RK4 at {sub} steps per frame (dt = {1.0 / (fps * sub):.2e} s) for "
          f"{man['integrate_s']:g} s; the dynamics in closed form; shown in real time on a {P:g} s cycle ({P * fps:.0f} "
          f"frames) with the nudge {na:g} s into the cycle, {cycles:.0f} cycles in {D:g} s; drawn at {ppm:g} px per metre; "
          f"deterministic, no seed")
    sa, al = geo["sin_a"], math.degrees(geo["alpha"])
    print(f"cone: slant length sqrt({h * 100:g}^2 + {(Rt - rb) * 100:g}^2) = {geo['slant'] * 100:.4f} cm = "
          f"{geo['slant'] * 100:.3f} cm; sin alpha = {(Rt - rb) * 100:g} / {geo['slant'] * 100:.3f} = {sa:.5f}, half-angle "
          f"alpha = {al:.4f} deg = {al:.3f} deg; the apex lies l1 = rb / sin alpha = {geo['l1'] * 100:.3f} cm = "
          f"{geo['l1'] * 100:.2f} cm beyond the small rim and l2 = Rt / sin alpha = {geo['l2'] * 100:.3f} cm = "
          f"{geo['l2'] * 100:.2f} cm from the large rim along the contact line (l2 - l1 = {(geo['l2'] - geo['l1']) * 100:.3f} "
          f"cm, the slant); both rims run on circles of those radii about the apex, so the cup turns l1 / rb = "
          f"{geo['l1'] / rb:.4f} = l2 / Rt = {geo['l2'] / Rt:.4f} = 1 / sin alpha = {cf['turns']:.4f} = {cf['turns']:.3f} "
          f"times per lap; a straight cup or can (alpha = 0) has its apex at infinity and rolls straight")
    print(f"mass: wall {mass['m_w'] * 1e4:.3f} cm^2 of sheet, bottom {mass['m_b'] * 1e4:.3f} cm^2: the wall carries "
          f"{mass['share_w']:.4f} = {mass['share_w'] * 100:.1f} percent of the mass; wall CM at (2/3)(l2^3 - l1^3)/(l2^2 - l1^2) "
          f"= {(2.0 / 3.0) * (geo['l2'] ** 3 - geo['l1'] ** 3) / (geo['l2'] ** 2 - geo['l1'] ** 2) * 100:.3f} cm along the "
          f"slant; the cup's centre of mass {mass['d_cm'] * 100:.3f} cm = {mass['d_cm'] * 100:.2f} cm from the apex along the "
          f"axis (quadrature {quad['d_cm'] * 100:.3f} cm, mass {quad['m'] / mass['m']:.6f} of the closed form), so it rides "
          f"a circle of radius rho = d_cm cos alpha = {cf['rho'] * 100:.3f} cm = {cf['rho'] * 100:.2f} cm at the constant "
          f"height d_cm sin alpha = {cf['h_cm'] * 100:.3f} cm; inertia about the apex per unit sheet density: I1 = "
          f"{mass['I1'] * 1e8:.3f} cm^4 (perpendicular to the axis; quadrature {quad['I1'] * 1e8:.3f}), I3 = "
          f"{mass['I3'] * 1e8:.4f} cm^4 (about the axis; quadrature {quad['I3'] * 1e8:.4f})")
    assert abs(quad["d_cm"] - mass["d_cm"]) < 1e-6 * mass["d_cm"] and abs(quad["I1"] - mass["I1"]) < 1e-5 * mass["I1"] \
        and abs(quad["I3"] - mass["I3"]) < 1e-5 * mass["I3"] and abs(quad["m"] - mass["m"]) < 1e-6 * mass["m"]
    run = rolling_cone(geo, mass, v, fps, sub, man["integrate_s"], g)
    half = rolling_cone(geo, mass, v, fps, 2 * sub, man["integrate_s"], g)
    print(f"cup rolling (closed form): the axis turns about the vertical through the apex at Omega = v / rho = "
          f"{cf['Omega']:.4f} rad/s; the angular velocity lies along the contact line, |omega_g| = Omega cot alpha = "
          f"{cf['wg']:.4f} rad/s, and in the frame turning with the axis the cup spins about its own axis at Omega / sin "
          f"alpha = {cf['ws']:.4f} rad/s = {cf['ws'] / TWO_PI:.4f} turns/s; one lap 2 pi rho / v = {cf['T_lap']:.4f} s = "
          f"{cf['T_lap']:.3f} s = {cf['T_lap']:.2f} s = {cf['T_lap']:.1f} s, {cf['turns']:.4f} turns; N = m g (the height "
          f"is constant); friction needed v^2 / (g rho) = {cf['mu']:.4f} = {cf['mu']:.3f} of the weight toward the apex "
          f"along the contact line, under the desk's {mu:g} by a factor {mu / cf['mu']:.1f}; friction acts along the "
          f"contact line through the apex, so its torque about the apex is zero; the normal resultant from dL/dt = "
          f"Omega z x L: x_N = rho + Omega^2 cot alpha (I1 sin^2 alpha + I3 cos^2 alpha) / (m g) = {cf['xn'] * 100:.3f} cm = "
          f"{cf['xn'] * 100:.2f} cm from the apex, {(cf['xn'] - cf['rho']) * 100:.2f} cm beyond the centre of mass, inside the "
          f"{geo['l1'] * 100:.2f} to {geo['l2'] * 100:.2f} cm contact segment")
    assert geo["l1"] < cf["xn"] < geo["l2"], "the normal resultant leaves the contact segment"
    print(f"cup rolling (RK4 on the rotation matrix, {run['steps']} steps): back through its start direction after "
          f"{run['T_lap']:.6f} s (closed form {cf['T_lap']:.6f} s, diff {run['T_lap'] - cf['T_lap']:+.1e} s); the centre of "
          f"mass back at its start after {run['T_ret']:.6f} s (closest approach {run['d_ret'] * 1e6:.3f} um); it turns "
          f"{run['turns_lap']:.6f} times per lap (closed form {cf['turns']:.6f}, diff {run['turns_lap'] - cf['turns']:+.1e}); "
          f"no slip: the arc of the large rim that has touched, Rt x turn, matches l2 x the contact line's turn within "
          f"{run['slip_large']:.1e} m at every step, the small rim within {run['slip_small']:.1e} m; the axis's height "
          f"stays within {run['az_dev']:.1e} of sin alpha, so the centre of mass height {cf['h_cm'] * 100:.3f} cm is constant "
          f"within {run['az_dev'] * mass['d_cm']:.1e} m (energy kept); the centre's speed stays within {run['speed_dev']:.1e} "
          f"m/s of {v:g}; orthonormality drift {run['ortho']:.1e}; half-step rerun: lap {half['T_lap']:.9f} s "
          f"({half['T_lap'] - run['T_lap']:+.1e} s), turns {half['turns_lap']:.9f}; dL/dt by central differences puts the "
          f"normal resultant at {run['xn_num'][0] * 100:.3f} cm (spread {run['xn_num'][1] * 100:.1e} cm over the lap; closed "
          f"form {cf['xn'] * 100:.3f}); dL_z/dt at most {run['dLz']:.1e} (no vertical torque)")
    assert abs(run["T_lap"] - cf["T_lap"]) < 1e-8 and abs(run["turns_lap"] - cf["turns"]) < 1e-8
    assert run["slip_large"] < 1e-9 and run["slip_small"] < 1e-9 and run["az_dev"] * mass["d_cm"] < 1e-9
    assert abs(run["xn_num"][0] - cf["xn"]) < 1e-5 and run["speed_dev"] < 1e-6
    # The can.
    t_edge = d / v
    t_fall = math.sqrt(2.0 * Hd / g)
    land = v * t_fall
    t_down = t_edge + t_fall
    can_turns = d / (TWO_PI * r_can)
    th_edge = math.degrees(cf["Omega"] * t_edge)
    near = d - geo["l2"]
    print(f"can: rolls straight without loss at {v:g} m/s (spin {v / r_can:.3f} rad/s, {can_turns:.3f} turns over the "
          f"{d * 100:g} cm); its centre reaches the edge after {t_edge:.4f} s = {t_edge:.3f} s = {t_edge:.2f} s = "
          f"{t_edge:.1f} s; it falls freely from the {Hd * 100:g} cm desk for sqrt(2 H / g) = {t_fall:.4f} s = "
          f"{t_fall:.3f} s, down at {t_down:.4f} s = {t_down:.3f} s, landing v t = {land * 100:.2f} cm out from the edge; "
          f"rolling at a steady speed needs no grip")
    print(f"cup against the edge: at the can's exit, {t_edge:.3f} s, the cup is {th_edge:.1f} deg round its circle; the "
          f"large rim's circle reaches l2 = {geo['l2'] * 100:.2f} cm toward the edge from the start line, against "
          f"{d * 100:g} cm, so the cup's track never comes closer to the edge than {near * 100:.2f} cm = {near * 100:.1f} cm "
          f"(nearest at a quarter lap, {cf['T_lap'] / 4:.3f} s after the nudge); the large rim's circle needs a desk at "
          f"least {2 * geo['l2'] * 100:.1f} cm across; after one lap the cup is back where it started, turned "
          f"{cf['turns']:.2f} times (the drawing holds it there; without loss it would circle for ever)")
    ev: dict = {"geo": geo, "mass": mass, "cf": cf, "run": run, "t_edge": t_edge, "t_fall": t_fall, "t_down": t_down,
                "land": land, "near": near, "can_turns": can_turns, "th_edge": th_edge}
    # Variants for the description.
    descr, var = [], {}
    for name, (dt_, db_, hh) in man["description_cups"].items():
        gq = cone_geometry(dt_ / 2.0, db_ / 2.0, hh)
        mq = cup_mass(gq)
        cq = closed_forms(gq, mq, v, g)
        var[name] = (gq, mq, cq)
        descr.append(f"{name} (top {dt_ * 100:g}, bottom {db_ * 100:g}, height {hh * 100:g} cm): alpha "
                     f"{math.degrees(gq['alpha']):.2f} deg, apex {gq['l1'] * 100:.2f} cm beyond the small rim and "
                     f"{gq['l2'] * 100:.2f} cm = {gq['l2'] * 100:.1f} cm from the large rim, {cq['turns']:.3f} = {cq['turns']:.2f} "
                     f"turns per lap, CM circle {cq['rho'] * 100:.2f} cm, lap {cq['T_lap']:.2f} s at {v:g} m/s, grip needed "
                     f"{cq['mu']:.4f}, nearest the edge {(d - gq['l2']) * 100:.1f} cm")
    descr.append(f"a straight cup (alpha 0, like the can): apex at infinity, no circle, off the desk at {t_edge:.3f} s")
    for v2 in man["description_speeds_m_s"]:
        c2 = closed_forms(geo, mass, v2, g)
        var[v2] = c2
        descr.append(f"nudge {v2:g} m/s: lap {c2['T_lap']:.2f} s, friction needed {c2['mu']:.4f} = {c2['mu']:.3f}"
                     f"{' (over the desk grip: it would skid)' if c2['mu'] > mu else ''}; the can off at {d / v2:.3f} s")
    print("for the description: " + "; ".join(descr))
    ev["var"] = var
    # The brief's checks.
    g12, _, c12 = var["12 oz cup"]
    g4, _, c4 = var["4 oz cup"]
    checks: list[tuple[str, float, float, float]] = [
        ("slant (cm)", geo["slant"] * 100, 9.086, 6e-4), ("alpha (deg)", al, 7.907, 6e-4),
        ("apex to small rim (cm)", geo["l1"] * 100, 19.99, 6e-3), ("apex to large rim (cm)", geo["l2"] * 100, 29.08, 6e-3),
        ("l1 / rb", geo["l1"] / rb, 7.269, 6e-4), ("l2 / Rt", geo["l2"] / Rt, 7.269, 6e-4),
        ("turns per lap (RK4)", run["turns_lap"], 7.269, 6e-4),
        ("CM circle radius (cm, research)", cf["rho"] * 100, 23.82, 6e-2),
        ("lap time (s, research 4.990)", cf["T_lap"], 4.990, 5e-3), ("lap time RK4 (s)", run["T_lap"], 4.990, 5e-3),
        ("CM height constant (m)", run["az_dev"] * mass["d_cm"], 0.0, 1e-9),
        ("friction needed", cf["mu"], 0.038, 6e-4), ("friction needed at 0.5 m/s", var[0.5]["mu"], 0.107, 6e-4),
        ("normal resultant inside the contact segment (cm)", cf["xn"] * 100, (geo["l1"] + geo["l2"]) * 50, (geo["l2"] - geo["l1"]) * 50),
        ("nearest approach to the edge (cm)", near * 100, 10.9, 6e-2),
        ("can off the desk (s)", t_edge, 1.333, 6e-4), ("can down 0.75 m (s)", t_down, 1.724, 6e-4),
        ("12 oz: large rim circle (cm)", g12["l2"] * 100, 30.3, 6e-2), ("12 oz: turns per lap", c12["turns"], 6.74, 6e-3),
        ("4 oz: large rim circle (cm)", g4["l2"] * 100, 21.3, 6e-2), ("4 oz: turns per lap", c4["turns"], 6.08, 6e-3),
        ("no slip, large rim (m)", run["slip_large"], 0.0, 1e-9), ("no slip, small rim (m)", run["slip_small"], 0.0, 1e-9),
        ("RK4 lap against the closed form (s)", run["T_lap"] - cf["T_lap"], 0.0, 1e-9),
        ("half-step rerun lap (s)", half["T_lap"] - run["T_lap"], 0.0, 1e-9),
        ("dL/dt numeric against closed form (cm)", (run["xn_num"][0] - cf["xn"]) * 100, 0.0, 1e-3),
    ]
    fails, out = 0, []
    for name, got, want, tol in checks:
        ok = abs(got - want) <= tol
        fails += 0 if ok else 1
        out.append(f"{name}: brief {want:g}, sim {got:.6g}, diff {got - want:+.1e}: {'ok' if ok else 'FAIL'}")
    print(f"checks against the brief ({len(checks)} checks, {fails} failed): " + "; ".join(out))
    print(f"note: the brief puts the normal resultant at about 23.6 cm, short of the centre of mass; the sim's dL/dt = "
          f"Omega z x L puts it {(cf['xn'] - cf['rho']) * 100:.2f} cm beyond the centre of mass at {cf['xn'] * 100:.2f} cm "
          f"(closed form and finite differences agree); either lies inside the contact segment")
    assert fails == 0, "a check against the brief failed"
    ev["check_count"] = len(checks)
    # Geometry on screen.
    ax_, ay_, cx_ = float(man["apex_x_px"]), float(START_Y), float(man["can_x_px"])
    edge_y, bottom = float(man["edge_y_px"]), float(man["desk_bottom_px"])
    assert abs((ay_ - edge_y) - d * ppm) < 1e-9, "the start line is not 40 cm (480 px) below the edge"
    l1p, l2p, rhop = geo["l1"] * ppm, geo["l2"] * ppm, cf["rho"] * ppm
    can_w, can_h = L_can * ppm, 2 * r_can * ppm
    print(f"drawing: {ppm:g} px per metre; the desk edge at y {edge_y:.0f}, the desk to y {bottom:.0f} ({(bottom - edge_y) / ppm * 100:g} "
          f"cm deep); the start line at y {START_Y} ({d * 100:g} cm = {d * ppm:.0f} px below the edge); the cup's cone tip "
          f"at x {ax_:.0f} on the start line, the small rim {l1p:.0f} px to its right (x {ax_ + l1p:.0f}), the large rim "
          f"{l2p:.0f} px (x {ax_ + l2p:.0f}), the cup {2 * rb * ppm:.0f} to {2 * Rt * ppm:.0f} px wide and {h * ppm:.0f} px "
          f"long, its centre of mass at x {ax_ + rhop:.0f}; the large rim's circle (radius {l2p:.1f} px) spans x "
          f"{ax_ - l2p:.0f} to {ax_ + l2p:.0f} and y {ay_ - l2p:.0f} to {ay_ + l2p:.0f} ({(ay_ - l2p - edge_y) / ppm * 100:.1f} "
          f"cm from the edge); the can {can_w:.0f} by {can_h:.0f} px at x {cx_:.0f} (x {cx_ - can_w / 2:.0f} to "
          f"{cx_ + can_w / 2:.0f}), rolling up its lane to the edge and on into the dark beyond it, drawn smaller as it "
          f"drops (scale {man['camera_height_m']:g} / ({man['camera_height_m']:g} + drop)), landing at y "
          f"{ay_ - v * t_down * ppm:.0f} at scale {man['camera_height_m'] / (man['camera_height_m'] + Hd):.3f}")
    assert ay_ - l2p > edge_y + 4 and ay_ + l2p < bottom - 4 and ax_ - l2p > 4, "the large rim's circle leaves the desk"
    assert ax_ + l2p < cx_ - can_w / 2 - 40, "the cup's circle reaches the can's lane"
    assert cx_ + can_w / 2 < W - 20, "the can leaves the frame sideways"
    # The schedule in video time.
    t0 = man["first_cycle_at"]
    k0 = math.ceil((0.0 - t0) / P - 1e-9) - 1
    k1 = math.floor((D - t0) / P - 1e-9)
    starts = [t0 + kk * P for kk in range(k0, k1 + 1)]

    def lst(off_: float) -> str:
        return ", ".join(f"{st + off_:.2f}" for st in starts if 0.0 <= st + off_ < D)

    assert na + run["T_lap"] < P - F - 0.5, "the cup is still rolling at the reset fade"
    assert na + t_down < P - F, "the can is still falling at the reset fade"
    ev["lap_v"], ev["edge_v"], ev["down_v"] = na + run["T_lap"], na + t_edge, na + t_down
    print(f"schedule (video time, real time): cycles of {P:g} s start at " + ", ".join(f"{st:.2f}" for st in starts)
          + f" s; the finger marks move in over the first {man['finger_s']:g} s and tap both objects {na:g} s into each cycle "
          f"at {lst(na)} s; the can's centre passes the edge {t_edge:.3f} s later at {lst(na + t_edge)} s (its event row "
          f"lights) and it is down on the floor at {lst(na + t_down)} s ({na + t_down:.3f} s into the cycle); the cup is a "
          f"quarter lap round (nearest the edge; the dashed rim circles appear) at {lst(na + run['T_lap'] / 4)} s, half "
          f"way at {lst(na + run['T_lap'] / 2)} s and back at its start {run['T_lap']:.3f} s after the nudge at "
          f"{lst(na + run['T_lap'])} s (its event row lights; the drawing holds it there); the reset crossfade runs over "
          f"the last {F:g} s of each cycle (from {lst(P - F)} s); on the first frame both objects rest on the start line "
          f"with the finger marks {na:g} s from the tap; title until {man['title_until']:g} s; payoff card from "
          f"{man['payoff_t']:g} s; the title fades back in over the last {man['loop_fade']:g} s and the last frame repeats "
          f"the first (the scene is periodic: {D:g} s holds exactly {cycles:.0f} cycles)")
    # Text widths and layout boxes.
    font = os.environ["SEED_ZERO_FONT"]
    f24, f28, f34, f40, f56 = (ImageFont.truetype(font, n) for n in (24, 28, 34, 40, 56))
    widths = {"overlay@34": (f34, man["overlay"])}
    for j, line in enumerate(man["title"].split("|")):
        widths[f"title line {j + 1}@56"] = (f56, line)
    widths["legend@40"] = (f40, legend_text())
    widths["clock@28"] = (f28, clock_text(1.2515))
    widths["clock held@28"] = (f28, clock_text(-1.0))
    widths["label cup@40"] = (f40, label_text("cup"))
    widths["label can@40"] = (f40, label_text("can"))
    widths["sub@28"] = (f28, sub_text(man))
    widths["counter turned@28"] = (f28, turned_text(7.27))
    widths["counter lap@28"] = (f28, lap_text(1.0))
    widths["tip@24"] = (f24, tip_text())
    widths["can moved@28"] = (f28, moved_text(0.4))
    widths["can off@28"] = (f28, off_text())
    widths["can floor@28"] = (f28, floor_text())
    widths["event can@40"] = (f40, event_text(ev, "can"))
    widths["event cup@40"] = (f40, event_text(ev, "cup"))
    for j, line in enumerate(payoff_lines(man, ev)):
        widths[f"payoff line {j + 1}@40"] = (f40, line)
    print("text widths (the on-screen strings verbatim): " + ", ".join(f"{kk} {f.getlength(s):.0f} px '{s}'"
                                                                      for kk, (f, s) in widths.items()))
    assert all(f.getlength(s) < 950 for f, s in widths.values()), "a text line is wider than 950 px"
    assert len(payoff_lines(man, ev)) <= 6, "the card has more than six lines"
    assert len(man["title"].split("|")) <= 3, "more than three title rows"
    wd = {k: f.getlength(s) for k, (f, s) in widths.items()}
    lane_x0 = cx_ - can_w / 2.0
    boxes = {}
    for j in range(len(man["title"].split("|"))):
        boxes[f"title {j + 1}"] = (TEXT_X0, TITLE_Y[j] - 28, TEXT_X0 + wd[f"title line {j + 1}@56"], TITLE_Y[j] + 28)
    boxes["legend"] = (TEXT_X0, LEGEND_Y - 20, TEXT_X0 + wd["legend@40"], LEGEND_Y + 20)
    boxes["clock"] = (TEXT_X0, CLOCK_Y - 14, TEXT_X0 + max(wd["clock@28"], wd["clock held@28"]), CLOCK_Y + 14)
    boxes["label cup"] = (ROW_X0, LABEL_Y - 20, ROW_X0 + wd["label cup@40"], LABEL_Y + 20)
    boxes["label can"] = (ROW_X1 - wd["label can@40"], LABEL_Y - 20, ROW_X1, LABEL_Y + 20)
    sub_cx = (ROW_X0 + ROW_X1) / 2.0
    boxes["sub"] = (sub_cx - wd["sub@28"] / 2.0, SUB_Y - 14, sub_cx + wd["sub@28"] / 2.0, SUB_Y + 14)
    rw = max(wd["can moved@28"], wd["can off@28"], wd["can floor@28"])
    boxes["can readout"] = (ROW_X1 - rw, READ_Y - 14, ROW_X1, READ_Y + 14)
    boxes["counter turned"] = (ax_ - wd["counter turned@28"] / 2.0, ay_ + COUNTER_DY[0] - 14, ax_ + wd["counter turned@28"] / 2.0, ay_ + COUNTER_DY[0] + 14)
    boxes["counter lap"] = (ax_ - wd["counter lap@28"] / 2.0, ay_ + COUNTER_DY[1] - 14, ax_ + wd["counter lap@28"] / 2.0, ay_ + COUNTER_DY[1] + 14)
    boxes["tip tag"] = (ax_ - wd["tip@24"] / 2.0, ay_ + TIP_DY - 12, ax_ + wd["tip@24"] / 2.0, ay_ + TIP_DY + 12)
    for j, m in enumerate(("can", "cup")):
        boxes[f"event {m}"] = (W / 2.0 - wd[f"event {m}@40"] / 2.0, EVENT_Y[j] - 20, W / 2.0 + wd[f"event {m}@40"] / 2.0, EVENT_Y[j] + 20)
    for j in range(len(payoff_lines(man, ev))):
        boxes[f"payoff {j + 1}"] = (W / 2.0 - wd[f"payoff line {j + 1}@40"] / 2.0, PAYOFF_Y + j * PAYOFF_PITCH - 20,
                                    W / 2.0 + wd[f"payoff line {j + 1}@40"] / 2.0, PAYOFF_Y + j * PAYOFF_PITCH + 20)
    cap_y0, cap_y1 = int(man["caption_y"] * H), int(man["caption_y"] * H) + 90
    land_y = ay_ - v * t_down * ppm
    land_scale = man["camera_height_m"] / (man["camera_height_m"] + Hd)
    print(f"layout check: text boxes (x0, y0, x1, y1): " + "; ".join(f"{k} ({b[0]:.0f}, {b[1]:.0f}, {b[2]:.0f}, {b[3]:.0f})"
                                                                  for k, b in boxes.items())
          + f"; the can's lane x {lane_x0:.0f} to {cx_ + can_w / 2:.0f} from y {ay_ + can_h / 2:.0f} up (its finger below it "
          f"to y {ay_ + can_h / 2 + 60 + FINGER_L:.0f}); the landed can at y {land_y:.0f}, {can_h * land_scale / 2:.0f} px "
          f"tall either side; the cup's finger at x {ax_ + rhop:.0f} below y {ay_ + Rt * ppm:.0f}; the large rim's circle "
          f"radius {l2p:.0f} px, the small rim's {l1p:.0f} px about ({ax_:.0f}, {ay_:.0f}); the overlay band y 96 to 130, "
          f"the caption band y {cap_y0} to {cap_y1}; the geometry layer y {LAYER_Y0} to {LAYER_Y1}; the title rows and the "
          f"legend/clock share the zone above the edge but never show together (the title fades out over 0.4 s before the "
          f"legend fades in); every other pair of boxes is disjoint")
    for a_name, a_box in boxes.items():
        for b_name, b_box in boxes.items():
            if a_name < b_name:
                # The title rows and the legend/clock share the zone above the desk edge but never show together:
                # the title fades out before the legend and clock fade in.
                if {a_name.split()[0], b_name.split()[0]} in ({"title", "legend"}, {"title", "clock"}):
                    continue
                sep = a_box[2] <= b_box[0] or b_box[2] <= a_box[0] or a_box[3] <= b_box[1] or b_box[3] <= a_box[1]
                assert sep, f"{a_name} meets {b_name}"
        assert a_box[0] >= 20 and a_box[2] <= W - 20, f"{a_name} reaches the frame edge"
        assert a_box[3] <= 96 or a_box[1] >= 130, f"{a_name} meets the overlay band"
        assert a_box[3] <= cap_y0 or a_box[1] >= cap_y1, f"{a_name} meets the caption band"
        # The can's lane: a box must end left of it or sit below the can's start.
        assert a_box[2] < lane_x0 - 10 or a_box[1] > ay_ + can_h / 2 + 60 + FINGER_L + 10, f"{a_name} meets the can's lane"
    for name in ("label cup", "label can", "sub", "can readout"):
        x0, y0, x1, y1 = boxes[name]
        xs = min(max(ax_, x0), x1)
        if abs(xs - ax_) < l2p:
            yc = ay_ - math.sqrt(l2p ** 2 - (xs - ax_) ** 2)
            assert y1 + 6 < yc, f"{name} reaches the cup's circle (circle at y {yc:.0f})"
        assert y0 > edge_y + 6, f"{name} reaches the desk edge"
    for name in ("counter turned", "counter lap", "tip tag"):
        x0, y0, x1, y1 = boxes[name]
        far = max(math.hypot(x - ax_, y - ay_) for x in (x0, x1) for y in (y0, y1))
        assert far < l1p - 8, f"{name} leaves the empty disc inside the small rim's circle"
        assert y1 < ay_ - 10 or y0 > ay_ + 10, f"{name} meets the cone tip dot"
    for name in ("event can", "event cup"):
        assert boxes[name][1] - 6 > ay_ + l2p, f"{name} reaches the cup's circle"
        assert boxes[name][3] < bottom - 4, f"{name} leaves the desk"
    assert land_y - can_h * land_scale / 2 > 136, "the landed can reaches the overlay band"
    assert boxes["title 3" if "title 3" in boxes else "title 2"][3] <= edge_y, "the title reaches the desk edge"
    assert PAYOFF_Y - 20 > cap_y1, "the card meets the caption band"
    assert PAYOFF_Y + (len(payoff_lines(man, ev)) - 1) * PAYOFF_PITCH + 20 < H - 40, "the card leaves the frame"
    return ev


def legend_text() -> str:
    return "same desk, same nudge, real time"


def clock_text(r: float) -> str:
    return "before the nudge" if r < 0.0 else f"{r:.2f} s since the nudge"


def label_text(m: str) -> str:
    return "paper cup" if m == "cup" else "straight can"


def sub_text(man: dict) -> str:
    return f"same nudge, {man['start_to_edge_m'] * 100:g} cm from the edge"


def turned_text(turns: float) -> str:
    return f"cup: turned {turns:.1f} times"


def lap_text(lap: float) -> str:
    return f"cup: lap {lap:.2f}"


def tip_text() -> str:
    return "cone tip"


def moved_text(x: float) -> str:
    return f"can: moved {x * 100:.0f} cm"


def off_text() -> str:
    return "can: off the desk"


def floor_text() -> str:
    return "can: on the floor"


def event_text(ev: dict, m: str) -> str:
    if m == "can":
        return f"can: off the desk at {ev['t_edge']:.2f} s"
    return f"cup: back at the start at {ev['run']['T_lap']:.1f} s"


def payoff_lines(man: dict, ev: dict) -> list[str]:
    text = man["payoff_text"].format(t_edge=ev["t_edge"], t_lap=ev["run"]["T_lap"], turns=ev["run"]["turns_lap"],
                                     l2_cm=ev["geo"]["l2"] * 100, near_cm=ev["near"] * 100, rho_cm=ev["cf"]["rho"] * 100,
                                     mu=ev["cf"]["mu"])
    return [s.strip() for s in text.split("|")]


# --- state over time ----------------------------------------------------------
def cup_state(ev: dict, rt: float) -> dict:
    """The cup rt real seconds after the nudge: the contact line's turn theta, the stripe's body
    angle psi (from the contact toward the direction of motion), both from the RK4 table; held at
    the end of the lap."""
    run = ev["run"]
    if rt <= 0.0:
        return {"theta": 0.0, "psi": math.pi, "rolling": False, "done": False, "rt": rt}
    T = run["T_lap"]
    tt = min(rt, T)
    th = float(np.interp(tt, run["t"], run["theta"]))
    ps = math.pi + float(np.interp(tt, run["t"], run["psi"]))
    return {"theta": th, "psi": ps, "rolling": rt < T, "done": rt >= T, "rt": rt}


def can_state(ev: dict, man: dict, rt: float) -> dict:
    v, r, g = man["nudge_speed_m_s"], man["can_diameter_m"] / 2.0, man["g"]
    if rt <= 0.0:
        return {"y": 0.0, "drop": 0.0, "psi": math.pi, "off": False, "floor": False}
    y = v * rt
    psi = math.pi - y / r
    if rt < ev["t_edge"]:
        return {"y": y, "drop": 0.0, "psi": psi, "off": False, "floor": False}
    u = rt - ev["t_edge"]
    if u >= ev["t_fall"]:
        return {"y": v * ev["t_down"], "drop": man["desk_height_m"], "psi": psi, "off": True, "floor": True}
    return {"y": y, "drop": 0.5 * g * u * u, "psi": psi, "off": True, "floor": False}


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
        self.ppm = float(man["px_per_m"])
        self.P = man["cycle_s"]
        self.P_f = int(round(man["cycle_s"] * self.fps))
        self.c0_f = int(round(man["first_cycle_at"] * self.fps))
        self.na, self.F = man["nudge_at"], man["reset_fade"]
        self.geo = ev["geo"]
        self.ax, self.ay = float(man["apex_x_px"]), float(START_Y)
        self.cx = float(man["can_x_px"])
        self.edge_y, self.bottom = float(man["edge_y_px"]), float(man["desk_bottom_px"])
        self.r_can = man["can_diameter_m"] / 2.0
        self.L_can = man["can_length_m"]
        self.rho = ev["cf"]["rho"]
        self.Hc = man["camera_height_m"]

    def phase(self, f: int) -> tuple[int, float]:
        k, tau_f = divmod(f - self.c0_f, self.P_f)
        return k, tau_f / self.fps

    @staticmethod
    def L_(x: float, y: float) -> tuple[float, float]:
        """Layer (2x) pixel of a frame point, rounded to 1e-4 px so equal states draw equal pixels."""
        return round(x * SS, 4), round((y - LAYER_Y0) * SS, 4)

    def D_(self, x: float, y: float) -> tuple[float, float]:
        """Layer pixel of a desk point (metres from the cone tip; x along the start line, y toward the edge)."""
        return self.L_(self.ax + x * self.ppm, self.ay - y * self.ppm)

    @staticmethod
    def dashed(d: ImageDraw.ImageDraw, pts: list, col, dash: float, gap: float, width: int) -> None:
        for (ax, ay), (bx, by) in zip(pts[:-1], pts[1:]):
            length = math.hypot(bx - ax, by - ay)
            if length < 1e-6:
                continue
            ux, uy = (bx - ax) / length, (by - ay) / length
            s = 0.0
            while s < length:
                e = min(length, s + dash)
                d.line((ax + ux * s, ay + uy * s, ax + ux * e, ay + uy * e), fill=col, width=width)
                s = e + gap

    def dashed_circle(self, d: ImageDraw.ImageDraw, rad_m: float, col, a: float) -> None:
        n = 180
        pts = [self.D_(rad_m * math.cos(TWO_PI * k / n), rad_m * math.sin(TWO_PI * k / n)) for k in range(n + 1)]
        # Dash by segments: every other segment drawn.
        for k in range(0, n, 2):
            d.line((*pts[k], *pts[k + 1]), fill=blend(col, a, DECK_A), width=2 * SS)

    def draw_desk(self, d: ImageDraw.ImageDraw) -> None:
        # The dark floor beyond the edge (the background), a shadow under the edge, the desk slab.
        for k in range(12):
            y0 = self.edge_y - 36 + 3 * k
            d.rectangle((*self.L_(0, y0), *self.L_(W, y0 + 3)), fill=blend((0, 0, 0), 0.55 * (k / 12.0), BG))
        d.rectangle((*self.L_(0, self.edge_y), *self.L_(W, self.bottom)), fill=DECK_A)
        d.rectangle((*self.L_(0, self.edge_y), *self.L_(W, self.edge_y + 5)), fill=RIM)
        d.rectangle((*self.L_(0, self.edge_y + 5), *self.L_(W, self.edge_y + 7)), fill=DECK_B)
        # The start line.
        self.dashed(d, [self.L_(ROW_X0, START_Y), self.L_(W - ROW_X0, START_Y)], blend(MUTED, 0.55, DECK_A), 10 * SS, 8 * SS, 2 * SS)

    def cup_frame(self, theta: float) -> tuple:
        g = (math.cos(theta), math.sin(theta))
        yv = (-math.sin(theta), math.cos(theta))
        return g, yv

    def cup_point(self, s: float, u: float, theta: float) -> tuple[float, float]:
        """Desk point of the cup's silhouette: slant s from the apex, u in [-1, 1] across its width."""
        geo = self.geo
        g, yv = self.cup_frame(theta)
        along = s * geo["cos_a"] ** 2
        across = u * s * geo["sin_a"]
        return along * g[0] + across * yv[0], along * g[1] + across * yv[1]

    def rim_points(self, s: float, theta: float, n: int = 48) -> list:
        """The rim at slant s seen from above: an ellipse of half-axes s sin^2 alpha along the axis and s sin alpha across."""
        geo = self.geo
        g, yv = self.cup_frame(theta)
        cx, cy = s * geo["cos_a"] ** 2 * g[0], s * geo["cos_a"] ** 2 * g[1]
        a_al, a_ac = s * geo["sin_a"] ** 2, s * geo["sin_a"]
        pts = []
        for k in range(n):
            ph = TWO_PI * k / n
            dx, dy = a_al * math.cos(ph), a_ac * math.sin(ph)
            pts.append(self.D_(cx + dx * g[0] + dy * yv[0], cy + dx * g[1] + dy * yv[1]))
        return pts

    def draw_cup(self, d: ImageDraw.ImageDraw, st: dict, tau: float) -> None:
        geo = self.geo
        l1, l2 = geo["l1"], geo["l2"]
        th, ps = st["theta"], st["psi"]
        rt = st["rt"]
        T = self.ev["run"]["T_lap"]
        # Guides: the centre's trail (an arc), the rim circles after a quarter lap, the cone tip.
        if rt > 0.0:
            n = max(2, int(th / 0.02) + 1)
            pts = [self.D_(self.rho * math.cos(th * k / n), self.rho * math.sin(th * k / n)) for k in range(n + 1)]
            d.line(pts, fill=blend(CORAL, 0.4, DECK_A), width=2 * SS)
            if rt >= T / 4.0:
                a = min(1.0, (rt - T / 4.0) / 0.4)
                self.dashed_circle(d, l2, MUTED, 0.7 * a)
                self.dashed_circle(d, l1, MUTED, 0.35 * a)
            a = min(1.0, rt / 0.3)
            X, Y = self.D_(0.0, 0.0)
            r = 6 * SS
            d.ellipse((X - r, Y - r, X + r, Y + r), fill=blend(GOLD, a, DECK_A))
        # The body: shaded slices across the width (lighter in the middle, like a cylinder).
        nb = 14
        for k in range(nb):
            u0, u1 = -1.0 + 2.0 * k / nb, -1.0 + 2.0 * (k + 1) / nb
            um = 0.5 * (u0 + u1)
            b = 0.55 + 0.45 * math.sqrt(max(0.0, 1.0 - um * um))
            poly = [self.D_(*self.cup_point(l1, u0, th)), self.D_(*self.cup_point(l2, u0, th)),
                    self.D_(*self.cup_point(l2, u1, th)), self.D_(*self.cup_point(l1, u1, th))]
            d.polygon(poly, fill=blend(CORAL, b, CUP_DARK))
        # The stripe along one generator: visible while its outward normal points up.
        vis = -(geo["cos_a"] ** 2 * math.cos(ps) + geo["sin_a"] ** 2)
        if vis > 0.02:
            g, yv = self.cup_frame(th)
            pts = []
            for s in (l1, l2):
                along = s * (geo["cos_a"] ** 2 + geo["sin_a"] ** 2 * math.cos(ps))
                across = s * geo["sin_a"] * math.sin(ps)
                pts.append(self.D_(along * g[0] + across * yv[0], along * g[1] + across * yv[1]))
            d.line((*pts[0], *pts[1]), fill=blend(STRIPE, min(1.0, vis / 0.96), CORAL), width=5 * SS)
        # The outline, the closed bottom (small rim) and the open mouth (large rim).
        outline = [self.D_(*self.cup_point(l1, -1.0, th)), self.D_(*self.cup_point(l2, -1.0, th)),
                   self.D_(*self.cup_point(l2, 1.0, th)), self.D_(*self.cup_point(l1, 1.0, th))]
        d.line(outline + [outline[0]], fill=CUP_DARK, width=2 * SS)
        d.polygon(self.rim_points(l1, th), fill=blend(CORAL, 0.75, CUP_DARK), outline=CUP_DARK, width=2 * SS)
        d.polygon(self.rim_points(l2, th), fill=CUP_MOUTH, outline=blend(CORAL, 0.8, WHITE), width=2 * SS)

    def draw_can(self, d: ImageDraw.ImageDraw, st: dict) -> None:
        man = self.man
        ppm = self.ppm
        scale = self.Hc / (self.Hc + st["drop"])
        dim = 1.0 - 0.65 * min(1.0, st["drop"] / man["desk_height_m"])
        base = DECK_A if not st["off"] else BG
        cx = self.cx
        cy = self.ay - st["y"] * ppm
        hw, hh = 0.5 * self.L_can * ppm * scale, self.r_can * ppm * scale
        # The trail of the centre on the desk.
        if st["y"] > 0.0:
            ye = max(cy, self.edge_y)
            d.line((*self.L_(cx, self.ay), *self.L_(cx, ye)), fill=blend(TEAL, 0.4, DECK_A), width=2 * SS)
        # Shaded bands across the roll direction (lighter along the top line of the cylinder).
        nb = 12
        for k in range(nb):
            v0, v1 = -1.0 + 2.0 * k / nb, -1.0 + 2.0 * (k + 1) / nb
            vm = 0.5 * (v0 + v1)
            b = (0.5 + 0.5 * math.sqrt(max(0.0, 1.0 - vm * vm))) * dim
            d.rectangle((*self.L_(cx - hw, cy + v0 * hh), *self.L_(cx + hw, cy + v1 * hh)), fill=blend(TEAL, b, base))
        # Two stripes half a turn apart, each visible while its normal points up.
        for ps in (st["psi"], st["psi"] + math.pi):
            vis = -math.cos(ps)
            if vis > 0.02:
                yy = cy - self.r_can * ppm * scale * math.sin(ps)
                d.line((*self.L_(cx - hw + 2, yy), *self.L_(cx + hw - 2, yy)), fill=blend(STRIPE, vis * dim, TEAL), width=max(1, int(6 * scale)) * SS)
        # The ends (the lids edge-on) and the outline.
        for sx in (-1.0, 1.0):
            d.rectangle((*self.L_(cx + sx * hw - (4 * scale if sx > 0 else 0), cy - hh), *self.L_(cx + sx * hw + (4 * scale if sx < 0 else 0), cy + hh)),
                        fill=blend(WHITE, 0.6 * dim, base))
        d.rectangle((*self.L_(cx - hw, cy - hh), *self.L_(cx + hw, cy + hh)), outline=blend(CAN_DARK, dim, base), width=2 * SS)

    def draw_finger(self, d: ImageDraw.ImageDraw, tau: float, x: float, top: float) -> None:
        """A finger mark below the object: it slides up, taps at the nudge, pulls back and fades."""
        na, fs = self.na, self.man["finger_s"]
        if tau < na:
            u = max(0.0, (tau - (na - fs)) / fs)
            gap = 60.0 * (1.0 - u * u)
            a = 1.0
        else:
            u = (tau - na) / 0.6
            if u >= 1.0:
                return
            gap = 60.0 * u
            a = 1.0 - u
        y0 = top + gap
        y1 = y0 + FINGER_L
        x0, x1 = x - FINGER_T / 2.0, x + FINGER_T / 2.0
        d.rounded_rectangle((*self.L_(x0, y0), *self.L_(x1, y1)), radius=FINGER_T / 2.0 * SS, fill=blend(FINGER, a, DECK_A))
        d.rounded_rectangle((*self.L_(x0 + 3, y0 + 3), *self.L_(x1 - 3, y0 + 14)), radius=3 * SS, fill=blend(NAIL, a, DECK_A))
        if 0.0 <= tau - na < 0.3:
            b = 1.0 - (tau - na) / 0.3
            for ang in (-40, 0, 40):
                sx, cx_ = math.sin(math.radians(ang)), math.cos(math.radians(ang))
                q0 = self.L_(x + 10 * sx, top - 4 - 4 * cx_)
                q1 = self.L_(x + 20 * sx, top - 4 - 14 * cx_)
                d.line((*q0, *q1), fill=blend(GOLD, b, DECK_A), width=2 * SS)

    def scene(self, tau: float) -> tuple[Image.Image, dict]:
        """The geometry layer at tau seconds into a cycle (both objects at rest before the nudge)."""
        layer = Image.new("RGB", (W * SS, (LAYER_Y1 - LAYER_Y0) * SS), BG)
        d = ImageDraw.Draw(layer)
        self.draw_desk(d)
        rt = tau - self.na
        cs = cup_state(self.ev, rt)
        ks = can_state(self.ev, self.man, rt)
        self.draw_cup(d, cs, tau)
        self.draw_can(d, ks)
        # The fingers: under the cup's centre of mass and under the can.
        cup_bottom = self.ay + (self.rho / self.geo["cos_a"]) * self.geo["sin_a"] * self.ppm
        self.draw_finger(d, tau, self.ax + self.rho * self.ppm, cup_bottom)
        self.draw_finger(d, tau, self.cx, self.ay + self.r_can * self.ppm)
        turn = float(np.interp(min(max(rt, 0.0), self.ev["run"]["T_lap"]), self.ev["run"]["t"], np.abs(self.ev["run"]["psi"])))
        st = {"rt": rt, "cup": cs, "can": ks, "turns": turn / TWO_PI, "lap": cs["theta"] / TWO_PI}
        return layer, st

    def draw_frame_layer(self, f: int) -> tuple[Image.Image, dict]:
        k, tau = self.phase(f)
        P, F = self.P, self.F
        layer, st = self.scene(tau)
        st["alpha"], st["k"] = 1.0, k
        if tau >= P - F:
            # Crossfade to the next cycle's setup (the cup holds at its start and the can rests on the floor by now, asserted).
            a = (tau - (P - F)) / F
            new, st_new = self.scene(tau - P)
            layer = Image.blend(layer, new, a)
            st["alpha"] = max(0.0, 1.0 - 2.0 * a)
            st_new["alpha"], st_new["k"] = max(0.0, 2.0 * a - 1.0), k + 1
            if a >= 0.5:
                st = st_new
        return layer, st

    def draw_text(self, d: ImageDraw.ImageDraw, st: dict, hud_alpha: float) -> None:
        man, ev = self.man, self.ev
        a = st["alpha"]
        d.text((ROW_X0, LABEL_Y), label_text("cup"), font=self.font, fill=CORAL, anchor="lm")
        d.text((ROW_X1, LABEL_Y), label_text("can"), font=self.font, fill=TEAL, anchor="rm")
        d.text(((ROW_X0 + ROW_X1) / 2.0, SUB_Y), sub_text(man), font=self.font_small, fill=MUTED, anchor="mm")
        ks, cs = st["can"], st["cup"]
        if ks["floor"]:
            d.text((ROW_X1, READ_Y), floor_text(), font=self.font_small, fill=blend(GOLD, a), anchor="rm")
        elif ks["off"]:
            d.text((ROW_X1, READ_Y), off_text(), font=self.font_small, fill=blend(GOLD, a), anchor="rm")
        else:
            d.text((ROW_X1, READ_Y), moved_text(ks["y"]), font=self.font_small, fill=blend(TEXT, a), anchor="rm")
        d.text((self.ax, self.ay + COUNTER_DY[0]), turned_text(st["turns"]), font=self.font_small,
               fill=blend(GOLD if cs["done"] else TEXT, a, DECK_A), anchor="mm")
        d.text((self.ax, self.ay + COUNTER_DY[1]), lap_text(st["lap"]), font=self.font_small,
               fill=blend(GOLD if cs["done"] else TEXT, a, DECK_A), anchor="mm")
        if cs["rt"] > 0.0:
            d.text((self.ax, self.ay + TIP_DY), tip_text(), font=self.font_tiny,
                   fill=blend(GOLD, 0.85 * min(1.0, cs["rt"] / 0.3) * a, DECK_A), anchor="mm")
        if ks["off"]:
            d.text((W / 2.0, EVENT_Y[0]), event_text(ev, "can"), font=self.font, fill=blend(GOLD, a, DECK_A), anchor="mm")
        if cs["done"]:
            d.text((W / 2.0, EVENT_Y[1]), event_text(ev, "cup"), font=self.font, fill=blend(GOLD, a, DECK_A), anchor="mm")
        if hud_alpha > 0.02:
            d.text((TEXT_X0, LEGEND_Y), legend_text(), font=self.font, fill=blend(TEXT, hud_alpha), anchor="lm")
            d.text((TEXT_X0, CLOCK_Y), clock_text(st["rt"]), font=self.font_small, fill=blend(MUTED, hud_alpha), anchor="lm")

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
        layer, st = self.draw_frame_layer(f)
        img.paste(layer.reduce(SS), (0, LAYER_Y0))
        d = ImageDraw.Draw(img)
        self.draw_text(d, st, hud_alpha)
        if title_alpha > 0.0:
            for j, line in enumerate(man["title"].split("|")):
                d.text((TEXT_X0, TITLE_Y[j]), line, font=self.font_title, fill=blend(TEXT, title_alpha), anchor="lm")
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
            # The geometry runs on; the legend, clock and card fade out over the first half of the
            # loop fade and the title fades in over the second half, so the two never overlap.
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
        wrap = self.live_frame(total, title_alpha=1.0, hud_alpha=0.0)   # the scene one period on, drawn live
        diff = np.abs(first.astype(int) - wrap.astype(int))
        print(f"periodicity check: the scene drawn live at {self.man['scene_duration']:g} s differs from 0 s in "
              f"{int((diff.max(axis=2) > 24).sum())} px (max channel difference {int(diff.max())})")
        prev = self.frame_at(total - 2)
        diff = np.abs(prev.astype(int) - last.astype(int))
        print(f"loop step: the frame before the last differs from the last in {int((diff.max(axis=2) > 24).sum())} px")
        # The overlay band and the caption band must stay background in the footage.
        for name, y0, y1 in (("overlay band", 96, 130), ("caption band", 1440, 1530)):
            worst = 0
            for f in (0, total // 7, total // 3, total // 2, int(0.9 * total)):
                band = self.frame_at(f)[y0:y1 + 1]
                worst = max(worst, int(np.abs(band.astype(int) - np.array(BG)).max()))
            print(f"{name} check (y {y0} to {y1}, five frames): max channel difference from the background {worst}")
            assert worst == 0, f"the {name} is not background-only"
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
    man = json.loads((ROOT / "projects/cuproll/manifest.json").read_text())
    ev = measure(man)
    if "--measure-only" in sys.argv:
        return
    if "--frames" in sys.argv:
        times = [float(v) for v in sys.argv[sys.argv.index("--frames") + 1].split(",")]
        r = Renderer(man, ev)
        (ROOT / "media/cuproll").mkdir(parents=True, exist_ok=True)
        for tv in times:
            Image.fromarray(r.frame_at(int(round(tv * man["fps"])))).save(ROOT / f"media/cuproll/smoke-{tv}.png")
        print("smoke frames: " + ", ".join(f"{tv}" for tv in times))
        return
    Renderer(man, ev).render(ROOT / "media/cuproll/footage.mp4")


if __name__ == "__main__":
    main()
