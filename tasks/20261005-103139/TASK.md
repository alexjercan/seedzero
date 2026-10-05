# Produce short: cart on a ramp, fired straight up or square to the ramp, does the ball land back in the cup

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day37

## Goal

Backlog idea (trend research 2026-10-05, task 20261005-100712, pillar 2
chaos and physics, everyday mechanics; read the full entry under "Added
by trend research 2026-10-05" in docs/niche.md): cart on a ramp. A cart
rolling down a ramp fires a ball; fired straight up (vertical) the ball
lands behind the cart, fired square to the ramp it lands back in the
cup.

Orchestrator notes (2026-10-05, before this brief; closed forms in
/tmp/day37/closed-cartramp.py with the log in /tmp/day37/closed-cartramp.log,
g = 9.807; the research agent's own measurement in /tmp/day37/research/).
The model: a 1.00 kg cart with light wheels and no friction (say so) is
let go from rest at the top of a 30 degree ramp 1.80 m long; it rolls at
g sin a = 4.9035 m/s^2 along the ramp (its normal force M g cos a = 8.493
N stays positive); 30 cm down the ramp it passes a trigger, at 0.3498 s
moving 1.7153 m/s, and its spring launcher fires a 50 g ball at u = 2.00
m/s relative to the cart; the ball then flies freely at g with no air
drag (say so). Top band: the launcher points straight up (vertical in the
lab). The ball's velocity relative to the cart has an up-slope part u sin
a = 1.000 m/s and a part square to the ramp u cos a = 1.732 m/s; in the
cart's frame, which accelerates down the slope at g sin a, the along-slope
pull of gravity is cancelled, so the ball keeps its 1.000 m/s up-slope
drift while gravity square to the ramp (g cos a) brings it back in 2 u
cos a / (g cos a) = 2 u / g = 0.4079 s, 17.66 cm above the ramp at the
top; the launch kicks the cart 0.050 m/s down-slope (m u sin a / M, the
square part absorbed by the ramp), so the ball lands on the ramp 42.83 cm
up-slope of the cart (closed form 2 u^2 sin a (1 + m / M) / g = 0.4283 m;
0.4079 m without the recoil, print both); the cart is then 1.1279 m past
the trigger at 3.765 m/s. Bottom band: the launcher points square to the
ramp; the ball has no up-slope drift relative to the cart, flies 2 u /
(g cos a) = 0.4710 s to 23.55 cm above the ramp and drops dead into the
cup (miss 0 to 1e-9 m); the cart is 1.3517 m past the trigger at 4.025
m/s (no recoil along the slope; the recoil square to the ramp presses the
cart into the ramp). Both carts reach a stop pad at the foot of the ramp
(1.80 m from the top) and stop there (no bounce, say so). Integrate both
bands in the lab frame with RK4 at dt = 1e-4 s (cart along the ramp, ball
in free flight; find the landing on the ramp line by bisection to 1e-9
s), as a check against the closed forms (a half-step rerun agreeing
within 1e-9 s); print the miss along the ramp, the flight times, the
apexes, the cart positions and speeds, the normal force, the ball's
energy in flight (kinetic plus potential, constant to 1e-12), the
momentum balance of the launch, and the position table at 0.1 s steps
after the trigger for both bands (cart distance past the trigger, ball
height above the ramp, ball along-slope position relative to the cart).

Checks, not facts (the sim must print and compare; state them as checks):
trigger at 0.3498 s, 1.7153 m/s; vertical launch: flight 0.4079 s, apex
17.66 cm, lands 42.83 cm behind the cart (40.79 cm without recoil), cart
1.1279 m past the trigger at 3.765 m/s; square launch: flight 0.4710 s,
apex 23.55 cm, miss 0.00 cm, cart 1.3517 m past the trigger at 4.025 m/s;
normal force 8.493 N; vertical panel table (cart past the trigger / ball
above the ramp at 0.1, 0.2, 0.3, 0.4079 s): 0.201 / 0.131, 0.451 / 0.177,
0.750 / 0.137, 1.128 / 0.000 m (print the exact figures); for the
description: 20 deg: 29.3 cm, 45 deg: 60.6 cm, u 1.5 m/s: 24.1 cm, u 3.0
m/s: 96.4 cm, a 5 kg cart: 41.2 cm, from rest at the trigger (no roll
before the launch): still 42.8 cm behind and still dead in the cup (the
miss does not depend on the cart's speed; print it as a check). Print
the schedule in video time, the text widths and the layout clearances.

Drawing: two-band layout (sims/deskchain and sims/wedge style, today's
wedge sim draws a 30 degree slope; read it), side view, the vertical
launch on top (the "no" case) and the square launch below; same scale,
same clock. Scale 400 px per metre: the ramp descends left to right,
1.80 m long (624 px of run, 360 px of rise), its top at the band's left
near x 80, a trigger mark 30 cm down the slope, a stop pad at the foot;
the cart a 40 px box with wheels and an open cup on top riding on the
ramp, the launcher a short tube on the cart (vertical in the top band,
square to the ramp in the bottom band); the ball 16 px; the ball's
flight as a faint dotted lab path left behind it; a dashed gold mark on
the ramp where the ball lands in the top band (43 cm up-slope of the
cart at that instant, 171 px along the slope) and a small splash of the
landing; in the bottom band the ball drops into the cup. Keep the apex
(94 px above the ramp) and the cart at the stop pad inside the band. Label
rows (40 px, coloured): "fired straight up" (coral) and "fired square to
the ramp" (teal). Readouts (28 px): left column "cart: N.NN m down the
ramp" and the clock; right column "ball: NN.N cm above the ramp" and
"gap: NN.N cm" (the along-slope gap between ball and cart; 0 in the
bottom band). Gold event rows: top "straight up: lands 43 cm behind the
cart" (lit at the landing and held), bottom "square to the ramp: dead in
the cup" (lit and held). Shown at 1/4 speed; cycle 8 s (480 frames):
release at 0.5 s of the cycle, the trigger at 0.5 + 4 * 0.3498 = 1.90 s,
landings at 1.90 + 4 * 0.4079 = 3.53 s (top) and 1.90 + 4 * 0.4710 = 3.78
s (bottom), the carts reach the stop pad later (print when), hold, reset
by a crossfade over the last 0.6 s of the cycle; 5 cycles in 40 s,
exactly periodic, the last frame equal to the first. The legend row after
the title: "same cart, same ramp, same ball, 1/4 speed"; the shared clock
in real seconds since the release. Overlay: "1 kg cart, 30 deg ramp |
ball 2 m/s | no seed" (measure it; shorten if over 950 px).

Day thirty-seven, third slot. Chosen by the research run because the
howitzer cart is a popular short, the incline version is debated online
("ahead, behind or in the cart"), the two panels end visibly differently
(a ball on the ramp 43 cm behind one cart, a ball in the cup of the
other), the number is exact and the repeat is a natural loop. Question in
the first two seconds: "A cart rolls down a ramp and fires a ball
straight up. Does it land back in the cart?" is long; prefer "Fire a ball
straight up from a rolling cart. Does it land back in the cup?" or "Does
the ball land back in the cart?" after a short setup; pre-test the
variants and keep the question identical in the title, the hook and the
payoff. Setup number: thirty degrees (the ramp; "two meters a second" for
the ball may go to the overlay and card). Payoff: no, it lands forty
three centimeters behind the cart; fired square to the ramp it lands dead
in the cup (speak at most two numbers in the payoff beat; "forty three
centimeters" is the one payoff number; the flight times 0.41 and 0.47 s
go to the card). The mechanism sentence must follow the picture: while
the ball is in the air the cart keeps speeding up down the slope and runs
out from under it; fired square to the ramp the ball shares the cart's
roll exactly and comes straight back down into the cup (never "pull" as
a noun; "frame of reference" stays out of the narration). Whisper risks:
"cart" (whisper may hear "card"; pre-test; "trolley" is the fallback, and
the title can keep "cart"), "ramp" (pre-test), "square to the ramp"
(pre-test; "straight out from the ramp" is the fallback), "forty three
centimeters" (pre-test), "cup" (pre-test), "fires" and "fired" (pre-test;
"shoots" is the fallback), avoid "do you", avoid "fly" and "flies"
(digit 5), avoid "pull" as a noun. Pre-test hooks with
scripts/voiceover.sh and keep the one whose question lands earliest
under two seconds. Measure every fixed text line with PIL before
rendering and keep every line under 950 px, and the title under 100
characters with no < or >. Music seed 114. Templates: sims/deskchain
(two-band layout, asserts, the clock, the crossfade; read it whole),
sims/wedge (today's 30 degree slope drawing, event rows; read it),
sims/monkeyhunter (a launched ball with a dotted flight path),
sims/uphill (a slope with an object). Sim name cartramp:
sims/cartramp/cartramp.py, projects/cartramp/, media/cartramp/.

## Claim (expected; the sim's numbers replace these)

A 1 kg cart rolling without friction down a 30 degree ramp fires a 50 g
ball at 2 m/s relative to itself as it passes a trigger 30 cm down.
Fired straight up, the ball flies 0.408 s to 17.7 cm above the ramp and
lands 42.8 cm up the ramp behind the cart, because the cart keeps
speeding up down the slope while the ball drifts up-slope at 1 m/s
relative to it (2 u^2 sin a (1 + m / M) / g, 40.8 cm without the 0.05
m/s recoil). Fired square to the ramp, the ball flies 0.471 s to 23.6 cm
and lands dead in the cup, because in the cart's frame gravity along the
slope is cancelled. Narrated: thirty degrees (setup); no, forty three
centimeters behind; square to the ramp, dead in the cup (payoff). Card:
the question; the answer with 43 cm behind against dead in the cup;
flights 0.41 and 0.47 s; apex 17.7 and 23.6 cm; the miss does not depend
on the cart's speed; 45 deg: 61 cm. Description: the model statement,
the equations, the two runs, the angle, speed and mass variants, the
checks.

## Claim

A 1 kg cart with light wheels and no friction rolls from rest down a 30
degree ramp 1.8 m long and, 30 cm down (0.3498 s, 1.7153 m/s), fires a
50 g ball at 2 m/s relative to itself. Fired straight up, the ball is in
the air 0.4079 s, rises 17.66 cm above the ramp and lands 42.83 cm up
the ramp behind the cart (40.79 cm without the 0.050 m/s recoil kick):
the cart keeps speeding up down the slope and runs out from under the
ball, which keeps a 1.000 m/s up-slope drift relative to the cart. Fired
square to the ramp, the ball is in the air 0.4710 s, rises 23.55 cm and
lands dead in the cup (miss 1.4e-11 cm): in the cart's frame the
along-slope pull of gravity is cancelled. The miss does not depend on the
cart's speed (from rest at the trigger: still 42.83 cm, still dead in the
cup). Narrated: thirty degree ramp, shown four times slower (setup);
square to the ramp, yes, dead in the cup; fired straight up, no, forty
three centimeters behind the cart (payoff). Card: the question; 42.8 cm
behind against dead in the cup; air 0.41 and 0.47 s; up 17.7 and 23.5
cm; same miss from rest at the trigger; 45 deg 60.6 cm, 5 kg cart 41.2
cm.

## Evidence

### Measurements

Sim: sims/cartramp/cartramp.py with projects/cartramp/manifest.json
(RK4 at dt = 1e-4 s in the lab frame, bisection for the trigger, apex,
landing and foot, half-step rerun, closed forms; deterministic, no seed,
no wall clock). Log: media/cartramp/measure.log (exit 0; the full final
log follows).

Brief checks (the sim prints "checks against the brief (33 checks, 0
failed)"): trigger 0.3498 s / 1.7153 m/s (sim 0.349802 s, 1.715255
m/s); cart acceleration 4.9035 m/s^2; normal force 8.493 N (8.4931 N);
vertical flight 0.4079 s (0.407872 s), apex 17.66 cm (17.6614 cm), miss
42.83 cm (42.8266 cm; closed form diff +1.7e-11 cm), 40.79 cm without
recoil (40.7872 cm), cart 1.1279 m at 3.765 m/s (1.127870 m, 3.765255
m/s); square flight 0.4710 s (0.470970 s), apex 23.55 cm (23.5485 cm),
miss 0 (1.4e-11 cm), cart 1.3517 m at 4.025 m/s (1.351663 m, 4.024656
m/s); up-slope drift 1.000 m/s, square part 1.732 m/s, recoil kick
0.050 m/s; vertical table 0.201 / 0.131, 0.451 / 0.177, 0.750 / 0.137,
1.128 / 0.000 m (sim 0.2010 / 0.1307, 0.4511 / 0.1765, 0.7502 / 0.1374,
1.1279 / 0.0000 m); description: 20 deg 29.3 cm (29.30), 45 deg 60.6 cm
(60.57), 1.5 m/s 24.1 cm (24.09), 3 m/s 96.4 cm (96.36), 5 kg cart 41.2
cm (41.20), from rest 42.8 cm (42.83) and square miss 3.3e-12 cm. Also
printed: energy in flight within 9.6e-15 J (top) and 1.9e-14 J (bottom);
momentum along the slope 1.801018 kg m/s before and after the launch;
half-step rerun within 2.7e-15 s (top) and 4.7e-14 s (bottom); the carts
reach the stop pad 0.5011 s (4.2222 m/s) and 0.5070 s (4.2015 m/s)
after the trigger; the schedule, the text widths (every line under 950
px, max 922 px for payoff line 3) and the layout clearances.

Final measure.log:

```
Mon Oct  5 10:56:52 AM EEST 2026
warning: Git tree '/home/alex/personal/seedzero' is dirty
setup: side view, two panels on one clock, the same ramp drawn the same way at the same scale: a 1 kg cart with light wheels and no friction is let go from rest at the top of a 30 degree ramp 1.8 m long (90 cm of drop, 155.9 cm of run); it rolls at g sin a = 4.9035 m/s^2 and its normal force M g cos a = 8.493 N stays positive; 30 cm down the ramp it passes a trigger and its spring launcher fires a 50 g ball at u = 2 m/s relative to the cart's velocity at that instant (the ball's lab velocity is the cart's plus u along the tube; the cart takes the opposite along-slope impulse; the impulse square to the ramp is absorbed by the ramp); the ball then flies freely at g = 9.807 m/s^2 with no air drag; top panel the tube points straight up (vertical in the lab), bottom panel square to the ramp; after the landing the top ball rests at its landing point and the bottom ball in the cup; both carts roll on to a stop pad at the foot of the ramp (1.8 m from the top) and stop there (no bounce; the stop itself is not modelled); the cart and the ball are points on the ramp line for every measurement and are drawn larger than life; both bands integrated by classical RK4 at 10000 steps per second (dt = 1e-04 s) in the lab frame, the trigger, the apex, the landing on the ramp line and the foot located by bisection inside the step, checked against the closed forms and a half-step rerun; shown at 1/4 speed on a 8 s cycle (480 frames) with the release 0.5 s into the cycle, 5 cycles in 40 s; drawn at 340 px per metre (the ramp 530 px of run and 306 px of rise, the ball 16 px); deterministic, no seed
trigger: the cart from rest reaches the trigger 30 cm down the ramp at 0.349802 s = 0.3498 s moving 1.715255 m/s = 1.7153 m/s (closed form sqrt(2 d / (g sin a)) = 0.349802 s, g sin a t = 1.715255 m/s; diffs +7.0e-15 s, -4.6e-14 m/s), 3498 steps; the normal force on the cart M g cos a = 8.4931 N = 8.493 N, positive, so the cart stays on the ramp
straight up (top panel): the ball's velocity relative to the cart has an up-slope part u sin a = 1.0000 m/s and a part square to the ramp u cos a = 1.7321 m/s; the launch kicks the cart m u sin a / M = 0.0500 m/s down the slope (the square part m u cos a = 0.0866 kg m/s goes into the ramp); RK4: the ball is in the air 0.407872 s = 0.4079 s (closed form 2 u / g = 0.407872 s, diff +6.6e-15 s), reaches 17.6614 cm = 17.66 cm above the ramp line at 0.2039 s (closed form 17.6614 cm, diff +8.1e-13 cm) and comes down on the ramp line 69.9604 cm past the trigger while the cart is 1.127870 m = 1.1279 m past the trigger at 3.765255 m/s = 3.765 m/s (closed form 1.127870 m, 3.765255 m/s; diffs +1.3e-13 m, +6.7e-13 m/s): the ball lands 42.8266 cm = 42.83 cm = 43 cm up the slope behind the cart (closed form 2 u^2 sin a (1 + m / M) / g = 42.8266 cm, diff +1.7e-11 cm); the ball's energy in flight (kinetic plus potential) stays within 9.6e-15 J of its launch value; momentum along the slope at the launch: before (M + m) v = 1.801018 kg m/s, after M V + m v_ball = 1.801018 kg m/s (diff +0.0e+00); the cart reaches the stop pad at the foot 0.501051 s = 0.5011 s after the trigger at 4.2222 m/s (closed form 0.501051 s, 4.2222 m/s) and stops; 8509 steps; half-step rerun (dt = 5e-05 s): in the air 0.407871928 s (+2.7e-15 s), lands 42.826552463 cm behind (-2.7e-11 cm); drawing: the ball's centre is drawn 23.9 px above the ramp surface in the cup, so the drawn flight is sheared linearly in time by 15.9 px = 4.68 cm square to the ramp (a constant velocity offset of 0.1149 m/s, so the drawn path is still a parabola) and the drawn ball lands on the measured mark with its centre 8 px above the surface; the readouts and the mark are the model's
square to the ramp (bottom panel): the ball's velocity relative to the cart is all square to the ramp, u = 2.0000 m/s, with no along-slope part (0.0e+00 m/s), so the cart gets no along-slope kick (-0.0e+00 m/s; the impulse m u = 0.1000 kg m/s presses the cart into the ramp); RK4: the ball is in the air 0.470970 s = 0.4710 s (closed form 2 u / (g cos a) = 0.470970 s, diff +2.8e-14 s), reaches 23.5485 cm = 23.55 cm above the ramp line at 0.2355 s (closed form 23.5485 cm, diff +9.4e-13 cm) and comes down on the ramp line 135.1663 cm past the trigger while the cart is 1.351663 m = 1.3517 m past the trigger at 4.024656 m/s = 4.025 m/s (closed form 1.351663 m, 4.024656 m/s; diffs +2.5e-13 m, +8.6e-13 m/s): the ball lands 1.40e-11 cm from the cart along the slope: dead in the cup (miss 1.4e-13 m) (closed form 0 = -0.0000 cm, diff +1.4e-11 cm); the ball's energy in flight (kinetic plus potential) stays within 1.9e-14 J of its launch value; momentum along the slope at the launch: before (M + m) v = 1.801018 kg m/s, after M V + m v_ball = 1.801018 kg m/s (diff -2.2e-16); the cart reaches the stop pad at the foot 0.507035 s = 0.5070 s after the trigger at 4.2015 m/s (closed form 0.507035 s, 4.2015 m/s) and stops; 8708 steps; half-step rerun (dt = 5e-05 s): in the air 0.470969935 s (-4.7e-14 s), lands -0.000000000 cm behind (-2.8e-11 cm); drawing: the ball's centre is drawn 25.0 px above the ramp surface in the cup and comes back to the same point, no shear needed
table vertical (RK4 table, real time after the trigger): 0.0000 s: cart 0.0000 m past the trigger, ball 0.00 cm above the ramp line and 0.00 cm up-slope of the cart; 0.1000 s: cart 0.2010 m past the trigger, ball 13.07 cm above the ramp line and 10.50 cm up-slope of the cart; 0.2000 s: cart 0.4511 m past the trigger, ball 17.65 cm above the ramp line and 21.00 cm up-slope of the cart; 0.3000 s: cart 0.7502 m past the trigger, ball 13.74 cm above the ramp line and 31.50 cm up-slope of the cart; 0.4000 s: cart 1.0984 m past the trigger, ball 1.34 cm above the ramp line and 42.00 cm up-slope of the cart; 0.4079 s: cart 1.1279 m past the trigger, ball 0.00 cm above the ramp line and 42.83 cm up-slope of the cart
table square (RK4 table, real time after the trigger): 0.0000 s: cart 0.0000 m past the trigger, ball 0.00 cm above the ramp line and 0.00 cm up-slope of the cart; 0.1000 s: cart 0.1960 m past the trigger, ball 15.75 cm above the ramp line and 0.00 cm up-slope of the cart; 0.2000 s: cart 0.4411 m past the trigger, ball 23.01 cm above the ramp line and 0.00 cm up-slope of the cart; 0.3000 s: cart 0.7352 m past the trigger, ball 21.78 cm above the ramp line and 0.00 cm up-slope of the cart; 0.4000 s: cart 1.0784 m past the trigger, ball 12.06 cm above the ramp line and 0.00 cm up-slope of the cart; 0.4710 s: cart 1.3517 m past the trigger, ball 0.00 cm above the ramp line and 0.00 cm up-slope of the cart
for the description: straight up without the recoil kick (the cart's speed unchanged by the launch): the ball lands 40.79 cm behind the cart (closed form 2 u^2 sin a / g = 40.79 cm), the cart 1.1075 m past the trigger at 3.715 m/s; 20 degree ramp (the same trigger 30 cm down, reached at 0.4229 s at 1.4186 m/s; the ramp long enough): straight up the ball is in the air 0.4079 s, 19.16 cm high, and lands 29.30 cm = 29.3 cm behind the cart (closed form 29.30 cm); square to the ramp 0.4340 s, 21.70 cm high, miss 5.3e-12 cm; 45 degree ramp (the same trigger 30 cm down, reached at 0.2941 s at 2.0398 m/s; the ramp long enough): straight up the ball is in the air 0.4079 s, 14.42 cm high, and lands 60.57 cm = 60.6 cm behind the cart (closed form 60.57 cm); square to the ramp 0.5768 s, 28.84 cm high, miss 5.2e-11 cm; ball at 1.5 m/s (30 degrees, the ramp long enough): straight up in the air 0.3059 s, 9.93 cm high, lands 24.09 cm = 24.1 cm behind the cart (closed form 24.09 cm); square to the ramp 0.3532 s, 13.25 cm high, miss 1.0e-11 cm; ball at 3 m/s (30 degrees, the ramp long enough): straight up in the air 0.6118 s, 39.74 cm high, lands 96.36 cm = 96.4 cm behind the cart (closed form 96.36 cm); square to the ramp 0.7065 s, 52.98 cm high, miss 1.2e-11 cm; a 5 kg cart (the same 50 g ball at 2 m/s): the kick drops to 0.0100 m/s and the straight-up ball lands 41.20 cm = 41.2 cm behind (closed form 41.20 cm); square to the ramp miss 1.4e-11 cm; launched from rest at the trigger (no roll before the launch, the cart at 0 m/s): straight up the ball is in the air 0.4079 s and still lands 42.83 cm = 42.8 cm behind the cart (the cart 0.4283 m past the trigger at 2.050 m/s); square to the ramp still dead in the cup (miss 3.3e-12 cm): the miss does not depend on the cart's speed
checks against the brief (33 checks, 0 failed): trigger at (s): brief 0.3498, sim 0.349802, diff +2.2e-06: ok; trigger speed (m/s): brief 1.7153, sim 1.71526, diff -4.5e-05: ok; cart a (m/s^2): brief 4.9035, sim 4.9035, diff -8.9e-16: ok; normal force (N): brief 8.493, sim 8.49311, diff +1.1e-04: ok; vertical flight (s): brief 0.4079, sim 0.407872, diff -2.8e-05: ok; vertical apex (cm): brief 17.66, sim 17.6614, diff +1.4e-03: ok; vertical miss (cm): brief 42.83, sim 42.8266, diff -3.4e-03: ok; vertical miss, no recoil (cm): brief 40.79, sim 40.7872, diff -2.8e-03: ok; vertical cart past the trigger (m): brief 1.1279, sim 1.12787, diff -3.0e-05: ok; vertical cart speed (m/s): brief 3.765, sim 3.76526, diff +2.6e-04: ok; square flight (s): brief 0.471, sim 0.47097, diff -3.0e-05: ok; square apex (cm): brief 23.55, sim 23.5485, diff -1.5e-03: ok; square miss (cm): brief 0, sim 1.39888e-11, diff +1.4e-11: ok; square cart past the trigger (m): brief 1.3517, sim 1.35166, diff -3.7e-05: ok; square cart speed (m/s): brief 4.025, sim 4.02466, diff -3.4e-04: ok; up-slope drift (m/s): brief 1, sim 1, diff -1.1e-16: ok; square part (m/s): brief 1.732, sim 1.73205, diff +5.1e-05: ok; recoil kick (m/s): brief 0.05, sim 0.05, diff -6.9e-18: ok; vertical table 0.1 s cart (m): brief 0.201, sim 0.201043, diff +4.3e-05: ok; vertical table 0.1 s ball (m): brief 0.131, sim 0.13074, diff -2.6e-04: ok; vertical table 0.2 s cart (m): brief 0.451, sim 0.451121, diff +1.2e-04: ok; vertical table 0.2 s ball (m): brief 0.177, sim 0.176548, diff -4.5e-04: ok; vertical table 0.3 s cart (m): brief 0.75, sim 0.750234, diff +2.3e-04: ok; vertical table 0.3 s ball (m): brief 0.137, sim 0.137425, diff +4.3e-04: ok; vertical table 0.4079 s cart (m): brief 1.128, sim 1.12787, diff -1.3e-04: ok; vertical table 0.4079 s ball (m): brief 0, sim -8.57445e-09, diff -8.6e-09: ok; 20 deg miss (cm): brief 29.3, sim 29.2951, diff -4.9e-03: ok; 45 deg miss (cm): brief 60.6, sim 60.5659, diff -3.4e-02: ok; u 1.5 m/s miss (cm): brief 24.1, sim 24.0899, diff -1.0e-02: ok; u 3 m/s miss (cm): brief 96.4, sim 96.3597, diff -4.0e-02: ok; 5 kg cart miss (cm): brief 41.2, sim 41.1951, diff -4.9e-03: ok; from rest miss (cm): brief 42.8, sim 42.8266, diff +2.7e-02: ok; from rest square miss (cm): brief 0, sim 3.30846e-12, diff +3.3e-12: ok
schedule (video time, 1/4 speed): cycles of 8 s start at -1.00, 7.00, 15.00, 23.00, 31.00, 39.00 s (the first 1.00 s before the first frame); both carts are let go 0.5 s into each cycle at 7.50, 15.50, 23.50, 31.50, 39.50 s (the stop pins fade over 0.3 s); both pass the trigger and fire 1.40 s after the release at 0.90, 8.90, 16.90, 24.90, 32.90 s; the straight-up ball lands 1.63 s after the launch at 2.53, 10.53, 18.53, 26.53, 34.53 s (3.53 s into the cycle; its event row lights with a 0.3 s splash); the square ball drops into the cup 1.88 s after the launch at 2.78, 10.78, 18.78, 26.78, 34.78 s (3.78 s into the cycle; its event row lights); the top cart reaches the stop pad at 2.90, 10.90, 18.90, 26.90, 34.90 s (3.90 s into the cycle) and the bottom cart at 2.93, 10.93, 18.93, 26.93, 34.93 s (3.93 s into the cycle); the reset crossfade runs over the last 0.6 s of each cycle (from 6.40, 14.40, 22.40, 30.40, 38.40 s; the readouts out over its first half and in over its second); on the first frame the cycle is 1.00 s in (0.125 s real after the release: the carts rolling at 0.038 m, the top ball cup at 0.0 cm up, 0.0 cm behind; the bottom ball cup at 0.0 cm up); title until 3 s; payoff card from 33.6 s; the title fades back in over the last 0.5 s and the last frame repeats the first (the scene is periodic: 40 s holds exactly 5 cycles)
text widths (the on-screen strings verbatim): overlay@34 846 px '1 kg cart, 30 deg ramp | ball 2 m/s | no seed', title line 1@56 702 px 'Fired straight up from', title line 2@56 858 px 'a rolling cart: does the ball', title line 3@56 673 px 'land back in the cup?', legend@40 752 px 'same cart, same ramp, 1/4 speed', clock@28 390 px '1.125 s after the release', clock held@28 194 px 'held, at rest', label vertical@40 370 px 'fired straight up', cart vertical@28 440 px 'cart: 1.80 m down the ramp', air vertical@28 268 px 'in the air 0.408 s', flight vertical@28 208 px 'flight 0.408 s', gap vertical@40 292 px 'gap: 42.8 cm', height vertical@28 253 px 'ball: 17.7 cm up', speed vertical@28 312 px 'cart speed 4.22 m/s', event vertical@40 718 px 'no: lands 43 cm behind the cart', label square@40 554 px 'fired square to the ramp', cart square@28 440 px 'cart: 1.80 m down the ramp', air square@28 268 px 'in the air 0.471 s', flight square@28 208 px 'flight 0.471 s', gap square@40 264 px 'gap: 0.0 cm', height square@28 253 px 'ball: 23.5 cm up', speed square@28 312 px 'cart speed 4.20 m/s', event square@40 458 px 'yes: dead in the cup', cup@28 226 px 'ball in the cup', trigger@24 94 px 'trigger', gap mark@24 81 px '43 cm', payoff line 1@40 787 px 'does the ball land back in the cup?', payoff line 2@40 905 px 'straight up: no, 42.8 cm behind the cart', payoff line 3@40 922 px 'square to the ramp: yes, dead in the cup', payoff line 4@40 911 px 'air 0.41 and 0.47 s; up 17.7 and 23.5 cm', payoff line 5@40 780 px 'same miss from rest at the trigger', payoff line 6@40 800 px '45 deg: 60.6 cm; 5 kg cart: 41.2 cm'
row check: the left column ends at x 594 px, the right column starts at x 728 px; both end 134 px under the band top; the event rows span 152 to 192 px under the band top, right-aligned at x 1040 from x 322 (top, 718 px) and 582 (bottom, 458 px); the ramp's drawn top at x 80, 190 px under the band top, the cart's start (s = 0) at x 106.0, 205.0 px, the foot (s = 1.8 m) at x 636.0, 511.0 px, the plank's lower end corner at x 659.4, 538.4 px, the stop pad's top corner at x 683.6, 508.5 px, the legs' feet at y 317 and 453 px; the tube's top at the start is 162.3 px (top band) and 159.0 px (bottom band) under the band top; the drawn ball paths rise to 206.9 px (top) and 213.1 px (bottom) under the band top, and over the event rows' x range to 224.0 and 398.9 px; the landing mark at x 400.3, 374.9 px and the cart's position at that instant at x 526.4, 447.7 px (146 px along the slope), the gap label at y 347 px under the band top; the trigger label at y 287 px; each band is 550 px tall (y 330 to 880 and 880 to 1430); the caption band starts at y 1440; the title rows end at y 330 and the overlay band ends at y 130
Mon Oct  5 10:56:54 AM EEST 2026
```

### Production

- Manifest: projects/cartramp/manifest.json (fps 60, 40 s, 1/4 speed,
  cycle 8 s, release 0.5 s into the cycle, first_cycle_at -1.0, reset
  crossfade 0.6 s, 340 px/m, ramp top at x 80 and 190 px under the band
  top, title until 3 s, payoff_t 33.6 s, hold 0.6 s, loop fade 0.5 s,
  music seed 114, music gain 0.18, voice offset 0.6, caption_y 0.75).
- Schedule (video time): releases 7.50, 15.50, 23.50, 31.50, 39.50 s;
  triggers 0.90, 8.90, 16.90, 24.90, 32.90 s; straight-up landings 2.53,
  10.53, 18.53, 26.53, 34.53 s; square landings 2.78, 10.78, 18.78,
  26.78, 34.78 s; carts at the stop pad 2.90/2.93 s and every 8 s;
  crossfades from 6.40, 14.40, 22.40, 30.40, 38.40 s. Frame 0: the carts
  rolling at 0.038 m, both balls in the cup, 0.125 s after the release.
- Smoke frames viewed: media/cartramp/smoke-{0.0,2.4,34.0,35.5}.png
  (also an earlier set at 0.0, 2.0, 3.4, 10.1 with first_cycle_at -1.5):
  frame 0 carts rolling with the balls in the cups under the title; 2.4
  s the top ball 0.375 s in the air 39.4 cm behind the cart; 34.0 the
  card rising with the balls mid-flight; 35.5 the landed state with the
  gold 43 cm mark, both gold event rows and the card.
- Render: media/cartramp/render.log, footage.mp4 (2400 frames, 27 s);
  loop check 0 px (max channel difference 0); periodicity check 0 px;
  loop step 2283 px between the last two frames.
- Hook pre-tests (media/cartramp/hooks/pretest.log): hook1 "Fired
  straight up from a rolling cart: does the ball land back in the cup?"
  ok, question ends 2.61 s of video; hook2 "Does the ball land back in
  the cup? A cart rolls down a ramp and fires it straight up." ok,
  question at 0.6 s; hook3 "A rolling cart fires a ball straight up.
  Does it land back in the cup?" ok, question at 2.96 s; hook4 "Fire a
  ball straight up from a rolling cart. Does it land back in the cup?"
  ok, 3.18 s; hook5 "Does it land back in the cup? A ball fired straight
  up from a cart rolling down a ramp." ok, 0.6 s. Chosen: the question
  first (hook2 form), spoken at 0.60 s. Word test: "cart", "ramp",
  "square to the ramp", "forty three centimeters", "cup", "fires",
  "trigger", "Partway down", "Every run the same" all matched;
  sentence-initial "Straight up, no." was heard as "trade", so the
  narration says "Fired straight up, no".
- Narration: projects/cartramp/narration.txt, 117 words. Voice: pass 1
  (107 words, ok, 31.47 s) then pass 2 with the final text (ok,
  34.99 s; media/cartramp/voice.log). Final voice ends at 35.59 s of
  video. Timing (media/cartramp/timing.log): question 0.60-4.86;
  "shown four times slower. Partway down, a trigger fires a ball from
  each" 5.88-10.39 (trigger at 8.90); "the cart keeps speeding up down
  the slope and runs out from under the ball" 15.30-19.03 (top landing
  18.53); "comes back down into the cup" to 24.94; "Does the ball land
  back in the cup? Fired square to the ramp. Yes." 24.94-28.79 (square
  landing 26.78); "the cart runs away" 31.27-32.60; "and the ball lands
  43 centimeters behind the cart" 32.60-35.59 (card from 33.6, top
  landing 34.53). 13 silences at -35 dB / 0.22 s.
