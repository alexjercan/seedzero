# Produce short: Carry a weight on a string, then stop at 1 s or 2 s, does it swing

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day36

## Goal

Research candidate (trend research run 11, 2026-10-04, task
20261004-101250, throwaway script /tmp/day36/research/crane_stop.py and
the orchestrator's rerun with the repo's g in
/tmp/day36/carrystop-closed.py, log /tmp/day36/carrystop-closed.log;
pillar 2 chaos and physics, everyday mechanics): "Carry and stop: a
weight hanging on a string from a hand (or a crane hook) that moves at a
steady speed and then stops dead; stop after half a swing and the weight
swings on at twice the carrying swing; stop after exactly one full swing
and it hangs still. The crane operator's trick, the waiter's tray, the
shopping bag."

Orchestrator notes (2026-10-04, g = 9.807). The model: a point weight
(bob) hangs on a light inextensible string of length L = g / pi^2 =
0.993657 m (99.4 cm, chosen so the small-swing period is exactly 2 pi
sqrt(L / g) = 2.0000 s; say "a string that swings once in two seconds")
from a pivot (the hand) that moves along a level line at V = 0.5 m/s
from t = 0 and stops dead at t = tau (top panel tau = 1.0 s, half a
swing; bottom panel tau = 2.0 s, one full swing). The start and the stop
are instant (the hand jumps from rest to V and from V to rest; a hand
with a 0.1 s or 0.3 s ramp is a description-only variant, and the sim
must print it). At the start the bob keeps its absolute velocity (zero),
so in the hand's frame it moves backwards at V: relative angular speed
theta' = -V / L with theta = 0. Between the jumps the hand moves at a
steady speed, so the hand's frame is inertial and the bob is a plain
pendulum: L theta'' = -g sin(theta), integrate with RK4 at dt = 1e-4 s
with compensated summation, energy (1/2) L^2 theta'^2 + g L (1 - cos
theta) constant to 1e-12 per unit mass between the jumps. At the stop
the bob keeps its absolute velocity again: its tangential speed becomes
L theta' + V cos(theta) (the string's impulse kills the radial part V
sin(theta); print that killed radial speed, it must be tiny at both
stops, under 0.001 m/s) so theta' jumps by +V cos(theta) / L. After the
stop the bob swings about the fixed hand; its swing amplitude is
acos(1 - E / (g L)) with E the energy per unit mass after the stop. The
string's tension per unit mass is g cos(theta) + L theta'^2 (print its
minimum; it must stay positive). Linear theory, for the description and
as a check: the swing during the move is V / (omega L) = 9.18 degrees
with omega = pi rad/s, and the residual swing after the stop is 2 (V /
(omega L)) |sin(pi tau / T)|: twice the carrying swing at tau = T / 2,
zero at tau = T. The nonlinear period at 9.19 degrees is 2.0032 s, so
the stop at 2.0000 s leaves 0.093 degrees (0.2 cm of sideways motion at
the bob): say "hangs still" and give the 0.093 in the card and the
description; the exact zero is at 2.0032 s (print it). Shown at 1/2
speed.

Checks, not facts (the sim must print and compare; state them as
checks): L = 0.993657 m, T = 2.0000 s; the swing during the move 9.187
degrees (energy form acos(1 - V^2 / (2 g L)); linear 9.177); stop at
1.0 s: the hand has moved 0.500 m, the bob is at -0.046 degrees at the
stop, the residual swing is 18.434 degrees (linear 18.354), the least
tension 0.949 g, the bob's sideways reach 31.4 cm; stop at 2.0 s: the
hand has moved 1.000 m, the bob is at 0.093 degrees at the stop, the
residual swing 0.093 degrees (linear 0.000), the least tension 0.987 g,
the sideways reach 0.2 cm; the ratio of the two residuals about 198;
the exact zero of the residual at tau = 2.0032 s (0.001 degrees);
half-step rerun (dt 5e-5) agrees within 1e-6 degrees. For the
description: stop at 0.5 s or 1.5 s: 12.9 to 13.0 degrees; at V = 1.0
m/s: 18.43 during, 37.37 after a stop at 1.0 s, 0.75 after a stop at
2.0 s (its exact zero at 2.0130 s); with a 0.1 s ramp on the start and
the stop: 18.35 and 0.091 degrees; with 0.3 s ramps: 17.73 and 0.080; a
10 m crane cable (T = 6.345 s) at 1.0 m/s: stop at 3.17 s leaves 11.6
degrees, stop at 6.345 s leaves 0.02; a 1.00 m string (T 2.0064 s) at
0.5 m/s: 18.37 and 0.27 degrees at stops of 1.0 and 2.0 s. Print the
angle, angular speed, tension and the bob's position tables at 0.1 s
intervals for both panels (real time, 0 to 5 s), the schedule in video
time, the text widths and the layout clearances.

