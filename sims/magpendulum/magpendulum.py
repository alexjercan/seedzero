#!/usr/bin/env python3
"""Magnetic pendulum: same drop, same magnet?

A steel bob on a one metre string swings over three magnets and slows
with light drag until it stops over one of them. Seen from above. Two
bobs are released from rest a tenth of a millimetre apart: the same
table, the same magnets, the same equation,

    r'' = -(g / L) r - damping r' + sum_i K (m_i - r) / (|m_i - r|^2 + gap^2)^(3/2)

integrated with RK4 at a fixed step. The release point is not hand
picked: the sim first maps a 200 by 200 grid of release points one
millimetre apart (each run to its final magnet), then takes the grid
point nearest a fixed reference point whose neighbour a tenth of a
millimetre to the right ends at a different magnet, and confirms the pair
with the fine integrator.

Measured and printed: the map's share of release points whose neighbour
one millimetre away, and a tenth of a millimetre away, ends at a
different magnet; the chosen release point; the gap between the two bobs
over time and the moment it passes one bob width; the final magnet and
settle time of each bob; energy bookkeeping; and the on-screen text
widths.

usage: magpendulum.py [--measure-only] [--frames t1,t2,...] [--no-map]  (--no-map reuses media/magpendulum/map.npz)
"""

from __future__ import annotations

import json
import math
import os
import subprocess
import sys
import time
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
MAGNETS = [(232, 96, 88), (90, 170, 230), (200, 140, 230)]
BOB_A = (236, 240, 244)
BOB_B = GOLD

# Layout: the seed overlay (compose) sits at y 96..130, the title or the
# header label below it, the table seen from above (square, y 260..1200),
# captions below it at caption_y 0.655 (y 1258..1330), the gap strip below
# the captions and the payoff at the bottom.
TABLE = {"cx": 540.0, "cy": 730.0, "half_px": 470.0, "label_y": 205}
STRIP = {"y": 1520.0, "x0": 140.0, "x1": 940.0, "label_y": 1430}
PAYOFF_Y = 1836.0


def smoothstep(u: float) -> float:
    u = max(0.0, min(1.0, u))
    return u * u * (3 - 2 * u)


def magnets_xy(man: dict) -> np.ndarray:
    R = man["magnet_radius"]
    return np.array([[R * math.cos(math.radians(a)), R * math.sin(math.radians(a))] for a in man["magnet_angles_deg"]])


def accel(p: np.ndarray, v: np.ndarray, man: dict, mags: np.ndarray) -> np.ndarray:
    """p, v shaped (..., 2). Vectorised over leading dimensions."""
    a = -(man["g"] / man["length"]) * p - man["damping"] * v
    gap2 = man["magnet_gap"] ** 2
    for m in mags:
        dm = m - p
        r2 = np.sum(dm * dm, axis=-1, keepdims=True) + gap2
        a = a + man["magnet_strength"] * dm / r2 ** 1.5
    return a


def rk4_step(p, v, dt, man, mags):
    k1v = accel(p, v, man, mags); k1p = v
    k2v = accel(p + 0.5 * dt * k1p, v + 0.5 * dt * k1v, man, mags); k2p = v + 0.5 * dt * k1v
    k3v = accel(p + 0.5 * dt * k2p, v + 0.5 * dt * k2v, man, mags); k3p = v + 0.5 * dt * k2v
    k4v = accel(p + dt * k3p, v + dt * k3v, man, mags); k4p = v + dt * k3v
    return p + dt / 6 * (k1p + 2 * k2p + 2 * k3p + k4p), v + dt / 6 * (k1v + 2 * k2v + 2 * k3v + k4v)


