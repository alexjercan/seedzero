# Build the shorts composition pipeline

- STATUS: OPEN
- PRIORITY: 1
- TAGS: pilot

## Goal

Build the reusable render path that turns one project folder into a
finished vertical short: footage frames, voice, music, captions, seed
overlay, preview, and contact sheet.

## Direction

- Input contract: `sims/<name>/` renders numbered 1080x1920 frames and
  prints measurements; `projects/<name>/` holds `manifest.json`,
  `narration.txt`, and `metadata.json`.
- `scripts/compose.sh <name>`: FFmpeg assembles frames at 60 fps, mixes
  voice over music with ducking, burns captions timed to the voice, stamps
  the seed overlay, writes `media/<name>/final.mp4` and a 540x960 preview.
- `scripts/music.py <seed> <duration> <out.wav>`: deterministic procedural
  track, quiet enough to sit under narration. Start from the approach in
  `~/personal/nova-showcase/scripts/generate-music.py` but write our own
  sound.
- Caption timing: estimate from measured words per second, then verify
  against the transcription API's output if it returns timestamps.
- Everything deterministic from the manifest. No hand edits of output.

## Acceptance

- One command produces final and preview from a project folder.
- Re-running produces the same content.
- A contact sheet script exists for inspection.
- Shell checks and `nix flake check` pass.

## Evidence
