#!/usr/bin/env python3
"""Pendulum wave: simulation, measurement, and footage.

Thirty pendulums, tuned so pendulum i completes base_cycles + i full
swings in one period. Displacement y_i(t) = A cos(omega_i t). They start
as one line, scatter into traveling waves, split into a perfect mirror
at half period, and realign into one line at exactly the period. The
sim prints the tuned lengths, verifies the mirror split, finds the
moment of maximum disorder, and measures the realignment gap.

usage: pendulumwave.py [--measure-only]
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent.parent
W, H = 1080, 1920
G = 9.81  # m/s^2

BG = (11, 14, 18)
BOB = (216, 222, 230)
ACCENT = (92, 200, 165)
MUTED = (138, 148, 163)
GRID = (70, 80, 94)

# Layout. The caption band burned in by compose.sh sits at y = 1344..1420;
# nothing draws text there.
CLOCK_Y = 210.0
BAR_Y = 380.0
X0, X1 = 120.0, 960.0
MID_Y = 900.0
AMP_PX = 380.0
TL_X0, TL_X1 = 140.0, 940.0
TL_Y = 1560.0
EVENT_Y = (1650.0, 1730.0)
PAYOFF_Y = 1868.0

# Timeline (seconds).
INTRO_HOLD = 2.0
RESET_GAP = 0.5
LABEL_FADE = 0.6


def frequencies(manifest: dict) -> np.ndarray:
    n, base, period = manifest["pendulums"], manifest["base_cycles"], manifest["period"]
    return (base + np.arange(n)) / period  # Hz


def positions(manifest: dict, t: float) -> np.ndarray:
    """Vertical bob displacement in [-1, 1] (1 = release side, at the top)."""
    return np.cos(2 * np.pi * frequencies(manifest) * t)


def measure_report(manifest: dict) -> dict:
    n, period = manifest["pendulums"], manifest["period"]
    fps = manifest["fps"]
    freqs = frequencies(manifest)
    omega = 2 * np.pi * freqs
    lengths_cm = G / omega**2 * 100

    # Mirror at half period: strict alternation at full amplitude.
    y_half = positions(manifest, period / 2)
    signs = np.sign(y_half)
    mirror_ok = bool(
        np.all(np.abs(np.abs(y_half) - 1.0) < 1e-9)
        and np.all(signs[::2] == signs[0])
        and np.all(signs[1::2] == -signs[0])
    )
    # Realign gap at the full period, in render pixels.
    y_T = positions(manifest, period)
    gap_px = float((y_T.max() - y_T.min()) * AMP_PX)
    # Maximum disorder: minimum phase coherence over one period.
    frames = int(period * fps) + 1
    ts = np.arange(frames) / fps
    phases = omega[None, :] * ts[:, None]
    r = np.abs(np.exp(1j * phases).mean(axis=1))
    worst = int(np.argmin(r))

    m = {
        "len_slow_cm": float(lengths_cm[0]),
        "len_fast_cm": float(lengths_cm[-1]),
        "mirror_ok": mirror_ok,
        "gap_px": gap_px,
        "worst_t": float(ts[worst]),
        "worst_r": float(r[worst]),
    }
    print(f"pendulums: {n}  period: {period}s  "
          f"cycles: {manifest['base_cycles']}..{manifest['base_cycles'] + n - 1}")
    print(f"slowest: {freqs[0]:.4f} Hz, length {m['len_slow_cm']:.1f} cm")
    print(f"fastest: {freqs[-1]:.4f} Hz, length {m['len_fast_cm']:.1f} cm")
    print(f"mirror at {period / 2:.3f}s (alternating, full amplitude): {mirror_ok}")
    print(f"realign at {period:.3f}s: max gap {gap_px:.6f} px")
    print(f"max disorder: t={m['worst_t']:.2f}s coherence R={m['worst_r']:.3f}")
    return m


class Renderer:
    def __init__(self, manifest, meas):
        self.man = manifest
        self.fps = manifest["fps"]
        self.scene_dur = manifest["scene_duration"]
        self.period = manifest["period"]
        self.meas = meas
        self.n = manifest["pendulums"]
        self.xs = np.linspace(X0, X1, self.n)
        self.font = ImageFont.truetype(os.environ["SEED_ZERO_FONT"], 42)
        self.font_small = ImageFont.truetype(os.environ["SEED_ZERO_FONT"], 36)
        self.font_big = ImageFont.truetype(os.environ["SEED_ZERO_FONT"], 58)

    def draw_wave(self, d, s: float):
        d.line((X0 - 40, BAR_Y, X1 + 40, BAR_Y), fill=GRID, width=6)
        y = MID_Y - AMP_PX * positions(self.man, s)
        pts = list(zip(self.xs, y))
        for x in self.xs:
            d.line((x, BAR_Y + 3, x, BAR_Y + 16), fill=GRID, width=3)
        d.line(pts, fill=(60, 120, 100), width=3)
        for x, yy in pts:
            d.ellipse((x - 11, yy - 11, x + 11, yy + 11), fill=BOB)

    def draw_clock(self, d, s: float):
        d.text((W / 2, CLOCK_Y), f"{s:5.2f} s", font=self.font_big,
               fill=ACCENT, anchor="mm")

    def draw_timeline(self, d, s: float):
        half, full = self.period / 2, self.period
        span = self.scene_dur
        d.line((TL_X0, TL_Y, TL_X1, TL_Y), fill=GRID, width=3)
        for t_ev, label in ((half, "mirror"), (full, "realign")):
            x = TL_X0 + t_ev / span * (TL_X1 - TL_X0)
            d.line((x, TL_Y - 14, x, TL_Y + 14), fill=MUTED, width=3)
            d.text((x, TL_Y + 44), f"{t_ev:.0f}s {label}", font=self.font_small,
                   fill=MUTED, anchor="mm")
        x = TL_X0 + min(s, span) / span * (TL_X1 - TL_X0)
        d.ellipse((x - 9, TL_Y - 9, x + 9, TL_Y + 9), fill=ACCENT)
        if s >= half:
            d.text((W / 2, EVENT_Y[0]),
                   "15.0 s: two lines. 15 up, 15 down.",
                   font=self.font, fill=BOB, anchor="mm")
        if s >= full:
            d.text((W / 2, EVENT_Y[1]),
                   f"30.0 s: one line. gap {self.meas['gap_px']:.1f} px",
                   font=self.font, fill=ACCENT, anchor="mm")

    def frame_at(self, s: float) -> np.ndarray:
        frame = np.zeros((H, W, 3), dtype=np.uint8)
        frame[:, :] = BG
        img = Image.fromarray(frame)
        d = ImageDraw.Draw(img)
        self.draw_clock(d, s)
        self.draw_wave(d, s)
        self.draw_timeline(d, s)
        alpha = min(1.0, max(0.0, (s - self.man["payoff_fade"]) / LABEL_FADE))
        if alpha > 0:
            shade = tuple(int(v * alpha + BG[i] * (1 - alpha))
                          for i, v in enumerate(BOB))
            d.text((W / 2, PAYOFF_Y),
                   "30 speeds, one line, every 30.0 s",
                   font=self.font, fill=shade, anchor="mm")
        return np.asarray(img)

    def render(self, out_path: Path) -> None:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        total = int(round((INTRO_HOLD + RESET_GAP + self.scene_dur) * self.fps))
        proc = subprocess.Popen(
            ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
             "-s", f"{W}x{H}", "-r", str(self.fps), "-i", "-",
             "-c:v", "libx264", "-crf", "16", "-preset", "medium",
             "-pix_fmt", "yuv420p", str(out_path)],
            stdin=subprocess.PIPE,
        )
        assert proc.stdin is not None
        for f in range(total):
            t = f / self.fps
            if t < INTRO_HOLD:
                frame = self.frame_at(self.scene_dur)
            elif t < INTRO_HOLD + RESET_GAP:
                frame = self.frame_at(0.0)
            else:
                frame = self.frame_at(t - INTRO_HOLD - RESET_GAP)
            proc.stdin.write(frame.tobytes())
            if f % 300 == 0:
                print(f"frame {f}/{total}", file=sys.stderr)
        proc.stdin.close()
        if proc.wait() != 0:
            raise RuntimeError("ffmpeg failed")
        print(f"footage: {out_path} ({total / self.fps:.2f}s at {self.fps} fps)")


def main() -> None:
    manifest = json.loads((ROOT / "projects/pendulumwave/manifest.json").read_text())
    meas = measure_report(manifest)
    if "--measure-only" in sys.argv:
        return
    Renderer(manifest, meas).render(ROOT / "media/pendulumwave/footage.mp4")


if __name__ == "__main__":
    main()
