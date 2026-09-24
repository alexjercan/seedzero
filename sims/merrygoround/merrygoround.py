#!/usr/bin/env python3
"""Merry-go-round throw: do you hit your friend?

A round platform of radius R turns at a constant rate omega (counter-
clockwise seen from above). You stand at the centre, the one point of
the platform that does not move; your friend rides the rim. At the
throw instant a ball leaves the centre at speed v aimed exactly at the
friend. Seen from above the ball moves in a straight line at constant
speed (a flat toss: only the horizontal motion is drawn, no air) and
crosses the rim after R / v seconds; the friend has moved omega R / v
radians by then and the miss is the chord 2 R sin(omega R / (2 v))
between the friend and the crossing point (the arc is R omega R / v).
Seen from the ride every position is rotated by -omega t about the
centre: the platform and the friend stand fixed and the ball curves
away opposite to the turn on r = v t, angle -omega t. The ride view is
also integrated in the rotating frame with the Coriolis and centrifugal
terms (RK4) as a check on the rotated straight line. One throw every
throw_period seconds; the platform period and the throw period both
divide the scene length, so the scene is exactly periodic and the last
frame equals the first. Deterministic, no seed.

Measured and printed: the flight time (sampled crossing against R / v),
the angle the friend moves (against omega R / v), the chord and the arc
miss (against the closed forms), where the ball crosses the rim
relative to the friend, the friend's rim speed, the ride-view path
(RK4 in the rotating frame against the rotated line, its crossing time
and angle, a half-step check), the direction of the curve, the Coriolis
and centrifugal accelerations, the same throw at other speeds for the
description, the schedule in video time, the loop and periodicity
checks and the on-screen text widths.

usage: merrygoround.py [--measure-only] [--frames t1,t2,...]
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
# the first seconds, then the turn counter at y 236 and the legend at y
# 290; the "from above" row (label, flight clock, miss readout) at y 360
# over the top platform centred at (540, 640); the "from the ride" row at
# y 930 over the bottom platform centred at (540, 1190); the geometry
# band y 380..1436 drawn at 2x; captions at caption_y 0.75 (y 1440..1520);
# the payoff card from y 1592.
COUNTER_Y, TAG_Y = 236, 290
GEOM_Y0, GEOM_Y1 = 380, 1436
SS = 2
PAYOFF_Y = 1592.0
VIEWS = {"above": {"label": "from above", "row_y": 360}, "ride": {"label": "from the ride", "row_y": 930}}
ROW_X0, CLOCK_X, MISS_X = 100, 700, 980


def blend(col, a: float, base=BG) -> tuple:
    a = max(0.0, min(1.0, a))
    return tuple(int(round(c * a + b * (1 - a))) for c, b in zip(col, base))


def rot(x: float, y: float, ang: float) -> tuple[float, float]:
    c, s = math.cos(ang), math.sin(ang)
    return c * x - s * y, s * x + c * y


# --- measurement --------------------------------------------------------------
def ride_path_rk4(omega: float, v: float, a_f: float, R: float, dt: float) -> dict:
    """The ball in the frame turning with the platform: x'' = 2 w y' + w^2 x, y'' = -2 w x' + w^2 y
    (Coriolis and centrifugal terms of a free particle), from the centre at speed v toward the
    friend at platform angle a_f, until it crosses the rim; the crossing is interpolated inside
    the last step. Compared at every step with the rotated straight line v t at angle a_f - w t."""

    def deriv(s: np.ndarray) -> np.ndarray:
        return np.array([s[2], s[3], 2.0 * omega * s[3] + omega * omega * s[0], -2.0 * omega * s[2] + omega * omega * s[1]])

    s = np.array([0.0, 0.0, v * math.cos(a_f), v * math.sin(a_f)])
    t, max_err, cross = 0.0, 0.0, 0.0
    pts = [(0.0, 0.0, 0.0)]
    while True:
        k1 = deriv(s)
        k2 = deriv(s + 0.5 * dt * k1)
        k3 = deriv(s + 0.5 * dt * k2)
        k4 = deriv(s + dt * k3)
        sn = s + dt / 6.0 * (k1 + 2 * k2 + 2 * k3 + k4)
        tn = t + dt
        r0, r1 = math.hypot(s[0], s[1]), math.hypot(sn[0], sn[1])
        if r1 >= R:
            frac = (R - r0) / (r1 - r0)
            t_cross = t + frac * dt
            p = s[:2] + frac * (sn[:2] - s[:2])
            ang = math.atan2(p[1], p[0])
            break
        s, t = sn, tn
        ax, ay = v * t * math.cos(a_f - omega * t), v * t * math.sin(a_f - omega * t)
        max_err = max(max_err, math.hypot(s[0] - ax, s[1] - ay))
        # Sign of the turning: v x a < 0 means the velocity turns clockwise (to the right).
        cross = min(cross, s[2] * deriv(s)[3] - s[3] * deriv(s)[2])
        pts.append((t, s[0], s[1]))
    return {"t_cross": t_cross, "angle": ang, "max_err": max_err, "turn_sign": cross, "pts": pts}


def measure(man: dict) -> dict:
    R, rpm, v = man["platform_radius_m"], man["rpm"], man["throw_speed_m_s"]
    omega = rpm * 2.0 * math.pi / 60.0
    T_turn = 60.0 / rpm
    P, D, fps = man["throw_period"], man["scene_duration"], man["fps"]
    a_f = math.radians(man["friend_angle_deg"])
    dt = 1.0 / man["steps_per_second"]
    turns, throws = D / T_turn, D / P
    assert abs(turns - round(turns)) < 1e-9, "the platform period must divide the scene length"
    assert abs(throws - round(throws)) < 1e-9, "the throw period must divide the scene length"
    print(f"setup: a round platform of radius {R:g} m turning counterclockwise (seen from above) at {rpm:g} rpm "
          f"(omega = {omega:.4f} rad/s, {T_turn:.3f} s per turn); you stand at the centre, your friend rides the "
          f"rim at platform angle {man['friend_angle_deg']:g} degrees; at each throw a ball leaves the centre at "
          f"{v:g} m/s aimed exactly at the friend, a flat toss seen from above (horizontal motion only, no air), "
          f"a straight line at constant speed in the ground frame; the ride view rotates every position by "
          f"-omega t; ground path sampled and the ride view integrated with RK4 at {man['steps_per_second']} "
          f"steps per second (dt = {dt:.0e} s); real time, one throw every {P:g} s, {throws:.0f} throws and "
          f"{turns:.0f} turns in {D:g} s; drawn at {man['px_per_m']:g} px per metre (rim radius "
          f"{R * man['px_per_m']:.0f} px); deterministic, no seed")
    # Ground frame: r = v t sampled until it reaches the rim.
    t_f_closed = R / v
    n = int(math.ceil(1.5 * t_f_closed / dt))
    ts = np.arange(n + 1) * dt
    rs = v * ts
    i = int(np.argmax(rs >= R))
    t_f = float(ts[i - 1] + (R - rs[i - 1]) / (rs[i] - rs[i - 1]) * dt)
    theta = omega * t_f
    theta_closed = omega * R / v
    fx, fy = R * math.cos(a_f + theta), R * math.sin(a_f + theta)   # the friend at the crossing (ground)
    cx_, cy_ = R * math.cos(a_f), R * math.sin(a_f)                 # the crossing point (ground)
    chord = math.hypot(fx - cx_, fy - cy_)
    chord_closed = 2.0 * R * math.sin(theta_closed / 2.0)
    arc = R * theta
    print(f"flight: the ball crosses the rim after {t_f:.4f} s (closed form R / v = {t_f_closed:.4f} s, diff "
          f"{abs(t_f - t_f_closed):.1e}); the friend moves {math.degrees(theta):.2f} degrees = {theta:.4f} rad in "
          f"that time (closed form omega R / v = {math.degrees(theta_closed):.2f} degrees); the friend's rim speed "
          f"is omega R = {omega * R:.4f} m/s against the ball's {v:g} m/s")
    print(f"miss: the chord between the friend and the crossing point is {chord:.4f} m (closed form 2 R sin(omega "
          f"R / (2 v)) = {chord_closed:.4f} m, diff {abs(chord - chord_closed):.1e}); the arc along the rim is "
          f"{arc:.4f} m (R omega R / v = {R * theta_closed:.4f} m); the ball crosses the rim at the ground point "
          f"where the friend was at the throw, {math.degrees(theta):.1f} degrees behind the friend (clockwise of "
          f"them, opposite to the turn); the centre, the friend and the crossing point form a triangle with two "
          f"sides R and the angle {math.degrees(theta):.1f} degrees between them"
          + (f", an equilateral triangle, so the miss equals the radius (chord - R = {chord - R:.1e} m)"
             if abs(theta - math.pi / 3) < 1e-9 else ""))
    ride = ride_path_rk4(omega, v, a_f, R, dt)
    half = ride_path_rk4(omega, v, a_f, R, dt / 2)
    swing = math.degrees(a_f - ride["angle"])
    print(f"ride view (RK4 in the turning frame, Coriolis and centrifugal terms): the ball crosses the rim after "
          f"{ride['t_cross']:.4f} s at platform angle {math.degrees(ride['angle']):.2f} degrees, {swing:.2f} degrees "
          f"clockwise of the friend at {man['friend_angle_deg']:g} degrees (closed form a_f - omega R / v = "
          f"{man['friend_angle_deg'] - math.degrees(theta_closed):.2f}); chord to the friend "
          f"{2.0 * R * math.sin(math.radians(swing) / 2.0):.4f} m; max distance from the rotated straight line "
          f"r = v t, angle a_f - omega t over all steps {ride['max_err']:.1e} m; half-step check {half['t_cross']:.6f} "
          f"s against {ride['t_cross']:.6f} s (diff {abs(half['t_cross'] - ride['t_cross']):.1e} s)")
    print(f"direction: v x a stays {'negative' if ride['turn_sign'] < 0 else 'positive'} in the turning frame, so "
          f"the ball curves {'to its right (clockwise on screen)' if ride['turn_sign'] < 0 else 'to its left'}, "
          f"opposite to the platform's counterclockwise turn; at the rim it is {R * math.cos(theta):.3f} m along the "
          f"aim line and {R * math.sin(theta):.3f} m to the side of it; the sideways (Coriolis) acceleration in the "
          f"turning frame is 2 omega v = {2 * omega * v:.4f} m/s^2 throughout the flight, the outward (centrifugal) "
          f"term omega^2 r grows from 0 to {omega * omega * R:.4f} m/s^2 at the rim")
    print("ride-view path (t s, r m, angle deg, x m, y m): " + "; ".join(
        f"{t:.2f} {v * t:.3f} {math.degrees(a_f - omega * t):.1f} {x:.3f} {y:.3f}"
        for t, x, y in [ride["pts"][int(round(tt / dt))] for tt in (0.0, 0.25, 0.5, 0.75)] + [(ride["t_cross"],
                                                                                            R * math.cos(ride["angle"]), R * math.sin(ride["angle"]))]))
    print("for the description (same platform, other throw speeds): " + "; ".join(
        f"{u:g} m/s: flight {R / u:.3f} s, friend moves {math.degrees(omega * R / u):.1f} degrees, chord "
        f"{2 * R * math.sin(omega * R / (2 * u)):.3f} m, arc {omega * R * R / u:.3f} m" for u in man["description_speeds_m_s"]))
    # Schedule in video time.
    t0, lead, mfade = man["first_throw_at"], man["aim_lead"], man["marker_fade"]
    exit_t = man["exit_fade_m"] / v
    assert t_f + exit_t < P - lead - mfade, "the throw period is too short for the flight, the marker and the aim lead"
    k0 = math.ceil((0.0 - t0) / P - 1e-9)
    k1 = math.floor((D - t0) / P - 1e-9)
    throws_v = [(k, t0 + k * P) for k in range(k0, k1 + 1)]
    dirs = ", ".join(f"{tk:.2f} s ({(man['friend_angle_deg'] + math.degrees(omega * k * P)) % 360:.0f} deg)" for k, tk in throws_v)
    print(f"schedule (video time, real time): the platform angle is 0 at the first throw ({t0:g} s), throws every "
          f"{P:g} s at {dirs} with the ground direction of each throw in brackets (the friend's position at that "
          f"instant); each ball crosses the rim {t_f:.2f} s after its throw and fades out {exit_t:.2f} s later, "
          f"{man['exit_fade_m']:g} m beyond the rim; the miss marker holds from the crossing until {mfade:g} s "
          f"before the aim lead, which starts {lead:g} s before the next throw; crossings at "
          + ", ".join(f"{tk + t_f:.2f}" for _, tk in throws_v if 0.0 <= tk + t_f < D)
          + f" s; title until {man['title_until']:g} s; payoff card from {man['payoff_t']:g} s; the title fades back "
          f"in over the last {man['loop_fade']:g} s and the last frame repeats the first")
    ev = {"omega": omega, "T_turn": T_turn, "t_f": t_f, "theta": theta, "chord": chord, "arc": arc,
          "turns": int(round(turns)), "throws": int(round(throws)), "ride": ride}
    # Text widths.
    font = os.environ["SEED_ZERO_FONT"]
    f28, f34, f40, f56 = (ImageFont.truetype(font, n) for n in (28, 34, 40, 56))
    widths = {"overlay@34": (f34, man["overlay"])}
    for j, line in enumerate(man["title"].split("|")):
        widths[f"title line {j + 1}@56"] = (f56, line)
    widths["counter@40"] = (f40, counter_text(man, ev, ev["turns"] - 1))
    widths["legend@28"] = (f28, legend_text(man))
    for name in VIEWS:
        widths[f"label {name}@40"] = (f40, VIEWS[name]["label"])
    widths["clock@40"] = (f40, clock_text(t_f))
    widths["miss@40"] = (f40, miss_text(chord))
    widths["you tag@28"] = (f28, "you")
    widths["friend tag@28"] = (f28, "friend")
    for j, line in enumerate(payoff_lines(man, ev)):
        widths[f"payoff line {j + 1}@40"] = (f40, line)
    print("text widths: " + ", ".join(f"{k} {f.getlength(s):.0f} px" for k, (f, s) in widths.items()))
    assert all(f.getlength(s) < 950 for f, s in widths.values()), "a text line is wider than 950 px"
    return ev


def counter_text(man: dict, ev: dict, turn: int) -> str:
    return f"turn {turn + 1} of {ev['turns']}"


def legend_text(man: dict) -> str:
    return f"you at the center, friend on the rim, flat toss at {man['throw_speed_m_s']:g} m/s"


def clock_text(t: float) -> str:
    return f"flight {t:.2f} s"


def miss_text(chord: float) -> str:
    return f"miss {chord:.2f} m"


def payoff_lines(man: dict, ev: dict) -> list[str]:
    text = man["payoff_text"].format(chord=ev["chord"], angle=math.degrees(ev["theta"]), flight=ev["t_f"])
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
        self.R = man["platform_radius_m"]
        self.v = man["throw_speed_m_s"]
        self.omega = ev["omega"]
        self.a_f = math.radians(man["friend_angle_deg"])
        self.P, self.t0 = man["throw_period"], man["first_throw_at"]
        self.t_f = ev["t_f"]
        self.exit_t = man["exit_fade_m"] / self.v
        self.centres = {"above": tuple(man["top_centre"]), "ride": tuple(man["bottom_centre"])}

    # --- state helpers ------------------------------------------------------
    def phi(self, t: float) -> float:
        """Platform angle (rad, counterclockwise), 0 at the first throw."""
        return self.omega * (t - self.t0)

    def phase(self, t: float) -> tuple[int, float]:
        k = math.floor((t - self.t0) / self.P + 1e-9)
        return k, t - (self.t0 + k * self.P)

    def throw_dir(self, k: int) -> float:
        """Ground direction of throw k: the friend's ground angle at that instant."""
        return self.a_f + self.omega * k * self.P

    def view_rot(self, view: str, t: float) -> float:
        return 0.0 if view == "above" else -self.phi(t)

    # --- pixel helpers ------------------------------------------------------
    def px(self, view: str, x: float, y: float) -> tuple[float, float]:
        cx, cy = self.centres[view]
        return cx + x * self.ppm, cy - y * self.ppm

    def L(self, view: str, x: float, y: float) -> tuple[float, float]:
        X, Y = self.px(view, x, y)
        return X * SS, (Y - GEOM_Y0) * SS

    def polar(self, view: str, r: float, ang: float) -> tuple[float, float]:
        return self.L(view, r * math.cos(ang), r * math.sin(ang))

    def circle(self, d: ImageDraw.ImageDraw, X: float, Y: float, rr: float, **kw) -> None:
        d.ellipse((X - rr, Y - rr, X + rr, Y + rr), **kw)

    def arc(self, d: ImageDraw.ImageDraw, view: str, r: float, a0: float, a1: float, fill, width: int) -> None:
        """Arc on the rim from angle a0 to a1 counterclockwise (rad, y up)."""
        cx, cy = self.L(view, 0.0, 0.0)
        rr = r * self.ppm * SS
        s, e = (-math.degrees(a1)) % 360.0, (-math.degrees(a0)) % 360.0
        if e < s:
            e += 360.0
        d.arc((cx - rr, cy - rr, cx + rr, cy + rr), s, e, fill=fill, width=width)

    def dashed(self, d: ImageDraw.ImageDraw, p0, p1, fill, width: int, dash: float, gap: float) -> None:
        (x0, y0), (x1, y1) = p0, p1
        seg = math.hypot(x1 - x0, y1 - y0)
        ux, uy = (x1 - x0) / seg, (y1 - y0) / seg
        pos = 0.0
        while pos < seg:
            run = min(dash, seg - pos)
            d.line((x0 + ux * pos, y0 + uy * pos, x0 + ux * (pos + run), y0 + uy * (pos + run)), fill=fill, width=width)
            pos += dash + gap

    # --- the scene ----------------------------------------------------------
    def draw_panel(self, d: ImageDraw.ImageDraw, view: str, t: float) -> dict:
        man = self.man
        R, v, omega = self.R, self.v, self.omega
        k, tau = self.phase(t)
        phi = self.phi(t)
        rot_v = self.view_rot(view, t)
        Rpx = R * self.ppm * SS
        cX, cY = self.L(view, 0.0, 0.0)
        # The deck: alternating sectors fixed to the platform, then the rim.
        n_sec = man["sectors"]
        for j in range(n_sec):
            a0 = 2 * math.pi * j / n_sec + phi + rot_v
            a1 = a0 + 2 * math.pi / n_sec
            s, e = (-math.degrees(a1)) % 360.0, (-math.degrees(a0)) % 360.0
            if e < s:
                e += 360.0
            d.pieslice((cX - Rpx, cY - Rpx, cX + Rpx, cY + Rpx), s, e, fill=DECK_A if j % 2 == 0 else DECK_B)
        self.circle(d, cX, cY, Rpx, outline=RIM, width=3 * SS)
        # Ground marks: ticks just outside the rim, fixed to the ground.
        for j in range(man["ground_ticks"]):
            a = 2 * math.pi * j / man["ground_ticks"] + rot_v
            p0 = self.polar(view, R + 8 / self.ppm, a)
            p1 = self.polar(view, R + 20 / self.ppm, a)
            d.line((*p0, *p1), fill=blend(MUTED, 0.7), width=2 * SS)
        # Phase-dependent alphas: the throw's trail, arc and marker hold until marker_fade before
        # the next throw (hold_a); the chord and the cross fade in over 0.15 s at the crossing.
        lead, mfade = man["aim_lead"], man["marker_fade"]
        in_flight = tau < self.t_f
        ball_on = tau < self.t_f + self.exit_t
        hold_end = self.P - lead                     # the marker is gone before the next aim lead
        hold_a = 1.0 if tau <= hold_end - mfade else max(0.0, (hold_end - tau) / mfade)
        crossed = tau >= self.t_f
        marker_a = min(hold_a, (tau - self.t_f) / 0.15) if crossed else 0.0
        pre = tau >= hold_end
        aim_a = (tau - hold_end) / lead if pre else hold_a
        d_k = self.throw_dir(k)
        friend_g = self.a_f + phi                    # the friend's ground angle now
        # Where the ball crosses the rim and where the friend is at that instant, in the view's own
        # frame: fixed to the ground in the view from above (the trail, the cross, the chord and the
        # ghost stay where the miss happened while the friend rides on), fixed to the platform in the
        # view from the ride.
        if view == "above":
            a_cross, a_friend_x = d_k, d_k + omega * self.t_f
        else:
            a_cross, a_friend_x = self.a_f - omega * self.t_f, self.a_f
        # The arc the friend moves along the rim during the flight (ground view only).
        if view == "above" and hold_a > 0.0:
            self.arc(d, view, R - 5 / self.ppm, d_k, friend_g if in_flight else a_friend_x, blend(GOLD, 0.8 * hold_a), 5 * SS)
        # The aim line: before the throw it follows the friend, then it is fixed in each view's frame.
        if aim_a > 0.0:
            aim = friend_g + rot_v if pre else (d_k if view == "above" else self.a_f)
            self.dashed(d, self.polar(view, 0.16, aim), self.polar(view, R, aim), blend(WHITE, 0.55 * aim_a),
                        3 * SS, 9 * SS, 8 * SS)
        # The trail of the current throw: each point fixed in the view's frame at its own time.
        trail_a = hold_a
        if hold_a > 0.0:
            t_throw = self.t0 + k * self.P
            n_pts = int(math.floor(min(tau, self.t_f) * self.fps)) + 1
            pts = []
            for j in range(n_pts):
                s_j = t_throw + j / self.fps
                r_j = min(v * (j / self.fps), R)
                x, y = r_j * math.cos(d_k), r_j * math.sin(d_k)
                if view == "ride":
                    x, y = rot(x, y, -self.phi(s_j))
                pts.append(self.L(view, x, y))
            if in_flight:
                x, y = v * tau * math.cos(d_k), v * tau * math.sin(d_k)
                if view == "ride":
                    x, y = rot(x, y, rot_v)
                pts.append(self.L(view, x, y))
            if len(pts) >= 2:
                d.line(pts, fill=blend(CORAL, 0.75 * trail_a), width=4 * SS, joint="curve")
        # Ghosts of the friend (ground view): where they were at the throw (the aim point) during
        # the flight, and where they were at the crossing once the ball has crossed.
        if view == "above" and hold_a > 0.0:
            fr_px = man["friend_radius_m"] * self.ppm * SS
            if in_flight:
                gx, gy = self.polar(view, R, d_k)
                self.circle(d, gx, gy, fr_px, outline=blend(GOLD, 0.5 * hold_a), width=2 * SS)
            if marker_a > 0.0:
                gx, gy = self.polar(view, R, a_friend_x)
                self.circle(d, gx, gy, fr_px, outline=blend(GOLD, 0.6 * marker_a), width=2 * SS)
        # The miss marker: the chord from the friend to the crossing point and a cross at the crossing.
        if marker_a > 0.0:
            fx, fy = self.polar(view, R, a_friend_x)
            mx, my = self.polar(view, R, a_cross)
            d.line((fx, fy, mx, my), fill=blend(GOLD, marker_a), width=4 * SS)
            s = 9 * SS
            for dx, dy in ((1, 1), (1, -1)):
                d.line((mx - s * dx, my - s * dy, mx + s * dx, my + s * dy), fill=blend(WHITE, marker_a), width=4 * SS)
        # You at the centre, the friend on the rim, the ball.
        self.circle(d, cX, cY, 8 * SS, fill=blend(WHITE, 0.85), outline=BG, width=SS)
        fx, fy = self.polar(view, R, self.a_f + phi + rot_v)
        fr = man["friend_radius_m"] * self.ppm * SS
        self.circle(d, fx, fy, fr, fill=GOLD, outline=(120, 84, 30), width=2 * SS)
        if ball_on:
            r_b = v * tau
            x, y = r_b * math.cos(d_k), r_b * math.sin(d_k)
            if view == "ride":
                x, y = rot(x, y, rot_v)
            a = 1.0 if r_b <= R else max(0.0, 1.0 - (r_b - R) / man["exit_fade_m"])
            bx, by = self.L(view, x, y)
            br = man["ball_radius_m"] * self.ppm * SS
            self.circle(d, bx, by, br, fill=blend(CORAL, a), outline=blend((120, 40, 34), a), width=2 * SS)
            self.circle(d, bx - br * 0.3, by - br * 0.35, br * 0.22, fill=blend((246, 170, 160), a))
        tag_p = self.px(view, *rot(*((R - 0.5) * math.cos(self.a_f + 0.25), (R - 0.5) * math.sin(self.a_f + 0.25)), phi + rot_v))
        return {"k": k, "tau": tau, "in_flight": in_flight, "crossed": crossed, "hold_a": hold_a, "marker_a": marker_a,
                "aim_a": aim_a, "pre": pre, "friend_tag": tag_p}

    def draw_text(self, d: ImageDraw.ImageDraw, states: dict, t: float, hud_alpha: float) -> None:
        man, ev = self.man, self.ev
        for view, st in states.items():
            row = VIEWS[view]["row_y"]
            d.text((ROW_X0, row), VIEWS[view]["label"], font=self.font, fill=TEXT, anchor="lm")
            tau = st["tau"]
            if st["in_flight"]:
                d.text((CLOCK_X, row), clock_text(tau), font=self.font, fill=TEXT, anchor="rm")
            elif st["crossed"] and st["hold_a"] > 0.0:
                d.text((CLOCK_X, row), clock_text(self.t_f), font=self.font, fill=blend(MUTED, st["hold_a"]), anchor="rm")
                if st["marker_a"] > 0.0:
                    d.text((MISS_X, row), miss_text(ev["chord"]), font=self.font, fill=blend(GOLD, st["marker_a"]), anchor="rm")
            elif st["pre"]:
                d.text((CLOCK_X, row), clock_text(0.0), font=self.font, fill=blend(TEXT, st["aim_a"]), anchor="rm")
            cx, cy = self.centres[view]
            d.text((cx - 22, cy), "you", font=self.font_small, fill=blend(WHITE, 0.8), anchor="rm")
            d.text(st["friend_tag"], "friend", font=self.font_small, fill=GOLD, anchor="mm")
        if hud_alpha > 0.02:
            turn = int(math.floor(t / ev["T_turn"] + 1e-9))
            d.text((W / 2, COUNTER_Y), counter_text(man, ev, turn), font=self.font, fill=blend(TEXT, hud_alpha), anchor="mm")
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
        states = {view: self.draw_panel(ld, view, t) for view in VIEWS}
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
              f"(the platform turns {math.degrees(self.omega / self.fps):.2f} degrees per frame)")
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
    man = json.loads((ROOT / "projects/merrygoround/manifest.json").read_text())
    ev = measure(man)
    if "--measure-only" in sys.argv:
        return
    if "--frames" in sys.argv:
        times = [float(v) for v in sys.argv[sys.argv.index("--frames") + 1].split(",")]
        r = Renderer(man, ev)
        (ROOT / "media/merrygoround").mkdir(parents=True, exist_ok=True)
        for tv in times:
            Image.fromarray(r.frame_at(int(round(tv * man["fps"])))).save(ROOT / f"media/merrygoround/smoke-{tv}.png")
        print("smoke frames: " + ", ".join(f"{tv}" for tv in times))
        return
    Renderer(man, ev).render(ROOT / "media/merrygoround/footage.mp4")


if __name__ == "__main__":
    main()
