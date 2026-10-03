# Produce short: Coin on a record, 45 turns a minute beside 78, does the coin stay on

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day35

## Goal

Backlog idea (trend research 2026-09-30, task 20260930-100404, pillar 2
chaos and physics, everyday mechanics; read the full entry under "Added
by trend research 2026-09-30" in docs/niche.md): "Coin on a 45 or a 78: a
coin 10 cm from the centre of a record with mu 0.3 at 45 rpm beside 78
rpm; measure whether it stays and where it leaves; expect 45 rpm to need
0.226 g against 0.3 available (stays, out to 13.25 cm) and 78 rpm to need
0.680 g, the coin sliding on a spiral to the 15 cm edge in 0.180 s, 69
degrees round, at 0.876 m/s while the disc turns 84 degrees; threshold
51.8 rpm at 10 cm (sqrt(mu g / r)); 33 1/3 rpm holds out to 24 cm; RK4
with Coulomb friction against the disc; the turntable prop was used on
2026-09-16 and the threshold depends on mu, so rank it low;
deterministic, no seed."

Orchestrator notes (2026-10-03, before this brief). The model: a 30 cm
record (radius R = 15 cm) turns at a steady speed, clockwise as seen from
above like a real turntable, flush with a still deck around it (a lazy
susan: the deck beyond the rim does not turn). A coin (a point mass for
the physics, drawn 2.4 cm across; its mass cancels) sits 10 cm from the
centre, held down by a fingertip so it moves with the record; at the
release the fingertip lifts and friction alone must hold the coin.
Friction coefficient mu = 0.3 between the coin and the record and the
same mu on the deck, the same at rest and sliding (a chosen value for a
coin on vinyl; say so; the threshold scales with sqrt(mu)). Top panel 45
rpm, bottom panel 78 rpm. Static test: the coin rides along while the
grip it needs, omega^2 r / g, is at most mu. At 45 rpm (omega = 4.7124
rad/s) it needs 0.2264: it stays, and the sim prints the margin and the
radius out to which 45 rpm holds, mu g / omega^2 = 13.25 cm. At 78 rpm
(omega = 8.1681 rad/s) it needs 0.6803: it slides. The threshold at 10 cm
is omega* = sqrt(mu g / r) = 5.4241 rad/s = 51.80 rpm. Sliding: integrate
the coin in the inertial (deck) frame with RK4 at 1e-5 s steps (and a
half-step rerun as a check): the acceleration is mu g opposite to the
coin's velocity relative to the record surface under it (the surface at
(x, y) moves at omega times (-y, x)); at the release the relative velocity
is zero, so the first step's friction is mu g toward the centre (the
direction of impending slip); after that the relative speed is positive
and the direction is defined. When the coin's radius reaches R it is off
the record: record the time, the coin's position angle in the deck frame,
its velocity direction and speed, its speed relative to the record, and
the record's turn by then. Past the rim the coin skids on the still deck
under the same mu, decelerating at mu g in a straight line from its exit
velocity until it stops: distance v^2 / (2 mu g), time v / (mu g).

Checks, not facts (orchestrator RK4 in /tmp/day35/closed.py and
closed2.py, g = 9.807): 45 rpm: needs 0.2264 of grip against 0.30, stays
(the panel never moves relative to the record); holds out to 13.25 cm.
78 rpm: off the rim at 0.1797 s after the release, 69.2 degrees round the
centre in the deck frame from where it started, moving at 0.8758 m/s
(0.689 m/s relative to the record) while the record turned 84.1 degrees,
so the coin lags the record by 14.8 degrees at the rim; the skid on the
deck: 13.0 cm in 0.298 s, the coin at rest 0.477 s after the release. The
exit velocity points 125.9 degrees from the coin's starting radius
(counterclockwise in a frame where the record turns counterclockwise;
mirror it for clockwise), so a starting angle of -125.9 degrees makes the
coin leave the rim moving along +x. For the description: 33 1/3 rpm needs
0.1242 and holds out to 24.15 cm; 60 rpm: off at 0.3199 s, 103.2 degrees
round, 0.7598 m/s, a 9.8 cm skid; 52 rpm (just over the limit): off at
0.9514 s; 100 rpm: off at 0.1241 s at 1.0737 m/s, a 19.6 cm skid; the
radius at which 78 rpm would hold the coin: mu g / omega^2 = 4.41 cm
(inside the label); the half-step rerun must agree with the 1e-5 run to
better than 1e-4 s on the exit time. Print the static test for both
panels, the full slide table (time, radius, angle, speed) at 10 ms
intervals for 78 rpm, the exit numbers, the skid, the description
variants, the schedule in video time, the text widths and the layout
clearances. State every number above as a check the sim must print, not
as a fact.

