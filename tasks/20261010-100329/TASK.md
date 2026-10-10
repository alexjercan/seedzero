# Research trends: run 15 for the day 42 slate and the backlog

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: backlog

## Goal

Fifteenth research-trends run, 2026-10-10 from about 10:05 EEST, for
all three slots of day 42 and the backlog. The backlog in `docs/niche.md`
holds twenty-four unproduced ideas. The day 39 and day 40 closes judged
most of them weak for a first pick: space time-lapses and counters
(Kelvin wake, Collatz, secretary problem, rogue wave, Saturn retrograde,
Halley, L2 drift), low-ranked ideas (corner reflector, basketball arc,
Moon clock, sliding ladder, falling chimney, two springs stacked or side
by side, stick or string, train wheel backward, fridge tip with a broken
model, ladder at 75 or 60 degrees rank 6, monkey and weight rank 8), a
tie payoff (bathtub drain) and a heavy build (dam break). Ideas not
ranked low: front drive up an icy hill nose first or reversing (rank 4,
from run 14; the Car Talk debate), rope or bungee (rank 5) and bosun's
chair (rank 6). Tall glass or short glass is a tray sibling of the
marble-or-dice short published 2026-10-07 and waits until about
2026-10-14: do not pick it today. Find 6 to 9 new candidates that fit
the winning format: continuous tabletop or everyday motion, two panels
on the same input that end visibly differently on a phone screen, one
plain question in the first two seconds, one setup number, one payoff
number, a closed-form check, a loop or a repeat, and a build of about 25
minutes with RK4, event-driven steps or closed forms (no PDE, no fluid
grid, no ray tracing, no fitted aerodynamics, no rider or posture
models, no chosen material strengths). Avoid siblings of produced shorts
(read the [produced ...] notes in docs/niche.md: drops beside a ball,
Atwood, yo-yo, chain off a desk, capstan, coin on a record, river
crossing, kerb hop, carried pendulum, balloon in a car, belt, broom,
bat, strings, spool, cue ball, tablecloth, brake or swerve, ice cube
against ball, bucket, swing, spring drop, hoop bead, gyro top, Kapitza,
resonance, metronomes, block on a wedge, spinning glass, cart on a
ramp, push or pull a crate, marble on rails, fingers under a ruler,
tilting tray, boat jump, banked curve, toast off a table, stack of books
past the edge, round or hexagonal pencil). Re-judge the icy hill, rope
or bungee and bosun's chair against the new candidates; any of them may
take a slot today if it beats them. Measure every survivor with a
throwaway script in /tmp/day42/research/ (g = 9.807, python3 via `nix
develop -c python3`) and check the model (contact forces positive,
no-slip friction available with the minimum mu stated, energy kept where
it should be, panels visibly different at 1080x1920). Rank the survivors
and name the best three for today's three slots with their numbers,
question, setup and payoff numbers and a drawing sketch each in the
style of the day 40 briefs (read tasks/20261008-102529/TASK.md "Goal"
for the brief style and tasks/20261008-100401/TASK.md for the evidence
style). No production in this run.

Channel results to weigh (views after a few days, refreshed 2026-10-10
10:04): the strongest recent shorts were "which climbs higher" ice cube
against ball (973), the balloon in a car (943), brake or swerve (734),
the stick on ice (619), the ball or the ring coming back (512), the
banked road (366), the box or the ball on a belt (347), the Atwood drop
(320), the fingers under a ruler (263), the wedge (239); weak ones were
the chain off the desk (3), the capstan (5), the car leaving the road
(2), the spinning glass (5), the push-or-pull crate (14), the boat jump
(13), the string snap (46), the broom (45), the bat (52), the carried
pendulum (75), the tilting tray (79); the day 41 shorts (toast 70, books
72, pencils 3) are one day old. Everyday objects a viewer owns beat lab
props; a visible yes-or-no ending beats a rate difference; cars, balls
and kitchen or desk objects did best.

Rules for this run: follow the research-trends skill (five to ten
focused queries, WebSearch and WebFetch). Append the survivors to
docs/niche.md at the very end of the file under a new paragraph "Added by
trend research 2026-10-10 (evidence in task 20261010-100329; selection
favoured ...)" in the existing one-line bullet format; re-read the file
right before editing and append only. Record the evidence in this task
file (tasks/20261010-100329/TASK.md: queries, URLs, what each showed,
why each idea was accepted or rejected, the measurement logs) under "##
Evidence". Do not edit web/data/ (the orchestrator appends the journal
entry from your report), do not run git, do not produce anything, do not
spawn subagents, never use sleep in Bash. Finish by reporting: the
ranked survivors with their numbers, the recommended three slot ideas
each with a full brief paragraph, the docs/niche.md lines you added, and
a one-paragraph journal line for web/data/log.jsonl.

