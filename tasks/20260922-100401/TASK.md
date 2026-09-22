# Produce short: Bounce down a slope, a 20 cm drop on a 14.5 degree slope beside a flat floor

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day24

## Goal

Backlog idea (trend research 2026-09-20, task 20260920-100347, pillar 2
chaos and physics):
"Bounce down a slope: a ball dropped 20 cm onto a 20 degree slope with
perfect bounces beside the same ball on a flat floor; measure the gaps
between landings and the hang time of each hop; expect gaps of 0.547,
1.094, 1.642, 2.189 m (exactly 1:2:3:4, x_n = 8 n h sin beta) and every
hop 0.404 s (2 sqrt(2h/g)) while the flat-floor ball lands on the same
spot every time; deterministic, no seed."
Day twenty-four, first slot. Chosen because bouncing and rolling balls
on tabletop geometry are the channel's proven format (loop the loop 963
views, rolling race 950, monkey and hunter 963, cradle 958) and the
result is a clean integer pattern a viewer can count on screen: the same
drop, the same ball, a flat floor beside a tilted one. Question in the
first two seconds: "Drop a ball on a slope. How far apart are the
bounces?" (or the producer's better wording, kept identical in the title,
the hook and the payoff).

## Claim

A ball dropped twenty centimeters onto a slope with perfect bounces lands
at gaps that grow exactly one, two, three, four times the first gap
(forty centimeters, then eighty, one point two and one point six meters
along the slope on a slope with sin beta = 1/4, 14.48 degrees), and every
hop lasts the same zero point four seconds, while the same ball on a flat
floor lands on the same spot every time. Every number in the narration is
printed by the sim before the script is written. (The backlog's 20
degrees was reduced for the render: four gaps must fit the panel width,
and sin beta = 1/4 makes the narrated numbers round, 40 cm and 1.6 m.)

## Evidence

### Measurements

(recorded after the measure-only run, before scripting)

`sims/bounceslope/bounceslope.py --measure-only` with
`projects/bounceslope/manifest.json` (a ball dropped from h = 0.20 m,
vertical to the first contact point, onto a slope with sin beta = 1/4,
beta = 14.4775 degrees, the slope drops 1 m in 4 m, with perfectly
elastic, frictionless bounces, beside the same ball dropped 0.20 m onto a
flat floor, released at the same instant in two panels at the same scale,
244 px per metre so the drop is 49 px and the hop height 47 px on the
slope and 49 px on the floor; g = 9.80665 m/s^2; the slope run is an
event-driven flight: the time to the plane is the root of a quadratic,
the normal velocity is reflected, the tangential velocity is untouched,
no time step; checked by an RK4 free flight at 6,000 steps per second
(dt = 1.67e-4 s) with linear plane-crossing interpolation; the ball is a
point for every number and is drawn larger than life; played at 1/5
speed; deterministic, no seed; run at 10:21:30 EEST, re-run at 10:22:31
after the layout fix with the numbers unchanged, log in
`media/bounceslope/measure.log`):

- closed forms: impact speed v0 = sqrt(2 g h) = 1.9806 m/s, drop time
  sqrt(2 h / g) = 0.2020 s, hop time T = 2 v0 / g = 0.4039 s on the slope
  and on the floor alike (the normal speed after the bounce is v0 cos
  beta and the normal gravity g cos beta, so the ratio is angle-free),
  hop height above the slope h cos beta = 0.1936 m (floor 0.2000 m),
  speed along the slope at the first contact v0 sin beta = 0.4951 m/s,
  gaining g sin beta T = 0.9903 m/s per hop, landing gap n: x_n = 8 n h
  sin beta = 0.4000 n m, total after 4 hops 4.0000 m along the slope
  (3.8730 m across, 1.0000 m down), whole run 1.8177 s
