# Produce short: front-wheel drive up an icy hill, nose first or in reverse, which one climbs

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day42

## Goal

Backlog idea (trend research 2026-10-08, re-judged 2026-10-10 in task
20261010-100329, pillar 2 chaos and physics, road debates; read the
full "Front drive up an icy hill, nose first or reversing" bullet in
docs/niche.md): the same front-wheel-drive car starting up an icy hill
nose first beside backing up it; nose first it spins its wheels and
rolls back, in reverse it climbs.

Orchestrator notes (2026-10-10; closed forms in /tmp/day42/closed.py
with the log /tmp/day42/closed.log; research script
/tmp/day42/research/misc.py with misc.log; g = 9.807 m/s^2). Read
/tmp/day42/producer-conventions.md first. The model: a 1,300 kg
front-wheel-drive car, wheelbase L = 2.60 m, 60 / 40 front-to-rear
static split so the centre of mass is b = 1.56 m ahead of the rear axle
and h = 0.55 m up, grip mu = 0.3 on ice (all chosen, say so), starting
from rest on a theta = 10 degree hill with the driver flooring it so the
driven (front) wheels spin and deliver mu N_front uphill. Loads from
the slope and the acceleration a (positive uphill along the slope):
N_front = m g cos theta (b / L) -/+ m (g sin theta + a) (h / L), the
minus sign NOSE FIRST (the front axle uphill, unloaded by the pitch) and
the plus sign REVERSING (the front axle downhill, loaded); N_rear = m g
cos theta - N_front; a = mu N_front / m - g sin theta, solved exactly
(x = N_front / (m g) = (b / L) cos theta / (1 +/- mu h / L)). Top band
NOSE FIRST: a = -0.0683 m/s^2, the wheels spin forward while the car
slides back 0.85 m in 5 s. Bottom band REVERSING: a = +0.1533 m/s^2, it
climbs 1.92 m in 5 s. Integrate both with RK4 (constant acceleration,
so the check against the closed form is 1e-9) and print the axle loads,
the steepest hill each way, the variants for the description and the
schedule.

Checks, not facts (the sim must print and compare): nose first front
load 0.556 W (0.5556), a = -0.0683 m/s^2, -0.85 m at 5 s; reversing
0.631 W (0.6309), a = +0.1533 m/s^2, +1.92 m at 5 s; steepest hills
atan(mu b / (L + mu h)) = 9.61 deg nose first and atan(mu b / (L - mu
h)) = 10.88 deg reversing (grip 0.2: 6.57 and 7.14; grip 0.4: 12.48 and
14.69; rear-wheel drive nose first 7.30; all-wheel drive atan(mu) =
16.70); both axle loads positive in both runs and summing to m g cos
theta; the undriven axle rolls freely (no traction from it); RK4 within
1e-9 m of the closed form; the window between the two limits is 1.27
degrees wide and the 10 degree hill sits inside it (state that the
answer depends on the chosen grip, split and height).

