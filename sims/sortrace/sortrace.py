#!/usr/bin/env python3
"""Sorting race: quicksort vs bubble sort, honest comparison counters.

One seeded shuffle of 512 distinct values. Both algorithms sort the same
array; every comparison is counted and every swap is logged with the
comparison count at which it happened. The race replays both event logs
at the same fixed comparisons-per-second rate, chosen so bubble sort
finishes exactly at race_duration. Quicksort finishes when its counter
runs out, then waits. The measured counts, the rate, and both finish
times are printed.

usage: sortrace.py [--measure-only]
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
BARS = (216, 222, 230)
DONE = (92, 200, 165)
MUTED = (138, 148, 163)
GRID = (70, 80, 94)

# Layout. The caption band burned in by compose.sh sits at y = 1344..1420;
# nothing draws text there.
PANEL_X0, PANEL_X1 = 60, 1020
PANELS = {"quick": (330, 760), "bubble": (900, 1330)}
LABEL_YS = {"quick": 285, "bubble": 855}
CLOCK_Y = 210.0
PAYOFF_Y = 1868.0
COUNTER_Y = 1560.0

# Timeline (seconds).
INTRO_HOLD = 2.0
RESET_GAP = 0.5
LABEL_FADE = 0.6


def instrumented_bubble(a: np.ndarray):
    a = a.copy()
    comps = 0
    events = []  # (comps_at_event, i, j)
    n = len(a)
    for p in range(n - 1):
        swapped = False
        for i in range(n - 1 - p):
            comps += 1
            if a[i] > a[i + 1]:
                a[[i, i + 1]] = a[[i + 1, i]]
                events.append((comps, i, i + 1))
                swapped = True
        if not swapped:
            break
    assert np.all(np.diff(a) > 0)
    return comps, events


def instrumented_quick(a: np.ndarray):
    a = a.copy()
    comps = 0
    events = []
    stack = [(0, len(a) - 1)]
    while stack:
        lo, hi = stack.pop()
        if lo >= hi:
            continue
        mid = (lo + hi) // 2
        a[[mid, hi]] = a[[hi, mid]]
        events.append((comps, mid, hi))
        pivot = a[hi]
        store = lo
        for i in range(lo, hi):
            comps += 1
            if a[i] < pivot:
                if i != store:
                    a[[i, store]] = a[[store, i]]
                    events.append((comps, i, store))
                store += 1
        a[[store, hi]] = a[[hi, store]]
        events.append((comps, store, hi))
        stack.append((lo, store - 1))
        stack.append((store + 1, hi))
    assert np.all(np.diff(a) > 0)
    return comps, events


def measure_report(manifest: dict) -> dict:
    rng = np.random.RandomState(manifest["seed"])
    values = np.arange(1, manifest["bars"] + 1)
    rng.shuffle(values)
    q_comps, q_events = instrumented_quick(values)
    b_comps, b_events = instrumented_bubble(values)
    rate = b_comps / manifest["race_duration"]
    m = {
        "values": values,
        "q_comps": q_comps, "q_events": q_events,
        "b_comps": b_comps, "b_events": b_events,
        "rate": rate,
        "q_finish": q_comps / rate,
        "ratio": b_comps / q_comps,
        "q_swaps": len(q_events),
        "b_swaps": len(b_events),
    }
    print(f"bars: {manifest['bars']}  seed: {manifest['seed']}")
    print(f"quicksort:  {q_comps} comparisons, {len(q_events)} swaps")
    print(f"bubble:     {b_comps} comparisons, {len(b_events)} swaps")
    print(f"ratio: {m['ratio']:.1f} to 1")
    print(f"race rate: {rate:.0f} comparisons/s "
          f"(bubble finishes at {manifest['race_duration']}s)")
    print(f"quicksort finishes at {m['q_finish']:.2f}s")
    return m


class Replay:
    """Bar heights over time for one algorithm's event log."""

    def __init__(self, values: np.ndarray, events, comps: int, rate: float):
        self.state = values.copy()
        self.events = events
        self.comps = comps
        self.rate = rate
        self.cursor = 0

    def at(self, s: float) -> tuple[np.ndarray, int, bool]:
        ops = int(s * self.rate)
        while self.cursor < len(self.events) and self.events[self.cursor][0] <= ops:
            _, i, j = self.events[self.cursor]
            self.state[[i, j]] = self.state[[j, i]]
            self.cursor += 1
        done = ops >= self.comps
        return self.state, min(ops, self.comps), done


