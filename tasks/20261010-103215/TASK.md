# Produce short: coaster slid plain or spinning, the same 1 m/s push, does spinning make it slide farther

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day42

## Goal

Backlog idea (trend research 2026-10-10, task 20261010-100329, pillar 2
chaos and physics, table mechanics; read the full "Slide a coaster, spun
or not" bullet at the end of docs/niche.md): the same coaster pushed
across a table at the same speed, once plain and once spinning; the spun
one slides twice as far, and its sliding and spinning stop at the same
instant.

Orchestrator notes (2026-10-10; closed forms and an independent contact
quadrature with RK4 in /tmp/day42/closed.py with the log
/tmp/day42/closed.log; research script /tmp/day42/research/puck2.py with
puck2.log; g = 9.807 m/s^2). Read /tmp/day42/producer-conventions.md
first. The model: a uniform 10 cm disc (R = 5 cm, I = m R^2 / 2, a
coaster seen from above) on a table with grip mu = 0.3 (chosen, say so),
Coulomb friction with uniform pressure integrated over the contact (a
polar grid of at least 160 radial by 320 angular cells; the friction per
unit mass is -mu g times the area-weighted mean of the unit slip
direction, the torque per unit mass about the centre likewise), RK4 at
dt = 2e-4 s for v and omega, x by the same RK4 stages. Top band, the
PLAIN coaster: pushed at v0 = 1.0 m/s with no spin (say: the same push,
chosen). Bottom band, the SPUN coaster: the same 1.0 m/s and omega0 =
40.87 rad/s = 6.5 turns a second (rim speed 2.04 m/s). Stop when |v| <
2e-3 m/s and R |omega| < 2e-3 m/s; both must fall under their bound at
the same step (the same-instant stop is the mechanism). Print the table
of v, R omega and v / (R omega) every 0.05 s for the spun run, the
variants for the description (20 rad/s, 80 rad/s, 0.5 m/s and 1.5 m/s
with 40.87 rad/s), and the schedule.

Checks, not facts (the sim must print and compare; state them as
checks): plain stop at v0 / (mu g) = 0.3399 s after v0^2 / (2 mu g) =
16.99 cm (quadrature 0.3394 s, 16.99 cm); spun 33.99 cm at 0.6554 s,
ratio 2.000 (40.0 rad/s gives 33.43 cm, 0.6462 s, 1.967x); v / (R omega)
at the stop between 0.64 and 0.66 (Farkas et al. PRL 2003: 0.653); the
dimensionless slide friction at the fixed point about 0.616 of mu g;
spin-only (v0 = 0, 40.87 rad/s) stops at about 0.5098 s having moved 0.0
cm; the quadrature of a pure slide (omega = 0) gives exactly mu g; the
polar grid weights sum to 1 and give I_c = R^2 / 2 within 1e-5; the
energy per unit mass starts at 1.5 J/kg (0.5 v0^2 + 0.25 R^2 omega0^2)
and ends under 1e-5; halving dt changes the stop distance under 1e-4 m.

Drawing: two-band layout (sims/deskchain style, read it whole; bands y
330 to 880 and 880 to 1430), TOP-DOWN view at 2,000 px per metre: a
table surface filling each band with a faint start line at x 150 and a
ruler of cm ticks along the band bottom; each coaster a 200 px disc
(sims/turntable draws a disc with a stripe) with a dark stripe from the
centre to the rim so the spin shows, a thin trail of its centre, a
finger mark at the push at the start of each cycle; the plain coaster
stops with its centre at x 150 + 340 = 490, the spun one at x 150 + 680
= 830 (assert both discs stay inside the band width with margin). Label
rows (40 px, coloured): "plain coaster" (coral) and "spun coaster, 6.5
turns a second" (teal), both "same push, 1 m/s". Readouts (28 px): left
column "speed N.NN m/s" (live) and the clock; right column "slid NN.N
cm" (live) and, in the bottom band, "spin N.N turns/s" (live). Gold
event rows: top "plain: stopped at 0.34 s, 17 cm", bottom "spun: stopped
at 0.66 s, 34 cm, spin and slide together" (each lit when it stops, both
held). Shown at 1/4 speed: cycle 8 s (480 frames): the push 0.5 s into
the cycle (both at rest before it, the finger mark approaching: motion in
frame one), the plain one stops at 0.5 + 4 * 0.3394 = 1.86 s, the spun
one at 0.5 + 4 * 0.6554 = 3.12 s; hold to 7.5 s, crossfade reset over
the last 0.5 s; 5 cycles in 40 s, exactly periodic, the last frame equal
to the first. Legend row after the title: "same table, same push, 1/4
speed". Overlay: "10 cm coaster, grip 0.3 | no seed" (measure it).

