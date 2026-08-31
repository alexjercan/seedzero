# Produce short: Boids flock snap

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: pilot

## Goal

Two hundred boids, three rules as on-screen toggles, live polarization
meter; narrate the tick the scatter snaps into alignment, collapse the
flock by toggling alignment off, re-form it by toggling back on.
Completes the pilot slate (idea 4 in docs/niche.md).

## Claim

Two hundred simulated birds with no leader go from seven percent to
above ninety percent in sync at seven point eight seconds, on three
local rules. Turn the alignment rule off and sync falls to fifty
percent; turn it back on and the flock snaps back above ninety in
under two seconds.

## Evidence

### Measurements

`sims/boids/boids.py` at final manifest: seed 0, 200 boids, toroidal
arena, no heading noise, alignment off at 16.0 s, on at 29.0 s, scene
40.0 s:

- polarization at start: 0.073
- snap (first 1 s hold above 0.9): 7.78 s
- polarization before alignment off: 0.986
- polarization min while alignment off: 0.505 (meter displays 50%)
- re-snap after alignment on: 1.67 s after the toggle
- polarization at end: 0.970

### Tuning iterations (all measured, seed 0)

- Walled arena: sync peaked at 0.296 before the toggle; wall turns
  break global alignment. Switched to a toroidal arena with
  minimum-image neighbor offsets, the classic boids setup: snap 7.78 s.
- Off-window sweeps: 16-26 s min 0.574; 14-27 s min 0.319; final
  16-29 s min 0.505. The floor is state-dependent (which mills form).
- Vicsek-style heading noise 2.5/1.2/0.6 deg per frame delayed the
  snap (12.5 s to never) without deepening the collapse; removed.
- First composition: toggle flipped at 16.5 s video but the narration
  reached "turn the alignment rule off" at 24 s. Reordered the script
  (mechanism into the cruise phase, rule recap into the collapse) and
  timed sentences at the measured 3.3 words per second so each beat
  lands on its visual anchor.

### Hooks considered

1. "Two hundred birds. No leader. Watch them agree in eight
   seconds." [kept]
2. "Nobody is in charge of this flock. That is the point."
3. "These birds cannot see the flock. They each see three rules."

Kept 1: it names the measured snap time and matches the intro visual
(formed flock at one hundred percent, then the scatter reset).

### Production

- `sims/boids/boids.py` renders the arena, three rule pills (alignment
  goes amber "off" during the toggle window), a live "in sync" meter
  with the polarization curve, the snap marker, and the payoff line
  "7% to 99% in 7.8s - no leader". Footage 42.5 s, 1080x1920, 60 fps;
  last frame equals the intro frame so the loop closes.
- Voice round-trip: three iterations. Fixed "%" folding in
  `scripts/normalize.py` (whisper writes "50%", narration says "fifty
  percent"); "whole" heard as "holed" (rephrased); sentence-initial
  "Three" heard as "pretty" (moved three mid-phrase); "their" heard as
  "the", "any more" as "anymore", bare "ninety" transcribed with an
  added "percent" (narration adjusted to the robust forms). Final pass
  ok at 41.39 s.
- Full-resolution frame inspection: hook frame works as thumbnail
  (formed flock, 97%, payoff line), off-frame shows amber pill with
  clump visual, captions clear of all UI text. Mix: mean -15.2 dB,
  limiter at 0.9.

### Upload and publish

- Uploaded private at 2026-08-31 ~09:07 +03:00 (still the 2026-08-30
  Pacific quota day, spending its expiring surplus; 1,600 units):
  video `-hm9P9TXi60`, <https://youtu.be/-hm9P9TXi60>.
- QA on the processed video: processing succeeded, duration PT43S,
  title, description, tags, category, privacy, kids flag all verified
  against `projects/boids/metadata.json`.
- Published public at 2026-08-31 ~09:12 +03:00 under the self-QA
  policy (owner authorized 2026-08-30). First of the day's three
  slots; slots two and three land in the fresh Pacific quota day.