- Compose: media/cartramp/compose.log: music seed 114, 40.00 s;
  captions 22 pauses detected, 22 matched, max chunk start shift
  0.911 s; final.mp4 40.000000 s.

### Local QA

- media/cartramp/final.mp4: md5 a047545c7db210364e0b34520f7add9a,
  4527257 bytes; ffprobe h264 1080x1920 60/1, aac 22050 Hz mono,
  duration 40.000000; moov at byte 36 before mdat at 44640 (faststart).
- Caption text against the narration: 37 drawtext chunks (the first is
  the overlay); the joined caption text equals the narration word for
  word (the only difference the typographic apostrophe in "cart's" that
  captions.py writes). The first caption "Does the ball land" is enabled
  from 0.797 s.
- signalstats YMAX on footage.mp4: caption band rows 1440-1530 = 28
  (background), overlay band rows 96-130 = 28: nothing drawn under the
  captions or the overlay.
- Full-resolution frames viewed (media/cartramp/qa-T.png): 0.00 overlay,
  three-row title, carts rolling at 0.04 m with the balls in the cups,
  no caption; 1.00 both balls just fired (0.025 s in the air), caption
  "Does the ball land"; 2.10 both balls in flight, "back in the cup?";
  8.00 legend and clock 0.125 s, carts just released, "Partway down, a";
  18.40 top ball 0.375 s in the air 39.4 cm behind the cart, bottom
  ball over its cart, "runs out from under"; 26.70 top ball at the
  landing with the splash ring and the dashed gold 43 cm span, event
  row "no: lands 43 cm behind the cart", bottom ball 0.450 s in the air
  about to drop into the cup, caption "cup?"; 34.00 card rising, balls
  mid-flight, caption "lands forty three"; 35.40 landed state, "flight
  0.408 s" and "flight 0.471 s", gold gap 42.8 cm and 0.0 cm, both event
  rows, card, caption "the cart."; 39.983 identical to frame 0 (title
  back, no caption). media/cartramp/sheet.png viewed: 40 cells, the
  captions in order, no clipping, the card from 33.6 s.
