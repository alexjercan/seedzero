#!/usr/bin/env python3
"""Parking-lot probing: 950 cars into 1,000 spaces. How far does the last car go?

One long row of 1,000 spaces, drawn as 50 columns by 20 rows so the linear
order reads row by row (space 999 wraps to space 0). 950 cars arrive one at
a time; car i wants one preferred spot p_i drawn uniformly from the seeded
generator, and the same p_i sequence feeds both lots. Top lot, roll forward
(linear probing): a blocked car drives forward one space at a time until it
finds a free one. Bottom lot, fresh random spot (random probing): a blocked
car draws a new random spot from a second seeded stream and tries there,
again and again, until it finds a free one. A car's "spots passed" is the
number of taken spots it drove past or tried before it parked (probes minus
one). Deterministic: two streams spawned from one SeedSequence(seed), no
wall clock, no network.

Measured and printed: the spots passed per car, the average and maximum over
each block of fifty cars and over cars 901 to 950 (the lot 90 to 95 percent
full), the closed forms beside them (linear probing expects
(1 + 1/(1 - a)^2) / 2 probes at load a, random probing 1 / (1 - a)), the
longest run of consecutive taken spots at 900 and at 950 cars, the last car
in each lot, checks over seeds 1 to 5, a 100,000-space lot at the same loads,
and the on-screen text widths.

usage: parking.py [--measure-only] [--frames t1,t2,...]
"""

from __future__ import annotations

import json
import math
import multiprocessing
import os
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor
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
WHITE = (236, 240, 244)
FREE_FILL = (20, 24, 30)
FREE_EDGE = (52, 58, 70)

# Layout: overlay at y 96..130 (compose), title rows at y 190/252 for the
# first seconds, two panels stacked at y 300 (roll forward) and 860 (fresh
# random spot), each with three text rows (label and the running average of
# the last fifty cars; the rule and the longest full run; cars parked and the
# current car's spots passed) and a 50 x 20 grid of 1,000 spaces
# at a 20 px pitch from 130 px below the panel top (grid 1000 x 400 px, x 40
# to 1040); captions at caption_y 0.75 (y 1440..1520), payoff card from
# y 1592.
COLS, ROWS, PITCH, CELL = 50, 20, 20, 16
GRID_X0 = 40
GRID_DY = 130
GRID_W, GRID_H = COLS * PITCH, ROWS * PITCH
PAYOFF_Y = 1592.0
PANELS = [
    {"name": "linear", "label": "roll forward", "sub": "blocked? drive on to the next free spot",
     "colour": GOLD, "top": 300},
    {"name": "random", "label": "fresh random spot", "sub": "blocked? try a fresh random spot",
     "colour": CORAL, "top": 860},
]


def blend(col, a, base=BG):
    return tuple(int(round(c * a + b * (1 - a))) for c, b in zip(col, base))


def cf_linear(a: float) -> float:
    """Expected probes to insert with linear probing at load a (Knuth)."""
    return 0.5 * (1.0 + 1.0 / (1.0 - a) ** 2)


def cf_random(a: float) -> float:
    """Expected tries to insert with random probing at load a."""
    return 1.0 / (1.0 - a)


def cf_block(fn, n_spaces: int, i0: int, i1: int) -> float:
    """Closed form averaged over cars i0..i1-1 (0-based), car i arriving at load i / n."""
    return float(np.mean([fn(i / n_spaces) for i in range(i0, i1)]))


def longest_run(taken: np.ndarray) -> int:
    """Longest run of consecutive taken spots around the circular lot."""
    n = taken.size
    if taken.all():
        return n
    if not taken.any():
        return 0
    first_free = int(np.flatnonzero(~taken)[0])
    rolled = np.roll(taken, -first_free)
    x = np.concatenate(([0], rolled.astype(np.int8), [0]))
    d = np.diff(x)
    starts = np.flatnonzero(d == 1)
    ends = np.flatnonzero(d == -1)
    return int((ends - starts).max())


