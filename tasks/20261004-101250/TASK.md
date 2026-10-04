# Research trends: run 11 for the day 36 third slot and the backlog

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: backlog

## Goal

Eleventh research-trends run, 2026-10-04 from about 10:15 EEST, for the
third slot of day 36 and the backlog. The backlog in `docs/niche.md`
holds eighteen unproduced ideas; the day 36 orchestrator took kerb hop
(reframed as a 3 cm step, 0.7 against 0.9 m/s) and Atwood drop for slots
one and two and judged the rest weak for a first pick: space time-lapses
and counters (Kelvin wake, Collatz, secretary problem, rogue wave, Saturn
retrograde, Halley, L2 drift), low-ranked ideas (corner reflector,
basketball arc, Moon clock, sliding ladder, falling chimney, two springs
stacked or side by side), a tie payoff (bathtub drain), a heavy build
(dam break) and a model problem (fridge tip). Find 6 to 9 new candidates
that fit the winning format: continuous tabletop or everyday motion, two
panels on the same input that end visibly differently on a phone screen,
one plain question in the first two seconds, one setup number, one payoff
number, a closed-form check, a loop or a repeat, and a build of about 25
minutes with RK4, event-driven steps or closed forms (no PDE, no fluid
grid, no ray tracing, no fitted aerodynamics, no rider or posture models,
no chosen material strengths). Measure every survivor with a throwaway
script in /tmp/day36/research/ and check the model (contact forces
positive, no-slip friction available with the minimum mu stated, energy
kept where it should be, panels visibly different at 1080x1920). Rank the
survivors and name the best one for today's third slot with its numbers.
No production in this run.

## Evidence

Research ran 2026-10-04 about 10:15 to 10:40 EEST (throwaway scripts
and logs in /tmp/day36/research/, one per candidate, g 9.80665) and the
closing agent reran the winner with the repo's g 9.807
(/tmp/day36/carrystop-closed.py, log carrystop-closed.log) and ran the
web queries below at about 18:10. No production in this run.

### Queries (9 WebSearch, 6 WebFetch of which 4 failed or were unreadable)

1. "crane operator stop load swing trick pendulum timing". Showed the
   NIST news item and the AJP 2022 paper "The crane operator's trick
   and other shenanigans with a pendulum" (Carter and others): a
   payload is stopped dead by timed trolley speed changes a pendulum
   period (or half a period at double speed) apart; Cranes Today "Swing
   low" on anti-sway controls; HOIST Magazine on anti-sway systems.
   https://www.nist.gov/news-events/news/2022/02/nist-researchers-link-cutting-edge-gravity-research-safer-operation
   https://pubs.aip.org/aapt/ajp/article/90/3/169/2819818/The-crane-operator-s-trick-and-other-shenanigans
   https://www.cranestodaymagazine.com/analysis/swing-low/
2. "physics shorts viral 2026 pendulum demonstration tiktok youtube
   shorts". Showed TikTok discover pages for "physics teacher pendulum
   demonstration" and "simple pendulum physics", PhysicsIsFun's coupled
   and Foucault pendulum clips, a pendulum-wave short and a guide
   listing physics among the strongest Shorts niches: pendulum props
   are a live subject, so a pendulum with a measured surprise fits.
   https://www.tiktok.com/discover/physics-teacher-pendulum-demonstration
   https://fluxnote.io/guides/viral-physics-youtube-shorts-ideas-2026
3. "block sliding on movable wedge frictionless which reaches bottom
   first explanation". Showed Physics Forums threads, an Oregon State
   handout and a YouTube worked problem; the search summary itself got
   the direction wrong ("the block's acceleration is reduced"), which
   confirms the debate: on a free wedge the block reaches the floor
   sooner (measured 1.6x the acceleration along the slope).
   https://www.physicsforums.com/threads/block-sliding-down-wedge-problem.690377/
   https://paradigms.oregonstate.edu/act/handout/2404/pdf/
4. "spinning glass of water parabolic surface how fast rpm bottom dry".
   Showed Mungan's "Newton's rotating water bucket: a simple model"
   (USNA), the arXiv paper "Form of spinning liquids in diverse
   geometries" (dry patch when the paraboloid apex drops below the
   base) and a note that a 300 rpm cylinder takes about a minute to
   reach its paraboloid: the spin-up lag is real, narrate rpm not time.
   https://www.usna.edu/Users/physics/mungan/_files/documents/Publications/WAS6.pdf
   https://arxiv.org/pdf/2208.05059
