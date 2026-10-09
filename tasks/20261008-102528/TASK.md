# Produce short: toast nudged or swiped off a table, which face lands down

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day40

## Goal

Backlog idea (trend research 2026-10-08, task 20261008-100401, pillar 2
chaos and physics, everyday mechanics; read the full "Toast, nudged or
swiped" bullet at the end of docs/niche.md): the same slice of toast
leaving the same table, nudged over the edge beside swiped off; the
nudged one lands butter down, the swiped one butter up.

Orchestrator notes (2026-10-08; closed forms and an independent RK4 in
/tmp/day40/closed.py with the log /tmp/day40/closed.log; research script
/tmp/day40/research/toast.py with toast.log; g = 9.807 m/s^2). Read
/tmp/day40/producer-conventions.md first. The model: the toast is a thin
uniform plate of length 2a = 10 cm (a rod in side view, I = m a^2 / 3),
on a table H = 75 cm high. The clock starts when the centre of mass
passes the table corner moving horizontally at v with no tilt (say so:
the speed at the edge is the chosen setup number). Then it slides and
tips on the corner: with s the centre of mass past the corner along the
toast and theta the nose-down tilt,
  s'' = s theta'^2 + g sin theta,
  (a^2/3 + s^2) theta'' = g s cos theta - 2 s s' theta',
  N/m = (a^2/3) theta'' / s
(the corner is frictionless: Mahajan, AJP 2022; the paper's point is
that the answer does not hang on the grip). The toast leaves the corner
when N reaches zero or its back end passes the corner (s = a), then it
flies freely, turning at the leave spin, until its lower end touches the
floor; it lands butter down when cos(theta) < 0 at that instant. Top
band, the "nudged" case: v = 0.05 m/s. Bottom band, the "swiped" case:
v = 1.5 m/s. Integrate the slide-and-tip phase with RK4 at dt = 1e-5 s
(the event by interpolation inside the step), a half-step rerun agreeing
within 1e-6 s, energy per kilogram conserved within 1e-12 J until the
leave; the free flight closed-form; print both runs, the table at 20 ms
steps (s, tilt, spin, N), the speeds for the description, and the
landing face against the speed.

Checks, not facts (the sim must print and compare; state them as
checks; tolerance 1e-3 relative or the brief's rounding): nudged 0.05
m/s: leaves the corner at 193.2 ms when N reaches zero, tilt 38.81 deg,
spin 8.89 rad/s (1.41 turns a second), falls 0.3386 s, turned 211.22 deg
at touchdown, butter DOWN, centre of mass 8.7 cm out from the edge;
swiped 1.5 m/s: leaves at 33.3 ms when its back end passes the corner,
tilt 2.46 deg, spin 2.45 rad/s, falls 0.3614 s, turned 53.12 deg,
butter UP, 59.2 cm out; the face flips at 0.86 to 0.87 m/s (0.80 m/s
turns 96.4 deg and lands DOWN, 1.00 m/s 78.4 deg UP, 2.00 m/s 40.16 deg
UP, 78.7 cm out); 0.20 m/s turns 199.9 deg DOWN, 0.50 m/s 140.9 DOWN;
N/m stays at or above zero until the leave (print the minimum); with
Bacon's grips (static 0.32, kinetic 0.24; AJP 2001) the nudge lands at
178.7 deg DOWN and the swipe at 54.1 deg UP, flip at 0.92 m/s (print
this variant for the description; the panels use the frictionless
corner); a 12 cm toast flips at 0.85 m/s. Print the schedule in video
time, the text widths and the layout clearances.

Drawing: two-band layout (sims/deskchain style, read it whole; the
bands y 330 to 880 and 880 to 1430; sims/tablecloth and sims/deskchain
draw a table edge, sims/hingedstick and sims/broom turning rods,
sims/tray a tip about an edge), SIDE view at 500 px per metre: the table
top 150 px under the band top, its edge at x about 380 with a leg, the
floor 525 px under the band top (0.75 m = 375 px; assert); the toast a
50 by 8 px slab (a 3 px yellow butter line on its top face so the face
reads at a glance) with a thin trail of its centre; after touchdown
draw it settling flat onto the face it shows (a drawing step only: say
so in the description). Label rows (40 px, coloured): "nudged, 5 cm/s"
(coral) and "swiped, 1.5 m/s" (teal). Readouts (28 px): left column
"turned NNN deg" (live) and the clock in ms since the edge; right column
"spin N.N turns a second" (live during the flight) and "N cm out". Gold
event rows: top "nudged: butter down" (lit at its touchdown and held),
bottom "swiped: butter up" (lit at its touchdown and held). Shown at 1/8
speed: cycle 10 s (600 frames): both centres of mass pass the edge 0.8 s
into the cycle (the nudged toast sits 4 mm from the edge at the cycle
start, the swiped one 12 cm back, both already moving: motion in the
first frame), the swiped toast touches the floor 0.394 s real = 3.16 s
after the edge (3.96 s of the cycle), the nudged one 0.532 s real =
4.26 s after the edge (5.06 s of the cycle); both lie on the floor to 9.5
s, then a crossfade reset over the last 0.5 s; 4 cycles in 40 s,
exactly periodic, the last frame equal to the first. The legend row
after the title: "same toast, same 75 cm table, 1/8 speed". Overlay:
"10 cm toast, 75 cm table | no seed" (measure it).

Day forty, first slot. Chosen because "does toast always land butter
side down" is a kitchen debate everyone has had (Matthews' 1995 Ig Nobel
result), both answers appear on screen in one scene, the mechanism (the
slow toast tips on the corner and gets a half turn of spin; the fast one
clears the corner before it can tip) follows the picture, and the fall
repeats as a loop. Question in the first two seconds: "Does toast always
land butter side down?" (pre-test; it is the first sentence; "Toast
slides off the table: does it always land butter side down?" is the
fallback if "Does toast" clips). Keep the question identical in the
title, the hook and the payoff. Setup number: "one and a half meters a
second" for the swipe (one setup number only; the nudge is "slowly" in
narration and "5 cm/s" on the label and in the description). Payoff:
"No. Nudged, it lands butter down. Swiped at one and a half meters a
second, it lands butter up." (the turned angle 53 degrees goes to the
card and the description; at most two numbers in the payoff beat). The
mechanism sentence must follow the picture: the slow toast tips on the
corner and picks up a half turn; the fast one is past the corner before
it can tip. Whisper risks: "toast" (pre-test; may come back "test"),
"butter side down", "nudged", "swiped", "meters a second", "half a
turn"; avoid "do you", avoid "too", no sentence-initial "Spin". Pre-test
hooks with scripts/voiceover.sh and keep the one whose question lands
earliest under two seconds. Measure every fixed text line with PIL
before rendering and keep every line under 950 px, and the title under
100 characters with no < or >. Music seed 121. Templates: sims/deskchain
(two-band layout, asserts, the clock, the crossfade; read it whole),
sims/tablecloth (table scene), sims/hingedstick (turning rod),
sims/tray (tip about an edge, yesterday's). Sim name toast:
sims/toast/toast.py, projects/toast/, media/toast/.

## Claim (expected; the sim's numbers replace these)

The same 10 cm slice of toast leaves the same 75 cm table. Nudged over
the edge at 5 cm/s it tips on the corner, leaves after 193 ms spinning
8.89 rad/s, turns 211 degrees in the fall and lands butter down 8.7 cm
out. Swiped off at 1.5 m/s it clears the corner in 33 ms with only 2.45
rad/s of spin, turns 53 degrees and lands butter up 59 cm out. The face
flips at 0.87 m/s. Narrated: one and a half meters a second (setup);
butter down against butter up (payoff). Card: the question; the answer
(nudged: butter down, 211 deg; swiped at 1.5 m/s: butter up, 53 deg);
the flip speed 0.87 m/s; the leave spin 8.9 against 2.5 rad/s.
Description: the model statement, the equations, the two runs, the
speed table, the grip variant, the 12 cm toast, the checks.

## Claim

The same 10 cm slice of toast (a thin uniform plate, a rod in side view)
leaves the same 75 cm table, the clock started as its centre of mass
passes the corner moving at v with no tilt (v chosen); the corner is
frictionless. Nudged at 5 cm/s it tips on the corner and leaves it after
193.2 ms when the corner force reaches zero, tilted 38.81 deg and
spinning 8.89 rad/s (1.41 turns a second); it falls 0.3386 s, has turned
211.22 deg at touchdown and lands butter down, its centre 8.7 cm out.
Swiped at 1.5 m/s its back end clears the corner after 33.3 ms, tilted
2.46 deg at 2.45 rad/s; it falls 0.3614 s, turns 53.12 deg and lands
butter up, 59.2 cm out. The face flips at 0.862 m/s (0.86 between 0.86
and 0.87 on a 0.01 grid); every speed up to 0.8 m/s lands butter down.
With Bacon's grips (0.32 / 0.24, stick-slip) the nudge turns 174.63 deg
(down), the swipe 54.14 deg (up), the flip moves to 0.911 m/s; a 12 cm
toast flips at 0.846 m/s (0.906 with the grip).
Narrated: one point five meters a second (setup); "No. Nudged, it lands
butter down; swiped at one point five meters a second, it lands butter
up." (payoff). Card: the question; "No. Nudged: butter down, 211 deg";
"swiped at 1.5 m/s: butter up, 53 deg"; "leave spin 8.89 against 2.45
rad/s"; "the face flips at 0.86 m/s"; "with grip on the corner: 0.91 m/s".

## Evidence

### Measurements

`nix develop -c python3 sims/toast/toast.py --measure-only`
(final run 10:42:06, exit 0, saved as media/toast/measure.log):

```
Thu Oct  8 10:42:01 AM EEST 2026
warning: Git tree '/home/alex/personal/seedzero' is dirty
setup: side view, two panels on one clock, the same table drawn the same way at the same scale: the same slice of toast, a thin uniform plate 10 cm long (2a; a rod in side view, I = m a^2 / 3; its mass cancels) leaves a table 75 cm high; g = 9.807 m/s^2; the clock starts when the centre of mass passes the table corner moving horizontally at v with no tilt (v is the chosen setup number; on the table the toast slides with no loss); top panel nudged at v = 0.05 m/s = 5 cm/s, bottom panel swiped at v = 1.5 m/s; then it slides and tips on the corner, frictionless (Mahajan, AJP 2022), with s the centre of mass past the corner along the toast and theta the nose-down tilt: s'' = s theta'^2 + g sin theta, (a^2/3 + s^2) theta'' = g s cos theta - 2 s s' theta', N/m = (a^2/3) theta'' / s; RK4 at dt = 1e-05 s; it leaves the corner when N reaches zero or its back end passes the corner (s = a = 5 cm), the event located inside the step by bisection on the RK4 sub-step; then free flight in closed form, turning at the leave spin, until its lower end touches the floor; butter down when cos theta < 0 then; shown at 1/8 speed on a 10 s cycle (600 frames), 4 cycles in 40 s; drawn at 500 px per metre; deterministic, no seed
nudged at 0.05 m/s: leaves the corner at 193.1795 ms = 193.2 ms when N reaches zero (s = 2.3833 cm past the corner, s' = 0.4299 m/s), tilt 38.8138 deg = 38.81 deg, spin 8.8877 rad/s = 8.89 rad/s = 1.4145 turns a second = 1.41; centre of mass 1.857 cm out and 1.494 cm down, moving (0.2022, -0.4345) m/s; falls 0.338557 s = 0.3386 s and touches the floor 0.531737 s = 0.532 s after the edge turned 211.2173 deg = 211.22 deg: cos theta = -0.8552, butter DOWN; centre of mass 8.703 cm = 8.7 cm out from the edge; minimum N/m 0.000000 m/s^2 until the leave; energy per kilogram drift 5.0e-16 J over 19318 steps; half-step rerun (dt = 5e-06 s): leaves at 193.179455 ms (-6.4e-16 s), turned 211.217289 deg (+8.2e-13 deg)
  nudged t   0 ms on the corner: s  0.000 cm, tilt    0.00 deg, spin  0.00 rad/s, N/m  9.807 m/s^2
  nudged t  20 ms on the corner: s  0.100 cm, tilt    0.04 deg, spin  0.12 rad/s, N/m  9.783 m/s^2
  nudged t  40 ms on the corner: s  0.200 cm, tilt    0.36 deg, spin  0.47 rad/s, N/m  9.712 m/s^2
  nudged t  60 ms on the corner: s  0.304 cm, tilt    1.21 deg, spin  1.05 rad/s, N/m  9.587 m/s^2
  nudged t  80 ms on the corner: s  0.416 cm, tilt    2.86 deg, spin  1.87 rad/s, N/m  9.376 m/s^2
  nudged t 100 ms on the corner: s  0.549 cm, tilt    5.58 deg, spin  2.93 rad/s, N/m  8.998 m/s^2
  nudged t 120 ms on the corner: s  0.723 cm, tilt    9.67 deg, spin  4.24 rad/s, N/m  8.284 m/s^2
  nudged t 140 ms on the corner: s  0.969 cm, tilt   15.39 deg, spin  5.78 rad/s, N/m  6.958 m/s^2
  nudged t 160 ms on the corner: s  1.334 cm, tilt   22.94 deg, spin  7.38 rad/s, N/m  4.739 m/s^2
  nudged t 180 ms on the corner: s  1.882 cm, tilt   32.17 deg, spin  8.61 rad/s, N/m  1.798 m/s^2
  nudged t 200 ms in flight: centre   1.99 cm out,   1.81 cm down, tilt   42.29 deg, spin  8.89 rad/s, N 0
  nudged t 220 ms in flight: centre   2.40 cm out,   3.01 cm down, tilt   52.47 deg, spin  8.89 rad/s, N 0
  nudged t 240 ms in flight: centre   2.80 cm out,   4.60 cm down, tilt   62.66 deg, spin  8.89 rad/s, N 0
  nudged t 260 ms in flight: centre   3.21 cm out,   6.59 cm down, tilt   72.84 deg, spin  8.89 rad/s, N 0
  nudged t 280 ms in flight: centre   3.61 cm out,   8.96 cm down, tilt   83.03 deg, spin  8.89 rad/s, N 0
  nudged t 300 ms in flight: centre   4.02 cm out,  11.73 cm down, tilt   93.21 deg, spin  8.89 rad/s, N 0
  nudged t 320 ms in flight: centre   4.42 cm out,  14.89 cm down, tilt  103.39 deg, spin  8.89 rad/s, N 0
  nudged t 340 ms in flight: centre   4.83 cm out,  18.44 cm down, tilt  113.58 deg, spin  8.89 rad/s, N 0
  nudged t 360 ms in flight: centre   5.23 cm out,  22.39 cm down, tilt  123.76 deg, spin  8.89 rad/s, N 0
  nudged t 380 ms in flight: centre   5.63 cm out,  26.73 cm down, tilt  133.95 deg, spin  8.89 rad/s, N 0
  nudged t 400 ms in flight: centre   6.04 cm out,  31.45 cm down, tilt  144.13 deg, spin  8.89 rad/s, N 0
  nudged t 420 ms in flight: centre   6.44 cm out,  36.58 cm down, tilt  154.32 deg, spin  8.89 rad/s, N 0
  nudged t 440 ms in flight: centre   6.85 cm out,  42.09 cm down, tilt  164.50 deg, spin  8.89 rad/s, N 0
  nudged t 460 ms in flight: centre   7.25 cm out,  48.00 cm down, tilt  174.69 deg, spin  8.89 rad/s, N 0
  nudged t 480 ms in flight: centre   7.66 cm out,  54.30 cm down, tilt  184.87 deg, spin  8.89 rad/s, N 0
  nudged t 500 ms in flight: centre   8.06 cm out,  60.99 cm down, tilt  195.06 deg, spin  8.89 rad/s, N 0
  nudged t 520 ms in flight: centre   8.47 cm out,  68.07 cm down, tilt  205.24 deg, spin  8.89 rad/s, N 0
  nudged t 193.2 ms leaves; touchdown at 531.7 ms turned 211.22 deg
swiped at 1.5 m/s: leaves the corner at 33.2967 ms = 33.3 ms when the back end passes the corner (s = 5.0000 cm past the corner, s' = 1.5074 m/s), tilt 2.4623 deg = 2.46 deg, spin 2.4466 rad/s = 2.45 rad/s = 0.3894 turns a second = 0.39; centre of mass 4.995 cm out and 0.215 cm down, moving (1.5007, -0.1870) m/s; falls 0.361357 s = 0.3614 s and touches the floor 0.394654 s = 0.395 s after the edge turned 53.1167 deg = 53.12 deg: cos theta = +0.6002, butter UP; centre of mass 59.225 cm = 59.2 cm out from the edge; minimum N/m 0.605536 m/s^2 until the leave; energy per kilogram drift 4.9e-15 J over 3330 steps; half-step rerun (dt = 5e-06 s): leaves at 33.296676 ms (+4.9e-17 s), turned 53.116661 deg (-1.6e-13 deg)
  swiped t   0 ms on the corner: s  0.000 cm, tilt    0.00 deg, spin  0.00 rad/s, N/m  9.807 m/s^2
  swiped t  20 ms on the corner: s  3.001 cm, tilt    0.85 deg, spin  1.70 rad/s, N/m  2.264 m/s^2
  swiped t  40 ms in flight: centre   6.00 cm out,   0.36 cm down, tilt    3.40 deg, spin  2.45 rad/s, N 0
  swiped t  60 ms in flight: centre   9.00 cm out,   1.06 cm down, tilt    6.21 deg, spin  2.45 rad/s, N 0
  swiped t  80 ms in flight: centre  12.00 cm out,   2.16 cm down, tilt    9.01 deg, spin  2.45 rad/s, N 0
  swiped t 100 ms in flight: centre  15.01 cm out,   3.64 cm down, tilt   11.81 deg, spin  2.45 rad/s, N 0
  swiped t 120 ms in flight: centre  18.01 cm out,   5.52 cm down, tilt   14.62 deg, spin  2.45 rad/s, N 0
  swiped t 140 ms in flight: centre  21.01 cm out,   7.79 cm down, tilt   17.42 deg, spin  2.45 rad/s, N 0
  swiped t 160 ms in flight: centre  24.01 cm out,  10.46 cm down, tilt   20.22 deg, spin  2.45 rad/s, N 0
  swiped t 180 ms in flight: centre  27.01 cm out,  13.51 cm down, tilt   23.03 deg, spin  2.45 rad/s, N 0
  swiped t 200 ms in flight: centre  30.01 cm out,  16.96 cm down, tilt   25.83 deg, spin  2.45 rad/s, N 0
  swiped t 220 ms in flight: centre  33.01 cm out,  20.80 cm down, tilt   28.63 deg, spin  2.45 rad/s, N 0
  swiped t 240 ms in flight: centre  36.02 cm out,  25.03 cm down, tilt   31.44 deg, spin  2.45 rad/s, N 0
  swiped t 260 ms in flight: centre  39.02 cm out,  29.65 cm down, tilt   34.24 deg, spin  2.45 rad/s, N 0
  swiped t 280 ms in flight: centre  42.02 cm out,  34.67 cm down, tilt   37.04 deg, spin  2.45 rad/s, N 0
  swiped t 300 ms in flight: centre  45.02 cm out,  40.08 cm down, tilt   39.85 deg, spin  2.45 rad/s, N 0
  swiped t 320 ms in flight: centre  48.02 cm out,  45.88 cm down, tilt   42.65 deg, spin  2.45 rad/s, N 0
  swiped t 340 ms in flight: centre  51.02 cm out,  52.08 cm down, tilt   45.46 deg, spin  2.45 rad/s, N 0
  swiped t 360 ms in flight: centre  54.02 cm out,  58.66 cm down, tilt   48.26 deg, spin  2.45 rad/s, N 0
  swiped t 380 ms in flight: centre  57.03 cm out,  65.64 cm down, tilt   51.06 deg, spin  2.45 rad/s, N 0
  swiped t 33.3 ms leaves; touchdown at 394.7 ms turned 53.12 deg
nudged: in flight the lowest toast point over the table side (x < 0) is +0.015 mm from the table plane
swiped: in flight the lowest toast point over the table side (x < 0) is never over the table
landing face against the speed (frictionless corner): 0.05 m/s: leaves at 193.2 ms (N zero), tilt 38.81 deg, spin 8.89 rad/s, falls 0.3386 s, turned 211.22 deg, butter DOWN, 8.7 cm out; 0.1 m/s: leaves at 158.3 ms (N zero), tilt 36.19 deg, spin 9.19 rad/s, falls 0.3367 s, turned 213.41 deg, butter DOWN, 9.0 cm out; 0.2 m/s: leaves at 128.8 ms (N zero), tilt 31.21 deg, spin 8.79 rad/s, falls 0.3348 s, turned 199.86 deg, butter DOWN, 11.4 cm out; 0.3 m/s: leaves at 114.9 ms (N zero), tilt 27.31 deg, spin 8.01 rad/s, falls 0.3350 s, turned 181.14 deg, butter DOWN, 14.8 cm out; 0.4 m/s: leaves at 106.7 ms (N zero), tilt 24.27 deg, spin 7.22 rad/s, falls 0.3277 s, turned 159.89 deg, butter DOWN, 18.2 cm out; 0.5 m/s: leaves at 93.5 ms (back end), tilt 18.95 deg, spin 6.47 rad/s, falls 0.3292 s, turned 140.92 deg, butter DOWN, 21.7 cm out; 0.6 m/s: leaves at 80.3 ms (back end), tilt 14.14 deg, spin 5.71 rad/s, falls 0.3338 s, turned 123.36 deg, butter DOWN, 25.2 cm out; 0.8 m/s: leaves at 61.7 ms (back end), tilt 8.42 deg, spin 4.48 rad/s, falls 0.3423 s, turned 96.37 deg, butter DOWN, 32.5 cm out; 1 m/s: leaves at 49.7 ms (back end), tilt 5.48 deg, spin 3.64 rad/s, falls 0.3494 s, turned 78.34 deg, butter UP, 40.0 cm out; 1.5 m/s: leaves at 33.3 ms (back end), tilt 2.46 deg, spin 2.45 rad/s, falls 0.3614 s, turned 53.12 deg, butter UP, 59.2 cm out; 2 m/s: leaves at 25.0 ms (back end), tilt 1.39 deg, spin 1.84 rad/s, falls 0.3682 s, turned 40.16 deg, butter UP, 78.7 cm out
flip: the face turns from butter down to butter up at 0.86207 m/s = 0.862 m/s = 0.86 m/s (bisection; 0.86 m/s lands down, 0.87 m/s up); every speed up to 0.8 m/s lands butter down
grip variant (Bacon, AJP 2001: static 0.32, kinetic 0.24 on the corner, stick-slip): nudged at 0.05 m/s sticks at 21.3 ms (0.53 mm past the corner, tilt 0.04 deg); slips at 322.2 ms (tilt 17.73 deg); leaves at 469.5 ms when N reaches zero, tilted 48.68 deg at 6.48 rad/s, turns 174.63 deg, butter DOWN, 8.8 cm out; swiped at 1.5 m/s never sticks; leaves at 33.8 ms at 2.49 rad/s and turns 54.14 deg, butter UP, 57.9 cm out; the face flips at 0.91112 m/s = 0.91 m/s (0.91 lands down, 0.92 up)
the research script's friction (-0.24 N sign(s'), no sticking: s' chatters about zero while the kinetic grip holds) for the nudge: leaves at 459.4 ms tilted 48.42 deg at 6.66 rad/s, turns 178.70 deg, butter DOWN; the stick-slip model above turns 174.63 deg (-4.07 deg): the same face
12 cm toast: flips at 0.84647 m/s = 0.85 m/s frictionless (0.84 down, 0.85 up), at 0.90608 m/s = 0.91 m/s with the grip (0.90 down, 0.91 up)
checks against the brief (41 checks, 0 failed): nudged leave (ms): brief 193.2, sim 193.179, diff -2.1e-02: ok; nudged leave tilt (deg): brief 38.81, sim 38.8138, diff +3.8e-03: ok; nudged spin (rad/s): brief 8.89, sim 8.88773, diff -2.3e-03: ok; nudged turns a second: brief 1.41, sim 1.41453, diff +4.5e-03: ok; nudged fall (s): brief 0.3386, sim 0.338557, diff -4.3e-05: ok; nudged turned (deg): brief 211.22, sim 211.217, diff -2.7e-03: ok; nudged out (cm): brief 8.7, sim 8.70255, diff +2.5e-03: ok; swiped leave (ms): brief 33.3, sim 33.2967, diff -3.3e-03: ok; swiped leave tilt (deg): brief 2.46, sim 2.46225, diff +2.3e-03: ok; swiped spin (rad/s): brief 2.45, sim 2.44657, diff -3.4e-03: ok; swiped fall (s): brief 0.3614, sim 0.361357, diff -4.3e-05: ok; swiped turned (deg): brief 53.12, sim 53.1167, diff -3.3e-03: ok; swiped out (cm): brief 59.2, sim 59.2253, diff +2.5e-02: ok; 0.80 m/s turned (deg): brief 96.4, sim 96.3724, diff -2.8e-02: ok; 1.00 m/s turned (deg): brief 78.4, sim 78.3448, diff -5.5e-02: ok; 2.00 m/s turned (deg): brief 40.16, sim 40.1562, diff -3.8e-03: ok; 2.00 m/s out (cm): brief 78.7, sim 78.6549, diff -4.5e-02: ok; 0.20 m/s turned (deg): brief 199.9, sim 199.86, diff -4.0e-02: ok; 0.50 m/s turned (deg): brief 140.9, sim 140.923, diff +2.3e-02: ok; flip at least 0.86: sim 0.86207: ok; flip at most 0.87: sim 0.86207: ok; grip nudge turned, research friction (deg): brief 178.7, sim 178.702, diff +2.2e-03: ok; grip swipe turned (deg): brief 54.1, sim 54.1365, diff +3.7e-02: ok; grip flip, first 0.01 step up (m/s): brief 0.92, sim 0.92, diff +0.0e+00: ok; 12 cm flip, first 0.01 step up (m/s): brief 0.85, sim 0.85, diff +0.0e+00: ok; swiped touchdown = brief 33.3 ms + 0.3614 s (s real): brief 0.3947, sim 0.394654, diff -4.6e-05: ok; nudged touchdown (s real): brief 0.532, sim 0.531737, diff -2.6e-04: ok; nudged leaves when N reaches zero: ok; swiped leaves when its back end passes: ok; nudged butter DOWN: ok; swiped butter UP: ok; 0.80 m/s DOWN: ok; 1.00 m/s UP: ok; 2.00 m/s UP: ok; 0.20 m/s DOWN: ok; 0.50 m/s DOWN: ok; grip nudge DOWN: ok; grip swipe UP: ok; N/m at or above zero until the leave (min nudged 0.0e+00, swiped 0.6055): ok; energy within 1e-12 J/kg (5.0e-16, 4.9e-15): ok; half-step rerun within 1e-6 s (-6.4e-16, 4.9e-17): ok
schedule (video time, 1/8 speed): cycles of 10 s start at -10.00, 0.00, 10.00, 20.00, 30.00 s; at the cycle start (100 ms real before the edge) the nudged toast's centre is 5.0 mm from the edge and the swiped one's 15.0 cm back, both moving; both centres pass the edge 0.8 s into each cycle at 0.80, 10.80, 20.80, 30.80 s; the swiped toast leaves the corner 0.266 s later and touches the floor 0.3947 s real = 3.157 s after the edge (3.957 s into the cycle) at 3.96, 13.96, 23.96, 33.96 s (its event row lights); the nudged toast leaves the corner 1.545 s after the edge and touches the floor 0.5317 s real = 4.254 s after the edge (5.054 s into the cycle) at 5.05, 15.05, 25.05, 35.05 s (its event row lights); each settles flat over 0.4 s (drawing only); both lie on the floor until the reset crossfade over the last 0.5 s of each cycle (from 9.50, 19.50, 29.50, 39.50 s; the readouts out over its first half and in over its second); title until 3 s; payoff card from 31.6 s; the title fades back in over the last 0.5 s and the last frame repeats the first (the scene is periodic: 40 s holds exactly 4 cycles)
text widths (the on-screen strings verbatim): overlay@34 661 px '10 cm toast, 75 cm table | no seed', title line 1@56 730 px 'Does toast always land', title line 2@56 571 px 'butter side down?', legend@40 926 px 'same toast, same 75 cm table, 1/8 speed', label nudged@40 345 px 'nudged, 5 cm/s', event nudged@40 478 px 'nudged: butter down', label swiped@40 353 px 'swiped, 1.5 m/s', event swiped@40 402 px 'swiped: butter up', turned@28 243 px 'turned 211 deg', clock before@28 241 px 'edge in 162 ms', clock@28 343 px '532 ms past the edge', clock landed@28 273 px 'landed at 532 ms', spin@28 369 px 'spin 1.4 turns a second', out@28 187 px '59.2 cm out', on the table@28 192 px 'on the table', payoff line 1@40 943 px 'Does toast always land butter side down?', payoff line 2@40 784 px 'No. Nudged: butter down, 211 deg', payoff line 3@40 824 px 'swiped at 1.5 m/s: butter up, 53 deg', payoff line 4@40 764 px 'leave spin 8.89 against 2.45 rad/s', payoff line 5@40 560 px 'the face flips at 0.86 m/s', payoff line 6@40 744 px 'with grip on the corner: 0.91 m/s'
row check: label row to x 393 px, event row from x 562 px (widest 478 px), left readouts to x 383 px, right readouts from x 671 px; the label and event rows span 20 to 59 px, the readouts 65 to 126 px under the band top; the table top 150 px under the band top (slab to 174), its edge at x 380, the floor at 525 (375 px = 0.75 m at 500 px/m); the toast slab (50 by 10 px) over the whole cycle spans x 233 to 695 and y 132 to 525 px under the band top: 0 touches with a text box; each band is 550 px tall (y 330 to 880 and 880 to 1430); the caption band starts at y 1440
exit 0
Thu Oct  8 10:42:06 AM EEST 2026
```

Checks in the brief, each printed and compared by the sim (41 checks,
0 failed; tolerance 1e-3 relative or the brief's rounding; assert):

- nudged 0.05 m/s leaves at 193.2 ms when N reaches zero: sim 193.1795
  ms, cause N reaches zero. ok.
- nudged tilt 38.81 deg, spin 8.89 rad/s (1.41 turns a second): sim
  38.8138 deg, 8.8877 rad/s, 1.4145 turns a second. ok.
- nudged falls 0.3386 s, turned 211.22 deg, butter DOWN, 8.7 cm out: sim
  0.338557 s, 211.2173 deg (cos -0.8552), DOWN, 8.703 cm. ok.
- swiped 1.5 m/s leaves at 33.3 ms when its back end passes: sim
  33.2967 ms, back end. ok.
- swiped tilt 2.46 deg, spin 2.45 rad/s, falls 0.3614 s, turned 53.12
  deg, butter UP, 59.2 cm out: sim 2.4623 deg, 2.4466 rad/s, 0.361357
  s, 53.1167 deg (cos +0.6002), UP, 59.225 cm. ok.
- face flips between 0.86 and 0.87 m/s: sim 0.86207 m/s by bisection
  (0.86 lands down, 0.87 up). ok.
- 0.80 m/s 96.4 deg DOWN: sim 96.3724, DOWN; 1.00 m/s 78.4 deg UP: sim
  78.3448, UP; 2.00 m/s 40.16 deg UP, 78.7 cm: sim 40.1562, UP, 78.65
  cm; 0.20 m/s 199.9 DOWN: sim 199.86; 0.50 m/s 140.9 DOWN: sim 140.923.
  ok.
- N/m at or above zero until the leave: minimum 0.000000 (nudged, the
  leave itself) and 0.6055 m/s^2 (swiped). ok.
- energy per kilogram within 1e-12 J until the leave: 5.0e-16 and
  4.9e-15 J. ok.
- half-step rerun within 1e-6 s: -6.4e-16 s and +4.9e-17 s. ok.
- Bacon's grips: nudge 178.7 deg DOWN: the brief's number comes from the
  research script's friction (kinetic only, sign switching, no
  sticking); the sim replicates it (178.70 deg, DOWN; checked) and uses
  a stick-slip model for the description: 174.63 deg, DOWN (see
  Deviations). Swipe 54.1 deg UP: sim 54.1365, UP. Flip 0.92 m/s
  (first 0.01 step up): sim 0.92 (bisection 0.91112). ok.
- 12 cm toast flips at 0.85 m/s (first 0.01 step up): sim 0.85
  (bisection 0.84647). ok.
- schedule: swiped touchdown 0.394 s real: sim 0.394654 s (the brief's
  own 33.3 ms + 0.3614 s = 0.3947 s; the check compares that sum);
  3.157 s after the edge, 3.957 s into the cycle (brief 3.16 / 3.96).
  Nudged 0.532 s real: sim 0.531737 s, 4.254 s after the edge, 5.054 s
  into the cycle (brief 4.26 / 5.06, a rounding of 0.532 x 8). ok.
- floor 525 px under the band top, 375 px = 0.75 m at 500 px/m:
  asserted. ok.
- in flight the nudged toast never dips under the table plane on the
  table side (closest +0.015 mm); the swiped toast is never over the
  table. ok.
- every fixed text line under 950 px: widest is payoff line 1 at 943
  px, then the legend at 926 px; asserted. ok.
- layout: the toast slab over the whole cycle spans x 233 to 695 and y
  132 to 525 px under the band top, 0 touches with the label, event and
  readout boxes (readouts end at 126 px); asserted. ok.

### Production

- sims/toast/toast.py (new): two-band side view after sims/deskchain
  (asserts, clock, crossfade, render loop), table after sims/tablecloth.
  RK4 on (s, s', theta, theta') at 100000 steps per second, the leave
  located inside the step by bisection on the RK4 sub-step, half-step
  rerun, energy drift, minimum N; free flight in closed form with the
  touchdown root scanned at 0.1 ms and bisected; flip speed by bisection
  on v; the grip variant as stick-slip (static 0.32, kinetic 0.24) plus
  a replication of the research script's friction; 41 brief checks with
  assert; text-width, box-collision, floor and table-clearance asserts;
  loop and periodicity asserts in the renderer. Deterministic, no seed.
- projects/toast/manifest.json: toast 0.10 m, table 0.75 m, v 0.05 and
  1.5 m/s, g 9.807, steps_per_second 100000, slow 8, cycle 10 s, edge_at
  0.8, first_cycle_at 0.0, reset_fade 0.5, settle_s 0.4, px_per_m 500,
  edge x 380, table top 150, floor 525, toast 10 px thick, title_until
  3.0, payoff_t 31.6, music_seed 121, voice_offset 0.6.
- Smoke frames (media/toast/smoke-*.png at 0.0, 1.5, 2.0, 2.5, 3.2,
  3.96, 4.5, 5.06, 6.0, 9.75, 32.6, 39.75 s) viewed with 4x crops of the
  landed slices: nudged lies butter down at x about 420, swiped butter
  up at x about 666. Fixes from the smoke pass: the payoff card lines
  shortened to fit 950 px; the slab made 10 px with a 4 px butter strip
  and darker crust, so the face reads at phone size.
- Full render media/toast/render.log: loop check 0 px (max diff 0),
  periodicity 0 px (max diff 0), loop step 7944 px (the readouts at 87
  percent alpha one frame before the loop); footage.mp4 40.00 s at 60
  fps, 2400 frames.
- Speech service: the shared Piper service on port 10303 answered 503
  backend_unavailable to every call from 10:27 (journal: no successful
  POST today; its health endpoint says ok). Running the same piper binary
  by hand worked, so every take here used a private copy of the same
  server.py, piper binary and en_US-lessac-medium voice on
  127.0.0.1:10373 (TTS_API override for scripts/voiceover.sh; whisper on
  10301 as usual). The helper was stopped by its PID (2707468) after the
  last take.
- Hook pre-tests (media/toast/hooks/pretest.log, one take each): hook1
  "Does toast always land butter side down? Same toast, same table,
  nudged or swiped." ok (5.36 s, no pause inside the question); hook2 "Toast slides off
  the table: does it always land butter side down?" ok, the question
  after the pause ending 1.84 s (2.44 s of video); hook3 "Does toast
  always land butter side down? The same slice, the same table." ok,
  pause after the question at 2.42 s; hook4 "... Two slices leave one
  table." ok. Words file (nudged slowly, swiped off at one and a half
  meters a second, tips on the corner, flips past upside down, butter
  faces the floor, barely turns, it lands butter down / up): failed:
  "one and a half" came back "1.5" both times; rewritten as "one point
  five". Chosen opener: the question first ("Toast" and "butter side
  down" passed in every take).
