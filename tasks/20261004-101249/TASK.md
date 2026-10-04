# Produce short: Atwood drop, 1.1 kg against 1.0 kg beside a free drop, how slowly does it fall

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day36

## Goal

Backlog idea (trend research 2026-09-25, task 20260925-101408, pillar 2
chaos and physics, everyday mechanics; read the full entry under "Added
by trend research 2026-09-25" in docs/niche.md): "Atwood drop: a 1.1 kg
weight dropped beside the same weight on a string over a pulley against
1.0 kg; measure the time to fall 1 m; expect 0.452 s against 2.069 s,
4.58 times slower, the acceleration g / 21 (0.467 m/s^2) because both
weights must speed up, not g / 11 (1.50 s) as the weight difference alone
suggests; closed form; mild surprise, so rank it low; repeat the drop;
deterministic, no seed."

Orchestrator notes (2026-10-04, before this brief; closed forms in
/tmp/day36/closed.py, g = 9.807). The model: on the left a 1.1 kg weight
is held 1.00 m above a floor pad and dropped; it falls freely at g (no
air drag, say so) and the pad stops it (no bounce). On the right the same
1.1 kg weight hangs on a light string over a light, frictionless pulley
against a 1.0 kg weight; the heavy weight starts level with the dropped
one, 1.00 m above its pad, the light weight starts on its own pad on the
floor; both weights are held and let go at the same instant as the drop.
String massless and inextensible, pulley massless and frictionless (say
so; a pulley with mass is a description-only variant), so the two weights
share one speed and the system obeys (m1 + m2) a = (m1 - m2) g: a = 0.1
g / 2.1 = g / 21 = 0.4670 m/s^2, the tension T = 2 m1 m2 g / (m1 + m2) =
10.274 N (0.9524 of the heavy weight's 10.788 N, 1.0476 of the light
weight's 9.807 N). The heavy weight reaches its pad after sqrt(2 h / a) =
2.0695 s at 0.966 m/s and the pad stops it (the light weight is then 1 m
up and the string goes slack; hold both there until the reset, say so);
the free weight lands at sqrt(2 h / g) = 0.4516 s at 4.43 m/s. Integrate
both with RK4 at dt = 1e-4 s as a check against the closed forms (a
half-step rerun agreeing within 1e-9 s), print the energy balance of the
Atwood pair (m1 g x - m2 g x against (1/2)(m1 + m2) v^2, to 1e-12), the
tension, and the position and speed tables at 0.25 s intervals for
both.

Checks, not facts (the sim must print and compare; state them as
checks): a = 0.4670 m/s^2 = g / 21.00 exactly (m1 + m2 = 21 (m1 - m2));
the heavy weight lands at 2.0695 s, the free weight at 0.4516 s; the
ratio 4.5826 = sqrt(21); the naive g / 11 = 0.8915 m/s^2 would land it at
1.4978 s (print it as the wrong guess); the heavy weight has dropped a t^2 / 2 =
0.4670 * 0.4516^2 / 2 = 4.76 cm when the free one lands (print the exact
figure and use the sim's value); speeds at the floor 0.9664 against 4.4288 m/s; the tension
10.274 N; for the description: a 0.2 kg pulley disc (I / r^2 = 0.1 kg): a
= 0.4458 m/s^2, 2.1182 s; a 0.5 kg disc: 0.4173 m/s^2, 2.1892 s; 1.2 kg
against 1.0: g / 11, 1.4978 s; 1.5 against 1.0: g / 5, 1.0098 s; 2.0
against 1.0: g / 3, 0.7822 s. Print the schedule in video time, the text
widths and the layout clearances.

Drawing: one shared scene between y 330 and 1430 (sims/yoyo style), side
view, because the two weights must share one height scale: a release
line (the start height of the two 1.1 kg weights) across both columns
with two small hand marks, the free 1.1 kg weight at x 330 drawn as a
block (a lighter rounded rectangle with "1.1 kg" inside at 28 px), the
Atwood heavy 1.1 kg weight at x 700 hanging on a thin string that runs
up over a pulley (a disc with a hub, drawn at the top of the scene,
centred over x 790 at about y 380; the string's two vertical legs at x
700 and x 880) and down to the 1.0 kg weight at x 880 resting on the
floor pad at the start; a 1 m height scale on the left (x 150 to 230,
ticks every 10 cm, "1 m" at the bottom, "0" at the top), the floor pads
(lighter slabs) under each weight at 1.00 m below the release line, with
the floor slab below them; 700 px per metre, so the 1 m drop is 700 px
(release line near y 480, pads near y 1180; keep the pulley, its string
and the risen light weight inside y 330 to 1430 and clear of the title
rows which end at y 280). The 1.0 kg weight rises 1 m as the heavy one
falls (it ends level with the release line). Live readouts (28 px): a
left column "dropped: NN.N cm down" and its real-time clock, a right
column "on the pulley: NN.N cm down" and "speed N.NN m/s"; gold event
rows under the pads (y 1290 and 1340 or so, above the caption band at
1440): "dropped: lands at 0.45 s; the pulley weight 4.8 cm down" (lit at
the free landing and held) and "on the pulley: lands at 2.07 s, 4.6x
later" (lit at the Atwood landing and held). The pulley turns with the
string (a spoke mark on the disc so it reads; circumference arbitrary,
choose a 6 cm radius drawn to scale, 42 px). Shown at 1/3 speed; cycle
10 s (600 frames): both let go 1.0 s into the cycle, the free weight
lands at 1.0 + 1.355 = 2.35 s of the cycle, the heavy weight at 1.0 +
6.209 = 7.21 s; hold; the weights are reset by a crossfade over the last
0.6 s of the cycle; 4 cycles in 40 s, exactly periodic, the last frame
equal to the first. The legend row after the title: "same weight, same
height, 1/3 speed"; the shared clock in real seconds since the release.
Overlay: "1.1 kg against 1.0 kg | 1 m drop | 1/3 speed | no seed"
(measure it; shorten to "1.1 kg vs 1.0 kg | 1 m | 1/3 speed | no seed" if
over 950 px).

Day thirty-six, second slot. Chosen because "which lands first" drops are
the channel's strongest format (folded chain against a ball 990 views,
yo-yo against a ball yesterday, stick against a ball 735), the weights
end visibly differently (the free one is down while the pulley pair has
barely moved, then creeps down for two seconds), the factor is exact
(root twenty one, like the yo-yo's root nineteen and the broom's root
eight), and the repeat is a natural loop. Question in the first two
seconds: "Hang one point one kilograms against one. How fast does the
heavy side fall?" is too long before the question; prefer "Which weight
lands first?" or "How slowly does the heavy side fall?" as the question
after a short setup ("Two weights, the same one point one kilograms.")
and pre-test the variants; keep the question identical in the title, the
hook and the payoff. Setup number: one point one kilograms against one
(spoken as "one point one kilograms against one kilogram"; pre-test).
Payoff: the free weight lands in under half a second; the heavy side on
the pulley takes two seconds, four point six times as long (speak at
most two numbers in the payoff beat: "two seconds" and "four point six
times" are the preferred pair; "point four five seconds" and "two point
zero seven seconds" go to the card). The mechanism sentence must follow
the picture: only the extra tenth of a kilogram pulls, but it has to get
both weights moving, two point one kilograms in all, so the pair speeds
up at one twenty first of a free fall (never "pull" as a noun; "pulls"
as a verb is fine; "one twenty first" must be pre-tested, "a twenty
first" is the fallback, else say "twenty one times more slowly"). The
g / 11 wrong guess, the tension and the pulley variants go to the card
and the description. Whisper risks: "Atwood" (avoid in narration; the
title and description can carry it), "pulley" (pre-test), "kilograms"
and "kilogram" (pre-test), "one point one" (pre-test), "root twenty
one" (pre-test; "root eight" passed 2026-10-02, "root nineteen" failed
2026-10-03 as "route"), "hangs", "lands", "creeps" (pre-test), avoid
"do you", avoid "fly", avoid "pull" as a noun. Pre-test hooks with
scripts/voiceover.sh and keep the one whose question lands earliest under
two seconds. Measure every fixed text line with PIL before rendering and
keep every line under 950 px, and the title under 100 characters with no
< or >. Music seed 111. Templates: sims/yoyo (one shared scene, a drop
beside a drop with the height scale, the finish line, releases on a
cycle with a reset fade, loop checks; read it whole), sims/chain (the
hand marks and the floor slab), sims/deskchain (layout asserts, the
clock, the crossfade). Sim name atwood: sims/atwood/atwood.py,
projects/atwood/, media/atwood/.

## Claim (expected; the sim's numbers replace these)

A 1.1 kg weight dropped from 1 m lands at 0.452 s. The same 1.1 kg weight
on a string over a light pulley against 1.0 kg, let go from the same
height at the same instant, lands at 2.069 s, 4.58 times later (exactly
sqrt(21)): it accelerates at g / 21 = 0.467 m/s^2 because the 0.1 kg of
net weight must move all 2.1 kg, not at g / 11 (1.50 s) as the weight
difference alone suggests; the string holds 10.27 N. Narrated: one point
one kilograms against one (setup); the free weight lands first, in under
half a second; the pulley side takes two seconds, four point six times
as long (payoff). Card: the question; dropped 0.45 s, on the pulley 2.07
s, 4.58x = root 21; a = g / 21; not g / 11 (1.50 s); the string holds
10.3 N; a 0.5 kg pulley: 2.19 s. Description: the model statement, the
equations, the two drops, the tension, the wrong guess, the pulley-mass
and mass-ratio variants, the checks.

## Claim

A 1.1 kg weight dropped from 1.00 m lands at 0.4516 s at 4.43 m/s (g =
9.807 m/s^2, no air drag, the pad stops it). The same 1.1 kg weight on a
massless inextensible string over a massless frictionless pulley against
1.0 kg, let go from the same height at the same instant, accelerates at
(m1 - m2) g / (m1 + m2) = g / 21 = 0.4670 m/s^2 and lands at 2.0695 s,
1.6179 s after the dropped weight and 4.5826 times later (exactly
sqrt(21)), at 0.9664 m/s; when the dropped weight lands the heavy weight
is only 4.762 cm down; the string holds 10.274 N (0.9524 of the heavy
weight, 1.0476 of the light one); the weight difference alone would
suggest g / 11 and a landing at 1.4978 s. RK4 at dt 1e-4 s with
compensated summation agrees with the closed forms to +0.0e+00 s and the
half-step rerun to 1e-9 s. Narrated: one point one kilograms against one
kilogram, one third speed (setup); the dropped one, down in under half a
second; the pulley side takes two seconds, four point six times as long
(payoff). Card: the question; dropped 0.45 s, on the pulley 2.07 s;
4.58x = root 21, a = g / 21; 0.1 kg of net weight moves all 2.1 kg; not g
/ 11 (1.50 s); tension 10.3 N; a 0.5 kg pulley disc 2.19 s.

## Evidence

### Measurements

The final measure.log (media/atwood/measure.log, 2026-10-04 10:38:21 to
10:38:22 EEST, exit 0, written by sims/atwood/atwood.py with
projects/atwood/manifest.json --measure-only; the render at 10:38:23 to
10:38:59 printed the same numbers):

```
Sun Oct  4 10:38:21 AM EEST 2026
warning: Git tree '/home/alex/personal/seedzero' is dirty
setup: one scene, side view, both weights on one height scale: on the left a 1.1 kg weight is held 1 m above a floor pad and dropped; it falls freely at g = 9.807 m/s^2 with no air drag and the pad stops it, no bounce; on the right the same 1.1 kg hangs on a string over a pulley against 1 kg; the heavy weight starts level with the dropped one, 1.00 m above its own pad, and the light weight starts on its pad on the floor; both are held and let go at the same instant as the drop; the string is massless and inextensible and the pulley massless and frictionless (a pulley with mass is a description-only variant), so the two weights share one speed; the pad stops the heavy weight, the light weight is then 1 m up, level with the release line, the string goes slack and both rest until the reset; both drops integrated by RK4 at 10000 steps per second (dt = 1e-04 s) with compensated (Kahan) summation of the state, the landing located by bisection inside the step, a half-step rerun as a check, against the closed forms; shown at 1/3 speed on a 10 s cycle (600 frames) with both let go 1 s into the cycle, 4 cycles in 40 s; drawn at 640 px per metre (the blocks 120 x 56 px, the pulley 90 px in radius = 14.06 cm at this scale, its size does not enter the motion); deterministic, no seed
model: (m1 + m2) a = (m1 - m2) g gives a = 0.1000 kg x g / 2.1000 kg = 0.46700 m/s^2 = 0.4670 m/s^2 = 0.467 m/s^2 = g / 21.0000 = g / 21.00 (exactly g / 21: (m1 + m2) / (m1 - m2) = 21.0000, diff -1.8e-14); the tension T = m2 (g + a) = 10.2740 N = m1 (g - a) = 10.2740 N = 2 m1 m2 g / (m1 + m2) = 10.2740 N = 10.274 N = 10.3 N, 0.9524 of the heavy weight's 10.788 N = 10.8 N and 1.0476 of the light weight's 9.807 N; the net weight on the pair is (m1 - m2) g = 0.9807 N moving 2.1 kg; a is the same for any height
dropped weight (RK4, 4516 steps): lands at 0.451593 s = 0.4516 s = 0.45 s (closed form sqrt(2 h / g) = 0.451593 s, diff +0.0e+00 s; under half a second: 0.4516 < 0.5) at 4.4288 m/s = 4.43 m/s (closed form g t = 4.4288 m/s, diff -8.9e-16); energy balance m g x against m v^2 / 2 within 5.3e-15 J; half-step rerun (dt = 5e-05 s): 0.451592697 s (+0.0e+00 s); the pad stops it
on the pulley (RK4, 20695 steps): the heavy weight lands at 2.069458 s = 2.0695 s = 2.069 s = 2.07 s (closed form sqrt(2 h / a) = 2.069458 s, diff +0.0e+00 s; about two seconds), 1.6179 s after the dropped weight, 4.5826 times later = 4.58 times = 4.6 times (exactly sqrt(21) = 4.5826, diff -1.8e-15), moving at 0.9664 m/s = 0.966 m/s = 0.97 m/s (closed form sqrt(2 a h) = 0.9664 m/s, diff +0.0e+00) against the dropped weight's 4.4288 m/s; when the dropped weight lands at 0.4516 s the heavy weight has dropped 0.04762 m = 4.762 cm = 4.76 cm = 4.8 cm (closed form a t^2 / 2 = h / 21 = 4.762 cm, diff +1.6e-10 m) at 0.2109 m/s = 0.21 m/s, and the light weight has risen the same 4.8 cm; when the heavy weight lands the dropped one has been down for 1.6179 s = 1.62 s; the light weight is then 1 m up, level with the release line, with zero speed, and the string goes slack (tension 0); energy balance (m1 - m2) g x against (m1 + m2) v^2 / 2 within 3.3e-16 J over the drop; half-step rerun (dt = 5e-05 s): lands at 2.069457718 s (+0.0e+00 s) at 0.966436754 m/s (+0.0e+00 m/s)
wrong guess: the weight difference alone, 0.1 kg of 1.1 kg, suggests a = g / 11 = 0.8915 m/s^2, which would land the heavy weight at 1.4978 s = 1.50 s, 3.32 times the free drop; the true a = g / 21 because the 0.1 kg of net weight must get all 2.1 kg moving, 1.9091 times more mass than the difference alone counts
tables (RK4 tables, real time since the release): 0.00 s: dropped 0.0 cm, 0.00 m/s; pulley side 0.0 cm down, 0.000 m/s, light weight 0.0 cm up; 0.25 s: dropped 30.6 cm, 2.45 m/s; pulley side 1.5 cm down, 0.117 m/s, light weight 1.5 cm up; 0.50 s: dropped on the pad (100 cm); pulley side 5.8 cm down, 0.234 m/s, light weight 5.8 cm up; 0.75 s: dropped on the pad (100 cm); pulley side 13.1 cm down, 0.350 m/s, light weight 13.1 cm up; 1.00 s: dropped on the pad (100 cm); pulley side 23.4 cm down, 0.467 m/s, light weight 23.4 cm up; 1.25 s: dropped on the pad (100 cm); pulley side 36.5 cm down, 0.584 m/s, light weight 36.5 cm up; 1.50 s: dropped on the pad (100 cm); pulley side 52.5 cm down, 0.701 m/s, light weight 52.5 cm up; 1.75 s: dropped on the pad (100 cm); pulley side 71.5 cm down, 0.817 m/s, light weight 71.5 cm up; 2.00 s: dropped on the pad (100 cm); pulley side 93.4 cm down, 0.934 m/s, light weight 93.4 cm up; 2.25 s: dropped on the pad (100 cm); pulley side on the pad (100 cm), light weight 100 cm up
for the description: a 0.2 kg uniform pulley disc (I / r^2 = 0.1 kg) with the same weights: a = 0.9807 N / 2.20 kg = 0.4458 m/s^2 = g / 22.00, lands at 2.1182 s = 2.12 s (closed form 2.1182 s, diff +0.0e+00 s), 4.69 times the free drop; a 0.5 kg uniform pulley disc (I / r^2 = 0.25 kg) with the same weights: a = 0.9807 N / 2.35 kg = 0.4173 m/s^2 = g / 23.50, lands at 2.1892 s = 2.19 s (closed form 2.1892 s, diff +0.0e+00 s), 4.85 times the free drop; 1.2 kg against 1 kg (massless pulley): a = g / 11.00 = 0.8915 m/s^2, lands at 1.4978 s = 1.50 s (closed form 1.4978 s, diff +0.0e+00 s), 3.32 times the free drop, the string holding 10.699 N; 1.5 kg against 1 kg (massless pulley): a = g / 5.00 = 1.9614 m/s^2, lands at 1.0098 s = 1.01 s (closed form 1.0098 s, diff +2.2e-16 s), 2.24 times the free drop, the string holding 11.768 N; 2 kg against 1 kg (massless pulley): a = g / 3.00 = 3.2690 m/s^2, lands at 0.7822 s = 0.78 s (closed form 0.7822 s, diff +0.0e+00 s), 1.73 times the free drop, the string holding 13.076 N
brief checks (26 of 26 agree at the brief's precision): a (m/s^2): brief 0.4670, sim 0.4670 (ok); g / a: brief 21.00, sim 21.00 (ok); t heavy (s): brief 2.0695, sim 2.0695 (ok); t free (s): brief 0.4516, sim 0.4516 (ok); ratio: brief 4.5826, sim 4.5826 (ok); sqrt(21): brief 4.5826, sim 4.5826 (ok); naive a = g / 11 (m/s^2): brief 0.8915, sim 0.8915 (ok); naive t (s): brief 1.4978, sim 1.4978 (ok); heavy down when the free lands (cm): brief 4.76, sim 4.76 (ok); v heavy at the pad (m/s): brief 0.9664, sim 0.9664 (ok); v free at the pad (m/s): brief 4.4288, sim 4.4288 (ok); tension (N): brief 10.274, sim 10.274 (ok); T / heavy weight: brief 0.9524, sim 0.9524 (ok); T / light weight: brief 1.0476, sim 1.0476 (ok); heavy weight (N): brief 10.788, sim 10.788 (ok); light weight (N): brief 9.807, sim 9.807 (ok); 0.2 kg disc a (m/s^2): brief 0.4458, sim 0.4458 (ok); 0.2 kg disc t (s): brief 2.1182, sim 2.1182 (ok); 0.5 kg disc a (m/s^2): brief 0.4173, sim 0.4173 (ok); 0.5 kg disc t (s): brief 2.1892, sim 2.1892 (ok); 1.2 kg: g / a: brief 11.0, sim 11.0 (ok); 1.2 kg t (s): brief 1.4978, sim 1.4978 (ok); 1.5 kg: g / a: brief 5.0, sim 5.0 (ok); 1.5 kg t (s): brief 1.0098, sim 1.0098 (ok); 2.0 kg: g / a: brief 3.0, sim 3.0 (ok); 2.0 kg t (s): brief 0.7822, sim 0.7822 (ok)
drawing: the string turns the pulley x / r = 7.111 rad = 1.132 turns over the 1 m drop (0.182 turns per video second on average, 2.19 degrees per frame at the end), counterclockwise as the heavy side goes down; a spoke mark on the disc shows it; the string is drawn as the two vertical legs and the arc over the top of the disc; the gold 4.8 cm tick appears left of the heavy block at its depth when the dropped weight lands
schedule (video time, 1/3 speed): cycles of 10 s start at -10.00, 0.00, 10.00, 20.00, 30.00 s (the first -0.00 s before the first frame); both let go 1 s into each cycle at 1.00, 11.00, 21.00, 31.00 s; the dropped weight lands 1.355 s after the release at 2.35, 12.35, 22.35, 32.35 s (the first event row lights, the gold 4.8 cm tick appears beside the heavy block; it rests on its pad until the fade); the heavy weight on the pulley lands 6.208 s after the release at 7.21, 17.21, 27.21, 37.21 s (7.21 s into the cycle; the second event row lights; the light weight is then level with the release line and both rest); the heavy weight is 2.6 cm down 1 s of video after the release, 10.4 cm after 2 s and 41.5 cm after 4 s; the reset crossfade runs over the last 0.6 s of each cycle (from 9.40, 19.40, 29.40, 39.40 s; the readouts out over its first half and in over its second; the blocks blend back to the release line and the light weight to its pad); on the first frame the cycle is 0.00 s in (-0.333 s real: the dropped weight held, the pulley pair held); title until 3 s; payoff card from 30.4 s; the title fades back in over the last 0.5 s and the last frame repeats the first (the scene is periodic: 40 s holds exactly 4 cycles)
text widths (the on-screen strings verbatim): overlay@34 820 px '1.1 kg vs 1.0 kg | 1 m | 1/3 speed | no seed', title line 1@56 814 px 'Two weights, both 1.1 kg.', title line 2@56 565 px 'Which lands first?', legend@40 844 px 'same weight, same height, 1/3 speed', clock@28 390 px '2.070 s after the release', clock held@28 194 px 'held, at rest', row free held@28 333 px 'dropped: in the hand', row free moving@28 547 px 'dropped: 100.0 cm down, 4.43 m/s', row free landed@28 541 px 'dropped: 100.0 cm down, stopped', row atw held@28 408 px 'on the pulley: in the hand', row atw moving@28 623 px 'on the pulley: 100.0 cm down, 4.43 m/s', row atw landed@28 616 px 'on the pulley: 100.0 cm down, stopped', block heavy@28 98 px '1.1 kg', block light@28 98 px '1.0 kg', scale top@28 19 px '0', scale bottom@28 58 px '1 m', tick@24 90 px '4.8 cm', event 1@40 929 px 'dropped: 0.45 s, pulley side 4.8 cm down', event 2@40 905 px 'on the pulley: lands at 2.07 s, 4.6x later', payoff line 1@40 785 px 'which lands first? the dropped one', payoff line 2@40 815 px 'dropped 0.45 s, on the pulley 2.07 s', payoff line 3@40 853 px '4.58x later, exactly root 21: a = g / 21', payoff line 4@40 838 px '0.1 kg of net weight moves all 2.1 kg', payoff line 5@40 848 px 'not g / 11, which would land at 1.50 s', payoff line 6@40 920 px 'tension 10.3 N; 0.5 kg pulley disc: 2.19 s'
row check: the readout rows end at x 663 px (the pulley's left edge is at x 700); both rows end at y 418; the hand marks rise to y 506 over the block tops at y 544; the release line is at y 600 (x 250 to 960); the pulley is centred at (790, 432) with radius 90 px (y 342 to 522; its lowest point over a block's inner edge is at y 516.9), hanging from a bracket ending at y 340; the string legs are at x 700 and 880 from y 432; the free block spans x 270 to 390 and drops from y 544..600 to 1184..1240; the heavy block x 640 to 760 the same way; the light block x 820 to 940 rises from y 1184..1240 to 544..600; the pads from y 1240 to 1256 (x 258..402, 628..772, 808..952), the floor to y 1280; the scale at x 230 with ticks to x 200 and labels from x 136; the gold tick at y 630.5 from x 610 to 630, its label from x 514; the event rows at y 1326 and 1374 (from 1304 to 1396, widest 929 px centred on 540); the band is y 330 to 1430; the caption band starts at y 1440; the title rows span y 162 to 280, the overlay band ends at y 130
exit 0
Sun Oct  4 10:38:22 AM EEST 2026
```

Checks from the brief: the sim's own check block reports 26 of 26
agreeing at the brief's precision (a = 0.4670 m/s^2 = g / 21.00; t heavy
2.0695 s; t free 0.4516 s; ratio 4.5826 = sqrt(21); naive g / 11 =
0.8915 m/s^2 landing at 1.4978 s; 4.76 cm down when the free weight
lands; 0.9664 and 4.4288 m/s at the pads; tension 10.274 N, 0.9524 and
1.0476 of the weights 10.788 and 9.807 N; the 0.2 kg and 0.5 kg disc
variants 2.1182 and 2.1892 s; the 1.2, 1.5 and 2.0 kg variants g / 11,
g / 5, g / 3 at 1.4978, 1.0098 and 0.7822 s). Energy balances within
5.3e-15 J (free) and 3.3e-16 J (pair); half-step rerun +0.0e+00 s on
both landings; the tables at 0.25 s intervals printed; the schedule,
text widths and row check printed and asserted.

### Production

- Sim: sims/atwood/atwood.py (one shared scene between y 330 and 1430,
  sims/yoyo style, both weights on one 640 px per metre height scale;
  RK4 at 10000 steps per second with Kahan summation, bisection on the
  landings, a half-step rerun; measure() prints every number, the text
  widths and the row check and asserts them). Manifest
  projects/atwood/manifest.json: seed 0, fps 60, scene_duration 40.0,
  slow 3.0 (1/3 speed), cycle_s 10.0, release_at 1.0, title "Two
  weights, both 1.1 kg.|Which lands first?", title_until 3.0, payoff_t
  30.4, payoff_hold 0.6, loop_fade 0.5, music_seed 111, music_gain 0.18,
  voice_offset 0.6, caption_y 0.75, overlay "1.1 kg vs 1.0 kg | 1 m |
  1/3 speed | no seed" (820 px; the brief's longer overlay measured over
  950 px and the brief named this fallback).
- Layout deviation from the brief: 640 px per metre instead of 700 (the
  release line at y 600, the pads at y 1240) so the pulley (radius 90 px
  at (790, 432), hanging from a bracket at y 340) and the risen light
  weight stay inside y 330 to 1430 and clear of the title rows ending
  at y 280; the row check in measure.log lists every clearance.
- Hook pre-tests (media/atwood/hooks/pretest.log, 10:25): six hooks,
  all passing the round trip. hook3 "Which lands first? Two weights,
  both one point one kilograms, one of them on a pulley." puts the
  question first (question start 0.0 s of voice, 0.6 s of video) and
  was kept; the others put the question at 1.46 s (hook4), 2.03 to 2.46
  s (hooks 1, 2, 5, 6) of voice. The risky-words test (words.txt) found
  "one twenty first" heard as "21st" and "root twenty one" as "route";
  both phrasings were dropped from the narration ("twenty one times
  more slowly" and "four point six times as long" are used instead).
- Narration: projects/atwood/narration.txt, 112 words, the question
  "Which lands first?" is the first sentence and is repeated word for
  word before the payoff; setup numbers one point one kilograms, one
  kilogram, one third speed; mechanism "only the extra tenth of a
  kilogram pulls, but it must move both weights, two point one
  kilograms in all, so the pair speeds up twenty one times more slowly
  than a free fall"; payoff "the dropped one, down in under half a
  second, while the pulley side takes two seconds, four point six times
  as long".
- Voice (media/atwood/voice.log): pass 1 at 10:36:04 (110 words) failed
  on "light weight" heard as "lightweight"; pass 2 at 10:36:18 failed
  on a dropped "second"; pass 3 at 10:37:24 (112 words, "the lighter
  one rises" and "under half a second, while") passed: "ok: transcript
  matches narration (35.282721s)". voice-timing.py (timing.log): the
  question at 0.71 to 1.96 s of video, the payoff "the dropped one" at
  29.27 s, "four point six times as long" at 34.06 to 35.88 s, the
  voice ends at 35.88 s of video.
- Schedule and sync: releases at 1.0, 11.0, 21.0 and 31.0 s of video;
  the dropped weight lands at 2.35, 12.35, 22.35, 32.35 s and the heavy
  weight at 7.21, 17.21, 27.21, 37.21 s; "The dropped one is down at
  once" is spoken at 10.23 to 13.60 s over the second cycle's drop and
  landing at 12.35 s; "The pulley side creeps" over its creep; the
  payoff card rises at 30.4 s as "the dropped one" is spoken (29.27 to
  30.21 s) and the fourth cycle's drop at 32.35 s plays under "down in
  under half a second"; the heavy landing at 37.21 s under the end of
  "four point six times as long".
- Smoke frames (media/atwood/smoke-*.png at 0.0, 1.5, 2.0, 2.5, 4.0,
  7.3, 9.7, 12.4, 31.6, 37.3, 39.7, 39.983) viewed by the producer at
  10:32 before the render. Render log (media/atwood/render.log,
  10:38:23 to 10:38:59): 2400 frames, the loop check "the scene drawn
  live at 40 s differs from 0 s in 0 px", the loop step 1361 px between
  the last two frames (the title fading back in), footage.mp4 40.00 s at
  60 fps.
- Compose (media/atwood/compose.log, 10:38:59 to 10:39:13): music seed
  111 40.00 s; "captions: 19 pauses detected, 19 matched, max chunk
  start shift 1.022 s against word-count timing"; final.mp4 40.000000 s,
  preview.mp4, sheet.png 8x5 at 1 fps.
- Text widths: every on-screen string measured in measure.log at its
  drawn size, widest the event row 1 at 929 px, every line under 950 px.

### Local QA (orchestrator, 2026-10-04 18:05 to 18:20 EEST)

- Frames extracted from final.mp4 at 0.00, 1.00, 2.10, 15.00, 30.80,
  32.20, 33.50, 37.30 and 39.983 s (media/atwood/qa-*.png) and viewed.
  0.00: overlay, the two title rows "Two weights, both 1.1 kg. / Which
  lands first?", both 1.1 kg blocks held at the release line with hand
  marks, the 1.0 kg block on its pad, the pulley with its spoke mark,
  the 1 m scale, no caption yet. 2.10: the dropped block 65.9 cm down
  at 3.60 m/s, the pulley block 3.1 cm down at 0.17 m/s, the pulley
  turned, caption "Two weights, both" under the scene. 15.00: legend
  "same weight, same height, 1/3 speed", clock 1.333 s after the
  release, the dropped block on its pad, the pulley block 41.5 cm down,
  the gold 4.8 cm tick, the first gold event row, caption "of a
  kilogram pulls,". 30.80: the fourth cycle held at rest with the gold
  payoff card (six lines) and caption "down in under half a". 32.20:
  0.400 s after the release, the dropped block 78.5 cm down, the pulley
  block 3.7 cm down, the card up, caption "second, while the". 39.983:
  identical to frame 0 (title back, blocks held, no caption or card).
  sheet.png (8x5 at 1 fps) shows the four cycles, the captions in
  order, the event rows lighting after each landing and the card from
  31 s.
- Question timing: on screen from frame 0 in the title; spoken from
  0.82 s (caption "Which lands first?" enabled 0.823 to 2.089 s).
- Captions: 37 drawtext chunks from 0.823 to 35.883 s; their
  words match narration.txt word for word (112 of 112, checked by
  script after stripping punctuation).
- Payoff: "the dropped one" spoken at 29.27 s with the card from 30.4 s
  carrying "dropped 0.45 s, on the pulley 2.07 s" and the event rows
  "dropped: 0.45 s, pulley side 4.8 cm down" and "on the pulley: lands
  at 2.07 s, 4.6x later" lit from the first cycle; "four point six
  times as long" spoken at 34.06 to 35.88 s with the 4.6x row and the
  4.58x card line on screen.
- Bands: ffmpeg signalstats on footage.mp4 crops, caption band rows
  1440 to 1530 YMAX 28 and overlay band rows 96 to 130 YMAX 28 over all
  2400 frames (background only).
- Loop: render.log loop check 0 px; the last frame viewed equals the
  first.
- ffprobe final.mp4: h264 1080x1920 60/1 fps, duration 40.000000 s,
  aac 22050 Hz; atom order ftyp, moov, free, mdat (faststart).
- md5sum final.mp4: ff236b08457695c7fa49dae5e6037c94
- Narrated numbers against measure.log: one point one kilograms (1.1
  kg), one kilogram (1 kg), one third speed (1/3 speed), a tenth of a
  kilogram (0.1 kg), two point one kilograms (2.1 kg), twenty one times
  (g / 21), under half a second (0.4516 < 0.5), two seconds (2.0695 s,
  "about two seconds"), four point six times (4.6 times): every one is
  a line in measure.log.
- Metadata numbers: all 89 distinct numbers in the description appear
  in measure.log (commas stripped, checked by script).

### Metadata

projects/atwood/metadata.json: title "Two 1.1 kg weights. Which lands
first? Dropped: 0.45 s. On a pulley vs 1.0 kg: 2.07 s, 4.6x later" (97
characters, ASCII, no < or >); description 4308 characters (the model
and the constants, "Measured:" bullets, "Why:", the rerun line, the
agent line); 12 tags (two weights which lands first, atwood machine,
pulley, pulley physics, which lands first, free fall, newton's second
law, acceleration, physics, physics visualization, simulation, shorts);
categoryId 27, privacyStatus private, containsSyntheticMedia true,
selfDeclaredMadeForKids false.

### Deviations from the brief

- 640 px per metre instead of 700, so the pulley and the risen light
  weight fit inside the scene band (see Production).
- The short overlay "1.1 kg vs 1.0 kg | 1 m | 1/3 speed | no seed" (the
  brief's fallback) because the long form measured over 950 px.
- Hook3 (question first) kept instead of the brief's "Two weights,
  both 1.1 kg..." hook, because the question lands at 0.6 s of video
  instead of 2.6 s.
- The producer agent stopped before writing the metadata and the
  evidence (its session ended at about 10:39); the orchestrator wrote
  both from the logs and its own QA pass at 18:05 to 18:20.

## Niche note

[produced 2026-10-04 as "Two 1.1 kg weights. Which lands first?
Dropped: 0.45 s. On a pulley vs 1.0 kg: 2.07 s, 4.6x later"; measured
a = g / 21 = 0.4670 m/s^2, the dropped weight lands at 0.4516 s, the
pulley side at 2.0695 s, 4.5826x = sqrt(21), 4.76 cm down when the free
weight lands, tension 10.274 N; task 20261004-101249]

### Upload

- Attempt 1 of 5 of the quota day 2026-10-04T10:00 EEST (zero earlier attempts): scripts/yt-upload.py atwood started at 2026-10-04T18:11:07+03:00 (videos.insert, 1,600 units), private.
- Outcome: uploaded private as YPXH-ht0gEo (https://youtu.be/YPXH-ht0gEo) at 2026-10-04T18:11:13+03:00, the insert succeeded on its first try.
- QA gate: scripts/yt-qa.py atwood YPXH-ht0gEo --wait --publish run once in the foreground at 18:11:29: uploadStatus processed, processingStatus succeeded, hd, 1080x1920, title, description and tags match, categoryId 27, not made for kids, duration PT41S (40.000 s), private before publish; gate 15 of 15 on the first processed read.
- Published: privacyStatus public at 2026-10-04T18:12:03+03:00, re-read public, embeddable, madeForKids false. Quota this run 54 units; 1,654 units for the slot.
- Niche note appended to the Atwood drop bullet in docs/niche.md at 2026-10-04T18:12:57+03:00.
