#!/usr/bin/env python3
"""Three-body figure eight: does a tiny nudge kill the choreography?

Two copies of the Chenciner-Montgomery figure-eight orbit run side by side
in the same integrator. The second copy starts with one star displaced by
`nudge` along x; the stars begin exactly one unit from the centre, so the
nudge is that fraction of a starting radius. Every lap the code measures the
largest distance between a star and its counterpart in the other copy, then
fits a straight line through those gaps and prints the residual. The claim
is the growth law, so the fit is the measurement.

Integration is a 4th-order Yoshida composition of leapfrog steps, which is
symplectic and time-reversible; the trail before t = 0 is produced by
stepping the same scheme backwards.

usage: threebody.py [--measure-only]
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
EXACT = (222, 228, 236)
NUDGED = (240, 176, 84)
ACCENT = (92, 200, 165)
MUTED = (138, 148, 163)
GRID = (32, 38, 46)

# Chenciner-Montgomery figure eight: three equal masses, G = 1.
X0 = np.array([[0.97000436, -0.24308753],
               [0.0, 0.0],
               [-0.97000436, 0.24308753]])
_V2 = np.array([-0.93240737, -0.86473146])
V0 = np.array([-_V2 / 2, _V2, -_V2 / 2])
PERIOD = 6.32591398

# Yoshida 4th-order composition weights.
_C = 2.0 ** (1.0 / 3.0)
_W1 = 1.0 / (2.0 - _C)
_W0 = -_C / (2.0 - _C)
WEIGHTS = (_W1, _W0, _W1)

# Layout. The caption band burned in by compose.sh sits at y = 1344..1420.
ORBIT_CX, ORBIT_CY = W / 2, 540.0
ORBIT_HALF_X = 1.15          # world half-width mapped to PLOT_X0..PLOT_X1
PLOT_X0, PLOT_X1 = 60, 1020
CHART_X0, CHART_X1 = 150, 1000
CHART_Y0, CHART_Y1 = 860.0, 1270.0
CLOCK_Y = 205.0
READOUT_Y = 1520.0
PAYOFF_Y = 1868.0
TRAIL_LAPS = 0.28
FADE = 0.6


def accel(x: np.ndarray) -> np.ndarray:
    """Newtonian acceleration for a stack of 3-body systems, shape (S, 3, 2)."""
    d = x[:, :, None, :] - x[:, None, :, :]
    r2 = (d ** 2).sum(-1)
    idx = np.arange(3)
    r2[:, idx, idx] = 1.0
    inv = r2 ** -1.5
    inv[:, idx, idx] = 0.0
    return -(d * inv[..., None]).sum(2)


def leapfrog(x, v, h):
    v = v + 0.5 * h * accel(x)
    x = x + h * v
    v = v + 0.5 * h * accel(x)
    return x, v


def step(x, v, h):
    for w in WEIGHTS:
        x, v = leapfrog(x, v, w * h)
    return x, v


def energy(x: np.ndarray) -> np.ndarray:
    d = x[:, :, None, :] - x[:, None, :, :]
    r = np.sqrt((d ** 2).sum(-1))
    iu = np.triu_indices(3, 1)
    return -(1.0 / r[:, iu[0], iu[1]]).sum(-1)


def integrate(manifest: dict):
    """Return positions for both copies, sampled every step, plus the trail."""
    n = int(round(PERIOD / manifest["dt"]))
    h = PERIOD / n
    laps = manifest["laps"]

    x = np.stack([X0, X0])
    v = np.stack([V0, V0])
    x[1, 0, 0] += manifest["nudge"]

    # Trail before t = 0: the same scheme run backwards, then reversed.
    back = []
    xb, vb = x.copy(), v.copy()
    for _ in range(int(TRAIL_LAPS * n) + 1):
        xb, vb = step(xb, vb, -h)
        back.append(xb.copy())
    pre = np.array(back[::-1])

    fwd = [x.copy()]
    ke0 = 0.5 * (v ** 2).sum(-1).sum(-1)
    e0 = ke0 + energy(x)
    for k in range(laps * n):
        x, v = step(x, v, h)
        fwd.append(x.copy())
    ke = 0.5 * (v ** 2).sum(-1).sum(-1)
    drift = np.abs(ke + energy(x) - e0).max()
    return pre, np.array(fwd), n, drift


def measure_report(manifest: dict):
    pre, pos, n, drift = integrate(manifest)
    laps = manifest["laps"]
    nudge = manifest["nudge"]

    lap_index = np.arange(1, laps + 1) * n
    gaps = np.sqrt(((pos[lap_index, 0] - pos[lap_index, 1]) ** 2).sum(-1)).max(-1)
    lap = np.arange(1, laps + 1, dtype=float)
    slope = float(np.linalg.lstsq(lap[:, None], gaps, rcond=None)[0][0])
    resid = float(np.abs(gaps - slope * lap).max())

    # The untouched copy must still be a closed figure eight.
    ret = np.abs(pos[lap_index, 0] - X0).max(-1).max(-1)
    span = np.sqrt((((pos[:, 0][:, :, None, :] - pos[:, 0][:, None, :, :]) ** 2)
                    .sum(-1))).max()

    print(f"figure-eight period: {PERIOD} (star starts "
          f"{np.linalg.norm(X0[0]):.9f} from the centre)")
    print(f"nudge: {nudge} along x on one star, dt {manifest['dt']} "
          f"({n} steps per lap)")
    print(f"energy drift over {laps} laps: {drift:.3e}")
    print(f"exact copy: max return error {ret.max():.3e}, "
          f"max pair distance {span:.4f} (stays bounded)")
    for L in (1, 5, 10, 20, 30, 40):
        if L <= laps:
            print(f"  lap {L:2d}: gap {gaps[L-1]:.6f}  "
                  f"({gaps[L-1] / nudge:.1f}x the nudge)")
    print(f"straight-line fit: {slope:.6f} per lap, max residual {resid:.4f}")
    print(f"amplification after {laps} laps: {gaps[-1] / nudge:.1f}x "
          f"(a doubling law would give {2.0 ** laps:.3e}x)")
    return {"pre": pre, "pos": pos, "n": n, "gaps": gaps,
            "slope": slope, "resid": resid, "drift": drift,
            "amp": gaps[-1] / nudge}


class Renderer:
    def __init__(self, manifest, meas):
        self.man = manifest
        self.meas = meas
        self.fps = manifest["fps"]
        self.n = meas["n"]
        self.pre = meas["pre"]
        self.pos = meas["pos"]
        self.gaps = meas["gaps"]
        self.laps = manifest["laps"]
        self.trail = int(TRAIL_LAPS * self.n)
        font = os.environ["SEED_ZERO_FONT"]
        self.font = ImageFont.truetype(font, 42)
        self.font_small = ImageFont.truetype(font, 34)
        self.font_big = ImageFont.truetype(font, 58)
        self.scale = (PLOT_X1 - PLOT_X0) / (2 * ORBIT_HALF_X)
        # Static faint track: one lap of the untouched copy.
        # All three stars follow the same closed curve, so one body over one
        # period traces the whole figure eight.
        self.track = [self.to_px(p) for p in self.pos[:self.n + 1:6, 0, 0]]
        # Chart mapping.
        self.gmax = float(self.gaps[-1]) * 1.12
        self.dots = [self.chart_px(i + 1, g) for i, g in enumerate(self.gaps)]
        self.ref_end = self.chart_px(self.laps, self.gaps[0] * self.laps)
        self.ref_start = self.chart_px(0.0, 0.0)

    def to_px(self, p):
        return (ORBIT_CX + p[0] * self.scale, ORBIT_CY - p[1] * self.scale)

    def chart_px(self, lap, gap):
        x = CHART_X0 + (CHART_X1 - CHART_X0) * lap / self.laps
        y = CHART_Y1 - (CHART_Y1 - CHART_Y0) * min(gap, self.gmax) / self.gmax
        return (x, y)

    def lap_at(self, t: float) -> float:
        """Laps elapsed: a linear speed ramp, then a constant race rate.

        The rate rises from `intro_rate` to the race rate over `intro_slow`
        seconds so the shape reads before the orbit is played fast, with no
        jump in speed at the handover.
        """
        m = self.man
        t1, r0 = m["intro_slow"], m["intro_rate"]
        race = (self.laps - r0 * t1 / 2) / (m["race_end"] - t1 / 2)
        if t < t1:
            return r0 * t + (race - r0) * t * t / (2 * t1)
        if t < m["race_end"]:
            return t1 * (r0 + race) / 2 + race * (t - t1)
        return float(self.laps)

    def blend(self, color, alpha):
        return tuple(int(c * alpha + BG[i] * (1 - alpha)) for i, c in enumerate(color))

    def sample(self, idx: int, copy: int):
        """Position history sample, negative indices reaching into the trail."""
        if idx >= 0:
            return self.pos[idx, copy]
        return self.pre[len(self.pre) + idx, copy]

    def trail_points(self, copy: int, body: int, i: int, step_by: int):
        pts = []
        j = i - self.trail
        while j <= i:
            pts.append(self.to_px(self.sample(j, copy)[body]))
            j += step_by
        return pts

    def frame_at(self, t: float) -> np.ndarray:
        lap = self.lap_at(t)
        i = min(int(lap * self.n), len(self.pos) - 1)
        img = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(img)

        d.line(self.track, fill=GRID, width=2, joint="curve")

        for copy, color in ((0, EXACT), (1, NUDGED)):
            for body in range(3):
                pts = self.trail_points(copy, body, i, 12)
                cut = max(2, len(pts) // 4)
                for k, alpha in enumerate((0.18, 0.34, 0.58, 0.95)):
                    seg = pts[k * cut:(k + 1) * cut + 1]
                    if len(seg) > 1:
                        d.line(seg, fill=self.blend(color, alpha), width=5,
                               joint="curve")
                px, py = self.to_px(self.sample(i, copy)[body])
                r = 11 if copy == 0 else 8
                d.ellipse([px - r, py - r, px + r, py + r], fill=color)

        d.text((W / 2, CLOCK_Y), f"lap {lap:.2f}", font=self.font_big,
               fill=ACCENT, anchor="mm")

        # Chart: straight reference line, then one dot per completed lap.
        d.line([(CHART_X0, CHART_Y1), (CHART_X1, CHART_Y1)], fill=GRID, width=3)
        d.line([(CHART_X0, CHART_Y0), (CHART_X0, CHART_Y1)], fill=GRID, width=3)
        d.line([self.ref_start, self.ref_end], fill=self.blend(ACCENT, 0.75),
               width=3)
        d.text((CHART_X0 - 16, CHART_Y0), "gap", font=self.font_small,
               fill=MUTED, anchor="rm")
        d.text((CHART_X1, CHART_Y1 + 34), f"lap {self.laps}",
               font=self.font_small, fill=MUTED, anchor="rm")
        d.text((CHART_X0, CHART_Y1 + 34), "lap 1", font=self.font_small,
               fill=MUTED, anchor="lm")
        d.text((self.ref_end[0], self.ref_end[1] - 28), "straight line",
               font=self.font_small, fill=ACCENT, anchor="rs")
        done = int(lap)
        for k in range(min(done, self.laps)):
            x, y = self.dots[k]
            d.ellipse([x - 7, y - 7, x + 7, y + 7], fill=NUDGED)

        shown = self.gaps[done - 1] if done >= 1 else 0.0
        d.text((W / 2, READOUT_Y),
               f"gap after {min(done, self.laps)} laps: {shown:.3f}"
               f"   ({shown / self.man['nudge']:.0f}x the nudge)",
               font=self.font, fill=EXACT if done else MUTED, anchor="mm")

        alpha = min(1.0, max(0.0, (t - self.man["payoff_fade"]) / FADE))
        if alpha > 0:
            d.text((W / 2, PAYOFF_Y),
                   f"{self.laps} laps: {self.meas['amp']:.0f}x, not a trillion",
                   font=self.font, fill=self.blend(EXACT, alpha), anchor="mm")
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
            proc.stdin.write(self.frame_at(f / self.fps).tobytes())
            if f % 300 == 0:
                print(f"frame {f}/{total}", file=sys.stderr)
        proc.stdin.close()
        if proc.wait() != 0:
            raise RuntimeError("ffmpeg failed")
        print(f"footage: {out_path} ({total / self.fps:.2f}s at {self.fps} fps)")


def main() -> None:
    manifest = json.loads((ROOT / "projects/threebody/manifest.json").read_text())
    meas = measure_report(manifest)
    if "--measure-only" in sys.argv:
        return
    Renderer(manifest, meas).render(ROOT / "media/threebody/footage.mp4")


if __name__ == "__main__":
    main()