- Narration projects/toast/narration.txt, 106 words; the question "Does
  toast always land butter side down?" is the first sentence and is
  repeated word for word before the payoff.
- Voice round trip media/toast/voice.log: pass 1 ok (35.16 s, the first
  order: setup for both, then the mechanism); pass 2 reordered so each
  beat follows its panel (the nudge beats, then the swipe beats): FAIL,
  the sentence-initial "Swiped" after "butter down." came back "wiped";
  pass 3 joined the two payoff clauses with a semicolon: ok (33.36 s).
  3 passes, 2 ok, the final file is pass 3.
- Timing media/toast/timing.log (offset 0.6 s): the question starts at
  0.60 s of video with no leading pause (whisper on the first 1.4 s of
  voice hears "Does toast always land", on the first 2.2 s the whole
  question; the question ends at 2.43 s of voice = 3.03 s of video);
  "On top, it is nudged slowly over the edge" 6.40 to 9.31 s; "It tips on
  the corner while it slides, and it leaves the table spinning" 9.31 to
  about 13 s (the nudged slice reaches the edge at 10.80, leaves the
  corner at 12.35); "In the fall it flips past upside down" to 15.28 s
  (touchdown 15.05); "Below, it is swiped off at 1.5 meters a second"
  16.94 to about 20.6 s; "It is past the corner before it can tip" to
  22.67 s (the swiped slice leaves the corner at 21.07); "and it barely
  turns before it lands" (touchdown 23.96); the repeated question to
  about 27.8 s; "No." 27.8 s; "Nudged, it lands butter down" 28.3 to
  30.0 s (the cycle-3 rows lit to 29.5); "swiped at 1.5 meters a second"
  30.0 to 32.76 s (the swiped slice flies 31.07 to 33.96); "It lands
  butter up." 32.76 to 33.96 s, the touchdown at 33.96 s; the voice ends
  at 33.96 s of video.
