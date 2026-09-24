# Produce short: Merry-go-round throw, the ground view beside the rider's view

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day26

## Goal

Backlog idea (trend research 2026-09-23, task 20260923-101345, pillar 2
chaos and physics, rotation; read the full entry under "Added by trend
research 2026-09-23" in docs/niche.md):
"Merry-go-round throw: a 2 m platform at 10 rpm, a 4 m/s throw straight
at the rider opposite, the ground view beside the rider's view; measure
the miss; expect a 2.0 m chord (the target moves 60 degrees in the
1.000 s flight; 2 R sin(omega R / v)) with the ball straight from above
and curving in the rider's view; exactly periodic so the short loops;
deterministic, no seed."
Research feasibility numbers (task 20260923-101345): 1.000 s flight,
the target moves 60.0 degrees, a 2.000 m chord (2.094 m of arc).
Orchestrator note (2026-09-24, before this brief): a thrower standing
on the rim moves sideways with the platform, so a ball thrown "straight
at the rider" from the rim does not fly straight across in the ground
frame and the research's numbers do not hold as written. Put the
thrower at the centre of the platform (the one point that does not
move) and the friend on the rim: the ball's ground path is then an
exact straight line at the throw speed, the rider's-view path is the
same line seen from the turning platform (r = v t, angle -omega t), the
friend moves omega R / v radians during the flight and the miss is the
chord 2 R sin(omega t_flight / 2). With the research's headline numbers
the platform has radius 2 m, turns at 10 rpm and the throw is 2 m/s:
flight 1.000 s, the friend moves 60.0 degrees, chord 2.000 m, arc 2.094
m. The producer may pick other round values (for example 4 m/s and a 4
m radius, or a rate whose period divides the scene length so the short
loops exactly: 10 rpm is a 6 s turn, so 42 s holds 7 turns; 12 rpm is a
5 s turn, so 40 s holds 8), as long as the sim prints the chosen values
and the loop closes.
Day twenty-six, third slot. Chosen because it is a two-view piece on
the same throw (the ground view beside the rider's view; one ball, one
throw) with continuous periodic motion, a plain question and an exact
closed-form check, the format of the channel's best shorts (turntable
ball 973, hoop bead 925, Dzhanibekov 946), and because the ball curving
in the rider's view while flying dead straight from above is the whole
Coriolis story in one picture. Question in the first two seconds:
"Throw straight at your friend on a merry-go-round. Do you hit them?"
(or the producer's better wording, kept identical in the title, the
hook and the payoff). Setup number: the turn rate (or the throw
speed); payoff number: the miss in meters.
Model: kinematics only; the platform turns at a constant rate, the ball
leaves the centre at the throw speed aimed at the friend's position at
the instant of the throw, flies in a straight line at constant speed
across the platform (rolling or sliding on a frictionless deck, or a
flat toss; state which) and crosses the rim after R / v seconds; the
rider's view rotates the same positions by -omega t. Print the flight
time, the angle the friend moves, the chord and arc miss, where the
ball crosses the rim relative to the friend, the closed forms, the
rider's-view path (the Coriolis curve) and the deflection direction
(the ball curves opposite to the turn), and text widths. One throw per
turn or a spacing that fits the loop; make the last frame equal the
first. Music seed 82.

## Claim

On a merry-go-round two meters across from centre to rim turning ten
times a minute, a ball thrown from the centre straight at a friend on
the rim at two meters a second flies dead straight from above and still
misses: the friend has moved sixty degrees around the rim in the one
second flight and the ball crosses the rim two meters away from them,
curving away in the rider's view. Every number in the narration is
printed by the sim before the script is written (the producer may
change the round values; the sim sets the claim).

## Evidence

### Measurements

(recorded after the measure-only run, before scripting)

`sims/merrygoround/merrygoround.py --measure-only` with
`projects/merrygoround/manifest.json` (a round platform of radius 2 m
turning counterclockwise, seen from above, at 10 rpm, 6.000 s per turn;
you stand at the centre, the one point that does not move, and the
friend rides the rim at platform angle 90 degrees; at each throw a ball
leaves the centre at 2 m/s aimed exactly at the friend, a flat toss
seen from above, horizontal motion only, no air, a straight line at
constant speed in the ground frame; the ride view rotates every
position by -omega t; the ground path sampled and the ride view
integrated with RK4 in the turning frame at 10,000 steps per second;
real time, one throw every 3 s, 14 throws and 7 turns in 42 s; drawn at
105 px per metre, rim radius 210 px; deterministic, no seed; run at
10:24:33 EEST, log in `media/merrygoround/measure.log`):

