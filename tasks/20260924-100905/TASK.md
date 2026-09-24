# Produce short: Ballistic pendulum, a ball that sticks beside a ball that bounces

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day26

## Goal

Backlog idea (trend research 2026-09-23, task 20260923-101345, pillar 2
chaos and physics, collisions; read the full entry under "Added by trend
research 2026-09-23" in docs/niche.md):
"Ballistic pendulum: a 20 g ball at 20 m/s into a 200 g block on a 1 m
string, a ball that sticks beside a ball that bounces; measure the
swing height and angle; expect 16.9 cm (33.8 degrees) against 67.4 cm
(71.0 degrees), exactly 4 times higher when it bounces at any mass
ratio ((2m/(M+m))^2 against (m/(M+m))^2), the stuck pair keeping 9.1
percent of the energy; the swing periods differ (2.05 against 2.22 s),
so repeat the shot rather than loop the swing; RK4; deterministic, no
seed."
Research feasibility numbers (task 20260923-101345): sticks: block
1.8182 m/s, rises 16.855 cm, 33.75 degrees, the pair keeps 9.09 percent
of the energy; bounces (elastic): block 3.6364 m/s, rises 67.419 cm,
70.99 degrees, the ball comes back at 16.36 m/s; height ratio 4.0000
exactly at every mass ratio tried (10 g at 300 m/s into 2 kg: 11.36
against 45.43 cm; 50 g at 15 m/s into 500 g: 9.48 against 37.92 cm);
RK4 swing at 0.1 ms: peaks 33.752 degrees at 0.5128 s and 70.985
degrees at 0.5545 s, back at the bottom at 1.0255 and 1.1089 s.
Day twenty-six, first slot. Chosen because it is a two-panel collision
on the same input (same ball, same speed, same block, same string; only
the hit differs) with continuous motion, an exact integer ratio and a
plain question, the format of the channel's best shorts (Newton's
cradle 958, pi collisions 943, coupled pendulum swap 1,046), and
because most viewers expect the ball that sticks, which hands over all
its momentum, to swing the block higher. Question in the first two
seconds: "Which swings the block higher: the ball that sticks, or the
ball that bounces?" (or the producer's better wording, kept identical
in the title, the hook and the payoff).
Model: the hit is instantaneous and horizontal through the block's
centre while the block hangs at rest at the bottom (momentum conserved
across the hit; the stuck hit is perfectly inelastic, the bouncing hit
perfectly elastic, a bouncy ball on a hard block); after the hit the
block (with the ball inside it in the sticking panel, alone in the
bouncing panel) swings as a point mass on a light rigid rod or taut
string, integrated with RK4; no air, no losses. Print the block speed
after each hit, the peak height above the rest position, the peak angle,
the time of the peak, the height ratio, the energy kept by each block
after the hit, the ball's speed after the bounce, the closed-form
checks (v = m u / (M + m) and 2 m u / (M + m); h = v^2 / 2 g; cos theta
= 1 - h / L) and a half-step check. State the model in the overlay and
the description. Check that the string stays taut (the block never
passes 90 degrees, so the closed form for the height holds) and print
the tension at the bottom. Shown slowed so the hit and the rise read;
the swing periods differ, so repeat the shot (fire, rise to the peak,
fall back, catch and reset) rather than loop the swing, and make the
last frame equal the first. Music seed 80.

## Claim

A twenty gram ball at twenty meters a second hits a two hundred gram
block hanging on a one meter string. When the ball sticks in the block,
the block swings up about seventeen centimeters. When the ball bounces
straight back, the same block swings up about sixty seven centimeters,
exactly four times higher, because the bouncing ball hands over twice
the momentum. Every number in the narration is printed by the sim
before the script is written.

## Evidence

### Measurements

(recorded after the measure-only run, before scripting)

`sims/ballistic/ballistic.py --measure-only` with
`projects/ballistic/manifest.json` (a 20 g ball at 20 m/s hits a 200 g
block hanging at rest at the bottom of a 1 m light string, horizontally
through the block's centre, in an instant, momentum conserved across
the hit; top panel a sticky ball, perfectly inelastic, the pair swings
together; bottom panel a bouncy ball, perfectly elastic, the ball comes
back and the block swings alone; after the hit a point mass on a taut
string, theta'' = -(g / L) sin theta, g = 9.80665, RK4 at 10,000 steps
per second from theta = 0, omega = v / L, the peak and the return
interpolated inside the step; no air, no losses; played at quarter
speed, 4 shots of 10 s; the string drawn at 400 px per metre, the ball
and the block drawn larger than scale; deterministic, no seed; run at
10:23:48 EEST, log in `media/ballistic/measure.log`):

