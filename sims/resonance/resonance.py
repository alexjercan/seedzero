#!/usr/bin/env python3
"""Resonance until failure: two identical weights on identical springs, the
same one-millimetre shake at the mount, one exactly at the spring's own
frequency and one a few percent faster. Measure how far each stretch grows
and when the on-tempo spring passes its limit.

Model: a mass on a linear spring with light damping, base-excited. With x
the stretch beyond rest length (mm) and the mount at y_b = A sin(w_d t),
    x'' + 2 zeta w0 x' + w0^2 x = A w_d^2 sin(w_d t).
Integrated with fixed-step RK4 (16 substeps per frame); the run is repeated
at half the step and the difference is printed. The spring snaps the first
time x exceeds limit_mm; the mass then falls freely and the run for that
panel ends. Steady-state gains from the closed form are printed alongside
as a check, never narrated.

usage: resonance.py [--measure-only]
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
RED = (232, 96, 88)
TEXT = (216, 222, 230)
MUTED = (138, 148, 163)
DIM = (70, 80, 94)
GRIDLINE = (40, 48, 58)
METAL = (170, 180, 195)

PX_PER_MM = 5.0
PANEL_X = (300.0, 780.0)
LABEL_Y = 170.0
MOUNT_Y = 290.0
REST_PX = 480.0
MASS_W, MASS_H = 120, 80
SPRING_W = 56.0
COILS = 14
READ_Y1, READ_Y2, READ_Y3 = 1172.0, 1217.0, 1262.0
CLIP_Y = 1140.0  # a falling mass slides out of view above the readouts
CHART_X0, CHART_X1, CHART_Y0, CHART_Y1 = 150, 1000, 1500, 1780
PAYOFF_Y = 1868.0
G_MM = 9810.0  # free fall after the snap, mm/s^2


def gain(r: float, zeta: float) -> float:
    return r * r / math.sqrt((1 - r * r) ** 2 + (2 * zeta * r) ** 2)


def simulate(man: dict, detune: float, duration: float, substeps: int) -> dict:
    """Fixed-step RK4. Returns per-substep arrays of t and x, cycle peaks,
    and the snap time if the stretch passes the limit."""
    f0, zeta, amp, limit = man["f0_hz"], man["zeta"], man["drive_mm"], man["limit_mm"]
    w0 = 2 * math.pi * f0
    wd = 2 * math.pi * f0 * (1 + detune)
    dt = 1.0 / (man["fps"] * substeps)
    n = int(round(duration / dt))

    def acc(t, x, v):
        return amp * wd * wd * math.sin(wd * t) - 2 * zeta * w0 * v - w0 * w0 * x

    ts = np.arange(n + 1) * dt
    xs = np.zeros(n + 1)
    x = v = 0.0
    snap_t = None
    snap_i = None
    for i in range(n):
        t = ts[i]
        k1x, k1v = v, acc(t, x, v)
        k2x, k2v = v + 0.5 * dt * k1v, acc(t + 0.5 * dt, x + 0.5 * dt * k1x, v + 0.5 * dt * k1v)
        k3x, k3v = v + 0.5 * dt * k2v, acc(t + 0.5 * dt, x + 0.5 * dt * k2x, v + 0.5 * dt * k2v)
        k4x, k4v = v + dt * k3v, acc(t + dt, x + dt * k3x, v + dt * k3v)
        x += dt * (k1x + 2 * k2x + 2 * k3x + k4x) / 6
        v += dt * (k1v + 2 * k2v + 2 * k3v + k4v) / 6
        xs[i + 1] = x
        if snap_t is None and x > limit:
            snap_t, snap_i = float(ts[i + 1]), i + 1
            break
    if snap_i is not None:
        ts, xs = ts[: snap_i + 1], xs[: snap_i + 1]
    # Peak stretch inside each drive cycle (push k covers [k/fd, (k+1)/fd)).
    fd = f0 * (1 + detune)
    cycles = np.floor(ts * fd).astype(int)
    peaks = {}
    for k in range(int(cycles.max()) + 1):
        m = cycles == k
        if m.any():
            peaks[k] = float(np.max(xs[m]))
    return {"t": ts, "x": xs, "peaks": peaks, "snap_t": snap_t, "fd": fd, "dt": dt}


def first_above(res: dict, level: float):
    idx = np.nonzero(res["x"] > level)[0]
    if len(idx) == 0:
        return None
    t = float(res["t"][idx[0]])
    return t, int(math.floor(t * res["fd"]))


def measure(man: dict) -> dict:
    f0, zeta, amp, limit = man["f0_hz"], man["zeta"], man["drive_mm"], man["limit_mm"]
    T = man["scene_duration"]
    print(f"spring: natural frequency {f0} Hz, damping ratio {zeta} (Q = {1 / (2 * zeta):.0f}), mount shake {amp} mm, "
          f"limit {limit} mm, RK4 with {man['substeps']} substeps per frame (dt = {1 / (man['fps'] * man['substeps']):.5f} s)")
    out = {}
    for name, detune in (("on", 0.0), ("off", man["detune"])):
        res = simulate(man, detune, T, man["substeps"])
        res2 = simulate(man, detune, T, 2 * man["substeps"])
        n = min(len(res["x"]), (len(res2["x"]) + 1) // 2)
        diff = float(np.max(np.abs(res["x"][:n] - res2["x"][: 2 * n: 2][:n])))
        r = 1 + detune
        print(f"{name} tempo: drive {res['fd']:.3f} Hz ({100 * detune:+.1f}%), steady-state gain from the closed form {gain(r, zeta):.1f}x "
              f"= {gain(r, zeta) * amp:.1f} mm; RK4 half-step check: max difference {diff:.2e} mm")
        pk = res["peaks"]
        # Push numbers are one-based: push n covers [(n - 1) / fd, n / fd).
        print("  peak stretch by push: " + ", ".join(f"{k + 1}: {pk[k]:.1f}" for k in sorted(pk) if k + 1 in (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 16, 21, 26, 27, 30, 40)))
        early = [pk[k + 1] - pk[k] for k in range(0, 9) if k + 1 in pk]
        print(f"  growth per push over pushes 1 to 10: min {min(early):.2f}, max {max(early):.2f} mm (pi x shake = {math.pi * amp:.2f} mm)")
        for lv in (10, 20, 30, 40, 50, limit):
            fa = first_above(res, lv)
            print(f"  first stretch above {lv:g} mm: " + ("never" if fa is None else f"{fa[0]:.2f} s, during push {fa[1] + 1}"))
        imax = int(np.argmax(res["x"]))
        print(f"  max stretch in {float(res['t'][-1]):.2f} s: {res['x'][imax]:.1f} mm at {res['t'][imax]:.2f} s")
        if res["snap_t"] is not None:
            print(f"  SNAP at {res['snap_t']:.2f} s, push {int(math.floor(res['snap_t'] * res['fd'])) + 1}")
        out[name] = res
    # The off-tempo spring for a long time: does it ever pass the limit?
    long = simulate(man, man["detune"], man["long_duration"], 4)
    imax = int(np.argmax(long["x"]))
    print(f"off tempo for {man['long_duration']:.0f} s ({long['fd'] * man['long_duration']:.0f} pushes): max stretch {long['x'][imax]:.1f} mm at {long['t'][imax]:.2f} s; "
          f"snapped: {long['snap_t'] is not None}; last 60 s peak {float(np.max(long['x'][-int(60 / long['dt']):])):.1f} mm")
    print("context (not narrated): other detunes, max stretch over the scene and over the long run")
    for det in (0.01, 0.02, 0.05, 0.10, -man["detune"]):
        a = simulate(man, det, T, 4)
        b = simulate(man, det, man["long_duration"], 4)
        print(f"  {100 * det:+.0f}%: scene max {float(np.max(a['x'])):.1f} mm{' (SNAP at %.2f s)' % a['snap_t'] if a['snap_t'] else ''}; "
              f"long max {float(np.max(b['x'])):.1f} mm{' (SNAP at %.2f s)' % b['snap_t'] if b['snap_t'] else ''}; closed-form gain {gain(1 + det, zeta) * amp:.1f} mm")
    snap = out["on"]["snap_t"]
    off_at_snap = float(np.max(out["off"]["x"][out["off"]["t"] <= snap]))
    print(f"at the snap ({snap:.2f} s) the off-tempo stretch has peaked at {off_at_snap:.1f} mm")
    out["long_max"] = float(long["x"][imax])
    return out


class Renderer:
    def __init__(self, man: dict, meas: dict):
        self.man, self.meas = man, meas
        self.fps = man["fps"]
        font = os.environ["SEED_ZERO_FONT"]
        self.font = ImageFont.truetype(font, 40)
        self.font_small = ImageFont.truetype(font, 32)
        self.font_tiny = ImageFont.truetype(font, 26)
        self.sub = man["substeps"]

    def state(self, name: str, t: float):
        res = self.meas[name]
        i = int(round(t / res["dt"]))
        snap = res["snap_t"]
        if snap is not None and t >= snap:
            return None, snap
        i = min(i, len(res["x"]) - 1)
        return float(res["x"][i]), snap

    def draw_spring(self, d, x: float, y0: float, y1: float, col, coils: int = COILS, width: int = 5):
        pts = [(x, y0), (x, y0 + 16)]
        seg = (y1 - 16 - (y0 + 16)) / coils
        for k in range(coils):
            side = SPRING_W / 2 if k % 2 == 0 else -SPRING_W / 2
            pts.append((x + side, y0 + 16 + (k + 0.5) * seg))
        pts.append((x, y1 - 16))
        pts.append((x, y1))
        d.line(pts, fill=col, width=width, joint="curve")

    def draw_panel(self, d, name: str, cx: float, t: float, label: str, sub: str, col):
        man = self.man
        res = self.meas[name]
        amp = man["drive_mm"]
        wd = 2 * math.pi * res["fd"]
        mount = MOUNT_Y + amp * math.sin(wd * t) * PX_PER_MM
        x, snap = self.state(name, t)
        d.text((cx - 200, LABEL_Y), label, font=self.font, fill=col, anchor="lm")
        d.text((cx + 200, LABEL_Y), sub, font=self.font_small, fill=MUTED, anchor="rm")
        # Mount bar and the shake track.
        d.rectangle((cx - 90, mount - 10, cx + 90, mount + 10), fill=METAL)
        d.line((cx - 200, MOUNT_Y, cx + 200, MOUNT_Y), fill=GRIDLINE, width=1)
        # Limit line.
        ly = MOUNT_Y + REST_PX + man["limit_mm"] * PX_PER_MM
        for sx in range(int(cx - 200), int(cx + 200), 24):
            d.line((sx, ly, sx + 12, ly), fill=RED, width=2)
        d.text((cx - 200, ly + 22), f"limit {man['limit_mm']:g} mm", font=self.font_tiny, fill=RED, anchor="lm")
        push = int(math.floor(t * res["fd"]))
        if x is None:
            # Snapped: a stub hangs from the mount, the mass falls.
            fall = t - snap
            top = mount + REST_PX + man["limit_mm"] * PX_PER_MM + 0.5 * G_MM * fall * fall * PX_PER_MM
            self.draw_spring(d, cx, mount + 10, mount + 10 + 0.42 * REST_PX, col, coils=6)
            if top < CLIP_Y:
                d.rectangle((cx - MASS_W / 2, top, cx + MASS_W / 2, min(top + MASS_H, CLIP_Y)), fill=col)
            d.text((cx, MOUNT_Y + REST_PX + 40), f"snapped at push {int(math.floor(snap * res['fd'])) + 1}", font=self.font, fill=RED, anchor="mm")
            d.text((cx - 200, READ_Y1), f"peak {man['limit_mm']:.1f} mm", font=self.font_small, fill=RED, anchor="lm")
            d.text((cx - 200, READ_Y2), "snapped", font=self.font_small, fill=RED, anchor="lm")
            d.text((cx - 200, READ_Y3), f"push {int(math.floor(snap * res['fd'])) + 1}  |  {res['fd']:.2f} Hz", font=self.font_small, fill=MUTED, anchor="lm")
            return
        top = mount + 10 + REST_PX + x * PX_PER_MM
        self.draw_spring(d, cx, mount + 10, top, col)
        d.rectangle((cx - MASS_W / 2, top, cx + MASS_W / 2, top + MASS_H), fill=col)
        i = int(round(t / res["dt"]))
        peak = float(np.max(res["x"][: i + 1]))
        d.text((cx - 200, READ_Y1), f"peak {peak:.1f} mm", font=self.font_small, fill=col, anchor="lm")
        d.text((cx - 200, READ_Y2), f"stretch {x:+.1f} mm", font=self.font_small, fill=TEXT, anchor="lm")
        d.text((cx - 200, READ_Y3), f"push {push + 1}  |  {res['fd']:.2f} Hz", font=self.font_small, fill=MUTED, anchor="lm")

    def frame_at(self, f: int) -> np.ndarray:
        man = self.man
        scene_t = f / self.fps
        # The shake starts at start_t so the snap lands where the narration says it.
        t = max(0.0, scene_t - man.get("start_t", 0.0))
        img = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(img)
        det = man["detune"]
        self.draw_panel(d, "on", PANEL_X[0], t, "on tempo", f"{man['f0_hz']:.2f} Hz", TEAL)
        self.draw_panel(d, "off", PANEL_X[1], t, f"{100 * det:g}% faster", f"{man['f0_hz'] * (1 + det):.2f} Hz", GOLD)
        # Chart: peak stretch per push against time, both springs.
        d.rectangle((CHART_X0, CHART_Y0, CHART_X1, CHART_Y1), outline=GRIDLINE, width=2)
        d.text((CHART_X0, CHART_Y0 - 28), "peak stretch per push", font=self.font_small, fill=MUTED, anchor="lm")
        d.text((CHART_X1, CHART_Y1 + 26), f"{man['scene_duration']:.0f} s", font=self.font_small, fill=MUTED, anchor="rm")
        d.text((CHART_X0, CHART_Y1 + 26), "0 s", font=self.font_small, fill=MUTED, anchor="lm")
        y_hi = man["limit_mm"] * 1.15

        def cx_of(tt):
            return CHART_X0 + (CHART_X1 - CHART_X0) * tt / man["scene_duration"]

        def cy_of(v):
            return CHART_Y1 - (CHART_Y1 - CHART_Y0) * min(v, y_hi) / y_hi

        for v in (20, 40, man["limit_mm"]):
            y = cy_of(v)
            d.line((CHART_X0, y, CHART_X1, y), fill=RED if v == man["limit_mm"] else GRIDLINE, width=1)
            d.text((CHART_X0 - 12, y), f"{v:g} mm", font=self.font_tiny, fill=RED if v == man["limit_mm"] else MUTED, anchor="rm")
        for name, col in (("on", TEAL), ("off", GOLD)):
            res = self.meas[name]
            pts = [(cx_of((k + 0.5) / res["fd"]), cy_of(v)) for k, v in sorted(res["peaks"].items()) if (k + 1) / res["fd"] <= t]
            if len(pts) > 1:
                d.line(pts, fill=col, width=4)
            if res["snap_t"] is not None and t >= res["snap_t"]:
                sx, sy = cx_of(res["snap_t"]), cy_of(man["limit_mm"])
                d.ellipse((sx - 9, sy - 9, sx + 9, sy + 9), fill=RED)
        if scene_t >= man["payoff_t"]:
            alpha = min(1.0, (scene_t - man["payoff_t"]) / man["payoff_hold"])
            shade = tuple(int(c * alpha + BG[i] * (1 - alpha)) for i, c in enumerate(GOLD))
            d.text((W / 2, PAYOFF_Y), man["payoff_text"], font=self.font, fill=shade, anchor="mm")
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
    man = json.loads((ROOT / "projects/resonance/manifest.json").read_text())
    meas = measure(man)
    if "--measure-only" in sys.argv:
        return
    Renderer(man, meas).render(ROOT / "media/resonance/footage.mp4")


if __name__ == "__main__":
    main()
