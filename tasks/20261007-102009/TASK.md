# Produce short: banked curve on ice, flat road beside a 20 degree bank at 50 km/h, which one keeps the car in its lane

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day39

## Goal

Backlog idea (trend research 2026-10-07, task 20261007-100305, pillar 2
chaos and physics, everyday mechanics; read the full "Banked curve on
ice" bullet under "Added by trend research 2026-10-07" in docs/niche.md):
the same car at the same speed round the same icy curve, on a flat road
beside a banked road; the flat car leaves its lane, the banked one holds.

Orchestrator notes (2026-10-07; closed forms in /tmp/day39/closed.py with
the log /tmp/day39/closed.log, research script
/tmp/day39/research/bank.py with bank.log; g = 9.807 m/s^2). Read
/tmp/day39/producer-conventions.md first. The model: a point car at v =
50.00 km/h = 13.889 m/s entering a curve whose lane centre line has
radius R = 50 m, in a lane 7 m wide (edges 3.5 m either side of the
centre line), on ice with grip mu = 0.1; the speed is held constant
(say so: chosen). Top band, the "no" case: the FLAT road: holding the
curve needs v^2 / R = 3.858 m/s^2 = 0.3934 g sideways and the tyres can
give 0.1 g; with full-grip steering (the swerve model, say so) the car
follows a circle of radius v^2 / (mu g) = 196.70 m and crosses the
outer lane edge 3.5 m out after 22.05 m of travel, 1.5876 s, 25.3
degrees round the curve; then it keeps going off the road (draw it
leaving the band's lane and stop it at the run end). Bottom band, the
"yes" case: the road BANKED at theta = 20 degrees (the outer edge
higher): the grip needed is (v^2 cos theta / R - g sin theta) / (g cos
theta + v^2 sin theta / R) = 0.0257 outward, the road push N = 1.0742
weights, so the car holds its lane with 0.1 of grip to spare. Integrate
the flat slide with RK4 at dt = 1e-4 s (x, y on the plane at constant
speed, lateral acceleration mu g toward the centre of the lane's curve
as the steering demands), bisection for the lane-edge crossing, a
half-step rerun agreeing within 1e-9 s, as a check against the 196.70 m
circle; for the banked car integrate the lane-following motion (it
stays on the centre line) and print the force balance per kilogram in
the road frame (normal and along-slope components, the grip used
against the grip available), the table at 0.25 s steps (both cars'
offset from the lane centre line and angle round the curve) and the
description variants.

Checks, not facts (the sim must print and compare; state them as checks):
needed 3.858 m/s^2 = 0.3934 g against 0.1 g; flat radius 196.70 m; over
the lane edge after 22.05 m, 1.5876 s, 25.3 deg; banked grip needed
0.0257, N 1.0742 weights; flat limit sqrt(mu g R) = 25.21 km/h; no-grip
design speed sqrt(g R tan theta) = 48.09 km/h; the banked window with
grip 0.1 is 40.23 to 55.32 km/h (below it the car slides down the bank,
above it up and out: print 30, 40, 60 and 70 km/h on the bank; 60 and
70 slide out, 30 slides down, 40 is just below the window); grips 0.3 /
0.5 / 0.8 give flat limits 43.7 / 56.4 / 71.3 km/h; the bank needed to
hold 50 km/h with grip 0.1 is 15.76 deg, with no grip 21.47 deg. Print
the schedule in video time, the text widths and the layout clearances.

Drawing: two-band layout (sims/deskchain style, read it whole; sims/
swerve draws a top-down car, lane edges and an exit mark; sims/braking
and sims/hump draw road scenes), TOP-DOWN view in each band with the
curve bending to the left: the lane as two edge arcs 7 m apart around
the 50 m centre line (about 30 px per metre, so the lane is 210 px wide
and the drawn arc covers roughly 25 to 35 degrees of the curve across
the band: the entry straight at the bottom right of the band and the
curve sweeping up and left; assert the arcs stay inside the band), the
car as a small rounded rectangle (about 24 by 44 px) turned to its
heading, with a thin trail. The flat band shows the 196.7 m circle the
car actually follows as a faint dashed arc and a gold mark at the edge
crossing with "over the edge at 1.59 s" (24 px). Each band carries a
small cross-section inset (about 200 by 90 px, in a corner clear of the
lane): a flat line with the car on it and a dashed arrow for the
missing sideways push (top); the road drawn at 20 degrees with the car
on it and the road's push arrow in gold tilted toward the centre
(bottom). Label rows (40 px, coloured): "flat road, grip 0.1" (coral)
and "banked 20 deg, grip 0.1" (teal). Readouts (28 px): left column
"needs 0.39 g sideways" (top) / "needs 0.026 g of grip" (bottom) and
the clock; right column "N.N m off the lane centre" and "speed 50
km/h". Gold event rows: top "flat: over the edge at 1.59 s" (lit at the
crossing and held), bottom "banked: holds its lane" (lit when the flat
car crosses, so both rows light together, and held). Shown at 1/2
speed: cycle 10 s (600 frames): entry at 0.5 s of the cycle, the flat
car over the edge at 0.5 + 2 * 1.5876 = 3.675 s, both cars run on to
4.0 s real = 8.5 s of the cycle (the flat car well off the lane, the
banked car still on the centre line, both still inside the band:
assert it), hold, reset by a crossfade over the last 0.5 s of the
cycle; 4 cycles in 40 s, exactly periodic, the last frame equal to the
first. The legend row after the title: "same car, same icy curve, 1/2
speed"; the shared clock in real seconds since the entry. Overlay: "50
km/h, 50 m curve, grip 0.1 | no seed" (measure it; shorten if over 950
px).

