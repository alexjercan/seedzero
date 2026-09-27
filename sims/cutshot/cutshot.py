#!/usr/bin/env python3
"""Cut shot: do the two balls split at a right angle?

Two cue balls hit a ball at rest half on (the cue ball's centre aimed at the
object ball's edge: impact parameter one radius, sin(cut) = 1/2, a 30 degree
cut) at the same speed v0, seen from above one panel above the other. The top
cue ball arrives sliding with no spin (a stun shot: struck with the little
backspin that the cloth wears off exactly at the hit); the bottom cue ball
arrives rolling (spin v0 / R along its line). Equal masses, an instantaneous,
elastic and frictionless hit between the balls: the object ball takes the
component of the cue ball's velocity along the line of centres (v0 cos 30,
30 degrees off the cue line to one side) and the cue ball keeps the
perpendicular component (v0 sin 30 along the tangent line, 60 degrees off its
line to the other side) and whatever spin it had. The cloth acts on any
slipping contact with sliding friction mu (a solid sphere, I = 2/5 m R^2):
the slip u = v - w (w the spin as a surface velocity) keeps a fixed
direction and shrinks at 7/2 mu g, so each sliding phase is a constant
acceleration piece, -mu g u_hat on the velocity and 5/2 mu g u_hat on the
spin; a ball with no slip rolls on at constant velocity (no rolling
resistance). So the no-spin cue ball only slows along the tangent line and
settles rolling at 5/7 of v0 sin 30, its path exactly 90 degrees from the
object ball's; the rolling cue ball keeps its old spin, the cloth acts along
one fixed direction, its path is a parabola and it settles at v_final =
(5/7) v_after + (2/7) v0_vec, bent back toward its old line, so the two paths
meet at less than 90 degrees. Every ball is integrated as exact constant
acceleration pieces between the events (a slip closing, the hit) and checked
against the closed forms. The shot repeats every shot_period seconds of
video with a crossfade to the next launch; the period divides the scene
length, so the scene is exactly periodic and the last frame equals the
first. Shown at 1/slow speed. Deterministic, no seed.

Measured and printed: the launch states, the state of both cue balls at the
instant of the hit, the contact geometry, the velocities right after the hit
with the momentum and energy balance, each cue ball's settled speed, heading,
time and slip distance against the closed forms, the object ball's settled
speed, time and distance, the angle between the two balls' final paths in
each panel, the same shot at other cuts (the 30 degree rule) and other
speeds for the description, the schedule in video time, the loop and
periodicity checks and the on-screen text widths.

usage: cutshot.py [--measure-only] [--frames t1,t2,...]
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
CLOTH = (26, 62, 52)
CLOTH_RIM = (74, 104, 90)
DOT = (60, 30, 26)
OBJ_DOT = (110, 72, 24)

# Layout: overlay at y 96..130 (captions.py), three title rows at y 172/234/296 for
# the first seconds, then the shot counter at y 236 and the legend at y
# 290; the "no spin" row (label, state, readout) at y 380 over the top
# panel, a top-down cloth at y 404..874; the "rolling" row at y 920 over
# the bottom panel, its cloth at y 944..1414; both cloths x 40..1040,
# drawn at 2x; captions at caption_y 0.75 (y 1440..1520); the payoff card
# from y 1592.
COUNTER_Y, TAG_Y = 236, 290
PANEL_X0, PANEL_W, PANEL_H = 40, 1000, 470
SS = 2
PAYOFF_Y = 1592.0
PANELS = {"top": {"label": "no spin", "row_y": 380, "cloth_y": 404},
          "bottom": {"label": "rolling", "row_y": 920, "cloth_y": 944}}
ROW_X0, STATE_GAP, READ_X = 100, 26, 980
STATES = ("sliding", "rolling", "slipping")
LIGHT = np.array([-0.35, 0.45, 0.82])
LIGHT /= np.linalg.norm(LIGHT)


def blend(col, a: float, base=BG) -> tuple:
    a = max(0.0, min(1.0, a))
    return tuple(int(round(c * a + b * (1 - a))) for c, b in zip(col, base))


def deg(v) -> float:
    return math.degrees(math.atan2(v[1], v[0]))


def cross2(a, b) -> float:
    return float(a[0] * b[1] - a[1] * b[0])


def angle_between(v1, v2) -> float:
    c = float(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))
    return math.degrees(math.acos(max(-1.0, min(1.0, c))))


# --- measurement --------------------------------------------------------------
def slip_accel(v: np.ndarray, w: np.ndarray, ug: float):
    """Cloth friction on a ball with velocity v and spin w (both 2-vectors, w as the surface
    velocity of the spin, so the contact slips at u = v - w and rolling is v = w): the
    acceleration -mu g u_hat of v, the rate 5/2 mu g u_hat of w, and the time until the slip
    closes at 7/2 mu g; zeros and None when the ball rolls."""
    u = v - w
    s = float(np.hypot(u[0], u[1]))
    if s < 1e-9:
        return np.zeros(2), np.zeros(2), None
    uh = u / s
    return -ug * uh, 2.5 * ug * uh, s / (3.5 * ug)


def first_root(g0: float, dv: float, da: float):
    """Smallest positive t with g0 + dv t + da t^2 / 2 = 0 while the gap is closing."""
    if abs(da) < 1e-12:
        if dv < -1e-15 and g0 > 0.0:
            return g0 / -dv
        return None
    A, B, C = 0.5 * da, dv, g0
    disc = B * B - 4.0 * A * C
    if disc < 0.0:
        return None
    sq = math.sqrt(disc)
    for r in sorted(((-B - sq) / (2.0 * A), (-B + sq) / (2.0 * A))):
        if r > 1e-12 and dv + da * r < 0.0:
            return r
    return None


def integrate(cue: dict, obj: dict, x_hit: float, t_start: float, t_end: float, ug: float) -> dict:
    """Both balls of one panel from t_start (before the launch at t = 0, the launch state run
    backward with its own accelerations) to t_end as exact constant-acceleration pieces
    (t0, t1, p0, v0, a, w0, alpha) between the events: a slip closing, the hit. Before the hit
    the cue ball runs along the x axis toward x_hit (its centre at contact) and the object ball
    rests, so the hit is the root of a quadratic in t."""
    balls = {"cue": {k: np.array(v, dtype=float) for k, v in cue.items()},
             "obj": {k: np.array(v, dtype=float) for k, v in obj.items()}}
    for b in balls.values():
        a, al, _ = slip_accel(b["v"], b["w"], ug)
        ts = t_start
        b["p"] = b["p"] + b["v"] * ts + 0.5 * a * ts * ts
        b["v"] = b["v"] + a * ts
        b["w"] = b["w"] + al * ts
    pieces: dict[str, list] = {"cue": [], "obj": []}
    events: list = []
    t = t_start
    hit_done = False
    while t < t_end - 1e-12:
        acc = {}
        dt_next, kind = t_end - t, ("end", None)
        for name, b in balls.items():
            a, al, dt_close = slip_accel(b["v"], b["w"], ug)
            acc[name] = (a, al)
            if dt_close is not None and dt_close < dt_next:
                dt_next, kind = dt_close, ("roll", name)
        if not hit_done:
            c = balls["cue"]
            r = first_root(x_hit - c["p"][0], -c["v"][0], -acc["cue"][0][0])
            if r is not None and r < dt_next:
                dt_next, kind = r, ("hit", None)
        for name, b in balls.items():
            a, al = acc[name]
            pieces[name].append((t, t + dt_next, b["p"].copy(), b["v"].copy(), a.copy(), b["w"].copy(), al.copy()))
            b["p"] = b["p"] + b["v"] * dt_next + 0.5 * a * dt_next * dt_next
            b["v"] = b["v"] + a * dt_next
            b["w"] = b["w"] + al * dt_next
        t += dt_next
        for name, b in balls.items():
            # Every ball whose slip closes on this step (in the rolling panel the cue ball and the
            # object ball close theirs at the same instant): snap out the rounding, record the event.
            if np.any(acc[name][0] != 0.0) and float(np.hypot(*(b["v"] - b["w"]))) < 1e-7:
                b["w"] = b["v"].copy()
                events.append((t, "roll", name, {k: v.copy() for k, v in b.items()}))
        if kind[0] == "hit":
            before = {n: {k: v.copy() for k, v in b.items()} for n, b in balls.items()}
            d = balls["obj"]["p"] - balls["cue"]["p"]
            n = d / np.linalg.norm(d)
            J = float(np.dot(balls["cue"]["v"] - balls["obj"]["v"], n)) * n
            balls["cue"]["v"] = balls["cue"]["v"] - J
            balls["obj"]["v"] = balls["obj"]["v"] + J
            events.append((t, "hit", None, {"before": before, "n": n, "gap": float(np.linalg.norm(d)),
                                            "after": {n_: {k: v.copy() for k, v in b.items()} for n_, b in balls.items()}}))
            hit_done = True
    return {"pieces": pieces, "events": events, "t_start": t_start, "t_end": t_end,
            "final": {n: {k: v.copy() for k, v in b.items()} for n, b in balls.items()}}


def state_at(shot: dict, name: str, r: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """(p, v, w) of a ball at real time r, clamped to the shot's span."""
    ps = shot["pieces"][name]
    r = min(max(r, ps[0][0]), ps[-1][1])
    for t0, t1, p0, v0, a, w0, al in ps:
        if r < t1 - 1e-9:
            break                   # on a boundary (to rounding) the later piece wins: the state after the event
    dt = r - t0
    return p0 + v0 * dt + 0.5 * a * dt * dt, v0 + a * dt, w0 + al * dt


