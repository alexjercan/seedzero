# Produce pilot short: Galton board

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: pilot

## Goal

Produce the first Seed Zero short: a Galton board with twelve rows of pegs
and ten thousand balls, landing the measured claim that the center bin
outdraws the edge bin by roughly nine hundred twenty four to one.

## Direction

- Claim source: binomial distribution, twelve fair coin flips. Expected
  ratio of bin six to bin zero is C(12,6) = 924. The sim must measure the
  actual counts at the shown seed and narrate the measured ratio, not the
  theoretical one, and may note they agree.
- Sim: `sims/galton/`. Physics can be idealized (each peg is a fair coin)
  but honest: every rendered ball follows its own sampled path, balls
  stack visibly in bins, motion stays readable at 60 fps portrait.
- Hook idea: start with the full bell curve already stacked, rewind to
  empty, then let it refill while narrating. Loop closes on the same
  curve.
- Narration: 100 to 150 words, numbers as words, one claim only.
- Depends on the composition pipeline task for final assembly.

## Acceptance

- Measured bin counts at the manifest seed are recorded in evidence and
  support the narrated ratio.
- Voice-over passes the round-trip check.
- `media/galton/final.mp4` is 1080x1920, 60 fps, 30 to 45 seconds, with a
  clean loop, inspected via preview and contact sheet.
- `projects/galton/metadata.json` is complete: title, description with
  seed and reproduction note, tags, Education, private, altered-content
  disclosure true.

## Evidence

### Measurements (seed 0, 10,000 balls, 12 rows)

- counts: [2, 35, 162, 529, 1250, 1933, 2181, 1938, 1244, 534, 164, 27, 1]
- center bin 6: 2181; edge bin 0: 2; edge bin 12: 1; both edges: 3.
- Theory: C(12,6) = 924 paths to center vs 1 per edge; expected center
  2256, expected per edge 2.44. Measured values agree.
- The narration quotes only measured numbers: two thousand one hundred
  eighty one center, three at both edges, nine hundred twenty four paths.

### Production

- `sims/galton/galton.py` simulates every ball as twelve fair coin flips
  and renders every ball's own sampled path; 10,000 balls pour over ~21.5 s
  with a live landed-ball counter drawn from sim state. Footage:
  32.32 s, 1080x1920, 60 fps. Structure: 2 s hook on the finished curve
  with bin labels, wipe to empty, pour, payoff labels plus the smooth
  normal-approximation curve, closing on the same frame as the hook for a
  clean loop.
- Voice-over passed the round-trip check first try: 30.56 s.
- Composed with `scripts/compose.sh galton`: music seed 0, captions, seed
  overlay. `media/galton/final.mp4` 32.3 s; preview and contact sheet
  rendered and inspected (hook lands inside two seconds, captions match
  narration and fit the frame, payoff numbers on screen when spoken, loop
  closes).
- `projects/galton/metadata.json` complete: title, description with seed
  and reproduction note, tags, Education, private, synthetic-media
  disclosure true.

### Upload

Uploaded private for owner QA: video `K_ntI_mY4v0`,
<https://youtu.be/K_ntI_mY4v0>, privacy private, uploadStatus uploaded.
Publishing to public awaits the owner's go.
