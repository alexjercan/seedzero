#!/usr/bin/env python3
"""Cue ball follow: does the cue ball stop?

Two cue balls hit a ball at rest dead on at the same speed v0, drawn from
the side one above the other. The top cue ball arrives sliding with no spin
(a stun shot: it is struck with the little backspin that the cloth wears off
exactly at the hit); the bottom cue ball arrives rolling (spin v0 / R). The
balls have equal mass and the hit is head on, elastic and frictionless
between the balls, so the hit swaps the balls' forward speeds and leaves each
ball's spin as it was. The cloth acts on any slipping contact with sliding
friction mu (a solid sphere, I = 2/5 m R^2): the slip v - R omega closes at
7/2 mu g, a ball with no slip rolls on at constant speed (no rolling
resistance). So the top cue ball hands its v0 to the struck ball and stays
put; the bottom cue ball hands over its v0, is left at rest but spinning,
and the cloth drags it forward again until it rolls at 2 v0 / 7 after
v0 / (7/2 mu g) seconds and 1/2 mu g t^2 of creep; the struck ball leaves
sliding at v0 with no spin and settles at 5 v0 / 7 after the same time. Both
balls of each panel are integrated as exact constant-acceleration pieces
between the events (slip closure, the hit) and compared with the closed
forms. The shot repeats every shot_period seconds of video with a crossfade
to the next launch; the period divides the scene length, so the scene is
exactly periodic and the last frame equals the first. Shown at 1/slow
speed. Deterministic, no seed.

Measured and printed: the launch states, the state of both cue balls at the
instant of the hit (against v0, spin 0 and spin v0 / R), the speeds right
after the hit, the bottom cue ball's rolling speed, time and creep distance
(against 2 v0 / 7, v0 / (7/2 mu g) and 1/2 mu g t^2), the struck ball's
settled speed, time and distance (against 5 v0 / 7 and v0 t - 1/2 mu g t^2),
the top cue ball's rest check, the fractions, the same shot on other cloths
and at other speeds for the description, the schedule in video time, the
loop and periodicity checks and the on-screen text widths.

usage: cueball.py [--measure-only] [--frames t1,t2,...]
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

# Layout: overlay at y 96..130 (captions.py), title rows at y 190/252 for
# the first seconds, then the shot counter at y 236 and the legend at y
# 290; the "no spin" row (label, state, speed readout) at y 380 over the
# top panel with its cloth at y 700; the "rolling" row at y 920 over the
# bottom panel with its cloth at y 1240; the geometry band y 400..1420
# drawn at 2x; captions at caption_y 0.75 (y 1440..1520); the payoff card
# from y 1592.
COUNTER_Y, TAG_Y = 236, 290
GEOM_Y0, GEOM_Y1 = 400, 1420
SS = 2
PAYOFF_Y = 1592.0
PANELS = {"top": {"label": "no spin", "row_y": 380, "cloth_key": "top_cloth_y"},
          "bottom": {"label": "rolling", "row_y": 920, "cloth_key": "bottom_cloth_y"}}
ROW_X0, STATE_GAP, SPEED_X = 100, 26, 980


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


def integrate(cue: dict, obj: dict, t_start: float, t_end: float, R: float, ug: float, alpha: float) -> dict:
    """Both balls of one panel from t_start (before the launch at t = 0, the launch state run
    backward with its own accelerations) to t_end as exact constant-acceleration pieces
    (t0, t1, x0, v0, a, omega0, alpha, theta0) between the events: a slip closing, the hit."""
    balls = {"cue": dict(cue), "obj": dict(obj)}
    for b in balls.values():
        a, al, _ = ball_accel(b["v"], b["w"], R, ug, alpha)
        ts = t_start
        b["th"] = b["w"] * ts + 0.5 * al * ts * ts   # the stripe angle is 0 at the launch
        b["x"] += b["v"] * ts + 0.5 * a * ts * ts
        b["v"] += a * ts
        b["w"] += al * ts
    pieces: dict[str, list] = {"cue": [], "obj": []}
    events: list = []
    t = t_start
    while t < t_end - 1e-12:
        acc = {}
        dt_next, kind = t_end - t, ("end", None)
        for name, b in balls.items():
            a, al, dt_close = ball_accel(b["v"], b["w"], R, ug, alpha)
            acc[name] = (a, al)
            if dt_close is not None and dt_close < dt_next:
                dt_next, kind = dt_close, ("roll", name)
        g0 = balls["obj"]["x"] - balls["cue"]["x"] - 2.0 * R
        r = first_root(g0, balls["obj"]["v"] - balls["cue"]["v"], acc["obj"][0] - acc["cue"][0])
        if r is not None and r < dt_next:
            dt_next, kind = r, ("hit", None)
        for name, b in balls.items():
            a, al = acc[name]
            pieces[name].append((t, t + dt_next, b["x"], b["v"], a, b["w"], al, b["th"]))
            b["th"] += b["w"] * dt_next + 0.5 * al * dt_next * dt_next
            b["x"] += b["v"] * dt_next + 0.5 * a * dt_next * dt_next
            b["v"] += a * dt_next
            b["w"] += al * dt_next
        t += dt_next
        for name, b in balls.items():
            # Every ball whose slip closes on this step (the cue ball and the struck ball close
            # theirs at the same instant): snap out the rounding and record the event.
            if acc[name][0] != 0.0 and abs(b["v"] - R * b["w"]) < 1e-7:
                b["w"] = b["v"] / R
                events.append((t, "roll", name, dict(b)))
        if kind[0] == "hit":
            before = {n: dict(b) for n, b in balls.items()}
            balls["cue"]["v"], balls["obj"]["v"] = balls["obj"]["v"], balls["cue"]["v"]
            events.append((t, "hit", None, {"before": before, "after": {n: dict(b) for n, b in balls.items()}}))
    return {"pieces": pieces, "events": events, "t_start": t_start, "t_end": t_end,
            "final": {n: dict(b) for n, b in balls.items()}}


def state_at(shot: dict, name: str, r: float) -> tuple[float, float, float, float]:
    """(x, v, omega, theta) of a ball at real time r, clamped to the shot's span."""
    ps = shot["pieces"][name]
    r = min(max(r, ps[0][0]), ps[-1][1])
    for t0, t1, x0, v0, a, w0, al, th0 in ps:
        if r < t1:
            break                   # on a boundary the later piece wins: the state after the event
    dt = r - t0
    return (x0 + v0 * dt + 0.5 * a * dt * dt, v0 + a * dt, w0 + al * dt, th0 + w0 * dt + 0.5 * al * dt * dt)


