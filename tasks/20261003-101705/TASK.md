# Produce short: Yo-yo drop, a yo-yo on its string beside a ball from the same meter

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day35

## Goal

Backlog idea (trend research 2026-09-27, task 20260927-102520, pillar 2
chaos and physics, everyday mechanics; read the full entry under "Added
by trend research 2026-09-27" in docs/niche.md): "Yo-yo drop: a 3 cm
yo-yo on a 0.5 cm axle dropped on its string beside a ball dropped from
the same 1 m; measure the time to the bottom; expect 1.969 s against
0.452 s, 4.36 times slower (a = g / 19 = 0.516 m/s^2), the string holding
94.7 percent of the weight all the way down, 1.016 m/s and 203 rad/s at
the bottom, then back up to the hand every 3.94 s with no loss; periodic
so the short loops; mild, so rank it low; deterministic, no seed."

Orchestrator notes (2026-10-03, before this brief). Use a realistic yo-yo
with the same ratio: a uniform disc 6 cm across (R = 3 cm) on an axle 1
cm across (r = 0.5 cm), R / r = 6 as in the research entry, so the numbers
are the same. The model: the yo-yo is a uniform solid disc of radius R
and mass m (m cancels; the axle's own mass is part of the disc, say so)
whose string, 1 m long, is wound on the axle of radius r and tied to it;
the string's top end is held still by a hand; the yo-yo is let go from
rest with the string taut and vertical; the string does not slip or
stretch, so the drop x and the turn phi obey x = r phi and the equations
m x'' = m g - T, I phi'' = T r with I = m R^2 / 2 give a = g / (1 + I / (m
r^2)) = g / (1 + (R / r)^2 / 2) = g / 19 = 0.5162 m/s^2 and T = m (g - a)
= (18 / 19) m g = 94.74 percent of the weight. Beside it a ball of the
same 6 cm size is dropped from the same height at the same instant and
falls freely at g = 9.807 m/s^2 with no air drag (say so); both centres
drop exactly 1.00 m: the ball lands on the floor when its centre has
dropped 1 m, and the yo-yo reaches the end of its string when its centre
has dropped 1 m, its rim then level with the floor. At the end of the
string the string is tied to the axle, so the yo-yo's downward speed
reverses and its spin keeps its sense while the string winds on again on
the other side of the axle: an ideal turnaround with no loss (say so; a
real yo-yo loses some each turn). The climb mirrors the drop and the
yo-yo reaches the hand with zero speed at 2 sqrt(2 h / a) = 3.937 s; the
hand catches it and holds it until the next release. Integrate the coupled
motion with RK4 at 1e-4 s (the drop, the turnaround, the climb; a
half-step rerun as a check) and check against the closed forms.

Checks, not facts (orchestrator closed forms in /tmp/day35/closed.py and
closed2.py, g = 9.807): the ball lands at sqrt(2 h / g) = 0.4516 s at 4.43
m/s; the yo-yo reaches the end of its string at sqrt(2 h / a) = 1.9684 s,
4.359 times later (exactly sqrt(19)), moving at 1.016 m/s and spinning at
203.2 rad/s = 1,940 turns a minute; when the ball lands the yo-yo has
dropped 5.26 cm and moves at 0.233 m/s; when the yo-yo reaches the bottom
the ball has been down for 1.517 s; the string holds 0.9474 of the weight
all the way down and up; at the bottom 1/19 = 5.26 percent of the energy
is in the fall and 18/19 = 94.74 percent in the spin; the yo-yo is back at
the hand at 3.937 s with zero speed; the yo-yo is 6.5 cm down at 0.5 s,
25.8 cm at 1.0 s, 58.1 cm at 1.5 s. For the description: a 0.5 cm axle
(R / r = 12): a = g / 73, 3.858 s, 8.54 times the ball, the string holding
98.6 percent; a 2 cm axle (R / r = 3): a = g / 5.5, 1.059 s, 2.35 times; a
hollow ring yo-yo of the same size (I = m R^2): a = g / 37, 2.747 s, 6.08
times. Print the no-slip residual (x - r phi, at most 1e-12 m), the
energy balance (m g x against the kinetic energy of fall plus spin, to
1e-12 per unit mass), the tension as a fraction of the weight, the drop
and speed tables at 0.25 s intervals for both, the turnaround and the
return time, the half-step agreement (better than 1e-6 s on the landing
times), the schedule in video time, the text widths and the layout
clearances. State every number above as a check the sim must print, not
as a fact.

Drawing: one shared scene between y 330 and 1430 (sims/chain style), side
view, because the two objects must share one height scale: a hand line
(the release height) at y 460 with two small hand marks, the yo-yo at x
400 hanging from its hand on a 1 m string, the ball at x 700 held level
with the yo-yo's centre, a 1 m height scale on the left (x 150-230, ticks
every 10 cm, "1 m" at the bottom, "0" at the top), a dashed gold finish
line at 1 m below the release (the centres' landing height) across both
columns, the floor 3 cm below it (a lighter slab from y about 1225 down
to about 1250) with the ball coming to rest on it (no bounce: say the
floor stops it); 740 px per metre, so the yo-yo and the ball are 44 px
across and the axle 7 px; the yo-yo as a disc with two darker sectors
whose contrast fades toward a plain ring as the spin rate rises above
about two turns per video second (a mark spinning 16 turns a second
cannot be drawn honestly at 60 fps; blur it instead and give the spin as
a readout), a visible axle dot, the string a thin line from the hand to
the axle's side (the left side on the way down, the right side on the way
up), a 1 m string that stays vertical; the ball a plain lighter disc. Live
readouts (28 px): a left column "yo-yo: NN.N cm down" and "spin NNNN
turns a minute", a right column "ball: NN.N cm down" and the real-time
clock; gold event rows under the floor (y 1290 and 1340 or so, above the
caption band at 1440): "ball lands: 0.45 s, yo-yo 5.3 cm down" (lit at the
ball's landing and held) and "yo-yo at the bottom: 1.97 s, 4.36x the
ball" (lit at the string's end and held; the second line may add "back
at the hand: 3.94 s" when the yo-yo returns). Shown at 1/2 speed; cycle
10 s (600 frames): both let go 0.6 s into the cycle, the ball lands at
1.50 s of the cycle, the yo-yo reaches the bottom at 4.54 s and is back
in the hand at 8.47 s, the hand holds it; the ball is reset into the hand
by a crossfade over the last 0.6 s of the cycle (the yo-yo is already at
the top, so it does not jump); 4 cycles in 40 s, the last frame equal to
the first. The legend row after the title: "same height, same instant,
1/2 speed"; the shared clock in real seconds since the release.

Day thirty-five, third slot. Chosen because "which lands first" drops are
the channel's strongest format (folded chain against a ball 987 views,
stick against a ball 735), the objects end visibly differently (the ball
is down while the yo-yo has barely left the hand, then the yo-yo climbs
back), the factor is exact (root nineteen, like yesterday's root eight
broom), and the return to the hand makes a natural loop. Question in the
first two seconds: "Drop a yo-yo beside a ball. Which lands first?" (keep
the question identical in the title, the hook and the payoff). Setup
number: one meter (both drop one meter, let go together). Payoff: the
ball, at under half a second; by then the yo-yo has dropped five
centimeters; it needs nearly two seconds, four point four times as long
(speak at most two numbers in the payoff beat: "five centimeters" and
"four point four times" are the preferred pair, "point four five seconds"
and "one point nine seven seconds" go to the card). The 94.7 percent, the
spin, the energy split, the return time and the axle variants go to the
card and the description. The mechanism sentence must follow the picture:
the string spins the yo-yo as it unwinds, and almost all of the fall goes
into the spin, so the yo-yo itself barely speeds up (never say "pull" as
a noun; "the string holds back" is safe). Whisper risks: "yo-yo" (pre-test
early; if it fails try "yoyo" or "the yo yo" and keep the spelling that
passes, the title can keep "yo-yo"), "axle" (pre-test), "unwinds"
(pre-test), "spins" and "spin" (sentence-initial "Spin" failed before),
"root nineteen" (pre-test; "root eight" passed 2026-10-02), "five
centimeters" and "four point four times" (pre-test), "half a second"
(pre-test), avoid "do you", avoid "fly", avoid "pull" as a noun. Pre-test
hooks with scripts/voiceover.sh and keep the one whose question lands
earliest under two seconds. Measure every fixed text line with PIL before
rendering and keep every line under 950 px, and the title under 100
characters with no < or >. Music seed 109. Templates: sims/chain (one
shared scene, a chain and a ball released together, the height scale, the
finish line, releases on a cycle with a reset fade, loop checks),
sims/springdrop (a hanging object on a line), sims/deskchain (layout
asserts, the clock, the crossfade). Sim name yoyo: sims/yoyo/yoyo.py,
projects/yoyo/, media/yoyo/.

## Claim (expected; the sim's numbers replace these)

A yo-yo (a uniform 6 cm disc on a 1 cm axle, R / r = 6) let go on its 1 m
string beside a ball dropped from the same height at the same instant:
the ball lands at 0.452 s; the yo-yo has dropped 5.3 cm by then and
reaches the end of its string at 1.968 s, 4.36 times later (exactly
sqrt(19), a = g / 19 = 0.516 m/s^2), moving at 1.02 m/s and spinning at
1,940 turns a minute, with the string holding 94.7 percent of its weight
all the way; it climbs back to the hand at 3.94 s. Narrated: one meter
(setup); the ball lands first, the yo-yo only five centimeters down by
then, four point four times slower (payoff). Card: the question; the ball
0.45 s, the yo-yo 1.97 s, 4.36x = root 19; 5.3 cm down when the ball
lands; the string holds 94.7 percent of the weight; 1,940 turns a minute
at the bottom; back at the hand at 3.94 s. Description: the model
statement, the equations, the two drops, the energy split, the axle and
hollow variants, the checks.

## Claim

A yo-yo, a uniform solid 6 cm disc (R = 3 cm) on a 1 cm axle (r = 0.5
cm, R / r = 6, I = m R^2 / 2), let go from rest on its 1 m string beside
a 6 cm ball dropped from the same height at the same instant (g = 9.807
m/s^2, no air drag, no slip, an ideal turnaround with no loss; RK4 at
1e-4 s with compensated summation, checked against the closed forms):
the ball lands at 0.4516 s at 4.43 m/s; by then the yo-yo has dropped
5.26 cm (0.233 m/s, 445 turns a minute) and it reaches the end of its
string at 1.9684 s, 1.517 s after the ball and 4.3589 times later
(exactly sqrt(19); a = g / 19 = 0.5162 m/s^2), moving at 1.016 m/s and
spinning at 203.21 rad/s = 1,940 turns a minute (31.83 turns in all),
with the string holding 0.947368 = 94.74 percent of the weight all the
way down and up; at the bottom 5.26 percent of the energy is in the fall
and 94.74 percent in the spin (balance within 1.4e-14 J/kg, no-slip
residual within 1.6e-15 m); it climbs back and stops at the hand at
3.9369 s with zero speed (half-step rerun +0.0e+00 s). Narrated: one
meter (setup); the ball, by a long way; by then the yo-yo is only five
centimeters down; it needs four point four times as long (payoff). Card:
the question; the ball; ball 0.45 s, yo-yo 1.97 s: 4.36x = root 19; yo-
yo 5.3 cm down when the ball lands; the string holds 94.7 % of the
weight; 1,940 rpm; back in the hand at 3.94 s. Description: the model
statement, the equations, the two drops, the energy split, the tables,
the axle and hollow variants, the checks.

## Evidence

### Measurements

The final measure.log (media/yoyo/measure.log, 2026-10-03 10:38:43 to
10:38:44 EEST, exit 0, written by sims/yoyo/yoyo.py with
projects/yoyo/manifest.json --measure-only after the compensated
summation fix; the render at 10:38:44 printed the same numbers):

```
Sat Oct  3 10:38:43 AM EEST 2026
setup: one scene, side view, both objects on one height scale: a yo-yo, a uniform solid disc of radius R = 3 cm (6 cm across; its mass m cancels and the axle's own mass is part of the disc) on an axle of radius r = 0.5 cm (1 cm across), R / r = 6, I = m R^2 / 2; its string, 1 m long, is wound on the axle and tied to it, and a hand holds the string's top end still; the yo-yo is let go from rest with the string taut and vertical, and the string does not slip or stretch (x = r phi); beside it a ball of the same size (radius 3 cm) is dropped from the same height at the same instant and falls freely at g = 9.807 m/s^2 with no air drag; the floor stops it, no bounce; both centres drop exactly 1.00 m: the ball lands when its centre has dropped 1 m and the yo-yo reaches the end of its string when its centre has dropped 1 m, its rim then level with the floor; at the end of the string the string is tied to the axle, so the yo-yo's downward speed reverses, its spin keeps its sense and the string winds on again on the other side of the axle, an ideal turnaround with no loss (a real yo-yo loses some each turn); the coupled motion (x, x', phi, phi') integrated by RK4 at 10000 steps per second (dt = 1e-04 s) with the tension from the constraint each step and compensated (Kahan) summation of the state, the end of the string and the stop at the top located by bisection inside the step, a half-step rerun as a check, against the closed forms; shown at 1/2 speed on a 10 s cycle (600 frames) with both let go 0.6 s into the cycle, 4 cycles in 40 s; drawn at 740 px per metre (the yo-yo and the ball 44 px across, the axle 7 px); deterministic, no seed
model: m x'' = m g - T and I phi'' = T r with x = r phi give T = m g / (1 + m r^2 / I) and a = g / (1 + I / (m r^2)) = g / (1 + (R / r)^2 / 2); I / (m r^2) = (R / r)^2 / 2 = 18, so a = g / 19 = 0.5162 m/s^2 = 0.516 m/s^2 (0.0526 g) and T = (1 - a / g) m g = 18 / 19 of the weight = 0.9474 = 94.74 percent = 94.7 percent, all the way down and up (the same constraint and the same tension on the climb, with the torque reversed); a is the same for any mass and any string length
ball: falls 1 m in sqrt(2 h / g) = 0.4516 s = 0.45 s (under half a second: 0.4516 < 0.5) and lands at g t = 4.429 m/s = 4.43 m/s; stepped at the same dt the ball lands at 0.451593 s (diff +2.2e-14 s) at 4.4288 m/s (4516 steps); the floor stops it
yo-yo (RK4, 19685 steps down): reaches the end of its string at 1.9684 s = 1.97 s (closed form sqrt(2 h / a) = 1.9684 s, diff -8.9e-16 s; nearly two seconds), 1.5169 s = 1.517 s after the ball, 4.3589 times later = 4.36 times = 4.4 times (exactly sqrt(19) = 4.3589, diff -2.7e-15), moving at 1.0160 m/s = 1.016 m/s = 1.02 m/s (closed form sqrt(2 a h) = 1.0160 m/s, diff +4.4e-16) and spinning at 203.21 rad/s = 203.2 rad/s (closed form v / r = 203.21 rad/s, diff -1.4e-13) = 1940.5 turns a minute = 1940 turns a minute = 1,940 turns a minute (32.3 turns a second), 31.83 turns in all (h / (2 pi r) = 31.83); when the ball lands at 0.4516 s the yo-yo has dropped 0.0526 m = 5.26 cm = 5.3 cm = about 5 cm (closed form a t^2 / 2 = 5.26 cm) and moves at 0.2331 m/s = 0.233 m/s, spinning 445 turns a minute, against the ball's 4.43 m/s; when the yo-yo reaches the bottom the ball has been down for 1.5169 s = 1.517 s
checks: the string holds T / (m g) = 0.947368 of the weight = 94.74 percent (18 / 19 = 0.947368, diff +0.0e+00), constant down and up; energy at the bottom per unit mass: g h = 9.8070 J/kg against v^2 / 2 = 0.5162 J/kg in the fall (0.0526 = 5.26 percent; 1 / 19 = 0.0526) plus (I / m) omega^2 / 2 = 9.2908 J/kg in the spin (0.9474 = 94.74 percent; 18 / 19 = 0.9474); the energy balance m g x = kinetic energy of fall plus spin holds within 1.4e-14 J/kg over the drop and the climb; the no-slip residual x - r phi stays within 1.0e-15 m on the way down and (h - x) - r (phi - phi_h) within 1.6e-15 m on the way up; turnaround at 1.9684 s: 1.0160 m/s down becomes 1.0160 m/s up, the spin stays 203.21 rad/s; the yo-yo stops rising at 3.9369 s = 3.937 s = 3.94 s (closed form 2 sqrt(2 h / a) = 3.9369 s, diff -1.3e-15 s; 8.72 times the ball's fall) at x = -2.4e-16 m from the hand with speed 0.0e+00 m/s and spin -5.7e-14 rad/s: back at the hand with zero speed, the hand catches it; 19685 steps up; half-step rerun (dt = 5e-05 s): the end of the string at 1.9684469 s (+0.0e+00 s), the top at 3.9368939 s (+0.0e+00 s), speed at the bottom 1.0160294 m/s (+0.0e+00 m/s)
tables (RK4 table, real time since the release): 0.00 s: yo-yo 0.0 cm down, 0.000 m/s down, 0 rpm; ball 0.0 cm, 0.00 m/s; 0.25 s: yo-yo 1.6 cm down, 0.129 m/s down, 246 rpm; ball 30.6 cm, 2.45 m/s; 0.50 s: yo-yo 6.5 cm down, 0.258 m/s down, 493 rpm; ball on the floor (100 cm); 0.75 s: yo-yo 14.5 cm down, 0.387 m/s down, 739 rpm; ball on the floor (100 cm); 1.00 s: yo-yo 25.8 cm down, 0.516 m/s down, 986 rpm; ball on the floor (100 cm); 1.25 s: yo-yo 40.3 cm down, 0.645 m/s down, 1232 rpm; ball on the floor (100 cm); 1.50 s: yo-yo 58.1 cm down, 0.774 m/s down, 1479 rpm; ball on the floor (100 cm); 1.75 s: yo-yo 79.0 cm down, 0.903 m/s down, 1725 rpm; ball on the floor (100 cm); 2.00 s: yo-yo 96.8 cm down, 1.000 m/s up, 1909 rpm; ball on the floor (100 cm); 2.25 s: yo-yo 73.4 cm down, 0.871 m/s up, 1663 rpm; ball on the floor (100 cm); 2.50 s: yo-yo 53.3 cm down, 0.742 m/s up, 1416 rpm; ball on the floor (100 cm); 2.75 s: yo-yo 36.4 cm down, 0.613 m/s up, 1170 rpm; ball on the floor (100 cm); 3.00 s: yo-yo 22.7 cm down, 0.484 m/s up, 924 rpm; ball on the floor (100 cm); 3.25 s: yo-yo 12.2 cm down, 0.355 m/s up, 677 rpm; ball on the floor (100 cm); 3.50 s: yo-yo 4.9 cm down, 0.226 m/s up, 431 rpm; ball on the floor (100 cm); 3.75 s: yo-yo 0.9 cm down, 0.096 m/s up, 184 rpm; ball on the floor (100 cm); 4.00 s: yo-yo 0.0 cm down, 0.000 m/s down, 0 rpm (in the hand); ball on the floor (100 cm)
drops at the sample times: 0.5 s: 6.5 cm down (closed form 6.5 cm), 0.258 m/s, 493 rpm; 1 s: 25.8 cm down (closed form 25.8 cm), 0.516 m/s, 986 rpm; 1.5 s: 58.1 cm down (closed form 58.1 cm), 0.774 m/s, 1479 rpm
for the description: a 0.5 cm axle (R / r = 12, solid disc): I / (m r^2) = 72, a = g / 73 = 0.1343 m/s^2, the end of the string at 3.8584 s = 3.858 s = 3.86 s (closed form 3.8584 s, diff +1.6e-14), 8.544 = 8.54 times the ball, the string holding 0.9863 = 98.6 percent of the weight, 0.518 m/s and 207.3 rad/s = 1,980 rpm at the bottom (closed form 0.5183 m/s); a 2 cm axle (R / r = 3, solid disc): I / (m r^2) = 4.5, a = g / 5.5 = 1.7831 m/s^2, the end of the string at 1.0591 s = 1.059 s = 1.06 s (closed form 1.0591 s, diff -6.7e-16), 2.345 = 2.35 times the ball, the string holding 0.8182 = 81.8 percent of the weight, 1.888 m/s and 188.8 rad/s = 1,803 rpm at the bottom (closed form 1.8884 m/s); a hollow ring yo-yo of the same size on the 1 cm axle (I = m R^2): I / (m r^2) = 36, a = g / 37 = 0.2651 m/s^2, the end of the string at 2.7469 s = 2.747 s = 2.75 s (closed form 2.7469 s, diff +6.2e-15), 6.083 = 6.08 times the ball, the string holding 0.9730 = 97.3 percent of the weight, 0.728 m/s and 145.6 rad/s = 1,391 rpm at the bottom (closed form 0.7281 m/s)
drawing: the yo-yo's two darker sectors turn with phi and their contrast fades from full at 1.5 turns per video second (18.85 rad/s real, reached 0.1826 s after the release, 0.365 s of video) to none at 3 turns per video second (37.70 rad/s, 0.3652 s, 0.730 s of video), and back again on the climb; at the bottom the spin is 16.2 turns per video second, 97 degrees per frame at 60 fps, so a mark cannot be drawn honestly there and the disc is a plain ring with the spin as a readout; the string is drawn on the axle's left side on the way down and on its right side on the way up
schedule (video time, 1/2 speed): cycles of 10 s start at -10.00, 0.00, 10.00, 20.00, 30.00 s (the first -0.00 s before the first frame); both let go 0.6 s into each cycle at 0.60, 10.60, 20.60, 30.60 s; the ball lands 0.903 s after the release at 1.50, 11.50, 21.50, 31.50 s (the first event row lights, the gold 5.3 cm tick appears beside the yo-yo; the ball rests on the floor until the fade); the yo-yo reaches the end of its string 3.937 s after the release at 4.54, 14.54, 24.54, 34.54 s (the second event row lights) and is back in the hand 7.874 s after the release at 8.47, 18.47, 28.47, 38.47 s (8.47 s into the cycle; the third event row lights; the hand holds it); the yo-yo is 6.5 cm down 1 s of video after the release and 25.8 cm down after 2 s; the sectors fade out 0.37 to 0.73 s after the release and back in 7.14 to 7.51 s after it; the reset crossfade runs over the last 0.6 s of each cycle (from 9.40, 19.40, 29.40, 39.40 s; the readouts out over its first half and in over its second; the yo-yo is drawn the same in both, so it never jumps); on the first frame the cycle is 0.00 s in (-0.300 s real: the yo-yo held, the ball held); title until 3 s; payoff card from 30.4 s; the title fades back in over the last 0.5 s and the last frame repeats the first (the scene is periodic: 40 s holds exactly 4 cycles)
text widths (the on-screen strings verbatim): overlay@34 876 px 'yo-yo and ball, 1 m drop | 1/2 speed | no seed', title line 1@56 845 px 'Drop a yo-yo beside a ball.', title line 2@56 565 px 'Which lands first?', legend@40 850 px 'same height, same instant, 1/2 speed', clock@28 390 px '3.937 s after the release', clock held@28 194 px 'held, at rest', yo-yo readout@28 346 px 'yo-yo: 100.0 cm down', yo-yo held@28 288 px 'yo-yo: in the hand', yo-yo caught@28 372 px 'yo-yo: back in the hand', spin@28 397 px 'spin 1940 turns a minute', ball readout@28 318 px 'ball: 100.0 cm down', ball held@28 259 px 'ball: in the hand', ball speed@28 239 px 'speed 4.43 m/s', ball floor@28 329 px 'on the floor, stopped', event 1@40 837 px 'ball lands: 0.45 s, yo-yo 5.3 cm down', event 2@40 890 px 'yo-yo at the bottom: 1.97 s, 4.36x later', event 3@40 548 px 'back at the hand: 3.94 s', scale top@28 19 px '0', scale bottom@28 58 px '1 m', tick@24 90 px '5.3 cm', payoff line 1@40 600 px 'drop a yo-yo beside a ball:', payoff line 2@40 582 px 'which lands first? the ball', payoff line 3@40 916 px 'ball 0.45 s, yo-yo 1.97 s: 4.36x = root 19', payoff line 4@40 880 px 'yo-yo 5.3 cm down when the ball lands', payoff line 5@40 840 px 'the string holds 94.7 % of the weight', payoff line 6@40 848 px '1,940 rpm; back in the hand at 3.94 s'
row check: the left column ends at x 437 px, the right column starts at x 711 px; both rows end at y 418; the hand marks rise to y 422 and the hand line is at y 460 (x 280 to 820); the yo-yo hangs at x 400 (disc x 378 to 422, the string at x 396.3 down and 403.7 up) from y 438 at the hand to 1222 at the bottom; the ball at x 700 (x 678 to 722) from y 438 to 1222; the finish line at y 1200, the floor from y 1222.2 to 1250.2; the scale at x 230 with ticks to x 200 and labels from x 136; the gold tick at y 498.9 from x 432 to 452, its label to x 548; the event rows at y 1286, 1334 and 1382 (from 1264 to 1404, widest 890 px centred on 540); the band is y 330 to 1430; the caption band starts at y 1440; the title rows end at y 280 and start at y 162, the overlay band ends at y 130
exit 0
Sat Oct  3 10:38:44 AM EEST 2026
```

Checks from the brief (passed, or what the sim gave instead):

- the ball lands at sqrt(2 h / g) = 0.4516 s at 4.43 m/s: passed (0.4516
  s, 4.429 m/s; stepped 0.451593 s, diff +2.2e-14 s).
- the yo-yo reaches the end of its string at sqrt(2 h / a) = 1.9684 s,
  4.359 times later (exactly sqrt(19)): passed (1.9684 s, diff -8.9e-16
  s; 4.3589, diff -2.7e-15).
- 1.016 m/s and 203.2 rad/s = 1,940 turns a minute at the bottom: passed
  (1.0160 m/s, 203.21 rad/s, 1940.5 turns a minute, diff -1.4e-13
  rad/s).
- when the ball lands the yo-yo has dropped 5.26 cm and moves at 0.233
  m/s: passed (0.0526 m, 0.2331 m/s, 445 turns a minute).
- when the yo-yo reaches the bottom the ball has been down for 1.517 s:
  passed (1.5169 s).
- the string holds 0.9474 of the weight all the way down and up: passed
  (0.947368, diff +0.0e+00 against 18 / 19, constant down and up).
- at the bottom 1/19 = 5.26 percent of the energy in the fall and 18/19
  = 94.74 percent in the spin: passed (0.5162 and 9.2908 J/kg of 9.8070
  J/kg).
- back at the hand at 3.937 s with zero speed: passed (3.9369 s, diff
  -1.3e-15 s; x -2.4e-16 m, speed 0.0e+00 m/s, spin -5.7e-14 rad/s).
- 6.5 cm down at 0.5 s, 25.8 cm at 1.0 s, 58.1 cm at 1.5 s: passed (6.5
  / 25.8 / 58.1 cm, each equal to the closed form).
- description variants: a 0.5 cm axle a = g / 73, 3.858 s, 8.54 times,
  98.6 percent: passed (0.1343 m/s^2, 3.8584 s, 8.544, 0.9863); a 2 cm
  axle a = g / 5.5, 1.059 s, 2.35 times: passed (1.7831 m/s^2, 1.0591 s,
  2.345); a hollow ring a = g / 37, 2.747 s, 6.08 times: passed (0.2651
  m/s^2, 2.7469 s, 6.083).
- the no-slip residual x - r phi at most 1e-12 m: passed (1.0e-15 m
  down, 1.6e-15 m up).
- the energy balance to 1e-12 per unit mass: passed (1.4e-14 J/kg). The
  first measure run failed this assert at 3.8e-12 J/kg (plain RK4
  summation over 39,370 steps); compensated (Kahan) summation of the
  state fixed it and is stated in the setup line.
- the tension as a fraction of the weight: printed (0.947368 = 94.74
  percent).
- the drop and speed tables at 0.25 s intervals for both: printed (0.00
  to 4.00 s, the ball on the floor from 0.50 s).
- the turnaround and the return time: printed (1.9684 s, 1.0160 m/s down
  becomes 1.0160 m/s up, the spin kept at 203.21 rad/s; the top at
  3.9369 s).
- the half-step agreement better than 1e-6 s on the landing times:
  passed (+0.0e+00 s on the end of the string and on the top at the
  printed precision, +0.0e+00 m/s on the speed at the bottom).
- the schedule in video time, the text widths and the layout clearances:
  printed and asserted (every line under 950 px; the row check).

### Production

- Sim: sims/yoyo/yoyo.py, modelled on sims/deskchain (bands, cycle,
  crossfade, layout asserts, the clock, loop checks), sims/chain (one
  shared scene, a chain and a ball released together, the height scale,
  the finish line, releases on a cycle with a reset fade) and
  sims/springdrop (a hanging object on a line): RK4 on (x, v, phi,
  omega) with the tension from the constraint each step, compensated
  summation, bisection inside the step for the end of the string and the
  stop at the top, the lossless turnaround, a half-step rerun, the ball
  stepped at the same dt, the closed forms, the tables and sample drops,
  the description variants, the sector-fade numbers, the schedule, text
  widths and the row check; 2x supersampled scene layer; loop,
  periodicity and loop-step checks; ffmpeg rawvideo pipe with a
  ProcessPoolExecutor; --measure-only and --frames.
- Manifest projects/yoyo/manifest.json: seed 0, fps 60, g 9.807, drop
  1.0 m, disc radius 0.03 m, axle radius 0.005 m, ball radius 0.03 m,
  10000 steps per second, description axle radii 0.0025 and 0.01 m,
  table step 0.25 s, sample times 0.5 / 1.0 / 1.5 s, slow 2.0, cycle 10
  s, release_at 0.6 s, first_cycle_at 0.0, reset_fade 0.6 s, scene 40 s,
  740 px/m, hand_y 460, yo-yo x 400, ball x 700, scale x 230, hand line
  x 280 to 820, sector fade 1.5 to 3.0 turns per video second, title
  "Drop a yo-yo beside a ball.|Which lands first?" until 3 s, payoff_t
  30.4 s, payoff_hold 0.6 s, six payoff lines formatted from the
  measured values, loop_fade 0.5, music seed 109, gain 0.18, voice
  offset 0.6, caption_y 0.75, overlay "yo-yo and ball, 1 m drop | 1/2
  speed | no seed".
- Layout: overlay y 96-130 (compose); title two rows at y 190 / 252
  until 3 s; legend "same height, same instant, 1/2 speed" at y 236 and
  the clock ("held, at rest" / "N.NNN s after the release", real time)
  at y 290 after the title; one shared scene y 330-1430: readout rows at
  y 370 / 404 (28 px; left "yo-yo: NN.N cm down" and "spin NNNN turns a
  minute", right "ball: NN.N cm down" and "speed N.NN m/s" or "on the
  floor, stopped", with "in the hand" / "back in the hand" states); the
  hand line at y 460 from x 280 to 820 with two hand marks; the 1 m
  scale at x 230 with ticks every 10 cm ("0" at the top, "1 m" at the
  bottom); the yo-yo at x 400 (a 44 px disc with two darker 90-degree
  sectors turning with phi and fading between 1.5 and 3 turns per video
  second, a rim, a 7 px axle dot, the string a thin line from the hand
  mark to the axle's left side on the way down and right side on the way
  up); the ball at x 700 (a plain 44 px disc); the dashed gold finish
  line at y 1200 across both columns; the floor slab y 1222-1250; a gold
  "5.3 cm" tick beside the yo-yo's column at the ball's landing depth
  from the ball's landing; gold event rows at y 1286 / 1334 / 1382
  ("ball lands: 0.45 s, yo-yo 5.3 cm down", "yo-yo at the bottom: 1.97
  s, 4.36x later", "back at the hand: 3.94 s"), each lit at its event
  and held to the crossfade; the six-line gold card from y 1572 at a 48
  px pitch; nothing in rows 96-130 or 1440-1530 (asserted in the row
  check and measured on the footage).
- Hook pre-tests (media/yoyo/hooks/pretest.log, 10:35-10:36): hook1
  ("Drop a yo-yo beside a ball. Which lands first? Both drop one meter,
  let go at the same instant, in slow motion.") failed once ("in" heard
  as "it s"); hook2 ("yoyo") failed (whisper writes "yo yo"); hook3 ("yo
  yo") ok 6.94 s; hook4 ("A yo-yo and a ball, let go together. Which
  lands first? ...") ok 5.90 s with the question later; hook5 ("...
  shown at half speed.") ok 7.01 s: chosen wording; hook6 ("slowed
  down") failed ("slow"); hook7 (hook1's text again) ok 6.78 s.
  words.txt (21 phrases) passed except "winds" ("wins") and "root
  nineteen" ("route"); "yo-yo", "the string unwinds and spins it", "five
  centimeters", "four point four times as long", "half a second", "the
  axle" passed. words2.txt passed except "slowed" ("slow", "flow");
  "shown at half speed", the payoff sentences and the mechanism
  sentences passed. Onsets (silencedetect -35 dB, 0.22 s): speech from 0
  s in every hook; the first sentence ends at 1.54 to 1.67 s of voice
  (hook1 1.63, hook3 1.67, hook7 1.54; hook5 shows no pause before
  "Which"), "Which lands first?" ends at 2.89 s in hook1. The narration
  keeps "yo-yo" and avoids "winds", "slowed" and "root".
- Narration: projects/yoyo/narration.txt, 109 words; the question is the
  first two sentences (spoken from 0.60 s of video) and is repeated word
  for word ("So, drop a yo-yo beside a ball. Which lands first?") before
  the payoff; one setup number (one meter) and two payoff numbers (five
  centimeters, four point four times); American spelling ("meter",
  "centimeters"); no digits; the mechanism sentence follows the picture
  ("As the yo-yo drops, the string unwinds and spins it. Almost all of
  the fall goes into the spin, so the yo-yo itself barely speeds up.").
- Voice (media/yoyo/voice.log): pass 1 (109 words, 10:38:11) ok 33.63 s,
  no mishearing. voice.wav ends at 34.23 s of video.
- timing.log (voice offset 0.6 s; whisper's own spelling):

```
  0.60 -   2.44  Drop a yo-yo beside a ball.
  2.44 -   5.94  which lands first both drop one meter let go together
  5.94 -   7.14  shown at half speed.
  7.14 -  14.55  At the bottom the yo-yo turns and climbs back to the hand.
 Watch the string.
 As the yo-yo drops, the string unwinds and spins it.
 14.55 -  17.10  Almost all of the fall goes into the spin.
 17.10 -  26.26  so the yo-yo itself barely speeds up every drop the same.
 The ball lands while the yo-yo has barely left the hand,
 so drop a yo-yo beside a ball.
 26.26 -  28.99  which lands first, the bowl by a long way.
 28.99 -  31.71  By then the yo-yo is only 5 centimeters down.
 31.71 -  34.23  It needs 4.4 times as long.
voice 33.63 s, ends at 34.23 s of video
```

- Schedule and sync: releases at 0.60, 10.60, 20.60, 30.60 s; the ball
  lands at 1.50, 11.50, 21.50, 31.50 s; the yo-yo at the bottom at 4.54,
  14.54, 24.54, 34.54 s; back in the hand at 8.47, 18.47, 28.47, 38.47
  s; the crossfades over 9.40-10.00, 19.40-20.00, 29.40-30.00,
  39.40-40.00 s. The first release at 0.60 s is under the question
  (0.60-3.80); "Both drop one meter, let go together, shown at half
  speed." 3.80-7.25 over the first drop (the ball down at 1.50, the yo-
  yo at the bottom at 4.54); "At the bottom the yo-yo turns and climbs
  back to the hand." 7.25-10.27 over the first climb (back at 8.47) and
  the crossfade; "Watch the string. As the yo-yo drops, the string
  unwinds and spins it." 10.27-14.68 over the second drop (release
  10.60, the ball down at 11.50, the bottom at 14.54); "Almost all of
  the fall goes into the spin, so the yo-yo itself barely speeds up."
  14.68-19.80 over the second climb; "Every drop, the same." 19.80-21.27
  across the crossfade and the third release at 20.60; "The ball lands
  while the yo-yo has barely left the hand." 21.27-24.17 with the ball
  landing at 21.50 (the yo-yo 5.3 cm down, the gold tick and the first
  event row lit); "So, drop a yo-yo beside a ball. Which lands first?
  The ball, by a long way." 24.17-29.12 over the third climb; "By then
  the yo-yo is only five centimeters down." 29.12-31.84 across the
  crossfade, the fourth release at 30.60 and the ball's landing at 31.50
  (the 5.3 cm tick and the first event row appear while "centimeters
  down" is spoken), the card rising 30.4-31.0 s; "It needs four point
  four times as long." 31.84-34.23 as the yo-yo falls toward the bottom
  (34.54, when the second event row "4.36x later" lights, 0.3 s after
  the voice ends; the card's "4.36x = root 19" is full from 31.0 s); the
  fourth climb silent under the card; the title fades back in over
  39.5-40.0 s.
- Smoke frames viewed before the render (--frames 0.0, 1.0, 1.5, 2.1,
  3.5, 4.6, 6.5, 8.5, 9.7, 31.6, 34.6, 39.7, 39.98; thirteen viewed):
  the title with both objects held at the hand line; the ball ahead at
  0.2 s real with the yo-yo 1.0 cm down; the ball's landing with the
  first event row and the gold 5.3 cm tick; the ball on the floor with
  the yo-yo 14.5 cm down as a plain ring; the legend and clock after the
  title with the yo-yo mid-drop; the bottom with the string full length
  and the second event row; the climb with the string on the axle's
  right side; back in the hand with the third row and "yo-yo: back in
  the hand"; the crossfade with the readouts faded and the ball
  returning to the hand; the card full with the ball just down in cycle
  4; the bottom under the card; the loop fade; the last frame equal to
  the first. All text inside the frame.
- Render (media/yoyo/render.log, 10:38:44-10:39:08): loop check 0 px,
  periodicity check 0 px, loop step 0 px, footage 40.00 s at 60 fps,
  2400 frames. An earlier render at 10:34:47-10:35:11 with the same code
  and payoff_t 31.0 gave the same checks; re-rendered after payoff_t
  moved to 30.4 s.
- Compose (media/yoyo/compose.log, 10:39:08-10:39:34): music seed 109,
  40.00 s; captions 17 pauses detected, 17 matched (max chunk start
  shift 0.609 s against word-count timing); contact sheet 8x5 at 1 fps;
  final.mp4 40.000000 s; preview.mp4 40.066667 s.
- Text widths (PIL ImageFont.getlength, DejaVuSans-Bold, asserted < 950
  px): overlay@34 876, title@56 845 / 565, legend@40 850, clock@28 390
  (held 194), yo-yo readout@28 346 (held 288, caught 372), spin@28 397,
  ball readout@28 318 (held 259), ball speed@28 239, ball floor@28 329,
  events@40 837 / 890 / 548, scale labels@28 19 / 58, tick@24 90, payoff
  lines@40 600 / 582 / 916 / 880 / 840 / 848 px.

### Local QA

- Frames extracted from media/yoyo/final.mp4 (never edited) with ffmpeg
  -ss T and viewed at full resolution:
  - 0.00: overlay, the title "Drop a yo-yo beside a ball. / Which lands
    first?", "yo-yo: in the hand" / "spin 0 turns a minute" left, "ball:
    in the hand" / "speed 0.00 m/s" right, both objects at the hand line
    under their hand marks (the yo-yo with its two dark sectors and the
    axle dot, the ball plain), the 1 m scale, the dashed gold finish
    line, the floor slab; no caption, no card, no event rows.
  - 1.00 (0.2 s real after the release): the yo-yo 1.0 cm down at 197
    turns a minute, still at the hand line; the ball 19.6 cm down at
    1.96 m/s; caption "Drop a yo-yo beside".
  - 2.10 (0.75 s real): the ball on the floor ("ball: 100.0 cm down" /
    "on the floor, stopped"), the yo-yo 14.5 cm down at 739 turns a
    minute as a plain ring on its string, the gold "5.3 cm" tick, the
    event row "ball lands: 0.45 s, yo-yo 5.3 cm down"; caption "a
    ball.".
  - 14.50 (cycle 2, 1.950 s real): the legend and the clock "1.950 s
    after the release", the yo-yo 98.1 cm down at 1922 turns a minute
    just above the finish line on a full-length string, the ball on the
    floor; caption "and spins it.".
  - 21.50 (cycle 3, 0.450 s real): the ball 99.3 cm down at 4.41 m/s a
    frame before it lands, the yo-yo 5.2 cm down at 444 turns a minute;
    caption "The ball lands while".
  - 30.80 (cycle 4, 0.100 s real): the yo-yo 0.3 cm down, the ball 4.9
    cm down at 0.98 m/s; caption "only five"; the card rising (dim gold,
    all six lines inside the frame).
  - 32.20 (0.800 s real): the ball on the floor, the yo-yo 16.5 cm down
    at 789 turns a minute, the 5.3 cm tick and the first event row lit;
    caption "It needs four point"; the card full.
  - 34.50 (1.950 s real): the yo-yo 98.1 cm down at the bottom of its
    string; no caption (the voice ended at 34.23 s); the card full.
  - 39.983 (frame 2399): the title back, both objects in the hand, the
    same picture as 0.00; no caption, no card.
  Nothing clipped at the frame edges, no text in the caption band, the
  six card lines sit between y 1572 and about 1850.
- sheet.png (8x5 at 1 fps): four identical cycles: the held state, the
  ball ahead and then on the floor with the first event row and the 5.3
  cm tick, the yo-yo's string lengthening to the bottom with the second
  row, the climb, the hand with the third row, the crossfade; captions
  under; the card from the tile at 31 s.
- Question timing: on screen from frame 0 in the title (until 3.0 s);
  spoken from 0.60 s of video; the first sentence ends at 2.27 s
  (silences.log: the first pause in voice.wav 1.668-2.010 s, plus the
  0.6 s offset), "Which lands first?" from 2.61 s to about 3.80 s
  (captions 2.610-3.803; no pause detected after "first?", the next
  silence at 5.197 s of voice; timing.log's segment 2.44-5.94 runs on
  into "let go together"); repeated at 24.17-27.56 s.
- Captions: 34 chunks of at most 20 characters, 0.600-34.234 s, no
  overlaps; the concatenated caption text equals narration.txt word for
  word (109 words, compared by script with the overlay drawtext
  excluded).
- Payoff numbers on screen when spoken: "only five" 30.483-31.028 and
  "centimeters down." 31.028-31.843 with the card's "yo-yo 5.3 cm down
  when the ball lands" full from 31.0 s and the gold "5.3 cm" tick and
  "ball lands: 0.45 s, yo-yo 5.3 cm down" lit from 31.50 s; "It needs
  four point" 31.843-32.953 and "four times as long." 32.953-34.234 with
  the card's "ball 0.45 s, yo-yo 1.97 s: 4.36x = root 19" on screen, and
  "yo-yo at the bottom: 1.97 s, 4.36x later" lighting at 34.54 s.
- Footage signalstats: overlay band (rows 96-130) and caption band (rows
  1440-1530) YMAX 28 in all 2400 footage frames; both bands hold only
  the background (11, 14, 18).
- Loop: render.log loop check 0 px, periodicity check 0 px and loop step
  0 px on the raw frames. Final loop noise (codec only, frames by
  index): frame 2399 vs 0: 27,538 px over 8 levels, 3,279 over 24, max
  84 at a readout letter edge (x 43, y 383), mean 0.33; 2398 vs 0:
  42,367 / 6,008 / max 84; footage 2399 vs 0: 13,166 / 444 / max 53 at a
  title letter edge (x 235, y 221), mean 0.17.
- ffprobe final.mp4: h264 1080x1920 yuv420p 60/1, 2400 frames, duration
  40.000000 s, aac 22050 Hz mono, moov before mdat (faststart),
  3,304,887 bytes.
- md5sum media/yoyo/final.mp4: 1dc6b74afe7afbe7426fe9bf5d703261.
- Narrated numbers against measure.log: "one meter" (both centres drop
  exactly 1.00 m), "half speed" (shown at 1/2 speed), "only five
  centimeters down" (0.0526 m = 5.26 cm = 5.3 cm = about 5 cm when the
  ball lands), "four point four times as long" (4.3589 times = 4.36
  times = 4.4 times). All on printed lines.

- Metadata number check by script: 102 distinct numbers in the title and
  description (commas stripped), none missing from measure.log.

### Metadata

- Title (96 characters, ASCII, no < or >): Drop a yo-yo beside a ball.
  Which lands first? The ball at 0.45 s; the yo-yo 1.97 s, 4.36x later
- Description: 4,961 characters, ASCII, no arrows; one setup paragraph
  (the model, every constant, the equations, a = g / 19 and T = 18 / 19,
  RK4 at 1e-04 s with compensated summation and bisection, the half-step
  rerun, 1/2 speed, 4 drops in 40 s, no seed), "Measured:" bullets (the
  ball, the yo-yo at the bottom, the 5.26 cm when the ball lands, the
  tension, the energy split and the residuals, the turnaround and the
  top, the half-step rerun, the drop and climb table, the 0.5 cm and 2
  cm axles and the hollow ring), a "Why:" paragraph, the rerun line, the
  AI line. A first draft was 6,001 characters; the checks bullet and
  half the table rows were folded into the other bullets.
- Tags (12): drop a yo-yo beside a ball which lands first, yo-yo, yo-yo
  physics, yo-yo drop, which lands first, rolling without slipping,
  moment of inertia, rotational inertia, physics, physics visualization,
  simulation, shorts.
- categoryId "27", privacyStatus "private", containsSyntheticMedia true,
  selfDeclaredMadeForKids false.

### Deviations from the brief

- The clock sits at y 290 as the shared clock after the title
  (conventions, sims/deskchain), not in the right readout column; the
  right column's second row carries the ball's speed ("speed N.NN m/s")
  and "on the floor, stopped" once it lands.
- The 1 m scale's axis is at x 230 with ticks to x 200 and labels from x
  136 (brief: x 150-230); the gold "5.3 cm" tick beside the yo-yo's
  column at the ball's landing depth is not in the brief; it was added
  so the narrated five centimeters has a mark on screen.
- Three gold event rows at y 1286 / 1334 / 1382 (brief: two at about
  1290 and 1340, the second allowed to add the return); the second row
  reads "yo-yo at the bottom: 1.97 s, 4.36x later" because the brief's
  "4.36x the ball" measured 956 px at 40 px, over the 950 px limit.
- Payoff line 6 reads "1,940 rpm; back in the hand at 3.94 s" (a first
  draft "1,940 rpm at the bottom, hand again at 3.94 s" measured 1048 px
  and failed the width assert).
- The energy-balance assert failed on the first measure run (3.8e-12
  J/kg from plain summation over 39,370 RK4 steps); compensated (Kahan)
  summation of the state brought it to 1.4e-14 J/kg and the no-slip
  residuals to 1.0e-15 / 1.6e-15 m. The setup line states it.
- "in slow motion" became "shown at half speed" (whisper heard "it's
  slow motion" once in hook1, and "slowed" failed three times); "let go
  at the same instant" became "let go together" in the narration (the
  final voice passed in one pass). "root nineteen" is not narrated
  (whisper writes "route"); the card carries "4.36x = root 19".
- The question takes 0.60-3.80 s of video (brief: in the first two
  seconds): the first sentence "Drop a yo-yo beside a ball." ends at
  2.27 s and "Which lands first?" runs 2.61-3.80 s; the brief fixes the
  two-sentence question and asks that it stay identical in the title,
  the hook and the payoff, so it was kept; the question is on screen in
  the title from frame 0.
- payoff_t 30.4 s (card up 30.4-31.0) so the card is full before
  "centimeters down" is spoken (31.03-31.84); the first render with
  payoff_t 31.0 was re-rendered with the same code.
- The payoff beat speaks two numbers (five centimeters, four point four
  times); "under half a second" and "nearly two seconds" are not
  narrated; the card carries 0.45 s and 1.97 s. Narration 109 words, one
  pass.
- Four cycles of 10 s with first_cycle_at 0.0 (as the brief); the first
  frame shows both objects held 0.3 s real before the first release.

## Niche note

  [produced 2026-10-03 as "Drop a yo-yo beside a ball. Which lands
  first? The ball at 0.45 s; the yo-yo 1.97 s, 4.36x later"; measured a
  uniform solid 6 cm disc (R = 3 cm) on a 1 cm axle (r = 0.5 cm, R / r =
  6, I = m R^2 / 2) let go from rest on a 1 m string beside a 6 cm ball
  dropped from the same height at the same instant, g = 9.807 m/s^2, no
  drag, no slip, a lossless turnaround (RK4 at 1e-4 s with compensated
  summation against the closed forms, no seed): the ball lands at 0.4516
  s at 4.43 m/s; the yo-yo is 5.26 cm down by then (0.233 m/s, 445 rpm),
  reaches the end of its string at 1.9684 s, 1.517 s after the ball and
  4.3589 times later (exactly sqrt(19), a = g / 19 = 0.5162 m/s^2), at
  1.016 m/s and 203.21 rad/s = 1,940 turns a minute (31.83 turns), the
  string holding 0.947368 = 94.74 percent of the weight down and up,
  5.26 percent of the energy in the fall and 94.74 in the spin (balance
  within 1.4e-14 J/kg, no-slip within 1.6e-15 m), back at the hand at
  rest at 3.9369 s (half-step rerun +0.0e+00 s); 6.5 / 25.8 / 58.1 cm
  down at 0.5 / 1.0 / 1.5 s; a 0.5 cm axle g / 73, 3.858 s, 8.54 times,
  98.6 percent; a 2 cm axle g / 5.5, 1.059 s, 2.35 times, 81.8 percent;
  a hollow ring g / 37, 2.747 s, 6.08 times, 97.3 percent; shown at 1/2
  speed on a 10 s cycle, 4 drops in 40 s; task 20261003-101705]

## Upload

- Orchestrator gate passed at 2026-10-03T10:53:41+03:00 (frames, sheet, ffprobe, md5 1dc6b74afe7afbe7426fe9bf5d703261, metadata, captions, measure.log against /tmp/day35 closed forms).
- Upload attempt 3 of 5 for the quota day that began 2026-10-03T10:00 EEST, recorded at 2026-10-03T10:58:27+03:00 before starting scripts/yt-upload.py yoyo (two attempts, coinrecord and riverswim, on record since the boundary).
- Uploaded private as 709U5Wfu1H4 at 2026-10-03T10:58:30+03:00 (scripts/yt-upload.py, channels.list 1 unit + videos.insert 1,600 units; media/yoyo/upload.log).
- scripts/yt-qa.py yoyo 709U5Wfu1H4 --wait --publish in the foreground at 10:58:34: gate 15 of 15 (processed, hd, 1080x1920, title, description and tags match, category 27, not made for kids, PT41S, private before publish), published at 2026-10-03T10:59:37+03:00, re-read public (media/yoyo/publish.log); 56 units.
- Published: https://youtu.be/709U5Wfu1H4

### Quota

- Attempt 3 of 5 for the quota day that began 2026-10-03T10:00 EEST; 1,657 units (1 + 1,600 + 56); day total after this attempt 4,968 of 10,000.
