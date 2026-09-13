#!/usr/bin/env python3
"""Slinky drop: when does the bottom start to fall?

A stretched slinky hangs from its top coil beside a solid rod of the same
length. Both are released at the same moment. The slinky is a chain of N
equal coils joined by springs of rest length d (the gap of two touching
coils); coils cannot pass through each other, and coils that touch move on
together (a perfectly inelastic pile-up, the standard collapse model of a
falling slinky). Hanging at rest, the spring below coil i carries the weight
of every coil under it, so the coils near the top are far apart and the
coils near the bottom nearly touch.

The equations are integrated with semi-implicit Euler at a fixed small step;
after every step any run of coils closer than d is placed at spacing d about
its centre of mass with the momentum-conserving common velocity. The rod is
in free fall. No seed: the run is deterministic.

Measured and printed: the hanging length and the coil spacings, the time the
bottom coil first moves by 0.01 mm and by 1 mm, the time the collapse front
reaches the bottom coil, how far the top coil and the rod's bottom have
fallen by then, the top coil's average acceleration in units of g, the
largest movement of the bottom coil before the front arrives, a centre of
mass free-fall check (internal forces cannot move the centre of mass), a
step-halving check, three other slinkies, the linear wave-transit estimate,
and the on-screen text widths.

usage: slinky.py [--measure-only] [--frames t1,t2,...]
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
CLAMP = (120, 130, 145)

# Layout: two panels side by side, captions in the band at caption_y 0.75
# (y 1440..1510), payoff lines under it.
PANELS = {"slinky": {"x": 300.0}, "rod": {"x": 780.0}}
LABEL_Y = 236
READ_Y = 290
VALUE_Y = 338
TOP_Y = 420.0
PX_PER_M = 760.0
CLIP_Y = 1428
WATCH_Y = 1000.0
PAYOFF_Y = 1592.0


def hanging_positions(n: int, m: float, k: float, g: float, d: float) -> np.ndarray:
    """Depth of every coil below the top coil at rest, top coil at 0."""
    spacing = d + (n - 1 - np.arange(n - 1)) * m * g / k
    return np.concatenate([[0.0], np.cumsum(spacing)])


def simulate(n: int, mass: float, stiffness: float, d: float, g: float, dt: float,
             duration: float, record_every: int) -> dict:
    """Chain of n coils with inelastic pile-up. Returns recorded positions and events."""
    m = mass / n
    k = stiffness * (n - 1)
    x0 = hanging_positions(n, m, k, g, d)
    x = x0.copy()
    v = np.zeros(n)
    steps = int(round(duration / dt))
    rec_t, rec_x = [], []
    t_bottom_001 = None
    t_bottom_1 = None
    t_front = None
    top_at_front = None
    precursor = 0.0
    com_err = 0.0
    com0 = x0.mean()
    for s in range(steps + 1):
        t = s * dt
        if s % record_every == 0:
            rec_t.append(t)
            rec_x.append(x.copy())
        moved = x[-1] - x0[-1]
        if t_front is None:
            precursor = max(precursor, moved)
            if x[-1] - x[-2] < d + 1e-9:
                t_front = t
                top_at_front = x[0] - x0[0]
        if t_bottom_001 is None and moved > 1e-5:
            t_bottom_001 = t
        if t_bottom_1 is None and moved > 1e-3:
            t_bottom_1 = t
        com_err = max(com_err, abs((x.mean() - com0) - 0.5 * g * t * t))
        if s == steps:
            break
        ext = np.diff(x) - d
        f = k * ext
        a = np.full(n, g)
        a[:-1] += f / m
        a[1:] -= f / m
        v += a * dt
        x += v * dt
        gap = np.diff(x)
        if np.any(gap < d):
            i = 0
            while i < n - 1:
                if x[i + 1] - x[i] < d:
                    j = i + 1
                    while j < n - 1 and x[j + 1] - x[j] < d + 1e-12:
                        j += 1
                    cnt = j - i + 1
                    v[i:j + 1] = v[i:j + 1].mean()
                    c = x[i:j + 1].mean()
                    x[i:j + 1] = c + (np.arange(cnt) - (cnt - 1) / 2) * d
                    i = j + 1
                else:
                    i += 1
    return {"t": np.array(rec_t), "x": np.array(rec_x), "x0": x0, "length": float(x0[-1]),
            "t_bottom_001": t_bottom_001, "t_bottom_1": t_bottom_1, "t_front": t_front,
            "top_at_front": top_at_front, "precursor": precursor, "com_err": com_err,
            "m": m, "k": k, "n": n, "dt": dt}


def measure(man: dict) -> dict:
    n, mass, kt, d, g = man["coils"], man["mass_kg"], man["stiffness_n_per_m"], man["coil_gap_m"], man["g"]
    run = simulate(n, mass, kt, d, g, man["dt"], man["sim_duration"], man["record_every"])
    x0 = run["x0"]
    L = run["length"]
    print(f"slinky: {n} coils, {mass * 1000:.0f} g, whole-slinky stiffness {kt:g} N/m "
          f"({run['k']:.2f} N/m per coil spring), touching coils {d * 1000:.1f} mm apart; hanging at rest the "
          f"top two coils are {(x0[1] - x0[0]) * 1000:.1f} mm apart, the bottom two {(x0[-1] - x0[-2]) * 1000:.2f} mm; "
          f"hanging length {L:.3f} m; collapsed length {(n - 1) * d * 1000:.1f} mm; semi-implicit Euler at "
          f"{1 / man['dt']:.0f} steps per second, deterministic, no seed")
    tf = run["t_front"]
    print(f"bottom coil: first moves 0.01 mm at {run['t_bottom_001']:.4f} s and 1 mm at {run['t_bottom_1']:.4f} s "
          f"after release; the collapse front (the last stretched coil touching down) arrives at {tf:.4f} s; "
          f"before that the bottom coil moved at most {run['precursor'] * 1e6:.3f} um")
    top_fall = run["top_at_front"]
    print(f"top coil at the front's arrival: fell {top_fall:.3f} m of the {L:.3f} m hang "
          f"(average acceleration {2 * top_fall / (g * tf * tf):.2f} g); a body in free fall drops "
          f"{0.5 * g * tf * tf:.3f} m in {tf:.3f} s, so the rod's bottom has fallen {0.5 * g * tf * tf:.3f} m "
          f"when the slinky's bottom starts")
    print(f"check: centre of mass free fall, largest gap between the centre of mass drop and g t^2 / 2 over the run "
          f"{run['com_err'] * 1e6:.3f} um")
    fine = simulate(n, mass, kt, d, g, man["check_dt"], min(man["sim_duration"], 0.5), man["record_every"] * 2)
    print(f"check: half the step ({1 / man['check_dt']:.0f} per second): front at {fine['t_front']:.4f} s, "
          f"bottom coil 1 mm at {fine['t_bottom_1']:.4f} s, top fell {fine['top_at_front']:.3f} m")
    est = math.sqrt(2 * L / (3 * g))
    lin = (n - 1) * math.sqrt(run["m"] / run["k"])
    print(f"estimates: sqrt(2 L / 3 g) = {est:.4f} s; linear wave transit (n - 1) sqrt(m / k) = {lin:.4f} s "
          f"(the pile-up front outruns the linear wave)")
    for var in man["check_variants"]:
        r = simulate(var["coils"], mass, var["stiffness_n_per_m"], d, g, man["dt"], 0.7, man["record_every"] * 4)
        print(f"check: {var['coils']} coils at {var['stiffness_n_per_m']:g} N/m hang {r['length']:.3f} m; "
              f"front at {r['t_front']:.4f} s (sqrt(2 L / 3 g) = {math.sqrt(2 * r['length'] / (3 * g)):.4f} s), "
              f"top fell {r['top_at_front']:.3f} m, bottom moved at most {r['precursor'] * 1e6:.3f} um before it")
    rod_at_front = 0.5 * g * tf * tf
    return {"run": run, "length": L, "t_front": tf, "top_at_front": top_fall, "rod_at_front": rod_at_front}


def smoothstep(u: float) -> float:
    u = max(0.0, min(1.0, u))
    return u * u * (3 - 2 * u)


class Renderer:
    def __init__(self, man: dict, meas: dict):
        self.man, self.meas = man, meas
        self.fps = man["fps"]
        font = os.environ["SEED_ZERO_FONT"]
        self.font = ImageFont.truetype(font, 40)
        self.font_small = ImageFont.truetype(font, 32)
        self.font_title = ImageFont.truetype(font, 56)
        self.font_read = ImageFont.truetype(font, 44)
        self.font_watch = ImageFont.truetype(font, 64)
        self.first = None
        self.hanging = None
        run = meas["run"]
        self.rec_t, self.rec_x, self.x0 = run["t"], run["x"], run["x0"]
        self.rod_len = meas["length"]
        widths = {"overlay@34": (ImageFont.truetype(font, 34), man["overlay"])}
        for j, line in enumerate(man["title"].split("|")):
            widths[f"title line {j + 1}@56"] = (self.font_title, line)
        widths["label slinky@40"] = (self.font, "slinky")
        widths["label rod@40"] = (self.font, "solid rod, same length")
        widths["readout label@32"] = (self.font_small, "bottom moved")
        widths["readout@44"] = (self.font_read, "1234 mm")
        widths["watch@64"] = (self.font_watch, "0.000 s")
        widths["watch label@32"] = (self.font_small, "since the drop")
        for j, line in enumerate(self.payoff_lines()):
            widths[f"payoff line {j + 1}@40"] = (self.font, line)
        print("text widths: " + ", ".join(f"{k} {f.getlength(s):.0f} px" for k, (f, s) in widths.items()))

    def payoff_lines(self) -> list[str]:
        text = self.man["payoff_text"].format(t_front=self.meas["t_front"])
        return [s.strip() for s in text.split("|")]

    def state_at(self, s: float) -> np.ndarray:
        i = min(int(round(s / (self.rec_t[1] - self.rec_t[0]))), len(self.rec_t) - 1)
        return self.rec_x[i]

    def look_at(self, t: float):
        """Return (sim time or None when hanging, readouts flag, reset blend alpha)."""
        man = self.man
        fade = man["reset_fade"]
        for look in man["looks"]:
            if look["t0"] - 1.0 <= t < look["end"] + fade:
                s = max(0.0, (t - look["t0"]) * look["speed"])
                if look.get("freeze_at_crash"):
                    # Hold the crash frame, then let everything fall away.
                    s = min(s, self.meas["t_front"])
                    if t > look["hold_until"]:
                        s = self.meas["t_front"] + (t - look["hold_until"]) * look["resume_speed"]
                alpha = smoothstep((t - look["end"]) / fade) if t >= look["end"] else 0.0
                return s, look["readouts"], alpha
        return 0.0, False, 0.0

    def draw_scene(self, s: float, readouts: bool, title_on: bool) -> Image.Image:
        man = self.man
        g = man["g"]
        img = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(img)
        x = self.state_at(s)
        released = s > 0.0
        # Starting line of the bottoms.
        y_line = TOP_Y + self.x0[-1] * PX_PER_M
        for xx in range(150, 930, 24):
            d.line([(xx, y_line), (xx + 12, y_line)], fill=WIRE, width=2)
        # Slinky coils, teal while stretched, gold once piled up.
        px = PANELS["slinky"]["x"]
        rx = man["coil_radius_m"] * PX_PER_M
        ry = 9.0
        gap = np.diff(x)
        touching = gap < man["coil_gap_m"] + 1e-6
        for i in range(len(x) - 1, -1, -1):
            y = TOP_Y + x[i] * PX_PER_M
            if y - ry > CLIP_Y:
                continue
            piled = (i < len(x) - 1 and touching[i]) or (i > 0 and touching[i - 1])
            col = GOLD if piled else TEAL
            d.ellipse((px - rx, y - ry, px + rx, y + ry), outline=col, width=3)
        # Rod.
        rx_rod = 11.0
        px_r = PANELS["rod"]["x"]
        drop = 0.5 * g * s * s
        y_top = TOP_Y + drop * PX_PER_M
        y_bot = y_top + self.rod_len * PX_PER_M
        if y_top < CLIP_Y:
            d.rounded_rectangle((px_r - rx_rod, y_top, px_r + rx_rod, min(y_bot, CLIP_Y + 40)), radius=8, fill=CORAL)
        # Clamps while held.
        if not released:
            for cx in (px, px_r):
                d.rectangle((cx - 44, TOP_Y - 30, cx + 44, TOP_Y - 16), fill=CLAMP)
                d.rectangle((cx - 6, TOP_Y - 16, cx + 6, TOP_Y - 2), fill=CLAMP)
        # Bottom of the frame is clipped: things fall out of view.
        d.rectangle((0, CLIP_Y, W, H), fill=BG)
        if not title_on:
            d.text((px, LABEL_Y), "slinky", font=self.font, fill=TEAL, anchor="mm")
            d.text((px_r, LABEL_Y), "solid rod, same length", font=self.font, fill=CORAL, anchor="mm")
            if readouts:
                moved_s = (x[-1] - self.x0[-1]) * 1000
                moved_r = drop * 1000
                for cx, moved in ((px, moved_s), (px_r, moved_r)):
                    d.text((cx, READ_Y), "bottom moved", font=self.font_small, fill=MUTED, anchor="mm")
                    d.text((cx, VALUE_Y), f"{moved:.0f} mm", font=self.font_read, fill=TEXT, anchor="mm")
                d.text((W / 2, WATCH_Y), f"{s:.3f} s", font=self.font_watch, fill=TEXT, anchor="mm")
                d.text((W / 2, WATCH_Y + 50), "since the drop", font=self.font_small, fill=MUTED, anchor="mm")
        return img

    def live_frame(self, f: int) -> np.ndarray:
        man = self.man
        t = f / self.fps
        title_on = t < man["title_until"]
        s, readouts, alpha = self.look_at(t)
        img = self.draw_scene(s, readouts, title_on)
        d = ImageDraw.Draw(img)

        def shade_col(col, a):
            return tuple(int(c * a + BG[j] * (1 - a)) for j, c in enumerate(col))

        if title_on:
            a = 1.0 if t < man["title_until"] - 0.4 else (man["title_until"] - t) / 0.4
            for j, line in enumerate(man["title"].split("|")):
                d.text((W / 2, 176 + j * 62), line, font=self.font_title, fill=shade_col(TEXT, a), anchor="mm")
        if t >= man["payoff_t"]:
            a = min(1.0, (t - man["payoff_t"]) / man["payoff_hold"])
            for j, line in enumerate(self.payoff_lines()):
                d.text((W / 2, PAYOFF_Y + j * 56), line, font=self.font, fill=shade_col(GOLD, a), anchor="mm")
        out = np.asarray(img, dtype=np.float32)
        if alpha > 0.0:
            if self.hanging is None:
                self.hanging = np.asarray(self.draw_scene(0.0, False, False), dtype=np.float32)
            out = out * (1 - alpha) + self.hanging * alpha
        return out

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
    man = json.loads((ROOT / "projects/slinky/manifest.json").read_text())
    meas = measure(man)
    if "--measure-only" in sys.argv:
        return
    if "--frames" in sys.argv:
        times = [float(v) for v in sys.argv[sys.argv.index("--frames") + 1].split(",")]
        r = Renderer(man, meas)
        for tv in times:
            Image.fromarray(r.frame_at(int(round(tv * man["fps"])))).save(ROOT / f"media/slinky/smoke-{tv}.png")
        print("smoke frames: " + ", ".join(f"{tv}" for tv in times))
        return
    Renderer(man, meas).render(ROOT / "media/slinky/footage.mp4")


if __name__ == "__main__":
    main()
