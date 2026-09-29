# Research trends: run 9 for the day 31 slate

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: backlog

## Goal

Ninth research-trends run, 2026-09-29 from about 10:02 EEST, for the
three slots of day 31. The backlog in `docs/niche.md` holds eighteen
unproduced ideas and none is a strong first pick: space time-lapses and
counters (Kelvin wake, Collatz, secretary problem, rogue wave, Saturn
retrograde, Halley, L2 drift), low-ranked ideas (corner reflector,
basketball arc, Moon clock, Atwood drop, yo-yo drop), a tie payoff
(bathtub drain), a heavy build (dam break), a half-known answer (balance
a broom), a late-October peg (bat sweet spot), an invisible payoff
(inertia ball: 5 ms, 0.085 mm) and a model problem (fridge tip). Find 6
to 9 new candidates that fit the winning format: continuous tabletop or
everyday motion, two panels on the same input that end differently, one
plain question in the first two seconds, one setup number, one payoff
number, a closed-form check, a loop or a repeat, and a build of about 25
minutes with RK4, event-driven steps or closed forms (no PDE, no fluid
grid, no ray tracing, no fitted aerodynamics, no rider or posture
models). Measure every survivor with a throwaway script and check the
model (contact forces positive, no-slip friction available, energy
kept, panels visibly different on 1080x1920). No production in this run.
By instruction `web/data/status.json`, sims/, projects/, media/ and
secrets/ were not touched and no commit was made; `web/data/slate.json`
only had its backlog count updated.

## Channel evidence used for the filter

Views at run time (`web/data/slate.json`, refreshed 2026-09-29 10:01):
the shorts the feed picks up sit near 600 to 1,000 views and share one
format: continuous tabletop or everyday motion, two panels on the same
input that end differently, one plain question in the first two
seconds, one setup number, one payoff number, a closed-form check, a
loop or a repeat. Recent: stopping distance 1,012, folded chain beside a
ball 986, cue ball follow 957, cut shot 952, superball under a table
940, bucket over the head 939, spring squash 928, spring pendulum swap
830, racing balls 744. Weak recently: coin rotation 233, tablecloth 268,
rope swing 321, head-on crash 167 and stick on ice 395 and peg swing 63
after one day. Formats at 5 to 99 views historically: space
time-lapses, counters and random-draw statistics, drawings, tie
payoffs. Road and pool pieces (stopping distance, cue ball follow, cut
shot) are the strongest recent genres. The filter therefore favoured
everyday "which first", "which higher", "which way" and "does it make
it" debates with an exact fraction, factor or threshold, two panels
that end visibly differently, and cheap builds; it rejected space,
counters, drawings, tie payoffs, fitted constants and rider models.

## Queries (10 WebSearch, 6 WebFetch of which 2 returned unreadable PDF and 1 the wrong page)

1. "viral physics question debate shorts September 2026 which one wins
   counterintuitive". Showed the "Debunking Terrible Physics" early and
   mid-September 2026 sessions again, the fluxnote idea lists (unchanged
   since run 5), exam-paper "viral question" videos and a Wikipedia
   2026-in-science page. No single demo or debate dominates this month,
   so the run leaned on channel evidence and classic debates.
   https://www.youtube.com/watch?v=WvaE85Ht8uc
   https://fluxnote.io/guides/viral-physics-youtube-shorts-ideas-2026
2. "wall ahead brake or swerve physics turning needs twice the distance
   friction circle". Showed two Physics Forums threads ("Brake or
   swerve?", "Why is braking faster than swerving to avoid a wall?"),
   Rhett Allain's Dot Physics posts "Turn or go straight? Quick!" and
   "More on turning and braking" (the first fetched below) and the Wikipedia
   circle-of-forces page: a standing debate with an exact factor of 2,
   and the known caveat that a narrow obstacle can favour the swerve.
   https://scienceblogs.com/dotphysics/2010/08/05/turn-or-go-straight-quick
   https://www.physicsforums.com/threads/brake-or-swerve.196655/
   https://en.wikipedia.org/wiki/Circle_of_forces
