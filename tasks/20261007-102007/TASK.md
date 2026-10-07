# Produce short: jump from a boat, tied beside free, does it matter if the boat is tied

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day39

## Goal

Backlog idea (trend research 2026-10-07, task 20261007-100305, pillar 2
chaos and physics, everyday mechanics; read the full "Jump from a boat,
tied or free" bullet under "Added by trend research 2026-10-07" in
docs/niche.md): the same jump from the same boat toward a dock, the boat
tied up beside the boat free; the free jump falls in.

Orchestrator notes (2026-10-07; closed forms in /tmp/day39/closed.py with
the log /tmp/day39/closed.log, research script
/tmp/day39/research/boat.py with boat.log; g = 9.807 m/s^2). Read
/tmp/day39/producer-conventions.md first. The model: a jumper of mass m
= 70 kg as a point mass standing at the bow of a boat of mass M = 50 kg
(a light dinghy, say so) on still water; the dock edge is 1.00 m from
the bow at the boat's floor height; the legs give the jumper a takeoff
of u = 3.50 m/s at 45 degrees relative to the boat (the textbook form,
say so: the push is defined by the relative speed); horizontal momentum
of jumper plus boat is conserved during the push; the vertical impulse
(m u sin 45 = 173.2 N s) goes into the water through the hull, so the
boat does not move vertically (say so); no water drag on the boat and
no air drag in the 0.5 s flight (chosen). Top band, the "no" case: the
FREE boat: the jumper leaves at u_x M / (M + m) = 1.0312 m/s over the
ground (horizontal), the boat recoils at u_x m / (M + m) = 1.4437 m/s;
flight 2 u_y / g = 0.5047 s, apex u_y^2 / 2g = 0.3123 m; the jumper
lands 0.5205 m from the bow's starting point, 0.4795 m short of the
dock, in the water; the boat is 0.7286 m back by then. Bottom band, the
"yes" case: the TIED boat (a taut rope to the dock, say so: the dock
takes the recoil): the jumper leaves at 2.4749 m/s horizontal, the same
0.5047 s flight and apex, lands 1.2491 m out, 0.2491 m past the edge, on
the dock. Ratio of the two landing distances exactly (M + m) / M =
2.4000. Integrate both flights with RK4 at dt = 1e-4 s (x, y of the
jumper; x of the boat), bisection for the floor level, a half-step
rerun agreeing within 1e-9 s, as a check against the closed forms;
print the momentum balance (zero horizontal momentum of jumper plus
free boat; 173.2 N s vertical impulse), the kinetic energy after the
push (tied 428.8 J; free 303.7 J, 251.6 in the jumper and 52.1 in the
boat), the table at 0.1 s steps (jumper x, y; boat x) and the
description variants.

Checks, not facts (the sim must print and compare; state them as checks):
flight 0.5047 s, apex 0.3123 m; tied lands 1.2491 m (2.4749 m/s); free
lands 0.5205 m (1.0312 m/s), 0.4795 m short, boat back 0.7286 m at
1.4437 m/s; ratio 2.4000; for the description: boats of 30 / 100 / 200
/ 400 kg land the free jump at 0.37 / 0.73 / 0.93 / 1.06 m; the free
jump clears 1.00 m only from a boat of at least 281 kg; from the 50 kg
boat it needs a takeoff of 4.85 m/s relative to the boat (u^2 = g L (M
+ m) / M; the research log's 6.72 m/s used another definition: print
yours and say which); kinetic energy 428.8 J tied against 303.7 J free.
Print the schedule in video time, the text widths and the layout
clearances.

Drawing: two-band layout (sims/deskchain style, read it whole; sims/
cartramp draws a launched ball with an arc trail and a landing mark;
sims/riverswim draws a water band; sims/pushpull draws a block on a
floor), side view, the free boat on top (the "no" case) and the tied
boat below; same scale, same clock. About 300 px per metre: the water
line across the band, the boat as a flat-bottomed hull block about 1.5
m long (450 px) with its bow at x about 560 and the dock as a block
whose edge is 1.00 m (300 px) right of the bow (x about 860) with its
top at the boat's floor height; the tied boat gets a short rope line
from its bow to the dock. The jumper is a dot or a small stick figure
on the bow (about 20 px) with a thin trail of its arc; the apex is 0.31
m (about 94 px); the landing spot is a gold mark with "48 cm short"
(24 px) in the top band and "25 cm past the edge" in the bottom band;
in the top band the jumper's dot drops below the water line at the end
of the flight (a small splash ring is enough) and the boat has slid
0.73 m (219 px) left: assert the boat's stern stays inside the band.
Readouts (28 px): left column "jumper N.NN m out" and the clock; right
column "boat N.NN m back" (top) or "boat tied: 0.00 m" (bottom) and
"height N.NN m". Gold event rows: top "free boat: 0.52 m, in the water"
(lit at the landing and held), bottom "tied boat: 1.25 m, on the dock"
(lit and held). Shown at 1/4 speed: cycle 5 s (300 frames): takeoff at
0.5 s of the cycle, landing at 0.5 + 4 * 0.5047 = 2.519 s, hold, reset
by a crossfade over the last 0.5 s of the cycle; 8 cycles in 40 s,
exactly periodic, the last frame equal to the first. The legend row
after the title: "same jump, same boat, 1/4 speed"; the shared clock in
real seconds since the takeoff. Overlay: "70 kg jumper, 50 kg boat, 1 m
gap | no seed" (measure it; shorten if over 950 px).