def event(shot: dict, kind: str, name=None):
    for ev in shot["events"]:
        if ev[1] == kind and ev[2] == name:
            return ev
    return None


def path_length(shot: dict, name: str, r0: float, r1: float, n: int = 4000) -> float:
    ts = np.linspace(r0, r1, n + 1)
    pts = np.array([state_at(shot, name, r)[0] for r in ts])
    return float(np.sum(np.hypot(*np.diff(pts, axis=0).T)))


def run_panel(man: dict, panel: str, v0: float, cut_deg: float, t_start: float, t_end: float) -> dict:
    """One panel's shot at speed v0 and cut angle cut_deg: the launch states and the integration."""
    R, ug = man["ball_radius_m"], man["mu"] * man["g"]
    alpha = 2.5 * ug
    c = math.radians(cut_deg)
    x_hit = man["hit_x_m"]
    d_b = man["run_up_m"]
    t_run = d_b / v0
    obj0 = {"p": (x_hit + 2.0 * R * math.cos(c), 2.0 * R * math.sin(c)), "v": (0.0, 0.0), "w": (0.0, 0.0)}
    if panel == "top":
        # The stun launch, run backward from the hit over t_run with the cloth's friction on
        # (slip positive: the speed falls, the backspin wears off).
        v_l = v0 + ug * t_run
        w_l = -alpha * t_run
        d_t = v_l * t_run - 0.5 * ug * t_run * t_run
        cue0 = {"p": (x_hit - d_t, 0.0), "v": (v_l, 0.0), "w": (w_l, 0.0)}
    else:
        cue0 = {"p": (x_hit - d_b, 0.0), "v": (v0, 0.0), "w": (v0, 0.0)}
    shot = integrate(cue0, obj0, x_hit, t_start, t_end, ug)
    shot["launch"], shot["obj0"], shot["t_run"], shot["x_hit"] = cue0, obj0, t_run, x_hit
    return shot


