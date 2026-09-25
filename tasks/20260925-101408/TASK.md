# Research trends: rolling, spin and drop debates, run 7

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: backlog

## Goal

Seventh research-trends run, 2026-09-25 from about 10:05 EEST, for the
three slots of day 27. The backlog in `docs/niche.md` holds twelve
unproduced ideas, none of them a strong first pick: seven are space
time-lapses or counters (Kelvin wake, Collatz, secretary, rogue wave,
Saturn retrograde, Halley, L2 drift), run 6 ranked corner reflector,
basketball arc and Moon clock low, bathtub drain is a tie payoff and dam
break is a heavy build. Find 6 to 9 new candidates that fit the winning
format: continuous tabletop motion, two panels on the same input that
end differently, one plain question in the first two seconds, one setup
number, one payoff number, a closed-form check, a loop or a repeat, and a
build of about 25 minutes with RK4 or closed forms (no PDE, no fluid
grid, no ray tracing). Measure every survivor with a throwaway script
before recording it. No production in this run. By instruction
`web/data/status.json`, sims/, projects/, media/ and secrets/ were not
touched and no commit was made; `web/data/slate.json` only had its
backlog count updated.

## Channel evidence used for the filter

Views at run time (`web/data/slate.json`, refreshed 2026-09-24 10:56):
the shorts the feed picked up sit near 900 to 1,050 and share one
format: coupled pendulums 1,047, braking distance 1,012, pi blocks 991,
big swing 990, turntable ball 973, loop the loop 965, monkey and hunter
963, cradle 958, rolling race 950, tsunami 940, hoop bead 925, water
wheel 922. Formats at 5 to 99: space time-lapses (orbit 6, gravity train
74, gravity assist 33), counters and random-draw statistics (birthday 5,
sticker album 36, buses 47), drawings (rainbow 79, Mach cone 79) and tie
payoffs (bullet drop 85). Pendulum and ball pieces are the strongest
genres; path races and collisions with an exact ratio carry. Days 25 and
26 (spring swap 44, Zeno 138, racing balls 95, ballistic 1, superball 0,
merry-go-round 0) are too new to judge. The filter therefore favoured
tabletop motion with a "which way" or "which first" debate, two panels
that end differently, an exact fraction or angle, and cheap builds; it
rejected space, counters, drawings, tie payoffs and contested constants.

## Queries (10 WebSearch, 9 WebFetch of which 3 failed)

1. "viral physics demonstration shorts September 2026 counterintuitive
   tabletop experiment debate". Showed the "Debunking Terrible Physics"
   early-September 2026 session (bad TikTok physics broken down, so the
   debate format is live), the fluxnote list (unchanged since run 5),
   "Counter-Intuitive Physics" and "science tricks" shorts, and two
   phys.org items (a tabletop fundamental-physics test, June 2026; light
   swimming upstream in a quantum fluid, September 2026: not motion sims).
   No single demo dominates this month.
   https://www.youtube.com/watch?v=kjN6hqTU_W4
   https://fluxnote.io/guides/science-youtube-shorts-ideas
   https://phys.org/news/2026-09-upstream-quantum-fluid-violating-newton.html
2. "physics simulation animation channel new video September 2026
   pendulum collision rolling ball". Showed the Simulated Physics and
   Physics Simulations channels, myPhysicsLab, physics-simulations.org
   (double pendulum) and the BU HTML5 list; the sim channels still post
   satisfying sims with no measured claim, so the gap stands. Nothing new
   this month worth a peg.
   https://www.youtube.com/channel/UCi0_J1sxClKRC5ppdnWbE2w
   https://myphysicslab.com/
   http://physics.bu.edu/~duffy/HTML5/index.html
3. "spool yo-yo pulled by string which way does it roll physics demo
   critical angle". Showed SMU (fetched below), NSTA "The Pulled Spool:
   Which Way Does It Roll?" (2020), Harvard's yo-yo demo, the OAPT
   "Mystery of a Pulled Spool", UW "Walking the Spool", Mungan's TPT 57
   "Pulling a Spool" and Purdue 1J-13: a standard prediction demo with a
   majority wrong answer, three outcomes (toward, away, slide), and the
   critical angle set by the axle-to-wheel ratio. Run 6 had already seen
   the two-part spool demo among trending shorts.
   https://demos.smu.ca/demos/mechanics/124-torque-on-a-spool
   https://www.nsta.org/science-teacher/science-teacher-aprilmay-2020/pulled-spool-which-way-does-it-roll
   https://www.usna.edu/Users/physics/mungan/_files/documents/Publications/TPT57.pdf
