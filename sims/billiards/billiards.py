#!/usr/bin/env python3
"""Stadium versus circle billiards: two point balls launched delta degrees
apart on each table, exact event-driven reflection, measured gap over time.

Both tables get the same start point and the same pair of launch angles.
The circle is integrable, so the gap between its two balls grows at most
linearly with the bounce count. The Bunimovich stadium is chaotic, so its
gap grows exponentially until the balls are on opposite sides. There is no
time step: each ball moves in straight legs from one exact hit to the next,
and the gap is sampled from those exact legs.

usage: billiards.py [--measure-only]
"""

from __future__ import annotations

import json
import math
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent.parent
W, H = 1080, 1920

BG = (11, 14, 18)
COL_A = (92, 200, 165)
COL_B = (216, 222, 230)
GOLD = (240, 176, 84)
TEXT = (216, 222, 230)
MUTED = (138, 148, 163)
OUTLINE = (96, 110, 128)
GRIDLINE = (40, 48, 58)

SCALE = 500.0  # px per metre
CIRCLE_C = (540.0, 470.0)
STADIUM_C = (540.0, 1050.0)
CHART_X0, CHART_X1 = 150, 1000
CHART_Y0, CHART_Y1 = 1500, 1800
PAYOFF_Y = 1875
BALL_PX = 14
EPS = 1e-9


def ray_circle(p: np.ndarray, d: np.ndarray, c: np.ndarray, r: float) -> list[float]:
    q = p - c
    b = float(q @ d)
    cc = float(q @ q) - r * r
    disc = b * b - cc
    if disc < 0:
        return []
    s = math.sqrt(disc)
    return [-b - s, -b + s]


class Circle:
    name = "round"

    def __init__(self, r: float):
        self.r = r
        self.c = np.zeros(2)

    def hit(self, p: np.ndarray, d: np.ndarray):
        best = None
        for t in ray_circle(p, d, self.c, self.r):
            if t > EPS and (best is None or t < best):
                best = t
        assert best is not None, "ball escaped the circle"
        hit = p + best * d
        return best, (hit - self.c) / self.r

    def inside(self, p: np.ndarray) -> bool:
        return float(np.hypot(*p)) <= self.r + 1e-7


class Stadium:
    name = "stadium"

    def __init__(self, r: float, straight: float):
        self.r = r
        self.half = straight / 2.0
        self.cr = np.array([self.half, 0.0])
        self.cl = np.array([-self.half, 0.0])

    def hit(self, p: np.ndarray, d: np.ndarray):
        cands = []
        if d[1] > 0:
            t = (self.r - p[1]) / d[1]
            if t > EPS and abs(p[0] + t * d[0]) <= self.half:
                cands.append((t, np.array([0.0, 1.0])))
        if d[1] < 0:
            t = (-self.r - p[1]) / d[1]
            if t > EPS and abs(p[0] + t * d[0]) <= self.half:
                cands.append((t, np.array([0.0, -1.0])))
        for c, sign in ((self.cr, 1.0), (self.cl, -1.0)):
            for t in ray_circle(p, d, c, self.r):
                if t > EPS:
                    hit = p + t * d
                    if sign * (hit[0] - c[0]) >= -1e-12:
                        cands.append((t, (hit - c) / self.r))
        assert cands, "ball escaped the stadium"
        return min(cands, key=lambda x: x[0])

    def inside(self, p: np.ndarray) -> bool:
        x = min(max(p[0], -self.half), self.half)
        return float(np.hypot(p[0] - x, p[1])) <= self.r + 1e-7


class Ball:
    def __init__(self, table, p, angle_rad: float):
        self.table = table
        self.p = np.array(p, dtype=float)
        self.d = np.array([math.cos(angle_rad), math.sin(angle_rad)])
        self.t = 0.0
        self.bounces = 0
        self.angles: list[float] = []  # angle between path and wall at each hit, degrees

    def advance_to(self, T: float, speed: float, corners: list | None = None) -> None:
        while True:
            dist, n = self.table.hit(self.p, self.d)
            t_hit = self.t + dist / speed
            if t_hit > T:
                break
            self.p = self.p + self.d * dist
            self.angles.append(math.degrees(math.asin(min(1.0, abs(float(self.d @ n))))))
            self.d = self.d - 2.0 * float(self.d @ n) * n
            self.d /= float(np.hypot(*self.d))
            self.t = t_hit
            self.bounces += 1
            if corners is not None:
                corners.append(self.p.copy())
        self.p = self.p + self.d * (speed * (T - self.t))
        self.t = T


