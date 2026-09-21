# Produce short: Tetherball versus hole, a puck on a shortening string

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day23

## Goal

Backlog idea (trend research 2026-09-20, task 20260920-100347, pillar 2
chaos and physics):
"Tetherball versus hole: a puck on ice at 1 m/s on a 50 cm string, one
string wrapping a 2.5 cm pole beside one pulled through a hole at 10
cm/s; measure the speed at half the string; expect the pole puck to keep
1.00 m/s all the way in (3.02 turns, hits the pole at 4.99 s, the string
does no work) and the hole puck to double to 2.00 m/s at 25 cm and reach
10 m/s at 5 cm (angular momentum; 14.3 turns in 4.5 s); deterministic,
no seed."
Day twenty-three, third slot. Chosen because spinning tabletop motion in
two panels on the same input is the channel's proven format (ball on a
spinning record 1,042 views, hoop bead 984, top precession 909, coupled
pendulums 1,085) and the contrast is clean: both strings get shorter,
only one puck speeds up. Question in the first two seconds: "The string
gets shorter. Does the puck speed up?" (or the producer's better
wording, kept identical in the title, the hook and the payoff).

## Claim

A puck on a fifty centimeter string at one meter per second keeps one
meter per second while its string wraps a pole, but doubles to two
meters per second by the time the string is pulled in to twenty five
centimeters through a hole. Every number in the narration is printed by
the sim before the script is written.

## Evidence

### Measurements

(recorded after the measure-only run, before scripting)

`sims/tetherball/tetherball.py --measure-only` with
`projects/tetherball/manifest.json` (a puck on frictionless ice at v0 =
1 m/s on a string of L0 = 0.50 m, released at the same instant in two
panels at the same scale, 400 px per metre so the string is 200 px; top
panel: the string runs through a hole in the ice and is pulled in at u =
10 cm/s, r = L0 - u t, until r = 5 cm, then held; bottom panel: the
string wraps a fixed pole of radius a = 2.5 cm (10 px), the puck runs on
the involute of the pole circle with the free length l obeying l dl/dt =
-a v0; both runs are drawn from the closed forms and checked by a
Cartesian RK4 of the puck under the string force at 7,200 steps per
second (dt = 1.39e-4 s); the puck is a point for every number and is
drawn larger than life; played at 1/3.5 speed; deterministic, no seed;
first run at 10:20 EEST, re-run at 10:20:51 after the overlay and card
text fix and at 10:25:33 after the panel swap, the numbers unchanged,
log in `media/tetherball/measure.log`):

- pole (closed form l^2 = L0^2 - 2 a v0 t): the string is at half length
  l = 0.25 m at 3.7500 s, speed 1.0000 m/s, 1.5836 turns of the puck
  about the pole (1.5915 turns of string on the pole, 10.0000 rad); the
  puck reaches the pole (l = 0) at 5.0000 s after 2.9410 turns (3.1831
  turns of string on the pole, 20.0000 rad) at 1.0000 m/s all the way;
  kinetic energy 0.5000 J/kg throughout (the tension is at a right angle
  to the velocity and does no work); angular momentum about the pole
  centre v0 l: 0.5000 m^2/s at the start, 0.2500 at half, 0 at the pole
  (the tension is tangent to the pole, so it has a torque about the
  centre); the pole holds the puck from 5.0000 s
- hole (closed form r = L0 - u t, r v_t = L0 v0 = 0.5000 m^2/s): at the
  start v_t = 1.0000 m/s with 0.1 m/s inward, full speed 1.0050 m/s
  (shown as 1.00); the string is at half length r = 0.25 m at 2.5000 s:
  tangential speed 2.0000 m/s, full speed 2.0025 m/s (1.9926 x the
  start), 1.5915 turns; at r = 0.05 m at 4.5000 s: tangential 10.0000
  m/s, full 10.0005 m/s, 14.3239 turns (90.0000 rad); the pull then
  stops and the puck circles at 5 cm at 10.00 m/s (31.83 turns per
  second); kinetic energy 0.5050 J/kg at the start, 2.0050 at half
  (3.970 x), 50.0050 at the stop; work done by the string 1.5000 J/kg by
  half and 49.4950 by the stop; angular momentum 0.5000 = 0.5000 = 0.5000
  m^2/s (conserved, the pull is central)
