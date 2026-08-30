# Produce pilot short: Galton board

- STATUS: OPEN
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
