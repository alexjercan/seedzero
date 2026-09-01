#!/usr/bin/env python3
"""A* versus breadth-first search on one seeded grid of walls.

Both searches run on the same grid, from the same start to the same goal,
with the same four-neighbour moves. Every cell either search removes from
its queue is counted as one check. The replay plays both check logs at one
shared rate, so the two panels are always at the same number of checks. Both
paths are asserted to be the same length before anything is rendered.

A* uses the Manhattan heuristic with the standard prefer-higher-g tie break,
which keeps the path optimal and stops it from spreading over the plateau of
equally good routes.

usage: pathrace.py [--measure-only]
"""

from __future__ import annotations

import heapq
import json
import os
import subprocess
import sys
from collections import deque
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent.parent
W, H = 1080, 1920

BG = (11, 14, 18)
WALL = (35, 42, 52)
OPEN = (19, 24, 31)
SEEN = (64, 116, 176)
GLOW = (196, 226, 255)
PATH = (92, 200, 165)
START = (92, 200, 165)
GOAL = (240, 176, 84)
TEXT = (216, 222, 230)
MUTED = (138, 148, 163)

# Layout. The caption band burned in by compose.sh sits at y = 1344..1420.
PANEL_X0 = 60
PANEL_TOP = {"bfs": 260, "astar": 840}
LABEL_DY = -52
COUNT_DY = -46
READOUT_Y = 1560.0
PAYOFF_Y = 1868.0
GLOW_TAU = 90.0
GLOW_FLOOR = 0.34
MOVES = ((-1, 0), (1, 0), (0, -1), (0, 1))


def build_grid(man: dict) -> np.ndarray:
    """Rectangular wall blocks dropped at seeded positions. True = walkable."""
    rng = np.random.RandomState(man["seed"])
    gw, gh = man["grid_w"], man["grid_h"]
    grid = np.ones((gh, gw), dtype=bool)
    for _ in range(man["blocks"]):
        bw = rng.randint(man["block_min"], man["block_max"])
        bh = rng.randint(man["block_min"], man["block_max"])
        x = rng.randint(0, gw - bw)
        y = rng.randint(0, gh - bh)
        grid[y:y + bh, x:x + bw] = False
    grid[0, :] = grid[-1, :] = True
    grid[:, 0] = grid[:, -1] = True
    return grid


def bfs(grid, start, goal):
    gh, gw = grid.shape
    prev = {start: None}
    queue = deque([start])
    order = []
    while queue:
        cell = queue.popleft()
        order.append(cell)
        if cell == goal:
            break
        y, x = cell
        for dy, dx in MOVES:
            nxt = (y + dy, x + dx)
            if 0 <= nxt[0] < gh and 0 <= nxt[1] < gw and grid[nxt] and nxt not in prev:
                prev[nxt] = cell
                queue.append(nxt)
    return order, prev


def astar(grid, start, goal):
    gh, gw = grid.shape

    def h(c):
        return abs(c[0] - goal[0]) + abs(c[1] - goal[1])

    prev = {start: None}
    best = {start: 0}
    heap = [(h(start), 0, start)]
    order = []
    closed = set()
    while heap:
        _, neg_g, cell = heapq.heappop(heap)
        if cell in closed:
            continue
        closed.add(cell)
        order.append(cell)
        if cell == goal:
            break
        y, x = cell
        cost = -neg_g + 1
        for dy, dx in MOVES:
            nxt = (y + dy, x + dx)
            if (0 <= nxt[0] < gh and 0 <= nxt[1] < gw and grid[nxt]
                    and cost < best.get(nxt, 1 << 30)):
                best[nxt] = cost
                prev[nxt] = cell
                heapq.heappush(heap, (cost + h(nxt), -cost, nxt))
    return order, prev


def trace(prev, goal):
    cells = []
    cell = goal
    while cell is not None:
        cells.append(cell)
        cell = prev[cell]
    return cells[::-1]


def measure_report(man: dict) -> dict:
    grid = build_grid(man)
    gh, gw = grid.shape
    start, goal = (2, 2), (gh - 3, gw - 3)
    assert grid[start] and grid[goal], "endpoint is inside a wall"

    b_order, b_prev = bfs(grid, start, goal)
    a_order, a_prev = astar(grid, start, goal)
    assert goal in b_prev and goal in a_prev, "goal unreachable"
    b_path, a_path = trace(b_prev, goal), trace(a_prev, goal)
    assert len(b_path) == len(a_path), "paths differ in length"
    for path in (b_path, a_path):
        assert path[0] == start and path[-1] == goal
        for u, v in zip(path, path[1:]):
            assert abs(u[0] - v[0]) + abs(u[1] - v[1]) == 1 and grid[v]

    walkable = int(grid.sum())
    print(f"grid {gw}x{gh} = {gw * gh} cells, {walkable} walkable, "
          f"{man['blocks']} wall blocks at seed {man['seed']}")
    print(f"start {start} -> goal {goal}")
    print(f"breadth first: {len(b_order)} cells checked "
          f"({100 * len(b_order) / walkable:.1f}% of the walkable grid)")
    print(f"A star:        {len(a_order)} cells checked")
    print(f"ratio: {len(b_order) / len(a_order):.1f} to 1")
    print(f"path length: {len(b_path)} cells, identical for both searches")
    return {"grid": grid, "start": start, "goal": goal,
            "b_order": b_order, "a_order": a_order,
            "b_path": b_path, "a_path": a_path,
            "walkable": walkable,
            "ratio": len(b_order) / len(a_order)}


