# Produce short: Ball at a 3 cm step, 0.7 beside 0.9 m/s, does it get up

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day36

## Goal

Backlog idea (trend research 2026-09-30, task 20260930-100404, pillar 2
chaos and physics, everyday mechanics; read the full entry under "Added
by trend research 2026-09-30" in docs/niche.md): "Kerb hop: a football
(R 11 cm) rolling at 0.7 m/s beside 1.0 m/s into a 3 cm kerb, the ball
grabbing the edge without slip and pivoting about it; measure whether it
climbs; expect the threshold 0.805 m/s (sqrt(2 g h / (1 + k)) / (1 - h /
((1 + k) R)); the edge keeps 0.805 of the spin), the 0.7 m/s ball to rise
2.27 of the 3 cm, drop back onto the floor at 0.344 s and roll back at
0.454 m/s, and the 1.0 m/s ball to be on top at 0.142 s rolling on at
0.478 m/s with the edge force never below 0.126 weights; above 1.10 m/s
the edge force is negative at the first touch and the model ends (a real
ball bounces off the kerb), and a 5 cm kerb has no window at all for this
ball (needs 1.24 m/s but flies above 1.14); a bike-wheel ring (R 33 cm)
takes a 10 cm kerb from 1.17 m/s; the floor landing kills the vertical
speed; RK4 pivot plus stepped Coulomb slip; repeat the roll;
deterministic, no seed."

Orchestrator notes (2026-10-04, before this brief; closed forms in
/tmp/day36/closed.py, g = 9.807). Two changes to the research entry.
First, the research used k = 2/5, which is a SOLID ball, not a hollow
football: call it a solid ball 22 cm across (R = 11 cm, I = (2/5) m R^2,
m cancels) and give the hollow-shell variant (k = 2/3, threshold 0.7104
m/s) in the description only. Second, the fast panel is 0.9 m/s, not 1.0:
pivoting about the edge without slip needs a tangential force of k / (1 +
k) m g sin(phi) = 0.2857 m g sin(phi) against a normal force N = m g
cos(phi) - m R omega^2, and at the first touch of a 1.0 m/s ball that is
a grip of 1.55 (N only 0.126 weights); at 0.9 m/s it is 0.82 (N 0.241
weights), which a grippy rubber ball on a rough concrete edge can give.
Say in the description that the ball grips the edge and never slips
there, and print the grip the edge must give (the largest ratio of the
tangential to the normal force during the pivot, and the ratio of the
tangential to the normal impulse at the grab).

The model: a level floor meets a step (a low kerb) of height h = 3 cm
with a sharp edge; the top of the step is level and continues to the
right. A solid ball of radius R = 11 cm rolls without slipping on the
floor at v0 toward the step (top panel v0 = 0.7 m/s, bottom panel 0.9
m/s), its spin omega0 = v0 / R. The ball's surface at the height of the
edge is sqrt(R^2 - (R - h)^2) = 7.55 cm ahead of its centre and lower
parts of the ball are nearer the centre line, so the first contact is
the edge itself: the centre is then at angle phi0 = acos((R - h) / R) =
43.34 degrees from the vertical over the edge. Grab: the ball catches the
edge and from that instant rolls about it without slipping (the material
point at the edge is at rest), so angular momentum about the edge is
conserved through the grab: m v0 (R - h) + k m R^2 omega0 = (1 + k) m R^2
omega1, omega1 = (v0 / R) (1 - h / ((1 + k) R)) = 0.8052 v0 / R (the edge
keeps 0.8052 of the spin; the lost 0.1948 is the grab's loss). Pivot: a
rigid body about the fixed edge, (1 + k) m R^2 phi'' = m g R sin(phi), phi
measured from the vertical over the edge toward the floor side; the ball
climbs while phi falls toward 0; integrate with RK4 at dt = 1e-5 s and
check energy (1/2)(1 + k) R^2 phi'^2 + g R cos(phi) constant to 1e-12 per
unit mass; the normal force N / (m g) = cos(phi) - R phi'^2 / g must stay
positive (print its minimum) and the needed grip is (k / (1 + k))
sin(phi) / (N / m g) (print its maximum). Over the top: when phi reaches
0 the centre is over the edge and the ball's lowest point touches the
top of the step at the edge; the pivot speed R phi' equals the rolling
speed, so the ball rolls on along the top without slipping at v_top = R
|phi'| = sqrt((omega1 R)^2 - 2 g h / (1 + k)) with no further loss (say
so). Fall back: if phi' reaches 0 before phi reaches 0 (energy (1/2)(1 +
k) (omega1 R)^2 under g h), the ball rises (1 + k)(omega1 R)^2 / (2 g)
above the floor at its highest, pivots back down, and returns to the
floor at the start geometry with phi' = +omega1 (energy conserved on the
pivot); its centre then moves back at omega1 (R - h) and down at omega1
sqrt(R^2 - (R - h)^2); the floor landing is plastic (the floor kills the
downward speed; say so) and the ball leaves the edge; angular momentum
about the floor contact is conserved through the landing: L = m R
(omega1 (R - h)) + k m R^2 omega1 = (1 + k) m R v_back, so v_back = omega1 ((R - h) + k R) / (1 + k) (the needed floor
grip is the horizontal over the vertical impulse: (v_back - omega1 (R -
h)) / (omega1 sqrt(R^2 - (R - h)^2)), print it); the ball then rolls back
left at v_back without slipping. Threshold: v* = sqrt(2 g h / (1 + k)) /
(1 - h / ((1 + k) R)) = 0.8052 m/s at which the ball just reaches the top
with zero speed. The edge-force limit: N = 0 at the first touch when
omega1 = sqrt(g (R - h)) / R, v0 = 1.100 m/s; above it the model ends (a
real ball bounces off), say so in the description. Shown at 1/10 speed.

