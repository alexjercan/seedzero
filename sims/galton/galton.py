#!/usr/bin/env python3
"""Galton board simulation and footage renderer.

Reads projects/galton/manifest.json, simulates every ball as twelve fair
coin flips, renders 1080x1920 footage at the manifest fps, and prints the
measured bin counts the narration must quote.

usage: galton.py [--measure-only]
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
PEG = (58, 70, 86)
BALL = (216, 222, 230)
BAR = (92, 200, 165)
CURVE = (138, 148, 163)
TEXT = (216, 222, 230)
MUTED = (138, 148, 163)

# Layout.
CENTER_X = W / 2
BOARD_TOP = 260.0
BOARD_BOTTOM = 1030.0
BIN_BASE = 1660.0
BAR_MAX_PX = 470.0
BIN_W = 72.0
BALL_R = 7

# Timeline (seconds).
INTRO_HOLD = 2.0
POUR_START = 2.5
SPAWN_WINDOW = 21.5
ROW_TIME = 0.16
DROP_TIME = 0.4
LABEL_FADE = 0.6


def simulate(seed: int, balls: int, rows: int):
    rng = np.random.RandomState(seed)
    steps = 2 * rng.randint(0, 2, size=(balls, rows)) - 1
    offsets = np.concatenate(
        [np.zeros((balls, 1), dtype=np.int64), np.cumsum(steps, axis=1)], axis=1
    )
    bins = (offsets[:, -1] + rows) // 2
    counts = np.bincount(bins, minlength=rows + 1)
    return offsets, bins, counts


def measure_report(counts: np.ndarray, rows: int) -> None:
    center = rows // 2
    print(f"counts: {counts.tolist()}")
    print(f"center bin {center}: {counts[center]}")
    print(f"edge bin 0: {counts[0]}   edge bin {rows}: {counts[rows]}")
    edge_total = counts[0] + counts[rows]
    print(f"both edges combined: {edge_total}")
    if edge_total:
        print(f"measured center vs both edges: {counts[center] / edge_total:.1f} to 1")
    expected_center = math.comb(rows, center) / 2**rows * counts.sum()
    print(f"theory: C({rows},{center})=924, expected center {expected_center:.0f}, "
          f"expected per edge {counts.sum() / 2**rows:.2f}")


class Renderer:
    def __init__(self, manifest: dict, offsets, bins, counts):
        self.rows = manifest["rows"]
        self.fps = manifest["fps"]
        self.balls = manifest["balls"]
        self.offsets, self.bins, self.counts = offsets, bins, counts
        self.font = ImageFont.truetype(os.environ["SEED_ZERO_FONT"], 46)
        self.font_small = ImageFont.truetype(os.environ["SEED_ZERO_FONT"], 38)

        rng = np.random.RandomState(manifest["seed"] + 1)  # spawn jitter only
        spawn = POUR_START + SPAWN_WINDOW * (
            np.arange(self.balls) + rng.random_sample(self.balls)
        ) / self.balls
        self.spawn = spawn
        self.transit = ROW_TIME * self.rows
        self.land = self.spawn + self.transit + DROP_TIME
        self.pour_end = float(self.land.max())
        self.duration = self.pour_end + 6.0

        self.board = self.draw_board()
        self.bar_scale = BAR_MAX_PX / self.counts.max()

    def draw_board(self) -> np.ndarray:
        frame = np.zeros((H, W, 3), dtype=np.uint8)
        frame[:, :] = BG
        img = Image.fromarray(frame)
        d = ImageDraw.Draw(img)
        for i in range(self.rows):
            y = BOARD_TOP + (BOARD_BOTTOM - BOARD_TOP) * (i + 1) / self.rows
            for j in range(i + 1):
                x = CENTER_X + (j - i / 2) * BIN_W
                d.ellipse((x - 5, y - 5, x + 5, y + 5), fill=PEG)
        for k in range(self.rows + 2):
            x = CENTER_X + (k - (self.rows + 1) / 2) * BIN_W
            d.rectangle((x - 2, BIN_BASE - BAR_MAX_PX - 40, x + 2, BIN_BASE), fill=PEG)
        d.rectangle((0, BIN_BASE, W, BIN_BASE + 6), fill=PEG)
        return np.asarray(img).copy()

    def ball_xy(self, t: float):
        """Positions of balls in flight at time t (vectorized)."""
        age = t - self.spawn
        flying = (age > 0) & (t < self.land)
        idx = np.nonzero(flying)[0]
        age = age[idx]
        row_pos = np.minimum(age / ROW_TIME, self.rows)
        row = row_pos.astype(np.int64)
        frac = row_pos - row
        smooth = frac * frac * (3 - 2 * frac)
        o = self.offsets[idx]
        cur = o[np.arange(len(idx)), row]
        nxt = o[np.arange(len(idx)), np.minimum(row + 1, self.rows)]
        x = CENTER_X + (cur + (nxt - cur) * smooth) * (BIN_W / 2)
        in_board = age <= self.transit
        y_board = BOARD_TOP + (BOARD_BOTTOM - BOARD_TOP) * np.minimum(row_pos / self.rows, 1.0)
        drop_frac = np.clip((age - self.transit) / DROP_TIME, 0, 1)
        y_drop = BOARD_BOTTOM + (BIN_BASE - 30 - BOARD_BOTTOM) * drop_frac
        y = np.where(in_board, y_board, y_drop)
        x = np.where(in_board, x, CENTER_X + (self.bins[idx] - self.rows / 2) * BIN_W)
        return x, y

    def landed_counts(self, t: float) -> np.ndarray:
        landed = self.land <= t
        if landed.all():
            return self.counts
        return np.bincount(self.bins[landed], minlength=self.rows + 1)

    def draw_bars(self, frame: np.ndarray, counts: np.ndarray) -> None:
        for b, count in enumerate(counts):
            if count == 0:
                continue
            h = max(2, int(round(count * self.bar_scale)))
            x0 = int(CENTER_X + (b - self.rows / 2) * BIN_W - BIN_W / 2 + 4)
            x1 = int(x0 + BIN_W - 8)
            frame[int(BIN_BASE - h) : int(BIN_BASE), x0:x1] = BAR

    def draw_balls(self, frame: np.ndarray, t: float) -> None:
        x, y = self.ball_xy(t)
        for xi, yi in zip(x.astype(int), y.astype(int)):
            frame[
                max(0, yi - BALL_R) : yi + BALL_R, max(0, xi - BALL_R) : xi + BALL_R
            ] = BALL

    def draw_curve(self, d: ImageDraw.ImageDraw) -> None:
        total = self.counts.sum()
        pts = []
        for i in range(200):
            k = i / 199 * self.rows
            # Smooth normal approximation of the binomial, same scale as bars.
            mu, var = self.rows / 2, self.rows / 4
            y = total * math.exp(-((k - mu) ** 2) / (2 * var)) / math.sqrt(2 * math.pi * var)
            pts.append(
                (CENTER_X + (k - self.rows / 2) * BIN_W, BIN_BASE - y * self.bar_scale)
            )
        d.line(pts, fill=CURVE, width=4)

    def draw_labels(self, d: ImageDraw.ImageDraw, alpha: float) -> None:
        c = self.rows // 2
        shade = tuple(int(v * alpha + BG[i] * (1 - alpha)) for i, v in enumerate(TEXT))
        entries = [(0, self.counts[0]), (c, self.counts[c]), (self.rows, self.counts[self.rows])]
        for b, count in entries:
            x = CENTER_X + (b - self.rows / 2) * BIN_W
            h = count * self.bar_scale
            d.text(
                (x, BIN_BASE - h - 46), f"{count}",
                font=self.font, fill=shade, anchor="mm",
            )

    def frame_at(self, t: float, final_preview: bool) -> np.ndarray:
        frame = self.board.copy()
        if final_preview:
            counts = self.counts
        else:
            counts = self.landed_counts(t)
        self.draw_bars(frame, counts)
        if not final_preview:
            self.draw_balls(frame, t)
        img = Image.fromarray(frame)
        d = ImageDraw.Draw(img)
        landed_total = int(counts.sum())
        d.text((W - 60, 190), f"{landed_total:5d}", font=self.font_small,
               fill=MUTED, anchor="rm")
        if final_preview or t > self.pour_end + LABEL_FADE:
            alpha = 1.0 if final_preview else min(
                1.0, (t - self.pour_end - LABEL_FADE) / LABEL_FADE
            )
            self.draw_curve(d)
            self.draw_labels(d, alpha)
        return np.asarray(img)

    def render(self, out_path: Path) -> None:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        total_frames = int(round((INTRO_HOLD + self.duration - POUR_START + 0.5) * self.fps))
        proc = subprocess.Popen(
            [
                "ffmpeg", "-y", "-v", "error",
                "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                "-r", str(self.fps), "-i", "-",
                "-c:v", "libx264", "-crf", "16", "-preset", "medium",
                "-pix_fmt", "yuv420p", str(out_path),
            ],
            stdin=subprocess.PIPE,
        )
        assert proc.stdin is not None
        for f in range(total_frames):
            t = f / self.fps
            if t < INTRO_HOLD:
                frame = self.frame_at(t, final_preview=True)
            else:
                sim_t = t - INTRO_HOLD + POUR_START - 0.5
                frame = self.frame_at(max(sim_t, POUR_START - 0.5), final_preview=False)
            proc.stdin.write(frame.tobytes())
            if f % 300 == 0:
                print(f"frame {f}/{total_frames}", file=sys.stderr)
        proc.stdin.close()
        if proc.wait() != 0:
            raise RuntimeError("ffmpeg failed")
        print(f"footage: {out_path} ({total_frames / self.fps:.2f}s at {self.fps} fps)")


def main() -> None:
    manifest = json.loads((ROOT / "projects/galton/manifest.json").read_text())
    offsets, bins, counts = simulate(manifest["seed"], manifest["balls"], manifest["rows"])
    measure_report(counts, manifest["rows"])
    if "--measure-only" in sys.argv:
        return
    Renderer(manifest, offsets, bins, counts).render(ROOT / "media/galton/footage.mp4")


if __name__ == "__main__":
    main()
