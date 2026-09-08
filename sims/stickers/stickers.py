#!/usr/bin/env python3
"""Coupon collector: the last stickers cost the most.

An album has fifty numbered stickers. Packs are opened one at a time and
each pack holds one sticker drawn uniformly at random (seed 0, numpy
RandomState). A new sticker flies into its album slot; a duplicate bounces
off and drops onto a pile. The album fills quickly at first and then
stalls: the expected number of packs to find the k-th new sticker is
50 / (50 - k + 1), so the last sticker alone costs fifty packs on average.

Measured and printed: the packs opened when the album completes, the
packs spent on the first forty stickers, on the last ten, and on the last
one, the duplicate count, the exact expectations 50 x H(50), 50 x (H(50)
- H(10)), 50 x H(10) and 50, and as a check the same numbers over many
seeds.

usage: stickers.py [--measure-only]
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
SLOT = (19, 24, 31)
WHITE = (255, 255, 255)

HUD_Y = 150.0
COLS, ROWS = 5, 10
SLOT_W, SLOT_H, GAP = 176, 76, 10
ALBUM_X0 = (W - (COLS * SLOT_W + (COLS - 1) * GAP)) // 2
ALBUM_Y0 = 250
ALBUM_Y1 = ALBUM_Y0 + ROWS * SLOT_H + (ROWS - 1) * GAP
PACK_XY = (W / 2, ALBUM_Y0 - 30)
PILE_COLS = 12
PILE_X0, PILE_X1 = 60, 1020
PILE_FLOOR = 1790
PILE_TOP = 1360
PAYOFF_Y = 1868.0


def harmonic(n: int) -> float:
    return sum(1.0 / k for k in range(1, n + 1))


def collect(rng: np.random.RandomState, n: int, cap: int) -> np.ndarray:
    """Draw stickers until all n are found (at most cap draws)."""
    seen = np.zeros(n, dtype=bool)
    draws = []
    while not seen.all() and len(draws) < cap:
        s = int(rng.randint(0, n))
        draws.append(s)
        seen[s] = True
    return np.array(draws, dtype=int)


def milestones(draws: np.ndarray, n: int) -> np.ndarray:
    """Pack index (1-based) at which the k-th new sticker arrives, k = 1..n."""
    seen = np.zeros(n, dtype=bool)
    out = np.zeros(n, dtype=int)
    k = 0
    for i, s in enumerate(draws):
        if not seen[s]:
            seen[s] = True
            out[k] = i + 1
            k += 1
    return out


def measure(man: dict) -> dict:
    n, seed = man["stickers"], man["seed"]
    draws = collect(np.random.RandomState(seed), n, 100_000)
    ms = milestones(draws, n)
    total = int(ms[-1])
    first40, last10, last1 = int(ms[39]), int(ms[-1] - ms[39]), int(ms[-1] - ms[-2])
    dups = total - n
    print(f"{n} stickers, one random sticker per pack, seed {seed}")
    print(f"  album complete after {total} packs; {dups} duplicates")
    print(f"  first 40 stickers: {first40} packs (exact expectation {n * (harmonic(n) - harmonic(10)):.2f})")
    print(f"  last 10 stickers: {last10} packs (exact expectation {n * harmonic(10):.2f})")
    print(f"  last 1 sticker: {last1} packs (exact expectation {n:.2f})")
    print(f"  exact expected packs for all {n}: {n * harmonic(n):.2f}")
    for k in (10, 20, 30, 40, 45, 48, 49, 50):
        print(f"  sticker {k:>2} found at pack {int(ms[k - 1]):>4}")
    dup_by_pack = np.cumsum(np.array([1 if i + 1 not in set(ms.tolist()) else 0 for i in range(total)]))
    print(f"  duplicates when 40 found: {int(dup_by_pack[first40 - 1])}, at the end: {int(dup_by_pack[-1])}")
    # Check: many seeds.
    seeds = man["check_seeds"]
    tot = np.empty(seeds, dtype=int)
    f40 = np.empty(seeds, dtype=int)
    l10 = np.empty(seeds, dtype=int)
    l1 = np.empty(seeds, dtype=int)
    for s in range(seeds):
        m = milestones(collect(np.random.RandomState(s), n, 100_000), n)
        tot[s], f40[s], l10[s], l1[s] = m[-1], m[39], m[-1] - m[39], m[-1] - m[-2]
    print(f"check: seeds 0..{seeds - 1}: mean packs {tot.mean():.1f} (exact {n * harmonic(n):.2f}), median {np.median(tot):.0f}, "
          f"sd {tot.std():.1f}, min {tot.min()}, max {tot.max()}")
    print(f"check: mean first 40: {f40.mean():.1f}, mean last 10: {l10.mean():.1f}, mean last 1: {l1.mean():.1f}")
    print(f"check: last 10 cost more than the first 40 in {100 * (l10 > f40).mean():.1f}% of albums")
    for lim in (150, 200, 300, 400, 500):
        print(f"check: albums needing more than {lim} packs: {int((tot > lim).sum()):,} = {100 * (tot > lim).mean():.1f}%")
    print(f"check: seed {seed} sits at percentile {100 * (tot < total).mean():.0f} of the {seeds} albums")
    return {"draws": draws, "ms": ms, "total": total, "first40": first40, "last10": last10, "last1": last1, "dups": dups}


def pack_times(keys: list, meas: dict, n_total: int) -> np.ndarray:
    pts = []
    for t, v in keys:
        if v == "first40":
            v = meas["first40"]
        elif v == "all":
            v = n_total
        pts.append((float(t), float(v)))
    counts = np.arange(1, n_total + 1, dtype=float)
    return np.interp(counts, [p[1] for p in pts], [p[0] for p in pts])


def sticker_colour(s: int, n: int) -> tuple:
    h = (s / n) * 6.0
    i = int(h)
    f = h - i
    p, q = 0.35, 0.35 + 0.65 * f
    r = 0.35 + 0.65 * (1 - f)
    table = [(1, q, p), (r, 1, p), (p, 1, q), (p, r, 1), (q, p, 1), (1, p, r)]
    c = table[i % 6]
    return tuple(int(230 * v) for v in c)


class Renderer:
    def __init__(self, man: dict, meas: dict):
        self.man, self.meas = man, meas
        self.fps = man["fps"]
        font = os.environ["SEED_ZERO_FONT"]
        self.font = ImageFont.truetype(font, 40)
        self.font_small = ImageFont.truetype(font, 32)
        self.font_tiny = ImageFont.truetype(font, 26)
        self.font_big = ImageFont.truetype(font, 56)
        n = man["stickers"]
        self.n = n
        draws = meas["draws"]
        total = meas["total"]
        self.total = total
        self.t_pack = pack_times(man["pack_keys"], meas, total)
        self.t_replay = man["replay_t"] + np.arange(total) * (man["replay_s"] / total)
        # Which packs are new, and cumulative counts.
        seen = np.zeros(n, dtype=bool)
        self.new = np.zeros(total, dtype=bool)
        for i, s in enumerate(draws):
            if not seen[s]:
                seen[s] = True
                self.new[i] = True
        self.found_cum = np.cumsum(self.new)
        self.dup_cum = np.cumsum(~self.new)
        # Pile placement: duplicate j lands on column (sticker id mod cols).
        dups = meas["dups"]
        self.brick_w = (PILE_X1 - PILE_X0) / PILE_COLS
        heights = np.zeros(PILE_COLS, dtype=int)
        self.pile_col = np.full(total, -1, dtype=int)
        self.pile_row = np.full(total, -1, dtype=int)
        for i in range(total):
            if not self.new[i]:
                c = int(draws[i]) % PILE_COLS
                self.pile_col[i] = c
                self.pile_row[i] = heights[c]
                heights[c] += 1
        tallest = max(1, int(heights.max()))
        self.brick_h = min(18.0, (PILE_FLOOR - PILE_TOP) / tallest)
        self.colours = [sticker_colour(s, n) for s in range(n)]

    def slot_box(self, s: int) -> tuple:
        r, c = divmod(s, COLS)
        x0 = ALBUM_X0 + c * (SLOT_W + GAP)
        y0 = ALBUM_Y0 + r * (SLOT_H + GAP)
        return (x0, y0, x0 + SLOT_W, y0 + SLOT_H)

    def brick_box(self, i: int) -> tuple:
        c, r = self.pile_col[i], self.pile_row[i]
        x0 = PILE_X0 + c * self.brick_w
        y1 = PILE_FLOOR - r * self.brick_h
        return (x0 + 1, y1 - self.brick_h + 1, x0 + self.brick_w - 1, y1)

    def card(self, d: ImageDraw.ImageDraw, x: float, y: float, s: int, scale: float = 1.0) -> None:
        w, h = SLOT_W * 0.7 * scale, SLOT_H * 0.7 * scale
        d.rectangle((x - w / 2, y - h / 2, x + w / 2, y + h / 2), fill=self.colours[s], outline=WHITE, width=2)
        d.text((x, y), f"{s + 1}", font=self.font_small, fill=BG, anchor="mm")

    def frame_at(self, f: int) -> np.ndarray:
        man, m = self.man, self.meas
        t = f / self.fps
        draws, ms = m["draws"], m["ms"]
        replay = t >= man["replay_t"]
        wiped = t >= man["wipe_t"]
        t_pack = self.t_replay if replay else self.t_pack
        n_open = 0 if wiped else int(np.searchsorted(t_pack, t, side="right"))
        fly, drop = float(man["fly_s"]), float(man["drop_s"])
        # A pack "opens" at t_pack; the card lands at t_pack + fly; a duplicate settles at t_pack + fly + drop.
        landed = 0 if wiped else int(np.searchsorted(t_pack + fly, t, side="right"))
        settled = 0 if wiped else int(np.searchsorted(t_pack + fly + drop, t, side="right"))
        img = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(img)
        found = int(self.found_cum[landed - 1]) if landed else 0
        dups = int(self.dup_cum[settled - 1]) if settled else 0
        # HUD
        tag = "  (replay)" if replay and not wiped else ""
        d.text((60, HUD_Y), "packs opened" + tag, font=self.font, fill=TEXT, anchor="lm")
        d.text((W - 60, HUD_Y), f"{n_open:,}", font=self.font_big, fill=TEXT, anchor="rm")
        d.text((60, HUD_Y + 62), "stickers found", font=self.font, fill=GOLD, anchor="lm")
        d.text((W - 60, HUD_Y + 62), f"{found} / {self.n}", font=self.font_big, fill=GOLD, anchor="rm")
        # Album slots
        got = np.zeros(self.n, dtype=bool)
        got_at = np.full(self.n, -1, dtype=int)
        for i in range(landed):
            if self.new[i]:
                got[draws[i]] = True
                got_at[draws[i]] = i
        for s in range(self.n):
            box = self.slot_box(s)
            if got[s]:
                col = self.colours[s]
                age = t - (t_pack[got_at[s]] + fly)
                if age < 0.3:
                    a = 1.0 - age / 0.3
                    col = tuple(int(c * (1 - a) + 255 * a) for c in col)
                d.rectangle(box, fill=col)
                d.text(((box[0] + box[2]) / 2, (box[1] + box[3]) / 2), f"{s + 1}", font=self.font_small, fill=BG, anchor="mm")
            else:
                d.rectangle(box, fill=SLOT, outline=GRIDLINE, width=2)
                d.text(((box[0] + box[2]) / 2, (box[1] + box[3]) / 2), f"{s + 1}", font=self.font_small, fill=MUTED, anchor="mm")
        # Pile of duplicates
        d.line((PILE_X0, PILE_FLOOR + 2, PILE_X1, PILE_FLOOR + 2), fill=TEXT, width=2)
        for i in range(settled):
            if not self.new[i]:
                d.rectangle(self.brick_box(i), fill=self.colours[draws[i]])
        d.text((60, PILE_TOP - 34), "duplicates", font=self.font, fill=RED, anchor="lm")
        d.text((W - 60, PILE_TOP - 34), f"{dups}", font=self.font_big, fill=RED, anchor="rm")
        # Cards in flight
        if not wiped:
            for i in range(settled, n_open):
                s = int(draws[i])
                t0 = t_pack[i]
                box = self.slot_box(s)
                sx, sy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
                if t < t0 + fly:
                    u = (t - t0) / fly
                    u = u * u * (3 - 2 * u)
                    x = PACK_XY[0] + (sx - PACK_XY[0]) * u
                    y = PACK_XY[1] + (sy - PACK_XY[1]) * u
                    self.card(d, x, y, s, 1.0 - 0.3 * u)
                elif not self.new[i]:
                    u = (t - t0 - fly) / drop
                    bx = self.brick_box(i)
                    ex, ey = (bx[0] + bx[2]) / 2, (bx[1] + bx[3]) / 2
                    x = sx + (ex - sx) * u
                    y = sy + (ey - sy) * u * u
                    self.card(d, x, y, s, 0.7 - 0.3 * u)
        # Milestone tags
        if not wiped and not replay and landed >= m["total"]:
            d.text((W / 2, ALBUM_Y1 + 30), f"40 found after {m['first40']} packs   |   50 after {m['total']}", font=self.font_small, fill=TEXT, anchor="mm")
        elif not wiped and not replay and landed >= m["first40"]:
            d.text((W / 2, ALBUM_Y1 + 30), f"40 found after {m['first40']} packs", font=self.font_small, fill=TEXT, anchor="mm")
        if t >= man["payoff_t"]:
            alpha = min(1.0, (t - man["payoff_t"]) / man["payoff_hold"])
            if wiped:
                alpha *= max(0.0, 1.0 - (t - man["wipe_t"]) / (man["scene_duration"] - man["wipe_t"]))
            shade = tuple(int(c * alpha + BG[i] * (1 - alpha)) for i, c in enumerate(GOLD))
            text = man["payoff_text"].format(first40=m["first40"], last10=m["last10"], last1=m["last1"])
            d.text((W / 2, PAYOFF_Y), text, font=self.font, fill=shade, anchor="mm")
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
    man = json.loads((ROOT / "projects/stickers/manifest.json").read_text())
    meas = measure(man)
    if "--measure-only" in sys.argv:
        return
    Renderer(man, meas).render(ROOT / "media/stickers/footage.mp4")


if __name__ == "__main__":
    main()
