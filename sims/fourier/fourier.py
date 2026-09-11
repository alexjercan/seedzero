#!/usr/bin/env python3
"""Fourier square from circles: add more circles, does the bump go away?

Spinning circles chained end to end draw the Fourier partial sum of a square
wave of height 1:

    S_N(x) = (4 / pi) sum_{k=0}^{N-1} sin((2k + 1) x) / (2k + 1)

The k-th circle has radius (4 / pi) / (2k + 1) times the wave height and
turns 2k + 1 times per period, so the pen's height is exactly S_N. Measured
and printed: the highest point of S_N for 5, 50, 500 and 5,000 circles (the
Gibbs overshoot), where it sits after the jump, how wide the bump is, the
root-mean-square distance from the square, the limit (2 / pi) Si(pi), and
the on-screen text widths. The drawing is periodic, so five periods of eight
seconds loop exactly.

usage: fourier.py [--measure-only] [--frames t1,t2,...]
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
TARGET = (52, 60, 72)

PANELS = {"few": {"label_y": 330, "centre_y": 620}, "many": {"label_y": 1090, "centre_y": 1380}}
COLOURS = {"few": GOLD, "many": TEAL}
PAYOFF_Y = 1836.0
EXTRA_Y = 1650.0


def partial_sum(x: np.ndarray, n: int) -> np.ndarray:
    """S_N(x) evaluated term by term (exact, no FFT)."""
    out = np.zeros_like(x, dtype=np.float64)
    for k in range(n):
        m = 2 * k + 1
        out += np.sin(m * x) / m
    return out * 4.0 / math.pi


def peak_of(n: int) -> tuple[float, float]:
    """Highest point of S_N on (0, pi/N] by golden-section search; returns (x, value)."""
    lo, hi = 0.0, math.pi / n
    gr = (math.sqrt(5) - 1) / 2
    c, d = hi - gr * (hi - lo), lo + gr * (hi - lo)
    fc, fd = float(partial_sum(np.array([c]), n)[0]), float(partial_sum(np.array([d]), n)[0])
    for _ in range(200):
        if fc > fd:
            hi, d, fd = d, c, fc
            c = hi - gr * (hi - lo)
            fc = float(partial_sum(np.array([c]), n)[0])
        else:
            lo, c, fc = c, d, fd
            d = lo + gr * (hi - lo)
            fd = float(partial_sum(np.array([d]), n)[0])
    x = (lo + hi) / 2
    return x, float(partial_sum(np.array([x]), n)[0])


def bump_width(n: int, x_peak: float) -> float:
    """Distance from the jump to where S_N first comes back down to 1 after the peak."""
    xs = np.linspace(x_peak, 3 * math.pi / n, 20001)
    s = partial_sum(xs, n)
    i = int(np.argmax(s < 1.0))
    return float(xs[i])


def measure(man: dict) -> dict:
    grid = np.linspace(0, 2 * math.pi, 200001)[:-1]
    square = np.where(np.sin(grid) >= 0, 1.0, -1.0)
    # Wilbraham-Gibbs constant (2/pi) Si(pi) by Simpson quadrature.
    u = np.linspace(1e-12, math.pi, 200001)
    si = np.trapezoid(np.sin(u) / u, u)
    limit = 2 * si / math.pi
    print(f"square wave of height 1 as (4/pi) sum sin((2k+1)x)/(2k+1); one period drawn in {man['period_s']:g} s; "
          f"limit of the highest point for infinitely many circles: (2/pi) Si(pi) = {limit:.6f}, "
          f"{(limit - 1) * 100:.2f}% above the flat top; deterministic, no seed")
    results: dict[int, dict] = {}
    terms = list(man["circles"].values()) + list(man["check_terms"])
    for n in terms:
        xp, vp = peak_of(n)
        w = bump_width(n, xp)
        s = partial_sum(grid, n)
        rms = float(np.sqrt(np.mean((s - square) ** 2)))
        results[n] = {"x": xp, "peak": vp, "pct": (vp - 1) * 100, "width": w, "rms": rms}
        print(f"{n} circles (harmonics 1 to {2 * n - 1}): highest point {vp:.6f}, {(vp - 1) * 100:.2f}% above the flat top, "
              f"{xp / (2 * math.pi) * man['period_s'] * 1000:.1f} ms after the jump ({xp:.6f} rad); the bump is back at "
              f"the top level {w / (2 * math.pi) * man['period_s'] * 1000:.1f} ms after the jump; root-mean-square gap to "
              f"the square over a period {rms:.4f}")
    few, many = man["circles"]["few"], man["circles"]["many"]
    print(f"from {few} to {many} circles the bump got {results[few]['width'] / results[many]['width']:.1f}x thinner and "
          f"its height went from {results[few]['pct']:.2f}% to {results[many]['pct']:.2f}% above the top; "
          f"{man['check_terms'][-1]} circles: {results[man['check_terms'][-1]]['pct']:.2f}%")
    return {"results": results, "limit": limit}


class Renderer:
    def __init__(self, man: dict, meas: dict):
        self.man, self.meas = man, meas
        self.fps = man["fps"]
        font = os.environ["SEED_ZERO_FONT"]
        self.font = ImageFont.truetype(font, 40)
        self.font_small = ImageFont.truetype(font, 32)
        self.font_big = ImageFont.truetype(font, 56)
        self.font_title = ImageFont.truetype(font, 56)
        self.font_read = ImageFont.truetype(font, 48)
        self.first = None
        self.A = man["amplitude_px"]
        self.speed = man["px_per_period"] / man["period_s"]  # px per second of trace scroll
        widths = {"overlay@34": (ImageFont.truetype(font, 34), man["overlay"])}
        for j, line in enumerate(man["title"].split("|")):
            widths[f"title line {j + 1}@56"] = (self.font_title, line)
        for name, n in man["circles"].items():
            widths[f"label {name}@56"] = (self.font_big, f"{n} circles")
            widths[f"readout {name}@48"] = (self.font_read, self.readout(name))
        for j, line in enumerate(self.payoff_lines()):
            widths[f"payoff line {j + 1}@40"] = (self.font, line)
        for n, _ in man["extra_checks"]:
            widths[f"extra {n}@40"] = (self.font, f"{n:,} circles: peak {meas['results'][n]['pct']:.0f}% too high")
        print("text widths: " + ", ".join(f"{k} {f.getlength(s):.0f} px" for k, (f, s) in widths.items()))

    def readout(self, name: str) -> str:
        n = self.man["circles"][name]
        return f"peak {self.meas['results'][n]['pct']:.0f}% too high"

    def payoff_lines(self) -> list[str]:
        man, res = self.man, self.meas["results"]
        few, many, big = man["circles"]["few"], man["circles"]["many"], man["check_terms"][0]
        text = man["payoff_text"].format(few=few, many=many, big=big, few_pct=res[few]["pct"],
                                         many_pct=res[many]["pct"], big_pct=res[big]["pct"])
        return [s.strip() for s in text.split("|")]

    def draw_panel(self, d: ImageDraw.ImageDraw, name: str, t: float, title_on: bool) -> None:
        man = self.man
        n = man["circles"][name]
        p = PANELS[name]
        cy = p["centre_y"]
        col = COLOURS[name]
        T = man["period_s"]
        theta = 2 * math.pi * (t % T) / T
        A = self.A
        x0, x1 = man["trace_x0"], man["trace_x1"]
        # Target square wave and guide lines in the trace window.
        xs = np.arange(x0, x1 + 1, 2.0)
        ths = theta - (xs - x0) / self.speed * 2 * math.pi / T
        sq = np.where(np.sin(ths) >= 0, 1.0, -1.0)
        d.line([(float(x), cy - A * float(v)) for x, v in zip(xs, sq)], fill=TARGET, width=3)
        for x in np.arange(x0, x1, 14.0):
            d.line([(x, cy - A), (x + 7, cy - A)], fill=MUTED, width=2)
        peak = self.meas["results"][n]["peak"]
        for x in np.arange(x0, x1, 14.0):
            d.line([(x, cy - A * peak), (x + 7, cy - A * peak)], fill=col, width=2)
        # Trace of the pen: exact partial sum over the visible window.
        ys = partial_sum(ths, n)
        d.line([(float(x), cy - A * float(v)) for x, v in zip(xs, ys)], fill=col, width=4)
        # Epicycle chain.
        cx = man["chain_x"]
        px, py = cx, cy
        for k in range(n):
            m = 2 * k + 1
            r = 4.0 / math.pi * A / m
            nx, ny = px + r * math.cos(m * theta), py - r * math.sin(m * theta)
            if r >= 1.5:
                d.ellipse((px - r, py - r, px + r, py + r), outline=WIRE, width=2)
                d.line([(px, py), (nx, ny)], fill=MUTED if k else TEXT, width=2)
            px, py = nx, ny
        # Pen, connector to the trace, and the bump flash just after each rising edge.
        d.line([(px, py), (x0, py)], fill=self.blend(col, 0.5), width=2)
        d.ellipse((px - 7, py - 7, px + 7, py + 7), fill=col)
        d.ellipse((x0 - 8, py - 8, x0 + 8, py + 8), fill=TEXT)
        xp = self.meas["results"][n]["x"]
        t_peak = xp / (2 * math.pi) * T
        since = (t % T) - t_peak
        if 0 <= since < man["flash_seconds"]:
            a = 1.0 - since / man["flash_seconds"]
            rr = 16 + 30 * (1 - a)
            d.ellipse((x0 - rr, py - rr, x0 + rr, py + rr), outline=self.blend(col, a), width=4)
        # Labels.
        if not (name == "few" and title_on):
            d.text((60, p["label_y"]), f"{n} circles", font=self.font_big, fill=col, anchor="lm")
        d.text((W - 60, p["label_y"]), self.readout(name), font=self.font_read, fill=col, anchor="rm")

    @staticmethod
    def blend(col: tuple, alpha: float) -> tuple:
        return tuple(int(c * alpha + BG[j] * (1 - alpha)) for j, c in enumerate(col))

    def live_frame(self, f: int) -> Image.Image:
        man = self.man
        t = f / self.fps
        img = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(img)
        title_on = t < man["title_until"]
        for name in PANELS:
            self.draw_panel(d, name, t, title_on)
        if title_on:
            alpha = 1.0 if t < man["title_until"] - 0.4 else (man["title_until"] - t) / 0.4
            for j, line in enumerate(man["title"].split("|")):
                d.text((W / 2, 186 + j * 62), line, font=self.font_title, fill=self.blend(TEXT, alpha), anchor="mm")
        # Extra circle counts, shown as they are spoken, between the panels and the payoff.
        for j, (n, t_on) in enumerate(man["extra_checks"]):
            if t >= t_on:
                alpha = min(1.0, (t - t_on) / 0.4)
                pct = self.meas["results"][n]["pct"]
                d.text((W / 2, EXTRA_Y + j * 52), f"{n:,} circles: peak {pct:.0f}% too high", font=self.font,
                       fill=self.blend(TEXT, alpha), anchor="mm")
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
    man = json.loads((ROOT / "projects/fourier/manifest.json").read_text())
    meas = measure(man)
    if "--measure-only" in sys.argv:
        return
    if "--frames" in sys.argv:
        times = [float(v) for v in sys.argv[sys.argv.index("--frames") + 1].split(",")]
        r = Renderer(man, meas)
        for tv in times:
            Image.fromarray(r.frame_at(int(round(tv * man["fps"])))).save(ROOT / f"media/fourier/smoke-{tv}.png")
        print("smoke frames: " + ", ".join(f"{tv}" for tv in times))
        return
    Renderer(man, meas).render(ROOT / "media/fourier/footage.mp4")


if __name__ == "__main__":
    main()