4. "folded falling chain free end falls faster than gravity
   demonstration". Showed the 2022 ScienceDirect paper (10,000 fps
   imaging: the free tip of a U-folded chain accelerates faster than g,
   then whips), the arXiv "two falling-chain demonstrations" note (the
   falling time is 85 percent of free fall), Hamm's "weight of a falling
   chain", Harvard's "Falling Faster than g" demo and Inspiring Science.
   A viral demo with a closed form and a race format.
   https://www.sciencedirect.com/science/article/pii/S002074622200227X
   https://arxiv.org/html/physics/0609219v1
   https://sciencedemonstrations.fas.harvard.edu/presentations/falling-faster-g
5. "cue ball follow shot stun shot physics rolling cue ball after
   head-on collision 2/7 speed". Showed Wikipedia cue-sports techniques
   (follow: the cue ball resumes rolling forward after a dead-on hit;
   stun: it stops), Dr Dave's cue-ball control pages, Bullseye Billiards
   and Masi Carbon: stop, stun and follow are the everyday pool debate,
   but none of the pages gives the exact fraction; the sim supplies it.
   https://en.wikipedia.org/wiki/Cue_sports_techniques
   https://drdavepoolinfo.com/faq/cue-ball-control/speed/
   https://bullseyebilliards.com/blogs/articles/19575939-billiard-physics-ball-ball-contact
6. "bucket of water swung over head why does water stay in minimum
   speed physics". Showed two Physics Forums threads, UCSB 16.15 (fetched
   below), UW Wonders of Physics, Williams College, MyTutor and
   LibreTexts: the condition v^2 / r >= g, one worked example (0.8 m
   radius, period under 1.80 s); the "why does it stay in" question is
   still asked and answered in words, not with a threshold on screen.
   https://web.physics.ucsb.edu/~lecturedemonstrations/Composer/Pages/16.15.html
   https://wonders.physics.wisc.edu/water-pail/
   https://www.physicsforums.com/threads/vertical-circular-motion-question-why-does-the-water-stay-in-the-bucket.121314/
7. "baseball bat sweet spot center of percussion physics handle sting
   World Series 2026". Showed Rod Cross's baseball pages and "sweet spot
   of a baseball bat", Russell's bat pages, Wikipedia (fetched below),
   Harvard and Iowa demos and two patents: the centre of percussion of a
   uniform rod is two thirds from the pivot; the felt sweet spot of a
   real bat is set mostly by bending nodes and the grip, about 17 cm
   from the barrel end. A peg for late October; the claim must say
   "stiff stick".
   https://www.physics.usyd.edu.au/~cross/baseball.html
   https://baseball.physics.illinois.edu/CrossSweetSpotBat.pdf
   https://www.acs.psu.edu/drussell/bats/bend-sweet.html
8. "bicycle pedal paradox pull bottom pedal backward which way does the
   bike move". Showed the Wolfram demonstration, the Simons Foundation
   video page (fetched below), Hackaday, Quora threads and Amherst's Q&A:
   pulling the bottom pedal backward moves the bike backward and the
   pedal toward 5 o'clock; the flip needs the pedal radius times the
   gear ratio to exceed the wheel radius. Same mechanism as the spool.
   https://www.simonsfoundation.org/2014/03/20/mathematical-impressions-the-bicycle-pulling-puzzle/
   https://physicsqanda.sites.amherst.edu/Trikeans.htm
9. "askphysics everyday physics questions 2026 why does it spin bounce
   swing simple explanation". Showed TeachEngineering on swings,
   Wikipedia's bouncing ball, a swing-physics forum, the arXiv spinning
   top note and Princeton's "In Praise of Simple Physics": the audience
   questions are still swings, bounces and spinning tops; the pumping
   swing sat at 11 views, so no new swing idea.
   https://www.teachengineering.org/lessons/cub_pend_lesson01
   https://ar5iv.labs.arxiv.org/html/physics/0602078
