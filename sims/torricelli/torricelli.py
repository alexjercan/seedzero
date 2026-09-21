#!/usr/bin/env python3
"""Torricelli jets: three holes in a full tank. Which jet lands farthest?

A tank of water H = 1 m deep stands on the floor and is kept full. Three
holes in its right wall sit h = 0.25, 0.50 and 0.75 m below the surface.
Each hole emits a horizontal jet at the Torricelli speed v = sqrt(2 g h);
the jets are drawn as streams of particles, one particle every
emit_interval seconds of simulated time, and each particle then falls
freely (closed form, g = 9.80665) until it reaches the floor. The
landing distance of each jet is measured by stepping one particle at
steps_per_second and locating the floor crossing, then checked against
the closed form 2 sqrt(h (H - h)). Played at 1/slow_factor speed. The
emission period divides the scene, so the streams are periodic and the
last frame continues into the first. Deterministic, no seed.

Measured and printed: for each hole the depth, the height above the
floor, the exit speed, the fall time, the landing distance (stepped
particle and closed form), the particle spacing and the count in flight;
the closed forms, the depth of the longest jet, the symmetric pairs and
a scan of other depths (not drawn); a draining note (closed form, not
drawn); the video schedule (closing, re-opening, first landings, label
times) and the on-screen text widths.

usage: torricelli.py [--measure-only] [--frames t1,t2,...]
"""

from __future__ import annotations

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
WHITE = (236, 240, 244)
WATER = (36, 78, 128)
SURFACE = (110, 170, 220)
GLASS = (150, 164, 182)
SLAB = (48, 56, 68)
FLOOR = (120, 132, 150)
PLUG = (196, 204, 214)

# Layout: overlay at y 96 (captions.py), title rows at y 190/252 for the
# first seconds, the tank on the left with its surface at y 460 and the
# floor at y 1160 (1 m at px_per_m = 700), the jets to the right of the
# wall at x 250, a floor slab with the ruler marks (0, 0.5 m, 1.0 m)
# engraved in it, the landing labels on two rows under the slab (leaders
# start below the slab so they cross no ruler label), captions at
# caption_y 0.75 (y 1440..1520), the payoff card under them from y 1592.
HOLES = {"top": TEAL, "middle": GOLD, "bottom": CORAL}
GEOM_Y0, GEOM_Y1 = 400, 1340
SURFACE_Y = 460.0
TANK_X0, TANK_X1 = 40.0, 242.0  # the water
WALL = 8.0
JET_X0 = TANK_X1 + WALL  # outer face of the right wall: x = 0 for the jets
RIM = 16.0
SS = 2
PAYOFF_Y = 1592.0
SLAB_H = 44.0
RULER_DY = 30.0  # ruler label centre below the floor line, inside the slab
ROW_Y = {"middle": 1256.0, "tie": 1304.0}
TITLE_Y = 190.0


def blend(col, a, base=BG):
    a = max(0.0, min(1.0, a))
    return tuple(int(round(c * a + b * (1 - a))) for c, b in zip(col, base))


def torricelli(g: float, h: float) -> float:
    return math.sqrt(2.0 * g * h)


def fall_time(g: float, y0: float) -> float:
    return math.sqrt(2.0 * y0 / g)


def closed_range(H: float, h: float) -> float:
    return 2.0 * math.sqrt(h * (H - h))


def step_particle(g: float, v: float, y0: float, steps: int) -> dict:
    """One particle from (0, y0) with velocity (v, 0), stepped at 1/steps s until it reaches the floor.

    Each step is the exact constant-acceleration update; the floor crossing
    is located by linear interpolation inside the step that crosses.
    """
    dt = 1.0 / steps
    x, y, vy = 0.0, y0, 0.0
    peak_v = 0.0
    for i in range(10 * steps):
        x_new = x + v * dt
        y_new = y + vy * dt - 0.5 * g * dt * dt
        vy_new = vy - g * dt
        if y_new <= 0.0:
            frac = y / (y - y_new)
            t_land = (i + frac) * dt
            return {"t": t_land, "x": x + frac * (x_new - x), "vy": vy + frac * (vy_new - vy),
                    "steps": i + 1, "dt": dt}
        x, y, vy = x_new, y_new, vy_new
    raise RuntimeError("the particle never reached the floor")


