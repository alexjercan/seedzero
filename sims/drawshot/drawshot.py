#!/usr/bin/env python3
"""Draw shot: hit it low, does the cue ball come back?

The same low hit on two cue balls, drawn from the side one above the other.
A level cue strikes each cue ball tip_offset_R radii below its centre, so the
ball leaves at v0 with backspin: the horizontal impulse J gives m v0 = J and
I omega0 = J h with I = 2/5 m R^2, so R omega0 = (5/2)(h / R) v0 against the
roll. The cloth acts on any slipping contact with sliding friction mu (a solid
sphere): the speed falls at mu g and the backspin R omega at (5/2) mu g, so
the slip v - R omega (omega counted forward) closes at (7/2) mu g; the
backspin is gone after h v0 / (mu g) seconds and

    d* = v0^2 h (2 - h) / (2 mu g) = (v0^2 - (v0 - 0.4 R omega0)^2) / (2 mu g),

after which the spin turns forward and the ball rolls at (5 v0 - 2 R omega0) / 7.
The other ball waits dead ahead: 30 cm of the cue ball's travel to the hit on
top (the near panel), 1.2 m below (the far panel). The balls have equal mass
and the hit is head on, instantaneous, elastic and frictionless between the
balls, so the cue ball hands over all its speed and keeps its spin; the cloth
then turns that spin into motion: backspin R omega brings it back at 2/7 of
R omega, forward spin sends it after the other ball at 2/7 of its rolling
speed. Every ball is integrated as exact constant-acceleration pieces between
the events (a slip closing, the hit) and checked against the closed forms and
against a stepped integration. The shot repeats every cycle_s seconds of video
with a crossfade; the cycle divides the scene length and the frames are drawn
from the frame number modulo the cycle, so the scene is exactly periodic and
the last frame equals the first. Shown at 1/slow speed. Deterministic, no seed.

Measured and printed: the launch (the impulse relation), where and when the
backspin is gone and the ball rolls, both hits (time, speed, spin left), the
cue ball's speed after each hit (back or forward, the slip distance, the 2/7
fractions), the object balls, the threshold d* and a sweep of the other ball's
distance, the threshold at other cloths, tip offsets and speeds for the
description, the stepped-integration check, the schedule in video time, the
loop and periodicity checks and the on-screen text widths.

usage: drawshot.py [--measure-only] [--frames t1,t2,...]
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
DECK_A = (30, 36, 46)
CLOTH = (38, 120, 92)
WOOD = (196, 160, 112)
WOOD_DARK = (150, 116, 76)
CHALK = (70, 120, 210)

# Layout: overlay at y 96..130 (drawn by compose), the title in three rows at
# y 180/242/304 for the first seconds, then the legend at y 236 and the clock
# at y 290; the near panel with its label row at y 430, its second row at 474,
# the dashed line's label at y 572 and the cloth at y 740; the far panel the
# same 500 px lower (rows 930/974, label 1072, cloth 1240); each table body 60
# px deep under its cloth holds the gold trail at +10, the distance bracket at
# +24 and the bracket label and the d* mark (right of the gold line) at +44; the geometry layer y 560..1340 is
# drawn at 2x; captions at caption_y 0.75 (y 1440..1530); the seven-line card
# from y 1572 at a 48 px pitch (last row centred at 1860).
TITLE_Y0, TITLE_PITCH = 180, 62
LEGEND_Y, CLOCK_Y = 236, 290
GEOM_Y0, GEOM_Y1 = 560, 1340
SS = 2
PAYOFF_Y, PAYOFF_PITCH = 1572.0, 48
PANELS = {"near": {"label": "close", "row_y": 430, "cloth_y": 740, "dist_key": "near_object_m"},
          "far": {"label": "far", "row_y": 930, "cloth_y": 1240, "dist_key": "far_object_m"}}
SUB_DY, LINE_TOP_DY, LINE_LABEL_DY = 44, 150, 168
BODY_PX, TRAIL_DY, BRACKET_DY, BODY_LABEL_DY = 60, 10, 24, 44
ROW_X0, ROW_X1, STATE_GAP = 40, 1040, 22
MARK_DX = 10
STATES = ("at rest", "backspin", "no spin", "topspin", "rolling", "rolling back")


def blend(col, a: float, base=BG) -> tuple:
    a = max(0.0, min(1.0, a))
    return tuple(int(round(c * a + b * (1 - a))) for c, b in zip(col, base))


# --- measurement --------------------------------------------------------------
def ball_accel(v: float, w: float, R: float, ug: float, alpha: float):
    """Acceleration of the speed and of the spin from the cloth: sliding friction against the
    slip v - R omega (omega counted forward, so rolling is v = R omega), none when it rolls.
    Returns (a, alpha, time until the slip closes or None)."""
    s = v - R * w
    if abs(s) < 1e-9:
        return 0.0, 0.0, None
    sg = 1.0 if s > 0.0 else -1.0
    return -ug * sg, alpha * sg, abs(s) / (3.5 * ug)


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


def integrate(cue: dict, obj: dict | None, t_end: float, R: float, ug: float, alpha: float) -> dict:
    """The cue ball from the strike at t = 0 (and the other ball, if any) to t_end as exact
    constant-acceleration pieces (t0, t1, x0, v0, a, omega0, alpha, theta0) between the events:
    a slip closing, the hit."""
    balls = {"cue": dict(cue, th=0.0)}
    if obj is not None:
        balls["obj"] = dict(obj, th=0.0)
    launch = {n: dict(b) for n, b in balls.items()}
    pieces: dict[str, list] = {n: [] for n in balls}
    events: list = []
    t = 0.0
    while t < t_end - 1e-12:
        acc = {}
        dt_next, kind = t_end - t, "end"
        for name, b in balls.items():
            a, al, dt_close = ball_accel(b["v"], b["w"], R, ug, alpha)
            acc[name] = (a, al)
            if dt_close is not None and dt_close < dt_next:
                dt_next, kind = dt_close, "roll"
        if obj is not None:
            g0 = balls["obj"]["x"] - balls["cue"]["x"] - 2.0 * R
            r = first_root(g0, balls["obj"]["v"] - balls["cue"]["v"], acc["obj"][0] - acc["cue"][0])
            if r is not None and r < dt_next:
                dt_next, kind = r, "hit"
        for name, b in balls.items():
            a, al = acc[name]
            pieces[name].append((t, t + dt_next, b["x"], b["v"], a, b["w"], al, b["th"]))
            b["th"] += b["w"] * dt_next + 0.5 * al * dt_next * dt_next
            b["x"] += b["v"] * dt_next + 0.5 * a * dt_next * dt_next
            b["v"] += a * dt_next
            b["w"] += al * dt_next
        t += dt_next
        for name, b in balls.items():
            # Every ball whose slip closes on this step: snap out the rounding and record the event.
            if acc[name][0] != 0.0 and abs(b["v"] - R * b["w"]) < 1e-7:
                b["w"] = b["v"] / R
                events.append((t, "roll", name, dict(b)))
        if kind == "hit":
            before = {n: dict(b) for n, b in balls.items()}
            balls["cue"]["v"], balls["obj"]["v"] = balls["obj"]["v"], balls["cue"]["v"]
            events.append((t, "hit", None, {"before": before, "after": {n: dict(b) for n, b in balls.items()}}))
    return {"pieces": pieces, "events": events, "t_end": t_end, "launch": launch,
            "final": {n: dict(b) for n, b in balls.items()}}


def state_at(shot: dict, name: str, r: float) -> tuple[float, float, float, float]:
    """(x, v, omega, theta) of a ball at real time r after the strike; at rest before it."""
    if r < 0.0:
        return shot["launch"][name]["x"], 0.0, 0.0, 0.0
    ps = shot["pieces"][name]
    r = min(r, ps[-1][1])
    for t0, t1, x0, v0, a, w0, al, th0 in ps:
        if r < t1:
            break                   # on a boundary the later piece wins: the state after the event
    dt = r - t0
    return (x0 + v0 * dt + 0.5 * a * dt * dt, v0 + a * dt, w0 + al * dt, th0 + w0 * dt + 0.5 * al * dt * dt)


def events_of(shot: dict, kind: str, name=None) -> list:
    return [ev for ev in shot["events"] if ev[1] == kind and ev[2] == name]


def spin_zero(shot: dict, R: float):
    """The first instant the cue ball's backspin is gone (omega crosses zero from below) inside a
    piece: (t, x, v) or None."""
    for t0, t1, x0, v0, a, w0, al, th0 in shot["pieces"]["cue"]:
        if w0 < 0.0 and al > 0.0 and w0 + al * (t1 - t0) >= 0.0:
            dt = -w0 / al
            return t0 + dt, x0 + v0 * dt + 0.5 * a * dt * dt, v0 + a * dt
    return None


def cross_time(shot: dict, name: str, x_target: float, lo: float, hi: float, below: bool) -> float:
    """Bisection for the instant a ball's x passes x_target (moving right, or left when below)."""
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        x = state_at(shot, name, mid)[0]
        if (x <= x_target) if below else (x >= x_target):
            hi = mid
        else:
            lo = mid
    return hi


