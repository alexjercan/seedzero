# Produce short: Golden angle, a tenth of a degree off

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day6

## Goal

Backlog idea "Golden angle: place one thousand seeds at the golden
angle, then a tenth of a degree off; measure how far packing efficiency
collapses and count the spiral arms that appear." Day six slate, first
slot, chosen because the channel's best format is a two-panel physics
comparison where a tiny difference blows up (double pendulum 1,161
views, pendulum wave 722, billiards 666 in its first day). Same claim
shape: one angle, two panels, one tenth of a degree apart. Measure the
gaps and count the arms.

## Claim

Two discs grow by the same rule: each new seed turns 137.5 degrees from
the last one and the older seeds move out. The bottom disc adds one
tenth of a degree. For three hundred seeds they look the same. At seed
three hundred seventy seven the first two seeds touch; at seed four
hundred ten there are thirty four spiral arms, and from then on the
arms only get longer. At one thousand seeds the golden angle has zero
seeds touching and every neighbor at least one point six seed diameters
away; plus a tenth of a degree has six hundred fifty eight seeds
touching, packed into thirty four arms.

## Evidence

### Measurements

`sims/goldenangle/goldenangle.py --measure-only` with
`projects/goldenangle/manifest.json` (Vogel model, seed k at angle
k x alpha and radius sqrt(n - k), 1,000 seeds, seed width 1.0 spacing
units, touching = centres closer than one seed width; log in
`media/goldenangle/measure.log`):

- golden angle 360/phi^2 = 137.507764 deg; offset 137.607764 deg
- golden at 100, 200, 500, 1,000 seeds: closest pair 1.60 seed widths
  at every count, 0 seeds touching, biggest empty circle 2.99, 2.99,
  2.99, 2.95 seed widths wide, nearest-neighbour index difference mode
  13, 21, 34, 34
- offset at 100 seeds: closest 1.58, 0 touching; at 200: closest 1.30,
  0 touching; at 500: closest 0.93, 158 touching, 34 chains, longest 5;
  at 1,000: closest 0.89, 658 touching, 34 chains of 2 or more seeds,
  34 chains of 3 or more, longest chain 20 seeds, index difference mode
  34 for 85% of the outer seeds
- per-count scan of the offset disc: first touching pair at 377 seeds
  (2 touching, 1 chain); 24 chains at 400 seeds; 34 chains first at 410
  seeds (68 touching); touching 108 at 450, 158 at 500, then +50 per 50
  seeds to 658 at 1,000
- verification of "from then on the arms only get longer" (script run
  in the session over every count from 410 to 1,000): chain count is
  34 at all 591 counts, the touching count never drops, and the longest
  chain never drops (2 at 410, 3 at 411, 4 at 450, 20 at 1,000)
- why 34: 34 x 137.6078 mod 360 = -1.34 deg is the smallest residual
  for k < 200 with the offset (for the golden angle the smallest is
  k = 144 at +1.12 deg), and 34 is a Fibonacci number
- context, not narrated: -0.1 deg gives 0 touching, 21 arms; +0.05 deg
  gives 0 touching; +0.2 deg gives 0 touching but 21 wide ring gaps.
  The backlog's "packing efficiency" claim is weak (biggest gap only
  1.32x wider with the offset), so the short counts touching seeds.

No seed and no randomness: positions are exact functions of k.

### Production

- The disc count runs on `count_keys`: 60 seeds at 0 s, 377 at 16.5 s
  ("Seed three hundred seventy seven" 15.6 to 17.6 s), 410 at 19.5 s
  ("Seed four hundred ten" 18.9 to 20.9 s), 1,000 at 23.5 s ("One
  thousand seeds" at 24.2 s); payoff card "+0.1 deg: 34 arms, 658 seeds
  touching" from 24.5 s. Newest seed and touching seeds are drawn gold;
  each disc has live readouts of the closest pair and the touching
  count.
- The first narration said "every seed after that lands on an arm". A
  check in the session showed the newest seed lands at the centre and
  is not touching; what is true is that the 34 chains persist and only
  grow, so the line became "From then on the arms only get longer."
- Voice round-trip: 116 words, 38.68 s, third wording. "thirty four
  arms" was transcribed as "30 forearms" (now "thirty four spiral
  arms") and "seed widths" as "whits" (now "seed diameters").
- Layout fixes from the frames: the overlay was shortened to
  "137.508 vs 137.608 deg | 1,000 seeds | deterministic" so it fits;
  the caption band moved to 48.7% height between the discs, the discs
  shrank to radius 340 and the readouts sit under each disc; the
  count keys were retimed so each event is on screen when spoken.
- Full-resolution frames at 0.5, 16.6, 17, 20, 21.2, 24.5, 28.5 and
  36 s plus the contact sheet inspected after the final compose.
- Mix: mean -15.4 dB, peak -0.0 dB. Final 40.00 s, 1080x1920, 60 fps,
  music seed 15.

### Handoff verification (2026-09-04 09:32)

Re-checked before upload, in a second session:

- `--measure-only` re-run reproduces every number. The stored log was
  written before the print was compacted, so it was regenerated; the old
  one is kept as `media/goldenangle/measure-superseded-print.log`. The
  current log's event line reads: first touching pair at 377 seeds
  (16.50 s of video), 34 touching chains from 410 seeds (19.50 s),
  "every new seed adds exactly one touching seed: False" (the check that
  forced the narration rewrite), 1,000 seeds at 23.50 s.
- "From then on the arms only get longer" re-verified over all 591 counts
  from 410 to 1,000: chain count is 34 at every count, the touching count
  and the longest chain never drop, ending at 658 touching and a longest
  chain of 20. Log: `media/goldenangle/arms-check.log`.
- Voice round trip re-run against the shipped `voice.wav`: transcript
  matches `narration.txt` after normalisation. Duration 38.68 s.
- `final.mp4` re-probed: 1080x1920, 60 fps, h264 High, AAC, 40.000 s.
  Mean -15.4 dB, peak -0.0 dB, matching the recorded mix.
- Six full-resolution frames re-extracted from the final (0.5, 8, 16,
  24.5, 30, 36 s) and inspected: overlay and payoff fit inside the frame,
  captions sit clear of both readout lines, the count keys land on the
  spoken events.

### Published

- Video id: `PqQJxCkhUAo` <https://youtu.be/PqQJxCkhUAo>
- Uploaded private: 2026-09-04 10:01 local (just after the midnight
  Pacific quota reset), `scripts/yt-upload.py goldenangle`.
- QA gate against `projects/goldenangle/metadata.json` after processing
  succeeded: channel `UCWXsZTvrh_OHkzt6v1xkTsw`, uploadStatus
  processed, processingStatus succeeded, no rejection or failure reason,
  definition hd, embeddable, source stream 1080x1920, title, description,
  tags, categoryId 27, madeForKids false and selfDeclaredMadeForKids
  false all matching. 15 of 15 checks pass.
- Two check definitions were corrected during the gate, not the video:
  YouTube returns tags alphabetised rather than in submission order, and
  it rounds the reported duration up, so a 40.000 s upload reads back as
  PT41S. The already-published 40.000 s short `-Jkxs7kNpCg` reports the
  same PT41S, which confirms it is normal for this pipeline.
- Made public: 2026-09-04 10:02:50 +03:00 (07:02:49Z). Re-read after the flip confirms
  privacyStatus public with the synthetic-media disclosure preserved.
