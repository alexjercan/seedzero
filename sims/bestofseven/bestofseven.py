#!/usr/bin/env python3
"""Best of seven: how often does the better team win the series?

One team wins any single game with probability p (0.55). One hundred
thousand best-of-seven series are played from one seeded stream: games
continue until a team has four wins. The sim counts the series the better
team wins, the series lengths, and the sweeps, and checks the count
against the exact probability from the binomial tail. It also computes,
exactly, the series win probability for every odd series length up to
max_games and reports the shortest series that gives the better team the
title nine times in ten (and 95 and 99 in 100).

usage: bestofseven.py [--measure-only]
"""

from __future__ import annotations

import json
import math
from fractions import Fraction
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
TEXT = (216, 222, 230)
MUTED = (138, 148, 163)
GRIDLINE = (40, 48, 58)
DIM_TEAL = (44, 96, 80)
DIM_GOLD = (110, 84, 44)

# Layout. Caption band at caption_y 0.68: y 1306..1390.
GRID_COLS, GRID_ROWS, CELL = 400, 250, 2       # 100,000 series, 800 x 500 px
GRID_X0, GRID_Y0 = 140, 200
BOARD_Y = 760.0                                # the series being played now
BAR_Y0, BAR_H = 880, 56                        # two racing bars
BAR_X0, BAR_X1 = 140, 940
CHART_X0, CHART_X1, CHART_Y0, CHART_Y1 = 190, 980, 1500, 1780
PAYOFF_Y = 1868.0


def series_win_prob(n_games: int, p: float) -> float:
    """Probability that a team winning each game with probability p wins a
    best-of-n_games series (first to (n_games + 1) / 2 wins): the binomial
    tail, summed in log space so long series do not overflow."""
    need = (n_games + 1) // 2
    lp, lq = math.log(p), math.log(1 - p)
    lg = math.lgamma
    return sum(math.exp(lg(n_games + 1) - lg(k + 1) - lg(n_games - k + 1) + k * lp + (n_games - k) * lq)
               for k in range(need, n_games + 1))


def series_win_prob_exact(n_games: int, p: Fraction) -> Fraction:
    """The same tail in exact rational arithmetic, used as a check."""
    need = (n_games + 1) // 2
    return sum(Fraction(math.comb(n_games, k)) * p ** k * (1 - p) ** (n_games - k) for k in range(need, n_games + 1))


def play(man: dict) -> dict:
    rng = np.random.RandomState(man["seed"])
    n, p, g = man["series"], man["p"], man["games"]
    need = (g + 1) // 2
    # Every game of every series is drawn up front from the one stream, in
    # series order, so the record is reproducible from the seed alone.
    wins = rng.random_sample((n, g)) < p          # True: the better team won the game
    better = np.cumsum(wins, axis=1)
    worse = np.cumsum(~wins, axis=1)
    b_done = np.where(better[:, -1] >= need, np.argmax(better >= need, axis=1) + 1, g + 1)
    w_done = np.where(worse[:, -1] >= need, np.argmax(worse >= need, axis=1) + 1, g + 1)
    length = np.minimum(b_done, w_done)
    better_won = b_done < w_done
    return {"wins": wins, "length": length, "better_won": better_won}


def measure(man: dict) -> dict:
    n, p, g = man["series"], man["p"], man["games"]
    res = play(man)
    won = int(res["better_won"].sum())
    exact = series_win_prob(g, p)
    exact_frac = series_win_prob_exact(g, Fraction(p).limit_denominator(1000))
    print(f"exact best-of-{g} probability as a fraction: {exact_frac} = {float(exact_frac):.6f}; log-space value {exact:.6f}")
    print(f"{n:,} best-of-{g} series at seed {man['seed']}; the better team wins each game with probability {p}")
    print(f"  better team won the series {won:,} times = {100 * won / n:.2f}%; the worse team {n - won:,} = {100 * (n - won) / n:.2f}%")
    print(f"  exact probability {100 * exact:.3f}%; the seeded count is {(won / n - exact) * 100:+.3f} points off "
          f"(one standard deviation is {100 * math.sqrt(exact * (1 - exact) / n):.3f} points)")
    for L in range(4, g + 1):
        m = res["length"] == L
        bw = int((res["better_won"] & m).sum())
        print(f"  series over in {L} games: {int(m.sum()):,} ({100 * m.mean():.1f}%), better team won {bw:,} of them")
    sweeps = int(((res["length"] == 4) & res["better_won"]).sum())
    swept = int(((res["length"] == 4) & ~res["better_won"]).sum())
    print(f"  sweeps: better team swept {sweeps:,} series, was swept in {swept:,}")
    g7 = res["length"] == g
    print(f"  game sevens: {int(g7.sum()):,}; the better team won {int((res['better_won'] & g7).sum()):,} of them "
          f"= {100 * (res['better_won'] & g7).sum() / g7.sum():.1f}%")
    # A single game and the exact curve over series length.
    print("exact series win probability by length:")
    curve = {}
    for L in range(1, man["max_games"] + 1, 2):
        curve[L] = series_win_prob(L, p)
    for L in (1, 3, 5, 7, 9, 11, 15, 21, 31, 51, 101):
        print(f"  best of {L:3d}: {100 * curve[L]:.2f}%")
    firsts = {}
    for target in man["targets"]:
        L = next(L for L in sorted(curve) if curve[L] >= target)
        firsts[target] = L
        print(f"  first series length giving the better team at least {100 * target:.0f}%: best of {L} ({100 * curve[L]:.2f}%; best of {L - 2}: {100 * curve[L - 2]:.2f}%)")
    return {**res, "won": won, "exact": exact, "curve": curve, "firsts": firsts}


