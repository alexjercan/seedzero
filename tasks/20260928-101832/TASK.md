# Produce short: Head-on crash, two cars at 50 km/h beside one car into a wall at 50 and one at 100

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day30

## Goal

Backlog idea (trend research 2026-09-27, task 20260927-102520, pillar 2
chaos and physics, collisions; read the full entry under "Added by trend
research 2026-09-27" in docs/niche.md):
"Head-on crash: two 1,000 kg cars at 50 km/h head-on beside one car
into a wall at 50 and one at 100, the crumple a 1e6 N/m spring; measure
the crush of each car; expect 43.9 cm per car in the head-on, the
contact plane never moving, exactly the wall at 50 (43.9 cm, 44.8 g,
99 ms) and half the wall at 100 (87.8 cm); crush v sqrt(m / k); a
constant-force crumple gives 4x instead of 2x, so say "a car that
crumples like a spring"; the equality with the 50 wall holds for any
crumple law; repeat the crash; deterministic, no seed."

Orchestrator notes (2026-09-28, before this brief). The model: a car is
a rigid body of m = 1,000 kg with a crumple zone at its front that acts
as a linear spring of k = 1,000,000 N/m while it compresses, and locks
at maximum compression (a car does not spring back; the cars stay
stopped where they are). The maximum crush, the time to reach it and
the peak deceleration do not depend on the lock; print them. Lane 1,
head-on: two identical cars at 50 km/h = 13.889 m/s toward each other,
bumpers touching at t = 0. By symmetry the contact plane never moves,
so each car meets an immovable plane and crushes x = v sqrt(m / k) =
0.4392 m, reached at (pi / 2) sqrt(m / k) = 49.7 ms, peak deceleration
v sqrt(k / m) = 439.2 m/s^2 = 44.8 g; the spring stores 96.5 kJ, the
car's whole kinetic energy at 50 km/h. Lane 2, one car at 50 km/h into
a rigid wall: identical, 43.9 cm at 49.7 ms, 44.8 g. Lane 3, one car at
100 km/h = 27.778 m/s into the wall: 87.8 cm at 49.7 ms (the same
time), 878.4 m/s^2 = 89.5 g. The spring makes the crush proportional to
the speed, so the 100 wall is exactly 2.00 times the 50 wall; a crumple
zone that resists with a constant force would give crush proportional
to the speed squared, 4x, so the narration says "a car that crumples
like a spring" and the card and description state k. The equality
between the head-on at 50 + 50 and the wall at 50 holds for any crumple
law, by symmetry. Integrate lane 1 as a two-body system (the two
crumple springs in series between the bodies; each car's crush is its
own spring's compression) and lanes 2 and 3 as one body against a fixed
wall, RK4 at 100,000 steps a second or finer (the whole event is 100
ms), and check every number above against the closed forms. Print the
contact plane's largest displacement in lane 1 (expect 0.0000 mm), the
crush per car, the time to maximum crush, the peak deceleration in
m/s^2 and in g, the energy check, and the 2.00 ratio. For the
description also print the crush at 30 and 70 km/h (26.4 and 61.5 cm
expected) and the 4x that a constant-force crumple would give.

State every derived number above as a check the sim must print, not as
a fact.

Drawing: three lanes stacked, side view, the same clock, the same
horizontal scale. Lane 1: two cars closing on each other, a thin fixed
vertical line at the contact plane so the viewer sees it does not move.
Lane 2: one car into a thick wall block. Lane 3: one car into the same
wall, twice as fast. All three impacts start at the same instant: give
the 100 km/h car twice the run-up distance. Slow motion so the 100 ms
crush plays over about 2 s on screen (1/20 or 1/25 speed; say "slow
motion" and the factor on screen). Draw the crumple zone as a
distinctly coloured front section that shortens as it compresses, with
a live crush readout in cm under each car, a speed label on each car,
and the crushed cars held still after the lock. Hold with the readouts,
then a repeat cycle (fade and reset as tablecloth does, or a cycle
length that divides the scene); several cycles in about 40 s; the last
frame equals the first.

Day thirty, first slot. Chosen because "is a head-on at 50 like hitting
a wall at 100?" is a famous debate almost everyone answers wrong, three
lanes on the same clock answer it with one visible quantity (crush
depth), the closed form is exact, and no seed. Question in the first
two seconds: "Head-on at fifty. Is that a wall at one hundred?" (or the
producer's better wording; keep the words before the question under
nine; keep the question identical in the title, the hook and the
payoff). Setup number: fifty (kilometers an hour; say the unit once).
Payoff number: forty four centimeters of crush each, the same as the
wall at fifty; the wall at one hundred, eighty eight. The 44.8 g, the
49.7 ms, the 96.5 kJ and the 4x go to the card and the description.
Whisper risks: say "kilometers an hour" not "km/h"; do not say "g"
(the unit) in the narration; "head-on" is fine (the normalizer splits
it into two words); pre-test the hooks with scripts/voiceover.sh and
keep the one whose question lands earliest under two seconds. Make the
last frame equal the first. Measure every fixed text line with PIL
before rendering and keep every line under 950 px, and the title under
100 characters with no < or >. Music seed 92. Templates: sims/braking
(two cars in lanes, closed-form checks), sims/cradle (contact springs),
sims/tablecloth (slow motion, cycles, reset fade, two panels on one
clock). Sim name crash: sims/crash/crash.py, projects/crash/,
media/crash/.

## Claim

Two 1,000 kg cars that crumple like a spring (k = 1,000,000 N/m at the
front, locking at maximum compression) meet head-on at 50 + 50 km/h and
each crushes 43.92 cm in 49.67 ms at a peak of 44.79 g, with the contact
plane between them never moving (largest displacement 0.0000 mm): exactly
what one car crushes into a rigid wall at 50 km/h (43.92 cm, ratio
1.0000). One car into the same wall at 100 km/h crushes 87.84 cm, ratio
2.0000, in the same 49.67 ms at 89.57 g. The two cars of the head-on
together crush 87.84 cm, the wall-at-100 figure, shared by two crumple
zones. Narrated: fifty (setup, "kilometers an hour" once); forty four
centimeters each; the wall at fifty, forty four, the same; at one
hundred, eighty eight, twice as deep; the line between the two cars
never moves. Card: 43.9 cm each, the same as the wall at 50; a wall at
100, 87.8 cm, twice as deep; peak 44.8 g and 89.6 g, both in 49.7 ms.
Description: 96.45 / 192.90 / 385.80 kJ, the 0.0000 mm plane, 26.35 cm
at 30 km/h and 61.49 cm at 70, and the constant-force crumple's 4.0000
ratio (175.68 cm at 100 for the same 43.92 cm at 50).

## Evidence

### Measurements

`nix develop -c python3 sims/crash/crash.py projects/crash/manifest.json --measure-only`
at 10:39:46 EEST, media/crash/measure.log, copied whole:

```
setup: a car is a rigid body of 1000 kg with a 1 m crumple zone at its front that acts as a linear spring of k = 1e+06 N/m while it compresses and locks at maximum compression (no spring-back); lane 1: two identical cars at 50 km/h = 13.8889 m/s head-on, bumpers touching at t = 0, the two crumple springs in series between the two bodies with the massless contact plane where their forces balance; lane 2: one car at 50 km/h into a rigid wall; lane 3: one car at 100 km/h = 27.7778 m/s into the same wall; all three impacts at the same instant, integrated by RK4 at 100000 steps per second (dt = 1e-05 s) with the lock located by bisection inside the step; shown at 1/40 speed on a 14 s cycle (840 frames) with the impact 1.3 s into the cycle (32.5 ms of run-up, 0.451 m at 50 km/h and 0.903 m at 100), 3 cycles in 42 s; drawn at 100 px per metre, 3.8 m cars; deterministic, no seed
closed forms (x_max = v sqrt(m / k), t_max = (pi / 2) sqrt(m / k), a_peak = v sqrt(k / m), g = 9.80665): sqrt(m / k) = 0.031623 s, sqrt(k / m) = 31.6228 1/s; at 50 km/h x_max = 0.4392 m = 43.92 cm, t_max = 49.67 ms, a_peak = 439.2 m/s^2 = 44.79 g, kinetic energy m v^2 / 2 = 96.45 kJ = k x_max^2 / 2 = 96.45 kJ; at 100 km/h x_max = 0.8784 m = 87.84 cm, t_max = 49.67 ms (the same), a_peak = 878.4 m/s^2 = 89.57 g, energy 385.80 kJ = 385.80 kJ; the crush is proportional to the speed, ratio 2.0000
lane 1, head-on at 50 + 50 km/h (RK4, two bodies, 4968 steps): the crumple springs lock at t = 49.67 ms (closed form 49.67, diff 4.6e-12 ms) with car A crushed 43.92 cm and car B crushed 43.92 cm (closed form 43.92 cm each, diff 2.2e-14 cm), 87.84 cm of crush in all; the contact plane's largest displacement is 0.0000 mm (it never moves: each car meets an immovable plane); both cars stop: speeds at the lock -2.17e-19 and 2.17e-19 m/s; peak deceleration 439.2 m/s^2 = 44.79 g (car A) and 439.2 m/s^2 (car B); total momentum stays within 0.0e+00 kg m/s of zero; kinetic energy of both cars 192.90 kJ, stored in the two springs at the lock 192.90 kJ (diff 2.0e-10 J); RK4 stays within 8.6e-15 m of the closed form x = (v / omega) sin(omega t)
lane 2, one car at 50 km/h into the wall (RK4, 4968 steps): the crumple spring locks at t = 49.67 ms (closed form 49.67, diff 4.6e-12 ms) with the car crushed 43.92 cm (closed form 43.92, diff 2.2e-14 cm); the car stops: speed at the lock -2.17e-19 m/s; peak deceleration 439.2 m/s^2 = 44.79 g (closed form 439.2 m/s^2 = 44.79 g); kinetic energy 96.45 kJ, stored in the spring at the lock 96.45 kJ (diff 1.0e-10 J); RK4 stays within 8.6e-15 m of the closed form
lane 3, one car at 100 km/h into the wall (RK4, 4968 steps): the crumple spring locks at t = 49.67 ms (closed form 49.67, diff 4.6e-12 ms) with the car crushed 87.84 cm (closed form 87.84, diff 4.4e-14 cm); the car stops: speed at the lock -4.34e-19 m/s; peak deceleration 878.4 m/s^2 = 89.57 g (closed form 878.4 m/s^2 = 89.57 g); kinetic energy 385.80 kJ, stored in the spring at the lock 385.80 kJ (diff 4.1e-10 J); RK4 stays within 1.7e-14 m of the closed form
comparison: head-on at 50 + 50, 43.92 cm per car, against the wall at 50, 43.92 cm: diff 0.0e+00 cm, ratio 1.0000 (the same crash for each car); the wall at 100, 87.84 cm, against the wall at 50: ratio 2.0000 (twice the speed, twice the crush, in the same 49.7 ms); the head-on per car against the wall at 100: ratio 0.5000; the two cars of the head-on together crush 87.84 cm, the same as the one car into the wall at 100 (87.84 cm, ratio 1.0000): the closing speed of 100 km/h is shared by two crumple zones; peak deceleration 44.79 g in the head-on and the wall at 50, 89.57 g in the wall at 100
constant-force crumple, for comparison (not drawn): a crumple zone that resists with a constant force F gives crush m v^2 / (2 F), proportional to the speed squared; with F = 219.6 kN, chosen so that 50 km/h gives the same 43.92 cm (closed form 43.92), 100 km/h gives 175.68 cm (closed form 175.68), ratio 4.0000: 4 times, not 2, so the 2.00 depends on the spring law, in 63.2 and 126.5 ms at a constant 22.4 g; the head-on equality does not depend on the law: two identical cars with any crumple law meet at a plane where the two equal forces balance, so the plane is fixed by symmetry and each car crushes exactly as it would into a wall at its own speed
for the description (same cars, other speeds into the wall): 30 km/h: 26.35 cm (closed form 26.35) in 49.7 ms, peak 26.9 g; a head-on at 30 + 30 crushes each car the same 26.35 cm; 70 km/h: 61.49 cm (closed form 61.49) in 49.7 ms, peak 62.7 g; a head-on at 70 + 70 crushes each car the same 61.49 cm
schedule (video time, 1/40 speed): cycles of 14 s start at -14.00, 0.00, 14.00, 28.00 s (the first -0.00 s before the first frame); the bumpers touch 1.3 s into each cycle at 1.30, 15.30, 29.30 s; the crush grows for 1.99 s of video and all three lanes lock at 3.29, 17.29, 31.29 s (readouts 43.9, 43.9 and 43.9 cm in lane 1 and 2, 87.8 cm in lane 3, gold from the lock); the crushed cars hold until 13.40, 27.40, 41.40 s, then each cycle fades to the run-up of the next over 0.6 s (out over 13.40 to 13.70 s, in over 13.70 to 14.00 s after the cycle start); on the first frame the cycle is 0.00 s in (-32.5 ms real before impact): the cars are in their run-up; title until 3 s, then the legend and the clock; payoff card from 27 s; the title fades back in over the last 0.5 s and the last frame repeats the first (the scene is periodic: 42 s holds exactly 3 cycles)
text widths: overlay@34 817 px, title line 1@56 644 px, title line 2@56 716 px, legend@40 884 px, clock before@28 355 px, clock after@28 329 px, label headon@40 511 px, facts headon@28 330 px, label wall@40 301 px, facts wall@28 330 px, label wall2@40 329 px, facts wall2@28 330 px, speed@28 146 px, readout@40 316 px, plane@28 478 px, payoff line 1@40 855 px, payoff line 2@40 672 px, payoff line 3@40 833 px, payoff line 4@40 838 px, payoff line 5@40 899 px
row check: the lane label ends at x 601 px and the facts line starts at 660 px; the two head-on readouts are 144 px apart
```

Earlier measure runs (all the physics lines identical to the above; only
the schedule and text lines changed): 10:30:24, first run, every physics
check already at the values above (43.92 cm, 49.67 ms, 44.79 g, 0.0000
mm, ratios 1.0000 and 2.0000, RK4 within 8.6e-15 m), crashed on a
format bug in the schedule print; 10:30:5x, the width assert failed
(overlay 1186 px, payoff line 5 985 px), the overlay shortened to
"1,000 kg, k 1e6 N/m | 1/40 speed | no seed" and the card's last row to
"peak 44.8 g and 89.6 g, both in 49.7 ms"; 10:31, the row check failed
(the lane label "head-on, 50 km/h each" ended at 614 px, the facts line
"locked at 49.7 ms, peak 44.8 g" started at 496 px, and the two head-on
readouts were 20 px apart), fixed by "head-on, 50 + 50 km/h", "peak 44.8
g, 49.7 ms" and readout columns at x 310 / 770; 10:32, the row check
failed by 1 px (gap 39), the row margins moved to x 90 / 990; 10:35:40,
the title and card reworded to "same as a wall at 100?" (8 s cycles, 5
in 40 s, first_cycle_at -0.5); 10:38, the scene set to 42 s with three
14 s cycles from first_cycle_at 0.0; 10:39:46 (above), payoff_t 27.0.
Brief checks against the log: 43.9 cm per car in the head-on (43.92),
the contact plane never moving (0.0000 mm), the wall at 50 the same
(43.92, diff 0.0e+00 cm, ratio 1.0000), 44.8 g (44.79), 49.7 ms (49.67;
the niche entry's "99 ms" is the half period, the crush to the lock is a
quarter period), the wall at 100 87.8 cm (87.84, ratio 2.0000, the same
49.67 ms, 878.4 m/s^2 = 89.57 g), 96.5 kJ (96.45 kJ = k x_max^2 / 2), 30
and 70 km/h 26.4 and 61.5 cm (26.35, 61.49), the constant-force 4x
(4.0000), momentum 0.0e+00, RK4 within 8.6e-15 m of the closed form.
Every check passed; no claim was changed.

### Production

- Sim: sims/crash/crash.py with projects/crash/manifest.json (seed 0,
  fps 60, g 9.80665, car_mass_kg 1000, crumple_k_n_m 1e6, speed_km_h 50,
  fast_speed_km_h 100, description_speeds_km_h [30, 70],
  steps_per_second 100000, car_length_m 3.8, crumple_zone_m 1.0, slow
  40, cycle_s 14.0, impact_at 1.3, first_cycle_at 0.0, reset_fade 0.6,
  scene_duration 42.0, px_per_m 100, plane_x_px 540, lane_y [340, 700,
  1060, 1420], title_until 3.0, payoff_t 27.0, payoff_hold 0.6,
  loop_fade 0.5, music_seed 92, music_gain 0.18, voice_offset 0.6,
  caption_y 0.75). Lane 1 is a two-body RK4 system (xA, vA, xB, vB) with
  the two crumple springs in series and the massless plane at the force
  balance (cA = cB = s / 2 for identical linear springs, plane = xA -
  cA); lanes 2 and 3 are one body against a fixed wall; the lock (closing
  rate zero) is bisected inside the step (60 halvings) and the state is
  held after it. The renderer interpolates the sampled crush and body
  displacement at real time (tau - impact_at) / slow; before impact the
  cars glide at their speed. The cycle phase comes from the frame integer
  modulo 840 frames, so the scene is exactly periodic; the last frame is
  the live frame 0.
- Layout (1080x1920): overlay at y 96 (34 px teal, drawn by compose);
  title two rows at y 190 / 252 (56 px) until 3 s, then the legend "same
  cars, one clock, slow motion 1/40" at y 236 (40 px) and the clock
  "12.5 ms after impact" at y 290 (28 px); three lanes 340..700,
  700..1060, 1060..1420, each drawn at 2x: lane label at +36 (40 px, x
  90) with the gold facts line "peak 44.8 g, 49.7 ms" right-aligned at x
  990 after the lock; speed labels at +92 (28 px) over each rigid body;
  ground at +250; 3.8 m cars 1.35 m tall (blue body, light cabin, coral
  1.0 m crumple zone with four creases that bunch as it shortens, dark
  bumper, headlight) with the contact plane / wall face at x 540 in
  every lane; a 2 px white plane line in lane 1, a 60 px hatched wall
  block in lanes 2 and 3; readouts "crush 43.9 cm" at +300 (40 px,
  gold from the lock) at x 310 / 770 (lane 1) and 372 (lanes 2, 3);
  "contact plane moved 0.00 mm" at +340 (28 px teal) in lane 1; captions
  at y 1440 (64 px); the five-row gold card from y 1580 at a 52 px pitch
  (last row centre 1788).
- Hook pre-tests (media/crash/hooks/pretest.log, 10:32:11 to 10:35:13
  EEST), each through scripts/voiceover.sh; question onset = first
  silence_end (n=-35dB d=0.08) plus 0.6 s: hook1 "Head-on at fifty. Is
  that a wall at one hundred? Three crashes, one clock." failed (whisper
  added an "o" token); hook2 "Head-on at fifty: is that a wall at one
  hundred? Three crashes, one clock." ok, 2.00 s; hook3 "Head-on at
  fifty, is that ..." failed ("one hundred? Three" folds to 103 in
  normalize.py on the narration side, whisper gave "100 3"); hook4 "Is a
  head-on at fifty like a wall at one hundred? Three crashes ..." failed
  (the same 103 fold); hook5 "Two cars, head-on at fifty. Is that ..."
  ok but the question starts after the second pause, 2.56 s; hook6
  "Head-on at fifty. Is that like a wall at one hundred? ..." ok, 1.86 s;
  hook7 (period form, "Same cars, one clock, slow motion.") failed
  ("Head" heard as "hit", "same" as "sane", an extra "o"); hook8 (colon
  form, same follow-up) ok, 1.85 s; hook9 (period form with "like")
  failed (extra "o" before "slow"); hook10 "Head-on at fifty: same as a
  wall at one hundred? The same cars, the same clock, slow motion." ok,
  1.77 s. Kept hook10's question ("same as" keeps "wall at one hundred?"
  inside one 20-character caption chunk, which "is that a wall at one
  hundred?" cannot). Lessons: never put a number word right after "one
  hundred" (the normalizer folds "hundred eighty eight" to 188 and
  "hundred three" to 103), and "one clock, slow motion" drew a spurious
  token three times.
