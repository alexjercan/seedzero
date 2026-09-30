# Produce short: Ball or ring into a wall, which one comes back

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day32

## Goal

Backlog idea (trend research 2026-09-30, task 20260930-100404, pillar 2
chaos and physics, rotation and friction; read the full entry under
"Added by trend research 2026-09-30" in docs/niche.md):
"Ball or ring into a wall: a solid ball and a ring (hoop) rolling at
1.0 m/s on a table with mu 0.3 into a smooth wall 1 m away with a
perfect bounce; measure the speed each rolls back at; expect the ball
to slide 13.9 cm for 0.194 s and roll back at exactly 3/7 = 0.4286 m/s
and the ring to slide 17.0 cm and stop dead (k = 1, 0.000 m/s) while a
spinless puck on ice comes back at the full 1.0 m/s; cylinder 1/3,
hollow ball 1/5; mu only sets the slip distance; a bounce of 0.8 gives
2/7 for the ball and the ring creeps back toward the wall at 0.1;
a grippy wall would also kick the ball up, so say smooth wall;
repeat the roll; deterministic, no seed."

Orchestrator notes (2026-09-30, before this brief). The model: a solid
ball (I = (2/5) m r^2, k = 2/5) and a thin ring (k = 1) of the same
radius r (choose r 3.0 cm, drawn with a stripe or spokes so the spin is
visible) roll without slipping at v0 = 1.0 m/s on a level table with
sliding friction mu = 0.3 toward a smooth vertical wall 1.00 m from
each body's leading edge... define the distance from the start line to
the wall as 1.00 m for the body's centre minus r, so that the hit is at
exactly 1.000 s; print the convention. The wall is smooth (no
tangential impulse) with a perfect bounce (e = 1): at the hit the
centre's velocity reverses and the spin is unchanged. After the hit the
contact point slides on the table at 2 v0, kinetic friction mu m g
acts toward the wall (opposing the slip), slows the centre and unwinds
the spin; the slip ends when the contact point is at rest and the body
rolls again. Checks, not facts (orchestrator closed forms in
/tmp/day32/check.py and check.log): the body rolls again at v0 (e - k)
/ (1 + k) away from the wall: ball 3/7 = 0.4286 m/s, ring 0.0000 m/s
(it stops dead with no spin left); slip time (1 + e) v0 k / ((1 + k) mu
g): ball 0.1942 s, ring 0.3399 s; distance from the wall when the slip
ends: ball 13.87 cm, ring 17.00 cm; energy kept 9/49 = 18.37 percent
(ball) and 0 (ring); angular momentum about the table contact line is
conserved through the slip (print it before and after). Timeline at
1.0 m/s from 1.0 m: both hit at 1.000 s; the ball rolls again at 1.194
s and crosses its start line on the way back at 3.204 s; the ring stops
at 1.340 s. Integrate the slip by a stepped Coulomb model at 1e-6 s (or
finer) and print it against the closed forms, and a half-step rerun.
For the description also print: cylinder 1/3 and hollow ball 1/5 of
v0; a spinless puck on ice comes back at the full 1.0 m/s; a bounce of
e = 0.8 gives 2/7 for the ball and the ring creeps back toward the wall
at 0.1 v0; mu 0.15 and 0.6 change only the slip distance (27.7 and 6.9
cm for the ball); two rolling balls meeting head on each roll back at
3/7; a grippy wall would stop the wall contact from sliding and kick
the body upward, so the claim needs a smooth wall. State every derived
number above as a check the sim must print, not as a fact.

Drawing: side view, two panels stacked on one clock (ball on top, ring
below, the same scale, the same wall at the right, the same start line
at the left), each body with a stripe or spokes so the viewer sees the
spin keep turning the wrong way after the bounce; a slip mark on the
table where the contact slides; readouts per panel: speed toward or
away from the wall and a spin arrow; when the slip ends, labels "rolls
back at 0.43 m/s, 3/7" (ball) and "stops dead, 17 cm from the wall"
(ring) with a distance bracket. Slow motion so the 0.2 to 0.34 s slip
is visible (1/2 or 1/3 speed; say the factor on screen and in the
overlay), several runs in about 40 s with a fade and reset as
tablecloth does; the last frame equals the first. The ball must be
seen rolling all the way back past its start line at least once.

Day thirty-two, first slot. Chosen because "which one comes back" is
argued wrong (most expect both to come back the same), the answer is
two exact fractions (3/7 and zero), the panels end on opposite sides
of the table (the ball back at the start, the ring parked by the
wall), and the cue-ball family (957, 952) is the channel's strongest
without reusing the pool table. Question in the first two seconds:
"Roll a ball and a ring into a wall. Which one comes back?" (or the
producer's shorter wording with the question by word nine; keep the
question identical in the title, the hook and the payoff). Setup
number: one meter per second (say the unit once). Payoff number: the
ball comes back at three sevenths of its speed; the ring stops dead.
The 13.9 cm, 17 cm, 0.19 s and 0.34 s go to the card and the
description. Whisper risks: pre-test "ring", "sevenths" (if "three
sevenths" fails, say "less than half its speed" in the narration and
keep 3/7 on the card and in the title), "dead"; avoid "do you" before
a verb; avoid "pull" as a noun; pre-test hooks with
scripts/voiceover.sh and keep the one whose question lands earliest
under two seconds. Make the last frame equal the first. Measure every
fixed text line with PIL before rendering and keep every line under
950 px, and the title under 100 characters with no < or >. Music seed
98. Templates: sims/cueball (stepped Coulomb slip on a cloth, closed
forms), sims/rollrace and sims/uphill (rolling bodies with stripes,
two panels on one clock, cycle and loop checks), sims/tablecloth (slow
motion, reset fade). Sim name wallbounce: sims/wallbounce/wallbounce.py,
projects/wallbounce/, media/wallbounce/.