Drawing: two-band side view (sims/deskchain layout, bands y 330 to 880
and 880 to 1430; sims/hump draws a car on a road profile; sims/wedge
draws a slope with force arrows; read them), the same 10 degree slope
rising to the right in both bands at 300 px per metre (the road a
thick line from x 60 at the band bottom-left rising at 10 degrees; the
car a 4.2 m = 126 px body with two wheels on the slope, starting with
its centre at x 300 on a start line painted across the road; the front
axle in teal and marked DRIVEN, its wheel drawn with a spoke that spins
fast when the wheels spin and a small spray of ice marks behind it); in
the top band the car faces uphill, in the bottom band it faces downhill
and backs up; a load bar under each band ("front 56 %" and "front 63
%", live from the sim), a readout "moved -0.85 m" / "moved +1.92 m"
(live, signed, uphill positive) and the clock; a thin trail of the
car's centre. Label rows (40 px, coloured): "nose first" (coral) and
"in reverse" (teal), both "front-wheel drive, 10 degree ice". Gold
event rows: top "nose first: rolled back 0.85 m in 5 s", bottom "in
reverse: climbed 1.92 m in 5 s" (lit at 5 s of the run, held). Real
time, cycle 8 s (480 frames): throttle at 0.5 s into the cycle (both
cars at rest on the start line before it, a throttle marker rising:
motion in frame one), the readouts frozen at 5.5 s, hold to 7.5 s,
crossfade reset over the last 0.5 s; 5 cycles in 40 s, exactly
periodic, the last frame equal to the first. Keep the slope angle
geometrically true (10 degrees), so the 1.92 m climb shows as 576 px
along the road: check the car stays inside the band (assert). Legend
row after the title: "same car, same hill, real time". Overlay: "1,300
kg front drive, grip 0.3 | no seed" (measure it).

Day forty-two, third slot. Chosen because the "back up the icy hill"
debate is an everyday car argument, cars have done well on the channel
(brake or swerve 734, banked road 366), the two cars end visibly apart
(one below the line, one well above it), and the start repeats as a
loop. Question in the first two seconds: "Front-wheel drive on an icy
hill: nose first, or in reverse?" (pre-test; it is the first sentence;
"Icy hill: drive up it, or back up it?" is the fallback). Keep the
question identical in the title, the hook and the payoff. Setup number:
"a ten degree hill" (one setup number only; the grip, the mass and the
split go to the overlay, card and description). Payoff: "Nose first it
rolls back. In reverse it climbs one point nine meters in five
seconds." (at most two numbers in the payoff beat). The mechanism
sentence must follow the picture and the load bars: the hill and the
push move the car's weight onto the downhill wheels; backing up, the
downhill wheels are the front, driving wheels, so they carry sixty
three percent of the weight instead of fifty six. Whisper risks: "in
reverse" (pre-test; "backing up" is the fallback), "nose first", "icy",
"front-wheel drive", "ten degree"; avoid "do you", avoid "too". Pre-test
hooks with scripts/voiceover.sh and keep the one whose question lands
earliest under two seconds. Measure every fixed text line with PIL
before rendering and keep every line under 950 px, and the title under
100 characters with no < or >. Music seed 126. Templates: sims/hump
(side-view car on a road), sims/swerve (two cars), sims/wedge (slope
with force arrows), sims/deskchain (two-band layout, asserts, the clock,
the crossfade; read it whole). Sim name icyhill:
sims/icyhill/icyhill.py, projects/icyhill/, media/icyhill/.

## Claim (expected; the sim's numbers replace these)

The same 1,300 kg front-wheel-drive car on a 10 degree icy hill (grip
0.3) floors it from rest. Nose first the front wheels carry 56 percent
of the weight, spin, and the car slides back 0.85 m in 5 s. In reverse
the front wheels, now downhill, carry 63 percent, and the car climbs
1.92 m in 5 s. The steepest hill it can climb is 9.61 degrees nose
first and 10.88 degrees in reverse. Narrated: a ten degree hill (setup);
rolls back against climbs one point nine meters in five seconds
(payoff). Card: the question; the answer (nose first: -0.85 m; reverse:
+1.92 m); front load 56 against 63 percent; limits 9.6 and 10.9 degrees.
Description: the model statement, the load equations, both runs, the
grip and drive variants, the chosen numbers, the checks.

## Claim

The same 1,300 kg front-wheel-drive car (wheelbase 2.6 m, 60 / 40 static
split, centre of mass 0.55 m up, grip 0.3, all chosen) floors it from rest
on a 10 degree icy hill. Nose first the driven front wheels sit uphill and
carry 0.5556 of the weight (55.6 percent, 7084 N); the ice gives 1.6347
m/s^2 of push against 1.7030 m/s^2 of slope, a = -0.0683 m/s^2, and the
car slides back 0.8533 m in 5 s (-0.3413 m/s) with its wheels spinning
forward. In reverse the driven wheels sit downhill and carry 0.6309 (63.1
percent, 8044 N); the push is 1.8562 m/s^2, a = +0.1533 m/s^2, and it
climbs 1.9159 m in 5 s (+0.7664 m/s). Steepest hill at full throttle: 9.61
degrees nose first, 10.88 degrees in reverse; the window is 1.27 degrees
wide and the 10 degree hill sits inside it, so the answer depends on the
chosen grip, split and height. Narrated: a ten degree hill (setup); nose
first it rolls back, in reverse it climbs one point nine meters in five
seconds (payoff). Card: the question; nose first: rolled back 0.85 m in 5
s; in reverse: climbed 1.92 m in 5 s; front wheels carry 56 % against 63
%; steepest hill 9.6 against 10.9 degrees.

