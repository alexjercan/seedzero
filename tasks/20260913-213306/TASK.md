# Produce short: Slinky drop, when does the bottom start to fall

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day15

## Goal

Backlog idea (trend research 2026-09-13, task 20260913-212839): "Slinky
drop: a stretched slinky hanging from its top beside a rigid rod of the
same length; release both; measure how long the bottom coil stays still
and how far the top has fallen by then." Day fifteen, first slot. Chosen
because it is a two-panel same-input drop with continuous visible
motion, the channel's measured winner format (gyroscope 924 views,
Fourier 1,044, brachistochrone 949, tautochrone 945, Dzhanibekov 939),
and the surprise is one number in (the hanging length) and one number
out (how long the bottom waits). Question in the first two seconds:
"Drop a slinky. When does the bottom start to fall?"

## Claim

Drop a slinky. When does the bottom start to fall? Not when you let go.
The bottom coil hangs still until the collapsing top crashes into it.
Every number below is printed by the sim before the script is written.

## Evidence

### Measurements

(recorded after the measure-only run, before scripting)

`sims/slinky/slinky.py` with `projects/slinky/manifest.json` (chain of
equal coils joined by springs of rest length 0.8 mm with a perfectly
inelastic pile-up when coils touch; semi-implicit Euler at 100,000 steps
per second; deterministic, no seed; log in `media/slinky/measure.log`):

- slinky: 80 coils, 200 g, whole-slinky stiffness 0.8 N/m (63.20 N/m per
  coil spring), coil radius 3.3 cm; hanging at rest the top two coils
  are 31.5 mm apart and the bottom two 1.19 mm; hanging length 1.289 m;
  collapsed length 63.2 mm
- bottom coil: first moves 0.01 mm at 0.2905 s and 1 mm at 0.2908 s
  after release; the collapse front (the last stretched coil touching
  down) arrives at 0.2905 s; before that the bottom coil moved at most
  1.835 um
- top coil at the front's arrival: fell 1.226 m of the 1.289 m hang,
  average acceleration 2.96 g; a body in free fall drops 0.414 m in
  0.290 s, so the rod's bottom has fallen 0.414 m when the slinky's
  bottom starts
- check, centre of mass: largest gap between the centre-of-mass drop and
  g t^2 / 2 over the 1 s run 49 um (the semi-implicit Euler offset
  g dt t / 2 at t = 1 s is 49 um, so internal forces and the pile-up
  handling move the centre of mass by nothing measurable)
- check, half the step (200,000 per second): front at 0.2905 s, bottom
  coil 1 mm at 0.2908 s, top fell 1.226 m, unchanged
- estimates: sqrt(2 L / 3 g) = 0.2960 s; the linear wave transit
  (n - 1) sqrt(m / k) = 0.4969 s, so the pile-up front outruns the
  linear wave
- check, other slinkies: 100 coils at 0.8 N/m hang 1.305 m, front at
  0.2901 s, top fell 1.226 m, bottom moved at most 0.126 um before it;
  80 coils at 0.6 N/m hang 1.698 m, front 0.3354 s, top fell 1.635 m,
  bottom at most 8.054 um; 80 coils at 1.2 N/m hang 0.881 m, front
  0.2372 s, top fell 0.818 m, bottom at most 4.930 um
- payoff: the bottom starts to fall when the top crashes into it, 0.29 s
  after the drop; setup number 1.3 m hanging length

Narration numbers: one point three meters (setup), zero point two nine
seconds (payoff).

### Production

- `sims/slinky/slinky.py` renders the slinky (80 coil ellipses, teal
  while stretched, gold once piled up) beside a solid rod of the same
  length, clamps that vanish at release, a dashed starting line under
  both bottoms, labels "slinky" and "solid rod, same length", readouts
  "bottom moved" in mm for each, a central stopwatch "since the drop",
  the three-line question for the first 2.4 s, and the three-line payoff
  from 29.4 s; everything below y 1428 is clipped so falling objects
  leave the frame; four looks: 0.25x from 0.5 s (the whole drop under
  the title), 0.02x from 8.9 s (the bottom hangs while the rod's bottom
  leaves the line), 0.07x from 25.0 s frozen at the crash (0.2905 s)
  from 29.15 to 33.0 s then falling away at 0.25x, and a last 0.25x drop
  from 35.6 s; 0.4 s reset fades between looks and a 0.6 s crossfade
  back to the title
- layout fixes from smoke frames: the two-line title's second line
  measured 1,130 px (split into three lines, 431, 721 and 390 px); the
  readouts "bottom moved: 0 mm" at 624 px collided across the 480 px
  panel gap (stacked as a 32 px label over a 44 px value, 263 and
  229 px); the end of the first cut held a static frozen frame for 10 s
  (replaced by the hold, the fall away and the last drop)
