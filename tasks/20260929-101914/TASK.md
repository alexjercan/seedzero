# Produce short: Brake or swerve, a braking car beside a swerving car at the same wall

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day31

## Goal

Backlog idea (trend research 2026-09-29, task 20260929-100144, pillar 2
chaos and physics, road; read the full entry under "Added by trend
research 2026-09-29" in docs/niche.md):
"Brake or swerve: two cars at 50 km/h with the same 0.8 g of grip, a
wide wall 15 m ahead, one braking straight beside one steering away
at full grip; measure where each stops or hits; expect the braking
car to stop in 12.29 m after 1.77 s, 2.71 m short, and the turning
car to need a 24.59 m radius, exactly twice as far (v^2 / (2 mu g)
against v^2 / (mu g)), hitting the wall at 50 km/h at 1.16 s turned
37.6 degrees (asin(d / R)); braking first then turning is never
shorter; a narrow obstacle (2 m sidestep, 9.71 m) can favour the
swerve, so say "a wide wall"; top-down view; repeat the run;
deterministic, no seed."

Orchestrator notes (2026-09-29, before this brief). The model: each car
is a point (drawn as a car body 4.5 m by 1.8 m around it) at v = 50
km/h = 13.8889 m/s with a tyre grip limit of 0.8 g = 7.8453 m/s^2 in any
direction (a friction circle, the same figure the braking short used,
g = 9.80665). A wall spans the whole road width 15.0 m ahead of the
cars' front reference point at t = 0 (a wall across a wide road or a
car park: say "a wall across the road", never a narrow obstacle). No
reaction time: both act at t = 0. Panel A, brake: straight-line
deceleration at the full 0.8 g. Panel B, swerve: full grip sideways, no
braking, the car follows a circle of radius R = v^2 / (mu g) at a
constant 50 km/h. Checks, not facts (orchestrator closed forms in
/tmp/day31/check.py): brake stops in 12.2940 m after 1.7703 s, 2.706 m
short of the wall; swerve radius 24.5881 m, exactly 2.0000 times the
braking distance, and to clear a wall across the road the car must turn
a full 90 degrees, which needs R forward; so at 15 m the swerving car
hits the wall at 1.1616 s turned 37.59 degrees (asin(15 / R)), 5.105 m
to the side, still at 50.00 km/h (39.62 km/h of it square to the wall).
Brake to a speed u and then turn at full grip: the forward distance
(v^2 - u^2) / (2 a) + u^2 / a is least at u = 0, so pure braking wins
for a wide wall (print the scan). Integrate both cars by RK4 (the
swerve as a velocity vector turned by a perpendicular acceleration of
magnitude mu g, the brake as a deceleration) at 6,000 steps a second
or finer and check against the closed forms; print the speed of the
swerve car at every step stays 50.00 km/h and its path radius. For the
description also print the same at 70 km/h (braking 24.10 m, radius
48.19 m) and the narrow-obstacle case (a 2 m sidestep needs 9.71 m
forward, so for a narrow obstacle the swerve can win; say it in the
description, keep it out of the narration). A real car with ABS and
tyre limits differs; say "the same grip, 0.8 g" and point car model in
the description.

State every derived number above as a check the sim must print, not as
a fact.

Drawing: top-down, the road running up the screen as in sims/braking;
two panels side by side or one wide car park with both cars in their
own lanes, the same scale and the same wall; the wall as a solid band
across the top of each panel at 15 m; a start line; the braking car
leaving a skid mark and stopping with a gap readout "stops 2.7 m short";
the swerving car tracing its arc (a faint dashed full quarter circle
showing the 24.6 m it would need, reaching past the wall) and hitting
the wall with an impact flash and "hits at 50 km/h"; live readouts:
distance travelled forward and speed for each car. Keep the whole arc
inside the frame (the swerve car moves 5.1 m sideways before the hit;
start it near the side it turns away from). Slow motion so the 1.2 to
1.8 s event plays over several seconds (1/3 speed like braking, or the
producer's choice; say the factor on screen). Repeat the run (fade and
reset as tablecloth does, or a cycle length that divides the scene);
several runs in about 40 s; the last frame equals the first.