def measure(man: dict) -> dict:
    g, Hd = man["g"], man["tank_depth_m"]
    fps, slow, steps = man["fps"], man["slow_factor"], man["steps_per_second"]
    p = man["emit_interval_s"]
    depths = man["hole_depths_m"]
    print(f"setup: a tank of water {Hd:g} m deep standing on the floor, kept full (constant level); three holes in its "
          f"right wall {depths['top']:g}, {depths['middle']:g} and {depths['bottom']:g} m below the surface; each hole "
          f"emits a horizontal jet at the Torricelli speed sqrt(2 g h) drawn as a stream of particles, one every "
          f"{p:g} s of simulated time ({1 / p:g} per second), each in free fall (closed form) to the floor; g = {g:g} "
          f"m/s^2; no air drag; the landing distance is measured by stepping one particle at {steps} steps per second "
          f"(dt = {1 / steps:.2e} s) and locating the floor crossing; played at 1/{slow:g} speed; deterministic, no seed")
    print(f"closed forms: exit speed v = sqrt(2 g h); fall time t = sqrt(2 (H - h) / g); range R = v t = 2 sqrt(h (H - h)); "
          f"R is largest where h (H - h) is largest, at h = H / 2 = {Hd / 2:g} m, where R = H = {Hd:g} m exactly; "
          f"h and H - h give the same range (the pairs tie)")
    holes = {}
    for name, h in depths.items():
        y0 = Hd - h
        v = torricelli(g, h)
        t = fall_time(g, y0)
        R = closed_range(Hd, h)
        m = step_particle(g, v, y0, steps)
        spacing = v * p
        n_flight = int(math.ceil(t / p))
        holes[name] = {"h": h, "y0": y0, "v": v, "t": t, "R": R, "x_meas": m["x"], "t_meas": m["t"],
                       "spacing": spacing, "n_flight": n_flight, "vy_land": m["vy"]}
        print(f"{name} hole, {h:g} m below the surface ({h / Hd:g} of the depth), {y0:g} m above the floor: exit speed "
              f"sqrt(2 g h) = {v:.4f} m/s; fall time sqrt(2 (H - h) / g) = {t:.4f} s; stepped particle reaches the floor "
              f"at {m['t']:.4f} s ({m['steps']} steps, {m['t'] - t:+.1e} s), {m['x']:.4f} m from the wall (closed form "
              f"2 sqrt(h (H - h)) = {R:.4f} m, {m['x'] - R:+.1e} m), moving {abs(m['vy']):.3f} m/s down and {v:.3f} m/s "
              f"along at the landing ({math.degrees(math.atan2(abs(m['vy']), v)):.1f} degrees below horizontal); "
              f"particles {spacing * 100:.2f} cm apart along the jet, {n_flight} in flight at a time")
    rt, rm, rb = (holes[n]["x_meas"] for n in ("top", "middle", "bottom"))
    order = sorted(holes, key=lambda n: -holes[n]["x_meas"])
    print(f"result: the middle jet lands farthest, {rm:.4f} m from the wall; the top jet lands at {rt:.4f} m and the bottom "
          f"jet at {rb:.4f} m, a tie to {abs(rt - rb):.1e} m; the middle jet beats them by {rm - rt:.4f} m = "
          f"{(rm - rt) * 100:.1f} cm; order {' > '.join(order)}; the bottom jet leaves "
          f"{holes['bottom']['v'] / holes['top']['v']:.3f} times faster than the top jet but flies "
          f"{holes['top']['t'] / holes['bottom']['t']:.3f} times shorter")
    scan = ", ".join(f"{h:g} m -> {closed_range(Hd, h):.4f} m" for h in man["check_depths_m"])
    print(f"check depths (closed form, not drawn): {scan}; a hole at the surface or at the floor gives 0 m")
    T_note = 1.0 - math.sqrt(0.5)
    print(f"draining note (closed form, not drawn, not narrated): if the tank were left to drain through one hole in "
          f"its bottom, the level would fall as H (1 - t / T)^2, so the top half of the water leaves in "
          f"{T_note * 100:.1f} percent of the emptying time T and the bottom half takes the other "
          f"{(1 - T_note) * 100:.1f} percent")
    # Schedule in video frames.
    Pf = p * slow * fps
    assert abs(Pf - round(Pf)) < 1e-9, "the emission period must be a whole number of frames"
    Pf = int(round(Pf))
    total = int(round(man["scene_duration"] * fps))
    assert total % Pf == 0, "the emission period must divide the scene"
    close_f = int(round(man["close_at"] * fps))
    sched = {"Pf": Pf, "total": total, "close_f": close_f, "open_f": {}, "first_emit_f": {}, "land_f": {},
             "last_emit_f": None, "drained_f": {}}
    last_emit = (math.ceil(close_f / Pf) - 1) * Pf
    sched["last_emit_f"] = last_emit
    lines = []
    for name in HOLES:
        of = int(round(man["open_at"][name] * fps))
        fe0 = math.ceil(of / Pf) * Pf
        tf = holes[name]["t"] * slow * fps
        land_f = fe0 + tf
        drained = last_emit + tf
        sched["open_f"][name] = of
        sched["first_emit_f"][name] = fe0
        sched["land_f"][name] = land_f
        sched["drained_f"][name] = drained
        lines.append(f"{name}: last particle before the closing lands {drained / fps:.2f} s; re-opens {of / fps:.2f} s, "
                     f"first particle out {fe0 / fps:.3f} s, lands {land_f / fps:.2f} s (the landing mark and the "
                     f"{'tie ' if name != 'middle' else ''}label appear then)")
    print(f"schedule (1/{slow:g} speed; one particle every {Pf} frames from each open hole, {total // Pf} emissions in "
          f"the {man['scene_duration']:g} s scene, so the streams are periodic and frame {total} equals frame 0; all "
          f"three jets flow from the first frame; the holes close at {man['close_at']:g} s, last particle out "
          f"{last_emit / fps:.3f} s): " + "; ".join(lines))
    print(f"title until {man['title_until']:g} s; payoff card from {man['payoff_t']:g} s; loop crossfade over the last "
          f"{man['loop_fade']:g} s (the card, the marks and the labels fade out, the title fades in; the streams run "
          f"through the loop point unchanged)")
    # Text widths.
    font = os.environ["SEED_ZERO_FONT"]
    f26, f28, f32, f34, f36, f40, f56 = (ImageFont.truetype(font, n) for n in (26, 28, 32, 34, 36, 40, 56))
    widths = {"overlay@34": (f34, man["overlay"])}
    for j, line in enumerate(man["title"].split("|")):
        widths[f"title line {j + 1}@56"] = (f56, line)
    widths["tank label@28"] = (f28, tank_label(man))
    for name in HOLES:
        widths[f"{name} depth label@28"] = (f28, depth_label(holes[name]))
        widths[f"{name} speed label@32"] = (f32, speed_label(holes[name]))
    for s in ("0", "0.5 m", "1.0 m"):
        widths[f"ruler {s}@26"] = (f26, s)
    widths["middle landing label@36"] = (f36, dist_label(holes["middle"]))
    widths["tie landing label@36"] = (f36, dist_label(holes["bottom"]) + ", a tie")
    for j, line in enumerate(payoff_lines(man, holes)):
        widths[f"payoff line {j + 1}@40"] = (f40, line)
    print("text widths: " + ", ".join(f"{k} {f.getlength(s):.0f} px" for k, (f, s) in widths.items()))
    return {"holes": holes, "sched": sched}


