# Produce short: Superball under a table, a rough ball beside a smooth ball on the same throw

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day26

## Goal

Backlog idea (trend research 2026-09-23, task 20260923-101345, pillar 2
chaos and physics, collisions; read the full entry under "Added by trend
research 2026-09-23" in docs/niche.md):
"Superball under a table: a rough bouncy ball beside a smooth ball, both
thrown from 40 cm at 2.5 m/s forward and 2.5 m/s down under a 70 cm
table; measure where the third bounce lands; expect the rough ball back
0.68 m behind the throw after floor, table, floor (Garwin's
rough-elastic map: the contact-point velocity reverses, angular
momentum about the contact point kept, alpha 2/5) and the smooth ball
1.7 m ahead at 2.5 m/s; deterministic, no seed."
Research feasibility numbers (task 20260923-101345, Garwin map, alpha
2/5, R 3 cm): floor at x 0.300 m, table underside at 0.594 m, third
bounce at 0.670 s; the smooth ball keeps 2.50 m/s and is at x 1.675 m
at its third bounce.
Orchestrator check (2026-09-24, before this brief): the research's
speeds after the second and third bounces (-4.64 and -1.99 m/s) do not
conserve energy and look like contact-point speeds. Deriving the map
from the two rules (the contact-point velocity along the surface
reverses; angular momentum about the contact point is conserved; the
normal velocity reverses) with I = alpha m R^2, alpha 2/5, x forward, y
up, omega counterclockwise: on the floor (contact below the centre, u =
vx + R omega) vx' = (3 vx - 4 R omega) / 7 and R omega' = (-10 vx - 3 R
omega) / 7; on the underside of the table (contact above, u = vx - R
omega) vx' = (3 vx + 4 R omega) / 7 and R omega' = (10 vx - 3 R omega)
/ 7. From vx 2.5 and no spin: floor vx 1.0714, R omega -3.5714; table
vx -1.5816, R omega 3.0612; floor vx -2.4271, R omega 0.9475; the
kinetic plus spin energy is 3.125 J/kg through every bounce, and the
product of the three maps is (1/343) [[-333, 52], [130, 333]], so the
ball comes back at 333/343 = 97.1 percent of the throw speed with
little spin, Garwin's result. Flight (g 9.80665, centre from 0.40 m,
2.5 m/s down): floor at 0.300 m and 0.120 s, the table underside
(centre at 0.67 m) at 0.594 m and 0.395 s, the floor again at 0.159 m
and 0.670 s, then back up through the release height 0.4 m at about
x -0.13 m and 0.79 s, moving backward at 2.43 m/s: the ball returns to
the hand. The sim must derive and print all of this itself; the
narration uses only the sim's numbers.
Day twenty-six, second slot. Chosen because it is a two-panel collision
on the same throw (same start, same speed, same table; only the ball's
grip differs), a real audience demo with a visible surprise (the ball
comes back to the thrower), continuous motion and a plain question, the
format of the channel's best shorts (Newton's cradle 958, pi collisions
943, Galilean cannon 385 aside). Question in the first two seconds:
"Throw a bouncy ball under a table. Where does it end up?" (or the
producer's better wording, kept identical in the title, the hook and
the payoff). Payoff: it comes back to your hand (the sim's numbers:
where it is at the release height on the way back, its speed as a share
of the throw speed); the smooth ball flies out the far side.
Model: a rough perfectly elastic ball (Garwin 1969; alpha 2/5, a solid
rubber ball; no air) beside a smooth perfectly elastic ball (no
friction, no spin change, vx kept); both released at the same point
with the same velocity, under a table whose underside spans the bounce
points; flights are exact parabolas with the bounce instants solved
exactly (event driven), an RK4 check optional. Draw a spoke or pattern
on the balls and a spin readout so the spin is visible; draw the
contact-point velocity arrow at each bounce if it reads. Print every
bounce (time, x, vx, vy, R omega before and after), the energy after
each bounce, the position and speed at the release height on the way
back, the smooth ball's third-bounce position and its exit, and text
widths. Shown slowed (about one fifth speed) so the three bounces read;
the throw repeats so the last frame equals the first. Music seed 81.

## Claim

A bouncy ball thrown down under a table at two and a half meters a
second, forward and down, bounces off the floor, off the underside of
the table, off the floor again, and comes back to the hand that threw
it, at about ninety seven percent of its speed; a smooth ball with the
same throw flies out the far side. Every number in the narration is
printed by the sim before the script is written.

