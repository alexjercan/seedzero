# Produce short: Seven shuffles, the guesser's edge

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day8

## Goal

Backlog idea "Seven shuffles: riffle shuffle thousands of decks one to
ten times; a card guesser plays each deck and measures its edge over
chance, which survives four shuffles and dies near seven." Day eight
slate, first slot, algorithms pillar, chosen as the slate's race
format (A-star 978 views, sorting race 489): eight rows of fifty two
cards dealt one after another, a guesser scoring each row, and the
score collapsing toward chance. Measure the guesser's average score
after every shuffle count over ten thousand decks, the chance baseline,
and the exact distance from a random deck as a check, before scripting.

## Claim

A deck in factory order, riffled seven times, ten thousand decks per
row at seed zero. A guesser who knows the factory order and remembers
every card it sees still names thirty one cards of fifty two after one
shuffle, twenty after two, thirteen after three, nearly nine after
four, six and a half after five, five and a half after six and five
after seven. A random deck gives four and a half, pure chance. Each
riffle roughly halves the edge over chance.

## Evidence

### Measurements

`sims/shuffles/shuffles.py --measure-only` with
`projects/shuffles/manifest.json` (seed 0, 52 cards, 10,000 decks each
shuffled 10 times with the Gilbert-Shannon-Reeds riffle: cut at
Binomial(52, 1/2), interleave uniformly among all interleavings, numpy
RandomState; the deck after every shuffle is kept, so row k holds the
same decks one shuffle further on; plus 10,000 uniformly random decks;
log in `media/shuffles/measure.log`):

- guesser strategy "longest": the unseen cards form runs of
  consecutive factory ranks; before each card the guesser names the
  first card of the longest run, ties to the run that continues the
  card just seen, then the lowest run. It needs no knowledge of the
  shuffle count. Every strategy names one specific unseen card, so on a
  random deck a guess is right with probability 1 over the cards left
  and the expected score is H_52 = 4.538
- mean right guesses of 52 by shuffle count: 1: 31.18, 2: 19.67,
  3: 12.92, 4: 8.79, 5: 6.59, 6: 5.49, 7: 5.01, 8: 4.78, 9: 4.66,
  10: 4.61; random deck 4.55 (chance 4.54)
- edge over chance: 26.64, 15.13, 8.38, 4.25, 2.05, 0.96, 0.47, 0.25,
  0.12, 0.08: the ratio between consecutive shuffles is 0.57, 0.55,
  0.51, 0.48, 0.47, 0.49, so "each riffle roughly halves the edge"
- medians 31, 20, 13, 9, 6, 5, 5, 5, 5, 4; random 4; best single decks
  44, 31, 24, 18, 16, 14, 13, 14, 14, 14; random 14
- decks scoring above 10 of 52: 100%, 100%, 84.8%, 20.6%, 3.0%, 0.9%,
  0.3%, 0.2%, 0.2%, 0.1%; random 0.1%
- two other strategies measured and not used: "recency" (the next
  unseen card after the one just seen) scores 27.03, 14.82, 9.10, 6.53,
  5.45, 4.94, 4.73 for 1 to 7 shuffles; "capped" (longest, with runs
  capped at 52 over 2^k, so the guesser is told k) 31.18, 19.74, 12.92,
  8.69, 6.37, 4.97, 4.75. Longest is best or tied at every count and
  needs no k, so it is the one on screen
- checks: mean rising sequences 2.00, 4.00, 7.95, 14.09, 19.59, 22.90,
  24.71, 25.61, 26.03, 26.29 (random 26.52, exact 26.5); exact total
  variation distance from a random deck by the Bayer-Diaconis formula
  with exact Eulerian numbers: 1.000, 1.000, 1.000, 1.000, 0.924,
  0.614, 0.334, 0.167, 0.085, 0.043, which is the published table for
  52 cards, so the shuffle model is right
- the rows on screen show lineage 993, the deck whose tallies over rows
  1 to 7 sit closest to the row averages: 31, 19, 13, 9, 7, 6, 5 right;
  the random row shows random deck 6 with 5 right (the first deck whose
  tally is closest to the random mean). The narration quotes the row
  averages; the bar chart on screen shows the running averages over
  all 10,000 decks per row

### Production

- `sims/shuffles/shuffles.py` renders 8 rows (1 to 7 shuffles and a
  random deck) of 52 cards in rainbow rank colours; each row deals its
  cards over 2 s to end as the narration speaks its number (deal ends
  10.2, 12.6, 13.8, 15.2, 17.4, 19.6, 21.6, 23.8 s), a white tick marks
  every right guess, the right count sits at the row's right edge and
  the bar chart of row averages grows with each deal; edge text at 25 s,
  payoff at 30 s. Guesser strategy "longest" per the manifest
- narration `projects/shuffles/narration.txt`, 87 words; voice round
  trip passed on the first try, 32.31 s; music seed 21 at gain 0.18
- `scripts/compose.sh shuffles`: final.mp4 40.000 s, 1080x1920, 60 fps,
  h264 + aac, faststart (moov before mdat), 2.5 MB, mean -17.7 dB, peak
  -0.0 dB
- inspected: contact sheet and full-resolution frames at 1.0, 12.0,
  20.5, 27.0, 33.0, 38.5 s. Defects found on smoke frames and fixed
  before the final render: the chance label sat on top of short bars
  (moved to the chart's top right), the edge text ran into the payoff
  line (chart shrunk, row pitch tightened, captions at 0.60), and PIL
  refused a bar under one pixel (bar guard). Final composite clean:
  captions sit between the rows and the chart title, tallies 31, 19,
  13, 9, 7, 6, 5, 5 match the measured lineage, chart bars 31.2 to 5.0
  and 4.5 match the measured means

### Published

- Video id: `IEzd2tJSBXU` <https://youtu.be/IEzd2tJSBXU>
- Uploaded private: 2026-09-06 10:00:13 local (07:00:13Z; Pacific quota day
  2026-09-06, clock verified 10:00:11 EEST = 00:00:11 PDT),
  `scripts/yt-upload.py shuffles`.
- QA gate against `projects/shuffles/metadata.json` after processing
  succeeded: channel `UCWXsZTvrh_OHkzt6v1xkTsw`, uploadStatus processed,
  processingStatus succeeded, no rejection or failure reason, definition
  hd, embeddable, source stream 1080x1920, title, description, tags (as
  a set), categoryId 27, madeForKids false, selfDeclaredMadeForKids
  false, duration PT40S or PT41S, private before the flip. 15 of 15
  checks pass on 1 gate read. Log in `media/shuffles/publish.log`.
- processingHints empty (faststart MP4).
- Made public: 2026-09-06 10:01:14 +03:00 (07:01:14Z) by videos.update on
  status (privacyStatus public, selfDeclaredMadeForKids false,
  containsSyntheticMedia true, embeddable true). The re-read 15 s later
  returned privacyStatus public, madeForKids false,
  selfDeclaredMadeForKids false, embeddable true.

### Quota for 2026-09-06

Spent 4,963 of the 10,000 daily units on the whole day-eight slate:
4,800 for three `videos.insert`, 3 for the channel-identity check inside
each upload, 150 for three `videos.update`, 7 for gate reads (one per
short before publishing, one extra while the bus upload processed, one
per short inside the publish run) and 3 for the confirming re-reads.
That leaves room for a full re-upload plus analytics, as the cadence
rule requires. No slot slipped.