10. "autumn physics falling leaf tumbling maple seed conker Halloween
    science October 2026 events". Showed the Science (AAAS) piece on
    fluttering leaves getting lift, Science Sparks and Science Buddies
    autumn lists (conkers, helicopter seeds, leaf colour): the leaf and
    samara motions need a fitted aerodynamic model, and conkers are the
    ballistic pendulum again (published 2026-09-24). No autumn or
    Halloween peg with a closed-form tabletop motion; Nobel physics
    (2026-10-06), Saturn opposition (2026-10-04) and the Orionids
    (2026-10-21) stay space or no-motion pegs as in run 6.
    https://www.science.org/content/article/how-autumn-leaves-get-lift
    https://www.sciencebuddies.org/blog/fall-science-activities

## Sources (fetched pages)

- https://demos.smu.ca/demos/mechanics/124-torque-on-a-spool : rope
  wrapped under the axle, pulled at several angles; critical angle
  asin(r1 / r2) measured from the vertical (the same as acos(r / R) from
  the table); shallower pulls roll toward the puller, steeper pulls roll
  away, at the critical angle it slides; no numbers, the gap the sim
  fills.
- https://web.physics.ucsb.edu/~lecturedemonstrations/Composer/Pages/16.15.html
  : half a litre in a bucket swung in a vertical circle of about 0.9 m;
  the water stays while v^2 / r >= g, about 3 m/s at the top; below that
  it falls out.
- https://en.wikipedia.org/wiki/Center_of_percussion : the point where a
  perpendicular impact gives no reactive shock at the pivot; for a
  uniform rod pivoted at one end it is 2/3 of the length from the pivot
  (b = L / 6 beyond the centre); the felt sweet spot of a bat is set by
  the vibration nodes, not the centre of percussion, since bats are not
  rigid.
- https://www.simonsfoundation.org/2014/03/20/mathematical-impressions-the-bicycle-pulling-puzzle/
  : "pull straight back on the lower pedal: forward or backward?", a
  classic puzzle (Gardner, Mathematics Magazine 1972) with the full
  answer in the video only.
- https://www.scientificamerican.com/article/physicists-explain-gravity-defying-chain-trick/
  : turned out to be the chain fountain (Biggins: the pot kicks the
  chain up; isolated beads make no fountain; chains landing on a table
  fall faster than in free space), not the folded chain; kept as
  evidence that chain tricks travel.
- https://drdavepoolinfo.com/faq/cue-ball-control/speed/ : only the
  90-degree and 30-degree path rules and how speed changes the path; no
  speed fraction, so the 2/7 comes from the sim and its closed form.
- https://www.usna.edu/Users/physics/mungan/_files/documents/Publications/TPT57.pdf
  : PDF returned as binary, unreadable.
- https://sciencedemonstrations.fas.harvard.edu/presentations/falling-faster-g
  and https://sciencedemonstrations.fas.harvard.edu/presentations/center-percussion
  : HTTP 403.

## Measurements (python under nix, run 2026-09-25, /tmp/rt7/measure.py)

- Falling folded chain (Calkin and March: v^2 = g x (2L - x) / (L - x)
  for the free tip): L 1 m, the tip lands at 0.3826 s against the ball's
  0.4516 s (ratio 0.8472, lead 69 ms; the literature says 85 percent);
  the ball has fallen 0.718 m when the tip lands, 28 cm still to go; at
  half depth the tip is at 3.83 m/s against the ball's 3.13 at the same
  depth; at 0.9 L 9.85 against 4.20 m/s. RK4 on a = g (1 + x (2L - x) /
  (2 (L - x)^2)) at 2 us steps reaches 0.9 L at 0.3759 s and 9.853 m/s,
  the closed form 9.853. Times scale with sqrt(L): 0.5 m 0.271 against
  0.319 s, 2 m 0.541 against 0.639 s.
