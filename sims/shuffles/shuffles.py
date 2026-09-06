#!/usr/bin/env python3
"""Seven shuffles: how many riffle shuffles until a card guesser is blind?

Model: a 52-card deck starts in factory order. Each riffle shuffle is the
Gilbert-Shannon-Reeds model: cut at a Binomial(52, 1/2) point, then
interleave the two packets so that every interleaving is equally likely
(equivalently, drop cards with probability proportional to packet size).
Ten thousand decks are each shuffled `shuffles` times from one seeded
stream and the deck after every shuffle is kept, so the row for k shuffles
holds the same decks one shuffle further on.

The guesser knows the factory order and remembers every card it has seen.
Before each card is turned it names one card. Strategies measured:

- recency: the card after the one just seen (the lowest unseen card above
  it); if there is none, the lowest unseen card.
- longest: the unseen cards form runs of consecutive ranks; guess the
  first card of the longest run, ties to the run that continues the card
  just seen, then the lowest run.
- capped: like longest, but a run counts for at most 52 / 2^k cards, the
  typical packet size after k shuffles (the guesser is told k). For a
  random deck the cap is under one card, so every run ties and the rule
  falls back to recency.

Every strategy names one specific unseen card, so on a truly random deck
each guess is right with probability 1 / (cards left) and the expected
score is the harmonic number H_52 = 4.538. The sim also computes the
exact total variation distance to a random deck after k shuffles from the
Bayer-Diaconis formula with exact Eulerian numbers, as a check that the
guesser's edge dies where the theory says the deck becomes random.

usage: shuffles.py [--measure-only]
"""

from __future__ import annotations

import colorsys
import json
import math
import os
import subprocess
import sys
from fractions import Fraction
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
WHITE = (255, 255, 255)

# Layout. Eight rows of 52 cards; captions at caption_y 0.62 (y 1190..1270).
LANE_X0, CARD_W, CARD_GAP = 72, 16, 2
LANE_Y0, LANE_PITCH, BAR_H = 170, 118, 66
CHART_X0, CHART_X1, CHART_Y0, CHART_Y1 = 150, 1000, 1340, 1700
PAYOFF_Y = 1868.0


def riffle(deck: np.ndarray, rng: np.random.RandomState) -> np.ndarray:
    n = len(deck)
    cut = rng.binomial(n, 0.5)
    # Positions of the top packet in the shuffled deck, uniformly at random
    # among all C(n, cut) interleavings; the packets keep their own order.
    pos = np.sort(rng.choice(n, size=cut, replace=False))
    out = np.empty(n, dtype=deck.dtype)
    mask = np.zeros(n, dtype=bool)
    mask[pos] = True
    out[mask] = deck[:cut]
    out[~mask] = deck[cut:]
    return out


def guess_deck(deck: np.ndarray, strategy: str, k: int) -> np.ndarray:
    """Returns a boolean array: was guess j (before card j is turned) right."""
    n = len(deck)
    cap = n / 2 ** k if strategy == "capped" and k > 0 else n
    # Maximal runs of unseen consecutive ranks as [start, end] inclusive.
    runs = [[0, n - 1]]
    last = -1
    right = np.zeros(n, dtype=bool)
    for j in range(n):
        if strategy == "recency":
            guess = None
            for a, b in runs:
                if b > last:
                    guess = max(a, last + 1)
                    break
            if guess is None:
                guess = runs[0][0]
        else:
            best, guess = -1.0, None
            for a, b in runs:
                length = min(b - a + 1, cap)
                # Ties go to the run that continues the card just seen, then
                # to the lowest run (the list is sorted by rank).
                bonus = 0.5 if a == last + 1 else 0.0
                if length + bonus > best:
                    best, guess = length + bonus, a
        card = int(deck[j])
        right[j] = guess == card
        last = card
        # Remove the card from its run, splitting the run if needed.
        for i, (a, b) in enumerate(runs):
            if a <= card <= b:
                new = []
                if a <= card - 1:
                    new.append([a, card - 1])
                if card + 1 <= b:
                    new.append([card + 1, b])
                runs[i:i + 1] = new
                break
    return right


def eulerian(n: int) -> list[int]:
    """Eulerian numbers A(n, r) for r = 1..n rising sequences, exact."""
    row = [1]
    for m in range(2, n + 1):
        prev = row
        row = []
        for r in range(1, m + 1):
            a = prev[r - 1] * r if r - 1 < len(prev) else 0
            b = prev[r - 2] * (m - r + 1) if r >= 2 else 0
            row.append(a + b)
    return row


