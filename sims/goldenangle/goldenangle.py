#!/usr/bin/env python3
"""Golden angle phyllotaxis: the same seeds placed at the golden angle and
at the golden angle plus a small offset, measured for spacing and arms.

Vogel's model: seed k sits at radius sqrt(N - k) spacing units and angle
k * alpha, where N is the number of seeds so far. New seeds appear at the
centre and older seeds move outward, so the pattern grows on screen. The
geometry at any seed count is exact and needs no seed value.

Measurements at a fixed seed count, for each angle:

- nearest-neighbour distance of every seed (min, mean, max)
- the largest empty circle inside the disc (the biggest gap)
- the parastichy count: the most common index difference between a seed
  in the outer half and its nearest neighbour, which is the number of
  spiral arms the eye follows

usage: goldenangle.py [--measure-only]
"""

from __future__ import annotations

import json
import math
import os
import subprocess
import sys
from collections import Counter
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent.parent
W, H = 1080, 1920

BG = (11, 14, 18)
SEED = (216, 222, 230)
NEW = (240, 176, 84)
GOLD = (240, 176, 84)
TEAL = (92, 200, 165)
TEXT = (216, 222, 230)
MUTED = (138, 148, 163)
GRIDLINE = (40, 48, 58)

GOLDEN_ANGLE = 360.0 / ((1.0 + math.sqrt(5.0)) / 2.0) ** 2  # 137.507764 deg

PANEL_R = 340.0
TOP_C = (540.0, 548.0)
BOT_C = (540.0, 1425.0)
TOP_LABEL_Y = 158.0
BOT_LABEL_Y = 1042.0
READOUT_DY = 358.0  # readout line below each disc centre
PAYOFF_Y = 1868.0


def positions(alpha_deg: float, n: float) -> np.ndarray:
    """Seed positions in spacing units for a (possibly fractional) count n.
    Seed k (0-based, oldest first) has radius sqrt(n - k) and angle k*alpha."""
    k = np.arange(int(math.ceil(n)))
    r = np.sqrt(n - k)
    a = np.radians(alpha_deg) * k
    return np.column_stack((r * np.cos(a), r * np.sin(a)))