- the hit: momentum before 0.4000 kg m/s, energy before 4.0000 J;
  sticky ball: the 220 g pair leaves at v = m u / (M + m) = 1.8182 m/s
  (momentum after 0.4000), energy after 0.3636 J, 9.09 percent kept;
  bouncy ball: the block leaves at v = 2 m u / (M + m) = 3.6364 m/s and
  the ball comes back at (m - M) u / (M + m) = -16.3636 m/s (momentum
  after 0.4000), the block carries 1.3223 J (33.06 percent), the ball
  keeps 2.6777 J (66.94 percent), total 4.0000 J; the bounce gives the
  block 2.0000 times the speed of the stuck pair; impulse on the block
  0.7273 N s against 0.3636 N s for the block inside the pair (0.4000 N
  s for the pair)
- sticky ball: the RK4 swing from 1.8182 m/s peaks at h = 16.8548 cm
  (closed form v^2 / 2 g = 16.8548 cm, diff 3.9e-8 cm; shown as 17 cm),
  33.7518 degrees (closed form acos(1 - h / L) = 33.7518), at t =
  0.5127 s after the hit (elliptic quarter period sqrt(L / g) K(sin(theta
  / 2)) = 0.5127 s, full period 2.0508 s); back at the bottom at 1.0254
  s (half period 1.0254) at -1.8182 m/s; string tension at the bottom
  1.3371 of the swinging weight = 2.8847 N, minimum over the swing
  0.8315 of the weight (at the peak), so the string stays taut; energy
  drift 1.5e-14
- bouncy ball: the RK4 swing from 3.6364 m/s peaks at h = 67.4193 cm
  (closed form 67.4193 cm, diff 1.0e-6 cm; shown as 67 cm), 70.9855
  degrees (closed form 70.9855), at t = 0.5544 s after the hit
  (elliptic quarter period 0.5544 s, full period 2.2177 s); back at the
  bottom at 1.1089 s (half period 1.1089) at -3.6364 m/s; tension at
  the bottom 2.3484 of the swinging weight = 4.6060 N, minimum over the
  swing 0.3258 of the weight (at the peak, cos 70.99 degrees), so the
  string stays taut; energy drift 1.9e-14
- ratio: the bouncy block rises 4.0000 times as high as the stuck pair
  (67.4193 / 16.8548 cm; closed form (2 m / (M + m))^2 / (m / (M + m))^2
  = 4 at every mass ratio); the angles are not in that ratio (70.99
  against 33.75 degrees, 2.103 times)
- half-step check (20,000 steps per second): sticky peak 16.854813 cm
  (+2.0e-8 cm), 33.751830 degrees at 0.512703 s (-2.6e-14 s), return at
  1.025405 s; bouncy peak 67.419254 cm (+7.8e-7 cm), 70.985498 degrees
  at 0.554436 s (-4.1e-14 s), return at 1.108871 s; energy drift 2.5e-14
  and 7.0e-15
- for the description, the same two hits at other mass ratios (closed
  form): 10 g at 300 m/s into 2 kg: 11.36 against 45.43 cm (27.6 against
  56.9 degrees on a 1 m string), ratio 4.0000; 50 g at 15 m/s into 500
  g: 9.48 against 37.92 cm (25.2 against 51.6 degrees), ratio 4.0000
- schedule printed by the sim (video time, quarter speed, first
  manifest): each 10 s shot fires the ball at 0.3 s from x = -1.12 m
  (52 px, inside the launcher), 1.0225 m of approach in 0.2045 s, the
  hit at 0.5045 s; the stuck pair peaks 2.0508 s after the hit (at
  2.5553 s) and is caught at the bottom at 4.6061 s; the bouncy block
  peaks 2.2177 s after the hit (at 2.7222 s) and is caught at 4.9400 s;
  the bouncy ball leaves the frame at 0.79 s; readouts held 4.06 s
  after the last catch, then a 0.5 s reset and 0.5 s at rest; peaks at
  2.56/2.72, 12.56/12.72, 22.56/22.72, 32.56/32.72 s (stick/bounce);
  title until 4 s; payoff card from 22 s (to be set from the voice
  timing); loop fade 39.5 to 40 s