Day thirty-one, first slot. Chosen because "brake or swerve?" is a
driving debate most people answer wrong, the stopping-distance short
(1,012 views) is the best recent road short and its sim is a template,
the two panels end visibly differently (stopped short against a hit),
and the 2x is exact. Question in the first two seconds: "Wall ahead.
Brake or swerve?" (or the producer's better wording; keep the words
before the question under nine; keep the question identical in the
title, the hook and the payoff). Setup number: fifty (kilometers an
hour; say the unit once). Payoff number: braking stops in twelve
meters, a swerve needs twenty five, twice as far. The 2.7 m short, the
1.16 s, the 37.6 degrees and the 70 km/h figures go to the card and the
description. Whisper risks: say "kilometers an hour" not "km/h"; do not
say "g" in the narration; "brakes" (verb) came back "breaks" once on
2026-09-22, so prefer "braking" or "the braking car"; "swerve" is new
to the round trip, pre-test it; avoid "do you" before a verb (whisper
drops "do"); pre-test the hooks with scripts/voiceover.sh and keep the
one whose question lands earliest under two seconds. Make the last
frame equal the first. Measure every fixed text line with PIL before
rendering and keep every line under 950 px, and the title under 100
characters with no < or >. Music seed 95. Templates: sims/braking (the
top-down road, two cars, closed-form checks), sims/tablecloth (two
panels on one clock, slow motion, cycles, reset fade). Sim name swerve:
sims/swerve/swerve.py, projects/swerve/, media/swerve/.

## Claim

Two point cars at 50 km/h = 13.8889 m/s with the same grip, a friction
circle of 0.8 g = 7.8453 m/s^2 (g = 9.80665), and a wall across the
whole road 15 m ahead, no reaction time. The braking car stops in
12.2940 m after 1.7703 s, 2.7060 m short of the wall (v^2 / (2 mu g)).
The swerving car keeps 50.00 km/h and runs on a circle of radius
24.5881 m (v^2 / (mu g)); to stop moving toward a wall across the road it
must turn a full quarter turn, which needs 24.5881 m forward, 2.0000
times the braking distance, exactly twice at any speed. At 15 m it hits
the wall at 1.1616 s, turned 37.59 degrees, 5.105 m to the side, still
at 50.00 km/h (39.62 km/h square to the wall). Braking to a speed u and
then turning needs v^2 / (2 mu g) + u^2 / (2 mu g), least at u = 0, so
pure braking wins for a wall across the road. A narrow obstacle is
different (a 2 m sidestep needs 9.7135 m forward); that stays in the
description. Narrated: fifty kilometers an hour (setup); braking needs
only twelve meters, a full swerve needs twenty five, twice as far
(payoff). Card: 12.3 m, 2.7 m short; 24.6 m, twice as far; the hit at
1.16 s, 50 km/h, 37.6 degrees, 5.1 m to the side; 70 km/h: brake 24.1
m, swerve 48.2 m.

## Evidence

### Measurements

`nix develop -c python3 sims/swerve/swerve.py --measure-only` at
10:49:31 EEST (the final manifest), media/swerve/measure.log, copied
whole:

```
Tue Sep 29 10:49:31 AM EEST 2026
setup: two cars side by side in one wide car park, both at 50 km/h = 13.8889 m/s with the same tyre grip, a friction circle of 0.8 g = 7.8453 m/s^2 in any direction (g = 9.80665); each car is a point, the centre of its front bumper, drawn as a 4.5 x 1.8 m body behind it; a wall spans the whole width 15 m ahead of both points at t = 0; no reaction time, both act at t = 0; left car brakes straight at the full grip, right car steers left at the full grip with no braking; RK4 at 12000 steps per second (dt = 8.33e-05 s), events by bisection inside the step; shown at 1/3 speed, drawn at 34 px per metre; deterministic, no seed
brake: RK4 stops at 12.2940 m after 1.7703 s (closed forms v^2 / (2 mu g) = 12.2940 m, v / (mu g) = 1.7703 s); it stops 2.7060 m short of the wall; sideways drift 0.0e+00 m; max |x - closed form| 2.5e-12 m and |v - closed form| 4.6e-12 m/s over 21245 steps
swerve: the speed stays 50.00 km/h at every step (max |speed - v| 3.9e-14 m/s to the wall, 6.8e-14 m/s over the full quarter turn) and the path is a circle of radius 24.5881 m about the point 24.5881 m to the left of the start (closed form v^2 / (mu g) = 24.5881 m; the distance to that centre stays between 24.588065 and 24.588065 m, max |r - R| 1.8e-13 m over 33371 steps); the radius is 2.0000 times the RK4 braking distance
swerve hits the wall: RK4 at 1.1616 s (closed form R asin(D / R) / v = 1.1616 s), turned 37.59 degrees (closed form asin(D / R) = 37.59), 5.105 m to the side (closed form R (1 - cos) = 5.105 m), at 50.00 km/h, of which 39.62 km/h is square to the wall and 30.50 km/h along it
a full swerve (a quarter turn, until the car runs along the wall): RK4 24.5881 m forward and 24.5881 m to the side after 2.7808 s (closed forms R = 24.5881 m, (pi / 2) R / v = 2.7808 s); it needs 9.5881 m more than the 15 m to the wall; full swerve over braking: 2.0000
at the moment of the hit (1.1616 s) the braking car is 10.840 m from the line doing 17.19 km/h; it stops 0.6088 s later
body check: the point model hits when the bumper centre reaches the wall; the outer front corner (0.9 m to the right of the centre) is (R + 0.9) sin(angle) ahead, so the body touches first at 1.1139 s, turned 36.05 degrees, with the bumper centre at 14.470 m, 0.0476 s earlier (drawn: the car stops at the point-model hit with that corner under the wall band)
brake then turn (brake straight at full grip to a speed u, then turn at full grip until running along the wall; forward distance (v^2 - u^2) / (2 mu g) + u^2 / (mu g) = v^2 / (2 mu g) + u^2 / (2 mu g)): to 0 km/h: 12.2940 m in 1.7703 s (closed form 12.2940); to 10 km/h: 12.7858 m in 1.9724 s (closed form 12.7858); to 20 km/h: 14.2611 m in 2.1745 s (closed form 14.2611); to 30 km/h: 16.7199 m in 2.3766 s (closed form 16.7199); to 40 km/h: 20.1622 m in 2.5787 s (closed form 20.1622); to 50 km/h: 24.5881 m in 2.7808 s (closed form 24.5881); least at 0 km/h, 12.2940 m: pure braking; any turning adds u^2 / (2 mu g), and the grip can never slow the car toward the wall faster than mu g, so no path stops the forward motion in under 12.2940 m
for the description: a narrow obstacle: to move 2 m sideways the swerving car needs 9.7135 m forward (closed form sqrt(2 R s - s^2) = 9.7135 m) after 0.7190 s, less than the 12.2940 m braking distance, so for a narrow obstacle a swerve can win; at the braking distance the swerve is 3.2942 m to the side (closed form R (1 - sqrt(3) / 2) = 3.2942 m), so a swerve wins only when less than that much sideways room is needed; at 70 km/h: braking 24.0963 m in 2.4785 s, full swerve 48.1926 m (radius 48.1926 m, ratio 2.0000), a 2 m sidestep 13.7394 m, the tie at 6.4566 m to the side
check at half the time step (24000 steps per second): brake stop 12.294032 m (-1.8e-14) at 1.770341 s (+6.5e-13); swerve hit at 1.161567 s (+6.5e-13), full swerve 24.588065 m (+2.0e-13)
schedule (video time, 1/3 speed; the swerve hits 3.485 s and the braking car stops 5.311 s after each release; each run drives in 0.8 s before its release and fades over the last 0.8 s): run 1: drives in from 5.00, release 5.80, swerve hits 9.28, brake stops 11.11, holds 7.29 s, fades 18.40 to 19.20; run 2: drives in from 19.20, release 20.00, swerve hits 23.48, brake stops 25.31, holds 9.49 s, fades 34.80 to 35.60; run 3: drives in from 35.60, release 36.40, swerve hits 39.88, brake stops 41.71, holds 0.49 s, fades 42.20 to 43.00 (past the scene end, so on the circle: swerve hits 1.88, brake stops 3.71, fades 4.20 to 5.00); the last run is the first run one scene later (36.40 - 38 = -1.60 s), so on the first frame the run is 0.5333 s real after the line: the swerving car 7.30 m forward, 1.11 m to the side, turned 17.3 degrees, the braking car 6.29 m forward at 34.9 km/h; title until 3 s; payoff card from 26.6 s; full-swerve label gold from 29.3 s; the dashed quarter circle beyond the wall brightened from 16.4 to 19.9 s; the title fades back in over the last 0.5 s and the last frame repeats the first
text widths: overlay@34 911 px, title line 1@56 370 px, title line 2@56 545 px, legend@40 771 px, clock@28 332 px, clock rest@28 233 px, label brake@40 128 px, label swerve@40 161 px, speed@48 269 px, stopped@48 220 px, forward@32 276 px, start@28 144 px, wall@26 583 px, full swerve@32 485 px, gap@36 233 px, stop mark@32 278 px, hit@36 306 px, ruler@22 61 px, payoff line 1@40 817 px, payoff line 2@40 822 px, payoff line 3@40 899 px, payoff line 4@40 784 px, payoff line 5@40 872 px, payoff line 6@40 865 px
layout: start line y 1240, wall face y 730.0 (band from y 689.2), braking stop y 822.0, full-swerve line y 404.0 (label centre y 372.0), arc centre x 144.0, impact x 806.4
row check: the brake column spans x 240 to 516 px (car to x 211), the swerve column x 644 to 920 px (car from x 949); the start label spans x 468 to 612
clearance: the hit label (x 554 to 860, y 887 to 923) is 17 px under the crashed body, 42 px left of the swerve's path and 23 px under the braking stop label
exit 0
Tue Sep 29 10:49:36 AM EEST 2026
```

