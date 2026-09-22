# Produce short: Stopping distance, 50 beside 100 km/h with the same brakes

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day24

## Goal

Backlog idea (trend research 2026-09-20, task 20260920-100347, pillar 2
chaos and physics):
"Stopping distance: two cars braking at 0.8 g from 50 and 100 km/h at
the same line; measure the stopping distances and the fast car's speed
at the slow car's stop mark; expect 12.3 against 49.2 m (4x for 2x
speed) and the fast car still doing 86.6 km/h where the slow one has
stopped (sqrt(v2^2 - v1^2)); deterministic, no seed."
Day twenty-four, second slot. Chosen because it is continuous motion in
two lanes on the same input (the same brakes, the same line) with a
closed-form check, the format of the channel's best shorts (coupled
pendulums 1,046 views, turntable 973, loop the loop 963, rolling race
950), and because "double the speed, double the distance" is a common
wrong answer that the picture corrects. Braking only, no reaction time
(stated in the description). Question in the first two seconds: "Twice
the speed. How much farther to stop?" (or the producer's better wording,
kept identical in the title, the hook and the payoff).

## Claim

Two cars braking at the same line with the same brakes, one at fifty
kilometers an hour and one at a hundred, stop at twelve meters and at
forty-nine meters: double the speed needs four times the distance, and
where the slow car has stopped the fast car is still doing eighty-seven
kilometers an hour. Every number in the narration is printed by the sim
before the script is written.

## Evidence

### Measurements

(recorded after the measure-only run, before scripting)

`sims/braking/braking.py --measure-only` with
`projects/braking/manifest.json` (two cars in the two lanes of one road,
front bumpers on the same line at t = 0, both braking at a constant 0.8
g = 7.8453 m/s^2 (g = 9.80665, a dry-road figure) with no reaction time,
so braking distance only; car A in the left lane at 50 km/h = 13.8889
m/s, car B in the right lane at 100 km/h = 27.7778 m/s; 4.5 x 1.8 m cars
in 4.5 m lanes at 19 px per metre; both drawn from the closed forms x =
v0 t - a t^2 / 2, v = v0 - a t and checked by an RK4 integration at
6,000 steps per second (dt = 1.67e-4 s); played at 1/3 speed;
deterministic, no seed; run at 10:19:23 EEST, log in
`media/braking/measure.log`):

- closed forms (d = v0^2 / (2 a), t = v0 / a): car A stops at 12.2940 m
  after 1.7703 s; car B stops at 49.1761 m after 3.5407 s; distance
  ratio 4.0000 for a speed ratio of 2.0000; time ratio 2.0000; the
  difference is 36.8821 m
- car B at car A's stop mark (12.2940 m): speed sqrt(vB^2 - 2 a dA) =
  24.0563 m/s = 86.60 km/h at t = 0.4744 s (86.6 percent of its start
  speed, 75.0 percent of its kinetic energy left); car A at that instant
  is at 5.7057 m doing 36.60 km/h
- car B at the instant car A stops (t = 1.7703 s): at 36.8821 m doing
  13.8889 m/s = 50.00 km/h with 12.2940 m still to go (a car at 50 km/h
  needs exactly 12.2940 m: a t_A = v_A)
- mean braking speed v0 / 2: car A 25.00 km/h over 1.7703 s, car B 50.00
  km/h over 3.5407 s; twice the mean speed for twice the time is four
  times the distance
- RK4 check, car A (10,623 steps to v = 0): max |x - closed form|
  1.94e-12 m, max |v - closed form| 3.17e-12 m/s; interpolated stop t =
  1.7703 s (closed form 1.7703), x = 12.2940 m (closed form 12.2940)
- RK4 check, car B (21,245 steps to v = 0): max |x - closed form|
  1.01e-11 m, max |v - closed form| 9.16e-12 m/s; interpolated stop t =
  3.5407 s (closed form 3.5407), x = 49.1761 m (closed form 49.1761); at
  car A's stop mark t = 0.4744 s (closed form 0.4744), speed 24.0563
  m/s = 86.60 km/h (closed form 86.60); ratio of the RK4 stop distances
  4.000000
