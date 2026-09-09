#!/usr/bin/env python3
"""Dzhanibekov flip: which one flips?

Two identical bricks in zero g, sides 1 by 2 by 3, each spun at the same
rate with the same tiny wobble. The top brick spins about its long axis
(the smallest moment of inertia). The bottom brick spins about its middle
axis (the intermediate moment). Euler's rigid-body equations in the body
frame plus a unit quaternion for the orientation, RK4 at a fixed step.
The camera looks along the angular momentum, tilted, and the two faces
that the spin axis passes through are teal (front) and gold (back), so a
flip shows as the brick turning its gold face to the camera.

Measured and printed: the moments of inertia, the predicted growth rate,
every flip time (the body spin axis crossing ninety degrees from the
angular momentum), the flip period, the flips inside the short, how long
one flip takes, the largest tilt of the long-axis brick, energy and
angular momentum drift, and checks at other wobbles and about the thin
axis.

usage: dzhanibekov.py [--measure-only]
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
SIDE = (150, 158, 170)
ROD = (232, 96, 88)

# Layout: two panels, captions between them at caption_y 0.49 (y 941..1021).
PANELS = {"long": {"label_y": 214, "cy": 610}, "middle": {"label_y": 1104, "cy": 1500}}
PX_PER_UNIT = 105.0
STRIP_Y = {"long": 880, "middle": 1770}
PAYOFF_Y = 1836.0


def quat_mul(p: np.ndarray, q: np.ndarray) -> np.ndarray:
    w1, x1, y1, z1 = p
    w2, x2, y2, z2 = q
    return np.array([
        w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2,
        w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2,
        w1 * y2 - x1 * z2 + y1 * w2 + z1 * x2,
        w1 * z2 + x1 * y2 - y1 * x2 + z1 * w2,
    ])


def quat_to_matrix(q: np.ndarray) -> np.ndarray:
    w, x, y, z = q
    return np.array([
        [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
        [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
        [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)],
    ])


def quat_axis_angle(axis: np.ndarray, angle: float) -> np.ndarray:
    axis = axis / np.linalg.norm(axis)
    return np.concatenate([[math.cos(angle / 2)], math.sin(angle / 2) * axis])


def derivative(state: np.ndarray, inertia: np.ndarray) -> np.ndarray:
    w, q = state[:3], state[3:]
    dw = np.cross(inertia * w, w) / inertia
    dq = 0.5 * quat_mul(q, np.array([0.0, w[0], w[1], w[2]]))
    return np.concatenate([dw, dq])


def rk4(state: np.ndarray, dt: float, inertia: np.ndarray) -> np.ndarray:
    k1 = derivative(state, inertia)
    k2 = derivative(state + 0.5 * dt * k1, inertia)
    k3 = derivative(state + 0.5 * dt * k2, inertia)
    k4 = derivative(state + dt * k3, inertia)
    out = state + dt / 6.0 * (k1 + 2 * k2 + 2 * k3 + k4)
    out[3:] /= np.linalg.norm(out[3:])
    return out


def simulate(inertia: np.ndarray, axis: int, spin: float, wobble: float, q0: np.ndarray,
             duration: float, fps: int, substeps: int) -> dict:
    """Spin about body axis `axis` at `spin` rad/s with `wobble` rad/s on the
    other two axes. Returns per-frame quaternions and the tilt of the body
    spin axis away from the angular momentum, plus conservation checks."""
    dt = 1.0 / (fps * substeps)
    frames = int(round(duration * fps))
    w0 = np.full(3, wobble)
    w0[axis] = spin
    state = np.concatenate([w0, q0])
    L0 = quat_to_matrix(q0) @ (inertia * w0)
    L_dir = L0 / np.linalg.norm(L0)
    E0 = 0.5 * float(w0 @ (inertia * w0))
    quats = np.empty((frames, 4))
    tilt = np.empty(frames)
    fine_tilt = []
    max_dE = max_dL = max_dLdir = 0.0
    for f in range(frames):
        quats[f] = state[3:]
        R = quat_to_matrix(state[3:])
        tilt[f] = math.degrees(math.acos(max(-1.0, min(1.0, float(R[:, axis] @ L_dir)))))
        for _ in range(substeps):
            state = rk4(state, dt, inertia)
            R = quat_to_matrix(state[3:])
            fine_tilt.append(float(R[:, axis] @ L_dir))
            w = state[:3]
            L = R @ (inertia * w)
            max_dE = max(max_dE, abs(0.5 * float(w @ (inertia * w)) - E0) / E0)
            max_dL = max(max_dL, abs(np.linalg.norm(L) - np.linalg.norm(L0)) / np.linalg.norm(L0))
            max_dLdir = max(max_dLdir, float(np.linalg.norm(L / np.linalg.norm(L) - L_dir)))
    cos_t = np.array(fine_tilt)
    flips = []
    for i in range(1, len(cos_t)):
        if (cos_t[i - 1] > 0) != (cos_t[i] > 0):
            flips.append((i + (0 - cos_t[i - 1]) / (cos_t[i] - cos_t[i - 1])) * dt)
    # How long one flip takes: from 10 to 170 degrees of tilt around each crossing.
    deg = np.degrees(np.arccos(np.clip(cos_t, -1, 1)))
    durations = []
    for tf in flips:
        i = int(tf / dt)
        a = i
        while a > 0 and deg[a] > 10 and deg[a] < 170:
            a -= 1
        b = i
        while b < len(deg) - 1 and deg[b] > 10 and deg[b] < 170:
            b += 1
        durations.append((b - a) * dt)
    return {"quats": quats, "tilt": tilt, "flips": np.array(flips), "durations": np.array(durations),
            "max_tilt": float(tilt.max()), "dE": max_dE, "dL": max_dL, "dLdir": max_dLdir, "L_dir": L_dir}


def measure(man: dict) -> dict:
    a, b, c = man["sides"]
    inertia = np.array([(b * b + c * c) / 12, (a * a + c * c) / 12, (a * a + b * b) / 12])
    spin = 2 * math.pi * man["turns_per_second"]
    eps = man["wobble_rad_s"]
    fps, sub, dur = man["fps"], man["substeps"], man["scene_duration"]
    order = np.argsort(inertia)
    i_small, i_mid, i_big = inertia[order]
    lam = spin * math.sqrt((i_mid - i_small) * (i_big - i_mid) / (i_small * i_big))
    print(f"brick {a} x {b} x {c}: moments of inertia x {inertia[0]:.4f}, y {inertia[1]:.4f}, z {inertia[2]:.4f} "
          f"(long axis z smallest, middle axis y intermediate, thin axis x largest)")
    print(f"spin {man['turns_per_second']} turn/s = {spin:.4f} rad/s, wobble {eps} rad/s on the other two axes, "
          f"{fps * sub} steps per second")
    print(f"linearised growth rate about the middle axis: {lam:.4f} per second; "
          f"first flip predicted near ln(spin/wobble)/rate = {math.log(spin / eps) / lam:.2f} s")
    # Both bricks start with their spin axis along space Y (towards the camera).
    q_long = np.array([0.5, -0.5, -0.5, -0.5])  # body z -> space Y, body y -> space X, body x -> space Z
    q_mid = np.array([1.0, 0.0, 0.0, 0.0])                              # body y = space Y
    runs = {
        "long": simulate(inertia, 2, spin, eps, q_long, dur, fps, sub),
        "middle": simulate(inertia, 1, spin, eps, q_mid, dur, fps, sub),
    }
    for name, r in runs.items():
        print(f"{name} axis: {len(r['flips'])} flips in {dur:.0f} s; largest tilt of the spin axis from the angular "
              f"momentum {r['max_tilt']:.4f} deg; energy drift {r['dE']:.1e}, |L| drift {r['dL']:.1e}, "
              f"L direction drift {r['dLdir']:.1e}")
        if len(r["flips"]):
            gaps = np.diff(r["flips"])
            print(f"  flip times: " + ", ".join(f"{t:.3f}" for t in r["flips"]))
            if len(gaps):
                print(f"  flip period: mean {gaps.mean():.3f} s (min {gaps.min():.3f}, max {gaps.max():.3f})")
            print(f"  one flip, 10 to 170 degrees: mean {r['durations'].mean():.3f} s")
            print(f"  tilt at the first frame {r['tilt'][0]:.4f} deg, at 1 s {r['tilt'][fps]:.4f}, "
                  f"at 2 s {r['tilt'][2 * fps]:.3f}, at 2.5 s {r['tilt'][int(2.5 * fps)]:.2f}")
    # Checks.
    thin = simulate(inertia, 0, spin, eps, np.array([1.0, 0.0, 0.0, 0.0]), dur, fps, sub)
    print(f"check: thin axis (largest moment): {len(thin['flips'])} flips, largest tilt {thin['max_tilt']:.4f} deg")
    for e2 in man["check_wobbles"]:
        r2 = simulate(inertia, 1, spin, e2, q_mid, dur, fps, sub)
        gaps = np.diff(r2["flips"])
        print(f"check: middle axis with wobble {e2}: first flip {r2['flips'][0]:.3f} s, "
              f"{len(r2['flips'])} flips, period {gaps.mean():.3f} s")
    out = {"inertia": inertia, "runs": runs, "lam": lam}
    mid = runs["middle"]
    out["first_flip"] = float(mid["flips"][0])
    out["period"] = float(np.diff(mid["flips"]).mean())
    out["n_flips"] = int(len(mid["flips"]))
    out["max_tilt_long"] = runs["long"]["max_tilt"]
    return out


class Renderer:
    def __init__(self, man: dict, meas: dict):
        self.man, self.meas = man, meas
        self.fps = man["fps"]
        font = os.environ["SEED_ZERO_FONT"]
        self.font = ImageFont.truetype(font, 40)
        self.font_small = ImageFont.truetype(font, 32)
        self.font_big = ImageFont.truetype(font, 56)
        self.font_title = ImageFont.truetype(font, 60)
        a, b, c = man["sides"]
        h = np.array([a, b, c]) / 2.0
        self.verts = np.array([[sx * h[0], sy * h[1], sz * h[2]] for sx in (-1, 1) for sy in (-1, 1) for sz in (-1, 1)])
        # Faces as vertex index quads with outward normals (body frame).
        self.faces = [
            ((1, 3, 7, 5), np.array([0, 0, 1.0])), ((0, 4, 6, 2), np.array([0, 0, -1.0])),
            ((2, 6, 7, 3), np.array([0, 1.0, 0])), ((0, 1, 5, 4), np.array([0, -1.0, 0])),
            ((4, 5, 7, 6), np.array([1.0, 0, 0])), ((0, 2, 3, 1), np.array([-1.0, 0, 0])),
        ]
        tilt = math.radians(man["camera_tilt_deg"])
        # Camera: space Y is the view axis (into the screen), tipped by the tilt
        # about space X so the viewer looks slightly down onto the spin axis.
        self.cam = np.array([[1, 0, 0], [0, math.cos(tilt), -math.sin(tilt)], [0, math.sin(tilt), math.cos(tilt)]])
        self.light = np.array([-0.4, -0.5, 0.75])
        self.light /= np.linalg.norm(self.light)
        self.axis_index = {"long": 2, "middle": 1}
        self.side_len = {"long": c, "middle": b}

    def face_colour(self, name: str, normal_body: np.ndarray) -> tuple:
        ax = self.axis_index[name]
        # The spin axis points away from the camera at the start, so the face
        # on the minus side faces the viewer first: teal first, gold after a flip.
        if normal_body[ax] < -0.5:
            return TEAL
        if normal_body[ax] > 0.5:
            return GOLD
        return SIDE

    def draw_brick(self, d: ImageDraw.ImageDraw, name: str, q: np.ndarray, cx: float, cy: float) -> None:
        R = self.cam @ quat_to_matrix(q)
        pts = self.verts @ R.T
        screen = [(cx + p[0] * PX_PER_UNIT, cy - p[2] * PX_PER_UNIT) for p in pts]
        ax = self.axis_index[name]
        rod = np.zeros(3)
        rod[ax] = self.side_len[name] / 2 + 1.4
        rod_p, rod_m = R @ rod, R @ (-rod)
        ends = [(rod_p, 1), (rod_m, -1)]
        ends.sort(key=lambda e: e[0][1], reverse=True)  # far end (larger depth) first

        def draw_rod_end(vec, sign):
            base = vec * (self.side_len[name] / 2) / (self.side_len[name] / 2 + 1.4)
            p0 = (cx + base[0] * PX_PER_UNIT, cy - base[2] * PX_PER_UNIT)
            p1 = (cx + vec[0] * PX_PER_UNIT, cy - vec[2] * PX_PER_UNIT)
            d.line([p0, p1], fill=ROD, width=8)
            if sign > 0:
                d.ellipse((p1[0] - 12, p1[1] - 12, p1[0] + 12, p1[1] + 12), fill=ROD)

        draw_rod_end(*ends[0])
        for idx, normal in self.faces:
            n_cam = R @ normal
            if n_cam[1] > 0:  # facing away from the camera
                continue
            base = self.face_colour(name, normal)
            shade = 0.72 + 0.28 * max(0.0, float(n_cam @ self.light))
            col = tuple(int(v * shade) for v in base)
            d.polygon([screen[i] for i in idx], fill=col, outline=BG)
        draw_rod_end(*ends[1])

    def frame_at(self, f: int) -> np.ndarray:
        man, m = self.man, self.meas
        t = f / self.fps
        img = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(img)
        title_on = t < man["title_until"]
        for name, p in PANELS.items():
            run = m["runs"][name]
            label = "spun about its long axis" if name == "long" else "spun about its middle axis"
            if name == "long" and title_on:
                alpha = 1.0 if t < man["title_until"] - 0.4 else (man["title_until"] - t) / 0.4
                shade = tuple(int(c * alpha + BG[j] * (1 - alpha)) for j, c in enumerate(TEXT))
                d.text((W / 2, p["label_y"]), man["title"], font=self.font_title, fill=shade, anchor="mm")
            else:
                d.text((60, p["label_y"]), label, font=self.font, fill=TEAL, anchor="lm")
            self.draw_brick(d, name, run["quats"][f], W / 2, p["cy"])
            flips_done = int(np.searchsorted(run["flips"], t, side="right"))
            if not title_on:
                col = GOLD if flips_done else TEXT
                d.text((W - 60, p["label_y"]), f"flips: {flips_done}", font=self.font_big, fill=col, anchor="rm")
                d.text((60, p["label_y"] + 56), f"axis tilt {run['tilt'][f]:6.2f} deg", font=self.font_small,
                       fill=MUTED, anchor="lm")
            # Flip timeline: one tick per flip, the whole short as the span.
            sy = STRIP_Y[name]
            d.line((80, sy, W - 80, sy), fill=WIRE, width=2)
            for k in range(0, int(man["scene_duration"]) + 1, 10):
                x = 80 + (W - 160) * k / man["scene_duration"]
                d.line((x, sy - 8, x, sy + 8), fill=WIRE, width=2)
                d.text((x, sy + 14), f"{k} s", font=self.font_small, fill=MUTED, anchor="mt")
            x_now = 80 + (W - 160) * min(t, man["scene_duration"]) / man["scene_duration"]
            d.line((x_now, sy - 18, x_now, sy + 10), fill=TEXT, width=3)
            for tf in run["flips"]:
                if tf > t:
                    break
                x = 80 + (W - 160) * tf / man["scene_duration"]
                d.line((x, sy - 30, x, sy + 10), fill=GOLD, width=6)
        if t >= man["payoff_t"]:
            alpha = min(1.0, (t - man["payoff_t"]) / man["payoff_hold"])
            shade = tuple(int(c * alpha + BG[j] * (1 - alpha)) for j, c in enumerate(GOLD))
            text = man["payoff_text"].format(period=m["period"], n=m["n_flips"], first=m["first_flip"],
                                             tilt=m["max_tilt_long"])
            for j, line in enumerate(text.split("|")):
                d.text((W / 2, PAYOFF_Y + j * 58), line.strip(), font=self.font, fill=shade, anchor="mm")
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
    man = json.loads((ROOT / "projects/dzhanibekov/manifest.json").read_text())
    meas = measure(man)
    if "--measure-only" in sys.argv:
        return
    Renderer(man, meas).render(ROOT / "media/dzhanibekov/footage.mp4")


if __name__ == "__main__":
    main()