## Evidence

### Measurements

`nix develop -c python3 sims/icyhill/icyhill.py --measure-only > media/icyhill/measure.log`
(media/icyhill/measure.log verbatim):

```
Sat Oct 10 10:50:30 AM EEST 2026
setup: the same hill in both panels, side view: a 1,300 kg front-wheel-drive car, wheelbase L = 2.6 m, 60 / 40 front-to-rear static split so the centre of mass is b = 1.56 m ahead of the rear axle and h = 0.55 m up, grip mu = 0.3 on ice, a theta = 10 degree hill (all chosen); g = 9.807 m/s^2; the car starts from rest with the brakes on and the driver floors it at the throttle: the driven front wheels spin and push uphill with mu N_front, the rear wheels roll free and push nothing; top panel nose first (the front axle uphill), bottom panel in reverse (the same car turned round, the front axle downhill, backing up); loads N_front = m g cos theta (b / L) -/+ m (g sin theta + a) (h / L) (minus nose first, plus in reverse), N_rear = m g cos theta - N_front, a = mu N_front / m - g sin theta; both runs integrated by RK4 at 1000 steps per second (dt = 1e-03 s) for 5 s with the loads solved from the state at every stage, checked against the closed form x = (b / L) cos theta / (1 +/- mu h / L), s = a t^2 / 2 and a half-step rerun; real time on a 8 s cycle (480 frames) with the throttle 0.5 s into the cycle, the picture and the readouts held from 5.5 s, 5 cycles in 40 s; drawn at 130 px per metre; deterministic, no seed
nose first (the front axle uphill): at rest with the brakes on (a = 0) the front axle carries 0.5542 of the weight m g and the rear 0.4307 (sum 0.9848 = cos theta 0.9848); wheels spinning, the load equation and a = mu N_front / m - g sin theta solve to x = N_front / (m g) = (b / L) cos theta / (1 + mu h / L) = 0.5556 = 0.556 (55.6 percent, 7084 N), the rear axle 0.4292 (42.9 percent, 5472 N), both positive, sum 0.9848 = cos theta; the load equation evaluated at the solved a gives back 0.555624 (diff +0.0e+00); the ice gives mu N_front = 1.6347 m/s^2 of push against g sin theta = 1.7030 m/s^2 of slope, so a = -0.0683 m/s^2 = -0.0683 (rolls back, the wheels spinning forward); RK4 from rest: after 5 s the car has moved -0.8533 m = -0.85 m at -0.3413 m/s (closed form a t^2 / 2 = -0.8533 m, diff +1.6e-14 m; the table stays within 2.2e-14 m of the closed form), 5000 steps; half-step rerun (dt = 5e-04 s): -0.8533324 m (-1.0e-13 m); the rear wheels roll free: no traction from them
in reverse (the front axle downhill): at rest with the brakes on (a = 0) the front axle carries 0.6276 of the weight m g and the rear 0.3572 (sum 0.9848 = cos theta 0.9848); wheels spinning, the load equation and a = mu N_front / m - g sin theta solve to x = N_front / (m g) = (b / L) cos theta / (1 - mu h / L) = 0.6309 = 0.631 (63.1 percent, 8044 N), the rear axle 0.3539 (35.4 percent, 4512 N), both positive, sum 0.9848 = cos theta; the load equation evaluated at the solved a gives back 0.630924 (diff +0.0e+00); the ice gives mu N_front = 1.8562 m/s^2 of push against g sin theta = 1.7030 m/s^2 of slope, so a = +0.1533 m/s^2 = +0.1533 (climbs); RK4 from rest: after 5 s the car has moved +1.9159 m = +1.92 m at +0.7664 m/s (closed form a t^2 / 2 = +1.9159 m, diff +1.6e-13 m; the table stays within 1.6e-13 m of the closed form), 5000 steps; half-step rerun (dt = 5e-04 s): +1.9159251 m (+8.5e-14 m); the rear wheels roll free: no traction from them
steepest hill (a = 0): tan theta* = mu b / (L + mu h) nose first = 9.6068 deg = 9.61 deg, mu b / (L - mu h) in reverse = 10.8794 deg = 10.88 deg; the window between them is 1.2727 deg = 1.27 deg wide and the 10 degree hill sits inside it (9.61 < 10 < 10.88): the answer depends on the chosen grip, split and height
for the description: grip 0.2: nose first front load 0.5669, a -0.5910 m/s^2, -7.39 m in 5 s, steepest 6.57 deg; in reverse front load 0.6170, a -0.4928 m/s^2, -6.16 m in 5 s, steepest 7.14 deg; window 0.57 deg; grip 0.4: nose first front load 0.5448, a +0.4341 m/s^2, +5.43 m in 5 s, steepest 12.48 deg; in reverse front load 0.6455, a +0.8292 m/s^2, +10.37 m in 5 s, steepest 14.69 deg; window 2.21 deg; grip 0.3: nose first front load 0.5556, a -0.0683 m/s^2, -0.85 m in 5 s, steepest 9.61 deg; in reverse front load 0.6309, a +0.1533 m/s^2, +1.92 m in 5 s, steepest 10.88 deg; window 1.27 deg; rear-wheel drive nose first at grip 0.3 (the driven rear axle downhill): rear load 0.4598, a -0.3501 m/s^2, -4.38 m in 5 s, steepest atan(mu (L - b) / (L - mu h)) = 7.30 deg (its lighter rear axle gives it less than the front drive even with the pitch helping); all-wheel drive at grip 0.3: a = mu g cos theta - g sin theta = +1.1944 m/s^2, +14.93 m in 5 s, steepest atan(mu) = 16.70 deg, whatever the split
checks against the brief (23 checks, 0 failed): nose first front load (W): brief 0.556, sim 0.555624, diff -3.8e-04: ok; nose first front load (4 places): brief 0.5556, sim 0.555624, diff +2.4e-05: ok; nose first a (m/s^2): brief -0.0683, sim -0.0682666, diff +3.3e-05: ok; nose first moved at 5 s (m): brief -0.85, sim -0.853332, diff -3.3e-03: ok; in reverse front load (W): brief 0.631, sim 0.630924, diff -7.6e-05: ok; in reverse front load (4 places): brief 0.6309, sim 0.630924, diff +2.4e-05: ok; in reverse a (m/s^2): brief 0.1533, sim 0.153274, diff -2.6e-05: ok; in reverse moved at 5 s (m): brief 1.92, sim 1.91593, diff -4.1e-03: ok; steepest nose first (deg): brief 9.61, sim 9.60675, diff -3.2e-03: ok; steepest in reverse (deg): brief 10.88, sim 10.8794, diff -5.8e-04: ok; grip 0.2 steepest nose first: brief 6.57, sim 6.5675, diff -2.5e-03: ok; grip 0.2 steepest in reverse: brief 7.14, sim 7.14201, diff +2.0e-03: ok; grip 0.4 steepest nose first: brief 12.48, sim 12.4772, diff -2.8e-03: ok; grip 0.4 steepest in reverse: brief 14.69, sim 14.6914, diff +1.4e-03: ok; rear-wheel drive nose first steepest: brief 7.3, sim 7.3016, diff +1.6e-03: ok; all-wheel drive steepest: brief 16.7, sim 16.6992, diff -7.6e-04: ok; window (deg): brief 1.27, sim 1.27266, diff +2.7e-03: ok; nose first loads sum to cos theta: brief 0.984808, sim 0.984808, diff +0.0e+00: ok; in reverse loads sum to cos theta: brief 0.984808, sim 0.984808, diff +0.0e+00: ok; nose first RK4 against the closed form (m): brief 0, sim 1.59872e-14, diff +1.6e-14: ok; in reverse RK4 against the closed form (m): brief 0, sim 1.57208e-13, diff +1.6e-13: ok; both axle loads positive in both runs: least 0.3539 W: ok; the 10 degree hill inside the window: ok
drawing: 130 px per metre, the slope a true 10 degrees rising to the right; the car 4.2 m = 546 px long with 42 px wheel radius and its centre of mass +0.26 m ahead of the mid-wheelbase, 0.55 m up; both cars start with their mid-wheelbase at x 470 on the start line, where the road surface is 400 px under the band top (the road at x 0 is at 483 px, at x 1080 at 292 px); the 1.92 m climb shows as 249 px along the road (245 px across, 43 px up) and the 0.85 m roll-back as 111 px; the nose first car spans x 76 to 732 and y 216 to 449 over its run, the in reverse car x 185 to 977 and y 168 to 430 (band 0 to 550, text rows end at 136); the driven wheel's spoke is drawn turning at 2.5 turns a second while the wheels spin (drawing only: the spin rate is not modelled) and the free wheel's spoke rolls with the car at v / r
schedule (video time, real time): cycles of 8 s start at -8.00, 0.00, 8.00, 16.00, 24.00, 32.00 s; the throttle gauge rises over the first 0.5 s of each cycle and the driver floors it 0.5 s in at 0.50, 8.50, 16.50, 24.50, 32.50 s; the cars move for 5 s; the event rows light and the readouts and the picture hold 5 s after the throttle at 5.50, 13.50, 21.50, 29.50, 37.50 s; the reset crossfade runs over the last 0.5 s of each cycle (from 7.50, 15.50, 23.50, 31.50, 39.50 s; the readouts out over its first half and in over its second); on the first frame the cycle is 0.00 s in (both cars at rest on the start line, the gauge at zero and rising); title until 3 s; payoff card from 34.4 s; the title fades back in over the last 0.5 s and the last frame repeats the first (the scene is periodic: 40 s holds exactly 5 cycles)
text widths (the on-screen strings verbatim): overlay@34 744 px '1,300 kg front drive, grip 0.3 | no seed', title line 1@56 656 px 'Front-wheel drive on', title line 2@56 665 px 'an icy hill: nose first,', title line 3@56 436 px 'or in reverse?', legend@40 663 px 'same car, same hill, real time', clock@28 376 px '1.25 s after the throttle', clock rest@28 297 px 'before the throttle', label nose@40 213 px 'nose first', sublabel nose@28 509 px 'front-wheel drive, 10 degree ice', event nose@32 638 px 'nose first: rolled back 0.85 m in 5 s', moved nose@40 336 px 'moved -0.85 m', load nose@28 376 px 'front wheels carry 56 %', driven label nose@24 177 px 'DRIVEN 56 %', rear label nose@24 130 px 'rear 43 %', label rev@40 227 px 'in reverse', sublabel rev@28 509 px 'front-wheel drive, 10 degree ice', event rev@32 590 px 'in reverse: climbed 1.92 m in 5 s', moved rev@40 353 px 'moved +1.92 m', load rev@28 376 px 'front wheels carry 63 %', driven label rev@24 177 px 'DRIVEN 63 %', rear label rev@24 130 px 'rear 35 %', speed@28 251 px 'speed -0.34 m/s', gauge label@24 104 px 'throttle', payoff line 1@40 715 px 'Front-wheel drive on an icy hill:', payoff line 2@40 553 px 'nose first, or in reverse?', payoff line 3@40 797 px 'nose first: rolled back 0.85 m in 5 s', payoff line 4@40 738 px 'in reverse: climbed 1.92 m in 5 s', payoff line 5@40 842 px 'front wheels carry 56 % against 63 %', payoff line 6@40 855 px 'steepest hill 9.6 against 10.9 degrees'
row check: the left column spans x 40 to 549 px and the right column x 664 to 1040 px, both y 20 to 136 under the band top (the load bar x 720 to 1040 at y 108 to 124); the throttle gauge x 80 to 104, y 160 to 270 with its label at y 290 (104 px wide); the event row x 402 to 1040 (widest 638 px at 32 px) at y 496 to 528, over the slab (the road surface at x 402 is at y 412); the wheel labels 22 px under the road at each wheel: nose driven label at the start x 548 to 725, y 380 to 406; nose rear label at the start x 238 to 369, y 438 to 464; nose driven label at the end x 439 to 615, y 399 to 425; nose rear label at the end x 129 to 259, y 458 to 484; rev driven label at the start x 215 to 392, y 438 to 464; rev rear label at the start x 571 to 702, y 380 to 406; rev driven label at the end x 461 to 637, y 395 to 421; rev rear label at the end x 817 to 947, y 336 to 362; each band is 550 px tall (y 330 to 880 and 880 to 1430); the caption band starts at y 1440; the title rows end at y 330, the band text starts at y 350; the overlay band ends at y 130
car check: the body outline and both wheel squares of each car, at 61 positions along its run, are clear of the left column, the right column, the throttle gauge and the event row (polygon against box); the car points within 30 px right of the gauge are never higher than y 343 (the gauge label ends at y 304)
Sat Oct 10 10:50:31 AM EEST 2026
```

