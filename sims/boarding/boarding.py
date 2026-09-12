#!/usr/bin/env python3
"""Plane boarding: what is the fastest way to board a plane?

The same 150 passengers board the same 25-row, six-abreast plane three
times, in three orders. A passenger is a seat (row, letter), a bag-stowing
time drawn once from the seeded generator, and a walking pace shared by
everyone. The single aisle is a line of cells, one per row plus the door
cell; a passenger enters the door cell when it is free, walks one cell per
walk time when the next cell is free, stops in the aisle beside their row to
stow the bag, waits a fixed penalty for every seated neighbour they have to
climb over, then sits and frees the cell. Only the queue order differs:

- back to front: five zones of five rows, rear zone first, seeded random
  order inside a zone (the common airline call);
- random: one seeded shuffle of everyone;
- Steffen: window seats first, then middle, then aisle; inside each, rows
  25, 23, 21, ... on one side, then the same rows on the other side, then
  the even rows, so consecutive passengers stand two rows apart and stow
  bags at the same time.

Measured and printed: the boarding time of each order (the moment the last
passenger sits), how many passengers ever stood blocked behind someone
stowing, the peak number stowing at once, the peak number standing blocked,
the ratios, the same run at half the time step, a twenty-seed ensemble of
bag draws, and the on-screen text widths.

usage: boarding.py [--measure-only] [--frames t1,t2,...]
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
CORAL = (232, 96, 88)
TEXT = (216, 222, 230)
MUTED = (138, 148, 163)
WIRE = (70, 80, 94)
HULL = (30, 36, 44)

SEATS = "ABCDEF"  # A, F window; B, E middle; C, D aisle
PANEL_TOPS = (300.0, 655.0, 1010.0)
FUSE_X0, FUSE_X1 = 130.0, 1030.0
SEAT_X0, SEAT_X1 = 194.0, 990.0
LEGEND_Y = 1382.0
PAYOFF_Y = 1836.0

# Simulation states
QUEUE, WALK, STOW, SIT, SEATED = 0, 1, 2, 3, 4


def seat_kind(letter: str) -> str:
    return {"A": "window", "F": "window", "B": "middle", "E": "middle", "C": "aisle", "D": "aisle"}[letter]


def blockers(letter: str) -> list[str]:
    """Seats between the aisle and this seat."""
    return {"A": ["C", "B"], "B": ["C"], "C": [], "D": [], "E": ["D"], "F": ["D", "E"]}[letter]


def make_passengers(man: dict, seed: int) -> list[dict]:
    rng = np.random.RandomState(seed)
    rows = man["rows"]
    out = []
    lo, hi = man["bag_seconds"]
    for row in range(1, rows + 1):
        for letter in SEATS:
            # Bag times sit on a tenth-second grid so every time step that
            # divides 0.1 s gives the same boarding times.
            out.append({"row": row, "seat": letter, "bag": int(rng.randint(int(lo * 10), int(hi * 10) + 1)) / 10.0})
    return out


def order_back_to_front(pax: list[dict], man: dict, seed: int) -> list[int]:
    rng = np.random.RandomState(seed + 1)
    rows, zone = man["rows"], man["zone_rows"]
    order = []
    for z_top in range(rows, 0, -zone):
        ids = [i for i, p in enumerate(pax) if z_top - zone < p["row"] <= z_top]
        order.extend(int(i) for i in rng.permutation(ids))
    return order


def order_random(pax: list[dict], man: dict, seed: int) -> list[int]:
    rng = np.random.RandomState(seed + 2)
    return [int(i) for i in rng.permutation(len(pax))]


def order_steffen(pax: list[dict], man: dict, seed: int) -> list[int]:
    rows = man["rows"]
    order = []
    for letters in (("A", "F"), ("B", "E"), ("C", "D")):
        for parity in (rows % 2, 1 - rows % 2):  # rear row's parity first
            for letter in letters:
                for row in range(rows, 0, -1):
                    if row % 2 == parity:
                        order.append(next(i for i, p in enumerate(pax) if p["row"] == row and p["seat"] == letter))
    return order


ORDERS = {
    "back to front": order_back_to_front,
    "random": order_random,
    "window seats first": order_steffen,
}
COLOURS = {"back to front": CORAL, "random": GOLD, "window seats first": TEAL}


def simulate(pax: list[dict], order: list[int], man: dict, dt: float, record: bool) -> dict:
    """Time-stepped aisle model. Returns the boarding time, the mechanism
    counts and, when record is set, the state at every step for rendering."""
    rows = man["rows"]
    walk, penalty = int(round(man["walk_seconds"] / dt)), int(round(man["climb_seconds"] / dt))
    n = len(pax)
    state = np.full(n, QUEUE, dtype=np.int64)
    pos = np.full(n, -1, dtype=np.int64)  # aisle cell, 0 = door, r = beside row r
    timer = np.zeros(n, dtype=np.int64)  # steps left in the current action
    blocked = np.zeros(n, dtype=bool)
    ever_blocked = np.zeros(n, dtype=bool)
    seated = np.zeros((rows + 1, len(SEATS)), dtype=bool)
    cell = np.full(rows + 1, -1, dtype=np.int64)  # who stands in each aisle cell
    queue = list(order)
    t = 0.0
    frames = []
    peak_stow, peak_blocked, n_seated = 0, 0, 0
    max_steps = int(man["max_seconds"] / dt)
    for step in range(max_steps):
        # Process from the rear of the plane forward so a freed cell can be
        # taken by the passenger behind it in the same step.
        active = [i for i in np.argsort(-pos) if state[i] in (WALK, STOW, SIT)]
        stowing = 0
        n_blocked = 0
        for i in active:
            p = pax[i]
            if state[i] == WALK:
                timer[i] = max(0, timer[i] - 1)
                if timer[i] == 0:
                    nxt = pos[i] + 1
                    if cell[nxt] < 0:
                        cell[pos[i]] = -1
                        cell[nxt] = i
                        pos[i] = nxt
                        timer[i] = walk
                        blocked[i] = False
                        if pos[i] == p["row"]:
                            state[i] = STOW
                            timer[i] = int(round(p["bag"] / dt))
                            stowing += 1
                    else:
                        blocked[i] = True
                        ever_blocked[i] = True
                        n_blocked += 1
            elif state[i] == STOW:
                stowing += 1
                timer[i] -= 1
                if timer[i] == 0:
                    letter_i = SEATS.index(p["seat"])
                    in_way = sum(1 for b in blockers(p["seat"]) if seated[p["row"], SEATS.index(b)])
                    state[i] = SIT
                    timer[i] = penalty * in_way
                    if timer[i] == 0:
                        seated[p["row"], letter_i] = True
                        state[i] = SEATED
                        cell[pos[i]] = -1
                        n_seated += 1
            elif state[i] == SIT:
                timer[i] -= 1
                if timer[i] == 0:
                    seated[p["row"], SEATS.index(p["seat"])] = True
                    state[i] = SEATED
                    cell[pos[i]] = -1
                    n_seated += 1
        # Next in the queue steps through the door when the door cell is free.
        if queue and cell[0] < 0:
            i = queue.pop(0)
            state[i] = WALK
            pos[i] = 0
            cell[0] = i
            timer[i] = walk
        peak_stow = max(peak_stow, stowing)
        peak_blocked = max(peak_blocked, n_blocked)
        t = (step + 1) * dt
        if record:
            frames.append((state.copy(), pos.copy(), blocked.copy()))
        if n_seated == n:
            break
    else:
        raise RuntimeError("boarding did not finish inside max_seconds")
    return {
        "time": t,
        "avg_stow": sum(p["bag"] for p in pax) / t,
        "ever_blocked": int(ever_blocked.sum()),
        "peak_stow": peak_stow,
        "peak_blocked": peak_blocked,
        "frames": frames,
    }


def measure(man: dict) -> dict:
    seed, dt = man["seed"], man["dt"]
    pax = make_passengers(man, seed)
    bags = np.array([p["bag"] for p in pax])
    print(f"{len(pax)} passengers on {man['rows']} rows of six (A and F window, B and E middle, C and D aisle), "
          f"every seat taken; bag times drawn once per passenger, uniform {man['bag_seconds'][0]:g} to "
          f"{man['bag_seconds'][1]:g} s (mean {bags.mean():.2f} s, total {bags.sum():.0f} s); walking {man['walk_seconds']:g} s "
          f"per row; {man['climb_seconds']:g} s for every seated neighbour climbed over; time step {dt:g} s; seed {seed}")
    runs = {}
    for name, fn in ORDERS.items():
        order = fn(pax, man, seed)
        assert sorted(order) == list(range(len(pax)))
        r = simulate(pax, order, man, dt, record=True)
        runs[name] = r
        first = ", ".join(f"{pax[i]['row']}{pax[i]['seat']}" for i in order[:6])
        print(f"{name}: last passenger seated at {r['time']:.1f} s = {r['time'] / 60:.2f} min; {r['ever_blocked']} of "
              f"{len(pax)} passengers stood blocked in the aisle at some point; on average {r['avg_stow']:.2f} passengers "
              f"stowing bags at the same time, at most {r['peak_stow']}; at most {r['peak_blocked']} standing blocked at "
              f"once; first in line {first}")
    t_b2f, t_rand, t_ste = runs["back to front"]["time"], runs["random"]["time"], runs["window seats first"]["time"]
    print(f"ratios: back to front over window seats first {t_b2f / t_ste:.2f}x, random over window seats first "
          f"{t_rand / t_ste:.2f}x, back to front over random {t_b2f / t_rand:.2f}x")
    print(f"order slowest to fastest: " + ", ".join(f"{k} {v['time'] / 60:.1f} min" for k, v in sorted(runs.items(), key=lambda kv: -kv[1]["time"])))
    # Check: half the time step.
    halves = {}
    for name, fn in ORDERS.items():
        halves[name] = simulate(pax, fn(pax, man, seed), man, dt / 2, record=False)["time"]
    print("check, half the time step: " + ", ".join(f"{k} {v:.1f} s" for k, v in halves.items()))
    # Check: an ensemble of bag draws and shuffles.
    ens = {name: [] for name in ORDERS}
    for s in range(man["ensemble_seeds"]):
        px = make_passengers(man, s)
        for name, fn in ORDERS.items():
            ens[name].append(simulate(px, fn(px, man, s), man, dt, record=False)["time"])
    means = {k: float(np.mean(v)) for k, v in ens.items()}
    print(f"check, {man['ensemble_seeds']} seeds (0 to {man['ensemble_seeds'] - 1}): mean boarding time " +
          ", ".join(f"{k} {v / 60:.2f} min (min {min(ens[k]) / 60:.2f}, max {max(ens[k]) / 60:.2f})" for k, v in means.items()) +
          f"; mean ratio back to front over window seats first {means['back to front'] / means['window seats first']:.2f}x; "
          f"back to front slowest in {sum(1 for a, b in zip(ens['back to front'], ens['random']) if a > b)} of "
          f"{man['ensemble_seeds']} seeds, window seats first fastest in "
          f"{sum(1 for a, b in zip(ens['window seats first'], ens['random']) if a < b)}")
    playback = man["playback"]
    t0 = man["start_offset"]
    print(f"on screen at {playback:g}x from sim time {t0:g} s: the orders finish at " +
          ", ".join(f"{k} {(v['time'] - t0) / playback:.1f} s" for k, v in runs.items()))
    return {"pax": pax, "runs": runs, "t_b2f": t_b2f, "t_rand": t_rand, "t_ste": t_ste}


def fmt_clock(seconds: float) -> str:
    seconds = max(0.0, seconds)
    m, s = divmod(int(round(seconds)), 60)
    return f"{m}:{s:02d}"


class Renderer:
    def __init__(self, man: dict, meas: dict):
        self.man, self.meas = man, meas
        self.fps = man["fps"]
        font = os.environ["SEED_ZERO_FONT"]
        self.font = ImageFont.truetype(font, 40)
        self.font_small = ImageFont.truetype(font, 30)
        self.font_big = ImageFont.truetype(font, 56)
        self.font_title = ImageFont.truetype(font, 56)
        self.font_label = ImageFont.truetype(font, 44)
        self.first = None
        rows = man["rows"]
        self.pitch = (SEAT_X1 - SEAT_X0) / rows
        widths = {"overlay@34": (ImageFont.truetype(font, 34), man["overlay"])}
        for j, line in enumerate(man["title"].split("|")):
            widths[f"title line {j + 1}@56"] = (self.font_title, line)
        for name in ORDERS:
            widths[f"label {name}@44"] = (self.font_label, name)
        widths["clock@56"] = (self.font_big, "24:59")
        widths["subtitle@40"] = (self.font, man["subtitle"])
        widths["boarded@30"] = (self.font_small, "boarded")
        widths["legend@30"] = (self.font_small, "stowing a bag        waiting behind them")
        for j, line in enumerate(self.payoff_lines()):
            widths[f"payoff line {j + 1}@40"] = (self.font, line)
        print("text widths: " + ", ".join(f"{k} {f.getlength(s):.0f} px" for k, (f, s) in widths.items()))

    def payoff_lines(self) -> list[str]:
        m = self.man
        text = m["payoff_text"].format(ste=fmt_clock(self.meas["t_ste"]), b2f=fmt_clock(self.meas["t_b2f"]), rand=fmt_clock(self.meas["t_rand"]))
        return [s.strip() for s in text.split("|")]

    @staticmethod
    def blend(col: tuple, alpha: float) -> tuple:
        return tuple(int(c * alpha + BG[j] * (1 - alpha)) for j, c in enumerate(col))

    def seat_xy(self, row: int, letter: str) -> tuple[float, float, float]:
        """Centre of a seat cell and the aisle y for the current panel base."""
        x = SEAT_X0 + (row - 0.5) * self.pitch
        k = SEATS.index(letter)
        dy = {0: -90.0, 1: -54.0, 2: -18.0, 3: 18.0, 4: 54.0, 5: 90.0}[k]
        return x, dy, 0.0

    def draw_panel(self, d: ImageDraw.ImageDraw, name: str, top: float, sim_t: float, title_on: bool) -> None:
        man, m = self.man, self.meas
        run = m["runs"][name]
        col = COLOURS[name]
        pax = m["pax"]
        rows = man["rows"]
        dt = man["dt"]
        k = min(len(run["frames"]) - 1, max(0, int(sim_t / dt) - 1))
        state, pos, blocked = run["frames"][k]
        done = sim_t >= run["time"]
        cy = top + 70.0 + 130.0  # aisle centre line
        # Fuselage: rounded hull with a nose at the door end.
        d.rounded_rectangle((FUSE_X0, cy - 128, FUSE_X1, cy + 128), radius=44, fill=HULL, outline=WIRE, width=3)
        d.rectangle((FUSE_X0 + 10, cy - 22, FUSE_X0 + 54, cy + 22), fill=WIRE)  # door cell
        # Seats.
        seated_count = 0
        for i, p in enumerate(pax):
            x, dy, _ = self.seat_xy(p["row"], p["seat"])
            y = cy + dy + (14 if dy > 0 else -14)  # push rows off the aisle band
            if dy < 0:
                y = cy + dy - 14
            else:
                y = cy + dy + 14
            half = self.pitch / 2 - 3
            if state[i] == SEATED:
                d.rectangle((x - half, y - 14, x + half, y + 14), fill=self.blend(col, 0.75))
                seated_count += 1
            else:
                d.rectangle((x - half, y - 14, x + half, y + 14), outline=WIRE, width=2)
        # Aisle: walkers, blocked walkers and stowers.
        for i, p in enumerate(pax):
            if state[i] in (WALK, STOW, SIT):
                x = FUSE_X0 + 32.0 if pos[i] == 0 else SEAT_X0 + (pos[i] - 0.5) * self.pitch
                if state[i] in (STOW, SIT):
                    d.ellipse((x - 15, cy - 15, x + 15, cy + 15), outline=col, width=3)
                    d.ellipse((x - 7, cy - 7, x + 7, cy + 7), fill=col)
                elif blocked[i]:
                    d.ellipse((x - 10, cy - 10, x + 10, cy + 10), fill=TEXT)
                else:
                    d.ellipse((x - 10, cy - 10, x + 10, cy + 10), fill=col)
        # Label line: name, seated count, clock.
        d.text((FUSE_X0, top + 30), name, font=self.font_label, fill=col, anchor="lm")
        clock = run["time"] if done else sim_t
        d.text((FUSE_X1, top + 30), fmt_clock(clock), font=self.font_big, fill=col if done else TEXT, anchor="rm")
        if done:
            d.text((FUSE_X1 - 200, top + 34), "boarded", font=self.font_small, fill=col, anchor="rm")

    def live_frame(self, f: int) -> Image.Image:
        man = self.man
        t = f / self.fps
        sim_t = man["start_offset"] + t * man["playback"]
        img = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(img)
        title_on = t < man["title_until"]
        for name, top in zip(ORDERS, PANEL_TOPS):
            self.draw_panel(d, name, top, sim_t, title_on)
        if title_on:
            alpha = 1.0 if t < man["title_until"] - 0.4 else (man["title_until"] - t) / 0.4
            for j, line in enumerate(man["title"].split("|")):
                d.text((W / 2, 176 + j * 62), line, font=self.font_title, fill=self.blend(TEXT, alpha), anchor="mm")
        else:
            d.text((W / 2, 205), man["subtitle"], font=self.font, fill=MUTED, anchor="mm")
        # Legend for the aisle symbols.
        lx = 160
        d.ellipse((lx - 15, LEGEND_Y - 15, lx + 15, LEGEND_Y + 15), outline=TEXT, width=3)
        d.ellipse((lx - 7, LEGEND_Y - 7, lx + 7, LEGEND_Y + 7), fill=TEXT)
        d.text((lx + 30, LEGEND_Y), "stowing a bag", font=self.font_small, fill=MUTED, anchor="lm")
        lx = 600
        d.ellipse((lx - 10, LEGEND_Y - 10, lx + 10, LEGEND_Y + 10), fill=TEXT)
        d.text((lx + 30, LEGEND_Y), "waiting behind them", font=self.font_small, fill=MUTED, anchor="lm")
        if t >= man["payoff_t"]:
            alpha = min(1.0, (t - man["payoff_t"]) / man["payoff_hold"])
            for j, line in enumerate(self.payoff_lines()):
                d.text((W / 2, PAYOFF_Y - 32 + j * 64), line, font=self.font, fill=self.blend(GOLD, alpha), anchor="mm")
        return img

    def frame_at(self, f: int) -> np.ndarray:
        man = self.man
        total = int(round(man["scene_duration"] * self.fps))
        live = np.asarray(self.live_frame(f), dtype=np.float32)
        fade_frames = int(round(man["loop_fade"] * self.fps))
        if f >= total - fade_frames:
            if self.first is None:
                self.first = np.asarray(self.live_frame(0), dtype=np.float32)
            a = (f - (total - fade_frames) + 1) / fade_frames
            live = live * (1 - a) + self.first * a
        return live.astype(np.uint8)

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
    man = json.loads((ROOT / "projects/boarding/manifest.json").read_text())
    meas = measure(man)
    if "--measure-only" in sys.argv:
        return
    if "--frames" in sys.argv:
        times = [float(v) for v in sys.argv[sys.argv.index("--frames") + 1].split(",")]
        r = Renderer(man, meas)
        (ROOT / "media/boarding").mkdir(parents=True, exist_ok=True)
        for tv in times:
            Image.fromarray(r.frame_at(int(round(tv * man["fps"])))).save(ROOT / f"media/boarding/smoke-{tv}.png")
        print("smoke frames: " + ", ".join(f"{tv}" for tv in times))
        return
    Renderer(man, meas).render(ROOT / "media/boarding/footage.mp4")


if __name__ == "__main__":
    main()
