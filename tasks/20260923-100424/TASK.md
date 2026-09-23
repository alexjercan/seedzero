# Produce short: Zeno bounce, 0.8 beside 0.9 restitution from the same 1 m drop

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day25

## Goal

Backlog idea (trend research 2026-09-20, task 20260920-100347, pillar 2
chaos and physics, collisions):
"Zeno bounce: a ball dropped 1 m with a 0.8 bounce beside one with 0.9;
measure the bounce count and the moment each ball stops; expect
infinitely many bounces that end at 4.064 s and 8.580 s (t0 (1 + e) /
(1 - e); path 4.56 and 9.53 m), the 16th and 33rd bounces the first
under 1 mm; the count is a counter, so the ball stays on screen;
deterministic, no seed."
Research feasibility numbers (task 20260920-100347): from 1 m, e 0.5
stops at 1.355 s (path 1.667 m), e 0.8 at 4.064 s (4.556 m, bounce 16
first under 1 mm), e 0.9 at 8.580 s (9.526 m, bounce 33).
Day twenty-five, second slot. Chosen because it is two balls on the same
drop with continuous motion, exact closed forms (a geometric series),
and a plain question with a surprising answer: the bounces never run
out, yet the ball is still by a fixed time. Question in the first two
seconds: "How many bounces before it stops?" (or the producer's better
wording, kept identical in the title, the hook and the payoff). Honesty
rule: the sim counts bounces down to a stated floor (for example the
first bounce under one micrometre) and prints the count above 1 mm, the
index of the first bounce under 1 mm, and the closed-form stop time; the
narration quotes only printed numbers and never narrates "infinite" as a
measurement (the limit argument goes to the description). Play the drops
slowed (about 1/4 speed) so the 0.9 ball finishes inside the 40 s short.

## Claim

A ball dropped from one meter that keeps eighty percent of its height on
every bounce is bouncing under a millimeter by bounce sixteen and lies
still at four point zero six seconds, while the same drop with a ninety
percent bounce is under a millimeter at bounce thirty-three and still at
eight point five eight seconds: the bounces get quicker without end, yet
they all fit before a fixed moment. Every number in the narration is
printed by the sim before the script is written.

## Evidence

### Measurements

(recorded after the measure-only run, before scripting)

`sims/zenobounce/zenobounce.py --measure-only` with
`projects/zenobounce/manifest.json` (a ball dropped from h0 = 1 m onto a
hard floor with no air, g = 9.80665 m/s^2, once with restitution e = 0.8
in the left panel, each bounce keeping 80 percent of the speed and 64
percent of the height, and once with e = 0.9 in the right panel, 90
percent of the speed and 81 percent of the height; released at the same
instant, two panels at the same scale, 700 px per metre; event-driven
flights with closed forms, bounce n leaving the floor at e^n v0, rising
to h0 e^(2n) and flying 2 t0 e^n, no time step; counted down to the
first bounce under 1e-6 m; checked by an RK4 free flight at 6,000 steps
per second with floor-crossing interpolation over the drop and the first
five bounces; the ball is a point for every number; played at 1/4 speed,
one run; deterministic, no seed; first run at 10:27:36 EEST, re-run at
10:31:55 with the final schedule, log in `media/zenobounce/measure.log`):

- closed forms: drop time t0 = sqrt(2 h0 / g) = 0.451601 s, impact speed
  v0 = sqrt(2 g h0) = 4.4287 m/s; impact n at t0 + 2 t0 e (1 - e^(n-1)) /
  (1 - e); stop time T = t0 (1 + e) / (1 - e); path h0 (1 + e^2) /
  (1 - e^2)
- left panel (e = 0.8): bounce 1 leaves at 3.5430 m/s, rises to 0.6400 m
  and flies 0.7226 s; bounces above 1 mm: 15 (bounce 15 rises to 1.2379
  mm); first bounce under 1 mm: bounce 16, 0.7923 mm high, 25.42 ms
  long, leaving the floor at 3.9373 s; first bounce under 1e-6 m (the
  count floor): bounce 31, 9.808e-7 m high (bounce 30: 1.532e-6 m),
  0.8945 ms long, leaving the floor at 4.059934 s (closed form 4.059934,
  diff 8.9e-16) and landing at 4.060829 s; closed-form stop time T =
  0.451601 x 9 = 4.064407 s, 3.58e-3 s after the floor bounce lands;
  path to the floor bounce 4.555552 m, closed-form path 4.555556 m (diff
  3.5e-6); bounce 32 would rise to 6.28e-7 m and bounce 100 to 4.15e-20
  m, both positive: no bounce height is zero, the counter stops only at
  the stated floor