## Evidence

### Measurements

(recorded after the measure-only run, before scripting)

`sims/superball/superball.py --measure-only` with
`projects/superball/manifest.json` (two balls of radius 3 cm released
at the same point, centre 0.4 m above the floor, x = 0 at the hand,
with the same velocity, 2.5 m/s forward and 2.5 m/s down (3.5355 m/s),
under a table whose underside is 0.7 m above the floor, a 4 cm slab
spanning x = -0.5 to 1.5 m; the top ball rough and perfectly elastic
(Garwin: the normal velocity reverses, the contact-point velocity along
the surface reverses, the angular momentum about the contact point is
conserved, I = alpha m R^2, alpha 0.4, no air); the bottom ball smooth
and perfectly elastic (no spin change, vx kept); flights are exact
parabolas with the bounce instants solved as quadratic roots (event
driven, no time step); g = 9.80665; played at 1/6 speed, 5 throws of 8
s; drawn at 476 px per metre from x = -0.3 to 1.8 m; deterministic, no
seed; first run at about 10:25 EEST before scripting, re-run at
10:32:53 EEST after the overlay text change with identical numbers, log
in `media/superball/measure.log`):

- bounce map solved from the two rules as a 2 x 2 linear system (no
  hard-coded fractions): floor (contact below) vx' = 0.428571 vx -
  0.571429 R omega, R omega' = -1.428571 vx - 0.428571 R omega; table
  underside (contact above) vx' = 0.428571 vx + 0.571429 R omega, R
  omega' = 1.428571 vx - 0.428571 R omega; max difference from the
  closed-form fractions (3, -4; -10, -3) / 7 and (3, 4; 10, -3) / 7 is
  5.6e-17; the sim asserts vx^2 + alpha (R omega)^2 conserved at every
  bounce
- rough ball, bounce 1 (floor) at t = 0.1198 s, x = 0.2996 m (residual
  6.9e-17 m): vx 2.5000 -> 1.0714 m/s, vy -3.6752 -> 3.6752 m/s, R
  omega 0 -> -3.5714 m/s (18.95 turns/s, top spin), contact-point
  speed along the surface 2.5000 -> -2.5000 m/s
- bounce 2 (table underside) at t = 0.3950 s, x = 0.5944 m (residual
  0): vx 1.0714 -> -1.5816 m/s (backward), vy 0.9769 -> -0.9769 m/s, R
  omega -3.5714 -> 3.0612 m/s (16.24 turns/s, reversed), contact-point
  speed 4.6429 -> -4.6429 m/s
- bounce 3 (floor) at t = 0.6701 s, x = 0.1592 m (residual 8.3e-17 m):
  vx -1.5816 -> -2.4271 m/s, vy -3.6752 -> 3.6752 m/s, R omega 3.0612
  -> 0.9475 m/s (5.03 turns/s), contact-point speed 1.4796 -> -1.4796
  m/s
- energy: horizontal plus spin (vx^2 + alpha (R omega)^2) / 2 = 3.1250
  J/kg at the throw and after every bounce, max deviation 4.4e-16;
  total 10.1727 J/kg, max deviation 0
