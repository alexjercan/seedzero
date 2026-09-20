#!/usr/bin/env python3
"""Pi collisions: push a heavy block into a light one. How many clicks?

A light block (1 kg) rests on a frictionless floor between a wall on the
left and a heavy block pushed toward it at 1 m/s. Every collision is
elastic. Count every click, block on block and block on wall, until the
pair drift apart for good. Two panels on the same push and the same
start: the heavy block 100 times heavier on top, 10,000 times heavier
below. The count is the largest N with N atan(sqrt(m / M)) below pi:
31 and 314, the digits of pi.

Event driven: the sim jumps from click to click by solving each next
contact time exactly (the motion between clicks is uniform), so there
is no time step; frames sample the piecewise linear motion at the frame
time and the counter counts every click up to that time, including the
sub-millisecond ones at the turnaround. Deterministic, no seed.

Measured and printed: the closed form count and the sim's count for
mass ratios 1, 100, 10,000 and 1,000,000; for each drawn ratio the
block-on-block and wall clicks, the click at which the heavy block
stops and how close its face gets to the wall, the light block's peak
speed, the fastest click interval, the last click and the lone last
trip before it, the final speeds, the energy drift, the momentum given
to the wall and the momentum drift across block-on-block clicks; the
click schedule in video time at the playback factor; the on-screen
text widths.

usage: piblocks.py [--measure-only] [--frames t1,t2,...]
"""

from __future__ import annotations

import bisect
import json
import math
import multiprocessing
import os
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor
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
WHITE = (236, 240, 244)
GHOST = (30, 36, 44)

# Layout: overlay at y 96 (captions.py), four title rows at y 190/252/
# 314/376 for the first seconds, two panels (100 to 1 on top, 10,000 to
# 1 below) each 470 px tall with the wall at x 40..60 and the floor at
# panel top + 450, captions at caption_y 0.75 (y 1440..1520), payoff
# card under them.
PANELS = ({"name": "top", "y": 430, "colour": TEAL}, {"name": "bottom", "y": 940, "colour": CORAL})
PANEL_FLOOR = 450
X_WALL = 60
PAYOFF_Y = 1592.0
LIGHT_H = 120
HEAVY_H = 200


def blend(col, a, base=BG):
    return tuple(int(round(c * a + b * (1 - a))) for c, b in zip(col, base))


def fmt_mass(kg: float) -> str:
    return f"{kg:,.0f} kg"


def closed_form(ratio: float) -> tuple[int, float]:
    """Largest N with N atan(sqrt(m / M)) strictly below pi, and N atan."""
    theta = math.atan(math.sqrt(1.0 / ratio))
    n = int(math.floor(math.pi / theta))
    if n * theta >= math.pi - 1e-12:
        n -= 1
    return n, n * theta


def simulate(man: dict, m_heavy: float) -> dict:
    """Event-driven run. Returns the click list and the state after each click.

    x1 is the light block's left face (the wall is at 0), x2 the heavy
    block's left face; the light block's width sits between them, so the
    contact condition is x2 - x1 == light width. Both blocks move
    uniformly between clicks.
    """
    m, M = man["m_light_kg"], m_heavy
    w = man["light_width_m"]
    x1, v1 = man["wall_gap_m"], 0.0
    x2, v2 = man["wall_gap_m"] + w + man["block_gap_m"], -man["push_speed_mps"]
    t = 0.0
    e0 = 0.5 * M * v2 * v2
    times: list[float] = []
    kinds: list[str] = []
    states: list[tuple[float, float, float, float]] = [(x1, v1, x2, v2)]
    p_wall = 0.0
    p_drift = 0.0
    e_drift = 0.0
    while True:
        cands = []
        if v2 < v1:
            cands.append(((x2 - x1 - w) / (v1 - v2), "block"))
        if v1 < 0.0:
            cands.append((x1 / (-v1), "wall"))
        if not cands:
            break
        dt, kind = min(cands)
        t += dt
        x1 += v1 * dt
        x2 += v2 * dt
        if kind == "block":
            x1 = x2 - w  # exact contact
            p_before = m * v1 + M * v2
            v1, v2 = ((m - M) * v1 + 2.0 * M * v2) / (m + M), ((M - m) * v2 + 2.0 * m * v1) / (m + M)
            p_drift = max(p_drift, abs(m * v1 + M * v2 - p_before) / abs(p_before))
        else:
            x1 = 0.0
            p_wall += 2.0 * m * abs(v1)
            v1 = -v1
        e_drift = max(e_drift, abs(0.5 * m * v1 * v1 + 0.5 * M * v2 * v2 - e0) / e0)
        times.append(t)
        kinds.append(kind)
        states.append((x1, v1, x2, v2))
    return {"M": m_heavy, "times": times, "kinds": kinds, "states": states, "p_wall": p_wall,
            "p_drift": p_drift, "e_drift": e_drift, "e0": e0}


