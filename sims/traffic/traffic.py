#!/usr/bin/env python3
"""Traffic jam from nothing: identical cars on a ring road, no obstacle.

Twenty two cars start evenly spaced on a 230 m ring, the Sugiyama 2008
layout, with a seeded jitter of at most half a metre. Every car follows the
optimal velocity model (Bando 1995): it accelerates toward the speed that
its headway allows, with one reaction sensitivity. Nothing else happens.
The sim measures when the first car stops, how fast the jam then travels
backward around the ring, and checks that no two cars ever touch.

usage: traffic.py [--measure-only] [--dt SECONDS]
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
ROAD = (28, 34, 42)
LANE = (52, 60, 72)
TEXT = (216, 222, 230)
MUTED = (138, 148, 163)
ACCENT = (92, 200, 165)
FAST = np.array((92, 200, 165), dtype=np.float32)
SLOW = np.array((240, 176, 84), dtype=np.float32)
STOP = np.array((232, 84, 84), dtype=np.float32)

RING_CX, RING_CY, RING_R = 540, 640, 400
ROAD_HALF = 34
CAR_R = 17
READOUT_Y = 1150
BAND_X0, BAND_X1 = 60, 1020
BAND_Y0, BAND_Y1 = 1470, 1820
PAYOFF_Y = 1875


def idm_params(man: dict) -> dict:
    return {"v0": man["desired_kmh"] / 3.6, "T": man["time_headway_s"],
            "a": man["accel_mps2"], "b": man["brake_mps2"],
            "s0": man["min_gap_m"], "l": man["car_len_m"]}


def equilibrium_speed(gap: float, p: dict) -> float:
    lo, hi = 0.0, p["v0"]
    for _ in range(80):
        v = 0.5 * (lo + hi)
        want = (p["s0"] + v * p["T"]) / gap
        if 1 - (v / p["v0"]) ** 4 - want * want > 0:
            lo = v
        else:
            hi = v
    return 0.5 * (lo + hi)


def headways(x: np.ndarray, L: float) -> np.ndarray:
    return (np.roll(x, -1) - x) % L


def rhs(state: np.ndarray, p: dict, L: float) -> np.ndarray:
    """Intelligent driver model (Treiber 2000): gap and closing speed."""
    x, v = state
    gap = headways(x, L) - p["l"]
    dv = v - np.roll(v, -1)
    s_star = p["s0"] + v * p["T"] + v * dv / (2 * math.sqrt(p["a"] * p["b"]))
    acc = p["a"] * (1 - (v / p["v0"]) ** 4 - (s_star / gap) ** 2)
    return np.stack([v, acc])


def simulate(man: dict, dt: float) -> dict:
    p = idm_params(man)
    L, n = man["ring_m"], man["cars"]
    rng = np.random.RandomState(man["seed"])
    x = np.arange(n) * L / n + rng.uniform(-man["jitter_m"], man["jitter_m"], n)
    x -= x.min()
    v_eq = equilibrium_speed(L / n - p["l"], p)
    v = np.full(n, v_eq)
    clamps = 0
    state = np.stack([x, v])
    steps = int(round(man["sim_seconds"] / dt))
    sample_every = max(1, int(round(0.1 / dt)))
    ts, xs, vs = [], [], []
    min_h = math.inf
    for k in range(steps + 1):
        if k % sample_every == 0:
            ts.append(k * dt)
            xs.append(state[0] % L)
            vs.append(state[1].copy())
        k1 = rhs(state, p, L)
        k2 = rhs(state + 0.5 * dt * k1, p, L)
        k3 = rhs(state + 0.5 * dt * k2, p, L)
        k4 = rhs(state + dt * k3, p, L)
        state = state + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        if (state[1] < 0).any():
            clamps += int((state[1] < 0).sum())
            state[1] = np.maximum(state[1], 0.0)
        min_h = min(min_h, float(headways(state[0], L).min()))
    return {"t": np.array(ts), "x": np.array(xs), "v": np.array(vs),
            "v_eq": v_eq, "min_h": min_h, "p": p, "clamps": clamps}


def stop_events(run: dict, stop_v: float, go_v: float) -> list[tuple[int, float, float]]:
    """(car, time, position) each time a car's speed drops below stop_v.
    A car must climb back above go_v before it can count as stopping again,
    so creeping inside one jam is one stop, not several."""
    v, x, t = run["v"], run["x"], run["t"]
    n = v.shape[1]
    stopped = np.zeros(n, dtype=bool)
    events = []
    for k in range(len(t)):
        newly = (v[k] < stop_v) & ~stopped
        for i in np.nonzero(newly)[0]:
            events.append((int(i), float(t[k]), float(x[k, i])))
        stopped = (stopped | newly) & ~(v[k] > go_v)
    return events


def stopped_clusters(v_row: np.ndarray, stop_v: float) -> list[list[int]]:
    """Groups of consecutive stopped cars (by car index, wrapping round)."""
    n = len(v_row)
    stopped = v_row < stop_v
    if stopped.all():
        return [list(range(n))]
    if not stopped.any():
        return []
    # Start scanning just after a moving car so no cluster is split by the wrap.
    start = int(np.argmin(stopped))
    clusters, cur = [], []
    for k in range(n):
        i = (start + k) % n
        if stopped[i]:
            cur.append(i)
        elif cur:
            clusters.append(cur)
            cur = []
    if cur:
        clusters.append(cur)
    return clusters


def track_jam(run: dict, L: float, stop_v: float, t_from: float, t_to: float) -> dict:
    """Follow the back of the main jam: at t_from take the largest group of
    consecutive stopped cars, then at each later sample pick the group whose
    rearmost car is nearest to where the tracked back was. Unwrap and fit a
    straight line: the slope is the jam's speed (negative = backward)."""
    t, x, v = run["t"], run["x"], run["v"]
    k0 = int(np.searchsorted(t, t_from))
    clusters = stopped_clusters(v[k0], stop_v)
    if not clusters:
        return {}
    main = max(clusters, key=len)
    back = main[0]
    pos = x[k0, back]
    ts, unwrapped, sizes = [t[k0]], [pos], [len(main)]
    for k in range(k0 + 1, len(t)):
        if t[k] > t_to + 1e-9:
            break
        clusters = stopped_clusters(v[k], stop_v)
        if not clusters:
            continue
        cand = []
        for c in clusters:
            d = (x[k, c[0]] - pos + L / 2) % L - L / 2
            cand.append((abs(d), d, c))
        _, d, c = min(cand)
        pos = (pos + d) % L
        unwrapped.append(unwrapped[-1] + d)
        ts.append(t[k])
        sizes.append(len(c))
    ts, unwrapped = np.array(ts), np.array(unwrapped)
    slope, icpt = np.polyfit(ts, unwrapped, 1)
    resid = unwrapped - (slope * ts + icpt)
    return {"mps": float(slope), "kmh": float(slope * 3.6),
            "t0": float(ts[0]), "t1": float(ts[-1]),
            "travel_m": float(unwrapped[-1] - unwrapped[0]),
            "max_resid_m": float(np.abs(resid).max()),
            "samples": len(ts), "size_min": int(min(sizes)), "size_max": int(max(sizes)),
            "size_mean": float(np.mean(sizes))}


