#!/usr/bin/env python3
"""Elevator paradox: you wait on floor 2, which way is the first elevator going?

One elevator runs from the ground floor to the top floor and back at a
constant pace, never stopping. You stand on a low floor and press the button
at seeded random moments. The first elevator to reach you is going down
whenever it was above you when you pressed, and going up only when it was
between you and the ground floor. The share of the cycle it spends above
floor f is (floors - f) / (floors - 1), so 8/9 on floor 2 of ten.

Measured and printed: the count of arrivals going down and going up over
the seeded presses, the same for a friend on a high floor and for the middle
floor, the mean waits, the exact shares, a million-press check at another
seed, the on-screen schedule and the text widths.

usage: elevator.py [--measure-only] [--frames t1,t2,...]
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

FLOOR_H = 100.0
Y_GROUND = 1300.0  # floor 1 line
BUILD_X0, SHAFT_X0, SHAFT_X1, BUILD_X1 = 120.0, 300.0, 420.0, 470.0
TRACE_X0, TRACE_X1 = 540.0, 1040.0
TALLY_Y = 1352.0
BAR_Y = 1398.0
PAYOFF_Y = 1836.0


def floor_y(f: float) -> float:
    return Y_GROUND - (f - 1.0) * FLOOR_H


class Lift:
    def __init__(self, floors: int, floor_seconds: float):
        self.floors = floors
        self.half = (floors - 1) * floor_seconds
        self.cycle = 2 * self.half
        self.fs = floor_seconds

    def pos(self, t: float) -> float:
        ph = t % self.cycle
        if ph < self.half:
            return 1.0 + ph / self.fs
        return float(self.floors) - (ph - self.half) / self.fs

    def going_up(self, t: float) -> bool:
        return (t % self.cycle) < self.half

    def next_arrival(self, f: int, tau: float) -> tuple[float, bool]:
        """First time strictly after tau the lift is at floor f, and whether it
        is going down then."""
        k = math.floor(tau / self.cycle)
        best = None
        for kk in (k, k + 1):
            t_up = kk * self.cycle + (f - 1) * self.fs
            t_down = kk * self.cycle + self.half + (self.floors - f) * self.fs
            for t_arr, down in ((t_up, False), (t_down, True)):
                if t_arr > tau and (best is None or t_arr < best[0]):
                    best = (t_arr, down)
        assert best is not None
        return best


def presses_for(man: dict, seed: int, n: int) -> np.ndarray:
    rng = np.random.RandomState(seed)
    lift = Lift(man["floors"], man["floor_seconds"])
    t0 = man["start_offset"] + man["press_from_video_s"] * man["playback"]
    return np.sort(t0 + rng.uniform(0.0, man["cycles"] * lift.cycle, n))


def tally(lift: Lift, f: int, taus: np.ndarray) -> dict:
    arr = np.empty(len(taus))
    down = np.empty(len(taus), dtype=bool)
    for i, tau in enumerate(taus):
        arr[i], down[i] = lift.next_arrival(f, float(tau))
    wait = arr - taus
    return {"arrival": arr, "down": down, "n_down": int(down.sum()), "n_up": int((~down).sum()),
            "wait_down": float(wait[down].mean()) if down.any() else 0.0,
            "wait_up": float(wait[~down].mean()) if (~down).any() else 0.0, "wait": float(wait.mean())}


def measure(man: dict) -> dict:
    lift = Lift(man["floors"], man["floor_seconds"])
    taus = presses_for(man, man["seed"], man["presses"])
    you, friend, mid = man["your_floor"], man["friend_floor"], (man["floors"] + 1) // 2
    print(f"{man['floors']} floors, one elevator at {man['floor_seconds']:g} s per floor, never stopping: "
          f"{lift.half:g} s up, {lift.half:g} s down, cycle {lift.cycle:g} s; {man['presses']:,} button presses at seed "
          f"{man['seed']} spread evenly over {man['cycles']} full cycles ({man['cycles'] * lift.cycle:g} s) starting at "
          f"sim time {taus[0]:.1f} s")
    out = {"lift": lift, "taus": taus}
    for label, f in (("you", you), ("friend", friend), ("middle", mid)):
        t = tally(lift, f, taus)
        above = (man["floors"] - f) / (man["floors"] - 1)
        print(f"floor {f} ({label}): first elevator going down {t['n_down']:,} times, going up {t['n_up']:,} "
              f"({100 * t['n_down'] / len(taus):.2f}% down; exact share of the cycle spent above floor {f}: "
              f"{man['floors'] - f}/{man['floors'] - 1} = {100 * above:.2f}%); mean wait {t['wait']:.1f} s, "
              f"{t['wait_down']:.1f} s when it came down, {t['wait_up']:.1f} s when it came up")
        out[label] = t
    big = tally(lift, you, presses_for(man, man["check_seed"], man["check_presses"]))
    print(f"check, {man['check_presses']:,} presses at seed {man['check_seed']} on floor {you}: "
          f"{100 * big['n_down'] / man['check_presses']:.3f}% down")
    you_t = out["you"]
    pb, t0 = man["playback"], man["start_offset"]
    last = you_t["arrival"].max()
    print(f"on screen at {pb:g}x from sim time {t0:g} s: presses from {(taus[0] - t0) / pb:.2f} to {(taus[-1] - t0) / pb:.2f} s "
          f"of video, last press answered at {(last - t0) / pb:.2f} s; the elevator is at floor {lift.pos(t0):.2f} "
          f"{'going up' if lift.going_up(t0) else 'going down'} in the first frame")
    out["n_down"], out["n_up"] = you_t["n_down"], you_t["n_up"]
    return out


class Renderer:
    def __init__(self, man: dict, meas: dict):
        self.man, self.meas = man, meas
        self.fps = man["fps"]
        font = os.environ["SEED_ZERO_FONT"]
        self.font = ImageFont.truetype(font, 40)
        self.font_small = ImageFont.truetype(font, 30)
        self.font_big = ImageFont.truetype(font, 56)
        self.font_title = ImageFont.truetype(font, 56)
        self.font_label = ImageFont.truetype(font, 36)
        self.font_tally = ImageFont.truetype(font, 44)
        self.first = None
        self.px_per_s = (TRACE_X1 - TRACE_X0) / man["trace_seconds"]
        self.taus = meas["taus"]
        self.arrival = meas["you"]["arrival"]
        self.down = meas["you"]["down"]
        widths = {"overlay@34": (ImageFont.truetype(font, 34), man["overlay"]), "subtitle@40": (self.font, man["subtitle"])}
        for j, line in enumerate(man["title"].split("|")):
            widths[f"title line {j + 1}@56"] = (self.font_title, line)
        widths["tally down@44"] = (self.font_tally, f"going down {meas['n_down']:,}")
        widths["tally up@44"] = (self.font_tally, f"going up {meas['n_up']:,}")
        for j, line in enumerate(self.payoff_lines()):
            widths[f"payoff line {j + 1}@40"] = (self.font, line)
        print("text widths: " + ", ".join(f"{k} {f.getlength(s):.0f} px" for k, (f, s) in widths.items()))

    def payoff_lines(self) -> list[str]:
        text = self.man["payoff_text"].format(down=self.meas["n_down"], up=self.meas["n_up"], n=self.man["presses"])
        return [s.strip() for s in text.split("|")]

    @staticmethod
    def blend(col: tuple, alpha: float) -> tuple:
        return tuple(int(c * alpha + BG[j] * (1 - alpha)) for j, c in enumerate(col))

    def live_frame(self, f: int) -> Image.Image:
        man, lift = self.man, self.meas["lift"]
        t = f / self.fps
        now = man["start_offset"] + t * man["playback"]
        img = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(img)
        floors, you = man["floors"], man["your_floor"]
        title_on = t < man["title_until"]
        # Building: floor lines, shaft, landings.
        d.rectangle((BUILD_X0, floor_y(floors) - 70, BUILD_X1, Y_GROUND + 10), fill=HULL, outline=WIRE, width=3)
        d.rectangle((SHAFT_X0, floor_y(floors) - 60, SHAFT_X1, Y_GROUND), fill=BG, outline=WIRE, width=2)
        for fl in range(1, floors + 1):
            y = floor_y(fl)
            col = TEXT if fl == you else WIRE
            d.line((BUILD_X0, y, SHAFT_X0, y), fill=col, width=4 if fl == you else 2)
            d.line((SHAFT_X1, y, BUILD_X1, y), fill=col, width=4 if fl == you else 2)
            d.text((BUILD_X0 + 14, y - 22), str(fl), font=self.font_small, fill=TEXT if fl == you else MUTED, anchor="lm")
            # Faint guide into the trace.
            d.line((TRACE_X0, y, TRACE_X1, y), fill=self.blend(WIRE, 0.6) if fl != you else self.blend(TEXT, 0.35), width=2)
        # You, on your floor.
        yx, yy = 232.0, floor_y(you)
        d.ellipse((yx - 13, yy - 78, yx + 13, yy - 52), fill=TEXT)
        d.line((yx, yy - 52, yx, yy - 22), fill=TEXT, width=6)
        d.line((yx, yy - 22, yx - 12, yy - 2), fill=TEXT, width=6)
        d.line((yx, yy - 22, yx + 12, yy - 2), fill=TEXT, width=6)
        d.line((yx, yy - 44, yx + 22, yy - 40), fill=TEXT, width=5)
        d.text((yx, yy - 104), "you", font=self.font_label, fill=TEXT, anchor="mm")
        d.ellipse((SHAFT_X0 - 16, yy - 46, SHAFT_X0 - 4, yy - 34), fill=GOLD)  # the button
        # Trace of where the elevator has been, coloured above and below you.
        n_pts = 400
        ts = np.linspace(now - man["trace_seconds"], now, n_pts)
        pts = [(TRACE_X1 - (now - tt) * self.px_per_s, floor_y(lift.pos(tt))) for tt in ts]
        for (x0, y0), (x1, y1) in zip(pts[:-1], pts[1:]):
            above = (y0 + y1) / 2 < floor_y(you)
            d.line((x0, y0, x1, y1), fill=TEAL if above else GOLD, width=5)
        # Presses on your floor line: white until answered, then coloured by the direction.
        vis = (self.taus <= now) & (self.taus >= now - man["trace_seconds"])
        yl = floor_y(you)
        for tau, arr, dn in zip(self.taus[vis], self.arrival[vis], self.down[vis]):
            x = TRACE_X1 - (now - tau) * self.px_per_s
            col = (TEAL if dn else GOLD) if now >= arr else TEXT
            d.line((x, yl - 9, x, yl + 9), fill=col, width=2)
        d.text((TRACE_X0, floor_y(floors) - 40), "where the elevator has been", font=self.font_small, fill=MUTED, anchor="lm")
        # Elevator car with its direction arrow.
        cy = floor_y(lift.pos(now))
        cx = (SHAFT_X0 + SHAFT_X1) / 2
        d.rectangle((SHAFT_X0 + 10, cy - 42, SHAFT_X1 - 10, cy + 2), fill=self.blend(TEXT, 0.25), outline=TEXT, width=3)
        if lift.going_up(now):
            d.polygon([(cx, cy - 34), (cx - 14, cy - 10), (cx + 14, cy - 10)], fill=TEAL)
        else:
            d.polygon([(cx, cy - 6), (cx - 14, cy - 30), (cx + 14, cy - 30)], fill=TEAL)
        # Tally so far.
        answered = self.arrival <= now
        n_down = int((self.down & answered).sum())
        n_up = int((~self.down & answered).sum())
        d.text((BUILD_X0, TALLY_Y), f"going down {n_down:,}", font=self.font_tally, fill=TEAL, anchor="lm")
        d.text((TRACE_X1, TALLY_Y), f"going up {n_up:,}", font=self.font_tally, fill=GOLD, anchor="rm")
        tot = n_down + n_up
        d.rectangle((BUILD_X0, BAR_Y - 7, TRACE_X1, BAR_Y + 7), fill=WIRE)
        if tot:
            split = BUILD_X0 + (TRACE_X1 - BUILD_X0) * n_down / tot
            d.rectangle((BUILD_X0, BAR_Y - 7, split, BAR_Y + 7), fill=TEAL)
            d.rectangle((split, BAR_Y - 7, TRACE_X1, BAR_Y + 7), fill=GOLD)
        # Title or subtitle.
        if title_on:
            alpha = 1.0 if t < man["title_until"] - 0.4 else (man["title_until"] - t) / 0.4
            lines = man["title"].split("|")
            for j, line in enumerate(lines):
                d.text((W / 2, 168 + j * 60), line, font=self.font_title, fill=self.blend(TEXT, alpha), anchor="mm")
        else:
            d.text((W / 2, 205), man["subtitle"], font=self.font, fill=MUTED, anchor="mm")
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
    man = json.loads((ROOT / "projects/elevator/manifest.json").read_text())
    meas = measure(man)
    if "--measure-only" in sys.argv:
        return
    if "--frames" in sys.argv:
        times = [float(v) for v in sys.argv[sys.argv.index("--frames") + 1].split(",")]
        r = Renderer(man, meas)
        (ROOT / "media/elevator").mkdir(parents=True, exist_ok=True)
        for tv in times:
            Image.fromarray(r.frame_at(int(round(tv * man["fps"])))).save(ROOT / f"media/elevator/smoke-{tv}.png")
        print("smoke frames: " + ", ".join(f"{tv}" for tv in times))
        return
    Renderer(man, meas).render(ROOT / "media/elevator/footage.mp4")


if __name__ == "__main__":
    main()
