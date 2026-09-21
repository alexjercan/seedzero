# Produce short: Big swing versus small swing, 10 degrees beside 103 degrees

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day23

## Goal

Backlog idea (trend research 2026-09-20, task 20260920-100347, pillar 2
chaos and physics):
"Big swing versus small swing: the same 2.000 s pendulum released at 10
degrees beside 103.0 degrees; measure the periods; expect 2.004 against
2.500 s (T/T0 = (2/pi) K(sin(theta0/2)); 90 degrees runs 18.0 percent
slow, 150 degrees 76 percent, 179 degrees 3.9x), so 20 small swings beat
16 big ones in 40 s and the pair drift out of step and back exactly, a
seamless loop; Galileo said equal; deterministic, no seed."
Day twenty-three, first slot. Chosen because pendulum pieces are the
channel's strongest format (coupled pendulums 1,085 views, hoop bead
984, top precession 909, inverted pendulum 830), it is continuous
tabletop motion in two panels on the same input with a closed-form check,
and everyone was taught that the period does not depend on the swing.
Question in the first two seconds: "Same pendulum, bigger swing. Does it
take longer?" (or the producer's better wording, kept identical in the
title, the hook and the payoff).

## Claim

The same two second pendulum released at ten degrees and at one hundred
three degrees does not keep time: the small swing takes two point zero
seconds a swing and the big swing two point five, so in forty seconds
the small one makes twenty swings and the big one sixteen. Every number
in the narration is printed by the sim before the script is written.

## Evidence

### Measurements

(recorded after the measure-only run, before scripting)

`sims/bigswing/bigswing.py --measure-only` with
`projects/bigswing/manifest.json` (one simple pendulum, a point bob on a
massless rod of length L, g = 9.80665 m/s^2, theta'' = -(g / L) sin
theta, drawn twice at the same scale: the top panel released from rest
at 10 degrees, the bottom panel from rest at the big angle, both at t =
0; L chosen so that the 10 degree swing takes exactly 2.000 s out and
back and the big angle solved by bisection so that its swing takes
exactly 2.500 s, from T = 4 sqrt(L / g) K(sin(theta0 / 2)) with K by the
AGM; RK4 on (theta, omega) at 3,600 steps per second (dt = 2.78e-4 s)
for 41 s, the turnarounds and the bottom crossings interpolated inside
the step; played at real speed; deterministic, no seed; first run 10:19
EEST, re-run at 10:19 after two print fixes, log in
`media/bigswing/measure.log`):

- closed forms: K(sin 5 deg) = K(0.087156) = 1.573792131; L = g (T / 4
  K)^2 = 0.989842 m (98.98 cm); small-angle period T0 = 2 pi sqrt(L / g)
  = 1.996193 s, so the 10 degree swing runs 0.19 percent slow; big angle
  103.415 degrees (103.414844; 13.415 degrees above horizontal, the bob
  rises 0.2320 L = 22.96 cm above the pivot at the turnaround); check: k
  = sin(51.7074 deg) = 0.784857, K(k) = 1.967240164, 4 sqrt(L / g) K =
  2.500000000 s, T / T0 = 1.252384 = (2 / pi) K; T(103.415) / T(10) =
  1.2500
- T / T0 table for this pendulum: 10 deg 1.0019 (2.000 s), 30 deg 1.0174
  (2.031 s), 45 deg 1.0400 (2.076 s), 60 deg 1.0732 (2.142 s), 90 deg
  1.1803 (18.0 percent slow, 2.356 s), 120 deg 1.3729 (2.741 s), 150 deg
  1.7622 (76.2 percent slow, 3.518 s), 170 deg 2.4394 (4.869 s), 179 deg
  3.9011 (7.787 s)