def front_speeds(events, n: int, L: float, window: float, t_from: float) -> np.ndarray:
    """Backward speed of the stop front: for each stop, pair it with the most
    recent stop of the car directly ahead and divide the distance by the
    delay. Pairs where the car ahead last stopped more than a quarter ring
    away belong to a different passage and are dropped, and so are stops
    before t_from, while the jam is still forming. Positive numbers mean
    the front moves against traffic."""
    last = {}
    speeds = []
    for car, t, x in events:
        ahead = (car + 1) % n
        if ahead in last:
            t_a, x_a = last[ahead]
            dt = t - t_a
            dx = (x_a - x) % L
            if 0 < dt <= window and dx < L / 4 and t >= t_from:
                speeds.append(dx / dt)
        last[car] = (t, x)
    return np.array(speeds)


def measure(man: dict, dt: float, quiet: bool = False) -> dict:
    L, n = man["ring_m"], man["cars"]
    run = simulate(man, dt)
    t, x, v = run["t"], run["x"], run["v"]
    stop_v = man["stop_kmh"] / 3.6
    stopped = v.min(axis=1) < stop_v
    first_stop_i = int(np.argmax(stopped)) if stopped.any() else -1
    out = {"v_eq_kmh": run["v_eq"] * 3.6, "min_h": run["min_h"],
           "first_stop_s": float(t[first_stop_i]) if first_stop_i >= 0 else None}
    assert run["min_h"] > man["car_len_m"], f"cars touched: min headway {run['min_h']:.2f} m"
    if first_stop_i >= 0:
        events = stop_events(run, stop_v, man["go_kmh"] / 3.6)
        settle = t[first_stop_i] + man["settle_s"]
        speeds = front_speeds(events, n, L, man["pair_window_s"], settle)
        out["stop_events"] = len(events)
        out["front_pairs"] = len(speeds)
        out["front_mps"] = float(speeds.mean())
        out["front_kmh"] = float(speeds.mean() * 3.6)
        out["front_median_kmh"] = float(np.median(speeds) * 3.6)
        out["front_min_kmh"] = float(speeds.min() * 3.6)
        out["front_max_kmh"] = float(speeds.max() * 3.6)
        out["min_v_kmh"] = float(v.min() * 3.6)
        after = t >= t[first_stop_i]
        out["max_v_after_kmh"] = float(v[after].max() * 3.6)
        out["mean_v_after_kmh"] = float(v[after].mean() * 3.6)
        stops_per_car = np.bincount([e[0] for e in events], minlength=n)
        out["stops_per_car_min"] = int(stops_per_car.min())
        out["stops_per_car_max"] = int(stops_per_car.max())
        out["jam"] = track_jam(run, L, stop_v, settle, settle + man["track_s"])
        out["front_laps"] = float(-out["jam"]["mps"] * (t[-1] - t[first_stop_i]) / L)
        out["jam_after"] = track_jam(run, L, stop_v, settle + man["track_s"], t[-1])
        win = (t >= settle) & (t <= settle + man["track_s"])
        out["mean_v_window_kmh"] = float(v[win].mean() * 3.6)
        out["max_v_window_kmh"] = float(v[win].max() * 3.6)
        out["car_laps_after"] = float(v[after].mean() * (t[-1] - t[first_stop_i]) / L)
    if not quiet:
        p = run["p"]
        print(f"{n} cars on a {L:.0f} m ring, seed {man['seed']}, spacing jitter <= {man['jitter_m']} m, dt {dt}")
        print(f"mean headway {L / n:.2f} m, gap {L / n - p['l']:.2f} m, "
              f"equilibrium speed {out['v_eq_kmh']:.1f} km/h")
        print(f"IDM: desired {p['v0'] * 3.6:.0f} km/h, time headway {p['T']} s, "
              f"accel {p['a']} m/s2, brake {p['b']} m/s2, min gap {p['s0']} m, car {p['l']} m")
        print(f"min headway over the run {out['min_h']:.2f} m (car length {man['car_len_m']} m), "
              f"stopped-car holds {run['clamps']}")
        if out["first_stop_s"] is None:
            print("no car ever stopped")
        else:
            print(f"first car below {man['stop_kmh']} km/h at t = {out['first_stop_s']:.1f} s")
            print(f"stop events {out['stop_events']}, per car {out['stops_per_car_min']}-"
                  f"{out['stops_per_car_max']}; front pairs after {man['settle_s']} s of settling: "
                  f"{out['front_pairs']}")
            print(f"stop front moves backward at {out['front_mps']:.3f} m/s = {out['front_kmh']:.2f} km/h "
                  f"(median {out['front_median_kmh']:.2f}, range {out['front_min_kmh']:.2f} to "
                  f"{out['front_max_kmh']:.2f})")
            j = out["jam"]
            print(f"main jam, back car tracked from {j['t0']:.1f} s to {j['t1']:.1f} s "
                  f"({j['samples']} samples): moved {j['travel_m']:.1f} m, "
                  f"slope {j['mps']:.3f} m/s = {j['kmh']:.2f} km/h, max residual {j['max_resid_m']:.2f} m, "
                  f"stopped cars in it {j['size_min']}-{j['size_max']} (mean {j['size_mean']:.1f})")
            j = out["jam_after"]
            print(f"same tracker over the rest of the run, {j['t0']:.1f} s to {j['t1']:.1f} s: "
                  f"{j['kmh']:.2f} km/h, max residual {j['max_resid_m']:.2f} m")
            print(f"same window, all cars: average {out['mean_v_window_kmh']:.1f} km/h, "
                  f"max {out['max_v_window_kmh']:.1f} km/h (equilibrium before the jam {out['v_eq_kmh']:.1f})")
            print(f"after the first stop: cars average {out['mean_v_after_kmh']:.1f} km/h, "
                  f"max {out['max_v_after_kmh']:.1f} km/h, min {out['min_v_kmh']:.1f} km/h")
            print(f"front laps backward after first stop: {out['front_laps']:.2f}; "
                  f"car laps forward: {out['car_laps_after']:.2f}")
    out["run"] = run
    return out


