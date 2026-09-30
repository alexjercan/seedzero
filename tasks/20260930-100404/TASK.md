# Research trends: run 10 for the day 32 slate

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: backlog

## Goal

Tenth research-trends run, 2026-09-30 from about 10:05 EEST, for the
three slots of day 32. The backlog in `docs/niche.md` holds twenty-two
unproduced ideas and the day 31 close judged none a strong first pick:
space time-lapses and counters (Kelvin wake, Collatz, secretary
problem, rogue wave, Saturn retrograde, Halley, L2 drift), low-ranked
ideas (corner reflector, basketball arc, Moon clock, Atwood drop, yo-yo
drop, sliding ladder, falling chimney), a tie payoff (bathtub drain), a
heavy build (dam break), a half-known answer (balance a broom), a
late-October peg (bat sweet spot), an invisible payoff (inertia ball), a
model problem (fridge tip), and the three left from run 9 (car over a
hump, swim to the flag, sliding ladder). Find 6 to 9 new candidates that
fit the winning format: continuous tabletop or everyday motion, two
panels on the same input that end visibly differently on a phone
screen, one plain question in the first two seconds, one setup number,
one payoff number, a closed-form check, a loop or a repeat, and a build
of about 25 minutes with RK4, event-driven steps or closed forms (no
PDE, no fluid grid, no ray tracing, no fitted aerodynamics, no rider or
posture models, no chosen material strengths). Measure every survivor
with a throwaway script and check the model (contact forces positive,
no-slip friction available with the minimum mu stated, energy kept
where it should be, panels visibly different at 1080x1920). No
production in this run. By instruction `web/data/`, sims/, projects/,
media/ and secrets/ were not touched and no commit was made.

## Channel evidence used for the filter

Views at run time (2026-09-30 10:02): the shorts the feed picks up sit
at 600 to 1,050 views and share one format: everyday tabletop or road
motion, two panels on the same input that end visibly differently, an
exact factor, fraction or threshold, and a closed-form check. Strong:
stopping distance 1,012, folded chain beside a ball 987, cue ball
follow 957, cut shot 952, superball under a table 940, bucket over the
head 939, spring squash 928, racing balls 744, ice cube or ball uphill
677 (day 31). Weak (30 to 300): coin rotation 257, tablecloth 297,
head-on crash 216, rope swing 319, peg swing 82, brake or swerve 172
(day 31), draw shot 30 (day 31, the third pool short in a week: pool
may be saturating), merry-go-round 2. Historically 5 to 99: space
time-lapses, counters and random-draw statistics, drawings, tie
payoffs. The filter therefore favoured tabletop "which comes back",
"does it make it" and "which way" debates with an exact fraction or
threshold, avoided pool and road as the main prop, and rejected space,
counters, drawings, tie payoffs, fitted constants, rider models and
siblings of shorts already produced (rolling races, uphill, superball
map, stopping distance).

## Queries (12 WebSearch, 9 WebFetch of which 1 returned an unreadable PDF and 1 a login redirect)

1. "rolling ball bounces off wall elastic rebound speed spin friction
   3/7 rolling again physics". Showed Rod Cross's bounce papers and the
   2021 Scientific Reports paper "Collision-enhanced friction of a
   bouncing ball on a rough vibrating surface" (fetched from PMC
   below): a rolling ball off a smooth wall keeps its spin and reverses
   its velocity, floor friction then restores rolling and the loss is
   large even when the wall bounce is elastic.
   https://pmc.ncbi.nlm.nih.gov/articles/PMC7801373/
   https://www.physics.usyd.edu.au/~cross/PUBLICATIONS/GripSlip.pdf
2. "ball placed on moving conveyor belt treadmill rolls final velocity
   2/7 belt speed physics". Showed two Physics Forums threads: "What
   happens to a ball placed on a moving conveyor belt?" (fetched below;
   its summary answer is belt speed, which is the box answer, and the
   inclined-belt no-slip limit mu of at least (2/7) tan theta) and the
   cylinder thread whose answer is one third of the belt speed. The
   2/7 for a ball comes from the sim and the angular momentum check.
   https://www.physicsforums.com/threads/what-happens-to-a-ball-placed-on-a-moving-conveyor-belt.1008654/
   https://www.physicsforums.com/threads/how-do-you-determine-the-final-velocity-of-a-cylinder-on-a-moving-conveyor-belt.57435/
