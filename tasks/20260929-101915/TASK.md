# Produce short: Ice cube or ball uphill, a sliding cube beside a rolling ball at the same speed

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day31

## Goal

Backlog idea (trend research 2026-09-29, task 20260929-100144, pillar 2
chaos and physics, rolling; read the full entry under "Added by trend
research 2026-09-29" in docs/niche.md):
"Ice cube or ball uphill: an ice cube sliding on ice beside a solid
ball rolling, both at 3 m/s at the foot of the same 20 degree slope;
measure how high each climbs; expect 45.9 cm against 64.2 cm, the
ball 1.400 times higher because its spin climbs too (h = (1 + k) v^2 /
2g, k = 2/5; cylinder 1.5x, hollow ball 1.667x, hoop exactly 2x), tops
at 0.894 and 1.252 s; rolling needs mu 0.104 or more ((2/7) tan
theta); a rolling ball that meets an ice slope stops at 45.9 cm still
spinning; V valley so each panel repeats (periods 3.91 and 5.34 s with
a 0.5 m flat); deterministic, no seed."

Orchestrator notes (2026-09-29, before this brief). The model: panel A,
an ice cube (say 4 cm) that slides with no friction; panel B, a solid
ball (say radius 3 cm, I = (2/5) m r^2) that rolls without slipping on
a grippy ramp (mu 0.104 or more needed on the slope, (k / (1 + k)) tan
20; print it). The ramp geometry is identical in both panels: a flat
run-in, a smooth circular fillet (radius about 0.3 m; the producer's
choice) into a straight 20 degree slope long enough that neither
object reaches its end. Both cross the same start mark on the flat at
3.0 m/s (the ball rolling, omega = v / r). Integrate each along the
track (arc-length coordinate) by RK4 at 6,000 steps a second or finer;
for the ball the equation of motion along the track is s'' = -g sin
(slope angle) / (1 + k) with the centre on the offset curve; measure
the rise of each centre of mass. Checks, not facts (orchestrator closed
forms in /tmp/day31/check.py, g = 9.80665): cube rises 45.89 cm (v^2 /
2g), 134.17 cm along the slope if the slope started at the start mark;
ball rises 64.24 cm, 187.83 cm along, exactly 7/5 = 1.4000 times the
cube; on a plain slope the tops come 0.8944 and 1.2522 s after the foot
(the fillet changes the times a little; print both the plain-slope
closed form and the sim). Both rise the same way on the way up only
because the ball's spin energy (2/7 of its total) also turns into
height; the ball must slow its spin as it climbs, which needs friction.
Print the friction the ball needs along the whole path (it must stay
under the chosen mu everywhere, including the fillet) and the normal
force (stays positive). For the description print the solid cylinder
1.5x (68.83 cm), hollow ball 1.667x (76.48 cm), hoop 2x (91.77 cm), and
the rolling ball that meets an ice slope: it rises only 45.89 cm and
keeps spinning at the top. Energy check to 1e-9 on both panels.

State every derived number above as a check the sim must print, not as
a fact.

Drawing: two panels stacked, the same ramp drawn identically at the same
scale and the same clock; panel A an ice cube on a pale icy ramp, panel
B a ball with a stripe or a dot so the spin shows, on a darker grippy
ramp; height ticks on the slope (10 cm steps) or a height ruler at the
side; a live "height NN cm" readout for each; a peak marker left at the
highest point of each (a gold tick and "46 cm" / "64 cm") that stays
after the object slides back; a faint horizontal line from the cube's
peak across the ball's panel is optional if it reads clearly. Each
object climbs, stops, and runs back down the slope and off the flat;
repeat the run (fade and reset as tablecloth does, or the V-valley
loop if it keeps both panels on one clock); slow motion so the 1.3 s
climb plays over 2 to 4 s (say the factor on screen); several runs in
about 40 s; the last frame equals the first.

Day thirty-one, second slot. Chosen because "same speed, which climbs
higher?" splits intuition (the research search tool's own summary got
it wrong), the two panels end at visibly different heights, the 7/5 is
exact and closed form, and no seed. Question in the first two seconds:
"Ice cube or ball. Which climbs higher?" (or the producer's better
wording; keep the words before the question under nine; keep the
question identical in the title, the hook and the payoff). Setup number:
three meters a second (the same speed). Payoff number: the ball,
sixty four centimeters against forty six, one point four times as
high; its spin turns into height too. The 7/5, the times, the friction
and the other shapes go to the card and the description. Say "slides
with no friction" and "rolls without slipping" in the description; the
narration can say "slides on ice" and "rolls". Whisper risks: "ice
cube" may come back "ice cubes"; "climbs" may come back "climes";
"higher" is fine; avoid "do you" before a verb; write "one point four
times" (not "1.4") and "centimeters" (American); pre-test the hooks
with scripts/voiceover.sh and keep the one whose question lands
earliest under two seconds. Make the last frame equal the first.
Measure every fixed text line with PIL before rendering and keep every
line under 950 px, and the title under 100 characters with no < or >.
Music seed 96. Templates: sims/rollrace (rolling bodies on a ramp with
k), sims/racingballs (a rolling ball along a shaped track, RK4 along
the track), sims/tablecloth (two panels on one clock, slow motion,
cycles, reset fade). Sim name uphill: sims/uphill/uphill.py,
projects/uphill/, media/uphill/.