def measure(man: dict) -> dict:
    R, mu, g, v0 = man["ball_radius_m"], man["mu"], man["g"], man["hit_speed_m_s"]
    ug = mu * g
    cut = man["cut_deg"]
    slow, P, D, fps = man["slow"], man["shot_period"], man["scene_duration"], man["fps"]
    F = man["reset_fade"]
    ppm = man["px_per_m"]
    shots_n = D / P
    assert abs(shots_n - round(shots_n)) < 1e-9, "the shot period must divide the scene length"
    for key in ("shot_period", "first_shot_at", "reset_fade"):
        assert abs(man[key] * fps - round(man[key] * fps)) < 1e-9, f"{key} must be a whole number of frames"
    x_hit = man["hit_x_m"]
    t_run = man["run_up_m"] / v0
    b = 2.0 * R * math.sin(math.radians(cut))
    print(f"setup: two cue balls hit a ball at rest half on at v0 = {v0:g} m/s, seen from above one panel above "
          f"the other (ball radius {R * 1000:g} mm, a {2 * R * 1000:g} mm ball, equal masses, a solid sphere I = 2/5 "
          f"m R^2, cloth sliding friction mu = {mu:g} on any slipping contact, g = {g:g} m/s^2, no rolling "
          f"resistance, no friction between the balls, an instantaneous elastic hit that hands the object ball the "
          f"velocity component along the line of centres and keeps each ball's spin); the object ball sits half a "
          f"ball to one side of the cue line (impact parameter b = R = {b * 1000:.1f} mm, sin(cut) = b / 2 R = "
          f"{b / (2 * R):.4f}, cut {cut:g} degrees), its centre {2 * R * math.cos(math.radians(cut)) * 100:.2f} cm "
          f"ahead of the hit point along the line and {2 * R * math.sin(math.radians(cut)) * 100:.2f} cm to the side; "
          f"the top cue ball arrives sliding with no spin (a stun shot: struck with the backspin that the cloth "
          f"wears off exactly at the hit), the bottom cue ball arrives rolling (spin v0 / R = {v0 / R:.2f} rad/s); "
          f"the run-up is {man['run_up_m'] * 100:g} cm to the hit point at x = {x_hit:g} m of the "
          f"{PANEL_W / ppm:.2f} by {PANEL_H / ppm:.2f} m cloth, the cue line across its middle; each panel "
          f"integrated as exact constant-acceleration pieces between the events (a slip closing, the hit); shown "
          f"at 1/{slow:g} speed, one shot every {P:g} s of video, {shots_n:.0f} shots in {D:g} s; drawn at {ppm:g} "
          f"px per metre (ball radius {R * ppm:.1f} px); deterministic, no seed")
    t_start, t_end = -(F / 2.0) / slow, P / slow
    shots = {p: run_panel(man, p, v0, cut, t_start, t_end) for p in PANELS}
    lt, lb = shots["top"]["launch"], shots["bottom"]["launch"]
    print(f"launch (t = 0 of each shot, real time): the rolling cue ball leaves x = {lb['p'][0]:.4f} m at "
          f"{lb['v'][0]:.4f} m/s rolling (spin {lb['v'][0] / R:.3f} rad/s) and reaches the hit point after "
          f"{t_run:.4f} s ({man['run_up_m']:.4f} m); the no-spin cue ball leaves x = {lt['p'][0]:.4f} m, "
          f"{(x_hit - lt['p'][0]) * 100:.2f} cm behind the hit point, at {lt['v'][0]:.4f} m/s with "
          f"{-lt['w'][0] / R:.3f} rad/s of backspin (surface speed {-lt['w'][0]:.4f} m/s), so that the cloth (mu g "
          f"= {ug:.4f} m/s^2 on the speed, 5/2 mu g = {2.5 * ug:.4f} m/s^2 on the spin's surface speed, 7/2 mu g "
          f"= {3.5 * ug:.4f} m/s^2 on the slip) wears the backspin off exactly at the hit")
    hits = {p: event(shots[p], "hit") for p in PANELS}
    hb = {p: hits[p][3]["before"] for p in PANELS}
    ha = {p: hits[p][3]["after"] for p in PANELS}
    t_hit = {p: hits[p][0] for p in PANELS}
    n_hit = hits["bottom"][3]["n"]
    print(f"hit: at {t_hit['top']:.4f} s (top) and {t_hit['bottom']:.4f} s (bottom) of real time (target {t_run:.4f} "
          f"s, diffs {abs(t_hit['top'] - t_run):.1e} and {abs(t_hit['bottom'] - t_run):.1e}) the cue balls' centres "
          f"reach x = {hb['top']['cue']['p'][0]:.4f} m ({x_hit:.4f}) with the centres {hits['top'][3]['gap'] * 1000:.3f} "
          f"mm apart (2 R = {2 * R * 1000:.3f}) on a line of centres {deg(n_hit):.2f} degrees off the cue line "
          f"(cut {cut:g}); top cue ball {np.linalg.norm(hb['top']['cue']['v']):.4f} m/s, spin surface speed "
          f"{np.linalg.norm(hb['top']['cue']['w']):.1e} m/s (target {v0:.4f} and 0); bottom cue ball "
          f"{np.linalg.norm(hb['bottom']['cue']['v']):.4f} m/s, spin {np.linalg.norm(hb['bottom']['cue']['w']) / R:.3f} "
          f"rad/s along its line (v0 / R = {v0 / R:.3f}); right after: the object ball {np.linalg.norm(ha['top']['obj']['v']):.4f} "
          f"(top) and {np.linalg.norm(ha['bottom']['obj']['v']):.4f} m/s (bottom) at {deg(ha['bottom']['obj']['v']):.2f} "
          f"degrees off the cue line with no spin (closed form v0 cos {cut:g} = {v0 * math.cos(math.radians(cut)):.4f} "
          f"m/s); the cue balls {np.linalg.norm(ha['top']['cue']['v']):.4f} and {np.linalg.norm(ha['bottom']['cue']['v']):.4f} "
          f"m/s at {deg(ha['bottom']['cue']['v']):.2f} degrees off the cue line to the other side, along the tangent "
          f"line (closed form v0 sin {cut:g} = {v0 * math.sin(math.radians(cut)):.4f} m/s at {90 - cut:g} degrees), "
          f"the top one with no spin and the bottom one with its rolling spin unchanged "
          f"({np.linalg.norm(ha['bottom']['cue']['w']) / R:.3f} rad/s along the old line); the two paths leave the hit "
          f"{angle_between(ha['bottom']['cue']['v'], ha['bottom']['obj']['v']):.2f} degrees apart in both panels; "
          f"momentum before and after the hit ({hb['bottom']['cue']['v'][0] + hb['bottom']['obj']['v'][0]:.4f}, "
          f"{hb['bottom']['cue']['v'][1] + hb['bottom']['obj']['v'][1]:.4f}) = "
          f"({ha['bottom']['cue']['v'][0] + ha['bottom']['obj']['v'][0]:.4f}, "
          f"{ha['bottom']['cue']['v'][1] + ha['bottom']['obj']['v'][1]:.4f}), translational energy "
          f"{0.5 * (np.dot(hb['bottom']['cue']['v'], hb['bottom']['cue']['v']) + np.dot(hb['bottom']['obj']['v'], hb['bottom']['obj']['v'])):.4f} = "
          f"{0.5 * (np.dot(ha['bottom']['cue']['v'], ha['bottom']['cue']['v']) + np.dot(ha['bottom']['obj']['v'], ha['bottom']['obj']['v'])):.4f} "
          f"per unit mass")
    # The no-spin cue ball: friction only along the tangent line.
    v_t = v0 * math.sin(math.radians(cut))
    t_a_c = v_t / (3.5 * ug)
    v_a_c = 5.0 * v_t / 7.0
    d_a_c = v_t * t_a_c - 0.5 * ug * t_a_c * t_a_c
    ra = event(shots["top"], "roll", "cue")
    t_a, s_a = ra[0] - t_hit["top"], ra[3]
    d_a = path_length(shots["top"], "cue", t_hit["top"], ra[0])
    ro = {p: event(shots[p], "roll", "obj") for p in PANELS}
    ang_a = angle_between(s_a["v"], ro["top"][3]["v"])
    head_a = deg(s_a["v"])
    print(f"no spin: after the hit the slip at the contact is the ball's own velocity, so the cloth only slows it "
          f"along the tangent line; it settles rolling at {np.linalg.norm(s_a['v']):.4f} m/s, {head_a:.2f} degrees "
          f"off its old line (unchanged), after {t_a:.4f} s and {d_a * 100:.2f} cm of slip (closed forms 5/7 of "
          f"{v_t:.4f} = {v_a_c:.4f} m/s, 2 v / (7 mu g) = {t_a_c:.4f} s, v t - 1/2 mu g t^2 = {d_a_c * 100:.2f} cm; "
          f"diffs {abs(np.linalg.norm(s_a['v']) - v_a_c):.1e}, {abs(t_a - t_a_c):.1e}, {abs(d_a - d_a_c):.1e}); the "
          f"deviation from the tangent line along the way is at most "
          f"{max(abs(cross2(state_at(shots['top'], 'cue', t_hit['top'] + k * 0.002)[0] - hb['top']['cue']['p'], ha['top']['cue']['v'] / v_t)) for k in range(int((t_end - t_hit['top']) / 0.002))) * 1000:.1e} "
          f"mm; its path and the object ball's path meet at {ang_a:.2f} degrees (a right angle)")
    # The rolling cue ball: the kept spin, a slip along one fixed direction, a parabola.
    u_b = ha["bottom"]["cue"]["v"] - ha["bottom"]["cue"]["w"]
    t_b_c = np.linalg.norm(u_b) / (3.5 * ug)
    v_b_c = 5.0 / 7.0 * ha["bottom"]["cue"]["v"] + 2.0 / 7.0 * hb["bottom"]["cue"]["v"]
    rb = event(shots["bottom"], "roll", "cue")
    t_b, s_b = rb[0] - t_hit["bottom"], rb[3]
    d_b = path_length(shots["bottom"], "cue", t_hit["bottom"], rb[0])
    chord = float(np.linalg.norm(s_b["p"] - hb["bottom"]["cue"]["p"]))
    ang_b = angle_between(s_b["v"], ro["bottom"][3]["v"])
    head_b = deg(s_b["v"])
    print(f"rolling: right after the hit the slip at the contact is v_after - v0_vec = ({u_b[0]:.4f}, {u_b[1]:.4f}) "
          f"m/s, {np.linalg.norm(u_b):.4f} m/s at {deg(u_b):.2f} degrees, and it keeps that direction while it "
          f"shrinks at 7/2 mu g, so the cloth's push mu g on the cue ball points one fixed way and the path is a "
          f"parabola; it settles rolling at ({s_b['v'][0]:.4f}, {s_b['v'][1]:.4f}) = {np.linalg.norm(s_b['v']):.4f} "
          f"m/s, {abs(head_b):.2f} degrees off its old line, after {t_b:.4f} s, {d_b * 100:.2f} cm of curve "
          f"({chord * 100:.2f} cm as the crow flies) (closed forms v_final = 5/7 v_after + 2/7 v0_vec = "
          f"({v_b_c[0]:.4f}, {v_b_c[1]:.4f}) = {np.linalg.norm(v_b_c):.4f} m/s at {abs(deg(v_b_c)):.2f} degrees, "
          f"2 |u| / (7 mu g) = {t_b_c:.4f} s; diffs {abs(np.linalg.norm(s_b['v']) - np.linalg.norm(v_b_c)):.1e}, "
          f"{abs(abs(head_b) - abs(deg(v_b_c))):.1e}, {abs(t_b - t_b_c):.1e}); its spin turns from {v0 / R:.3f} rad/s "
          f"along the old line to {np.linalg.norm(s_b['w']) / R:.3f} rad/s along the new one; the kept spin bends "
          f"it from {abs(deg(ha['bottom']['cue']['v'])):.2f} to {abs(head_b):.2f} degrees off its line, "
          f"{abs(deg(ha['bottom']['cue']['v'])) - abs(head_b):.2f} degrees back from the tangent line; its path and "
          f"the object ball's path meet at {ang_b:.2f} degrees ({cut:g} + {abs(head_b):.2f}), not a right angle")
    # The object ball, both panels.
    v_o = v0 * math.cos(math.radians(cut))
    t_o_c = v_o / (3.5 * ug)
    v_o_c = 5.0 * v_o / 7.0
    d_o_c = v_o * t_o_c - 0.5 * ug * t_o_c * t_o_c
    t_o = {p: ro[p][0] - t_hit[p] for p in PANELS}
    d_o = {p: float(np.linalg.norm(ro[p][3]["p"] - shots[p]["obj0"]["p"])) for p in PANELS}
    exit_t = {}
    for p in PANELS:
        exit_t[p] = {}
        for name in ("cue", "obj"):
            lo, hi = t_hit[p], t_end
            for _ in range(80):
                mid = 0.5 * (lo + hi)
                pm = state_at(shots[p], name, mid)[0]
                out = pm[0] - R > PANEL_W / ppm or abs(pm[1]) - R > PANEL_H / (2.0 * ppm)
                if out:
                    hi = mid
                else:
                    lo = mid
            exit_t[p][name] = hi - t_hit[p]
    print(f"object ball: leaves sliding at {v_o:.4f} m/s with no spin, {cut:g} degrees off the cue line, and rolls at "
          f"{np.linalg.norm(ro['top'][3]['v']):.4f} (top) and {np.linalg.norm(ro['bottom'][3]['v']):.4f} m/s (bottom) "
          f"after {t_o['top']:.4f} and {t_o['bottom']:.4f} s and {d_o['top'] * 100:.2f} and {d_o['bottom'] * 100:.2f} "
          f"cm, its direction unchanged ({deg(ro['bottom'][3]['v']):.2f} degrees) (closed forms 5/7 of {v_o:.4f} = "
          f"{v_o_c:.4f} m/s, {t_o_c:.4f} s, {d_o_c * 100:.2f} cm; diffs {abs(np.linalg.norm(ro['bottom'][3]['v']) - v_o_c):.1e}, "
          f"{abs(t_o['bottom'] - t_o_c):.1e}, {abs(d_o['bottom'] - d_o_c):.1e}); in the rolling panel the object ball "
          f"and the cue ball settle at the same instant (both slips start at {np.linalg.norm(u_b):.4f} m/s); the "
          f"balls leave the cloth (top panel) {exit_t['top']['obj'] * slow:.2f} s (object) and {exit_t['top']['cue'] * slow:.2f} "
          f"s (cue) of video after the hit, (bottom panel) {exit_t['bottom']['obj'] * slow:.2f} and "
          f"{exit_t['bottom']['cue'] * slow:.2f} s")
    print(f"answer: the two balls' final paths meet at {ang_a:.2f} degrees with no spin and {ang_b:.2f} degrees "
          f"rolling; the cue ball settles at {np.linalg.norm(s_a['v']):.4f} m/s after {d_a * 100:.1f} cm of slip "
          f"with no spin and at {np.linalg.norm(s_b['v']):.4f} m/s after {d_b * 100:.1f} cm of curve rolling")
    # Other cuts (the 30 degree rule) and other speeds, for the description.
    descr = []
    for cd, name in zip(man["description_cuts_deg"], man["description_cut_names"]):
        s = run_panel(man, "bottom", v0, cd, t_start, t_end)
        h = event(s, "hit")
        rc, rob = event(s, "roll", "cue"), event(s, "roll", "obj")
        dl = path_length(s, "cue", h[0], rc[0])
        descr.append(f"{name} ({cd:.2f} degree cut, sin = {math.sin(math.radians(cd)):.2f}): the rolling cue ball leaves "
                     f"at {90 - cd:.2f} degrees and settles {abs(deg(rc[3]['v'])):.2f} degrees off its line at "
                     f"{np.linalg.norm(rc[3]['v']):.4f} m/s after {dl * 100:.1f} cm, the paths {angle_between(rc[3]['v'], rob[3]['v']):.2f} "
                     f"degrees apart (no spin: {90.0:.2f})")
    print("for the description (same speed, other cuts; the 30 degree rule): " + "; ".join(descr))
    descr = []
    for u in man["description_speeds_m_s"]:
        st = run_panel(man, "top", u, cut, t_start, t_end)
        sb = run_panel(man, "bottom", u, cut, t_start, t_end)
        hst, hsb = event(st, "hit"), event(sb, "hit")
        rt, rbb = event(st, "roll", "cue"), event(sb, "roll", "cue")
        rot, rob = event(st, "roll", "obj"), event(sb, "roll", "obj")
        descr.append(f"{u:g} m/s: no spin {angle_between(rt[3]['v'], rot[3]['v']):.2f} degrees after "
                     f"{path_length(st, 'cue', hst[0], rt[0]) * 100:.1f} cm of slip, rolling "
                     f"{angle_between(rbb[3]['v'], rob[3]['v']):.2f} degrees ({abs(deg(rbb[3]['v'])):.2f} off its line) "
                     f"after {path_length(sb, 'cue', hsb[0], rbb[0]) * 100:.1f} cm of curve, the object ball "
                     f"{np.linalg.norm(rob[3]['v']):.4f} m/s after {np.linalg.norm(rob[3]['p'] - sb['obj0']['p']) * 100:.1f} cm")
    print("for the description (same cut, other speeds): " + "; ".join(descr))
    # Schedule in video time.
    t0 = man["first_shot_at"]
    k0 = math.ceil((0.0 - t0) / P - 1e-9)
    k1 = math.floor((D - t0) / P - 1e-9)
    launches_v = [t0 + k * P for k in range(k0, k1 + 1)]
    hit_v = t_run * slow
    hits_v = [tl + hit_v for tl in [t0 + k * P for k in range(k0 - 1, k1 + 1)] if 0.0 <= tl + hit_v < D]
    print(f"schedule (video time, 1/{slow:g} speed): launches every {P:g} s at "
          + ", ".join(f"{tl:.2f}" for tl in launches_v)
          + f" s (the first shot launched at {t0:g} s, {-t0:.2f} s before the first frame, its cue balls "
          f"{-t0 / slow * v0 * 100:.1f} cm into the run-up); the hit {hit_v:.2f} s after each launch, at "
          + ", ".join(f"{th:.2f}" for th in hits_v)
          + f" s; the no-spin cue ball rolls again {t_a * slow:.2f} s after the hit, at "
          + ", ".join(f"{th + t_a * slow:.2f}" for th in hits_v)
          + f" s; the rolling cue ball and both object balls roll again {t_b * slow:.2f} s after the hit, at "
          + ", ".join(f"{th + t_b * slow:.2f}" for th in hits_v)
          + f" s; the balls leave the cloth {min(min(e.values()) for e in exit_t.values()) * slow:.2f} to "
          f"{max(max(e.values()) for e in exit_t.values()) * slow:.2f} s after the hit and the trails stay; the "
          f"shot crossfades to the next launch over the last {F:g} s of each {P:g} s (out over {P - F:.2f} to "
          f"{P - F / 2:.2f} s, in over {P - F / 2:.2f} to {P:.2f} s after the launch, the incoming cue balls run in "
          f"from the left); title until {man['title_until']:g} s; payoff card from {man['payoff_t']:g} s; the "
          f"title fades back in over the last {man['loop_fade']:g} s and the last frame repeats the first")
    ev = {"ug": ug, "t_run": t_run, "x_hit": x_hit, "shots": shots, "t_hit": t_hit["bottom"], "t_hits": dict(t_hit),
          "v_a": float(np.linalg.norm(s_a["v"])), "t_a": t_a, "d_a": d_a, "ang_a": ang_a,
          "v_b": float(np.linalg.norm(s_b["v"])), "t_b": t_b, "d_b": d_b, "ang_b": ang_b, "head_b": abs(head_b),
          "v_obj": float(np.linalg.norm(ro["bottom"][3]["v"])), "d_obj": d_o["bottom"], "t_obj": t_o["bottom"],
          "shots_n": int(round(shots_n)), "n_hit": n_hit, "v_t": v_t}
    # Text widths.
    font = os.environ["SEED_ZERO_FONT"]
    f28, f34, f40, f56 = (ImageFont.truetype(font, n) for n in (28, 34, 40, 56))
    widths = {"overlay@34": (f34, man["overlay"])}
    for j, line in enumerate(man["title"].split("|")):
        widths[f"title line {j + 1}@56"] = (f56, line)
    widths["counter@40"] = (f40, counter_text(ev, ev["shots_n"] - 1))
    widths["legend@28"] = (f28, legend_text(man))
    for p in PANELS:
        widths[f"label {p}@40"] = (f40, PANELS[p]["label"])
    for s in STATES:
        widths[f"state {s}@28"] = (f28, s)
    widths["speed@40"] = (f40, speed_text(lt["v"][0]))
    widths["split@40"] = (f40, split_text(ang_a))
    widths["cue tag@28"] = (f28, "cue ball")
    widths["scale@28"] = (f28, scale_text(man))
    widths["tangent tag@28"] = (f28, "tangent line")
    for j, line in enumerate(payoff_lines(man, ev)):
        widths[f"payoff line {j + 1}@40"] = (f40, line)
    print("text widths: " + ", ".join(f"{k} {f.getlength(s):.0f} px" for k, (f, s) in widths.items()))
    assert all(f.getlength(s) < 950 for f, s in widths.values()), "a text line is wider than 950 px"
    row_w = max(f40.getlength(PANELS[p]["label"]) for p in PANELS) + STATE_GAP + max(f28.getlength(s) for s in STATES)
    read_w = max(f40.getlength(speed_text(lt["v"][0])), f40.getlength(split_text(ang_a)))
    print(f"row check: label plus state end at x {ROW_X0 + row_w:.0f} px at most, the readout starts at x "
          f"{READ_X - read_w:.0f} px")
    assert ROW_X0 + row_w < READ_X - read_w - 40, "the row texts collide"
    return ev


