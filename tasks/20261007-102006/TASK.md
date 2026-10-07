# Produce short: tilting tray, a marble beside a dice on a tray tilting at 3 degrees a second, which one goes first

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day39

## Goal

Backlog idea (trend research 2026-10-07, task 20261007-100305, pillar 2
chaos and physics, everyday mechanics; read the full "Tilting tray,
marble or dice" bullet under "Added by trend research 2026-10-07" in
docs/niche.md): a marble and a dice side by side on a tray that tilts
slowly; the marble leaves almost at once, the dice waits.

Orchestrator notes (2026-10-07; closed forms in /tmp/day39/closed.py with
the log /tmp/day39/closed.log, research script /tmp/day39/research/tray.py
with tray.log; g = 9.807 m/s^2). Read /tmp/day39/producer-conventions.md
first. The model: a solid marble of radius R = 1 cm (k = 2/5; the mass
cancels, say so; no rolling resistance, chosen) and a dice (a 1.6 cm cube
modelled as a sliding block with grip mu = 0.4, static equal to kinetic;
a cube only tips above 45 degrees of tilt, so it slides first, say so)
rest side by side with their contact points 0.40 m up a tray from its
low edge. The tray tilts from flat at w = 3.00 deg/s = 0.052360 rad/s
about its low edge, which stays put. Top band, the slow "no" case: the
DICE. Friction holds it until tan(theta) = mu, theta = 21.80 deg at t =
7.267 s; then it slides with a = g sin(theta) - mu g cos(theta) (plus
the tray-frame terms) and leaves the edge at 8.910 s, 26.73 deg, 0.727
m/s; its floor push never drops below 0.901 of its weight. Bottom band,
the fast "yes" case: the MARBLE. Friction can only turn a ball, so it
rolls from the first instant: s = g (w t - sin w t) / ((1 + k) w^2) in
the tray frame without the frame terms, off the edge at 1.871 s and
5.612 deg; with the centrifugal (+ w^2 x) and Coriolis terms it is 1.873
s, 5.62 deg, 0.642 m/s; grip needed k / (1 + k) tan(theta) = 0.0281 at
the edge (any grip above that rolls it without slipping); floor push
0.995 of its weight. Margin: the dice leaves 7.04 s and 21.1 deg after
the marble. Integrate both bands with RK4 at dt = 1e-4 s in the tray
frame (position along the tray from the low edge, speed; the marble's
spin from v = omega R), a stick-slip event for the dice (it stays still
while the drive along the tray is within mu N, and never moves uphill),
bisection for the edge arrival, a half-step rerun agreeing within 1e-9 s,
as a check against the closed forms; print the energy balance per
kilogram for the marble at the edge (the tray does work on it, so print
the potential drop, the translation and spin shares 5/7 and 2/7 of its
kinetic energy and the work done by the tray's rotation), the no-slip
condition, the table at 1 s steps (tilt, positions and speeds of both)
and the description variants.

Checks, not facts (the sim must print and compare; state them as checks):
marble off at 1.873 s, 5.62 deg, 0.642 m/s (closed form without frame
terms 1.871 s, 5.61 deg); dice slide start 21.80 deg at 7.267 s, off at
8.910 s, 26.73 deg, 0.727 m/s; margin 7.04 s and 21.1 deg; grip needed
by the marble 0.0281; for the description: dice grips 0.2 / 0.3 / 0.5 /
0.6 leave at 16.3 / 21.7 / 31.4 / 35.8 deg; tilt rates 1 / 2 / 5 deg/s
put the marble off at 2.7 / 4.3 / 7.9 deg against the dice at 24.2 /
25.6 / 28.8 deg; an ice cube on ice (no grip) leaves at 5.0 deg, a solid
cylinder (k = 1/2) at 5.7, a hollow ball (k = 2/3) at 6.0, a ring (k =
1) at 6.3 deg; the marble's leaving tilt does not depend on its radius
(print 5 mm and 20 mm: unchanged); the frame terms are worth about 0.006
deg. Print the schedule in video time, the text widths and the layout
clearances.

Drawing: two-band layout (sims/deskchain style, read it whole; sims/uphill
and sims/rails draw a slope with a rolling striped ball; sims/cartramp
draws a stop pad and a gold mark on a slope; sims/pushpull draws a block
on a floor), side view, the dice band on top (the "no" case) and the
marble band below; same scale, same clock. The tray is a thick line
about 0.46 m long, about 950 px per metre (437 px), pivoted at its low
edge on the RIGHT of the band (x about 900) and rising on the left as it
tilts (at 26.7 deg the far end is about 196 px up, so put the pivot low
in the band, about 150 px above the band bottom, and keep the raised
end under the label rows: assert it); a small pivot mark at the low
edge and a short drop below it so the leaving object visibly falls off
the end. Objects start with their contact points 0.40 m (380 px) left
of the pivot: the dice as a 1.6 cm cube drawn larger than life (about
30 px, with pips) and the marble as a 2 cm ball drawn about 22 px with
a stripe so the spin shows (say so in measure.log: drawn larger than
life, the physics uses R = 1 cm). Readouts (28 px): left column "tilt
NN.N deg" and the clock; right column "N.NN m from the edge" and "speed
N.NN m/s" (the marble band may show "spin NN.N turns/s"). Gold event
rows: top "dice: off at 26.7 deg (8.91 s)" (lit at the edge and held),
bottom "marble: off at 5.6 deg (1.87 s)" (lit and held). A gold dashed
tick on the dice band at 21.8 deg (the slide start) with "starts to
slide" (24 px) when it happens. Shown in REAL TIME (the tilt is slow):
cycle 10 s (600 frames): release at 0.4 s of the cycle (the tray starts
tilting), the marble off the edge at 0.4 + 1.873 = 2.273 s, the dice
starts sliding at 7.667 s and leaves at 9.310 s, then a crossfade over
the last 0.5 s of the cycle back to the flat tray; 4 cycles in 40 s,
exactly periodic, the last frame equal to the first. That puts the dice
leaving at 9.3, 19.3, 29.3 and 39.3 s of video: set payoff_t near 28.5
s so the card rises as the dice goes over in the third cycle, and put
the payoff words there. The legend row after the title: "same tray,
tilting 3 deg a second, real time"; the shared clock in seconds since
the tilt began. Overlay: "marble and dice, 3 deg/s tilt, grip 0.4 | no
seed" (measure it; shorten if over 950 px).

Day thirty-nine, first slot. Chosen because "which goes first" on a
slowly tilting tray reads as a close call to most viewers and is not
(the marble leaves at 6 degrees, the dice at 27), the two panels end
visibly differently (one object gone while the other sits still for
seven more seconds), the thresholds are exact (tan(theta) = mu for the
block; the ball rolls at any tilt) and the repeat is a natural loop.
Question in the first two seconds: "Tilt a tray with a marble and a
dice on it. Which one goes first?" (pre-test; a question-first form
"Which goes first off a tilting tray, the marble or the dice?" lands at
0.6 s). Keep the question identical in the title, the hook and the
payoff. Setup number: "three degrees a second" (one setup number only;
the grip 0.4 goes to the overlay, card and description). Payoff: the
marble, at six degrees; the dice waits until twenty seven (the two
panel results; at most two numbers in the payoff beat). The mechanism
sentence must follow the picture: friction holds a block, but on a ball
it can only make it turn, so the ball rolls at any tilt; the block
waits until the slope beats its grip. Whisper risks: "dice" (pre-test;
never "die"), "tray", "tilt", "tilts", "tilting" (pre-test), "marble"
(passed on day 38), sentence-initial "Grip" and "Spin" (never start a
sentence with them), avoid "do you", avoid "too", "twenty seven" (pre-
test "twenty seven degrees"). Pre-test hooks with scripts/voiceover.sh
and keep the one whose question lands earliest under two seconds.
Measure every fixed text line with PIL before rendering and keep every
line under 950 px, and the title under 100 characters with no < or >.
Music seed 118. Templates: sims/deskchain (two-band layout, asserts,
the clock, the crossfade; read it whole), sims/uphill and sims/rails (a
rolling striped ball on a slope), sims/cartramp (stop pad, gold mark),
sims/pushpull (a block with friction). Sim name tray: sims/tray/tray.py,
projects/tray/, media/tray/.