- Narrated numbers: "thirty degree ramp" (manifest angle_deg 30, log
  "30 degree ramp"), "four times slower" (1/4 speed), "forty three
  centimeters" (log "42.8266 cm = 42.83 cm = 43 cm"). Description
  numbers checked by script against measure.log (33 strings present;
  every square miss in the log at most 5.2e-11 cm).

### Metadata

projects/cartramp/metadata.json written by a Python script with asserts
(title 94 chars, description 2498 chars, 11 tags, ASCII, no < or >;
every description number present in measure.log). Title: "Fired
straight up from a rolling cart: does the ball land back in the cup? No,
43 cm behind it". privacyStatus private, categoryId 27,
containsSyntheticMedia true, selfDeclaredMadeForKids false.

### Deviations from the brief

- Scale 340 px/m with the ramp top 190 px under the band top (the
  brief's 400 px/m did not fit the 550 px band under three text rows);
  the ball 16 px as asked, the cart about 52 px long.
- Legend "same cart, same ramp, 1/4 speed" (the brief's "same cart, same
  ramp, same ball, 1/4 speed" measured 997 px). Event rows "no: lands 43
  cm behind the cart" and "yes: dead in the cup" (the brief's "straight
  up: lands 43 cm behind the cart" measured 912 px and crowded the
  gap readout). Right readout "ball: NN.N cm up" instead of "ball: NN.N
  cm above the ramp" (463 px collided with the left column).
- The drawn ball sits 23.9 px above the ramp surface in the cup, so the
  top band's drawn flight is sheared linearly in time by 15.9 px (4.68
  cm, a constant 0.1149 m/s offset, still a parabola) so that the drawn
  ball lands on the measured gold mark; the readouts and the mark are
  the model's (printed in measure.log).
