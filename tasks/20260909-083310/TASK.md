# Trend research run 2: analytics review and backlog refill

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: backlog

## Run

Second research-trends run, 2026-09-09 08:18 to about 09:00 EEST
(scufris job ecb4e2416e04). Scope: read the channel's measured analytics
with a handful of API reads, use them to say what is working, then refill
the empty backlog from web research. No production, render, upload or
publish in this run. Mid-run the owner added viewer feedback as
qualitative evidence (recorded below, kept apart from the measurements).

## Analytics (measured)

### Reads and quota

- Data API, 3 units on the Sep 8 Pacific quota day: `channels.list`
  (identity gate: the token sees exactly Seed Zero, UCWXsZTvrh_OHkzt6v1xkTsw),
  `videos.list` for all 30 ids in one call, `commentThreads.list` for the
  whole channel in one call. Day total after the day 10 slate and the
  morning briefing: about 4,972 of 10,000.
- Analytics API (separate quota pool), 20 `reports.query` calls: daily
  channel totals, per-video totals, traffic sources, one `dimensions=video`
  read per day from Aug 30 to Sep 8 (10), and six retention curves. One
  call was rejected (`dimensions=video,day` is not supported) and replaced
  by the per-day reads. Raw responses saved in the job scratchpad; nothing
  was read twice.
- Pull time 2026-09-09 08:23 EEST = 2026-09-08 22:23 PDT.

### Data latency and limits

- Analytics rows exist through the Sep 6 Pacific day only. The six videos
  published Sep 7 and Sep 8 have no Analytics rows at all; the Sep 6 slate
  has its publish day only. Retention and traffic below therefore cover 24
  of 30 videos and the period Aug 30 to Sep 6.
- Retention curves were read for 6 of 30 videos, chosen to span formats
  (top views, race, two-panel physics, bar-chart probability, chart
  probability, dense grid), not at random.
- The API has no swipe-away metric. `engagedViews` is the closest proxy
  (views that were not immediate skips). `relativeRetentionPerformance`
  ranks the video against all YouTube videos of similar length, not
  against shorts in this niche. There is no impression or click data for
  Shorts, so view counts mix feed distribution with viewer interest;
  retention and engaged share measure viewer behaviour, views mostly
  measure the feed's pick.
- Videos with 1 or 2 views (golden angle, birthday) carry no signal.
- Channel-level `statistics.viewCount` reads 1,722 against a per-video
  sum of 7,822; the per-video sum is used everywhere, as before.
- The descriptive groupings below use n = 6 or n = 24 and are not tests.

### Channel totals

- 5 subscribers (gained 2, 2, 1 on Aug 30, 31 and Sep 1; 0 since).
- 30 public videos, 7,822 views (Data API per-video sum, matching the
  08:01 morning refresh), 84 likes, 2 shares (both on the double
  pendulum), 1 comment (Galton, "and thats how u lose at plinko").
- Analytics daily views Aug 30 to Sep 6: 691, 1,975, 1,962, 243, 1,191,
  1,148, 185, 185. Engaged views the same days: 193, 665, 899, 69, 268,
  337, 51, 61.

### Traffic sources, Aug 30 to Sep 6 Pacific

| Source | Views | Share | Avg view duration |
|---|---|---|---|
| Shorts feed | 7,065 | 93.2% | 26 s |
| Other YouTube pages | 322 | 4.2% | 23 s |
| YouTube search | 98 | 1.3% | 17 s |
| Channel page | 58 | 0.8% | 28 s |
| External links | 22 | 0.3% | 37 s |
| Subscriber feed | 7 | 0.1% | 2 s |
| Other / related | 6 | 0.1% | |

### Per-video (Analytics through Sep 6; Data API views for the last six)

Engaged share = engagedViews / views. Avg% = averageViewPercentage.