- table at 0.8 g, braking distance only: 30 km/h 4.43 m in 1.06 s; 50
  km/h 12.29 m in 1.77 s; 70 km/h 24.10 m in 2.48 s; 100 km/h 49.18 m
  in 3.54 s; 130 km/h 83.11 m in 4.60 s
- schedule printed by the sim (3 runs of 13.3333 s = 800 frames at 1/3
  speed, brakes on at 0 s of each run, crossfade reset over the last 0.5
  s; the stop marks lit in run 1 stay on the road for runs 2 and 3, so
  the marks are up from 5.31 s (car A) and 10.62 s (car B) to the loop
  fade, and car B's crossing of car A's mark is flagged from run 2): run
  1 brakes on 0.00 s, car B at car A's mark 1.42 s (the mark is not lit
  yet, no flash), car A stops 5.31 s, car B stops 10.62 s, hold to 12.83
  s, reset to 13.33 s; run 2 brakes on 13.33 s, car B at car A's mark
  14.76 s (readout gold, label "86.6 km/h here" lit), car A stops 18.64
  s, car B stops 23.96 s, hold to 26.17 s, reset to 26.67 s; run 3
  brakes on 26.67 s, crossing 28.09 s, car A stops 31.98 s, car B stops
  37.29 s, hold to 39.50 s, reset to 40.00 s (the last one is also the
  loop fade); title until 2.4 s; card from 24 s in the first manifest,
  to be set from the voice timing; 1/3 rather than 1/4 because three
  runs show the stops three times and the 3.54 s real run fills 10.62 s
  with a 2.2 s hold, while 1/4 would leave one run fewer for the loop
- text widths (DejaVuSans-Bold): overlay 784 px at 34 (the first draft
  "same brakes | 0.8 g | no reaction time | 1/3 speed | no seed" was
  1,136 px, "... | no reaction | ..." 1,038 px and "0.8 g | no reaction
  time | 1/3 speed | no seed" 858 px; "no reaction time" moved to a
  small on-panel note and the description); title lines 529 and 845 px
  at 56; note lines 242 and 317 px at 26; column labels 301 and 329 px
  at 40; readout number "100.0" 202 px at 64 with the unit "km/h" 89 px
  at 32 (the full "100.0 km/h" at 64 is 403 px and would run from x 666
  to 1,069, 11 px from the frame edge, so the unit is set beside the
  number at 32); "stopped" 294 px at 64; distance 139 px and "stopped at
  49.2 m" 370 px at 36; marks "12.3 m" and "49.2 m" 123 px and "86.6
  km/h here" 272 px at 32; tick label 61 px at 22; payoff lines 374,
  598, 391 and 787 px at 40 (the first draft's line 1 "twice the speed.
  how much farther to stop?" was 986 px and was split into two lines
  before any render); nothing over 950 px

Narration numbers: fifty against a hundred kilometers an hour (setup),
four times as far, twelve meters against forty nine (payoff; the measured
12.2940 and 49.1761 m, shown as 12.3 and 49.2 on the marks and the
card), and the readout car B shows at car A's mark, about eighty seven
kilometers an hour (86.60, the on-screen label says 86.6). The times,
the 50 km/h with 12.29 m to go, the energy fraction, the table and the
RK4 checks go to the description. No number contradicted the claim.

### Production

- layout (`sims/braking/braking.py`): overlay at y 96, title at y
  190/252, a top-down two-lane road from y 350 to 1436 centred at x 540
  (4.5 m lanes, 85.5 px each, faintly tinted in the lane colour, a
  dashed divider, ticks every 10 m on both edges with the numbers 10 to
  50 painted on the divider), the braking line in white at y 1320 with
  the cars driving up from it at 19 px per metre (front bumpers on the
  line at t = 0, 4.5 x 1.8 m bodies of 86 x 34 px with cabin,
  headlights and lit brake lights with a red glow, teal for 50 km/h in
  the left lane and coral for 100 km/h in the right lane), skid marks
  from each car's rear axle start to its rear axle now, a right-aligned
  readout column for car A at x 414 and a left-aligned one for car B at
  x 666 (label "from 50 km/h" / "from 100 km/h" at 40 px in the lane
  colour, the speed number at 64 px with "km/h" at 32 px beside it,
  "stopped" in grey once the car stops, the distance at 36 px turning
  gold at the stop), a two-line note "no reaction time / braking
  distance only" at 26 px top left, gold stop marks across each car's
  lane the moment it stops with the labels "12.3 m" left of the road and
  "49.2 m" right of it, car A's mark continued as a dashed line across
  car B's lane, the label "86.6 km/h here" right of that line and car
  B's readout in gold for 0.3 s of real time either side of the
  crossing (only once the mark exists, so from run 2), captions at
  caption_y 0.75, the four-line card from y 1592; geometry drawn at 2x
  and reduced; the marks lit in run 1 stay on the road through the
  resets so runs 2 and 3 show car B passing car A's stop mark, and the
  last run's reset blends to the mark-free first frame under the loop
  fade
