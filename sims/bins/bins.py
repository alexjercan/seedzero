#!/usr/bin/env python3
"""Balls into bins: random versus two choices.

Balls fall into one hundred bins (seed 0, numpy RandomState). Every ball
draws two bin numbers from the seeded stream. In the random panel the ball
takes its first draw. In the two-choices panel the ball peeks at both bins
and takes the emptier one (ties go to the first draw). So both panels get
the same balls with the same first pick, and the only difference is one
extra look. The claim is read at ten thousand balls; the same run then
continues to one hundred thousand.

Measured and printed for each rule: the tallest and shortest stack, the
spread between them, the standard deviation of the loads, how many bins
sit far from the average, the running tallest stack as the balls land,
how often the peek changed the pick, and as checks the mean spread over
many seeds and that the long run starts with the exact same picks.

usage: bins.py [--measure-only]
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
RED = (232, 96, 88)
TEXT = (216, 222, 230)
MUTED = (138, 148, 163)
GRIDLINE = (40, 48, 58)
WHITE = (255, 255, 255)

# Layout: two panels, captions between them at caption_y 0.49 (y 941..1021).
PANEL = {"random": {"y0": 130, "col": GOLD, "label": "one pick: take that bin"},
         "two": {"y0": 1050, "col": TEAL, "label": "two picks: take the emptier bin"}}
BIN_X0, BIN_X1 = 60, 1020
TOP_DY, FLOOR_DY = 80, 640
READ_DY = 706
PAYOFF_Y = 1868.0


def run(rng: np.random.RandomState, n: int, bins: int) -> dict:
    picks = rng.randint(0, bins, size=(n, 2))
    random_bin = picks[:, 0].copy()
    two = np.empty(n, dtype=int)
    changed = np.zeros(n, dtype=bool)
    load = np.zeros(bins, dtype=int)
    tied = 0
    for i in range(n):
        a, b = int(picks[i, 0]), int(picks[i, 1])
        if load[b] < load[a]:
            c = b
            changed[i] = True
        else:
            c = a
            if load[a] == load[b] and a != b:
                tied += 1
        two[i] = c
        load[c] += 1
    return {"picks": picks, "random": random_bin, "two": two, "changed": changed, "tied": tied}


def stats(loads: np.ndarray) -> dict:
    return {"tallest": int(loads.max()), "shortest": int(loads.min()), "spread": int(loads.max() - loads.min()),
            "sd": float(loads.std()), "over": int((loads > loads.mean() * 1.1).sum()), "under": int((loads < loads.mean() * 0.9).sum())}


def landing_times(keys: list, n: int) -> np.ndarray:
    """Landing time of ball i (count i + 1) from (time, count) keys; the count
    grows log-linearly inside a segment and holds where two keys share a count."""
    t = np.empty(n)
    for (t0, n0), (t1, n1) in zip(keys, keys[1:]):
        n0, n1 = int(n0), int(n1)
        if n1 <= n0:
            continue
        c = np.arange(n0 + 1, min(n1, n) + 1, dtype=float)
        t[n0 : n0 + len(c)] = t0 + (t1 - t0) * (np.log(c + 1.0) - np.log(n0 + 1.0)) / (np.log(n1 + 1.0) - np.log(n0 + 1.0))
    return t


def measure(man: dict) -> dict:
    n, bins, claim = man["balls"], man["bins"], man["claim_balls"]
    r = run(np.random.RandomState(man["seed"]), n, bins)
    print(f"{n:,} balls into {bins} bins at seed {man['seed']}, claim read at {claim:,} balls; both panels use the same first pick")
    print(f"  the second pick changed the choice {int(r['changed'][:claim].sum()):,} times in the first {claim:,} balls "
          f"= {100 * r['changed'][:claim].mean():.1f}%, {int(r['changed'].sum()):,} times in all {n:,}; "
          f"the two bins were tied {r['tied']:,} times")
    out = {"run": r}
    for name in ("random", "two"):
        chosen = r[name]
        for label, k in (("claim", claim), ("long", n)):
            loads = np.bincount(chosen[:k], minlength=bins)
            s = stats(loads)
            out[f"{name}_{label}"] = s
            print(f"{name} at {k:,} balls: tallest {s['tallest']:,}, shortest {s['shortest']:,}, spread {s['spread']}, "
                  f"average {loads.mean():.1f}, standard deviation {s['sd']:.2f}; bins over 110% of average: {s['over']}, under 90%: {s['under']}")
        for k in (100, 1000, 2000, 5000, 10000, 20000, 50000, 100000):
            if k > n:
                break
            lk = np.bincount(chosen[:k], minlength=bins)
            print(f"  after {k:>7,} balls: tallest {int(lk.max()):>5,}, shortest {int(lk.min()):>5,}, spread {int(lk.max() - lk.min()):>4}, average {k / bins:,.0f}")
    print(f"ratio of spreads at {claim:,}: {out['random_claim']['spread'] / out['two_claim']['spread']:.1f}x; "
          f"at {n:,}: {out['random_long']['spread'] / out['two_long']['spread']:.1f}x")
    print(f"theory: random load standard deviation sqrt(balls/bins): {np.sqrt(claim / bins):.1f} at {claim:,}, {np.sqrt(n / bins):.1f} at {n:,}; "
          f"two choices keep the tallest within about log2(ln {bins}) = {np.log2(np.log(bins)):.1f} of the average, whatever the count")
    # Check: a separate run of claim_balls at the same seed makes the same picks.
    short = run(np.random.RandomState(man["seed"]), claim, bins)
    same = bool(np.array_equal(short["picks"], r["picks"][:claim]) and np.array_equal(short["two"], r["two"][:claim]))
    print(f"check: a separate {claim:,}-ball run at seed {man['seed']} makes the same picks and choices: {same}")
    # Check: many seeds at the claim count.
    seeds = man["check_seeds"]
    sp = {"random": [], "two": []}
    tall = {"random": [], "two": []}
    for s in range(seeds):
        rr = run(np.random.RandomState(s), claim, bins)
        for name in ("random", "two"):
            l = np.bincount(rr[name], minlength=bins)
            sp[name].append(int(l.max() - l.min()))
            tall[name].append(int(l.max()))
    for name in ("random", "two"):
        a, t = np.array(sp[name]), np.array(tall[name])
        print(f"check: {name} at {claim:,} balls over seeds 0..{seeds - 1}: spread mean {a.mean():.1f} (min {a.min()}, max {a.max()}), "
              f"tallest mean {t.mean():.1f} (min {t.min()}, max {t.max()})")
    return out


class Renderer:
    def __init__(self, man: dict, meas: dict):
        self.man, self.meas = man, meas
        self.fps = man["fps"]
        font = os.environ["SEED_ZERO_FONT"]
        self.font = ImageFont.truetype(font, 40)
        self.font_small = ImageFont.truetype(font, 32)
        self.font_tiny = ImageFont.truetype(font, 26)
        self.font_big = ImageFont.truetype(font, 56)
        n, bins = man["balls"], man["bins"]
        self.bins = bins
        self.t_land = landing_times(man["land_keys"], n)
        self.fall = float(man["fall_s"])
        self.pitch = (BIN_X1 - BIN_X0) / bins
        self.changed_cum = np.concatenate([[0], np.cumsum(meas["run"]["changed"])])
        # Rank of each ball inside its bin under each rule, for the landing height.
        self.rank = {}
        for name in ("random", "two"):
            chosen = meas["run"][name]
            seen = np.zeros(bins, dtype=int)
            rank = np.empty(n, dtype=int)
            for i, c in enumerate(chosen):
                rank[i] = seen[c]
                seen[c] += 1
            self.rank[name] = rank

    def bin_x(self, b: int) -> float:
        return BIN_X0 + (b + 0.5) * self.pitch

    def frame_at(self, f: int) -> np.ndarray:
        man, m = self.man, self.meas
        t = f / self.fps
        n_land = int(np.searchsorted(self.t_land, t, side="right"))
        hi = int(np.searchsorted(self.t_land, t + self.fall, side="right"))
        pil = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(pil)
        bw = self.pitch - 1.6
        loads = {name: np.bincount(m["run"][name][:n_land], minlength=self.bins) for name in PANEL}
        # One shared vertical scale so the panels compare honestly; it zooms
        # out as the random panel's tallest stack grows.
        scale = max(float(man["scale_balls"]), 1.12 * float(loads["random"].max()))
        ppb = (FLOOR_DY - TOP_DY - 40) / scale
        stride = max(1, (hi - n_land) // man["max_falling"])
        for name, p in PANEL.items():
            y0, col = p["y0"], p["col"]
            floor = y0 + FLOOR_DY
            chosen = m["run"][name]
            ld = loads[name]
            d.text((60, y0 + 20), p["label"], font=self.font, fill=col, anchor="lm")
            d.text((W - 60, y0 + 20), f"balls {n_land:,}", font=self.font_tiny, fill=MUTED, anchor="rm")
            d.line((BIN_X0, floor, BIN_X1, floor), fill=TEXT, width=2)
            if name == "two" and n_land < man["peek_until"]:
                for i in range(n_land, hi):
                    for b in m["run"]["picks"][i]:
                        x = self.bin_x(int(b))
                        d.rectangle((x - bw / 2 - 2, y0 + TOP_DY, x + bw / 2 + 2, floor), outline=col, width=1)
            for b in range(self.bins):
                hgt = ld[b] * ppb
                if hgt >= 1:
                    x = self.bin_x(b)
                    d.rectangle((x - bw / 2, floor - hgt, x + bw / 2, floor - 1), fill=col)
            if n_land:
                avg = n_land / self.bins
                ya = floor - avg * ppb
                for xs in np.arange(BIN_X0, BIN_X1, 24):
                    d.line((xs, ya, xs + 12, ya), fill=TEXT, width=2)
                d.text((BIN_X1, ya - 8), f"average {avg:,.0f}", font=self.font_tiny, fill=TEXT, anchor="rb",
                       stroke_width=3, stroke_fill=BG)
            for i in range(n_land, hi, stride):
                u = 1.0 - (self.t_land[i] - t) / self.fall
                x = self.bin_x(int(chosen[i]))
                y_end = floor - (self.rank[name][i] + 1) * ppb
                y = y0 + TOP_DY + (y_end - y0 - TOP_DY) * u * u
                d.ellipse((x - 5, y - 5, x + 5, y + 5), fill=WHITE)
            if n_land >= man["mark_from"]:
                tall_b, short_b = int(ld.argmax()), int(ld.argmin())
                for b, val, colr in ((tall_b, ld[tall_b], RED), (short_b, ld[short_b], MUTED)):
                    x = self.bin_x(b)
                    ytop = floor - val * ppb
                    d.polygon(((x, ytop - 12), (x - 9, ytop - 28), (x + 9, ytop - 28)), fill=colr)
                # The readout row carries the marker colours, so the bars stay free of labels.
                tall_txt = f"tallest {ld.max():,}"
                d.text((60, y0 + READ_DY), tall_txt, font=self.font_small, fill=RED, anchor="lm")
                tw = d.textlength(tall_txt, font=self.font_small)
                d.text((60 + tw + 36, y0 + READ_DY), f"shortest {ld.min():,}", font=self.font_small, fill=MUTED, anchor="lm")
                d.text((W - 60, y0 + READ_DY), f"gap {ld.max() - ld.min():,}", font=self.font_big, fill=col, anchor="rm")
            if name == "two" and t >= man["peek_t"]:
                claim = man["claim_balls"]
                d.text((60, y0 + 60), f"{claim:,} balls: the second look changed the pick {int(self.changed_cum[claim]):,} times",
                       font=self.font_tiny, fill=MUTED, anchor="lm")
        if t >= man["payoff_t"]:
            alpha = min(1.0, (t - man["payoff_t"]) / man["payoff_hold"])
            shade = tuple(int(c * alpha + BG[i] * (1 - alpha)) for i, c in enumerate(GOLD))
            d.text((W / 2, PAYOFF_Y), man["payoff_text"], font=self.font, fill=shade, anchor="mm")
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
    man = json.loads((ROOT / "projects/bins/manifest.json").read_text())
    meas = measure(man)
    if "--measure-only" in sys.argv:
        return
    Renderer(man, meas).render(ROOT / "media/bins/footage.mp4")


if __name__ == "__main__":
    main()