| Video | Published | Views | Engaged share | Avg% | Title numerals |
|---|---|---|---|---|---|
| Double pendulum BU_j-UbPR7k | 08-30 | 1,171 | 30% | 86.4% | 1 |
| A-star flood tp5SPF6mIEo | 09-01 | 979 | 54% | 52.9% | 2 |
| Resonance _oFXN2TRdGE | 09-04 | 874 | 30% | 60.3% | 3 |
| Billiards 8l_VDPlOLC0 | 09-03 | 807 | 29% | 50.4% | 3 |
| Pendulum wave kIuhNc9TguE | 08-31 | 725 | 36% | 61.1% | 3 |
| Sorting race wZt9K5LYZB4 | 08-31 | 490 | 38% | 61.5% | 2 |
| Galton K_ntI_mY4v0 | 08-30 | 473 | 33% | 70.9% | 2 |
| Boids -hm9P9TXi60 | 08-31 | 366 | 34% | 135.2% | 2 |
| Busy beaver -Jkxs7kNpCg | 09-03 | 326 | 13% | 47.4% | 2 |
| Three-body 2zsfLnS9k34 | 09-01 | 314 | 39% | 68.1% | 4 |
| Pi race 7H-27Updk5g | 09-04 | 211 | 24% | 76.2% | 2 |
| Glider gun BSlee2s9ezM | 09-03 | 135 | 15% | 47.7% | 5 |
| Coin flip AbSkSS1F2Mw | 09-01 | 111 | 32% | 67.8% | 3 |
| Percolation i_YIsr65vgk | 09-02 | 110 | 28% | 86.7% | 3 |
| Monty Hall cT8Tcjm7mUs | 08-30 | 99 | 34% | 47.0% | 1 |
| Seven shuffles IEzd2tJSBXU | 09-06 | 88 | 43% | 53.5% | 6 |
| Random walk D0H64ZV2lB4 | 09-05 | 73 | 25% | 27.9% | 4 |
| Schelling WFSD0ywLnAM | 09-02 | 61 | 20% | 53.0% | 2 |
| Best of seven ispETEpU3I0 | 09-05 | 50 | 32% | 49.3% | 4 |
| Bus wait KpidSRY8hpM | 09-06 | 46 | 22% | 42.6% | 4 |
| Epidemic jD5cymWeNgM | 09-05 | 39 | 28% | 44.2% | 5 |
| Gambler's ruin P2tQerZucVI | 09-06 | 29 | 14% | 35.2% | 6 |
| Traffic jam jCLHCYeRziY | 09-02 | 21 | 29% | 22.3% | 4 |
| Golden angle PqQJxCkhUAo | 09-04 | 2 | | 54.9% | 3 |
| Balls into bins b5UMZJhc9UY | 09-07 | 63 (Data API) | no rows | | 6 |
| Buffon's needle rY2w4GjBfoc | 09-07 | 27 (Data API) | no rows | | 3 |
| Birthday two ways fMkt_YLUjUA | 09-07 | 2 (Data API) | no rows | | 4 |
| Benford HkqX1e1EK_M | 09-08 | 68 (Data API) | no rows | | 8 |
| Streak test w50iLhHg-8o | 09-08 | 55 (Data API) | no rows | | 6 |
| Coupon collector P_igHVYavLI | 09-08 | 34 (Data API) | no rows | | 6 |

Channel engaged share over the 24 videos with rows: 2,544 of about
7,580 views, 34%.

### First-day behaviour (views by Pacific day per video)

Publish-day (d0) sums per slate, then the next day (d1), then the slate
total to Sep 6:

| Slate | d0 | d1 | Total | d0 share |
|---|---|---|---|---|
| Aug 30 (published 10:28 to 12:07 PDT) | 702 | 811 | 1,743 | 40% (d0+d1 87%) |
| Aug 31 | 1,172 | 377 | 1,581 | 74% (d0+d1 98%) |
| Sep 1 | 1,373 | 25 | 1,404 | 98% |
| Sep 2 | 177 | 11 | 192 | 92% |
| Sep 3 | 1,172 | 91 | 1,268 | 92% |
| Sep 4 | 1,051 | 29 | 1,087 | 97% |
| Sep 5 | 152 | 10 | 162 | 94% |
| Sep 6 | 163 | not yet in rows | 163 | |
| Sep 7 | no rows; Data API 92 at about 47 h | | | |
| Sep 8 | no rows; Data API 157 at about 23 h | | | |

Per video the same holds: A-star 959 / 14 / 3 / 3 (d0 / d1 / d2 / later),
billiards 726 / 77 / 1 / 3, resonance 844 / 23 / 7 / 0, pendulum wave
522 / 183 / 17 / 3. Boids went public at 22:55 PDT on Aug 30, so its
first full day (304) is Aug 31. Since Sep 1, 92 to 98 percent of a
short's views arrive on its publish day; the 27 older videos gained 7
views combined between the Sep 8 and Sep 9 morning refreshes.

