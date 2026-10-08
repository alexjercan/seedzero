# Research trends: run 14 for the day 40 slate and the backlog

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: backlog

## Goal

Fourteenth research-trends run, 2026-10-08 from about 10:10 EEST, for
all three slots of day 40 and the backlog. The backlog in `docs/niche.md`
holds twenty-one unproduced ideas. The day 39 close judged most of them
weak for a first pick: space time-lapses and counters (Kelvin wake,
Collatz, secretary problem, rogue wave, Saturn retrograde, Halley, L2
drift), low-ranked ideas (corner reflector, basketball arc, Moon clock,
sliding ladder, falling chimney, two springs stacked or side by side,
stick or string, train wheel backward, fridge tip with a broken model), a
tie payoff (bathtub drain) and a heavy build (dam break). Three ideas from
research run 13 remain: tall glass or short glass (rank 4, but it is a
tray sibling of the marble-or-dice short published 2026-10-07, so it must
wait about a week: do not pick it today), rope or bungee (rank 5) and
bosun's chair (rank 6). Find 6 to 9 new candidates that fit the winning
format: continuous tabletop or everyday motion, two panels on the same
input that end visibly differently on a phone screen, one plain question
in the first two seconds, one setup number, one payoff number, a
closed-form check, a loop or a repeat, and a build of about 25 minutes
with RK4, event-driven steps or closed forms (no PDE, no fluid grid, no
ray tracing, no fitted aerodynamics, no rider or posture models, no
chosen material strengths). Avoid siblings of produced shorts (read the
[produced ...] notes in docs/niche.md: drops beside a ball, Atwood,
yo-yo, chain off a desk, capstan, coin on a record, river crossing, kerb
hop, carried pendulum, balloon in a car, belt, broom, bat, strings,
spool, cue ball, tablecloth, brake or swerve, ice cube against ball,
bucket, swing, spring drop, hoop bead, gyro top, Kapitza, resonance,
metronomes, block on a wedge, spinning glass, cart on a ramp, push or
pull a crate, marble on rails, fingers under a ruler, tilting tray,
boat jump, banked curve). Re-judge rope or bungee and bosun's chair
against the new candidates; either may take a slot today if it beats
them. Measure every survivor with a throwaway script in
/tmp/day40/research/ (g = 9.807, python3 via `nix develop -c python3`)
and check the model (contact forces positive, no-slip friction available
with the minimum mu stated, energy kept where it should be, panels
visibly different at 1080x1920). Rank the survivors and name the best
three for today's three slots with their numbers, question, setup and
payoff numbers and a drawing sketch each in the style of the day 39
briefs (read tasks/20261007-102009/TASK.md "Goal" for the brief style and
tasks/20261007-100305/TASK.md for the evidence style). No production in
this run.

Channel results to weigh (views after a few days): the strongest recent
shorts were "which lands first" drops (chain against ball 990), "which
climbs higher" (973), the balloon in a car (943), the spring squash
(929), the cut shot (950), brake or swerve (734), the stick on ice (619);
weak ones were the peg swing (86), the low cue ball (81), the carried
pendulum (75), the spinning glass (5), the push-or-pull crate (13) and
the fingers under a ruler (29). Everyday objects a viewer owns beat lab
props; a visible yes-or-no ending beats a rate difference.

Rules for this run: follow the research-trends skill (five to ten
focused queries, WebSearch and WebFetch). Append the survivors to
docs/niche.md at the very end of the file under a new paragraph "Added by
trend research 2026-10-08 (evidence in task 20261008-100401; selection favoured
...)" in the existing one-line bullet format; re-read the file right
before editing and append only. Record the evidence in this task file
(queries, URLs, what each showed, why each idea was accepted or rejected,
the measurement logs) under "## Evidence". Do not edit web/data/ (the
orchestrator appends the journal entry from your report), do not run
git, do not produce anything, do not spawn subagents, never use sleep in
Bash. Finish by reporting: the ranked survivors with their numbers, the
recommended three slot ideas each with a full brief paragraph, the
docs/niche.md lines you added, and a one-paragraph journal line for
web/data/log.jsonl.

## Evidence

Research ran 2026-10-08 from about 10:10 EEST. Throwaway scripts and
logs in /tmp/day40/research/ (one per candidate, g 9.807, python3 via
nix develop). No production, no git, no web/data change in this run.

### Queries (9 WebSearch, 5 WebFetch)