- slope (event-driven, 4 hops): first contact at 0.2020 s at s = 0.0000 m
  (residual off the plane 5.4e-17 m), speed 1.9806 m/s, along the slope
  0.4951 m/s; hop 1: 0.4039 s, lands at 0.6059 s at s = 0.4000 m, gap
  0.4000 m (closed form 0.4000), ratio 1.0000, along the slope 1.4854
  m/s, full speed 2.4257 m/s; hop 2: 0.4039 s, lands at 1.0098 s at s =
  1.2000 m, gap 0.8000 m (0.8000), ratio 2.0000, along the slope 2.4757
  m/s, full 3.1316 m/s; hop 3: 0.4039 s, lands at 1.4137 s at s = 2.4000
  m, gap 1.2000 m (1.2000), ratio 3.0000, along the slope 3.4660 m/s,
  full 3.9611 m/s; hop 4: 0.4039 s, lands at 1.8177 s at s = 4.0000 m,
  gap 1.6000 m (1.6000), ratio 4.0000, along the slope 4.4563 m/s, full
  4.8514 m/s; hop height 0.1936 m every hop; energy 1.9613 J/kg at every
  landing (max deviation over the landings 2.0e-15)
- floor (event-driven, 4 hops): first contact at 0.2020 s, then landings
  at 0.6059, 1.0098, 1.4137 and 1.8177 s, every hop 0.4039 s, every
  landing at s = 0.0000 m (gaps 0.0000, 0.0000, 0.0000, 0.0000 m), hop
  height 0.2000 m, along the floor 0.0000 m/s, full speed 1.9806 m/s at
  every landing, energy 1.9613 J/kg
- RK4 check, slope (10,908 steps to landing 4): max |landing time -
  event| 3.82e-7 s, max |landing position - event| 1.66e-6 m, max |speed
  along the slope - event| 9.36e-7 m/s, max |full speed - event| 1.16e-6
  m/s, max |energy - g h| 1.56e-6 J/kg (g h = 1.9613); landings at
  0.2020 s / 0.0000 m, 0.6059 / 0.4000, 1.0098 / 1.2000, 1.4137 /
  2.4000, 1.8177 / 4.0000 (the residual errors are the linear crossing
  interpolation at dt = 1.67e-4 s; RK4 is exact for the free flight)
- RK4 check, floor (10,908 steps): max |landing time - event| 3.82e-7 s,
  max |landing position - event| 0, max |full speed - event| 7.88e-7 m/s,
  max |energy - g h| 1.56e-6 J/kg
- result: slope gaps 0.4000, 0.8000, 1.2000, 1.6000 m = 1.0000 : 2.0000 :
  3.0000 : 4.0000; floor gaps 0, 0, 0, 0; every hop 0.4039 s in both
  panels
- schedule printed by the sim (3 runs of 13.33 s at 1/5 speed, release
  at 0 s into each run, each hop 2.02 s of video, crossfade reset over
  the last 0.5 s): run 1: release 0.00 s, first contact 1.01 s, landings
  3.03, 5.05, 7.07, 9.09 s (gaps 0.40, 0.80, 1.20, 1.60 m lit in turn),
  hold from 9.09 s, reset 12.83 to 13.33 s; run 2: release 13.33 s,
  first contact 14.34 s, landings 16.36, 18.38, 20.40, 22.42 s, hold from
  22.42 s, reset 26.17 to 26.67 s; run 3: release 26.67 s, first contact
  27.68 s, landings 29.70, 31.72, 33.74, 35.75 s, hold from 35.75 s,
  reset 39.50 to 40.00 s (also the loop fade); title until 2.4 s; card
  from 23 s in the first manifest, to be set from the voice timing