5. "why does a door close by itself tilted hinges physics". Showed
   home-repair pages (Precision Home Worx, Dayoris, D and D Hardware)
   that explain a self-closing door as an out-of-plumb hinge line, and
   a gravity gate thread; the audience question is "why does my door
   close by itself", answered by tilt, with hinge friction deciding.
   https://www.precisionhomeworx.com/blog/why-do-doors-swing-open-or-shut-on-their-own
   https://www.tractorbynet.com/forums/threads/self-closing-gravity-gate-angled-hinges.375767
6. "hoop with weight on rim rolling hops Tokieda loaded hoop jump".
   Showed Tokieda's "The hopping hoop", Theron's thesis and papers,
   the 2025 LAJPE paper and the 2026 AJP "Littlewood's hopping hoop
   dynamics": the rebuttals (Butler, Pritchett, Theron, Yanzhu) hold
   that a rigid loaded hoop must slip before N reaches zero, which is
   what hoop_hop2.log measured (grip 3.6 to 19 needed near the hop).
   https://www.semanticscholar.org/paper/The-Hopping-Hoop-Tokieda/a0a18e86b2809cd7a3156679c023349759478271
   https://pubs.aip.org/aapt/ajp/article-abstract/94/5/359/3387077/The-Littlewood-s-hopping-hoop-dynamics
   https://royalsocietypublishing.org/rspa/article/475/2231/20190440/56865/Gliding-motions-of-a-rigid-body-the-curious
7. "Feynman wobbling plate spin wobble ratio 2 to 1 explanation video".
   Showed Tuleja's AJP 2007 paper, Chao's 1989 "Feynman's dining hall
   dynamics", a Wolfram demonstration and a three.js page; the known
   twist is that Feynman stated the ratio inverted (it wobbles twice
   as fast as it spins); the demonstrations are all 3D rigid-body
   renders with a rim mark, which is the readability problem.
   https://pubs.aip.org/aapt/ajp/article/75/3/240/1056339/Feynman-s-wobbling-plate
   https://demonstrations.wolfram.com/FeynmansWobblingPlate/
8. "physical pendulum rod vs simple pendulum same length which swings
   faster". Showed physics.info, LibreTexts and a calculator page: the
   rod behaves like a 2/3-length string, a common student question
   with the answer often given backwards (longer period for a door).
   https://physics.info/pendulum/
   https://phys.libretexts.org/Bookshelves/University_Physics/University_Physics_I_-_Classical_Mechanics_(Gea-Banacloche)/11:_Simple_Harmonic_Motion/11.03:_Pendulums
9. "carrying bag OR bucket swinging stop walking pendulum trick reddit
   explain". Showed only Steve Spangler's coupled-pendulum "stop and
   go" trick and bag patents: no popular treatment of stopping a
   carried bag by timing, so the carry-and-stop angle is fresh.
   https://stevespangler.com/experiments/swinging-pendulum-stop-go-trick/

### Sources (fetched pages)

- https://www.nist.gov/news-events/news/2022/02/nist-researchers-link-cutting-edge-gravity-research-safer-operation
  : short haul, apply a trolley velocity and the same velocity in the
  opposite sense exactly one pendulum period later; long haul, start
  at a speed and double it half a period later; the trick formalises
  what operators do by feel; "swing a thousand-pound chunk of steel
  too fast or too far and someone can get killed". No lengths given.
- https://www.cranestodaymagazine.com/analysis/swing-low/ : operators
  "drive into the swing to dampen it"; the pendulum period depends on
  the cable length and not on the load; anti-sway controls model the
  pendulum; no numbers.
- https://pubs.aip.org/aapt/ajp/article/90/3/169/2819818/... : HTTP
  403, abstract taken from the search result.
- https://scholar.sun.ac.za/bitstreams/e9259d2b-.../download (Theron,
  loaded hoops): HTTP 429, not read.
- http://lajpe.org/jun25/19_2_05.pdf : certificate mismatch, not read.
- https://physedu.science.upjs.sk/modelovanie/files/feynman_plate_2007.pdf
  : PDF not readable by the fetcher; the 2/cos(tilt) ratio was
  measured in-repo instead (feynman_plate.log).
- https://scienceblogs.com/principles/2015/03/12/the-physics-of-our-back-gate
  : about gate sag torque, not tilted hinges; not used.

### Measured candidates (python3, /tmp/day36/research/*.py and *.log)