Brief checks (the sim prints and asserts each; 23 checks, 0 failed):

- nose first front load 0.556 W (0.5556): sim 0.555624, ok
- nose first a = -0.0683 m/s^2: sim -0.0682666, ok
- nose first -0.85 m at 5 s: sim -0.853332 m, ok
- in reverse front load 0.631 W (0.6309): sim 0.630924, ok
- in reverse a = +0.1533 m/s^2: sim +0.153274, ok
- in reverse +1.92 m at 5 s: sim +1.91593 m, ok
- steepest atan(mu b / (L + mu h)) = 9.61 deg nose first: sim 9.60675, ok
- steepest atan(mu b / (L - mu h)) = 10.88 deg in reverse: sim 10.8794, ok
- grip 0.2: 6.57 and 7.14 deg: sim 6.5675 and 7.14201, ok
- grip 0.4: 12.48 and 14.69 deg: sim 12.4772 and 14.6914, ok
- rear-wheel drive nose first 7.30 deg: sim 7.3016, ok
- all-wheel drive atan(mu) = 16.70 deg: sim 16.6992, ok
- both axle loads positive in both runs (least 0.3539 W) and summing to
  m g cos theta (0.984808 both runs, diff 0): ok
- the undriven axle rolls freely, no traction from it: ok (printed per run)
- RK4 within 1e-9 m of the closed form: 1.6e-14 m and 1.6e-13 m, ok;
  half-step rerun within 1.0e-13 m, ok