- text widths (DejaVuSans-Bold): overlay 845 px at 34 (the first draft
  "same ball | 20 cm drop | perfect bounces | 1/5 speed | no seed" was
  1,190 px; "perfect bounces" moved to the slope sublabel); title lines
  828 and 860 px at 56 (the first question "How far apart are the
  bounces?" was 998 px and was reworded before any render); labels 517
  (slope) and 305 (floor) px at 40; sublabels 512 and 463 px at 28; "last
  gap" 127 px at 28; big readout "1.60 m" 247 px at 64; clock line "hop 4
  of 4: 0.40 s" 354 px and speed lines 500 / 485 px at 36; gap marks 116
  px and "same spot" 174 px at 30; hop marks 82 px and "20 cm" 81 px at
  24; payoff lines 609, 647, 705 and 861 px at 40 (the first draft's line
  4 "every hop 0.40 s, flat floor: the same spot" was 949 px and was
  shortened before any render); nothing over 950 px

Narration numbers: twenty centimeters (setup), one, then two, then
three, then four times the first gap, forty centimeters and one point
six meters (payoff; the measured 0.4000 and 1.6000 m, shown as 0.40 and
1.60 m on the marks and the card). The hop time 0.40 s stays on screen
(the clock, the marks, the card) and goes to the description with the
speeds, the energies and the RK4 checks: "zero point four seconds" is 23
characters, so captions.py would split the number from its unit, and the
framing rule allows one setup and one payoff number. No number
contradicted the claim; the angle in the claim was set to the manifest's
sin beta = 1/4 before scripting.

### Production

- layout (`sims/bounceslope/bounceslope.py`): overlay at y 96, title at y
  190/252, the slope panel from y 350 to 870 with the first contact point
  at x 60, y 528 and the slope descending to the right at sin beta = 1/4
  (244 px per metre, so the four gaps span 945 px across and 244 px
  down, the last landing at x 1005), the flat-floor panel from y 870 to
  1436 with the floor at y 1190 and the ball at x 160; each surface is a
  slab 84 px deep with a 3 px surface line; the ball (gold, 14 px) is
  drawn resting on the surface (its centre offset by the radius along
  the normal, so the path and the marks keep the point's geometry); a
  "20 cm" bracket and label at the release point; the path of the whole
  run persists at 30 percent and the last 1 s of video time fades from
  full to 35 percent in the panel colour (coral for the slope, teal for
  the floor); at each landing a gold tick 14 px into the slab, a gold
  bar along the slab from the last tick, a 0.5 s expanding pulse ring,
  and under the slab the gap "0.40 m" (30 px gold) with the hop time
  "0.40 s" (24 px muted) beneath it (the floor shows "same spot" and
  "every hop 0.40 s" once); a velocity arrow (24 px per m/s, capped at
  120); a right-aligned column at x 1040 in each panel with the label
  (40 px, "on a 14.5 degree slope" / "on a flat floor"), the sublabel
  (28 px, "dropped 20 cm, perfect bounces" / "the same ball, the same
  drop"), "last gap" and the big readout at 64 px ("--" until the first
  gap, then the gap, gold for 0.6 s of video after each landing), the
  clock line "hop 2 of 4: 0.23 s" ("drop: 0.12 s" before the first
  contact, gold when held at the end) and the speed line "along the
  slope 1.49 m/s" at 36 px; after the fourth landing the state is held
  (both balls resting, all marks lit) until the crossfade reset; captions
  at caption_y 0.75, the four-line card from y 1592; geometry drawn at
  2x and reduced; the slope is on top because it is the subject and the
  floor the control, and both balls land at the same instants anyway
- angle: the backlog's 20 degrees gives gaps of 0.55 to 2.19 m (5.47 m
  along the slope), too long for the panel width at a readable hop
  height; the prompt's 15 degrees gives 0.414 n m; sin beta = 1/4
  (14.48 degrees) was chosen instead so the first gap is exactly 40 cm
  and the narration says "forty centimeters" (17 characters) and "one
  point six meters" (20), each inside one caption chunk, where "forty
  one centimeters" (21) and "one point six six meters" (24) would split
  the number from its unit; the whole run is then 4.00 m along the
  slope, 1.00 m down; the manifest key is slope_sin and the sim prints
  the angle
- smoke frames (`--frames`, pass 1 at 10:21:42 EEST, at 0, 1.5, 3.1,
  5.1, 7.1, 9.1, 10.5, 13.1, 16.4, 23.5 and 39.8 s): two defects: the
  gap-1 hop-time mark "0.40 s" straddled the slab's bottom edge (slab 76
  px, mark at depth 64), and hop 4's velocity arrow could reach the
  column's bottom line (text bottom at y 614, the arrow tip at about
  620); fixes: slab 84 px deep and the slope origin moved from y 520 to
  528 (the column's bottom line ends at y 614, the hop-4 ball top is at
  about 645, the slab bottom at the right end at 862, under the 870
  separator); smoke pass 2 at 10:22:31 EEST (the same times plus 7.9 s,
  mid hop 4) clean: nothing clips, nothing enters the caption band, the
  four arcs and the four gap labels read at the hold, the reset at 13.1
  s crossfades to the release state, the loop fade at 39.8 s blends
  into the title frame