## Evidence

Research ran 2026-10-10 from about 10:05 EEST. Throwaway scripts and
logs in /tmp/day42/research/ (cup.py, puck.py, puck2.py, misc.py with
.log files; g 9.807, python3 via nix develop). No production, no git,
no web/data change in this run.

### Queries (9 WebSearch, 5 WebFetch)

1. "ball on rotating turntable rolls in a circle 2/7 angular velocity
   physics demonstration Weltner". Showed the Harvard problem of the
   week, UCSB demo 16.03, arXiv 1812.02739 and Weltner's paper: a ball
   placed on a turning disc circles at 2/7 of the disc rate. Rejected
   before measuring: the channel produced "Push a ball across a spinning
   record" (sims/turntable, 2026-09-16, a circle every 3.5 turns), so a
   ball on a lazy Susan is a produced sibling.
   https://www.physics.harvard.edu/resource/sol21pdf
2. "why does a paper cup roll in a circle cone rolling physics radius
   apex". Showed Physics Forums (radius of a rolling paper cup),
   Wikipedia rolling cone motion: a truncated cone rolls about its
   apex; the rim circles have radii set by extending the cup to a point.
   https://www.physicsforums.com/threads/calculate-radius-of-rolling-paper-cup.82514/
   https://en.wikipedia.org/wiki/Rolling_cone_motion
3. "ball bouncing down stairs steady bounce height coefficient of
   restitution never stops physics". Showed textbook problems (h = d /
   (1 - e^2)) and Gruiz et al., Eur J Phys 2017 "Chaotic or just
   complicated? Ball bouncing down the stairs": stationary bouncing
   always sets in. https://fiztan.phd.elte.hu/english/student/meszena_ball.pdf
4. "viral physics debate October 2026 everyday "which one" experiment
   shorts". Showed only generic idea lists and news feeds: no specific
   peg this week. https://fluxnote.io/guides/viral-physics-youtube-shorts-ideas-2026
5. "Farkas frictional coupling between sliding and spinning motion disk
   stops translating and rotating at the same time 0.653". Showed
   Farkas, Bartels, Unger, Wolf PRL 90, 248302 (2003), the APS story
   "Slip-Slidin' Away" and the 2005 PRL on terminal regimes: a sliding
   spinning disc stops both motions at the same instant, v / (R w) tends
   to 0.653 for a uniform disc, and a spinning disc slides farther.
   https://arxiv.org/abs/physics/0210024
   https://physics.aps.org/story/v11/st26
6. "tailgating two second rule physics both cars brake same deceleration
   does following car hit reaction time gap". Showed Wikipedia
   two-second rule and stopping-distance pages: the rule is a reaction
   buffer; with equal braking the gap after the reaction stays constant.
   https://en.wikipedia.org/wiki/Two-second_rule
7. "Nobel Prize in Physics 2026 announced October 6 2026 winners".
   Showed the prize to Francis Halzen for IceCube neutrinos: no
   tabletop peg. https://www.nobelprize.org/prizes/physics/2026/press-release/
8. "pull a stuck car with a rope tied to a tree push the rope sideways in
   the middle force multiplication trick physics". Showed textbook
   problems (65 to 80 N sideways gives about 300 N on the car at 2 m of
   sag) and a Car Talk thread: a static trick.
   https://community.cartalk.com/t/physics-help/29908
9. (sibling check, local) projects/turntable, bounceslope, zenobounce,
   racingballs, wallbounce titles read from metadata.json.

### Sources (fetched pages)

- arXiv physics/0210024 abstract: "friction force and torque ... are
  inherently coupled"; the disc "always stops its sliding and spinning
  motion at the same moment". The 0.653 terminal ratio came from the
  search summary of the PRL; this run's quadrature reproduces it
  (ratio at the stop 0.648 to 0.657 from every start).
- APS Physics story v11/st26: a plastic disc spun across a flat surface
  and filmed; "a spinning disk experiences less friction and slides
  farther than a disk without rotation"; curling and shuffleboard named.
- Physics Forums 82514: extend the cup to its apex (a / r = (a + h) /
  R), rim circle radii r1 = sqrt(a^2 + r^2) and r2 = (a + h) r1 / a; the
  circumference goes as 1 / slope.
- Gruiz et al. PDF: binary only (no pdftotext in the shell); the
  closed form h = d / (1 - e^2) from the search results is what the
  script checks.

