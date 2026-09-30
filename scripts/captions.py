#!/usr/bin/env python3
"""Emit an FFmpeg video filter script: timed captions plus the seed overlay.

usage: captions.py [--voice VOICE_WAV] NARRATION_FILE VOICE_DURATION
                   VOICE_OFFSET OVERLAY_TEXT [CAPTION_Y]

Caption timing is proportional to word count across the voice duration.
With --voice the timing follows the pauses in the voice wav instead:
ffmpeg silencedetect finds the pauses, a monotone dynamic program matches
them to the punctuation marks in the narration, and word count spreads
the time only between matched pauses. Without --voice, or when no pause
can be matched, the plain word-count timing is used and stderr says so.
CAPTION_Y is the caption top as a fraction of the frame height (0.70 by
default); a project whose layout needs the band elsewhere sets it in its
manifest as caption_y.
The filter script goes to stdout and is used with ffmpeg -/filter:v. One
summary line goes to stderr.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys

MAX_CHARS = 20  # at fontsize 64 this keeps lines well inside 1080 px
SILENCE_FILTER = "silencedetect=n=-35dB:d=0.12"  # the pause signal of voice-timing.py
EDGE_TOLERANCE = 0.05  # s: a silence this close to a wav edge is leading or trailing
BOUNDARY_MARKS = ".!?,;:"  # Piper pauses after each of these
TRAILING_QUOTES = "\"'`)]}’”»"
# Squared-fraction cost of leaving a detected pause unmatched. The three
# day-32 voices keep every real pause from 7e-4 up; a spurious pause is
# still left alone unless a free boundary sits within about three words.
UNMATCHED_PENALTY = 2e-3
USAGE = ("usage: captions.py [--voice VOICE_WAV] NARRATION_FILE VOICE_DURATION "
         "VOICE_OFFSET OVERLAY [CAPTION_Y]")


def escape(text: str) -> str:
    # drawtext escaping: backslash, quote, colon, comma, semicolon. The
    # filters use expansion=none, so a percent sign needs no escape.
    for char, repl in (
        ("\\", "\\\\"),
        ("'", "’"),
        (":", "\\:"),
        (",", "\\,"),
        (";", "\\;"),
    ):
        text = text.replace(char, repl)
    return text


def chunks(text: str) -> list[list[str]]:
    out: list[list[str]] = []
    for sentence in re.split(r"(?<=[.!?])\s+", text.strip()):
        chunk: list[str] = []
        length = 0
        for word in sentence.split():
            if chunk and length + 1 + len(word) > MAX_CHARS:
                out.append(chunk)
                chunk, length = [], 0
            chunk.append(word)
            length += (1 if length else 0) + len(word)
        if chunk:
            out.append(chunk)
    return out


def word_count_spans(parts: list[list[str]], voice_dur: float, offset: float) -> list[tuple[float, float]]:
    """Plain timing: each chunk gets voice time in proportion to its words."""
    total_words = sum(len(c) for c in parts)
    spans = []
    clock = offset
    for chunk in parts:
        span = voice_dur * len(chunk) / total_words
        spans.append((clock, clock + span))
        clock += span
    return spans


def detect_silences(wav: str) -> tuple[list[float], list[float]] | None:
    """Run ffmpeg silencedetect on the wav; (starts, ends) in wav time, or None."""
    try:
        run = subprocess.run(
            ["ffmpeg", "-i", wav, "-af", SILENCE_FILTER, "-f", "null", "-"],
            stdin=subprocess.DEVNULL, capture_output=True, text=True,
        )
    except OSError:
        return None
    if run.returncode != 0:
        return None
    starts = [float(m) for m in re.findall(r"silence_start: (-?[\d.]+)", run.stderr)]
    ends = [float(m) for m in re.findall(r"silence_end: (-?[\d.]+)", run.stderr)]
    return starts, ends


def split_silences(starts: list[float], ends: list[float], duration: float
                   ) -> tuple[float, float, list[tuple[float, float]]]:
    """Speech start, speech end and the interior pauses, all in wav time.

    A trailing silence may have no end; a leading silence starts at 0.
    """
    silences = []
    for k, start in enumerate(starts):
        end = ends[k] if k < len(ends) else duration
        silences.append((start, min(end, duration)))
    silences.sort()
    speech_start, speech_end = 0.0, duration
    interior = []
    for start, end in silences:
        if start <= EDGE_TOLERANCE:
            speech_start = max(speech_start, end)
        elif end >= duration - EDGE_TOLERANCE:
            speech_end = min(speech_end, start)
        elif end > start:
            interior.append((start, end))
    return speech_start, speech_end, interior


def boundaries(words: list[str]) -> list[int]:
    """Indices of the words that close a phrase (they end with a boundary mark)."""
    marks = tuple(BOUNDARY_MARKS)
    return [k for k, word in enumerate(words[:-1]) if word.rstrip(TRAILING_QUOTES).endswith(marks)]


def align(bounds: list[int], pauses: list[tuple[float, float]], total_words: int,
          speech_start: float, speech_end: float, penalty: float = UNMATCHED_PENALTY
          ) -> list[tuple[int, int]]:
    """Match the detected pauses to the text boundaries, in order.

    Returns (pause index, boundary index) pairs, strictly increasing in
    both, that minimise the sum over the segments between anchors of
    (word fraction - speech time fraction)^2 plus a penalty for every
    pause left unmatched. Speech time excludes all pause durations.
    """
    M, K = len(pauses), len(bounds)
    if not M or not K or total_words <= 0:
        return []
    # Speech clock: wav time with the pause durations removed, so a pause
    # is one instant on it. Index 0 is the speech start, M + 1 the end.
    clock = [speech_start]
    removed = 0.0
    for start, end in pauses:
        clock.append(start - removed)
        removed += end - start
    clock.append(speech_end - removed)
    total_speech = clock[-1] - clock[0]
    if total_speech <= 0:
        return []
    last_word = [-1] + list(bounds) + [total_words - 1]

    def segment_cost(i0: int, j0: int, i1: int, j1: int) -> float:
        word_frac = (last_word[j1] - last_word[j0]) / total_words
        time_frac = (clock[i1] - clock[i0]) / total_speech
        return (word_frac - time_frac) ** 2

    inf = float("inf")
    cost = [[inf] * (K + 2) for _ in range(M + 2)]
    back: list[list[tuple[int, int] | None]] = [[None] * (K + 2) for _ in range(M + 2)]
    cost[0][0] = 0.0
    for i in range(1, M + 2):
        columns = range(1, K + 1) if i <= M else (K + 1,)
        for j in columns:
            best, arg = inf, None
            for i0 in range(i):
                skipped = penalty * (i - i0 - 1)
                row = cost[i0]
                for j0 in range(j):
                    if row[j0] == inf:
                        continue
                    c = row[j0] + skipped + segment_cost(i0, j0, i, j)
                    if c < best:
                        best, arg = c, (i0, j0)
            cost[i][j] = best
            back[i][j] = arg
    pairs = []
    i, j = M + 1, K + 1
    while (i, j) != (0, 0):
        step = back[i][j]
        if step is None:
            return []
        i, j = step
        if i:
            pairs.append((i - 1, j - 1))
    pairs.reverse()
    return pairs


def word_starts(total_words: int, bounds: list[int], pauses: list[tuple[float, float]],
                pairs: list[tuple[int, int]], speech_start: float, speech_end: float) -> list[float]:
    """Wav-time start of every word: piecewise linear between the anchors."""
    starts = [0.0] * total_words

    def fill(first: int, last: int, t0: int, t1: float) -> None:
        n = last - first + 1
        for w in range(first, last + 1):
            starts[w] = t0 + (w - first) * (t1 - t0) / n

    first, t0 = 0, speech_start
    for pause_index, bound_index in pairs:
        last = bounds[bound_index]
        fill(first, last, t0, pauses[pause_index][0])
        first, t0 = last + 1, pauses[pause_index][1]
    fill(first, total_words - 1, t0, speech_end)
    return starts


def aligned_spans(wav: str, parts: list[list[str]], voice_dur: float, offset: float
                  ) -> tuple[list[tuple[float, float]] | None, str]:
    """Chunk spans aligned to the pauses in the wav, or (None, reason)."""
    words = [w for chunk in parts for w in chunk]
    detected = detect_silences(wav)
    if detected is None:
        return None, "ffmpeg silencedetect failed"
    speech_start, speech_end, pauses = split_silences(*detected, voice_dur)
    if not pauses:
        return None, "no interior pause found"
    bounds = boundaries(words)
    pairs = align(bounds, pauses, len(words), speech_start, speech_end)
    if not pairs:
        return None, "no pause matched a text boundary"
    starts = word_starts(len(words), bounds, pauses, pairs, speech_start, speech_end)
    chunk_starts = []
    first = 0
    for chunk in parts:
        chunk_starts.append(offset + starts[first])
        first += len(chunk)
    ends = chunk_starts[1:] + [offset + voice_dur]
    return list(zip(chunk_starts, ends)), f"{len(pauses)} pauses detected, {len(pairs)} matched"


def main() -> None:
    argv = sys.argv[1:]
    voice = None
    for k, arg in enumerate(argv):
        if arg == "--voice" and k + 1 < len(argv):
            voice = argv[k + 1]
            del argv[k:k + 2]
            break
        if arg.startswith("--voice="):
            voice = arg[len("--voice="):]
            del argv[k]
            break
    if len(argv) not in (4, 5):
        sys.exit(USAGE)
    narration_file, voice_dur, offset, overlay = argv[:4]
    voice_dur, offset = float(voice_dur), float(offset)
    caption_y = float(argv[4]) if len(argv) == 5 else 0.70
    font = os.environ["SEED_ZERO_FONT"]

    with open(narration_file) as handle:
        text = handle.read()
    parts = chunks(text)
    spans = word_count_spans(parts, voice_dur, offset)
    if voice is not None:
        aligned, note = aligned_spans(voice, parts, voice_dur, offset)
        if aligned is None:
            print(f"captions: word-count timing ({note})", file=sys.stderr)
        else:
            shift = max(abs(a[0] - b[0]) for a, b in zip(aligned, spans))
            print(f"captions: {note}, max chunk start shift {shift:.3f} s "
                  "against word-count timing", file=sys.stderr)
            spans = aligned

    filters = [
        f"drawtext=fontfile={font}:expansion=none:text='{escape(overlay)}'"
        ":fontsize=34:fontcolor=0x5cc8a5@0.9:x=(w-text_w)/2:y=96"
    ]
    for chunk, (start, end) in zip(parts, spans):
        line = escape(" ".join(chunk))
        filters.append(
            f"drawtext=fontfile={font}:expansion=none:text='{line}'"
            ":fontsize=64:fontcolor=white:borderw=6:bordercolor=black@0.9"
            f":x=(w-text_w)/2:y=h*{caption_y:.3f}"
            f":enable='between(t,{start:.3f},{end:.3f})'"
        )

    sys.stdout.write(",\n".join(filters) + "\n")


if __name__ == "__main__":
    main()