- narration (written after the measure-only run, 10:25 EEST): three
  hooks tried, "A ball dropped on a slope. How far apart does it land?"
  (kept: a noun-phrase opening, six words before the question so it
  starts at 2.10 s, the same words as the title), "Drop a ball on a
  slope. How far apart are the bounces?" (dropped: a sentence-initial
  verb risks the clipped onset seen with "Spin", "Start" and "Shorten",
  and "How far apart are the bounces?" is 998 px at 56 px, too wide for
  the title line) and "Same ball, same drop, one slope and one flat
  floor. How far apart does it land?" (dropped: ten words before the
  question, and an s-initial first word); `projects/bounceslope/
  narration.txt`, 108 words; every number checked with chunks(): "twenty
  centimeters," 19, "forty centimeters." 18, "one point six meters" 20
  (followed by "along the slope." so no punctuation pushes it over 20;
  "The fourth, one point six meters." would have split after "one");
  "The ball is dropped" (19) fills its chunk so "twenty centimeters"
  starts the next; the hop time is not spoken ("zero point four seconds"
  is 23 characters and would split; the clock, the marks and the card
  show 0.40 s) and the mechanism beat says "Every hop takes the same
  time, on the slope and on the flat floor. But on the slope, the ball
  keeps gaining speed along the slope, so each hop covers more ground.";
  "one, then two, then three, then four" rather than "one, two, three,
  four" so a transcribed "1,2,3,4" cannot fold into one number; no
  s-initial sentences, no "pull", "still", "spread", "got", no
  apostrophes, American spelling
- voice: `scripts/voiceover.sh projects/bounceslope/narration.txt` pass
  1 at 10:26:00 EEST passed, "ok: transcript matches narration": 108
  words, 30.23 s, ends at 30.83 s of the 40 s video, 3.57 words/s; log
  in `media/bounceslope/voice.log`
- timing (`scripts/voice-timing.py`, +0.6 s offset, log in
  `media/bounceslope/timing.log`): "A ball dropped on a slope." 0.60 to
  2.10 s; "How far apart does it land? The ball is dropped twenty
  centimeters, on a slope and on a flat floor." 2.10 to 7.58 over the
  title (to 2.4 s) and run 1's drop and first three landings (1.01,
  3.03, 5.05, 7.07 s); "On the flat floor, it lands on the same spot
  every time." 7.58 to 10.77 over run 1's last landing (9.09 s) and the
  hold; "Every hop takes the same time, on the slope and on the flat
  floor." 10.77 to 14.63 over the hold, the reset (12.83 to 13.33 s) and
  run 2's drop; "but on the slope, the ball keeps gaining speed along the
  slope," 14.63 to 18.18 over run 2's first two hops (landings 16.36 and
  18.38 s) with the speed readout climbing; "So each hop covers more
  ground. So how far apart does it land? The gaps grow. One, then two,
  then three." 18.18 to 24.30 over hops 3 and 4 (20.40 and 22.42 s), the
  card lighting from 20.4 s and the hold with all four gaps lit from
  22.42 s; "then four times the first gap. The first gap is forty
  centimeters. The fourth gap is one point six meters along the slope."
  24.30 to 30.83 over the hold, the reset (26.17 to 26.67 s) and run 3's
  drop and first landing (29.70 s, "0.40 m" in gold); the rest of run 3
  (landings 31.72, 33.74, 35.75 s, the hold, the loop fade) plays under
  the card with no narration
