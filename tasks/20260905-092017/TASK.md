# Produce short: Best of seven, the better team

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day7

## Goal

Backlog idea "Best of seven: one hundred thousand series where the
better team wins each game fifty five percent of the time; measure how
often it wins the series (expect near sixty percent; peg: playoff
season, September and October)." Day seven slate, third slot, chosen
for the timely peg and the race format with honest counters (A-star
978 views, sorting race 489). Measure the series win rate over one
hundred thousand seeded series, the exact probability by dynamic
programming as a check, and how long a series would have to be for the
better team to win nine in ten.

## Claim

The better team wins each game fifty five percent of the time. In one
hundred thousand best-of-seven series at seed zero it won sixty
thousand seven hundred twenty one, sixty point seven percent (exact
probability sixty point eight). Thirty thousand four hundred fifty six
series went to a game seven, and the better team won fifty five percent
of those. To win nine series in ten it needs a best of one hundred
sixty three; ninety nine in one hundred needs a best of five hundred
thirty nine.

## Evidence

### Measurements

`sims/bestofseven/bestofseven.py --measure-only` with
`projects/bestofseven/manifest.json` (seed 0, 100,000 best-of-seven
series, per-game win probability 0.55, every game drawn up front from
one numpy RandomState stream, series length 4 to 7; exact series
probability as the binomial tail summed in log space with lgamma for
odd lengths up to 2,001, checked with Fraction arithmetic for the best
of seven; log in `media/bestofseven/measure.log`):

- better team won 60,721 of 100,000 series = 60.72%; the other team
  39,279 = 39.28%
- exact best-of-seven probability 38,930,419 / 64,000,000 = 60.83%
  (Fraction and log-space values agree); the seeded count is 0.108
  points below it, one standard deviation being 0.154 points
- series over in 4 games: 13,158 (better team won 9,052, was swept in
  4,106); 5 games: 25,491 (better won 16,424); 6 games: 30,895 (better
  won 18,524); 7 games: 30,456 (better won 16,721)
- game sevens: 30,456 series; the better team won 16,721 = 54.9%
- exact series win probability by length: 1: 55.00%, 3: 57.48%,
  5: 59.31%, 7: 60.83%, 9: 62.14%, 11: 63.31%, 15: 65.35%, 21: 67.90%,
  31: 71.32%, 51: 76.41%, 101: 84.38%
- shortest series giving the better team at least 90%: best of 163
  (90.01%; best of 161 gives 89.87%); 95%: best of 269 (95.01%); 99%:
  best of 539 (99.01%; best of 537 gives 98.99%)

The first exact-probability code summed binomial coefficients as
integers and overflowed converting to float near a best of 1,001; it
was replaced by the lgamma log-space sum, and the Fraction check on
the best of seven confirms the two agree to six decimals.

### Production

- Timeline: the 400 by 250 grid fills in play order from 0.5 s to 8.0 s
  with the racing bars counting alongside, so the final counts 60,721
  and 39,279 are on screen from 8 s, before they are spoken (7.9 to
  12.5 s). The game-seven readout appears with the full grid. The exact
  curve draws from 22 to 27 s and its markers (best of 7, 163, 539) and
  labels appear at 27 s, ahead of "best of one hundred sixty three"
  (26.6 s) and "five hundred thirty nine" (32.2 s). Payoff "best of 7:
  60.7%. nine in ten needs best of 163" fades in at 31.0 s.
- Voice round trip: 123 words, 38.01 s, fifth wording. The first draft
  ran about 41 s and was trimmed. "worse team" was transcribed "worst"
  and became "The other team". "Ninety nine in one hundred" came back
  as "99 and 100" and became "For ninety nine times out of one
  hundred". "sixty point seven" folded to 67 in the normaliser; the
  normaliser (`scripts/normalize.py`) now treats "point" as a number
  boundary so "sixty point seven" and "60.7" both read "60 7".
- Layout fixes from the full-resolution frames: the chart title sat on
  the "best of 539: 99%" label and moved up 36 px; the caption band
  moved from 0.70 to 0.68 to keep clear of it; the "this series" board
  showed one frozen series from 8 s to 40 s and now steps through the
  record four series a second, so the middle of the video has motion
  while the counters hold.
- Inspected after the final render: the contact sheet and frames at
  0.5, 3, 9, 14, 25, 28 and 32 s. The grid fills top to bottom, the
  bars stop at 60.7% and 39.3%, the curve rises through the 90% line at
  163 and the labels clear the title, the payoff fits the frame width.
- Mix: mean -15.9 dB, peak -0.0 dB. Final 40.000 s, 1080x1920, 60 fps,
  h264 plus AAC, music seed 20, faststart MP4.

### Published

- Video id: `ispETEpU3I0` <https://youtu.be/ispETEpU3I0>
- Uploaded private: 2026-09-05 10:00:54 local (Pacific quota day
  2026-09-05, clock verified), `scripts/yt-upload.py bestofseven`.
- QA gate against `projects/bestofseven/metadata.json` after processing
  succeeded: channel `UCWXsZTvrh_OHkzt6v1xkTsw`, uploadStatus processed,
  processingStatus succeeded, no rejection or failure reason, definition
  hd, embeddable, source stream 1080x1920, title, description, tags (as
  a set; YouTube returns them alphabetised), categoryId 27, madeForKids
  false, selfDeclaredMadeForKids false, duration PT41S (YouTube rounds
  40.000 s up), private before the flip. 15 of 15 checks pass. Log in
  `media/bestofseven/publish.log`.
- processingHints empty (faststart MP4).
- Made public: 2026-09-05 10:01:58 +03:00 (07:01:58Z publishedAt). The
  re-read issued in the same second as the update still returned
  privacyStatus private; a second read 15 s later returned public with
  publishedAt 07:01:58Z, so the first read was read-after-write lag,
  not a failed update. No second update was sent.

### Quota for 2026-09-05

Spent 4,961 of the 10,000 daily units on the whole day-seven slate:
4,800 for three `videos.insert`, 3 for the channel-identity check inside
each upload, 150 for three `videos.update`, 7 for QA reads and 1 for the
confirming re-read. That leaves room for a full re-upload plus analytics,
as the cadence rule requires. The investigation's 103 read units fell on
the Sep 4 Pacific quota day, before the reset.
