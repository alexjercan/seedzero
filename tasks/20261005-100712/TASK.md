# Research trends: run 12 for the day 37 third slot and the backlog

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: backlog

## Goal

Twelfth research-trends run, 2026-10-05 from about 10:20 EEST, for the
third slot of day 37 and the backlog. The backlog in `docs/niche.md`
holds nineteen unproduced ideas; the day 37 orchestrator took the block
on a wedge (fixed or free) and the spinning glass (4 cm or 6 cm) for
slots one and two and judged the rest weak for a first pick: space
time-lapses and counters (Kelvin wake, Collatz, secretary problem, rogue
wave, Saturn retrograde, Halley, L2 drift), low-ranked ideas (corner
reflector, basketball arc, Moon clock, sliding ladder, falling chimney,
two springs stacked or side by side, stick or string), a tie payoff
(bathtub drain), a heavy build (dam break) and a model problem (fridge
tip). Find 6 to 9 new candidates that fit the winning format:
continuous tabletop or everyday motion, two panels on the same input
that end visibly differently on a phone screen, one plain question in
the first two seconds, one setup number, one payoff number, a
closed-form check, a loop or a repeat, and a build of about 25 minutes
with RK4, event-driven steps or closed forms (no PDE, no fluid grid, no
ray tracing, no fitted aerodynamics, no rider or posture models, no
chosen material strengths). Avoid siblings of produced shorts (read the
[produced ...] notes in docs/niche.md: drops beside a ball, Atwood,
yo-yo, chain off a desk, capstan, coin on a record, river crossing,
kerb hop, carried pendulum, balloon in a car, belt, broom, bat, strings,
spool, cue ball, tablecloth, brake or swerve, ice cube against ball,
bucket, swing, spring drop, hoop bead, gyro top, Kapitza, resonance,
metronomes). Measure every survivor with a throwaway script in
/tmp/day37/research/ (g = 9.807) and check the model (contact forces
positive, no-slip friction available with the minimum mu stated, energy
kept where it should be, panels visibly different at 1080x1920). Rank the
survivors and name the best one for today's third slot with its numbers,
its question, its setup and payoff numbers and a drawing sketch in the
style of the day 37 briefs (/tmp/day37/brief-wedge.md). No production in
this run.

Rules for this run: follow the research-trends skill (five to ten
focused queries, WebSearch and WebFetch). Append the survivors to
docs/niche.md at the very end of the file under a new paragraph "Added by
trend research 2026-10-05 (evidence in task 20261005-100712; selection
favoured ...)" in the existing one-line bullet format; re-read the file
right before editing and append only (two producers edit their own
bullets in the same file at the same time). Record the evidence in this
task file (queries, URLs, what each showed, why each idea was accepted or
rejected, the measurement logs) under "## Evidence". Do not edit
web/data/ (the orchestrator appends the journal entry from your report),
do not run git, do not produce anything, do not spawn subagents, never
use sleep in Bash. Finish by reporting: the ranked survivors with their
numbers, the recommended third-slot idea with a full brief paragraph, the
docs/niche.md lines you added, and a one-paragraph journal line for
web/data/log.jsonl.

## Evidence

Research ran 2026-10-05 about 10:20 to 10:50 EEST. Throwaway scripts
and logs in /tmp/day37/research/ (one per candidate, g 9.807, python3
via nix develop). No production, no git, no web/data change in this
run.

### Queries (10 WebSearch, 5 WebFetch of which 2 returned 403)

1. "ballistic cart on incline ball fired perpendicular lands back in
   cart demonstration". Showed the PASCO ME-9486 manual, the Notre
   Dame demo page (ballistic cart incline: the ball fired square to
   the track from a cart rolling down an incline still lands in the
   cart), a 1995 Physics Teacher note "The Ballistic Cart on an
   Incline Revisited", a MasteringPhysics video tutor "Ball Fired from
   Cart on Incline" and the ASU and UMass howitzer-on-incline demos:
   a standard lecture demo with a known "will it land in the cart"
   debate.
   https://sites.google.com/nd.edu/ndphysicsdemos/mechanics/motion-in-two-dimensions/ballistic-cart-incline
   https://eric.ed.gov/?id=EJ518777
   https://pirt.asu.edu/demos/1D60.15
2. "is it easier to push or pull a box physics friction angle normal
   force explanation". Showed Brainly and Testbook homework threads,
   TutorChase ("why is it easier to push" asked the other way round),
   ScienceInsights and the PSU slipping-vs-tipping page: the question
   is asked both ways, the answer is pull (N = m g - F sin theta
   against m g + F sin theta).
   https://scienceinsights.org/is-pushing-or-pulling-easier-the-physics-explained/
   https://mechanicsmap.psu.edu/websites/7_friction/7-2_slipping_vs_tipping/slippingvstipping.html