- schedule decisions: 3 runs of 13.33 s at 1/5 speed released at the
  run start (motion from the first frame; the first frame is both balls
  hanging 20 cm above their surfaces under the title); 1/5 rather than
  1/4 because the 9.09 s of motion plus a 3.74 s hold puts run 2's hops
  under the mechanism sentences (14.6 to 20.2 s) and run 2's hold, with
  all four gaps and the four "0.40 s" marks lit, under "So how far apart
  does it land?" and "one, then two, then three, then four"; payoff_t
  20.4 s from the timing, so the card is fully lit at 21.0 s, during the
  repeated question (about 20.1 to 22.0 s), 1 s before "The gaps grow"
  and 2 s before "one, then two"; at "forty centimeters" (about 26.5 to
  28.3 s) run 3 is in its drop, so the number is on screen on the card
  ("0.40 m, 0.80 m, 1.20 m, 1.60 m"), and run 3's first gap lights in
  gold at 29.70 s under "one point six meters"
- footage: `sims/bounceslope/bounceslope.py` (no arguments) wrote
  `media/bounceslope/footage.mp4`, 40.00 s at 60 fps, 2,400 frames, h264
  crf 16 yuv420p, in 43 s with eight forked workers, 10:26:41 to
  10:27:24 EEST; the same run re-printed every measurement above
  (`media/bounceslope/render.log`); loop check on the raw frames: the
  last frame differs from the first in 0 px
- compose: `scripts/compose.sh bounceslope` wrote
  `media/bounceslope/final.mp4` at 10:27:34 EEST (h264 1080x1920 60 fps,
  2,400 frames, aac 22050 Hz mono, 40.000 s, 3,518,544 bytes; music seed
  74 at gain 0.18; captions at caption_y 0.75, 33 drawtext filters, the
  overlay plus 32 caption chunks); loudness mean -17.3 dB, peak -0.0 dB;
  preview (40.07 s) and 8x5 contact sheet written
  (`media/bounceslope/compose.log`)

### Local QA

- smoke pass 1 (10:21:42 EEST, `--frames` before any render): two
  layout defects found and fixed (the gap-1 hop-time mark on the slab
  edge, the hop-4 arrow near the column; see Production); smoke pass 2
  (10:22:31 EEST) clean before the footage render
