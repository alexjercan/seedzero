# Produce short: fingers under a ruler, slide two fingers together under a ruler beside a hammer stick, where do they meet

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day38

## Goal

Backlog idea (trend research 2026-10-05, task 20261005-100712, pillar 2
chaos and physics, everyday mechanics; read the full "Fingers under a
ruler" bullet under "Added by trend research 2026-10-05" in docs/niche.md):
slide two fingers together under a ruler and under a hammer-like stick;
where do they meet?

Orchestrator notes (2026-10-06; closed forms in /tmp/day38/closed-fix.py
with the log /tmp/day38/closed-fix.log, the "fingers, start 5 cm and 90
cm" section is the model; g = 9.807 m/s^2, the weight W cancels). Read
/tmp/day38/producer-conventions.md first. The model: a stick of length 1
m rests level on two finger pads 1.5 cm wide, the left pad's centre at 5
cm and the right pad's centre at 90 cm from the left end (asymmetric on
purpose, so no tie; say so). Grip between the pads and the stick: static
0.4, sliding 0.3 (chosen; say so). With x_left and x_right the pads'
distances from the stick's balance point, the loads are N_left = W
x_right / (x_left + x_right) and N_right = W x_left / (x_left + x_right)
(the finger nearer the balance point carries more). Exactly one finger
slips at a time: the finger carrying less weight (the one farther from
the balance point) slides under the stick at 10 cm/s while the other
holds; the stick stays still in the model (the gripping finger holds it;
in your hands the stick drifts along with the gripping finger instead,
and the meeting point is the same: say so in the description). The
sliding finger's friction 0.3 N_slip is balanced by the holding finger's
static friction, which can reach 0.4 N_hold; the slide ends when 0.3
N_slip = 0.4 N_hold, that is when the slider's distance from the balance
point is 0.3 / 0.4 = 0.75 of the holder's; then they swap. The fingers
have met when the pad centres are 1.5 cm apart (the pads touch); the
balance point then lies between them. Because exactly one finger moves
at any instant, the total time is (85 cm - 1.5 cm) / 10 cm/s = 8.350 s in
every case. Top band: the RULER, uniform, balance point at 50 cm: start
loads left 0.4706 W (45 cm from the middle), right 0.5294 W (40 cm), so
the left finger slips first: it slides 15.00 cm to 20.0 cm (t 1.500 s),
then the right slides 17.50 cm to 72.5 cm (3.250 s), the left 13.13 cm to
33.13 cm (4.563 s), the right 9.84 cm to 62.66 cm (5.547 s), the left
7.38 cm to 40.51 cm (6.285 s), the right 5.54 cm to 57.12 cm (6.839 s),
the left 4.15 cm to 44.66 cm (7.254 s), the right 3.11 cm to 54.00 cm
(7.566 s), and so on, 15 slips, meeting at 49.21 and 50.71 cm (centre
49.96 cm) at 8.350 s; during the slips the loads alternate 0.5714 W on
the holder and 0.4286 W on the slider. Bottom band: the HAMMER STICK,
its balance point 20 cm from the head end (the head on the left; draw a
heavy head and a thin handle whose combined balance point is at 20 cm,
and print the drawn shape's balance point as a check): start loads left
0.8235 W (15 cm from the balance point), right 0.1765 W (70 cm), so the
right finger slips first and slides 58.75 cm to 31.25 cm (t 5.875 s),
then the left 6.56 cm to 11.56 cm (6.531 s), the right 4.92 cm to 26.33
cm (7.023 s), the left 3.69 cm to 15.25 cm (7.393 s), the right 2.77 cm
to 23.56 cm (7.669 s), the left 2.08 cm to 17.33 cm (7.877 s), the right
1.56 cm to 22.00 cm (8.033 s), the left 1.17 cm to 18.50 cm (8.150 s),
and so on, 11 slips, meeting at 19.16 and 20.66 cm (centre 19.91 cm) at
8.350 s. Simulate the slip sequence as an event-driven Coulomb model
(the slider moves at 10 cm/s; at each step test the swap condition;
locate each swap exactly) and print every slip (which finger, how far,
until when, both positions, both loads), the meeting positions and
centre, the slip count, the total time, the force balance at each swap
(0.3 N_slip = 0.4 N_hold), and the description variants.

Checks, not facts (the sim must print and compare; state them as checks):
ruler: 15 slips, meet at 49.21 / 50.71 cm (centre 49.96 cm) at 8.350 s;
first four swaps at 20.0 cm (1.500 s), 72.5 cm (3.250 s), 33.13 cm
(4.563 s), 62.66 cm (5.547 s); hammer: 11 slips, meet at 19.16 / 20.66
cm (centre 19.91 cm) at 8.350 s; the right finger slides 58.75 cm first
until 5.875 s, then 11.56 cm (6.531 s), 26.33 cm (7.023 s), 15.25 cm
(7.393 s); loads at the swaps 0.5714 against 0.4286 W (the slider stops
when its distance is 0.75 of the holder's); for the description: grips
0.5 / 0.45 give 39 slips on the ruler (first swap at 14.0 cm, 0.900 s),
grips 0.6 / 0.3 give 7 slips on the ruler (first swap at 30.0 cm, 2.500
s) and 5 on the hammer (the right finger sliding 62.50 cm first), 5 cm/s
gives the same positions in 16.700 s, a stick with its balance point at
30 cm gives 13 slips meeting at 29.21 / 30.71 cm; in every case the
fingers meet at the balance point. Print the schedule in video time, the
text widths and the layout clearances.

Drawing: two-band layout (sims/deskchain style; sims/broom draws a
fingertip, sims/hingedstick and sims/sweetspot draw a stick with marks;
read deskchain whole and the fingertip drawing of broom), side view, the
ruler on top and the hammer stick below; same scale, same clock. The
stick is level at 800 px per metre (from x 140 to 940; the hammer head
may rise above the stick's line but must stay under the readout rows):
the ruler a 1 m bar with ticks every 10 cm and small numbers every 20 cm
(24 px; measure them), the hammer a heavy head on the left and a thin
handle. Two finger pads below the stick (left teal, right coral), 1.5 cm
= 12 px wide, drawn as rounded fingertips; the slipping finger shows
motion (a small trail or a brighter outline) and the holding finger is
dim. Under each pad a load bar (its share of the weight, 0 to 1, with
"NN% of the weight" in 24 px). A gold mark at the balance point revealed
at the meeting with "balance point" (24 px), and a dashed gold mark for
the first swap position in the hammer band. Label rows (40 px,
coloured): "a 1 m ruler" (teal) and "a hammer, heavy end left" (coral).
Readouts (28 px): left column "left finger: NN.N cm" and the clock; right
column "right finger: NN.N cm" and "slips: N". Gold event rows: top
"ruler: they meet at 50 cm, the middle" (lit at the meeting and held),
bottom "hammer: they meet at 20 cm, the balance point" (lit and held;
measure both, shorten if over 950 px). Shown at real speed; cycle 10 s
(600 frames): the fingers start moving 0.4 s into the cycle, the ruler's
first swap at 1.90 s, the hammer's first swap at 6.275 s, both meetings
at 0.4 + 8.350 = 8.75 s, hold, reset by a crossfade over the last 0.6 s
of the cycle (from 9.4 s); 4 cycles in 40 s, exactly periodic, the last
frame equal to the first. If the hold is too short to read, use a
13.333 s cycle (800 frames, 3 cycles) instead and say so. The legend
row after the title: "same fingers, same grip, real time"; the shared
clock in seconds since the fingers started. Overlay: "fingers at 10
cm/s, grip 0.4 / 0.3 | no seed" (measure it; shorten if over 950 px).

Day thirty-eight, third slot. Chosen because "where do they meet" is a
classroom trick with a live debate (the Science World and Scientific
American hammer-ruler trick), the two panels end visibly differently
(fingers together in the middle of the ruler, fingers together near the
hammer's head), the alternating slips are the visible mechanism, the
answer is exact and the repeat is a natural loop. Question in the first
two seconds: "Slide two fingers together under a ruler. So where do they
meet?" (pre-test; never start a sentence with "Where" after a full stop,
whisper doubled it on 2026-09-16 and heard "for" on 2026-09-22; a
question-first form "Where do two fingers meet under a ruler?" lands at
0.6 s). Keep the question identical in the title, the hook and the
payoff. Setup number: "one meter" (the ruler) or "ten centimeters a
second"; one setup number only. Payoff: at the balance point, every
time: fifty centimeters on the ruler, twenty centimeters from the head
on the hammer (the two panel results; say "centimeters" once if you can,
whisper heard it as "cm" three times on 2026-10-05, or put a verb right
after each number). The mechanism sentence must follow the picture: the
finger carrying less weight slips; as it slides in it takes on more
weight, until the other finger slips instead; they take turns, and the
turns shrink toward the balance point (the load bars and the alternating
motion show exactly this). Whisper risks: "ruler" (pre-test), "hammer"
(pre-test), "fingers" and "finger" (pre-test; "on a fingertip" came back
"and a fingertip"), "slips" and "slides" (pre-test), "balance point"
(pre-test), "take turns" (pre-test), avoid "do you", avoid "too", avoid
"pull". Pre-test hooks with scripts/voiceover.sh and keep the one whose
question lands earliest under two seconds. Measure every fixed text line
with PIL before rendering and keep every line under 950 px, and the
title under 100 characters with no < or >. Music seed 117. Templates:
sims/deskchain (two-band layout, asserts, the clock, the crossfade; read
it whole), sims/broom (fingertip drawing), sims/hingedstick and
sims/sweetspot (a stick with marks), sims/carrystop (an event-driven
stop). Sim name fingers: sims/fingers/fingers.py, projects/fingers/,
media/fingers/.

## Claim (expected; the sim's numbers replace these)

A 1 m ruler rests on two fingers at 5 and 90 cm; the fingers slide
toward each other at 10 cm/s, one slipping at a time (grip 0.4 at rest,
0.3 sliding). The finger carrying less weight slips until its distance
from the balance point is three quarters of the other's, then they swap:
15 slips, and the fingers meet at 49.2 and 50.7 cm, the middle, at 8.35
s. Under a hammer-like stick with its balance point 20 cm from the head
the right finger slides 58.8 cm before the first swap, then 10 more
slips bring them together at 19.2 and 20.7 cm, the balance point, at
8.35 s. Narrated: one meter (setup); fifty centimeters against twenty
centimeters from the head (payoff). Card: the question; the answer with
50 and 20 cm; 15 and 11 slips; the slider stops at 3/4 of the other's
distance; the first hammer slide 58.8 cm; grips 0.6 / 0.3: 7 and 5
slips, same meeting. Description: the model statement, the load
formula, the slip rule, the two runs, the grip, speed and balance-point
variants, the checks.

## Claim

A 1 m ruler rests on two finger pads 1.5 cm wide, their centres at 5 and
90 cm; the fingers slide toward each other at 10 cm/s, exactly one
slipping at a time (grip 0.4 at rest, 0.3 sliding; the stick stays still
in the model). The finger carrying less weight slips until its distance
from the balance point is 0.75 of the other's, then they swap: 15 slips,
and the fingers meet at 49.21 and 50.71 cm (centre 49.96 cm), the
middle, at 8.350 s. Under a hammer-like stick with its balance point 20
cm from the head the right finger slides 58.75 cm before the first swap
(5.875 s), then 10 more slips bring them together at 19.16 and 20.66 cm
(centre 19.91 cm), the balance point, at 8.350 s. At every swap the
loads are 0.5714 W on the finger that just slid in and 0.4286 W on the
one about to slide (0.3 x 0.5714 = 0.4 x 0.4286 = 0.1714 W). Narrated:
one meter (setup); at the balance point, fifty centimeters on the ruler,
twenty from the head of the hammer (payoff). Card: the question; at the
balance point: 50 cm and 20 cm; 15 and 11 slips, both done in 8.35 s; a
slide ends at 3/4 of the other's distance; hammer: the first slide is
58.75 cm long; grip 0.6 / 0.3: 7 and 5 slips, same spots.

## Evidence

### Measurements

Sim: sims/fingers/fingers.py with projects/fingers/manifest.json
(event-driven Coulomb slips stepped at dt = 1e-4 s, the swap and meeting
conditions tested at each step, each event located by bisection inside
its step and compared with the closed form; deterministic, no seed, no
wall clock). Log: media/fingers/measure.log (exit 0; the full final log
follows).

Brief checks (the sim prints "checks against the brief (49 checks, 0
failed)"): ruler 15 slips (sim 15), meet at 49.21 / 50.71 cm (49.2127 /
50.7127), centre 49.96 cm (49.9627), 8.350 s (8.350); first four swaps
at 20.0 cm, 1.500 s (20.00, 1.500), 72.5 cm, 3.250 s (72.50, 3.250),
33.13 cm, 4.563 s (33.125, 4.5625), 62.66 cm, 5.547 s (62.6562,
5.54688); hammer 11 slips (11), meet at 19.16 / 20.66 cm (19.1553 /
20.6553), centre 19.91 cm (19.9053), 8.350 s (8.350); the right finger
slides 58.75 cm first until 5.875 s (58.75 cm to 31.25 cm at 5.875 s),
then 11.56 cm, 6.531 s (11.5625, 6.53125), 26.33 cm, 7.023 s (26.3281,
7.02344), 15.25 cm, 7.393 s (15.2539, 7.39258); loads at the swaps
0.5714 against 0.4286 W (0.571429 / 0.428571) with the slider stopping
at 0.75 of the holder's distance (0.7500 at every swap); start loads
ruler 0.4706 / 0.5294 W (0.470588 / 0.529412), hammer 0.8235 / 0.1765 W
(0.823529 / 0.176471); grips 0.5 / 0.45: 39 slips on the ruler, first
swap at 14.0 cm, 0.900 s (39, 14.0, 0.900); grips 0.6 / 0.3: 7 slips on
the ruler, first swap at 30.0 cm, 2.500 s (7, 30.0, 2.500) and 5 under
the hammer with the right finger sliding 62.50 cm first (5, 62.50);
5 cm/s: the same positions in 16.700 s (15 slips, same positions yes,
16.700 s, 49.21 / 50.71 cm); balance point at 30 cm: 13 slips meeting at
29.21 / 30.71 cm (13, 29.2081 / 30.7081); in every case the fingers meet
at the balance point (the gap's centre within 0.75 cm of it in all seven
runs, the farthest 0.19 cm for the hammer at grips 0.6 / 0.3); the drawn
hammer's balance point 20.00 cm from the head end (closed form and 2x
pixel mask, diff 0). Also printed: every event within 2.8e-17 m of its
closed form (83506 and 83504 steps); the force balance at every swap
0.3 x 0.5714 = 0.4 x 0.4286 = 0.1714 W (diff at most 8.3e-17); the total
time (90 - 5 - 1.5) cm / 10 cm/s = 8.350 s in every run; the hammer
variant at grips 0.5 / 0.45 (29 slips, the right finger 56.50 cm first);
the schedule; the text widths (every line under 950 px, max 941 px for
payoff line 1 and 939 px for payoff line 4) and the layout clearances.

Final measure.log:

```
Tue Oct  6 10:34:27 AM EEST 2026
setup: side view, two panels on one clock at the same scale: a stick of 1 m rests level on two finger pads 1.5 cm wide, the left pad's centre at 5 cm and the right pad's centre at 90 cm from the left end (asymmetric on purpose, so there is no tie); grip between the pads and the stick: static 0.4, sliding 0.3 (chosen); with x_left and x_right the pads' distances from the balance point the loads are N_left = W x_right / (x_left + x_right) and N_right = W x_left / (x_left + x_right) (the finger nearer the balance point carries more; the weight W cancels, g = 9.807 m/s^2 never enters); exactly one finger slips at a time: the finger carrying less weight slides under the stick at 10 cm/s while the other holds and the stick stays still (in your hands the stick drifts along with the gripping finger instead; the meeting point is the same); the slide ends when 0.3 N_slip = 0.4 N_hold, that is when the slider's distance from the balance point is 0.3 / 0.4 = 0.7500 of the holder's; then they swap; the fingers have met when the pad centres are 1.5 cm apart; top panel a uniform ruler with its balance point at 50 cm, bottom panel a hammer-like stick with its balance point 20 cm from the head end (the head on the left); event-driven Coulomb model stepped at 10000 steps per second (dt = 1e-04 s), each swap located by bisection inside its step and checked against the closed form; total time (90 - 5 - 1.5) cm / 10 cm/s = 8.350 s in every case because exactly one finger moves at any instant; shown at real speed on a 13.3333 s cycle (800 frames) with the fingers starting 0.4 s into the cycle, 3 cycles in 40 s; drawn at 800 px per metre; deterministic, no seed
start loads: ruler left (45 cm from the middle) 0.4706 W, right (40 cm) 0.5294 W: the left finger slips first; hammer left (15 cm from the balance point) 0.8235 W, right (70 cm) 0.1765 W: the right finger slips first
ruler, balance point 50 cm (top panel): fingers meet at 49.21 / 50.71 cm (centre 49.96 cm, 0.04 cm from the balance point, inside the 1.5 cm gap) after 15 slips and 8.350 s at 10 cm/s, final gap 1.5 cm; 83506 steps, every event within 2.8e-17 m of its closed form
   slip 1: left finger slid 15.00 cm until t 1.500 s: fingers at 20.00 and 90.00 cm; loads left 0.5714 W, right 0.4286 W; swap: 0.3 x 0.5714 = 0.1714 W = 0.4 x 0.4286 = 0.1714 W (diff +0.0e+00), the slider's distance 0.7500 of the holder's
   slip 2: right finger slid 17.50 cm until t 3.250 s: fingers at 20.00 and 72.50 cm; loads left 0.4286 W, right 0.5714 W; swap: 0.3 x 0.5714 = 0.1714 W = 0.4 x 0.4286 = 0.1714 W (diff +0.0e+00), the slider's distance 0.7500 of the holder's
   slip 3: left finger slid 13.13 cm until t 4.563 s: fingers at 33.13 and 72.50 cm; loads left 0.5714 W, right 0.4286 W; swap: 0.3 x 0.5714 = 0.1714 W = 0.4 x 0.4286 = 0.1714 W (diff +2.8e-17), the slider's distance 0.7500 of the holder's
   slip 4: right finger slid 9.84 cm until t 5.547 s: fingers at 33.13 and 62.66 cm; loads left 0.4286 W, right 0.5714 W; swap: 0.3 x 0.5714 = 0.1714 W = 0.4 x 0.4286 = 0.1714 W (diff +2.8e-17), the slider's distance 0.7500 of the holder's
   slip 5: left finger slid 7.38 cm until t 6.285 s: fingers at 40.51 and 62.66 cm; loads left 0.5714 W, right 0.4286 W; swap: 0.3 x 0.5714 = 0.1714 W = 0.4 x 0.4286 = 0.1714 W (diff +5.6e-17), the slider's distance 0.7500 of the holder's
   slip 6: right finger slid 5.54 cm until t 6.839 s: fingers at 40.51 and 57.12 cm; loads left 0.4286 W, right 0.5714 W; swap: 0.3 x 0.5714 = 0.1714 W = 0.4 x 0.4286 = 0.1714 W (diff +2.8e-17), the slider's distance 0.7500 of the holder's
   slip 7: left finger slid 4.15 cm until t 7.254 s: fingers at 44.66 and 57.12 cm; loads left 0.5714 W, right 0.4286 W; swap: 0.3 x 0.5714 = 0.1714 W = 0.4 x 0.4286 = 0.1714 W (diff +2.8e-17), the slider's distance 0.7500 of the holder's
   slip 8: right finger slid 3.11 cm until t 7.566 s: fingers at 44.66 and 54.00 cm; loads left 0.4286 W, right 0.5714 W; swap: 0.3 x 0.5714 = 0.1714 W = 0.4 x 0.4286 = 0.1714 W (diff -5.6e-17), the slider's distance 0.7500 of the holder's
   slip 9: left finger slid 2.34 cm until t 7.799 s: fingers at 47.00 and 54.00 cm; loads left 0.5714 W, right 0.4286 W; swap: 0.3 x 0.5714 = 0.1714 W = 0.4 x 0.4286 = 0.1714 W (diff -2.8e-17), the slider's distance 0.7500 of the holder's
   slip 10: right finger slid 1.75 cm until t 7.974 s: fingers at 47.00 and 52.25 cm; loads left 0.4286 W, right 0.5714 W; swap: 0.3 x 0.5714 = 0.1714 W = 0.4 x 0.4286 = 0.1714 W (diff -5.6e-17), the slider's distance 0.7500 of the holder's
   slip 11: left finger slid 1.31 cm until t 8.106 s: fingers at 48.31 and 52.25 cm; loads left 0.5714 W, right 0.4286 W; swap: 0.3 x 0.5714 = 0.1714 W = 0.4 x 0.4286 = 0.1714 W (diff +0.0e+00), the slider's distance 0.7500 of the holder's
   slip 12: right finger slid 0.99 cm until t 8.204 s: fingers at 48.31 and 51.27 cm; loads left 0.4286 W, right 0.5714 W; swap: 0.3 x 0.5714 = 0.1714 W = 0.4 x 0.4286 = 0.1714 W (diff -2.8e-17), the slider's distance 0.7500 of the holder's
   slip 13: left finger slid 0.74 cm until t 8.278 s: fingers at 49.05 and 51.27 cm; loads left 0.5714 W, right 0.4286 W; swap: 0.3 x 0.5714 = 0.1714 W = 0.4 x 0.4286 = 0.1714 W (diff +0.0e+00), the slider's distance 0.7500 of the holder's
   slip 14: right finger slid 0.55 cm until t 8.334 s: fingers at 49.05 and 50.71 cm; loads left 0.4286 W, right 0.5714 W; swap: 0.3 x 0.5714 = 0.1714 W = 0.4 x 0.4286 = 0.1714 W (diff -2.8e-17), the slider's distance 0.7500 of the holder's
   slip 15: left finger slid 0.16 cm until t 8.350 s: fingers at 49.21 and 50.71 cm; loads left 0.4751 W, right 0.5249 W; the pads touch
hammer stick, balance point 20 cm from the head end (bottom panel): fingers meet at 19.16 / 20.66 cm (centre 19.91 cm, 0.09 cm from the balance point, inside the 1.5 cm gap) after 11 slips and 8.350 s at 10 cm/s, final gap 1.5 cm; 83504 steps, every event within 1.4e-17 m of its closed form
   slip 1: right finger slid 58.75 cm until t 5.875 s: fingers at 5.00 and 31.25 cm; loads left 0.4286 W, right 0.5714 W; swap: 0.3 x 0.5714 = 0.1714 W = 0.4 x 0.4286 = 0.1714 W (diff -8.3e-17), the slider's distance 0.7500 of the holder's
   slip 2: left finger slid 6.56 cm until t 6.531 s: fingers at 11.56 and 31.25 cm; loads left 0.5714 W, right 0.4286 W; swap: 0.3 x 0.5714 = 0.1714 W = 0.4 x 0.4286 = 0.1714 W (diff -2.8e-17), the slider's distance 0.7500 of the holder's
   slip 3: right finger slid 4.92 cm until t 7.023 s: fingers at 11.56 and 26.33 cm; loads left 0.4286 W, right 0.5714 W; swap: 0.3 x 0.5714 = 0.1714 W = 0.4 x 0.4286 = 0.1714 W (diff +0.0e+00), the slider's distance 0.7500 of the holder's
   slip 4: left finger slid 3.69 cm until t 7.393 s: fingers at 15.25 and 26.33 cm; loads left 0.5714 W, right 0.4286 W; swap: 0.3 x 0.5714 = 0.1714 W = 0.4 x 0.4286 = 0.1714 W (diff +5.6e-17), the slider's distance 0.7500 of the holder's
   slip 5: right finger slid 2.77 cm until t 7.669 s: fingers at 15.25 and 23.56 cm; loads left 0.4286 W, right 0.5714 W; swap: 0.3 x 0.5714 = 0.1714 W = 0.4 x 0.4286 = 0.1714 W (diff -2.8e-17), the slider's distance 0.7500 of the holder's
   slip 6: left finger slid 2.08 cm until t 7.877 s: fingers at 17.33 and 23.56 cm; loads left 0.5714 W, right 0.4286 W; swap: 0.3 x 0.5714 = 0.1714 W = 0.4 x 0.4286 = 0.1714 W (diff -2.8e-17), the slider's distance 0.7500 of the holder's
   slip 7: right finger slid 1.56 cm until t 8.033 s: fingers at 17.33 and 22.00 cm; loads left 0.4286 W, right 0.5714 W; swap: 0.3 x 0.5714 = 0.1714 W = 0.4 x 0.4286 = 0.1714 W (diff +2.8e-17), the slider's distance 0.7500 of the holder's
   slip 8: left finger slid 1.17 cm until t 8.150 s: fingers at 18.50 and 22.00 cm; loads left 0.5714 W, right 0.4286 W; swap: 0.3 x 0.5714 = 0.1714 W = 0.4 x 0.4286 = 0.1714 W (diff +2.8e-17), the slider's distance 0.7500 of the holder's
   slip 9: right finger slid 0.88 cm until t 8.237 s: fingers at 18.50 and 21.13 cm; loads left 0.4286 W, right 0.5714 W; swap: 0.3 x 0.5714 = 0.1714 W = 0.4 x 0.4286 = 0.1714 W (diff -5.6e-17), the slider's distance 0.7500 of the holder's
   slip 10: left finger slid 0.66 cm until t 8.303 s: fingers at 19.16 and 21.13 cm; loads left 0.5714 W, right 0.4286 W; swap: 0.3 x 0.5714 = 0.1714 W = 0.4 x 0.4286 = 0.1714 W (diff -2.8e-17), the slider's distance 0.7500 of the holder's
   slip 11: right finger slid 0.47 cm until t 8.350 s: fingers at 19.16 and 20.66 cm; loads left 0.4369 W, right 0.5631 W; the pads touch
hammer shape: a head 10 cm long and 7 cm tall at the left end (80 px) with 6 times the handle's density, a handle 2 cm tall to the right end; areas 70 and 180 cm^2; balance point of the drawn shape 20.00 cm from the head end (closed form), 20.00 cm from the 2x pixel mask it is drawn from (diff +0.0e+00 cm); the model's 20 cm
for the description: ruler, grips 0.5 / 0.45: 39 slips, the left finger slides 9.00 cm first to 14.0 cm (0.900 s), meeting at 49.23 / 50.73 cm (centre 49.98 cm) at 8.350 s; hammer, grips 0.5 / 0.45: 29 slips, the right finger slides 56.50 cm first to 33.5 cm (5.650 s), meeting at 19.21 / 20.71 cm (centre 19.96 cm) at 8.350 s; ruler, grips 0.6 / 0.3: 7 slips, the left finger slides 25.00 cm first to 30.0 cm (2.500 s), meeting at 49.12 / 50.62 cm (centre 49.88 cm) at 8.350 s; hammer, grips 0.6 / 0.3: 5 slips, the right finger slides 62.50 cm first to 27.5 cm (6.250 s), meeting at 19.06 / 20.56 cm (centre 19.81 cm) at 8.350 s; ruler at 5 cm/s: 15 slips, the same positions (yes), meeting at 49.21 / 50.71 cm at 16.700 s; a stick with its balance point at 30 cm: 13 slips, the right finger slides 41.25 cm first, meeting at 29.21 / 30.71 cm (centre 29.96 cm) at 8.350 s; in every case the fingers meet at the balance point (the gap's centre within 0.75 cm of it: yes)
checks against the brief (49 checks, 0 failed): ruler slips: brief 15, sim 15, diff +0.0e+00: ok; ruler meet left (cm): brief 49.21, sim 49.2127, diff +2.7e-03: ok; ruler meet right (cm): brief 50.71, sim 50.7127, diff +2.7e-03: ok; ruler meet centre (cm): brief 49.96, sim 49.9627, diff +2.7e-03: ok; ruler total time (s): brief 8.35, sim 8.35, diff +0.0e+00: ok; hammer slips: brief 11, sim 11, diff +0.0e+00: ok; hammer meet left (cm): brief 19.16, sim 19.1553, diff -4.7e-03: ok; hammer meet right (cm): brief 20.66, sim 20.6553, diff -4.7e-03: ok; hammer meet centre (cm): brief 19.91, sim 19.9053, diff -4.7e-03: ok; hammer total time (s): brief 8.35, sim 8.35, diff +0.0e+00: ok; ruler start load left (W): brief 0.4706, sim 0.470588, diff -1.2e-05: ok; ruler start load right (W): brief 0.5294, sim 0.529412, diff +1.2e-05: ok; hammer start load left (W): brief 0.8235, sim 0.823529, diff +2.9e-05: ok; hammer start load right (W): brief 0.1765, sim 0.176471, diff -2.9e-05: ok; slider stops at (of the holder's distance): brief 0.75, sim 0.75, diff -1.1e-16: ok; ruler swap 1 position (cm): brief 20, sim 20, diff +0.0e+00: ok; ruler swap 1 time (s): brief 1.5, sim 1.5, diff +2.2e-16: ok; ruler swap 2 position (cm): brief 72.5, sim 72.5, diff +0.0e+00: ok; ruler swap 2 time (s): brief 3.25, sim 3.25, diff +8.9e-16: ok; ruler swap 3 position (cm): brief 33.13, sim 33.125, diff -5.0e-03: ok; ruler swap 3 time (s): brief 4.563, sim 4.5625, diff -5.0e-04: ok; ruler swap 4 position (cm): brief 62.66, sim 62.6562, diff -3.8e-03: ok; ruler swap 4 time (s): brief 5.547, sim 5.54688, diff -1.2e-04: ok; hammer first slide (cm): brief 58.75, sim 58.75, diff -7.1e-15: ok; hammer first slide finger is right: brief 1, sim 1, diff +0.0e+00: ok; hammer swap 1 position (cm): brief 31.25, sim 31.25, diff +7.1e-15: ok; hammer swap 1 time (s): brief 5.875, sim 5.875, diff -8.9e-16: ok; hammer swap 2 position (cm): brief 11.56, sim 11.5625, diff +2.5e-03: ok; hammer swap 2 time (s): brief 6.531, sim 6.53125, diff +2.5e-04: ok; hammer swap 3 position (cm): brief 26.33, sim 26.3281, diff -1.9e-03: ok; hammer swap 3 time (s): brief 7.023, sim 7.02344, diff +4.4e-04: ok; hammer swap 4 position (cm): brief 15.25, sim 15.2539, diff +3.9e-03: ok; hammer swap 4 time (s): brief 7.393, sim 7.39258, diff -4.2e-04: ok; holder load at a swap (W): brief 0.5714, sim 0.571429, diff +2.9e-05: ok; slider load at a swap (W): brief 0.4286, sim 0.428571, diff -2.9e-05: ok; ruler grips 0.5 / 0.45 slips: brief 39, sim 39, diff +0.0e+00: ok; ruler grips 0.5 / 0.45 first swap (cm): brief 14, sim 14, diff -1.1e-14: ok; ruler grips 0.5 / 0.45 first swap (s): brief 0.9, sim 0.9, diff -6.7e-16: ok; ruler grips 0.6 / 0.3 slips: brief 7, sim 7, diff +0.0e+00: ok; ruler grips 0.6 / 0.3 first swap (cm): brief 30, sim 30, diff +0.0e+00: ok; ruler grips 0.6 / 0.3 first swap (s): brief 2.5, sim 2.5, diff +0.0e+00: ok; hammer grips 0.6 / 0.3 slips: brief 5, sim 5, diff +0.0e+00: ok; hammer grips 0.6 / 0.3 first slide (cm): brief 62.5, sim 62.5, diff +0.0e+00: ok; ruler at 5 cm/s total time (s): brief 16.7, sim 16.7, diff +0.0e+00: ok; ruler at 5 cm/s meet left (cm): brief 49.21, sim 49.2127, diff +2.7e-03: ok; balance 30 cm slips: brief 13, sim 13, diff +0.0e+00: ok; balance 30 cm meet left (cm): brief 29.21, sim 29.2081, diff -1.9e-03: ok; balance 30 cm meet right (cm): brief 30.71, sim 30.7081, diff -1.9e-03: ok; drawn hammer balance point (cm): brief 20, sim 20, diff +0.0e+00: ok
schedule (video time, real speed): cycles of 13.3333 s start at -6.67, 6.67, 20.00, 33.33 s (the first 6.67 s before the first frame); the fingers start 0.4 s into each cycle at 7.067, 20.400, 33.733 s; the ruler's first swap at 8.567, 21.900, 35.233 s, its second at 10.317, 23.650, 36.983 s, its third at 11.629, 24.963, 38.296 s; the hammer's first swap at 12.942, 26.275, 39.608 s, its second at 0.265, 13.598, 26.931 s; both meetings 8.350 s after the start at 2.083, 15.417, 28.750 s (the gold balance marks and both event rows light); the met state holds 3.983 s; the reset crossfade runs over the last 0.6 s of each cycle (from 6.067, 19.400, 32.733 s; the readouts out over its first half and in over its second); on the first frame the cycle is 6.67 s in (+6.267 s after the start: the ruler's fingers slide at 40.3 and 62.7 cm, the hammer's slide at 8.9 and 31.3 cm); title until 3 s; payoff card from 27.8 s; the title fades back in over the last 0.5 s and the last frame repeats the first (the scene is periodic: 40 s holds exactly 3 cycles)
text widths (the on-screen strings verbatim): overlay@34 801 px 'fingers at 10 cm/s, grip 0.4 / 0.3 | no seed', title line 1@56 680 px 'Where do two fingers', title line 2@56 628 px 'meet under a ruler?', legend@40 777 px 'same fingers, same grip, real time', clock@28 513 px '8.350 s since the fingers started', clock rest@28 225 px 'fingers at rest', label ruler@40 247 px 'a 1 m ruler', event ruler@40 849 px 'ruler: they meet at 50 cm, the middle', label hammer@40 574 px 'a hammer, heavy end left', event hammer@40 928 px 'hammer: they meet 20 cm from the head', left finger@28 303 px 'left finger: 49.2 cm', right finger@28 326 px 'right finger: 90.0 cm', state rest@28 187 px 'both at rest', state slide right@28 306 px 'sliding: right finger', state slide left@28 284 px 'sliding: left finger', state met@28 258 px 'fingers together', slips@28 132 px 'slips: 15', load@24 247 px '82% of the weight', load full@24 263 px '100% of the weight', ruler number 0@24 17 px '0', ruler number 20@24 33 px '20', ruler number 40@24 33 px '40', ruler number 60@24 33 px '60', ruler number 80@24 33 px '80', ruler number 100@24 50 px '100', balance@24 184 px 'balance point', first swap@24 134 px 'first swap', payoff line 1@40 941 px 'where do two fingers meet under a ruler?', payoff line 2@40 868 px 'at the balance point: 50 cm and 20 cm', payoff line 3@40 806 px '15 and 11 slips, both done in 8.35 s', payoff line 4@40 939 px 'a slide ends at 3/4 of the other's distance', payoff line 5@40 901 px 'hammer: the first slide is 58.75 cm long', payoff line 6@40 890 px 'grip 0.6 / 0.3: 7 and 5 slips, same spots'
row check: the left column ends at x 614 px, the right column starts at x 714 px; both end 136 px under the band top; the stick spans x 140 to 940 px with its underside 256 px under the band top (the ruler from 216 px, the hammer's handle from 240 px, its head from 200 px over x 140 to 220 px); the gold balance marks at x 540 (ruler) and 300 px (hammer) with their labels from 189 and 213 px under the band top to x 738 and 498 px; the pads hang from 256 to 336 px between x 174 and 866 px; the load bars at 352 to 368 px span x 48 to 945 px at their widest; the load labels at 374 to 398 px span x 40 to 1040 px at their widest (each at most 263 px wide); the hammer's dashed first-swap mark at x 390 px from 262 to 346 px with its label right of it to x 536 px at 262 to 286 px (inside the pad zone, crossed only by the right finger's first trail); the event row centred 480 px under the band top (460 to 500), widest 928 px; each band is 550 px tall (y 330 to 880 and 880 to 1430); the caption band starts at y 1440; the title rows end at y 280 and the overlay band ends at y 130
Tue Oct  6 10:34:28 AM EEST 2026
```

### Production

- Manifest: projects/fingers/manifest.json (fps 60, 40 s, real speed,
  cycle 13.333 s = 800 frames, fingers start 0.4 s into the cycle,
  first_cycle_at -6.667 s = -400 frames, reset crossfade 0.6 s, 800
  px/m with the stick from x 140 to 940, pads 1.5 cm = 12 px, hammer
  head 10 x 7 cm at 6 times the handle's density, handle 2 cm, title
  until 3 s, payoff_t 27.8 s, hold 0.6 s, loop fade 0.5 s, music seed
  117, music gain 0.18, voice offset 0.6, caption_y 0.75; description
  variants grips 0.5 / 0.45 and 0.6 / 0.3, 5 cm/s, balance point 30 cm).
- Layout: two bands y 330-880 (ruler, teal label) and 880-1430 (hammer,
  coral label); rows at 40 (label), 84 ("left finger: NN.N cm" left,
  "right finger: NN.N cm" right) and 120 ("sliding: left finger" /
  "both at rest" / "fingers together" left, "slips: N" right); the stick's
  underside 256 px under the band top (ruler 40 px thick with ticks every
  10 cm and 24 px numbers every 20 cm inside the bar; hammer handle 16 px,
  head 80 x 56 px flush with the underside); gold balance triangle and
  "balance point" (24 px) above the stick, revealed over 0.3 s at the
  meeting; pads 12 px wide capsules from 256 to 336 px (the slider bright
  with a white outline and a translucent trail from the slip's start, the
  holder dim); load bars at 352-368 px growing outward from the pads (160
  px = the whole weight) with "NN% of the weight" (24 px) under them,
  clamped inside x 40-1040; the hammer's dashed gold first-swap mark at x
  390 (31.25 cm) from 262 to 346 px with "first swap" (24 px) to its
  right; gold event rows centred 480 px under the band top: "ruler: they
  meet at 50 cm, the middle" (849 px) and "hammer: they meet 20 cm from
  the head" (928 px). Legend "same fingers, same grip, real time" at y
  236, shared clock "N.NNN s since the fingers started" at y 290 (frozen
  at 8.350 s once met). Columns end at x 614 and start at x 714.
- Schedule (video time): cycles start at -6.667, 6.667, 20.000, 33.333
  s; fingers start 7.067, 20.400, 33.733 s; ruler first swaps 8.567,
  21.900, 35.233 s; hammer first swaps 12.942, 26.275, 39.608 s; meetings
  2.083, 15.417, 28.750 s; the met state holds 3.983 s; crossfades from
  6.067, 19.400, 32.733 s. Frame 0: 6.267 s after the start, the ruler's
  fingers sliding at 40.3 and 62.7 cm (slip 5), the hammer's at 8.9 and
  31.3 cm (slip 2).
- Smoke frames viewed: media/fingers/smoke-{0.0,1.5,2.0,3.4,6.5,8.9,9.6,
  16.3,28.0,29.0}.png with the first 10 s layout (rest state under the
  title; the left finger sliding with its trail at 1.5 s; the swap state
  at 3.4 s; both bands mid-run at 6.5 s; the met state with both gold
  marks and event rows at 8.9 s; the crossfade at 9.6 s; the card at 28.0
  and 29.0 s). Two fixes from them: the "balance point" label touched
  the ruler's top (lifted 4 px) and the dashed first-swap line crossed
  the right load label (now ends at 346 px, label moved beside it);
  re-rendered smoke-6.5 and smoke-8.9 viewed clean.
- Hook pre-tests (media/fingers/hooks/pretest.log, all five passed the
  round trip): hook1 "Where do two fingers meet under a ruler? Slide them
  together and watch." (3.88 s), question at 0.60 s; hook2 "Slide two
  fingers together under a ruler. So where do they meet?" (3.63 s), no
  pause detected, the question after about 2.4 s; hook3 "Two fingers
  slide under a ruler. So where do they meet?" (3.11 s), question after
  about 2.2 s; hook4 "So where do two fingers meet under a ruler? Slide
  them in and watch." (3.95 s), 0.60 s; hook5 "Where do two fingers meet
  under a ruler? One slips at a time." (3.99 s), 0.60 s. Chosen: the
  question-first form (hook1's first sentence). Word test (words.txt,
  40.7 s, matched): "one meter ruler", "hammer, heavy end on the left",
  "Only one finger slides at a time", "slips instead", "They take
  turns", "balance point", "fifty centimeters on the ruler, twenty from
  the head of the hammer", "Fifty centimeters, the middle. Twenty
  centimeters from the head.", "Ten centimeters a second", "The turns
  shrink", "Fifteen slips. Eleven slips.", "So, where do two fingers meet
  under a ruler?" all matched.
- Narration: projects/fingers/narration.txt, 110 words; the question is
  the first sentence (spoken 0.60-2.9 s) and repeats before the payoff as
  "So, where do two fingers meet under a ruler?" (23.97-26.13 s). One
  setup number ("one meter"), the payoff numbers "fifty centimeters on
  the ruler, twenty from the head of the hammer" ("centimeters" once).
- Voice (media/fingers/voice.log): pass 1 (111 words, the 10 s cycle
  draft) ok 34.59 s; pass 2 (105 words, rewritten for the 13.333 s
  cycle) ok 32.82 s, but "At the balance point" landed at 26.3 s, 1.2 s
  before the third meeting; pass 3 (110 words, "Watch the last few
  slips." added) ok 34.18 s. No mishearing in any pass. Final voice ends
  at 34.78 s of video.
- Timing (media/fingers/timing.log, pass 3): question 0.60-2.9; "On top,
  a one meter ruler on two fingers" to 5.63; "Below, a hammer, heavy end
  on the left, only one finger slides at a time" 5.63-10.46 (run 2 starts
  7.067); "the finger carrying less weight, as it slides in, it takes on
  more weight, until the other finger slips instead" 10.46-17.71 (ruler
  swaps 10.32, 11.63, 12.60, 13.35; hammer swaps 12.94, 13.60, 14.09;
  meeting 15.42); "They take turns, and the turns shrink until the
  fingers touch" 17.71-20.10 (met state held to 19.4); "Under the
  hammer, the far finger slides a long way first" 20.10-23.97 (the hammer's
  right finger slides 20.40-26.275); "So, where do two fingers meet under
  a ruler?" 23.97-26.13; a finer split (silencedetect d=0.12) of the last
  chunk: "Watch the last few slips" 26.25-27.72, "at the balance point"
  27.89-28.85 (meeting 28.75), "fifty centimeters on the ruler"
  29.03-30.56, "twenty from the head of the hammer" 30.78-32.01, "same
  grip" 32.21-32.73 (hold ends 32.733), "same answer" 33.08-33.82, "every
  time" 34.06-34.78 (run 4 from 33.733). 13 silences at -35 dB / 0.22 s
  (media/fingers/silences.log).