Checks, not facts (the sim must print and compare; state them as checks):
phi0 = 43.34 degrees, the edge 7.55 cm ahead of the centre at the touch;
omega1 / omega0 = 0.8052; threshold v* = 0.8052 m/s; 0.7 m/s: omega0
6.364 rad/s, omega1 5.124 rad/s, rises 2.268 cm of the 3 cm (closed form
(1 + k)(omega1 R)^2 / (2 g)), highest at 0.172 s, back on the floor at
0.3443 s after the touch moving back 0.410 m/s and down 0.387 m/s, rolls
back at 0.4538 m/s, minimum edge force 0.433 weights, needed edge grip
0.453 at the touch (its maximum), needed floor grip about 0.11; 0.9 m/s:
omega0 8.182 rad/s, omega1 6.588 rad/s, over the edge at 0.1845 s after
the touch, rolls on along the top at 0.3238 m/s (closed form sqrt((omega1
R)^2 - 2 g h / (1 + k))), minimum edge force 0.241 weights, needed edge
grip about 0.82 at the touch (its maximum); the grab's impulse ratio
(tangential over normal) about 0.11 for both; half-step rerun (dt 5e-6)
agrees within 1e-6 s on the event times. For the description: 1.0 m/s
over at 0.1424 s rolling on at 0.4775 m/s but needing a grip of 1.55 at
the touch (N 0.126 weights); 0.8 m/s rises 2.962 cm, back on the floor at
0.7287 s, rolls back at 0.5187 m/s; 1.1 m/s: the edge force is zero at
the touch (the limit, over at 0.1194 s at 0.6035 m/s); a hollow ball (k =
2/3) of the same size: threshold 0.7104 m/s; a 5 cm step for this ball:
threshold 1.2393 m/s but the edge force is negative above 1.1359 m/s, so
no speed takes it; a bike-wheel ring (R 33 cm, k = 1) takes a 10 cm kerb
from 1.1671 m/s. Print the position and speed tables at 20 ms intervals
for both balls (centre x and height, phi, phi', N / m g, the needed
grip), the energy residuals, the schedule in video time, the text widths
and the layout clearances.