- Question-first hook ("Does the ball land back in the cup?" at 0.60 s)
  with the three-row title "Fired straight up from a rolling cart: does
  the ball land back in the cup?"; the narration says "two carts" and
  "fires a ball from each" to match the two bands, and "Partway down"
  instead of a second setup number; "Fired straight up, no" instead of
  the sentence-initial "Straight up, no" (whisper heard "trade").
- Card lines shortened to fit under 950 px: "air 0.41 and 0.47 s; up
  17.7 and 23.5 cm", "same miss from rest at the trigger", "45 deg: 60.6
  cm; 5 kg cart: 41.2 cm".
- The narration is 117 words (34.99 s), above the 104-110 target, so
  that the "runs away" beat lands under the final run; the voice ends at
  35.59 s with the card up from 33.6 s.

## Niche note

Appended to the "Cart on a ramp" bullet in docs/niche.md (see the
bracketed note there).

## Upload

- Attempt 3 of 5 (quota day 2026-10-05T10:00 EEST) recorded at 2026-10-05T11:10:08+03:00 before scripts/yt-upload.py cartramp; two earlier attempts (wedge, spinglass, both succeeded).
- Uploaded private as 6FMt4nruGWc at 2026-10-05T11:10:11+03:00 (videos.insert 1,600 units). yt-qa.py --wait --publish: gate 15 of 15 on the first processed read, published at 2026-10-05T11:10:54+03:00, re-read public, 54 units. https://youtu.be/6FMt4nruGWc
