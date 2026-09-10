# Produce short: Brachistochrone race, which slide is fastest

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day12

## Goal

Backlog idea "Brachistochrone race: straight, circular-arc and cycloid
tracks from the same start to the same end; measure the arrival times and
track lengths; expect the longest track (the cycloid) to win by about
eighteen percent over the straight line." Day twelve slate, first slot.
Chosen because yesterday's two physics motion shorts (tautochrone 940
views, Dzhanibekov 933) beat every recent counter format (under 131), and
this idea shares the tautochrone's bead-on-a-wire solver. Question in the
first two seconds: "Which slide is fastest?" One setup number (how much
longer the curved slide is), one payoff number (its arrival time against
the straight slide). Every number below is printed by the sim before the
script is written.

## Claim

Which slide is fastest? Three frictionless slides from the same start to
the same end, one ball on each, released together. The straight slide is
the shortest. The curved slide is a cycloid and the longest, seven percent
longer than the straight one. The third slide is a circular arc with a
gentle start. The curve drops steeply at once, so its ball gains speed
first and keeps it: it arrives at one point zero seconds, the straight
slide at one point two, the gentle slide last. The shortest path is not
the fastest.

## Evidence

### Measurements

`sims/brachistochrone/brachistochrone.py` with
`projects/brachistochrone/manifest.json` (bead on a wire, s'' = -g dy/ds,
RK4 at 2,400 steps per physics second, g 9.81, deterministic, no seed,
played at quarter speed; log in `media/brachistochrone/measure.log`):

- cycloid a 0.99396 m so its descent is exactly 1.000 s; start (0, 0),
  end (3.1226, -1.9879) m: 3.12 m across, 1.99 m down; straight slope
  32.5 deg
- straight: length 3.7017 m, arrives at 1.1854 s (closed form 1.1854,
  quadrature 1.1849), energy drift 8e-9
- curve (cycloid): length 3.9758 m, arrives at 1.0000 s (closed form
  1.0000, quadrature 0.9996), energy drift 1e-15
- gentle start (circle radius 6.161 m, start slope 15 deg): length
  3.7598 m, arrives at 1.5030 s (quadrature 1.5022), energy drift 3e-8
- the curve is 7.4% longer than the straight slide and arrives 15.6%
  sooner; the straight slide takes 18.5% longer; the gentle slide takes
  50.3% longer than the curve; arrival order curve 1.000, straight
  1.185, gentle 1.503 s; on-screen gaps at quarter speed 0.74 s and
  1.27 s
- checks, circles with steeper starts: 45 deg start arrives at 1.0832 s
  (8.3% after the cycloid), 60 deg 1.0218 (2.2%), 75 deg 1.0050 (0.5%),
  90 deg (vertical start, radius 2.194 m) 1.0254 (2.5%); every shape
  tried arrives after the cycloid; the classic vertical-start circle is
  too close to the cycloid to separate on screen, so the third slide is
  the gentle-start arc, which loses visibly
- the quadrature check is a midpoint sum of ds / sqrt(2 g h) with a
  1/sqrt singularity at the start, so it reads 0.0004 to 0.0008 s low;
  the closed forms confirm the RK4 times to four decimals
- 5 races of 8 s each; all balls home 6.01 s into a race; reset over the
  last 0.8 s of each race, so the last frame equals the first
- payoff: the longest slide wins, 1.0 s against the straight slide's 1.2 s

### Design notes

- Third slide: a 15 deg gentle-start circular arc (1.503 s) instead of the
  classic vertical-start arc (1.025 s), which is too close to the cycloid
  to separate on screen.
- Five races of 8 s at quarter speed; races start at 0, 8, 16, 24, 32 s,
  balls arrive 4.0, 4.7 and 6.0 s into each race, reset over the last
  0.8 s. The narration is ordered around the race starts: "so its ball
  crawls" at race 2's start (8 s), "Watch the start" just before race 3
  (16 s), "The curve arrives at one point zero seconds" at race 4's curve
  arrival (28.0 s). Payoff text appears at 28.0 s.