- window 1.27 deg wide (1.27266) and the 10 degree hill inside it
  (9.61 < 10 < 10.88): ok; the dependence on grip, split and height is
  stated in the log and the description
- the car stays inside the band (assert): nose first x 76 to 732, y 216
  to 449; in reverse x 185 to 977, y 168 to 430 (band 0 to 550); the
  polygon-against-box car check at 61 positions per run is clear of every
  text column, the gauge and the event row
- every fixed text line under 950 px (widest: payoff line 6, 855 px);
  overlay 744 px; title under 100 characters, no < or >

### Production

- sims/icyhill/icyhill.py reads projects/icyhill/manifest.json; modes
  --measure-only and --frames; deterministic, no seed, no wall clock.
- Smoke frames media/icyhill/smoke-{0.0,0.3,0.5,1.0,2.1,3.5,5.6,7.7,
  35.5,39.6}.png viewed; fixes before the full render: the right-column
  load text shortened to "front wheels carry 56 %" (the long form met the
  left column); the car-against-gauge test changed from a loose bbox to a
  polygon-against-box test, which found sub-pixel clips of the gauge label
  by the rolled-back car's roof, so the gauge moved to y 160 to 270 with
  the label at y 290; the CM trail drawn over the car in white (the car
  moves less than its length, so a trail under it was hidden); the ice
  spray enlarged.