def total_variation(n: int, k: int, eul: list[int]) -> Fraction:
    """Bayer-Diaconis: after k GSR shuffles a deck with r rising sequences has
    probability C(2^k + n - r, n) / 2^(nk); the distance to uniform sums
    over r with the Eulerian count of such decks."""
    two = 2 ** k
    fact = math.factorial(n)
    total = Fraction(0)
    for r in range(1, n + 1):
        p = Fraction(math.comb(two + n - r, n), two ** n)
        total += eul[r - 1] * abs(p - Fraction(1, fact))
    return total / 2


def rising_sequences(deck: np.ndarray) -> int:
    pos = np.empty(len(deck), dtype=np.int64)
    pos[deck] = np.arange(len(deck))
    return 1 + int((pos[1:] < pos[:-1]).sum())


def simulate(man: dict) -> dict:
    rng = np.random.RandomState(man["seed"])
    n, d, s = man["cards"], man["decks"], man["shuffles"]
    decks = np.empty((d, s + 1, n), dtype=np.int16)
    for i in range(d):
        deck = np.arange(n, dtype=np.int16)
        decks[i, 0] = deck
        for k in range(1, s + 1):
            deck = riffle(deck, rng)
            decks[i, k] = deck
    random_decks = np.stack([rng.permutation(n).astype(np.int16) for _ in range(d)])
    return {"decks": decks, "random": random_decks}


def measure(man: dict) -> dict:
    n, d, s = man["cards"], man["decks"], man["shuffles"]
    sim = simulate(man)
    decks, random_decks = sim["decks"], sim["random"]
    h = sum(1.0 / m for m in range(1, n + 1))
    print(f"{d:,} decks of {n} cards, seed {man['seed']}, GSR riffle shuffles, {s} shuffles each plus {d:,} random decks")
    print(f"chance for any one-card guesser on a random deck: H_{n} = {h:.3f} right of {n}")
    eul = eulerian(n)
    assert sum(eul) == math.factorial(n)
    print("rising sequences (mean) and exact total variation distance from a random deck:")
    for k in range(1, s + 1):
        rs = np.mean([rising_sequences(decks[i, k]) for i in range(min(d, 2000))])
        tv = total_variation(n, k, eul)
        print(f"  {k:2d} shuffles: rising sequences {rs:5.2f}, distance {float(tv):.3f}")
    rs_rand = np.mean([rising_sequences(random_decks[i]) for i in range(min(d, 2000))])
    print(f"  random deck: rising sequences {rs_rand:5.2f} (exact mean {(n + 1) / 2})")
    out = {"h": h, "decks": decks, "random": random_decks, "scores": {}, "right": {}}
    for strategy in ("recency", "longest", "capped"):
        scores = np.zeros((d, s + 1), dtype=np.int16)
        rights = np.zeros((d, s + 1, n), dtype=bool)
        for k in range(0, s + 1):
            for i in range(d):
                r = guess_deck(decks[i, k], strategy, k)
                rights[i, k] = r
                scores[i, k] = r.sum()
        rand_scores = np.zeros(d, dtype=np.int16)
        rand_rights = np.zeros((d, n), dtype=bool)
        for i in range(d):
            r = guess_deck(random_decks[i], strategy, 99)
            rand_rights[i] = r
            rand_scores[i] = r.sum()
        out["scores"][strategy] = (scores, rand_scores)
        out["right"][strategy] = (rights, rand_rights)
        line = ", ".join(f"{k}: {scores[:, k].mean():.2f}" for k in range(0, s + 1))
        print(f"strategy {strategy}: mean right guesses by shuffle count {line}; random deck {rand_scores.mean():.2f}")
    strategy = man["strategy"]
    scores, rand_scores = out["scores"][strategy]
    print(f"chosen strategy: {strategy}")
    for k in range(0, s + 1):
        col = scores[:, k]
        print(f"  {k:2d} shuffles: mean {col.mean():.2f} right of {n}, median {int(np.median(col))}, "
              f"min {col.min()}, max {col.max()}, edge over chance {col.mean() - h:+.2f}, "
              f"decks scoring above 10: {100 * (col > 10).mean():.1f}%")
    print(f"  random deck: mean {rand_scores.mean():.2f}, median {int(np.median(rand_scores))}, min {rand_scores.min()}, "
          f"max {rand_scores.max()}, decks scoring above 10: {100 * (rand_scores > 10).mean():.1f}%")
    # The row on screen shows one lineage: the deck whose tallies over rows
    # 1..lanes sit closest to the row averages (first such deck).
    lanes = man["lanes"]
    dev = np.abs(scores[:, 1:lanes + 1] - scores[:, 1:lanes + 1].mean(axis=0)).sum(axis=1)
    shown = int(np.argmin(dev))
    rand_dev = np.abs(rand_scores - rand_scores.mean())
    shown_rand = int(np.argmin(rand_dev))
    print(f"deck shown on screen: lineage {shown} with tallies {scores[shown, 1:lanes + 1].tolist()} "
          f"(row means {[round(float(x), 2) for x in scores[:, 1:lanes + 1].mean(axis=0)]}); "
          f"random deck shown: {shown_rand} with tally {int(rand_scores[shown_rand])}")
    out.update({"shown": shown, "shown_rand": shown_rand, "strategy": strategy})
    return out