- Render: media/fingers/render.log, footage.mp4 (2400 frames, 26 s wall
  time); loop check 0 px (max channel difference 0); periodicity check 0
  px; loop step 4762 px between the last two frames.
- Compose: media/fingers/compose.log: music seed 117, 40.00 s; captions
  21 pauses detected, 21 matched, max chunk start shift 0.770 s;
  final.mp4 40.000000 s.
- Text widths (measure.log): overlay 801 px; title rows 680 and 628 px at
  56 px; legend 777; event rows 849 and 928; payoff lines 941, 868, 806,
  939, 901, 890 px; all other lines under 530 px; every line under 950 px
  (asserted).

### Local QA

- media/fingers/final.mp4: md5 52899c7868b07e60d9bbf1c8b99278fe,
  4264431 bytes; ffprobe h264 1080x1920 60/1, aac 22050 Hz mono,
  duration 40.000000; moov at byte 36 before mdat at 44584 (faststart).
  footage.mp4: 40.000000 s, 2400 frames.
- Caption text against the narration: 39 drawtext chunks (the first is
  the overlay), the 38 captions joined equal the narration word for word
  (checked by script, the typographic apostrophe of captions.py aside;
  the narration has no apostrophe). The first caption "Where do two
  fingers" is enabled 0.802-1.777 s, "meet under a ruler?" 1.777-2.894;
  "At the balance" 27.893-28.609, "Fifty centimeters on" 29.032-29.949,
  "the ruler, twenty" 29.949-30.955; the last caption ends 34.780 s.
