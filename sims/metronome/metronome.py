#!/usr/bin/env python3
"""Metronome sync: why do two metronomes end up ticking together?

Two identical metronomes, modelled as escapement-driven pendulums (a van der
Pol term keeps each swinging at its set amplitude), stand on a light board.
In the top panel the board rests on two cans and rolls freely (with a small
viscous drag); in the bottom panel the board is fixed to the table. Both
pairs start the same way: metronome one at the end of its swing, metronome
two a quarter of a beat behind it. The equations come from the Lagrangian
of a base of mass M sliding in one dimension with two pendulums of mass m
and length l hung from it; at every RK4 stage the 3 by 3 linear system for
the board and pendulum accelerations is solved. On the fixed table the
board acceleration is zero and the metronomes never feel each other. No
seed: the run is deterministic.

Measured and printed: the metronome and board parameters, the starting
gap between the ticks, the gap over time on both panels, the time the
board pair locks in step (the gap under a small fraction of a beat and
staying there), the gap of the table pair at the end, the board's largest
excursion, and checks with half the step, other board masses and other
starting gaps.

usage: metronome.py [--measure-only] [--frames t1,t2,...]
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
BODY = (44, 52, 62)
CAN = (90, 100, 116)

PANELS = {
    "board": {"label_y": 236, "read_y": 300, "board_y": 690.0, "label": "on a board that rolls on two cans", "rolls": True},
    "table": {"label_y": 900, "read_y": 960, "board_y": 1400.0, "label": "on the table", "rolls": False},
}
CLOCK_Y = 815
METRO_X = (320.0, 760.0)
PX_PER_M = 1100.0
BODY_H = 230
BODY_W = 170
PIVOT_UP = 64
BOARD_HALF = 360
CAN_R = 30
PAYOFF_Y = 1592.0


def limit_cycle(g: float, ell: float, theta0: float, eps: float, dt: float, gap_s: float) -> tuple[np.ndarray, np.ndarray]:
    """Run one metronome on a fixed base until it is on its limit cycle; return
    its state at a swing end and its state gap_s earlier (angle, rate)."""
    w0 = math.sqrt(g / ell)
    th, om = theta0, 0.0
    hist = []
    n = int(round(40.0 / dt))

    def f(th_, om_):
        return om_, -(g / ell) * math.sin(th_) - eps * w0 * ((th_ / theta0) ** 2 - 1.0) * om_

    for i in range(n + 1):
        hist.append((th, om))
        k1 = f(th, om)
        k2 = f(th + 0.5 * dt * k1[0], om + 0.5 * dt * k1[1])
        k3 = f(th + 0.5 * dt * k2[0], om + 0.5 * dt * k2[1])
        k4 = f(th + dt * k3[0], om + dt * k3[1])
        th += dt / 6.0 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0])
        om += dt / 6.0 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1])
    hist = np.array(hist)
    # Last swing end (rate crossing from positive to negative) after 30 s.
    idx = [i for i in range(int(30.0 / dt), n) if hist[i, 1] > 0.0 >= hist[i + 1, 1]]
    i_end = idx[-1]
    i_lag = i_end - int(round(gap_s / dt))
    return hist[i_end], hist[i_lag]


def simulate(g: float, ell: float, m: float, M: float, b: float, theta0: float, eps: float,
             start_gap: float, rolls: bool, dt: float, duration: float, record_every: int) -> dict:
    """Base of mass M with two escapement pendulums; start_gap is a lag in beats."""
    w0 = math.sqrt(g / ell)
    Mt = M + 2 * m

    def accel(s: np.ndarray) -> np.ndarray:
        X, th1, th2, V, om1, om2 = s
        th = np.array([th1, th2])
        om = np.array([om1, om2])
        drive = -eps * w0 * ((th / theta0) ** 2 - 1.0) * om          # escapement, per unit m l^2
        rhs_p = -g * ell * np.sin(th) + ell * ell * drive             # pendulum rows / m
        if rolls:
            A = np.array([
                [Mt, m * ell * math.cos(th1), m * ell * math.cos(th2)],
                [ell * math.cos(th1), ell * ell, 0.0],
                [ell * math.cos(th2), 0.0, ell * ell],
            ])
            rhs = np.array([-b * V + m * ell * float(np.sum(om * om * np.sin(th))), rhs_p[0], rhs_p[1]])
            acc = np.linalg.solve(A, rhs)
        else:
            acc = np.array([0.0, rhs_p[0] / (ell * ell), rhs_p[1] / (ell * ell)])
        return np.array([V, om1, om2, acc[0], acc[1], acc[2]])

    # Metronome one at the end of its swing on its limit cycle, metronome two
    # start_gap beats behind it on the same cycle; the board starts so that
    # the whole system has no net momentum (it would otherwise drift off).
    beat0 = math.pi / w0
    (th1, om1), (th2, om2) = limit_cycle(g, ell, theta0, eps, dt, start_gap * beat0)
    V0 = -m * ell * (om1 * math.cos(th1) + om2 * math.cos(th2)) / Mt if rolls else 0.0
    s = np.array([0.0, th1, th2, V0, om1, om2])
    n = int(round(duration / dt))
    rec_t, rec = [], []
    ticks = ([], [])          # times each metronome passes the centre swinging toward negative angles
    for i in range(n + 1):
        t = i * dt
        if i % record_every == 0:
            rec_t.append(t)
            rec.append(s.copy())
        k1 = accel(s)
        k2 = accel(s + 0.5 * dt * k1)
        k3 = accel(s + 0.5 * dt * k2)
        k4 = accel(s + dt * k3)
        s_new = s + dt / 6.0 * (k1 + 2 * k2 + 2 * k3 + k4)
        for k in (0, 1):
            a0, a1 = s[1 + k], s_new[1 + k]
            if a0 > 0.0 >= a1:
                ticks[k].append(t + dt * a0 / (a0 - a1))
        s = s_new
    rec = np.array(rec)
    t = np.array(rec_t)
    # Gap between the ticks: for every tick of metronome one, the nearest
    # same-direction tick of metronome two, in beats (a full swing is two
    # beats, so the gap lies in (-1, 1]; 0 is in step, 1 is opposite).
    period = 2 * math.pi / w0
    beat = period / 2
    t2 = np.array(ticks[1])
    gap_t, gap_b = [], []
    for t1 in ticks[0]:
        if len(t2) == 0:
            break
        j = int(np.argmin(np.abs(t2 - t1)))
        d = t2[j] - t1
        d = (d + period / 2) % period - period / 2
        gap_t.append(t1)
        gap_b.append(d / beat)
    gap_t, gap_b = np.array(gap_t), np.array(gap_b)
    return {"t": t, "rec": rec, "ticks": ticks, "gap_t": gap_t, "gap_beats": gap_b, "w0": w0,
            "board_max": float(np.max(np.abs(rec[:, 0]))) if rolls else 0.0}


def lock_time(run: dict, tol: float) -> float | None:
    """The first tick from which the gap stays within tol beats of zero."""
    t, gap = run["gap_t"], run["gap_beats"]
    inside = np.abs(gap) < tol
    if not inside[-1]:
        return None
    k = len(inside) - 1
    while k > 0 and inside[k - 1]:
        k -= 1
    return float(t[k])


def gap_at(run: dict, s: float) -> float:
    """Gap of the latest tick pair at time s (the starting gap before the first tick)."""
    k = int(np.searchsorted(run["gap_t"], s, side="right")) - 1
    return float(run["gap_beats"][k]) if k >= 0 else float(run["gap_beats"][0])


def fmt_gap(beats: float, beat: float, tol: float) -> str:
    return f"ticks {abs(beats) * beat * 1000:.0f} ms apart" if abs(beats) >= tol else "ticks in step"


def measure(man: dict) -> dict:
    g, bpm, m, M, b = man["g"], man["beats_per_minute"], man["bob_mass_kg"], man["board_mass_kg"], man["board_damping_kg_per_s"]
    theta0 = math.radians(man["swing_deg"])
    eps = man["escapement"]
    f = bpm / 120.0                     # full swings per second (two beats per swing)
    ell = g / (2 * math.pi * f) ** 2
    beat = 0.5 / f
    gap0 = man["start_gap_beats"]
    tol = man["lock_beats"]
    print(f"metronomes: {bpm} beats per minute (one full swing every {1 / f:.2f} s, a beat every {beat:.2f} s), "
          f"pendulum length {ell * 100:.1f} cm, bob {m * 1000:.0f} g, swing {man['swing_deg']:g} degrees held by an "
          f"escapement of strength {eps:g}; board {M * 1000:.0f} g on two cans with drag {b:g} kg/s, or fixed to the table; "
          f"metronome two starts {man['start_gap_beats']:g} beat ({man['start_gap_beats'] * beat * 1000:.0f} ms) behind "
          f"metronome one; RK4 at {1 / man['dt']:.0f} steps per second, deterministic, no seed")
    runs = {}
    for name, rolls in (("board", True), ("table", False)):
        runs[name] = simulate(g, ell, m, M, b, theta0, eps, gap0, rolls, man["dt"], man["sim_duration"], man["record_every"])
    for name, run in runs.items():
        samples = ", ".join(f"{gap_at(run, tt):.3f} at {tt:.0f} s" for tt in (0, 5, 10, 15, 20, 25, 30, 40, 60))
        print(f"{name}: gap between the ticks in beats (metronome two behind one): {samples}")
    lock = lock_time(runs["board"], tol)
    if lock is None:
        raise SystemExit("the board pair never locked")
    t_end = runs["board"]["t"][-1]
    print(f"board pair: in step (gap under {tol:g} beat = {tol * beat * 1000:.0f} ms, and staying there) from the tick at "
          f"{lock:.2f} s; gap at the end {abs(runs['board']['gap_beats'][-1]):.4f} beat = "
          f"{abs(runs['board']['gap_beats'][-1]) * beat * 1000:.1f} ms; the board moves at most "
          f"{runs['board']['board_max'] * 1000:.1f} mm from its start; ticks of metronome one near the lock: "
          + ", ".join(f"{x:.3f}" for x in runs["board"]["ticks"][0] if lock - 2.1 < x < lock + 1.1) + " s; metronome two: "
          + ", ".join(f"{x:.3f}" for x in runs["board"]["ticks"][1] if lock - 2.1 < x < lock + 1.1) + " s")
    tg = runs["table"]["gap_beats"]
    print(f"table pair: gap {abs(tg[0]):.4f} beat at the start, {abs(tg[-1]):.4f} beat at the last tick "
          f"({runs['table']['gap_t'][-1]:.1f} s); largest change over the run {np.max(np.abs(np.abs(tg) - abs(tg[0]))):.5f} beat: "
          f"never in step")
    fine = simulate(g, ell, m, M, b, theta0, eps, gap0, True, man["check_dt"], man["sim_duration"], man["record_every"] * 2)
    print(f"check, half the step: board pair in step from {lock_time(fine, tol):.2f} s")
    for Mc in man["check_board_masses_kg"]:
        r = simulate(g, ell, m, Mc, b, theta0, eps, gap0, True, man["dt"], man["sim_duration"], man["record_every"])
        lk = lock_time(r, tol)
        print(f"check, board {Mc * 1000:.0f} g: " + (f"in step from {lk:.2f} s" if lk else f"not in step by {t_end:.0f} s "
              f"(gap {abs(r['gap_beats'][-1]):.3f} beat)"))
    for gs in man["check_start_gaps_beats"]:
        r = simulate(g, ell, m, M, b, theta0, eps, gs, True, man["dt"], man["sim_duration"], man["record_every"])
        lk = lock_time(r, tol)
        print(f"check, start {gs:g} beat apart: " + (f"in step from {lk:.2f} s" if lk else f"not in step by {t_end:.0f} s "
              f"(gap {abs(r['gap_beats'][-1]):.3f} beat)"))
    return {"runs": runs, "lock": lock, "beat": beat, "ell": ell, "theta0": theta0,
            "table_gap": abs(float(tg[-1]))}


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
        widths = {"overlay@34": (ImageFont.truetype(font, 34), man["overlay"])}
        for j, line in enumerate(man["title"].split("|")):
            widths[f"title line {j + 1}@56"] = (self.font_title, line)
        for k, p in PANELS.items():
            widths[f"label {k}@40"] = (self.font, p["label"])
        widths["readout@44"] = (self.font_read, "ticks 125 ms apart")
        widths["watch@64"] = (self.font_watch, "39.9 s")
        for j, line in enumerate(self.payoff_lines()):
            widths[f"payoff line {j + 1}@40"] = (self.font, line)
        print("text widths: " + ", ".join(f"{k} {f.getlength(s):.0f} px" for k, (f, s) in widths.items()))
        print(f"playback {man['playback']:g}x from the release at {man['release_t']:g} s of video; the board pair is in "
              f"step from {man['release_t'] + meas['lock'] / man['playback']:.2f} s of video")

    def payoff_lines(self) -> list[str]:
        gap = f"{self.meas['table_gap'] * self.meas['beat'] * 1000:.0f} ms"
        text = self.man["payoff_text"].format(lock=self.meas["lock"], gap=gap)
        return [s.strip() for s in text.split("|")]

    def state(self, name: str, s: float):
        run = self.meas["runs"][name]
        t = run["t"]
        i = min(int(round(s / (t[1] - t[0]))), len(t) - 1)
        return run["rec"][i], gap_at(run, s)

    def metronome(self, d: ImageDraw.ImageDraw, x: float, base_y: float, th: float, col) -> None:
        # Body: a trapezoid standing on the board; pivot low in the body; rod up.
        top = base_y - BODY_H
        d.polygon([(x - BODY_W / 2, base_y), (x + BODY_W / 2, base_y), (x + BODY_W * 0.32, top), (x - BODY_W * 0.32, top)],
                  fill=BODY, outline=WIRE)
        px, py = x, base_y - PIVOT_UP
        rod = self.meas["ell"] * PX_PER_M
        tx, ty = px + rod * math.sin(th), py - rod * math.cos(th)
        d.line([(px, py), (tx, ty)], fill=(190, 196, 206), width=6)
        d.ellipse((px - 8, py - 8, px + 8, py + 8), fill=BEAM)
        bx, by = px + 0.78 * rod * math.sin(th), py - 0.78 * rod * math.cos(th)
        d.rounded_rectangle((bx - 27, by - 19, bx + 27, by + 19), radius=7, fill=col)

    def draw_scene(self, s: float, readouts: bool, title_on: bool) -> Image.Image:
        img = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(img)
        for name, p in PANELS.items():
            rec, gap = self.state(name, s)
            X = rec[0] * PX_PER_M if p["rolls"] else 0.0
            by = p["board_y"]
            if p["rolls"]:
                for cx in (540 - 200, 540 + 200):
                    d.ellipse((cx - CAN_R, by + 4, cx + CAN_R, by + 4 + 2 * CAN_R), fill=CAN)
                    # A spoke shows the can turning with the board.
                    ang = -X / CAN_R
                    d.line([(cx, by + 4 + CAN_R), (cx + CAN_R * 0.8 * math.sin(ang), by + 4 + CAN_R - CAN_R * 0.8 * math.cos(ang))],
                           fill=BG, width=4)
                d.line([(100, by + 4 + 2 * CAN_R + 6), (980, by + 4 + 2 * CAN_R + 6)], fill=WIRE, width=4)
            else:
                d.line([(100, by + 6), (980, by + 6)], fill=WIRE, width=4)
            d.rectangle((540 + X - BOARD_HALF, by - 12, 540 + X + BOARD_HALF, by), fill=BEAM)
            for k, mx in enumerate(METRO_X):
                self.metronome(d, mx + X, by - 12, float(rec[1 + k]), (GOLD, TEAL)[k])
            if not title_on:
                d.text((540, p["label_y"]), p["label"], font=self.font, fill=GOLD if p["rolls"] else TEAL, anchor="mm")
                if readouts:
                    d.text((540, p["read_y"]), fmt_gap(gap, self.meas["beat"], self.man["lock_beats"]),
                           font=self.font_read, fill=TEXT, anchor="mm")
        if not title_on and readouts:
            d.text((540, CLOCK_Y), f"{s:.1f} s", font=self.font_watch, fill=TEXT, anchor="mm")
        return img

    def live_frame(self, f: int) -> np.ndarray:
        man = self.man
        t = f / self.fps
        title_on = t < man["title_until"]
        s = max(0.0, (t - man["release_t"]) * man["playback"])
        s = min(s, (man["hold_until"] - man["release_t"]) * man["playback"])
        readouts = t >= man["release_t"]
        img = self.draw_scene(s, readouts, title_on)
        d = ImageDraw.Draw(img)

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
    man = json.loads((ROOT / "projects/metronome/manifest.json").read_text())
    meas = measure(man)
    if "--measure-only" in sys.argv:
        return
    if "--frames" in sys.argv:
        times = [float(v) for v in sys.argv[sys.argv.index("--frames") + 1].split(",")]
        r = Renderer(man, meas)
        for tv in times:
            Image.fromarray(r.frame_at(int(round(tv * man["fps"])))).save(ROOT / f"media/metronome/smoke-{tv}.png")
        print("smoke frames: " + ", ".join(f"{tv}" for tv in times))
        return
    Renderer(man, meas).render(ROOT / "media/metronome/footage.mp4")


if __name__ == "__main__":
    main()
