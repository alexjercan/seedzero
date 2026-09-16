#!/usr/bin/env python3
"""Quantum tunnelling: can a ball go through a wall?

Two panels, same wall, same energy. Top: a classical ball with eighty
percent of the energy needed to top a rectangular wall; it bounces back.
Bottom: a quantum wave packet with the same energy (natural units, hbar =
m = 1) hitting the same wall, integrated with the split-step Fourier
method (Strang splitting, periodic grid far wider than the run). The
share of the packet found on the far side of the wall once the packet has
cleared it is the measured payoff. Deterministic, no seed.

Measured and printed: the plane-wave transmission at this energy from the
closed form 1 / (1 + V0^2 sinh^2(kappa a) / (4 E (V0 - E))) for this wall,
half the wall and twice the wall; the packet's mean energy and the share
of its momentum components that could top the wall classically; the
share of the packet reflected, inside the wall and transmitted at the end
of the run with the norm; the video times of the ball's bounce and of the
transmitted share passing half its final value; and checks at half the
time step, twice the grid, half the wall and twice the wall. On screen
the wave panel draws the amplitude |psi| so the transmitted part is
visible; the readout integrates |psi|^2 past the far face.

usage: tunnel.py [--measure-only] [--frames t1,t2,...]
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
WALL = (58, 66, 80)
WALL_EDGE = (120, 132, 150)
WHITE = (236, 240, 244)

# Layout: overlay at y 96 (captions.py), title at y 206 and 268 for the
# first seconds, the ball panel with its floor at BALL_FLOOR, the wave
# panel with its baseline at WAVE_BASE, both walls WALL_H tall, the
# caption band at caption_y 0.75 (y 1440..1510), the payoff under it.
LABEL_Y = 350
BALL_FLOOR = 800
WAVE_LABEL_Y = 900
WAVE_BASE = 1380
WALL_H = 380
WAVE_PEAK_PX = 190
DIVIDER_Y = 850
PAYOFF_Y = 1592.0


def plane_wave_T(E: float, V0: float, a: float) -> float:
    kappa = math.sqrt(2.0 * (V0 - E))
    return 1.0 / (1.0 + V0 * V0 * math.sinh(kappa * a) ** 2 / (4.0 * E * (V0 - E)))


class Packet:
    def __init__(self, man: dict, grid_factor: int = 1, steps_per_frame: int | None = None,
                 wall_width: float | None = None):
        # Cell-centred grid whose cells tile the wall exactly: the wall is
        # wall_cells cells wide, so its width does not move with the grid.
        self.n = man["grid_n"] * grid_factor
        self.dx = man["wall_width"] / (man["wall_cells"] * grid_factor)
        self.L = self.n * self.dx
        self.x = (np.arange(self.n) - self.n / 2 + 0.5) * self.dx
        self.k = 2.0 * np.pi * np.fft.fftfreq(self.n, self.dx)
        self.k0, self.sigma, self.x0 = man["k0"], man["sigma"], man["x0"]
        self.E = 0.5 * self.k0 ** 2
        self.V0 = self.E / man["energy_ratio"]
        self.a = wall_width if wall_width is not None else man["wall_width"]
        spf = steps_per_frame or man["steps_per_frame"]
        self.frames = int(round(man["scene_duration"] * man["fps"]))
        self.dt = man["t_end"] / (self.frames * spf)
        self.spf = spf
        self.V = np.where(np.abs(self.x) < self.a / 2, self.V0, 0.0)
        psi = np.exp(-((self.x - self.x0) ** 2) / (4.0 * self.sigma ** 2)) * np.exp(1j * self.k0 * self.x)
        psi /= math.sqrt(float(np.sum(np.abs(psi) ** 2) * self.dx))
        self.psi = psi.astype(np.complex128)
        self.half_v = np.exp(-0.5j * self.V * self.dt)
        self.kin = np.exp(-0.5j * self.k ** 2 * self.dt)
        self.t = 0.0

    def mean_energy(self) -> float:
        phi = np.fft.fft(self.psi)
        pk = np.abs(phi) ** 2
        pk /= pk.sum()
        return float(np.sum(pk * 0.5 * self.k ** 2) + np.sum(self.V * np.abs(self.psi) ** 2) * self.dx)

    def over_wall_share(self) -> float:
        phi = np.fft.fft(self.psi)
        pk = np.abs(phi) ** 2
        pk /= pk.sum()
        return float(np.sum(pk[0.5 * self.k ** 2 > self.V0]))

    def step(self, m: int) -> None:
        psi = self.psi
        for _ in range(m):
            psi = psi * self.half_v
            psi = np.fft.ifft(self.kin * np.fft.fft(psi))
            psi = psi * self.half_v
        self.psi = psi
        self.t += m * self.dt

    def shares(self) -> tuple[float, float, float]:
        p = np.abs(self.psi) ** 2 * self.dx
        left = float(np.sum(p[self.x < -self.a / 2]))
        inside = float(np.sum(p[np.abs(self.x) < self.a / 2]))
        right = float(np.sum(p[self.x > self.a / 2]))
        return left, inside, right

    def run(self, keep: bool = False) -> tuple[list[np.ndarray] | None, np.ndarray]:
        """Advance to t_end frame by frame; optionally keep |psi|^2 per frame."""
        dens = [] if keep else None
        right = np.empty(self.frames + 1)
        right[0] = self.shares()[2]
        if keep:
            dens.append((np.abs(self.psi) ** 2).astype(np.float32))
        for f in range(1, self.frames + 1):
            self.step(self.spf)
            right[f] = self.shares()[2]
            if keep:
                dens.append((np.abs(self.psi) ** 2).astype(np.float32))
        return dens, right


def ball_x(man: dict, t: float) -> float:
    """The classical ball: speed k0 (hbar = m = 1), hard bounce off the near face."""
    v = man["k0"]
    hit_x = -man["wall_width"] / 2 - man["ball_radius"]
    t_hit = (hit_x - man["x0"]) / v
    if t < t_hit:
        return man["x0"] + v * t
    return hit_x - v * (t - t_hit)


def measure(man: dict) -> dict:
    p = Packet(man)
    scale = man["t_end"] / man["scene_duration"]
    print(f"setup: natural units (hbar = m = 1); wave packet k0 = {p.k0:g}, width sigma = {p.sigma:g}, "
          f"starting at x = {p.x0:g}; kinetic energy k0^2 / 2 = {p.E:g}; wall height V0 = {p.V0:g} so the "
          f"energy is {man['energy_ratio'] * 100:g}% of the wall; wall width a = {p.a:g} (kappa = "
          f"{math.sqrt(2 * (p.V0 - p.E)):g}, kappa a = {math.sqrt(2 * (p.V0 - p.E)) * p.a:.3f}); grid "
          f"{p.n:,} points over {p.L:g} (dx = {p.dx:.4f}), dt = {p.dt:.5f}, {p.frames} frames of "
          f"{p.spf} steps to t = {man['t_end']:g}; the ball has the same energy, speed {p.k0:g}, radius "
          f"{man['ball_radius']:g}; deterministic, no seed")
    T1 = plane_wave_T(p.E, p.V0, p.a)
    Th = plane_wave_T(p.E, p.V0, p.a / 2)
    Td = plane_wave_T(p.E, p.V0, 2 * p.a)
    print(f"closed form, plane wave at E = {man['energy_ratio']:g} V0: transmission {T1 * 100:.3f}% through "
          f"this wall, {Th * 100:.2f}% through half the wall, {Td * 100:.4f}% through twice the wall")
    print(f"packet: mean energy {p.mean_energy():.5f} = {p.mean_energy() / p.V0 * 100:.2f}% of the wall; "
          f"share of its momentum components with enough energy to top the wall classically: "
          f"{p.over_wall_share():.2e}")
    dens, right = p.run(keep=True)
    left, inside, trans = p.shares()
    t_half = float(np.argmax(right >= trans / 2)) / man["fps"]
    t_99 = float(np.argmax(right >= 0.99 * trans)) / man["fps"]
    t_hit = (-p.a / 2 - man["ball_radius"] - p.x0) / p.k0
    print(f"packet at t = {p.t:g}: reflected {left * 100:.3f}%, inside the wall {inside * 100:.2e}%, "
          f"past the wall {trans * 100:.3f}%; norm {left + inside + trans:.10f}; the transmitted share "
          f"passes half its final value at {t_half:.2f} s of video and 99% of it at {t_99:.2f} s; the "
          f"ball hits the wall at t = {t_hit:.2f}, {t_hit / scale:.2f} s of video, and never passes")
    checks = {}
    for label, kw in (("half the time step", {"steps_per_frame": 2 * man["steps_per_frame"]}),
                      ("twice the grid", {"grid_factor": 2}),
                      ("half the wall", {"wall_width": p.a / 2}),
                      ("twice the wall", {"wall_width": 2 * p.a})):
        q = Packet(man, **kw)
        q.run()
        checks[label] = q.shares()[2]
    print(f"checks: past the wall {checks['half the time step'] * 100:.3f}% at half the time step, "
          f"{checks['twice the grid'] * 100:.3f}% on twice the grid; {checks['half the wall'] * 100:.2f}% "
          f"through half the wall ({checks['half the wall'] / trans:.1f}x), "
          f"{checks['twice the wall'] * 100:.4f}% through twice the wall ({trans / checks['twice the wall']:.0f}x less)")
    return {"packet": p, "dens": dens, "right": right, "trans": trans, "left": left, "T1": T1,
            "t_hit": t_hit, "scale": scale}


class Renderer:
    def __init__(self, man: dict, meas: dict):
        self.man, self.meas = man, meas
        self.fps = man["fps"]
        font = os.environ["SEED_ZERO_FONT"]
        self.font = ImageFont.truetype(font, 40)
        self.font_small = ImageFont.truetype(font, 32)
        self.font_title = ImageFont.truetype(font, 56)
        self.font_tag = ImageFont.truetype(font, 28)
        self.first = None
        self.p = meas["packet"]
        self.x_view = man["view_x"]
        self.ppu = W / (self.x_view[1] - self.x_view[0])
        self.cols = self.x_view[0] + (np.arange(W) + 0.5) / self.ppu
        # The curve shows the wave's amplitude |psi| (so the 3% that gets
        # through is visible); the readout is the probability share.
        self.peak0 = math.sqrt(float(meas["dens"][0].max()))
        self.labels = ("the ball, 80% of the energy needed", "the wave, the same 80%")
        widths = {"overlay@34": (ImageFont.truetype(font, 34), man["overlay"])}
        for j, line in enumerate(man["title"].split("|")):
            widths[f"title line {j + 1}@56"] = (self.font_title, line)
        for j, label in enumerate(self.labels):
            widths[f"label {j + 1}@32"] = (self.font_small, label)
        widths["readout@32"] = (self.font_small, "past the wall: 0.0%")
        widths["energy tag@28"] = (self.font_tag, "energy: 80% of the wall")
        for j, line in enumerate(self.payoff_lines()):
            widths[f"payoff line {j + 1}@40"] = (self.font, line)
        print("text widths: " + ", ".join(f"{k} {f.getlength(s):.0f} px" for k, (f, s) in widths.items()))
        print(f"video: {meas['scale']:g} time units per second; the ball bounces at {meas['t_hit'] / meas['scale']:.2f} s; "
              f"payoff card at {man['payoff_t']:g} s")

    def payoff_lines(self) -> list[str]:
        text = self.man["payoff_text"].format(t=self.meas["trans"] * 100)
        return [s.strip() for s in text.split("|")]

    def to_px(self, x: float) -> float:
        return (x - self.x_view[0]) * self.ppu

    def draw_wall(self, d: ImageDraw.ImageDraw, base: float) -> None:
        a = self.p.a
        x0, x1 = self.to_px(-a / 2), self.to_px(a / 2)
        d.rectangle((x0, base - WALL_H, x1, base), fill=WALL, outline=WALL_EDGE, width=2)
        ey = base - WALL_H * self.man["energy_ratio"]
        for xs in range(int(x1) + 24, W - 20, 28):
            d.line([(xs, ey), (xs + 14, ey)], fill=(110, 118, 130), width=2)
        for xs in range(20, int(x0) - 30, 28):
            d.line([(xs, ey), (xs + 14, ey)], fill=(110, 118, 130), width=2)
        d.text((W - 24, ey - 22), "energy: 80% of the wall", font=self.font_tag, fill=MUTED, anchor="rm")

    def draw_scene(self, t: float, title_on: bool) -> Image.Image:
        man, p = self.man, self.p
        f = int(round(t * self.fps))
        f = min(f, len(self.meas["dens"]) - 1)
        sim_t = f / self.fps * self.meas["scale"]
        img = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(img)
        # Ball panel.
        d.line([(0, BALL_FLOOR), (W, BALL_FLOOR)], fill=WIRE, width=2)
        self.draw_wall(d, BALL_FLOOR)
        bx = self.to_px(ball_x(man, sim_t))
        r = man["ball_radius"] * self.ppu
        by = BALL_FLOOR - r - 1
        since = sim_t - self.meas["t_hit"]
        if 0 <= since < 6.0:
            u = since / 6.0
            rr = r + 40 * u
            col = tuple(int(CORAL[q] * (1 - u) + BG[q] * u) for q in range(3))
            d.ellipse((bx - rr, by - rr, bx + rr, by + rr), outline=col, width=3)
        d.ellipse((bx - r, by - r, bx + r, by + r), fill=CORAL)
        d.text((36, LABEL_Y), self.labels[0], font=self.font_small, fill=TEXT, anchor="lm")
        d.text((W - 36, LABEL_Y), "past the wall: 0%", font=self.font_small, fill=CORAL, anchor="rm")
        # Wave panel.
        d.line([(0, DIVIDER_Y), (W, DIVIDER_Y)], fill=WIRE, width=1)
        d.line([(0, WAVE_BASE), (W, WAVE_BASE)], fill=WIRE, width=2)
        self.draw_wall(d, WAVE_BASE)
        amp = np.sqrt(np.interp(self.cols, p.x, self.meas["dens"][f]))
        ys = WAVE_BASE - amp / self.peak0 * WAVE_PEAK_PX
        a = p.a
        regions = ((self.cols < -a / 2, TEAL), (np.abs(self.cols) <= a / 2, (150, 200, 190)), (self.cols > a / 2, GOLD))
        for mask, col in regions:
            idx = np.nonzero(mask)[0]
            if len(idx) < 2:
                continue
            i0, i1 = int(idx[0]), int(idx[-1])
            poly = [(i0, WAVE_BASE)] + [(i, float(ys[i])) for i in range(i0, i1 + 1)] + [(i1, WAVE_BASE)]
            d.polygon(poly, fill=col)
        line = [(i, float(ys[i])) for i in range(W)]
        d.line(line, fill=WHITE, width=2)
        share = float(self.meas["right"][f]) * 100
        d.text((36, WAVE_LABEL_Y), self.labels[1], font=self.font_small, fill=TEXT, anchor="lm")
        d.text((W - 36, WAVE_LABEL_Y), f"past the wall: {share:.1f}%", font=self.font_small, fill=GOLD, anchor="rm")
        return img

    def live_frame(self, f: int) -> np.ndarray:
        man = self.man
        t = f / self.fps
        title_on = t < man["title_until"]
        img = self.draw_scene(t, title_on)
        d = ImageDraw.Draw(img)

        def shade_col(col, a):
            return tuple(int(c * a + BG[j] * (1 - a)) for j, c in enumerate(col))

        if title_on:
            a = 1.0 if t < man["title_until"] - 0.4 else (man["title_until"] - t) / 0.4
            for j, line in enumerate(man["title"].split("|")):
                d.text((W / 2, 206 + j * 62), line, font=self.font_title, fill=shade_col(TEXT, a), anchor="mm")
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
    man = json.loads((ROOT / "projects/tunnel/manifest.json").read_text())
    meas = measure(man)
    if "--measure-only" in sys.argv:
        return
    if "--frames" in sys.argv:
        times = [float(v) for v in sys.argv[sys.argv.index("--frames") + 1].split(",")]
        r = Renderer(man, meas)
        for tv in times:
            Image.fromarray(r.frame_at(int(round(tv * man["fps"])))).save(ROOT / f"media/tunnel/smoke-{tv}.png")
        print("smoke frames: " + ", ".join(f"{tv}" for tv in times))
        return
    Renderer(man, meas).render(ROOT / "media/tunnel/footage.mp4")


if __name__ == "__main__":
    main()
