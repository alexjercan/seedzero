#!/usr/bin/env python3
"""Streak test: which coin is fair?

Two coins flip side by side from the same seeded draws (seed 0, numpy
RandomState). The top coin is fair: heads when the draw is under one half.
The bottom coin gets the same intended flip but is never allowed more than
three of the same side in a row: after three, it switches whatever the
draw says. Ten thousand runs of one hundred flips each. A coin that lands
inside a streak of six or more lights up gold.

Measured and printed for each coin: how many of the runs hold a streak of
five, six, seven, eight and ten or more, the longest streak in the whole
stream and which run holds it, the mean longest streak per run, the exact
probabilities from a transfer matrix for the fair coin, and as checks the
same counts at another seed and the mean over many seeds.

usage: streaks.py [--measure-only]
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
HEADS = (70, 150, 200)
TAILS = (58, 66, 78)
WHITE = (255, 255, 255)

# Layout: two panels, captions between them at caption_y 0.49 (y 941..1021).
PANEL = {"fair": {"y0": 130}, "safe": {"y0": 1050}}
BODY_TOP, BODY_BOTTOM = 120, 750
PER_ROW = 25
PITCH_X = 40.0
PITCH_Y = 42.0
COIN_R = 15
X0 = 60.0
PAYOFF_Y = 1868.0


def flip_streams(rng: np.random.RandomState, runs: int, per_run: int, safe_max: int) -> dict:
    u = rng.random_sample(runs * per_run)
    fair = u < 0.5
    safe = np.empty_like(fair)
    for r in range(runs):
        base = r * per_run
        streak = 0
        last = None
        for i in range(base, base + per_run):
            want = bool(fair[i])
            if last is not None and want == last and streak >= safe_max:
                want = not want
            if want == last:
                streak += 1
            else:
                streak = 1
                last = want
            safe[i] = want
    return {"fair": fair, "safe": safe}


def streak_info(flips: np.ndarray, runs: int, per_run: int) -> dict:
    """Per flip: the index where its streak began (run-local streaks) and the
    streak length ending at that flip. Per run: the longest streak."""
    n = runs * per_run
    start = np.empty(n, dtype=np.int64)
    length = np.empty(n, dtype=np.int64)
    final = np.empty(n, dtype=np.int64)
    longest = np.zeros(runs, dtype=np.int64)
    for r in range(runs):
        base = r * per_run
        s = base
        for i in range(base, base + per_run):
            if i > base and flips[i] != flips[i - 1]:
                final[s:i] = i - s
                s = i
            start[i] = s
            length[i] = i - s + 1
        final[s : base + per_run] = base + per_run - s
        longest[r] = length[base : base + per_run].max()
    return {"start": start, "length": length, "final": final, "longest": longest}


def exact_no_run(n: int, k: int) -> float:
    """Probability that n fair flips hold no run of k or more."""
    # state j = current run length (1..k-1); after the first flip the run is 1.
    probs = np.zeros(k)
    probs[1] = 1.0
    for _ in range(n - 1):
        nxt = np.zeros(k)
        for j in range(1, k):
            nxt[1] += 0.5 * probs[j]
            if j + 1 < k:
                nxt[j + 1] += 0.5 * probs[j]
        probs = nxt
    return float(probs.sum())


def measure(man: dict) -> dict:
    runs, per_run, k, safe_max = man["runs"], man["flips_per_run"], man["streak"], man["safe_max"]
    streams = flip_streams(np.random.RandomState(man["seed"]), runs, per_run, safe_max)
    out = {}
    print(f"{runs:,} runs of {per_run} flips at seed {man['seed']}; the safe coin never runs past {safe_max}")
    for name in ("fair", "safe"):
        info = streak_info(streams[name], runs, per_run)
        longest = info["longest"]
        out[name] = {"flips": streams[name], **info}
        print(f"{name} coin:")
        for kk in (4, 5, 6, 7, 8, 10):
            c = int((longest >= kk).sum())
            line = f"  runs with a streak of {kk} or more: {c:,} of {runs:,} = {100 * c / runs:.1f}%"
            if name == "fair":
                line += f" (exact {100 * (1 - exact_no_run(per_run, kk)):.1f}%)"
            print(line)
        r_best = int(longest.argmax())
        print(f"  longest streak: {int(longest.max())} in run {r_best + 1:,}; mean longest per run {longest.mean():.2f}; "
              f"heads {100 * streams[name].mean():.2f}%")
        counts = np.bincount(longest, minlength=per_run + 1)
        top = ", ".join(f"{i}: {int(counts[i]):,}" for i in range(1, per_run + 1) if counts[i])
        print(f"  longest streak per run, histogram: {top}")
    same = int((streams["fair"] == streams["safe"]).sum())
    print(f"the safe coin agreed with the fair coin on {same:,} of {runs * per_run:,} flips; forced switches {runs * per_run - same:,}")
    # Checks.
    cs = man["check_seed"]
    chk = flip_streams(np.random.RandomState(cs), runs, per_run, safe_max)
    lg = streak_info(chk["fair"], runs, per_run)["longest"]
    print(f"check: fair coin at seed {cs}: {int((lg >= k).sum()):,} of {runs:,} runs hold {k}+; longest {int(lg.max())}")
    small_runs = 100
    counts6 = []
    for s in range(man["check_seeds"]):
        st = flip_streams(np.random.RandomState(s), small_runs, per_run, safe_max)
        counts6.append(int((streak_info(st["fair"], small_runs, per_run)["longest"] >= k).sum()))
    a = np.array(counts6)
    print(f"check: fair coin, {small_runs} runs per seed over seeds 0..{man['check_seeds'] - 1}: "
          f"mean {a.mean():.1f} of {small_runs} hold {k}+ (min {a.min()}, max {a.max()}); exact {100 * (1 - exact_no_run(per_run, k)):.1f}%")
    out["fair6"] = int((out["fair"]["longest"] >= k).sum())
    out["longest"] = int(out["fair"]["longest"].max())
    return out


def landing_times(keys: list, n: int) -> np.ndarray:
    counts = np.arange(1, n + 1, dtype=float)
    keys = np.array(keys, dtype=float)
    return np.interp(np.log(counts + 1.0), np.log(keys[:, 1] + 1.0), keys[:, 0])


class Renderer:
    def __init__(self, man: dict, meas: dict):
        self.man, self.meas = man, meas
        self.fps = man["fps"]
        font = os.environ["SEED_ZERO_FONT"]
        self.font = ImageFont.truetype(font, 40)
        self.font_small = ImageFont.truetype(font, 32)
        self.font_tiny = ImageFont.truetype(font, 26)
        self.font_big = ImageFont.truetype(font, 56)
        self.font_coin = ImageFont.truetype(font, 20)
        self.runs, self.per_run, self.k = man["runs"], man["flips_per_run"], man["streak"]
        n = self.runs * self.per_run
        self.n = n
        self.t_land = landing_times(man["flip_keys"], n)
        nr = man["replay_runs"] * self.per_run
        self.t_replay = man["replay_t"] + np.arange(nr) * (man["replay_s"] / nr)
        self.rows_visible = int((BODY_BOTTOM - BODY_TOP) // PITCH_Y)
        for name in ("fair", "safe"):
            lg = meas[name]["longest"]
            meas[name]["hit_cum"] = np.concatenate([[0], np.cumsum(lg >= self.k)])
            meas[name]["long_cum"] = np.concatenate([[0], np.maximum.accumulate(lg)])

    def coin(self, d: ImageDraw.ImageDraw, x: float, y: float, heads: bool, hot: bool, squash: float = 1.0) -> None:
        ry = COIN_R * max(0.12, squash)
        fill = GOLD if hot else (HEADS if heads else TAILS)
        d.ellipse((x - COIN_R, y - ry, x + COIN_R, y + ry), fill=fill)
        if squash > 0.7:
            d.text((x, y + 1), "H" if heads else "T", font=self.font_coin, fill=BG if hot else WHITE, anchor="mm")

    def frame_at(self, f: int) -> np.ndarray:
        man, m = self.man, self.meas
        t = f / self.fps
        replay = t >= man["replay_t"]
        t_land = self.t_replay if replay else self.t_land
        c = int(np.searchsorted(t_land, t, side="right"))
        revealed = t >= man["reveal_t"]
        img = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(img)
        runs_done = c // self.per_run
        for name, p in PANEL.items():
            y0 = p["y0"]
            data = m[name]
            flips, start, final = data["flips"], data["start"], data["final"]
            if revealed:
                label = "fair coin" if name == "fair" else f"same draws, never past {man['safe_max']}"
                col = GOLD if name == "fair" else MUTED
            else:
                label = "coin A" if name == "fair" else "coin B"
                col = TEAL
            if replay:
                hits, longest, shown = int(data["hit_cum"][self.runs]), int(data["long_cum"][self.runs]), self.runs
                label = ("fair coin" if name == "fair" else f"never past {man['safe_max']}") + "  (replay)"
            else:
                hits, longest, shown = int(data["hit_cum"][runs_done]), int(data["long_cum"][runs_done]), runs_done
            d.text((60, y0 + 20), label, font=self.font, fill=col, anchor="lm")
            d.text((W - 60, y0 + 20), f"longest {longest}", font=self.font_small, fill=TEXT, anchor="rm")
            d.text((60, y0 + 76), f"runs with {self.k}+ in a row", font=self.font_small, fill=TEXT, anchor="lm")
            d.text((W - 60, y0 + 76), f"{hits:,} of {shown:,}", font=self.font_big, fill=GOLD if hits else MUTED, anchor="rm")
            # Rows glide upward as flips land; the newest row sits at the bottom.
            body_top, body_bottom = y0 + BODY_TOP, y0 + BODY_BOTTOM
            r_cur = c // PER_ROW
            frac = (c % PER_ROW) / PER_ROW
            y_cur = body_bottom - PITCH_Y / 2 - frac * PITCH_Y
            for k in range(max(0, r_cur - self.rows_visible), r_cur + 1):
                y = y_cur - (r_cur - k) * PITCH_Y
                if y < body_top + COIN_R:
                    continue
                if (k * PER_ROW) % self.per_run == 0:
                    d.line((40, y - PITCH_Y / 2, W - 40, y - PITCH_Y / 2), fill=GRIDLINE, width=2)
                for j in range(PER_ROW):
                    idx = k * PER_ROW + j
                    if idx >= c:
                        break
                    hot = final[idx] >= self.k and c >= start[idx] + self.k
                    age = t - t_land[idx]
                    x = X0 + j * PITCH_X
                    if idx >= c - 3 and age < 0.12:
                        u = age / 0.12
                        self.coin(d, x, y - (1 - u) * 60, bool(flips[idx]), hot, abs(math.cos(u * 4.0)))
                    else:
                        self.coin(d, x, y, bool(flips[idx]), hot)
        if t >= man["payoff_t"]:
            alpha = min(1.0, (t - man["payoff_t"]) / man["payoff_hold"])
            shade = tuple(int(c_ * alpha + BG[i] * (1 - alpha)) for i, c_ in enumerate(GOLD))
            text = man["payoff_text"].format(fair6=m["fair6"], runs=self.runs, longest=m["longest"])
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
    man = json.loads((ROOT / "projects/streaks/manifest.json").read_text())
    meas = measure(man)
    if "--measure-only" in sys.argv:
        return
    Renderer(man, meas).render(ROOT / "media/streaks/footage.mp4")


if __name__ == "__main__":
    main()