- top panel, 10.000 degrees: RK4 swing (out and back, turnaround to
  turnaround on the release side) first 2.000000 s, mean of the 20
  swings in 40 s 2.000000 s, min 2.000000, max 2.000000 (closed form
  2.000000, +8.9e-15); swings done at 40.000 s: 20, the last turnaround
  at 40.000000 s; bottom crossings at 0.500000, 1.500000, 2.500000 s ...
  (40 in 40 s), half swing mean 1.000000 s (spread 7.1e-15); speed at
  the bottom 0.5431 m/s (closed form sqrt(2 g L (1 - cos theta0)) =
  0.5431); 0 s above horizontal; energy drift 4.8e-14
- bottom panel, 103.415 degrees: first swing 2.500000 s, mean of the 16
  swings in 40 s 2.500000 s, min 2.500000, max 2.500000 (closed form
  2.500000, +5.3e-15); swings done at 40.000 s: 16, the last turnaround
  at 40.000000 s; bottom crossings at 0.625000, 1.875000, 3.125000 s ...
  (32 in 40 s), half swing mean 1.250000 s (spread 1.1e-14); speed at
  the bottom 4.8906 m/s (closed form 4.8906); per swing 0.8789 s above
  horizontal and 0.7600 s within 10 degrees of a turnaround (30.4
  percent of the swing for 19.3 percent of the arc); energy drift
  2.0e-14
- half-step check (7,200 steps per second): 10 degrees first swing
  2.000000 s (-5.8e-15), 20 swings at 40 s, last turnaround 40.000000 s,
  drift 3.5e-13; 103.415 degrees first swing 2.500000 s (-8.9e-16), 16
  swings, last turnaround 40.000000 s, drift 1.3e-14
- drift: the small swing gains 0.500 s a swing, a quarter swing every
  big swing; both bobs are at a turnaround together at 5, 15, 25 and 35
  s (small on the far side, big on the release side) and at 10, 20, 30
  and 40 s (both on the release side); the counters differ by up to 4
  swings
- counter schedule (real speed, both released at 0 s, the counter shows
  the swing in progress, 1 at the release): 0 s 1/1; 2.00 s 2/1; 2.50 s
  2/2; 5 s 3/3; 10 s 6/5; 15 s 8/7; 20 s 11/9; 25 s 13/11; 30 s 16/13;
  35 s 18/15; 39.98 s 20/16; the small counter ticks at 2, 4, 6 ... s
  and the big one at 2.5, 5, 7.5 ... s; the period readouts appear at
  2.000 s (small) and 2.500 s (big); the strip ticks at every swing
  start, 20 small and 16 big by the end
- text widths (DejaVuSans-Bold): overlay 729 px at 34; title lines 531,
  430 and 635 px at 56; panel labels 265 and 217 px at 40; sublabels 319
  and 300 px at 28; "swing" 92, stopwatch 267, "out and back" 205 and
  "timing" 102 px at 28; counter 122 px at 88; period 197 px at 48;
  clock 164 px at 40; payoff lines 540, 740 and 640 px at 40; nothing
  over 950 px; the left column budget is 332 px (the big bob never comes
  nearer than 20 px to x 370) and the widest column line is 319 px (the
  first draft's overlay "same pendulum | same length | real speed | no
  seed" measured 1,002 px and the sublabel "let go at 103.4 degrees" 369
  px; both were shortened before any render)

Narration numbers: ten degrees (setup, the small release, with the big
swing named as "up past horizontal"), two seconds a swing against two
and a half (payoff, the 2.000000 and 2.500000 s measured) and twenty
swings against sixteen after forty seconds (payoff, the counts at
40.000 s). The length, the solved angle, the elliptic-integral check,
the T / T0 table, the bottom speeds, the time above horizontal and the
coincidences go to the description. No number contradicted the claim.

### Production

