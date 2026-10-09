# Produce short: round pencil or hexagonal pencil, same nudge, which one rolls off the desk

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day40

## Goal

Backlog idea (trend research 2026-10-08, task 20261008-100401, pillar 2
chaos and physics, desk mechanics; read the full "Round or hexagonal
pencil" bullet at the end of docs/niche.md): two pencils on a flat desk
given the same nudge; the round one rolls off the edge, the hexagonal
one stops after two faces.

Orchestrator notes (2026-10-08; closed forms and an independent RK4 in
/tmp/day40/closed.py with the log /tmp/day40/closed.log; research script
/tmp/day40/research/pencil.py with pencil.log; g = 9.807 m/s^2). Read
/tmp/day40/producer-conventions.md first. The model: two 7.0 mm pencils
seen end-on on a level desk, both 25 cm from the edge, both given the
same centre-of-mass speed v0 = 0.15 m/s (say so: the same speed, chosen;
"the same nudge" in narration). Top band, the ROUND pencil: a solid
cylinder of radius 3.5 mm rolling without slipping and with no rolling
loss (say so: chosen), so it keeps 0.15 m/s, reaches the edge after
1.667 s and drops off (free fall from a 75 cm desk: 0.391 s, lands 5.9
cm out; draw it falling out of the band). Bottom band, the HEXAGONAL
pencil: a uniform regular hexagonal prism 7.0 mm across the flats, so
the corner radius R = 3.5 mm / cos 30 deg = 4.041 mm (the side length
equals R), I = 5/12 m R^2 about the centre and 17/12 m R^2 about a
corner. It rolls one face at a time: pivoting on its front corner from
phi = -30 deg to +30 deg (phi the angle of the centre from the vertical
over the corner) with phi'' = (12 g / (17 R)) sin phi (energy conserved
over a face; the start and end heights are equal); at the next corner
an inelastic no-slip impact keeps omega+ = (11/17) omega- (angular
momentum about the new corner: (5/12 + cos 60 deg) / (17/12) = 11/17
exactly, 121/289 = 0.4187 of the energy). It passes a corner only while
omega at the start of the face exceeds sqrt(24 g (1 - cos 30 deg) / (17
R)) = 21.42 rad/s (centre speed 0.0866 m/s); below that it rocks back on
the same face: the same pivot and impact rules with the sign reversed,
so the rocks decay by 11/17 each time. The corner stays loaded while
omega^2 R < g cos phi, worst at the face ends: omega < 45.84 rad/s
(0.1853 m/s); the no-slip grip needed at the corner during the two
faces peaks at 0.30, so state the desk grip as 0.5 (chosen) and print
the grip needed. Integrate each face with RK4 at dt = 1e-6 s (the face
end by interpolation), check the end spin equals the start spin within
1e-9, count faces, rocks and the time to stop (spin under 1 percent of
the corner threshold), print the table of the hexagonal pencil's spin
after each impact, the variants for the description, and the schedule.

Checks, not facts (the sim must print and compare; state them as
checks; exact fractions where exact): R = 4.041 mm; omega+ / omega- =
11/17 = 0.6471; corner threshold 21.42 rad/s (0.0866 m/s); corner loaded
below 45.84 rad/s (0.1853 m/s); at 0.15 m/s (omega0 37.12 rad/s): face 1
ends at 37.12 rad/s, impact to 24.02, face 2 (just above the threshold)
ends at 24.02, impact to 15.54 under the threshold, so 2 faces = 2 R =
8.08 mm = 8.1 mm in 102.0 ms, then about 10 to 11 rocks before the spin
is under 1 percent of the threshold; grip needed at the corner 0.302;
0.10 and 0.12 m/s give 1 face (4.0 mm in 64.2 and 44.5 ms), 0.18 m/s 2
faces in 72.4 ms (grip needed 0.89), 0.20 m/s hops (omega0 49.5 over
45.84); a hexagonal pencil tips from rest only on a desk tilted past 30
deg; the round pencil: 25 cm in 1.667 s, falls 0.391 s, 5.9 cm out.
Print the schedule in video time, the text widths and the layout
clearances.

Drawing: two-band layout (sims/deskchain style, read it whole; bands y
330 to 880 and 880 to 1430; sims/kerbhop pivots a wheel about an edge
with an impact, sims/rollrace and sims/coinroll draw rolling with a
stripe), END-ON view at 3,000 px per metre: the desk top 380 px under
the band top, its edge at x 900 with a leg, the pencils start with their
centres at x 150 (25 cm = 750 px; assert), each pencil a 21 px circle or
hexagon with a dark stripe from the centre to the rim so the turn shows,
a thin trail of its centre; a finger-tap mark at the start of each
cycle; in the top right of each band a 10x cross-section inset (about
280 by 220 px, in a corner clear of the desk and the rows: assert) that
shows the same pencil turning at 210 px across with its stripe and, for
the hexagonal one, the corner it pivots on highlighted; the round pencil
drops off the edge and out of the band. Label rows (40 px, coloured):
"round pencil" (coral) and "hexagonal pencil" (teal), both "7 mm, same
nudge". Readouts (28 px): left column "speed N.NN m/s" (live) and the
clock; right column "rolled NN.N mm" (live, in cm for the round one once
over 10 cm: "rolled 25.0 cm"). Gold event rows: top "round: off the desk
at 1.67 s", bottom "hexagonal: stopped after 2 faces, 8 mm" (lit when
the hexagonal pencil stops; the top row lit when the round pencil leaves
the edge; both held). Shown at 1/2 speed: cycle 8 s (480 frames): the
nudge 0.5 s into the cycle (both pencils at rest before it, the finger
mark approaching: motion in frame one), the hexagonal pencil's two faces
by 0.70 s and its rocking dying out by about 1.5 s of the cycle, the
round pencil at the edge at 0.5 + 2 * 1.667 = 3.83 s and on the floor
(out of the band) by 4.7 s; hold to 7.5 s, crossfade reset over the last
0.5 s; 5 cycles in 40 s, exactly periodic, the last frame equal to the
first. If the smoke frames show the hexagonal pencil's motion as a
single flick, switch to 1/4 speed with the same 8 s cycle (round pencil
at the edge at 7.17 s, crossfade from 7.5 s) and say so. Legend row
after the title: "same desk, same nudge, 1/2 speed". Overlay: "7 mm
pencils, 25 cm from the edge | no seed" (measure it).

