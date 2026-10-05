# Produce short: block on a wedge, bolted or free, which block reaches the floor first

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day37

## Goal

Backlog idea (trend research 2026-10-04, task 20261004-101250, pillar 2
chaos and physics, everyday mechanics; read the full entry under "Added
by trend research 2026-10-04" in docs/niche.md): "Block on a wedge, fixed
or free: a 1 kg block sliding down a 30 degree wedge of 1 kg from 30 cm
up (60 cm of slope), the wedge bolted down beside the same wedge free on
ice, all frictionless; measure which block reaches the floor first;
expect the free wedge to win, the block down in 0.391 s against 0.495 s
(acceleration along the slope (M + m) g sin a / (M + m sin^2 a) = 7.845
against 4.903 m/s^2, exactly 1.6x, time 1.265x = sqrt 1.6), the wedge
sliding back 26.0 cm while the block goes 26.0 cm forward in the lab
(equal masses split the 52 cm run), the block pressing only 0.693 of its
weight; a wedge of 2x, 5x and 0.5x the block gives 1.333x, 1.143x and
2.000x; RK4 of the two-body system within 1e-4 s of the closed form,
horizontal momentum 1e-13, energy 2.942 J both ways; repeat the drop;
deterministic, no seed."

Orchestrator notes (2026-10-05, before this brief; closed forms in
/tmp/day37/closed.py with the log in /tmp/day37/closed.log, g = 9.807).
The model: a 1.00 kg block (a 6 cm cube, treated as a point mass at its
centre for the motion, say so) rests at the top of a 30 degree wedge
whose slope is 60 cm long (30 cm tall, 51.96 cm of run), 1.00 kg; no
friction between the block and the wedge (say so). Top band: the wedge
is bolted to the floor; the block slides down the slope at g sin a =
4.9035 m/s^2 and reaches the floor after sqrt(2 L / a) = 0.4947 s at
2.426 m/s, pressing 0.866 of its weight (8.493 N). Bottom band: the same
wedge sits free on ice (no friction under it either, say so) and is let
go with the block at the same instant; the wedge is pushed back by the
block's press and slides left at A = m g sin a cos a / (M + m sin^2 a)
= 3.3972 m/s^2 while the block speeds down the slope, relative to the
wedge, at (M + m) g sin a / (M + m sin^2 a) = 7.8456 m/s^2, exactly 1.6
times the bolted case, so it reaches the floor at 0.3911 s, 1.2649 times
sooner (exactly sqrt(1.6)); the block presses only 0.6928 of its weight
(6.794 N); in the lab the block moves 25.98 cm forward and the wedge
25.98 cm back (equal masses split the 51.96 cm run), the block's lab path
is 49.1 degrees below horizontal (steeper than the 30 degree slope), and
at the floor the block moves at 2.030 m/s in the lab (1.329 m/s forward,
1.534 m/s down) while the wedge moves at 1.329 m/s back; when the free
block reaches the floor (0.3911 s) the bolted block has slid 37.5 cm of
its 60 cm (0.5 * 4.9035 * 0.3911^2 = 0.375 m, print the exact figure).
After the floor: the block stops on a floor pad at the foot of the slope
(no bounce, say so) and the free wedge keeps sliding on the ice at 1.329
m/s until the reset (or is stopped by a buffer; choose one, say which,
and keep it inside the band). Integrate both bands with RK4 at dt =
1e-4 s on the block and wedge coordinates with the normal force solved
from the contact constraint at each step (block stays on the slope), as a
check against the closed forms (a half-step rerun agreeing within 1e-9
s); print the contact residual (at most 1e-12 m), the horizontal
momentum of the free pair (at most 1e-13 kg m/s), the energy balance
(m g h = 2.9421 J against the kinetic energy of block plus wedge, to
1e-12), the normal forces, and the position tables at 0.05 s intervals
for both bands (slope distance, block drop, wedge shift).

Checks, not facts (the sim must print and compare; state them as checks):
bolted a = 4.9035 m/s^2, floor at 0.4947 s, 2.4257 m/s, N = 8.4931 N
(0.8660 of the weight); free a_rel = 7.8456 m/s^2 (ratio 1.6000 exactly),
floor at 0.3911 s (ratio 1.2649 = sqrt(1.6)), wedge A = 3.3972 m/s^2,
N = 6.7945 N (0.6928 of the weight), block 25.98 cm forward and wedge
25.98 cm back, block lab speed 2.0295 m/s (vx 1.3286, vy 1.5342), wedge
1.3286 m/s, lab path 49.11 deg below horizontal, momentum 0, energy
2.9421 J both ways; the bolted block is at 0.375 m of 0.600 m when the
free block lands; for the description: wedge 2 kg: ratio 1.3333, floor
at 0.4284 s, wedge back 17.32 cm; wedge 5 kg: 1.1429, 0.4627 s, 8.66 cm;
wedge 0.5 kg: 2.0000, 0.3498 s, 34.64 cm; wedge 10 kg: 1.0732, 0.4775 s,
4.72 cm; the same 30 cm drop at 20 deg: ratio 1.7905, 0.7232 against
0.5405 s; 45 deg: 1.3333, 0.3498 against 0.3029 s; 60 deg: 1.1429, 0.2856
against 0.2672 s. Print the schedule in video time, the text widths and
the layout clearances.

Drawing: two-band layout (sims/deskchain and sims/uphill style), side
view, the bolted wedge on top (the slower case) and the free wedge below;
same scale, same clock. Scale 600 px per metre: the wedge a right
triangle 312 px of run and 180 px of rise, the block a 36 px square
riding on the slope (its centre offset from the slope by half its
diagonal is fine; draw the block square to the slope); in each band a
floor line with a floor pad at the foot of the slope, the bolted wedge
with two small bolt marks at its base, the free wedge on a pale ice strip
with no bolts; a faint dotted trace of the block's lab path in each
band so the steeper free path shows (30 deg against 49 deg); the free
wedge starting with its foot at about x 560 and ending 156 px to the
left; the block's lab x in the free band runs 156 px to the right; keep
everything inside its band at the extremes (the free wedge after the
floor keeps sliding; stop it with a buffer or hold it at the reset,
inside the band). Label rows (40 px, coloured): "bolted down" (coral)
and "free on ice" (teal). Readouts (28 px): left column "block: NN.N cm
down" (vertical drop of its centre) and the clock; right column "slope:
NN.N of 60 cm" (and in the free band "wedge: NN.N cm back"). Gold event
rows: top "bolted: floor at 0.49 s" (lit at the landing and held), bottom
"free: floor at 0.39 s, 1.26x sooner; wedge 26 cm back" (lit and held).
Shown at 1/8 speed; cycle 10 s (600 frames): both let go 1.0 s into the
cycle, the free block lands at 1.0 + 8 * 0.3911 = 4.13 s of the cycle,
the bolted block at 1.0 + 8 * 0.4947 = 4.96 s; hold; reset by a crossfade
over the last 0.6 s of the cycle; 4 cycles in 40 s, exactly periodic,
the last frame equal to the first. The legend row after the title: "same
block, same wedge, same instant, 1/8 speed"; the shared clock in real
seconds since the release. Overlay: "1 kg block on a 1 kg wedge | 30 deg,
30 cm | no seed" (measure it; shorten if over 950 px).

Day thirty-seven, first slot. Chosen because "which gets down first"
races are the channel's strongest format (folded chain against a ball
990 views, ice cube against a ball 973, stick against a ball 619), the
two blocks end visibly differently (the free block is down while the
bolted one is still a third of the way up, and the wedge has slid away),
the factor is exact (1.6, time root 1.6), the debate is live online (the
search summaries get the direction wrong), and the repeat is a natural
loop. Question in the first two seconds: "Which block reaches the floor
first?" after a short setup ("A block on a wedge. Bolted down, or free to
slide."), or "Bolt the wedge or let it slide: which block gets down
first?"; pre-test the variants and keep the question identical in the
title, the hook and the payoff. Setup number: thirty centimeters up (or
"a thirty degree wedge"; one setup number spoken). Payoff: the block on
the free wedge, at point three nine seconds against point four nine
(speak at most two numbers in the payoff beat; "point three nine" and
"point four nine" are the preferred pair; "one point six times" and
"twenty six centimeters" go to the card unless the mechanism beat shows
the wedge sliding back, where "twenty six centimeters" may be spoken).
The mechanism sentence must follow the picture: the wedge slides out
from under the block, so the block falls on a steeper path; the block
presses the wedge less, and the slope runs away under it (never "pull"
as a noun; never "frictionless", say "no friction" or "on ice"). Whisper
risks: "wedge" (pre-test), "bolted" and "bolt" (pre-test; a
sentence-initial "Bolt" risks the onset clip), "slides" and "slide"
(pre-test), "point three nine seconds" and "point four nine" (pre-test),
"one point six times" (pre-test), "steeper" (pre-test), avoid "do you",
avoid "fly", avoid "pull" as a noun. Pre-test hooks with
scripts/voiceover.sh and keep the one whose question lands earliest
under two seconds. Measure every fixed text line with PIL before
rendering and keep every line under 950 px, and the title under 100
characters with no < or >. Music seed 112. Templates: sims/deskchain
(two-band layout, asserts, the clock, the crossfade; read it whole),
sims/uphill (a slope with an object on it in two bands), sims/kerbhop (a
rolling object meeting a step, event rows). Sim name wedge:
sims/wedge/wedge.py, projects/wedge/, media/wedge/.