## Claim

A solid ball (I = (2/5) m r^2) and a thin ring (I = m r^2) of the same
radius 3 cm roll without slipping at 1 m/s on a table with sliding
friction 0.3 into a smooth vertical wall 1 m from the start line, with a
perfect bounce (e = 1). The wall flips the centre's velocity and leaves
the spin, so the contact point slides at 2.00 m/s and the table's
friction acts toward the wall until the slip closes. The ball slides
0.1942 s and 13.87 cm and rolls back at 0.4286 m/s = 3/7 of its speed
(v0 (k - e) / (1 + k)), keeping 0.1837 of its energy; the ring slides
0.3399 s and 17.00 cm and stops dead (0.0000 m/s, no spin). The angular
momentum about the table contact line, (v + k r omega) / v0, is -0.6000
(ball) and 0.0000 (ring) right after the hit and unchanged after the
slip. Timeline: hit 1.000 s, the ball rolls again 1.194 s, the ring
stops 1.340 s, the ball's leading edge back on the start line 3.204 s.
Narrated: one meter per second (setup); the ball comes back at three
sevenths of its speed, the ring stops dead (payoff). Card: the question;
the ball 3/7, 0.43 m/s; the ring stops dead, 17 cm; the wall flips the
motion, not the spin; slip 0.19 s and 0.34 s; cylinder 1/3, hollow ball
1/5, no spin 1/1. Description: the other shapes, the puck, e = 0.8, mu
0.15 and 0.6, two balls head on, the grippy wall and the checks.

## Evidence

### Measurements

`nix develop -c python3 sims/wallbounce/wallbounce.py --measure-only` at
11:00:14 EEST (the final manifest), media/wallbounce/measure.log, copied
whole:

```
Wed Sep 30 11:00:14 AM EEST 2026
setup: side view, two panels on one clock, the same table (sliding friction mu = 0.3) and the same smooth vertical wall (restitution e = 1, no tangential impulse) 1 m from the start line; top panel a solid ball of radius 3 cm (I = 0.4 m r^2), bottom panel a thin ring of the same radius (I = 1 m r^2); convention: at t = 0 each body's leading edge is on the start line (its centre 3 cm behind it) and rolls without slipping at v0 = 1 m/s, spinning at v0 / r = 33.33 rad/s (5.31 turns a second), so the centre travels 1 m and the hit comes at exactly 1.000 s; 'distance from the wall' is the gap between the wall face and the body's near edge (the centre's travel since the hit); 'back at the start line' is the same edge crossing the line on the way back; g = 9.80665 m/s^2; at the hit the centre's velocity reverses (to -e v0) and the spin is unchanged, then the contact slides and friction mu m g acts toward the wall until the slip closes: stepped Coulomb model at dt = 1e-06 s with the closure located by linear interpolation inside the step, the free rolls before the hit and after the slip at constant speed (no force acts); shown at 1/3 speed on a 12 s cycle (720 frames) with the start line crossed 0.6 s into the cycle, 3 cycles in 36 s; drawn at 840 px per metre, the stripe on each body is a massless mark; deterministic, no seed
ball: stepped model: the hit comes at 1.000000 s with the centre 1.000 m past the start line (the leading edge on the wall); after the hit the centre moves at 1.0000 m/s away from the wall with the spin unchanged at 33.33 rad/s the old way, so the contact slides at 2.0000 m/s; the slip closes 0.194232 s after the hit (closed form (1 + e) v0 k / ((1 + k) mu g) = 0.194232 s, diff +1.0e-12 s) over 194232 steps, 13.874 cm from the wall (closed form e v0 t - mu g t^2 / 2 = 13.874 cm, diff +1.3e-10 cm), and the ball then rolls at 0.428571 m/s away from the wall (closed form v0 (k - e) / (1 + k) = 0.428571 m/s = 3/7, diff -5.9e-12 m/s), spinning at 14.29 rad/s (2.27 turns a second); energy kept 0.1837 of the start (closed form ((k - e) / (1 + k))^2 = 0.1837); angular momentum about the table contact line (v + k r omega) / v0: 1.4000 before the hit, -0.6000 after the hit, -0.6000 after the slip (drift 8.4e-12 through the slip: friction acts on that line and cannot change it); the slip covers 13.874 cm of the centre's path with the spin falling from 33.33 to -14.29 rad/s; timeline: hit 1.000 s, rolls again 1.194 s, leading edge back on the start line 3.204 s, off the left edge of the frame 3.515 s
ring: stepped model: the hit comes at 1.000000 s with the centre 1.000 m past the start line (the leading edge on the wall); after the hit the centre moves at 1.0000 m/s away from the wall with the spin unchanged at 33.33 rad/s the old way, so the contact slides at 2.0000 m/s; the slip closes 0.339905 s after the hit (closed form (1 + e) v0 k / ((1 + k) mu g) = 0.339905 s, diff -2.0e-12 s) over 339906 steps, 16.995 cm from the wall (closed form e v0 t - mu g t^2 / 2 = 16.995 cm, diff +2.1e-10 cm), and the ring then rolls at 0.000000 m/s stopped (closed form v0 (k - e) / (1 + k) = 0.000000 m/s = 0, diff -7.1e-12 m/s), spinning at 0.00 rad/s (0.00 turns a second); energy kept 0.0000 of the start (closed form ((k - e) / (1 + k))^2 = 0.0000); angular momentum about the table contact line (v + k r omega) / v0: 2.0000 before the hit, 0.0000 after the hit, 0.0000 after the slip (drift 1.6e-11 through the slip: friction acts on that line and cannot change it); the slip covers 16.995 cm of the centre's path with the spin falling from 33.33 to 0.00 rad/s; timeline: hit 1.000 s, stops 1.340 s and stays 17.00 cm from the wall
the two panels: the ball rolls back at 0.4286 m/s, 0.4286 of its speed (3/7 = 0.4286), after sliding 0.1942 s and coming to rest as a roller 13.87 cm from the wall; the ring rolls back at 0.0000 m/s: it stops dead after sliding 0.3399 s, 17.00 cm from the wall; the ball keeps 0.1837 of its energy, the ring 0.0000; same speed, same wall, same table: the bounce flips the motion and not the spin, the spin fights the return, and the ring's spin (k = 1) holds exactly as much as its motion
for the description (same table, same 1 m/s): solid cylinder (k = 0.5000): rolls back at 0.3333 m/s (0.3333 v0, closed form 1/3), slip 0.2266 s, 15.11 cm from the wall, energy kept 0.1111; hollow ball (k = 0.6667): rolls back at 0.2000 m/s (0.2000 v0, closed form 1/5), slip 0.2719 s, 16.32 cm from the wall, energy kept 0.0400; a spinless puck on ice (no spin, no friction): comes back at 1.0000 m/s (1.0000 v0), no slip to close, energy kept 1.0000; bounce e = 0.8, ball: leaves the wall at 0.80 m/s, slip 0.1748 s, 9.49 cm from the wall, then rolls at 0.2857 m/s (0.2857 v0, closed form 2/7) away from the wall; bounce e = 0.8, ring: leaves the wall at 0.80 m/s, slip 0.3059 s, 10.71 cm from the wall, then rolls at 0.1000 m/s (0.1000 v0, closed form 1/10) toward the wall (it creeps back to the wall); mu 0.15, ball: rolls back at 0.4286 m/s (the same 3/7), slip 0.3885 s, 27.75 cm from the wall (mu sets only the slip time and distance); mu 0.6, ball: rolls back at 0.4286 m/s (the same 3/7), slip 0.0971 s, 6.94 cm from the wall (mu sets only the slip time and distance); two rolling balls meeting head on (equal masses, frictionless contact: the centre velocities swap, the spins stay): each is in the e = 1 wall state and rolls back at 0.4286 m/s (0.4286 v0) after sliding 0.1942 s; a grippy wall (not modelled in the panels): the wall contact moves down at v0 during the hit, so wall friction that stops that slide gives an upward kick v0 k / (1 + k) = 0.2857 m/s (ball, 2/7 v0) and 0.5000 m/s (ring, 1/2 v0) and takes spin away, so the claim needs a smooth wall
check at half the time step (dt = 5e-07 s): ball slip 0.194231660 s (-2.9e-12), 13.8736900 cm (-2.5e-10), rolls back at 0.428571429 m/s (+1.5e-11), 388464 steps; ring slip 0.339905404 s (-1.6e-12), 16.9952702 cm (-4.2e-10), rolls back at 0.000000000 m/s (+5.1e-12), 679811 steps
schedule (video time, 1/3 speed): cycles of 12 s start at -0.50, 11.50, 23.50, 35.50 s (the first 0.50 s before the first frame); both bodies come in from the left edge 0.40 s before their leading edge crosses the start line, 0.6 s into each cycle at 0.10, 12.10, 24.10 s; both hit the wall at 3.10, 15.10, 27.10 s; the ball rolls again (label lit) at 3.68, 15.68, 27.68 s and the ring stops (label lit) at 4.12, 16.12, 28.12 s; the ball is back at the start line at 9.71, 21.71, 33.71 s and off the frame at 10.64, 22.64, 34.64 s; the marks and the parked ring fade over the last 0.6 s of each cycle (from 10.90, 22.90, 34.90 s); on the first frame the cycle is 0.50 s in (-0.033 s real: both centres 6.3 cm before the start line, rolling in); title until 3 s; payoff card from 27 s; the title fades back in over the last 0.5 s and the last frame repeats the first (the scene is periodic: 36 s holds exactly 3 cycles)
text widths: overlay@34 680 px, title line 1@56 740 px, title line 2@56 629 px, legend@40 772 px, clock@28 418 px, clock rest@28 319 px, label ball@40 204 px, sublabel ball@28 397 px, fixed ball@28 470 px, payoff label ball@40 584 px, bracket ball@28 125 px, label ring@40 194 px, sublabel ring@28 352 px, fixed ring@28 470 px, payoff label ring@40 727 px, bracket ring@28 125 px, speed in@40 560 px, speed out@40 637 px, speed back@40 637 px, speed stopped@40 405 px, spin@28 246 px, contact slides@28 364 px, contact rest@28 355 px, contact stopped@28 381 px, wall word 1@24 101 px, wall word 2@24 55 px, start@24 123 px, payoff line 1@40 807 px, payoff line 2@40 772 px, payoff line 3@40 920 px, payoff line 4@40 852 px, payoff line 5@40 670 px, payoff line 6@40 901 px
layout: the left column ends at x 510 px, the right column starts at x 403 px, both end 136 px under the band top, and on each of the three rows the gap between the left text and the right text is at least 159 px; the wall face is at x 950 px, the wall from 262 to 470 px under the band top; the payoff label row at 200 px spans x 183 to 910 px (its bottom 220 px, above the wall top); the wall label (two words inside the wall) at 292 and 320 px, x 965 to 1065 px (the wall face at 950, the frame edge at 1080), the hatch from 344 px; the bracket text at 372 px (bottom 386) and the bracket at 400 px sit above the body top at 420 px (brackets from x 833 px to the wall with the text x 817 to 942 px (ball), 807 px to the wall with the text x 816 to 941 px (ring)); the bodies are 50 px across; the slip streaks run 117 px (ball) and 143 px (ring) back from the contact at the hit (x 925 px); the geometry layer is y 330 to 1430, the card from y 1552 to 1832; the overlay band y 96 to 130 and the caption band y 1440 to 1530 hold no sim drawing
Wed Sep 30 11:00:17 AM EEST 2026
```