def counter_text(ev: dict, shot: int) -> str:
    return f"shot {shot + 1} of {ev['shots_n']}"


def legend_text(man: dict) -> str:
    return f"no spin at the hit above, rolling below; 1/{man['slow']:g} speed"


def speed_text(v: float) -> str:
    return f"cue ball {v:.2f} m/s"


def split_text(ang: float) -> str:
    return f"split {ang:.1f}°"


def scale_text(man: dict) -> str:
    return f"{man['scale_bar_m'] * 100:g} cm"


def payoff_lines(man: dict, ev: dict) -> list[str]:
    text = man["payoff_text"].format(ang_a=ev["ang_a"], ang_b=ev["ang_b"], head_b=ev["head_b"], d_a_cm=ev["d_a"] * 100,
                                     d_b_cm=ev["d_b"] * 100, v_a=ev["v_a"], v_b=ev["v_b"])
    return [s.strip() for s in text.split("|")]


# --- rendering ---------------------------------------------------------------
def rodrigues(th: np.ndarray) -> np.ndarray:
    a = float(np.linalg.norm(th))
    if a < 1e-15:
        return np.eye(3)
    k = th / a
    K = np.array([[0.0, -k[2], k[1]], [k[2], 0.0, -k[0]], [-k[1], k[0], 0.0]])
    return np.eye(3) + math.sin(a) * K + (1.0 - math.cos(a)) * (K @ K)