## Claim (expected; the sim's numbers replace these)

A marble and a dice sit side by side 40 cm up a tray that tilts at 3
degrees a second. The marble rolls at once and is off the edge at 5.6
degrees, after 1.87 s. The dice (grip 0.4) sits still until the tilt
reaches 21.8 degrees at 7.27 s, then slides and leaves at 26.7 degrees,
after 8.91 s, 7.0 s and 21 degrees after the marble. Narrated: three
degrees a second (setup); six degrees against twenty seven degrees
(payoff). Card: the question; the answer with 5.6 against 26.7 degrees;
the dice starts to slide at 21.8 degrees (tan = grip 0.4); grip 0.2
leaves at 16.3, grip 0.6 at 35.8 degrees; any grip above 0.028 rolls the
marble. Description: the model statement, the equations, the two runs,
the grip and tilt-rate variants, the other rolling shapes, the checks.

## Claim

A solid marble (radius 1 cm, k = 2/5, the mass cancels, no rolling
resistance, chosen) and a dice (a 1.6 cm cube as a sliding block with
grip 0.4, static equal to kinetic; it tips only above 45 degrees, so it
slides first) sit side by side with their contact points 0.40 m up a
0.46 m tray that tilts from flat at 3.00 deg/s (0.052360 rad/s) about
its low edge; g = 9.807 m/s^2. Friction can only turn a ball, so the
marble rolls from the first instant and is off the edge at 1.8726 s,
tilt 5.6179 deg, at 0.6415 m/s (closed form without the frame terms
1.8707 s, 5.6121 deg; the frame terms are worth 0.0058 deg); grip needed
at the edge 0.0281; floor push 0.9883 of its weight. The dice holds
until tan(theta) = 0.4 (21.80 deg at 7.267 s), then slides and leaves at
8.8910 s, 26.6729 deg, at 0.7441 m/s (floor push never below 0.8856 of
its weight), 7.02 s and 21.06 deg after the marble. Narrated: three
degrees a second (setup); six degrees against twenty seven (payoff).
Card: the question; the marble at 5.6 deg, the dice at 26.7; the dice
slides from 21.8 deg, tan = grip 0.4; grip 0.2 leaves at 16.3 deg, 0.6
at 35.7; any grip above 0.028 rolls the marble; friction holds a block,
only turns a ball.

## Evidence

### Measurements

Sim: sims/tray/tray.py with projects/tray/manifest.json (RK4 at dt =
1e-4 s in the tray frame on the position up the tray and the speed,
with the centrifugal term + w^2 x and the Coriolis term 2 w x' in the
normal force, a stick-slip start event for the dice found by bisection,
bisection for the edge arrival, half-step rerun, the closed form for the
marble; deterministic, no seed, no wall clock). Log: media/tray/
measure.log (exit 0; the full final log follows).