- smoke frames (`--frames`, pass 1 at 10:19:56 EEST at 0, 1.5, 5.4,
  10.7, 12.9, 14.8, 18.7, 24.5 and 39.8 s): three defects: the tick
  labels "10 m" and "50 m" painted on the divider touched the stopped
  cars' inner edges by about 5 px; car B's "km/h" unit sat at a fixed x
  so short numbers left a wide gap; the "stopped" readout was repeated
  by a "stopped at 12.3 m" distance row; fixes: bare numbers 10 to 50
  on the divider (31 px wide, 12 px clear of the car bodies) and no
  label at the line, the unit placed right after the number, the
  distance row simply turns gold; a faint lane tint added; pass 2 at
  10:22:28 (the same times plus 28.1 s) clean except that car B's gold
  mark at 49.18 m (y 386) ran through the "50" number at y 385; fix:
  the numbers moved 15 px lower (tick + 30 px); pass 3 at 10:23:47 (0,
  10.7, 14.8, 39.8 s) clean: nothing clips, nothing enters the caption
  band, the marks and labels sit clear of the cars and the numbers
- narration (written after the measure-only run, 10:22 EEST): three
  hooks tried, "Two cars, the same brakes. Twice the speed. How much
  farther to stop?" (kept: names the picture in five words, the
  question starts at 2.35 s in the recording), "Twice the speed. How
  much farther to stop? Two cars, the same brakes, the same line."
  (dropped: the question lands before the viewer knows what the two
  cars are, and the setup number comes later), "Same brakes, same line.
  Twice the speed. How much farther to stop?" (dropped: a
  sentence-initial "Same" risks the onset clip seen with "Spin" and
  "Start", and it never says "two cars"); `projects/braking/narration.txt`,
  102 words; "brakes" tested through the round trip before scripting
  and kept (four phrases passed); "one hundred" rather than "a hundred"
  (the normaliser folds only the former); "twice that: one hundred"
  keeps the number inside one 20-character chunk ("that: one hundred."
  18; "Left car, fifty" 15 with "kilometers an hour." 19 next, since the
  24-character "fifty kilometers an hour" cannot fit one chunk;
  "Twelve meters, then" 19; "forty nine meters." 18; "about eighty
  seven" then "kilometers an hour." 19), checked with chunks() before
  recording, 32 chunks, none over 20; no possessives, no "still", no
  "pull"; the second beat names the readout the picture shows ("about
  eighty seven", the label says 86.6); the mechanism follows the
  readouts: the same rate, twice the speed to shed, twice as long, and
  faster the whole way; the payoff repeats the question verbatim
- voice: `scripts/voiceover.sh projects/braking/narration.txt` pass 1
  at 10:22:33 EEST failed on two tokens ("a hundred" came back as the
  digits 100, which the normaliser does not fold from "a hundred", and
  the verb "brakes" in "so it brakes for twice as long" came back
  "breaks" while the two earlier "brakes" passed); rephrased to "twice
  that: one hundred" and "so it takes twice as long to stop"; pass 2 at
  10:23:18 passed (108 words, 32.80 s) but its timing put "eighty
  seven" at 17.2 s, 2.4 s after the run-2 crossing, so the sentence
  "The slow car stops in a few car lengths" between the setup and the
  87 beat was cut; pass 3 at 10:24:35 failed on one token (the
  sentence-initial "Where" after "one hundred." came back "for");
  rephrased to "At the spot where the slow car has stopped"; pass 4 at
  10:25:04 passed, "ok: transcript matches narration": 102 words, 31.23
  s, ends at 31.83 s of the 40 s video, 3.27 words/s; every pass in
  `media/braking/voice.log`
- timing (`scripts/voice-timing.py`, +0.6 s offset, log in
  `media/braking/timing.log`): "Two cars, the same brakes." 0.60 to
  2.35 s; "twice the speed" 2.35 to 3.50 (the question starts at 2.35
  s, under the title that holds to 2.4 s); "How much farther to stop?"
  3.50 to 4.99; "Both hit the brakes at the line, left car." 4.99 to
  7.39 with run 1's car A stop at 5.31 s; "fifty kilometers an hour."
  7.39 to 8.98; "Right car." 8.98 to 9.82; "Twice that." 9.82 to 10.67;
  "one hundred." 10.67 to 11.52 with run 1's car B stop at 10.62 s; "At
  the spot where the slow car has stopped" 11.52 to 13.88 over the
  reset (12.83 to 13.33 s) and run 2's start; "the fast car is doing
  about eighty seven kilometers an hour." 13.88 to 17.24 with run 2's
  crossing at 14.76 s (readout gold 13.86 to 15.66 s, the label "86.6
  km/h here" lit from 14.76 s) and "eighty seven" at about 15.7 s;
  "Both cars shed speed at the same rate. The fast car has twice the
  speed to shed" 17.24 to 21.84 with run 2's car A stop at 18.64 s;
  "so it takes twice as long to stop" 21.84 to 23.99 ending as run 2's
  car B stops (23.96 s); "and it is faster the whole way, twice the
  speed, how much farther to stop" 23.99 to 28.08 with the card lit
  from 24.8 s (fully at 25.4 s, about 0.6 s before "twice the speed");
  "Four times as far, twelve meters, then forty nine meters." 28.08 to
  31.83 with run 3's crossing at 28.09 s (readout gold 27.19 to 28.99
  s) and the marks and the card on screen; the rest of run 3 (car A
  stops 31.98 s, car B stops 37.29 s, hold, loop fade) plays under the
  card with no narration
- schedule decisions: 3 runs of 13.3333 s (800 frames) at 1/3 speed
  with the brakes on at the run start (motion from the first frame; the
  first frame is both cars on the line at 50.0 and 100.0 km/h under the
  title); 1/3 rather than 1/4 because three runs show the stops three
  times and the 3.54 s real run fills 10.62 s with a 2.2 s hold on both
  marks, while 1/4 would leave two runs; the marks persist so the
  second beat is visible in run 2 and again in run 3 rather than only
  after the answer is known; payoff_t 24.8 s from the timing, after
  run 2's car B stop (23.96 s) and before the payoff question (about
  26.0 s), so the card is fully lit 0.6 s before the question and 2.7 s
  before the first payoff number; the setup number is the two start
  speeds, the payoff number is four times (12.3 against 49.2 m), the
  86.6 km/h readout is named in the second beat because the picture
  shows it
- footage: `sims/braking/braking.py` (no arguments) wrote
  `media/braking/footage.mp4`, 40.00 s at 60 fps, 2,400 frames, h264 crf
  16 yuv420p, in 40 s with eight forked workers, 10:25:30 to 10:26:10
  EEST; the same run re-printed every measurement above
  (`media/braking/render.log`); loop check on the raw frames: the last
  frame differs from the first in 0 px
- compose: `scripts/compose.sh braking` wrote `media/braking/final.mp4`
  at 10:26:24 EEST (h264 1080x1920 60 fps, 2,400 frames, aac 22050 Hz
  mono, 40.000 s, 2,921,075 bytes; music seed 75 at gain 0.18; captions
  at caption_y 0.75, 33 drawtext filters, the overlay plus 32 caption
  chunks, all at y = h * 0.750, the first from 0.600 s and the last to
  31.831 s); loudness mean -17.6 dB, peak -0.0 dB; preview (40.07 s) and
  8x5 contact sheet written (`media/braking/compose.log`)

### Local QA

- smoke pass 1 (10:19:56 EEST, `--frames` before any render): three
  layout defects found and fixed (the tick labels against the stopped
  cars, the floating unit, the repeated "stopped"; see Production);
  smoke pass 2 (10:22:28) found the "50" under car B's mark, fixed;
  smoke pass 3 (10:23:47) clean before the footage render
- final pass (10:27 to 10:30 EEST): frames at 0.02, 1.5, 3.0, 7.5,
  10.7, 14.8, 15.9, 18.7, 22.5, 24.0, 25.5, 27.0, 28.5, 30.5, 33.0,
  37.3 and 39.95 s extracted from final.mp4 (`media/braking/frame-*.png`)
  and inspected with the 8x5 contact sheet (`media/braking/sheet.png`):
  0.02 s shows the overlay "same brakes | 0.8 g | 1/3 speed | no seed"
  at y 96, the title "Twice the speed. / How much farther to stop?" at y
  190 and 252 clear of it and of the road, both cars on the white line
  with brake lights lit, readouts 49.7 and 99.7 km/h at 0.2 and 0.3 m
  (frame 2; frame 0 reads 50.0 and 100.0 at 0.0 m), the note and the
  painted 10 to 50 (the thumbnail); 1.5 s shows both cars a few metres
  up with skid marks under "Two cars, the same"; 3.0 s shows the title
  gone and the cars at 10.0 and 23.9 m under "Twice the speed."; 7.5 s
  shows car A stopped with the gold "12.3 m" mark, its dashed
  continuation across car B's lane and the gold distance, car B at 29.4
  km/h and 44.9 m, under "Left car, fifty"; 10.7 s shows both stopped
  with "49.2 m" fading in at car B's front, under "At the spot where";
  14.8 s shows run 2's crossing: car B at car A's mark with its readout
  86.2 km/h in gold and "86.6 km/h here" fading in, car A at 36.2 km/h,
  under "car is doing about"; 15.9 s shows the label fully lit with car
  B at 75.8 km/h under "kilometers an hour."; 18.7 s shows run 2's car A
  stop (gold 12.3 m) with car B at 49.5 km/h and 37.1 m under "at the
  same rate."; 22.5 s shows car B at 13.7 km/h and 48.3 m under "shed,
  so it takes"; 24.0 s shows both stopped under "stop, and it is"; 25.5
  s shows the card fully lit ("twice the speed. / how much farther to
  stop? / four times as far: / 50 km/h: 12.3 m, 100 km/h: 49.2 m")
  under "faster the whole"; 27.0 s shows run 3's start (46.9 and 96.9
  km/h) with the marks and the card, under "Twice the speed."; 28.5 s
  shows run 3's crossing with the gold 82.7 readout under "stop?"; 30.5
  s shows "Twelve meters, then" with car A at 11.3 m and the marks; 33.0
  s shows run 3 with no caption (the voice ended at 31.83 s), car A
  stopped and car B at 40.4 km/h; 37.3 s shows run 3's car B stop with
  both marks and the card; 39.95 s shows the loop fade to the title
  frame with the card and marks almost gone; captions match the
  narration word for word (captions.py builds them from
  narration.txt) and sit in the y 1440 to 1520 band with the lowest
  road element at y 1436 and the card from 1592; the widest text (the
  title's second line, 845 px) is centred with 117 px margins and
  nothing clips at the frame edges; the payoff numbers are on screen
  when spoken (marks from 5.31 and 10.62 s, card from 24.8 s, "twelve
  meters" at about 29.5 s and "forty nine meters" at about 31 s); the
  loop closes: the raw last frame differs from the raw first frame in 0
  px (render.log), on the encoded footage frame 2399 differs from frame
  0 in 709 px by more than 24 levels (0.034 percent, max channel
  difference 64), and on final.mp4 in 2,479 px (0.120 percent, max 79,
  mean 0.40, all at text edges, encoder noise); ffprobe: h264
  1080x1920, 60/1 fps, 2,400 frames (nb_read_frames 2400), aac 22050 Hz
  mono, 40.000000 s, atoms ftyp, moov, free, mdat (moov before mdat),
  md5 6acebfd9af2b6e7cd4018a73cb67af70; approved locally

### Metadata

- `projects/braking/metadata.json`: title "Twice the speed. How much
  farther to stop? Four times: 12.3 m from 50 km/h, 49.2 m from 100
  km/h" (96 characters); description with the setup (two cars on one
  line, 0.8 g as a dry-road figure, no reaction time so braking
  distance only with the reaction distance excluded, 50 and 100 km/h,
  the closed forms checked by RK4 at 6,000 steps per second, the
  persistent marks, 1/3 speed, no seed), a Measured list (both stops
  with times, the ratio 4.0000, the 86.6 km/h at the slow car's mark
  with 75 percent of the energy left, the 50 km/h with 12.29 m to go
  at the instant the slow car stops, the 30/70/130 km/h table, the RK4
  agreement), a Why paragraph in plain words (the same brakes take away
  the same speed every second, twice the speed to shed means twice the
  time, faster the whole way means twice the average speed, so four
  times the distance; the square law with the printed 70 against 100
  km/h pair; reaction distance comes on top), the rerun line and the
  AI-made line; 10 tags (braking distance, stopping distance, road
  safety, speed and stopping distance, kinematics, cars, physics,
  physics visualization, simulation, shorts); category 27; private;
  containsSyntheticMedia true; selfDeclaredMadeForKids false; the same
  keys in the same order as projects/tetherball/metadata.json
- not uploaded; task left open for the orchestrator's review and upload

### Release

- orchestrator review (10:32 EEST): the task evidence, the 8x5 contact
  sheet and the full-resolution frames at 0.02, 15.9, 25.5 and 39.95 s
  inspected: the question "Twice the speed. / How much farther to stop?"
  over both cars on the line with the readouts 49.7 and 99.7 km/h on the
  first frame; 15.9 s shows the gold "12.3 m" mark across both lanes with
  the label "86.6 km/h here" under "kilometers an hour." while the fast
  car is at 20.9 m doing 75.8 km/h; 25.5 s shows both cars stopped at
  12.3 and 49.2 m with the card "twice the speed. / how much farther to
  stop? / four times as far: / 50 km/h: 12.3 m, 100 km/h: 49.2 m" under
  "faster the whole"; 39.95 s shows the crossfade to the title frame;
  the "no reaction time / braking distance only" note sits top left of
  the panel, clear of everything; every caption in the clear band, no
  clipping; final.mp4 h264 1080x1920 60 fps, 2,400 frames, aac 22050 Hz
  mono, 40.000 s, moov before mdat, md5
  6acebfd9af2b6e7cd4018a73cb67af70; title 96 characters; approved for
  release
- quota check: clock 2026-09-22T10:33:53+03:00; one upload attempt (bounceslope, 10:32:36,
  published as hlBy6yci8_U at 10:33:10) recorded since the 2026-09-22
  10:00 EEST boundary (log entries and media/*/upload.log both checked);
  this is insert attempt 2 of the hard cap of 5
- attempt 2 recorded at 2026-09-22T10:33:53+03:00, video name braking, before running
  `scripts/yt-upload.py braking`

### Published

- upload: `scripts/yt-upload.py braking` ran 10:33:53 to 10:33:59 EEST,
  token verified to see only the Seed Zero channel, video id
  faJeNRiCo5Y, private (`media/braking/upload.log`)
- gate: `scripts/yt-qa.py braking faJeNRiCo5Y --wait --publish` ran in
  the foreground from 10:34:05 EEST: processing succeeded and the 10 tags
  read back on the first poll, 15 of 15 pass (processed, succeeded, hd,
  1080x1920, title, description, tags as a set, category 27, not for
  kids, PT41S for the 40.000 s file, private); containsSyntheticMedia
  reads absent as on every earlier upload (`media/braking/publish.log`)
- publish: the same run set the video public at 2026-09-22T10:34:38+03:00;
  the re-read after 15 s shows privacyStatus public, madeForKids false,
  embeddable true; public at https://youtu.be/faJeNRiCo5Y
- slot resolution: published for the 2026-09-22 quota day

### Quota

- attempt 2 of the hard cap of 5 for the quota day that began
  2026-09-22T10:00 EEST; cost 1 + 1,600 + 54 = 1,655 units (the
  channels.list verification inside yt-upload.py, the insert, the gate
  run's reads, update and re-read as printed by yt-qa.py); day total
  after two attempts 3,309 units