def stepped(man: dict, D: float, dt: float, t_end: float) -> dict:
    """The same shot by fixed steps: semi-implicit Euler on the speed and the spin while the ball
    slips, the slip snapped to rolling on the step where it would change sign (at the rolling speed
    (5 v + 2 R omega) / 7 that the contact keeps), the hit on the first step with the balls
    touching. Independent of the piecewise solution."""
    R, ug, v0 = man["ball_radius_m"], man["mu"] * man["g"], man["strike_speed_m_s"]
    alpha = 5.0 * ug / (2.0 * R)
    cue = [0.0, v0, -2.5 * man["tip_offset_R"] * v0 / R]
    obj = [D + 2.0 * R, 0.0, 0.0]
    out = {"rolls": {"cue": [], "obj": []}, "hit": None, "gone": None}
    close = 3.5 * ug * dt
    n = int(round(t_end / dt))
    for i in range(n):
        t = (i + 1) * dt
        for name, b in (("cue", cue), ("obj", obj)):
            s = b[1] - R * b[2]
            if s == 0.0:
                b[0] += b[1] * dt
                continue
            if abs(s) <= close:
                vr = (5.0 * b[1] + 2.0 * R * b[2]) / 7.0
                b[0] += 0.5 * (b[1] + vr) * dt
                b[1], b[2] = vr, vr / R
                out["rolls"][name].append((t, b[0], b[1]))
                continue
            w_old = b[2]
            sg = 1.0 if s > 0.0 else -1.0
            b[1] -= ug * sg * dt
            b[2] += alpha * sg * dt
            b[0] += b[1] * dt
            if name == "cue" and out["gone"] is None and w_old < 0.0 <= b[2]:
                out["gone"] = (t, b[0], b[1])
        if out["hit"] is None and obj[0] - cue[0] - 2.0 * R <= 0.0:
            out["hit"] = (t, cue[0], cue[1], R * cue[2])
            cue[1], obj[1] = obj[1], cue[1]
    out["final"] = {"cue": list(cue), "obj": list(obj)}
    return out


def threshold(v0: float, h: float, mu: float, g: float) -> float:
    """d* = v0^2 h (2 - h) / (2 mu g): the cue ball's travel when the cloth has worn the backspin off."""
    return v0 * v0 * h * (2.0 - h) / (2.0 * mu * g)


