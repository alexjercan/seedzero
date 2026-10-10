# Produce short: paper cup or straight can, the same nudge 40 cm from the edge, which one rolls off the desk

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day42

## Goal

Backlog idea (trend research 2026-10-10, task 20261010-100329, pillar 2
chaos and physics, desk mechanics; read the full "Paper cup or straight
can" bullet at the end of docs/niche.md): a paper cup and a can on a
desk given the same nudge toward the edge; the can rolls straight off,
the cup rolls in a circle and comes back.

Orchestrator notes (2026-10-10; closed forms in /tmp/day42/closed.py
with the log /tmp/day42/closed.log; research script
/tmp/day42/research/cup.py with cup.log; g = 9.807 m/s^2). Read
/tmp/day42/producer-conventions.md first. The model: a thin-walled 8 oz
paper cup (top diameter 8.0 cm, bottom diameter 5.5 cm, height 9.0 cm,
the wall plus a bottom disc of the same sheet, so the wall carries about
89 percent of the mass) lying on its side, and a straight can 8.0 cm in
diameter, both on a level desk with grip 0.5 (chosen, say so), both
starting 40 cm from the edge and both nudged to a centre speed of 0.30
m/s (say: the same nudge, chosen). The CAN rolls straight without loss
and leaves the edge at 0.40 / 0.30 = 1.333 s, then falls 0.75 m in
0.391 s (draw it dropping out of the frame). The CUP is a slice of a
cone: slant length sqrt(9.0^2 + 1.25^2) = 9.086 cm, half-angle alpha
with sin alpha = 1.25 / 9.086, 7.907 deg; rolling without slipping it
pivots about its apex, which lies 2.75 / sin alpha = 19.99 cm beyond the
small rim and 4.0 / sin alpha = 29.08 cm from the large rim along the
contact line; both rims run on circles of those radii about the apex,
the cup's centre of mass (about 24 cm from the apex along the axis)
rides a circle of about 23.8 cm radius at a constant height, the axis
turns at v / rho, one lap in about 5.0 s, and the cup spins exactly 1 /
sin alpha = 7.269 turns per lap. Integrate the lap as a kinematic
rolling cone (the apex fixed, the generator in contact, the cup turning
about its own axis at omega = v_cm / (rho sin alpha)) and print the
checks; the dynamics are a closed form, so print them too.

Checks, not facts (the sim must print and compare; exact where exact):
slant 9.086 cm; alpha 7.907 deg; apex 19.99 cm from the small rim and
29.08 cm from the large rim; l1 / r = l2 / R = 7.269 = turns per lap (no
slip on both rims); the CM circle radius (print it; research 23.82 cm,
orchestrator's cruder CM 24.05 cm; the sim's value stands) and lap time
2 pi rho / v (about 4.99 to 5.04 s); CM height constant to 1e-9 (energy
kept); friction needed v^2 / (g rho) = 0.038 under 0.5 (0.107 at 0.5
m/s); the normal resultant from dL/dt = Omega x L lies inside the 19.99
to 29.08 cm contact segment (print its position, about 23.6 cm); the
cup's track never comes closer to the edge than about 10.9 cm (the
large-rim circle reaches 29.08 cm from the start line against 40 cm);
the can off the desk at 1.333 s, down 0.75 m at 1.724 s; variants for
the description: a 12 oz cup and a 4 oz cup (print their apex distances
and turns per lap), and a straight cup (alpha 0) that would roll off
like the can.

Drawing: one TOP-DOWN desk scene (sims/tray draws a shared surface top
down; read it whole), 1,200 px per metre: the desk 90 cm wide by 80 cm
deep (1080 by 960 px) filling the frame from y 330 to 1290 with the
desk EDGE along the top at y 330 and the floor drawn beyond it (y 168
to 330 under the title rows: a dark drop zone; the can falls up and out
through it, shrinking with depth); both objects start 40 cm = 480 px
below the edge (y 810) with a start line; the can on the right (an 8 by
12 cm rectangle, 96 by 144 px, seen from above with a stripe across it
so the roll shows), the cup on the left (a trapezoid 66 to 96 px wide
and 108 px long with a stripe along one generator, its small end to the
left so the apex sits 240 px to its left at 19.99 cm = 240 px beyond
the small rim; the large-rim circle of radius 29.08 cm = 349 px must
stay inside the desk: assert); a dot at the apex and the dashed rim
circle drawn after the first quarter lap; thin trails of the can's
centre and the cup's centre. Label rows (40 px, coloured): "paper cup"
(coral) and "straight can" (teal), both "same nudge, 40 cm from the
edge". Readouts (28 px): left column "cup: turned N.N times" and "cup:
lap N.NN" (live) and the clock; right column "can: moved NN cm" (live).
Gold event rows: "can: off the desk at 1.33 s" and "cup: back at the
start at 5.0 s" (each lit at its event, both held). Real time, cycle 8
s (480 frames): the nudge 0.5 s into the cycle (both at rest before it,
finger marks approaching: motion in frame one), the can at the edge at
1.83 s and gone by 2.3 s, the cup back at its start point at about 5.5
s; hold to 7.5 s, crossfade reset over the last 0.5 s; 5 cycles in 40
s, exactly periodic, the last frame equal to the first. If the cup's
lap reads as slow on the smoke frames, keep real time (the can's exit
needs it) and say so. Legend row after the title: "same desk, same
nudge, real time". Overlay: "8 oz cup and 8 cm can, grip 0.5 | no seed"
(measure it).