3. "rolling ball hits step curb minimum speed to climb angular momentum
   about edge conserved physics problem". Showed Zengel's "Motion of a
   ball rolled over a shallow step" (arXiv 2605.20481, The Physics
   Teacher 61, 477, 2023; PDF not readable, abstract fetched), the
   Physics Forums cylinder-up-a-step thread (fetched below) and the
   LibreTexts rolling-and-slipping page: the textbook model is an
   impulsive grab at the edge with angular momentum about the edge
   kept, then a pivot without slip.
   https://arxiv.org/abs/2605.20481
   https://www.physicsforums.com/threads/how-does-angular-momentum-conservation-apply-to-a-cylinder-rolling-up-a-step.721503/
   https://phys.libretexts.org/Bookshelves/University_Physics/Mechanics_and_Relativity_(Idema)/05:_Rotational_Motion_Torque_and_Angular_Momentum/5.08:_Rolling_and_Slipping_Motion
4. "helium balloon in accelerating car which way does it move pendulum
   debate physics". Showed the Physics Forums thread (fetched below),
   Scientific American's "Buoyant Balloon", IFLScience, PhysLink and a
   blog on the equivalence principle: a standing "which way" debate
   whose answer (forward) still surprises; no page gives the tilt
   angle, the sim supplies atan(a / g).
   https://www.physicsforums.com/threads/helium-balloon-motion-in-a-moving-car.55098/
   https://www.scientificamerican.com/article/buoyant-balloon-float-forward-with-fluid-physics/
   https://www.iflscience.com/you-have-a-helium-balloon-in-your-car-what-direction-does-it-go-when-you-accelerate-78598
5. "chain slides off table edge friction fraction hanging threshold
   cosh charger cable falls off desk physics". Showed the Physics
   Forums chain thread, the Profound Physics step-by-step page (fetched
   below) and homework pages: threshold hanging fraction mu / (1 + mu),
   cosh runaway, time acosh formula.
   https://www.physicsforums.com/threads/chain-sliding-off-the-edge-of-a-table.48928/
   https://profoundphysics.com/rope-sliding-down-a-table-with-friction-step-by-step-solution/
6. "capstan equation rope wrapped around post turns hold load e^(mu
   theta) demonstration belay". Showed the Wikipedia capstan page, the
   Firgelli mechanism pages, a Physics Forums derivation and a rope
   simulator: T2 = T1 e^(mu phi); half a turn at mu 0.3 gives 2.6,
   three turns over 280.
   https://en.wikipedia.org/wiki/Capstan_equation
   https://www.physicsforums.com/threads/how-does-the-capstan-equation-derive-rope-tension.885769/
   https://physandbox.com/mechanics/capstan-rope
7. "viral physics debate September 2026 which one wins counterintuitive
   demo shorts". Showed the "Debunking Terrible Physics" early and mid
   September 2026 sessions and the fluxnote idea lists again (as in
   runs 5 to 9): no single new debate this month, so the run leaned on
   channel evidence and classic puzzles.
   https://www.youtube.com/watch?v=WvaE85Ht8uc
   https://fluxnote.io/guides/science-youtube-shorts-ideas
8. "coin on turntable flies off speed threshold mu g spiral path
   kinetic friction record player". Showed two Physics Forums threads
   ("Why does a coin fly off a turntable?", fetched below, and "Which
   coin flies off first") and homework pages: v = sqrt(mu g r), the
   path after slipping curves between the tangent and the circle.
   https://www.physicsforums.com/threads/why-does-a-coin-fly-off-a-turntable.703561/
   https://www.physicsforums.com/threads/which-coin-flies-off-first-from-a-speeding-turntable.742468/
9. "two springs in series vs parallel same mass oscillation period
   ratio exactly 2 demonstration". Showed the UCSB lecture demo 40.15,
   a Fullerton lab sheet and Physics Forums: series k/2, parallel 2k,
   period ratio exactly 2.
   https://web.physics.ucsb.edu/~lecturedemonstrations/Composer/Pages/40.15.html
10. "counterintuitive classical mechanics puzzles rolling friction
    exact answer list 2026". Showed Simanek's puzzle pages (fetched
    below), askthephysicist and a 2026 arXiv on spheroids rolling up
    diverging rails (the double cone): nothing new that passes the
    filter.
    https://dsimanek.vialattea.net/puzzles/ideas-answers.htm
    https://arxiv.org/pdf/2608.19541