Day forty, third slot. Chosen because it is a desk-object debate with
an exact fraction behind it (each corner keeps 11/17 of the spin), the
two pencils end visibly apart (one on the floor, one stopped 8 mm on),
and the nudge repeats as a loop. Question in the first two seconds:
"Nudge both pencils the same: which one rolls off the desk?" (pre-test;
it is the first sentence; "Round pencil or hexagonal pencil: which one
rolls off the desk?" is the fallback). Keep the question identical in
the title, the hook and the payoff. Setup number: "fifteen centimeters
a second" (one setup number only; the 7 mm and the 25 cm go to the
overlay, card and description). Payoff: "The round one rolls off. The
hexagonal one stops after eight millimeters." (at most two numbers in
the payoff beat). The mechanism sentence must follow the picture and
the inset: every corner the hexagonal pencil lands on takes a third of
its spin, so two faces on it has too little left to climb the next
corner; the round pencil has no corners. Whisper risks: "hexagonal"
(pre-test; "six-sided" is the fallback), "millimeters", "fifteen
centimeters a second", "nudge", "rolls off", "corner"; avoid "do you",
avoid "too". Pre-test hooks with scripts/voiceover.sh and keep the one
whose question lands earliest under two seconds. Measure every fixed
text line with PIL before rendering and keep every line under 950 px,
and the title under 100 characters with no < or >. Music seed 123.
Templates: sims/deskchain (two-band layout, asserts, the clock, the
crossfade; read it whole), sims/kerbhop (pivot with an impact),
sims/rollrace and sims/coinroll (rolling with a stripe), sims/bankcurve
(an inset per band, yesterday's). Sim name pencil: sims/pencil/pencil.py,
projects/pencil/, media/pencil/.

## Claim (expected; the sim's numbers replace these)

Two 7 mm pencils on a desk 25 cm from the edge get the same nudge, 0.15
m/s. The round one rolls without loss, reaches the edge in 1.67 s and
drops off. The hexagonal one rolls over two corners, 8.1 mm in 0.10 s,
and stops: each corner it lands on keeps only 11/17 of its spin, and
climbing the next corner needs 21.4 rad/s; after two it has 15.5. Narrated:
fifteen centimeters a second (setup); the round one rolls off against
stops after eight millimeters (payoff). Card: the question; the answer
(round: off the desk at 1.67 s; hexagonal: 2 faces, 8 mm); each corner
keeps 11/17 of the spin; the corner needs 21.4 rad/s. Description: the
model statement, the equations, both runs, the speed variants, the hop
limit, the tilt limit, the checks.

## Claim

Two 7 mm pencils on a level desk, their centres 25 cm from the edge,
get the same nudge: each centre moves off at 0.15 m/s (chosen). The
round pencil (solid cylinder, r 3.5 mm, no rolling loss, chosen) keeps
0.15 m/s, reaches the edge after 1.667 s, falls 0.391 s from the 75 cm
desk and lands 5.9 cm out. The hexagonal pencil (7 mm across the
flats, corner radius R = 4.041 mm, I = 17/12 m R^2 about a corner)
starts at omega0 = 37.12 rad/s, rolls face 1 and ends it at 37.12
rad/s, the corner impact leaves 24.02 (11/17 exactly), face 2 ends at
24.02, the impact leaves 15.54, under the 21.42 rad/s (0.0866 m/s) the
next corner needs. So it rolls 2 faces = 8.08 mm (8.1 mm) in 0.1020 s,
rocks 10 times (each keeps 11/17) and is stopped 0.2150 s after the
nudge. Grip needed at the corner 0.3024 on the faces, 0.3711 on the
rocks, 0.3712 at each impact, under the desk's 0.5 (chosen); the corner
stays loaded (least load 0.3319 of the weight; hop limit 45.84 rad/s).
Narrated: fifteen centimeters a second (setup); "The round one rolls
off. The hexagonal one stops after eight millimeters." (payoff). Card:
the question; round: off the desk at 1.67 s; hexagonal: stops after
8.1 mm; each corner keeps 11/17 of the spin; next corner needs 21.4
rad/s, has 15.5.

## Evidence

### Measurements

`nix develop -c python3 sims/pencil/pencil.py --measure-only` (final
run 10:48:04, exit 0, saved as media/pencil/measure.log):

```
Thu Oct  8 10:48:04 AM EEST 2026
setup: the same desk in both panels, seen end-on: two 7 mm pencils on a level desk, their centres 25 cm from the edge, each given the same nudge, its centre moving off at v0 = 0.15 m/s (chosen); g = 9.807 m/s^2; top panel the round pencil, a solid cylinder of radius 3.5 mm rolling without slipping and with no rolling loss (chosen), leaving the desk as its centre passes the edge and falling freely from a 75 cm desk; bottom panel the hexagonal pencil, a uniform regular hexagonal prism 7 mm across the flats, the nudge leaving its centre moving at v0 on an arc about the front corner (omega0 = v0 / R); the desk grip 0.5 (chosen); each face and rock integrated by RK4 at 1000000 steps per second (dt = 1e-06 s), the face end located by bisection inside the last step; stopped when the spin is under 1 percent of the corner threshold; shown at 1/4 speed on a 8 s cycle (480 frames) with the nudge 0.3 s into the cycle, 5 cycles in 40 s; drawn at 3000 px per metre with a 10x cross-section inset; deterministic, no seed
hexagon: corner radius R = (a / 2) / cos 30 deg = 4.0415 mm = 4.041 mm (the side length equals R; across the corners 8.083 mm); I = 5/12 m R^2 about the centre, 17/12 m R^2 about a corner; on a corner phi'' = (12 g / (17 R)) sin phi = 1712.90 sin phi per s^2; a face is one side = R = 4.041 mm of travel and 60 deg of turn; the centre rises R (1 - cos 30 deg) = 0.5415 mm over a corner
impact: angular momentum about the new corner, (17/12) omega+ = (5/12 + cos 60 deg) omega-, so omega+ / omega- = 11/17 = 0.6471 exactly; the energy kept (11/17)^2 = 121/289 = 0.4187; the spin each corner takes 1 - 11/17 = 6/17 = 0.3529; the impulse the corner gives, per m R omega-: -0.3057 along the desk, +0.8235 up (the desk pushes, no bounce), a grip of 0.3712
corner threshold: over the top of a corner needs (17/24) R^2 omega^2 > g R (1 - cos 30 deg), omega > sqrt(24 g (1 - cos 30 deg) / (17 R)) = 21.4236 rad/s (centre speed 0.08658 m/s); hop limit: the corner stays loaded while omega^2 R < g cos phi, worst at the face ends (cos 30 deg): omega < 45.8421 rad/s (0.18527 m/s); tilt: on a desk tilted by beta the centre passes over the downhill corner when tan beta > (R / 2) / (a / 2), beta > 30.0000 deg: a hexagonal pencil tips from rest only past 30 deg
hexagonal pencil at 0.15 m/s (omega0 = v0 / R = 37.1154 rad/s, under the hop limit 45.84): face 1 (forward) 0.00 to 32.16 ms: starts 37.1154 rad/s, ends 37.1154 (diff -1.4e-13), after the impact 24.0158 rad/s; face 2 (forward) 32.16 to 101.98 ms: starts 24.0158 rad/s, ends 24.0158 (diff -7.1e-14), after the impact 15.5397 rad/s; rock 1 (forward) 101.98 to 147.36 ms: starts 15.5397 rad/s, ends 15.5397 (diff -3.9e-13), after the impact 10.0551 rad/s; rock 2 (back) 147.36 to 172.70 ms: starts 10.0551 rad/s, ends 10.0551 (diff +2.5e-13), after the impact 6.5062 rad/s; rock 3 (forward) 172.70 to 188.35 ms: starts 6.5062 rad/s, ends 6.5062 (diff +3.6e-13), after the impact 4.2099 rad/s; rock 4 (back) 188.35 to 198.30 ms: starts 4.2099 rad/s, ends 4.2099 (diff +2.7e-13), after the impact 2.7241 rad/s; rock 5 (forward) 198.30 to 204.70 ms: starts 2.7241 rad/s, ends 2.7241 (diff -5.1e-14), after the impact 1.7626 rad/s; rock 6 (back) 204.70 to 208.82 ms: starts 1.7626 rad/s, ends 1.7626 (diff -1.4e-13), after the impact 1.1405 rad/s; rock 7 (forward) 208.82 to 211.49 ms: starts 1.1405 rad/s, ends 1.1405 (diff -1.4e-12), after the impact 0.7380 rad/s; rock 8 (back) 211.49 to 213.21 ms: starts 0.7380 rad/s, ends 0.7380 (diff -8.3e-13), after the impact 0.4775 rad/s; rock 9 (forward) 213.21 to 214.32 ms: starts 0.4775 rad/s, ends 0.4775 (diff +8.7e-13), after the impact 0.3090 rad/s; rock 10 (back) 214.32 to 215.05 ms: starts 0.3090 rad/s, ends 0.3090 (diff +2.3e-12), after the impact 0.1999 rad/s
hexagonal result: 2 faces = 2 R = 8.0829 mm = 8.1 mm in 101.98 ms (0.1020 s); spin left after the last face's impact 15.5397 rad/s, under the 21.4236 rad/s the next corner needs; then 10 rocks (each keeps 11/17) until the spin is 0.1999 rad/s, under 1 percent of the threshold (0.2142), stopped at 215.05 ms (0.2150 s) after the nudge; grip needed at the corner during the faces 0.3024, during the rocks up to 0.3711, at each impact 0.3712, all under the desk's 0.5; least corner load 0.3319 of the weight (positive: the corner never lets go); every swing's end spin equals its start spin within 2.3e-12 rad/s; 215051 RK4 steps
drawing check: over 2001 times the pivot corner sits on a corner of the turned hexagon within 3.9e-18 m
the first rock climbs from -30 deg to -20.53 deg over the third corner (9.47 deg of tilt) and falls back; the rocks then get smaller by 11/17 in spin each time
round pencil: rolls without loss at 0.15 m/s (spin 42.8571 rad/s); its centre reaches the edge 25 cm on after 1.6667 s = 1.667 s; it falls freely from the 75 cm desk for sqrt(2 H / g) = 0.3911 s = 0.391 s and lands v0 t = 5.866 cm = 5.9 cm out from the edge at 3.838 m/s; the drawn circle overlaps the desk corner by at most 0.2142 mm (0.64 px) as it tips off (its centre leaves at the edge, v0^2 / r = 6.43 m/s^2 under g); rolling at a steady speed needs no grip
for the description (hexagonal pencil at other nudges): 0.10 m/s (omega0 24.74 rad/s): 1 face = 4.0 mm in 64.2 ms, spin left 16.01 rad/s, 10 rocks, stopped at 181.8 ms, grip needed 0.297 (rocks 0.371); the round pencil reaches the edge in 2.500 s and lands 3.9 cm out; 0.12 m/s (omega0 29.69 rad/s): 1 face = 4.0 mm in 44.5 ms, spin left 19.21 rad/s, 11 rocks, stopped at 202.1 ms, grip needed 0.245 (rocks 0.371); the round pencil reaches the edge in 2.083 s and lands 4.7 cm out; 0.18 m/s (omega0 44.54 rad/s): 2 faces = 8.1 mm in 72.4 ms, spin left 18.65 rad/s, 11 rocks, stopped at 221.3 ms, grip needed 0.891 (rocks 0.371); the round pencil reaches the edge in 1.389 s and lands 7.0 cm out; 0.20 m/s: omega0 49.49 rad/s over the hop limit 45.84: the corner lets go at once, the model ends (a real pencil hops); 0.15 m/s (omega0 37.12 rad/s): 2 faces = 8.1 mm in 102.0 ms, spin left 15.54 rad/s, 10 rocks, stopped at 215.0 ms, grip needed 0.302 (rocks 0.371); the round pencil reaches the edge in 1.667 s and lands 5.9 cm out
checks against the brief (32 checks, 0 failed): R (mm): brief 4.041, sim 4.04145, diff +4.5e-04: ok; omega+ / omega- = 11/17: brief 0.647059, sim 0.647059, diff +0.0e+00: ok; omega+ / omega- (4 places): brief 0.6471, sim 0.647059, diff -4.1e-05: ok; energy kept 121/289: brief 0.418685, sim 0.418685, diff +5.6e-17: ok; corner threshold (rad/s): brief 21.42, sim 21.4236, diff +3.6e-03: ok; corner threshold (m/s): brief 0.0866, sim 0.0865823, diff -1.8e-05: ok; hop limit (rad/s): brief 45.84, sim 45.8421, diff +2.1e-03: ok; hop limit (m/s): brief 0.1853, sim 0.185269, diff -3.1e-05: ok; omega0 at 0.15 (rad/s): brief 37.12, sim 37.1154, diff -4.6e-03: ok; face 1 end spin (rad/s): brief 37.12, sim 37.1154, diff -4.6e-03: ok; after impact 1 (rad/s): brief 24.02, sim 24.0158, diff -4.2e-03: ok; face 2 end spin (rad/s): brief 24.02, sim 24.0158, diff -4.2e-03: ok; after impact 2 (rad/s): brief 15.54, sim 15.5397, diff -3.4e-04: ok; faces at 0.15: brief 2, sim 2, diff +0.0e+00: ok; distance (mm): brief 8.08, sim 8.0829, diff +2.9e-03: ok; distance (mm, 1 place): brief 8.1, sim 8.0829, diff -1.7e-02: ok; time for 2 faces (ms): brief 102, sim 101.981, diff -1.9e-02: ok; grip needed at the corner: brief 0.302, sim 0.302436, diff +4.4e-04: ok; 0.10 m/s faces: brief 1, sim 1, diff +0.0e+00: ok; 0.10 m/s time (ms): brief 64.2, sim 64.1977, diff -2.3e-03: ok; 0.12 m/s faces: brief 1, sim 1, diff +0.0e+00: ok; 0.12 m/s time (ms): brief 44.5, sim 44.4702, diff -3.0e-02: ok; 0.18 m/s faces: brief 2, sim 2, diff +0.0e+00: ok; 0.18 m/s time (ms): brief 72.4, sim 72.3871, diff -1.3e-02: ok; 0.18 m/s grip needed: brief 0.89, sim 0.891418, diff +1.4e-03: ok; 0.20 m/s omega0 (rad/s): brief 49.5, sim 49.4872, diff -1.3e-02: ok; 0.20 m/s hops: brief 1, sim 1, diff +0.0e+00: ok; tilt to tip from rest (deg): brief 30, sim 30, diff -3.6e-15: ok; round: time to the edge (s): brief 1.667, sim 1.66667, diff -3.3e-04: ok; round: fall (s): brief 0.391, sim 0.391091, diff +9.1e-05: ok; round: lands out (cm): brief 5.9, sim 5.86636, diff -3.4e-02: ok; rocks before the spin is under 1 percent of the threshold: brief about 10 to 11, sim 10: ok
drawing: 3000 px per metre; the round pencil 21.0 px across, the hexagonal one 21.0 px across the flats (24.2 across the corners); centres start at x 150, the edge at x 900: 750 px = 25 cm; the hexagonal pencil stops 24.2 px on; inset at 10x: 210 px across the flats
schedule (video time, 1/4 speed): cycles of 8 s start at -8.00, 0.00, 8.00, 16.00, 24.00, 32.00 s; the finger mark moves in over the first 0.3 s and taps both pencils 0.3 s into each cycle at 0.30, 8.30, 16.30, 24.30, 32.30 s; the hexagonal pencil ends its first face 0.129 s later, its second 0.408 s after the nudge at 0.71, 8.71, 16.71, 24.71, 32.71 s, its first rock peaks and falls back by 0.589 s after the nudge and it stops 0.860 s after the nudge at 1.16, 9.16, 17.16, 25.16, 33.16 s (its event row lights); the round pencil reaches the edge 6.667 s after the nudge at 6.97, 14.97, 22.97, 30.97, 38.97 s (its event row lights) and is out of the band 0.456 s later at 7.42, 15.42, 23.42, 31.42, 39.42 s (7.422 s into the cycle; it would hit the floor at 8.531 s into the cycle); the reset crossfade runs over the last 0.5 s of each cycle (from 7.50, 15.50, 23.50, 31.50, 39.50 s); title until 3 s; payoff card from 35.2 s; the title fades back in over the last 0.5 s and the last frame repeats the first (the scene is periodic: 40 s holds exactly 5 cycles)
text widths (the on-screen strings verbatim): overlay@34 863 px '7 mm pencils, 25 cm from the edge | no seed', title line 1@56 612 px 'Nudge both pencils', title line 2@56 653 px 'the same: which one', title line 3@56 566 px 'rolls off the desk?', legend@40 792 px 'same desk, same nudge, 1/4 speed', clock@28 373 px '1.252 s after the nudge', clock held@28 274 px 'before the nudge', label round@40 282 px 'round pencil', sublabel round@28 300 px '7 mm, same nudge', event round@32 513 px 'round: off the desk at 1.67 s', label hex@40 383 px 'hexagonal pencil', sublabel hex@28 300 px '7 mm, same nudge', event hex@32 720 px 'hexagonal: stopped after 2 faces, 8 mm', speed@28 239 px 'speed 0.15 m/s', speed floor@28 184 px 'on the floor', rolled mm@28 238 px 'rolled 99.9 mm', rolled cm@28 226 px 'rolled 25.0 cm', inset label@24 49 px '10x', payoff line 1@40 675 px 'Nudge both pencils the same:', payoff line 2@40 647 px 'which one rolls off the desk?', payoff line 3@40 642 px 'round: off the desk at 1.67 s', payoff line 4@40 693 px 'hexagonal: stops after 8.1 mm', payoff line 5@40 809 px 'each corner keeps 11/17 of the spin', payoff line 6@40 871 px 'next corner needs 21.4 rad/s, has 15.5'
row check: the left column spans x 40 to 423 px and y 20 to 134 under the band top; the rolled readout x 802 to 1040 at y 40; the inset x 760 to 1040 and y 66 to 340 (its desk at y 324, the hexagon's highest corner at y 82, its body within x 779 to 1021, the label x 770 to 819 at y 72 to 98); the pencils' centre line at y 369.5, their tops at 359.0, the desk top at 380 (slab to 408); the leg x 828 to 850 down to 526; the event row x 40 to 760 (widest 720 px) at y 442 to 482; the finger mark from x 10; the round pencil falls past the edge between x 900 and 962 (clear of the leg at 828 to 850); each band is 550 px tall (y 330 to 880 and 880 to 1430); the caption band starts at y 1440; the title rows end at y 330, the band text starts at y 350; the overlay band ends at y 130
inset label check: the label ends at x 819, y 98; the hexagon's centre is at least y 203 and its body at the label's bottom edge spans at most x 839 to 961
Thu Oct  8 10:48:05 AM EEST 2026
```

Checks in the brief, each printed and compared by the sim with an
assert (32 checks, 0 failed):

- R = 4.041 mm: sim 4.0415 mm. ok.
- omega+ / omega- = 11/17 = 0.6471: exact Fraction 11/17, float diff
  0; energy kept 121/289 = 0.4187. ok.
- corner threshold 21.42 rad/s (0.0866 m/s): sim 21.4236 rad/s
  (0.08658 m/s). ok.
- corner loaded below 45.84 rad/s (0.1853 m/s): sim 45.8421 rad/s
  (0.18527 m/s); least corner load over the run 0.3319 of the weight.
  ok.
- at 0.15 m/s, omega0 37.12: face 1 ends at 37.1154, impact to
  24.0158, face 2 ends at 24.0158, impact to 15.5397 under the
  threshold. ok.
- 2 faces = 2 R = 8.08 mm = 8.1 mm in 102.0 ms: sim 8.0829 mm in
  101.98 ms. ok.
- each face's end spin equals its start spin within 1e-9: worst
  2.3e-12 rad/s over 2 faces and 10 rocks. ok.
- about 10 to 11 rocks before the spin is under 1 percent of the
  threshold: sim 10 (spin 0.1999 against 0.2142), stopped at 215.05
  ms. ok.
- grip needed at the corner 0.302: sim 0.3024 during the faces (the
  rocks need up to 0.3711, each impact 0.3712; all under 0.5). ok.
- 0.10 and 0.12 m/s give 1 face, 4.0 mm in 64.2 and 44.5 ms: sim 1
  face, 64.20 and 44.47 ms. ok.
- 0.18 m/s 2 faces in 72.4 ms, grip needed 0.89: sim 72.39 ms, 0.8914.
  ok.
- 0.20 m/s hops (omega0 49.5 over 45.84): sim 49.49 rad/s, hops. ok.
- a hexagonal pencil tips from rest only on a desk tilted past 30 deg:
  sim atan((R / 2) / (a / 2)) = 30.0000 deg. ok.
- round pencil 25 cm in 1.667 s, falls 0.391 s, 5.9 cm out: sim
  1.6667 s, 0.3911 s, 5.866 cm. ok.
- start 25 cm = 750 px from the edge at 3,000 px per metre: asserted
  (centres at x 150, edge at x 900). ok.
- the pivot corner is drawn on a corner of the turned hexagon: within
  3.9e-18 m over 2001 sample times; asserted. ok.
- every fixed text line under 950 px: widest title line 2 653 px at
  56, payoff line 6 871 px, overlay 863 px; asserted. ok.
- layout boxes (left column, rolled readout, inset, desk and pencils,
  leg, event row) pairwise clear; the inset label clear of the
  hexagon's reach; the falling pencil clear of the leg and inside the
  frame; the bottom band ends at the caption band; asserted. ok.
- schedule: nudge 0.3 s into each 8 s cycle (0.30, 8.30, 16.30, 24.30,
  32.30 s), the hexagonal pencil's two faces by 0.71 s and stopped at
  1.16 s of each cycle, the round pencil at the edge at 6.97 s and out
  of the band at 7.42 s, before the crossfade at 7.50 s; 5 cycles in
  40 s; asserted. ok.

### Production

- sims/pencil/pencil.py (new): two-band end-on scene after
  sims/deskchain (bands, clock, crossfade, render loop through ffmpeg
  rawvideo), insets after sims/bankcurve, pivot with an impact after
  sims/kerbhop, stripe after sims/coinroll. Each hexagon face and rock
  is integrated by RK4 at 1e6 steps per second in the corner frame,
  the end located by bisection on an RK4 sub-step; the impact rule
  omega+ = (11/17) omega- is an exact Fraction; 32 brief checks with
  assert; text-width, box and inset-label asserts; loop and periodicity
  prints in the renderer. Deterministic, no seed used.
- projects/pencil/manifest.json: g 9.807, across flats 7 mm, round
  radius 3.5 mm, nudge 0.15 m/s, 25 cm to the edge, desk 75 cm, grip
  0.5, steps_per_second 1e6, stop_fraction 0.01, slow 4, cycle 8 s,
  nudge_at 0.3, finger_s 0.3, reset_fade 0.5, px_per_m 3000, start x
  150, edge x 900, desk top 380 px under the band top, inset 10x,
  title_until 3.0, payoff_t 35.2, music_seed 123, voice_offset 0.6,
  caption_y 0.75.
- Drawing: each pencil 21 px across with a dark stripe from the centre
  to the rim and a thin centre trail; a finger mark slides in from the
  left over the first 0.3 s of each cycle and taps both pencils (three
  gold tick marks); the hexagonal pencil's pivot corner is a gold dot in
  its 10x inset (280 by 274 px, top right, camera follows the centre,
  desk ticks every millimetre scroll past); the round pencil drops off
  the edge and out of the band, its inset showing the desk edge pass
  and the pencil fall out. Gold event rows under the desk (32 px),
  "rolled" readouts turn gold at the event.
- Smoke frames viewed before the full render (media/pencil/smoke-*.png
  at 0.0, 0.35, 0.5, 0.65, 0.8, 1.3, 4.0, 7.05, 7.3, 7.75, 34.0, 39.6
  s). At 1/2 speed (first measure) the hexagonal pencil's whole motion
  (two faces 0.204 s, stopped 0.43 s of video) is a single flick, so
  the scene runs at 1/4 speed as the brief allows (two faces over 0.41
  s, the first rock to 0.59 s, stopped 0.86 s after the nudge). Fixes
  from the smoke pass: the inset desk rectangle failed once the edge
  left the inset (guarded); the inset label shortened to "10x" so the
  hexagon's top corner never meets it.
- Full render: media/pencil/render.log: loop check 0 px (max diff 0),
  periodicity 0 px, loop step 6224 px (the crossfade into the first
  frame); footage.mp4 40.00 s at 60 fps, 2400 frames, 1080x1920.
- TTS: the Piper service on port 10303 returned 503 backend_unavailable
  from 10:29 (its PrivateTmp directory under /tmp is gone, so
  tempfile.NamedTemporaryFile raises OSError; running piper directly
  works). All takes used the same server.py, piper 1.4.2 binary and
  en_US-lessac-medium model as the service, started as a private helper
  on 127.0.0.1:10313 (TTS_API for scripts/voiceover.sh; whisper on
  10301 unchanged); the helper was stopped by its PID after the voice.
- Hook pre-tests (media/pencil/hooks/pretest.log, each one take, all
  ok): hook1 "Nudge both pencils the same: which one rolls off the
  desk?" 3.52 s, the question from 0 s of voice (pause at 1.72 s after
  "the same:"); hook2 "Round pencil or hexagonal pencil: ..." 3.80 s;
  hook3 "Two pencils, the same nudge: ..." 3.24 s; hook4 hook1 plus
  "Same desk, same nudge, fifteen centimeters a second." 7.08 s. Chosen
  hook1: the brief's question, first thing said, identical to the
  title and the payoff. Word pre-test (round pencil, hexagonal pencil,
  stops after eight millimeters, rolls off, over a corner, every corner
  it lands on, rocks back and stops, not enough spin, no corners) ok on
  the first take; "hexagonal" passed, so no fallback.
