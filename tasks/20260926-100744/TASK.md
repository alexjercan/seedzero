# Produce short: Weight on a spring, lowered gently beside let go from the rest height

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day28

## Goal

Backlog idea (trend research 2026-09-25, task 20260925-101408, pillar 2
chaos and physics, springs; read the full entry under "Added by trend
research 2026-09-25" in docs/niche.md):
"Weight on a spring: a 1 kg weight lowered gently onto a spring that
sags 5 cm under it, beside the same weight let go from the spring's
rest height; measure the deepest squash; expect 5.00 cm against 10.00
cm, exactly double (m g x = k x^2 / 2), bouncing between 0 and 10 cm
every 0.449 s for ever; from 5 cm above the spring 13.7 cm; RK4
matches; periodic so the short loops; deterministic, no seed."

Orchestrator notes (2026-09-26, before this brief). The model: a 1.00
kg weight on a vertical massless spring with no damping, stiffness k =
m g / 0.05 m = 196.2 N/m, chosen so the spring sags exactly 5.00 cm
under the weight at rest. Panel A (lowered): a hand lowers the weight
from the spring's free top at a slow, steady rate (about 2 cm/s, so the
motion is quasi-static); the spring compresses as the hand descends,
the hand's share of the load falls as k x and reaches zero at x = 5.00
cm, where the weight rests on the spring alone; the hand lets go and
moves away. If the hand releases while still moving at u, the weight
oscillates with amplitude u / omega (2 cm/s gives 1.4 mm); either ease
the hand to a stop at 5 cm (then the residual is zero) or print the
residual amplitude and say so; the producer chooses. Panel B (let go):
the same weight released from rest touching the free top of the
spring; it descends to 10.00 cm (x_max = 2 m g / k, from m g x = k x^2
/ 2), stops for an instant, returns to 0 and bounces between 0 and 10
cm every 0.4486 s (2 pi sqrt(m / k)) for ever; x(t) = (m g / k) (1 -
cos(omega t)), omega = sqrt(k / m) = 14.01 rad/s. Integrate panel B by
RK4 or velocity Verlet at 10,000 steps a second and check it against
the closed form; print the deepest squash, the time to reach it (a
half period, 0.2243 s), the period, and the speed as it passes 5 cm
(omega times 5 cm, 0.700 m/s). g = 9.81 m/s^2.

State every derived number above as a check the sim must print, not as
a fact: 5.00 cm lowered, 10.00 cm let go, exactly double, period
0.4486 s, 0.2243 s to the bottom, 0.700 m/s through the 5 cm mark;
also print for the description the squash when the weight is dropped
from 5 cm above the spring (13.66 cm; m g (h + x) = k x^2 / 2) and from
10 cm above (print it), and the static sag under 2 kg (10.00 cm, the
same number by a different route, worth one line in the description).

Drawing: two panels side by side or stacked, the same spring and
weight in both: a coil drawn as a zigzag that compresses, a block on
top, a hand or bracket in panel A, a centimetre scale beside each
spring with marks at 0, 5 and 10 and a marker that stays at the
deepest point reached; a legend saying "no friction, no damping". Slow
motion for panel B (1/4 speed gives a bounce every 1.79 s) and a
lower-hold-lift cycle for panel A; make both cycles divide the scene
length so the scene is periodic and the last frame equals the first
(a cycle length that is a whole number of frames), and print the
schedule in video time and the loop check.

Day twenty-eight, third slot. Chosen because it is a lower-or-drop
question everyone can picture (the spring swap 836 and the Zeno bounce
636 are the family), two panels on the same spring that end apart, an
exact factor of two a closed form checks, and no seed. Question in the
first two seconds: "Lower a weight onto a spring, or drop it on. How
far does the spring squash?" (or the producer's better wording; keep
the words before the question under nine, e.g. "Drop it, or lower it.
How far does the spring squash?"; keep the question identical in the
title, the hook and the payoff). Setup number: five centimeters (the
spring sags five centimeters when the weight is lowered). Payoff
number: ten centimeters, exactly double, when it is dropped. The
period, the half period, the 13.7 cm and the 0.70 m/s go to the card
and the description. Make the last frame equal the first. Measure
every fixed text line with PIL before rendering and keep every line
under 950 px. Music seed 88.

## Claim

A 1 kg weight lowered gently onto a spring that sags exactly 5.00 cm
under it at rest, beside the same weight let go from rest at the
spring's free top: lowered, the spring squashes 5.00 cm and the weight
rests there; dropped, it squashes 10.00 cm, exactly double (m g x = k
x^2 / 2), and bounces between 0 and 10 cm every 0.449 s for ever. Every
number in the narration is printed by the sim before the script is
written; the sim sets the claim.