- Narration: projects/crash/narration.txt, 116 words, the question at
  words 1 to 10 (nothing before it), identical in the title, the hook and
  the payoff; numbers as words; "kilometers an hour" once; no "g"; no
  number word after "one hundred" ("At one hundred, it is eighty eight");
  American "centimeters", "kilometers".
- Voice (media/crash/voice.log): pass 1 at 10:35:40 (122 words, "The
  same cars, the same clock, slow motion." and "In the head-on, the line
  between them never moves.") passed at 37.013 s, but the number block
  would have run to 28.0 s and the payoff to 37.6 s, past the holds any
  cycle length could give; the intro was trimmed. Pass 2 at 10:38:29 (116
  words): "ok: transcript matches narration (35.108571s) ->
  media/crash/voice.wav". The voice ends at 35.71 s of video.
- Timing (scripts/voice-timing.py media/crash/voice.wav 0.6, in
  media/crash/timing.log): 0.60 to 1.68 "Head-on at fifty:"; 1.68 to
  5.10 "same as a wall at one hundred? In slow motion. On top,"; 5.10 to
  8.08 "two cars at fifty kilometers an hour, head-on."; 8.08 to 10.64
  "In the middle, one car into a wall at fifty."; 10.64 to 13.09 "At the
  bottom, the same wall at one hundred."; 13.09 to 21.20 "Each car
  crumples like a spring. Watch the red zones shorten. The line between
  the two cars never moves. Each car crushes forty four centimeters.";
  21.20 to 22.31 "The wall at fifty,"; 22.31 to 23.23 "forty four.";
  23.23 to 24.00 "The same."; 24.00 to 28.09 "At one hundred, it is
  eighty eight. Twice as deep. So, head-on at fifty:"; 28.09 to 33.68
  "same as a wall at one hundred? No. It is a wall at fifty. Forty four
  centimeters of crush each."; 33.68 to 35.71 "At one hundred, it is
  eighty eight." Question onset on the full take: first silence_end
  1.203 s in the wav plus 0.6 = 1.80 s (media/crash/silences.log).
- Schedule: three 14 s cycles from 0.0 s; the bumpers touch at 1.30,
  15.30, 29.30 s; the crush grows for 1.99 s and locks at 3.29, 17.29,
  31.29 s (readouts 43.9 / 43.9 / 87.8 cm gold from the lock); the
  crushed cars hold to 13.40, 27.40, 41.40 s, then fade out over 0.3 s
  and the next run-up fades in over 0.3 s. The question (0.6 to about
  3.5 s) plays over the first run-up and crush; the lane naming (5.1 to
  13.1) over the first hold; "Each car crumples like a spring" (13.1 to
  14.9) over the fade and the fresh run-up; "Watch the red zones shorten"
  (about 14.9 to 16.4) inside the second crush 15.30 to 17.29; "The line
  between the two cars never moves", "forty four", "The wall at fifty,
  forty four. The same.", "At one hundred, it is eighty eight." and
  "Twice as deep." (16.4 to 26.9) inside the second hold with the
  readouts locked; "So, head-on at fifty: same as a wall at one hundred?"
  (26.9 to 30.2) over the third fade, run-up and crush, the card lit
  from 27.0 (full at 27.6); "No. It is a wall at fifty. Forty four
  centimeters of crush each. At one hundred, it is eighty eight." (30.2
  to 35.71) with the third lock at 31.29 and the readouts held to 41.4.