Brief checks (the sim prints "checks against the brief (29 checks, 9
failed)"): marble off 1.873 s (sim 1.872627) ok, 5.62 deg (5.61788) ok,
0.642 m/s (0.641485) ok; closed form 1.871 s (1.870701) ok, 5.61 deg
(5.6121) ok; dice slide start 21.80 deg (21.8014) ok at 7.267 s
(7.26714) ok; dice off 8.910 s (sim 8.890970) FAIL, 26.73 deg (26.6729)
FAIL, 0.727 m/s (0.744130) FAIL; margin 7.04 s (7.01834) FAIL, 21.1 deg
(21.0550) ok; marble grip needed 0.0281 (0.0281046) ok; frame terms
0.006 deg (0.00578) ok; dice least N / W 0.901 (0.885638) FAIL; dice
grips 0.2 / 0.3 / 0.5 / 0.6 off at 16.3 / 21.7 / 31.4 / 35.8 deg (sim
16.285 ok / 21.6284 FAIL / 31.3697 ok / 35.6951 FAIL); tilt rates 1 / 2
/ 5 deg/s marble 2.7 / 4.3 / 7.9 deg (2.69833 / 4.28511 / 7.90636, all
ok) against the dice 24.2 / 25.6 / 28.8 deg (24.1481 ok / 25.5222 FAIL /
28.6418 FAIL); ice cube 5.0 deg (5.02229) ok, solid cylinder 5.7
(5.74848) ok, hollow ball 6.0 (5.95382) ok, ring 6.3 (6.32667) ok; 5 mm
and 20 mm marbles: the leaving tilt unchanged (5.6179 deg, asserted).
All nine failed checks are dice numbers and all come from one cause:
the orchestrator's closed.py and research/tray.py carry the Coriolis
term in the normal force with the opposite sign (N = g cos(theta) - 2 w
x' with x' < 0, so N grows as the block slides toward the pivot). In the
inertial frame r'' = (x'' - w^2 x) e_r + 2 w x' e_t, so the tray must
push N = m g cos(theta) + 2 m w x', which is smaller for a block moving
toward the pivot; the sim uses that sign. The sim also runs the dice
with the brief's sign as a comparison and prints "the same dice checks
with the Coriolis term on N reversed ... (13 checks, 0 failed)": 8.9095
s, 26.7286 deg, 0.7274 m/s, N / W 0.9009, margin 7.037 s / 21.11 deg,
grips 16.31 / 21.67 / 31.44 / 35.77 deg, rates 24.16 / 25.55 / 28.75
deg, each within the check tolerance of the brief. The whole difference
is 0.056 deg and 0.019 s on the dice; the claim (card 26.7 deg, narrated
twenty seven, 7.0 s and 21 deg after the marble) is unchanged under
either sign. Also printed: the half-step reruns agree within 7.1e-15 s;
the marble's RK4 without the frame terms agrees with the closed form
within 2.5e-14 s; the energy balance for the marble closes to -1.2e-15
J/kg (potential drop 0: its contact point starts and ends at the pivot's
height, the tray does the work, 0.2878 J/kg, split 5/7 translation and
2/7 spin); the no-slip condition; the 1 s table; the schedule; the text
widths (every line under 950 px, max 910 px for payoff line 3); the
layout clearances.

Final measure.log:

