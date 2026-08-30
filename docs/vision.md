# Production vision

Seed Zero turns one measured simulation result into a short, repeatable
production:

1. Pick one surprising, checkable claim from the idea backlog.
2. Write a deterministic simulation in `sims/<name>/` that both renders the
   frames and measures the claim. The measurement is printed, not eyeballed.
3. Run the simulation. Record the measured numbers in the task evidence. If
   the numbers do not support the claim, change the claim, not the numbers.
4. Write several hooks and one narration script that quotes only measured
   facts. Write numbers as words so the voice reads them well.
5. Generate voice-over with `scripts/voiceover.sh`. The round-trip
   transcription must match the narration text.
6. Generate the music track procedurally from a fixed seed.
7. Compose the final vertical video with FFmpeg from a tracked manifest:
   footage, voice, music, captions, seed overlay.
8. Inspect a low preview and a contact sheet. Revise inputs and re-render.
   Never hand-edit the output.

## Short structure

A default short makes one surprising claim in 30 to 45 seconds:

- 0-2 seconds: visual hook, motion already in progress.
- 2-8 seconds: establish the setup and the seed on screen.
- 8-25 seconds: run the simulation; narrate the mechanism.
- 25-40 seconds: land the measured payoff number.
- Final beat: loop cleanly back to the opening frame when possible. Looping
  shorts replay, and replays feed the feed.

## Quality bars

- One claim per short. Cut anything that serves a second claim.
- The claim must survive this test: a viewer who reruns the sim at the shown
  seed gets the narrated number.
- Captions match the narration word for word.
- Voice, music, and footage are mixed so narration stays legible on a phone
  speaker.
- The first rendered frame must work as the thumbnail.

## Determinism

- Fixed seeds everywhere; the seed is part of the manifest and the video.
- Same inputs produce the same file, byte differences from encoders aside.
- No network calls, wall-clock time, or LLM output inside render code paths.
