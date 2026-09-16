# Research trends: continuous-motion refill, run 4

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: backlog

## Goal

Fourth research-trends run, 2026-09-16 about 10:10 to 10:20 EEST. The
backlog in `docs/niche.md` held five unproduced ideas (parking-lot
probing, Collatz flights, secretary problem, rogue wave, Kelvin wake with
a failed feasibility check). Rainbow angle and quantum tunnelling are in
production today and were not re-proposed. Find 8 to 12 new candidates
that fit the winning formats: continuous physical motion, two-panel
same-input comparisons, one plain question in the first two seconds, one
setup number, one payoff number, seamless loops of periodic physics, and
numbers that a closed form can check. No production in this run. By
instruction `web/data/slate.json` and `web/data/status.json` were not
touched, sims/, projects/, media/ and secrets/ were not touched, and no
commit was made.

## Channel evidence used for the filter

Views at run time: Fourier circles 1,047, brachistochrone 946,
tautochrone 943, Dzhanibekov 941, elevator 918, gyroscope top 909,
Langton 902, Kapitza 829, slinky 774, boarding 771. Probability grids,
counters and number drawings sit at 5 to 132. Continuous motion with a
plain question hook wins; counters and static drawings do not.

## Queries (10 WebSearch, 3 WebFetch)

1. "viral physics shorts September 2026 trending physics demonstration
   tiktok youtube". Showed the fluxnote 2026 idea lists and Shorts
   playlists: gyroscopes, vacuum free fall, the double slit "simplified
   visually", pendulum waves, the spinning stool, Magnus effect and
   Bernoulli demos are the recurring subjects; the winning formula is a
   counterintuitive "wait, what" moment inside 60 seconds. Matches the
   channel's own measurements.
2. "solid vs hollow cylinder ramp race which reaches bottom first moment
   of inertia demo". Showed Scientific American "Rolling Race", UCSC and
   UCSB demo pages, ASU "Racing Spheres": the solid object always wins,
   mass and diameter do not matter, a full soup can beats an empty one.
   Standard lecture demo, still a viral kitchen experiment.
3. "Newton's cradle why two balls swing out not one ball twice the speed
   explanation". Showed Wikipedia, Physics Forums, Quora, Virginia Tech
   demo page: one ball at double speed conserves momentum but doubles the
   energy; steel contacts finish in under 200 microseconds so the
   collisions are sequential. The "why not one ball faster" question is
   the plain question for the hook.
4. "ball rolling on rotating turntable moves in circles 2/7 angular
   velocity". Showed the Weckesser AJP paper listing (Colgate), Fowler's
   UVA notes, Physics Forums, UCSB 16.21 (balls on rotating hoops): a ball
   rolling on a turning plane runs in a circle at 2/7 of the table rate,
   any circle, centre set by the release. Fetched below.
5. "astronomy events October November 2026 Orionids Leonids meteor shower
   comet". Showed NHM, Star Walk, Farmers' Almanac, Sea and Sky: Orionids
   peak 2026-10-21 from Halley's dust, Taurids 11-05, Leonids 11-17,
   supermoon 11-24. Fetched the Sea and Sky calendar below.
6. "physics anniversary October 2026 OR November 2026 100 years OR 150
   years OR 200 years discovery centenary". Showed nothing usable for the
   window beyond the Schrodinger centenary already in the backlog and a
   Brookhaven symposium; no new anniversary peg.
7. "Sun-Earth L2 unstable e-folding time days JWST station keeping drift
   away Lagrange point instability". Showed the JWST user docs (station
   keeping every 21 days, halo orbit dynamically unstable), the USTC
   lecture note (e-fold about 23 days for L1 and L2, 150 years for L3),
   AJP 94 741 (2026) on the linear stability of Lagrange points. Live
   subject with a clean number.
8. "tsunami shoaling Green's law wave height grows fourth root depth
   speed sqrt(gh) 1 m open ocean beach". Showed Wikipedia Green's law,
   Terence Tao's shallow-water post, CSULB notes: speed sqrt(g h), 198
   m/s at 4,000 m; height grows as the fourth root of the depth ratio.
