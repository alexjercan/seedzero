#!/usr/bin/env python3
"""Pulled spool: which way does the spool roll?

A spool (two flanges of radius R joined by an axle of radius r, mass m,
moment of inertia k m R^2 about its centre) rests on a level table. A
string is wound on the axle and leaves the bottom of the axle
tangentially toward the hand, which holds it at a fixed angle theta
above the table and pulls with a constant force F. The hand moves with
the spool (taking up or paying out the string that winds on or off the
axle) so the angle and the pull stay fixed. The spool rolls without
slipping, so about the contact point P the equation of motion is
I_P alpha = torque with I_P = (k + 1) m R^2 and a = alpha R. The
string is tangent to the axle at T = C + r (sin theta, -cos theta), so
the line of the string passes P at the distance R cos theta - r and
the torque about P is F (R cos theta - r) toward the hand: the spool
rolls toward the hand when cos theta > r / R, away when cos theta <
r / R, and the switch is at acos(r / R). The same line meets the table
at (r - R cos theta) / sin theta from P: behind P (on the far side
from the hand) when the spool rolls toward the hand, ahead of P
(between P and the hand) when it rolls away, through P at the switch.
Both panels are integrated with RK4 (the torque taken from the string
geometry at every step) and compared with the closed form a = F (R cos
theta - r) / ((k + 1) m R). The friction the roll needs (f = m a - F
cos theta against N = m g - F sin theta) and the lift check (F sin
theta < m g) are printed and asserted against mu. Each pull lasts
pull_duration seconds, the end state holds, the scene fades and the
spool is reset for the next pull; the pull period divides the scene
length, so the scene is periodic and the last frame equals the first.
Deterministic, no seed.

Measured and printed: the accelerations and the distances at the end
of the pull in both panels against the closed form, the end speeds,
the direction of each roll, the switch angle acos(r / R), where the
string line meets the table relative to P and the lever arm about P
in both panels, the lift and no-slip checks and the friction each
roll needs, the wheel turn and the string wound in or paid out, the
same pull at other angles for the description, the schedule in video
time, the loop and periodicity checks and the on-screen text widths.

usage: spool.py [--measure-only] [--frames t1,t2,...]
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

# Layout: overlay at y 96..130 (captions.py), title rows at y 190/248 (50 px)
# for the first seconds, then the pull counter and clock at y 236 and the
# legend at y 290; a panel row (label left, direction readout right) at y
# 380 over the table at y 780 and one at y 900 over the table at y 1300;
# each panel has its own start x (the 30 degree spool starts on the left
# and rolls right, the 80 degree spool starts on the right and rolls left);
# the geometry band y 400..1400 drawn at 2x; captions at caption_y 0.75
# (y 1440..1520); the payoff card from y 1580.
COUNTER_Y, TAG_Y = 236, 290
TITLE_Y, TITLE_STEP = 190, 58
GEOM_Y0, GEOM_Y1 = 400, 1400
SS = 2
PAYOFF_Y, PAYOFF_STEP = 1580.0, 56
ROW_X0, READ_X = 100, 980
TABLE_X0, TABLE_X1 = 60, 1020
REF_LEN_PX = 200
READ_MIN_M = 0.0005   # the readout and the bar appear once the spool has moved 0.05 cm


def blend(col, a: float, base=BG) -> tuple:
    a = max(0.0, min(1.0, a))
    return tuple(int(round(c * a + b * (1 - a))) for c, b in zip(col, base))


# --- measurement --------------------------------------------------------------
def string_geometry(man: dict, theta_deg: float) -> dict:
    """The string line for a pull at theta: P at the origin, x toward the hand, y up."""
    R, r, F = man["wheel_radius_m"], man["axle_radius_m"], man["pull_N"]
    th = math.radians(theta_deg)
    s, c = math.sin(th), math.cos(th)
    Tx, Ty = r * s, R - r * c                 # the tangent point on the axle, relative to P
    Fx, Fy = F * c, F * s                     # the pull along the string
    torque = Ty * Fx - Tx * Fy                # clockwise torque about P: positive rolls toward the hand
    lever = R * c - r                         # signed distance from P to the string line (= torque / F)
    x_meet = (r - R * c) / s if s > 1e-12 else math.inf   # where the string line meets the table, from P
    return {"th": th, "T": (Tx, Ty), "F": (Fx, Fy), "torque": torque, "lever": lever, "x_meet": x_meet}


def pull_rk4(man: dict, theta_deg: float, dt: float) -> dict:
    """Roll without slipping about P: x'' = torque(geometry) / ((k + 1) m R), RK4 for the pull."""
    R, m, k = man["wheel_radius_m"], man["mass_kg"], man["inertia_k"]
    I_P = (k + 1.0) * m * R * R

    def accel(x: float, v: float) -> float:
        g = string_geometry(man, theta_deg)   # the angle is held fixed, so the torque does not depend on x or v
        return g["torque"] / I_P * R

    n = int(round(man["pull_duration"] / dt))
    ts = np.arange(n + 1) * dt
    xs, vs = np.zeros(n + 1), np.zeros(n + 1)
    x = v = 0.0
    for i in range(1, n + 1):
        k1x, k1v = v, accel(x, v)
        k2x, k2v = v + 0.5 * dt * k1v, accel(x + 0.5 * dt * k1x, v + 0.5 * dt * k1v)
        k3x, k3v = v + 0.5 * dt * k2v, accel(x + 0.5 * dt * k2x, v + 0.5 * dt * k2v)
        k4x, k4v = v + dt * k3v, accel(x + dt * k3x, v + dt * k3v)
        x += dt / 6.0 * (k1x + 2 * k2x + 2 * k3x + k4x)
        v += dt / 6.0 * (k1v + 2 * k2v + 2 * k3v + k4v)
        xs[i], vs[i] = x, v
    return {"ts": ts, "xs": xs, "vs": vs, "a": accel(0.0, 0.0)}


def direction_word(a: float) -> str:
    return "toward the hand" if a > 1e-12 else ("away from the hand" if a < -1e-12 else "no roll")


def measure(man: dict) -> dict:
    R, r, m, k, F, g, mu = (man[key] for key in ("wheel_radius_m", "axle_radius_m", "mass_kg", "inertia_k",
                                                  "pull_N", "g", "mu"))
    T_pull, P, D, fps = man["pull_duration"], man["pull_period"], man["scene_duration"], man["fps"]
    dt = 1.0 / man["steps_per_second"]
    pulls = D / P
    assert abs(pulls - round(pulls)) < 1e-9, "the pull period must divide the scene length"
    assert T_pull + man["hold"] + 2 * man["reset_fade"] <= P + 1e-9, "the pull period is too short for the pull, the hold and the reset"
    angles = man["angles_deg"]
    print(f"setup: a spool of mass {m * 1000:g} g with a wheel (flange) of radius R = {R * 100:g} cm and an axle of radius "
          f"r = {r * 100:g} cm (r / R = {r / R:g}), I = {k:g} m R^2 about the centre, on a level table with friction "
          f"coefficient mu = {mu:g}, g = {g:g} m/s^2; the string is wound on the axle and leaves its bottom tangentially "
          f"toward the hand (to the right), held at a fixed angle above the table and pulled with a constant F = {F:g} N "
          f"({F / (m * g):.3f} m g); the hand moves with the spool so the angle and the pull stay fixed; rolling "
          f"without slipping about the contact point P, I_P = (k + 1) m R^2 = {(k + 1) * m * R * R:.3e} kg m^2, "
          f"integrated with RK4 at {man['steps_per_second']} steps per second (dt = {dt:.0e} s) with the torque taken "
          f"from the string geometry at every step; two panels, the string at {angles[0]:g} degrees above and "
          f"{angles[1]:g} degrees below; each pull lasts {T_pull:g} s, one pull every {P:g} s, {pulls:.0f} pulls in "
          f"{D:g} s; drawn at {man['px_per_cm']:g} px per cm (wheel radius {R * 100 * man['px_per_cm']:.0f} px), the "
          f"{angles[0]:g} degree spool starting at x = {man['start_x'][0]:g} px and the {angles[1]:g} degree spool at x = "
          f"{man['start_x'][1]:g} px; "
          f"deterministic, no seed")
    ev: dict = {"pulls": [], "switch_deg": math.degrees(math.acos(r / R))}
    for th_deg in angles:
        geo = string_geometry(man, th_deg)
        run = pull_rk4(man, th_deg, dt)
        half = pull_rk4(man, th_deg, dt / 2)
        a_closed = F * (R * math.cos(geo["th"]) - r) / ((k + 1.0) * m * R)
        x_end, v_end = float(run["xs"][-1]), float(run["vs"][-1])
        x_closed = 0.5 * a_closed * T_pull * T_pull
        N = m * g - geo["F"][1]
        f = m * run["a"] - geo["F"][0]
        mu_needed = abs(f) / N
        turn = x_end / R
        print(f"pull at {th_deg:g} degrees: torque about P = F (R cos theta - r) = {geo['torque']:.4e} N m "
              f"({'clockwise' if geo['torque'] > 0 else 'counterclockwise'}), lever arm R cos theta - r = "
              f"{geo['lever'] * 100:+.3f} cm; acceleration {run['a']:+.4f} m/s^2 (closed form {a_closed:+.4f} m/s^2, "
              f"diff {abs(run['a'] - a_closed):.1e}); after {T_pull:.2f} s the spool has rolled {abs(x_end) * 100:.2f} cm "
              f"{direction_word(x_end)} (closed form a t^2 / 2 = {abs(x_closed) * 100:.2f} cm, diff "
              f"{abs(x_end - x_closed):.1e} m; half-step check {abs(float(half['xs'][-1])) * 100:.6f} cm, diff "
              f"{abs(float(half['xs'][-1]) - x_end):.1e} m) at {abs(v_end):.4f} m/s; the wheel turns "
              f"{math.degrees(turn):.1f} degrees ({turn:.3f} rad) and the axle "
              f"{'winds in' if x_end > 0 else 'pays out'} {abs(turn) * r * 100:.2f} cm of string; the string line "
              f"meets the table {abs(geo['x_meet']) * 100:.2f} cm {'ahead of P, between P and the hand' if geo['x_meet'] > 0 else 'behind P, on the far side from the hand'}; "
              f"lift check F sin theta = {geo['F'][1]:.3f} N against m g = {m * g:.3f} N ({'ok' if geo['F'][1] < m * g else 'LIFTS'}); "
              f"no-slip check: friction f = m a - F cos theta = {f:+.4f} N against N = m g - F sin theta = {N:.4f} N, "
              f"needs mu >= {mu_needed:.3f} ({'ok' if mu_needed <= mu else 'SLIPS'} with mu = {mu:g})")
        assert geo["F"][1] < m * g, "the pull lifts the spool off the table"
        assert mu_needed <= mu, "the spool slips"
        assert abs(run["a"] - a_closed) < 1e-12 and abs(x_end - x_closed) < 1e-9
        ev["pulls"].append({"theta_deg": th_deg, "ts": run["ts"], "xs": run["xs"], "vs": run["vs"], "a": run["a"],
                            "x_end": x_end, "v_end": v_end, "x_meet": geo["x_meet"], "lever": geo["lever"],
                            "mu_needed": mu_needed, "f": f, "N": N})
    sw = ev["switch_deg"]
    geo_sw = string_geometry(man, sw)
    print(f"switch: the spool rolls toward the hand when cos theta > r / R = {r / R:g}, away when cos theta < r / R; "
          f"acos(r / R) = {sw:.2f} degrees; at {sw:.2f} degrees the torque about P is {geo_sw['torque']:.1e} N m, the "
          f"acceleration {geo_sw['torque'] / ((k + 1) * m * R):.1e} m/s^2 and the string line meets the table "
          f"{geo_sw['x_meet'] * 100:.4f} cm from P (through the touch point, tangent to the axle); "
          f"{angles[0]:g} degrees is {sw - angles[0]:.2f} degrees below the switch, {angles[1]:g} degrees is "
          f"{angles[1] - sw:.2f} degrees above it")
    def tidy(v: float) -> float:
        return 0.0 if abs(v) < 1e-12 else v

    scan = []
    for u in man["description_angles_deg"]:
        gu = string_geometry(man, u)
        au = tidy(gu["torque"] / ((k + 1) * m * R))
        scan.append(f"{u:g} degrees: a {au:+.4f} m/s^2, {abs(au) * 0.5 * T_pull * T_pull * 100:.2f} cm "
                    f"{direction_word(au)}, the line meets the table "
                    f"{'beyond the table edge' if not math.isfinite(gu['x_meet']) else f'{tidy(gu['x_meet']) * 100:+.2f} cm from P'}, "
                    f"mu >= {abs(m * au - gu['F'][0]) / (m * g - gu['F'][1]):.3f}")
    print("for the description (the same spool and pull at other angles, distance after "
          f"{T_pull:.2f} s, + ahead of P toward the hand): " + "; ".join(scan))
    # Schedule in video time.
    t0, hold, fade = man["first_pull_at"], man["hold"], man["reset_fade"]
    k0 = math.ceil((0.0 - t0) / P - 1e-9)
    k1 = math.floor((D - t0) / P - 1e-9)
    pulls_v = [(kk, t0 + kk * P) for kk in range(k0 - 1, k1 + 1)]
    print(f"schedule (video time, real time): pulls every {P:g} s at "
          + ", ".join(f"{tk:.2f}" for _, tk in pulls_v) + f" s (the first pull starts at {t0:g} s, so the first frame "
          f"is {-t0:g} s into it); each pull ends {T_pull:g} s after its start, the end state holds {hold:g} s, "
          f"the scene fades out over {fade:g} s and fades back in at the start over {fade:g} s, then waits for the "
          f"next pull; pull ends at " + ", ".join(f"{tk + T_pull:.2f}" for _, tk in pulls_v if 0.0 <= tk + T_pull < D)
          + f" s; title until {man['title_until']:g} s; payoff card from {man['payoff_t']:g} s; the title fades back "
          f"in over the last {man['loop_fade']:g} s and the last frame repeats the first")
    ev.update({"n_pulls": int(round(pulls))})
    # Text widths.
    font = os.environ["SEED_ZERO_FONT"]
    f28, f34, f40, f50 = (ImageFont.truetype(font, n) for n in (28, 34, 40, 50))
    widths = {"overlay@34": (f34, man["overlay"])}
    for j, line in enumerate(man["title"].split("|")):
        widths[f"title line {j + 1}@50"] = (f50, line)
    widths["counter@40"] = (f40, counter_text(ev["n_pulls"] - 1, ev["n_pulls"], T_pull))
    widths["legend@28"] = (f28, legend_text(man))
    for p in ev["pulls"]:
        widths[f"label {p['theta_deg']:g}@40"] = (f40, label_text(p["theta_deg"]))
        widths[f"readout {p['theta_deg']:g}@40"] = (f40, readout_text(p["x_end"]))
    widths["hand tag@28"] = (f28, "hand")
    widths["switch tag@28"] = (f28, switch_tag(ev))
    for j, line in enumerate(payoff_lines(man, ev)):
        widths[f"payoff line {j + 1}@40"] = (f40, line)
    print("text widths: " + ", ".join(f"{key} {f.getlength(s):.0f} px" for key, (f, s) in widths.items()))
    assert all(f.getlength(s) < 950 for f, s in widths.values()), "a text line is wider than 950 px"
    return ev


def counter_text(pull: int, n: int, clock: float) -> str:
    return f"pull {pull % n + 1} of {n}, {clock:.2f} s"


def legend_text(man: dict) -> str:
    return f"{man['mass_kg'] * 1000:g} g spool, axle half the wheel, {man['pull_N']:g} N on the string"


def label_text(theta_deg: float) -> str:
    return f"pull at {theta_deg:g} degrees"


def readout_text(x: float) -> str:
    return f"{'toward' if x > 0 else 'away'} {abs(x) * 100:.1f} cm"


def switch_tag(ev: dict) -> str:
    return f"{ev['switch_deg']:.0f} degrees"


def payoff_lines(man: dict, ev: dict) -> list[str]:
    text = man["payoff_text"].format(switch=ev["switch_deg"])
    return [s.strip() for s in text.split("|")]


# --- rendering ---------------------------------------------------------------
class Renderer:
    def __init__(self, man: dict, ev: dict):
        self.man, self.ev = man, ev
        self.fps = man["fps"]
        font = os.environ["SEED_ZERO_FONT"]
        self.font = ImageFont.truetype(font, 40)
        self.font_title = ImageFont.truetype(font, 50)
        self.font_small = ImageFont.truetype(font, 28)
        self.ppm = float(man["px_per_cm"]) * 100.0
        self.R, self.r = man["wheel_radius_m"], man["axle_radius_m"]
        self.P, self.t0 = man["pull_period"], man["first_pull_at"]
        self.T_pull, self.hold, self.fade = man["pull_duration"], man["hold"], man["reset_fade"]
        self.x0s = [float(v) for v in man["start_x"]]

    # --- state helpers ------------------------------------------------------
    def phase(self, t: float) -> tuple[int, float]:
        k = math.floor((t - self.t0) / self.P + 1e-9)
        return k, t - (self.t0 + k * self.P)

    def group_state(self, tau: float) -> tuple[float, float, bool]:
        """(time into the pull for the position, alpha of the moving group, pulling now)."""
        hold_end = self.T_pull + self.hold
        if tau < self.T_pull:
            return tau, 1.0, True
        if tau < hold_end:
            return self.T_pull, 1.0, False
        if tau < hold_end + self.fade:
            return self.T_pull, 1.0 - (tau - hold_end) / self.fade, False
        if tau < hold_end + 2 * self.fade:
            return 0.0, (tau - hold_end - self.fade) / self.fade, False
        return 0.0, 1.0, False

    # --- pixel helpers ------------------------------------------------------
    def L(self, X: float, Y: float) -> tuple[float, float]:
        return X * SS, (Y - GEOM_Y0) * SS

    def circle(self, d: ImageDraw.ImageDraw, X: float, Y: float, rr: float, **kw) -> None:
        d.ellipse((X - rr, Y - rr, X + rr, Y + rr), **kw)

    def dashed(self, d: ImageDraw.ImageDraw, p0, p1, fill, width: int, dash: float, gap: float) -> None:
        (x0, y0), (x1, y1) = p0, p1
        seg = math.hypot(x1 - x0, y1 - y0)
        if seg < 1e-6:
            return
        ux, uy = (x1 - x0) / seg, (y1 - y0) / seg
        pos = 0.0
        while pos < seg:
            run = min(dash, seg - pos)
            d.line((x0 + ux * pos, y0 + uy * pos, x0 + ux * (pos + run), y0 + uy * (pos + run)), fill=fill, width=width)
            pos += dash + gap

    # --- the scene ----------------------------------------------------------
    def draw_panel(self, layer: Image.Image, idx: int, t: float, ref_alpha: float) -> dict:
        man = self.man
        d = ImageDraw.Draw(layer)
        pull = self.ev["pulls"][idx]
        table_y = man["panel_tables"][idx]
        x0 = self.x0s[idx]
        k, tau = self.phase(t)
        tt, ga, pulling = self.group_state(tau)
        x_m = float(np.interp(tt, pull["ts"], pull["xs"]))
        Rpx, rpx = self.R * self.ppm, self.r * self.ppm
        cx, cy = x0 + x_m * self.ppm, table_y - Rpx
        th = math.radians(pull["theta_deg"])
        s, c = math.sin(th), math.cos(th)
        L = self.L
        # The table, the start tick and the displacement bar under the table.
        d.rectangle((*L(TABLE_X0, table_y), *L(TABLE_X1, table_y + 12)), fill=DECK_B)
        d.line((*L(TABLE_X0, table_y), *L(TABLE_X1, table_y)), fill=RIM, width=3 * SS)
        d.line((*L(x0, table_y - 8), *L(x0, table_y + 32)), fill=blend(MUTED, 0.8), width=2 * SS)
        col = TEAL if x_m > 0 else CORAL
        # The moving group (bar, spool, string, hand, string line, touch point) is drawn on its own
        # RGBA overlay and composited over the table at the group alpha, so a fading group never
        # paints background-coloured shapes over the table.
        ov = Image.new("RGBA", layer.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        ga_draw, ga = ga, 1.0
        if abs(x_m) >= READ_MIN_M:
            d.line((*L(x0, table_y + 24), *L(cx, table_y + 24)), fill=blend(col, ga), width=6 * SS)
        # The wheel with six spokes and a rim dot, turned by -x / R (clockwise when rolling right).
        self.circle(d, *L(cx, cy), Rpx * SS, fill=blend(DECK_B, ga), outline=blend(RIM, ga), width=3 * SS)
        ang0 = -x_m / self.R
        for j in range(6):
            a = ang0 + j * math.pi / 3.0
            p0 = L(cx + (rpx + 6) * math.cos(a), cy - (rpx + 6) * math.sin(a))
            p1 = L(cx + (Rpx - 5) * math.cos(a), cy - (Rpx - 5) * math.sin(a))
            d.line((*p0, *p1), fill=blend(MUTED, 0.75 * ga), width=3 * SS)
        self.circle(d, *L(cx + (Rpx - 12) * math.cos(ang0), cy - (Rpx - 12) * math.sin(ang0)), 6 * SS,
                    fill=blend(WHITE, 0.8 * ga))
        # The axle with the wound string as its rim.
        self.circle(d, *L(cx, cy), rpx * SS, fill=blend(DECK_A, ga), outline=blend(WHITE, 0.6 * ga), width=4 * SS)
        # The tangent point T at the bottom of the axle, the string line to the table (dashed, gold) and
        # its meeting tick, the free string to the hand (white) and the pull arrow while pulling.
        Tx, Ty = cx + rpx * s, cy + rpx * c
        Ld = (table_y - Ty) / s
        Mx = Tx - Ld * c
        self.dashed(d, L(Tx, Ty), L(Mx, table_y), blend(GOLD, 0.9 * ga), 3 * SS, 9 * SS, 8 * SS)
        d.line((*L(Mx, table_y - 12), *L(Mx, table_y + 12)), fill=blend(GOLD, ga), width=4 * SS)
        Ls = man["string_m"] * self.ppm
        Hx, Hy = Tx + Ls * c, Ty - Ls * s
        d.line((*L(Tx, Ty), *L(Hx, Hy)), fill=blend(WHITE, ga), width=3 * SS)
        if pulling:
            tip = (Hx + 34 * c, Hy - 34 * s)
            base = (Hx + 16 * c, Hy - 16 * s)
            px_, py_ = -s, -c    # perpendicular to the string on screen
            d.polygon([L(*tip), L(base[0] + 9 * px_, base[1] + 9 * py_), L(base[0] - 9 * px_, base[1] - 9 * py_)],
                      fill=blend(WHITE, 0.9 * ga))
        self.circle(d, *L(Hx, Hy), 13 * SS, fill=blend(WHITE, 0.9 * ga), outline=blend(MUTED, ga), width=2 * SS)
        # The 60-degree reference line through P, tangent to the axle (payoff only).
        if ref_alpha > 0.0:
            sw = math.radians(self.ev["switch_deg"])
            self.dashed(d, L(cx, table_y), L(cx + REF_LEN_PX * math.cos(sw), table_y - REF_LEN_PX * math.sin(sw)),
                        blend(GOLD, 0.7 * ref_alpha * ga), 3 * SS, 4 * SS, 6 * SS)
        # The touch point P.
        self.circle(d, *L(cx, table_y), 7 * SS, fill=blend(WHITE, ga), outline=blend(BG, ga), width=2 * SS)
        if ga_draw > 0.0:
            if ga_draw < 1.0:
                ov.putalpha(ov.getchannel("A").point(lambda a: int(round(a * ga_draw))))
            layer.paste(ov, (0, 0), ov)
        ga = ga_draw
        # The hand tag sits beyond the pull arrow along the string, clear of the arrow head.
        tag = (Hx + 62 * c, Hy - 62 * s)
        return {"k": k, "tau": tau, "tt": tt, "ga": ga, "pulling": pulling, "x_m": x_m, "hand": (Hx, Hy), "tag": tag,
                "P": (cx, table_y), "col": col}

    def draw_text(self, d: ImageDraw.ImageDraw, states: list[dict], t: float, hud_alpha: float, ref_alpha: float) -> None:
        man, ev = self.man, self.ev
        for idx, st in enumerate(states):
            row = man["panel_rows"][idx]
            d.text((ROW_X0, row), label_text(ev["pulls"][idx]["theta_deg"]), font=self.font, fill=TEXT, anchor="lm")
            if abs(st["x_m"]) >= READ_MIN_M and st["ga"] > 0.0:
                d.text((READ_X, row), readout_text(st["x_m"]), font=self.font, fill=blend(st["col"], st["ga"]), anchor="rm")
            hx, hy = st["tag"]
            d.text((hx, hy), "hand", font=self.font_small, fill=blend(TEXT, st["ga"]), anchor="mm")
            if ref_alpha > 0.0:
                px_, py_ = st["P"]
                d.text((px_, py_ + 58), switch_tag(ev), font=self.font_small, fill=blend(GOLD, ref_alpha * st["ga"]), anchor="mm")
        if hud_alpha > 0.02:
            st = states[0]
            d.text((W / 2, COUNTER_Y), counter_text(st["k"], ev["n_pulls"], st["tt"]), font=self.font,
                   fill=blend(TEXT, hud_alpha), anchor="mm")
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
        ref_alpha = min(1.0, (t - man["payoff_t"]) / man["payoff_hold"]) * hud_alpha if t >= man["payoff_t"] else 0.0
        img = Image.new("RGB", (W, H), BG)
        layer = Image.new("RGB", (W * SS, (GEOM_Y1 - GEOM_Y0) * SS), BG)
        states = [self.draw_panel(layer, idx, t, ref_alpha) for idx in range(len(man["angles_deg"]))]
        img.paste(layer.reduce(SS), (0, GEOM_Y0))
        d = ImageDraw.Draw(img)
        self.draw_text(d, states, t, hud_alpha, ref_alpha)
        if title_alpha > 0.0:
            for j, line in enumerate(man["title"].split("|")):
                d.text((W / 2, TITLE_Y + j * TITLE_STEP), line, font=self.font_title, fill=blend(TEXT, title_alpha), anchor="mm")
        if ref_alpha > 0.0:
            for j, line in enumerate(payoff_lines(man, self.ev)):
                d.text((W / 2, PAYOFF_Y + j * PAYOFF_STEP), line, font=self.font, fill=blend(GOLD, ref_alpha), anchor="mm")
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
    man = json.loads((ROOT / "projects/spool/manifest.json").read_text())
    ev = measure(man)
    if "--measure-only" in sys.argv:
        return
    if "--frames" in sys.argv:
        times = [float(v) for v in sys.argv[sys.argv.index("--frames") + 1].split(",")]
        r = Renderer(man, ev)
        (ROOT / "media/spool").mkdir(parents=True, exist_ok=True)
        for tv in times:
            Image.fromarray(r.frame_at(int(round(tv * man["fps"])))).save(ROOT / f"media/spool/smoke-{tv}.png")
        print("smoke frames: " + ", ".join(f"{tv}" for tv in times))
        return
    Renderer(man, ev).render(ROOT / "media/spool/footage.mp4")


if __name__ == "__main__":
    main()
