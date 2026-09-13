# Produce short: Gravity train, a tunnel through the Earth

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day15

## Goal

Backlog idea (trend research 2026-09-13, task 20260913-212839): "Gravity
train: a capsule dropped into a straight tunnel through the centre of a
uniform Earth beside one dropped into a short chord tunnel; measure the
arrival time at the far end and the top speed; expect 42.2 min for
both." Day fifteen, third slot. Chosen because it is a two-panel
same-input comparison whose motion is exactly periodic (the short loops)
and whose surprise is one number: the same arrival time for both
tunnels. Question in the first two seconds: "Fall through the Earth. How
long to the other side?"

## Claim

Two capsules dropped at the same moment, one into a tunnel through the
centre of the Earth and one into a short straight tunnel, arrive at the
far ends at the same time, about forty two minutes, with no engine.
Every number below is printed by the sim before the script is written.

## Evidence

### Measurements

(recorded after the measure-only run, before scripting)

`sims/gravitytrain/gravitytrain.py` with
`projects/gravitytrain/manifest.json` (a capsule on each straight
frictionless tunnel through a uniform-density Earth; the full central
force g0 r / R is integrated along the tunnel with RK4 at 20 steps per
second of travel; deterministic, no seed; log in
`media/gravitytrain/measure.log`):

- Earth radius 6,371 km, surface gravity 9.81 m/s^2; the tunnel through
  the centre is 12,742 km long; the chord tunnel is 4,000 km long,
  6,049 km from the centre, its midpoint 322 km below the surface
- centre tunnel: arrives at the far end at 2,531.74 s = 42:12 (42.196
  min); top speed 7,905.7 m/s at the midpoint; back at the start at
  5,063.48 s = 84.391 min
- chord tunnel: arrives at 2,531.74 s = 42:12; top speed 2,481.8 m/s at
  the midpoint; back at the start at 5,063.48 s
- difference in arrival times 0.000 ms; closed forms pi sqrt(R / g0) =
  2,531.7 s = 42.20 min, sqrt(g0 R) = 7,906 m/s, (c / 2) sqrt(g0 / R) =
  2,482 m/s
- check, double the steps: both arrive at 2,531.740 s
- check, other chords: 340 km (2 km deep, top speed 211 m/s), 1,000 km
  (20 km deep, 620 m/s), 8,000 km (1,412 km deep, 4,964 m/s) and
  12,000 km (4,229 km deep, 7,445 m/s) all arrive at 42:12
- check, two-layer Earth (core 3,480 km at 11,000 kg/m^3, mantle
  4,450 kg/m^3, surface gravity 9.83 m/s^2, 10.70 m/s^2 at the core
  boundary): the centre tunnel arrives at 2,332.0 s = 38:52 with a top
  speed of 9,633 m/s and the chord at 2,520.0 s = 42:00 with 2,503
  m/s, so the equal times need the uniform Earth
- on screen: three periods in 40 s (379.8x), arrivals at 6.67, 20.00
  and 33.33 s of video, returns at 13.33, 26.67 and 40.00 s so the last
  frame equals the first
- payoff: 42:12 through the centre and 42:12 through the 4,000 km
  tunnel; setup number 4,000 km

Narration numbers: four thousand kilometers (setup), forty two minutes
(payoff).

### Production

- `sims/gravitytrain/gravitytrain.py` renders a cross-section of the
  Earth (radius 470 px, radial gradient) with the centre tunnel down the
  middle (gold capsule) and the 4,000 km chord tunnel near the right
  edge (teal capsule); a stopwatch left of centre shows the simulated
  time since the drop and resets at each period; each tunnel has a
  label, a live speed readout and an "arrived 42:12" stamp that appears
  when its capsule reaches the far end and clears at the next drop; the
  two-line question for the first 2.4 s and the three-line payoff from
  30.6 s; the fall runs at 379.8x so three round trips fill 40 s with
  arrivals at 6.67, 20.00 and 33.33 s and the last frame equals the
  first (0.6 s loop crossfade)
- text widths measured before rendering: overlay 871 px, title lines
  718 and 876, labels 428 and 368, speed 243, arrived 303, watch 204,
  watch label 259, payoff lines 621, 586 and 614