```
Wed Oct  7 10:40:57 AM EEST 2026
warning: Git tree '/home/alex/personal/seedzero' is dirty
setup: side view, two bands on one clock, the same tray drawn the same way at the same scale: a tray 0.46 m long tilts from flat at w = 3.00 deg/s = 0.052360 rad/s about its low edge (the pivot stays put), in real time; a solid marble of radius R = 1 cm (2 cm across; I = k m R^2 with k = 0.4; the mass cancels; no rolling resistance, chosen) and a dice (a 1.6 cm cube modelled as a sliding block with grip mu = 0.4, static equal to kinetic, a chosen number; a cube only tips above 45 degrees of tilt (tan 45 = 1 against tan(theta) = 0.4 for the slide), so it slides first and never tips) rest side by side with their contact points 0.4 m up the tray from its low edge; g = 9.807 m/s^2; top band the dice (the slow 'no' case), bottom band the marble (the fast 'yes' case); both integrated by classical RK4 at 10000 steps per second (dt = 1e-04 s) in the tray frame on the position up the tray and the speed (the marble's spin from v = omega R), with the centrifugal term + w^2 x and the Coriolis term 2 w x' in the normal force (an object moving toward the pivot presses less on the tray: N = m g cos(theta) + 2 m w x', x' < 0), a stick-slip start event for the dice (bisection on the time the drive beats the grip; it never moves uphill), the edge arrival located by bisection inside the step, checked against the closed form and a half-step rerun; after the edge each object falls freely in the room frame; shown in real time on a 10 s cycle (600 frames) with the tilt starting 0.4 s into the cycle, 4 cycles in 40 s; drawn at 950 px per metre (tray 437 px, start 380 px left of the pivot); the objects are drawn larger than life: the dice 30 px against the model's 1.6 cm = 15.2 px, the marble 22 px across against the model's 2 cm = 19.0 px, and the drawn marble's stripe rolls without slipping at its drawn size (the physics uses R = 1 cm); the readouts are the model's; deterministic, no seed
marble (bottom band): friction can only turn a ball, so it rolls from the first instant (starts moving at 0.000 s, 0.00 deg; the tray already turns, so the centrifugal push w^2 L = 0.00110 m/s^2 rolls it uphill by 1.2 nm at up to 0.84 um/s until g sin(theta) beats it 2.1 ms in, then it rolls toward the edge); (1 + k) x'' = -g sin(theta) + w^2 x; RK4 with the frame terms: off the edge at 1.872627 s = 1.873 s, tilt 5.6179 deg = 5.62 deg = 5.6 deg = 6 deg (rounded), speed 0.641485 m/s = 0.641 m/s, 18726 steps; without the frame terms 1.870701 s, 5.6121 deg, 0.641266 m/s (closed form g (w t - sin w t) / ((1 + k) w^2) = L: 1.870701 s, 5.6121 deg, 0.641266 m/s; diffs -2.5e-14 s, -7.6e-14 deg, -8.7e-15 m/s); the frame terms are worth +0.0019 s and +0.0058 deg; half-step rerun (dt = 5e-05 s): 1.872626586 s (-2.2e-15 s) at 0.641485340 m/s (-4.2e-15 m/s); spin at the edge omega = v / R = 64.1 rad/s = 10.2 turns per second, 6.37 turns over the 40 cm; no-slip condition: the friction needed is k / (1 + k) of the drive along the tray, so the grip needed at the edge is k / (1 + k) tan(theta) = 0.0281 (0.0283 with the Coriolis part of N; any grip above that rolls it without slipping, so the chosen 0.4 holds by a factor 14); floor push N / W = cos(theta) - 2 w v / g = 0.9883 of its weight at the edge (cos alone 0.9952; the least over the run 0.9883)
dice (top band): at rest the drive along the tray is g sin(theta) - w^2 x against a grip of mu g cos(theta); tan(theta) = mu gives 21.8014 deg = 21.80 deg at 7.2671 s = 7.267 s; with the centrifugal term (w^2 L = 0.00110 m/s^2) the RK4 start event is at 7.2691 s, 21.8074 deg; then x'' = -g sin(theta) + w^2 x + mu N with N = g cos(theta) + 2 w x'; off the edge at 8.890970 s = 8.891 s = 8.89 s, tilt 26.6729 deg = 26.67 deg = 26.7 deg = 27 deg (rounded), speed 0.744130 m/s = 0.744 m/s = 0.74 m/s, 16218 steps, 1.6219 s of sliding; the floor push never drops below 0.8856 of its weight; without the frame terms 8.898442 s, 26.6953 deg, 0.735428 m/s; with the Coriolis term on N reversed (the orchestrator's closed.py and research/tray.py convention, N = g cos(theta) - 2 w x': a comparison, not the model) 8.909549 s, 26.7286 deg, 0.727366 m/s, least N / W 0.9009; half-step rerun (dt = 5e-05 s): 8.890970322 s (-7.1e-15 s) at 0.744129629 m/s (-4.7e-15 m/s); small-angle slide after the start dt^3 = 6 L / (g sqrt(1 + mu^2) w): 1.6311 s
margin: the dice leaves 7.0183 s = 7.02 s = 7.0 s and 21.0550 deg = 21.06 deg = 21 deg after the marble; when the dice starts to slide the marble has been gone for 5.40 s; the tilt at the edge is 4.75 times the marble's
energy per kg for the marble at the edge: potential drop g (h0 - h_edge) = 0.0000 J/kg (its contact point starts on the flat tray at the pivot's height and leaves at the pivot; the tray lifts it to a peak height of 1.85 cm at 1.18 s on the way); kinetic energy 0.2881 J/kg = translation 0.2058 (0.7143 = 1 / (1 + k) = 5/7) + spin 0.0823 (0.2857 = k / (1 + k) = 2/7; the spin relative to the tray, 0.5 k v^2); the start kinetic energy with the tray already turning 0.5 (L w)^2 = 0.000219 J/kg; work done by the tray's rotation through the normal force, integral of N x w dt = 0.287833 J/kg; balance KE - KE0 - W = -1.2e-15 J/kg
  t 0.0000 s, tilt  0.000 deg: dice 0.4000 m from the edge (v -0.0000 m/s, rest); marble 0.4000 m from the edge (v -0.0000 m/s)
  t 1.0000 s, tilt  3.000 deg: dice 0.4000 m from the edge (v -0.0000 m/s, rest); marble 0.3393 m from the edge (v 0.1826 m/s)
  t 1.8726 s, tilt  5.618 deg: dice 0.4000 m from the edge (v -0.0000 m/s, rest); marble off the edge
  t 2.0000 s, tilt  6.000 deg: dice 0.4000 m from the edge (v -0.0000 m/s, rest); marble off the edge
  t 3.0000 s, tilt  9.000 deg: dice 0.4000 m from the edge (v -0.0000 m/s, rest); marble off the edge
  t 4.0000 s, tilt 12.000 deg: dice 0.4000 m from the edge (v -0.0000 m/s, rest); marble off the edge
  t 5.0000 s, tilt 15.000 deg: dice 0.4000 m from the edge (v -0.0000 m/s, rest); marble off the edge
  t 6.0000 s, tilt 18.000 deg: dice 0.4000 m from the edge (v -0.0000 m/s, rest); marble off the edge
  t 7.0000 s, tilt 21.000 deg: dice 0.4000 m from the edge (v -0.0000 m/s, rest); marble off the edge
  t 7.2691 s, tilt 21.807 deg: dice 0.4000 m from the edge (v -0.0000 m/s, move); marble off the edge
  t 8.0000 s, tilt 24.000 deg: dice 0.3637 m from the edge (v 0.1492 m/s, move); marble off the edge
  t 8.8910 s, tilt 26.673 deg: dice off the edge; marble off the edge
for the description: dice grip 0.2: slides from 11.31 deg (3.77 s), off at 16.28 deg = 16.3 deg (5.43 s) at 0.727 m/s; dice grip 0.3: slides from 16.70 deg (5.57 s), off at 21.63 deg = 21.6 deg (7.21 s) at 0.734 m/s; dice grip 0.5: slides from 26.57 deg (8.86 s), off at 31.37 deg = 31.4 deg (10.46 s) at 0.755 m/s; dice grip 0.6: slides from 30.96 deg (10.32 s), off at 35.70 deg = 35.7 deg (11.90 s) at 0.768 m/s; tilt rate 1 deg/s: marble off at 2.70 deg = 2.7 deg (2.70 s), dice off at 24.15 deg = 24.1 deg (24.15 s); tilt rate 2 deg/s: marble off at 4.29 deg = 4.3 deg (2.14 s), dice off at 25.52 deg = 25.5 deg (12.76 s); tilt rate 5 deg/s: marble off at 7.91 deg = 7.9 deg (1.58 s), dice off at 28.64 deg = 28.6 deg (5.73 s); ice cube on ice (slides, no grip) (k = 0): off at 5.02 deg = 5.0 deg (1.67 s); solid cylinder (k = 0.5): off at 5.75 deg = 5.7 deg (1.92 s); hollow ball (k = 0.6667): off at 5.95 deg = 6.0 deg (1.98 s); ring (k = 1): off at 6.33 deg = 6.3 deg (2.11 s); marble radius 5 mm: off at 5.6179 deg (1.872627 s), unchanged (the radius does not enter (1 + k) x'' = -g sin(theta) + w^2 x; spin at the edge 20.4 turns/s); marble radius 20 mm: off at 5.6179 deg (1.872627 s), unchanged (the radius does not enter (1 + k) x'' = -g sin(theta) + w^2 x; spin at the edge 5.1 turns/s); the frame terms (centrifugal + w^2 x, Coriolis 2 w x' in N) are worth 0.0058 deg for the marble and -0.0224 deg for the dice
checks against the brief (29 checks, 9 failed): marble off (s): brief 1.873, sim 1.87263, diff -3.7e-04: ok; marble off (deg): brief 5.62, sim 5.61788, diff -2.1e-03: ok; marble off speed (m/s): brief 0.642, sim 0.641485, diff -5.1e-04: ok; marble closed form (s): brief 1.871, sim 1.8707, diff -3.0e-04: ok; marble closed form (deg): brief 5.61, sim 5.6121, diff +2.1e-03: ok; dice slide start (deg): brief 21.8, sim 21.8014, diff +1.4e-03: ok; dice slide start (s): brief 7.267, sim 7.26714, diff +1.4e-04: ok; dice off (s): brief 8.91, sim 8.89097, diff -1.9e-02: FAIL; dice off (deg): brief 26.73, sim 26.6729, diff -5.7e-02: FAIL; dice off speed (m/s): brief 0.727, sim 0.74413, diff +1.7e-02: FAIL; margin (s): brief 7.04, sim 7.01834, diff -2.2e-02: FAIL; margin (deg): brief 21.1, sim 21.055, diff -4.5e-02: ok; marble grip needed: brief 0.0281, sim 0.0281046, diff +4.6e-06: ok; frame terms (deg): brief 0.006, sim 0.00577813, diff -2.2e-04: ok; dice least N / W: brief 0.901, sim 0.885638, diff -1.5e-02: FAIL; dice grip 0.2 off (deg): brief 16.3, sim 16.285, diff -1.5e-02: ok; dice grip 0.3 off (deg): brief 21.7, sim 21.6284, diff -7.2e-02: FAIL; dice grip 0.5 off (deg): brief 31.4, sim 31.3697, diff -3.0e-02: ok; dice grip 0.6 off (deg): brief 35.8, sim 35.6951, diff -1.0e-01: FAIL; rate 1 marble off (deg): brief 2.7, sim 2.69833, diff -1.7e-03: ok; rate 1 dice off (deg): brief 24.2, sim 24.1481, diff -5.2e-02: ok; rate 2 marble off (deg): brief 4.3, sim 4.28511, diff -1.5e-02: ok; rate 2 dice off (deg): brief 25.6, sim 25.5222, diff -7.8e-02: FAIL; rate 5 marble off (deg): brief 7.9, sim 7.90636, diff +6.4e-03: ok; rate 5 dice off (deg): brief 28.8, sim 28.6418, diff -1.6e-01: FAIL; ice cube on ice (slides, no grip) off (deg): brief 5, sim 5.02229, diff +2.2e-02: ok; solid cylinder off (deg): brief 5.7, sim 5.74848, diff +4.8e-02: ok; hollow ball off (deg): brief 6, sim 5.95382, diff -4.6e-02: ok; ring off (deg): brief 6.3, sim 6.32667, diff +2.7e-02: ok
the same dice checks with the Coriolis term on N reversed, the brief's convention (13 checks, 0 failed; a comparison, the model above is the sim's): dice off (s): brief 8.91, sim 8.90955, diff -4.5e-04: ok; dice off (deg): brief 26.73, sim 26.7286, diff -1.4e-03: ok; dice off speed (m/s): brief 0.727, sim 0.727366, diff +3.7e-04: ok; dice least N / W: brief 0.901, sim 0.900913, diff -8.7e-05: ok; margin (s): brief 7.04, sim 7.03692, diff -3.1e-03: ok; margin (deg): brief 21.1, sim 21.1108, diff +1.1e-02: ok; dice grip 0.2 off (deg): brief 16.3, sim 16.3139, diff +1.4e-02: ok; dice grip 0.3 off (deg): brief 21.7, sim 21.6711, diff -2.9e-02: ok; dice grip 0.5 off (deg): brief 31.4, sim 31.4377, diff +3.8e-02: ok; dice grip 0.6 off (deg): brief 35.8, sim 35.7744, diff -2.6e-02: ok; rate 1 dice off (deg): brief 24.2, sim 24.161, diff -3.9e-02: ok; rate 2 dice off (deg): brief 25.6, sim 25.5546, diff -4.5e-02: ok; rate 5 dice off (deg): brief 28.8, sim 28.7519, diff -4.8e-02: ok
schedule (video time, real time): cycles of 10 s start at -10.00, 0.00, 10.00, 20.00, 30.00 s; the tray starts tilting 0.4 s into each cycle at 0.40, 10.40, 20.40, 30.40 s; the marble leaves the edge 1.873 s later at 2.27, 12.27, 22.27, 32.27 s (2.273 s into the cycle; its event row lights) and is out of its band 0.186 s after that at 2.46, 12.46, 22.46, 32.46 s; the dice starts to slide at 7.67, 17.67, 27.67, 37.67 s (7.669 s into the cycle; the 'starts to slide' tick lights over 0.3 s) and leaves the edge at 9.29, 19.29, 29.29, 39.29 s (9.291 s into the cycle; its event row lights), out of its band 0.173 s later at 9.46, 19.46, 29.46, 39.46 s (9.464 s into the cycle, before the fade at 9.50 s); the tray reaches 28.80 deg at the end of the cycle; the reset crossfade back to the flat tray runs over the last 0.5 s of each cycle (from 9.50, 19.50, 29.50, 39.50 s; the readouts out over its first half and in over its second); on the first frame the cycle is 0.00 s in (-0.400 s after the tilt began: the dice held at 40.0 cm, the marble held at 40.0 cm, the tray at 0.0 deg); title until 3 s; payoff card from 28.4 s; the title fades back in over the last 0.5 s and the last frame repeats the first (the scene is periodic: 40 s holds exactly 4 cycles)
text widths (the on-screen strings verbatim): overlay@34 901 px 'marble and dice, 3 deg/s tilt, grip 0.4 | no seed', title line 1@56 454 px 'Marble or dice', title line 2@56 515 px 'on a tilting tray:', title line 3@56 670 px 'which one goes first?', legend@40 823 px 'same tray, 3 deg a second, real time', clock@28 432 px '12.35 s since the tilt began', clock held@28 178 px 'flat, at rest', label dice@40 489 px 'dice: a block, grip 0.4', fixed dice@28 323 px 'slides from 21.8 deg', event dice@40 641 px 'dice: off at 26.7 deg (8.89 s)', label marble@40 486 px 'marble: a ball, it rolls', fixed marble@28 521 px 'needs grip 0.028: rolls at any tilt', event marble@40 678 px 'marble: off at 5.6 deg (1.87 s)', tilt@28 194 px 'tilt 26.7 deg', from the edge@28 342 px '0.40 m from the edge', off@28 192 px 'off the edge', speed@28 239 px 'speed 0.74 m/s', left at@28 241 px 'left at 0.74 m/s', tick@24 188 px 'starts to slide', payoff line 1@40 479 px 'which one goes first?', payoff line 2@40 889 px 'the marble, at 5.6 deg; the dice at 26.7', payoff line 3@40 910 px 'dice slides from 21.8 deg, tan = grip 0.4', payoff line 4@40 878 px 'grip 0.2 leaves at 16.3 deg, 0.6 at 35.7', payoff line 5@40 850 px 'any grip above 0.028 rolls the marble', payoff line 6@40 871 px 'friction holds a block, only turns a ball'
row check: the left column ends at x 561 px, the right column starts at x 698 px; both end 136 px under the band top; the pivot at x 900, 400 px under the band top (150 px above the band bottom; the stand to 422); the tray is 437 px long, its far end at x 463 when flat and 211 px up at the cycle's last tilt (28.80 deg), its surface there 189 px under the band top; the dice's top corner at the slide start 231 px under the band top; the objects start 380 px left of the pivot at x 520; the slide-start tick runs from radius 40 to 300 px along the 21.8 deg ray and its label is centred at x 655, 367 px (188 px wide; the tray slab's underside over the label's right end is 350 px under the band top at the slide start); the event row spans 468 to 512 px under the band top and x 61 to 739 px (widest 678 px, centred on 400); the falling objects pass x 870 and beyond; each band is 550 px tall (y 330 to 880 and 880 to 1430); the caption band starts at y 1440; the title rows end at y 330 and the overlay band ends at y 130
exit 0
Wed Oct  7 10:40:59 AM EEST 2026
```

