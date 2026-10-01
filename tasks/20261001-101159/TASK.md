# Produce short: Car over a hump, 40 km/h beside 60 km/h on the same humpback bridge

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day33

## Goal

Backlog idea (trend research 2026-09-29, task 20260929-100144, pillar 2
chaos and physics, everyday mechanics; read the full entry under "Added
by trend research 2026-09-29" in docs/niche.md): "Car over a hump: the
same car at a steady 40 and 60 km/h over a cosine hump 1.5 m high and 24
m long (crest radius 19.45 m); measure whether the wheels leave the road;
expect the threshold sqrt(g R) = 49.7 km/h, 40 km/h holding with 0.35 of
the weight on the road, 60 km/h leaving 3.0 m before the top and flying
12.8 m in 0.77 s, at most 32 cm above the road (55 km/h: 9.4 m, 10 cm);
point car, no suspension; draw the gap clearly or use a sharper hump;
repeat; deterministic, no seed."

Orchestrator notes (2026-10-01, before this brief). Use a bigger hump
with the same limit so the gap is visible: a humpback bridge H = 2.5 m
high and L = 31 m long, y(x) = (H / 2)(1 + cos(2 pi x / L)) for |x| <= L
/ 2 and flat road elsewhere (the hump joins the road with zero slope);
crest radius R = L^2 / (2 pi^2 H) = 19.47 m; steepest slope atan(pi H /
L) = 14.2 degrees. The car is a point moving along the road at a steady
speed v while its wheels touch (the engine holds the speed; a real car's
suspension changes the gap, not the limit; no suspension, say so); on the
road the push of the road per unit mass is N = g cos(theta) - v^2 kappa
with theta the road slope and kappa the road's convex curvature (y'' /
(1 + y'^2)^1.5 with its sign: convex over the crest); the wheels leave
where N reaches zero; from there the point flies on a parabola from the
tangent velocity and lands where the parabola meets the road again (find
the root by bisection); the landing takes the vertical speed and the car
continues along the road at its steady speed. At the crest N = g - v^2 /
R, so the limit is v* = sqrt(g R) = 13.82 m/s = 49.7 km/h, independent of
the car's mass. Checks, not facts (orchestrator stepped march at 1e-4 s,
/tmp/day33): at 40 km/h (11.11 m/s) N never drops below 0.354 of the
weight (at the crest) and the wheels stay down; at 60 km/h (16.67 m/s)
the wheels leave 3.86 m before the crest, the car flies 16.21 m in 0.988
s, at most 0.506 m above the road (measured straight up at the car's x),
and lands 12.35 m past the crest with 6.76 m/s of downward speed; at 50
km/h N dips to -0.01 g 0.66 m before the crest (2.6 m of weightless
rolling, gap under 1 mm: right on the limit); for the description: 55
km/h (leave point, flight length, gap) and 70 km/h, and the 1.5 m / 24 m
hump of the brief (limit 49.7 km/h, 60 km/h flies 12.8 m with a 32 cm
gap); check the leave point against the closed form N = 0 solved by
bisection on x, the flight against the parabola at half the step, and
print the times in real seconds and in video seconds. State every
derived number above as a check the sim must print, not as a fact.

Drawing: two stacked bands, the 40 km/h car on top and the 60 km/h car
below; side view; the camera follows each car horizontally (the car's
point at a fixed x near 480 px) and is fixed vertically, so the hump
scrolls under the car and the car rises over the crest; 80 px per metre
(the hump 200 px high, flat road 470 px under the band top, the car
about 4.0 x 1.3 m as a simple body with two wheels, drawn tangent to the
road at its point while the wheels touch and holding its last angle
while in the air); the road as a filled dark slab with a lighter surface
line, lane dashes that scroll at the car's speed (smeared over one
frame's travel so they never strobe), a crest marker; when the wheels
are off the road: a dashed vertical gap line from the wheels to the road
with a gold live readout "wheels NN cm off the road" and a shadow on the
road under the car; a small minimap strip at the top of each band (the
whole hump, 300 px wide, with a dot for the car) so the viewer knows
where the car is; left column: the label "40 km/h" / "60 km/h" and
"road push: 0.NN of the car's weight" live (gold at its minimum); right
column: "x NN m from the crest"; a gold event row "wheels stay on the
road" (top, lit as the car passes the crest) and "in the air 16 m, 0.99
s" (bottom, lit at the landing). Shown at 1/3 speed; cycle 10 s (600
frames) with each car starting 19.5 m before the crest (4 m before the
hump) at the cycle start, so in 3.33 real seconds the 40 km/h car ends
2 m past the hump and the 60 km/h car 20 m past it; the 60 km/h car
leaves the road at 2.81 s and lands at 5.78 s of each cycle; a reset
crossfade at the end of the cycle, 4 cycles in 40 s, the last frame
equal to the first. Check that the car body never enters the readout
rows at the crest or in the air (assert the roof's highest y) and that
nothing is drawn under the captions.

Day thirty-three, third slot. Chosen because "does the car take off
over the hump" is a famous road debate, the panels end visibly
differently (one car hugs the road, the other hangs in the air with a
half-metre of daylight), and the limit is one clean number. Question in
the first two seconds: "Does the car leave the road?" (or "A hump in the
road. Does the car leave the road?"; keep the question identical in the
title, the hook and the payoff). Setup number: the same hump at forty
and sixty kilometers an hour. Payoff number: at forty, no; at sixty,
yes: sixteen meters through the air; the limit is fifty. The gap, the
flight time, the 50 and 55 km/h cases and the crest radius go to the
card and the description. Whisper risks: never say "fly" or "flies"
(whisper wrote "5" on 2026-09-26: say "leaves the road", "in the air");
"hump" (pre-test; "bump" is worse), "wheels", "crest", "forty" and
"sixty" as words, "kilometers an hour" (passed before); avoid "do you";
avoid "pull" as a noun. Pre-test hooks with scripts/voiceover.sh and
keep the one whose question lands earliest under two seconds. Measure
every fixed text line with PIL before rendering and keep every line
under 950 px, and the title under 100 characters with no < or >. Music
seed 103. Templates: sims/belt (two bands, layout asserts, the scrolling
belt texture), sims/braking or sims/swerve (a drawn car and road marks),
sims/balloon (lane dashes smeared over a frame's travel). Sim name hump:
sims/hump/hump.py, projects/hump/, media/hump/.

## Claim (expected; the sim's numbers replace these)

Over a 2.5 m high, 31 m long humpback bridge (crest radius 19.47 m) a
car at a steady 40 km/h keeps its wheels on the road (the road still
pushes with 0.354 of the car's weight at the crest) and a car at 60 km/h
leaves the road 3.86 m before the crest, is in the air for 16.21 m and
0.988 s, at most 0.51 m above the road, and lands 12.35 m past the
crest. The limit is sqrt(g R) = 49.7 km/h, whatever the car weighs.
Narrated: the same hump at forty and sixty kilometers an hour (setup);
at forty, no; at sixty, yes, sixteen meters through the air; the limit
is fifty (payoff). Card: the question; 40: wheels down, 60: 16 m in the
air; the limit sqrt(g R) = 49.7 km/h, R 19.5 m; 60 km/h: off 3.9 m before
the top, 0.99 s, 51 cm up; 50 km/h: just on the limit; 55 km/h: NN m.
Description: the model statement, the 1.5 m hump of the research entry,
70 km/h, the checks.

## Claim

Over a humpback bridge 2.5 m high and 31 m long (cosine hump, crest
radius 19.4739 m) a car at a steady 40 km/h keeps its wheels on the road:
the road push bottoms at 0.3535 of the car's weight at the crest. The
same car at 60 km/h leaves the road 3.859 m before the crest, is in the
air for 16.206 m and 0.9877 s, at most 0.5060 m (50.6 cm) above the
road, and lands 12.347 m past the crest with 6.757 m/s of downward
speed. The limit between them is sqrt(g R) = 13.8193 m/s = 49.75 km/h,
whatever the car weighs. Narrated: the same hump at forty and sixty
kilometers an hour (setup); at forty, no; at sixty, yes: sixteen meters
through the air; the limit is fifty kilometers an hour (payoff). Card:
16.2 m in the air; limit sqrt(g R) = 49.7 km/h, R = 19.5 m; 60: off 3.9
m before the top, up to 51 cm, in the air 0.99 s; 55 km/h: 11.8 m, 16
cm; 50: on the limit; any car weight. Description: the model, 50, 55 and
70 km/h, the 1.5 m / 24 m hump of the research entry, the checks.

## Evidence

### Measurements

Final `media/hump/measure.log` (sims/hump/hump.py --measure-only with
projects/hump/manifest.json, first_cycle_at -6.1):

```
Thu Oct  1 10:40:03 AM EEST 2026
warning: Git tree '/home/alex/personal/seedzero' is dirty
setup: the same humpback bridge in both panels, a cosine hump H = 2.5 m high and L = 31 m long on a flat road, y(x) = (H / 2)(1 + cos(2 pi x / L)) for |x| <= L / 2 (it joins the road with zero slope); crest radius R = L^2 / (2 pi^2 H) = 19.4739 m, steepest slope atan(pi H / L) = 14.22 degrees; the car is a point moving along the road at a steady speed (the engine holds the speed; no suspension), g = 9.80665 m/s^2; on the road the push per unit mass is N = g cos(theta) - v^2 kappa, the wheels leave where N reaches zero, fly on the parabola from the tangent velocity and land where it meets the road (bisection); the landing takes the vertical speed; at the crest N = g - v^2 / R, so the limit is v* = sqrt(g R) = 13.8193 m/s = 49.75 km/h (about 50 km/h), whatever the car weighs; top panel 40 km/h, bottom panel 60 km/h; stepped at dt = 1e-04 s (RK4 along the road, the leave point by bisection inside the step, the closed-form parabola in the air, the landing by bisection), checked against N = 0 solved by bisection on x and a half-step rerun; shown at 1/3 speed on a 10 s cycle (600 frames = 3.3333 s of real time) with both cars starting at x = -19.5 m (4 m before the hump) at the cycle start, 4 cycles in 40 s; drawn at 80 px per metre; deterministic, no seed
slow panel, 40 km/h (11.1111 m/s): the wheels never leave; the road push bottoms at 0.3535 of the weight at x = -0.000 m (closed form at the crest 1 - v^2 / (g R) = 0.3535); passes the crest at 1.7771 s; 0 flight(s) in the 3.3333 s run; ends at x = +17.046 m (1.55 m past the hump); 33334 steps
fast panel, 60 km/h (16.6667 m/s): the wheels leave 3.859 m before the crest (x = -3.8588 m, slope 10.12 deg, 0.9519 s after the start), the car is in the air for 16.206 m and 0.9877 s, at most 0.5060 m (50.6 cm) above the road at x = +7.989 m, 0.0546 m above the crest as it passes it, and lands 12.347 m past the crest at 1.9396 s with 6.757 m/s of downward speed (4.230 m/s into the road); passes the crest at 1.1871 s; 1 flight(s) in the 3.3333 s run; ends at x = +35.563 m (20.06 m past the hump); 33332 steps
the two panels: at 40 km/h the wheels stay on the road, the push never under 0.3535 of the weight (at the crest); at 60 km/h the wheels leave 3.86 m before the crest and the car is in the air for 16.21 m (16 m) and 0.99 s, at most 51 cm above the road; the limit between them is 49.7 km/h (50 km/h); the parabola's apex is 2.5744 m, +0.0744 m against the crest
check, leave point: N = 0 solved by bisection on x gives x = -3.858788 m; the march left at -3.858788 m (diff +0.0e+00 m); N just before the leave +2.1e-07 g, just after -2.1e-07 g
check at half the time step (5e-05 s), 60 km/h: leaves at x = -3.858788 m (+0.0e+00), 0.951888 s (+2.1e-14); in the air 16.206131 m (+0.0e+00) and 0.987747 s (+0.0e+00); gap 0.506030 m (-4.4e-16); lands at x = +12.347343 m (+0.0e+00) with 6.756848 m/s down (+0.0e+00); the flight is the closed-form parabola x = x0 + vx t, y = y0 + vy t - g t^2 / 2 from vx = 16.4072, vy = 2.9296 m/s, so halving the step only moves the landing root
check at half the time step, 40 km/h: no flight, push bottoms at 0.353541 of the weight (+9.1e-17) at x = -0.0003 m; crest at 1.777123 s (+2.7e-12)
for the description, the same hump: 50 km/h (13.8889 m/s): the wheels leave 0.658 m before the crest (x = -0.6576 m, slope 1.93 deg, 1.3743 s after the start), the car is in the air for 2.633 m and 0.1897 s, at most 0.0004 m (0.0 cm) above the road at x = +1.316 m, 0.0000 m above the crest as it passes it, and lands 1.976 m past the crest at 1.5641 s with 1.393 m/s of downward speed (0.022 m/s into the road); N at the crest -0.0101 g; 55 km/h (15.2778 m/s): the wheels leave 2.882 m before the crest (x = -2.8822 m, slope 7.95 deg, 1.1032 s after the start), the car is in the air for 11.820 m and 0.7812 s, at most 0.1602 m (16.0 cm) above the road at x = +5.870 m, 0.0175 m above the crest as it passes it, and lands 8.938 m past the crest at 1.8844 s with 5.547 m/s of downward speed (1.771 m/s into the road); N at the crest -0.2222 g; 70 km/h (19.4444 m/s): the wheels leave 5.003 m before the crest (x = -5.0028 m, slope 12.14 deg, 0.7559 s after the start), the car is in the air for 22.195 m and 1.1676 s, at most 1.3959 m (139.6 cm) above the road at x = +10.670 m, 0.1470 m above the crest as it passes it, and lands 17.193 m past the crest at 1.9235 s with 7.361 m/s of downward speed (7.361 m/s into the road); N at the crest -0.9798 g
for the description, the research entry's hump 1.5 m high and 24 m long: crest radius 19.4537 m, limit sqrt(g R) = 13.8121 m/s = 49.72 km/h; 60 km/h (16.6667 m/s): the wheels leave 3.037 m before the crest (x = -3.0367 m, slope 7.98 deg, 0.9940 s after the start), the car is in the air for 12.779 m and 0.7742 s, at most 0.3237 m (32.4 cm) above the road at x = +6.295 m, 0.0349 m above the crest as it passes it, and lands 9.742 m past the crest at 1.7683 s with 5.279 m/s of downward speed (3.452 m/s into the road)
schedule (video time at 1/3 speed): cycles of 10 s start at -6.10, 3.90, 13.90, 23.90, 33.90 s (the first 6.10 s before the first frame); both cars start at x = -19.5 m at each cycle start; the 60 km/h car leaves the road 2.86 s into the cycle (0.9519 s real) at 6.76, 16.76, 26.76, 36.76 s, passes the crest 3.56 s in at 7.46, 17.46, 27.46, 37.46 s and lands 5.82 s in (1.9396 s real) at 9.72, 19.72, 29.72, 39.72 s, 2.96 s of video in the air; the 40 km/h car passes the crest 5.33 s in (1.7771 s real) at 9.23, 19.23, 29.23, 39.23 s; at the cycle end the 40 km/h car is at x = +17.05 m and the 60 km/h car at x = +35.56 m; the reset crossfade runs over the last 0.4 s of each cycle (the readouts out from 3.50, 13.50, 23.50, 33.50 s, the fresh cars in from 3.70, 13.70, 23.70, 33.70 s); on the first frame the cycle is 6.10 s in (2.0333 s real: the 40 km/h car at x = +2.84 m, road, push 0.463; the 60 km/h car at x = +13.90 m, road, gap 0.0 cm); title until 3 s; payoff card from 26.2 s; the title fades back in over the last 0.5 s and the last frame repeats the first (the scene is periodic: 40 s holds exactly 4 cycles)
text widths: overlay@34 886 px, title line 1@56 908 px, title line 2@56 894 px, legend@40 887 px, clock@28 575 px, label slow@40 181 px, push slow@28 542 px, push air slow@28 421 px, where slow before@28 372 px, where slow past@28 338 px, event slow@28 379 px, label fast@40 181 px, push fast@28 542 px, push air fast@28 421 px, where fast before@28 372 px, where fast past@28 338 px, event fast@28 377 px, gap@28 410 px, crest@24 68 px, payoff line 1@40 644 px, payoff line 2@40 825 px, payoff line 3@40 878 px, payoff line 4@40 921 px, payoff line 5@40 915 px, payoff line 6@40 710 px
row check: the left column ends at x 582 px, the right column starts at x 668 px; the rows end 136 px under the band top; the minimap strip spans x 740 to 1040, y 68 to 106 under the band top; the flat road is 480 px under the band top and the crest 280 px; the car's highest drawn point over a cycle is 167.5 px under the band top (fast panel, 3.70 s into the cycle) and its lowest 480.0 px; the gap readout is centred at x 480 (410 px wide), 516 px under the band top inside the slab; each band is 550 px tall (y 330 to 880 and 880 to 1430); the caption band starts at y 1440; the title rows end at y 280 and the overlay band ends at y 130
Thu Oct  1 10:40:06 AM EEST 2026
```

Checks in the brief (orchestrator's march at 1e-4 s) against the sim:

- crest radius 19.47 m, steepest slope 14.2 deg: 19.4739 m, 14.22 deg
  (passed).
- limit v* = sqrt(g R) = 13.82 m/s = 49.7 km/h: 13.8193 m/s = 49.75 km/h
  (passed; narrated as fifty, card and title 49.7).
- 40 km/h: N never under 0.354 of the weight, at the crest, wheels stay
  down: push bottoms at 0.3535 at x = -0.000 m, closed form 1 - v^2 /
  (g R) = 0.3535, 0 flights (passed).
- 60 km/h: leaves 3.86 m before the crest: 3.859 m, x = -3.8588 m, slope
  10.12 deg, 0.9519 s after the start (passed).
- 60 km/h: in the air 16.21 m in 0.988 s: 16.206 m, 0.9877 s (passed).
- 60 km/h: at most 0.506 m above the road, measured straight up at the
  car's x: 0.5060 m at x = +7.989 m (passed).
- 60 km/h: lands 12.35 m past the crest with 6.76 m/s down: 12.347 m at
  1.9396 s, 6.757 m/s down, 4.230 m/s into the road (passed).
- 50 km/h: N dips to -0.01 g 0.66 m before the crest, 2.6 m of
  weightless rolling, gap under 1 mm: N at the crest -0.0101 g, leaves
  0.658 m before the crest, 2.633 m and 0.1897 s in the air, gap 0.0004
  m, lands 1.976 m past the crest (passed).
- 55 km/h for the description: leaves 2.882 m before the crest, 11.820
  m and 0.7812 s in the air, gap 0.1602 m (16.0 cm), lands 8.938 m past
  the crest, 5.547 m/s down (printed).
- 70 km/h for the description: leaves 5.003 m before the crest, 22.195 m
  and 1.1676 s, gap 1.3959 m (139.6 cm), lands 17.193 m past the crest,
  7.361 m/s down (printed).
- the research entry's 1.5 m / 24 m hump: limit 49.7 km/h, 60 km/h flies
  12.8 m with a 32 cm gap: crest radius 19.4537 m, limit 13.8121 m/s =
  49.72 km/h, 60 km/h leaves 3.037 m before the crest, 12.779 m and
  0.7742 s in the air, gap 0.3237 m (32.4 cm), lands 9.742 m past the
  crest (passed; the entry's 55 km/h numbers were not rerun on that
  hump).
- leave point against the closed form N = 0 solved by bisection on x:
  -3.858788 m both ways, diff +0.0e+00 m; N just before the leave
  +2.1e-07 g, just after -2.1e-07 g (passed).
- flight against the parabola at half the step (5e-05 s): leave time
  +2.1e-14 s, flight length, flight time, largest gap and landing point
  unchanged (diffs +0.0e+00, gap -4.4e-16 m); 40 km/h minimum push
  +9.1e-17, crest time +2.7e-12 s (passed; the air phase is the closed-
  form parabola, so halving the step only moves the landing root).
- times printed in real seconds and in video seconds: the schedule line
  (passed).
- the brief's cycle timing (60 km/h leaves at 2.81 s and lands at 5.78 s
  of each cycle; the 40 km/h car ends 2 m past the hump and the 60 km/h
  car 20 m past): the sim gives 2.86 s and 5.82 s into the cycle (0.9519
  s and 1.9396 s real), 1.55 m and 20.06 m past the hump.
- the car body never enters the readout rows: the roof's highest drawn
  point is 167.5 px under the band top (fast panel, 3.70 s into the
  cycle) against rows that end 136 px under the band top (asserted, 31.5
  px clear); lowest point 480.0 px (the flat road).
- every fixed text line under 950 px: widest 921 px (payoff line 4),
  asserted in measure().

### Production

- Sim `sims/hump/hump.py`: `Hump` (y, y', y'', curvature, cos theta,
  N, R), `march` (RK4 along the road at dt 1e-4 s, the leave point by
  bisection inside the step, closed-form parabola in the air, landing
  root by bisection, largest gap by golden section, phase arrays), the
  closed-form N = 0 bisection on x and the half-step rerun as checks,
  `measure(man)` printing every line above and asserting the text
  widths and the layout clearances, `Renderer` (two 550 px bands drawn
  at 2x on their own layers and reduced; camera following the car's
  point at x 480 and fixed vertically; 80 px/m; the flat road 480 px
  and the crest 280 px under the band top; lane dashes smeared over one
  frame's travel; crest marker; minimap strip x 740 to 1040, y 68 to
  106 under the band top with a dot for the car; dashed gold gap line
  from the wheels to the road, a shadow on the road and the gold readout
  "wheels NN cm off the road" 516 px under the band top inside the slab;
  reset crossfade 0.4 s; frames drawn from the frame integer modulo the
  600-frame cycle; loop fade 0.5 s; ffmpeg rawvideo pipe fed by a
  ProcessPoolExecutor), `main` with --measure-only and --frames.
- Manifest `projects/hump/manifest.json`: seed 0, fps 60, g 9.80665,
  hump 2.5 m x 31.0 m, speeds 40 and 60 km/h, description speeds 50, 55,
  70, research hump 1.5 m x 24.0 m, step 1e-4 s, slow_motion 3.0, cycle
  10.0 s, first_cycle_at -6.1, reset_fade 0.4, scene 40.0 s, start_x
  -19.5 m, 80 px/m, car 4.0 x 1.3 m, wheelbase 2.6 m, wheel radius 0.32
  m, dashes 2.0 m every 4.0 m, minimap x -20 to 40 m, title "Does the
  car leave the road?|same hump, 40 and 60 km/h" until 3.0 s, payoff_t
  26.2, payoff_hold 0.6, six payoff lines formatted from the measured
  values, loop_fade 0.5, music_seed 103, music_gain 0.18, voice_offset
  0.6, caption_y 0.75, overlay "hump 2.5 m x 31 m | 40 and 60 km/h | no
  seed".
- Layout: overlay y 96 to 130; title rows at y 190 and 252 (56 px, end
  at y 280); legend "same hump, 40 and 60 km/h, 1/3 speed" at y 236 (40
  px) and the clock "real time N.NN s, shown at 1/3 speed" at y 290 (28
  px) after the title; bands y 330 to 880 (40 km/h, teal) and 880 to
  1430 (60 km/h, coral); per band a 40 px label row, a left column (x
  40, 28 px: "road push 0.NN of the car's weight" or "road push: none,
  in the air", gold at the minimum, and the gold event row "wheels stay
  on the road" / "in the air 16.2 m, 0.99 s") ending at x 582 and a
  right column (x 668 to 1040: "NN.N m before/past the crest" and the
  minimap); captions y 1440 to 1530 untouched; payoff card 40 px lines
  from y 1572 at a 48 px pitch.
- Hook pre-tests (`media/hump/hooks/pretest.log`, video time = wav +
  0.6 s): hook1 "Does the car leave the road? The same hump at forty
  and at sixty kilometers an hour." ok 4.54 s, question 0.60 to 2.08 s;
  hook2 "A hump in the road. Does the car leave the road? ..." ok 5.32
  s, question from 2.98 s (the first sentence ends 2.74 s); hook3 "Does
  the car take off over the hump? ..." ok 5.14 s, no pause detected;
  hook4 "Do the wheels leave the road? A hump in the road, and the same
  car over it twice, ..." ok 6.90 s, question 0.60 to 3.07 s; hook5
  "Does the car leave the road? A hump in the road, and the same car
  drives over it twice, once at forty and once at sixty kilometers an
  hour." ok 7.56 s, leading silence 0.23 s so the question runs 0.83 to
  2.98 s; words.txt (hump, wheels, crest, leave the road, in the air,
  lift, runs out before the top, weight, forty, sixty, sixteen meters,
  fifty kilometers an hour) ok 17.32 s. No mishearing in any pre-test.
  Kept the question "Does the car leave the road?" first and hook5's
  setup sentence; never "fly" or "flies".
- Narration `projects/hump/narration.txt`: 110 words, two paragraphs;
  the question is the first sentence (words 1 to 6) and is repeated
  word for word as the first sentence of the payoff paragraph; setup
  number "once at forty and once at sixty kilometers an hour"; payoff
  "At forty, no. At sixty, yes: sixteen meters through the air. The
  limit is fifty kilometers an hour."; American spelling; numbers as
  words.
- Voice (`media/hump/voice.log`): pass 1 ok 30.75 s on a 104-word draft;
  pass 2 ok 31.53 s on 111 words (one over the limit; "On the top of"
  trimmed to "On top of"); pass 3 ok 31.90 s on the final 110 words. No
  mishearing in any pass; passes 2 and 3 were re-records for the word
  count and the timing, not for a mismatch. `media/hump/voice.wav` is
  pass 3; the voice ends at 32.50 s of video.
- timing.log (voice-timing.py, offset 0.6 s): 0.60 to 2.17 "Does the
  car leave the road?"; 2.17 to 3.30 "A hump in the road."; 3.30 to
  5.74 "and the same car drives over it twice,"; 5.74 to 8.55 "once at
  40 and once at 60 kilometers an hour."; 8.55 to 11.45 "On top of the
  hump the road curves away under the wheels,"; 11.45 to 12.89 "so it
  pushes up less."; 12.89 to 15.24 "The faster the car, the less it
  pushes."; 15.24 to 17.82 "At 60, the push runs out before the top,";
  17.82 to 22.38 "and the wheels lift. At 40, the road still pushes, and
  the wheels stay down."; 22.38 to 23.99 "Does the car leave the
  road?"; 23.99 to 26.07 "at 40 no at 60"; 26.07 to 32.50 "Yes, 16
  meters through the air. The limit is 50 kilometers an hour. The
  weight of the car makes no difference." The fine split at d 0.12
  (`timing-fine.log`) puts "At 40," at 19.02 to 19.73, "At 60." at
  25.29 to 26.07, "Yes, 16 meters through the air." at 26.07 to 28.32
  and "The limit is 50 kilometers an hour." at 28.32 to 30.44.
- Schedule and sync (first_cycle_at -6.1; cycles start -6.10, 3.90,
  13.90, 23.90, 33.90 s; caption windows from captions.filter): the 60
  km/h car leaves the road at 6.76 s under "and once at sixty" (6.68 to
  7.67), is in the air under "kilometers an hour." and lands at 9.72 s
  under "On top of the hump" (8.69 to 9.78), where the 40 km/h car
  crests at 9.23 s with its push at the gold minimum 0.35; mechanism
  beat: leave 16.76 s under "runs out before the" (16.40 to 17.42),
  crest 17.46 s under "top, and the wheels" (17.42 to 18.71), largest
  gap 50 cm at 18.85 s under "lift." (18.71 to 19.08), the 40 km/h car
  crests at 19.23 s under "At forty, the road" (19.08 to 20.37), the 60
  km/h car lands at 19.72 s, "wheels stay on the road" lit under "still
  pushes, and the wheels stay down." (20.37 to 22.52); the readouts fade
  out at 23.50 s and the fresh cars come in at 23.70 s under "Does the
  car leave the road?" (22.52 to 24.14); payoff beat: "At sixty, yes:"
  (25.36 to 26.56) with the push falling to zero, the card rises from
  26.2 s (fully up 26.8 s), leave 26.76 s under "sixteen meters" (26.56
  to 27.22), crest 27.46 s and the gap 19 to 45 cm under "through the
  air." (27.22 to 28.43), largest gap 50.6 cm at 28.85 s under "The
  limit is fifty" (28.43 to 29.53), landing 29.72 s under "kilometers an
  hour." (29.53 to 30.52), "in the air 16.2 m, 0.99 s" lit under "The
  weight of the car makes no difference." (30.52 to 32.50). On the first
  frame the cycle is 6.10 s in: the 40 km/h car 2.8 m past the crest
  with "wheels stay on the road" lit, the 60 km/h car landed at 13.9 m
  with "in the air 16.2 m, 0.99 s" lit.
- A first full render used first_cycle_at -5.6 (final.mp4 md5
  0f51fa40ede70f67f4056328cb469c88, superseded). Its QA frames showed
  the 60 km/h car still on the road under "sixteen meters" (leave at
  27.26 s) and a 6 cm gap at payoff + 1.8 s, so the cycle was moved 0.5
  s earlier and the measure, render and compose were rerun; every log
  below is from the second run.
- Smoke frames (first run, `media/hump/smoke-*.png`, viewed): 0.0
  (title, both cars past the crest, the 60 km/h car in the air with the
  gap line, shadow and "wheels 26 cm off the road"), 1.0, 1.5, 2.0, 7.4,
  8.0, 9.5 (largest gap, "wheels 51 cm off the road"), 9.8, 10.0, 10.3
  (landing on both wheels), 14.2 (reset crossfade), 17.3 (just left the
  road), 19.75 (40 km/h car at the crest, push 0.35 in gold), 27.3,
  27.9 (card up), 30.3 (landed, event row lit), 39.98 (equal to 0.0).
  The first smoke pass showed the rear wheel sunk about 30 px into the
  road at the landing when the car held its take-off angle; fixed by
  interpolating the drawn pitch (see deviations) and the gap line and
  shadow were thickened for phone screens.
- Footage render (`media/hump/render.log`, 10:40:06 to 10:40:32):
  2400 frames; "loop check: last frame differs from the first in 0 px
  (max channel difference 0)"; "periodicity check: the scene drawn live
  at 40 s differs from 0 s in 0 px"; "loop step: the frame before the
  last differs from the last in 20448 px"; footage.mp4 40.00 s at 60
  fps.
- Compose (`media/hump/compose.log`, 10:40:32 to 10:40:44): music seed
  103, 40.00 s; "captions: 19 pauses detected, 19 matched, max chunk
  start shift 1.166 s against word-count timing" (pause alignment used,
  no fallback); contact sheet 8x5 at 1 fps; final.mp4 40.000000 s;
  preview.mp4 40.066667 s.
- Text widths (PIL, DejaVuSans-Bold, from measure.log): overlay@34 886
  px, title line 1@56 908 px, title line 2@56 894 px, legend@40 887 px,
  clock@28 575 px, labels@40 181 px, push rows@28 542 px, push air@28
  421 px, where rows@28 372 / 338 px, event rows@28 379 / 377 px, gap
  readout@28 410 px, crest@24 68 px, payoff lines@40 644, 825, 878,
  921, 915, 710 px; all under 950 px.

### Local QA

- Frames extracted from final.mp4 and viewed (`media/hump/frame-*.png`):
  - 0.00: overlay, title "Does the car leave the road? / same hump, 40
    and 60 km/h"; 40 km/h car 2.8 m past the crest, "road push 0.46 of
    the car's weight", "wheels stay on the road" lit; 60 km/h car 13.9
    m past the crest just landed, "road push 2.36 of the car's weight",
    "in the air 16.2 m, 0.99 s" lit; minimap dots; nothing in the
    caption band.
  - 1.00: title; caption "Does the car leave"; 40 km/h car 6.5 m past
    the crest on the downslope (push 0.82), 60 km/h car 19.5 m past on
    the flat (push 1.00).
  - 2.10: title; caption "the road?"; 40 km/h car 10.4 m past (push
    1.29), 60 km/h car 25.6 m past.
  - 19.00: legend and clock "real time 1.70 s"; 40 km/h car 0.9 m before
    the crest with "road push 0.36" in gold; 60 km/h car 8.4 m past the
    crest in the air, dashed gold gap line, shadow on the road, "wheels
    50 cm off the road"; caption "lift.".
  - 26.60 (payoff + 0.4): card rising (dim gold, six lines, none
    clipped); caption "sixteen meters"; 40 km/h car 9.6 m before the
    crest (push 1.19), 60 km/h car 4.7 m before the crest with "road
    push 0.19" (about to leave).
  - 27.90: card up; caption "through the air."; 60 km/h car 2.4 m past
    the crest in the air, "wheels 19 cm off the road", crest marker
    under it; 40 km/h car 4.9 m before the crest.
  - 28.00 (payoff + 1.8): same beat, 60 km/h car 2.9 m past the crest,
    "wheels 22 cm off the road"; 40 km/h car 4.5 m before the crest.
  - 29.00: caption "The limit is fifty"; 60 km/h car 8.4 m past the
    crest at the largest gap, "wheels 50 cm off the road"; 40 km/h car
    0.9 m before the crest with "road push 0.36" in gold; card readable
    with "limit sqrt(g R) = 49.7 km/h, R = 19.5 m".
  - 39.98: identical to 0.00 (title back in, same positions and
    readouts).
  - sheet.png (8x5 at 1 fps): the four cycles read the same; the 60
    km/h car hangs in the air with the gap readout at 6 to 9, 16 to 19,
    26 to 29 and 36 to 39 s; the card is up from 26 s; no clipped text.
- Question timing: on screen from frame 0 in the title; spoken 0.71 to
  2.17 s of video; captions "Does the car leave" 0.81 to 1.63 s, "the
  road?" 1.63 to 2.30 s.
- Captions against the narration (script over captions.filter): 33
  chunks, 110 words, word-for-word match True, longest chunk 20
  characters.
- Payoff number on screen when spoken: the card ("at 40 no, at 60 yes:
  16.2 m in the air", "limit sqrt(g R) = 49.7 km/h") is fully up at
  26.8 s; "sixteen meters" is spoken 26.56 to 27.22 s with the 60 km/h
  car leaving the road at 26.76 s, "fifty" 28.43 to 29.53 s with the car
  at its largest gap.
- Band signalstats on footage.mp4: overlay rows 96 to 130 YMAX 28 in
  all 2400 frames; caption rows 1440 to 1530 YMAX 28 in all 2400
  frames.
- Loop: render.log 0 px (footage); final.mp4 frame 2399 against frame 0
  max luma difference 76, mean 0.372 (the title's last fade step plus
  codec noise).
- ffprobe final.mp4: h264 1080x1920, 60/1, 2400 frames; aac 22050 Hz
  mono, 863 frames; duration 40.000000 s; 6815299 bytes; moov at byte
  36 before mdat at 44872 (faststart).
- md5sum final.mp4: 073014606d65a898e8fa94bcc379f9a9
- Narrated numbers against measure.log: "forty" and "sixty" are the
  panel speeds "40 km/h" / "60 km/h"; "sixteen meters" is "16.21 m (16
  m)"; "fifty" is "49.7 km/h (50 km/h)" / "49.75 km/h (about 50 km/h)";
  "no" / "yes" are "0 flight(s)" / "1 flight(s)".
- Metadata number check (script, commas stripped): 79 distinct numbers
  in the description, none missing from measure.log.

### Metadata

- Title: "Does the car leave the road? 40 km/h no, 60 km/h yes: 16 m in
  the air; the limit is 49.7 km/h" (93 characters, ASCII, no < or >).
- Description: 4606 characters, ASCII; the question and the model with
  every constant, "Measured:" bullets (40, 60, the limit, 50, 55, 70,
  the 1.5 m / 24 m hump, the checks), "Why:", the rerun line, the AI
  line.
- Tags (12): does the car leave the road, car over a hump, humpback
  bridge, car jump, road hump, speed limit over a hump, normal force,
  centripetal acceleration, physics, physics visualization, simulation,
  shorts.
- categoryId "27", privacyStatus "private", containsSyntheticMedia
  true, selfDeclaredMadeForKids false.

### Deviations from the brief

- Drawn pitch in the air: the brief said the car holds its last angle
  while in the air. The road is 18.7 deg steeper at the landing than at
  the take-off, so holding the angle buried the rear wheel about 45 cm
  into the road at the landing. The drawing now sits the body on the
  chord between its two wheel contacts and turns the pitch evenly from
  the take-off chord to the landing chord during the flight (drawing
  only; the point model has no attitude; stated in the description).
- Cycle phase: the brief put the cycle start at the start of the scene.
  first_cycle_at is -6.1 s so the flight sits under the words that say
  so (see schedule); on the first frame both cars are past the crest,
  the 60 km/h car just landed with the event row lit.
- Flat road 480 px under the band top (brief: 470) so the gap readout
  fits inside the slab at 516 px; the crest is 280 px under the band
  top.
- The event row is the third row of the left column (28 px) and the
  minimap sits in the right column (x 740 to 1040, y 68 to 106 under
  the band top); the right column reads "NN.N m before/past the crest"
  instead of "x NN m from the crest"; a muted "crest" label 24 px under
  the surface marks the crest.
- Title row 2 is "same hump, 40 and 60 km/h"; the card lines were
  reworded for width (lines 2 and 4 first measured 986 and 1026 px).
- Narration: the mechanism beat is ordered sixty then forty so the
  flight and the 40 km/h crest fall in one cycle (the payoff keeps
  forty then sixty as briefed); added "The faster the car, the less it
  pushes." (to place the leave under its words) and the closing "The
  weight of the car makes no difference."; the repeated question has no
  "So,".
- The narration says "fifty" for the limit while the title and card
  say 49.7 km/h; measure.log prints both "49.75 km/h (about 50 km/h)"
  and "49.7 km/h (50 km/h)".
- The 60 km/h push readout rises above 1 (up to about 2.36) on the
  concave stretches after the landing and before the hump; correct for
  the point model (v^2 kappa with the sign of the curvature), left in.
- The voice ends at 32.50 s; the last 7.5 s hold the card over the
  running scene with music only.

## Niche note

[produced 2026-10-01 as "Does the car leave the road? 40 km/h no, 60 km/h
yes: 16 m in the air; the limit is 49.7 km/h"; on a bigger hump 2.5 m
high and 31 m long (crest radius 19.4739 m, the same limit sqrt(g R) =
13.8193 m/s = 49.75 km/h) so the gap shows; measured at 40 km/h the push
bottoms at 0.3535 of the weight at the crest and the wheels stay down; at
60 km/h the wheels leave 3.859 m before the crest, the car is in the air
for 16.206 m and 0.9877 s, at most 0.5060 m above the road, and lands
12.347 m past the crest with 6.757 m/s down; 50 km/h on the limit (N
-0.0101 g at the crest, 2.633 m of weightless rolling, gap 0.0004 m); 55
km/h 11.820 m, 0.7812 s, 16.0 cm; 70 km/h 22.195 m, 1.1676 s, 139.6 cm;
this entry's 1.5 m / 24 m hump: limit 49.72 km/h, 60 km/h in the air
12.779 m and 0.7742 s, 32.4 cm; leave point equal to N = 0 by bisection,
half-step rerun unchanged; task 20261001-101159]

## Upload

- orchestrator review (2026-10-01T10:48:52+03:00): task evidence, sheet.png and full frames at
  0.00, 19.00, 29.00 and 39.98 s inspected; ffprobe h264 1080x1920 60 fps
  2400 frames 40.000 s; md5 073014606d65a898e8fa94bcc379f9a9; title 93
  chars, no angle brackets; 12 tags; captions match narration word for
  word (33 chunks); measure.log matches the closed forms (R = L^2 / (2
  pi^2 H) = 19.4739 m, limit sqrt(g R) = 49.75 km/h, at 40 km/h the push
  bottoms at 1 - v^2 / (g R) = 0.3535, at 60 km/h leave 3.859 m before
  the crest, 16.206 m and 0.9877 s in the air, gap 0.506 m; 55 km/h
  11.820 m and 16.0 cm as on the card)
- gate fix (2026-10-01T10:48:52+03:00): the description in projects/hump/metadata.json held
  "for |x| <= L / 2", and YouTube rejects < and > in descriptions
  (scripts/yt-upload.py refuses them); replaced with "for x from minus
  L / 2 to plus L / 2"; description now 4626 chars with no angle
  brackets; no other change; approved for upload, waits for attempts 1
  and 2 to resolve
- upload attempt 3 of 5 for the quota day that began 2026-10-01T10:00
  EEST, recorded at 2026-10-01T11:02:15+03:00 before starting scripts/yt-upload.py; two
  attempts (deskchain 12ESwWxQ9Ws and capstan aByGt6B3gh0, both
  published) were on record since the boundary
- uploaded private as UIGCz7tcivw at 2026-10-01T11:02:23+03:00
  (https://youtu.be/UIGCz7tcivw); channels.list 1 unit + videos.insert
  1,600 units; media/hump/upload.log
- scripts/yt-qa.py hump UIGCz7tcivw --wait --publish in the foreground
  (started 2026-10-01T11:02:32+03:00): gate 15 of 15 on the first
  processed read (processed, succeeded, hd, 1080x1920, title,
  description and tags match, category 27, not made for kids, PT41S for
  the 40.000 s file, private before publish); published at
  2026-10-01T11:02:51+03:00; re-read privacyStatus=public
  selfDeclaredMadeForKids=False embeddable=True; yt-qa quota 53 units;
  media/hump/publish.log
- attempt 3 of 5 complete: 1,654 units; slot 3 of 3 resolved as
  published (recorded 2026-10-01T11:03:23+03:00)

### Quota
- attempt 3 of the hard cap of 5 for the quota day that began
  2026-10-01T10:00 EEST; cost 1,654 units (the channels.list verification
  inside yt-upload.py, the 1,600-unit insert, and the gate run's reads,
  update and re-read as printed by yt-qa.py, 53); day total after three
  attempts 1,656 + 1,656 + 1,654 = 4,966 of 10,000 used, 5,034 remaining
  before the closing stats refresh; target of three met