- text widths (DejaVuSans-Bold): overlay "20 g at 20 m/s into 200 g |
  1/4 speed | no seed" 889 px at 34 (the first draft "20 g at 20 m/s |
  200 g block | 1/4 speed | no seed" was 940 px and "20 g ball at 20
  m/s | 200 g block | 1/4 speed | no seed" 1,022 px, both rejected
  before any render); title lines 820 and 865 px at 56; counter 241 px
  at 40; model tag 774 px at 28; panel labels 230 and 260 px at 40;
  sublabels 287 and 339 px at 28; "speed after the hit" 296 px at 28;
  speed value 193 px at 40; "rise" 59 and "peak" 77 px at 28; the rise
  readout "67 cm" 216 px at 64; mark labels 19 and 94 px at 28; payoff
  lines 581, 618, 844 and 370 px at 40; nothing over 950 px; the left
  readout column has 401 px before the block

Narration numbers: seventeen (the stuck pair's peak, 16.8548 cm shown as
17 cm on the readout and the mark; the setup number, spoken as the top
block peaks) and sixty seven (the bouncy block's peak, 67.4193 cm shown
as 67 cm; the payoff number), with "four times higher" for the measured
ratio 4.0000 and "twice the speed" for the measured 2.0000. The unit
goes in the sentence before ("The rise is marked in centimeters"),
because "seventeen centimeters" (21 characters) and "sixty seven
centimeters" (23) cannot sit whole in a 20-character caption chunk.
The 20 m/s, the 20 g and 200 g stay on the overlay; the block speeds
1.82 and 3.64 m/s sit on the readouts; the angles, the periods, the
energy shares, the rebound speed, the tension and the checks go to the
description. The claim's "about seventeen" (16.85) and "about sixty
seven" (67.42) hold and the ratio is exactly 4.0000; the claim's
"hands over twice the momentum" is narrated as "twice the speed"
(the block leaves at 3.6364 against 1.8182 m/s; the impulse on the
block is 0.7273 against 0.3636 N s, also twice). No number contradicted
the claim; the claim text is left as written.

### Production

- layout (`sims/ballistic/ballistic.py`): overlay at y 96, title
  "Sticky ball or bouncy ball: / which block swings higher?" at y
  190/252 for the first 4.0 s, then the shot counter "shot k of 4" at y
  236 and the model tag "point mass on a 1 m string, instant hit, no
  losses" at y 290; two panels of 543 px from y 350 (top: the sticky
  ball, teal; bottom: the bouncy ball, gold); in each panel the pivot at
  x 500, 70 px under the panel top, with a 400 px string (1 m at 400 px
  per metre), so the block hangs at rest 470 px under the panel top and
  swings to the right, up to x 878 and 270 px above its rest level; the
  ball waits in a launcher at the left edge on the rest level (x 52) and
  flies in along it with a 0.12 s fading trail; the block is a wood
  rectangle 56 x 48 px that turns with the string, the ball an 11 px disc
  in the panel colour (both larger than scale; the string is to scale);
  in the sticky panel the ball stays embedded in the block's hit face,
  in the bouncy panel it flies back left with a trail and leaves the
  frame 0.29 s after the hit; a white ring flashes at the launcher on
  the fire, at the contact point on the hit and at the rest position on
  the catch; the block traces its arc in the panel colour up to the
  highest angle reached and a tick marks the peak; a clamp (two
  brackets) appears when the block is caught at the bottom; readouts in
  the left column x 40..340: the label at 40 px in the panel colour,
  the sublabel ("sticks in the block" / "bounces off the block") at 28
  px, "speed after the hit" with "0.00 m/s" before the hit and "1.82
  m/s" / "3.64 m/s" in the panel colour after it, and "rise" with the
  live height at 64 px that turns into "peak" and the panel colour when
  the block turns (17 cm / 67 cm, whole centimetres, the measured
  16.8548 and 67.4193); dashed height marks at 0, 17 cm and 67 cm from
  x 540 to 930 with labels from x 946 in both panels; the readouts,
  the trace and the stuck ball fade out over the 0.5 s reset while a
  new ball fades into the launcher, then 0.5 s at rest; captions at
  caption_y 0.75; the four-line card from y 1592; geometry drawn at 2x
  and reduced