- Lane readouts sit above the finish marks (right edge 1036 px of 1080);
  lanes start at x 360 so the "gentle start" label (267 px) clears the
  balls. Overlay 909 px, title 758 px, payoff lines 633 and 439 px.
- Loop: the title returns during the last reset; frame 2399 matches
  frame 0.

### Production

- `sims/brachistochrone/brachistochrone.py` renders the three slides
  (gentle circular arc, straight line, cycloid) from one start mark to one
  end mark, a ball on each, and three lanes below with the slide name,
  its length and a per-ball progress bar with the arrival time printed
  above the finish mark; five races of 8 s at quarter speed (starts at 0,
  8, 16, 24, 32 s; arrivals 4.00, 4.74 and 6.01 s after each start); the
  question "Which slide is fastest?" is drawn for the first 2.4 s and
  again while the balls glide back to the start in the last reset, with
  the top-right clock hidden during that crossfade so the last frame
  equals the first; payoff from 28.0 s ("the longest slide wins: 1.0 s /
  straight slide: 1.2 s") held to the final reset
- narration `projects/brachistochrone/narration.txt`, 107 words; round
  trip passed at 34.749 s (log `media/brachistochrone/voice.log`); the
  race starts and the caption schedule (chunks with the 0.6 s voice
  offset) line up so "Watch the start" is spoken as race 3 begins and
  "The curve arrives at one point zero seconds" as race 4 ends; music
  seed 34 at gain 0.18
- compose: 2,400 frames at 60 fps, final.mp4 40.000 s, 1080x1920, h264,
  aac, faststart; mean volume -16.2 dB, peak 0.0 dB
- text widths measured before rendering: overlay 909 px, title 758 px,
  lane labels 267 px, arrival readouts 152 px with the right edge at
  1,036 px of 1,080, payoff lines 633 and 439 px
- inspection: contact sheet plus full-resolution frames at 1.0, 2.8,
  6.0, 15.4, 24.8, 29.5, 33.0 and 37.9 s from the first final and 0.5,
  20.0, 39.5 and 39.95 s from the re-composed final; fixed lane readouts clipping at the
  right edge and colliding with the balls (lanes moved to x 360..960,
  readouts above the finish marks) and the clock overlapping the
  returning title; the finals show the question with all three balls
  on the start mark at 0.5 s, the curve's ball ahead in every race, the
  payoff on screen while it is spoken, and the balls back on the start
  under the title at 39.95 s

### Published

- clock before upload: 10:00:11 EEST 2026-09-10 = 00:00:11 PDT, the
  fresh Pacific quota day
- uploaded private to the Seed Zero channel (UCWXsZTvrh_OHkzt6v1xkTsw)
  via `scripts/yt-upload.py`: video WJMYAZP0YGw, publishedAt 10:00:25 EEST
  (log in `media/brachistochrone/upload.log`)
- QA gate (scratchpad yt-qa.py, videos.list): 15 of 15 on the first read
  at 10:01:04 EEST: Seed Zero channel, uploadStatus processed,
  processingStatus succeeded, no rejection, HD, embeddable, 1080x1920,
  title, description, tags, categoryId 27, madeForKids false,
  selfDeclaredMadeForKids false, duration PT41S (40.000 s rounds up),
  private
- published (videos.update privacyStatus public, containsSyntheticMedia
  true) at 10:01:22 EEST after a second clean gate read; re-read 15 s
  later: public, madeForKids false, selfDeclaredMadeForKids false,
  embeddable true (log in `media/brachistochrone/publish.log`)
- public URL: https://youtu.be/WJMYAZP0YGw

### Quota

- this short: 1,600 (insert) + 1 (channel check) + 1 (gate read) + 52
  (publish and re-read) = 1,654 units; the day 12 slate together 4,967
  units by the successful requests (plus 2 for the page refresh), at most
  6,568 of 10,000 if the rejected Kapitza insert counted; four insert
  attempts today against the hard cap of five