## Evidence

### Measurements

(recorded after the measure-only run, before scripting)

`sims/springdrop/springdrop.py --measure-only` with
`projects/springdrop/manifest.json` (a 1 kg weight on a vertical
massless spring, no friction, no damping; the stiffness set so the
spring sags exactly 5 cm under the weight at rest, k = m g / 0.05 m =
196.2 N/m; g 9.81 m/s^2; omega = sqrt(k / m) = 14.0071 rad/s, one bounce
every 2 pi / omega = 0.4486 s; left panel: a hand lowers the weight from
the spring's free top over 4 s along a smootherstep profile (1.25 cm/s
on average, 2.34 cm/s at most, easing to a stop at the sag), stays on it
for 2.8 s carrying nothing, moves away, comes back 9 s after the release,
lifts it back over 4 s and holds it at the top for 3 s, a 20 s cycle in
real time; right panel: the same weight let go from rest
touching the free top, integrated by RK4 at 10,000 steps per second (dt
1e-4 s) against the closed form x(t) = (m g / k)(1 - cos omega t), shown
4.4586x slow so one bounce fills 2 s (120 frames); 2 lowering cycles and
20 bounces in 40 s; drawn at 2000 px per metre; deterministic, no seed;
first run at 10:23:30 EEST with a 2.5 s lowering on a 10 s cycle, the
numbers below recorded from it before scripting; re-run at 10:28:08 EEST
with the final 4 s lowering on a 20 s cycle set from the voice timing,
the physics unchanged, only the hand's inertial term and the schedule
differ; log in `media/springdrop/measure.log`):

- static: the spring force k x balances the weight m g = 9.81 N at x =
  m g / k = 5.00 cm (the setup number); under 2 kg the sag is 10.00 cm;
  the spring pushes with 9.81 N at 5 cm (the weight) and 19.62 N at 10
  cm (twice the weight)
- lowered: the hand's share of the load is m g - k x - m x'' (the
  inertia of the smooth profile is at most 0.18 % of the weight on the
  final 4 s lowering, 0.47 % on the first run's 2.5 s lowering); it
  falls from 100.0 % (9.81 N) at the free top to 0.0 % (0.0e+00 N) at x
  = 5.00 cm and never goes negative (minimum 0.00 %, so the hand only
  ever carries, never holds down); quasi-static shares 0 cm 100 %, 1 cm
  80 %, 2 cm 60 %, 3 cm 40 %, 4 cm 20 %, 5 cm 0 %; the lift back needs
  0.0 to 100.0 % of the weight; after the hand lets go at 5.00 cm with
  zero speed, RK4 over 9 s (3.5 s on the first run) moves the weight at
  most 0.0e+00 mm from the sag (no wobble; the sag is the equilibrium); a hand that let go
  while still moving at 2 cm/s would leave a wobble of u / omega = 1.43
  mm (RK4 1.43 mm)
- dropped: let go from rest at the free top; RK4 reaches its deepest
  squash 10.0000 cm at 0.2243 s (closed form 2 m g / k = 10.0000 cm at a
  half period 0.2243 s; 10.00 cm, 2.0000 times the static sag, exactly
  double), comes back up to 2.0e-13 cm at 0.4486 s (closed form 0.4486
  s; one bounce every 0.449 s), passes the 5 cm resting point on the way
  down at 0.7004 m/s at 0.1121 s (closed form omega x = 0.7004 m/s at a
  quarter period 0.1121 s); over 20 bounces (8.97 s) RK4 stays within
  2.0e-13 m and 2.8e-12 m/s of the closed form and the 20 bottoms lie
  between 10.0000 and 10.0000 cm; energy: m g x_max = 0.9810 J against k
  x_max^2 / 2 = 0.9810 J; no damping, so it bounces between 0 and 10 cm
  for ever
- for the description (RK4 with the spring pushing only while the
  weight is on it): from 5 cm above the spring the deepest squash is
  13.66 cm at 0.257 s (closed form m g (h + x) = k x^2 / 2: 13.66 cm,
  diff 6.0e-8 cm); from 10 cm above, 16.18 cm at 0.288 s (closed form
  16.18 cm, diff 2.4e-7 cm); the first run reported the same depths at
  1.799 and 0.864 s because its argmax over 2 s of bouncing picked a
  later bottom (diffs 1.4e-6 and 8.5e-8 cm), fixed to report the first
  bottom before the re-run
