#!/usr/bin/env python3
"""Bead on a spinning hoop: spin the hoop. Where does the bead settle?

A bead slides on a vertical hoop of radius R that spins about its
vertical diameter. Two hoops: the slow one spins up to 60 turns a
minute, the fast one to 100. theta is the bead's angle from the bottom
of the hoop, omega(t) the spin rate:

    theta'' = (omega(t)^2 cos theta - g / R) sin theta - c theta'

integrated with RK4 at a fixed step. Both hoops start at rest with the
bead 2 degrees off the bottom; from 1 s the spin rate ramps linearly
over 6 s to each hoop's target; the fast hoop passes the tipping rate
sqrt(g / R) on the way, the slow one never reaches it. At 22 s both
beads get the same nudge (25 degrees added to theta instantly) and come
back. Deterministic, no seed.

Measured and printed: the tipping rate in rad/s and rpm and when the
fast hoop crosses it; the closed form rest angle arccos(g / (omega^2 R))
at 100 rpm and at 134 rpm; the angle each bead holds at the end, the
settling times, the spin rate and video time at which the fast bead
lifts off (theta past 5 degrees) and first reaches its rest angle, its
overshoot, the slow bead's largest excursion after the ramp, the nudge
recovery times and swings, the small-oscillation rates about each rest
angle (closed form and measured), a 134 rpm run, a half-step check and
the on-screen text widths.

usage: hoopbead.py [--measure-only] [--frames t1,t2,...]
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
GHOST = (30, 36, 44)

# Layout: overlay at y 96 (captions.py), title rows at y 190/252/314 for
# the first seconds, two hoops centred at x 540 (slow on top, fast below)
# with their labels in the top corners of each panel, captions at
# caption_y 0.75 (y 1440..1520), payoff card under them.
PANELS = {"slow": {"cy": 590.0, "colour": TEAL}, "fast": {"cy": 1160.0, "colour": CORAL}}
SS = 2  # supersampling of the geometry layer
GEOM_Y0, GEOM_Y1 = 336, 1436
PAYOFF_Y = 1592.0
BEAD_R = 16.0


def blend(col, a, base=BG):
    return tuple(int(round(c * a + b * (1 - a))) for c, b in zip(col, base))


def rpm_to_rad(rpm: float) -> float:
    return rpm * 2.0 * math.pi / 60.0


def rad_to_rpm(w: float) -> float:
    return w * 60.0 / (2.0 * math.pi)


def spin_rate(man: dict, target_rpm: float, t: float) -> float:
    w = rpm_to_rad(target_rpm)
    t0, d = man["ramp_start_s"], man["ramp_duration_s"]
    if t <= t0:
        return 0.0
    if t >= t0 + d:
        return w
    return w * (t - t0) / d


def spin_angle(man: dict, target_rpm: float, t: float) -> float:
    w = rpm_to_rad(target_rpm)
    t0, d = man["ramp_start_s"], man["ramp_duration_s"]
    if t <= t0:
        return 0.0
    if t >= t0 + d:
        return 0.5 * w * d + w * (t - t0 - d)
    return 0.5 * w * (t - t0) ** 2 / d


def simulate(man: dict, target_rpm: float, duration: float, substeps: int, nudge: bool = True,
             damping: float | None = None) -> dict:
    """Per-step theta (rad from the bottom) and theta' of one bead."""
    g, R = man["g"], man["hoop_radius_m"]
    c = man["damping_per_s"] if damping is None else damping
    steps = man["fps"] * substeps
    dt = 1.0 / steps
    n = int(round(duration * steps))
    theta = np.empty(n + 1)
    th, w = math.radians(man["theta0_deg"]), 0.0
    nudge_step = int(round(man["nudge_t"] * steps)) if nudge else -1
    dth = math.radians(man["nudge_deg"])

    def deriv(t: float, th: float, w: float) -> tuple[float, float]:
        om = spin_rate(man, target_rpm, t)
        return w, (om * om * math.cos(th) - g / R) * math.sin(th) - c * w

    for i in range(n + 1):
        t = i * dt
        if i == nudge_step:
            th += dth if th >= 0.0 else -dth  # away from the bottom, on the bead's own side
        theta[i] = th
        if i == n:
            break
        k1 = deriv(t, th, w)
        k2 = deriv(t + 0.5 * dt, th + 0.5 * dt * k1[0], w + 0.5 * dt * k1[1])
        k3 = deriv(t + 0.5 * dt, th + 0.5 * dt * k2[0], w + 0.5 * dt * k2[1])
        k4 = deriv(t + dt, th + dt * k3[0], w + dt * k3[1])
        th += dt / 6.0 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0])
        w += dt / 6.0 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1])
    # The equation is symmetric in theta; u is theta with the side the bead
    # is on at the nudge taken as positive, so every measurement reads as
    # an angle away from the bottom.
    ref = nudge_step if nudge else n
    u = theta if theta[ref] >= 0.0 else -theta
    return {"theta": theta, "u": u, "dt": dt, "rpm": target_rpm, "nudge_step": nudge_step}


