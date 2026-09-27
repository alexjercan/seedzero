# Produce short: Tablecloth pull, 1 m/s beside 3 m/s on the same cloth and glass

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day29

## Goal

Backlog idea (trend research 2026-09-27, task 20260927-102520, pillar 2
chaos and physics, friction; read the full entry under "Added by trend
research 2026-09-27" in docs/niche.md):
"Tablecloth: a glass 30 cm from the far edge of a cloth (glass on cloth
mu 0.2, glass on table 0.4, 40 cm from the table edge), the cloth
pulled at a steady 1.0 m/s beside 3.0 m/s; measure how far the glass
moves; expect the slow glass to reach cloth speed after 25 cm and ride
off the table at 0.66 s, the fast glass to move 1.05 cm on the cloth
plus 0.53 cm on the table, 1.6 cm, the cloth clear in 104 ms; the
threshold sqrt(2 mu g L) = 1.08 m/s (4 m/s gives 0.9 cm); repeat the
pull; deterministic, no seed."

Orchestrator notes (2026-09-27, before this brief). The model: a short
tumbler (a sliding block that does not tip: a block tips under friction
only if mu exceeds its width over its height; a 7 cm wide, 9 cm tall
tumbler has 0.78, above both 0.2 and 0.4, so print that check and say
"a short glass") stands on a tablecloth 0.30 m from the cloth's far
edge, 0.40 m from the table edge on the puller's side. At t = 0 the
cloth is pulled toward the table edge at a steady speed V (a jerk to V
that is then held; say "pulled at a steady speed"). Glass on cloth:
sliding friction mu 0.2, so the glass accelerates toward the puller at
mu g = 1.961 m/s^2 (g 9.80665) while the cloth slips under it. The
cloth has passed out from under the glass when the relative displacement
V t - mu g t^2 / 2 reaches L = 0.30 m, which needs V^2 / (2 mu g) >= L,
so the threshold is V* = sqrt(2 mu g L) = 1.085 m/s. Panel A, V = 1.0
m/s (below the threshold): the glass reaches cloth speed at t = V / (mu
g) = 0.510 s after moving V^2 / (2 mu g) = 25.5 cm (the cloth has moved
51 cm, 25.5 cm of it under the glass, so 4.5 cm of cloth is still under
it), rides with the cloth from then on and goes over the table edge
(0.40 m from its start) at 0.655 s. Panel B, V = 3.0 m/s: the cloth is
clear at t1 = (V - sqrt(V^2 - 2 mu g L)) / (mu g) = 103.5 ms with the
glass at 0.203 m/s having moved 1.05 cm; on the bare table (mu 0.4,
decel 3.923 m/s^2) it slides a further v1^2 / (2 mu2 g) = 0.53 cm in 52
ms and stops: 1.58 cm in all. V = 4.0 m/s gives 0.57 + 0.29 = 0.86 cm
(for the description), and V = 1.1 just clears (print it). Integrate
both panels by RK4 at 10,000 steps a second with the friction switching
at the cloth's edge and at zero slip, and check against these closed
forms; print the tipping check.

State every derived number above as a check the sim must print, not as
a fact: the threshold 1.085 m/s; at 1.0 m/s the 25.5 cm, 0.510 s, and
the ride off the edge at 0.655 s; at 3.0 m/s the 103.5 ms, 1.05 cm on
the cloth, 0.53 cm on the table, 1.58 cm in all, the 0.203 m/s handover
speed; for the description 4.0 m/s (0.86 cm), 1.1 m/s, 2.0 m/s (print),
and how the threshold scales with the cloth length (sqrt L) and the
cloth friction (sqrt mu). All numbers depend on the chosen mu 0.2 and
0.4 and L 0.30 m, so the overlay, card and description state them and
the narration says "with this cloth".

Drawing: two panels stacked, a side view of the table (edge at the
right), the cloth as a coloured band with a visible pattern or ticks so
its motion reads, the glass as a short tumbler with a mark on the table
at its start, a hand or arrow at the pull end, a live readout of the
glass's travel in centimetres; slow motion (1/8 or 1/10 speed) so the
3 m/s pull takes about a second on screen; the two panels on the same
clock; the pull repeated so the short loops (fade and reset as cueball
does, or a cycle length that divides the scene); the last frame equals
the first.

