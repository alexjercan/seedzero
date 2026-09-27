# Research trends: pool cuts, coins and tablecloths, run 8

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: backlog

## Goal

Eighth research-trends run, 2026-09-27 from about 10:05 EEST, for the
three slots of day 29. The backlog in `docs/niche.md` holds fifteen
unproduced ideas and none is a strong first pick: seven are space
time-lapses or counters (Kelvin wake, Collatz, secretary, rogue wave,
Saturn retrograde, Halley, L2 drift), corner reflector, basketball arc
and Moon clock were ranked low, bathtub drain is a tie payoff, dam break
is a heavy build, balance a broom is ranked mid (half-known answer), bat
sweet spot has a late-October peg and a near-tie panel, Atwood drop is
ranked low. Find 6 to 9 new candidates that fit the winning format:
continuous tabletop motion, two panels on the same input that end
differently, one plain question in the first two seconds, one setup
number, one payoff number, a closed-form check, a loop or a repeat, and
a build of about 25 minutes with RK4 or closed forms (no PDE, no fluid
grid, no ray tracing, no fitted aerodynamics). Measure every survivor
with a throwaway script before recording it. No production in this run.
By instruction `web/data/status.json`, sims/, projects/, media/ and
secrets/ were not touched and no commit was made; `web/data/slate.json`
only had its backlog count updated.

## Channel evidence used for the filter

Views at run time (`web/data/slate.json`, refreshed 2026-09-27 10:02):
the shorts the feed picks up sit near 900 to 1,050 and share one format:
continuous tabletop motion, two panels on the same input that end
differently, one plain question, one setup number, one payoff number, a
closed-form check, a loop or a repeat. Recent: cue ball follow 957 and
bucket over the head 920 after two days, superball under a table 935 and
ballistic pendulum 591 after three, spool 490, spring squash 462, folded
chain 353, Tarzan release 120 after one day, merry-go-round 2 (a
space-like top-down view); earlier braking 1010, spring swap 835, racing
balls 743, Zeno bounce 636, lifeguard 680, bounce slope 675, coupled
pendulums 1,047, pi blocks 994, loop the loop 967, monkey and hunter
963, cradle 958, rolling race 950. Formats at 5 to 99 views: space
time-lapses (orbit 6, gravity train 74, gravity assist 33), counters and
random-draw statistics (birthday 5, sticker album 36, buses 47),
drawings (rainbow 79, Mach cone 79) and tie payoffs (bullet drop 85).
Collision and pool pieces, threshold questions ("how slow before it
spills") and loop-or-fall pieces are the strongest genres. The filter
therefore favoured everyday "which way", "which first", "does it stop"
debates with an exact fraction, angle or threshold, two panels that end
differently, and cheap builds; it rejected space, counters, drawings,
tie payoffs, fitted constants and rider or posture models.

## Queries (10 WebSearch, 9 WebFetch of which 1 failed)

1. "viral physics demonstration shorts September 2026 counterintuitive
   tabletop debate". Showed the "Debunking Terrible Physics" early and
   mid-September 2026 sessions (bad TikTok physics broken down, so the
   debate format is still live), the fluxnote list (unchanged since run
   5), "Counter-Intuitive Physics" shorts, the Expert TA demo guide with
   the two-part spool (produced 2026-09-25) and a June 2026 phys.org
   tabletop fundamental-physics item (no motion sim). No single demo
   dominates this month.
   https://www.youtube.com/watch?v=WvaE85Ht8uc
   https://www.youtube.com/watch?v=kjN6hqTU_W4
   https://blog.theexpertta.com/in-class-physics-demonstrations
   https://fluxnote.io/guides/science-youtube-shorts-ideas
2. "physics simulation animation channel new video September 2026
   rolling collision pendulum". Showed the Simulated Physics and Physics
   Simulations channels, physics-simulations.org pendulum pages and
   Box2D-style sim playlists; the sim channels still post satisfying
   sims with no measured claim, so the gap stands. Nothing new this
   month worth a peg.
   https://www.youtube.com/channel/UCi0_J1sxClKRC5ppdnWbE2w
   https://www.youtube.com/channel/UCXGN2hXVqqyk6jI6vOJgVoA/videos
   https://physics-simulations.org/simulation/double-pendulum/
3. "coin rotation paradox rolls around identical coin how many turns
   SAT question viral". Showed Wikipedia (fetched below), Scientific
   American's "The SAT Problem That Everybody Got Wrong" (fetched
   below), two calculators, NeoTeo, Umais and a 2026 Oreate blog retelling
   the 1982 SAT story (3 of 300,000 test takers caught it): the paradox
   keeps recirculating and the answer is an exact integer.
   https://en.wikipedia.org/wiki/Coin_rotation_paradox
   https://www.scientificamerican.com/article/the-sat-problem-that-everybody-got-wrong/
   https://www.neoteo.com/en/the-rolling-coin-paradox