## Claim (expected; the sim's numbers replace these)

A 1 kg block let go at the top of a 30 degree, 60 cm slope (30 cm up) on
a 1 kg wedge, no friction anywhere: on the bolted wedge the block reaches
the floor at 0.495 s; on the same wedge free on ice it reaches the floor
at 0.391 s, 1.26 times sooner, because the wedge slides back 26 cm and
the block's acceleration along the slope is exactly 1.6 times larger
(7.85 against 4.90 m/s^2), its path 49 degrees steep instead of 30, and
it presses the wedge with only 0.69 of its weight. Narrated: thirty
centimeters up (setup); the free one first, point three nine seconds
against point four nine (payoff). Card: the question; the answer with
0.39 against 0.49 s, 1.26x sooner; a = 1.6x along the slope, exactly;
wedge 26 cm back, block 26 cm forward; presses 0.69 of its weight; wedge
2 kg: 1.33x, 0.43 s. Description: the model statement, the equations,
the two runs, the mass and angle variants, the checks.

## Claim

A 1 kg block let go at the top of a 30 degree, 60 cm slope (30 cm up)
on a 1 kg wedge, no friction anywhere: on the bolted wedge the block
reaches the floor at 0.4947 s (0.49 s); on the same wedge free on ice
it reaches the floor at 0.3911 s (0.39 s), 1.2649 times sooner (exactly
sqrt 1.6), because the wedge slides back 25.98 cm, the block's
acceleration along the slope is exactly 1.6000 times larger (7.8456
against 4.9035 m/s^2), its lab path is 49.11 degrees steep instead of
30, and it presses the wedge with 0.6928 of its weight against 0.8660.
Narrated: "thirty centimeters up" and "eight times slower" (setup);
"down in zero point three nine seconds, against zero point four nine on
the bolted wedge" (payoff). Card: the question; free wedge 0.39 s,
bolted 0.49 s, 1.26x; slope a 1.6x: 7.85 vs 4.90 m/s^2; wedge 26 cm
back, block 26 cm forward; path 49 deg; presses 0.69 of its weight;
wedge 2 kg: 1.33x, 0.43 s; 5 kg: 0.46 s.