### Retention curves (audienceWatchRatio at 10 / 30 / 50 / 100 percent of the video; relative retention performance, 0 to 1 rank)

| Video | 10% | 30% | 50% | 100% | Rel. min (where) | Rel. at end |
|---|---|---|---|---|---|---|
| Double pendulum | 1.28 | 1.02 | 0.84 | 0.48 | 0.55 (20-25%) | 0.86 |
| A-star flood | 1.11 | 0.62 | 0.43 | 0.25 | 0.14 (40%) | 0.58 |
| Resonance | 1.17 | 0.72 | 0.53 | 0.25 | 0.43 (15%) | 0.73 |
| Monty Hall | 0.97 | 0.50 | 0.47 | 0.12 | 0.16 (15%) | 0.61 |
| Best of seven | 1.06 | 0.69 | 0.38 | 0.06 | 0.05 (45%) | 0.17 |
| Schelling | 1.08 | 0.67 | 0.50 | 0.17 | 0.17 (65%) | 0.33 |

All six hold at or above 0.97 through the 10 percent mark (the first
4 s). The largest loss on every curve is between 10 and 30 percent (4 to
12 s): pendulum -0.26, A-star -0.49, resonance -0.44, Monty Hall -0.47,
best of seven -0.37, Schelling -0.42. The relative rank sinks below the
median of similar-length videos in that window on all six and recovers
at the end only for the two physics pieces.

### Descriptive, in-repo (n = 6 per group)

The six best retainers with rows (boids, percolation, pendulum, pi race,
Galton, three-body) carry on average 2.3 numerals in the title and 110
narration words; the six worst (traffic, random walk, ruin, buses,
epidemic, Monty Hall) carry 4.0 numerals and 117 words. The six most
recent shorts, which have no retention rows yet, carry 3 to 8 numerals
(mean 5.5).

## What the numbers say about formats (measured contrasts, no causes)

- Distribution is decided on the publish day by the Shorts feed (93% of
  views). Since Sep 1 a short earns 92 to 98 percent of its views on day
  zero and the back catalogue is flat. View counts therefore report the
  feed's first-day pick; retention and engaged share report what viewers
  did once served.
- By topic family (views): every physics or chaos motion piece except the
  traffic ring reached 314 to 1,171 views (double pendulum, resonance,
  billiards, pendulum wave, Galton, boids, three-body). Algorithm races
  reached 490 to 979 and the exact machines 135 to 326. Probability
  pieces sit at 2 to 131 whether staged as charts (Aug 30 to Sep 6) or as
  physical motion (Sep 7 and 8, Data API only). Slates that contained a
  physics motion piece totalled 1,051 to 1,373 on day zero; slates
  without one totalled 152 to 177 (Sep 2, 5, 6) and 92 to 157 (Sep 7, 8,
  Data API). The Sep 8 "physical staging" slate (157 at 23 h) sits inside
  the 152 to 163 band of the chart-shaped Sep 5 and Sep 6 slates, so the
  staging change did not move the slate total.
- Retention (viewer behaviour): best are boids 135% (replays), percolation
  87%, double pendulum 86%, pi race 76%, Galton 71%, three-body 68%, coin
  flip 68%. Worst are traffic 22%, random walk 28%, ruin 35%, buses 43%,
  epidemic 44%, Monty Hall 47%, busy beaver 47%, glider gun 48%. The
  physics and chaos pieces span 50 to 135 percent; the grid-of-counters
  and bar-chart pieces span 22 to 54 except percolation and coin flip.
  View winners are not retention winners: A-star has 979 views at 53%,
  percolation 110 views at 87%.
- Engaged share: A-star 54% is the standout; most physics and race pieces
  sit at 29 to 43 percent; busy beaver 13%, ruin 14% and glider gun 15%
  are the lowest. Two thirds of counted views are not engaged views.
- Hooks: the first 4 s hold on all six curves, so the opening-motion hook
  is not where viewers leave. The exit is at 4 to 12 s, the setup beat.
- Loops: boids (135%) and the double pendulum (watch ratio above 1.0 to
  the 30 percent mark) show replays; the pendulum wave, built as a
  seamless loop, sits at 61%. A seamless loop alone did not produce
  replays; the two replayed pieces open on the densest motion.