4. "pool 90 degree rule 30 degree rule cut shot rolling cue ball physics
   natural roll". Showed Dr Dave's 30 degree and 90 degree rule pages
   (fetched below), the pooltool documentation example, an AzBilliards
   thread and a 2005 Billiards Digest article: the 90 degree rule holds
   for a sliding cue ball and the 30 degree rule (about 34 degrees near a
   half-ball hit) for a rolling one; the exact fraction (5/7 and 2/7)
   comes from the sim. The sibling of cue ball follow (957 views).
   https://drdavepoolinfo.com/faq/30-90-rules/30-degree-rule/
   https://drdavepoolinfo.com/faq/30-90-rules/
   https://pooltool.readthedocs.io/en/latest/examples/30_degree_rule.html
5. "tablecloth trick physics how fast must you pull friction glass
   stays". Showed UCSB 12.12 (fetched below), Science World, UW Wonders
   of Physics, UMD lecdem, PhysLink and two Physics Forums threads: all
   explain the trick in words (impulse, short contact time) and none
   gives the threshold pull speed; the sim supplies it.
   https://web.physics.ucsb.edu/~lecturedemonstrations/Composer/Pages/12.12.html
   https://wonders.physics.wisc.edu/beaker-and-cloth/
   https://lecdem.physics.umd.edu/tools-and-resources/lecdem-blog/411-blog-highlight-tablecloth-part1.html
6. "inertia ball two strings which string breaks pull slowly jerk
   demonstration". Showed the PIRA 1F20.10 inertia ball at Brown, UW,
   Minnesota, Washington, Wesleyan and UCSC, Mungan's note and the arXiv
   "Analytic expression for pull-or-jerk experiment" (fetched below): a
   standard prediction demo with a majority wrong answer, slow pull
   snaps the top string, a jerk snaps the bottom.
   https://ar5iv.arxiv.org/html/1408.6393
   https://wiki.brown.edu/confluence/display/PhysicsLabs/1F20.10+Inertia+Ball
   https://www.usna.edu/Users/physics/mungan/_files/documents/Scholarship/InertiaBall.pdf
7. "bicycle front brake over the handlebars physics threshold
   deceleration center of mass endo". Showed two Physics Forums
   threads, Ron George's endo analysis (fetched below), three brake
   patents and the Wikipedia geometry page: the rear lifts when the
   deceleration passes g times the centre-of-mass distance behind the
   front contact over its height, about 0.5 g; what happens after the
   lift depends on the rider, so the idea was rejected.
   http://www.georgeron.com/2009/10/analysis-of-bicycle-endo.html
   https://www.physicsforums.com/threads/bicycle-physics-flying-over-the-handlebars.205437/
8. "head-on collision two cars 50 mph each same as wall at 100 mph
   physics debate". Showed the rec.autos.tech thread, a Physics Forums
   thread, Rhett Allain's Medium piece (403), Wikipedia head-on
   collision, Warp's collision math and Greg Laden's MythBusters
   write-up (fetched below): a live debate that MythBusters settled with
   crushed cars; each car in a 50 + 50 head-on takes a 50 into a wall,
   not a 100.
   https://gregladen.com/blog/2017/10/11/mythbusters-on-head-on-collisions/
   https://www.physicsforums.com/threads/what-is-the-true-impact-speed-when-two-cars-collide-head-on-at-50mph.456239/
   https://en.wikipedia.org/wiki/Head-on_collision
