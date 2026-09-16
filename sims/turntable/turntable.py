#!/usr/bin/env python3
"""Turntable ball: push a ball across a spinning record. Where does it go?

A record turns at 33 1/3 rpm. A solid ball is pushed from the centre at
a set speed and rolls without slipping; a puck with no grip is given the
same push and slides. The ball's centre, velocity and spin vector are
integrated with RK4 under the rolling constraint: the contact point of
the ball moves with the record, the friction force at the contact is
whatever keeps it so, and that force also torques the ball. The no-slip
residual is checked every step. Deterministic, no seed.

Measured and printed: the ball's loop time (its return to the start,
interpolated, and the time its velocity turns through a full circle) in
seconds and in record turns against the closed form (1 + k) / k turns
for a ball with moment of inertia k m r^2; the circle's radius and its
farthest point from the record's centre; the no-slip residual; the
number of loops in the video; the puck's exit time; the same for a
hollow ball (k = 2/3); and checks with a different push, half the time
step, and the closed-form radius v / (k Omega / (1 + k)).

usage: turntable.py [--measure-only] [--frames t1,t2,...]
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
VINYL = (24, 28, 34)
GROOVE = (38, 44, 52)
LABEL = (60, 52, 72)
LABEL_MARK = (150, 130, 170)

# Layout: overlay at y 96 (captions.py), title at y 190/252/314 for the
# first seconds, the counters at y 236 after it, the record centred at
# record_centre_px, captions at caption_y 0.75 (y 1440..1510), payoff
# under the captions.
COUNTER_Y = 236
PAYOFF_Y = 1592.0


def rk4(state: np.ndarray, dt: float, deriv) -> np.ndarray:
    k1 = deriv(state)
    k2 = deriv(state + 0.5 * dt * k1)
    k3 = deriv(state + 0.5 * dt * k2)
    k4 = deriv(state + dt * k3)
    return state + dt / 6.0 * (k1 + 2 * k2 + 2 * k3 + k4)


class Ball:
    """State [x, y, vx, vy, wx, wy, wz] of a ball rolling on the turning record."""

    def __init__(self, omega: float, r: float, k: float, x0: np.ndarray, v0: np.ndarray):
        self.omega, self.r, self.k = omega, r, k
        self.c = k / (1.0 + k)
        # Spin from the no-slip condition at the start: v + w x (-r z) = Omega z x x.
        wx = (omega * x0[0] - v0[1]) / r
        wy = (v0[0] + omega * x0[1]) / r
        self.state = np.array([x0[0], x0[1], v0[0], v0[1], wx, wy, 0.0])

    def deriv(self, s: np.ndarray) -> np.ndarray:
        # Friction keeps the contact point on the record: a = c Omega z x v.
        ax = -self.c * self.omega * s[3]
        ay = self.c * self.omega * s[2]
        # The same force torques the ball about its centre: dw/dt = (-r z) x F / I.
        dwx = ay / (self.k * self.r)
        dwy = -ax / (self.k * self.r)
        return np.array([s[2], s[3], ax, ay, dwx, dwy, 0.0])

    def slip(self, s: np.ndarray) -> float:
        cx = s[2] - self.r * s[5] + self.omega * s[1]
        cy = s[3] + self.r * s[4] - self.omega * s[0]
        return math.hypot(cx, cy)


def run_ball(man: dict, k: float, speed: float, direction_deg: float, substeps: int, t_end: float) -> dict:
    omega = man["rpm"] * 2.0 * math.pi / 60.0
    r = man["ball_radius_m"]
    fps = man["fps"]
    dt = 1.0 / (fps * substeps)
    v0 = speed * np.array([math.cos(math.radians(direction_deg)), math.sin(math.radians(direction_deg))])
    b = Ball(omega, r, k, np.zeros(2), v0)
    n = int(round(t_end * fps))
    frames = np.empty((n + 1, 7))
    frames[0] = b.state
    slip_max = 0.0
    s = b.state
    # Fine record for the return time and the velocity angle.
    times, dist, angle = [0.0], [0.0], [math.atan2(v0[1], v0[0])]
    unwrapped = angle[0]
    for f in range(1, n + 1):
        for _ in range(substeps):
            s = rk4(s, dt, b.deriv)
            slip_max = max(slip_max, b.slip(s))
            t = times[-1] + dt
            times.append(t)
            dist.append(math.hypot(s[0], s[1]))
            a = math.atan2(s[3], s[2])
            da = (a - angle[-1] + math.pi) % (2 * math.pi) - math.pi
            unwrapped += da
            angle.append(a)
        frames[f] = s
    times_a, dist_a = np.array(times), np.array(dist)
    # First return to the start: the first local minimum of the distance after leaving.
    left = np.argmax(dist_a > 0.5 * dist_a.max())
    i = left + int(np.argmin(dist_a[left:]))
    # Parabolic interpolation of the minimum.
    if 0 < i < len(dist_a) - 1:
        y0, y1, y2 = dist_a[i - 1], dist_a[i], dist_a[i + 1]
        denom = y0 - 2 * y1 + y2
        off = 0.5 * (y0 - y2) / denom if denom != 0 else 0.0
        t_return = times_a[i] + off * dt
        d_return = y1 - 0.25 * (y0 - y2) * off
    else:
        t_return, d_return = times_a[i], dist_a[i]
    # Velocity turning through a full circle: unwrapped angle reaches 2 pi.
    t_turn = 2.0 * math.pi / (b.c * omega)  # closed form; the measured version below
    ang = np.array(angle)
    dang = (np.diff(ang) + math.pi) % (2 * math.pi) - math.pi
    cum = np.concatenate([[0.0], np.cumsum(dang)])
    j = int(np.argmax(np.abs(cum) >= 2.0 * math.pi))
    if j > 0:
        frac = (2.0 * math.pi - abs(cum[j - 1])) / (abs(cum[j]) - abs(cum[j - 1]))
        t_turn_meas = times_a[j - 1] + frac * dt
    else:
        t_turn_meas = float("nan")
    radius = 0.5 * float(dist_a.max())
    return {"frames": frames, "t_return": t_return, "d_return": d_return, "t_turn": t_turn_meas,
            "t_turn_closed": t_turn, "radius": radius, "far": float(dist_a.max()), "slip_max": slip_max,
            "omega": omega, "c": b.c, "k": k, "speed": speed}


def measure(man: dict) -> dict:
    omega = man["rpm"] * 2.0 * math.pi / 60.0
    t_table = 60.0 / man["rpm"]
    R, r = man["record_radius_m"], man["ball_radius_m"]
    k = man["inertia_factor"]
    v = man["push_m_per_s"]
    dur = man["scene_duration"]
    print(f"setup: record of radius {R * 100:g} cm turning at {man['rpm']:.4g} rpm ({t_table:.3f} s per turn, "
          f"Omega = {omega:.4f} rad/s); a solid ball of radius {r * 100:g} cm (I = {k:g} m r^2) pushed from the "
          f"centre at {v * 100:g} cm/s and rolling without slipping; a puck with no grip given the same push; "
          f"RK4 at {man['substeps']} steps per frame (dt = {1 / (man['fps'] * man['substeps']):.2e} s) for "
          f"{dur:g} s = {dur / t_table:.2f} turns of the record; deterministic, no seed")
    ball = run_ball(man, k, v, man["push_dir_deg"], man["substeps"], dur)
    closed_turns = (1.0 + k) / k
    print(f"ball: back at the start after {ball['t_return']:.4f} s = {ball['t_return'] / t_table:.4f} turns of the "
          f"record (closest approach {ball['d_return'] * 1e6:.2f} um); its velocity turns a full circle in "
          f"{ball['t_turn']:.4f} s = {ball['t_turn'] / t_table:.4f} turns; closed form (1 + k) / k = "
          f"{closed_turns:.4f} turns = {closed_turns * t_table:.4f} s; the path is a circle of radius "
          f"{ball['radius'] * 100:.3f} cm (closed form v / (c Omega) = {v / (ball['c'] * omega) * 100:.3f} cm) "
          f"reaching {ball['far'] * 100:.2f} cm from the record's centre, {(R - ball['far'] - r) * 100:.1f} cm "
          f"inside the edge; no-slip residual under {ball['slip_max']:.1e} m/s; {dur / ball['t_return']:.3f} "
          f"loops in the video")
    t_puck = R / v
    print(f"puck: with no grip it slides straight at {v * 100:g} cm/s and its centre passes the edge at "
          f"{t_puck:.2f} s, {t_puck / t_table:.2f} turns of the record")
    hollow = run_ball(man, man["hollow_inertia_factor"], v, man["push_dir_deg"], man["substeps"], 12.0)
    kh = man["hollow_inertia_factor"]
    print(f"hollow ball (I = {kh:.4g} m r^2, not drawn): back at the start after {hollow['t_return']:.4f} s = "
          f"{hollow['t_return'] / t_table:.4f} turns (closed form {(1 + kh) / kh:.4f}); circle radius "
          f"{hollow['radius'] * 100:.3f} cm")
    other = run_ball(man, k, man["check_push_m_per_s"], man["check_push_dir_deg"], man["substeps"], 8.0)
    half = run_ball(man, k, v, man["push_dir_deg"], 2 * man["substeps"], 8.0)
    print(f"checks: pushed at {man['check_push_m_per_s'] * 100:g} cm/s toward {man['check_push_dir_deg']:g} degrees "
          f"the ball is back after {other['t_return']:.4f} s = {other['t_return'] / t_table:.4f} turns on a circle "
          f"of radius {other['radius'] * 100:.3f} cm; at half the time step the return is at {half['t_return']:.4f} s")
    return {"ball": ball, "t_puck": t_puck, "t_table": t_table, "hollow": hollow, "omega": omega}


class Renderer:
    def __init__(self, man: dict, meas: dict):
        self.man, self.meas = man, meas
        self.fps = man["fps"]
        font = os.environ["SEED_ZERO_FONT"]
        self.font = ImageFont.truetype(font, 40)
        self.font_small = ImageFont.truetype(font, 32)
        self.font_title = ImageFont.truetype(font, 56)
        self.font_tag = ImageFont.truetype(font, 28)
        self.first = None
        self.cx, self.cy = man["record_centre_px"]
        self.ppm = man["px_per_m"]
        self.R = man["record_radius_m"] * self.ppm
        self.r = man["ball_radius_m"] * self.ppm
        self.turns = meas["ball"]["t_return"] / meas["t_table"]
        widths = {"overlay@34": (ImageFont.truetype(font, 34), man["overlay"])}
        for j, line in enumerate(man["title"].split("|")):
            widths[f"title line {j + 1}@56"] = (self.font_title, line)
        widths["counter@40"] = (self.font, "record turns 21.00   ball loops 6")
        widths["tag ball@28"] = (self.font_tag, "ball, rolling")
        widths["tag puck@28"] = (self.font_tag, "puck, no grip: off the record at 3.0 s")
        for j, line in enumerate(self.payoff_lines()):
            widths[f"payoff line {j + 1}@40"] = (self.font, line)
        print("text widths: " + ", ".join(f"{k} {f.getlength(s):.0f} px" for k, (f, s) in widths.items()))
        print(f"video: real time; the puck leaves the record at {meas['t_puck']:.2f} s; the ball is back at the "
              f"centre every {meas['ball']['t_return']:.3f} s ({self.turns:.2f} turns), "
              f"{man['scene_duration'] / meas['ball']['t_return']:.2f} loops in {man['scene_duration']:g} s; "
              f"payoff card at {man['payoff_t']:g} s")

    def payoff_lines(self) -> list[str]:
        text = self.man["payoff_text"].format(turns=self.turns, puck=self.meas["t_puck"])
        return [s.strip() for s in text.split("|")]

    def to_px(self, x: float, y: float) -> tuple[float, float]:
        return self.cx + x * self.ppm, self.cy - y * self.ppm

    def draw_record(self, d: ImageDraw.ImageDraw, t: float) -> None:
        cx, cy, R = self.cx, self.cy, self.R
        d.ellipse((cx - R, cy - R, cx + R, cy + R), fill=VINYL, outline=WIRE, width=3)
        for g in np.linspace(0.40, 0.97, 14):
            rr = R * g
            d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), outline=GROOVE, width=1)
        # The label turns with the record: a disc with two opposite marks
        # (the pattern repeats every half turn) and a short radial line.
        phi = self.meas["omega"] * t
        rl = R * 0.34
        d.ellipse((cx - rl, cy - rl, cx + rl, cy + rl), fill=LABEL)
        for sgn in (1, -1):
            mx = cx + sgn * rl * 0.72 * math.cos(phi)
            my = cy - sgn * rl * 0.72 * math.sin(phi)
            d.ellipse((mx - 9, my - 9, mx + 9, my + 9), fill=LABEL_MARK)
        for sgn in (1, -1):
            ex = cx + sgn * R * 0.98 * math.cos(phi + math.pi / 2)
            ey = cy - sgn * R * 0.98 * math.sin(phi + math.pi / 2)
            sx = cx + sgn * R * 0.86 * math.cos(phi + math.pi / 2)
            sy = cy - sgn * R * 0.86 * math.sin(phi + math.pi / 2)
            d.line([(sx, sy), (ex, ey)], fill=LABEL_MARK, width=4)
        d.ellipse((cx - 6, cy - 6, cx + 6, cy + 6), fill=BG)

    def draw_scene(self, t: float, title_on: bool) -> Image.Image:
        man, meas = self.man, self.meas
        f = min(int(round(t * self.fps)), len(meas["ball"]["frames"]) - 1)
        img = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(img)
        self.draw_record(d, t)
        # The puck's straight path and the puck.
        v = man["push_m_per_s"]
        ang = math.radians(man["push_dir_deg"])
        px, py = v * t * math.cos(ang), v * t * math.sin(ang)
        p0 = self.to_px(0, 0)
        p1 = self.to_px(px, py)
        reach = min(math.hypot(px, py), man["record_radius_m"] + 0.012)
        d.line([p0, self.to_px(reach * math.cos(ang), reach * math.sin(ang))], fill=(50, 110, 92), width=3)
        rp = self.r
        if math.hypot(px, py) <= man["record_radius_m"] + 0.05:
            fade = 1.0 if math.hypot(px, py) <= man["record_radius_m"] else max(0.0, 1.0 - (math.hypot(px, py) - man["record_radius_m"]) / 0.05)
            col = tuple(int(TEAL[q] * fade + BG[q] * (1 - fade)) for q in range(3))
            d.ellipse((p1[0] - rp, p1[1] - rp, p1[0] + rp, p1[1] + rp), fill=col, outline=BG, width=2)
        # The ball's trail over the last loop, then the ball.
        fr = meas["ball"]["frames"]
        n_trail = int(round(meas["ball"]["t_return"] * self.fps))
        f0 = max(0, f - n_trail)
        pts = [self.to_px(fr[i, 0], fr[i, 1]) for i in range(f0, f + 1)]
        if len(pts) >= 2:
            for i in range(1, len(pts)):
                a = 0.25 + 0.75 * (i / len(pts))
                col = tuple(int(CORAL[q] * a + VINYL[q] * (1 - a)) for q in range(3))
                d.line([pts[i - 1], pts[i]], fill=col, width=4)
        bx, by = self.to_px(fr[f, 0], fr[f, 1])
        rb = self.r
        d.ellipse((bx - rb, by - rb, bx + rb, by + rb), fill=CORAL, outline=(120, 40, 34), width=2)
        d.ellipse((bx - rb * 0.45, by - rb * 0.55, bx - rb * 0.05, by - rb * 0.15), fill=(246, 160, 150))
        # Tags near the objects.
        d.text((bx, by - rb - 22), "ball, rolling", font=self.font_tag, fill=CORAL, anchor="mm")
        if math.hypot(px, py) <= man["record_radius_m"]:
            d.text((p1[0], p1[1] + rp + 22), "puck, no grip", font=self.font_tag, fill=TEAL, anchor="mm")
        else:
            d.text((W / 2, self.cy + self.R + 60), f"puck, no grip: off the record at {meas['t_puck']:.1f} s",
                   font=self.font_tag, fill=TEAL, anchor="mm")
        if not title_on:
            turns = t / meas["t_table"]
            loops = int(math.floor(t / meas["ball"]["t_return"] + 1e-6))
            d.text((W / 2, COUNTER_Y), f"record turns {turns:.2f}   ball loops {loops}", font=self.font,
                   fill=TEXT, anchor="mm")
        return img

    def live_frame(self, f: int) -> np.ndarray:
        man = self.man
        t = f / self.fps
        title_on = t < man["title_until"]
        img = self.draw_scene(t, title_on)
        d = ImageDraw.Draw(img)

        def shade_col(col, a):
            return tuple(int(c * a + BG[j] * (1 - a)) for j, c in enumerate(col))

        if title_on:
            a = 1.0 if t < man["title_until"] - 0.4 else (man["title_until"] - t) / 0.4
            for j, line in enumerate(man["title"].split("|")):
                d.text((W / 2, 190 + j * 62), line, font=self.font_title, fill=shade_col(TEXT, a), anchor="mm")
        if t >= man["payoff_t"]:
            a = min(1.0, (t - man["payoff_t"]) / man["payoff_hold"])
            for j, line in enumerate(self.payoff_lines()):
                d.text((W / 2, PAYOFF_Y + j * 56), line, font=self.font, fill=shade_col(GOLD, a), anchor="mm")
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
    man = json.loads((ROOT / "projects/turntable/manifest.json").read_text())
    meas = measure(man)
    if "--measure-only" in sys.argv:
        return
    if "--frames" in sys.argv:
        times = [float(v) for v in sys.argv[sys.argv.index("--frames") + 1].split(",")]
        r = Renderer(man, meas)
        for tv in times:
            Image.fromarray(r.frame_at(int(round(tv * man["fps"])))).save(ROOT / f"media/turntable/smoke-{tv}.png")
        print("smoke frames: " + ", ".join(f"{tv}" for tv in times))
        return
    Renderer(man, meas).render(ROOT / "media/turntable/footage.mp4")


if __name__ == "__main__":
    main()
