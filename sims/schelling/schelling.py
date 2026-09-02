#!/usr/bin/env python3
"""Schelling segregation: two kinds of agents on a grid, each content when
at least a given share of its occupied neighbours are its own kind. Every
round, every discontented agent moves to a random empty cell. The sim
measures how alike the neighbourhoods end up, against how alike anyone
asked for.

usage: schelling.py [--measure-only] [--want SHARE]
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
EMPTY = (19, 24, 31)
KIND = (np.array((92, 200, 165), dtype=np.uint8), np.array((240, 176, 84), dtype=np.uint8))
TEXT = (216, 222, 230)
MUTED = (138, 148, 163)
ACCENT = (92, 200, 165)
WARM = (240, 176, 84)
CURVE = (216, 222, 230)

GRID_X0, GRID_Y0 = 90, 190
READOUT_Y = 1150
CHART_X0, CHART_X1 = 130, 1000
CHART_Y0, CHART_Y1 = 1480, 1810
PAYOFF_Y = 1875


def neighbour_counts(grid: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """For every cell: occupied neighbours, and neighbours of the same kind
    as the cell's own occupant (Moore neighbourhood, hard edges)."""
    occ = (grid >= 0).astype(np.int16)
    same = np.zeros(grid.shape, dtype=np.int16)
    total = np.zeros(grid.shape, dtype=np.int16)
    padded = np.pad(grid, 1, constant_values=-1)
    pocc = np.pad(occ, 1)
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if dy == 0 and dx == 0:
                continue
            shifted = padded[1 + dy:1 + dy + grid.shape[0], 1 + dx:1 + dx + grid.shape[1]]
            total += pocc[1 + dy:1 + dy + grid.shape[0], 1 + dx:1 + dx + grid.shape[1]]
            same += ((shifted == grid) & (grid >= 0)).astype(np.int16)
    return total, same


def alike_share(grid: np.ndarray) -> tuple[float, np.ndarray]:
    """Mean share of same-kind neighbours over agents with any neighbours,
    plus the per-cell share (nan where empty or isolated)."""
    total, same = neighbour_counts(grid)
    with np.errstate(divide="ignore", invalid="ignore"):
        share = np.where(total > 0, same / total, np.nan)
    share[grid < 0] = np.nan
    return float(np.nanmean(share)), share


def discontent(grid: np.ndarray, want: float) -> np.ndarray:
    total, same = neighbour_counts(grid)
    # An agent with no neighbours at all is content.
    return (grid >= 0) & (total > 0) & (same < want * total - 1e-9)