Day forty-two, second slot. Chosen because every viewer has rolled a
cup on a desk, the two objects end visibly apart (one on the floor, one
back where it started), the answer is a clean yes-or-no, and the nudge
repeats as a loop. Question in the first two seconds: "Nudge a paper cup
and a can the same: which one rolls off the desk?" (pre-test; it is the
first sentence; "Paper cup or can: which one rolls off the desk?" is
the fallback). Keep the question identical in the title, the hook and
the payoff. Setup number: "forty centimeters from the edge" (one setup
number only; the 0.3 m/s, the cup sizes and the grip go to the overlay,
card and description). Payoff: "The can rolls off at one point three
seconds. The cup circles and is back in five seconds." (at most two
numbers in the payoff beat). The mechanism sentence must follow the
picture: a cup is a slice of a cone, so its wide end must travel farther
each turn than its narrow end, and it curves round the point where the
cone would come to a tip. Whisper risks: "can" as a noun (pre-test; "tin
can" is the fallback), "paper cup", "circles", "nudge", "one point
three", "rolls off"; avoid "apex" in narration, avoid "do you", avoid
"too". Pre-test hooks with scripts/voiceover.sh and keep the one whose
question lands earliest under two seconds. Measure every fixed text line
with PIL before rendering and keep every line under 950 px, and the
title under 100 characters with no < or >. Music seed 125. Templates:
sims/tray (shared surface, top down, read it whole), sims/turntable and
sims/coinroll (rolling with a stripe), sims/pencil (an object leaving
the frame, finger mark, asserts), sims/deskchain (clock, crossfade,
asserts). Sim name cuproll: sims/cuproll/cuproll.py, projects/cuproll/,
media/cuproll/.

## Claim (expected; the sim's numbers replace these)

A paper cup and a can on a desk, 40 cm from the edge, get the same
nudge, 0.30 m/s. The can rolls straight and is off the desk at 1.33 s.
The cup rolls in a circle about the tip of its cone, 29 cm from its big
rim, turns 7.27 times, and is back at its start in about 5.0 s, never
closer than 11 cm to the edge. Narrated: forty centimeters from the edge
(setup); off at one point three seconds against back in five seconds
(payoff). Card: the question; the answer (can: off at 1.33 s; cup: back
at 5.0 s after 7.27 turns); the cone tip 29 cm from the big rim.
Description: the model statement, the geometry, both runs, the cup-size
variants, the no-slip check, the checks.

## Claim

A thin-walled 8 oz paper cup (top 8 cm, bottom 5.5 cm, 9 cm tall) and
an 8 by 12 cm can lie on a level desk with their axes parallel to the
edge, 40 cm from it, grip 0.5 (chosen). Each gets the same nudge: its
centre moves off at 0.3 m/s (chosen). The can rolls straight, its
centre passes the edge 1.333 s after the nudge, it falls 0.391 s from
the 75 cm desk and lands 11.73 cm out. The cup is a slice of a cone:
slant 9.086 cm, half-angle 7.907 deg; rolling without slipping it
pivots about the apex 19.99 cm beyond the small rim and 29.08 cm from
the large rim, so it turns 1 / sin alpha = 7.269 times per lap. Its
centre of mass (24.05 cm from the apex along the axis) rides a circle
of radius 23.82 cm at a constant height of 3.309 cm; the axis turns at
1.2592 rad/s, the cup spins at 9.1533 rad/s, and one lap takes 4.990 s
(RK4 4.989821 s, closed form 4.989821 s). It never comes closer than
10.92 cm to the edge (the large rim's circle reaches 29.08 cm from the
start line against 40 cm). Friction needed 0.0385 of the weight (0.107
at 0.5 m/s), under the desk's 0.5; the normal resultant sits 24.08 cm
from the apex, inside the 19.99 to 29.08 cm contact segment. Narrated:
forty centimeters from the edge (setup); "The can rolls straight off at
one point three seconds. The cup circles and is back in five seconds."
(payoff). Card: the question; can: straight off the desk at 1.33 s;
cup: circles, back at the start at 4.99 s; the cone tip is 29.1 cm from
the big rim; 7.27 turns a lap, 10.9 cm from the edge.

## Evidence

### Measurements

`nix develop -c python3 sims/cuproll/cuproll.py --measure-only` (final
run 11:01:48 to 11:01:50, exit 0, saved as media/cuproll/measure.log; the same text
is printed again by the footage render at 11:01:50):

```
Sat Oct 10 11:01:48 AM EEST 2026
setup: one desk seen from above, real time: a thin-walled 8 oz paper cup (top diameter 8 cm, bottom diameter 5.5 cm, height 9 cm; the wall plus a bottom disc of the same sheet) lying on its side and a straight can 8 cm in diameter and 12 cm long, both with their axes parallel to the desk edge, both 40 cm from the edge, on a level desk with grip 0.5 (chosen); each gets the same nudge: its centre moves off toward the edge at v = 0.3 m/s (chosen); g = 9.807 m/s^2; the can rolls straight without loss (chosen), leaves the desk as its centre passes the edge and falls freely from a 75 cm desk; the cup rolls without slipping as a slice of a cone, pivoting about the cone's apex; its rotation matrix integrated by RK4 at 100 steps per frame (dt = 1.67e-04 s) for 5.2 s; the dynamics in closed form; shown in real time on a 8 s cycle (480 frames) with the nudge 0.5 s into the cycle, 5 cycles in 40 s; drawn at 1200 px per metre; deterministic, no seed
cone: slant length sqrt(9^2 + 1.25^2) = 9.0864 cm = 9.086 cm; sin alpha = 1.25 / 9.086 = 0.13757, half-angle alpha = 7.9072 deg = 7.907 deg; the apex lies l1 = rb / sin alpha = 19.990 cm = 19.99 cm beyond the small rim and l2 = Rt / sin alpha = 29.076 cm = 29.08 cm from the large rim along the contact line (l2 - l1 = 9.086 cm, the slant); both rims run on circles of those radii about the apex, so the cup turns l1 / rb = 7.2691 = l2 / Rt = 7.2691 = 1 / sin alpha = 7.2691 = 7.269 times per lap; a straight cup or can (alpha = 0) has its apex at infinity and rolls straight
mass: wall 192.684 cm^2 of sheet, bottom 23.758 cm^2: the wall carries 0.8902 = 89.0 percent of the mass; wall CM at (2/3)(l2^3 - l1^3)/(l2^2 - l1^2) = 24.814 cm along the slant; the cup's centre of mass 24.053 cm = 24.05 cm from the apex along the axis (quadrature 24.053 cm, mass 1.000000 of the closed form), so it rides a circle of radius rho = d_cm cos alpha = 23.825 cm = 23.82 cm at the constant height d_cm sin alpha = 3.309 cm; inertia about the apex per unit sheet density: I1 = 128173.814 cm^4 (perpendicular to the axis; quadrature 128173.813), I3 = 2359.8913 cm^4 (about the axis; quadrature 2359.8911)
cup rolling (closed form): the axis turns about the vertical through the apex at Omega = v / rho = 1.2592 rad/s; the angular velocity lies along the contact line, |omega_g| = Omega cot alpha = 9.0662 rad/s, and in the frame turning with the axis the cup spins about its own axis at Omega / sin alpha = 9.1533 rad/s = 1.4568 turns/s; one lap 2 pi rho / v = 4.9898 s = 4.990 s = 4.99 s = 5.0 s, 7.2691 turns; N = m g (the height is constant); friction needed v^2 / (g rho) = 0.0385 = 0.039 of the weight toward the apex along the contact line, under the desk's 0.5 by a factor 13.0; friction acts along the contact line through the apex, so its torque about the apex is zero; the normal resultant from dL/dt = Omega z x L: x_N = rho + Omega^2 cot alpha (I1 sin^2 alpha + I3 cos^2 alpha) / (m g) = 24.080 cm = 24.08 cm from the apex, 0.25 cm beyond the centre of mass, inside the 19.99 to 29.08 cm contact segment
cup rolling (RK4 on the rotation matrix, 31200 steps): back through its start direction after 4.989821 s (closed form 4.989821 s, diff -9.8e-15 s); the centre of mass back at its start after 4.989827 s (closest approach 3.605 um); it turns 7.269113 times per lap (closed form 7.269113, diff -3.3e-13); no slip: the arc of the large rim that has touched, Rt x turn, matches l2 x the contact line's turn within 8.6e-14 m at every step, the small rim within 5.9e-14 m; the axis's height stays within 0.0e+00 of sin alpha, so the centre of mass height 3.309 cm is constant within 0.0e+00 m (energy kept); the centre's speed stays within 5.5e-10 m/s of 0.3; orthonormality drift 1.4e-14; half-step rerun: lap 4.989821075 s (+1.8e-15 s), turns 7.269112738; dL/dt by central differences puts the normal resultant at 24.080 cm (spread 5.4e-13 cm over the lap; closed form 24.080); dL_z/dt at most 5.2e-16 (no vertical torque)
can: rolls straight without loss at 0.3 m/s (spin 7.500 rad/s, 1.592 turns over the 40 cm); its centre reaches the edge after 1.3333 s = 1.333 s = 1.33 s = 1.3 s; it falls freely from the 75 cm desk for sqrt(2 H / g) = 0.3911 s = 0.391 s, down at 1.7244 s = 1.724 s, landing v t = 11.73 cm out from the edge; rolling at a steady speed needs no grip
cup against the edge: at the can's exit, 1.333 s, the cup is 96.2 deg round its circle; the large rim's circle reaches l2 = 29.08 cm toward the edge from the start line, against 40 cm, so the cup's track never comes closer to the edge than 10.92 cm = 10.9 cm (nearest at a quarter lap, 1.247 s after the nudge); the large rim's circle needs a desk at least 58.2 cm across; after one lap the cup is back where it started, turned 7.27 times (the drawing holds it there; without loss it would circle for ever)
for the description: 12 oz cup (top 9, bottom 6, height 10 cm): alpha 8.53 deg, apex 20.22 cm beyond the small rim and 30.34 cm = 30.3 cm from the large rim, 6.741 = 6.74 turns per lap, CM circle 24.49 cm, lap 5.13 s at 0.3 m/s, grip needed 0.0375, nearest the edge 9.7 cm; 4 oz cup (top 7, bottom 5, height 6 cm): alpha 9.46 deg, apex 15.21 cm beyond the small rim and 21.29 cm = 21.3 cm from the large rim, 6.083 = 6.08 turns per lap, CM circle 17.46 cm, lap 3.66 s at 0.3 m/s, grip needed 0.0526, nearest the edge 18.7 cm; a straight cup (alpha 0, like the can): apex at infinity, no circle, off the desk at 1.333 s; nudge 0.2 m/s: lap 7.48 s, friction needed 0.0171 = 0.017; the can off at 2.000 s; nudge 0.5 m/s: lap 2.99 s, friction needed 0.1070 = 0.107; the can off at 0.800 s
checks against the brief (26 checks, 0 failed): slant (cm): brief 9.086, sim 9.08639, diff +3.9e-04: ok; alpha (deg): brief 7.907, sim 7.90716, diff +1.6e-04: ok; apex to small rim (cm): brief 19.99, sim 19.9901, diff +6.0e-05: ok; apex to large rim (cm): brief 29.08, sim 29.0765, diff -3.5e-03: ok; l1 / rb: brief 7.269, sim 7.26911, diff +1.1e-04: ok; l2 / Rt: brief 7.269, sim 7.26911, diff +1.1e-04: ok; turns per lap (RK4): brief 7.269, sim 7.26911, diff +1.1e-04: ok; CM circle radius (cm, research): brief 23.82, sim 23.8246, diff +4.6e-03: ok; lap time (s, research 4.990): brief 4.99, sim 4.98982, diff -1.8e-04: ok; lap time RK4 (s): brief 4.99, sim 4.98982, diff -1.8e-04: ok; CM height constant (m): brief 0, sim 0, diff +0.0e+00: ok; friction needed: brief 0.038, sim 0.0385194, diff +5.2e-04: ok; friction needed at 0.5 m/s: brief 0.107, sim 0.106998, diff -1.6e-06: ok; normal resultant inside the contact segment (cm): brief 24.5333, sim 24.0796, diff -4.5e-01: ok; nearest approach to the edge (cm): brief 10.9, sim 10.9235, diff +2.4e-02: ok; can off the desk (s): brief 1.333, sim 1.33333, diff +3.3e-04: ok; can down 0.75 m (s): brief 1.724, sim 1.72442, diff +4.2e-04: ok; 12 oz: large rim circle (cm): brief 30.3, sim 30.3356, diff +3.6e-02: ok; 12 oz: turns per lap: brief 6.74, sim 6.74125, diff +1.2e-03: ok; 4 oz: large rim circle (cm): brief 21.3, sim 21.2897, diff -1.0e-02: ok; 4 oz: turns per lap: brief 6.08, sim 6.08276, diff +2.8e-03: ok; no slip, large rim (m): brief 0, sim 8.59313e-14, diff +8.6e-14: ok; no slip, small rim (m): brief 0, sim 5.90639e-14, diff +5.9e-14: ok; RK4 lap against the closed form (s): brief 0, sim -9.76996e-15, diff -9.8e-15: ok; half-step rerun lap (s): brief 0, sim 1.77636e-15, diff +1.8e-15: ok; dL/dt numeric against closed form (cm): brief 0, sim -1.87169e-05, diff -1.9e-05: ok
note: the brief puts the normal resultant at about 23.6 cm, short of the centre of mass; the sim's dL/dt = Omega z x L puts it 0.25 cm beyond the centre of mass at 24.08 cm (closed form and finite differences agree); either lies inside the contact segment
drawing: 1200 px per metre; the desk edge at y 330, the desk to y 1290 (80 cm deep); the start line at y 810 (40 cm = 480 px below the edge); the cup's cone tip at x 430 on the start line, the small rim 240 px to its right (x 670), the large rim 349 px (x 779), the cup 66 to 96 px wide and 108 px long, its centre of mass at x 716; the large rim's circle (radius 348.9 px) spans x 81 to 779 and y 461 to 1159 (10.9 cm from the edge); the can 144 by 96 px at x 970 (x 898 to 1042), rolling up its lane to the edge and on into the dark beyond it, drawn smaller as it drops (scale 1.5 / (1.5 + drop)), landing at y 189 at scale 0.667
schedule (video time, real time): cycles of 8 s start at -8.00, 0.00, 8.00, 16.00, 24.00, 32.00 s; the finger marks move in over the first 0.5 s and tap both objects 0.5 s into each cycle at 0.50, 8.50, 16.50, 24.50, 32.50 s; the can's centre passes the edge 1.333 s later at 1.83, 9.83, 17.83, 25.83, 33.83 s (its event row lights) and it is down on the floor at 2.22, 10.22, 18.22, 26.22, 34.22 s (2.224 s into the cycle); the cup is a quarter lap round (nearest the edge; the dashed rim circles appear) at 1.75, 9.75, 17.75, 25.75, 33.75 s, half way at 2.99, 10.99, 18.99, 26.99, 34.99 s and back at its start 4.990 s after the nudge at 5.49, 13.49, 21.49, 29.49, 37.49 s (its event row lights; the drawing holds it there); the reset crossfade runs over the last 0.5 s of each cycle (from 7.50, 15.50, 23.50, 31.50, 39.50 s); on the first frame both objects rest on the start line with the finger marks 0.5 s from the tap; title until 3 s; payoff card from 28.4 s; the title fades back in over the last 0.5 s and the last frame repeats the first (the scene is periodic: 40 s holds exactly 5 cycles)
text widths (the on-screen strings verbatim): overlay@34 785 px '8 oz cup and 8 cm can, grip 0.5 | no seed', title line 1@56 554 px 'Paper cup or can:', title line 2@56 477 px 'which one rolls', title line 3@56 409 px 'off the desk?', legend@40 776 px 'same desk, same nudge, real time', clock@28 358 px '1.25 s since the nudge', clock held@28 274 px 'before the nudge', label cup@40 226 px 'paper cup', label can@40 273 px 'straight can', sub@28 541 px 'same nudge, 40 cm from the edge', counter turned@28 341 px 'cup: turned 7.3 times', counter lap@28 205 px 'cup: lap 1.00', tip@24 109 px 'cone tip', can moved@28 286 px 'can: moved 40 cm', can off@28 264 px 'can: off the desk', can floor@28 260 px 'can: on the floor', event can@40 588 px 'can: off the desk at 1.33 s', event cup@40 671 px 'cup: back at the start at 5.0 s', payoff line 1@40 396 px 'Paper cup or can:', payoff line 2@40 647 px 'which one rolls off the desk?', payoff line 3@40 782 px 'can: straight off the desk at 1.33 s', payoff line 4@40 873 px 'cup: circles, back at the start at 4.99 s', payoff line 5@40 897 px 'the cone tip is 29.1 cm from the big rim', payoff line 6@40 898 px '7.27 turns a lap, 10.9 cm from the edge'
layout check: text boxes (x0, y0, x1, y1): title 1 (40, 158, 594, 214); title 2 (40, 216, 517, 272); title 3 (40, 274, 449, 330); legend (40, 216, 816, 256); clock (40, 276, 398, 304); label cup (40, 352, 266, 392); label can (587, 352, 860, 392); sub (179, 400, 721, 428); can readout (574, 436, 860, 464); counter turned (260, 706, 600, 734); counter lap (328, 742, 532, 770); tip tag (375, 822, 485, 846); event can (246, 1180, 834, 1220); event cup (205, 1228, 875, 1268); payoff 1 (342, 1552, 738, 1592); payoff 2 (217, 1600, 863, 1640); payoff 3 (149, 1648, 931, 1688); payoff 4 (103, 1696, 977, 1736); payoff 5 (91, 1744, 989, 1784); payoff 6 (91, 1792, 989, 1832); the can's lane x 898 to 1042 from y 858 up (its finger below it to y 988); the landed can at y 189, 32 px tall either side; the cup's finger at x 716 below y 858; the large rim's circle radius 349 px, the small rim's 240 px about (430, 810); the overlay band y 96 to 130, the caption band y 1440 to 1530; the geometry layer y 136 to 1290; the title rows and the legend/clock share the zone above the edge but never show together (the title fades out over 0.4 s before the legend fades in); every other pair of boxes is disjoint
Sat Oct 10 11:01:50 AM EEST 2026
```

The brief's checks (the "checks against the brief" line above, 26
checks, 0 failed, asserted):