Drawing: two stacked bands (y 330 to 880 and 880 to 1430), side view,
sims/deskchain layout (label row 40 px coloured, two readout rows 28 px
in a left and a right column ending 134 px under the band top, the gold
event row 156 to 196 px under the band top), top band "stop after 1 s"
(teal, the "yes it swings" case), bottom band "stop after 2 s" (coral,
the "no" case), 300 px per metre: a thin rail line at 215 px under the
band top from x 330 to x 660 with ticks and small labels "0", "0.5 m",
"1 m" (24 px, muted) at x 330, 480, 630; the hand a small lighter block
(28 x 16 px) riding on the rail, its centre starting at x 330; the
string a thin light line from the hand to the bob; the bob a lighter
disc 28 px across (radius 14), the string 298 px long (0.9937 m x 300),
so the bob hangs 298 px under the hand: at rest its centre is 513 px
under the band top and its bottom 527 px (under the 550 px band
bottom); a dashed muted plumb line straight down from the hand so the
angle reads; a thin dashed trail of the bob's centre over the last 1 s
of video; after the stop a short gold arc at the hand marking the swing
amplitude with its label ("18.4 deg" / "0.1 deg", 24 px) beside it. At
18.4 degrees the bob is 94 px sideways and 15 px higher, from x 386 to
574 in the top band (the hand stopped at x 480); in the bottom band the
hand stops at x 630 and the bob hangs under it. Assert the clearances
(the bob stays inside its band and clear of the rows, the trail and
arc labels under 950 px and inside the frame). Readouts (28 px): left
column "hand: 0.50 m/s, 0.50 m" live then "hand: stopped at 1.0 s" (or
2.0 s), right column "angle 9.2 deg" live (the signed angle from the
plumb line) and the shared clock "N.NNN s after the start" (and "held,
at rest" before it) at y 290; legend row at y 236: "same string, same
speed, 1/2 speed". Event rows (gold, lit at the stop plus one full
swing so the result is settled, held until the fade): "stopped at 1 s:
swings 18.4 degrees" and "stopped at 2 s: hangs still, 0.1 degrees".
Schedule (video time, 1/2 speed; cycle 10 s = 600 frames, 4 cycles in
40 s, exactly periodic, the last frame equal to the first): the hand
starts 0.5 s into the cycle (1.0 s of video from the first frame of the
cycle, 0.5 s real... use: the start at 1.0 s of the cycle = real t 0,
both hands move, the top hand stops at 1.0 + 2.0 = 3.0 s of the cycle,
the bottom hand at 1.0 + 4.0 = 5.0 s; the top bob swings on through 5.0
to 9.4 s (2.2 real swings); the reset crossfade runs over the last 0.6 s
of each cycle (the hands and bobs blend back to the start position, the
readouts out over its first half and in over its second). On the first
frame the hands are at x 330 and the bobs hang still under them (held).
Title (56 px, two rows at y 190 and 252): "Carry a weight, then stop.|
Does it swing?" (measure both rows). Overlay: "99 cm string, 2.0 s
swing | 0.5 m/s | 1/2 speed | no seed" (measure; shorten to "2.0 s
swing | 0.5 m/s | 1/2 speed | no seed" if over 950 px). Payoff card
(payoff_t set so it rises as the payoff number is spoken, 6 lines, each
under 950 px): "carry a weight, then stop: does it swing?" | "stop at
1 s: 18.4 deg, stop at 2 s: 0.1 deg" | "the string swings once in 2.0
s (99 cm)" | "half a swing: the stop throws it on" | "a whole swing: it
arrives back at rest" | "at 1 m/s: 37.4 deg against 0.75 deg". Music
seed 112.

Day thirty-six, third slot (the research run's best candidate; Moon
clock was the fallback). Chosen because it is a "stop at the right
moment" trick everyone has felt with a shopping bag or a mug on a tray,
the two panels end visibly differently (one bob swinging 31 cm each way,
the other hanging dead still under a stopped hand), the setup is one
number (a string that swings once in two seconds; the speed is spoken
once) and the payoff is one number (eighteen degrees against still),
with an exact linear closed form and a natural loop. Question in the
first two seconds: "Carry a weight on a string, then stop. Does it
swing?" (keep it identical in the title, the hook and the payoff; a
question-first variant "Does it swing? Carry a weight on a string and
stop dead." is allowed, pre-test both; the title can drop "on a
string"). Setup: "the string swings once in two seconds" and "walk at
half a meter a second" (one setup number, the speed spoken as words);
"on top, stop after one second; below, after two". Mechanism beat
(follow the picture): at the start the weight hangs back; it swings
forward and, half a swing later, it is moving ahead of the hand; stop
then and the stop throws it into a bigger swing; a full swing later it
is moving back toward the hand at the hand's own speed; stop then and
it arrives at rest. Payoff: "So, carry a weight on a string, then stop.
Does it swing? Stop after one second: yes, eighteen degrees. Stop after
two seconds: no, it hangs still." Whisper risks: "swing" and "swings"
(sentence-initial "Swing" is a known miss; pre-test "Does it swing?"),
"eighteen degrees" ("Not at eighteen" was heard as "9"; pre-test
"eighteen degrees" in a short sentence), "hangs still", "dead" (avoid
"stop dead" if misheard), "half a meter a second", "ahead of the hand",
"throws", avoid "do you", avoid "pull" as a noun, avoid "jerk". Keep
the narration 100 to 110 words, numbers as words, American spelling.
Pre-test hooks with scripts/voiceover.sh and keep the one whose
question lands earliest under two seconds. Measure every fixed text
line with PIL before rendering and keep every line under 950 px, and
the title under 100 characters with no < or >. Templates: sims/deskchain
(two bands, layout asserts, the clock, the crossfade, the loop checks),
sims/pegswing or sims/tarzan (a string and a bob on a pivot, the arc
mark), sims/wallbounce (a state word per phase, event rows). Sim name
carrystop: sims/carrystop/carrystop.py, projects/carrystop/,
media/carrystop/. The niche bullet "Carry and stop" will be appended to
docs/niche.md under "Added by trend research 2026-10-04" by the research
agent in parallel; re-read docs/niche.md right before you append your
[produced ...] note to that bullet, and if the bullet is not there yet
when you finish, report that instead of adding it.

## Claim (expected; the sim's numbers replace these)

A weight on a 99.4 cm string (one swing every 2.000 s) is carried at
0.5 m/s by a hand that starts and stops instantly. Stopped after 1.0 s
(half a swing, 0.5 m) the weight swings on at 18.4 degrees, twice its
9.2 degree carrying swing, reaching 31 cm each way; stopped after 2.0 s
(one full swing, 1.0 m) it hangs still, 0.09 degrees (0.2 cm). Linear
theory: residual swing = 2 (V / (omega L)) |sin(pi tau / T)|. Narrated:
two seconds (the string's swing) and half a meter a second (setup); one
second, yes, eighteen degrees; two seconds, no, it hangs still
(payoff). Card: the question; stop at 1 s 18.4 deg, stop at 2 s 0.1
deg; the string swings once in 2.0 s (99 cm); half a swing: the stop
throws it on; a whole swing: it arrives back at rest; at 1 m/s: 37.4
against 0.75 deg. Description: the model statement, the equations, the
two runs, the killed radial speed, the ramped-hand and crane variants,
the checks.

## Claim

A weight on a 99.4 cm string (one swing every 2.0000 s) is carried at
0.5 m/s by a hand that starts and stops instantly. Stopped after 1.0 s
(half a swing, 0.500 m) the weight swings on at 18.434 degrees, 2.006
times its 9.187 degree carrying swing, reaching 31.4 cm each way;
stopped after 2.0 s (one full swing, 1.000 m) it hangs still, 0.093
degrees (0.16 cm). Linear theory: residual swing = 2 (V / (omega L))
|sin(pi tau / T)| = 18.354 and 0.000 degrees. Narrated: two seconds
(the string's swing) and half a meter a second (setup); one second,
yes, eighteen degrees; two seconds, no, it hangs still (payoff).

## Evidence

### Measurements

Full `media/carrystop/measure.log` (`nix develop -c python3
sims/carrystop/carrystop.py --measure-only`, exit 0):

```
Sun Oct  4 06:26:47 PM EEST 2026
setup: two panels on the same clock, the same string and the same speed, side view: a point weight (the bob) hangs on a light inextensible string of length L = g (T / 2 pi)^2 = 0.993657 m = 99.4 cm, chosen so the small-swing period is T = 2 pi sqrt(L / g) = 2.0000 s (a string that swings once in 2 seconds; g = 9.807 m/s^2), from a hand that moves along a level rail at V = 0.5 m/s from t = 0 and stops dead at t = tau: top panel tau = 1 s (half a swing), bottom panel tau = 2 s (one full swing); the start and the stop are instant (the bob keeps its absolute velocity at each jump: theta' = -V / L at the start, theta' + V cos(theta) / L at the stop, the string's impulse killing the radial part V sin(theta)); between the jumps the hand's frame is inertial and the bob is a plain pendulum L theta'' = -g sin(theta), integrated by RK4 at 10000 steps per second (dt = 1e-04 s) with compensated (Kahan) summation, the energy per unit mass (1/2) L^2 theta'^2 + g L (1 - cos theta) checked between the jumps, a half-step rerun as a check; after the stop the bob swings about the fixed hand with amplitude acos(1 - E / (g L)); the string's tension per unit mass is g cos(theta) + L theta'^2; shown at 1/2 speed on a 10 s cycle (600 frames) with the start 0.6 s into the cycle, 4 cycles in 40 s; drawn at 300 px per metre (the string 298 px, the bob 28 px across); deterministic, no seed
the move: in the hand's frame the bob starts at theta = 0 with theta' = -V / L = -0.5032 rad/s (-28.83 deg/s): it hangs back, swings forward through the plumb line half a swing later and is ahead of the hand for the second half; the swing during the move is acos(1 - V^2 / (2 g L)) = 9.187 degrees = 9.2 degrees (energy form; linear V / (omega L) = 9.177 degrees with omega = 3.1416 rad/s = pi to -4.4e-16); the RK4 peak during the move is 9.187 degrees (-9.6e-10 degrees from the energy form); the small-swing period is T = 2.0000 s and the nonlinear period at 9.187 degrees is 2.0032 s (AGM), measured on the RK4 table as the second zero crossing at 2.0032 s (the first at 1.0016 s; diff +1.6e-13 s); the bob is 15.9 cm behind the hand at the far point and 1.3 cm higher; tension between 0.9872 g and 1.0257 g during the move
stop at 1.0 s (top panel, 0.5 of a swing): the hand has moved V tau = 0.500 m; at the stop the bob is at -0.046 degrees from the plumb line moving at theta' = +0.5032 rad/s in the hand's frame (the bob's absolute speed along the rail +1.0000 m/s against the hand's 0.5); the string's impulse kills the radial speed V sin(theta) = -0.00040 m/s (|0.0004| < 0.001) and theta' becomes +1.0064 rad/s; the residual swing is acos(1 - E / (g L)) = 18.434 degrees = 18.4 degrees (the RK4 table peaks at 18.434 degrees after the stop; linear 2 (V / (omega L)) |sin(pi tau / T)| = 18.354 degrees), 2.006 times the carrying swing; the least tension over the run is 0.949 g (9.3038 m/s^2 per unit mass, positive: the string stays taut); the bob's sideways reach after the stop is L sin(amp) = 31.4 cm each way (94 px) and it rises 5.10 cm; energy drift 5.8e-16 J/kg during the move and 1.2e-15 J/kg after the stop (E 0.125000 then 0.499997 J/kg); half-step rerun (dt = 5e-05 s): residual 18.4335732 degrees (+0.0e+00), angle at the stop -0.046395 degrees (+2.2e-15); 50000 steps
stop at 2.0 s (bottom panel, 1 of a swing): the hand has moved V tau = 1.000 m; at the stop the bob is at +0.093 degrees from the plumb line moving at theta' = -0.5032 rad/s in the hand's frame (the bob's absolute speed along the rail +0.0000 m/s against the hand's 0.5); the string's impulse kills the radial speed V sin(theta) = +0.00081 m/s (|0.0008| < 0.001) and theta' becomes +0.0000 rad/s; the residual swing is acos(1 - E / (g L)) = 0.093 degrees = 0.1 degrees (the RK4 table peaks at 0.093 degrees after the stop; linear 2 (V / (omega L)) |sin(pi tau / T)| = 0.000 degrees), 0.010 times the carrying swing; the least tension over the run is 0.987 g (9.6812 m/s^2 per unit mass, positive: the string stays taut); the bob's sideways reach after the stop is L sin(amp) = 0.2 cm each way (0 px) and it rises 0.00 cm; energy drift 5.8e-16 J/kg during the move and 8.7e-16 J/kg after the stop (E 0.125000 then 0.000013 J/kg); half-step rerun (dt = 5e-05 s): residual 0.0927903 degrees (+0.0e+00), angle at the stop +0.092789 degrees (-4.3e-15); 50000 steps
the two stops against each other: 18.434 / 0.093 = 198.7 times the swing (about 200); the stop at 2 s leaves 0.093 degrees because the nonlinear period is 2.0032 s, not 2.0000 s: the exact zero of the residual is at tau = 2.0032 s (+2.1e-08 s from the AGM period) where the residual is 0.000 degrees (0.00000); the residual at tau = 2 s on the same table is 0.093 degrees (the full run gave 0.093); 0.09 degrees is 0.16 cm of sideways motion at the bob: hangs still
table, stop at 1 s (RK4 table, real time since the start; the angle from the plumb line, positive ahead of the hand; the bob's position along the rail from the start and down from the rail): 0.0 s: +0.00 deg, -28.8 deg/s, tension 1.026 g, hand 0.00 m, bob +0.000 m along and 0.994 m down; 0.1 s: -2.84 deg, -27.4 deg/s, tension 1.022 g, hand 0.05 m, bob +0.001 m along and 0.992 m down; 0.2 s: -5.39 deg, -23.3 deg/s, tension 1.012 g, hand 0.10 m, bob +0.007 m along and 0.989 m down; 0.3 s: -7.43 deg, -17.0 deg/s, tension 1.000 g, hand 0.15 m, bob +0.022 m along and 0.985 m down; 0.4 s: -8.73 deg, -9.0 deg/s, tension 0.991 g, hand 0.20 m, bob +0.049 m along and 0.982 m down; 0.5 s: -9.19 deg, -0.1 deg/s, tension 0.987 g, hand 0.25 m, bob +0.091 m along and 0.981 m down; 0.6 s: -8.75 deg, +8.8 deg/s, tension 0.991 g, hand 0.30 m, bob +0.149 m along and 0.982 m down; 0.7 s: -7.45 deg, +16.8 deg/s, tension 1.000 g, hand 0.35 m, bob +0.221 m along and 0.985 m down; 0.8 s: -5.43 deg, +23.2 deg/s, tension 1.012 g, hand 0.40 m, bob +0.306 m along and 0.989 m down; 0.9 s: -2.88 deg, +27.4 deg/s, tension 1.022 g, hand 0.45 m, bob +0.400 m along and 0.992 m down; 1.0 s: -0.05 deg, +57.7 deg/s, tension 1.026 g, hand 0.50 m, bob +0.499 m along and 0.994 m down (stopped); 1.1 s: +5.63 deg, +54.9 deg/s, tension 1.088 g, hand 0.50 m, bob +0.597 m along and 0.989 m down (stopped); 1.2 s: +10.75 deg, +46.8 deg/s, tension 1.050 g, hand 0.50 m, bob +0.685 m along and 0.976 m down (stopped); 1.3 s: +14.83 deg, +34.1 deg/s, tension 1.003 g, hand 0.50 m, bob +0.754 m along and 0.961 m down (stopped); 1.4 s: +17.47 deg, +18.3 deg/s, tension 0.964 g, hand 0.50 m, bob +0.798 m along and 0.948 m down (stopped); 1.5 s: +18.43 deg, +0.7 deg/s, tension 0.949 g, hand 0.50 m, bob +0.814 m along and 0.943 m down (stopped); 1.6 s: +17.62 deg, -16.9 deg/s, tension 0.962 g, hand 0.50 m, bob +0.801 m along and 0.947 m down (stopped); 1.7 s: +15.10 deg, -33.0 deg/s, tension 0.999 g, hand 0.50 m, bob +0.759 m along and 0.959 m down (stopped); 1.8 s: +11.13 deg, -45.9 deg/s, tension 1.046 g, hand 0.50 m, bob +0.692 m along and 0.975 m down (stopped); 1.9 s: +6.07 deg, -54.4 deg/s, tension 1.086 g, hand 0.50 m, bob +0.605 m along and 0.988 m down (stopped); 2.0 s: +0.42 deg, -57.6 deg/s, tension 1.103 g, hand 0.50 m, bob +0.507 m along and 0.994 m down (stopped); 2.1 s: -5.27 deg, -55.2 deg/s, tension 1.090 g, hand 0.50 m, bob +0.409 m along and 0.989 m down (stopped); 2.2 s: -10.45 deg, -47.4 deg/s, tension 1.053 g, hand 0.50 m, bob +0.320 m along and 0.977 m down (stopped); 2.3 s: -14.61 deg, -35.1 deg/s, tension 1.006 g, hand 0.50 m, bob +0.249 m along and 0.962 m down (stopped); 2.4 s: -17.35 deg, -19.4 deg/s, tension 0.966 g, hand 0.50 m, bob +0.204 m along and 0.948 m down (stopped); 2.5 s: -18.42 deg, -1.9 deg/s, tension 0.949 g, hand 0.50 m, bob +0.186 m along and 0.943 m down (stopped); 2.6 s: -17.72 deg, +15.8 deg/s, tension 0.960 g, hand 0.50 m, bob +0.198 m along and 0.946 m down (stopped); 2.7 s: -15.31 deg, +32.0 deg/s, tension 0.996 g, hand 0.50 m, bob +0.238 m along and 0.958 m down (stopped); 2.8 s: -11.42 deg, +45.2 deg/s, tension 1.043 g, hand 0.50 m, bob +0.303 m along and 0.974 m down (stopped); 2.9 s: -6.42 deg, +54.0 deg/s, tension 1.084 g, hand 0.50 m, bob +0.389 m along and 0.987 m down (stopped); 3.0 s: -0.80 deg, +57.6 deg/s, tension 1.102 g, hand 0.50 m, bob +0.486 m along and 0.994 m down (stopped); 3.1 s: +4.91 deg, +55.6 deg/s, tension 1.092 g, hand 0.50 m, bob +0.585 m along and 0.990 m down (stopped); 3.2 s: +10.13 deg, +48.1 deg/s, tension 1.056 g, hand 0.50 m, bob +0.675 m along and 0.978 m down (stopped); 3.3 s: +14.37 deg, +36.0 deg/s, tension 1.009 g, hand 0.50 m, bob +0.747 m along and 0.963 m down (stopped); 3.4 s: +17.22 deg, +20.5 deg/s, tension 0.968 g, hand 0.50 m, bob +0.794 m along and 0.949 m down (stopped); 3.5 s: +18.41 deg, +3.1 deg/s, tension 0.949 g, hand 0.50 m, bob +0.814 m along and 0.943 m down (stopped); 3.6 s: +17.82 deg, -14.7 deg/s, tension 0.959 g, hand 0.50 m, bob +0.804 m along and 0.946 m down (stopped); 3.7 s: +15.52 deg, -31.0 deg/s, tension 0.993 g, hand 0.50 m, bob +0.766 m along and 0.957 m down (stopped); 3.8 s: +11.72 deg, -44.4 deg/s, tension 1.040 g, hand 0.50 m, bob +0.702 m along and 0.973 m down (stopped); 3.9 s: +6.77 deg, -53.6 deg/s, tension 1.082 g, hand 0.50 m, bob +0.617 m along and 0.987 m down (stopped); 4.0 s: +1.17 deg, -57.5 deg/s, tension 1.102 g, hand 0.50 m, bob +0.520 m along and 0.993 m down (stopped); 4.1 s: -4.55 deg, -55.9 deg/s, tension 1.093 g, hand 0.50 m, bob +0.421 m along and 0.991 m down (stopped); 4.2 s: -9.82 deg, -48.7 deg/s, tension 1.059 g, hand 0.50 m, bob +0.331 m along and 0.979 m down (stopped); 4.3 s: -14.14 deg, -36.9 deg/s, tension 1.012 g, hand 0.50 m, bob +0.257 m along and 0.964 m down (stopped); 4.4 s: -17.08 deg, -21.6 deg/s, tension 0.970 g, hand 0.50 m, bob +0.208 m along and 0.950 m down (stopped); 4.5 s: -18.38 deg, -4.2 deg/s, tension 0.950 g, hand 0.50 m, bob +0.187 m along and 0.943 m down (stopped); 4.6 s: -17.91 deg, +13.5 deg/s, tension 0.957 g, hand 0.50 m, bob +0.194 m along and 0.945 m down (stopped); 4.7 s: -15.72 deg, +30.0 deg/s, tension 0.990 g, hand 0.50 m, bob +0.231 m along and 0.957 m down (stopped); 4.8 s: -12.00 deg, +43.7 deg/s, tension 1.037 g, hand 0.50 m, bob +0.293 m along and 0.972 m down (stopped); 4.9 s: -7.12 deg, +53.1 deg/s, tension 1.079 g, hand 0.50 m, bob +0.377 m along and 0.986 m down (stopped); 5.0 s: -1.55 deg, +57.5 deg/s, tension 1.102 g, hand 0.50 m, bob +0.473 m along and 0.993 m down (stopped)
table, stop at 2 s (RK4 table, real time since the start; the angle from the plumb line, positive ahead of the hand; the bob's position along the rail from the start and down from the rail): 0.0 s: +0.00 deg, -28.8 deg/s, tension 1.026 g, hand 0.00 m, bob +0.000 m along and 0.994 m down; 0.1 s: -2.84 deg, -27.4 deg/s, tension 1.022 g, hand 0.05 m, bob +0.001 m along and 0.992 m down; 0.2 s: -5.39 deg, -23.3 deg/s, tension 1.012 g, hand 0.10 m, bob +0.007 m along and 0.989 m down; 0.3 s: -7.43 deg, -17.0 deg/s, tension 1.000 g, hand 0.15 m, bob +0.022 m along and 0.985 m down; 0.4 s: -8.73 deg, -9.0 deg/s, tension 0.991 g, hand 0.20 m, bob +0.049 m along and 0.982 m down; 0.5 s: -9.19 deg, -0.1 deg/s, tension 0.987 g, hand 0.25 m, bob +0.091 m along and 0.981 m down; 0.6 s: -8.75 deg, +8.8 deg/s, tension 0.991 g, hand 0.30 m, bob +0.149 m along and 0.982 m down; 0.7 s: -7.45 deg, +16.8 deg/s, tension 1.000 g, hand 0.35 m, bob +0.221 m along and 0.985 m down; 0.8 s: -5.43 deg, +23.2 deg/s, tension 1.012 g, hand 0.40 m, bob +0.306 m along and 0.989 m down; 0.9 s: -2.88 deg, +27.4 deg/s, tension 1.022 g, hand 0.45 m, bob +0.400 m along and 0.992 m down; 1.0 s: -0.05 deg, +28.8 deg/s, tension 1.026 g, hand 0.50 m, bob +0.499 m along and 0.994 m down; 1.1 s: +2.79 deg, +27.5 deg/s, tension 1.022 g, hand 0.55 m, bob +0.598 m along and 0.992 m down; 1.2 s: +5.36 deg, +23.4 deg/s, tension 1.013 g, hand 0.60 m, bob +0.693 m along and 0.989 m down; 1.3 s: +7.40 deg, +17.1 deg/s, tension 1.001 g, hand 0.65 m, bob +0.778 m along and 0.985 m down; 1.4 s: +8.72 deg, +9.1 deg/s, tension 0.991 g, hand 0.70 m, bob +0.851 m along and 0.982 m down; 1.5 s: +9.19 deg, +0.2 deg/s, tension 0.987 g, hand 0.75 m, bob +0.909 m along and 0.981 m down; 1.6 s: +8.76 deg, -8.7 deg/s, tension 0.991 g, hand 0.80 m, bob +0.951 m along and 0.982 m down; 1.7 s: +7.48 deg, -16.7 deg/s, tension 1.000 g, hand 0.85 m, bob +0.979 m along and 0.985 m down; 1.8 s: +5.47 deg, -23.2 deg/s, tension 1.012 g, hand 0.90 m, bob +0.995 m along and 0.989 m down; 1.9 s: +2.92 deg, -27.3 deg/s, tension 1.022 g, hand 0.95 m, bob +1.001 m along and 0.992 m down; 2.0 s: +0.09 deg, +0.0 deg/s, tension 1.000 g, hand 1.00 m, bob +1.002 m along and 0.994 m down (stopped); 2.1 s: +0.09 deg, -0.1 deg/s, tension 1.000 g, hand 1.00 m, bob +1.002 m along and 0.994 m down (stopped); 2.2 s: +0.08 deg, -0.2 deg/s, tension 1.000 g, hand 1.00 m, bob +1.001 m along and 0.994 m down (stopped); 2.3 s: +0.05 deg, -0.2 deg/s, tension 1.000 g, hand 1.00 m, bob +1.001 m along and 0.994 m down (stopped); 2.4 s: +0.03 deg, -0.3 deg/s, tension 1.000 g, hand 1.00 m, bob +1.001 m along and 0.994 m down (stopped); 2.5 s: +0.00 deg, -0.3 deg/s, tension 1.000 g, hand 1.00 m, bob +1.000 m along and 0.994 m down (stopped); 2.6 s: -0.03 deg, -0.3 deg/s, tension 1.000 g, hand 1.00 m, bob +1.000 m along and 0.994 m down (stopped); 2.7 s: -0.05 deg, -0.2 deg/s, tension 1.000 g, hand 1.00 m, bob +0.999 m along and 0.994 m down (stopped); 2.8 s: -0.07 deg, -0.2 deg/s, tension 1.000 g, hand 1.00 m, bob +0.999 m along and 0.994 m down (stopped); 2.9 s: -0.09 deg, -0.1 deg/s, tension 1.000 g, hand 1.00 m, bob +0.998 m along and 0.994 m down (stopped); 3.0 s: -0.09 deg, -0.0 deg/s, tension 1.000 g, hand 1.00 m, bob +0.998 m along and 0.994 m down (stopped); 3.1 s: -0.09 deg, +0.1 deg/s, tension 1.000 g, hand 1.00 m, bob +0.998 m along and 0.994 m down (stopped); 3.2 s: -0.08 deg, +0.2 deg/s, tension 1.000 g, hand 1.00 m, bob +0.999 m along and 0.994 m down (stopped); 3.3 s: -0.05 deg, +0.2 deg/s, tension 1.000 g, hand 1.00 m, bob +0.999 m along and 0.994 m down (stopped); 3.4 s: -0.03 deg, +0.3 deg/s, tension 1.000 g, hand 1.00 m, bob +0.999 m along and 0.994 m down (stopped); 3.5 s: -0.00 deg, +0.3 deg/s, tension 1.000 g, hand 1.00 m, bob +1.000 m along and 0.994 m down (stopped); 3.6 s: +0.03 deg, +0.3 deg/s, tension 1.000 g, hand 1.00 m, bob +1.000 m along and 0.994 m down (stopped); 3.7 s: +0.05 deg, +0.2 deg/s, tension 1.000 g, hand 1.00 m, bob +1.001 m along and 0.994 m down (stopped); 3.8 s: +0.07 deg, +0.2 deg/s, tension 1.000 g, hand 1.00 m, bob +1.001 m along and 0.994 m down (stopped); 3.9 s: +0.09 deg, +0.1 deg/s, tension 1.000 g, hand 1.00 m, bob +1.002 m along and 0.994 m down (stopped); 4.0 s: +0.09 deg, +0.0 deg/s, tension 1.000 g, hand 1.00 m, bob +1.002 m along and 0.994 m down (stopped); 4.1 s: +0.09 deg, -0.1 deg/s, tension 1.000 g, hand 1.00 m, bob +1.002 m along and 0.994 m down (stopped); 4.2 s: +0.08 deg, -0.2 deg/s, tension 1.000 g, hand 1.00 m, bob +1.001 m along and 0.994 m down (stopped); 4.3 s: +0.05 deg, -0.2 deg/s, tension 1.000 g, hand 1.00 m, bob +1.001 m along and 0.994 m down (stopped); 4.4 s: +0.03 deg, -0.3 deg/s, tension 1.000 g, hand 1.00 m, bob +1.001 m along and 0.994 m down (stopped); 4.5 s: +0.00 deg, -0.3 deg/s, tension 1.000 g, hand 1.00 m, bob +1.000 m along and 0.994 m down (stopped); 4.6 s: -0.03 deg, -0.3 deg/s, tension 1.000 g, hand 1.00 m, bob +1.000 m along and 0.994 m down (stopped); 4.7 s: -0.05 deg, -0.2 deg/s, tension 1.000 g, hand 1.00 m, bob +0.999 m along and 0.994 m down (stopped); 4.8 s: -0.07 deg, -0.2 deg/s, tension 1.000 g, hand 1.00 m, bob +0.999 m along and 0.994 m down (stopped); 4.9 s: -0.09 deg, -0.1 deg/s, tension 1.000 g, hand 1.00 m, bob +0.998 m along and 0.994 m down (stopped); 5.0 s: -0.09 deg, -0.0 deg/s, tension 1.000 g, hand 1.00 m, bob +0.998 m along and 0.994 m down (stopped)
for the description: stop at 0.5 s (moved 0.250 m): residual 12.906 degrees = 12.9 degrees (linear 12.978), least tension 0.975 g, reach 22.2 cm; stop at 1.5 s (moved 0.750 m): residual 12.972 degrees = 13.0 degrees (linear 12.978), least tension 0.974 g, reach 22.3 cm; at V = 1 m/s on the same string: the swing during the move is 18.43 degrees (RK4 peak 18.43; nonlinear period 2.0130 s), a stop at 1 s leaves 37.36 degrees (linear 36.71; least tension 0.795 g; reach 60.3 cm) and a stop at 2 s leaves 0.75 degrees (1.3 cm; its exact zero is at 2.0130 s with 0.000 degrees left); a hand that ramps from rest to 0.5 m/s over 0.1 s and back to rest over 0.1 s (the ramps starting at 0 and at tau; no jumps): the stop at 1 s leaves 18.35 degrees and the stop at 2 s leaves 0.092 degrees (least tension 0.949 and 0.987 g); a hand that ramps from rest to 0.5 m/s over 0.3 s and back to rest over 0.3 s (the ramps starting at 0 and at tau; no jumps): the stop at 1 s leaves 17.73 degrees and the stop at 2 s leaves 0.080 degrees (least tension 0.953 and 0.988 g); a 10 m crane cable (T = 6.345 s) carried at 1 m/s: the load swings 5.79 degrees during the move; a stop after half a swing at 3.172 s leaves 11.59 degrees = 11.6 degrees (201 cm each way) and a stop after one swing at 6.345 s leaves 0.023 degrees = 0.02 degrees; a 1.00 m string (T = 2.0064 s) at 0.5 m/s: stops at 1 and 2 s leave 18.37 and 0.27 degrees; a stop at its own period 2.0064 s leaves 0.092 degrees
schedule (video time, 1/2 speed): cycles of 10 s start at -10.00, 0.00, 10.00, 20.00, 30.00 s (the first -0.00 s before the first frame); the hands start 0.6 s into each cycle at 0.60, 10.60, 20.60, 30.60 s (real t = 0); the top hand stops 2 s later at 2.60, 12.60, 22.60, 32.60 s (2.60 s into the cycle; the bob has swung back and forward once through the plumb line) and the bottom hand at 4.60, 14.60, 24.60, 34.60 s (4.60 s into the cycle; the bob has swung back, forward and back again); the top bob swings on from 2.60 to 9.40 s of the cycle (6.8 s of video, 3.4 s real, 1.7 swings); the top event row lights 1 swing after its stop at 6.60, 16.60, 26.60, 36.60 s and the bottom row 0.5 swing after its stop at 6.60, 16.60, 26.60, 36.60 s (6.60 s into the cycle); the gold arc and its label appear at each stop; the trail follows the bob over the last 1 s of video; the reset crossfade runs over the last 0.6 s of each cycle (from 9.40, 19.40, 29.40, 39.40 s; the hands and bobs blend back to the held start, the readouts out over its first half and in over its second); on the first frame the cycle is 0.00 s in (-0.300 s real: both hands at x 330 px, held, the bobs hanging still); title until 3 s; payoff card from 30.5 s; the title fades back in over the last 0.5 s and the last frame repeats the first (the scene is periodic: 40 s holds exactly 4 cycles)
text widths (the on-screen strings verbatim): overlay@34 801 px '2.0 s swing | 0.5 m/s | 1/2 speed | no seed', title line 1@56 828 px 'Carry a weight, then stop.', title line 2@56 458 px 'Does it swing?', legend@40 814 px 'same string, same speed, 1/2 speed', clock@28 350 px '3.000 s after the start', clock held@28 194 px 'held, at rest', label half@40 606 px 'stop after 1 s: half a swing', hand carry half@28 363 px 'hand: 0.50 m/s, 0.50 m', hand stopped half@28 356 px 'hand: stopped at 1.0 s', event half@40 817 px 'stopped at 1 s: swings 18.4 degrees', arc label half@24 118 px '18.4 deg', label full@40 649 px 'stop after 2 s: one full swing', hand carry full@28 363 px 'hand: 0.50 m/s, 1.00 m', hand stopped full@28 356 px 'hand: stopped at 2.0 s', event full@40 883 px 'stopped at 2 s: hangs still, 0.1 degrees', arc label full@24 102 px '0.1 deg', hand held@28 168 px 'hand: held', state weight at rest@28 222 px 'weight at rest', state weight hangs back@28 297 px 'weight hangs back', state weight swings ahead@28 333 px 'weight swings ahead', state weight swings on@28 275 px 'weight swings on', state weight hangs still@28 282 px 'weight hangs still', angle@28 247 px 'angle -18.4 deg', tension@28 246 px 'tension 1.000 g', rail label 0@24 17 px '0', rail label 0.5@24 76 px '0.5 m', rail label 1@24 50 px '1 m', payoff line 1@40 923 px 'carry a weight, then stop: does it swing?', payoff line 2@40 932 px 'stop at 1 s: 18.4 deg, stop at 2 s: 0.1 deg', payoff line 3@40 876 px 'the string swings once in 2.0 s (99 cm)', payoff line 4@40 777 px 'half a swing: the stop throws it on', payoff line 5@40 838 px 'a whole swing: it arrives back at rest', payoff line 6@40 801 px 'at 1 m/s: 37.4 deg against 0.75 deg'
row check: the left column ends at x 689 px, the right column starts at x 793 px; both end 134 px under the band top; the event row is centred 176 px under the band top (156 to 196; widest 883 px, x 98 to 982); the rail is 215 px under the band top from x 330 to 660 with ticks at x 330, 480, 630 and labels ending 12 px left of their ticks from x 301, 392, 568 at 239 px under the band top (a stopped string is at most 8 px from its tick at that depth); the hand block (28 x 16 px) rides the rail from x 330 to 480 (top) and 630 (bottom); the string is 298 px, the bob (28 px) rests with its centre 513 px under the band top and its bottom 527 px; over the drawn run the bob's centre spans x 330 to 630 px and y 498 to 513 px under the band top (top band x 330 to 574, bottom band x 330 to 630), so the bob's disc stays inside x 316 to 644 and y 484 to 527; the gold arc has radius 60 px about the stopped hand with its label from x 524 to 642 (top) and 674 to 776 (bottom) at 285 px under the band top, the string at most 23 px from the plumb line at that depth; each band is 550 px tall (y 330 to 880 and 880 to 1430); the caption band starts at y 1440; the title rows span y 162 to 280 and the overlay band ends at y 130; the card spans y 1552 to 1832
exit 0
Sun Oct  4 06:26:49 PM EEST 2026
```

Brief checks:

- Period 2.0000 s from L = 0.993657 m = 99.4 cm: matches the brief's
  99.4 cm and 2.000 s.
- Carrying swing 9.187 degrees (brief 9.19): matches.
- Stop at 1.0 s: 18.434 degrees (brief 18.43), 31.4 cm (brief 31 cm),
  linear 18.354 (brief 18.35): matches.
- Stop at 2.0 s: 0.093 degrees (brief 0.093), 0.2 cm (brief 0.2 cm):
  matches. Exact nonlinear period 2.0032 s leaves 0.000 degrees (brief
  0.001): the sim's golden-section zero is tighter than the brief's.
- Stops at 0.5 and 1.5 s: 12.906 and 12.972 (brief 12.9 and 13.0):
  matches.
- 0.1 s ramps: 18.35 and 0.092 (brief 18.35 and 0.091); 0.3 s ramps:
  17.73 and 0.080 (brief 17.73 and 0.080). The 0.092 against 0.091
  comes from the ramp model (linear ramps starting at 0 and at tau);
  description-only.
- At 1.0 m/s: 37.36 against 0.75 (brief 37.4 against 0.75): matches at
  the card's precision (37.4).
- Crane 10 m (6.345 s) at 1 m/s: 11.59 and 0.023 (brief 11.6 and 0.02):
  matches.
- Least tension 0.949 g (brief 0.949): matches; the string stays taut.
- Half-step rerun identical to +0.0e+00 degrees (brief 1e-6): matches.
- Energy drift at most 1.2e-15 J/kg (assert < 1e-12).
- The killed radial speed is below 0.001 m/s at both stops, so the
  instant stop loses no visible energy to the string.

### Production

- Sim: `sims/carrystop/carrystop.py`, manifest
  `projects/carrystop/manifest.json` (fps 60, 10000 steps/s, 1/2 speed,
  10 s cycle, start_at 0.6, payoff_t 30.5, voice_offset 1.4, music seed
  112). Deterministic, no seed.
- Smoke frames `media/carrystop/smoke-{0.0,1.1,1.5,2.5,3.2,4.0,5.2,7.2,
  9.6,31.9,39.7,39.983}.png` viewed; rail labels moved left of their
  ticks after the stopped string crossed "0.5 m"; the overlay cut to
  the brief's short form after the long form measured 1066 px.
- Footage `media/carrystop/render.log`: loop check 0 px, periodicity 0
  px, loop step 0 px, 40.00 s, every on-screen string under 950 px
  (widest 932 px, payoff line 2).
- Hook pretests `media/carrystop/hooks/pretest.log`: hook1-5 and the
  risky-word list all round-trip; hook2 ("Does it swing? Carry a weight
  on a string, then stop.") chosen: the question lands at 0 s of the
  voice.
- Narration `projects/carrystop/narration.txt`, 110 words, numbers as
  words. Voice `media/carrystop/voice.log`: pass 1 ok at 113 words
  (over the limit), pass 2 failed (sentence-initial "Half" heard as
  "Have"), pass 3 ok, 33.785 s. Timing `media/carrystop/timing.log`
  (offset 1.4 s): the setup numbers at 1.40-9.13 s, "Stop then" at
  15.94 and 23.07 s, "yes" by 31.09 s, "18 degrees" 31.09-33.63 s,
  "No, it hangs still" 33.63-35.19 s; voice ends at 35.19 s.
  Silences `media/carrystop/silences.log`: 9 pauses of 0.27-0.42 s.
- Compose `media/carrystop/compose.log`: music seed 112, 40.00 s;
  captions 22 pauses detected, 22 matched, max chunk start shift
  1.647 s; final.mp4 40.000000 s.
- Sync: the top hand stops at 2.60, 12.60, 22.60, 32.60 s and the
  bottom at 4.60, 14.60, 24.60, 34.60 s; "Stop then" (15.94 s) follows
  the cycle-2 top stop and "Stop then!" (23.07 s) sits between the
  cycle-3 top stop and the bottom stop at 24.60 s, which the voice then
  calls "arrives at rest" (24.19-26.32 s); the payoff "hangs still"
  (33.63-35.19 s) covers the cycle-4 bottom stop at 34.60 s.

### Local QA

- Frames from final.mp4 viewed at 0.00, 1.0, 2.1, 13.0, 24.7, 30.9,
  32.3, 34.9 and 39.983 s (`media/carrystop/qa-*.png`):
  - 0.00: title on, both hands held at 0, both weights at rest, angle
    +0.0, tension 1.000 g, no caption.
  - 1.0: both hands at 0.10 m, weights hang back -5.4 deg, title on.
  - 2.1: hands at 0.38 m, -6.5 deg, trails behind the bobs, caption
    "Does it swing?", title on.
  - 13.0: cycle 2, 1.200 s after the start: top stopped at 1.0 s,
    swings on +10.8 deg with the gold "18.4 deg" arc; bottom carrying
    at 0.60 m, +5.4 deg; caption "hangs back."
  - 24.7: cycle 3, 2.050 s: top swings on -2.5 deg; bottom stopped at
    2.0 s, "weight hangs still", +0.1 deg, tension 1.000 g, "0.1 deg"
    arc label; caption "Stop then, and it".
  - 30.9: cycle 4, 0.150 s: payoff card on (six gold lines, 18.4 deg
    against 0.1 deg, 2.0 s (99 cm), 37.4 against 0.75), caption
    "second: yes,".
  - 32.3: 0.850 s, both carrying at 0.42 m, -4.2 deg, caption "Stop
    after two", card on.
  - 34.9: 2.150 s, top swings on -8.0 deg, bottom hangs still +0.1
    deg, caption "hangs still.", card on.
  - 39.983: last frame equals the first (title, held, at rest).
  - No clipped text, no overlap between captions, card and bands.
- `media/carrystop/sheet.png` viewed: 40 cells, the four cycles
  identical, captions in narration order, the card from cell 32.
- Captions against narration by script: 34 caption chunks, 111 tokens
  against 110 words; the one difference is "hand's" split at the
  typographic apostrophe (U+2019) the caption filter uses; otherwise
  identical. Max chunk 20 characters, no overlapping windows.
- Band signalstats on footage.mp4 crops: rows 96-130 YMAX 28, rows
  1440-1530 YMAX 28 (background only).
- ffprobe final.mp4: h264 1080x1920 60/1 fps, 2400 frames, aac 22050
  Hz mono, duration 40.000000 s, 4407254 bytes, moov before mdat.
- md5sum final.mp4: 18f80794fe577283abd89395e1b883fc
- Narrated numbers against measure.log by script: "two seconds"
  (2.0000 s), "half a meter a second" (0.5 m/s), "eighteen degrees"
  (18.434), "hangs still" (0.093 degrees, 0.16 cm): all present.
- Description decimals against measure.log by script: 76 distinct
  decimals in the Measured bullets, none missing.

### Metadata

`projects/carrystop/metadata.json`: title 96 characters, ASCII, no
angle brackets; description 4601 characters, ASCII; 12 tags;
categoryId 27; privacyStatus private; containsSyntheticMedia true;
selfDeclaredMadeForKids false.

### Deviations from the brief

- Overlay uses the brief's short form (the long form measured 1066 px).
- start_at 0.6 s and voice_offset 1.4 s instead of 1.0 and 0.6 so that
  "hangs still" covers the cycle-4 bottom stop; payoff_t 30.5 s.
- The top bob swings 1.7 swings after its stop before the crossfade,
  not 2.2; the bottom event row lights half a swing after its stop so
  that both rows light at 6.6 s of the cycle.
- Description-only numbers that differ from the brief in the last
  digit: 37.36 (brief 37.37) at 1 m/s, 0.092 (brief 0.091) with 0.1 s
  ramps; the card shows 37.4 and the description quotes the sim.
- Narration trimmed from 113 to 110 words; "Half a swing on" reworded
  after whisper heard "Have".

## Niche note

[produced 2026-10-04 as "Carry a weight, then stop. Does it swing? Stop
at 1 s: 18.4 degrees; stop at 2 s: it hangs still"; measured 9.187
degree carrying swing, 18.434 degrees after the 1.0 s stop (31.4 cm,
2.006 times), 0.093 degrees after the 2.0 s stop (0.16 cm, hangs
still), ratio 198.7, exact zero at 2.0032 s; task 20261004-180827]

## Upload

- Orchestrator QA (2026-10-04 18:35 EEST): 8 frames (0.5, 3.4, 12.6,
  16.0, 22.0, 26.3, 33.5, 36.6 s) and sheet.png viewed, no clipping or
  overlap; 34 caption chunks match the narration token for token
  (111 tokens); bands rows 96-130 and 1440-1530 YMAX 28; ffprobe
  40.000000 s, 2400 frames, moov before mdat; md5
  18f80794fe577283abd89395e1b883fc; title 96 chars ASCII, description
  4601 chars, 12 tags, categoryId 27, private, synthetic true, kids
  false; 78 decimals all present in measure.log; docs/niche.md note
  present under the "Carry and stop" bullet.
- Attempt 4 of 5 (quota day 2026-10-04T10:00 EEST), recorded 2026-10-04T18:35:26+03:00
  before the call. Attempts before this: 1 atwood ok, 2 kerbhop failed
  before the API, 3 kerbhop ok.
- Outcome: uploaded as EEpe7RdbNAs (https://youtu.be/EEpe7RdbNAs) at
  2026-10-04T15:35:34Z, private. `scripts/yt-qa.py carrystop
  EEpe7RdbNAs --wait --publish`: gate 15 of 15 (channel Seed Zero,
  processed, succeeded, hd, embeddable, 1080x1920, title, description
  and tags match, categoryId 27, madeForKids false, PT41S, private
  before publish). Published 2026-10-04T18:36:17+03:00; re-read
  privacyStatus public. Quota: 1,600 units for the insert and 54 for
  the QA run; day total about 5,017 of 10,000 after 4 attempts.
- Record: media/carrystop/upload.log and media/carrystop/publish.log.