Earlier measure runs, all with the same physics and the same numbers
(only the layout, the labels and the schedule lines changed): the first
draft of the brake RK4 never reached its stop event, because the
deceleration flipped sign with the velocity near zero; the brake is now
a constant deceleration along the road and the stop is located by
bisection. The turn run first shared one drift record between the hit
run and the quarter-turn run; each run now has its own recorder. One
run failed the layout assert "the gap label touches the hit label"
(both at y 776); the hit label moved under the crashed car (x 554 to
860, y 887 to 923) and a clearance check was added (17 px under the
body, 42 px from the path, 23 px under the stop label). The schedule
then moved from a 40 s scene to 38 s with releases at 5.8, 20.0 and
36.4 s, set from the pass 5 voice timing, and the arc highlight window
16.4 to 19.9 s was added. The RK4 numbers, the checks and the widths of
the unchanged lines were identical in every run.

The brief's checks against the log: brake 12.29 m after 1.77 s
(12.2940 m, 1.7703 s), 2.71 m short (2.7060 m); radius 24.59 m (24.5881
m), exactly twice (2.0000); the hit at 1.16 s turned 37.6 degrees
(1.1616 s, 37.59 degrees), 5.105 m to the side (5.105 m), 50.00 km/h
with 39.62 km/h square to the wall (50.00, 39.62); brake then turn
never shorter (least at 0 km/h, 12.2940 m); 70 km/h braking 24.10 m and
radius 48.19 m (24.0963, 48.1926 m); the 2 m sidestep 9.71 m (9.7135 m).
Every check holds. One extra fact from the log: the point model hits
when the bumper centre reaches the wall; the body's outer front corner
touches 0.0476 s earlier (1.1139 s).

### Production

- Sim: sims/swerve/swerve.py with projects/swerve/manifest.json (seed 0,
  fps 60, g 9.80665, grip_g 0.8, speed_km_h 50, wall_m 15, car 4.5 x 1.8
  m, lane 3.0 m, wall 1.2 m thick, steps_per_second 12000, scan speeds 0
  to 50 km/h, description speed 70 km/h, sidestep 2 m, slow 3, preroll
  0.8, release_times 5.8 / 20.0 / 36.4, reset_fade 0.8, hit_flash 0.5,
  scene_duration 38.0, px_per_m 34, line_y_px 1240, brake_x_px 180,
  swerve_x_px 980, title_until 3.0, payoff_t 26.6, payoff_hold 0.6,
  swerve_gold_t 29.3, arc_hi 16.4 to 19.9, loop_fade 0.5, music_seed 95,
  music_gain 0.18, voice_offset 0.6, caption_y 0.75). RK4 on (x, y, vx,
  vy): the brake as a constant deceleration mu g along the road, the
  swerve as the velocity turned by a perpendicular acceleration of
  magnitude mu g; the stop, the hit (y = 15 m) and the quarter turn (vy
  = 0) by 60 bisections inside the crossing step; checked against the
  closed forms and a half-step rerun at 24,000 steps a second. Frames
  draw the closed forms at the video time (the RK4 agrees within
  2.5e-12 m on the brake and 1.8e-13 m on the swerve radius). Each run drives in at 50 km/h for 0.8 s before its
  release, holds, then fades over 0.8 s (the old run out in the first
  half, the new run in over the second half); the third run crosses the
  loop seam, so frame 0 is 0.5333 s real after its release and the last
  frame is the live frame 0.
- Layout (1080x1920): overlay at y 96 (34 px teal, drawn by compose);
  title two rows at y 190, 252 (56 px) until 3 s, then the legend "same
  speed, same grip, 1/3 speed" at y 236 (40 px) and the shared clock
  "N.NNN s after the line" at y 290 (28 px); one geometry layer y 320 to
  1430 drawn at 2x and downsampled; the start line at y 1240, 34 px per
  metre, the wall face at y 730 (15 m) with a concrete band, joints and
  a hazard stripe from y 689, the label "wall across the whole road, 15
  m ahead" (26 px) on the band; a ruler at x 22 every 5 m; the braking
  car's lane at x 180 (teal), the swerving car from x 980 turning left
  (coral); beyond the wall a faint dashed quarter circle to the full-turn
  line at y 404 (24.6 m) with "a full swerve needs 24.6 m" (32 px, coral,
  gold from 29.3 s) and an arc highlight 16.4 to 19.9 s; skid marks, a
  stop mark with the gap bracket "2.7 m short" (36 px gold) and "stops in
  12.3 m" (32 px gold); the swerve trace, an impact flash (white core,
  ring, 12 spikes) for 0.5 s and "hits at 50 km/h" (36 px) under the
  crashed car; readout columns at x 240 (left-aligned, brake) and x 920
  (right-aligned, swerve) in rows y 1290 / 1345 / 1395: label (40 px),
  speed or "stopped" (48 px), "N.N m forward" (32 px); captions at y
  1440 (64 px); the six-line gold card from y 1572 at a 48 px pitch.