## Evidence

### Measurements

Final `nix develop -c python3 sims/wedge/wedge.py --measure-only`
(media/wedge/measure.log, 2026-10-05 10:21:51, exit 0):

```
Mon Oct  5 10:21:51 AM EEST 2026
warning: Git tree '/home/alex/personal/seedzero' is dirty
setup: side view, two panels on one clock, the same wedge drawn the same way at the same scale: a 1 kg block (a 6 cm cube, treated as a point mass at its centre for the motion) rests at the top of a 30 degree wedge of 1 kg whose slope is L = h / sin a = 0.6000 m = 60 cm long (30 cm tall, 51.96 cm of run); no friction between the block and the wedge; g = 9.807 m/s^2; top panel the wedge is bolted to the floor; bottom panel the same wedge sits free on ice (no friction under it either) and is let go with the block at the same instant; after the floor the block stops on a floor pad at the foot of the slope (no bounce) and a buffer on the ice stops the free wedge at its landing position, at the instant the block lands (a plastic stop); both bands integrated by classical RK4 at 10000 steps per second (dt = 1e-04 s) on the block's and the wedge's coordinates with the normal force solved from the contact constraint at every stage, the floor crossing located by bisection inside the step, checked against the closed forms and a half-step rerun; shown at 1/8 speed on a 10 s cycle (600 frames) with the release 1 s into the cycle, 4 cycles in 40 s; drawn at 600 px per metre (the wedge 312 px of run and 180 px of rise, the block 36 px square; the drawn slope runs 3 cm past the block's start so the whole block sits on it); deterministic, no seed
bolted down (top panel): a along the slope g sin a = 4.9035 m/s^2 = 4.90 m/s^2 (RK4 table 2 s / t^2 = 4.9035, diff -4.2e-14); RK4: the block reaches the floor at 0.494695 s = 0.4947 s = 0.49 s (closed form sqrt(2 L / a) = 0.494695 s, diff +2.1e-15 s), 4947 steps, moving at 2.4257 m/s = 2.43 m/s in the lab (vx 2.1007, vy 1.2129 down; closed form 2.4257, diff +5.8e-14), 60.00 cm along the slope; the normal force N = 8.4931 N = 0.8660 of the block's weight 9.8070 N (closed form 8.4931 N, diff +0.0e+00); the wedge does not move (bolted): 0.00 cm; the block moves 51.9615 cm = 51.96 cm forward in the lab (closed form 51.9615 cm) and 30.00 cm down; the sum 51.96 cm is the run L cos a = 51.96 cm; the block's lab path is 30.0000 degrees = 30.00 degrees = 30 degrees below horizontal (closed form 30.0000); the contact residual (block to slope, normal) stays within 7.5e-15 m; the block's horizontal momentum grows to 2.1007 kg m/s (the bolts and the floor take the push); energy: m g h = 2.9421 J against the kinetic energy of block plus wedge at the floor 2.9421 J (diff +1.4e-13 J), the balance along the run within 2.6e-13 J; half-step rerun (dt = 5e-05 s): floor at 0.494695014 s (+9.7e-15 s)
free on ice (bottom panel): a along the slope (M + m) g sin a / (M + m sin^2 a) = 7.8456 m/s^2 = 7.85 m/s^2 (RK4 table 2 s / t^2 = 7.8456, diff -1.7e-14); RK4: the block reaches the floor at 0.391091 s = 0.3911 s = 0.39 s (closed form sqrt(2 L / a) = 0.391091 s, diff +4.4e-16 s), 3911 steps, moving at 2.0295 m/s = 2.03 m/s in the lab (vx 1.3286, vy 1.5342 down; closed form 2.0295, diff +8.6e-14), 60.00 cm along the slope; the normal force N = 6.7945 N = 0.6928 of the block's weight 9.8070 N (closed form 6.7945 N, diff +0.0e+00); the wedge accelerates back at A = m g sin a cos a / (M + m sin^2 a) = 3.3972 m/s^2 and slides back 25.9808 cm = 25.98 cm = 26 cm (closed form 25.9808 cm) at 1.3286 m/s; the block moves 25.9808 cm = 25.98 cm forward in the lab (closed form 25.9808 cm) and 30.00 cm down; the sum 51.96 cm is the run L cos a = 51.96 cm; the block's lab path is 49.1066 degrees = 49.11 degrees = 49 degrees below horizontal (closed form 49.1066); the contact residual (block to slope, normal) stays within 1.4e-14 m; horizontal momentum of the pair m vx + M V within 0.0e+00 kg m/s; energy: m g h = 2.9421 J against the kinetic energy of block plus wedge at the floor 2.9421 J (diff +2.4e-13 J), the balance along the run within 1.2e-13 J; half-step rerun (dt = 5e-05 s): floor at 0.391090748 s (-5.2e-15 s)
the two panels: the free wedge's block accelerates along the slope 1.6000 times as hard as the bolted one (7.8456 against 4.9035 m/s^2; exactly (M + m) / (M + m sin^2 a) = 1.6000, diff +0.0e+00) and reaches the floor at 0.3911 s against 0.4947 s, 1.2649 times sooner = 1.26 times (exactly sqrt(1.6) = 1.2649, diff +4.0e-15), 103.6 ms earlier; when the free block lands at 0.3911 s the bolted block is at 0.3750 m = 37.5 cm of 0.600 m along its slope (closed form a t^2 / 2 = 0.3750 m), 62.5 percent of the way; the free block presses 0.6928 of its weight against 0.8660 on the bolted wedge; the free block's lab path is 49.11 degrees below horizontal against the 30 degree slope; at the floor the free block moves at 2.0295 m/s in the lab against 2.4257 m/s on the bolted wedge, and the wedge at 1.3286 m/s back; the free wedge is stopped by the buffer 0.0000 s after the landing, 25.98 cm from its start
table bolted (RK4 table, real time after the release): 0.0000 s: slope 0.00 cm, block 0.00 cm down and 0.00 cm forward, wedge 0.00 cm back, block 0.000 m/s; 0.0500 s: slope 0.61 cm, block 0.31 cm down and 0.53 cm forward, wedge 0.00 cm back, block 0.245 m/s; 0.1000 s: slope 2.45 cm, block 1.23 cm down and 2.12 cm forward, wedge 0.00 cm back, block 0.490 m/s; 0.1500 s: slope 5.52 cm, block 2.76 cm down and 4.78 cm forward, wedge 0.00 cm back, block 0.736 m/s; 0.2000 s: slope 9.81 cm, block 4.90 cm down and 8.49 cm forward, wedge 0.00 cm back, block 0.981 m/s; 0.2500 s: slope 15.32 cm, block 7.66 cm down and 13.27 cm forward, wedge 0.00 cm back, block 1.226 m/s; 0.3000 s: slope 22.07 cm, block 11.03 cm down and 19.11 cm forward, wedge 0.00 cm back, block 1.471 m/s; 0.3500 s: slope 30.03 cm, block 15.02 cm down and 26.01 cm forward, wedge 0.00 cm back, block 1.716 m/s; 0.4000 s: slope 39.23 cm, block 19.61 cm down and 33.97 cm forward, wedge 0.00 cm back, block 1.961 m/s; 0.4500 s: slope 49.65 cm, block 24.82 cm down and 43.00 cm forward, wedge 0.00 cm back, block 2.207 m/s; 0.4947 s: slope 60.00 cm, block 30.00 cm down and 51.96 cm forward, wedge 0.00 cm back, block 2.426 m/s
table free (RK4 table, real time after the release): 0.0000 s: slope 0.00 cm, block 0.00 cm down and 0.00 cm forward, wedge 0.00 cm back, block 0.000 m/s; 0.0500 s: slope 0.98 cm, block 0.49 cm down and 0.42 cm forward, wedge 0.42 cm back, block 0.259 m/s; 0.1000 s: slope 3.92 cm, block 1.96 cm down and 1.70 cm forward, wedge 1.70 cm back, block 0.519 m/s; 0.1500 s: slope 8.83 cm, block 4.41 cm down and 3.82 cm forward, wedge 3.82 cm back, block 0.778 m/s; 0.2000 s: slope 15.69 cm, block 7.85 cm down and 6.79 cm forward, wedge 6.79 cm back, block 1.038 m/s; 0.2500 s: slope 24.52 cm, block 12.26 cm down and 10.62 cm forward, wedge 10.62 cm back, block 1.297 m/s; 0.3000 s: slope 35.31 cm, block 17.65 cm down and 15.29 cm forward, wedge 15.29 cm back, block 1.557 m/s; 0.3500 s: slope 48.05 cm, block 24.03 cm down and 20.81 cm forward, wedge 20.81 cm back, block 1.816 m/s; 0.3911 s: slope 60.00 cm, block 30.00 cm down and 25.98 cm forward, wedge 25.98 cm back, block 2.030 m/s
for the description: wedge 2 kg (block 1 kg, 30 degrees): a along the slope 1.3333 times the bolted case, the floor at 0.4284 s (1.1547 times sooner; closed form 0.4284 s, diff -6.7e-16), the wedge back 17.32 cm (closed form 17.32), the block pressing 0.7698 of its weight; wedge 5 kg (block 1 kg, 30 degrees): a along the slope 1.1429 times the bolted case, the floor at 0.4627 s (1.0690 times sooner; closed form 0.4627 s, diff -2.7e-15), the wedge back 8.66 cm (closed form 8.66), the block pressing 0.8248 of its weight; wedge 0.5 kg (block 1 kg, 30 degrees): a along the slope 2.0000 times the bolted case, the floor at 0.3498 s (1.4142 times sooner; closed form 0.3498 s, diff +1.3e-15), the wedge back 34.64 cm (closed form 34.64), the block pressing 0.5774 of its weight; wedge 10 kg (block 1 kg, 30 degrees): a along the slope 1.0732 times the bolted case, the floor at 0.4775 s (1.0359 times sooner; closed form 0.4775 s, diff -1.8e-15), the wedge back 4.72 cm (closed form 4.72), the block pressing 0.8449 of its weight; 20 degrees (the same 30 cm drop, 87.71 cm of slope, equal masses): a ratio 1.7905, bolted floor at 0.7232 s, free at 0.5405 s (1.3381 times sooner), the wedge back 41.21 cm, the free block pressing 0.8413 of its weight (closed forms 0.7232 and 0.5405 s); 45 degrees (the same 30 cm drop, 42.43 cm of slope, equal masses): a ratio 1.3333, bolted floor at 0.3498 s, free at 0.3029 s (1.1547 times sooner), the wedge back 15.00 cm, the free block pressing 0.4714 of its weight (closed forms 0.3498 and 0.3029 s); 60 degrees (the same 30 cm drop, 34.64 cm of slope, equal masses): a ratio 1.1429, bolted floor at 0.2856 s, free at 0.2672 s (1.0690 times sooner), the wedge back 8.66 cm, the free block pressing 0.2857 of its weight (closed forms 0.2856 and 0.2672 s)
checks against the brief (46 checks, 0 failed): bolted a (m/s^2): brief 4.9035, sim 4.9035, diff -8.9e-16: ok; bolted floor at (s): brief 0.4947, sim 0.494695, diff -5.0e-06: ok; bolted speed at the floor (m/s): brief 2.4257, sim 2.42574, diff +3.7e-05: ok; bolted N (N): brief 8.4931, sim 8.49311, diff +1.1e-05: ok; bolted N / weight: brief 0.866, sim 0.866025, diff +2.5e-05: ok; free a_rel (m/s^2): brief 7.8456, sim 7.8456, diff -8.9e-16: ok; a ratio: brief 1.6, sim 1.6, diff +0.0e+00: ok; free floor at (s): brief 0.3911, sim 0.391091, diff -9.3e-06: ok; time ratio: brief 1.2649, sim 1.26491, diff +1.1e-05: ok; time ratio = sqrt(1.6): brief 1.26491, sim 1.26491, diff +4.0e-15: ok; wedge A (m/s^2): brief 3.3972, sim 3.39724, diff +4.4e-05: ok; free N (N): brief 6.7945, sim 6.79449, diff -1.1e-05: ok; free N / weight: brief 0.6928, sim 0.69282, diff +2.0e-05: ok; block forward (cm): brief 25.98, sim 25.9808, diff +7.6e-04: ok; wedge back (cm): brief 25.98, sim 25.9808, diff +7.6e-04: ok; block lab speed (m/s): brief 2.0295, sim 2.02952, diff +1.7e-05: ok; block vx (m/s): brief 1.3286, sim 1.32863, diff +3.1e-05: ok; block vy (m/s): brief 1.5342, sim 1.53417, diff -2.9e-05: ok; wedge speed (m/s): brief 1.3286, sim 1.32863, diff +3.1e-05: ok; lab path (deg): brief 49.11, sim 49.1066, diff -3.4e-03: ok; momentum (kg m/s): brief 0, sim 0, diff +0.0e+00: ok; energy bolted (J): brief 2.9421, sim 2.9421, diff +1.4e-13: ok; energy free (J): brief 2.9421, sim 2.9421, diff +2.4e-13: ok; m g h (J): brief 2.9421, sim 2.9421, diff +0.0e+00: ok; bolted block when the free lands (m): brief 0.375, sim 0.375, diff +2.1e-09: ok; wedge 2 kg ratio: brief 1.3333, sim 1.33333, diff +3.3e-05: ok; wedge 2 kg floor at (s): brief 0.4284, sim 0.428418, diff +1.8e-05: ok; wedge 2 kg back (cm): brief 17.32, sim 17.3205, diff +5.1e-04: ok; wedge 5 kg ratio: brief 1.1429, sim 1.14286, diff -4.3e-05: ok; wedge 5 kg floor at (s): brief 0.4627, sim 0.462745, diff +4.5e-05: ok; wedge 5 kg back (cm): brief 8.66, sim 8.66025, diff +2.5e-04: ok; wedge 0.5 kg ratio: brief 2, sim 2, diff +0.0e+00: ok; wedge 0.5 kg floor at (s): brief 0.3498, sim 0.349802, diff +2.2e-06: ok; wedge 0.5 kg back (cm): brief 34.64, sim 34.641, diff +1.0e-03: ok; wedge 10 kg ratio: brief 1.0732, sim 1.07317, diff -2.9e-05: ok; wedge 10 kg floor at (s): brief 0.4775, sim 0.477533, diff +3.3e-05: ok; wedge 10 kg back (cm): brief 4.72, sim 4.72377, diff +3.8e-03: ok; 20 deg ratio: brief 1.7905, sim 1.79055, diff +4.6e-05: ok; 20 deg bolted floor at (s): brief 0.7232, sim 0.723196, diff -4.3e-06: ok; 20 deg free floor at (s): brief 0.5405, sim 0.540459, diff -4.1e-05: ok; 45 deg ratio: brief 1.3333, sim 1.33333, diff +3.3e-05: ok; 45 deg bolted floor at (s): brief 0.3498, sim 0.349802, diff +2.2e-06: ok; 45 deg free floor at (s): brief 0.3029, sim 0.302938, diff +3.8e-05: ok; 60 deg ratio: brief 1.1429, sim 1.14286, diff -4.3e-05: ok; 60 deg bolted floor at (s): brief 0.2856, sim 0.285612, diff +1.2e-05: ok; 60 deg free floor at (s): brief 0.2672, sim 0.267166, diff -3.4e-05: ok
schedule (video time, 1/8 speed): cycles of 10 s start at -10.00, 0.00, 10.00, 20.00, 30.00 s (the first -0.00 s before the first frame); both blocks are let go 1 s into each cycle at 1.00, 11.00, 21.00, 31.00 s (the stop pins fade over 0.3 s); the free block reaches the floor 3.13 s after the release at 4.13, 14.13, 24.13, 34.13 s (4.13 s into the cycle; its event row lights, the block settles flat on the pad over 0.12 s) and the buffer stops the free wedge 0.00 s after the landing at 4.13, 14.13, 24.13, 34.13 s; the bolted block reaches the floor 3.96 s after the release at 4.96, 14.96, 24.96, 34.96 s (4.96 s into the cycle; its event row lights); the free block is 6.1 cm down the slope 1 s of video after the release and the bolted 3.8 cm, after 2 s 24.5 and 15.3 cm; the reset crossfade runs over the last 0.6 s of each cycle (from 9.40, 19.40, 29.40, 39.40 s; the readouts out over its first half and in over its second); on the first frame the cycle is 0.00 s in (-0.125 s real: both blocks held at the top); title until 3 s; payoff card from 31 s; the title fades back in over the last 0.5 s and the last frame repeats the first (the scene is periodic: 40 s holds exactly 4 cycles)
text widths (the on-screen strings verbatim): overlay@34 934 px '1 kg block, 1 kg wedge | 30 deg, 30 cm | no seed', title line 1@56 858 px 'Bolted down or free on ice:', title line 2@56 639 px 'which block reaches', title line 3@56 451 px 'the floor first?', legend@40 814 px 'same block, same wedge, 1/8 speed', clock@28 390 px '1.125 s after the release', clock held@28 194 px 'held, at rest', label bolted@40 280 px 'bolted down', slope bolted@40 457 px 'slope: 60.0 of 60 cm', block bolted@28 324 px 'block: 30.0 cm down', speed bolted@28 239 px 'speed 2.43 m/s', wedge bolted@28 352 px 'wedge: bolted, 0.0 cm', press bolted@28 409 px 'presses 0.87 of its weight', event bolted@40 489 px 'bolted: floor at 0.49 s', label free@40 240 px 'free on ice', slope free@40 457 px 'slope: 60.0 of 60 cm', block free@28 324 px 'block: 30.0 cm down', speed free@28 239 px 'speed 2.03 m/s', wedge free@28 333 px 'wedge: 26.0 cm back', press free@28 409 px 'presses 0.69 of its weight', event free@40 758 px 'free: floor at 0.39 s, 1.26x sooner', wedge mass@24 58 px '1 kg', ice@24 39 px 'ice', payoff line 1@40 793 px 'which block reaches the floor first?', payoff line 2@40 882 px 'free wedge 0.39 s, bolted 0.49 s, 1.26x', payoff line 3@40 733 px 'slope a 1.6x: 7.85 vs 4.90 m/s^2', payoff line 4@40 906 px 'wedge 26 cm back, block 26 cm forward', payoff line 5@40 885 px 'path 49 deg; presses 0.69 of its weight', payoff line 6@40 873 px 'wedge 2 kg: 1.33x, 0.43 s; 5 kg: 0.46 s'
row check: the left column ends at x 364 px, the right column starts at x 583 px; both end 134 px under the band top; the floor surface is 420 px under the band top, the slab to 448 px; the event row spans 476 to 516 px under the band top and x 161 to 919 px (widest 758 px, centred on 540); the wedge's foot starts at x 600, the block's start (the top of the slope) at x 288.2, 240.0 px under the band top, the drawn apex at x 272.6, 231.0 px (the slope extended 18 px); the block's highest corner at the start is 199.8 px under the band top and its leftmost corner at x 272.6; the free wedge slides 155.9 px left to its landing position (drawn apex at x 116.8) and 0 px more to the buffer face at x 117 (the buffer from x 95); the blocks land with their centres at x 600.0 (bolted) and 444.1 (free) px and settle flat on the pads at x 600 to 648 and 444 to 492; the wedge mass label sits at x 267 at its furthest left; each band is 550 px tall (y 330 to 880 and 880 to 1430); the caption band starts at y 1440; the title rows end at y 330 and the overlay band ends at y 130
exit 0
Mon Oct  5 10:21:52 AM EEST 2026
```