3. "rolling ball versus sliding block same speed up incline which goes
   higher 7/5". Showed Mungan's "A Race Between Rolling and Sliding Up
   and Down an Incline" (TPT 52; fetched, PDF not readable), a TPT 2023
   note "Acceleration of a Ball Up an Incline", Quora, Brainly and
   Physics Forums threads. The search tool's own summary answered it
   wrong (it said the block goes higher), which shows the intuition is
   split; the energy answer is the ball, 7/5 as high.
   https://www.usna.edu/Users/physics/mungan/_files/documents/Publications/TPT52.pdf
   https://pubs.aip.org/aapt/pte/article/61/5/378/2887582/Acceleration-of-a-Ball-Up-an-Incline
   https://brainly.com/question/15209413
4. "draw shot physics backspin wears off distance object ball cue ball
   comes back 2/7 Dr Dave". Showed Dr Dave's draw pages (cloth effects
   fetched below, physics advice, maximum spin at half a radius tip
   offset), a May 2024 Billiards Digest "Draw Shot Control" article and
   the Wikipedia cue-sports techniques page: the draw wearing off on the
   way to the object ball is a common player question; none of the pages
   gives the distance, the sim supplies it.
   https://drdavepoolinfo.com/faq/draw/cloth-effects/
   https://drdavepoolinfo.com/faq/sidespin/maximum/
   https://drdavepoolinfo.com//bd_articles/2024/may24.pdf
5. "hump back bridge car leaves the road speed sqrt(gR) airborne crest
   physics". Showed two Physics Forums threads, Quora, Vedantu, The
   Student Room and the Wikipedia humpback-bridge page: a standard exam
   question with the threshold sqrt(g R).
   https://www.physicsforums.com/threads/calculating-max-speed-of-car-over-humpback-bridge-before-it-leaves-the-ground.453347/
   https://en.wikipedia.org/wiki/Humpback_bridge
6. "sliding ladder frictionless wall top leaves the wall at two thirds
   of initial height". Showed Physics Forums threads, Rhett Allain's
   Medium piece "When Does a Sliding Ladder Lose Contact With the Wall?",
   the AAPT advanced-lab file and the UT Austin ladder page; the Allain
   blog page fetched was the static friction version. The 2/3 comes from
   the sim.
   https://rjallain.medium.com/when-does-a-sliding-ladder-lose-contact-with-the-wall-0f2346548b76
   https://www.physicsforums.com/threads/ladder-leaning-on-frictionless-wall-and-frictionless-floor.495487/
7. "falling chimney breaks one third height bending moment toppling
   demolition physics". Showed Varieschi's Falling Chimney page (fetched
   below), "Toy models for the falling chimney", two 2023 and 2025
   demolition studies (middle break and bottom collapse) and an
   engineering-guidance page: brick chimneys break in mid-air near a
   third of the height, concrete ones topple whole.
   https://gvarieschi.lmu.build/chimney/chimney.html
   https://www.researchgate.net/publication/2168068_Toy_models_for_the_falling_chimney
   https://pmc.ncbi.nlm.nih.gov/articles/PMC12753805/
8. "swimmer always heads toward point across river current pursuit
   curve lands downstream half the width". Showed the Wikipedia
   radiodrome page (Bouguer 1732 dog curve), the arXiv "On swimmer's
   strategies in various currents" (fetched, PDF not readable, the
   summary garbled) and homework pages. The sim supplies the times.
   https://en.wikipedia.org/wiki/Radiodrome
   https://arxiv.org/pdf/2303.02751
9. "5 km/h faster impact speed where the slower car stops road safety
   physics 60 versus 65 km/h reaction time". Showed THINK! South
   Australia (risk doubles per 5 km/h in town), the AA and NHTSA stopping
   tables and calculators: the same mechanism as the stopping-distance
   short (1,012), so no new candidate.
   https://thinkroadsafety.sa.gov.au/staying-safe/safe-speeds
   https://www.theaa.com/breakdown-cover/advice/stopping-distances
10. "October 2026 science anniversaries physics events calendar early
    October 2026". Showed conference calendars (STS Forum, IAC Antalya
    5 to 9 October) and the Wikipedia October anniversaries portal:
    no tabletop peg in the next two weeks; Nobel physics 2026-10-06 and
    Sputnik 1957-10-04 stay space or no-motion pegs.
    https://en.wikipedia.org/wiki/Portal:History_of_science/Selected_anniversaries/October

## Sources (fetched pages)

- https://scienceblogs.com/dotphysics/2010/08/05/turn-or-go-straight-quick
  : a car can stop in half the distance it needs to turn; stopping
  v0^2 / (2 mu g), turning radius v0^2 / (mu g); same friction for
  braking and turning; a brake-then-turn mix was still longer than pure
  braking; comments note tyre, weight-transfer and narrow-obstacle
  limits.