- slant 9.086 cm (sim 9.08639); alpha 7.907 deg (7.90716). ok.
- apex 19.99 cm from the small rim (19.9901) and 29.08 cm from the
  large rim (29.0765). ok.
- l1 / r = l2 / R = 7.269 = turns per lap: 7.26911 by all three, RK4
  7.269113; no slip on both rims within 8.6e-14 m and 5.9e-14 m at
  every step. ok.
- CM circle radius 23.8246 cm (research 23.82; the sim's value
  stands); lap time 2 pi rho / v = 4.989821 s against the research
  4.990 s (the brief's "about 4.99 to 5.04 s": 4.9898 rounds to 4.99;
  the check is against 4.990 within 5e-3). ok.
- CM height constant: the axis's z component drifts 0.0e+00 over the
  lap (threshold 1e-9); energy kept. ok.
- friction needed 0.0385 (brief 0.038) under 0.5 by a factor 13.0;
  0.107 at 0.5 m/s. ok.
- normal resultant from dL/dt = Omega z x L at 24.080 cm, inside the
  19.99 to 29.08 cm contact segment (closed form and central
  differences agree to 5.4e-13 cm; dL_z/dt at most 5.2e-16). ok. Note:
  the brief expected about 23.6 cm, short of the centre of mass; the
  sim puts it 0.25 cm beyond the centre of mass (see Deviations).