Each brief check against the measurement (46 checks, 0 failed, the
tolerances in `measure()`):

- bolted a along the slope 4.9035 m/s^2 (brief 4.9035); floor at
  0.494695 s (brief 0.4947); speed at the floor 2.4257 m/s (brief
  2.4257); N 8.4931 N = 0.8660 of the weight (brief 8.4931, 0.866).
- free a along the slope 7.8456 m/s^2 (brief 7.8456); a ratio 1.6000
  exact (diff +0.0e+00); floor at 0.391091 s (brief 0.3911); time ratio
  1.2649 (brief 1.2649) = sqrt(1.6) within 4.0e-15; wedge A 3.3972 m/s^2
  (brief 3.3972); N 6.7945 N = 0.6928 of the weight (brief 6.7945,
  0.6928); block 25.9808 cm forward and the wedge 25.9808 cm back (brief
  25.98 both); block lab speed 2.0295 m/s (vx 1.3286, vy 1.5342; brief
  2.0295, 1.3286, 1.5342); wedge 1.3286 m/s (brief 1.3286); lab path
  49.1066 degrees (brief 49.11).
- horizontal momentum of the free pair 0.0e+00 kg m/s (brief 0); energy
  m g h 2.9421 J against 2.9421 J kinetic in both bands (diffs +1.4e-13
  and +2.4e-13 J); the bolted block at 0.3750 m when the free one lands
  (brief 0.375).