1. Crane stop / carry and stop (crane_stop.py, .log; rerun with g 9.807
   in /tmp/day36/carrystop-closed.py, .log). L = g / pi^2 = 0.9937 m,
   T0 2.0000 s, hand at 0.5 m/s, instant start and stop. Lag during
   the carry 9.187 deg. Residual swing by stop time: 0.5 s 12.906,
   1.0 s 18.434 (linear 18.354, 31.4 cm sideways), 1.5 s 12.972, 2.0 s
   0.093 (0.2 cm), 2.0032 s (nonlinear period) 0.001, 3.0 s 18.433,
   4.0 s 0.186. Min string tension 0.949 g. Ramps 0.1 s: 18.353 and
   0.091; 0.3 s: 17.731 and 0.080. At 1.0 m/s: lag 18.434, stops 37.365
   and 0.750, nonlinear period 2.0130 s. Crane L 10 m (T 6.345 s) at
   1.0 m/s: 11.591 and 0.022. L 1.00 m (T 2.0064 s): 2.0 s stop 0.274,
   2.0064 s 0.091. RK4 1e-4 s, half step identical to 1e-6 deg.
2. Wedge block (wedge_block.py, .log). 1 kg block, 1 kg wedge, 30 deg,
   30 cm drop, 60 cm slope, frictionless. Fixed: 4.9033 m/s^2, 0.4947
   s, 2.426 m/s. Free: a_rel 7.8453 (1.6000x), wedge 3.3971 m/s^2 back,
   0.3911 s (1.2649x), N 0.693 of the block weight, wedge back 0.2598 m
   and block forward 0.2598 m. RK4 two-DOF: 0.3911 s, momentum
   -1.5e-13, energy 2.942 = 2.942 J. Wedge 0.5x, 2x, 5x: 2.000x,
   1.333x, 1.143x acceleration.
3. Stick vs string (stick_vs_string.py, .log). 1 m from 20 deg: 2.0218
   against 1.6508 s, ratio 0.8165 = sqrt(2/3); stick like a 66.67 cm
   string; 14.84 against 18.17 swings in 30 s.
4. Spinning glass (spinning_glass.py, .log). R 3.5 cm, H 10 cm. Fill
   3 cm: dry at 296.0 rpm, spill 493.3; 4 cm: dry 341.8 (rim 8.00 cm),
   spill 427.2; 5 cm: both at 382.1; 6 cm: spill 341.8 (centre 2.00
   cm), dry 418.6; 7 cm: spill 296.0, dry 452.1. Ramp 0 to 450 rpm in
   30 s: 4 cm dry 22.785 s, spill 28.481 s; 6 cm spill 22.785 s, dry
   27.905 s. Ekman spin-up at 342 rpm 8.4 s. Volume check 0.153938 L
   both ways.
5. Door tilt (door_tilt.py, .log). 0.8 m door from 90 deg, no hinge
   friction: tilt 0.10 deg shuts in 10.350 s, 0.25 6.546, 0.50 4.629,
   1.00 3.273 (edge 0.64 m/s), 2.00 2.314, 3.00 1.890; RK4 equals the
   closed form; time scales 1 / sqrt(sin alpha) (1 deg / 4 deg =
   1.9992). A 20 kg door at 1 deg needs under 1.369 N m of hinge
   friction to move at all.
6. Ramp pendulum (ramp_pendulum.py, .log). 30 cm pendulum on a sled
   down a frictionless 20 deg slope: equilibrium 20.00 deg from
   vertical (the slope angle), the 2 m run lasts 1.092 s = 0.96 of the
   1.134 s period; released vertical and undamped it swings 0 to 37.76
   deg and reads 0.08 at the bottom; damping 1/s reads 7.92, 3/s 15.33;
   rough slope mu 0.2 gives atan(mu) = 11.31 deg.
7. Feynman plate (feynman_plate.py, .log). Thin disc I3 = 2 I1 at 1
   turn/s spin: wobble 2.0012 turns/s at 2 deg tilt, 2.0076 at 5,
   2.0309 at 10, 2.1284 at 20 (= 2 / cos tilt); a 12 cm plate 8 mm
   thick has I3 / I1 = 1.9970.