Drawing: two stacked bands (y 330 to 880 and 880 to 1430), side view, the
same floor and step drawn the same way at the same scale, 0.7 m/s on top
(the "no" case) and 0.9 m/s below (the "yes" case), 1000 px per metre
(the ball 220 px across, the step 30 px tall) with the step's edge at x
640 in both bands and the floor surface 470 px under the band top (y 800
and 1350), the step top 440 px under the band top, a lighter slab for the
floor and the step down to 520 px under the band top; the ball a lighter
disc with a spoke mark (a radius line and a dot) so the spin reads, a
thin dashed trail of the centre; the edge drawn as a small bright corner
mark that lights gold while the ball pivots on it; a short height scale
beside the step (0 to 3 cm, ticks every 1 cm) so the 2.3 cm rise reads.
Schedule (video time, 1/10 speed; cycle 10 s = 600 frames, 4 cycles in
40 s, exactly periodic, the last frame equal to the first): both balls
start 0.0 s into the cycle at 3.0 s of video from the touch (the 0.7 m/s
ball's centre 21.0 cm + 7.55 cm from the edge, the 0.9 m/s ball's 27.0 cm
+ 7.55 cm, so both touch the edge at 3.00 s of the cycle); the 0.9 ball
is over the top at 3.00 + 1.845 = 4.85 s and rolls on at 0.3238 m/s
(16.7 cm by the end of the cycle, so its centre ends about 23 cm right of
the edge, inside the band); the 0.7 ball is highest at 4.72 s, back on
the floor at 6.44 s and rolls back at 0.4538 m/s (16.2 cm by the end,
ending about 24 cm left of the edge); the gold event row of each band
lights at its settled result ("over the top at 0.18 s, rolls on at 0.32
m/s" and "falls back at 0.34 s, rose 2.3 of 3 cm"); the reset crossfade
runs over the last 0.6 s of each cycle. Readouts (28 px): left column
"speed 0.70 m/s" and the state word ("rolling", "on the edge", "over the
top", "falling back", "rolling back"), right column "rise N.N cm" live
and the shared clock in real seconds since the touch. Legend row after
the title: "same ball, same step, 1/10 speed". Overlay: "solid ball 22 cm
| step 3 cm | 1/10 speed | no seed" (measure it).

Day thirty-six, first slot. Chosen because "does it make it" thresholds
on everyday motion are the channel's strongest format (loop the loop
967, pendulum and peg, car over a hump 2 with a weak feed day; ice cube
or ball uphill 974, stopping distance 1,012), the panels end visibly
differently (one ball sits on the step and rolls away, the other rolls
back where it came from), the threshold is exact and the repeat is a
natural loop. Question in the first two seconds: "Roll a ball at a step.
Does it get up?" (keep the question identical in the title, the hook and
the payoff; "Does it make it up?" is an alternative, pre-test both).
Setup number: three centimeters (the step) with the two speeds spoken as
"zero point seven meters a second" and "zero point nine" (pre-test "zero
point seven"; "seven tenths of a meter a second" is the fallback).
Payoff: at zero point seven, no: it climbs two of the three centimeters
and rolls back; at zero point nine, yes, it is up and away; the limit is
zero point eight (speak at most two numbers in the payoff beat; the
times go to the card). The mechanism sentence must follow the picture:
the ball catches the edge and swings up over it like a pendulum stood on
its head; the swing costs a fifth of its spin at the catch, and the rest
must lift it three centimeters (say "swing" and "lift", never "pull" as
a noun; "momentum" is fine if the catch is on screen). Whisper risks:
"kerb" (avoid in narration; say "step"), "step" and "steps" (pre-test),
"zero point seven" and "zero point nine" (pre-test), "climbs", "rolls
back", "gets up" (pre-test), "pivots" (avoid; say "swings"), "edge"
(pre-test), avoid "do you", avoid "fly", avoid "pull" as a noun. Pre-test
hooks with scripts/voiceover.sh and keep the one whose question lands
earliest under two seconds. Measure every fixed text line with PIL
before rendering and keep every line under 950 px, and the title under
100 characters with no < or >. Music seed 110. Templates:
sims/deskchain (two bands, layout asserts, the clock, the crossfade, the
loop checks), sims/wallbounce (a rolling ball with a spin mark on a
table in two bands, a state word per phase, event rows), sims/uphill (a
rolling ball on a surface with a fillet, the height scale). Sim name
kerbhop: sims/kerbhop/kerbhop.py, projects/kerbhop/, media/kerbhop/.

## Claim (expected; the sim's numbers replace these)

A solid ball 22 cm across rolls at a 3 cm step. At 0.7 m/s it catches
the edge, swings up 2.3 of the 3 cm, falls back onto the floor 0.34 s
after the touch and rolls back at 0.45 m/s; at 0.9 m/s it is over the
top 0.18 s after the touch and rolls on along the step at 0.32 m/s. The
limit is 0.805 m/s: sqrt(2 g h / (1 + k)) / (1 - h / ((1 + k) R)), the
catch keeping 0.805 of the spin. Narrated: three centimeters (setup),
zero point seven and zero point nine meters a second; no and yes, the
limit zero point eight (payoff). Card: the question; 0.7: rose 2.3 cm,
back at 0.34 s, rolls back 0.45 m/s; 0.9: over at 0.18 s, on at 0.32
m/s; the limit 0.81 m/s; the catch keeps 0.81 of the spin; above 1.10
m/s it bounces off. Description: the model statement, the equations, the
two runs, the grips needed, the variants (1.0, 0.8, 1.1 m/s, the hollow
ball, the 5 cm step, the bike wheel), the checks.

## Claim

A solid ball 22 cm across (R = 11 cm, k = 0.4) rolls without slipping
at a 3 cm step with a sharp edge (g = 9.807 m/s^2); it grips the edge
and pivots about it. The catch keeps 0.8052 of the spin (conserved
angular momentum about the edge, a loss of 0.1948, about one fifth). At
0.7 m/s the ball rises 2.2676 cm of the 3 cm, is highest at 0.1722 s,
is back on the floor at 0.3443 s after the touch and rolls back at
0.4538 m/s; at 0.9 m/s it is over the edge at 0.1845 s and rolls on
along the step at 0.3238 m/s. The limit is v* = sqrt(2 g h / (1 + k)) /
(1 - h / ((1 + k) R)) = 0.8052 m/s; above 1.1000 m/s the edge force is
negative at the touch and the model ends. RK4 at dt 1e-5 s agrees with
the closed forms to 1e-15 and the half-step rerun to +0.0e+00. Narrated:
three centimeters, zero point seven and zero point nine meters a second
(setup); a fifth of its spin (mechanism); at zero point seven no, it
climbs two of the three centimeters and rolls back; at zero point nine
yes; the limit is zero point eight (payoff). Card: the question; 0.7
m/s no, 0.9 m/s yes, limit 0.81 m/s; 0.7 rose 2.3 of 3 cm, back at
0.34 s; 0.9 over at 0.18 s, rolls on at 0.32 m/s; the catch keeps 0.81
of the spin; above 1.10 m/s it bounces off the edge.

## Evidence

### Measurements

The final measure.log (media/kerbhop/measure.log, 2026-10-04 18:10:01
to 18:10:02 EEST, exit 0, written by sims/kerbhop/kerbhop.py with
projects/kerbhop/manifest.json --measure-only; identical, apart from the
timestamps, to the producer's run at 10:37:57, kept at
/tmp/day36/kerbhop-measure-1038.log; the final render at 18:10:02 to
18:10:46 printed the same numbers):

```
Sun Oct  4 06:10:02 PM EEST 2026
warning: Git tree '/home/alex/personal/seedzero' is dirty
setup: side view, two panels on one clock, the same level floor and the same step of h = 3 cm with a sharp edge (the top level and continuing to the right); a solid ball of radius R = 11 cm (22 cm across, I = 0.4 m R^2, m cancels) rolls without slipping on the floor at v0 toward the step, spinning at omega0 = v0 / R; top panel v0 = 0.7 m/s, bottom panel 0.9 m/s; g = 9.807 m/s^2; the ball grips the edge and never slips there (the grip it needs is printed); the pivot about the edge integrated by RK4 at dt = 1e-05 s with compensated summation, the events located by bisection inside the step, checked against the energy, the closed forms and a half-step rerun; the floor landing is plastic (the floor kills the downward speed) and conserves angular momentum about the floor contact; shown at 1/10 speed on a 10 s cycle (600 frames) with the touch 3 s into the cycle, 4 cycles in 40 s; drawn at 1000 px per metre (the ball 220 px across, the step 30 px tall); deterministic, no seed
geometry: the ball's surface at the height of the edge is d0 = sqrt(R^2 - (R - h)^2) = 7.5498 cm = 7.55 cm ahead of its centre, and at every lower height the half-chord is smaller (at most 7.5392 cm under the edge height), so the first contact is the edge itself; the centre is then phi0 = acos((R - h) / R) = 43.3418 degrees = 43.34 degrees from the vertical over the edge; the grab keeps omega1 / omega0 = 1 - h / ((1 + k) R) = 0.8052 of the spin and loses 0.1948, about one fifth (1/5 = 0.2000); the energy kept through the grab is keep^2 = 0.6483; the grab's impulse ratio, tangential over normal, is (h / R)(k / (1 + k)) / sin(phi0) = 0.1135 for any v0; the floor landing needs a grip (horizontal over vertical impulse) of k h / ((1 + k) d0) = 0.1135 for any v0; threshold v* = sqrt(2 g h / (1 + k)) / (1 - h / ((1 + k) R)) = 0.8052 m/s = 0.81 m/s = 0.8 m/s (the ball just reaches the top with zero speed); edge-force limit: N = 0 at the first touch when omega1 = sqrt(g (R - h)) / R = 8.0523 rad/s, v0 = 1.1000 m/s = 1.10 m/s; above it the edge force is negative at the touch and the model ends (a real ball bounces off)
0.7 m/s (top panel): omega0 = 6.3636 rad/s = 1.013 turns/s, omega1 = 5.1240 rad/s = 0.816 turns/s after the grab; under the threshold by 0.1052 m/s; at the touch the edge force is 0.4328 weights and the grip needed 0.4531; RK4: the energy (1/2)(1 + k)(omega1 R)^2 = 0.2224 J/kg is under g h = 0.2942 J/kg, so it falls back: highest at 0.1722 s after the touch with the centre 2.2676 cm = 2.268 cm = 2.3 cm above its floor level, about 2 of the 3 cm (closed form (1 + k)(omega1 R)^2 / (2 g) = 2.2676 cm, diff -1.0e-15 cm; phi at the top 21.03 degrees), 0.73 cm short of the top; back on the floor at 0.3443 s = 0.34 s after the touch (2 x the time to the top) with phi' = 5.1240 rad/s (omega1 5.1240), the centre moving back at omega1 (R - h) = 0.4099 m/s and down at omega1 d0 = 0.3869 m/s; the floor kills the downward speed and the ball rolls back at v_back = omega1 ((R - h) + k R) / (1 + k) = 0.4538 m/s = 0.45 m/s, spinning at 4.1258 rad/s (the floor grip needed 0.1135); the edge force N / (m g) is at least 0.4328 weights (at 0.0000 s) and the grip the edge must give is at most 0.4531 (at 0.0000 s, the touch); the grab's impulse ratio is 0.1135; the energy stays within 2.2e-16 J/kg of 1.006940 J/kg over 34431 steps; half-step rerun (dt = 5e-06 s): highest at 0.1721521 s (+0.0e+00 s), back at 0.3443042 s (+0.0e+00 s), rise 2.2675657 cm (+0.0e+00 cm), rolls back at 0.4538371 m/s (+0.0e+00 m/s)
0.9 m/s (bottom panel): omega0 = 8.1818 rad/s = 1.302 turns/s, omega1 = 6.5880 rad/s = 1.049 turns/s after the grab; over the threshold by 0.0948 m/s; at the touch the edge force is 0.2405 weights and the grip needed 0.8155; RK4: over the edge (phi = 0) at 0.1845 s after the touch, rolling on along the top at 0.3238 m/s = 0.32 m/s (closed form sqrt((omega1 R)^2 - 2 g h / (1 + k)) = 0.3238 m/s, diff +0.0e+00 m/s) with no further loss, spinning at 2.9437 rad/s; the rise is the full 3 cm; the edge force N / (m g) is at least 0.2405 weights (at 0.0000 s) and the grip the edge must give is at most 0.8155 (at 0.0000 s, the touch); the grab's impulse ratio is 0.1135; the energy stays within 2.2e-16 J/kg of 1.152168 J/kg over 18446 steps; half-step rerun (dt = 5e-06 s): over at 0.1844561 s (+0.0e+00 s) at 0.3238122 m/s (+5.6e-17 m/s)
the two panels: at 0.7 m/s the ball catches the edge, swings up 2.3 of the 3 cm and falls back onto the floor 0.34 s after the touch, rolling back at 0.45 m/s; at 0.9 m/s it is over the top 0.18 s after the touch and rolls on along the step at 0.32 m/s; the limit is 0.8052 m/s = 0.81 m/s = 0.8 m/s; the catch keeps 0.8052 = 0.81 of the spin and costs 0.1948, about one fifth; the rest must lift the centre 3 cm
table 0.7 m/s (RK4 table, real time after the touch; x from the edge, y the centre's height above the floor; N in weights): 0.0000 s: x -7.55 cm, y 11.00 cm, phi 43.34 deg, phi' -5.124 rad/s, N 0.433, grip 0.453; 0.0200 s: x -6.77 cm, y 11.67 cm, phi 37.95 deg, phi' -4.296 rad/s, N 0.582, grip 0.302; 0.0400 s: x -6.07 cm, y 12.18 cm, phi 33.46 deg, phi' -3.554 rad/s, N 0.693, grip 0.227; 0.0600 s: x -5.46 cm, y 12.55 cm, phi 29.78 deg, phi' -2.888 rad/s, N 0.774, grip 0.183; 0.0800 s: x -4.96 cm, y 12.82 cm, phi 26.82 deg, phi' -2.285 rad/s, N 0.834, grip 0.155; 0.1000 s: x -4.57 cm, y 13.01 cm, phi 24.52 deg, phi' -1.734 rad/s, N 0.876, grip 0.135; 0.1200 s: x -4.27 cm, y 13.14 cm, phi 22.83 deg, phi' -1.224 rad/s, N 0.905, grip 0.123; 0.1400 s: x -4.07 cm, y 13.22 cm, phi 21.71 deg, phi' -0.742 rad/s, N 0.923, grip 0.114; 0.1600 s: x -3.96 cm, y 13.26 cm, phi 21.12 deg, phi' -0.278 rad/s, N 0.932, grip 0.110; 0.1800 s: x -3.95 cm, y 13.26 cm, phi 21.07 deg, phi' +0.179 rad/s, N 0.933, grip 0.110; 0.2000 s: x -4.04 cm, y 13.23 cm, phi 21.54 deg, phi' +0.641 rad/s, N 0.926, grip 0.113; 0.2200 s: x -4.22 cm, y 13.16 cm, phi 22.54 deg, phi' +1.118 rad/s, N 0.910, grip 0.120; 0.2400 s: x -4.49 cm, y 13.04 cm, phi 24.11 deg, phi' +1.621 rad/s, N 0.883, grip 0.132; 0.2600 s: x -4.87 cm, y 12.86 cm, phi 26.27 deg, phi' +2.162 rad/s, N 0.844, grip 0.150; 0.2800 s: x -5.35 cm, y 12.61 cm, phi 29.08 deg, phi' +2.753 rad/s, N 0.789, grip 0.176; 0.3000 s: x -5.93 cm, y 12.27 cm, phi 32.61 deg, phi' +3.405 rad/s, N 0.712, grip 0.216; 0.3200 s: x -6.61 cm, y 11.79 cm, phi 36.91 deg, phi' +4.129 rad/s, N 0.608, grip 0.282; 0.3400 s: x -7.37 cm, y 11.16 cm, phi 42.10 deg, phi' +4.938 rad/s, N 0.468, grip 0.409; 0.3443 s: x -7.55 cm, y 11.00 cm, phi 43.34 deg, phi' +5.124 rad/s, N 0.433, grip 0.453
table 0.9 m/s (RK4 table, real time after the touch; x from the edge, y the centre's height above the floor; N in weights): 0.0000 s: x -7.55 cm, y 11.00 cm, phi 43.34 deg, phi' -6.588 rad/s, N 0.240, grip 0.816; 0.0200 s: x -6.51 cm, y 11.87 cm, phi 36.27 deg, phi' -5.774 rad/s, N 0.432, grip 0.391; 0.0400 s: x -5.51 cm, y 12.52 cm, phi 30.06 deg, phi' -5.079 rad/s, N 0.576, grip 0.248; 0.0600 s: x -4.58 cm, y 13.00 cm, phi 24.59 deg, phi' -4.496 rad/s, N 0.683, grip 0.174; 0.0800 s: x -3.71 cm, y 13.35 cm, phi 19.72 deg, phi' -4.017 rad/s, N 0.760, grip 0.127; 0.1000 s: x -2.91 cm, y 13.61 cm, phi 15.34 deg, phi' -3.634 rad/s, N 0.816, grip 0.093; 0.1200 s: x -2.17 cm, y 13.78 cm, phi 11.36 deg, phi' -3.341 rad/s, N 0.855, grip 0.066; 0.1400 s: x -1.47 cm, y 13.90 cm, phi 7.66 deg, phi' -3.131 rad/s, N 0.881, grip 0.043; 0.1600 s: x -0.80 cm, y 13.97 cm, phi 4.15 deg, phi' -3.000 rad/s, N 0.896, grip 0.023; 0.1800 s: x -0.14 cm, y 14.00 cm, phi 0.75 deg, phi' -2.946 rad/s, N 0.903, grip 0.004; 0.1845 s: x -0.00 cm, y 14.00 cm, phi 0.00 deg, phi' -2.944 rad/s, N 0.903, grip 0.000
for the description (same ball, same 3 cm step unless said): 1 m/s: over at 0.1424 s, rolling on at 0.4775 m/s; edge force at the touch 0.1263 weights (its minimum 0.1263), grip needed at the touch 1.553 (its maximum 1.553); 0.8 m/s: rises 2.9617 cm (closed form 2.9617), highest at 0.3644 s, back on the floor at 0.7287 s, rolls back at 0.5187 m/s; edge force at the touch 0.3426 weights, grip needed 0.572; 1.1 m/s: over at 0.1194 s, rolling on at 0.6035 m/s; edge force at the touch 0.0001 weights (its minimum 0.0001), grip needed at the touch 3013.306 (its maximum 3013.306); a hollow ball (thin shell, k = 0.6667) of the same size: threshold 0.7104 m/s (keeps 0.8364 of the spin), edge-force limit 1.0591 m/s; a 5 cm step for this ball: threshold 1.2393 m/s but the edge force is negative at the touch above 1.1359 m/s, so no speed takes it (the ball bounces off before it can climb); a bike-wheel ring (R = 33 cm, k = 1) at a 10 cm kerb: threshold 1.1671 m/s, edge-force limit 1.7701 m/s (it keeps 0.8485 of the spin)
checks against the brief (37 checks, 0 failed): phi0 (degrees): brief 43.34, sim 43.342, diff +1.8e-03: ok; edge ahead of the centre (cm): brief 7.55, sim 7.5498, diff -1.7e-04: ok; omega1 / omega0: brief 0.8052, sim 0.80519, diff -5.2e-06: ok; threshold v* (m/s): brief 0.8052, sim 0.80515, diff -4.6e-05: ok; grab impulse ratio: brief 0.11, sim 0.11353, diff +3.5e-03: ok; floor grip: brief 0.11, sim 0.11353, diff +3.5e-03: ok; 0.7 m/s omega0 (rad/s): brief 6.364, sim 6.3636, diff -3.6e-04: ok; 0.7 m/s omega1 (rad/s): brief 5.124, sim 5.124, diff -3.3e-05: ok; 0.7 m/s rise (cm): brief 2.268, sim 2.2676, diff -4.3e-04: ok; 0.7 m/s highest at (s): brief 0.172, sim 0.17215, diff +1.5e-04: ok; 0.7 m/s back on the floor at (s): brief 0.3443, sim 0.3443, diff +4.2e-06: ok; 0.7 m/s moving back (m/s): brief 0.41, sim 0.40992, diff -8.3e-05: ok; 0.7 m/s moving down (m/s): brief 0.387, sim 0.38685, diff -1.5e-04: ok; 0.7 m/s rolls back at (m/s): brief 0.4538, sim 0.45384, diff +3.7e-05: ok; 0.7 m/s minimum edge force (weights): brief 0.433, sim 0.43278, diff -2.2e-04: ok; 0.7 m/s needed edge grip at the touch: brief 0.453, sim 0.45311, diff +1.1e-04: ok; 0.7 m/s needed floor grip: brief 0.11, sim 0.11353, diff +3.5e-03: ok; 0.9 m/s omega0 (rad/s): brief 8.182, sim 8.1818, diff -1.8e-04: ok; 0.9 m/s omega1 (rad/s): brief 6.588, sim 6.588, diff -4.3e-05: ok; 0.9 m/s over the edge at (s): brief 0.1845, sim 0.18446, diff -4.4e-05: ok; 0.9 m/s rolls on at (m/s): brief 0.3238, sim 0.32381, diff +1.2e-05: ok; 0.9 m/s minimum edge force (weights): brief 0.241, sim 0.24046, diff -5.4e-04: ok; 0.9 m/s needed edge grip at the touch: brief 0.82, sim 0.8155, diff -4.5e-03: ok; 1.0 m/s over at (s): brief 0.1424, sim 0.14238, diff -1.9e-05: ok; 1.0 m/s rolls on at (m/s): brief 0.4775, sim 0.47753, diff +3.4e-05: ok; 1.0 m/s needed grip at the touch: brief 1.55, sim 1.553, diff +3.0e-03: ok; 1.0 m/s edge force at the touch: brief 0.126, sim 0.12627, diff +2.7e-04: ok; 0.8 m/s rise (cm): brief 2.962, sim 2.9617, diff -2.8e-04: ok; 0.8 m/s back on the floor at (s): brief 0.7287, sim 0.72873, diff +3.3e-05: ok; 0.8 m/s rolls back at (m/s): brief 0.5187, sim 0.51867, diff -2.9e-05: ok; 1.1 m/s edge force at the touch: brief 0, sim 6.5078e-05, diff +6.5e-05: ok; 1.1 m/s over at (s): brief 0.1194, sim 0.11944, diff +4.3e-05: ok; 1.1 m/s rolls on at (m/s): brief 0.6035, sim 0.60348, diff -1.9e-05: ok; hollow ball threshold (m/s): brief 0.7104, sim 0.71043, diff +3.5e-05: ok; 5 cm step threshold (m/s): brief 1.2393, sim 1.2393, diff +4.3e-05: ok; 5 cm step edge-force limit (m/s): brief 1.1359, sim 1.1359, diff -2.4e-05: ok; bike-wheel ring threshold (m/s): brief 1.1671, sim 1.1671, diff +4.3e-05: ok
schedule (video time, 1/10 speed): cycles of 10 s start at -10.00, 0.00, 10.00, 20.00, 30.00 s (the first -0.00 s before the first frame); both balls roll in from 3 s before the touch, the 0.7 m/s ball's centre 28.55 cm and the 0.9 m/s ball's 34.55 cm left of the edge at the cycle start; both touch the edge 3 s into each cycle at 3.00, 13.00, 23.00, 33.00 s; the 0.9 m/s ball is over the top 1.84 s later at 4.84, 14.84, 24.84, 34.84 s (its event row lights) and rolls on at 0.3238 m/s, its centre 16.7 cm right of the edge at the end of the cycle; the 0.7 m/s ball is highest 1.72 s after the touch at 4.72, 14.72, 24.72, 34.72 s (the gold rise mark appears), back on the floor 3.44 s after the touch at 6.44, 16.44, 26.44, 36.44 s (its event row lights) and rolls back at 0.4538 m/s, its centre 23.7 cm left of the edge at the end of the cycle; the reset crossfade runs over the last 0.6 s of each cycle (from 9.40, 19.40, 29.40, 39.40 s; the readouts out over its first half and in over its second); on the first frame the cycle is 0.00 s in (-0.300 s real: both balls rolling in); title until 3 s; payoff card from 25.6 s; the title fades back in over the last 0.5 s and the last frame repeats the first (the scene is periodic: 40 s holds exactly 4 cycles)
text widths (the on-screen strings verbatim): overlay@34 853 px '22 cm ball | 3 cm step | 1/10 speed | no seed', title line 1@56 633 px 'Roll a ball at a step.', title line 2@56 478 px 'Does it get up?', legend@40 754 px 'same ball, same step, 1/10 speed', clock@28 363 px '0.344 s after the touch', clock before@28 264 px 'before the touch', label slow@40 322 px 'ball at 0.7 m/s', fixed slow@28 408 px 'limit 0.81 m/s, 0.11 under', event slow@40 818 px 'falls back at 0.34 s, rose 2.3 of 3 cm', label fast@40 322 px 'ball at 0.9 m/s', fixed fast@28 386 px 'limit 0.81 m/s, 0.09 over', event fast@40 775 px 'over at 0.18 s, rolls on at 0.32 m/s', speed@28 239 px 'speed 0.90 m/s', state rolling@28 102 px 'rolling', state on the edge@28 189 px 'on the edge', state falling back@28 184 px 'falling back', state over the top@28 195 px 'over the top', state rolling back@28 186 px 'rolling back', rise@40 248 px 'rise 3.0 cm', spin@28 266 px 'spin 1.30 turns/s', scale top@24 64 px '3 cm', scale bottom@24 17 px '0', peak@24 90 px '2.3 cm', payoff line 1@40 793 px 'roll a ball at a step: does it get up?', payoff line 2@40 889 px '0.7 m/s: no, 0.9 m/s: yes, limit 0.81 m/s', payoff line 3@40 809 px '0.7: rose 2.3 of 3 cm, back at 0.34 s', payoff line 4@40 876 px '0.9: over at 0.18 s, rolls on at 0.32 m/s', payoff line 5@40 726 px 'the catch keeps 0.81 of the spin', payoff line 6@40 879 px 'above 1.10 m/s it bounces off the edge'
row check: the left column ends at x 362 px, the right column starts at x 632 px; both end 134 px under the band top; the event row spans 156 to 196 px under the band top and x 131 to 949 px (widest 818 px, centred on 540); the floor surface is 470 px under the band top, the step top 440 px, the slab to 520 px, the edge at x 640; the ball is 220 px across, its top 250 px under the band top on the floor and 220 px on the step; centres at the cycle start x 354.5 (0.7) and 294.5 (0.9) px, at the fade start of the incoming cycle 312.5 and 240.5 px, at the cycle end 403.1 (0.7, rolling back) and 806.9 (0.9, on the step) px; the slow ball's centre at its peak x 600.5 px, its bottom 447.3 px under the band top (the step top at 440); the height scale on the step's side at x 910 (898 to 922) from 440 to 470 px, its labels from x 934 to 998 px; the gold rise mark runs from the ball's bottom to x 772 px with its label x 784 to 874 px at 447.3 px; each band is 550 px tall (y 330 to 880 and 880 to 1430); the caption band starts at y 1440; the title rows end at y 280 and the overlay band ends at y 130
Sun Oct  4 06:10:02 PM EEST 2026
```

Checks from the brief: the sim's own check block reports 37 checks, 0
failed (phi0 43.34 degrees, the edge 7.55 cm ahead; omega1 / omega0
0.8052; v* 0.8052 m/s; the grab's impulse ratio and the floor grip
0.1135; 0.7 m/s: omega0 6.364 and omega1 5.124 rad/s, rise 2.268 cm,
highest 0.172 s, back at 0.3443 s moving back 0.410 and down 0.387 m/s,
rolls back 0.4538 m/s, least edge force 0.433 weights, grip 0.453; 0.9
m/s: omega0 8.182 and omega1 6.588 rad/s, over at 0.1845 s, rolls on
at 0.3238 m/s, least edge force 0.241, grip 0.8155; the 1.0, 0.8 and
1.1 m/s variants, the hollow ball 0.7104 m/s, the 5 cm step 1.2393 and
1.1359 m/s, the bike-wheel ring 1.1671 m/s). The energy stays within
2.2e-16 J/kg on both pivots; the half-step rerun agrees to +0.0e+00 on
every event; the edge force stays positive on both pivots (its minimum
at the touch); the 20 ms tables, the schedule, the text widths and the
row check are printed and asserted.

### Production

- Sim: sims/kerbhop/kerbhop.py (two stacked bands, sims/deskchain
  layout; RK4 at 1e-5 s with Kahan summation on the pivot, bisection on
  the events, a half-step rerun; the grab and the floor landing as
  angular-momentum jumps; measure() prints every number, the text
  widths and the row check and asserts them). Manifest
  projects/kerbhop/manifest.json: seed 0, fps 60, scene_duration 40.0,
  slow 10.0 (1/10 speed), cycle_s 10.0, touch_at 3.0, title "Roll a
  ball at a step.|Does it get up?", title_until 3.0, payoff_t 25.6,
  payoff_hold 0.6, loop_fade 0.5, music_seed 110, music_gain 0.18,
  voice_offset 0.6, caption_y 0.75, overlay "22 cm ball | 3 cm step |
  1/10 speed | no seed" (853 px).
- Layout: 1000 px per metre, the edge at x 640 in both bands, the floor
  470 px and the step top 440 px under the band top, the ball 220 px
  across with a spoke mark and a dashed centre trail, the edge mark
  gold while the ball pivots, a 0 to 3 cm scale beside the step, the
  gold rise mark at the 0.7 m/s ball's peak; the row check in
  measure.log lists every clearance.
- Hook pre-tests (media/kerbhop/hooks/pretest.log, 10:32 to 10:33):
  hooks 1 to 4 passed the round trip, hook5 (27 words, with both
  speeds) failed; hook1 "Roll a ball at a step. Does it get up? The
  step is three centimeters." was kept (the question starts at 1.36 s
  of voice, 1.96 s of video; hook2 "Does it make it up?" 1.32 s, hook3
  1.46 s). The risky-words tests found "rolls in" losing "in"; the
  narration avoids "rolls in".
