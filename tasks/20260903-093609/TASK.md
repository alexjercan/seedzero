# Produce short: Gosper glider gun

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day5

## Goal

Backlog idea "Conway glider gun: count cells alive over time; a machine
from four rules." Day five slate, chosen because the dense-grid format
with continuous motion leads after chaos (A-star 971 views, percolation
the best of the day-four three). Emergence pillar. Measure the exact
live-cell count and the glider launch law at a fixed generation.

## Claim

Thirty six live cells and the four Life rules. The first glider breaks
away at generation fifteen; one more launches every thirty generations,
exactly, and moves one cell diagonally every four generations. The gun
returns to the same thirty six cells at every multiple of thirty. At
generation one thousand five hundred it has launched fifty gliders and
two hundred eighty six cells are alive; the live count grows by exactly
five every thirty generations, with no exception over two thousand
generations.

## Evidence

### Measurements

`sims/lifegun/lifegun.py` with `projects/lifegun/manifest.json` (Gosper
glider gun, 36 cells at origin (2, 2), unbounded sparse grid, 3,200
generations; a glider is a 5-cell 8-connected component matching one of
the four glider phases; everything else counts as the gun):

- first glider separates at generation 15
- launches: 107 by generation 3,200, spacing min 30 max 30 generations
- gun cells repeat every 30 generations over the whole run; no shorter
  period works; the gun stays inside x 2..37, y 2..10 (36 by 9 cells)
- gun cells at every multiple of 30: exactly 36 (min 36 max 61 between)
- live(g + 30) - live(g): min 5 max 5 for every g in 0..3,170
- generation 1,500: 286 live cells, 50 gliders; generation 3,000: 536
  live, 100 gliders; generation 3,200: 584 live, 107 gliders
- leading glider centroid: 0.2499 cells per generation in x, 0.2500 in
  y, one diagonal cell every 4.00 generations

The rules are exact integer arithmetic: no seed, no step size, no
floating point. The scene shows 3,138 generations; playback ramps from
4 to 100 generations per second (rate keys in the manifest), and
generation 1,500 lands at 26.63 s of video.

### Production

- First measurement split the gun from the gliders by bounding box and
  asserted on a forming glider at generation 28; replaced by the shape
  match above, which counts only fully formed, separated gliders.
- Voice round-trip: 107 words, 41.54 s, after four rephrases: "Start
  it" transcribed as "started", "neighbours" needs the US spelling,
  "leaves" transcribed as "leads", and "one thousand five hundred: fifty
  gliders" folded into 1,550 (fixed by "the gun has launched fifty").
- Layout fixes from the contact sheet: 12 px cells left the glider
  stream exiting the frame with the bottom third empty, so cells are
  14 px on 60 rows with the four rules printed under the grid; the
  payoff card overflowed and was shortened to "gen 1,500: 50 gliders,
  286 alive. +5 every 30"; the chart's "generation" label collided with
  the 3,000 tick, so ticks are 0, 1,000, 2,000. Scene 41 to 43 s and
  generations 3,100 to 3,200 to fit the voice.
- Timing: "five cells break away" is spoken at 6-7 s with the first
  glider gold on screen (generation 33-49); the payoff card fades in at
  26.63 s before "one thousand five hundred: the gun has launched fifty"
  at 27-33 s; "Two thousand generations" at 37-39 s with the counter past
  2,400.
- Contact sheet and full-resolution frames at 0.5, 6.5, 27 and 38 s
  inspected: captions sit between the rules text and the chart, no
  clipping, gun teal and gliders gold, the alive chart a straight
  sawtooth line.
- Mix: mean -15.8 dB, peak 0.0 dB. Final 43.00 s, 1080x1920, 60 fps,
  music seed 13.

### Upload and publish

- Uploaded private at 10:20 +03:00 on the fresh Pacific quota day (1,600
  units): video `BSlee2s9ezM`, <https://youtu.be/BSlee2s9ezM>.
- QA of the processed upload: processing succeeded, upload status
  processed, PT44S, hd, channel id UCWXsZTvrh_OHkzt6v1xkTsw, and title,
  description, all nine tags, category 27 and made-for-kids false
  verified against `projects/lifegun/metadata.json`.
- Published public at 2026-09-03 10:22:07 +03:00 under the self-QA
  policy, then re-read to confirm. Second of the day's three slots.