- Question timing: on screen from frame 0 (title rows at y 190 and 252)
  and spoken from 0.60 s (voice start plus the 0.6 s offset).
- signalstats YMAX on footage.mp4: caption band rows 1440-1530 = 28
  (background), overlay band rows 96-130 = 28: nothing drawn under the
  captions or the overlay.
- Full-resolution frames viewed (media/fingers/qa-T.png): 0.00 overlay,
  two-row title, the ruler's left finger sliding at 40.3 cm with its
  trail (slips 4) and the hammer's left finger at 8.9 cm (slips 1), load
  bars 57/43 and 50/50 percent, no caption; 1.0 ruler 44.7/57.0 cm slips
  7, hammer 14.0/26.3 slips 3, caption "Where do two fingers"; 2.1 both
  pairs together (49.2/50.7 and 19.2/20.7), "fingers together", slips 15
  and 11, both gold event rows lit, the balance marks just starting to
  fade in, caption "meet under a ruler?"; 11.0 legend and clock 3.933 s,
  ruler 26.8/72.5 slips 2 with the left finger's trail, the hammer's
  right finger at 50.7 cm with its long trail from 90 cm, caption "the
  finger carrying"; 28.2 clock 7.800 s, ruler 47.0/54.0 slips 9, hammer
  16.6/23.6 slips 5, caption "At the balance", the card rising (dim
  gold); 29.6 met state, clock 8.350 s, gold triangles with "balance
  point" at 50 and 20 cm, both event rows, 48/52 and 44/56 percent,
  caption "Fifty centimeters on", card full; 31.0 same met state, caption
  "from the head of the"; 39.983 identical to frame 0 (title back, no
  caption, same readouts 40.3/62.7 and 8.9/31.3). media/fingers/sheet.png
  viewed: 40 cells, the captions in order from "Where do two fingers" to
  "answer, every time.", the met state in cells 3-7, 16-20 and 29-33, the
  card from cell 29, no clipping at the frame edges.