Earlier measure runs, not kept (the physics lines were identical in
every run): 10:54:17 failed the width assert on card line 1 "which one
comes back, the ball or the ring?" (984 px) and line 6 "cylinder 1/3,
hollow ball 1/5, no spin: all of it" (1007 px; now 807 and 901 px), and
the ring's residual v_end of -7.1e-12 m/s produced a nonsense
back-at-the-line time (now |v| under 1e-9 m/s counts as stopped);
10:55:23 failed the layout assert on the wall label ("smooth wall" at 24
px is 164 px wide and ran past x 1070; now two words inside a wall block
that runs off the frame edge); 10:56:04 passed with a 13 s cycle and a
39 s scene (hits at 3.10, 16.10, 29.10 s). After the first smoke frames
the bracket text was clamped 8 px clear of the wall face (it had crossed
the wall) and the stopped ring's contact row became "contact at rest,
stopped". After the voice timing the cycle went to 12 s and the scene
to 36 s (hits at 3.10, 15.10, 27.10 s) and payoff_t from 29.6 to 27.0.

The brief's checks against the log: rolls again at v0 (e - k) / (1 + k):
ball 3/7 = 0.4286 m/s (log 0.428571, closed form 0.428571 = 3/7, diff
-5.9e-12), ring 0.0000 (0.000000, diff -7.1e-12); slip time (1 + e) v0
k / ((1 + k) mu g): ball 0.1942 s (0.194232, diff +1.0e-12), ring
0.3399 s (0.339905, diff -2.0e-12); distance from the wall when the slip
ends: ball 13.87 cm (13.874), ring 17.00 cm (16.995); energy kept 9/49 =
18.37 percent (0.1837) and 0 (0.0000); angular momentum about the
contact line conserved through the slip (-0.6000 and 0.0000 before and
after, drift 8.4e-12 and 1.6e-11); both hit at 1.000 s (1.000000); the
ball rolls again at 1.194 s (1.194) and crosses its start line at 3.204
s (3.204); the ring stops at 1.340 s (1.340); stepped Coulomb at 1e-6 s
(1e-06, 194,232 and 339,906 steps) with a half-step rerun (5e-07 s,
differences 2.9e-12 and 1.6e-12 s); cylinder 1/3 (0.3333, 1/3) and
hollow ball 1/5 (0.2000, 1/5); a spinless puck on ice comes back at 1.0
m/s (1.0000); e = 0.8 gives 2/7 for the ball (0.2857, 2/7) and the ring
creeps back toward the wall at 0.1 v0 (0.1000 toward the wall); mu 0.15
and 0.6 change only the slip distance, 27.7 and 6.9 cm for the ball
(27.75 and 6.94 cm, still 0.4286 m/s); two rolling balls head on each
roll back at 3/7 (0.4286); a grippy wall kicks the body upward (v0 k /
(1 + k) = 0.2857 m/s ball, 0.5000 m/s ring; closed form only, not in the
panels). No check failed; the sim agrees with every derived number in
the brief.

### Production

- Sim: sims/wallbounce/wallbounce.py with
  projects/wallbounce/manifest.json (seed 0, fps 60, g 9.80665, v0 1.0
  m/s, mu 0.3, e 1.0, wall 1.0 m, radius 0.03 m, k_ball 0.4, k_ring 1.0,
  description shapes cylinder 0.5 and hollow ball 2/3, description_e
  0.8, description_mus 0.15 and 0.6, dt 1e-6 s, sim_end 4.0, slow 3,
  cycle_s 12.0, cross_at 0.6, first_cycle_at -0.5, reset_fade 0.6,
  scene_duration 36.0, px_per_m 840, line_x_px 110, title_until 3.0,
  payoff_t 27.0, payoff_hold 0.6, loop_fade 0.5, music_seed 98,
  music_gain 0.18, voice_offset 0.6, caption_y 0.75). Convention: at t
  = 0 each body's leading edge is on the start line (its centre r
  behind it) and the wall face is 1.00 m from the line, so the centre
  travels 1.00 m and the hit comes at exactly 1.000 s; "distance from
  the wall" is the gap between the wall face and the body's near edge.
  The free rolls before the hit and after the slip are constant speed
  (no force acts); the slip is a stepped Coulomb model at 1e-6 s (the
  friction sign re-evaluated every step, the closure by linear
  interpolation inside the step, then the spin snapped to v / r),
  checked against the three closed forms, the angular momentum about
  the contact line and a half-step rerun. Frames are drawn from the
  frame integer modulo the 720-frame cycle, so the scene is exactly
  periodic; the last frame is the live frame 0.
