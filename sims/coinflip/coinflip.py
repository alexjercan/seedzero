#!/usr/bin/env python3
"""Coin flip for a million, taken again and again.

Ten thousand players each face the viral poll: keep `sure` or flip a fair
coin for `prize`. Flipping multiplies a player's stake by prize / sure on
heads and wipes it out on tails, so the expected value of every flip is half
that multiplier: ten times the safe money. The winners are offered the same
bet again, round after round, until nobody is left holding anything.

The code counts survivors and the total pot after every round from one
seeded stream of flips, and prints the round at which the pot reaches zero.

usage: coinflip.py [--measure-only]
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

BG = (11, 14, 18)
GOLD = (240, 186, 88)
DEAD = (28, 34, 42)
ACCENT = (92, 200, 165)
TEXT = (216, 222, 230)
MUTED = (138, 148, 163)

# Layout. The caption band burned in by compose.sh sits at y = 1344..1420.
ROUND_Y = 205.0
GRID_Y0 = 320
HOLDING_Y = 1275.0
POT_Y = 1490.0
BAR_X0, BAR_X1 = 110.0, 970.0
BAR_BASE, BAR_H = 1800.0, 210.0
PAYOFF_Y = 1868.0
SCALES = ((1e18, "quintillion"), (1e15, "quadrillion"), (1e12, "trillion"),
          (1e9, "billion"), (1e6, "million"), (1e3, "thousand"))


def compact(value: float) -> str:
    if value <= 0:
        return "0"
    for size, name in SCALES:
        if value >= size:
            return f"{value / size:.3g} {name}"
    return f"{value:,.0f}"


def measure_report(man: dict) -> dict:
    rng = np.random.RandomState(man["seed"])
    n = man["players"]
    mult = man["prize"] / man["sure"]
    alive = np.ones(n, dtype=bool)
    # Round at which each player loses everything; 0 means still holding.
    bust = np.zeros(n, dtype=np.int32)
    survivors, pot = [], []
    rnd = 0
    while alive.any():
        rnd += 1
        heads = rng.random_sample(n) < 0.5
        killed = alive & ~heads
        bust[killed] = rnd
        alive &= heads
        survivors.append(int(alive.sum()))
        pot.append(float(alive.sum()) * man["sure"] * mult ** rnd)
    rounds = rnd

    print(f"{n} players at seed {man['seed']}: keep {man['sure']:,} "
          f"or flip for {man['prize']:,} ({mult:.0f}x the stake, "
          f"expected value {mult / 2:.0f}x)")
    print(f"safe total, never flipping: {n * man['sure']:,}")
    for i, (s, p) in enumerate(zip(survivors, pot), start=1):
        print(f"  round {i:2d}: still holding {s:5d}  pot {compact(p):>16s}"
              f"  expected value per player {compact(man['sure'] * 10.0 ** i)}")
    print(f"pot reaches zero at round {rounds}; expected value then says "
          f"{compact(10.0 ** rounds)} times the stake")
    growth = [pot[i] / pot[i - 1] for i in range(1, len(pot)) if pot[i] > 0]
    print(f"pot growth per round before the last: "
          f"min {min(growth):.2f}x, max {max(growth):.2f}x, "
          f"mean {sum(growth) / len(growth):.2f}x")
    return {"bust": bust, "survivors": survivors, "pot": pot,
            "rounds": rounds, "mult": mult}


class Renderer:
    def __init__(self, man, meas):
        self.man = man
        self.meas = meas
        self.fps = man["fps"]
        self.rounds = meas["rounds"]
        self.cols = man["grid_cols"]
        self.rows = man["players"] // self.cols
        self.cell = man["cell_px"]
        self.dot = man["dot_px"]
        font = os.environ["SEED_ZERO_FONT"]
        self.font = ImageFont.truetype(font, 40)
        self.font_small = ImageFont.truetype(font, 32)
        self.font_big = ImageFont.truetype(font, 58)
        # Round one holds long enough to be narrated, then a steady cadence.
        step = (man["last_round"] - man["resume_at"]) / max(1, self.rounds - 2)
        self.round_at = [man["first_round"]] + [
            man["resume_at"] + step * k for k in range(self.rounds - 1)]
        # Death time per player, laid out as the grid.
        bust = meas["bust"].reshape(self.rows, self.cols)
        death = np.full(bust.shape, np.inf)
        for k in range(1, self.rounds + 1):
            death[bust == k] = self.round_at[k - 1]
        self.death = death
        self.grid_x0 = (W - self.cols * self.cell) // 2

    def round_index(self, t: float) -> int:
        done = 0
        for k, at in enumerate(self.round_at, start=1):
            if t >= at:
                done = k
        return done

    def frame_at(self, t: float) -> np.ndarray:
        frame = np.zeros((H, W, 3), dtype=np.uint8)
        frame[:, :] = BG
        gone = np.clip((t - self.death) / self.man["fade"], 0.0, 1.0)
        cells = (np.array(GOLD, dtype=np.float32)
                 + gone[..., None] * (np.array(DEAD, dtype=np.float32)
                                      - np.array(GOLD, dtype=np.float32)))
        block = np.repeat(np.repeat(cells.astype(np.uint8), self.cell, 0),
                          self.cell, 1)
        pad = self.cell - self.dot
        if pad:
            mask = np.ones((self.cell,), dtype=bool)
            mask[self.dot:] = False
            block[~np.tile(mask, self.rows), :] = BG
            block[:, ~np.tile(mask, self.cols)] = BG
        frame[GRID_Y0:GRID_Y0 + block.shape[0],
              self.grid_x0:self.grid_x0 + block.shape[1]] = block

        img = Image.fromarray(frame)
        d = ImageDraw.Draw(img)
        done = self.round_index(t)
        holding = self.meas["survivors"][done - 1] if done else self.man["players"]
        pot = (self.meas["pot"][done - 1] if done
               else self.man["players"] * self.man["sure"])
        label = f"round {done}" if done else "the offer"
        d.text((W / 2, ROUND_Y), label, font=self.font_big, fill=ACCENT,
               anchor="mm")
        d.text((W / 2, HOLDING_Y),
               f"still holding: {holding:,} of {self.man['players']:,}",
               font=self.font, fill=TEXT if holding else MUTED, anchor="mm")
        pot_label = "pot" if done else "safe total, if nobody flips"
        d.text((W / 2, POT_Y), f"{pot_label}: {compact(pot)}", font=self.font,
               fill=GOLD if pot else MUTED, anchor="mm")
        self.draw_bars(d, t)
        alpha = min(1.0, max(0.0, (t - self.man["payoff_fade"]) / 0.6))
        if alpha > 0:
            shade = tuple(int(c * alpha + BG[i] * (1 - alpha))
                          for i, c in enumerate(TEXT))
            d.text((W / 2, PAYOFF_Y),
                   f"{self.rounds} rounds: 0 of {self.man['players']:,} left",
                   font=self.font, fill=shade, anchor="mm")
        return np.asarray(img)

    def draw_bars(self, d, t: float) -> None:
        """One bar per round: how many players are still holding anything."""
        counts = [self.man["players"]] + self.meas["survivors"]
        width = (BAR_X1 - BAR_X0) / len(counts)
        d.line([(BAR_X0, BAR_BASE), (BAR_X1, BAR_BASE)], fill=DEAD, width=3)
        for k, count in enumerate(counts):
            at = -1.0 if k == 0 else self.round_at[k - 1]
            grown = min(1.0, max(0.0, (t - at) / self.man["fade"]))
            if grown <= 0 or count == 0:
                continue
            height = BAR_H * count / self.man["players"] * grown
            x = BAR_X0 + width * k
            d.rectangle([x + 4, BAR_BASE - max(height, 2.0),
                         x + width - 4, BAR_BASE], fill=GOLD)
        d.text((BAR_X0, BAR_BASE - BAR_H), f"{self.man['players']:,}",
               font=self.font_small, fill=MUTED, anchor="ls")

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
            proc.stdin.write(self.frame_at(f / self.fps).tobytes())
            if f % 300 == 0:
                print(f"frame {f}/{total}", file=sys.stderr)
        proc.stdin.close()
        if proc.wait() != 0:
            raise RuntimeError("ffmpeg failed")
        print(f"footage: {out_path} ({total / self.fps:.2f}s at {self.fps} fps)")


def main() -> None:
    man = json.loads((ROOT / "projects/coinflip/manifest.json").read_text())
    meas = measure_report(man)
    if "--measure-only" in sys.argv:
        return
    Renderer(man, meas).render(ROOT / "media/coinflip/footage.mp4")


if __name__ == "__main__":
    main()