- schedule printed by the sim (first manifest, lower_at 6.0 s on a 10
  s cycle of 2.5 s lowering, 3.5 s rest, 2.5 s lift and 1.5 s hold:
  lowering at 6.0, 16.0, 26.0, 36.0 s; replaced after the voice timing
  by the final manifest, lower_at 7.7 s and bottom_at 0 s): the lowered
  panel runs in real time on a 20 s cycle (1200 frames): lowering
  starts at 7.7, 27.7 s, the hand lets go 4 s later at 11.7, 31.7 s
  (the weight rests at the sag from then on), stays on it carrying
  nothing for 2.8 s and moves away over 0.6 s from 14.5, 34.5 s, comes
  back over 0.6 s and lifts from 20.7, 40.7 s, holds at the top for the
  last 3 s of the cycle; the dropped panel runs 4.4586x slow on a 2 s
  cycle (120 frames): at the top at 1 + 2 k s, at its deepest at 0 + 2
  k s; on the first frame the lowered weight rests at 5 cm, 5.50 s
  after the hand moved away, and the dropped weight is at its deepest
  point; title until 3 s, then the legend, the tags, the live readouts
  and the fixed lines; payoff card from 29.8 s; the title fades back in
  over the last 0.5 s and the last frame repeats the first (the scene
  is periodic: 40 s holds exactly 2 lowering cycles and 20 bounces)
- text widths (DejaVuSans-Bold): overlay 871 px at 34; title lines 662,
  409 and 601 px at 56 (the brief's question "How far does the spring
  squash?" measures 1036 px on one 56 px line, so the title is three
  lines: "Lowered or dropped:" / "how far does" / "the spring squash?");
  legend 593 px at 40, tag 482 px at 28; panel labels 376 and 368 px at
  40; panel tags 142 and 299 px, live readouts 303 and 239 px, fixed
  lines 261, 421, 281 and 465 px, scale label 94 px, block label 68 px
  at 28; payoff lines 461, 735, 669 and 884 px at 40; nothing over 950
  px; the sim asserts every line under 950 px and every panel line
  under 470 px

Narration numbers: five centimeters (setup; the static sag m g / k =
5.00 cm, the lowered panel's deepest squash) and ten centimeters
(payoff; the dropped panel's deepest squash 10.0000 cm by RK4, 2 m g / k
closed form, 2.0000 times the sag). The 0.449 s period, the 0.2243 s to
the bottom, the 0.70 m/s through the 5 cm mark, the 13.66 cm from 5 cm
above and the 2 kg sag go to the card, the readouts and the description.
The numbers match the brief; no change to the claim.

### Production

- layout (`sims/springdrop/springdrop.py`): overlay "1 kg on a spring |
  lowered, dropped | no seed" at y 96 (drawn by compose from the
  manifest), title "Lowered or dropped: / how far does / the spring
  squash?" at y 172/234/296 (56 px, three lines because the question
  measures 1036 px on one line) for the first 3 s, then the legend "same
  weight, same spring" at y 236 (40 px) and the tag "no friction, no
  damping, no air" at y 290 (28 px, muted); two panels side by side at
  2000 px per metre, spring centres at x 225 and 765, each with its label
  "lowered by hand" / "let go at the top" at y 380 (40 px), its time-base
  tag "real time" / "slow motion, 4.46x" at y 420 (28 px, muted), its
  live readout "hand carries N %" / "speed N m/s" at y 460 (28 px) and
  its fixed lines "deepest 5.00 cm" (gold) / "the hand carries 0 % there"
  and "deepest 10.00 cm" (gold) / "exactly double, every 0.449 s" at y
  502/536 (28 px), all left-aligned at x 40 / 580; the spring base at y
  1380 with hatching to 1397, the free top at 880, a 10-coil teal zigzag
  that compresses, a light-grey 0.12 by 0.10 m block labelled "1 kg", a
  coral hand bracket (bar, two fingers, stem) over the lowered block that
  lifts 80 px and fades when it moves away, a centimetre scale 158 px
  right of each spring with ticks every centimetre and labels 0, 5, 10
  cm, a gold triangle on the scale and a gold dashed line across the
  block at the deepest point (5 cm left, 10 cm right, shown with the
  HUD); geometry band y 320 to 1420 drawn at 2x and reduced; captions at
  caption_y 0.75 (y 1440 to 1520); the four-line card from y 1592 (40
  px, 56 px pitch); the HUD (legend, tag, panel tags, live readouts,
  fixed lines, markers, card) fades out over the first 0.25 s of the
  last 0.5 s and the title fades in over the last 0.25 s, the last frame
  equal to the first; the cycle phases and the bounce phase are frame
  integers modulo the cycle length so the periodicity is exact