- Narration: projects/kerbhop/narration.txt, 108 words, the question
  "Roll a ball at a step. Does it get up?" first and repeated word for
  word before the payoff; setup three centimeters, zero point seven
  and zero point nine; mechanism "the ball catches it and swings up
  over it, like a pendulum stood on its head; the catch costs a fifth
  of its spin; the rest must lift the ball three centimeters"; payoff
  "at zero point seven, no, it climbs two of the three centimeters and
  rolls back; at zero point nine, yes, up and away; the limit is zero
  point eight".
- Voice (media/kerbhop/voice.log): pass 1 at 10:33:31, 108 words,
  "ok: transcript matches narration (33.192925s)". voice-timing.py
  (timing.log): the question at 0.60 to 4.42 s of video (the caption
  "Does it get up?" from 1.85 s), "At 0.7, No" at 24.21 to 26.10 s,
  "It climbs two of the three centimeters and rolls back" to 28.93 s,
  "At 0.9, yes, up and away" to 32.00 s, "The limit is 0.8" 32.00 to
  33.79 s; the voice ends at 33.79 s of video.
- Schedule and sync: touches at 3.0, 13.0, 23.0 and 33.0 s of video;
  "Watch the edge. The ball catches it and swings up over it" spoken
  at 11.34 to 14.53 s over the second cycle's touch at 13.0 s; the
  payoff card rises at 25.6 s as "At zero point seven, no" is spoken
  (24.21 to 26.10 s) while the third cycle's 0.7 m/s ball is at its
  peak (24.72 s) and falls back (26.44 s) under "climbs two of the
  three centimeters and rolls back"; the 0.9 m/s ball is over the top
  at 24.84 s with its event row lit under "At zero point nine, yes".