1. "tumbling toast butter side down physics Matthews table height swipe
   fast lands butter up". Showed Bacon, Heald and James (AJP 69, 38,
   2001), Matthews (Eur J Phys 1995, Ig Nobel 1996), Mahajan "Toast
   sliding off a table" (AJP 90, 727, 2022), Science Buddies, Wikipedia
   and a Boing Boing piece from 2026-07-29: a famous myth with live
   coverage this year; a 76 cm table gives about half a turn; a table
   over about 3 m gives a full turn.
   https://en.wikipedia.org/wiki/Buttered_toast_phenomenon
   https://boingboing.net/2026/07/29/buttered-toast-phenomenon.html
2. "book stacking overhang harmonic series top book completely past
   table edge four books demonstration". Showed MathWorld, Wikipedia
   block-stacking, Math Lair, Physics Forums, MIT 6.042 notes: the
   overhang of n books is H_n / 2 book lengths; four books (25/24) put
   the top book wholly past the edge.
   https://mathworld.wolfram.com/BookStackingProblem.html
   https://en.wikipedia.org/wiki/Block-stacking_problem
3. "front wheel drive vs rear wheel drive icy hill weight transfer
   physics which climbs better". Showed Edmunds, a Car Talk thread
   "The snow driving uphill in reverse debacle: myth or fact?", Quora
   and several winter-driving pages: FWD versus RWD and "reverse up the
   hill" are live everyday debates; the pages contradict each other on
   which way the load moves.
   https://community.cartalk.com/t/the-snow-driving-uphill-in-reverse-debacle-myth-or-fact/60728
4. ""Toast sliding off a table" American Journal of Physics 2022
   abstract speed butter". Showed Mahajan's paper (MIT DSpace,
   ResearchGate, AIP) and the "Falling toast" follow-up (AJP 90, 808):
   a thin uniform ruler sliding off the corner under gravity and the
   normal force only; "as the initial speed increases ... the toast
   rotates through a smaller angle ... more likely to land butter side
   up".
   https://pubs.aip.org/aapt/ajp/article/90/10/727/2820262/Toast-sliding-off-a-table
5. "ladder safety 4 to 1 rule 75 degrees ladder slips at base climber
   halfway friction coefficient physics". Showed HSE/OSHA 4:1 pages, an
   ASSE paper on required friction, ladder angle calculators: 75.96 deg
   rule, slide-out below about 70 deg; no climber-height number given.
   https://aeasseincludes.assp.org/professionalsafety/pastissues/050/09/010905as.pdf
6. "Lewis Carroll monkey and weight puzzle rope over pulley monkey
   climbs what happens to the weight answer". Showed Numericana,
   Futility Closet, the Cyclopedia of Puzzles and Physics Forums: the
   weight rises with the monkey, always face to face; Carroll's
   correspondents gave four different answers.
   http://www.numericana.com/answer/physics.htm
7. "viral physics debate October 2026 shorts "which one" everyday
   experiment". Showed the fluxnote list, Physics World on viral
   experiments and generic "experiments that look fake" shorts: no
   specific peg this week.
   https://physicsworld.com/a/what-makes-a-physics-experiment-go-viral/
8. "moving walkway puzzle tie your shoe on the walkway or off it which
   gets you there sooner". Showed Terry Tao's 2008 airport puzzle post
   and a 2025 essay: tie it on the walkway, always.
   https://terrytao.wordpress.com/2008/12/09/an-airport-inspired-puzzle/
9. "swing ride chair empty vs full same angle conical pendulum mass
   independent wave swinger physics question". Showed Wikipedia, physics
   lesson pages: the angle does not depend on the rider's mass (a tie).
   https://en.wikipedia.org/wiki/Conical_pendulum

### Sources (fetched pages)

