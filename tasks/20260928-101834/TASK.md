# Produce short: Pendulum and peg, a peg halfway down the string beside a peg seventy percent down

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day30

## Goal

Backlog idea (trend research 2026-09-27, task 20260927-102520, pillar 2
chaos and physics, strings; read the full entry under "Added by trend
research 2026-09-27" in docs/niche.md):
"Pendulum and peg: a 1 m pendulum released from horizontal with a peg
halfway down the string beside a peg 70 percent down; measure whether
the bob loops the peg; expect the halfway string to go slack 41.8
degrees above the peg (48.2 short of the top) at 1.81 m/s, the bob to
fly 0.55 s and be caught 35 degrees from the bottom on the far side
keeping 10 percent of its energy, and the 70 percent peg to loop at
2.80 m/s over the top (needs 1.72) with 1.67 weights of tension, lap
0.528 s; the peg must be at least 3/5 down (5 d = 3 L; slack angle
asin(2 d / 3 r)); RK4 with a slack event and a parabola; the looping
panel is periodic; deterministic, no seed."

Orchestrator notes (2026-09-28, before this brief). The model: a bob (a
point mass) on a massless string of length L = 1.0 m from a fixed
pivot, released from rest with the string horizontal (the bob level
with the pivot, on the left). A thin peg (zero radius in the
kinematics; draw a small dot and say "a thin peg") is fixed on the
vertical below the pivot at distance d. The bob swings down as a
pendulum (theta'' = -(g / L) sin theta, RK4, checked against v^2 = 2 g
L (1 - cos theta) from the horizontal; at the bottom v0 = sqrt(2 g L) =
4.429 m/s). When the string passes the vertical it catches the peg and
the bob continues on a circle of radius r = L - d about the peg with the
same speed (the velocity is tangent to both circles at the bottom, so
the catch loses nothing; print that check). On the small circle, with
psi the angle from the bottom about the peg, v^2 = 2 g L - 2 g r (1 -
cos psi) and the tension per unit mass is T = v^2 / r + g cos psi. The
bob loops the peg when the string is still taut at the top, v_top^2 >=
g r, that is 2 L - 4 r >= r, r <= 2 L / 5, d >= 3 L / 5: the peg must
be at least three fifths of the way down. Panel A, d = 0.5 L (r = 0.5
m): T reaches 0 at cos psi = -2 (L - r) / (3 r) = -2/3, psi = 131.8
degrees from the bottom, 48.2 degrees short of the top, 41.8 degrees
above the peg's level, at v = sqrt(g L / 3) = 1.808 m/s, 0.333 m above
the peg on the far side. The string goes slack and the bob flies as a
projectile. Event handling for the flight, in two regimes: while the
bob is on the far side of the vertical through the peg (x > 0) the
string is wrapped round the peg and snaps taut again if the bob's
distance from the peg returns to r; once the bob has crossed to the
near side (x < 0) the string has unwrapped and runs straight from the
pivot, so it snaps taut when the bob's distance from the pivot reaches
L. Orchestrator integration (checks, not facts): the bob peaks 0.426 m
above the peg, crosses the vertical after 0.309 s of flight at 0.281 m
above the peg (inside the small circle, so the string is slack there),
and is caught 0.561 s after the slack on the near side by the straight
string, 17.7 degrees from the bottom about the pivot, moving at 4.32
m/s almost straight along the string; the jerk kills the radial
component (4.32 m/s) and keeps the tangential 0.11 m/s, 0.1 percent of
the bottom kinetic energy: the ball drops nearly dead on the string and
then hangs. The research's "35 degrees on the far side keeping 10
percent" used the wrong catch circle; measure and print what the sim
gets. After the catch let the bob swing as a pendulum from the pivot
until the panel resets. Panel B, d = 0.7 L (r = 0.3 m): v_top^2 = 2 g L
- 4 g r = 7.848, v_top = 2.801 m/s (needs sqrt(g r) = 1.716), tension
at the top 1.67 weights, the lap round the peg 0.528 s (quadrature of r
ds / v); with a zero-radius peg every lap is identical, so the looping
panel is exactly periodic. Print, per panel: the bottom speed, the slack
angle and speed (A), the flight time, peak and catch (A), the energy
kept at the catch (A), the top speed and tension (B), the lap time (B),
the threshold d = 3 L / 5 with the d just below and just above it (0.59
and 0.61 L: print whether each loops), and for the description the same
outcome at d = 0.6 L (the exact threshold: the string just reaches the
top with zero tension).

State every derived number above as a check the sim must print, not as
a fact.

Drawing: two panels stacked, the same pivot height and scale, the same
clock; the string as a line, the peg as a small dot with a short label
("peg halfway", "peg 70 % down"), the bob a bright disc with a trail;
the small circle about the peg as a faint ghost ring so the viewer can
see the ball leave it (A) or ride it (B); a live tension readout in
weights on each panel (turns red and reads 0.00 at the slack); real
time or mild slow motion (the swing from horizontal to the bottom takes
0.60 s; a 2x slow motion reads well); repeat the release so the short
loops (fade and reset as cueball and tablecloth do, or a cycle length
that divides the scene); several cycles in about 40 s; the last frame
equals the first.

Day thirty, second slot. Chosen because "will it swing round the peg?"
is a does-it question with a visible yes and no on the same swing, the
threshold is an exact fraction a closed form checks, and no seed. The
48.2 degrees is the loop-the-loop slack angle again (looptrack,
2026-09-20), so the payoff here is the threshold, not the slack angle:
the peg must be at least three fifths of the way down. Question in the
first two seconds: "Will the ball swing round the peg?" (or the
producer's better wording; keep the words before the question under
nine; keep the question identical in the title, the hook and the
payoff). Setup number: one meter string, let go level with the pivot
(or "peg halfway down" as the panel label; pick one for the narration).
Payoff: halfway down, no, the string goes slack and the ball drops;
seventy percent down, yes; the peg must be at least three fifths of the
way down. The 48 degrees, 1.8 m/s, 2.8 m/s, 1.67 weights and 0.528 s
go to the card and the description. Whisper risks: "peg" may come back
as "pig" or "pack", "bob" as "Bob", "loop" as "look"; say "ball" not
"bob", pre-test the hooks with scripts/voiceover.sh, and keep the one
whose question lands earliest under two seconds. Make the last frame
equal the first. Measure every fixed text line with PIL before rendering
and keep every line under 950 px, and the title under 100 characters
with no < or >. Music seed 93. Templates: sims/looptrack (slack event
and parabola with a tension readout), sims/tarzan (pendulum RK4 with a
release into flight), sims/tetherball (a string that shortens),
sims/tablecloth (two panels on one clock, cycles, reset fade). Sim name
pegswing: sims/pegswing/pegswing.py, projects/pegswing/, media/pegswing/.

## Claim

A ball on a 1 m string let go level with the pivot swings round a thin
peg only if the peg sits at least three fifths of the way down the
string (d >= 3 L / 5, r <= 2 L / 5; the string is taut at the top only
if v_top^2 = 2 g L - 4 g r >= g r). Peg halfway down (r = 0.5 m): the
string pull reaches zero 48.19 degrees short of the top (131.81 degrees
from the bottom about the peg, 41.81 above the peg's level) at 1.8080
m/s, 0.3487 s after the catch; the ball flies 0.5608 s, peaks 0.4259 m
above the peg, crosses the vertical 0.2813 m above it (inside the 0.5 m
circle) and drops onto the straight string from the pivot 17.65 degrees
from the bottom on the near side at 4.3232 m/s; the jerk kills 4.3218
m/s radial and keeps 0.1104 m/s tangential, 0.062 percent of the bottom
kinetic energy, and the ball swings low. Peg 70 percent down (r = 0.3
m): over the top at 2.8009 m/s (needs 1.7152) with 1.6667 weights of
pull, lap 0.5283 s, every lap identical. Peg 0.59 L: slack 16.39
degrees short of the top; 0.60 L: the top with zero pull; 0.61 L: loops
at 2.0772 m/s with 0.1282 weights. Narrated: same ball, same string,
let go level with the pivot, peg halfway down and peg seventy percent
down (setup); halfway down no, seventy percent down yes, the peg must
sit at least three fifths of the way down (payoff). Card: slack 48
degrees short of the top, flies off at 1.8 m/s, 2.8 m/s over the top,
1.67 weights at the top, one lap 0.528 s, the peg must be at least 3/5
down. Description: the threshold with 0.59, 0.60 and 0.61 L, the
flight numbers and the energy kept at the catch.

## Evidence

### Measurements

`nix develop -c python3 sims/pegswing/pegswing.py projects/pegswing/manifest.json --measure-only`
at 10:46 EEST (first_cycle_at -2.55), media/pegswing/measure.log,
copied whole:

```
setup: a ball (a point mass) on a massless string of L = 1 m from a fixed pivot, let go from rest with the string horizontal (the ball level with the pivot, on the left); a thin peg (zero radius) fixed on the vertical below the pivot at d = 0.5 L (upper panel, r = L - d = 0.50 m) and d = 0.7 L (lower panel, r = 0.30 m); g = 9.80665 m/s^2; RK4 at 20000 steps per second (dt = 5e-05 s) with the catch, the slack, the crossing of the vertical, the re-catch, the top and the laps located by bisection inside the step; shown at 1/2.5 speed on a 8.8 s cycle (528 frames) with the release 0.3 s into the cycle, 5 cycles in 44 s; drawn at 400 px per metre; deterministic, no seed
closed forms: bottom speed sqrt(2 g L) = 4.4287 m/s; time from the horizontal to the bottom sqrt(L / g) K(sin 45 deg) = 0.5921 s; on the small circle v^2 = 2 g L - 2 g r (1 - cos psi) and T = v^2 / r + g cos psi; the string is taut at the top only if v_top^2 = 2 g L - 4 g r >= g r, i.e. r <= 2 L / 5, d >= 3 L / 5 = 0.60 m; T at the top = 2 L / r - 5 weights; where the pull reaches zero cos psi = -2 (L - r) / (3 r) and v^2 = 2 g (L - r) / 3
upper panel (d = 0.5 m, r = 0.5 m): the ball reaches the bottom at 0.5921 s (closed form 0.5921 s, diff 2.0e-15 s) at 4.4287 m/s (closed form 4.4287, diff 1.6e-14); the string passes the vertical and catches the peg: the velocity is 0.0 degrees from horizontal, tangent to both circles, so the speed is 4.4287 m/s on both sides and the catch loses nothing; the pull jumps from 3.0000 weights (v^2 / L + g) to 5.0000 weights (v^2 / r + g); RK4 pull stays within 3.5e-14 weights of the energy closed form over 18817 samples up to 0.941 s
upper panel, slack: the pull reaches 0 at 0.9408 s (0.3487 s after the catch; quadrature of r dpsi / v 0.3487 s) at psi = 131.81 degrees from the bottom about the peg = 48.19 degrees short of the top = 41.81 degrees above the peg's level (closed form 131.81, 48.19 short, 41.81 above), at 1.8080 m/s (closed form sqrt(2 g (L - r) / 3) = 1.8080), 0.3333 m above the peg (closed form 0.3333) and 0.3727 m to the far side; the pull there -9.1e-17 weights; the string goes slack and the ball flies with velocity (-1.2053, 1.3476) m/s
upper panel, flight: the ball peaks 0.4259 m above the peg (closed form 0.4259) at x = 0.2070 m, 0.1374 s after the slack; it crosses the vertical 0.3092 s after the slack (closed form 0.3092) at 0.2813 m above the peg (closed form 0.2813), 0.2813 m from the peg against r = 0.5 m, so inside the small circle: the string round the peg never came taut on the far side; from here the string has slipped off the peg and runs straight from the pivot (0.2187 m from it against L = 1); it comes taut 0.5608 s after the slack (closed form 0.5608, diff 1.1e-16 s) at 1.5016 s, on the near side 17.65 degrees from the bottom about the pivot, at (-0.3032, -0.9529) m, moving at 4.3232 m/s 73.8 degrees below horizontal, almost straight along the string: the jerk kills the radial part 4.3218 m/s and keeps the tangential 0.1104 m/s, 0.062 percent of the bottom kinetic energy (0.06 %); afterwards the ball swings between 17.8 degrees left of the bottom about the pivot and 25.2 degrees right about the peg, until the panel resets
lower panel (d = 0.7 m, r = 0.3 m): the ball reaches the bottom at 0.5921 s (closed form 0.5921 s, diff 2.0e-15 s) at 4.4287 m/s (closed form 4.4287, diff 1.6e-14); the string passes the vertical and catches the peg: the velocity is 0.0 degrees from horizontal, tangent to both circles, so the speed is 4.4287 m/s on both sides and the catch loses nothing; the pull jumps from 3.0000 weights (v^2 / L + g) to 7.6667 weights (v^2 / r + g); RK4 pull stays within 7.6e-14 weights of the energy closed form over 43537 samples up to 2.177 s
lower panel, loop: the ball passes the top at 0.8562 s (0.2641 s after the catch; quadrature 0.2641 s) at 2.8009 m/s (closed form sqrt(2 g L - 4 g r) = 2.8009; it needs sqrt(g r) = 1.7152) with the pull 1.6667 weights (closed form 2 L / r - 5 = 1.6667), the minimum over the laps 1.6667 weights, so the string stays taut and the ball LOOPS THE PEG; laps round the peg take 0.5283, 0.5283, 0.5283, 0.5283 s (spread 9.2e-14 s; quadrature of r dpsi / v over 2 pi 0.5283 s): every lap is the same, the panel is periodic; 6 laps done by 3.762 s, 6 in the 4 s run
threshold: the peg must be at least 3 L / 5 = 0.60 m down the string (r <= 2 L / 5 = 0.40 m); d = 0.59 L: does NOT loop, the pull reaches 0 at 163.61 degrees from the bottom (16.39 short of the top; closed form 16.39), v_top^2 would be 3.5304 against the g r = 4.0207 needed, T at the top would be -0.1220 weights; d = 0.6 L: LOOPS, passes the top at 1.9806 m/s (needs 1.9806) with the pull 4.34e-09 weights (closed form 2 L / r - 5 = 0.0000); the exact threshold: the string just reaches the top with zero pull; d = 0.61 L: LOOPS, passes the top at 2.0772 m/s (needs 1.9557) with the pull 1.28e-01 weights (closed form 2 L / r - 5 = 0.1282)
schedule (video time, 1/2.5 speed): cycles of 8.8 s start at -2.55, 6.25, 15.05, 23.85, 32.65, 41.45 s (the first 2.55 s before the first frame); the release 0.3 s into each cycle at 6.55, 15.35, 24.15, 32.95, 41.75 s; both balls reach the bottom and catch the peg 1.48 s after the release at 8.03, 16.83, 25.63, 34.43, 43.23 s; the upper string goes slack 2.35 s after the release at 0.10, 8.90, 17.70, 26.50, 35.30 s, the upper ball peaks at 0.45, 9.25, 18.05, 26.85, 35.65 s, crosses the vertical at 0.87, 9.67, 18.47, 27.27, 36.07 s and is caught by the straight string 3.75 s after the release at 1.50, 10.30, 19.10, 27.90, 36.70 s; the lower ball passes the top at 1.21, 2.53, 3.85, 5.17, 8.69, 10.01, 11.33, 12.65, 13.97, 17.49, 18.81, 20.13, 21.45, 22.77, 26.29, 27.61, 28.93, 30.25, 31.57, 35.09, 36.41, 37.73, 39.05, 40.37, 43.89 s (lap 1.32 s of video); each cycle crossfades to the ball at rest over its last 0.6 s (8.20 to 8.80 s after the cycle start); on the first frame the cycle is 2.55 s in (0.900 s real after the release): the upper ball is round the peg at (0.421, -0.230) m, the lower ball round the peg at (-0.120, -0.425) m; title until 3 s; payoff card from 32.3 s; the title fades back in over the last 0.5 s and the last frame repeats the first (the scene is periodic: 44 s holds exactly 5 cycles)
text widths: overlay@34 817 px, title line 1@56 583 px, title line 2@56 480 px, legend@40 746 px, clock@28 598 px, clock rest@28 432 px, label upper@40 409 px, mark upper@32 459 px, label lower@40 343 px, mark lower@32 414 px, peg label@28 59 px, readout label@28 162 px, readout@48 349 px, readout slack@48 349 px, state 0@28 432 px, state 1@28 237 px, state 2@28 224 px, state 3@28 263 px, state 4@28 549 px, state lap@28 342 px, payoff line 1@40 766 px, payoff line 2@40 864 px, payoff line 3@40 917 px, payoff line 4@40 838 px, payoff line 5@40 902 px, payoff line 6@40 774 px
layout (panel px): pivot (540, 80), release point (140, 80), bottom of the swing (540, 480), the ghost rings' tops at y 80, the upper ball's flight peak at (623, 110); the label ends at x 469 and the mark starts at x 561 (both in rows 10..50); the readout ends at x 409 (rows 492..540) and the state word starts at x 471 (rows 502..530); the readout's top-right corner is 432 px from the pivot against the ball's 414
```

Earlier runs. The first measure run (before the narration) used
scene_duration 40 s with an 8.0 s cycle; every physics line (bottom,
catch, slack, flight, catch by the string, top, laps, threshold) was
identical to the log above, since the physics does not depend on the
schedule; it failed the text-width assert (payoff line 2 at 1000 px and
line 6 at 1024 px), so the card lines were shortened to "halfway: no,
slack 48 deg short of the top" and "the peg must be at least 3/5 down".
Two layout asserts then fired and the layout was changed, not the
numbers: "the flight peak touches the mark" (the mark row at 74 px met
the ghost ring's top and the flight peak), fixed by moving the panel
label to the top-left and the mark to the top-right at row 30; and
"the ball at the bottom touches the rows" (readout row 492 against the
ball's bottom at 494, x-separated), replaced by a state-word y check
and a readout x check (the readout ends at x 409, the ball's bottom is
at x 526 or more). The narration at 137 words ran 42.1 s, so the scene
grew to 44 s (5 cycles of 8.8 s) instead of cutting content. The 10:44
run (an earlier first_cycle_at, smoke frames at 7.5, 9.2, 11.2, 18.8,
19.6, 27.4, 34.5, 36.5, 37.0 s) put the slack later than the words;
first_cycle_at moved to -2.55 s so the slack lands at 17.70 s, and only
the schedule line changed.

### Production

- Sim: sims/pegswing/pegswing.py with projects/pegswing/manifest.json
  (seed 0 unused, fps 60, g 9.80665, string_m 1.0, peg_fractions [0.5,
  0.7], check_fractions [0.59, 0.6, 0.61], steps_per_second 20000,
  slack_tol_weights 1e-6, sim_end_s 4.0, slow 2.5, cycle_s 8.8,
  release_at 0.3, first_cycle_at -2.55, reset_fade 0.6, trail_s 0.3,
  scene_duration 44.0, px_per_m 400, pivot_dy 80, band_y [340, 880,
  1420], title_until 3.0, payoff_t 32.3, payoff_hold 0.6, loop_fade
  0.5, music_seed 93, music_gain 0.18, voice_offset 0.6, caption_y
  0.75). RK4 on theta'' = -(g / L) sin theta from the horizontal; at
  the vertical the string catches the peg and the state switches to a
  circle of radius r about the peg (same velocity, tangent to both
  circles); the pull T = v^2 / r + g cos psi in weights; when T reaches
  0 (bisection inside the step, 80 halvings) the ball flies as a
  projectile; on the far side (x > 0) the string is round the peg and
  would catch at distance r from the peg, on the near side (x < 0) it
  runs straight from the pivot and catches at distance L; the jerk
  kills the radial velocity and keeps the tangential; afterwards the
  ball swings from the pivot. The peg, slack, peak, cross, catch,
  unwrap, top and lap events are located by bisection and checked
  against the closed forms (elliptic quarter period, sqrt(2 g L), cos
  psi = -2 (L - r) / (3 r), 2 L / r - 5, Simpson quadrature of r dpsi
  / v). Each frame is the state at the frame's phase inside an 8.8 s
  cycle (528 frames), crossfaded to the ball at rest over the last 0.6
  s; 44 s is exactly 5 cycles, so the last frame is the live frame 0.
  No wall clock, no random draws; the seed sits in the manifest unused.
- Layout (1080x1920): overlay at y 96 (34 px teal, drawn by compose);
  title two rows at y 190 and 252 (56 px) until 3 s, then the legend
  "same ball, same swing, two pegs" at y 236 (40 px) and the clock "x.xx
  s after release, 2.5x slow motion" or "at rest, level with the pivot"
  at y 290 (28 px, drawn only after the title fades); geometry band y
  340 to 1420 drawn at 2x and downsampled, split into the upper panel
  (340 to 880, coral label "peg halfway down") and the lower panel (880
  to 1420, teal label "peg 70 % down"); in each panel the pivot sits at
  (540, 80) panel px with a mount bar and a faint level line to the
  release point (140, 80), 400 px per metre, the bottom of the swing at
  (540, 480); the peg a white dot with a dotted leader to "peg"; the
  small circle a faint ghost ring (coral upper, teal lower); the ball a
  gold disc (r 14 px) with a teal trail (0.3 s); the string white when
  taut and a coral sagging curve when slack; after the slack a gold arc
  from the top of the ring to the slack point, a gold ring at the slack
  point and a gold radius; after the first top a gold ring at the top.
  Panel label top-left at row 30 (40 px), event mark top-right at row
  30 (32 px gold: "slack 48 deg short of the top" / "over the top at
  2.8 m/s"); "string pull" at row 470 (28 px) and the number at row 516
  (48 px; muted at rest, coral at 0.00 while slack); state word
  bottom-right at row 516 (28 px: "at rest, level with the pivot",
  "swinging down", "round the peg" / "round the peg, lap n", coral
  "slack, flying free", gold "caught by the string, swinging low");
  captions at y 1440 (64 px); payoff card six gold 40 px rows from y
  1580, step 48.
- Hook pre-tests (media/pegswing/hooks/pretest.log, 10:35:22 to
  10:35:29 EEST), each through scripts/voiceover.sh, all five passed on
  the first pass; question onset = first silence_end (n=-35dB d=0.08)
  plus 0.6 s, or the leading silence_end (d=0.01) plus 0.6 s when the
  question comes first: hook1 "Will the ball swing round the peg? ..."
  0.66 s (leading silence 0.062 s); hook2 "Will the ball swing around
  the peg? ..." 0.67 s; hook3 "A peg below. Will the ball ..." 1.70 s;
  hook4 "Ball on a string. Will the ball ..." 1.82 s; hook5 "One
  string, one peg. Will the ball ..." 2.27 s. Kept hook1.
- Narration: projects/pegswing/narration.txt, 132 words, the question
  as words 1 to 7, identical in the title, the hook and the payoff;
  numbers as words; "ball" not "bob"; "seventy percent" (whisper writes
  70%, the round trip normalises it); no "loop" alone ("loops over the
  top" passed).
- Voice (media/pegswing/voice.log): pass 1 at 10:36:34 (137 words, the
  panel intros before the catch sentence) passed at 42.109 s, too long
  and the catch words 6 s from the catch; pass 2 at 10:43:45 (137
  words, the catch sentence moved before the panel intros) failed:
  whisper wrote "the" for "a" twice (tokens 93 and 101, "a lower peg, a
  tighter circle") and "beat" for "be at" (token 129); pass 3 at
  10:44:28 ("Lower peg, tighter circle, lower top, so the ball keeps
  more speed there." and "The peg must sit at least three fifths of the
  way down."): "ok: transcript matches narration (40.634921s) ->
  media/pegswing/voice.wav". The pass-3 header in voice.log says 133
  words; wc -w on the file says 132. The voice ends at 41.23 s of
  video.
- Timing (scripts/voice-timing.py media/pegswing/voice.wav 0.6, in
  media/pegswing/timing.log): 0.60 to 2.34 "Will the ball swing round
  the peg?"; 2.34 to 7.96 "Same ball, same string. Let go level with
  the pivot. At the bottom of the swing the string catches the peg.";
  7.96 to 16.43 "and the ball turns on a tight circle. Above, a thin
  peg halfway down the string. Below, a peg 70% down. With the peg
  halfway down,"; 16.43 to 18.48 "The string goes slack before the
  top."; 18.48 to 21.75 "The ball flies, drops onto the string and
  swings low."; 21.75 to 23.68 "With the peg 70% down,"; 23.68 to 25.08
  "the string stays tight,"; 25.08 to 26.72 "and the ball loops over
  the top,"; 26.72 to 28.89 "Again and again. Lower peg."; 28.89 to
  30.63 "Tighter circle, lower top."; 30.63 to 32.54 "so the ball keeps
  more speed there."; 32.54 to 34.71 "So will the ball swing round the
  peg?"; 34.71 to 35.74 "Halfway down."; 35.74 to 38.21 "No. 70% down,
  yes."; 38.21 to 41.23 "The peg must sit at least three-fifths of the
  way down." (the timing tool's own transcript writes "pig" twice; the
  round trip on the full take passed). Question onset on the full take:
  leading silence 0 to 0.060 s in the wav plus 0.6 = 0.66 s; first
  silence_end (d=0.08) 1.858 s is the pause after the question
  (media/pegswing/silences.log).
- Schedule (measure.log, video time at 1/2.5 speed): releases at 6.55,
  15.35, 24.15, 32.95, 41.75 s; peg catches 1.48 s later at 8.03,
  16.83, 25.63, 34.43, 43.23 s; the upper string slack at 0.10, 8.90,
  17.70, 26.50, 35.30 s; caught by the straight string at 1.50, 10.30,
  19.10, 27.90, 36.70 s; the lower ball over the top every 1.32 s
  (1.21, 2.53, ... 43.89 s). "catches the peg" ends at 7.96 as the
  catch lands at 8.03 with the readouts jumping to 5.00 and 7.67
  weights; "The string goes slack before the top." (16.43 to 18.48)
  holds the slack at 17.70 with the readout coral 0.00; "The ball
  flies, drops onto the string and swings low." (18.48 to 21.75) holds
  the flight (17.70 to 19.10), the catch at 19.10 and the low swing;
  "and the ball loops over the top, again and again" (25.08 to 28.89)
  holds the tops at 26.29, 27.61 and 28.93; the card (payoff_t 32.3,
  lit at 32.9) lights inside the repeated question (32.54 to 34.71) as
  the last full cycle releases at 32.95; "Halfway down. No." (34.71 to
  36.3) holds the slack at 35.30 and the flight; "70% down, yes."
  (36.3 to 38.21) holds the tops at 36.41 and 37.73; the final line
  (38.21 to 41.23) runs while the upper ball swings low on the string
  and the lower ball laps (39.05, 40.37).
- Smoke frames (--frames): a 10:44 batch at 7.5, 9.2, 11.2, 18.8,
  19.6, 27.4, 34.5, 36.5, 37.0 s found the clock crowding the title's
  second row on frame 0 (the clock now waits for the title to fade)
  and the slack string's sag bulging sideways on a near-vertical chord
  (the droop now hangs straight down); the 10:46 batch at 0.0, 2.0,
  8.03, 9.0, 10.0, 17.7, 18.3, 19.1, 20.5, 26.3, 32.9, 35.3, 36.0,
  37.7, 41.0, 43.5, 43.98 s, of which 0.0, 18.3, 20.5, 35.3 and 43.5
  were viewed: title without clock, the J-shaped coral droop, the gold
  "caught by the string, swinging low", the six-line card under the
  caption band, frame 43.98 identical to frame 0. Captions checked
  with captions.py chunks(): 41 chunks, longest 20 characters, the
  payoff chunks "Halfway down, no." / "Seventy percent" / "down, yes."
  / "The peg must sit at" / "least three fifths" / "of the way down."
- Footage: render 10:48:08 to 10:48:58 (media/pegswing/render.log):
  loop check 0 px (max channel difference 0), periodicity check 0 px,
  loop step 5,804 px; media/pegswing/footage.mp4 6,490,724 B, 2640
  frames.
- Compose: scripts/compose.sh 10:49:03 to 10:49:23 (compose.log): music
  seed 93, 44.00 s; captions.filter 42 drawtext (overlay plus 41
  chunks); final.mp4 44.000000 s; preview 44.066667 s; sheet 8x6 at 1
  fps.
- Text widths (PIL, from measure.log, all under 950 px): overlay 817,
  title 583 / 480, legend 746, clock 598, clock rest 432, label upper
  409, mark upper 459, label lower 343, mark lower 414, peg label 59,
  readout label 162, readout 349, readout slack 349, state words 432 /
  237 / 224 / 263 / 549, state lap 342, payoff 766 / 864 / 917 / 838 /
  902 / 774. Layout asserts (label against mark, mark row against the
  ring top and the flight peak, the swing against the readout corner,
  the ball at the bottom against the state word, readout against the
  state word, rows inside the panel) all passed.

### Local QA

- Frames extracted from media/pegswing/final.mp4 (never edited) and
  viewed with the Read tool:
  - frame-0.0.png: overlay, two title rows ("Will the ball swing" /
    "round the peg?"), no clock, both labels, the upper ball round the
    peg at 0.38 weights ("round the peg"), the lower ball round the peg
    at 1.92 weights ("round the peg, lap 1") with the gold top ring and
    "over the top at 2.8 m/s"; no caption, no card. Clean.
  - frame-1.5.png: title still up, caption "Will the ball swing" at y
    1440; the upper string slack at 0.10 s (coral droop, "slack 48 deg
    short of the top", coral "0.00 weights", "slack, flying free"); the
    lower ball on lap 2 at 3.45 weights.
  - frame-8.03.png: the catch: both balls at the bottom on the vertical
    string, 0.59 s after release, 5.00 and 7.67 weights, "round the
    peg" / "round the peg, lap 1", the trails on the swing; caption
    "swing the string".
  - frame-17.7.png: 0.94 s after release, the upper ball at the slack
    point on the ring at 0.01 weights (the last taut sample), the lower
    ball past the top on lap 1 at 2.60 weights; caption "down, the
    string".
  - frame-19.1.png: 1.50 s after release, the upper ball caught by the
    straight string at the bottom-left (0.00 weights, the last slack
    sample, the gold slack arc and ring on the far side); caption "the
    top."; the lower ball on lap 2.
  - frame-26.3.png: 0.86 s after release, the lower ball at the top
    inside the gold ring at 1.67 weights, "round the peg, lap 1"; the
    upper ball just before the slack at 0.87 weights; caption "and the
    ball loops".
  - frame-33.0.png: the card lit (six gold rows), both balls 0.02 s
    after release with "swinging down" and 0.01 weights; caption "So,
    will the ball". The card is on screen inside the spoken question.
  - frame-35.9.png: caption "Halfway down, no."; the upper ball flying
    at 1.18 s after release with the coral droop, coral "0.00 weights",
    "slack, flying free"; the lower ball at 6.61 weights on lap 2; the
    card lit.
  - frame-37.7.png: caption "The peg must sit at"; 1.90 s after release,
    the upper ball on the string at the bottom, 1.09 weights, gold
    "caught by the string, swinging low"; the lower ball at the top on
    lap 3 at 1.69 weights; the card lit. The yes and the no are on
    screen together during the payoff.
  - frame-43.983.png: title back, no clock, no caption, no card; the
    same picture as frame-0.0.png.
  - sheet.png (44 thumbnails at 1 fps): the title for the first 3 s,
    then the legend and clock; five releases; captions readable in
    every thumbnail from 1 to 41 s; the card from 33 s, fading in the
    last two; no clipped text, nothing at the frame edge.
- Question: on screen from frame 0 in the title (two rows, 583 / 480
  px), spoken from 0.66 s (caption "Will the ball swing" 0.600 to
  1.831, "round the peg?" from 1.831).
- Captions: media/pegswing/captions.filter, 41 chunks, 132 words,
  matches projects/pegswing/narration.txt word for word (script check:
  filter texts equal chunks() True, join equals the narration True),
  longest chunk 20 characters; "goes slack before" 18.15 to 19.07,
  "the top." 19.07 to 19.69, "The ball flies," 19.69 to 20.61, "and
  the ball loops" 25.84 to 27.07, "over the top, again" 27.07 to 28.31,
  "swing round the peg?" 34.16 to 35.39, "Halfway down, no." 35.39 to
  36.31, "Seventy percent" 36.31 to 36.92, "down, yes." 36.92 to 37.54,
  "least three fifths" 39.08 to 40.00, "of the way down." 40.00 to
  41.23.
- Bands: signalstats over all 2,640 footage frames: the caption band
  (rows 1440 to 1530) and the overlay band (rows 96 to 130) have YMAX
  28 in every frame (background only), so the sim draws nothing under
  the captions or the overlay.
- Loop: footage last frame equals the first (0 px, max channel
  difference 0). In final.mp4 frame 2639 against frame 0: 30,222 px
  over 8 levels, 910 over 32, max 76, mean 0.36 (h264 quantisation, the
  same order as days 28 and 29); loop step 5,988 px, so the seam is no
  larger than one frame of motion.
- ffprobe: h264 1080x1920 yuv420p 60/1, 2640 frames; aac 22050 Hz mono;
  44.000000 s; 6,532,841 bytes; moov before mdat (ftyp, moov at 32,
  free, mdat).
- md5sum media/pegswing/final.mp4: c9947d6be79b77bc4fa867692adce89b
- Narrated numbers against measure.log: "halfway down" (d = 0.5 L, r =
  0.50 m) and "seventy percent down" (d = 0.7 L, r = 0.30 m); "goes
  slack before the top" (the pull reaches 0 at 131.81 degrees, 48.19
  short of the top); "flies, drops onto the string, and swings low"
  (flight 0.5608 s, caught by the straight string 17.65 degrees from
  the bottom, 0.1104 m/s kept, then 17.8 / 25.2 degree swings); "stays
  tight, loops over the top, again and again" (pull 1.6667 weights at
  the top, the minimum, 6 laps by 3.762 s); "keeps more speed there"
  (2.8009 m/s at the lower top against 0 for r = L / 2); "three fifths"
  (3 L / 5 = 0.60 m; 0.59 L slack, 0.60 L zero pull at the top, 0.61 L
  loops). Marks "slack 48 deg short of the top" (48.19) and "over the
  top at 2.8 m/s" (2.8009); readouts 5.00 / 7.67 at the catch (5.0000
  / 7.6667), 0.00 at the slack, 1.67 at the top (1.6667). Card 48 deg
  (48.19), 1.8 m/s (1.8080), 2.8 m/s (2.8009), 1.67 weights (1.6667),
  0.528 s (0.5283), 3/5.
- Metadata check: every number in the description (0.5921, 4.4287,
  3.0000, 5.0000, 7.6667, 0.9408, 0.3487, 131.81, 48.19, 41.81, 1.8080,
  0.3333, 0.3727, 0.4259, 0.1374, 0.3092, 0.2813, 0.5608, 1.5016,
  17.65, 4.3232, 73.8, 4.3218, 0.1104, 0.062, 17.8, 25.2, 0.8562,
  0.2641, 2.8009, 1.7152, 1.6667, 0.5283, 9.2e-14, 163.61, 16.39,
  4.0207, 3.5304, 4.34e-09, 1.9806, 2.0772, 1.9557, 0.1282, 3.5e-14,
  7.6e-14, 2.0e-15) found in the 10:46 measure.log by a grep loop.

### Metadata

projects/pegswing/metadata.json: title "Will the ball swing round the
peg? Halfway down: no, slack 48 deg short. 70 % down: yes. Needs 3/5"
(98 characters, no angle brackets); description 4,912 characters after the orchestrator's angle-bracket correction (4,876 as produced) with
the model, the "Measured:" list, the "Why:" paragraph (energy sets the
speed, the peg sets the circle, taut at the top only if v_top^2 >= g
r, so r <= 2 L / 5), the rerun line and the AI-made line; 11 tags;
categoryId 27; privacyStatus private; containsSyntheticMedia true;
selfDeclaredMadeForKids false.

### Deviations from the brief

- Scene 44 s (5 cycles of 8.8 s) instead of about 40 s: the 132-word
  narration runs 40.63 s and ends at 41.23 s of video; 40 s would have
  cut the mechanism sentence.
- The hook is the bare question, no words before it (the brief allowed
  up to nine); question onset 0.66 s.
- Slow motion 2.5x, not 2x: the swing to the bottom takes 1.48 s of
  video and the flight 1.40 s, so the slack, the flight and the catch
  can each sit under their own words.
- "the string stays tight," (23.68 to 25.08) is spoken during the reset
  crossfade and the swing down of cycle 4 (release 24.15, catch 25.63);
  the loop lands on "loops over the top, again and again" (tops 26.29,
  27.61, 28.93).
- The final line's last 0.4 s (40.85 to 41.23) overlaps the crossfade
  to rest of cycle 5 (40.85 to 41.45); the card stays lit until the loop
  fade.
- The narration says "must sit at least three fifths of the way down";
  the card says "the peg must be at least 3/5 down" (whisper wrote
  "beat" for "be at" in pass 2).
- Panel labels "peg halfway down" / "peg 70 % down" instead of "peg
  halfway" / "peg 70 % down".
- The research's "caught 35 degrees from the bottom on the far side
  keeping 10 percent" is replaced by the measured catch: 17.65 degrees
  on the near side by the straight string, 0.062 percent kept (as the
  orchestrator's integration anticipated).
- The loop seam is mid-cycle (0.900 s real after the release, both
  balls round the peg), not at a reset: 44 s holds exactly 5 cycles so
  the last frame equals the first anyway.
- voice.log's pass-3 header says 133 words; the file has 132.

- Orchestrator correction before upload (2026-09-28 11:20): the description
  used ">=" and "<=" in two places, which scripts/yt-upload.py rejects
  (YouTube refuses angle brackets); replaced by "is at least" / "is at
  most" and "at least" / "at most". No number changed.

## Niche note

[produced 2026-09-28 as "Will the ball swing round the peg? Halfway
down: no, slack 48 deg short. 70 % down: yes. Needs 3/5"; measured, peg
halfway down (r = 0.5 m): the string pull reaches zero 48.19 degrees
short of the top at 1.8080 m/s, the ball flies 0.5608 s (peak 0.4259 m
above the peg, crosses the vertical 0.2813 m above it, inside the
circle) and drops onto the straight string 17.65 degrees from the bottom
on the near side at 4.3232 m/s keeping 0.1104 m/s, 0.062 percent of the
bottom energy (not the research's 35 degrees far side and 10 percent);
peg 70 percent down (r = 0.3 m): over the top at 2.8009 m/s (needs
1.7152), 1.6667 weights, lap 0.5283 s, periodic; threshold 3 L / 5:
0.59 L slack 16.39 degrees short, 0.60 L zero pull at the top, 0.61 L
loops at 2.0772 m/s; task 20260928-101834]

## Upload

- orchestrator review (2026-09-28T11:26:34+03:00): task evidence, sheet.png and the frames in
  /tmp/day30/review/pegswing inspected; readouts match measure.log and the
  RK4 check in /tmp/day30/check_peg2.py; description angle brackets replaced
  by words (see Metadata); approved for upload
- upload attempt 2 of 5 for the quota day that began 2026-09-28T10:00
  EEST, recorded at 2026-09-28T11:26:34+03:00 before starting scripts/yt-upload.py; one attempt
  (crash, published) was on record since the boundary
- uploaded private as ApHSHT_MgzU at 2026-09-28T11:26:42+03:00
  (https://youtu.be/ApHSHT_MgzU); channels.list 1 unit + videos.insert
  1,600 units; media/pegswing/upload.log
- scripts/yt-qa.py pegswing ApHSHT_MgzU --wait --publish in the foreground
  at 11:26:45: processed/succeeded on the first poll, gate 14 of 15, the
  one failure snippet.tags read back absent (title, description, category,
  PT45S, private all matched); publish refused; 2 units
- snippet re-read at 11:28:07 (1 unit, no update sent): tags still absent,
  title and description match; this is the 2026-09-18 read-back lag (tags
  absent for about six minutes after a fresh insert); gate to be re-run in
  the foreground after 11:33 rather than re-sending the snippet
- gate re-run in the foreground at 11:33:12 (6 min 30 s after the insert):
  tags present, gate 15 of 15; published at 2026-09-28T11:33:15+03:00;
  re-read privacyStatus=public; yt-qa quota 52 units;
  media/pegswing/publish.log
- attempt 2 of 5 complete at 2026-09-28T11:34:25+03:00: 1,656 units (1 + 1,600 + 2 + 1 + 52);
  slot 2 of 3 resolved as published; tag read-back lag absent at +0:03 and
  +1:25, present at +6:30, matching the 2026-09-18 record

### Quota
- attempt 2 of the hard cap of 5 for the quota day that began
  2026-09-28T10:00 EEST; cost 1 + 1,600 + 2 + 1 + 52 = 1,656 units (the
  channels.list verification inside yt-upload.py, the insert, the first gate
  run's two reads that found the tags absent, the 11:28 snippet re-read, and
  the second gate run's read, update and re-read as printed by yt-qa.py);
  day total after three attempts 1,655 + 1,656 + 1,655 = 4,966 units plus 5
  for the 10:05 stats refresh and 5 for the 11:35 refresh, target of three
  met

### Repository
- committed as 3a82f2e "Publish the day thirty slate" (sims, projects,
  tasks, docs/niche.md, web/data; no media, previews or secrets) and pushed
  to origin/master at 2026-09-28 11:36 EEST on top of 76e0f46
