# Produce short: push or pull a crate, the same 50 N at 30 degrees pushing down beside pulling up, which one moves it

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day38

## Goal

Backlog idea (trend research 2026-10-05, task 20261005-100712, pillar 2
chaos and physics, everyday mechanics; read the full "Push or pull a box"
bullet under "Added by trend research 2026-10-05" in docs/niche.md): the
same force on the same crate, pushing down on it beside pulling up on it;
one moves, one never does.

Orchestrator notes (2026-10-06; closed forms in /tmp/day38/closed.py with
the log /tmp/day38/closed.log, the tipping check in closed-fix.py and
closed-fix.log; g = 9.807 m/s^2). Read /tmp/day38/producer-conventions.md
first. The model: a 10 kg crate, a 50 cm cube, rests on a level floor with
grip (friction coefficient) 0.4, the same at rest and sliding (say so:
chosen); weight m g = 98.07 N. The same force F = 50 N acts on the crate
at 30 degrees to the floor, applied at mid-height (25 cm up) so the crate
slides and never tips (the sim prints the tipping check: overturning
moments F cos a times 0.25 m = 10.83 N m against m g w / 2 = 24.52 N m
and the lift F sin a times w = 12.50 N m against 24.52 + 10.83 N m).
Horizontal drive F cos a = 43.30 N in both bands; vertical part F sin a =
25.00 N. Top band, the "no" case: PUSH, a rod on the rear (left) face
presses forward and down at 30 degrees below the horizontal: floor push
N = m g + 25.00 = 123.07 N, grip limit mu N = 49.23 N, above the 43.30 N
drive, so the crate stays still (a = 0.0000, 0.000 m at 2 s). Bottom
band, the "yes" case: PULL, a rope on the front (right) face pulls forward
and up at 30 degrees above the horizontal: floor push N = 98.07 - 25.00 =
73.07 N, grip limit 29.23 N, net 14.07 N, a = 1.4073 m/s^2, 0.704 m at 1
s, 2.815 m at 2 s moving 2.815 m/s (3 s would be 6.333 m). The
measurement window is 2 s; at 2.0 s the rope is let go and the crate
skids to a stop under sliding friction (deceleration mu g = 3.9228 m/s^2):
skid about 1.010 m in about 0.7175 s, at rest about 3.825 m from the start
at about 2.7175 s (print the exact figures). The push band stays still
throughout (the rod keeps pressing for the 2 s, then lifts off). Integrate
both bands with RK4 at dt = 1e-4 s with the stick-slip rule each step
(static while |drive| is at most mu N and v = 0; sliding friction mu N
against the motion otherwise; the crate stops when v crosses zero), as a
check against the closed forms and a half-step rerun (agree within 1e-9
m); print the forces (weight, press or lift, floor push, grip limit,
drive, net), the acceleration, the position and speed table at 0.5 s
steps to 2 s plus the release, the skid, the tipping check, the energy
at 2 s on the pull (drive work 121.88 J = friction heat 82.27 J + kinetic
39.61 J) and the description variants.

Checks, not facts (the sim must print and compare; state them as checks):
pull: N 73.07 N, grip 29.23 N, a 1.4073 m/s^2, 2.815 m and 2.815 m/s at 2
s; push: N 123.07 N, grip 49.23 N, a 0, 0.000 m; thresholds at 30 degrees
36.80 N to pull against 58.90 N to push (ratio 1.6006), flat 39.23 N; lock
angle acot(mu) = 68.20 degrees (at or above it no push however hard moves
the crate); best pull angle atan(mu) = 21.80 degrees needing 36.42 N (7.2
percent less than flat); 40 N: pull 0.683 m, push 0; 60 N: 4.947 against
0.147 m; 70 N: 7.079 against 1.479 m; grip 0.3: 4.276 against 1.276 m;
grip 0.5: 1.353 against 0 m; 0 degrees: 2.154 m both; 15 degrees: 2.849
against 0.778 m; 45 degrees: 2.054 against 0 m; 60 degrees: 0.619 against
0 m (all at 2 s). Print the schedule in video time, the text widths and
the layout clearances.

Drawing: two-band layout (sims/deskchain style; sims/belt and
sims/tablecloth draw a box on a surface with friction; read deskchain
whole and the drawing parts of belt), side view, the push on top (the "no"
case) and the pull below; same scale, same clock, the crates move left to
right. Scale about 220 px per metre (the crate 110 px, the pull crate's
far position at about 3.83 m plus its width must stay inside the band:
assert it): the floor line about 150 px above the band bottom, the start
mark at x about 70; a dashed gold 2 s mark on the floor at 2.815 m in the
pull band lit when the clock reaches 2 s. Force arrows at 2 px per newton:
the applied 50 N arrow (teal) at 30 degrees from the rod or rope into the
crate's mid-height, the floor push arrow (muted, upward, under the crate,
its length tracking N), the weight arrow (muted, down, from the centre)
and the friction arrow (coral, along the floor, its length the grip limit
in the push band and the sliding friction in the pull band). A "grip
meter" per band: a bar for the 43.3 N drive against a bar for the grip
limit (49.2 and 29.2 N), the longer one wins; label it. Label rows (40
px, coloured): "push down at 30 deg" (coral) and "pull up at 30 deg"
(teal). Readouts (28 px): left column "floor push: NNN N" and the clock;
right column "grip limit: NN N" and "moved: N.NN m". Gold event rows: top
"push down: it never moves" (lit at 2 s and held), bottom "pull up: 2.8 m
in 2 s" (lit at 2 s and held). Shown at 1/2 speed; cycle 8 s (480 frames):
the force comes on 0.5 s into the cycle, the 2 s mark at 0.5 + 2 * 2.0 =
4.5 s, the pull crate at rest at about 0.5 + 2 * 2.7175 = 5.94 s (print
when), hold, reset by a crossfade over the last 0.6 s of the cycle; 5
cycles in 40 s, exactly periodic, the last frame equal to the first. The
legend row after the title: "same crate, same 50 N, 1/2 speed" (measure
it); the shared clock in real seconds since the force came on. Overlay:
"10 kg crate, grip 0.4 | 50 N at 30 deg | no seed" (measure it; shorten
if over 950 px).

