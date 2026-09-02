# Produce short: Percolation threshold

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day4


## Goal

Backlog idea "Percolation: grid fills randomly; measure the sharp threshold
where a path suddenly connects." Day four slate, chosen for the dense-grid
format that leads the channel numbers (A-star 957 views in a day).

## Claim

A hundred by hundred grid, cells switched on in seeded random order. At
fifty percent filled the biggest patch is three point four percent of the
grid, at fifty eight it is fifteen, and at sixty one point four one cell
connects top to bottom with the patch more than half the grid. Across one
thousand random grids the connection point averages fifty nine point two
six percent; theory for an infinite grid says fifty nine point two seven.

## Evidence

### Measurements

`sims/percolation/percolation.py` with `projects/percolation/manifest.json`
(seed 0, 100x100, ensemble of 1,000 seeds 0-999, union-find with virtual
top and bottom nodes):

- seed 0: first top-to-bottom path at cell 6,137 = 61.37% filled
- biggest cluster: 1.4% at 40% filled, 3.4% at 50%, 5.9% at 55%, 15.3% at
  58%, 54.6% at 61.37% (connection), 55.7% at 62%, 61.7% at 65%, 68.1% at
  70%
- five points before connection 10.6%, five points after 63.6%
- ensemble: mean 59.26%, median 59.29%, min 52.48%, max 63.86%, std 1.54
  points; 792 of 1,000 within 2 points of 59.27%, 948 within 3, 999
  within 5
- histogram (1-point bins): 52-53: 1, 54-55: 2, 55-56: 16, 56-57: 58,
  57-58: 121, 58-59: 222, 59-60: 268, 60-61: 179, 61-62: 99, 62-63: 28,
  63-64: 6
- reference: site percolation threshold on the square lattice 0.5927
  (Newman and Ziff 2000)

The measurement is exact integer arithmetic, so there is no step-size
question; the ensemble is fully determined by the seeds.

### Production

- Voice round-trip: 121 words, 41.25 s after three rephrases. "Cells
  switch on" and later "Watch the cells" both transcribed as "cell", so
  the hook became "Watch the grid fill at random"; "a hundred" became
  "one hundred"; "fifty nine point two six" needed the decimal split rule
  in scripts/normalize.py to compare digit by digit.
- Narration change after the first sheet: "It is not growing. It is
  waiting." contradicted the visible growth of the patch between 58% and
  61%, replaced by "Three more points of fill, and it happens", which is
  what the readout shows (58.3% to 61.4%).
- Fill keyframes pin each spoken number to the readout: the fill crawls
  from 50.0% to 50.3% while "three point four" is spoken (biggest cluster
  reads 3.4% across that whole window, 3.42% to 3.44% measured), from
  57.8% to 58.3% while "fifteen percent" is spoken (15.3%), then reaches
  the seed-0 span at 61.37% at 25.6 s as "four: one cell" is spoken.
  The payoff fades in at the span, before "fifty nine point two six" at
  35 s.
- Fix before the final render: the payoff line overflowed both edges at
  fontsize 40, shortened to "1,000 grids: 59.26%. theory: 59.27%".
- Contact sheet and full-resolution frames at 18.2 s (filled 50.1%,
  biggest 3.4%, "three point four"), 21.5 s (58.1%, 15.3%, "fifteen
  percent"), 26.0 s (61.6%, 54.9%, "top and bottom connected", payoff
  visible) and 36.0 s inspected: no clipping, captions clear of the
  chart, colour flip green to gold at the span.
- Mix: mean -15.8 dB, peak 0.0 dB. Final 43.00 s, 1080x1920, 60 fps,
  music seed 10.

### Upload and publish

- Uploaded private at 10:01 +03:00 on the fresh Pacific quota day (1,600
  units): video `i_YIsr65vgk`, <https://youtu.be/i_YIsr65vgk>.
- QA of the processed upload: processing succeeded, upload status
  processed, PT44S, hd, channel id UCWXsZTvrh_OHkzt6v1xkTsw, and title,
  description, all nine tags (YouTube returns them sorted), category 27
  and made-for-kids false verified against
  `projects/percolation/metadata.json`.
- Published public at 2026-09-02 10:07:48 +03:00 under the self-QA
  policy, then re-read to confirm. Second of the day's three slots.
