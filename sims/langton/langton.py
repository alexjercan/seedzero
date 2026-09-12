#!/usr/bin/env python3
"""Langton's ant: one ant, two rules, what does it build?

An ant stands on an empty grid facing up. Two rules: on an empty cell it
paints the cell, turns right and steps forward; on a painted cell it wipes
the cell, turns left and steps forward. Exact integers, no seed. For
thousands of steps the ant scribbles a shapeless blob; then it locks into a
104-step cycle that moves it two cells diagonally every cycle, the highway,
and never leaves it.

Measured and printed: the first step from which every later 104-step block
repeats the same turns and lands two cells further along the same diagonal
(checked over the whole run), the period found by scanning for the smallest
shift that repeats, the displacement per period, how many periods are
verified out to the run length, the blob's extent and painted-cell count when
the highway starts, the on-screen schedule and the text widths.

usage: langton.py [--measure-only] [--frames t1,t2,...]
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
TEAL = (92, 200, 165)
GOLD = (240, 176, 84)
CORAL = (232, 96, 88)
TEXT = (216, 222, 230)
MUTED = (138, 148, 163)
WIRE = (70, 80, 94)

VIEW_X0, VIEW_X1 = 40.0, 1040.0
VIEW_Y0, VIEW_Y1 = 400.0, 1380.0
PAYOFF_Y = 1836.0

# Headings: 0 up, 1 right, 2 down, 3 left (y grows downward on screen).
DX = (0, 1, 0, -1)
DY = (-1, 0, 1, 0)


def run_ant(n: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Run n steps from the origin facing up on an empty grid. Returns the
    position before each step (n + 1 rows), the heading before each step, and
    the turn taken at each step (+1 right, -1 left)."""
    painted: set[tuple[int, int]] = set()
    pos = np.zeros((n + 1, 2), dtype=np.int64)
    head = np.zeros(n + 1, dtype=np.int64)
    turns = np.zeros(n, dtype=np.int64)
    x, y, h = 0, 0, 0
    for s in range(n):
        cell = (x, y)
        if cell in painted:
            painted.remove(cell)
            h = (h - 1) % 4
            turns[s] = -1
        else:
            painted.add(cell)
            h = (h + 1) % 4
            turns[s] = 1
        x += DX[h]
        y += DY[h]
        pos[s + 1] = (x, y)
        head[s + 1] = h
    return pos, head, turns


def highway_start(pos: np.ndarray, head: np.ndarray, period: int) -> tuple[int, tuple[int, int]]:
    """Smallest s such that for every s' >= s (with s' + period inside the
    run) the ant at s' + period is the ant at s' shifted by the same vector."""
    n = len(pos) - 1
    d = tuple(int(v) for v in pos[n] - pos[n - period])
    ok = np.all(pos[period:] - pos[:-period] == np.array(d), axis=1) & (head[period:] == head[:-period])
    # ok[s] is for step s; find the last failure.
    bad = np.flatnonzero(~ok)
    start = int(bad[-1]) + 1 if len(bad) else 0
    return start, d


def find_period(pos: np.ndarray, head: np.ndarray, tail_from: int, max_p: int = 2000) -> int:
    for p in range(1, max_p + 1):
        seg = pos[tail_from + p:] - pos[tail_from:-p]
        if np.all(seg == seg[0]) and np.all(head[tail_from + p:] == head[tail_from:-p]):
            return p
    raise RuntimeError("no period found")


def steps_at(man: dict, t: float) -> int:
    """Cumulative step count at video time t from the speed profile
    [(t, steps per second), ...] with linear interpolation."""
    prof = man["speed_profile"]
    total = 0.0
    for (t0, v0), (t1, v1) in zip(prof[:-1], prof[1:]):
        if t <= t0:
            break
        te = min(t, t1)
        ve = v0 + (v1 - v0) * (te - t0) / (t1 - t0)
        total += 0.5 * (v0 + ve) * (te - t0)
    return int(total)


