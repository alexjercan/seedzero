# Produce short: Inertia ball, pull the bottom string slowly beside a jerk, which string snaps

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day34

## Goal

Backlog idea (trend research 2026-09-27, task 20260927-102520, pillar 2
chaos and physics, everyday mechanics; read the full entry under "Added
by trend research 2026-09-27" in docs/niche.md): "Inertia ball: a 1 kg
ball hung by a string with a second string below, both snapping at 20 N
with 1 cm of stretch (k 2,000 N/m), the lower end pulled at 5 cm/s beside
jerked at 2 m/s; measure which string snaps and when; expect the slow
pull to snap the top string at 0.22 s after the ball sinks 5.1 mm (bottom
at 11.5 N) and the jerk to snap the bottom in 5 ms with the ball moved
0.085 mm (top 9.98 N); x'' + (2 k / m) x = (k V / m) t, tensions k x + m g
and k (V t - x); the 0.41 m/s threshold depends on the stiffness and
break chosen, so narrate the two outcomes; repeat; deterministic, no
seed."

Orchestrator notes (2026-10-02, before this brief). The model: a ball of
mass m = 1 kg hangs from a fixed hook on a string of stiffness k = 2000
N/m; an identical string hangs from the ball's underside down to a hand.
Each string is a massless linear spring that carries tension only (slack
when shorter than its free length) and snaps the instant its tension
reaches F = 20 N (1 cm of stretch), about twice the ball's weight; say
these are chosen numbers for a thin cord. A small damping on the ball,
c = 1 N s/m (chosen; it moves the snap times by 2 ms and 0 ms, print
the no-damping rerun); g = 9.80665. At rest the top string carries m g =
9.807 N, stretched 4.903 mm; the bottom string is just taut at zero
tension. x is the ball's downward displacement from that rest; the hand
moves down at a steady V from t = 0: top tension f1 = m g + k x, bottom
tension f2 = k (V t - x) (zero if negative), so m x'' = f2 - (f1 - m g)
- c x' = k V t - 2 k x - c x'. Top panel, slow pull V = 0.05 m/s: the
ball follows the hand at about half its speed (quasi-static x = V t /
2), both tensions rise together, but the top one starts 9.8 N ahead
because it carries the ball, so it reaches 20 N first. Bottom panel, jerk
V = 2 m/s: the bottom string stretches 1 cm in 5 ms while the ball's
inertia keeps it where it is (it moves k V t^3 / (6 m) = 0.083 mm), so
the bottom string reaches 20 N first and the top string never gets past
10 N. After the top snaps (slow pull): the ball falls, pulled by gravity
and by the bottom string until that goes slack as the ball outruns the
hand, then free fall; it drops out of the band. After the bottom snaps
(jerk): the ball stays on the top string with an invisible 0.085 mm
wobble (period 2 pi sqrt(m / k) = 140 ms, damped); the hand carries on
down with the broken piece and leaves the band.

Checks, not facts (orchestrator RK4 at 1 us, /tmp/day34/closed.log):
V 0.05 m/s: the top string snaps at 217.03 ms with the ball 5.097 mm
down and the bottom string at 11.51 N (quasi-static estimate 2 (F - m g)
/ (k V) = 203.9 ms; the gap is the ball's lag behind x = V t / 2; no
damping 219.05 ms). V 2 m/s: the bottom string snaps at 5.043 ms with
the ball 0.0850 mm down and the top string at 9.977 N (closed form F /
(k V) = 5.000 ms with the ball still; the ball's move k V t^3 / (6 m) =
0.0833 mm). The top string snaps when x = (F - m g) / k = 5.0967 mm; the
bottom when V t - x = F / k = 10.000 mm. Other speeds for the
description: 0.1 m/s top at 114.0 ms, 0.2 m/s top at 50.6 ms, 0.4 m/s
top at 37.0 ms (bottom at 19.43 N, a near miss), 0.41 top at 36.7 ms,
0.42 bottom at 34.5 ms (ball 4.49 mm), 0.5 bottom at 24.2 ms (ball 2.08
mm), 1 m/s bottom at 10.36 ms (0.362 mm), 5 m/s bottom at 2.00 ms (0.013
mm); the crossover sits between 0.41 and 0.42 m/s and depends on k, F
and c, so it goes to the description only, never to the narration or the
title. Integrate by RK4 at 100,000 steps per second (dt 1e-5 s; the
jerk's 5 ms is 500 steps) with the snap located by bisection inside the
step; check the slow pull against the quasi-static estimate and the jerk
against F / (k V) and the cubic; half-step rerun. Also print the fall
after the top snaps (when the bottom string goes slack, when the ball
leaves the band) and the wobble after the bottom snaps (amplitude,
period, the top tension's peak). State every number above as a check
the sim must print, not as a fact.

Drawing: front view, two bands (y 330-880 and 880-1430), the same hook,
ball, strings and hand in both, drawn at the same scale (400 px per
metre). The ball a 60 px disc; the strings thin lines whose stretch is
exaggerated 20x on screen (1 cm of real stretch drawn as 20 cm = 80 px)
so the slow pull's 1.1 cm of hand travel and the ball's 5 mm sink are
visible: draw the ball at rest + 20 x and the hand at its string's
anchor + 20 (V t - x) + the ball's drawn offset while that string is
intact; after a string snaps, the free bodies continue from where they
are drawn at true scale (the ball's fall after the top snaps, the hand's
run after the bottom snaps); write this rule in the docstring and say
"stretch drawn 20x" in the overlay and the legend. Each string's colour
warms from the panel colour toward coral as its tension nears 20 N. Two
vertical tension bars per band at the right (top string, bottom string)
with the 20 N break line in gold and the 9.8 N weight tick; a gold event
row "top string snaps at 0.217 s" / "bottom string snaps at 0.005 s" lit
at the snap, with the string drawn broken (a gap, the loose ends
recoiling); the left column: "pulled at 5 cm/s" / "jerked at 2 m/s" (40
px) and a live "ball moved N.NNN mm" (28 px) that freezes gold at the
snap. Shown at 1/10 speed: the slow pull snaps 2.17 s after the pull
starts, the jerk 0.05 s = 3 frames after; that instant snap is the
point, so flash the broken string and hold the event text. Cycle 8 s
with the pull starting 0.4 s in and a reset crossfade at the end, 5
cycles in 40 s, the last frame equal to the first; the fallen ball and
the departing hand must be out of the band before the fade (assert).
Nothing in the overlay rows 96-130 or under the captions from y 1440.

Day thirty-four, first slot. Chosen because it is the PIRA 1F20.10
prediction demo with a majority wrong answer, the panels end visibly
differently (the ball drops against the ball stays), and the mechanism
is one picture: the top string carries the weight plus the pull, the
bottom string only the pull, and a jerk outruns the ball. Question in
the first two seconds: "Pull slowly or jerk it. Which string snaps?"
(pre-tested through whisper at 10:03 today, passed; keep the question
identical in the title, the hook and the payoff). Setup number: each
string snaps at twenty newtons, twice the ball's weight. Payoff: pulled
slowly, the top string snaps, after a fifth of a second; jerked, the
bottom string snaps in five thousandths of a second, before the ball has
moved a tenth of a millimeter. The 0.41 m/s crossover, the other speeds
and the damping go to the description. Whisper risks: "jerk" / "jerked"
(passed once), "snaps" (passed), "newtons" (pre-test), "inertia" (avoid
in the hook; name it in the mechanism beat only if the picture shows
it), "five thousandths of a second" and "a tenth of a millimeter"
(pre-test; "five milliseconds" as a fallback), "kilo" (passed
2026-10-01); avoid "do you"; avoid "pull" as a noun (it risks "pole");
say "pull slowly" and "jerk it". Pre-test hooks with
scripts/voiceover.sh and keep the one whose question lands earliest
under two seconds. Measure every fixed text line with PIL before
rendering and keep every line under 950 px, and the title under 100
characters with no < or >. Music seed 104. Templates: sims/deskchain
(two bands, a clamp release inside the cycle, RK4 with bisection, reset
fade, layout asserts), sims/springdrop (a weight on a vertical spring,
a hand that moves), sims/capstan (rope tension readouts). Sim name
twostrings: sims/twostrings/twostrings.py, projects/twostrings/,
media/twostrings/.

## Claim (expected; the sim's numbers replace these)

A 1 kg ball between two strings that snap at 20 N (k 2000 N/m, 1 cm of
stretch): pulled down at 5 cm/s the top string snaps at 0.217 s after
the ball has sunk 5.1 mm (the bottom string at 11.5 N); jerked at 2 m/s
the bottom string snaps at 5.0 ms with the ball moved 0.085 mm (the top
string at 9.98 N). Narrated: a one kilo ball, a string above and a
string below, each snaps at twice the ball's weight (setup); pulled
slowly the top snaps after a fifth of a second, jerked the bottom snaps
in five thousandths of a second before the ball has moved a tenth of a
millimeter (payoff). Card: the question; slow pull: top string at 0.217
s, ball down 5.1 mm; jerk: bottom string at 0.005 s, ball moved 0.085
mm; the top string carries the weight plus the pull; crossover between
0.41 and 0.42 m/s for these strings; 0.5 m/s 0.024 s, 1 m/s 0.010 s.
Description: the model statement, the equation, the quasi-static and
cubic estimates, the other speeds, the RK4 checks, the damping rerun.

## Claim

A 1 kg ball between two identical strings (k 2000 N/m, each snapping at
20 N = 1 cm of stretch, 2.04 times the ball's weight; damping c = 1 N s/m
while the ball hangs on the top string; g 9.80665): pulled down at 5 cm/s
the top string snaps at 217.027 ms with the ball sunk 5.0967 mm and the
bottom string at 11.509 N (quasi-static estimate 203.867 ms, the ball lags
V t / 2 by 0.329 mm; no damping 219.048 ms; half step within 3.4e-12 ms);
jerked at 2 m/s the bottom string snaps at 5.042 ms with the ball moved
0.0849 mm and the top string at 9.977 N (closed form F / (k V) = 5.000 ms,
cubic 0.0833 mm; no damping 5.043 ms and 0.0850 mm; half step within
3.5e-15 ms). After the top snaps the bottom string pulls the falling ball
(peak 11.564 N, never snaps) until it goes slack 26.06 ms later, then free
fall; after the bottom snaps the ball wobbles on the top string with 1.111
mm amplitude and a 140.51 ms period (closed form 140.50), the top tension
peaking at 12.029 N. The crossover sits between 0.41 and 0.42 m/s
(bisected to 0.4130 m/s; 0.4154 with no damping). Narrated: each string
snaps at twenty newtons, twice the ball's weight (setup); pull slowly and
the top string snaps after a fifth of a second; jerk it and the bottom
string snaps in five thousandths of a second, before the ball has moved a
tenth of a millimeter (payoff). Card: the question; pulled at 5 cm/s: top
string at 0.217 s; jerked at 2 m/s: bottom string at 0.005 s; the ball
moved 5.1 mm, then 0.085 mm; the top string also carries the ball;
crossover between 0.41 and 0.42 m/s. Description: the model statement, the
equation, the quasi-static and cubic estimates, the other speeds, the
bisected crossover, the RK4 checks, the damping reruns, the fall and the
wobble.

## Evidence

### Measurements

media/twostrings/measure.log (`nix develop -c python3
sims/twostrings/twostrings.py --measure-only`, 2026-10-02 10:31:20 EEST,
final manifest):

```
Fri Oct  2 10:31:20 AM EEST 2026
setup: the same ball and the same strings in both panels: a ball of m = 1 kg hangs from a fixed hook on a string of stiffness k = 2000 N/m; an identical string hangs from the ball's underside down to a hand; each string is a massless linear spring that carries tension only (slack when shorter than its free length) and snaps the instant its tension reaches F = 20 N (10 mm of stretch; chosen numbers for a thin cord), 2.04 times the ball's weight; a small damping c = 1 N s/m on the ball while it hangs from the top string (chosen); g = 9.80665 m/s^2; x is the ball's downward displacement from rest and the hand moves down at a steady V from t = 0: f1 = m g + k x, f2 = k (V t - x), m x'' = k V t - 2 k x - c x'; top panel pulled at V = 0.05 m/s, bottom panel jerked at V = 2 m/s; integrated by RK4 at 100000 steps per second (dt = 1e-05 s) with the snap located by bisection inside the step, checked against the quasi-static estimate 2 (F - m g) / (k V), the jerk's F / (k V) and the cubic k V t^3 / (6 m), a half-step rerun and a no-damping rerun; after the top snaps the ball falls with the bottom string's pull until it goes slack, then freely (no drag); after the bottom snaps the ball wobbles on the top string (m x'' = -k x - c x'); shown at 1/10 speed on a 8 s cycle (480 frames) with the pull starting 0.4 s into the cycle, 5 cycles in 40 s; drawn at 400 px per metre with the stretch drawn 20x; deterministic, no seed
rest: the top string carries m g = 9.807 N, stretched m g / k = 4.903 mm; the bottom string is just taut at 0 N; the top string snaps when x = (F - m g) / k = 5.0967 mm, the bottom when V t - x = F / k = 10.000 mm; the ball's natural period on both strings 2 pi sqrt(m / 2 k) = 99.35 ms, on the top string alone 2 pi sqrt(m / k) = 140.50 ms; damping rate c / (2 m) = 0.5 per second
slow pull (top panel, V = 0.05 m/s = 5 cm/s): the top string snaps at 217.027 ms = 0.2170 s with the ball 5.0967 mm down (moving at 15.86 mm/s) and the hand 10.851 mm down; the top string at 20.000 N, the bottom string at 11.509 N; quasi-static estimate 2 (F - m g) / (k V) = 203.867 ms (x = V t / 2; the ball lags V t / 2 by 0.329 mm at the snap, which is the 13.160 ms gap); 21703 steps; half-step rerun (dt = 5e-06 s): 217.0266 ms (+3.4e-12 ms), ball 5.0967 mm; no damping: top at 219.048 ms, ball 5.0967 mm, bottom 11.711 N; after the snap the bottom string pulls the falling ball (its tension peaks at 11.564 N, under 20 N, so it never snaps) until it goes slack 26.06 ms later at 243.089 ms with the ball 12.154 mm down at 0.475 m/s; then free fall: the ball's drawn top is out of the band at 0.6237 s real = 6.24 s video after the pull starts
jerk (bottom panel, V = 2 m/s): the bottom string snaps at 5.042 ms = 0.0050 s with the ball 0.0849 mm down (moving at 50.3 mm/s) and the hand 10.085 mm down; the bottom string at 20.000 N, the top string at 9.977 N; closed form with the ball still F / (k V) = 5.000 ms; the cubic k V t^3 / (6 m) gives 0.0833 mm at 5.000 ms and 0.0855 mm at 5.042 ms; 505 steps (3.03 frames of video); half-step rerun: 5.0425 ms (-3.5e-15 ms), ball 0.0849 mm; no damping: bottom at 5.043 ms, ball 0.0850 mm, top 9.977 N; after the snap the ball wobbles on the top string: amplitude 1.111 mm (the ball's speed at the snap over omega = sqrt(k / m) = 44.72 per second gives sqrt(x^2 + (v / omega)^2) = 1.129 mm), first peak 1.111 mm at 38.24 ms, period 140.51 ms (closed form 140.50 ms), the top tension peaks at 12.029 N (never 20 N); the hand carries on at 2 m/s with the broken piece and is out of the band at 0.1667 s real = 1.67 s video after the pull starts
for the description: 0.1 m/s: the top string at 113.959 ms, ball 5.0967 mm, the other string at 12.598 N; 0.2 m/s: the top string at 50.579 ms, ball 5.0967 mm, the other string at 10.038 N; 0.4 m/s: the top string at 37.033 ms, ball 5.0967 mm, the other string at 19.433 N; 0.41 m/s: the top string at 36.660 ms, ball 5.0967 mm, the other string at 19.868 N; 0.42 m/s: the bottom string at 34.502 ms, ball 4.4909 mm, the other string at 18.789 N; 0.5 m/s: the bottom string at 24.155 ms, ball 2.0775 mm, the other string at 13.962 N; 1 m/s: the bottom string at 10.362 ms, ball 0.3621 mm, the other string at 10.531 N; 5 m/s: the bottom string at 2.003 ms, ball 0.0134 mm, the other string at 9.833 N; the crossover (top below, bottom above) sits between 0.41 and 0.42 m/s, bisected to 0.4130 m/s with c = 1 (0.4154 m/s with no damping); it depends on k, F and c
schedule (video time, 1/10 speed): cycles of 8 s start at -0.40, 7.60, 15.60, 23.60, 31.60, 39.60 s (the first 0.40 s before the first frame); the pull starts 0.4 s into each cycle at 0.00, 8.00, 16.00, 24.00, 32.00 s; the slow pull's top string snaps 2.17 s after the pull at 2.17, 10.17, 18.17, 26.17, 34.17 s (the event row lights, the ball falls at true scale), its bottom string goes slack at 2.43, 10.43, 18.43, 26.43, 34.43 s (the hand opens and steps aside over 0.3 s) and the ball is out of the band 4.07 s after the snap at 6.24, 14.24, 22.24, 30.24, 38.24 s (6.64 s into the cycle, before the fade at 7.40 s); the jerk's bottom string snaps 0.050 s = 3.0 frames after the pull at 0.05, 8.05, 16.05, 24.05, 32.05 s (the event row lights, the broken ends recoil over 0.3 s, the flash lasts 0.4 s) and the hand is out of the band at 1.67, 9.67, 17.67, 25.67, 33.67 s (2.07 s into the cycle); the ball's wobble period is 1.41 s of video; the reset crossfade runs over the last 0.6 s of each cycle (from 7.00, 15.00, 23.00, 31.00, 39.00 s; the readouts out over its first half and in over its second); on the first frame the cycle is 0.40 s in (0.000 s real after the pull starts: the slow panel pull at 0.000 mm, the jerk panel pull at 0.000 mm); title until 3 s; payoff card from 23.6 s; the title fades back in over the last 0.5 s and the last frame repeats the first (the scene is periodic: 40 s holds exactly 5 cycles)
on screen: the event rows read 'top string snaps at 0.217 s' / 'bottom string snaps at 0.005 s'; the readouts freeze at 'ball moved 5.097 mm, hand moved 10.85 mm' / 'ball moved 0.085 mm, hand moved 10.08 mm'; the card reads: pull slowly or jerk it. which string snaps? | pulled at 5 cm/s: top string at 0.217 s | jerked at 2 m/s: bottom string at 0.005 s | the ball moved 5.1 mm, then 0.085 mm | the top string also carries the ball | crossover between 0.41 and 0.42 m/s
text widths: overlay@34 797 px, title line 1@56 651 px, title line 2@56 637 px, legend@40 731 px, clock@28 436 px, clock held@28 194 px, label slow@40 360 px, ball moved slow@28 340 px, hand moved slow@28 361 px, event slow line 1@40 368 px, event slow line 2@40 224 px, label jerk@40 338 px, ball moved jerk@28 340 px, hand moved jerk@28 361 px, event jerk line 1@40 457 px, event jerk line 2@40 224 px, break@24 185 px, weight@24 71 px, bar value@24 88 px, snapped@24 115 px, bar top@24 45 px, bar bottom@24 98 px, payoff line 1@40 926 px, payoff line 2@40 851 px, payoff line 3@40 917 px, payoff line 4@40 889 px, payoff line 5@40 772 px, payoff line 6@40 845 px
row check: the left column ends at x 497 px; the ball column spans x 560 to 620 px and the hand x 590 to 676 px (746 px when it steps aside); the weight label starts at x 761 px and the bars span x 856 to 1008 px from 140 to 440 px under the band top (12 px per newton; the break line 200 px under the band top, the weight tick 322 px); the hook at 24 px, the ball's centre at rest 204 px and the pinch point 364 px under the band top; at the slow snap the ball's centre is drawn 244.8 px and the pinch point 450.8 px under the band top (the hand's lowest pixel 499 px); at the jerk's snap the pinch point is 444.7 px under the band top and the ball's drawn wobble is 8.9 px; the event rows at 300 and 346 px under the band top; each band is 550 px tall (y 330 to 880 and 880 to 1430); the caption band starts at y 1440; the title rows end at y 280 and the overlay band ends at y 130
Fri Oct  2 10:31:21 AM EEST 2026
```

Brief checks (every number is a line the sim printed):

- V 0.05 m/s: the top string snaps at 217.03 ms with the ball 5.097 mm
  down and the bottom string at 11.51 N: passed (217.027 ms, 5.0967 mm,
  11.509 N).
- Quasi-static estimate 2 (F - m g) / (k V) = 203.9 ms: passed (203.867
  ms); the gap is the ball's lag behind x = V t / 2: printed (0.329 mm at
  the snap, the 13.160 ms gap).
- No damping, slow pull 219.05 ms: passed (219.048 ms, bottom 11.711 N).
- V 2 m/s: the bottom string snaps at 5.043 ms with the ball 0.0850 mm
  down and the top string at 9.977 N: the sim gives 5.042 ms (5.0425 ms,
  the brief's 5.043 is the same value rounded up) with the ball 0.0849 mm
  down (the no-damping rerun gives 0.0850 mm) and the top string at 9.977
  N: passed within rounding.
- Closed form F / (k V) = 5.000 ms, the cubic k V t^3 / (6 m) = 0.0833 mm:
  passed (5.000 ms; 0.0833 mm at 5.000 ms, 0.0855 mm at 5.042 ms).
- The top string snaps when x = (F - m g) / k = 5.0967 mm, the bottom when
  V t - x = F / k = 10.000 mm: passed.
- Other speeds: 0.1 m/s top at 114.0 ms (113.959), 0.2 m/s top at 50.6 ms
  (50.579), 0.4 m/s top at 37.0 ms with the bottom at 19.43 N (37.033 ms,
  19.433 N), 0.41 top at 36.7 ms (36.660), 0.42 bottom at 34.5 ms with
  the ball 4.49 mm (34.502 ms, 4.4909 mm), 0.5 bottom at 24.2 ms with
  2.08 mm (24.155 ms, 2.0775 mm), 1 m/s bottom at 10.36 ms with 0.362 mm
  (10.362 ms, 0.3621 mm), 5 m/s bottom at 2.00 ms with 0.013 mm (2.003
  ms, 0.0134 mm): all passed.
- The crossover between 0.41 and 0.42 m/s: passed, and bisected to 0.4130
  m/s with c = 1 (0.4154 m/s with no damping); description only.
- RK4 at 100,000 steps per second with the snap by bisection inside the
  step; half-step rerun: passed (slow +3.4e-12 ms, jerk -3.5e-15 ms;
  21,703 and 505 steps; the jerk's 5 ms is 3.03 frames of video).
- The fall after the top snaps: printed (the bottom string's tension
  peaks at 11.564 N under 20 N, goes slack 26.06 ms after the snap at
  243.089 ms with the ball 12.154 mm down at 0.475 m/s; the ball's drawn
  top is out of the band 0.6237 s real = 6.24 s video after the pull
  starts).
- The wobble after the bottom snaps: printed (amplitude 1.111 mm, first
  peak at 38.24 ms, period 140.51 ms against 2 pi sqrt(m / k) = 140.50
  ms, the top tension peaks at 12.029 N). The brief expected an
  "invisible 0.085 mm wobble": the ball is moving at 50.3 mm/s when the
  string snaps, so the amplitude is sqrt(x^2 + (v / omega)^2) = 1.13 mm,
  not 0.085 mm; drawn 20x it is an 8.9 px shiver.
- Natural periods 2 pi sqrt(m / 2 k) = 99.35 ms and 2 pi sqrt(m / k) =
  140.50 ms: printed.
- The fallen ball and the departing hand out of the band before the fade:
  asserted (6.64 s and 2.07 s into the 8 s cycle; the fade starts at 7.40
  s).

### Production

- Sim: sims/twostrings/twostrings.py, modelled on sims/deskchain: RK4 at
  100,000 steps/s with a time-dependent forcing k V t and bisection on
  the snap step (rk4_pull), the fall after the top snap with the bottom
  string until slack (rk4_fall, bisection on the slack instant) then
  analytic free fall, the wobble after the bottom snap (rk4_wobble, peaks
  by parabolic vertex), closed-form, half-step and no-damping checks, the
  other speeds and the crossover bisection; the drawing reads the RK4
  tables (np.interp); 2x supersampled bands; loop, periodicity and
  loop-step checks; ffmpeg rawvideo pipe with a ProcessPoolExecutor;
  --measure-only and --frames. The drawing rule (stretch drawn 20x while a
  string is intact, true scale for the free bodies after a snap, the hand
  stepping aside when its slack string stops acting) is in the docstring.
- Manifest projects/twostrings/manifest.json: seed 0, fps 60, g 9.80665,
  mass 1 kg, stiffness 2000 N/m, break 20 N, damping 1 N s/m, speeds slow
  0.05 / jerk 2 m/s, description speeds 0.1 / 0.2 / 0.4 / 0.41 / 0.42 /
  0.5 / 1 / 5, crossover bracket 0.41-0.42, 100,000 steps/s, wobble run 1
  s, slow 10, cycle 8 s, release_at 0.4, first_cycle_at -0.4, reset_fade
  0.6, recoil 0.3 s, flash 0.4 s, hand aside 0.3 s, scene 40 s, 400 px/m,
  stretch_draw_x 20, string column x 590, hook 24 px, top string 150 px,
  ball radius 30 px, bottom string 130 px, title "Pull slowly or jerk
  it.|Which string snaps?" until 3 s, payoff_t 23.6, payoff_hold 0.6, six
  card lines formatted from the measured values, loop_fade 0.5, music
  seed 104, gain 0.18, voice offset 0.6, caption_y 0.75, overlay "1 kg
  ball | 1/10 speed | stretch drawn 20x".
- Layout: overlay y 96-130 (compose); title two rows at y 190 / 252 until
  3 s; legend "same strings, stretch drawn 20x" at y 236 and the clock
  ("held, at rest" / "N.NNN s after the pull starts") at y 290 after the
  title; bands y 330-880 (pulled at 5 cm/s, teal) and 880-1430 (jerked at
  2 m/s, sky); per band: label (40 px) at 40 px under the band top, "ball
  moved N.NNN mm" (28 px, gold and frozen at the snap) at 84, "hand moved
  NN.NN mm" (28 px muted, frozen at the snap) at 120; the hook bar at 24
  px, the ball's centre at rest 204 px, the pinch point 364 px under the
  band top on x 590; the hand a palm with two fingers pinching the string
  from the right (opens and steps 70 px aside when its string goes slack
  after the top snap); the strings warm from the panel colour toward
  coral as their tension nears 20 N and break into two recoiling stubs
  with a gold flash ring; two tension bars at x 856 and 972 (36 px wide,
  140-440 px under the band top, 12 px per newton) with the gold break
  line labelled "snaps at 20 N", the "9.8 N" weight tick, live values
  above ("snapped" in gold after a snap) and "top" / "bottom" under; the
  gold event rows "top string snaps" / "at 0.217 s" and "bottom string
  snaps" / "at 0.005 s" at 300 and 346 px under the band top in the left
  column; the six-line gold card from y 1572 at a 48 px pitch; nothing in
  rows 96-130 or 1440-1530 (asserted in the row check and measured on the
  footage).
- Hook pre-tests (media/twostrings/hooks/pretest.log, 10:27): hook1
  ("Pull slowly or jerk it. Which string snaps? One ball, a string above,
  a string below. Each string snaps at twenty newtons, twice the ball's
  weight.") ok 9.21 s, the first sentence to 1.33 s and the question's
  second sentence to 2.66 s of voice; hook2 (the question reordered,
  "Which string snaps? Pull slowly, or jerk it.") ok 8.41 s; hook3 ok 9.03
  s; hook1 chosen because it keeps the brief's question word for word
  (the title and the payoff repeat it). words.txt: "Pull slowly", "Jerk
  it", "Jerked", "The hand jerks", "The hand jerks it", "The top string
  snaps", "The bottom string snaps", "Twenty newtons", "Twice the ball's
  weight", "After a fifth of a second", "In five thousandths of a
  second", "A tenth of a millimeter", "Five milliseconds", "One kilo",
  "Before the ball can follow", "The hand is gone", "It snaps alone",
  "The ball stays", "The ball drops", "It reaches twenty newtons first"
  all passed (25.14 s).
- Narration: projects/twostrings/narration.txt, 110 words; the question
  is the first two sentences (spoken 0.60-3.12 s of video) and is
  repeated word for word ("Pull slowly or jerk it. Which string snaps?")
  before the payoff; one setup number (twenty newtons, twice the ball's
  weight) and one payoff pair (after a fifth of a second; in five
  thousandths of a second, before the ball has moved a tenth of a
  millimeter); the mechanism sentence names only what the frame shows
  (the top bar starts at the 9.8 N weight tick; the bottom string
  stretches while the ball stays); American spelling; no digits; no "do
  you", no "pull" as a noun.
- Voice (media/twostrings/voice.log): pass 1 (112 words, 10:28:11)
  failed, "newtons" heard as "newt ons" and the sentence-initial "Pulled"
  as "pull ed"; pass 2 (10:28:49, one "newtons" only, the payoff recast
  as "Pull slowly, and the top string snaps ..." / "Jerk it, and the
  bottom string snaps ...") ok 35.25 s at 112 words; pass 3 (10:29:12,
  trimmed to 110 words: "Each string snaps" to "Each snaps", "Both
  strings stretch" to "Both stretch") ok 34.18 s. voice.wav ends at
  34.78 s of video; no leading silence over 0.05 s (speech from under
  0.65 s of video).
- timing.log (voice offset 0.6 s; whisper's own spelling):

```
  0.60 -   3.12  Pull slowly or jerk it.
 Which string snaps?
  3.12 -   5.02  A string above the ball, one below.
  5.02 -  10.87  Each snaps at 20 newtons, twice the ball's weight, on top
 the hand pulls slowly, both stretch.
 10.87 -  13.26  but the top one also carries the ball.
 13.26 -  17.11  so it snaps first and the ball drops below the hand jerks
 17.11 -  20.60  The bottom string stretches before the ball can follow and
 snaps.
 20.60 -  21.69  The ball stays.
 21.69 -  23.35  Pull slowly or jerk it.
 23.35 -  25.64  Which string snaps?
 Pull slowly.
 25.64 -  29.13  and the top string snaps after a fifth of a second.
 Jerk it!
 29.13 -  32.15  and the bottom string snaps in five thousandths of a second
.
 32.15 -  34.78  before the ball has moved a tenth of a millimeter.
voice 34.18 s, ends at 34.78 s of video
```

- Schedule and sync: pulls at 0, 8, 16, 24, 32 s; slow snaps at 2.17,
  10.17, 18.17, 26.17, 34.17 s; jerk snaps at 0.05, 8.05, 16.05, 24.05,
  32.05 s. "A string above the ball, one below. Each snaps at twenty
  newtons, twice the ball's weight." 3.12-8.0 over the setup; "On top,
  the hand pulls slowly. Both stretch," 8.0-10.9 as the cycle-2 pull
  starts at 8.0 and the strings warm; "but the top one also carries the
  ball." 10.87-13.26 with the top string just snapped at 10.17 and the
  ball falling (slack at 10.43, out at 14.24); "so it snaps first, and the
  ball drops." 13.26-15.5 as the ball leaves the band; "Below, the hand
  jerks." 15.5-17.1 over the cycle-3 jerk at 16.05 (the flash and the
  event row); "The bottom string stretches before the ball can follow,
  and snaps. The ball stays." 17.11-21.69 with the broken bottom string,
  the hand gone at 17.67 and the ball on the top string; "Pull slowly or
  jerk it. Which string snaps?" 21.69-24.8 as the cycle 3-4 crossfade runs
  (23.0-23.6) and the card rises from 23.6 (full at 24.2); "Pull slowly,
  and the top string snaps after a fifth of a second." 24.8-29.1 with the
  cycle-4 top snap at 26.17 lighting "top string snaps at 0.217 s" under
  those words; "Jerk it, and the bottom string snaps in five thousandths
  of a second, before the ball has moved a tenth of a millimeter."
  29.1-34.78 with the card's "bottom string at 0.005 s" and "0.085 mm"
  on screen and the cycle-5 jerk at 32.05; the title fades back in over
  39.5-40.0 s.
- Smoke frames viewed before the render: smoke-{0.0, 1.0, 2.2, 2.6, 3.5,
  5.0, 6.8, 7.3, 8.1, 9.0, 23.3, 39.6, 39.98}.png on the first layout
  (bars at x 880 / 964, string at x 600: the bar value labels collided,
  "snapped" over "11.5 N") and smoke-{1.0, 2.6, 8.1}.png on the final
  layout (bars at x 856 / 972, string at x 590; a label-pair assert
  added): title and resting setup at 0; the strings warming and the jerk's
  hand departing at 1.0; the slow snap flash at 2.2; the slack string and
  the hand aside at 2.6; the fall at 3.5; the ball gone at 6.8; the
  crossfade at 7.3; the jerk flash at 8.1; the card at 23.3; the loop fade
  at 39.6 and the title back at 39.98. All text inside the frame.
- Render (media/twostrings/render.log, 10:31:21-10:31:47): loop check 0
  px, periodicity check 0 px, loop step 0 px (threshold 24 levels), footage
  40.00 s at 60 fps, 2400 frames.
- Compose (media/twostrings/compose.log, 10:31:57-10:32:08): music seed
  104, 40.00 s; captions 19 pauses detected, 19 matched (max chunk start
  shift 1.434 s against word-count timing); contact sheet 8x5 at 1 fps;
  final.mp4 40.000000 s; preview.mp4 40.066667 s.
- Text widths (PIL ImageFont.getlength, DejaVuSans-Bold, asserted < 950
  px): overlay@34 797, title@56 651 / 637, legend@40 731, clock@28 436
  (held 194), labels@40 360 / 338, ball moved@28 340, hand moved@28 361,
  event lines@40 368 / 224 and 457 / 224, break@24 185, weight@24 71, bar
  value@24 88, snapped@24 115, bar names@24 45 / 98, payoff lines@40 926 /
  851 / 917 / 889 / 772 / 845 px.

### Local QA

- Frames extracted from media/twostrings/final.mp4 (never edited) with
  ffmpeg -ss T and viewed at full resolution:
  - 0.00: overlay "1 kg ball | 1/10 speed | stretch drawn 20x", the title
    "Pull slowly or jerk it. / Which string snaps?", both panels at rest
    (ball moved 0.000 mm, hand moved 0.00 mm, top bars at 9.8 N, bottom
    0.0 N, the gold "snaps at 20 N" line), no caption, no card.
  - 1.00: the slow panel pulling (ball 2.484 mm, hand 5.00 mm, top 14.8 N
    coral, bottom 5.0 N); the jerk panel already snapped (ball 0.085 mm
    gold, "bottom string snaps at 0.005 s", "snapped", the hand departing
    at the band bottom with its stub); caption "Pull slowly or jerk".
  - 2.20: the slow snap: the gold flash ring on the top string, "top
    string snaps at 0.217 s", ball 5.097 mm gold, top bar "snapped",
    bottom 11.5 N; caption "Which string snaps?".
  - 11.00 (mid-run, cycle 2 at 0.300 s): legend and clock, the ball
    falling with the slack string hanging under it, the hand open and
    aside, both bars empty ("snapped" / 0.0 N); the jerk panel's ball on
    the top string at 11.1 N; caption "Both stretch, but".
  - 16.30 (cycle 3 at 0.030 s): the slow panel pulling (0.373 mm, 10.6 N);
    the jerk flash ring with the hand just below it, "bottom string snaps
    at 0.005 s"; caption "Below, the hand".
  - 24.50 (payoff + 0.9, cycle 4 at 0.050 s): the card full in gold, both
    panels in their early-cycle states; caption "Which string snaps?".
  - 26.30 (cycle 4 at 0.230 s): the top string's flash ring and "top
    string snaps at 0.217 s" lit under the caption "top string snaps";
    the card full.
  - 33.00 (cycle 5 at 0.100 s): both panels mid-cycle, the card full;
    caption "the ball has moved a".
  - 39.983 (frame 2399): the title back, both panels at rest, the same
    picture as 0.00; no caption, no card.
  Nothing clipped at the frame edges, no text in the caption band; the
  card's text spans rows 1560-1829 on the 24.50 s frame (PIL row scan).
- sheet.png (8x5 at 1 fps): five identical cycles: the resting setup, the
  jerk's string broken in the first tile of each cycle with the hand
  leaving, the slow panel's strings warming then the top one breaking and
  the ball dropping out with the hand aside, the crossfade back; captions
  under; the card from the tile at 24 s.
- Question timing: on screen from frame 0 in the title; spoken from under
  0.65 s of video (no leading silence over 0.05 s in voice.wav plus the
  0.6 s offset); timing.log puts both sentences in 0.60-3.12 s, and in the
  hook1 pre-test the first sentence ends at 1.33 s of voice and "Which
  string snaps?" at 2.66 s (about 1.9 and 3.3 s of video); repeated at
  21.69-24.8 s; answered "Pull
  slowly, and the top string snaps after a fifth of a second. Jerk it, and
  the bottom string snaps in five thousandths of a second ..." at
  24.8-34.78 s.
- Captions: 36 chunks of at most 20 characters, 0.60-34.78 s; the
  concatenated caption text equals narration.txt word for word (110
  words, compared by script from media/twostrings/captions.filter).
- Payoff number on screen when spoken: the card is full from 24.2 s
  ("top string at 0.217 s", "bottom string at 0.005 s", "5.1 mm, then
  0.085 mm") while "after a fifth of a second" is spoken about 27-29 s,
  "in five thousandths of a second" 29.1-32.15 s and "a tenth of a
  millimeter" 32.15-34.78 s; the event rows "top string snaps at 0.217 s"
  (lit from 26.17) and "bottom string snaps at 0.005 s" (lit from 24.05)
  are on screen through the payoff.
- Footage signalstats: overlay band (rows 96-130) and caption band (rows
  1440-1530) YMAX 28 in all 2400 footage frames; both bands hold only the
  background.
- Loop: render.log loop check 0 px and periodicity check 0 px on the
  footage. Final loop noise (codec only): frame 39.983 vs 0.00: 29,159 px
  over 8 levels, 553 over 32, max 65, mean 0.53.
- ffprobe final.mp4: h264 1080x1920 yuv420p 60/1, 2400 frames, duration
  40.000000 s, aac 22050 Hz mono, moov before mdat (faststart; ftyp 0,
  moov 32, free 44780, mdat 44788), 4,059,966 bytes.
- md5sum media/twostrings/final.mp4: 5a8cfc05098bf5fcb6165d1491320940.
- Narrated numbers against measure.log: "twenty newtons" (F = 20 N),
  "twice the ball's weight" (2.04 times the ball's weight), "after a fifth
  of a second" (the top string snaps at 217.027 ms = 0.2170 s, after 0.2
  s), "five thousandths of a second" (the bottom string snaps at 5.042 ms
  = 0.0050 s), "a tenth of a millimeter" (the ball 0.0849 mm down, under
  0.1 mm), "pulled at 5 cm/s" / "jerked at 2 m/s" on screen (V = 0.05 m/s
  = 5 cm/s, V = 2 m/s). All on printed lines.
- Metadata number check by script (commas stripped): 106 numbers in the
  description (67 distinct), none missing from measure.log; the title's
  0.217 and 0.005 present (the "on screen" line prints the event rows and
  the card).

### Metadata

- Title (99 characters, ASCII, no < or >): Pull slowly or jerk it. Which string snaps? Slow: the top at 0.217 s. Jerked: the bottom at 0.005 s
- Description: 3,796 characters, ASCII, no arrows; one setup paragraph
  (the model, every constant, the equation, RK4 and its checks, 1/10
  speed with the stretch drawn 20x, 5 runs in 40 s, no seed), "Measured:"
  bullets (the rest state and thresholds, the slow pull with its
  estimate and reruns and the fall, the jerk with its closed forms and
  reruns and the wobble, the other speeds, the bisected crossover, the
  natural periods and the step count), a "Why:" paragraph, the rerun
  line, the AI line.
- Tags (11): which string snaps, inertia ball, pull slowly or jerk it, inertia demonstration, inertia, first law of motion, string snaps, physics, physics visualization, simulation, shorts.
- categoryId "27", privacyStatus "private", containsSyntheticMedia true,
  selfDeclaredMadeForKids false.

### Deviations from the brief

- The jerk's snap prints as 5.042 ms (5.0425 ms) and the ball's sink as
  0.0849 mm; the brief's 5.043 ms and 0.0850 mm are the same values
  rounded up (the no-damping rerun gives 5.043 ms and 0.0850 mm). The
  card, the title and the narration say 0.005 s and 0.085 mm.
- The wobble after the bottom snaps has an amplitude of 1.111 mm, not
  the brief's "invisible 0.085 mm": the ball has 50.3 mm/s of speed when
  the string snaps (v / omega = 1.12 mm). Drawn 20x it is an 8.9 px
  shiver; the narration does not mention it; the description gives the
  measured value.
- The damping acts only while the ball hangs on the top string; after
  the top snaps the ball falls without drag (c = 1 N s/m would be an
  unphysical 4 N of drag at 4 m/s). Stated in the docstring, the setup
  line and the description.
- When the bottom string goes slack after the top snap, the hand opens
  and steps 70 px aside and the slack string is drawn limp under the
  falling ball (the brief did not say what the hand does; the model has
  no collision and a slack string does not act on the ball). The
  slow-pull hand therefore stays in the band until the crossfade; only
  the jerk's hand leaves it.
- The event row is two lines ("top string snaps" / "at 0.217 s") in the
  left column at 40 px, since the one-line form is 457 px wide at the
  column's width.
- The overlay drops "no seed" ("1 kg ball | 1/10 speed | stretch drawn
  20x | no seed" is 983 px at 34 px); the legend is "same strings,
  stretch drawn 20x" ("same ball, same strings, stretch drawn 20x" is
  977 px at 40 px). The description says "Deterministic, no seed".
- The card's sixth line gives only the crossover bracket ("crossover
  between 0.41 and 0.42 m/s"); the 0.5 and 1 m/s times go to the
  description (the combined line is over 950 px).
- hook1 keeps the brief's question word for word, so the second sentence
  of the question ("Which string snaps?") ends at 3.12 s of video; the
  question starts under 0.65 s and is on screen from frame 0. hook2 put
  "Which string snaps?" first (done by 1.9 s) but reorders the question.
- The brief's payoff wording "Pulled slowly, the top string, after a
  fifth of a second" became "Pull slowly, and the top string snaps after
  a fifth of a second" and "Jerk it, and the bottom string snaps in five
  thousandths of a second ..." (whisper split the sentence-initial
  "Pulled" into "pull ed"); the second "newtons" was dropped ("newt
  ons").
- payoff_t 23.6 s (the brief's structure; chosen from timing.log so the
  card is full at 24.2 s, before "Pull slowly, and the top string snaps"
  at about 24.8 s).
- The crossover was bisected (0.4130 m/s with c = 1, 0.4154 without) in
  addition to the 0.41 / 0.42 bracket; description only.

## Niche note

  [produced 2026-10-02 as "Pull slowly or jerk it. Which string snaps?
  Slow: the top at 0.217 s. Jerked: the bottom at 0.005 s"; measured a
  1 kg ball on two identical strings (k 2000 N/m, snapping at 20 N = 1 cm
  of stretch, 2.04 times the weight; damping 1 N s/m on the hanging ball;
  g 9.80665), RK4 at 100,000 steps/s with bisection at the snap: pulled
  at 5 cm/s the top string snaps at 217.027 ms with the ball 5.0967 mm
  down and the bottom string at 11.509 N (quasi-static 203.867 ms, the
  ball lags V t / 2 by 0.329 mm; no damping 219.048 ms; half step within
  3.4e-12 ms), then the bottom string pulls the falling ball (peak 11.564
  N) until slack 26.06 ms later; jerked at 2 m/s the bottom string snaps
  at 5.042 ms with the ball 0.0849 mm down and the top string at 9.977 N
  (F / (k V) = 5.000 ms, cubic 0.0833 mm; no damping 5.043 ms, 0.0850 mm;
  half step within 3.5e-15 ms), then the ball wobbles 1.111 mm at 140.51
  ms (closed form 140.50) with the top string peaking at 12.029 N; other
  speeds 0.1 / 0.2 / 0.4 / 0.41 m/s top at 113.959 / 50.579 / 37.033 /
  36.660 ms, 0.42 / 0.5 / 1 / 5 m/s bottom at 34.502 / 24.155 / 10.362 /
  2.003 ms; crossover between 0.41 and 0.42 m/s, bisected to 0.4130 m/s
  (0.4154 with no damping); shown at 1/10 speed with the stretch drawn
  20x on an 8 s cycle, 5 pulls in 40 s; task 20261002-101233]

## Upload

- orchestrator review (2026-10-02T10:52:39+03:00): task evidence, sheet.png and full frames at
  0.00, 2.20, 11.00, 26.30 and 39.98 s inspected; ffprobe h264 1080x1920 60 fps
  2400 frames 40.000 s; md5 5a8cfc05098bf5fcb6165d1491320940; title 99 chars, no angle brackets; description 3796 chars, no angle brackets, 11 tags; captions match narration word for word, compose pause alignment 19 of 19; measure.log matches the closed forms (V 0.05 m/s: top string at 217.03 ms with the ball 5.097 mm down and the bottom string at 11.51 N; V 2 m/s: bottom string at 5.043 ms with the ball 0.0850 mm down and the top string at 9.977 N; snap stretch (F - m g) / k = 5.0967 mm and F / k = 10.000 mm); question on screen from frame 0 and
  repeated word for word before the payoff; nothing clipped at the 1080 px
  frame; last frame equals the first; approved for upload
- upload attempt 1 of 5 for the quota day that began 2026-10-02T10:00
  EEST, recorded at 2026-10-02T10:52:39+03:00 before starting scripts/yt-upload.py; zero
  attempts were on record since the boundary (journal and media/*/upload.log
  checked at 10:51:59)
- uploaded private as yD8XL-OnEz4 at 2026-10-02T10:52:51+03:00
  (https://youtu.be/yD8XL-OnEz4); channels.list 1 unit + videos.insert
  1,600 units; media/twostrings/upload.log
- scripts/yt-qa.py twostrings yD8XL-OnEz4 --wait --publish in the
  foreground (started 2026-10-02T10:53:00+03:00): gate 15 of 15 on the first
  processed read (processed, succeeded, hd, 1080x1920, title, description
  and tags match, category 27, not made for kids, PT41S for the 40.000 s
  file, private before publish); published at 2026-10-02T10:53:17+03:00;
  re-read privacyStatus=public selfDeclaredMadeForKids=False
  embeddable=True; yt-qa quota 53 units; media/twostrings/publish.log
- attempt 1 of 5 complete: 1,654 units; slot 1 of 3 resolved as
  published (recorded 2026-10-02T10:53:46+03:00)

### Quota
- attempt 1 of the hard cap of 5 for the quota day that began
  2026-10-02T10:00 EEST; cost 1,654 units (the channels.list verification
  inside yt-upload.py, the 1,600-unit insert, and the gate run's reads,
  update and re-read as printed by yt-qa.py, 53); day total after one
  attempt 1,654 of 10,000 used, 8,346 remaining