- https://drdavepoolinfo.com/faq/draw/cloth-effects/ : sliding friction
  on the cloth wears the draw off on the way to the object ball; sticky
  cloth wears it faster; no distances or formulas.
- https://gvarieschi.lmu.build/chimney/chimney.html : bending moment of
  a uniform chimney falling about its base, N_b = -(1/4) m g sin(theta)
  H (r^3/H^3 - 2 r^2/H^2 + r/H), largest at a third of the height; at
  small angles breaks can come near the middle; Detroit (near the base)
  and Glasgow (near the middle) photos cited.
- https://www.usna.edu/Users/physics/mungan/_files/documents/Publications/TPT52.pdf
  and https://arxiv.org/pdf/2303.02751 : PDF bodies not readable by
  the fetch tool; titles only.
- https://rhettallain.com/2018/12/11/the-ladder-problem/ : the static
  friction ladder, not the frictionless slide.

## Measurements (python3, run 2026-09-29, /tmp/rt9/measure.py, log in /tmp/rt9/measure.log)

- Brake or swerve: 50 km/h (13.889 m/s), grip 0.8 g (7.8453 m/s^2) in
  any direction. Braking stops in 12.2940 m after 1.7703 s (RK4
  12.2940 m); turning at full grip and constant speed has radius
  24.5881 m, ratio 2.0000 (70 km/h: 24.10 against 48.19 m). Wall 15 m
  ahead: the braking car stops 2.71 m short; the turning car hits at
  1.1616 s at 50.00 km/h, turned 37.59 degrees (asin(d / R) = 37.59),
  5.105 m to the side, 39.62 km/h straight into the wall. Wall 20 m
  ahead: stops 7.71 m short; the turn hits turned 54.43 degrees. Wall
  10 m ahead: braking hits at 21.60 km/h, turning at 50.00 km/h. Brake
  first then turn: best total 12.294 m at brake share 1.00 (pure
  braking). Narrow obstacle: a 1, 2 or 3 m sidestep needs only 6.94,
  9.71 or 11.77 m forward, so the claim holds for a wide wall only.
- Ice cube against rolling ball: both at 3.0 m/s at the foot of a 20
  degree slope. Heights: ice cube 45.89 cm (v^2 / 2g), solid ball 64.24
  cm (1.400x, (1 + 2/5) v^2 / 2g), solid cylinder 68.83 (1.5x), hollow
  ball 76.48 (1.667x), hoop 91.77 (2.000x). Along the slope 134.17
  against 187.83 cm; tops at 0.8944 against 1.2522 s (RK4 equal to 1e-4
  s). No slip needs mu of at least (2/7) tan 20 = 0.104 for the ball
  (0.182 for the hoop). A ball rolling at 3 m/s onto an ice slope stops
  at 45.89 cm, 5/7 of 64.24, still spinning. V valley with a 0.5 m flat:
  periods 3.911 and 5.342 s.
- Draw shot: cue ball at 2.0 m/s struck half a radius below centre
  (R w0 = (5/2)(b/R) v0 = 2.5 m/s backspin), cloth mu 0.2, head-on hit
  on an equal ball. Slip speed falls at (7/2) mu g, forward speed at mu
  g, backspin at (5/2) mu g. Backspin gone at 0.5099 s after 76.48 cm
  at 1.0000 m/s (d* = (v0^2 - (v0 - 0.4 R w0)^2) / (2 mu g)); rolling
  at 0.6555 s after 88.97 cm at 0.7143 m/s ((5/7)(v0 - 0.4 R w0)).
  Object ball 30 cm away: hit at 0.1630 s at 1.6802 m/s with 1.7006 m/s
  of backspin left, the cue ball comes back at 0.4859 m/s (2/7 of the
  spin) after 6.0 cm of slip; 50 cm: back at 0.3056; 76.48 cm: stops
  dead; 120 and 150 cm: follows at 0.2041 m/s (2/7 of 0.7143); the
  object ball leaves at 1.680 and 0.714 m/s (it rolls at 5/7 of that).
