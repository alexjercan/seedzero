#!/usr/bin/env python3
"""Benford's law: doubling versus counting.

Two panels take the same number of steps. The top panel counts up, one
at a time: 1, 2, 3, ... The bottom panel doubles: 1, 2, 4, 8, ... At every
step the leading digit of the current number drops into one of nine bins.
Counting spreads the leading digits almost evenly. Doubling piles them on
1: the leading digit of 2^k is 1 whenever the fractional part of k times
log10(2) falls below log10(2), which happens 30.1% of the time.

Everything is exact integer arithmetic; there is no seed. Measured and
printed: the leading-digit counts of both sequences after the claim step
count and after the long run, the counts for 1 and 9, their ratio, and
Benford's exact proportions log10(1 + 1/d).

usage: benford.py [--measure-only]
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
WHITE = (255, 255, 255)

# Layout: two panels, captions between them at caption_y 0.49 (y 941..1021).
PANEL = {"count": {"y0": 130, "col": TEAL, "label": "count up: add 1 each step"},
         "double": {"y0": 1050, "col": GOLD, "label": "double: times 2 each step"}}
BIN_X0, BIN_X1 = 60, 1020
NUM_DY = 118
TOP_DY, FLOOR_DY = 170, 620
LABEL_DY = 650
READ_DY = 706
PAYOFF_Y = 1868.0
SHOW_DIGITS = 14


def sequences(steps: int) -> dict:
    """Leading digits and display strings of 1..steps and 2^0..2^(steps-1)."""
    count_lead = np.empty(steps, dtype=np.int8)
    double_lead = np.empty(steps, dtype=np.int8)
    count_txt = []
    double_txt = []
    double_len = np.empty(steps, dtype=np.int32)
    v = 1
    for k in range(steps):
        s = str(k + 1)
        count_lead[k] = int(s[0])
        count_txt.append(f"{k + 1:,}")
        d = str(v)
        double_lead[k] = int(d[0])
        double_len[k] = len(d)
        double_txt.append(d[:SHOW_DIGITS])
        v *= 2
    return {"count_lead": count_lead, "double_lead": double_lead, "count_txt": count_txt,
            "double_txt": double_txt, "double_len": double_len}


def measure(man: dict) -> dict:
    steps, claim = man["steps"], man["claim_steps"]
    seq = sequences(steps)
    print(f"count up 1..{steps:,} against double 2^0..2^{steps - 1:,}; claim read at {claim:,} steps; exact integers, no seed")
    out = {"seq": seq}
    for name in ("count", "double"):
        lead = seq[f"{name}_lead"]
        for label, k in (("claim", claim), ("long", steps)):
            counts = np.bincount(lead[:k], minlength=10)
            out[f"{name}_{label}"] = counts
            row = ", ".join(f"{d}: {int(counts[d]):,}" for d in range(1, 10))
            print(f"{name} after {k:,} steps: {row}")
            print(f"  leading 1: {int(counts[1]):,} = {100 * counts[1] / k:.1f}%, leading 9: {int(counts[9]):,} = {100 * counts[9] / k:.2f}%, "
                  f"ratio {counts[1] / counts[9]:.2f} to 1")
    print("benford exact: " + ", ".join(f"{d}: {100 * math.log10(1 + 1 / d):.1f}%" for d in range(1, 10)))
    print(f"benford exact at {claim:,}: 1 leads {claim * math.log10(2):.1f} times, 9 leads {claim * math.log10(10 / 9):.1f}; "
          f"ratio {math.log10(2) / math.log10(10 / 9):.2f} to 1")
    print(f"2^{claim - 1:,} has {int(seq['double_len'][claim - 1]):,} digits; 2^{steps - 1:,} has {int(seq['double_len'][steps - 1]):,} digits")
    for k in (10, 20, 50, 100, 200, 500, 1000, 2000, 5000, 10000):
        if k > steps:
            break
        cd = np.bincount(seq["double_lead"][:k], minlength=10)
        cc = np.bincount(seq["count_lead"][:k], minlength=10)
        print(f"  after {k:>6,} steps: doubling 1 leads {int(cd[1]):>5,}, 9 leads {int(cd[9]):>4,}; counting {int(cc[1]):>5,} and {int(cc[9]):>5,}")
    return out


def landing_times(keys: list, n: int) -> np.ndarray:
    t = np.empty(n)
    for (t0, n0), (t1, n1) in zip(keys, keys[1:]):
        n0, n1 = int(n0), int(n1)
        if n1 <= n0:
            continue
        c = np.arange(n0 + 1, min(n1, n) + 1, dtype=float)
        t[n0 : n0 + len(c)] = t0 + (t1 - t0) * (np.log(c + 1.0) - np.log(n0 + 1.0)) / (np.log(n1 + 1.0) - np.log(n0 + 1.0))
    return t


class Renderer:
    def __init__(self, man: dict, meas: dict):
        self.man, self.meas = man, meas
        self.fps = man["fps"]
        font = os.environ["SEED_ZERO_FONT"]
        self.font = ImageFont.truetype(font, 40)
        self.font_small = ImageFont.truetype(font, 32)
        self.font_tiny = ImageFont.truetype(font, 26)
        self.font_big = ImageFont.truetype(font, 56)
        self.font_num = ImageFont.truetype(font, 52)
        self.font_ball = ImageFont.truetype(font, 22)
        self.steps = man["steps"]
        self.t_land = landing_times(man["step_keys"], self.steps)
        self.t_replay = landing_times(man["replay_keys"], man["claim_steps"])
        self.fall = float(man["fall_s"])
        self.pitch = (BIN_X1 - BIN_X0) / 9

    def bin_x(self, d: int) -> float:
        return BIN_X0 + (d - 0.5) * self.pitch

    def frame_at(self, f: int) -> np.ndarray:
        man, m = self.man, self.meas
        seq = m["seq"]
        t = f / self.fps
        replay = t >= man["replay_t"]
        t_land = self.t_replay if replay else self.t_land
        n = int(np.searchsorted(t_land, t, side="right"))
        hi = int(np.searchsorted(t_land, t + self.fall, side="right"))
        pil = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(pil)
        loads = {name: np.bincount(seq[f"{name}_lead"][:n], minlength=10) for name in PANEL}
        scale = max(float(man["scale_steps"]), 1.12 * float(max(loads["count"].max(), loads["double"].max())))
        ppb = (FLOOR_DY - TOP_DY) / scale
        bw = self.pitch - 14
        stride = max(1, (hi - n) // man["max_falling"])
        for name, p in PANEL.items():
            y0, col = p["y0"], p["col"]
            floor = y0 + FLOOR_DY
            ld = loads[name]
            d.text((60, y0 + 20), p["label"], font=self.font, fill=col, anchor="lm")
            d.text((W - 60, y0 + 20), f"step {n:,}" + ("  (replay)" if replay else ""), font=self.font_tiny, fill=MUTED, anchor="rm")
            # The current number, leading digit in the panel colour.
            if n:
                k = n - 1
                if name == "count":
                    txt, tail = seq["count_txt"][k], ""
                else:
                    txt = seq["double_txt"][k]
                    ln = int(seq["double_len"][k])
                    tail = f"...  ({ln:,} digits)" if ln > SHOW_DIGITS else ""
                x = 60
                d.text((x, y0 + NUM_DY), txt[0], font=self.font_num, fill=col, anchor="lm")
                x += d.textlength(txt[0], font=self.font_num)
                d.text((x, y0 + NUM_DY), txt[1:], font=self.font_num, fill=TEXT, anchor="lm")
                x += d.textlength(txt[1:], font=self.font_num)
                if tail:
                    d.text((x + 8, y0 + NUM_DY + 8), tail, font=self.font_tiny, fill=MUTED, anchor="lm")
            d.line((BIN_X0, floor, BIN_X1, floor), fill=TEXT, width=2)
            # A bar pulses white when the narration names its count, then keeps its label.
            pulse = {}
            if not replay and t < man["pulse_until"]:
                for pt, pname, pdg in man["pulses"]:
                    if pname == name and t >= pt:
                        pulse[pdg] = min(1.0, (t - pt) / 0.8)
            for dg in range(1, 10):
                x = self.bin_x(dg)
                hgt = ld[dg] * ppb
                bar_col = col
                if dg in pulse:
                    a = pulse[dg]
                    bar_col = tuple(int(WHITE[i] * (1 - a) + col[i] * a) for i in range(3))
                if hgt >= 1:
                    d.rectangle((x - bw / 2, floor - hgt, x + bw / 2, floor - 1), fill=bar_col)
                if dg in pulse:
                    d.text((x, floor - hgt - 22), f"{int(ld[dg]):,}", font=self.font_small, fill=WHITE, anchor="mm")
                d.text((x, y0 + LABEL_DY), str(dg), font=self.font_small, fill=TEXT if dg in (1, 9) else MUTED, anchor="mm")
            lead = seq[f"{name}_lead"]
            for i in range(n, hi, stride):
                u = 1.0 - (t_land[i] - t) / self.fall
                dg = int(lead[i])
                x = self.bin_x(dg)
                y_end = floor - (ld[dg] + 1) * ppb
                y_start = y0 + NUM_DY + 40
                y = y_start + (y_end - y_start) * u * u
                d.ellipse((x - 14, y - 14, x + 14, y + 14), fill=WHITE)
                d.text((x, y + 1), str(dg), font=self.font_ball, fill=BG, anchor="mm")
            if n:
                d.text((60, y0 + READ_DY), f"starts with 1: {int(ld[1]):,}", font=self.font_small, fill=col, anchor="lm")
                d.text((W - 60, y0 + READ_DY), f"starts with 9: {int(ld[9]):,}", font=self.font_small, fill=TEXT, anchor="rm")
        if t >= man["payoff_t"]:
            if t >= man["long_payoff_t"]:
                alpha = min(1.0, (t - man["long_payoff_t"]) / man["payoff_hold"])
                cc, cd = m["count_long"], m["double_long"]
                text = man["long_payoff_text"].format(c1=int(cc[1]), c9=int(cc[9]), d1=int(cd[1]), d9=int(cd[9]))
            else:
                alpha = min(1.0, (t - man["payoff_t"]) / man["payoff_hold"])
                cc, cd = m["count_claim"], m["double_claim"]
                text = man["payoff_text"].format(c1=int(cc[1]), c9=int(cc[9]), d1=int(cd[1]), d9=int(cd[9]))
            shade = tuple(int(c * alpha + BG[i] * (1 - alpha)) for i, c in enumerate(GOLD))
            d.text((W / 2, PAYOFF_Y), text, font=self.font, fill=shade, anchor="mm")
        return np.asarray(pil)

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
    man = json.loads((ROOT / "projects/benford/manifest.json").read_text())
    meas = measure(man)
    if "--measure-only" in sys.argv:
        return
    Renderer(man, meas).render(ROOT / "media/benford/footage.mp4")


if __name__ == "__main__":
    main()