- Smoke frames (media/kerbhop/smoke-*.png, 17 frames at 0.0 to 39.983
  s) viewed by the producer at 10:33 to 10:39 before and after the
  render. The producer edited the sim once more at 10:39 after its
  10:38 render (a smoke frame at 9.55 s checking the crossfade), so the
  orchestrator re-measured (identical numbers) and re-rendered at
  18:10 before composing. Render log (media/kerbhop/render.log,
  18:10:02 to 18:10:46): 2400 frames, "loop check: last frame differs
  from the first in 0 px", "periodicity check: ... 0 px", the loop step
  6806 px (the title fading back in), footage.mp4 40.00 s at 60 fps.
- Compose (media/kerbhop/compose.log, 18:10:46 to 18:10:59): music seed
  110 40.00 s; "captions: 23 pauses detected, 23 matched, max chunk
  start shift 0.923 s against word-count timing"; final.mp4 40.000000
  s, preview.mp4, sheet.png 8x5 at 1 fps.
- Text widths: every on-screen string measured in measure.log at its
  drawn size, widest the payoff line 2 at 889 px, every line under 950
  px.

### Local QA (orchestrator, 2026-10-04 18:11 to 18:16 EEST)

- Frames extracted from final.mp4 at 0.00, 1.00, 2.10, 13.50, 26.00,
  27.40, 33.00, 36.50 and 39.983 s (media/kerbhop/qa-*.png) and viewed.
  0.00: overlay, the title "Roll a ball at a step. / Does it get up?",
  both bands with their labels, speed and spin readouts, the balls
  rolling in with spoke marks, the step with its edge mark and 3 cm
  scale, no caption. 2.10: both balls nearer the edge with dashed
  trails, caption "Does it get up?". 13.50: legend "same ball, same
  step, 1/10 speed", clock 0.050 s after the touch, both balls "on the
  edge" with the gold edge mark, rise 1.4 and 1.8 cm, caption "and
  swings up over". 26.00: 0.300 s after the touch, the 0.7 ball
  "falling back" at rise 1.3 cm with the gold 2.3 cm mark, the 0.9
  ball "over the top" on the step with its event row lit, the payoff
  card up, caption "no.". 27.40: 0.440 s after the touch, the 0.7 ball
  "rolling back" at 0.45 m/s with its event row "falls back at 0.34 s,
  rose 2.3 of 3 cm", the 0.9 ball rolling on along the step, the card
  up, caption "It climbs two of the". 36.50: 0.350 s after the fourth
  touch, both event rows lit, the card up, no caption (the voice has
  ended). 39.983: identical to frame 0. sheet.png (8x5 at 1 fps) shows
  the four cycles, the captions in order and the card from 26 s.
