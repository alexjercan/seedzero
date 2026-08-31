# Produce short: Pendulum wave realignment

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day2

## Goal

Thirty pendulums tuned one swing apart scatter into apparent chaos,
split into a perfect mirror at half period, and snap back into one
line at exactly the period. Seamless with an on-screen clock. Backlog
idea from trend research 2026-08-30 (pendulum wave).

## Claim

Thirty pendulums, tuned by length so the slowest swings thirty times
in thirty seconds and each neighbor exactly one more. At fifteen point
zero seconds they split into two perfect lines. At twenty five seconds
measured order hits zero. At thirty point zero seconds they realign
into one line with a measured gap of zero point zero pixels.

## Evidence

### Measurements

`sims/pendulumwave/pendulumwave.py` at manifest: 30 pendulums, cycles
30..59 over period 30.0 s, displacement y = A cos(omega t):

- slowest: 1.0000 Hz, tuned length 24.8 cm (g = 9.81)
- fastest: 1.9667 Hz, tuned length 6.4 cm
- mirror at 15.000 s: strict alternation at full amplitude: True
- realign at 30.000 s: max gap 0.000000 px (at 380 px amplitude)
- max disorder: t = 25.00 s, phase coherence R = 0.000

### Production

- Voice round-trip: three iterations. "order: zero" transcribed as
  "0.0" (said "zero point zero"); adjacent number sentences merged
  ("...zero point zero. Thirty point zero..." heard as one number
  cluster; added "At" before the realign sentence); trimmed 113 to
  106 words after measuring Piper at 0.366 s/word with short
  sentences. Final ok at 38.45 s.
- Contact sheet: mirror caption lands on the exact zigzag frame,
  realign caption on the one-line frame; changed "the scramble peaks"
  to "spread the widest" because the 25 s frame shows an elegant
  W-wave, and the measured zero is phase spread, not visual mess.
- Mix: mean -15.6 dB. Loop closes (intro = end state).

### Upload and publish

- Uploaded private after the Pacific quota reset (1,600 units):
  video `kIuhNc9TguE`, <https://youtu.be/kIuhNc9TguE>.
- QA: processing succeeded, PT41S, all metadata fields verified.
- Published public at 2026-08-31 ~10:04 +03:00 under the self-QA
  policy. Second of the day's three slots.