11. "rolling ball elastic collision wall returns with 3/7 of speed hoop
    stops rolling sphere wall friction". Showed two Physics Forums
    threads on the rolling sphere and the wall (113683 and 691097, the
    second fetched below: 3v/7), a YouTube worked solution and arXiv
    1909.11471 with the wall map v' = (5/7) v - (2/7) R w: a known
    puzzle that students get wrong first.
    https://www.physicsforums.com/threads/finding-the-post-collision-speed-of-a-rolling-sphere-colliding-with-a-wall.691097/
    https://www.physicsforums.com/threads/velocity-of-sphere-after-collision-with-vertical-wall.113683/
    https://www.youtube.com/watch?v=nvUhv_MwC1Q
    https://arxiv.org/pdf/1909.11471
12. "ball on floor of accelerating car rolls backward acceleration 5/7
    relative to car physics forums". Showed the Pearson railroad-car
    ball problem (5/7 of the car's acceleration backward relative to
    the car) and a pendulum-in-a-car page: the car version of the belt
    idea is a standard exercise.
    https://www.pearson.com/channels/physics/asset/7254bab7/ii-a-solid-rubber-ball-rests-on-the-floor-of-a-railroad-car-when-the-car-begins-

## Sources (fetched pages)

- https://www.physicsforums.com/threads/what-happens-to-a-ball-placed-on-a-moving-conveyor-belt.1008654/
  : the summary answer is that the ball ends at belt speed with the
  contact at rest (true for a box, not for a free-rolling ball, which
  keeps rolling backward on the belt at 5/7 V); the inclined-belt part
  gives mu_s of at least (2/7) tan theta; no disagreement in the thread.
- https://arxiv.org/abs/2605.20481 : a ball rolled over a shallow step
  edge gains speed perpendicular to the step; the ball rolls without
  slipping on the edge the whole time; a classroom demo with a ball and
  a stack of paper. The PDF body was not readable by the fetch tool.
- https://www.physicsforums.com/threads/how-does-angular-momentum-conservation-apply-to-a-cylinder-rolling-up-a-step.721503/
  : angular momentum about the step edge is kept through the impact
  because gravity is finite over an instant; for a cylinder and a step
  of R/4 the spin drops to 5/6; after the hit the body rolls about the
  edge.
- https://www.physicsforums.com/threads/helium-balloon-motion-in-a-moving-car.55098/
  : posters agree the balloon goes forward and argue only about the
  mechanism (denser air piling up at the back against the equivalence
  principle); no tilt formula, no pendulum comparison.
- https://profoundphysics.com/rope-sliding-down-a-table-with-friction-step-by-step-solution/
  : x'' = (g / l)(1 + mu) x - mu g; slides when x0 / l exceeds
  mu / (1 + mu); x(t) = (x0 - x*) cosh(sqrt(g (1 + mu) / l) t) + x*;
  time off t_s = sqrt(l / (g (1 + mu))) acosh((1 - f*) / (x0 / l - f*)).
- https://dsimanek.vialattea.net/puzzles/ideas-answers.htm : classic
  puzzle answers (equal-mass impact leaves at 90 degrees, rolling races
  tie for any mass, the soda can's lowest centre at a quarter height,
  the gravity tunnel 42 minutes); nothing new for this filter.
- https://pmc.ncbi.nlm.nih.gov/articles/PMC7801373/ (the Nature link
  redirected to a login page): a rolling ball meeting a smooth wall has
  v reversed and omega kept, so v / (R omega) is about -1 and the
  contact slides at -2v; floor friction pushes it back to rolling; the
  coupling of an elastic wall hit with rotation and friction loses more
  energy than inelasticity does.
- https://www.physicsforums.com/threads/why-does-a-coin-fly-off-a-turntable.703561/
  : v = sqrt(mu g r) from static friction as the centripetal force; the
  coin then slides on a curve between the tangent and the circle;
  posters argued about wording, not the threshold.
- https://www.physicsforums.com/threads/finding-the-post-collision-speed-of-a-rolling-sphere-colliding-with-a-wall.691097/
  : a solid sphere rolling at v, elastic hit on a smooth wall, rough
  floor: it rolls again at 3v/7; the poster first doubted whether the
  spin changes at the wall; the clean route is angular momentum about
  the floor contact point, m v R - I v / R = m v' R + I v' / R.