def measure(man: dict) -> dict:
    R, mu, g, v0, h = man["ball_radius_m"], man["mu"], man["g"], man["strike_speed_m_s"], man["tip_offset_R"]
    ug = mu * g
    alpha = 5.0 * ug / (2.0 * R)
    slow, P, D, fps = man["slow"], man["cycle_s"], man["scene_duration"], man["fps"]
    F, sa = man["reset_fade"], man["strike_at"]
    ppm, x0_px = man["px_per_m"], man["start_x_px"]
    cycles_n = D / P
    assert abs(cycles_n - round(cycles_n)) < 1e-9, "the cycle must divide the scene length"
    assert abs(P * fps - round(P * fps)) < 1e-9 and abs(man["first_cycle_at"] * fps - round(man["first_cycle_at"] * fps)) < 1e-9
    dist = {p: man[PANELS[p]["dist_key"]] for p in PANELS}
    Rw0 = 2.5 * h * v0
    w0 = -Rw0 / R
    print(f"setup: the same low hit on two cue balls, drawn from the side one above the other; a level cue strikes "
          f"each ball {h:g} radius below its centre and it leaves at v0 = {v0:g} m/s; ball radius {R * 1000:g} mm (a "
          f"{2 * R * 1000:g} mm ball), equal masses, a solid sphere I = 2/5 m R^2, cloth sliding friction mu = {mu:g} "
          f"on any slipping contact, g = {g:g} m/s^2, no rolling resistance, no cushion; the other ball waits dead "
          f"ahead, {dist['near'] * 100:g} cm of the cue ball's travel to the hit on top (centre to contact: the cue "
          f"ball's centre moves {dist['near'] * 100:g} cm before the balls touch, centres {(dist['near'] + 2 * R) * 100:.2f} "
          f"cm apart) and {dist['far'] * 100:g} cm below (centres {(dist['far'] + 2 * R) * 100:.2f} cm apart); the hit "
          f"is head on, instantaneous, elastic and frictionless between the balls (the cue ball hands over its speed "
          f"and keeps its spin); every ball integrated as exact constant-acceleration pieces between the events (a "
          f"slip closing, the hit), checked against the closed forms and a stepped integration; shown at 1/{slow:g} "
          f"speed on a {P:g} s cycle ({int(round(P * fps))} frames) with the strike {sa:g} s into the cycle, "
          f"{cycles_n:.0f} shots in {D:g} s; drawn at {ppm:g} px per metre (ball radius {R * ppm:.1f} px); "
          f"deterministic, no seed")
    # Launch and the run-out of the backspin, on its own (no other ball).
    J_spin = 2.5 * h * v0
    print(f"launch: the impulse J at h = {h:g} R below the centre gives m v0 = J and (2/5) m R^2 omega0 = J h, so R "
          f"omega0 = (5/2)(h / R) v0 = {J_spin:.4f} m/s of backspin (omega0 = {-w0:.3f} rad/s against the roll); "
          f"the slip v - R omega starts at {v0 + Rw0:.4f} m/s; the cloth slows the ball at mu g = {ug:.5f} m/s^2, "
          f"the backspin R omega at (5/2) mu g = {2.5 * ug:.5f} m/s^2 and the slip at (7/2) mu g = {3.5 * ug:.5f} m/s^2")
    solo = integrate({"x": 0.0, "v": v0, "w": w0}, None, 3.0, R, ug, alpha)
    tz, xz, vz = spin_zero(solo, R)
    tz_c, xz_c, vz_c = h * v0 / ug, threshold(v0, h, mu, g), v0 * (1.0 - h)
    xz_c2 = (v0 * v0 - (v0 - 0.4 * Rw0) ** 2) / (2.0 * ug)
    rl = events_of(solo, "roll", "cue")[0]
    tr_c = (v0 + Rw0) / (3.5 * ug)
    vr_c = (5.0 * v0 - 2.0 * Rw0) / 7.0
    xr_c = v0 * tr_c - 0.5 * ug * tr_c * tr_c
    print(f"backspin gone: the cue ball's backspin is gone at {tz:.4f} s after {xz * 100:.2f} cm at {vz:.4f} m/s "
          f"(closed forms h v0 / (mu g) = {tz_c:.4f} s, d* = v0^2 h (2 - h) / (2 mu g) = {xz_c * 100:.2f} cm = (v0^2 - "
          f"(v0 - 0.4 R omega0)^2) / (2 mu g) = {xz_c2 * 100:.2f} cm, v0 (1 - h) = {vz_c:.4f} m/s; diffs "
          f"{abs(tz - tz_c):.1e}, {abs(xz - xz_c):.1e}, {abs(vz - vz_c):.1e}); from there the spin turns forward and "
          f"the ball rolls at {rl[3]['v']:.4f} m/s at {rl[0]:.4f} s after {rl[3]['x'] * 100:.2f} cm (closed forms (5 v0 - "
          f"2 R omega0) / 7 = {vr_c:.4f} m/s, (v0 + R omega0) / (7/2 mu g) = {tr_c:.4f} s, {xr_c * 100:.2f} cm; diffs "
          f"{abs(rl[3]['v'] - vr_c):.1e}, {abs(rl[0] - tr_c):.1e}, {abs(rl[3]['x'] - xr_c):.1e})")
    shots = {p: integrate({"x": 0.0, "v": v0, "w": w0}, {"x": dist[p] + 2.0 * R, "v": 0.0, "w": 0.0},
                          (P - sa) / slow, R, ug, alpha) for p in PANELS}
    res = {}
    for p in PANELS:
        shot = shots[p]
        hit = events_of(shot, "hit")[0]
        t_hit, hb, ha = hit[0], hit[3]["before"], hit[3]["after"]
        rolls = [ev for ev in events_of(shot, "roll", "cue") if ev[0] > t_hit]
        rc = rolls[0]
        ro = [ev for ev in events_of(shot, "roll", "obj")][0]
        Rw_hit = R * hb["cue"]["w"]
        v_fin = rc[3]["v"]
        slip_d = rc[3]["x"] - hb["cue"]["x"]
        res[p] = {"t_hit": t_hit, "v_hit": hb["cue"]["v"], "Rw_hit": Rw_hit, "x_hit": hb["cue"]["x"], "v_fin": v_fin,
                  "t_settle": rc[0], "slip_d": slip_d, "v_obj": ro[3]["v"], "t_obj": ro[0], "x_obj_roll": ro[3]["x"],
                  "mom": (hb["cue"]["v"] + hb["obj"]["v"], ha["cue"]["v"] + ha["obj"]["v"]),
                  "en": (0.5 * (hb["cue"]["v"] ** 2 + hb["obj"]["v"] ** 2), 0.5 * (ha["cue"]["v"] ** 2 + ha["obj"]["v"] ** 2)),
                  "w_after": ha["cue"]["w"]}
    # Near: the backspin is not gone at the hit.
    n_, f_ = res["near"], res["far"]
    t_n_c = (v0 - math.sqrt(v0 * v0 - 2.0 * ug * dist["near"])) / ug
    v_n_c = v0 - ug * t_n_c
    Rw_n_c = -(Rw0 - 2.5 * ug * t_n_c)
    vb_c = (2.0 / 7.0) * Rw_n_c
    ts_n_c = abs(Rw_n_c) / (3.5 * ug)
    ds_n_c = -0.5 * ug * ts_n_c * ts_n_c
    print(f"near (the other ball {dist['near'] * 100:g} cm ahead, closer than d*): the cue ball hits it at {n_['t_hit']:.4f} s "
          f"at {n_['v_hit']:.4f} m/s with R omega = {n_['Rw_hit']:+.4f} m/s, {-n_['Rw_hit']:.4f} m/s of backspin left "
          f"(closed forms {t_n_c:.4f} s, {v_n_c:.4f} m/s, {Rw_n_c:+.4f} m/s; diffs {abs(n_['t_hit'] - t_n_c):.1e}, "
          f"{abs(n_['v_hit'] - v_n_c):.1e}, {abs(n_['Rw_hit'] - Rw_n_c):.1e}); right after the hit the cue ball has 0 "
          f"m/s and keeps its backspin; the cloth drags it back and it rolls back at {n_['v_fin']:+.4f} m/s "
          f"({-n_['v_fin']:.4f} m/s back) {n_['t_settle'] - n_['t_hit']:.4f} s after the hit and {-n_['slip_d'] * 100:.2f} cm "
          f"of slip (closed forms (2/7) R omega = {vb_c:+.4f} m/s, |R omega| / (7/2 mu g) = {ts_n_c:.4f} s, "
          f"{-ds_n_c * 100:.2f} cm; diffs {abs(n_['v_fin'] - vb_c):.1e}, {abs(n_['t_settle'] - n_['t_hit'] - ts_n_c):.1e}, "
          f"{abs(n_['slip_d'] - ds_n_c):.1e}); that is {-n_['v_fin'] / -n_['Rw_hit']:.5f} of the spin left (2/7 = "
          f"{2 / 7:.5f}); the other ball leaves at {n_['v_hit']:.4f} m/s with no spin and rolls at {n_['v_obj']:.4f} m/s "
          f"(5/7 of {n_['v_hit']:.4f} = {5 * n_['v_hit'] / 7:.4f}); momentum {n_['mom'][0]:.4f} = {n_['mom'][1]:.4f} and "
          f"translational energy {n_['en'][0]:.4f} = {n_['en'][1]:.4f} per unit mass across the hit")
    t_f_c = tr_c + (dist["far"] - xr_c) / vr_c
    vf_c = (2.0 / 7.0) * vr_c
    ts_f_c = vr_c / (3.5 * ug)
    ds_f_c = 0.5 * ug * ts_f_c * ts_f_c
    print(f"far (the other ball {dist['far'] * 100:g} cm ahead, farther than d*): the cue ball rolls into it at "
          f"{f_['t_hit']:.4f} s at {f_['v_hit']:.4f} m/s with R omega = {f_['Rw_hit']:+.4f} m/s (forward spin, rolling; "
          f"closed forms {t_f_c:.4f} s, {vr_c:.4f} m/s; diffs {abs(f_['t_hit'] - t_f_c):.1e}, {abs(f_['v_hit'] - vr_c):.1e}); "
          f"right after the hit the cue ball has 0 m/s and keeps its forward spin; the cloth drags it forward and it "
          f"follows at {f_['v_fin']:+.4f} m/s {f_['t_settle'] - f_['t_hit']:.4f} s after the hit and {f_['slip_d'] * 100:.2f} "
          f"cm of slip (closed forms (2/7) v = {vf_c:+.4f} m/s, v / (7/2 mu g) = {ts_f_c:.4f} s, {ds_f_c * 100:.2f} cm; "
          f"diffs {abs(f_['v_fin'] - vf_c):.1e}, {abs(f_['t_settle'] - f_['t_hit'] - ts_f_c):.1e}, "
          f"{abs(f_['slip_d'] - ds_f_c):.1e}); the other ball leaves at {f_['v_hit']:.4f} m/s and rolls at "
          f"{f_['v_obj']:.4f} m/s (5/7 = {5 * f_['v_hit'] / 7:.4f}); momentum {f_['mom'][0]:.4f} = {f_['mom'][1]:.4f}, "
          f"energy {f_['en'][0]:.4f} = {f_['en'][1]:.4f} per unit mass")
    print(f"answer: the same strike, only the other ball's distance differs: at {dist['near'] * 100:g} cm the cue ball comes "
          f"back at {-n_['v_fin']:.4f} m/s, at {dist['far'] * 100:g} cm it follows at {f_['v_fin']:.4f} m/s; the line between "
          f"is d* = {xz * 100:.2f} cm: any other ball closer than that is hit while backspin is left and the cue ball "
          f"comes back, any farther and the spin has turned forward and the cue ball follows (at d* itself it stops dead)")
    # The sweep over the other ball's distance.
    sweep = []
    for Dm in list(man["sweep_m"]) + [xz]:
        s = integrate({"x": 0.0, "v": v0, "w": w0}, {"x": Dm + 2.0 * R, "v": 0.0, "w": 0.0}, 4.0, R, ug, alpha)
        hv = events_of(s, "hit")[0]
        vfin = s["final"]["cue"]["v"]
        word = "comes back" if vfin < -1e-9 else ("follows" if vfin > 1e-9 else "stops dead")
        sweep.append((Dm, hv[0], hv[3]["before"]["cue"]["v"], R * hv[3]["before"]["cue"]["w"], vfin, word))
    sweep.sort()
    print("sweep (the same strike, the other ball at other distances; the cue ball's final speed, + forward): " + "; ".join(
        f"{Dm * 100:.2f} cm: hit at {th:.4f} s at {vh:.4f} m/s, R omega {rw:+.4f}, {word} at {vf:+.4f} m/s"
        for Dm, th, vh, rw, vf, word in sweep))
    # Other cloths, tips and speeds: the threshold from the piecewise run and the closed form.
    def d_star_run(v_: float, h_: float, mu_: float) -> float:
        u_ = mu_ * g
        s_ = integrate({"x": 0.0, "v": v_, "w": -2.5 * h_ * v_ / R}, None, 5.0, R, u_, 5.0 * u_ / (2.0 * R))
        return spin_zero(s_, R)[1]
    desc = {}
    parts = []
    for m_ in man["description_mus"]:
        desc[("mu", m_)] = d_star_run(v0, h, m_)
        parts.append(f"mu {m_:g}: {desc[('mu', m_)] * 100:.2f} cm (closed form {threshold(v0, h, m_, g) * 100:.2f})")
    for h_ in man["description_tips_R"]:
        desc[("tip", h_)] = d_star_run(v0, h_, mu)
        parts.append(f"tip {h_:g} R low (R omega0 = {2.5 * h_ * v0:.2f} m/s): {desc[('tip', h_)] * 100:.2f} cm (closed form "
                     f"{threshold(v0, h_, mu, g) * 100:.2f})")
    for u in man["description_speeds_m_s"]:
        desc[("v", u)] = d_star_run(u, h, mu)
        parts.append(f"{u:g} m/s: {desc[('v', u)] * 100:.2f} cm (closed form {threshold(u, h, mu, g) * 100:.2f})")
    print(f"for the description (the threshold d* moves with the cloth, the tip and the speed; here mu {mu:g}, tip "
          f"{h:g} R, {v0:g} m/s: {xz * 100:.2f} cm): " + "; ".join(parts)
          + "; d* grows as 1 / mu and as v0^2 and with the tip's depth h (2 - h)")
    # The stepped check.
    chk = []
    for dt in man["stepped_dts"]:
        row = []
        for p in PANELS:
            st = stepped(man, dist[p], dt, 1.25)
            th_, xh_, vh_, rw_ = st["hit"]
            after = [ev for ev in st["rolls"]["cue"] if ev[0] > th_]
            v_after = after[0][2]
            row.append(f"{p}: hit at {th_:.6f} s ({th_ - res[p]['t_hit']:+.1e}), {vh_:.6f} m/s ({vh_ - res[p]['v_hit']:+.1e}), "
                       f"R omega {rw_:+.6f} ({rw_ - res[p]['Rw_hit']:+.1e}), the cue ball ends at {v_after:+.6f} m/s "
                       f"({v_after - res[p]['v_fin']:+.1e})")
            if p == "far":
                tg, xg, vg = st["gone"]
                row.append(f"backspin gone at {tg:.6f} s ({tg - tz:+.1e}) after {xg * 100:.4f} cm ({(xg - xz) * 100:+.1e} cm)")
        chk.append(f"dt {dt:g} s: " + ", ".join(row))
    print("stepped check (semi-implicit Euler, the slip snapped to rolling on its closing step; differences from the "
          "exact pieces in brackets): " + "; ".join(chk))
    # Schedule in video time.
    c0 = man["first_cycle_at"]
    k0 = math.floor((0.0 - c0) / P)
    k1 = math.floor((D - c0) / P)
    starts = [c0 + k * P for k in range(k0, k1 + 1)]
    strikes = [s + sa for s in starts if 0.0 <= s + sa < D]
    x_left = -(x0_px / ppm) - R
    x_right = (W - x0_px) / ppm + R
    t_back_start = cross_time(shots["near"], "cue", 0.0, n_["t_settle"], shots["near"]["t_end"], below=True)
    t_leave = cross_time(shots["near"], "cue", x_left, n_["t_settle"], shots["near"]["t_end"], below=True)
    exit_obj = {p: cross_time(shots[p], "obj", x_right, res[p]["t_hit"], shots[p]["t_end"], below=False) for p in PANELS}
    x_far_end = state_at(shots["far"], "cue", (P - F - sa) / slow)[0]

    def lst(dr: float) -> str:
        return ", ".join(f"{s + dr * slow:.2f}" for s in strikes)
    print(f"schedule (video time, 1/{slow:g} speed): cycles of {P:g} s start at " + ", ".join(f"{s:.2f}" for s in starts)
          + f" s; the strike {sa:g} s into each cycle at {lst(0.0)} s; near: the hit {n_['t_hit'] * slow:.2f} s after the "
          f"strike at {lst(n_['t_hit'])} s, the cue ball rolls back from {lst(n_['t_settle'])} s, is back over its start at "
          f"{lst(t_back_start)} s and leaves the panel on the left at {lst(t_leave)} s ({t_leave:.4f} s real); far: the "
          f"backspin is gone at the gold line {tz * slow:.2f} s after the strike at {lst(tz)} s, the ball rolls from "
          f"{lst(rl[0])} s, the hit at {lst(f_['t_hit'])} s, the cue ball follows at its final speed from "
          f"{lst(f_['t_settle'])} s and has crept {(x_far_end - f_['x_hit']) * 100:.1f} cm past the hit point when the "
          f"reset starts; the other balls leave the panel on the right {exit_obj['near'] * slow:.2f} s (near) and "
          f"{exit_obj['far'] * slow:.2f} s (far) after the strike; the stick (drawn only) waits {man['stick_ready_m'] * 100:g} "
          f"cm behind the ball, strokes in at {man['stick_speed_m_s']:g} m/s from {man['stick_ready_m'] / man['stick_speed_m_s'] * slow:.2f} s "
          f"before the strike, follows through {man['stick_follow_m'] * 100:g} cm and fades after it; the reset crossfades over the last {F:g} s of each cycle (out "
          f"{P - F:.2f} to {P - F / 2:.2f} s, in {P - F / 2:.2f} to {P:.2f} s after the cycle start); the first frame is "
          f"{0.0 - c0:.2f} s into a cycle ({(0.0 - c0 - sa) / slow:+.4f} s real from the strike); title until {man['title_until']:g} "
          f"s; payoff card from {man['payoff_t']:g} s; the title fades back in over the last {man['loop_fade']:g} s and "
          f"the last frame repeats the first (the scene holds exactly {cycles_n:.0f} cycles)")
    ev = {"ug": ug, "alpha": alpha, "Rw0": Rw0, "w0": w0, "shots": shots, "res": res, "d_star": xz, "t_star": tz,
          "t_rollout": rl[0], "v_rollout": rl[3]["v"], "desc": desc, "cycles_n": int(round(cycles_n)),
          "t_leave": t_leave}
    # Text widths.
    font = os.environ["SEED_ZERO_FONT"]
    f28, f34, f40, f56 = (ImageFont.truetype(font, n) for n in (28, 34, 40, 56))
    widths = {"overlay@34": (f34, man["overlay"])}
    for j, line in enumerate(man["title"].split("|")):
        widths[f"title line {j + 1}@56"] = (f56, line)
    widths["legend@40"] = (f40, legend_text(man))
    widths["clock@28"] = (f28, clock_text(1.875))
    widths["clock before@28"] = (f28, clock_text(-0.1))
    for p in PANELS:
        widths[f"label {p}@40"] = (f40, PANELS[p]["label"])
        widths[f"sub {p}@28"] = (f28, sub_text(dist[p]))
        widths[f"bracket {p}@28"] = (f28, bracket_text(dist[p]))
    for s in STATES:
        widths[f"state {s}@28"] = (f28, s)
    widths["readout before@40"] = (f40, readout_text("before", v0))
    widths["readout near@40"] = (f40, readout_text("back", n_["v_fin"]))
    widths["readout far@40"] = (f40, readout_text("follows", f_["v_fin"]))
    widths["line label@28"] = (f28, "backspin gone here")
    widths["line mark@28"] = (f28, line_mark_text(xz))
    for j, line in enumerate(payoff_lines(man, ev)):
        widths[f"payoff line {j + 1}@40"] = (f40, line)
    print("text widths: " + ", ".join(f"{k} {f.getlength(s):.0f} px" for k, (f, s) in widths.items()))
    assert all(f.getlength(s) < 950 for f, s in widths.values()), "a text line is wider than 950 px"
    # Row check: the label plus the widest state word, and the sub line, against the readout.
    left = ROW_X0 + max(f40.getlength(PANELS[p]["label"]) for p in PANELS) + STATE_GAP + max(f28.getlength(s) for s in STATES)
    left_sub = ROW_X0 + max(f28.getlength(sub_text(dist[p])) for p in PANELS)
    right = ROW_X1 - max(f40.getlength(readout_text(k, v)) for k, v in
                         (("before", v0), ("back", n_["v_fin"]), ("follows", f_["v_fin"])))
    print(f"row check: the label and state end at x {left:.0f} px, the sub line at x {left_sub:.0f} px, the readout "
          f"starts at x {right:.0f} px")
    assert left < right - 30, "the label row collides with the readout"
    # Body labels: the bracket label and the d* mark must not overlap.
    xl = x0_px + xz * ppm
    wm = f28.getlength(line_mark_text(xz))
    for p in PANELS:
        xb = x0_px + dist[p] / 2.0 * ppm
        wb = f28.getlength(bracket_text(dist[p]))
        gap = (xl + MARK_DX) - (xb + wb / 2.0)
        print(f"body labels {p}: the bracket label spans x {xb - wb / 2:.0f} to {xb + wb / 2:.0f} px, the d* mark "
              f"{xl + MARK_DX:.0f} to {xl + MARK_DX + wm:.0f} px (right of the gold line), gap {gap:.0f} px")
        assert gap > 30, "the body labels overlap"
    x_obj_far = x0_px + (dist["far"] + 2 * R) * ppm
    print(f"frame check: the start at x {x0_px} px, the gold line at x {xl:.0f} px, the far other ball at x "
          f"{x_obj_far:.0f} px (right edge {x_obj_far + R * ppm:.0f} px of {W}); the stick's tip at the strike at x "
          f"{x0_px - math.sqrt(1 - h * h) * R * ppm:.0f} px")
    assert x_obj_far + R * ppm < W - 20
    return ev