def rank_colour(rank: int, n: int, bright: float = 1.0) -> tuple[int, int, int]:
    r, g, b = colorsys.hsv_to_rgb(0.83 * rank / (n - 1), 0.92, 0.96 * bright)
    return int(255 * r), int(255 * g), int(255 * b)


class Renderer:
    def __init__(self, man: dict, meas: dict):
        self.man, self.meas = man, meas
        self.fps = man["fps"]
        font = os.environ["SEED_ZERO_FONT"]
        self.font = ImageFont.truetype(font, 40)
        self.font_small = ImageFont.truetype(font, 32)
        self.font_tiny = ImageFont.truetype(font, 26)
        n, lanes = man["cards"], man["lanes"]
        self.n = n
        decks = meas["decks"][meas["shown"]]
        rights, rand_rights = meas["right"][meas["strategy"]]
        scores, rand_scores = meas["scores"][meas["strategy"]]
        # Rows: k = 1..lanes from the shown lineage, then the random deck.
        self.rows = [(f"{k} shuffle" + ("s" if k > 1 else ""), decks[k], rights[meas["shown"], k],
                      decks[k - 1], scores[:, k]) for k in range(1, lanes + 1)]
        self.rows.append(("random deck", meas["random"][meas["shown_rand"]], rand_rights[meas["shown_rand"]],
                          decks[0], rand_scores))
        # Running batch averages: mean right guesses among the first j cards.
        self.running = [np.cumsum(rights[:, k, :], axis=1).mean(axis=0) for k in range(1, lanes + 1)]
        self.running.append(np.cumsum(rand_rights, axis=1).mean(axis=0))
        self.colours = [rank_colour(r, n) for r in range(n)]
        self.dim = [rank_colour(r, n, 0.55) for r in range(n)]

    def dealt_at(self, li: int, scene_t: float) -> float:
        """Cards turned in row li: each row deals its 52 cards over deal_len
        seconds and finishes at deal_end[li], when its number is spoken."""
        man = self.man
        end = man["deal_end"][li]
        frac = (scene_t - (end - man["deal_len"])) / man["deal_len"]
        return float(self.n) * max(0.0, min(1.0, frac))

    def frame_at(self, f: int) -> np.ndarray:
        man = self.man
        scene_t = f / self.fps
        n = self.n
        pil = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(pil)
        for li, (label, deck, right, prev, batch) in enumerate(self.rows):
            y = LANE_Y0 + li * LANE_PITCH
            dealt = self.dealt_at(li, scene_t)
            j_now = int(dealt)
            t_row = man["lane_t0"] + li * man["lane_dt"]
            if scene_t < t_row:
                continue
            anim = min(1.0, (scene_t - t_row) / man["lane_anim"])
            # Positions: where each rank sits in the previous deck and in this one.
            pos_new = np.empty(n)
            pos_new[deck] = np.arange(n)
            pos_old = np.empty(n)
            pos_old[prev] = np.arange(n)
            ease = 0.5 - 0.5 * math.cos(math.pi * anim)
            bar_y0, bar_y1 = y + 46, y + 46 + BAR_H
            d.text((LANE_X0, y + 14), label, font=self.font_small, fill=TEXT if anim >= 1 else MUTED, anchor="lm")
            if anim >= 1.0 and dealt > 0:
                tally = int(right[:j_now].sum())
                d.text((LANE_X0 + n * (CARD_W + CARD_GAP) - CARD_GAP, y + 14), f"{tally} right",
                       font=self.font_small, fill=GOLD, anchor="rm")
            order = np.argsort(pos_new) if anim >= 1 else np.arange(n)
            for rank in order:
                x = LANE_X0 + (pos_old[rank] * (1 - ease) + pos_new[rank] * ease) * (CARD_W + CARD_GAP)
                j = int(pos_new[rank])
                col = self.colours[rank] if (anim >= 1 and j < j_now) else self.dim[rank]
                if anim < 1:
                    col = self.colours[rank]
                d.rectangle((x, bar_y0, x + CARD_W - 1, bar_y1), fill=col)
                if anim >= 1 and j < j_now and right[j]:
                    d.rectangle((x, bar_y0 - 12, x + CARD_W - 1, bar_y0 - 6), fill=WHITE)
            if anim >= 1 and 0 < dealt < n:
                x = LANE_X0 + j_now * (CARD_W + CARD_GAP)
                d.rectangle((x - 2, bar_y0 - 3, x + CARD_W + 1, bar_y1 + 3), outline=WHITE, width=2)
        # Chart: running batch averages, one bar per row.
        rows = len(self.rows)
        d.text((CHART_X0, CHART_Y0 - 58), f"average right guesses, {man['decks']:,} decks per row", font=self.font_small, fill=MUTED, anchor="lm")
        d.rectangle((CHART_X0, CHART_Y0, CHART_X1, CHART_Y1), outline=GRIDLINE, width=2)
        vmax = 40.0
        def cy(v):
            return CHART_Y1 - (CHART_Y1 - CHART_Y0) * v / vmax
        for v in (10, 20, 30, 40):
            d.line((CHART_X0, cy(v), CHART_X1, cy(v)), fill=GRIDLINE, width=1)
            d.text((CHART_X0 - 12, cy(v)), f"{v}", font=self.font_tiny, fill=MUTED, anchor="rm")
        slot = (CHART_X1 - CHART_X0) / rows
        for li in range(rows):
            label = self.rows[li][0]
            t_row = man["lane_t0"] + li * man["lane_dt"] + man["lane_anim"]
            if scene_t < t_row:
                continue
            j_now = int(self.dealt_at(li, scene_t))
            val = float(self.running[li][j_now - 1]) if j_now > 0 else 0.0
            x0 = CHART_X0 + slot * li + slot * 0.18
            x1 = CHART_X0 + slot * (li + 1) - slot * 0.18
            col = TEAL if li < rows - 1 else GOLD
            if val > 0 and cy(val) < CHART_Y1 - 1:
                d.rectangle((x0, cy(val), x1, CHART_Y1 - 1), fill=col)
                d.text(((x0 + x1) / 2, cy(val) - 18), f"{val:.1f}", font=self.font_tiny, fill=TEXT, anchor="mm")
            short = label.replace(" shuffles", "").replace(" shuffle", "") if li < rows - 1 else "rnd"
            d.text(((x0 + x1) / 2, CHART_Y1 + 24), short, font=self.font_tiny, fill=MUTED, anchor="mm")
        d.text((CHART_X1, CHART_Y1 + 52), "shuffles", font=self.font_tiny, fill=MUTED, anchor="rm")
        # Chance line.
        h = self.meas["h"]
        d.line((CHART_X0, cy(h), CHART_X1, cy(h)), fill=GOLD, width=2)
        d.text((CHART_X1 - 10, CHART_Y0 + 22), f"gold line: chance {h:.1f}", font=self.font_tiny, fill=GOLD, anchor="rm")
        if scene_t >= man["edge_t"]:
            edges = ", ".join(f"{float(self.running[li][-1]) - h:.1f}" for li in range(rows - 1))
            d.text((W / 2, CHART_Y1 + 90), f"edge over chance: {edges}", font=self.font_tiny, fill=TEXT, anchor="mm")
            d.text((W / 2, CHART_Y1 + 122), "about half of it survives each riffle", font=self.font_tiny, fill=MUTED, anchor="mm")
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
    man = json.loads((ROOT / "projects/shuffles/manifest.json").read_text())
    meas = measure(man)
    if "--measure-only" in sys.argv:
        return
    Renderer(man, meas).render(ROOT / "media/shuffles/footage.mp4")


if __name__ == "__main__":
    main()
