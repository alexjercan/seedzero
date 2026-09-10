#!/usr/bin/env python3
"""Brachistochrone race: which slide is fastest?

Three frictionless slides from the same start to the same end, one ball on
each, released together from rest. The straight slide is the shortest. The
curved slide is a cycloid, the longest of the three. The third slide is a
circular arc that starts gently (a shallower slope than the straight one)
and steepens toward the end. Every ball obeys the same bead-on-a-wire
equation, s'' = -g dy/ds along its own slide, integrated with RK4 at a
fixed step; only the slide shape differs. The race is played at quarter
speed and repeats every eight seconds of video, so the last frame equals
the first.

Measured and printed: each slide's length, each ball's arrival time (RK4)
against an independent quadrature of ds / sqrt(2 g h) and the closed forms
for the line and the cycloid, the energy drift, arrival times for a set of
check arcs, the on-screen text widths, and the loop closure error.

usage: brachistochrone.py [--measure-only]
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
BALL_R = 16

# Layout: the slide picture on top, captions between at caption_y 0.49
# (y 941..1021), the three lanes below.
TOP = {"label_y": 214, "start": (90.0, 300.0), "width_px": 900.0}
LANES = {"label_y": 1104, "x0": 360.0, "x1": 960.0, "ys": (1240.0, 1440.0, 1640.0)}
PAYOFF_Y = 1836.0


class Track:
    """A slide y(s), s the arc length from the start, y up, y <= 0."""

    name: str
    colour: tuple

    def y(self, s: float) -> float:
        return self.xy(s)[1]

    def dyds(self, s: float) -> float:
        raise NotImplementedError

    def xy(self, s: float) -> tuple[float, float]:
        raise NotImplementedError

    def exact_time(self, g: float) -> float | None:
        return None


class Line(Track):
    def __init__(self, X: float, Y: float):
        self.name, self.colour = "straight", GOLD
        self.X, self.Y = X, Y
        self.length = math.hypot(X, Y)

    def dyds(self, s: float) -> float:
        return -self.Y / self.length

    def xy(self, s: float) -> tuple[float, float]:
        return s * self.X / self.length, -s * self.Y / self.length

    def exact_time(self, g: float) -> float:
        return math.sqrt(2.0 * self.length ** 2 / (g * self.Y))


class Cycloid(Track):
    def __init__(self, a: float):
        self.name, self.colour = "curve", TEAL
        self.a = a
        self.length = 4.0 * a

    def theta(self, s: float) -> float:
        return 2.0 * math.acos(max(-1.0, min(1.0, 1.0 - s / (4.0 * self.a))))

    def dyds(self, s: float) -> float:
        return -math.cos(self.theta(s) / 2.0)

    def xy(self, s: float) -> tuple[float, float]:
        th = self.theta(s)
        return self.a * (th - math.sin(th)), -self.a * (1.0 - math.cos(th))

    def exact_time(self, g: float) -> float:
        return math.pi * math.sqrt(self.a / g)


class Arc(Track):
    """The circle through the start and the end whose tangent at the start
    points `start_deg` below horizontal."""

    def __init__(self, X: float, Y: float, start_deg: float, name: str = "gentle start", colour: tuple = CORAL):
        self.name, self.colour, self.start_deg = name, colour, start_deg
        al = math.radians(start_deg)
        tx, ty = math.cos(al), -math.sin(al)
        best = None
        for nx, ny in ((ty, -tx), (-ty, tx)):
            dot = nx * X - ny * Y
            if dot <= 1e-12:
                continue
            best = (nx, ny, (X * X + Y * Y) / (2.0 * dot))
        if best is None:
            raise ValueError(f"no circle for start angle {start_deg}")
        nx, ny, R = best
        self.R = R
        self.cx, self.cy = R * nx, R * ny
        self.phi0 = math.atan2(-self.cy, -self.cx)
        # Direction along the circle that matches the start tangent.
        self.sigma = 1.0 if (-math.sin(self.phi0) * tx + math.cos(self.phi0) * ty) > 0 else -1.0
        phi1 = math.atan2(-Y - self.cy, X - self.cx)
        delta = (self.sigma * (phi1 - self.phi0)) % (2.0 * math.pi)
        self.length = R * delta

    def phi(self, s: float) -> float:
        return self.phi0 + self.sigma * s / self.R

    def dyds(self, s: float) -> float:
        return self.sigma * math.cos(self.phi(s))

    def xy(self, s: float) -> tuple[float, float]:
        p = self.phi(s)
        return self.cx + self.R * math.cos(p), self.cy + self.R * math.sin(p)


def quadrature_time(track: Track, g: float, n: int = 400_000) -> float:
    """Independent check: T = integral ds / sqrt(2 g (-y))."""
    s = np.linspace(0.0, track.length, n + 1)
    mid = 0.5 * (s[1:] + s[:-1])
    y = np.array([track.y(v) for v in mid])
    return float(np.sum((s[1] - s[0]) / np.sqrt(np.maximum(2.0 * g * (-y), 1e-300))))


def integrate(track: Track, g: float, frames: int, frame_dt: float, substeps: int):
    """RK4 on (s, v) with s'' = -g y'(s) from rest at the start. Returns
    per-frame s (clamped at the end after arrival), the arrival time and
    the energy drift at arrival."""
    dt = frame_dt / substeps
    s, v = 0.0, 0.0
    ss = np.empty(frames)
    arrival, drift = None, 0.0

    def acc(x: float) -> float:
        return -g * track.dyds(min(x, track.length))

    for f in range(frames):
        ss[f] = min(s, track.length)
        if arrival is not None:
            continue
        for k in range(substeps):
            t = (f * substeps + k) * dt
            k1v, k1s = acc(s), v
            k2v, k2s = acc(s + 0.5 * dt * k1s), v + 0.5 * dt * k1v
            k3v, k3s = acc(s + 0.5 * dt * k2s), v + 0.5 * dt * k2v
            k4v, k4s = acc(s + dt * k3s), v + dt * k3v
            s_new = s + dt / 6.0 * (k1s + 2 * k2s + 2 * k3s + k4s)
            v_new = v + dt / 6.0 * (k1v + 2 * k2v + 2 * k3v + k4v)
            if s_new >= track.length > s:
                arrival = t + dt * (track.length - s) / (s_new - s)
                v_end = v + (v_new - v) * (track.length - s) / (s_new - s)
                drift = abs(0.5 * v_end * v_end + g * track.y(track.length)) / abs(g * track.y(track.length))
                s, v = track.length, v_end
                break
            s, v = s_new, v_new
    return ss, arrival, drift


def measure(man: dict) -> dict:
    g, fps, sub = man["g"], man["fps"], man["substeps"]
    a = g * (man["cycloid_time"] / math.pi) ** 2
    X, Y = math.pi * a, 2.0 * a
    tracks = [Arc(X, Y, man["gentle_start_deg"]), Line(X, Y), Cycloid(a)]
    frame_dt = man["playback"] / fps  # physics seconds per video frame
    race_frames = int(round(man["race_period"] * fps))
    print(f"cycloid a = {a:.5f} m so its time is exactly {man['cycloid_time']:.3f} s; start (0, 0), end ({X:.4f}, -{Y:.4f}) m: "
          f"{X:.3f} m across, {Y:.3f} m down; g = {g}; RK4 at {fps * sub / man['playback']:.0f} steps per physics second, "
          f"played at {man['playback']:g} speed")
    out = {"a": a, "X": X, "Y": Y, "tracks": tracks, "runs": [], "frame_dt": frame_dt, "race_frames": race_frames}
    for tr in tracks:
        ss, arr, drift = integrate(tr, g, race_frames, frame_dt, sub)
        quad = quadrature_time(tr, g)
        exact = tr.exact_time(g)
        extra = f", closed form {exact:.4f}" if exact is not None else ""
        shape = f" (circle radius {tr.R:.3f} m, start slope {tr.start_deg:g} deg)" if isinstance(tr, Arc) else ""
        print(f"{tr.name}{shape}: length {tr.length:.4f} m, arrives at {arr:.4f} s (quadrature {quad:.4f}{extra}), "
              f"energy drift {drift:.1e}")
        out["runs"].append({"track": tr, "s": ss, "arrival": arr, "quad": quad})
    line = next(r for r in out["runs"] if r["track"].name == "straight")
    cyc = next(r for r in out["runs"] if r["track"].name == "curve")
    gentle = next(r for r in out["runs"] if r["track"].name == "gentle start")
    print(f"straight slope {math.degrees(math.atan2(Y, X)):.1f} deg; the curve is {100 * (cyc['track'].length / line['track'].length - 1):.1f}% "
          f"longer than the straight slide and arrives {100 * (1 - cyc['arrival'] / line['arrival']):.1f}% sooner "
          f"(the straight slide takes {100 * (line['arrival'] / cyc['arrival'] - 1):.1f}% longer); gentle start takes "
          f"{100 * (gentle['arrival'] / cyc['arrival'] - 1):.1f}% longer than the curve")
    print(f"arrival order: " + ", ".join(f"{r['track'].name} {r['arrival']:.3f} s" for r in sorted(out["runs"], key=lambda r: r["arrival"])))
    print(f"gaps at quarter speed on screen: curve to straight {(line['arrival'] - cyc['arrival']) / man['playback']:.2f} s, "
          f"straight to gentle {(gentle['arrival'] - line['arrival']) / man['playback']:.2f} s")
    for deg in man["check_start_degs"]:
        tr = Arc(X, Y, deg, name=f"check arc {deg:g} deg")
        _, arr, _ = integrate(tr, g, race_frames, frame_dt, sub)
        print(f"check: circle with a {deg:g} deg start (radius {tr.R:.3f} m, length {tr.length:.4f} m) arrives at {arr:.4f} s, "
              f"{100 * (arr / cyc['arrival'] - 1):.1f}% after the cycloid")
    out["t_cyc"], out["t_line"], out["t_gentle"] = cyc["arrival"], line["arrival"], gentle["arrival"]
    out["longer_pct"] = 100 * (cyc["track"].length / line["track"].length - 1)
    n_races = int(man["scene_duration"] / man["race_period"])
    last_arrival = max(r["arrival"] for r in out["runs"]) / man["playback"]
    print(f"{n_races} races of {man['race_period']:g} s each; all balls home {last_arrival:.2f} s into a race, "
          f"reset over the last {man['reset_dur']:g} s of each race")
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
        self.px_per_m = TOP["width_px"] / meas["X"]
        self.lane_px_per_m = (LANES["x1"] - LANES["x0"]) / max(r["track"].length for r in meas["runs"])
        self.paths = {}
        for r in meas["runs"]:
            tr = r["track"]
            self.paths[tr.name] = [self.px(*tr.xy(s)) for s in np.linspace(0.0, tr.length, 300)]
        text = man["payoff_text"].format(cyc=meas["t_cyc"], line=meas["t_line"])
        widths = {"overlay@34": (ImageFont.truetype(font, 34), man["overlay"]), "title@60": (self.font_title, man["title"]),
                  "lane label@40": (self.font, "gentle start"), "arrival@56": (self.font_big, f"{meas['t_gentle']:.1f} s")}
        print(f"lane readout right edge: {LANES['x1'] + self.font_big.getlength(f'{meas['t_gentle']:.1f} s') / 2:.0f} px of {W}")
        for j, line in enumerate(text.split("|")):
            widths[f"payoff line {j + 1}@40"] = (self.font, line.strip())
        print("text widths: " + ", ".join(f"{k} {f.getlength(s):.0f} px" for k, (f, s) in widths.items()))

    def px(self, x: float, y: float) -> tuple[float, float]:
        sx, sy = TOP["start"]
        return sx + x * self.px_per_m, sy - y * self.px_per_m

    def race_state(self, t: float):
        """Video time -> (race index, frame into the race, reset fraction)."""
        man = self.man
        k = int(t // man["race_period"])
        tau = t - k * man["race_period"]
        f = int(round(tau * self.fps))
        reset_start = man["race_period"] - man["reset_dur"]
        u = smoothstep((tau - reset_start) / man["reset_dur"]) if tau >= reset_start else 0.0
        return k, min(f, self.meas["race_frames"] - 1), u, tau

    def ball_s(self, run: dict, f: int, u: float) -> float:
        s = float(run["s"][f])
        return s * (1.0 - u) if u > 0 else s

    def frame_at(self, fidx: int) -> np.ndarray:
        man, m = self.man, self.meas
        t = fidx / self.fps
        img = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(img)
        k, f, u, tau = self.race_state(t)
        phys_t = min(tau, max(r["arrival"] for r in m["runs"]) / man["playback"]) * man["playback"]
        last = k == int(man["scene_duration"] / man["race_period"]) - 1
        if t < man["title_until"]:
            title_alpha = 1.0 if t < man["title_until"] - 0.4 else (man["title_until"] - t) / 0.4
            hud_alpha = 0.0
        elif last and u > 0:
            title_alpha, hud_alpha = u, 1.0 - u
        else:
            title_alpha, hud_alpha = 0.0, 1.0

        def shade(col, alpha):
            return tuple(int(c * alpha + BG[j] * (1 - alpha)) for j, c in enumerate(col))

        # Top: the three slides, start and end marks.
        for r in m["runs"]:
            d.line(self.paths[r["track"].name], fill=shade(r["track"].colour, 0.45), width=8, joint="curve")
        sx, sy = self.px(0.0, 0.0)
        ex, ey = self.px(m["X"], -m["Y"])
        d.line((sx - 30, sy, sx + 30, sy), fill=MUTED, width=4)
        d.text((sx, sy - 34), "start", font=self.font_small, fill=MUTED, anchor="mm")
        d.line((ex, ey + BALL_R + 4, ex, ey + 46), fill=MUTED, width=4)
        d.text((ex, ey + 66), "end", font=self.font_small, fill=MUTED, anchor="mm")
        if title_alpha == 0:
            d.text((60, TOP["label_y"]), "three slides, one ball each", font=self.font, fill=TEAL, anchor="lm")
        if hud_alpha > 0.02 and not (last and u > 0):
            col = TEXT if u == 0 else shade(TEXT, 1 - u)
            d.text((W - 60, TOP["label_y"]), f"{phys_t:.1f} s", font=self.font_big, fill=shade(col, hud_alpha), anchor="rm")
        # Trails then balls.
        trail_frames = int(man["trail_seconds"] * self.fps)
        for r in m["runs"]:
            tr = r["track"]
            if u == 0:
                for back in range(trail_frames, 0, -1):
                    fb = f - back
                    if fb < 0:
                        continue
                    x, y = self.px(*tr.xy(float(r["s"][fb])))
                    rad = BALL_R * (1 - back / (trail_frames + 1)) * 0.8
                    d.ellipse((x - rad, y - rad, x + rad, y + rad), fill=shade(tr.colour, 0.35 * (1 - back / (trail_frames + 1))))
        for r in m["runs"]:
            tr = r["track"]
            x, y = self.px(*tr.xy(self.ball_s(r, f, u)))
            d.ellipse((x - BALL_R, y - BALL_R, x + BALL_R, y + BALL_R), fill=tr.colour)
        # Lanes: each slide unrolled to its true length, a ball per lane.
        if title_alpha == 0:
            d.text((60, LANES["label_y"]), "the same race, each slide unrolled", font=self.font, fill=TEAL, anchor="lm")
        for r, ly in zip(m["runs"], LANES["ys"]):
            tr = r["track"]
            x_end = LANES["x0"] + tr.length * self.lane_px_per_m
            d.line((LANES["x0"], ly, x_end, ly), fill=WIRE, width=10)
            d.line((x_end, ly - 26, x_end, ly + 26), fill=shade(tr.colour, 0.7), width=6)
            d.text((60, ly - 14), tr.name, font=self.font, fill=tr.colour, anchor="lm")
            d.text((60, ly + 30), f"{tr.length:.2f} m", font=self.font_small, fill=MUTED, anchor="lm")
            s = self.ball_s(r, f, u)
            x = LANES["x0"] + s * self.lane_px_per_m
            d.ellipse((x - BALL_R, ly - BALL_R, x + BALL_R, ly + BALL_R), fill=tr.colour)
            arrived = r["arrival"] / man["playback"] <= tau and u == 0
            if arrived and hud_alpha > 0.02:
                d.text((x_end, ly - 56), f"{r['arrival']:.1f} s", font=self.font_big, fill=shade(tr.colour, hud_alpha), anchor="mm")
        if title_alpha > 0.02:
            d.text((W / 2, TOP["label_y"]), man["title"], font=self.font_title, fill=shade(TEXT, title_alpha), anchor="mm")
        if man["payoff_t"] <= t < man["payoff_end"]:
            alpha = min(1.0, (t - man["payoff_t"]) / man["payoff_hold"], (man["payoff_end"] - t) / man["payoff_hold"])
            text = man["payoff_text"].format(cyc=m["t_cyc"], line=m["t_line"])
            for j, line in enumerate(text.split("|")):
                d.text((W / 2, PAYOFF_Y - 32 + j * 64), line.strip(), font=self.font, fill=shade(GOLD, alpha), anchor="mm")
        return np.asarray(img)

    def render(self, out_path: Path) -> None:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        total = int(round(self.man["scene_duration"] * self.fps))
        first = self.frame_at(0)
        last = self.frame_at(total - 1)
        diff = np.abs(first.astype(int) - last.astype(int))
        print(f"loop check: last frame differs from the first in {int((diff.max(axis=2) > 24).sum())} px "
              f"(max channel difference {int(diff.max())})")
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
    man = json.loads((ROOT / "projects/brachistochrone/manifest.json").read_text())
    meas = measure(man)
    if "--measure-only" in sys.argv:
        return
    if "--frames" in sys.argv:
        times = [float(v) for v in sys.argv[sys.argv.index("--frames") + 1].split(",")]
        r = Renderer(man, meas)
        for tv in times:
            Image.fromarray(r.frame_at(int(round(tv * man["fps"])))).save(ROOT / f"media/brachistochrone/smoke-{tv}.png")
        print("smoke frames: " + ", ".join(f"{tv}" for tv in times))
        return
    Renderer(man, meas).render(ROOT / "media/brachistochrone/footage.mp4")


if __name__ == "__main__":
    main()
