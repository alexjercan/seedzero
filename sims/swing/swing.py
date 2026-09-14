#!/usr/bin/env python3
"""Swing pumping: nobody is pushing, how does a swing go higher?

Two identical swings are released from the same small angle with nobody
pushing. The rider is a point mass whose distance from the pivot the rider
can change by a fixed fraction of the rope: standing raises the centre of
mass, squatting lowers it. On the top swing the rider stands at the bottom
of the arc and squats at the ends (the playground rhythm); on the bottom
swing the rider does the opposite. The rider's target length switches when
the swing passes the bottom and when it reaches an end (short after the
bottom, long after an end, or the reverse) and the rider's centre of mass
moves to it with a short time constant, and the rope angle
obeys the variable-length pendulum equation
theta'' = -(g / L) sin(theta) - 2 (L' / L) theta', integrated with RK4 at a
fixed step. No seed: the run is deterministic.

Measured and printed: the rope and the two lengths, the peak angle after
every swing on both swings, the swing on which the pumped swing first
passes the target angle, the other swing's peak on that swing, a swing at
rest, a half-step check, a half-lag check, a smaller length change, the
impulsive closed form, and the on-screen text widths.

usage: swing.py [--measure-only] [--frames t1,t2,...]
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
BEAM = (120, 130, 145)

# Layout: two swings stacked, each with a label row and a readout row above
# its pivot; captions at caption_y 0.75 (y 1440..1510); payoff under them.
PANELS = {
    "pump": {"label_y": 236, "read_y": 318, "pivot_y": 430.0, "colour": GOLD,
             "label": "stand at the bottom, squat at the top"},
    "anti": {"label_y": 890, "read_y": 946, "pivot_y": 1000.0, "colour": TEAL,
             "label": "the other way round"},
}
PIVOT_X = 540.0
PX_PER_M = 150.0
BOB_R = 26
PAYOFF_Y = 1592.0


def simulate(g: float, L_long: float, frac: float, lag: float, theta0: float, pump: bool,
             dt: float, duration: float, record_every: int, stop: float) -> dict:
    """Variable-length pendulum with an event-driven rider. Angles in radians.

    The rider's centre of mass moves toward a target length with a short
    time constant. The pumped rider makes the target short when the swing
    passes the bottom (stands up) and long when it reaches an end (squats).
    The other rider does the opposite.
    """
    L_short = L_long * (1.0 - frac)

    def deriv(y: np.ndarray, tgt: float) -> np.ndarray:
        th, om, L = y
        Lp = (tgt - L) / lag
        return np.array([om, -(g / L) * math.sin(th) - 2.0 * (Lp / L) * om, Lp])

    tgt = L_long if pump else L_short   # released at an end
    y = np.array([theta0, 0.0, tgt])
    n = int(round(duration / dt))
    rec_t, rec = [], []
    peaks = []          # (time, signed angle) at every turning point
    swings = []         # peak angle after each full swing (turning point on the start side)
    swing_times = []
    end_t = duration
    for i in range(n + 1):
        t = i * dt
        if i % record_every == 0:
            rec_t.append(t)
            rec.append(y.copy())
        k1 = deriv(y, tgt)
        k2 = deriv(y + 0.5 * dt * k1, tgt)
        k3 = deriv(y + 0.5 * dt * k2, tgt)
        k4 = deriv(y + dt * k3, tgt)
        y_new = y + dt / 6.0 * (k1 + 2 * k2 + 2 * k3 + k4)
        if i > 0 and (y[1] > 0.0) != (y_new[1] > 0.0):
            # An end of the swing: the pumped rider squats, the other stands.
            f = y[1] / (y[1] - y_new[1])
            peaks.append((t + f * dt, float(y[0] + f * (y_new[0] - y[0]))))
            if len(peaks) % 2 == 0:
                swings.append(abs(peaks[-1][1]))
                swing_times.append(peaks[-1][0])
            tgt = L_long if pump else L_short
        if (y[0] > 0.0) != (y_new[0] > 0.0):
            # The bottom of the swing: the pumped rider stands, the other squats.
            tgt = L_short if pump else L_long
        y = y_new
        if abs(y[0]) > stop:
            end_t = t + dt
            break
    return {"t": np.array(rec_t), "y": np.array(rec), "peaks": peaks, "swings": swings,
            "swing_times": swing_times, "L_long": L_long, "L_short": L_short, "dt": dt,
            "end_t": end_t}


def measure(man: dict) -> dict:
    g, L, frac, lag = man["g"], man["rope_m"], man["length_change"], man["rider_lag_s"]
    th0 = math.radians(man["start_deg"])
    target = math.radians(man["target_deg"])
    stop = math.radians(man["stop_deg"])
    T0 = 2 * math.pi * math.sqrt(L / g)
    print(f"swing: rope {L:g} m, the rider's centre of mass {L * (1 - frac):.3g} m from the pivot standing and "
          f"{L:g} m squatting ({frac * 100:.0f}% length change), reaction lag {lag * 1000:.0f} ms; both released from "
          f"rest at {man['start_deg']:g} degrees with nobody pushing; small-swing period 2 pi sqrt(L / g) = {T0:.2f} s; "
          f"RK4 at {1 / man['dt']:.0f} steps per second, deterministic, no seed")
    runs = {}
    for name, pump in (("pump", True), ("anti", False)):
        runs[name] = simulate(g, L, frac, lag, th0, pump, man["dt"], man["sim_duration"], man["record_every"], stop)
    pump, anti = runs["pump"], runs["anti"]
    n_target = next((k + 1 for k, a in enumerate(pump["swings"]) if a >= target), None)
    if n_target is None:
        raise SystemExit("the pumped swing never reached the target angle")
    t_target = pump["swing_times"][n_target - 1]
    print("peak angle after each swing, stand at the bottom and squat at the top: " +
          ", ".join(f"{math.degrees(a):.1f}" for a in pump["swings"][:n_target + 2]) + " deg")
    print("peak angle after each swing, the other way round: " +
          ", ".join(f"{math.degrees(a):.2f}" for a in anti["swings"][:n_target + 2]) + " deg")
    print(f"the pumped swing first passes {man['target_deg']:g} degrees on swing {n_target} "
          f"({math.degrees(pump['swings'][n_target - 1]):.3f} deg at {t_target:.2f} s); on that swing the other rhythm "
          f"peaks at {math.degrees(anti['swings'][n_target - 1]):.2f} degrees (at {anti['swing_times'][n_target - 1]:.2f} s); "
          f"the pumped swing passes {man['stop_deg']:g} degrees at {pump['end_t']:.2f} s on swing "
          f"{len(pump['swings']) + 1}; halfway to the target ({man['target_deg'] / 2:g} deg) on swing "
          f"{next(k + 1 for k, a in enumerate(pump['swings']) if a >= target / 2)}")
    ratios = [pump["swings"][k + 1] / pump["swings"][k] for k in range(min(4, n_target - 1))]
    print(f"growth per swing (pumped, first swings): " + ", ".join(f"{r:.3f}x" for r in ratios) +
          f"; impulsive closed form (L / L')^3 = {(1 / (1 - frac)) ** 3:.3f}x in energy per half swing, "
          f"{(1 / (1 - frac)) ** 1.5:.3f}x in angle per half swing at small angles; the other rhythm shrinks by "
          + ", ".join(f"{anti['swings'][k + 1] / anti['swings'][k]:.3f}x" for k in range(min(3, len(anti["swings"]) - 1))))
    rest = simulate(g, L, frac, lag, 0.0, True, man["dt"], 20.0, man["record_every"], stop)
    print(f"check, a swing at rest with the same rider: largest angle in 20 s {math.degrees(np.max(np.abs(rest['y'][:, 0]))):.6f} deg "
          f"(nothing to pump)")
    fine = simulate(g, L, frac, lag, th0, True, man["check_dt"], t_target + 1.0, man["record_every"] * 2, stop)
    print(f"check, half the step: passes the target on swing "
          f"{next((k + 1 for k, a in enumerate(fine['swings']) if a >= target), None)} at "
          f"{next((tt for a, tt in zip(fine['swings'], fine['swing_times']) if a >= target), float('nan')):.2f} s; "
          f"peaks after swings 1 to 3: " + ", ".join(f"{math.degrees(a):.2f}" for a in fine["swings"][:3]) + " deg")
    quick = simulate(g, L, frac, man["check_lag_s"], th0, True, man["dt"], man["sim_duration"], man["record_every"], stop)
    print(f"check, half the reaction lag ({man['check_lag_s'] * 1000:.0f} ms): passes the target on swing "
          f"{next((k + 1 for k, a in enumerate(quick['swings']) if a >= target), None)}; peaks after swings 1 to 3: "
          + ", ".join(f"{math.degrees(a):.2f}" for a in quick["swings"][:3]) + " deg")
    small = simulate(g, L, man["check_length_change"], lag, th0, True, man["dt"], man["sim_duration"], man["record_every"], stop)
    ns = next((k + 1 for k, a in enumerate(small["swings"]) if a >= target), None)
    print(f"check, a {man['check_length_change'] * 100:.0f}% length change: passes the target on swing {ns}"
          + (f" at {small['swing_times'][ns - 1]:.2f} s" if ns else " (never in the run)")
          + "; peaks after swings 1 to 3: " + ", ".join(f"{math.degrees(a):.2f}" for a in small["swings"][:3]) + " deg")
    return {"runs": runs, "n_target": n_target, "t_target": t_target,
            "anti_at_target": math.degrees(anti["swings"][n_target - 1]),
            "pump_at_target": math.degrees(pump["swings"][n_target - 1])}


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
        self.first = None
        self.rest = None
        widths = {"overlay@34": (ImageFont.truetype(font, 34), man["overlay"])}
        for j, line in enumerate(man["title"].split("|")):
            widths[f"title line {j + 1}@56"] = (self.font_title, line)
        for k, p in PANELS.items():
            widths[f"label {k}@40"] = (self.font, p["label"])
        widths["readout@44"] = (self.font_read, "swing 10   peak 62.3 deg")
        for j, line in enumerate(self.payoff_lines()):
            widths[f"payoff line {j + 1}@40"] = (self.font, line)
        print("text widths: " + ", ".join(f"{k} {f.getlength(s):.0f} px" for k, (f, s) in widths.items()))
        print(f"playback {man['playback']:g}x from the release at {man['release_t']:g} s of video; the pumped swing "
              f"passes the target at {man['release_t'] + meas['t_target'] / man['playback']:.2f} s of video, frozen "
              f"until {man['hold_until']:g} s")

    def payoff_lines(self) -> list[str]:
        text = self.man["payoff_text"].format(swings=self.meas["n_target"], target=self.man["target_deg"])
        return [s.strip() for s in text.split("|")]

    def state(self, name: str, s: float):
        run = self.meas["runs"][name]
        t, y = run["t"], run["y"]
        i = min(int(round(s / (t[1] - t[0]))), len(t) - 1)
        th, om, L = y[i]
        # Peak readouts: the last completed swing at time s.
        n_done = sum(1 for tt in run["swing_times"] if tt <= s)
        peak = run["swings"][n_done - 1] if n_done > 0 else abs(y[0][0])
        return float(th), float(L), n_done, float(peak)

    def draw_scene(self, s: float, readouts: bool, title_on: bool) -> Image.Image:
        man = self.man
        img = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(img)
        for name, p in PANELS.items():
            th, L, n_done, peak = self.state(name, s)
            col = p["colour"]
            py = p["pivot_y"]
            L_long = self.meas["runs"][name]["L_long"]
            # Beam and pivot.
            d.line([(PIVOT_X - 140, py - 26), (PIVOT_X + 140, py - 26)], fill=BEAM, width=10)
            d.ellipse((PIVOT_X - 9, py - 9, PIVOT_X + 9, py + 9), fill=BEAM)
            # Faint arc of the current peak angle.
            rr = L_long * PX_PER_M + 40
            if peak > 0.02:
                deg = math.degrees(peak)
                d.arc((PIVOT_X - rr, py - rr, PIVOT_X + rr, py + rr), start=90 - deg, end=90 + deg, fill=WIRE, width=3)
            # Rope to the seat, seat at the long length, rider at L.
            sx, sy = PIVOT_X + L_long * PX_PER_M * math.sin(th), py + L_long * PX_PER_M * math.cos(th)
            d.line([(PIVOT_X, py), (sx, sy)], fill=(160, 168, 180), width=4)
            ux, uy = -math.cos(th), math.sin(th)  # perpendicular to the rope
            d.line([(sx - 30 * ux, sy - 30 * uy), (sx + 30 * ux, sy + 30 * uy)], fill=BEAM, width=8)
            bx, by = PIVOT_X + L * PX_PER_M * math.sin(th), py + L * PX_PER_M * math.cos(th)
            d.ellipse((bx - BOB_R, by - BOB_R, bx + BOB_R, by + BOB_R), fill=col)
            d.ellipse((bx - 7, by - 7, bx + 7, by + 7), fill=BG)
            if not title_on:
                d.text((PIVOT_X, p["label_y"]), p["label"], font=self.font, fill=col, anchor="mm")
                if readouts:
                    d.text((110, p["read_y"]), f"swing {n_done}", font=self.font_read, fill=TEXT, anchor="lm")
                    d.text((970, p["read_y"]), f"peak {math.degrees(peak):.1f} deg", font=self.font_read, fill=TEXT, anchor="rm")
        return img

    def live_frame(self, f: int) -> np.ndarray:
        man = self.man
        t = f / self.fps
        title_on = t < man["title_until"]
        s = max(0.0, (t - man["release_t"]) * man["playback"])
        s = min(s, self.meas["t_target"])
        readouts = t >= man["release_t"]
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
    man = json.loads((ROOT / "projects/swing/manifest.json").read_text())
    meas = measure(man)
    if "--measure-only" in sys.argv:
        return
    if "--frames" in sys.argv:
        times = [float(v) for v in sys.argv[sys.argv.index("--frames") + 1].split(",")]
        r = Renderer(man, meas)
        for tv in times:
            Image.fromarray(r.frame_at(int(round(tv * man["fps"])))).save(ROOT / f"media/swing/smoke-{tv}.png")
        print("smoke frames: " + ", ".join(f"{tv}" for tv in times))
        return
    Renderer(man, meas).render(ROOT / "media/swing/footage.mp4")


if __name__ == "__main__":
    main()