- Smoke frames (--frames, 10:39:5x): 14 PNGs at 0.0, 1.8, 2.3, 3.29,
  13.55, 15.9, 17.29, 20.0, 25.0, 27.8, 30.5, 34.5, 41.6, 41.98 s (an
  earlier set of 12 at the 8 s cycle, 10:32, and one at 10:35 checked
  the layout); viewed 0.0, 1.8, 2.79 (old cycle), 27.6, 13.55, 15.9,
  27.8: the caption band (y 1440 to 1530) and overlay band (y 96 to 130)
  empty, no text row touching another (title rows end at 280, the lane
  label row at 376 / 736 / 1096, the speed labels at 432 / 792 / 1152
  over roofs at 455 / 815 / 1175, readouts at 640 / 1000 / 1360, the
  plane line at 680, the card 1580 to 1808).
- Footage: render 10:39:46 to 10:40:23 (media/crash/render.log): loop
  check 0 px, periodicity check 0 px, loop step 27,083 px;
  media/crash/footage.mp4 3,231,399 B, 2520 frames.
- Compose: scripts/compose.sh 10:40:33 to 10:40:46 (compose.log): music
  seed 92, 42.00 s; captions 40 chunks; final.mp4 42.000000 s; preview
  42.066667 s; sheet 8x6 at 1 fps.