### Measured candidates (python3, /tmp/day42/research/*.py and *.log)

1. Slide a coaster, spun or not (puck.py, puck.log, puck2.py,
   puck2.log). A 10 cm disc (R 5 cm) with uniform pressure on a table
   with grip 0.3, Coulomb friction integrated over the contact (160 x
   320 polar cells), RK4 at 2e-4 s (half step 1e-4 s identical to 4
   figures). Pushed at 1.0 m/s with no spin: stops at 0.3394 s after
   16.99 cm (closed form v / (mu g) = 0.3399 s, v^2 / (2 mu g) = 16.99
   cm). Pushed at the same 1.0 m/s spinning 40 rad/s (6.37 turns a
   second, rim 2.0 m/s): stops at 0.6462 s after 33.43 cm, 1.967 times
   as far; 40.87 rad/s (6.50 turns/s) gives exactly 2.000 times (33.99
   cm, 0.6554 s); 20 rad/s 21.66 cm (1.275x), 80 rad/s 60.62 cm
   (3.567x). Sliding and spinning end at the same instant from every
   start; v / (R w) runs 0.500 -> 0.552 (0.4 s) -> 0.649 at the stop
   (Farkas 0.653). Friction on the slide at the fixed point F_hat(0.653)
   = 0.616 of mu m g; pure spin T_hat(0) = 2/3 (spin-only stop 0.5094 s
   against the closed form 0.5098 s, moves 0.000 cm). Ic per unit mass
   1.249976e-3 against R^2 / 2 = 1.25e-3. Energy at the start 1.5 J/kg
   (0.5 slide + 1.0 spin), all gone at the stop. Variants: 0.5 m/s 4.25
   against 15.15 cm (3.57x), 1.5 m/s 38.24 against 56.83 cm (1.49x);
   grip 0.15 33.99 against 43.33 cm; a glass base ring (3.0 to 3.5 cm)
   at 20 rad/s 20.85 cm, end ratio 0.93; a 7.5 x 15 cm phone at 20
   rad/s 27.18 cm, end ratio 0.98.
2. Paper cup or straight can (cup.py, cup.log). An 8 oz paper cup (top
   8.0 cm, bottom 5.5 cm, height 9.0 cm, thin wall with a bottom disc)
   beside a straight 8 cm can, both nudged to a centre speed of 0.30
   m/s on a desk, 40 cm from the edge. Closed forms: slant 9.086 cm,
   half-angle 7.907 deg, apex 19.99 cm from the small rim and 29.08 cm
   from the large rim, so the rims run on circles of those radii about
   the apex; the cup turns 1 / sin(alpha) = 7.269 times per lap; the
   centre of mass is 24.05 cm from the apex along the axis (89.0 percent
   of the mass in the wall), circles at radius 23.82 cm at a constant
   3.31 cm height (energy kept), one lap every 4.990 s at 1.259 rad/s;
   the cup spins at 1.443 turns a second. Steady-rolling check from the
   inertia tensor about the apex (surface quadrature, 4000 x 720 cells):
   dL/dt = Omega x L needs the normal resultant at 23.56 cm along the
   contact line, inside the 19.99 to 29.08 cm line (OK); friction needed
   0.0385 of the weight (0.0171 at 0.2 m/s, 0.107 at 0.5 m/s) against
   desk grip 0.5; dL_x and dL_z zero. The can reaches the edge at 1.333 s
   and falls 0.391 s; the cup's rim never gets closer than 10.9 cm to
   the edge (its track reaches 29.08 cm from the start line) and the cup
   is back at its start after 4.990 s. Other cups: 12 oz (9 / 6 / 10 cm)
   rim circle 30.3 cm, 6.74 turns; 4 oz (7 / 5 / 6 cm) 21.3 cm, 6.08
   turns; a 6 cm base 36.2 cm; a 4 cm base 18.4 cm.
3. Icy hill, nose first or reversing (misc.py, misc.log; the run 14
   model). 1,300 kg, wheelbase 2.60 m, 60 / 40 front, CG 0.55 m, grip
   0.3, 10 deg hill: nose first -0.0683 m/s^2, front load 0.556 W, rolls
   back 0.85 m in 5 s with the wheels spinning; reversing +0.1533 m/s^2,
   front load 0.631 W, climbs 1.92 m in 5 s. Steepest hills 9.61 against
   10.88 deg (window 1.27 deg; grip 0.2 6.57 / 7.14, grip 0.4 12.48 /
   14.69). Unchanged from run 14.