- Two-panel tiny-difference comparisons win views (807 to 1,171) with
  middling retention (50 to 86%); single-motion snaps (pendulum wave,
  boids, Galton) retain 61 to 135 percent at 366 to 725 views.
- Search brings 1.3% of views; nothing suggests titles are found by
  search yet.

## Owner viewer feedback (qualitative, 2026-09-09)

Relayed by the owner during this run, kept apart from the measurements:
the shorts are often hard to understand quickly, hard to follow, and
sometimes leave the viewer unable to identify the goal. Pace is not the
problem; cognitive load and unclear framing are. Guidance given with it:
establish one concrete question or goal immediately, reduce jargon and
competing numbers, keep narration synchronized with one visible causal
story, use plain language, and make the payoff explicitly answer the
opening question. Do not let it dictate topics.

## Consistency check (judgement, not causation)

The retention evidence is consistent with the feedback: viewers stay
through the opening motion and leave fastest in the 4 to 12 s window
where the setup and the numbers are narrated, and the relative rank drops
below the median of similar-length videos exactly there. The descriptive
title-numeral contrast (2.3 for the best retainers, 4.0 for the worst,
5.5 for the newest six) points the same way. None of this shows cause:
the same drop shape could come from the feed serving uninterested
viewers, from the subject, or from the narration, and n is small. The
guidance is adopted as production rules in `docs/vision.md` (Framing)
because it costs nothing and the evidence does not contradict it.

## Selection criteria used for the refill (judgement)

1. Continuous physical motion with one visible divergence, ideally the
   two-panel same-input comparison or a single motion that snaps.
2. One plain question a viewer can state in the first two seconds, and
   one payoff number that answers it. One setup number.
3. A deterministic in-repo simulation at 1080x1920 that prints the
   number, with an exact-theory check where one exists.
4. A seamless loop where the physics is periodic.
5. Avoid grid-of-counters staging, bar charts, and repeats of the worst
   retainers.

## Queries run (WebSearch, 14) and pages fetched (5)

Searches: trending physics simulation YouTube Shorts 2026 viral science
animation; Primer channel new simulation video 2026; Dzhanibekov effect
intermediate axis theorem simulation viral short; Langton's ant highway
emerges after 10,000 steps; airplane boarding simulation back to front vs
random vs Steffen method faster; ant double bridge experiment shorter
branch pheromone simulation Deneubourg colony stuck on long path;
brachistochrone race video cycloid vs straight line viral; hash table
linear probing primary clustering visualization animation; science math
anniversaries October November 2026 physics discovery date; YouTube
Shorts educational retention 2026 clear question hook cognitive load
first 3 seconds; 3Blue1Brown 2026 new video topic; magnetic pendulum
three magnets fractal basin chaos simulation unpredictable; why do ants
walk in a line follow each other explained question; Nobel Prize in
Physics 2026 announcement date October.

Fetched: Wikipedia Langton's ant; Wikipedia Steffen Boarding Method;
shortimize.com Shorts retention page; fluxnote.io viral physics shorts
ideas 2026; Wikipedia Tennis racket theorem.

## Sources and what each showed

- https://fluxnote.io/guides/viral-physics-youtube-shorts-ideas-2026 :
  counterintuitive results have the highest share rate in physics
  content; the winning formats are demo-then-explain and misconception;
  gyroscopes, pendulum waves, resonance and Magnus effect are on the
  list. Formats only; nothing copied.
- https://www.shortimize.com/blog/youtube-shorts-retention-rate : refuses
  a single benchmark; treat the first second as the thumbnail; viewers
  swipe if they cannot tell what is happening in under half a second;
  replays are good when the moment is surprising and bad when the viewer
  is confused.
- https://aibrify.com/blog/youtube-shorts-retention-curve-playbook and
  https://miraflow.ai/blog/youtube-shorts-best-practices-2026-complete-guide
  (search summaries): open on a question or visual surprise within the
  first second; educational shorts work at 25 to 40 s; fitting too much
  information into one short is the common failure.
- https://en.wikipedia.org/wiki/Langton%27s_ant and
  https://www.101computing.net/langtons-ant/ : chaos until about 10,000
  steps, then a highway of period 104; 101computing quotes 9,977. A
  scratch run in this job reproduced 9,977 exactly (drift 2,2 per 104
  steps). arXiv 2505.05426 and 2506.10482 show the subject is still
  studied in 2025-2026.