- Question timing: on screen from frame 0 in the title; spoken from
  0.60 s ("Roll a ball at a step." 0.60 to 1.85 s, "Does it get up?"
  1.85 to 2.77 s).
- Captions: 34 drawtext chunks from 0.600 to 33.793 s; their
  words match narration.txt word for word (108 of 108, checked by
  script after stripping punctuation).
- Payoff: "At zero point seven, no" spoken at 24.21 to 26.10 s with the
  card from 25.6 s carrying "0.7 m/s: no, 0.9 m/s: yes, limit 0.81
  m/s"; "the limit is zero point eight" at 32.00 to 33.79 s with the
  card's "limit 0.81 m/s" and the fixed readouts "limit 0.81 m/s, 0.11
  under / 0.09 over" on screen (measure.log prints the limit as 0.8052
  = 0.81 = 0.8 m/s).
- Bands: ffmpeg signalstats on footage.mp4 crops, caption band rows
  1440 to 1530 YMAX 28 and overlay band rows 96 to 130 YMAX 28 over all
  2400 frames (background only).
- Loop: render.log loop check 0 px; the last frame viewed equals the
  first.
- ffprobe final.mp4: h264 1080x1920 60/1 fps, duration 40.000000 s,
  aac 22050 Hz; atom order ftyp, moov, free, mdat (faststart).