- Hook pre-tests (media/swerve/hooks/pretest.log, 10:24:28 to 10:25:05
  EEST), each through scripts/voiceover.sh; question onset = the end of
  the pause after the opening words plus 0.6 s: hook1 "Wall ahead. Brake
  or swerve? ..." passed, 1.78 s, repeat takes 1.62 and 1.54 s; hook2
  "A wall ahead. ..." failed ("ahead" heard "head"); hook3 "Wall ahead.
  Should you brake or swerve? ..." passed, 1.52 s, but the question
  differs from the title; hook4 "A wall across the road. Brake or
  swerve? ..." failed ("brake" heard "break"); hook5 "Wall ahead. Brake
  hard or swerve? ..." failed ("wallhead", "harder"). Kept hook1, the
  brief's wording.
- Narration: projects/swerve/narration.txt, 106 words, the question at
  words 3 to 5 ("Wall ahead." is two words), identical in the title, the
  hook and the payoff; numbers as words ("fifty kilometers an hour",
  "twelve meters", "twenty five", "twice as far"); "the braking car"
  and "braking" for the verb; no "g" and no "km/h" spoken.
- Voice (media/swerve/voice.log): pass 1 at 10:29:23 passed (33.054 s,
  the left car first). Pass 2 at 10:31:24 ("reordered: the right car
  first, then the left car, then the wall, then the payoff") passed
  (33.065 s). Pass 3 at 10:44:15 (the final 106-word text; payoff
  "Braking needs only twelve meters." so the caption keeps the number
  with its unit) failed: "swerve" heard "s werve". Pass 4 at 10:44:25,
  the same text, failed: "brake" heard "break" three times. Pass 5 at
  10:44:38, the same text: "ok: transcript matches narration
  (31.497868s) -> media/swerve/voice.wav". The voice ends at 32.10 s of
  video.
- Timing (scripts/voice-timing.py media/swerve/voice.wav 0.6, in
  media/swerve/timing.log; its pieces are transcribed alone, so "Wall
  ahead" comes back "Wallahood" and "Brake" "Break" there, while the
  full-file round trip passed): 0.60 to 1.38 "Wall ahead."; 1.38 to 8.06
  "Brake or swerve? Two cars at 50 kilometers an hour, with the same
  grip, the right car steers away as hard as it can,"; 8.06 to 9.58 "and
  hits the wall at 50."; 9.58 to 12.05 "The left car is braking as hard
  as it can,"; 12.05 to 25.39 "and stops short. ... So, wall ahead.";
  25.39 to 27.02 "Brake or swerve, brake."; 27.02 to 29.14 "Braking needs
  only 12 meters."; 29.14 to 32.10 "A full swerve needs 25, twice as
  far.". Finer split from the pauses (silencedetect n=-35dB d=0.08,
  media/swerve/silences.log, plus 0.6 s): "Wall ahead." 0.60 to 1.23;
  "Brake or swerve? Two cars at fifty kilometers an hour," 1.53 to
  4.40; "with the same grip." 4.61 to 5.40; "The right car steers away as
  hard as it can," 5.57 to 7.89; "and hits the wall at fifty." 8.23 to
  9.44; "The left car is braking as hard as it can," 9.72 to 11.93; "and
  stops short." 12.17 to 13.01; "The wall spans the whole road, so a
  swerve must turn all the way." 13.14 to 16.40; "The dashed line is
  that turn. It reaches past the wall." 16.60 to 19.64; "The swerving
  car keeps all its speed." 19.80 to 21.53; "The braking car loses speed
  the whole way." 21.67 to 24.00; "So, wall ahead. Brake or swerve?"
  24.16 to 26.42; "Brake." 26.61 to 26.88; "Braking needs only twelve
  meters." 27.16 to 29.02; "A full swerve needs twenty five, twice as
  far." 29.27 to 31.88 (pause after "twenty five," at 30.92 to 31.10).