Day thirty-nine, second slot. Chosen because "does it matter if the boat
is tied" is a real everyday debate with a visible yes-or-no ending (one
jumper on the dock, the other in the water), the factor is exact ((M +
m) / M = 2.4) and the repeat is a natural loop. Question in the first
two seconds: "Jump from a boat to the dock. Does it matter if the boat
is tied?" (pre-test; a question-first form "Does it matter if the boat
is tied when you jump to the dock?" lands at 0.6 s). Keep the question
identical in the title, the hook and the payoff. Setup number: "one
meter" (the gap; one setup number only; the masses go to the overlay,
card and description). Payoff: tied, you land one point two five meters
out, on the dock; not tied, fifty two centimeters, in the water (the
two panel results; at most two numbers in the payoff beat). The
mechanism sentence must follow the picture: your push goes into the
boat as much as into you, and a light boat takes most of it, so the
boat shoots back and you barely move. Whisper risks: "tied" ("tide";
pre-test "tied up" and "the boat is tied"), "untied" and "loose"
(avoid; say "not tied" or "free"), "dock" (pre-test), "boat" (pre-
test), "dinghy" (keep it out of the narration), "fifty two
centimeters" (keep a single "centimeters" per take), avoid "do you",
avoid "too". Pre-test hooks with scripts/voiceover.sh and keep the one
whose question lands earliest under two seconds. Measure every fixed
text line with PIL before rendering and keep every line under 950 px,
and the title under 100 characters with no < or >. Music seed 119.
Templates: sims/deskchain (two-band layout, asserts, the clock, the
crossfade; read it whole), sims/cartramp (a launched ball, arc trail,
landing mark), sims/riverswim (a water band), sims/pushpull (a block on
a floor). Sim name boatjump: sims/boatjump/boatjump.py,
projects/boatjump/, media/boatjump/.

## Claim (expected; the sim's numbers replace these)

A 70 kg jumper pushes off a 50 kg boat at 3.5 m/s and 45 degrees toward
a dock 1 m away. With the boat tied the jumper lands 1.25 m out, on the
dock. With the boat free the push shoves the boat back at 1.44 m/s and
the jumper leaves at only 1.03 m/s over the water, lands 0.52 m out, 48
cm short, in the water; exactly 2.4 times shorter. Narrated: one meter
(setup); one point two five meters against fifty two centimeters
(payoff). Card: the question; the answer with 1.25 against 0.52 m; the
boat shoved 0.73 m back; 2.4 times shorter, (M + m) / M; a 100 kg boat
0.73 m, a 281 kg boat just makes it. Description: the model statement,
the equations, the two runs, the boat-mass variants, the takeoff needed,
the energies, the checks.

## Claim

A 70 kg jumper (a point mass) pushes off a 50 kg dinghy at 3.5 m/s and
45 degrees relative to the boat toward a dock edge 1.00 m away at floor
height; horizontal momentum of jumper plus boat conserved, the vertical
impulse (173.2 N s) into the water through the hull, no water drag and no
air drag (chosen), g = 9.807. Both flights last 0.5047 s and reach an
apex of 0.3123 m. With the boat tied the jumper leaves at 2.4749 m/s over
the ground and lands 1.2491 m out, 24.9 cm past the edge, on the dock.
With the boat free the push shoves the boat back at 1.4437 m/s (0.7286 m
by the landing) and the jumper leaves at only 1.0312 m/s, lands 0.5205 m
out, 48.0 cm short, in the water; exactly 2.4000 = (M + m) / M times
shorter. Kinetic energy after the push 428.8 J tied against 303.7 J free
(251.6 in the jumper, 52.1 in the boat). Narrated: one meter (setup); one
point two five meters, on the dock, against fifty two centimeters, in the
water (payoff). Card: the question; tied 1.25 m on the dock, free 0.52 m;
48 cm short, boat shoved 0.73 m back; 2.4 times shorter, exactly (M + m)
/ M; a 100 kg boat 0.73 m, 281 kg makes it; this boat needs a 4.85 m/s
takeoff.

## Evidence

### Measurements