def state_at(run: dict, tau: float) -> tuple[float, float, float, float]:
    k = bisect.bisect_right(run["times"], tau)
    x1, v1, x2, v2 = run["states"][k]
    t0 = run["times"][k - 1] if k > 0 else 0.0
    return x1 + v1 * (tau - t0), v1, x2 + v2 * (tau - t0), v2


def count_at(run: dict, tau: float) -> int:
    return bisect.bisect_right(run["times"], tau)


def measure(man: dict) -> dict:
    m = man["m_light_kg"]
    pb = man["playback"]
    fps = man["fps"]
    print(f"setup: a {m:g} kg block at rest {man['wall_gap_m']:g} m from a wall on a frictionless floor; a heavy block "
          f"{man['block_gap_m']:g} m to its right pushed toward it at {man['push_speed_mps']:g} m/s; every collision "
          f"elastic; two panels, the heavy block {man['m_heavy_kg'][0]:,.0f} kg on top and {man['m_heavy_kg'][1]:,.0f} kg "
          f"below; light block {man['light_width_m']:g} m wide (the width only shifts the contact point; the motion "
          f"depends on the wall gap and the block gap alone); event driven: no time step, each next contact time is "
          f"solved exactly and the motion between clicks is uniform; deterministic, no seed")
    checks = []
    for ratio in man["check_ratios"]:
        n, ntheta = closed_form(ratio)
        run = simulate(man, m * ratio)
        checks.append((ratio, n, len(run["times"])))
        note = " (4 atan(1) = pi exactly, not below it, so 3)" if ratio == 1.0 else ""
        print(f"closed form at mass ratio {ratio:,.0f} to 1: largest N with N atan(sqrt(m / M)) < pi is {n:,} "
              f"(N atan = {ntheta:.6f}, (N + 1) atan = {ntheta + ntheta / n:.6f}, pi = {math.pi:.6f}){note}; "
              f"sim counts {len(run['times']):,} clicks")
    runs = {}
    for panel, M in zip(PANELS, man["m_heavy_kg"]):
        run = simulate(man, M)
        runs[panel["name"]] = run
        T, K, S = run["times"], run["kinds"], run["states"]
        n = len(T)
        n_block = K.count("block")
        n_wall = K.count("wall")
        stop = next(i for i, s in enumerate(S[1:]) if s[3] >= 0.0)  # index of the click after which v2 >= 0
        x_close = min(s[2] for s in S)
        speeds = [abs(s[1]) for s in S[1:]]
        peak_i = int(np.argmax(speeds))
        gaps = np.diff(T)
        fast_i = int(np.argmin(gaps))
        x1f, v1f, x2f, v2f = S[-1]
        e_end = 0.5 * m * v1f * v1f + 0.5 * M * v2f * v2f
        print(f"{panel['name']} panel, {M:,.0f} kg into {m:g} kg ({M / m:,.0f} to 1): {n:,} clicks in all, "
              f"{n_block:,} block on block and {n_wall:,} on the wall; first click at {T[0]:.4f} s; the heavy block "
              f"stops (its speed passes zero) at click {stop + 1:,} at {T[stop]:.4f} s with its face {x_close * 100:.2f} cm "
              f"from the wall at the closest; the light block peaks at {speeds[peak_i]:.3f} m/s after click "
              f"{peak_i + 1:,} at {T[peak_i]:.4f} s; fastest click interval {gaps[fast_i] * 1e3:.4f} ms between clicks "
              f"{fast_i + 1:,} and {fast_i + 2:,} at {T[fast_i]:.4f} s; click {n - 1:,} ({K[-2]}) at {T[-2]:.4f} s, "
              f"then the light block's lone last trip at {abs(S[-2][1]):.3f} m/s takes {T[-1] - T[-2]:.4f} s to click "
              f"{n:,} ({K[-1]}) at {T[-1]:.4f} s, with the heavy block's face {x2f:.3f} m from the wall; after it the "
              f"light block moves right at {v1f:.4f} m/s and the heavy block at {v2f:.4f} m/s, so they never meet again; "
              f"energy {e_end:.6f} J against {run['e0']:.6f} J at the start (largest relative drift {run['e_drift']:.2e}); "
              f"momentum given to the wall {run['p_wall']:.4f} kg m/s (start {-M * man['push_speed_mps']:.1f}, end "
              f"{m * v1f + M * v2f:.4f}); largest relative momentum drift across a block-on-block click {run['p_drift']:.2e}")
    ppm = man["px_per_m"]
    track_m = (W - 40 - X_WALL) / ppm
    for panel in PANELS:
        run = runs[panel["name"]]
        T, S = run["times"], run["states"]
        n = len(T)
        stop = next(i for i, s in enumerate(S[1:]) if s[3] >= 0.0)
        # when the heavy block's right face passes the right edge of the frame
        x_exit = (W - X_WALL) / ppm - man["heavy_width_m"]
        t_exit = None
        for k in range(len(S)):
            x1, v1, x2, v2 = S[k]
            t0 = T[k - 1] if k > 0 else 0.0
            t1 = T[k] if k < n else math.inf
            if v2 > 0 and x2 <= x_exit and x2 + v2 * (t1 - t0) > x_exit:
                t_exit = t0 + (x_exit - x2) / v2
                break
        exit_txt = f"{t_exit / pb:.2f} s" if t_exit else "never"
        print(f"video, {panel['name']} panel at 1/{round(1 / pb)} speed ({pb:g}): first click at {T[0] / pb:.2f} s, "
              f"the heavy block stops at {T[stop] / pb:.2f} s (click {stop + 1:,}), click {n - 1:,} at {T[-2] / pb:.2f} s, "
              f"the last click {n:,} at {T[-1] / pb:.2f} s; the heavy block's right face leaves the frame (x {W}) at {exit_txt}; "
              f"a frame is {1e3 * pb / fps:.3f} ms of real time, at most "
              f"{max(count_at(run, (f + 1) * pb / fps) - count_at(run, f * pb / fps) for f in range(int(man['scene_duration'] * fps))):,} "
              f"clicks fall in one frame")
        if n <= 40:
            print(f"  click times, video s: " + " ".join(f"{t / pb:.2f}{k[0]}" for t, k in zip(T, run["kinds"])))
        else:
            picks = list(range(0, n, 25)) + list(range(n - 5, n))
            print(f"  click times, video s (every 25th and the last five): "
                  + " ".join(f"#{i + 1} {T[i] / pb:.2f}{run['kinds'][i][0]}" for i in sorted(set(picks))))
    print(f"track: {track_m:.3f} m across {W - 40 - X_WALL} px at {ppm:g} px/m; the start needs "
          f"{man['wall_gap_m'] + man['light_width_m'] + man['block_gap_m'] + man['heavy_width_m']:.2f} m; "
          f"the heavy block is drawn {man['heavy_width_m'] * ppm:.0f} x {HEAVY_H} px in both panels (a fixed size with a "
          f"mass label, not the cube-root size ratio); payoff card at {man['payoff_t']:g} s")
    return {"runs": runs, "checks": checks}