- right panel (e = 0.9): bounce 1 leaves at 3.9858 m/s, rises to 0.8100
  m and flies 0.8129 s; bounces above 1 mm: 32 (bounce 32 rises to
  1.1790 mm); first bounce under 1 mm: bounce 33, 0.9550 mm high, 27.91
  ms long, leaving the floor at 8.3013 s; first bounce under 1e-6 m:
  bounce 66, 9.120e-7 m high (bounce 65: 1.126e-6 m), 0.8626 ms long,
  leaving the floor at 8.571789 s (closed form 8.571789, diff 1.8e-15)
  and landing at 8.572651 s; closed-form stop time T = 0.451601 x 19 =
  8.580414 s, 7.76e-3 s after the floor bounce lands; path to the floor
  bounce 9.526308 m, closed-form path 9.526316 m (diff 7.8e-6); bounce
  67 would rise to 7.39e-7 m and bounce 100 to 7.06e-10 m, both positive
- every bounce down to the floor is printed (launch speed, height, flight
  time, impact time; 31 and 66 lines in the log); ratio of the stop
  times 2.1111
- RK4 checks (17,286 and 22,685 steps over the drop and the first five
  bounces): max |landing time - event| 2.58e-7 s (left) and 2.45e-7 s
  (right), max |landing speed - event| 4.84e-7 and 3.75e-7 m/s, max
  |apex - h0 e^(2n)| 5.33e-8 and 9.00e-8 m (the apex sampled at the
  step; the first draft's apex list was shifted by one entry and read
  0.36 m, fixed before scripting); RK4 on a constant acceleration is
  exact, so the residual is the linear crossing interpolation
- schedule printed by the sim (1/4 speed, release at 0.2 s): left
  impacts 1 at 2.01 s, 2 at 4.90, 3 at 7.21, 4 at 9.06, 5 at 10.54, 10
  at 14.52, 16 at 15.95, 31 at 16.44; left clock frozen at 4.06 s from
  16.46 s; left bounces last 2.89, 2.31, 1.18, 0.39 and 0.10 s of video
  at bounces 1, 2, 5, 10 and 16; right impacts 1 at 2.01 s, 2 at 5.26,
  3 at 8.18, 4 at 10.82, 5 at 13.19, 10 at 21.92, 33 at 33.41, 66 at
  34.49; right clock frozen at 8.58 s from 34.52 s; right bounces last
  3.25, 2.93, 2.13, 1.26 and 0.11 s of video at bounces 1, 2, 5, 10 and
  33; title until 2.4 s; card from 19.2 s, its last line from 33.0 s;
  hold to 39.50 s; loop fade 39.50 to 40.00 s (the first draft had
  release 0.5 and the card at 20 / 34 s; set from the voice timing)
- text widths (DejaVuSans-Bold): overlay 830 px at 34; title lines 611
  and 496 px at 56; panel labels "keeps 80% of its speed" 468 px at 36
  in a 490 px panel; sublabels "and 64% of its height" 338 px at 28
  (the first draft "64% of its height, every bounce" was 502 px, wider
  than the panel, shortened before any render); counters "31" and "66"
  89 px at 64; clocks "t 8.58 s" 186 px and frozen "8.58 s" 150 px at
  44; "bounces" 131 and "at rest" 105 px at 28; "counted to 0.001 mm"
  289 and "real seconds" 171 px at 24; scale "1 m" 50 and "0.5 m" 76 px
  at 24; payoff lines 800, 664, 494 and 494 px at 40; nothing over 950
  px