- nearest approach to the edge 10.9235 cm (brief about 10.9), at a
  quarter lap 1.247 s after the nudge. ok.
- can off the desk at 1.33333 s, down 0.75 m at 1.72442 s. ok.
- variants: 12 oz cup apex 20.22 cm beyond the small rim and 30.34 cm
  from the large rim, 6.741 turns per lap, lap 5.13 s; 4 oz cup 15.21
  and 21.29 cm, 6.083 turns, lap 3.66 s; straight cup (alpha 0): apex at
  infinity, off the desk at 1.333 s like the can; nudges 0.2 and 0.5
  m/s: laps 7.48 and 2.99 s, friction 0.0171 and 0.107. ok.
- integration: RK4 on the rotation matrix, 100 steps per frame (dt
  1.67e-04 s), orthonormality drift 1.4e-14, the centre's speed within
  5.5e-10 m/s of 0.3, lap against the closed form within 9.8e-15 s, a
  half-step rerun moves the lap by 1.8e-15 s. ok.
- drawing: 1200 px/m, edge y 330, desk to y 1290, start line y 810,
  apex x 430, small rim x 670, large rim x 779, the large rim's circle
  (349 px) inside the desk and clear of the can's lane; asserted. ok.
- text widths (PIL, DejaVuSans-Bold): overlay 785 px at 34; title rows
  554, 477, 409 px at 56; legend 776 px at 40; card lines 554, 647,
  782, 873, 897, 898 px at 40; every fixed line under 950 px, asserted.
  ok.
