#!/usr/bin/env python3
"""Gosper glider gun in Conway's Game of Life on an unbounded grid.

The grid is a set of live cells, so nothing is ever clipped: gliders that
leave the visible window keep flying and keep being counted. The sim
measures the exact live-cell count at every generation, the generation at
which each glider separates from the gun, the gun's period, and the glider
speed. The window shows the gun and the stream of gliders it fires.

usage: lifegun.py [--measure-only]
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
GRID = (19, 24, 31)
GUN = (92, 200, 165)
GLIDER = (240, 176, 84)
TEXT = (216, 222, 230)
MUTED = (138, 148, 163)
GRIDLINE = (40, 48, 58)

GRID_Y0 = 190
CHART_X0, CHART_X1 = 130, 1000
CHART_Y0, CHART_Y1 = 1500, 1800
PAYOFF_Y = 1875

GOSPER = """
........................O...........
......................O.O...........
............OO......OO............OO
...........O...O....OO............OO
OO........O.....O...OO..............
OO........O...O.OO....O.O...........
..........O.....O.......O...........
...........O...O....................
............OO......................
"""

NEIGH = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]


def parse(pattern: str, ox: int, oy: int) -> frozenset:
    cells = set()
    for y, row in enumerate(l for l in pattern.strip("\n").splitlines()):
        for x, ch in enumerate(row):
            if ch == "O":
                cells.add((x + ox, y + oy))
    return frozenset(cells)


def step(cells: frozenset) -> frozenset:
    counts: dict = {}
    for (x, y) in cells:
        for dx, dy in NEIGH:
            k = (x + dx, y + dy)
            counts[k] = counts.get(k, 0) + 1
    return frozenset(k for k, c in counts.items() if c == 3 or (c == 2 and k in cells))


def components(cells: set) -> list[set]:
    seen: set = set()
    out = []
    for c in cells:
        if c in seen:
            continue
        comp = set()
        stack = [c]
        seen.add(c)
        while stack:
            x, y = stack.pop()
            comp.add((x, y))
            for dx, dy in NEIGH:
                k = (x + dx, y + dy)
                if k in cells and k not in seen:
                    seen.add(k)
                    stack.append(k)
        out.append(comp)
    return out


GLIDER_SEED = """
.O.
..O
OOO
"""


def normalize(comp) -> frozenset:
    x0 = min(x for x, _ in comp)
    y0 = min(y for _, y in comp)
    return frozenset((x - x0, y - y0) for x, y in comp)


def glider_shapes() -> set:
    """The four phases of a glider heading down-right, normalized."""
    cells = parse(GLIDER_SEED, 0, 0)
    shapes = set()
    for _ in range(4):
        shapes.add(normalize(cells))
        cells = step(cells)
    return shapes


SHAPES = glider_shapes()


def split(cells: frozenset) -> tuple[set, list[set]]:
    """Separate the live cells into gun cells and a list of gliders. A glider
    is a 5-cell component with exactly a glider shape; everything else is
    the gun."""
    gun: set = set()
    gliders = []
    for comp in components(set(cells)):
        if len(comp) == 5 and normalize(comp) in SHAPES:
            gliders.append(comp)
        else:
            gun |= comp
    return gun, gliders


def measure(man: dict) -> dict:
    cells = parse(GOSPER, *man["gun_origin"])
    n_gen = man["generations"]
    print(f"Gosper glider gun, {len(cells)} live cells at generation 0, unbounded grid, "
          f"{n_gen} generations; a glider is a 5-cell component with one of the 4 glider shapes")
    history = [cells]
    live = [len(cells)]
    gun0, gl0 = split(cells)
    assert not gl0
    gliders = [0]
    glider_cells = [frozenset()]
    launches = []
    gun_states = [frozenset(gun0)]
    lead = {}
    for g in range(1, n_gen + 1):
        cells = step(cells)
        history.append(cells)
        live.append(len(cells))
        gun, comps = split(cells)
        gun_states.append(frozenset(gun))
        glider_cells.append(frozenset().union(*comps) if comps else frozenset())
        assert len(comps) >= gliders[-1], f"a glider vanished at generation {g}"
        gliders.append(len(comps))
        if len(comps) > gliders[-2]:
            launches.append(g)
        if comps:
            far = max(comps, key=lambda c: sum(x + y for x, y in c))
            lead[g] = (sum(x for x, _ in far) / 5.0, sum(y for _, y in far) / 5.0)
    live_arr = np.array(live)
    gl = np.array(gliders)
    print(f"first glider separates from the gun at generation {launches[0]}")
    gaps = np.diff(launches)
    print(f"glider launches: {len(launches)} by generation {n_gen}; spacing between launches "
          f"min {gaps.min()} max {gaps.max()} generations")
    # Gun periodicity: the cells inside the gun box repeat every 30 generations.
    per = man["period"]
    ok = all(gun_states[i] == gun_states[i + per] for i in range(0, len(gun_states) - per))
    print(f"gun cells repeat every {per} generations from generation 0 to {n_gen}: {ok}")
    shorter = [q for q in range(1, per) if all(gun_states[i] == gun_states[i + q] for i in range(0, len(gun_states) - q))]
    print(f"shorter periods that also work: {shorter if shorter else 'none'}")
    gx = [x for st in gun_states for x, _ in st]
    gy = [y for st in gun_states for _, y in st]
    print(f"gun cells stay inside x {min(gx)}..{max(gx)}, y {min(gy)}..{max(gy)} over the whole run")
    inc = [live[g + per] - live[g] for g in range(0, n_gen - per + 1)]
    print(f"live cells {per} generations later minus live cells now: min {min(inc)} max {max(inc)} "
          f"over generations 0 to {n_gen - per}")
    gun_counts = sorted({len(s) for s in gun_states})
    print(f"gun cells (everything that is not a separated glider) over the run: min {min(gun_counts)} max {max(gun_counts)}")
    print(f"gun cells at every multiple of {per}: {sorted({len(gun_states[g]) for g in range(0, n_gen + 1, per)})}")
    for g in man["report_generations"]:
        print(f"generation {g}: {live[g]} live cells, {gliders[g]} gliders launched, "
              f"{live[g] - 5 * gliders[g]} cells in the gun")
    # Glider speed from the leading glider's centroid.
    gs = sorted(lead)
    g0, g1 = gs[0], gs[-1]
    (x0, y0), (x1, y1) = lead[g0], lead[g1]
    print(f"leading glider centroid moved ({x1 - x0:.2f}, {y1 - y0:.2f}) cells over {g1 - g0} generations: "
          f"{(x1 - x0) / (g1 - g0):.4f} cells per generation in x and {(y1 - y0) / (g1 - g0):.4f} in y "
          f"(one diagonal cell every {(g1 - g0) / (x1 - x0):.2f} generations)")
    bx = [c[0] for c in history[0]]
    by = [c[1] for c in history[0]]
    print(f"gun bounding box at generation 0: x {min(bx)}..{max(bx)}, y {min(by)}..{max(by)} "
          f"({max(bx) - min(bx) + 1} by {max(by) - min(by) + 1} cells)")
    return {"history": history, "live": live_arr, "gliders": gl, "launches": launches,
            "glider_cells": glider_cells}


def generation_at(man: dict, t: float) -> float:
    """Integrate the generations-per-second keyframes up to time t."""
    keys = man["rate_keys"]
    gen = 0.0
    for (t0, r0), (t1, r1) in zip(keys, keys[1:]):
        if t <= t0:
            break
        te = min(t, t1)
        re = r0 + (r1 - r0) * (te - t0) / (t1 - t0)
        gen += 0.5 * (r0 + re) * (te - t0)
    if t > keys[-1][0]:
        gen += keys[-1][1] * (t - keys[-1][0])
    return gen


class Renderer:
    def __init__(self, man: dict, meas: dict):
        self.man, self.meas = man, meas
        self.fps = man["fps"]
        self.cell = man["cell_px"]
        self.cols = W // self.cell
        self.rows = man["window_rows"]
        font = os.environ["SEED_ZERO_FONT"]
        self.font = ImageFont.truetype(font, 40)
        self.font_small = ImageFont.truetype(font, 32)
        self.font_tiny = ImageFont.truetype(font, 26)
        self.base = np.zeros((H, W, 3), dtype=np.uint8)
        self.base[:] = BG
        y1 = GRID_Y0 + self.rows * self.cell
        self.base[GRID_Y0:y1, :] = GRID
        for x in range(0, W, self.cell):
            self.base[GRID_Y0:y1, x] = BG
        for y in range(GRID_Y0, y1, self.cell):
            self.base[y, :] = BG
        self.grid_y1 = y1
        self.payoff_t = None

    def frame_at(self, f: int) -> np.ndarray:
        man, meas = self.man, self.meas
        t = f / self.fps
        g = min(int(generation_at(man, t)), man["generations"])
        cells = meas["history"][g]
        glider_cells = meas["glider_cells"][g]
        frame = self.base.copy()
        block = np.zeros((self.rows, self.cols, 3), dtype=np.uint8)
        mask = np.zeros((self.rows, self.cols), dtype=bool)
        for (x, y) in cells:
            if 0 <= x < self.cols and 0 <= y < self.rows:
                block[y, x] = GLIDER if (x, y) in glider_cells else GUN
                mask[y, x] = True
        big = np.repeat(np.repeat(block, self.cell, 0), self.cell, 1)
        bigmask = np.repeat(np.repeat(mask, self.cell, 0), self.cell, 1)
        # Leave a one-pixel gutter so cells read as tiles.
        bigmask[:, ::self.cell] = False
        bigmask[::self.cell, :] = False
        region = frame[GRID_Y0:self.grid_y1, :self.cols * self.cell]
        region[bigmask] = big[bigmask]

        img = Image.fromarray(frame)
        d = ImageDraw.Draw(img)
        live = int(meas["live"][g])
        gl = int(meas["gliders"][g])
        d.text((60, 150), f"generation {g:,}", font=self.font, fill=TEXT, anchor="lm")
        d.text((1020, 150), f"alive {live:,}", font=self.font, fill=GLIDER if gl else GUN, anchor="rm")
        # Readouts under the grid, then the four rules.
        ry = self.grid_y1 + 40
        d.text((60, ry), f"gliders launched {gl}", font=self.font_small, fill=GLIDER, anchor="lm")
        d.text((1020, ry), f"gun cells {live - 5 * gl}", font=self.font_small, fill=GUN, anchor="rm")
        for k, line in enumerate(man["rules_text"]):
            d.text((W / 2, ry + 90 + 44 * k), line, font=self.font_small, fill=MUTED, anchor="mm")
        # Chart: live cells against generation.
        d.rectangle((CHART_X0, CHART_Y0, CHART_X1, CHART_Y1), outline=GRIDLINE, width=2)
        d.text((CHART_X0, CHART_Y0 - 28), "cells alive", font=self.font_small, fill=MUTED, anchor="lm")
        d.text((CHART_X1, CHART_Y1 + 26), "generation", font=self.font_small, fill=MUTED, anchor="rm")
        g_end = man["generations"]
        v_max = float(meas["live"][g_end]) * 1.05

        def cx(gg):
            return CHART_X0 + (CHART_X1 - CHART_X0) * gg / g_end

        def cy(v):
            return CHART_Y1 - (CHART_Y1 - CHART_Y0) * v / v_max

        for gg in man["chart_ticks"]:
            d.line((cx(gg), CHART_Y1, cx(gg), CHART_Y1 + 8), fill=MUTED, width=2)
            d.text((cx(gg), CHART_Y1 + 26), f"{gg:,}", font=self.font_tiny, fill=MUTED, anchor="mm")
        for v in man["chart_vticks"]:
            d.line((CHART_X0 - 8, cy(v), CHART_X0, cy(v)), fill=MUTED, width=2)
            d.text((CHART_X0 - 14, cy(v)), f"{v}", font=self.font_tiny, fill=MUTED, anchor="rm")
        pts = [(cx(k), cy(float(meas["live"][k]))) for k in range(0, g + 1, max(1, g // 400))]
        if pts[-1][0] < cx(g):
            pts.append((cx(g), cy(live)))
        if len(pts) > 1:
            d.line(pts, fill=GLIDER, width=4)
        if g >= man["payoff_generation"]:
            if self.payoff_t is None:
                self.payoff_t = t
            alpha = min(1.0, (t - self.payoff_t) / man["payoff_hold"])
            shade = tuple(int(c * alpha + BG[i] * (1 - alpha)) for i, c in enumerate(GLIDER))
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
    man = json.loads((ROOT / "projects/lifegun/manifest.json").read_text())
    meas = measure(man)
    if "--measure-only" in sys.argv:
        return
    print(f"generation at scene end: {generation_at(man, man['scene_duration']):.1f}")
    total = int(round(man["scene_duration"] * man["fps"]))
    for f in range(total):
        if int(generation_at(man, f / man["fps"])) >= man["payoff_generation"]:
            print(f"generation {man['payoff_generation']} reached at video time {f / man['fps']:.2f} s (frame {f})")
            break
    Renderer(man, meas).render(ROOT / "media/lifegun/footage.mp4")


if __name__ == "__main__":
    main()
