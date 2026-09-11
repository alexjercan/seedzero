# Niche: simulation-driven science shorts

One deterministic simulation per short. One measured, surprising claim.
Seed on screen.

## Why this niche

- The agent's real strength is writing correct code and verifying claims by
  computation. This niche turns that strength into the content itself.
- Accuracy is structural, not editorial: the render and the claim come from
  the same program, so the footage cannot contradict the narration.
- Zero copyright exposure: no gameplay, no stock, no licensed music.
- Competitors in this space either post raw sims with no story, or stories
  with no verification. The measured-claim framing is the gap.

## Audience

- STEM-curious viewers, roughly 16 to 35, watching the Shorts feed.
- They reward: a hook already in motion, one concrete number, a payoff they
  can screenshot, and clean loops that trigger replays.
- They punish: slow intros, vague claims ("scientists say"), and text walls.
- Behavior is near-identical on TikTok and IG Reels; the same vertical file
  reuses there without edits if those platforms are granted later.
- Comments will try to nerd-snipe the claim. That is good. Reproducibility
  (seed on screen, code in a public repo eventually) turns pedants into
  evangelists.

## Content pillars

1. **Probability paradoxes.** Monty Hall as a ten-thousand-door race. The
   birthday paradox as a filling grid. The Galton board burying its edges.
   Gambler's ruin. The inspection paradox with buses.
2. **Chaos and physics.** Double pendulum divergence from a hair-width
   nudge. Three-body orbits. Resonance building until failure [produced
   2026-09-04: 1 mm shake, damping ratio 0.004; on tempo the stretch
   grows about 3 mm a push and snaps the 60 mm limit at push 27, 3%
   faster peaks at 29.1 mm on push 16 and never reaches 30 mm in 618
   pushes]. Billiards in stadium versus circle tables.
3. **Emergence.** Boids from three rules. Traffic jams from nothing.
   Segregation from tiny preferences (Schelling). Ant trails [in the backlog 2026-09-09 as the
   double bridge]. Conway life guns.
4. **Algorithms in motion.** Sorting races with honest operation counts.
   Pathfinding A* versus BFS flood. Epidemic spread on networks. Hash
   collisions filling a table [in the backlog 2026-09-09 as parking-lot
   probing].

## Claim style

Bad: "The double pendulum is chaotic."
Good: "These two pendulums started one thousandth of a degree apart. At
eight point two seconds they are on opposite sides of the screen."

The good version names the initial difference, the measured divergence time,
and both are printed by the sim.

Framing rules (2026-09-09, from viewer feedback and the retention curves)
live in `docs/vision.md`: one plain question in the first two seconds, one
setup number, one payoff number that answers the question, narration tied
to the one thing moving on screen.

## Pilot slate (first four)

1. Galton board: twelve rows of pegs, ten thousand balls; center bin beats
   the edge bin by nine hundred twenty four to one. [produced]
2. Double pendulum: two runs, one thousandth of a degree apart; measure the
   time to full divergence. [produced]
3. Monty Hall: ten thousand simultaneous games as two racing bars; switching
   wins about two thirds. [produced]
4. Boids: three rules on screen as toggles; flocking appears and collapses
   as rules toggle off and on. Research 2026-08-30: also measure flock
   polarization each frame and narrate the tick the scatter snaps into
   alignment; answers "how do flocks work with no leader". [produced]

## Backlog

Each idea must yield one measurable surprise before it earns a slot.

- Birthday paradox: a grid of fifty rooms of twenty three people fills;
  count how many rooms hold a shared birthday (expect about half).
  Research 2026-08-30: demand validated; ten thousand rooms gives a
  sharper count (expect near five thousand seventy). [produced
  2026-09-07 as two panels on the same 10,000 rooms at seed 0: someone
  shares your birthday in 569 rooms (exact 5.86%), any two share one in
  4,922 (exact 50.73%), 22 comparisons against 253 pairs; the top room
  keeps filling and reaches a coin flip on your own birthday at 253
  people, 4,986 rooms; 100,000-room check at seed 1 gives 6.00% and
  50.65%]
- Gambler's ruin: a fair coin, one player has ten times the bankroll;
  measure how often the small stack survives. [produced 2026-09-06: 10
  chips against 100, 10,000 games per panel at seed 0 on the same draws;
  the fair coin let 866 break the house (exact 9.09%), the 49% coin 64
  (exact 0.61%), 13.5 to 1; average game 950 and 462 flips]