def make_tables(man: dict):
    return Circle(man["radius"]), Stadium(man["radius"], man["straight"])


def simulate(man: dict, delta_deg: float, angle_deg: float, T: float, rate: int):
    """Sample the gap on both tables every 1/rate seconds. Returns dict of arrays."""
    circle, stadium = make_tables(man)
    a0 = math.radians(angle_deg)
    a1 = math.radians(angle_deg + delta_deg)
    balls = {
        "round": (Ball(circle, man["start"], a0), Ball(circle, man["start"], a1)),
        "stadium": (Ball(stadium, man["start"], a0), Ball(stadium, man["start"], a1)),
    }
    n = int(round(T * rate))
    times = np.arange(n + 1) / rate
    out = {"t": times}
    for name, (a, b) in balls.items():
        gaps = np.empty(n + 1)
        bounces = np.empty(n + 1, dtype=int)
        for i, t in enumerate(times):
            a.advance_to(float(t), man["speed"])
            b.advance_to(float(t), man["speed"])
            assert a.table.inside(a.p) and b.table.inside(b.p)
            gaps[i] = float(np.hypot(*(a.p - b.p)))
            bounces[i] = a.bounces
        out[name] = {"gap": gaps, "bounces": bounces, "b_bounces": b.bounces,
                     "angles_a": a.angles, "angles_b": b.angles}
    return out


def first_cross(t: np.ndarray, gap: np.ndarray, level: float):
    idx = np.nonzero(gap > level)[0]
    return None if len(idx) == 0 else float(t[idx[0]])


def fit_exponential(t, gap, bounces, lo: float, hi: float):
    """Fit ln(gap) against time and against bounces from the first sample
    above lo to the first sample above hi (the growth phase only)."""
    above_lo = np.nonzero(gap > lo)[0]
    above_hi = np.nonzero(gap > hi)[0]
    if len(above_lo) == 0 or len(above_hi) == 0:
        return None
    i0, i1 = int(above_lo[0]), int(above_hi[0])
    if i1 - i0 < 10:
        return None
    tt = t[i0:i1 + 1]
    lg = np.log(gap[i0:i1 + 1])
    slope_t, icpt_t = np.polyfit(tt, lg, 1)
    resid_t = np.max(np.abs(lg - (slope_t * tt + icpt_t)))
    bb = bounces[i0:i1 + 1].astype(float)
    slope_b, icpt_b = np.polyfit(bb, lg, 1)
    return {
        "t0": float(tt[0]), "t1": float(tt[-1]),
        "per_s": float(slope_t), "double_s": float(math.log(2) / slope_t),
        "resid_log": float(resid_t),
        "per_bounce": float(slope_b), "double_bounces": float(math.log(2) / slope_b),
        "b0": int(bounces[i0]), "b1": int(bounces[i1]),
    }


def fmt_gap(g: float) -> str:
    mm = g * 1000.0
    if mm < 1.0:
        return f"{mm:.3f} mm"
    if mm < 100.0:
        return f"{mm:.1f} mm"
    return f"{g:.2f} m"