Day thirty-nine, third slot. Chosen because "which road keeps the car in
its lane" is an everyday debate with a visible yes-or-no ending (one car
off the road, the other on the line), road shorts have been among the
strongest on the channel (brake or swerve 734 views), the thresholds are
exact (sqrt(mu g R), sqrt(g R tan theta)) and the repeat is a natural
loop. Question in the first two seconds: "Icy curve at fifty. Flat road
or banked road: which one keeps the car in its lane?" (pre-test; a
question-first form "Which road keeps a car in its lane on ice, flat or
banked?" lands at 0.6 s). Keep the question identical in the title, the
hook and the payoff. Setup number: "fifty kilometers an hour" (one setup
number only; the radius and the grip go to the overlay, card and
description). Payoff: flat, off the road in one point six seconds;
banked twenty degrees, it holds (at most two numbers in the payoff
beat). The mechanism sentence must follow the picture: on the flat road
only grip can push the car sideways, and ice gives almost none; the
banked road pushes the car toward the centre by itself, as the inset
arrow shows. Whisper risks: "banked" and "bank" (pre-test "banked road",
"banked twenty degrees"), "icy" (pre-test; "on ice" is the fallback),
"lane" (pre-test), sentence-initial "Grip" (never start a sentence with
it), "kilometers an hour" (pre-test), "fifty" (passed on day 38 as
"forty five"), avoid "do you", avoid "too". Pre-test hooks with
scripts/voiceover.sh and keep the one whose question lands earliest
under two seconds. Measure every fixed text line with PIL before
rendering and keep every line under 950 px, and the title under 100
characters with no < or >. Music seed 120. Templates: sims/deskchain
(two-band layout, asserts, the clock, the crossfade; read it whole),
sims/swerve (top-down car, lane edges, exit mark), sims/braking and
sims/hump (road scenes). Sim name bankcurve: sims/bankcurve/bankcurve.py,
projects/bankcurve/, media/bankcurve/.

## Claim (expected; the sim's numbers replace these)

The same car at 50 km/h enters the same 50 m curve on ice with grip 0.1.
Holding the curve needs 0.39 g sideways. On a flat road the tyres give
0.1 g, the car follows a 197 m circle and is over the outer lane edge
after 22 m, in 1.59 s. On a road banked at 20 degrees the road itself
pushes the car toward the centre and only 0.026 of grip is needed, so it
holds its lane; the bank alone holds 48 km/h with no grip at all.
Narrated: fifty kilometers an hour (setup); off the road in one point
six seconds against it holds (payoff). Card: the question; the answer
with 1.59 s against holds; needs 0.39 g, ice gives 0.1 g; the banked
road needs 0.026 g; flat limit 25 km/h, banked window 40 to 55 km/h.
Description: the model statement, the equations, the two runs, the
speed and grip variants, the bank angles, the checks.

## Claim

The same car at 50 km/h enters the same 50 m curve on ice with grip 0.1
(point car, the speed held constant, both chosen). Holding the curve
needs v^2 / R = 3.858 m/s^2 = 0.3934 g sideways. On the flat road the
tyres give 0.1 g, 3.93 times less, so with full-grip steering (the
swerve model) the car follows a 196.70 m circle and crosses the outer
lane edge 3.5 m out after 22.05 m, 1.5876 s after the entry, 25.3
degrees round the curve; at 4 s it is 19.2 m outside the lane centre
line. On the road banked at 20 degrees the road's push N = 1.0742
weights is tilted toward the centre and supplies 3.6032 of the 3.858
m/s^2 needed; the friction needed is 0.2712 m/s^2 down the slope, a
grip of 0.0257 against 0.1 available (0.0743 to spare), so the car
holds its centre line (RK4 offset within 4.1e-13 m). The flat road
holds this curve only up to 25.21 km/h; the bank alone holds 48.09 km/h
with no grip; with grip 0.1 the bank holds 40.23 to 55.32 km/h.
Narrated: fifty kilometers an hour (setup); "The banked road: it holds.
The flat car is off the road in one point six seconds." (payoff).

