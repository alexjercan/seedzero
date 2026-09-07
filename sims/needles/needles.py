#!/usr/bin/env python3
"""Buffon's needle: pi from sticks falling on floorboards.

A floor of boards, each exactly as wide as one stick. Ten thousand sticks
fall at a uniformly random position and angle (seed 0, numpy RandomState).
A stick counts when it crosses a line between two boards. Buffon's result:
a stick as long as a board is wide crosses a line with probability 2/pi,
so two times the number of sticks over the number crossing estimates pi.

Measured and printed: the crossing count, the estimate, its error, the
running estimate as the sticks land, the mean shadow of a stick (|cos of
the angle|, expected 2/pi), and as checks a million sticks at another
seed and the spread of the 10,000-stick estimate over many seeds.

usage: needles.py [--measure-only]
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
RED = (232, 96, 88)
TEXT = (216, 222, 230)
MUTED = (138, 148, 163)
GRIDLINE = (40, 48, 58)
FLOOR = (19, 24, 31)
LINE = (74, 86, 102)
MISS = (46, 118, 98)
WHITE = (255, 255, 255)

FLOOR_Y0, FLOOR_Y1 = 240, 1290
HUD_Y = 150.0
EST_LABEL_Y = 1490.0
EST_Y = 1610.0
PAYOFF_Y = 1868.0


def drop(rng: np.random.RandomState, n: int, board: float) -> dict:
    """n sticks of length `board` on boards `board` wide. Centre x is uniform
    over the frame width (board lines sit at every multiple of `board`, the
    frame edges included), centre y uniform over the floor, angle uniform
    over a half turn. A stick crosses a line when its half shadow reaches
    the nearest line."""
    xc = rng.uniform(0.0, W, n)
    yc = rng.uniform(FLOOR_Y0 + board / 2, FLOOR_Y1 - board / 2, n)
    theta = rng.uniform(0.0, np.pi, n)
    half = board / 2 * np.abs(np.cos(theta))
    off = xc % board
    dist = np.minimum(off, board - off)
    cross = half >= dist
    return {"xc": xc, "yc": yc, "theta": theta, "cross": cross}


def estimate(n: int, c: int) -> float:
    return 2.0 * n / c if c else float("nan")


def measure(man: dict) -> dict:
    rng = np.random.RandomState(man["seed"])
    n, board = man["needles"], float(man["board_px"])
    run = drop(rng, n, board)
    cross = run["cross"]
    c = int(cross.sum())
    est = estimate(n, c)
    print(f"{n:,} sticks of {board:.0f} px on boards {board:.0f} px wide at seed {man['seed']}")
    print(f"  crossing a line: {c:,} = {100 * c / n:.2f}% (exact 2/pi = {200 / math.pi:.2f}%, "
          f"one standard deviation {100 * math.sqrt((2 / math.pi) * (1 - 2 / math.pi) / n):.2f} points)")
    print(f"  estimate 2 x {n:,} / {c:,} = {est:.5f}; pi = {math.pi:.5f}; error {est - math.pi:+.5f} "
          f"= {100 * abs(est - math.pi) / math.pi:.3f}%")
    print(f"  mean shadow |cos angle| {np.abs(np.cos(run['theta'])).mean():.4f} (exact 2/pi = {2 / math.pi:.4f})")
    cum = np.cumsum(cross)
    for k in (1, 2, 5, 10, 20, 50, 100, 200, 500, 1000, 2000, 5000, n):
        ck = int(cum[k - 1])
        print(f"  after {k:>6,} sticks: {ck:>5,} crossing, estimate {estimate(k, ck):.4f}")
    counts = np.arange(1, n + 1)
    ests = 2.0 * counts / np.maximum(cum, 1)
    for tol in (0.1, 0.01):
        bad = np.where(~(np.abs(ests - math.pi) < tol))[0]
        stay = int(bad[-1] + 2) if len(bad) else 1
        print(f"  the estimate stays within {tol} of pi from stick {stay:,} on")
    digits = np.floor(ests * 100) == 314
    bad = np.where(~digits)[0]
    print(f"  the estimate reads 3.14 from stick {int(bad[-1] + 2) if len(bad) else 1:,} on")
    # checks
    m, cs = man["check_needles"], man["check_seed"]
    chk = drop(np.random.RandomState(cs), m, board)
    cm = int(chk["cross"].sum())
    print(f"check: {m:,} sticks at seed {cs}: {cm:,} crossing, estimate {estimate(m, cm):.5f}, "
          f"error {estimate(m, cm) - math.pi:+.5f}")
    e = np.array([estimate(n, int(drop(np.random.RandomState(s), n, board)["cross"].sum()))
                  for s in range(man["check_seeds"])])
    print(f"check: {n:,} sticks over seeds 0..{man['check_seeds'] - 1}: mean {e.mean():.4f}, sd {e.std():.4f}; "
          f"within 0.1 of pi {100 * (np.abs(e - math.pi) < 0.1).mean():.1f}%, within 0.01 "
          f"{100 * (np.abs(e - math.pi) < 0.01).mean():.1f}%, reading 3.14 "
          f"{100 * (np.floor(e * 100) == 314).mean():.1f}%; lowest {e.min():.4f}, highest {e.max():.4f}")
    run.update({"cum": cum, "c": c, "est": est})
    return run


class Renderer:
    def __init__(self, man: dict, meas: dict):
        self.man, self.meas = man, meas
        self.fps = man["fps"]
        self.board = float(man["board_px"])
        font = os.environ["SEED_ZERO_FONT"]
        self.font = ImageFont.truetype(font, 40)
        self.font_small = ImageFont.truetype(font, 32)
        self.font_tiny = ImageFont.truetype(font, 26)
        self.font_big = ImageFont.truetype(font, 56)
        self.font_huge = ImageFont.truetype(font, 120)
        keys = np.array(man["land_keys"], dtype=float)
        n = man["needles"]
        counts = np.arange(1, n + 1, dtype=float)
        # Landing time of stick i: the count curve is log-linear between keys.
        self.t_land = np.interp(np.log(counts + 1.0), np.log(keys[:, 1] + 1.0), keys[:, 0])
        self.fall = float(man["fall_s"])
        # After the payoff numbers are spoken the same 10,000 sticks fall
        # again at a steady pace, so the last frame is the finished floor.
        self.t_replay = man["replay_t"] + np.arange(n) * (man["replay_s"] / n)
        i = np.arange(n)
        # Tumble and drop height come from the index, so the measurement
        # stream stays untouched by the animation.
        self.spin = np.where(i % 2 == 0, 1.0, -1.0) * np.pi * (1.0 + (i * 7 % 5) / 4.0)
        self.height = 520.0 + (i * 13 % 7) * 40.0
        self.base = self.floor_image()
        self.landed = 0

    def floor_image(self) -> Image.Image:
        img = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(img)
        d.rectangle((0, FLOOR_Y0, W, FLOOR_Y1), fill=FLOOR)
        k = 0
        while k * self.board <= W:
            x = k * self.board
            d.line((x, FLOOR_Y0, x, FLOOR_Y1), fill=LINE, width=4)
            k += 1
        return img

    def stick(self, d: ImageDraw.ImageDraw, x: float, y: float, th: float, col: tuple, width: int = 3) -> None:
        dx, dy = self.board / 2 * math.cos(th), self.board / 2 * math.sin(th)
        d.line((x - dx, y - dy, x + dx, y + dy), fill=col, width=width)

    def frame_at(self, f: int) -> np.ndarray:
        man, m = self.man, self.meas
        t = f / self.fps
        xc, yc, th, cross, cum = m["xc"], m["yc"], m["theta"], m["cross"], m["cum"]
        replay = t >= man["replay_t"]
        t_land = self.t_replay if replay else self.t_land
        n_land = int(np.searchsorted(t_land, t, side="right"))
        if n_land < self.landed:
            self.base = self.floor_image()
            self.landed = 0
        d0 = ImageDraw.Draw(self.base)
        for i in range(self.landed, n_land):
            self.stick(d0, xc[i], yc[i], th[i], GOLD if cross[i] else MISS)
        self.landed = n_land
        img = self.base.copy()
        d = ImageDraw.Draw(img)
        hi = int(np.searchsorted(t_land, t + self.fall, side="right"))
        for i in range(n_land, hi):
            u = 1.0 - (t_land[i] - t) / self.fall
            y = yc[i] - (1.0 - u) ** 2 * self.height[i]
            self.stick(d, xc[i], y, th[i] + (1.0 - u) * self.spin[i], WHITE)
        # Falling sticks are only visible over the floor, never over the HUD or readout.
        d.rectangle((0, 0, W, FLOOR_Y0 - 1), fill=BG)
        d.rectangle((0, FLOOR_Y1 + 1, W, H), fill=BG)
        c = int(cum[n_land - 1]) if n_land else 0
        d.text((60, HUD_Y), "sticks dropped" + ("  (replay)" if replay else ""), font=self.font, fill=TEXT, anchor="lm")
        d.text((W - 60, HUD_Y), f"{n_land:,}", font=self.font_big, fill=TEXT, anchor="rm")
        d.text((60, HUD_Y + 62), "crossing a line", font=self.font, fill=GOLD, anchor="lm")
        d.text((W - 60, HUD_Y + 62), f"{c:,}", font=self.font_big, fill=GOLD, anchor="rm")
        if n_land >= man["show_est_from"] or replay:
            # The replay only re-drops the same sticks: the readout keeps the result of the full run.
            n_all = len(xc)
            est = estimate(n_all, int(cum[-1])) if replay else estimate(n_land, c)
            label = f"final estimate from all {n_all:,} sticks" if replay else "two times the sticks, over the crossings"
            d.text((60, EST_LABEL_Y), label, font=self.font_small, fill=MUTED, anchor="lm")
            d.text((60, EST_Y), f"{est:.4f}" if c else "--", font=self.font_huge, fill=GOLD, anchor="lm")
            d.text((W - 60, EST_Y - 30), "pi", font=self.font_small, fill=MUTED, anchor="rm")
            d.text((W - 60, EST_Y + 22), f"{math.pi:.4f}", font=self.font, fill=TEXT, anchor="rm")
        if t >= man["payoff_t"]:
            alpha = min(1.0, (t - man["payoff_t"]) / man["payoff_hold"])
            shade = tuple(int(c_ * alpha + BG[i] * (1 - alpha)) for i, c_ in enumerate(GOLD))
            d.text((W / 2, PAYOFF_Y), man["payoff_text"], font=self.font, fill=shade, anchor="mm")
        return np.asarray(img)

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
    man = json.loads((ROOT / "projects/needles/manifest.json").read_text())
    meas = measure(man)
    if "--measure-only" in sys.argv:
        return
    Renderer(man, meas).render(ROOT / "media/needles/footage.mp4")


if __name__ == "__main__":
    main()