Sim: sims/boatjump/boatjump.py with projects/boatjump/manifest.json (RK4
at dt = 1e-4 s on the jumper's x, y and the boat's x, bisection for the
landing at the floor level, half-step rerun, closed forms; deterministic,
no seed, no wall clock). Log: media/boatjump/measure.log (exit 0; the
full final log follows).

Brief checks (the sim prints "checks against the brief (21 checks, 0
failed)"): flight 0.5047 s (sim 0.504716), apex 0.3123 m (0.312277);
tied lands 1.2491 m (1.249108) at 2.4749 m/s (2.47487); free lands
0.5205 m (0.520462) at 1.0312 m/s (1.03120), 0.4795 m short (0.479538),
boat back 0.7286 m (0.728646) at 1.4437 m/s (1.44368); ratio 2.4000
(2.4000, diff 1.3e-13); vertical impulse 173.2 N s (173.241); boats of
30 / 100 / 200 / 400 kg land 0.37 / 0.73 / 0.93 / 1.06 m (0.374732 /
0.734769 / 0.925265 / 1.06307); mass to clear 1 m 281 kg (281.003);
takeoff to clear 1 m from the 50 kg boat 4.85 m/s (4.85147; the research
log's 6.72 m/s was a linear scaling of the speed with the distance, the
sim prints 6.7248 and says so); kinetic energy 428.8 J tied (428.75)
against 303.7 J free (303.698; 251.593 in the jumper, 52.105 in the
boat). Also printed: the RK4 landings agree with the closed forms within
3e-14 s and 1e-13 m, the half-step rerun within 5e-14 s; the horizontal
momentum of jumper plus free boat after the push 0.00e+00; the table at
0.1 s steps; the angle, takeoff and same-energy variants; the schedule;
the text widths (every line under 950 px, max 882 px for payoff line 5);
the layout clearances. All checks passed; no check failed.

Final measure.log:

```
Wed Oct  7 10:35:39 AM EEST 2026
warning: Git tree '/home/alex/personal/seedzero' is dirty
setup: side view, two panels on one clock, the same boat drawn the same way at the same scale: a jumper of 70 kg (a point mass) stands at the bow of a light dinghy of 50 kg on still water; the dock edge is 1 m from the bow at the boat's floor height; the legs give a takeoff of 3.5 m/s at 45 degrees relative to the boat (the textbook form: the push is defined by the relative speed); the horizontal momentum of jumper plus boat is conserved during the push; the vertical impulse goes into the water through the hull, so the boat does not move vertically; no water drag on the boat and no air drag in the flight (chosen); g = 9.807 m/s^2; top panel the boat is free, bottom panel a taut rope to the dock takes the recoil; both flights integrated by classical RK4 at 10000 steps per second (dt = 1e-04 s) on the jumper's x, y and the boat's x, the landing at the floor level located by bisection inside the step, checked against the closed forms and a half-step rerun; the run holds at the landing; shown at 1/4 speed on a 5 s cycle (300 frames) with the takeoff 0.5 s into the cycle, 8 cycles in 40 s; drawn at 260 px per metre with a 1.3 m hull; deterministic, no seed
takeoff: u_x = u cos a = 2.4749 m/s, u_y = u sin a = 2.4749 m/s; flight T = 2 u_y / g = 0.5047 s, apex u_y^2 / 2g = 0.3123 m; vertical impulse m u_y = 173.2 N s into the water through the hull
free boat (top panel): the jumper leaves at u_x M / (M + m) = 1.0312 m/s over the ground, the boat recoils at u_x m / (M + m) = 1.4437 m/s; RK4 from the takeoff: lands 0.504716 s = 0.5047 s later at x 0.520462 m = 0.5205 m out (closed form 2 u_y / g = 0.5047 s, v T = 0.5205 m; diffs +2.2e-14 s, -9.8e-15 m), 5048 steps; the table stays within 4.0e-14 m of v t and 5.5e-14 m of u_y t - g t^2 / 2; half-step rerun (dt = 5e-05 s): 0.504715761 s (-4.1e-14 s) at 0.520461575 m (+4.3e-14 m); 48.0 cm short of the dock, in the water; the boat is 0.7286 m back by then; vertical speed at the landing -2.4749 m/s
tied boat (bottom panel): the rope takes the recoil, so the jumper leaves at u_x = 2.4749 m/s over the ground and the boat stays at 0 m/s; RK4 from the takeoff: lands 0.504716 s = 0.5047 s later at x 1.249108 m = 1.2491 m out (closed form 2 u_y / g = 0.5047 s, v T = 1.2491 m; diffs +2.2e-14 s, +4.4e-14 m), 5048 steps; the table stays within 1.1e-14 m of v t and 5.5e-14 m of u_y t - g t^2 / 2; half-step rerun (dt = 5e-05 s): 0.504715761 s (-4.1e-14 s) at 1.249107780 m (-1.0e-13 m); 24.9 cm past the edge, on the dock; the boat has moved 0.0000 m; vertical speed at the landing -2.4749 m/s
ratio of the landing distances tied / free = 2.4000 = (M + m) / M = 2.4000; horizontal momentum of jumper plus free boat after the push m v_j + M v_b = 0.00e+00 kg m/s (zero: it was zero before); vertical impulse 173.2 N s; kinetic energy after the push: tied m u^2 / 2 = 428.8 J; free 303.7 J (251.6 in the jumper and 52.1 in the boat; less: the legs push against a boat that is moving away)
  t 0.0 s: free jumper x 0.0000 m, y 0.0000 m, boat x 0.0000 m; tied jumper x 0.0000 m, y 0.0000 m, boat x 0.0000 m
  t 0.1 s: free jumper x 0.1031 m, y 0.1985 m, boat x -0.1444 m; tied jumper x 0.2475 m, y 0.1985 m, boat x 0.0000 m
  t 0.2 s: free jumper x 0.2062 m, y 0.2988 m, boat x -0.2887 m; tied jumper x 0.4950 m, y 0.2988 m, boat x 0.0000 m
  t 0.3 s: free jumper x 0.3094 m, y 0.3011 m, boat x -0.4331 m; tied jumper x 0.7425 m, y 0.3011 m, boat x 0.0000 m
  t 0.4 s: free jumper x 0.4125 m, y 0.2054 m, boat x -0.5775 m; tied jumper x 0.9899 m, y 0.2054 m, boat x 0.0000 m
  t 0.5 s: free jumper x 0.5156 m, y 0.0116 m, boat x -0.7218 m; tied jumper x 1.2374 m, y 0.0116 m, boat x 0.0000 m
  t 0.5047 s (landing): free jumper x 0.5205 m, y 0.0000 m, boat x -0.7286 m; tied jumper x 1.2491 m, y 0.0000 m, boat x 0.0000 m
for the description: a 30 kg boat, free: the jumper at 0.7425 m/s lands 0.3747 m = 0.37 m out (short), the boat 0.8744 m back (closed 0.3747 m); a 100 kg boat, free: the jumper at 1.4558 m/s lands 0.7348 m = 0.73 m out (short), the boat 0.5143 m back (closed 0.7348 m); a 200 kg boat, free: the jumper at 1.8332 m/s lands 0.9253 m = 0.93 m out (short), the boat 0.3238 m back (closed 0.9253 m); a 400 kg boat, free: the jumper at 2.1063 m/s lands 1.0631 m = 1.06 m out (on the dock), the boat 0.1860 m back (closed 1.0631 m); the free jump clears 1 m only from a boat of at least M = m D / (u_x T - D) = 281.0 kg (check: a 281.0 kg boat lands 1.0000 m); from the 50 kg boat the free jump needs a takeoff of u = sqrt(g D (M + m) / (M sin 2a)) = 4.8515 m/s = 4.85 m/s relative to the boat (check: lands 1.0000 m; the landing distance grows as u^2); the research log's 6.7248 m/s scaled the speed linearly with the distance, which is not this definition; takeoff at 30 degrees: tied 1.0818 m, free 0.4507 m (flight 0.3569 s); takeoff at 60 degrees: tied 1.0818 m, free 0.4507 m (flight 0.6181 s); takeoff 2.5 m/s: tied 0.6373 m, free 0.2655 m; takeoff 4 m/s: tied 1.6315 m, free 0.6798 m; an alternative model with the same push energy instead of the same relative speed (v_j = u_x sqrt(M / (M + m)) = 1.5975 m/s) lands 0.8063 m, still short of 1 m; not used
checks against the brief (21 checks, 0 failed): flight (s): brief 0.5047, sim 0.504716, diff +1.6e-05: ok; apex (m): brief 0.3123, sim 0.312277, diff -2.3e-05: ok; tied lands (m): brief 1.2491, sim 1.24911, diff +7.8e-06: ok; tied jumper (m/s): brief 2.4749, sim 2.47487, diff -2.6e-05: ok; free lands (m): brief 0.5205, sim 0.520462, diff -3.8e-05: ok; free jumper (m/s): brief 1.0312, sim 1.0312, diff -2.6e-06: ok; free short (m): brief 0.4795, sim 0.479538, diff +3.8e-05: ok; boat back (m): brief 0.7286, sim 0.728646, diff +4.6e-05: ok; boat speed (m/s): brief 1.4437, sim 1.44368, diff -2.4e-05: ok; ratio: brief 2.4, sim 2.4, diff +1.3e-13: ok; vertical impulse (N s): brief 173.2, sim 173.241, diff +4.1e-02: ok; mass to clear 1 m (kg): brief 281, sim 281.003, diff +2.9e-03: ok; takeoff to clear 1 m (m/s): brief 4.85, sim 4.85147, diff +1.5e-03: ok; kinetic energy tied (J): brief 428.8, sim 428.75, diff -5.0e-02: ok; kinetic energy free (J): brief 303.7, sim 303.698, diff -2.1e-03: ok; free jumper energy (J): brief 251.6, sim 251.593, diff -7.1e-03: ok; free boat energy (J): brief 52.1, sim 52.105, diff +5.0e-03: ok; 30 kg boat lands (m): brief 0.37, sim 0.374732, diff +4.7e-03: ok; 100 kg boat lands (m): brief 0.73, sim 0.734769, diff +4.8e-03: ok; 200 kg boat lands (m): brief 0.93, sim 0.925265, diff -4.7e-03: ok; 400 kg boat lands (m): brief 1.06, sim 1.06307, diff +3.1e-03: ok
schedule (video time, 1/4 speed): cycles of 5 s start at -1.00, 4.00, 9.00, 14.00, 19.00, 24.00, 29.00, 34.00, 39.00 s (the first 1.00 s before the first frame); both jumpers take off 0.5 s into each cycle at 4.50, 9.50, 14.50, 19.50, 24.50, 29.50, 34.50, 39.50 s; the apex 1.01 s after the takeoff at 0.51, 5.51, 10.51, 15.51, 20.51, 25.51, 30.51, 35.51 s; both land 2.019 s after the takeoff at 1.52, 6.52, 11.52, 16.52, 21.52, 26.52, 31.52, 36.52 s (2.519 s into the cycle; both event rows and the gold marks light); the free jumper's dot runs on to the water line 9.2 cm under the floor level 0.140 s later at 1.66, 6.66, 11.66, 16.66, 21.66, 26.66, 31.66, 36.66 s (the splash ring runs 0.5 s and the dot sinks 12 px over 0.4 s, drawing details); the run holds at the landing; the reset crossfade runs over the last 0.5 s of each cycle (from 3.50, 8.50, 13.50, 18.50, 23.50, 28.50, 33.50, 38.50 s; the readouts out over its first half and in over its second); on the first frame the cycle is 1.00 s in (0.125 s real after the takeoff: the free jumper air at x 0.13 m, y 0.23 m, the tied jumper at x 0.31 m); title until 3 s; payoff card from 24.6 s; the title fades back in over the last 0.5 s and the last frame repeats the first (the scene is periodic: 40 s holds exactly 8 cycles)
text widths (the on-screen strings verbatim): overlay@34 843 px '70 kg jumper, 50 kg boat, 1 m gap | no seed', title line 1@56 806 px 'Does it matter if the boat', title line 2@56 696 px 'is tied when you jump', title line 3@56 390 px 'to the dock?', legend@40 760 px 'same jump, same boat, 1/4 speed', clock@28 385 px '0.505 s after the takeoff', clock held@28 300 px 'on the bow, at rest', label free@40 436 px 'free boat (not tied)', out free@28 292 px 'jumper 0.52 m out', air free@28 208 px 'flight 0.505 s', boat free@28 273 px 'boat 0.73 m back', height free@28 220 px 'height 0.31 m', event free@40 696 px 'free boat: 0.52 m, in the water', mark free@24 161 px '48 cm short', label tied@40 628 px 'tied boat (rope to the dock)', out tied@28 292 px 'jumper 1.25 m out', air tied@28 208 px 'flight 0.505 s', boat tied@28 272 px 'boat tied: 0.00 m', height tied@28 220 px 'height 0.31 m', event tied@40 683 px 'tied boat: 1.25 m, on the dock', mark tied@24 277 px '25 cm past the edge', on the bow@28 176 px 'on the bow', payoff line 1@40 749 px 'does it matter if the boat is tied?', payoff line 2@40 872 px 'tied: 1.25 m, on the dock; free: 0.52 m', payoff line 3@40 863 px '48 cm short; boat shoved 0.73 m back', payoff line 4@40 851 px '2.4 times shorter, exactly (M + m) / M', payoff line 5@40 882 px 'a 100 kg boat: 0.73 m; 281 kg makes it', payoff line 6@40 771 px 'this boat needs a 4.85 m/s takeoff'
row check: the left column ends at x 668 px, the right column starts at x 767 px; both end 136 px under the band top; the floor level (the boat's floor and the dock top) is 330 px under the band top, the water line 354 px, the hull bottom 374 px; the hull spans x 222 to 560 px at the start and x 33 to 371 px when the free jumper lands (recoil 189 px); the dock starts at x 820 px (gap 260 px); the jumpers land at x 695 px (free, over the water) and 885 px (tied, on the dock); the figure's highest pixel at the apex is 222 px under the band top (81 px of rise); the gold mark labels are centred at x 758 and 852 px (677 to 838 and 714 to 991 px) 180 px under the band top over the dashed gap line at 206 px; the event rows span 458 to 502 px under the band top and x 92 to 788 px (widest 696 px, centred on 440) in the water left of the dock; the sunk figure reaches 370 px under the band top; each band is 550 px tall (y 330 to 880 and 880 to 1430); the caption band starts at y 1440; the title rows end at y 330 and the overlay band ends at y 130
exit 0
Wed Oct  7 10:35:40 AM EEST 2026
```