def final_magnets(points: np.ndarray, man: dict, mags: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Run every release point (n, 2) from rest for map_duration; return the
    nearest magnet at the end and the speed at the end."""
    dt = 1.0 / man["map_steps_per_s"]
    p = points.astype(np.float64).copy()
    v = np.zeros_like(p)
    for _ in range(int(man["map_duration"] * man["map_steps_per_s"])):
        p, v = rk4_step(p, v, dt, man, mags)
    d2 = np.stack([np.sum((p - m) ** 2, axis=-1) for m in mags], axis=-1)
    return d2.argmin(axis=-1), np.hypot(v[:, 0], v[:, 1])


def run_pair(release: np.ndarray, man: dict, mags: np.ndarray, duration: float) -> dict:
    """Fine run of the two bobs; positions sampled once per screen frame (fps / playback
    samples per physics second) and events."""
    fps, sub = man["fps"], man["substeps"]
    dt = 1.0 / (fps * sub)
    samples_per_s = fps / man["playback"]
    steps_per_sample = int(round(fps * sub / samples_per_s))
    assert abs(steps_per_sample * samples_per_s - fps * sub) < 1e-9, "playback must divide the step rate"
    n = int(round(duration * samples_per_s))
    p = np.array([release, release + [man["separation"], 0.0]])
    v = np.zeros_like(p)
    pos = np.empty((n + 1, 2, 2))
    split_t = None
    settle = [None, None]
    settle_mag = [None, None]
    bob = man["bob_diameter"]
    for f in range(n + 1):
        pos[f] = p
        if f == n:
            break
        for k in range(steps_per_sample):
            t = (f * steps_per_sample + k) * dt
            p_new, v_new = rk4_step(p, v, dt, man, mags)
            gap_old, gap_new = np.hypot(*(p[1] - p[0])), np.hypot(*(p_new[1] - p_new[0]))
            if split_t is None and gap_old < bob <= gap_new:
                split_t = t + dt * (bob - gap_old) / (gap_new - gap_old)
            for b in range(2):
                d = np.hypot(*(mags - p_new[b]).T)
                near = int(d.argmin())
                slow = np.hypot(*v_new[b]) < man["settle_speed"]
                if d[near] < man["settle_radius"] and slow:
                    if settle[b] is None:
                        settle[b], settle_mag[b] = t + dt, near
                elif settle[b] is not None and settle_mag[b] != near:
                    settle[b], settle_mag[b] = None, None  # left again
            p, v = p_new, v_new
    d2 = np.stack([np.sum((p - m) ** 2, axis=-1) for m in mags], axis=-1)
    return {"pos": pos, "samples_per_s": samples_per_s, "split_t": split_t, "final": d2.argmin(axis=-1), "settle_t": settle,
            "settle_mag": settle_mag, "end_speed": np.hypot(v[:, 0], v[:, 1]), "end_dist": np.sqrt(d2.min(axis=-1))}


def measure(man: dict, with_map: bool = True) -> dict:
    mags = magnets_xy(man)
    names = man["magnet_names"]
    print(f"string {man['length']:g} m, drag {man['damping']:g} per second, three magnets {man['magnet_radius'] * 100:.0f} cm from the centre at "
          f"{man['magnet_angles_deg']} deg, bob {man['magnet_gap'] * 100:.0f} cm above them, magnet strength {man['magnet_strength']:g} m^3/s^2 "
          f"(pull straight above a magnet {man['magnet_strength'] / man['magnet_gap'] ** 2 / man['g']:.2f} g), bob {man['bob_diameter'] * 1000:.0f} mm across, "
          f"pair {man['separation'] * 1000:.1f} mm apart, RK4 at {man['fps'] * man['substeps']} steps per second for the pair")
    n, hw, sep = man["map_n"], man["view_half_width"], man["separation"]
    xs = -hw + (np.arange(n) + 0.5) * (2 * hw / n)
    gx, gy = np.meshgrid(xs, xs)
    grid = np.stack([gx.ravel(), gy.ravel()], axis=-1)
    ref = np.array(man["reference_point"])
    if with_map:
        t0 = time.time()
        mag_a, speed_a = final_magnets(grid, man, mags)
        mag_b, speed_b = final_magnets(grid + [sep, 0.0], man, mags)
        pix = 2 * hw / n
        map_a = mag_a.reshape(n, n)
        right_differs = (map_a[:, 1:] != map_a[:, :-1])
        up_differs = (map_a[1:, :] != map_a[:-1, :])
        share_1mm = float((right_differs[:-1, :] | up_differs[:, :-1]).mean())
        share_right = float(right_differs.mean())
        share_01 = float((mag_a != mag_b).mean())
        counts = np.bincount(mag_a, minlength=3)
        print(f"map: {n} x {n} release points {pix * 1000:.1f} mm apart over a {2 * hw * 100:.0f} cm square, each run {man['map_duration']:g} s at "
              f"{man['map_steps_per_s']} steps per second ({time.time() - t0:.0f} s of compute); final magnets "
              + ", ".join(f"{names[i]} {counts[i]}" for i in range(3))
              + f"; still moving faster than {man['settle_speed'] * 1000:.0f} mm/s at the end: {int((speed_a > man['settle_speed']).sum())} points")
        print(f"map: {100 * share_right:.1f}% of release points end at a different magnet from their neighbour {pix * 1000:.0f} mm to the right "
              f"({100 * share_1mm:.1f}% differ from the right or the upper neighbour); "
              f"{100 * share_01:.2f}% differ from a neighbour {sep * 1000:.1f} mm to the right")
        cand = np.nonzero(mag_a != mag_b)[0]
        order = cand[np.argsort(np.hypot(*(grid[cand] - ref).T), kind="stable")]
        np.savez(ROOT / "media/magpendulum/map.npz", mag_a=mag_a, mag_b=mag_b, grid=grid)
    else:
        saved = np.load(ROOT / "media/magpendulum/map.npz")
        mag_a, mag_b = saved["mag_a"], saved["mag_b"]
        cand = np.nonzero(mag_a != mag_b)[0]
        order = cand[np.argsort(np.hypot(*(grid[cand] - ref).T), kind="stable")]
        print("map: loaded from media/magpendulum/map.npz")
    chosen = None
    run_dur = man["run_duration"]
    for rank, idx in enumerate(order[:10]):
        pair = run_pair(grid[idx], man, mags, run_dur)
        fa, fb = pair["final"]
        ok = fa != fb and pair["split_t"] is not None
        print(f"candidate {rank + 1}: release ({grid[idx][0] * 100:.2f}, {grid[idx][1] * 100:.2f}) cm, {np.hypot(*(grid[idx] - ref)) * 100:.2f} cm from the "
              f"reference {tuple(round(v * 100, 1) for v in ref)} cm; map says {names[mag_a[idx]]} and {names[mag_b[idx]]}; fine run ends at "
              f"{names[fa]} and {names[fb]}" + (" -> accepted" if ok else " -> rejected"))
        if ok:
            chosen = (grid[idx], pair)
            break
    if chosen is None:
        raise SystemExit("no candidate release point survived the fine run")
    release, pair = chosen
    fps = int(round(pair["samples_per_s"]))  # samples per physics second
    gap = np.hypot(*(pair["pos"][:, 1] - pair["pos"][:, 0]).T)
    print(f"release: ({release[0] * 100:.2f}, {release[1] * 100:.2f}) cm and {man['separation'] * 1000:.1f} mm to the right of it, both from rest")
    marks = [0.001, 0.01, 0.1]
    for g_ in marks:
        i = int(np.argmax(gap > g_)) if (gap > g_).any() else None
        print(f"gap passes {g_ * 1000:g} mm at {i / fps:.2f} s" if i is not None else f"gap never passes {g_ * 1000:g} mm")
    print("gap in the first second: " + ", ".join(f"{k / 10:.1f} s {gap[k * fps // 10] * 1000:.3f} mm" for k in range(0, 11, 2)))
    print(f"gap at 1 s {gap[fps] * 1000:.3f} mm, 2 s {gap[2 * fps] * 1000:.3f} mm, 3 s {gap[3 * fps] * 1000:.2f} mm, 5 s {gap[5 * fps] * 1000:.1f} mm, "
          f"largest {gap.max() * 100:.1f} cm at {gap.argmax() / fps:.1f} s; "
          f"the gap is {gap[int(3.0 * fps)] / man['separation']:.0f} times the release gap at 3 s")
    i100 = int(np.argmax(gap > 0.1))
    print(f"the gap is a thousand times the release gap ({man['separation'] * 1000 * 1000:.0f} mm) at {i100 / fps:.2f} s")
    print(f"split (gap passes one bob width, {man['bob_diameter'] * 1000:.0f} mm): {pair['split_t']:.3f} s")
    for b, label in enumerate(("white bob", "gold bob")):
        st = pair["settle_t"][b]
        print(f"{label}: ends over the {names[pair['final'][b]]} magnet, {pair['end_dist'][b] * 1000:.2f} mm from its centre, speed {pair['end_speed'][b] * 1000:.2f} mm/s at "
              f"{run_dur:g} s; settled (within {man['settle_radius'] * 1000:.0f} mm, under {man['settle_speed'] * 1000:.0f} mm/s) at "
              + (f"{st:.2f} s" if st is not None else "never"))
    # Independent check: the pair at half the step size.
    fine = dict(man)
    fine["substeps"] = man["substeps"] * 2
    pair2 = run_pair(release, fine, mags, run_dur)
    print(f"check: the same pair at {fine['fps'] * fine['substeps']} steps per second splits at {pair2['split_t']:.3f} s and ends at "
          f"{names[pair2['final'][0]]} and {names[pair2['final'][1]]}")
    # Check: the pair released farther apart, 1 mm and 1 cm.
    for s_ in (0.001, 0.01):
        alt = dict(man)
        alt["separation"] = s_
        p3 = run_pair(release, alt, mags, run_dur)
        print(f"check: released {s_ * 1000:g} mm apart instead: split at {p3['split_t']:.3f} s, ends at {names[p3['final'][0]]} and {names[p3['final'][1]]}")
    n_drops = int(round(man["scene_duration"] / man["drop_period"]))
    shown = (man["drop_period"] - man["release_t"] - man["reset_dur"]) * man["playback"]
    assert shown <= run_dur, "the drop shows more physics than was run"
    print(f"video: {n_drops} drops of {man['drop_period']:g} s at {man['playback']:g} speed, released {man['release_t']:g} s into each drop, "
          f"{shown:.1f} s of physics shown per drop; on screen the split comes {pair['split_t'] / man['playback']:.1f} s after release and both "
          f"bobs are settled {max(pair['settle_t']) / man['playback']:.1f} s after release")
    return {"mags": mags, "release": release, "pair": pair, "gap": gap, "split_t": pair["split_t"], "names": names}


class Renderer:
    def __init__(self, man: dict, meas: dict):
        self.man, self.meas = man, meas
        self.fps = man["fps"]
        font = os.environ["SEED_ZERO_FONT"]
        self.font = ImageFont.truetype(font, 40)
        self.font_small = ImageFont.truetype(font, 32)
        self.font_big = ImageFont.truetype(font, 56)
        self.font_title = ImageFont.truetype(font, 56)
        self.px_per_m = TABLE["half_px"] / man["view_half_width"]
        names = meas["names"]
        self.payoff = man["payoff_text"].format(a=names[meas["pair"]["final"][0]], b=names[meas["pair"]["final"][1]])
        widths = {"overlay@34": (ImageFont.truetype(font, 34), man["overlay"])}
        for j, line in enumerate(man["title"].split("|")):
            widths[f"title line {j + 1}@56"] = (self.font_title, line)
        for j, line in enumerate(self.payoff.split("|")):
            widths[f"payoff line {j + 1}@40"] = (self.font, line.strip())
        widths["label@40"] = (self.font, "two pendulums, from above")
        print("text widths: " + ", ".join(f"{k} {f.getlength(s):.0f} px" for k, (f, s) in widths.items()))
        # Loop check: the last frame must match the first (both bobs held at the release point, title up).
        total = int(round(man["scene_duration"] * self.fps))
        a, b = self.frame_at(0).astype(int), self.frame_at(total - 1).astype(int)
        print(f"loop check: mean abs pixel difference between frame 0 and frame {total - 1} is {np.abs(a - b).mean():.3f}")

    def px(self, x: float, y: float) -> tuple[float, float]:
        return TABLE["cx"] + x * self.px_per_m, TABLE["cy"] - y * self.px_per_m

    def strip_x(self, gap_m: float) -> float:
        lo, hi = math.log10(0.0001), math.log10(0.2)
        u = (math.log10(max(gap_m, 0.0001)) - lo) / (hi - lo)
        return STRIP["x0"] + max(0.0, min(1.0, u)) * (STRIP["x1"] - STRIP["x0"])

    def drop_state(self, t: float):
        """Video time -> (drop index, sample index into the run, reset fraction, physics seconds since release)."""
        man = self.man
        k = int(t // man["drop_period"])
        tau = t - k * man["drop_period"]
        reset_start = man["drop_period"] - man["reset_dur"]
        if tau < man["release_t"]:
            return k, 0, 0.0, 0.0
        held = min(tau, reset_start) - man["release_t"]
        f = min(int(round(held * self.fps)), len(self.meas["pair"]["pos"]) - 1)
        u = smoothstep((tau - reset_start) / man["reset_dur"]) if tau >= reset_start else 0.0
        return k, f, u, held * man["playback"]

    def frame_at(self, fidx: int) -> np.ndarray:
        man, m = self.man, self.meas
        t = fidx / self.fps
        pos, names = m["pair"]["pos"], m["names"]
        img = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(img)
        k, f, u, phys_t = self.drop_state(t)
        n_drops = int(round(man["scene_duration"] / man["drop_period"]))
        last = k >= n_drops - 1
        if t < man["title_until"]:
            title_alpha = 1.0 if t < man["title_until"] - 0.4 else (man["title_until"] - t) / 0.4
        elif last and u > 0:
            title_alpha = u
        else:
            title_alpha = 0.0
        # The header shares its band with the title, so it is hidden whenever the title shows.
        hud_alpha = 0.0 if title_alpha > 0.02 else 1.0

        def shade(col, alpha):
            return tuple(int(c * alpha + BG[j] * (1 - alpha)) for j, c in enumerate(col))

        # Table edge, then the trails, then the magnets on top of them.
        cx, cy, hp = TABLE["cx"], TABLE["cy"], TABLE["half_px"]
        d.rectangle((cx - hp, cy - hp, cx + hp, cy + hp), outline=WIRE, width=3)
        # Trails: dim for the whole drop, bright for the last second; they fade out during the reset.
        for b, col in ((0, BOB_A), (1, BOB_B)):
            pts = [self.px(*pos[j, b]) for j in range(0, f + 1, 2)]
            if len(pts) > 1 and u < 0.9:
                d.line(pts, fill=shade(col, 0.22 * (1 - u)), width=3, joint="curve")
            recent = [self.px(*pos[j, b]) for j in range(max(0, f - self.fps), f + 1)]
            if len(recent) > 1 and u == 0:
                d.line(recent, fill=shade(col, 0.75), width=4, joint="curve")
        for i, mg in enumerate(m["mags"]):
            x, y = self.px(*mg)
            d.ellipse((x - 34, y - 34, x + 34, y + 34), fill=shade(MAGNETS[i], 0.35))
            d.ellipse((x - 22, y - 22, x + 22, y + 22), fill=MAGNETS[i])
            d.text((x, y + 72), names[i], font=self.font_small, fill=MAGNETS[i], anchor="mt")
        # Settled rings.
        for b, col in ((0, BOB_A), (1, BOB_B)):
            st = m["pair"]["settle_t"][b]
            if st is not None and phys_t >= st and u == 0:
                x, y = self.px(*m["mags"][m["pair"]["settle_mag"][b]])
                r = 52 + 10 * b
                d.ellipse((x - r, y - r, x + r, y + r), outline=col, width=5)
        # Release mark, bobs (during the reset they glide back to the release point).
        rx, ry = self.px(*m["release"])
        d.line((rx - 14, ry, rx + 14, ry), fill=MUTED, width=3)
        d.line((rx, ry - 14, rx, ry + 14), fill=MUTED, width=3)
        r = 22
        for b, col in ((0, BOB_A), (1, BOB_B)):
            x, y = self.px(*(pos[f, b] * (1 - u) + pos[0, b] * u))
            if b == 0:
                d.ellipse((x - r, y - r, x + r, y + r), fill=col)
            else:
                d.ellipse((x - r, y - r, x + r, y + r), outline=col, width=6)
        # Labels.
        if title_alpha > 0.02:
            for j, line in enumerate(man["title"].split("|")):
                d.text((W / 2, 168 + j * 58), line, font=self.font_title, fill=shade(TEXT, title_alpha), anchor="mm")
        if hud_alpha > 0.02:
            d.text((60, TABLE["label_y"]), "two pendulums, from above", font=self.font, fill=shade(TEAL, hud_alpha), anchor="lm")
            d.text((W - 60, TABLE["label_y"]), f"{phys_t:.1f} s", font=self.font_big, fill=shade(TEXT, hud_alpha), anchor="rm")
        # Gap strip on a log scale.
        gap = float(m["gap"][f]) if u == 0 else float(m["gap"][0])
        sy = STRIP["y"]
        d.text((60, STRIP["label_y"]), "gap between the pendulums", font=self.font, fill=TEAL, anchor="lm")
        d.line((STRIP["x0"], sy, STRIP["x1"], sy), fill=WIRE, width=4)
        for g_, lab in ((0.0001, "0.1 mm"), (0.001, "1 mm"), (0.01, "1 cm"), (0.1, "10 cm")):
            x = self.strip_x(g_)
            d.line((x, sy - 12, x, sy + 12), fill=MUTED, width=3)
            d.text((x, sy + 22), lab, font=self.font_small, fill=MUTED, anchor="mt")
        xb = self.strip_x(man["bob_diameter"])
        d.line((xb, sy - 40, xb, sy - 16), fill=GOLD, width=4)
        d.text((xb, sy - 46), "one ball width", font=self.font_small, fill=GOLD, anchor="mb")
        xg = self.strip_x(gap)
        d.line((STRIP["x0"], sy, xg, sy), fill=TEXT, width=10)
        d.ellipse((xg - 12, sy - 12, xg + 12, sy + 12), fill=TEXT)
        if gap < 0.001:
            gap_txt = f"{gap * 1000:.2f} mm"
        elif gap < 0.01:
            gap_txt = f"{gap * 1000:.1f} mm"
        else:
            gap_txt = f"{gap * 100:.1f} cm"
        d.text((W - 60, STRIP["label_y"]), gap_txt, font=self.font_big, fill=GOLD if gap >= man["bob_diameter"] else TEXT, anchor="rm")
        split = m["split_t"]
        if split is not None and u == 0 and phys_t >= split:
            d.text((W / 2, sy + 90), f"split at {split:.1f} s", font=self.font, fill=GOLD, anchor="mm")
        # Payoff: from the moment both bobs first settle, held to the final reset.
        both = [st for st in m["pair"]["settle_t"] if st is not None]
        payoff_t = man["release_t"] + max(both) / man["playback"] if len(both) == 2 else None
        payoff_end = man["scene_duration"] - man["reset_dur"]
        if payoff_t is not None and payoff_t <= t < payoff_end:
            alpha = min(1.0, (t - payoff_t) / man["payoff_hold"], (payoff_end - t) / man["payoff_hold"])
            for j, line in enumerate(self.payoff.split("|")):
                d.text((W / 2, PAYOFF_Y - 32 + j * 64), line.strip(), font=self.font, fill=shade(GOLD, alpha), anchor="mm")
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
    man = json.loads((ROOT / "projects/magpendulum/manifest.json").read_text())
    meas = measure(man, with_map="--no-map" not in sys.argv)
    if "--measure-only" in sys.argv:
        return
    if "--frames" in sys.argv:
        times = [float(v) for v in sys.argv[sys.argv.index("--frames") + 1].split(",")]
        r = Renderer(man, meas)
        for tv in times:
            Image.fromarray(r.frame_at(int(round(tv * man["fps"])))).save(ROOT / f"media/magpendulum/smoke-{tv}.png")
        print("smoke frames: " + ", ".join(f"{tv}" for tv in times))
        return
    Renderer(man, meas).render(ROOT / "media/magpendulum/footage.mp4")


if __name__ == "__main__":
    main()