- Car over a hump at constant speed: cosine hump 1.5 m high, 24 m long,
  crest radius 19.454 m, sqrt(g R) = 13.812 m/s = 49.72 km/h. At 40,
  45, 49 km/h it stays on the road (least road push 0.353, 0.181, 0.029
  weights); at 51 km/h it leaves 1.17 m before the top and hops 4.7 m,
  0.7 cm high; at 55 km/h 9.4 m, 10.4 cm; at 60 km/h it leaves 3.04 m
  before the top and flies 12.78 m in 0.774 s, 32.4 cm above the road
  at most.
- Swimmer across a 50 m river, swimming 1.0 m/s: current 0.8 m/s,
  heading always at the landing flag takes 138.64 s (closed form w v /
  (v^2 - u^2) = 138.89; the run stops 5 cm short) and is swept 16.89 m
  downstream before crawling back along the bank; aiming 53.13 degrees
  upstream crosses straight in 83.33 s (w / sqrt(v^2 - u^2)), ratio
  1.667; current 0.6 m/s: 78.1 against 62.5 s (1.25x), swept 11.81 m;
  current equal to the swim speed: the flag-heading swimmer ends 25.00
  m downstream, exactly half the width, and never lands.
- Sliding ladder, frictionless wall and floor, 4 m: the top leaves the
  wall at 0.66667 of its starting height from 75, 80 and 85 degrees
  (40.09, 41.04, 41.62 degrees above the floor; closed form sin theta =
  (2/3) sin theta0, where the centre's sideways speed peaks); lies flat
  at 1.34 to 1.91 s with the top landing 0.22 to 0.24 m from the wall;
  floor push after the release at least 0.19 weights. Visible
  difference is small.
- Falling chimney (uniform rod about its base): M(r) = (1/4) m g H sin
  theta (r/H)(1 - r/H)^2 peaks at r/H = 0.33333 with 1/27; a direct
  integral of the transverse loads gives the peak at 20 m of 60 m at 10,
  30 and 60 degrees; a 60 m stack from 0.5 degrees reaches 30 degrees
  at 9.68 s and lies flat at 12.00 s, top at 42.0 m/s.

## Candidates

Numbers are expectations to check; the sim measures the claim.

1. Brake or swerve (brakeswerve). Two cars at 50 km/h, a wide wall 15 m
   ahead, the same 0.8 g of grip; one brakes straight, one steers away
   at full grip. Hook: "Wall ahead. Brake or swerve?" Setup: 50 km/h;
   payoff: brake, it stops in 12.3 m; turning needs 24.6 m, twice as
   far, and hits at 50 km/h. Check: v^2 / (2 mu g) against v^2 / (mu
   g), impact angle asin(d / R). Renderable: top-down road, two point
   cars with a drawn body, closed forms plus RK4, under 25 minutes;
   repeat the run. Pillar: physics (friction). Accepted first: the
   sibling of stopping distance (1,012), a standing debate, an exact
   factor of 2, the panels end differently (stopped against crashed).
   Caveat: wide wall only (a 2 m sidestep needs 9.7 m), grip the same
   in every direction; say so in the description.
2. Ice cube or ball uphill (uphill). An ice cube sliding on ice and a
   solid ball rolling, both at 3 m/s at the foot of the same 20 degree
   slope. Hook: "Same speed. Which climbs higher, the ice cube or the
   ball?" Setup: 3 m/s; payoff: the ball, 64 cm against 46 cm, 40
   percent higher, because its spin also climbs. Check: h = (1 + k) v^2
   / 2g, k = 2/5; a hoop would go exactly twice as high. Renderable:
   closed forms in a V valley, a stripe on the ball, under 20 minutes;
   periodic per panel, repeat the launch. Pillar: physics (rotation,
   energy). Accepted: a split-intuition debate (the search tool itself
   got it wrong), the rolling-race family (950) with a new question,
   panels end at visibly different heights. Caveat: say the cube slides
   with no friction and the ball rolls without slipping (mu 0.104 or
   more needed).
3. Draw shot (drawshot). Two identical low hits, 2 m/s with backspin
   (tip half a radius low), the object ball 30 cm away beside 1.2 m
   away. Hook: "Hit it low. Does the cue ball come back?" Setup: the
   same low hit; payoff: only if the ball is closer than 76 cm; from 30
   cm it comes back at 0.49 m/s, from 1.2 m it follows at 0.20 m/s.
   Check: d* = (v0^2 - (v0 - 0.4 R w0)^2) / (2 mu g); after the hit the
   cue ball ends at 2/7 of its remaining spin. Renderable: the cue ball
   follow code (sims/cueball) with backspin and a second distance,
   under 25 minutes; repeat the shot. Pillar: physics (collisions,
   friction). Accepted: the third pool short after 957 and 952, a real
   player question, panels end on opposite sides. Caveat: the 76 cm
   depends on mu 0.2 and the tip offset, so state both.
4. Car over a hump (hump). The same car at a steady 40 and 60 km/h over
   a hump 1.5 m high and 24 m long. Hook: "How fast can you take the
   hump before the car flies?" Setup: a 19.5 m crest curve; payoff:
   about 50 km/h (sqrt(g R) = 49.7); at 60 km/h the wheels leave 3 m
   before the top and the car flies 12.8 m. Check: sqrt(g R). Renderable:
   side view, a point car with a drawn body, under 25 minutes; repeat.
   Pillar: physics (circular motion). Accepted mid: the bucket threshold
   family (939), but the hop is only 32 cm high, so draw the gap or use
   a sharper hump. Caveat: point car, no suspension.
5. Swim to the flag (swimflag). Two swimmers at 1.0 m/s across a 50 m
   river running 0.8 m/s, one always heading at the flag, one aiming
   53 degrees upstream. Hook: "Swim straight at the flag or aim
   upstream?" Setup: current 0.8 of the swim speed; payoff: aim
   upstream, 83 s against 139 s, the other swept 17 m down first.
   Check: w / sqrt(v^2 - u^2) against w v / (v^2 - u^2); at equal speed
   the flag swimmer ends half the width downstream for ever.
   Renderable: top-down river, RK4, under 20 minutes; played 5x. Pillar:
   physics (relative motion). Accepted mid: the lifeguard family (681),
   exact closed forms, visibly different paths. Caveat: a long real
   time, so speed it up.
6. Sliding ladder (ladder). A 4 m ladder let go at 75 degrees on a
   frictionless wall and floor. Hook: "Does a sliding ladder stay on the
   wall?" Payoff: no, the top leaves the wall at exactly 2/3 of its
   starting height. Check: sin theta = (2/3) sin theta0. Accepted low:
   exact, but the second panel is weak (a railed ladder lands in the
   corner, the free one 22 cm out) and the stick family sits at 395.
7. Falling chimney (chimney). A 60 m brick stack and a concrete stack
   toppling from the same lean. Hook: "A chimney falls. Where does it
   snap?" Payoff: a third of the way up (M = (1/4) m g H sin theta
   (r/H)(1 - r/H)^2). Accepted low: exact location, but the break angle
   is a chosen strength and the two-piece fall after the break is a
   40-minute build.

