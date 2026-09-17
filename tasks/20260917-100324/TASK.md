# Produce short: Coupled pendulum swap, one swing hands its motion to the other

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day19

## Goal

Backlog idea (trend research 2026-09-16, task 20260916-100924):
"Coupled pendulum swap: two identical 1 m pendulums joined by a weak
spring, one started at 10 degrees and the other hanging still, beside
the same pair with no spring; measure when the first pendulum stops
dead and the second holds the whole swing; expect the full swap at
20.0 s and the swing back at 40.0 s when the spring puts the mode
frequencies pi/20 rad/s apart (about ten swings per swap), the
unsprung neighbour never moving; the 40 s beat is exactly periodic so
the short loops; deterministic, no seed." Day nineteen, second slot.
Chosen because it is continuous motion, a two-panel same-input
comparison (the same two pendulums with and without the spring),
periodic so the short loops, with one plain question, one setup number
(the starting angle) and one payoff number (the swap time) that a
closed form checks.
Question in the first two seconds: "Can a swing pass its motion to
its neighbour?"

## Claim

Two identical pendulums joined by a weak spring: start one at ten
degrees and the other still, and the first one stops dead while the
second holds the whole swing, then they trade back. Without the spring
the neighbour never moves. Every number below is printed by the sim
before the script is written.

## Evidence

### Measurements

(recorded after the measure-only run, before scripting)

`sims/coupled/coupled.py` with `projects/coupled/manifest.json` (two
identical pendulums of length 0.99362 m = g / pi^2, small-swing period
2.0000 s, point bobs of 100 g, pivots 0.95 m apart, joined at bob level
by a spring of k = 0.050582 N/m (k / m = 0.50582 s^-2) whose natural
length equals the pivot spacing; the left pendulum starts at 10 degrees,
the right at 0, both at rest; the same pair with no spring below; the
full nonlinear equations with no damping, RK4 at 1200 steps per second
(dt = 8.33e-4 s) for 44 s, 40 s shown; deterministic, no seed; log in
`media/coupled/measure.log`):

- linear closed forms: in-phase mode omega1 = sqrt(g / L) = 3.14159
  rad/s (period 2.0000 s, 20.00 swings in 40 s), opposite mode omega2 =
  sqrt(g / L + 2 k / m) = 3.29867 rad/s (period 1.9048 s, 21.00
  swings), difference pi / 20 rad/s; full swap at pi / (omega2 -
  omega1) = 20.000 s, back at 40.000 s
- swings of the left pendulum (swing, end time, left peak, right peak
  in degrees): 1 1.95 s 10.00 1.17; 2 3.91 s 9.88 2.66; 3 5.86 s 9.53
  4.09; 4 7.82 s 8.96 5.43; 5 9.77 s 8.18 6.65; 6 11.72 s 7.21 7.71;
  7 13.67 s 6.07 8.59; 8 15.62 s 4.79 9.27; 9 17.55 s 3.39 9.73;
  10 19.40 s 1.93 9.97; 11 20.67 s 0.45 10.00 (this "swing" holds the
  rest at the bottom); 12 22.51 s 1.91 9.97; 13 24.45 s 3.37 9.74;
  14 26.40 s 4.77 9.28; 15 28.35 s 6.05 8.60; 16 30.30 s 7.19 7.72;
  17 32.25 s 8.17 6.66; 18 34.20 s 8.95 5.45; 19 36.16 s 9.53 4.11;
  20 38.11 s 9.88 2.68; 21 40.07 s 10.00 1.19
- swap: the left pendulum has its least energy at 20.039 s, a swing of
  0.0001 degrees (angle -0.0001 degrees, rate -0.0012 degrees/s: at
  rest at the bottom); the right pendulum is then at 9.998 degrees
  moving at -0.663 degrees/s, its nearest swing peak 10.000 degrees at
  20.033 s; the left pendulum's smallest turning point is 0.0001
  degrees at 20.039 s and its neighbouring swing peaks are 0.452
  degrees at 19.404 s and 0.434 degrees at 20.666 s; straight lines
  through the swing peaks over 4 s on each side cross at 20.047 s at
  -0.042 degrees; linear closed form 20.000 s
- back: the right pendulum has its least energy at 40.079 s, a swing
  of 0.0004 degrees; the left pendulum is then at 9.990 degrees moving
  at -1.412 degrees/s; linear closed form 40.000 s; 20.039 s to the
  swap and 20.039 s back
- loop: at 40 s the left pendulum is at 9.780 degrees moving at 6.704
  degrees/s and the right at 0.015 degrees moving at -0.390 degrees/s,
  against 10 and 0 degrees at rest at the start; the bobs are 1.5 px
  and 0.1 px from their first-frame positions; the 0.6 s loop fade
  covers the difference
- carrier: the left pendulum swings every 1.9518 s over its first seven
  swings (10.27 swings to the swap); linear mean of the two modes
  1.9512 s
- modes: started together at 10 degrees they swing every 2.0038 s and
  started opposite every 1.9094 s; at 1 degree, 2.0000 s together and
  1.9048 s opposite (linear 2.0000 and 1.9048 s); a 1 degree start
  swaps at 20.000 s with a swing of 0.0000 degrees (linear 20.000 s);
  the 10 degree start swaps at 20.039 s, 0.20 percent later
