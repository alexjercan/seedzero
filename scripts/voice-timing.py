#!/usr/bin/env python3
"""Print where each spoken phrase lands in the video.

usage: voice-timing.py VOICE_WAV [VOICE_OFFSET]

Splits the voice track at its pauses (ffmpeg silencedetect, -35 dB for at
least 0.22 s), transcribes each piece with the local speech API and prints
the video time span of every piece (voice time plus the offset, 0.6 s by
default). Used to check that a payoff or a scene event lands on the words
that name it. Writes nothing but temporary pieces.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
import urllib.request

STT_API = os.environ.get("STT_API", "http://localhost:10301/inference")


def transcribe(path: str) -> str:
    boundary = "----seedzero"
    data = open(path, "rb").read()
    body = (
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"model\"\r\n\r\nwhisper-1\r\n"
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"p.wav\"\r\n"
        f"Content-Type: audio/wav\r\n\r\n"
    ).encode() + data + f"\r\n--{boundary}--\r\n".encode()
    req = urllib.request.Request(STT_API, data=body,
                                 headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.load(r)["text"].strip()


def main() -> None:
    wav = sys.argv[1]
    offset = float(sys.argv[2]) if len(sys.argv) > 2 else 0.6
    out = subprocess.run(["ffmpeg", "-i", wav, "-af", "silencedetect=n=-35dB:d=0.22", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                "-of", "default=noprint_wrappers=1:nokey=1", wav], capture_output=True, text=True).stdout)
    starts = [float(m) for m in re.findall(r"silence_start: ([\d.]+)", out)]
    ends = [float(m) for m in re.findall(r"silence_end: ([\d.]+)", out)]
    cuts = [0.0] + [(s + e) / 2 for s, e in zip(starts, ends)] + [dur]
    with tempfile.TemporaryDirectory() as tmp:
        for k in range(len(cuts) - 1):
            a, b = cuts[k], cuts[k + 1]
            piece = os.path.join(tmp, f"p{k}.wav")
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", wav, "-ss", f"{a:.3f}", "-to", f"{b:.3f}", piece], check=True)
            print(f"{a + offset:6.2f} - {b + offset:6.2f}  {transcribe(piece)}")
    print(f"voice {dur:.2f} s, ends at {dur + offset:.2f} s of video")


if __name__ == "__main__":
    main()