## Claim

An ice cube that slides with no friction and a solid ball (I = (2/5) m
r^2) that rolls without slipping cross the same start mark at 3 m/s and
meet the same 20 degree slope (a 0.3 m fillet from the flat). The
cube's centre rises 45.89 cm, v0^2 / 2 g. The ball's centre rises 64.24
cm, (1 + 2/5) v0^2 / 2 g: 1.4000 times as high, 18.35 cm higher,
because its spin (2/7 of its energy at the mark, 0.2857) also turns
into height; the grip slows the spin from 50.0 rad/s to 0.0 at the top.
The tops come 0.9916 s (cube) and 1.3494 s (ball) after the mark,
0.9083 and 1.2661 s after the foot of the fillet (0.8944 and 1.2522 s
on a plain slope with no fillet). Rolling needs friction of at most
0.1040 of the normal force ((2/7) tan 20); the ramp has 0.6, and the
normal force stays between 0.940 and 4.824 weights. The same ball on an
ice slope rises only 45.89 cm and is still spinning at 50.0 rad/s at the
top. Narrated: three meters a second (setup); the ball climbs higher,
sixty four centimeters against forty six, one point four times as high;
its spin turns into height as well (payoff). Card: the question; 64 cm
against 46: 1.40 times; its spin, 2/7 of its energy, climbs too; top at
1.35 s (ball) and 0.99 s (cube); mu 0.104 or more; cylinder 1.5x,
hollow ball 1.67x, hoop 2x. Description: the other shapes, the ball on
ice, the forces and the checks.

## Evidence

### Measurements

`nix develop -c python3 sims/uphill/uphill.py --measure-only` at
10:40:25 EEST (the final manifest), media/uphill/measure.log, copied
whole:

```
Tue Sep 29 10:40:25 AM EEST 2026
setup: the same ramp in both panels, a flat run-in, a circular fillet of radius 0.3 m starting 0.25 m past the start mark and a straight 20 degree slope that runs off the frame; top panel an ice cube of side 12 cm that slides with no friction (k = 0, its centre 6 cm above the surface), bottom panel a solid ball of radius 6 cm (I = 0.4 m r^2) that rolls without slipping on a grippy ramp (friction coefficient 0.6); both centres ride the same offset curve (fillet radius 0.24 m); both cross the start mark at 3 m/s, the ball spinning at v0 / r = 50.0 rad/s (7.96 turns a second); (1 + k) s'' = -g sin alpha(s) along the centre path, g = 9.80665 m/s^2; RK4 at 12000 steps per second (dt = 8.33e-05 s) with the top and the return located by bisection inside the step; shown at 1/3 speed on a 10 s cycle (600 frames) with the mark crossed 0.8 s into the cycle, 4 cycles in 40 s; drawn at 380 px per metre; deterministic, no seed
cube: RK4: the ice cube's centre rises 45.89 cm (closed form (1 + k) v0^2 / 2 g = 45.89 cm, diff -1.1e-11 cm); the top comes 0.9916 s after the mark, 0.9083 s after the foot of the fillet (0.0833 s after the mark) and 0.8802 s after the start of the straight slope (reached at 0.1114 s); on a plain slope with no fillet the top would come 0.8944 s after the foot, 134.17 cm along the slope; here the centre travels 138.31 cm along its path from the foot (129.93 cm of it along the straight slope); back at the mark at 1.9832 s at 3.000000 m/s; the energy (1 / 2)(1 + k) v^2 + g y_c drifts by 2.5e-13 of the starting kinetic energy over 23799 steps; the normal force is 0.940 to 4.824 weights (at least 4.644 and at most 4.824 on the fillet, 0.940 on the slope), never zero
ball: RK4: the ball's centre rises 64.24 cm (closed form (1 + k) v0^2 / 2 g = 64.24 cm, diff -1.0e-11 cm); the top comes 1.3494 s after the mark, 1.2661 s after the foot of the fillet (0.0833 s after the mark) and 1.2380 s after the start of the straight slope (reached at 0.1114 s); on a plain slope with no fillet the top would come 1.2522 s after the foot, 187.83 cm along the slope; here the centre travels 191.98 cm along its path from the foot (183.60 cm of it along the straight slope); back at the mark at 2.6988 s at 3.000000 m/s; the energy (1 / 2)(1 + k) v^2 + g y_c drifts by 3.2e-13 of the starting kinetic energy over 32386 steps; the normal force is 0.940 to 4.824 weights (at least 4.678 and at most 4.824 on the fillet, 0.940 on the slope), never zero; to roll without slipping it needs a friction force f = m g sin alpha k / (1 + k) of up to 0.0977 weights, at most 0.1040 of the normal force (on the straight slope, (k / (1 + k)) tan theta = 0.1040; at most 0.0209 on the fillet), under the ramp's 0.6 everywhere; its spin v / r falls from 50.0 rad/s at the mark to 0.0 at the top; at the mark 0.2857 of its energy (2/7) is spin
the two panels: the ball's centre rises 64.24 cm against the cube's 45.89 cm, 1.4000 times as high ((1 + k) = 1.4000), 18.35 cm higher; the ball tops out 1.3494 s after the mark against 0.9916 s, and is back at the mark at 2.6988 s against 1.9832 s; same speed at the mark, but the ball carries an extra 2/5 of its motion energy in its spin, and the grip turns that spin into height as it climbs
for the description (same ramp, same 3 m/s at the mark): solid cylinder (k = 0.5000): rises 68.83 cm (closed form 68.83), 1.5000 times the cube, tops out 1.4388 s after the mark, needs friction 0.1213 of the normal force; hollow ball (k = 0.6667): rises 76.48 cm (closed form 76.48), 1.6667 times the cube, tops out 1.5879 s after the mark, needs friction 0.1456 of the normal force; hoop (k = 1.0000): rises 91.77 cm (closed form 91.77), 2.0000 times the cube, tops out 1.8860 s after the mark, needs friction 0.1820 of the normal force; the same rolling ball meeting an ice slope (no friction from the foot on, no torque about its centre): its centre rises 45.89 cm, like the cube, tops out 0.9916 s after the mark and is still spinning at 50.0 rad/s (7.96 turns a second) at the top: its 2/7 of spin energy stays in the spin
check at half the time step (24000 steps per second): cube rises 45.887230 cm (+3.7e-11), top at 0.991624 s (+4.1e-13), back at 1.983248 s (+8.2e-13); ball rises 64.242121 cm (-2.1e-11), top at 1.349388 s (-3.5e-13), back at 2.698776 s (-6.9e-13)
schedule (video time, 1/3 speed): cycles of 10 s start at -0.70, 9.30, 19.30, 29.30, 39.30 s (the first 0.70 s before the first frame); both objects come in from the left edge 0.48 and 0.46 s before they cross the mark, 0.8 s into each cycle at 0.10, 10.10, 20.10, 30.10 s; the cube tops out at 3.07, 13.07, 23.07, 33.07 s and the ball at 4.15, 14.15, 24.15, 34.15 s; the cube is back at the mark at 6.05, 16.05, 26.05, 36.05 s and off the frame at 6.53, 16.53, 26.53, 36.53 s, the ball back at the mark at 8.20, 18.20, 28.20, 38.20 s and off at 8.66, 18.66, 28.66, 38.66 s; the peak marks fade over the last 0.6 s of each cycle (from 8.70, 18.70, 28.70, 38.70 s); on the first frame the cycle is 0.70 s in (-0.033 s real after the mark: both centres 10.0 cm before the mark); title until 3 s; payoff card from 24.4 s; the title fades back in over the last 0.5 s and the last frame repeats the first (the scene is periodic: 40 s holds exactly 4 cycles)
text widths: overlay@34 857 px, title line 1@56 654 px, title line 2@56 515 px, legend@40 801 px, clock@28 440 px, clock rest@28 341 px, label cube@40 186 px, sublabel cube@28 379 px, fixed cube@28 397 px, readout cube@40 294 px, speed cube@28 239 px, spin cube@28 115 px, peak cube@40 135 px, label ball@40 83 px, sublabel ball@28 350 px, fixed ball@28 397 px, readout ball@40 294 px, speed ball@28 239 px, spin ball@28 246 px, peak ball@40 135 px, cross mark@28 235 px, mark@24 73 px, payoff line 1@40 842 px, payoff line 2@40 855 px, payoff line 3@40 824 px, payoff line 4@40 826 px, payoff line 5@40 831 px, payoff line 6@40 913 px
row check: the left column ends at x 437 px, the right column starts at x 746 px; both end 136 px under the band top; the ramp surface at x 1040 px is 218 px under the band top and the ball's top edge at its peak 210 px
peak marks: cube peak line from x 470 to 700 px at 303 px under the band top (39 px above the ramp at its right end), label x 323 to 458 px (107 px above the ramp); ball peak line from x 671 to 901 px at 233 px under the band top (35 px above the ramp at its right end), label x 524 to 659 px (104 px above the ramp); cube level in the ball panel line from x 480 to 710 px at 303 px under the band top (35 px above the ramp at its right end), label x 233 to 468 px (103 px above the ramp)
Tue Sep 29 10:40:26 AM EEST 2026
```