- narration `projects/gravitytrain/narration.txt`, 114 words; round trip
  failed once on "dives" (heard "d ives"), "straight" ("stray") and a
  sentence-initial "Through" ("for"), passed at 34.145 s with "races
  down", "every tunnel, long or short" and "Down through the center";
  then "Watch the far end of each tunnel." was added so the arrival line
  lands on the visual arrival, passed at 36.258 s (log
  `media/gravitytrain/voice.log`); hooks considered: "Fall through the
  Earth. How long to the other side?" (kept), "The gravity train."
  (no question), "Which tunnel is faster?" (weaker payoff)
- spoken timing checked by transcribing the voice track between its
  pauses (video time = voice time + 0.6 s): the question 0.6 to 3.05,
  the two tunnels to 11.0 while the first capsules arrive at 6.67, "Drop
  a capsule into each at the same moment" 11.0 to 15.1 over the second
  drop at 13.33, "And they arrive together" 18.2 to 19.6 with the second
  arrival at 20.00, the mechanism 19.6 to 28.9, "Forty two minutes"
  30.5 to 31.6 with the payoff from 30.6, the two tunnels named 31.6 to
  35.2 around the third arrival at 33.33, "forty two minutes, both"
  35.2 to 36.7 with both stamps on screen; music seed 47 at gain 0.18
- compose: `media/gravitytrain/final.mp4` 40.000 s, 1080x1920, 60 fps,
  h264 with faststart, aac, 4.1 MB; audio mean -16.5 dB, peak -0.2 dB
  after the limiter (log `media/gravitytrain/compose.log`)
- inspection (contact sheet 8x5 at 1 fps plus full-resolution frames of
  the composed final at 0.02, 2.0, 7.0, 13.5, 17.0, 19.0, 20.3, 30.9,
  33.5, 36.0 and 39.95 s): title on frame one over both capsules at the
  surface; the overlay clears the title; the stopwatch reads 44:18 with
  both "arrived 42:12" stamps at 7.0 s and 1:03 after the second drop at
  13.5 s; "And they arrive" is on screen at 20.3 s with both capsules at
  the far ends and both stamps; the payoff is on screen while "forty two
  minutes" is spoken; captions sit under the Earth and above the payoff;
  the loop crossfade closes on the title (first versus last frame mean
  pixel difference 0.42 of 255)
- `projects/gravitytrain/metadata.json`: title 96 characters, category
  27, private, altered-content disclosure true, not made for kids

### Published

- quota check before the insert: clock 2026-09-13T22:00:04+03:00 EEST = 12:00:04 PDT; two upload
  attempts recorded since the 10:00 EEST boundary (slinky 21:59:33,
  cannon 21:59:49); this is insert attempt 3 of the hard cap of 5
- attempt 3 recorded at 2026-09-13T22:00:04+03:00, video name gravitytrain, before running
  `scripts/yt-upload.py gravitytrain`
- uploaded private with `scripts/yt-upload.py gravitytrain` at 22:00:04
  to 22:00:09 EEST (publishedAt 2026-09-13T19:00:07Z), video
  WWpQVZMrn00, https://youtu.be/WWpQVZMrn00 (log
  `media/gravitytrain/upload.log`)
- gate read 1 at 22:01:46: 15 of 15 (processed, succeeded, hd,
  1080x1920, PT41S, Seed Zero channel, title, description and tags
  match, category 27, not for kids, private) (log
  `media/gravitytrain/qa.log`)
- published with `--publish` at 22:02:17 EEST after a fresh 15 of 15
  read; re-read privacyStatus public, embeddable, madeForKids false,
  selfDeclaredMadeForKids false (logs `media/gravitytrain/qa.log`,
  `media/gravitytrain/publish.log`)

### Quota

- this short: 1,600 insert + 1 channel check + 1 gate read + 52
  publish run (1 read, 50 update, 1 re-read) = 1,654 units; day total
  4,963 of 10,000; insert attempt 3 of the hard cap of five for the
  quota day that began 2026-09-13 10:00 EEST; two attempts remain
  unused

### Repository

- committed on master as ebe182a "Publish the day fifteen slate"
  (sims, projects, tasks, docs/niche.md, web/data; media and secrets
  untracked) and pushed to origin git@github.com:alexjercan/seedzero.git
  at 22:04 EEST on 2026-09-13; the push advanced origin/master from
  7d85634 to ebe182a; verified with `git rev-parse HEAD origin/master`
  (both ebe182a2bcdd38e5be5904c8642a7de5cb6eff93) and `git status -sb`
  (master...origin/master, no divergence); this note is committed
  separately as "Record the day fifteen push"