- Inspection paradox with buses (pillar idea): the same passengers and
  the same number of buses, on tempo versus at random moments; measure
  the average wait. [produced 2026-09-06: 1,008 buses a week, 10,000
  passengers, seed 0; on tempo the average wait is 4.97 min, at random
  10.02 (exact 5.00 and 9.99); the gap around a passenger is 10.0 versus
  19.9 min; 3,776 waited over 10 min at random, none on tempo; longest
  66 min]
- Schelling segregation: agents needing only thirty percent same-color
  neighbors; measure final segregation percentage. [produced 2026-09-02:
  seed 0, 100 by 100, ten percent empty; asking for 30% alike settles at
  75.9% alike after 16 rounds and 3,780 moves]
- Traffic jam from nothing: a ring road, one braking car; measure the
  backward wave speed of the phantom jam. Research 2026-08-30: use the
  Sugiyama twenty two car ring with no obstacle at all; expect the wave
  to roll backward near twenty km/h. [produced 2026-09-02: the optimal
  velocity model let cars overlap, so the short uses the Intelligent
  Driver Model; 22 cars at 50 km/h desired speed jam at 52 s and the jam
  rolls backward at 6.0 km/h, far below the twenty the research guessed]
- Sorting race: quicksort versus bubble sort on the same shuffled array
  with honest comparison counters. Research 2026-08-30: demand validated
  ("fastest sorting algorithm" is a recurring search); expect a ratio
  above twenty to one on five hundred twelve bars. [produced 2026-08-31,
  measured 29.3 to 1]
- A-star versus BFS: same maze, count the cells each one touches.
  [produced 2026-09-01: a perfect maze gives no story (1.03 to 1); use
  rectangular wall blocks and the prefer-higher-g tie break, measured
  26.4 to 1]
- Epidemic threshold: same virus, contact rate just below versus just
  above the threshold; measure final infected counts. [produced
  2026-09-05: SIR on a 200 by 200 grid town, seed 0, same 10 first
  cases, 5% per contact, 2 sick days; 11 contacts a day dies on day 50
  at 225 cases (realised R 0.93 over the first 100 cases), 13 a day
  burns out on day 255 at 11,397 cases (R 1.19), 50.7 to 1; over 300
  seeds 11 takes off in 6% of runs and 13 in 97%]
- Conway glider gun: count cells alive over time; a machine from four
  rules. [produced 2026-09-03: the Gosper gun fires one glider every 30
  generations exactly; at generation 1,500 it has launched 50 and 286
  cells are alive, and the count grows by exactly 5 every 30
  generations over the whole run]
- Buffon's needle: estimate pi by dropping ten thousand needles; show the
  estimate converge on screen. [produced 2026-09-07: 10,000 sticks
  tumble onto boards one stick wide at seed 0; 6,350 cross a line
  (exact 2/pi = 63.66%), estimate 3.1496, off by 0.26%; a million sticks
  at seed 1 give 3.1400; over 1,000 seeds the 10,000-stick estimate has
  sd 0.024, so ten thousand sticks buy two digits and a million three]
- Random walk versus drunk walk home: measure return-to-origin times in
  one and two dimensions. [produced 2026-09-05: 10,000 walkers each,
  seed 0, 2,000 steps; on the line 5,053 are home by step 2 and 9,793
  by step 2,000 (207 still out, exact expectation 178); on the plane
  2,480 by step 2 and 6,987 by step 2,000 (3,013 still out, 14.6x);
  three dimensions, not narrated: 3,335 home by step 2,000]
- Three-body figure eight: the periodic solution, then nudge it; measure
  how long the choreography survives. [produced 2026-09-01: survival time
  is not step-independent, so the claim became the linear growth law,
  482x the nudge over forty laps]
- Coupon collector: how many packs to complete a fifty-sticker album;
  measure the expected long tail. [produced 2026-09-08: 50 stickers, one
  random sticker per pack at seed 0; the first 40 took 64 packs, the
  last 10 took 136, complete after 200 with 150 doubles; 10,000 albums
  took 224.7 packs on average (exact 224.96), the last 10 cost more than
  the first 40 in 90.2% of them and 10.8% needed over 300]
- Benford's law: leading digits of powers of two; count the ones versus
  the nines. [produced 2026-09-08: two panels take the same steps,
  counting up versus doubling, leading digits drop into bins; after
  1,000 steps counting gives 112 ones and 111 nines, doubling gives 301
  and 45 (Benford exact 301.0 and 45.8); after 10,000 steps 3,010 and
  458; exact integers, no seed]
- Percolation: grid fills randomly; measure the sharp threshold where a
  path suddenly connects. [produced 2026-09-02: 1,000 grids of 100 by 100
  connect at 59.26% filled on average against the 59.27% theory; seed 0
  connects at 61.4%]
