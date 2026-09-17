#!/usr/bin/env python3
"""Rolling race: which shape rolls down first?

Four rigid bodies of the same mass and the same radius, a solid ball, a
solid cylinder, a hollow ball (thin shell) and a hoop (thin ring), are
released from rest at the top of the same ramp and roll without slipping.
Each has moment of inertia I = k m r^2, so the ramp pushes it down the
slope with a = m g sin(theta) / (m + I / r^2) = g sin(theta) / (1 + k).
Each body is integrated with RK4 at a fixed step and its arrival at the
bottom is interpolated inside the step that crosses the finish. The race is
played at quarter speed and repeats every race_period seconds of video,
so the video loops on the race. Deterministic, no seed.

Measured and printed: each arrival time against the closed form
sqrt(2 L (1 + k) / (g sin theta)), the speed at the bottom, the finishing
order, the gap between the winner and the hoop in seconds and percent,
the same race with ten times the mass and twice the radius, the friction
coefficient each shape needs to roll without slipping, a half-step check,
the time a frictionless block would take to slide the same ramp, and the
on-screen text widths.

usage: rollrace.py [--measure-only] [--frames t1,t2,...]
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
VIOLET = (168, 150, 236)
LANE = (17, 21, 27)

COLOURS = {"solid ball": CORAL, "solid cylinder": GOLD, "hollow ball": TEAL, "hoop": VIOLET}
LABELS = {"solid ball": ("solid", "ball"), "solid cylinder": ("solid", "cylinder"),
          "hollow ball": ("hollow", "ball"), "hoop": ("", "hoop")}
PLACES = ("1st", "2nd", "3rd", "4th")

# Layout: overlay at y 96..130 (captions.py), title at y 190/252/314 for
# the first seconds, then the race counter at y 236 and the ramp tag at
# y 290; lane labels at y 380/416, the lane clocks at y 470, the place
# tags at y 516, the objects rolling from start_y_px down to the finish
# line, captions at caption_y 0.75 (y 1440..1510), payoff under them.
# Each race: the run, a hold with the clocks frozen, a reset to the top,
# then ready_dur at rest so the loop crossfade meets objects at rest.
COUNTER_Y, TAG_Y = 236, 290
LABEL_Y = (380, 416)
CLOCK_Y, PLACE_Y = 470, 516
PAYOFF_Y = 1592.0


def rk4(state: np.ndarray, dt: float, deriv) -> np.ndarray:
    k1 = deriv(state)
    k2 = deriv(state + 0.5 * dt * k1)
    k3 = deriv(state + 0.5 * dt * k2)
    k4 = deriv(state + dt * k3)
    return state + dt / 6.0 * (k1 + 2 * k2 + 2 * k3 + k4)


def roll(L: float, g: float, theta: float, m: float, r: float, k: float, dt: float) -> dict:
    """A body of mass m, radius r and I = k m r^2 rolling without slipping
    from rest down a slope theta. RK4 on [s, v] along the slope; the
    arrival at s = L is interpolated inside the crossing step."""
    inertia = k * m * r * r
    a = m * g * math.sin(theta) / (m + inertia / (r * r))

    def deriv(st: np.ndarray) -> np.ndarray:
        return np.array([st[1], a])

    st = np.array([0.0, 0.0])
    ts, ss, vs = [0.0], [0.0], [0.0]
    t = 0.0
    t_arr = v_arr = float("nan")
    while True:
        nxt = rk4(st, dt, deriv)
        t += dt
        ts.append(t)
        ss.append(nxt[0])
        vs.append(nxt[1])
        if nxt[0] >= L:
            frac = (L - st[0]) / (nxt[0] - st[0])
            t_arr = t - dt + frac * dt
            v_arr = st[1] + frac * (nxt[1] - st[1])
            break
        st = nxt
    # The friction force that keeps it rolling is m a k, against a normal force m g cos theta.
    mu_min = k / (1.0 + k) * math.tan(theta)
    return {"t": np.array(ts), "s": np.array(ss), "v": np.array(vs), "t_arrive": t_arr, "v_arrive": v_arr,
            "a": a, "mu_min": mu_min, "k": k}


def closed_form(L: float, g: float, theta: float, k: float) -> float:
    return math.sqrt(2.0 * L * (1.0 + k) / (g * math.sin(theta)))


def measure(man: dict) -> dict:
    g, L = man["g"], man["ramp_length_m"]
    th = math.radians(man["ramp_angle_deg"])
    m, r = man["mass_kg"], man["radius_m"]
    dt = 1.0 / man["steps_per_second"]
    names = [sh["name"] for sh in man["shapes"]]
    print(f"setup: a ramp {L:g} m long at {man['ramp_angle_deg']:g} degrees (g = {g}, g sin theta = "
          f"{g * math.sin(th):.4f} m/s^2, friction coefficient {man['ramp_friction']:g}); four bodies of mass "
          f"{m:g} kg and radius {r * 100:g} cm released from rest at the top and rolling without slipping: "
          + ", ".join(f"{sh['name']} (I = {sh['k']:.4g} m r^2)" for sh in man["shapes"])
          + f"; RK4 at {man['steps_per_second']} steps per second (dt = {dt:.1e} s); deterministic, no seed")
    runs = []
    for sh in man["shapes"]:
        run = roll(L, g, th, m, r, sh["k"], dt)
        run["name"] = sh["name"]
        run["closed"] = closed_form(L, g, th, sh["k"])
        runs.append(run)
        print(f"{sh['name']}: accelerates at {run['a']:.4f} m/s^2, arrives at {run['t_arrive']:.4f} s "
              f"(closed form sqrt(2 L (1 + k) / (g sin theta)) = {run['closed']:.4f} s), speed at the bottom "
              f"{run['v_arrive']:.4f} m/s, needs friction coefficient >= {run['mu_min']:.4f} to roll without slipping")
    order = sorted(runs, key=lambda q: q["t_arrive"])
    for place, q in enumerate(order):
        q["place"] = place
    print("finishing order: " + ", ".join(f"{place + 1}. {q['name']} {q['t_arrive']:.4f} s" for place, q in enumerate(order)))
    ball = next(q for q in runs if q["name"] == "solid ball")
    hoop = next(q for q in runs if q["name"] == "hoop")
    gap = hoop["t_arrive"] - ball["t_arrive"]
    print(f"gap: the hoop arrives {gap:.4f} s after the solid ball, {100.0 * gap / ball['t_arrive']:.1f}% behind "
          f"(closed-form ratio sqrt((1 + 1) / (1 + 2/5)) = {math.sqrt(2.0 / 1.4):.4f}); at the finish the solid ball "
          f"moves at {ball['v_arrive']:.3f} m/s and the hoop at {hoop['v_arrive']:.3f} m/s; the ball's lead at the "
          f"moment it finishes is {L - float(np.interp(ball['t_arrive'], hoop['t'], hoop['s'])):.3f} m")
    mf, rf = man["check_mass_factor"], man["check_radius_factor"]
    heavy = [roll(L, g, th, m * mf, r * rf, sh["k"], dt) for sh in man["shapes"]]
    print(f"check: with {mf:g}x the mass ({m * mf:g} kg) and {rf:g}x the radius ({r * rf * 100:g} cm) the arrival "
          f"times are " + ", ".join(f"{n} {q['t_arrive']:.4f} s" for n, q in zip(names, heavy))
          + "; identical, the mass and the radius cancel")
    print(f"friction: rolling without slipping needs mu >= k / (1 + k) tan theta, at most {hoop['mu_min']:.4f} "
          f"(the hoop), so the ramp's friction coefficient {man['ramp_friction']:g} keeps all four rolling")
    half = [roll(L, g, th, m, r, sh["k"], dt / 2) for sh in man["shapes"]]
    print("check: at half the time step the arrivals are "
          + ", ".join(f"{n} {q['t_arrive']:.4f} s" for n, q in zip(names, half)))
    slide = roll(L, g, th, m, r, 0.0, dt)
    print(f"for the description: a frictionless block sliding the same ramp (no spin, k = 0) arrives at "
          f"{slide['t_arrive']:.4f} s (closed form sqrt(2 L / (g sin theta)) = {closed_form(L, g, th, 0.0):.4f} s) "
          f"at {slide['v_arrive']:.3f} m/s")
    pb = man["playback"]
    last = hoop["t_arrive"] / pb
    n_races = man["races"]
    print(f"video: played at {pb:g} speed; the solid ball finishes {ball['t_arrive'] / pb:.2f} s into each race and "
          f"the hoop {last:.2f} s in; all four clocks frozen from {last:.2f} s to "
          f"{man['race_period'] - man['ready_dur'] - man['reset_dur']:.2f} s of each {man['race_period']:g} s race, "
          f"then a {man['reset_dur']:g} s reset to the top and {man['ready_dur']:g} s at rest before the next release; "
          f"{n_races} races in {man['scene_duration']:g} s, so the video loops on the race")
    assert abs(n_races * man["race_period"] - man["scene_duration"]) < 1e-9
    return {"runs": runs, "ball": ball, "hoop": hoop, "gap": gap, "slide": slide}


def smoothstep(u: float) -> float:
    u = max(0.0, min(1.0, u))
    return u * u * (3 - 2 * u)


def shade(col, a: float) -> tuple:
    return tuple(int(round(c * a + BG[j] * (1 - a))) for j, c in enumerate(col))


def lighten(col, a: float) -> tuple:
    return tuple(int(round(c * (1 - a) + WHITE[j] * a)) for j, c in enumerate(col))


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
        self.ppm = man["px_per_m"]
        self.R = man["radius_m"] * self.ppm
        self.y0 = man["start_y_px"]
        self.y1 = self.y0 + man["ramp_length_m"] * self.ppm
        self.tag = f"{man['ramp_length_m']:g} m ramp at {man['ramp_angle_deg']:g} degrees, 1/4 speed"
        widths = {"overlay@34": (ImageFont.truetype(font, 34), man["overlay"])}
        for j, line in enumerate(man["title"].split("|")):
            widths[f"title line {j + 1}@56"] = (self.font_title, line)
        widths["counter@40"] = (self.font, f"race {man['races']} of {man['races']}")
        widths["tag@28"] = (self.font_tag, self.tag)
        for name, lines in LABELS.items():
            widths[f"label {lines[1]}@32"] = (self.font_small, lines[1] if lines[0] == "" else max(lines, key=len))
        widths["clock@40"] = (self.font, f"{meas['hoop']['t_arrive']:.2f} s")
        for j, line in enumerate(self.payoff_lines()):
            widths[f"payoff line {j + 1}@40"] = (self.font, line)
        print("text widths: " + ", ".join(f"{k} {f.getlength(s):.0f} px" for k, (f, s) in widths.items()))
        print(f"lane width {man['lane_x_px'][1] - man['lane_x_px'][0]} px, object diameter {2 * self.R:.0f} px, "
              f"finish line at y {self.y1 + self.R:.0f}; payoff card at {man['payoff_t']:g} s")

    def payoff_lines(self) -> list[str]:
        text = self.man["payoff_text"].format(ball=self.meas["ball"]["t_arrive"], hoop=self.meas["hoop"]["t_arrive"])
        return [s.strip() for s in text.split("|")]

    def race_state(self, t: float) -> tuple[int, float, float]:
        """Video time -> (race index, seconds into the race, reset fraction)."""
        man = self.man
        P = man["race_period"]
        k = int(t // P)
        tau = t - k * P
        reset_start = P - man["ready_dur"] - man["reset_dur"]
        u = smoothstep((tau - reset_start) / man["reset_dur"]) if tau >= reset_start else 0.0
        return k, tau, u

    def draw_object(self, d: ImageDraw.ImageDraw, name: str, cx: float, cy: float, phi: float) -> None:
        R, col = self.R, COLOURS[name]
        dark = shade(col, 0.42)
        c, s = math.cos(phi), math.sin(phi)
        box = (cx - R, cy - R, cx + R, cy + R)
        if name == "solid ball":
            d.ellipse(box, fill=col, outline=dark, width=3)
            d.ellipse((cx - R * 0.55, cy - R * 0.62, cx - R * 0.12, cy - R * 0.2), fill=lighten(col, 0.5))
            d.line([(cx, cy), (cx + R * 0.9 * c, cy + R * 0.9 * s)], fill=dark, width=7)
            d.ellipse((cx - 7, cy - 7, cx + 7, cy + 7), fill=dark)
        elif name == "solid cylinder":
            d.ellipse(box, fill=col, outline=dark, width=3)
            d.line([(cx - R * 0.9 * c, cy - R * 0.9 * s), (cx + R * 0.9 * c, cy + R * 0.9 * s)], fill=dark, width=14)
        elif name == "hollow ball":
            wall = 18
            d.ellipse(box, fill=shade(col, 0.14), outline=col, width=wall)
            rr = R - wall / 2
            mx, my = cx + rr * c, cy + rr * s
            d.ellipse((mx - 10, my - 10, mx + 10, my + 10), fill=dark)
        else:  # hoop
            wall = 7
            d.ellipse(box, outline=col, width=wall)
            rr = R - wall / 2
            mx, my = cx + rr * c, cy + rr * s
            d.ellipse((mx - 9, my - 9, mx + 9, my + 9), fill=WHITE)

    def draw_scene(self, t: float, hud_alpha: float) -> Image.Image:
        man, meas = self.man, self.meas
        L, r = man["ramp_length_m"], man["radius_m"]
        k, tau, u = self.race_state(t)
        tp = tau * man["playback"]
        img = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(img)
        R = self.R
        y_start, y_finish = self.y0 + R, self.y1 + R
        # Lanes: a faint stripe, the ramp surface on the left of each object, the start line.
        for x in man["lane_x_px"]:
            d.rectangle((x - 118, y_start - 2 * R - 10, x + 118, y_finish + 4), fill=LANE)
            d.line([(x - R - 6, y_start - 2 * R - 10), (x - R - 6, y_finish)], fill=WIRE, width=5)
            d.line([(x - 100, y_start), (x + 100, y_start)], fill=WIRE, width=2)
        # The finish line: a checkered strip across the width.
        seg = 24
        for i, x in enumerate(range(20, W - 20, seg)):
            d.rectangle((x, y_finish - 4, min(x + seg, W - 20), y_finish + 4), fill=WHITE if i % 2 == 0 else MUTED)
        for i, run in enumerate(meas["runs"]):
            name, cx, col = run["name"], man["lane_x_px"][i], COLOURS[run["name"]]
            for j, line in enumerate(LABELS[name]):
                if line:
                    d.text((cx, LABEL_Y[j]), line, font=self.font_small, fill=col, anchor="mm")
            arrived = tp >= run["t_arrive"]
            s = L if arrived else min(float(np.interp(tp, run["t"], run["s"])), L)
            s_draw = s * (1.0 - u)
            self.draw_object(d, name, cx, self.y0 + s_draw * self.ppm, s_draw / r)
            tc = run["t_arrive"] if arrived else tp
            if u < 0.5:
                text, a = f"{tc:.2f} s", 1.0 - 2.0 * u
            else:
                text, a = "0.00 s", 2.0 * u - 1.0
            frozen = arrived and u < 0.5
            d.text((cx, CLOCK_Y), text, font=self.font, fill=shade(col if frozen else TEXT, a), anchor="mm")
            if arrived and u < 0.5:
                d.text((cx, PLACE_Y), PLACES[run["place"]], font=self.font_tag, fill=shade(col, 1.0 - 2.0 * u), anchor="mm")
        if hud_alpha > 0.02:
            d.text((W / 2, COUNTER_Y), f"race {k + 1} of {man['races']}", font=self.font, fill=shade(TEXT, hud_alpha), anchor="mm")
            d.text((W / 2, TAG_Y), self.tag, font=self.font_tag, fill=shade(MUTED, hud_alpha), anchor="mm")
        return img

    def live_frame(self, f: int) -> np.ndarray:
        man = self.man
        t = f / self.fps
        title_on = t < man["title_until"]
        if title_on:
            title_alpha = 1.0 if t < man["title_until"] - 0.4 else (man["title_until"] - t) / 0.4
            hud_alpha = 0.0
        else:
            title_alpha = 0.0
            hud_alpha = min(1.0, (t - man["title_until"]) / 0.4)
        img = self.draw_scene(t, hud_alpha)
        d = ImageDraw.Draw(img)
        if title_on:
            for j, line in enumerate(man["title"].split("|")):
                d.text((W / 2, 190 + j * 62), line, font=self.font_title, fill=shade(TEXT, title_alpha), anchor="mm")
        if t >= man["payoff_t"]:
            a = min(1.0, (t - man["payoff_t"]) / man["payoff_hold"])
            for j, line in enumerate(self.payoff_lines()):
                d.text((W / 2, PAYOFF_Y + j * 56), line, font=self.font, fill=shade(GOLD, a), anchor="mm")
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
        first = self.frame_at(0)
        last = self.frame_at(total - 1)
        diff = np.abs(first.astype(int) - last.astype(int))
        print(f"loop check: last frame differs from the first in {int((diff.max(axis=2) > 24).sum())} px "
              f"(max channel difference {int(diff.max())})")
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
    man = json.loads((ROOT / "projects/rollrace/manifest.json").read_text())
    meas = measure(man)
    if "--measure-only" in sys.argv:
        return
    if "--frames" in sys.argv:
        times = [float(v) for v in sys.argv[sys.argv.index("--frames") + 1].split(",")]
        r = Renderer(man, meas)
        for tv in times:
            Image.fromarray(r.frame_at(int(round(tv * man["fps"])))).save(ROOT / f"media/rollrace/smoke-{tv}.png")
        print("smoke frames: " + ", ".join(f"{tv}" for tv in times))
        return
    Renderer(man, meas).render(ROOT / "media/rollrace/footage.mp4")


if __name__ == "__main__":
    main()