- whisper pre-test (10:25:03 to 10:25:13 EEST, before the full take;
  `media/ballistic/hooks/`): three hook variants and two sentence
  groups round-tripped through `scripts/voiceover.sh`, all passed on
  the first pass: "Sticky ball or bouncy ball: which block swings
  higher? Same mass, same speed, same block, same string. Only the ball
  differs." (8.14 s; the sentence-initial "Sticky" not clipped), "Which
  block swings higher: the one the ball sticks to, or the one it
  bounces off? Same mass, same speed, same string." (7.14 s), "A sticky
  ball, or a bouncy ball. Which block swings higher? Same mass, same
  speed, same block, same string." (7.12 s), the mechanism group "The
  rise is marked in centimeters. Watch the top block. The sticky ball
  sticks, and the pair swings up together, to seventeen. Below, the
  bouncy ball bounces back, and the block swings up alone. Much higher.
  Shot after shot, the same two peaks. The bounce gives the block twice
  the speed, and twice the speed lifts it four times as high." (19.56
  s; "seventeen" came back as 17) and the payoff group "Now watch the
  bottom block. It swings up to sixty seven. So, sticky ball or bouncy
  ball: which block swings higher? The bouncy ball. Four times higher."
  (8.85 s; "sixty seven" came back as 67)
- smoke frames (`--frames`, pass 1 at 10:24:00 EEST with every shot
  firing at 0.3 s, at 0, 0.4, 0.5, 0.7, 2.56, 2.72, 4.7, 5.2, 9.2, 9.7,
  22.5 and 39.8 s): no layout defect; the title clear of the panels,
  the ball trail from the launcher, the hit flash, the rebound trail,
  the peaks on the marks, the clamps, the mid-reset fade and the
  crossfade all read; pass 2 at 10:31:41 EEST after the timing
  (fire_at 2.8, payoff_t 24.6; at 0, 0.6, 2.56, 11.9, 13.0, 15.06, 17.5,
  23.0, 25.22, 25.5, 29.5 and 39.9 s) clean: the shot 1 readouts still
  frozen at 11.9 s with the launcher ball fading in, the shot 2 hit at
  13.0 s, "peak 17 cm" frozen at 15.06 s, both clamps at 17.5 s, the
  shot 3 bouncy peak on the 67 cm mark with the card lit at 25.22 s;
  nothing clips, nothing enters the caption band
- schedule change before the take: the first draft fired every shot at
  0.3 s into its 10 s period and reset at a fixed 9.0 s; the first
  timing table showed the shot 2 bouncy block already falling back
  while "bounces back, and the block swings up alone" was spoken, so
  the sim now takes `fire_at_first` (0.3 s, motion in the first second)
  and `fire_at` for shots 2 to 4, and each shot holds its frozen
  readouts until 1.0 s before the next fire (0.5 s reset, 0.5 s at
  rest); the last shot resets at 39.0 s so the loop fade plays over a
  scene at rest (asserted); the narration was restructured so that shot
  2 carries the top-block story and shot 3 the bottom-block story