- RK4 check, pole (Cartesian, T = v^2 / l toward the tangent point,
  35,641 steps to l = 0.05 m): max |l - closed form| 1.15e-12 m, max
  |speed - v0| 7.59e-14 m/s, max |angular momentum - v0 l| 1.16e-12; at
  half the string t = 3.7500 s (closed form 3.7500), speed 1.000000 m/s;
  at l = 0.0499 m t = 4.9501 s (closed form 4.9500), speed 1.000000 m/s,
  energy 0.500000 J/kg
- RK4 check, hole (Cartesian, T = v_t^2 / r toward the hole, 32,400
  steps to r = 0.05 m): max |r - (L0 - u t)| 2.62e-11 m, max |radial
  speed + u| 2.39e-9 m/s, max |angular momentum - L0 v0| 1.04e-9; at
  half the string t = 2.5000 s (closed form 2.5000), tangential 2.000000
  m/s, full 2.002498 m/s, angle 10.000000 rad (closed form 10.000000);
  at r = 0.05 m t = 4.5000 s (closed form 4.5000), tangential 10.000000
  m/s, full 10.000500 m/s, angle 90.000000 rad (closed form 90.000000),
  energy 50.005000 J/kg
- schedule printed by the sim (2 runs of 20 s at 1/3.5 speed, release at
  0 s into each run, crossfade reset over the last 0.5 s): in each run
  the hole puck is at half string at +8.75 s, the pole puck at half
  string at +13.12 s, the hole pull stops at +15.75 s and the pole puck
  hits the pole at +17.50 s; runs start at 0 and 20 s, so the hole
  half-string moments fall at 8.75 and 28.75 s, the pole ones at 13.12
  and 33.12 s, the hole stops at 15.75 and 35.75 s and the pole hits at
  17.50 and 37.50 s; resets 19.5-20 and 39.5-40 s (the last one is also
  the loop fade); title until 2.4 s; card from 22 s in the first
  manifest, to be set from the voice timing; 1/3.5 rather than 1/4
  because at 1/4 the pole hit (5.000 s real) would land exactly on the
  20 s reset and never be seen, while 1/3.5 gives a 2 s hold at the pole
  before each reset
- text widths (DejaVuSans-Bold): overlay 885 px at 34 (the first draft
  "same puck | ice, no friction | 1/3.5 speed | no seed" was 964 px and
  was shortened before any render); title lines 745 and 791 px at 56;
  panel labels 634 (hole) and 435 (pole) px at 40; sublabels 311 and
  291 px and "speed" 95 px at 28; readout "10.00 m/s" 353 px at 64;
  string readout 293 and turns readout 234 px at 36; half marks 334 and
  334 px and end marks 424 (hole) and 387 (pole) px at 32; ring label 81
  px at 24; payoff lines 561, 399, 709 and 719 px at 40 (the first
  draft's line 1 "does the puck speed up? at half the string:" was 973
  px and was split into two lines before any render); nothing over 950
  px

Narration numbers: one meter a second and fifty centimeters of string
(setup), at half the string through the hole two meters a second and
wrapping the pole one meter a second (payoff; the measured 2.0025 full
speed, 2.0000 tangential, and 1.0000, shown as 2.00 and 1.00 on the
marks and the card). The times, the turns, the 10 m/s at 5 cm, the
energies, the angular momenta and the RK4 checks go to the description.
No number contradicted the claim.

### Production