- whisper pre-tests (10:17:11 to 10:18:22 EEST, `media/springdrop/hooks/`,
  logs `hooks/pretest.log` and `hooks/onsets.log`): every passage passed
  on its first pass; eight hook variants, question onset from
  silencedetect (-35 dB, 0.08 s) plus the 0.6 s offset: hook1 "Lower the
  weight, or drop it. How far does the spring squash?" 2.26 s, hook2
  "Drop it, or lower it. How far ..." 1.99 s, hook3 "A weight, a spring.
  Lower it, or drop it. How far ..." 3.51 s, hook4 "Lower it, or drop
  it, how far ..." 2.16 s, hook5 "Lower it or drop it. How far ..." 1.96
  s, hook6 "Lower the weight or drop it, how far ..." 2.40 s, hook7
  "Lowered or dropped, how far does the spring squash?" 1.85 s, hook8
  "Lower it or drop it, how far ..." 2.23 s; the mechanism group "On the
  left, a hand lowers the weight, slowly. ... Every bounce, the same
  depth." (22.08 s) and the payoff group "So, lower the weight, or
  drop it. How far does the spring squash? Five centimeters lowered.
  Ten centimeters dropped. Exactly double." (7.96 s; the final payoff
  opens "So, lowered or dropped, how far ..." to match hook7 and was
  verified only in the full take, which passed); hook7 kept: the earliest question, and "lowered" / "dropped"
  are the words of the panel labels, the card and the payoff; the brief's
  two suggested hooks are hook1 and hook2 (2.26 and 1.99 s)
- narration (`projects/springdrop/narration.txt`): 104 words, 14
  sentences, "five centimeters" and "ten centimeters" the only measured
  numbers, both in words ("two ways down" is not a measurement); no
  "still", "pull", "spread", "straight", "a hundred", "metres", "brakes",
  "drifts", "games", "let's", "lets go", "onto", "for ever" or
  sentence-initial "Where" (the whisper mishearing list); "let go" as a
  verb only
- smoke frames (`--frames`, two passes): pass 1 at 10:24:09 EEST on the
  first 10 s cycle (0, 0.5, 1.0, 1.5, 2.9, 6.0, 7.25, 8.5, 8.8, 12.5,
  15.0, 29.85, 39.6, 39.98 s) found the title's third line at y 314
  touching the panel labels at y 362 and the dropped panel's live speed
  printed with a sign on the way up ("speed -0.41 m/s"); fixed by moving
  the title rows to 172/234/296 and the panel text rows to
  380/420/460/502/536 and printing the speed magnitude; pass 2 at
  10:28:11 EEST on the final 20 s cycle (0, 1.5, 2.9, 7.7, 9.7, 11.7,
  13.5, 14.8, 16.0, 22.7, 26.0, 31.9, 34.0, 39.6, 39.98 s) clean: the
  title clear of the labels at 0 s, the hand lingering at "hand carries
  0 %" on the resting weight at 13.5 s with the dropped weight through
  the 5 cm mark at "speed 0.70 m/s", the card at 31.9 s; smoke 39.98
  equals smoke 0.0 (0 px); the caption band rows 1420 to 1530 at the
  background on every smoke frame (max deviation 0); content rows 148 to
  1397 (1782 with the card), columns 40 to 1043; the pass 1 frames not
  redrawn by pass 2 (0.5, 1.0, 6.0, 7.25, 8.5, 8.8, 12.5, 15.0, 29.85 s)
  deleted so only the final cycle's smoke frames remain
- voice (`scripts/voiceover.sh springdrop`, log
  `media/springdrop/voice.log`): pass 1 at 10:25:33 EEST passed, "ok:
  transcript matches narration (35.027302s)"; voice.wav 35.03 s, ends at
  35.63 s of video with the 0.6 s offset
- timing (`scripts/voice-timing.py media/springdrop/voice.wav`, log
  `media/springdrop/timing.log`, video time): "lowered or dropped." 0.60
  to 1.70, the question "How far does the spring squash?" 1.70 to 3.70
  (silencedetect on the full take puts the pause after "dropped," at
  1.50 to 1.90 s, so the word "how" sounds at 1.90 s), "Same weight,
  same spring, two ways down." 3.70 to 6.38, "On the left," 6.38 to
  7.20, "a hand lowers the weight slowly ... five centimeters down" 7.20
  to 12.98, "The hand carries nothing," 12.98 to 14.55, "and it moves
  away." 14.55 to 15.86, "The weight rests there." 15.86 to 17.23, "On
  the right." 17.23 to 18.06, "The same weight is let go at the top."
  18.06 to 20.11, "nothing carries it" 20.11 to 21.23, "It is moving
  fast at the resting point," 21.23 to 23.36, "so it goes on down ...
  So, lowered or dropped," 23.36 to 29.78, "How far does the spring
  squash? 5 centimeters lowered. 10 centimeters dropped. Exactly double."
  29.78 to 35.63; silencedetect on the tail: the question 29.91 to
  31.52, "Five centimeters lowered." 31.69 to 33.05, "Ten centimeters
  dropped." 33.17 to 34.43, "Exactly double." 34.60 to 35.54
