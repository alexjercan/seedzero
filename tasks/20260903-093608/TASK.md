# Produce short: Stadium versus circle billiards

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day5

## Goal

Pillar idea from docs/niche.md "Chaos and physics: billiards in stadium
versus circle tables". Day five slate, chosen because the chaos-motion
format leads the channel (double pendulum 1,158 views, pendulum wave
716) and this is the same claim shape as the double pendulum: two balls
launched one thousandth of a degree apart, one round table where they
stay together and one stadium where they split. Measure the split.

## Claim

Two point balls launched from the same spot one thousandth of a degree
apart, at one metre per second, on two frictionless tables. On the round
table every bounce hits the wall at sixty nine point six degrees, and the
gap never passes about a tenth of a millimetre in forty three seconds.
On the stadium the balls are one centimetre apart at nine point zero two
seconds, one metre apart at seventeen point four five seconds, never
agree again, and reach one point seven nine metres apart.

## Evidence

### Measurements

`sims/billiards/billiards.py` with `projects/billiards/manifest.json`
(circle radius 0.5 m; Bunimovich stadium radius 0.5 m with 1.0 m
straights, 2.0 m long; start (0.17, -0.09) m, launch 37.0 deg, second
ball +0.001 deg = 1.745e-05 rad; speed 1 m/s; 43 s; event-driven exact
legs and reflections, gap sampled at 240 Hz from the exact legs):

- round: 46 bounces each; hit angle 69.612259 deg for every hit, spread
  2.39e-12 deg; gap 0.010 mm at 10 s, 0.045 mm at 20 s, 0.053 mm at
  40 s; first above 0.1 mm at 36.00 s; max 0.121 mm at 42.57 s; widest
  so far 0.081 mm at 30 s, 0.100 mm at 36 s, 0.112 mm at 40 s
- round per-bounce max gap grows linearly, 0.0028 mm per bounce, max
  residual 0.0092 mm (floating-point noise in the reflection, the same
  order as the nudge; no exponential growth)
- stadium: ball A 52 bounces, ball B 40; gap 0.097 mm at 5 s, 20.5 mm at
  10 s, 0.79 m at 15 s, 1.39 m at 25 s; first above 1 mm at 7.10 s, above
  1 cm at 9.02 s (8 bounces), above one ball width on screen (56 mm) at
  10.55 s, above 1 m at 17.45 s (15 bounces); max 1.79 m at 30.37 s;
  after the metre crossing the gap never falls below 19.5 mm (29.21 s)
- stadium hit angle: min 3.6 deg, max 87.8 deg over 52 hits
- stadium growth 0.1 mm to 5 cm (3.62 s to 10.53 s): 0.911 per second,
  doubling every 0.76 s, but bursty (max log residual 5.27), so no
  doubling time is narrated
- nudge and angle checks (0.0005 deg, 0.002 deg, 30 deg, 42 deg): the
  round table stays under 0.25 mm, the stadium reaches one ball width at
  9.95 to 11.40 s and one metre at 17.15 to 31.03 s (never for the
  0.0005 deg run inside 43 s)

No time step exists: the only approximations are floating-point
reflections, and the round-table result shows they stay at the 0.1 mm
scale over 46 bounces.

### Production

- The first exponential fit included post-saturation samples (residual
  7.8); it now fits the contiguous window from the first crossing of
  0.1 mm to the first crossing of 5 cm. Still bursty, so the narration
  keeps the crossing times and the widest gaps only.
- Voice round-trip: 128 words, 41.35 s, after six rephrases:
  "thousandth" was transcribed as "thousand", "one point, zero point
  zero zero one" merged into one number, "stadium's" became "stadiums",
  "centimetres" became "cm"; the metric words use US spelling. Fixed
  `scripts/normalize.py` so that "zero" is always its own digit and
  digit tokens fold with "million" like spelled numbers.
- Layout fixes from the sheet: balls 9 to 14 px, brighter and wider
  trails with a 2.5 s prefilled tail and fade 0.992, so the paths read
  at phone size. Scene 42 to 43 s to fit the voice.
- Full-resolution frames at 0, 10.5, 19, 40.5 and 42.9 s inspected. The
  chart labels ran past the right edge at the end of the scene, fixed by
  clamping them inside the frame and re-rendering. Timing: "nine point
  zero two" is spoken at about 18 s (event at 9.02 s), "seventeen point
  four five" at about 23 s, "about a tenth of a millimeter" at 35-36 s
  (widest 0.093 to 0.100 mm on screen), "one point seven nine" at about
  38 s (widest 1.79 m since 30.4 s), payoff card at 40 s: "40 s. round:
  0.111 mm. stadium: 1.79 m".
- Mix: mean -15.1 dB, peak 0.0 dB. Final 43.00 s, 1080x1920, 60 fps,
  music seed 12.

### Upload and publish

- Uploaded private at 10:20 +03:00 on the fresh Pacific quota day (1,600
  units): video `8l_VDPlOLC0`, <https://youtu.be/8l_VDPlOLC0>.
- QA of the processed upload: processing succeeded, upload status
  processed, PT44S, hd, channel id UCWXsZTvrh_OHkzt6v1xkTsw, and title,
  description, all nine tags, category 27 and made-for-kids false
  verified against `projects/billiards/metadata.json`.
- Published public at 2026-09-03 10:22:05 +03:00 under the self-QA
  policy, then re-read to confirm. First of the day's three slots.