- Schedule against the words: run 1 releases at 5.8 as "The right car
  steers away" starts (5.57); the swerve hits at 9.28 inside "and hits
  the wall at fifty" (8.23 to 9.44); the braking car stops at 11.11
  inside "The left car is braking as hard as it can" (9.72 to 11.93),
  just before "and stops short" (12.17). The arc beyond the wall is
  brightened 16.4 to 19.9 under "The dashed line is that turn. It
  reaches past the wall." (16.60 to 19.64). Run 2 releases at 20.0
  under "The swerving car keeps all its speed" (the coral readout stays
  50.0 km/h) and "The braking car loses speed the whole way" (21.67 to
  24.00, the teal readout falls); it hits at 23.48 and stops at 25.31,
  both results on screen with the card from 26.6 ("Brake." 26.61). "a
  full swerve needs 24.6 m" turns gold at 29.3 as "A full swerve needs
  twenty five" starts (29.27). Run 2 fades 34.8 to 35.6 after the voice
  ends (32.10); run 3 drives in from 35.6 and crosses the loop seam.
- Pre-render smoke frames (media/swerve/smoke-*.png, viewed): the
  title, the overlay and the readouts clear of each other; the gap and
  stop labels clear of the hit label; the whole arc inside the frame;
  the arc highlight at 17.5; the reset fade at 18.8 (cars gone, "before
  the line"); 37.98 the same picture as 0.0. Two blemishes found and
  fixed before the render: the ruler "0" label sat on the start line
  (the 0 and 15 labels are no longer drawn; the start line and the
  wall label name them), and the gap label overlapped the hit label
  (moved, see the measure runs).
- Footage: render 10:49:45 to 10:50:32 (media/swerve/render.log): loop
  check 0 px, periodicity check 0 px (the scene drawn live at 38 s
  equals 0 s), loop step 5,862 px (one frame of motion, the seam is
  inside a run); media/swerve/footage.mp4 2280 frames.
- Compose: scripts/compose.sh 10:50:41 to 10:50:53 (compose.log): music
  seed 95, 38.00 s; captions 34 chunks; final.mp4 38.000000 s; preview
  38.066667 s; sheet 8x5 at 1 fps.
- Text widths (PIL, from measure.log, all under 950 px): overlay 911,
  title 370 / 545, legend 771, clock 332 / 233, labels 128 / 161, speed
  269, stopped 220, forward 276, start 144, wall 583, full swerve 485,
  gap 233, stop mark 278, hit 306, ruler 61, payoff 817 / 822 / 899 /
  784 / 872 / 865.

### Local QA

- Frames extracted from media/swerve/final.mp4 (never edited) and viewed
  with the Read tool:
  - frame-0.00.png (frame 0): overlay "50 km/h | same grip, 0.8 g | 1/3
    speed | no seed", the title rows "Wall ahead." / "Brake or
    swerve?", the dashed quarter circle and "a full swerve needs 24.6
    m" (coral), the wall band and label, both cars mid-run (brake 34.9
    km/h, 6.3 m forward; swerve 50.0 km/h, 7.3 m forward, turning);
    no caption, no card. Clean; a usable thumbnail.
  - frame-0.60.png: caption "Wall ahead." at y 1440; the title still
    up; brake 29.3 km/h 8.1 m, swerve 9.9 m.
  - frame-1.60.png: caption "Brake or swerve?"; the swerve car near the
    wall at 13.9 m (it hits at 1.88 s); brake 19.9 km/h.
  - frame-9.30.png (the first hit, 9.28): the impact flash at the wall,
    the swerve readout "50.0 km/h" in red and "15.0 m forward" in
    gold, "hits at 50 km/h" fading in under the car, the braking car at
    17.0 km/h 10.9 m; legend and clock "1.167 s after the line";
    caption "wall at fifty.".
  - frame-28.30.png ("twelve meters" spoken, 27.16 to 29.02): the
    braking car stopped with "2.7 m short" and "stops in 12.3 m", the
    readout "stopped" / "12.3 m forward" in gold, the crashed swerve
    car with "hits at 50 km/h"; the card lit (six gold rows, "braking
    stops in 12.3 m, 2.7 m short" on row 2); caption "Braking needs
    only". The payoff number is on screen when spoken.
  - frame-30.50.png ("twenty five" spoken, before the pause at 30.92):
    "a full swerve needs 24.6 m" in gold at the end of the dashed
    quarter circle, the card row 3 "a full swerve needs 24.6 m, twice
    as far"; caption "A full swerve needs". The payoff number is on
    screen when spoken.
  - frame-37.98.png (frame 2279): title back, card and hud gone, both
    cars at the same positions and readouts as frame 0 (34.9 km/h 6.3
    m, 50.0 km/h 7.3 m). The loop closes.
  - sheet.png (38 thumbnails at 1 fps): the title for the first 3 s,
    then the legend and clock; run 3's hit at 1.9 s and its fade at 4
    to 5 s; run 1 5.8 to 19.2 with the hit, the stop and the labels;
    the arc highlight at 17 to 19; run 2 20 to 35.6; the card from 27
    s; captions readable in every thumbnail from 1 to 31 s; no clipped
    text, nothing at the frame edge.
- Question: on screen from frame 0 in the title (370 / 545 px), spoken
  from 1.53 s (first silence_end 0.928 s in the wav plus 0.6).
- Captions: media/swerve/captions.filter, 34 chunks, 106 words, matches
  projects/swerve/narration.txt word for word (script check True),
  longest chunk 20 characters; "Brake or swerve?" 1.194 to 2.086;
  "Brake." 27.641 to 27.938; "Braking needs only" 27.938 to 28.829;
  "twelve meters." 28.829 to 29.424; "A full swerve needs" 29.424 to
  30.612; "twenty five, twice" 30.612 to 31.504; "as far." 31.504 to
  32.098. captions.py spaces the chunks by word count, so they run
  ahead of the voice early ("Brake or swerve?" from 1.19 against 1.53)
  and up to about 1.4 s behind it mid-way ("Brake." 27.64 against
  26.61); every chunk shows while its sentence or the next one is
  spoken, and the numbers stay on screen in the labels and the card.
- Bands: signalstats over all 2,280 footage frames: the caption band
  (rows 1440 to 1530) and the overlay band (rows 96 to 130) have YMAX
  28 in every frame (background only), so the sim draws nothing under
  the captions or the overlay.
- Loop: footage last frame equals the first in the render (0 px); in
  footage.mp4 frame 2279 against 0: 12,846 px over 8 levels, 139 over
  32, max 56 (codec noise). In final.mp4 frame 2279 against frame 0:
  27,538 px over 8 levels, 525 over 32, max 75, mean 0.52 (h264
  quantisation, the same order as icerod's 21,831 / 388 / 85); frame
  2278 against 2279: 5,900 px over 32 (one frame of motion).
- ffprobe: h264 1080x1920 yuv420p 60/1, 2280 frames (counted); aac
  22050 Hz mono; 38.000000 s; 3,478,651 bytes; moov before mdat
  (faststart, moov at byte 36).
- md5sum media/swerve/final.mp4: 3d9f50fecbdb7b0f16652aff5f0190d7
- Narrated numbers against measure.log: "fifty kilometers an hour"
  (setup: 50 km/h = 13.8889 m/s); "hits the wall at fifty" (swerve hits
  the wall: at 50.00 km/h); "stops short" (brake: 2.7060 m short); "It
  reaches past the wall" (a full swerve: 24.5881 m forward, 9.5881 m
  more than the 15 m); "keeps all its speed" (swerve: the speed stays
  50.00 km/h at every step); "loses speed the whole way" (at the moment
  of the hit the braking car is at 17.19 km/h); "Brake." (brake then
  turn: least at 0 km/h, 12.2940 m, pure braking); "Braking needs only
  twelve meters" (brake: 12.2940 m); "A full swerve needs twenty five"
  (a full swerve: R = 24.5881 m); "twice as far" (full swerve over
  braking: 2.0000). Card: 12.3 / 2.7 / 24.6 m, 1.16 s, 50 km/h, 37.6
  degrees, 5.1 m, 70 km/h 24.1 / 48.2 m, all from the same lines.
- Metadata check: every number in the description read against
  media/swerve/measure.log after the final run by script (56 numbers;
  all present as printed except the title's 12.3 and 24.6 m, the
  on-screen roundings of 12.2940 and 24.5881 m).

### Metadata

projects/swerve/metadata.json: title "Wall ahead. Brake or swerve?
Braking needs 12.3 m, a full swerve 24.6 m, twice as far" (85
characters, no angle brackets); description 3,280 characters, ASCII,
with the model, the "Measured:" list (including the 70 km/h case, the
narrow obstacle and the point-model corner), the "Why:" paragraph with
the point car / ABS caveat and "the same grip", the rerun line and the
AI-made line; 12 tags; categoryId 27; privacyStatus private;
containsSyntheticMedia true; selfDeclaredMadeForKids false.