### Production

- Manifest: projects/tray/manifest.json (fps 60, 40 s, real time,
  cycle 10 s, the tilt starts 0.4 s into the cycle, first_cycle_at 0.0,
  reset crossfade 0.5 s, tick fade 0.3 s, 950 px/m with the pivot at x
  900 and 400 px under the band top, the dice drawn 30 px and the marble
  22 px across, title until 3 s, payoff_t 28.4 s, hold 0.6 s, loop fade
  0.5 s, music seed 118, music gain 0.18, voice offset 0.6, caption_y
  0.75, overlay "marble and dice, 3 deg/s tilt, grip 0.4 | no seed").
- Layout: two bands (dice y 330-880, marble 880-1430), label rows at 40
  px under the band top ("dice: a block, grip 0.4", "marble: a ball, it
  rolls"), readouts at 84 and 120 (left "tilt NN.N deg" and a fixed
  line, "slides from 21.8 deg" / "needs grip 0.028: rolls at any tilt";
  right "N.NN m from the edge" and "speed N.NN m/s", gold "off the edge"
  / "left at N.NN m/s" after the edge), the shared clock at y 290 ("N.NN
  s since the tilt began", "flat, at rest" while flat), the legend at y
  236 "same tray, 3 deg a second, real time"; gold event rows centred at
  x 400, 490 px under the band top ("dice: off at 26.7 deg (8.89 s)",
  "marble: off at 5.6 deg (1.87 s)"); the tray is a 10 px slab 437 px
  long pivoted on a gold dot over a small stand at x 900, rising on the
  left, with a dashed flat reference and a tilt arc at the pivot, and a
  red (dice) or teal (marble) start tick 380 px left of the pivot; a
  gold dashed ray along 21.8 deg with "starts to slide" (24 px) lights
  over 0.3 s at the slide start and holds; the dice is a 30 px cube with
  three pips that keeps its last orientation in flight, the marble a
  22 px striped ball whose stripe rolls without slipping at its drawn
  size; after the edge both fall freely and leave the band; the readouts
  are the model's (printed in measure.log).
- Schedule (video time): the tilt starts at 0.40, 10.40, 20.40, 30.40
  s; the marble leaves at 2.27, 12.27, 22.27, 32.27 s; the dice starts
  to slide at 7.67, 17.67, 27.67, 37.67 s and leaves at 9.29, 19.29,
  29.29, 39.29 s (out of its band at 9.46 s of the cycle, before the
  fade at 9.50); crossfades from 9.50, 19.50, 29.50, 39.50 s. Frame 0:
  the flat tray at rest, both objects held at 0.40 m.
- Smoke frames viewed: media/tray/smoke-{0.0,2.3,7.8,9.45,29.0}.png
  twice. First pass found: the marble band's tilt readout froze at 5.6
  deg after the marble left (the OFF state returned the leaving tilt),
  "speed -0.00 m/s" at the flat start, the "starts to slide" label
  overlapping the dashed ray, and the dim ray drawn on the flat tray
  before the tilt. Fixed (the tilt readout follows the tray after the
  edge, speeds clamped at 0, the label moved to radius 240 and 60 px
  above the ray with the row check on the slab's underside, the ray
  drawn only once the tilt has begun) and confirmed on the second pass:
  0.0 s title over the flat tray; 2.3 s the marble just off the edge
  with its event row, the dice still at 0.40 m; 7.8 s the dice sliding
  at 0.39 m with the gold ray and label; 9.45 s the dice falling past
  the pivot with "dice: off at 26.7 deg (8.89 s)"; 29.0 s the card up
  with the dice at 0.11 m.
- Measure-only fixes: the first run tripped the "moves uphill" assert
  because at t = 0 the centrifugal push w^2 L beats g sin(theta) for 2.1
  ms and rolls the marble uphill by 1.2 nm (physical; now tracked and
  printed, the strict assert kept for the block); payoff lines 2 / 3 / 4
  measured 988 / 1020 / 976 px and were shortened to 889 / 910 / 878 px.
- Render: media/tray/render.log, footage.mp4 (2400 frames, 28 s); loop
  check 0 px (max channel difference 0); periodicity check 0 px; loop
  step 7082 px between the last two frames.
- Hook pre-tests (media/tray/hooks/pretest.log), all ok on the first
  take: hook1 "Marble or dice on a tilting tray: which one goes first?
  The tray tilts at three degrees a second, in real time." (6.37 s, the
  question first, a pause at 1.89 s); hook2 "Tilt a tray with a marble
  and a dice on it. Which one goes first?" (the question from 2.32 s of
  voice, 2.9 s of video); hook3 "Which goes first off a tilting tray,
  the marble or the dice?" (3.05 s); hook4 "A marble or a dice on a
  tilting tray: which one goes first?" (3.49 s); hook5 "Marble or dice
  on a tilting tray, which one goes first? The tray tilts three degrees
  a second." (5.33 s). Chosen: hook1's first sentence (the question
  first, spoken from 0.60 s of video; the same words in the title, the
  payoff and the card). Word test (words.txt, 29.8 s) passed on the
  first take: "dice", "Tilt the tray", "tilts", "tilting", "tray",
  "marble", "three degrees a second", "twenty seven", "six degrees",
  "Flat again, and it repeats", "Friction holds a block, but on a ball
  it can only make it turn", "The dice holds on, then goes", "beats its
  grip", "Every run the same", "Watch the marble".