- layout (`sims/tetherball/tetherball.py`): overlay at y 96, title at y
  190/252, two panels of 543 px from y 350 (top: the hole, bottom: the
  pole) with the orbit centred at x 372 and y 621/1164, 400 px per metre
  so the 50 cm string is 200 px and the 1 m orbit fits the panel with 57
  px to spare; dashed reference rings at 50 and 25 cm with their labels
  outside each ring on the lower-left diagonal; the pole as a 10 px disc
  with the wrapped string drawn as rings of growing radius plus the
  partial turn, the free string leaving the outermost wrap at the tangent
  point; the hole as a dark 7 px disc with a coral rim and the string to
  its centre; the same gold 14 px puck in both panels, a velocity arrow
  (40 px per m/s, capped at 120) and, on the pole, a small right-angle
  mark between the string and the motion; a trail of the last 1.2 s of
  video time (240 samples) fading in the panel colour; a right-aligned
  column at x 1040 with the label (40 px), the sublabel (28), "speed"
  and the live readout at 64 px (gold for 0.35 s of real time either side
  of the half-string moment, "at the pole" in grey after the hit), the
  string length and the turn counter at 36 px, then the gold marks "at
  25 cm: 2.00 m/s" / "at 25 cm: 1.00 m/s" and "held at 5 cm: 10.00 m/s" /
  "hit the pole: 1.00 m/s" at 32 px; at the half-string moment a solid
  gold ring at 25 cm and a gold dot where the puck was; captions at
  caption_y 0.75, the four-line card from y 1592; geometry drawn at 2x
  and reduced; the hole panel is on top because its half-string moment
  comes first (2.5 s against 3.75 s real), so the narration reads the
  panels top to bottom and ends on the surprise
- smoke frames (`--frames`, pass 1 at 10:20:53 EEST, at 0, 1.5, 8.8,
  13.2, 15.9, 17.6, 19.7, 22.5, 28.8, 35.9 and 39.8 s): two defects: the
  trail was too faint to read (0.5 s at alpha 0.85 to 0 over 100
  samples) and the ring labels "50 cm | 25 cm" sat on the orbit's left
  side where both pucks cross them (the puck covered "25 cm" at 22.5 s);
  fixes: trail 1.2 s of video time at 240 samples with alpha 1.0 to
  0.12, ring labels moved outside each ring at 225 degrees; the panels
  were swapped at the same time (hole on top) and the card lines
  reordered to match; smoke pass 2 at 10:25:35 EEST (the same times plus
  33.2 s) clean: nothing clips, nothing enters the caption band, the
  wrapped string shows three rings at the hit, the 25 cm ring turns gold
  at each half-string moment, the crossfade at 39.8 s blends into the
  title frame