4. Tailgating at 100 km/h (misc.py). Lead car brakes at 0.8 g, follower
   the same after a reaction time: a 1 s gap with a 1.0 s reaction stops
   3.9 m short, with a 1.5 s reaction hits at 1.21 s closing at 34 km/h;
   a 2 s gap stops 31.7 / 22.7 m short. The answer flips with the chosen
   reaction time.
5. Ball bouncing down stairs (misc.py). e 0.8, 17 cm steps: the steady
   rebound is 2.435 m/s, apex 30.2 cm above the hit step and 47.2 cm
   above the next (d / (1 - e^2)), a bounce every 0.559 s at 0.501 m/s
   forward; the same ball dropped 47.2 cm on a flat floor is at rest
   after 2.79 s.
6. Runaway car up a hill (misc.py). v^2 / 2g: 50 / 90 / 100 / 130 km/h
   climb 9.83 / 31.86 / 39.34 / 66.48 m of height.
7. Rope trick (misc.py). 500 N sideways on the middle of a 10 m rope,
   car resists 2,000 N: the car moves until the sag is 7.18 deg, 7.91
   cm per pull.
8. Jump in a falling elevator (misc.py). A 10 m fall hits at 14.00 m/s;
   a 3 m/s jump leaves 11.00 m/s, a fall from 6.17 m.
9. Rope or bungee and bosun's chair: re-judged on the docs/niche.md
   numbers; no new script.

### Ranking

Filter as in run 14 (everyday motion, two panels on the same input that
end visibly differently, one plain question, one setup number, one
payoff number, a closed-form check, a loop or repeat, about 25 minutes
with RK4, events, quadrature or closed forms, no PDE, no fluid grid, no
fitted aerodynamics, no rider or posture models, no chosen material
strengths, no siblings of produced shorts).

1. Slide a coaster, spun or not (accepted, slot 1). Twice as far (34
   against 17 cm) from the same push, both motions stopping at the same
   instant, a published fixed point (0.653) the quadrature reproduces;
   an everyday object (coaster, puck, glass on a bar); a new mechanism
   for the channel (friction shared between two motions). The build is
   a contact quadrature plus RK4, about 30 minutes.
2. Paper cup or straight can (accepted, slot 2). The can is off the
   desk at 1.33 s, the cup circles and is back in 4.99 s after exactly
   1 / sin(alpha) = 7.27 turns; exact geometry, a natural loop, an
   everyday object. The pencil short (rolls off against stops, 3 views
   on day one) is the nearest produced short, but the mechanism here is
   geometry, not corner losses, and the cup comes back.
3. Icy hill, nose first or reversing (accepted, slot 3; was rank 4 in
   run 14). Rolls back against climbs, a live Car Talk debate, cars
   among the strongest recent shorts; the window is 1.27 deg on four
   chosen numbers, so the narration states grip and slope. Beats rope
   or bungee (rank 5) and bosun's chair (rank 6) today.
4. Ball bouncing down stairs (backlog, low). Bounces for ever at 47 cm
   against at rest in 2.79 s on the flat; a clear yes-or-no, but a
   sibling of the Zeno bounce and the bounce down a slope, and the
   restitution is chosen.
5. Runaway car up a hill (backlog, low). 100 km/h is a 39 m hill; a
   one-number conversion and a cousin of "which climbs higher".
6. Rope or bungee (backlog, stays rank 5 of run 13) and bosun's chair
   (stays rank 6).
7. Tailgating (rejected): kinematics only and the hit-or-stop answer
   flips with the chosen reaction time.
8. Rope trick (rejected): static, the car moves 8 cm per pull.
9. Jump in a falling elevator (rejected): a rate payoff on a human
   model.
10. Ball on a lazy Susan (rejected before measuring): sibling of the
    produced turntable ball.
11. SUV or sports car rollover (rejected without a script): an
    untripped roll needs grip above the stability factor, which real
    roads rarely give, so the pair would be contrived.
12. Marble in an upside-down glass (rejected): 3D rolling inside a
    cylinder, a build well past 25 minutes.

Tall glass or short glass still waits until about 2026-10-14. Nothing
in this run showed a queued idea weak or saturated beyond its notes.

### Files changed

- docs/niche.md: appended "Added by trend research 2026-10-10 (evidence
  in task 20261010-100329; ...)" with four bullets: Slide a coaster
  spun or not, Paper cup or straight can, Ball bouncing down stairs,
  Runaway car up a hill. No other bullet changed.
- tasks/20261010-100329/TASK.md (this file).
- No web/data change, no production, no upload, no commit in this run.
