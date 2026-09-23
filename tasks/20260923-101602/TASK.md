# Produce short: Racing balls, a flat track beside a dip at the same launch speed

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day25

## Goal

Backlog idea (trend research 2026-09-23, task 20260923-101345, pillar 2
chaos and physics, energy; read the full entry under "Added by trend
research 2026-09-23" in docs/niche.md):
"Racing balls: two equal balls launched at 1.0 m/s, a flat 2 m track
beside a track that dips 20 cm on cosine ramps and returns to the same
height; measure the arrival times; expect the dip to arrive at 1.544 s
against 2.000 s (v = sqrt(v0^2 + 2 g depth) along the track, flat time
L/v0), a 0.456 s win on a track 2.14 m long (7 percent longer), top
speed 2.22 m/s in the dip; the race repeats so the short loops;
deterministic, no seed."
Research feasibility numbers (task 20260923-101345): a frictionless
bead-on-wire RK4 run at 0.1 ms agrees with the closed form to four
decimals (1.5438 s, exit speed 1.0000 m/s); a rolling solid ball (k 2/5,
no slip) wins by 0.380 s instead.
Day twenty-five, third slot. Chosen because it is a path race on the
same start, the same launch speed and the same finish, the format of the
channel's best shorts (brachistochrone 948 views, rolling race 950), and
because most viewers predict a tie or the flat track. Question in the
first two seconds: "Same speed, same finish. Does the dip slow it down?"
(or the producer's better wording, kept identical in the title, the hook
and the payoff). Model choice is the producer's: prefer the rolling solid
ball (k 2/5, as in sims/rollingrace, since the title says balls; the
closed form is v = sqrt(v0^2 + 2 g depth / (1 + k))); the sliding puck is
acceptable. State the model in the overlay and the description, check
and print that the track force never drops to zero (no lift-off at the
ramp crests), and narrate only the numbers of the chosen model.

## Claim

Two equal balls leave the same line at one meter a second toward the
same finish two meters away, one on a flat track and one on a track
that dips twenty centimeters and comes back up: the dip ball arrives
first, near one point six seconds against two point zero for the flat
track (exact numbers from the sim), because it goes faster inside the
dip and gives that speed back only at the end. Every number in the
narration is printed by the sim before the script is written.

## Evidence

### Measurements

(recorded after the measure-only run, before scripting)

`sims/racingballs/racingballs.py --measure-only` with
`projects/racingballs/manifest.json` (two equal solid balls, I = 2/5 m
r^2, radius 4 cm, leave the same start line at 1 m/s toward a finish
line 2 m away; the top track is flat; the bottom track is flat to x =
0.3 m, drops 20 cm on a cosine ramp 0.5 m long, runs a flat floor 0.4 m
long, climbs a cosine ramp 0.5 m long back to the top at x = 1.7 m and
runs flat to the finish; the ball centre follows the profile; rolling
without slip, no losses, g = 9.80665; RK4 in x at 10,000 steps per
second, the crossing interpolated inside the last step, the speed
checked against the energy closed form v = sqrt(v0^2 + 2 g depth / (1 +
k)) at every step; played at quarter speed, 4 races of 10 s; drawn at
450 px per metre, 900 px across with 90 px margins, the dip 90 px deep;
deterministic, no seed; run at 10:28:53 EEST, log in
`media/racingballs/measure.log`):

- geometry decision: the research profile (0.3 m ramps, 0.6 m floor,
  `/tmp/rt6/racing.py`) has a crest curvature of 10.97 1/m (radius 9.1
  cm); at 1 m/s the track force there is -0.118 of the weight, so the
  ball would lift off at both crests. Scratch comparison
  (`/tmp/racingballs/geom.py`, rolling ball, dt 1e-4 s): 0.3 m ramps
  1.6199 s, force -0.118; 0.4 m ramps with a 0.6 m floor 1.5400 s,
  force 0.371; 0.5 m ramps with a 0.4 m floor 1.5637 s, force 0.594;
  0.6 m ramps with a 0.2 m floor 1.5911 s, force 0.705. Chosen: 0.5 m
  ramps, 0.4 m floor, 0.3 m flat at each end (a force margin of 0.59
  of the weight, the dip spanning 1.4 m of the 2 m track so it reads on
  screen)
- flat track: arrives at 2.0000 s (closed form L / v0 = 2.0000 s, diff
  0), speed at the finish 1.0000 m/s, track force 1.0000 of the weight
  throughout, max |v - closed form| 0
- dip track: arrives at 1.5637 s (quadrature of ds / v(s) 1.5637 s,
  diff 9.5e-9); track length 2.0924 m, 0.0924 m (4.6 percent) longer
  than the flat track; top speed 1.9498 m/s (closed form sqrt(v0^2 + 2
  g d / (1 + k)) = 1.9498) first reached at x = 0.8001 m, t = 0.6793 s,
  held along the floor to x = 1.2 m; speed at the finish 1.0000 m/s
  (the launch speed); max |v - closed form| over all steps 2.2e-8 m/s
- lead: the dip ball is ahead by at most 0.4363 m, first at t = 1.2629
  s (x = 1.6992 m, the top of the exit ramp), and by 0.4363 m when it
  arrives (the flat ball is at x = 1.5637 m); it wins by 0.4363 s (21.8
  percent of the flat time)
- track force on the dip ball (units of the weight): minimum 0.5939 at
  x = 0.3693 m, maximum 2.5305 at x = 0.7999 m; at the entry crest (x =
  0.3 m, curvature -3.948 1/m, radius 0.253 m) 0.5974, at the exit crest
  (x = 1.7 m) 0.5974; positive everywhere, no lift-off
- horizontal speed of the dip ball: minimum 1.0000 m/s (at x = 1.7 m,
  the flat ball's speed), so the dip ball is never behind the flat
  ball; speed along the track never below 1.0000 m/s
- dip crossing: the dip ball enters the dip at t = 0.3000 s and is back
  at the top at t = 1.2637 s, 0.9637 s for 1.4 m of horizontal distance
  that the flat ball covers in 1.4000 s
- half-step check: 1.563689 s at dt 5e-5 s against 1.563689 s at 1e-4 s
  (diff 2.3e-9 s)
- for the description: a sliding bead (k = 0, no spin) on the same dip
  arrives at 1.4823 s (quadrature 1.4823), top speed 2.2187 m/s (closed
  form 2.2187), wins by 0.5177 s, minimum track force 0.5683 of the
  weight (the research's 1.5438 s and 2.219 m/s were for its steeper
  0.3 m ramps)
- schedule printed by the sim (video time, quarter speed): each 10 s
  race releases both balls at 0.4 s, the dip ball arrives 6.25 s after
  the release and the flat ball 8.00 s after; clocks frozen for 0.70 s,
  then a 0.4 s slide back to the start and 0.5 s at rest; arrivals at
  6.65/8.40, 16.65/18.40, 26.65/28.40, 36.65/38.40 s (dip/flat); title
  until 2.4 s; payoff card from 26 s in the first manifest, to be set
  from the voice timing; loop fade 39.5 to 40 s over balls at rest
- text widths (DejaVuSans-Bold): overlay 894 px at 34 (the first draft
  "same launch 1 m/s | rolling ball | quarter speed | no seed" was
  1,092 px, shortened before any render); title lines 806 and 849 px at
  56; counter 240 px at 40; model tag 629 px at 28; track labels 165
  and 161 px at 32; clock "t 1.62 s" 271 px and the frozen "2.00 s" 218
  px at 64; "arrived" 130 px at 32; speed readout 239 px at 28; "start"
  76, "finish" 87, "20 cm" 94 px at 28; payoff lines 571, 602, 785 and
  428 px at 40; nothing over 950 px

Narration numbers: the dip is twenty centimeters deep (setup; the 1
m/s launch stays on the overlay and both speed readouts); one point
five six seconds on the dip track against two point zero on the flat
track (payoff; the measured 1.5637 and 2.0000, shown as 1.56 and 2.00
on the clocks and the card). The 0.44 s gap, the track length, the top
speed, the track force, the bead numbers and the checks go to the
description. The claim's "near one point six seconds" holds (1.5637
rounds to 1.6); it is not the research's 1.62 because the ramps had to
be lengthened from 0.3 to 0.5 m to keep the ball on the track. No
number contradicted the claim; the claim text is left as written.

### Production

- layout (`sims/racingballs/racingballs.py`): overlay at y 96, title at
  y 190/252 for the first 2.4 s, then the race counter "race k of 4" at
  y 236 and the model tag "solid ball, rolling without slip, no losses"
  at y 290; "start" and "finish" labels at y 480 over dashed lines that
  span both tracks (x 90 and 990); two tracks stacked at 450 px per
  metre: the flat track with its readout row at y 550 (label at 32 px
  in the track colour, "speed 1.00 m/s" at 28 px under it, the live
  clock "t 1.23 s" at 64 px right-aligned at x 980) and its ball level
  at y 740; the dip track with its row at y 890, its ball level at y
  1080 and the dip floor at y 1170; each track surface is the ball
  centre path offset down by the 4 cm ball radius (18 px), drawn 8 px
  thick in the track colour at alpha 0.55, teal for the flat track and
  gold for the dip; a dashed gold line continues the flat surface
  across the dip and a bracket at the dip centre carries "20 cm"; the
  balls are 18 px discs with a dark spoke that turns with the rolled
  arc length and a highlight, a 0.25 s fading trail behind them, and a
  0.6 s expanding ring at each arrival; at arrival the clock freezes
  in the track colour ("1.56 s") with a 32 px "arrived" tag to its
  left and the speed readout freezes at the finish speed; each 10 s
  race releases both balls at 0 s, holds the frozen clocks 1.1 s after
  the flat arrival, slides both balls back along their tracks over 0.4
  s (readouts fade to "t 0.00 s") and rests 0.5 s so the loop fade
  plays over balls at rest; captions at caption_y 0.75; the four-line
  card from y 1592; geometry drawn at 2x and reduced
- whisper pre-test (10:31:19 to 10:31:28 EEST, before the full take;
  `media/racingballs/hooks/`): three hook variants and two sentence
  groups round-tripped through `scripts/voiceover.sh`, all passed on
  the first pass: "Same speed, same finish. Does the dip slow it down?
  Two balls leave the line together." (5.45 s; the sentence-initial
  "Same" not clipped), "Two balls. Same speed, same finish. Does the
  dip slow it down?" (4.47 s), "One dip. Same speed, same finish. Does
  the dip slow it down?" (4.31 s), the mechanism group "Watch the
  bottom ball. It speeds up on the way down, and slows on the way back
  up to the launch speed. The dip track is longer, but every meter
  inside the dip is faster. The dip ball never falls behind, not for a
  moment. Race after race, the same result." (14.80 s) and the payoff
  group "It arrives first, at one point five six seconds. The flat
  ball takes two point zero seconds. So, does the dip slow it down?
  No. It makes it faster." (9.50 s; both numbers came back as 1.56 and
  2.0)
