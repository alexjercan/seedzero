#!/usr/bin/env python3
"""Monty Hall race: simulation, measurement, and footage.

Ten thousand games with prize and pick drawn from a seeded generator. The
host always opens a losing door the player did not pick. Every game is
scored twice, staying and switching, and two bars race as the games
resolve. A demo panel replays the first games one by one so the mechanism
stays on screen.

usage: montyhall.py [--measure-only]
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
DOOR = (58, 70, 86)
DOOR_EDGE = (86, 100, 118)
RECESS = (26, 31, 38)
STAY = (216, 222, 230)
SWITCH = (92, 200, 165)
PRIZE = (222, 186, 92)
GOAT = (110, 120, 133)
MUTED = (138, 148, 163)
TEXT = (216, 222, 230)

# Layout. The caption band burned in by compose.sh sits at y = 1344..1420;
# nothing else may draw text there.
CENTER_X = W / 2
DOOR_XS = (270.0, 540.0, 810.0)
DOOR_TOP = 330.0
DOOR_W, DOOR_H = 220.0, 330.0
DEMO_LABEL_Y = 745.0
ARROW_Y = 700.0
PAYOFF_Y = 890.0
BAR_X0 = 140.0
BAR_MAX_W = 800.0
BAR_H = 96.0
BAR_YS = {"stay": 1060.0, "switch": 1230.0}

# Timeline (seconds).
INTRO_HOLD = 2.0
RESET_GAP = 0.5
LABEL_FADE = 0.6

# Demo phase boundaries inside one demo game.
PICK_T = 0.7
HOST_T = 1.5
OFFER_T = 2.1
REVEAL_T = 2.8


def simulate(seed: int, games: int):
    rng = np.random.RandomState(seed)
    prize = rng.randint(0, 3, games)
    pick = rng.randint(0, 3, games)
    coin = rng.randint(0, 2, games)
    host = np.empty(games, dtype=np.int64)
    for g in range(games):
        goats = [d for d in range(3) if d != pick[g] and d != prize[g]]
        host[g] = goats[coin[g] % len(goats)]
    switch_door = 3 - pick - host
    stay_wins = prize == pick
    switch_wins = prize == switch_door
    assert np.array_equal(switch_wins, ~stay_wins)
    return prize, pick, host, switch_door, stay_wins


def measure_report(stay_wins: np.ndarray, pick, prize, host) -> tuple[int, int]:
    games = len(stay_wins)
    stay = int(stay_wins.sum())
    switch = games - stay
    print(f"games: {games}")
    print(f"stay wins: {stay} ({100 * stay / games:.2f}%)")
    print(f"switch wins: {switch} ({100 * switch / games:.2f}%)")
    print(f"switch vs stay: {switch / stay:.2f} to 1")
    print(f"theory: switch 2/3 = {2 * games / 3:.1f}, stay 1/3 = {games / 3:.1f}")
    honest = bool(np.all(host != pick) and np.all(host != prize))
    print(f"host check (never opens pick or prize): {honest}")
    return stay, switch


class Renderer:
    def __init__(self, manifest, prize, pick, host, switch_door, stay_wins):
        self.fps = manifest["fps"]
        self.games = manifest["games"]
        self.race_dur = manifest["race_duration"]
        self.payoff_hold = manifest["payoff_hold"]
        self.demo_time = manifest["demo_time"]
        self.prize, self.pick, self.host = prize, pick, host
        self.switch_door, self.stay_wins = switch_door, stay_wins
        self.cum_stay = np.concatenate([[0], np.cumsum(stay_wins)])
        self.stay_total = int(stay_wins.sum())
        self.switch_total = self.games - self.stay_total
        self.bar_scale = BAR_MAX_W / self.switch_total
        self.font = ImageFont.truetype(os.environ["SEED_ZERO_FONT"], 42)
        self.font_small = ImageFont.truetype(os.environ["SEED_ZERO_FONT"], 36)
        self.font_big = ImageFont.truetype(os.environ["SEED_ZERO_FONT"], 58)

    def resolved(self, s: float) -> int:
        x = min(max(s / self.race_dur, 0.0), 1.0)
        return int(round(self.games * x * x * (3 - 2 * x)))

    def draw_door(self, d, x, open_glyph=None, outline=None, outline_w=4):
        x0, y0 = x - DOOR_W / 2, DOOR_TOP
        x1, y1 = x + DOOR_W / 2, DOOR_TOP + DOOR_H
        if open_glyph is None:
            d.rounded_rectangle((x0, y0, x1, y1), 14, fill=DOOR, outline=DOOR_EDGE, width=3)
            d.ellipse((x1 - 44, (y0 + y1) / 2 - 8, x1 - 28, (y0 + y1) / 2 + 8), fill=DOOR_EDGE)
        else:
            d.rounded_rectangle((x0, y0, x1, y1), 14, fill=RECESS, outline=DOOR_EDGE, width=3)
            cx, cy = x, (y0 + y1) / 2
            if open_glyph == "goat":
                for sx in (-1, 1):
                    d.line((cx - sx * 34, cy - 34, cx + sx * 34, cy + 34), fill=GOAT, width=10)
            else:
                d.ellipse((cx - 34, cy - 34, cx + 34, cy + 34), fill=PRIZE)
                d.ellipse((cx - 16, cy - 16, cx + 16, cy + 16), outline=BG, width=5)
        if outline is not None:
            d.rounded_rectangle((x0 - 8, y0 - 8, x1 + 8, y1 + 8), 18,
                                outline=outline, width=outline_w)

    def draw_arrow(self, d, x_from, x_to):
        sgn = 1 if x_to > x_from else -1
        a, b = x_from + sgn * 30, x_to - sgn * 40
        d.line((a, ARROW_Y, b, ARROW_Y), fill=SWITCH, width=8)
        d.polygon([(b + sgn * 34, ARROW_Y), (b, ARROW_Y - 20), (b, ARROW_Y + 20)],
                  fill=SWITCH)

    def draw_demo(self, d, s: float, end: float):
        """Demo panel at scene time s; demos run back to back until `end`."""
        if s < 0 or s >= end:
            for x in DOOR_XS:
                self.draw_door(d, x)
            return
        g = int(s / self.demo_time)
        ph = s - g * self.demo_time
        pick, host, prize = int(self.pick[g]), int(self.host[g]), int(self.prize[g])
        sw = int(self.switch_door[g])
        stay_won = bool(self.stay_wins[g])
        for door, x in enumerate(DOOR_XS):
            open_glyph = None
            if ph >= HOST_T and door == host:
                open_glyph = "goat"
            if ph >= REVEAL_T and door == prize:
                open_glyph = "prize"
            outline = None
            if ph >= PICK_T and door == pick:
                outline = STAY
            if ph >= REVEAL_T:
                if stay_won and door == pick:
                    outline = STAY
                elif not stay_won and door == sw:
                    outline = SWITCH
            self.draw_door(d, x, open_glyph, outline,
                           outline_w=8 if ph >= REVEAL_T and outline else 4)
        if PICK_T <= ph:
            d.text((DOOR_XS[pick], DEMO_LABEL_Y), "pick",
                   font=self.font_small, fill=MUTED, anchor="mm")
        if OFFER_T <= ph < REVEAL_T:
            self.draw_arrow(d, DOOR_XS[pick], DOOR_XS[sw])
        if ph >= REVEAL_T:
            who = "stay wins" if stay_won else "switch wins"
            col = STAY if stay_won else SWITCH
            d.text((CENTER_X, ARROW_Y), who, font=self.font, fill=col, anchor="mm")

    def draw_bars(self, d, stay_c: int, switch_c: int, label_alpha: float):
        x23 = BAR_X0 + (2 * self.games / 3) * self.bar_scale
        for y in range(1036, 1330, 36):
            d.line((x23, y, x23, y + 18), fill=(70, 80, 94), width=3)
        d.text((x23, 1006), "2/3", font=self.font_small, fill=MUTED, anchor="mm")
        for key, count, col in (("stay", stay_c, STAY), ("switch", switch_c, SWITCH)):
            y = BAR_YS[key]
            w = max(2, int(round(count * self.bar_scale))) if count else 0
            if w:
                d.rectangle((BAR_X0, y, BAR_X0 + w, y + BAR_H), fill=col)
            d.text((BAR_X0, y - 32), key, font=self.font_small, fill=MUTED, anchor="lm")
            if w > 620:
                d.text((BAR_X0 + w - 24, y + BAR_H / 2), f"{count:,}",
                       font=self.font_big, fill=BG, anchor="rm")
            else:
                d.text((BAR_X0 + w + 24, y + BAR_H / 2), f"{count:,}",
                       font=self.font_big, fill=col, anchor="lm")
        if label_alpha > 0:
            shade = tuple(int(v * label_alpha + BG[i] * (1 - label_alpha))
                          for i, v in enumerate(TEXT))
            mut = tuple(int(v * label_alpha + BG[i] * (1 - label_alpha))
                        for i, v in enumerate(MUTED))
            ratio = self.switch_total / self.stay_total
            d.text((CENTER_X, PAYOFF_Y), f"{ratio:.2f} to 1",
                   font=self.font_big, fill=shade, anchor="mm")
            d.text((CENTER_X, PAYOFF_Y + 64), "switch vs stay, same games",
                   font=self.font_small, fill=mut, anchor="mm")

    def frame_at(self, s: float, demo_end: float) -> np.ndarray:
        """Scene time s: race runs on [0, race_dur], then the payoff hold."""
        frame = np.zeros((H, W, 3), dtype=np.uint8)
        frame[:, :] = BG
        img = Image.fromarray(frame)
        d = ImageDraw.Draw(img)
        n = self.resolved(s)
        stay_c = int(self.cum_stay[n])
        alpha = min(1.0, max(0.0, (s - self.race_dur) / LABEL_FADE))
        self.draw_bars(d, stay_c, n - stay_c, alpha)
        self.draw_demo(d, s, demo_end)
        d.text((W - 60, 190), f"{n:,} games", font=self.font_small,
               fill=MUTED, anchor="rm")
        return np.asarray(img)

    def render(self, out_path: Path) -> None:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        scene_dur = self.race_dur + self.payoff_hold
        demo_end = int(scene_dur / self.demo_time) * self.demo_time
        total = int(round((INTRO_HOLD + RESET_GAP + scene_dur) * self.fps))
        proc = subprocess.Popen(
            ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
             "-s", f"{W}x{H}", "-r", str(self.fps), "-i", "-",
             "-c:v", "libx264", "-crf", "16", "-preset", "medium",
             "-pix_fmt", "yuv420p", str(out_path)],
            stdin=subprocess.PIPE,
        )
        assert proc.stdin is not None
        for f in range(total):
            t = f / self.fps
            if t < INTRO_HOLD:
                frame = self.frame_at(scene_dur, demo_end=0.0)
            elif t < INTRO_HOLD + RESET_GAP:
                frame = self.frame_at(0.0, demo_end=0.0)
            else:
                s = t - INTRO_HOLD - RESET_GAP
                frame = self.frame_at(s, demo_end)
            proc.stdin.write(frame.tobytes())
            if f % 300 == 0:
                print(f"frame {f}/{total}", file=sys.stderr)
        proc.stdin.close()
        if proc.wait() != 0:
            raise RuntimeError("ffmpeg failed")
        print(f"footage: {out_path} ({total / self.fps:.2f}s at {self.fps} fps)")


def main() -> None:
    manifest = json.loads((ROOT / "projects/montyhall/manifest.json").read_text())
    prize, pick, host, switch_door, stay_wins = simulate(
        manifest["seed"], manifest["games"])
    measure_report(stay_wins, pick, prize, host)
    if "--measure-only" in sys.argv:
        return
    Renderer(manifest, prize, pick, host, switch_door, stay_wins).render(
        ROOT / "media/montyhall/footage.mp4")


if __name__ == "__main__":
    main()