- layout (`sims/bigswing/bigswing.py`): overlay at y 96, title at y
  190/252/314, two panels of 543 px from y 350 (top: 10 degrees, bottom:
  103.415 degrees) drawn at the same scale with the pivot at x 700, 100
  px under each panel top, and a 300 px rod (303 px per metre), so the
  bob sweeps x 384 to 1016 and the big bob rises 70 px above the pivot
  (14 px under the panel top at the turnaround); a dashed horizontal
  through the pivot, a dashed plumb line, the swing arc with a tick at
  each end, a marker under the arc bottom that flashes at every bottom
  crossing (with a ring that grows out of the bob), the rod, the pivot
  ring and the bob in the panel colour; the readouts in the left column
  x 40 to 370, which the bob never reaches: "small swing" / "big swing"
  at 40 px, "let go at 10 degrees" / "let go at 103.4 deg" at 28 px, the
  counter "swing N" (the swing in progress, 1 at the release, 88 px), a
  stopwatch "this swing 0.00 s" that restarts at every return to the
  release side, and "out and back" with the measured period of the last
  completed swing at 48 px ("timing" until the first swing completes,
  2.000 s from 2.0 s and 2.500 s from 2.5 s); a shared time strip at y
  845 between the panels (x 400 to 1016 for the 40 s) with a tick at the
  start of every swing (small ticks up in teal, big ticks down in coral;
  20 and 16 by the end, aligned at 10, 20, 30 and 40 s) and a white
  cursor, the elapsed clock at its left; from slow_mark_t the parts of
  the big arc above horizontal turn gold and the big bob turns gold
  while it is above horizontal (the "slow part"); captions at caption_y
  0.75, card from y 1592; geometry drawn at 2x and reduced; the loop:
  the pendulums are periodic over the 40 s, so only the counters, the
  stopwatch, the strip, the clock, the title and the card crossfade to
  the first frame over the last 0.5 s (HUD crossfade over the live
  geometry), and the last 4 frames blend the sub-pixel remainder of the
  bob positions to the first frame
- smoke frames (`--frames`, 10:19 EEST, at 0, 1.5, 2.2, 5.0, 12.5, 19.5,
  26.0, 33.0 and 39.9 s): the layout clean, the thumbnail (both bobs at
  their release positions under the question, the counters at 1) works,
  nothing clips, the readouts never meet the bob; one defect: at 26.0 s
  the small stopwatch read "-0.00 s" because the counter accepts a
  turnaround up to 1 ns after the frame time, so the elapsed time went
  slightly negative; fixed by clamping the stopwatch at 0 before the
  footage render; no second smoke pass was needed
- narration (written after the measure-only run, 10:20 EEST): three
  hooks tried, "One pendulum, top and bottom. Same pendulum, bigger
  swing. Does it take longer?" (recorded first: it passed the round trip
  but put the spoken question at 4.2 to 5.4 s and ran the voice to 36.5
  s; dropped), "Same pendulum, bigger swing. Does it take longer?"
  (kept: the title's own words, the question spoken by 3.5 s; the
  audio-initial "Same" was a clipped-onset risk and passed) and "Does a
  bigger swing take longer? Galileo said no." (dropped: the payoff could
  not answer it in the same words and it spends the Galileo beat before
  the setup); `projects/bigswing/narration.txt`, 103 words, 15
  sentences; the setup is "a small swing, ten degrees" and "the big
  swing goes up past horizontal", the payoffs "Two seconds a swing on
  top. Two and a half below." and "After forty seconds, twenty swings
  against sixteen."; "Below, ..." avoided at a sentence start (the
  day-22 mishearing), "in forty seconds" avoided ("in" between numbers
  comes back "and"), "gets ahead" chosen over "pulls ahead" ("pull" has
  come back "pole"); the setup sentence reordered so captions.py keeps
  "ten degrees" in one chunk ("On top, a small" / "swing, ten
  degrees."), and the payoff chunks are "Two seconds a swing" / "on
  top.", "Two and a half" / "below.", "After forty seconds," / "twenty
  swings" / "against sixteen." (34 chunks, checked with chunks() before
  recording)