- smoke frames (`--frames`, pass 1 at 10:28:01 EEST with release_at
  0.5 s, at 0, 1.5, 3.5, 6.75, 7.5, 8.5, 9.8, 26.75, 30 and 39.8 s):
  one defect: the last race's 0.4 s slide-back overlapped the 0.5 s
  loop fade, so ghost balls sat 0.3 m along both tracks at 39.9 s;
  fix: a rest_dur of 0.5 s after the reset (the sim asserts rest_dur >=
  loop_fade), the reset now ends at 9.5 s of each race; pass 2 at
  10:32:26 EEST after the timing (release_at 0, payoff_t 24.8; at 0,
  1.2, 2.7, 6.25, 8.0, 9.3, 26.25, 28.0, 33 and 39.9 s) clean: the
  title over both balls at the start line, the dip ball at 1.95 m/s on
  the floor at 2.7 s, the mid-reset frame with the readouts faded and
  the balls sliding back, the card lit at 26.25 s one frame before the
  dip arrival, the balls at rest under the crossfade at 39.9 s;
  nothing clips, nothing enters the caption band
- narration (written after the measure-only run, 10:31 EEST): the
  first hook kept because it puts the question at 1.86 s (the title's
  words in the title's order) and the pre-test showed the "Same" onset
  survives; the "Two balls." and "One dip." variants would delay the
  question to 2.5 s; `projects/racingballs/narration.txt`, 108 words;
  the balls named by their tracks ("the dip ball", "the flat ball"),
  matching the labels; the setup number is "twenty centimeters"
  (chunked whole as "twenty centimeters" after "The other track dips",
  chosen over "The bottom track dips" which split "twenty |
  centimeters"); "one point five six" and "two point zero" each sit
  whole in one caption chunk ("It arrives first, at | one point five
  six | seconds." and "The flat ball takes | two point zero |
  seconds."), checked with chunks() before recording; "Watch the
  bottom ball." changed to "Watch the dip ball." so it is one chunk;
  "still", "pull", "got", "spread", "straight" and "a hundred" avoided;
  no possessives; the narration order (dip ball first, flat ball
  second) follows the arrival order on screen
- voice: `scripts/voiceover.sh projects/racingballs/narration.txt`
  pass 1 at 10:31:43 EEST passed, "ok: transcript matches narration":
  108 words, 33.02 s, ends at 33.62 s of the 40 s video, 3.27 words/s;
  log in `media/racingballs/voice.log`
- timing (`scripts/voice-timing.py`, +0.6 s offset, log in
  `media/racingballs/timing.log`): "Same speed, same finish. Does the
  dip slow it down? Two balls leave together." 0.60 to 5.31 s (the
  question starts near 1.9 s, inside the title's 2.4 s); "One track is
  flat." 5.31 to 6.55; "The other track dips 20 centimeters and comes
  back up. Watch the dip ball." 6.55 to 10.99 with the race 1 arrivals
  at 6.25 and 8.00 s; "It speeds up on the way down," 10.99 to 12.89
  with the race 2 ball on the entry ramp from 11.2 s; "and slows on
  the way back up to the launch speed. The dip track is longer," 12.89
  to 16.95 with the exit ramp 13.5 to 15.05 s and the dip arrival at
  16.25 s; "but every meter inside the dip is faster." 16.95 to 19.23
  with the flat arrival at 18.00 s; "The dip ball never falls behind."
  19.23 to 21.34; "Not for a moment. Race after race. The same result."
  21.34 to 24.42 with race 3 released at 20.0 s; "It arrives first."
  24.42 to 25.59; "At 1.56 seconds." 25.59 to 27.53 with the dip
  arrival at 26.25 s on the number and the gold clock frozen from
  there; "The flat ball takes 2.0 seconds. So, does the dip slow it
  down? No. It makes it faster." 27.53 to 33.50 with the flat arrival
  at 28.00 s on "takes"; the piece after 33.50 s is the closing
  silence (whisper returned "Thank you." for it; the full-file round
  trip matched); race 4 (30 to 40 s) plays under the card
- schedule decisions: release_at 0 (both balls leave on the first
  frame, motion in progress under the title, as in rollrace) so that
  the race 3 arrivals land at 26.25 s inside "at one point five six
  seconds" (25.59 to 27.53) and at 28.00 s on "The flat ball takes"
  (from 27.53); a later release would push the dip arrival past the
  spoken number and shorten the 1.1 s hold; payoff_t 24.8 s from the
  timing, so the card is fully lit at 25.4 s, before the first payoff
  number at 25.59 s and 0.85 s before the dip ball arrives; the card
  names the flat time 2.6 s before the flat ball arrives, as the
  lifeguard card did
- footage: `sims/racingballs/racingballs.py` (no arguments) wrote
  `media/racingballs/footage.mp4`, 40.00 s at 60 fps, 2,400 frames,
  h264 crf 16 yuv420p, in 33 s with eight forked workers, 10:32:47 to
  10:33:20 EEST; the same run re-printed every measurement above
  (`media/racingballs/render.log`); loop check on the raw frames: the
  last frame differs from the first in 0 px (max channel difference 0)
- compose: `scripts/compose.sh racingballs` wrote
  `media/racingballs/final.mp4` at 10:33:31 EEST (h264 1080x1920 60
  fps, 2,400 frames, aac 22050 Hz mono, 40.000 s, 2,803,546 bytes;
  music seed 79 at gain 0.18; captions at caption_y 0.75, 35 drawtext
  filters, the overlay plus 34 caption chunks); loudness mean -16.3 dB,
  peak -0.0 dB; preview (40.07 s) and 8x5 contact sheet written
  (`media/racingballs/compose.log`)

### Local QA

- smoke pass 1 (10:28:01 EEST, `--frames` before any render): one
  defect found and fixed (the slide-back under the loop fade; see
  Production); smoke pass 2 (10:32:26 EEST) clean before the footage
  render
- final pass (10:34 EEST): frames at 0.02, 1.5, 2.7, 6.25, 8.0, 16.0,
  26.3, 28.05, 30.5 and 39.95 s extracted from final.mp4
  (`media/racingballs/frame-*.png`) and inspected with the 8x5 contact
  sheet (`media/racingballs/sheet.png`): 0.02 s shows the overlay
  "launch 1 m/s | rolling ball | 1/4 speed | no seed" at y 96, the
  title "Same speed, same finish. / Does the dip slow it down?" at y
  190 and 252 clear of it, "start" and "finish" over the dashed lines,
  both balls on the start line, both clocks "t 0.01 s", both speed
  readouts "1.00 m/s", the dip with its "20 cm" bracket (the
  thumbnail); 1.5 s shows the dip ball at the dip entry at "speed 1.08
  m/s" with its trail, the flat ball level with it, under "Same speed,
  same"; 2.7 s shows the counter "race 1 of 4" and the model tag in
  place of the title, the dip ball on the floor at "speed 1.95 m/s"
  well ahead of the flat ball, under "Does the dip slow it"; 6.25 s
  shows the dip ball on the finish line one frame before arrival at
  "t 1.56 s" with the flat ball 0.44 m short, under "The other track
  dips"; 8.0 s shows "arrived 2.00 s" in teal beside "arrived 1.56 s"
  in gold with the teal arrival ring, under "and comes back up."; 16.0
  s shows race 2 with the dip ball back at 1.00 m/s on the exit flat,
  under "The dip track is"; 26.3 s shows the race 3 dip arrival, the
  gold ring and "arrived 1.56 s" in gold, the flat clock at "t 1.58
  s", under "one point five six" with the card lit; 28.05 s shows both
  arrived under "The flat ball takes"; 30.5 s shows race 4 just
  released under "So, does the dip" with the card; 39.95 s shows the
  crossfade to the title frame with the card and the counter fading;
  captions match the narration word for word (the contact sheet reads
  every chunk in order) and sit in the y 1440 to 1520 band with the
  lowest geometry at y 1193 (the dip floor surface) and the card from
  1592; the widest text (the overlay, 894 px) is centred with 93 px
  margins and nothing clips at the frame edges; the payoff numbers are
  on screen when spoken (the card from 25.4 s and the gold clock from
  26.25 s against "at 1.56 seconds" 25.59 to 27.53; "2.00 s" on the
  card from 25.4 s and the frozen teal clock from 28.00 s against "The
  flat ball takes 2.0 seconds" from 27.53); the loop closes: the raw
  last frame differs from the raw first frame in 0 px (render.log),
  and on the encoded final frame 2399 differs from frame 0 in 1,969 px
  by more than 24 levels (0.09 percent, at text edges, max channel
  difference 72, mean 0.37, encoder noise); ffprobe: h264 1080x1920,
  60/1 fps, 2,400 frames (also by decode), aac 22050 Hz mono,
  40.000000 s, atoms ftyp, moov, free, mdat (moov before mdat), md5
  27f217a250aedae208b4aab8b42d0aeb; approved locally

### Metadata

- `projects/racingballs/metadata.json`: title "Same speed, same
  finish. Does the dip slow it down? No: dip ball 1.56 s, flat ball
  2.00 s" (89 characters); description with the setup (1 m/s launch, 2
  m to the finish, the flat track, the dip profile 0.3 + 0.5 + 0.4 +
  0.5 + 0.3 m with 20 cm depth, the rolling solid ball with k = 2/5
  and the closed form, the centre following the profile, RK4 at
  10,000 steps per second, quarter speed, no seed), a Measured list
  (2.0000 s against 1.5637 s, the quadrature, the 2.0924 m track 4.6
  percent longer, the top speed 1.9498 m/s, the finish speed 1.0000
  m/s, the 0.4363 s and 0.4363 m win, the horizontal speed never below
  1.00 m/s, the track force 0.594 to 2.53 of the weight, the bead's
  1.4823 s and 2.2187 m/s, the half-step and closed-form checks, the
  rejected 0.3 m ramps), a Why paragraph in plain words (gravity
  speeds the ball up on the way down and slows it by the same amount
  on the way up; inside the dip it is never slower than 1 m/s; at
  every instant it has moved at least as far as the flat ball; a ball
  that is never slower cannot arrive later, so it arrives first even
  on the longer track; a rolling ball gains less than a sliding one
  because part of the fall goes into spin), the rerun line and the
  AI-made line; 10 tags (racing balls, energy conservation, rolling
  ball, which ball wins, physics race, kinetic energy, physics,
  physics visualization, simulation, shorts); category 27; private;
  containsSyntheticMedia true; selfDeclaredMadeForKids false; the same
  keys in the same order as projects/lifeguard/metadata.json
- not uploaded; task left open for the orchestrator's review and upload

### Release

- orchestrator review (10:37 EEST): the task evidence, the 8x5 contact
  sheet and the full-resolution frames at 0.02, 8.0, 26.3 and 39.95 s
  inspected: the question "Same speed, same finish. / Does the dip slow
  it down?" over the two stacked tracks, the flat track above and the
  dip track with its "20 cm" depth mark below, both balls on the start
  line at "speed 1.00 m/s" and "t 0.01 s" on the first frame; 8.0 s
  shows race 1 finished with "arrived 2.00 s" on the flat track and
  "arrived 1.56 s" in gold on the dip track under "and comes back up.";
  26.3 s shows the race-3 dip arrival, "arrived 1.56 s" with the flat
  ball still at "t 1.58 s", the card "same speed, same finish. / does the
  dip slow it down? / no: the dip ball arrives first, 1.56 s / the flat
  ball: 2.00 s" lit under "one point five six"; 39.95 s shows the
  crossfade to the title frame with the race counter fading under it,
  as in the rollrace and lifeguard shorts; the voice timing puts the
  question inside the first piece (0.60 to 5.31 s, four words before
  it), with the title question on screen from frame 0; the producer's
  ramp change (0.5 m cosine ramps so the track force stays at 0.59 of
  the weight, arrival 1.5637 s instead of the research's 1.62 s) accepted
  as recorded in the task; every caption in the clear band, no clipping;
  final.mp4 h264 1080x1920 60 fps, 2,400 frames, aac 22050 Hz mono,
  40.000 s, moov before mdat, md5 27f217a250aedae208b4aab8b42d0aeb; title
  89 characters; approved for release
- quota check: clock 2026-09-23T10:41:22+03:00; two upload attempts (springswap, 10:38:12,
  published as utBc09NZWUk at 10:39:20; zenobounce, 10:39:37, published
  as mgoguyVzOmU at 10:40:44) recorded since the 2026-09-23 10:00 EEST
  boundary (log entries and media/*/upload.log both checked); this is
  insert attempt 3 of the hard cap of 5
- attempt 3 recorded at 2026-09-23T10:41:22+03:00, video name racingballs, before running
  `scripts/yt-upload.py racingballs`

### Published

- upload: `scripts/yt-upload.py racingballs` ran 10:41:00 to 10:41:27 EEST,
  token verified to see only the Seed Zero channel, video id
  KYBHKNWUuI4, private (`media/racingballs/upload.log`)
- gate: `scripts/yt-qa.py racingballs KYBHKNWUuI4 --wait --publish` ran
  in the foreground from 10:41:34 EEST: processing succeeded and the 10
  tags read back on the first poll, 15 of 15 pass (processed, succeeded,
  hd, 1080x1920, title, description, tags as a set, category 27, not for
  kids, PT41S for the 40.000 s file, private); containsSyntheticMedia
  reads absent as on every earlier upload
  (`media/racingballs/publish.log`)
- publish: the same run set the video public at 2026-09-23T10:42:21+03:00;
  the re-read after 15 s shows privacyStatus public, madeForKids false,
  embeddable true; public at https://youtu.be/KYBHKNWUuI4
- slot resolution: published for the 2026-09-23 quota day

### Quota

- attempt 3 of the hard cap of 5 for the quota day that began
  2026-09-23T10:00 EEST; cost 1 + 1,600 + 55 = 1,656 units (the
  channels.list verification inside yt-upload.py, the insert, the gate
  run's reads, update and re-read as printed by yt-qa.py); day total
  after three attempts 4,966 units, target of three met

### Repository

- committed as 93c0496 "Publish the day twenty-five slate" (sims,
  projects, tasks, docs/niche.md, web/data; no media, previews or
  secrets) and pushed to origin/master at 2026-09-23 10:44 EEST