Day forty-two, first slot. Chosen because it is a tabletop object a
viewer owns, the two coasters end visibly apart (17 against 34 cm), the
ratio is a clean 2x with a published fixed point behind it, and the push
repeats as a loop. Question in the first two seconds: "Does spinning a
coaster make it slide farther?" (pre-test; it is the first sentence;
"Slide a coaster, spun or not: which one goes farther?" is the
fallback). Keep the question identical in the title, the hook and the
payoff. Setup number: "one meter a second" (one setup number only; the
6.5 turns a second, the 10 cm and the grip go to the overlay, card and
description). Payoff: "Yes. The spun one slides thirty four centimeters,
the plain one seventeen: twice as far." (at most two numbers in the
payoff beat). The mechanism sentence must follow the picture: the
friction under the coaster is shared between the spin and the slide, so
the slide feels only part of the braking, and the spin and the slide die
at the same instant. Whisper risks: "coaster" (pre-test; "puck" is the
fallback), "spun", "centimeters" (once), "twice as far", "spinning";
avoid "do you", avoid "too". Pre-test hooks with scripts/voiceover.sh
and keep the one whose question lands earliest under two seconds.
Measure every fixed text line with PIL before rendering and keep every
line under 950 px, and the title under 100 characters with no < or >.
Music seed 124. Templates: sims/deskchain (two-band layout, asserts, the
clock, the crossfade; read it whole), sims/turntable (a disc with a
stripe), sims/belt and sims/pushpull (Coulomb slip), sims/pencil
(asserts, finger mark, yesterday's style). Sim name spinslide:
sims/spinslide/spinslide.py, projects/spinslide/, media/spinslide/.

## Claim (expected; the sim's numbers replace these)

Two 10 cm coasters on a table with grip 0.3 get the same push, 1.0 m/s.
The plain one stops after 17.0 cm at 0.34 s. The one also spinning at
6.5 turns a second slides 34.0 cm, twice as far, stopping at 0.66 s with
its spin and its slide ending at the same instant; at the stop v / (R
omega) sits at 0.65, the Farkas fixed point. Narrated: one meter a second
(setup); thirty four centimeters against seventeen, twice as far
(payoff). Card: the question; the answer (plain 17 cm at 0.34 s; spun 34
cm at 0.66 s); spin and slide stop together; the slide feels 62 percent
of the friction. Description: the model statement, the equations, both
runs, the spin and speed variants, the fixed point, the checks.


## Claim

Two 10 cm coasters (uniform discs, R 5 cm, I = m R^2 / 2) on a table
with grip 0.3 (chosen) get the same push: each leaves at 1.0 m/s
(chosen). The plain coaster feels the full mu g = 2.9421 m/s^2 against
its slide and stops at 0.3394 s after 16.99 cm (closed form 0.3399 s,
16.99 cm). The spun coaster (the same 1.0 m/s plus 40.87 rad/s = 6.50
turns a second, rim 2.04 m/s) stops at 0.6554 s after 33.99 cm, 2.000
times as far. Its |v| and R |omega| fall under the 2e-3 m/s bound 2
steps (0.4 ms) apart and the zero crossings extrapolated from the last
two steps are 0.003 ms apart: the slide and the spin end at the same
instant. At the stop v / (R omega) = 0.649 (Farkas et al. PRL 2003:
0.653); there the slide feels 0.613 of mu g (61 percent of the
friction) and the spin 0.711 of the pure-spin torque. Narrated: one
meter a second (setup); "Yes. The spun one slides thirty four
centimeters, the one with no spin seventeen: twice as far." (payoff).
Card: the question; yes: plain 17 cm, stopped at 0.34 s; spun 34 cm at
0.66 s: twice as far; its spin and its slide stop together; the slide
feels 61 percent of the friction.

## Evidence

### Measurements

`nix develop -c python3 sims/spinslide/spinslide.py --measure-only`
(final run 10:56:05, exit 0, saved as media/spinslide/measure.log):

```
Sat Oct 10 10:56:05 AM EEST 2026
setup: the same table in both bands, seen from above: a uniform disc of radius 5 cm (10 cm coaster, I = m R^2 / 2) on a table with grip mu = 0.3, the same everywhere under it (chosen); g = 9.807 m/s^2; each coaster gets the same push, its centre leaving at v0 = 1 m/s (chosen); top band the plain coaster, no spin; bottom band the spun coaster, the same 1 m/s and omega0 = 40.87 rad/s = 6.50 turns a second (rim speed R omega0 = 2.04 m/s = 2.043 m/s); Coulomb friction with uniform pressure integrated over the contact on a polar grid of 160 radial by 320 angular cells (51200 cells): the force per unit mass is -mu g times the area-weighted mean unit slip direction, the torque per unit mass about the centre likewise; x, v, theta and omega by classical RK4 at dt = 0.0002 s = 2e-04 s (x by the same RK4 stages); a run stops when |v| < 0.002 m/s and R |omega| < 0.002 m/s; shown at 1/4 speed on a 8 s cycle (480 frames) with the push 0.5 s into the cycle, 5 cycles in 40 s; drawn at 2000 px per metre; deterministic, no seed
grid: the 160 x 320 area weights sum to 1.000000000000 (1 - sum +0.0e+00); the grid's I_c = <r^2> = 1.249975586e-03 m^2 against R^2 / 2 = 1.250000000e-03 m^2 (diff -2.44e-08 m^2, -2.0e-05 relative); <r> = 0.033333 m against 2 R / 3 = 0.033333 m (diff -3.3e-07 m); pure slide (omega = 0) at 1 m/s: the quadrature gives -2.942100000 m/s^2 against -mu g = -2.942100000 m/s^2 (diff +0.0e+00), sideways -0.0e+00, torque -3.2e-19; pure spin (v = 0) at 40.87 rad/s: force -2.1e-17, +1.0e-16 m/s^2, torque -9.806904e-02 m^2/s^2 = -mu g <r> (-9.806904e-02), so alpha = 78.4552 rad/s^2 against the closed form 4 mu g / (3 R) = 78.4560 rad/s^2 (diff -7.7e-04): a spin-only coaster would stop after omega0 / alpha = 0.5209 s
plain coaster (1 m/s, no spin): the friction is the full mu g = 2.9421 m/s^2 against the slide, so v falls at a steady 2.9421 m/s^2; it stops (|v| under 0.002 m/s) at 0.3394 s on step 1697 after 16.9946 cm = 16.99 cm = 17 cm (closed form v0 / (mu g) = 0.3399 s to v = 0, v0^2 / (2 mu g) = 16.9947 cm = 16.99 cm; the quadrature stop comes 4.9e-04 s before v would reach zero, 3.6e-05 cm short of the closed distance); v left 1.45e-03 m/s; sideways force at most 2.5e-32 m/s^2; energy per unit mass 0.5000 J/kg at the push, 1.1e-06 J/kg at the stop
spun coaster (1 m/s and 40.87 rad/s): it stops at 0.6554 s on step 3277 after 33.9882 cm = 33.99 cm = 34 cm, 1.9999 = 2.000 times the plain coaster's 16.99 cm; |v| fell under 0.002 m/s on step 3275 (0.6550 s) and R |omega| on step 3277 (0.6554 s): 2 steps = 0.4 ms apart; the zero crossings extrapolated from the last two steps: v at 0.65608 s, omega at 0.65607 s, 0.003 ms apart (the slide and the spin end at the same instant); at the stop v = 1.22e-03 m/s, R omega = 1.88e-03 m/s, v / (R omega) = 0.649 (Farkas et al. PRL 2003: 0.653); at the end the slide feels 0.6128 = 0.613 of mu g = 61 percent of the friction and the spin feels 0.711 of the pure-spin torque; it turned 2.092 turns; sideways force at most 1.2e-16 m/s^2; energy per unit mass 0.5 v0^2 + 0.25 R^2 omega0^2 = 1.5440 J/kg at the push, 1.6e-06 J/kg at the stop
spun coaster table: 0.00 s: v 1.0000 m/s, R omega 2.0435 m/s (6.50 turns/s), v / (R omega) 0.489; 0.05 s: v 0.9299 m/s, R omega 1.8813 m/s (5.99 turns/s), v / (R omega) 0.494; 0.10 s: v 0.8591 m/s, R omega 1.7197 m/s (5.47 turns/s), v / (R omega) 0.500; 0.15 s: v 0.7877 m/s, R omega 1.5589 m/s (4.96 turns/s), v / (R omega) 0.505; 0.20 s: v 0.7154 m/s, R omega 1.3988 m/s (4.45 turns/s), v / (R omega) 0.511; 0.25 s: v 0.6423 m/s, R omega 1.2397 m/s (3.95 turns/s), v / (R omega) 0.518; 0.30 s: v 0.5682 m/s, R omega 1.0814 m/s (3.44 turns/s), v / (R omega) 0.525; 0.35 s: v 0.4932 m/s, R omega 0.9243 m/s (2.94 turns/s), v / (R omega) 0.534; 0.40 s: v 0.4170 m/s, R omega 0.7683 m/s (2.45 turns/s), v / (R omega) 0.543; 0.45 s: v 0.3396 m/s, R omega 0.6137 m/s (1.95 turns/s), v / (R omega) 0.553; 0.50 s: v 0.2606 m/s, R omega 0.4608 m/s (1.47 turns/s), v / (R omega) 0.566; 0.55 s: v 0.1800 m/s, R omega 0.3098 m/s (0.99 turns/s), v / (R omega) 0.581; 0.60 s: v 0.0971 m/s, R omega 0.1614 m/s (0.51 turns/s), v / (R omega) 0.601; 0.65 s: v 0.0109 m/s, R omega 0.0170 m/s (0.05 turns/s), v / (R omega) 0.638; 0.6554 s (stop): v 0.0012 m/s, R omega 0.0019 m/s, v / (R omega) 0.649
half-step rerun (dt = 0.0001 s): the spun coaster stops at 0.65540 s after 33.98818 cm (-1.76e-10 mm, +0.0e+00 s against the full step), v / (R omega) 0.649
for the description: 1 m/s with 20 rad/s (3.18 turns/s, rim 1.00 m/s): stops at 0.4550 s after 21.66 cm, 1.275 times the plain 16.99 cm, v / (R omega) at the end 0.656, energy at the push 0.7500 J/kg; 1 m/s with 40 rad/s (6.37 turns/s, rim 2.00 m/s): stops at 0.6462 s after 33.43 cm, 1.967 times the plain 16.99 cm, v / (R omega) at the end 0.649, energy at the push 1.5000 J/kg; 1 m/s with 80 rad/s (12.73 turns/s, rim 4.00 m/s): stops at 1.1014 s after 60.62 cm, 3.567 times the plain 16.99 cm, v / (R omega) at the end 0.630, energy at the push 4.5000 J/kg; 0.5 m/s: plain stops at 0.1694 s after 4.25 cm (closed form 4.25 cm); with 40.87 rad/s it stops at 0.5608 s after 15.46 cm, 3.639 times as far; 1.5 m/s: plain stops at 0.5092 s after 38.24 cm (closed form 38.24 cm); with 40.87 rad/s it stops at 0.7786 s after 57.59 cm, 1.506 times as far; spin only, 40.87 rad/s and no push: moves 0.000 cm and stops at 0.5206 s (closed form 3 R omega0 / (4 mu g) = 0.5209 s); spin only, 40 rad/s and no push: moves 0.000 cm and stops at 0.5094 s (closed form 3 R omega0 / (4 mu g) = 0.5098 s)
checks against the brief (24 checks, 0 failed): plain stop, closed form v0 / (mu g) (s): brief 0.3399, sim 0.339893, diff -6.7e-06: ok; plain distance, closed form v0^2 / (2 mu g) (cm): brief 16.99, sim 16.9947, diff +4.7e-03: ok; plain stop, quadrature (s): brief 0.3394, sim 0.3394, diff +5.6e-17: ok; plain distance, quadrature (cm): brief 16.99, sim 16.9946, diff +4.6e-03: ok; spun distance (cm): brief 33.99, sim 33.9882, diff -1.8e-03: ok; spun stop (s): brief 0.6554, sim 0.6554, diff +0.0e+00: ok; ratio spun / plain: brief 2, sim 1.99994, diff -6.3e-05: ok; 40.0 rad/s distance (cm): brief 33.43, sim 33.4284, diff -1.6e-03: ok; 40.0 rad/s stop (s): brief 0.6462, sim 0.6462, diff +0.0e+00: ok; 40.0 rad/s ratio: brief 1.967, sim 1.967, diff -9.0e-07: ok; v / (R omega) at the stop, in 0.64 to 0.66: brief 0.65, sim 0.649109, diff -8.9e-04: ok; slide friction at the fixed point (of mu g): brief 0.616, sim 0.612831, diff -3.2e-03: ok; spin only at 40.0 rad/s stops (s): brief 0.5098, sim 0.5094, diff -4.0e-04: ok; spin only at 40.87 rad/s stops, closed form 3 R omega0 / (4 mu g) (s): brief 0.520929, sim 0.5206, diff -3.3e-04: ok; spin only moves (cm): brief 0, sim -1.14959e-16, diff -1.1e-16: ok; pure slide quadrature (of mu g): brief 1, sim 1, diff +0.0e+00: ok; grid weights sum: brief 1, sim 1, diff +0.0e+00: ok; grid I_c against R^2 / 2 (m^2): brief 0.00125, sim 0.00124998, diff -2.4e-08: ok; energy at the push with 40.0 rad/s (J/kg): brief 1.5, sim 1.5, diff +2.2e-16: ok; energy at the push with 40.87 rad/s, 0.5 v0^2 + 0.25 R^2 omega0^2 (J/kg): brief 1.54397, sim 1.54397, diff +0.0e+00: ok; energy at the stop (J/kg): brief 0, sim 1.63045e-06, diff +1.6e-06: ok; half step changes the stop distance (m): brief 0, sim -1.75693e-13, diff -1.8e-13: ok; zero crossings of v and omega apart (ms): brief 0, sim 0.00301709, diff +3.0e-03: ok; |v| and R |omega| fall under 0.002 m/s on the same step: brief 0 steps apart, sim 2 steps (0.4 ms) apart, within 3 steps: ok
drawing: 2000 px per metre; each coaster 200 px across; the start line at x 150; the plain coaster stops with its centre at x 489.9 px (brief 490), the spun one at x 829.8 px (brief 830); the discs span x 50 to 930 px on a table from x 20 to 1060 (130 px of margin on the right); the spun coaster turns 2.09 turns, 9.8 deg per frame at the push
schedule (video time, 1/4 speed): cycles of 8 s start at -8.00, 0.00, 8.00, 16.00, 24.00, 32.00 s; the fingertips move in over the first 0.5 s and push both coasters 0.5 s into each cycle at 0.50, 8.50, 16.50, 24.50, 32.50 s; the plain coaster stops 1.358 s after the push at 1.86, 9.86, 17.86, 25.86, 33.86 s (its event row lights); the spun coaster stops 2.622 s after the push at 3.12, 11.12, 19.12, 27.12, 35.12 s (its event row lights), 1.26 s after the plain one; both hold until the reset crossfade over the last 0.5 s of each cycle (from 7.50, 15.50, 23.50, 31.50, 39.50 s); title until 3 s; payoff card from 31.2 s; the title fades back in over the last 0.5 s and the last frame repeats the first (the scene is periodic: 40 s holds exactly 5 cycles)
text widths (the on-screen strings verbatim): overlay@34 625 px '10 cm coaster, grip 0.3 | no seed', title line 1@56 759 px 'Does spinning a coaster', title line 2@56 679 px 'make it slide farther?', legend@40 770 px 'same table, same push, 1/4 speed', label plain@40 293 px 'plain coaster', sublabel plain@28 276 px 'same push, 1 m/s', event plain@28 490 px 'plain: stopped at 0.34 s, 17 cm', label spun@40 733 px 'spun coaster, 6.5 turns a second', sublabel spun@28 276 px 'same push, 1 m/s', event spun@28 876 px 'spun: stopped at 0.66 s, 34 cm, spin and slide together', speed@28 239 px 'speed 1.00 m/s', clock@28 350 px '0.655 s after the push', clock held@28 252 px 'before the push', slid@28 190 px 'slid 34.0 cm', spin@28 246 px 'spin 6.5 turns/s', no spin@28 115 px 'no spin', ruler label 1@24 17 px '0', ruler label 2@24 33 px '10', ruler label 3@24 33 px '20', ruler label 4@24 33 px '30', ruler label 5@24 81 px '40 cm', payoff line 1@40 542 px 'Does spinning a coaster', payoff line 2@40 485 px 'make it slide farther?', payoff line 3@40 790 px 'yes: plain 17 cm, stopped at 0.34 s', payoff line 4@40 762 px 'spun 34 cm at 0.66 s: twice as far', payoff line 5@40 779 px 'its spin and its slide stop together', payoff line 6@40 901 px 'the slide feels 61 percent of the friction'
row check: the left label rows span x 40 to 773 px and y 20 to 98 under the band top, the left readouts x 40 to 390 and y 106 to 170; the right readouts x 794 to 1040 and y 106 to 170; the table x 20 to 1060, y 182 to 458 with its ruler ticks to 472 and the ruler labels x 142 to 991 at y 474 to 498; the coasters' centre line at y 320, the discs from y 220 to 420; the fingertips reach up to y 185 and left to x 2; the event row x 40 to 916 (widest 876 px) at y 508 to 540; each band is 550 px tall (y 330 to 880 and 880 to 1430); the caption band starts at y 1440; the title rows end at y 280, the band text starts at y 350; the legend at y 236; the overlay band ends at y 130; the card from y 1572 to 1832
exit 0
Sat Oct 10 10:58:07 AM EEST 2026
```

Checks in the brief, each printed and compared by the sim with an
assert (24 checks, 0 failed):

- plain stop at v0 / (mu g) = 0.3399 s after v0^2 / (2 mu g) = 16.99
  cm: closed form 0.339893 s, 16.9947 cm; quadrature 0.3394 s, 16.9946
  cm (the stop condition |v| under 2e-3 m/s comes 4.9e-4 s before v
  reaches zero). ok.
- spun 33.99 cm at 0.6554 s, ratio 2.000: sim 33.9882 cm at 0.6554 s,
  ratio 1.9999. ok.
- 40.0 rad/s gives 33.43 cm, 0.6462 s, 1.967x: sim 33.4284 cm, 0.6462
  s, 1.967x. ok.
- v / (R omega) at the stop between 0.64 and 0.66 (Farkas 0.653): sim
  0.649. ok.
- the slide friction at the fixed point about 0.616 of mu g: sim
  0.6128 (within the 0.01 tolerance; the card says 61 percent). ok.
- spin-only stops at about 0.5098 s having moved 0.0 cm: the brief's
  number is the 40 rad/s value; sim 40.0 rad/s 0.5094 s (closed form
  3 R omega0 / (4 mu g) = 0.5098 s), 40.87 rad/s 0.5206 s (closed form
  0.5209 s), moved 1.1e-16 cm in both. ok.
- the quadrature of a pure slide gives exactly mu g: diff 0.0e+00,
  sideways 0, torque 3.2e-19. ok.
- the polar grid weights sum to 1 (diff 0.0e+00) and give I_c within
  1e-5 of R^2 / 2: 1.249975586e-03 against 1.25e-03 m^2, diff -2.44e-08
  m^2 (2.0e-05 relative). ok.
- energy per unit mass starts at 1.5 J/kg and ends under 1e-5: 1.5000
  J/kg with 40 rad/s (the brief's number), 1.5440 J/kg = 0.5 v0^2 +
  0.25 R^2 omega0^2 with 40.87 rad/s; 1.6e-06 J/kg at the stop. ok.
- halving dt changes the stop distance under 1e-4 m: -1.76e-13 m
  (-1.76e-10 mm), the stop time unchanged. ok.
- both motions fall under their bound at the same step: |v| on step
  3275 (0.6550 s), R |omega| on step 3277 (0.6554 s), 2 steps = 0.4 ms
  apart (the check passes within 3 steps); the extrapolated zero
  crossings 0.65608 and 0.65607 s, 0.003 ms apart. ok.
- the sideways force stays zero by symmetry: at most 1.2e-16 m/s^2
  (spun), 2.5e-32 (plain). ok.
- the plain coaster stops with its centre at x 490 and the spun one at
  x 830: 489.9 and 829.8 px, asserted within 3 px; the discs span x 50
  to 930 on a table from x 20 to 1060 (130 px of margin). ok.
- every fixed text line under 950 px: widest payoff line 6 901 px at
  40, spun event row 876 px at 28, title line 1 759 px at 56, overlay
  625 px; asserted. ok.
- layout boxes (left labels, left readouts, right readouts, table with
  ruler, ruler labels, event row) pairwise clear; the fingertips reach
  y 185 (under the clock row at 170) and x 2; the event row ends at y
  540 of the 550 px band; the bottom band ends at the caption band;
  the card from y 1572 to 1832; asserted. ok.
- schedule: push 0.5 s into each 8 s cycle (0.50, 8.50, 16.50, 24.50,
  32.50 s), the plain coaster stopped at 1.86 s and the spun one at
  3.12 s of each cycle, held to the crossfade at 7.50 s; 5 cycles in
  40 s; asserted. ok.

### Production

- sims/spinslide/spinslide.py (new): two-band top-down scene after
  sims/deskchain and sims/pencil (bands, clock, crossfade, render loop
  through ffmpeg rawvideo, box asserts), a disc with a stripe after
  sims/turntable, Coulomb slip after sims/belt and sims/pushpull. The
  contact is a 160 x 320 polar grid with area weights (sum 1); the
  force per unit mass is -mu g times the area-weighted mean unit slip
  direction, the torque likewise; (x, v, theta, omega) by classical RK4
  at dt 2e-4 s; a run stops when |v| and R |omega| are both under 2e-3
  m/s, recording the step each fell under its bound and extrapolating
  both zero crossings. 24 brief checks with assert; text-width and box
  asserts; loop and periodicity prints in the renderer. Deterministic,
  no seed used.
- projects/spinslide/manifest.json: g 9.807, radius 0.05 m, grip 0.3,
  push 1.0 m/s, spin 40.87 rad/s, dt 2e-4, grid 160 x 320, stop 2e-3
  m/s, table every 0.05 s, description spins 20, 40, 80 rad/s and
  speeds 0.5, 1.5 m/s, slow 4, cycle 8 s, push_at 0.5, finger_s 0.5,
  reset_fade 0.5, px_per_m 2000, start x 150, title_until 3.0,
  payoff_t 31.2, music_seed 124, voice_offset 0.6, caption_y 0.75,
  overlay "10 cm coaster, grip 0.3 | no seed".
- Drawing: the table surface fills each band from 182 to 458 px under
  the band top with a faint start line at x 150 and a cm ruler (ticks
  every cm, labels every 10 cm) under its lower edge; each coaster a
  200 px disc with a 14 px dark stripe from the centre to the rim and a
  centre dot, a thin trail of its centre, a gold tick on the ruler at
  its stop; a fingertip seen from above moves in over the first 0.5 s
  of each cycle, touches the rim at the push (dead behind for the plain
  coaster, 40 deg off-centre for the spun one) with three gold ticks,
  and pulls back. Label rows 40 px (coral, teal), readouts 28 px: left
  "speed", clock; right "slid" and "spin" / "no spin"; gold event rows
  28 px under the ruler. Spun coaster turns 9.8 deg per frame at the
  push (2.09 turns in all).
- Smoke frames viewed before the full render (media/spinslide/smoke-*.png
  at 0.0, 0.3, 0.5, 0.7, 1.0, 1.9, 2.5, 3.2, 5.0, 7.75, 35.5, 39.6,
  39.983 s). Fixes from the measure asserts before the smoke pass: the
  spun event row (55 characters) was 1001 px at 32 px, so both event
  rows went to 28 px (876 and 490 px); the spun label (733 px at 40)
  met the right-column readouts on the same row, so the "slid" and
  "spin" readouts moved to the speed and clock rows.
- Full render: media/spinslide/render.log: loop check 0 px (max diff
  0), periodicity 0 px, loop step 7074 px (the crossfade into the first
  frame); footage.mp4 40.00 s at 60 fps, 2400 frames, 1080x1920.
- Hook pre-tests (media/spinslide/hooks/pretest.log, each one take):
  hook1 "Does spinning a coaster make it slide farther?" ok, 2.29 s
  (the question from 0 s of voice, done by 2.9 s of video); hook2
  "Slide a coaster, spun or not: which one goes farther?" FAILED ("spun"
  came back "spawn"); hook3 "Push a coaster plain or spinning: which one
  slides farther?" FAILED ("plain" came back "plane"); hook4 hook1 plus
  "Same table, same push, one meter a second, shown four times slower."
  ok, 6.91 s. Chosen hook1: the brief's question, first thing said,
  identical to the title and the payoff. Word pre-tests: "plain" came
  back "plane" in all four places (words take), "its spin and its
  slide" lost an "s" (words2), "the other one seventeen" came back
  "117" and three "centimeters" came back "cm" (words3); "coaster",
  "the spun one", "spinning", "but spinning", "thirty four
  centimeters", "twice as far", "the one with no spin seventeen", "the
  grip is shared between the spin and the slide", "only part of the
  friction", "stop at the same instant", "not one after the other"
  all passed.
- Narration projects/spinslide/narration.txt, 112 words; the question
  is the first sentence and is repeated word for word before the
  payoff; one setup number (one meter a second), the payoff beat
  carries thirty four and seventeen.
- Voice round trip media/spinslide/voice.log: pass 1 ok (35.26 s). 1
  pass.
- Timing media/spinslide/timing.log (offset 0.6 s): the question 0.60
  to about 2.9 s ("Does spinning a coaster make it slide farther? Same
  table, same push." 0.60 to 4.36 s as one piece); "one meter a second"
  4.36 to 5.69 s; the repeated question 27.51 to 29.90 s; "Yes" 29.90
  s; "thirty four" 31.6 to 32.4 s and "centimeters" to about 33.1 s
  (whisper on 0.7 to 1.0 s slices); "seventeen" 34.0 to 34.7 s;
  "twice as far" 34.7 to 35.86 s; the voice ends at 35.86 s of video.
  The spun coaster stops (event row lit) at 27.12 s and again at 35.12
  s; the card rises from 31.2 s (up by 31.8 s) as "thirty four" is
  spoken, and the cycle-5 stop at 35.12 s lands on "twice as far".
- Compose media/spinslide/compose.log: music seed 124, 40.00 s;
  captions 20 pauses detected, 20 matched, max chunk start shift 1.282
  s against word-count timing; final.mp4 40.000000 s; preview.mp4
  (40.07 s) and sheet.png written.

### Local QA

- ffprobe final.mp4: h264 1080x1920 at 60/1, aac 22050 Hz mono,
  duration 40.000000 s, 2400 frames; atoms ftyp, moov at 32, free,
  mdat (faststart); 3923935 bytes; md5
  8355a5018066ced466b23afc78aae6fa.
- Caption and overlay bands: signalstats YMAX of footage.mp4 rows 1440
  to 1530 is 28 and rows 96 to 130 is 28 (background only).
- Captions: 38 caption chunks plus the overlay "10 cm coaster, grip 0.3
  | no seed" in media/spinslide/captions.filter; the joined caption
  text equals the narration word for word (112 words) after undoing
  the drawtext escapes; first captions "Does spinning a" 0.600 to
  1.379 s, "coaster make it" 1.379 to 2.159 s, "slide farther?" 2.159
  to 2.881 s; "thirty four" 31.824 to 32.411 s; "far." 35.385 to 35.860
  s.
- Full-resolution frames viewed (media/spinslide/qa-*.png): 0.00 s
  overlay, two-row title, both coasters at rest on the start line with
  the fingertips moving in (motion in frame one); 1.00 s both sliding
  (plain 10.2 cm at 0.63 m/s, spun 11.4 cm at 0.82 m/s and 5.2
  turns/s, the stripe turned), caption "Does spinning a"; 2.10 s the
  plain coaster stopped with its gold event row "plain: stopped at
  0.34 s, 17 cm", "slid 17.0 cm" gold, the gold ruler tick at 17, the
  spun one at 28.5 cm still turning; 3.20 s both stopped, "spun:
  stopped at 0.66 s, 34 cm, spin and slide together", the legend "same
  table, same push, 1/4 speed"; 20.00 s both stopped, caption "so the
  slide feels"; 31.50 s the card rising under "The spun one slides";
  35.20 s the card fully up, both event rows lit by the cycle-5 stop,
  caption "seventeen: twice as"; 39.983 s (frame 2399) the same
  picture as frame 0 (raw frames identical; decoded final frames differ
  only by encoder noise on text edges, 4153 px over 24, max 95, mean
  0.52). Nothing clipped at the frame edge; no text meets a disc, the
  table, the ruler or the fingertips.
- sheet.png (8x5 at 1 fps): 40 cells, the captions in order, the plain
  coaster stopped at 17 and the spun one at 34 in every cycle, the
  card from 32 s, the loop closes on the first frame.
- Phone read: the 200 px discs and their stripes are large; at 1/4
  speed the spun coaster takes 157 frames to stop and its stripe turns
  2.09 times, so the spin and the slide visibly die together; the two
  stop positions sit 17 cm apart on the same ruler.

### Metadata

- projects/spinslide/metadata.json written by
  media/spinslide/metadata.py with asserts: title 85 characters (at
  most 100), description 3353 characters (under 5,000), ASCII, no angle
  brackets, 12 tags; every number in the title and description (81
  distinct, commas stripped) appears in media/spinslide/measure.log.
- Title: Does spinning a coaster make it slide farther? Yes: 34 cm
  against 17 cm, twice as far
- privacyStatus private, categoryId 27, containsSyntheticMedia true,
  selfDeclaredMadeForKids false.

### Deviations from the brief

- Narration says "a coaster with no spin", "the top one" and "the one
  with no spin" instead of "plain": whisper returned "plane" for every
  "plain" in two pre-tests. The on-screen label "plain coaster", the
  title and the card keep the brief's word. The payoff reads "Yes. The
  spun one slides thirty four centimeters, the one with no spin
  seventeen: twice as far."
- The mechanism sentence says "only part of the friction", not "only
  part of the braking" (brake/break is a known mishearing), and "the
  spin and the slide stop at the same instant" instead of "its spin and
  its slide" (whisper dropped an "s").
- The event rows are 28 px, not 32 or 40: the spun row (55 characters)
  is 876 px at 28 and 1001 px at 32.
- The right-column readouts "slid" and "spin" / "no spin" sit on the
  speed and clock rows (120 and 156 px under the band top), not on the
  label rows: the spun label is 733 px wide at 40 px and would meet
  them.
- The two motions do not fall under the 2e-3 m/s bound on the same RK4
  step: |v| on step 3275, R |omega| on step 3277 (0.4 ms apart) because
  v / (R omega) = 0.65 at the end, so v crosses the bound first. The
  check is recorded as "within 3 steps" plus the extrapolated zero
  crossings (0.003 ms apart), which is the same-instant evidence.
- The brief's "1.5 J/kg" and "spin-only stops at about 0.5098 s" are
  the 40 rad/s values; at 40.87 rad/s the sim gives 1.5440 J/kg and
  0.5206 s (closed form 0.5209 s). Both are checked against their own
  closed forms; the 40 rad/s values are checked as written.
- The slide friction at the fixed point is 0.613 of mu g (61 percent),
  against the brief's about 0.616 (62 percent); within the 0.01
  tolerance, and the card says 61 percent.
- The finger mark is a fingertip seen from above (the view is
  top-down) that touches the rim, off-centre for the spun coaster; the
  brief's side-on finger mark would not fit left of a 200 px disc
  starting at x 150.
- payoff_t 31.2 s (the card up by 31.8 s as "thirty four" is spoken at
  31.6 s, after the cycle-4 stop at 27.12 s whose event row fades at
  31.5 s); the cycle-5 stop at 35.12 s lands on "twice as far".

## Niche note

[produced 2026-10-10 as "Does spinning a coaster make it slide farther?
Yes: 34 cm against 17 cm, twice as far"; measured plain coaster at 1.0
m/s on grip 0.3 stopped at 0.3394 s after 16.99 cm (closed form 0.3399
s); spun at 40.87 rad/s (6.50 turns/s) stopped at 0.6554 s after 33.99
cm, ratio 2.000, |v| and R |omega| under the bound 0.4 ms apart, zero
crossings 0.003 ms apart, v / (R omega) at the stop 0.649 (Farkas
0.653), the slide feels 0.613 of mu g; 40 rad/s 33.43 cm (1.967x), 20
rad/s 1.275x, 80 rad/s 3.567x, 0.5 m/s 3.639x, 1.5 m/s 1.506x; 24
checks, 0 failed; 1/4 speed; task 20261010-103215]

## Upload

- Attempt 1 of 5 recorded at 2026-10-10T11:09:08+03:00 (quota day 2026-10-10T10:00 EEST), scripts/yt-upload.py spinslide, md5 8355a5018066ced466b23afc78aae6fa.
- Uploaded private as yYRaj_ALn1k at 2026-10-10T08:09:11Z; scripts/yt-qa.py --wait --publish gate 15 of 15 on the first processed read; published 2026-10-10T11:10:07+03:00, re-read public; 55 units; attempt cost 1,655 units. https://youtu.be/yYRaj_ALn1k