- payoff_t 31.6: the card rises during "one point five meters a second"
  (captions 30.55 to 33.22 s); the setup number 1.5 m/s is on the bottom
  label for the whole video.
- Compose media/toast/compose.log: music seed 121, 40.00 s; captions 19
  pauses detected, 19 matched, max chunk start shift 1.353 s; final.mp4
  40.000000 s; preview.mp4 and sheet.png written.

### Local QA

- ffprobe final.mp4: h264 1080x1920 at 60/1, aac 22050 Hz mono,
  duration 40.000000 s; atoms ftyp, moov at 32, free, mdat (faststart);
  3016476 bytes; md5 0737689dea46a6f6f000eb29a9f5a097.
- footage.mp4: h264 1080x1920 at 60/1, 2400 frames, 40.000000 s.
- Caption and overlay bands: signalstats YMAX of footage.mp4 rows 1440
  to 1530 is 28 and rows 96 to 130 is 28 over all frames (background
  only).
- Captions: 36 caption chunks plus the overlay "10 cm toast, 75 cm table
  | no seed" in media/toast/captions.filter; the joined caption text
  equals the narration word for word (106 words) after undoing the
  drawtext escapes; first captions "Does toast always" 0.600 to 1.643
  s, "land butter side" 1.643 to 2.687 s, "down?" 2.687 to 3.201 s.