def measure(man: dict) -> dict:
    T = man["scene_duration"]
    rate = 240
    res = simulate(man, man["delta_deg"], man["angle_deg"], T, rate)
    t = res["t"]
    print(f"tables: circle radius {man['radius']} m; stadium radius {man['radius']} m with "
          f"{man['straight']} m straights ({2 * man['radius'] + man['straight']:.1f} m long)")
    print(f"start {man['start']} m, launch angle {man['angle_deg']} deg, second ball "
          f"+{man['delta_deg']} deg ({math.radians(man['delta_deg']):.3e} rad), speed {man['speed']} m/s, "
          f"{T:.0f} s, gap sampled at {rate} Hz from exact legs")
    levels = (1e-4, 1e-3, 1e-2, 2 * BALL_PX / SCALE, 0.1, 0.25, 0.5, 1.0)
    summary = {}
    for name in ("round", "stadium"):
        gap, bounces = res[name]["gap"], res[name]["bounces"]
        print(f"{name}: ball A {bounces[-1]} bounces, ball B {res[name]['b_bounces']} bounces in {T:.0f} s")
        for s in (1, 2, 5, 10, 15, 20, 25, 30, 40):
            if s <= T:
                i = int(round(s * rate))
                print(f"  gap at {s:2d} s: {fmt_gap(gap[i])} ({gap[i]:.3e} m), {bounces[i]} bounces")
        for lv in levels:
            tc = first_cross(t, gap, lv)
            label = f"{lv:g} m"
            if lv == 2 * BALL_PX / SCALE:
                label = f"{lv:.3f} m (one ball width on screen)"
            print(f"  first gap above {label}: " + ("never" if tc is None else f"{tc:.2f} s, {bounces[int(round(tc * rate))]} bounces"))
        imax = int(np.argmax(gap))
        print(f"  max gap {fmt_gap(gap[imax])} ({gap[imax]:.4e} m) at {t[imax]:.2f} s")
        running = np.maximum.accumulate(gap)
        print("  widest gap so far at " + ", ".join(f"{s} s: {fmt_gap(running[int(round(s * rate))])}"
                                                 for s in range(30, int(T) + 1, 2)))
        ang = np.array(res[name]["angles_a"])
        print(f"  ball A hit angle against the wall: min {ang.min():.6f} deg, max {ang.max():.6f} deg, "
              f"spread {ang.max() - ang.min():.2e} deg over {len(ang)} hits")
        summary[name] = {"end_gap": float(gap[-1]), "max_gap": float(gap[imax]), "bounces": int(bounces[-1])}
    # Circle: linear growth of the gap envelope per bounce.
    gap_c, b_c = res["round"]["gap"], res["round"]["bounces"]
    env_b, env_g = [], []
    for k in range(1, int(b_c[-1]) + 1):
        m = b_c == k
        if m.any():
            env_b.append(k)
            env_g.append(float(gap_c[m].max()))
    slope, icpt = np.polyfit(env_b, env_g, 1)
    print(f"  round table linear fit of per-bounce max gap: {1000 * slope:.4f} mm per bounce, "
          f"intercept {1000 * icpt:.4f} mm, max residual {1000 * np.max(np.abs(np.array(env_g) - (slope * np.array(env_b) + icpt))):.4f} mm")
    # Stadium: exponential fit before saturation.
    fit = fit_exponential(t, res["stadium"]["gap"], res["stadium"]["bounces"], 1e-4, 0.05)
    assert fit is not None
    print(f"  stadium exponential fit over gap 0.1 mm to 5 cm ({fit['t0']:.2f} s to {fit['t1']:.2f} s, "
          f"bounces {fit['b0']} to {fit['b1']}): {fit['per_s']:.3f} per second, gap doubles every "
          f"{fit['double_s']:.2f} s; {fit['per_bounce']:.3f} per bounce, doubles every {fit['double_bounces']:.2f} bounces; "
          f"max log residual {fit['resid_log']:.2f}")
    # Growth-law check: is the doubling time a property of the table, not of the nudge?
    print("nudge check (stadium doubling time and split time for other nudges and angles):")
    for delta, angle in ((0.0005, man["angle_deg"]), (0.002, man["angle_deg"]),
                         (0.001, man["angle_deg"] - 7.0), (0.001, man["angle_deg"] + 5.0)):
        r2 = simulate(man, delta, angle, T, rate)
        f2 = fit_exponential(r2["t"], r2["stadium"]["gap"], r2["stadium"]["bounces"], 1e-4, 0.05)
        tc = first_cross(r2["t"], r2["stadium"]["gap"], 2 * BALL_PX / SCALE)
        t1 = first_cross(r2["t"], r2["stadium"]["gap"], 1.0)
        gc = r2["round"]["gap"]
        print(f"  delta {delta} deg, angle {angle} deg: doubles every {f2['double_bounces']:.2f} bounces "
              f"({f2['double_s']:.2f} s, log residual {f2['resid_log']:.2f}), one ball width at {tc:.2f} s, one metre at "
              f"{'never' if t1 is None else f'{t1:.2f} s'}; round table max gap {fmt_gap(gc.max())}")
    gs = res["stadium"]["gap"]
    im = int(round(first_cross(t, gs, 1.0) * rate))
    print(f"  stadium gap after the one metre crossing: min {fmt_gap(gs[im:].min())} at {t[im + int(np.argmin(gs[im:]))]:.2f} s")
    split_t = first_cross(t, res["stadium"]["gap"], 2 * BALL_PX / SCALE)
    metre_t = first_cross(t, res["stadium"]["gap"], 1.0)
    return {"res": res, "fit": fit, "split_t": split_t, "metre_t": metre_t, "summary": summary}