def event(shot: dict, kind: str, name=None):
    for ev in shot["events"]:
        if ev[1] == kind and ev[2] == name:
            return ev
    return None


def measure(man: dict) -> dict:
    R, mu, g, v0 = man["ball_radius_m"], man["mu"], man["g"], man["hit_speed_m_s"]
    ug = mu * g
    alpha = 5.0 * ug / (2.0 * R)
    slow, P, D, fps = man["slow"], man["shot_period"], man["scene_duration"], man["fps"]
    F = man["reset_fade"]
    ppm = man["px_per_m"]
    shots_n = D / P
    assert abs(shots_n - round(shots_n)) < 1e-9, "the shot period must divide the scene length"
    x_obj = man["object_x_m"]
    x_hit = x_obj - 2.0 * R
    d_b = man["object_ahead_m"] - 2.0 * R
    t_run = d_b / v0
    panel_m = W / ppm
    print(f"setup: two cue balls hit a ball at rest dead on at v0 = {v0:g} m/s, drawn from the side one above the "
          f"other (ball radius {R * 1000:g} mm, a {2 * R * 1000:g} mm ball, equal masses, a solid sphere I = 2/5 m "
          f"R^2, cloth sliding friction mu = {mu:g} on any slipping contact, g = {g:g} m/s^2, no rolling "
          f"resistance, no friction between the balls, an elastic head-on hit that swaps the balls' forward speeds "
          f"and keeps each ball's spin); the top cue ball arrives sliding with no spin (a stun shot: struck with the "
          f"backspin that the cloth wears off exactly at the hit), the bottom cue ball arrives rolling (spin v0 / R "
          f"= {v0 / R:.2f} rad/s); the struck ball rests {man['object_ahead_m'] * 100:g} cm ahead of the rolling cue "
          f"ball (centre to centre) at x = {x_obj:g} m of the {panel_m:.2f} m panel; each panel integrated as exact "
          f"constant-acceleration pieces between the events (slip closure, the hit); shown at 1/{slow:g} speed, one "
          f"shot every {P:g} s of video, {shots_n:.0f} shots in {D:g} s; drawn at {ppm:g} px per metre (ball radius "
          f"{R * ppm:.1f} px); deterministic, no seed")
    # Launch states: the rolling ball rolls at v0 over d_b; the no-spin ball is run backward from the hit
    # over the same time with the cloth's friction on (slip positive: the speed falls, the spin rises).
    v_l = v0 + ug * t_run
    w_l = -alpha * t_run
    d_t = v_l * t_run - 0.5 * ug * t_run * t_run
    launches = {"top": {"x": x_hit - d_t, "v": v_l, "w": w_l},
                "bottom": {"x": x_hit - d_b, "v": v0, "w": v0 / R}}
    obj0 = {"x": x_obj, "v": 0.0, "w": 0.0}
    t_start, t_end = -(F / 2.0) / slow, P / slow
    shots = {p: integrate(launches[p], obj0, t_start, t_end, R, ug, alpha) for p in PANELS}
    print(f"launch (t = 0 of each shot, real time): the rolling cue ball leaves x = {launches['bottom']['x']:.4f} m "
          f"at {v0:.4f} m/s rolling (spin {v0 / R:.3f} rad/s) and reaches the ball after {t_run:.4f} s ({d_b:.4f} "
          f"m); the no-spin cue ball leaves x = {launches['top']['x']:.4f} m, {(x_obj - launches['top']['x']) * 100:.2f} "
          f"cm behind the ball (centre to centre), at {v_l:.4f} m/s with {-w_l:.3f} rad/s of backspin (R omega = "
          f"{R * w_l:.4f} m/s), so that the cloth (mu g = {ug:.4f} m/s^2 on the speed, 5 mu g / 2 R = {alpha:.2f} "
          f"rad/s^2 on the spin) wears the backspin off exactly at the hit")
    hits = {p: event(shots[p], "hit") for p in PANELS}
    hb = {p: hits[p][3]["before"] for p in PANELS}
    ha = {p: hits[p][3]["after"] for p in PANELS}
    t_hit = {p: hits[p][0] for p in PANELS}
    print(f"hit: at {t_hit['top']:.4f} s (top) and {t_hit['bottom']:.4f} s (bottom) of real time (target {t_run:.4f} "
          f"s, diff {abs(t_hit['top'] - t_run):.1e} and {abs(t_hit['bottom'] - t_run):.1e}) the cue balls touch the "
          f"ball at x = {hb['top']['cue']['x']:.4f} m ({x_hit:.4f}); top cue ball {hb['top']['cue']['v']:.4f} m/s, "
          f"spin {hb['top']['cue']['w']:.4f} rad/s (target {v0:.4f} and 0, diffs {abs(hb['top']['cue']['v'] - v0):.1e} "
          f"and {abs(hb['top']['cue']['w']):.1e}); bottom cue ball {hb['bottom']['cue']['v']:.4f} m/s, spin "
          f"{hb['bottom']['cue']['w']:.3f} rad/s (v0 / R = {v0 / R:.3f}, diff {abs(hb['bottom']['cue']['w'] - v0 / R):.1e}); "
          f"right after: top cue ball {ha['top']['cue']['v']:.4f} m/s spin {ha['top']['cue']['w']:.4f}, bottom cue "
          f"ball {ha['bottom']['cue']['v']:.4f} m/s spin {ha['bottom']['cue']['w']:.3f}, the struck ball "
          f"{ha['top']['obj']['v']:.4f} and {ha['bottom']['obj']['v']:.4f} m/s with spin {ha['top']['obj']['w']:.1f}; "
          f"momentum before and after the hit {hb['bottom']['cue']['v'] + hb['bottom']['obj']['v']:.4f} = "
          f"{ha['bottom']['cue']['v'] + ha['bottom']['obj']['v']:.4f}, translational energy "
          f"{0.5 * (hb['bottom']['cue']['v'] ** 2 + hb['bottom']['obj']['v'] ** 2):.4f} = "
          f"{0.5 * (ha['bottom']['cue']['v'] ** 2 + ha['bottom']['obj']['v'] ** 2):.4f} per unit mass")
    # The follow: the bottom cue ball rolls again.
    t_roll_c = v0 / (3.5 * ug)
    v_roll_c = 2.0 * v0 / 7.0
    d_roll_c = 0.5 * ug * t_roll_c * t_roll_c
    rc = event(shots["bottom"], "roll", "cue")
    t_c, s_c = rc[0] - t_hit["bottom"], rc[3]
    d_c = s_c["x"] - hb["bottom"]["cue"]["x"]
    print(f"follow: the bottom cue ball, at rest but spinning, is dragged forward by the cloth and rolls again at "
          f"{s_c['v']:.4f} m/s after {t_c:.4f} s and {d_c:.4f} m of creep (closed forms 2 v0 / 7 = {v_roll_c:.4f} m/s, "
          f"v0 / (7/2 mu g) = {t_roll_c:.4f} s, 1/2 mu g t^2 = {d_roll_c:.4f} m; diffs {abs(s_c['v'] - v_roll_c):.1e}, "
          f"{abs(t_c - t_roll_c):.1e}, {abs(d_c - d_roll_c):.1e}); that is {s_c['v'] / v0:.5f} of its arrival speed "
          f"(2/7 = {2 / 7:.5f}, diff {abs(s_c['v'] / v0 - 2 / 7):.1e}); its spin falls from {ha['bottom']['cue']['w']:.3f} "
          f"to {s_c['w']:.3f} rad/s (v / R = {s_c['v'] / R:.3f}); after that it rolls on at {s_c['v']:.4f} m/s "
          f"({shots['bottom']['final']['cue']['v']:.4f} m/s at the end of the shot)")
    # The struck ball.
    v_roll_o = 5.0 * v0 / 7.0
    d_roll_o = v0 * t_roll_c - 0.5 * ug * t_roll_c * t_roll_c
    ro = {p: event(shots[p], "roll", "obj") for p in PANELS}
    t_o = {p: ro[p][0] - t_hit[p] for p in PANELS}
    d_o = {p: ro[p][3]["x"] - x_obj for p in PANELS}
    x_exit = panel_m + R
    exit_t = {}
    for p in PANELS:
        lo, hi = t_hit[p], t_end
        for _ in range(80):
            mid = 0.5 * (lo + hi)
            if state_at(shots[p], "obj", mid)[0] >= x_exit:
                hi = mid
            else:
                lo = mid
        exit_t[p] = hi - t_hit[p]
    print(f"struck ball: leaves sliding at {ha['top']['obj']['v']:.4f} m/s with no spin and rolls at "
          f"{ro['top'][3]['v']:.4f} (top) and {ro['bottom'][3]['v']:.4f} m/s (bottom) after {t_o['top']:.4f} and "
          f"{t_o['bottom']:.4f} s and {d_o['top']:.4f} and {d_o['bottom']:.4f} m (closed forms 5 v0 / 7 = "
          f"{v_roll_o:.4f} m/s, {t_roll_c:.4f} s, v0 t - 1/2 mu g t^2 = {d_roll_o:.4f} m; diffs "
          f"{abs(ro['bottom'][3]['v'] - v_roll_o):.1e}, {abs(t_o['bottom'] - t_roll_c):.1e}, {abs(d_o['bottom'] - d_roll_o):.1e}); "
          f"that is {ro['bottom'][3]['v'] / v0:.5f} of the arrival speed (5/7 = {5 / 7:.5f}); it settles at x = "
          f"{ro['bottom'][3]['x']:.4f} m, inside the panel, and leaves the panel (x > {x_exit:.4f} m) "
          f"{exit_t['bottom']:.4f} s after the hit ({exit_t['bottom'] * slow:.2f} s of video)")
    # The stop: the top cue ball at rest.
    xs = [state_at(shots["top"], "cue", t_hit["top"] + k * 0.01)[:3] for k in range(int((t_end - t_hit["top"]) / 0.01) + 1)]
    max_dx = max(abs(x - hb["top"]["cue"]["x"]) for x, _, _ in xs)
    max_v = max(abs(v) for _, v, _ in xs)
    max_w = max(abs(w) for _, _, w in xs)
    print(f"stop: the top cue ball stays at x = {hb['top']['cue']['x']:.4f} m from the hit to the end of the shot "
          f"({t_end - t_hit['top']:.4f} s, {(t_end - t_hit['top']) * slow:.2f} s of video): max |x - x_hit| = {max_dx:.1e} m, "
          f"max |v| = {max_v:.1e} m/s, max |spin| = {max_w:.1e} rad/s (no slip, so the cloth has nothing to act on)")
    print("for the description (same shot, other cloths): " + "; ".join(
        f"mu {m:g}: the cue ball rolls again at {2 * v0 / 7:.4f} m/s after {v0 / (3.5 * m * g):.4f} s and "
        f"{0.5 * m * g * (v0 / (3.5 * m * g)) ** 2 * 100:.1f} cm, the struck ball at {5 * v0 / 7:.4f} m/s after "
        f"{(v0 * v0 / (3.5 * m * g) - 0.5 * m * g * (v0 / (3.5 * m * g)) ** 2) * 100:.1f} cm" for m in man["description_mus"]))
    print("for the description (same cloth, other speeds): " + "; ".join(
        f"{u:g} m/s: {2 * u / 7:.4f} and {5 * u / 7:.4f} m/s after {u / (3.5 * ug):.4f} s, creep "
        f"{0.5 * ug * (u / (3.5 * ug)) ** 2 * 100:.1f} cm" for u in man["description_speeds_m_s"]))
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
          + f" s; the bottom cue ball rolls again {t_roll_c * slow:.2f} s after the hit ({(hit_v + t_roll_c * slow):.2f} s "
          f"after the launch), at " + ", ".join(f"{th + t_roll_c * slow:.2f}" for th in hits_v)
          + f" s; the struck ball settles at the same instants and leaves the panel {exit_t['bottom'] * slow:.2f} s "
          f"after the hit; the shot crossfades to the next launch over the last {F:g} s of each {P:g} s (out over "
          f"{P - F:.2f} to {P - F / 2:.2f} s, in over {P - F / 2:.2f} to {P:.2f} s after the launch, the incoming cue "
          f"balls run in from the left); title until {man['title_until']:g} s; payoff card from {man['payoff_t']:g} "
          f"s; the title fades back in over the last {man['loop_fade']:g} s and the last frame repeats the first")
    ev = {"ug": ug, "alpha": alpha, "t_run": t_run, "x_hit": x_hit, "shots": shots, "launches": launches,
          "t_hit": t_hit["bottom"], "v_roll": s_c["v"], "t_roll": t_c, "creep": d_c, "v_obj": ro["bottom"][3]["v"],
          "d_obj": d_o["bottom"], "exit_t": exit_t["bottom"], "shots_n": int(round(shots_n)), "w_hit": v0 / R}
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
    for s in ("sliding", "at rest", "rolling", "spinning"):
        widths[f"state {s}@28"] = (f28, s)
    widths["speed@40"] = (f40, speed_text(v_l))
    widths["cue tag@28"] = (f28, "cue ball")
    for j, line in enumerate(payoff_lines(man, ev)):
        widths[f"payoff line {j + 1}@40"] = (f40, line)
    print("text widths: " + ", ".join(f"{k} {f.getlength(s):.0f} px" for k, (f, s) in widths.items()))
    assert all(f.getlength(s) < 950 for f, s in widths.values()), "a text line is wider than 950 px"
    row_w = max(f40.getlength(PANELS[p]["label"]) for p in PANELS) + STATE_GAP + max(
        f28.getlength(s) for s in ("sliding", "at rest", "rolling", "spinning"))
    print(f"row check: label plus state end at x {ROW_X0 + row_w:.0f} px at most, the speed readout starts at x "
          f"{SPEED_X - f40.getlength(speed_text(v_l)):.0f} px")
    assert ROW_X0 + row_w < SPEED_X - f40.getlength(speed_text(v_l)) - 40, "the row texts collide"
    return ev