class Renderer:
    def __init__(self, man: dict, ev: dict):
        self.man, self.ev = man, ev
        self.fps = man["fps"]
        font = os.environ["SEED_ZERO_FONT"]
        self.font = ImageFont.truetype(font, 40)
        self.font_title = ImageFont.truetype(font, 56)
        self.font_small = ImageFont.truetype(font, 28)
        self.ppm = float(man["px_per_m"])
        self.R = man["ball_radius_m"]
        self.slow = man["slow"]
        self.P, self.t0, self.F = man["shot_period"], man["first_shot_at"], man["reset_fade"]
        self.shots = ev["shots"]
        self.t_hit = ev["t_hit"]
        self.t_hits = ev["t_hits"]
        self.sin_band = math.sin(math.radians(man["stripe_half_angle_deg"]))
        self.cos_dot = math.cos(math.radians(man["dot_angle_deg"]))
        self.roll_end = {p: {n: (event(self.shots[p], "roll", n)[0] if event(self.shots[p], "roll", n) else None)
                             for n in ("cue", "obj")} for p in PANELS}
        # Orientation tables: the rotation of every ball at each frame of the shot span, from the
        # tau = -reset_fade / 2 frame to the tau = shot_period frame, integrated from the launch
        # (the identity: the stripe across the ball, the dot on top) with Rodrigues steps.
        self.j0 = int(round(self.F / 2.0 * self.fps))
        n = int(round((self.P + self.F / 2.0) * self.fps)) + 1
        sub = int(man["orientation_substeps"])
        self.rots = {p: {name: self.orientation_table(p, name, n, sub) for name in ("cue", "obj")} for p in PANELS}

    def orientation_table(self, panel: str, name: str, n: int, sub: int) -> np.ndarray:
        shot = self.shots[panel]
        R = self.R
        h = 1.0 / (self.fps * self.slow * sub)
        rots = np.empty((n, 3, 3))
        rots[self.j0] = np.eye(3)

        def omega_at(r: float) -> np.ndarray:
            w = state_at(shot, name, r)[2]
            return np.array([-w[1], w[0], 0.0]) / R      # omega = z x w / R: rolling forward spins about +y

        M = np.eye(3)
        for j in range(self.j0 + 1, n):
            r0 = (j - 1 - self.j0) / (self.fps * self.slow)
            for s in range(sub):
                M = rodrigues(omega_at(r0 + (s + 0.5) * h) * h) @ M
            rots[j] = M
        M = np.eye(3)
        for j in range(self.j0 - 1, -1, -1):
            r0 = (j + 1 - self.j0) / (self.fps * self.slow)
            for s in range(sub):
                M = rodrigues(-omega_at(r0 - (s + 0.5) * h) * h) @ M
            rots[j] = M
        return rots

    # --- state helpers ------------------------------------------------------
    def phase(self, f: int) -> tuple[int, int]:
        """(shot index, frame offset since its launch) of frame f."""
        f0 = int(round(self.t0 * self.fps))
        pf = int(round(self.P * self.fps))
        k = (f - f0) // pf
        return k, f - f0 - k * pf

    # --- pixel helpers ------------------------------------------------------
    def L(self, x: float, y: float) -> tuple[float, float]:
        """Layer (2x) pixel of a cloth point (x, y) in metres, y up on the cloth, the cue line at y = 0."""
        return x * self.ppm * SS, (PANEL_H / 2.0 - y * self.ppm) * SS

    def dashed(self, d: ImageDraw.ImageDraw, p0, p1, col, dash: float, gap: float, width: int) -> None:
        x0, y0 = p0
        x1, y1 = p1
        ln = math.hypot(x1 - x0, y1 - y0)
        if ln < 1e-9:
            return
        ux, uy = (x1 - x0) / ln, (y1 - y0) / ln
        s = 0.0
        while s < ln:
            e = min(ln, s + dash)
            d.line((x0 + ux * s, y0 + uy * s, x0 + ux * e, y0 + uy * e), fill=col, width=width)
            s += dash + gap

    def ball(self, arr: np.ndarray, X: float, Y: float, rot: np.ndarray, a: float, striped: bool) -> None:
        """A shaded sphere seen from above, composited into the layer array at alpha a: the base
        colour, the stripe band (|p . n| < sin of the half angle, n the body x axis turned by rot)
        and the dot (the body z axis, on top at the launch)."""
        rr = self.R * self.ppm * SS
        x0, x1 = int(math.floor(X - rr)) - 1, int(math.ceil(X + rr)) + 2
        y0, y1 = int(math.floor(Y - rr)) - 1, int(math.ceil(Y + rr)) + 2
        x0, y0 = max(0, x0), max(0, y0)
        x1, y1 = min(arr.shape[1], x1), min(arr.shape[0], y1)
        if x1 <= x0 or y1 <= y0:
            return
        xs = (np.arange(x0, x1) + 0.5 - X) / rr
        ys = (np.arange(y0, y1) + 0.5 - Y) / rr
        px = np.broadcast_to(xs[None, :], (y1 - y0, x1 - x0))
        py = np.broadcast_to(-ys[:, None], (y1 - y0, x1 - x0))
        r2 = px * px + py * py
        inside = r2 <= 1.0
        pz = np.sqrt(np.clip(1.0 - r2, 0.0, 1.0))
        shade = 0.58 + 0.42 * np.clip(px * LIGHT[0] + py * LIGHT[1] + pz * LIGHT[2], 0.0, 1.0)
        base = np.array(WHITE if striped else GOLD, dtype=float)
        col = np.empty((y1 - y0, x1 - x0, 3))
        col[:] = base
        if striped:
            nw = rot @ np.array([1.0, 0.0, 0.0])
            band = np.abs(px * nw[0] + py * nw[1] + pz * nw[2]) < self.sin_band
            col[band] = np.array(CORAL, dtype=float)
        dw = rot @ np.array([0.0, 0.0, 1.0])
        dot = (px * dw[0] + py * dw[1] + pz * dw[2]) > self.cos_dot
        col[dot] = np.array(DOT if striped else OBJ_DOT, dtype=float)
        col *= shade[..., None]
        edge = r2 > ((rr - 2.0 * SS) / rr) ** 2
        col[edge] = np.array(RIM if striped else (120, 84, 30), dtype=float)
        sub = arr[y0:y1, x0:x1]
        sub[inside] = sub[inside] * (1.0 - a) + col[inside] * a

    # --- the scene ----------------------------------------------------------
    def draw_shot(self, d: ImageDraw.ImageDraw, balls: list, panel: str, fo: int, a: float) -> dict:
        """One shot of one panel at frame offset fo since its launch, blended by a: the trails on
        the PIL layer now, the balls queued for the numpy pass."""
        shot = self.shots[panel]
        r = fo / (self.fps * self.slow)
        rr = self.R * self.ppm * SS
        cp, cv, cw = state_at(shot, "cue", r)
        op, ov, ow = state_at(shot, "obj", r)
        t_hit = self.t_hits[panel]
        hit = r >= t_hit - 1e-9          # the two panels' hit times differ by rounding only
        settled = {n: self.roll_end[panel][n] is not None and r >= self.roll_end[panel][n] - 1e-9 for n in ("cue", "obj")}
        if hit:
            # The trails from the hit: the cue ball's in white, the object ball's in gold.
            for name, col in (("obj", GOLD), ("cue", WHITE)):
                ts = np.arange(t_hit, r, 1.0 / (self.fps * self.slow))
                pts = [self.L(*state_at(shot, name, t)[0]) for t in ts] + [self.L(*(state_at(shot, name, r)[0]))]
                if len(pts) > 1:
                    d.line(pts, fill=blend(col, 0.75 * a, CLOTH), width=3 * SS, joint="curve")
        rots = self.rots[panel]
        j = fo + self.j0
        balls.append((self.L(*op), rots["obj"][j], a, False))
        balls.append((self.L(*cp), rots["cue"][j], a, True))
        cX, cY = self.L(*cp)
        tag = (PANEL_X0 + max(cX / SS, 62.0), PANELS[panel]["cloth_y"] + cY / SS - rr / SS - 20)
        # The tag only while the cue ball's centre is on the cloth, so no tag floats at the edge
        # while a stun ball is still in the run-up off the left edge.
        tag_on = cX / SS >= 0.0
        return {"p": cp, "v": cv, "w": cw, "ov": ov, "hit": hit, "settled": settled, "alpha": a, "tag": tag,
                "tag_on": tag_on}

    def draw_panel(self, img: Image.Image, panel: str, f: int, hud_alpha: float) -> dict:
        man = self.man
        k, fo = self.phase(f)
        layer = Image.new("RGB", (PANEL_W * SS, PANEL_H * SS), CLOTH)
        d = ImageDraw.Draw(layer)
        # The guides: the cue line (the cue ball's old line, faint and solid) and the tangent line
        # through the hit point (faint and dashed); the hit point tick; the scale bar.
        hx, hy = self.L(self.ev["x_hit"], 0.0)
        d.line((*self.L(0.0, 0.0), *self.L(PANEL_W / self.ppm, 0.0)), fill=blend(MUTED, 0.3, CLOTH), width=2 * SS)
        tdir = np.array([-self.ev["n_hit"][1], self.ev["n_hit"][0]])     # the tangent, 90 degrees from the line of centres
        span = 2.0 * PANEL_W / self.ppm
        p0 = np.array([self.ev["x_hit"], 0.0]) - tdir * span
        p1 = np.array([self.ev["x_hit"], 0.0]) + tdir * span
        self.dashed(d, self.L(*p0), self.L(*p1), blend(TEAL, 0.5, CLOTH), 16 * SS, 12 * SS, 3 * SS)
        d.line((hx - 8 * SS, hy - 8 * SS, hx + 8 * SS, hy + 8 * SS), fill=blend(WHITE, 0.6, CLOTH), width=2 * SS)
        d.line((hx - 8 * SS, hy + 8 * SS, hx + 8 * SS, hy - 8 * SS), fill=blend(WHITE, 0.6, CLOTH), width=2 * SS)
        sx0, sy0 = self.L(man["scale_bar_x_m"], -(PANEL_H / 2.0 - man["scale_bar_dy_px"]) / self.ppm)
        sx1, _ = self.L(man["scale_bar_x_m"] + man["scale_bar_m"], 0.0)
        d.line((sx0, sy0, sx1, sy0), fill=blend(TEXT, 0.8, CLOTH), width=3 * SS)
        for xx in (sx0, sx1):
            d.line((xx, sy0 - 8 * SS, xx, sy0 + 8 * SS), fill=blend(TEXT, 0.8, CLOTH), width=3 * SS)
        # The shot in progress, crossfading to the next launch over the last reset_fade frames.
        Ff, Pf = int(round(self.F * self.fps)), int(round(self.P * self.fps))
        a_old = 1.0 if fo <= Pf - Ff else max(0.0, (Pf - Ff / 2.0 - fo) / (Ff / 2.0))
        balls: list = []
        st = self.draw_shot(d, balls, panel, fo, a_old) if a_old > 0.0 else None
        if fo >= Pf - Ff / 2.0:
            a_new = (fo - (Pf - Ff / 2.0)) / (Ff / 2.0)
            st_new = self.draw_shot(d, balls, panel, fo - Pf, a_new)
            if st is None or a_new >= 0.5:
                st = st_new
        arr = np.asarray(layer, dtype=float)
        for (X, Y), rot, a, striped in balls:
            self.ball(arr, X, Y, rot, a, striped)
        layer = Image.fromarray(np.clip(arr + 0.5, 0, 255).astype(np.uint8))
        img.paste(layer.reduce(SS), (PANEL_X0, PANELS[panel]["cloth_y"]))
        st["k"] = k
        return st

    def draw_text(self, d: ImageDraw.ImageDraw, states: dict, t: float, hud_alpha: float) -> None:
        man, ev = self.man, self.ev
        for panel, st in states.items():
            row = PANELS[panel]["row_y"]
            label = PANELS[panel]["label"]
            d.text((ROW_X0, row), label, font=self.font, fill=TEXT, anchor="lm")
            if not st["hit"]:
                word = "sliding" if panel == "top" else "rolling"
            elif st["settled"]["cue"]:
                word = "rolling"
            else:
                word = "sliding" if panel == "top" else "slipping"
            a = st["alpha"]
            d.text((ROW_X0 + self.font.getlength(label) + STATE_GAP, row + 2), word, font=self.font_small,
                   fill=blend(MUTED, a), anchor="lm")
            if st["hit"]:
                final = st["settled"]["cue"] and st["settled"]["obj"]
                text = split_text(angle_between(st["v"], st["ov"]))
                d.text((READ_X, row), text, font=self.font, fill=blend(GOLD if final else TEXT, a), anchor="rm")
            else:
                d.text((READ_X, row), speed_text(float(np.linalg.norm(st["v"]))), font=self.font, fill=blend(TEXT, a), anchor="rm")
            if not st["hit"] and st["tag_on"]:
                d.text(st["tag"], "cue ball", font=self.font_small, fill=blend(WHITE, 0.8 * a), anchor="mm")
            cy = PANELS[panel]["cloth_y"]
            d.text((PANEL_X0 + man["scale_bar_x_m"] * self.ppm + man["scale_bar_m"] * self.ppm / 2.0,
                    cy + PANEL_H - man["scale_bar_dy_px"] - 22), scale_text(man), font=self.font_small, fill=MUTED, anchor="mm")
            # The tangent line's tag at its upper left end, inside the cloth, clear of every path.
            tdir = np.array([-ev["n_hit"][1], ev["n_hit"][0]])
            tdir = tdir if tdir[1] > 0 else -tdir
            s = (PANEL_H / 2.0 / self.ppm - 0.03) / tdir[1]
            tx = PANEL_X0 + (ev["x_hit"] + tdir[0] * s) * self.ppm - 112
            ty = cy + 30
            d.text((tx, ty), "tangent line", font=self.font_small, fill=blend(TEAL, 0.7, CLOTH), anchor="mm")
        if hud_alpha > 0.02:
            shot = min(max(states["top"]["k"], 0), ev["shots_n"] - 1)
            d.text((W / 2, COUNTER_Y), counter_text(ev, shot), font=self.font, fill=blend(TEXT, hud_alpha), anchor="mm")
            d.text((W / 2, TAG_Y), legend_text(man), font=self.font_small, fill=blend(MUTED, hud_alpha), anchor="mm")

    def live_frame(self, f: int, title_alpha: float | None = None, hud_alpha: float = 0.0) -> np.ndarray:
        """Frame f with the geometry at f / fps; title_alpha and hud_alpha override the title and
        the counter/legend/card blend during the loop fade."""
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
        states = {panel: self.draw_panel(img, panel, f, hud_alpha) for panel in PANELS}
        d = ImageDraw.Draw(img)
        for panel in PANELS:
            cy = PANELS[panel]["cloth_y"]
            d.rectangle((PANEL_X0 - 3, cy - 3, PANEL_X0 + PANEL_W + 2, cy + PANEL_H + 2), outline=CLOTH_RIM, width=3)
        self.draw_text(d, states, t, hud_alpha)
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
            # The geometry runs on; the counter, legend and card fade out over the first half of the
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
        wrap = self.live_frame(total, title_alpha=1.0, hud_alpha=0.0)   # the geometry one period on, drawn live
        diff = np.abs(first.astype(int) - wrap.astype(int))
        print(f"periodicity check: the scene drawn live at {self.man['scene_duration']:g} s differs from 0 s in "
              f"{int((diff.max(axis=2) > 24).sum())} px (max channel difference {int(diff.max())})")
        prev = self.frame_at(total - 2)
        diff = np.abs(prev.astype(int) - last.astype(int))
        print(f"loop step: the frame before the last differs from the last in {int((diff.max(axis=2) > 24).sum())} px "
              f"(the incoming cue balls are still fading in on that frame)")
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
    man = json.loads((ROOT / "projects/cutshot/manifest.json").read_text())
    ev = measure(man)
    if "--measure-only" in sys.argv:
        return
    if "--frames" in sys.argv:
        times = [float(v) for v in sys.argv[sys.argv.index("--frames") + 1].split(",")]
        r = Renderer(man, ev)
        (ROOT / "media/cutshot").mkdir(parents=True, exist_ok=True)
        for tv in times:
            Image.fromarray(r.frame_at(int(round(tv * man["fps"])))).save(ROOT / f"media/cutshot/smoke-{tv}.png")
        print("smoke frames: " + ", ".join(f"{tv}" for tv in times))
        return
    Renderer(man, ev).render(ROOT / "media/cutshot/footage.mp4")


if __name__ == "__main__":
    main()