## Evidence

### Measurements

`nix develop -c python3 sims/bankcurve/bankcurve.py projects/bankcurve/manifest.json --measure-only`
(final run 10:47:04, exit 0, saved as media/bankcurve/measure.log):

```
Wed Oct  7 10:47:04 AM EEST 2026
warning: Git tree '/home/alex/personal/seedzero' is dirty
setup: top-down view, two panels on one clock, the same curve drawn the same way at the same scale: a point car at 50 km/h = 13.8889 m/s (the speed held constant: chosen) enters a curve whose lane centre line has radius R = 50 m, in a lane 7 m wide (edges 3.5 m either side of the centre line), on ice with grip mu = 0.1 (a chosen number for tyres on ice); g = 9.807 m/s^2; top panel the flat road, bottom panel the road banked at theta = 20 degrees with the outer edge higher; the flat car steers with full grip (the swerve model: the lateral acceleration mu g perpendicular to its velocity, the speed held), the banked car follows its centre line; both integrated by classical RK4 at 10000 steps per second (dt = 1e-04 s) on (x, y, vx, vy) to 4 s after the entry, the flat car's lane-edge crossing located by bisection inside the step and checked against the circle v^2 / (mu g) and a half-step rerun; after the edge the flat car keeps its full-grip steer off the road (chosen); shown at 1/2 speed on a 10 s cycle (600 frames) with the entry 0.5 s into the cycle, 4 cycles in 40 s; drawn at 11 px per metre (the lane 77 px wide, the curve radius 550 px; the model's point car drawn as a 3.7 by 2 m body, 41 by 22 px); deterministic, no seed
needed: holding the curve needs v^2 / R = 3.8580 m/s^2 = 0.3934 g sideways; the tyres on ice can give at most mu g = 0.9807 m/s^2 = 0.1 g on the flat, 3.93 times less than needed; the flat road holds this curve up to sqrt(mu g R) = 7.0025 m/s = 25.21 km/h
flat road (top panel): with 0.1 g of grip the car follows a circle of radius v^2 / (mu g) = 196.6975 m = 196.70 m instead of 50 m; RK4 from the entry: it crosses the outer lane edge 3.5 m out after 22.0506 m of travel = 22.05 m, 1.587641 s = 1.5876 s after the entry, 25.27 degrees of arc at the lane's radius = 25.3 deg (its bearing from the curve centre 24.29 deg); closed form on the 196.70 m circle: 22.0506 m, 1.587641 s (diff +1.6e-14 s); small-arc check sqrt(2 w / (1 / R - 1 / R2)) = 21.663 m; the RK4 position stays within 5.1e-13 m of the circle over the 4 s run (40000 steps); half-step rerun (dt = 5e-05 s): over the edge at 1.587640596 s (-1.6e-14 s); at 4 s the car is 19.1852 m = 19.2 m outside the lane centre line (15.7 m past the edge), bearing 52.4 deg, speed kept 50.00 km/h
banked 20 degrees (bottom panel): the force balance per kilogram in the road frame: the road's push N = g cos theta + (v^2 / R) sin theta = 9.2156 + 1.3195 = 10.5351 m/s^2 = 1.0742 weights (its tilt toward the centre gives 3.6032 m/s^2 of the 3.8580 needed); along the slope, the needed (v^2 / R) cos theta = 3.6254 against gravity's g sin theta = 3.3542, so the friction needed is 0.2712 m/s^2 down the slope (inward: without it the car would creep up and out, the speed being above the design speed), grip needed F / N = 0.0257 against 0.1 available (1.0535 m/s^2 along the slope, 0.0743 of grip to spare), so the car holds its lane; RK4 of the lane-following motion (lateral acceleration v^2 / R): the offset from the centre line stays within 4.1e-13 m over 4 s and it never reaches the edge; no grip at all holds sqrt(g R tan theta) = 13.3594 m/s = 48.09 km/h on this bank (the design speed); with grip 0.1 the bank holds 40.23 to 55.32 km/h (below it the car slides down the bank, above it up and out)
  t 0.00 s: flat +0.0000 m off the lane centre (in the lane), 0.00 deg round the curve; banked +0.0e+00 m off, 0.00 deg round the curve
  t 0.25 s: flat +0.0898 m off the lane centre (in the lane), 3.97 deg round the curve; banked +0.0e+00 m off, 3.98 deg round the curve
  t 0.50 s: flat +0.3583 m off the lane centre (in the lane), 7.92 deg round the curve; banked +0.0e+00 m off, 7.96 deg round the curve
  t 0.75 s: flat +0.8026 m off the lane centre (in the lane), 11.83 deg round the curve; banked -7.1e-15 m off, 11.94 deg round the curve
  t 1.00 s: flat +1.4180 m off the lane centre (in the lane), 15.66 deg round the curve; banked -7.1e-15 m off, 15.92 deg round the curve
  t 1.25 s: flat +2.1981 m off the lane centre (in the lane), 19.40 deg round the curve; banked +0.0e+00 m off, 19.89 deg round the curve
  t 1.50 s: flat +3.1356 m off the lane centre (in the lane), 23.04 deg round the curve; banked +4.3e-14 m off, 23.87 deg round the curve
  t 1.75 s: flat +4.2220 m off the lane centre (over the edge), 26.56 deg round the curve; banked +5.7e-14 m off, 27.85 deg round the curve
  t 2.00 s: flat +5.4483 m off the lane centre (over the edge), 29.95 deg round the curve; banked +4.3e-14 m off, 31.83 deg round the curve
  t 2.25 s: flat +6.8049 m off the lane centre (over the edge), 33.22 deg round the curve; banked +1.1e-13 m off, 35.81 deg round the curve
  t 2.50 s: flat +8.2823 m off the lane centre (over the edge), 36.35 deg round the curve; banked +1.7e-13 m off, 39.79 deg round the curve
  t 2.75 s: flat +9.8713 m off the lane centre (over the edge), 39.34 deg round the curve; banked +9.9e-14 m off, 43.77 deg round the curve
  t 3.00 s: flat +11.5627 m off the lane centre (over the edge), 42.20 deg round the curve; banked +1.2e-13 m off, 47.75 deg round the curve
  t 3.25 s: flat +13.3477 m off the lane centre (over the edge), 44.94 deg round the curve; banked +2.2e-13 m off, 51.73 deg round the curve
  t 3.50 s: flat +15.2182 m off the lane centre (over the edge), 47.54 deg round the curve; banked +2.9e-13 m off, 55.70 deg round the curve
  t 3.75 s: flat +17.1664 m off the lane centre (over the edge), 50.03 deg round the curve; banked +3.7e-13 m off, 59.68 deg round the curve
  t 4.00 s: flat +19.1852 m off the lane centre (over the edge), 52.41 deg round the curve; banked +3.6e-13 m off, 63.66 deg round the curve
for the description: 30 km/h: the flat road needs grip 0.1416 (slides out); the bank needs grip 0.2114 up the slope (slides down the bank; N 0.9881 weights); 40 km/h: the flat road needs grip 0.2518 (slides out); the bank needs grip 0.1028 up the slope (slides down the bank; N 1.0258 weights); 60 km/h: the flat road needs grip 0.5665 (slides out); the bank needs grip 0.1679 down the slope (slides up and out; N 1.1334 weights); 70 km/h: the flat road needs grip 0.7711 (slides out); the bank needs grip 0.3179 down the slope (slides up and out; N 1.2034 weights); grip 0.3: the flat road holds up to 43.7 km/h, the 20 degree bank 19.1 to 68.8 km/h; grip 0.5: the flat road holds up to 56.4 km/h, the 20 degree bank 0.0 to 81.9 km/h; grip 0.8: the flat road holds up to 71.3 km/h, the 20 degree bank 0.0 to 102.2 km/h; the bank that holds 50 km/h on this curve with grip 0.1: tan theta = (v^2 / (g R) - mu) / (1 + mu v^2 / (g R)) gives 15.76 degrees; with no grip at all tan theta = v^2 / (g R) gives 21.47 degrees
checks against the brief (22 checks, 0 failed): needed (m/s^2): brief 3.858, sim 3.85802, diff +2.5e-05: ok; needed (g): brief 0.3934, sim 0.393395, diff -5.0e-06: ok; flat radius (m): brief 196.7, sim 196.697, diff -2.5e-03: ok; flat travel to the edge (m): brief 22.05, sim 22.0506, diff +5.6e-04: ok; flat time to the edge (s): brief 1.5876, sim 1.58764, diff +4.1e-05: ok; flat angle to the edge (deg): brief 25.3, sim 25.2681, diff -3.2e-02: ok; banked grip needed: brief 0.0257, sim 0.0257393, diff +3.9e-05: ok; banked N (weights): brief 1.0742, sim 1.07424, diff +4.2e-05: ok; flat limit (km/h): brief 25.21, sim 25.209, diff -1.0e-03: ok; design speed (km/h): brief 48.09, sim 48.0937, diff +3.7e-03: ok; banked window low (km/h): brief 40.23, sim 40.2318, diff +1.8e-03: ok; banked window high (km/h): brief 55.32, sim 55.3161, diff -3.9e-03: ok; bank needed with grip 0.1 (deg): brief 15.76, sim 15.7638, diff +3.8e-03: ok; bank needed with no grip (deg): brief 21.47, sim 21.4744, diff +4.4e-03: ok; small-arc travel (m): brief 21.663, sim 21.6632, diff +1.7e-04: ok; 30 km/h banked grip needed: brief -0.2114, sim -0.211449, diff -4.9e-05: ok; 40 km/h banked grip needed: brief -0.1028, sim -0.102779, diff +2.1e-05: ok; 60 km/h banked grip needed: brief 0.1679, sim 0.1679, diff +6.9e-08: ok; 70 km/h banked grip needed: brief 0.3179, sim 0.317875, diff -2.5e-05: ok; grip 0.3 flat limit (km/h): brief 43.7, sim 43.6633, diff -3.7e-02: ok; grip 0.5 flat limit (km/h): brief 56.4, sim 56.369, diff -3.1e-02: ok; grip 0.8 flat limit (km/h): brief 71.3, sim 71.3018, diff +1.8e-03: ok
schedule (video time, 1/2 speed): cycles of 10 s start at -1.00, 9.00, 19.00, 29.00, 39.00 s (the first 1.00 s before the first frame); both cars pass the entry 0.5 s into each cycle at 9.50, 19.50, 29.50, 39.50 s; the flat car is over the outer edge 3.175 s after the entry at 2.68, 12.68, 22.68, 32.68 s (3.675 s into the cycle; both event rows light and the gold edge mark fades in over 0.3 s); the run ends 8 s after the entry at 7.50, 17.50, 27.50, 37.50 s (8.5 s into the cycle: the flat car 19.2 m outside the lane centre line, the banked car on it) and both cars hold there until the reset crossfade over the last 0.5 s of each cycle (from 8.50, 18.50, 28.50, 38.50 s; the readouts out over its first half and in over its second); on the first frame the cycle is 1.00 s in (0.250 s real after the entry: the flat car 0.09 m off the centre line, the banked car 0.0e+00 m); title until 3 s; payoff card from 33.4 s; the title fades back in over the last 0.5 s and the last frame repeats the first (the scene is periodic: 40 s holds exactly 4 cycles)
text widths (the on-screen strings verbatim): overlay@34 752 px '50 km/h, 50 m curve, grip 0.1 | no seed', title line 1@56 808 px 'Flat road or banked road:', title line 2@56 524 px 'which one keeps', title line 3@56 587 px 'the car in its lane?', legend@40 812 px 'same car, same icy curve, 1/2 speed', clock@28 358 px '1.588 s after the entry', clock before@28 259 px 'before the entry', label flat@40 397 px 'flat road, grip 0.1', sub flat@28 357 px 'needs 0.39 g sideways', fixed flat@28 487 px 'grip needed 0.39, ice gives 0.1', event flat@40 631 px 'flat: over the edge at 1.59 s', label banked@40 538 px 'banked 20 deg, grip 0.1', sub banked@28 490 px 'road push 1.07 g, tilted inward', fixed banked@28 507 px 'grip needed 0.026, ice gives 0.1', event banked@40 498 px 'banked: holds its lane', offset@28 410 px '19.2 m off the lane centre', speed@28 231 px 'speed 50 km/h', mark@24 315 px 'over the edge at 1.59 s', inset label@24 179 px 'cross-section', payoff line 1@40 808 px 'which one keeps the car in its lane?', payoff line 2@40 919 px 'banked: holds its lane; flat: out at 1.59 s', payoff line 3@40 865 px 'needs 0.39 g sideways, ice gives 0.1 g', payoff line 4@40 831 px 'bank push 1.07 g, grip needed 0.026', payoff line 5@40 913 px 'flat limit 25 km/h; bank window 40 to 55', payoff line 6@40 858 px 'the bank alone holds 48 km/h, no grip'
row check: the left column ends at x 578 px, the right column starts at x 630 px; both end 136 px under the band top; the event rows span 152 to 192 px under the band top, right-aligned at x 1040 from x 409 (widest 631 px); the lane enters at the band's right edge 6.2 m before the entry point (1021, 465) heading 150 deg and is drawn to 67.7 deg round the curve, its edges and centre line within x 386 to 1040 and y 353 to 536 px under the band top; the flat car's dashed circle is drawn 58 m from the entry, within x 430 to 1021 and y 231 to 465; the flat car's body over the run spans x 434 to 1044 and y 222 to 485 (its point at the run end (456, 238)); the banked car's body spans x 418 to 1044 and y 380 to 504 (its point at the run end (441, 484)); the crossing point at (805, 356) with the lane's inner edge at y 433 under it and the mark label centred at (760, 485), 315 px wide; the cross-section inset spans x 44 to 244 and y 436 to 526 px under the band top with its label at y 406; each band is 550 px tall (y 330 to 880 and 880 to 1430); the caption band starts at y 1440; the title rows end at y 330 and the overlay band ends at y 130
Wed Oct  7 10:47:05 AM EEST 2026
```