- Bacon, Heald and James, AJP 69, 38 (2001), UMD copy
  (https://physics.umd.edu/courses/Phys405/Hill/Fall05/Information/AJP/AJP00038.pdf),
  text via pdftotext: board 10.2 x 10.8 x 1.3 cm, grip mu_s 0.32 and
  mu_k 0.24 measured, table 76 cm; slipping at the edge "plays an
  essential role"; from rest a thick board lands butter down for
  overhangs 0 to 0.8 and 2.7 to 5.1 cm; a thin plate (Matthews) rotates
  less than 270 deg. This run models a thin toast sliding off at a
  speed, Mahajan's case, and checks the result with Bacon's grips.
- Mahajan AJP 2022: AIP returned 403, MIT DSpace 405, ResearchGate 403;
  the model and the speed trend come from the search abstract (query 4).
- Car Talk thread: the posters treat "back up the hill in a FWD car" as
  fact (Camry, Cavalier reports); the reason given is load moving onto
  the front axle when the car pulls backward up the slope.

### Measured candidates (python3, /tmp/day40/research/*.py and *.log)

1. Toast: nudged or swiped (toast.py, toast.log, toast_energy.py,
   toast_energy.log). Thin uniform toast 10 cm (I = m a^2 / 3, a 5 cm),
   75 cm table, contact at the table corner with the normal force
   square to the toast; frictionless corner (Mahajan) and Bacon's grips
   0.32 / 0.24 with stick then slip; leaves when the corner force
   reaches zero or the back end passes the corner, then free flight to
   the first floor touch; butter down when cos(angle) < 0. RK4 dt 1e-5
   s. Nudged at 0.05 m/s: leaves after 193.2 ms tilted 38.81 deg at
   8.89 rad/s (1.41 rev/s), falls 0.3386 s, touches the floor turned
   211.22 deg: butter DOWN, 8.7 cm out. Swiped at 1.5 m/s: leaves after
   33.3 ms at 2.46 deg, 2.45 rad/s (0.39 rev/s), falls 0.3614 s, turned
   53.12 deg: butter UP, 59.2 cm out (2.0 m/s: 40.16 deg, 78.7 cm). The
   face flips at 0.87 m/s (frictionless) and 0.92 m/s (grips 0.32 /
   0.24); 12 cm toast 0.85 and 0.91 m/s. With grips the nudge lands at
   178.70 deg and the swipe at 54.14 deg, so the faces do not depend on
   the grip. Every speed from 0 to 0.80 m/s lands butter down (123 to
   249 deg), 1.0 m/s and up butter up. Corner force at or above zero
   until the leave (detection tolerance -0.001 g); frictionless energy
   drift 2.9e-15 J/kg.
2. Five books past the table edge (books.py, books.log, books5.py,
   books5.log, books_tip.py, books_tip.log). Books 20 cm long, 3 cm
   thick, stacked bottom up. Exact maximum for n books H_n / 2 lengths:
   4 books 25/24 = 1.0417 (20.83 cm, top book 0.83 cm clear), 5 books
   137/120 = 1.1417 (22.83 cm, 2.83 cm clear). Shrinking steps 1.9 /
   2.4 / 3.2 / 4.9 / 9.8 cm (each 1 to 2 mm under the 1/10, 1/8, 1/6,
   1/4, 1/2 limits): holds at every book, worst margin +0.200 cm, the
   top book's end 22.20 cm out and its back end 2.20 cm past the table
   edge. Equal steps of the same 22.2 cm / 5 = 4.44 cm: books 1 to 3
   hold (margin 1.12 cm), book 4 tips the stack (CG 1.10 cm past the
   edge; equal steps d fall at book n once d > L / (n + 1), 4.00 cm for
   book 4). Drawn as one rigid piece about the table edge: pivots 0.335
   s to 51.5 deg (grip 0.3) or 0.348 s to 57.6 deg (grip 0.5), then
   slides off. Four books: shrinking steps clear by only 0.4 cm, so use
   five.
3. Round or hexagonal pencil (pencil.py, pencil.log). 7.0 mm pencils on
   a flat desk, the same 0.15 m/s nudge. Hex prism, R 4.04 mm, I_cm =
   5/12 m R^2, I_corner = 17/12 m R^2; each corner impact keeps 11/17 =
   0.6471 of the spin (0.4187 of the energy); passing a corner needs
   21.43 rad/s (CG 0.0866 m/s); the corner stays loaded below 45.85
   rad/s (CG 0.185 m/s), so nudges stay under 0.185 m/s. At 0.15 m/s
   (37.1 rad/s) the hex rolls 2 faces, 8.1 mm in 0.102 s, then rocks
   about 11 times and stops; 0.10 / 0.12 / 0.18 m/s give 1 / 1 / 2
   faces. The round pencil (no rolling loss, stated) keeps 0.15 m/s and
   covers 25 cm in 1.67 s (30 cm in 2.00 s), falls 0.391 s from a 75 cm
   desk. A hex pencil tips from rest only on a desk tilted past 30 deg.
4. FWD car up an icy hill, nose first or reversing (fwd.py, fwd.log).
   1,300 kg, wheelbase 2.60 m, 60 / 40 front, CG 0.55 m high, traction
   mu N on the front axle, load moved by the slope and the
   acceleration. Steepest hill: nose first tan = mu b / (L + mu h),
   reversing tan = mu b / (L - mu h); grip 0.3: 9.607 against 10.879
   deg (RWD 7.30, AWD 16.70); grip 0.2: 6.57 against 7.14; 0.4: 12.48
   against 14.69. On a 10 deg hill with grip 0.3 the nose-first car's
   wheels spin and it rolls back 0.85 m in 5 s (-0.068 m/s^2, front load
   0.556 W), the reversing car climbs 1.92 m in 5 s (0.153 m/s^2, front
   load 0.631 W).
5. Ladder at 75 or 60 deg (ladder.py, ladder.log). 4 m, 12 kg ladder,
   80 kg climber as a point mass, smooth wall, floor grip 0.3. 75 deg
   needs grip 0.250 at the top and holds; 60 deg needs 0.540 and slips
   with the climber 2.09 m up the ladder (52 percent, 1.81 m high); 70
   deg slips at 3.49 m. Slide dynamics from the slip point: leaves the
   wall after 3.37 s at 29.7 deg (slow start from equilibrium).
6. Monkey and weight (monkey.py, monkey.log). Rope over a light pulley,
   10 kg monkey and 10 kg weight, the monkey pulls in rope at 0.5 m/s:
   both rise 0.25 m/s side by side and reach a pulley 3 m up together in
   12.0 s; on a rope tied to the ceiling 6.0 s. A 5 kg weight
   accelerates up at 3.27 m/s^2, 12 kg down at 0.89.
7. Shoe on the walkway (walkway.py, walkway.log). Walk 1.4 m/s,
   walkway 0.7 m/s, 20 s tie: tying on the walkway saves v T / (w + v) =
   6.667 s, 9.33 m ahead.
8. Swing ride, empty or full: closed form only, tan(angle) = w^2 r / g
   with no mass; the panels end the same.
9. Rope or bungee and bosun's chair: re-judged on the numbers in
   docs/niche.md (hop 19.1 cm every 3.82 s against a creep; nothing
   moves against 2.89 m in 2 s); no new script.

### Ranking

Filter: continuous tabletop or everyday motion, two panels on the same
input that end visibly differently on a phone, one plain question, one
setup number, one payoff number, a closed-form check, a loop or
repeat, about 25 minutes with RK4, events or closed forms, no PDE, no
fluid grid, no fitted aerodynamics, no rider or posture models, no
chosen material strengths, no siblings of produced shorts.

1. Toast, nudged or swiped (accepted, slot 1). Butter down at 211 deg
   against butter up at 53 deg; a famous everyday myth with a 2026
   news peg; the face does not depend on the grip or the toast length;
   corner force and energy checks hold; yes-or-no ending in yellow
   butter. Not a sibling: the hinged stick and the broom fall about a
   fixed pivot, this slides off a corner and lands.
2. Five books past the table edge (accepted, slot 2). Shrinking steps
   hold with the top book 2.2 cm clear of the table; equal steps fall
   at book 4; exact H_n / 2; everyday objects; the build-up is a natural
   repeat. Not a sibling of the fingers under a ruler (that slid to the
   balance point; this stacks balance points).
3. Round or hexagonal pencil (accepted, slot 3). Off the desk against
   8.1 mm and stopped; exact 11/17 per corner; everyday object; the
   pencil is small, so each band needs a magnified cross-section inset.
   Not a sibling of the rolling race (that compared round shapes).
4. FWD up an icy hill, nose first or reversing (accepted, rank 4). A
   live road debate, visible yes-or-no, but the window is 1.3 deg wide
   and rests on four chosen numbers (grip, CG height, split, slope);
   the climb is slow (1.9 m in 5 s). Strong alternate for a road slot.
5. Rope or bungee (backlog, stays rank 5). Same numbers; the stick-slip
   mechanism carried the fingers short (29 views).
6. Ladder at 75 or 60 deg (accepted, rank 6). Slips with the climber
   halfway up against holds to the top; the shallow-ladder answer is
   expected, the grip is chosen and the climber is a point mass.
7. Bosun's chair (backlog, stays rank 7). Chosen pull, pulley cousin
   of the Atwood drop.
8. Monkey and weight (accepted, rank 8). They rise face to face; a lab
   prop and a pulley sibling of the Atwood drop and bosun's chair.
9. Shoe on the walkway (rejected): a kinematics puzzle, two walkers
   and a 9.3 m gap, no physics on screen.
10. Swing ride (rejected): a tie, both chairs at the same angle.

Tall glass or short glass stays at rank 4 of run 13 and waits until
about 2026-10-14 (tray sibling). Queued backlog ideas: nothing in this
run showed a queued idea weak or saturated beyond its notes; no notes
added.

### Files changed

- docs/niche.md: appended "Added by trend research 2026-10-08 (evidence
  in task 20261008-100401; ...)" with six bullets: Toast nudged or
  swiped, Books past the table edge, Round or hexagonal pencil, Front
  drive up an icy hill, Ladder at 75 or 60 degrees, Monkey and weight.
  No other bullet changed.
- tasks/20261008-100401/TASK.md (this file).
- No web/data change, no production, no upload, no commit in this run.
