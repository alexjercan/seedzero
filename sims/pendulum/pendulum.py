#!/usr/bin/env python3
"""Double pendulum divergence: simulation, measurement, and footage.

Two identical frictionless double pendulums, released from the same angle
except for a difference of delta degrees on the first arm. RK4 integration
at a fixed step. The measured split times are what the narration quotes.

usage: pendulum.py [--measure-only] [--theta DEG]
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
COL_A = (92, 200, 165)
COL_B = (216, 222, 230)
MUTED = (138, 148, 163)

PIVOT = (540.0, 640.0)
SCALE = 270.0  # px per unit rod length
M1 = M2 = 1.0
L1 = L2 = 1.0
G = 9.81
TOTAL_L = L1 + L2

FPS_SUBSTEPS = 10
INTRO_HOLD = 2.0
RESET_GAP = 0.5
PAYOFF_HOLD = 5.0
TRAIL_FADE = 0.982

# Divergence thresholds in units of the full pendulum length.
SPLIT_FRAC = 0.1
FULL_FRAC = 1.0


def accel(state):
    t1, w1, t2, w2 = state
    d = t2 - t1
    cd, sd = math.cos(d), math.sin(d)
    den1 = (M1 + M2) * L1 - M2 * L1 * cd * cd
    a1 = (
        M2 * L1 * w1 * w1 * sd * cd
        + M2 * G * math.sin(t2) * cd
        + M2 * L2 * w2 * w2 * sd
        - (M1 + M2) * G * math.sin(t1)
    ) / den1
    den2 = (L2 / L1) * den1
    a2 = (
        -M2 * L2 * w2 * w2 * sd * cd
        + (M1 + M2) * (G * math.sin(t1) * cd - L1 * w1 * w1 * sd - G * math.sin(t2))
    ) / den2
    return np.array([w1, a1, w2, a2])


def rk4(state, dt):
    k1 = accel(state)
    k2 = accel(state + 0.5 * dt * k1)
    k3 = accel(state + 0.5 * dt * k2)
    k4 = accel(state + dt * k3)
    return state + dt / 6.0 * (k1 + 2 * k2 + 2 * k3 + k4)


def energy(state):
    t1, w1, t2, w2 = state
    v = (
        0.5 * (M1 + M2) * L1 * L1 * w1 * w1
        + M2 * L1 * L2 * w1 * w2 * math.cos(t1 - t2)
        + 0.5 * M2 * L2 * L2 * w2 * w2
    )
    u = -(M1 + M2) * G * L1 * math.cos(t1) - M2 * G * L2 * math.cos(t2)
    return v + u


def tip(state):
    t1, _, t2, _ = state
    return (
        L1 * math.sin(t1) + L2 * math.sin(t2),
        L1 * math.cos(t1) + L2 * math.cos(t2),
    )


def run(theta_deg: float, delta_deg: float, duration: float, fps: int):
    dt = 1.0 / (fps * FPS_SUBSTEPS)
    t0 = math.radians(theta_deg)
    a = np.array([t0, 0.0, t0, 0.0])
    b = np.array([t0 + math.radians(delta_deg), 0.0, t0, 0.0])
    frames = int(duration * fps)
    states_a, states_b, seps = [], [], []
    for _ in range(frames):
        states_a.append(a.copy())
        states_b.append(b.copy())
        xa, ya = tip(a)
        xb, yb = tip(b)
        seps.append(math.hypot(xa - xb, ya - yb) / TOTAL_L)
        for _ in range(FPS_SUBSTEPS):
            a = rk4(a, dt)
            b = rk4(b, dt)
    drift_a = abs(energy(states_a[-1]) - energy(states_a[0]))
    return states_a, states_b, np.array(seps), drift_a


def first_time(seps: np.ndarray, frac: float, fps: int):
    idx = np.argmax(seps > frac)
    if seps[idx] <= frac:
        return None
    return idx / fps


def measure_report(seps, drift, fps, theta_deg, delta_deg):
    t_split = first_time(seps, SPLIT_FRAC, fps)
    t_full = first_time(seps, FULL_FRAC, fps)
    print(f"theta {theta_deg} deg, delta {delta_deg} deg")
    print(f"split (gap > {SPLIT_FRAC:.2f} L): {t_split if t_split is None else round(t_split, 2)} s")
    print(f"full (gap > {FULL_FRAC:.2f} L): {t_full if t_full is None else round(t_full, 2)} s")
    print(f"max gap: {seps.max():.2f} L at {np.argmax(seps) / fps:.2f} s")
    print(f"energy drift pendulum A: {drift:.2e}")
    return t_split, t_full


class Renderer:
    def __init__(self, manifest, states_a, states_b, seps, t_split, t_full, run_dur):
        self.fps = manifest["fps"]
        self.states_a, self.states_b, self.seps = states_a, states_b, seps
        self.t_split, self.t_full, self.run_dur = t_split, t_full, run_dur
        self.font = ImageFont.truetype(os.environ["SEED_ZERO_FONT"], 42)
        self.font_big = ImageFont.truetype(os.environ["SEED_ZERO_FONT"], 52)
        self.fade_lut = [min(255, int(v * TRAIL_FADE)) for v in range(256)] * 3
        self.trail = Image.new("RGB", (W, H), (0, 0, 0))
        self.prev_tips = None

    def px(self, x, y):
        return (PIVOT[0] + x * SCALE, PIVOT[1] + y * SCALE)

    def joints(self, state):
        t1, _, t2, _ = state
        j = (L1 * math.sin(t1), L1 * math.cos(t1))
        t = (j[0] + L2 * math.sin(t2), j[1] + L2 * math.cos(t2))
        return self.px(*j), self.px(*t)

    def advance_trail(self, frame_idx):
        self.trail = self.trail.point(self.fade_lut)
        d = ImageDraw.Draw(self.trail)
        _, tip_a = self.joints(self.states_a[frame_idx])
        _, tip_b = self.joints(self.states_b[frame_idx])
        if self.prev_tips is not None:
            pa, pb = self.prev_tips
            d.line([pb, tip_b], fill=(120, 124, 130), width=4)
            d.line([pa, tip_a], fill=(60, 130, 107), width=4)
        self.prev_tips = (tip_a, tip_b)

    def draw_scene(self, frame_idx, show_labels, label_alpha=1.0):
        frame = np.zeros((H, W, 3), np.uint16)
        frame[:, :] = BG
        frame += np.asarray(self.trail, dtype=np.uint16)
        img = Image.fromarray(np.clip(frame, 0, 255).astype(np.uint8))
        d = ImageDraw.Draw(img)
        for state, col in ((self.states_b[frame_idx], COL_B), (self.states_a[frame_idx], COL_A)):
            j, t = self.joints(state)
            d.line([self.px(0, 0), j], fill=col, width=6)
            d.line([j, t], fill=col, width=6)
            d.ellipse((j[0] - 12, j[1] - 12, j[0] + 12, j[1] + 12), fill=col)
            d.ellipse((t[0] - 17, t[1] - 17, t[0] + 17, t[1] + 17), fill=col)
        d.ellipse((PIVOT[0] - 8, PIVOT[1] - 8, PIVOT[0] + 8, PIVOT[1] + 8), fill=MUTED)
        t = frame_idx / self.fps
        gap = self.seps[frame_idx]
        d.text((W - 60, 190), f"t = {t:5.2f} s", font=self.font, fill=MUTED, anchor="rm")
        d.text((W - 60, 250), f"gap = {gap:4.2f} L", font=self.font, fill=MUTED, anchor="rm")
        if show_labels:
            shade = tuple(int(v * label_alpha + BG[i] * (1 - label_alpha))
                          for i, v in enumerate((216, 222, 230)))
            d.text((540, 1450), f"visible split: {self.t_split:.1f} s",
                   font=self.font_big, fill=shade, anchor="mm")
            d.text((540, 1520), f"gap wider than the pendulum: {self.t_full:.1f} s",
                   font=self.font, fill=shade, anchor="mm")
        return np.asarray(img)

    def render(self, out_path):
        out_path.parent.mkdir(parents=True, exist_ok=True)
        run_frames = int(self.run_dur * self.fps)
        # Pass 1: build the final trail state for the intro hold.
        for f in range(run_frames):
            self.advance_trail(f)
        final_trail = self.trail.copy()
        self.trail = Image.new("RGB", (W, H), (0, 0, 0))
        self.prev_tips = None

        total = int((INTRO_HOLD + RESET_GAP + self.run_dur + PAYOFF_HOLD) * self.fps)
        proc = subprocess.Popen(
            ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
             "-s", f"{W}x{H}", "-r", str(self.fps), "-i", "-",
             "-c:v", "libx264", "-crf", "16", "-preset", "medium",
             "-pix_fmt", "yuv420p", str(out_path)],
            stdin=subprocess.PIPE,
        )
        assert proc.stdin is not None
        saved_trail = self.trail
        for f in range(total):
            t = f / self.fps
            if t < INTRO_HOLD:
                self.trail, keep = final_trail, self.trail
                frame = self.draw_scene(run_frames - 1, show_labels=True)
                self.trail = keep
            elif t < INTRO_HOLD + RESET_GAP:
                frame = self.draw_scene(0, show_labels=False)
            else:
                idx = min(int((t - INTRO_HOLD - RESET_GAP) * self.fps), run_frames - 1)
                if idx > 0 and t < INTRO_HOLD + RESET_GAP + self.run_dur:
                    self.advance_trail(idx)
                alpha = min(1.0, max(0.0, (t - (INTRO_HOLD + RESET_GAP + self.run_dur)) / 0.6 + 1.0)) \
                    if t > INTRO_HOLD + RESET_GAP + self.run_dur - 0.6 else 0.0
                frame = self.draw_scene(idx, show_labels=alpha > 0, label_alpha=alpha)
            proc.stdin.write(frame.tobytes())
            if f % 300 == 0:
                print(f"frame {f}/{total}", file=sys.stderr)
        proc.stdin.close()
        if proc.wait() != 0:
            raise RuntimeError("ffmpeg failed")
        print(f"footage: {out_path} ({total / self.fps:.2f}s at {self.fps} fps)")


def main() -> None:
    manifest = json.loads((ROOT / "projects/pendulum/manifest.json").read_text())
    theta = manifest["theta_deg"]
    for i, arg in enumerate(sys.argv):
        if arg == "--theta":
            theta = float(sys.argv[i + 1])
    fps = manifest["fps"]
    scout = manifest["scout_duration"]
    states_a, states_b, seps, drift = run(theta, manifest["delta_deg"], scout, fps)
    t_split, t_full = measure_report(seps, drift, fps, theta, manifest["delta_deg"])
    if "--measure-only" in sys.argv:
        return
    if t_full is None:
        raise SystemExit("no full divergence inside scout window; pick another theta")
    run_dur = t_full + manifest["after_full"]
    n = int(run_dur * fps)
    Renderer(manifest, states_a[:n], states_b[:n], seps[:n], t_split, t_full,
             run_dur).render(ROOT / "media/pendulum/footage.mp4")


if __name__ == "__main__":
    main()