- Narration: projects/tray/narration.txt, 109 words; the question is
  the first sentence (spoken 0.60-3.99 s of video) and is repeated word
  for word before the payoff ("So, marble or dice on a tilting tray:
  which one goes first?"); the payoff answers in the same words ("The
  marble, at six degrees. The dice waits until twenty seven."). One
  setup number (three degrees a second), two payoff numbers (the two
  band results).
- Voice: pass 1 ok on the first take (media/tray/voice.log: "ok:
  transcript matches narration (32.473107s)"); no mishearing. Timing
  (media/tray/timing.log, offset 0.6): "Marble or dice on a tilting
  tray." 0.60-2.65; "Which one goes first? The tray tilts at 3 degrees a
  second in real time. The dice holds on then goes." 2.65-9.01 (the
  first tilt from 0.40, the marble off at 2.27, the dice sliding from
  7.67 and off at 9.29); "flat again ... the dice waits until the slope
  beats its grip" 9.01-17.14 (reset 9.50, the second tilt from 10.40,
  marble off 12.27); "then slides. Friction holds a block." 17.14-19.47
  (the dice sliding from 17.67, off 19.29); "But it can only turn a
  bowl." 19.47-21.15 (whisper's spelling in the timing pass only; the
  round trip matched "ball"); "so the ball rolls at any tilt. So marble
  or dice on a tilting tray," 21.15-25.15 (the third tilt from 20.40,
  marble off 22.27); "Which one goes first?" 25.15-26.48; "The marble at
  six degrees." 26.48-28.26; "The dice waits until 27, every run the
  same." 28.26-31.33 (card from 28.4, the dice off at 29.29); "The
  marble always goes first." 31.33-33.07 (the fourth tilt from 30.40,
  marble off 32.27). Voice 32.47 s, ends at 33.07 s of video. 9 silences
  (media/tray/silences.log).
