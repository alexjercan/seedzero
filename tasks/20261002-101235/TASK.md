# Produce short: Bat sweet spot, a stick on ice hit two thirds along beside a hit at the tip

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day34

## Goal

Backlog idea (trend research 2026-09-25, task 20260925-101408, pillar 2
chaos and physics, rigid body; read the full entry under "Added by trend
research 2026-09-25" in docs/niche.md): "Bat sweet spot: a free 85 cm,
0.9 kg stiff stick struck by a 145 g ball at 30 m/s, 57 cm from the
handle end beside a hit at the tip; measure the handle end's speed after
the hit; expect 0.00 m/s at 56.7 cm (two thirds of the length, the
centre of percussion of a uniform rod) and the handle end kicking back
at 8.8 m/s from a tip hit (11.8 m/s if elastic), handle speed (J / m)(1
- 6 d / L); a real bat's sweet spot is also set by its bending nodes, so
say "stiff stick"; rigid impulse, closed form; repeat the hit;
deterministic, no seed (peg: World Series, late October 2026)."

Orchestrator notes (2026-10-02, before this brief). The model: a uniform
stiff stick, L = 0.85 m, M = 0.9 kg, at rest on frictionless ice seen
from above (no force in the plane before or after the hit, so after the
hit it moves as a free rigid body: the centre at a constant velocity, a
constant spin); a ball m_b = 0.145 kg at v0 = 30 m/s hits it square
(perpendicular to the stick) at a distance d from the handle end; an
instantaneous frictionless hit with restitution e = 0.5 (a chosen value
for a ball on wood; say so; e = 1 gives 11.76 m/s at the tip and e = 0
gives 5.88, and the sweet spot is the same for any e). Impulse J = (1 +
e) v0 / (1 / m_b + 1 / M + r^2 / I) with r = d - L / 2 and I = M L^2 /
12; after the hit the centre moves at J / M along the ball's direction,
the spin is J r / I, the ball keeps v0 - J / m_b, and the handle end's
velocity (perpendicular to the stick, positive along the ball's
direction) is J / M - (J r / I)(L / 2) = (J / M)(4 - 6 d / L): zero at
d = 2 L / 3 exactly, for any ball, any speed and any restitution. Top
panel: the hit at d = 2 L / 3 = 56.67 cm. Bottom panel: the hit at the
tip, d = L = 85 cm. The handle end is where a hand would hold a bat; the
spot where it does not move at the hit is the centre of percussion, and
a hand there would feel no jolt (say "stiff stick" everywhere; the
description says a real bat also bends, so its felt sweet spot is set
by its bending nodes too).

Checks, not facts (orchestrator closed forms, /tmp/day34/closed.log):
sweet spot hit at 56.67 cm: J 5.3712 N s, centre 5.968 m/s, spin 14.04
rad/s, handle end 0.000 m/s, tip end 11.94 m/s, the ball bounces back at
-7.043 m/s. Tip hit at 85 cm: J 3.9679 N s, centre 4.409 m/s, spin 31.12
rad/s, handle end -8.818 m/s (backward, toward where the ball came from,
twice the centre's speed), tip end 17.64 m/s, the ball carries on at
+2.635 m/s. For the description: a middle hit at 42.5 cm: J 5.620 N s,
centre 6.244 m/s, no spin, handle +6.244 m/s; a hit at 57 cm: handle
-0.140 m/s; a hit at the handle end itself: the tip end stays still and
the handle end takes 17.6 m/s (the mirror); e = 1 tip hit -11.757 m/s,
e = 0 -5.878 m/s. After the hit the stick moves freely, so the handle
end's velocity at the instant is the claim: after the sweet hit the
handle end stands still at the instant and the spin then sweeps it (1.67
m/s after 20 ms, 4.10 after 50 ms, 7.71 after 100 ms: a cycloid cusp;
its drawn trail shows the cusp), and after the tip hit it jumps back 4.4
cm in 5 ms, 8.6 cm in 10 ms, 16.0 cm in 20 ms, then the spin brings it
round (a loop in its trail). The readout must therefore say "handle end
at the hit", not a live speed. Print the momentum and angular momentum
balance of the hit (ball plus stick, before and after, to 1e-12) and the
energy lost (the fraction (1 - e^2) of the relative-motion energy); scan
d from 0 to L in 1 cm steps and print the sign change of the handle
end's velocity between 56 and 57 cm with the exact root 2 L / 3 = 56.667
cm; print the approach (the ball's position against time) and the free
motion after the hit (constant velocity and spin, no ODE: compute the
ends' positions in closed form) with the times the ends and the centre
leave the band; half-scale check of nothing is needed, but do verify
(J / M)(4 - 6 d / L) against the impulse arithmetic for both hits. State
every number above as a check the sim must print, not as a fact.

Drawing: top view, two bands (y 330-880 and 880-1430), the same ice, the
same stick and ball in both at 400 px per metre. The stick a 340 px rod
drawn vertical (along y) with its handle end at the bottom, marked with
a hand ring (a 56 px circle in the band's colour) that stays where the
handle end was at the hit; a muted tick on the stick at the hit point
("2/3" / "tip"); the ball (a 44 px disc) enters from the right edge,
moving left at 30 m/s, hits the stick at the tick; after the hit the
stick moves left and spins, the ball goes back (sweet spot) or follows
slowly (tip); the handle end leaves a gold trail (the cusp against the
backward loop). Keep the stick's centre at the band's vertical middle so
the spinning stick stays inside the band until it leaves through the
left edge (assert the stick's ends never cross the band's top or bottom
rows). Labels in the band's top row, inside the band: "hit two thirds
along, 56.7 cm" / "hit at the tip, 85 cm" (40 px), "stiff stick 85 cm,
ball 30 m/s" (28 px); a gold event row at the band's bottom row: "handle
end at the hit: 0.00 m/s" / "handle end at the hit: 8.8 m/s back" lit at
the hit and held. Shown at 1/20 speed: the ball crosses the approach in
about 0.6 s of video, the sweet-spot handle end stays put for about 0.4
s of video before the spin sweeps it, the tip hit's handle end jumps 64
px back in 0.4 s; the stick's centre moves 120 px per second and leaves
the band in about 5 s; cycle 8 s with the hit near 1.0 s in and a reset
crossfade at the end, 5 cycles in 40 s, the last frame equal to the
first. Nothing in the overlay rows 96-130 or under the captions from y
1440.

Day thirty-four, third slot. Chosen because "where is the sweet spot" is
a question every bat, racket and hammer user has asked, the panels end
visibly differently (the handle end stands still against the handle end
kicking back), the payoff is an exact fraction with a closed form that
holds for any ball and any speed, and the World Series peg opens in late
October. Question in the first two seconds: "Where is the sweet spot on
a bat?" (keep the question identical in the title, the hook and the
payoff; the model is a stiff stick, so say "a stiff stick stands in for
the bat" in the setup). Setup number: a ball at thirty meters a second.
Payoff: two thirds of the way along, the handle end does not move at
all; at the tip, it kicks back at nearly nine meters a second (eight
point eight). The middle hit, the restitution variants and the trails'
shapes go to the card and the description. Whisper risks: "sweet spot"
(pre-test), "bat" and "stick" (pre-test), "two thirds" and "two thirds
of the way along" (pre-test; 2026-09-30 "two sevenths" came back "two
seventh"; "two thirds along the stick" as a fallback), "handle" /
"handle end" (pre-test), "kicks back" (pre-test), "ice" (passed
2026-09-28), "eight point eight meters a second" (pre-test; "nearly nine
meters a second" as a fallback); avoid "do you"; avoid "pull". Pre-test
hooks with scripts/voiceover.sh and keep the one whose question lands
earliest under two seconds. Measure every fixed text line with PIL
before rendering and keep every line under 950 px, and the title under
100 characters with no < or >. Music seed 106. Templates: sims/cutshot
(top view, balls, an instantaneous hit, trails, reset fade), sims/icerod
(a stick drawn as a rod with marked ends), sims/deskchain (bands, cycle,
layout asserts). Sim name sweetspot: sims/sweetspot/sweetspot.py,
projects/sweetspot/, media/sweetspot/.

## Claim (expected; the sim's numbers replace these)

A stiff 85 cm, 0.9 kg stick free on ice, hit square by a 145 g ball at
30 m/s with restitution 0.5: hit two thirds along (56.67 cm from the
handle end) the handle end's speed at the hit is 0.000 m/s (centre 5.97
m/s, spin 14.0 rad/s, the ball back at 7.0 m/s); hit at the tip the
handle end kicks back at 8.82 m/s (centre 4.41 m/s, spin 31.1 rad/s,
the ball on at 2.6 m/s). The sweet spot is at exactly 2 L / 3 for any
ball, speed or restitution, (J / M)(4 - 6 d / L) = 0. Narrated: a stiff
stick on ice stands in for the bat, a ball at thirty meters a second
(setup); two thirds of the way along, the handle end does not move at
all; at the tip it kicks back at eight point eight meters a second
(payoff). Card: the question; two thirds along: handle end 0.00 m/s; at
the tip: 8.8 m/s back; the spot is 2/3 of the stick for any ball at any
speed; middle hit: the whole stick moves at 6.2 m/s, no spin;
restitution 1: 11.8 m/s back. Description: the model statement, the
impulse formula, the handle-end formula, the momentum and energy
balances, the scan, the trails, the real-bat caveat.

## Claim

A stiff 85 cm, 0.9 kg stick free on frictionless ice, hit square by a
145 g ball at 30 m/s with restitution 0.5: hit two thirds along (56.667
cm from the handle end) the handle end's velocity at the hit is +0.0000
m/s (J 5.3712 N s, centre 5.968 m/s, spin 14.04 rad/s, the ball back at
7.043 m/s, the tip end 11.94 m/s); hit at the tip the handle end kicks
back at 8.818 m/s, twice the centre's speed (J 3.9679 N s, centre 4.409
m/s, spin 31.12 rad/s, the ball on at 2.635 m/s, the tip end 17.64 m/s).
The sweet spot is exactly 2 L / 3 for any ball, speed or restitution: (J
/ M)(4 - 6 d / L) = 0 at 56.667 cm (the 1 cm scan changes sign once,
between 56 cm at +0.282 m/s and 57 cm at -0.140 m/s; the root stays zero
within 1.8e-15 m/s at 15 and 45 m/s, 50 and 500 g, e 0 and 1). Momentum
(4.350000 kg m/s) and angular momentum (0.616250 and 1.848750 kg m^2/s)
balance with a printed difference of 0.0; the energy lost, 40.284 J
(61.7 percent) and 29.759 J (45.6 percent), equals (1 - e^2) of the
relative-motion energy within 2.1e-14 J. Narrated: a stiff stick on ice
stands in for the bat, a ball at thirty meters a second (setup); two
thirds of the way along, the handle end does not move at all; hit the
tip, it kicks back at eight point eight meters a second (payoff). Card:
the question; hit 2/3 along: handle end 0.00 m/s; hit the tip: handle
end 8.8 m/s back; 2/3 of the stick, any ball, any speed; hit the middle:
6.2 m/s, no spin; bouncier ball, e = 1: 11.8 m/s back. Description: the
model statement, the impulse and handle-end formulas, both hits, the
scan and the invariance, the trails (cusp and loop), the other hits
(middle, 56, 57, one third, the handle end itself), e = 1 and 0, the
balances, the real-bat caveat.

## Evidence

### Measurements

media/sweetspot/measure.log (`nix develop -c python3
sims/sweetspot/sweetspot.py --measure-only`, 2026-10-02 10:40:13 EEST,
final manifest and sim; the same numbers as the 10:36 pass that preceded
the smoke frames, with the on-screen strings added to the text-widths
line):

```
Fri Oct  2 10:40:13 AM EEST 2026
setup: the same ice in both panels, seen from above: a uniform stiff stick of 85 cm and 0.9 kg lies at rest on frictionless ice (no force in the plane before or after the hit, so after the hit it moves as a free rigid body: its centre at a constant velocity, a constant spin), I = M L^2 / 12 = 0.054187 kg m^2; a ball of 145 g at 30 m/s hits it square (perpendicular to the stick) at a distance d from the handle end in an instantaneous frictionless hit with restitution e = 0.5 (a chosen value for a ball on wood; the sweet spot is the same for any e); impulse J = (1 + e) v0 / (1 / m_b + 1 / M + r^2 / I) with r = d - L / 2; top panel the hit at d = 2 L / 3 = 56.67 cm, bottom panel the hit at the tip, d = L = 85 cm; the free motion after the hit in closed form (no ODE); shown at 1/20 speed on a 8 s cycle (480 frames) with the hit 1.2 s into the cycle, 5 cycles in 40 s; drawn at 400 px per metre (the stick 340 px, the ball a 44 px disc); deterministic, no seed
hit two thirds along (top panel): d = 56.667 cm, r = d - L / 2 = 14.167 cm, r^2 / I = 0.37037 per kg, 1 / m_b + 1 / M + r^2 / I = 8.37803 per kg; impulse J = 5.3712 N s; after the hit the centre moves at J / M = 5.968 m/s along the ball's direction, the spin is J r / I = 14.04 rad/s, the ball bounces back at 7.043 m/s; the handle end's velocity J / M - (J r / I)(L / 2) = +0.0000 m/s = (J / M)(4 - 6 d / L) = +0.0000 m/s (diff +0.0e+00): 0.000 m/s still; the tip end 11.94 m/s; momentum before and after the hit 4.350000 = 4.350000 kg m/s (diff +0.0e+00), angular momentum about the stick's centre 0.616250 = 0.616250 kg m^2/s (diff +0.0e+00); kinetic energy 65.250 J before, 24.966 J after: 40.284 J lost = 61.7 percent, the closed form (1 - e^2) of the relative-motion energy 40.284 J (diff +2.1e-14)
hit at the tip (bottom panel): d = 85.000 cm, r = d - L / 2 = 42.500 cm, r^2 / I = 3.33333 per kg, 1 / m_b + 1 / M + r^2 / I = 11.34100 per kg; impulse J = 3.9679 N s; after the hit the centre moves at J / M = 4.409 m/s along the ball's direction, the spin is J r / I = 31.12 rad/s, the ball carries on at 2.635 m/s; the handle end's velocity J / M - (J r / I)(L / 2) = -8.8176 m/s = (J / M)(4 - 6 d / L) = -8.8176 m/s (diff -1.8e-15): 8.818 m/s back toward where the ball came from; the tip end 17.64 m/s; momentum before and after the hit 4.350000 = 4.350000 kg m/s (diff +0.0e+00), angular momentum about the stick's centre 1.848750 = 1.848750 kg m^2/s (diff +0.0e+00); kinetic energy 65.250 J before, 35.491 J after: 29.759 J lost = 45.6 percent, the closed form (1 - e^2) of the relative-motion energy 29.759 J (diff +7.1e-15)
sweet spot: the handle end's velocity (J / M)(4 - 6 d / L) is zero at d = 2 L / 3 = 56.667 cm for any ball, any speed and any restitution (the centre of percussion of a uniform rod); the scan of d from 0 to 85 cm in 1 cm steps changes sign once, between 56 cm (+0.282 m/s) and 57 cm (-0.140 m/s); at the root the handle end's velocity is +0.0e+00 m/s; the handle end moves along the ball at a hit under 56.7 cm and back at a hit over it
for the description (velocities along the ball's direction, negative = back): hit at the handle end itself (0 cm): J 3.968 N s, centre 4.409 m/s, spin -31.12 rad/s, handle end +17.635 m/s, tip end -8.818 m/s, the ball +2.635 m/s; hit in the middle (42.5 cm): J 5.620 N s, centre 6.244 m/s, no spin, handle end +6.244 m/s, tip end +6.244 m/s, the ball -8.756 m/s; hit 56 cm from the handle end (56 cm): J 5.393 N s, centre 5.992 m/s, spin 13.44 rad/s, handle end +0.282 m/s, tip end +11.703 m/s, the ball -7.194 m/s; hit 57 cm from the handle end (57 cm): J 5.360 N s, centre 5.955 m/s, spin 14.34 rad/s, handle end -0.140 m/s, tip end +12.051 m/s, the ball -6.965 m/s; hit one third along (28.333 cm, the mirror of the sweet spot): J 5.371 N s, centre 5.968 m/s, spin -14.04 rad/s, handle end +11.936 m/s, tip end +0.000 m/s: the tip end stays still; tip hit with restitution 1: J 5.291 N s, centre 5.878 m/s, handle end -11.757 m/s, the ball -6.486 m/s; tip hit with restitution 0: J 2.645 N s, centre 2.939 m/s, handle end -5.878 m/s, the ball +11.757 m/s; the hit at the handle end is the mirror of the tip hit (the handle end takes the tip end's 17.635 m/s and the tip end goes back at 8.818 m/s); the handle end's velocity at the two-thirds hit stays zero with ball at 15 m/s: +0.0e+00, ball at 45 m/s: +0.0e+00, a 50 g ball: +0.0e+00, a 500 g ball: -1.8e-15, restitution 1: +1.8e-15, restitution 0: +8.9e-16 m/s
free motion after the hit (closed form: the centre at J / M, the angle J r t / I): two-thirds hit: the handle end's speed at the instant is 0.00 m/s, the spin then sweeps it (20 ms: 1.67 m/s (2 (J / M) sin(omega t / 2) = 1.67), moved 1.7 cm; 50 ms: 4.10 m/s (2 (J / M) sin(omega t / 2) = 4.10), moved 10.3 cm; 100 ms: 7.71 m/s (2 (J / M) sin(omega t / 2) = 7.71), moved 39.7 cm); its trail is a cycloid with a cusp at the hand ring because (L / 2) omega = 5.968 m/s equals the centre's 5.968 m/s; a full turn takes 0.4474 s real = 8.95 s of video; tip hit: the handle end jumps back at 8.82 m/s (5 ms: 4.4 cm back, 8.90 m/s; 10 ms: 8.6 cm back, 9.13 m/s; 20 ms: 16.0 cm back, 9.98 m/s), reaches 22.6 cm back and the spin brings it round in a loop because (L / 2) omega = 13.23 m/s is more than the centre's 4.409 m/s; a full turn takes 0.2019 s real = 4.04 s of video
approach and exits (video time, 1/20 speed): the ball enters the band at the right edge 1.12 s before the hit (0.08 s into the cycle, after the fade), crosses at 600 px/s and meets the stick at x 429 px; sweet: the centre crosses the left edge 3.35 s after the hit (it moves 119 px/s), the whole stick is out of the band after 4.83 s (6.03 s into the cycle; at the fade's start its sweep reaches x -163 px at most); the ball leaves through the right edge 4.78 s after the hit; tip: the centre crosses the left edge 4.54 s after the hit (it moves 88 px/s), the whole stick is out of the band after 6.54 s (7.74 s into the cycle; at the fade's start its sweep reaches x 30 px at most); the ball drifts left at 53 px/s and is at x 71 px at the cycle's end; after the hit (one hit in the model) the ball's centre comes closest to the stick at 41.0 px = 10.2 cm (two thirds, 0.04 s after the hit) and 22.1 px = 5.5 cm (tip, 1.71 s after the hit: the handle end swinging back up through the ball's row); the drawn 44 px ball touches the 14 px stick at 29 px, so the tip hit's handle end cap passes inside the drawn ball's rim by 6.9 px on 7 of 408 frames (the ball is drawn on top); the two-thirds hit clears by 12.0 px
schedule (video time, 1/20 speed): cycles of 8 s start at -8.00, 0.00, 8.00, 16.00, 24.00, 32.00 s (the first -0.00 s before the first frame); the ball enters at 0.08, 8.08, 16.08, 24.08, 32.08 s; the hit 1.2 s into each cycle at 1.20, 9.20, 17.20, 25.20, 33.20 s (the event rows light); the two-thirds hit's handle end stays inside its ring for about 0.4 s of video (7 px moved) and the tip hit's handle end is 64 px back by then; the two-thirds stick is out of its band at 6.03, 14.03, 22.03, 30.03, 38.03 s and the tip stick at 7.74, 15.74, 23.74, 31.74, 39.74 s; the reset crossfade runs over the last 0.6 s of each cycle (from 7.40, 15.40, 23.40, 31.40, 39.40 s; the readouts out over its first half and in over its second); on the first frame the cycle is 0.00 s in (-0.060 s real: the ball 720 px from the stick); title until 3 s; payoff card from 22.9 s; the title fades back in over the last 0.5 s and the last frame repeats the first (the scene is periodic: 40 s holds exactly 5 cycles)
text widths (the on-screen strings verbatim): overlay@34 896 px 'stick 85 cm | ball 30 m/s | 1/20 speed | no seed', title line 1@56 767 px 'Where is the sweet spot', title line 2@56 292 px 'on a bat?', legend@40 763 px 'same stick, same ball, 1/20 speed', clock@28 317 px '0.123 s after the hit', clock before@28 218 px 'before the hit', label sweet@40 653 px 'hit two thirds along, 56.7 cm', event sweet@40 698 px 'handle end at the hit: 0.00 m/s', ball after sweet@28 309 px 'ball back at 7.0 m/s', hit label sweet@24 42 px '2/3', label tip@40 450 px 'hit at the tip, 85 cm', event tip@40 790 px 'handle end at the hit: 8.8 m/s back', ball after tip@28 274 px 'ball on at 2.6 m/s', hit label tip@24 37 px 'tip', sublabel@28 444 px 'stiff stick 85 cm, ball 30 m/s', ball before@28 173 px 'ball 30 m/s', hand@24 68 px 'hand', payoff line 1@40 763 px 'where is the sweet spot on a bat?', payoff line 2@40 773 px 'hit 2/3 along: handle end 0.00 m/s', payoff line 3@40 806 px 'hit the tip: handle end 8.8 m/s back', payoff line 4@40 806 px '2/3 of the stick, any ball, any speed', payoff line 5@40 706 px 'hit the middle: 6.2 m/s, no spin', payoff line 6@40 782 px 'bouncier ball, e = 1: 11.8 m/s back'
row check: the label row (alone on its row) ends at x 693 px; on the second row the sublabel ends at x 484 px and the ball readout starts at x 731 px; the rows end 96 px under the band top; the stick stands at x 400 px with its centre 292 px under the band top and its sweep (any angle, caps included) spans 115 to 469 px; the hand ring reaches 490 px; the ball's lane is 213 to 257 px (two thirds) and 100 to 144 px (tip); the event row spans 496 to 540 px under the band top and x 145 to 935 px (widest 790 px); the hit label starts at x 335 px and the hand label at x 292 px; each band is 550 px tall (y 330 to 880 and 880 to 1430); the caption band starts at y 1440; the title rows end at y 280 and the overlay band ends at y 130
exit 0
Fri Oct  2 10:40:14 AM EEST 2026
```

Brief checks (every number is a line the sim printed):

- Sweet hit at 56.67 cm: J 5.3712 N s, centre 5.968 m/s, spin 14.04
  rad/s, handle end 0.000 m/s, tip end 11.94 m/s, the ball back at 7.043
  m/s: passed (the handle end +0.0000 m/s by the impulse arithmetic and
  +0.0000 m/s by (J / M)(4 - 6 d / L), diff +0.0e+00).
- Tip hit at 85 cm: J 3.9679 N s, centre 4.409 m/s, spin 31.12 rad/s,
  handle end -8.818 m/s (twice the centre's 4.409), tip end 17.64 m/s,
  the ball on at +2.635 m/s: passed (the two forms within -1.8e-15 m/s).
- (J / M)(4 - 6 d / L) verified against the impulse arithmetic for both
  hits: passed (diffs +0.0e+00 and -1.8e-15 m/s).
- Middle hit at 42.5 cm: J 5.620 N s, centre 6.244 m/s, no spin, handle
  end +6.244 m/s: passed (the ball back at 8.756 m/s).
- Hit at 57 cm: handle end -0.140 m/s: passed; 56 cm: +0.282 m/s
  (printed for the scan).
- Hit at the handle end itself: the brief expected the tip end to stay
  still and the handle end to take 17.6 m/s. The sim gives handle end
  +17.635 m/s and tip end -8.818 m/s, the mirror of the tip hit, so the
  tip end does not stay still there. The tip end stays still at the
  mirror of the sweet spot, one third along (28.333 cm): handle end
  +11.936 m/s, tip end +0.000 m/s. Both printed; the description states
  both (deviation recorded).
- e = 1 tip hit -11.757 m/s, e = 0 -5.878 m/s: passed (e = 1: J 5.291 N
  s, the ball back at 6.486 m/s; e = 0: J 2.645 N s, the ball on at
  11.757 m/s).
- The sweet spot the same for any e, any ball, any speed: passed (the
  root's handle-end velocity within 1.8e-15 m/s at 15 and 45 m/s, 50 and
  500 g, restitution 0 and 1).
- Momentum and angular momentum balance to 1e-12: passed (4.350000 =
  4.350000 kg m/s, diff +0.0e+00; 0.616250 and 1.848750 kg m^2/s, diff
  +0.0e+00).
- Energy lost = (1 - e^2) of the relative-motion energy: passed (40.284
  J = 61.7 percent, diff +2.1e-14 J; 29.759 J = 45.6 percent, diff
  +7.1e-15 J).
- Scan of d from 0 to L in 1 cm steps with the sign change between 56
  and 57 cm and the exact root 2 L / 3 = 56.667 cm: passed (one sign
  change, +0.282 to -0.140 m/s; the root +0.0e+00 m/s).
- Free motion after the sweet hit: 1.67 m/s after 20 ms, 4.10 after 50
  ms, 7.71 after 100 ms, a cycloid cusp: passed (2 (J / M) sin(omega t /
  2); (L / 2) omega = 5.968 m/s equals the centre's 5.968 m/s; 1.7,
  10.3, 39.7 cm moved; a full turn 0.4474 s real).
- Free motion after the tip hit: back 4.4 cm in 5 ms, 8.6 cm in 10 ms,
  16.0 cm in 20 ms, then a loop: passed (8.90, 9.13, 9.98 m/s; the
  handle end reaches 22.6 cm back; (L / 2) omega = 13.23 m/s against the
  centre's 4.409 m/s; a full turn 0.2019 s real).
- The approach and the free motion printed with the times the centre and
  the ends leave the band: passed (the ball enters 1.12 s of video
  before the hit at 600 px/s; the two-thirds stick's centre crosses the
  left edge 3.35 s after the hit, the whole stick out at 4.83 s, 6.03 s
  into the cycle; the tip stick's centre at 4.54 s, out at 6.54 s, 7.74
  s into the cycle; the ball out right 4.78 s after the sweet hit and at
  x 71 px at the cycle's end after the tip hit).
- The stick's ends never cross the band's top or bottom rows: asserted
  (the sweep at any angle spans 115 to 469 px under the band top, under
  the rows that end at 96 px and above the event row at 496 px, inside
  the 550 px band).
- The sweet-spot handle end stays put for about 0.4 s of video: passed
  (7 px moved in 0.4 s); the tip hit's handle end 64 px back in 0.4 s:
  passed.
- 5 cycles in 40 s, the last frame equal to the first: passed (loop
  check 0 px, periodicity check 0 px).

### Production

- Sim: sims/sweetspot/sweetspot.py, modelled on sims/deskchain (bands,
  cycle, crossfade, layout asserts, loop checks), sims/cutshot (top
  view, an instantaneous hit, trails) and sims/icerod (a rod with marked
  ends): the rigid impulse in closed form, the free motion in closed
  form (no ODE), the momentum, angular momentum and energy balances, the
  1 cm scan and the exact root, the description hits, the invariance
  checks, the approach and exit times, a graze check of the ball against
  the moving stick, text widths and the row check; 2x supersampled
  bands; loop, periodicity and loop-step checks; ffmpeg rawvideo pipe
  with a ProcessPoolExecutor (12 workers); --measure-only and --frames.
- Manifest projects/sweetspot/manifest.json: seed 0, fps 60, stick 0.85
  m and 0.9 kg, ball 0.145 kg at 30.0 m/s, restitution 0.5, hit
  fractions 2/3 and 1.0, description hits 0 / 42.5 / 56 / 57 cm,
  description restitutions 1 and 0, speeds 15 and 45 m/s, ball masses 50
  and 500 g, handle speed times 20 / 50 / 100 ms, handle jump times 5 /
  10 / 20 ms, scan step 1 cm, slow 20, cycle 8 s, hit_at 1.2 s,
  first_cycle_at 0.0, reset_fade 0.6 s, scene 40 s, 400 px/m, stick x
  400 px, centre 292 px under the band top, ball radius 22 px, hand ring
  56 px, title "Where is the sweet spot|on a bat?" until 3 s, payoff_t
  22.9 s, payoff_hold 0.6 s, six payoff lines formatted from the
  measured values, loop_fade 0.5, music seed 106, gain 0.18, voice
  offset 0.6, caption_y 0.75, overlay "stick 85 cm | ball 30 m/s | 1/20
  speed | no seed".
- Layout: overlay y 96-130 (compose); title two rows at y 190 / 252
  until 3 s; legend "same stick, same ball, 1/20 speed" at y 236 and the
  clock ("before the hit" / "N.NNN s after the hit", real time) at y 290
  after the title; bands y 330-880 (two thirds, teal) and 880-1430 (tip,
  coral); per band: label "hit two thirds along, 56.7 cm" / "hit at the
  tip, 85 cm" (40 px) and "stiff stick 85 cm, ball 30 m/s" (28 px) in
  the top rows, the ball readout right-aligned ("ball 30 m/s" before,
  "ball back at 7.0 m/s" / "ball on at 2.6 m/s" in gold after); the
  stick a 340 px rod at x 400 with its centre 292 px under the band top
  and its handle end at the bottom inside the hand ring (56 px, band
  colour, fixed where the handle end was at the hit, labelled "hand"); a
  muted tick on the stick at the hit point with "2/3" / "tip" on the
  ice; the ball a 44 px disc from the right edge at 600 px/s; after the
  hit the stick moves left and spins, the ball goes back or follows, the
  handle end leaves a gold trail (the cusp against the loop); the gold
  event row at the band's bottom (496-540 px under the band top):
  "handle end at the hit: 0.00 m/s" / "handle end at the hit: 8.8 m/s
  back", lit at the hit and held to the crossfade; the six-line gold
  card from y 1572 at a 48 px pitch; nothing in rows 96-130 or 1440-1530
  (asserted in the row check and measured on the footage).
- Hook pre-tests (media/sweetspot/hooks/pretest.log, 10:26): hook1 (the
  question first) ok 8.89 s, speech from 0 s, the question ends at 1.74
  s of voice = 2.34 s of video: chosen; hook2 (", two thirds along on
  top and at the tip below") ok 9.01 s; hook3 ("Here is a bat. Where is
  the sweet spot on a bat?") ok 7.30 s, the question from 1.21 s of
  voice = 1.81 s of video, later than hook1. words.txt ("sweet spot",
  "the sweet spot on a bat", "a stiff stick", "two thirds", "two thirds
  along", "two thirds of the way along", "two thirds along the stick",
  "the handle end", "watch the handle end", "it kicks back", "the handle
  end kicks back", "eight point eight meters a second", "nearly nine
  meters a second", "where the hand goes", "the ball shoves the stick
  along and spins it", "shove and spin cancel at the handle end", "it
  stays put", "hit there", "hit the tip", "it does not move at all")
  passed in one take of 26.02 s.
- Narration: projects/sweetspot/narration.txt, 110 words; the question
  is the first sentence (spoken from 0.60 s of video) and is repeated
  word for word ("So, where is the sweet spot on a bat?") before the
  payoff; one setup number (thirty meters a second) and one payoff
  number (eight point eight); American spelling ("meters"); no digits;
  the mechanism sentence names only what the frame shows ("The ball
  shoves the stick and spins it. At two thirds, shove and spin cancel at
  the handle end.").
- Voice (media/sweetspot/voice.log): pass 1 (110 words, 10:27:50) ok
  30.53 s. voice.wav ends at 31.13 s of video.
- timing.log (voice offset 0.6 s; whisper's own spelling):

```
  0.60 -   2.50  Where is the sweet spot on a bat?
  2.50 -   7.02  A stiff stick on ice stands in for the bat, a ball at 30
 meters a second hits it.
  7.02 -   8.64  two-thirds along on top,
  8.64 -   9.76  at the tip below.
  9.76 -  11.07  Watch the handle end.
 11.07 -  12.32  where the hand goes.
 12.32 -  14.05  On top, it stays put.
 14.05 -  14.76  below.
 14.76 -  15.79  It kicks back.
 15.79 -  17.96  The ball shoves the stick and spins it.
 17.96 -  19.04  At two-thirds,
 19.04 -  21.68  shove and spin cancel at the handle end. So,
 21.68 -  25.67  Where is the sweet spot on a bat?
 Two-thirds of the way along.
 Hit there.
 25.67 -  31.13  The handle end does not move at all. Hit the tip. It kicks
 back at 8.8 meters a second.
voice 30.53 s, ends at 31.13 s of video
```

- Schedule and sync: hits at 1.2, 9.2, 17.2, 25.2, 33.2 s. The first hit
  at 1.2 s lands under the question (0.60-2.50); "A stiff stick on ice
  stands in for the bat. A ball at thirty meters a second hits it: two
  thirds along on top, at the tip below." 2.50-9.76 over the first
  cycle's free motion (the cusp and the loop, the sticks leaving left,
  the crossfade at 7.4-8.0); the second hit at 9.2 s just before "Watch
  the handle end, where the hand goes. On top, it stays put. Below, it
  kicks back." 9.76-15.79 with both event rows lit from 9.2 (the top
  handle end inside its ring until about 9.6 s, the bottom one 64 px
  back by then); the third hit at 17.2 s under "The ball shoves the
  stick and spins it." 15.79-17.96; "At two thirds, shove and spin
  cancel at the handle end." 17.96-21.68 over the cycle-3 free motion;
  "So, where is the sweet spot on a bat? Two thirds of the way along.
  Hit there," 21.68-25.67 over the cycle-3 crossfade (23.4-24.0) and the
  cycle-4 approach, the card rising from 22.9 s and full at 23.5 s; the
  fourth hit at 25.2 s under "Hit there, the handle end does not move at
  all." 25.67-27.73; "Hit the tip, it kicks back at eight point eight
  meters a second." 27.73-31.13 with "handle end at the hit: 8.8 m/s
  back" lit from 25.2 s (held to 31.4 s) and the card's "hit the tip:
  handle end 8.8 m/s back"; the fifth hit at 33.2 s silent under the
  card; the title fades back in over 39.5-40.0 s.
- Smoke frames viewed before the render (--frames 0.0, 1.0, 1.3, 1.6,
  2.2, 3.5, 5.0, 7.7, 9.6, 10.9, 23.5, 25.7, 39.7, 39.98; twelve
  viewed): the title and both sticks at rest with "ball 30 m/s"; the
  ball approaching; the hit instant with both event rows lit and the
  ball readouts in gold; the cusp and the loop trails; the sticks
  leaving left; the crossfade back to the rest state with the readouts
  faded; the HUD clock; the six-line card inside the frame; the loop
  fade; the last frame equal to the first. All text inside the frame.
- Render (media/sweetspot/render.log, 10:40:20-10:40:47): loop check 0
  px, periodicity check 0 px, loop step 0 px (threshold 24 levels; frame
  2398 carries 2.8 percent of the previous cycle in the crossfade),
  footage 40.00 s at 60 fps, 2400 frames. A first render at
  10:37:38-10:38:04 with the same code except the text-widths print gave
  the same footage.mp4 (md5 16fa44ee0441b1bf0a1560d272e8d704 both times)
  and the same final.mp4.
- Compose (media/sweetspot/compose.log, 10:40:47-10:40:58): music seed
  106, 40.00 s; captions 19 pauses detected, 19 matched (max chunk start
  shift 1.270 s against word-count timing); contact sheet 8x5 at 1 fps;
  final.mp4 40.000000 s; preview.mp4 40.066667 s.
- Text widths (PIL ImageFont.getlength, DejaVuSans-Bold, asserted < 950
  px): overlay@34 896, title@56 767 / 292, legend@40 763, clock@28 317
  (before 218), labels@40 653 / 450, events@40 698 / 790, ball after@28
  309 / 274, hit labels@24 42 / 37, sublabel@28 444, ball before@28 173,
  hand@24 68, payoff lines@40 763 / 773 / 806 / 806 / 706 / 782 px.

### Local QA

- Frames extracted from media/sweetspot/final.mp4 (never edited) with
  ffmpeg -ss T and viewed at full resolution:
  - 0.00: overlay, the title "Where is the sweet spot / on a bat?", both
    sticks at rest at x 400 inside their hand rings, the "2/3" and "tip"
    ticks, "ball 30 m/s" right, no ball yet, no caption, no card.
  - 1.30 (hit + 0.1 s, 0.005 s real): the ball at the tick on both
    sticks, both sticks starting to turn, "ball back at 7.0 m/s" / "ball
    on at 2.6 m/s" in gold, "handle end at the hit: 0.00 m/s" / "handle
    end at the hit: 8.8 m/s back" lit, the tip stick's handle end
    already right of its ring; caption "Where is the sweet".
  - 2.20: the two-thirds stick turned about 45 degrees with its handle
    end just out of its ring on the cusp and the ball going back right;
    the tip stick horizontal with its handle end on the loop and the
    ball drifting at the tip tick; caption "spot on a bat?".
  - 17.30 (mid-run, cycle 3): legend and clock "0.005 s after the hit",
    the third hit with both event rows lit; caption "stick and spins
    it.".
  - 24.00: clock "before the hit", both sticks back at rest in cycle 4
    with "ball 30 m/s", the card full in gold; caption "Two thirds of
    the".
  - 25.70 (hit + 0.5 s in cycle 4): clock "0.025 s after the hit", both
    sticks turning, both event rows lit, the card full; caption "Hit
    there, the".
  - 39.983 (frame 2399): the title back, both sticks at rest, the same
    picture as 0.00; no caption, no card.
  Nothing clipped at the frame edges, no text in the caption band, the
  six card lines sit between y 1572 and about 1850.
- sheet.png (8x5 at 1 fps): five identical cycles: the rest state, the
  ball in, the hit with both event rows lit, the cusp and the loop
  trails, the sticks out left, the crossfade back; captions under; the
  card from the tile at 23 s.
- Question timing: on screen from frame 0 in the title; spoken from 0.60
  s of video (speech from 0 s in voice.wav plus the 0.6 s offset; the
  question ends at 2.34 s in the hook pre-test, timing.log's first
  segment 0.60-2.50); the caption "Where is the sweet" from 0.600 s;
  repeated at 21.68-25.67 s.
- Captions: 33 chunks of at most 20 characters, 0.60-31.13 s; the
  concatenated caption text equals narration.txt word for word (110
  words, compared by script with the overlay drawtext excluded).
- Payoff number on screen when spoken: "handle end at the hit: 8.8 m/s
  back" lit from the hit at 25.2 s to the crossfade at 31.4 s and "hit
  the tip: handle end 8.8 m/s back" full on the card from 23.5 s while
  "kicks back at eight point eight meters a second" is spoken
  28.76-31.13 s (captions "kicks back at eight" 28.763-29.817, "point
  eight meters a" 29.817-30.871); "handle end at the hit: 0.00 m/s" and
  the card's "hit 2/3 along: handle end 0.00 m/s" on screen while "Hit
  there, the handle end does not move at all" is spoken 25.67-27.73 s.
- Footage signalstats: overlay band (rows 96-130) and caption band (rows
  1440-1530) YMAX 28 and YMIN 28 in all 2400 footage frames; both bands
  hold only the background (11, 14, 18).
- Loop: render.log loop check 0 px and periodicity check 0 px on the raw
  frames. Final loop noise (codec only, frames by index): frame 2399 vs
  0: 23,807 px over 8 levels, 2,651 over 24, max 92 at a title letter
  edge (x 408, y 263), mean 0.45; 2398 vs 0: 41,483 / 4,696 / max 92;
  footage 2399 vs 0: 11,630 / 547 / max 71 at a title letter edge, mean
  0.28.
- ffprobe final.mp4: h264 1080x1920 yuv420p 60/1, 2400 frames, duration
  40.000000 s, aac 22050 Hz mono, moov before mdat (faststart),
  4,035,058 bytes.
- md5sum media/sweetspot/final.mp4: 5a3e0f9bf3ca36a3eaa65d4a2982252a
  (identical after the deterministic rerun).
- Narrated numbers against measure.log: "thirty meters a second" (a ball
  of 145 g at 30 m/s), "two thirds" / "two thirds of the way along" (d =
  2 L / 3 = 56.667 cm, the root), "does not move at all" (the handle end
  +0.0000 m/s), "eight point eight meters a second" (the handle end
  -8.8176 m/s = 8.818 m/s back; on screen "handle end at the hit: 8.8
  m/s back"). All on printed lines.
- Metadata number check by script: 68 distinct numbers in the title and
  description, none missing from measure.log (the on-screen strings
  "0.00 m/s", "8.8 m/s back", "6.2 m/s, no spin" and "11.8 m/s back" are
  on the text-widths line).

### Metadata

- Title (95 characters, ASCII, no < or >): Where is the sweet spot on a
  bat? Hit 2/3 along: handle end 0.00 m/s. Hit the tip: 8.8 m/s back
- Description: 3,941 characters, ASCII, no arrows; one setup paragraph
  (the model, every constant, the impulse and handle-end formulas,
  closed-form free motion, 1/20 speed, 5 hits in 40 s, no seed),
  "Measured:" bullets (both hits, the sweet spot and the scan, the
  invariance, the free motion, the other hits, e = 1 and 0, the balances
  and the energy), a "Why:" paragraph, the real-bat caveat, the rerun
  line, the AI line.
- Tags (12): where is the sweet spot on a bat, sweet spot, centre of
  percussion, baseball bat physics, bat sweet spot, rigid body, impulse,
  physics, physics visualization, simulation, shorts, world series.
- categoryId "27", privacyStatus "private", containsSyntheticMedia true,
  selfDeclaredMadeForKids false.

### Deviations from the brief

- The hit at the handle end itself: the brief expected the tip end to
  stay still and the handle end to take 17.6 m/s; the sim gives the
  mirror of the tip hit (handle end +17.635 m/s, tip end -8.818 m/s).
  The tip end stays still at one third along (28.333 cm), the mirror of
  the sweet spot (handle end +11.936 m/s, tip end +0.000 m/s). The
  description states both as printed.
- Hits 1.2 s into the cycle with first_cycle_at 0.0 (brief: near 1.0 s):
  hits at 1.2, 9.2, 17.2, 25.2, 33.2 s so the first lands under the
  question, the third under "The ball shoves the stick and spins it."
  and the fourth under "Hit there, the handle end does not move at all."
- The approach takes 1.12 s of video (brief: about 0.6 s): the stick
  stands at x 400 so the spinning stick and its trail have room before
  the left edge; the ball at 600 px/s crosses 673 px from the right edge
  to the stick.
- The sticks' centres move 119 px/s (two thirds) and 88 px/s (tip)
  (brief: 120 px/s); the two-thirds stick is out of the band 4.83 s
  after the hit, the tip stick 6.54 s after (7.74 s into the cycle, 0.34
  s after the crossfade starts; at the fade's start its sweep reaches x
  30 px at most, a sliver at the left edge that fades with the reset).
- The ball is drawn on top of the stick: after the tip hit the handle
  end's loop swings back up through the ball's row and its cap passes
  inside the drawn 44 px ball's rim by 6.9 px on 7 of 408 frames (the
  ball's centre 22.1 px = 5.5 cm from the stick's axis, 1.71 s of video
  after the hit); there is one hit in the model, and a smaller ball
  barely changes the clearance (scanned 10 to 22 px), so the brief's 44
  px ball stays. The two-thirds hit clears by 12.0 px.
- The title shortened to 95 characters (a first draft was 108); the
  overlay (896 px) and three card lines (806 px at most) shortened from
  drafts over 950 px.
- The backlog entry's handle-end formula "(J / m)(1 - 6 d / L)": the sim
  uses (J / M)(4 - 6 d / L) from the orchestrator notes, verified
  against the impulse arithmetic for both hits.
- Narration 110 words (brief: 100-110), one pass.
- The text-widths line in measure.log gained the on-screen strings
  verbatim after the first render so the metadata number check can find
  "8.8 m/s back"; the rerun reproduced measure.log's numbers,
  footage.mp4 and final.mp4 byte for byte.

## Niche note

  [produced 2026-10-02 as "Where is the sweet spot on a bat? Hit 2/3
  along: handle end 0.00 m/s. Hit the tip: 8.8 m/s back"; measured a
  uniform stiff stick of 85 cm and 0.9 kg free on frictionless ice, hit
  square by a 145 g ball at 30 m/s with restitution 0.5 (rigid impulse
  and free motion in closed form, no seed): hit two thirds along (56.667
  cm from the handle end) J 5.3712 N s, centre 5.968 m/s, spin 14.04
  rad/s, the ball back at 7.043 m/s, the handle end +0.0000 m/s at the
  hit, the tip end 11.94 m/s, then a cycloid cusp (1.67 / 4.10 / 7.71
  m/s after 20 / 50 / 100 ms); hit at the tip J 3.9679 N s, centre 4.409
  m/s, spin 31.12 rad/s, the ball on at 2.635 m/s, the handle end 8.818
  m/s back (twice the centre's speed), the tip end 17.64 m/s, then a
  loop (4.4 / 8.6 / 16.0 cm back after 5 / 10 / 20 ms, 22.6 cm at most);
  the sweet spot at exactly 2 L / 3 for any ball, speed or restitution
  ((J / M)(4 - 6 d / L); the scan changes sign between 56 cm +0.282 and
  57 cm -0.140 m/s; 15 / 45 m/s, 50 / 500 g, e 0 / 1 within 1.8e-15
  m/s); middle hit 6.244 m/s with no spin; one third along the tip end
  stays still (the brief's handle-end hit is the mirror of the tip hit:
  handle +17.635, tip -8.818); e = 1 at the tip 11.757 m/s back, e = 0
  5.878; momentum 4.350000 kg m/s and angular momentum 0.616250 /
  1.848750 kg m^2/s balance exactly; energy lost 40.284 J (61.7 percent)
  and 29.759 J (45.6 percent) = (1 - e^2) of the relative-motion energy;
  shown at 1/20 speed on an 8 s cycle, 5 hits in 40 s; task
  20261002-101235]

## Upload

- orchestrator review (2026-10-02T10:52:39+03:00): task evidence, sheet.png and full frames at
  0.00, 2.20, 17.30, 25.70 and 39.98 s inspected; ffprobe h264 1080x1920 60 fps
  2400 frames 40.000 s; md5 5a3e0f9bf3ca36a3eaa65d4a2982252a; title 95 chars, no angle brackets; description 3941 chars, no angle brackets, 12 tags; captions match narration word for word, compose pause alignment 19 of 19; measure.log matches the closed forms (hit at 2 L / 3 = 56.67 cm: J 5.3712 N s, centre 5.968 m/s, spin 14.04 rad/s, handle end 0.000 m/s, ball back at 7.043 m/s; tip hit: J 3.9679 N s, centre 4.409 m/s, spin 31.12 rad/s, handle end 8.818 m/s back, ball on at 2.635 m/s; (J / M)(4 - 6 d / L) checked for both); question on screen from frame 0 and
  repeated word for word before the payoff; nothing clipped at the 1080 px
  frame; last frame equals the first; approved for upload
- upload attempt 3 of 5 for the quota day that began 2026-10-02T10:00
  EEST, recorded at 2026-10-02T10:54:46+03:00 before starting scripts/yt-upload.py; two
  attempts (twostrings yD8XL-OnEz4 and broom vpn_dIASulU, both published)
  were on record since the boundary
- uploaded private as lqFSVLtReYs at 2026-10-02T10:54:55+03:00
  (https://youtu.be/lqFSVLtReYs); channels.list 1 unit + videos.insert
  1,600 units; media/sweetspot/upload.log
- scripts/yt-qa.py sweetspot lqFSVLtReYs --wait --publish in the
  foreground (started 2026-10-02T10:55:04+03:00): gate 15 of 15 on the first
  processed read (processed, succeeded, hd, 1080x1920, title, description
  and tags match, category 27, not made for kids, PT41S for the 40.000 s
  file, private before publish); published at 2026-10-02T10:55:38+03:00;
  re-read privacyStatus=public selfDeclaredMadeForKids=False
  embeddable=True; yt-qa quota 54 units; media/sweetspot/publish.log
- attempt 3 of 5 complete: 1,655 units; slot 3 of 3 resolved as
  published (recorded 2026-10-02T10:56:19+03:00)

### Quota
- attempt 3 of the hard cap of 5 for the quota day that began
  2026-10-02T10:00 EEST; cost 1,655 units (the channels.list verification
  inside yt-upload.py, the 1,600-unit insert, and the gate run's reads,
  update and re-read as printed by yt-qa.py, 54); day total after three
  attempts 4,963 of 10,000 used, 5,037 remaining before the stats refresh