- layout boxes (title rows, legend, clock, labels, sub row, can
  readout, cup counters, tip tag, event rows, card lines) pairwise
  disjoint except the title rows against the legend/clock, which never
  show together; every box clear of the overlay band (y 96 to 130), the
  caption band (y 1440 to 1530) and the can's lane; the cup counters
  inside the empty disc about the apex; asserted. ok.
- schedule: cycles of 8 s, the nudge 0.5 s in (0.50, 8.50, 16.50,
  24.50, 32.50 s), the can's centre at the edge at 1.83 s and on the
  floor at 2.22 s of each cycle, the cup a quarter lap round at 1.75 s
  and back at its start at 5.49 s, hold, crossfade from 7.50 s; 5
  cycles in 40 s, periodic; asserted. ok.

### Production

- sims/cuproll/cuproll.py (new): one top-down desk scene after
  sims/tray (shared surface), the finger marks and an object leaving
  the frame after sims/pencil, the clock, crossfade and render loop
  after sims/deskchain, the stripe after sims/coinroll. Cone geometry
  and the thin-shell inertia about the apex in closed form (checked by
  quadrature: the mass to 1e-6, I1 and I3 to 1e-6 relative); the
  rolling cone integrated by RK4 on the rotation matrix with the
  angular velocity along the contact line (|omega| = v cot alpha /
  rho), the lap time, turns, no-slip arcs, axis height, speed and dL/dt
  recorded per step; the can in closed form; 26 brief checks with
  assert; text-width, box, band and lane asserts; loop, periodicity and
  band prints in the renderer. Deterministic, no seed used.