9. "pendulum string catches peg bob loops around peg 3/5 length
   condition demonstration". Showed the UMass 1M40.15 pendulum and peg
   demo, Penn's "The Peg and the Pendulum", av8n's interrupted pendulum
   page (fetched below), Brainly and Quizlet homework: a standard demo,
   the string stays taut around the peg only if the peg sits at least
   3/5 of the string below the pivot for a horizontal release.
   https://physicslectureprep.umasscreate.net/mechanics/1m40-15-pendulum-and-peg/
   https://www.physics.upenn.edu/demolab/manumech/we1.html
   https://www.av8n.com/physics/loop-de-loop.htm
10. "does it take longer to go up or come down ball ramp friction
    physics question". Showed BU's block on a ramp, UCSC and Illinois
    Physics Van pages, a Wolfram demonstration and a Physics Forums
    thread: with friction the way down takes longer, a homework-style
    result whose ratio is set by the friction number chosen; measured
    and rejected as mild.
    http://physics.bu.edu/~redner/211-sp06/class05/block_ramp.html
    https://ucscphysicsdemo.sites.ucsc.edu/physics-5a6a/ball-rolling-down-inclined-plane/

## Sources (fetched pages)

- https://drdavepoolinfo.com/faq/30-90-rules/30-degree-rule/ : for a
  rolling cue ball between a 1/4-ball hit (49 degree cut) and a 3/4-ball
  hit (14 degree cut) the cue ball deflects close to 30 degrees from its
  original direction, about 34 degrees near a half-ball hit and about 27
  near quarter and three-quarter; the cue ball must be rolling; the 90
  degree rule (sliding cue ball, paths perpendicular) is a separate
  page. The sim's 33.7 degrees at a half-ball hit matches the 34.
- https://en.wikipedia.org/wiki/Coin_rotation_paradox : a coin rolled
  around an identical coin makes two full rotations; in general R/r + 1
  outside; the May 1982 SAT problem had no correct choice and three
  students (Jungreis, Kartha, Taub) forced a regrade; the straight-line
  view explains the first rotation and the circular path the second.
- https://www.scientificamerican.com/article/the-sat-problem-that-everybody-got-wrong/
  : the 1982 SAT asked for a small circle rolling around one three times
  its radius; the key said 3, the answer is 4; 3 of 300,000 students
  reported it and 300,000 exams were rescored.
- https://web.physics.ucsb.edu/~lecturedemonstrations/Composer/Pages/12.12.html
  : a place setting on a bedsheet tablecloth; a slow pull carries
  everything to the floor, a fast pull leaves the setting; measured
  friction for a melamine plate 0.19 static, 0.16 kinetic (7.3 kg block
  on a 173 g plate); pull at about 45 degrees. No threshold speed.
- https://ar5iv.arxiv.org/html/1408.6393 : the pull-or-jerk model,
  x'' + ((k1 + k2)/m) x = (k2 V / m) t with tensions f1 = k1 x + m g and
  f2 = k2 (V t - x); slow pulls keep f1 above f2 so the upper string
  breaks; fast pulls let the tensions cross; example 500 g on sewing
  thread (12 N, 170 N/m), 1 m/s. The sim uses stiffer strings and a 1
  kg ball, the same equations.
- http://www.georgeron.com/2009/10/analysis-of-bicycle-endo.html : the
  rear wheel lifts when the braking force over the weight reaches A/H
  (centre of gravity aft of the front contact over its height); front
  brakes give up to 0.5 g, rear 0.1 to 0.2 g; the analysis stops at the
  lift and says the geometry varies with the rider.
- https://gregladen.com/blog/2017/10/11/mythbusters-on-head-on-collisions/
  : MythBusters ran one car into a wall at 50 mph, one at 100 mph and
  two cars head-on at 50 mph each; the head-on cars were mushed the same
  as the 50 mph wall car; the energy is split between two wrecks.
- https://www.av8n.com/physics/loop-de-loop.htm : the interrupted
  pendulum in units L = 1, g = 1: energy in [-1, 0] never slack, energy
  at or above 1.5 goes over the top with the string winding around the
  peg, between them the string goes slack where gravity along the string
  balances the centrifugal term (E = 1.5 S). No peg-distance ratio given;
  the 3/5 comes from the sim and the energy argument.