- Full-resolution frames viewed (media/toast/qa-*.png): 0.00 s overlay,
  two-row title, both slices on their tables (nudged 5 mm from the edge,
  swiped 15 cm back), readouts "edge in 100 ms", no caption; 1.00 s
  caption "Does toast always", the swiped slice just past the edge; 2.10
  s caption "land butter side", the nudged slice tilted 24 deg on the
  corner, the swiped one in flight with its trail; 11.50 s legend, the
  nudged slice tipping at 4 deg, caption "slides, and it"; 21.50 s the
  swiped slice past the corner at 10 deg, caption "corner before it
  can"; 25.10 s both landed, both gold event rows lit, "turned 211 deg"
  / "turned 53 deg" and "8.7 cm out" / "59.2 cm out" in gold, caption
  "So, does toast"; 32.20 s the card rising, the swiped slice in flight,
  caption "meters a second, it"; 34.10 s the swiped slice touching down
  with "swiped: butter up" lit, the card full, no caption (the voice
  ended at 33.96 s); 39.983 s identical to frame 0. Nothing clipped at
  the frame edge; the readouts, event rows and slices never overlap.
- sheet.png (8x5 at 1 fps): 40 cells, the captions in order, the card
  from 32 s, the loop closes on the first frame.

### Metadata

