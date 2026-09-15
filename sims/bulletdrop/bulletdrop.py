#!/usr/bin/env python3
"""Dropped versus fired bullet: which lands first?

Two bullets start at the same height at the same instant. The left one is
dropped from rest; the right one is fired level at the muzzle speed. Both
are integrated with RK4 at a fixed step in two dimensions, with gravity
only (the headline run), and the landing time of each is found by linear
interpolation of the height crossing zero. Checks: half the step, the same
two bullets in air with quadratic drag (drag acts along the velocity, so
the fast bullet's drag has a small upward part), and a ground that curves
away like the Earth. No seed: the run is deterministic.

Measured and printed: the landing time of each bullet, the gap between
them, the distance the fired bullet flew, the checks, and the on-screen
text widths.

usage: bulletdrop.py [--measure-only] [--frames t1,t2,...]
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
FLOOR = (120, 132, 150)
STRIPE_A = (40, 47, 58)
STRIPE_B = (16, 20, 26)

# Layout: labels and readouts under the overlay, the two panels side by
# side above the floor, the clock under the floor, captions at caption_y
# 0.75 (y 1440..1510), payoff under the captions.
LABEL_Y = 236
READ_Y = 290
VALUE_Y = 338
PANEL_X = {"drop": 270.0, "fire": 810.0}
DIVIDER_X = 540
FLOOR_Y = 1300
CLOCK_Y = 1352
PAYOFF_Y = 1592.0
RULER_DX = -150  # ruler x relative to the panel centre


def simulate(g: float, vx0: float, h: float, dt: float, drag_k: float = 0.0,
             curve_r: float = 0.0, t_max: float = 1.0) -> dict:
    """One bullet from (0, h) with velocity (vx0, 0) until it reaches the ground.

    drag_k is 0.5 rho Cd A / m (per metre); curve_r > 0 makes the ground
    drop away as x^2 / (2 R). Returns the sampled path and the landing
    time, interpolated within the last step.
    """
    s = np.array([0.0, h, vx0, 0.0])

    def deriv(st: np.ndarray) -> np.ndarray:
        v = math.hypot(st[2], st[3])
        ax = -drag_k * v * st[2]
        ay = -g - drag_k * v * st[3]
        return np.array([st[2], st[3], ax, ay])

    def ground(x: float) -> float:
        return -x * x / (2 * curve_r) if curve_r > 0 else 0.0

    n = int(round(t_max / dt))
    path = np.empty((n + 1, 4))
    landing = None
    for i in range(n + 1):
        path[i] = s
        if i > 0:
            above_prev = path[i - 1, 1] - ground(path[i - 1, 0])
            above = s[1] - ground(s[0])
            if above <= 0.0 < above_prev:
                f = above_prev / (above_prev - above)
                landing = (i - 1 + f) * dt
                land_x = path[i - 1, 0] + f * (s[0] - path[i - 1, 0])
                path = path[: i + 1]
                break
        k1 = deriv(s)
        k2 = deriv(s + 0.5 * dt * k1)
        k3 = deriv(s + 0.5 * dt * k2)
        k4 = deriv(s + dt * k3)
        s = s + dt / 6.0 * (k1 + 2 * k2 + 2 * k3 + k4)
    if landing is None:
        raise RuntimeError("bullet did not land inside t_max")
    return {"path": path, "dt": dt, "t_land": landing, "x_land": land_x,
            "v_land": math.hypot(path[-1, 2], path[-1, 3])}


def measure(man: dict) -> dict:
    g, h, v0, dt = man["g"], man["height_m"], man["muzzle_m_per_s"], man["dt"]
    air = man["air"]
    area = math.pi * (air["diameter_m"] / 2) ** 2
    k = 0.5 * air["density_kg_per_m3"] * air["drag_coefficient"] * area / air["mass_kg"]
    print(f"setup: two bullets released at the same instant from {h:g} m; one dropped from rest, one fired "
          f"level at {v0:g} m/s ({v0 * 3.6:,.0f} km/h, {v0 / 343:.2f} times the speed of sound); flat ground, "
          f"g {g:g} m/s^2, no air; RK4 at {dt:g} s steps, landing time interpolated inside the last step; "
          f"deterministic, no seed")
    drop = simulate(g, 0.0, h, dt)
    fire = simulate(g, v0, h, dt)
    closed = math.sqrt(2 * h / g)
    gap_ms = (fire["t_land"] - drop["t_land"]) * 1000
    print(f"dropped: hits the ground at {drop['t_land']:.5f} s at {drop['v_land']:.3f} m/s "
          f"(closed form sqrt(2h/g) = {closed:.5f} s)")
    print(f"fired: hits the ground at {fire['t_land']:.5f} s, {fire['x_land']:.2f} m from the start, "
          f"at {fire['v_land']:.2f} m/s; the fired bullet lands {gap_ms:+.3f} ms after the dropped one "
          f"({abs(gap_ms) * 1000:.1f} microseconds apart)")
    # Height match sampled along the fall: the two heights never differ.
    n = min(len(drop["path"]), len(fire["path"]))
    dh = np.max(np.abs(drop["path"][:n, 1] - fire["path"][:n, 1]))
    print(f"heights: over the whole fall the two bullets' heights differ by at most {dh * 1e6:.3f} micrometres")
    fine_d = simulate(g, 0.0, h, man["check_dt"])
    fine_f = simulate(g, v0, h, man["check_dt"])
    print(f"check, half the step ({man['check_dt']:g} s): dropped {fine_d['t_land']:.5f} s, fired "
          f"{fine_f['t_land']:.5f} s, gap {(fine_f['t_land'] - fine_d['t_land']) * 1000:+.3f} ms")
    air_d = simulate(g, 0.0, h, dt, drag_k=k)
    air_f = simulate(g, v0, h, dt, drag_k=k)
    print(f"check, in air (density {air['density_kg_per_m3']:g} kg/m^3, drag coefficient {air['drag_coefficient']:g}, "
          f"{air['diameter_m'] * 1000:g} mm bullet of {air['mass_kg'] * 1000:g} g, quadratic drag along the velocity, "
          f"k = {k:.3e} per metre): dropped {air_d['t_land']:.4f} s, fired {air_f['t_land']:.4f} s "
          f"({(air_f['t_land'] - air_d['t_land']) * 1000:+.1f} ms later, {air_f['x_land']:.1f} m from the start, "
          f"arriving at {air_f['v_land']:.0f} m/s); drag on the fast bullet has an upward part because the "
          f"drag force points against the velocity, which tilts down")
    curve_f = simulate(g, v0, h, dt, curve_r=man["earth_radius_m"])
    drop_curve = curve_f["x_land"] ** 2 / (2 * man["earth_radius_m"])
    print(f"check, ground curving away like the Earth (radius {man['earth_radius_m'] / 1000:,.0f} km): the fired "
          f"bullet lands at {curve_f['t_land']:.5f} s, {(curve_f['t_land'] - fire['t_land']) * 1000:+.2f} ms "
          f"later, the ground having dropped {drop_curve * 1000:.1f} mm under it")
    return {"drop": drop, "fire": fire, "gap_ms": gap_ms, "range": fire["x_land"]}


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
        self.font_ruler = ImageFont.truetype(font, 28)
        self.first = None
        self.pxm = man["px_per_m"]
        self.slow = man["slow_motion"]
        self.labels = {"drop": "dropped", "fire": f"fired level at {man['muzzle_m_per_s']:g} m/s"}
        widths = {"overlay@34": (ImageFont.truetype(font, 34), man["overlay"])}
        for j, line in enumerate(man["title"].split("|")):
            widths[f"title line {j + 1}@56"] = (self.font_title, line)
        for name, label in self.labels.items():
            widths[f"label {name}@40"] = (self.font, label)
        widths["readout label@32"] = (self.font_small, "height")
        widths["readout@44"] = (self.font_read, "1.500 m")
        widths["flown@32"] = (self.font_small, "flown 199.1 m")
        widths["watch@64"] = (self.font_watch, "0.553 s")
        widths["watch label@32"] = (self.font_small, f"1/{self.slow:g} speed")
        for j, line in enumerate(self.payoff_lines()):
            widths[f"payoff line {j + 1}@40"] = (self.font, line)
        print("text widths: " + ", ".join(f"{k} {f.getlength(s):.0f} px" for k, (f, s) in widths.items()))
        t_land = meas["drop"]["t_land"] * self.slow
        print(f"slow motion 1/{self.slow:g}: the fall starts at 0.0 s of video, both bullets land at "
              f"{t_land:.2f} s of video; payoff card at {man['payoff_t']:g} s")

    def payoff_lines(self) -> list[str]:
        text = self.man["payoff_text"].format(drop=self.meas["drop"]["t_land"], fire=self.meas["fire"]["t_land"],
                                              range=self.meas["range"])
        return [s.strip() for s in text.split("|")]

    def state(self, run: dict, sim_t: float) -> tuple[float, float, bool]:
        """Return x, height and whether the bullet has landed at sim time sim_t."""
        if sim_t >= run["t_land"]:
            return run["x_land"], 0.0, True
        i = min(int(sim_t / run["dt"]), len(run["path"]) - 1)
        f = sim_t / run["dt"] - i
        j = min(i + 1, len(run["path"]) - 1)
        x = run["path"][i, 0] + f * (run["path"][j, 0] - run["path"][i, 0])
        y = run["path"][i, 1] + f * (run["path"][j, 1] - run["path"][i, 1])
        return float(x), max(0.0, float(y)), False

    def bullet(self, d: ImageDraw.ImageDraw, cx: float, cy: float, col, horizontal: bool, streak: float = 0.0) -> None:
        # A capsule drawn larger than life (about 16 px wide, 44 px long).
        r = 10
        if horizontal:
            if streak > 0:
                for k in range(1, 5):
                    a = 0.45 * (1 - k / 5)
                    c = tuple(int(v * a + BG[q] * (1 - a)) for q, v in enumerate(col))
                    d.rounded_rectangle((cx - 26 - k * 30, cy - r, cx + 26 - k * 30, cy + r), radius=r, fill=c)
            d.rounded_rectangle((cx - 26, cy - r, cx + 26, cy + r), radius=r, fill=col)
            d.polygon([(cx + 26, cy - r), (cx + 40, cy), (cx + 26, cy + r)], fill=col)
        else:
            d.rounded_rectangle((cx - r, cy - 26, cx + r, cy + 26), radius=r, fill=col)
            d.polygon([(cx - r, cy + 26), (cx, cy + 40), (cx + r, cy + 26)], fill=col)

    def draw_scene(self, t: float, title_on: bool) -> Image.Image:
        man, meas = self.man, self.meas
        sim_t = t / self.slow
        img = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(img)
        pxm = self.pxm
        top_y = FLOOR_Y - man["height_m"] * pxm
        xd, hd, landed_d = self.state(meas["drop"], sim_t)
        xf, hf, landed_f = self.state(meas["fire"], sim_t)
        # Right panel ground: stripes every metre and a numbered post every
        # 10 m, streaming left as the camera follows the fired bullet.
        px, py = PANEL_X["fire"], FLOOR_Y
        left, right = DIVIDER_X + 2, W
        x_cam = xf  # metre under the bullet
        band_top = FLOOR_Y + 4
        band_bot = FLOOR_Y + 34
        m0 = math.floor(x_cam - (px - left) / pxm) - 1
        m1 = math.ceil(x_cam + (right - px) / pxm) + 1
        for m in range(m0, m1 + 1):
            x0 = px + (m - x_cam) * pxm
            x1 = x0 + pxm
            col = STRIPE_A if m % 2 == 0 else STRIPE_B
            xa, xb = max(left, x0), min(right, x1)
            if xb > xa:
                d.rectangle((xa, band_top, xb, band_bot), fill=col)
            if m % 10 == 0 and m > 0 and left <= x0 <= right:
                d.line([(x0, FLOOR_Y - 36), (x0, FLOOR_Y)], fill=MUTED, width=3)
                d.text((x0, FLOOR_Y - 52), f"{m} m", font=self.font_ruler, fill=MUTED, anchor="mm")
        # Left panel ground band, static.
        d.rectangle((0, band_top, DIVIDER_X - 2, band_bot), fill=STRIPE_A)
        # Rulers: the same height scale in both panels.
        for name, cx in PANEL_X.items():
            rx = cx + RULER_DX
            d.line([(rx, top_y - 10), (rx, FLOOR_Y)], fill=WIRE, width=2)
            k = 0
            while k * 0.5 <= man["height_m"] + 1e-9:
                y = FLOOR_Y - k * 0.5 * pxm
                d.line([(rx - 14, y), (rx, y)], fill=WIRE, width=2)
                d.text((rx - 22, y), f"{k * 0.5:g} m", font=self.font_ruler, fill=MUTED, anchor="rm")
                k += 1
        # Floor and divider.
        d.line([(0, FLOOR_Y), (W, FLOOR_Y)], fill=FLOOR, width=6)
        d.line([(DIVIDER_X, top_y - 40), (DIVIDER_X, FLOOR_Y + 30)], fill=WIRE, width=2)
        # A faint line joining the two heights: they stay level.
        yd = FLOOR_Y - hd * pxm
        yf = FLOOR_Y - hf * pxm
        if not landed_d:
            d.line([(PANEL_X["drop"] + 40, yd), (PANEL_X["fire"] - 60, yf)], fill=(40, 48, 58), width=2)
        # Bullets.
        if landed_d:
            d.ellipse((PANEL_X["drop"] - 30, FLOOR_Y - 10, PANEL_X["drop"] + 30, FLOOR_Y + 10), fill=TEAL)
        else:
            self.bullet(d, PANEL_X["drop"], yd - 6, TEAL, horizontal=False)
        if landed_f:
            d.ellipse((px - 30, FLOOR_Y - 10, px + 30, FLOOR_Y + 10), fill=GOLD)
        else:
            self.bullet(d, px, yf - 8, GOLD, horizontal=True, streak=1.0)
        if not title_on:
            for name, cx in PANEL_X.items():
                col = TEAL if name == "drop" else GOLD
                d.text((cx, LABEL_Y), self.labels[name], font=self.font, fill=col, anchor="mm")
                d.text((cx, READ_Y), "height", font=self.font_small, fill=MUTED, anchor="mm")
                h_now = hd if name == "drop" else hf
                d.text((cx, VALUE_Y), f"{h_now:.3f} m", font=self.font_read, fill=TEXT, anchor="mm")
            d.text((px, VALUE_Y + 44), f"flown {xf:.1f} m", font=self.font_small, fill=MUTED, anchor="mm")
            shown = min(sim_t, meas["fire"]["t_land"]) if landed_f and landed_d else sim_t
            d.text((W / 2, CLOCK_Y), f"{shown:.3f} s", font=self.font_watch, fill=TEXT, anchor="mm")
            d.text((W / 2, CLOCK_Y + 50), f"1/{self.slow:g} speed", font=self.font_small, fill=MUTED, anchor="mm")
        return img

    def live_frame(self, f: int) -> np.ndarray:
        man = self.man
        t = f / self.fps
        title_on = t < man["title_until"]
        img = self.draw_scene(t, title_on)
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
    man = json.loads((ROOT / "projects/bulletdrop/manifest.json").read_text())
    meas = measure(man)
    if "--measure-only" in sys.argv:
        return
    if "--frames" in sys.argv:
        times = [float(v) for v in sys.argv[sys.argv.index("--frames") + 1].split(",")]
        r = Renderer(man, meas)
        for tv in times:
            Image.fromarray(r.frame_at(int(round(tv * man["fps"])))).save(ROOT / f"media/bulletdrop/smoke-{tv}.png")
        print("smoke frames: " + ", ".join(f"{tv}" for tv in times))
        return
    Renderer(man, meas).render(ROOT / "media/bulletdrop/footage.mp4")


if __name__ == "__main__":
    main()