Narration numbers: one meter (setup); eighty and ninety percent (the
panel definitions, kept because they name the two balls); bounce sixteen
under a millimeter (mechanism; the measured bounce 16 at 0.7923 mm); a
thousandth of a millimeter (the count floor, 1e-6 m); four point zero
six seconds and eight point five eight seconds (payoffs; the measured
4.064407 and 8.580414, shown as 4.06 and 8.58 on the clocks and the
card). "More than the counter shows" rests on the printed positive
heights of bounces 32, 67 and 100. The counts 31 and 66, the 15 and 32
bounces above 1 mm, bounce 33, the path lengths, the flight times, the
ratio and the RK4 checks go to the description. No number contradicted
the claim.

### Production

- layout (`sims/zenobounce/zenobounce.py`): overlay at y 96, title at y
  190/252, two panels side by side from y 350 to 1436 (x 40 to 530 and
  550 to 1040, a faint separator at x 540); in each panel the label row
  at y 380 (36 px, coral for 80 percent, teal for 90) and the sublabel
  at y 420 (28 px); the floor at y 1190 with a 32 px slab and the 1 m
  release 700 px above it; a faint height scale 70 px in from the
  panel's left edge with ticks every 0.25 m and "1 m" / "0.5 m" labels;
  the ball (gold, 18 px radius, its bottom on the point) 285 px in from
  the panel's left edge; a short gold apex mark beside the ball's path
  at every bounce height reached so far (they pile up at the floor as
  the bounces shrink); a ring pulse on the floor for 0.3 s of video
  after each impact in the panel colour; the readouts from y 1244:
  "bounces" (28 px), the counter (64 px) with "counted to 0.001 mm"
  beside it (24 px), the clock "t 3.94 s" (44 px) and "real seconds"
  (24 px, bottom at y 1420); at the floor bounce the counter turns gold
  and freezes; at the closed-form stop time the clock freezes as
  "4.06 s" in gold with an "at rest" tag; captions at caption_y 0.75;
  the four-line card from y 1592, lines 1 to 3 (the question, "more
  than the counter shows", the 80 percent line) from payoff_t and the
  90 percent line from payoff_t_right; geometry drawn at 2x and reduced
- whisper pre-test (10:28:05 EEST, before scripting;
  `media/zenobounce/hooks/`, log `hooks.log`): three hook variants and
  one mechanism group round-tripped through `scripts/voiceover.sh`,
  all passed on the first pass: "A ball drops one meter. How many
  bounces before it stops?" (3.62 s), "How many bounces before it
  stops? A ball drops one meter onto a hard floor." (4.61 s, the
  sentence-initial "How" not clipped), "The ball falls one meter. How
  many bounces before it stops?" (3.41 s), and the mechanism group with
  every narrated number ("Two balls, the same drop, at quarter speed.
  ... sixteen ... a thousandth of a millimeter ... four point zero six
  seconds ... eight point five eight seconds. More than the counter
  shows.", 26.26 s); a fourth hook "A one meter drop. How many bounces
  before it stops?" (3.09 s, 10:29:25) passed after the chunk check
  below
- smoke frames (`--frames` at 10:30:32 EEST, with the first-draft
  release 0.5, at 0, 1.5, 2.31, 5.2, 12, 16.3, 16.8, 21, 33.7, 34.9, 37
  and 39.8 s): no defects: the title clear of the overlay and of the
  labels, both balls on the 1 m tick, the impact rings, the apex marks
  stacking at the floor, the frozen gold "31" and "4.06 s at rest"
  beside the live right column, the four-line card inside the frame,
  nothing in the caption band
- narration (written after the measure-only run, 10:29 EEST;
  `projects/zenobounce/narration.txt`, 115 words): chunks() checked
  before recording; the first draft "A ball drops one meter." split as
  "A ball drops one | meter." and "The ball lies at rest at four point
  zero six seconds." as "rest at four point | zero six seconds.", so
  the hook became "A one meter drop." (17 characters, one chunk) and the
  left payoff "... and the ball lies at rest at four point zero six
  seconds." which chunks as "ball lies at rest at | four point zero six
  | seconds." with the number intact; "eight point five eight" is 22
  characters and cannot sit in one chunk, so the last sentence is built
  for the split "at rest at eight | point five eight | seconds." (the
  lifeguard's accepted pattern) and the earlier "Yet the right ball
  lies at rest at eight point five eight seconds." (which split as
  "eight point five | eight seconds.") was dropped; the question-first
  hook dropped because the setup after the question delays the story;
  numbers as words, American spelling; "still", "got", "spread",
  "pull", "slow" at a sentence onset and "they are" avoided; "at rest"
  for the stopped ball; the balls named by their panels ("the left
  ball", "the right ball"); the order of the narration follows the
  screen (left stop, then the right ball, then the answer, then the
  right stop)
- voice: `scripts/voiceover.sh projects/zenobounce/narration.txt`
  passed on every pass (`media/zenobounce/voice.log`): pass 1 at
  10:29:39 EEST (106 words, 32.48 s, ending at 33.08 s of video),
  pass 2 at 10:30:26 (110 words, 32.77 s; the last sentence lengthened
  to "keeps going, and then lies at rest") and pass 3 at 10:31:16 (115
  words, 34.27 s, 3.36 words/s, ends at 34.87 s; six words added to
  the setup, "the same drop", "percent", "the one before", so the right
  stop lands on its number); the re-records were for timing, not for
  mishearings
- timing (`scripts/voice-timing.py`, +0.6 s offset, pass 3, log in
  `media/zenobounce/timing.log`): "A one meter drop. How many bounces
  before it stops? Two balls, the same drop." 0.60 to 5.05 s (the hook
  spans about 0.60 to 1.7 s, the question from about 1.7 s, inside the
  title's 2.4 s); "At quarter speed, the left ball keeps 80% of its
  speed on every bounce. The right ball keeps 90%." 5.05 to 11.35;
  "Each bounce is lower and quicker than the one before." 11.35 to
  14.02; "by bounce 16" 14.02 to 15.46; "The left ball is under a
  millimeter." 15.46 to 17.25 with the left bounce 16 at 15.95 s; "The
  counter stops at a thousandth of a millimeter," 17.25 to 19.68 with
  the left counter frozen at 31 from 16.44 s; "and the ball lies at
  rest at 4.06 seconds." 19.68 to 22.96 with the left clock frozen from
  16.46 s and the card lit from 19.8 s; "The right ball bounces longer
  and shrinks the same way. So, how many bounces before it stops?"
  22.96 to 28.74; "more than the counter shows." 28.74 to 30.25; "The
  right ball keeps going," 30.25 to 31.92; "and then lies at rest at
  8.58 seconds." 31.92 to 34.87 with the right bounce 33 at 33.41 s,
  the card's 90 percent line lit from 33.6 s and the right clock frozen
  at 34.52 s, on the number's last word; the hold (34.9 to 39.5 s) and
  the loop fade play under the card with no narration
- schedule decisions: release_at 0.2 s (both balls sit on the 1 m tick
  under the title for the first 12 frames; 0.2 rather than 0.5 so the
  right stop, 34.52 s, lands inside "eight point five eight" instead of
  after "seconds"); payoff_t 19.2 s so the card is fully lit at 19.8 s,
  before "four point zero six" at about 21.5 s and 3.3 s after the left
  stop; payoff_t_right 33.0 s so the 90 percent line is lit at 33.6 s,
  as the number is spoken and 0.9 s before the right clock freezes;
  the card names 8.58 s about one second before that clock freezes,
  which the lifeguard precedent (3.5 s) allows
- footage: `sims/zenobounce/zenobounce.py` (no arguments) wrote
  `media/zenobounce/footage.mp4`, 40.00 s at 60 fps, 2,400 frames, h264
  crf 16 yuv420p, in 29 s with eight forked workers, 10:31:55 to
  10:32:24 EEST; the same run re-printed every measurement above
  (`media/zenobounce/render.log`); loop check on the raw frames: the
  last frame differs from the first in 0 px
- compose: `scripts/compose.sh zenobounce` wrote
  `media/zenobounce/final.mp4` at 10:32:35 EEST (h264 1080x1920 60 fps,
  2,400 frames, aac 22050 Hz mono, 40.000 s, 2,503,536 bytes; music
  seed 78 at gain 0.18; captions at caption_y 0.75, 38 drawtext
  filters, the overlay plus 37 caption chunks); loudness mean -16.8 dB,
  peak -0.0 dB; preview (40.07 s) and 8x5 contact sheet written
  (`media/zenobounce/compose.log`)

### Local QA

- smoke pass (10:30:32 EEST, `--frames` before any render): clean, no
  layout defects (see Production); the two text-width fixes (the
  sublabel) and the RK4 apex fix were made from the measure-only
  output before the smoke pass
- final pass (10:33 to 10:35 EEST): frames at 0.02, 1.5, 2.01, 4.9, 12,
  15.95, 16.46, 21, 27, 33.41, 34.52, 37 and 39.95 s extracted from
  final.mp4 (`media/zenobounce/frame-*.png`) and inspected with the 8x5
  contact sheet (`media/zenobounce/sheet.png`): 0.02 s shows the
  overlay "same 1 m drop, no air | 1/4 speed | no seed" at y 96, the
  title "How many bounces / before it stops?" at y 190 and 252 clear of
  it and of the panel labels, both balls on the 1 m tick, the scales,
  "bounces 0" and "t 0.00 s" in both columns (the thumbnail); 1.5 s
  shows both balls at 0.5 m under "A one meter drop."; 2.01 s shows the
  first impact in both panels with the coral and teal rings, both
  counters at 1 and "t 0.45 s", under "How many bounces"; 4.9 s shows
  the left impact 2 with the right ball mid-flight under "drop, at
  quarter"; 12 s shows the left ball at bounce 6 and the right at 4
  with the apex marks under "Each bounce is lower"; 15.95 s shows the
  left counter at 16 with the impact ring under "the left ball is";
  16.46 s shows the left column frozen, "31" and "4.06 s at rest" in
  gold with the marks piled at the floor, the right ball at bounce 6
  and "t 4.07 s", under "under a millimeter."; 21 s shows "ball lies at
  rest at" with the card's first three lines lit; 27 s shows the right
  counter at 14 under "So, how many bounces"; 33.41 s shows the right
  bounce 33 with its ring, "t 8.30 s", the 90 percent line fading in,
  under "at rest at eight"; 34.52 s shows both columns frozen, "66" and
  "8.58 s at rest" in gold, the full card, under "point five eight";
  37 s shows the hold with no caption; 39.95 s shows the crossfade to
  the title frame with the card and the frozen readouts fading out;
  captions match the narration word for word (the contact sheet reads
  every chunk in order) and sit in the y 1440 to 1520 band with the
  lowest readout text ending at y 1420 and the card from 1592; the
  widest text (the overlay, 830 px) is centred with 125 px margins and
  nothing clips at the frame edges; the payoff numbers are on screen
  when spoken (the gold 4.06 s clock from 16.46 s and the card from
  19.8 s against "four point zero six" at about 21.5 s; "8.58 s" on the
  card from 33.6 s and the frozen clock from 34.52 s against "eight
  point five eight" at about 33.8 to 34.5 s); the loop closes: the raw
  last frame differs from the raw first frame in 0 px (render.log), and
  on the encoded final frame 2399 differs from frame 0 in 5,386 px by
  more than 24 levels (0.26 percent, at text edges, max channel
  difference 87, mean 0.42, encoder noise: the footage's own encoded
  first and last frames differ in 1,597 px); ffprobe: h264 1080x1920,
  60/1 fps, 2,400 frames (also by decode), aac 22050 Hz mono, 40.000000
  s, atoms ftyp, moov, free, mdat (moov before mdat), md5
  ebf8de9226cf4bc204bad027e0d035da; approved locally

### Metadata

- `projects/zenobounce/metadata.json`: title "How many bounces before it
  stops? More than the counter shows. 80%: at rest by 4.06 s, 90%: 8.58
  s" (98 characters; the first draft with "and 8.58 s (90%)" was 103);
  description with the setup (the 1 m drop, no air, g, the 80 and 90
  percent balls and their 64 and 81 percent of height, the closed-form
  flights, the 0.001 mm count floor, the RK4 check, 1/4 speed with the
  clocks in real seconds, no seed), a Measured list (the drop time and
  impact speed, both balls' bounce 1, the counts above 1 mm, bounces 16
  and 33, the floor bounces 31 and 66 with their times, the stop times
  9 t0 and 19 t0, the path lengths beside the partial sums, the 2.111
  ratio, the positive heights of bounces 32, 67 and 100, the RK4
  agreement), a Why paragraph in plain words (each flight lasts 0.8 of
  the one before, a geometric series with no last term but a finite
  sum, the first flight divided by 1 - 0.8, so 9 t0 and 19 t0; the
  heights add up the same way; Zeno's paradox in a bouncing ball; a
  real ball stops sooner but its total time is still bounded), the
  rerun line and the AI-made line; 10 tags (bouncing ball, coefficient
  of restitution, Zeno's paradox, geometric series, infinite series,
  kinematics, physics, physics visualization, simulation, shorts);
  category 27; private; containsSyntheticMedia true;
  selfDeclaredMadeForKids false; the same keys in the same order as
  projects/lifeguard/metadata.json
- not uploaded; task left open for the orchestrator's review and upload

### Release

- orchestrator review (10:37 EEST): the task evidence, the 8x5 contact
  sheet and the full-resolution frames at 0.02, 16.46, 34.52 and 39.95 s
  inspected: the question "How many bounces / before it stops?" over both
  panels with the labels "keeps 80% of its speed / and 64% of its height"
  and "keeps 90% of its speed / and 81% of its height", both balls at the
  1 m mark and the counters at 0 on the first frame; 16.46 s shows the
  left counter frozen at "31 counted to 0.001 mm" with "4.06 s at rest"
  in gold and the ladder of bounce heights beside the ball while the
  right ball is at bounce 6 at "t 4.07 s", under "under a millimeter.";
  34.52 s shows both stopped, "66" and "8.58 s at rest" on the right,
  the card "how many bounces before it stops? / more than the counter
  shows / 80%: at rest by 4.06 s / 90%: at rest by 8.58 s" under "point
  five eight"; 39.95 s shows the crossfade to the title frame; the voice
  timing puts the question inside the first piece (0.60 to 5.05 s, four
  words before it), with the title question on screen from frame 0; the
  honesty rule holds: the counters state their 0.001 mm floor on screen,
  the narration answers "More than the counter shows" and the
  geometric-series limit sits in the description only; every caption in
  the clear band, no clipping; 115 words accepted (the voice ends at
  34.87 s); final.mp4 h264 1080x1920 60 fps, 2,400 frames, aac 22050 Hz
  mono, 40.000 s, moov before mdat, md5
  ebf8de9226cf4bc204bad027e0d035da; title 98 characters; approved for
  release
- quota check: clock 2026-09-23T10:40:00+03:00; one upload attempt (springswap, 10:38:12,
  published as utBc09NZWUk at 10:39:20) recorded since the 2026-09-23
  10:00 EEST boundary (log entries and media/*/upload.log both checked);
  this is insert attempt 2 of the hard cap of 5
- attempt 2 recorded at 2026-09-23T10:40:00+03:00, video name zenobounce, before running
  `scripts/yt-upload.py zenobounce`

### Published

- upload: `scripts/yt-upload.py zenobounce` ran 10:39:37 to 10:40:05 EEST,
  token verified to see only the Seed Zero channel, video id
  mgoguyVzOmU, private (`media/zenobounce/upload.log`)
- gate: `scripts/yt-qa.py zenobounce mgoguyVzOmU --wait --publish` ran in
  the foreground from 10:40:11 EEST: processing succeeded and the 10 tags
  read back on the first poll, 15 of 15 pass (processed, succeeded, hd,
  1080x1920, title, description, tags as a set, category 27, not for
  kids, PT41S for the 40.000 s file, private); containsSyntheticMedia
  reads absent as on every earlier upload (`media/zenobounce/publish.log`)
- publish: the same run set the video public at 2026-09-23T10:40:44+03:00;
  the re-read after 15 s shows privacyStatus public, madeForKids false,
  embeddable true; public at https://youtu.be/mgoguyVzOmU
- slot resolution: published for the 2026-09-23 quota day

### Quota

- attempt 2 of the hard cap of 5 for the quota day that began
  2026-09-23T10:00 EEST; cost 1 + 1,600 + 54 = 1,655 units (the
  channels.list verification inside yt-upload.py, the insert, the gate
  run's reads, update and re-read as printed by yt-qa.py); day total
  after two attempts 3,310 units