### Deviations from the brief

- The scene is 38 s, not about 40 s: the pass 5 voice ends at 32.10 s,
  and a 40 s scene left a long silent tail.
- The runs are not on a fixed cycle: three releases at 5.8, 20.0 and
  36.4 s, set from the voice timing so each result lands on its words;
  the third run crosses the loop seam (its hit shows at 1.88 s under
  the question). The loop still closes (periodicity check 0 px).
- Payoff wording "Braking needs only twelve meters. A full swerve needs
  twenty five, twice as far." instead of "braking stops in twelve
  meters": the caption chunk keeps "twelve meters." together. The card
  and the on-screen label say "stops in 12.3 m".
- "fifty" is spoken twice ("fifty kilometers an hour" and "hits the
  wall at fifty"); the second is the swerve's speed at the hit, the
  same measured 50.00 km/h, not a second setup number.
- The point model hits when the bumper centre reaches the wall; the
  body's outer front corner would touch 0.0476 s earlier (1.1139 s).
  The drawn car stops at the point-model hit with that corner under
  the wall band. The description says so.
- The label "hits at 50 km/h" sits under the crashed car, not at the
  impact point, to keep it clear of the gap and stop labels.
- Captions are spaced by word count (captions.py), so they run up to
  about 1.4 s behind the voice mid-way; the numbers are on screen in the
  labels and the card before they are spoken.
- The voice passed on pass 5; passes 3 and 4 of the same text failed
  the round trip ("swerve" heard "s werve"; "brake" heard "break").
- The overlay carries "50 km/h | same grip, 0.8 g | 1/3 speed | no
  seed"; the slow-motion factor is also in the legend.
- Kept hook1 ("Wall ahead. Brake or swerve?") although hook3 ("Wall
  ahead. Should you brake or swerve?") landed its question earlier on
  its first take (1.52 against 1.78 s): hook3's question differs from
  the brief's title question, and hook1's repeat takes landed at 1.62
  and 1.54 s; the final voice lands it at 1.53 s.

## Niche note

[produced 2026-09-29 as "Wall ahead. Brake or swerve? Braking needs
12.3 m, a full swerve 24.6 m, twice as far"; measured at 50 km/h with
the same 0.8 g grip: braking stops in 12.2940 m after 1.7703 s, 2.7060
m short of a wall across the road at 15 m; the swerve keeps 50.00 km/h
on a 24.5881 m radius, a full quarter turn needs 24.5881 m, 2.0000
times; it hits at 1.1616 s turned 37.59 degrees, 5.105 m to the side,
39.62 km/h square to the wall; brake then turn least at u = 0; 70 km/h
24.0963 against 48.1926 m; a 2 m sidestep 9.7135 m (narrow obstacles
can favour the swerve); RK4 at 12,000 steps a second within 2.5e-12 m
of the closed forms; task 20260929-101914]

## Upload

- orchestrator review (2026-09-29T11:17:15+03:00): task evidence, sheet.png and frames at
  0.00, 30.50 and 37.98 s inspected; numbers match measure.log and the
  closed forms in /tmp/day31/check.py (v^2 / (2 mu g) = 12.2940 m, v^2 /
  (mu g) = 24.5881 m, asin(15 / R) = 37.59 degrees); approved for upload
- upload attempt 1 of 5 for the quota day that began 2026-09-29T10:00
  EEST, recorded at 2026-09-29T11:17:15+03:00 before starting scripts/yt-upload.py; zero
  attempts were on record since the boundary
- uploaded private as MFVd3MiPsUI at 2026-09-29T11:17:25+03:00
  (https://youtu.be/MFVd3MiPsUI); channels.list 1 unit + videos.insert
  1,600 units; media/swerve/upload.log
- scripts/yt-qa.py swerve MFVd3MiPsUI --wait --publish in the foreground:
  gate 15 of 15 on the first read (processed, succeeded, hd, 1080x1920,
  title, description and tags match, category 27, not made for kids,
  PT39S for the 38.000 s file, private before publish); published at
  2026-09-29T11:18:06+03:00; re-read privacyStatus=public; yt-qa quota
  54 units; media/swerve/publish.log
- attempt 1 of 5 complete: 1,655 units; slot 1 of 3 resolved as
  published

### Quota
- attempt 1 of the hard cap of 5 for the quota day that began
  2026-09-29T10:00 EEST; cost 1,655 units (the channels.list verification
  inside yt-upload.py, the 1,600-unit insert, and the gate run's reads,
  update and re-read as printed by yt-qa.py); day total after three
  attempts 1,655 + 1,655 + 1,654 = 4,964 units plus 5 for the 10:01
  stats refresh and 5 for the 11:21 refresh, 4,974 of 10,000 used,
  5,026 remaining; target of three met