- Text widths (PIL, from measure.log, all under 950 px): overlay 817,
  title 644 / 716, legend 884, clock 355 / 329, lane labels 511 / 301 /
  329, facts 330, speed 146, readout 316, plane 478, payoff 855 / 672 /
  833 / 838 / 899; row check: label ends at 601, facts start at 660, the
  head-on readouts 144 px apart.

### Local QA

- Frames extracted from media/crash/final.mp4 (never edited) and viewed
  with the Read tool:
  - frame-0.02.png: overlay, two title rows ("Head-on at 50 km/h:" /
    "same as a wall at 100?"), three lanes with the cars in their run-up
    (readouts 0.0 cm, plane 0.00 mm), no caption, no card. Clean; works
    as the thumbnail.
  - frame-1.8.png: title still up, caption "same as a wall at" at y
    1440, the cars 16.9 / 16.9 / 33.8 cm into the crush, zones shortened.
    The question is being spoken while the crash runs.
  - frame-3.29.png: the lock: 43.9 / 43.9 / 87.8 cm gold, the facts
    lines lit, the legend and the clock "50.0 ms after impact", caption
    "one hundred?".
  - frame-15.9.png: second crush at 20.1 / 20.1 / 40.1 cm, white
    readouts, caption "Watch the red zones". The zones shorten on the
    words.
  - frame-20.0.png: hold, 43.9 gold, caption "forty four".
  - frame-25.0.png: hold, 87.8 gold, caption "is eighty eight.".
  - frame-27.8.png: the third run-up fading in (cars at a third alpha,
    "37.5 ms before impact"), card fully lit, caption "fifty: same as a".
    The card is on screen inside the spoken question.
  - frame-32.5.png: third hold, 43.9 gold, caption "centimeters of
    crush", card lit.
  - frame-34.5.png: third hold, 87.8 gold, caption "At one hundred, it",
    card lit. The payoff numbers are on screen (readouts and card) when
    spoken.
  - frame-41.98.png: title back, legend, clock, facts and card gone, the
    cars in their run-up: the same picture as frame-0.02.
  - sheet.png (42 thumbnails at 1 fps): the title for the first 3 s, then
    the legend and clock; three crashes at 1 to 3, 15 to 17 and 29 to 31
    s with the readouts resetting at 14 and 28 s; captions readable in
    every thumbnail from 1 to 35 s; the card from 28 s; no clipped text,
    nothing at the frame edge.