- narration (written after the measure-only run, 10:27 EEST, final
  text 10:31 EEST): the first hook kept because it puts the title's
  words first and the question starts at 0.60 s (the pre-test showed
  the "Sticky" onset survives); `projects/ballistic/narration.txt`, 108
  words; the balls named by the panel labels ("sticky ball", "bouncy
  ball"); the setup number is "seventeen" (the stuck pair's peak, spoken
  as the shot 2 readout freezes) and the payoff number "sixty seven"
  (the bouncy block's peak, spoken as the shot 3 readout freezes), with
  the unit in the sentence before ("The rise is marked in
  centimeters"), because "seventeen centimeters" (21 characters) and
  "sixty seven centimeters" (23) cannot sit whole in a 20-character
  chunk; chunks() checked before every take: "to seventeen." and "to
  sixty seven." sit whole, "twice the speed." and "four times as high."
  sit whole; three earlier drafts rejected on the chunk check or the
  timing table: take 1 (109 words, 36.20 s, passed the round trip)
  split "four | times as high" and "twice the | speed"; take 2 (107
  words, 36.11 s, passed) had the narration order fighting the screen
  (see the schedule change); take 3 (105 words, 34.53 s, passed) split
  "alone, to sixty | seven", fixed with "alone, all the way to sixty
  seven"; "still", "pull", "got", "spread", "straight", "a hundred",
  "and a half" avoided; no possessives; the mechanism beat ("twice the
  speed") names what the speed readouts show
- voice: `scripts/voiceover.sh projects/ballistic/narration.txt` take
  4 at 10:31:33 EEST passed, "ok: transcript matches narration": 108
  words, 36.01 s, ends at 36.61 s of the 40 s video, 3.00 words/s; log
  in `media/ballistic/voice.log`; every take passed the round trip on
  its first pass (takes 1 to 3 kept in `media/ballistic/hooks/`)
- timing (`scripts/voice-timing.py`, +0.6 s offset, log in
  `media/ballistic/timing.log`): "sticky ball or bouncy ball." 0.60 to
  2.13 s (the question starts at 0.60 s, zero words before it, the
  title on screen from frame 0); "which block swings higher. Same
  mass, same speed," 2.13 to 5.51; "Same block, same string." 5.51 to
  7.42; "Only the ball differs." 7.42 to 8.91; "The rise is marked in
  centimeters." 8.91 to 11.02 with the shot 1 readouts frozen at 17 and
  67 cm since 2.56/2.72 s; "watch the top block the sticky ball sticks
  and the pair swings up together" 11.02 to 15.17 with the shot 1 reset
  at 11.80, the shot 2 fire at 12.80 and the hit at 13.00 s; "to 17 the
  pair falls back and the block is caught" 15.17 to 18.63 with the
  stuck pair's peak at 15.06 s (the readout frozen at "peak 17 cm" 0.11
  s before the words), the catches at 17.11 and 17.44 s; "ready for the
  next shot" 18.63 to 19.99; "Now watch the bottom block, the bouncy
  ball bounces back." 19.99 to 23.23 with the shot 3 fire at 22.80 and
  the hit at 23.00 s; "and the block swings up alone." 23.23 to 25.12
  with the bouncy block rising 23.00 to 25.22 s; "all the way to 67.
  So, sticky ball or bouncy ball," 25.12 to 27.67 with the bouncy peak
  at 25.22 s and the card lit from 24.6 s; "which block swings higher."
  27.67 to 28.92; "The bouncy ball." 28.92 to 30.39; "The bouncy ball
  gives the block twice the speed. Twice the speed." 30.39 to 35.28
  with the shot 4 hit at 33.00 s putting 1.82 and 3.64 m/s on the
  readouts; "four times as high" 35.28 to 36.61 with the shot 4 peaks
  at 35.06 and 35.22 s; the closing silence follows
- schedule decisions: fire_at_first 0.3 s (the ball leaves the
  launcher on the first shot under the title, both blocks at their
  peaks by 2.72 s); fire_at 2.8 s so that the shot 2 hit lands at 13.00
  s inside "the sticky ball sticks" (12.0 to 15.2), the stuck pair's
  peak at 15.06 s just before "to seventeen" (15.17), the catches at
  17.11/17.44 s inside "the block is caught" (to 18.63), the shot 3
  hit at 23.00 s on "bounces back" (piece ends 23.23) and the bouncy
  peak at 25.22 s just before "all the way to sixty seven" (from
  25.12); payoff_t 24.6 s from the timing, so the card is fully lit at
  25.2 s, before the first payoff number and as the bouncy block turns;
  shot 4 (fire 32.8, peaks 35.06/35.22, catches 37.11/37.44, reset 39.0,
  rest 39.5 to 40.0) plays under the card and lands both peaks on "four
  times as high"
- footage: `sims/ballistic/ballistic.py` (no arguments) wrote
  `media/ballistic/footage.mp4`, 40.00 s at 60 fps, 2,400 frames, h264
  crf 16 yuv420p, in 37 s with eight forked workers, 10:32:06 to
  10:32:43 EEST; the same run re-printed every measurement above
  (`media/ballistic/render.log`); loop check on the raw frames: the
  last frame differs from the first in 0 px (max channel difference 0)
- compose: `scripts/compose.sh ballistic` wrote
  `media/ballistic/final.mp4` at 10:33:40 EEST (h264 1080x1920 60 fps,
  2,400 frames, aac 22050 Hz mono, 40.000 s, 3,107,904 bytes; music
  seed 80 at gain 0.18; captions at caption_y 0.75, 36 drawtext
  filters, the overlay plus 35 caption chunks); loudness mean -16.7 dB,
  peak -0.0 dB; preview (40.07 s) and 8x5 contact sheet written
  (`media/ballistic/compose.log`)

### Local QA

- smoke pass 1 (10:24:00 EEST, `--frames` before any voice work): no
  layout defect; smoke pass 2 (10:31:41 EEST, after the timing) clean
  before the footage render; the defects fixed during production were
  in the inputs: the overlay shortened to 889 px before any render, the
  narration reworded three times on the chunk check and the timing
  table, the shot schedule split into a first fire time and a later
  fire time (see Production)
- final pass (10:34 to 10:36 EEST): frames at 0.02, 1.5, 4.5, 13.0,
  15.2, 17.5, 23.05, 25.3, 26.0, 35.3 and 39.95 s extracted from
  final.mp4 (`media/ballistic/frame-*.png`) and inspected with the 8x5
  contact sheet (`media/ballistic/sheet.png`): 0.02 s shows the overlay
  "20 g at 20 m/s into 200 g | 1/4 speed | no seed" at y 96, the title
  "Sticky ball or bouncy ball: / which block swings higher?" at y 190
  and 252 clear of it, both panels with their labels, "0.00 m/s" and
  "rise 0 cm", the marks 0, 17 cm and 67 cm, both blocks at rest and
  both balls in their launchers (the thumbnail); 1.5 s shows shot 1
  rising, the stuck pair at "rise 8 cm" and the bouncy block at "rise
  32 cm" with their traces, under "Sticky ball or"; 4.5 s shows "shot 1
  of 4" and the model tag in place of the title, both readouts frozen
  at "peak 17 cm" and "peak 67 cm" with the peak ticks, the pair back
  at the bottom and the bouncy block still falling, under "Same mass,
  same"; 13.0 s shows the shot 2 hit, both balls at the blocks with
  their trails, under "sticks, and the pair"; 15.2 s shows "peak 17
  cm" frozen in teal with the pair at its peak on the 17 cm mark and
  the bouncy block at "rise 67 cm" turning on the 67 cm mark, under
  "The pair falls back,"; 17.5 s shows both blocks caught in their
  clamps with the fading catch ring, under "and the block is"; 23.05 s
  shows the shot 3 hit: the sticky ball at its block with the hit
  flash and the bouncy ball already flying back with its trail, under
  "bounces back, and"; 25.3 s shows the bouncy block at "peak 67 cm"
  in gold on the 67 cm mark with its tick and the card lit, under
  "alone, all the way"; 26.0 s shows both peaks frozen and the bouncy
  block falling from its peak, under "to sixty seven." with the card;
  35.3 s shows shot 4 with both blocks at their peaks, 17 and 67 cm,
  under "four times as high." with the card; 39.95 s shows the
  crossfade to the title frame with the card and the counter fading;
  captions match the narration word for word (the contact sheet reads
  every chunk in order) and sit in the y 1440 to 1520 band with the
  lowest geometry at y 1393 (the bottom clamp) and the card from 1592;
  the widest text (the overlay, 889 px) is centred with 95 px margins
  and nothing clips at the frame edges; the payoff numbers are on
  screen when spoken (the card from 25.2 s and the gold "peak 67 cm"
  from 25.22 s against "all the way to sixty seven" from 25.12; the
  teal "peak 17 cm" from 15.06 s against "to seventeen" from 15.17);
  the loop closes: the raw last frame differs from the raw first frame
  in 0 px (render.log), and on the encoded final frame 2399 differs
  from frame 0 in 2,748 px by more than 24 levels (0.13 percent, at
  text edges, max channel difference 72, mean 0.42, encoder noise);
  ffprobe: h264 1080x1920, 60/1 fps, 2,400 frames (also by decode), aac
  22050 Hz mono, 40.000000 s, atoms ftyp, moov, free, mdat (moov before
  mdat), md5 0c23f9438d18531bef3476e3c9c95d34; approved locally

### Metadata

- `projects/ballistic/metadata.json`: title "Sticky ball or bouncy
  ball: which block swings higher? The bouncy ball: 67 cm against 17
  cm" (91 characters); description with the setup (20 g at 20 m/s into
  a 200 g block at rest on a 1 m string, the instant horizontal hit
  through the block's centre, the sticky and bouncy panels, the point
  mass on a taut string, RK4 at 10,000 steps per second, no air, no
  losses, the string to scale and the ball and block larger than
  scale, quarter speed, four shots, no seed), a Measured list (1.8182
  m/s and 16.855 cm at 33.75 degrees with 9.09 percent of the energy;
  3.6364 m/s and 67.419 cm at 70.99 degrees with 33.06 percent, the
  ball back at 16.36 m/s with 66.94 percent; the peak and return times;
  the ratio 4.0000 and the closed form with the two other mass ratios;
  the tension 1.34 and 2.35 of the weight at the bottom and 0.83 and
  0.33 at the peaks; momentum and energy conserved across the hit; the
  half-step and closed-form checks; the periods 2.0508 and 2.2177 s),
  a Why paragraph in plain words (the block only cares about the push
  at the hit; the bouncy ball is stopped and thrown back, so the block
  is pushed twice as hard and leaves at twice the speed; twice the
  speed is four times the energy, which the string turns into four
  times the height; the energy shares 9, 33 and 67 percent), the rerun
  line and the AI-made line; 10 tags (ballistic pendulum, momentum,
  elastic collision, inelastic collision, which swings higher,
  pendulum, physics, physics visualization, simulation, shorts);
  category 27; private; containsSyntheticMedia true;
  selfDeclaredMadeForKids false; the same keys in the same order as
  projects/racingballs/metadata.json
- not uploaded; task left open for the orchestrator's review and upload

### Release
- orchestrator review (10:46 EEST): the task evidence, the 8x5 contact
  sheet and the full-resolution frames at 0.02, 25.3 and 39.95 s inspected:
  the question "Sticky ball or bouncy ball: / which block swings higher?"
  over the two stacked panels from frame 0, both blocks at rest on their
  strings with "rise 0 cm" and the 17 and 67 cm marks on both scales (the
  thumbnail); 25.3 s shows shot 3 with both blocks at their peaks, "peak 17
  cm" in teal and "peak 67 cm" in gold with the swing arcs, the card "sticky
  ball or bouncy ball: / which block swings higher? / the bouncy ball: 67 cm
  against 17 cm / 4.0 times higher" lit under the caption "alone, all the
  way"; 39.95 s shows the crossfade to the title frame with "shot 4 of 4"
  fading, as in the racingballs short; the timing table puts the question at
  0.60 s with no words before it; the narrated numbers (seventeen, sixty
  seven, twice the speed, four times as high) match the sim's 16.8548 cm,
  67.4193 cm, speed ratio 2.0000 and height ratio 4.0000 in
  media/ballistic/measure.log; captions sit in the y 1440 to 1520 band clear
  of the geometry; final.mp4 h264 1080x1920 60 fps, 2,400 frames, aac 22050
  Hz mono, 40.000 s, moov before mdat, md5 0c23f9438d18531bef3476e3c9c95d34;
  title 91 characters; the producer's naming ("sticky ball", "bouncy ball")
  and the unit spoken in the sentence before the numbers accepted; approved
  for release
- quota check: clock 2026-09-24T10:46:59+03:00; zero upload attempts recorded
  since the 2026-09-24 10:00 EEST boundary (no "Upload attempt" entries
  dated today in web/data/log.jsonl and no media/*/upload.log newer than
  the boundary); this is insert attempt 1 of the hard cap of 5
- attempt 1 recorded at 2026-09-24T10:46:59+03:00, video name ballistic, before
  running `scripts/yt-upload.py ballistic`


### Published
- upload: `scripts/yt-upload.py ballistic` ran 10:47:06 to 10:47:11 EEST,
  token verified to see only the Seed Zero channel, video id bEni27RJgM4,
  private (`media/ballistic/upload.log`)
- gate: `scripts/yt-qa.py ballistic bEni27RJgM4 --wait --publish` ran in
  the foreground from 10:47:21 EEST: processing succeeded and the 10 tags
  read back on the first poll, 15 of 15 pass (processed, succeeded, hd,
  1080x1920, title, description, tags as a set, category 27, not for kids,
  PT41S for the 40.000 s file, private); containsSyntheticMedia reads
  absent as on every earlier upload (`media/ballistic/publish.log`)
- publish: the same run set the video public at 2026-09-24T10:47:53+03:00;
  the re-read after 15 s shows privacyStatus public, madeForKids false,
  embeddable true; public at https://youtu.be/bEni27RJgM4
- slot resolution: published for the 2026-09-24 quota day


### Quota
- attempt 1 of the hard cap of 5 for the quota day that began
  2026-09-24T10:00 EEST; cost 1 + 1,600 + 54 = 1,655 units (the
  channels.list verification inside yt-upload.py, the insert, the gate
  run's reads, update and re-read as printed by yt-qa.py); day total after
  one attempt 1,655 units


### Repository