- projects/cuproll/manifest.json: g 9.807, cup 8 / 5.5 / 9 cm, can 8 by
  12 cm, nudge 0.3 m/s, 40 cm to the edge, desk 75 cm, grip 0.5, 100
  substeps per frame, integrate 5.2 s, cycle 8 s, nudge_at 0.5,
  finger_s 0.5, reset_fade 0.5, px_per_m 1200, edge y 330, desk bottom
  1290, apex x 430, can x 970, camera height 1.5 m (the falling can
  shrinks by 1.5 / (1.5 + drop)), title "Paper cup or can:|which one
  rolls|off the desk?", title_until 3.0, payoff_t 28.4, payoff_hold
  0.6, music_seed 125, music_gain 0.18, voice_offset 0.6, caption_y
  0.75, overlay "8 oz cup and 8 cm can, grip 0.5 | no seed".
- Smoke frames (--frames 0.0, 0.3, 0.5, 1.0, 1.75, 1.9, 2.3, 3.5, 5.5,
  7.6, 35.5, 39.6, then 0.0 and 28.7 after the title and payoff_t were
  set) viewed: objects at rest on the start line with the finger marks
  below, the tap at 0.5 s, the cup turning about the apex with the trail,
  the can at the edge then shrinking and dimming in the drop zone and
  landing faint at y 189, the dashed rim circles from the quarter lap,
  the gold event rows, the hold and the crossfade, the card rising.
