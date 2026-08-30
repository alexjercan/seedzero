# Build the shorts composition pipeline

- STATUS: CLOSED
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

### Built (2026-08-30)

- `scripts/music.py SEED DURATION OUT`: seeded numpy track (A2 drone pad
  plus sparse pentatonic plucks, lowpassed, peak 0.30, fade in and out).
- `scripts/captions.py`: emits an FFmpeg video filter script with the seed
  overlay and captions chunked at 20 characters, timed proportionally to
  word count across the measured voice duration.
- `scripts/compose.sh NAME`: reads `projects/NAME/manifest.json`
  (music_seed, music_gain, voice_offset, overlay), generates music sized to
  the footage, mixes voice over music with a limiter, burns captions via
  `-/filter:v`, writes `final.mp4` (H.264/AAC 1080x1920) plus a 540x960
  30 fps preview and a contact sheet.
- `scripts/contact-sheet.sh`: one-frame-per-second 8-column sheet.

### Verification

- Smoke project (12 s synthetic footage, verified voice-over): one command
  produced final, preview, and sheet. Contact-sheet inspection caught
  caption overflow at fontsize 72 with word-count chunking; fixed by
  character-budget chunking at fontsize 64 and re-inspected a caption
  frame at full resolution.
- Determinism: reruns produce byte-identical `music.wav` and
  `captions.filter` (md5 checked); the encoder re-produces the same
  content.
- ffmpeg 8 dropped `-filter_script:v`; the pipeline uses `-/filter:v`.
- Python compile checks, bash syntax checks, and `nix flake check` pass.