- text widths measured before rendering: overlay 662 px, labels 132 and
  505, stopwatch 263, watch label 259, payoff lines 800, 450 and 922
- narration `projects/slinky/narration.txt`, 103 words; round trip
  failed once on "metres" (heard "meters") and passed at 31.033 s with
  "meters" (log `media/slinky/voice.log`); hooks considered: "Drop a
  slinky. When does the bottom start to fall?" (kept), "Does the bottom
  of a slinky know it was dropped?" (vague), "Can you drop something
  and have it not fall?" (two claims)
- caption schedule (chunks with the 0.6 s offset, voice 31.033 s):
  question 0.60 to 3.61 under the title; setup 3.61 to 8.73 while both
  hang; "Watch the bottom of each one." 8.73 to 10.54 as the second
  look releases at 8.9; "The rod's bottom falls at once." 10.54 to
  12.35 with the rod's readout at 5 to 13 mm; "The slinky's bottom just
  hangs there." 12.35 to 14.16 at 0 mm; the mechanism 14.16 to 24.40
  while the gold pile-up front moves down; the front lands at 23.4 as
  "down as the collapse itself" is spoken; the question again 24.40 to
  26.51 with the third look released at 25.0; "Not when you let go."
  26.51 to 28.02; "When the top crashes into it, zero point two nine
  seconds later." 28.02 to 31.63 with the crash frozen from 29.15 and
  the payoff on screen from 29.4; music seed 45 at gain 0.18
- compose: `media/slinky/final.mp4` 40.000 s, 1080x1920, 60 fps, h264
  with faststart, aac, 3.0 MB; audio mean -16.7 dB, peak -0.0 dB after
  the limiter (log `media/slinky/compose.log`)
- inspection (contact sheet 8x5 at 1 fps plus full-resolution frames of
  the composed final at 0.02, 0.5, 2.8, 12.0, 20.0, 29.5, 33.5, 37.0
  and 39.95 s): title on frame one over the hanging pair with clamps;
  the overlay at y 96 clears the title; captions sit under the dashed
  line and never touch the objects; the rod's bottom leaves the line
  while the slinky's bottom stays on it with "0 mm"; the crash frame
  shows the gold pile on the line at 0.290 s with the rod at 414 mm and
  the payoff under the caption; the last drop plays out and the loop
  crossfade closes on the title (first versus last frame mean pixel
  difference 0.40 of 255)
- `projects/slinky/metadata.json`: title 98 characters, category 27,
  private, altered-content disclosure true, not made for kids

### Published

- quota check before the insert: clock 2026-09-13T21:59:33+03:00 EEST = 11:59:33 PDT, zero upload
  attempts recorded since the 10:00 EEST boundary; this is insert
  attempt 1 of the hard cap of 5
- attempt 1 recorded at 2026-09-13T21:59:33+03:00, video name slinky, before running
  `scripts/yt-upload.py slinky`
- uploaded private with `scripts/yt-upload.py slinky` at 21:59:33 to
  21:59:39 EEST (publishedAt 2026-09-13T18:59:36Z), video d2ET4XCc_TY,
  https://youtu.be/d2ET4XCc_TY (log `media/slinky/upload.log`)
- gate read 1 at 21:59:46: 10 of 15 while processing (uploadStatus
  uploaded, processingStatus processing, definition sd, no source
  resolution, duration P0D); read 2 at 22:01:25: 15 of 15 (processed,
  succeeded, hd, 1080x1920, PT41S, Seed Zero channel, title,
  description and tags match, category 27, not for kids, private) (log
  `media/slinky/qa.log`)
- published with `--publish` at 22:01:36 EEST after a fresh 15 of 15
  read; re-read privacyStatus public, embeddable, madeForKids false,
  selfDeclaredMadeForKids false (logs `media/slinky/qa.log`,
  `media/slinky/publish.log`)

### Quota

- this short: 1,600 insert + 1 channel check + 2 gate reads + 52
  publish run (1 read, 50 update, 1 re-read) = 1,655 units; day total
  1,655 of 10,000 at this point; insert attempt 1 of the hard cap of
  five for the quota day that began 2026-09-13 10:00 EEST

### Repository

- committed on master as ebe182a "Publish the day fifteen slate"
  (sims, projects, tasks, docs/niche.md, web/data; media and secrets
  untracked) and pushed to origin git@github.com:alexjercan/seedzero.git
  at 22:04 EEST on 2026-09-13; the push advanced origin/master from
  7d85634 to ebe182a; verified with `git rev-parse HEAD origin/master`
  (both ebe182a2bcdd38e5be5904c8642a7de5cb6eff93) and `git status -sb`
  (master...origin/master, no divergence); this note is committed
  separately as "Record the day fifteen push"