- Loop: last frame equals the first (0 px, max channel difference 0).
- Narrated numbers: "one meter" (manifest stick_m 1.0, log "a stick of
  1 m"), "fifty centimeters on the ruler" (log "centre 49.96 cm", event
  row "they meet at 50 cm"), "twenty from the head of the hammer" (log
  "centre 19.91 cm", "balance point 20 cm from the head end"). The
  description's 85 numbers checked by script against measure.log
  (commas stripped): all present.

### Metadata

projects/fingers/metadata.json written by a Python script with asserts
(title 94 chars, description 3776 chars, 12 tags, ASCII, no < or >;
every description number present in measure.log), then confirmed with
ls -l (4342 bytes). Title: "Where do two fingers meet under a ruler? At
the balance point: 50 cm, and 20 cm under a hammer". Tags: where do two
fingers meet under a ruler, fingers under a ruler, hammer ruler trick,
balance point, center of mass, friction, physics, physics visualization,
simulation, shorts, classroom physics, mechanics. privacyStatus private,
categoryId 27, containsSyntheticMedia true, selfDeclaredMadeForKids
false.

### Deviations from the brief

- Cycle 13.333 s (800 frames, 3 cycles) instead of 10 s: with the 10 s
  cycle the met state held only 0.65 s before the fade, too short to read
  the event rows and to speak both payoff numbers; the brief allows this
  switch. first_cycle_at -6.667 s so that the third meeting lands at
  28.750 s under "at the balance point" and both payoff numbers are
  spoken while the fingers are together (hold to 32.733 s); frame 0 then
  shows the run 6.267 s in (motion already in progress) and the first
  meeting at 2.083 s under the question. The brief's video times (fingers
  start 0.4 s, first swaps 1.90 and 6.275 s, meetings 8.75 s) become
  7.067 / 20.400 / 33.733, 8.567 / 12.942 and 2.083 / 15.417 / 28.750 s.
