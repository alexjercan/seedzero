#!/usr/bin/env python3
"""Random walk home: the same coin on a line and on a plane.

Ten thousand walkers start at home on a line and step left or right by one
unit each turn. Ten thousand walkers start at home on a plane and step
north, south, east or west by one unit each turn. Both groups take the
same number of steps from the same seed. The measurement is how many
walkers have been back home (at the origin) at least once by a given step,
and when the ones who made it got there for the first time.

Printed for each world: walkers home by each check step, the median first
return step of the walkers that made it, the latest first return, the
number still out at the end, and for the line the exact probability of no
return as a check. A third group on a cubic lattice is run as context and
never narrated.

usage: randomwalk.py [--measure-only]
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
TEXT = (216, 222, 230)
MUTED = (138, 148, 163)
GRIDLINE = (40, 48, 58)
HOME = (255, 255, 255)

# Layout: the caption band sits at caption_y = 0.49 (y 941..1017).
LINE_LABEL_Y, LINE_TOP, LINE_BASE, LINE_READ_Y = 150.0, 230, 860, 905.0
LINE_X0, LINE_PX = 30, 3           # 3 px per unit, positions -170..170
PLANE_LABEL_Y, PLANE_Y0, PLANE_READ_Y = 1055.0, 1085, 1810.0
PLANE_X0, PLANE_CELLS, PLANE_PX = 190, 233, 3   # 233 cells of 3 px = 699 px
PAYOFF_Y = 1868.0


def walk(man: dict, dims: int) -> dict:
    """Run every walker for all steps. Returns positions per step (for the
    render) and the first return step of each walker (0 = never)."""
    rng = np.random.RandomState(man["seed"])
    m, n = man["walkers"], man["steps"]
    pos = np.zeros((m, dims), dtype=np.int32)
    first = np.zeros(m, dtype=np.int32)
    keep = dims <= 2 and m <= 20000
    hist = np.zeros((n + 1, m, dims), dtype=np.int16) if keep else None
    home_by = np.zeros(n + 1, dtype=np.int32)
    for s in range(1, n + 1):
        axis = rng.randint(dims, size=m) if dims > 1 else np.zeros(m, dtype=np.int64)
        sign = rng.randint(2, size=m) * 2 - 1
        pos[np.arange(m), axis] += sign
        at_home = ~pos.any(axis=1)
        new = at_home & (first == 0)
        first[new] = s
        home_by[s] = int((first > 0).sum())
        if keep:
            hist[s] = pos
    return {"first": first, "home_by": home_by, "hist": hist}


def no_return_exact_1d(n: int) -> float:
    """P(simple walk on the line has not returned to 0 by step n) = C(2k, k) / 4^k
    with k = n // 2 (returns happen on even steps only)."""
    k = n // 2
    return math.comb(2 * k, k) / 4 ** k


def measure(man: dict) -> dict:
    m, n = man["walkers"], man["steps"]
    print(f"{m:,} walkers per world at seed {man['seed']}, {n:,} steps each, one unit per step")
    out = {}
    for name, dims in (("line", 1), ("plane", 2), ("space", 3)):
        r = walk(man, dims)
        out[name] = r
        first = r["first"]
        back = first[first > 0]
        print(f"{name} ({dims} dimension{'s' if dims > 1 else ''}):")
        for s in man["check_steps"]:
            hb = r["home_by"][s]
            extra = f"   exact P(not home) {no_return_exact_1d(s):.4f}" if dims == 1 else ""
            print(f"  by step {s:5,}: home at least once {hb:6,} of {m:,} = {100 * hb / m:5.2f}%; still out {m - hb:5,} = {100 * (m - hb) / m:5.2f}%{extra}")
        print(f"  of the {len(back):,} walkers that got home: median first return step {int(np.median(back))}, "
              f"mean {back.mean():.1f}, latest {int(back.max())}; home by step 2: {int((first == 2).sum()):,}")
        qs = [int(np.percentile(back, q)) for q in (50, 75, 90, 99)]
        print(f"  first-return percentiles 50/75/90/99: {qs}")
    # Independent check of the line result with ten times the walkers.
    chk = {"seed": man["check_seed"], "walkers": man["check_walkers"], "steps": n}
    c = walk(chk, 1)
    still = chk["walkers"] - c["home_by"][n]
    print(f"check, not narrated: {chk['walkers']:,} line walkers at seed {chk['seed']}: still out at step {n:,} "
          f"{still:,} = {100 * still / chk['walkers']:.2f}% against exact {100 * no_return_exact_1d(n):.2f}%")
    lh, ph = out["line"]["home_by"][n], out["plane"]["home_by"][n]
    print(f"at step {n:,}: line {lh:,} home, plane {ph:,} home; still out: line {m - lh:,}, plane {m - ph:,} "
          f"({(m - ph) / (m - lh):.1f}x as many)")
    return out


