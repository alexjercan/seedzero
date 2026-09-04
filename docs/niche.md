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
   Segregation from tiny preferences (Schelling). Ant trails. Conway life
   guns.
4. **Algorithms in motion.** Sorting races with honest operation counts.
   Pathfinding A* versus BFS flood. Epidemic spread on networks. Hash
   collisions filling a table.

## Claim style

Bad: "The double pendulum is chaotic."
Good: "These two pendulums started one thousandth of a degree apart. At
eight point two seconds they are on opposite sides of the screen."

The good version names the initial difference, the measured divergence time,
and both are printed by the sim.

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
  sharper count (expect near five thousand seventy).
- Gambler's ruin: a fair coin, one player has ten times the bankroll;
  measure how often the small stack survives.
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
  above the threshold; measure final infected counts.
- Conway glider gun: count cells alive over time; a machine from four
  rules. [produced 2026-09-03: the Gosper gun fires one glider every 30
  generations exactly; at generation 1,500 it has launched 50 and 286
  cells are alive, and the count grows by exactly 5 every 30
  generations over the whole run]
- Buffon's needle: estimate pi by dropping ten thousand needles; show the
  estimate converge on screen.
- Random walk versus drunk walk home: measure return-to-origin times in
  one and two dimensions.
- Three-body figure eight: the periodic solution, then nudge it; measure
  how long the choreography survives. [produced 2026-09-01: survival time
  is not step-independent, so the claim became the linear growth law,
  482x the nudge over forty laps]
- Coupon collector: how many packs to complete a fifty-sticker album;
  measure the expected long tail.
- Benford's law: leading digits of powers of two; count the ones versus
  the nines.
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
  corrects the gambler's fallacy "due for tails" intuition).
- Seven shuffles: riffle shuffle thousands of decks one to ten times; a
  card guesser plays each deck and measures its edge over chance, which
  survives four shuffles and dies near seven.
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
  discrepancy breakthrough coverage, August 2026).
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
  September and October).