- Stadium versus circle billiards (pillar idea): two balls one
  thousandth of a degree apart on each table; measure the split.
  [produced 2026-09-03: event-driven, no time step; the round table
  keeps every hit at 69.6 degrees and the gap under 0.13 mm for 43 s,
  the stadium is 1 cm apart at 9.02 s, 1 m at 17.45 s, widest 1.79 m]

Added by trend research 2026-08-30 (evidence in task 20260830-222119):

- Pendulum wave: thirty pendulums with tuned lengths scatter into
  apparent chaos, then snap back into a perfect line; measure the exact
  realignment period and make the last frame equal the first for a
  seamless loop. [produced 2026-08-31, measured 30.0 s]
- Streak test: ten thousand seeded runs of one hundred coin flips;
  measure how many contain a streak of six or more (expect nearly all;
  corrects the gambler's fallacy "due for tails" intuition). [produced
  2026-09-08: two coins on the same seed-0 draws, one fair and one never
  allowed past three in a row; 8,102 of 10,000 fair runs hold 6+ (exact
  80.7%), 5,443 hold 7+, 879 hold 10+, longest streak 21; seed 1 gives
  8,029; the capped coin never streaks and it is the fake]
- Seven shuffles: riffle shuffle thousands of decks one to ten times; a
  card guesser plays each deck and measures its edge over chance, which
  survives four shuffles and dies near seven. [produced 2026-09-06:
  10,000 decks per row at seed 0; a guesser that knows the factory order
  names 31.2 of 52 after one riffle, then 19.7, 12.9, 8.8, 6.6, 5.5 and
  5.0 after two to seven; a random deck gives 4.5, pure chance; the edge
  roughly halves per riffle; exact total variation 0.924 after five
  riffles, 0.334 after seven]
- Busy beaver: run the five-state busy beaver champion machine to its
  halt as a scrolling tape; count every step, exactly 47,176,870 from
  five states (peg: ninety years of Turing's 1936 paper, window through
  December 2026). [produced 2026-09-03: exact run halts at step
  47,176,870 with 4,098 ones; the tape spans 100 cells at step 2,670,
  1,000 at 284,475, 10,000 at 25,615,315]
- Coin flip for a million: ten thousand players choose fifty thousand
  sure versus a coin flip for a million; expected value says flip, yet
  measure how many flippers walk away with nothing (peg: viral poll,
  publish by mid September 2026). [produced 2026-09-01: the one-shot
  version surprises nobody (5,064 of 10,000 keep the million), so the
  short repeats the bet; zero of ten thousand left at round thirteen]
- Random versus balanced: ten thousand items signed plus or minus by
  coin flip versus a greedy balancing rule; measure the random drift
  near one hundred against the balanced drift near three (peg:
  discrepancy breakthrough coverage, August 2026). [produced 2026-09-07
  as balls into bins: the scalar greedy rule never drifts past one, so
  the short uses the power of two choices; 10,000 balls into 100 bins at
  seed 0 on the same first pick, random stacks 78 to 134 (gap 56) against
  98 to 102 (gap 4) when each ball takes the emptier of two bins; the
  second look changed the pick 3,490 times; at 100,000 balls the gaps
  are 135 and 5]
- Golden angle: place one thousand seeds at the golden angle, then a
  tenth of a degree off; measure how far packing efficiency collapses
  and count the spiral arms that appear (peg: Fibonacci Day,
  2026-11-23). [produced 2026-09-04: packing efficiency is a weak
  claim (the biggest gap grows only 1.32x), so the short counts
  touching seeds: the golden angle keeps 0 of 1,000 seeds touching,
  closest pair 1.60 seed widths; +0.1 deg has 658 touching in exactly
  34 arms, first touch at seed 377, 34 arms from seed 410]
- Pi race: Leibniz versus Ramanujan series with digits locking in on
  screen; measure terms needed for seven correct digits, about five
  million versus two (peg: Ramanujan's birthday, 2026-12-22). [produced
  2026-09-04: the guess was wrong both ways; with exact arithmetic
  Leibniz's seventh digit locks at term 2,886,750 (error about 1/N) and
  Ramanujan has 7 digits after 1 term, 16 after 2]
- Best of seven: one hundred thousand series where the better team wins
  each game fifty five percent of the time; measure how often it wins
  the series (expect near sixty percent; peg: playoff season,
  September and October). [produced 2026-09-05: 100,000 series at seed
  0, the better team won 60,721 = 60.7% (exact 60.83%); 30,456 went to
  a game seven and it won 54.9% of those; nine in ten needs a best of
  163, ninety nine in a hundred a best of 539]