- final pass (10:28 to 10:31 EEST): frames at 0.02, 1.5, 3.1, 5.1, 7.1,
  9.1, 12.0, 16.4, 20.5, 22.5, 23.5, 25.0, 27.5, 29.8, 35.8 and 39.95 s
  extracted from final.mp4 (`media/bounceslope/frame-*.png`) and
  inspected with the 8x5 contact sheet (`media/bounceslope/sheet.png`):
  0.02 s shows the overlay at y 96, the title "A ball dropped on a slope.
  / How far apart does it land?" at y 190 and 252 clear of it and of
  the panels, both balls hanging 20 cm above their surfaces with the
  brackets, readouts "--", "drop: 0.01 s", "along the slope 0.02 m/s" /
  "along the floor 0.00 m/s" (the thumbnail); 1.5 s shows both balls
  just after the first contact with the pulse rings, the velocity
  arrows and "hop 1 of 4: 0.10 s" under "A ball dropped on a"; 3.1 s
  shows run 1's first gap under "How far apart does": "0.40 m" in gold,
  the tick, the bar and the mark "0.40 m / 0.40 s" under the slope, the
  floor ball back on its spot with "0.00 m" in gold and "same spot /
  every hop 0.40 s"; 5.1 and 7.1 s show the second and third gaps ("0.80
  m", "1.20 m" in gold, "hop 3 of 4", "hop 4 of 4", the speed 2.50 then
  3.51 m/s); 9.1 s shows the fourth landing with "1.60 m" in gold and
  all four arcs; 12.0 s shows the hold under "Every hop takes the": all
  four gap marks with their "0.40 s", both clocks gold at "hop 4 of 4:
  0.40 s", the speed 4.46 m/s; 16.4 s shows run 2's first gap under
  "the ball keeps" with the speed 1.50 m/s; 20.5 s shows "So how far
  apart" with the card fading in and run 2's third gap ("1.20 m" in
  gold, 3.51 m/s); 22.5 s shows "The gaps grow: one," with the card
  fully lit ("how far apart does it land? / 1, 2, 3, 4 times the first
  gap: / 0.40 m, 0.80 m, 1.20 m, 1.60 m / every hop 0.40 s, flat floor:
  same spot") and run 2's fourth landing in gold; 23.5 and 25.0 s show
  "then two, then" and "times the first gap." over the hold with all
  four gaps lit; 27.5 s shows "forty centimeters." with run 3 in its
  drop ("drop: 0.17 s", the card carrying 0.40 m); 29.8 s shows "one
  point six meters" with run 3's first gap in gold; 35.8 s shows run 3's
  hold under the card with no caption (the voice ended at 30.83 s);
  39.95 s shows the crossfade to the title frame with the card fading
  out; captions match the narration word for word and sit in the y 1440
  to 1520 band with the lowest panel element (the "every hop 0.40 s"
  mark) at y 1254 and the card from 1592; the widest text (the overlay,
  845 px) is centred with 117 px margins and nothing clips at the frame
  edges; the question is on screen from the first frame and spoken from
  2.10 s; the payoff numbers are on screen when spoken (card from 20.4
  s, "one, then two, then three, then four" from about 23 s with the
  four gap marks lit, "forty centimeters" and "one point six meters"
  with the card's 0.40 m and 1.60 m and run 3's gold 0.40 m at 29.70
  s); the loop closes: the raw last frame differs from the raw first
  frame in 0 px (render.log), and on the encoded final frame 2399
  differs from frame 0 in 3,271 px by more than 24 levels (0.16
  percent, max channel difference 71, mean 0.48, encoder noise at text
  edges as on tetherball's 3,084); ffprobe: h264 1080x1920, 60/1 fps,
  2,400 frames, aac 22050 Hz mono, 40.000000 s, atoms ftyp, moov, free,
  mdat (moov before mdat), md5 f72f11c6da22779f1b8b6807af310b46;
  loudness mean -17.3 dB, peak -0.0 dB; approved locally, pending the
  orchestrator's review

### Metadata

- `projects/bounceslope/metadata.json`: title "A ball dropped on a
  slope. How far apart does it land? 40, 80, 120, 160 cm apart: exactly
  1:2:3:4" (97 characters); description with the setup (the 20 cm drop
  with perfect bounces on a slope with sin beta = 1/4, 14.48 degrees,
  beside the flat floor, the two panels at the same scale, the
  event-driven flight checked by RK4 at 6,000 steps per second, the
  point ball, 1/5 speed, no seed), a Measured list (the impact speed,
  the drop time, the 0.4039 s hop time, the hop height, the gaps and the
  1 : 2 : 3 : 4 ratio, the 4.000 m run, the speeds along the slope at
  each landing and the 0.990 m/s gain per hop, the full speeds, the
  energy, the floor's same spot, the RK4 agreement), a Why paragraph in
  plain words (a perfect bounce only reverses the part of the velocity
  into the surface; on the floor the whole velocity points into the
  floor; on the slope every bounce resets the part across the slope so
  every hop lasts 0.40 s while gravity keeps adding speed along the
  slope; the start-of-hop speeds go 1, 3, 5, 7, the averages 2, 4, 6, 8,
  the gaps 1, 2, 3, 4), the rerun line and the AI-made line; 10 tags
  (bouncing ball, ball on a slope, projectile motion, elastic bounce,
  inclined plane, kinematics, physics, physics visualization,
  simulation, shorts); category 27; private; containsSyntheticMedia
  true; selfDeclaredMadeForKids false; the same keys in the same order
  as projects/tetherball/metadata.json
- not uploaded; task left open for the orchestrator's review and upload

### Release

- orchestrator review (10:33 EEST): the task evidence, the 8x5 contact
  sheet and the full-resolution frames at 0.02, 9.1, 22.5 and 39.95 s
  inspected: the question "A ball dropped on a slope. / How far apart
  does it land?" over both balls hanging 20 cm above the slope and the
  floor on the first frame; 9.1 s shows the fourth landing with the
  gold "last gap 1.60 m", the four marks 0.40, 0.80, 1.20, 1.60 m with
  "0.40 s" under each, and the flat-floor ball on its "same spot"; 22.5
  s shows the card "how far apart does it land? / 1, 2, 3, 4 times the
  first gap: / 0.40 m, 0.80 m, 1.20 m, 1.60 m / every hop 0.40 s, flat
  floor: same spot" under "The gaps grow: one,"; 39.95 s shows the
  crossfade to the title frame with the card fading out; every caption
  in the clear band, no clipping; the angle change to sin beta = 1/4
  (14.48 degrees) accepted (the heading of this task updated); final.mp4
  h264 1080x1920 60 fps, 2,400 frames, aac 22050 Hz mono, 40.000 s, moov
  before mdat, md5 f72f11c6da22779f1b8b6807af310b46; title 97
  characters; approved for release
- quota check: clock 2026-09-22T10:32:36+03:00; zero upload attempts recorded since the
  2026-09-22 10:00 EEST boundary (log entries and media/*/upload.log
  both checked, newest upload.log tetherball 2026-09-21 10:40); this is
  insert attempt 1 of the hard cap of 5
- attempt 1 recorded at 2026-09-22T10:32:36+03:00, video name bounceslope, before running
  `scripts/yt-upload.py bounceslope`

### Published

- upload: `scripts/yt-upload.py bounceslope` ran 10:32:36 to 10:32:42 EEST,
  token verified to see only the Seed Zero channel, video id
  hlBy6yci8_U, private (`media/bounceslope/upload.log`)
- gate: `scripts/yt-qa.py bounceslope hlBy6yci8_U --wait --publish` ran in
  the foreground from 10:32:52 EEST: processing succeeded and the 10 tags
  read back on the first poll, 15 of 15 pass (processed, succeeded, hd,
  1080x1920, title, description, tags as a set, category 27, not for
  kids, PT41S for the 40.000 s file, private); containsSyntheticMedia
  reads absent as on every earlier upload (`media/bounceslope/publish.log`)
- publish: the same run set the video public at 2026-09-22T10:33:10+03:00;
  the re-read after 15 s shows privacyStatus public, madeForKids false,
  embeddable true; public at https://youtu.be/hlBy6yci8_U
- slot resolution: published for the 2026-09-22 quota day

### Quota

- attempt 1 of the hard cap of 5 for the quota day that began
  2026-09-22T10:00 EEST; cost 1 + 1,600 + 53 = 1,654 units (the
  channels.list verification inside yt-upload.py, the insert, the gate
  run's reads, update and re-read as printed by yt-qa.py); day total
  after one attempt 1,654 units