- Narration projects/pencil/narration.txt, 114 words; the question is
  the first sentence and is repeated word for word before the payoff.
  Drafts at 128, 122 and 119 words were trimmed before any take.
- Voice round trip media/pencil/voice.log: pass 1 failed ("takes about
  a third of its spin" came back "a third if it spin"); pass 2 with
  "takes away about a third of the spin" ok (36.04 s). 2 passes.
- Timing media/pencil/timing.log (offset 0.6 s): the question 0.60 to
  about 4.1 s ("Nudge both pencils the same." 0.60 to 2.31 s);
  "fifteen centimeters a second" in 2.31 to 7.56 s; the repeated
  question 28.62 to about 32.5 s; "The round one rolls off." 32.54 s;
  "The hexagonal one stops after eight millimeters." 33.96 s, with
  "eight" at 35.23 s and "millimeters" 35.49 to 36.20 s (whisper word
  times on the cut tail); the voice ends at 36.64 s of video. The
  hexagonal pencil stops (event row lit) at 33.16 s; the card rises
  from 35.2 s as "eight" is spoken.
- Compose media/pencil/compose.log: music seed 123, 40.00 s; captions
  19 pauses detected, 19 matched, max chunk start shift 2.285 s against
  word-count timing; final.mp4 40.000000 s; preview.mp4 (40.07 s) and
  sheet.png written.

### Local QA

- ffprobe final.mp4: h264 1080x1920 at 60/1, aac 22050 Hz mono,
  duration 40.000000 s; atoms ftyp, moov at 32, free, mdat (faststart);
  4070139 bytes; md5 f3665224d8b37f4f7c64f256d5f6147c.
- Caption and overlay bands: signalstats YMAX of footage.mp4 rows 1440
  to 1530 is 28 and rows 96 to 130 is 28 (background only).
- Captions: 37 caption chunks plus the overlay "7 mm pencils, 25 cm
  from the edge | no seed" in media/pencil/captions.filter; the joined
  caption text equals the narration word for word (114 words) after
  undoing the drawtext escapes; first captions "Nudge both pencils"
  0.600 to 1.546 s, "the same: which one" 1.546 to 3.012 s, "rolls off
  the desk?" 3.012 to 4.164 s.
- Full-resolution frames viewed (media/pencil/qa-*.png): 0.00 s overlay,
  three-row title, both pencils at rest at the start mark, the finger
  marks approaching (motion in frame one), both insets; 0.45 s the tap
  marks, round 5.6 mm, hexagonal on its second face (4.5 mm, 0.08 m/s,
  the gold pivot corner in the inset); 0.70 s hexagonal 7.9 mm at the
  end of face 2; 1.00 s hexagonal 8.1 mm rocking (0.02 m/s, inset tilted
  on its corner), caption "Nudge both pencils"; 2.10 s hexagonal
  stopped, gold event row "hexagonal: stopped after 2 faces, 8 mm",
  rolled 8.1 mm gold; 7.10 s the round pencil just past the edge, its
  event row "round: off the desk at 1.67 s", rolled 25.0 cm gold, the
  inset showing the edge and the pencil dropping; 7.30 s the round
  pencil falling past the leg toward the band bottom, the inset empty;
  21.00 s legend "same desk, same nudge, 1/4 speed", clock, round 17.6
  cm, caption "each corner it lands"; 35.50 s the card rising, caption
  "stops after eight", event row lit; 39.983 s (frame 2399) the same
  picture as frame 0 (raw frames identical; decoded final frames differ
  only by encoder noise on thin lines and small text, 4477 px over 24,
  max 86). Nothing clipped at the frame edge; no text meets a pencil,
  the desk or the insets.
- sheet.png (8x5 at 1 fps): 40 cells, the captions in order, the
  hexagonal pencil stopped and the round pencil travelling in each
  cycle, the round pencil off the desk at 7 s of each cycle, the card
  from 36 s, the loop closes on the first frame.
- Phone read: at 1/4 speed the hexagonal pencil's two faces take 25
  frames and the first rock 11 more; in the 10x inset the hexagon
  visibly tips over two gold pivot corners and rocks back; in the main
  view the 21 px hexagon is small but its stripe and its 8 mm move are
  visible.

### Metadata

- projects/pencil/metadata.json written by a script with asserts: title
  99 characters (at most 100), description 3780 characters (under
  5,000), ASCII, no angle brackets, 12 tags; every number in the title
  and description (67 distinct, commas stripped) appears in
  media/pencil/measure.log.
- Title: Nudge both pencils the same: which one rolls off the desk?
  Round does; hexagonal stops after 8.1 mm
- privacyStatus private, categoryId 27, containsSyntheticMedia true,
  selfDeclaredMadeForKids false.

### Deviations from the brief

- Shown at 1/4 speed, not 1/2: at 1/2 the hexagonal pencil stops 0.43
  s of video after the nudge (two faces in 0.20 s), a single flick on
  the smoke frames. The brief allows the switch; the legend reads
  "same desk, same nudge, 1/4 speed" and the narration says "shown four
  times slower".
- Nudge 0.3 s into the cycle, not 0.5 s: at 1/4 speed with the nudge
  at 0.5 s the falling round pencil would leave the band at 7.62 s,
  inside the 7.5 s crossfade; with 0.3 s it reaches the edge at 6.97 s
  and is out of the band at 7.42 s (asserted). The finger mark still
  approaches from frame one.
- The hexagonal pencil's rocking dies out by 1.16 s of the cycle (0.86
  s after the nudge at 1/4 speed), not "about 1.5 s": the 10 rocks
  take 0.113 s real in total (rock 1 45.4 ms, then each shorter).