- Footage: `nix develop -c python3 sims/cuproll/cuproll.py` 11:01:50 to
  11:02:39 (media/cuproll/render.log): 2400 frames; loop check: the
  last frame differs from the first in 0 px; periodicity check: the
  scene drawn live at 40 s equals 0 s (0 px); the frame before the last
  differs from the last in 4925 px (motion into the loop); overlay band
  y 96 to 130 and caption band y 1440 to 1530: max channel difference
  from the background 0 over five sampled frames.
- Hook pre-tests (media/cuproll/hooks/pretest.log, each one take, all
  ok; voice-timing with the 0.6 s offset): hook1 "Nudge a paper cup
  and a can the same: which one rolls off the desk?" 3.76 s, "which
  one" from 2.57 s of video; hook2 "Paper cup or can: which one rolls
  off the desk?" 2.97 s, "which one" from 1.87 s; hook3 "Same nudge for
  a paper cup and a can: ..." 3.77 s, 2.67 s; hook4 "A paper cup and a
  tin can get the same nudge: ..." 4.08 s, 2.97 s. Chosen hook2 (the
  brief's fallback): the only one whose question lands under two
  seconds. Word pre-tests ok: "The can rolls off at one point three
  seconds. The cup circles and is back in five seconds." (hook5) and
  "Nudge a paper cup. It circles. It rolls off. It comes back. Tin
  can." (hook6). Full-narration pre-tests (narr1 to narr4): "The can
  rolls straight off ..." ok, "The can is off the desk ..." ok, "The
  can rolls off the edge ..." failed (round -> around), "The can rolls
  off at one point three seconds, and the cup ..." ok.
- Narration projects/cuproll/narration.txt: 113 words, the question
  first (no words before it), setup number "forty centimeters from the
  edge", the question repeated word for word before the payoff, payoff
  "The can rolls straight off at one point three seconds. The cup
  circles and is back in five seconds."
- Voice (media/cuproll/voice.log): take 1 failed at word 98 ("can" ->
  "cone"), take 2 failed at word 20 ("in" -> "a", "in real time"), take
  3 failed at word 62 ("round" -> "around"); take 4 ok, 32.473107 s,
  11:01:16. Piper 3.48 words a second. voice-timing
  (media/cuproll/timing.log): "Paper cup or can," 0.60 to 1.99 s,
  "which one rolls off the desk" from 1.99 s; the repeated question
  from 24.77 s ("which one" from 26.20 s); the payoff sentence
  "The can rolls straight off at one point three seconds" 27.81 to
  30.48 s of video; "The cup circles and is back in five seconds" 30.73
  to 33.07 s; the voice ends at 33.07 s of video.
- payoff_t 28.4 s: the card fades in over 0.6 s as "straight off at one
  point three" is spoken (29.0 to 30.5 s), after the can's exit of the
  fourth cycle (25.83 s) and the cup's return of the third (21.49 s);
  the cup's return of the fourth cycle (29.49 s) and the whole fifth
  cycle (can off 33.83 s, cup back 37.49 s) play under the card.
- Compose: `nix develop -c scripts/compose.sh cuproll` 11:02:39 to
  11:02:50 (media/cuproll/compose.log): music seed 125, 40.00 s;
  captions: 15 pauses detected, 15 matched, max chunk start shift
  1.539 s against word-count timing; final.mp4 40.000000 s; preview
  and sheet written.

### Local QA

- ffprobe final.mp4: h264 1080x1920 at 60/1, aac 22050 Hz mono,
  duration 40.000000 s; atoms ftyp, moov at 32, free, mdat (faststart);
  4141007 bytes; md5 bc1a8972797d7fcb9a78d3f1bdfc2db3.
- Caption and overlay bands: signalstats on footage.mp4 rows 1440 to
  1530 and rows 96 to 130: YMAX 28 and YMIN 28 on all 2400 frames
  (background only).
- Captions: 34 caption chunks plus the overlay "8 oz cup and 8 cm can,
  grip 0.5 | no seed" in media/cuproll/captions.filter; the joined
  caption text equals the narration word for word (113 words) after
  undoing the drawtext escapes; first captions "Paper cup or can:"
  0.600 to 2.193 s, "which one rolls off" 2.193 to 3.338 s, "the desk?"
  3.338 to 3.911 s; the last "is back in five seconds." ends at 33.073
  s.
- Full-resolution frames viewed (media/cuproll/qa-*.png): 0.00 s
  overlay, three-row title, both objects at rest on the start line, the
  finger marks below them (they move in over the first 0.5 s), no
  caption yet; 1.00 s the cup a tenth of a lap round, turned 0.7 times,
  the can 15 cm on, the caption "Paper cup or can:"; 2.10 s the can
  beyond the edge in the drop zone, "can: off the desk" readout, the
  gold event row "can: off the desk at 1.33 s", both rim circles, the
  cup at lap 0.32; 20.00 s legend and clock "3.50 s since the nudge",
  the landed can faint at the top right, the cup at lap 0.70 with its
  stripe, caption "the point where the"; 28.70 s the card rising under
  the caption "straight off at one", the cup at lap 0.84; 39.983 s the
  title back, both objects at the start, the finger marks back, no
  caption, the card gone; the renderer reports the last frame equal to the first in 0 px.