## Measurements (python3 with numpy, run 2026-09-30, /tmp/rt10/measure.py, log in /tmp/rt10/measure.log)

Stepped Coulomb slip at 2 us, RK4 at 10 to 100 us, g 9.80665, k is
I / (m R^2): solid ball 2/5, cylinder 1/2, hollow ball 2/3, ring 1.

- Ball or ring into a wall: 1.0 m/s rolling on mu 0.3 into a smooth
  wall 1 m away, perfect bounce. Rolls again at v (e - k) / (1 + k):
  ball 0.4286 m/s back (3/7, slip 0.1942 s over 13.87 cm, energy kept
  18.37 percent), cylinder 0.3333 (1/3), hollow ball 0.2000 (1/5), ring
  0.0000 (stops dead after 17.00 cm and 0.3399 s, energy kept 0); the
  stepped slip matches the closed forms to four decimals. Bounce 0.8:
  ball 0.2857 (2/7), ring +0.1000 (creeps back toward the wall). mu
  0.15 and 0.6 change only the slip (27.7 and 6.9 cm). Timeline: hit at
  1.000 s, the ball crosses its start line at 3.20 s, the ring stops at
  1.340 s. Ramp variant: from 20 cm the ball arrives at 1.6739 m/s and
  comes back up to 3.67 cm (9/49 h), the puck to 20.0, the ring 0. Two
  rolling balls head-on each roll back at 0.4286. A grippy wall would
  stop the wall contact from sliding (needs 2/7 m v0 of friction
  impulse against 0.6 available at mu 0.3) and kick the ball up at 2/7
  v0, so the claim needs a smooth wall.
- Ball or box on a moving belt: belt 1.0 m/s, 2 m long, mu 0.4. Box:
  belt speed at 0.2549 s after 12.75 cm, leaves at 2.127 s. Ball:
  0.2857 m/s (2/7 V) after 0.0728 s and 1.04 cm, rolling backward on
  the belt at 0.7143 m/s, leaves at 7.04 s; cylinder 1/3 (6.04 s),
  hollow ball 2/5 (5.05 s), ring 1/2 (4.06 s). Any mu above 0 works.
  Car at 0.3 g (2.9420 m/s^2): the ball rolls back at 2.1014 m/s^2
  (5/7 a) relative to the car, forward on the road at 0.8406 (2/7 a),
  crosses a 1 m footwell in 0.9756 s while the car moves 1.400 m; needs
  mu 0.0857; a box with mu 0.4 stays put, mu 0.2 slides back at 0.9807
  m/s^2.
- Kerb hop: football R 11 cm, kerb 3 cm, edge grab without slip, pivot
  about the edge, floor landing kills the vertical speed, mu 0.4 for
  the slip after landing. Threshold sqrt(2 g h / (1 + k)) / (1 - h /
  ((1 + k) R)) = 0.8051 m/s; the edge keeps 0.8052 of R omega; above
  1.1000 m/s the edge force is negative at the first touch and the
  model ends. 0.7 m/s: rises 2.27 cm, back on the floor at 0.3443 s,
  rolls back at 0.4539 m/s, least edge force 0.433 weights; 0.8: rises
  2.96 cm, back at 0.7291 s, rolls back at 0.5187; 0.9: climbs in
  0.1845 s, rolls on at 0.3238, least edge force 0.240; 1.0: climbs in
  0.1424 s, rolls on at 0.4775, least edge force 0.126; 1.2: leaves the
  edge at once (edge force -0.138 weights). Kerb 5 cm: needs 1.2393
  but flies above 1.1359, no window (a window needs h under 6.42 cm
  for this ball). Bike-wheel ring R 33 cm, kerb 10 cm: threshold 1.1671,
  fly-off above 1.7700; 1.0 m/s rises 7.34 cm and rolls back at 0.7199,
  1.2 climbs in 0.5642 s and rolls on at 0.2367.