- Compose: media/tray/compose.log: music seed 118, 40.00 s; captions 18
  pauses detected, 17 matched, max chunk start shift 0.733 s against
  word-count timing (no fallback); final.mp4 40.000000 s.
- Text widths (measure.log): overlay 901, title rows 454 / 515 / 670,
  legend 823, clock 432, labels 489 / 486, fixed lines 323 / 521,
  readouts at most 342, event rows 641 / 678, tick label 188, payoff
  lines 479 / 889 / 910 / 878 / 850 / 871 px; all under 950 px,
  asserted.

### Local QA

- media/tray/final.mp4: md5 d704ad8568ef4a78afc38f2a74ade692, 4212079
  bytes; ffprobe h264 1080x1920 60/1, aac 22050 Hz mono, duration
  40.000000; atoms ftyp@0 moov@32 free@44796 mdat@44804 (faststart).
- Caption text against the narration: 35 drawtext chunks (the first is
  the overlay); the joined caption text equals narration.txt word for
  word (checked by script after undoing the drawtext escapes). The first
  caption "Marble or dice on a" is enabled from 0.600 s, "tilting tray:
  which" 1.976-3.035, "one goes first?" 3.035-3.999; "The marble, at
  six" 26.613-27.821, "twenty seven." 29.450-30.188; the last chunk
  "goes first." ends at 33.073 s.
- signalstats YMAX on footage.mp4: caption band rows 1440-1530 = 28
  (background), overlay band rows 96-130 = 28: nothing drawn under the
  captions or the overlay.
- Full-resolution frames viewed (media/tray/qa-T.png): 0.00 overlay,
  three-row title "Marble or dice / on a tilting tray: / which one goes
  first?", both bands flat with the dice and the marble at 0.40 m, "tilt
  0.0 deg", "speed 0.00 m/s", the fixed lines "slides from 21.8 deg" and
  "needs grip 0.028: rolls at any tilt", no caption, no clock (the title
  covers it); 1.00 caption "Marble or dice on a", tilt 1.8 deg, the
  dashed flat reference visible, the dice still at 0.40 m, the marble at
  0.39 m at 0.07 m/s with its stripe turned; 2.10 "tilting tray: which",
  tilt 5.1 deg, the marble at 0.10 m at 0.53 m/s near the pivot, the
  dice unmoved; 18.60 legend and clock "8.20 s since the tilt began",
  tilt 24.6 deg, the dice sliding at 0.32 m, 0.24 m/s, with the gold ray
  and "starts to slide", the marble band empty with "off the edge",
  "left at 0.64 m/s" and the gold row "marble: off at 5.6 deg (1.87
  s)", caption "Friction holds a"; 28.80 card up in full gold (six
  lines, the last "friction holds a block, only turns a ball"), clock
  8.40 s, tilt 25.2 deg, the dice at 0.27 m, 0.36 m/s, caption "The dice
  waits until"; 29.40 clock 9.00 s, the dice in the air past the pivot
  with "off the edge", "left at 0.74 m/s" and the gold row "dice: off at
  26.7 deg (8.89 s)", the card and the same caption; 30.20 the tray
  flat again, "flat, at rest", both objects back at 0.40 m, caption
  "Every run the same:", the card still up; 39.983 identical to frame 0
  (title back, no caption, no card, no clock). media/tray/sheet.png
  viewed: 40 cells, the captions in order, the title on the first three
  cells, the card from 28.4 s (dim at 28 s, full from 29 s), the dice
  event row on the 9 s, 19 s, 29 s and 39 s cells, no clipping, the loop
  closes.