- wedge 2 kg: ratio 1.3333, floor 0.4284 s, back 17.32 cm; 5 kg:
  1.1429, 0.4627 s, 8.66 cm; 0.5 kg: 2.0000, 0.3498 s, 34.64 cm; 10 kg:
  1.0732, 0.4775 s, 4.72 cm (all as the brief).
- 20 degrees: ratio 1.7905, bolted 0.7232 s, free 0.5405 s; 45 degrees:
  1.3333, 0.3498, 0.3029; 60 degrees: 1.1429, 0.2856, 0.2672 (all as
  the brief).
- numerics: RK4 floor times against the closed forms +2.1e-15 s
  (bolted) and +4.4e-16 s (free); half-step rerun +9.7e-15 and -5.2e-15
  s; contact residual within 7.5e-15 and 1.4e-14 m; the RK4 table gives
  a = 2 s / t^2 = 4.9035 and 7.8456 (diffs -4.2e-14, -1.7e-14).
- text widths measured with PIL: every line under 950 px; the widest
  are the overlay 934 px, payoff line 4 906 px, payoff line 5 885 px,
  payoff line 2 882 px, title line 1 858 px (full list in the log).
- row check asserts: columns end 134 px under the band top, the floor
  surface at 420 px, the event row 476 to 516 px, bands y 330 to 880 and
  880 to 1430, captions from y 1440, the title rows end at y 330.

