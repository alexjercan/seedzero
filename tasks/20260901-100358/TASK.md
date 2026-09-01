# Produce short: A-star versus BFS on one maze

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day3

## Goal

Backlog idea "A-star versus BFS: same maze, count the cells each one
touches." Morning briefing candidate for the 2026-09-01 slate.

## Claim

One seeded grid of wall blocks, one start, one goal, one shared replay
rate. Breadth first checks nine thousand two hundred seventy two cells,
A star checks three hundred fifty one, twenty six to one, and both return
the same two hundred twenty three cell shortest path.

## Evidence

### Measurements

`sims/pathrace/pathrace.py` with `projects/pathrace/manifest.json`
(seed 0, 160x72 cells, 40 rectangular wall blocks, start (2,2), goal
(69,157)):

- 11,520 cells, 9,284 walkable
- breadth first: 9,272 cells checked, 99.9% of the walkable grid
- A star: 351 cells checked
- ratio 26.4 to 1
- path length 223 cells, identical for both; the sim asserts equal length
  and walks both paths to check each step is a legal move onto a walkable
  cell before rendering anything

### Geometry note

A first pass used a perfect maze from a recursive backtracker and measured
a ratio of 1.03 to 1: in a perfect maze the corridors force both searches
to touch nearly the same cells, so there is no claim there. The second
factor was the tie break. Plain A* with the Manhattan heuristic spreads
across the plateau of equally good monotone routes and checked 5,983
cells; the standard prefer-higher-g tie break keeps the path optimal and
brings it to 351. The description names the tie break.

### Production

- Voice round-trip: three iterations. Piper says "breadth" as "breath", and
  no respelling fixed it ("bredth", "bredeth", "breadthe", "bread th" all
  failed), so the narration says "flood fill" while the on-screen label
  keeps the formal name; the description explains that they are the same
  algorithm. "knew where to look" transcribed as "knew her to look" and was
  rephrased. Final ok at 36.943 s, 119 words.
- Layout: two render passes. The first had a redundant headline counter
  duplicating the breadth-first count, and the second panel's label
  collided with the first panel's goal marker. Dropped the headline and
  moved the panels apart.
- Contact sheet: A star finishes at 3.5 s and holds "351 checked found it"
  for the rest of the video; "A star has already finished. Three hundred
  fifty one cells checked." is spoken at 20-22 s against that readout;
  breadth first finishes at 27 s and "Nine thousand two hundred seventy
  two cells" is spoken at 28-29 s with 9,272 on screen; "the same shortest
  path: two hundred twenty three cells" at 31-34 s with "same path: 223
  cells long" on screen. Every narrated number is true when spoken.
- Mix: mean -15.2 dB. Final 38.50 s, 1080x1920, 60 fps.

### Upload and publish

- Uploaded private on the fresh Pacific quota day (1,600 units):
  video `tp5SPF6mIEo`, <https://youtu.be/tp5SPF6mIEo>.
- QA of the processed upload: processing succeeded, upload status
  processed, PT39S, hd, channel id UCWXsZTvrh_OHkzt6v1xkTsw, and title,
  description, all nine tags, category 27 and made-for-kids false all
  verified against `projects/*/metadata.json`.
- Published public at 2026-09-01 10:44 +03:00 under the self-QA
  policy, then re-read to confirm the visibility flip. Second of the day's three slots.