- Question: on screen from frame 0 in the title (two rows, 644 / 716
  px), spoken from 1.80 s ("Head-on at fifty:" caption 0.600 to 1.508,
  "same as a wall at" 1.508 to 3.021, "one hundred?" 3.021 to 3.627).
- Captions: media/crash/captions.filter, 40 chunks, 116 words, matches
  projects/crash/narration.txt word for word (script check True),
  longest chunk 20 characters; "forty four" 19.970 to 20.576, "forty
  four." 22.089 to 22.694, "The same." 22.694 to 23.300, "is eighty
  eight." 24.510 to 25.418, "wall at one hundred?" 28.445 to 29.655,
  "No." 29.655 to 29.958, "is eighty eight." 34.801 to 35.709.
- Bands: signalstats over all 2,520 footage frames: the caption band
  (rows 1420 to 1530) and the overlay band (rows 96 to 130) have YMAX 28
  in every frame (background only), so the sim draws nothing under the
  captions or the overlay.
- Loop: footage last frame equals the first (0 px), periodicity 0 px. In
  final.mp4 frame 2519 against frame 0: 63,538 px over 8 levels, 1,735
  over 32, max 71, mean 0.63 (h264 quantisation, the same order as day
  29's 36,883 / 1,153 / 96); loop step 34,972 px, so the seam is no
  larger than one frame of motion.
- ffprobe: h264 1080x1920 yuv420p 60/1, 2520 frames; aac 22050 Hz mono;
  42.000000 s; 3,762,480 bytes; moov before mdat.
- md5sum media/crash/final.mp4: d4823581a05d1d6044fe6b289aed7ce3
- Narrated numbers against measure.log: "fifty" and "one hundred" (50
  and 100 km/h, 13.8889 and 27.7778 m/s); "forty four centimeters" per
  car in the head-on (43.92 cm); "The wall at fifty, forty four. The
  same." (43.92 cm, diff 0.0e+00, ratio 1.0000); "At one hundred, it is
  eighty eight. Twice as deep." (87.84 cm, ratio 2.0000); "The line
  between the two cars never moves." (plane displacement 0.0000 mm);
  "Each car crumples like a spring." (k = 1e6 N/m linear). Card 43.9 /
  87.8 cm, 44.8 g / 89.6 g (44.79 / 89.57), 49.7 ms (49.67). Title 44
  cm / 88 cm / 50 / 100.
- Metadata check: every number in the description read against the
  10:39:46 measure.log (13.8889, 27.7778 m/s; 49.67 ms; 43.92, 87.84 cm;
  0.0000 mm; 439.2 and 878.4 m/s^2; 44.79 and 89.57 g; 96.45, 192.90,
  385.80 kJ; ratios 1.0000, 2.0000, 4.0000; 26.35 cm 26.9 g, 61.49 cm
  62.7 g; 219.6 kN, 175.68 cm, 63.2 and 126.5 ms, 22.4 g; 8.6e-15 and
  1.7e-14 m; 4.6e-12 ms; 0.0e+00 kg m/s).

### Metadata

projects/crash/metadata.json: title "Head-on at 50: same as a wall at
100? No. 44 cm of crush each, like a wall at 50. At 100: 88 cm" (95
characters); description 3,352 characters with the model, the
"Measured:" list, the "Why:" paragraph (mirror symmetry fixes the plane,
the closing speed's 87.84 cm is shared by two crumple zones, the spring
makes crush proportional to speed, a constant force would give 4x), the
rerun line and the AI-made line; 11 tags; categoryId 27; privacyStatus
private; containsSyntheticMedia true; selfDeclaredMadeForKids false; no
angle brackets.