9. "coupled pendulums energy transfer complete swap beat period weak
   spring demo". Showed PASCO, Exploratorium, UCSC and Basel lab manuals:
   one pendulum started, the other still; the first stops dead when the
   energy has swapped; swap time is inversely proportional to the mode
   frequency difference.
10. "Halley's comet perihelion speed 54 km/s aphelion 0.9 km/s time spent
    inside Earth orbit". Showed NASA, Space.com, UT Austin worked example:
    54.52 km/s at the 1986 perihelion, 0.909 km/s at aphelion; the 2061
    return crosses Earth's distance on 2061-06-19; no source gives the
    time inside 1 AU, so the sim supplies it (Kepler's equation check
    below).

Fetched pages:

- https://math.colgate.edu/~wweckesser/pubs/AJP_BallRolling.pdf : 404.
  Replaced by the UVA notes.
- https://galileoandeinstein.phys.virginia.edu/7010/CM_29_Rolling_Sphere.html
  : "For a uniform sphere, I = (2/5) M a^2, so r' = (2/7) omega n x
  (r - r0)"; the path is a circle, and it "could be any circle" with the
  centre set by the release point.
- https://www.seasky.org/astronomy/astronomy-calendar-2026.html : events
  in the window: equinox 09-23, Neptune opposition 09-25, Saturn
  opposition 10-04, Draconids 10-07, Mercury elongation 19.6 deg 10-12,
  Orionids 10-21/22, Taurids 11-04/05, Leonids 11-17/18, Mercury
  elongation 11-20, supermoon 11-24, Uranus opposition 11-25.

## Closed-form checks (python under nix, run 2026-09-16)

- Rolling race, 2 m ramp at 20 deg, t = sqrt(2L(1+k)/(g sin theta)):
  solid sphere 1.292 s, solid cylinder 1.337 s, hollow sphere 1.410 s,
  hoop 1.544 s; hoop/sphere 1.195.
- Turntable at 33 1/3 rpm (1.800 s per turn): solid ball loop 7/2 turns
  = 6.30 s; thin hollow ball (2/3 M a^2 gives 2/5) 5/2 turns = 4.50 s.
- Coupled pendulums, L = 1 m: w1 = 3.1316 rad/s (period 2.006 s); a
  spring with 2k/m = 1.0085 s^-2 gives w2 - w1 = pi/20, so the swap takes
  20.0 s and the beat 40.0 s, 9.97 swings per swap.
- Monkey and hunter, target 10 m up and 20 m away: at 30 m/s the hit is at
  0.745 s after both fell 2.724 m; at 60 m/s 0.373 s and 0.681 m; aimed 1
  deg high the miss is 0.440 m; below 15.66 m/s the target lands first.
- Bead on a 0.20 m hoop: threshold sqrt(g/R) = 7.00 rad/s = 66.9 rpm;
  1.5x gives 63.6 deg (100.3 rpm), 2x gives 75.5 deg (133.7 rpm).
- Saturn retrograde on circular orbits (1 AU, 1 yr; 9.5826 AU, 29.457
  yr): synodic 378.09 d, retrograde 137.5 d, loop 6.73 deg, net progress
  12.65 deg per synodic period.
- Halley, a 17.834 AU, e 0.96714: P 75.31 yr, q 0.586 AU, Q 35.08 AU;
  54.57 km/s at perihelion, 0.912 at aphelion (59.9 to 1); time inside 1
  AU 78 d, inside 1.524 AU 146 d, inside 5.203 AU 792 d, inside 10 AU
  2,081 d.
- Sun-Earth L2, mu 3.0035e-6: 1,501,107 km beyond Earth, c2 3.9408,
  unstable eigenvalue 2.4844 per time unit (58.13 d), e-fold 23.40 d,
  doubling 16.22 d; a 1,000 km offset is 71,800 km at day 100; L1 e-fold
  22.95 d; L4 stable, libration periods 1.00 and 222 yr.