Day twenty-nine, third slot. Chosen because the tablecloth trick is a
question everyone has asked, the two panels on the same cloth end
opposite ways (the glass goes over the edge against 1.6 cm), the
threshold has a closed form, and no seed. Question in the first two
seconds: "Pull the tablecloth. How fast do you need to pull?" (or the
producer's better wording; keep the words before the question under
nine; keep the question identical in the title, the hook and the
payoff). Whisper turned the noun "pull" into "pole" twice and clips
sentence-initial words, so pre-test the hooks and prefer "pulled" or
"yank" if "pull" fails. Setup number: thirty centimeters of cloth under
the glass (or "one meter a second" for the slow pull; pick one for the
narration and put the other in the overlay). Payoff number: one point
one meters a second (the threshold, "faster than one point one meters a
second with this cloth"), with the two outcomes in words: at one meter
a second the glass rides off the table, at three it moves one and a
half centimeters. The 25 cm, the 104 ms and the 0.86 cm go to the card
and the description. Make the last frame equal the first. Measure every
fixed text line with PIL before rendering and keep every line under 950
px, and the title under 100 characters with no < or >. Music seed 91.

## Claim

A short glass (7 cm wide, 9 cm tall) on a tablecloth, 30 cm from the
cloth's far edge and 40 cm from the table edge, sliding friction 0.2 on
the cloth and 0.4 on the table, the cloth pulled at a steady 1.0 m/s
beside 3.0 m/s: at 1.0 m/s the glass reaches cloth speed after 25.5 cm
with 4.5 cm of cloth still under it, rides with the cloth and goes over
the table edge at 0.655 s; at 3.0 m/s the cloth is clear in 103.5 ms and
the glass moves 1.05 cm on the cloth plus 0.53 cm on the bare table,
1.58 cm in all. The cloth clears the glass only above sqrt(2 mu g L) =
1.085 m/s with this cloth. Every number in the narration is printed by
the sim before the script is written; the sim sets the claim.

## Evidence

### Measurements

(recorded after the measure-only run, before scripting)

`sims/tablecloth/tablecloth.py --measure-only` with
`projects/tablecloth/manifest.json` (a 7 cm wide, 9 cm tall glass on a
tablecloth 30 cm from the cloth's far edge and 40 cm from the table edge
on the puller's side; at t = 0 the cloth is pulled toward the table edge
at a steady speed, a jerk to V then held; sliding friction mu 0.2
between glass and cloth (mu g = 1.9613 m/s^2) and 0.4 between glass and
table (3.9227 m/s^2), g 9.80665 m/s^2, the cloth thin and massless; top
panel V = 1 m/s, bottom panel V = 3 m/s, both integrated by RK4 at
10,000 steps per second (dt 1e-4 s) with the friction switches located
by bisection inside the step; shown at 1/8 speed on an 8.4 s cycle (504
frames) with the yank 0.6 s into the cycle, 5 cycles in 42 s; drawn at
1000 px per metre; deterministic, no seed; run at 10:48:48 EEST, log in
`media/tablecloth/measure.log`):

- tipping check: a block tips under friction only if mu exceeds its
  width over its height; this glass has 7 / 9 = 0.778, above both 0.2
  (cloth) and 0.4 (table), so it slides and never tips on either surface
  (a glass taller than 17.5 cm at 7 cm wide would tip on the table)
- threshold: the cloth is clear of the glass only if V^2 / (2 mu g) >=
  L, i.e. V >= sqrt(2 mu g L) = 1.0848 m/s with this cloth (mu 0.2, L 30
  cm); it scales with the square root of the cloth length under the
  glass (15 cm: 0.767 m/s, 60 cm: 1.534 m/s) and of the cloth friction
  (mu 0.1: 0.767 m/s, mu 0.4: 1.534 m/s); the table friction 0.4 only
  sets how far the glass slides afterwards
- slow pull (1 m/s, below the threshold): RK4: the glass slides on the
  cloth, gaining 1.961 m/s^2, and reaches cloth speed 1.0000 m/s at
  0.5099 s after moving 25.49 cm (closed forms V / (mu g) = 0.5099 s,
  V^2 / (2 mu g) = 25.49 cm; diffs 2.9e-14 s, 1.6e-12 cm); by then the
  cloth has moved 50.99 cm, 25.49 cm of it out from under the glass, so
  4.51 cm of cloth is still under it (closed form 4.51 cm) and the cloth
  never clears; the glass rides with the cloth at 1 m/s and its centre
  passes the table edge 40 cm from its start at 0.6549 s (closed form
  0.6549 s, diff 2.9e-14 s), the cloth's far edge then 4.51 cm behind
  the glass and 4.5 cm from the table edge; the cloth's far edge leaves
  the table at 0.700 s; RK4 stays within 2.8e-14 m of the closed form
  over 6551 samples
- fast pull (3 m/s, above the threshold): RK4: the cloth is clear of
  the glass at 103.5 ms (closed form (V - sqrt(V^2 - 2 mu g L)) / (mu g)
  = 103.5 ms, diff 6.9e-14 ms) with the glass at 0.2030 m/s (closed form
  0.2030) having moved 1.051 cm (closed form 1.051); on the bare table
  it slows at 3.923 m/s^2 and stops at 155.3 ms after 0.525 cm more
  (closed forms v1^2 / (2 mu g) = 0.525 cm in 51.8 ms); 1.576 cm in all
  (closed form 1.576 cm, diff 3.4e-14 cm), 1.58 cm, 38.4 cm short of the
  table edge; it stays there to the end of the run (2.00 s); the cloth's
  far edge leaves the table at 0.233 s; RK4 stays within 3.4e-16 m of
  the closed form over 20001 samples
- the same cloth and glass end opposite ways: at 1 m/s the glass goes
  over the edge, at 3 m/s it moves 1.58 cm, 3.9 % of the way to the edge
- for the description (same cloth, other pull speeds): 1.1 m/s: the
  cloth is clear in 467.9 ms with the glass at 0.918 m/s after 21.47 cm,
  it slides 10.74 cm more and stops after 32.21 cm at 702 ms, 7.8 cm
  short of the edge (closed form 32.21 cm, diff 9.2e-12 cm); 2 m/s: the
  cloth is clear in 163.0 ms with the glass at 0.320 m/s after 2.61 cm,
  it slides 1.30 cm more and stops after 3.91 cm at 245 ms, 36.1 cm
  short of the edge (closed form 3.91 cm); 4 m/s: the cloth is clear in
  76.4 ms with the glass at 0.150 m/s after 0.57 cm, it slides 0.29 cm
  more and stops after 0.86 cm at 115 ms, 39.1 cm short of the edge
  (closed form 0.86 cm)
- schedule printed by the sim (first manifest, first_cycle_at -4.2 s,
  payoff_t 29.0, title_until 2.6; to be reset from the voice timing):
  cycles of 8.4 s start at -4.20, 4.20, 12.60, 21.00, 29.40, 37.80 s;
  the yank 0.6 s into each cycle; the fast cloth is clear 0.83 s after
  the yank and the fast glass stops 1.24 s after it; the slow glass
  reaches cloth speed 4.08 s after the yank and goes over the edge 5.24
  s after it, then falls (a 0.29 m drop to the bottom of its panel,
  0.242 s real, 1.94 s of video); the cloth's far edge leaves the table
  2.47 s (fast) and 6.20 s (slow) after the cycle start and leaves the
  frame at 3.11 s (fast) and 8.12 s (slow); each cycle crossfades to the
  resting setup over its last 0.8 s (out 7.60 to 8.00 s, in 8.00 to 8.40
  s); the scene is periodic, 42 s holds exactly 5 cycles
- text widths (DejaVuSans-Bold): overlay 929 px at 34; title lines 605
  and 754 px at 56 ("how fast must you pull?"; the brief's "how fast do
  you need to pull?" measures 935 px and the word "do" fails the round
  trip, see the hook pre-tests); legend 774 px at 40; clock 333 and 349
  px at 28; panel labels 336 px at 40; fixed lines 812 and 658 px at 28;
  state words 220 to 389 px, readout 343 px at 40, speed 227 px, marks
  76 and 78 px at 28; card lines 431, 539, 768, 820 and 553 px at 40;
  nothing over 950 px; the sim asserts every line under 950 px and that
  the label/readout and state/speed rows do not collide (label ends at
  x 436, readout starts at 637; state ends at 489 at most, speed starts
  at 753)

Narration numbers: one meter a second and three meters a second (the
two pull speeds, the setup; "30 cm of cloth" goes to the overlay), one
point one meters a second (the payoff; the threshold sqrt(2 mu g L) =
1.0848 m/s) with the two outcomes: at one meter a second the glass rides
off the table (its centre passes the edge at 0.6549 s by RK4), at three
it moves one point six centimeters (1.576 cm by RK4, 1.051 on the cloth
plus 0.525 on the table). The 25.49 cm, the 103.5 ms, the 0.655 s and
the 1.58 cm go to the fixed lines under the panel labels and the
description; the 0.86 cm, 3.91 cm and 32.21 cm to the description. The
numbers match the brief; the fast-pull distance is narrated as "one
point six centimeters" (1.576 rounds to 1.6) rather than the brief's
"one and a half" (whisper writes "one and a half" as the digits 1.5,
which the normaliser cannot match, and 1.5 is the looser rounding).

### Production

- layout (`sims/tablecloth/tablecloth.py`): overlay "30 cm of cloth | mu
  0.2 cloth, 0.4 table | no seed" at y 96 (drawn by compose from the
  manifest), title "Pull the tablecloth: / how fast must you pull?" at y
  190/252 (56 px) for the first 3 s (fading over its last 0.4 s), then
  the legend "same cloth, same glass, 1/8 speed" at y 236 (40 px) and the
  shared clock "N.NNN s after the pull" / "at rest before the pull" at y
  290 (28 px, muted); two stacked side-view panels on the same clock,
  bands y 340 to 880 and 880 to 1420, each drawn at 2x in its own layer
  and reduced (so the falling glass is clipped at its panel's bottom); in
  each panel the label "pulled at 1 m/s" / "pulled at 3 m/s" at band top
  + 40 (40 px, left at x 100) with the live readout "moved N.N cm" on the
  same row (right at x 980, gold once the glass has left the cloth), the
  state words at + 84 (28 px: "at rest on the cloth", "sliding on the
  cloth", "riding with the cloth", "over the edge", "sliding on the bare
  table", "stopped on the table"; gold off the cloth) with "glass N.NN
  m/s" right-aligned, the fixed line at + 120 (28 px, gold, up with the
  HUD): "cloth speed after 25.5 cm; over the edge at 0.655 s" / "cloth
  clear in 104 ms; stops after 1.58 cm"; the table slab 40 px thick at
  band top + 350 (y 690 / 1230) from x 40 to the edge at x 840 with two
  legs, at 1000 px per metre (the glass starts at x 440, the cloth's far
  edge at x 140, 30 cm to its left, the table edge 40 cm to its right);
  the cloth an 8 px band of alternating 5 cm red and cream blocks from
  its far edge to the right frame edge with a white far-edge line; a
  coral pull arrow at the right from the yank; a gold start triangle
  under the slab and a gold travel bar from the start to the glass;
  "start" and "edge" labels 22 px under the slab; the glass a tapered 70
  by 90 px tumbler with water, standing on the cloth (8 px up) or on the
  bare table, and after the edge a projectile fall with a 5 rad/s spin;
  captions at caption_y 0.75 (y 1440 to 1520); the five-line card from y
  1580 (40 px, 52 px pitch, gold) from 22.9 s with a 0.6 s fade; each
  cycle crossfades to the resting setup over its last 0.8 s (out 7.6 to
  8.0, in 8.0 to 8.4 s after the cycle start); the HUD (legend, clock,
  fixed lines, card) fades out over the first 0.25 s of the last 0.5 s
  and the title fades in over the second 0.25 s; the cycle phase is an
  integer frame count modulo the 504-frame cycle so the periodicity is
  exact, and the last frame is drawn as frame 0
- whisper pre-tests (10:39:54 to 10:40:11 and 10:44:59 to 10:45:06
  EEST, `media/tablecloth/hooks/`, logs `hooks/pretest.log` and
  `hooks/onsets.log` at 10:45:17): nine hook variants, each "<opener>.
  <question> Same cloth, same glass, two speeds.", question onset from
  silencedetect (-35 dB, 0.08 s) plus the 0.6 s offset: hook1 "Pull the
  tablecloth. How fast do you need to pull?" pass, 2.06 s; hook2 "Yank
  the tablecloth. How fast do you need to pull?" fail ("do" dropped);
  hook3 "The tablecloth trick. How fast do you need to pull?" fail ("do"
  dropped); hook4 "Yank the tablecloth. How fast do you need to yank?"
  pass, 1.99 s; hook5 "Pull the table cloth. How fast do you need to
  pull?" fail ("table cloth" heard as "tablecloth" and "do" dropped);
  hook6 "Pull the tablecloth. How fast should you pull?" pass, 1.96 s;
  hook7 "Yank the tablecloth. How fast should you pull?" pass, 2.01 s;
  hook8 "Pull the tablecloth. How fast must you pull?" pass, 1.86 s;
  hook9 (hook1's text again) pass, 2.00 s; the brief's "how fast do you
  need to pull" loses "do" in 3 of 5 takes, so hook8 kept: the earliest
  onset, passes, and "must you pull" is also the card and title wording
- narration (`projects/tablecloth/narration.txt`): 107 words, 13
  sentences; the numbers in words: "one meter a second", "three meters a
  second", "one point one meters a second", "one meter a second",
  "three", "one point six centimeters"; American "meter" and
  "centimeters"; "tablecloth" one word; no "still", "spread",
  "straight", "a hundred", "metres", "brakes", "drifts", "let's",
  "onto", "for ever" or sentence-initial "Below" / "Where" (the
  whisper mishearing list; "pull" is on the list but passed in every
  take here); the payoff sentence worded "You must pull faster than one
  point one meters a second, with this cloth." so the chunker keeps
  "than one point one" on one caption
- smoke frames (`--frames`, one pass at 10:52 EEST on the final cycle:
  0, 1.0, 2.0, 4.5, 5.5, 6.6, 7.3, 12.6, 13.7, 17.3, 18.2, 23.6, 30.5,
  33.9, 41.6, 41.98 s) all clean: the title rows at 190/252 clear of the
  panel labels at 380; nothing in the caption band 1440 to 1530 (the
  card starts at 1580, its last line ends at about 1808); the falling
  glass clipped at the panel bottom at 6.6 and 7.3 s; the crossfade
  dimming the readouts at 41.6 s; smoke 41.98 equals smoke 0.0 (0 px)
- voice (`scripts/voiceover.sh tablecloth`, log
  `media/tablecloth/voice.log`): pass 1 at 10:50:36 to 10:50:39 EEST
  passed, "ok: transcript matches narration (33.935964s)"; voice.wav
  33.94 s, ends at 34.54 s of video with the 0.6 s offset
- timing (`scripts/voice-timing.py media/tablecloth/voice.wav`, log
  `media/tablecloth/timing.log`, video time): "Pull the tablecloth. How
  fast must you pull? Same cloth." 0.60 to 4.01, "Same glass. Two
  speeds. On top." 4.01 to 6.46, "Pulled at one meter a second, the
  cloth drags the glass." 6.46 to 9.99, "It speeds up, catches the
  cloth, and rides with it." 9.99 to 13.29, "Over the edge. On the
  bottom." 13.29 to 15.12, "Pulled at 3 meters a second. The cloth is
  gone before the glass gets going. It slides a little on the bare
  table." 15.12 to 21.19, "and stops." 21.19 to 22.11, "So, how fast
  must you pull? You must pull faster than 1.1 meters a second." 22.11
  to 27.30, "With this cloth." 27.30 to 28.20, "At one meter a second,"
  28.20 to 29.68, "the glass rides off the table. At 3, it moves 1.6
  centimeters." 29.68 to 34.54; silencedetect on the full take
  (`media/tablecloth/pauses.log`, video time): pause 1.62 to 1.80 after
  "tablecloth.", so "How" sounds at 1.80 s; 3.01 to 3.12 after "pull?";
  10.94 to 11.10 after "It speeds up,"; 12.18 to 12.33 after "catches
  the cloth,"; 13.14 to 13.44 after "rides with it," so "over the edge"
  sounds 13.44 to 14.11; 15.00 to 15.24 after "On the bottom,"; 16.68
  to 16.90 after "three meters a second." so "The cloth is gone before
  the glass gets going" sounds 16.90 to 19.15; "It slides a little on
  the bare table, and stops." 19.36 to 21.95; "So," 22.27 to 22.68 and
  "how fast must you pull?" 22.80 to 24.12; "You must pull faster than
  one point one meters a second," 24.27 to 27.10; "with this cloth."
  27.49 to 28.05; "At one meter a second," 28.35 to 29.46; "the glass
  rides off the table." 29.89 to 31.38; "At three," 31.56 to 32.09; "it
  moves one point six centimeters." 32.26 to 34.32
- schedule (manifest): 1/8 speed on an 8.4 s cycle (504 frames), the
  yank 0.6 s into the cycle and first_cycle_at -0.6, so the yanks fall
  at 0.0, 8.4, 16.8, 25.2 and 33.6 s and frame 0 is the yank instant
  (both glasses at rest at 0.0 cm with the pull arrows up, the
  thumbnail); the slow glass reaches cloth speed 4.08 s after each yank
  (12.48 s inside "and rides with it," 12.33 to 13.14) and passes the
  edge 5.24 s after it: 13.64 s inside "over the edge" (13.44 to 14.11)
  and 30.44 s inside "the glass rides off the table" (29.89 to 31.38);
  the fast cloth is clear 0.83 s after each yank and the fast glass
  stops 1.24 s after it: 17.63 and 18.04 s inside "The cloth is gone
  before the glass gets going" (16.90 to 19.15), so "It slides a little
  on the bare table, and stops." (19.36 to 21.95) plays over the glass
  already at "stopped on the table" with its gold "moved 1.6 cm" (the
  slide on the bare table lasts 0.41 s of video); the second cycle's
  reset fade (15.4 to 16.2 s) sits under "pulled at three meters a
  second" (15.24 to 16.68) and the third yank at 16.8 s comes 0.1 s
  before "The cloth is gone"; the fourth yank at 25.2 s under "You must
  pull faster than"; the fifth yank at 33.6 s under "one point six
  centimeters", its fast glass clear at 34.43 s and stopped at 34.84 s,
  0.3 s after the voice ends, so the card's "at 3 m/s it moves 1.6 cm"
  (lit from 23.5 s) and the fourth cycle's gold "moved 1.6 cm" readout
  (26.44 to 32.2 s) carry the number; title_until 3.0 (the caption
  "pull?" runs to 3.14 s); payoff_t 22.9 with a 0.6 s fade, so the card
  is fully lit at 23.5 s, inside the spoken question (22.80 to 24.12)
  and before the numbers
- footage (`nix develop -c python3 sims/tablecloth/tablecloth.py`, log
  `media/tablecloth/render.log`): one render 10:53:26 to 10:54:28 EEST:
  loop check 0 px (max channel difference 0), periodicity check 0 px
  (the scene drawn live at 42 s against 0 s), loop step 6,162 px; 2,520
  frames, eight forked workers, h264 crf 16 yuv420p 60 fps, footage.mp4
  3,434,230 bytes, 42.00 s; `--measure-only` re-run into
  `media/tablecloth/measure.log` at 10:54:28 EEST with the final
  manifest and sim (no change since)
- compose (`scripts/compose.sh tablecloth`, log
  `media/tablecloth/compose.log`): one run 10:54:58 to 10:55:14 EEST:
  music seed 91 at 42.00 s (gain 0.18), 34 caption chunks (longest 20
  characters; "than one point one" and "one point six" each one chunk),
  final.mp4 3,910,060 bytes 42.000000 s, preview.mp4 540x960 30 fps
  1,129,427 bytes 42.066667 s, sheet.png 8x6 at 1 fps 645,009 bytes
- text widths (measure.log, PIL at the drawn sizes): overlay 929 px,
  title lines 605 and 754 px, legend 774 px, clock 333 and 349 px, panel
  labels 336 px, fixed lines 812 and 658 px, state words 220 to 389 px,
  readout 343 px, speed 227 px, marks 76 and 78 px, card lines 431,
  539, 768, 820 and 553 px, all under 950 px; the label/readout and
  state/speed rows do not collide (label to x 436, readout from 637;
  state to 489, speed from 753); the overlay candidates with "mu"
  spelled out or the glass size measured 1000 to 1240 px and were
  dropped before any render; the brief's question "how fast do you need
  to pull?" measures 935 px on one 56 px line (would have fitted)

### Local QA

- frames (`media/tablecloth/frame-<t>.png` from final.mp4 at 0.02, 2.0,
  9.0, 13.7, 17.3, 23.6, 30.5, 33.9 and 41.98 s, plus `sheet.png`)
  inspected at 11:00 EEST: 0.02 s: overlay and the two-line title from
  frame 0, both glasses at rest on the patterned cloth over the gold
  start mark, "pulled at 1 m/s" / "pulled at 3 m/s", "moved 0.0 cm",
  "sliding on the cloth" at "glass 0.01 m/s" (the frame after the yank),
  the coral pull arrows at the right, the cloth pattern to the frame
  edge, the table slab with its legs and the "start" and "edge" labels
  (the thumbnail); 2.0 s: caption "How fast must you" in the band under
  the panels, the title still up, the top glass sliding at "moved 6.1
  cm" and "glass 0.49 m/s" with the gold travel bar, the bottom glass
  "stopped on the table" at gold "moved 1.6 cm" and "glass 0.00 m/s"
  with its cloth already past the edge; 9.0 s: caption "glass.", the
  legend and the clock "0.075 s after the pull" in place of the title,
  both glasses sliding on the cloth at "moved 0.6 cm" and "glass 0.15
  m/s" (the two runs are identical until the fast cloth clears), the
  fixed lines lit under the labels; 13.7 s: caption "On the bottom,"
  (the proportional caption runs about 0.9 s ahead of the voice here;
  "over the edge" sounds 13.44 to 14.11), clock "0.663 s after the
  pull", the top glass "over the edge" at gold "moved 40.0 cm" and
  "glass 1.00 m/s" with its centre just past the edge on the last 4.5 cm
  of cloth and the travel bar from the start to the edge, the bottom
  glass stopped at 1.6 cm; 17.3 s: caption "The cloth is gone", clock
  "0.063 s after the pull", both glasses at "moved 0.4 cm" and "glass
  0.12 m/s" sliding on the cloth, the top cloth's far edge 6 cm and the
  bottom one's 19 cm along; 23.6 s: caption "you pull?", the card "pull
  the tablecloth: / how fast must you pull? / faster than 1.1 m/s with
  this cloth / at 1 m/s the glass rides off the table / at 3 m/s it
  moves 1.6 cm" lit under it, clock "0.850 s after the pull", the top
  glass falling and turning below the table edge (clipped at its panel's
  bottom) at "over the edge" and "moved 40.0 cm" with its cloth almost
  out of frame, the bottom glass stopped at 1.6 cm; 30.5 s: caption
  "second, the glass", clock "0.663 s after the pull", the top glass at
  the edge at "over the edge" and "moved 40.0 cm", the card lit, the
  bottom glass stopped at 1.6 cm; 33.9 s: caption "one point six",
  clock "0.038 s after the pull", both glasses at "moved 0.1 cm" and
  "glass 0.07 m/s", the card's "at 3 m/s it moves 1.6 cm" lit; 41.98
  s: the title back and the HUD gone, both glasses at rest at "moved
  0.0 cm" and "glass 0.00 m/s", matches frame 0; the contact sheet
  shows the captions in narration order, the five pulls with the slow
  glass falling at 6, 14, 23, 31 and 39 to 40 s, the reset crossfades
  at 8, 16, 25, 33 and 41 s and the card from 23 s to 41 s
- question inside two seconds: the title carries the question from
  frame 0; the narration reaches "How fast must you pull?" after three
  words; the word "How" sounds at 1.80 s of video (pause 1.62 to 1.80 s
  on the full take; hook8 pre-test 1.86 s); the caption "Pull the
  tablecloth." shows 0.60 to 1.55 s, "How fast must you" 1.55 to 2.82 s
  and "pull?" 2.82 to 3.14 s
- captions: the 34 chunks read back from
  `media/tablecloth/captions.filter` match the 107 narration words
  exactly, in order; longest chunk 20 characters; "than one point one"
  (18) is one chunk 25.34 to 26.61 s and "one point six" (13) one chunk
  33.27 to 34.22 s; the proportional timing leads the voice by up to
  about 1 s around "over the edge." (caption 12.34 to 13.29, spoken
  13.44 to 14.11, because of the pause before the phrase) and is within
  0.3 s at the question and the payoff numbers
- payoff on screen when spoken: the card fades in 22.9 to 23.5 s and
  holds to the loop fade at 41.5 s; "faster than 1.1 m/s with this
  cloth" is lit while "one point one meters a second" sounds (24.27 to
  27.10) and "at 3 m/s it moves 1.6 cm" while "one point six
  centimeters" sounds (32.26 to 34.32; frame 33.9 inspected); "at 1 m/s
  the glass rides off the table" is lit while the top glass passes the
  edge at 30.44 s inside "the glass rides off the table" (29.89 to
  31.38; frame 30.5 inspected); the fixed lines "over the edge at 0.655
  s" and "stops after 1.58 cm" are up from 3.4 s
- clipping and bands: every one of the 2,520 footage frames scanned
  (numpy, more than 24 levels from the background): content columns 40
  to 1079 (the cloth band and the pull arrow run to the right frame
  edge by design) and rows 166 to 1805; the caption exclusion band rows
  1420 to 1530 never deviates more than 2 levels from the background (0
  frames over 8 levels); the lowest geometry row is the panel bottom at
  1420 (the falling glass is clipped there); the card starts at 1580
- loop: the raw last frame equals the first (0 px, max channel
  difference 0) and the live scene at 42 s equals 0 s (0 px); in the
  encoded final.mp4 frame 2519 against frame 0 differs in 23,833 px by
  more than 8 levels (max channel difference 68, mean 0.35 levels, 616
  px over 32 levels on the text and cloth edges), the same order as the
  day 28 springdrop final (27,332 px, max 109, mean 0.36), i.e. h264
  quantisation on the second-generation encode, not content; the loop
  step from frame 2518 to 2519 is 29,983 px
- ffprobe final.mp4: h264 1080x1920 yuv420p 60/1 fps, 2,520 frames,
  42.000000 s, 3,910,060 bytes, aac 22050 Hz mono, atoms ftyp, moov,
  free, mdat (moov before mdat); md5 7450f6082019b93429d61e47f5fe9e9a
- narrated numbers against measure.log: "one meter a second" and
  "three meters a second" are pull_speeds_m_s 1.0 and 3.0; "faster than
  one point one meters a second" is the threshold sqrt(2 mu g L) =
  1.0848 m/s at one decimal (the description gives 1.0848 and the 1.1
  m/s run that clears the cloth at 467.9 ms and stops 7.8 cm short of
  the edge); "the glass rides off the table" is the 1 m/s run reaching
  cloth speed at 0.5099 s after 25.49 cm with 4.51 cm of cloth still
  under it and its centre passing the edge at 0.6549 s; "one point six
  centimeters" is the 3 m/s run's 1.576 cm (1.051 cm on the cloth to
  103.5 ms, 0.525 cm on the table to 155.3 ms), shown as "moved 1.6 cm"
  on the readout and "stops after 1.58 cm" on the fixed line; the
  "30 cm of cloth" and "mu 0.2 cloth, 0.4 table" on the overlay are the
  manifest's cloth_under_glass_m 0.3, mu_cloth 0.2 and mu_table 0.4