- The clock is the shared row under the legend (y 290, real seconds
  after the nudge, as in deskchain and bankcurve), not a per-band
  left-column row; the left column holds the label, "7 mm, same nudge"
  and the live speed.
- Event rows at 32 px, not 40: "hexagonal: stopped after 2 faces, 8 mm"
  is 900 px at 40 px and would cross the desk leg; at 32 px it is 720
  px, left-aligned under the desk.
- Inset 280 by 274 px, not about 220 tall, and its label is "10x": at
  10x the hexagon is 242 px across the corners and its top corner rises
  to 242 px over the inset desk when a corner points up.
- The round pencil leaves the desk as its centre passes the edge (the
  brief's free fall); the drawn circle overlaps the desk corner by at
  most 0.64 px while it tips off (printed, asserted under 1 px).
- The 0.18 m/s variant needs grip 0.891 at the corner, more than the
  chosen 0.5; the description says so.
- Mechanism line: "each corner it lands on takes away about a third of
  the spin" (6/17 = 0.3529 measured, so "about"); "of its spin" failed
  the round trip.
- TTS through a private helper running the same server.py, binary and
  model as the 10303 service, because the service returned 503 (see
  Production).

## Niche note

[produced 2026-10-08 as "Nudge both pencils the same: which one rolls
off the desk? Round does; hexagonal stops after 8.1 mm"; measured
round pencil at 0.15 m/s off the 25 cm desk edge at 1.667 s, falls
0.391 s, lands 5.9 cm out; hexagonal R 4.041 mm, impact keeps 11/17
exactly, corner threshold 21.42 rad/s, faces 37.12 -> 24.02 -> 15.54
rad/s, 2 faces = 8.08 mm in 0.1020 s, 10 rocks, stopped at 0.2150 s,
grip needed 0.3024 (rocks 0.3711), hop limit 45.84 rad/s; 1/4 speed;
task 20261008-102529]

## Upload

- Slipped 2026-10-08T13:57:50+03:00 without an attempt: attempts 1 to 4 of the day went to toast (401, 410 with a stuck stub) and bookstack (401, 401) while Google rejected valid access tokens on about half of all requests from 11:12 to 14:00; attempt 5 was held under the recorded rule. final.mp4 (md5 f3665224d8b37f4f7c64f256d5f6147c) passed every local gate and is ready to upload on the next quota day. Gate: upload.
- Day 41 attempt 3 of 5 (quota day 2026-10-09T10:00 EEST) recorded at 2026-10-09T10:06:18+03:00 before scripts/yt-upload.py pencil; two earlier attempts since the boundary (toast and bookstack, both succeeded). Probe at 10:02 read 0 of 10 rejected.
- Uploaded private as DAoLIbdbjvA at 2026-10-09T07:06:25Z (videos.insert 1,600 units). yt-qa.py --wait --publish: gate 15 of 15 on the first processed read, published at 2026-10-09T10:07:38+03:00, re-read public, 56 units. https://youtu.be/DAoLIbdbjvA
