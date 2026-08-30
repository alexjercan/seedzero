#!/usr/bin/env python3
"""Generate a deterministic, quiet background track for a short.

usage: music.py SEED DURATION OUT_WAV
"""

from __future__ import annotations

import sys
import wave
from pathlib import Path

import numpy as np

RATE = 48_000
ROOT_HZ = 110.0  # A2
# A minor pentatonic ratios, one octave up for the pluck voice.
PENTA = (1.0, 6 / 5, 4 / 3, 3 / 2, 9 / 5)


def tone(freq: float, t: np.ndarray) -> np.ndarray:
    wave_ = np.sin(2 * np.pi * freq * t)
    wave_ += 0.35 * np.sin(2 * np.pi * freq * 2 * t)
    return wave_


def render(seed: int, duration: float) -> np.ndarray:
    rng = np.random.RandomState(seed)
    n = int(duration * RATE)
    t = np.arange(n) / RATE
    out = np.zeros(n)

    # Drone pad: root and fifth with a slow amplitude swell.
    swell = 0.5 + 0.5 * np.sin(2 * np.pi * t / 16.0 - np.pi / 2)
    out += (0.050 + 0.030 * swell) * tone(ROOT_HZ, t)
    out += (0.035 + 0.020 * swell) * tone(ROOT_HZ * 1.5, t)

    # Sparse plucks on a half-second grid, seeded choices.
    step = 0.5
    for k in range(int(duration / step)):
        if rng.random_sample() < 0.35:
            continue
        start = int(k * step * RATE)
        freq = ROOT_HZ * 2 * PENTA[rng.randint(len(PENTA))]
        length = min(int(0.9 * RATE), n - start)
        if length <= 0:
            break
        tt = np.arange(length) / RATE
        env = np.exp(-4.5 * tt)
        out[start : start + length] += 0.055 * env * np.sin(2 * np.pi * freq * tt)

    # Gentle one-pole lowpass to keep it soft under narration.
    alpha = 0.15
    filtered = np.empty_like(out)
    acc = 0.0
    for i, x in enumerate(out):
        acc += alpha * (x - acc)
        filtered[i] = acc

    fade = min(n, RATE)
    filtered[:fade] *= np.linspace(0.0, 1.0, fade)
    filtered[-fade:] *= np.linspace(1.0, 0.0, fade)
    peak = np.max(np.abs(filtered))
    if peak > 0:
        filtered *= 0.30 / peak
    return filtered


def main() -> None:
    if len(sys.argv) != 4:
        sys.exit("usage: music.py SEED DURATION OUT_WAV")
    seed, duration, out_path = int(sys.argv[1]), float(sys.argv[2]), Path(sys.argv[3])
    samples = (render(seed, duration) * 32767).astype("<i2")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(out_path), "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(RATE)
        f.writeframes(samples.tobytes())
    print(f"music: seed={seed} duration={duration:.2f}s -> {out_path}")


if __name__ == "__main__":
    main()