class Renderer:
    def __init__(self, man: dict, meas: dict):
        self.man, self.meas = man, meas
        self.fps = man["fps"]
        font = os.environ["SEED_ZERO_FONT"]
        self.font = ImageFont.truetype(font, 40)
        self.font_small = ImageFont.truetype(font, 32)
        self.font_tiny = ImageFont.truetype(font, 26)
        self.half = PLANE_CELLS // 2
        self.teal = np.array(TEAL, dtype=np.float32)
        self.gold = np.array(GOLD, dtype=np.float32)
        self.bg = np.array(BG, dtype=np.float32)

    def step_at(self, scene_t: float) -> int:
        """Piecewise-linear step clock from the manifest's step_keys, so each
        narrated step count is on screen when it is spoken."""
        keys = self.man["step_keys"]
        if scene_t <= keys[0][0]:
            return int(keys[0][1])
        for (t0, s0), (t1, s1) in zip(keys, keys[1:]):
            if scene_t <= t1:
                return int(s0 + (s1 - s0) * (scene_t - t0) / (t1 - t0))
        return int(keys[-1][1])

    def draw_line(self, frame: np.ndarray, s: int) -> None:
        r = self.meas["line"]
        pos = r["hist"][s][:, 0].astype(np.int64)
        home = (r["first"] > 0) & (r["first"] <= s)
        # bins of two positions so the parity comb does not show
        span = 170
        b = np.clip((pos + span) // 2, 0, span - 1)
        tot = np.bincount(b, minlength=span)
        hm = np.bincount(b[home], minlength=span)
        peak = max(1, int(tot.max()))
        height = LINE_BASE - LINE_TOP
        for i in range(span):
            if tot[i] == 0:
                continue
            x0 = LINE_X0 + i * 2 * LINE_PX
            x1 = x0 + 2 * LINE_PX - 1
            h_all = int(round(height * tot[i] / peak))
            h_home = int(round(height * hm[i] / peak))
            if h_all > 0:
                frame[LINE_BASE - h_all:LINE_BASE, x0:x1] = GOLD
            if h_home > 0:
                frame[LINE_BASE - h_home:LINE_BASE, x0:x1] = TEAL
        # baseline and home tick
        frame[LINE_BASE:LINE_BASE + 2, LINE_X0:LINE_X0 + span * 2 * LINE_PX] = GRIDLINE
        hx = LINE_X0 + (span // 2) * 2 * LINE_PX
        frame[LINE_BASE:LINE_BASE + 14, hx:hx + 2 * LINE_PX - 1] = HOME

    def draw_plane(self, frame: np.ndarray, s: int) -> None:
        r = self.meas["plane"]
        pos = r["hist"][s].astype(np.int64)
        home = (r["first"] > 0) & (r["first"] <= s)
        gx = pos[:, 0] + self.half
        gy = pos[:, 1] + self.half
        ok = (gx >= 0) & (gx < PLANE_CELLS) & (gy >= 0) & (gy < PLANE_CELLS)
        idx = gy[ok] * PLANE_CELLS + gx[ok]
        tot = np.bincount(idx, minlength=PLANE_CELLS ** 2).astype(np.float32)
        hm = np.bincount(idx[home[ok]], minlength=PLANE_CELLS ** 2).astype(np.float32)
        frac = np.where(tot > 0, hm / np.maximum(tot, 1), 0.0)[:, None]
        col = self.gold + (self.teal - self.gold) * frac
        cmax = max(1.0, float(tot.max()))
        inten = np.where(tot > 0, 0.45 + 0.55 * np.log1p(tot) / np.log1p(cmax), 0.0)[:, None]
        cells = self.bg + (col - self.bg) * inten
        img = cells.reshape(PLANE_CELLS, PLANE_CELLS, 3).astype(np.uint8)
        img = np.repeat(np.repeat(img, PLANE_PX, 0), PLANE_PX, 1)
        y0 = PLANE_Y0
        frame[y0:y0 + img.shape[0], PLANE_X0:PLANE_X0 + img.shape[1]] = img
        # frame the plane and mark home
        frame[y0 - 2:y0, PLANE_X0 - 2:PLANE_X0 + img.shape[1] + 2] = GRIDLINE
        frame[y0 + img.shape[0]:y0 + img.shape[0] + 2, PLANE_X0 - 2:PLANE_X0 + img.shape[1] + 2] = GRIDLINE
        frame[y0 - 2:y0 + img.shape[0] + 2, PLANE_X0 - 2:PLANE_X0] = GRIDLINE
        frame[y0 - 2:y0 + img.shape[0] + 2, PLANE_X0 + img.shape[1]:PLANE_X0 + img.shape[1] + 2] = GRIDLINE
        hx = PLANE_X0 + self.half * PLANE_PX
        hy = y0 + self.half * PLANE_PX
        frame[hy - 1:hy + PLANE_PX + 1, hx - 6:hx + PLANE_PX + 6] = HOME
        frame[hy - 6:hy + PLANE_PX + 6, hx - 1:hx + PLANE_PX + 1] = HOME

    def frame_at(self, f: int) -> np.ndarray:
        man = self.man
        scene_t = f / self.fps
        s = self.step_at(scene_t)
        frame = np.zeros((H, W, 3), dtype=np.uint8)
        frame[:, :] = BG
        self.draw_line(frame, s)
        self.draw_plane(frame, s)
        pil = Image.fromarray(frame)
        d = ImageDraw.Draw(pil)
        m = man["walkers"]
        for name, label, label_y, read_y in (("line", "the line", LINE_LABEL_Y, LINE_READ_Y),
                                             ("plane", "the plane", PLANE_LABEL_Y, PLANE_READ_Y)):
            hb = int(self.meas[name]["home_by"][s])
            d.text((LINE_X0 + 20, label_y), label, font=self.font, fill=TEXT, anchor="lm")
            d.text((W - LINE_X0 - 20, label_y), f"step {s:,}", font=self.font_small, fill=MUTED, anchor="rm")
            d.text((LINE_X0 + 20, read_y), f"been home: {hb:,} of {m:,}", font=self.font_small, fill=TEAL, anchor="lm")
            d.text((W - LINE_X0 - 20, read_y), f"still out: {m - hb:,}", font=self.font_small, fill=GOLD, anchor="rm")
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
    man = json.loads((ROOT / "projects/randomwalk/manifest.json").read_text())
    meas = measure(man)
    if "--measure-only" in sys.argv:
        return
    Renderer(man, meas).render(ROOT / "media/randomwalk/footage.mp4")


if __name__ == "__main__":
    main()