def legend_text(man: dict) -> str:
    return f"the same low hit on both, 1/{man['slow']:g} speed"


def clock_text(r: float) -> str:
    return "before the strike" if r < 0.0 else f"{r:.3f} s after the strike"


def sub_text(dist: float) -> str:
    return f"other ball {dist_text(dist)} away"


def dist_text(dist: float) -> str:
    return f"{dist * 100:.0f} cm" if dist < 1.0 else f"{dist:g} m"


def bracket_text(dist: float) -> str:
    return dist_text(dist)


def line_mark_text(d_star: float) -> str:
    return f"{d_star * 100:.1f} cm"


def readout_text(kind: str, v: float) -> str:
    if kind == "before":
        return f"cue ball {abs(v):.2f} m/s"
    if kind == "back":
        return f"comes back {abs(v):.2f} m/s"
    return f"follows {abs(v):.2f} m/s"


def payoff_lines(man: dict, ev: dict) -> list[str]:
    d = ev["desc"]
    mu_lo, mu_hi = man["description_mus"]
    tip_lo = man["description_tips_R"][0]
    text = man["payoff_text"].format(
        d_star_cm=ev["d_star"] * 100, v_back=-ev["res"]["near"]["v_fin"], spin_left=-ev["res"]["near"]["Rw_hit"],
        v_follow=ev["res"]["far"]["v_fin"], v_roll=ev["res"]["far"]["v_hit"], mu=man["mu"], mu_lo=mu_lo,
        d_mu_lo=d[("mu", mu_lo)] * 100, mu_hi=mu_hi, d_mu_hi=d[("mu", mu_hi)] * 100, tip_lo=tip_lo,
        d_tip_lo=d[("tip", tip_lo)] * 100, tip=man["tip_offset_R"])
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
        self.x0 = float(man["start_x_px"])
        self.R = man["ball_radius_m"]
        self.h = man["tip_offset_R"]
        self.S = man["slow"]
        self.P = man["cycle_s"]
        self.P_f = int(round(man["cycle_s"] * self.fps))
        self.c0_f = int(round(man["first_cycle_at"] * self.fps))
        self.sa, self.F = man["strike_at"], man["reset_fade"]
        self.shots, self.res = ev["shots"], ev["res"]
        self.dist = {p: man[PANELS[p]["dist_key"]] for p in PANELS}
        self.x_contact = -math.sqrt(1.0 - self.h * self.h) * self.R
        vs, fol = man["stick_speed_m_s"], man["stick_follow_m"]
        self.vs, self.fol, self.t_fol, self.ready = vs, fol, 2.0 * fol / 1.0, man["stick_ready_m"]

    # --- state helpers ------------------------------------------------------
    def phase(self, f: int) -> tuple[int, float]:
        k, tau_f = divmod(f - self.c0_f, self.P_f)
        return k, tau_f / self.fps

    # --- pixel helpers ------------------------------------------------------
    def Lp(self, x: float, y: float) -> tuple[float, float]:
        """Layer (2x) pixel of a screen point, rounded to 1e-4 px so equal states draw equal pixels."""
        return round(x * SS, 4), round((y - GEOM_Y0) * SS, 4)

    def X(self, x_m: float) -> float:
        return self.x0 + x_m * self.ppm

    def dashed_v(self, d: ImageDraw.ImageDraw, x: float, y0: float, y1: float, col, dash: float, gap: float, width: int) -> None:
        s = y0
        while s > y1:
            e = max(y1, s - dash)
            a, b = self.Lp(x, s), self.Lp(x, e)
            d.line((*a, *b), fill=col, width=width)
            s = e - gap

    def draw_table(self, d: ImageDraw.ImageDraw, p: str) -> None:
        cy = PANELS[p]["cloth_y"]
        a, b = self.Lp(0, cy), self.Lp(W, cy + BODY_PX)
        d.rectangle((a[0], a[1], b[0], b[1]), fill=DECK_A)
        a, b = self.Lp(0, cy - 2), self.Lp(W, cy + 3)
        d.rectangle((a[0], a[1], b[0], b[1]), fill=CLOTH)
        # The distance bracket: from the cue ball's start to where its centre is when the balls touch.
        xa, xb = self.X(0.0), self.X(self.dist[p])
        yb = cy + BRACKET_DY
        col = blend(MUTED, 0.9, DECK_A)
        d.line((*self.Lp(xa, yb), *self.Lp(xb, yb)), fill=col, width=2 * SS)
        for xe in (xa, xb):
            d.line((*self.Lp(xe, yb - 7), *self.Lp(xe, yb + 7)), fill=col, width=2 * SS)
        # The gold line where the backspin is gone, over the cloth and through the body.
        xl = self.X(self.ev["d_star"])
        self.dashed_v(d, xl, cy - 3, cy - LINE_TOP_DY, blend(GOLD, 0.85), 12, 8, 3 * SS)
        d.line((*self.Lp(xl, cy + 3), *self.Lp(xl, cy + 30)), fill=blend(GOLD, 0.85, DECK_A), width=3 * SS)

    def draw_stick(self, d: ImageDraw.ImageDraw, cy: float, x_tip: float, a: float) -> None:
        if a <= 0.01:
            return
        ay = cy - self.R * self.ppm + self.h * self.R * self.ppm      # the stick's axis: level, h R below the centre
        X_tip = self.X(x_tip)
        X_end = -20.0
        r_tip, slope = 0.0065 * self.ppm, 0.008                        # a 13 mm tip, the stick widening to the left

        def r_at(X: float) -> float:
            return r_tip + slope * (X_tip - X)

        segs = ((X_tip, X_tip - 0.004 * self.ppm, CHALK), (X_tip - 0.004 * self.ppm, X_tip - 0.018 * self.ppm, WHITE),
                (X_tip - 0.018 * self.ppm, X_end, WOOD))
        for xa, xb, col in segs:
            if xa <= X_end:
                continue
            xb = max(xb, X_end)
            poly = [self.Lp(xa, ay - r_at(xa)), self.Lp(xb, ay - r_at(xb)), self.Lp(xb, ay + r_at(xb)),
                    self.Lp(xa, ay + r_at(xa))]
            d.polygon(poly, fill=blend(col, a))
        # A darker lower edge so the stick reads as round.
        xa = max(X_tip - 0.018 * self.ppm, X_end)
        if xa > X_end:
            d.line((*self.Lp(xa, ay + 0.55 * r_at(xa)), *self.Lp(X_end, ay + 0.55 * r_at(X_end))),
                   fill=blend(WOOD_DARK, a), width=2 * SS)

    def ball(self, d: ImageDraw.ImageDraw, X: float, Y: float, th: float, a: float, cue: bool) -> None:
        rr = self.R * self.ppm * SS
        cx, cy = self.Lp(X, Y)
        if cue:
            d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), fill=blend(WHITE, a), outline=blend(RIM, a), width=2 * SS)
            # A great-circle stripe through the spin axis: a band across the ball that turns with it,
            # with a dark dot on one end (on top at rest) to show the full turn.
            q = th - math.pi / 2.0
            da = math.asin(0.3)
            pts = [(cx + rr * math.cos(v), cy + rr * math.sin(v)) for v in (q - da, q + da, q + math.pi - da, q + math.pi + da)]
            d.polygon(pts, fill=blend(CORAL, a))
            dx, dy = cx + 0.62 * rr * math.cos(q), cy + 0.62 * rr * math.sin(q)
            rd = 0.17 * rr
            d.ellipse((dx - rd, dy - rd, dx + rd, dy + rd), fill=blend((110, 36, 30), a))
        else:
            d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), fill=blend(GOLD, a), outline=blend((120, 84, 30), a), width=2 * SS)
            dx, dy = cx + 0.62 * rr * math.cos(th - math.pi / 2), cy + 0.62 * rr * math.sin(th - math.pi / 2)
            rd = 0.15 * rr
            d.ellipse((dx - rd, dy - rd, dx + rd, dy + rd), fill=blend((120, 84, 30), a))

    def spin_arrow(self, d: ImageDraw.ImageDraw, X: float, Y: float, Rw: float, a: float) -> None:
        """A curved arrow over the ball: its length follows the spin, it points the way the top turns;
        coral for backspin (against the travel of a ball going right), teal for forward spin."""
        frac = min(1.0, abs(Rw) / self.ev["Rw0"])
        span = 150.0 * frac
        if span < 8.0 or a <= 0.01:
            return
        col = blend(CORAL if Rw < 0 else TEAL, a)
        cx, cy = self.Lp(X, Y)
        ra = (self.R * self.ppm + 15) * SS
        d.arc((cx - ra, cy - ra, cx + ra, cy + ra), -90.0 - span / 2.0, -90.0 + span / 2.0, fill=col, width=5 * SS)
        # The head at the leading end: clockwise (forward spin) or counterclockwise (backspin) on screen.
        if Rw > 0:
            ph = math.radians(-90.0 + span / 2.0)
            tx, ty = -math.sin(ph), math.cos(ph)
        else:
            ph = math.radians(-90.0 - span / 2.0)
            tx, ty = math.sin(ph), -math.cos(ph)
        hx, hy = cx + ra * math.cos(ph), cy + ra * math.sin(ph)
        L, Wd = 16 * SS, 10 * SS
        nx, ny = -ty, tx
        pts = [(hx + tx * L, hy + ty * L), (hx + nx * Wd, hy + ny * Wd), (hx - nx * Wd, hy - ny * Wd)]
        d.polygon(pts, fill=col)

    def stick_tip(self, r: float) -> tuple[float, float]:
        """The stick's tip (metres from the cue ball's start) and its own fade: it waits stick_ready
        behind the ball, strokes in at stick_speed, touches the ball at the strike, follows through
        stick_follow and fades."""
        if r <= 0.0:
            return self.x_contact + max(self.vs * r, -self.ready), 1.0
        u = min(1.0, r / self.t_fol)
        x = self.x_contact + self.fol * (1.0 - (1.0 - u) ** 2)
        return x, max(0.0, min(1.0, 1.0 - (r - 0.10) / 0.15))

    def draw_scene(self, d: ImageDraw.ImageDraw, p: str, tau: float, a: float) -> dict:
        """The moving parts of one panel tau seconds of video into a cycle, blended by a."""
        r = (tau - self.sa) / self.S
        shot, res = self.shots[p], self.res[p]
        cy = PANELS[p]["cloth_y"]
        rr = self.R * self.ppm
        cx, cv, cw, cth = state_at(shot, "cue", r)
        ox, ov, ow, oth = state_at(shot, "obj", r)
        hit = r >= res["t_hit"]
        settled = r >= res["t_settle"]
        if hit:
            # The hit point: a tick on the cloth, and the cue ball's travel since the hit in gold.
            hx = self.X(res["x_hit"])
            d.line((*self.Lp(hx, cy + 3), *self.Lp(hx, cy + 18)), fill=blend(WHITE, 0.8 * a, DECK_A), width=2 * SS)
            X = min(max(self.X(cx), -10.0), W + 10.0)
            if abs(X - hx) > 2.0:
                d.line((*self.Lp(hx, cy + TRAIL_DY), *self.Lp(X, cy + TRAIL_DY)), fill=blend(GOLD, 0.95 * a, DECK_A),
                       width=4 * SS)
        x_tip, a_stick = self.stick_tip(r)
        self.draw_stick(d, cy, x_tip, a * a_stick)
        oX = self.X(ox)
        if oX < W + rr + 4:
            self.ball(d, oX, cy - rr, oth, a, cue=False)
        cX = self.X(cx)
        if cX > -rr - 4:
            self.ball(d, cX, cy - rr, cth, a, cue=True)
            self.spin_arrow(d, cX, cy - rr, self.R * cw, a)
        if hit:
            u = (r - res["t_hit"]) * self.S / 0.35
            if 0.0 <= u < 1.0:
                px, py = self.Lp(self.X(res["x_hit"]) + rr, cy - rr)
                ring = (10 + 40 * u) * SS
                d.ellipse((px - ring, py - ring, px + ring, py + ring), outline=blend(WHITE, (1 - u) * a), width=3 * SS)
        slipping = abs(cv - self.R * cw) > 1e-9
        if r < 0.0:
            state = "at rest"
        elif slipping:
            state = "backspin" if cw < -1e-9 else ("topspin" if cw > 1e-9 else "no spin")
        else:
            state = "rolling back" if cv < 0.0 else "rolling"
        if not hit:
            readout = readout_text("before", cv)
        else:
            readout = readout_text("back" if res["v_fin"] < 0 else "follows", cv)
        return {"r": r, "hit": hit, "settled": settled, "alpha": a, "state": state, "readout": readout, "spin": cw}

    def draw_panel(self, d: ImageDraw.ImageDraw, p: str, f: int) -> dict:
        self.draw_table(d, p)
        k, tau = self.phase(f)
        F, P = self.F, self.P
        a_old = 1.0 if tau <= P - F else max(0.0, (P - F / 2.0 - tau) / (F / 2.0))
        st = self.draw_scene(d, p, tau, a_old) if a_old > 0.0 else None
        if tau >= P - F / 2.0:
            # The new shot is fully in one frame before the cycle ends, so the frame before the seam
            # already equals the first frame of the next cycle.
            a_new = min(1.0, (tau - (P - F / 2.0)) / (F / 2.0 - 1.0 / self.fps))
            st_new = self.draw_scene(d, p, tau - P, a_new)
            if st is None or a_new >= 0.5:
                st = st_new
        st["k"] = k
        return st

    def draw_text(self, d: ImageDraw.ImageDraw, states: dict, hud_alpha: float) -> None:
        man, ev = self.man, self.ev
        xl = self.X(ev["d_star"])
        for p, st in states.items():
            row, cy = PANELS[p]["row_y"], PANELS[p]["cloth_y"]
            a = st["alpha"]
            label = PANELS[p]["label"]
            d.text((ROW_X0, row), label, font=self.font, fill=TEXT, anchor="lm")
            scol = CORAL if st["spin"] < -1e-9 else (TEAL if st["spin"] > 1e-9 else MUTED)   # the arrow's colours
            d.text((ROW_X0 + self.font.getlength(label) + STATE_GAP, row + 2), st["state"], font=self.font_small,
                   fill=blend(scol, a), anchor="lm")
            d.text((ROW_X0, row + SUB_DY), sub_text(self.dist[p]), font=self.font_small, fill=MUTED, anchor="lm")
            d.text((ROW_X1, row), st["readout"], font=self.font,
                   fill=blend(GOLD if st["settled"] else TEXT, a), anchor="rm")
            d.text((xl, cy - LINE_LABEL_DY), "backspin gone here", font=self.font_small, fill=GOLD, anchor="mm")
            d.text((xl + MARK_DX, cy + BODY_LABEL_DY), line_mark_text(ev["d_star"]), font=self.font_small, fill=GOLD,
                   anchor="lm")
            d.text((self.X(self.dist[p] / 2.0), cy + BODY_LABEL_DY), bracket_text(self.dist[p]), font=self.font_small,
                   fill=TEXT, anchor="mm")
        if hud_alpha > 0.02:
            d.text((W / 2, LEGEND_Y), legend_text(man), font=self.font, fill=blend(TEXT, hud_alpha), anchor="mm")
            d.text((W / 2, CLOCK_Y), clock_text(states["far"]["r"]), font=self.font_small,
                   fill=blend(MUTED, hud_alpha), anchor="mm")

    def live_frame(self, f: int, title_alpha: float | None = None, hud_alpha: float = 0.0) -> np.ndarray:
        """Frame f; title_alpha and hud_alpha override the title and the legend/clock/card blend
        during the loop fade."""
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
        states = {p: self.draw_panel(ld, p, f) for p in PANELS}
        img.paste(layer.reduce(SS), (0, GEOM_Y0))
        d = ImageDraw.Draw(img)
        self.draw_text(d, states, hud_alpha)
        if title_alpha > 0.0:
            for j, line in enumerate(man["title"].split("|")):
                d.text((W / 2, TITLE_Y0 + j * TITLE_PITCH), line, font=self.font_title, fill=blend(TEXT, title_alpha),
                       anchor="mm")
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
    man = json.loads((ROOT / "projects/drawshot/manifest.json").read_text())
    ev = measure(man)
    if "--measure-only" in sys.argv:
        return
    if "--frames" in sys.argv:
        times = [float(v) for v in sys.argv[sys.argv.index("--frames") + 1].split(",")]
        r = Renderer(man, ev)
        (ROOT / "media/drawshot").mkdir(parents=True, exist_ok=True)
        for tv in times:
            Image.fromarray(r.frame_at(int(round(tv * man["fps"])))).save(ROOT / f"media/drawshot/smoke-{tv}.png")
        print("smoke frames: " + ", ".join(f"{tv}" for tv in times))
        return
    Renderer(man, ev).render(ROOT / "media/drawshot/footage.mp4")


if __name__ == "__main__":
    main()