def settle_time(theta: np.ndarray, dt: float, final: float, tol: float, i0: int, i1: int) -> float:
    """First time from which |theta - final| stays under tol up to index i1."""
    out = np.nonzero(np.abs(theta[i0:i1] - final) >= tol)[0]
    return i0 * dt if len(out) == 0 else (i0 + out[-1] + 1) * dt


def first_above(theta: np.ndarray, dt: float, level: float, i0: int = 0) -> float | None:
    idx = np.nonzero(theta[i0:] > level)[0]
    return None if len(idx) == 0 else (i0 + idx[0]) * dt


def period_from_crossings(theta: np.ndarray, dt: float, final: float, i0: int, i1: int) -> float | None:
    s = np.sign(theta[i0:i1] - final)
    idx = np.nonzero(s[1:] * s[:-1] < 0)[0]
    return None if len(idx) < 3 else 2.0 * float(np.mean(np.diff(idx))) * dt


def rest_angle(man: dict, rpm: float) -> float | None:
    w = rpm_to_rad(rpm)
    q = man["g"] / (w * w * man["hoop_radius_m"])
    return None if q >= 1.0 else math.degrees(math.acos(q))


def measure(man: dict) -> dict:
    g, R, c = man["g"], man["hoop_radius_m"], man["damping_per_s"]
    fps, sub, dur = man["fps"], man["substeps"], man["scene_duration"]
    steps = fps * sub
    t0, d = man["ramp_start_s"], man["ramp_duration_s"]
    slow_rpm, fast_rpm = man["slow_rpm"], man["fast_rpm"]
    tol = math.radians(man["settle_tol_deg"])
    lift = math.radians(man["liftoff_deg"])
    print(f"setup: a bead on a vertical hoop of radius {R * 100:g} cm spinning about its vertical diameter, "
          f"g = {g:g} m/s^2, damping c = {c:g} per second; two hoops, both at rest with the bead "
          f"{man['theta0_deg']:g} degrees off the bottom, spin rate ramped linearly from {t0:g} s over {d:g} s to "
          f"{slow_rpm:g} rpm (slow) and {fast_rpm:g} rpm (fast); nudge: {man['nudge_deg']:g} degrees added to theta "
          f"instantly at {man['nudge_t']:g} s (theta' unchanged) on both beads; RK4 at {steps} steps per second "
          f"(dt = {1 / steps:.2e} s) for {dur:g} s; deterministic, no seed")
    w_tip = math.sqrt(g / R)
    rpm_tip = rad_to_rpm(w_tip)
    t_cross = t0 + d * w_tip / rpm_to_rad(fast_rpm)
    print(f"tipping rate sqrt(g / R) = {w_tip:.4f} rad/s = {rpm_tip:.2f} rpm; the fast hoop crosses it at "
          f"{t_cross:.3f} s of the ramp; the slow hoop's {slow_rpm:g} rpm is {slow_rpm / rpm_tip:.3f} of it "
          f"(g / (omega^2 R) = {g / (rpm_to_rad(slow_rpm) ** 2 * R):.4f} > 1, no rest angle above the bottom)")
    eq_fast = rest_angle(man, fast_rpm)
    eq_check = rest_angle(man, man["check_rpm"])
    print(f"closed form arccos(g / (omega^2 R)): {eq_fast:.2f} degrees at {fast_rpm:g} rpm "
          f"(omega = {rpm_to_rad(fast_rpm):.4f} rad/s); {eq_check:.2f} degrees at {man['check_rpm']:g} rpm")
    slow = simulate(man, slow_rpm, dur, sub)
    fast = simulate(man, fast_rpm, dur, sub)
    ns = slow["nudge_step"]
    n_end = len(slow["theta"]) - 1
    i_ramp_end = int(round((t0 + d) * steps))
    dt = slow["dt"]
    out = {"slow": slow, "fast": fast, "eq_fast": eq_fast, "w_tip": w_tip, "rpm_tip": rpm_tip, "t_cross": t_cross}
    for name, run in (("slow", slow), ("fast", fast)):
        th = run["u"]
        final = float(th[-1])
        run["final_deg"] = math.degrees(final)
        run["settle_t"] = settle_time(th, dt, final, tol, 0, ns)
        run["recover_t"] = settle_time(th, dt, final, tol, ns, n_end + 1)
        out[name + "_final"] = run["final_deg"]
    th = fast["u"]
    lift_t = first_above(th, dt, lift, int(t0 * steps))
    fast["lift_t"] = lift_t
    reach_t = first_above(th, dt, math.radians(eq_fast), int(t0 * steps))
    fast["reach_t"] = reach_t
    seg = th[int(lift_t / dt):ns]
    over_i = int(np.argmax(seg))
    print(f"fast bead ({fast_rpm:g} rpm): lifts off (theta past {man['liftoff_deg']:g} degrees) at {lift_t:.3f} s "
          f"with the hoop at {rad_to_rpm(spin_rate(man, fast_rpm, lift_t)):.1f} rpm, {lift_t - t_cross:.3f} s after "
          f"the tipping rate; first reaches its rest angle {eq_fast:.2f} degrees at {reach_t:.3f} s; overshoots to "
          f"{math.degrees(seg[over_i]):.2f} degrees at {lift_t + over_i * dt:.3f} s; stays within "
          f"{man['settle_tol_deg']:g} degrees of its final angle from {fast['settle_t']:.3f} s; holds "
          f"{fast['final_deg']:.2f} degrees at {dur:g} s ({fast['final_deg'] - eq_fast:+.3f} against the closed form); "
          f"angle at {man['nudge_t']:g} s just before the nudge {math.degrees(th[ns - 1]):.2f} degrees; it lifted off on the "
          f"{'right' if fast['theta'][ns] >= 0 else 'left'} half of the hoop (the side its residual swing was on)")
    th = slow["u"]
    seg = np.abs(th[i_ramp_end:ns])
    ex_i = int(np.argmax(seg))
    print(f"slow bead ({slow_rpm:g} rpm): angle at the end of the ramp ({t0 + d:g} s) {math.degrees(th[i_ramp_end]):.3f} "
          f"degrees; largest excursion after the ramp and before the nudge {math.degrees(seg[ex_i]):.3f} degrees at "
          f"{(i_ramp_end + ex_i) * dt:.2f} s; largest angle over the whole ramp {math.degrees(np.abs(th[:i_ramp_end]).max()):.3f} "
          f"degrees; within {man['settle_tol_deg']:g} degrees of the bottom from {slow['settle_t']:.3f} s; holds "
          f"{slow['final_deg']:.3f} degrees at {dur:g} s")
    for name, run in (("slow", slow), ("fast", fast)):
        th = run["u"]
        after = th[ns:]
        lo_i = int(np.argmin(after))
        final = math.radians(run["final_deg"])
        far = np.abs(after - final)
        print(f"nudge on the {name} bead: from {math.degrees(th[ns - 1]):.2f} to {math.degrees(th[ns]):.2f} degrees at "
              f"{man['nudge_t']:g} s; swings back through its rest angle to {math.degrees(after[lo_i]):.2f} degrees at "
              f"{man['nudge_t'] + lo_i * dt:.2f} s; within 5 degrees of its final angle from "
              f"{man['nudge_t'] + float(np.nonzero(far >= math.radians(5))[0][-1] + 1) * dt:.2f} s, within "
              f"{man['settle_tol_deg']:g} degrees from {run['recover_t']:.3f} s ({run['recover_t'] - man['nudge_t']:.2f} s after the nudge)")
    # Small oscillations about each rest angle.
    w_slow, w_fast = rpm_to_rad(slow_rpm), rpm_to_rad(fast_rpm)
    k_slow = math.sqrt(g / R - w_slow * w_slow)
    k_fast = w_fast * math.sin(math.radians(eq_fast))
    for name, run, k in (("slow", slow, k_slow), ("fast", fast, k_fast)):
        kd = math.sqrt(k * k - c * c / 4.0)
        i0 = int((man["nudge_t"] + 3.0) * steps)
        i1 = int((man["nudge_t"] + 11.0) * steps)
        meas_p = period_from_crossings(run["u"], dt, math.radians(run["final_deg"]), i0, i1)
        print(f"small swings about the {name} bead's rest angle: closed form {k:.3f} rad/s = {k / (2 * math.pi):.3f} Hz "
              f"(period {2 * math.pi / k:.3f} s, damped period {2 * math.pi / kd:.3f} s), amplitude halves every "
              f"{2 * math.log(2) / c:.2f} s; measured period after the nudge {meas_p:.3f} s")
    check = simulate(man, man["check_rpm"], dur, sub)
    ck_lift = first_above(check["u"], dt, lift, int(t0 * steps))
    print(f"check at {man['check_rpm']:g} rpm (not drawn): holds {math.degrees(check['u'][-1]):.2f} degrees at "
          f"{dur:g} s against the closed form {eq_check:.2f}; lifts off at {ck_lift:.3f} s")
    half = simulate(man, fast_rpm, dur, 2 * sub)
    h_lift = first_above(half["u"], half["dt"], lift, int(t0 * steps * 2))
    h_final = math.degrees(half["u"][-1])
    h_settle = settle_time(half["u"], half["dt"], half["u"][-1], tol, 0, half["nudge_step"])
    print(f"check at half the time step ({2 * steps} steps per second): the fast bead lifts off at {h_lift:.3f} s, "
          f"settles from {h_settle:.3f} s and holds {h_final:.2f} degrees at {dur:g} s "
          f"({h_final - fast['final_deg']:+.4f} against the full step)")
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
        self.Rpx = float(man["hoop_radius_px"])
        widths = {"overlay@34": (ImageFont.truetype(font, 34), man["overlay"])}
        for j, line in enumerate(man["title"].split("|")):
            widths[f"title line {j + 1}@56"] = (self.font_title, line)
        widths["label@40"] = (self.font, "slow hoop")
        widths["target@28"] = (self.font_small, f"spins up to {man['fast_rpm']:g} turns a minute")
        widths["readout unit@28"] = (self.font_small, "turns a minute")
        widths["readout number@48"] = (self.font_num, f"{man['fast_rpm']:.0f}")
        widths["angle@36"] = (self.font_read, "88.4 deg")
        widths["status@32"] = (self.font_status, "at the bottom")
        for j, line in enumerate(self.payoff_lines()):
            widths[f"payoff line {j + 1}@40"] = (self.font, line)
        print("text widths: " + ", ".join(f"{k} {f.getlength(s):.0f} px" for k, (f, s) in widths.items()))
        fast = meas["fast"]
        print(f"video: real time; hoops at rest until {man['ramp_start_s']:g} s, ramp to {man['ramp_start_s'] + man['ramp_duration_s']:g} s; "
              f"the fast hoop passes the tipping rate at {meas['t_cross']:.2f} s, its bead lifts off at {fast['lift_t']:.2f} s, "
              f"reaches {meas['eq_fast']:.1f} degrees at {fast['reach_t']:.2f} s and holds from {fast['settle_t']:.2f} s; "
              f"nudge at {man['nudge_t']:g} s, both back within {man['settle_tol_deg']:g} degrees by "
              f"{max(meas['slow']['recover_t'], fast['recover_t']):.2f} s; payoff card at {man['payoff_t']:g} s")

    def payoff_lines(self) -> list[str]:
        text = self.man["payoff_text"].format(fast=self.meas["fast_final"], slow=self.meas["slow_final"])
        return [s.strip() for s in text.split("|")]

    def draw_hoop(self, d: ImageDraw.ImageDraw, name: str, theta: float, phi: float) -> None:
        p = PANELS[name]
        col = p["colour"]
        cx, cy = W / 2 * SS, (p["cy"] - GEOM_Y0) * SS
        Rp = self.Rpx * SS
        d.ellipse((cx - Rp, cy - Rp, cx + Rp, cy + Rp), outline=GHOST, width=2 * SS)
        d.line((cx, cy - Rp - 26 * SS, cx, cy + Rp + 6 * SS), fill=WIRE, width=4 * SS)
        d.rectangle((cx - 70 * SS, cy + Rp + 6 * SS, cx + 70 * SS, cy + Rp + 18 * SS), fill=WIRE)
        n = 240
        a = np.linspace(0.0, 2.0 * math.pi, n + 1)
        x = cx + Rp * np.sin(a) * math.cos(phi)
        y = cy + Rp * np.cos(a)
        z = np.sin(a) * math.sin(phi)
        zm = 0.5 * (z[1:] + z[:-1])
        runs: list[tuple[bool, list]] = []
        for k in range(n):
            back = zm[k] > 1e-9
            pt = [(float(x[k]), float(y[k])), (float(x[k + 1]), float(y[k + 1]))]
            if runs and runs[-1][0] == back:
                runs[-1][1].append(pt[1])
            else:
                runs.append((back, pt))
        xb = cx + Rp * math.sin(theta) * math.cos(phi)
        yb = cy + Rp * math.cos(theta)
        zb = math.sin(theta) * math.sin(phi)

        def bead() -> None:
            dim = 1.0 - 0.35 * max(0.0, zb)
            r = BEAD_R * SS
            d.ellipse((xb - r, yb - r, xb + r, yb + r), fill=blend(GOLD, dim), outline=blend((120, 84, 30), dim), width=SS)
            hr = r * 0.32
            d.ellipse((xb - r * 0.45 - hr, yb - r * 0.45 - hr, xb - r * 0.45 + hr, yb - r * 0.45 + hr), fill=blend(WHITE, dim))

        for back, pts in runs:
            if back:
                d.line(pts, fill=blend(col, 0.42), width=3 * SS, joint="curve")
        if zb > 0:
            bead()
        for back, pts in runs:
            if not back:
                d.line(pts, fill=col, width=7 * SS, joint="curve")
        if zb <= 0:
            bead()

    def status(self, name: str, t: float) -> tuple[str, tuple]:
        man, run = self.man, self.meas[name]
        col = PANELS[name]["colour"]
        nt = man["nudge_t"]
        if nt - 0.2 <= t < nt + 1.2:
            return "nudge", GOLD
        if name == "fast":
            if t >= run["recover_t"] or run["settle_t"] <= t < nt - 0.2:
                return "holds", col
            if run["lift_t"] <= t < run["lift_t"] + 2.0:
                return "lifts off", col
            return "", col
        if t >= run["recover_t"] or run["settle_t"] + 0.5 <= t < nt - 0.2:
            return "at the bottom", col
        return "", col

    def draw_scene(self, t: float, title_on: bool) -> Image.Image:
        man, meas = self.man, self.meas
        img = Image.new("RGB", (W, H), BG)
        layer = Image.new("RGB", (W * SS, (GEOM_Y1 - GEOM_Y0) * SS), BG)
        ld = ImageDraw.Draw(layer)
        state = {}
        for name in PANELS:
            run = meas[name]
            i = min(int(round(t / run["dt"])), len(run["theta"]) - 1)
            theta = float(run["theta"][i])
            phi = spin_angle(man, run["rpm"], t)
            state[name] = (theta, phi)
            self.draw_hoop(ld, name, theta, phi)
        img.paste(layer.reduce(SS), (0, GEOM_Y0))
        d = ImageDraw.Draw(img)
        for name, p in PANELS.items():
            run = meas[name]
            col = p["colour"]
            theta, _ = state[name]
            cx, cy = W / 2, p["cy"]
            top = cy - self.Rpx
            rpm_now = rad_to_rpm(spin_rate(man, run["rpm"], t))
            d.text((40, top + 20), f"{name} hoop", font=self.font, fill=col, anchor="lm")
            d.text((40, top + 64), f"spins up to {run['rpm']:g} turns a minute", font=self.font_small, fill=MUTED, anchor="lm")
            d.text((W - 40, top + 16), "turns a minute", font=self.font_small, fill=MUTED, anchor="rm")
            d.text((W - 40, top + 64), f"{rpm_now:.0f}", font=self.font_num,
                   fill=col if rpm_now >= run["rpm"] - 1e-9 else TEXT, anchor="rm")
            ly = cy + self.Rpx * math.cos(theta)
            word, wcol = self.status(name, t)
            line_col = GOLD if word == "nudge" else blend(col, 0.55)
            d.line((cx - self.Rpx - 24, ly, cx + self.Rpx + 24, ly), fill=line_col, width=2)
            d.text((cx + self.Rpx + 36, ly), f"{abs(math.degrees(theta)):.1f} deg", font=self.font_read, fill=TEXT, anchor="lm")
            if word:
                d.text((cx - self.Rpx - 36, ly), word, font=self.font_status, fill=wcol, anchor="rm")
        return img

    def live_frame(self, f: int) -> np.ndarray:
        man = self.man
        t = f / self.fps
        title_on = t < man["title_until"]
        img = self.draw_scene(t, title_on)
        d = ImageDraw.Draw(img)
        if title_on:
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
    man = json.loads((ROOT / "projects/hoopbead/manifest.json").read_text())
    meas = measure(man)
    if "--measure-only" in sys.argv:
        return
    if "--frames" in sys.argv:
        times = [float(v) for v in sys.argv[sys.argv.index("--frames") + 1].split(",")]
        r = Renderer(man, meas)
        for tv in times:
            Image.fromarray(r.frame_at(int(round(tv * man["fps"])))).save(ROOT / f"media/hoopbead/smoke-{tv}.png")
        print("smoke frames: " + ", ".join(f"{tv}" for tv in times))
        return
    Renderer(man, meas).render(ROOT / "media/hoopbead/footage.mp4")


if __name__ == "__main__":
    main()