- schedule (manifest): the lowering cycle changed from the brief's
  2.5 s lowering on a 10 s cycle to a 4 s lowering (1.25 cm/s on
  average, 2.34 cm/s at most, against the brief's "about 2 cm/s") on a
  20 s cycle (lower 4, rest 9, lift 4, hold 3 s) with the hand lingering
  2.8 s at 0 % before it moves away, so that the descent spans the
  narration: lower_at 7.7 puts the hand at the top holding the weight
  during "On the left," (6.38 to 7.20), the lowering under "a hand
  lowers the weight slowly. The spring takes the load bit by bit." (7.7
  to 11.7 s), the arrival at 5.00 cm at 11.7 s under "Five centimeters
  down," (caption 11.71 to 12.39), the hand still on the weight at "hand
  carries 0 %" under "the hand carries nothing," (12.98 to 14.55) and
  moving away 14.5 to 15.1 s under "and it moves away." (14.55 to
  15.86), the weight at rest under "The weight rests there." (15.86 to
  17.23); the second lowering 27.7 to 31.7 s so the weight rests at 5 cm
  under "Five centimeters lowered." (31.69 to 33.05) and the hand moves
  away 34.5 to 35.1 s under "Exactly double."; bottom_at 0 puts the
  dropped weight at its deepest at every even second, at 34.0 s under
  "Ten centimeters dropped." (33.17 to 34.43), and at the top at every
  odd second, at 19 s under "let go at the top" (18.06 to 20.11);
  title_until 3.0 (the question caption "spring squash?" runs to 3.63
  s); payoff_t 29.8 with a 0.6 s fade, so the card is fully lit at 30.4
  s, inside the spoken question (29.91 to 31.52) and before the numbers
- footage (`nix develop -c python3 sims/springdrop/springdrop.py`, log
  `media/springdrop/render.log`): one render 10:29:01 to 10:29:32 EEST:
  loop check 0 px (max channel difference 0), periodicity check 0 px
  (the scene drawn live at 40 s against 0 s), loop step 3,205 px; 2,400
  frames, eight forked workers, h264 crf 16 yuv420p 60 fps, footage.mp4
  5,170,049 bytes, 40.00 s; `--measure-only` re-run into
  `media/springdrop/measure.log` at 10:28:08 EEST with the final
  manifest and sim (no change since)
- compose (`scripts/compose.sh springdrop`, log
  `media/springdrop/compose.log`): one run 10:29:39 to 10:30:08 EEST:
  music seed 88 at 40.00 s (gain 0.18), 37 caption chunks (longest 20
  characters; "Five centimeters" and "Ten centimeters" each one chunk),
  final.mp4 5,180,539 bytes 40.000000 s, preview.mp4 540x960 30 fps
  1,136,089 bytes 40.066667 s, sheet.png 8x5 at 1 fps 628,830 bytes
- text widths (measure.log, PIL at the drawn sizes): overlay 871 px,
  title lines 662, 409 and 601 px, legend 593 px, tag 482 px, panel
  labels 376 and 368 px, panel tags 142 and 299 px, live readouts 303
  and 239 px, fixed lines 261, 421, 281 and 465 px, scale label 94 px,
  block label 68 px, card lines 461, 735, 669 and 884 px, all under 950
  px and every panel line under its 470 px column; the first card draft
  "lowered 5 cm, dropped 10 cm: exactly double" measured 1029 px and was
  split across lines 3 and 4 before any render; the brief's question on
  one 56 px title line measured 1036 px, hence the three-line title

### Local QA