class Renderer:
    def __init__(self, man: dict, meas: dict):
        self.man, self.meas = man, meas
        self.fps = man["fps"]
        font = os.environ["SEED_ZERO_FONT"]
        self.font = ImageFont.truetype(font, 40)
        self.font_small = ImageFont.truetype(font, 32)
        self.font_tiny = ImageFont.truetype(font, 26)
        self.font_big = ImageFont.truetype(font, 58)
        n = man["series"]
        # Pixel colour per series, in order of play.
        col = np.where(meas["better_won"][:, None], np.array(TEAL, dtype=np.uint8), np.array(GOLD, dtype=np.uint8))
        self.cells = col.reshape(GRID_ROWS, GRID_COLS, 3)
        self.cum_better = np.concatenate([[0], np.cumsum(meas["better_won"])])
        self.n = n

    def played_at(self, scene_t: float) -> int:
        man = self.man
        frac = (scene_t - man["start_t"]) / (man["fill_end_t"] - man["start_t"])
        return int(max(0.0, min(1.0, frac)) * self.n)

    def frame_at(self, f: int) -> np.ndarray:
        man = self.man
        scene_t = f / self.fps
        k = self.played_at(scene_t)
        frame = np.zeros((H, W, 3), dtype=np.uint8)
        frame[:, :] = BG
        # The grid fills row by row; unplayed cells stay dark.
        grid = np.zeros((GRID_ROWS, GRID_COLS, 3), dtype=np.uint8)
        grid[:, :] = (22, 27, 34)
        if k > 0:
            full_rows, rem = divmod(k, GRID_COLS)
            grid[:full_rows] = self.cells[:full_rows]
            if rem:
                grid[full_rows, :rem] = self.cells[full_rows, :rem]
        img = np.repeat(np.repeat(grid, CELL, 0), CELL, 1)
        frame[GRID_Y0:GRID_Y0 + img.shape[0], GRID_X0:GRID_X0 + img.shape[1]] = img
        pil = Image.fromarray(frame)
        d = ImageDraw.Draw(pil)
        d.text((GRID_X0, GRID_Y0 - 40), f"series {k:,} of {self.n:,}", font=self.font_small, fill=MUTED, anchor="lm")
        d.text((GRID_X0 + img.shape[1], GRID_Y0 - 40), "best of 7", font=self.font_small, fill=MUTED, anchor="rm")
        # The series being played now: its games as dots. The board changes
        # four times a second, during the fill and after it, so the eye has
        # something to follow while the counters hold.
        board_t = math.floor(scene_t * 4) / 4
        if k < self.n:
            idx = min(self.played_at(board_t), self.n - 1)
        else:
            idx = (self.n - 1 + int((board_t - man["fill_end_t"]) * 4)) % self.n
        wins = self.meas["wins"][idx]
        length = int(self.meas["length"][idx])
        d.text((GRID_X0, BOARD_Y), "this series:", font=self.font_small, fill=MUTED, anchor="lm")
        for gi in range(man["games"]):
            cx = GRID_X0 + 250 + gi * 62
            if gi < length:
                col = TEAL if wins[gi] else GOLD
                d.ellipse((cx - 22, BOARD_Y - 22, cx + 22, BOARD_Y + 22), fill=col)
            else:
                d.ellipse((cx - 22, BOARD_Y - 22, cx + 22, BOARD_Y + 22), outline=GRIDLINE, width=3)
        # Racing bars.
        better = int(self.cum_better[k])
        worse = k - better
        for i, (label, count, col) in enumerate((("better team", better, TEAL), ("worse team", worse, GOLD))):
            y = BAR_Y0 + i * (BAR_H + 74)
            d.text((BAR_X0, y - 26), label, font=self.font_small, fill=col, anchor="lm")
            share = count / k if k else 0.0
            d.text((BAR_X1, y - 26), f"{count:,}  |  {100 * share:.1f}%" if k else "", font=self.font_small, fill=col, anchor="rm")
            d.rectangle((BAR_X0, y, BAR_X1, y + BAR_H), outline=GRIDLINE, width=2)
            wpx = int((BAR_X1 - BAR_X0) * count / self.n)
            if wpx > 0:
                d.rectangle((BAR_X0, y, BAR_X0 + wpx, y + BAR_H), fill=col)
        # Chart: exact series win probability against series length (log x).
        curve = self.meas["curve"]
        L_max = max(self.meas["firsts"].values()) * 1.6
        def cx_of(L):
            return CHART_X0 + (CHART_X1 - CHART_X0) * math.log(L) / math.log(L_max)
        def cy_of(v):
            return CHART_Y1 - (CHART_Y1 - CHART_Y0) * (v - 0.5) / 0.5
        d.rectangle((CHART_X0, CHART_Y0, CHART_X1, CHART_Y1), outline=GRIDLINE, width=2)
        d.text((CHART_X0, CHART_Y0 - 64), "how often the better team wins the series", font=self.font_small, fill=MUTED, anchor="lm")
        for v in (0.5, 0.6, 0.7, 0.8, 0.9, 1.0):
            y = cy_of(v)
            d.line((CHART_X0, y, CHART_X1, y), fill=GRIDLINE, width=1)
            d.text((CHART_X0 - 12, y), f"{100 * v:.0f}%", font=self.font_tiny, fill=MUTED, anchor="rm")
        firsts = self.meas["firsts"]
        for L in (1, 7, 21, 51, firsts[0.9], firsts[0.99]):
            if L <= L_max:
                d.text((cx_of(L), CHART_Y1 + 24), f"{L}", font=self.font_tiny, fill=MUTED, anchor="mm")
        d.text((CHART_X1, CHART_Y1 + 50), "games in the series (log scale)", font=self.font_tiny, fill=MUTED, anchor="rm")
        pts = [(cx_of(L), cy_of(v)) for L, v in sorted(curve.items()) if L <= L_max]
        # The curve draws in between chart_start_t and chart_end_t, then holds.
        reveal = (scene_t - man["chart_start_t"]) / (man["chart_end_t"] - man["chart_start_t"])
        reveal = max(0.0, min(1.0, reveal))
        npts = int(len(pts) * reveal)
        if npts >= 2:
            d.line(pts[:npts], fill=TEAL, width=4)
        if reveal >= 1.0:
            for L, lab, anchor in ((man["games"], f"best of {man['games']}: {100 * curve[man['games']]:.1f}%", "lt"),
                                   (firsts[0.9], f"best of {firsts[0.9]}: {100 * curve[firsts[0.9]]:.0f}%", "rb"),
                                   (firsts[0.99], f"best of {firsts[0.99]}: {100 * curve[firsts[0.99]]:.0f}%", "rb")):
                x, y = cx_of(L), cy_of(curve[L])
                d.ellipse((x - 9, y - 9, x + 9, y + 9), fill=GOLD)
                dx, dy = (16, 6) if anchor == "lt" else (-16, -8)
                d.text((x + dx, y + dy), lab, font=self.font_tiny, fill=GOLD, anchor=anchor)
        # Game sevens readout, once the grid is full.
        if k >= self.n:
            g7 = int((self.meas["length"] == man["games"]).sum())
            g7w = int((self.meas["better_won"] & (self.meas["length"] == man["games"])).sum())
            d.text((BAR_X0, 1150), f"went to game {man['games']}: {g7:,} series", font=self.font_small, fill=TEXT, anchor="lm")
            d.text((BAR_X0, 1200), f"the better team won {g7w:,} of those = {100 * g7w / g7:.1f}%", font=self.font_small, fill=MUTED, anchor="lm")
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
    man = json.loads((ROOT / "projects/bestofseven/manifest.json").read_text())
    meas = measure(man)
    if "--measure-only" in sys.argv:
        return
    Renderer(man, meas).render(ROOT / "media/bestofseven/footage.mp4")


if __name__ == "__main__":
    main()
