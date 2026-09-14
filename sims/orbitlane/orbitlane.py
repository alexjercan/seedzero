#!/usr/bin/env python3
"""Orbit passing lane: speed up in orbit, do you pull ahead?

Two ships sit side by side in the same circular orbit 400 km above a
point-mass Earth. At the burst the gold ship gains 10 m/s along its
direction of motion; the white ship does nothing. Both are integrated in the
inertial plane with RK4 at a fixed step (no closed forms in the run), and
the gold ship's position is measured in the white ship's local frame:
along-track (ahead or behind) and radial (higher or lower). The white ship's
lap is complete when its polar angle has advanced by one full turn. A
backward burst of the same size is run as a check, as are a half-step run,
an energy-drift check and the Clohessy-Wiltshire closed forms. No seed: the
run is deterministic.

Measured and printed: the orbit, the white ship's lap time, the gold ship's
early lead and when it falls back level, its height and gap at the far side,
its highest point, its own lap time, and the gap and height after one white
lap; the same for the backward burst; the checks; the on-screen text widths.

usage: orbitlane.py [--measure-only] [--frames t1,t2,...]
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
EARTH_IN = (22, 28, 38)
EARTH_OUT = (58, 72, 96)
RIM = (110, 130, 160)
WHITE = (236, 240, 244)

# Layout: readouts under the overlay, the lap dial above the middle, the
# local view (white ship fixed) below it, captions at caption_y 0.75
# (y 1440..1510), payoff under the captions.
LABEL_Y = 236
READ_Y = 290
VALUE_Y = 338
PANEL_X = {"gap": 300.0, "height": 780.0}
DIAL_C = (540.0, 600.0)
DIAL_R_EARTH = 112.0
CLOCK_Y = 792
SHIP_A = (930.0, 1230.0)
PX_PER_KM = 5.0
VIEW_TOP = 900
VIEW_BOT = 1400
PAYOFF_Y = 1592.0


def simulate(mu: float, r0: float, dv: float, dt: float, duration: float) -> dict:
    """Two ships from the same point; the second gets dv along track at t = 0."""
    v0 = math.sqrt(mu / r0)
    n = int(round(duration / dt))
    # state rows: x, y, vx, vy for ship A (white) and ship B (gold)
    A = np.array([r0, 0.0, 0.0, v0])
    B = np.array([r0, 0.0, 0.0, v0 + dv])

    def deriv(s: np.ndarray) -> np.ndarray:
        r3 = (s[0] * s[0] + s[1] * s[1]) ** 1.5
        return np.array([s[2], s[3], -mu * s[0] / r3, -mu * s[1] / r3])

    def step(s: np.ndarray) -> np.ndarray:
        k1 = deriv(s)
        k2 = deriv(s + 0.5 * dt * k1)
        k3 = deriv(s + 0.5 * dt * k2)
        k4 = deriv(s + dt * k3)
        return s + dt / 6.0 * (k1 + 2 * k2 + 2 * k3 + k4)

    SA = np.empty((n + 1, 4))
    SB = np.empty((n + 1, 4))
    for i in range(n + 1):
        SA[i], SB[i] = A, B
        if i == n:
            break
        A, B = step(A), step(B)
    t = np.arange(n + 1) * dt
    # Local frame of A: radial unit e_r, along-track unit e_t (direction of motion).
    rA = np.hypot(SA[:, 0], SA[:, 1])
    rel = SB[:, :2] - SA[:, :2]
    dist = np.hypot(rel[:, 0], rel[:, 1])
    rB = np.hypot(SB[:, 0], SB[:, 1])
    angA = np.unwrap(np.arctan2(SA[:, 1], SA[:, 0]))
    angB = np.unwrap(np.arctan2(SB[:, 1], SB[:, 0]))
    # Along the track: arc length ahead of the white ship at the white ship's
    # radius. Height: the difference of the two distances from the centre.
    along = (angB - angA) * rA
    radial = rB - rA
    energyB = 0.5 * (SB[:, 2] ** 2 + SB[:, 3] ** 2) - mu / rB

    def crossing(arr: np.ndarray, level: float) -> float:
        i = int(np.argmax(arr >= level))
        f = (level - arr[i - 1]) / (arr[i] - arr[i - 1])
        return t[i - 1] + f * dt

    lapA = crossing(angA, 2 * math.pi)
    lapB = crossing(angB, 2 * math.pi) if angB[-1] >= 2 * math.pi else None

    def at(time: float, arr: np.ndarray) -> float:
        return float(np.interp(time, t, arr))

    i_lead = int(np.argmax(along)) if dv > 0 else int(np.argmin(along))
    lead_t, lead = t[i_lead], along[i_lead]
    after = np.arange(len(t)) > i_lead
    sign = 1.0 if dv > 0 else -1.0
    j = int(np.argmax(after & (sign * along <= 0.0)))
    level_t = t[j - 1] + dt * (along[j - 1]) / (along[j - 1] - along[j])
    i_high = int(np.argmax(sign * radial))
    return {
        "t": t, "SA": SA, "SB": SB, "along": along, "radial": radial, "dist": dist,
        "angA": angA, "angB": angB, "rA": rA, "rB": rB, "dt": dt, "v0": v0,
        "lapA": lapA, "lapB": lapB,
        "lead_t": lead_t, "lead": lead, "level_t": level_t,
        "half_along": at(lapA / 2, along), "half_radial": at(lapA / 2, radial),
        "high_t": t[i_high], "high": radial[i_high],
        "end_along": at(lapA, along), "end_radial": at(lapA, radial), "end_dist": at(lapA, dist),
        "energy_drift": float(np.max(np.abs(energyB - energyB[0])) / abs(energyB[0])),
        "apo_km": (rB.max() - rA[0]) / 1000, "peri_km": (rB.min() - rA[0]) / 1000,
    }


def mmss(seconds: float) -> str:
    m = int(seconds // 60)
    s = int(round(seconds - 60 * m))
    if s == 60:
        m, s = m + 1, 0
    return f"{m}:{s:02d}"


def report(tag: str, run: dict) -> None:
    lap = run["lapA"]
    print(f"{tag}: the gold ship is ahead by at most {run['lead'] / 1000:.2f} km at {run['lead_t']:.0f} s = "
          f"{mmss(run['lead_t'])} after the burst, then falls back level at {run['level_t']:.0f} s = "
          f"{mmss(run['level_t'])}; at the far side ({lap / 2:.0f} s) it is {run['half_radial'] / 1000:+.2f} km in "
          f"height and {run['half_along'] / 1000:+.2f} km along the track; highest point {run['high'] / 1000:+.2f} km at "
          f"{run['high_t']:.0f} s = {mmss(run['high_t'])}; its own lap takes {run['lapB']:.1f} s = "
          f"{mmss(run['lapB'])} ({run['lapB'] - lap:+.1f} s against the white ship); after one white lap "
          f"({lap:.1f} s = {mmss(lap)}) it is {run['end_along'] / 1000:+.2f} km along the track, "
          f"{run['end_radial'] / 1000:+.2f} km in height, {run['end_dist'] / 1000:.2f} km away in a straight line; "
          f"orbit {run['peri_km']:+.2f} to {run['apo_km']:+.2f} km against the white ship's height; "
          f"energy drift {run['energy_drift']:.1e}")


def measure(man: dict) -> dict:
    mu = man["mu"]
    R = man["earth_radius_km"] * 1000.0
    r0 = R + man["altitude_km"] * 1000.0
    dv = man["burst_m_per_s"]
    v0 = math.sqrt(mu / r0)
    T = 2 * math.pi * math.sqrt(r0 ** 3 / mu)
    nrate = 2 * math.pi / T
    dur = 1.05 * T
    print(f"orbit: circular, {man['altitude_km']:,.0f} km above an Earth of radius {R / 1000:,.0f} km "
          f"(mu {mu:.6g} m^3/s^2); speed {v0:,.1f} m/s; lap time 2 pi sqrt(r^3 / mu) = {T:.1f} s = {mmss(T)}; "
          f"RK4 at {man['dt']:g} s steps, deterministic, no seed; the gold ship gains {dv:g} m/s along its "
          f"motion at the burst ({dv * 3.6:.0f} km/h, {dv / v0 * 100:.3f}% of its speed)")
    run = simulate(mu, r0, dv, man["dt"], dur)
    print(f"white ship: back at the burst point after {run['lapA']:.2f} s = {mmss(run['lapA'])} "
          f"(closed form {T:.2f} s)")
    report("forward burst", run)
    back = simulate(mu, r0, -dv, man["dt"], dur)
    report("check, backward burst", back)
    fine = simulate(mu, r0, dv, man["check_dt"], dur)
    print(f"check, half the step ({man['check_dt']:g} s): white lap {fine['lapA']:.2f} s; after one white lap the "
          f"gold ship is {fine['end_along'] / 1000:+.3f} km along the track and {fine['end_radial'] / 1000:+.3f} km "
          f"in height (full step {run['end_along'] / 1000:+.3f} and {run['end_radial'] / 1000:+.3f})")
    cw_end = -3 * T * dv
    cw_high = 4 * dv / nrate
    cw_lead_t = math.acos(0.75) / nrate
    cw_lead = (4 * math.sin(nrate * cw_lead_t) / nrate - 3 * cw_lead_t) * dv
    print(f"check, Clohessy-Wiltshire closed forms: along track after one lap -3 T dv = {cw_end / 1000:.2f} km; "
          f"highest point 4 dv / n = {cw_high / 1000:.2f} km; largest lead {cw_lead / 1000:.2f} km at "
          f"{cw_lead_t:.0f} s; the new lap is 3 T dv / v = {3 * T * dv / v0:+.1f} s longer")
    return {"run": run, "T": T, "r0": r0, "R": R, "behind_km": -run["end_along"] / 1000,
            "high_km": run["high"] / 1000, "lead_km": run["lead"] / 1000}


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
        self.font_watch = ImageFont.truetype(font, 64)
        self.first = None
        self.run = meas["run"]
        self.lap = self.run["lapA"]
        self.rate = self.lap / man["lap_seconds"]  # sim seconds per video second
        self.earth = self.draw_earth()
        widths = {"overlay@34": (ImageFont.truetype(font, 34), man["overlay"])}
        for j, line in enumerate(man["title"].split("|")):
            widths[f"title line {j + 1}@56"] = (self.font_title, line)
        widths["label gap@40"] = (self.font, "gold ship, along the track")
        widths["label height@40"] = (self.font, "gold ship, height")
        widths["gap@44"] = (self.font_read, "166.3 km behind")
        widths["height@44"] = (self.font_read, "+35.3 km higher")
        widths["watch@64"] = (self.font_watch, "92:24")
        widths["watch label@32"] = (self.font_small, "since the burst, lap 1.00")
        widths["scale@32"] = (self.font_small, "100 km")
        for j, line in enumerate(self.payoff_lines()):
            widths[f"payoff line {j + 1}@40"] = (self.font, line)
        print("text widths: " + ", ".join(f"{k} {f.getlength(s):.0f} px" for k, (f, s) in widths.items()))
        print(f"time-lapse: {self.rate:.1f}x, the burst at {man['burn_t']:g} s of video, one white lap in "
              f"{man['lap_seconds']:g} s, lap complete at {man['burn_t'] + man['lap_seconds']:g} s of video; "
              f"far side at {man['burn_t'] + man['lap_seconds'] / 2:.1f} s; level again at "
              f"{man['burn_t'] + self.run['level_t'] / self.rate:.1f} s")

    def payoff_lines(self) -> list[str]:
        text = self.man["payoff_text"].format(behind=self.meas["behind_km"])
        return [s.strip() for s in text.split("|")]

    def draw_earth(self) -> Image.Image:
        img = Image.new("RGB", (W, H), BG)
        cx, cy = DIAL_C
        R = DIAL_R_EARTH
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        r = np.hypot(xx - cx, yy - cy) / R
        arr = np.empty((H, W, 3), dtype=np.float32)
        inside = r <= 1.0
        for ch in range(3):
            arr[..., ch] = np.where(inside, EARTH_OUT[ch] + (EARTH_IN[ch] - EARTH_OUT[ch]) * np.clip(r, 0, 1), BG[ch])
        img = Image.fromarray(arr.astype(np.uint8))
        d = ImageDraw.Draw(img)
        d.ellipse((cx - R, cy - R, cx + R, cy + R), outline=RIM, width=3)
        ro = R * self.meas["r0"] / self.meas["R"]
        d.ellipse((cx - ro, cy - ro, cx + ro, cy + ro), outline=WIRE, width=2)
        return img

    def state(self, sim_t: float):
        """Return along, radial (m), the white ship's angle, and the trail up to sim_t."""
        run = self.run
        if sim_t <= 0.0:
            ang = 2 * math.pi * sim_t / self.lap
            return 0.0, 0.0, ang, None
        i = min(int(round(sim_t / run["dt"])), len(run["t"]) - 1)
        return float(run["along"][i]), float(run["radial"][i]), float(run["angA"][i]), i

    def local_xy(self, along: float, radial: float) -> tuple[float, float]:
        return SHIP_A[0] + along / 1000 * PX_PER_KM, SHIP_A[1] - radial / 1000 * PX_PER_KM

    def ship(self, d: ImageDraw.ImageDraw, x: float, y: float, col, flame: float = 0.0, outline: bool = False) -> None:
        # A rocket pointing along the track (to the right). The white ship is
        # drawn as an outline so the gold one shows inside it before the burst.
        pts = [(x + 44, y), (x - 28, y - 24), (x - 16, y), (x - 28, y + 24)]
        if outline:
            big = [(x + 60, y), (x - 40, y - 34), (x - 24, y), (x - 40, y + 34)]
            d.polygon(big, fill=(40, 46, 54), outline=col, width=5)
        else:
            d.polygon(pts, fill=col)
            d.ellipse((x - 4, y - 7, x + 10, y + 7), fill=BG)
        if flame > 0.0:
            ln = 50 + 70 * flame
            d.polygon([(x - 28, y - 13), (x - 28 - ln, y), (x - 28, y + 13)], fill=CORAL)
            d.polygon([(x - 28, y - 6), (x - 28 - ln * 0.55, y), (x - 28, y + 6)], fill=GOLD)

    def draw_scene(self, t: float, title_on: bool) -> Image.Image:
        man = self.man
        sim_t = (t - man["burn_t"]) * self.rate
        frozen = sim_t >= self.lap
        sim_t = min(sim_t, self.lap)
        along, radial, ang, i = self.state(sim_t)
        img = self.earth.copy()
        d = ImageDraw.Draw(img)
        cx, cy = DIAL_C
        ro = DIAL_R_EARTH * self.meas["r0"] / self.meas["R"]
        # Burst point marker on the dial and the lap progress arc.
        d.line([(cx + ro - 10, cy), (cx + ro + 16, cy)], fill=MUTED, width=3)
        if sim_t > 0.0:
            deg = math.degrees(ang)
            d.arc((cx - ro - 6, cy - ro - 6, cx + ro + 6, cy + ro + 6), start=-deg, end=0, fill=(60, 110, 90), width=4)
        for col, a in ((WHITE, ang), (GOLD, ang + (along / self.meas["r0"] if i is not None else 0.0))):
            px, py = cx + ro * math.cos(a), cy - ro * math.sin(a)
            d.ellipse((px - 8, py - 8, px + 8, py + 8), fill=col)
        # Local view: the white ship fixed, the gold ship in its frame.
        y0 = SHIP_A[1]
        for xx in range(60, 1020, 26):
            d.line([(xx, y0), (xx + 12, y0)], fill=WIRE, width=2)
        d.text((1000, y0 + 40), "same height", font=self.font_small, fill=MUTED, anchor="rm")
        bar = 100 * PX_PER_KM
        d.line([(80, VIEW_BOT - 20), (80 + bar, VIEW_BOT - 20)], fill=MUTED, width=3)
        for xx in (80, 80 + bar):
            d.line([(xx, VIEW_BOT - 30), (xx, VIEW_BOT - 10)], fill=MUTED, width=3)
        d.text((80 + bar / 2, VIEW_BOT - 48), "100 km", font=self.font_small, fill=MUTED, anchor="mm")
        if i is not None and i > 1:
            pts = [self.local_xy(float(a), float(r)) for a, r in
                   zip(self.run["along"][: i + 1: 4], self.run["radial"][: i + 1: 4])]
            if len(pts) > 1:
                d.line(pts, fill=(150, 116, 60), width=4)
        flame = 0.0
        if 0.0 <= t - man["burn_t"] < man["burn_flash"]:
            flame = 1.0 - (t - man["burn_t"]) / man["burn_flash"]
        gx, gy = self.local_xy(along, radial)
        self.ship(d, SHIP_A[0], SHIP_A[1], WHITE, outline=True)
        self.ship(d, gx, gy, GOLD, flame)
        if not title_on:
            d.text((PANEL_X["gap"], LABEL_Y), "along the track", font=self.font, fill=GOLD, anchor="mm")
            d.text((PANEL_X["height"], LABEL_Y), "height", font=self.font, fill=GOLD, anchor="mm")
            d.text((PANEL_X["gap"], READ_Y), "gold ship is", font=self.font_small, fill=MUTED, anchor="mm")
            d.text((PANEL_X["height"], READ_Y), "gold ship is", font=self.font_small, fill=MUTED, anchor="mm")
            km = abs(along) / 1000
            word = "ahead" if along > 50 else ("behind" if along < -50 else "level")
            gap_s = f"{km:.1f} km {word}" if word != "level" else "level"
            hk = radial / 1000
            hword = "higher" if hk > 0.05 else ("lower" if hk < -0.05 else "level")
            h_s = f"{abs(hk):.1f} km {hword}" if hword != "level" else "level"
            d.text((PANEL_X["gap"], VALUE_Y), gap_s, font=self.font_read, fill=TEXT, anchor="mm")
            d.text((PANEL_X["height"], VALUE_Y), h_s, font=self.font_read, fill=TEXT, anchor="mm")
            if sim_t > 0.0:
                d.text((W / 2, CLOCK_Y), mmss(sim_t), font=self.font_watch, fill=TEXT, anchor="mm")
                d.text((W / 2, CLOCK_Y + 50), f"since the burst, lap {sim_t / self.lap:.2f}",
                       font=self.font_small, fill=MUTED, anchor="mm")
            else:
                d.text((W / 2, CLOCK_Y), "side by side", font=self.font, fill=TEXT, anchor="mm")
                d.text((W / 2, CLOCK_Y + 50), "same orbit, same speed", font=self.font_small, fill=MUTED, anchor="mm")
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
    man = json.loads((ROOT / "projects/orbitlane/manifest.json").read_text())
    meas = measure(man)
    if "--measure-only" in sys.argv:
        return
    if "--frames" in sys.argv:
        times = [float(v) for v in sys.argv[sys.argv.index("--frames") + 1].split(",")]
        r = Renderer(man, meas)
        for tv in times:
            Image.fromarray(r.frame_at(int(round(tv * man["fps"])))).save(ROOT / f"media/orbitlane/smoke-{tv}.png")
        print("smoke frames: " + ", ".join(f"{tv}" for tv in times))
        return
    Renderer(man, meas).render(ROOT / "media/orbitlane/footage.mp4")


if __name__ == "__main__":
    main()