- no defect left

### Metadata

- `projects/tablecloth/metadata.json`: title "Pull the tablecloth: how
  fast must you pull? Above 1.1 m/s: 1 m/s rides off, 3 m/s moves 1.6
  cm" (95 characters; the first draft with "Faster than 1.1 m/s" was 101
  and never written); description (3,611 characters) with the setup (a
  7 by 9 cm glass on 30 cm of cloth, 40 cm from the table edge, mu 0.2
  on the cloth and 0.4 on the table, a jerk to a steady pull speed, RK4
  at 10,000 steps per second with the friction switches located by
  bisection, 1/8 speed, five pulls in 42 s, no seed), a Measured list
  (the threshold 1.0848 m/s and its square-root scaling with the cloth
  length and friction; the 1 m/s run: cloth speed at 0.5099 s after
  25.49 cm, 4.51 cm of cloth left, over the edge at 0.6549 s; the 3 m/s
  run: clear at 103.5 ms at 0.2030 m/s after 1.051 cm, 0.525 cm more on
  the table, stopped at 155.3 ms after 1.576 cm, 38.4 cm short of the
  edge; 1.1, 2 and 4 m/s stopping after 32.21, 3.91 and 0.86 cm; the
  tipping check 7 / 9 = 0.778 above both mu; the RK4 check within 3e-14
  m of the closed form), a Why paragraph in plain words (friction on the
  cloth can only give the glass mu g of acceleration; a slow pull keeps
  the cloth under the glass long enough for the glass to catch up and
  ride with it; a fast pull gets the 30 cm out before the glass has
  moved far, and the rougher table stops it in a few millimetres), the
  rerun line and the AI-made line; 10 tags (tablecloth trick, tablecloth
  pull, how fast must you pull, friction, sliding friction, inertia,
  physics, physics visualization, simulation, shorts); category 27;
  private; containsSyntheticMedia true; selfDeclaredMadeForKids false;
  the same keys in the same order as projects/springdrop/metadata.json;
  no "<" or ">"