3. "Galileo inclined plane ball rolling in groove on rails slower
   acceleration 5/7 error". Showed "Deep in Galileo's Groove" (The
   Physics Teacher 62, 104, 2024): Galileo's groove of 8.5 punti for a
   ball of radius 10 punti cut the linear acceleration by 5.75
   percent, and Galileo did not grasp the rotation; also BU lab
   handouts and PBS Learning Media on the inclined plane.
   https://pubs.aip.org/aapt/pte/article/62/2/104/3226191/Deep-in-Galileo-s-Groove
4. "part of a moving train always moving backwards flange wheel trick
   question". Showed the LinkedIn riddle post (wheel 420 mm, flange
   448 mm), two Quora threads, Wikipedia "Train wheel", Practical
   Engineering on rail shape and Scientific American "Train Wheel
   Science": the riddle is popular, the answer is the flange bottom.
   https://www.linkedin.com/pulse/question-what-part-train-moves-backwards-when-forward-dr-carlos
   https://www.quora.com/When-a-train-is-moving-forward-which-area-of-the-train-is-always-moving-backwards
5. "viral physics shorts October 2026 tabletop experiment debate
   which first". Showed only the fluxnote "50 viral science shorts
   ideas" list and tabletop-quantum funding news; nothing specific.
   https://fluxnote.io/guides/science-youtube-shorts-ideas
6. "pulling a sled rope angle optimal arctan friction coefficient best
   angle to pull". Showed Physics Forums sled threads, a Firgelli sled
   calculator with the atan(mu) optimum (16.7 degrees at mu 0.3) and
   homework pages: the optimum angle is a known but mild result.
   https://www.firgelliauto.com/blogs/engineering-calculators/sled-calculator
7. "rotating stool dumbbells spin faster demonstration how many times
   faster angular momentum arms in". Showed UCSC, Virginia Tech,
   UCSB, Stony Brook and HyperPhysics demo pages: the speed-up is
   I_out / I_in with the body's inertia chosen; a posture model.
   https://www.phys.vt.edu/outreach/projects-and-demos/demonstrations-wiki/mechanics/angular-momentum-stool.html
8. "physics demo tiktok 2026 ball launched from moving cart lands back
   in cart viral". Showed three YouTube Shorts (Part 1 flat cart,
   Part 3 "Ball launched from cart on incline - physics explanation"),
   Rhett Allain's howitzer-cart video analysis, a Northwestern demo
   page and TikTok discover pages: the flat version is a popular
   short and the incline version is framed as "ahead, behind or in
   the cart".
   https://www.youtube.com/shorts/R_8WNNHz1u0
   https://m.youtube.com/shorts/yvjXovAQEfQ
   https://groups.physics.northwestern.edu/demo/1D60.10.html
9. "bowling ball pendulum nose demonstration pushed instead of
   released why it hits". Showed Montana State, Iowa State, UCSB,
   Wisconsin and Colorado State demo pages: a push adds energy and the
   ball returns higher; no numbers.
   https://wonders.physics.wisc.edu/bowling-ball-pendulum/
10. "ruler on two fingers slide together always meet at center of mass
    friction explanation trick". Showed IOP Spark "Always balanced
    rule", Science World "Balance Rules", Scientific American "Seesaw
    Science: The Hammer-Ruler Trick", the AJP lab activity "Moving
    fingers under a stick", Dot Physics and the Modern Robotics
    meter-stick section: a classroom trick with the hammer variant
    (the fingers meet under the head).
    https://spark.iop.org/always-balanced-rule
    https://www.scientificamerican.com/article/seesaw-science-the-hammer-ndash-ruler-trick/
    https://www.researchgate.net/publication/241233474_Moving_fingers_under_a_stick_A_laboratory_activity

### Sources (fetched pages)

- Notre Dame ballistic cart incline: inclined track on a lab jack,
  launcher partway down, the ball fired as the cart passes and "still
  lands in the cart"; discussion of what gravity does in the cart's
  frame; no angles or speeds; no vertical-launch variant on the page.
- LinkedIn train riddle: wheel 420 mm, flange 448 mm, the flange point
  moves backward over about 35 degrees of rotation (the in-repo closed
  form gives 40.7 degrees = 2 acos(420 / 448); the post's figure is
  not reproduced).
- fluxnote science shorts ideas: lead with the counterintuitive detail
  in the first line, one concept per short, everyday comparisons; the
  physics list is space and quantum facts, not mechanics.