- projects/toast/metadata.json written by media/toast/metadata.py with
  asserts: title 90 characters (at most 100), description 3235
  characters (under 5,000), ASCII, no angle brackets, 11 tags; every
  number in the title and description (57 distinct, commas stripped)
  appears in media/toast/measure.log.
- Title: Does toast always land butter side down? No: nudged lands down,
  swiped at 1.5 m/s lands up
- privacyStatus private, categoryId 27, containsSyntheticMedia true,
  selfDeclaredMadeForKids false. The description says the settle onto
  the floor is a drawing step, not simulated.

### Deviations from the brief

- Setup number narrated as "one point five meters a second", not "one
  and a half meters a second": whisper returned "one and a half" as
  "1.5" in the word pre-test, which fails the round trip.
- The payoff's two sentences are joined by a semicolon ("No. Nudged, it
  lands butter down; swiped at one point five meters a second, it lands
  butter up."): in pass 2 the sentence-initial "Swiped" came back
  "wiped".
- Narration order: the nudge beats (setup, tip, spin, fall) then the
  swipe beats, so each sentence plays over its panel's motion.
- Toast slab 50 by 10 px with a 4 px butter strip, not 50 by 8 with 3:
  at 8 px the face did not read at phone size. The slab is centred on
  the model's line, so the line runs 5 px over the drawn table top and
  floor; the 375 px (0.75 m) drop is unchanged (asserted).