- https://rjallain.medium.com/is-a-50-mph-50-mph-collision-the-same-as-a-100-0-mph-collision-27c0d4391512
  : HTTP 403, replaced by the Greg Laden page.

## Measurements (python under nix, run 2026-09-27, /tmp/rt8/measure.py, log in /tmp/rt8/measure.log)

- Cut shot: 57.15 mm balls, cue ball at 2.0 m/s, cloth mu 0.2, an
  equal-mass frictionless ball hit, then cloth friction on the slip
  velocity (7/2 mu g) with v_final = v_after - (2/7) s0. Half-ball hit
  (30 degree cut): sliding cue ball leaves the tangent at 60 degrees
  from its line and stays there, paths 90.00 degrees apart, settles at
  0.7143 m/s (5/7 of 1.0) after 0.146 s and 12.5 cm; rolling cue ball
  bends to 33.67 degrees from its line (closed form (5/7) v_after +
  (2/7) v0 x, 33.670), paths 63.67 degrees apart, settles at 1.1157 m/s
  after 0.252 s and 26 cm; the object ball leaves at 1.732 m/s along
  the 30 degree line and rolls at 1.237 m/s (5/7) after 0.252 s and 37
  cm in both panels. Cuts of 14 and 49 degrees (3/4 and 1/4 ball):
  sliding 90.00 both; rolling 27.11 and 27.05 degrees off the line
  (paths 41.1 and 76.1 apart), Dr Dave's "about 27".
- Coin rotation: equal coins, no slip enforced (contact slip 0):
  exactly 2.0000 turns per lap, upright again halfway; around a coin of
  three times the radius 4.0000; inside a ring of 3 r 2.0000; inside 2 r
  1.0000 (Tusi); along a flat strip of the same length 1.0000.
- Tablecloth: glass on cloth mu 0.2, glass on table mu 0.4, 30 cm of
  cloth beyond the glass, glass 40 cm from the table edge, the cloth
  jumping to a steady speed V. Threshold sqrt(2 mu g L) = 1.085 m/s. V
  0.8: the glass reaches cloth speed at 0.41 s after 16 cm and rides off
  the edge at 0.70 s; V 1.0: rides off at 0.66 s; V 1.2: 18.1 cm; V 1.5:
  8.2 cm; V 2.0: 3.9 cm; V 3.0: the cloth clears in 104 ms, the glass at
  0.203 m/s, 1.05 cm on the cloth plus 0.53 cm on the table, 1.58 cm
  (numeric 1.051 cm on the cloth); V 4.0: 0.86 cm. A cloth accelerating
  at a steady rate instead: below mu g = 1.96 m/s^2 no slip at all; 20
  m/s^2 gives 4.9 cm, 50 m/s^2 1.8 cm.
- Inertia ball: 1 kg between two strings of stiffness 2,000 N/m (1 cm
  stretch at the 20 N break), damping 1 N s/m, the bottom end pulled at
  a steady speed. 0.05 m/s: the top snaps at 217 ms after the ball moves
  5.1 mm, bottom at 11.5 N; 0.2 m/s: top at 51 ms; 0.5 m/s: bottom at 24
  ms, ball 2.1 mm; 1 m/s: bottom at 10.4 ms, ball 0.36 mm, top 10.5 N; 2
  m/s: bottom at 5.05 ms, ball 0.085 mm, top 9.98 N; 5 m/s: 2.0 ms and
  0.014 mm. Threshold about 0.41 m/s (top below, bottom above); it
  depends on the stiffness and break tension chosen.
- Pendulum and peg: 1 m string released from horizontal, RK4 at 10 us,
  the peg d below the pivot, small circle r = L - d. Bottom at 0.592 s
  at 4.429 m/s. d 0.5 L: slack 41.81 degrees above the peg (48.19 short
  of the top; closed form asin(2d / 3r) = 41.81) at 1.808 m/s, flies
  0.55 s to a peak 0.43 m above the peg, the string catches 35 degrees
  from the bottom on the far side and the jerk keeps 10 percent of the
  energy; 0.55 L: slack 35.4 short of the top; 0.59 L: 16.4 short; 0.60
  L: exactly the top with zero tension; 0.61 L: loops, top tension 0.13
  weights; 0.65 L: loops, 0.71 weights, small-circle lap 0.656 s; 0.70
  L: loops at 2.801 m/s over the top (needs 1.715), 1.67 weights, lap
  0.528 s. Threshold exactly 3/5 (5 d = 3 L).