def simulate(n_spaces: int, n_cars: int, seed: int, paths: bool = False, runs: bool = False,
             run_marks: tuple[int, ...] = ()) -> dict:
    """Park n_cars cars in a lot of n_spaces by both rules; the same preferred spots feed both."""
    ss = np.random.SeedSequence(seed)
    pref_rng, retry_rng = (np.random.default_rng(s) for s in ss.spawn(2))
    pref = pref_rng.integers(0, n_spaces, size=n_cars)
    out = {"pref": pref, "n_spaces": n_spaces, "n_cars": n_cars, "seed": seed}
    for rule in ("linear", "random"):
        taken = bytearray(n_spaces)
        passed = np.zeros(n_cars, dtype=np.int64)
        park = np.zeros(n_cars, dtype=np.int64)
        path_list: list[np.ndarray] = []
        run_after = np.zeros(n_cars, dtype=np.int64) if runs else None
        marks: dict[int, int] = {}
        taken_np = np.zeros(n_spaces, dtype=bool)
        for i in range(n_cars):
            s = int(pref[i])
            path = [s]
            if rule == "linear":
                while taken[s]:
                    s += 1
                    if s == n_spaces:
                        s = 0
                    path.append(s)
            else:
                while taken[s]:
                    s = int(retry_rng.integers(0, n_spaces))
                    path.append(s)
            taken[s] = 1
            passed[i] = len(path) - 1
            park[i] = s
            if paths:
                path_list.append(np.array(path, dtype=np.int64))
            if runs or (i + 1) in run_marks:
                taken_np[s] = True
                if runs:
                    run_after[i] = longest_run(taken_np)
                if (i + 1) in run_marks:
                    marks[i + 1] = longest_run(taken_np)
            elif run_marks:
                taken_np[s] = True
        out[rule] = {"passed": passed, "park": park, "paths": path_list if paths else None,
                     "run_after": run_after, "run_marks": marks,
                     "taken": np.frombuffer(bytes(taken), dtype=np.uint8).astype(bool)}
    return out