- Layout (1080x1920): overlay "1 m/s | mu 0.3 | 1/3 speed | no seed" at
  y 96 (34 px teal, drawn by compose); title two rows at y 190, 252 (56
  px) until 3 s, then the legend "same speed, same wall, 1/3 speed" at y
  236 (40 px) and the shared clock "N.NNN s after the start line" at y
  290 (28 px); geometry layer y 330 to 1430 drawn at 2x and downsampled;
  ball band from y 330 with the table surface at y 800, ring band from y
  880 with the surface at y 1350; the start line at x 110 (gold notch,
  "start line" under it), 840 px per metre, ticks every 10 cm with "50
  cm" and "1 m", the wall face at x 950 and the wall block to the frame
  edge with "smooth / wall" inside it; left column at x 40: label (40
  px, panel colour), sublabel "mass through the middle" / "all its mass
  on the rim" (28 px), fixed "slides 0.19 s after the bounce" / "slides
  0.34 s after the bounce" (28 px gold, hud only); right column to x
  1040: live "N.NN m/s toward the wall" / "away from the wall" / "0.00
  m/s, stopped" (40 px, gold once the slip has closed), "spin N.N
  turns/s" with a curved arrow icon that shows the direction (28 px),
  and "contact slides N.NN m/s" / "contact at rest, rolling" / "contact
  at rest, stopped" (28 px); the ball coral with a white stripe and dot,
  the ring pale blue with a white diameter stripe and a dot on the rim
  (both marks massless); a streak in the body's colour on the table
  under the contact since the hit; when the slip ends, the gold label
  "rolls back at 0.43 m/s, 3/7" / "stops dead, 17 cm from the wall"
  (40 px, right-aligned 40 px left of the wall face, 200 px under the
  band top) and a gold bracket from the body's near edge to the wall
  face with "13.9 cm" / "17.0 cm" (28 px); the marks and the parked
  ring fade over the last 0.6 s of each cycle; captions at y 1440 (64
  px); the six-line gold card from y 1572 at a 48 px pitch.
- Hook pre-tests (media/wallbounce/hooks/pretest.log, 10:56:30 to
  10:57:00 EEST), each through scripts/voiceover.sh; question onset =
  the silence_end before the question plus 0.6 s, or the voice start
  (plus any leading silence) plus 0.6 s when the question comes first:
  hook1 "Roll a ball and a ring into a wall. Which one comes back?"
  (the brief's wording) passed, question at 2.80 s; hook2 "Ball and
  ring into a wall. Which one comes back?" passed, 2.41 s; hook3 "Which
  one comes back, the ball or the ring?" passed, 0.82 s (leading
  silence 0.22 s); hook4 "Which one comes back from the wall, ball or
  ring?" passed, 0.60 s; hook5 "Which comes back, ball or ring?"
  passed, 0.60 s; hook6 "A ball and a ring roll into a wall. Which one
  comes back?" passed, 2.70 s; hook7 (payoff words) "The ball comes
  back, at three sevenths of its speed. The ring stops dead. Its spin
  ate all of it." failed only on the sentence-initial "Its" (heard
  "it"): "three sevenths" and "stops dead" passed; hook8 (fallback) "The
  ball comes back, at less than half its speed. The ring stops dead. A
  ring is all rim." passed. Kept hook3: the question first, its words
  identical in the title.
- Narration: projects/wallbounce/narration.txt, 112 words, the question
  at words 1 to 9, identical in the title, the hook and the payoff ("So,
  once more, which one comes back? The ball comes back, at three
  sevenths of its speed. The ring stops dead."); numbers as words ("one
  meter per second", "three sevenths"); American "meter"; no
  sentence-initial "Its", no "do you", no "pull", no "too".
- Voice (media/wallbounce/voice.log): pass 1 at 10:58:36 EEST, "ok:
  transcript matches narration (33.088435s) ->
  media/wallbounce/voice.wav". One pass, no mishearing. The voice ends
  at 33.69 s of video.
- Timing (scripts/voice-timing.py media/wallbounce/voice.wav 0.6 in
  media/wallbounce/timing.log, video time; pieces split at the -35 dB /
  0.22 s pauses, so short pauses merge phrases): "Which one comes back,
  the ball or the ring, both roll into a smooth wall at one meter per
  second." 0.60 to 5.67 (the first pause in media/wallbounce/silences.log
  at 2.21 to 2.37 s of wav, so the question ends at 2.81 s of video);
  "The ball rolls back, but slower." 5.67 to 7.68; "The ring stays put.
  Watch the stripe at the next bounce. The wall flips the motion." 7.68
  to 12.32; "but not the spin, so the stripe still turns the old way,"
  12.32 to 15.78; "and the contact slides. The table's grip fights that
  spin, and that costs speed. A ring is all rim," 15.78 to 22.07 (the
  piece transcript heard "crip" for "grip"; the full-file round trip is
  the gate and passed); "so its spin carries as much as its motion. So,
  once more, which one comes back?" 22.07 to 27.03; "The ball comes
  back at three-sevenths of its speed." 27.03 to 29.81; "The ring stops
  dead." 29.81 to 31.06; "All of its speed went into fighting its spin."
  31.06 to 33.69.
- Schedule (from measure.log): cycles of 12 s start at -0.5, 11.5,
  23.5 s; the bodies come in from the left edge 0.40 s before the line
  and cross it at 0.10, 12.10, 24.10 s; both hit the wall at 3.10,
  15.10, 27.10 s; the ball rolls again (label lit) at 3.68, 15.68, 27.68
  s; the ring stops (label lit) at 4.12, 16.12, 28.12 s; the ball is
  back at the start line at 9.71, 21.71, 33.71 s and off the frame at
  10.64, 22.64, 34.64 s; the marks and the parked ring fade from 10.90,
  22.90, 34.90 s. Sync: the first run plays under the question and the
  setup (the first hit at 3.10 s as the question ends); "The ball rolls
  back, but slower. The ring stays put." 5.67 to 9.0 s while the ball
  rolls back and the ring sits parked; "Watch the stripe at the next
  bounce. The wall flips the motion, but not the spin." 9.0 to 13.5 s
  as the second run rolls in; "So the stripe still turns the old way,
  and the contact slides." 13.5 to 17.5 s across the second hit (15.10)
  and the slip (to 16.12); "The table's grip fights that spin, and that
  costs speed. A ring is all rim, so its spin carries as much as its
  motion." 17.5 to 24.6 s while the ball rolls back and the ring is
  parked; "So, once more, which one comes back?" 24.6 to 27.2 s as the
  third run rolls in; the third hit at 27.10 s under "The ball comes
  back," (27.16 to 28.24 caption), the ball's gold label lit at 27.68
  s and the card (payoff_t 27.0, lit at 27.6) before "at three sevenths
  of" (28.24 to 29.20); the ring's stop label lit at 28.12 s before
  "The ring stops dead." (29.94 to 31.19); "All of its speed went into
  fighting its spin." 31.19 to 33.69 s while the ball rolls back to the
  start line (33.71 s).
