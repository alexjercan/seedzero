#!/usr/bin/env python3
"""Kapitza pendulum: can a pendulum stand upside down?

Two identical rigid pendulums balanced upside down, the same length, the
same light air drag, the same small nudge at the same moment. Top: the
pivot holds still. Bottom: the pivot shakes straight up and down, a
centimetre each way, forty times a second. Part way through, the shaking
pendulum alone gets a hard kick and recovers; later the shaking is
switched off and it falls. Equation of motion with theta measured from the upright
and y_p(t) the pivot height:

    theta'' = (g + y_p'') / l * sin(theta) - damping * theta'

integrated with RK4 at a fixed step. The shaking panel is drawn with
sub-frame motion blur so the forty hertz motion shows honestly at sixty
frames per second.

Measured and printed: the stability numbers (A omega against sqrt(2 g l)),
the still pendulum's fall time (tilt through ninety degrees) and the time
it first hangs straight down, the shaking pendulum's largest tilt over the
video and over a ten minute run, its slow wobble period against the
averaged-motion prediction, the fall time after the shaking stops, checks
without drag, with the shake below the threshold and with a hard kick,
and the on-screen text widths.

usage: kapitza.py [--measure-only] [--frames t1,t2,...]
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
ROD = (216, 222, 230)
BOB_R = 20

# Layout: two panels, captions between them at caption_y 0.49 (y 941..1021).
PANELS = {"still": {"label_y": 214, "pivot": (540.0, 600.0)}, "shaking": {"label_y": 1104, "pivot": (540.0, 1440.0)}}
PX_PER_M = 2800.0
BLUR_BOX = (190, 1080, 890, 1800)  # crop blurred for the shaking panel (x0, y0, x1, y1)
PAYOFF_Y = 1836.0


def smoothstep(u: float) -> float:
    u = max(0.0, min(1.0, u))
    return u * u * (3 - 2 * u)


def simulate(man: dict, shaking: bool, duration: float, nudge: float, shake_off_t: float | None,
             damping: float | None = None, amplitude: float | None = None,
             kick: tuple[float, float] | None = None) -> dict:
    """Returns per-step theta (rad from upright), pivot height, and events.

    kick is an optional (time, rad/s) second impulse."""
    g, l = man["g"], man["length"]
    A = man["amplitude"] if amplitude is None else amplitude
    omega = 2 * math.pi * man["shake_hz"]
    gamma = man["damping"] if damping is None else damping
    steps_per_s = man["fps"] * man["substeps"]
    dt = 1.0 / steps_per_s
    ramp = man["shake_off_ramp"]

    def env(t: float) -> float:
        if not shaking:
            return 0.0
        if shake_off_t is None or t < shake_off_t:
            return 1.0
        return 1.0 - smoothstep((t - shake_off_t) / ramp)

    def y_p(t: float) -> float:
        return A * env(t) * math.cos(omega * t)

    h = 1e-5

    def y_pp(t: float) -> float:
        return (y_p(t + h) - 2 * y_p(t) + y_p(t - h)) / (h * h)

    def deriv(t: float, th: float, w: float) -> tuple[float, float]:
        return w, (g + y_pp(t)) / l * math.sin(th) - gamma * w

    n = int(round(duration * steps_per_s))
    theta = np.empty(n + 1)
    yp = np.empty(n + 1)
    th, w = 0.0, 0.0
    nudge_step = int(round(man["nudge_t"] * steps_per_s))
    kick_step = int(round(kick[0] * steps_per_s)) if kick else -1
    fall_t = bottom_t = None
    fall_after_off = None
    kick_max = 0.0
    for i in range(n + 1):
        t = i * dt
        if i == nudge_step:
            w += nudge
        if i == kick_step:
            w += kick[1]
        if kick and i > kick_step:
            kick_max = max(kick_max, abs(th))
        theta[i], yp[i] = th, y_p(t)
        if i == n:
            break
        k1 = deriv(t, th, w)
        k2 = deriv(t + 0.5 * dt, th + 0.5 * dt * k1[0], w + 0.5 * dt * k1[1])
        k3 = deriv(t + 0.5 * dt, th + 0.5 * dt * k2[0], w + 0.5 * dt * k2[1])
        k4 = deriv(t + dt, th + dt * k3[0], w + dt * k3[1])
        th_new = th + dt / 6 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0])
        w_new = w + dt / 6 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1])
        if fall_t is None and abs(th) < math.pi / 2 <= abs(th_new):
            fall_t = t + dt * (math.pi / 2 - abs(th)) / (abs(th_new) - abs(th))
            if shake_off_t is not None and t >= shake_off_t:
                fall_after_off = fall_t - shake_off_t
        if bottom_t is None and fall_t is not None and abs(th) < math.pi <= abs(th_new):
            bottom_t = t + dt * (math.pi - abs(th)) / (abs(th_new) - abs(th))
        th, w = th_new, w_new
    return {"theta": theta, "yp": yp, "dt": dt, "fall_t": fall_t, "bottom_t": bottom_t,
            "fall_after_off": fall_after_off, "nudge_t": man["nudge_t"], "kick_max_deg": math.degrees(kick_max)}


def slow_period(run: dict, t0: float, t1: float) -> float | None:
    """Mean period of the slow wobble from zero crossings of the frame-averaged tilt."""
    dt = run["dt"]
    th = run["theta"][int(t0 / dt):int(t1 / dt)]
    win = max(1, int(round((1.0 / 40.0) / dt)))  # average over one shake period
    kernel = np.ones(win) / win
    sm = np.convolve(th, kernel, mode="valid")
    sign = np.sign(sm)
    idx = np.nonzero((sign[1:] * sign[:-1]) < 0)[0]
    if len(idx) < 3:
        return None
    return float(2 * np.mean(np.diff(idx)) * dt)


def measure(man: dict) -> dict:
    g, l, A = man["g"], man["length"], man["amplitude"]
    omega = 2 * math.pi * man["shake_hz"]
    a_omega, threshold = A * omega, math.sqrt(2 * g * l)
    print(f"pendulum {l * 100:.0f} cm, pivot stroke {A * 100:.1f} cm each way at {man['shake_hz']:g} Hz "
          f"(peak pivot acceleration {A * omega * omega / g:.0f} g), air drag {man["damping"]:g} per second, "
          f"nudge {man['nudge_rad_s']:g} rad/s at {man['nudge_t']:g} s, RK4 at {man['fps'] * man['substeps']} steps per second")
    print(f"stability: A omega = {a_omega:.2f} m/s against the threshold sqrt(2 g l) = {threshold:.2f} m/s "
          f"({a_omega / threshold:.2f} times); "
          f"averaged-motion basin edge {math.degrees(math.acos(4 * g * l / a_omega ** 2 - 1)):.0f} deg from upright; "
          f"predicted slow wobble {2 * math.pi / math.sqrt(a_omega ** 2 / (2 * l * l) - g / l):.3f} s per cycle")
    dur = man["scene_duration"]
    still = simulate(man, False, dur, man["nudge_rad_s"], None)
    kick_spec = (man["kick_t"], man["kick_rad_s"])
    shaking = simulate(man, True, dur, man["nudge_rad_s"], man["shake_off_t"], kick=kick_spec)
    fall = still["fall_t"] - man["nudge_t"]
    print(f"pivot still: tilt passes 90 deg {fall:.3f} s after the nudge (at {still['fall_t']:.3f} s), "
          f"hangs straight down first at {still['bottom_t']:.3f} s; "
          f"tilt at the end of the video {math.degrees(abs(still['theta'][-1])):.1f} deg from upright")
    fps = man["fps"]
    off_i = int(man["shake_off_t"] / shaking["dt"])
    kick_i = int(man["kick_t"] / shaking["dt"])
    tilt_before = np.degrees(np.abs(shaking["theta"][:kick_i]))
    tilt_kicked = np.degrees(np.abs(shaking["theta"][kick_i:off_i]))
    print(f"pivot shaking: largest tilt after the nudge and before the kick {tilt_before.max():.2f} deg (at {tilt_before.argmax() * shaking['dt']:.2f} s); "
          f"tilt at 10 s {math.degrees(abs(shaking['theta'][int(10 / shaking['dt'])])):.2f} deg; "
          f"measured slow wobble {slow_period(shaking, man['nudge_t'], man['kick_t']):.3f} s per cycle")
    peak = int(tilt_kicked.argmax())
    back = kick_i + peak + int(np.argmax(tilt_kicked[peak:] < 5.0)) if (tilt_kicked[peak:] < 5.0).any() else None
    print(f"kick {man['kick_rad_s']:g} rad/s at {man['kick_t']:g} s ({man['kick_rad_s'] / man['nudge_rad_s']:.0f} times the nudge): swings out to "
          f"{tilt_kicked.max():.1f} deg (at {man['kick_t'] + tilt_kicked.argmax() * shaking['dt']:.2f} s), back under 5 deg at "
          + (f"{back * shaking['dt']:.2f} s" if back is not None else "never")
          + f", tilt at {man['shake_off_t']:g} s {math.degrees(abs(shaking['theta'][off_i])):.2f} deg, never fell before the shaking stops")
    assert shaking["fall_t"] is None or shaking["fall_t"] > man["shake_off_t"]
    print(f"shaking stops at {man['shake_off_t']:g} s (ramped down over {man['shake_off_ramp']:g} s): tilt passes 90 deg "
          f"{shaking['fall_after_off']:.3f} s later (at {shaking['fall_t']:.3f} s), hangs straight down first at {shaking['bottom_t']:.3f} s")
    long = simulate(man, True, man["long_run"], man["nudge_rad_s"], None)
    tilt_long = np.degrees(np.abs(long["theta"]))
    print(f"ten minute run, shaking never stopped: largest tilt {tilt_long.max():.2f} deg at {tilt_long.argmax() * long['dt']:.2f} s, "
          f"largest tilt after the first minute {tilt_long[int(60 / long['dt']):].max():.4f} deg, never fell "
          f"(fall time {long['fall_t']})")
    # Checks.
    nodrag = simulate(man, True, 120.0, man["nudge_rad_s"], None, damping=0.0)
    print(f"check: no drag, two minutes: largest tilt {np.degrees(np.abs(nodrag['theta'])).max():.2f} deg, fall time {nodrag['fall_t']}, "
          f"slow wobble {slow_period(nodrag, man['nudge_t'], 60.0):.3f} s per cycle")
    below = simulate(man, True, dur, man["nudge_rad_s"], None, amplitude=man["check_amplitude_below"])
    print(f"check: stroke {man['check_amplitude_below'] * 100:.1f} cm (A omega {man['check_amplitude_below'] * omega:.2f} m/s, below the threshold): "
          f"falls {below['fall_t'] - man['nudge_t']:.3f} s after the nudge" if below["fall_t"] else "check: below threshold did not fall")
    calm = simulate(man, True, dur, man["nudge_rad_s"], man["shake_off_t"])
    print(f"check: the same run without the kick: tilt at {man['shake_off_t']:g} s "
          f"{math.degrees(abs(calm['theta'][int(man['shake_off_t'] / calm['dt'])])):.3f} deg, falls {calm['fall_after_off']:.3f} s after the shaking stops")
    return {"still": still, "shaking": shaking, "fall": fall, "max_tilt_before_kick": float(tilt_before.max()),
            "kick_max": float(tilt_kicked.max()), "fall_after_off": shaking["fall_after_off"], "long_max": float(tilt_long.max())}


class Renderer:
    def __init__(self, man: dict, meas: dict):
        self.man, self.meas = man, meas
        self.fps = man["fps"]
        font = os.environ["SEED_ZERO_FONT"]
        self.font = ImageFont.truetype(font, 40)
        self.font_small = ImageFont.truetype(font, 32)
        self.font_big = ImageFont.truetype(font, 56)
        self.font_title = ImageFont.truetype(font, 56)
        self.L = man["length"] * PX_PER_M
        self.font_read = ImageFont.truetype(font, 48)
        widths = {"overlay@34": (ImageFont.truetype(font, 34), man["overlay"]), "title line 1@56": (self.font_title, man["title"].split("|")[0]), "title line 2@56": (self.font_title, man["title"].split("|")[-1]),
                  "label@40": (self.font, f"pivot shaking {man['shake_hz']:g} times a second"),
                  "readout@48": (self.font_read, f"fell in {meas['fall_after_off']:.2f} s"), "readout up@48": (self.font_read, f"up for {man['shake_off_t']:.1f} s")}
        for j, line in enumerate(self.payoff_lines(man["scene_duration"] - 1)):
            widths[f"payoff line {j + 1}@40"] = (self.font, line)
        for j, line in enumerate(self.payoff_lines(man["shake_off_t"] - 1)):
            widths[f"early payoff line {j + 1}@40"] = (self.font, line)
        print("text widths: " + ", ".join(f"{k} {f.getlength(s):.0f} px" for k, (f, s) in widths.items()))

    def payoff_lines(self, t: float) -> list[str]:
        man, m = self.man, self.meas
        if t < man["shake_off_t"]:
            shaking = f"pivot shaking: still up at {t:.0f} s"
        elif m["shaking"]["fall_t"] is None or t < m["shaking"]["fall_t"]:
            shaking = f"shaking off at {man['shake_off_t']:g} s"
        else:
            shaking = f"shaking off at {man['shake_off_t']:g} s: fell in {m['fall_after_off']:.2f} s"
        text = man["payoff_text"].format(fall=m["fall"], shaking=shaking)
        return [s.strip() for s in text.split("|")]

    def draw_pendulum(self, d: ImageDraw.ImageDraw, theta: float, pivot: tuple, yp: float, colour_rod=ROD, bob=TEAL, rail=True):
        px, py = pivot[0], pivot[1] - yp * PX_PER_M
        bx, by = px + self.L * math.sin(theta), py - self.L * math.cos(theta)
        if rail:
            d.line((px, pivot[1] - 70, px, pivot[1] + 70), fill=WIRE, width=4)
        d.line((px, py, bx, by), fill=colour_rod, width=10)
        d.rectangle((px - 16, py - 16, px + 16, py + 16), fill=MUTED)
        d.ellipse((bx - BOB_R, by - BOB_R, bx + BOB_R, by + BOB_R), fill=bob)

    def frame_at(self, f: int) -> np.ndarray:
        man, m = self.man, self.meas
        t = f / self.fps
        img = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(img)
        title_on = t < man["title_until"]
        steps_per_s = self.fps * man["substeps"]

        def shade_col(col, alpha):
            return tuple(int(c * alpha + BG[j] * (1 - alpha)) for j, c in enumerate(col))
        # Top: the still pivot, drawn once at the frame time.
        run = m["still"]
        i = min(int(round(t * steps_per_s)), len(run["theta"]) - 1)
        self.draw_pendulum(d, float(run["theta"][i]), PANELS["still"]["pivot"], 0.0, bob=GOLD)
        # Bottom: the shaking pivot with sub-frame motion blur.
        run = m["shaking"]
        x0, y0, x1, y1 = BLUR_BOX
        acc = np.zeros((y1 - y0, x1 - x0, 3), dtype=np.float32)
        nb = man["blur_samples"]
        for k in range(nb):
            ts = t + (k + 0.5) / (nb * self.fps)
            j = min(int(round(ts * steps_per_s)), len(run["theta"]) - 1)
            sub = Image.new("RGB", (x1 - x0, y1 - y0), BG)
            sd = ImageDraw.Draw(sub)
            piv = (PANELS["shaking"]["pivot"][0] - x0, PANELS["shaking"]["pivot"][1] - y0)
            self.draw_pendulum(sd, float(run["theta"][j]), piv, float(run["yp"][j]), bob=TEAL)
            acc += np.asarray(sub, dtype=np.float32)
        img.paste(Image.fromarray((acc / nb).astype(np.uint8)), (x0, y0))
        d = ImageDraw.Draw(img)
        # Shaker mark under the bottom pivot.
        spx, spy = PANELS["shaking"]["pivot"]
        env_on = t < man["shake_off_t"]
        col = TEAL if env_on else MUTED
        d.line((spx + 60, spy - 40, spx + 60, spy + 40), fill=col, width=4)
        d.polygon([(spx + 60, spy - 54), (spx + 50, spy - 36), (spx + 70, spy - 36)], fill=col)
        d.polygon([(spx + 60, spy + 54), (spx + 50, spy + 36), (spx + 70, spy + 36)], fill=col)
        # Labels and readouts.
        for name, p in PANELS.items():
            if name == "still" and title_on:
                alpha = 1.0 if t < man["title_until"] - 0.4 else (man["title_until"] - t) / 0.4
                shade = tuple(int(c * alpha + BG[j] * (1 - alpha)) for j, c in enumerate(TEXT))
                for j, line in enumerate(man["title"].split("|")):
                    d.text((W / 2, 186 + j * 62), line, font=self.font_title, fill=shade, anchor="mm")
                continue
            if name == "still":
                label = "pivot still"
            elif env_on:
                label = f"pivot shaking {man['shake_hz']:g} times a second"
            else:
                label = "shaking switched off"
            d.text((60, p["label_y"]), label, font=self.font, fill=TEAL if name == "shaking" and env_on else (GOLD if name == "still" else CORAL), anchor="lm")
            run = m[name]
            if t < man["nudge_t"]:
                status, col = "balanced", TEXT
            elif run["fall_t"] is not None and t >= run["fall_t"]:
                if name == "still":
                    status, col = f"fell in {run['fall_t'] - man['nudge_t']:.2f} s", GOLD
                else:
                    status, col = f"fell in {m['fall_after_off']:.2f} s", CORAL
            else:
                status, col = f"up for {t - man['nudge_t']:.1f} s", TEXT
            d.text((60, p["label_y"] + 54), status, font=self.font_read, fill=col, anchor="lm")
            # Nudge and kick marks: an arrow at the bob, pointing the way the push goes.
            pushes = [(man["nudge_t"], "nudge")]
            if name == "shaking":
                pushes.append((man["kick_t"], "kick"))
            for t_push, word in pushes:
                if t_push - 0.3 <= t < t_push + 0.6:
                    a = 1.0 if t < t_push + 0.3 else 1 - (t - t_push - 0.3) / 0.3
                    i = min(int(round(t_push * steps_per_s)), len(run["theta"]) - 1)
                    bx = p["pivot"][0] + self.L * math.sin(float(run["theta"][i]))
                    by = p["pivot"][1] - self.L * math.cos(float(run["theta"][i]))
                    colp = shade_col(GOLD, a)
                    d.line((bx - 110, by, bx - BOB_R - 14, by), fill=colp, width=8)
                    d.polygon([(bx - BOB_R - 6, by), (bx - BOB_R - 30, by - 16), (bx - BOB_R - 30, by + 16)], fill=colp)
                    d.text((bx - 70, by + 26), word, font=self.font_small, fill=colp, anchor="mt")
        if t >= man["payoff_t"]:
            alpha = min(1.0, (t - man["payoff_t"]) / man["payoff_hold"])
            shade = tuple(int(c * alpha + BG[j] * (1 - alpha)) for j, c in enumerate(GOLD))
            for j, line in enumerate(self.payoff_lines(t)):
                d.text((W / 2, PAYOFF_Y - 32 + j * 64), line, font=self.font, fill=shade, anchor="mm")
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
    man = json.loads((ROOT / "projects/kapitza/manifest.json").read_text())
    meas = measure(man)
    if "--measure-only" in sys.argv:
        return
    if "--frames" in sys.argv:
        times = [float(v) for v in sys.argv[sys.argv.index("--frames") + 1].split(",")]
        r = Renderer(man, meas)
        for tv in times:
            Image.fromarray(r.frame_at(int(round(tv * man["fps"])))).save(ROOT / f"media/kapitza/smoke-{tv}.png")
        print("smoke frames: " + ", ".join(f"{tv}" for tv in times))
        return
    Renderer(man, meas).render(ROOT / "media/kapitza/footage.mp4")


if __name__ == "__main__":
    main()