def px(table_c, p) -> tuple[float, float]:
    return table_c[0] + p[0] * SCALE, table_c[1] - p[1] * SCALE


class Renderer:
    def __init__(self, man: dict, meas: dict):
        self.man, self.meas = man, meas
        self.fps = man["fps"]
        self.sub = man["substeps"]
        font = os.environ["SEED_ZERO_FONT"]
        self.font = ImageFont.truetype(font, 40)
        self.font_small = ImageFont.truetype(font, 32)
        self.font_tiny = ImageFont.truetype(font, 26)
        circle, stadium = make_tables(man)
        a0 = math.radians(man["angle_deg"])
        a1 = math.radians(man["angle_deg"] + man["delta_deg"])
        self.balls = [
            (CIRCLE_C, Ball(circle, man["start"], a0), COL_A),
            (CIRCLE_C, Ball(circle, man["start"], a1), COL_B),
            (STADIUM_C, Ball(stadium, man["start"], a0), COL_A),
            (STADIUM_C, Ball(stadium, man["start"], a1), COL_B),
        ]
        self.trail = Image.new("RGB", (W, H), (0, 0, 0))
        fade = man["trail_fade"]
        self.lut = [int(v * fade) for v in range(256)] * 3
        self.gap_hist = {"round": [], "stadium": []}
        self.widest = {"round": 0.0, "stadium": 0.0}
        self.payoff_card = None
        self.prefill()

    def trail_color(self, col):
        return tuple(int(c * 0.8) for c in col)

    def prefill(self) -> None:
        """Give the first frame real history: run each ball backwards for
        trail_seconds and replay those legs into the fading trail buffer."""
        man = self.man
        n = int(man["trail_seconds"] * self.fps * self.sub)
        dt = 1.0 / (self.fps * self.sub)
        paths = []
        for table_c, ball, col in self.balls:
            back = Ball(ball.table, ball.p, 0.0)
            back.d = -ball.d.copy()
            pts = [ball.p.copy()]
            for _ in range(n):
                corners: list = []
                back.advance_to(back.t + dt, man["speed"], corners)
                pts.extend(corners)
                pts.append(back.p.copy())
            paths.append((table_c, list(reversed(pts)), col))
        # Replay oldest to newest with the same decay as the live render.
        counts = [len(p[1]) for p in paths]
        steps = max(counts)
        d = ImageDraw.Draw(self.trail)
        for k in range(1, steps):
            self.trail = self.trail.point(self.lut)
            d = ImageDraw.Draw(self.trail)
            for table_c, pts, col in paths:
                if k < len(pts):
                    d.line([px(table_c, pts[k - 1]), px(table_c, pts[k])],
                           fill=self.trail_color(col), width=4)

    def step(self, t_end: float) -> None:
        man = self.man
        dt = 1.0 / (self.fps * self.sub)
        for _ in range(self.sub):
            self.trail = self.trail.point(self.lut)
            d = ImageDraw.Draw(self.trail)
            for table_c, ball, col in self.balls:
                start = ball.p.copy()
                corners: list = []
                ball.advance_to(ball.t + dt, man["speed"], corners)
                pts = [start] + corners + [ball.p.copy()]
                d.line([px(table_c, p) for p in pts], fill=self.trail_color(col), width=4)

    def gap(self, name: str) -> float:
        i = 0 if name == "round" else 2
        return float(np.hypot(*(self.balls[i][1].p - self.balls[i + 1][1].p)))

    def frame_at(self, f: int) -> np.ndarray:
        man = self.man
        t = f / self.fps
        if f > 0:
            self.step(t)
        for name in ("round", "stadium"):
            self.gap_hist[name].append((t, self.gap(name)))
            self.widest[name] = max(self.widest[name], self.gap(name))

        img = Image.new("RGB", (W, H), BG)
        img = ImageChops.add(img, self.trail)
        d = ImageDraw.Draw(img)
        r = man["radius"] * SCALE
        half = man["straight"] / 2 * SCALE
        # Outlines.
        cx, cy = CIRCLE_C
        d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=OUTLINE, width=4)
        sx, sy = STADIUM_C
        d.line((sx - half, sy - r, sx + half, sy - r), fill=OUTLINE, width=4)
        d.line((sx - half, sy + r, sx + half, sy + r), fill=OUTLINE, width=4)
        d.arc((sx + half - r, sy - r, sx + half + r, sy + r), start=-90, end=90, fill=OUTLINE, width=4)
        d.arc((sx - half - r, sy - r, sx - half + r, sy + r), start=90, end=270, fill=OUTLINE, width=4)
        # Balls: A under B so an overlap reads as one ball.
        for table_c, ball, col in self.balls:
            x, y = px(table_c, ball.p)
            d.ellipse((x - BALL_PX, y - BALL_PX, x + BALL_PX, y + BALL_PX), fill=col)
        # Labels and readouts: two lines above each table.
        for name, table_c, y, i in (("round table", CIRCLE_C, cy - r - 70, 0), ("stadium", STADIUM_C, sy - r - 55, 2)):
            key = "round" if i == 0 else "stadium"
            ball_a = self.balls[i][1]
            gap = self.gap(key)
            split_col = GOLD if (i == 2 and gap > 2 * BALL_PX / SCALE) else MUTED
            d.text((60, y), name, font=self.font, fill=TEXT, anchor="lm")
            last = f"hit angle {ball_a.angles[-1]:.1f} deg  |  " if ball_a.angles else ""
            d.text((1020, y), f"{last}{ball_a.bounces} bounces", font=self.font_small, fill=MUTED, anchor="rm")
            d.text((1020, y + 36), f"gap {fmt_gap(gap)}  |  widest {fmt_gap(self.widest[key])}",
                   font=self.font_small, fill=split_col, anchor="rm")
        # Chart: gap on a log scale against time, both tables.
        d.rectangle((CHART_X0, CHART_Y0, CHART_X1, CHART_Y1), outline=GRIDLINE, width=2)
        d.text((CHART_X0, CHART_Y0 - 28), "gap between the two balls", font=self.font_small, fill=MUTED, anchor="lm")
        d.text((CHART_X1, CHART_Y1 + 26), f"{man['scene_duration']:.0f} s", font=self.font_small, fill=MUTED, anchor="rm")
        d.text((CHART_X0, CHART_Y1 + 26), "0 s", font=self.font_small, fill=MUTED, anchor="lm")
        g_lo, g_hi = 1e-6, 2.0

        def cy_of(g: float) -> float:
            g = min(max(g, g_lo), g_hi)
            return CHART_Y1 - (CHART_Y1 - CHART_Y0) * (math.log10(g) - math.log10(g_lo)) / (math.log10(g_hi) - math.log10(g_lo))

        def cx_of(tt: float) -> float:
            return CHART_X0 + (CHART_X1 - CHART_X0) * tt / man["scene_duration"]

        for g, label in ((1e-3, "1 mm"), (1e-2, "1 cm"), (1e-1, "10 cm"), (1.0, "1 m")):
            y = cy_of(g)
            d.line((CHART_X0, y, CHART_X1, y), fill=GRIDLINE, width=1)
            d.text((CHART_X0 - 12, y), label, font=self.font_tiny, fill=MUTED, anchor="rm")
        for name, col in (("round", COL_A), ("stadium", GOLD)):
            pts = [(cx_of(tt), cy_of(g)) for tt, g in self.gap_hist[name] if g > 0]
            if len(pts) > 1:
                d.line(pts, fill=col, width=4)
            if pts:
                # Keep the label inside the frame when the curve reaches the right edge.
                lx = min(pts[-1][0] + 10, W - 12 - d.textlength(name, font=self.font_tiny))
                d.text((lx, pts[-1][1]), name, font=self.font_tiny, fill=col, anchor="lm")
        # Payoff: the widest gaps at payoff_t, frozen into the card.
        if t >= man["payoff_t"]:
            if self.payoff_card is None:
                self.payoff_card = (f"{man['payoff_t']:.0f} s. round: {fmt_gap(self.widest['round'])}. "
                                    f"stadium: {fmt_gap(self.widest['stadium'])}")
            alpha = min(1.0, (t - man["payoff_t"]) / man["payoff_hold"])
            shade = tuple(int(c * alpha + BG[i] * (1 - alpha)) for i, c in enumerate(GOLD))
            d.text((W / 2, PAYOFF_Y), self.payoff_card, font=self.font, fill=shade, anchor="mm")
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
    man = json.loads((ROOT / "projects/billiards/manifest.json").read_text())
    meas = measure(man)
    if "--measure-only" in sys.argv:
        return
    Renderer(man, meas).render(ROOT / "media/billiards/footage.mp4")


if __name__ == "__main__":
    main()