- flight: the ball crosses the rim after 1.0000 s (closed form R / v =
  1.0000 s, diff 0); the friend moves 60.00 degrees = 1.0472 rad in
  that time (closed form omega R / v = 60.00 degrees); the friend's rim
  speed is omega R = 2.0944 m/s against the ball's 2 m/s
- miss: the chord between the friend and the crossing point is 2.0000
  m (closed form 2 R sin(omega R / (2 v)) = 2.0000 m, diff 2.2e-16); the
  arc along the rim is 2.0944 m (R omega R / v = 2.0944 m); the ball
  crosses the rim at the ground point where the friend was at the
  throw, 60.0 degrees behind the friend (clockwise of them, opposite
  to the turn); the centre, the friend and the crossing point form a
  triangle with two sides R and 60.0 degrees between them, an
  equilateral triangle, so the miss equals the radius (chord - R =
  -4.4e-16 m)
- ride view (RK4 in the turning frame with the Coriolis and
  centrifugal terms): the ball crosses the rim after 1.0000 s at
  platform angle 30.00 degrees, 60.00 degrees clockwise of the friend
  at 90 degrees (closed form a_f - omega R / v = 30.00); chord to the
  friend 2.0000 m; max distance from the rotated straight line r = v t,
  angle a_f - omega t, over all steps 2.7e-13 m; half-step check
  1.000000 s against 1.000000 s (diff 9.2e-15 s)
- direction: v x a stays negative in the turning frame, so the ball
  curves to its right (clockwise on screen), opposite to the
  platform's counterclockwise turn; at the rim it is 1.000 m along the
  aim line and 1.732 m to the side of it; the sideways (Coriolis)
  acceleration in the turning frame is 2 omega v = 4.1888 m/s^2
  throughout the flight, the outward (centrifugal) term omega^2 r grows
  from 0 to 2.1932 m/s^2 at the rim
- ride-view path (t, r, platform angle, x, y): 0.00 s, 0 m, 90.0 deg;
  0.25 s, 0.500 m, 75.0 deg (0.129, 0.483); 0.50 s, 1.000 m, 60.0 deg
  (0.500, 0.866); 0.75 s, 1.500 m, 45.0 deg (1.061, 1.061); 1.00 s,
  2.000 m, 30.0 deg (1.732, 1.000)