def simulate(man: dict, want: float, quiet: bool = False) -> dict:
    gw, gh = man["grid_w"], man["grid_h"]
    n = gw * gh
    rng = np.random.RandomState(man["seed"])
    cells = np.full(n, -1, dtype=np.int8)
    agents = int(round(n * (1 - man["empty_share"])))
    kinds = np.array([0, 1] * (agents // 2) + [0] * (agents % 2), dtype=np.int8)
    slots = rng.permutation(n)[:agents]
    cells[slots] = kinds
    grid = cells.reshape(gh, gw)
    history = [grid.copy()]
    rounds = []  # list of move lists: (from_index, to_index, kind)
    start_alike, _ = alike_share(grid)
    start_unhappy = int(discontent(grid, want).sum())
    alike_curve = [start_alike]
    unhappy_curve = [start_unhappy]
    total_moves = 0
    for r in range(man["max_rounds"]):
        unhappy = np.flatnonzero(discontent(grid, want).ravel())
        if len(unhappy) == 0:
            break
        rng.shuffle(unhappy)
        flat = grid.ravel()
        moves = []
        for src in unhappy:
            empties = np.flatnonzero(flat < 0)
            dst = int(empties[rng.randint(len(empties))])
            kind = int(flat[src])
            flat[dst] = kind
            flat[src] = -1
            moves.append((int(src), dst, kind))
        rounds.append(moves)
        total_moves += len(moves)
        a, _ = alike_share(grid)
        alike_curve.append(a)
        unhappy_curve.append(int(discontent(grid, want).sum()))
    final_alike, share = alike_share(grid)
    final_unhappy = int(discontent(grid, want).sum())
    out = {"grid0": history[0], "grid": grid, "rounds": rounds, "alike_curve": alike_curve,
           "unhappy_curve": unhappy_curve, "start_alike": start_alike,
           "final_alike": final_alike, "start_unhappy": start_unhappy,
           "final_unhappy": final_unhappy, "agents": agents, "total_moves": total_moves,
           "share": share}
    if not quiet:
        print(f"grid {gw}x{gh}, seed {man['seed']}, {agents} agents of two kinds, "
              f"{n - agents} empty cells, everyone wants at least {100 * want:.0f}% alike")
        print(f"start: neighbours alike {100 * start_alike:.1f}% on average, "
              f"{start_unhappy} of {agents} discontent ({100 * start_unhappy / agents:.1f}%)")
        print(f"settled after {len(rounds)} rounds and {total_moves} moves: "
              f"neighbours alike {100 * final_alike:.1f}% on average "
              f"({100 * final_alike:.0f}% to the nearest point), {final_unhappy} discontent")
        for r in (1, 2, 3, 5, 10, 15, 20):
            if r < len(alike_curve):
                print(f"  after round {r:2d}: alike {100 * alike_curve[r]:.1f}%, "
                      f"discontent {unhappy_curve[r]}")
        pct = np.nanpercentile(share, [10, 50, 90])
        print(f"final per-agent alike share: 10th pct {100 * pct[0]:.0f}%, median {100 * pct[1]:.0f}%, "
              f"90th pct {100 * pct[2]:.0f}%; agents with every neighbour alike: "
              f"{int(np.nansum(share >= 0.999))}")
    return out


def measure(man: dict) -> dict:
    out = simulate(man, man["want_alike"])
    print("same seed, other thresholds:")
    for want in (0.20, 0.25, 0.30, 0.35, 0.40, 0.50):
        o = simulate(man, want, quiet=True)
        print(f"  want {100 * want:.0f}% alike -> {100 * o['final_alike']:.1f}% alike after "
              f"{len(o['rounds'])} rounds, {o['total_moves']} moves, {o['final_unhappy']} left discontent")
    return out


class Renderer:
    def __init__(self, man: dict, meas: dict):
        self.man, self.meas = man, meas
        self.gw, self.gh = man["grid_w"], man["grid_h"]
        self.cell = man["cell_px"]
        self.fps = man["fps"]
        font = os.environ["SEED_ZERO_FONT"]
        self.font = ImageFont.truetype(font, 40)
        self.font_small = ImageFont.truetype(font, 32)
        self.flat = meas["grid0"].ravel().copy()
        self.applied = (0, 0)  # (round index, moves applied in it)
        self.rounds = meas["rounds"]
        self.alike_now = meas["alike_curve"][0]
        self.unhappy_now = meas["unhappy_curve"][0]

    def round_seconds(self, r: int) -> float:
        m = self.man
        early = m["round_seconds"]
        return early[r] if r < len(early) else m["later_round_seconds"]

    def settle_time(self) -> float:
        return self.man["first_round_at"] + sum(self.round_seconds(r) for r in range(len(self.rounds)))

    def progress_at(self, t: float) -> tuple[int, float]:
        """Round index and fraction of its moves applied at video time t."""
        clock = self.man["first_round_at"]
        if t < clock:
            return 0, 0.0
        for r in range(len(self.rounds)):
            span = self.round_seconds(r)
            if t < clock + span:
                return r, (t - clock) / span
            clock += span
        return len(self.rounds), 0.0

    def advance(self, r: int, frac: float) -> None:
        ar, ak = self.applied
        while ar < r:
            self.apply(ar, len(self.rounds[ar]), ak)
            ar, ak = ar + 1, 0
        if r < len(self.rounds):
            k = int(frac * len(self.rounds[r]))
            self.apply(r, k, ak)
            self.applied = (r, k)
        else:
            self.applied = (r, 0)

    def apply(self, r: int, upto: int, start: int) -> None:
        for src, dst, kind in self.rounds[r][start:upto]:
            self.flat[dst] = kind
            self.flat[src] = -1

    def frame_at(self, t: float) -> np.ndarray:
        man = self.man
        r, frac = self.progress_at(t)
        self.advance(r, frac)
        grid = self.flat.reshape(self.gh, self.gw)
        rgb = np.empty((self.gh, self.gw, 3), dtype=np.uint8)
        rgb[:] = EMPTY
        rgb[grid == 0] = KIND[0]
        rgb[grid == 1] = KIND[1]
        block = np.repeat(np.repeat(rgb, self.cell, 0), self.cell, 1)
        frame = np.zeros((H, W, 3), dtype=np.uint8)
        frame[:] = BG
        gy1, gx1 = GRID_Y0 + block.shape[0], GRID_X0 + block.shape[1]
        frame[GRID_Y0:gy1, GRID_X0:gx1] = block
        img = Image.fromarray(frame)
        d = ImageDraw.Draw(img)
        curve = self.meas["alike_curve"]
        unhappy = self.meas["unhappy_curve"]
        n_rounds_total = len(self.rounds)
        shown_round = min(r, len(self.rounds))
        # Readouts use the settled value of the last completed round.
        done_rounds = r if frac == 0.0 or r >= len(self.rounds) else r
        alike = curve[min(done_rounds, len(curve) - 1)]
        disc = unhappy[min(done_rounds, len(unhappy) - 1)]
        d.text((GRID_X0, READOUT_Y), f"round {shown_round}", font=self.font, fill=TEXT, anchor="lm")
        d.text((gx1, READOUT_Y), f"neighbours alike {100 * alike:4.1f}%", font=self.font,
               fill=WARM, anchor="rm")
        if r < n_rounds_total:
            disc = max(0, disc - self.applied[1])
        d.text((W / 2, READOUT_Y + 62),
               f"everyone wants {100 * man['want_alike']:.0f}% alike   |   "
               f"{disc:,} still want to move",
               font=self.font_small, fill=MUTED, anchor="mm")
        # Chart: alike share by round.
        d.rectangle((CHART_X0, CHART_Y0, CHART_X1, CHART_Y1), outline=(40, 48, 58), width=2)
        d.text((CHART_X0, CHART_Y0 - 28), "neighbours alike", font=self.font_small, fill=MUTED, anchor="lm")
        d.text((CHART_X1, CHART_Y1 + 26), "round", font=self.font_small, fill=MUTED, anchor="rm")
        n_rounds = len(self.rounds)

        def cx(k):
            return CHART_X0 + (CHART_X1 - CHART_X0) * k / max(1, n_rounds)

        def cy(v):
            return CHART_Y1 - (CHART_Y1 - CHART_Y0) * v

        want_y = cy(man["want_alike"])
        d.line((CHART_X0, want_y, CHART_X1, want_y), fill=ACCENT, width=2)
        d.text((CHART_X0 + 8, want_y - 20), f"asked for {100 * man['want_alike']:.0f}%",
               font=self.font_small, fill=ACCENT, anchor="lm")
        for v in (0.5, 0.75, 1.0):
            d.line((CHART_X0 - 8, cy(v), CHART_X0, cy(v)), fill=MUTED, width=2)
            d.text((CHART_X0 - 14, cy(v)), f"{int(100 * v)}%", font=self.font_small, fill=MUTED, anchor="rm")
        pts = [(cx(k), cy(curve[k])) for k in range(min(done_rounds, n_rounds) + 1)]
        if len(pts) > 1:
            d.line(pts, fill=WARM, width=4)
        elif pts:
            d.ellipse((pts[0][0] - 4, pts[0][1] - 4, pts[0][0] + 4, pts[0][1] + 4), fill=WARM)
        if r >= n_rounds:
            settle_t = self.settle_time()
            alpha = min(1.0, max(0.0, (t - settle_t) / 0.6))
            shade = tuple(int(c * alpha + BG[i] * (1 - alpha)) for i, c in enumerate(WARM))
            d.text((W / 2, PAYOFF_Y),
                   f"asked for {100 * man['want_alike']:.0f}% alike. "
                   f"got {100 * self.meas['final_alike']:.1f}%.",
                   font=self.font, fill=shade, anchor="mm")
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
            proc.stdin.write(self.frame_at(f / self.fps).tobytes())
            if f % 300 == 0:
                print(f"frame {f}/{total}", file=sys.stderr)
        proc.stdin.close()
        if proc.wait() != 0:
            raise RuntimeError("ffmpeg failed")
        print(f"footage: {out_path} ({total / self.fps:.2f}s at {self.fps} fps)")


def main() -> None:
    man = json.loads((ROOT / "projects/schelling/manifest.json").read_text())
    if "--want" in sys.argv:
        man["want_alike"] = float(sys.argv[sys.argv.index("--want") + 1])
    meas = measure(man)
    if "--measure-only" in sys.argv:
        return
    Renderer(man, meas).render(ROOT / "media/schelling/footage.mp4")


if __name__ == "__main__":
    main()