- Footage: media/icyhill/footage.mp4, h264 1080x1920 60/1, 2400 frames,
  40.000000 s, rendered 10:50:31 to 10:51:01 (media/icyhill/render.log).
  Loop check: last frame differs from the first in 0 px (max 0);
  periodicity check 0 px; loop step 20679 px (the scene moves).
- Narration projects/icyhill/narration.txt: 109 words; first sentence is
  the question (nine words, 0 before it); setup number "ten degree";
  payoff "one point nine meters in five seconds"; the question repeated
  word for word right before the payoff; numbers as words, American
  spelling; the mechanism sentence carries the brief's fifty six and
  sixty three percent after the load bars are on screen.
- Hook pre-tests (media/icyhill/hooks/pretest.log, all ok): hook1 "Front-
  wheel drive on an icy hill: nose first, or in reverse?" 3.738 s; hook2
  fallback "Icy hill: drive up it, or back up it?" 2.786 s; hook3 (hook1
  plus the legend sentence) 6.618 s; hook4 "Front-wheel drive, icy hill:
  nose first, or in reverse?" 3.901 s; risky words file (nose first, in
  reverse, icy hill, front-wheel drive, ten degree, backing up, the
  percentages, the payoff) 24.149 s ok. Kept hook1: it is the brief's
  question, it round-trips, and it lands at 2.48 s of video.