Checks in the brief, each printed and compared by the sim (22 checks,
0 failed; tolerance 1e-3 relative or the brief's rounding):

- needed 3.858 m/s^2 = 0.3934 g against 0.1 g: sim 3.85802 m/s^2 =
  0.393395 g; mu g = 0.9807 m/s^2, 3.93 times less. ok.
- flat radius 196.70 m: sim 196.6975 m. ok.
- over the lane edge after 22.05 m, 1.5876 s, 25.3 deg: sim 22.0506 m,
  1.587641 s, 25.27 deg of arc (bearing 24.29 deg). ok.
- RK4 against the circle: closed form 1.587641 s, diff +1.6e-14 s; the
  RK4 position within 5.1e-13 m of the circle over 40000 steps. ok.
- half-step rerun agreeing within 1e-9 s: dt 5e-05 s gives 1.587640596
  s, diff -1.6e-14 s. ok.
- banked grip needed 0.0257, N 1.0742 weights: sim 0.0257393 and
  1.07424. ok. The friction acts down the slope (inward), not outward
  as the brief says: 50 km/h is above the 48.09 km/h design speed, so
  without friction the car would creep up and out. The number is the
  same; see Deviations.
- flat limit sqrt(mu g R) = 25.21 km/h: sim 25.209. ok.
- no-grip design speed sqrt(g R tan theta) = 48.09 km/h: sim 48.0937.
  ok.
- banked window with grip 0.1 40.23 to 55.32 km/h: sim 40.2318 to
  55.3161. ok.
- 30, 40, 60, 70 km/h on the bank: 30 needs 0.2114 up the slope (slides
  down the bank), 40 needs 0.1028 up the slope (slides down, just below
  the window), 60 needs 0.1679 down the slope (slides up and out), 70
  needs 0.3179 (slides out). ok, all four signs as the brief says.
- grips 0.3 / 0.5 / 0.8 flat limits 43.7 / 56.4 / 71.3 km/h: sim
  43.6633 / 56.369 / 71.3018. ok.
- bank needed with grip 0.1 15.76 deg, with no grip 21.47 deg: sim
  15.7638 and 21.4744. ok.
- small-arc check 21.663 m: sim 21.6632 m. ok.
- the banked car stays on the centre line: RK4 offset within 4.1e-13 m
  over 4 s, never reaches the edge. ok.
- both cars inside the band at the run end: flat car body spans x 434
  to 1044 and y 222 to 485 under the band top (its point at the run end
  (456, 238)), banked car x 418 to 1044 and y 380 to 504; asserted. ok.
- the lane arcs inside the band: lane within x 386 to 1040 and y 353 to
  536 under the band top; asserted. ok.
- every fixed text line under 950 px: widest is payoff line 2 at 919
  px; asserted. ok.
- schedule: entry 0.5 s into the cycle, the flat car over the edge
  3.675 s into the cycle (2.68, 12.68, 22.68, 32.68 s of video), run end
  8.5 s into the cycle, crossfade over the last 0.5 s, 4 cycles in 40
  s. ok.

### Production

- sims/bankcurve/bankcurve.py (new): two-band top-down scene after
  sims/deskchain, car and lane drawing after sims/swerve, RK4 on
  (x, y, vx, vy) at 10000 steps per second with bisection for the edge
  crossing, closed-form and half-step checks, 22 brief checks with
  assert, text-width and box-collision asserts (left and right readout
  columns, event rows, inset, inset label, mark label against the lane,
  the dashed circle and both car bodies over the whole run), loop and
  periodicity asserts in the renderer. Deterministic, no seed used.
- projects/bankcurve/manifest.json: speed 50 km/h, R 50 m, lane 7 m, mu
  0.1, bank 20 deg, g 9.807, steps_per_second 10000, run_end_s 4.0,
  cycle 10 s, slow 2.0, entry_at 0.5, px_per_m 11, entry (1021, 465)
  heading 150 deg, title_until 3.0, payoff_t 33.4, music_seed 120,
  voice_offset 0.6.
- Smoke frames viewed before the full render (media/bankcurve/smoke-*.png
  at 0.0, 1.5, 2.0, 2.7, 3.4, 7.5, 8.75, 12.68, 17.0, 33.4, 38.7,
  39.5 s): the lane sweeps up and left from the band's right edge, the
  flat car runs wide along the dashed coral circle and is over the
  outer edge at 2.7 s with both gold event rows lit and the mark label
  fading in, at 7.5 s the flat car sits 19.2 m off at the upper left and
  the banked car at the far end on the centre line, 8.75 s is mid
  crossfade, 33.4 s shows the card rising, 39.5 s the title fading back
  in. One fix from the smoke pass: the banked inset's road line poked 3
  px out of its box (inset centre moved to INSET_Y0 + INSET_H - 30, half
  length 70) before the final render.
- Full render: media/bankcurve/render.log: loop check 0 px (max diff
  0), periodicity 0 px, loop step 788 px; footage.mp4 40.00 s at 60
  fps, 2400 frames.
- Hook pre-tests (media/bankcurve/hooks/pretest.log, each one take):
  hook1 "Flat road or banked road: which one keeps the car in its lane?
  Same car, same icy curve, fifty kilometers an hour." ok, the question
  starts at 0 s of voice (0.60 s of video), no silence of 0.22 s or
  more before it; hook2 "Icy curve at fifty. Flat road or banked road:
  ..." ok but the question lands after the pause ending at 3.14 s
  (3.74 s of video); hook3 "Banked road or flat road: ..." ok, leading
  silence to 0.30 s; hook4 "Which road keeps a car in its lane on ice,
  flat or banked?" ok, 3.37 s; hook5 "On ice at fifty, flat road or
  banked road: ..." ok, question at 2.91 s. Chosen hook1: the question
  is the first thing said and matches the title and the payoff word for
  word. Word pre-test (hooks/words.txt: icy, on ice, fifty kilometers an
  hour, banked, banked twenty degrees, lane, lane edge, runs wide,
  Turning needs a sideways push, Only grip gives it, center, by itself,
  stays on the line, Every run the same, The banked road: it holds, off
  the road in one point six seconds, shown two times slower, the outer
  edge higher) ok on the first take.
- Narration projects/bankcurve/narration.txt, 112 words; the question
  "Flat road or banked road: which one keeps the car in its lane?" is
  the first sentence and is repeated word for word before the payoff.
  Pass 1 had 113 words (over the limit); "On top, the road is flat."
  became "On top, a flat road.", 112 words.
- Voice round trip media/bankcurve/voice.log: pass 1 ok (34.20 s), pass
  2 ok on the trimmed text (34.27 s); 2 passes, both matched.
- Timing media/bankcurve/timing.log (offset 0.6 s): the question 0.60
  to 2.17 s plus "which one keeps the car in its lane" 2.17 s; "fifty
  kilometers an hour" at 5.96 s; the repeated question 24.50 to 29.92
  s; "The banked road." 29.92 s; "It holds." 30.96 s; "The flat car is
  off the road in 1.6 seconds." 31.79 to 34.87 s; the voice ends at
  34.87 s of video. The fourth edge crossing at 32.68 s sits inside the
  payoff sentence and the card rises at 33.4 s as "one point six
  seconds" is spoken.
- Compose media/bankcurve/compose.log: music seed 120, 40.00 s;
  captions 19 pauses detected, 19 matched, max chunk start shift 1.103
  s; final.mp4 40.000000 s; preview.mp4 and sheet.png written.

### Local QA

- ffprobe final.mp4: h264 1080x1920 at 60/1, aac 22050 Hz mono,
  duration 40.000000 s; atoms ftyp, moov at 32, free, mdat (faststart);
  3760572 bytes; md5 db5e2dd34cdf766525f2adc319cff2c5.
- Caption and overlay bands: signalstats YMAX of footage.mp4 rows 1440
  to 1530 is 28 and rows 96 to 130 is 28 (background only; the scene
  never draws into them).
- Captions: 35 drawtext chunks in media/bankcurve/captions.filter (the
  first is the overlay "50 km/h, 50 m curve, grip 0.1 | no seed"); the
  joined caption text equals the narration word for word (112 words)
  after undoing the drawtext escapes; first captions "Flat road or
  banked" 0.600 to 1.720 s, "road: which one" 1.720 to 2.781 s, "keeps
  the car in its" 2.781 to 3.874 s.
- Full-resolution frames viewed (media/bankcurve/qa-*.png): 0.00 s
  overlay, three-row title, both cars just past the entry at the right,
  flat car 0.1 m off, both insets, no caption; 1.00 s caption "Flat road
  or banked", 0.8 m off; 2.10 s caption "road: which one", 2.4 m off,
  the flat car near the outer edge; 22.00 s legend and clock 1.250 s,
  the gold fixed rows, 2.2 m off, caption "road pushes the car"; 32.70
  s clock 1.600 s, 3.6 m off in gold, both event rows lit, the gold dot
  at the crossing and the mark label fading in, caption "The flat car is
  off"; 33.80 s clock 2.150 s, 6.2 m off, the mark label full, the card
  rising, caption "the road in one"; 35.20 s clock 2.850 s, 10.5 m off,
  the card fully gold, no caption (the voice ended at 34.87 s); 39.983
  s identical to frame 0 (title back, no caption, no card). Nothing
  clipped at the frame edge; the readouts and the cars never overlap.
- sheet.png (8x5 at 1 fps): 40 cells, the captions in order, the card
  from 33 s, the loop closes on the first frame.

### Metadata

- projects/bankcurve/metadata.json written by a script with asserts:
  title 98 characters (at most 100), description 3923 characters (under
  5,000), ASCII, no angle brackets, 11 tags; every number in the title
  and description (75 distinct, commas stripped) appears in
  media/bankcurve/measure.log.
- Title: Flat road or banked road: which one keeps the car in its lane?
  Banked holds; flat is off in 1.59 s
- privacyStatus private, categoryId 27, containsSyntheticMedia true,
  selfDeclaredMadeForKids false.

### Deviations from the brief

- Scale 11 px per metre, not about 30: at 30 px/m the 50 m radius is
  1500 px and the 25.3 degrees to the crossing alone rise 630 px, more
  than the 550 px band, and the 4 s run (55.6 m of travel, 52 to 64
  degrees of arc) must fit the band with both cars inside (asserted).
  The lane is 77 px wide and the car 41 by 22 px (a 3.7 by 2 m body),
  entering from the band's right edge 6.2 m before the entry point
  heading 150 degrees, the curve sweeping up and left as the brief
  asks. The lane edges, the centre line and the dashed circle stay
  inside the band (asserted).
- Three title rows instead of two: the two-row form measured 1131 px.
- Bottom readout "road push 1.07 g, tilted inward" and fixed rows "grip
  needed 0.39, ice gives 0.1" / "grip needed 0.026, ice gives 0.1" in
  place of the brief's "needs 0.026 g of grip": the grip is a ratio of
  the road push, not a fraction of g, so the readouts name it as grip.
- The banked friction acts down the slope (inward), not "outward" as
  the brief and bank.log label it: the sim prints the sign (needed 3.6254
  along the slope against gravity's 3.3542). The grip number 0.0257 is
  unchanged. The brief's "0.1 of grip to spare" is 0.0743 to spare (0.1
  available minus 0.0257 needed).
- Hook1 chosen (the question first) rather than the brief's "Icy curve
  at fifty." lead-in: in the pre-test that lead-in pushed the question
  to 3.74 s of video, over the two-second rule.
- The payoff narrates "The banked road: it holds." without "twenty
  degrees"; the angle is on the band label, the card and in the
  description. The payoff beat carries one number (one point six
  seconds) against "it holds".
- Card from 33.4 s (the brief gives no time): it rises as "one point six
  seconds" is spoken and after the fourth crossing at 32.68 s.
- Payoff card lines reworded to fit 950 px: "banked: holds its lane;
  flat: out at 1.59 s", "bank push 1.07 g, grip needed 0.026", "flat
  limit 25 km/h; bank window 40 to 55", "the bank alone holds 48 km/h,
  no grip".

## Niche note

[produced 2026-10-07 as "Flat road or banked road: which one keeps the
car in its lane? Banked holds; flat is off in 1.59 s"; measured needed
3.858 m/s^2 = 0.3934 g against 0.1 g, flat circle 196.70 m, over the
outer edge after 22.05 m and 1.5876 s (25.3 deg), 19.2 m off at 4 s,
banked N 1.0742 weights with grip needed 0.0257 down the slope
(inward), flat limit 25.21 km/h, design 48.09 km/h, window 40.23 to
55.32 km/h, bank needed 15.76 deg (21.47 with no grip); task
20261007-102009]

## Upload

- Attempt 3 of 5 (quota day 2026-10-07T10:00 EEST) recorded at 2026-10-07T10:59:19+03:00 before scripts/yt-upload.py bankcurve; two earlier attempts since the boundary (tray and boatjump, both succeeded).
- Uploaded private as 5U_2xBkAJpY at 2026-10-07T07:59:22Z (videos.insert 1,600 units). yt-qa.py --wait --publish: gate 15 of 15 on the first processed read, published at 2026-10-07T11:00:19+03:00, re-read public, 55 units. https://youtu.be/5U_2xBkAJpY
