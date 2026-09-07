#!/usr/bin/env python3
"""Birthday paradox: your birthday versus any two.

Ten thousand rooms, birthdays uniform over the 365 days of a year (seed 0,
numpy RandomState). Both panels show the same rooms, the same people, the
same birthdays; one question changes. Top: how many rooms hold someone who
shares person one's birthday (yours). Bottom: how many rooms hold any two
people who share a birthday. People walk in one at a time, so both counts
grow person by person up to twenty three. The top room then keeps filling
to 253 people, the crowd it takes for a coin flip on your own birthday.

Measured and printed: both counts after every person, the exact
probabilities for a uniform year as a check, the number of pairs among
twenty three people, the count with 253 people in the room, the featured
room, and an independent run at another seed.

usage: birthday.py [--measure-only]
"""

from __future__ import annotations

import json
import math
import os
import subprocess
import sys
from collections import Counter
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
CELL = (30, 36, 44)
WHITE = (255, 255, 255)

DAYS = 365
MONTH_START = (0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334)
MONTH_LEN = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
MONTH_NAME = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")

# Layout: two panels, captions between them at caption_y 0.49 (y 941..1021).
# Each panel: a 31 x 12 calendar of days, then the first 100 rooms as a grid,
# the featured room's status and the count over all 10,000 rooms.
PANEL = {"you": {"y0": 130, "col": GOLD, "label": "someone shares YOUR birthday"},
         "any": {"y0": 1050, "col": TEAL, "label": "any two share a birthday"}}
CAL_X0, CAL_DY, CAL_PITCH = 90, 90, 30
DOOR_X = 30
GRID_X0, GRID_DY, GRID_PITCH = 60, 486, 26
STATUS_X = 360
SLOT_OFFSET = ((-6, -6), (6, 6), (6, -6), (-6, 6), (0, 0))
PAYOFF_Y = 1868.0


def month_of(day: int) -> int:
    return max(i for i, s in enumerate(MONTH_START) if s <= day)


def day_name(day: int) -> str:
    m = month_of(day)
    return f"{MONTH_NAME[m]} {day - MONTH_START[m] + 1}"