- not uploaded; task left open for the orchestrator's review and upload

### Niche note

[produced 2026-09-27 as "Pull the tablecloth: how fast must you pull?",
two stacked panels of the same 30 cm of cloth (mu 0.2) under the same 7
by 9 cm glass 40 cm from the table edge (mu 0.4 on the bare table),
pulled at 1 m/s and 3 m/s at 1/8 speed on an 8.4 s cycle, five pulls in
42 s: the threshold is sqrt(2 mu g L) = 1.0848 m/s and scales with the
square root of the cloth length and of the cloth friction (15 cm 0.767
m/s, 60 cm 1.534 m/s); at 1 m/s the glass reaches cloth speed at 0.5099
s after 25.49 cm with 4.51 cm of cloth still under it and rides over the
edge at 0.6549 s; at 3 m/s the cloth is clear in 103.5 ms with the glass
at 0.2030 m/s after 1.051 cm, it slides 0.525 cm more on the table and
stops at 155.3 ms after 1.576 cm, 38.4 cm short of the edge; 1.1 m/s
stops 7.8 cm short after 32.21 cm, 2 m/s after 3.91 cm, 4 m/s after 0.86
cm; the glass (7 / 9 = 0.778, above both mu) slides and never tips; RK4
at 10,000 steps a second within 3e-14 m of the closed form; whisper
drops "do" from "how fast do you need to pull" in 3 of 5 takes, so the
question is "how fast must you pull"; task 20260927-103224]

