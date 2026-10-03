# Produce short: Swim to the flag, aim at the flag beside aim upstream across a river

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day35

## Goal

Backlog idea (trend research 2026-09-29, task 20260929-100144, pillar 2
chaos and physics, everyday mechanics; read the full entry under "Added
by trend research 2026-09-29" in docs/niche.md): "Swim to the flag: two
swimmers at 1.0 m/s across a 50 m river running 0.8 m/s, one always
heading at the flag beside one aiming 53.1 degrees upstream; measure the
crossing times; expect 83.3 s straight across (w / sqrt(v^2 - u^2))
against 138.9 s (w v / (v^2 - u^2)), 1.67 times longer, the flag swimmer
swept 16.9 m downstream first; at a current equal to the swim speed the
flag swimmer ends exactly half the width (25.0 m) downstream and never
lands; RK4; play it fast; deterministic, no seed."

Orchestrator notes (2026-10-03, before this brief). The model: a river w
= 50 m wide with a uniform current u = 0.8 m/s everywhere (the same at
the banks and in the middle, say so); two swimmers who both move at v =
1.0 m/s relative to the water, both starting on the near bank directly
across from a flag on the far bank, both let go at the same instant.
Swimmer A ("aim at the flag") always points straight at the flag, so the
velocity is v times the unit vector toward the flag plus the current
(down the river). Swimmer B ("aim upstream") holds one fixed heading,
asin(u / v) = 53.13 degrees upstream of straight across, so the upstream
part of the swimming speed, v sin(theta) = 0.8 m/s, cancels the current
and the track is a straight line across at sqrt(v^2 - u^2) = 0.6 m/s.
Integrate A with RK4 at 1e-3 s steps (a half-step rerun as a check) and
stop when A is within 1 mm of the flag; B is closed form but integrate it
the same way and check the track stays on the line (|downstream| under
1e-9 m). Measure the crossing times and check them against the closed
forms: B: w / sqrt(v^2 - u^2) = 83.333 s; A: w v / (v^2 - u^2) = 138.889 s
(the pursuit time in a uniform stream); the ratio v / sqrt(v^2 - u^2) =
1.6667. Also measure for A: the furthest downstream point (16.89 m at
42.7 s), where A is when B lands at 83.33 s (49.13 m across, 11.09 m
downstream, 11.13 m from the flag, heading 85.5 degrees upstream, almost
straight into the current), and A's heading against time (it swings from
0 to 90 degrees upstream as it is swept down and then crawls up the far
bank). For the description: currents of 0.5 m/s (B 57.74 s at 30.0
degrees, A 66.67 s, swept 9.62 m), 0.9 m/s (B 114.71 s at 64.2 degrees, A
263.16 s, swept 20.11 m) and 1.0 m/s (B cannot hold a line, 90 degrees
upstream means swimming in place; A never lands: it settles 25.0 m
downstream and 50 m across, 1 mm short after 1,200 s is fine as the
printed check), and the swimmer who points straight across and lets the
current take it: lands 40.0 m downstream after 50.0 s. Print the two
tracks at 5 s intervals (across, downstream, heading), the landing times
against the closed forms with the differences, the half-step agreement
(better than 1e-3 s on both landings), the schedule in video time, the
text widths and the layout clearances. State every number above as a
check the sim must print, not as a fact.

Drawing: top view, two stacked bands (y 330-880 and 880-1430), A "aim at
the flag" on top (coral, the slow one), B "aim upstream" below (teal); the
same river drawn the same way at the same scale, 11 px per metre: the
river 550 px wide across the band from x 265 to 815, flowing down the
screen (downstream is +y), the near bank on the left (x 40-265) and the
far bank on the right (x 815-1040) as lighter slabs; the start on the near
bank's edge about 250 px under the band top and the flag (a small gold
pennant on a pole) on the far bank's edge directly across; the current
shown by faint chevrons or dashes that drift downstream at the current's
speed (5x: 4.0 m/s real = 44 px per video second; smear each mark over one
frame's travel so it never strobes, as sims/balloon does for lane dashes);
the swimmer a 10 px dot with a 26 px heading tick and a trail in its
band's colour (A's trail bows 16.9 m = 186 px downstream before curving
back to the flag; assert that the track plus the dot stays above the
event row and inside the band); a dashed straight line from the start to
the flag as the reference. Text in each band: the label row "aims at the
flag" / "aims 53 degrees upstream" (40 px, band colour) on the near bank
area above the river or across the band's top row, a second row "swims
1.0 m/s, current 0.8 m/s" (28 px), a right-aligned live readout "NN.N m
downstream" (28 px; gold at A's furthest point and held, "0.0 m
downstream" for B) and "NN m to the flag"; a gold event row at the band's
bottom row (496-540 px under the band top): "at the flag: 139 s" / "at
the flag: 83 s", lit as each swimmer lands. Shown at 5x speed (the clock
shows real seconds); a single run: both start 1.0 s into the video, B
lands at 17.67 s of video, A at 28.78 s; both then stand at the flag; the
title fades back in and the scene crossfades to its first frame over the
last loop_fade seconds so the last frame equals the first (a single-run
scene as sims/lifeguard). Legend row after the title: "same river, same
swimmers, 5x speed".