- Pulled spool: R 3 cm, r 1.5 cm, m 0.1 kg, I 0.6 m R^2, F 0.2 N, no
  slip, a = F (R cos theta - r) / ((k + 1) m R) toward the hand.
  Critical 60.00 degrees (cos = r / R). 0 deg +0.625 m/s^2 (31 cm in 1
  s), 30 deg +0.458 (22.9 cm toward), 45 deg +0.259 (12.9 cm), 59 deg
  +0.019, 61 deg -0.019, 70 deg -0.198 (9.9 cm away), 80 deg -0.408
  (20.4 cm away), 90 deg -0.625 (31 cm away). Friction needed at most
  0.145 of the normal force, so mu 0.3 holds everywhere.
- Cue ball follow: 57.15 mm balls, 2.0 m/s at impact, cloth mu 0.2. A
  sliding spinless cue ball stops dead; a rolling cue ball keeps its
  70.0 rad/s spin with zero translation, and friction pulls it forward to
  exactly 2/7 of its speed, 0.5714 m/s, after 0.291 s and 8.3 cm (numeric
  0.5714 at 0.291 s and 0.0832 m); the struck ball leaves at 2.0 m/s
  sliding and settles rolling at 5/7, 1.4286 m/s, after 0.291 s and 50
  cm in both panels. The following cue ball keeps 8.2 percent of its
  kinetic energy. Mu sets only the settling distance.
- Bucket on a 1 m arm at constant rpm, pivot 1.6 m up, water as free
  parcels once the bucket stops pushing: minimum 3.132 rad/s, 29.90 rpm,
  one turn every 2.006 s. 36 rpm stays, the water pressing on the bucket
  with 0.45 g at the top; 30 rpm stays with 0.01 g; 24 rpm spills, the
  water leaving 49.9 degrees before the top (40.1 above horizontal) at
  2.51 m/s and landing 0.69 m past the pivot line 0.90 s later.
- Centre of percussion: free uniform rod 0.85 m, 0.9 kg, 145 g ball at
  30 m/s. Handle-end speed (J / m)(1 - 6 d / L), zero at d = L / 6, i.e.
  56.7 cm from the handle end (two thirds). Restitution 0.5: sweet spot
  J 5.37 N s, centre 5.97 m/s, 14.0 rad/s, handle end 0.00 m/s; tip hit
  J 3.97 N s, centre 4.41 m/s, 31.1 rad/s, handle end -8.82 m/s (kicks
  back at twice the centre speed); middle hit handle +6.24 m/s.
  Restitution 1: handle end 0.00 and -11.76 m/s.
- Balance: uniform stick on a fingertip released at rest 1 degree off
  vertical, theta'' = 3 g sin theta / 2L, RK4. 1.2 m: 45 degrees at
  1.289 s, flat at 1.498 s. 0.15 m: 0.456 and 0.530 s. 1.0 m: 1.177 and
  1.368 s. 0.10 m: 0.372 and 0.433 s. Ratios exactly sqrt(8) = 2.828 and
  sqrt(10) = 3.162.
- Weight on a spring: 1 kg, static sag 5 cm (k 196.1 N/m). Lowered
  gently 5.00 cm; released from the rest height 10.00 cm (RK4 10.0000),
  period 0.449 s; dropped from 5, 10, 20 cm above: 13.66, 16.18, 20.00 cm
  (x = d (1 + sqrt(1 + 2 h / d))).
- Tarzan: rope 6 m, start 60 degrees, water 3 m below the low point,
  v^2 = 2 g L (cos theta - cos 60) then a parabola. Release at the bottom
  6.00 m; best release 30.9 degrees past the bottom 10.26 m; 45 degrees
  9.14 m; hanging on to the far top 5.20 m.
- Atwood: 1.1 kg against 1.0 kg, a = g / 21 = 0.467 m/s^2; 1 m takes
  2.069 s against 0.452 s in free fall (4.58x); a naive g / 11 would give
  1.498 s.

## Candidates

Numbers are expectations to check; the sim measures the claim.