def speed_color(v_kmh: np.ndarray) -> np.ndarray:
    v = np.clip(v_kmh / 20.0, 0.0, 1.0)[..., None]
    lo = STOP + (SLOW - STOP) * np.clip(v * 2, 0, 1)
    hi = SLOW + (FAST - SLOW) * np.clip(v * 2 - 1, 0, 1)
    return np.where(v < 0.5, lo, hi)


class Renderer:
    def __init__(self, man: dict, meas: dict):
        self.man, self.meas = man, meas
        self.run = meas["run"]
        self.L = man["ring_m"]
        self.fps = man["fps"]
        font = os.environ["SEED_ZERO_FONT"]
        self.font = ImageFont.truetype(font, 40)
        self.font_small = ImageFont.truetype(font, 32)
        self.sim_span = man["scene_duration"] * man["time_factor"]
        self.band = np.zeros((BAND_Y1 - BAND_Y0, BAND_X1 - BAND_X0, 3), dtype=np.uint8)
        self.band[:] = ROAD
        self.band_drawn = 0

    def sample_at(self, ts: float) -> tuple[np.ndarray, np.ndarray]:
        i = min(len(self.run["t"]) - 1, int(round(ts / 0.1)))
        return self.run["x"][i], self.run["v"][i]

    def draw_band_to(self, ts: float) -> None:
        h, w = self.band.shape[:2]
        n_samples = min(len(self.run["t"]), int(ts / 0.1) + 1)
        while self.band_drawn < n_samples:
            i = self.band_drawn
            row = int(self.run["t"][i] / self.sim_span * (h - 1))
            if 0 <= row < h:
                cols = (self.run["x"][i] / self.L * (w - 1)).astype(int)
                colors = speed_color(self.run["v"][i] * 3.6).astype(np.uint8)
                for c, col in zip(cols, colors):
                    self.band[row:row + 2, max(0, c - 1):c + 2] = col
            self.band_drawn += 1

    def frame_at(self, tv: float) -> np.ndarray:
        man = self.man
        ts = tv * man["time_factor"]
        x, v = self.sample_at(ts)
        self.draw_band_to(ts)
        img = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(img)
        # Ring road.
        d.ellipse((RING_CX - RING_R - ROAD_HALF, RING_CY - RING_R - ROAD_HALF,
                   RING_CX + RING_R + ROAD_HALF, RING_CY + RING_R + ROAD_HALF), fill=ROAD)
        d.ellipse((RING_CX - RING_R + ROAD_HALF, RING_CY - RING_R + ROAD_HALF,
                   RING_CX + RING_R - ROAD_HALF, RING_CY + RING_R - ROAD_HALF), fill=BG)
        # Lane dashes.
        for k in range(48):
            a0 = 2 * math.pi * k / 48
            a1 = a0 + 2 * math.pi / 96
            d.arc((RING_CX - RING_R, RING_CY - RING_R, RING_CX + RING_R, RING_CY + RING_R),
                  math.degrees(a0), math.degrees(a1), fill=LANE, width=3)
        colors = speed_color(v * 3.6).astype(int)
        for xi, col in zip(x, colors):
            th = 2 * math.pi * xi / self.L
            cx = RING_CX + RING_R * math.cos(th)
            cy = RING_CY - RING_R * math.sin(th)
            d.ellipse((cx - CAR_R, cy - CAR_R, cx + CAR_R, cy + CAR_R), fill=tuple(col))
        # Readouts.
        v_kmh = v * 3.6
        d.text((60, READOUT_Y), f"clock {ts:5.1f} s", font=self.font, fill=MUTED, anchor="lm")
        slow = v_kmh.min()
        d.text((W - 60, READOUT_Y), f"slowest car {slow:4.1f} km/h",
               font=self.font, fill=tuple(speed_color(np.array([slow])).astype(int)[0]),
               anchor="rm")
        d.text((W / 2, READOUT_Y + 60),
               f"fastest car {v_kmh.max():4.1f} km/h   |   playing at {man['time_factor']:.0f}x",
               font=self.font_small, fill=MUTED, anchor="mm")
        # Space-time band.
        frame = np.asarray(img).copy()
        frame[BAND_Y0:BAND_Y1, BAND_X0:BAND_X1] = self.band
        row = int(ts / self.sim_span * (BAND_Y1 - BAND_Y0 - 1))
        row = min(BAND_Y1 - BAND_Y0 - 1, row)
        frame[BAND_Y0 + row:BAND_Y0 + row + 2, BAND_X0:BAND_X1] = TEXT
        img = Image.fromarray(frame)
        d = ImageDraw.Draw(img)
        d.text((BAND_X0, BAND_Y0 - 30), "position around the ring",
               font=self.font_small, fill=MUTED, anchor="lm")
        d.text((BAND_X1, BAND_Y0 - 30), "time runs down",
               font=self.font_small, fill=MUTED, anchor="rm")
        alpha = min(1.0, max(0.0, (tv - man["payoff_fade"]) / 0.6))
        if alpha > 0:
            shade = tuple(int(c * alpha + BG[i] * (1 - alpha)) for i, c in enumerate(ACCENT))
            d.text((W / 2, PAYOFF_Y),
                   f"the jam rolls backward at {-self.meas['jam']['kmh']:.1f} km/h",
                   font=self.font, fill=shade, anchor="mm")
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
            proc.stdin.write(self.frame_at(f / self.fps).tobytes())
            if f % 300 == 0:
                print(f"frame {f}/{total}", file=sys.stderr)
        proc.stdin.close()
        if proc.wait() != 0:
            raise RuntimeError("ffmpeg failed")
        print(f"footage: {out_path} ({total / self.fps:.2f}s at {self.fps} fps)")


def main() -> None:
    man = json.loads((ROOT / "projects/traffic/manifest.json").read_text())
    dt = man["dt"]
    if "--dt" in sys.argv:
        dt = float(sys.argv[sys.argv.index("--dt") + 1])
    meas = measure(man, dt)
    if "--measure-only" in sys.argv:
        return
    Renderer(man, meas).render(ROOT / "media/traffic/footage.mp4")


if __name__ == "__main__":
    main()