- checks: total energy drifts by at most 3.1e-13 relative over 44 s;
  at 2400 steps per second the swap is at 20.039 s with a swing of
  0.0001 degrees; no spring: the right pendulum's largest angle over
  44 s is 0.000 degrees and the left one swings every 2.0038 s (its 10
  degree swing lengthens the 2.0000 s small-swing period by 0.19
  percent)

Narration numbers: ten degrees (setup), twenty seconds (payoff: the
measured 20.039 s rounds to 20.0, and the card prints the measured
value as "20.0 s"). The return at 40.079 s, the mode periods, the
swing table and the 1 degree check go to the description.

### Production

- footage: `sims/coupled/coupled.py` (no arguments) wrote
  `media/coupled/footage.mp4`, 40.00 s at 60 fps, 2,400 frames, in the
  resumed session at 15:36 EEST; the same run re-printed every
  measurement above (log in `media/coupled/render.log`); text widths
  at most 865 px (payoff line 4) so nothing clips at 1080 px; the
  0.6 s loop fade covers the 1.5 px between the last frame and the
  first; smoke frames at 0, 1.5, 3, 6, 10, 15, 20, 20.05, 25, 29.5 and
  39.7 s were rendered by the producing session at 10:18 and inspected
  in the resumed session at 15:33: title, beams with the readouts,
  spring, swing-peak arcs, the no-spring pair below, payoff card,
  crossfade
- voice: `scripts/voiceover.sh projects/coupled/narration.txt` passed
  the round trip on the first try (112 words, 34.17 s, ends at 34.77 s
  of the 40 s video, 3.3 words/s; the narration spells "neighbor" the
  way the transcriber writes it, the title and the card keep
  "neighbour"); timing (`scripts/voice-timing.py`, +0.6 s offset):
  "Watch the left swing shrink while the right one grows" 12.78 to
  18.76 s (readouts 6.1 and 8.2 degrees at 12.5 s), "At twenty seconds
  the left one stops dead" inside 18.76 to 22.34 s against the swap at
  20.04 s (readouts 0.0 and 10.0 at 20.1 s), "Yes, all of it in twenty
  seconds" 30.95 to 33.35 s with the payoff card from 29.0 s, "Without
  the spring, never" 33.35 to 34.77 s; log in `media/coupled/voice.log`
- compose: `scripts/compose.sh coupled` wrote `media/coupled/final.mp4`
  (h264 1080x1920 60 fps, aac, 40.000 s; music seed 57 at gain 0.18;
  captions at caption_y 0.75); loudness mean -16.0 dB, peak -0.0 dB;
  preview and 8x5 contact sheet written (`media/coupled/compose.log`)
- local QA: frames at 0.02, 1.5, 3, 8, 13, 18, 20.05, 24, 29.5, 33, 36
  and 39.95 s extracted from final.mp4; the contact sheet and the
  frames at 0.02, 13, 20.05, 33 and 39.95 s inspected: title on screen
  to 2.4 s with the left bob already released at 10 degrees, clock and
  readouts from 2.4 s, the left readout falling 9.9, 8.2, 5.4, 1.9,
  0.5 while the right climbs 1.9, 6.1, 8.2, 9.9, 10.0, "0.0 deg" and
  "10.0 deg" at 20.1 s under "At twenty seconds", the swing back to
  8.2 and 5.5 at 33 s, the no-spring pair at 10.0 and 0.0 throughout,
  the payoff card in four lines under the captions from 29 s, the last
  frame crossfading to the title; no clipped text, captions match the
  narration; approved
- metadata: `projects/coupled/metadata.json`, title 97 characters,
  description with the swing table, the swap and return times against
  the closed forms, the two mode periods, the no-spring check, the
  energy and half-step checks; 10 tags; category 27; private;
  containsSyntheticMedia true

### Published

- quota check before the insert: clock 2026-09-17T15:41:54+03:00 EEST; one upload
  attempt (rollrace, 15:40:39, published) recorded since the 10:00 EEST
  boundary (log entries and media/*/upload.log both checked); this is
  insert attempt 2 of the hard cap of 5
- attempt 2 recorded at 2026-09-17T15:41:54+03:00, video name coupled, before running
  `scripts/yt-upload.py coupled`
- upload: `scripts/yt-upload.py coupled` ran 15:41:54 to 15:41:59 EEST,
  token verified to see only the Seed Zero channel, video id
  wmkc_zygzXQ, private (`media/coupled/upload.log`)
- gate: `scripts/yt-qa.py coupled wmkc_zygzXQ --wait --publish` in the
  foreground from 15:42:07 EEST; processing succeeded within the first
  polls; 15 of 15 pass (processed, succeeded, hd, 1080x1920, title,
  description, tags, category 27, not for kids, PT41S for the 40.000 s
  file, private); containsSyntheticMedia reads absent as on every
  earlier upload (`media/coupled/publish.log`)
- publish: the same run set the video public at 2026-09-17T15:42:40+03:00;
  the re-read after 15 s shows privacyStatus public, madeForKids false,
  embeddable true; public at https://youtu.be/wmkc_zygzXQ

### Quota

- attempt 2 of the hard cap of 5 for the quota day that began
  2026-09-17T10:00 EEST; cost 1 + 1,600 + 3 + 50 + 1 = 1,655 units;
  day total after two attempts 3,309 units