- pubs.aip.org "Deep in Galileo's Groove": HTTP 403; the 5.75 percent
  figure comes from the search abstract and was checked in-repo (5.93
  percent for a sphere with k = 2/5 on a groove 8.5 punti wide).
- rjallain.medium.com howitzer cart: HTTP 403, not read.

### Measured candidates (python3, /tmp/day37/research/*.py and *.log)

1. Cart on a ramp (cart_ramp.py, .log; cart_ramp_sched.py, .log). 30
   degree frictionless ramp, cart 1 kg, ball 50 g, launch 2.0 m/s
   relative to the cart as it passes a trigger 30 cm down (1.7153 m/s
   at 0.3498 s after release). Square to the ramp: flight 0.4710 s =
   2 u / (g cos a), miss 0.0000 m (2.2e-13), 23.55 cm above the ramp,
   the cart 1.3517 m past the trigger at 4.025 m/s. Straight up:
   flight 0.4079 s = 2 u / g, lands 0.4283 m up the ramp behind the
   cart (closed form 2 u^2 sin a (1 + m / M) / g = 0.4283; 0.4079
   without recoil), 17.66 cm high, the cart 1.1279 m past the trigger
   at 3.765 m/s. From rest at the trigger: 0 and 0.4283 m. 20 degrees
   0.2930 m; 45 degrees 0.6057 m; u 1.5 m/s 0.2409 m; u 3.0 m/s
   0.9636 m; cart 5 kg 0.4120 m. Cart normal force 8.493 N. Stepped
   at 1e-4 s with bisection at the ramp line; agrees with the closed
   forms to the printed digits. Drawing at 400 px/m: ramp 1.80 m =
   624 by 360 px, miss 171 px, apex 94 px. Landing at 0.82 and 0.76 s
   after release, 3.3 and 3.0 s of video at 1/4 speed.
2. Push or pull (push_pull.py, .log). 10 kg, mu 0.4, 50 N at 30
   degrees. Pull: N 73.07 N, friction limit 29.23 N, drive 43.30 N, a
   1.407 m/s^2, 2.815 m in 2 s. Push: N 123.07 N, limit 49.23 N, no
   motion. Thresholds 36.80 against 58.90 N (1.6006x), flat 39.23 N.
   60 N: 4.947 against 0.147 m. 70 N: 7.079 against 1.479 m. mu 0.3:
   2.138 against 0.638 m/s^2. mu 0.5: 0.677 against 0. Lock angle
   acot(mu) 68.20 degrees. Best pull angle atan(mu) 21.80 degrees at
   36.42 N.
3. Marble on rails (rails.py, .log). 20 degrees, 1 m, k 2/5. Flat:
   2.3959 m/s^2, 0.9137 s, 2.189 m/s, mu 0.104, spin share 0.2857.
   Rails 1.6 R (contact 0.6 R): 1.5888 m/s^2, 1.1220 s, 1.783 m/s, mu
   0.115, spin share 0.5263. Ratio 1.5079 (closed 1.5079), time
   1.2280. Rail marble at 0.6632 m when the flat one lands. 1.2 R
   0.9843 s; 1.8 R 1.3607 s. Ice cube 0.7722 s. Galileo's groove:
   contact 0.9052 R, acceleration x 0.9407 (5.93 percent less).
4. Fingers under a ruler (fingers.py, .log). 1 m ruler, fingers at 5
   and 95 cm, 5 cm/s, mu_s 0.4, mu_k 0.3, meet when the gap is 1 cm:
   0.497 / 0.505 m after 17 swaps and 17.84 s; swaps at 0.163, 0.753,
   0.310, 0.642, 0.393, 0.580 m. Hammer stick (CoM 0.2 m): 0.195 /
   0.204 m after 13 swaps; the far finger slides from 0.95 to 0.312 m
   before the first swap. mu 0.5 / 0.45: 44 swaps; 0.6 / 0.3: 8. Swap
   rule x_slip = (mu_k / mu_s) x_other.
5. Train flange (flange.py, .log). R 0.420 m, flange 0.448 m. 100
   km/h: flange bottom 1.852 m/s = 6.67 km/h backward, backward for
   40.73 degrees per turn (11.3 percent), rim top 200 km/h, loop 13.24
   mm, flange 28 mm below the rail top. 50 km/h: 3.33 km/h backward.
   Tyre bottom 0 exactly. Toy R 10 cm, flange 15 cm at 1 m/s: 0.5 m/s
   back, loop 55.4 mm.
