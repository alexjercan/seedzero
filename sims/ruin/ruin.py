#!/usr/bin/env python3
"""Gambler's ruin: ten chips against a hundred, a fair coin versus a coin
that is forty nine percent.

Each game: the player starts with player_chips, the house with
house_chips, one chip a flip, and the game ends when one side has
nothing. Ten thousand games are played in each panel from the same seeded
stream of uniform draws: flip j of game i uses the same draw u in both
panels, and the player wins that flip when u < p. The fair panel uses
p = 0.5, the tilted panel p = 0.49, so exactly the draws that fall in
[0.49, 0.5) come out differently: about one flip in a hundred.

Measured and printed for each panel: how many players broke the house,
how many went bust, the mean, median and longest game in flips, and the
exact win probability and expected game length from the ruin formulas as
a check. Also printed: the share of draws that land differently between
the two panels.

usage: ruin.py [--measure-only]
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
PATH = (70, 84, 100)

# Layout: two chart panels, captions between them at caption_y 0.49 (y 941..1021).
PANEL = {"fair": {"label_y": 180.0, "y0": 300, "y1": 760, "read_y": 830.0, "col": TEAL},
         "tilted": {"label_y": 1120.0, "y0": 1240, "y1": 1700, "read_y": 1770.0, "col": GOLD}}
CHART_X0, CHART_X1 = 150, 1010
PAYOFF_Y = 1868.0


def exact_win(a: int, n: int, p: float) -> float:
    if p == 0.5:
        return a / n
    r = (1 - p) / p
    return (1 - r ** a) / (1 - r ** n)


def exact_length(a: int, n: int, p: float) -> float:
    if p == 0.5:
        return a * (n - a)
    q = 1 - p
    return a / (q - p) - n / (q - p) * exact_win(a, n, p)


def play(man: dict) -> dict:
    """Play all games in both panels on shared draws. Records for every
    game the outcome and length, and for the first shown_games the full
    chip path of the player (sampled every flip)."""
    rng = np.random.RandomState(man["seed"])
    g, a, n = man["games"], man["player_chips"], man["player_chips"] + man["house_chips"]
    chunk = man["chunk"]
    panels = {"fair": man["p_fair"], "tilted": man["p_tilted"]}
    chips = {k: np.full(g, a, dtype=np.int32) for k in panels}
    alive = {k: np.ones(g, dtype=bool) for k in panels}
    length = {k: np.zeros(g, dtype=np.int64) for k in panels}
    won = {k: np.zeros(g, dtype=bool) for k in panels}
    shown = man["shown_games"]
    paths = {k: [np.full((shown, 1), a, dtype=np.int16)] for k in panels}
    flips_done = 0
    differ = 0
    total_draws = 0
    while flips_done < man["max_flips"] and any(alive[k].any() for k in panels):
        u = rng.random_sample((g, chunk))
        total_draws += u.size
        differ += int(((u >= min(panels.values())) & (u < max(panels.values()))).sum())
        for k, p in panels.items():
            if not alive[k].any():
                continue
            step = np.where(u < p, 1, -1).astype(np.int32)
            step[~alive[k]] = 0
            run = chips[k][:, None] + np.cumsum(step, axis=1)
            # First flip index at which the game ends inside this chunk.
            ended = (run <= 0) | (run >= n)
            has_end = ended.any(axis=1)
            first = np.where(has_end, np.argmax(ended, axis=1), chunk)
            # Freeze the path after the end.
            idx = np.arange(chunk)[None, :]
            run_frozen = np.where(idx <= first[:, None], run, run[np.arange(g), np.minimum(first, chunk - 1)][:, None])
            paths[k].append(run_frozen[:shown].astype(np.int16))
            newly = alive[k] & has_end
            length[k][newly] = flips_done + first[newly] + 1
            won[k][newly] = run[newly, first[newly]] >= n
            chips[k] = run_frozen[:, -1]
            alive[k] &= ~has_end
        flips_done += chunk
    out = {"differ": differ / total_draws, "flips_done": flips_done}
    for k in panels:
        assert not alive[k].any(), f"{k}: {int(alive[k].sum())} games still running at {flips_done} flips"
        out[k] = {"won": won[k], "length": length[k], "paths": np.concatenate(paths[k], axis=1)}
    return out


def measure(man: dict) -> dict:
    g, a, n = man["games"], man["player_chips"], man["player_chips"] + man["house_chips"]
    res = play(man)
    print(f"{g:,} games per panel at seed {man['seed']}: player {a} chips, house {man['house_chips']} chips, one chip a flip, "
          f"same draws in both panels; {100 * res['differ']:.2f}% of draws land differently")
    for k, p in (("fair", man["p_fair"]), ("tilted", man["p_tilted"])):
        r = res[k]
        w = int(r["won"].sum())
        L = r["length"]
        ew, el = exact_win(a, n, p), exact_length(a, n, p)
        sd = math.sqrt(ew * (1 - ew) / g)
        print(f"{k}: player wins a flip with probability {p}")
        print(f"  player broke the house in {w:,} games = {100 * w / g:.2f}% (exact {100 * ew:.2f}%, one standard deviation {100 * sd:.2f} points); "
              f"went bust in {g - w:,} = {100 * (g - w) / g:.2f}%")
        print(f"  game length: mean {L.mean():.1f} flips (exact {el:.1f}), median {int(np.median(L))}, shortest {L.min()}, longest {L.max():,}")
        print(f"  games over within 10 flips: {int((L <= 10).sum()):,}; within 100: {int((L <= 100).sum()):,}; "
              f"within 1,000: {int((L <= 1000).sum()):,}; within 10,000: {int((L <= 10000).sum()):,}")
        wl = L[r["won"]]
        if len(wl):
            print(f"  winning games: mean {wl.mean():.1f} flips, median {int(np.median(wl))}, shortest {wl.min()}, longest {wl.max():,}")
        print(f"  peak chips reached by a busted player: {int(r['paths'][~r['won'][:len(r['paths'])]].max()) if (~r['won'][:len(r['paths'])]).any() else 0} (among the {len(r['paths'])} recorded paths)")
    wf, wt = int(res["fair"]["won"].sum()), int(res["tilted"]["won"].sum())
    print(f"ratio: {wf / max(wt, 1):.1f}x more players break the house with the fair coin")
    both = res["fair"]["won"] & res["tilted"]["won"]
    print(f"games won in both panels: {int(both.sum()):,}; won fair but lost tilted: {int((res['fair']['won'] & ~res['tilted']['won']).sum()):,}; "
          f"won tilted but lost fair: {int((~res['fair']['won'] & res['tilted']['won']).sum()):,}")
    print(f"exact win probability for other tilts from {a} against {man['house_chips']}: "
          + ", ".join(f"p={p}: {100 * exact_win(a, n, p):.2f}%" for p in (0.5, 0.495, 0.49, 0.48, 0.45)))
    return res


class Renderer:
    def __init__(self, man: dict, meas: dict):
        self.man, self.meas = man, meas
        self.fps = man["fps"]
        font = os.environ["SEED_ZERO_FONT"]
        self.font = ImageFont.truetype(font, 40)
        self.font_small = ImageFont.truetype(font, 32)
        self.font_tiny = ImageFont.truetype(font, 26)
        self.font_big = ImageFont.truetype(font, 56)
        self.n = man["player_chips"] + man["house_chips"]
        self.shown = man["shown_games"]
        # Log x axis from flip 1 to clock_max_flips; a column per pixel.
        self.cols = CHART_X1 - CHART_X0
        self.col_flip = np.unique(np.round(np.logspace(0, math.log10(man["clock_max_flips"]), self.cols)).astype(np.int64))
        self.canvas = {}
        self.drawn_cols = {}
        for k in ("fair", "tilted"):
            p = PANEL[k]
            self.canvas[k] = Image.new("RGB", (W, p["y1"] - p["y0"] + 1), BG)
            self.drawn_cols[k] = 0
            paths = meas[k]["paths"]
            idx = np.minimum(self.col_flip, paths.shape[1] - 1)
            meas[k]["sampled"] = paths[:, idx].astype(np.float64)   # shown_games x len(col_flip)
            order = np.argsort(meas[k]["length"], kind="stable")
            meas[k]["end_order"] = order
            meas[k]["end_len"] = meas[k]["length"][order]

    def x_of(self, flip: float) -> float:
        return CHART_X0 + self.cols * math.log10(max(1.0, flip)) / math.log10(self.man["clock_max_flips"])

    def flips_at(self, scene_t: float) -> float:
        man = self.man
        frac = (scene_t - man["start_t"]) / (man["clock_end_t"] - man["start_t"])
        frac = max(0.0, min(1.0, frac))
        return 10 ** (frac * math.log10(man["clock_max_flips"]))

    def draw_paths(self, k: str, flips: float) -> None:
        """Extend the persistent path canvas up to the current flip."""
        p = PANEL[k]
        y0, y1 = p["y0"], p["y1"]
        h = y1 - y0
        d = ImageDraw.Draw(self.canvas[k])
        target = int(np.searchsorted(self.col_flip, flips, side="right"))
        start = max(1, self.drawn_cols[k])
        sampled = self.meas[k]["sampled"]
        length = self.meas[k]["length"][:self.shown]
        won = self.meas[k]["won"][:self.shown]
        for c in range(start, target):
            f0, f1 = self.col_flip[c - 1], self.col_flip[c]
            xa, xb = self.x_of(f0), self.x_of(f1)
            for gi in range(self.shown):
                if length[gi] < f0:
                    continue
                ya = h - h * sampled[gi, c - 1] / self.n
                yb = h - h * sampled[gi, c] / self.n
                d.line((xa, ya, xb, yb), fill=PATH, width=1)
                if f0 < length[gi] <= f1:
                    col = TEAL if won[gi] else RED
                    d.ellipse((xb - 4, yb - 4, xb + 4, yb + 4), fill=col)
        self.drawn_cols[k] = max(self.drawn_cols[k], target)

    def frame_at(self, f: int) -> np.ndarray:
        man = self.man
        scene_t = f / self.fps
        flips = self.flips_at(scene_t)
        pil = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(pil)
        for k, label in (("fair", "fair coin: 50%"), ("tilted", "tilted coin: 49%")):
            p = PANEL[k]
            self.draw_paths(k, flips)
            pil.paste(self.canvas[k], (0, p["y0"]))
            y0, y1 = p["y0"], p["y1"]
            d.text((CHART_X0, p["label_y"]), label, font=self.font, fill=p["col"], anchor="lm")
            right = f"flip {int(flips):,}" if k == "fair" else f"{man['games']:,} games each"
            d.text((CHART_X1, p["label_y"]), right, font=self.font_small, fill=MUTED, anchor="rm")
            d.rectangle((CHART_X0, y0, CHART_X1, y1), outline=GRIDLINE, width=2)
            for chips, lab in ((0, "bust"), (man["player_chips"], f"{man['player_chips']}"), (self.n, f"{self.n}")):
                yy = y1 - (y1 - y0) * chips / self.n
                d.line((CHART_X0, yy, CHART_X1, yy), fill=GRIDLINE, width=1)
                d.text((CHART_X0 - 12, yy), lab, font=self.font_tiny, fill=MUTED, anchor="rm")
            d.text((CHART_X0 + 12, y0 + 14), f"house broke: player holds all {self.n} chips", font=self.font_tiny, fill=MUTED, anchor="lt")
            for fl in (1, 10, 100, 1000, 10000):
                x = self.x_of(fl)
                if fl == 10000:
                    # The unit rides on the last tick so the readout line below stays clear.
                    d.text((x - self.font_tiny.getlength("10,000") / 2, y1 + 22), "10,000 flips", font=self.font_tiny, fill=MUTED, anchor="lm")
                else:
                    d.text((x, y1 + 22), f"{fl:,}", font=self.font_tiny, fill=MUTED, anchor="mm")
            if flips > 1:
                x = self.x_of(flips)
                d.line((x, y0, x, y1), fill=TEXT, width=1)
            ms = man["milestone_flips"]
            if flips >= ms:
                xm = self.x_of(ms)
                over = int((self.meas[k]["length"] <= ms).sum())
                d.line((xm, y0, xm, y1), fill=MUTED, width=1)
                d.text((xm + 10, y0 + 54), f"over by flip {ms}: {over:,}", font=self.font_tiny, fill=TEXT, anchor="lt")
            # Tallies over all games, by the current flip.
            done = int(np.searchsorted(self.meas[k]["end_len"], flips, side="right"))
            order = self.meas[k]["end_order"][:done]
            won_now = int(self.meas[k]["won"][order].sum())
            bust_now = done - won_now
            playing = man["games"] - done
            d.text((CHART_X0, p["read_y"]), f"broke the house  {won_now:,}", font=self.font_small, fill=p["col"], anchor="lm")
            d.text((CHART_X1, p["read_y"]), f"bust  {bust_now:,}", font=self.font_small, fill=RED, anchor="rm")
            d.text((W / 2, p["read_y"] + 46), f"still playing {playing:,}" if playing else f"all over; average game {self.meas[k]['length'].mean():,.0f} flips",
                   font=self.font_tiny, fill=MUTED, anchor="mm")
        if scene_t >= man["payoff_t"]:
            alpha = min(1.0, (scene_t - man["payoff_t"]) / man["payoff_hold"])
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
    man = json.loads((ROOT / "projects/ruin/manifest.json").read_text())
    if "--check" in sys.argv:
        # Independent check: more games at another seed, both panels.
        i = sys.argv.index("--check")
        man = {**man, "games": int(sys.argv[i + 1]), "seed": int(sys.argv[i + 2]), "shown_games": 1}
        measure(man)
        return
    meas = measure(man)
    if "--measure-only" in sys.argv:
        return
    Renderer(man, meas).render(ROOT / "media/ruin/footage.mp4")


if __name__ == "__main__":
    main()