Earlier measure runs, not kept (the rises matched the closed forms in
every run): the first runs drew a 10 cm cube and a 5 cm ball; the
objects grew to 12 cm and 6 cm so that both show 46 px across (the
rises do not change; the times on the offset path moved a little with
the offset). One run had an energy drift of 5.6e-9 and 1.2e-8 of the
starting kinetic energy, over the brief's 1e-9, because RK4 steps
crossed the curvature jumps at the two ends of the fillet; the step now
splits at those points (drift 2.5e-13 and 3.2e-13, the rise diff down
from 5e-8 to 1.1e-11 cm). Two runs failed the width assert: the legend
"same speed at the mark, same slope, 1/3 speed" was 1079 px (now "same
speed, same slope, 1/3 speed", 801 px), and card line 4 was 1065 px
(now "top at 1.35 s (ball) and 0.99 s (cube)", 826 px). payoff_t went
from 26.0 to 24.4 after the voice timing.

The brief's checks against the log: cube 45.89 cm (log 45.89), 134.17
cm along a plain slope (134.17); ball 64.24 cm (64.24), 187.83 cm
(187.83); 7/5 = 1.4000 (1.4000); plain-slope tops 0.8944 and 1.2522 s
after the foot (0.8944 and 1.2522; with the fillet 0.9083 and 1.2661 s
after the foot, 0.9916 and 1.3494 s after the mark); rolling needs mu
0.104 or more ((2/7) tan 20 = 0.1040 on the straight slope, 0.0209 at
most on the fillet, under 0.6 everywhere); normal force positive (0.940
to 4.824 weights); spin 2/7 of the energy (0.2857); cylinder 1.5x 68.83
cm (1.5000, 68.83), hollow ball 1.667x 76.48 cm (1.6667, 76.48), hoop
2x 91.77 cm (2.0000, 91.77); the rolling ball on an ice slope stops at
45.9 cm still spinning (45.89 cm, 50.0 rad/s); energy within 1e-9
(2.5e-13 and 3.2e-13); RK4 at 6,000 steps a second or finer (12,000,
half-step check at 24,000). No check failed.

### Production

- Sim: sims/uphill/uphill.py with projects/uphill/manifest.json (seed 0,
  fps 60, g 9.80665, v0 3.0 m/s, slope 20 degrees, fillet 0.3 m, flat to
  foot 0.25 m, cube side 0.12 m, ball radius 0.06 m, k 0.4, mu_grip 0.6,
  description shapes cylinder 0.5, hollow ball 2/3, hoop 1.0,
  steps_per_second 12000, sim_end_s 4.0, slow 3, cycle_s 10.0, cross_at
  0.8, first_cycle_at -0.7, reset_fade 0.6, scene_duration 40.0,
  px_per_m 380, mark_x_px 150, title_until 3.0, payoff_t 24.4,
  payoff_hold 0.6, loop_fade 0.5, music_seed 96, music_gain 0.18,
  voice_offset 0.6, caption_y 0.75). RK4 on (s, s') along the centre's
  offset curve with (1 + k) s'' = -g sin alpha(s); each step splits at
  the two ends of the fillet so no step crosses a curvature jump; the
  top (s' = 0) and the return to the mark by 60 bisections inside the
  step; checked against the closed form (1 + k) v0^2 / 2 g, the energy
  (1 / 2)(1 + k) v^2 + g y_c and a half-step rerun; forces from the
  states (N / m g = cos alpha + v^2 kappa / g, f / m g = sin alpha k /
  (1 + k)); the ball spins at v / r and its stripe turns by s / r.
  Frames are drawn from the frame integer modulo the 600-frame cycle,
  so the scene is exactly periodic; the last frame is the live frame 0.
- Layout (1080x1920): overlay "3 m/s | 20 degree slope | 1/3 speed | no
  seed" at y 96 (34 px teal, drawn by compose); title two rows at y 190,
  252 (56 px) until 3 s, then the legend "same speed, same slope, 1/3
  speed" at y 236 (40 px) and the shared clock "N.NNN s after the start
  mark" at y 290 (28 px); geometry layer y 330 to 1430 drawn at 2x and
  downsampled; ice band from y 330 with the flat at y 830, grippy band
  from y 880 with the flat at y 1380; the start mark at x 150 (gold
  notch, "3 m/s" under it); 380 px per metre; height ticks every 10 cm
  up to 70 cm; left column at x 40: label (40 px, panel colour),
  sublabel "slides on ice, no friction" / "rolls on a grippy ramp" (28
  px), fixed "top 0.99 s after the mark" / "top 1.35 s after the mark"
  (28 px gold, hud only); right column to x 1040: live "height NN cm"
  (40 px, gold at the top), "speed N.NN m/s" and "no spin" / "spin N.N
  turns/s" (28 px); a pale ice ramp with highlights and a dark grippy
  ramp with a speckle; the cube turned to the local slope; the ball
  coral with a white stripe and a dot; after each top a gold dashed
  peak line with "46 cm" / "64 cm" and a gold tick on the surface, kept
  until the reset fade; on the ball panel, after the cube's top, a teal
  dashed "ice cube 46 cm" line at the cube's height; captions at y 1440
  (64 px); the six-line gold card from y 1572 at a 48 px pitch.
- Hook pre-tests (media/uphill/hooks/pretest.log, 10:22:50 to 10:23:36
  EEST), each through scripts/voiceover.sh with the setup sentence, all
  seven passed on the first pass; question onset = the silence_end
  before the question plus 0.6 s, or the voice start plus 0.6 s when the
  question comes first: hook1 "Ice cube or ball. Which climbs higher?"
  2.04 s; hook2 "Ice cube or ball, which climbs higher?" 2.10 s; hook3
  "Same speed, same slope. Which climbs higher?" 2.26 s; hook4 "Which
  climbs higher, an ice cube or a ball?" 0.63 s (leading silence 0.034
  s); hook5 "An ice cube and a ball. Which climbs higher?" 2.17 s; hook6
  "Which climbs higher, ice cube or ball?" at the voice start; hook7 "Ice
  cube or ball? Which climbs higher?" 1.92 s. Kept hook6: the question
  comes first, with the brief's words and no articles.
- Narration: projects/uphill/narration.txt, 110 words, the question at
  words 1 to 7, identical in the title, the hook and the payoff ("So,
  once more, side by side. Which climbs higher, ice cube or ball? The
  ball climbs higher."); numbers as words ("three meters a second",
  "Sixty four centimeters", "forty six", "One point four times");
  American "meters", "centimeters".
- Voice (media/uphill/voice.log): pass 1 at 10:37:19 (93 words) and pass
  2 at 10:38:21 (95 words, "Watch where each one stops, then slides
  back down." and "So, once more, side by side." added) passed, but
  "Sixty four" came before the ball's top on the third run. Pass 3 at
  10:39:10 (107 words, "Watch the white stripe." added, closing line
  "The ice cube has no spin to spend.") failed: whisper heard "too" as
  "2" before "The ice cube". Pass 4 at 10:39:42 (110 words, "turns into
  height as well", the answer "The ball climbs higher."): "ok:
  transcript matches narration (35.514921s) -> media/uphill/voice.wav".
  The voice ends at 36.11 s of video.
- Timing (scripts/voice-timing.py media/uphill/voice.wav 0.6 in
  media/uphill/timing.log; sentence bounds from the pauses in
  media/uphill/silences.log, video time; word starts from whisper
  verbose_json in media/uphill/words.log, which run up to about 0.3 s
  early against the pauses): the question 0.60 to 2.85 s ("Which climbs
  higher," ends at 1.60 s); "Both hit the same slope at three meters a
  second." 3.13 to 5.49; "Watch where each one stops, then slides back
  down." 5.62 to 8.56; "On top, the ice cube slides with no grip, until
  its speed runs out." 8.76 to 12.97; "Below, the ball rolls on a grippy
  ramp." 13.23 to 15.50; "Watch the white stripe." 15.81 to 16.95; "It
  spins as it rolls." 17.13 to 18.34; "So, once more, side by side."
  18.54 to 20.60; "Which climbs higher, ice cube or ball?" 20.82 to
  23.42; "The ball climbs higher. Sixty four centimeters," 23.56 to 25.98
  ("Sixty four" at 24.78 by whisper); "against forty six." 26.23 to 27.30
  ("forty six" at 26.78); "One point four times as high." 27.45 to
  29.09; "As it climbs, the grip slows the spin," 29.35 to 31.70; "and
  its spin turns into height as well." 32.03 to 33.92; "The ice cube has
  no spin to spend." 34.19 to 36.11.
- Schedule: cycles of 10 s start at -0.7, 9.3, 19.3, 29.3 s; both cross
  the mark at 0.10, 10.10, 20.10, 30.10 s; the cube tops out at 3.07,
  13.07, 23.07, 33.07 s and the ball at 4.15, 14.15, 24.15, 34.15 s;
  the cube is off the frame at 6.53 s and the ball at 8.66 s (plus 10 k);
  the peak marks fade from 8.70 s (plus 10 k). The ball's climb from the
  foot plays over 3.80 s (4.05 s from the mark). Sync: the first run
  plays under the question and the setup; the second run under "the ice
  cube slides with no grip, until its speed runs out" (cube top 13.07)
  and "Below, the ball rolls ... Watch the white stripe" (ball top
  14.15); the third run under the repeated question; the cube tops at
  23.07 and the ball at 24.15 while "The ball climbs higher" is spoken
  (from 23.56), then "Sixty four" (24.78) with the gold "64 cm" on,
  "forty six" (26.78) with the gold "46 cm" and the teal "ice cube 46
  cm" line on, "One point four times" (27.45); the card (payoff_t 24.4,
  lit at 25.0) stays to the end; the fourth run plays under "As it
  climbs, the grip slows the spin, and its spin turns into height as
  well" (29.35 to 33.92), and "The ice cube has no spin to spend"
  starts at 34.19, just after the cube's top at 33.07.
- Smoke frames (--frames): 19 PNGs at 0.0, 1.5, 3.2, 4.3, 7.0, 9.1,
  9.8, 12.5, 16.5, 23.5, 24.8, 26.8, 27.0, 28.9, 31.0, 34.2, 35.0, 39.6,
  39.98 s (media/uphill/smoke-*.png), used to check the layout, the peak
  marks and the card before the render.
- Footage: render 10:40:46 to 10:41:16 (media/uphill/render.log): loop
  check 0 px, periodicity check 0 px, loop step 3139 px (the seam is in
  motion: on frame 0 both objects are on the flat 10 cm before the
  mark); media/uphill/footage.mp4 2400 frames.
- Compose: scripts/compose.sh 10:41:22 to 10:41:37 (compose.log): music
  seed 96, 40.00 s; captions 36 chunks; final.mp4 40.000000 s; preview
  40.066667 s; sheet 8x5 at 1 fps.
- Text widths (PIL, from measure.log, all under 950 px): overlay 857,
  title 654 / 515, legend 801, clock 440 / 341, label cube 186, sublabel
  cube 379, fixed cube 397, readout cube 294, speed cube 239, spin cube
  115, peak cube 135, label ball 83, sublabel ball 350, fixed ball 397,
  readout ball 294, speed ball 239, spin ball 246, peak ball 135, cross
  mark 235, mark 73, payoff 842 / 855 / 824 / 826 / 831 / 913.

### Local QA

- Frames extracted from media/uphill/final.mp4 (never edited) and viewed
  with the Read tool:
  - frame-0.00.png: overlay, two title rows ("Which climbs higher," /
    "ice cube or ball?"), both objects on the flat before the mark,
    labels and live readouts, no hud, no caption, no card. Clean.
  - frame-0.50.png: title up; both objects on the fillet at 4 cm (cube
    2.88 m/s, "no spin"; ball 2.91 m/s, "spin 7.7 turns/s"); no caption
    yet (the voice starts at 0.6 s).
  - frame-1.00.png: caption "Which climbs higher," at y 1440.
  - frame-4.20.png: legend and clock "1.367 s after the start mark",
    fixed lines "top 0.99 s" / "top 1.35 s after the mark"; the cube at
    38 cm sliding back under the gold "46 cm" mark; the ball at its top,
    "height 64 cm" in gold, 0.04 m/s, spin 0.1 turns/s, the gold "64
    cm" mark and the teal "ice cube 46 cm" line under it; caption "slope
    at three".
  - frame-12.90.png: the cube near its top on the second run.
  - frame-16.50.png: the cube leaving at the left edge; the ball at 39
    cm rolling back, spin 5.0 turns/s, both marks on; caption "Watch the
    white".
  - frame-23.50.png: caption "The ball climbs", the cube's "46 cm" mark
    and the teal line on, the ball still climbing.
  - frame-24.80.png: caption "Sixty four", the gold "64 cm" mark, the
    card fading in.
  - frame-26.80.png: both peak marks on, caption "One point four
    times", the card lit.
  - frame-27.50.png: the six card rows lit and inside the frame
    ("which climbs higher, ice cube or ball?" / "the ball, 64 cm
    against 46: 1.40 times" / "its spin, 2/7 of its energy, climbs too"
    / "top at 1.35 s (ball) and 0.99 s (cube)" / "rolling needs grip: mu
    0.104 or more" / "cylinder 1.5x, hollow ball 1.67x, hoop 2x");
    caption "One point four times"; the ball rolling back at 13 cm.
  - frame-32.90.png: caption "into height as well.".
  - frame-35.00.png: caption "The ice cube has no".
  - frame-39.98.png: title back, hud gone, the same picture as
    frame-0.00.
  - sheet.png (40 thumbnails at 1 fps): the title for the first 3 s,
    then the legend and clock; four runs; captions readable in every
    thumbnail from 1 to 36 s; the card from 25 s; no clipped text,
    nothing at the frame edge.
- Question: on screen from frame 0 in the title (654 / 515 px), spoken
  from 0.66 s (whisper; the voice starts at 0.60 s); "Which climbs
  higher," caption 0.600 to 1.569, "ice cube or ball?" 1.569 to 2.860.
- Captions: media/uphill/captions.filter, 36 chunks, 110 words, matches
  projects/uphill/narration.txt word for word (script check True),
  longest chunk 20 characters; "The ball climbs" 23.200 to 24.169,
  "higher." 24.169 to 24.492, "Sixty four" 24.492 to 25.138,
  "centimeters, against" 25.138 to 25.783, "forty six." 25.783 to
  26.429, "One point four times" 26.429 to 27.720, "as high." 27.720 to
  28.366.
- Bands: signalstats over all 2,400 footage frames: the caption band
  (rows 1440 to 1530) and the overlay band (rows 96 to 130) have YMAX
  28 in every frame (background only), so the sim draws nothing under
  the captions or the overlay.
- Loop: footage last frame equals the first (0 px). In final.mp4 frame
  2399 against frame 0: 20,810 px over 8 levels, 409 over 32, max 70,
  mean 0.46 (h264 quantisation, the same order as day 30); frame 2398
  against 2399: 20,195 over 8, 3,265 over 32, max 251 (one step of
  motion and the title fade); frame 0 against 1 for reference: 3,775
  over 8, 2,317 over 32, max 245.
- ffprobe: h264 1080x1920 yuv420p 60/1, 2400 frames; aac 22050 Hz mono;
  40.000000 s; 3,893,587 bytes; moov before mdat (faststart).
- md5sum media/uphill/final.mp4: deac70572fc74d22bf8a6c2557c0ec61
- Narrated numbers against measure.log: "three meters a second" (setup
  line, "both cross the start mark at 3 m/s"); "Sixty four centimeters"
  (ball line, rises 64.24 cm); "against forty six" (cube line, rises
  45.89 cm); "One point four times as high" (the two panels line,
  1.4000); "the grip slows the spin" (ball line, spin 50.0 rad/s to 0.0
  at the top); "its spin turns into height as well" (ball line, 0.2857
  of its energy is spin; the two panels line); "The ice cube has no spin
  to spend" (setup line, k = 0). Card: 64 / 46 cm, 1.40 (1.4000), 2/7
  (0.2857), 1.35 / 0.99 s (1.3494 / 0.9916), mu 0.104 (0.1040),
  cylinder 1.5x (1.5000), hollow ball 1.67x (1.6667), hoop 2x (2.0000).
- Metadata check: every number in the description read against
  media/uphill/measure.log after the final run (45.89 / 64.24 cm,
  1.4000, 18.35 cm, tops 0.9916 / 1.3494 s, 0.9083 / 1.2661 s, plain
  slope 0.8944 / 1.2522 s and 134.17 / 187.83 cm, back at 1.9832 /
  2.6988 s at 3.000000 m/s, friction 0.0977 weights, 0.1040 and 0.0209
  of the normal force, normal force 0.940 to 4.824 weights, spin 50.0
  rad/s to 0.0, 0.2857, cylinder 68.83 cm / 1.5000 / 0.1213, hollow
  ball 76.48 cm / 1.6667 / 0.1456, hoop 91.77 cm / 2.0000 / 0.1820, the
  ball on ice 45.89 cm at 50.0 rad/s / 7.96 turns a second, drift
  2.5e-13 / 3.2e-13, closed-form diff 1.1e-11 cm, half step 4.1e-13 /
  3.5e-13 s).

### Metadata

projects/uphill/metadata.json: title "Which climbs higher, ice cube or
ball? The ball, 64 cm against 46, 1.4 times as high" (84 characters, no
angle brackets); description 2,973 characters with the model (it says
"slides with no friction" and "rolls without slipping"), the "Measured:"
list, the "Why:" paragraph, the rerun line and the AI-made line; 11
tags (ice cube or ball, which climbs higher, rolling ball, rolling
without slipping, frictionless slide, moment of inertia, rotational
energy, physics, physics visualization, simulation, shorts); categoryId
27; privacyStatus private; containsSyntheticMedia true;
selfDeclaredMadeForKids false.

### Deviations from the brief

- Hook "Which climbs higher, ice cube or ball?" instead of "Ice cube or
  ball. Which climbs higher?": the pre-test put the brief's wording at
  2.04 s (over two seconds); the kept hook starts with the question (no
  words before it). The title, the hook and the payoff carry the same
  question, and the answer uses its words ("The ball climbs higher.").
- Object sizes 12 cm cube and 6 cm radius ball instead of about 4 cm
  and 3 cm, so both show at 380 px per metre (46 px across) and both
  centres ride the same offset path, 6 cm above the surface (fillet
  offset radius 0.24 m). The rises do not depend on the size.
- The cube is a point on the offset curve with k = 0, drawn turned to
  the local slope; the small turn it makes on the fillet carries no
  energy in the model.
- The times include the 0.3 m fillet: the tops come 0.9083 and 1.2661 s
  after the foot of the fillet (0.9916 and 1.3494 s after the mark)
  against the brief's plain-slope 0.894 and 1.252 s; the log prints
  both, and the fixed lines, the card and the description use the times
  after the mark.
- No V valley: the objects run back off the left edge and the peak marks
  fade over the last 0.6 s of each 10 s cycle, so both panels share one
  clock (the V-valley periods 3.91 and 5.34 s differ).
- The loop seam is in motion: frame 0 shows both objects on the flat 10
  cm before the mark with the title; the last frame repeats it, so the
  motion holds for one frame at the loop point.
- Payoff "its spin turns into height as well" instead of "too": whisper
  heard "too" as "2" (pass 3).
- Sync on the first two runs: "Both hit the same slope at three meters
  a second" (3.13 to 5.49 s) plays while both climb and top out (3.07,
  4.15 s), and "Watch where each one stops, then slides back down" (5.62
  to 8.56 s) comes after both tops, while both slide back with the peak
  marks on; "On top, the ice cube slides with no grip" starts at 8.76 s,
  before the cube comes back in at 9.62 s; "It spins as it rolls" (17.13
  to 18.34 s) plays while the ball rolls back down.
- The spin readout shows the size of the spin (turns a second), also on
  the way down, when the ball turns the other way.
- Captions use word-proportional timing: the payoff captions lead the
  speech by up to about 1.0 s ("forty six." caption 25.783 s, spoken
  26.78 s by whisper) and the repeated question lags by up to about 0.4
  s (caption 20.940 s, spoken from 20.57 to 20.82 s).
- mu_grip 0.6 is a chosen value (the brief asks only for 0.104 or
  more); the description says so.

## Niche note

[produced 2026-09-29 as "Which climbs higher, ice cube or ball? The
ball, 64 cm against 46, 1.4 times as high"; measured the ice cube's
centre rising 45.89 cm against the rolling ball's 64.24 cm at 3 m/s on
a 20 degree slope, ratio 1.4000; tops 0.9916 and 1.3494 s after the
mark; rolling needs friction 0.1040 of the normal force; cylinder 68.83
cm (1.5x), hollow ball 76.48 cm (1.667x), hoop 91.77 cm (2x); ball on an
ice slope 45.89 cm still spinning at 50 rad/s; RK4 at 12,000 steps a
second, energy within 3.2e-13; task 20260929-101915]

## Upload

- orchestrator review (2026-09-29T11:18:37+03:00): task evidence, sheet.png and frames at
  0.00 and 26.80 s inspected; numbers match measure.log and the closed
  forms in /tmp/day31/check.py ((1 + k) v^2 / 2g = 45.89 and 64.24 cm,
  (k / (1 + k)) tan 20 = 0.1040); approved for upload
- upload attempt 2 of 5 for the quota day that began 2026-09-29T10:00
  EEST, recorded at 2026-09-29T11:18:37+03:00 before starting scripts/yt-upload.py; one
  attempt (swerve, published as MFVd3MiPsUI) was on record since the
  boundary
- uploaded private as rLaOH8SOh4U at 2026-09-29T11:18:42+03:00
  (https://youtu.be/rLaOH8SOh4U); channels.list 1 unit + videos.insert
  1,600 units; media/uphill/upload.log
- scripts/yt-qa.py uphill rLaOH8SOh4U --wait --publish in the foreground:
  gate 15 of 15 on the first read (processed, succeeded, hd, 1080x1920,
  title, description and tags match, category 27, not made for kids,
  PT41S for the 40.000 s file, private before publish); published at
  2026-09-29T11:19:21+03:00; re-read privacyStatus=public; yt-qa quota
  54 units; media/uphill/publish.log
- attempt 2 of 5 complete: 1,655 units; slot 2 of 3 resolved as
  published

### Quota
- attempt 2 of the hard cap of 5 for the quota day that began
  2026-09-29T10:00 EEST; cost 1,655 units (the channels.list verification
  inside yt-upload.py, the 1,600-unit insert, and the gate run's reads,
  update and re-read as printed by yt-qa.py); day total after three
  attempts 1,655 + 1,655 + 1,654 = 4,964 units plus 5 for the 10:01
  stats refresh and 5 for the 11:21 refresh, 4,974 of 10,000 used,
  5,026 remaining; target of three met