1. Pulled spool. A spool with a 3 cm wheel and a 1.5 cm axle, the string
   off the bottom of the axle pulled with 0.2 N at 30 degrees beside 80
   degrees. Hook: "Pull the string. Which way does the spool roll?"
   Setup: the axle is half the wheel; payoff: toward you below 60
   degrees, away above it, 22.9 cm toward against 20.4 cm away in one
   second. Check: cos theta = r / R, a = F (R cos theta - r) / ((k + 1)
   m R). Renderable: one ODE, string tangent to the axle, under 25
   minutes; repeat the pull. Pillar: physics (rolling). Accepted first:
   a prediction demo with a majority wrong answer, seen trending in run
   6, rolling family (rolling race 950, turntable 973), the panels end
   in opposite directions.
2. Cue ball follow. Two cue balls at 2.0 m/s into a still ball head-on,
   one sliding with no spin, one rolling. Hook: "Hit the ball dead on.
   Does the cue ball stop?" Setup 2.0 m/s; payoff: sliding stops dead,
   rolling creeps on at exactly 2/7, 0.57 m/s. Check: 2/7 and 5/7 from
   the rolling condition; mu only sets the 8 cm settling distance.
   Renderable: closed forms plus a friction phase, a stripe on the ball
   to show the spin, under 25 minutes; repeat the shot. Pillar: physics
   (collisions). Accepted: an everyday pool debate (stop, stun, follow),
   an exact fraction, collision family (cradle 958, pi blocks 991).
3. Bucket over the head. A bucket of water on a 1 m arm at a steady 36
   rpm beside 24 rpm, the water as parcels that fly free when the bucket
   stops pushing. Hook: "Swing a bucket over your head. How slow before
   it spills?" Setup: a 1 m arm; payoff: 30 turns a minute, one every
   2.0 s; at 24 rpm the water leaves 50 degrees before the top. Check:
   omega = sqrt(g / r). Renderable: kinematics plus free flight, under
   25 minutes; the fast panel is periodic and loops. Pillar: physics
   (rotation). Accepted: the loop-the-loop and hoop-bead family (965,
   925), a plain question everyone has asked, the panels end differently
   (stays against spills). Caveat: constant rpm is a motor, not an arm;
   say so.
4. Falling folded chain. A 1 m chain folded in half, one end held, the
   free end let go beside a ball dropped from the same height. Hook:
   "Can anything fall faster than a dropped ball?" Setup 1 m; payoff:
   the chain tip lands at 0.38 s, the ball at 0.45 s, still 28 cm up.
   Check: v^2 = g x (2L - x) / (L - x). Renderable: 1D ODE, a folded
   line whose fold moves at half the tip speed, under 25 minutes; repeat
   the drop. Pillar: physics (energy). Accepted: a viral "faster than g"
   demo with a race format (slinky drop 774, hinged stick 731). Caveat:
   the tip speed runs away in the last centimetres, so cap the drawing
   at the fold and say the real chain whips.
5. Tarzan release. A rider on a 6 m rope from 60 degrees, the water 3 m
   below the low point, one letting go at the bottom beside one letting
   go 31 degrees past it. Hook: "Swing on a rope. When do you let go?"
   Setup: a 6 m rope from 60 degrees; payoff: 10.3 m at 31 degrees past
   the bottom against 6.0 m at the bottom. Check: v^2 = 2 g L (cos theta
   - cos 60) then a parabola; scan of the release angle. Renderable:
   RK4 pendulum plus closed-form flight, under 25 minutes; the swing
   repeats so it loops. Pillar: physics (pendulum, projectile).
   Accepted: pendulum plus projectile (monkey and hunter 963, big swing
   990), a big contrast, a plain choice. Caveat: the "best angle" is a
   scan, so name the two angles shown, not an optimum claim.
6. Balance a broom. A 1.2 m stick beside a 15 cm pencil on a fingertip,
   both let go 1 degree off vertical. Hook: "Which is easier to balance:
   a pencil or a broom?" Setup 1 degree; payoff: the broom takes 1.50 s
   to fall flat, the pencil 0.53 s, 2.83 times longer, exactly sqrt(8).
   Check: t scales with sqrt(L). Renderable: two ODEs, under 20 minutes;
   repeat the release. Pillar: physics (inverted pendulum). Accepted
   mid: cheap and exact, but the answer is half known (Kapitza 830,
   hinged stick 731).