- product of the three maps (floor, table, floor) on (vx, R omega):
  [[-0.970845, 0.151603], [0.379009, 0.970845]] = (1/343) [[-333, 52],
  [130, 333]]; applied to the throw (2.5, 0) it gives vx -2.4271 and R
  omega 0.9475, the state after bounce 3; |vx| share 97.08 percent
  (Garwin's 333/343)
- return: the rough ball rises back through the release height 0.4 m
  at t = 0.7900 s, x = -0.1316 m (13.2 cm behind the hand), moving
  backward at 2.4271 m/s and up at 2.5000 m/s, full speed 3.4844 m/s;
  backward speed 97.08 percent of the 2.5 m/s forward throw speed, full
  speed 98.55 percent of the 3.5355 m/s throw speed; spin at the catch
  5.03 turns/s; the run ends by catch there (asserted, with the bounce
  kinds floor, table, floor)
- without the catch the rough ball would reach the table underside
  height at t = 0.9453 s, x = -0.5086 m, behind the near edge at -0.5
  m (apex 0.7187 m); the catch at 0.7900 s comes first
- smooth ball: vx 2.5000 m/s through every bounce; floor at 0.2996 m
  (0.1198 s), table at 0.9874 m (0.3950 s), floor at 1.6753 m (0.6701
  s), 0.1753 m beyond the far edge of the table; passes under the far
  edge (x 1.5 m) at t = 0.6000 s at a centre height of 0.2636 m; leaves
  the frame (x 1.9145 m) at t = 0.7658 s at a height of 0.3367 m, speed
  3.7070 m/s (the run ends by exit); energies 3.1250 and 10.1727 J/kg,
  deviation 0
- table length kept at -0.5 to 1.5 m from the brief: the rough bounces
  (0.2996, 0.5944, 0.1592 m) and the smooth table bounce (0.9874 m)
  are under it, the smooth third bounce (1.6753 m) is beyond the far
  edge, and the rough ball's would-be next table crossing (-0.5086 m)
  is behind the near edge and after the catch
- agreement with the orchestrator's derivation in the Goal: floor 0.300
  m, 1.0714, -3.5714; table 0.594 m, -1.5816, 3.0612; floor 0.159 m,
  -2.4271, 0.9475; return at x -0.13 m and 0.79 s at 2.43 m/s; product
  (1/343) [[-333, 52], [130, 333]]: all reproduced by the sim; the
  research's -4.64 and -1.99 m/s are contact-point speeds (the sim
  prints 4.6429 and 1.4796 m/s before the second and third bounces)
- schedule printed by the sim (video time, 1/6 speed): each 8 s throw
  releases both balls at 0 s; the rough ball bounces 0.72, 2.37 and
  4.02 s after the release, the hand reaches from 4.24 s and catches
  at 4.74 s; the smooth ball bounces at the same instants and leaves
  the frame 4.59 s after the release; held 2.26 s, then a 0.5 s reset
  to the hand and 0.5 s at rest; catches at 4.74, 12.74, 20.74, 28.74,
  36.74 s; exits at 4.59, 12.59, 20.59, 28.59, 36.59 s; title until 2.4
  s; payoff card from 27 s; loop fade 39.5 to 40 s
- text widths (DejaVuSans-Bold, asserted under 950 px): overlay 907 px
  at 34 (the first draft overlay was 1,144 px and aborted the measure
  run before any render; two shorter drafts at 1,031 and 961 px were
  also rejected); title lines 637, 445 and 659 px at 56; counter 274
  px at 40; model tag 647 px at 28; panel labels 316 and 357 px at 32;
  clock 169 px at 40; "caught" 124 and "gone" 89 px at 32; readouts
  147, 239 and 266 px at 28, the row 730 px; "hand" 68, "table" 69,
  "floor" 63 and the bounce numbers 17 px at 24; catch tag lines 267
  and 213 px and the exit tag 244 px at 28; payoff lines 779, 904, 773
  and 825 px at 40

Narration numbers: the setup number is "seventy centimeters" (the
height of the table underside; the 2.5 m/s throw stays on the overlay
and the speed readouts); the payoff number is "ninety seven percent of
its forward speed" (the measured 97.08 percent, "97 percent" on the
card). The 13 cm, the 0.79 s, the full-speed share 98.55 percent, the
spins, the product matrix and the smooth ball's positions go to the
description and the on-screen readouts. The claim's "about ninety seven
percent of its speed" holds for the forward speed (97.08 percent); the
full speed comes back at 98.55 percent, so the narration says "of its
forward speed". No number contradicted the claim; the claim text is
left as written.

### Production