class Renderer:
    def __init__(self, man: dict, meas: dict):
        self.man, self.meas = man, meas
        self.fps = man["fps"]
        font = os.environ["SEED_ZERO_FONT"]
        self.font = ImageFont.truetype(font, 40)
        self.font_title = ImageFont.truetype(font, 56)
        self.font_small = ImageFont.truetype(font, 28)
        self.font_count = ImageFont.truetype(font, 88)
        self.font_unit = ImageFont.truetype(font, 36)
        self.font_status = ImageFont.truetype(font, 32)
        self.font_mass = ImageFont.truetype(font, 36)
        self.font_mass_small = ImageFont.truetype(font, 26)
        self.first = None
        self.ppm = man["px_per_m"]
        self.tag = f"1/{round(1 / man['playback'])} speed"
        widths = {"overlay@34": (ImageFont.truetype(font, 34), man["overlay"])}
        for j, line in enumerate(man["title"].split("|")):
            widths[f"title line {j + 1}@56"] = (self.font_title, line)
        for M in man["m_heavy_kg"]:
            widths[f"label {M:,.0f}@40"] = (self.font, self.label(M))
            widths[f"sublabel {M:,.0f}@28"] = (self.font_small, self.sublabel(M))
            widths[f"mass {M:,.0f}@36"] = (self.font_mass, fmt_mass(M))
        widths["tag@28"] = (self.font_small, self.tag)
        widths["counter@88"] = (self.font_count, f"{len(meas['runs']['bottom']['times'])}")
        widths["unit@36"] = (self.font_unit, "clicks")
        widths["status@32"] = (self.font_status, "parted for good")
        widths["light mass@26"] = (self.font_mass_small, fmt_mass(man["m_light_kg"]))
        for j, line in enumerate(self.payoff_lines()):
            widths[f"payoff line {j + 1}@40"] = (self.font, line)
        print("text widths: " + ", ".join(f"{k} {f.getlength(s):.0f} px" for k, (f, s) in widths.items()))

    def label(self, M: float) -> str:
        return f"{M / self.man['m_light_kg']:,.0f} times heavier"

    def sublabel(self, M: float) -> str:
        return f"{fmt_mass(M)} pushed at {self.man['push_speed_mps']:g} m/s into {fmt_mass(self.man['m_light_kg'])} at rest"

    def payoff_lines(self) -> list[str]:
        runs = self.meas["runs"]
        text = self.man["payoff_text"].format(top=len(runs["top"]["times"]), bottom=len(runs["bottom"]["times"]))
        return [s.strip() for s in text.split("|")]

    def draw_panel(self, d: ImageDraw.ImageDraw, panel: dict, t: float) -> None:
        man = self.man
        run = self.meas["runs"][panel["name"]]
        col = panel["colour"]
        py = panel["y"]
        floor = py + PANEL_FLOOR
        pb = man["playback"]
        tau = t * pb
        M = run["M"]
        ppm = self.ppm
        wl = man["light_width_m"] * ppm
        wh = man["heavy_width_m"] * ppm
        # header
        d.text((40, py + 24), self.label(M), font=self.font, fill=col, anchor="lm")
        d.text((W - 40, py + 24), self.tag, font=self.font_small, fill=MUTED, anchor="rm")
        d.text((40, py + 70), self.sublabel(M), font=self.font_small, fill=MUTED, anchor="lm")
        # wall and floor
        d.rectangle((40, py + 240, X_WALL, floor), fill=WIRE)
        d.line((40, floor, W - 40, floor), fill=WIRE, width=4)
        # light block ghosts over the frame's exposure, then the blocks at the frame time
        n_ghost = man["ghosts"]
        for j in range(1, n_ghost + 1):
            tg = tau - j * pb / (self.fps * n_ghost)
            if tg < 0.0:
                continue
            x1, _, _, _ = state_at(run, tg)
            xa = X_WALL + x1 * ppm
            d.rectangle((xa, floor - LIGHT_H, xa + wl, floor), fill=blend(GOLD, 0.16))
        x1, v1, x2, v2 = state_at(run, tau)
        xh = X_WALL + x2 * ppm
        if xh < W:
            d.rectangle((xh, floor - HEAVY_H, xh + wh, floor), fill=col)
            d.text((xh + wh / 2, floor - HEAVY_H / 2), fmt_mass(M), font=self.font_mass, fill=BG, anchor="mm")
        xa = X_WALL + x1 * ppm
        d.rectangle((xa, floor - LIGHT_H, xa + wl, floor), fill=GOLD)
        d.text((xa + wl / 2, floor - LIGHT_H / 2), fmt_mass(man["m_light_kg"]), font=self.font_mass_small, fill=BG, anchor="mm")
        # click flashes: the wall face and the heavy block's face light up for flash_s of video after a click
        flash = man["flash_s"] * pb
        k = bisect.bisect_right(run["times"], tau)
        wall_a = block_a = 0.0
        i = k - 1
        while i >= 0 and tau - run["times"][i] < flash:
            a = 1.0 - (tau - run["times"][i]) / flash
            if run["kinds"][i] == "wall":
                wall_a = max(wall_a, a)
            else:
                block_a = max(block_a, a)
            i -= 1
        if wall_a > 0.0:
            d.rectangle((X_WALL - 4, floor - LIGHT_H - 20, X_WALL + 4, floor), fill=blend(WHITE, wall_a, WIRE))
        if block_a > 0.0 and xh < W:
            d.rectangle((xh - 4, floor - HEAVY_H - 20, xh + 4, floor), fill=blend(WHITE, block_a, col))
        # counter and status
        n = len(run["times"])
        count_col = col if k == n else TEXT
        d.text((640, py + 150), f"{k:,}", font=self.font_count, fill=count_col, anchor="rm")
        d.text((664, py + 160), "clicks", font=self.font_unit, fill=MUTED, anchor="lm")
        if k == 0:
            word, wcol = "pushing", MUTED
        elif k == n:
            word, wcol = "parted for good", col
        else:
            word, wcol = "", MUTED
        if word:
            d.text((540, py + 218), word, font=self.font_status, fill=wcol, anchor="mm")

    def live_frame(self, f: int) -> np.ndarray:
        man = self.man
        t = f / self.fps
        img = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(img)
        for panel in PANELS:
            self.draw_panel(d, panel, t)
        if t < man["title_until"]:
            a = 1.0 if t < man["title_until"] - 0.4 else (man["title_until"] - t) / 0.4
            for j, line in enumerate(man["title"].split("|")):
                d.text((W / 2, 190 + j * 62), line, font=self.font_title, fill=blend(TEXT, a), anchor="mm")
        if t >= man["payoff_t"]:
            a = min(1.0, (t - man["payoff_t"]) / man["payoff_hold"])
            for j, line in enumerate(self.payoff_lines()):
                d.text((W / 2, PAYOFF_Y + j * 56), line, font=self.font, fill=blend(GOLD, a), anchor="mm")
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
        global _RENDERER
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
        _RENDERER = self
        workers = min(8, os.cpu_count() or 1)
        with ProcessPoolExecutor(max_workers=workers, mp_context=multiprocessing.get_context("fork")) as pool:
            for f, frame in enumerate(pool.map(_frame_bytes, range(total), chunksize=8)):
                proc.stdin.write(frame)
                if f % 300 == 0:
                    print(f"frame {f}/{total}", file=sys.stderr)
        proc.stdin.close()
        if proc.wait() != 0:
            raise RuntimeError("ffmpeg failed")
        print(f"footage: {out_path} ({total / self.fps:.2f}s at {self.fps} fps)")


_RENDERER: Renderer | None = None


def _frame_bytes(f: int) -> bytes:
    assert _RENDERER is not None
    return _RENDERER.frame_at(f).tobytes()


def main() -> None:
    man = json.loads((ROOT / "projects/piblocks/manifest.json").read_text())
    meas = measure(man)
    if "--measure-only" in sys.argv:
        return
    if "--frames" in sys.argv:
        times = [float(v) for v in sys.argv[sys.argv.index("--frames") + 1].split(",")]
        r = Renderer(man, meas)
        (ROOT / "media/piblocks").mkdir(parents=True, exist_ok=True)
        for tv in times:
            Image.fromarray(r.frame_at(int(round(tv * man["fps"])))).save(ROOT / f"media/piblocks/smoke-{tv}.png")
        print("smoke frames: " + ", ".join(f"{tv}" for tv in times))
        return
    Renderer(man, meas).render(ROOT / "media/piblocks/footage.mp4")


if __name__ == "__main__":
    main()