### Production

- sims/wedge/wedge.py (two-body RK4 on Cartesian state with N from the
  contact constraint at each stage, bisection for the floor crossing,
  half-step rerun, closed forms, measure(), two-band Renderer with the
  crossfade reset, loop fade and periodicity checks).
- projects/wedge/manifest.json: g 9.807, 1 kg block, 1 kg wedge, 30
  degrees, 0.3 m, block side 0.06 m, 10000 steps per second, slow 8,
  cycle 10 s, release at 1.0 s, reset fade 0.6 s, pin fade 0.3 s,
  settle 0.12 s, buffer gap 0 m, 40 s, 600 px per metre, foot at x 600,
  title until 3 s, payoff card from 31 s, music seed 112, voice offset
  0.6 s, caption_y 0.75.
- measure: media/wedge/measure.log (above). Smoke frames
  media/wedge/smoke-*.png viewed at 0.0, 3.4, 4.2, 5.1, 9.6 and 34.3 s
  before the full render.
- render: media/wedge/render.log 10:21:52 to 10:22:31; loop check 0 px,
  periodicity check 0 px, loop step 0 px; footage.mp4 40.00 s, 2400
  frames at 60 fps.
- hook pre-tests (media/wedge/hooks/pretest.log, all five pass the
  round trip): hook1 question ends at 1.88 s of voice; hook2 the
  question starts after 3.0 s; hook3 after 1.53 s (ends 3.77 s); hook4
  question ends at 1.94 s of voice; hook5 the question from 1.53 to
  3.44 s. Kept hook4 (question first, clean flow into the two panels).
  Word pre-tests: "zero point three nine seconds against zero point
  four nine" passes; "point three nine" folds to "39" and fails; "one
  eighth" returns "8th" and fails; "eight times slower" passes; "slowed
  down eight times" fails ("slow", "tines"). "wedge", "bolted", "slides",
  "steeper" all pass.