- frames (`media/springdrop/frame-<t>.png` from final.mp4 at 0.02, 2.0,
  9.7, 13.5, 15.0, 32.3, 34.0, 35.0 and 39.98 s, plus `sheet.png`)
  inspected: 0.02 s: overlay and the three-line title from frame 0, both
  "1 kg" blocks with their scales, the lowered block at rest with its
  bottom at the 5 mark and no hand, the dropped block at its deepest
  with its bottom at the 10 cm mark (the thumbnail); 2.0 s: caption "how
  far does the" in the band under the panels, the title still up, the
  hand on the lowered block partway up its lift, the dropped block at
  the 10 cm mark; 9.7 s: caption "The spring takes the", the legend and
  tags in place of the title, the hand lowering the block through 2.5 cm
  with "hand carries 50 %", the gold markers at 5 and 10 cm, the dropped
  block on its way down at "speed 0.57 m/s"; 13.5 s: caption "carries
  nothing, and", the lowered block at rest on the 5 cm marker with the
  hand still on it at "hand carries 0 %", the dropped block through the 5
  cm mark at "speed 0.70 m/s"; 15.0 s: caption "it moves away.", the
  hand lifted 80 px and faded to a dark red, the dropped block at the top
  at "speed 0.00 m/s"; 32.3 s: caption "does the spring", the card
  "lowered or dropped: / how far does the spring squash? / lowered 5 cm,
  dropped 10 cm / exactly double; a bounce every 0.449 s" lit under it,
  the lowered block resting at 5 cm with the hand lingering, the dropped
  block rising through 5 cm; 34.0 s: caption "Ten centimeters", the
  dropped block at its deepest with its bottom on the gold 10 cm marker
  at "speed 0.00 m/s", the card lit; 35.0 s: caption "Exactly double.",
  the hand moving away on the left, the dropped block at the top; 39.98
  s: the title back and the HUD gone, matches 0.02 s; the contact sheet
  shows the captions in narration order, the hand cycling twice and the
  card from 30 s to 39 s
- question inside two seconds: the title carries the question from
  frame 0; the narration reaches "how far does the spring squash?" after
  three words; the word "how" sounds at 1.90 s of video (pause 1.50 to
  1.90 s in video time on the full take; timing.log chunk boundary 1.70
  s; hook7 pre-test 1.85 s); the caption "Lowered or dropped," shows
  0.60 to 1.61 s, "how far does the" 1.61 to 2.96 s and "spring squash?"
  2.96 to 3.63 s
- captions: the 37 chunks read back from `media/springdrop/captions.filter`
  match the 104 narration words exactly, in order; longest chunk 20
  characters; "Five centimeters" (16) is one chunk 32.93 to 33.61 s and
  "Ten centimeters" (15) one chunk 33.94 to 34.62 s
- payoff on screen when spoken: the card fades in 29.8 to 30.4 s and
  holds to the loop fade; "lowered 5 cm, dropped 10 cm" and "exactly
  double" are fully lit at 30.4 s while the question sounds 29.91 to
  31.52 s and stay lit through "Five centimeters lowered." (31.69 to
  33.05), "Ten centimeters dropped." (33.17 to 34.43) and "Exactly
  double." (34.60 to 35.54); the fixed lines "deepest 5.00 cm" and
  "deepest 10.00 cm" are up from 3.4 s; the dropped block sits on the 10
  cm marker at 34.0 s (frames 32.3 and 34.0 inspected); the captions
  "Five centimeters" and "Ten centimeters" lag the voice by about 1.2 s
  (proportional timing), and the card and the fixed lines cover the gap
- clipping and bands: every one of the 2,400 footage frames scanned
  (numpy, more than 24 levels from the background): content columns 40
  to 1043 of 0 to 1079 and rows 148 to 1783; the caption exclusion band
  rows 1420 to 1530 never deviates more than 2 levels from the
  background (0 frames over 8 levels); the lowest geometry row is 1397
  (the base hatching); the card starts at 1592
- loop: the raw last frame equals the first (0 px, max channel
  difference 0) and the live scene at 40 s equals 0 s (0 px); in the
  encoded final.mp4 frame 2399 against frame 0 differs in 27,332 px by
  more than 8 levels (max channel difference 109, mean 0.36 levels, 866
  px over 32 levels on the title and block edges), the same order as the
  published bucket final (20,985 px, max 67, mean 0.31), i.e. h264
  quantisation on the second-generation encode, not content; the loop
  step from frame 2398 to 2399 is 34,448 px
- ffprobe final.mp4: h264 1080x1920 yuv420p 60/1 fps, 2,400 frames,
  40.000000 s, 5,180,539 bytes, aac 22050 Hz mono, moov before mdat;
  md5 62dafe629446d58ae27013a5d81bd93a