- md5sum final.mp4: c7bbf34fb04b16a3c26aaa6bbf943e9b
- Narrated numbers against measure.log: three centimeters (h = 3 cm),
  zero point seven and zero point nine meters a second (v0 0.7 and 0.9
  m/s), a fifth of its spin (loses 0.1948, about one fifth), two of the
  three centimeters (2.2676 cm, "about 2 of the 3 cm"), the limit zero
  point eight (0.8052 m/s = 0.8 m/s): every one is a line in
  measure.log.
- Metadata numbers: all 89 distinct numbers in the description
  appear in measure.log (commas stripped, checked by script).

### Metadata

projects/kerbhop/metadata.json: title "Roll a ball at a 3 cm step. Does it get up? 0.7 m/s: no, 0.9 m/s: yes. The limit is 0.81 m/s" (92 characters,
ASCII, no < or >); description 4999 characters (the model and the
constants, "Measured:" bullets, "Why:", the rerun line, the agent
line; a first draft of 5,518 characters was cut to fit under 5,000);
12 tags (roll a ball at a step does it get up, ball rolling over a
step, kerb hop, rolling ball, rolling without slipping, angular
momentum, inverted pendulum, threshold speed, physics, physics
visualization, simulation, shorts); categoryId 27, privacyStatus
private, containsSyntheticMedia true, selfDeclaredMadeForKids false.

