#!/usr/bin/env bash
set -euo pipefail

# Compose a final short from a project folder: footage + voice + music +
# captions + seed overlay -> media/<name>/final.mp4 and a 540x960 preview.
# Inputs: media/<name>/footage.mp4, media/<name>/voice.wav,
# projects/<name>/manifest.json, projects/<name>/narration.txt.

if [ $# -ne 1 ]; then
    echo "usage: compose.sh NAME" >&2
    exit 2
fi

name=$1
root=$(dirname "$(readlink -f "$0")")/..
proj=$root/projects/$name
med=$root/media/$name
manifest=$proj/manifest.json

for f in "$manifest" "$proj/narration.txt" "$med/footage.mp4" "$med/voice.wav"; do
    [ -f "$f" ] || { echo "error: missing $f" >&2; exit 1; }
done

music_seed=$(jq -r .music_seed "$manifest")
music_gain=$(jq -r '.music_gain // 0.18' "$manifest")
voice_offset=$(jq -r '.voice_offset // 0.6' "$manifest")
overlay=$(jq -r .overlay "$manifest")

duration=$(ffprobe -v error -show_entries format=duration \
    -of default=noprint_wrappers=1:nokey=1 "$med/footage.mp4")
voice_dur=$(ffprobe -v error -show_entries format=duration \
    -of default=noprint_wrappers=1:nokey=1 "$med/voice.wav")

python3 "$root/scripts/music.py" "$music_seed" "$duration" "$med/music.wav"
python3 "$root/scripts/captions.py" "$proj/narration.txt" "$voice_dur" \
    "$voice_offset" "$overlay" >"$med/captions.filter"

offset_ms=$(python3 -c "print(round($voice_offset * 1000))")
ffmpeg -y -v error -i "$med/footage.mp4" -i "$med/voice.wav" -i "$med/music.wav" \
    -/filter:v "$med/captions.filter" \
    -filter_complex "[1:a]adelay=${offset_ms}|${offset_ms}[va];\
[2:a]volume=${music_gain}[ma];\
[va][ma]amix=inputs=2:duration=longest:normalize=0,alimiter=limit=0.9[a]" \
    -map 0:v -map '[a]' -c:v libx264 -crf 18 -preset medium -pix_fmt yuv420p \
    -c:a aac -b:a 192k -shortest "$med/final.mp4"

ffmpeg -y -v error -i "$med/final.mp4" \
    -vf scale=540:960 -r 30 -c:v libx264 -crf 28 -preset fast -pix_fmt yuv420p \
    -c:a aac -b:a 96k "$med/preview.mp4"

"$root/scripts/contact-sheet.sh" "$med/final.mp4" "$med/sheet.png"

for f in final.mp4 preview.mp4; do
    d=$(ffprobe -v error -show_entries format=duration \
        -of default=noprint_wrappers=1:nokey=1 "$med/$f")
    echo "compose: $med/$f (${d}s)"
done