Deviations from the brief: the question is "How fast must you pull?"
(the brief's "how fast do you need to pull?" lost the word "do" in the
whisper round trip in 3 of 5 pre-test takes; "must" passed, is the
earliest onset at 1.86 s, and is the wording of the title, the card and
the payoff); the fast-pull distance is narrated as "one point six
centimeters" (1.576 cm rounds to 1.6) rather than the brief's "one and
a half" (whisper writes "one and a half" as the digits 1.5, which the
normaliser cannot match, and 1.5 is the looser rounding); the run is
shown at 1/8 speed on an 8.4 s cycle with five pulls in 42 s so each
pull spans its narration and the slow edge crossings land on "over the
edge" and "the glass rides off the table"; the 25.5 cm, 104 ms, 0.655 s
and 1.58 cm are also shown as fixed lines under the panel labels and go
to the description; the card shows 1.1 m/s and 1.6 cm at the
narration's precision while the readouts show one decimal and the fixed
line 1.58 cm; the fifth pull's fast glass stops 0.3 s after the voice
ends, the card carrying the number. The claim and every narrated number
stand as briefed.

## Upload

- orchestrator review (2026-09-27T11:13:26+03:00): task evidence, sheet.png and frames at 0.02,
  13.7, 23.6 and 33.9 s inspected; numbers match measure.log and the
  orchestrator's closed forms; approved for upload
