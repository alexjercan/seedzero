# Research trends: tabletop debates refill, run 6

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: backlog

## Goal

Sixth research-trends run, 2026-09-23 from about 10:05 EEST, for the third
slot of day 25. The backlog in `docs/niche.md` holds nine unproduced ideas:
spring pendulum swap and Zeno bounce (both in production today, not
proposed here) and seven that the run-5 filter rejected as space
time-lapses, counters or drawings (Collatz flights, secretary problem,
rogue wave, Saturn retrograde, Halley's comet, L2 drift, Kelvin wake).
Find 6 to 10 new candidates that fit the winning formats: continuous
physical motion, two panels on the same input, one plain question in the
first two seconds, one setup number, one payoff number, a closed-form
check, and a seamless loop where the physics is periodic. Measure the top
three with throwaway scripts before recording them. No production in this
run. By instruction `web/data/slate.json` and `web/data/status.json` were
not touched, sims/, projects/, media/ and secrets/ were not touched, and
no commit was made.

## Channel evidence used for the filter

Views at run time (`web/data/slate.json`, refreshed 2026-09-22 10:36):
double pendulum 1,161, Fourier circles 1,047, coupled pendulum swap
1,046, A-star maze 978, big swing 973, turntable ball 973, loop the loop
963, monkey and hunter 963, Newton's cradle 958, rolling race 950,
brachistochrone 948, Dzhanibekov 946, tautochrone 943, pi collisions 941,
tsunami 940, hoop bead 925, water wheel 922. The pattern holds from run 5:
continuous motion, a plain question, two panels on the same input, one
setup number, one payoff number, a loop where the physics is periodic,
and path races on the same start and end (brachistochrone, rolling race,
A-star). Underperformers: space time-lapses (orbit passing lane 6,
gravity assist 33, gravity train 74), probability counters (Monty Hall
99, best of seven 50, buses 47), static drawings (birthday 5, sticker 36,
rainbow 79), tie payoffs (bullet drop 85). New since run 5: the day-23
trio split (big swing 973 against tetherball 158 and Torricelli 239), so
a spiral-geometry piece and a static-tank jet piece did not carry, while
the nonlinear pendulum pair did; day 24 is one day old (braking 466,
lifeguard 330, bounce slope 277). The filter therefore favoured tabletop
mechanics and fluids in visible motion, path races, collisions with an
exact ratio, and viral debates a number settles; it rejected space,
counters, drawings, tie payoffs and anything with a contested constant.

## Queries (10 WebSearch, 5 WebFetch, one DNS failure)

1. "viral physics demonstration shorts September 2026 counterintuitive
   tabletop experiment". Showed a "Debunking Terrible Physics" early
   September 2026 session, the fluxnote list (unchanged from run 5),
   "Counter-Intuitive Physics" and "physics is fun" shorts, the two-part
   spool demo, and the Veritasium and Physics Girl pages. No single demo
   dominates this month; the winning form is still one "I had no idea"
   moment inside 60 s. Debunking wrong physics is itself a live format,
   which supports the debate candidates below.
   https://www.youtube.com/watch?v=kjN6hqTU_W4
   https://fluxnote.io/guides/science-youtube-shorts-ideas
   https://www.youtube.com/shorts/4bXppejuEkE
2. "physics simulation animation YouTube channel shorts 2026 popular sim
   videos pendulum collision fluid". Showed the Simulated Physics
   channel, Blender physics-sim playlists, a May 2026 "most satisfying 3D
   physics simulation showcase" (4K Blender compilations with no claim),
   MinutePhysics (5.94 M) and Physics Girl (3.48 M). The sim channels near
   the niche post raw satisfying sims with no measured number; the gap
   in `docs/niche.md` still stands.
   https://www.youtube.com/channel/UCi0_J1sxClKRC5ppdnWbE2w
   https://www.youtube.com/watch?v=F-Rp6HgGfxI
   https://en.wikipedia.org/wiki/MinutePhysics
3. "Nobel Prize physics 2026 predictions announcement October 6 2026
   Clarivate citation laureates". Showed the physics announcement is
   Tuesday 2026-10-06 at 11:45 CEST; predictions favour quantum
   computing, dark matter detection and gravitational waves; Clarivate's
   2026 citation laureates land at the end of September. None of these
   is a tabletop motion sim, so Nobel week stays a peg for the queued
   quantum ideas only (tunnelling and double slit already produced).
   https://www.nobelprize.org/press-release/the-2026-nobel-prize-announcements/
   https://www.physicsforums.com/threads/nobel-prize-in-physics-2026-predictions.1086166/
4. "bathtub drain direction Coriolis hemisphere myth Shapiro 1962
   experiment residual rotation 24 hours settle". Showed the Straight
   Dope, MIT Technology Review, the Daily Texan and Weird Science History
   (fetched below): Shapiro's 6 ft tank at 42 N sat still for a day, took
   20 min to drain, the float sat still 12 to 15 min then turned
   counterclockwise up to one turn every 3 to 4 s; the Coriolis
   acceleration was thirty-millionths of gravity; Sydney repeated it in
   1965 clockwise. The myth is still asked and still answered wrong.
   https://www.straightdope.com/21341330/do-bathtubs-drain-counterclockwise-in-the-northern-hemisphere
   https://www.technologyreview.com/2012/10/24/183079/verifying-a-vortex/
   https://www.weirdsciencehistory.com/articles/the-bathtub-that-took-24-hours-to-drain-to-test-a-myth
5. "two ball track race dip track longer path arrives first demo". Showed
   the Stony Brook, UCLA, Purdue and Maryland lecture-demo pages, an NTNU
   applet, a Bruce Yeany video and a Glassdoor interview question: two
   equal balls launched at the same speed, one track flat, one dips and
   returns; the dipped ball wins although its track is longer; the demo
   is used as a prediction question because most people pick the flat
   track or a tie. Fetched Maryland below.
   https://lecdem.physics.umd.edu/highlight-racing-balls.html
   https://labdemos.physics.sunysb.edu/c.-kinematics-and-dynamics/c2.-kinematics-in-one-and-two-dimentions/racing-balls
   https://ephysics.physics.ucla.edu/racing-balls
6. "ballistic pendulum bullet bounces off versus embeds which swings
   higher". Showed Pearson, LibreTexts, BU, LVC and CK-12 ballistic
   pendulum pages, a Physics Forums thread and Homework.Study: the block
   moves faster when the bullet bounces than when it sticks; the
   embedded case keeps only m/(M+m) of the energy. The stick-or-bounce
   question is a standard misconception item (arXiv 1602.07756).
   https://phys.libretexts.org/Courses/Prince_Georges_Community_College/General_Physics_I:_Classical_Mechanics/32:_The_Ballistic_Pendulum
   https://physicsforums.com/threads/2-bullets-same-mass-same-v-fired-at-wood-and-steel-block-which-block-has-v.278944
   https://arxiv.org/pdf/1602.07756
7. "superball thrown under table comes back Garwin model spin reversal
   bounce". Showed Garwin 1969 (rough elastic ball: the contact-point
   velocity reverses), Rod Cross's bounce pages and papers, and the
   ScienceDirect floor-and-wall kinematics paper: a superball thrown
   under a table returns to the hand after floor, table, floor. A real
   audience demo with a closed-form bounce map.
   https://www.physics.usyd.edu.au/~cross/BOUNCE.htm
   https://www.physics.usyd.edu.au/~cross/PUBLICATIONS/31.%20Spin.pdf
   https://www.sciencedirect.com/science/article/abs/pii/S0020746210001344