- layout (`sims/superball/superball.py`): overlay "2.5 m/s | rough vs
  smooth | 1/6 speed | no seed" at y 96; the title "Throw a bouncy
  ball / under a table. / So where does it go?" at y 190/252/314 for
  the first 2.4 s, then the counter "throw k of 5" at y 236 and the
  model tag "solid rubber ball, perfect bounces, no air" at y 290; two
  panels stacked in the y 360 to 1400 geometry band, the rough ball
  (gold) with the label "rough ball (grips)" at y 400 and its floor at
  y 830, the smooth ball (teal) with "smooth ball (slides)" at y 935
  and its floor at y 1365; each panel at 476 px per metre from x -0.3
  to 1.8 m: a floor line over a ground band, the 4 cm slab with its
  edges and dim legs at x -0.5 and 1.5 m, "hand", "table" and "floor"
  labels at 24 px (the table label at the left end of the slab), the
  ball a 14.3 px disc with a two-tone half pattern that turns with the
  integrated spin, a rim and a highlight, the hand a rounded palm
  behind the ball with a thumb tab; a persistent path with a brighter
  0.3 s trail, a ring and a 0.4 s flash at each bounce with the bounce
  number under the floor or the underside; a readout row at 28 px ("x
  0.31 m", "speed 3.78 m/s", "spin 18.9 turns/s") with the clock "t
  0.72 s" at 40 px, frozen at the end in the panel colour with a
  "caught" or "gone" tag; the catch tag "back at the hand / 13 cm
  behind" above the hand and "out the far side" at the right edge;
  each 8 s throw releases both balls on its first frame, holds 2.26 s
  after the catch, resets over 0.5 s (the rough ball and the hand
  slide back, the smooth ball fades in at the hand, paths and marks
  fade) and rests 0.5 s so the loop fade plays over balls at rest;
  captions at caption_y 0.75; the four-line card from y 1592; geometry
  drawn at 2x and reduced; eight forked workers at most
- whisper pre-test (10:26:09 to 10:26:18 and 10:29:54 to 10:30:00
  EEST, before the full take; `media/superball/hooks/`): six hook
  variants, the mechanism group and the payoff group round-tripped
  through `scripts/voiceover.sh`, all passed on the first pass: h1
  "Throw a bouncy ball under a table. So where does it go? The
  underside is seventy centimeters above the floor." (6.41 s), h2 "A
  bouncy ball, thrown under a table. ..." (6.41 s), h3 "... So where
  does it end up? ..." (6.21 s), h4 "A bouncy ball under a table. ..."
  (5.87 s, "So" at 1.66 s of voice), h5 "Bouncy ball under a table.
  ..." (5.74 s, 1.61 s), h6 "Throw a ball under a table. ..." (5.98 s,
  1.54 s); the mechanism group "The top ball is rough. It grips. On
  the floor, it slows and spins fast. At the table, the spin flips it
  back. On the floor again, the spin turns into speed." (9.37 s); the
  payoff group "Throw after throw, the same three bounces. So where
  does it go? Back to your hand. It comes back at ninety seven percent
  of its forward speed." (8.10 s; the number came back as 97%)
- smoke frames (`--frames`, pass 1 at 10:26:38 EEST at 0, 1.5, 4.0,
  4.6, 4.75, 6.0, 7.25, 7.8, 26.5 and 39.9 s): three defects: the
  "table" label centred on the slab (x 1.05 m) collided with the
  smooth ball's "2" bounce mark at 0.987 m (fix: the label at the left
  end of the slab, x -0.28 m); the one-line catch tag "back at the
  hand, 13 cm behind" was crossed by the descending path from bounce
  2 (fix: two lines above the hand at x -0.19 m, y 0.60 and 0.528 m,
  where the paths stay right of x 0.45 m); "out the far side" was
  crossed by the smooth ball's path (fix: raised to y 0.56 m at the
  right edge); pass 2 at 10:29:25 EEST (2.5 and 4.75 s) clean: the
  throw-1 catch frame with both tags clear of the paths, nothing
  clipping, nothing in the caption band