6. Sled rope angle (sled.py, .log). 10 kg, mu 0.4, 40 N: flat 0.0772
   m/s^2 (0.154 m in 2 s), 10 degrees 0.2943, 21.80 degrees 0.3853
   (0.771 m), 30 degrees 0.3413, 45 degrees 0.0370, 60 degrees 0.
   Flat needs 39.23 N, best 36.42 N (7.2 percent less).
7. Leaking bottle (bottle.py, .log). Hole 20 cm under the surface:
   held 1.981 m/s, landing 0.632 m out from 0.5 m up; falling 0 m/s;
   floor at 0.319 s.
8. Bowling-ball nose pendulum (nose.py, .log). 3 m, 30 degrees:
   released returns to 30.000 degrees; pushed 0.3 m/s 30.175 degrees,
   0.46 cm higher, 0.79 cm further; pushed 1.0 m/s 31.894 degrees,
   5.10 cm higher, 8.50 cm further.
9. Rotating stool (stool.py, .log). Two 2 kg weights 0.7 to 0.2 m with
   a chosen body inertia 1 kg m^2: spin x 2.552.

### Ranking

Filter: continuous tabletop or everyday motion, two panels on the same
input that end visibly differently on a phone, one plain question, one
setup number, one payoff number, a closed-form check, a loop or repeat,
about 25 minutes with RK4, events or closed forms, no PDE, no fluid
grid, no fitted aerodynamics, no rider or posture models, no chosen
material strengths, no siblings of produced shorts.

1. Cart on a ramp (accepted, winner for the day 37 third slot). Square
   launch dead in the cup (0.0 cm) against the straight-up launch 42.8
   cm behind the cart; an exact closed form, a live "in the cart or
   behind it" debate, no friction constant at all, continuous motion,
   a natural repeat.
2. Push or pull a box (accepted). The same 50 N at 30 degrees: pull
   2.81 m in 2 s, push does not move; thresholds 1.60 apart; an
   everyday debate asked both ways online; the grip and force are
   chosen (stated), the panels end as "moves" against "still".
3. Fingers under a ruler (accepted). Meet at the balance point
   whatever the grip: 50 cm against 20 cm from the hammer head; the
   swap rule x = (mu_k / mu_s) x_other is exact; the panels end at
   visibly different places; stepped Coulomb slip with an event per
   swap; a slow build-up (18 s at 5 cm/s), so play it 2x.
4. Marble on rails (accepted, rank mid). 0.914 against 1.122 s, 1.508
   times the acceleration, exact; the Galileo peg is strong, but it is
   the fourth rolling short (rolling race, ice cube against ball, ball
   or ring, belt) and the mechanism is already told.
5. Train wheel backward (accepted, rank low). 6.67 km/h backward at
   100 km/h, exact; a riddle with one number rather than a two-panel
   race, and the 13 mm loop needs an inset or a toy wheel.
6. Sled rope angle (folded into the push-or-pull bullet). The optimum
   atan(mu) = 21.8 degrees saves only 7 percent of the force; the 15
   against 77 cm panels need a force tuned to the threshold.
7. Leaking bottle (rejected). 1.98 m/s against 0: a sibling of the
   produced Torricelli jets (same tank and jet drawing) and the water
   is a fluid parcel model again.
8. Bowling-ball nose pendulum (rejected). A 0.3 m/s push returns the
   ball only 0.46 cm higher, 5 cm for 1 m/s: the difference is not
   visible at 1080x1920, and the channel has produced six pendulum
   shorts (big swing, peg, carry and stop, Tarzan, coupled, wave).
9. Rotating stool (rejected). The speed-up depends on a chosen body
   inertia and a posture; the filter excludes rider and posture
   models.

Queued backlog ideas: nothing in this run showed a queued idea weak or
saturated beyond the notes already on them; no notes added.

### Winner

Cart on a ramp: a 1 kg cart rolling from rest down a 30 degree
frictionless ramp fires a 50 g ball at 2.0 m/s relative to itself as it
passes a trigger 30 cm down (1.715 m/s); the launcher pointing square
to the ramp drops the ball dead in the cup after 0.471 s (0.0 cm, the
cart 1.35 m further down); the launcher pointing straight up drops it
42.8 cm up the ramp behind the cart after 0.408 s (closed form 2 u^2
sin a (1 + m / M) / g; 40.8 cm without the recoil). Recommended for
the day 37 third slot; see the brief in the research report.

### Files changed

- docs/niche.md: appended "Added by trend research 2026-10-05 (evidence
  in task 20261005-100712; ...)" with five bullets: Cart on a ramp,
  Push or pull a box, Fingers under a ruler, Marble on rails (rank
  mid), Train wheel backward (rank low). No other bullet changed.
- tasks/20261005-100712/TASK.md (this file).
- No web/data change, no production, no upload, no commit in this run.