### Deviations from the brief

- The overlay reads "22 cm ball | 3 cm step | 1/10 speed | no seed"
  (the brief's "solid ball 22 cm | step 3 cm | ..." reworded, 853 px).
- The narration speaks "zero point eight" for the 0.8052 m/s limit
  while the card and the readouts show 0.81 m/s; measure.log prints
  both roundings.
- The producer agent stopped at about 10:39 after the render and the
  voice, before composing, the metadata and the evidence; the
  orchestrator re-measured and re-rendered (identical numbers),
  composed, ran QA and wrote the metadata and the evidence at 18:10 to
  18:16.

## Niche note

[produced 2026-10-04 as "Roll a ball at a 3 cm step. Does it get up? 0.7 m/s: no, 0.9 m/s: yes. The limit is 0.81 m/s"; measured threshold 0.8052 m/s, the
catch keeps 0.8052 of the spin, 0.7 m/s rises 2.2676 cm and is back on
the floor at 0.3443 s rolling back at 0.4538 m/s, 0.9 m/s is over at
0.1845 s rolling on at 0.3238 m/s, edge-force limit 1.1000 m/s; task
20261004-101248]

### Upload

- Attempt 2 of 5 of the quota day 2026-10-04T10:00 EEST, recorded at
  2026-10-04T18:14:25+03:00: scripts/yt-upload.py kerbhop failed at
  once with FileNotFoundError on projects/kerbhop/metadata.json before
  building the API client (the metadata write in the same script had
  failed its own length check, 5,518 characters, and a shell pipe hid
  the failure). No videos.insert call was made and no quota was used;
  counted as an attempt all the same, so the cap allows three more.
- Attempt 3 of 5: scripts/yt-upload.py kerbhop started at 2026-10-04T18:16:13+03:00 (videos.insert, 1,600 units), private.
- Outcome: uploaded private as jx6LnUOl1Aw (https://youtu.be/jx6LnUOl1Aw) at 2026-10-04T18:16:19+03:00, the insert succeeded on its first try.
- QA gate: scripts/yt-qa.py kerbhop jx6LnUOl1Aw --wait --publish run once in the foreground at 18:16:25: uploadStatus processed, processingStatus succeeded, hd, 1080x1920, title, description and tags match, categoryId 27, not made for kids, duration PT41S (40.000 s), private before publish; gate 15 of 15 on the first processed read.
- Published: privacyStatus public at 2026-10-04T18:17:14+03:00, re-read public, embeddable, madeForKids false. Quota this run 55 units; 1,655 units for the slot (attempt 2 used none).
- Niche note appended to the Kerb hop bullet in docs/niche.md at 2026-10-04T18:17:49+03:00.