class Renderer:
    def __init__(self, manifest, meas):
        self.man = manifest
        self.fps = manifest["fps"]
        self.scene_dur = manifest["scene_duration"]
        self.race_dur = manifest["race_duration"]
        self.meas = meas
        self.n = manifest["bars"]
        self.font = ImageFont.truetype(os.environ["SEED_ZERO_FONT"], 42)
        self.font_small = ImageFont.truetype(os.environ["SEED_ZERO_FONT"], 36)
        self.font_big = ImageFont.truetype(os.environ["SEED_ZERO_FONT"], 58)
        self.replays = {
            "quick": Replay(meas["values"], meas["q_events"], meas["q_comps"], meas["rate"]),
            "bubble": Replay(meas["values"], meas["b_events"], meas["b_comps"], meas["rate"]),
        }
        # Column pixel ranges for each bar.
        edges = np.linspace(PANEL_X0, PANEL_X1, self.n + 1).astype(int)
        self.col0, self.col1 = edges[:-1], edges[1:]

    def draw_bars(self, frame: np.ndarray, key: str, state: np.ndarray, done: bool):
        y0, y1 = PANELS[key]
        height = y1 - y0
        col = DONE if done else BARS
        tops = (y1 - state / self.n * height).astype(int)
        for b in range(self.n):
            frame[tops[b]:y1, self.col0[b]:self.col1[b]] = col

    def frame_at(self, s: float) -> np.ndarray:
        frame = np.zeros((H, W, 3), dtype=np.uint8)
        frame[:, :] = BG
        states = {}
        for key, rep in self.replays.items():
            state, ops, done = rep.at(min(s, self.race_dur))
            states[key] = (ops, done)
            self.draw_bars(frame, key, state, done)
        img = Image.fromarray(frame)
        d = ImageDraw.Draw(img)
        d.text((W / 2, CLOCK_Y), f"{min(s, self.race_dur):5.2f} s",
               font=self.font_big, fill=DONE, anchor="mm")
        for key, label in (("quick", "quicksort"), ("bubble", "bubble sort")):
            ops, done = states[key]
            d.text((PANEL_X0, LABEL_YS[key]), label, font=self.font,
                   fill=MUTED, anchor="lm")
            suffix = "  done" if done else ""
            d.text((PANEL_X1, LABEL_YS[key]), f"{ops:,} comparisons{suffix}",
                   font=self.font, fill=DONE if done else BARS, anchor="rm")
        if states["quick"][1] and not states["bubble"][1]:
            d.text((W / 2, COUNTER_Y),
                   f"quicksort finished at {self.meas['q_finish']:.1f} s",
                   font=self.font, fill=DONE, anchor="mm")
        alpha = min(1.0, max(0.0, (s - self.man["payoff_fade"]) / LABEL_FADE))
        if alpha > 0:
            shade = tuple(int(v * alpha + BG[i] * (1 - alpha))
                          for i, v in enumerate(BARS))
            d.text((W / 2, PAYOFF_Y),
                   f"same array: {self.meas['q_comps']:,} vs "
                   f"{self.meas['b_comps']:,} comparisons",
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
        intro = self.frame_at(self.scene_dur)
        for key in self.replays:
            self.replays[key] = Replay(self.meas["values"],
                                       self.meas[f"{key[0]}_events"],
                                       self.meas[f"{key[0]}_comps"],
                                       self.meas["rate"])
        for f in range(total):
            t = f / self.fps
            if t < INTRO_HOLD:
                frame = intro
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
    manifest = json.loads((ROOT / "projects/sortrace/manifest.json").read_text())
    meas = measure_report(manifest)
    if "--measure-only" in sys.argv:
        return
    Renderer(manifest, meas).render(ROOT / "media/sortrace/footage.mp4")


if __name__ == "__main__":
    main()