- Head-on crash: 1,000 kg cars with a linear crumple spring 1e6 N/m
  (crush v sqrt(m / k)). Wall at 50 km/h: 43.9 cm, 44.8 g peak, 99 ms;
  wall at 100: 87.8 cm, 89.6 g; two cars at 50 head-on (springs in
  series, RK4): each car crushes 43.9 cm, the contact plane never moves,
  rebound 50 km/h each. A constant-force crumple (400 kN) gives 24.1 and
  96.5 cm (4x), so the 2x is the spring's; the equality with the 50
  wall holds for any crumple law.
- Fridge: 80 kg, 0.7 m wide, 1.8 m tall, mu 0.3, pushed with 1.05 mu m
  g = 247 N. Tip threshold h* = m g w / (2 F) = 1.111 m (w / (2 mu) =
  1.167 m at the limit push); no-return angle atan(w / H) = 21.25
  degrees. Push at 0.9 or 1.1 m: slides at 0.147 m/s^2, 7.4 cm in 1 s,
  29 cm in 2 s; at 1.2 m: past the no-return angle at 1.16 s, flat at
  1.65 s; at 1.4 m: no return at 0.81 s, flat at 1.27 s (rotation about
  the front bottom edge, I = m (w^2 + H^2) / 3).
- Rod on ice versus pinned foot: 1 m rod from 80 degrees above the
  floor. Ice (the centre of mass falls straight down, theta'^2 = 12 g
  (sin 80 - sin theta) / (L (1 + 3 cos^2 theta))): flat at 0.517 s, the
  tip lands 0.50 m from its start line; pinned (theta'' = -(3 g / 2 L)
  cos theta): flat at 0.768 s, tip 1.00 m out; both hit at 5.383 rad/s.
  Ratio 1.487.
- Yo-yo: 3 cm disc on a 0.5 cm axle, a = g / 19 = 0.516 m/s^2; 1 m in
  1.969 s against 0.452 s for a dropped ball (4.36x); the string holds
  0.947 of the weight; bottom speed 1.016 m/s at 203 rad/s; up and back
  every 3.937 s with no loss.
- Bicycle endo (rejected): centre of mass 1.1 m up and 0.55 m behind
  the front contact, threshold 0.500 g; at 0.4 g from 5 m/s it stops in
  3.19 m; at 0.6 and 0.8 g the crude pseudo-force model pitches the
  rider over the front contact at 0.91 and 0.60 s, but the result hangs
  on the rider's posture and speed.
- Up and down a 30 degree slope at 3 m/s (rejected): rolling ball up
  0.857 s and down 0.857 s; sliding block mu 0.2 up 0.454 s over 0.68 m,
  down 0.652 s (1.435x = sqrt(6.60 / 3.21)), back at 2.09 m/s.
- Ice cube versus rolling ball, 2 m at 20 degrees (rejected): 1.092
  against 1.292 s, sqrt(7/5); a block with mu 0.104 ties the ball.

## Candidates

Numbers are expectations to check; the sim measures the claim.

1. Cut shot (cutshot). Two cue balls at 2.0 m/s hitting a still ball
   half-ball (30 degree cut), one sliding with no spin and one rolling.
   Hook: "Cut the ball. Do the two paths make a right angle?" Setup: a
   half-ball hit at 2 m/s; payoff: sliding, exactly 90 degrees; rolling,
   64 degrees, the cue ball bending to 34 degrees off its line. Check:
   v_final = (5/7) v_after + (2/7) v0 along the original line; the 90
   from equal masses. Renderable: the cue ball follow code (sims/cueball)
   with a lateral hit, the curved slip path drawn, under 25 minutes;
   repeat the shot. Pillar: physics (collisions). Accepted first: the
   sibling of cue ball follow (957 views), a real pool aiming debate
   (the 90 degree rule against the 30 degree rule), an exact angle, the
   panels end on different lines.