- upload attempt 3 of 5 for the quota day that began 2026-09-27T10:00
  EEST, recorded at 2026-09-27T11:13:26+03:00 before starting scripts/yt-upload.py; two attempts
  (cutshot aEgJbsPwqeo, coinroll myMUuK-p_L8) were on record since the
  boundary
- uploaded private as -ry3tM_rZ98 at 11:13:32 EEST (media/tablecloth/upload.log);
  scripts/yt-qa.py --wait --publish: gate 15 of 15 (PT43S for the 42.000 s
  file), set public at 11:15:41 EEST and re-read public
  (media/tablecloth/publish.log); https://youtu.be/-ry3tM_rZ98
- attempt 3 of 5 complete at 2026-09-27T11:16:08+03:00: 1,653 units (1 channels read, 1,600
  insert, 52 gate, update and re-read); the id starts with a hyphen, so
  pass it bare to yt-qa.py (a `--` separator prints usage and exits 2
  before any API call)
- slot resolution: published for the 2026-09-27 quota day at 11:15:41 EEST,
  https://youtu.be/-ry3tM_rZ98

### Quota
- attempt 3 of the hard cap of 5 for the quota day that began
  2026-09-27T10:00 EEST; cost 1 + 1,600 + 52 = 1,653 units (the
  channels.list verification inside yt-upload.py, the insert, the gate
  run's single read, update and re-read as printed by yt-qa.py); day total
  after three attempts 1,655 + 1,655 + 1,653 = 4,963 units plus 5 for the
  10:02 stats refresh and 5 for the 11:17 refresh, target of three met