Drawing: top view, two stacked bands (y 330-880 and 880-1430), 45 rpm on
top (teal), 78 rpm below (coral), the same record drawn the same way at
the same scale, 1200 px per metre (the record 360 px across) with its
centre at about x 460 and about 305 px under the band top; a lighter
deck slab behind the record (the still part, to the band's edges); the
record as dark vinyl with concentric groove rings (rotationally
symmetric, so the cycle reset does not jump) and a small label with one
marker and a spindle so the turn is visible; the coin a 29 px disc
(2.4 cm) in gold-ish silver with a thin outline; the fingertip a muted
rounded pad over the coin that fades out at the release (like the clamp
in sims/deskchain); after the release the top coin rides round with the
record; the bottom coin spirals out, leaves a thin trail on the record
(drawn in the record's frame so it turns with the record) and skids
straight across the deck to rest; choose the coin's starting angle so the
exit velocity points to the right and the skid stays in the clear middle
of the right column (assert that the coin and its skid never enter a
text row or the event row and never leave the band). Text in each band:
label row "45 turns a minute" / "78 turns a minute" (40 px), second row
"coin 10 cm from the centre, grip 0.30" (28 px) in the left column, a
right-aligned live readout "needs 0.23 of grip" / "needs 0.68 of grip"
(28 px) that turns gold at the release; a gold event row at the band's
bottom row (496-540 px under the band top): "stays on: needs 0.23, has
0.30" (lit about 1 s after the release) / "off the record in 0.18 s" (lit
as the coin crosses the rim) and held to the crossfade. Shown at 1/10
speed; cycle 10 s (600 frames): the fingertip lifts 1.0 s into the cycle,
the 78 coin crosses the rim at 2.80 s and is at rest on the deck at 5.77
s of the cycle; a reset crossfade over the last 0.6 s; 4 cycles in 40 s,
the last frame equal to the first. The record's angle is drawn from the
cycle time, so the marker jumps under the crossfade (the grooves do not).
Legend row after the title: "same coin, same grip, 1/10 speed"; the
shared clock in real seconds after the release ("held" before it).

Day thirty-five, first slot. Chosen because "will the coin stay on" is a
question anyone with a turntable or a lazy susan has asked, the panels
end visibly differently (one coin rides round, the other is flung off the
rim in under a fifth of a second), the limit is one clean number, and the
turntable prop drew 974 views on 2026-09-16. Question in the first two
seconds: "Does the coin stay on the record?" (keep the question identical
in the title, the hook and the payoff). Setup number: forty five turns a
minute on top, seventy eight below (the two speeds name the panels; say
"turns a minute", never "rpm", in the narration). Payoff: at forty five it
stays; at seventy eight it is off the record in a fifth of a second (or
"in point one eight seconds"); the limit, fifty two turns a minute, goes
to the card and the description (it may be spoken if the words fit). The
grip numbers, 13 cm, the skid and the 33, 60 and 100 variants go to the
card and the description. Whisper risks: "fingertip" (pre-test; 2026-10-02
"on a fingertip" came back "and a fingertip"), "coin" ("coins" came back
"coin" once; keep it singular), "record" (fine), "rim", "grip",
"spirals", "skids", "flung", "a fifth of a second" and "one fifth"
(pre-test both; 2026-09-30 "two sevenths" failed), "forty five" and
"seventy eight" as words (pre-test), "turns a minute" (pre-test); avoid
"do you"; avoid "pull" as a noun; avoid "fly". Pre-test hooks with
scripts/voiceover.sh and keep the one whose question lands earliest under
two seconds. Measure every fixed text line with PIL before rendering and
keep every line under 950 px, and the title under 100 characters with no
< or >. Music seed 107. Templates: sims/deskchain (two bands, cycle,
crossfade, the clamp that releases, layout asserts, loop checks),
sims/turntable (the drawn record and RK4 on a turning disc), sims/cutshot
(top view, trails). Sim name coinrecord: sims/coinrecord/coinrecord.py,
projects/coinrecord/, media/coinrecord/.

## Claim (expected; the sim's numbers replace these)

A coin 10 cm from the centre of a 30 cm record with grip mu = 0.3: at 45
rpm it needs 0.226 of grip and stays (45 rpm holds out to 13.25 cm); at
78 rpm it needs 0.680, slides out on a spiral and is off the rim 0.18 s
after the fingertip lifts, 69 degrees round, at 0.88 m/s while the record
turns 84 degrees, then skids 13 cm on the still deck and stops 0.48 s
after the release. The limit at 10 cm is sqrt(mu g / r) = 51.8 rpm.
Narrated: forty five and seventy eight turns a minute (setup); at forty
five it stays; at seventy eight it is off the record in a fifth of a
second (payoff). Card: the question; 45: stays, needs 0.23 of its 0.30
grip; 78: off the record in 0.18 s, needs 0.68; the limit at 10 cm: 52
rpm; 45 holds out to 13 cm, 78 only to 4.4 cm; 33 1/3 holds out to 24 cm.
Description: the model statement (fingertip release, steady speed, mu
0.3 chosen, the flush deck), the static test, the slide, the skid, the
variants, the checks.

## Claim

A coin 10 cm from the centre of a 30 cm record with grip mu = 0.3 (g =
9.807 m/s^2, the same mu on the still deck round the record): at 45 rpm
(omega 4.7124 rad/s) it needs 0.2264 of grip, under the 0.30 it has
(margin 0.0736), so it stays and rides round with the record; 45 rpm holds
a coin out to 13.25 cm. At 78 rpm (omega 8.1681 rad/s) it needs 0.6803,
2.27 times what it has, so it slides: RK4 in the deck frame at 1e-05 s
steps puts the coin's radius at the 15 cm rim 0.1797 s after the fingertip
lifts, 69.2 degrees round the centre from where it started, moving at
0.8758 m/s (0.689 m/s relative to the record surface) while the record
turned 84.1 degrees (the coin lags the record by 14.8 degrees at the rim);
78 rpm would hold a coin only out to 4.41 cm. Past the rim the coin skids
straight on the still deck 13.0 cm in 0.298 s and is at rest 0.477 s after
the release, 28.0 cm from the record's centre. The limit at 10 cm is
sqrt(mu g / r) = 5.4241 rad/s = 51.80 rpm. The half-step rerun moves the
exit time by -7.4e-15 s. Narrated: forty five and seventy eight turns a
minute (setup); at forty five, yes, it stays; at seventy eight, no, it is
off the record in under a fifth of a second (payoff; the sim prints 0.1797
< 0.2000 s). Card: the question; 45: stays, needs 0.23 of its 0.30 grip;
78: off the record in 0.18 s, needs 0.68; the limit at 10 cm: 52 turns a
minute; 45 holds out to 13 cm, 78 only to 4.4 cm; 33 1/3 holds out to 24
cm. Description: the model statement (fingertip release, steady speed,
mu 0.3 chosen, the flush deck), the limit, both static tests, the slide
with its 10 ms table, the skid, 33 1/3, 52, 60 and 100 rpm, the rim and
other grips, the checks.

## Evidence

### Measurements

media/coinrecord/measure.log (`nix develop -c python3
sims/coinrecord/coinrecord.py --measure-only`, 2026-10-03 10:35:16 EEST,
final manifest and sim; the same numbers as the 10:29 and 10:31 passes
that preceded the smoke frames, with payoff_t set to 26.9 s):

```
Sat Oct  3 10:35:15 AM EEST 2026
warning: Git tree '/home/alex/personal/seedzero' is dirty
setup: the same record in both panels, seen from above: a 30 cm record (radius 15 cm) turns at a steady speed, clockwise as seen from above, flush with a still deck around it (a lazy susan: the deck beyond the rim does not turn); a coin (a point mass for the physics, drawn 2.4 cm across; its mass cancels) sits 10 cm from the centre, held down by a fingertip so it moves with the record; at the release the fingertip lifts and friction alone must hold the coin; friction mu = 0.3 between the coin and the record and the same on the deck, the same at rest and sliding (a chosen value for a coin on vinyl; the limit scales with sqrt(mu)); g = 9.807 m/s^2; top panel 45 rpm (omega = 4.7124 rad/s), bottom panel 78 rpm (omega = 8.1681 rad/s); the slide integrated in the deck frame by RK4 at dt = 1e-05 s (friction mu g opposite to the coin's velocity relative to the record surface under it, toward the centre at the release when that velocity is zero) with the rim crossing located by bisection inside the step and checked by a half-step rerun; past the rim a straight skid on the still deck at mu g; shown at 1/10 speed on a 10 s cycle (600 frames) with the release 1 s into the cycle, 4 cycles in 40 s; drawn at 1200 px per metre (the record 360 px across, the coin 28.8 px); deterministic, no seed
limit: the coin rides along while the grip it needs, omega^2 r / g, is at most mu = 0.3; at r = 10 cm the limit is omega* = sqrt(mu g / r) = 5.4241 rad/s = 51.80 rpm; a speed omega holds a coin out to r = mu g / omega^2
45 rpm (top panel): omega = 4.7124 rad/s, the coin needs omega^2 r / g = 0.2264 of grip against 0.30 available, margin 0.0736: it stays and rides round with the record (its velocity relative to the record stays zero; no integration needed); 45 rpm holds a coin out to mu g / omega^2 = 13.25 cm; it needs 51.80 rpm to move a coin at 10 cm, 6.80 rpm more
78 rpm (bottom panel): omega = 8.1681 rad/s, the coin needs omega^2 r / g = 0.6803 of grip against 0.30 available, 2.27 times what it has: it slides; 78 rpm would hold a coin only out to mu g / omega^2 = 4.41 cm (inside the label); RK4 from the release: the coin's radius reaches the rim R = 15 cm at 0.1797 s, 69.2 degrees round the centre in the deck frame from where it started, moving at 0.8758 m/s = 0.88 m/s (0.689 m/s relative to the record surface) while the record turned omega t = 84.1 degrees, so the coin lags the record by 14.8 degrees at the rim; its velocity points 125.9 degrees from its starting radius (counterclockwise in the frame where the record turns counterclockwise) and 56.7 degrees outward of the tangent direction's radius; that is under one fifth of a second (0.1797 < 0.2000 s); 17966 steps; the relative speed after the first step stays above 3.73e-05 m/s (the friction direction is defined); half-step rerun (dt = 5e-06 s): off at 0.1796503 s (-7.4e-15 s), 69.2293 degrees round, 0.875789 m/s (+4.4e-15 m/s); reference run from angle 0: off at 0.1796503 s (-1.0e-15 s), 69.2293 degrees round; start check: in the record's frame the coin starts outward at omega^2 r - mu g = 3.7298 m/s^2, so after 10 ms it is 0.0186 cm out; RK4 gives 0.0186 cm
slide table (78 rpm, time after the release, radius, angle round the centre in the deck frame from the start, speed in the deck frame): 0 ms r 10.00 cm, 0.0 deg, 0.817 m/s; 10 ms r 10.02 cm, 4.7 deg, 0.817 m/s; 20 ms r 10.07 cm, 9.3 deg, 0.818 m/s; 30 ms r 10.17 cm, 13.9 deg, 0.819 m/s; 40 ms r 10.29 cm, 18.5 deg, 0.820 m/s; 50 ms r 10.46 cm, 22.9 deg, 0.822 m/s; 60 ms r 10.65 cm, 27.2 deg, 0.824 m/s; 70 ms r 10.88 cm, 31.5 deg, 0.826 m/s; 80 ms r 11.14 cm, 35.6 deg, 0.829 m/s; 90 ms r 11.42 cm, 39.5 deg, 0.832 m/s; 100 ms r 11.74 cm, 43.3 deg, 0.836 m/s; 110 ms r 12.07 cm, 47.0 deg, 0.839 m/s; 120 ms r 12.44 cm, 50.6 deg, 0.844 m/s; 130 ms r 12.82 cm, 54.0 deg, 0.848 m/s; 140 ms r 13.22 cm, 57.3 deg, 0.853 m/s; 150 ms r 13.64 cm, 60.5 deg, 0.858 m/s; 160 ms r 14.09 cm, 63.5 deg, 0.864 m/s; 170 ms r 14.54 cm, 66.5 deg, 0.870 m/s; 179.7 ms r 15.00 cm, 69.2 deg, 0.876 m/s
skid (78 rpm): past the rim the coin skids straight on the still deck from 0.8758 m/s at mu g = 2.942 m/s^2: v^2 / (2 mu g) = 13.0 cm = 13.04 cm in v / (mu g) = 0.298 s; the coin is at rest 0.477 s after the release, 28.0 cm from the record's centre
start angle: the drawn coin starts at -125.9 degrees (the physics frame, counterclockwise from +x; the screen mirrors y so the record turns clockwise), so its exit velocity points 0.000000 degrees from +x (to the right) and the skid runs straight right from the rim point at -56.7 degrees; the top coin starts at the same angle and rides round
for the description: 33 1/3 rpm (33.3333; omega 3.4907 rad/s) needs 0.1242 of grip and holds a coin out to 24.15 cm; 52 rpm (omega 5.4454 rad/s) needs 0.3024: off the rim at 0.9514 s, 289.7 degrees round, at 0.7309 m/s while the record turned 296.8 degrees; skid 9.1 cm in 0.248 s, at rest 1.200 s after the release; 60 rpm (omega 6.2832 rad/s) needs 0.4026: off the rim at 0.3199 s, 103.2 degrees round, at 0.7598 m/s while the record turned 115.2 degrees; skid 9.8 cm in 0.258 s, at rest 0.578 s after the release; 100 rpm (omega 10.4720 rad/s) needs 1.1182: off the rim at 0.1241 s, 58.9 degrees round, at 1.0737 m/s while the record turned 74.5 degrees; skid 19.6 cm in 0.365 s, at rest 0.489 s after the release; a coin at the rim itself (15 cm) slides above sqrt(mu g / R) = 42.29 rpm; grip 0.2 at 10 cm: the limit is 42.29 rpm (45 rpm slides, 78 rpm slides); grip 0.5 at 10 cm: the limit is 66.87 rpm (45 rpm holds, 78 rpm slides)
schedule (video time, 1/10 speed): cycles of 10 s start at -10.00, 0.00, 10.00, 20.00, 30.00 s (the first -0.00 s before the first frame); the fingertip lifts 1 s into each cycle at 1.00, 11.00, 21.00, 31.00 s (over 0.3 s); the 78 rpm coin crosses the rim 1.80 s after the release at 2.80, 12.80, 22.80, 32.80 s (2.80 s into the cycle; the event row lights) and is at rest on the deck at 5.77, 15.77, 25.77, 35.77 s (5.77 s into the cycle, before the fade at 9.40 s); the 45 rpm coin rides round and its event row lights 1 s after the release at 2.00, 12.00, 22.00, 32.00 s; the record turns 27.0 and 46.8 degrees per second of video (4.50 and 7.80 turns a minute on screen) and 270 and 468 degrees per cycle, so the label marker jumps under the crossfade (the grooves are symmetric and do not); the reset crossfade runs over the last 0.6 s of each cycle (from 9.40, 19.40, 29.40, 39.40 s; the readouts out over its first half and in over its second); on the first frame the cycle is 0.00 s in (-0.100 s real: both coins held); title until 3 s; payoff card from 26.9 s; the title fades back in over the last 0.5 s and the last frame repeats the first (the scene is periodic: 40 s holds exactly 4 cycles)
text widths (the on-screen strings verbatim): overlay@34 875 px 'coin at 10 cm | grip 0.3 | 1/10 speed | no seed', title line 1@56 583 px 'Does the coin stay', title line 2@56 459 px 'on the record?', legend@40 757 px 'same coin, same grip, 1/10 speed', clock@28 390 px '0.180 s after the release', clock held@28 69 px 'held', label top@40 403 px '45 turns a minute', sublabel top@28 590 px 'coin 10 cm from the centre, grip 0.30', readout top@28 288 px 'needs 0.23 of grip', event top@40 687 px 'stays on: needs 0.23, has 0.30', label bottom@40 403 px '78 turns a minute', sublabel bottom@28 590 px 'coin 10 cm from the centre, grip 0.30', readout bottom@28 288 px 'needs 0.68 of grip', event bottom@40 515 px 'off the record in 0.18 s', state held@28 69 px 'held', state ride@28 182 px 'rides round', state slide@28 105 px 'sliding', state skid@28 371 px 'off the record, skidding', state rest@28 300 px 'at rest on the deck', payoff line 1@40 754 px 'does the coin stay on the record?', payoff line 2@40 828 px '45: stays, needs 0.23 of its 0.30 grip', payoff line 3@40 878 px '78: off the record in 0.18 s, needs 0.68', payoff line 4@40 832 px 'the limit at 10 cm: 52 turns a minute', payoff line 5@40 909 px '45 holds out to 13 cm, 78 only to 4.4 cm', payoff line 6@40 574 px '33 1/3 holds out to 24 cm'
row check: the label row ends at x 443 px and the state word starts at x 669 px; the second row's sublabel ends at x 630 px and the grip readout starts at x 752 px; the rows end 98 px under the band top; the deck slab spans x 24 to 1056 and 108 to 492 px under the band top; the record (360 px) is centred at x 460 and 304 px under the band top, so it spans 124 to 484 px and x 280 to 640; the riding coin (fingertip pad included) stays between 146 and 462 px; the 78 rpm coin leaves the rim at x 559, 154 px under the band top, skids right and rests at x 715; its whole path (coin radius 14.4 px included) spans x 375 to 730 and 139 to 221 px under the band top; the event row spans 496 to 540 px under the band top and x 196 to 884 px (widest 687 px, centred on 540); each band is 550 px tall (y 330 to 880 and 880 to 1430); the caption band starts at y 1440; the title rows end at y 280 and the overlay band ends at y 130
exit 0
Sat Oct  3 10:35:16 AM EEST 2026
```

Brief checks (every number is a line the sim printed):

- 45 rpm needs 0.2264 of grip against 0.30 and stays: passed (margin
  0.0736; the coin's velocity relative to the record stays zero, it rides
  round; no integration needed).
- 45 rpm holds out to 13.25 cm: passed (mu g / omega^2 = 13.25 cm; it
  needs 51.80 rpm to move a coin at 10 cm, 6.80 rpm more).
- 78 rpm needs 0.6803: passed (2.27 times what it has; it slides).
- 78 rpm off the rim at 0.1797 s after the release: passed (0.1796503 s,
  17966 RK4 steps, the crossing by bisection inside the step).
- 69.2 degrees round the centre in the deck frame: passed (69.2293).
- 0.8758 m/s at the rim, 0.689 m/s relative to the record: passed.
- the record turned 84.1 degrees, the coin lags by 14.8 degrees: passed.
- the exit velocity 125.9 degrees from the starting radius, so a start at
  -125.9 degrees makes the coin leave along +x: passed (the drawn run
  starts at -125.9 degrees and its exit velocity points 0.000000 degrees
  from +x; the rim point is at -56.7 degrees; the run from angle 0 agrees
  within -1.0e-15 s and gives the same 69.2293 degrees).
- the skid on the deck 13.0 cm in 0.298 s, at rest 0.477 s after the
  release: passed (13.04 cm; 28.0 cm from the record's centre).
- the limit at 10 cm omega* = 5.4241 rad/s = 51.80 rpm: passed.
- 33 1/3 rpm needs 0.1242 and holds out to 24.15 cm: passed.
- 60 rpm: off at 0.3199 s, 103.2 degrees round, 0.7598 m/s, a 9.8 cm
  skid: passed (the record turned 115.2 degrees; skid 0.258 s).
- 52 rpm (just over the limit): off at 0.9514 s: passed (289.7 degrees
  round, 0.7309 m/s, the record turned 296.8 degrees, skid 9.1 cm in
  0.248 s).
- 100 rpm: off at 0.1241 s at 1.0737 m/s, a 19.6 cm skid: passed (58.9
  degrees round, the record turned 74.5 degrees, skid 0.365 s).
- the radius at which 78 rpm holds a coin, 4.41 cm: passed (inside the
  label).
- the half-step rerun agrees with the 1e-5 run to better than 1e-4 s on
  the exit time: passed (dt 5e-06 s: -7.4e-15 s; +4.4e-15 m/s on the
  speed).
- the static test for both panels, the slide table at 10 ms (time,
  radius, angle, speed), the exit numbers, the skid, the description
  variants, the schedule in video time, the text widths and the layout
  clearances: all printed (above).
- extra checks the sim adds: in the record's frame the coin starts
  outward at omega^2 r - mu g = 3.7298 m/s^2, so after 10 ms it is 0.0186
  cm out, and the RK4 table gives 0.0186 cm; the relative speed after the
  first step stays above 3.73e-05 m/s, so the friction direction is
  defined at every later step; the coin at the rim itself slides above
  42.29 rpm; grip 0.2 moves the limit to 42.29 rpm (both speeds slide),
  grip 0.5 to 66.87 rpm (45 holds, 78 slides).
- 4 cycles in 40 s, the last frame equal to the first: passed (loop
  check 0 px, periodicity check 0 px).

### Production

- Sim: sims/coinrecord/coinrecord.py, modelled on sims/deskchain (two
  bands, cycle, crossfade, the held setup that releases, layout asserts,
  loop checks, 2x supersampled bands, ffmpeg rawvideo pipe with a
  ProcessPoolExecutor of 12 workers, --measure-only and --frames),
  sims/turntable (the drawn record, RK4 on a turning disc) and
  sims/cutshot (top view, trails): the static test, the limit, the RK4
  slide in the deck frame with Coulomb friction against the surface
  velocity (toward the centre on the first evaluation, when the relative
  velocity is zero), bisection on the rim crossing, a half-step rerun, a
  reference run from angle 0, the record-frame start check, the 10 ms
  table, the skid in closed form, the description speeds and grips, the
  start angle that sends the exit velocity along +x, the schedule, text
  widths and the row check.
- Manifest projects/coinrecord/manifest.json: seed 0, fps 60, g 9.807,
  mu 0.3, coin_radius_m 0.10, record_radius_m 0.15, coin_diameter_m
  0.024, rpm top 45 and bottom 78, description_rpm_static [33 1/3],
  description_rpm_slide [52, 60, 100], description_mus [0.2, 0.5], dt_s
  1e-05, table_step_s 0.01, trail_step_s 0.001, slow 10, cycle_s 10,
  release_at 1.0, first_cycle_at 0.0, reset_fade 0.6, hold_event_after_s
  1.0, finger_lift_s 0.3, scene_duration 40, px_per_m 1200,
  record_centre_px [460, 304], title "Does the coin stay|on the record?"
  until 3 s, payoff_t 26.9, payoff_hold 0.6, six payoff lines formatted
  from the measured values, loop_fade 0.5, music_seed 107, music_gain
  0.18, voice_offset 0.6, caption_y 0.75, overlay "coin at 10 cm | grip
  0.3 | 1/10 speed | no seed".
- Layout: overlay y 96-130 (compose); title two rows at y 190 / 252
  until 3 s; legend "same coin, same grip, 1/10 speed" at y 236 and the
  clock ("held" / "N.NNN s after the release", real time) at y 290 after
  the title; bands y 330-880 (45 rpm, teal) and 880-1430 (78 rpm,
  coral); per band: label "45 turns a minute" / "78 turns a minute" (40
  px) with a right-aligned state word (28 px: held, rides round, sliding,
  off the record, skidding, at rest on the deck; gold once the result is
  settled) on the label row, "coin 10 cm from the centre, grip 0.30" (28
  px) with the right-aligned "needs 0.23 of grip" / "needs 0.68 of grip"
  (gold from the release) on the second row; a deck slab x 24-1056, 108
  to 492 px under the band top; the record 360 px across centred at x
  460, 304 px under the band top (dark vinyl, 16 symmetric groove rings,
  a rim, a label with one marker and a short radial line, a spindle),
  turning clockwise from the cycle time; the coin a 28.8 px gold disc
  with an outline and an inner ring, 120 px from the centre; the
  fingertip a muted pad 1.45 times the coin set 6 px left and 7 px up so
  a sliver of the coin shows, growing a quarter and fading out over 0.3 s
  from the release; the 78 coin's slip path drawn in the record's frame
  (it turns with the record) and a thin skid mark on the deck from the
  rim point to the coin; the gold event row at 518 px under the band top
  (496-540): "stays on: needs 0.23, has 0.30" lit 1 s after the release
  and "off the record in 0.18 s" lit as the coin's centre crosses the
  rim, both held to the crossfade; the six-line gold card from y 1572 at
  a 48 px pitch; nothing in rows 96-130 or 1440-1530 (asserted in the row
  check and measured on the footage).
- Hook pre-tests (media/coinrecord/hooks/pretest.log, 10:29-10:30):
  hook1 "Does the coin stay on the record? Forty five turns a minute on
  top, seventy eight below." ok 4.88 s, speech from 0 s (no leading
  silence), the question from 0.60 s of video: chosen (three retakes ok,
  4.78 / 5.10 / 5.14 s). hook2 (", A coin on a turning record, forty five
  ...") ok 6.82 s with a 0.22 s leading silence (the question from 0.82
  s). hook3 ("A coin on a record. Does the coin stay on the record? ...")
  and hook4 ("Does the coin stay on the record when you let go? ...")
  failed: whisper wrote "stay on a record"; hook5 (hook1 plus "The coin
  sits ten centimeters from the center, held down by a fingertip.")
  failed the same way, so the mishearing depends on the context, not on
  the phrase. payoff1 ("So, does the coin stay on the record? At forty
  five, yes. It stays. At seventy eight, no. It is off the record in
  under a fifth of a second.") ok three times (8.97 / 9.01 / 8.49 s).
  words.txt (125 words: fingertip, held by a fingertip, let go, rides
  round, under a fifth of a second, one fifth of a second, point one
  eight seconds, slips, spirals out, flung, rim, skids, deck, forty five
  and seventy eight turns a minute, yes / no, grip, fifty two turns a
  minute, ten centimeters from the center, slides, flies off) failed on
  one word only: "flung" came back "plon"; everything else passed, so the
  narration says "thrown".
- Narration: projects/coinrecord/narration.txt, 108 words; the question
  is the first sentence (spoken from 0.60 s of video) and is repeated
  word for word ("So, does the coin stay on the record?") before the
  payoff; one setup number pair (forty five and seventy eight turns a
  minute, naming the panels) and one payoff ("in under a fifth of a
  second", the printed bound 0.1797 < 0.2000 s); no digits; the
  mechanism sentences name only what the frame shows ("Going round takes
  grip, and faster takes more. At seventy eight, the record asks for more
  grip than the coin has.").
- Voice (media/coinrecord/voice.log): pass 1 (110 words, 10:32:16) ok
  33.75 s, no mishearing, but timing.log put "Let go" about 1 s before
  the second release and "Below, it slips, spirals out" after the 78
  coin had already left the rim, so the narration was reordered (the
  bottom panel described first after "Let go", "each one" added before
  "held", the mechanism line shortened); pass 2 (108 words, 10:33:28) ok
  33.02 s, no mishearing. voice.wav ends at 33.62 s of video.
- timing.log (pass 2, voice offset 0.6 s; whisper's own spelling):

```
  0.60 -   4.06  Does the coin stay on the record?
 45 turns a minute on top.
  4.06 -   5.50  78 below.
  5.50 -   6.66  The same coin.
  6.66 -   9.96  the same grip, each one held in place by a fingertip.
  9.96 -  10.82  Let go!
 10.82 -  11.46  below.
 11.46 -  12.55  The coin slips,
 12.55 -  13.75  spirals out
 13.75 -  15.70  and is thrown off the rim onto the deck.
 15.70 -  16.48  On top.
 16.48 -  21.08  The coin rides round with the record, going round takes
 grip and faster takes more.
 21.08 -  22.28  At 78.
 22.28 -  29.57  The record asks for more grip than the coin has.
 So, does the coin stay on the record?
 At 45, yes.
 It stays.
 29.57 -  31.24  At 78, no.
 31.24 -  33.62  It is off the record in under a fifth of a second.
voice 33.02 s, ends at 33.62 s of video
```

- Schedule and sync: the fingertips lift at 1.0, 11.0, 21.0, 31.0 s; the
  78 coin crosses the rim at 2.80, 12.80, 22.80, 32.80 s and is at rest
  on the deck at 5.77, 15.77, 25.77, 35.77 s; the top event row lights
  at 2.0, 12.0, 22.0, 32.0 s; the crossfades run 9.4-10.0, 19.4-20.0,
  29.4-30.0, 39.4-40.0 s. The question (0.60-2.25 s in the captions) runs
  over the first release and the first slide; "Forty five turns a minute
  on top, seventy eight below. The same coin, the same grip, each one
  held in place by a fingertip." 2.25-9.96 over the first skid, the rest
  and the crossfade back to the held setup; "Let go!" 9.96-10.82 just
  before the 11.0 s lift; "Below, the coin slips, spirals out" 10.82-13.75
  over the slide (11.0-12.8) and "and is thrown off the rim onto the
  deck." 13.75-15.70 over the skid (to 15.77); "On top, the coin rides
  round with the record." 15.70-18.5 with the top coin riding; "Going
  round takes grip, and faster takes more. At seventy eight, the record
  asks for more grip than the coin has." 18.5-25.10 over the cycle-3
  release (21.0) and exit (22.8); "So, does the coin stay on the record?"
  25.10-27.20 (the card rises from 26.9 s and is full at 27.5); "At forty
  five, yes. It stays." 27.20-29.77 with "stays on: needs 0.23, has 0.30"
  lit and the card's "45: stays, needs 0.23 of its 0.30 grip"; "At
  seventy eight, no." 29.77-31.36 over the cycle-4 crossfade and the
  held setup; "It is off the record in under a fifth of a second."
  31.36-33.62 over the fourth release (31.0) and exit (32.8), with "off
  the record in 0.18 s" lit from 32.8 s and the card's "78: off the
  record in 0.18 s, needs 0.68" on screen throughout; the title fades
  back in over 39.5-40.0 s.
- Smoke frames viewed before the render (--frames 0.0, 1.0, 1.5, 2.0,
  2.5, 2.8, 3.5, 5.0, 6.0, 9.7, 24.5, 25.1, 39.7, 39.983; eight viewed:
  0.0, 1.5, 2.5, 3.5, 6.0, 9.7, 25.1, 39.7; then 0.0 and 2.6 again after
  the fingertip pad was offset and the trail widened): the title and
  both held coins; the release with the readouts in gold; the 78 coin
  sliding out with its trail and the top event row lit; the coin
  skidding right on the deck with the HUD clock; the coin at rest; the
  mid-crossfade ghost of both states; the six-line card inside the
  frame; the loop fade. All text inside the frame.
- Render (media/coinrecord/render.log, 10:35:16-10:35:42): loop check 0
  px, periodicity check 0 px, loop step 1365 px (the coins, pads and
  markers move 1 to 2 px every frame before the release, so any two
  consecutive frames differ: frame 0 against frame 1 differs in 665 px
  by the same measure; the loop-step pixels sit in rows 548-1193 and
  columns 314-508, the coin and label region of both bands), footage
  40.00 s at 60 fps, 2400 frames, md5
  ff549edba5def07b0559da2b978c6dfe.
- Compose (media/coinrecord/compose.log, 10:35:42-10:35:54): music seed
  107, 40.00 s; captions 22 pauses detected, 22 matched (max chunk start
  shift 1.413 s against word-count timing; no fallback); contact sheet
  8x5 at 1 fps; final.mp4 40.000000 s; preview.mp4 40.066667 s.
- Text widths (PIL ImageFont.getlength, DejaVuSans-Bold, asserted < 950
  px): overlay@34 875, title@56 583 / 459, legend@40 757, clock@28 390
  (held 69), labels@40 403 / 403, sublabels@28 590, readouts@28 288,
  events@40 687 / 515, state words@28 69 / 182 / 105 / 371 / 300, payoff
  lines@40 754 / 828 / 878 / 832 / 909 / 574 px.

### Local QA

- Frames extracted from media/coinrecord/final.mp4 (never edited) with
  ffmpeg -ss T and viewed at full resolution:
  - 0.00: overlay, the title "Does the coin stay / on the record?", both
    records at angle 0 with the coins held under the grey fingertip pads
    at the upper left (a gold sliver of each coin showing), "held" and
    "needs 0.23 of grip" / "needs 0.68 of grip" in white, no caption, no
    card.
  - 1.00 (the release instant): the pads still over the coins, which
    have ridden a little clockwise; "rides round" / "sliding" and both
    grip readouts in gold; caption "Does the coin stay".
  - 2.10 (0.11 s real after the release): the top coin riding near the
    top of its record; the 78 coin a little outside its circle with a
    short coral trail; "stays on: needs 0.23, has 0.30" lit; caption "on
    the record?".
  - 12.90 (cycle 2, clock "0.190 s after the release"): legend and
    clock; the 78 coin just past the rim at the upper right with its
    trail on the vinyl, "off the record, skidding" and "off the record in
    0.18 s" lit; the top coin riding; caption "slips, spirals out,".
  - 27.30 (payoff + 0.4 s): the card rising in dim gold under the
    caption "At forty five, yes."; the top coin riding at the lower
    right, the 78 coin at rest on the deck at the end of its skid mark
    with the trail turned to the lower left of its record; clock 0.630
    s.
  - 28.70 (payoff + 1.8 s): the card full in gold, six lines between y
    1572 and about 1812; caption "At forty five, yes."; both event rows
    lit.
  - 32.90 (cycle 4, 0.190 s after the release): the 78 coin just over
    the rim again, "off the record in 0.18 s" lit, the card full, caption
    "in under a fifth of".
  - 39.983 (frame 2399): the title back, both coins held under the pads,
    the same picture as 0.00; no caption, no card.
  Nothing clipped at the frame edges, no text in the caption band.
- sheet.png (8x5 at 1 fps): four identical cycles: the held setup, the
  release, the 78 coin flung off to the right and skidding to rest while
  the 45 coin rides round, the crossfade back; captions under; the card
  from the tile at 27 s.
- Question timing: on screen from frame 0 in the title; spoken from 0.60
  s of video (speech from 0 s in voice.wav plus the 0.6 s offset); the
  captions "Does the coin stay" 0.600-1.543 and "on the record?"
  1.543-2.251 s; repeated at 25.10-27.20 s ("So, does the coin" /
  "stay on the record?").
- Captions: 34 chunks of at most 20 characters, 0.600-33.619 s; the
  concatenated caption text equals narration.txt word for word (108
  words, compared by script with the overlay drawtext excluded).
- Payoff number on screen when spoken: "off the record in 0.18 s" lit
  from 32.8 s (and from 22.8 to 29.4 s before it) and the card's "78: off
  the record in 0.18 s, needs 0.68" full from 27.5 s while "It is off the
  record in under a fifth of a second." is spoken 31.36-33.62 s (captions
  "It is off the record" 31.363-32.303, "in under a fifth of"
  32.303-33.243, "a second." 33.243-33.619); "stays on: needs 0.23, has
  0.30" and the card's "45: stays, needs 0.23 of its 0.30 grip" on
  screen while "At forty five, yes. It stays." is spoken 27.20-29.77 s.
- Footage signalstats: overlay band (rows 96-130) and caption band (rows
  1440-1530) YMAX 28 in all 2400 footage frames (the raw frames 0, 1 and
  2398 peak at 18 of 255 in those rows); both bands hold only the
  background (11, 14, 18).
- Loop: render.log loop check 0 px and periodicity check 0 px on the raw
  frames; the renderer's frame 2399 equals frame 0 exactly (0 px, max
  channel difference 0).
- ffprobe final.mp4: h264 1080x1920 yuv420p 60/1, 2400 frames, duration
  40.000000 s, aac 22050 Hz mono, atoms ftyp, moov, free, mdat (moov
  before mdat, faststart), 3,708,674 bytes.
- md5sum media/coinrecord/final.mp4: c7ccff04b968551ef50ed2c52741d17c.
- Narrated numbers against measure.log: "forty five turns a minute" (45
  rpm, top panel), "seventy eight" (78 rpm, bottom panel), "At forty
  five, yes. It stays." (it stays and rides round with the record), "At
  seventy eight, no. It is off the record" (the coin's radius reaches
  the rim R = 15 cm at 0.1797 s), "in under a fifth of a second" (under
  one fifth of a second (0.1797 < 0.2000 s)). All on printed lines.
- Metadata number check by script: 94 distinct numbers in the title and
  description, none missing from measure.log (commas stripped; the
  on-screen strings "0.18 s", "0.23", "0.68", "52 turns a minute", "13
  cm", "4.4 cm" and "24 cm" are on the text-widths line).

### Metadata

- Title (91 characters, ASCII, no < or >): Does the coin stay on the
  record? At 45 rpm it stays; at 78 rpm it is off the rim in 0.18 s
- Description: 4,602 characters, ASCII, no arrows; one setup paragraph
  (the model, every constant, the static test, the limit formula, the
  RK4 slide, the skid, 1/10 speed, 4 runs in 40 s, no seed), "Measured:"
  bullets (the limit, both panels, the slide with its exit numbers and
  table, the skid, 33 1/3, 52, 60 and 100 rpm, the rim and other grips,
  the checks), a "Why:" paragraph, the rerun line, the AI line.
- Tags (12): does the coin stay on the record, coin on a record, coin on
  a turntable, turntable physics, friction, centripetal force, 45 rpm vs
  78 rpm, lazy susan, physics, physics visualization, simulation, shorts.
- categoryId "27", privacyStatus "private", containsSyntheticMedia true,
  selfDeclaredMadeForKids false.

### Deviations from the brief

- "flung" is "thrown" in the narration: whisper returned "plon" in the
  words pre-test.
- The narration describes the bottom panel first after "Let go" (brief:
  top then bottom) so the words follow the 78 coin's slide and skid in
  real time; "On top, the coin rides round with the record" follows.
  108 words (brief: 100-110).
- The payoff is spoken as "in under a fifth of a second" (brief: "in a
  fifth of a second" or "in point one eight seconds"): the sim prints
  the bound (0.1797 < 0.2000 s) so the spoken words are a printed fact;
  the exact 0.18 s is on the event row, the card, the title and the
  description.
- "ten centimeters" is not narrated (the overlay, the sublabel, the card
  and the description carry 10 cm), so the narration has only the two
  speeds as setup numbers.
- The right column carries a state word on the label row (held, rides
  round, sliding, off the record, skidding, at rest on the deck) in
  addition to the brief's grip readout, which sits on the second row.
- A thin skid mark is drawn on the deck from the rim point to the coin,
  and the fingertip pad is offset 6 px left and 7 px up so a sliver of
  the coin shows under it.
- g = 9.807 m/s^2 as in the orchestrator's check scripts (deskchain used
  9.80665).
- The render log's loop-step check is 1365 px rather than 0: the coins
  ride round before the release, so consecutive frames always differ by
  1 to 2 px of coin motion (frame 0 against frame 1: 665 px); the loop
  and periodicity checks are 0 px.
- The 52 rpm description run's angle is unwrapped along the path (289.7
  degrees round); a first print wrapped it to -70.3 degrees.
- payoff_t 26.9 s so the card is full as "At forty five, yes." starts at
  27.20 s.

## Niche note

  [produced 2026-10-03 as "Does the coin stay on the record? At 45 rpm
  it stays; at 78 rpm it is off the rim in 0.18 s"; measured a coin 10 cm
  from the centre of a 30 cm record with grip 0.3 on the record and the
  still deck round it (g 9.807, RK4 at 1e-05 s in the deck frame, the rim
  crossing by bisection, no seed): 45 rpm needs 0.2264 of grip and rides
  round (holds a coin out to 13.25 cm); 78 rpm needs 0.6803 (holds only
  to 4.41 cm) and is off the rim 0.1797 s after the fingertip lifts, 69.2
  degrees round the centre, at 0.8758 m/s (0.689 m/s relative to the
  record) while the record turns 84.1 degrees (the coin lags by 14.8
  degrees), then skids 13.0 cm on the deck in 0.298 s and rests 0.477 s
  after the release; the limit at 10 cm sqrt(mu g / r) = 51.80 rpm; 33
  1/3 rpm needs 0.1242 and holds out to 24.15 cm; 52 rpm off at 0.9514 s
  (289.7 degrees round), 60 rpm at 0.3199 s (103.2 degrees, 0.7598 m/s,
  a 9.8 cm skid), 100 rpm at 0.1241 s (1.0737 m/s, 19.6 cm); the
  half-step rerun within 7.4e-15 s; shown at 1/10 speed on a 10 s cycle,
  4 cycles in 40 s; task 20261003-101703]

## Upload

- Orchestrator gate passed at 2026-10-03T10:53:41+03:00 (frames, sheet, ffprobe, md5 c7ccff04b968551ef50ed2c52741d17c, metadata, captions, measure.log against /tmp/day35 closed forms).
- Upload attempt 1 of 5 for the quota day that began 2026-10-03T10:00 EEST, recorded at 2026-10-03T10:53:41+03:00 before starting scripts/yt-upload.py coinrecord (zero attempts on record since the boundary).
- Uploaded private as P6pelJ2izjA at 2026-10-03T10:53:47+03:00 (scripts/yt-upload.py, channels.list 1 unit + videos.insert 1,600 units; media/coinrecord/upload.log).
- scripts/yt-qa.py coinrecord P6pelJ2izjA --wait --publish in the foreground at 10:53:58: gate 15 of 15 (processed, hd, 1080x1920, title, description and tags match, category 27, not made for kids, PT41S, private before publish), published at 2026-10-03T10:54:30+03:00, re-read public (media/coinrecord/publish.log); 54 units.
- Published: https://youtu.be/P6pelJ2izjA

### Quota

- Attempt 1 of 5 for the quota day that began 2026-10-03T10:00 EEST; 1,655 units (1 + 1,600 + 54); day total after this attempt 1,655 of 10,000.