- Tsunami: sqrt(g h) 198.1 m/s at 4,000 m, 9.90 m/s at 10 m; Green's law
  (4000/10)^(1/4) = 4.47 (2.99 at 50 m); wavelength ratio 20.
- Double slit, lambda 2 cm, d 10 cm: bright bands at 11.5, 23.6, 36.9
  and 53.1 deg; on a screen 60 cm away 12.2, 26.2, 45.0 cm.
- Newton's cradle: two balls in at v; one ball out at 2v needs twice the
  energy and would rise 40 cm from a 10 cm release; on 30 cm strings a
  10 cm rise is a 48.2 deg swing, half period about 0.55 s.

## Candidates

Numbers below are expectations to check; the sim measures the claim.

1. Turntable ball. Solid ball rolling across a 33 1/3 rpm record beside a
   hollow ball with the same push; a frictionless puck slides off. Expect
   closed circles, 3.5 table turns per loop (6.30 s, 2/7) against 2.5
   (4.50 s, 2/5). Pillar: physics (rotation). Rolling-constraint ODE, RK4,
   exact check against 2/7. Hook: "Roll a ball on a spinning record. Does
   it fly off?" Loops exactly. Sources: UVA notes, UCSB 16.21. Accepted:
   the most surprising number of the run, under one hour.
2. Rolling race. Solid ball, solid cylinder, hollow ball, hoop on the same
   2 m ramp at 20 deg. Expect 1.292, 1.337, 1.410, 1.544 s, same order at
   any mass or size. Pillar: physics. Exact constant acceleration, a
   second run with doubled mass and size to show the same times. Hook:
   "Same size, same weight. Which rolls down first?" Sources: Scientific
   American, UCSC, ASU. Accepted: viral kitchen demo, under 45 min.
3. Coupled pendulum swap. Two 1 m pendulums joined by a weak spring, one
   started at 10 deg, beside the same pair with no spring. Expect the
   first to stop dead at 20.0 s and the swing to return at 40.0 s, the
   unsprung neighbour never moving. Pillar: physics (oscillators). Linear
   two-mode ODE, RK4, exact beat check. Hook: "Why does this pendulum stop
   by itself?" 40 s beat loops exactly. Sources: PASCO, Exploratorium.
   Accepted: cheap, periodic, one clean payoff time.
4. Monkey and hunter. Dart at a target 10 m up and 20 m away, target
   dropped at the shot, 30 beside 60 m/s. Expect 0.000 m miss for both,
   44 cm miss when aimed 1 deg high, target lands first under 15.7 m/s.
   Pillar: physics (viral debate). Exact projectile motion. Hook: "The
   target drops the moment you shoot. Aim at it or above it?" Accepted:
   classic debate, under 45 min; the 0.000 m tie is the same shape as the
   bullet drop, so hold it a few days.
5. Newton's cradle. Five steel balls with Hertz contacts, two lifted 10 cm
   beside one lifted 10 cm. Expect two out to 10 cm, never one at double
   speed (40 cm, twice the energy). Pillar: physics (collisions).
   Pendulum swings exact, contacts integrated at microsecond steps;
   momentum and energy checked. Hook: "Two balls in. Why not one ball
   out at twice the speed?" Sources: Wikipedia, Virginia Tech. Accepted:
   viral question; about 1.5 hours for the contact stepping.
6. Bead on a spinning hoop. 20 cm hoop at 60 beside 100 rpm. Expect the
   slow bead at the bottom and the fast bead holding at 63.6 deg
   (threshold 66.9 rpm). Pillar: physics (rotation, bifurcation). Damped
   ODE, exact angle check. Hook: "Spin the hoop faster. Where does the
   bead sit?" Sources: UCSB 16.21. Accepted: cheap, one number.
7. Saturn retrograde. Circular orbits, Sun's view beside Earth's sky view.
   Expect 137 days backward per 378-day cycle, 6.7 deg loop, 12.65 deg
   net. Pillar: physics (orbital). Exact circles, loops. Hook: "Why does
   Saturn go backward?" Peg: Saturn opposition 2026-10-04 (also Sputnik
   day). Source: Sea and Sky calendar. Accepted: live peg, under 45 min;
   real dates differ a little because the orbits are not circles, state
   that in the description.