8. Hoop hop (hoop_hop.py, .log; hoop_hop2.py, .log). Rim mass on a
   rolling hoop, no slip. Mass at the top (R 0.35 m): hop threshold
   1.819 m/s at m/M 3, 2.620 at m/M 1, 0.678 at m/M 10, 0.050 at m/M
   1000; just below threshold the grip needed is 1.7 to 13.7, and at
   the hop the friction force is finite while N is zero (mu to
   infinity). Mass at the bottom, M 0.30 kg, m 0.35 kg: R 0.15 m hops
   from 4.90 m/s at the top of the arc (top speed 3.209 = sqrt((M + m)
   g R / m)); R 0.30 m from 5.24 m/s; grip needed before the hop 1.0 at
   N = 50 percent of the weight, 1.7 at 20, 2.5 at 10, 3.6 at 5; at
   1.3x threshold 5.0 / 9.7 / 19.1; energy drift 1e-13.

### Ranking

Filter: continuous tabletop or everyday motion, two panels on the same
input that end visibly differently on a phone, one plain question, one
setup number, one payoff number, a closed-form check, a loop or repeat,
about 25 minutes with RK4 or closed forms, no PDE, no fluid grid, no
fitted aerodynamics, no chosen material strengths.

1. Carry and stop (accepted, winner for the day 36 third slot). Stop
   after 1.0 s: 18.43 deg swing; stop after 2.0 s: hangs still at 0.093
   deg. Everyday motion (a carried bag, a crane hook), an exact zero at
   one period, a 2 s loop, closed form against RK4, pegged to the
   crane operator's trick (NIST, AJP 2022), no friction or material
   constants at all.
2. Block on a wedge, fixed or free (accepted). 0.391 against 0.495 s,
   exactly 1.6x the acceleration; a debate the web gets backwards;
   closed form, momentum and energy checks; frictionless everywhere,
   said plainly.
3. Stick or string (accepted, rank low). 1.651 against 2.022 s,
   exactly sqrt(2/3); both keep swinging, so the panels differ in rate,
   not outcome, like the queued two-springs idea.
4. Spinning glass, 4 cm or 6 cm (accepted, rank low). Dry spot first
   at 341.8 rpm against spill first at the same 341.8 rpm, the swap at
   half full (382.1 rpm). A fluid, but rigid-rotation closed forms, no
   grid; the Ekman spin-up of about 8 s means the rpm is the claim,
   not the time; the glass must be a true cylinder.
5. Door tilt (rejected). Both panels close (3.27 against 6.55 s), so
   they differ in time not outcome, and whether a real door moves at
   all is a chosen hinge-friction torque (1.369 N m at 1 deg for 20
   kg), the kind of chosen material constant the filter excludes.
6. Ramp pendulum (rejected). The payoff atan(a / g) = slope angle is
   the balloon-or-dice lean produced 2026-09-30, the 2 m run is only
   0.96 periods so the settled angle depends on a chosen damping, and a
   rough slope reads a chosen mu.
7. Feynman plate (rejected). The 2 / cos(tilt) ratio needs a 3D
   rigid-body render with a rim mark read against a wobble, hard to
   read on a phone, and it has no two-panel debate on one input.
8. Hoop hop (rejected). The sim's own check fails the filter: the hop
   needs the grip to go to infinity as N reaches zero (3.6 at 5
   percent of the weight, 19 at 1.3x threshold), the mass-at-the-top
   threshold hops at t = 0 with F = 0 (a degenerate start), the thin
   hoop limit hops at 0.05 m/s, and the literature since Tokieda says a
   rigid loaded hoop slips before it hops. A slip model would be a
   40-minute build with a chosen mu.

Queued backlog ideas: nothing in this run showed a queued idea weak or
saturated beyond the notes already on them; no notes added.

### Winner

Carry and stop: a weight on a 99.4 cm string (period 2.000 s, g 9.807)
carried at 0.5 m/s by a hand that stops instantly; stopped after 1.0 s
(50 cm) it swings 18.43 degrees (31 cm sideways), stopped after 2.0 s
(100 cm) it hangs still at 0.093 degrees; lag during the carry 9.19
degrees; linear closed form 2 V / sqrt(g L) |sin(pi tau / T)| gives
18.35 and 0; string tension never below 0.949 of the weight. Being
produced as sims/carrystop under the newest day 36 task (20261004-18xxxx).

### Files changed

- docs/niche.md: appended "Added by trend research 2026-10-04 (evidence
  in task 20261004-101250; ...)" with four bullets: Carry and stop
  (taken for the day 36 third slot), Block on a wedge fixed or free,
  Stick or string (rank low), Spinning glass 4 cm or 6 cm (rank low).
  No other bullet changed.
- tasks/20261004-101250/TASK.md (this file).
- No web/data change, no production, no upload, no commit in this run.
