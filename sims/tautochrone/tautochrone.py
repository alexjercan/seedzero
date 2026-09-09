#!/usr/bin/env python3
"""Tautochrone bowl: do they arrive together?

Two bowls of the same depth, five balls in each, released at the same
five heights. The top bowl is round (a circle arc). The bottom bowl is a
cycloid. Every ball obeys the same frictionless bead-on-a-wire equation,
s'' = -g dy/ds along the wire, integrated with RK4 at a fixed step; only
the bowl shape y(s) differs. The cycloid's period is set to exactly two
seconds so twenty periods fill the forty second short and the last frame
returns to the first.

Measured and printed: every bottom crossing of every ball, the spread of
the k-th crossing across the five balls in each bowl, each ball's period
against the closed forms (4 pi sqrt(a/g) for the cycloid, the elliptic
integral for the circle), the energy drift, and the loop closure error.

usage: tautochrone.py [--measure-only]
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
WIRE = (70, 80, 94)
BALLS = [(92, 200, 165), (90, 170, 230), (240, 176, 84), (232, 96, 88), (200, 140, 230)]
BALL_R = 15

# Layout: two panels, captions between them at caption_y 0.49 (y 941..1021).
PANELS = {"round": {"label_y": 214, "rim_y": 330}, "curve": {"label_y": 1104, "rim_y": 1220}}
PX_PER_M = 640.0
STRIP_H = 70
PAYOFF_Y = 1830.0


def agm_k(k: float) -> float:
    """Complete elliptic integral of the first kind K(k) by the AGM."""
    a, b = 1.0, math.sqrt(1.0 - k * k)
    while abs(a - b) > 1e-15:
        a, b = 0.5 * (a + b), math.sqrt(a * b)
    return math.pi / (2 * a)


class Bowl:
    """A wire y(s) with s the arc length from the bottom, y up."""

    def __init__(self, kind: str, size: float):
        self.kind, self.size = kind, size  # size = R for round, a for curve

    def y(self, s: float) -> float:
        if self.kind == "round":
            return self.size * (1.0 - math.cos(s / self.size))
        return s * s / (8.0 * self.size)

    def dyds(self, s: float) -> float:
        if self.kind == "round":
            return math.sin(s / self.size)
        return s / (4.0 * self.size)

    def s_at_height(self, h: float) -> float:
        if self.kind == "round":
            return self.size * math.acos(1.0 - h / self.size)
        return math.sqrt(8.0 * self.size * h)

    def xy(self, s: float) -> tuple[float, float]:
        """Metres: x from the bowl centre, y from the bottom (up)."""
        if self.kind == "round":
            return self.size * math.sin(s / self.size), self.y(s)
        a = self.size
        c = max(-1.0, min(1.0, -s / (4.0 * a)))
        th = 2.0 * math.acos(c)
        return a * (th - math.sin(th)) - math.pi * a, a * (1.0 + math.cos(th))

    def s_max(self) -> float:
        return self.size * math.pi / 2 if self.kind == "round" else 4.0 * self.size

    def exact_period(self, h: float, g: float) -> float:
        if self.kind == "round":
            phi0 = math.acos(1.0 - h / self.size)
            return 4.0 * math.sqrt(self.size / g) * agm_k(math.sin(phi0 / 2))
        return 4.0 * math.pi * math.sqrt(self.size / g)


def integrate(bowl: Bowl, s0: float, g: float, duration: float, fps: int, substeps: int):
    """RK4 on (s, v) with s'' = -g y'(s). Returns per-frame s, v and the
    interpolated bottom-crossing times."""
    dt = 1.0 / (fps * substeps)
    frames = int(round(duration * fps))
    s, v = s0, 0.0
    ss, vs, crossings = np.empty(frames), np.empty(frames), []

    def acc(x: float) -> float:
        return -g * bowl.dyds(x)

    for f in range(frames):
        ss[f], vs[f] = s, v
        for k in range(substeps):
            t = (f * substeps + k) * dt
            k1v, k1s = acc(s), v
            k2v, k2s = acc(s + 0.5 * dt * k1s), v + 0.5 * dt * k1v
            k3v, k3s = acc(s + 0.5 * dt * k2s), v + 0.5 * dt * k2v
            k4v, k4s = acc(s + dt * k3s), v + dt * k3v
            s_new = s + dt / 6.0 * (k1s + 2 * k2s + 2 * k3s + k4s)
            v_new = v + dt / 6.0 * (k1v + 2 * k2v + 2 * k3v + k4v)
            if (s < 0 <= s_new) or (s_new < 0 <= s) or (s == 0 and s_new != 0 and f + k > 0):
                if s != s_new:
                    crossings.append(t + dt * (0 - s) / (s_new - s))
            s, v = s_new, v_new
    energy0 = g * bowl.y(s0)
    energy_end = 0.5 * v * v + g * bowl.y(s)
    return ss, vs, np.array(crossings), abs(energy_end - energy0) / energy0


def measure(man: dict) -> dict:
    g, fps, sub = man["g"], man["fps"], man["substeps"]
    dur = man["scene_duration"]
    period_c = dur / man["curve_periods"]
    a = g * period_c ** 2 / (16 * math.pi ** 2)
    depth = 2.0 * a
    bowls = {"round": Bowl("round", depth), "curve": Bowl("curve", a)}
    heights = [frac * depth for frac in man["height_fractions"]]
    print(f"cycloid a = {a:.5f} m (period set to {period_c:.3f} s, {man['curve_periods']} periods in {dur:.0f} s); "
          f"round bowl radius = depth = {depth:.5f} m; g = {g}")
    print(f"round bowl {2 * depth:.3f} m wide, curved bowl {2 * math.pi * a:.3f} m wide, both {depth:.3f} m deep")
    print("heights (m): " + ", ".join(f"{h:.4f}" for h in heights))
    out = {"a": a, "depth": depth, "heights": heights, "period_c": period_c, "bowls": bowls, "balls": {}}
    for name, bowl in bowls.items():
        print(f"{name} bowl:")
        runs = []
        for i, h in enumerate(heights):
            s0 = bowl.s_at_height(h)
            ss, vs, cr, drift = integrate(bowl, s0, g, dur, fps, sub)
            exact = bowl.exact_period(h, g)
            periods = cr[2:] - cr[:-2]
            meas_period = float(periods.mean()) if len(periods) else float("nan")
            where = f"angle {math.degrees(s0 / bowl.size):.1f} deg" if name == "round" else f"{s0 / bowl.s_max():.3f} of the way to the cusp"
            print(f"  ball {i + 1} at {h:.4f} m (arc {s0:.4f} m, {where}): first bottom at {cr[0]:.4f} s, "
                  f"period {meas_period:.5f} s (exact {exact:.5f}), {len(cr)} crossings, energy drift {drift:.1e}")
            runs.append({"s0": s0, "s": ss, "v": vs, "cross": cr, "period": meas_period, "exact": exact})
        n = min(len(r["cross"]) for r in runs)
        spreads = np.array([max(r["cross"][k] for r in runs) - min(r["cross"][k] for r in runs) for k in range(n)])
        firsts = [r["cross"][0] for r in runs]
        print(f"  first arrival spread: {max(firsts) - min(firsts):.4f} s")
        show = [k for k in range(n) if k < 12 or (k + 1) % 10 == 0]
        print("  spread of the k-th crossing (max minus min over the five balls): "
              + ", ".join(f"{k + 1}: {spreads[k]:.3f} s" for k in show))
        print(f"  largest spread inside {n} common crossings: {spreads.max():.3f} s at crossing {int(spreads.argmax()) + 1}")
        out["balls"][name] = runs
        out[f"spread_{name}"] = spreads
    # Loop closure: the cycloid balls at the last frame versus the first.
    curve = out["balls"]["curve"]
    dt = 1.0 / fps
    err_s = max(abs(r["s"][-1] - r["s0"]) for r in curve)
    err_v = max(abs(r["v"][-1]) for r in curve)
    print(f"loop check: cycloid balls at the last frame (t = {dur - dt:.4f} s) are within {err_s * 1000:.3f} mm of their "
          f"marks with speed under {err_v * 1000:.3f} mm/s; at t = {dur:.0f} s they are back at rest on their marks")
    k = man["payoff_crossing"]
    out["payoff_round"] = float(out["spread_round"][k - 1])
    out["payoff_curve"] = float(out["spread_curve"][k - 1])
    print(f"payoff at crossing {k}: round {out['payoff_round']:.3f} s apart, curved {out['payoff_curve']:.3f} s apart")
    return out


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
        self.font_big = ImageFont.truetype(font, 56)
        self.font_title = ImageFont.truetype(font, 60)
        self.bowls = meas["bowls"]
        self.wire = {}
        for name, bowl in self.bowls.items():
            smax = bowl.s_max()
            pts = [self.px(name, *bowl.xy(s)) for s in np.linspace(-smax, smax, 400)]
            self.wire[name] = pts
        self.spreads = {name: meas[f"spread_{name}"] for name in self.bowls}

    def px(self, name: str, x: float, y: float) -> tuple[float, float]:
        rim = PANELS[name]["rim_y"]
        depth = self.meas["depth"]
        return W / 2 + x * PX_PER_M, rim + (depth - y) * PX_PER_M

    def ball_state(self, name: str, i: int, f: int, t: float):
        man = self.man
        run = self.meas["balls"][name][i]
        s, v = float(run["s"][f]), float(run["v"][f])
        if name == "round" and t >= man["reset_t"]:
            f0 = int(round(man["reset_t"] * self.fps))
            u = smoothstep((t - man["reset_t"]) / man["reset_dur"])
            s = float(run["s"][f0]) * (1 - u) + run["s0"] * u
        return s, v

    def frame_at(self, f: int) -> np.ndarray:
        man, m = self.man, self.meas
        t = f / self.fps
        img = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(img)
        resetting = t >= man["reset_t"]
        reset_u = smoothstep((t - man["reset_t"]) / man["reset_dur"]) if resetting else 0.0
        # The question is on screen while the balls sit on their marks: the
        # first seconds and the reset at the end, so the loop closes on it.
        if t < man["title_until"]:
            title_alpha = 1.0 if t < man["title_until"] - 0.4 else (man["title_until"] - t) / 0.4
            hud_alpha = 0.0
        elif resetting:
            title_alpha, hud_alpha = reset_u, 1.0 - reset_u
        else:
            title_alpha, hud_alpha = 0.0, 1.0

        def shade(col, alpha):
            return tuple(int(c * alpha + BG[j] * (1 - alpha)) for j, c in enumerate(col))

        for name, bowl in self.bowls.items():
            p = PANELS[name]
            label = "round bowl" if name == "round" else "curved bowl"
            if name == "curve" or title_alpha == 0:
                d.text((60, p["label_y"]), label, font=self.font, fill=TEAL, anchor="lm")
            # The wire and the bottom mark.
            d.line(self.wire[name], fill=WIRE, width=10, joint="curve")
            bx, by = self.px(name, 0.0, 0.0)
            d.line((bx, by + 8, bx, by + 30), fill=MUTED, width=4)
            # Release marks.
            for i, h in enumerate(m["heights"]):
                x, y = self.px(name, *bowl.xy(bowl.s_at_height(h)))
                d.ellipse((x - BALL_R - 4, y - BALL_R - 4, x + BALL_R + 4, y + BALL_R + 4), outline=BALLS[i], width=2)
            # Timeline strip: one row per ball, so crossings that coincide
            # line up as a column and crossings that differ stagger.
            strip_y = p["rim_y"] + m["depth"] * PX_PER_M + 60
            span = man["strip_seconds"]
            runs = m["balls"][name]
            t_cut = min(t, man["reset_t"]) if name == "round" else t
            if hud_alpha > 0.02:
                d.text((80, strip_y - 6), f"bottom crossings, last {span:.0f} seconds", font=self.font_small,
                       fill=shade(MUTED, hud_alpha), anchor="lb")
                for i, run in enumerate(runs):
                    ry = strip_y + 6 + i * 16
                    d.line((80, ry + 6, W - 80, ry + 6), fill=shade(WIRE, hud_alpha), width=1)
                    for tc in run["cross"]:
                        age = t - tc
                        if tc > t_cut or age > span:
                            continue
                        x = W - 80 - (age / span) * (W - 160)
                        d.line((x, ry, x, ry + 13), fill=shade(BALLS[i], hud_alpha), width=6)
            for i, run in enumerate(runs):
                for tc in run["cross"]:
                    age = t - tc
                    if tc > t_cut or age < 0 or age >= 0.35:
                        continue
                    r = BALL_R + 6 + 40 * age / 0.35
                    d.ellipse((bx - r, by - r, bx + r, by + r), outline=shade(BALLS[i], 1 - age / 0.35), width=3)
            # Balls.
            for i in range(len(runs)):
                s, _ = self.ball_state(name, i, f, t)
                x, y = self.px(name, *bowl.xy(s))
                d.ellipse((x - BALL_R, y - BALL_R, x + BALL_R, y + BALL_R), fill=BALLS[i])
            # Spread readout: the latest crossing all five balls have made.
            n_done = min(int(np.searchsorted(run["cross"], t_cut, side="right")) for run in runs)
            if hud_alpha > 0.02 and n_done:
                spread = self.spreads[name][n_done - 1]
                col = TEAL if name == "curve" else (GOLD if spread >= 0.1 else TEXT)
                d.text((W - 60, p["label_y"]), f"crossing {n_done}: {spread:.3f} s apart", font=self.font_small,
                       fill=shade(col, hud_alpha), anchor="rm")
            if name == "round" and resetting and reset_u < 0.98:
                d.text((W - 60, strip_y + 104), "reset", font=self.font_small, fill=shade(MUTED, 1 - reset_u), anchor="rm")
        if title_alpha > 0.02:
            d.text((W / 2, PANELS["round"]["label_y"]), man["title"], font=self.font_title, fill=shade(TEXT, title_alpha), anchor="mm")
        if man["payoff_t"] <= t < man["payoff_end"]:
            alpha = min(1.0, (t - man["payoff_t"]) / man["payoff_hold"], (man["payoff_end"] - t) / man["payoff_hold"])
            text = man["payoff_text"].format(k=man["payoff_crossing"], round=m["payoff_round"], curve=m["payoff_curve"])
            for j, line in enumerate(text.split("|")):
                d.text((W / 2, PAYOFF_Y + j * 64), line.strip(), font=self.font, fill=shade(GOLD, alpha), anchor="mm")
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
    man = json.loads((ROOT / "projects/tautochrone/manifest.json").read_text())
    meas = measure(man)
    if "--measure-only" in sys.argv:
        return
    Renderer(man, meas).render(ROOT / "media/tautochrone/footage.mp4")


if __name__ == "__main__":
    main()
