#!/usr/bin/env python3
"""Mach cone: where is the jet when you hear it?

Three jets fly at half, once and twice the speed of sound along three
parallel paths. Each jet has been sending out a ring of sound every tenth
of a second since before the video starts; every ring is an exact circle
that grows at the speed of sound around the point where it was emitted.
A listener stands a fixed distance to the side of each path. The jets are
placed so that all three pass the listener at the same moment.

Measured and printed, per jet: when the first sound reaches the listener
and where the jet is at that moment, both for the continuous wavefront
(the earliest arrival over all emission times, found by scanning the
emission time finely) and for the drawn rings; the cone half angle fitted
to the drawn rings of the supersonic jet against the exact asin(c / v);
the spread of the ring fronts at the speed of sound (a wall); and how far
the rings lead the subsonic jet. Exact geometry, no time step to check,
no seed.

usage: machcone.py [--measure-only] [--frames t1,t2,...]
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
WHITE = (236, 240, 244)

# Layout: three panels stacked between the overlay and the captions
# (caption_y 0.75, y 1440..1510), the clock where the title was, payoff
# under the captions.
PANEL_TOPS = (290, 661, 1032)
PANEL_H = 370
PATH_DY = 120
SRC_X = 680
CLOCK_Y = 200
PAYOFF_Y = 1592.0
RING_MAX_AGE = 3.3


class Jet:
    def __init__(self, mach: float, c: float, x0: float):
        self.mach = mach
        self.v = mach * c
        self.x0 = x0  # position at t = 0, the listener is at x = 0

    def x(self, t: float) -> float:
        return self.x0 + self.v * t


def first_arrival(jet: Jet, c: float, side: float, t_emit0: float, t_end: float, step: float) -> tuple[float, float]:
    """Earliest time any sound emitted from t_emit0 on reaches the listener, and the jet's x then."""
    te = np.arange(t_emit0, t_end, step)
    xe = jet.x0 + jet.v * te
    arrive = te + np.hypot(xe, side) / c
    i = int(np.argmin(arrive))
    return float(arrive[i]), float(jet.x(arrive[i]))


def ring_arrival(jet: Jet, c: float, side: float, t_emit0: float, every: float, t_end: float) -> tuple[float, float, float]:
    """Earliest arrival over the drawn rings (emitted every `every` seconds from t_emit0)."""
    best = (math.inf, 0.0, 0.0)
    k = 0
    while True:
        te = t_emit0 + k * every
        if te > t_end:
            break
        arrive = te + math.hypot(jet.x0 + jet.v * te, side) / c
        if arrive < best[0]:
            best = (arrive, jet.x(arrive), te)
        k += 1
    return best


def cone_fit(jet: Jet, c: float, t: float, t_emit0: float, every: float) -> float:
    """Half angle of the envelope of the drawn rings behind the jet, fitted from their union."""
    xs = jet.x(t)
    rings = []
    k = 0
    while True:
        te = t_emit0 + k * every
        if te > t:
            break
        rings.append((jet.x0 + jet.v * te, c * (t - te)))
        k += 1
    sample_x = np.linspace(xs - 400.0, xs - 40.0, 361)
    env = np.zeros_like(sample_x)
    for cx, r in rings:
        dx = sample_x - cx
        inside = np.abs(dx) < r
        env[inside] = np.maximum(env[inside], np.sqrt(r * r - dx[inside] ** 2))
    dist = xs - sample_x
    # The envelope is scalloped between rings; its upper convex hull runs
    # through the points where each ring touches the cone, so fit those.
    pts = sorted(zip(dist.tolist(), env.tolist()))
    hull: list[tuple[float, float]] = []
    for p in pts:
        while len(hull) >= 2:
            (x1, y1), (x2, y2) = hull[-2], hull[-1]
            if (x2 - x1) * (p[1] - y1) - (y2 - y1) * (p[0] - x1) >= 0:
                hull.pop()
            else:
                break
        hull.append(p)
    hx = np.array([p[0] for p in hull[1:-1]])
    hy = np.array([p[1] for p in hull[1:-1]])
    slope = np.polyfit(hx, hy, 1)[0]
    return math.degrees(math.atan(slope))