- narration: projects/wedge/narration.txt, 114 words, numbers spelled
  out. Voice: media/wedge/voice.log pass 1 ok, 36.153 s,
  media/wedge/voice.wav.
- timing (media/wedge/timing.log, video time with the 0.6 s offset):
  the question 0.60 to 2.50 s; "thirty centimeters up" 7.41 to 10.01 s;
  "both let go together" 11.41 to 12.92 s over the second release at
  11.00 s; "eight times slower" 12.92 to 14.38 s; the mechanism beat
  15.12 to 25.02 s over the third drop (release 21.00 s); "The one on
  the free wedge" 30.21 to 31.58 s; "down in 0.39 seconds" 31.58 to
  33.96 s; "against 0.49 on the bolted wedge" 33.96 to 36.75 s; the
  voice ends at 36.75 s with the fourth drop landing at 34.13 and 34.96
  s under it.
- compose: media/wedge/compose.log 10:22:31 to 10:22:54; music seed 112;
  captions 21 pauses detected, 21 matched, max chunk start shift 1.523
  s; final.mp4 40.000000 s; preview.mp4; sheet.png 8x5.

### Local QA

- ffprobe final.mp4: h264 1080x1920 60/1, aac 22050 Hz, duration
  40.000000 s; atoms ftyp, moov, free, mdat (faststart).
- md5 d11298f93bcafecbfffd4efba46eef1e media/wedge/final.mp4 (4338257
  bytes).
- footage.mp4 signalstats over all 2400 frames: caption band (1080x90
  at y 1440) YMAX 28, overlay band (1080x34 at y 96) YMAX 28, so the
  footage leaves both bands empty for the compose text.
- captions (media/wedge/captions.filter): 36 chunks, 114 of 114 words
  match the narration word for word; "Which block reaches" 0.600 to
  1.494 s, "the floor first?" 1.494 to 2.609 s; "point three nine"
  32.617 to 33.480 s; "zero point four nine" 34.434 to 35.529 s; the
  last chunk ends at 36.753 s. The title holds the question on screen
  from frame 0 to 3.0 s and the card repeats it from 31.0 s.