8. "dam break Ritter solution front speed 2 sqrt(gh) dry bed shallow
   water simulation wet bed Stoker bore". Showed Ritter 1892 (dry front
   at 2 sqrt(g h0), the dam-site depth 4/9 h0), Stoker 1957 (wet bed,
   a bore), Coastal Wiki, an arXiv 2026 Python library (amerta) for 1D
   Saint-Venant dam breaks, and flume comparisons that confirm the front
   speed. A fluids candidate with an exact check but a heavier solver.
   https://www.coastalwiki.org/wiki/Dam_break_flow
   https://arxiv.org/pdf/2605.31011
   https://www.researchgate.net/publication/313539545_Ritter's_dry-bed_dam-break_flows_positive_and_negative_wave_dynamics
9. "physics anniversaries October 2026 centenary". Showed the CFR and UK
   2026 anniversary lists (Goddard's liquid rocket 1926, Baird's
   television 1926, Bell's telephone 1876, US 250th) and the Wikipedia
   October physics portal (fetched below). No mechanics anniversary with
   a round number in the window; no new peg.
   https://en.wikipedia.org/wiki/Portal:Physics/Anniversaries/October
   https://www.cfr.org/articles/ten-anniversaries-note-2026
10. "basketball shot arc entry angle effective hoop width 45 degrees vs
    flat shot". Showed Spalding and Noah Basketball: the hoop looks 18 in
    wide to a ball entering vertically, 12.7 in at 45 degrees and 9.0 in
    at 30 degrees (under the 9.5 in ball, so no clean shot); the trade
    is that high arcs spread more in depth. A sports peg for the NBA
    opening in late October 2026, a cheap projectile sim.
    https://smartbasketball.spalding.com/pages/how-shot-arc-affects-shooting-accuracy
    https://www.noahbasketball.com/blog/the-science-of-shooting-arc

Fetched pages:

- https://lecdem.physics.umd.edu/highlight-racing-balls.html : two
  parallel tracks, equal balls at identical launch speeds; one straight
  and level, one slopes down, runs level lower, slopes back up; the dipped
  ball finishes first because it is never slower and is faster on the
  low section; no numbers given, which is the gap the sim fills.
- http://classic.scopeweb.mit.edu/articles/shapiros-bathtub-experiment/ :
  DNS failure.
- https://www.weirdsciencehistory.com/articles/the-bathtub-that-took-24-hours-to-drain-to-test-a-myth
  : 6 ft by 6 in tank, centred drain on a 20 ft hose, 42 N, filled with a
  clockwise swirl, sealed a full day; drained in about 20 min; the float
  was still for 12 to 15 min, then turned counterclockwise up to one turn
  every 3 to 4 s; Coriolis thirty-millionths of gravity; Sydney 1965
  clockwise.
- https://en.wikipedia.org/wiki/Portal:Physics/Anniversaries/October :
  Yang 1922-10-01, NASA 1958-10-01, Bohr 1885-10-07, Dirac died
  1984-10-20; none round in 2026.
- https://www.3blue1brown.com and the run-5 pages were not re-fetched.

## Measurements (python under nix, run 2026-09-23, scripts in /tmp/rt6)

- Racing balls: launch 1.0 m/s, 2.0 m of track, cosine ramps 0.3 m long
  from x 0.4 m into a 0.6 m low section, energy along the track (v^2 =
  v0^2 + 2 g depth / (1 + k)). Flat track 2.0000 s. Dip 0.10 m: sliding
  1.6263 s (lead 0.374 s, track +2.0%), rolling ball (k 2/5) 1.6941 s.
  Dip 0.20 m: sliding 1.5438 s (lead 0.456 s, track 2.1406 m, +7.0%, top
  speed 2.219 m/s), rolling 1.6199 s (lead 0.380 s). Dip 0.30 m: sliding
  1.5291 s, rolling 1.6111 s (track +13.9%). An RK4 bead-on-wire run
  (xddot = -(g y' + y' y'' xdot^2)/(1 + y'^2), 0.1 ms steps) crosses the
  2 m line at 1.5438 s with exit speed 1.0000 m/s, matching the energy
  integral to four decimals.
- Ballistic pendulum: 20 g ball at 20 m/s into a 200 g block on a 1.0 m
  string. Sticks: block 1.8182 m/s, rises 16.855 cm, 33.75 degrees, the
  pair keeps 9.09 percent of the energy. Bounces (elastic): block 3.6364
  m/s, rises 67.419 cm, 70.99 degrees, the ball comes back at 16.36 m/s.
  Height ratio 4.0000 exactly at every mass ratio tried (10 g at 300 m/s
  into 2 kg: 11.36 against 45.43 cm; 50 g at 15 m/s into 500 g: 9.48
  against 37.92 cm), because (2m/(M+m))^2 / (m/(M+m))^2 = 4. RK4 swing
  at 0.1 ms: peaks 33.752 degrees at 0.5128 s and 70.985 degrees at
  0.5545 s, back at the bottom at 1.0255 and 1.1089 s (the big swing is
  8 percent slower, so the panels drift; the short repeats the shot
  rather than looping the swing).
- Bathtub drain: Shapiro's 6 ft tank (R 0.9144 m) at 42 N, f/2 = 4.879e-5
  rad/s (one turn every 35.77 h), constant depth, sink flow r^2 = R^2 (1
  - t/1200 s), a parcel's absolute spin r^2 (omega + f/2) conserved so
  omega(r) = (omega0 + f/2)(R/r)^2 - f/2 (sign of f flipped in the south).
  Leftover swirl one turn per 10 min (0.01047 rad/s, 215x f/2): the drain
  spins the leftover way in both hemispheres, 0.93 percent apart (5 mm
  drain radius 351.9 against 348.6 rad/s; 2 cm plughole 21.99 against
  21.79 rad/s, one turn per 0.29 s), 20.92 against 20.75 turns from rim
  to drain. One turn per hour: 5.44 percent apart, still the same way.
  Perfectly still water: north counterclockwise, south clockwise, one
  turn per 3.85 s at a 5 mm drain (Shapiro saw 3 to 4 s), one turn per
  61.6 s at a 2 cm plughole; the parcel makes only 0.088 turns on the
  whole way in and passes one turn per minute only in the last second
  at r 2 cm. Threshold: the leftover swirl must be under one turn per
  35.8 h for the hemisphere to decide the direction.
- Superball under a table (Garwin map, rough elastic, alpha 2/5, R 3 cm):
  thrown from 0.4 m at 2.5 m/s forward and 2.5 m/s down under a table
  0.7 m high; floor at x 0.300 m (vx 2.50 to +1.07 m/s), table underside
  at 0.594 m (to -4.64 m/s), floor at x -0.683 m (to -1.99 m/s): back
  behind the thrower after three bounces at 0.670 s; the smooth ball
  keeps 2.50 m/s and is at x 1.675 m at the same third bounce.
- Merry-go-round: 2 m platform at 10 rpm, a 4 m/s throw straight at the
  rider opposite: 1.000 s flight, the target moves 60.0 degrees, the
  ball misses by a 2.000 m chord (2.094 m of arc).
- Corner reflector: a 90 degree corner returns the puck 0.0 degrees off
  its incoming line from any entry angle; 85 degrees 10.0 off, 80 or 100
  degrees 20.0 off (deviation 2 alpha).
- Ritter dam break: 1 m wall, dry bed: front 6.263 m/s (2 sqrt(g h0)),
  the dam site settles at 0.4444 m (4/9 h0) flowing 2.088 m/s, the
  drawdown runs back at 3.132 m/s, front 62.6 m out at 10 s; 4 m wall:
  12.526 m/s front (2x for 4x the height), 1.778 m at the dam.
- Basketball: hoop 45.7 cm, ball 24.0 cm; the hoop looks 22.8 cm wide at
  a 30 degree entry (1.2 cm narrower than the ball), 32.3 at 45, 37.4 at
  55, 45.7 at 90. Free throw (release 2.0 m, rim 3.05 m, 4.19 m out):
  launch 35 degrees at 8.252 m/s enters at 11.3 degrees and the hoop
  looks 8.9 cm wide; 45 degrees at 7.405 m/s enters at 26.5 (20.4 cm);
  52 degrees at 7.257 m/s (the slowest shot) enters at 37.9 (28.1 cm);
  60 degrees at 7.448 m/s enters at 50.9 (35.5 cm).
- Moon clock: a pendulum swing is sqrt(9.80665/1.62) = 2.4604x slower on
  the Moon (1.000 s becomes 2.460 s); a spring clock keeps 1.000 s.

## Candidates

Numbers are expectations to check; the sim measures the claim.

1. Racing balls. Two equal balls launched at 1 m/s on a flat track beside
   a track that dips 20 cm and comes back up. Hook: "Which ball finishes
   first: the flat track or the dip?" Setup 1 m/s over 2 m; payoff: the
   dip wins by 0.46 s (1.54 against 2.00 s) on a track 7 percent longer.
   Check: v = sqrt(v0^2 + 2 g depth) along the track, flat time L/v0.
   Renderable: bead on a wire like the brachistochrone sim, RK4, under 45
   minutes. Visual: two balls side by side, one drops, races ahead on the
   low road, climbs back to the same speed and is still ahead; the race
   repeats. Pillar: physics (energy). Accepted: the path-race family
   (brachistochrone 948, rolling race 950, A-star 978), a prediction
   question with a majority wrong answer, cheapest build of the set.
2. Ballistic pendulum. A 20 g ball at 20 m/s into a 200 g block on a 1 m
   string, a ball that sticks beside a ball that bounces. Hook: "Which
   swings the block higher: the ball that sticks or the ball that
   bounces?" Setup 20 m/s; payoff: sticks 17 cm, bounces 67 cm, exactly
   4 times higher. Check: (2m/(M+m))^2 / (m/(M+m))^2 = 4 at any masses.
   Renderable: one impulse rule plus an RK4 pendulum, under 45 minutes.
   Visual: two blocks hit at once, one swings to 34 degrees, the other to
   71; the shot repeats. Pillar: physics (collisions). Accepted: a
   standard misconception item, an exact integer ratio, continuous
   motion; caveat: the panels drift out of step (periods 2.05 against
   2.22 s), so repeat the shot rather than loop the swing.
3. Bathtub drain. Shapiro's 6 ft tank with a leftover swirl of one turn
   every 10 minutes, at 42 N beside 42 S. Hook: "Does the bath drain the
   other way in Australia?" Setup: one turn every 10 minutes leftover;
   payoff: no, both drains spin the leftover way, 0.9 percent apart; the
   water must sit stiller than one turn every 36 hours before the
   hemisphere decides (Shapiro waited a day and saw one turn every 3 to 4
   s). Check: (omega0 + f/2)(R/r)^2 - f/2 with f = 2 Omega sin(latitude).
   Renderable: surface parcels spiralling into a sink with conserved
   absolute spin, exact per parcel, under one hour. Visual: two tubs of
   tracer particles draining and whirling the same way; second beat, the
   still tubs turn opposite ways. Pillar: physics (fluids). Accepted: a
   viral debate settled with a number, fluids in motion (tsunami 940);
   caveat: the inviscid model gives very fast drain spin at a small
   drain, so state the model and pick the 2 cm plughole.
4. Superball under a table. A rough bouncy ball beside a smooth ball
   thrown the same way under a 70 cm table. Hook: "Throw a bouncy ball
   under a table. Where does it end up?" Setup 2.5 m/s; payoff: back
   behind you, 0.68 m behind the throw after three bounces, while the
   smooth ball is 1.7 m ahead. Check: Garwin's rough-elastic map
   (contact velocity reverses, angular momentum about the contact point
   kept). Renderable: projectile plus two bounce maps, under one hour.
   Pillar: physics (collisions). Accepted mid: a real audience demo, but
   spin is the mechanism and is hard to read on a plain ball.
5. Merry-go-round throw. A 2 m platform at 10 rpm, a 4 m/s throw straight
   at the rider opposite, the ground view beside the rider's view. Hook:
   "Throw straight at your friend on a merry-go-round. Do you hit?"
   Setup 10 rpm; payoff: a 2.0 m miss, the ball curves away in the
   rider's view while flying straight from above. Check: miss chord 2 R
   sin(omega R / v). Renderable: kinematics, exact, under 30 minutes;
   periodic so it loops. Pillar: physics (rotation). Accepted mid: same
   theme as the turntable ball (973); the surprise is milder.
6. Corner reflector. A puck fired into a 90 degree corner beside an 80
   degree corner at several entry angles. Hook: "Fire a puck into a
   corner. Where does it come back?" Setup 90 degrees; payoff: straight
   back along its own line, 0.0 degrees off at every angle; the 80 degree
   corner sends it 20 degrees off. Check: deviation 2 alpha. Renderable:
   two wall reflections, under 30 minutes; repeats. Pillar: physics
   (collisions). Accepted lower: exact and cheap, but the payoff is a
   tie-like "always zero", the family that sat at 85 views.
7. Dam break. A 1 m wall of water released onto a dry channel beside a 4
   m wall. Hook: "Break a dam. How fast does the flood run?" Setup 1 m;
   payoff: the front runs at 6.3 m/s (2x the wave speed) and the level at
   the dam drops to 44 cm and holds. Check: Ritter, 2 sqrt(g h0) and
   4/9 h0. Renderable: 1D nonlinear shallow water with a dry front
   (HLL finite volume), one to two hours, heavier than RK4. Pillar:
   physics (fluids). Accepted with a build caveat: exact check, fluids
   in motion, but not a one-hour sim.
8. Basketball arc. The same free throw at a 35 degree launch beside 52
   degrees. Hook: "Does a higher arc make the shot easier?" Setup: a 24
   cm ball into a 45.7 cm hoop; payoff: the flat shot enters at 11
   degrees and the hoop looks 8.9 cm wide to it, the 52 degree shot
   enters at 38 degrees and the hoop looks 28 cm wide. Check: effective
   width D sin(entry). Renderable: projectile, under 30 minutes; repeats.
   Pillar: physics (projectiles). Accepted lower (peg: NBA opening, late
   October 2026): cheap, but the payoff is a width, closer to a drawing.
9. Moon clock. A pendulum clock and a spring clock on Earth beside the
   same pair on the Moon. Hook: "Take two clocks to the Moon. Which one
   slows down?" Setup 1.000 s per swing; payoff: the pendulum takes 2.46
   s, the spring keeps 1.000 s. Check: sqrt(g / g_moon) = 2.460.
   Renderable: two ODEs, under 30 minutes; periodic so it loops. Pillar:
   physics (oscillators). Accepted lowest: exact and cheap, mild
   surprise, four moving things on screen.

Rejected: interrupted pendulum with a peg (same energy story as loop the
loop, published three days ago); ballistics cart (a tie payoff, the
bullet-drop family at 85); sloshing seiche period (no surprise);
Euler's spinning disk (rolling-disk rigid body, over an hour, the
finite-time singularity depends on a dissipation model); Nobel
prediction topics (quantum computing, dark matter, gravitational waves:
no tabletop motion sim); Blender "satisfying" showcases (no claim);
October anniversaries (none round); the fluxnote thermal items (no motion
sim, contested constants).

## Ranking

For today's third slot, one agent, under an hour with RK4 or closed forms:

1. Racing balls (the dip wins by 0.46 s over 2 m on a 7 percent longer
   track; bead-on-wire RK4 exists in-repo; the path-race family sits
   near 950).
2. Ballistic pendulum (sticks 17 cm, bounces 67 cm, exactly 4x; one
   impulse rule plus an RK4 pendulum).
3. Bathtub drain (both hemispheres spin the leftover way, 0.9 percent
   apart; still water needs 36 h; a fluids debate with Shapiro's numbers
   as the peg).

Then superball under a table, merry-go-round throw, corner reflector,
dam break (heavier), basketball arc, Moon clock.

## Outcome

Nine ideas appended to `docs/niche.md` under "Added by trend research
2026-09-23 (evidence in task 20260923-101345; selection favoured continuous physical
motion, two-panel same-input comparisons, one plain question per short,
one setup number and one payoff number, path races and collisions with
an exact ratio, viral debates a number settles, and numbers that a closed
form can check)". One line appended to `web/data/log.jsonl`. No slate or
status update, no production, no commit in this run by instruction.
Existing backlog entries were not changed.