def measure(man: dict) -> dict:
    c = man["sound_speed_m_per_s"]
    side = man["listener_side_m"]
    every = man["ring_every_s"]
    t_emit0 = -man["pre_roll_s"]
    t_abeam = man["abeam_t"]
    t_end = man["scene_duration"] / man["slow_motion"]
    jets = [Jet(m, c, -m * c * t_abeam) for m in man["machs"]]
    print(f"setup: three jets at Mach {', '.join(f'{m:g}' for m in man['machs'])} (speed of sound {c:g} m/s), "
          f"each sending out a ring of sound every {every:g} s since {-t_emit0:g} s before the video starts; "
          f"a listener {side:g} m to the side of each path; the jets start "
          f"{', '.join(f'{-j.x0:,.1f}' for j in jets)} m before the listener so all three pass it at "
          f"{t_abeam:g} s; the run covers {t_end:.3f} s at 1/{man['slow_motion']:g} speed; exact circles, "
          f"no time step, no seed")
    results = []
    for j in jets:
        t_cont, x_cont = first_arrival(j, c, side, t_emit0, t_end + 2.0, 1e-4)
        t_ring, x_ring, te_ring = ring_arrival(j, c, side, t_emit0, every, t_end + 2.0)
        where = f"{abs(x_cont):.1f} m {'past' if x_cont > 0 else 'before'} the listener"
        print(f"Mach {j.mach:g} ({j.v:g} m/s): the first sound reaches the listener at {t_cont:.4f} s, "
              f"{t_cont - t_abeam:+.4f} s from the jet passing abeam, when the jet is {where}; "
              f"the first drawn ring (sent at {te_ring:.1f} s) arrives at {t_ring:.4f} s with the jet "
              f"{abs(x_ring):.1f} m {'past' if x_ring > 0 else 'before'}")
        results.append({"t_first": t_cont, "x_first": x_cont, "t_ring": t_ring, "x_ring": x_ring})
    # Supersonic cone: fitted from the drawn rings at the end of the run, and exact.
    sup = jets[-1]
    fitted = cone_fit(sup, c, t_end, t_emit0, every)
    exact = math.degrees(math.asin(c / sup.v))
    past_exact = side / math.tan(math.radians(exact))
    print(f"cone at Mach {sup.mach:g}: half angle fitted to the union of the drawn rings behind the jet at "
          f"{t_end:.3f} s: {fitted:.2f} degrees; exact asin(c / v) = {exact:.3f} degrees; a listener {side:g} m "
          f"to the side is first reached when the jet is {side:g} / tan({exact:.1f} deg) = {past_exact:.1f} m past")
    far = man["check_listener_side_m"]
    t_far, x_far = first_arrival(sup, c, far, t_emit0 - 20.0, t_end + 20.0, 1e-3)
    print(f"check, listener {far:g} m to the side at Mach {sup.mach:g}: first sound at {t_far:.3f} s, the jet "
          f"{x_far:.0f} m past (closed form {far / math.tan(math.radians(exact)):.0f} m)")
    # At the speed of sound every ring's front edge sits on the nose.
    son = jets[1]
    fronts = []
    k = 0
    while True:
        te = t_emit0 + k * every
        if te > t_end:
            break
        fronts.append((son.x0 + son.v * te) + c * (t_end - te) - son.x(t_end))
        k += 1
    print(f"wall at Mach {son.mach:g}: at {t_end:.3f} s the front edges of all {len(fronts)} rings are within "
          f"{max(abs(f) for f in fronts):.6f} m of the jet's nose")
    sub = jets[0]
    lead = (sub.x0 + sub.v * t_emit0) + c * (t_end - t_emit0) - sub.x(t_end)
    print(f"lead at Mach {sub.mach:g}: at {t_end:.3f} s the oldest ring's front is {lead:.1f} m ahead of the jet, "
          f"and every ring leads it by ({c:g} - {sub.v:g}) m per second of age")
    return {"jets": jets, "results": results, "fitted": fitted, "exact": exact, "past": results[-1]["x_first"],
            "t_end": t_end}


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
        self.font_watch = ImageFont.truetype(font, 64)
        self.font_tag = ImageFont.truetype(font, 28)
        self.first = None
        self.c = man["sound_speed_m_per_s"]
        self.mpp = man["m_per_px"]
        self.slow = man["slow_motion"]
        self.labels = ["half the speed of sound", "the speed of sound", "twice the speed of sound"]
        widths = {"overlay@34": (ImageFont.truetype(font, 34), man["overlay"])}
        for j, line in enumerate(man["title"].split("|")):
            widths[f"title line {j + 1}@56"] = (self.font_title, line)
        for j, label in enumerate(self.labels):
            widths[f"label {j + 1}@32"] = (self.font_small, label)
        widths["tag@28"] = (self.font_tag, "hears it: jet 173 m past")
        widths["watch@64"] = (self.font_watch, "2.667 s")
        widths["watch label@32"] = (self.font_small, f"1/{self.slow:g} speed")
        for j, line in enumerate(self.payoff_lines()):
            widths[f"payoff line {j + 1}@40"] = (self.font, line)
        print("text widths: " + ", ".join(f"{k} {f.getlength(s):.0f} px" for k, (f, s) in widths.items()))
        ev = ", ".join(f"Mach {j.mach:g} at {r['t_first'] * self.slow:.2f} s" for j, r in zip(meas["jets"], meas["results"]))
        print(f"video: 1/{self.slow:g} speed, the jets pass the listener at {man['abeam_t'] * self.slow:.2f} s of "
              f"video; the listener hears: {ev}; payoff card at {man['payoff_t']:g} s")

    def payoff_lines(self) -> list[str]:
        text = self.man["payoff_text"].format(past=self.meas["past"])
        return [s.strip() for s in text.split("|")]

    def draw_panel(self, k: int, t: float) -> Image.Image:
        """One jet's panel at real time t, in its own image (clipped)."""
        man, meas = self.man, self.meas
        jet = meas["jets"][k]
        res = meas["results"][k]
        img = Image.new("RGB", (W, PANEL_H), BG)
        d = ImageDraw.Draw(img)
        py = PATH_DY
        mpp = self.mpp
        # Flight path, faint.
        d.line([(0, py), (W, py)], fill=(30, 36, 44), width=2)
        # Rings, oldest first so fresh rings draw on top.
        te0 = -man["pre_roll_s"]
        every = man["ring_every_s"]
        n = int(math.floor((t - te0) / every)) + 1
        for i in range(n):
            te = te0 + i * every
            age = t - te
            if age < 0 or age > RING_MAX_AGE:
                continue
            r = self.c * age / mpp
            cx = SRC_X - jet.v * age / mpp
            a = 0.12 + 0.88 * (1.0 - age / RING_MAX_AGE) ** 1.6
            col = tuple(int(TEAL[q] * a + BG[q] * (1 - a)) for q in range(3))
            d.ellipse((cx - r, py - r, cx + r, py + r), outline=col, width=3)
        # The cone of the supersonic jet: the envelope, exact asin(c / v).
        if jet.v > self.c:
            th = math.asin(self.c / jet.v)
            L = 900.0
            colc = tuple(int(GOLD[q] * 0.55 + BG[q] * 0.45) for q in range(3))
            for sgn in (-1, 1):
                d.line([(SRC_X, py), (SRC_X - L * math.cos(th), py + sgn * L * math.sin(th))], fill=colc, width=2)
            deg = math.degrees(th)
            d.arc((SRC_X - 90, py - 90, SRC_X + 90, py + 90), start=180 - deg, end=180, fill=colc, width=2)
            d.text((SRC_X - 132, py + 40), f"{deg:.0f}°", font=self.font_tag, fill=GOLD, anchor="mm")
        # The jet: a small arrowhead pointing right.
        d.polygon([(SRC_X + 26, py), (SRC_X - 18, py - 12), (SRC_X - 8, py), (SRC_X - 18, py + 12)], fill=WHITE)
        # The listener.
        lx = SRC_X - jet.x(t) / mpp
        ly = py + man["listener_side_m"] / mpp
        heard = t >= res["t_first"]
        if -80 <= lx <= W + 80:
            if heard:
                since = (t - res["t_first"]) * self.slow
                if since < 0.5:
                    rr = 14 + 70 * since / 0.5
                    a = 1.0 - since / 0.5
                    colb = tuple(int(GOLD[q] * a + BG[q] * (1 - a)) for q in range(3))
                    d.ellipse((lx - rr, ly - rr, lx + rr, ly + rr), outline=colb, width=3)
                d.ellipse((lx - 12, ly - 12, lx + 12, ly + 12), fill=GOLD)
                xj = jet.x(t) if False else res["x_first"]
                tag = f"hears it: jet {abs(xj):.0f} m {'past' if xj > 0 else 'away'}"
                colt = GOLD
            else:
                d.ellipse((lx - 9, ly - 9, lx + 9, ly + 9), fill=MUTED)
                tag = "you"
                colt = MUTED
            tw = self.font_tag.getlength(tag)
            tx = min(max(lx, tw / 2 + 16), W - tw / 2 - 16)
            d.text((tx, ly + 34), tag, font=self.font_tag, fill=colt, anchor="mm")
        d.text((36, 30), self.labels[k], font=self.font_small, fill=TEXT, anchor="lm")
        return img

    def draw_scene(self, t_video: float, title_on: bool) -> Image.Image:
        man = self.man
        t = t_video / self.slow
        img = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(img)
        for k, top in enumerate(PANEL_TOPS):
            img.paste(self.draw_panel(k, t), (0, top))
            if k > 0:
                d.line([(0, top - 1), (W, top - 1)], fill=WIRE, width=1)
        d.line([(0, PANEL_TOPS[-1] + PANEL_H), (W, PANEL_TOPS[-1] + PANEL_H)], fill=WIRE, width=1)
        if not title_on:
            d.text((W / 2, CLOCK_Y), f"{t:.3f} s", font=self.font_watch, fill=TEXT, anchor="mm")
            d.text((W / 2, CLOCK_Y + 50), f"1/{self.slow:g} speed", font=self.font_small, fill=MUTED, anchor="mm")
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
    man = json.loads((ROOT / "projects/machcone/manifest.json").read_text())
    meas = measure(man)
    if "--measure-only" in sys.argv:
        return
    if "--frames" in sys.argv:
        times = [float(v) for v in sys.argv[sys.argv.index("--frames") + 1].split(",")]
        r = Renderer(man, meas)
        for tv in times:
            Image.fromarray(r.frame_at(int(round(tv * man["fps"])))).save(ROOT / f"media/machcone/smoke-{tv}.png")
        print("smoke frames: " + ", ".join(f"{tv}" for tv in times))
        return
    Renderer(man, meas).render(ROOT / "media/machcone/footage.mp4")


if __name__ == "__main__":
    main()