- narration (written after the measure-only run, 10:25 to 10:31 EEST;
  `projects/superball/narration.txt`, 102 words): the balls named by
  their panels ("the top ball", "the bottom ball") and their labels
  ("rough", "smooth"); the setup number sits whole as "seventy
  centimeters" between "The underside is" and "above the floor."
  (chunks() check; "The table is seventy centimeters high" would split
  the number); the payoff "It comes back at | ninety seven percent | of
  its forward speed." checked the same way ("The rough ball comes |
  back at ninety" would split); the lead-in cut to "Throw a bouncy
  ball." so the question "So where does it go?" starts at 1.29 s of
  voice, 1.89 s of video (the seven-word lead-in "Throw a bouncy ball
  under a table." put it at 2.38 s of video in the second take; the
  h4, h5 and h6 lead-ins would still put it at 2.14 to 2.26 s); "under
  a table" moved into "Same throw for both, under a table."; "forward
  and down" moved to the description so the mechanism sentences track
  the throw-3 bounces; "the same path" added so the throw-4 catch
  lands on "It comes back at"; take 1 failed the round trip ("keeps its
  speed" heard as "heaps"), reworded to "holds its speed"; no sentence
  starts with "Spin", "Where", "Still" or "Through"; still, pull, got,
  spread, straight, brakes, drifts, dives, "a hundred", "and a half"
  and possessives avoided; American spelling; numbers as words
- voice: `scripts/voiceover.sh projects/superball/narration.txt`: take
  1 failed ("37c37 keeps / heaps"), take 2 passed (31.35 s) but put the
  question at 2.38 s of video, take 3 with the final text passed at
  10:31:55 EEST, "ok: transcript matches narration (31.219229s)": 102
  words, 31.22 s, ends at 31.82 s of the 40 s video, 3.27 words/s; log
  in `media/superball/voice.log`
- timing (`scripts/voice-timing.py`, +0.6 s offset,
  `media/superball/timing.log`: coarse pieces 0.60 to 14.51, 14.51 to
  19.97, 19.97 to 23.76, 23.76 to 25.17, 25.17 to 27.36 and 27.36 to
  31.82 s; sentence onsets from a finer silencedetect pass (d 0.08 s)
  in video time): "Throw a bouncy ball." 0.60 to 1.75; "So where does
  it go?" 1.89 to 3.12 (the question starts at 1.89 s, inside the
  first two seconds, under the title until 2.4 s); "Same throw for
  both," 3.32 to 4.44; "under a table." 4.62 to 5.28 with the throw-1
  catch at 4.74 s; "The underside is seventy centimeters above the
  floor." 5.44 to 8.11; "The bottom ball is smooth." 8.31 to 9.54 with
  throw 2 released at 8.0 s and its floor bounce at 8.72 s; "It
  slides," 9.70 to 10.35 with the table bounce at 10.37 s; "holds its
  speed," 10.56 to 11.46; "and flies out the far side." 11.62 to 13.09
  with the smooth ball's third bounce at 12.02 s and its exit at 12.59
  s; "The top ball is rough." 13.25 to 14.40 after the rough catch at
  12.74 s; "It grips." 14.63 to 15.27; "On the floor," 15.48 to 16.16
  with throw 3 released at 16.0 s; "it slows and spins fast." 16.27 to
  17.85 with the floor bounce at 16.72 s; "At the table," 18.04 to
  18.62 with the table bounce at 18.37 s; "the spin flips it back."
  18.72 to 19.84; "On the floor again," 20.09 to 21.00 with the floor
  bounce at 20.02 s; "the spin turns into speed." 21.15 to 22.55 with
  the catch at 20.74 s; "Throw after throw," 22.70 to 23.60; "the same
  three bounces," 23.91 to 25.05 with throw 4 released at 24.0 s and
  its floor bounce at 24.72 s; "the same path." 25.29 to 25.96; "So
  where does it go?" 26.11 to 27.22 with the table bounce at 26.37 s;
  "Back to your hand." 27.50 to 28.34 with the floor bounce at 28.02 s
  and the card lit from 27.6 s; "It comes back at ninety seven percent
  of its forward speed." 28.50 to 31.63 with the throw-4 catch at 28.74
  s on "It comes back at" (caption chunk 28.45 to 29.68) and the chunk
  "ninety seven percent" at 29.68 to 30.59 s; the voice ends at 31.82
  s; throw 5 (32 to 40 s) plays under the card
- schedule decisions: playback 1/6 instead of the brief's "about one
  fifth" so that the three throw-3 bounces (16.72, 18.37, 20.02 s) each
  fall inside the sentence naming them and the throw-4 catch (28.74 s)
  lands 0.4 s after "Back to your hand." on "It comes back at"; at 1/5
  speed the bounces would run ahead of the mechanism sentences;
  release_at 0 (both balls leave on the first frame, as in racingballs);
  payoff_t 27.0 s from the timing, so the card is fully lit at 27.6 s
  inside "Back to your hand." (27.50 to 28.34), 1.1 s before the catch
  and 2.1 s before the spoken "ninety seven percent" (29.68 s);
  payoff_hold 0.6 s
- footage: `sims/superball/superball.py` (no arguments) wrote
  `media/superball/footage.mp4`, 40.00 s at 60 fps, 2,400 frames, h264
  crf 16 yuv420p, in 59 s with eight forked workers, 10:32:53 to
  10:33:52 EEST; the same run re-printed every measurement above
  (`media/superball/render.log`, identical to measure.log); loop check
  on the raw frames: the last frame differs from the first in 0 px
  (max channel difference 0)