- sheet.png (8x5 at 1 fps) viewed: five cycles, the can off and down
  each cycle, the cup round and held each cycle, the card from 29 s.
- Nothing wider than the frame: every fixed line measured under 950
  px (max 898 px, card line 6); the caption chunks are drawn centred by
  captions.py from the narration.

### Metadata

- projects/cuproll/metadata.json written by media/cuproll/metadata.py
  with asserts: title 94 characters (at most 100), description 3864
  characters (under 5,000), ASCII, no angle brackets, 11 tags; every
  number in the title and description (65 distinct, commas stripped)
  appears in media/cuproll/measure.log.
- Title: Paper cup or can: which one rolls off the desk? The can at 1.3
  s; the cup circles, back in 5 s
- privacyStatus private, categoryId 27, containsSyntheticMedia true,
  selfDeclaredMadeForKids false.

### Deviations from the brief

- Hook: the brief's fallback "Paper cup or can: which one rolls off the
  desk?" is used in the hook, the title and the card, not "Nudge a
  paper cup and a can the same: ...": the brief keeps the hook whose
  question lands earliest under two seconds, and only the fallback does
  (1.87 s against 2.57 s).
- Payoff sentence "The can rolls straight off at one point three
  seconds.": "straight" added because "The can rolls off" came back as
  "cone" in the round trip (take 1); the card says the same ("can:
  straight off the desk at 1.33 s").
- "curves around the point" (American) instead of "curves round": whisper
  heard "around" (take 3). "in real time" dropped from the setup
  sentence (heard "a real time", take 2); the legend row says "real
  time".
- Floor-zone text is left-aligned at x 40 (the title rows, the legend
  and the clock), not centred: centred rows would cross the can's drop
  lane (x 898 to 1042) through which the can falls out; asserted clear.
- The clock sits under the legend in the floor zone (y 290, "N.NN s
  since the nudge"), not in the left readout column.
- One shared sub row "same nudge, 40 cm from the edge" (centred under
  both labels), not one per column: the 541 px line does not fit twice.
- The cup's readouts "cup: turned N.N times" and "cup: lap N.NN" sit in
  the empty disc inside the small rim's circle, above the apex, not in
  the left column under the label: under the label they would touch
  the large rim's circle (its top is at y 461).
- Both rim circles are drawn dashed after the quarter lap (the small
  rim's 240 px as well as the large rim's 349 px), with a "cone tip"
  tag under the apex dot. No cone silhouette lines (they would cross
  the counters).
- The can is not gone by 2.3 s: it shrinks and dims as it falls (camera
  height 1.5 m) and stays as a faint landed can in the drop zone at y
  189 until the crossfade; its drop stripe trail and the cup's trail
  are kept.
- The cup is held at its start after one lap (5.49 s of the cycle) to
  the crossfade; without loss it would keep circling. The description
  says so.
- The normal resultant: the brief expected about 23.6 cm (short of the
  centre of mass); the sim's dL/dt = Omega z x L gives 24.08 cm, 0.25
  cm beyond the centre of mass (closed form and central differences
  agree). The check is "inside the contact segment", which holds.
- Lap time check against the research 4.990 s within 5e-3 s, not the
  brief's band 4.99 to 5.04 s: the sim's 4.9898 s rounds to 4.99 but
  sits 2e-4 s under the band's lower end.
- The title rows and the legend/clock share the zone above the desk
  edge (y 158 to 330) and are exempt from the pairwise box check
  because they never show together (the title fades out over 0.4 s
  before the legend fades in); every other pair is asserted disjoint.

## Niche note

[produced 2026-10-10 as "Paper cup or can: which one rolls off the
desk? The can at 1.3 s; the cup circles, back in 5 s"; measured 8 oz
cup (8 / 5.5 / 9 cm) and 8 by 12 cm can at 0.3 m/s from 40 cm: can off
the desk at 1.333 s, down at 1.724 s, 11.73 cm out; cup slant 9.086 cm,
alpha 7.907 deg, apex 19.99 cm beyond the small rim and 29.08 cm from
the large rim, 7.269 turns per lap, CM circle 23.82 cm, lap 4.990 s,
nearest the edge 10.92 cm, friction needed 0.0385, normal resultant
24.08 cm inside the contact segment; 12 oz cup 30.34 cm and 6.741
turns, 4 oz cup 21.29 cm and 6.083 turns; real time; task
20261010-103219]

## Upload

- Attempt 2 of 5 recorded at 2026-10-10T11:10:34+03:00 (quota day 2026-10-10T10:00 EEST), scripts/yt-upload.py cuproll, md5 bc1a8972797d7fcb9a78d3f1bdfc2db3.
- Uploaded private as cLZ4xAJ0Ptc at 2026-10-10T08:10:37Z; scripts/yt-qa.py --wait --publish gate 15 of 15 on the first processed read; published 2026-10-10T11:11:17+03:00, re-read public; 54 units; attempt cost 1,654 units. https://youtu.be/cLZ4xAJ0Ptc