2. Coin rotation (coinroll). A coin rolled around an identical coin
   beside the same coin rolled along a flat strip as long as the other
   coin's rim. Hook: "Roll a coin around a coin. How many times does it
   turn?" Setup: two coins the same size; payoff: 2 turns, not 1, while
   the strip gives exactly 1. Check: R / r + 1 outside, exact; the 1982
   SAT keyed a 3:1 version as 3 and it is 4. Renderable: two circles, a
   marked point, no-slip kinematics, under 20 minutes; one lap is
   exactly periodic so the short loops. Pillar: algorithms and math in
   motion. Accepted: a viral exact-integer paradox, continuous rolling
   motion (not a drawing), the cheapest build of the run. Caveat: name
   the frame (turns as seen from the table).
3. Tablecloth (tablecloth). A glass 30 cm from the far edge of a cloth,
   the cloth pulled at 1.0 m/s beside 3.0 m/s. Hook: "Pull the
   tablecloth. How fast do you need to pull?" Setup: 30 cm of cloth
   under the glass; payoff: faster than 1.1 m/s; at 3 m/s the glass
   moves 1.6 cm, at 1 m/s it rides the cloth off the table. Check:
   sqrt(2 mu g L) and two quadratics. Renderable: piecewise closed
   forms, under 20 minutes; repeat the pull. Pillar: physics (friction,
   inertia). Accepted: an everyday trick everybody has argued about, a
   threshold like the bucket (920), panels end differently (stays
   against off the table). Caveat: state the friction numbers and that
   the cloth jumps to a steady speed.
4. Inertia ball (twostrings). A 1 kg ball hung by a string with a
   second string below, the lower end pulled at 5 cm/s beside jerked at
   2 m/s. Hook: "Pull the bottom string. Which one snaps?" Setup: the
   strings snap at 20 N, twice the weight; payoff: pulled slowly the
   top snaps after 0.2 s; jerked, the bottom snaps in 5 ms with the ball
   moved 0.09 mm. Check: x'' + (2k/m) x = (k V / m) t, tensions k x + m
   g and k (V t - x). Renderable: one ODE, two strings drawn with the
   stretch exaggerated, a snap event, under 25 minutes; repeat. Pillar:
   physics (inertia). Accepted: the PIRA 1F20.10 prediction demo with a
   majority wrong answer, panels end differently (ball drops against
   ball stays). Caveat: the 0.41 m/s threshold depends on the stiffness
   and break tension chosen, so narrate the two outcomes, not the
   threshold.
5. Pendulum and peg (pegswing). A 1 m pendulum released from horizontal
   with a peg halfway down the string beside a peg 70 percent down.
   Hook: "The string hits a peg. Does the ball loop around it?" Setup:
   a peg at half the string; payoff: no, the string goes slack 48
   degrees short of the top and the ball falls; at 70 percent it loops
   at 2.8 m/s over the top; the peg must be 3/5 of the way down. Check:
   5 d = 3 L from energy and zero tension at the top; slack angle asin(2
   d / 3 r). Renderable: RK4 on two circles, a slack event with a
   parabola and a catch, under 30 minutes; the looping panel is
   periodic. Pillar: physics (energy). Accepted mid: the loop-the-loop
   family (967), a standard demo, an exact fraction. Caveat: the 48
   degrees is the loop-the-loop number again, so lead with 3/5.
6. Head-on crash (headon). Two cars at 50 km/h head-on beside one car
   into a wall at 50 and one at 100, crumple as a spring. Hook: "Two
   cars at 50 head-on. Is that like a wall at 100?" Setup: 50 km/h each;
   payoff: no, each car crushes 44 cm, the same as the wall at 50; the
   wall at 100 crushes 88 cm. Check: crush v sqrt(m / k); the contact
   plane never moves. Renderable: 1D springs, RK4, under 20 minutes;
   repeat the crash. Pillar: physics (momentum, energy). Accepted mid:
   a live debate MythBusters settled, three panels with a clear odd one
   out. Caveat: the 2x is the spring's; a constant-force crumple gives
   4x, so say "a car that crumples like a spring"; not tabletop.