- Smoke frames (--frames, before the cycle change, on the 13 s-cycle
  schedule): 16 PNGs at 0.0, 1.5, 3.2, 3.5, 3.8, 4.3, 7.0, 9.8, 12.2,
  12.6, 16.4, 29.9, 30.5, 35.8, 38.7, 38.98 s (media/wallbounce/
  smoke-*.png), five of them re-rendered after the bracket and wording
  fixes; used to check the layout, the labels, the bracket, the fade and
  the card before the render.
- Footage: render 11:00:17 to 11:00:53 EEST (media/wallbounce/render.log):
  loop check 0 px, periodicity check 0 px, loop step 3597 px (the seam
  is in motion: on frame 0 both centres are 6.3 cm before the start line,
  rolling in); media/wallbounce/footage.mp4 2160 frames, 36.00 s.
- Compose: scripts/compose.sh 11:00:53 to 11:01:17 (compose.log): music
  seed 98, 36.00 s; "captions: 19 pauses detected, 19 matched, max chunk
  start shift 0.827 s against word-count timing" (every pause matched,
  no fallback); final.mp4 36.000000 s; preview 36.066667 s; sheet 8x5
  at 1 fps.
- Text widths (PIL, from measure.log, all under 950 px): overlay 680,
  title 740 / 629, legend 772, clock 418 / 319, label ball 204, sublabel
  ball 397, fixed ball 470, payoff label ball 584, bracket ball 125,
  label ring 194, sublabel ring 352, fixed ring 470, payoff label ring
  727, bracket ring 125, speed 560 / 637 / 637 / 405, spin 246, contact
  364 / 355 / 355, wall words 101 / 55, start 123, card 807 / 772 / 920 /
  852 / 670 / 901.

### Local QA