7. Bat sweet spot (peg: World Series, late October 2026). A free 85 cm
   stiff stick struck by a 145 g ball at 30 m/s, 57 cm from the handle
   beside a hit at the tip. Hook: "Where do you hit the ball so the
   handle does not kick?" Setup: an 85 cm stick; payoff: 57 cm up, two
   thirds, the handle end does not move; a tip hit kicks it back at 8.8
   m/s. Check: (J / m)(1 - 6 d / L). Renderable: rigid impulse, under 25
   minutes; repeat the hit. Pillar: physics (rigid body). Accepted mid:
   exact and cheap; the real bat's sweet spot is set by bending nodes,
   so the claim must say "stiff stick", and a zero payoff on one panel
   is close to a tie.
8. Weight on a spring. A 1 kg weight lowered gently onto a spring that
   sags 5 cm, beside the same weight let go from the rest height. Hook:
   "Set it down or let it go. How far does the spring squash?" Setup 5
   cm; payoff: 10 cm, exactly double, bouncing for ever every 0.449 s.
   Check: m g x = k x^2 / 2. Renderable: one ODE, under 20 minutes;
   periodic so it loops. Pillar: physics (oscillators). Accepted mid:
   exact and cheap; the spring family is young (spring swap 44).
9. Atwood drop. A 1.1 kg weight dropped beside the same weight on a
   string over a pulley against 1.0 kg. Hook: "Hang 1.1 kg against 1.0
   kg. How fast does the heavy one fall?" Setup 1.1 against 1.0; payoff:
   g / 21, 2.07 s for 1 m against 0.45 s. Check: a = g (m1 - m2) / (m1
   + m2). Renderable: closed form, under 15 minutes; repeat the drop.
   Pillar: physics (dynamics). Accepted lowest: exact and cheap, mild
   surprise.

Rejected: bicycle pedal paradox (the same rolling-constraint mechanism
as the spool; the flip needs a cog more than twice the chainring, so
the second panel is contrived, and the drawing is a build risk); capsize
of a tall against a wide box (polygon clipping of the submerged area,
over 25 minutes); moving-paddle bounce 2u + v (mild, the gravity-assist
family at 33); spinning raw against boiled egg (the shell-to-yolk
coupling is a contested constant); helium balloon in a braking car (the
angles tie, only the sign differs); throw from a cliff at 30 against 45
degrees (a 5 percent range difference, mild); Foucault pendulum (a
day-long time-lapse); tuned mass damper (contested damping); tumbling
leaf and maple samara (fitted aerodynamic models, no closed form);
ball leaving a dome at 48 degrees (the loop-the-loop number again);
Nobel, Saturn opposition and Orionid pegs (space or no tabletop motion);
the phys.org quantum-fluid item (no motion sim).

## Ranking

For today's three slots, one producer each, about 25 minutes with RK4 or
closed forms:

1. Pulled spool (toward below 60 degrees, away above; 22.9 cm toward at
   30 degrees against 20.4 cm away at 80; a trending prediction demo).
2. Cue ball follow (the sliding cue ball stops, the rolling one creeps on
   at exactly 2/7, 0.57 m/s from 2.0).
3. Bucket over the head (30 turns a minute keeps the water in; at 24 rpm
   it leaves 50 degrees before the top).
4. Falling folded chain (tip 0.38 s against ball 0.45 s over 1 m).
5. Tarzan release (10.3 m at 31 degrees past the bottom against 6.0 m).

Then balance a broom, bat sweet spot, weight on a spring, Atwood drop.

## Outcome

Nine ideas appended to `docs/niche.md` under "Added by trend research
2026-09-25 (evidence in task 20260925-101408; ...)". One line appended
to `web/data/log.jsonl`. The backlog count in the last entry of
`web/data/slate.json` changed from twelve to twenty-one. No status
update, no production, no commit in this run by instruction. Existing
backlog entries were not changed.

## Files changed

- tasks/20260925-101408/TASK.md (this file)
- docs/niche.md (nine backlog bullets appended)
- web/data/log.jsonl (one line appended)
- web/data/slate.json (last entry title: twenty-one unproduced ideas)