- Balloon or dice in a car: 0.3 g with a 0.5 s throttle ramp, 50 cm
  strings, balloon 30 cm (air 17.3 g, balloon 6.4 g, lift over inertia
  0.726 with added mass half the air). Equilibrium atan(a / g) = 16.70
  degrees (0.5 g 26.57, 1.0 g 45.00). Damping 0.5/s: peaks 27.96 (dice,
  0.95 s) and 28.32 (balloon, 1.07 s), 22.84 and 21.94 at 2.5 s, not
  settled; an undamped sudden start would peak at 33.40. Damping 2.0/s
  and 4 s of throttle: 17.06 back and 16.39 forward at 3.9 s, peaks
  23.27 and 22.82. Small-swing periods 1.419 and 1.665 s. Car at 29.1
  km/h after 3 s.
- Necklace over the desk edge: 1 m chain, mu 0.25, threshold 20.00
  percent, rate sqrt((1 + mu) g / L) = 3.5012 /s (e-fold 0.2856 s). 18
  cm: holds (margin 0.025 m-weight); 20 cm: at the limit; 21 cm: off at
  1.4496 s (closed 1.4495), 22 cm: 1.2516 s (1.2515), 25 cm: 0.9896,
  30 cm: 0.7908, last link at 2.78 to 2.80 m/s. Frictionless: 1 cm
  hanging leaves at 1.6919 s, 10 cm at 0.9558. mu 0.4 needs 28.57
  percent, mu 0.1 9.09.
- Rope round a post: mu 0.3, pull 20 N. Half a turn 2.57x (51 N), one
  turn 6.59x (131.7 N, 13.4 kg), 1.25 turns 10.55x (211 N), two turns
  43.38x (867 N, 88.5 kg), three 285.68x. A 20 kg load needs 1.211
  turns; with one turn it falls at 3.221 m/s^2 (net 64.4 N), 1 m in
  0.788 s. Two turns at mu 0.2: 12.3x, at mu 0.4: 152.4x.
- Coin on a turntable: mu 0.3, coin at 10 cm, record edge 15 cm. 33 1/3
  rpm needs 0.124 g (stays out to 24.15 cm), 45 rpm 0.226 g (stays out
  to 13.25 cm), 78 rpm 0.680 g (holds only inside 4.41 cm). Threshold
  at 10 cm 5.4240 rad/s = 51.80 rpm. At 78 rpm the coin reaches the
  edge at 0.1797 s, 69.2 degrees round at 0.876 m/s while the disc turns
  84.1 degrees (the coin slips back 14.9 degrees on the disc).
- Two springs: 1 kg on 100 N/m springs. One: sag 9.81 cm, period
  0.6283 s; side by side (200 N/m): 4.90 cm, 0.4443 s; stacked (50
  N/m): 19.61 cm, 0.8886 s; ratios exactly 2.0000 and 4; the pair loop
  every 0.8886 s.
- Same spot, which lands first (rejected): 15 m/s at 30 and 60 degrees
  both land at 19.870 m, after 1.5296 and 2.6493 s (ratio 0.5774 =
  1 / sqrt 3); the high ball is 8.40 m up when the low one lands.

## Candidates

Numbers are expectations to check; the sim measures the claim.

1. Ball or ring into a wall (wallbounce). A solid ball and a ring
   rolling at 1.0 m/s on the same table (mu 0.3) into the same smooth
   wall, perfect bounce. Hook: "Roll a ball and a ring into the wall.
   Which one comes back?" Setup: 1.0 m/s; payoff: the ball, at 3/7 of
   its speed (0.43 m/s); the ring slides 17 cm and stops dead. Check:
   v (e - k) / (1 + k), angular momentum about the floor contact; slip
   time (1 + e) v k / ((1 + k) mu g). Renderable: side view, a stripe
   on each body, closed forms plus stepped Coulomb slip like
   sims/cueball, under 25 minutes; repeat the roll. Pillar: physics
   (rotation, friction). Accepted first: a known Physics Forums puzzle
   that students get wrong, two exact fractions (3/7 and 0), the
   panels end on opposite sides of the table, the cue-ball-follow
   family (957) without a pool table. Caveats: smooth wall and a
   perfect bounce (a grippy wall kicks the ball up at 2/7 v0, a 0.8
   bounce gives 2/7 and the ring creeps back toward the wall); say
   both in the description.