- Frames extracted from media/wallbounce/final.mp4 (never edited) and
  viewed with the Read tool at full resolution:
  - frame-0.00.png: overlay, two title rows ("Which one comes back," /
    "the ball or the ring?"), both bodies just left of the start line
    with their stripes, labels and live readouts ("1.00 m/s toward the
    wall", "spin 5.3 turns/s" with the clockwise arrow, "contact at
    rest, rolling"), the smooth wall at the right, no hud, no caption,
    no card. Clean.
  - frame-1.00.png: title up; caption "Which one comes" at y 1440; both
    bodies a third of the way to the wall.
  - frame-2.50.png: caption "the ring?"; both bodies near the wall.
  - frame-3.50.png: legend and clock "1.133 s after the start line",
    fixed lines; the first slip: both at 0.61 m/s away from the wall,
    the ball's spin down to 0.1 turns/s (still the old way), the ring's
    3.2 turns/s, "contact slides 0.63 m/s" / "1.22 m/s", the coloured
    streaks on the table; caption "Both roll into a".
  - frame-4.30.png: the first run's payoff state: the ball "0.43 m/s
    away from the wall" in gold, spin 2.3 turns/s with the arrow
    reversed, "rolls back at 0.43 m/s, 3/7", the "13.9 cm" bracket; the
    ring "0.00 m/s, stopped", "spin 0.0 turns/s", "contact at rest,
    stopped", "stops dead, 17 cm from the wall", the "17.0 cm" bracket;
    caption "smooth wall at one".
  - frame-15.40.png: the second slip, 0.71 m/s away from the wall, the
    ball's spin 1.4 turns/s and the ring's 3.7 turns/s the old way;
    caption "turns the old way,".
  - frame-27.30.png: the third slip 0.2 s after the hit; caption "The
    ball comes back,"; the card fading in; the labels not yet lit.
  - frame-28.70.png: caption "at three sevenths of"; the ball's gold
    label "rolls back at 0.43 m/s, 3/7" lit, the "13.9 cm" bracket, the
    speed row gold; the ring stopped with its label and bracket; the
    six card rows lit and inside the frame ("which one comes back, ball
    or ring?" / "the ball: 3/7 of its speed, 0.43 m/s" / "the ring stops
    dead, 17 cm from the wall" / "the wall flips the motion, not the
    spin" / "slip 0.19 s (ball), 0.34 s (ring)" / "cylinder 1/3, hollow
    ball 1/5, no spin 1/1").
  - frame-30.50.png: caption "The ring stops dead."; the ring parked 17
    cm from the wall with "stops dead, 17 cm from the wall" and the
    "17.0 cm" bracket lit; the ball halfway back; the card lit.
  - frame-33.50.png: caption "its spin."; the ball back at the start
    line, the ring still parked, both labels lit, the card lit.
  - frame-35.98.png: title back, hud gone, the same picture as
    frame-0.00.
  - sheet.png (36 thumbnails at 1 fps): the title for the first 3 s,
    then the legend and clock; three runs; captions readable in every
    thumbnail from 1 to 33 s; the card from 28 s; the fades at 11, 23
    and 35 s; no clipped text, nothing at the frame edge.
- Question: on screen from frame 0 in the title (740 / 629 px), spoken
  from 0.60 s (the voice starts at 0.60 s with no leading silence over
  0.12 s; the question ends at 2.81 s); captions "Which one comes"
  0.600 to 1.337, "back, the ball or" 1.337 to 2.320, "the ring?" 2.320
  to 2.969.
- Captions: media/wallbounce/captions.filter, 35 chunks, 112 words,
  matches projects/wallbounce/narration.txt word for word (script check
  True), longest chunk 20 characters; aligned to the voice pauses (19
  of 19 matched); "So, once more, which" 24.575 to 26.133, "one comes
  back?" 26.133 to 27.158, "The ball comes back," 27.158 to 28.237, "at
  three sevenths of" 28.237 to 29.202, "its speed." 29.202 to 29.936,
  "The ring stops dead." 29.936 to 31.187, "All of its speed" 31.187 to
  32.218, "went into fighting" 32.218 to 32.992, "its spin." 32.992 to
  33.688.
- Bands: signalstats over all 2,160 footage frames: the caption band
  (rows 1440 to 1530) and the overlay band (rows 96 to 130) have YMAX
  28 in every frame (background only), so the sim draws nothing under
  the captions or the overlay.
- Loop: footage last frame equals the first (0 px), periodicity 0 px.
  In final.mp4 frame 2159 against frame 0: 23,917 px over 8 levels, 583
  over 32, max 89, mean 0.53 (h264 quantisation); frame 2158 against
  2159: 26,618 over 8, 3,717 over 32, max 251 (one step of motion and
  the title fade); frame 0 against 1 for reference: 4,622 over 8, 2,824
  over 32, max 255.
- ffprobe: h264 1080x1920 yuv420p 60/1, 2160 frames; aac 22050 Hz mono;
  36.000000 s; 3,326,832 bytes; atoms ftyp moov free mdat (faststart).
- md5sum media/wallbounce/final.mp4: 183c07ace0444f2b304d311bda5f7c56
- Narrated numbers against measure.log: "one meter per second" (setup
  line, v0 = 1 m/s); "three sevenths of its speed" (ball line, 0.428571
  m/s = 3/7; the two panels line 0.4286 of its speed); "The ring stops
  dead" (ring line, 0.000000 m/s stopped; the two panels line "stops
  dead"); "The ball rolls back, but slower. The ring stays put." (the
  same lines); "The wall flips the motion, but not the spin" (setup
  line: the centre's velocity reverses and the spin is unchanged); "the
  stripe still turns the old way, and the contact slides" (ball and
  ring lines: the spin unchanged at 33.33 rad/s the old way, the contact
  slides at 2.0000 m/s); "The table's grip fights that spin, and that
  costs speed" (setup line: friction acts toward the wall until the
  slip closes; the two panels line); "A ring is all rim, so its spin
  carries as much as its motion" (the two panels line: the ring's spin
  (k = 1) holds exactly as much as its motion); "All of its speed went
  into fighting its spin" (ring line: energy kept 0.0000). Card: 3/7
  and 0.43 m/s (0.428571), 17 cm (16.995), 0.19 s (0.194232), 0.34 s
  (0.339905), cylinder 1/3 (0.3333), hollow ball 1/5 (0.2000), no spin
  1/1 (the puck 1.0000).
- Metadata check (script): the 52 distinct numbers in the description
  (0.3, 1 m, 3 cm, 0.4, 1 m r^2, 33.33, 1.000, 2.00, 1e-06, 1/3 speed,
  12 s, 36 s, 0.1942, 13.87, 0.4286, 3/7, 0.1837, 14.29, 0.3399, 17.00,
  0.0000, -0.6000, 8.4e-12, 1.6e-11, 1.194, 3.204, 1.340, 0.3333,
  0.2266, 15.11, 1/5, 0.2000, 0.2719, 16.32, 1.0000, 0.8, 2/7, 0.2857,
  9.49, 0.1000, 0.15, 0.6, 27.75, 6.94, 1/2, 0.5000, 2.0e-12, 2.1e-10,
  7.1e-12, 2.9e-12, 1.6e-12 and the rest) all appear in
  media/wallbounce/measure.log after the final run; none missing.

### Metadata

projects/wallbounce/metadata.json: title "Which one comes back, the ball
or the ring? The ball, at 3/7 of its speed; the ring stops dead" (94
characters, no angle brackets); description 3,549 characters, ASCII,
with the model (the smooth wall, the perfect bounce, the stepped Coulomb
slip at 1e-06 s), the "Measured:" list, the "Why:" paragraph, the rerun
line and the "Made end to end by an AI agent" line; 12 tags (ball or
ring, which one comes back, rolling ball, bouncing off a wall, rolling
without slipping, moment of inertia, angular momentum, friction,
physics, physics visualization, simulation, shorts); categoryId 27;
privacyStatus private; containsSyntheticMedia true;
selfDeclaredMadeForKids false.

### Deviations from the brief

- Hook "Which one comes back, the ball or the ring?" instead of "Roll a
  ball and a ring into a wall. Which one comes back?": the pre-test put
  the brief's wording at 2.80 s (over two seconds); the kept hook starts
  with the question. The title, the hook, the repeat and the payoff
  carry the same words ("which one comes back"), and the answer uses
  them ("The ball comes back").
- Start-line convention: the leading edge starts on the start line (the
  centre r behind it) and the wall face is 1.00 m from the line, so the
  centre travels 1.00 m to the hit at exactly 1.000 s and the ball's
  leading edge is back on the line at 3.204 s, the orchestrator's
  figure. The log prints the convention.