Day thirty-five, second slot. Chosen because "aim at the flag or aim
upstream" is a debate every river swimmer has had, the panels end
visibly differently (one track bows far downstream and crawls back
against the current, the other is a straight line that lands first), the
answer is an exact factor with a closed form, and water subjects did well
on the channel (lifeguard 681 views, tsunami 955). Question in the first
two seconds: "Swim to the flag across a river. Aim at the flag, or aim
upstream?" (or "Aim at the flag, or aim upstream?" first; keep the
question identical in the title, the hook and the payoff). Setup number:
the current is eight tenths of their swimming speed (pre-test "eight
tenths" and "eighty percent"; the width, 50 m, and the speeds go to the
overlay and the card). Payoff: aim upstream: eighty three seconds; aim at
the flag: one hundred thirty nine seconds, nearly twice as long (one
point seven times goes to the card). The 16.9 m sweep, the 53 degrees,
the 0.5 / 0.9 / 1.0 m/s variants and the "swept to 25 m, never lands" case
go to the card and the description. Whisper risks: "upstream" and
"downstream" (pre-test), "flag" (pre-test), "current" (pre-test), "swept"
(pre-test), "aims" / "aim at" (pre-test), "eighty three" and "one hundred
thirty nine" as words (pre-test), "straight" came back "stray" once (use
"a straight line" inside a sentence or avoid), avoid "do you" ("should
you aim"), avoid "pull" as a noun ("the current drags" instead), "river"
(pre-test), never "fly". Pre-test hooks with scripts/voiceover.sh and
keep the one whose question lands earliest under two seconds. Measure
every fixed text line with PIL before rendering and keep every line
under 950 px, and the title under 100 characters with no < or >. Music
seed 108. Templates: sims/deskchain (two bands, layout asserts, loop
checks, the crossfade), sims/lifeguard (top view, two runners on a shared
clock, a single run that fades back to the start, the dashed reference
line), sims/belt or sims/balloon (a texture that drifts at a set speed
without strobing). Sim name riverswim: sims/riverswim/riverswim.py,
projects/riverswim/, media/riverswim/.

## Claim (expected; the sim's numbers replace these)

Across a 50 m river running at 0.8 m/s, two swimmers at 1.0 m/s: the one
who aims 53.1 degrees upstream swims a straight line across at 0.6 m/s
and lands at the flag after 83.3 s; the one who always aims at the flag
is swept 16.9 m downstream, turns ever more into the current and lands
after 138.9 s, 1.67 times longer (w v / (v^2 - u^2) against w / sqrt(v^2
- u^2)). Narrated: the current is eight tenths of their swimming speed
(setup); aim upstream: eighty three seconds; aim at the flag: one hundred
thirty nine (payoff). Card: the question; aim upstream: 83 s; aim at the
flag: 139 s, 1.7x; the flag swimmer swept 16.9 m downstream first;
upstream heading 53 degrees, sin = 0.8; current equal to the swim speed:
never lands. Description: the model statement, the closed forms, the
tracks, the variants, the checks.

## Claim

Across a 50 m river with a uniform current of 0.8 m/s, two swimmers at
1.0 m/s relative to the water: the one who aims asin(0.8 / 1.0) = 53.130
degrees upstream swims a straight line across at 0.6000 m/s and lands at
the flag after 83.333333 s (closed form w / sqrt(v^2 - u^2) = 83.3333 s,
diff +1.2e-10 s; the track stays 0.0e+00 m from the line); the one who
always aims at the flag is swept 16.8852 m downstream first (furthest at
42.7368 s, 37.3361 m across, heading 53.130 degrees upstream there, the
same angle the other swimmer holds), turns ever more into the current
and lands after 138.888889 s (closed form w v / (v^2 - u^2) =
138.888889 s, diff +3.4e-13 s), 1.6667 times longer (v / sqrt(v^2 -
u^2)), 55.56 s longer. When the upstream swimmer lands the flag swimmer
is 49.13 m across, 11.09 m downstream, 11.13 m from the flag, heading
85.5 degrees upstream, with 55.56 s still to swim at a net 0.2118 m/s.
The half-step rerun moves the landings by -3.2e-10 s and -1.4e-12 s.
Narrated: the current is eight tenths of the swimming speed (setup); aim
upstream takes eighty three seconds; aim at the flag takes one hundred
thirty nine seconds, nearly twice as long (payoff). Card: the question;
aim upstream 83 s, aim at the flag 139 s; 1.7x longer, swept 16.9 m
downstream; upstream 53 degrees: sin = 0.8, no drift; 0.5 m/s: 58 and
67 s, 0.9: 115 and 263 s; current = swim speed: never lands.
Description: the model statement, the closed forms, the pursuit curve,
the tracks and heading marks, the variants (0.5, 0.9, 1.0 m/s and the
drifter), the checks.

## Evidence

### Measurements

media/riverswim/measure.log (`nix develop -c python3
sims/riverswim/riverswim.py --measure-only`, 2026-10-03 10:39:03 EEST,
final manifest and sim; the same physics numbers as the earlier passes
that preceded the smoke frames, after the pursuit-curve check was
restricted to r > 1 m and the card lines were shortened):

```
Sat Oct  3 10:39:03 AM EEST 2026
warning: Git tree '/home/alex/personal/seedzero' is dirty
setup: the same river in both panels, seen from above: 50 m wide with a uniform current of 0.8 m/s everywhere (the same at the banks and in the middle), flowing down the screen; two swimmers who both move at 1 m/s relative to the water (the current is 0.8 of their swimming speed, eight tenths), both starting on the near bank directly across from a flag on the far bank, both let go at the same instant; top panel the swimmer who always points straight at the flag (velocity 1 m/s toward the flag plus the current), bottom panel the swimmer who holds one fixed heading asin(u / v) = 53.13 degrees upstream of straight across; both integrated by classical RK4 at dt = 0.001 s (a half-step rerun as a check), the flag swimmer stopped within 1 mm of the flag by bisection inside the step; shown at 5x speed, one run per video with the start 1 s into the 40 s scene; drawn at 11 px per metre (550 px of water); deterministic, no seed
aim upstream (bottom panel): heading theta = asin(0.8 / 1) = 53.130 degrees upstream of straight across; the upstream part of the swimming speed v sin(theta) = 0.8000 m/s cancels the current 0.8 m/s, the across part v cos(theta) = sqrt(v^2 - u^2) = 0.6000 m/s; closed form w / sqrt(v^2 - u^2) = 83.3333 s; RK4: lands at 83.333333 s (diff +1.2e-10 s), 83334 steps, the track stays within 0.0e+00 m of the straight line (|downstream| under 1e-9 m: yes); half-step rerun (dt = 0.0005 s): lands at 83.333333 s (-3.2e-10 s); on screen 'at the flag: 83 s' = 83.3 s = eighty three seconds
aim at the flag (top panel): RK4 from the start: within 1 mm of the flag at 138.883889 s (138884 steps; there the heading is 90.000000 degrees upstream and the closing speed v - u = 0.2 m/s, so the last 1 mm take 0.0050 s); lands at 138.888889 s (closed form w v / (v^2 - u^2) = 138.888889 s, diff +3.4e-13 s); 1.6667 times the upstream swimmer's 83.3333 s (closed form v / sqrt(v^2 - u^2) = 1.6667), 55.56 s longer, nearly twice as long; on screen 'at the flag: 139 s' = 138.9 s = one hundred thirty nine seconds; 1.7 times longer on the card; furthest downstream 16.8852 m at 42.7368 s, 37.3361 m across, heading 53.130 degrees upstream (the downstream velocity -v sin(phi) + u is zero at sin(phi) = u / v, the same angle the upstream swimmer holds; closed form r = w cos^(k-1)(phi) / (1 + sin phi)^k = 21.1065 m from the flag, 16.8852 m downstream and 37.3361 m across, diffs -9.1e-10 and +5.3e-10 m; the time by quadrature 42.7368 s, diff +2.9e-09 s); swept 16.9 m downstream first = 185.7 px; the RK4 track stays within 1.9e-12 m of the pursuit curve r(phi) while more than 10 m from the flag and within 2.2e-09 m while more than 1 m from it (k = v / u = 1.25; nearer the flag the heading phi from (w - x, y) is ill-conditioned, w - x being at round-off, so the curve is not evaluated there); half-step rerun (dt = 0.0005 s): lands at 138.888889 s (-1.4e-12 s), furthest 16.885237 m at 42.736842 s (-7.8e-14 m, -6.7e-13 s)
when the upstream swimmer lands at 83.33 s the flag swimmer is 49.13 m across, 11.09 m downstream, 11.13 m from the flag, heading 85.5 degrees upstream (almost straight into the current), with 55.56 s still to swim; its net speed then is 0.2118 m/s
track of the flag swimmer (time: m across, m downstream, heading in degrees upstream): 0.0 s: 0.00 across, 0.0 down, 0.0 deg; 5.0 s: 4.99 across, 3.8 down, 4.8 deg; 10.0 s: 9.95 across, 7.1 down, 10.1 deg; 15.0 s: 14.82 across, 10.0 down, 15.9 deg; 20.0 s: 19.55 across, 12.4 down, 22.2 deg; 25.0 s: 24.06 across, 14.3 down, 28.8 deg; 30.0 s: 28.29 across, 15.6 down, 35.7 deg; 35.0 s: 32.16 across, 16.4 down, 42.6 deg; 40.0 s: 35.63 across, 16.8 down, 49.5 deg; 45.0 s: 38.65 across, 16.9 down, 56.0 deg; 50.0 s: 41.21 across, 16.6 down, 62.1 deg; 55.0 s: 43.34 across, 16.0 down, 67.5 deg; 60.0 s: 45.06 across, 15.3 down, 72.2 deg; 65.0 s: 46.42 across, 14.5 down, 76.2 deg; 70.0 s: 47.47 across, 13.6 down, 79.5 deg; 75.0 s: 48.26 across, 12.7 down, 82.2 deg; 80.0 s: 48.84 across, 11.7 down, 84.4 deg; 85.0 s: 49.26 across, 10.8 down, 86.0 deg; 90.0 s: 49.54 across, 9.8 down, 87.3 deg; 95.0 s: 49.73 across, 8.8 down, 88.3 deg; 100.0 s: 49.85 across, 7.8 down, 88.9 deg; 105.0 s: 49.93 across, 6.8 down, 89.4 deg; 110.0 s: 49.97 across, 5.8 down, 89.7 deg; 115.0 s: 49.99 across, 4.8 down, 89.8 deg; 120.0 s: 50.00 across, 3.8 down, 89.9 deg; 125.0 s: 50.00 across, 2.8 down, 90.0 deg; 130.0 s: 50.00 across, 1.8 down, 90.0 deg; 135.0 s: 50.00 across, 0.8 down, 90.0 deg; 138.9 s: 50.00 across, 0.0 down, 90.0 deg
track of the upstream swimmer (time: m across, m downstream, heading): 0.0 s: 0.00 across, 0.0 down, 53.1 deg; 5.0 s: 3.00 across, 0.0 down, 53.1 deg; 10.0 s: 6.00 across, 0.0 down, 53.1 deg; 15.0 s: 9.00 across, 0.0 down, 53.1 deg; 20.0 s: 12.00 across, 0.0 down, 53.1 deg; 25.0 s: 15.00 across, 0.0 down, 53.1 deg; 30.0 s: 18.00 across, 0.0 down, 53.1 deg; 35.0 s: 21.00 across, 0.0 down, 53.1 deg; 40.0 s: 24.00 across, 0.0 down, 53.1 deg; 45.0 s: 27.00 across, 0.0 down, 53.1 deg; 50.0 s: 30.00 across, 0.0 down, 53.1 deg; 55.0 s: 33.00 across, 0.0 down, 53.1 deg; 60.0 s: 36.00 across, 0.0 down, 53.1 deg; 65.0 s: 39.00 across, 0.0 down, 53.1 deg; 70.0 s: 42.00 across, 0.0 down, 53.1 deg; 75.0 s: 45.00 across, 0.0 down, 53.1 deg; 80.0 s: 48.00 across, 0.0 down, 53.1 deg; 83.3 s: 50.00 across, 0.0 down, 53.1 deg
heading of the flag swimmer against time (degrees upstream of straight across, rising from 0 at the start to 90 at the flag, monotone: yes): 30 degrees at 25.89 s (24.84 m across, 14.53 m downstream); 45 degrees at 36.70 s (33.38 m across, 16.62 m downstream); 60 degrees at 48.24 s (40.36 m across, 16.70 m downstream); 75 degrees at 63.45 s (46.03 m across, 14.80 m downstream); 85 degrees at 81.74 s (49.00 m across, 11.41 m downstream); 89 degrees at 100.68 s (49.87 m across, 7.64 m downstream); it is swept downstream while the heading is under 53.13 degrees (until 42.74 s) and crawls back up the far bank after; it reaches 49.9 m across at 102.82 s and 49.99 m across at 116.13 s
for the description: current 0.5 m/s: aim upstream 30.0 degrees, across at 0.8660 m/s, lands at 57.74 s (closed form 57.7350 s, diff -7.1e-11); aim at the flag lands at 66.67 s (closed form 66.6667 s, diff +2.4e-12), 1.15 times longer, swept 9.62 m downstream at 34.6 s (closed form 9.6225 m, diff -7.5e-06); current 0.9 m/s: aim upstream 64.2 degrees, across at 0.4359 m/s, lands at 114.71 s (closed form 114.7079 s, diff -1.5e-10); aim at the flag lands at 263.16 s (closed form 263.1579 s, diff -2.5e-11), 2.29 times longer, swept 20.11 m downstream at 50.3 s (closed form 20.1102 m, diff -1.7e-06); current 1 m/s, equal to the swim speed: aim upstream needs asin(1) = 90 degrees, straight into the current, across at 0.0 m/s: swimming in place, it never crosses; aim at the flag never lands: after 1200 s it is 50.0000 m across and 25.0000 m downstream, 25.0000 m from the flag, moving at 3.6e-12 m/s (the limit point is (w, w / 2) = (50, 25) m, half the width downstream: r(phi) = w / (1 + sin phi) at k = 1; it is within 1 mm of the limit from 283.0 s and 9.0e-11 m from it at 1200 s; the distance to the flag never drops under 25.0000 m); the drifter who points straight across and lets the current take it: lands 40.0 m downstream after 50.0 s (closed form w / v = 50.0 s and u w / v = 40.0 m)
schedule (video time, 5x speed): both start at 1 s; the flag swimmer is furthest downstream at 9.55 s (16.9 m, the gold furthest rows light in both bands); the upstream swimmer lands at 17.67 s (its event row lights) with the flag swimmer 11.1 m from the flag; the flag swimmer passes 49.9 m across at 21.56 s and lands at 28.78 s (its event row lights); both stand at the flag to 39.50 s; the title fades back in and the scene crossfades to its first frame over 39.50 to 40.00 s; title until 3 s; payoff card from 27.8 s; the current's chevrons drift 44.0 px per video second (4 m/s of video) on a 55 px period, 32 periods in 40 s (exact: True), so the water phase at the last frame equals the first; each chevron is smeared over one frame's travel (0.733 px)
text widths (the on-screen strings verbatim): overlay@34 921 px 'river 50 m | current 0.8 m/s | 5x speed | no seed', title line 1@56 489 px 'Aim at the flag,', title line 2@56 555 px 'or aim upstream?', legend@40 857 px 'same river, same swimmers, 5x speed', clock@28 350 px '123.4 s after the start', clock before@28 251 px 'before the start', clock landed@28 382 px '138.9 s: both at the flag', label flag@40 354 px 'aims at the flag', sublabel flag@28 485 px 'swims 1.0 m/s, current 0.8 m/s', furthest flag@28 463 px 'furthest: 16.9 m downstream', event flag@40 385 px 'at the flag: 139 s', label upstream@40 601 px 'aims 53 degrees upstream', sublabel upstream@28 485 px 'swims 1.0 m/s, current 0.8 m/s', furthest upstream@28 444 px 'furthest: 0.0 m downstream', event upstream@40 357 px 'at the flag: 83 s', downstream@28 314 px '16.9 m downstream', to the flag@28 252 px '50 m to the flag', heading@28 474 px 'heading 90 degrees upstream', start@24 65 px 'start', flag@24 51 px 'flag', payoff line 1@40 756 px 'aim at the flag, or aim upstream?', payoff line 2@40 914 px 'aim upstream 83 s, aim at the flag 139 s', payoff line 3@40 877 px '1.7x longer, swept 16.9 m downstream', payoff line 4@40 907 px 'upstream 53 degrees: sin = 0.8, no drift', payoff line 5@40 902 px '0.5 m/s: 58 and 67 s, 0.9: 115 and 263 s', payoff line 6@40 787 px 'current = swim speed: never lands'
row check: left and right columns end and start at x 641 / 726 (label row, gap 85 px), 525 / 788 (second row, gap 263 px), 514 / 577 (third row, gap 63 px); the rows end 136 px under the band top; the river spans 150 to 480 px under the band top, the water x 265 to 815 (50 m at 11 px/m) between the banks x 40 to 265 and 815 to 1040; the start at x 265, 250 px under the band top, the flag at x 815 with its pole up to 214 px and its pennant to x 841; the flag swimmer's track bows to 435.7 px under the band top (185.7 px downstream of the line) and its dot to 441.7 px, above the water's bottom row 480 and the event row (spans 496 to 540 px under the band top, x 347 to 733, widest 385 px); the heading tick reaches 224 px at most (straight upstream), under the rows; the dots stay between x 260 and 826; the 'start' label spans x 186 to 251 on the near bank and 'flag' x 834 to 885 on the far bank; each band is 550 px tall (y 330 to 880 and 880 to 1430); the caption band starts at y 1440; the card runs from y 1572 to 1832; the title rows end at y 280 and the overlay band ends at y 130
exit 0
Sat Oct  3 10:39:07 AM EEST 2026
```

Checks the brief asked for, against the log:

- B's heading asin(u / v) = 53.13 degrees: passed, 53.130 degrees.
- v sin(theta) = 0.8 m/s cancels the current, across at sqrt(v^2 - u^2)
  = 0.6 m/s: passed, 0.8000 and 0.6000 m/s.
- B closed form 83.333 s against RK4: passed, 83.333333 s against
  83.3333 s, diff +1.2e-10 s, 83334 steps.
- B's track stays on the line, |downstream| under 1e-9 m: passed,
  0.0e+00 m.
- A integrated with RK4 at 1e-3 s and stopped within 1 mm of the flag:
  passed, within 1 mm at 138.883889 s after 138884 steps (heading
  90.000000 degrees there, closing speed v - u = 0.2 m/s, so the last
  1 mm take 0.0050 s), lands at 138.888889 s.
- A closed form 138.889 s: passed, 138.888889 s against 138.888889 s,
  diff +3.4e-13 s.
- Ratio v / sqrt(v^2 - u^2) = 1.6667: passed, 1.6667 (closed form
  1.6667); 55.56 s longer.
- A's furthest downstream point 16.89 m at 42.7 s: passed, 16.8852 m at
  42.7368 s, 37.3361 m across, heading 53.130 degrees upstream; the
  pursuit curve r = w cos^(k-1)(phi) / (1 + sin phi)^k gives 21.1065 m
  from the flag, 16.8852 m downstream and 37.3361 m across (diffs
  -9.1e-10 and +5.3e-10 m); the time by Simpson quadrature 42.7368 s
  (diff +2.9e-09 s).
- A when B lands at 83.33 s (49.13 m across, 11.09 m downstream, 11.13 m
  from the flag, heading 85.5 degrees): passed, 49.13 / 11.09 / 11.13 m,
  85.5 degrees, 55.56 s still to swim, net speed 0.2118 m/s.
- A's heading swings from 0 to 90 degrees upstream: passed, monotone;
  30 / 45 / 60 / 75 / 85 / 89 degrees at 25.89 / 36.70 / 48.24 / 63.45
  / 81.74 / 100.68 s; swept downstream until 42.74 s, then crawls up the
  far bank; 49.9 m across at 102.82 s, 49.99 m at 116.13 s.
- Half-step rerun agreement better than 1e-3 s on both landings:
  passed, -3.2e-10 s (B) and -1.4e-12 s (A); A's furthest point moves
  -7.8e-14 m and -6.7e-13 s.
- Current 0.5 m/s (B 57.74 s at 30.0 degrees, A 66.67 s, swept 9.62 m):
  passed, 30.0 degrees, 0.8660 m/s across, 57.74 s (closed form 57.7350
  s, diff -7.1e-11), 66.67 s (closed form 66.6667 s, diff +2.4e-12),
  1.15 times, swept 9.62 m at 34.6 s (closed form 9.6225 m).
- Current 0.9 m/s (B 114.71 s at 64.2 degrees, A 263.16 s, swept 20.11
  m): passed, 64.2 degrees, 0.4359 m/s across, 114.71 s (closed form
  114.7079 s), 263.16 s (closed form 263.1579 s), 2.29 times, swept
  20.11 m at 50.3 s (closed form 20.1102 m).
- Current 1.0 m/s (B at 90 degrees swims in place; A settles 25.0 m
  downstream and 50 m across, 1 mm short after 1,200 s acceptable):
  passed with a tighter result: B needs asin(1) = 90 degrees and 0.0 m/s
  across; A after 1200 s is 50.0000 m across, 25.0000 m downstream,
  25.0000 m from the flag, moving 3.6e-12 m/s; it is within 1 mm of the
  limit (50, 25) from 283.0 s and 9.0e-11 m from it at 1200 s; the
  distance to the flag never drops under 25.0000 m.
- The drifter (points straight across, lets the current take it) lands
  40.0 m downstream after 50.0 s: passed, 40.0 m after 50.0 s (closed
  form w / v = 50.0 s, u w / v = 40.0 m).
- Both tracks at 5 s intervals (across, downstream, heading): printed.
- Schedule in video time: printed; start 1 s, B lands 17.67 s, A lands
  28.78 s as the brief asks; A's furthest point at 9.55 s; both at the
  flag to 39.50 s, fade 39.50-40.00 s.
- Text widths: printed with the strings verbatim; every line under 950
  px, the widest the overlay at 921 px.
- Layout clearances: printed; A's track bows to 435.7 px and its dot to
  441.7 px under the band top, above the water's bottom row (480) and
  the event row (496-540); the heading tick reaches 224 px at most,
  under the text rows (end 136); the dots stay in x 260-826.
- Added beyond the brief: A's RK4 track stays within 1.9e-12 m of the
  pursuit curve while more than 10 m from the flag and 2.2e-09 m while
  more than 1 m from it.

### Production

Sim and manifest. sims/riverswim/riverswim.py: classical RK4 with
bisection inside the step on the stop event (80 iterations), the
half-step rerun, the closed forms, the pursuit curve r(phi) and the
Simpson quadrature for the furthest-point time, measure() printing every
line above with asserts, and the renderer (2x supersampled band layers,
the drifting smeared chevron water texture, the single-run crossfade).
projects/riverswim/manifest.json: seed 0 (unused: deterministic, no
seed), fps 60, width 50 m, current 0.8 m/s, swim 1.0 m/s, dt 0.001 s,
stop 0.001 m, description currents 0.5 / 0.9 / 1.0 m/s, never-lands run
1200 s, table step 5 s, heading marks 30 / 45 / 60 / 75 / 85 / 89
degrees, speedup 5, release at 1.0 s, scene 40 s, 11 px/m, chevron
period 5 m (55 px) in 5 columns, title "Aim at the flag,|or aim
upstream?" until 3.0 s, payoff card from 27.8 s with a 0.6 s rise, six
card lines, loop fade 0.5 s, music seed 108, music gain 0.18, voice
offset 0.6 s, caption y 0.75, overlay "river 50 m | current 0.8 m/s |
5x speed | no seed".

Layout. Overlay band y 96-130; title rows y 190 / 252 (56 px) until
3.0 s with a 0.4 s fade out; legend "same river, same swimmers, 5x
speed" at y 236 and the clock at y 290 ("before the start", "NN.N s
after the start", "138.9 s: both at the flag") fading in over 0.4 s as
the title leaves. Two bands, y 330-880 (A, "aims at the flag", coral)
and 880-1430 (B, "aims 53 degrees upstream", teal). Each band: label
row at 40 px under the band top (40 px band colour, left) with the live
"NN.N m downstream" (28 px, right); second row at 84 px: "swims 1.0
m/s, current 0.8 m/s" (left) and "NN m to the flag" (right); third row
at 120 px: "heading NN degrees upstream" (left) and the gold held
"furthest: 16.9 m downstream" / "furthest: 0.0 m downstream" (right),
lit in both bands from A's furthest point (9.55 s of video). The river
spans 150-480 px under the band top: banks x 40-265 and 815-1040 as
lighter slabs with edge lines, water x 265-815 (50 m at 11 px/m) with
five columns of faint chevrons drifting down the screen at 44 px per
video second (55 px period, 32 periods in 40 s, so the water phase
returns to the first frame), each smeared over one frame's travel
(0.733 px). The start at x 265, 250 px under the band top (ring plus
"start" label on the near bank); the flag at x 815 (gold pole to 214 px
and pennant to x 841, "flag" label on the far bank); a dashed reference
line between them. The swimmer a 10 px dot with a 26 px heading tick and
a trail from 0.05 s samples in the band colour; a gold dot at A's
furthest point; a ring once landed. Gold event row centred at x 540,
518 px under the band top (spanning 496-540): "at the flag: 139 s" /
"at the flag: 83 s" as each lands. Caption band y 1440-1530; the card
from y 1572 at 48 px pitch to 1832.

Hook pre-tests (media/riverswim/hooks/pretest.log, scripts/voiceover.sh
round trip, onsets by silencedetect; video time = voice time + 0.6 s):

- hook1 "Aim at the flag, or aim upstream? Two swimmers cross a river
  to a flag. Both swim at the same speed, and the current is eight
  tenths of that speed.": FAIL, "tenths" came back "tenth s".
- hook2 "Swim to the flag across a river. Aim at the flag, or aim
  upstream? ...": ok 7.88 s; the question starts at 1.76 s of voice =
  2.36 s of video (over two seconds).
- hook3 "A river, a flag on the far bank. Aim at the flag, or aim
  upstream? ...": ok 7.94 s; the question at 2.19 s of voice = 2.79 s
  of video.
- hook4 "Swim to the flag. Aim at the flag, or aim upstream? Two
  swimmers, same speed. The current runs at eighty percent of their
  swimming speed.": FAIL, "swimmers" came back "sw immers".
- words list (upstream, downstream, aim upstream, aim at the flag, the
  flag, the current, the current drags, swept downstream, swept sixteen
  meters downstream, aims at the flag, aims upstream, eighty three
  seconds, one hundred thirty nine seconds, the river, across the
  river, eight tenths, eighty percent, a straight line across, it lands
  first, nearly twice as long, fifty meters wide, holds that angle,
  crawls up the far bank, turns into the current, he lands first, she
  is still out there): run 1 FAIL with one "current" dropped, run 2 FAIL
  only on "she" -> "sheet"; every other word passed both times.
- words2 ("The current is eight tenths of their swimming speed. The
  current drags the top swimmer down the river. Two swimmers, same
  speed. Both swimmers start together. The current drags. Into the
  current. Against the current. The upstream angle cancels the current.
  Eight tenths. The other holds that angle."): FAIL only on "The other"
  -> "ladder"; "eight tenths" passed twice, "drags" and "cancels the
  current" passed.
- hook5 (hook1 text again): FAIL, "tenths" -> "tenth s" again, so "eight
  tenths of that speed" was dropped.
- hook6 "Aim at the flag, or aim upstream? Two swimmers cross a river
  to a flag. Same swimming speed for both. The current is eight tenths
  of it.": ok 7.65 s; the question is the first sentence, at 0.60 s of
  video. Chosen (the context-first hooks put the question past two
  seconds).

Narration (projects/riverswim/narration.txt, 109 words, question first
at 0.60 s of video, the question identical in title, hook and payoff):
"Aim at the flag, or aim upstream? Two swimmers cross a river. Same
swimming speed for both. The current is eight tenths of it. On top, the
swimmer always points at the flag. The current drags it down the river.
Below, the swimmer holds one fixed angle upstream. The upstream angle
cancels the current. The track is a straight line, and it lands first.
On top, the swimmer turns more and more into the current, then crawls
up the far bank. So, aim at the flag, or aim upstream? Aim upstream
takes eighty three seconds. Aim at the flag takes one hundred thirty
nine seconds. Nearly twice as long."

Voice (media/riverswim/voice.log). Pass 1 (10:36:41, 112 words, kept at
media/riverswim/narration-pass1.txt): ok, 35.13 s, no mishearing; but
its order ("On top ... Below ... The current drags the top swimmer ...
Below, the upstream angle ...") played the drag sentence after B's
introduction and ended at 35.73 s of video, late against the picture.
Pass 2 (10:37:56, the final text above, 109 words: the drag sentence
moved right after the top swimmer's sentence, B's two sentences joined,
"the top swimmer" -> "it"): ok, 33.59 s, ends at 34.19 s of video. No
mishearing in either pass; two passes used of six.

Timing (media/riverswim/timing.log, scripts/voice-timing.py, video
time): 0.60-1.60 "Aim at the flag."; 1.60-4.24 "or aim upstream, two
swimmers cross a river."; 4.24-6.11 "Same swimming speed for both.";
6.11-7.81 "The current is eight tenths of it."; 7.81-8.51 "On top";
8.51-17.52 the points-at-the-flag, drags, holds-one-fixed-angle and
cancels-the-current sentences (fine pause map at d = 0.10: pauses at
10.53-10.70, 12.26-12.41, 12.78-12.94, 15.23-15.37, so "The current
drags it down the river" plays about 10.7-12.3 s); 17.52-20.29 "The
track is a straight line, and it lands first."; 20.29-21.04 "On top";
21.04-26.72 "the swimmer turns more and more into the current, then
crawls up the far bank. So, aim at the flag"; 26.72-29.87 "or aim
upstream? Aim upstream takes eighty three seconds." (pause 27.66-27.86
between them); 29.87-34.19 "Aim at the flag takes one hundred thirty
nine seconds, nearly twice as long." (pause 32.48-32.70 before "nearly").
Voice 33.59 s, ends 34.19 s of video.

Schedule and sync (video time). Start 1.00 s under the caption "Aim at
the flag, or" (0.60-1.99); A's furthest point 9.55 s, the gold rows
light, while "The current drags it down the river" plays 10.7-12.3 s;
B lands 17.67 s (event row "at the flag: 83 s") under "The track is a
straight line, and it lands first" 17.65-20.14 s; A reaches 49.9 m
across at 21.56 s and crawls up the far bank under "turns more and
more into the current, then crawls up the far bank" 21.15-25.1 s; the
question repeats 25.25-27.66 s; the card rises from 27.80 s (full at
28.40 s), A lands 28.78 s (event row "at the flag: 139 s"), "eighty
three" is spoken 28.80-29.43 s and "one hundred thirty nine seconds"
30.99-32.70 s with both event rows and the card on screen; "Nearly
twice as long" 32.70-33.99 s; both stand at the flag to 39.50 s; title
back and crossfade to the first frame 39.50-40.00 s.

Smoke frames (`--frames`, media/riverswim/smoke-T.png): rendered at
0.0, 1.5, 2.0, 3.5, 9.55, 17.7, 21.0, 25.5, 28.9, 35.0, 39.7, 39.983 s;
viewed 0.0 (title, overlay, both swimmers at the start with heading
ticks: A straight across, B 53 degrees upstream), 1.5 (A moving, trail
starting), 3.5 (legend and clock "12.5 s after the start", title gone),
9.55 (A at its furthest point, gold dot, gold furthest rows in both
bands, A's tick at 53 degrees), 17.7 (B landed with its ring and "at
the flag: 83 s", A at 86 degrees heading 11.1 m downstream), 25.5 (card
rising, A 3 m to the flag), 28.9 (both at the flag, both event rows,
clock "138.9 s: both at the flag", card full), 39.7 (mid-fade: ghost of
the title over the legend, scene blending), 39.983 (equal to the first
frame). 2.0, 21.0 and 35.0 were rendered but not viewed.

Footage render (media/riverswim/render.log, 10:39:07-10:39:52, 12
workers): loop check 0 px (max channel difference 0); fade check: the
last live frame before the fade (39.483 s) differs from the first in
132643 px (max 229) and is blended into the first frame over 30 frames;
the mid-fade frame differs in 120402 px (max 107); loop step 0 px;
footage 40.00 s at 60 fps, md5 208852d3b69b51acb84fb69ea480b51f.

Compose (media/riverswim/compose.log, 10:39:52-10:40:05): music seed
108, 40.00 s; "captions: 21 pauses detected, 21 matched, max chunk
start shift 0.520 s against word-count timing"; contact sheet 8x5;
final.mp4 40.000000 s; preview.mp4 40.066667 s; exit 0.

Text widths (PIL getlength, from measure.log, all under 950 px):
overlay@34 921, title lines@56 489 / 555, legend@40 857, clock@28 350 /
251 / 382, label flag@40 354, sublabel@28 485, furthest flag@28 463,
event flag@40 385, label upstream@40 601, furthest upstream@28 444,
event upstream@40 357, downstream@28 314, to the flag@28 252,
heading@28 474, start@24 65, flag@24 51, payoff lines@40 756 / 914 /
877 / 907 / 902 / 787. Row check: label row columns end / start at x
641 / 726 (gap 85 px), second row 525 / 788 (263 px), third row 514 /
577 (63 px).

### Local QA

Frames viewed at full resolution (media/riverswim/qa-T.png from
final.mp4):

- 0.00 s: overlay "river 50 m | current 0.8 m/s | 5x speed | no seed",
  title in two rows, both bands with banks, chevrons, dashed line, start
  ring and flag, both swimmers at the start with heading ticks; no
  caption, no card, no legend.
- 1.0 s: caption "Aim at the flag, or"; both swimmers on the start line,
  "0.0 m downstream", "50 m to the flag", headings 0 and 53 degrees.
- 2.1 s: caption "aim upstream?"; A 4.1 m downstream heading 5 degrees,
  45 m to the flag; B on the line, 47 m to the flag.
- 17.7 s: legend and clock "83.5 s after the start"; B landed with its
  ring and gold "at the flag: 83 s"; A 11.1 m downstream heading 86
  degrees with the gold furthest dot on its track and the gold furthest
  rows in both bands; caption "The track is a".
- 28.2 s: clock "136.0 s after the start"; A 1 m to the flag heading 90
  degrees, crawling up the far bank; the card rising in dim gold;
  caption "Aim upstream takes".
- 29.6 s: both at the flag, both rings, "at the flag: 139 s" and "at the
  flag: 83 s", clock "138.9 s: both at the flag", the card full with its
  six lines; caption "seconds.".
- 39.983 s: title back, identical to 0.00 s; no caption, no card.

No text touches the frame edges in any frame. sheet.png: 8x5 tiles,
one run (A's track bows downstream and curves back, B's a straight
line), captions under the tiles, the card from tile 28, both event rows
lit from tile 29, the first and last tiles alike.

Question timing: the caption "Aim at the flag, or" shows 0.600-1.986 s
and "aim upstream?" 1.986-2.690 s; the voice starts at 0.60 s with the
question. Captions (media/riverswim/captions.filter): 36 chunks of at
most 20 characters, the text equal to the narration word for word,
spans from 0.600 to 34.188 s; 21 of 21 pauses matched.

Band signalstats on footage.mp4: rows 96-130 (overlay band) YMAX 28 on
2396 frames and 27 on 4 (background only, no stray drawing); rows
1440-1530 (caption band) YMAX 28 / 27 and YMIN 28 / 27 (background
only). Loop: render loop check 0 px; codec-only noise on final.mp4
frame 2399 against frame 0: 26939 px over 8 levels, 2086 over 24, max
69 at x 269 y 582 (a title letter edge), mean 0.444; frame 2398: 77638
/ 2296 / 69 / 0.754; footage.mp4 frame 2399: 12009 / 738 / max 57 /
0.288.

ffprobe final.mp4: h264 1080x1920, 60/1 fps, 2400 frames, aac 22050 Hz
mono, duration 40.000000 s, 3983093 bytes, atom order ftyp moov free
mdat (faststart). md5sum final.mp4 fb7c8a6f986f45df38bdee8d575d6516;
footage.mp4 208852d3b69b51acb84fb69ea480b51f; voice.wav
0caa92d8cfb8e71d18c664ab36692ce5.

Narrated numbers against measure.log: "eight tenths" (setup: "the
current is 0.8 of their swimming speed, eight tenths"); "eighty three
seconds" ("on screen 'at the flag: 83 s' = 83.3 s = eighty three
seconds"); "one hundred thirty nine seconds" ("'at the flag: 139 s' =
138.9 s = one hundred thirty nine seconds"); "nearly twice as long"
(printed on the aim-at-the-flag line). Card: 83 s, 139 s, 1.7x, 16.9 m,
53 degrees, sin = 0.8, 0.5 m/s: 58 and 67 s, 0.9: 115 and 263 s (58 /
67 / 115 / 263 are the printed 57.74 / 66.67 / 114.71 / 263.16 s
rounded; the card strings are printed verbatim in the text-widths
line), never lands. Metadata number check by script: 95 distinct
numbers in the description, every one present in measure.log (one
"1.67" found missing and changed to the printed 1.6667).

### Metadata

projects/riverswim/metadata.json. Title (98 characters, ASCII, no < or
>): "Aim at the flag, or aim upstream? Aim upstream: 83 s. Aim at the
flag: 139 s, nearly twice as long". Description 4746 characters: the
question, the model statement (river, current, both swimmers, the
closed forms, the pursuit curve, RK4 and the stop rule, 5x speed, no
seed), "Measured:" with twelve bullets (both landings against the
closed forms, the furthest point, the pursuit-curve check, A when B
lands, the heading marks, the track at 20 s intervals, the 0.5 / 0.9 /
1.0 m/s variants, the drifter, the checks), the "Why:" paragraph
(closing speed 0.2 m/s near the flag, 0.8 m/s spent cancelling the
current, ratio 1.6667 growing without bound as u -> v), "Rerun
sims/riverswim/riverswim.py with projects/riverswim/manifest.json and
you get these numbers exactly.", "Made end to end by an AI agent:
simulation, footage, voice, music, and edit." Tags (12): aim at the
flag or aim upstream, swim across a river, river crossing, river
current, pursuit curve, swimming upstream, ferry angle, vector
addition, physics, physics visualization, simulation, shorts.
categoryId 27, privacyStatus private, containsSyntheticMedia true,
selfDeclaredMadeForKids false.

### Deviations from the brief

- Hook: the question-first form "Aim at the flag, or aim upstream? Two
  swimmers cross a river. Same swimming speed for both. The current is
  eight tenths of it." (the brief allowed either order); the
  context-first hooks put the question at 2.36-2.79 s of video.
- Setup phrasing: "eight tenths of it" instead of "eight tenths of
  their swimming speed"; whisper returned "tenth s" twice for "eight
  tenths of that speed" while "eight tenths" alone and "eight tenths of
  it" passed. The number is the same.
- Narration reordered after a passing pass 1 (112 words) to pass 2
  (109 words) so that "The current drags it down the river" plays over
  A's sweep and "it lands first" over B's landing.
- The live "NN.N m downstream" readout stays in text colour; the brief's
  "gold at A's furthest point and held" is realised as a third text row
  per band, gold "furthest: 16.9 m downstream" (A) and "furthest: 0.0 m
  downstream" (B), lit from A's furthest point and held, plus a gold
  dot on A's track at that point and a live "heading NN degrees
  upstream" row on the left.
- The river occupies rows 150-480 under the band top (not the whole
  band) so that the three text rows (to 136 px) and the event row
  (496-540) sit on background.
- Card lines shortened for width (the first drafts of lines 3-6
  measured 1097-1434 px): "1.7x longer, swept 16.9 m downstream",
  "upstream 53 degrees: sin = 0.8, no drift", "0.5 m/s: 58 and 67 s,
  0.9: 115 and 263 s", "current = swim speed: never lands".
- The pursuit-curve comparison is restricted to r > 1 m (and reported
  for r > 10 m) because phi = atan2(y, w - x) is ill-conditioned next
  to the flag, where w - x is at round-off; the first assert at every
  point failed with 2.9e-02 m for that reason, not from the integrator.
- The u = v run settles within 9.0e-11 m of (50, 25) at 1200 s (within
  1 mm from 283.0 s), tighter than the "1 mm short after 1,200 s" the
  brief accepted.
- Title is the question alone in two rows; the river context goes to
  the overlay ("river 50 m | current 0.8 m/s | 5x speed | no seed") and
  the legend.
- Smoke frames 2.0, 21.0 and 35.0 s were rendered but not viewed; the
  QA frames at 2.1 and 28.2 s and the contact sheet cover those times.

## Niche note

[produced 2026-10-03 as "Aim at the flag, or aim upstream? Aim
upstream: 83 s. Aim at the flag: 139 s, nearly twice as long"; measured
a 50 m river with a uniform 0.8 m/s current and two swimmers at 1.0 m/s
(RK4 at 1e-3 s with a half-step rerun, no seed): aim 53.130 degrees
upstream lands at 83.333333 s (closed form 83.3333 s, 0.0 m off the
line); aim at the flag lands at 138.888889 s (closed form 138.888889
s), 1.6667 times longer, swept 16.8852 m downstream at 42.7368 s with
heading 53.130 degrees there, at 49.13 m across and 11.09 m downstream
when the other lands; 0.5 m/s: 57.74 against 66.67 s, swept 9.62 m; 0.9
m/s: 114.71 against 263.16 s, swept 20.11 m; current = swim speed:
never lands, within 1 mm of (50, 25) from 283.0 s; the drifter 40.0 m
after 50.0 s; task 20261003-101704]

## Upload

- Orchestrator gate passed at 2026-10-03T10:53:41+03:00 (frames, sheet, ffprobe, md5 fb7c8a6f986f45df38bdee8d575d6516, metadata, captions, measure.log against /tmp/day35 closed forms).
- Upload attempt 2 of 5 for the quota day that began 2026-10-03T10:00 EEST, recorded at 2026-10-03T10:55:07+03:00 before starting scripts/yt-upload.py riverswim (one attempt, coinrecord, on record since the boundary).
- Uploaded private as bmuZD5MV7gk at 2026-10-03T10:55:10+03:00 (scripts/yt-upload.py, channels.list 1 unit + videos.insert 1,600 units; media/riverswim/upload.log).
- scripts/yt-qa.py riverswim bmuZD5MV7gk --wait --publish in the foreground at 10:55:14: gate 15 of 15 (processed, hd, 1080x1920, title, description and tags match, category 27, not made for kids, PT41S, private before publish), published at 2026-10-03T10:56:02+03:00, re-read public (media/riverswim/publish.log); 55 units.
- Published: https://youtu.be/bmuZD5MV7gk

### Quota

- Attempt 2 of 5 for the quota day that began 2026-10-03T10:00 EEST; 1,656 units (1 + 1,600 + 55); day total after this attempt 3,311 of 10,000.
