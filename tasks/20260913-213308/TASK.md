# Produce short: Galilean cannon, tennis ball on a basketball

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day15

## Goal

Backlog idea (trend research 2026-09-13, task 20260913-212839):
"Galilean cannon: a tennis ball on a basketball dropped together from 1 m
beside a tennis ball dropped alone; measure the peak height of the tennis
ball." Day fifteen, second slot. Chosen because it is the most widely
shared physics demo in the candidate list, a two-panel same-input drop
with continuous motion, and one number in (the drop height) and one
number out (how high the tennis ball flies). Question in the first two
seconds: "Drop a tennis ball on a basketball. How high does it fly?"

## Claim

The same tennis ball dropped from the same height, alone against riding
on a basketball, with perfect bounces and no air: alone it comes back to
the drop height, on the basketball it flies several times higher. Every
number below is printed by the sim before the script is written.

## Evidence

### Measurements

(recorded after the measure-only run, before scripting)

`sims/cannon/cannon.py` with `projects/cannon/manifest.json` (one
dimensional, event driven: exact parabolas between collisions, closed-form
collision times, perfectly elastic floor and ball-to-ball bounces, no air;
deterministic, no seed; log in `media/cannon/measure.log`):

- balls: basketball radius 12 cm, 620 g; tennis ball radius 3.3 cm, 58 g;
  mass ratio 10.69; the tennis ball's bottom starts 1.00 m above the
  floor in both panels, the basketball's bottom 0.76 m
- alone: hits the floor at 0.4515 s at 4.429 m/s, back to a peak of
  1.0000 m at 0.903 s, then every 0.903 s; energy drift 1.9e-16
- on the basketball: both fall together and the basketball hits the
  floor at 0.3936 s at 3.862 m/s; it bounces up into the tennis ball
  still coming down at 3.862 m/s; after the hit the tennis ball goes up
  at 10.263 m/s (closed form (3M - m)/(M + m) v = 10.263) and the
  basketball at 2.540 m/s (closed form (M - 3m)/(M + m) v = 2.540, 66%
  of its bounce speed); speed factor 2.6578 (limit 3 for a very heavy
  bottom ball, height factor 9)
- the tennis ball's bottom peaks at 5.6086 m at 1.440 s (5.61x its own
  bounce and 5.61x the drop height); its top reaches 5.675 m; the
  basketball peaks at 0.329 m at 0.653 s; 15 collisions in 4 s; energy
  drift 6.0e-16
- later flights (not narrated): after the first flight comes down the
  balls keep colliding and the tennis ball's highest point in the 4 s
  run is 8.655 m
- check, lossy bounces (restitution 0.85 at the floor and between
  balls): alone 0.723 m, on the basketball 3.687 m (5.10x)
- check, mass ratios: 3 gives 3.280 m (speed factor 2.000), 10 gives
  5.522 m (2.636), 100 gives 6.901 m (2.960), 1000 gives 7.062 m (2.996)
- check, a third ball on top (45.9 g, radius 2.1 cm): it peaks at
  7.53 m at 1.608 s (7.5x its own bounce)
- payoff: alone back up to 1.0 m, on a basketball 5.6 m; setup number
  1 m drop

Narration numbers: one meter (setup), five point six meters (payoff).

### Production

- `sims/cannon/cannon.py` renders two panels over one floor line with a
  shared height ruler on the left: the tennis ball alone (teal) and the
  tennis ball on a basketball (gold, seam lines); the camera zooms out
  as the highest tennis ball rises (600 px/m at the start, about 166
  px/m at the peak) so the floor stays in view; a constant-size ring
  marks each tennis ball and a short fading trail follows it; labels
  "alone" and "on a basketball" with a "highest so far" readout; the
  three-line question for the first 2.4 s and the three-line payoff
  from 29.5 s; five looks: 0.5x from 0.5 s under the title, 0.25x from
  9.4 s (alone bounces back, the stack takes off), 0.15x from 14.4 s
  (the floor hit and the head-on hit), 0.3x from 24.6 s frozen at the
  peak (1.440 s) from 29.4 to 34.0 s then falling at 0.5x, and a last
  0.5x drop from 37.0 s; 0.4 s reset fades between looks and a 0.6 s
  crossfade back to the title