def measure(man: dict) -> dict:
    n, cars, seed = man["n_spaces"], man["n_cars"], man["seed"]
    block = man["block"]
    print(f"setup: one row of {n:,} spaces drawn as {COLS} columns by {ROWS} rows (space {n - 1} wraps to space 0); "
          f"{cars} cars arrive one at a time; car i wants one preferred spot drawn uniformly from the seeded generator "
          f"(numpy default_rng, SeedSequence({seed}) spawned into a preferred-spot stream and a retry stream), and the same "
          f"preferred spots feed both lots; top lot, roll forward: a blocked car drives forward one space at a time to "
          f"the next free spot (linear probing); bottom lot, fresh random spot: a blocked car draws a new random spot "
          f"from the retry stream and tries there until it finds a free one (random probing, a retry may hit the same "
          f"taken spot twice); spots passed = taken spots driven past or tried before parking = probes minus one; "
          f"seed {seed}")
    a90, a95 = 900 / n, 950 / n
    print(f"closed forms: linear probing expects (1 + 1/(1 - a)^2) / 2 probes at load a: {cf_linear(a90):.1f} at "
          f"{a90:.2f} and {cf_linear(a95):.1f} at {a95:.2f} ({cf_linear(a90) - 1:.1f} and {cf_linear(a95) - 1:.1f} spots "
          f"passed); random probing expects 1 / (1 - a) tries: {cf_random(a90):.1f} at {a90:.2f} and {cf_random(a95):.1f} "
          f"at {a95:.2f} ({cf_random(a90) - 1:.1f} and {cf_random(a95) - 1:.1f} spots passed); car {cars} arrives at "
          f"load {(cars - 1) / n:.3f}: {cf_linear((cars - 1) / n) - 1:.1f} and {cf_random((cars - 1) / n) - 1:.1f} "
          f"spots passed expected; averaged over cars {cars - block + 1} to {cars} (loads {(cars - block) / n:.3f} to "
          f"{(cars - 1) / n:.3f}): {cf_block(cf_linear, n, cars - block, cars) - 1:.1f} and "
          f"{cf_block(cf_random, n, cars - block, cars) - 1:.1f} spots passed")
    run = simulate(n, cars, seed, paths=True, runs=True)
    lin, rnd = run["linear"], run["random"]
    rows = []
    for b in range(cars // block):
        i0, i1 = b * block, (b + 1) * block
        rows.append(f"cars {i0 + 1}-{i1} (load {i0 / n:.2f}-{(i1 - 1) / n:.3f}): roll forward avg "
                    f"{lin['passed'][i0:i1].mean():.1f} (closed form {cf_block(cf_linear, n, i0, i1) - 1:.1f}) max "
                    f"{lin['passed'][i0:i1].max()}, fresh random spot avg {rnd['passed'][i0:i1].mean():.1f} (closed form "
                    f"{cf_block(cf_random, n, i0, i1) - 1:.1f}) max {rnd['passed'][i0:i1].max()}")
    print("blocks of fifty cars, spots passed: " + "; ".join(rows))
    i0, i1 = cars - block, cars
    print(f"cars {i0 + 1} to {i1} (the lot {100 * i0 / n:.0f} to {100 * i1 / n:.0f} percent full): roll forward avg "
          f"{lin['passed'][i0:i1].mean():.1f} spots passed (closed form {cf_block(cf_linear, n, i0, i1) - 1:.1f}), max "
          f"{lin['passed'][i0:i1].max()} (car {i0 + 1 + int(lin['passed'][i0:i1].argmax())}), median "
          f"{np.median(lin['passed'][i0:i1]):.0f}; fresh random spot avg {rnd['passed'][i0:i1].mean():.1f} (closed form "
          f"{cf_block(cf_random, n, i0, i1) - 1:.1f}), max {rnd['passed'][i0:i1].max()} (car "
          f"{i0 + 1 + int(rnd['passed'][i0:i1].argmax())}), median {np.median(rnd['passed'][i0:i1]):.0f}; ratio of the "
          f"averages {lin['passed'][i0:i1].mean() / rnd['passed'][i0:i1].mean():.1f}; rounded for the card and the "
          f"narration: {int(round(float(lin['passed'][i0:i1].mean())))} and {int(round(float(rnd['passed'][i0:i1].mean())))} "
          f"spots per car; the running average over the last {block} parked cars at 900 cars: "
          f"{lin['passed'][i0 - block:i0].mean():.1f} and {rnd['passed'][i0 - block:i0].mean():.1f}")
    print(f"all {cars} cars: roll forward avg {lin['passed'].mean():.2f} spots passed, total {lin['passed'].sum():,}, "
          f"{int((lin['passed'] == 0).sum())} cars parked at their preferred spot, first car past 100 spots: car "
          f"{int(np.argmax(lin['passed'] >= 100)) + 1 if (lin['passed'] >= 100).any() else 0}; fresh random spot avg "
          f"{rnd['passed'].mean():.2f}, total {rnd['passed'].sum():,}, {int((rnd['passed'] == 0).sum())} cars at their "
          f"preferred spot, max over all cars {rnd['passed'].max()} (car {int(rnd['passed'].argmax()) + 1})")
    print(f"longest run of consecutive taken spots: at 900 cars roll forward {lin['run_after'][899]}, fresh random spot "
          f"{rnd['run_after'][899]}; at 950 cars roll forward {lin['run_after'][949]}, fresh random spot "
          f"{rnd['run_after'][949]}; roll forward first run over 100 after car "
          f"{int(np.argmax(lin['run_after'] >= 100)) + 1 if (lin['run_after'] >= 100).any() else 0}, over 200 after car "
          f"{int(np.argmax(lin['run_after'] >= 200)) + 1 if (lin['run_after'] >= 200).any() else 0}")
    last = cars - 1
    lp = lin["paths"][last]
    rp = rnd["paths"][last]
    print(f"last car (car {cars}, preferred spot {int(run['pref'][last])}, load {last / n:.3f}): roll forward drove past "
          f"{lin['passed'][last]} spots, from spot {int(lp[0])} to spot {int(lp[-1])}"
          f"{' (wrapping past space ' + str(n - 1) + ')' if lin['passed'][last] > 0 and int(lp[-1]) < int(lp[0]) else ''}; "
          f"fresh random spot tried {rnd['passed'][last]} taken spots ({', '.join(str(int(s)) for s in rp[:-1])}) and "
          f"parked at spot {int(rp[-1])}; the fifty cars before it: roll forward "
          f"{', '.join(str(int(v)) for v in lin['passed'][i0:i1])}; fresh random spot "
          f"{', '.join(str(int(v)) for v in rnd['passed'][i0:i1])}")
    # Checks: other seeds, and a big lot at the same loads.
    lines = []
    for s in range(1, man["check_seeds"] + 1):
        r = simulate(n, cars, s, run_marks=(900, 950))
        L, R = r["linear"], r["random"]
        lines.append(f"seed {s}: cars {i0 + 1}-{i1} avg {L['passed'][i0:i1].mean():.1f} / {R['passed'][i0:i1].mean():.1f}, "
                     f"max {L['passed'][i0:i1].max()} / {R['passed'][i0:i1].max()}, last car {L['passed'][last]} / "
                     f"{R['passed'][last]}, longest run at 900 cars {L['run_marks'][900]} / {R['run_marks'][900]} and at "
                     f"950 cars {L['run_marks'][950]} / {R['run_marks'][950]}")
    print("check, seeds 1 to " + str(man["check_seeds"]) + " (roll forward / fresh random spot): " + "; ".join(lines))
    big = man["check_spaces"]
    big_cars = int(round(big * man["check_load_max"]))
    r = simulate(big, big_cars, seed, run_marks=(int(0.9 * big), int(0.95 * big)))
    L, R = r["linear"], r["random"]
    parts = []
    for centre, half in ((0.90, man["check_window"]), (0.95, man["check_window"])):
        j0, j1 = int(round((centre - half) * big)), int(round((centre + half) * big))
        parts.append(f"cars at load {centre - half:.3f} to {centre + half:.3f} ({j1 - j0:,} cars): roll forward avg "
                     f"{L['passed'][j0:j1].mean():.1f} (closed form {cf_block(cf_linear, big, j0, j1) - 1:.1f}, at "
                     f"{centre:.2f} exactly {cf_linear(centre) - 1:.1f}), fresh random spot avg {R['passed'][j0:j1].mean():.2f} "
                     f"(closed form {cf_block(cf_random, big, j0, j1) - 1:.2f}, at {centre:.2f} exactly {cf_random(centre) - 1:.1f})")
    j0, j1 = int(0.9 * big), int(0.95 * big)
    print(f"check, {big:,}-space lot, {big_cars:,} cars, seed {seed}: " + "; ".join(parts) +
          f"; cars {j0 + 1:,} to {j1:,} (load 0.90 to 0.95) avg {L['passed'][j0:j1].mean():.1f} / "
          f"{R['passed'][j0:j1].mean():.2f} (closed forms {cf_block(cf_linear, big, j0, j1) - 1:.1f} / "
          f"{cf_block(cf_random, big, j0, j1) - 1:.2f}); longest run at 90 percent {L['run_marks'][j0]:,} / "
          f"{R['run_marks'][j0]} and at 95 percent {L['run_marks'][j1]:,} / {R['run_marks'][j1]}")
    return run


class Renderer:
    def __init__(self, man: dict, run: dict):
        self.man, self.run = man, run
        self.fps = man["fps"]
        font = os.environ["SEED_ZERO_FONT"]
        self.font = ImageFont.truetype(font, 40)
        self.font_title = ImageFont.truetype(font, 56)
        self.font_read = ImageFont.truetype(font, 36)
        self.font_small = ImageFont.truetype(font, 28)
        self.first = None
        n, cars = man["n_spaces"], man["n_cars"]
        assert n == COLS * ROWS
        self.fade = man["trail_fade"]
        # Schedule: cars 1..fast_cars in phase A with slots growing as a square from slot_min; the rest share
        # the time to t_last_park in proportion to slow_base + the longer of their two path lengths, so a
        # long drive gets more screen time; a car's paths light up over 70 percent of its slot.
        fast = man["fast_cars"]
        t_first, t_fast_end, t_last = man["t_first_car"], man["t_fast_end"], man["t_last_park"]
        lens = {p["name"]: run[p["name"]]["passed"].astype(float) for p in PANELS}
        longer = np.maximum(lens["linear"], lens["random"])
        q = (np.arange(fast) / (fast - 1)) ** 2
        slot_min = man["slot_min"]
        b = (t_fast_end - t_first - fast * slot_min) / q.sum()
        slots = np.zeros(cars)
        slots[:fast] = slot_min + b * q
        w = man["slow_base"] + longer[fast:cars]
        slots[fast:cars] = (t_last - t_fast_end) * w / w.sum()
        self.slots = slots
        self.t_start = t_first + np.concatenate(([0.0], np.cumsum(slots[:-1])))
        # Sweep speed (spots per second): the longer path of a car is lit over 70 percent of its slot, the
        # shorter path at the same speed.
        self.speed = np.where(longer > 0, longer / (0.7 * slots), np.inf)
        self.park_t = {}
        self.park_time = {}
        self.path_flat = {}
        self.path_off = {}
        for p in PANELS:
            name = p["name"]
            r = run[name]
            L = lens[name]
            park_t = self.t_start + np.where(L > 0, L / self.speed, 0.0)
            self.park_t[name] = park_t
            pt = np.full(n, np.inf)
            pt[r["park"]] = park_t
            self.park_time[name] = pt
            off = np.zeros(cars + 1, dtype=np.int64)
            off[1:] = np.cumsum([len(pp) for pp in r["paths"]])
            self.path_off[name] = off
            self.path_flat[name] = np.concatenate(r["paths"])
            block = man["block"]
            cs = np.concatenate(([0.0], np.cumsum(L)))
            idx = np.arange(1, cars + 1)
            lo_i = np.maximum(0, idx - block)
            self.avg_after = getattr(self, "avg_after", {})
            self.avg_after[name] = (cs[idx] - cs[lo_i]) / (idx - lo_i)
            p["tint"] = np.array(blend(WHITE, 0.5, p["colour"]), dtype=np.float32)
            p["flash"] = np.array(blend(WHITE, 0.85, p["colour"]), dtype=np.float32)
            p["col"] = np.array(p["colour"], dtype=np.float32)
        self.t_park_last = max(self.park_t[p["name"]][cars - 1] for p in PANELS)
        # Static base: background plus the outlines of every free space.
        base = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(base)
        for p in PANELS:
            y0 = p["top"] + GRID_DY
            for r_ in range(ROWS):
                for c in range(COLS):
                    x, y = GRID_X0 + c * PITCH, y0 + r_ * PITCH
                    d.rectangle((x, y, x + CELL - 1, y + CELL - 1), fill=FREE_FILL, outline=FREE_EDGE, width=1)
        self.base = np.asarray(base, dtype=np.float32)
        inner = np.zeros((PITCH, PITCH), dtype=np.float32)
        inner[:CELL, :CELL] = 1.0
        self.inner = np.tile(inner, (ROWS, COLS))[:, :, None]
        widths = {"overlay@34": (ImageFont.truetype(font, 34), man["overlay"])}
        for j, line in enumerate(man["title"].split("|")):
            widths[f"title line {j + 1}@56"] = (self.font_title, line)
        for p in PANELS:
            widths[f"label {p['name']}@40"] = (self.font, p["label"])
            widths[f"sublabel {p['name']}@28"] = (self.font_small, p["sub"])
        widths["readout avg@36"] = (self.font_read, f"last {man['block']} cars: avg "
                                    f"{int(round(max(self.avg_after[p['name']].max() for p in PANELS)))} spots")
        widths["readout parked@28"] = (self.font_small, f"cars parked {cars} of {n:,} ({cars * 100 // n}% full)")
        widths["readout passed@28"] = (self.font_small, f"this car passed {int(max(lens['linear'].max(), lens['random'].max()))} spots")
        widths["readout run@28"] = (self.font_small, f"longest full run {int(run['linear']['run_after'].max())}")
        for j, line in enumerate(self.payoff_lines()):
            widths[f"payoff line {j + 1}@40"] = (self.font, line)
        print("text widths: " + ", ".join(f"{k} {f.getlength(s):.0f} px" for k, (f, s) in widths.items()))
        longest_i = fast + int(np.argmax(longer[fast:cars]))
        print(f"video: {man['scene_duration']:g} s at {self.fps} fps; car 1 arrives at {t_first:g} s; cars 1 to {fast} park "
              f"by {max(self.park_t[p['name']][fast - 1] for p in PANELS):.2f} s (slots {slots[0] * 1000:.1f} to "
              f"{slots[fast - 1] * 1000:.1f} ms, {fast / (t_fast_end - t_first):.0f} cars per second); cars {fast + 1} to {cars} "
              f"take {slots[fast:cars].min() * 1000:.0f} to {slots[fast:cars].max() * 1000:.0f} ms each "
              f"({slots[fast:cars].min() * self.fps:.0f} to {slots[fast:cars].max() * self.fps:.0f} frames), the longest drive "
              f"(car {longest_i + 1}, {int(longer[longest_i])} spots) from {self.t_start[longest_i]:.2f} s at "
              f"{longer[longest_i] / (0.7 * slots[longest_i]) / self.fps:.1f} spots per frame; car {cars} starts at "
              f"{self.t_start[cars - 1]:.2f} s and parks at {self.t_park_last:.2f} s (roll forward "
              f"{self.park_t['linear'][cars - 1]:.2f} s, fresh random spot {self.park_t['random'][cars - 1]:.2f} s); "
              f"trails fade over {self.fade:g} s; payoff card at {man['payoff_t']:g} s; title until {man['title_until']:g} s")

    def payoff_numbers(self) -> dict:
        cars, block = self.man["n_cars"], self.man["block"]
        out = {}
        for p in PANELS:
            passed = self.run[p["name"]]["passed"]
            out[p["name"]] = int(passed[cars - 1]) if self.man["payoff_stat"] == "last" else \
                int(round(float(passed[cars - block:cars].mean())))
        return out

    def payoff_lines(self) -> list[str]:
        nums = self.payoff_numbers()
        text = self.man["payoff_text"].format(lin=nums["linear"], rnd=nums["random"])
        return [s.strip() for s in text.split("|")]

    def panel_state(self, p: dict, t: float) -> tuple[np.ndarray, np.ndarray, dict]:
        """Cell colours and alphas of one lot at video time t, plus the readouts."""
        man = self.man
        name = p["name"]
        n, cars = man["n_spaces"], man["n_cars"]
        r = self.run[name]
        park_time = self.park_time[name]
        taken = park_time <= t
        col = np.where(taken[:, None], p["col"], 0.0).astype(np.float32)
        alpha = taken.astype(np.float32)
        park_t = self.park_t[name]
        hi = int(np.searchsorted(self.t_start, t, side="right"))  # cars 0..hi-1 have started
        lo = int(np.searchsorted(park_t + self.fade, t, side="right"))  # cars below lo have faded
        off, flat = self.path_off[name], self.path_flat[name]
        passed = r["passed"]
        current = None
        for i in range(lo, hi):
            L = int(passed[i])
            tp = park_t[i]
            if t < tp:
                n_lit = min(L, int((t - self.t_start[i]) * self.speed[i]) + 1)
                a = 1.0
            else:
                n_lit = L
                a = 1.0 - (t - tp) / self.fade
                if a <= 0.0:
                    continue
            path = flat[off[i]:off[i + 1]]
            if L > 0:
                spots = path[:n_lit]
                col[spots] = p["tint"] * a + col[spots] * (1.0 - a)
                col[path[0]] = p["flash"] * a + col[path[0]] * (1.0 - a)
            if t >= tp:
                s = path[-1]
                col[s] = p["flash"] * a + col[s] * (1.0 - a)
            if i == hi - 1:
                current = n_lit if t < tp else L
        parked = int(np.count_nonzero(park_t <= t))
        reads = {
            "parked": parked,
            "pct": parked * 100 // n,
            "run": int(r["run_after"][parked - 1]) if parked > 0 else 0,
            "avg": int(round(float(self.avg_after[name][parked - 1]))) if parked > 0 else 0,
            "passed": current if current is not None else (int(passed[hi - 1]) if hi > 0 else 0),
        }
        return col.reshape(ROWS, COLS, 3), alpha.reshape(ROWS, COLS), reads

    def live_frame(self, f: int) -> np.ndarray:
        man = self.man
        t = f / self.fps
        frame = self.base.copy()
        reads = {}
        for p in PANELS:
            col, alpha, rd = self.panel_state(p, t)
            reads[p["name"]] = rd
            col_up = np.repeat(np.repeat(col, PITCH, axis=0), PITCH, axis=1)
            a_up = np.repeat(np.repeat(alpha, PITCH, axis=0), PITCH, axis=1)[:, :, None] * self.inner
            y0, x0 = p["top"] + GRID_DY, GRID_X0
            region = frame[y0:y0 + GRID_H, x0:x0 + GRID_W]
            frame[y0:y0 + GRID_H, x0:x0 + GRID_W] = region * (1.0 - a_up) + col_up * a_up
        img = Image.fromarray(frame.astype(np.uint8))
        d = ImageDraw.Draw(img)
        n = man["n_spaces"]
        for p in PANELS:
            top, colr, rd = p["top"], p["colour"], reads[p["name"]]
            d.text((GRID_X0, top + 24), p["label"], font=self.font, fill=colr, anchor="lm")
            d.text((GRID_X0 + GRID_W, top + 24), f"last {man['block']} cars: avg {rd['avg']} spots", font=self.font_read,
                   fill=TEXT, anchor="rm")
            d.text((GRID_X0, top + 66), p["sub"], font=self.font_small, fill=MUTED, anchor="lm")
            d.text((GRID_X0 + GRID_W, top + 66), f"longest full run {rd['run']}", font=self.font_small,
                   fill=colr if rd["run"] >= 100 else MUTED, anchor="rm")
            d.text((GRID_X0, top + 100), f"cars parked {rd['parked']} of {n:,} ({rd['pct']}% full)", font=self.font_small,
                   fill=MUTED, anchor="lm")
            d.text((GRID_X0 + GRID_W, top + 100), f"this car passed {rd['passed']} spot{'' if rd['passed'] == 1 else 's'}",
                   font=self.font_small, fill=TEXT, anchor="rm")
        if t < man["title_until"]:
            a = 1.0 if t < man["title_until"] - 0.4 else (man["title_until"] - t) / 0.4
            for j, line in enumerate(man["title"].split("|")):
                d.text((W / 2, 190 + j * 62), line, font=self.font_title, fill=blend(TEXT, a), anchor="mm")
        if t >= man["payoff_t"]:
            a = min(1.0, (t - man["payoff_t"]) / man["payoff_hold"])
            for j, line in enumerate(self.payoff_lines()):
                d.text((W / 2, PAYOFF_Y + j * 56), line, font=self.font, fill=blend(GOLD, a), anchor="mm")
        return np.asarray(img, dtype=np.float32)

    def frame_at(self, f: int) -> np.ndarray:
        man = self.man
        total = int(round(man["scene_duration"] * self.fps))
        live = self.live_frame(f)
        fade_frames = int(round(man["loop_fade"] * self.fps))
        if f >= total - fade_frames:
            if self.first is None:
                self.first = self.live_frame(0)
            a = (f - (total - fade_frames) + 1) / fade_frames
            live = live * (1 - a) + self.first * a
        return live.astype(np.uint8)

    def render(self, out_path: Path) -> None:
        global _RENDERER
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
        _RENDERER = self
        workers = min(8, os.cpu_count() or 1)
        with ProcessPoolExecutor(max_workers=workers, mp_context=multiprocessing.get_context("fork")) as pool:
            for f, frame in enumerate(pool.map(_frame_bytes, range(total), chunksize=8)):
                proc.stdin.write(frame)
                if f % 300 == 0:
                    print(f"frame {f}/{total}", file=sys.stderr)
        proc.stdin.close()
        if proc.wait() != 0:
            raise RuntimeError("ffmpeg failed")
        print(f"footage: {out_path} ({total / self.fps:.2f}s at {self.fps} fps)")


_RENDERER: Renderer | None = None


def _frame_bytes(f: int) -> bytes:
    assert _RENDERER is not None
    return _RENDERER.frame_at(f).tobytes()


def main() -> None:
    man = json.loads((ROOT / "projects/parking/manifest.json").read_text())
    run = measure(man)
    if "--measure-only" in sys.argv:
        return
    if "--frames" in sys.argv:
        times = [float(v) for v in sys.argv[sys.argv.index("--frames") + 1].split(",")]
        r = Renderer(man, run)
        (ROOT / "media/parking").mkdir(parents=True, exist_ok=True)
        for tv in times:
            Image.fromarray(r.frame_at(int(round(tv * man["fps"])))).save(ROOT / f"media/parking/smoke-{tv}.png")
        print("smoke frames: " + ", ".join(f"{tv}" for tv in times))
        return
    Renderer(man, run).render(ROOT / "media/parking/footage.mp4")


if __name__ == "__main__":
    main()
