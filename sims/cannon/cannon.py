#!/usr/bin/env python3
"""Galilean cannon: drop a tennis ball on a basketball, how high does it fly?

Two panels, the same tennis ball dropped from the same height (its bottom
one metre above the floor). Left: the tennis ball alone. Right: the tennis
ball resting on a basketball. Every ball moves in one dimension under
gravity; the floor and the balls bounce perfectly (elastic, no air, no spin).
The motion is event driven: between collisions every ball follows the exact
parabola, the time to the next floor hit or ball contact is solved in closed
form, and a collision swaps velocities by the one-dimensional elastic rule.
No seed: the run is deterministic.

Measured and printed: the floor-hit speed, the speed of each ball after the
ball-to-ball hit against the closed-form elastic result, the peak height of
the tennis ball's bottom in both panels and the time of that peak, the
number of collisions, the energy drift, the same stack with lossy bounces
for the description, other mass ratios and the heavy-ball limit, a third
ball on top, and the on-screen text widths.

usage: cannon.py [--measure-only] [--frames t1,t2,...]
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
FLOOR = (52, 60, 72)

# Layout: two panels side by side, a shared height ruler on the left,
# captions in the band at caption_y 0.75 (y 1440..1510), payoff under it.
PANELS = {"alone": {"x": 360.0, "label": "alone"}, "stack": {"x": 800.0, "label": "on a basketball"}}
COLOURS = {"tennis": TEAL, "basketball": GOLD, "third": CORAL}
LABEL_Y = 236
READ_Y = 290
VALUE_Y = 338
FLOOR_Y = 1380.0
RULER_X = 96
TOP_LIMIT = 400.0
PAYOFF_Y = 1592.0
MARKER_R = 24


def simulate(balls: list[dict], g: float, duration: float, rate: int, restitution: float = 1.0) -> dict:
    """Event-driven bounce of stacked balls. balls: bottom-up list of {r, m, h, v} (h = bottom height)."""
    n = len(balls)
    h = np.array([b["h"] for b in balls], dtype=float)
    v = np.array([b["v"] for b in balls], dtype=float)
    r = np.array([b["r"] for b in balls], dtype=float)
    m = np.array([b["m"] for b in balls], dtype=float)
    e = restitution
    t = 0.0
    samples_t = np.arange(0.0, duration + 0.5 / rate, 1.0 / rate)
    samples = np.empty((len(samples_t), n))
    si = 0
    events: list[tuple[float, str, int, np.ndarray, np.ndarray]] = []

    def energy() -> float:
        return float(np.sum(0.5 * m * v * v + m * g * (h + r)))

    E0 = energy()
    dE = 0.0
    while True:
        # Next floor hit of ball 0 (the only one that can reach the floor).
        cand = []
        if n:
            a, b, c = -0.5 * g, v[0], h[0]
            disc = b * b - 4 * a * c
            if disc >= 0:
                for root in ((-b + math.sqrt(disc)) / (2 * a), (-b - math.sqrt(disc)) / (2 * a)):
                    if root > 1e-12:
                        cand.append((root, "floor", 0))
        for i in range(n - 1):
            gap = h[i + 1] - (h[i] + 2 * r[i])
            closing = v[i] - v[i + 1]
            if closing > 0:
                dt = gap / closing
                if dt >= 0:
                    cand.append((max(dt, 0.0), "ball", i))
        if not cand:
            dt, kind, idx = duration - t, "end", -1
        else:
            dt, kind, idx = min(cand, key=lambda c: c[0])
        if t + dt > duration:
            dt, kind = duration - t, "end"
        # Sample the parabolas up to the event.
        while si < len(samples_t) and samples_t[si] <= t + dt + 1e-12:
            tau = samples_t[si] - t
            samples[si] = h + v * tau - 0.5 * g * tau * tau
            si += 1
        h = h + v * dt - 0.5 * g * dt * dt
        v = v - g * dt
        t += dt
        if kind == "end":
            break
        before = v.copy()
        if kind == "floor":
            h[0] = 0.0
            v[0] = -e * v[0]
        else:
            i = idx
            h[i + 1] = h[i] + 2 * r[i]
            m1, m2, u1, u2 = m[i], m[i + 1], v[i], v[i + 1]
            v[i] = (m1 * u1 + m2 * u2 - m2 * e * (u1 - u2)) / (m1 + m2)
            v[i + 1] = (m1 * u1 + m2 * u2 + m1 * e * (u1 - u2)) / (m1 + m2)
        events.append((t, kind, idx, before, v.copy()))
        if e == 1.0:
            dE = max(dE, abs(energy() - E0) / E0)
    return {"t": samples_t, "h": samples, "r": r, "m": m, "events": events, "dE": dE}


def peak(run: dict, ball: int, ev: tuple, g: float) -> tuple[float, float]:
    """Peak of the flight that starts at the event ev: closed form, checked against the samples."""
    t_from = ev[0]
    h_ev = run["h"][np.searchsorted(run["t"], t_from)]  # first sample at or after the event
    v = ev[4][ball]
    t_peak = t_from + v / g
    # Height at the event from the sample just after it, run back to the event time.
    tau = float(run["t"][np.searchsorted(run["t"], t_from)]) - t_from
    h0 = float(h_ev[ball]) - v * tau + 0.5 * g * tau * tau
    h_peak = h0 + v * v / (2 * g)
    window = (run["t"] >= t_from) & (run["t"] <= t_from + 2 * v / g)
    sampled = float(run["h"][window, ball].max())
    assert abs(sampled - h_peak) < 1e-4, (sampled, h_peak)
    return h_peak, t_peak


def stack_balls(man: dict, third: dict | None = None) -> list[dict]:
    bb, tb = man["balls"]["basketball"], man["balls"]["tennis"]
    hd = man["drop_height"]
    balls = [{"r": bb["radius"], "m": bb["mass"], "h": hd - 2 * bb["radius"], "v": 0.0},
             {"r": tb["radius"], "m": tb["mass"], "h": hd, "v": 0.0}]
    if third is not None:
        balls.append({"r": third["radius"], "m": third["mass"], "h": hd + 2 * tb["radius"], "v": 0.0})
    return balls


def measure(man: dict) -> dict:
    g, rate, dur = man["g"], man["sample_rate"], man["sim_duration"]
    bb, tb = man["balls"]["basketball"], man["balls"]["tennis"]
    hd = man["drop_height"]
    print(f"balls: basketball radius {bb['radius'] * 100:.0f} cm, {bb['mass'] * 1000:.0f} g; tennis ball radius "
          f"{tb['radius'] * 100:.1f} cm, {tb['mass'] * 1000:.0f} g; mass ratio {bb['mass'] / tb['mass']:.2f}; "
          f"the tennis ball's bottom starts {hd:.2f} m above the floor in both panels, the basketball's bottom "
          f"{hd - 2 * bb['radius']:.2f} m; perfect bounces, no air; event driven, exact parabolas, no seed")
    alone = simulate([{"r": tb["radius"], "m": tb["mass"], "h": hd, "v": 0.0}], g, dur, rate)
    stack = simulate(stack_balls(man), g, dur, rate)
    fl = [ev for ev in alone["events"] if ev[1] == "floor"]
    pa, ta = peak(alone, 0, fl[0], g)
    print(f"alone: hits the floor at {fl[0][0]:.4f} s at {abs(fl[0][3][0]):.3f} m/s, back to a peak of {pa:.4f} m at "
          f"{ta:.3f} s, then every {2 * (ta - fl[0][0]):.3f} s; {len(alone['events'])} floor hits in {dur:g} s; "
          f"energy drift {alone['dE']:.1e}")
    ev = stack["events"]
    floor1 = next(e_ for e_ in ev if e_[1] == "floor")
    hit1 = next(e_ for e_ in ev if e_[1] == "ball")
    v_in = abs(floor1[3][0])
    M, mm = bb["mass"], tb["mass"]
    v_t_formula = v_in * (3 * M - mm) / (M + mm)
    v_b_formula = v_in * (M - 3 * mm) / (M + mm)
    ps, ts = peak(stack, 1, hit1, g)
    pb, tb_ = peak(stack, 0, hit1, g)
    print(f"stack: both fall together and the basketball hits the floor at {floor1[0]:.4f} s at {v_in:.3f} m/s; it "
          f"bounces up into the tennis ball still coming down at {abs(hit1[3][1]):.3f} m/s; after the hit the tennis "
          f"ball goes up at {hit1[4][1]:.3f} m/s (closed form (3M - m)/(M + m) v = {v_t_formula:.3f}) and the "
          f"basketball at {hit1[4][0]:.3f} m/s (closed form (M - 3m)/(M + m) v = {v_b_formula:.3f}, "
          f"{hit1[4][0] / v_in * 100:.0f}% of its bounce speed)")
    print(f"stack: the tennis ball's bottom peaks at {ps:.4f} m at {ts:.3f} s ({ps / pa:.2f}x its own bounce, "
          f"{ps / hd:.2f}x the drop height); its top reaches {ps + 2 * tb['radius']:.3f} m; the basketball peaks at "
          f"{pb:.3f} m at {tb_:.3f} s; {len(ev)} collisions in {dur:g} s; energy drift {stack['dE']:.1e}")
    later = float(stack["h"][stack["t"] > ts, 1].max())
    print(f"later flights (not narrated): after the first flight comes down the balls keep colliding; the tennis "
          f"ball's highest point in the {dur:g} s run is {later:.3f} m")
    print(f"speed factor: {hit1[4][1] / v_in:.4f} (limit 3 for a very heavy bottom ball, height factor 9)")
    lossy = simulate(stack_balls(man), g, dur, rate, man["check_restitution"])
    hl = next(e_ for e_ in lossy["events"] if e_[1] == "ball")
    pl, _ = peak(lossy, 1, hl, g)
    lossy_alone = simulate([{"r": tb["radius"], "m": tb["mass"], "h": hd, "v": 0.0}], g, dur, rate, man["check_restitution"])
    fla = next(e_ for e_ in lossy_alone["events"] if e_[1] == "floor")
    pla, _ = peak(lossy_alone, 0, fla, g)
    print(f"check, lossy bounces (restitution {man['check_restitution']:g} at the floor and between balls): alone "
          f"{pla:.3f} m, on the basketball {pl:.3f} m ({pl / pla:.2f}x)")
    for ratio in man["check_mass_ratios"]:
        balls = stack_balls(man)
        balls[0]["m"] = tb["mass"] * ratio
        r_ = simulate(balls, g, dur, rate)
        h_ = next(e_ for e_ in r_["events"] if e_[1] == "ball")
        p_, _ = peak(r_, 1, h_, g)
        print(f"check, mass ratio {ratio:g}: tennis ball peaks at {p_:.3f} m ({p_ / pa:.2f}x its own bounce), speed factor "
              f"{h_[4][1] / v_in:.3f}")
    three = simulate(stack_balls(man, man["check_third_ball"]), g, dur, rate)
    hits = [e_ for e_ in three["events"] if e_[1] == "ball" and e_[2] == 1]
    p3, t3 = peak(three, 2, hits[0], g)
    print(f"check, a third ball on top ({man['check_third_ball']['mass'] * 1000:.1f} g, radius "
          f"{man['check_third_ball']['radius'] * 100:.1f} cm): it peaks at {p3:.2f} m at {t3:.3f} s "
          f"({p3 / pa:.1f}x its own bounce)")
    return {"alone": alone, "stack": stack, "peak_alone": pa, "peak_stack": ps, "t_peak_stack": ts,
            "t_floor": floor1[0], "t_hit": hit1[0]}


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
        self.font_ruler = ImageFont.truetype(font, 28)
        self.first = None
        self.hanging = None
        self.rate = man["sample_rate"]
        tb = man["balls"]["tennis"]["radius"]
        # Running maximum of the tennis ball's top over both panels, for the zoom.
        tops = np.maximum(meas["alone"]["h"][:, 0], meas["stack"]["h"][:, 1]) + 2 * tb
        self.top_running = np.maximum.accumulate(tops)
        widths = {"overlay@34": (ImageFont.truetype(font, 34), man["overlay"])}
        for j, line in enumerate(man["title"].split("|")):
            widths[f"title line {j + 1}@56"] = (self.font_title, line)
        for name, p in PANELS.items():
            widths[f"label {name}@40"] = (self.font, p["label"])
        widths["readout label@32"] = (self.font_small, "highest so far")
        widths["readout@44"] = (self.font_read, "5.62 m")
        for j, line in enumerate(self.payoff_lines()):
            widths[f"payoff line {j + 1}@40"] = (self.font, line)
        print("text widths: " + ", ".join(f"{k} {f.getlength(s):.0f} px" for k, (f, s) in widths.items()))

    def payoff_lines(self) -> list[str]:
        text = self.man["payoff_text"].format(alone=self.meas["peak_alone"], stack=self.meas["peak_stack"])
        return [s.strip() for s in text.split("|")]

    def index(self, s: float) -> int:
        return min(int(round(s * self.rate)), len(self.meas["alone"]["t"]) - 1)

    def look_at(self, t: float):
        man = self.man
        fade = man["reset_fade"]
        for look in man["looks"]:
            if look["t0"] - 1.0 <= t < look["end"] + fade:
                s = max(0.0, (t - look["t0"]) * look["speed"])
                if look.get("freeze_at_peak"):
                    # Hold the peak frame, then let the balls come down.
                    s = min(s, self.meas["t_peak_stack"])
                    if t > look["hold_until"]:
                        s = self.meas["t_peak_stack"] + (t - look["hold_until"]) * look["resume_speed"]
                alpha = smoothstep((t - look["end"]) / fade) if t >= look["end"] else 0.0
                return s, look["readouts"], alpha, look["t0"]
        return 0.0, False, 0.0, 0.0

    def scale(self, s: float) -> float:
        man = self.man
        top = self.top_running[self.index(s)]
        return min(man["px_per_m_max"], (FLOOR_Y - TOP_LIMIT) / (top + man["zoom_margin"]))

    def draw_scene(self, s: float, readouts: bool, title_on: bool) -> Image.Image:
        man, meas = self.man, self.meas
        img = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(img)
        pxm = self.scale(s)
        i = self.index(s)
        # Ruler.
        top_m = (FLOOR_Y - TOP_LIMIT) / pxm
        step = 1.0 if pxm < 380 else 0.5
        k = 0
        while k * step <= top_m + 1e-9:
            y = FLOOR_Y - k * step * pxm
            d.line([(RULER_X - 14, y), (RULER_X, y)], fill=WIRE, width=2)
            if abs(k * step - round(k * step)) < 1e-9 and (k > 0):
                d.text((RULER_X - 22, y), f"{int(round(k * step))} m", font=self.font_ruler, fill=MUTED, anchor="rm")
            k += 1
        d.line([(RULER_X, TOP_LIMIT - 10), (RULER_X, FLOOR_Y)], fill=WIRE, width=2)
        # Floor.
        d.line([(RULER_X, FLOOR_Y), (W - 80, FLOOR_Y)], fill=FLOOR, width=6)
        runs = {"alone": (meas["alone"], ["tennis"]), "stack": (meas["stack"], ["basketball", "tennis"])}
        trail_n = int(0.10 * self.rate)
        for name, p in PANELS.items():
            run, kinds = runs[name]
            cx = p["x"]
            for b, kind in enumerate(kinds):
                r = run["r"][b]
                for j in range(4, 0, -1):
                    ii = i - j * (trail_n // 4)
                    if kind == "tennis" and ii >= 0:
                        yy = FLOOR_Y - (run["h"][ii, b] + r) * pxm
                        col = tuple(int(c * 0.18 * (5 - j) / 4 + BG[q] * (1 - 0.18 * (5 - j) / 4)) for q, c in enumerate(TEAL))
                        d.ellipse((cx - 6, yy - 6, cx + 6, yy + 6), fill=col)
                hb = run["h"][i, b]
                yc = FLOOR_Y - (hb + r) * pxm
                rp = r * pxm
                if yc + rp < TOP_LIMIT - 60:
                    continue
                col = COLOURS[kind]
                d.ellipse((cx - rp, yc - rp, cx + rp, yc + rp), fill=col)
                if kind == "basketball":
                    d.ellipse((cx - rp, yc - rp, cx + rp, yc + rp), outline=(160, 110, 40), width=max(2, int(rp * 0.05)))
                    d.line([(cx, yc - rp), (cx, yc + rp)], fill=(160, 110, 40), width=max(2, int(rp * 0.04)))
                    d.line([(cx - rp, yc), (cx + rp, yc)], fill=(160, 110, 40), width=max(2, int(rp * 0.04)))
                if kind == "tennis":
                    d.ellipse((cx - MARKER_R, yc - MARKER_R, cx + MARKER_R, yc + MARKER_R), outline=TEAL, width=2)
        d.rectangle((0, TOP_LIMIT - 80, W, TOP_LIMIT - 60), fill=BG)
        if not title_on:
            for name, p in PANELS.items():
                d.text((p["x"], LABEL_Y), p["label"], font=self.font, fill=GOLD if name == "stack" else TEAL, anchor="mm")
                if readouts:
                    run, kinds = runs[name]
                    b = kinds.index("tennis")
                    hi = float(run["h"][: i + 1, b].max())
                    d.text((p["x"], READ_Y), "highest so far", font=self.font_small, fill=MUTED, anchor="mm")
                    d.text((p["x"], VALUE_Y), f"{hi:.2f} m", font=self.font_read, fill=TEXT, anchor="mm")
        return img

    def live_frame(self, f: int) -> np.ndarray:
        man = self.man
        t = f / self.fps
        title_on = t < man["title_until"]
        s, readouts, alpha, _ = self.look_at(t)
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
    man = json.loads((ROOT / "projects/cannon/manifest.json").read_text())
    meas = measure(man)
    if "--measure-only" in sys.argv:
        return
    if "--frames" in sys.argv:
        times = [float(v) for v in sys.argv[sys.argv.index("--frames") + 1].split(",")]
        r = Renderer(man, meas)
        for tv in times:
            Image.fromarray(r.frame_at(int(round(tv * man["fps"])))).save(ROOT / f"media/cannon/smoke-{tv}.png")
        print("smoke frames: " + ", ".join(f"{tv}" for tv in times))
        return
    Renderer(man, meas).render(ROOT / "media/cannon/footage.mp4")


if __name__ == "__main__":
    main()