Day thirty-eight, first slot. Chosen because "push or pull" is a live
everyday debate (movers, physics classes, exam questions), the two panels
end visibly differently (one crate 2.8 m away, one not moved a
centimeter), the number is exact and the repeat is a natural loop.
Question in the first two seconds: "Push down on a crate, or pull up on
it: which one moves it?" (pre-test; nine words before the question is
the limit; a question-first form "Which moves the crate: pushing down, or
pulling up?" lands at 0.6 s). Keep the question identical in the title,
the hook and the payoff. Setup number: "fifty newtons" (say "newtons"
exactly once in the whole take: a second "newtons" came back "newt ons"
on 2026-10-02; the 30 degrees and the 10 kg go to the overlay and card).
Payoff: pulling up moves it, two point eight meters in two seconds;
pushing down, it never moves (at most two numbers in the payoff beat).
The mechanism sentence must follow the picture: pushing down presses the
crate into the floor and the floor grips it harder; pulling up lifts part
of the weight off the floor and the grip drops (the arrows and the grip
meter show exactly this). Whisper risks: "pull" as a noun ("pole"; use
it only as a verb: "pull up on it"), sentence-initial "Pulled" ("pull
ed"; avoid), "crate" (pre-test; "box" is the fallback), "grip" and
"grips" (pre-test), "presses" (pre-test), "newtons" (once), "slides"
(passed 2026-10-05), avoid "do you", avoid "too". Pre-test hooks with
scripts/voiceover.sh and keep the one whose question lands earliest
under two seconds. Measure every fixed text line with PIL before
rendering and keep every line under 950 px, and the title under 100
characters with no < or >. Music seed 115. Templates: sims/deskchain
(two-band layout, asserts, the clock, the crossfade; read it whole),
sims/belt (a box sliding on a surface with friction, a stripe to show
motion), sims/tablecloth (stick-slip friction), sims/wedge (event rows,
force-free drawing of a block). Sim name pushpull: sims/pushpull/
pushpull.py, projects/pushpull/, media/pushpull/.

## Claim (expected; the sim's numbers replace these)

A 10 kg crate on a floor with grip 0.4 gets the same 50 N at 30 degrees.
Pushing down on it, the floor push rises to 123 N and the grip limit to
49 N, above the 43 N drive: it never moves. Pulling up on it, the floor
push drops to 73 N and the grip limit to 29 N: it slides 2.8 m in 2 s
(1.41 m/s^2). Narrated: fifty newtons (setup); two point eight meters in
two seconds against never moves (payoff). Card: the question; the answer
with 2.8 m in 2 s against 0; floor push 73 against 123 N, grip 29 against
49 N under a 43 N drive; to move it you need 36.8 N pulling, 58.9 N
pushing; above 68 degrees no push works. Description: the model
statement, the equations, the two runs, the force, grip and angle
variants, the skid, the checks.

## Claim

A 10 kg crate (50 cm cube, weight 98.07 N) on a level floor with grip 0.4
gets the same 50 N at 30 degrees, applied at mid-height. Pushing down on
it (a rod on the rear face), the floor push rises to 123.07 N and the grip
limit to 49.23 N, above the 43.30 N drive: it never moves (a = 0, 0.000 m
at 2 s). Pulling up on it (a rope on the front face), the floor push drops
to 73.07 N and the grip limit to 29.23 N, net 14.07 N: a = 1.4073 m/s^2,
2.8147 m at 2 s moving 2.8147 m/s; the rope lets go at 2 s and the crate
skids 1.0098 m in 0.7175 s to rest 3.8244 m from the start at 2.7175 s.
Narrated: fifty newtons (setup); two point eight meters in two seconds
against never moves (payoff). Card: the question; pull up 2.8 m in 2 s
against push down 0 m; floor push 73 against 123 N; grip 29 against 49 N
under the 43 N drive; needs 36.8 N pulling, 58.9 N pushing; above 68 deg
no push works.

## Evidence

### Measurements

Sim: sims/pushpull/pushpull.py with projects/pushpull/manifest.json (RK4
at dt = 1e-4 s with the stick-slip rule decided once per step from the
step-start state, the forces held over each step so the step boundaries
fall on the 2 s release, the stop located by bisection, a half-step
rerun, closed forms; deterministic, no seed, no wall clock). Log:
media/pushpull/measure.log (exit 0; the full final log follows).

Brief checks (the sim prints "checks against the brief (50 checks, 0
failed)"): pull N 73.07 N (sim 73.0700), grip 29.23 N (29.2280), a 1.4073
m/s^2 (1.407327), 2.815 m and 2.815 m/s at 2 s (2.8147 both), 1 s 0.704 m
(0.7037), 3 s without the release 6.333 m (6.33297); push N 123.07 N
(123.0700), grip 49.23 N (49.2280), a 0 (0.000000), 0.000 m (0.0, RK4 max
|x| 0.0e+00 m); drive 43.30 N (43.3013), vertical 25.00 N, weight 98.07
N; thresholds 36.80 N pull (36.7984) against 58.90 N push (58.8987), ratio
1.6006 (1.60058), flat 39.23 N (39.228); lock angle 68.20 deg (68.1986);
best pull angle 21.80 deg (21.8014) needing 36.42 N (36.4223), 7.2 percent
less (7.15); skid about 1.010 m in about 0.7175 s to rest about 3.825 m at
about 2.7175 s (sim 1.0098 m, 0.717511 s, 3.8244 m, 2.717511 s); energy at
2 s drive work 121.88 J (121.878) = heat 82.27 J (82.2667) + kinetic 39.61
J (39.6114); tipping 10.83 N m against 24.52 N m and lift 12.50 N m
against 24.52 + 10.83 = 35.34 N m (push 10.83 against 37.02 N m): no tip;
variants at 2 s: 40 N 0.683 against 0 (0.6826 / 0.0), 60 N 4.947 against
0.147 (4.9467 / 0.1467), 70 N 7.079 against 1.479 (7.0788 / 1.4788), grip
0.3 4.276 against 1.276 (4.27605 / 1.27605), grip 0.5 1.353 against 0
(1.35325 / 0.0), 0 deg 2.154 both (2.1544), 15 deg 2.849 against 0.778
(2.84893 / 0.778382), 45 deg 2.054 against 0 (2.05389 / 0.0), 60 deg 0.619
against 0 (0.618502 / 0.0). All passed within the rounding (tolerances 6e-3
N, 6e-4 m, 6e-5 m/s^2 or s). Also printed: the RK4 table at 0.5 s steps,
the closed-form agreement within 2.3e-13 m over the window, the half-step
rerun within 1.7e-12 m and 1.8e-13 s, the schedule in video time, the
text widths (every line under 950 px, widest the overlay at 895 px) and
the layout clearances.

Final measure.log:

```
Tue Oct  6 10:30:36 AM EEST 2026
warning: Git tree '/home/alex/personal/seedzero' is dirty
setup: side view, two bands on one clock, the same floor drawn the same way at the same scale: a 10 kg crate (50 cm cube, weight m g = 98.07 N) rests on a level floor with grip (friction coefficient) mu = 0.4, the same at rest and sliding (a chosen number); g = 9.807 m/s^2; the same force F = 50 N acts at 30 degrees to the floor, applied at mid-height (25 cm up) so the crate slides and never tips; top band PUSH: a rod on the rear face presses forward and down; bottom band PULL: a rope on the front face pulls forward and up; the force acts for 2 s (the measurement window), then the tool lets go and a moving crate skids to a stop under sliding friction mu m g; RK4 at 10000 steps per second (dt = 1e-04 s) with the stick-slip rule each step, the forces held over each step, the stop located by bisection, checked against the closed forms and a half-step rerun; shown at 1/2 speed on a 8 s cycle (480 frames) with the force coming on 0.5 s into the cycle, 5 cycles in 40 s; drawn at 220 px per metre; deterministic, no seed
the same in both bands: horizontal drive F cos a = 43.30 N = 43.3013 N, vertical part F sin a = 25.00 N; weight 98.07 N; a crate at rest moves only when the drive exceeds the grip limit mu N
push down at 30 deg (top band): weight 98.07 N, press F sin a = 25.00 N, floor push N = 123.07 N (123.0700 N), grip limit mu N = 49.23 N (49.2280 N), drive 43.30 N, net -5.93 N: the crate stays still; a = 0.0000 m/s^2 (0.000000); RK4 table (real time after the force came on): 0.0 s: 0.0000 m at 0.0000 m/s (closed 0.0000 m, diff +0.0e+00 m); 0.5 s: 0.0000 m at 0.0000 m/s (closed 0.0000 m, diff +0.0e+00 m); 1.0 s: 0.0000 m at 0.0000 m/s (closed 0.0000 m, diff +0.0e+00 m); 1.5 s: 0.0000 m at 0.0000 m/s (closed 0.0000 m, diff +0.0e+00 m); 2.0 s: 0.0000 m at 0.0000 m/s (closed 0.0000 m, diff +0.0e+00 m); at the release (2 s) 0.0000 m = 0.000 m moving 0.0000 m/s = 0.000 m/s (closed form a T^2 / 2 = 0.0000 m, a T = 0.0000 m/s; diffs +0.0e+00 m, +0.0e+00 m/s); the position stays within 0.0e+00 m of the closed form over the window; 40000 steps; half-step rerun (dt = 5e-05 s): 0.000000000 m (+0.0e+00 m) at 0.000000000 m/s; 1 s 0.000 m, 3 s without the release would be 0.000 m
push: the rod keeps pressing for the 2 s, then lifts off; the crate never moved (RK4 max |x| 0.0e+00 m); the static friction equals the drive 43.30 N, 5.93 N under the grip limit
pull up at 30 deg (bottom band): weight 98.07 N, lift F sin a = 25.00 N, floor push N = 73.07 N (73.0700 N), grip limit mu N = 29.23 N (29.2280 N), drive 43.30 N, net +14.07 N: the crate slides; a = 1.4073 m/s^2 (1.407327); RK4 table (real time after the force came on): 0.0 s: 0.0000 m at 0.0000 m/s (closed 0.0000 m, diff +0.0e+00 m); 0.5 s: 0.1759 m at 0.7037 m/s (closed 0.1759 m, diff +4.9e-15 m); 1.0 s: 0.7037 m at 1.4073 m/s (closed 0.7037 m, diff +8.2e-15 m); 1.5 s: 1.5832 m at 2.1110 m/s (closed 1.5832 m, diff +1.8e-13 m); 2.0 s: 2.8147 m at 2.8147 m/s (closed 2.8147 m, diff +2.0e-13 m); at the release (2 s) 2.8147 m = 2.815 m moving 2.8147 m/s = 2.815 m/s (closed form a T^2 / 2 = 2.8147 m, a T = 2.8147 m/s; diffs +2.0e-13 m, -3.3e-13 m/s); the position stays within 2.3e-13 m of the closed form over the window; 40000 steps; half-step rerun (dt = 5e-05 s): 2.814654038 m (-1.0e-12 m) at 2.814654038 m/s; 1 s 0.704 m, 3 s without the release would be 6.333 m
pull skid: at 2 s the rope lets go and the crate skids under sliding friction mu m g = 39.23 N (deceleration mu g = 3.9228 m/s^2): skid 1.0098 m = 1.010 m in 0.7175 s (closed form v^2 / (2 mu g) = 1.0098 m, v / (mu g) = 0.7175 s; diffs +2.3e-13 m, +8.0e-14 s), at rest 3.8244 m = 3.824 m from the start at 2.7175 s; half-step rerun stops at 3.824427332 m (-1.7e-12 m) at 2.717511481 s (-1.8e-13 s)
pull energy at 2 s: drive work F cos a x = 121.88 J = friction heat mu N x = 82.27 J + kinetic m v^2 / 2 = 39.61 J (sum 121.88 J, diff +1.2e-11 J); the skid turns the 39.61 J into heat over 1.010 m (39.61 J)
tipping check (force at 25 cm up on a 50 cm cube): pull: lifting the rear about the front bottom edge F cos a h = 10.83 N m against m g w / 2 = 24.52 N m: no tip; lifting the front about the rear bottom edge F sin a w = 12.50 N m against 24.52 + 10.83 = 35.34 N m: no tip; push: lifting the rear about the front bottom edge 10.83 N m against m g w / 2 + F sin a w = 37.02 N m: no tip; the crate slides and never tips
thresholds: the force that just moves the crate at 30 deg is mu m g / (cos a + mu sin a) = 36.80 N pulling against mu m g / (cos a - mu sin a) = 58.90 N pushing (ratio 1.6006); flat (0 deg) mu m g = 39.23 N; push lock angle acot(mu) = 68.20 deg (at or above it no push, however hard, moves the crate: the extra press adds more grip than drive); best pull angle atan(mu) = 21.80 deg needing mu m g / sqrt(1 + mu^2) = 36.42 N (7.2 percent less than flat)
for the description: F 40 N at 30 deg: pull N 78.07 N, grip 31.23 N, a 0.341 m/s^2; push N 118.07 N, grip 47.23 N, a 0.000 m/s^2; drive 34.64 N; at 2 s 0.683 against 0.000 m; F 60 N at 30 deg: pull N 68.07 N, grip 27.23 N, a 2.473 m/s^2; push N 128.07 N, grip 51.23 N, a 0.073 m/s^2; drive 51.96 N; at 2 s 4.947 against 0.147 m; F 70 N at 30 deg: pull N 63.07 N, grip 25.23 N, a 3.539 m/s^2; push N 133.07 N, grip 53.23 N, a 0.739 m/s^2; drive 60.62 N; at 2 s 7.079 against 1.479 m; grip 0.3, 50 N at 30 deg: pull N 73.07 N, grip 21.92 N, a 2.138 m/s^2; push N 123.07 N, grip 36.92 N, a 0.638 m/s^2; drive 43.30 N; at 2 s 4.276 against 1.276 m; grip 0.5, 50 N at 30 deg: pull N 73.07 N, grip 36.54 N, a 0.677 m/s^2; push N 123.07 N, grip 61.54 N, a 0.000 m/s^2; drive 43.30 N; at 2 s 1.353 against 0.000 m; 50 N at 0 deg: pull N 98.07 N, grip 39.23 N, a 1.077 m/s^2; push N 98.07 N, grip 39.23 N, a 1.077 m/s^2; drive 50.00 N; at 2 s 2.154 against 2.154 m; 50 N at 15 deg: pull N 85.13 N, grip 34.05 N, a 1.424 m/s^2; push N 111.01 N, grip 44.40 N, a 0.389 m/s^2; drive 48.30 N; at 2 s 2.849 against 0.778 m; 50 N at 45 deg: pull N 62.71 N, grip 25.09 N, a 1.027 m/s^2; push N 133.43 N, grip 53.37 N, a 0.000 m/s^2; drive 35.36 N; at 2 s 2.054 against 0.000 m; 50 N at 60 deg: pull N 54.77 N, grip 21.91 N, a 0.309 m/s^2; push N 141.37 N, grip 56.55 N, a 0.000 m/s^2; drive 25.00 N; at 2 s 0.619 against 0.000 m
checks against the brief (50 checks, 0 failed): push floor push N (N): brief 123.07, sim 123.07, diff +1.4e-14: ok; push grip limit (N): brief 49.23, sim 49.228, diff -2.0e-03: ok; push a (m/s^2): brief 0, sim 0, diff +0.0e+00: ok; push 2 s (m): brief 0, sim 0, diff +0.0e+00: ok; pull floor push N (N): brief 73.07, sim 73.07, diff +1.4e-14: ok; pull grip limit (N): brief 29.23, sim 29.228, diff -2.0e-03: ok; pull a (m/s^2): brief 1.4073, sim 1.40733, diff +2.7e-05: ok; pull 1 s (m): brief 0.704, sim 0.703664, diff -3.4e-04: ok; pull 2 s (m): brief 2.815, sim 2.81465, diff -3.5e-04: ok; pull 2 s speed (m/s): brief 2.815, sim 2.81465, diff -3.5e-04: ok; pull 3 s without release (m): brief 6.333, sim 6.33297, diff -2.8e-05: ok; skid (m): brief 1.01, sim 1.00977, diff -2.3e-04: ok; skid time (s): brief 0.7175, sim 0.717511, diff +1.1e-05: ok; at rest (m): brief 3.825, sim 3.82443, diff -5.7e-04: ok; at rest at (s): brief 2.7175, sim 2.71751, diff +1.1e-05: ok; drive work (J): brief 121.88, sim 121.878, diff -1.9e-03: ok; friction heat (J): brief 82.27, sim 82.2667, diff -3.3e-03: ok; kinetic (J): brief 39.61, sim 39.6114, diff +1.4e-03: ok; drive F cos a (N): brief 43.3, sim 43.3013, diff +1.3e-03: ok; vertical F sin a (N): brief 25, sim 25, diff -3.6e-15: ok; weight (N): brief 98.07, sim 98.07, diff +1.4e-14: ok; tip F cos a h (N m): brief 10.83, sim 10.8253, diff -4.7e-03: ok; restoring m g w / 2 (N m): brief 24.52, sim 24.5175, diff -2.5e-03: ok; lift F sin a w (N m): brief 12.5, sim 12.5, diff -1.8e-15: ok; pull threshold (N): brief 36.8, sim 36.7984, diff -1.6e-03: ok; push threshold (N): brief 58.9, sim 58.8987, diff -1.3e-03: ok; threshold ratio: brief 1.6006, sim 1.60058, diff -2.2e-05: ok; flat threshold (N): brief 39.23, sim 39.228, diff -2.0e-03: ok; lock angle (deg): brief 68.2, sim 68.1986, diff -1.4e-03: ok; best pull angle (deg): brief 21.8, sim 21.8014, diff +1.4e-03: ok; best pull force (N): brief 36.42, sim 36.4223, diff +2.3e-03: ok; best pull saving (percent): brief 7.2, sim 7.15233, diff -4.8e-02: ok; F 40 N at 30 deg pull 2 s (m): brief 0.683, sim 0.682603, diff -4.0e-04: ok; F 40 N at 30 deg push 2 s (m): brief 0, sim 0, diff +0.0e+00: ok; F 60 N at 30 deg pull 2 s (m): brief 4.947, sim 4.9467, diff -3.0e-04: ok; F 60 N at 30 deg push 2 s (m): brief 0.147, sim 0.146705, diff -3.0e-04: ok; F 70 N at 30 deg pull 2 s (m): brief 7.079, sim 7.07876, diff -2.4e-04: ok; F 70 N at 30 deg push 2 s (m): brief 1.479, sim 1.47876, diff -2.4e-04: ok; grip 0.3, 50 N at 30 deg pull 2 s (m): brief 4.276, sim 4.27605, diff +5.4e-05: ok; grip 0.3, 50 N at 30 deg push 2 s (m): brief 1.276, sim 1.27605, diff +5.4e-05: ok; grip 0.5, 50 N at 30 deg pull 2 s (m): brief 1.353, sim 1.35325, diff +2.5e-04: ok; grip 0.5, 50 N at 30 deg push 2 s (m): brief 0, sim 0, diff +0.0e+00: ok; 50 N at 0 deg pull 2 s (m): brief 2.154, sim 2.1544, diff +4.0e-04: ok; 50 N at 0 deg push 2 s (m): brief 2.154, sim 2.1544, diff +4.0e-04: ok; 50 N at 15 deg pull 2 s (m): brief 2.849, sim 2.84893, diff -6.6e-05: ok; 50 N at 15 deg push 2 s (m): brief 0.778, sim 0.778382, diff +3.8e-04: ok; 50 N at 45 deg pull 2 s (m): brief 2.054, sim 2.05389, diff -1.1e-04: ok; 50 N at 45 deg push 2 s (m): brief 0, sim 0, diff +0.0e+00: ok; 50 N at 60 deg pull 2 s (m): brief 0.619, sim 0.618502, diff -5.0e-04: ok; 50 N at 60 deg push 2 s (m): brief 0, sim 0, diff +0.0e+00: ok
schedule (video time, 1/2 speed): cycles of 8 s start at -4.00, 4.00, 12.00, 20.00, 28.00, 36.00 s (the first 4.00 s before the first frame); the force comes on 0.5 s into each cycle at 4.50, 12.50, 20.50, 28.50, 36.50 s; the 2 s mark (the rope and the rod let go, both event rows light) is 4.50 s into the cycle at 0.50, 8.50, 16.50, 24.50, 32.50 s; the pull crate is at rest 5.935 s into the cycle (5.435 s after the force) at 1.94, 9.94, 17.94, 25.94, 33.94 s, before the fade at 7.40 s; the tools fade over 0.4 s after the release; the reset crossfade runs over the last 0.6 s of each cycle (from 3.40, 11.40, 19.40, 27.40, 35.40 s; the readouts out over its first half and in over its second); on the first frame the cycle is 4.00 s in (1.750 s real after the force came on: the push crate force at 0.000 m, the pull crate force at 2.155 m moving 2.463 m/s); title until 3 s; payoff card from 30 s; the title fades back in over the last 0.5 s and the last frame repeats the first (the scene is periodic: 40 s holds exactly 5 cycles)
text widths (the on-screen strings verbatim): overlay@34 895 px '10 kg crate, grip 0.4 | 50 N at 30 deg | no seed', title line 1@56 789 px 'Push down on a crate, or', title line 2@56 743 px 'pull up on it: which one', title line 3@56 303 px 'moves it?', legend@40 765 px 'same crate, same 50 N, 1/2 speed', clock@28 497 px '1.252 s after the force came on', clock held@28 315 px 'at rest, no force yet', label push@40 473 px 'push down at 30 deg', floor push push@28 302 px 'floor push: 123.1 N', fixed push@28 438 px 'weight 98.1 N, press 25.0 N', grip push@28 268 px 'grip limit: 49.2 N', event push@40 610 px 'push down: it never moves', label pull@40 384 px 'pull up at 30 deg', floor push pull@28 283 px 'floor push: 73.1 N', fixed pull@28 397 px 'weight 98.1 N, lift 25.0 N', grip pull@28 268 px 'grip limit: 29.2 N', event pull@40 448 px 'pull up: 2.8 m in 2 s', moved@40 335 px 'moved: 3.82 m', speed@28 239 px 'speed 2.81 m/s', meter label@24 124 px 'grip limit', meter value@24 104 px '123.1 N', verdict@24 78 px 'slides', mark@24 39 px '2 s', start@24 65 px 'start', payoff line 1@40 867 px 'push down or pull up: which moves it?', payoff line 2@40 836 px 'pull up: 2.8 m in 2 s; push down: 0 m', payoff line 3@40 868 px 'floor push 73 N pulling, 123 N pushing', payoff line 4@40 768 px 'grip 29 N against 49 N, drive 43 N', payoff line 5@40 834 px 'needs 36.8 N pulling, 58.9 N pushing', payoff line 6@40 661 px 'above 68 deg, no push works'
row check: the left column ends at x 513 px, the right column starts at x 705 px; both end 136 px under the band top; the grip meter spans 143 to 195 px under the band top and x 516 to 1040; the floor line is 398 px under the band top (plank to 422), the crate 110 px square from 288 px with its rear face at x 100 at the start; the pull crate's rear face reaches x 719 at the 2 s mark and its front face x 1051.4 at rest (3.824 m), the rope's far end x 985 and 253 px under the band top; the push arrow's tail at x 13.4; the floor push arrow tops 152 (push), 252 (pull) and 202 (skid, N = m g) px under the band top; the weight arrow's tip at 539 px; the friction arrow reaches x 57 inside the plank; the event row spans 448 to 492 px under the band top and x 215 to 825 (push, 610 px) and 296 to 744 (pull, 448 px), centred on 520; the push weight arrow stands at x 169, the pull one at x 788 when its event row lights; the 2 s mark at x 719.2; each band is 550 px tall (y 330 to 880 and 880 to 1430); the caption band starts at y 1440; the title rows end at y 330 and the overlay band ends at y 130
Tue Oct  6 10:30:37 AM EEST 2026
```

### Production

- Manifest: projects/pushpull/manifest.json (fps 60, 40 s, 1/2 speed,
  cycle 8 s, the force on 0.5 s into the cycle, window 2 s,
  first_cycle_at -4.0, reset crossfade 0.6 s, tool fade 0.4 s, 220 px/m,
  start x 100, floor 398 px under the band top, three-row title until 3
  s, payoff_t 30.0 s, hold 0.6 s, loop fade 0.5 s, music seed 115, music
  gain 0.18, voice offset 0.6, caption_y 0.75, overlay "10 kg crate, grip
  0.4 | 50 N at 30 deg | no seed").
- Layout: two bands (push on top, pull below), label row at 40 px, left
  column "floor push: NNN.N N" and the fixed "weight 98.1 N, press/lift
  25.0 N", right column "moved: N.NN m" (40 px, gold once the 2 s mark
  passes), "grip limit: NN.N N" and "speed N.NN m/s"; the grip meter at
  156/182 px under the band top on the right (teal drive bar against a
  coral grip-limit bar at 2 px/N, values, the winner's row marked
  "holds" or "slides" in gold); the floor line with a 24 px plank, a gold
  start notch, a dashed 2 s mark on the pull floor at 2.815 m (dim, lit
  gold from 2 s); the crate 110 px; arrows at 2 px/N: drive (teal, 100
  px) along the rod or rope, floor push (light grey, up from the floor
  through the crate, 246 / 146 px, 196 px during the skid), weight
  (grey, down from the centre, 196 px), friction (coral, in the plank;
  a dim coral line to the grip limit under it); event rows in the ground
  region at 470 px, centred on x 520.
- Schedule (video time): force on 4.50, 12.50, 20.50, 28.50, 36.50 s; 2
  s marks 8.50, 16.50, 24.50, 32.50 s (0.50 s before frame 0 as well);
  pull crate at rest 9.94, 17.94, 25.94, 33.94 s; crossfades from 3.40,
  11.40, 19.40, 27.40, 35.40 s. Frame 0: 1.750 s after the force, the
  push crate held at 0.000 m, the pull crate at 2.155 m moving 2.463
  m/s.
- Smoke frames viewed: media/pushpull/smoke-{0.0,1.5,2.0,4.6,8.3,9.0,
  11.6,32.6,34.0}.png: frame 0 the title over the rod pressing and the
  pull crate at 2.15 m with the rope; 4.6 s the legend and clock 0.050
  s with the force just on; 9.0 s the skid at 2.250 s with both event
  rows lit and the lit 2 s mark; 11.6 s the crossfade (old crate at
  rest fading out, new crate at the start fading in, readouts dimmed);
  34.0 s the six-line card.
- Render: media/pushpull/render.log, footage.mp4 (2400 frames, 28 s);
  loop check 0 px (max channel difference 0); periodicity check 0 px;
  loop step 11147 px between the last two frames.
- Hook pre-tests (media/pushpull/hooks/pretest.log): hook1 "Push down
  on a crate, or pull up on it: which one moves it?" ok (3.70 s), the
  question starts at 0.60 s of video; hook2 the same plus "On top, a
  rod presses forward and down." ok (6.19 s), question at 0.60 s; hook3
  "Which moves the crate: pushing down, or pulling up?" ok (3.01 s),
  0.60 s; hook4 "Same crate, same force. Push down on a crate, ..." ok
  (5.12 s), the question after a pause ending at 2.86 s, so 3.46 s of
  video. Chosen: hook1, the question first at 0.60 s. Word test: "The
  crate slides", "the floor grips it harder", "The rod presses forward
  and down", "Pulling up lifts part of the weight off the floor", "Every
  run, the same", "Two point eight meters in two seconds", "The rod
  loses", "The rope wins", "Pushing down, it never moves", "Same fifty
  newtons, at the same angle" all matched; the sentence-initial "Shown
  at half speed" came back "joan", so the narration keeps "shown at half
  speed" mid-sentence (it passed in the full take).
- Narration: projects/pushpull/narration.txt, 113 words (wc); the
  question is the first sentence (0.60 to 4.17 s of video) and is
  repeated word for word before the payoff ("So, push down on a crate,
  or pull up on it: which one moves it?" 26.4 to 28.8 s). One setup
  number ("fifty newtons", "newtons" once in the take) and the payoff
  "two point eight meters in two seconds" against "it never moves".
- Voice: one pass, ok, 33.56 s (media/pushpull/voice.log); the voice
  ends at 34.16 s of video. Timing (media/pushpull/timing.log):

```
  0.60 -   1.90  Push down on a crate.
  1.90 -   2.96  or pull up on it.
  2.96 -   4.17  Which one moves it?
  4.17 -   4.89  on top
  4.89 -   7.57  A rod presses forward and down below.
  7.57 -  15.76  A rope pulls forward and up, same crate, same 50 Newtons,
 at the same angle, shown at half speed.
 Pushing down presses the crate into the floor,
 15.76 -  18.52  so the floor grips it harder and the rod loses.
 18.52 -  20.93  Pulling up lifts part of the weight off the floor,
 20.93 -  26.41  so the grip drops and the rope wins every run the same so
 pushed down on a crate
 26.41 -  27.48  or pull up on it.
 27.48 -  29.96  Which one moves it? Pulling up moves it.
 29.96 -  34.16  2.8 meters in 2 seconds, pushing down, it never moves.
voice 33.56 s, ends at 34.16 s of video
```

  Sync: "On top, a rod presses forward and down" 4.2 to 6.3 s under the
  rod pressing from 4.50 s; "Below, a rope pulls forward and up" to about
  8.0 s under the pull (release 8.50 s); the mechanism sentences 11.5 to
  23 s over the force windows 12.50 to 16.50 and 20.50 to 24.50 s; the
  question repeat 26.4 to 28.8 s over the skid and the reset; "Pulling
  up moves it" 28.8 to 29.96 s with the force on at 28.50 s; "two point
  eight meters in two seconds" from 29.96 s with the card from 30.0 s
  and the crate reaching the gold 2 s mark at 32.50 s; "Pushing down, it
  never moves" to 34.16 s with the push event row lit from 32.50 s. 22
  silences at -35 dB / 0.22 s (media/pushpull/silences.log).
- Compose: media/pushpull/compose.log: music seed 115, 40.00 s; captions
  18 pauses detected, 18 matched, max chunk start shift 0.772 s;
  final.mp4 40.000000 s.
- Text widths (measure.log): overlay 895, title rows 789 / 743 / 303,
  legend 765, clock 497, labels 473 / 384, event rows 610 / 448, card
  lines 867 / 836 / 868 / 768 / 834 / 661 px; all under 950 px.

### Local QA

- media/pushpull/final.mp4: md5 caac45f25aaa1fbc30da0a27dba57af8,
  4152508 bytes; ffprobe h264 1080x1920 60/1, aac 22050 Hz mono,
  duration 40.000000; atoms ftyp, moov at 32, free, mdat at 44588
  (faststart).
- Caption text against the narration (by script): 35 drawtext chunks
  (the first is the overlay); the joined caption text equals the
  narration word for word (113 words). The first caption "Push down on
  a" is enabled from 0.600 s; the last ends at 34.164 s.
- Question timing: on screen from frame 0 (three-row title) and spoken
  from 0.60 s of video (hook1, question first).
- signalstats YMAX on footage.mp4 over all frames: caption band rows
  1440-1530 = 28 (background), overlay band rows 96-130 = 28: nothing
  drawn under the captions or the overlay.
- Full-resolution frames viewed (media/pushpull/qa-T.png): 0.00 the
  teal overlay, the three-row title, the push crate held at the start
  with the rod and teal arrow, the pull crate at 2.15 m with the rope
  and arrows, both meters ("holds" / "slides"), no caption; 1.00 the
  title still up, the rod lifted (floor push 98.1 N), the pull crate
  skidding at 3.40 m past the lit 2 s mark, both gold event rows,
  caption "Push down on a"; 2.10 the pull crate at rest at 3.82 m,
  caption "crate, or pull up on"; 14.00 legend and clock 0.750 s, the
  rod pressing (floor push 123.1 N, grip 49.2 N, "holds"), the pull
  crate at 0.40 m (73.1 N, 29.2 N, "slides"), caption "Pushing down
  presses"; 30.40 the card rising, pull crate at 0.64 m, caption "two
  point eight"; 31.80 the card full, pull crate at 1.92 m approaching
  the 2 s mark, caption "meters in two"; 32.60 the crate just past the
  lit gold 2 s mark at 2.95 m with the rope released and both event
  rows lit, caption "Pushing down, it"; 39.983 identical to frame 0
  (title back, no caption, no card). media/pushpull/sheet.png viewed:
  40 cells, the captions in order, no clipping, the card from the 31st
  cell (30 s).
- Loop check: render.log "last frame differs from the first in 0 px",
  periodicity 0 px.
- Narrated numbers against measure.log: "fifty newtons" (log "F = 50 N
  acts at 30 degrees"), "two point eight meters in two seconds" (log "at
  the release (2 s) 2.8147 m = 2.815 m"), "half speed" (log "shown at
  1/2 speed"), "it never moves" (log "the crate never moved (RK4 max |x|
  0.0e+00 m)"). Description numbers checked by script against
  measure.log with commas stripped: 77 distinct number tokens, 0
  missing.

### Metadata

projects/pushpull/metadata.json written by a Python script with asserts
(title 97 chars, description 3194 chars, 12 tags, ASCII, no < or >;
every description number present in measure.log), then confirmed with
ls -l (3759 bytes). Title: "Push down on a crate, or pull up on it:
which one moves it? Pull up: 2.8 m in 2 s, push down: 0 m". Tags: the
question, push or pull, friction, normal force, crate, physics, physics
visualization, simulation, shorts, mechanics, classical mechanics,
newton's laws. privacyStatus private, categoryId 27,
containsSyntheticMedia true, selfDeclaredMadeForKids false.

### Deviations from the brief

- Start mark at x 100 instead of about 70: the 100 px teal drive arrow
  into the rear face needs 86.6 px to the left of the crate, and at x 70
  its tail would leave the frame (13.4 px margin at x 100). The pull
  crate's front face at rest is at x 1051.4 (asserted inside the frame).
- Floor line 398 px under the band top (152 px above the band bottom):
  the window that lets the 246 px floor-push arrow clear the text rows
  (top at 152) and the 196 px weight arrow stay inside the band (tip at
  539).
- Push band friction arrow drawn at the static friction actually acting
  (43.3 N, equal to the drive) with a dim coral line under it to the
  grip limit (49.2 N), instead of a solid arrow at the grip limit: a 49 N
  friction arrow against a 43 N drive would show an unbalanced leftward
  force on a crate at rest. The grip meter shows the 49.2 N limit beside
  the 43.3 N drive.
- Grip meter placed at 156/182 px under the band top on the right (x 516
  to 1040) with the winner's row marked "holds" or "slides" in gold, the
  only region no arrow reaches in either band.
- Readouts: the right column carries "moved" (40 px), "grip limit" and
  "speed"; the left column "floor push" and the fixed "weight, press /
  lift" line; the per-band clock is the shared clock at y 290.
- Card first line "push down or pull up: which moves it?" (the full
  question measures over 1300 px at 40 px); second line "pull up: 2.8 m
  in 2 s; push down: 0 m"; the other lines shortened to fit under 950
  px ("grip 29 N against 49 N, drive 43 N", "needs 36.8 N pulling, 58.9
  N pushing", "above 68 deg, no push works").
- Narration order: the rod and rope sentences come right after the
  question and before the setup sentence, so they play under the first
  force window (4.50 to 8.50 s); the setup sentence says "at the same
  angle" and "shown at half speed" (the 30 degrees and the 10 kg stay in
  the overlay and card as asked). 113 words by wc (33.56 s of voice,
  inside the 30.5 to 35.3 s pace range).
- first_cycle_at -4.0 so that frame 0 shows the pull crate moving at
  2.155 m (motion in progress) and the 2 s mark of the fifth cycle lands
  at 32.50 s under the payoff words.
- The rest position prints as 3.8244 m (the brief's "about 3.825 m";
  v^2 / (2 mu g) = 1.0098 m); the figures in the description are the
  sim's.

## Niche note

Appended to the "Push or pull a box" bullet in docs/niche.md:

[produced 2026-10-06 as "Push down on a crate, or pull up on it: which
one moves it? Pull up: 2.8 m in 2 s, push down: 0 m"; measured drive
43.30 N, vertical 25.00 N; push down N 123.07 N, grip 49.23 N, a 0,
0.000 m; pull up N 73.07 N, grip 29.23 N, a 1.4073 m/s^2, 2.815 m and
2.815 m/s at 2 s, skid 1.010 m in 0.7175 s to rest 3.824 m at 2.7175 s;
thresholds 36.80 against 58.90 N (ratio 1.6006), flat 39.23 N, lock
angle 68.20 deg, best pull 21.80 deg at 36.42 N; 40 N 0.683 against 0,
60 N 4.947 against 0.147, 70 N 7.079 against 1.479 m; grip 0.3 4.276
against 1.276, grip 0.5 1.353 against 0 m; 0 deg 2.154 both, 15 deg
2.849 against 0.778, 45 deg 2.054 against 0, 60 deg 0.619 against 0 m;
RK4 dt 1e-4 s with the stick-slip rule against the closed forms within
2.3e-13 m, 50 checks, 0 failed; task 20261006-101400]

## Upload

- Attempt 1 of 5 (quota day 2026-10-06T10:00 EEST) recorded at 2026-10-06T10:44:06+03:00 before scripts/yt-upload.py pushpull; zero earlier attempts since the boundary.
- Uploaded private as vFjXXGz8o54 at 2026-10-06T10:44:09Z (videos.insert 1,600 units). yt-qa.py --wait --publish: gate 15 of 15 on the first processed read, published at 2026-10-06T10:45:10+03:00, re-read public, 55 units. https://youtu.be/vFjXXGz8o54