def counter_text(ev: dict, shot: int) -> str:
    return f"shot {shot + 1} of {ev['shots_n']}"


def legend_text(man: dict) -> str:
    return f"no spin at the hit above, rolling below; 1/{man['slow']:g} speed"


def speed_text(v: float) -> str:
    return f"cue ball {v:.2f} m/s"


def payoff_lines(man: dict, ev: dict) -> list[str]:
    text = man["payoff_text"].format(v_roll=ev["v_roll"], v0=man["hit_speed_m_s"], creep_cm=ev["creep"] * 100,
                                     t_roll=ev["t_roll"], v_obj=ev["v_obj"])
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
        self.R = man["ball_radius_m"]
        self.slow = man["slow"]
        self.P, self.t0, self.F = man["shot_period"], man["first_shot_at"], man["reset_fade"]
        self.shots = ev["shots"]
        self.t_hit = ev["t_hit"]
        self.th_hit = {p: state_at(self.shots[p], "cue", self.t_hit)[3] for p in PANELS}
        self.t_roll_end = {p: event(self.shots[p], "roll", "cue")[0] if event(self.shots[p], "roll", "cue") else None
                           for p in PANELS}

    # --- state helpers ------------------------------------------------------
    def phase(self, t: float) -> tuple[int, float]:
        k = math.floor((t - self.t0) / self.P + 1e-9)
        return k, t - (self.t0 + k * self.P)

    # --- pixel helpers ------------------------------------------------------
    def L(self, x: float, y: float) -> tuple[float, float]:
        """Layer (2x) pixel of a table point x metres along the cloth at frame row y."""
        return x * self.ppm * SS, (y - GEOM_Y0) * SS

    def circle(self, d: ImageDraw.ImageDraw, X: float, Y: float, rr: float, **kw) -> None:
        d.ellipse((X - rr, Y - rr, X + rr, Y + rr), **kw)

    def ball(self, d: ImageDraw.ImageDraw, X: float, Y: float, th: float, a: float, striped: bool) -> None:
        rr = self.R * self.ppm * SS
        if striped:
            self.circle(d, X, Y, rr, fill=blend(WHITE, a), outline=blend(RIM, a), width=2 * SS)
            # A great-circle stripe in a plane through the spin axis: a band across the ball that
            # turns with it; the dark dot on one end shows the full turn.
            da = math.asin(0.3)
            pts = [(X + rr * math.cos(q), Y + rr * math.sin(q))
                   for q in (th - da, th + da, th + math.pi - da, th + math.pi + da)]
            d.polygon(pts, fill=blend(CORAL, a))
            self.circle(d, X + 0.62 * rr * math.cos(th), Y + 0.62 * rr * math.sin(th), 0.15 * rr,
                        fill=blend((120, 40, 34), a))
        else:
            self.circle(d, X, Y, rr, fill=blend(GOLD, a), outline=blend((120, 84, 30), a), width=2 * SS)
            self.circle(d, X + 0.62 * rr * math.cos(th), Y + 0.62 * rr * math.sin(th), 0.15 * rr,
                        fill=blend((120, 84, 30), a))

    # --- the scene ----------------------------------------------------------
    def draw_shot(self, d: ImageDraw.ImageDraw, panel: str, tau: float, a: float) -> dict:
        """One shot of one panel at tau seconds of video after its launch, blended by a."""
        shot = self.shots[panel]
        r = tau / self.slow
        cloth_y = self.man[PANELS[panel]["cloth_key"]]
        rr = self.R * self.ppm * SS
        cx, cv, cw, cth = state_at(shot, "cue", r)
        ox, ov, ow, oth = state_at(shot, "obj", r)
        hit = r >= self.t_hit
        settled = self.t_roll_end[panel] is not None and r >= self.t_roll_end[panel]
        if hit:
            # The hit point: a tick on the cloth under the cue ball's centre, and the creep from it.
            hx, _ = self.L(self.ev["x_hit"], cloth_y)
            _, y0 = self.L(0.0, cloth_y)
            d.line((hx, y0 - 2 * SS, hx, y0 + 16 * SS), fill=blend(WHITE, 0.7 * a), width=2 * SS)
            X, _ = self.L(cx, cloth_y)
            if X - hx > 2 * SS:
                d.line((hx, y0 + 8 * SS, X, y0 + 8 * SS), fill=blend(GOLD, 0.9 * a), width=4 * SS)
        oX, oY = self.L(ox, cloth_y - self.R * self.ppm)
        self.ball(d, oX, oY, oth, a, striped=False)
        cX, cY = self.L(cx, cloth_y - self.R * self.ppm)
        self.ball(d, cX, cY, cth - self.th_hit[panel], a, striped=True)
        return {"x": cx, "v": cv, "w": cw, "hit": hit, "settled": settled, "alpha": a,
                "tag": (max(cX / SS, 76.0), GEOM_Y0 + cY / SS - rr / SS - 22)}   # the tag stays inside the frame while the ball runs in

    def draw_panel(self, d: ImageDraw.ImageDraw, panel: str, t: float) -> dict:
        man = self.man
        cloth_y = man[PANELS[panel]["cloth_key"]]
        k, tau = self.phase(t)
        # The table: the cloth line with faint ticks every cloth_tick_m, the body below it.
        x0, y0 = self.L(0.0, cloth_y)
        x1, _ = self.L(W / self.ppm, cloth_y)
        d.rectangle((x0, y0, x1, y0 + 52 * SS), fill=DECK_A)
        d.line((x0, y0, x1, y0), fill=blend(TEAL, 0.55), width=3 * SS)
        n_ticks = int(W / self.ppm / man["cloth_tick_m"]) + 1
        for j in range(n_ticks):
            tx, _ = self.L(j * man["cloth_tick_m"], cloth_y)
            d.line((tx, y0 + 30 * SS, tx, y0 + 44 * SS), fill=blend(MUTED, 0.45), width=2 * SS)
        # The shot in progress, crossfading to the next launch over the last reset_fade seconds.
        F, P = self.F, self.P
        a_old = 1.0 if tau <= P - F else max(0.0, (P - F / 2.0 - tau) / (F / 2.0))
        st = self.draw_shot(d, panel, tau, a_old) if a_old > 0.0 else None
        if tau >= P - F / 2.0:
            a_new = (tau - (P - F / 2.0)) / (F / 2.0)
            st_new = self.draw_shot(d, panel, tau - P, a_new)
            if st is None or a_new >= 0.5:
                st = st_new
        st["k"] = k
        return st

    def draw_text(self, d: ImageDraw.ImageDraw, states: dict, t: float, hud_alpha: float) -> None:
        man, ev = self.man, self.ev
        for panel, st in states.items():
            row = PANELS[panel]["row_y"]
            label = PANELS[panel]["label"]
            d.text((ROW_X0, row), label, font=self.font, fill=TEXT, anchor="lm")
            if panel == "top":
                word = "at rest" if st["hit"] else "sliding"
            else:
                word = "rolling" if (not st["hit"] or st["settled"]) else "spinning"
            a = st["alpha"]
            d.text((ROW_X0 + self.font.getlength(label) + STATE_GAP, row + 2), word, font=self.font_small,
                   fill=blend(MUTED, a), anchor="lm")
            final = st["hit"] and (panel == "top" or st["settled"])
            d.text((SPEED_X, row), speed_text(st["v"]), font=self.font, fill=blend(GOLD if final else TEXT, a), anchor="rm")
            d.text(st["tag"], "cue ball", font=self.font_small, fill=blend(WHITE, 0.8 * a), anchor="mm")
        if hud_alpha > 0.02:
            shot = min(states["top"]["k"], ev["shots_n"] - 1)
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
        layer = Image.new("RGB", (W * SS, (GEOM_Y1 - GEOM_Y0) * SS), BG)
        ld = ImageDraw.Draw(layer)
        states = {panel: self.draw_panel(ld, panel, t) for panel in PANELS}
        img.paste(layer.reduce(SS), (0, GEOM_Y0))
        d = ImageDraw.Draw(img)
        self.draw_text(d, states, t, hud_alpha)
        if title_alpha > 0.0:
            for j, line in enumerate(man["title"].split("|")):
                d.text((W / 2, 190 + j * 62), line, font=self.font_title, fill=blend(TEXT, title_alpha), anchor="mm")
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
    man = json.loads((ROOT / "projects/cueball/manifest.json").read_text())
    ev = measure(man)
    if "--measure-only" in sys.argv:
        return
    if "--frames" in sys.argv:
        times = [float(v) for v in sys.argv[sys.argv.index("--frames") + 1].split(",")]
        r = Renderer(man, ev)
        (ROOT / "media/cueball").mkdir(parents=True, exist_ok=True)
        for tv in times:
            Image.fromarray(r.frame_at(int(round(tv * man["fps"])))).save(ROOT / f"media/cueball/smoke-{tv}.png")
        print("smoke frames: " + ", ".join(f"{tv}" for tv in times))
        return
    Renderer(man, ev).render(ROOT / "media/cueball/footage.mp4")


if __name__ == "__main__":
    main()