Added by trend research 2026-09-09 (evidence in task 20260909-083310;
selection favoured continuous physical motion, two-panel same-input
comparisons, one plain question per short, and seamless loops where the
physics is periodic):

- Tautochrone bowl: five balls released from five heights in a circular
  bowl versus a cycloid bowl; measure the arrival-time spread and each
  ball's period; expect 0.000 s and equal periods on the cycloid against
  a spread that grows every swing in the circle; the cycloid panel is
  exactly periodic, so the last frame equals the first. [produced
  2026-09-09: five balls at 20 to 100 percent of the depth in a round
  bowl against a cycloid of the same depth; round periods 1.452 to 1.669
  s, spread 0.054 s at the first crossing, 3.209 s at crossing 30, 4.297
  s at 40; cycloid period 2.000 s for every ball, spread 0.000 s at all
  40 crossings; 20 exact periods in 40 s so the video loops;
  deterministic, no seed]
- Brachistochrone race: straight, circular-arc and cycloid tracks from
  the same start to the same end; measure the arrival times and track
  lengths; expect the longest track (the cycloid) to win by about
  eighteen percent over the straight line.
  [produced 2026-09-10: bead on a wire, no friction, start (0, 0) to
  end (pi a, -2a) with a 0.994 m so the cycloid takes 1.0000 s; cycloid
  3.976 m in 1.0000 s, straight line 3.702 m in 1.1854 s, gentle
  circular arc 3.760 m in 1.5030 s; arcs of 45/60/75/90 deg 1.083,
  1.022, 1.005, 1.025 s; five races of 8 s at quarter speed loop;
  deterministic, no seed]
- Dzhanibekov flip: a 1:2:3 box in zero g spun about the intermediate
  axis versus the long axis with the same 0.001 rad/s wobble; measure
  the first flip time, the flip period and the count of flips in forty
  seconds, with the long axis never flipping; check energy and angular
  momentum to 1e-10 (peg: Nobel week, physics prize 2026-10-06).
  [produced 2026-09-09: a 1 x 2 x 3 brick at one turn per second with a
  0.001 rad/s wobble; long axis 0 flips, tilt under 0.032 deg; middle
  axis 6 flips at 3.04, 9.85, 16.66, 23.47, 30.28, 37.09 s, one every
  6.810 s; energy and angular momentum drift under 1e-12; thin axis also
  steady; deterministic, no seed]
- Magnetic pendulum: two bobs released a tenth of a millimetre apart over
  three magnets; measure the time they separate by a bob width and the
  final magnet of each; plus a grid of releases counting the share whose
  one-pixel neighbour ends at a different magnet (expect a large share).
  [produced 2026-09-10: 1 m string, drag 0.3/s, three magnets 6 cm out at
  90/210/330 deg, bob 3 cm above them, strength 0.006 m^3/s^2, RK4 at
  1200 steps/s; released at (-0.05, 7.95) cm and 0.1 mm to the right;
  gap passes one bob width (10 mm) at 1.071 s and 100 mm at 3.29 s;
  white bob settles over purple at 7.85 s, gold over red at 7.96 s; 200
  x 200 release map: 41.7% of points end at a different magnet from the
  neighbour 1 mm to the right, 26.9% from 0.1 mm; 2400 steps/s agrees;
  two drops of 22 s at half speed loop; deterministic, no seed]
- Kapitza pendulum: the same inverted pendulum with the same 0.001 rad
  nudge, pivot still versus pivot shaking 2 cm at 30 Hz; measure the fall
  time of the still one and the maximum tilt of the shaken one over ten
  minutes (expect it never falls; stability 3.77 against a threshold of
  1.40).
  [produced 2026-09-10: 10 cm pendulum, air drag 0.2/s, pivot stroke 1 cm
  each way at 40 Hz (stability 1.79 against the threshold), nudge 0.5
  rad/s at 2.5 s; still pivot falls past 90 deg 0.427 s after the nudge; shaking pivot peaks at 2.35 deg and wobbles with a
  0.423 s period; a 6 rad/s kick at 15 s swings it out to 28.5 deg and
  it is back under 5 deg 0.09 s later; shaking stopped at 29 s, it falls
  in 0.429 s; a 600 s run never fell; stroke 0.3 cm falls in 0.474 s;
  deterministic, no seed]