def nearest(p: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Distance and index of the nearest other seed, for every seed."""
    d = np.hypot(p[:, 0, None] - p[None, :, 0], p[:, 1, None] - p[None, :, 1])
    np.fill_diagonal(d, np.inf)
    j = np.argmin(d, axis=1)
    return d[np.arange(len(p)), j], j


def largest_empty_circle(p: np.ndarray, radius: float) -> tuple[float, tuple[float, float]]:
    """Largest circle with no seed inside, centred within the given radius of
    the origin. Coarse grid, then a fine grid around the best cell."""
    def search(x0, x1, y0, y1, step):
        xs = np.arange(x0, x1 + step / 2, step)
        ys = np.arange(y0, y1 + step / 2, step)
        gx, gy = np.meshgrid(xs, ys)
        g = np.column_stack((gx.ravel(), gy.ravel()))
        g = g[np.hypot(g[:, 0], g[:, 1]) <= radius]
        best_d, best_c = -1.0, (0.0, 0.0)
        for i in range(0, len(g), 20000):
            chunk = g[i:i + 20000]
            d = np.hypot(chunk[:, 0, None] - p[None, :, 0], chunk[:, 1, None] - p[None, :, 1]).min(axis=1)
            k = int(np.argmax(d))
            if d[k] > best_d:
                best_d, best_c = float(d[k]), (float(chunk[k, 0]), float(chunk[k, 1]))
        return best_d, best_c

    d0, c0 = search(-radius, radius, -radius, radius, 0.1)
    d1, c1 = search(c0[0] - 0.15, c0[0] + 0.15, c0[1] - 0.15, c0[1] + 0.15, 0.005)
    return (d1, c1) if d1 >= d0 else (d0, c0)


def arms(p: np.ndarray, j: np.ndarray) -> tuple[int, float]:
    """Parastichy count: the most common |k - nearest(k)| over the outer half
    of the seeds, and the share of outer seeds that agree with it."""
    n = len(p)
    outer = np.arange(n // 2, n)
    diffs = np.abs(outer - j[outer])
    count = Counter(diffs.tolist())
    k, c = count.most_common(1)[0]
    return int(k), c / len(outer)


def ring_arms(p: np.ndarray, r_lo: float, r_hi: float, gap_factor: float = 1.5) -> int:
    """Count angular clusters of the seeds in one ring: the number of gaps
    wider than gap_factor times the mean gap. Zero means evenly spread."""
    r = np.hypot(p[:, 0], p[:, 1])
    a = np.sort(np.degrees(np.arctan2(p[:, 1], p[:, 0]))[(r >= r_lo) & (r < r_hi)])
    if len(a) < 4:
        return 0
    gaps = np.diff(np.append(a, a[0] + 360.0))
    return int(np.sum(gaps > gap_factor * 360.0 / len(a)))


def touching_chains(p: np.ndarray, seed_w: float) -> tuple[int, int, int]:
    """Connected components of the graph that links seeds closer than one
    seed width: (chains of 2 or more seeds, chains of 3 or more, longest)."""
    n = len(p)
    d = np.hypot(p[:, 0, None] - p[None, :, 0], p[:, 1, None] - p[None, :, 1])
    parent = list(range(n))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    ii, jj = np.nonzero(np.triu(d < seed_w, 1))
    for i, j in zip(ii.tolist(), jj.tolist()):
        parent[find(i)] = find(j)
    sizes = Counter(find(i) for i in range(n))
    big = [c for c in sizes.values() if c >= 2]
    return len(big), sum(1 for c in big if c >= 3), (max(big) if big else 0)


def stats(alpha_deg: float, n: int, seed_w: float) -> dict:
    p = positions(alpha_deg, float(n))
    d, j = nearest(p)
    gap_r, gap_c = largest_empty_circle(p, math.sqrt(n) - 1.0)
    k, share = arms(p, j)
    chains2, chains3, longest = touching_chains(p, seed_w)
    return {
        "chains2": chains2, "chains3": chains3, "longest": longest,
        "alpha": alpha_deg, "n": n,
        "nn_min": float(d.min()), "nn_mean": float(d.mean()), "nn_max": float(d.max()),
        "nn_min_outer": float(d[n // 2:].min()), "nn_max_outer": float(d[n // 2:].max()),
        "gap_r": gap_r, "gap_c": gap_c, "gap_w": 2.0 * gap_r,
        "arms": k, "arms_share": share,
        "ring_arms": ring_arms(p, math.sqrt(n) - 2.0, math.sqrt(n) - 1.0),
        "touching": int(np.sum(d < seed_w)),
        "seed_w": seed_w,
    }


def describe(s: dict) -> None:
    sw = s["seed_w"]
    print(f"  angle {s['alpha']:.4f} deg, {s['n']} seeds:")
    print(f"    nearest neighbour: min {s['nn_min']:.3f}, mean {s['nn_mean']:.3f}, max {s['nn_max']:.3f} "
          f"(outer half: min {s['nn_min_outer']:.3f}, max {s['nn_max_outer']:.3f}); spread max/min {s['nn_max'] / s['nn_min']:.2f}; "
          f"closest pair {s['nn_min'] / sw:.2f} seed widths apart; {s['touching']} seeds touch a neighbour (closer than one seed width)")
    print(f"    biggest gap: empty circle of diameter {s['gap_w']:.3f} at ({s['gap_c'][0]:.2f}, {s['gap_c'][1]:.2f}), "
          f"radius {math.hypot(*s['gap_c']):.2f}; that is {s['gap_w'] / sw:.2f} seed widths wide")
    print(f"    arms: nearest-neighbour index difference mode {s['arms']} ({100 * s['arms_share']:.1f}% of outer seeds); "
          f"outer ring has {s['ring_arms']} wide angular gaps; touching chains: {s['chains2']} of 2+ seeds, "
          f"{s['chains3']} of 3+ seeds, longest {s['longest']} seeds")


def measure(man: dict) -> dict:
    n = man["seeds"]
    sw = man["seed_width"]
    a0 = GOLDEN_ANGLE
    a1 = a0 + man["offset_deg"]
    print(f"golden angle 360/phi^2 = {a0:.6f} deg; offset {man['offset_deg']:+.3f} deg -> {a1:.6f} deg; "
          f"{n} seeds; seed dot width {sw:.2f} spacing units")
    out = {}
    for name, a in (("golden", a0), ("offset", a1)):
        print(f"{name}:")
        out[name] = {}
        for m in man["report_counts"]:
            s = stats(a, m, sw)
            describe(s)
            out[name][m] = s
    print("context (not narrated): other offsets at the final count")
    for off in (-man["offset_deg"], man["offset_deg"] / 2, 2 * man["offset_deg"]):
        describe(stats(a0 + off, n, sw))
    g, o = out["golden"][n], out["offset"][n]
    print(f"ratios at {n} seeds: biggest gap {o['gap_w'] / g['gap_w']:.2f}x wider with the offset; "
          f"closest pair {g['nn_min'] / o['nn_min']:.2f}x closer with the offset; "
          f"golden gap {g['gap_w'] / sw:.2f} seed widths, offset gap {o['gap_w'] / sw:.2f} seed widths")
    # Events on the offset disc as the count grows, one seed at a time.
    first_touch = first_34 = None
    per_seed = True
    prev = None
    for m in range(2, n + 1):
        p = positions(a1, float(m))
        d, _ = nearest(p)
        touch = int(np.sum(d < sw))
        if first_touch is None and touch:
            first_touch = m
        if first_34 is None and touching_chains(p, sw)[0] == 34:
            first_34 = m
        if first_34 is not None and prev is not None and touch - prev != 1:
            per_seed = False
        prev = touch
    keys = man["count_keys"]

    def t_of(m):
        for (t0, n0), (t1, n1) in zip(keys, keys[1:]):
            if m <= n1:
                return t0 + (t1 - t0) * (m - n0) / (n1 - n0)
        return keys[-1][0]

    print(f"offset disc events: first touching pair at {first_touch} seeds ({t_of(first_touch):.2f} s of video); "
          f"34 touching chains from {first_34} seeds ({t_of(first_34):.2f} s); "
          f"from there every new seed adds exactly one touching seed: {per_seed}; "
          f"{n} seeds at {t_of(n):.2f} s")
    # Residuals of k*alpha modulo 360 (the arithmetic behind the arm count).
    for name, a in (("golden", a0), ("offset", a1)):
        res = []
        for k in range(1, 200):
            r = (k * a + 180.0) % 360.0 - 180.0
            res.append((abs(r), k, r))
        best = sorted(res)[:4]
        print(f"  {name}: smallest |k*alpha mod 360| for k<200: " +
              ", ".join(f"k={k}: {r:+.2f} deg" for _, k, r in best))
    return out


class Renderer:
    def __init__(self, man: dict, meas: dict):
        self.man, self.meas = man, meas
        self.fps = man["fps"]
        font = os.environ["SEED_ZERO_FONT"]
        self.font = ImageFont.truetype(font, 40)
        self.font_small = ImageFont.truetype(font, 32)
        self.font_tiny = ImageFont.truetype(font, 26)
        self.scale = PANEL_R / math.sqrt(man["seeds"])
        self.dot = 0.5 * man["seed_width"] * self.scale
        self.a0 = GOLDEN_ANGLE
        self.a1 = GOLDEN_ANGLE + man["offset_deg"]

    def count_at(self, t: float) -> float:
        man = self.man
        keys = man["count_keys"]
        if t <= keys[0][0]:
            return keys[0][1]
        for (t0, n0), (t1, n1) in zip(keys, keys[1:]):
            if t <= t1:
                u = (t - t0) / (t1 - t0)
                return n0 + (n1 - n0) * u
        return keys[-1][1]

    def draw_panel(self, d: ImageDraw.ImageDraw, centre, alpha: float, n: float) -> dict:
        """Draw one disc; seeds closer than one seed width to a neighbour are
        gold. Returns the live readouts."""
        p = positions(alpha, n)
        dist, _ = nearest(p)
        touching = dist < self.man["seed_width"]
        cx, cy = centre
        d.ellipse((cx - PANEL_R - 8, cy - PANEL_R - 8, cx + PANEL_R + 8, cy + PANEL_R + 8), outline=GRIDLINE, width=2)
        r = self.dot
        for i, (x, y) in enumerate(p):
            px, py = cx + x * self.scale, cy - y * self.scale
            col = NEW if (i == len(p) - 1 or touching[i]) else SEED
            d.ellipse((px - r, py - r, px + r, py + r), fill=col)
        return {"touching": int(touching.sum()), "nn_min": float(dist.min())}

    def frame_at(self, f: int) -> np.ndarray:
        man = self.man
        t = f / self.fps
        n = self.count_at(t)
        n_final = man["seeds"]
        img = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(img)
        payoff = t >= man["payoff_t"]
        live_g = self.draw_panel(d, TOP_C, self.a0, n)
        live_o = self.draw_panel(d, BOT_C, self.a1, n)
        # Labels: name left, angle and count right, one line above each disc;
        # live readouts one line below each disc.
        sw = man["seed_width"]
        d.text((60, TOP_LABEL_Y), "golden angle", font=self.font, fill=TEXT, anchor="lm")
        d.text((1020, TOP_LABEL_Y), f"{self.a0:.3f} deg  |  {int(n):,} seeds", font=self.font_small, fill=MUTED, anchor="rm")
        d.text((60, BOT_LABEL_Y), f"plus {man['offset_deg']:.1f} deg", font=self.font, fill=GOLD, anchor="lm")
        d.text((1020, BOT_LABEL_Y), f"{self.a1:.3f} deg  |  {int(n):,} seeds", font=self.font_small, fill=MUTED, anchor="rm")
        for live, centre in ((live_g, TOP_C), (live_o, BOT_C)):
            y = centre[1] + READOUT_DY
            col = GOLD if live["touching"] else MUTED
            d.text((60, y), f"closest pair {live['nn_min'] / sw:.2f} seed widths apart", font=self.font_tiny, fill=MUTED, anchor="lm")
            d.text((1020, y), f"{live['touching']} seeds touching", font=self.font_tiny, fill=col, anchor="rm")
        if payoff:
            alpha_f = min(1.0, (t - man["payoff_t"]) / man["payoff_hold"])
            shade = tuple(int(c * alpha_f + BG[i] * (1 - alpha_f)) for i, c in enumerate(GOLD))
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
    man = json.loads((ROOT / "projects/goldenangle/manifest.json").read_text())
    meas = measure(man)
    if "--measure-only" in sys.argv:
        return
    Renderer(man, meas).render(ROOT / "media/goldenangle/footage.mp4")


if __name__ == "__main__":
    main()