- The stepped Coulomb model runs from the hit until the slip closes;
  the free rolls before the hit and after the slip are constant speed
  (no force acts on a rolling body here), not stepped.
- Three runs of 12 s in a 36 s scene instead of about 40 s: the voice
  put "at three sevenths" at 28.24 s and "The ring stops dead" at 29.94
  s, and a 12 s cycle lights the third run's labels at 27.68 and 28.12
  s, just before those words; the ball is back at the start line (33.71
  s) as the voice ends (33.69 s).
- The narration of run 2 runs ahead of the picture: "The wall flips the
  motion, but not the spin" (10.96 to 13.52 s) is spoken before the
  second hit (15.10 s), and "So the stripe still turns the old way, and
  the contact slides" (13.52 to 17.46 s) spans the hit and the slip. The
  first hit (3.10 s) falls under the setup sentence (2.97 to 5.86 s).
- The 13.9 cm, 17 cm, 0.19 s and 0.34 s are not narrated; they are on
  the labels, the brackets, the card and in the description.
- Card line 1 is "which one comes back, ball or ring?" (the full title
  question was 984 px), and the puck is "no spin 1/1".
- The ring's stripe is a white diameter line and a rim dot (massless
  marks), not spokes; the spin readout shows the size in turns/s with
  a direction arrow rather than a signed number.
- Sublabels "mass through the middle" / "all its mass on the rim" name
  the one difference between the panels in plain words; k is on the
  card and in the description.
- The wall block runs off the right edge of the frame (x 950 to 1080)
  with "smooth / wall" inside it; a block ending at x 1040 had no room
  for the label.
- The card lights at 27.6 s, before the number is spoken (28.24 s), so
  the answer is on screen when "three sevenths" sounds.

## Niche note

[produced 2026-09-30 as "Which one comes back, the ball or the ring?
The ball, at 3/7 of its speed; the ring stops dead"; measured a solid
ball and a thin ring (r 3 cm) rolling at 1 m/s on mu 0.3 into a smooth
wall 1 m away with e = 1: the ball slides 0.1942 s and 13.87 cm and
rolls back at 0.4286 m/s (3/7, energy kept 0.1837), the ring slides
0.3399 s and 17.00 cm and stops dead (0.0000 m/s); angular momentum
about the contact line -0.6000 and 0.0000 before and after the slip;
hit 1.000 s, the ball rolls again 1.194 s and is back at the start line
3.204 s, the ring stops 1.340 s; cylinder 1/3, hollow ball 1/5, spinless
puck 1.0; e 0.8 gives 2/7 (ball) and 0.1 toward the wall (ring); mu 0.15
and 0.6 give 27.75 and 6.94 cm at the same 3/7; two balls head on 3/7
each; a grippy wall would kick the ball up at 0.2857 m/s; stepped
Coulomb at 1e-6 s within 2.0e-12 s of the closed forms, half step
2.9e-12 s; task 20260930-104024]

## Upload

- orchestrator review (2026-09-30T11:15:47+03:00): task evidence, sheet.png and full frames at
  0.00, 28.70, 30.50 and 35.98 s inspected; ffprobe h264 1080x1920 60 fps
  2160 frames 36.000 s; md5 183c07ace0444f2b304d311bda5f7c56; title 94
  chars, no angle brackets; captions match narration word for word;
  measure.log numbers match the closed forms in /tmp/day32/check.py (ball
  back at v(e-k)/(1+k) = 0.4286 m/s, slip 0.1942 s and 13.87 cm; ring
  0.0000 m/s, 0.3399 s and 17.00 cm); approved for upload
- upload attempt 1 of 5 for the quota day that began 2026-09-30T10:00
  EEST, recorded at 2026-09-30T11:15:47+03:00 before starting scripts/yt-upload.py; zero
  attempts were on record since the boundary (no 2026-09-30 upload
  entries in web/data/log.jsonl, no media/*/upload.log newer than the
  boundary)
- uploaded private as vC17_o8y_y4 at 2026-09-30T11:16:10+03:00
  (https://youtu.be/vC17_o8y_y4); channels.list 1 unit + videos.insert
  1,600 units; media/wallbounce/upload.log
- scripts/yt-qa.py wallbounce vC17_o8y_y4 --wait --publish in the
  foreground (started 2026-09-30T11:16:13+03:00): processing wait about
  2.5 min; gate 15 of 15 (processed, succeeded, hd, 1080x1920, title,
  description and tags match, category 27, not made for kids, PT37S for
  the 36.000 s file, private before publish); published at
  2026-09-30T11:19:02+03:00; re-read privacyStatus=public
  selfDeclaredMadeForKids=False embeddable=True; yt-qa quota 63 units;
  media/wallbounce/publish.log
- attempt 1 of 5 complete: 1,664 units; slot 1 of 3 resolved as
  published (recorded 2026-09-30T11:19:38+03:00)

### Quota
- attempt 1 of the hard cap of 5 for the quota day that began
  2026-09-30T10:00 EEST; cost 1,664 units (the channels.list verification
  inside yt-upload.py, the 1,600-unit insert, and the gate run's 12 reads,
  update and re-read as printed by yt-qa.py); day total after this
  attempt 1,664 + 5 for the 10:02 stats refresh = 1,669 of 10,000 used,
  8,331 remaining

## Push
- committed as 5710175 "Publish the day thirty-two slate" and pushed to
  origin/master at 2026-09-30T11:25:56+03:00 (ec85030..5710175; the push also carried
  the unpushed day 31 commit 3b58b88); media/ and secrets/ not committed