### Production

- Manifest: projects/boatjump/manifest.json (fps 60, 40 s, 1/4 speed,
  cycle 5 s, takeoff 0.5 s into the cycle, first_cycle_at -1.0, reset
  crossfade 0.5 s, splash 0.5 s, sink 12 px over 0.4 s, 260 px/m with
  the bow at x 560, the floor level 330 px under the band top, the water
  line 24 px under it, a 1.3 m hull 44 px deep, title until 3 s,
  payoff_t 24.6 s, hold 0.6 s, loop fade 0.5 s, music seed 119, music
  gain 0.18, voice offset 0.6, caption_y 0.75, overlay "70 kg jumper, 50
  kg boat, 1 m gap | no seed").
- Layout: two bands (free boat y 330-880, tied boat 880-1430), label
  rows at 40 px under the band top ("free boat (not tied)" coral, "tied
  boat (rope to the dock)" teal), readouts at 84 and 120 (left "jumper
  N.NN m out" and "on the bow" / "in the air N.NNN s" / "flight 0.505
  s"; right "boat N.NN m back" or "boat tied: 0.00 m" and "height N.NN
  m"), gold event rows in the water at 480 px under the band top centred
  on x 440 ("free boat: 0.52 m, in the water", "tied boat: 1.25 m, on
  the dock"); the water from the water line to the band bottom, the dock
  block from x 820 with its top at the floor level on two pilings, the
  hull as a tapered block ending at the bow (x 222 to 560 at the start;
  x 33 to 371 when the free jumper lands); the tied boat has a taut rope
  with a cleat at each end; the jumper is a 22 px stick figure with a
  thin trail of its arc; at the landing a gold dot at the landing point,
  dashed gold ticks at the landing point and the dock edge up to a
  dashed gap line at 206 px under the band top with the label ("48 cm
  short", "25 cm past the edge", 24 px) at 180 px, above the apex (the
  figure's top at 222 px); the free jumper's figure runs on to the water
  line with a splash ring and sinks 12 px (drawing details, printed).
- Schedule (video time): takeoffs 4.50, 9.50, ..., 39.50 s; landings
  1.52, 6.52, 11.52, 16.52, 21.52, 26.52, 31.52, 36.52 s; crossfades
  from 3.50, 8.50, ..., 38.50 s. Frame 0: 0.125 s after a takeoff, both
  jumpers in the air (free 0.13 m out, tied 0.31 m), the free boat 0.18
  m back.
- Smoke frames viewed: media/boatjump/smoke-{0.0,1.0,1.52,1.7,2.1,3.4,
  5.0,6.6,8.0,8.7,31.0}.png; viewed 0.0 (title over both jumpers in
  flight), 1.7 (both landed: the free figure at the water line with the
  splash ring, the gold marks and labels, both event rows, the free boat
  0.73 m back), 3.4 (legend and clock 0.505 s, both held), 5.0 (next
  cycle, 0.125 s in), 8.7 (the crossfade: both boat positions blended,
  the rows dimmed), 31.0 (the card up). No drawing fix was needed after
  the smoke pass; before it the measure asserts caught two card lines
  (992 and 981 px, shortened) and the mark line meeting the apex figure
  (moved from 222/198 to 206/180 px).
- Render: media/boatjump/render.log, footage.mp4 (2400 frames, 27 s);
  loop check 0 px (max channel difference 0); periodicity check 0 px;
  loop step 2467 px between the last two frames.
- Hook pre-tests (media/boatjump/hooks/pretest.log; all five passed the
  round trip on the first take): hook1 "Does it matter if the boat is
  tied when you jump to the dock? Same jumper, same push, one meter to
  the dock." ok, question first, no leading silence at -35 dB / 0.22 s
  (question at 0.6 s of video); hook2 "Jump from a boat to the dock.
  Does it matter if the boat is tied?" (the brief's form) ok, but the
  question starts after the pause at 1.66 s of voice = 2.26 s of video,
  past two seconds; hook3 "... tied up when you jump ..." ok, leading
  silence 0.23 s (question at 0.83 s); hook4 "Does it matter if the boat
  is tied? Jump from the boat to the dock, one meter away." ok at 0.6 s;
  hook5 "Boat tied, or boat free: does it matter when you jump to the
  dock?" ok, "does it matter" at 2.05 s of voice = 2.65 s of video.
  Chosen: hook1. Word test (words.txt, 100 words, 28.5 s) passed on the
  first take: "The boat is tied", "tied up", "Tied, you land on the
  dock", "Not tied, you land in the water", "Below, a rope holds it to
  the dock", the mechanism sentence, "Fifty two centimeters, in the
  water", "One point two five meters out, on the dock", "shown four
  times slower", "On top the boat is free", "Watch the free boat",
  "Yes.", "Every run the same".
- Narration: projects/boatjump/narration.txt, 109 words; the question is
  the first sentence (spoken 0.71-3.9 s of video; first caption enabled
  from 0.826 s after the 0.23 s leading silence) and is repeated word
  for word before the payoff ("So, does it matter if the boat is tied
  when you jump to the dock?"); the payoff answers in the same words
  ("Yes. Tied, you land one point two five meters out, on the dock. Not
  tied, fifty two centimeters, in the water."). One setup number (one
  meter, plus the 1/4 speed note), two payoff numbers (the two panel
  results); the mechanism sentence verbatim from the brief.
- Voice: pass 1 ok on the first take (media/boatjump/voice.log: "ok:
  transcript matches narration (29.802812s)"); no mishearing in the full
  take (in the per-piece timing run whisper wrote "duck" for "dock" in
  one piece; the full round trip matched). Timing
  (media/boatjump/timing.log, offset 0.6): question 0.71-3.9 (whisper
  splits the chunk at "Same jumper"); "Same push." to 5.55; "one meter
  to the dock" 5.55-6.94 (takeoff 4.50, landing 6.52); "shown four times
  slower" 6.94-8.51; "On top the boat is free" 8.51-10.10 (takeoff
  9.50); "Below, a rope holds it to the dock" 10.10-12.13 (landing
  11.52); "Watch the free boat" 12.13-13.37; mechanism 13.37-20.44
  (takeoff 14.50, landing 16.52, takeoff 19.50); the question again
  20.44-23.54 (landing 21.52); "Yes, tied, you land 1.25 meters out, on
  the dock, not tied, 52 centimeters in the water" 23.54-30.40 (takeoff
  24.50, card from 24.6 as "one point two five" is spoken, landing 26.52
  under "on the dock", the free jumper in the water under "fifty two
  centimeters, in the water", takeoff 29.50). Voice 29.80 s, ends at
  30.40 s of video. 12 silences at -35 dB / 0.22 s
  (media/boatjump/silences.log).
- Compose: media/boatjump/compose.log: music seed 119, 40.00 s; captions
  16 pauses detected, 16 matched, max chunk start shift 1.171 s against
  word-count timing (no fallback); final.mp4 40.000000 s.
- Text widths (measure.log): overlay 843, title rows 806 / 696 / 390,
  legend 760, labels 436 / 628, readouts at most 385, event rows 696 /
  683, marks 161 / 277, payoff lines 749 / 872 / 863 / 851 / 882 / 771
  px; all under 950 px, asserted.

### Local QA

- media/boatjump/final.mp4: md5 bf1c16ea96ba77e6cb395e3eaf2c2a87,
  4295470 bytes; ffprobe h264 1080x1920 60/1, aac 22050 Hz mono,
  duration 40.000000; atoms ftyp@0 moov@32 free@44860 mdat@44868
  (faststart).
- Caption text against the narration: 33 drawtext chunks (the first is
  the overlay); the joined caption text equals narration.txt word for
  word (checked by script after undoing the drawtext escapes). The first
  caption "Does it matter if" is enabled 0.826-1.721 s, "the boat is
  tied" 1.721-2.616, "when you jump to the" 2.616-3.736.
- signalstats YMAX on footage.mp4 over all 2400 frames: caption band
  rows 1440-1530 = 28 (background), overlay band rows 96-130 = 28:
  nothing drawn under the captions or the overlay.
- Full-resolution frames viewed (media/boatjump/qa-T.png): 0.00 overlay,
  three-row title "Does it matter if the boat / is tied when you jump /
  to the dock?", both jumpers 0.125 s into a flight (0.13 / 0.31 m out,
  height 0.23 m), the free boat 0.18 m back, the tied boat's rope, no
  caption; 1.0 caption "Does it matter if", jumpers at 0.39 / 0.93 m,
  the free boat 0.54 m back; 2.1 caption "the boat is tied", both landed
  at 0.52 / 1.25 m with the gold marks "48 cm short" and "25 cm past the
  edge", the free figure in the water with the splash ring, both gold
  event rows, "boat 0.73 m back"; 16.0 legend and clock 0.375 s, caption
  "into you, and a", both in the air; 25.0 the card rising (dim gold),
  caption "Tied, you land one", jumpers 0.125 s into the flight; 26.4
  the card up, caption "meters out, on the", 0.475 s after the takeoff
  (the tied jumper over the dock, the free one over the water at 0.07
  m); 29.0 both jumpers on the bow ("on the bow, at rest"), caption
  "centimeters, in the", card; 39.983 identical to frame 0 (title back,
  no caption, no card). media/boatjump/sheet.png viewed: 40 cells, the
  captions in order, the card from 25 s, no clipping, the loop closes.
- Question timing: on screen from frame 0 (title) and spoken from 0.71
  s (first caption enable 0.826 s).
- Narrated numbers: "one meter" (manifest gap_m 1.0, log "1 m from the
  bow"), "four times slower" (1/4 speed), "one point two five meters"
  (log 1.249108 m = 1.2491 m), "fifty two centimeters" (log 0.520462 m
  = 0.5205 m). Description and title numbers checked by script against
  measure.log (82 distinct numbers, none missing).

### Metadata

projects/boatjump/metadata.json written by a Python script with asserts
(title 98 chars, description 3666 chars, 11 tags, ASCII, no < or >;
every number in the title and description present in measure.log);
ls -l confirmed the file. Title: "Does it matter if the boat is tied
when you jump to the dock? Tied 1.25 m on the dock, free 0.52 m".
privacyStatus private, categoryId 27, containsSyntheticMedia true,
selfDeclaredMadeForKids false.

### Deviations from the brief

- Scale 260 px/m with a 1.3 m hull (338 px) and the bow at x 560
  instead of 300 px/m with a 1.5 m hull: with the brief's numbers the
  free boat's stern would sit at x -109 after the 219 px recoil, outside
  the band, and the brief asks to assert it stays inside; at 260 px/m
  the stern lands at x 33 (asserted > 16). Gap 260 px, apex 81 px,
  recoil 189 px, tied landing at x 885.
- The gold mark labels sit above the arc (180 px under the band top over
  a dashed gap line at 206 px, with dashed ticks down to the floor level
  at the landing point and the dock edge) rather than at the landing
  height: a label at floor height next to the dock edge would cross the
  tied jumper's descending arc.
- Gold event rows in the water (480 px under the band top, centred on x
  440) rather than in the right column, so they stay clear of the marks
  and the dock.
- The left column's second readout is "on the bow" / "in the air N.NNN
  s" / "flight 0.505 s" (the per-band clock from the takeoff) and the
  shared clock sits at y 290 (deskchain style); the run holds at the
  landing, so the shared clock holds at 0.505 s (the free boat, with no
  water drag, would otherwise glide out of the band before the
  crossfade; stated in measure.log).
- The free jumper's figure runs on past the floor level to the water
  line (9.2 cm lower, 0.14 s of video) and sinks 12 px with a splash
  ring: drawing details in video time after the measured landing,
  printed in the schedule.
- Hook: the question-first form "Does it matter if the boat is tied when
  you jump to the dock?" (the brief's alternative) instead of "Jump from
  a boat to the dock. Does it matter if the boat is tied?": both passed
  the round trip, but the latter's question starts at 2.26 s of video.
  Identical in the title, the hook and the payoff.
- Card line 3 "48 cm short; boat shoved 0.73 m back" and line 5 "a 100
  kg boat: 0.73 m; 281 kg makes it" (the longer forms measured 992 and
  981 px).
- The narration is 109 words but the voice read it in 29.80 s (3.66
  words a second, faster than the day 38 pace), so it ends at 30.40 s of
  video and the last 9.6 s carry the card, the loop and the music only.
- Takeoff needed from the 50 kg boat: 4.85 m/s (u^2 scaling, as the
  brief's own closed form); the research log's 6.72 m/s is printed and
  named as a linear scaling.

## Niche note

Appended to the "Jump from a boat, tied or free" bullet in docs/niche.md:
[produced 2026-10-07 as "Does it matter if the boat is tied when you jump
to the dock? Tied 1.25 m on the dock, free 0.52 m"; measured flight
0.5047 s, apex 0.3123 m, tied 2.4749 m/s lands 1.2491 m (24.9 cm past the
edge), free 1.0312 m/s lands 0.5205 m (48.0 cm short) with the boat
0.7286 m back at 1.4437 m/s, ratio 2.4000 = (M + m) / M, energy 428.8
against 303.7 J, 30 / 100 / 200 / 400 kg boats 0.37 / 0.73 / 0.93 / 1.06
m, 281.0 kg clears 1 m, the 50 kg boat needs 4.85 m/s (u^2 scaling; the
6.72 m/s was a linear scaling); RK4 dt 1e-4 s against the closed forms,
21 checks, 0 failed; task 20261007-102007]

## Upload

- Attempt 2 of 5 (quota day 2026-10-07T10:00 EEST) recorded at 2026-10-07T10:58:19+03:00 before scripts/yt-upload.py boatjump; one earlier attempt since the boundary (tray, succeeded).
- Uploaded private as gV_1nhnppGU at 2026-10-07T07:58:21Z (videos.insert 1,600 units). yt-qa.py --wait --publish: gate 15 of 15 on the first processed read, published at 2026-10-07T10:58:53+03:00, re-read public, 53 units. https://youtu.be/gV_1nhnppGU