- Question timing: on screen from frame 0 (title) and spoken from 0.60
  s (first caption enable 0.600 s).
- Narrated numbers: "three degrees a second" (manifest rate_deg_s 3.0,
  log "w = 3.00 deg/s"), "six degrees" (log "5.6179 deg = 5.62 deg = 5.6
  deg = 6 deg (rounded)"), "twenty seven" (log "26.6729 deg = 26.67 deg
  = 26.7 deg = 27 deg (rounded)"). Description and title numbers checked
  by script against measure.log (77 distinct numbers, none missing).

### Metadata

projects/tray/metadata.json written by a Python script with asserts
(title 99 chars, description 3996 chars, 11 tags, ASCII, no < or >;
every number in the title and description present in measure.log);
ls -l confirmed the file (4567 bytes). Title: "Marble or dice on a
tilting tray: which one goes first? The marble at 5.6 deg, the dice at
26.7 deg". privacyStatus private, categoryId 27, containsSyntheticMedia
true, selfDeclaredMadeForKids false. The description states the
Coriolis-sign finding in its checks bullet.

### Deviations from the brief

- Coriolis sign: the brief's dice numbers (off at 8.910 s, 26.73 deg,
  0.727 m/s; N / W 0.901; margin 7.04 s; grips 0.3 / 0.6 at 21.7 / 35.8
  deg; rates 2 / 5 deg/s at 25.6 / 28.8 deg) come from N = g cos(theta)
  - 2 w x' in closed.py and tray.py. The physical sign is N = g
  cos(theta) + 2 w x' (x' < 0 toward the pivot: the block presses less).
  The sim uses the physical sign (8.891 s, 26.67 deg, 0.744 m/s, N / W
  0.8856, margin 7.02 s / 21.06 deg, grips 16.28 / 21.63 / 31.37 / 35.70
  deg, rates 24.15 / 25.52 / 28.64 deg for the dice) and prints the
  brief's convention as a comparison (13 of 13 pass). The event row
  reads "(8.89 s)"; the card and the narration are unchanged (26.7 deg,
  twenty seven).
- Hook: "Marble or dice on a tilting tray: which one goes first?"
  (question first, from 0.60 s) instead of "Tilt a tray with a marble
  and a dice on it. Which one goes first?" (the question from 2.9 s of
  video); identical in the title, the hook, the card and the payoff.
- The title is three rows ("Marble or dice / on a tilting tray: / which
  one goes first?"), rows at y 186 / 244 / 302, the last row ending at
  y 330 (asserted against the band top).
- The narration is 109 words (32.47 s), inside the 104-112 target; the
  voice ends at 33.07 s and the fourth cycle runs under music only.
- payoff_t 28.4 s (the brief says near 28.5): the card is at full gold
  by 29.0 s, before the dice goes over at 29.29 s, and "The dice waits
  until twenty seven" is spoken 28.26-30.19 s.
- Readouts: the left column's second line is a fixed line per band
  ("slides from 21.8 deg", "needs grip 0.028: rolls at any tilt")
  instead of a per-band clock; the shared clock sits at y 290. No spin
  readout (the right column holds the distance and the speed).
- Legend "same tray, 3 deg a second, real time" (the brief's "same
  tray, tilting 3 deg a second, real time" shortened).
- Card line 2 "the marble, at 5.6 deg; the dice at 26.7", line 3 "dice
  slides from 21.8 deg, tan = grip 0.4", line 4 "grip 0.2 leaves at
  16.3 deg, 0.6 at 35.7" (shortened to fit 950 px).
- The "starts to slide" ray and label are hidden while the tray is flat
  (before the tilt begins) and dim until the slide start, then gold.
- The marble rolls uphill by 1.2 nm for the first 2.1 ms (the
  centrifugal push beats g sin(theta) while the tray is still flat);
  printed, not asserted away. The dice never moves uphill (asserted).

## Niche note

Appended to the "Tilting tray, marble or dice" bullet in docs/niche.md:
[produced 2026-10-07 as "Marble or dice on a tilting tray: which one
goes first? The marble at 5.6 deg, the dice at 26.7 deg"; measured the
marble off the edge at 1.8726 s, 5.6179 deg, 0.6415 m/s (closed form
1.8707 s, 5.6121 deg; grip needed 0.0281), the dice sliding from 21.80
deg at 7.267 s and off at 8.8910 s, 26.6729 deg, 0.7441 m/s (N / W
never below 0.8856; with the Coriolis term on N reversed, the planning
convention, 8.9095 s, 26.7286 deg), margin 7.02 s and 21.06 deg, grips
0.2 / 0.3 / 0.5 / 0.6 off at 16.28 / 21.63 / 31.37 / 35.70 deg, rates 1
/ 2 / 5 deg/s marble 2.70 / 4.29 / 7.91 against dice 24.15 / 25.52 /
28.64 deg, ice cube 5.02, cylinder 5.75, hollow ball 5.95, ring 6.33
deg, radius 5 or 20 mm unchanged; RK4 dt 1e-4 s in the tray frame, 29
checks, 9 failed on the Coriolis sign (13 of 13 under the planning
sign); task 20261007-102006]

## Upload

- Attempt 1 of 5 (quota day 2026-10-07T10:00 EEST) recorded at 2026-10-07T10:56:45+03:00 before scripts/yt-upload.py tray; zero earlier attempts since the boundary.
- Uploaded private as Ccobr2TekTc at 2026-10-07T07:56:52Z (videos.insert 1,600 units). yt-qa.py --wait --publish: gate 15 of 15 on the first processed read, published at 2026-10-07T10:57:52+03:00, re-read public, 55 units. https://youtu.be/Ccobr2TekTc
