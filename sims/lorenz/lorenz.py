#!/usr/bin/env python3
"""Lorenz forecast horizon: know the start a thousand times better, how much
longer can you predict?

The Lorenz system

    x' = sigma (y - x),  y' = x (rho - z) - y,  z' = x y - beta z

with sigma 10, rho 28, beta 8/3, integrated with RK4 at a fixed step. A
reference run starts on the attractor (after a transient from (1, 1, 1)).
Three copies start with x moved by 1e-3, 1e-6 and 1e-9. Each copy "splits"
when its distance from the reference first reaches one unit. Measured and
printed: the split time of each copy, the gaps between them, the Lyapunov
exponent they imply, a step-halving check, nudges along y and z, an
ensemble of starts along the attractor, and the on-screen text widths. One
model time unit plays as one second of video.

usage: lorenz.py [--measure-only] [--frames t1,t2,...]
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
BACKDROP = (30, 36, 45)

COLOURS = {"a": GOLD, "b": TEAL, "c": CORAL}
RING_R = {"a": 20, "b": 14, "c": 8}
ROW_Y = {"a": 1622, "b": 1682, "c": 1742}
ROW_HEADER_Y = 1566
TITLE_Y = (186, 248)


def deriv(s: np.ndarray, sigma: float, rho: float, beta: float) -> np.ndarray:
    x, y, z = s[..., 0], s[..., 1], s[..., 2]
    return np.stack([sigma * (y - x), x * (rho - z) - y, x * y - beta * z], axis=-1)


def rk4_run(s0: np.ndarray, n: int, dt: float, p: tuple, keep: bool = True) -> np.ndarray:
    """Integrate n steps. Returns the trajectory (n + 1, ..., 3) or the final state."""
    s = np.array(s0, dtype=np.float64)
    out = np.empty((n + 1,) + s.shape) if keep else None
    for i in range(n + 1):
        if keep:
            out[i] = s
        if i == n:
            break
        k1 = deriv(s, *p)
        k2 = deriv(s + 0.5 * dt * k1, *p)
        k3 = deriv(s + 0.5 * dt * k2, *p)
        k4 = deriv(s + dt * k3, *p)
        s = s + dt / 6.0 * (k1 + 2 * k2 + 2 * k3 + k4)
    return out if keep else s


def crossing(d: np.ndarray, level: float, dt: float) -> float | None:
    idx = np.nonzero((d[:-1] < level) & (d[1:] >= level))[0]
    if len(idx) == 0:
        return None
    i = idx[0]
    return (i + (level - d[i]) / (d[i + 1] - d[i])) * dt


def ensemble(starts: np.ndarray, man: dict, p: tuple, dt: float, horizon: float) -> np.ndarray:
    """Split times (nudge, start) for every start integrated together."""
    ns = len(starts)
    thr = man["threshold"]
    names = list(man["nudges"])
    st = np.concatenate([starts] + [starts + np.array([eps, 0.0, 0.0]) for eps in man["nudges"].values()])
    split_t = np.full((len(names), ns), np.nan)
    prev = np.zeros((len(names), ns))
    for i in range(int(round(horizon / dt))):
        k1 = deriv(st, *p)
        k2 = deriv(st + 0.5 * dt * k1, *p)
        k3 = deriv(st + 0.5 * dt * k2, *p)
        k4 = deriv(st + dt * k3, *p)
        st = st + dt / 6.0 * (k1 + 2 * k2 + 2 * k3 + k4)
        refe = st[:ns]
        for j in range(len(names)):
            d = np.linalg.norm(st[(j + 1) * ns:(j + 2) * ns] - refe, axis=1)
            new = np.isnan(split_t[j]) & (d >= thr)
            if new.any():
                frac = (thr - prev[j][new]) / (d[new] - prev[j][new])
                split_t[j][new] = (i + frac) * dt
            prev[j] = d
    return split_t


def measure(man: dict) -> dict:
    p = (man["sigma"], man["rho"], man["beta"])
    steps = man["fps"] * man["substeps"]
    dt = 1.0 / steps
    dur = man["scene_duration"]
    thr = man["threshold"]
    names = list(man["nudges"])
    print(f"model: Lorenz sigma {p[0]:g}, rho {p[1]:g}, beta {p[2]:.4f}; RK4 at {steps} steps per time unit; "
          f"one time unit plays as one second; deterministic, no seed")
    base = rk4_run(np.array([1.0, 1.0, 1.0]), int(round(man["transient"] * steps)), dt, p, keep=False)
    # Candidate starts spaced along the attractor; the ensemble gives the average law and picks the start.
    ns = man["check_starts"]
    spacing = man["check_start_spacing"]
    starts = np.empty((ns, 3))
    s = base.copy()
    nsp = int(round(spacing * steps))
    for i in range(ns):
        starts[i] = s
        s = rk4_run(s, nsp, dt, p, keep=False)
    split_t = ensemble(starts, man, p, dt, 30.0)
    means = np.nanmean(split_t, axis=1)
    for j, name in enumerate(names):
        v = split_t[j]
        print(f"ensemble, {ns} starts spaced {spacing:g} s along the attractor from a {man['transient']:g} s transient, "
              f"copy {name} (x moved by {man['nudges'][name]:g}): distance reaches {thr:g} at {means[j]:.3f} s on average "
              f"(sd {np.nanstd(v):.3f}, min {np.nanmin(v):.3f}, max {np.nanmax(v):.3f}"
              f"{'' if not np.isnan(v).any() else f', {int(np.isnan(v).sum())} unsplit in 30 s'})")
    g1 = split_t[1] - split_t[0]
    g2 = split_t[2] - split_t[1]
    allg = np.concatenate([g1, g2])
    ens_gap = float(np.nanmean(allg))
    print(f"ensemble gaps: {np.nanmean(g1):.3f} s (sd {np.nanstd(g1):.3f}) and {np.nanmean(g2):.3f} s "
          f"(sd {np.nanstd(g2):.3f}); mean gap {ens_gap:.3f} s, so a thousandfold in precision buys {ens_gap:.1f} s "
          f"on average; implied growth rate {math.log(1000.0) / ens_gap:.4f} per unit time (Lorenz's largest "
          f"Lyapunov exponent is about 0.9056); both gaps within 1 s of the mean in "
          f"{int(np.sum((np.abs(g1 - ens_gap) < 1) & (np.abs(g2 - ens_gap) < 1)))} of {ns} starts")
    # Pick the start whose three split times are closest to the ensemble averages.
    score = np.nansum((split_t - means[:, None]) ** 2, axis=0)
    score[np.isnan(split_t).any(axis=0)] = np.inf
    k = int(np.argmin(score))
    r0 = starts[k]
    print(f"start for the video: candidate {k} of {ns} (transient {man['transient'] + k * spacing:.2f} s), the start "
          f"whose split times are closest to the ensemble averages: ({r0[0]:.6f}, {r0[1]:.6f}, {r0[2]:.6f}); "
          f"its ensemble split times {', '.join(f'{split_t[j][k]:.3f}' for j in range(len(names)))} s")
    n = int(round(dur * steps))
    ref = rk4_run(r0, n, dt, p)
    runs: dict[str, dict] = {}
    for name, eps in man["nudges"].items():
        traj = rk4_run(r0 + np.array([eps, 0.0, 0.0]), n, dt, p)
        d = np.linalg.norm(traj - ref, axis=1)
        split = crossing(d, thr, dt)
        marks = {lvl: crossing(d, lvl, dt) for lvl in (0.01, 0.1, 10.0)}
        runs[name] = {"traj": traj, "dist": d, "split": split, "eps": eps}
        print(f"copy {name}: x moved by {eps:g} ({man['nudge_labels'][name]}); distance reaches {thr:g} at "
              f"{split:.4f} s; 0.01 at {marks[0.01]:.3f} s, 0.1 at {marks[0.1]:.3f} s, 10 at {marks[10.0]:.3f} s; "
              f"largest distance in {dur:g} s: {d.max():.2f}")
    splits = [runs[k]["split"] for k in names]
    gaps = [splits[1] - splits[0], splits[2] - splits[1]]
    mean_gap = sum(gaps) / 2
    print(f"gaps between the splits in the video: {gaps[0]:.4f} s and {gaps[1]:.4f} s (mean {mean_gap:.4f}); "
          f"implied growth rate {math.log(1000.0) / mean_gap:.4f} per unit time")
    # Checks from the same start.
    fine = man["check_steps_per_second"]
    dtf = 1.0 / fine
    nf = int(round(dur * fine))
    reff = rk4_run(r0, nf, dtf, p)
    parts = []
    for name, eps in man["nudges"].items():
        traj = rk4_run(r0 + np.array([eps, 0.0, 0.0]), nf, dtf, p)
        parts.append(f"{name} {crossing(np.linalg.norm(traj - reff, axis=1), thr, dtf):.4f} s")
    print(f"check, the same start at {fine} steps per unit: splits " + ", ".join(parts))
    for axis, label in ((1, "y"), (2, "z")):
        parts = []
        for name, eps in man["nudges"].items():
            s0 = r0.copy()
            s0[axis] += eps
            traj = rk4_run(s0, n, dt, p)
            parts.append(f"{name} {crossing(np.linalg.norm(traj - ref, axis=1), thr, dt):.4f} s")
        print(f"check, the same nudges along {label} instead of x: splits " + ", ".join(parts))
    backdrop = rk4_run(r0, int(round(man["backdrop_duration"] * steps)), dt, p)
    # Pre-roll: the path leading into the start, so the copies are already moving at frame 0.
    n_pre = int(round(man["preroll"] * steps))
    m = int(math.ceil(n_pre / nsp))
    pre = rk4_run(starts[k - m], m * nsp, dt, p)
    assert np.array_equal(pre[-1], r0), "pre-roll must land exactly on the start"
    pre = pre[len(pre) - 1 - n_pre:-1]
    print(f"pre-roll: {man['preroll']:g} s of the reference path before the start, landing exactly on it; "
          f"the copies start (and the stopwatches) at {man['preroll']:g} s of video, so the splits show at "
          + ", ".join(f"{man['preroll'] + s:.1f}" for s in splits) + " s of video")
    return {"ref": ref, "runs": runs, "splits": dict(zip(names, splits)), "gaps": gaps,
            "gap": mean_gap, "ens_gap": ens_gap, "ens_means": means, "backdrop": backdrop, "dt": dt,
            "pre": pre}


class Renderer:
    def __init__(self, man: dict, meas: dict):
        self.man, self.meas = man, meas
        self.fps = man["fps"]
        self.steps = man["fps"] * man["substeps"]
        font = os.environ["SEED_ZERO_FONT"]
        self.font = ImageFont.truetype(font, 40)
        self.font_small = ImageFont.truetype(font, 32)
        self.font_title = ImageFont.truetype(font, 48)
        self.font_read = ImageFont.truetype(font, 48)
        self.first = None
        self.scale = man["px_per_unit"]
        self.cx, self.cy = man["view_centre"]
        pre = meas["pre"]
        self.n_pre = len(pre)
        self.screen = {k: self.to_screen(np.concatenate([pre, v["traj"]])) for k, v in meas["runs"].items()}
        self.screen["ref"] = self.to_screen(np.concatenate([pre, meas["ref"]]))
        self.start_xy = tuple(self.screen["ref"][self.n_pre])
        self.backdrop = self.make_backdrop()
        widths = {"overlay@34": (ImageFont.truetype(font, 34), man["overlay"])}
        for j, line in enumerate(man["title"].split("|")):
            widths[f"title line {j + 1}@48"] = (self.font_title, line)
        for j, line in enumerate(self.payoff_lines()):
            widths[f"payoff line {j + 1}@40"] = (self.font, line)
        for k in ("a", "b", "c"):
            widths[f"row {k}@40"] = (self.font, f"{man['nudge_labels'][k]}    split at {meas['splits'][k]:.1f} s")
        print("text widths: " + ", ".join(f"{k} {f.getlength(s):.0f} px" for k, (f, s) in widths.items()))
        sx = np.concatenate([v[:, 0] for v in self.screen.values()])
        sy = np.concatenate([v[:, 1] for v in self.screen.values()])
        print(f"screen extent of the paths: x {sx.min():.0f} to {sx.max():.0f}, y {sy.min():.0f} to {sy.max():.0f}")

    def to_screen(self, traj: np.ndarray) -> np.ndarray:
        out = np.empty((len(traj), 2))
        out[:, 0] = self.cx + traj[:, 0] * self.scale
        out[:, 1] = self.cy - traj[:, 2] * self.scale
        return out

    def make_backdrop(self) -> Image.Image:
        img = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(img)
        pts = self.to_screen(self.meas["backdrop"][::10])
        d.line([tuple(q) for q in pts], fill=BACKDROP, width=2)
        return img

    def payoff_lines(self) -> list[str]:
        s = self.meas["splits"]
        text = self.man["payoff_text"].format(gap=self.meas["gap"], a=s["a"], b=s["b"], c=s["c"])
        return [q.strip() for q in text.split("|")]

    @staticmethod
    def blend(col: tuple, alpha: float) -> tuple:
        return tuple(int(c * alpha + BG[j] * (1 - alpha)) for j, c in enumerate(col))

    def draw_trail(self, d: ImageDraw.ImageDraw, key: str, i: int, col: tuple, width: int) -> None:
        n_trail = int(self.man["trail_seconds"] * self.steps)
        lo = max(0, i - n_trail)
        pts = self.screen[key][lo:i + 1:8]
        if len(pts) < 2:
            return
        segs = 8
        per = max(2, math.ceil(len(pts) / segs))
        for s in range(segs):
            a, b = s * per, min(len(pts), (s + 1) * per + 1)
            if b - a < 2:
                continue
            alpha = 0.15 + 0.85 * (s + 1) / segs
            d.line([tuple(q) for q in pts[a:b]], fill=self.blend(col, alpha), width=width)

    def live_frame(self, f: int) -> Image.Image:
        man, m = self.man, self.meas
        t = f / self.fps
        tm = t - man["preroll"]  # model time since the copies started
        i = min(int(round(t * self.steps)), len(self.screen["ref"]) - 1)
        img = self.backdrop.copy()
        d = ImageDraw.Draw(img)
        order = ("a", "b", "c")
        # Start marker where the copies begin, shown for a few seconds after they start.
        if 0 <= tm < 4.0:
            alpha = min(1.0, tm / 0.3, (4.0 - tm) / 0.5)
            sx, sy = self.start_xy
            col = self.blend(TEXT, alpha)
            d.ellipse((sx - 30, sy - 30, sx + 30, sy + 30), outline=col, width=3)
            d.text((sx + 40, sy - 34), "start", font=self.font_small, fill=col, anchor="lm", stroke_width=3, stroke_fill=BG)
        for k in order:
            self.draw_trail(d, k, i, COLOURS[k], 3)
        self.draw_trail(d, "ref", i, TEXT, 3)
        for k in order:
            x, y = self.screen[k][i]
            r = RING_R[k]
            d.ellipse((x - r, y - r, x + r, y + r), outline=COLOURS[k], width=4)
        x, y = self.screen["ref"][i]
        d.ellipse((x - 4, y - 4, x + 4, y + 4), fill=TEXT)
        # Title, then payoff in the same place.
        payoff_t = man["preroll"] + m["splits"]["c"] + man["payoff_delay"]
        if t < man["title_until"]:
            alpha = 1.0 if t < man["title_until"] - 0.4 else (man["title_until"] - t) / 0.4
            for j, line in enumerate(man["title"].split("|")):
                d.text((W / 2, TITLE_Y[j]), line, font=self.font_title, fill=self.blend(TEXT, alpha), anchor="mm")
        elif t >= payoff_t:
            alpha = min(1.0, (t - payoff_t) / man["payoff_hold"])
            for j, line in enumerate(self.payoff_lines()):
                d.text((W / 2, TITLE_Y[j]), line, font=self.font, fill=self.blend(GOLD, alpha), anchor="mm")
        # Rows: label, ring icon, stopwatch that freezes at the split.
        d.text((60, ROW_HEADER_Y), "start off by", font=self.font_small, fill=MUTED, anchor="lm")
        d.text((W - 60, ROW_HEADER_Y), "splits at", font=self.font_small, fill=MUTED, anchor="rm")
        for k in order:
            y = ROW_Y[k]
            col = COLOURS[k]
            r = RING_R[k] * 0.7
            d.ellipse((84 - r, y - r, 84 + r, y + r), outline=col, width=3)
            d.text((124, y), man["nudge_labels"][k], font=self.font, fill=TEXT, anchor="lm")
            split = m["splits"][k]
            if tm < split:
                d.text((W - 60, y), f"{max(0.0, tm):.1f} s", font=self.font_read, fill=MUTED, anchor="rm")
            else:
                flash = min(1.0, (tm - split) / 0.3)
                d.text((W - 60, y), f"{split:.1f} s", font=self.font_read, fill=self.blend(col, 0.6 + 0.4 * flash), anchor="rm")
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
    man = json.loads((ROOT / "projects/lorenz/manifest.json").read_text())
    meas = measure(man)
    if "--measure-only" in sys.argv:
        return
    if "--frames" in sys.argv:
        times = [float(v) for v in sys.argv[sys.argv.index("--frames") + 1].split(",")]
        r = Renderer(man, meas)
        for tv in times:
            Image.fromarray(r.frame_at(int(round(tv * man["fps"])))).save(ROOT / f"media/lorenz/smoke-{tv}.png")
        print("smoke frames: " + ", ".join(f"{tv}" for tv in times))
        return
    Renderer(man, meas).render(ROOT / "media/lorenz/footage.mp4")


if __name__ == "__main__":
    main()