- Voice: scripts/voiceover.sh pass 1: "ok: transcript matches narration
  (36.025760s)" (media/icyhill/voice.log). Voice 36.03 s, offset 0.6 s,
  ends at 36.63 s of video.
- Timing (media/icyhill/timing.log): question 0.60 to 2.48 s; repeated
  question 25.85 to 33.22 s; payoff tail 33.22 to 36.63 s; whisper word
  times "one" 34.49, "nine" 34.93, "meters" 35.15 to 35.60, "five" 35.76,
  "seconds" to 36.46 s. payoff_t set to 34.4 s (the card rises as "one
  point nine" is spoken; the event rows have been lit since 5.5 s of the
  cycle and the fifth run has moved for 1.9 s at 34.4 s).
- Compose: `nix develop -c scripts/compose.sh icyhill` (media/icyhill/
  compose.log): music seed 126; captions 19 pauses detected, 19 matched,
  max chunk start shift 0.985 s; final.mp4 40.000000 s; preview.mp4
  40.066667 s; sheet.png 8x5.

### Local QA

- ffprobe media/icyhill/final.mp4: stream h264 1080x1920 60/1; stream aac
  22050 Hz mono; format duration 40.000000; atoms ftyp, moov at 32, free,
  mdat (faststart); 7510209 bytes; md5 100d91e8b5eb666ab6cb958d5c34b73f.
- QA frames viewed: qa-0.00 (title on, overlay on, both cars at rest on
  the start line, gauge at zero), qa-1.00 (gauge full, cars 0.5 s into the
  run, live readouts), qa-2.10 (caption "nose first, or in reverse?" in
  the band), qa-20.00 (third cycle, rolled-back and climbed cars apart,
  wheel labels under the road), qa-34.70 (card rising, caption "one point
  nine"), qa-35.50 (card full, event rows lit), qa-39.983 (last frame,
  title faded back in, equals the first frame); sheet.png viewed.
- Captions: 38 chunks; joined text equals the narration word for word
  (109 words); widest chunk 785 px; first caption 0.600 to 1.465 s
  "Front-wheel drive on"; "one point nine" 34.495 to 35.353 s.
- footage.mp4 caption band (y 1440 to 1530) and overlay band (y 96 to
  130): background only (YMAX 28 over all frames).
- final.mp4 frame 2399 against frame 0: 9143 px differ over 24, max 80
  (encoder noise; the raw loop check is 0 px).
- Nothing wider than the frame: all text lines under 950 px (measured);
  the cars stay inside their bands (asserted).