7. Fridge tip (fridge). An 80 kg fridge 0.7 m wide pushed just hard
   enough to move it, at 0.9 m up beside 1.4 m up. Hook: "Push the
   fridge high or low. Does it slide or tip?" Setup: a push at 0.9
   against 1.4 m; payoff: below 1.1 m it slides, above it tips, past the
   point of no return in 0.8 s. Check: h* = m g w / (2 F), w / (2 mu)
   at the limit push; no-return angle atan(w / H). Renderable: slide
   phase plus rotation about the front bottom edge, under 25 minutes;
   repeat the push. Pillar: physics (torque). Accepted mid: a household
   question with a clean threshold, the panels end differently (slides
   against falls over). Caveat: the slide at a 5 percent overpush is
   slow (7 cm in 1 s), so tune the push.
8. Rod on ice (icestick). A 1 m rod standing 10 degrees off vertical on
   ice beside the same rod with its foot pinned. Hook: "A pencil tips
   over on ice. Does it fall faster?" Setup: 10 degrees off vertical;
   payoff: yes, flat at 0.52 s against 0.77 s, and its tip lands half
   as far out. Check: theta'^2 = 12 g (sin 80 - sin theta) / (L (1 + 3
   cos^2 theta)) against 3 g (sin 80 - sin theta) / L. Renderable: two
   ODEs, under 20 minutes; repeat. Pillar: physics (rigid body).
   Accepted low: cheap and exact, the hinged-stick family (734), but the
   surprise is mild and both panels end flat.
9. Yo-yo drop (yoyo). A yo-yo dropped on its string beside a ball dropped
   from the same 1 m. Hook: "Drop a yo-yo and a ball. Which lands
   first?" Setup: 1 m; payoff: the ball at 0.45 s, the yo-yo at 1.97 s,
   4.4 times slower, then it climbs back to the hand. Check: a = g / (1
   + k R^2 / r^2). Renderable: closed form, a spinning disc, under 20
   minutes; periodic so it loops. Pillar: physics (rotation). Accepted
   lowest: exact and cheap, a charming loop, but the Atwood family was
   ranked low as mild.

Rejected: bicycle endo (the lift threshold is exact but what happens
next depends on the rider's posture and speed; the fridge carries the
tip-or-slide story); up and down a slope (a homework result, the 1.43x
set by the friction number chosen); ice cube against rolling ball (the
rolling race again, 18 percent); buttered toast (edge friction and
overhang contested, a 40-minute build); capstan rope (the holding panel
does not move); Tusi couple (the payoff is a shape, not a number);
monkey and weight over a pulley (a tie); wagon-wheel effect (a 30 fps
render aliases the "true" panel too); the pegs (JUICE flyby, Saturn
opposition, Nobel physics, Orionids: space or no motion; World Series:
the bat sweet spot already in the backlog; Halloween: no closed-form
tabletop motion); the sim channels and "Debunking Terrible Physics"
(no new subject).

## Ranking

For today's three slots, one producer each, about 25 minutes with RK4 or
closed forms:

1. Cut shot (sliding cue ball: paths 90 degrees apart; rolling: 64,
   the cue ball bending to 34 degrees off its line).
2. Coin rotation (2 turns around an identical coin, 1 along a strip of
   the same length; exactly periodic).
3. Tablecloth (faster than 1.1 m/s; 1.6 cm at 3 m/s, off the table at
   1 m/s).
4. Inertia ball (slow: the top snaps after 0.2 s; jerk: the bottom in
   5 ms).
5. Pendulum and peg (the peg must be 3/5 down; at half, slack 48
   degrees short of the top).

Then head-on crash, fridge tip, rod on ice, yo-yo drop.

## Outcome

Nine ideas appended to `docs/niche.md` under "Added by trend research
2026-09-27 (evidence in task 20260927-102520; ...)". One line appended to
`web/data/log.jsonl`. The backlog count in the last entry of
`web/data/slate.json` changed from fifteen to twenty-four. No status
update, no production, no commit in this run by instruction. Existing
backlog entries were not changed.

## Files changed

- tasks/20260927-102520/TASK.md (this file)
- docs/niche.md (nine backlog bullets appended)
- web/data/log.jsonl (one line appended)
- web/data/slate.json (last entry title: twenty-four unproduced ideas)
