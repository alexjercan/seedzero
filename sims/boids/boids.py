#!/usr/bin/env python3
"""Boids flock snap: simulation, measurement, and footage.

Two hundred boids start scattered with random headings. Three rules run:
separation, alignment, cohesion. Polarization (how much the headings
agree, 0 to 1) is measured every frame. The sim finds the snap: the
first moment polarization holds above the threshold for a full second.
Mid-scene the alignment rule toggles off and the flock falls apart, then
toggles back on and the flock re-forms. All boundaries and measurements
come from the seeded run.

usage: boids.py [--measure-only]
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent.parent
W, H = 1080, 1920

BG = (11, 14, 18)
BIRD = (216, 222, 230)
ACCENT = (92, 200, 165)
WARN = (222, 186, 92)
MUTED = (138, 148, 163)
GRID = (70, 80, 94)
PILL_OFF = (40, 47, 56)

# Layout. The caption band burned in by compose.sh sits at y = 1344..1420;
# nothing draws text there.
ARENA = (60.0, 330.0, 1020.0, 1290.0)
PILL_XS = (270.0, 540.0, 810.0)
PILL_Y, PILL_W, PILL_H = 205.0, 264.0, 64.0
METER_LABEL_Y = 1495.0
CURVE_X0, CURVE_X1 = 140.0, 940.0
CURVE_Y0, CURVE_Y1 = 1555.0, 1815.0
PAYOFF_Y = 1868.0

# Timeline (seconds).
INTRO_HOLD = 2.0
RESET_GAP = 0.5
LABEL_FADE = 0.6

# Flock physics (px, seconds). The arena wraps around (toroidal world);
# neighbor offsets use the minimum-image convention.
R_SEP, R_ALI, R_COH = 42.0, 95.0, 115.0
W_SEP, W_ALI, W_COH = 1.7, 1.3, 0.9
V_MIN, V_MAX = 160.0, 260.0
F_MAX = 640.0
NOISE_DEG = 0.0  # per-frame heading jitter (Vicsek-style), seeded
SNAP_P = 0.9
SNAP_HOLD = 1.0


def limit(vec: np.ndarray, cap: float) -> np.ndarray:
    mag = np.linalg.norm(vec, axis=1, keepdims=True)
    over = mag > cap
    return np.where(over, vec / np.maximum(mag, 1e-9) * cap, vec)


def simulate(manifest: dict):
    """Run the full scene; return positions, headings, polarization per frame."""
    rng = np.random.RandomState(manifest["seed"])
    n = manifest["boids"]
    fps = manifest["fps"]
    frames = int(round(manifest["scene_duration"] * fps))
    off_f = int(round(manifest["align_off"] * fps))
    on_f = int(round(manifest["align_on"] * fps))
    dt = 1.0 / fps

    x0, y0, x1, y1 = ARENA
    box = np.array([x1 - x0, y1 - y0])
    pos = np.stack([rng.uniform(0, box[0], n),
                    rng.uniform(0, box[1], n)], axis=1)
    theta = rng.uniform(0, 2 * np.pi, n)
    speed = rng.uniform(V_MIN, V_MAX, n)
    vel = np.stack([np.cos(theta), np.sin(theta)], axis=1) * speed[:, None]

    all_pos = np.empty((frames, n, 2))
    all_head = np.empty((frames, n, 2))
    pol = np.empty(frames)

    for f in range(frames):
        align_on = f < off_f or f >= on_f
        diff = pos[None, :, :] - pos[:, None, :]
        diff -= np.round(diff / box) * box  # minimum-image wrap
        dist = np.linalg.norm(diff, axis=2)
        np.fill_diagonal(dist, np.inf)

        force = np.zeros((n, 2))
        # Separation: push away from close neighbors, weighted by 1/dist.
        close = dist < R_SEP
        if close.any():
            away = -diff / np.maximum(dist, 1e-9)[:, :, None] ** 2
            away = np.where(close[:, :, None], away, 0.0).sum(axis=1)
            cnt = close.sum(axis=1, keepdims=True)
            has = cnt[:, 0] > 0
            desired = away[has] / np.maximum(
                np.linalg.norm(away[has], axis=1, keepdims=True), 1e-9) * V_MAX
            force[has] += W_SEP * limit(desired - vel[has], F_MAX)
        # Alignment: steer toward the mean neighbor velocity.
        if align_on:
            near = dist < R_ALI
            cnt = near.sum(axis=1, keepdims=True)
            has = cnt[:, 0] > 0
            mean_v = np.where(near[:, :, None], vel[None, :, :], 0.0).sum(axis=1)
            mean_v = mean_v[has] / cnt[has]
            desired = mean_v / np.maximum(
                np.linalg.norm(mean_v, axis=1, keepdims=True), 1e-9) * V_MAX
            force[has] += W_ALI * limit(desired - vel[has], F_MAX)
        # Cohesion: steer toward the mean neighbor position.
        near = dist < R_COH
        cnt = near.sum(axis=1, keepdims=True)
        has = cnt[:, 0] > 0
        to_c = np.where(near[:, :, None], diff, 0.0).sum(axis=1)
        to_c = to_c[has] / cnt[has]
        desired = to_c / np.maximum(
            np.linalg.norm(to_c, axis=1, keepdims=True), 1e-9) * V_MAX
        force[has] += W_COH * limit(desired - vel[has], F_MAX)

        vel = vel + force * dt
        jitter = rng.normal(0.0, np.deg2rad(NOISE_DEG), n)
        cj, sj = np.cos(jitter), np.sin(jitter)
        vel = np.stack([vel[:, 0] * cj - vel[:, 1] * sj,
                        vel[:, 0] * sj + vel[:, 1] * cj], axis=1)
        spd = np.linalg.norm(vel, axis=1, keepdims=True)
        vel = vel / np.maximum(spd, 1e-9) * np.clip(spd, V_MIN, V_MAX)
        pos = np.mod(pos + vel * dt, box)

        head = vel / np.maximum(np.linalg.norm(vel, axis=1, keepdims=True), 1e-9)
        all_pos[f] = pos
        all_head[f] = head
        pol[f] = np.linalg.norm(head.mean(axis=0))

    return all_pos, all_head, pol


def sustained_cross(pol: np.ndarray, start_f: int, fps: int) -> int:
    """First frame >= start_f where pol holds >= SNAP_P for SNAP_HOLD seconds."""
    hold = int(SNAP_HOLD * fps)
    above = pol >= SNAP_P
    run = 0
    for f in range(start_f, len(pol)):
        run = run + 1 if above[f] else 0
        if run >= hold:
            return f - hold + 1
    return -1


def measure_report(manifest: dict, pol: np.ndarray) -> dict:
    fps = manifest["fps"]
    off_f = int(round(manifest["align_off"] * fps))
    on_f = int(round(manifest["align_on"] * fps))
    snap_f = sustained_cross(pol, 0, fps)
    resnap_f = sustained_cross(pol, on_f, fps)
    m = {
        "p_start": float(pol[0]),
        "snap_s": snap_f / fps if snap_f >= 0 else None,
        "p_before_off": float(pol[off_f - 1]),
        "p_min_off": float(pol[off_f:on_f].min()),
        "resnap_s": (resnap_f - on_f) / fps if resnap_f >= 0 else None,
        "p_end": float(pol[-1]),
    }
    print(f"boids: {manifest['boids']}  seed: {manifest['seed']}")
    print(f"polarization at start: {m['p_start']:.3f}")
    print(f"snap (first {SNAP_HOLD:.0f}s hold above {SNAP_P}): "
          f"{m['snap_s']:.2f}s" if m["snap_s"] is not None else "snap: never")
    print(f"polarization before alignment off ({manifest['align_off']}s): "
          f"{m['p_before_off']:.3f}")
    print(f"polarization min while alignment off: {m['p_min_off']:.3f}")
    print(f"re-snap after alignment on ({manifest['align_on']}s): "
          f"{m['resnap_s']:.2f}s after toggle"
          if m["resnap_s"] is not None else "re-snap: never")
    print(f"polarization at end: {m['p_end']:.3f}")
    return m


class Renderer:
    def __init__(self, manifest, all_pos, all_head, pol, meas):
        self.man = manifest
        self.fps = manifest["fps"]
        self.scene_dur = manifest["scene_duration"]
        self.frames = len(pol)
        self.all_pos, self.all_head, self.pol = all_pos, all_head, pol
        self.meas = meas
        self.font = ImageFont.truetype(os.environ["SEED_ZERO_FONT"], 42)
        self.font_small = ImageFont.truetype(os.environ["SEED_ZERO_FONT"], 36)
        self.font_big = ImageFont.truetype(os.environ["SEED_ZERO_FONT"], 58)

    def align_on_at(self, s: float) -> bool:
        return s < self.man["align_off"] or s >= self.man["align_on"]

    def draw_pills(self, d, s: float):
        labels = ("separation", "alignment", "cohesion")
        for i, (x, label) in enumerate(zip(PILL_XS, labels)):
            on = True if i != 1 else self.align_on_at(s)
            x0, y0 = x - PILL_W / 2, PILL_Y - PILL_H / 2
            x1, y1 = x + PILL_W / 2, PILL_Y + PILL_H / 2
            if on:
                d.rounded_rectangle((x0, y0, x1, y1), 32, fill=ACCENT)
                d.text((x, PILL_Y), label, font=self.font_small, fill=BG, anchor="mm")
            else:
                d.rounded_rectangle((x0, y0, x1, y1), 32, outline=WARN, width=3)
                d.text((x, PILL_Y), label, font=self.font_small, fill=WARN, anchor="mm")
        if not self.align_on_at(s):
            d.text((PILL_XS[1], PILL_Y + 62), "off", font=self.font_small,
                   fill=WARN, anchor="mm")

    def draw_arena(self, d, f: int):
        d.rounded_rectangle(ARENA, 18, outline=GRID, width=3)
        pos, head = self.all_pos[f], self.all_head[f]
        for (px, py), (ux, uy) in zip(pos + np.array(ARENA[:2]), head):
            wx, wy = -uy, ux
            d.polygon(
                [(px + ux * 13, py + uy * 13),
                 (px - ux * 7 + wx * 6, py - uy * 7 + wy * 6),
                 (px - ux * 7 - wx * 6, py - uy * 7 - wy * 6)],
                fill=BIRD)

    def draw_meter(self, d, f: int, label_alpha: float):
        pct = int(round(self.pol[f] * 100))
        d.text((CURVE_X0, METER_LABEL_Y), "in sync", font=self.font_small,
               fill=MUTED, anchor="lm")
        d.text((CURVE_X1, METER_LABEL_Y), f"{pct}%", font=self.font_big,
               fill=ACCENT, anchor="rm")
        # Grid: 0 and 100 solid, snap threshold dashed.
        for p, col in ((0.0, GRID), (1.0, GRID)):
            y = CURVE_Y1 - p * (CURVE_Y1 - CURVE_Y0)
            d.line((CURVE_X0, y, CURVE_X1, y), fill=col, width=2)
        y90 = CURVE_Y1 - SNAP_P * (CURVE_Y1 - CURVE_Y0)
        for x in range(int(CURVE_X0), int(CURVE_X1), 26):
            d.line((x, y90, x + 13, y90), fill=GRID, width=2)
        d.text((CURVE_X1 + 14, y90), "90", font=self.font_small, fill=MUTED,
               anchor="lm")
        # Polarization curve up to the current frame.
        step = max(1, self.frames // 400)
        pts = []
        for g in range(0, f + 1, step):
            x = CURVE_X0 + (g / (self.frames - 1)) * (CURVE_X1 - CURVE_X0)
            y = CURVE_Y1 - self.pol[g] * (CURVE_Y1 - CURVE_Y0)
            pts.append((x, y))
        if len(pts) >= 2:
            d.line(pts, fill=ACCENT, width=5)
        # Snap marker.
        if self.meas["snap_s"] is not None and f / self.fps >= self.meas["snap_s"]:
            xs = CURVE_X0 + (self.meas["snap_s"] / self.scene_dur) * (CURVE_X1 - CURVE_X0)
            d.line((xs, CURVE_Y0 - 8, xs, CURVE_Y1), fill=BIRD, width=3)
            d.text((xs, CURVE_Y0 - 34), "snap", font=self.font_small,
                   fill=BIRD, anchor="mm")
        if label_alpha > 0:
            shade = tuple(int(v * label_alpha + BG[i] * (1 - label_alpha))
                          for i, v in enumerate(BIRD))
            line = (f"{self.meas['p_start'] * 100:.0f}% to "
                    f"{self.meas['p_before_off'] * 100:.0f}% in "
                    f"{self.meas['snap_s']:.1f}s - no leader")
            d.text((W / 2, PAYOFF_Y), line, font=self.font, fill=shade, anchor="mm")

    def frame_at(self, s: float) -> np.ndarray:
        frame = np.zeros((H, W, 3), dtype=np.uint8)
        frame[:, :] = BG
        img = Image.fromarray(frame)
        d = ImageDraw.Draw(img)
        f = min(self.frames - 1, max(0, int(round(s * self.fps))))
        alpha = min(1.0, max(0.0, (s - self.man["payoff_fade"]) / LABEL_FADE))
        self.draw_pills(d, s)
        self.draw_arena(d, f)
        self.draw_meter(d, f, alpha)
        return np.asarray(img)

    def render(self, out_path: Path) -> None:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        total = int(round((INTRO_HOLD + RESET_GAP + self.scene_dur) * self.fps))
        proc = subprocess.Popen(
            ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
             "-s", f"{W}x{H}", "-r", str(self.fps), "-i", "-",
             "-c:v", "libx264", "-crf", "16", "-preset", "medium",
             "-pix_fmt", "yuv420p", str(out_path)],
            stdin=subprocess.PIPE,
        )
        assert proc.stdin is not None
        end_s = (self.frames - 1) / self.fps
        for f in range(total):
            t = f / self.fps
            if t < INTRO_HOLD:
                frame = self.frame_at(end_s)
            elif t < INTRO_HOLD + RESET_GAP:
                frame = self.frame_at(0.0)
            else:
                frame = self.frame_at(t - INTRO_HOLD - RESET_GAP)
            proc.stdin.write(frame.tobytes())
            if f % 300 == 0:
                print(f"frame {f}/{total}", file=sys.stderr)
        proc.stdin.close()
        if proc.wait() != 0:
            raise RuntimeError("ffmpeg failed")
        print(f"footage: {out_path} ({total / self.fps:.2f}s at {self.fps} fps)")


def main() -> None:
    manifest = json.loads((ROOT / "projects/boids/manifest.json").read_text())
    all_pos, all_head, pol = simulate(manifest)
    meas = measure_report(manifest, pol)
    if "--measure-only" in sys.argv:
        return
    Renderer(manifest, all_pos, all_head, pol, meas).render(
        ROOT / "media/boids/footage.mp4")


if __name__ == "__main__":
    main()
