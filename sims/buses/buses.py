#!/usr/bin/env python3
"""Bus wait: the same buses on tempo versus at random.

One bus stop, one week of 10,080 minutes. The top road runs 1,008 buses on
tempo, one every ten minutes. The bottom road runs the same 1,008 buses at
times drawn uniformly at random over the week from the seeded stream, so
both roads average one bus every ten minutes. Ten thousand passengers
arrive at uniformly random moments of the week, the same moments on both
roads. Each passenger waits for the next bus; the week repeats, so a
passenger after the last bus waits for the first bus of the next week.

Measured and printed for each road: the average wait, the median and the
longest wait, the share of passengers waiting more than one headway, the
average gap between the two buses around each passenger, and the average
gap between consecutive buses. The theory for a Poisson-like schedule says
the wait doubles (a random moment tends to fall in a long gap), and the
sim prints the exact expectations for the uniform model as a check.

usage: buses.py [--measure-only]
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
ROAD = (26, 32, 40)
WHITE = (255, 255, 255)

# Layout: two road panels, captions between them at caption_y 0.49 (y 941..1021).
PANEL = {"tempo": {"label_y": 150.0, "road_y": 235, "read_y": 405.0, "hist_y0": 560, "hist_y1": 770, "col": TEAL},
         "random": {"label_y": 1090.0, "road_y": 1175, "read_y": 1345.0, "hist_y0": 1500, "hist_y1": 1710, "col": GOLD}}
ROAD_X0, ROAD_X1, ROAD_H = 60, 1020, 110
STOP_X = 900
HIST_X0, HIST_X1, HIST_BIN, HIST_MAX_MIN = 150, 1020, 2.0, 70.0
PAYOFF_Y = 1868.0


def schedule(man: dict) -> dict:
    rng = np.random.RandomState(man["seed"])
    week, hw = man["week_min"], man["headway_min"]
    n_bus = int(round(week / hw))
    passengers = np.sort(rng.uniform(0.0, week, size=man["passengers"]))
    tempo = np.arange(1, n_bus + 1) * hw            # 10, 20, ..., 10080
    random = np.sort(rng.uniform(0.0, week, size=n_bus))
    return {"passengers": passengers, "tempo": tempo, "random": random, "n_bus": n_bus}


def waits(buses: np.ndarray, passengers: np.ndarray, week: float) -> dict:
    # Cyclic week: the schedule repeats, so the bus after the last one is
    # the first one plus a week, and the bus before the first one is the
    # last one minus a week.
    ext = np.concatenate([[buses[-1] - week], buses, [buses[0] + week]])
    idx = np.searchsorted(ext, passengers, side="right")   # next bus index in ext
    nxt = ext[idx]
    prv = ext[idx - 1]
    wait = nxt - passengers
    gap = nxt - prv
    board_bus = idx - 1                                    # index into buses, may be n (wrap)
    return {"wait": wait, "gap": gap, "next": nxt, "board": board_bus}


def measure(man: dict) -> dict:
    sch = schedule(man)
    week, hw = man["week_min"], man["headway_min"]
    n_bus, pas = sch["n_bus"], sch["passengers"]
    print(f"one stop, one week of {week:,.0f} minutes, {n_bus:,} buses per road, {len(pas):,} passengers at seed {man['seed']}")
    out = {"schedule": sch}
    for name in ("tempo", "random"):
        buses = sch[name]
        r = waits(buses, pas, week)
        out[name] = r
        gaps = np.diff(np.concatenate([buses, [buses[0] + week]]))
        w = r["wait"]
        print(f"{name}: {len(buses):,} buses, bus-to-bus gap mean {gaps.mean():.3f} min, median {np.median(gaps):.2f}, "
              f"longest {gaps.max():.2f}, shortest {gaps.min():.3f}")
        print(f"  passenger wait mean {w.mean():.3f} min, median {np.median(w):.2f}, longest {w.max():.2f}; "
              f"waited over {hw:.0f} min: {int((w > hw).sum()):,} = {100 * (w > hw).mean():.1f}%; "
              f"over {2 * hw:.0f} min: {int((w > 2 * hw).sum()):,} = {100 * (w > 2 * hw).mean():.1f}%; "
              f"under 1 min: {int((w < 1).sum()):,}")
        print(f"  gap around the passenger mean {r['gap'].mean():.3f} min (bus-to-bus mean {gaps.mean():.3f})")
        for day in (1, 2, 3):
            m = pas < day * 1440
            print(f"    first {day} day{'s' if day > 1 else ''}: {int(m.sum()):,} passengers, mean wait {w[m].mean():.3f} min")
        for mins in (120, 600, 3000):
            m = pas < mins
            print(f"    first {mins} min: {int(m.sum()):,} passengers, mean wait {w[m].mean():.3f} min")
    # Exact expectations for the uniform model: n points uniform on a circle
    # of length L; a random moment's wait has mean L / (n + 1) on tempo (L/n
    # gaps, uniform inside: half a gap = L/(2n)) and 2L/(2(n+1)) = L/(n+1) at
    # random (length-biased gap mean 2L/(n+1), half of it waited).
    print(f"exact: tempo wait {hw / 2:.3f} min, gap {hw:.3f}; random wait {week / (n_bus + 1):.3f} min, "
          f"gap around the passenger {2 * week / (n_bus + 1):.3f}, share waiting over {hw:.0f} min "
          f"{100 * (1 - hw / week) ** (n_bus):.1f}%")
    print(f"ratio of mean waits: {out['random']['wait'].mean() / out['tempo']['wait'].mean():.2f}x")
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
        self.keys = man["clock_keys"]
        sch = meas["schedule"]
        self.pas = sch["passengers"]
        self.cum = {name: np.concatenate([[0.0], np.cumsum(meas[name]["wait"])]) for name in ("tempo", "random")}
        bins = np.arange(0.0, HIST_MAX_MIN + HIST_BIN, HIST_BIN)
        self.hist = {name: np.histogram(np.minimum(meas[name]["wait"], HIST_MAX_MIN - 1e-9), bins=bins)[0] for name in ("tempo", "random")}
        self.hist_max = max(h.max() for h in self.hist.values())
        # Per passenger: the histogram bin of the wait and the boarding time,
        # so the histogram grows live as passengers board.
        nb = len(bins) - 1
        self.bin_idx = {name: np.minimum((meas[name]["wait"] / HIST_BIN).astype(int), nb - 1) for name in ("tempo", "random")}
        self.board_t = {name: self.pas + meas[name]["wait"] for name in ("tempo", "random")}

    def sim_time(self, scene_t: float) -> tuple[float, bool]:
        """Sim minutes since the start of the week and whether the week is
        over. After the week the same schedule replays slowly so the roads
        keep moving while the totals hold."""
        keys = self.keys
        if scene_t <= keys[0][0]:
            return keys[0][1], False
        for (t0, s0), (t1, s1) in zip(keys, keys[1:]):
            if scene_t <= t1:
                return s0 + (s1 - s0) * (scene_t - t0) / (t1 - t0), False
        return (scene_t - keys[-1][0]) * self.man["replay_rate"], True

    def frame_at(self, f: int) -> np.ndarray:
        man = self.man
        scene_t = f / self.fps
        now, done = self.sim_time(scene_t)
        week = man["week_min"]
        road_min = man["road_min"]
        px_per_min = (STOP_X - ROAD_X0) / road_min
        pil = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(pil)
        n_pas_total = len(self.pas)
        n_pas = n_pas_total if done else int(np.searchsorted(self.pas, now, side="right"))
        for name, label in (("tempo", "on tempo: one bus every 10 min"), ("random", "at random: same 1,008 buses")):
            p = PANEL[name]
            buses = self.meas["schedule"][name]
            col = p["col"]
            d.text((ROAD_X0, p["label_y"]), label, font=self.font, fill=col, anchor="lm")
            if name == "tempo":
                day = int(now // 1440)
                clock = f"day {day + 1}  {int((now % 1440) // 60):02d}:{int(now % 60):02d}" if not done else "replay"
                d.text((ROAD_X1, p["label_y"]), clock, font=self.font_tiny, fill=MUTED, anchor="rm")
            ry0, ry1 = p["road_y"], p["road_y"] + ROAD_H
            d.rectangle((ROAD_X0, ry0, ROAD_X1, ry1), fill=ROAD)
            d.line((ROAD_X0, (ry0 + ry1) / 2, ROAD_X1, (ry0 + ry1) / 2), fill=GRIDLINE, width=2)
            d.rectangle((STOP_X - 4, ry0 - 44, STOP_X + 4, ry1 + 8), fill=TEXT)
            d.text((STOP_X + 40, ry0 - 30), "stop", font=self.font_tiny, fill=MUTED, anchor="lm")
            # Buses drive left to right and reach the stop at their time.
            lo = np.searchsorted(buses, now - 2.0)
            hi = np.searchsorted(buses, now + road_min, side="right")
            n_passed = len(buses) if done else int(np.searchsorted(buses, now, side="right"))
            for b in buses[lo:hi]:
                x = STOP_X - (b - now) * px_per_min
                if x > ROAD_X1 + 60 or x < ROAD_X0 - 60:
                    continue
                d.rounded_rectangle((x - 54, ry0 + 20, x + 6, ry1 - 20), radius=8, fill=col)
                d.rectangle((x - 46, ry0 + 30, x - 2, ry0 + 48), fill=BG)
            # Passengers waiting now, queued left of the stop.
            r = self.meas[name]
            k = int(np.searchsorted(self.pas, now, side="right"))
            arrived = self.pas[:k]
            waiting = arrived[r["next"][:k] > now]
            n_wait = len(waiting)
            for i, a in enumerate(waiting[-60:]):
                qx = STOP_X - 22 - (i // 2) * 14
                qy = ry0 - 16 - (i % 2) * 14
                d.ellipse((qx - 5, qy - 5, qx + 5, qy + 5), fill=WHITE)
            avg = self.cum[name][n_pas] / n_pas if n_pas else 0.0
            d.text((ROAD_X0, p["read_y"]), f"buses {n_passed:,}   passengers {n_pas:,}" + (f"   waiting now {n_wait}" if not done else "   week done"),
                   font=self.font_small, fill=MUTED, anchor="lm")
            d.text((ROAD_X0, p["read_y"] + 62), "average wait", font=self.font_small, fill=TEXT, anchor="lm")
            d.text((ROAD_X1, p["read_y"] + 62), f"{avg:.1f} min" if n_pas else "", font=self.font_big, fill=col, anchor="rm")
            if scene_t >= man["gap_t"]:
                d.text((ROAD_X0, p["read_y"] + 118), "gap around a passenger", font=self.font_tiny, fill=MUTED, anchor="lm")
                d.text((ROAD_X1, p["read_y"] + 118), f"{r['gap'].mean():.1f} min", font=self.font_small, fill=col, anchor="rm")
            # Histogram of waits, growing live as passengers board.
            nb = len(self.hist[name])
            counts = self.hist[name] if done else np.bincount(self.bin_idx[name][self.board_t[name] <= now], minlength=nb)
            hy0, hy1 = p["hist_y0"], p["hist_y1"]
            d.rectangle((HIST_X0, hy0, HIST_X1, hy1), outline=GRIDLINE, width=2)
            bw = (HIST_X1 - HIST_X0) / nb
            for i, c in enumerate(counts):
                hgt = (hy1 - hy0 - 6) * c / self.hist_max
                if hgt >= 1:
                    d.rectangle((HIST_X0 + i * bw + 1, hy1 - hgt, HIST_X0 + (i + 1) * bw - 1, hy1 - 1), fill=col)
            for mins in (0, 10, 20, 30, 40, 50, 60):
                x = HIST_X0 + (HIST_X1 - HIST_X0) * mins / HIST_MAX_MIN
                d.text((x, hy1 + 20), f"{mins}", font=self.font_tiny, fill=MUTED, anchor="mm")
            d.text((HIST_X1, hy1 + 46), "minutes waited, 10,000 passengers", font=self.font_tiny, fill=MUTED, anchor="rm")
            if scene_t >= man["marker_t"]:
                x10 = HIST_X0 + (HIST_X1 - HIST_X0) * 10 / HIST_MAX_MIN
                d.line((x10, hy0, x10, hy1), fill=TEXT, width=2)
                over = int((r["wait"] > 10).sum())
                d.text((x10 + 12, hy0 + 20), f"over 10 min: {over:,}", font=self.font_small, fill=TEXT, anchor="lt")
            if scene_t >= man["longest_t"]:
                longest = float(r["wait"].max())
                xl = HIST_X0 + (HIST_X1 - HIST_X0) * min(longest, HIST_MAX_MIN) / HIST_MAX_MIN
                d.polygon(((xl, hy1 - 30), (xl - 10, hy1 - 50), (xl + 10, hy1 - 50)), fill=RED)
                d.text((min(xl, HIST_X1 - 10), hy1 - 60), f"longest {longest:.0f} min", font=self.font_tiny, fill=RED, anchor="rb" if xl > (HIST_X0 + HIST_X1) / 2 else "lb")
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
    man = json.loads((ROOT / "projects/buses/manifest.json").read_text())
    meas = measure(man)
    if "--measure-only" in sys.argv:
        return
    Renderer(man, meas).render(ROOT / "media/buses/footage.mp4")


if __name__ == "__main__":
    main()