- for the description (same platform, other throw speeds): 1 m/s:
  flight 2.000 s, the friend moves 120.0 degrees, chord 3.464 m, arc
  4.189 m; 4 m/s (the research's figure): flight 0.500 s, 30.0
  degrees, chord 1.035 m, arc 1.047 m
- schedule printed by the sim (first manifest, first_throw_at -0.4 s,
  to be set from the voice timing): the platform angle is 0 at the
  first throw; throws every 3 s alternate between ground directions 90
  and 270 degrees (the friend's position at each throw instant, half a
  turn apart); each ball crosses the rim 1.00 s after its throw and
  fades out 0.10 s later, 0.2 m beyond the rim; the miss marker holds
  from the crossing until 0.4 s before the next throw; the aim line
  leads each throw by 0.4 s; crossings at 0.60, 3.60, ..., 39.60 s;
  title until 2.4 s; the title fades back in over the last 0.5 s and
  the last frame repeats the first (the scene is periodic: 42 s holds
  exactly 7 turns and 14 throws)
- text widths (DejaVuSans-Bold): overlay 869 px at 34; title lines 718
  and 728 px at 56; counter 238 px, panel labels 257 and 298 px, clock
  270 px, miss readout 271 px at 40; legend 843 px, "you" and "friend"
  tags 57 and 95 px at 28; payoff lines 515, 515, 662 and 883 px at 40
  (a first draft of line 4, "your friend moves 60 degrees in the 1.00 s
  flight", measured 1,105 px and was shortened before any render);
  nothing over 950 px; the sim asserts every line under 950 px

Narration numbers: ten turns a minute (setup; the radius and the throw
speed stay on the overlay and the legend); two meters (payoff; the
measured chord 2.0000 m, shown as 2.00 m on the miss readout and the
card). The flight time, the 60 degrees, the arc, the rim speed, the
ride-view path and the checks go to the description (60 degrees and
1.00 s also on the card). No number contradicted the claim; the claim
text is left as written (the sim confirms 1.000 s, 60.0 degrees, a
2.000 m chord and a 2.094 m arc).

### Production

- layout (`sims/merrygoround/merrygoround.py`): overlay at y 96, title
  "Merry-go-round: / do you hit your friend?" at y 190/252 for the
  first 2.4 s, then the turn counter "turn k of 7" at y 236 and the
  legend "you at the center, friend on the rim, flat toss at 2 m/s" at
  y 290 (28 px, muted); two platforms stacked at 105 px per metre (rim
  radius 210 px): "from above" with its readout row at y 360 (label at
  40 px, the flight clock "flight 0.83 s" right-aligned at x 700, the
  miss readout "miss 2.00 m" in gold right-aligned at x 980) over the
  platform centred at (540, 640), and "from the ride" with its row at
  y 930 over the platform centred at (540, 1190); the deck is eight
  alternating sectors fixed to the platform with a rim ring, twelve
  ground ticks just outside the rim fixed to the ground (they turn in
  the ride view), you as a white disc at the centre with a "you" tag,
  the friend as a gold disc on the rim with a "friend" tag fixed to
  the platform, the ball a coral disc with a coral trail; each throw
  shows a dashed aim line (it follows the friend for 0.4 s before the
  throw, then stays fixed in each view's own frame), the ball, its
  trail (a straight line in the ground view, the spiral r = v t, angle
  -omega t in the ride view), the flight clock running to 1.00 s, and
  at the crossing a white cross at the crossing point, a gold chord to
  the friend and the miss readout; in the ground view the cross, the
  chord, the ghost ring where the friend was at the crossing and the
  gold arc the friend moved along the rim stay fixed to the ground
  while the friend rides on; in the ride view the same marks are fixed
  to the platform; the ball fades out over 0.2 m beyond the rim; the
  marker holds until 0.8 s before the next throw and fades over 0.4
  s; throws every 3 s alternate between up and down in the ground
  view (the friend is half a turn on), always toward the top of the
  ride view; geometry band y 380 to 1436 drawn at 2x and reduced;
  captions at caption_y 0.75; the four-line card from y 1592
- whisper pre-tests (10:25:47 to 10:29 EEST, before the full take;
  `media/merrygoround/hooks/`, log `hooks/pretest.log`): every passage
  passed the round trip on its first pass: hook1 "Merry-go-round
  throw. Do you hit your friend? You stand at the center." (4.37 s),
  hook2 "A throw on a merry-go-round. Do you hit your friend? ..."
  (4.16 s), hook3 "Throw straight at your friend on a merry-go-round.
  Do you hit them? ..." (4.89 s; "straight" survived), the setup group
  "Your friend rides the rim. Ten turns a minute. The top view is from
  above. The bottom view rides with the platform. You throw right at
  your friend. From above, the ball flies in a straight line, and your
  friend rides away from it. From the ride, the platform holds fixed,
  and the ball curves off to the side." (16.36 s; "in a straight
  line" survived) and the payoff group "Same throw, same miss, every
  time. Watch the ball reach the rim. It arrives right where your
  friend was a moment ago. So, do you hit your friend? No. The ball
  misses by two meters, every time." (11.48 s; the number came back as
  "2 meters"); the question onset was then measured on the hook wavs
  (silencedetect at -35 dB, 0.08 s, plus the 0.6 s offset): after a
  full stop the question starts at 2.38 s (hook1) and 2.30 s (colon
  variant hook5), after "Throw straight at your friend on a
  merry-go-round." at 3.7 s (hook3), after "Merry-go-round throw," at
  2.00 s (hook4), after "One throw," at 1.54 s (hook8) and after
  "Merry-go-round," at 1.69 s (hook7); hook7 kept: the merry-go-round
  stays in the lead-in and the question starts inside two seconds;
  the title and the card carry the same words with a colon
  ("Merry-go-round: / do you hit your friend?"), the narration a comma
- smoke frames (`--frames`): pass 1 at 10:26:09 EEST (at 0, 0.5, 1.2,
  2.6, 3.0, 3.6, 4.5, 5.6, 6.1, 30.5, 41.6, 41.98 s) found two
  defects: at the crossing instant the trail and the rim arc dropped
  to black for 0.15 s because their alpha followed the marker's
  fade-in, and in the ground view the cross and the chord were fixed
  to the platform while the trail was fixed to the ground, so the
  cross walked away from the end of the trail; fixed by holding the
  trail and the arc at full alpha until the marker fade and by
  drawing the ground view's marker as a ground-fixed snapshot (cross,
  chord, ghost ring, arc); pass 2 at 10:29:28 EEST found the ground
  view's aim line pointing at the friend's crossing position after
  the throw instead of along the throw (fixed: the aim line after the
  throw is the throw direction in the ground view and the friend's
  platform angle in the ride view); pass 3 at 10:30:55 EEST (at 0,
  1.65, 2.6, 3.7, 24.6, 26.0, 30.9, 41.7, 41.98 s) found the clock
  reading "flight 0.00 s" on the exact crossing frame (the frozen
  clock keyed on the marker's fade-in alpha) and the returning title
  overlapping the fading turn counter during the loop fade; fixed by
  keying the frozen clock on the hold alpha, ending the marker hold
  before the aim lead (hold to 2.2 s of each 3 s cycle, fade to 2.6
  s, aim lead 2.6 to 3.0 s) and splitting the loop fade (counter,
  legend and card gone over the first 0.25 s, the title in over the
  last 0.25 s); pass 4 at 10:31:59 EEST (at 0, 2.6, 24.6, 26.3, 26.8,
  30.9, 41.6, 41.75, 41.9, 41.98 s) clean: "flight 1.00 s" frozen on
  the crossing frame with the ball on the rim, the aim lead following
  the friend, the throw at 26.6 s leaving the centre, the card lit at
  30.9 s, the HUD gone at 41.75 s before the title returns, the last
  frame equal to the first
- narration (written after the measure-only run, 10:25 EEST;
  `projects/merrygoround/narration.txt`, 107 words, American
  spelling): "Merry-go-round, do you hit your friend?" then the setup
  (you at the center, the friend on the rim, "Ten turns a minute." as
  its own sentence so the number and unit sit in one 19-character
  caption chunk), the two views named as on the labels ("from above",
  "the ride"), the throw, the ground-view line and the friend riding
  away, the ride-view curve, "Same throw, same miss, every time.",
  "Watch the ball reach the rim." for the crossing, "It arrives right
  where your friend was a moment ago." for the ghost, and the payoff
  "So, do you hit your friend? No. The ball misses by two meters,
  every time." (the chunks are "The ball misses by | two meters, every
  | time.", the number whole with its unit; "You miss by two meters."
  would have split "two | meters" and was not used); chunks() checked
  before recording; "still", "pull", "got", "spread", "straight" as a
  lone word, "brakes", "drifts", "dives", "a hundred", possessives and
  "and a half" avoided ("the platform holds fixed" instead of "stands
  still", "from the ride" instead of "the rider's view"); the setup
  number is the turn rate, the payoff number the miss; the throw
  speed and the radius stay on the overlay and the legend
- voice: `scripts/voiceover.sh projects/merrygoround/narration.txt`
  pass 1 at 10:29:05 EEST passed, "ok: transcript matches narration":
  107 words, 32.12 s, ends at 32.72 s of the 42 s video, 3.33 words/s;
  log in `media/merrygoround/voice.log`
- timing (`scripts/voice-timing.py`, +0.6 s offset, log in
  `media/merrygoround/timing.log`, with the fine pause table from
  silencedetect at -35 dB, 0.08 s appended): "Merry-go-round, do you
  hit your friend?" 0.60 to 2.67 with the pause after "Merry-go-round"
  at 1.44 to 1.65, so the question starts at 1.65 s; "You stand at
  the center." 2.67 to 4.01; "Your friend rides the rim. Ten turns a
  minute." 4.01 to 6.67; "The top view is from above. The bottom view
  rides with the platform." 6.67 to 10.62; "You throw right at your
  friend. From above," 10.62 to 13.00 with the throw at 11.60 s; "the
  ball flies in a straight line," 13.00 to 14.87 with the 11.6 s
  throw's straight trail held to 14.2 s; "and your friend rides away
  from it, from the ride," 14.87 to 17.52 with the throw at 14.60 and
  the friend riding off the aim point to 15.60; "the platform holds
  fixed, and the ball curves off to the side. Same throw, same miss,
  every time." 17.52 to 23.49 with throws at 17.60 and 20.60; "Watch
  the ball reach the rim." 23.62 to 24.99 with the crossing at 24.60
  s; "It arrives right where your friend was a moment ago." 25.14 to
  27.91 with the ghost ring, cross and chord held to 26.2 s; "So, do
  you hit your friend?" 28.02 to 29.46; "No," 29.69 to 30.05; "the
  ball misses by two meters," 30.23 to 31.73 with the crossing at
  30.60 s and "two meters" from about 31.1 s; "every time." 31.94 to
  32.57; the per-piece transcript merged "From above" into the
  previous piece and "from the ride" into the next (pause splits, not
  mishearings; the full-file round trip matched)
- schedule decisions: first_throw_at -0.4 s (the first ball is 0.4 s
  into its flight on the first frame, motion in progress under the
  title, and crosses the rim at 0.6 s), which puts the crossings at
  0.6 + 3 k s: 24.60 s inside "Watch the ball reach the rim" (23.62
  to 24.99) and 30.60 s inside "the ball misses by" (30.23 to 31.0),
  just before "two meters"; payoff_t 30.3 s from the timing, so the
  card is fully lit at 30.9 s, after "No" (29.69 to 30.05) and before
  the payoff number at about 31.1 s; the caption "two meters, every"
  runs 31.52 to 32.42 s with the card lit and "miss 2.00 m" on both
  rows (the 30.6 s marker holds to 32.2 s)
- footage: `sims/merrygoround/merrygoround.py` (no arguments) wrote
  `media/merrygoround/footage.mp4`, 42.00 s at 60 fps, 2,520 frames,
  h264 crf 16 yuv420p, in 41 s with eight forked workers, 10:32:33 to
  10:33:14 EEST; the same run re-printed every measurement above
  (`media/merrygoround/render.log`); loop check on the raw frames: the
  last frame differs from the first in 0 px (max channel difference
  0); periodicity check: the scene drawn live at 42 s differs from 0
  s in 0 px; the frame before the last differs from the last in 5,416
  px (the platform turns 1.00 degrees per frame)
- compose: `scripts/compose.sh merrygoround` wrote
  `media/merrygoround/final.mp4` at 10:33:57 EEST (h264 1080x1920 60
  fps, 2,520 frames, aac 22050 Hz mono, 42.000 s, 5,283,064 bytes;
  music seed 82 at gain 0.18; captions at caption_y 0.75, 38 drawtext
  filters, the overlay plus 37 caption chunks); loudness mean -16.5
  dB, peak -0.0 dB; preview (42.07 s) and 8x6 contact sheet written
  (`media/merrygoround/compose.log`)

### Local QA

- smoke passes 1 to 3 (10:26 to 10:31 EEST, `--frames` before any
  render): four defects found and fixed (the trail and arc blackout
  at the crossing, the platform-fixed cross in the ground view, the
  aim line direction, the clock and the title overlap in the loop
  fade; see Production); pass 4 (10:31:59 EEST) clean before the
  footage render
- final pass (10:34 EEST): frames at 0.02, 1.7, 3.0, 12.0, 24.6,
  27.0, 30.95, 31.4, 41.6 and 41.98 s extracted from final.mp4
  (`media/merrygoround/frame-*.png`) and inspected with the 8x6
  contact sheet (`media/merrygoround/sheet.png`): 0.02 s shows the
  overlay "radius 2 m | 10 rpm | flat toss 2 m/s | no seed" at y 96,
  the title "Merry-go-round: / do you hit your friend?" at y 190 and
  252 clear of it, both platforms with the friend at the top of the
  ride view and just past the top of the ground view, the ball 0.43 s
  into its flight with its straight trail above and its curved trail
  below, "flight 0.43 s" on both rows, no caption yet (the thumbnail);
  1.7 s shows the caption "you hit your friend?" under the title with
  the first crossing's cross, chord and "miss 2.00 m" on both rows;
  3.0 s shows the counter "turn 1 of 7" and the legend in place of the
  title under "You stand at the"; 12.0 s shows the 11.6 s throw in
  flight under "your friend."; 24.6 s shows the crossing frame,
  "flight 1.00 s" frozen, the ball on the top of the rim with the gold
  arc to the friend 60 degrees on, and the ride-view ball at 30
  degrees, under "Watch the ball reach"; 27.0 s shows the ground-fixed
  cross, ghost ring and chord with the friend ridden on, under "where
  your friend"; 30.95 s shows the card "merry-go-round: / do you hit
  your friend? / no: the ball misses by 2.00 m / your friend moves 60
  degrees in 1.00 s" fully lit with "miss 2.00 m" on both rows under
  "The ball misses by"; 31.4 s the same with the friend further on;
  41.6 s shows the loop fade starting (counter, legend and card
  dimming, the 41.6 s throw at "flight 0.00 s"); 41.98 s shows the
  title frame (the last frame equals the first); captions match the
  narration word for word (the contact sheet reads every chunk in
  order) and sit in the y 1440 to 1502 band; the lowest geometry row
  is 1419 (the ground ticks), no frame has content in rows 1422 to
  1439, and the card's glyphs start at row 1576; the widest text (the
  overlay, 869 px) is centred with 105 px margins and the widest
  content column span is 98 to 978, nothing clips; the payoff number
  is on screen when spoken (the card from 30.9 s and "miss 2.00 m"
  from 30.75 s against "two meters" from about 31.1 s, caption "two
  meters, every" 31.52 to 32.42); the question starts at 1.65 s with
  the title on screen from frame 0 and the question caption from 1.20
  s; the loop closes: the raw last frame differs from the raw first
  frame in 0 px (render.log), and on the encoded final frame 2519
  differs from frame 0 in 1,713 px by more than 24 levels (0.08
  percent, max channel difference 80, mean 0.28, encoder noise);
  ffprobe: h264 1080x1920, 60/1 fps, 2,520 frames (also by decode),
  aac 22050 Hz mono, 42.000000 s, atoms ftyp, moov, free, mdat (moov
  before mdat), md5 90047751655ef61ac9674f918797ad0a; approved locally
- measure.log refreshed at 10:35:13 EEST with the final manifest
  (payoff_t 30.3); every number identical to the 10:24:33 run

### Metadata

- `projects/merrygoround/metadata.json`: title "Merry-go-round: do you
  hit your friend? No, the ball misses by 2.0 m at 10 rpm" (78
  characters); description with the setup (2 m radius, 10 rpm, one
  turn every 6 s, you at the centre, the friend on the rim, the 2 m/s
  flat toss as a straight line at constant speed seen from above, the
  ride view as the same positions rotated by -omega t, the RK4 check
  in the turning frame at 10,000 steps per second, real time, 14
  throws and 7 turns in 42 s, no seed), a Measured list (1.0000 s
  flight, 60.00 degrees and 2.0944 m of arc, the 2.0000 m chord and
  the equilateral triangle, the crossing at the friend's throw-time
  position 60 degrees behind them, the 2.0944 m/s rim speed, the
  ride-view path at 0.25 s steps, the direction of the curve, the
  4.19 m/s^2 Coriolis and 2.19 m/s^2 centrifugal terms, the 2.7e-13 m
  and 9e-15 s checks, the 1 m/s and 4 m/s variants), a Why paragraph
  in plain words (the friend moves and the ball does not move with
  them; from above the ball goes where you aimed and reaches the rim
  where the friend was when you let go, but the rim has carried the
  friend 60 degrees on; from the ride the ball seems to bend away
  because the seat turns while the ball keeps its direction; the
  Coriolis effect named here only; faster turn or slower throw,
  bigger miss), the rerun line and the AI-made line; 10 tags
  (merry-go-round, coriolis effect, rotating frame, do you hit your
  friend, thrown ball, reference frames, physics, physics
  visualization, simulation, shorts); category 27; private;
  containsSyntheticMedia true; selfDeclaredMadeForKids false; the same
  keys in the same order as projects/racingballs/metadata.json
- not uploaded; task left open for the orchestrator's review and upload

### Release
- orchestrator review (10:51 EEST): the task evidence, the 8x6 contact
  sheet and the full-resolution frames at 0.02, 30.95 and 41.98 s
  inspected: the question "Merry-go-round: / do you hit your friend?" over
  the two platform views from frame 0 with the first throw already in
  flight ("flight 0.43 s"), "you" at the centre and "friend" on the rim in
  both views (the thumbnail); 30.95 s shows turn 6 with "flight 1.00 s
  miss 2.00 m" on both rows, the chord drawn from the friend to the
  crossing mark in the ground view and the curved ride-view path ending
  at the mark, the card "merry-go-round: / do you hit your friend? / no:
  the ball misses by 2.00 m / your friend moves 60 degrees in 1.00 s" lit
  under the caption "The ball misses by"; 41.98 s matches the first frame
  (the title over the next throw in flight, no crossfade needed because
  the platform makes exactly 7 turns in 42 s); the timing table puts the
  question words at 1.65 s after the pause following "Merry-go-round";
  the narrated numbers (ten turns a minute, two meters) match the 10 rpm
  setup and the 2.0000 m chord in media/merrygoround/measure.log, with
  the thrower at the centre as briefed; captions sit in the y 1440 to
  1520 band clear of the geometry; final.mp4 h264 1080x1920 60 fps, 2,520
  frames, aac 22050 Hz mono, 42.000 s (scene_duration 42, inside the 30
  to 45 s range, so the gate accepts PT42S or PT43S), moov before mdat,
  md5 90047751655ef61ac9674f918797ad0a; title 78 characters; the
  description carries no < or >; the producer's 2 m/s toss and the
  two-throws-per-turn schedule accepted; approved for release
- quota check: clock 2026-09-24T10:51:41+03:00; three upload attempts (ballistic,
  10:46:59, published as bEni27RJgM4 at 10:47:53; superball, 10:48:38,
  failed with invalidDescription; superball, 10:50:02, published as
  l-MyYaMlxc8 at 10:50:55) recorded since the 2026-09-24 10:00 EEST
  boundary (log entries and media/*/upload.log both checked); this is
  insert attempt 4 of the hard cap of 5
- attempt 4 recorded at 2026-09-24T10:51:41+03:00, video name merrygoround,
  before running `scripts/yt-upload.py merrygoround`


### Published
- upload: `scripts/yt-upload.py merrygoround` (attempt 4) ran 10:53:35 to
  10:53:43 EEST, token verified to see only the Seed Zero channel, video
  id z_YTpx0EntM, private (`media/merrygoround/upload.log`)
- gate: `scripts/yt-qa.py merrygoround z_YTpx0EntM --wait --publish` ran
  in the foreground from 10:53:46 EEST: processing succeeded and the 10
  tags read back on the first poll, 15 of 15 pass (processed, succeeded,
  hd, 1080x1920, title, description, tags as a set, category 27, not for
  kids, PT43S for the 42.000 s file, private); containsSyntheticMedia
  reads absent as on every earlier upload (`media/merrygoround/publish.log`)
- publish: the same run set the video public at 2026-09-24T10:54:21+03:00;
  the re-read after 15 s shows privacyStatus public, madeForKids false,
  embeddable true; public at https://youtu.be/z_YTpx0EntM
- slot resolution: published for the 2026-09-24 quota day


### Quota
- attempt 4 of the hard cap of 5 for the quota day that began
  2026-09-24T10:00 EEST; cost 1 + 1,600 + 54 = 1,655 units (the
  channels.list verification inside yt-upload.py, the insert, the gate
  run's reads, update and re-read as printed by yt-qa.py); day total after
  four attempts 6,566 units, 3,434 remaining before the stats refresh


### Repository
- committed as 26e1279 "Publish the day twenty-six slate" (sims,
  projects, tasks, docs/niche.md, web/data; no media, previews or
  secrets) and pushed to origin/master at 2026-09-24 10:57 EEST; the
  yt-upload.py bracket check went out in the owner's earlier commit
  4b1345c at 10:52

