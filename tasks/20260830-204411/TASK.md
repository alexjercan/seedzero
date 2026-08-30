# Produce short: double pendulum divergence

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: pilot

## Goal

Two identical frictionless double pendulums, one thousandth of a degree
apart; measure the divergence times and produce the short.

## Evidence

### Measurements

- Physics: point masses m1=m2=1, rods l1=l2=1, g=9.81, RK4 at dt=1/600.
  Scouted release angles 90 to 135 degrees; chose 110 degrees.
- At 110 deg, delta 0.001 deg: visible split (gap > 0.1 L) at 9.82 s;
  gap wider than the pendulum (> 1.0 L) at 14.9 s; max gap 1.99 L;
  energy drift 7.3e-7 over the run, so the integration is trustworthy.
- Hook claim check: 0.001 deg at arm's length (0.7 m) is 12.2
  micrometers of displacement, genuinely thinner than a hair (50-100).
- Narration quotes only these measured values.

### Production

- `sims/pendulum/pendulum.py` simulates both runs, draws overlapping
  pendulums (green over white, so the overlap phase reads as one), fading
  tip trails, live timer and gap HUD, payoff labels with the measured
  times. Footage 34.9 s, 1080x1920, 60 fps; loops end to hook.
- First voiceover pass measured 33.19 s, longer than planned footage;
  extended the post-divergence phase instead of cutting narration. Voice
  round-trip passed.
- Contact-sheet inspection caught the compose overlay colliding with the
  sim HUD; moved the overlay to y=96 in `scripts/captions.py` (benefits
  all future shorts) and shortened the overlay text. Re-inspected clean.

### Upload

Private for owner QA: video `BU_j-UbPR7k`, <https://youtu.be/BU_j-UbPR7k>.