def measure(man: dict) -> dict:
    n = man["run_steps"]
    pos, head, turns = run_ant(n)
    period = find_period(pos, head, n // 2)
    start, d = highway_start(pos, head, period)
    verified = (n - start) // period
    first_turns = turns[start:start + period]
    turn_ok = all(np.array_equal(turns[start + k * period:start + (k + 1) * period], first_turns) for k in range(verified))
    blob = pos[: start + 1]
    x0, x1 = int(blob[:, 0].min()), int(blob[:, 0].max())
    y0, y1 = int(blob[:, 1].min()), int(blob[:, 1].max())
    # Painted cells at the highway start.
    painted: set[tuple[int, int]] = set()
    for s in range(start):
        c = (int(pos[s, 0]), int(pos[s, 1]))
        if c in painted:
            painted.remove(c)
        else:
            painted.add(c)
    print(f"Langton's ant from an empty grid facing up: paint and turn right on an empty cell, wipe and turn left on a "
          f"painted cell; exact integers, no seed; run {n:,} steps")
    print(f"period of the settled motion, smallest repeating shift scanned from step {n // 2:,}: {period} steps, moving "
          f"({d[0]:+d}, {d[1]:+d}) cells per period ({'right' if d[0] > 0 else 'left'} and {'down' if d[1] > 0 else 'up'} on screen)")
    print(f"highway starts at step {start:,}: from that step every {period}-step block repeats the same {period} turns "
          f"({int((first_turns > 0).sum())} right, {int((first_turns < 0).sum())} left) and lands 2 cells further along the "
          f"diagonal; verified for {verified:,} periods out to step {start + verified * period:,}; turn sequence identical in every "
          f"period: {turn_ok}")
    print(f"before the highway the ant painted {len(painted):,} cells and wandered over a box {x1 - x0 + 1} by {y1 - y0 + 1} "
          f"cells (x {x0} to {x1}, y {y0} to {y1}); ant at ({pos[start, 0]}, {pos[start, 1]}) facing "
          f"{['up', 'right', 'down', 'left'][head[start]]} at step {start:,}")
    total_video_steps = steps_at(man, man["scene_duration"])
    t_hw = next(t / 100 for t in range(int(man["scene_duration"] * 100) + 1) if steps_at(man, t / 100) >= start)
    print(f"on screen: {total_video_steps:,} steps in {man['scene_duration']:g} s; the highway starts at {t_hw:.2f} s of video "
          f"and runs {(total_video_steps - start) // period} periods ({2 * ((total_video_steps - start) // period)} cells) by the end; "
          f"speed profile {man['speed_profile']}")
    seen = pos[: total_video_steps + 1]
    bx0, bx1 = int(seen[:, 0].min()), int(seen[:, 0].max())
    by0, by1 = int(seen[:, 1].min()), int(seen[:, 1].max())
    print(f"cells visited during the video span x {bx0} to {bx1}, y {by0} to {by1} ({bx1 - bx0 + 1} by {by1 - by0 + 1})")
    return {"pos": pos, "head": head, "period": period, "start": start, "d": d, "verified": verified,
            "video_steps": total_video_steps, "t_hw": t_hw, "bbox": (bx0, bx1, by0, by1), "painted_at_start": len(painted)}


class Renderer:
    def __init__(self, man: dict, meas: dict):
        self.man, self.meas = man, meas
        self.fps = man["fps"]
        font = os.environ["SEED_ZERO_FONT"]
        self.font = ImageFont.truetype(font, 40)
        self.font_small = ImageFont.truetype(font, 30)
        self.font_big = ImageFont.truetype(font, 56)
        self.font_title = ImageFont.truetype(font, 56)
        self.font_rule = ImageFont.truetype(font, 34)
        self.first = None
        # The view is turned a quarter turn anticlockwise so the highway runs
        # right and down on screen. A rotation keeps right turns right turns.
        pos = meas["pos"]
        self.pos = np.stack([pos[:, 1], -pos[:, 0]], axis=1)
        self.head = (meas["head"] - 1) % 4
        sx0, sx1, sy0, sy1 = meas["bbox"]
        bx0, bx1, by0, by1 = sy0, sy1, -sx1, -sx0
        margin = man["view_margin_cells"]
        self.gx0, self.gy0 = bx0 - margin, by0 - margin
        self.gw, self.gh = bx1 - bx0 + 1 + 2 * margin, by1 - by0 + 1 + 2 * margin
        self.cell = int(min((VIEW_X1 - VIEW_X0) // self.gw, (VIEW_Y1 - VIEW_Y0) // self.gh))
        self.ox = int((VIEW_X0 + VIEW_X1) / 2 - self.gw * self.cell / 2)
        self.oy = int((VIEW_Y0 + VIEW_Y1) / 2 - self.gh * self.cell / 2)
        self.grid = np.zeros((self.gh, self.gw), dtype=bool)
        self.grid_steps = 0
        print(f"view: {self.gw} by {self.gh} cells at {self.cell} px per cell, origin ({self.ox}, {self.oy})")
        widths = {"overlay@34": (ImageFont.truetype(font, 34), man["overlay"])}
        for j, line in enumerate(man["title"].split("|")):
            widths[f"title line {j + 1}@56"] = (self.font_title, line)
        for j, line in enumerate(man["rules"].split("|")):
            widths[f"rule {j + 1}@34"] = (self.font_rule, line)
        widths["counter@56"] = (self.font_big, f"step {meas['video_steps']:,}")
        widths["highway@34"] = (self.font_rule, self.highway_text())
        for j, line in enumerate(self.payoff_lines()):
            widths[f"payoff line {j + 1}@40"] = (self.font, line)
        print("text widths: " + ", ".join(f"{k} {f.getlength(s):.0f} px" for k, (f, s) in widths.items()))

    def highway_text(self) -> str:
        return self.man["highway_text"].format(start=self.meas["start"], period=self.meas["period"])

    def payoff_lines(self) -> list[str]:
        text = self.man["payoff_text"].format(start=self.meas["start"], period=self.meas["period"])
        return [s.strip() for s in text.split("|")]

    @staticmethod
    def blend(col: tuple, alpha: float) -> tuple:
        return tuple(int(c * alpha + BG[j] * (1 - alpha)) for j, c in enumerate(col))

    def grid_at(self, n: int) -> np.ndarray:
        if n < self.grid_steps:
            self.grid[:] = False
            self.grid_steps = 0
        pos = self.pos
        for s in range(self.grid_steps, n):
            x, y = int(pos[s, 0]) - self.gx0, int(pos[s, 1]) - self.gy0
            self.grid[y, x] = not self.grid[y, x]
        self.grid_steps = n
        return self.grid

    def live_frame(self, f: int) -> Image.Image:
        man, m = self.man, self.meas
        t = f / self.fps
        n = min(steps_at(man, t), len(m["pos"]) - 1)
        img = Image.new("RGB", (W, H), BG)
        grid = self.grid_at(n)
        tile = np.zeros((self.gh, self.gw, 3), dtype=np.uint8)
        tile[:] = BG
        tile[grid] = TEAL
        # Highway cells painted after the start get gold so the road stands out.
        cells = Image.fromarray(tile, "RGB").resize((self.gw * self.cell, self.gh * self.cell), Image.NEAREST)
        img.paste(cells, (self.ox, self.oy))
        d = ImageDraw.Draw(img)
        d.rectangle((self.ox - 2, self.oy - 2, self.ox + self.gw * self.cell + 1, self.oy + self.gh * self.cell + 1), outline=WIRE, width=2)
        # The ant.
        ax, ay = int(self.pos[n, 0]) - self.gx0, int(self.pos[n, 1]) - self.gy0
        cx, cy = self.ox + (ax + 0.5) * self.cell, self.oy + (ay + 0.5) * self.cell
        r = max(7, self.cell)
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=GOLD, outline=BG, width=2)
        h = int(self.head[n])
        d.line((cx, cy, cx + DX[h] * r * 2.2, cy + DY[h] * r * 2.2), fill=GOLD, width=4)
        # Title, rules, counter.
        title_on = t < man["title_until"]
        if title_on:
            alpha = 1.0 if t < man["title_until"] - 0.4 else (man["title_until"] - t) / 0.4
            for j, line in enumerate(man["title"].split("|")):
                d.text((W / 2, 176 + j * 62), line, font=self.font_title, fill=self.blend(TEXT, alpha), anchor="mm")
        else:
            for j, line in enumerate(man["rules"].split("|")):
                d.text((VIEW_X0 + 20, 170 + j * 44), line, font=self.font_rule, fill=MUTED, anchor="lm")
        d.text((VIEW_X1 - 20, 340), f"step {n:,}", font=self.font_big, fill=TEXT, anchor="rm")
        if n >= m["start"] and not title_on:
            alpha = min(1.0, (t - m["t_hw"]) / 0.4)
            d.text((VIEW_X0 + 20, 258), self.highway_text(), font=self.font_rule, fill=self.blend(GOLD, alpha), anchor="lm")
        if t >= man["payoff_t"]:
            alpha = min(1.0, (t - man["payoff_t"]) / man["payoff_hold"])
            for j, line in enumerate(self.payoff_lines()):
                d.text((W / 2, PAYOFF_Y - 32 + j * 64), line, font=self.font, fill=self.blend(GOLD, alpha), anchor="mm")
        return img

    def frame_at(self, f: int) -> np.ndarray:
        man = self.man
        total = int(round(man["scene_duration"] * self.fps))
        live = np.asarray(self.live_frame(f), dtype=np.float32)
        fade_frames = int(round(man["loop_fade"] * self.fps))
        if f >= total - fade_frames:
            if self.first is None:
                self.first = np.asarray(self.live_frame(0), dtype=np.float32)
            a = (f - (total - fade_frames) + 1) / fade_frames
            live = live * (1 - a) + self.first * a
        return live.astype(np.uint8)

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
    man = json.loads((ROOT / "projects/langton/manifest.json").read_text())
    meas = measure(man)
    if "--measure-only" in sys.argv:
        return
    if "--frames" in sys.argv:
        times = [float(v) for v in sys.argv[sys.argv.index("--frames") + 1].split(",")]
        r = Renderer(man, meas)
        (ROOT / "media/langton").mkdir(parents=True, exist_ok=True)
        for tv in times:
            Image.fromarray(r.frame_at(int(round(tv * man["fps"])))).save(ROOT / f"media/langton/smoke-{tv}.png")
        print("smoke frames: " + ", ".join(f"{tv}" for tv in times))
        return
    Renderer(man, meas).render(ROOT / "media/langton/footage.mp4")


if __name__ == "__main__":
    main()