- fixes from the measure run: the peak search first took the highest
  sample after the hit, which belonged to a later flight (8.66 m at
  3.79 s after more collisions); the peak is now the closed form of the
  flight that starts at the hit, checked against the samples (5.6086 m
  at 1.440 s), and the later flights are printed separately; the event
  lookup by time picked the floor hit that shares the instant of the
  ball hit, so peaks are keyed by the event itself
- text widths measured before rendering: overlay 692 px, title lines
  562, 504 and 660, labels 124 and 345, readout label 250, readout 170,
  payoff lines 467, 532 and 502
- narration `projects/cannon/narration.txt`, 104 words; round trip
  failed once on "Head on." (heard "hit on") and passed at 32.508 s
  with "They meet head on." (log `media/cannon/voice.log`); hooks
  considered: "Drop a tennis ball on a basketball. How high does it
  fly?" (kept), "Why does the small ball fly?" (answer needs the
  mechanism first), "Two balls, one drop, 5.6 m." (no question)
- caption schedule (chunks with the 0.6 s offset, voice 32.508 s):
  question 0.60 to 4.28 under the title while the first drop plays at
  0.5x; setup 4.28 to 9.80 while both hang; "Alone, it bounces straight
  back up to one meter." 9.80 to 12.56 with the second look released
  at 9.4 (alone peaks at 13.0); "On the basketball, it takes off."
  12.56 to 14.40 while the stack rises; "Slow it down." 14.40 to 15.32
  with the third look released at 14.4; "The big ball hits the floor
  first" 15.32 to 17.77 with the floor hit at 17.0; the head-on beat to
  27.59 while the ball rises to its peak at 24.0; the question again
  27.59 to 29.12 with the fourth look rising; "Five point six meters"
  29.12 to 31.27 with the peak frozen from 29.4 and the payoff from
  29.5; "Perfect bounces, no air." 31.88 to 33.11; music seed 46 at
  gain 0.18
- compose: `media/cannon/final.mp4` 40.000 s, 1080x1920, 60 fps, h264
  with faststart, aac, 2.3 MB; audio mean -16.6 dB, peak -0.0 dB after
  the limiter (log `media/cannon/compose.log`)
- inspection (contact sheet 8x5 at 1 fps plus full-resolution frames of
  the composed final at 0.02, 1.5, 5.0, 12.0, 17.0, 20.0, 29.6, 35.0,
  38.5 and 39.95 s): title on frame one over both balls at rest at 1 m;
  the overlay clears the title; the ruler relabels as the camera zooms
  out and the floor never leaves the frame; captions sit under the
  floor line; the readouts freeze at 1.00 m and 5.61 m; the payoff is on
  screen while "five point six meters" is spoken with the ball frozen
  at 5.6 m on the ruler; the last drop plays out and the loop crossfade
  closes on the title (first versus last frame mean pixel difference
  0.27 of 255)
- `projects/cannon/metadata.json`: title 92 characters, category 27,
  private, altered-content disclosure true, not made for kids

### Published

- quota check before the insert: clock 2026-09-13T21:59:49+03:00 EEST = 11:59:49 PDT; one upload
  attempt recorded since the 10:00 EEST boundary (slinky at 21:59:33);
  this is insert attempt 2 of the hard cap of 5
- attempt 2 recorded at 2026-09-13T21:59:49+03:00, video name cannon, before running
  `scripts/yt-upload.py cannon`
- uploaded private with `scripts/yt-upload.py cannon` at 21:59:49 to
  21:59:54 EEST (publishedAt 2026-09-13T18:59:51Z), video wN82zmHFM5c,
  https://youtu.be/wN82zmHFM5c (log `media/cannon/upload.log`)
- gate read 1 at 22:01:26: 15 of 15 (processed, succeeded, hd,
  1080x1920, PT41S, Seed Zero channel, title, description and tags
  match, category 27, not for kids, private) (log `media/cannon/qa.log`)
- published with `--publish` at 22:01:54 EEST after a fresh 15 of 15
  read; re-read privacyStatus public, embeddable, madeForKids false,
  selfDeclaredMadeForKids false (logs `media/cannon/qa.log`,
  `media/cannon/publish.log`)

### Quota

- this short: 1,600 insert + 1 channel check + 1 gate read + 52
  publish run (1 read, 50 update, 1 re-read) = 1,654 units; day total
  3,309 of 10,000 at this point; insert attempt 2 of the hard cap of
  five for the quota day that began 2026-09-13 10:00 EEST
