#!/usr/bin/env python3
"""The five-state busy beaver champion (Marxen and Buntrock 1990) run from
a blank tape to its halt, counting every step exactly.

Machine: 1RB1LC_1RC1RB_1RD0LE_1LA1LD_1RZ0LA. Each entry is what the machine
does in a state when it reads 0 or 1: write, move (L/R), next state (Z is
halt). The halting transition counts as a step, the standard convention.

The sim records the step count, the ones on the tape, and the tape span at
halt, plus snapshots of the tape at the steps the video shows, so the
render draws real tape contents at every frame.

usage: busybeaver.py [--measure-only]
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
ONE = (240, 176, 84)
ZERO = (25, 31, 40)
HEAD = (92, 200, 165)
TEXT = (216, 222, 230)
MUTED = (138, 148, 163)
GRIDLINE = (40, 48, 58)
HALT = (236, 96, 96)

MACHINE = "1RB1LC_1RC1RB_1RD0LE_1LA1LD_1RZ0LA"
STATES = "ABCDE"

TABLE_Y = 230
STRIP_Y = 400
STRIP_CELL = 40
STRIP_CELLS = 27
DIAG_X0, DIAG_X1 = 40, 1040
DIAG_Y0, DIAG_Y1 = 520, 1290
COUNTER_Y = 1500
PAYOFF_Y = 1875


def parse_machine(text: str):
    write, move, nxt = [], [], []
    for chunk in text.split("_"):
        for sym in (0, 1):
            w, m, s = chunk[3 * sym:3 * sym + 3]
            write.append(int(w))
            move.append(1 if m == "R" else -1)
            nxt.append(-1 if s == "Z" else STATES.index(s))
    return write, move, nxt


def step_targets(man: dict) -> list[int]:
    """The step count shown at every frame, from the (time, step) keys with
    log interpolation between keys, so the count accelerates smoothly."""
    keys = man["step_keys"]
    total = int(round(man["scene_duration"] * man["fps"]))
    out = []
    for f in range(total):
        t = f / man["fps"]
        s = keys[-1][1]
        for (t0, s0), (t1, s1) in zip(keys, keys[1:]):
            if t0 <= t <= t1:
                if s0 <= 0:
                    s = s0 + (s1 - s0) * (t - t0) / (t1 - t0)
                else:
                    s = math.exp(math.log(s0) + (math.log(s1) - math.log(s0)) * (t - t0) / (t1 - t0))
                break
        s = int(round(s))
        out.append(min(max(s, 0), keys[-1][1]))
    return out


def run(man: dict, targets: list[int]):
    """Run the machine to the halt. Snapshot the tape at every target step."""
    write, move, nxt = parse_machine(MACHINE)
    size = man["tape_alloc"]
    tape = bytearray(size)
    pos = size // 2
    state = 0
    steps = 0
    ones = 0
    lo = hi = pos
    want = sorted(set(targets) | set(man["report_steps"]))
    wi = 0
    snaps: dict = {}
    marks = {}
    milestones = sorted(man["span_milestones"])
    mi = 0
    if want and want[0] == 0:
        snaps[0] = (bytes(tape[lo:hi + 1]), lo, hi, pos, state, ones)
        wi = 1
    while state >= 0:
        sym = tape[pos]
        k = state * 2 + sym
        w = write[k]
        tape[pos] = w
        ones += w - sym
        pos += move[k]
        state = nxt[k]
        steps += 1
        if pos < lo:
            lo = pos
        elif pos > hi:
            hi = pos
        if mi < len(milestones) and hi - lo + 1 >= milestones[mi]:
            marks[milestones[mi]] = (steps, ones)
            mi += 1
        if wi < len(want) and steps == want[wi]:
            snaps[steps] = (bytes(tape[lo:hi + 1]), lo, hi, pos, state, ones)
            wi += 1
    assert 0 < lo and hi < size - 1, "tape allocation too small"
    final = (bytes(tape[lo:hi + 1]), lo, hi, pos, state, ones)
    return {"steps": steps, "ones": ones, "lo": lo, "hi": hi, "snaps": snaps,
            "final": final, "marks": marks, "last_k": k}


def measure(man: dict, targets: list[int]) -> dict:
    res = run(man, targets)
    write, move, nxt = parse_machine(MACHINE)
    print(f"machine {MACHINE}: {len(STATES)} states, 2 symbols, blank tape, head at cell 0")
    for i, s in enumerate(STATES):
        parts = []
        for sym in (0, 1):
            k = i * 2 + sym
            parts.append(f"reads {sym}: write {write[k]}, move {'R' if move[k] > 0 else 'L'}, "
                         f"{'halt' if nxt[k] < 0 else 'go to ' + STATES[nxt[k]]}")
        print(f"  state {s}: " + "; ".join(parts))
    span = res["hi"] - res["lo"] + 1
    print(f"halted after {res['steps']:,} steps (halting transition counted)")
    print(f"ones on the tape at halt: {res['ones']:,}")
    print(f"tape cells visited: {span:,} (from {res['lo'] - man['tape_alloc'] // 2} to {res['hi'] - man['tape_alloc'] // 2} relative to the start)")
    k = res["last_k"]
    print(f"halting transition: state {STATES[k // 2]} reads {k % 2}, writes {write[k]}, moves "
          f"{'R' if move[k] > 0 else 'L'}, halts")
    for m in sorted(res["marks"]):
        s, o = res["marks"][m]
        print(f"tape first spans {m:,} cells at step {s:,} ({o:,} ones then)")
    for s in sorted(res["snaps"]):
        if s in man["report_steps"]:
            tape, lo, hi, pos, state, ones = res["snaps"][s]
            print(f"step {s:,}: tape spans {hi - lo + 1:,} cells, {ones:,} ones, head at "
                  f"{pos - man['tape_alloc'] // 2:+,}, state {STATES[state] if state >= 0 else 'halt'}")
    tape = res["final"][0]
    runs = []
    cur, n = tape[0], 0
    for b in tape:
        if b == cur:
            n += 1
        else:
            runs.append((cur, n))
            cur, n = b, 1
    runs.append((cur, n))
    print(f"final tape has {len(runs)} runs; longest run of ones {max(n for v, n in runs if v == 1):,}, "
          f"longest run of zeros inside the span {max((n for v, n in runs if v == 0), default=0):,}")
    return res


class Renderer:
    def __init__(self, man: dict, meas: dict, targets: list[int]):
        self.man, self.meas, self.targets = man, meas, targets
        self.fps = man["fps"]
        font = os.environ["SEED_ZERO_FONT"]
        self.font = ImageFont.truetype(font, 40)
        self.font_big = ImageFont.truetype(font, 76)
        self.font_small = ImageFont.truetype(font, 32)
        self.font_tiny = ImageFont.truetype(font, 26)
        self.write, self.move, self.nxt = parse_machine(MACHINE)
        self.n_rows = DIAG_Y1 - DIAG_Y0
        self.width = DIAG_X1 - DIAG_X0
        self.rows: list = [None] * self.n_rows  # (tape float array, lo, hi) per row
        self.total = len(targets)
        self.span = meas["hi"] - meas["lo"] + 1

    def diag_row(self, entry, lo_now: int, hi_now: int) -> np.ndarray:
        """Bin one tape snapshot into the diagram width at the current zoom,
        so the whole history is redrawn at the span the tape has right now."""
        arr, lo, hi = entry
        width = self.width
        span = hi_now - lo_now + 1
        cells = np.arange(lo, hi + 1) - lo_now
        bins = (cells * width // span).astype(int)
        sums = np.bincount(bins, weights=arr, minlength=width)[:width]
        cnts = np.bincount(bins, minlength=width)[:width]
        frac = np.zeros(width)
        nz = cnts > 0
        frac[nz] = (sums[nz] / cnts[nz]) ** 0.6
        row = np.empty((width, 3), dtype=np.uint8)
        for i in range(3):
            row[:, i] = (ZERO[i] + (ONE[i] - ZERO[i]) * frac).astype(np.uint8)
        return row

    def frame_at(self, f: int) -> np.ndarray:
        man, meas = self.man, self.meas
        t = f / self.fps
        s = self.targets[f]
        snap = meas["snaps"][s]
        tape, lo, hi, pos, state, ones = snap
        # Space-time diagram: one row per moment, the whole history redrawn
        # at the current tape span so the picture always fills the width.
        row_idx = min(self.n_rows - 1, int(f * self.n_rows / self.total))
        self.rows[row_idx] = (np.frombuffer(tape, dtype=np.uint8).astype(float), lo, hi)
        for r in range(row_idx):
            if self.rows[r] is None:
                self.rows[r] = self.rows[row_idx]
        diag = np.zeros((self.n_rows, self.width, 3), dtype=np.uint8)
        diag[:] = ZERO
        for r in range(row_idx + 1):
            diag[r] = self.diag_row(self.rows[r], lo, hi)

        frame = np.zeros((H, W, 3), dtype=np.uint8)
        frame[:] = BG
        frame[DIAG_Y0:DIAG_Y1, DIAG_X0:DIAG_X1] = diag
        img = Image.fromarray(frame)
        d = ImageDraw.Draw(img)
        halted = state < 0
        # State table.
        col_w = 200
        for i, name in enumerate(STATES):
            x = 40 + i * col_w + col_w / 2
            active = (not halted and state == i) or (halted and i == 4)
            d.rectangle((x - 92, TABLE_Y - 40, x + 92, TABLE_Y + 76), fill=(24, 30, 40) if active else BG,
                        outline=HEAD if active else GRIDLINE, width=3 if active else 2)
            d.text((x, TABLE_Y - 12), name, font=self.font, fill=HEAD if active else TEXT, anchor="mm")
            for sym in (0, 1):
                k = i * 2 + sym
                rule = f"{sym}: {self.write[k]}{'R' if self.move[k] > 0 else 'L'}{'halt' if self.nxt[k] < 0 else STATES[self.nxt[k]]}"
                d.text((x, TABLE_Y + 24 + sym * 30), rule, font=self.font_tiny,
                       fill=TEXT if active else MUTED, anchor="mm")
        d.text((40, TABLE_Y - 70), "5 states. reads 0 or 1: write, move, switch.", font=self.font_small, fill=MUTED, anchor="lm")
        # Tape strip around the head.
        c0 = pos - STRIP_CELLS // 2
        for i in range(STRIP_CELLS):
            c = c0 + i
            v = tape[c - lo] if lo <= c <= hi else 0
            x = i * STRIP_CELL
            d.rectangle((x + 2, STRIP_Y, x + STRIP_CELL - 2, STRIP_Y + STRIP_CELL - 4),
                        fill=ONE if v else ZERO, outline=GRIDLINE if not v else ONE)
        hx = (STRIP_CELLS // 2) * STRIP_CELL + STRIP_CELL / 2
        d.polygon([(hx, STRIP_Y - 6), (hx - 14, STRIP_Y - 30), (hx + 14, STRIP_Y - 30)], fill=HALT if halted else HEAD)
        d.text((hx, STRIP_Y - 50), "halt" if halted else STATES[state], font=self.font_small,
               fill=HALT if halted else HEAD, anchor="mm")
        d.text((40, STRIP_Y + 64), "tape around the head", font=self.font_tiny, fill=MUTED, anchor="lm")
        d.text((1040, STRIP_Y + 64), f"head at cell {pos - man['tape_alloc'] // 2:+,}", font=self.font_tiny, fill=MUTED, anchor="rm")
        # Diagram frame and labels.
        d.rectangle((DIAG_X0 - 2, DIAG_Y0 - 2, DIAG_X1 + 1, DIAG_Y1 + 1), outline=GRIDLINE, width=2)
        d.text((DIAG_X0, DIAG_Y0 - 26), "whole tape, one row per moment, time runs down", font=self.font_tiny, fill=MUTED, anchor="lm")
        d.text((DIAG_X1, DIAG_Y1 + 24), f"{self.span:,} cells wide", font=self.font_tiny, fill=MUTED, anchor="rm")
        d.text((DIAG_X0, DIAG_Y1 + 24), f"tape spans {hi - lo + 1:,} cells", font=self.font_tiny, fill=ONE, anchor="lm")
        # Counters.
        d.text((W / 2, COUNTER_Y), f"step {s:,}", font=self.font_big, fill=HALT if halted else TEXT, anchor="mm")
        d.text((60, COUNTER_Y + 80), f"ones on tape {ones:,}", font=self.font_small, fill=ONE, anchor="lm")
        d.text((1020, COUNTER_Y + 80), "HALTED" if halted else "running", font=self.font_small,
               fill=HALT if halted else HEAD, anchor="rm")
        if t >= man["payoff_t"]:
            alpha = min(1.0, (t - man["payoff_t"]) / man["payoff_hold"])
            shade = tuple(int(c * alpha + BG[i] * (1 - alpha)) for i, c in enumerate(ONE))
            d.text((W / 2, PAYOFF_Y), man["payoff_text"], font=self.font, fill=shade, anchor="mm")
        return np.asarray(img)

    def render(self, out_path: Path) -> None:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        total = self.total
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
    man = json.loads((ROOT / "projects/busybeaver/manifest.json").read_text())
    targets = step_targets(man)
    meas = measure(man, targets)
    if "--measure-only" in sys.argv:
        return
    Renderer(man, meas, targets).render(ROOT / "media/busybeaver/footage.mp4")


if __name__ == "__main__":
    main()
