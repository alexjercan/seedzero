#!/usr/bin/env python3
"""Rainbow angle: why is every rainbow the same size?

Parallel rays of one colour enter a round water drop at evenly spaced
heights from the centre to the top edge. Each ray bends going in (Snell),
bounces once off the back of the drop, and bends again coming out. The
exit direction is measured from the antisolar direction (straight back
toward the sun). The rays' exit angles pile up at one angle and none
leaves past it; that angle is the rainbow. Red (n = 1.331) is traced
first, then violet (n = 1.343). Exact geometry with vector Snell and
reflection, no time step, no seed.

Measured and printed, per colour: the largest exit angle over the rays
and the closed form 4 asin(sin i0 / n) - 2 i0 with cos^2 i0 = (n^2 - 1)
/ 3, the ray height where it happens, how many rays leave within one
degree and within a tenth of a degree of it, how many leave past it, the
exit angle of the centre ray and the edge ray, the tallest histogram bin,
the two-bounce pile (the secondary bow) and the count of rays of either
kind between the two piles (the dark band).

usage: rainbow.py [--measure-only] [--frames t1,t2,...]
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
DROP_FILL = (16, 22, 30)
RED = (242, 92, 70)
VIOLET = (150, 110, 245)
WHITE = (236, 240, 244)
COLOURS = {"red": RED, "violet": VIOLET}

# Layout: overlay at y 96 (captions.py), the readout at y 236 where the
# title sits for the first seconds, the drop in the upper middle, the ray
# haze faded out between FADE_Y0 and FADE_Y1, the histogram box under the
# fade and above the caption band (caption_y 0.75, y 1440..1510), the
# payoff under the captions.
READ_Y = 236
FADE_Y0, FADE_Y1 = 990, 1110
CHART_X0, CHART_X1 = 340, 1040
CHART_TOP, CHART_BASE = 1176, 1380
CHART_LABEL_Y = 1146
PAYOFF_Y = 1592.0


def refract(d: np.ndarray, n_out: np.ndarray, eta: float) -> np.ndarray:
    """Vector Snell. n_out points toward the side the ray comes from."""
    c1 = -float(np.dot(n_out, d))
    c2 = math.sqrt(1.0 - eta * eta * (1.0 - c1 * c1))
    return eta * d + (eta * c1 - c2) * n_out


def trace(b: float, n: float, bounces: int = 1) -> dict:
    """One ray at height b (drop radius 1, centre at the origin) of index n."""
    d = np.array([1.0, 0.0])
    p = np.array([-math.sqrt(1.0 - b * b), b])
    pts = [p]
    d = refract(d, p, 1.0 / n)  # into the drop: normal p points outward
    for _ in range(bounces):
        p = p + (-2.0 * float(np.dot(p, d))) * d  # next point on the circle
        pts.append(p)
        d = d - 2.0 * float(np.dot(d, p)) * p  # reflect off the inside
    p = p + (-2.0 * float(np.dot(p, d))) * d
    pts.append(p)
    e = refract(d, -p, n)  # out of the drop: normal -p points inward
    theta = math.degrees(math.acos(max(-1.0, min(1.0, -e[0]))))  # from the antisolar direction
    i = math.degrees(math.asin(b))
    r = math.degrees(math.asin(b / n))
    return {"pts": pts, "e": e, "theta": theta, "i": i, "r": r}


def rainbow_closed_form(n: float, bounces: int = 1) -> tuple[float, float]:
    """Angle from the antisolar direction of the k-bounce bow and the incidence angle."""
    k = bounces
    cos2 = (n * n - 1.0) / (k * k + 2.0 * k)
    i0 = math.acos(math.sqrt(cos2))
    r0 = math.asin(math.sin(i0) / n)
    dev = 2.0 * i0 - 2.0 * (k + 1) * r0 + k * math.pi  # total turning
    theta = abs(math.pi - (dev % (2.0 * math.pi)))
    return math.degrees(theta), math.degrees(i0)


def measure(man: dict) -> dict:
    n_rays = man["n_rays"]
    bs = (np.arange(n_rays) + 0.5) / n_rays
    binw = man["hist_bin_deg"]
    nbins = int(round(man["hist_max_deg"] / binw))
    print(f"setup: {n_rays:,} parallel rays of each colour enter one round drop at evenly spaced heights "
          f"from the centre to the top edge (b = (k + 1/2) / {n_rays:,} drop radii), bend in, bounce once "
          f"off the back and bend out; exit angle measured from the antisolar direction; "
          f"red n = {man['colours']['red']}, violet n = {man['colours']['violet']}; exact geometry, no seed")
    out: dict = {"bs": bs, "colours": {}}
    for name, n in man["colours"].items():
        rays = [trace(float(b), n) for b in bs]
        theta = np.array([r["theta"] for r in rays])
        k_peak = int(np.argmax(theta))
        peak = float(theta[k_peak])
        closed, i0 = rainbow_closed_form(n)
        near1 = int(np.sum(theta >= peak - 1.0))
        near01 = int(np.sum(theta >= peak - 0.1))
        past = int(np.sum(theta > closed))
        hist, _ = np.histogram(theta, bins=nbins, range=(0.0, man["hist_max_deg"]))
        top = int(np.argmax(hist))
        two = np.array([trace(float(b), n, bounces=2)["theta"] for b in bs])
        two_peak = float(two.min())
        band = int(np.sum((theta > peak) & (theta < two_peak))) + int(np.sum((two > peak) & (two < two_peak)))
        print(f"{name} (n = {n}): the exit angles pile up at {peak:.2f} degrees (closed form {closed:.3f}, incidence "
              f"{i0:.2f} degrees), reached by ray {k_peak + 1:,} at height {bs[k_peak]:.4f} of the radius; "
              f"{near1:,} of {n_rays:,} rays leave within one degree of it and {near01:,} within a tenth of a "
              f"degree; {past} rays leave past {closed:.3f} degrees; the centre ray leaves at {theta[0]:.2f} "
              f"degrees and the edge ray at {theta[-1]:.2f}; tallest {binw:g}-degree bin {top * binw:.1f} to "
              f"{(top + 1) * binw:.1f} degrees holds {int(hist[top]):,} rays")
        print(f"{name} two bounces: the exit angles pile up at {two_peak:.2f} degrees (closed form "
              f"{rainbow_closed_form(n, 2)[0]:.3f}); {band} rays of either kind leave between {peak:.2f} and "
              f"{two_peak:.2f} degrees, the dark band")
        # Check the vector trace against the angle formula on the peak ray.
        rk = rays[k_peak]
        formula = 4.0 * rk["r"] - 2.0 * rk["i"]
        assert abs(formula - rk["theta"]) < 1e-9, (formula, rk["theta"])
        out["colours"][name] = {"n": n, "rays": rays, "theta": theta, "peak": peak, "closed": closed,
                                "k_peak": k_peak, "hist": hist, "near1": near1, "two_peak": two_peak}
    reds, vios = out["colours"]["red"], out["colours"]["violet"]
    print(f"band: red piles at {reds['peak']:.2f} degrees and violet at {vios['peak']:.2f}, "
          f"{reds['peak'] - vios['peak']:.2f} degrees apart; the histogram scale is the tallest bin, "
          f"{max(int(reds['hist'].max()), int(vios['hist'].max())):,} rays")
    return out


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
        self.font_tag = ImageFont.truetype(font, 28)
        self.first = None
        self.cx, self.cy = man["drop_centre_px"]
        self.R = man["drop_radius_px"]
        self.n_rays = man["n_rays"]
        self.acc = {name: np.zeros((H, W), dtype=np.float32) for name in man["colours"]}
        self.done = {name: 0 for name in man["colours"]}
        self.polys = {name: [self.polyline(r) for r in meas["colours"][name]["rays"]] for name in man["colours"]}
        self.hist_scale = max(int(meas["colours"][c]["hist"].max()) for c in man["colours"])
        ys = np.arange(H, dtype=np.float32)
        self.fade = np.clip((FADE_Y1 - ys) / (FADE_Y1 - FADE_Y0), 0.0, 1.0)[:, None]
        widths = {"overlay@34": (ImageFont.truetype(font, 34), man["overlay"])}
        for j, line in enumerate(man["title"].split("|")):
            widths[f"title line {j + 1}@56"] = (self.font_title, line)
        widths["readout@40"] = (self.font, "ray 10,000 of 10,000   exit angle 40.7°")
        widths["readout 2@40"] = (self.font, "red: 1,196 of 10,000 rays within 1° of 42.4°")
        widths["chart label@28"] = (self.font_tag, "rays by exit angle")
        widths["sun label@32"] = (self.font_small, "sunlight")
        for j, line in enumerate(self.payoff_lines()):
            widths[f"payoff line {j + 1}@40"] = (self.font, line)
        print("text widths: " + ", ".join(f"{k} {f.getlength(s):.0f} px" for k, (f, s) in widths.items()))
        red = meas["colours"]["red"]
        a, b = man["red_sweep"]
        t_peak = a + (b - a) * (red["k_peak"] + 0.5) / self.n_rays
        print(f"video: red rays sweep {a:g} to {b:g} s and reach the pile at {t_peak:.2f} s; violet rays sweep "
              f"{man['violet_sweep'][0]:g} to {man['violet_sweep'][1]:g} s; payoff card at {man['payoff_t']:g} s")

    def payoff_lines(self) -> list[str]:
        c = self.meas["colours"]
        text = self.man["payoff_text"].format(red=c["red"]["peak"], violet=c["violet"]["peak"])
        return [s.strip() for s in text.split("|")]

    def to_px(self, p: np.ndarray) -> tuple[float, float]:
        return self.cx + p[0] * self.R, self.cy - p[1] * self.R

    def polyline(self, ray: dict) -> list[tuple[float, float]]:
        pts = [self.to_px(p) for p in ray["pts"]]
        start = (0.0, pts[0][1])
        ex, ey = ray["e"]
        far = 3000.0
        end = (pts[-1][0] + ex * far, pts[-1][1] - ey * far)
        return [start, *pts, end]

    def splat(self, acc: np.ndarray, poly: list[tuple[float, float]]) -> None:
        xs, ys = [], []
        for (x0, y0), (x1, y1) in zip(poly[:-1], poly[1:]):
            length = math.hypot(x1 - x0, y1 - y0)
            m = max(2, int(math.ceil(length)))
            u = np.arange(m) / m
            xs.append(x0 + (x1 - x0) * u)
            ys.append(y0 + (y1 - y0) * u)
        x = np.concatenate(xs)
        y = np.concatenate(ys)
        keep = (x >= 0) & (x < W - 1) & (y >= 0) & (y < H - 1)
        x, y = x[keep], y[keep]
        ix, iy = np.floor(x).astype(int), np.floor(y).astype(int)
        fx, fy = (x - ix).astype(np.float32), (y - iy).astype(np.float32)
        np.add.at(acc, (iy, ix), (1 - fx) * (1 - fy))
        np.add.at(acc, (iy, ix + 1), fx * (1 - fy))
        np.add.at(acc, (iy + 1, ix), (1 - fx) * fy)
        np.add.at(acc, (iy + 1, ix + 1), fx * fy)

    def count_at(self, name: str, t: float) -> int:
        a, b = self.man[f"{name}_sweep"]
        if t < a:
            return 0
        return min(self.n_rays, int(math.floor(self.n_rays * (t - a) / (b - a))) + 1)

    def advance(self, name: str, k: int) -> None:
        if k < self.done[name]:
            self.acc[name][:] = 0.0
            self.done[name] = 0
        for j in range(self.done[name], k):
            self.splat(self.acc[name], self.polys[name][j])
        self.done[name] = k

    def haze(self) -> Image.Image:
        base = np.empty((H, W, 3), dtype=np.float32)
        base[:] = BG
        total = np.zeros((H, W), dtype=np.float32)
        for name, acc in self.acc.items():
            v = (1.0 - np.exp(-acc / 90.0)) * self.fade
            col = np.array(COLOURS[name], dtype=np.float32)
            base += v[:, :, None] * (col - np.array(BG, dtype=np.float32)) * 0.95
            total += acc
        w = np.clip(total / 520.0, 0.0, 1.0) ** 2 * self.fade
        base += w[:, :, None] * (np.array(WHITE, dtype=np.float32) - base) * 0.7
        return Image.fromarray(np.clip(base, 0, 255).astype(np.uint8))

    def draw_chart(self, img: Image.Image, counts: dict[str, int]) -> None:
        man = self.man
        binw = man["hist_bin_deg"]
        nbins = int(round(man["hist_max_deg"] / binw))
        px_per_deg = (CHART_X1 - CHART_X0) / man["hist_max_deg"]
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        for name in man["colours"]:
            k = counts[name]
            if k == 0:
                continue
            theta = self.meas["colours"][name]["theta"][:k]
            hist, _ = np.histogram(theta, bins=nbins, range=(0.0, man["hist_max_deg"]))
            col = COLOURS[name] + (200,)
            for j, c in enumerate(hist):
                if c == 0:
                    continue
                hgt = (CHART_BASE - CHART_TOP) * c / self.hist_scale
                x0 = CHART_X0 + j * binw * px_per_deg
                d.rectangle((x0, CHART_BASE - hgt, x0 + binw * px_per_deg - 1, CHART_BASE), fill=col)
        img.paste(Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB"))
        d = ImageDraw.Draw(img)
        d.line([(CHART_X0, CHART_BASE), (CHART_X1, CHART_BASE)], fill=WIRE, width=2)
        for deg in range(0, int(man["hist_max_deg"]) + 1, 10):
            x = CHART_X0 + deg * px_per_deg
            d.line([(x, CHART_BASE), (x, CHART_BASE + 10)], fill=WIRE, width=2)
            d.text((x, CHART_BASE + 30), f"{deg}°", font=self.font_tag, fill=MUTED, anchor="mm")
        d.text((CHART_X0, CHART_LABEL_Y), "rays by exit angle", font=self.font_tag, fill=MUTED, anchor="lm")
        for name, side in (("red", 1), ("violet", -1)):
            c = self.meas["colours"][name]
            if counts[name] > c["k_peak"]:
                x = CHART_X0 + c["peak"] * px_per_deg
                d.line([(x, CHART_TOP - 8), (x, CHART_BASE)], fill=COLOURS[name], width=2)
                d.text((x + side * 12, CHART_LABEL_Y), f"{c['peak']:.1f}°", font=self.font_small,
                       fill=COLOURS[name], anchor="lm" if side > 0 else "rm")

    def draw_scene(self, t: float, title_on: bool) -> Image.Image:
        man = self.man
        counts = {name: self.count_at(name, t) for name in man["colours"]}
        for name, k in counts.items():
            self.advance(name, k)
        img = self.haze()
        d = ImageDraw.Draw(img)
        # The drop outline over the haze.
        cx, cy, R = self.cx, self.cy, self.R
        d.ellipse((cx - R, cy - R, cx + R, cy + R), outline=WIRE, width=3)
        # The sun side.
        d.text((60, cy - R - 40), "sunlight", font=self.font_small, fill=MUTED, anchor="lm")
        d.line([(60, cy - R - 10), (150, cy - R - 10)], fill=MUTED, width=2)
        d.polygon([(150, cy - R - 10), (136, cy - R - 18), (136, cy - R - 2)], fill=MUTED)
        # The current ray, bright, with dots at the bends.
        current = None
        for name in man["colours"]:
            k = counts[name]
            a, b = man[f"{name}_sweep"]
            if 0 < k and t <= b + 0.5:
                current = (name, k)
        if current is not None:
            name, k = current
            j = min(k, self.n_rays) - 1
            poly = self.polys[name][j]
            ray = self.meas["colours"][name]["rays"][j]
            col = COLOURS[name]
            pts = [(min(max(x, -50), W + 50), min(max(y, -50), H + 50)) for x, y in poly]
            (x0, y0), (x1, y1) = pts[-2], pts[-1]
            if y1 > FADE_Y1 > y0:  # the highlighted ray ends where the haze fades out
                u = (FADE_Y1 - y0) / (y1 - y0)
                pts[-1] = (x0 + (x1 - x0) * u, FADE_Y1)
            d.line(pts, fill=WHITE, width=3)
            for p in ray["pts"]:
                x, y = self.to_px(p)
                d.ellipse((x - 7, y - 7, x + 7, y + 7), fill=col)
            if not title_on:
                d.text((W / 2, READ_Y), f"ray {j + 1:,} of {self.n_rays:,}   exit angle {ray['theta']:.1f}°",
                       font=self.font, fill=col, anchor="mm")
        elif not title_on:
            reds, vios = self.meas["colours"]["red"], self.meas["colours"]["violet"]
            if counts["violet"] >= self.n_rays:
                d.text((W / 2, READ_Y), f"red piles at {reds['peak']:.1f}°   violet at {vios['peak']:.1f}°",
                       font=self.font, fill=TEXT, anchor="mm")
            elif counts["red"] >= self.n_rays:
                d.text((W / 2, READ_Y), f"red: {reds['near1']:,} of {self.n_rays:,} rays within 1° of {reds['peak']:.1f}°",
                       font=self.font, fill=RED, anchor="mm")
        self.draw_chart(img, counts)
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
                saved = ({k: v.copy() for k, v in self.acc.items()}, dict(self.done))
                self.first = self.live_frame(0)
                self.acc, self.done = saved
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
    man = json.loads((ROOT / "projects/rainbow/manifest.json").read_text())
    meas = measure(man)
    if "--measure-only" in sys.argv:
        return
    if "--frames" in sys.argv:
        times = [float(v) for v in sys.argv[sys.argv.index("--frames") + 1].split(",")]
        r = Renderer(man, meas)
        for tv in times:
            Image.fromarray(r.frame_at(int(round(tv * man["fps"])))).save(ROOT / f"media/rainbow/smoke-{tv}.png")
        print("smoke frames: " + ", ".join(f"{tv}" for tv in times))
        return
    Renderer(man, meas).render(ROOT / "media/rainbow/footage.mp4")


if __name__ == "__main__":
    main()