- compose: `scripts/compose.sh superball` wrote
  `media/superball/final.mp4` at 10:34:47 EEST (h264 1080x1920 60 fps,
  2,400 frames, aac 22050 Hz mono, 40.000 s, 3,639,936 bytes; music
  seed 81 at gain 0.18; captions at caption_y 0.75 (y 1440), 34
  drawtext filters, the overlay plus 33 caption chunks); loudness mean
  -15.9 dB, peak -0.0 dB; preview (40.07 s) and 8x5 contact sheet
  written (`media/superball/compose.log`)

### Local QA

- smoke pass 1 (10:26:38 EEST, `--frames` before any render): three
  defects found and fixed (the table label, the catch tag and the exit
  tag against the paths; see Production); smoke pass 2 (10:29:25 EEST)
  clean before the footage render
- final pass (10:35 EEST): frames at 0.02, 1.5, 2.4, 4.75, 8.75, 12.6,
  16.75, 18.4, 20.05, 27.6, 28.75, 30.0 and 39.95 s extracted from
  final.mp4 (`media/superball/frame-*.png`) and inspected with the 8x5
  contact sheet (`media/superball/sheet.png`): 0.02 s shows the overlay
  at y 96, the title "Throw a bouncy ball / under a table. / So where
  does it go?" clear of it, both panels with the slab, the legs and the
  "hand", "table" and "floor" labels, each ball leaving its hand at "x
  0.01 m", "t 0.01 s", "speed 3.57 m/s" and "spin 0.0 turns/s" (the
  thumbnail); 1.5 s shows both balls rising from the first floor bounce
  and its "1" mark at "t 0.25 s", the rough ball at "x 0.44 m", "speed
  2.63 m/s", "spin 18.9 turns/s" and the smooth ball ahead at "x 0.62
  m", "speed 3.46 m/s", "spin 0.0 turns/s", under "Throw a bouncy
  ball."; 2.4 s shows the title faded out at the crossover to "throw 1
  of 5" (the upper band empty for that frame) with both balls at their
  table bounce inside the bounce flash, the rough ball at "x 0.59 m",
  "speed 1.89 m/s", "spin 16.2 turns/s" and the smooth ball at "x 1.00
  m", "speed 2.70 m/s", under "So where does it go?"; 4.75 s shows the
  throw-1 catch: the rough ball in the hand, "caught t 0.79 s" in gold,
  "back at the hand / 13 cm behind" over the hand, and the smooth panel
  "gone t 0.77 s" in teal with "out the far side" at the right edge,
  under "under a table."; 8.75 s shows throw 2 at "t 0.12 s" with both
  balls on the floor at "x 0.31 m" inside their bounce flashes (rough
  "speed 3.78 m/s", "spin 18.9 turns/s"; smooth "speed 4.40 m/s") under
  "The bottom ball is"; 12.6 s shows throw 2 at "t 0.77 s", the rough
  ball at "x -0.08 m", "speed 3.65 m/s", "spin 5.0 turns/s" reaching the
  hand with its marks "1", "2", "3" on the path, and the smooth panel
  frozen at "gone t 0.77 s", "x 1.91 m" with "out the far side" and the
  path leaving at the right edge past its "3" mark beyond the table leg,
  under "the far side."; 16.75, 18.4 and 20.05 s show the throw-3
  bounces with the readouts x 0.31 m, speed 3.78 m/s, spin 18.9 turns/s
  under "slows and spins", x 0.59 m, speed 1.89 m/s, spin 16.2 turns/s
  under "At the table, the", and x 0.15 m, speed 4.36 m/s, spin 5.0
  turns/s under "On the floor again,"; 27.6 s shows the card fully lit
  under "Back to your hand." with the throw-4 rough ball at "t 0.60 s"
  falling from its "2" mark on the underside toward the third bounce ("x
  0.27 m", "speed 3.38 m/s", "spin 16.2 turns/s") and the smooth ball
  passing under the far edge at "x 1.50 m"; 28.75 s shows the throw-4
  catch under "It comes back at" with the card; 30.0 s shows "ninety
  seven percent" under the caught ball and the card naming 97 percent;
  39.95 s shows the crossfade to the title frame with the counter and
  the card fading; captions match the narration word for word (the
  contact sheet reads every chunk in order) and sit in the y 1440 to
  1520 band with the lowest geometry at y 1400 and the card from 1592;
  the widest text (the overlay, 907 px) is centred with 86 px margins
  and nothing clips at the frame edges; the payoff number is on screen
  when spoken (the card from 27.6 s against the chunk "ninety seven
  percent" 29.68 to 30.59 s); the loop closes: the raw last frame
  differs from the raw first frame in 0 px (render.log), and on the
  encoded final frame 2399 differs from frame 0 in 2,060 px by more than
  24 levels (0.10 percent, at text edges, max channel difference 70,
  mean 0.49, encoder noise); ffprobe: h264 1080x1920, 60/1 fps, 2,400
  frames (also by decode), aac 22050 Hz mono, 40.000000 s, atoms ftyp,
  moov, free, mdat (moov before mdat), md5
  8874cc39d0323e62f5828b29b501698f; approved locally

### Metadata

- `projects/superball/metadata.json`: title "Throw a bouncy ball under
  a table. So where does it go? Back to your hand, 97% of its forward
  speed" (99 characters; "at 97%" was 101 and cut); description with
  the setup (the 3 cm balls, the 40 cm release, 2.5 m/s forward and
  2.5 m/s down, the 70 cm underside and the 4 cm slab from -0.5 to 1.5
  m, Garwin's rules with I = 2/5 m R^2, the smooth ball, exact
  parabolas with event-driven bounces, the map solved as a 2 x 2
  system, 1/6 speed, five throws, no seed), a Measured list (the three
  rough bounces with positions, times, speeds and spins, the return at
  0.790 s 13 cm behind the hand at 2.43 m/s = 97.1 percent of the
  forward throw and 3.48 m/s = 98.6 percent of the full throw speed,
  the product matrix (1/343) [[-333, 52], [130, 333]], the energies
  3.125 and 10.173 J/kg with their deviations, the smooth ball's
  0.300, 0.987 and 1.675 m bounces, its passage under the far edge at
  26 cm and its exit at 0.766 s, the map fractions and their 6e-17
  difference), a Why paragraph in plain words (the rough ball cannot
  slide, so the floor turns most of its forward motion into spin; at
  the underside the contact point is on top, so the spin is thrown
  back into motion the other way and the ball leaves backward; the
  third bounce drains the spin into backward speed; every bounce keeps
  the energy and reverses the up-and-down motion, so the ball climbs
  back through the release height 13 cm behind the hand; the smooth
  ball has nothing to grab and keeps 2.5 m/s out the far side), the
  rerun line and the AI-made line; 10 tags (superball, bouncy ball,
  under a table, spin, elastic collision, angular momentum, physics,
  physics visualization, simulation, shorts); category 27; private;
  containsSyntheticMedia true; selfDeclaredMadeForKids false; the same
  keys in the same order as projects/racingballs/metadata.json
- not uploaded; task left open for the orchestrator's review and upload

- metadata fix (2026-09-24T10:49:49+03:00, orchestrator): the four " -> " arrows in the
  Measured list replaced by " to " after YouTube rejected the description
  (invalidDescription: < and > are not allowed); nothing else changed


### Release
- orchestrator review (10:48 EEST): the task evidence, the 8x5 contact
  sheet and the full-resolution frames at 0.02, 28.75 and 39.95 s inspected:
  the three-line title "Throw a bouncy ball / under a table. / So where does
  it go?" over the two table panels from frame 0, both balls at the hand
  with the readouts "x 0.01 m", "speed 3.57 m/s", "spin 0.0 turns/s" (the
  thumbnail); 28.75 s shows throw 4 with the rough ball caught at the hand
  under "back at the hand / 13 cm behind" at "caught t 0.79 s" with its
  three numbered bounce marks, and the smooth ball "gone t 0.77 s" with the
  "out the far side" tag and its path leaving the frame past the table
  edge, the card "throw a bouncy ball under a table. / so where does it go?
  back to your hand, / at 97 percent of its forward speed / the smooth ball
  flies out the far side" lit under the caption "It comes back at"; 39.95 s
  shows the crossfade to the title frame with "throw 5 of 5" fading; the
  timing table puts the question at 1.89 s after the four-word lead-in
  "Throw a bouncy ball."; the narrated numbers (seventy centimeters, ninety
  seven percent) match the 0.7 m table underside and the 97.08 percent
  return share in media/superball/measure.log, and the producer's bounce map
  solved from the two rules reproduces the orchestrator's derivation in the
  Goal (product map (1/343) [[-333, 52], [130, 333]], energy 3.125 J/kg
  through every bounce); captions sit in the y 1440 to 1520 band clear of
  the geometry; final.mp4 h264 1080x1920 60 fps, 2,400 frames, aac 22050 Hz
  mono, 40.000 s, moov before mdat, md5 8874cc39d0323e62f5828b29b501698f;
  title 99 characters; the producer's 1/6 playback and the forward-speed
  share as the payoff number accepted; approved for release
- quota check: clock 2026-09-24T10:48:38+03:00; one upload attempt (ballistic,
  10:46:59, published as bEni27RJgM4 at 10:47:53) recorded since the
  2026-09-24 10:00 EEST boundary (log entries and media/*/upload.log both
  checked); this is insert attempt 2 of the hard cap of 5
- attempt 2 recorded at 2026-09-24T10:48:38+03:00, video name superball, before
  running `scripts/yt-upload.py superball`

- attempt 2 outcome: `scripts/yt-upload.py superball` ran 10:48:43 to
  10:48:46 EEST and failed at the resumable-upload start with HTTP 400
  invalidDescription ("The request metadata specifies an invalid video
  description", location body.snippet.description) before any media was
  sent (`media/superball/upload.log`); no video was created. Cause: the
  Measured list in `projects/superball/metadata.json` wrote the bounce
  speed changes as "2.50 -> 1.07 m/s" and YouTube rejects the characters <
  and > in titles and descriptions. Fix at 2026-09-24T10:49:49+03:00: the four
  " -> " arrows replaced by " to " (the only change; the JSON keys, title,
  tags and every number unchanged; no < or > remain in any of today's
  three metadata files); `scripts/yt-upload.py` now refuses a title or
  description containing < or >, or a description over 5,000 characters,
  before it calls the API. The attempt counts toward the daily cap
  (counted at 1 + 1,600 units, the worst case, although the insert was
  refused at the metadata stage); a replacement upload follows as attempt
  3 of 5.

- quota check: clock 2026-09-24T10:50:02+03:00; two upload attempts (ballistic,
  10:46:59, published as bEni27RJgM4 at 10:47:53; superball, 10:48:38,
  failed at 10:48:46 with invalidDescription, no video created) recorded
  since the 2026-09-24 10:00 EEST boundary (log entries and
  media/*/upload.log both checked); this is insert attempt 3 of the hard
  cap of 5, the replacement upload with the fixed description; final.mp4
  unchanged, md5 8874cc39d0323e62f5828b29b501698f
- attempt 3 recorded at 2026-09-24T10:50:02+03:00, video name superball, before
  running `scripts/yt-upload.py superball`




### Published
- upload: `scripts/yt-upload.py superball` (attempt 3, the fixed
  description) ran 10:50:07 to 10:50:13 EEST, token verified to see only
  the Seed Zero channel, video id l-MyYaMlxc8, private
  (`media/superball/upload.log`, which also holds the failed attempt 2)
- gate: `scripts/yt-qa.py superball l-MyYaMlxc8 --wait --publish` ran in
  the foreground from 10:50:22 EEST: processing succeeded and the 10 tags
  read back on the first poll, 15 of 15 pass (processed, succeeded, hd,
  1080x1920, title, description, tags as a set, category 27, not for kids,
  PT41S for the 40.000 s file, private); containsSyntheticMedia reads
  absent as on every earlier upload (`media/superball/publish.log`)
- publish: the same run set the video public at 2026-09-24T10:50:55+03:00;
  the re-read after 15 s shows privacyStatus public, madeForKids false,
  embeddable true; public at https://youtu.be/l-MyYaMlxc8
- slot resolution: published for the 2026-09-24 quota day


### Quota
- attempts 2 and 3 of the hard cap of 5 for the quota day that began
  2026-09-24T10:00 EEST; attempt 2 (failed insert, invalidDescription)
  counted at 1 + 1,600 = 1,601 units as the worst case; attempt 3 cost
  1 + 1,600 + 54 = 1,655 units (the channels.list verification inside
  yt-upload.py, the insert, the gate run's reads, update and re-read as
  printed by yt-qa.py); day total after three attempts 4,911 units


### Repository
- committed as 26e1279 "Publish the day twenty-six slate" (sims,
  projects, tasks, docs/niche.md, web/data; no media, previews or
  secrets) and pushed to origin/master at 2026-09-24 10:57 EEST; the
  yt-upload.py bracket check went out in the owner's earlier commit
  4b1345c at 10:52

