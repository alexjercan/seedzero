#!/usr/bin/env python3
"""Site percolation on a square grid: cells open one at a time in a seeded
random order, and the sim records the exact moment a path of open cells
first connects the top edge to the bottom edge.

The on-screen grid is seed 0. The same experiment is repeated on an
ensemble of seeded grids of the same size, and the fraction filled at the
moment of connection is recorded for every one of them. Union-find with
virtual top and bottom nodes decides connection; the biggest cluster is
tracked exactly at every step.

usage: percolation.py [--measure-only]
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
CLOSED = (19, 24, 31)
OPEN = (58, 92, 132)
BIG = (92, 200, 165)
SPAN = (240, 176, 84)
TEXT = (216, 222, 230)
MUTED = (138, 148, 163)
CURVE = (92, 200, 165)
BAND = (240, 176, 84)

GRID_X0, GRID_Y0 = 90, 190
READOUT_Y = 1150
CHART_X0, CHART_X1 = 130, 1000
CHART_Y0, CHART_Y1 = 1480, 1810
PAYOFF_Y = 1875


class UnionFind:
    def __init__(self, n: int):
        self.parent = list(range(n))
        self.size = [1] * n

    def find(self, a: int) -> int:
        p = self.parent
        while p[a] != a:
            p[a] = p[p[a]]
            a = p[a]
        return a

    def union(self, a: int, b: int) -> int:
        a, b = self.find(a), self.find(b)
        if a == b:
            return a
        if self.size[a] < self.size[b]:
            a, b = b, a
        self.parent[b] = a
        self.size[a] += self.size[b]
        return a


def run_grid(seed: int, gw: int, gh: int, want_curve: bool):
    """Open sites in seeded order. Returns the step of first connection, the
    order, and (optionally) the biggest-cluster size after every step."""
    n = gw * gh
    top, bottom = n, n + 1
    rng = np.random.RandomState(seed)
    order = rng.permutation(n)
    uf = UnionFind(n + 2)
    uf.size[top] = uf.size[bottom] = 0
    is_open = bytearray(n)
    biggest = 1
    curve = [] if want_curve else None
    span_step = None
    for step, s in enumerate(order, start=1):
        s = int(s)
        is_open[s] = 1
        y, x = divmod(s, gw)
        root = s
        if y == 0:
            root = uf.union(root, top)
        if y == gh - 1:
            root = uf.union(root, bottom)
        if x > 0 and is_open[s - 1]:
            root = uf.union(root, s - 1)
        if x < gw - 1 and is_open[s + 1]:
            root = uf.union(root, s + 1)
        if y > 0 and is_open[s - gw]:
            root = uf.union(root, s - gw)
        if y < gh - 1 and is_open[s + gw]:
            root = uf.union(root, s + gw)
        if uf.size[root] > biggest:
            biggest = uf.size[root]
        if curve is not None:
            curve.append(biggest)
        if span_step is None and uf.find(top) == uf.find(bottom):
            span_step = step
            if curve is None:
                break
    return span_step, order, curve


def measure(man: dict) -> dict:
    gw, gh = man["grid_w"], man["grid_h"]
    n = gw * gh
    span_step, order, curve = run_grid(man["seed"], gw, gh, True)
    curve = np.array(curve) / n
    p_span = span_step / n
    print(f"grid {gw}x{gh} = {n} cells, seed {man['seed']}, cells open one at a time in random order")
    print(f"first top-to-bottom path at cell {span_step}: {100 * p_span:.2f}% filled")
    for f in (0.40, 0.50, 0.55, 0.58, p_span, 0.62, 0.65, 0.70):
        step = int(round(f * n))
        print(f"  biggest cluster at {100 * f:6.2f}% filled: {100 * curve[step - 1]:5.1f}% of the grid")
    before = int(round((p_span - 0.05) * n))
    after = int(round((p_span + 0.05) * n))
    print(f"  biggest cluster 5 points before connection: {100 * curve[before - 1]:.1f}%, "
          f"5 points after: {100 * curve[after - 1]:.1f}%")
    spans = []
    for seed in range(man["ensemble"]):
        s, _, _ = run_grid(seed, gw, gh, False)
        spans.append(s / n)
    spans = np.array(spans)
    print(f"ensemble of {man['ensemble']} grids (seeds 0-{man['ensemble'] - 1}), same size:")
    print(f"  connection fraction min {100 * spans.min():.2f}%, max {100 * spans.max():.2f}%, "
          f"mean {100 * spans.mean():.2f}%, median {100 * np.median(spans):.2f}%, "
          f"std {100 * spans.std():.2f} points")
    lo, hi = np.floor(100 * spans.min()), np.ceil(100 * spans.max())
    hist, edges = np.histogram(100 * spans, bins=np.arange(lo, hi + 1, 1.0))
    for c, e in zip(hist, edges):
        print(f"  {e:5.1f}-{e + 1:5.1f}%: {c}")
    for w in (0.02, 0.03, 0.05):
        inside = int(np.sum(np.abs(spans - 0.5927) <= w))
        print(f"  within {100 * w:.0f} points of 59.27%: {inside} of {man['ensemble']}")
    print(f"  never below {100 * spans.min():.2f}%, never above {100 * spans.max():.2f}%; "
          f"theory for an infinite grid: 59.27%")
    return {"order": order, "curve": curve, "span_step": span_step, "p_span": p_span,
            "spans": spans}


class Renderer:
    def __init__(self, man: dict, meas: dict):
        self.man, self.meas = man, meas
        self.gw, self.gh = man["grid_w"], man["grid_h"]
        self.n = self.gw * self.gh
        self.cell = man["cell_px"]
        self.fps = man["fps"]
        font = os.environ["SEED_ZERO_FONT"]
        self.font = ImageFont.truetype(font, 40)
        self.font_small = ImageFont.truetype(font, 32)
        self.order = meas["order"]
        self.uf = UnionFind(self.n + 2)
        self.uf.size[self.n] = self.uf.size[self.n + 1] = 0
        self.is_open = bytearray(self.n)
        self.opened = 0
        self.spanned = False

    def fill_at(self, t: float) -> int:
        keys = self.man["fill_keys"]
        if t <= keys[0][0]:
            frac = keys[0][1]
        elif t >= keys[-1][0]:
            frac = keys[-1][1]
        else:
            for (t0, f0), (t1, f1) in zip(keys, keys[1:]):
                if t0 <= t <= t1:
                    frac = f0 + (f1 - f0) * (t - t0) / (t1 - t0)
                    break
        return int(round(frac * self.n))

    def advance(self, target: int) -> None:
        gw, gh, n = self.gw, self.gh, self.n
        uf, is_open = self.uf, self.is_open
        while self.opened < target:
            s = int(self.order[self.opened])
            self.opened += 1
            is_open[s] = 1
            y, x = divmod(s, gw)
            if y == 0:
                uf.union(s, n)
            if y == gh - 1:
                uf.union(s, n + 1)
            if x > 0 and is_open[s - 1]:
                uf.union(s, s - 1)
            if x < gw - 1 and is_open[s + 1]:
                uf.union(s, s + 1)
            if y > 0 and is_open[s - gw]:
                uf.union(s, s - gw)
            if y < gh - 1 and is_open[s + gw]:
                uf.union(s, s + gw)
            if not self.spanned and uf.find(n) == uf.find(n + 1):
                self.spanned = True
                self.span_t = None

    def roots(self) -> np.ndarray:
        parent = np.array(self.uf.parent)
        r = parent[np.arange(self.n)]
        while True:
            nxt = parent[r]
            if np.array_equal(nxt, r):
                return r
            r = nxt

    def frame_at(self, t: float) -> np.ndarray:
        man = self.man
        target = self.fill_at(t)
        was_spanned = self.spanned
        self.advance(target)
        if self.spanned and not was_spanned:
            self.span_video_t = t
        open_mask = np.frombuffer(bytes(self.is_open), dtype=np.uint8).astype(bool)
        roots = self.roots()
        counts = np.bincount(roots[open_mask], minlength=self.n + 2)
        big_root = int(np.argmax(counts))
        big_size = int(counts[big_root])
        grid = np.empty((self.n, 3), dtype=np.uint8)
        grid[:] = CLOSED
        grid[open_mask] = OPEN
        big_mask = open_mask & (roots == big_root)
        if self.spanned:
            span_root = self.uf.find(self.n)
            span_mask = open_mask & (roots == span_root)
            grid[big_mask] = BIG
            grid[span_mask] = SPAN
        else:
            grid[big_mask] = BIG
        block = grid.reshape(self.gh, self.gw, 3)
        block = np.repeat(np.repeat(block, self.cell, 0), self.cell, 1)

        frame = np.zeros((H, W, 3), dtype=np.uint8)
        frame[:] = BG
        gy1 = GRID_Y0 + block.shape[0]
        gx1 = GRID_X0 + block.shape[1]
        frame[GRID_Y0:gy1, GRID_X0:gx1] = block
        # Edge bars: the two sides that must connect.
        bar = SPAN if self.spanned else MUTED
        frame[GRID_Y0 - 14:GRID_Y0 - 6, GRID_X0:gx1] = bar
        frame[gy1 + 6:gy1 + 14, GRID_X0:gx1] = bar

        img = Image.fromarray(frame)
        d = ImageDraw.Draw(img)
        filled = 100 * self.opened / self.n
        big = 100 * big_size / self.n
        d.text((GRID_X0, READOUT_Y), f"filled {filled:5.1f}%", font=self.font, fill=TEXT, anchor="lm")
        d.text((gx1, READOUT_Y), f"biggest cluster {big:5.1f}%", font=self.font,
               fill=SPAN if self.spanned else BIG, anchor="rm")
        status = "top and bottom connected" if self.spanned else "no path from top to bottom"
        d.text((W / 2, READOUT_Y + 62), status, font=self.font_small,
               fill=SPAN if self.spanned else MUTED, anchor="mm")

        # Chart: biggest cluster share against filled share.
        d.rectangle((CHART_X0, CHART_Y0, CHART_X1, CHART_Y1), outline=(40, 48, 58), width=2)
        d.text((CHART_X0, CHART_Y0 - 28), "biggest cluster", font=self.font_small, fill=MUTED, anchor="lm")
        d.text((CHART_X1, CHART_Y1 + 26), "filled", font=self.font_small, fill=MUTED, anchor="rm")
        fill_end = man["fill_keys"][-1][1]

        def cx(f):
            return CHART_X0 + (CHART_X1 - CHART_X0) * f / fill_end

        def cy(v):
            return CHART_Y1 - (CHART_Y1 - CHART_Y0) * v

        for f in (0.2, 0.4, 0.6):
            d.line((cx(f), CHART_Y1, cx(f), CHART_Y1 + 8), fill=MUTED, width=2)
            d.text((cx(f), CHART_Y1 + 26), f"{int(100 * f)}%", font=self.font_small, fill=MUTED, anchor="mm")
        if self.spanned:
            spans = self.meas["spans"]
            x0, x1 = cx(spans.min()), cx(spans.max())
            band = Image.new("RGBA", img.size, (0, 0, 0, 0))
            bd = ImageDraw.Draw(band)
            bd.rectangle((x0, CHART_Y0 + 2, x1, CHART_Y1 - 2), fill=BAND + (60,))
            img = Image.alpha_composite(img.convert("RGBA"), band).convert("RGB")
            d = ImageDraw.Draw(img)
        curve = self.meas["curve"]
        pts = []
        step = max(1, self.opened // 300)
        for k in range(0, self.opened, step):
            pts.append((cx((k + 1) / self.n), cy(curve[k])))
        if self.opened:
            pts.append((cx(self.opened / self.n), cy(curve[self.opened - 1])))
        if len(pts) > 1:
            d.line(pts, fill=CURVE, width=4)
        if self.spanned:
            xs = cx(self.meas["p_span"])
            d.line((xs, CHART_Y0, xs, CHART_Y1), fill=SPAN, width=3)
            d.text((xs - 12, CHART_Y0 + 24), f"this grid {100 * self.meas['p_span']:.1f}%",
                   font=self.font_small, fill=SPAN, anchor="rm")
            spans = self.meas["spans"]
            xm = cx(spans.mean())
            d.line((xm, CHART_Y0, xm, CHART_Y1), fill=TEXT, width=2)
            d.text((xm - 12, CHART_Y0 + 66), f"{len(spans):,} grids: average {100 * spans.mean():.2f}%",
                   font=self.font_small, fill=TEXT, anchor="rm")
            alpha = min(1.0, (t - self.span_video_t) / man["payoff_hold"])
            shade = tuple(int(c * alpha + BG[i] * (1 - alpha)) for i, c in enumerate(SPAN))
            d.text((W / 2, PAYOFF_Y),
                   f"{len(spans):,} grids: {100 * spans.mean():.2f}%. theory: 59.27%",
                   font=self.font, fill=shade, anchor="mm")
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
            proc.stdin.write(self.frame_at(f / self.fps).tobytes())
            if f % 300 == 0:
                print(f"frame {f}/{total}", file=sys.stderr)
        proc.stdin.close()
        if proc.wait() != 0:
            raise RuntimeError("ffmpeg failed")
        print(f"footage: {out_path} ({total / self.fps:.2f}s at {self.fps} fps)")


def main() -> None:
    man = json.loads((ROOT / "projects/percolation/manifest.json").read_text())
    meas = measure(man)
    if "--measure-only" in sys.argv:
        return
    Renderer(man, meas).render(ROOT / "media/percolation/footage.mp4")


if __name__ == "__main__":
    main()