- https://en.wikipedia.org/wiki/Steffen_Boarding_Method ,
  https://www.scientificamerican.com/article/there-are-quicker-ways-to-board-a-plane-so-why-dont-airlines-use-them/ ,
  https://www.popsci.com/technology/best-way-to-board-an-airplane-according-to-science/ :
  Steffen's method is about twice as fast as back-to-front and 20 to 30
  percent faster than random; back-to-front is the second worst method.
- https://en.wikipedia.org/wiki/Tennis_racket_theorem and
  https://www.youtube.com/shorts/BU5HwNyE4mk : Euler equations; spin
  about the largest and smallest moments is stable, the intermediate axis
  is not; the flip already circulates as a short.
- Ant double bridge (Goss, Aron, Deneubourg, Pasteels 1989, via
  https://www.arxiv.org/pdf/1908.08007v1 and researchgate figures): the
  colony converges on the shorter branch by pheromone feedback; when the
  short branch is offered after the long one is established, most ants
  keep the long branch.
- https://www.sciencefocus.com/nature/why-do-ants-walk-in-a-line ,
  https://www.colorado.edu/today/2025/05/06/curiosity-why-and-how-do-ants-walk-perfect-line ,
  Medium (Apr 2026): "why do ants walk in a line" is a recurring
  audience question.
- https://www.youtube.com/shorts/aZDzlZQNmoo (Aug 2025),
  https://demonstrations.wolfram.com/TheGreatBrachistochroneRace/ ,
  https://sites.imsa.edu/hadron/2026/01/15/when-straight-lines-arent-the-fastest-way-the-brachistochrone-curve/ :
  the cycloid race is an active short-form subject; the straight line
  loses.
- https://beltoforion.de/en/magnetic-pendulum/ ,
  https://faculty.tru.ca/rtaylor/pendmag/index.html ,
  https://ima.org.uk/13908/chaos-in-the-magnetic-pendulum/ , arXiv
  2504.01580: fractal basins; a hair's difference in release changes the
  final magnet.
- https://en.wikipedia.org/wiki/Primary_clustering ,
  https://visualgo.net/en/hashtable , arXiv 2107.01250 and 2501.11582:
  linear probing clusters into long runs; still an active research topic.
- https://www.nobelprize.org/press-release/the-2026-nobel-prize-announcements/ :
  announcements Oct 5 to 12, physics on Tue Oct 6 at 11:45 CEST.
  Wikipedia physics anniversaries: Bohr born Oct 7 1885; general
  relativity presented Nov 25 1915.
- 3Blue1Brown 2026: entropy and compression series (June), puzzle videos;
  no simulation peg. Primer: no 2026 information surfaced.

## Scratch expectation checks (research expectations, not measurements)

Run in the job scratchpad, kept out of the repo: Langton highway at step
9,977; Collatz 27 takes 111 steps and peaks at 9,232; cycloid descent
1.003 s against a straight line 1.189 s (18.5% slower) though the cycloid
is longer (4.00 against 3.72); a circular bowl's period grows from 2.01 s
at 10 degrees to 3.54 s at 150 degrees while the cycloid's does not;
secretary rule picks the best 37.4% of 20,000 runs against 1.0% for a
random pick; elevator paradox on floor 2 of 10 gives 88.9% going down;
Kapitza stability A*omega 3.77 against a threshold 1.40 for a 10 cm
pendulum shaken 2 cm at 30 Hz; linear probing 50.5 against 10 probes at
90% load and 200 against 20 at 95% (Knuth); Gibbs peak 1.182, 1.179 and
1.179 at 5, 50 and 500 terms; Lorenz nudges of 1e-3, 1e-6 and 1e-9 reach
order one after 7.6, 15.3 and 22.9 time units. Projectile with baseball
drag at 30 m/s: the best angle is 43 degrees, 0.3% farther than 45.

## Accepted (16, appended to docs/niche.md)

Each entry: staging; the question in the hook; what the sim measures;
the expected surprise; checks.

1. Tautochrone bowl. Physics, two panels, seamless loop. "Do they arrive
   together?" Five balls released from five heights in a circular bowl
   (left) and a cycloid bowl (right); measure the arrival-time spread at
   the bottom and each ball's period. Expect cycloid spread 0.000 s and
   equal periods (exact isochronism), circular spread growing every
   swing (up to 1.5 s per period across 10 to 150 degrees). The cycloid
   panel is exactly periodic, so the last frame equals the first.
2. Brachistochrone race. Physics, three tracks. "Which slide is
   fastest?" Straight, circular arc and cycloid beads from the same start
   to the same end; measure arrival times and track lengths. Expect the
   cycloid to win by about 18% over the straight line while being the
   longest track. Closed-form check for the cycloid and the line.
3. Dzhanibekov flip. Physics, two panels. "Which spin stays put?" A box
   with moments 1:2:3 in zero g, spun about the intermediate axis (left)
   and the long axis (right) with the same 0.001 rad/s wobble; Euler
   equations with RK4; measure the first flip time, the flip period, the
   flips in 40 s and the bounded wobble on the right; check energy and
   angular momentum conserved to 1e-10. Needs a small projected-box
   renderer (8 vertices, painter's order). Peg: Nobel week Oct 5 to 12.
4. Magnetic pendulum. Chaos, two bobs one hair apart. "Same drop, same
   magnet?" Two bobs released 0.1 mm apart over three magnets; measure
   the time to separate by one bob width and the final magnet of each;
   plus a 200x200 grid of releases to count the share whose one-pixel
   neighbour ends elsewhere. Expect a large unpredictable share (fractal
   basin boundary).
5. Kapitza inverted pendulum. Physics, two panels. "Can a pendulum stand
   upside down?" Same 10 cm inverted pendulum, same 0.001 rad nudge; left
   pivot still, right pivot shaking 2 cm at 30 Hz; measure the fall time
   on the left and the maximum tilt on the right over 600 s. Expect the
   left to fall within about a second and the right to stay up (stability
   3.77 against 1.40).
6. Lorenz forecast horizon. Chaos, measured law. "How far ahead can you
   predict it?" Two Lorenz copies nudged by 1e-3, 1e-6 and 1e-9; measure
   the time to disagree by one unit. Expect about 7.6, 15.3 and 22.9 time
   units: every thousandfold gain in precision buys the same 7.6.
   Rendered as the butterfly with two dots per panel.
7. Gyroscope top. Physics, two panels. "Why doesn't it fall?" Two
   identical tops with the same 1 degree tilt, one spinning three times
   faster; measure the precession period of each (expect a 3:1 ratio
   against the exact mgr / (I omega)) and the fall time of a top spun
   below the critical rate. Shares the projected-box renderer with 3.
8. Kelvin wake. Physics, seamless loop, heavier build. "Why do all boats
   leave the same V?" A moving pressure source on a deep-water dispersive
   surface (spectral solver); measure the wake half-angle at three
   speeds. Expect 19.47 degrees at every speed. Measure the angle before
   scripting; if the solver cannot resolve it cleanly, drop the idea.
9. Langton's ant. Emergence, exact, no seed. "Will this ever make
   sense?" Two rules, one ant; measure the step the highway starts, its
   period and drift, and the black-cell count. Expect step 9,977, period
   104, drift 2 cells per period (scratch-confirmed). Note: exact-machine
   pieces (busy beaver 326 views at 47%, glider gun 135 at 48%) sat
   mid-pack; the difference here is the visible switch from chaos to
   order.
10. Ant double bridge. Emergence, two panels; the pillar's "ant trails".
    "Do ants find the shortest path?" Same colony, same seed, pheromone
    deposit and evaporation; left: short and long bridge open from the
    start; right: long only, the short bridge opens at 60 s. Measure the
    share of trips on the short bridge at 10 minutes in each panel.
    Expect about nine in ten on the left and a minority on the right:
    the colony that found the long path first keeps it (Goss 1989).
11. Plane boarding. Algorithms in motion. "What is the slowest way to
    board?" Same 150 passengers, same seats and bag times at seed 0;
    back-to-front, random and Steffen; measure boarding time in ticks.
    Expect Steffen about twice as fast as back-to-front and 20 to 30
    percent faster than random, with back-to-front the slowest of the
    three.
12. Elevator paradox. Probability in motion. "Why is the first elevator
    always going the wrong way?" Ten floors, elevators cycling, you wait
    on floor 2; measure over 10,000 waits how often the first arrival
    goes down. Expect about 89% (closed form 8/9 for one elevator).
13. Parking-lot probing. Algorithms, two panels; the pillar's "hash
    collisions". "Why does the left street jam?" A street of 1,000
    spaces, 950 cars with the same preferred spots at seed 0; left: roll
    forward to the next free spot (linear probing); right: a fresh random
    spot on each retry (uniform probing). Measure the average spots
    passed by the last 50 cars and the longest run of taken spots.
    Expect about 50 against 10 at 90% full and 200 against 20 at 95%
    (Knuth).
14. Collatz flights. Algorithms, exact. "Does it always come back down?"
    Start numbers launched as flights with altitude equal to the value;
    measure steps and peak. Expect 27 to take 111 steps and climb to
    9,232; verify the longest flight under one million in the sim.
15. Secretary problem. Probability in motion. "When should you stop
    looking?" 100 candidates walk past; skip 37, take the next best;
    measure the share of 10,000 runs that pick the very best. Expect
    about 37% against 1% for a random pick.
16. Fourier square from circles. Algorithms, seamless loop. "How many
    circles fix the corner?" Spinning circles draw a square wave;
    measure the peak overshoot at 5, 50 and 500 circles. Expect the peak
    18% above the flat top every time (Gibbs; 8.9% of the jump).

## Rejected (15)

1. Projectile at 45 degrees with drag: for a baseball at 30 m/s the best
   angle is 43 degrees, 0.3% farther; a visible gap needs a very light
   ball, so the number would be about the ball chosen.
2. Stroboscopic wagon wheel: the effect depends on the viewer's playback
   frame rate, so a viewer cannot reproduce the narrated number.
3. Binary search, 20 guesses for a million: the number is already
   famous and the linear walker gives 40 s of monotone motion.
4. Sieve of Eratosthenes race: no surprising number.
5. Spatial prisoner's dilemma: dense grid, jargon-heavy setup, the payoff
   means nothing without it.
6. Bus bunching: a repeat of the traffic ring, the worst retainer (22%).
7. Martingale betting: a repeat of gambler's ruin (35%, 29 views).
8. Luck versus skill tournament: the payoff is set by the assumed luck
   weight, not measured from a mechanism.
9. Gerrymandering: grid staging, an arbitrary districting rule, loaded.
10. Chladni plate: near-duplicate of resonance with a weaker number.
11. Chaos game (Sierpinski): the surprise is a picture, not a number.
12. Abelian sandpile: the fractal is the point; the largest-avalanche
    count is not a surprise to a viewer; dense-grid family.
13. Monte Carlo pi from random dots: a repeat of Buffon's needle (27
    views).
14. Bertrand's box, two-child and Simpson's paradox: chart-shaped, no
    motion, the setup is the whole short.
15. Nobel week, Bohr's birthday, general relativity anniversary: facts
    to report, not surprises to measure. Nobel week (physics Oct 6) is
    kept as a scheduling peg for the strongest physics piece.

## Slotting notes (judgement)

- Three strongest for the next slate: tautochrone bowl (loop, exact
  isochronism), Dzhanibekov flip (two panels, high demand), ant double
  bridge (emergence, the audience's own question). Alternates:
  brachistochrone, Kapitza, magnetic pendulum.
- Tautochrone and brachistochrone share a bead-on-wire solver; build one
  and the other is cheap, but keep them on different days.
- Dzhanibekov and the gyroscope share the projected-box renderer.
- Kelvin wake is the only heavy build; measure the angle before
  committing a slot.
- Every new short follows the Framing rules in `docs/vision.md`: one
  question in the first two seconds, one setup number, one payoff number
  that answers the question, narration tied to what moves.
- Backlog after this run: 16 unproduced ideas, above the 15 threshold.
  The ramp condition in AGENTS.md also needs retention data that shows
  which formats work; the retention contrast above is a first reading
  from 24 videos, and the day-zero distribution pattern says more uploads
  do not lift older videos. Cadence stays at 3 per day.

## Files changed

- `docs/niche.md`: 16 backlog entries, pillar notes for ant trails and
  hash collisions, a pointer to the framing rules.
- `docs/vision.md`: Framing section.
- `web/data/log.jsonl`: one entry; `web/data/slate.json`: backlog line
  (on top of the preserved morning refresh of views, likes and status).
- This task.