class Renderer:
    def __init__(self, man, meas):
        self.man = man
        self.meas = meas
        self.fps = man["fps"]
        self.cell = man["cell_px"]
        self.grid = meas["grid"]
        gh, gw = self.grid.shape
        self.gw, self.gh = gw, gh
        self.total = len(meas["b_order"])
        font = os.environ["SEED_ZERO_FONT"]
        self.font = ImageFont.truetype(font, 40)
        self.font_small = ImageFont.truetype(font, 34)

        self.runs = {}
        for key, order, path in (("bfs", meas["b_order"], meas["b_path"]),
                                 ("astar", meas["a_order"], meas["a_path"])):
            idx = np.full((gh, gw), -1, dtype=np.int32)
            ys = np.fromiter((c[0] for c in order), int, len(order))
            xs = np.fromiter((c[1] for c in order), int, len(order))
            idx[ys, xs] = np.arange(len(order))
            pmask = np.zeros((gh, gw), dtype=bool)
            pmask[[c[0] for c in path], [c[1] for c in path]] = True
            self.runs[key] = {"idx": idx, "n": len(order), "path": pmask}

        base = np.empty((gh, gw, 3), dtype=np.uint8)
        base[:] = OPEN
        base[~self.grid] = WALL
        self.base = base

    def checks_at(self, t: float) -> float:
        """Shared replay schedule: a slow opening, then a constant race rate."""
        m = self.man
        if t <= 0:
            return 0.0
        if t < m["slow_end"]:
            return m["slow_cells"] * t / m["slow_end"]
        if t < m["race_end"]:
            frac = (t - m["slow_end"]) / (m["race_end"] - m["slow_end"])
            return m["slow_cells"] + (self.total - m["slow_cells"]) * frac
        return float(self.total)

    def panel(self, key: str, checks: int) -> tuple[np.ndarray, int, bool]:
        run = self.runs[key]
        shown = min(checks, run["n"])
        done = checks >= run["n"]
        img = self.base.copy()
        seen = (run["idx"] >= 0) & (run["idx"] < shown)
        age = (shown - 1 - run["idx"][seen]).astype(np.float32)
        alpha = GLOW_FLOOR + (1.0 - GLOW_FLOOR) * np.exp(-age / GLOW_TAU)
        ramp = (np.array(SEEN, dtype=np.float32)
                + alpha[:, None] * (np.array(GLOW, dtype=np.float32)
                                    - np.array(SEEN, dtype=np.float32)))
        img[seen] = ramp.astype(np.uint8)
        if done:
            img[run["path"]] = PATH
        for cell, color in ((self.meas["start"], START), (self.meas["goal"], GOAL)):
            y, x = cell
            img[max(0, y - 1):y + 2, max(0, x - 1):x + 2] = color
        return np.repeat(np.repeat(img, self.cell, 0), self.cell, 1), shown, done

    def frame_at(self, t: float) -> np.ndarray:
        checks = int(self.checks_at(t))
        frame = np.zeros((H, W, 3), dtype=np.uint8)
        frame[:, :] = BG
        states = {}
        for key in ("bfs", "astar"):
            block, shown, done = self.panel(key, checks)
            top = PANEL_TOP[key]
            frame[top:top + block.shape[0],
                  PANEL_X0:PANEL_X0 + block.shape[1]] = block
            states[key] = (shown, done)

        img = Image.fromarray(frame)
        d = ImageDraw.Draw(img)
        panel_x1 = PANEL_X0 + self.gw * self.cell
        for key, label in (("bfs", "breadth first"), ("astar", "A star")):
            shown, done = states[key]
            y = PANEL_TOP[key] + LABEL_DY
            d.text((PANEL_X0, y), label, font=self.font, fill=MUTED, anchor="lm")
            suffix = "  found it" if done else ""
            d.text((panel_x1, y), f"{shown:,} checked{suffix}",
                   font=self.font, fill=PATH if done else TEXT, anchor="rm")
        if states["astar"][1] and not states["bfs"][1]:
            d.text((W / 2, READOUT_Y),
                   f"A star finished after {self.runs['astar']['n']:,} cells",
                   font=self.font, fill=PATH, anchor="mm")
        elif states["bfs"][1]:
            d.text((W / 2, READOUT_Y),
                   f"same path: {len(self.meas['b_path']):,} cells long",
                   font=self.font, fill=PATH, anchor="mm")
        alpha = min(1.0, max(0.0, (t - self.man["payoff_fade"]) / 0.6))
        if alpha > 0:
            shade = tuple(int(c * alpha + BG[i] * (1 - alpha))
                          for i, c in enumerate(TEXT))
            d.text((W / 2, PAYOFF_Y),
                   f"{self.runs['bfs']['n']:,} checks vs "
                   f"{self.runs['astar']['n']:,}",
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
    man = json.loads((ROOT / "projects/pathrace/manifest.json").read_text())
    meas = measure_report(man)
    if "--measure-only" in sys.argv:
        return
    Renderer(man, meas).render(ROOT / "media/pathrace/footage.mp4")


if __name__ == "__main__":
    main()
