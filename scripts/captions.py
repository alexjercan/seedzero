#!/usr/bin/env python3
"""Emit an FFmpeg video filter script: timed captions plus the seed overlay.

usage: captions.py NARRATION_FILE VOICE_DURATION VOICE_OFFSET OVERLAY_TEXT

Caption timing is proportional to word count across the voice duration.
The output goes to stdout and is used with ffmpeg -filter_script:v.
"""

from __future__ import annotations

import os
import re
import sys

MAX_CHARS = 20  # at fontsize 64 this keeps lines well inside 1080 px


def escape(text: str) -> str:
    # drawtext escaping: backslash, quote, colon, comma, semicolon.
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


def main() -> None:
    if len(sys.argv) != 5:
        sys.exit("usage: captions.py NARRATION_FILE VOICE_DURATION VOICE_OFFSET OVERLAY")
    narration_file, voice_dur, offset, overlay = sys.argv[1:5]
    voice_dur, offset = float(voice_dur), float(offset)
    font = os.environ["SEED_ZERO_FONT"]

    text = open(narration_file).read()
    parts = chunks(text)
    total_words = sum(len(c) for c in parts)

    filters = [
        f"drawtext=fontfile={font}:text='{escape(overlay)}'"
        ":fontsize=34:fontcolor=0x5cc8a5@0.9:x=(w-text_w)/2:y=96"
    ]
    clock = offset
    for chunk in parts:
        span = voice_dur * len(chunk) / total_words
        line = escape(" ".join(chunk))
        filters.append(
            f"drawtext=fontfile={font}:text='{line}'"
            ":fontsize=64:fontcolor=white:borderw=6:bordercolor=black@0.9"
            ":x=(w-text_w)/2:y=h*0.70"
            f":enable='between(t,{clock:.3f},{clock + span:.3f})'"
        )
        clock += span

    sys.stdout.write(",\n".join(filters) + "\n")


if __name__ == "__main__":
    main()