- narrated numbers against measure.log: "Five centimeters" is the static
  sag m g / k = 5.00 cm and the lowered panel's deepest squash (the hand
  lets go at x = 5.00 cm with 0.0e+00 N and RK4 moves the weight 0.0
  mm); "Ten centimeters" is the dropped panel's RK4 deepest squash
  10.0000 cm (closed form 2 m g / k = 10.0000 cm); "Exactly double" is
  2.0000 times the static sag; the card's "a bounce every 0.449 s" is the
  0.4486 s period; the tag "slow motion, 4.46x" is 4.4586; the live
  "speed 0.70 m/s" at the 5 cm mark is 0.7004 m/s; "hand carries 50 %"
  at 2.5 cm is the quasi-static share 1 - x / sag; "1 kg" on the blocks
  and the overlay is mass_kg 1.0
- no defect left

### Metadata

- `projects/springdrop/metadata.json`: title "Lowered or dropped: how
  far does the spring squash? 5 cm lowered, 10 cm dropped, exactly
  double" (95 characters); description (2,828 characters) with the setup
  (1 kg on a vertical massless spring, no friction, no damping, k = m g
  / 0.05 m = 196.2 N/m, the 4 s smooth lowering at 1.25 cm/s on average,
  the hand's share reaching zero at 5 cm, the linger and the lift on a
  20 s cycle, the drop from rest at the free top by RK4 at 10,000 steps
  per second against the closed form, 4.46x slow motion, 2 cycles and 20
  bounces in 40 s, no seed), a Measured list (the 5.00 cm sag with 9.81
  N and 19.62 N at 10 cm and the 2 kg sag 10.00 cm; the hand's share 100
  to 0 % with the quasi-static table, the 0.18 % inertial term, the 0.0
  mm residual and the 1.43 mm wobble of a 2 cm/s release; the 10.00 cm
  at 0.2243 s, 2.0000 times the sag, the 0.4486 s period, the 0.700 m/s
  through 5 cm, the 2e-13 m RK4 check and the 0.981 J energy check; the
  13.66 cm from 5 cm above and 16.18 cm from 10 cm above), a Why
  paragraph in plain words (the spring pushes back harder the deeper it
  goes; lowered, the hand carries what the spring cannot yet, so the
  weight arrives at 5 cm with no speed; dropped, gravity's work m g x
  outruns the stored k x^2 / 2 until x = 2 m g / k, exactly double; no
  damping, so it bounces for ever; the doubling holds for any weight and
  spring), the rerun line and the AI-made line; 10 tags (spring, weight
  on a spring, lowered or dropped, how far does the spring squash,
  spring compression, energy conservation, physics, physics
  visualization, simulation, shorts); category 27; private;
  containsSyntheticMedia true; selfDeclaredMadeForKids false; the same
  keys in the same order as projects/bucket/metadata.json; no "<" or ">"
- not uploaded; task left open for the orchestrator's review and upload

### Niche note

[produced 2026-09-26 as "Lowered or dropped: how far does the spring
squash?", the hand lowering over 4 s (1.25 cm/s on average, easing to a
stop so the release leaves no wobble; a 2 cm/s release would leave 1.43
mm) beside the same weight let go at the free top, shown 4.46x slow so a
bounce fills 2 s: lowered 5.00 cm (the hand's share falls from 100 % to
0 % there), dropped 10.00 cm at 0.2243 s, exactly double (2.0000 times
the sag), bouncing between 0 and 10 cm every 0.4486 s for ever, 0.700
m/s through the 5 cm mark, RK4 at 10,000 steps a second within 2e-13 m
of the closed form; from 5 cm above the spring 13.66 cm, from 10 cm
above 16.18 cm; the 2 kg sag is 10.00 cm; the title is three lines
because the question measures 1036 px at 56 px; task 20260926-100744]

Deviations from the brief: the hook is "Lowered or dropped, how far
does the spring squash?" (the brief's "Lower a weight onto a spring, or
drop it on" and "Drop it, or lower it" put the question at 2.26 and 1.99
s; this one at 1.90 s on the full take, and its words match the labels
and the payoff); the lowering takes 4 s (1.25 cm/s on average, 2.34 cm/s
at most) rather than about 2 cm/s so the descent spans its narration, and
the hand lingers 2.8 s at 0 % before moving away so "it moves away" lands
on the words; the hand eases to a stop at 5 cm (the brief's first
option), so the residual is zero and the 1.43 mm wobble of a moving
release is printed for the description; the dropped panel runs 4.4586x
slow (2 s per bounce, 120 frames) instead of 1/4 speed (1.79 s is not a
whole number of frames); the title is three lines at 56 px; the panel
label reads "let go at the top" to match the narration; the first
measure run reported the description drops at a later bounce (1.799 and
0.864 s), fixed to the first bottom (0.257 and 0.288 s) before the
re-run. The claim and every narrated number stand as briefed.