- Bottom event row "hammer: they meet 20 cm from the head" (the brief's
  "hammer: they meet at 20 cm, the balance point" measured 1079 px).
- Third readout row: "sliding: left finger" / "sliding: right finger" /
  "both at rest" / "fingers together" instead of a per-band clock; the
  shared clock at y 290 carries the time.
- Load bars grow outward from the pads (the left finger's leftward, the
  right finger's rightward, 160 px for the whole weight) so they never
  overlap at the meeting; the "NN% of the weight" labels sit under the
  bars, clamped inside x 40-1040, so at the extreme positions they are
  near, not exactly under, the pad.
- The dashed first-swap mark ends above the load bars (y 262-346 band
  local) with a "first swap" label to its right; the "balance point"
  label sits right of the gold triangle above the stick.
- Ruler numbers inside the 5 cm (40 px) bar; the hammer head drawn 10 x 7
  cm at 6 times the handle's density (so the drawn balance point is
  exactly 20 cm, printed and checked) with the head flush with the
  handle's underside so both pads touch one line.
- Hook: the question-first form "Where do two fingers meet under a
  ruler?" (0.60 s) rather than "Slide two fingers together under a
  ruler. So where do they meet?" (the question would land at about 2.4
  s); the payoff repeats it as "So, where do two fingers meet under a
  ruler?"; the sentence "Watch the last few slips." was added before the
  payoff so that it lands on the third meeting. Narration 110 words
  (34.18 s), at the top of the 104-110 target.
