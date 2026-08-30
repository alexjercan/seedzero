---
name: produce-short
description: Run the full Seed Zero production flow for one short, from claim to inspected final render.
---

# Produce a short

Follow `docs/vision.md`. One short is one tracked task with this checklist:

1. **Claim.** Pick one subject from `docs/niche.md`. State the claim as a
   sentence with a measurable number in it.
2. **Simulate.** Write `sims/<name>/` code that renders 1080x1920 60 fps
   frames and prints the measured numbers. Fix the seed. Put the seed in
   `projects/<name>/manifest.json`.
3. **Measure.** Run the sim. Copy the printed measurements into the task
   evidence. If the numbers contradict the claim, change the claim.
4. **Script.** Write `projects/<name>/narration.txt` (120-150 words, numbers
   as words) and `projects/<name>/captions` timing. Write three hook
   variants; keep the best.
5. **Voice.** Run `scripts/voiceover.sh`; it must pass round trip.
6. **Music.** Generate a seeded procedural track sized to the voice length.
7. **Compose.** Render `media/<name>/final.mp4` with FFmpeg from the
   manifest: footage, voice, music ducked under narration, captions, and
   the seed overlay. Render a 540x960 preview.
8. **Inspect.** Watch the preview via a one-frame-per-second contact sheet
   and check: hook lands inside two seconds, captions match narration, the
   payoff number is on screen when spoken, the loop closes.
9. **Package.** Write `projects/<name>/metadata.json`: title, description
   (claim plus seed plus reproduction note), tags, category Education,
   visibility private, altered-content disclosure true.
10. **Close.** Record all evidence in the task, then close it.

Media stays out of git. Manifests, narration, metadata, and sim code are
tracked.