### Deviations from the brief

- Question "Head-on at fifty: same as a wall at one hundred?" instead of
  "Head-on at fifty. Is that a wall at one hundred?": the period form
  clipped "Head" to "hit" in one pre-test, and "is that a wall at one
  hundred?" splits "one" / "hundred?" across two 20-character caption
  chunks, while "same as a wall at" / "one hundred?" does not. The title,
  hook, card and payoff all carry the same question.
- Slow motion 1/40, not 1/20 or 1/25: the crush to the lock is a quarter
  period, 49.67 ms (the niche entry's 99 ms is the half period), so 1/40
  is what plays it over about 2 s (1.99 s) as the brief intended. The
  factor is on the legend and the overlay.
- Scene 42 s with three 14 s cycles, not about 40 s with more cycles:
  the narration needs the locked readouts on screen from 16.4 to 26.9 s
  and again from 31.3 to 35.7 s, which only a 14 s cycle with a 10.1 s
  hold gives while keeping frame 0 in a run-up (day 27 tablecloth also
  ran 42 s).
- The readouts show 43.9 / 43.9 / 87.8 from the first lock at 3.29 s,
  during the lane naming, and are not hidden as day 29's counters were:
  the brief asks for live readouts under each car from the start, and
  the crush depth is the visible quantity anyway.
- The narration says "In slow motion." rather than the brief's "say slow
  motion and the factor on screen" only; the factor 1/40 is on screen
  (legend and overlay), not spoken.
- The 44.8 g, 49.7 ms and 96.5 kJ went to the card (44.8 g, 89.6 g, 49.7
  ms) and the description (kJ), as the brief asked; the description also
  carries the 4x constant-force comparison and 30 / 70 km/h.
- The niche entry's "99 ms" was not reproduced: the sim measures the
  time to maximum crush, 49.67 ms = (pi / 2) sqrt(m / k), as the
  orchestrator notes expected.

## Niche note

[produced 2026-09-28 as "Head-on at 50: same as a wall at 100? No. 44 cm
of crush each, like a wall at 50. At 100: 88 cm"; measured two 1,000 kg
cars with a 1e6 N/m spring crumple head-on at 50 + 50 km/h crushing
43.92 cm each in 49.67 ms at 44.79 g with the contact plane displaced
0.0000 mm, exactly one car into a wall at 50 (43.92 cm, ratio 1.0000);
one car into the wall at 100, 87.84 cm, ratio 2.0000, the same 49.67 ms,
89.57 g; the head-on's two cars together crush 87.84 cm, the wall-at-100
figure; a constant-force crumple would give 4.0000 (175.68 cm); 26.35 cm
at 30 km/h, 61.49 at 70; RK4 within 8.6e-15 m of the closed forms; task
20260928-101832]

## Upload

- orchestrator review (2026-09-28T11:15:56+03:00): task evidence, sheet.png and frames at 0.02,
  1.8, 3.29, 32.5, 34.5 and 41.98 s inspected; numbers match measure.log and
  the closed forms x = v sqrt(m / k) in /tmp/day30/check.py; approved for upload
- upload attempt 1 of 5 for the quota day that began 2026-09-28T10:00
  EEST, recorded at 2026-09-28T11:15:56+03:00 before starting scripts/yt-upload.py; zero
  attempts were on record since the boundary
- uploaded private as Hxfc-VeBVko at 2026-09-28T11:16:04+03:00
  (https://youtu.be/Hxfc-VeBVko); channels.list 1 unit + videos.insert
  1,600 units; media/crash/upload.log
- scripts/yt-qa.py crash Hxfc-VeBVko --wait --publish in the foreground:
  gate 15 of 15 (processed, succeeded, hd, 1080x1920, title, description
  and tags match, category 27, not made for kids, PT43S, private before
  publish); published at 2026-09-28T11:16:40+03:00; re-read
  privacyStatus=public; yt-qa quota 54 units; media/crash/publish.log
- attempt 1 of 5 complete at 2026-09-28T11:26:34+03:00: 1,655 units; slot 1 of 3 resolved as
  published

### Quota
- attempt 1 of the hard cap of 5 for the quota day that began
  2026-09-28T10:00 EEST; cost 1 + 1,600 + 54 = 1,655 units (the
  channels.list verification inside yt-upload.py, the insert, the gate run's
  single read, update and re-read as printed by yt-qa.py); day total after
  three attempts 1,655 + 1,656 + 1,655 = 4,966 units plus 5 for the 10:05
  stats refresh and 5 for the 11:35 refresh, target of three met

### Repository
- committed as 3a82f2e "Publish the day thirty slate" (sims, projects,
  tasks, docs/niche.md, web/data; no media, previews or secrets) and pushed
  to origin/master at 2026-09-28 11:36 EEST on top of 76e0f46