- At the cycle start the nudged slice's centre is 5 mm from the edge and
  the swiped one's 15 cm back, not 4 mm and 12 cm: 0.8 s of video at
  1/8 speed is 0.1 s real (0.05 x 0.1 = 5 mm, 1.5 x 0.1 = 15 cm).
- Touchdown times: swiped 0.3947 s real (the brief's 0.394 truncates its
  own 33.3 ms + 0.3614 s), 3.157 s after the edge at 3.957 s of the
  cycle; nudged 4.254 s after the edge at 5.054 s of the cycle (brief
  4.26 / 5.06 from 0.532 x 8).
- Grip variant: the description uses a stick-slip model (static 0.32
  holds the nudged slice from 21.3 ms to 322.2 ms, then kinetic 0.24):
  174.63 deg, butter down. The brief's 178.7 deg comes from the research
  script's friction, which applies only the kinetic grip with a switching
  sign (no sticking); the sim reproduces 178.70 deg with that model and
  prints both. The face, the swipe (54.14 deg up) and the 0.92 m/s grid
  flip (0.911 by bisection) are unchanged.
- The leave event is located by bisection on the RK4 sub-step inside the
  step (as sims/deskchain does), not by linear interpolation; the
  half-step rerun agrees within 6.4e-16 s.
- Readouts: the left clock reads "edge in N ms" before the edge, "N ms
  past the edge" after it and "landed at N ms" after touchdown (held);
  "turned", "spin" and "cm out" hold their touchdown values while the
  drawing settles. The right column shows "on the table" before the
  edge. The gold event rows sit right-aligned on the label row.