- Card line 2 "at the balance point: 50 cm and 20 cm" (the forms naming
  the ruler and the hammer measured 958-1318 px); line 5 says 58.75 cm
  with two decimals (58.75 at one decimal formats as 58.7).
- One description-only variant added: the hammer at grips 0.5 / 0.45
  (29 slips, the right finger 56.50 cm first).

## Niche note

Appended to the "Fingers under a ruler" bullet in docs/niche.md:
[produced 2026-10-06 as "Where do two fingers meet under a ruler? At
the balance point: 50 cm, and 20 cm under a hammer"; measured 15 slips
on the ruler meeting at 49.21 / 50.71 cm (centre 49.96 cm) and 11
under the hammer meeting at 19.16 / 20.66 cm (centre 19.91 cm), both
in 8.350 s at 10 cm/s with grips 0.4 / 0.3 from pads at 5 and 90 cm,
swaps at 20.00, 72.50, 33.13, 62.66 cm on the ruler, the hammer's
right finger sliding 58.75 cm first, loads 0.5714 against 0.4286 W at
every swap; grips 0.5 / 0.45 give 39 and 29 slips, 0.6 / 0.3 give 7
and 5, 5 cm/s the same spots in 16.700 s, balance point 30 cm meets
at 29.21 / 30.71 cm; events within 2.8e-17 m of the closed form, 49
checks, 0 failed; task 20261006-101406]

## Upload

- Attempt 3 of 5 (quota day 2026-10-06T10:00 EEST) recorded at 2026-10-06T10:47:19+03:00 before scripts/yt-upload.py fingers; two earlier attempts (pushpull, rails, both succeeded).
- Uploaded private as 0FDvNFg8KHc at 2026-10-06T10:47:22Z (videos.insert 1,600 units). yt-qa.py --wait --publish: gate 15 of 15 on the first processed read, published at 2026-10-06T10:48:06+03:00, re-read public, 54 units. https://youtu.be/0FDvNFg8KHc
