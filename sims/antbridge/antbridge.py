#!/usr/bin/env python3
"""Ant double bridge: do ants find the shortest path?

One colony, two panels, the same random draws. A nest on the left, food on
the right, a short bridge (straight) and a long bridge (an arc twice as
long). Every ant walks at the same speed, so the long bridge takes twice
as long. At the nest and at the food an ant picks a bridge by the
Deneubourg rule: the chance of bridge i is (k + C_i)^n over the sum,
where C_i is the scent on that bridge, k = 20 and n = 2 (Deneubourg 1990).
Every completed crossing adds one unit of scent to its bridge; scent
evaporates with a fixed half life. Each ant owns one seeded random
stream, and the two panels consume the streams in the same order, so the
panels differ only in the world: on the top panel both bridges are open
from the start; on the bottom panel only the long bridge is open at first
and the short bridge opens after a delay.

Measured and printed: for each panel and each minute, the share of
crossings that used the short bridge, the scent on each bridge, the
total crossings, the minute the top panel passes eighty percent, and the
shares at ten minutes; checks at other seeds.

usage: antbridge.py [--measure-only]
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
WIRE = (60, 68, 80)
SCENT = (196, 120, 60)
ANT_OUT = (216, 222, 230)
ANT_BACK = (240, 176, 84)
NEST = (70, 80, 94)
FOOD = (120, 170, 90)

# Layout: two panels, captions between them at caption_y 0.49 (y 941..1021).
PANELS = {"open": {"label_y": 214, "base_y": 850}, "late": {"label_y": 1104, "base_y": 1740}}
NEST_X, FOOD_X = 220.0, 860.0
CHORD = FOOD_X - NEST_X
PAYOFF_Y = 1836.0


def arc_geometry(chord: float, ratio: float) -> tuple[float, float]:
    """Circular arc with arc length = ratio x chord: returns (radius, half angle)."""
    lo, hi = 1e-6, math.pi - 1e-6
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if math.sin(mid) / mid > 1.0 / ratio:
            lo = mid
        else:
            hi = mid
    theta = 0.5 * (lo + hi)
    return chord / (2.0 * math.sin(theta)), theta


def simulate(man: dict, late: bool, seed: int, frames: int, record: bool) -> dict:
    n_ants = man["ants"]
    k, n = man["k"], man["n"]
    comp = man["compression"]
    fps, sub = man["fps"], man["substeps"]
    dt = comp / (fps * sub)
    t_short = man["short_seconds"]
    t_long = t_short * man["length_ratio"]
    pause = man["pause_seconds"]
    decay = math.log(2) / man["half_life_seconds"]
    opens = man["short_opens_at"] if late else -math.inf
    rngs = [np.random.RandomState(seed * 1000 + i) for i in range(n_ants)]
    # Ant state: place 0 nest, 1 food; bridge 0 short, 1 long; progress 0..1; wait seconds.
    place = np.zeros(n_ants, dtype=int)
    on_bridge = np.zeros(n_ants, dtype=bool)
    bridge = np.zeros(n_ants, dtype=int)
    outbound = np.ones(n_ants, dtype=bool)
    progress = np.zeros(n_ants)
    wait = np.arange(n_ants) * man["release_gap_seconds"]
    scent = np.zeros(2)
    minute_cross = np.zeros((int(frames / fps * comp / 60) + 2, 2))
    total_cross = np.zeros(2)
    pos = np.zeros((frames, n_ants, 3)) if record else None  # bridge, progress(-1 = at a place), outbound
    scent_log = np.zeros((frames, 2))
    share_log = np.zeros(frames)
    recent = []  # (time, bridge) of completed crossings for the rolling share
    t = -man["preroll_seconds"]  # ants start leaving before the clock starts, so frame 0 is in motion

    def choose(i: int) -> int:
        u = rngs[i].random_sample()
        if t < opens:
            return 1
        ws = (k + scent[0]) ** n
        wl = (k + scent[1]) ** n
        return 0 if u < ws / (ws + wl) else 1

    preroll_frames = int(round(man["preroll_seconds"] / comp * fps))
    for f in range(-preroll_frames, frames):
        if f < 0:
            pass
        elif record:
            pos[f, :, 0] = bridge
            pos[f, :, 1] = np.where(on_bridge, progress, -1.0)
            pos[f, :, 2] = outbound
        if f >= 0:
            scent_log[f] = scent
            while recent and recent[0][0] < t - 60.0:
                recent.pop(0)
            share_log[f] = (sum(1 for _, b in recent if b == 0) / len(recent)) if recent else float("nan")
        for _ in range(sub):
            for i in range(n_ants):
                if on_bridge[i]:
                    progress[i] += dt / (t_short if bridge[i] == 0 else t_long)
                    if progress[i] >= 1.0:
                        on_bridge[i] = False
                        progress[i] = 0.0
                        place[i] = 1 if outbound[i] else 0
                        outbound[i] = not outbound[i]
                        wait[i] = pause
                        scent[bridge[i]] += 1.0
                        total_cross[bridge[i]] += 1
                        if t >= 0:
                            minute_cross[int(t // 60), bridge[i]] += 1
                        recent.append((t, bridge[i]))
                else:
                    wait[i] -= dt
                    if wait[i] <= 0.0:
                        bridge[i] = choose(i)
                        on_bridge[i] = True
                        progress[i] = 0.0
            scent *= math.exp(-decay * dt)
            t += dt
    return {"pos": pos, "scent": scent_log, "share": share_log, "minute": minute_cross, "total": total_cross}


def minute_share(run: dict, minute: int) -> float:
    row = run["minute"][minute - 1]
    return row[0] / row.sum() if row.sum() else float("nan")


def measure(man: dict) -> dict:
    fps, comp = man["fps"], man["compression"]
    frames = int(round(man["scene_duration"] * fps))
    minutes = int(man["colony_minutes"])
    print(f"{man['ants']} ants, seed {man['seed']}, short bridge {man['short_seconds']} s to cross, long bridge "
          f"{man['length_ratio']}x, k = {man['k']}, n = {man['n']}, scent half life {man['half_life_seconds']} s, "
          f"{man['pause_seconds']} s pause at each end, one ant released every {man['release_gap_seconds']} s; "
          f"{man['preroll_seconds']:.0f} s of pre-roll before the clock starts; "
          f"video runs {comp}x, so {man['colony_minutes']} colony minutes take {60 * man['colony_minutes'] / comp:.1f} s")
    runs = {}
    for name, late in (("open", False), ("late", True)):
        r = simulate(man, late, man["seed"], frames, record=True)
        runs[name] = r
        label = "both bridges open from the start" if not late else f"long bridge only, short bridge opens at {man['short_opens_at']:.0f} s"
        print(f"{name} panel ({label}):")
        for m in range(1, minutes + 1):
            row = r["minute"][m - 1]
            fr = min(frames - 1, int(round(m * 60 / comp * fps)))
            print(f"  minute {m}: {int(row[0])} short, {int(row[1])} long crossings, short share {100 * minute_share(r, m):.1f}%; "
                  f"scent short {r['scent'][fr][0]:.0f}, long {r['scent'][fr][1]:.0f}")
        tot = r["minute"][:minutes].sum(axis=0)
        print(f"  all {minutes} minutes: {int(tot[0])} short, {int(tot[1])} long crossings, short share {100 * tot[0] / tot.sum():.1f}%")
        over = [m for m in range(1, minutes + 1) if minute_share(r, m) >= 0.8]
        if over:
            print(f"  first minute with the short share at 80% or more: minute {over[0]}")
    out = {"runs": runs, "share_open": minute_share(runs["open"], minutes), "share_late": minute_share(runs["late"], minutes)}
    print(f"payoff, minute {minutes}: open panel {100 * out['share_open']:.1f}% of crossings on the short bridge, "
          f"late panel {100 * out['share_late']:.1f}%")
    for s in man["check_seeds"]:
        a = simulate(man, False, s, frames, record=False)
        b = simulate(man, True, s, frames, record=False)
        print(f"check: seed {s}: open panel minute {minutes} share {100 * minute_share(a, minutes):.1f}%, "
              f"late panel {100 * minute_share(b, minutes):.1f}%")
    return out


class Renderer:
    def __init__(self, man: dict, meas: dict):
        self.man, self.meas = man, meas
        self.fps = man["fps"]
        font = os.environ["SEED_ZERO_FONT"]
        self.font = ImageFont.truetype(font, 40)
        self.font_small = ImageFont.truetype(font, 32)
        self.font_big = ImageFont.truetype(font, 56)
        self.font_title = ImageFont.truetype(font, 54)
        self.radius, self.theta = arc_geometry(CHORD, man["length_ratio"])

    def point(self, name: str, bridge: int, u: float, outbound: bool) -> tuple[float, float]:
        base = PANELS[name]["base_y"]
        s = u if outbound else 1.0 - u
        if bridge == 0:
            return NEST_X + s * CHORD, base
        cx = (NEST_X + FOOD_X) / 2
        cy = base + self.radius * math.cos(self.theta)
        ang = -self.theta + 2 * self.theta * s
        return cx + self.radius * math.sin(ang), cy - self.radius * math.cos(ang)

    def frame_at(self, f: int) -> np.ndarray:
        man, m = self.man, self.meas
        t = f / self.fps
        t_col = t * man["compression"]
        img = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(img)
        title_on = t < man["title_until"]
        for name, p in PANELS.items():
            run = m["runs"][name]
            base = p["base_y"]
            label = "both bridges open from the start" if name == "open" else "short bridge opens later"
            if name == "open" and title_on:
                alpha = 1.0 if t < man["title_until"] - 0.4 else (man["title_until"] - t) / 0.4
                shade = tuple(int(c * alpha + BG[j] * (1 - alpha)) for j, c in enumerate(TEXT))
                d.text((W / 2, p["label_y"]), man["title"], font=self.font_title, fill=shade, anchor="mm")
            else:
                d.text((60, p["label_y"]), label, font=self.font, fill=TEAL, anchor="lm")
            scent = run["scent"][f]
            top = max(scent.max(), 1.0)
            closed = name == "late" and t_col < man["short_opens_at"]
            for b in (1, 0):
                level = scent[b] / top
                width = int(3 + 30 * level)
                col = tuple(int(WIRE[j] * (1 - level) + SCENT[j] * level) for j in range(3))
                pts = [self.point(name, b, u, True) for u in np.linspace(0, 1, 120)]
                if b == 0 and closed:
                    for i in range(0, 118, 4):
                        d.line([pts[i], pts[i + 2]], fill=WIRE, width=3)
                    d.text((W / 2, base + 44), "closed", font=self.font_small, fill=MUTED, anchor="mm")
                else:
                    d.line(pts, fill=col, width=width, joint="curve")
            cx = (NEST_X + FOOD_X) / 2
            cy = base + self.radius * math.cos(self.theta)
            d.text((cx, cy - self.radius - 30), "long bridge, twice as long", font=self.font_small, fill=MUTED, anchor="mm")
            if not closed:
                d.text((W / 2, base + 44), "short bridge", font=self.font_small, fill=MUTED, anchor="mm")
            # Nest and food.
            d.ellipse((NEST_X - 46, base - 46, NEST_X + 46, base + 46), fill=NEST)
            d.text((NEST_X, base), "nest", font=self.font_small, fill=TEXT, anchor="mm")
            d.ellipse((FOOD_X - 46, base - 46, FOOD_X + 46, base + 46), fill=FOOD)
            d.text((FOOD_X, base), "food", font=self.font_small, fill=BG, anchor="mm")
            # Ants.
            pos = run["pos"][f]
            for i in range(pos.shape[0]):
                b, u, out = int(pos[i, 0]), float(pos[i, 1]), bool(pos[i, 2])
                if u < 0:
                    continue
                x, y = self.point(name, b, u, out)
                col = ANT_OUT if out else ANT_BACK
                d.ellipse((x - 6, y - 6, x + 6, y + 6), fill=col)
            # Readouts: the clock and the rolling share of crossings on the short bridge.
            mins, secs = divmod(int(t_col), 60)
            if not title_on:
                d.text((W - 60, p["label_y"]), f"{mins}:{secs:02d}", font=self.font, fill=TEXT, anchor="rm")
                share = run["share"][f]
                if not math.isnan(share):
                    col = GOLD if share >= 0.5 else TEXT
                    d.text((60, p["label_y"] + 56), f"short bridge: {100 * share:.0f}% of trips this minute",
                           font=self.font_small, fill=col, anchor="lm")
        if t >= man["payoff_t"]:
            alpha = min(1.0, (t - man["payoff_t"]) / man["payoff_hold"])
            shade = tuple(int(c * alpha + BG[j] * (1 - alpha)) for j, c in enumerate(GOLD))
            text = man["payoff_text"].format(open=100 * m["share_open"], late=100 * m["share_late"], minutes=man["colony_minutes"])
            for j, line in enumerate(text.split("|")):
                d.text((W / 2, PAYOFF_Y + j * 58), line.strip(), font=self.font, fill=shade, anchor="mm")
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
            proc.stdin.write(self.frame_at(f).tobytes())
            if f % 300 == 0:
                print(f"frame {f}/{total}", file=sys.stderr)
        proc.stdin.close()
        if proc.wait() != 0:
            raise RuntimeError("ffmpeg failed")
        print(f"footage: {out_path} ({total / self.fps:.2f}s at {self.fps} fps)")


def main() -> None:
    man = json.loads((ROOT / "projects/antbridge/manifest.json").read_text())
    meas = measure(man)
    if "--measure-only" in sys.argv:
        return
    Renderer(man, meas).render(ROOT / "media/antbridge/footage.mp4")


if __name__ == "__main__":
    main()
