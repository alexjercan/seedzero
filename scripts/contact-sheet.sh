#!/usr/bin/env bash
set -euo pipefail

# Render a one-frame-per-second contact sheet for inspection.

if [ $# -ne 2 ]; then
    echo "usage: contact-sheet.sh VIDEO OUT_PNG" >&2
    exit 2
fi

video=$1
out=$2

duration=$(ffprobe -v error -show_entries format=duration \
    -of default=noprint_wrappers=1:nokey=1 "$video")
cols=8
rows=$(python3 -c "import math; print(max(1, math.ceil(math.ceil($duration) / $cols)))")

ffmpeg -y -v error -i "$video" \
    -vf "fps=1,scale=202:360,tile=${cols}x${rows}:padding=4:color=0x0b0e12" \
    -frames:v 1 "$out"
echo "contact sheet: $out (${cols}x${rows} at 1 fps)"