- voice.wav silencedetect (-35 dB, 0.12 s): 33 pauses, the first at
  1.788 s (after "first?") and 2.488 s (after "On top").
- frames viewed at full resolution (media/wedge/qa-*.png):
  - 0.00 s: overlay, the three-row title with the question, both blocks
    held at the top with gold stop pins, two bolt marks on the top wedge,
    the ice strip with the buffer and the "ice" tag below, readouts at
    0.0, no caption.
  - 1.00 s: the same scene with the caption "Which block reaches".
  - 2.10 s: caption "the floor first?"; both blocks moving (bolted 4.6
    of 60 cm, free 7.4 of 60 cm, the free wedge 3.2 cm back).
  - 15.00 s: legend and clock (0.500 s after the release); both blocks
    flat on their pads, dashed trails (30 against 49 degrees), both
    event rows lit in gold ("bolted: floor at 0.49 s", "free: floor at
    0.39 s, 1.26x sooner"), "wedge: 26.0 cm back" in gold; caption "On
    top, the block".
  - 23.50 s: 0.312 s after the release, bolted 23.9 of 60 cm, free 38.3
    of 60 cm and the wedge 16.6 cm back; caption "and the slope runs".
  - 31.40 s: the fourth release 0.050 s in, the card fading in with six
    gold lines, caption "wedge, down in zero".
  - 32.80 s: caption "point three nine" with the card fully lit
    ("free wedge 0.39 s, bolted 0.49 s, 1.26x"), both blocks mid-slope.
  - 34.30 s: the free block landed (0.412 s), its event row lit, the
    bolted block at 41.7 of 60 cm; caption "seconds, against".
  - 39.983 s: identical in content to 0.00 s (title back, blocks held,
    no caption).
  - sheet.png: 40 thumbs at 1 fps show four clean drops, the captions
    readable, the card from 31 s, nothing clipped at the frame edge.
- loop: the renderer's own check finds 0 px between the raw last and
  first frames; between the decoded footage.mp4 frames 0 and 2399 the
  maximum channel difference is 68 on 281 of 2,073,600 pixels (text
  edges, h264 quantisation), mean 0.51; the final.mp4 QA frames 0.00
  and 39.983 differ by at most 79 on 2455 pixels, mean 0.81.
- no clipped text: every measured line under 950 px, the widest 934 px.

### Metadata

projects/wedge/metadata.json written by a Python script with asserts:
title 97 characters (at most 100), description 4223 characters (under
5000), no "<" or ">", ASCII only, 12 tags, categoryId 27, private,
containsSyntheticMedia true, selfDeclaredMadeForKids false. The same
script checked every numeric token of the title and the description
(135 tokens, commas stripped) and the narrated numbers (thirty, eight,
zero point three nine, zero point four nine) against the numeric tokens
of measure.log: none missing. Title: "Bolted down or free on ice: which
block reaches the floor first? Free wedge 0.39 s, bolted 0.49 s".

### Deviations from the brief

- Legend shortened to "same block, same wedge, 1/8 speed" (the brief's
  legend measured 1136 px); overlay "1 kg block, 1 kg wedge | 30 deg, 30
  cm | no seed" (the brief's 1016 px); the free event row "free: floor
  at 0.39 s, 1.26x sooner" (the brief's longer row 1205 px); the wedge
  travel sits in the readout "wedge: 26.0 cm back" instead.
- The buffer sits at the free wedge's landing position (buffer_gap_m
  0) so the readout holds the narrated 26 cm; with the 8 cm gap the
  readout read 34.0 cm.
- The drawn slope runs 3 cm (18 px) past the block's start so the whole
  cube sits on the wedge; the motion uses the block's centre.
- The wedge foot sits at x 600 (not 560) so the free wedge's 156 px of
  travel clears the buffer at x 95.
- Narration says "shown eight times slower" instead of "one eighth
  speed" (whisper returns "8th"), and "zero point three nine seconds"
  instead of "point three nine" (whisper folds ".39" to "39").
- The spoken question ends at 2.50 s of video (1.94 s of voice after
  the 0.6 s offset); the question is on screen from frame 0 in the
  title and from 0.60 s in the captions.
- Payoff card lines 2 and 3 shortened to fit under 950 px (the brief's
  wording measured 994 and 961 px).

## Niche note

Appended inside the wedge bullet of docs/niche.md: produced 2026-10-05
as "Bolted down or free on ice: which block reaches the floor first?
Free wedge 0.39 s, bolted 0.49 s"; measured bolted floor at 0.4947 s,
free at 0.3911 s (1.2649 times sooner = sqrt 1.6), slope a 7.8456
against 4.9035 m/s^2 (1.6000x exact), the wedge 25.98 cm back and the
block 25.98 cm forward, path 49.11 degrees, N 0.6928 against 0.8660 of
the weight, momentum 0.0e+00, energy 2.9421 J both; task
20261005-100707.

## Upload

- Attempt 1 of 5 (quota day 2026-10-05T10:00 EEST) recorded at 2026-10-05T11:01:59+03:00 before scripts/yt-upload.py wedge; zero earlier attempts since the boundary.
- Uploaded private as qU1dbX1Ro2E at 2026-10-05T11:02:02+03:00 (videos.insert 1,600 units). yt-qa.py --wait --publish: gate 15 of 15 on the first processed read, published at 2026-10-05T11:03:06+03:00, re-read public, 55 units. https://youtu.be/qU1dbX1Ro2E