- narration (written after the measure-only run, 10:25 EEST): three
  hooks tried, "A puck on the ice, one meter a second, fifty centimeters
  of string. The string gets shorter. Does the puck speed up?" (kept: a
  noun-phrase opening, the setup number, then the title question in the
  title's words), "The string gets shorter. Does the puck speed up? A
  puck on the ice at one meter per second on fifty centimeters of
  string." (dropped: "one meter per second" is exactly 20 characters, so
  with any punctuation captions.py splits "second" off; and the setup
  after the question delays the story) and "Shorten the string. Does the
  puck speed up?" (dropped: an audio-initial clipped verb, the risk seen
  with "Spin" and "Start", and it names neither the puck nor the setup
  number); `projects/tetherball/narration.txt`, 109 words; speeds
  written "one meter a second" and "two meters a second" so that each
  number and its unit stay inside one 20-character chunk ("one meter a
  second," 19, "Two meters a second," 20, "fifty centimeters of" 20),
  checked with chunks() before recording; "pull" used only as the verb
  "pulled" (both passes transcribed it correctly), "tugs" / "a sideways
  tug" for the force, "never changes the speed" instead of "cannot" or
  "does not" (a transcribed "can't" or "doesn't" would split at the
  apostrophe in the normaliser), no possessives ("the pole's string"
  would tokenise as "pole s"); the setup, the mechanism and the payoff
  all go hole then pole so the narration reads the panels top to bottom
  and ends on the surprise ("Wrapping the pole, no. One meter a second,
  the same.")
- voice: `scripts/voiceover.sh projects/tetherball/narration.txt` pass 1
  at 10:26:28 EEST failed on one word, "drifts" came back as "dr ifts";
  rephrased to "the puck moves inward" (same word count); pass 2 at
  10:26:43 EEST passed, "ok: transcript matches narration": 109 words,
  32.95 s, ends at 33.55 s of the 40 s video, 3.31 words/s; log in
  `media/tetherball/voice.log`
- timing (`scripts/voice-timing.py`, +0.6 s offset, log in
  `media/tetherball/timing.log`): "A puck on the ice." 0.60 to 1.82 s;
  "one meter a second" 1.82 to 3.03; "fifty centimeters of string. The
  string gets shorter." 3.03 to 5.96 over the title (to 2.4 s) and run
  1's first turn; "Does the puck speed up? On top, the string is pulled
  in through a hole." 5.96 to 9.74 with run 1's hole half-string moment
  at 8.75 s; "Below, the string wraps around a pole. Through the hole,
  the string tugs inward," 9.74 to 14.00 with the pole half-string
  moment at 13.12 s; "and the puck moves inward." 14.00 to 15.57 over the
  hole puck's fast final spiral; "so the string does work. Around the
  pole, the string tugs at a right angle to the motion." 15.57 to 20.42
  over the hole stop (15.75 s), the pole hit (17.50 s), the hold and the
  reset (19.5 to 20 s); "A sideways tug turns the puck," 20.42 to 22.36
  and "but never changes the speed." 22.36 to 24.26 over run 2's first
  turn; "So does the puck speed up?" 24.26 to 25.96 with the card lit
  from 24.6 s; "At half the string: through the hole, yes. Two meters a
  second." 25.96 to 29.66 with run 2's hole half-string moment at 28.75 s
  (readout gold from 27.5 to 30.0 s); "Double. Wrapping the pole, no."
  29.66 to 31.47; "One meter a second" 31.47 to 32.79 and "The same."
  32.79 to 33.55 with the pole readout gold from 31.9 s and the pole
  half-string moment at 33.12 s; the rest of run 2 (hole stop 35.75 s,
  pole hit 37.50 s, hold, loop fade) plays under the card with no
  narration
- schedule decisions: 2 runs of 20 s at 1/3.5 speed released at the run
  start (motion from the first frame; the first frame is both pucks at
  twelve o'clock on full strings under the title); 1/3.5 rather than 1/4
  because at 1/4 the pole hit (5.000 s real) lands exactly on the 20 s
  reset and is never seen, while 1/3.5 shows the hit at 17.5 s with a 2
  s hold before each reset and keeps the 10 m/s finish readable (19 px
  per frame, 6.6 frames per turn at 5 cm); payoff_t 24.0 s from the
  timing, after run 2's start (20 s) and the mechanism sentences and
  before "So does the puck speed up?" (24.26 s), so the card is fully
  lit at 24.6 s and 2 s before the first payoff number; the hole is
  narrated first in the payoff because its half-string moment (28.75 s)
  comes 4.4 s before the pole's (33.12 s) on screen; the readouts show
  the full speed, so the hole panel reads 1.00 on the first frame and
  1.01 from the second (1.005 m/s with the 10 cm/s reel-in), which the
  description states; the setup number is the circling speed
- footage: `sims/tetherball/tetherball.py` (no arguments) wrote
  `media/tetherball/footage.mp4`, 40.00 s at 60 fps, 2,400 frames, h264
  crf 16 yuv420p, in 47 s with eight forked workers, 10:27:33 to
  10:28:20 EEST; the same run re-printed every measurement above
  (`media/tetherball/render.log`); loop check on the raw frames: the last
  frame differs from the first in 0 px
- compose: `scripts/compose.sh tetherball` wrote
  `media/tetherball/final.mp4` at 10:28:38 EEST (h264 1080x1920 60 fps,
  2,400 frames, aac 22050 Hz mono, 40.000 s, 5,114,404 bytes; music seed
  73 at gain 0.18; captions at caption_y 0.75, 37 drawtext filters, the
  overlay plus 36 caption chunks); loudness mean -16.8 dB, peak -0.0 dB;
  preview (40.07 s) and 8x5 contact sheet written
  (`media/tetherball/compose.log`)

### Local QA

- smoke pass 1 (10:20:53 EEST, `--frames` before any render): two layout
  defects found and fixed (the faint trail, the ring labels on the
  orbit; see Production); smoke pass 2 (10:25:35 EEST) clean before the
  footage render
- final pass (10:29 EEST): frames at 0.02, 1.5, 8.8, 13.2, 15.9, 17.6,
  24.5, 26.5, 28.8, 30.5, 32.0, 33.2, 35.9, 37.6 and 39.95 s extracted
  from final.mp4 (`media/tetherball/frame-*.png`) and inspected with the
  8x5 contact sheet (`media/tetherball/sheet.png`): 0.02 s shows the
  overlay at y 96, the title "The string gets shorter. / Does the puck
  speed up?" at y 190 and 252 clear of it and of the panels, both pucks
  at twelve o'clock on full 50 cm strings with their velocity arrows,
  readouts 1.01 (hole, full speed) and 1.00 m/s, string 49.9 / 50.0 cm,
  turns 0.00 (the thumbnail); 1.5 s shows both pucks a seventh of a turn
  round with trails under "A puck on the ice,"; 8.8 s shows run 1's hole
  half-string moment under "is pulled in through": the readout 2.01 m/s
  in gold, string 24.9 cm, turns 1.61, the mark "at 25 cm: 2.00 m/s",
  the gold 25 cm ring and dot, while the pole puck reads 1.00 at 35.3
  cm; 13.2 s shows the pole half-string moment under "Through the
  hole,": 1.00 m/s in gold, string 24.8 cm, turns 1.60, "at 25 cm: 1.00
  m/s", the hole puck at 4.07 m/s and 12.3 cm; 15.9 s shows the hole
  puck held at 5 cm under "moves inward, so the": 10.00 m/s, turns
  15.69, "held at 5 cm: 10.00 m/s", the trail a red ring round the hole,
  the pole puck at 15.1 cm with two wraps on the pole; 17.6 s shows the
  pole hit under "Around the pole, the": "at the pole", string 0.0 cm,
  turns 2.94, "hit the pole: 1.00 m/s", three teal rings on the pole,
  the hole puck still circling (turns 31.15); 24.5 s shows the card
  fading in under "changes the speed." with run 2 at 1.35 and 1.00 m/s;
  26.5 s shows "speed up?" with the card fully lit ("does the puck speed
  up? / at half the string: / through the hole: yes, 2.00 m/s / wrapping
  the pole: no, 1.00 m/s"); 28.8 s shows "yes." with run 2's hole
  half-string moment: 2.01 m/s in gold, the mark, the gold ring and dot;
  30.5 s shows "double." with the hole puck at 2.50 m/s and 20.0 cm;
  32.0 s shows "One meter a second," with the pole readout 1.00 m/s in
  gold at 28.0 cm; 33.2 s shows "the same." with the pole half-string
  moment: 1.00 m/s in gold, 24.8 cm, "at 25 cm: 1.00 m/s"; 35.9 s shows
  run 2's hole puck held at 5 cm under the card with no caption (the
  voice ended at 33.55 s); 37.6 s shows run 2's pole hit under the card;
  39.95 s shows the crossfade to the title frame with the card and the
  marks fading out; captions match the narration word for word and sit
  in the y 1440 to 1520 band with the lowest panel element (the "50 cm"
  label) at y 1330 and the card from 1592; the widest text (the overlay,
  885 px) is centred with 97 px margins and nothing clips at the frame
  edges; the payoff numbers are on screen when spoken (card from 24.0 s,
  "two meters a second" at about 28.5 s with the gold 2.01 readout and
  the mark, "one meter a second" at 31.47 s with the gold 1.00 readout);
  the loop closes: the raw last frame differs from the raw first frame
  in 0 px (render.log), and on the encoded final frame 2399 differs from
  frame 0 in 3,084 px by more than 24 levels (0.15 percent, all at text
  edges, max channel difference 70, mean 0.54, encoder noise: the
  footage's own encoded first and last frames differ in 910 px); ffprobe:
  h264 1080x1920, 60/1 fps, 2,400 frames, aac 22050 Hz mono, 40.000000
  s, atoms ftyp, moov, free, mdat (moov before mdat), md5
  071140c2a72b3d24e96133452df127c0; approved

### Metadata

- `projects/tetherball/metadata.json`: title "The string gets shorter.
  Does the puck speed up? Through a hole: yes, 2 m/s. On a pole: no, 1
  m/s" (97 characters); description with the setup (the puck at 1 m/s on
  50 cm, the two panels at the same scale, the hole pulled at 10 cm/s to
  5 cm then held, the 2.5 cm pole and the involute, the closed forms
  checked by a Cartesian RK4 at 7,200 steps per second, the point puck,
  1/3.5 speed, no seed), a Measured list (the hole run's speeds, turns,
  energies and angular momentum at half and at 5 cm; the pole run's
  speed, turns, time to the pole, constant energy and falling angular
  momentum; the RK4 agreement), a Why paragraph in plain words (a string
  can only pull along itself; the pole's string leaves at a tangent and
  pulls at a right angle to the motion, so it does no work; the hole's
  string pulls toward the hole while the puck moves toward the hole, so
  it does work, and it has no torque about the hole so r times v stays
  fixed), the rerun line and the AI-made line; 10 tags (tetherball,
  angular momentum, conservation of angular momentum, puck on a string,
  circular motion, work and energy, physics, physics visualization,
  simulation, shorts); category 27; private; containsSyntheticMedia
  true; selfDeclaredMadeForKids false; the same keys in the same order
  as projects/looptrack/metadata.json
- not uploaded; task left open for the orchestrator's review and upload

### Release

- orchestrator review (10:36 EEST): the task evidence, the 8x5 contact
  sheet and the full-resolution frames at 0.02, 8.8, 17.6, 28.8, 33.2 and
  39.95 s inspected: the question over the two pucks at their start with
  the readouts 1.01 and 1.00 m/s on the first frame (the hole readout is
  the full speed with the 0.1 m/s inward part, stated in the
  description); 8.8 s shows the hole puck at half string with the gold
  2.01 m/s readout and the mark "at 25 cm: 2.00 m/s" under "is pulled
  in through"; 17.6 s shows the hole puck held at 10.00 m/s and the pole
  puck "at the pole" after 2.94 turns with "hit the pole: 1.00 m/s";
  28.8 s shows the card "does the puck speed up? / at half the string: /
  through the hole: yes, 2.00 m/s / wrapping the pole: no, 1.00 m/s"
  under "yes." with run 2's hole puck at half string in gold; 33.2 s
  shows the pole puck at half string with the gold 1.00 m/s under "the
  same."; 39.95 s shows the crossfade to the title frame with the card
  fading out; every caption in the clear band, no clipping; final.mp4
  h264 1080x1920 60 fps, 2,400 frames, aac 22050 Hz mono, 40.000 s, moov
  before mdat, md5 071140c2a72b3d24e96133452df127c0; title 97
  characters; approved for release
- quota check: clock 2026-09-21T10:39:57+03:00; two upload attempts (bigswing, 10:37:09,
  published as AO0xsAawEUw at 10:37:49; torricelli, 10:38:33, published
  as oNbFaWeSD44 at 10:39:19) recorded since the 2026-09-21 10:00 EEST
  boundary (log entries and media/*/upload.log both checked); this is
  insert attempt 3 of the hard cap of 5
- attempt 3 recorded at 2026-09-21T10:39:57+03:00, video name tetherball, before running
  `scripts/yt-upload.py tetherball`

### Published

- upload: `scripts/yt-upload.py tetherball` ran 10:39:57 to 10:40:03 EEST,
  token verified to see only the Seed Zero channel, video id
  X58adh7gsmc, private (`media/tetherball/upload.log`)
- gate: `scripts/yt-qa.py tetherball X58adh7gsmc --wait --publish` ran in
  the foreground from 10:40:10 EEST: processing succeeded and the 10
  tags read back on the first poll, 15 of 15 pass (processed, succeeded,
  hd, 1080x1920, title, description, tags as a set, category 27, not for
  kids, PT41S for the 40.000 s file, private); containsSyntheticMedia
  reads absent as on every earlier upload (`media/tetherball/publish.log`)
- publish: the same run set the video public at 2026-09-21T10:40:42+03:00;
  the re-read after 15 s shows privacyStatus public, madeForKids false,
  embeddable true; public at https://youtu.be/X58adh7gsmc
- slot resolution: published for the 2026-09-21 quota day

### Quota

- attempt 3 of the hard cap of 5 for the quota day that began
  2026-09-21T10:00 EEST; cost 1 + 1,600 + 54 = 1,655 units (the
  channels.list verification inside yt-upload.py, the insert, the gate
  run's reads, update and re-read as printed by yt-qa.py); day total
  after three attempts 4,964 units

### Repository

- committed as 84cdda2 "Publish the day twenty-three slate" (sims,
  projects, tasks, docs/niche.md, web/data; no media, previews or
  secrets) and pushed to origin/master at 2026-09-21 10:42 EEST