- voice: take 1 (108 words, the first hook) passed at 10:21:52 EEST,
  35.91 s, ending at 36.51 s of video (3.0 words/s over 16 short
  sentences), rejected for the late question and the late ending; take
  2 (103 words) passed on its first run at 10:23:04 EEST with no
  misheard word ("two and a half" and "Galileo" came back as written;
  the numbers came back as digits and matched through the normaliser):
  33.34 s, ends at 33.94 s of the 40 s video, 3.1 words/s; log in
  `media/bigswing/voice.log`
- timing (`scripts/voice-timing.py`, +0.6 s offset, with the merged 23
  to 32 s span re-split at the 0.12 s pauses): "Same pendulum, bigger
  swing." 0.60 to 2.37 s under the title; "Does it take longer?" 2.37 to
  3.53 s as the small counter ticks to 2 (2.0 s) and both period
  readouts appear (2.0 and 2.5 s); "Both are let go at the same
  instant." 3.53 to 5.63 s; "On top, a small swing, ten degrees." 5.63
  to 8.16 s; "Under it, the big swing goes up past horizontal." 8.16 to
  11.24 s with the big bob at its far turnaround at 8.75 s and above
  horizontal on the release side at 10.0 s; "Galileo said a swing takes
  the same time, big or small." 11.24 to 14.88 s; "Watch the counters."
  14.88 to 16.05 s (counters 8 and 7 at 15 s); "The small swing gets
  ahead, a little more every swing." 16.05 to 19.24 s; "The big swing
  climbs high and almost stops at the top of every swing." 19.24 to
  23.10 s with the gold slow-part mark from 19.4 s and the big bob at
  its turnarounds at 20.0, 21.25 and 22.5 s; "That slow part is where
  the extra time goes." 23.10 to 25.77 s; "So does it take longer?"
  25.77 to 27.03 s with the card fading in from 25.8 s; "Yes." 27.03 to
  27.67 s; "Two seconds a swing on top. Two and a half below." 27.67 to
  30.44 s with 2.000 s and 2.500 s in the readouts and 2.0 s / 2.5 s on
  the card; "After forty seconds," 30.44 to 31.84 s; "twenty swings
  against sixteen." 31.84 to 33.85 s with "20 swings against 16 in 40 s"
  on the card and the counters at 17 and 14; the counters reach 20 and
  16 at 38.0 and 37.5 s and hold to the loop
- schedule decisions: real speed, both released at 0 s (motion from the
  first frame; the first frame is the bobs at rest at their release
  positions under the title); the counter shows the swing in progress
  because a completed-swing counter would reach 20 and 16 only at
  40.000 s, the loop point, and never be seen; slow_mark_t 19.4 s from
  the timing of "climbs high"; payoff_t 25.8 s from the timing of "So
  does it take longer?"; title until 2.4 s
- footage: `sims/bigswing/bigswing.py` (no arguments) wrote
  `media/bigswing/footage.mp4`, 40.00 s at 60 fps, 2,400 frames, h264
  crf 16 yuv420p, in 36 s with eight forked workers, 10:24:25 to
  10:25:01 EEST; the same run re-printed every measurement above
  (`media/bigswing/render.log`); loop check on the raw frames: the last
  frame differs from the first in 0 px (max channel difference 0)
- compose: `scripts/compose.sh bigswing` wrote `media/bigswing/final.mp4`
  at 10:25:18 EEST (h264 1080x1920 60 fps, aac 22050 Hz mono, 40.000 s;
  music seed 71 at gain 0.18; captions at caption_y 0.75, 35 drawtext
  filters: the overlay and 34 caption chunks); loudness mean -15.9 dB,
  peak 0.0 dB; preview (40.07 s) and 8x5 contact sheet written
  (`media/bigswing/compose.log`)

### Local QA

- smoke pass (10:19 EEST, `--frames` before any render): one defect
  found and fixed (the "-0.00 s" stopwatch; see Production); the layout,
  the widths, the column budget and the vertical spacing were clean