- Lorenz forecast horizon: nudge the Lorenz system by 1e-3, 1e-6 and 1e-9;
  measure the time to disagree by one unit; expect about 7.6, 15.3 and
  22.9, so every thousandfold gain in precision buys the same 7.6.
  [produced 2026-09-11: three copies nudged by 1e-3, 1e-6 and 1e-9 split
  from the reference by one unit at 6.72, 14.22 and 21.82 s (gaps 7.50 and
  7.60 s; 200-start ensemble means 6.77, 14.35 and 22.15 s; unchanged to
  0.0003 s at half the step); https://youtu.be/td7bbyUL77s, task
  20260911-102046]
- Gyroscope top: two identical tops with the same one-degree tilt, one
  spinning three times faster; measure the precession periods (expect a
  3:1 ratio against the exact mgr / (I omega)) and the fall time of a top
  spun below the critical rate. [produced 2026-09-11: a 2 cm disc top
  at a 30 deg lean, started in steady precession; 30 turns a second
  circles once every 1.9758 s (20 laps in 40 s), 90 turns a second
  every 6.0245 s (6 laps), ratio 3.049 against exactly 3 from
  m g r / (I3 w3); rigid-body quaternion and step-halving checks agree;
  released from rest the averages are 1.9756 and 6.0238 s; below 6.52
  turns a second the top falls past horizontal from rest (5 turns a
  second in 0.097 s); deterministic, no seed]
- Kelvin wake: a moving source on a deep-water surface at three speeds;
  measure the wake half-angle; expect 19.47 degrees at every speed
  (heavier build: a spectral wave solver; measure the angle before
  committing a slot). [measured 2026-09-11, slot not committed: the
  steady linear deep-water wake of a 1 m Gaussian pressure patch,
  computed spectrally, gives amplitude peaks along rays at 18.8, 10.3
  and 8.8 deg for 4, 8 and 12 m/s (the visible wake narrows with speed,
  Rabaud and Moisy 2013) and noisy outer-crest fits of 19.7, 19.1 and
  13.2 deg; the constant 19.47 deg is the crest-cusp geometry, not what
  the amplitude shows, so the claim needs a boat-size definition and a
  two-part story; evidence in task 20260911-103540]
- Langton's ant: two rules, one ant; measure the step at which the
  highway starts, its period and its drift; expect step 9,977, period
  104, two cells per period; exact, no seed.
- Ant double bridge (pillar idea, ant trails): same colony and seed;
  short and long bridge open from the start versus the short bridge
  opening a minute after the long one; measure the share of trips on the
  short bridge at ten minutes; expect about nine in ten against a
  minority: the colony that found the long path first keeps it.
  [produced 2026-09-09: 60 ants, seed 0, Deneubourg rule k 20 n 2, 600 s
  scent half life; both bridges open: 98.0% of trips on the short bridge
  at minute 10 (64% in minute 1, 80% or more from minute 3); long bridge
  first with the short bridge opening at minute 8: 0 short trips in ten
  minutes, 0.0% at minute 10; seeds 1 to 3 give 97.4, 96.7, 98.7%
  against 0.0%]
- Plane boarding: the same 150 passengers, seats and bag times;
  back-to-front versus random versus Steffen; measure boarding time;
  expect Steffen about twice as fast as back-to-front and back-to-front
  the slowest of the three.
- Elevator paradox: ten floors, you wait on floor two; measure over ten
  thousand waits how often the first elevator to arrive is going down;
  expect about eighty nine percent.
- Parking-lot probing (pillar idea, hash collisions): 1,000 spaces, 950
  cars with the same preferred spots; roll forward to the next free spot
  versus a fresh random spot on each retry; measure the spots passed by
  the last fifty cars and the longest run of taken spots; expect about
  fifty against ten at ninety percent full and two hundred against
  twenty at ninety five.
- Collatz flights: start numbers launched as flights with altitude equal
  to the value; measure steps and peak; expect 27 to take 111 steps and
  climb to 9,232; measure the longest flight under a million in the sim.
- Secretary problem: one hundred candidates walk past; skip thirty seven
  and take the next best; measure the share of ten thousand runs that
  pick the very best; expect about thirty seven percent against one
  percent for a random pick.
- Fourier square from circles: spinning circles draw a square wave;
  measure the peak overshoot at 5, 50 and 500 circles; expect the peak
  eighteen percent above the flat top every time (Gibbs), with the drawing
  as a seamless loop. [produced 2026-09-11: 5, 50, 500 and 5,000 circles
  overshoot the flat top by 18.23, 17.90, 17.90 and 17.90 percent (limit
  (2/pi) Si(pi) = 1.178980, 17.90 percent) while the bump gets 10x thinner
  per step (400, 40, 4 and 0.4 ms after the jump); one period drawn in 8 s
  so the 40 s short loops exactly; https://youtu.be/iIWkxb6zYqE, task
  20260911-103540]