Rejected: ten km/h faster with a reaction time (the same payoff as the
stopping-distance short); rope fall factor (the panels end alike, the
payoff is a force reading); walk or run in the rain (a drop counter
with a body-box model); front against rear wheels locked (depends on the
nudge, tyre model over 25 minutes); soup can against frozen can (fitted
can masses, 18 percent, the rolling race again); block-stacking overhang
(static); bowling hook (oil pattern fitted, pin action unverifiable);
jumping in a falling lift (small visible difference, morbid); train
wheel flange moving backward (kinematics puzzle like the coin rotation
at 233); coffee and milk cooling (no motion); the pegs (Nobel physics,
Sputnik, IAC: space or no motion).

## Ranking

For today's three slots, one producer each, about 25 minutes with RK4 or
closed forms:

1. Brake or swerve (stops in 12.3 m; turning needs 24.6 m, twice as
   far, and hits at 50 km/h).
2. Ice cube or ball uphill (the ball, 64 cm against 46 cm, 1.4x).
3. Draw shot (back only if closer than 76 cm; 30 cm back at 0.49 m/s,
   1.2 m follows at 0.20 m/s).

Then car over a hump, swim to the flag, sliding ladder, falling chimney.

## Outcome

Seven ideas appended to `docs/niche.md` under "Added by trend research
2026-09-29 (evidence in task 20260929-100144; ...)". One line appended to
`web/data/log.jsonl`. The backlog count in the last entry of
`web/data/slate.json` changed from eighteen to twenty-five. No status
update, no production, no commit in this run by instruction. Existing
backlog entries were not changed.

## Files changed

- tasks/20260929-100144/TASK.md (this file)
- docs/niche.md (seven backlog bullets appended)
- web/data/log.jsonl (one line appended)
- web/data/slate.json (last entry title: twenty-five unproduced ideas)