- final pass (10:26 to 10:28 EEST): frames at 0.02, 1.5, 2.6, 8.5, 20.2,
  26.3, 28.5, 32.5, 35.0 and 39.95 s extracted from final.mp4
  (`media/bigswing/frame-*.png`) and inspected with the 8x5 contact
  sheet (`media/bigswing/sheet.png`): 0.02 s shows the overlay at y 96,
  the title "Same pendulum, / bigger swing. / Does it take longer?" at y
  190 to 314 clear of it and of the panels, both bobs at rest at their
  release positions (the small at 10 degrees, the big at 103.4 degrees
  above the dashed horizontal), both counters at "swing 1", "timing" in
  both period slots and the clock at 0.03 s (the thumbnail); 1.5 s shows
  both bobs falling toward the bottom under "bigger swing."; 2.6 s shows
  "Does it take longer?" with the small counter at 2, the big at 2, the
  readouts "2.000 s" and "2.500 s" both lit, the small bob crossing the
  bottom with the flash ring and the strip with the two release ticks
  and the 2.0 s teal tick; 8.5 s shows "Under it, the big" with the big
  bob on the far side just above horizontal and the counters 5 and 4;
  20.2 s shows "high and almost" with the gold slow-part arcs lit and
  the big bob gold at its release-side turnaround, counters 11 and 9;
  26.3 s shows "So does it take" with the card fading in ("does it take
  longer? yes / 2.0 s a swing on top, 2.5 s below / 20 swings against
  16 in 40 s") and the big bob gold at its far turnaround, counters 14
  and 11; 28.5 s shows "Two seconds a swing" with the card fully lit,
  the readouts 2.000 s and 2.500 s and the counters 15 and 12; 32.5 s
  shows "After forty seconds," with the counters 17 and 14 and the big
  bob gold at its turnaround; 35.0 s shows the counters 18 and 15 under
  the card with no caption; 39.95 s shows the crossfade to the title
  frame with the card fading out, the counters "1" over the faint "20"
  and "16" and the strip's ticks fading; the contact sheet shows every
  caption in the y 1440 to 1520 band under the geometry (the bottom
  panel's lowest element, the flash marker, ends at y 1341) and the card
  from y 1592, the title only in the first two tiles and the last, the
  counters climbing 1/1 to 20/16 with the drift and the realignments at
  10, 20 and 30 s; captions match the narration word for word (they are
  generated from the narration file; 34 chunks); no text clips at the
  frame edges (the widest lines are the overlay at 729 px and the
  payoff at 740 px, the big bob's outer edge reaches x 1008); the payoff
  numbers are on screen when spoken (card from 25.8 s, the readouts
  from 2.5 s, "two seconds" at 27.67 s, "two and a half" at about 29 s,
  "twenty swings against sixteen" at 31.84 s); the loop closes: the raw
  render's last frame differs from the first in 0 px; on the encoded
  final.mp4 frames 0 and 2399 differ in 2,787 px above a channel
  difference of 24 (max 75), all of it at text and line edges (0 px in
  the caption band and 0 px in the card band, so no caption or card
  leaks into the loop point), against 1,050 to 1,723 px for adjacent
  encoded frames (frames 0 and 1, 1 and 2, 2398 and 2399) and 0 px after
  a 5x5 box blur of both frames, so the difference is encoder noise
- ffprobe of final.mp4: h264 1080x1920 60/1 fps, 2,400 frames, yuv420p;
  aac 22050 Hz mono; 40.000000 s; 4,277,093 bytes; atom order ftyp moov
  free mdat (moov before mdat, faststart); md5
  ed715482d4f1f616feecdfca931e72ef; approved

### Metadata

- `projects/bigswing/metadata.json`: title "Same pendulum, bigger swing.
  Does it take longer? Yes: 2.0 s a swing at 10 degrees, 2.5 s at 103."
  (97 characters; the question, the setup number and the payoff
  number); description with the setup (one pendulum drawn twice, 0.9898
  m, g, the two release angles, the length chosen for 2.000 s and the
  angle solved for 2.500 s from the elliptic-integral closed form, RK4
  at 3,600 steps per second, no seed, real speed, what the counter and
  the strip show), a Measured list (the closed form with K(sin 5 deg),
  L, T0, the solved angle with its K check and the 1.2500 ratio; the 10
  degree run with its 20 swings, 40 crossings, bottom speed and drift;
  the 103.415 degree run with its 16 swings, 32 crossings, bottom
  speed, rise above the pivot, time above horizontal and near the
  turnarounds, and drift; the T / T0 table from 30 to 179 degrees; the
  drift and coincidence schedule with the counter readings; the
  half-step check and the loop), a Why paragraph (the push back toward
  the bottom grows only as the sine of the angle, so Galileo's rule is
  the small-angle limit; past 90 degrees the push shrinks again and the
  big bob lingers near the top of every swing, where the extra half
  second goes), the rerun line and the AI-made line; 10 tags (pendulum,
  pendulum period, large amplitude pendulum, Galileo, elliptic integral,
  simple harmonic motion, physics, physics visualization, simulation,
  shorts); category 27; private; containsSyntheticMedia true;
  selfDeclaredMadeForKids false
- not uploaded; task left open for the orchestrator's review and upload

### Release

- orchestrator review (10:36 EEST): the task evidence, the 8x5 contact
  sheet and the full-resolution frames at 0.02, 2.6, 20.2, 28.5 and
  39.95 s inspected: the question over the two pendulums at their
  release marks on the first frame, both counters at 1; 2.6 s shows
  "Does it take longer?" with both period readouts lit (2.000 s and
  2.500 s) and the first ticks on the strip; 20.2 s shows the gold
  slow-part arcs and the gold bob near its top under "high and almost";
  28.5 s shows the card "does it take longer? yes / 2.0 s a swing on
  top, 2.5 s below / 20 swings against 16 in 40 s" under "Two seconds a
  swing" with the counters at 15 and 12; 39.95 s shows the crossfade to
  the title frame with the card fading out; every caption in the clear
  band, no clipping; final.mp4 h264 1080x1920 60 fps, 2,400 frames, aac
  22050 Hz mono, 40.000 s, moov before mdat, md5
  ed715482d4f1f616feecdfca931e72ef; title 97 characters; approved for
  release
- quota check: clock 2026-09-21T10:37:09+03:00; zero upload attempts recorded since the
  2026-09-21 10:00 EEST boundary (no upload entries in web/data/log.jsonl
  today, newest media/*/upload.log is hingedstick at 2026-09-20 10:48);
  this is insert attempt 1 of the hard cap of 5
- attempt 1 recorded at 2026-09-21T10:37:09+03:00, video name bigswing, before running
  `scripts/yt-upload.py bigswing`

### Published

- upload: `scripts/yt-upload.py bigswing` ran 10:37:09 to 10:37:15 EEST,
  token verified to see only the Seed Zero channel, video id
  AO0xsAawEUw, private (`media/bigswing/upload.log`)
- gate: `scripts/yt-qa.py bigswing AO0xsAawEUw --wait --publish` ran in
  the foreground from 10:37:26 EEST: processing succeeded and the 10
  tags read back on the first poll, 15 of 15 pass (processed, succeeded,
  hd, 1080x1920, title, description, tags as a set, category 27, not for
  kids, PT41S for the 40.000 s file, private); containsSyntheticMedia
  reads absent as on every earlier upload (`media/bigswing/publish.log`)
- publish: the same run set the video public at 2026-09-21T10:37:49+03:00;
  the re-read after 15 s shows privacyStatus public, madeForKids false,
  embeddable true; public at https://youtu.be/AO0xsAawEUw
- slot resolution: published for the 2026-09-21 quota day

### Quota

- attempt 1 of the hard cap of 5 for the quota day that began
  2026-09-21T10:00 EEST; cost 1 + 1,600 + 53 = 1,654 units (the
  channels.list verification inside yt-upload.py, the insert, the gate
  run's read, update and re-read as printed by yt-qa.py); day total
  after one attempt 1,654 units

### Repository