8. Halley's comet. The 75.3-year orbit beside Earth's. Expect 54.6 against
   0.91 km/s and 78 days of 75.3 years inside 1 AU (792 inside Jupiter).
   Pillar: physics (orbital). Kepler propagation, vis-viva check, loops.
   Hook: "Halley takes 76 years. How long is it near us?" Peg: Orionids
   2026-10-21. Sources: NASA, Space.com. Accepted: peg and a sharp number.
9. L2 drift. Probe 1,000 km off L2 with no engine beside one 1,000 km off
   L4. Expect doubling every 16.2 days (e-fold 23.4), 72,000 km at day
   100; L4 never leaves. Pillar: physics (orbital, chaos family).
   Rotating-frame CR3BP RK4, eigenvalue check. Hook: "Park a telescope at
   L2. How long before it drifts away?" Peg: JWST station keeping.
   Sources: JWST docs, USTC note. Accepted: strong number, about one hour.
10. Tsunami shoaling. 1 m wave from 4,000 m onto a slope to 10 m beside a
    flat tank. Expect 198 to 9.9 m/s and 1 m to 4.5 m. Pillar: waves. 1D
    shallow water, Green's law check. Hook: "This wave is 1 m tall at
    sea. Why is it 4 m at the beach?" Peg: World Tsunami Awareness Day
    2026-11-05. Sources: Wikipedia, Tao. Accepted; about 1.5 hours.
11. Double slit ripple tank. One slit beside two slits 10 cm apart, 2 cm
    waves. Expect bands at 11.5, 23.6, 36.9 deg and none from one slit.
    Pillar: waves. 2D finite-difference solver, d sin theta = n lambda
    check, steady state loops. Hook: "Open a second slit. Why do dark
    lines appear?" Peg: Schrodinger centenary, Nobel week. Source:
    fluxnote list ("double slit simplified visually"). Accepted; about
    1.5 hours; ranked below the mechanical ideas.
12. Lorenz water wheel. Leaking buckets under a steady tap beside a faster
    tap. Expect steady turning against irregular reversals; count the
    reversals. Pillar: chaos. RK4 on the Malkus wheel. Hook: "The tap is
    steady. Why does the wheel keep reversing?" Accepted with a caveat:
    the count depends on the chosen tap rate, so the visible reversals
    carry the story; ranked last.

Rejected: Karman vortex street (2D fluid solver, over three hours);
Tacoma Narrows flutter (needs an aerodynamic model, so the number would
be model-dependent; anniversary 1940-11-07); Magnus curve ball and
Bernoulli beach ball (lift coefficient is a choice, not a measurement);
domino chain, chain fountain, tippe top (contact dynamics too heavy);
Coriolis in a sink (effect too small to show honestly); Foucault
pendulum (rejected in run 3, weak number); Mercury elongation (weak
number); Newton's cannonball (third orbital slot this week, kept as a
spare); Fibonacci Day drawings (number drawings sit at 5 to 132 views);
Coriolis carousel throw (covered by the turntable ball).

## Ranking

For today's third slot, one agent, about 90 minutes each:

1. Turntable ball (closed circles, 3.5 table turns per loop, 2/7 exact;
   under one hour; loops).
2. Rolling race (1.292 against 1.544 s, same order at any mass or size;
   under 45 minutes; loops).
3. Coupled pendulum swap (stops dead at 20.0 s, back at 40.0 s; under one
   hour; the 40 s beat loops exactly).

Then Saturn retrograde and Halley for their October pegs, L2 drift, bead
on a hoop, monkey and hunter, Newton's cradle, tsunami, double slit,
water wheel.

## Outcome

Twelve ideas appended to `docs/niche.md` under "Added by trend research
2026-09-16 (evidence in task 20260916-100924)". One line appended to
`web/data/log.jsonl`. No slate or status update, no production, no
commit in this run by instruction.