### Metadata

- projects/icyhill/metadata.json written by media/icyhill/metadata.py
  (asserts: title 100 characters, ASCII, no < or >, question first then
  the answer with both numbers; description 4052 characters, ASCII; 12
  tags; 66 distinct numbers in the title and description all found in
  media/icyhill/measure.log; categoryId "27", privacyStatus "private",
  containsSyntheticMedia true, selfDeclaredMadeForKids false).
- Title: Front-wheel drive on an icy hill: nose first, or in reverse? 10
  deg ice: only reverse climbs, 1.92 m
- Description: the model statement, the load equations and the closed
  form, both runs with the loads in W and N, the rest-state loads, the
  steepest hills and the window, grip 0.2 and 0.4, rear-wheel drive and
  all-wheel drive, the checks, "Deterministic, no seed", the reproduction
  note (sims/icyhill/icyhill.py with projects/icyhill/manifest.json) and
  the AI-agent line.

### Deviations from the brief

- Scale: 130 px per metre, one true scale for the car and the road (the
  brief's 300 px per metre with a 126 px car is two scales and the 576 px
  climb does not fit beside a 4.2 m car in a 550 px band). The car is 546
  px, the climb 249 px, the roll-back 111 px; the slope is a true 10
  degrees.
- Start: both cars start with the mid-wheelbase at x 470 (not 300) on a
  start tick; the road passes through (470, 400) band-local instead of
  rising from x 60 at the band bottom-left, so the climbing car stays
  inside the band and clear of the right column.
- Event rows are 32 px, right-aligned over the slab (x 402 to 1040), not
  40 px: a 40 px row did not fit beside the car.
- Load display: a right-column bar and text "front wheels carry 56 %"
  (the brief's "front 56 %") plus per-wheel labels "DRIVEN 56 %" and
  "rear 43 %" under the road; "of the weight" dropped for width. The
  rest-state loads (55 % and 63 %) show before the throttle, the spinning
  loads after it.
- One shared clock row ("before the throttle" / "N s after the throttle")
  instead of a clock per band.
- From 5.5 s of the cycle the picture and the readouts hold and the
  throttle gauge drops to zero (the brief says the readouts freeze; the
  cars also stop so the picture matches the frozen numbers).
- The narration carries the brief's mechanism percentages (fifty six and
  sixty three) and the two payoff numbers the brief asked for, beyond the
  one-setup-one-payoff rule in the conventions; the brief allows at most
  two numbers in the payoff beat.
- The CM trail is drawn over the car body (white, blended) because the
  car moves less than its own length; the wheel spin rate (2.5 turns a
  second) and the ice spray are drawing only, stated in the log and the
  description.
- Metadata script lives at media/icyhill/metadata.py (the brief's pattern
  file media/pencil/metadata.py does not exist; media/toast/metadata.py was
  the pattern).

## Niche note

[produced 2026-10-10 as "Front-wheel drive on an icy hill: nose first, or
in reverse? 10 deg ice: only reverse climbs, 1.92 m"; measured a 1,300 kg
front-wheel-drive car at grip 0.3 on a 10 degree hill: nose first the
front wheels carry 0.5556 W, a = -0.0683 m/s^2, -0.85 m in 5 s; in
reverse 0.6309 W, a = +0.1533 m/s^2, +1.92 m in 5 s; steepest 9.61 against
10.88 degrees, window 1.27 degrees; task 20261010-103221]

## Upload

- Attempt 3 of 5 recorded at 2026-10-10T11:11:44+03:00 (quota day 2026-10-10T10:00 EEST), scripts/yt-upload.py icyhill, md5 100d91e8b5eb666ab6cb958d5c34b73f.
- Uploaded private as H9jNRb9cR9Q at 2026-10-10T08:11:47Z; scripts/yt-qa.py --wait --publish gate 15 of 15 on the first processed read; published 2026-10-10T11:12:43+03:00, re-read public; 55 units; attempt cost 1,655 units. https://youtu.be/H9jNRb9cR9Q