def first_matches(b: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Per room: the 1-based person whose entry creates the first match with
    person one, and the first match between any two people; K + 1 if none."""
    r, k = b.shape
    first_you = np.full(r, k + 1)
    first_any = np.full(r, k + 1)
    for j in range(1, k):
        you = b[:, 0] == b[:, j]
        anyp = (b[:, :j] == b[:, j : j + 1]).any(axis=1)
        first_you = np.where((first_you == k + 1) & you, j + 1, first_you)
        first_any = np.where((first_any == k + 1) & anyp, j + 1, first_any)
    return first_you, first_any


def exact(k: int) -> tuple[float, float]:
    p_you = 1.0 - ((DAYS - 1) / DAYS) ** (k - 1)
    p_any = 1.0 - math.prod((DAYS - j) / DAYS for j in range(k))
    return p_you, p_any


def measure(man: dict) -> dict:
    rng = np.random.RandomState(man["seed"])
    r, k, kmax = man["rooms"], man["people"], man["coin_people"]
    big = rng.randint(0, DAYS, size=(r, kmax))
    b = big[:, :k]
    first_you, first_any = first_matches(big)
    count_you = np.array([(first_you <= j).sum() for j in range(1, kmax + 1)])
    count_any = np.array([(first_any <= j).sum() for j in range(1, kmax + 1)])
    p_you, p_any = exact(k)
    print(f"{r:,} rooms, {DAYS}-day year, seed {man['seed']}; person one is you; the first {k} people count, "
          f"the top room then fills to {kmax}")
    for j in range(1, k + 1):
        ey, ea = exact(j)
        print(f"  {j:>2} people: shares yours {count_you[j - 1]:>5,} rooms ({100 * count_you[j - 1] / r:5.2f}%, exact {100 * ey:5.2f}%)   "
              f"any two share {count_any[j - 1]:>5,} rooms ({100 * count_any[j - 1] / r:5.2f}%, exact {100 * ea:5.2f}%)")
    cy, ca = int(count_you[k - 1]), int(count_any[k - 1])
    print(f"final at {k}: shares yours {cy:,} of {r:,} = {100 * cy / r:.2f}% (exact {100 * p_you:.2f}%, one standard deviation "
          f"{100 * math.sqrt(p_you * (1 - p_you) / r):.2f} points); any two {ca:,} = {100 * ca / r:.2f}% (exact {100 * p_any:.2f}%, "
          f"one standard deviation {100 * math.sqrt(p_any * (1 - p_any) / r):.2f} points); ratio {ca / cy:.2f}x")
    pairs = k * (k - 1) // 2
    print(f"comparisons: you against {k - 1} others; any two makes {pairs} pairs")
    grid = man["grid_rooms"]
    print(f"first {grid} rooms on screen at {k} people: shares yours {int((first_you[:grid] <= k).sum())}, any two {int((first_any[:grid] <= k).sum())}")
    for j in (30, 50, 100, 150, 200, kmax):
        print(f"  {j:>3} people: shares yours {count_you[j - 1]:>5,} rooms ({100 * count_you[j - 1] / r:5.2f}%, exact {100 * exact(j)[0]:5.2f}%); "
              f"any two {count_any[j - 1]:>6,} ({100 * count_any[j - 1] / r:6.2f}%)")
    print(f"the smallest crowd with an exact chance over 50% that someone shares yours: "
          f"{next(n for n in range(1, 2000) if exact(n)[0] > 0.5)} people; any two over 50% at {next(n for n in range(1, 400) if exact(n)[1] > 0.5)}")
    # Featured room: the first room where two strangers match and nobody matches you.
    feat = int(np.argmax((first_any <= k) & (first_you > k)))
    room = b[feat]
    pairs_in_room = [(i, j) for i in range(k) for j in range(i + 1, k) if room[i] == room[j]]
    print(f"featured room {feat + 1:,}: first pair match at person {first_any[feat]}, first match with you at person "
          f"{first_you[feat] if first_you[feat] <= kmax else 'none'}; pairs among {k}: "
          f"{[(i + 1, j + 1, day_name(int(room[i]))) for i, j in pairs_in_room]}; birthdays {[day_name(int(x)) for x in room]}")
    # Independent check at another seed.
    rc, sc = man["check_rooms"], man["check_seed"]
    bc = np.random.RandomState(sc).randint(0, DAYS, size=(rc, k))
    fy, fa = first_matches(bc)
    print(f"check: {rc:,} rooms of {k} at seed {sc}: shares yours {100 * (fy <= k).mean():.2f}%, any two {100 * (fa <= k).mean():.2f}% "
          f"(exact {100 * p_you:.2f}% and {100 * p_any:.2f}%)")
    return {"big": big, "first_you": first_you, "first_any": first_any, "count_you": count_you, "count_any": count_any,
            "feat": feat, "pairs": pairs_in_room}


class Renderer:
    def __init__(self, man: dict, meas: dict):
        self.man, self.meas = man, meas
        self.fps = man["fps"]
        font = os.environ["SEED_ZERO_FONT"]
        self.font = ImageFont.truetype(font, 40)
        self.font_small = ImageFont.truetype(font, 32)
        self.font_tiny = ImageFont.truetype(font, 26)
        self.font_big = ImageFont.truetype(font, 56)
        k, kmax = man["people"], man["coin_people"]
        self.k, self.kmax = k, kmax
        t_in = np.empty(kmax)
        t_in[:k] = man["people_start"] + np.arange(k) * man["people_step"]
        t_in[k:] = np.linspace(man["rush_t0"], man["rush_t1"], kmax - k)
        self.t_in = t_in
        self.walk = np.where(np.arange(kmax) < k, man["walk_s"], man["walk_rush_s"])
        self.t_done = t_in + self.walk
        self.room = meas["big"][meas["feat"]]
        seen: Counter = Counter()
        self.slot = []
        for day in self.room:
            self.slot.append(min(seen[int(day)], len(SLOT_OFFSET) - 1))
            seen[int(day)] += 1

    def cell(self, day: int, y0: int) -> tuple[float, float]:
        m = month_of(day)
        return CAL_X0 + (day - MONTH_START[m]) * CAL_PITCH, y0 + CAL_DY + m * CAL_PITCH

    def frame_at(self, f: int) -> np.ndarray:
        man, m = self.man, self.meas
        t = f / self.fps
        pil = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(pil)
        for name, p in PANEL.items():
            y0, col = p["y0"], p["col"]
            kcap = self.kmax if name == "you" else self.k
            n_arr = min(kcap, int(np.searchsorted(self.t_done, t, side="right")))
            d.text((60, y0 + 20), p["label"], font=self.font, fill=col, anchor="lm")
            d.text((W - 60, y0 + 62), f"people in the room: {n_arr}", font=self.font_tiny, fill=MUTED, anchor="rm")
            # Which days are matched under this panel's rule, among arrived people.
            days_in = Counter(int(self.room[j]) for j in range(n_arr))
            if name == "you":
                lit_days = {int(self.room[0])} if days_in[int(self.room[0])] >= 2 else set()
            else:
                lit_days = {day for day, c in days_in.items() if c >= 2}
            mix = tuple(int(0.45 * c + 0.55 * g) for c, g in zip(col, CELL))
            for mi in range(12):
                cy = y0 + CAL_DY + mi * CAL_PITCH + CAL_PITCH / 2
                d.text((CAL_X0 - 28, cy), MONTH_NAME[mi][0], font=self.font_tiny, fill=MUTED, anchor="mm")
                for dd in range(MONTH_LEN[mi]):
                    day = MONTH_START[mi] + dd
                    x, y = self.cell(day, y0)
                    if day in lit_days:
                        d.rectangle((x + 1, y + 1, x + CAL_PITCH - 1, y + CAL_PITCH - 1), fill=mix, outline=col, width=2)
                    else:
                        d.rectangle((x + 1, y + 1, x + CAL_PITCH - 1, y + CAL_PITCH - 1), fill=CELL)
            door_y = y0 + CAL_DY + 6 * CAL_PITCH
            d.rectangle((DOOR_X - 6, door_y - 40, DOOR_X + 6, door_y + 40), fill=GRIDLINE)
            # People walk from the door to their day.
            for j in range(kcap):
                if t < self.t_in[j]:
                    break
                u = min(1.0, (t - self.t_in[j]) / self.walk[j])
                x, y = self.cell(int(self.room[j]), y0)
                ox, oy = SLOT_OFFSET[self.slot[j]]
                tx, ty = x + CAL_PITCH / 2 + ox, y + CAL_PITCH / 2 + oy
                px, py = DOOR_X + (tx - DOOR_X) * u, door_y + (ty - door_y) * u
                is_you = j == 0
                rad = 9 if is_you else 7
                d.ellipse((px - rad, py - rad, px + rad, py + rad), fill=GOLD if is_you else TEXT)
            # The "you" label is drawn last, outlined, so later arrivals never cover it.
            if t >= self.t_in[0] + self.walk[0]:
                x, y = self.cell(int(self.room[0]), y0)
                d.text((x + CAL_PITCH / 2, y - 4), "you", font=self.font_tiny, fill=GOLD, anchor="mb",
                       stroke_width=3, stroke_fill=BG)
            # First grid_rooms rooms as cells, lit when the rule has a match.
            first = m["first_you"] if name == "you" else m["first_any"]
            g = man["grid_rooms"]
            side = int(math.isqrt(g))
            d.text((GRID_X0, y0 + GRID_DY - 16), f"first {g} rooms", font=self.font_tiny, fill=MUTED, anchor="lm")
            for idx in range(g):
                rx = GRID_X0 + (idx % side) * GRID_PITCH
                ry = y0 + GRID_DY + (idx // side) * GRID_PITCH
                lit = n_arr > 0 and first[idx] <= n_arr
                d.rectangle((rx, ry, rx + GRID_PITCH - 2, ry + GRID_PITCH - 2), fill=col if lit else CELL)
            d.text((STATUS_X, y0 + 500), f"room {m['feat'] + 1:,} of {man['rooms']:,}", font=self.font_tiny, fill=MUTED, anchor="lm")
            status = ""
            if name == "you":
                if n_arr >= self.k and t < man["coin_t"]:
                    status = "nobody shares yours" if not lit_days else "someone shares yours"
                if t >= man["coin_t"]:
                    status = f"a coin flip on yours: {self.kmax} people"
            else:
                done = sorted({day_name(int(self.room[i])) for i, j in m["pairs"] if n_arr > j})
                if done:
                    status = "both born " + done[0] if len(done) == 1 else " and ".join(done)
                if t >= man["pairs_t"]:
                    status = f"{self.k} people: {self.k * (self.k - 1) // 2} pairs"
            if status:
                d.text((STATUS_X, y0 + 546), status, font=self.font_tiny, fill=col, anchor="lm")
            counts = m["count_you"] if name == "you" else m["count_any"]
            count = int(counts[n_arr - 1]) if n_arr else 0
            d.text((W - 60, y0 + 620), "rooms with a match", font=self.font_small, fill=TEXT, anchor="rm")
            d.text((W - 60, y0 + 682), f"{count:,} of {man['rooms']:,}", font=self.font_big, fill=col, anchor="rm")
            d.text((W - 60, y0 + 736), f"{100 * count / man['rooms']:.1f}%", font=self.font_small, fill=col, anchor="rm")
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
    man = json.loads((ROOT / "projects/birthday/manifest.json").read_text())
    meas = measure(man)
    if "--measure-only" in sys.argv:
        return
    Renderer(man, meas).render(ROOT / "media/birthday/footage.mp4")


if __name__ == "__main__":
    main()
