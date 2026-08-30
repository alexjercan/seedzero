#!/usr/bin/env bash
set -euo pipefail

# Speak a narration file with the local speech API, then round-trip the audio
# through transcription and fail when the words differ.

api=${SPEECH_API:-http://localhost:10300}

if [ $# -ne 2 ]; then
    echo "usage: voiceover.sh NARRATION_FILE OUT_WAV" >&2
    exit 2
fi

narration_file=$1
out_wav=$2

text=$(tr '\n\t' '  ' <"$narration_file" | sed 's/  */ /g; s/^ //; s/ $//')
if [ -z "$text" ]; then
    echo "error: empty narration file" >&2
    exit 1
fi

mkdir -p "$(dirname "$out_wav")"

jq -n --arg input "$text" \
    '{model: "piper-1", voice: "en_US-lessac-medium", input: $input, response_format: "wav"}' |
    curl -sf -X POST "$api/v1/audio/speech" \
        -H 'Content-Type: application/json' -d @- -o "$out_wav"

transcript=$(curl -sf -X POST "$api/v1/audio/transcriptions" \
    -F file=@"$out_wav" -F model=whisper-1 | jq -r .text)

script_dir=$(dirname "$(readlink -f "$0")")

normalize() {
    printf '%s' "$1" | python3 "$script_dir/normalize.py"
}

want=$(normalize "$text")
got=$(normalize "$transcript")

duration=$(ffprobe -v error -show_entries format=duration \
    -of default=noprint_wrappers=1:nokey=1 "$out_wav")

if [ "$want" = "$got" ]; then
    echo "ok: transcript matches narration (${duration}s) -> $out_wav"
else
    echo "error: transcript differs from narration" >&2
    diff <(printf '%s\n' "$want") <(printf '%s\n' "$got") >&2 || true
    exit 1
fi