def tank_label(man: dict) -> str:
    return f"{man['tank_depth_m']:g} m of water, kept full"


def depth_label(hole: dict) -> str:
    return f"{hole['h']:.2f} m down"


def speed_label(hole: dict) -> str:
    return f"{hole['v']:.2f} m/s"


def dist_label(hole: dict) -> str:
    return f"{hole['x_meas']:.2f} m"


def payoff_lines(man: dict, holes: dict) -> list[str]:
    text = man["payoff_text"].format(mid=holes["middle"]["x_meas"], tie=holes["bottom"]["x_meas"])
    return [s.strip() for s in text.split("|")]


class Renderer:
    def __init__(self, man: dict, meas: dict):
        self.man, self.meas = man, meas
        self.holes, self.sched = meas["holes"], meas["sched"]
        self.fps = man["fps"]
        self.slow = float(man["slow_factor"])
        self.ppm = float(man["px_per_m"])
        self.g = man["g"]
        self.pr = float(man["particle_r_px"])
        self.total = self.sched["total"]
        self.Pf = self.sched["Pf"]
        font = os.environ["SEED_ZERO_FONT"]
        self.f26 = ImageFont.truetype(font, 26)
        self.f28 = ImageFont.truetype(font, 28)
        self.f32 = ImageFont.truetype(font, 32)
        self.f36 = ImageFont.truetype(font, 36)
        self.f40 = ImageFont.truetype(font, 40)
        self.f56 = ImageFont.truetype(font, 56)
        self.floor_y = SURFACE_Y + man["tank_depth_m"] * self.ppm
        self.first = None

    # --- geometry helpers -------------------------------------------------
    def hole_y(self, name: str) -> float:
        return SURFACE_Y + self.holes[name]["h"] * self.ppm

    def jet_px(self, x: float, y: float) -> tuple[float, float]:
        """Screen point for a jet position x m from the wall, y m above the floor."""
        return JET_X0 + x * self.ppm, self.floor_y - y * self.ppm

    def is_open(self, name: str, f_emit: int) -> bool:
        """Whether the hole emits at video frame f_emit (negative frames are the tail of the previous loop)."""
        if f_emit < self.sched["close_f"]:
            return True
        return f_emit >= self.sched["open_f"][name]

    def particles(self, name: str, f: int) -> list[tuple[float, float]]:
        """(x, y) in metres of every particle of one jet in flight at video frame f."""
        hole = self.holes[name]
        tf = hole["t"] * self.slow * self.fps
        k_lo = math.ceil((f - tf) / self.Pf)
        k_hi = f // self.Pf
        out = []
        for k in range(k_lo, k_hi + 1):
            fe = k * self.Pf
            age_f = f - fe
            if age_f < 0 or age_f >= tf or not self.is_open(name, fe):
                continue
            a = age_f / (self.fps * self.slow)
            out.append((hole["v"] * a, hole["y0"] - 0.5 * self.g * a * a))
        return out

    def landed(self, name: str, f: int) -> bool:
        return f >= self.sched["land_f"][name]

    # --- drawing ----------------------------------------------------------
    def draw_geometry(self, f: int) -> Image.Image:
        """Tank, water, holes, jets, floor and ruler ticks on the supersampled layer."""
        layer = Image.new("RGB", (W * SS, (GEOM_Y1 - GEOM_Y0) * SS), BG)
        d = ImageDraw.Draw(layer)

        def P(sx: float, sy: float) -> tuple[float, float]:
            return sx * SS, (sy - GEOM_Y0) * SS

        fy = self.floor_y
        # Water and its surface.
        d.rectangle((*P(TANK_X0, SURFACE_Y), *P(TANK_X1, fy)), fill=WATER)
        d.rectangle((*P(TANK_X0, SURFACE_Y - 1.5), *P(TANK_X1, SURFACE_Y + 1.5)), fill=SURFACE)
        # Glass walls and the tank bottom; the floor slab runs to the right.
        d.rectangle((*P(TANK_X0 - WALL, SURFACE_Y - RIM), *P(TANK_X0, fy)), fill=GLASS)
        d.rectangle((*P(TANK_X1, SURFACE_Y - RIM), *P(JET_X0, fy)), fill=GLASS)
        d.rectangle((*P(TANK_X0 - WALL, fy), *P(W - 20, fy + SLAB_H)), fill=SLAB)
        d.rectangle((*P(TANK_X0 - WALL, fy - 1.5), *P(W - 20, fy + 1.5)), fill=FLOOR)
        # Ruler ticks engraved in the slab.
        for x in (0.0, 0.5, 1.0):
            sx = JET_X0 + x * self.ppm
            d.rectangle((*P(sx - 1.5, fy + 2), *P(sx + 1.5, fy + 14)), fill=MUTED)
        # Holes: an opening through the right wall, plugged when closed.
        for name, col in HOLES.items():
            hy = self.hole_y(name)
            r = 9.0
            d.rectangle((*P(TANK_X1 - 2, hy - r), *P(JET_X0 + 1, hy + r)), fill=BG)
            if not self.is_open(name, f):
                d.rectangle((*P(TANK_X1 - 4, hy - r - 3), *P(JET_X0 + 6, hy + r + 3)), fill=PLUG)
        # Jets.
        for name, col in HOLES.items():
            pr = self.pr * SS
            core = blend(WHITE, 0.55, col)
            for x, y in self.particles(name, f):
                sx, sy = self.jet_px(x, y)
                px, py = P(sx, sy)
                d.ellipse((px - pr, py - pr, px + pr, py + pr), fill=col)
                cr = pr * 0.42
                d.ellipse((px - cr * 1.3, py - cr * 1.3, px + cr * 0.3, py + cr * 0.3), fill=core)
        return layer.reduce(SS)

    def draw_labels(self, d: ImageDraw.ImageDraw, f: int) -> None:
        """Tank label, ruler labels, depth and speed labels (independent of the fade)."""
        d.text((TANK_X0 - WALL, SURFACE_Y - RIM - 24), tank_label(self.man), font=self.f28, fill=MUTED, anchor="lm")
        for x, s in ((0.0, "0"), (0.5, "0.5 m"), (1.0, "1.0 m")):
            d.text((JET_X0 + x * self.ppm, self.floor_y + RULER_DY), s, font=self.f26, fill=MUTED, anchor="mm")
        for name, col in HOLES.items():
            hy = self.hole_y(name)
            hole = self.holes[name]
            d.text((JET_X0 + 16, hy - 60), depth_label(hole), font=self.f28, fill=TEXT, anchor="lm")
            if self.is_open(name, f):
                d.text((JET_X0 + 16, hy - 26), speed_label(hole), font=self.f32, fill=col, anchor="lm")

    def draw_marks(self, d: ImageDraw.ImageDraw, f: int, alpha: float) -> None:
        """Landing ticks, leaders, distance labels and the first-landing flash."""
        if alpha <= 0.0:
            return
        fy = self.floor_y
        flash = self.man["mark_flash"] * self.fps
        landed = {name: self.landed(name, f) for name in HOLES}
        for name, col in HOLES.items():
            if not landed[name]:
                continue
            x_land = JET_X0 + self.holes[name]["x_meas"] * self.ppm
            dx = {"top": -4.0, "middle": 0.0, "bottom": 4.0}[name]
            d.rectangle((x_land + dx - 2.5, fy - 24, x_land + dx + 2.5, fy - 2), fill=blend(col, alpha))
            u = (f - self.sched["land_f"][name]) / flash
            if 0.0 <= u < 1.0:
                rr = 18 + 70 * u
                d.ellipse((x_land - rr, fy - rr, x_land + rr, fy + rr), outline=blend(col, alpha * (1 - u)), width=4)
        # Middle jet: its own row.
        if landed["middle"]:
            hole = self.holes["middle"]
            x_land = JET_X0 + hole["x_meas"] * self.ppm
            d.rectangle((x_land - 1, fy + SLAB_H + 4, x_land + 1, ROW_Y["middle"] - 22), fill=blend(GOLD, 0.7 * alpha))
            d.text((x_land, ROW_Y["middle"]), dist_label(hole), font=self.f36, fill=blend(GOLD, alpha), anchor="mm")
        # Top and bottom: one shared row at the tie point.
        if landed["top"] or landed["bottom"]:
            first = "bottom" if landed["bottom"] else "top"
            hole = self.holes[first]
            x_land = JET_X0 + hole["x_meas"] * self.ppm
            both = landed["top"] and landed["bottom"]
            col = TEXT if both else HOLES[first]
            text = dist_label(hole) + (", a tie" if both else "")
            d.rectangle((x_land - 1, fy + SLAB_H + 4, x_land + 1, ROW_Y["tie"] - 22), fill=blend(col, 0.7 * alpha))
            d.text((x_land, ROW_Y["tie"]), text, font=self.f36, fill=blend(col, alpha), anchor="mm")

    def draw_title(self, d: ImageDraw.ImageDraw, alpha: float) -> None:
        if alpha <= 0.0:
            return
        for j, line in enumerate(self.man["title"].split("|")):
            d.text((W / 2, TITLE_Y + j * 62), line, font=self.f56, fill=blend(TEXT, alpha), anchor="mm")

    def draw_card(self, d: ImageDraw.ImageDraw, alpha: float) -> None:
        if alpha <= 0.0:
            return
        for j, line in enumerate(payoff_lines(self.man, self.holes)):
            d.text((W / 2, PAYOFF_Y + j * 56), line, font=self.f40, fill=blend(GOLD, alpha), anchor="mm")

    def frame_at(self, f: int) -> np.ndarray:
        man = self.man
        t = f / self.fps
        img = Image.new("RGB", (W, H), BG)
        img.paste(self.draw_geometry(f), (0, GEOM_Y0))
        d = ImageDraw.Draw(img)
        self.draw_labels(d, f)
        if t < man["title_until"] - 0.4:
            title_a = 1.0
        elif t < man["title_until"]:
            title_a = (man["title_until"] - t) / 0.4
        else:
            title_a = 0.0
        card_a = min(1.0, (t - man["payoff_t"]) / man["payoff_hold"]) if t >= man["payoff_t"] else 0.0
        marks_a = 1.0
        fade_frames = int(round(man["loop_fade"] * self.fps))
        if f >= self.total - fade_frames:
            a = min(1.0, (f - (self.total - fade_frames) + 1) / fade_frames)
            title_a = max(title_a, a)
            card_a *= 1.0 - a
            marks_a = 1.0 - a
        self.draw_marks(d, f, marks_a)
        self.draw_title(d, title_a)
        self.draw_card(d, card_a)
        return np.asarray(img, dtype=np.uint8)

    def render(self, out_path: Path) -> None:
        global _RENDERER
        out_path.parent.mkdir(parents=True, exist_ok=True)
        total = self.total
        first = self.frame_at(0)
        last = self.frame_at(total - 1)
        wrap = self.frame_at(total)
        for label, other in (("the last frame", last), (f"frame {total} (the wrap-around, one step later)", wrap)):
            diff = np.abs(first.astype(int) - other.astype(int))
            print(f"loop check: {label} differs from the first in {int((diff.max(axis=2) > 24).sum())} px "
                  f"(max channel difference {int(diff.max())})")
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
    man = json.loads((ROOT / "projects/torricelli/manifest.json").read_text())
    meas = measure(man)
    if "--measure-only" in sys.argv:
        return
    if "--frames" in sys.argv:
        times = [float(v) for v in sys.argv[sys.argv.index("--frames") + 1].split(",")]
        r = Renderer(man, meas)
        (ROOT / "media/torricelli").mkdir(parents=True, exist_ok=True)
        for tv in times:
            Image.fromarray(r.frame_at(int(round(tv * man["fps"])))).save(ROOT / f"media/torricelli/smoke-{tv}.png")
        print("smoke frames: " + ", ".join(f"{tv}" for tv in times))
        return
    Renderer(man, meas).render(ROOT / "media/torricelli/footage.mp4")


if __name__ == "__main__":
    main()