2. Ball or box on a moving belt (belt). A box and a solid ball set
   down at rest on the same 2 m belt running at 1.0 m/s. Hook: "Box
   and ball on a moving belt. Which one keeps up?" Setup: 1.0 m/s;
   payoff: the box rides off at belt speed in 2.1 s; the ball settles
   at exactly 2/7 of the belt speed (0.29 m/s), rolls backward on the
   belt for ever and leaves at 7.0 s. Check: V k / (1 + k) from angular
   momentum about the belt line; ring 1/2, cylinder 1/3. Renderable:
   side view with a moving belt texture, closed forms plus slip, under
   20 minutes; the belt is periodic so it loops. Pillar: physics
   (rolling). Accepted: the Physics Forums thread itself answers "belt
   speed", so the intuition is split; an exact fraction; the panels end
   with the box gone and the ball still on the belt; everyday
   (checkout belt, treadmill). Caveats: no rolling resistance (a real
   ball creeps up to belt speed eventually); the car version (5/7 of
   the car's acceleration, 1 m in 0.98 s at 0.3 g) is the same claim if
   a road prop is wanted.
3. Kerb hop (kerb). A football rolling at 0.7 m/s beside one at 1.0
   m/s into the same 3 cm kerb. Hook: "How fast must a ball roll to
   climb the kerb?" Setup: a 3 cm kerb; payoff: 0.81 m/s; at 0.7 the
   ball rises 2.3 cm and rolls back at 0.45 m/s, at 1.0 it is on top
   in 0.14 s at 0.48 m/s. Check: sqrt(2 g h / (1 + k)) / (1 - h /
   ((1 + k) R)) with the edge keeping (1 - h / ((1 + k) R)) of the
   spin; edge force m (g cos phi - R phi'^2) stays positive in the
   window 0.81 to 1.10 m/s. Renderable: side view, RK4 pivot about the
   edge plus a slip phase after the landing, about 30 minutes; repeat
   the roll. Pillar: physics (rotation). Accepted mid: the "does it
   make it" family (bucket 939, loop, peg) with a threshold and panels
   that end on opposite sides of the kerb. Caveats: the edge-grab model
   (textbook, Physics Forums, Zengel 2023) ends above 1.10 m/s where
   the edge force turns negative and a real ball bounces; a 5 cm kerb
   has no window for this ball; state the inelastic landing.
4. Necklace over the desk edge (necklace). A 1 m chain on a desk (mu
   0.25) with 18 cm hanging beside 22 cm. Hook: "How much can hang
   over the edge before it all slides off?" Setup: a fifth (20 percent,
   mu / (1 + mu)); payoff: 18 cm holds for ever, 22 cm is gone in 1.25
   s, the runaway doubling its excess every 0.2 s. Check: the
   Profound Physics cosh solution; RK4 within 1e-4 s. Renderable: side
   view, a 1D chain drawn as links, under 20 minutes; repeat the
   release. Pillar: physics (friction). Accepted mid: everyday (a
   necklace, a charger cable), a threshold, panels that end differently
   (on the desk against on the floor). Caveats: the 20 percent depends
   on mu; the chain is idealised as a flexible line with no stiffness.
5. Balloon or dice in a car (balloon). A helium balloon and a hanging
   dice on 50 cm strings in a car pulling 0.3 g. Hook: "Floor it. Which
   way does the balloon swing?" Setup: 0.3 g; payoff: forward, 17
   degrees, while the dice swings 17 degrees back. Check: atan(a / g)
   for both; buoyancy as the displaced air's weight in the tilted
   effective gravity. Renderable: side view inside the car, two RK4
   pendulums, under 20 minutes; repeat. Pillar: physics. Accepted mid:
   a famous "which way" debate (Physics Forums, Scientific American,
   IFLScience) with an exact angle. Caveats: the swing size and
   settling depend on the damping chosen (2/s settles by 4 s); the
   payoff is a mirror pair of angles, weaker than a threshold.
6. Rope round a post (capstan). A 20 kg load on a rope wrapped one
   turn beside two turns round a post, a hand holding 2 kg. Hook: "Can
   two turns of rope hold a 20 kg weight with a 2 kg pull?" Payoff:
   one turn holds 6.6 times the pull and slips (the load falls 1 m in
   0.79 s), two turns hold 43 times. Check: e^(mu theta). Accepted
   low: a threshold with a fall against a hold, but the factor is a
   chosen mu (0.2: 12x, 0.4: 152x) and there is little motion in the
   holding panel.
7. Coin on a 45 or a 78 (coin). A coin 10 cm out on a record at 45 rpm
   beside 78 rpm (mu 0.3). Hook: "Does the coin stay on at 78?" Payoff:
   at 45 it stays (needs 0.23 g of 0.30), at 78 it spirals off the
   edge in 0.18 s; threshold 52 rpm. Check: sqrt(mu g / r). Accepted
   low: the turntable prop was used on 2026-09-16 and the threshold is
   a chosen mu.
8. Two springs, stacked or side by side (springs). The same 1 kg on two
   springs side by side beside the same two stacked. Hook: "Stack the
   springs or pair them: which bounces faster?" Payoff: side by side,
   exactly twice as fast (0.44 against 0.89 s) and a quarter of the
   sag (4.9 against 19.6 cm). Check: k 2k against k/2. Accepted low:
   exact and periodic (loops every 0.889 s) but both panels keep
   bouncing, so they differ in rate, not in outcome.

## Rejected

Bullet block, spinning against not (both rise the same: a tie); same
spot, which lands first (30 against 60 degrees: both land on the same
spot and the low one first is not a debate); ruler on two fingers
(the payoff is the balance point and the switch count depends on the
static-to-kinetic mu ratio); bicycle pedal pulled backward (a
kinematics puzzle like the coin rotation at 257); rolling off a dome
(54.0 against 48.2 degrees, too close on a phone); monkey and
counterweight (a tie); seesaw launch (chosen masses, no debate); box
in a braking truck (the stopping-distance payoff again); rolling
against sliding downhill and the ski-jump range (siblings of the
uphill short produced on day 31 and the rolling race); topspin or
backspin off a wall (the superball map again); domino chain (multi-body
contacts, over 25 minutes); double cone rolling uphill (a 3D drawing);
tippe top and rattleback (friction-dependent heavy builds); ball in an
accelerating car as a separate short (the belt claim with a road
prop, kept as a note); the pegs (Nobel physics 2026-10-06, Sputnik
1957-10-04, World Space Week: space or no motion).

## Ranking

For today's three slots, one producer each, about 25 minutes with RK4,
stepped Coulomb slip or closed forms:

1. Ball or ring into a wall (the ball comes back at 3/7 = 0.43 m/s; the
   ring slides 17 cm and stops dead; a puck on ice at the full 1.0).
2. Ball or box on a moving belt (the box rides off at belt speed in 2.1
   s; the ball settles at exactly 2/7 = 0.29 m/s and leaves at 7.0 s).
3. Kerb hop (0.81 m/s to climb a 3 cm kerb; 0.7 rolls back at 0.45
   m/s, 1.0 is on top in 0.14 s at 0.48 m/s).

Then necklace over the desk edge, balloon or dice in a car, rope round
a post, coin on a 45 or a 78, two springs.

## Outcome

Eight ideas appended to `docs/niche.md` under "Added by trend research
2026-09-30 (evidence in task 20260930-100404; ...)". No `web/data/`
change, no status update, no production, no commit in this run by
instruction. Existing backlog entries were not changed. The task stays
open for the day 32 orchestrator.

## Files changed

- tasks/20260930-100404/TASK.md (this file)
- docs/niche.md (eight backlog bullets appended)

## Close (day 32 orchestrator, 2026-09-30T11:24:37+03:00)

- Selected from this run: ball or ring into a wall (task 20260930-104024,
  published as https://youtu.be/vC17_o8y_y4), ball or box on a moving
  belt (task 20260930-104026, https://youtu.be/mYyXLCyecNA) and balloon
  or dice in a car (task 20260930-104027, https://youtu.be/910Al8RGRNU).
- Passed over: kerb hop (the rigid edge-grab model ends above 1.1 m/s
  and a real football bounces), necklace (one panel is static for the
  whole short and the threshold is a chosen mu), rope round a post and
  coin on a record (chosen mu, little motion in the holding panel, the
  turntable prop reused), two springs (the panels differ in rate, not
  outcome).
- Two brief figures for the balloon idea were corrected before
  production (lift over inertia 0.712, not 0.724; balloon period 1.681 s,
  not 1.667 s); the produced short used 0 to 100 km/h in 10 s (2.7778
  m/s^2, atan 15.82 degrees) instead of the 0.3 g in the bullet, and the
  produced note under the bullet in docs/niche.md records the measured
  numbers.
- The three produced notes are appended under their bullets in
  docs/niche.md; twenty-seven unproduced ideas remain (kerb hop,
  necklace, rope round a post, coin on a record and two springs from
  this run). Closed with the day 32 slate.