### Release
- orchestrator review (10:46 EEST): the task evidence, the 8x5 contact
  sheet and the full-resolution frames at 0.02, 13.5, 34.0 and 39.98 s
  inspected: the question "Lowered or dropped: / how far does / the
  spring squash?" over both panels from frame 0 with the lowered block
  at rest on the 5 cm mark and the dropped block at its deepest on the
  10 cm mark (the thumbnail); 13.5 s shows the coral hand bracket on
  the lowered block at "hand carries 0 %" with the block on the gold 5
  cm marker, the dropped block through the 5 cm mark at "speed 0.70
  m/s", the fixed lines "deepest 5.00 cm / the hand carries 0 % there"
  and "deepest 10.00 cm / exactly double, every 0.449 s", the legend
  "same weight, same spring" and the tag "no friction, no damping, no
  air", under the caption "carries nothing, and"; 34.0 s shows the
  dropped block on the gold 10 cm marker at "speed 0.00 m/s" with the
  card "lowered or dropped: / how far does the spring squash? / lowered
  5 cm, dropped 10 cm / exactly double; a bounce every 0.449 s" lit
  under the caption "Ten centimeters"; 39.98 s matches 0.02 s; the
  contact sheet shows the captions in narration order, the hand cycling
  twice and the card from 30 s; the narrated numbers (five centimeters,
  ten centimeters, exactly double) match the static sag m g / k = 5.00
  cm, the RK4 deepest squash 10.0000 cm and the 2.0000 ratio in
  media/springdrop/measure.log, and the orchestrator's own closed forms
  before the brief (k 196.2 N/m, 5.00 cm, 10.00 cm, period 0.4486 s,
  13.66 cm from 5 cm above) agree; the producer's changes (the hook
  "Lowered or dropped, how far does the spring squash?" for a 1.90 s
  question onset; a 4 s lowering easing to a stop with a 2.8 s linger;
  4.4586x slow motion for an exact 120-frame bounce; a three-line
  title) are recorded in the task and keep the claim; captions sit in
  the y 1440 to 1520 band, scanned clean on all 2,400 footage frames;
  final.mp4 h264 1080x1920 60 fps, 2,400 frames, aac 22050 Hz mono,
  40.000 s (scene_duration 40, so the gate accepts PT40S or PT41S), moov
  before mdat, md5 62dafe629446d58ae27013a5d81bd93a; title 95
  characters; the description carries no < or >; approved for release
- quota check: clock 2026-09-26T10:50:48+03:00; two upload attempts (chain, 10:47:12,
  published as hDic9PCXFKs at 10:48:06; tarzan, 10:49:13, published as
  f-ZLd4-azw0 at 10:49:59) recorded since the 2026-09-26 10:00 EEST
  boundary (log entries and media/*/upload.log both checked); this is
  insert attempt 3 of the hard cap of 5
- attempt 3 recorded at 2026-09-26T10:50:48+03:00, video name springdrop, before running
  `scripts/yt-upload.py springdrop`

### Published
- upload: `scripts/yt-upload.py springdrop` (attempt 3) ran 10:50:48 to
  10:50:55 EEST, token verified to see only the Seed Zero channel, video
  id 3jzgy7G2whs, private (`media/springdrop/upload.log`)
- gate: `scripts/yt-qa.py springdrop 3jzgy7G2whs --wait --publish` ran in
  the foreground from 10:51:16 EEST: processing had already succeeded and
  the 10 tags read back on the first read at 10:51:19, 15 of 15 pass
  (processed, succeeded, hd, 1080x1920, title, description, tags as a
  set, category 27, not for kids, PT41S for the 40.000 s file, private);
  containsSyntheticMedia reads absent as on every earlier upload
  (`media/springdrop/publish.log`)
- publish: the same run set the video public at 2026-09-26T10:51:21+03:00;
  the re-read after 15 s shows privacyStatus public, madeForKids false,
  embeddable true; public at https://youtu.be/3jzgy7G2whs
- slot resolution: published for the 2026-09-26 quota day

### Quota
- attempt 3 of the hard cap of 5 for the quota day that began
  2026-09-26T10:00 EEST; cost 1 + 1,600 + 52 = 1,653 units (the
  channels.list verification inside yt-upload.py, the insert, the gate
  run's single read, update and re-read as printed by yt-qa.py); day total
  after three attempts 1,655 + 1,655 + 1,653 = 4,963 units plus 5 for the
  10:03 stats refresh, target of three met
