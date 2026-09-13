#!/usr/bin/env python3
"""Gravity train: fall through the Earth, how long to the other side?

One Earth of uniform density, two straight frictionless tunnels, no engine.
Tunnel A runs through the centre, pole to pole. Tunnel B is a vertical chord
near the edge, 4,000 km long. A capsule is dropped into the top of each at
the same moment. Inside a uniform sphere gravity points to the centre with
strength g0 r / R, so the component along any straight tunnel is
-(g0 / R) s with s the distance from the tunnel's midpoint: every tunnel is
the same harmonic oscillator and the crossing time does not depend on the
tunnel. The sim integrates the full central force (not the closed form) with
RK4 along each tunnel and measures the crossing times, the top speeds and
the periods; the closed forms pi sqrt(R / g0) and sqrt(g0 R) are printed
beside them. A two-layer Earth (dense core, lighter mantle) is run as a
check for the description. No seed: the run is deterministic.

Measured and printed: the tunnel geometry, the arrival time at the far end
of each tunnel, the top speed and where it occurs, the return time (the
period), the closed forms, a step-halving check, other chord lengths, the
two-layer Earth, and the on-screen text widths.

usage: gravitytrain.py [--measure-only] [--frames t1,t2,...]
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
EARTH_IN = (22, 28, 38)
EARTH_OUT = (58, 72, 96)
RIM = (110, 130, 160)

# Layout: the Earth disc in the middle, header labels above it, captions in
# the band at caption_y 0.75 (y 1440..1510), payoff under it.
CENTRE = (540.0, 900.0)
R_PX = 470.0
LABEL_Y = 236
READ_Y = 290
VALUE_Y = 338
WATCH_X = 300.0
WATCH_Y = 900.0
PAYOFF_Y = 1592.0
CAPSULE_R = 14
PANEL_X = {"centre": 300.0, "chord": 780.0}


def gravity_uniform(r: float, R: float, g0: float) -> float:
    return g0 * r / R


def gravity_layers(r: float, layers: list[dict], G: float = 6.674e-11) -> float:
    m = 0.0
    r_prev = 0.0
    for lay in layers:
        r_out = lay["radius_km"] * 1000.0
        r_here = min(r, r_out)
        if r_here > r_prev:
            m += 4.0 / 3.0 * math.pi * (r_here ** 3 - r_prev ** 3) * lay["density"]
        r_prev = r_out
        if r <= r_out:
            break
    return G * m / (r * r) if r > 0 else 0.0


def simulate(R: float, half_len: float, offset: float, grav, duration: float, steps_per_s: int) -> dict:
    """Capsule on a straight tunnel: s from the midpoint (start at +half_len), offset from the centre."""
    dt = 1.0 / steps_per_s
    n = int(round(duration * steps_per_s))

    def acc(s: float) -> float:
        r = math.hypot(offset, s)
        return -grav(r) * (s / r) if r > 0 else 0.0

    s, v = half_len, 0.0
    S = np.empty(n + 1)
    V = np.empty(n + 1)
    arrival = None
    ret = None
    for i in range(n + 1):
        S[i], V[i] = s, v
        if i == n:
            break
        k1v, k1s = acc(s), v
        k2v, k2s = acc(s + 0.5 * dt * k1s), v + 0.5 * dt * k1v
        k3v, k3s = acc(s + 0.5 * dt * k2s), v + 0.5 * dt * k2v
        k4v, k4s = acc(s + dt * k3s), v + dt * k3v
        s_new = s + dt / 6.0 * (k1s + 2 * k2s + 2 * k3s + k4s)
        v_new = v + dt / 6.0 * (k1v + 2 * k2v + 2 * k3v + k4v)
        # The far end is the first turning point (v from negative to positive);
        # the start is reached again at the next one.
        if arrival is None and i > 0 and v < 0 <= v_new:
            arrival = (i + (-v) / (v_new - v)) * dt
        if arrival is not None and ret is None and v > 0 >= v_new:
            ret = (i + v / (v - v_new)) * dt
        s, v = s_new, v_new
    imax = int(np.argmax(np.abs(V)))
    return {"s": S, "v": V, "dt": dt, "arrival": arrival, "period": ret,
            "vmax": float(abs(V[imax])), "t_vmax": imax * dt}


def mmss(seconds: float) -> str:
    m = int(seconds // 60)
    s = int(round(seconds - 60 * m))
    if s == 60:
        m, s = m + 1, 0
    return f"{m}:{s:02d}"


def measure(man: dict) -> dict:
    R = man["earth_radius_km"] * 1000.0
    g0 = man["surface_g"]
    c = man["chord_length_km"] * 1000.0
    half = c / 2
    offset = math.sqrt(R * R - half * half)
    depth = R - offset
    T = 2 * math.pi * math.sqrt(R / g0)
    dur = 1.05 * T
    sps = man["steps_per_second"]
    grav = lambda r: gravity_uniform(r, R, g0)
    print(f"earth: radius {R / 1000:,.0f} km, uniform density, surface gravity {g0:g} m/s^2; tunnel through the "
          f"centre {2 * R / 1000:,.0f} km long; chord tunnel {c / 1000:,.0f} km long, {offset / 1000:,.0f} km from "
          f"the centre, its midpoint {depth / 1000:,.0f} km below the surface; RK4 at {sps} steps per second of "
          f"travel, deterministic, no seed")
    print(f"closed forms: half period pi sqrt(R / g0) = {T / 2:.1f} s = {T / 120:.2f} min; period {T:.1f} s = "
          f"{T / 60:.2f} min; top speed through the centre sqrt(g0 R) = {math.sqrt(g0 * R):,.0f} m/s; top speed "
          f"on the chord (c / 2) sqrt(g0 / R) = {half * math.sqrt(g0 / R):,.0f} m/s")
    runs = {"centre": simulate(R, R, 0.0, grav, dur, sps), "chord": simulate(R, half, offset, grav, dur, sps)}
    for name, run in runs.items():
        print(f"{name} tunnel: arrives at the far end at {run['arrival']:.2f} s = {mmss(run['arrival'])} "
              f"({run['arrival'] / 60:.3f} min); top speed {run['vmax']:,.1f} m/s at {run['t_vmax']:.0f} s "
              f"(the midpoint); back at the start at {run['period']:.2f} s = {run['period'] / 60:.3f} min")
    print(f"difference in arrival times: {abs(runs['centre']['arrival'] - runs['chord']['arrival']) * 1000:.3f} ms")
    fine = {k: simulate(R, R if k == "centre" else half, 0.0 if k == "centre" else offset, grav, dur,
                        man["check_steps_per_second"]) for k in runs}
    print("check, double the steps: " + "; ".join(f"{k} arrives at {v['arrival']:.3f} s" for k, v in fine.items()))
    for ckm in man["check_chords_km"]:
        h2 = ckm * 500.0
        off = math.sqrt(R * R - h2 * h2)
        r_ = simulate(R, h2, off, grav, dur, sps)
        print(f"check, {ckm:,.0f} km chord ({(R - off) / 1000:,.0f} km deep at the midpoint): arrives at "
              f"{r_['arrival']:.2f} s = {mmss(r_['arrival'])}, top speed {r_['vmax']:,.0f} m/s")
    layers = man["check_layers"]
    gl = lambda r: gravity_layers(r, layers)
    print(f"check, two-layer Earth (core {layers[0]['radius_km']:,.0f} km at {layers[0]['density']:,.0f} kg/m^3, "
          f"mantle {layers[1]['density']:,.0f} kg/m^3; surface gravity {gl(R):.2f} m/s^2, gravity at the core "
          f"boundary {gl(layers[0]['radius_km'] * 1000):.2f} m/s^2):")
    for name, hl, off in (("centre", R, 0.0), ("chord", half, offset)):
        r_ = simulate(R, hl, off, gl, dur, sps)
        print(f"  {name} tunnel arrives at {r_['arrival']:.1f} s = {mmss(r_['arrival'])}, top speed "
              f"{r_['vmax']:,.0f} m/s; the two tunnels no longer agree")
    return {"runs": runs, "R": R, "half": half, "offset": offset, "period": T,
            "arrival": {k: v["arrival"] for k, v in runs.items()}}


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
        self.period = meas["runs"]["centre"]["period"]
        self.rate = self.period * man["periods_in_scene"] / man["scene_duration"]  # sim seconds per video second
        self.earth = self.draw_earth()
        widths = {"overlay@34": (ImageFont.truetype(font, 34), man["overlay"])}
        for j, line in enumerate(man["title"].split("|")):
            widths[f"title line {j + 1}@56"] = (self.font_title, line)
        widths["label centre@40"] = (self.font, "through the centre")
        widths["label chord@40"] = (self.font, f"{man['chord_length_km']:,.0f} km tunnel")
        widths["speed@44"] = (self.font_read, "7,906 m/s")
        widths["arrived@40"] = (self.font, "arrived 42:14")
        widths["watch@64"] = (self.font_watch, "42:14")
        widths["watch label@32"] = (self.font_small, "since the drop")
        for j, line in enumerate(self.payoff_lines()):
            widths[f"payoff line {j + 1}@40"] = (self.font, line)
        print("text widths: " + ", ".join(f"{k} {f.getlength(s):.0f} px" for k, (f, s) in widths.items()))
        print(f"time-lapse: {self.rate:.1f}x, {man['periods_in_scene']} periods in {man['scene_duration']:g} s; "
              f"arrivals at " + ", ".join(f"{(k + 0.5) * self.period / self.rate:.2f}" for k in range(man["periods_in_scene"])) + " s of video")

    def payoff_lines(self) -> list[str]:
        a = self.meas["arrival"]
        text = self.man["payoff_text"].format(centre=mmss(a["centre"]), chord=mmss(a["chord"]),
                                              chord_km=self.man["chord_length_km"])
        return [s.strip() for s in text.split("|")]

    def draw_earth(self) -> Image.Image:
        """Disc shaded by the strength of gravity inside: dark at the centre, bright at the rim."""
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        r = np.hypot(xx - CENTRE[0], yy - CENTRE[1]) / R_PX
        img = np.empty((H, W, 3), dtype=np.float32)
        inside = r <= 1.0
        for ch in range(3):
            img[..., ch] = np.where(inside, EARTH_IN[ch] + (EARTH_OUT[ch] - EARTH_IN[ch]) * np.clip(r, 0, 1), BG[ch])
        im = Image.fromarray(img.astype(np.uint8))
        d = ImageDraw.Draw(im)
        cx, cy = CENTRE
        d.ellipse((cx - R_PX, cy - R_PX, cx + R_PX, cy + R_PX), outline=RIM, width=4)
        for k in (0.25, 0.5, 0.75):
            d.ellipse((cx - R_PX * k, cy - R_PX * k, cx + R_PX * k, cy + R_PX * k), outline=(40, 50, 66), width=1)
        return im

    def tunnel_xy(self, name: str, s: float) -> tuple[float, float]:
        cx, cy = CENTRE
        if name == "centre":
            return cx, cy - s / self.meas["R"] * R_PX
        return cx + self.meas["offset"] / self.meas["R"] * R_PX, cy - s / self.meas["R"] * R_PX

    def live_frame(self, f: int) -> Image.Image:
        man, meas = self.man, self.meas
        t = f / self.fps
        title_on = t < man["title_until"]
        sim_t = t * self.rate
        img = self.earth.copy()
        d = ImageDraw.Draw(img)
        since_drop = sim_t % self.period if sim_t < man["periods_in_scene"] * self.period - 1e-9 else self.period
        colours = {"centre": GOLD, "chord": TEAL}
        for name, run in meas["runs"].items():
            half = meas["R"] if name == "centre" else meas["half"]
            x0, y0 = self.tunnel_xy(name, half)
            x1, y1 = self.tunnel_xy(name, -half)
            d.line([(x0, y0), (x1, y1)], fill=(14, 18, 24), width=12)
            d.line([(x0, y0), (x1, y1)], fill=colours[name], width=2)
            for yy in (y0, y1):
                d.line([(x0 - 16, yy), (x0 + 16, yy)], fill=colours[name], width=4)
            i = min(int(round(since_drop / run["dt"])), len(run["s"]) - 1)
            s, v = float(run["s"][i]), float(run["v"][i])
            x, y = self.tunnel_xy(name, s)
            d.ellipse((x - CAPSULE_R, y - CAPSULE_R, x + CAPSULE_R, y + CAPSULE_R), fill=colours[name])
            d.ellipse((x - 5, y - 5, x + 5, y + 5), fill=TEXT)
            if not title_on:
                px = PANEL_X[name]
                label = "through the centre" if name == "centre" else f"{man['chord_length_km']:,.0f} km tunnel"
                d.text((px, LABEL_Y), label, font=self.font, fill=colours[name], anchor="mm")
                d.text((px, READ_Y), "speed", font=self.font_small, fill=MUTED, anchor="mm")
                d.text((px, VALUE_Y), f"{abs(v):,.0f} m/s", font=self.font_read, fill=TEXT, anchor="mm")
                if since_drop >= run["arrival"]:
                    d.text((px, VALUE_Y + 52), f"arrived {mmss(run['arrival'])}", font=self.font, fill=colours[name], anchor="mm")
        if not title_on:
            d.text((WATCH_X, WATCH_Y), mmss(since_drop), font=self.font_watch, fill=TEXT, anchor="mm")
            d.text((WATCH_X, WATCH_Y + 50), "since the drop", font=self.font_small, fill=MUTED, anchor="mm")

        def shade_col(col, a):
            return tuple(int(c * a + BG[j] * (1 - a)) for j, c in enumerate(col))

        if title_on:
            a = 1.0 if t < man["title_until"] - 0.4 else (man["title_until"] - t) / 0.4
            for j, line in enumerate(man["title"].split("|")):
                d.text((W / 2, 200 + j * 62), line, font=self.font_title, fill=shade_col(TEXT, a), anchor="mm")
        if t >= man["payoff_t"]:
            a = min(1.0, (t - man["payoff_t"]) / man["payoff_hold"])
            for j, line in enumerate(self.payoff_lines()):
                d.text((W / 2, PAYOFF_Y + j * 56), line, font=self.font, fill=shade_col(GOLD, a), anchor="mm")
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
    man = json.loads((ROOT / "projects/gravitytrain/manifest.json").read_text())
    meas = measure(man)
    if "--measure-only" in sys.argv:
        return
    if "--frames" in sys.argv:
        times = [float(v) for v in sys.argv[sys.argv.index("--frames") + 1].split(",")]
        r = Renderer(man, meas)
        for tv in times:
            Image.fromarray(r.frame_at(int(round(tv * man["fps"])))).save(ROOT / f"media/gravitytrain/smoke-{tv}.png")
        print("smoke frames: " + ", ".join(f"{tv}" for tv in times))
        return
    Renderer(man, meas).render(ROOT / "media/gravitytrain/footage.mp4")


if __name__ == "__main__":
    main()