- The card's flip line says "the face flips at 0.86 m/s" (sim 0.862);
  the brief's card note says 0.87 (the first 0.01 step that lands up).
  The leave spins on the card are 8.89 and 2.45 rad/s (2.45 rounds to
  2.4 at one decimal, so two decimals are used).
- Voice made through a private copy of the Piper server (same code,
  binary and voice) because the shared service on 10303 failed; see
  Production.

## Niche note

[produced 2026-10-08 as "Does toast always land butter side down? No:
nudged lands down, swiped at 1.5 m/s lands up"; measured nudged 5 cm/s
leaves the corner at 193.2 ms (N zero) tilted 38.81 deg at 8.89 rad/s,
falls 0.3386 s, turns 211.22 deg, butter down 8.7 cm out; swiped 1.5
m/s clears the corner at 33.3 ms tilted 2.46 deg at 2.45 rad/s, falls
0.3614 s, turns 53.12 deg, butter up 59.2 cm out; flip 0.862 m/s (0.911
stick-slip grip 0.32 / 0.24, 12 cm toast 0.846); every speed up to 0.8
m/s lands down; task 20261008-102528]

## Upload

- Attempt 1 of 5 (quota day 2026-10-08T10:00 EEST) recorded at 2026-10-08T11:12:39+03:00 before scripts/yt-upload.py toast; zero attempts on record since the boundary.
- Attempt 1 failed before the insert at 11:12:39 (HTTP 401 Invalid Credentials on channels.list; the stored access token had expired 2026-09-19; forced refresh at 11:13:02 succeeded, token.json rewritten). Attempt 2 of 5 recorded at 2026-10-08T11:13:19+03:00 before scripts/yt-upload.py toast.
- Attempt 2 raised HTTP 410 Gone in request.next_chunk() at 11:13, but the uploads playlist and videos.list at 11:16 show private video sQp6CqF01is (created 08:13:21Z, uploadStatus uploaded, fileSize 3016476 = final.mp4, processing). The insert succeeded; 1,600 units counted. QA gate started with scripts/yt-qa.py toast sQp6CqF01is --wait --publish at 2026-10-08T11:16:18+03:00.
- Stub sQp6CqF01is never finished processing (uploadStatus uploaded, processingStatus processing, P0D, no streams at 11:41:49, 28 min after creation). Slot 1 marked processing timeout; toast is queued for a replacement upload as attempt 5 after bookstack and pencil.
- Toast replacement upload cancelled: attempt 3 (bookstack) failed on a 401, so only two attempts remain for bookstack and pencil. Slot 1 slips today unless the owner frees quota.
- Slipped 2026-10-08T13:57:50+03:00: stub sQp6CqF01is still unprocessed; no replacement attempt was possible. final.mp4 (md5 0737689dea46a6f6f000eb29a9f5a097) is ready to upload on the next quota day; delete the stub (videos.delete, 50 units) once a good copy is public. Gate: upload (410 on the media PUT, stub never finalized).
- Day 41 (quota day 2026-10-09T10:00 EEST): raw probe at 10:02 read 0 of 10 rejected; stub sQp6CqF01is still unprocessed after 26 h. Attempt 1 of 5 recorded at 2026-10-09T10:03:18+03:00 before scripts/yt-upload.py toast; zero attempts on record since the boundary.
- Uploaded private as YD1H8hALGew at 2026-10-09T07:03:25Z (videos.insert 1,600 units). yt-qa.py --wait --publish: gate 15 of 15 on the first processed read, published at 2026-10-09T10:04:11+03:00, re-read public, 54 units. https://youtu.be/YD1H8hALGew
