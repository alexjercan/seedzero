# Produce short: Schelling segregation

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day4


## Goal

Backlog idea "Schelling segregation: agents needing only thirty percent
same-color neighbors; measure final segregation percentage." Day four
slate: emergence pillar, grid format, and a social hook.

## Claim

Nine thousand agents of two kinds on a hundred by hundred grid, each
content when thirty percent of its neighbours are its own kind. From
fifty point seven percent alike at the start, the grid settles after
sixteen rounds and three thousand seven hundred eighty moves at seventy
five point nine percent alike, with two thousand six hundred eighty one
agents having no different neighbour at all.

## Evidence

### Measurements

`sims/schelling/schelling.py` with `projects/schelling/manifest.json`
(seed 0, 100x100, 10% empty, want 30% alike, Moore neighbourhood, every
discontented agent moves to a seeded random empty cell each round):

- 9,000 agents (4,500 of each kind), 1,000 empty cells
- start: 50.7% alike on average, 1,505 of 9,000 discontent (16.7%)
- after round 1: 60.0% alike, 850 discontent; round 2: 65.8%, 546;
  round 3: 69.2%, 353; round 5: 73.6%, 125; round 10: 75.8%, 8;
  round 15: 75.9%, 3
- settled after 16 rounds and 3,780 moves: 75.9% alike (76% to the
  nearest point), 0 discontent
- final per-agent alike share: 10th percentile 50%, median 75%, 90th
  percentile 100%; 2,681 agents with every neighbour alike
- same seed, other thresholds: want 20% -> 57.9% (8 rounds, 782 moves);
  25% -> 58.5%; 30% -> 75.9%; 35% -> 77.4%; 40% -> 83.0% (27 rounds,
  6,486 moves); 50% -> 88.0% (23 rounds, 9,881 moves)

Exact integer bookkeeping, fully determined by the seed.

### Production

- Voice round-trip: 123 words, passed first time at 38.85 s; re-voiced
  once at 40.05 s after the per-round numbers were changed from rounded
  ("sixty nine", "seventy four") to the exact readouts ("sixty nine point
  two", "seventy three point six") so the voice never disagrees with the
  on-screen decimal.
- Compose failed twice on the overlay's "30%": drawtext treats a stray
  percent sign as an expansion error and accepts neither "%%" nor "\%".
  scripts/captions.py now sets expansion=none on every drawtext, which
  this project never needed anyway.
- Round schedule pins the readouts to the voice: round one replays its
  1,505 moves from 1.0 s to 17.6 s (the hook is in motion from the first
  second), round three is on screen from 19.6 s to 20.9 s under "nine
  point two", round five from 21.6 s to 22.8 s under "three point six",
  rounds seven to sixteen run at 0.8 s each and the grid settles at 30.8 s
  as "nobody wants to move" is spoken; the payoff "asked for 30% alike.
  got 75.9%." fades in there, before "seventy five point nine" at 32.5 s.
- Contact sheet and full-resolution frames at 1.5 s (round 0, 1,460 still
  want to move), 18.0 s (round 1, 60.0%), 20.7 s (round 3, 69.2%), 22.6 s
  (round 5, 73.6%) and 31.0 s (round 16, 75.9%, 0 still want to move,
  payoff) inspected: no clipping, captions clear of the chart, every
  narrated number on screen for the whole caption that speaks it.
- Mix: mean -15.5 dB, peak 0.0 dB. Final 41.50 s, 1080x1920, 60 fps,
  music seed 11.

### Upload and publish

- Uploaded private at 10:01 +03:00 on the fresh Pacific quota day (1,600
  units): video `WFSD0ywLnAM`, <https://youtu.be/WFSD0ywLnAM>.
- QA of the processed upload: processing succeeded, upload status
  processed, PT42S, hd, channel id UCWXsZTvrh_OHkzt6v1xkTsw, and title,
  description, all nine tags (YouTube returns them sorted), category 27
  and made-for-kids false verified against
  `projects/schelling/metadata.json`.
- Published public at 2026-09-02 10:07:50 +03:00 under the self-QA
  policy; the first re-read one second later still said private, a
  second read at 10:08:23 confirmed public. Third of the day's three
  slots: the daily cadence cap is reached, no more uploads today. Quota
  spent about 4,970 of 10,000 units (three uploads at 1,600, three
  channel checks, sixteen videos.list reads, three visibility updates),
  so the day keeps room for a re-upload.
