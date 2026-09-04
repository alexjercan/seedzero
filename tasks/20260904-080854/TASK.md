# Produce short: Pi race, Leibniz versus Ramanujan

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day6

## Goal

Backlog idea "Pi race: Leibniz versus Ramanujan series with digits
locking in on screen; measure terms needed for seven correct digits,
about five million versus two." Day six slate, second slot, algorithms
in motion pillar, chosen because the race format with honest counters
works on this channel (sorting race 487 views, A-star 975). Measure the
term at which each partial sum reaches each digit count, with exact
integer arithmetic so the counts cannot depend on floating point.

## Claim

Two formulas for pi race to seven correct digits. Leibniz (four, minus
four thirds, plus four fifths, ...) is off by a thousandth after a
thousand terms and by a millionth after a million terms; its seventh
digit only stops changing at term two million, eight hundred eighty six
thousand, seven hundred fifty. Ramanujan's 1914 series has seven digits
right after one term and sixteen after two.

## Evidence

### Measurements

`sims/pirace/pirace.py --measure-only` with `projects/pirace/manifest.json`
(6,000,000 Leibniz terms in 30-digit integer arithmetic, Ramanujan with
exact Fractions and a 60-digit isqrt for sqrt 2, reference pi from
Machin's formula at 40 digits; log in `media/pirace/measure.log`):

- Leibniz partial sums: term 1: 4.0; term 2: 2.666...; term 3: 3.466...;
  term 1,000: 3.140592653839... (off by 1.0e-3); term 1,000,000:
  3.141591653589... (off by 1.0e-6)
- Leibniz digits first correct and locked (locked = the term after the
  last wrong term, guaranteed by the alternating-series tail bound
  4/(2N+3) at N = 6,000,000): 1 digit first at 3, locked from 7; 2 at
  19 / 25; 3 at 119 / 627; 4 at 1,688 / 2,454; 5 at 10,794 / 136,120;
  6 at 136,121 / 376,847; 7 at 1,530,012 / 2,886,750; 8 or more never
  in six million terms
- Ramanujan: 1 term 3.14159273001330..., 7 correct digits, error
  7.642e-08; 2 terms 16 correct digits, error 6.395e-16; 3 terms 24
  correct digits, error 5.682e-24
- ratio for seven digits: 2,886,750 to 1

No seed and no floating point in the sums, so the numbers are exact by
construction. The earlier backlog guess of "about five million versus
two" was wrong on both sides: the measured answer is 2,886,750 versus 1.

### Production

- The term counter runs on a logarithmic clock (`term_keys`): terms 1
  to 4 are held while each one is spoken (1 at 2.0 to 5.2 s, 2 at 5.8
  s, 3 at 6.9 s, 4 at 8.0 to 8.7 s), then 10 at 8.9 s, 1,000 at 16.8 s,
  one million at 19.4 s and 2,886,750 at 27.0 s, where "finally stops"
  is spoken (26.95 to 27.70 s). Ramanujan's first term appears at 9.5 s
  and the second at 12.8 s, both as they are spoken. The digit strip
  shows 16 digits; locked digits are bright, the rest dim.
- Voice round-trip: 103 words, 38.77 s. "Leibniz" was transcribed as
  "lebanese", so the narration says "the top one" and the name stays on
  screen. A 123-word draft ran 44.2 s and was trimmed.
- Fixes before the final render: the stored dense partial sums were
  raised to 3,000,000 so the lock term is inside them; the error chart
  is drawn from 400 log-spaced stored sums instead of frame history (the
  first version showed one dot); the Ramanujan formula gained its
  prefactor line; the zoom window label prints 0.985 instead of 9.9e-1
  above 1e-3; "1 terms" became "1 term".
- Full-resolution frames at 0.5, 3, 5.6, 7.8, 8.6, 9.6, 10, 17, 27 and
  33 s plus the contact sheet inspected after the final render: captions
  sit between the Ramanujan readouts and the chart, the overlay fits,
  the chart shows the Leibniz line and both Ramanujan dots.
- Mix: mean -15.9 dB, peak -0.0 dB. Final 40.00 s, 1080x1920, 60 fps,
  music seed 16.

### Handoff verification (2026-09-04 09:32)

Re-checked before upload, in a second session:

- `--measure-only` re-run reproduces every number: the digit lock terms
  (7 / 25 / 627 / 2,454 / 136,120 / 376,847 / 2,886,750), the Ramanujan
  errors (7.642e-08, 6.395e-16, 5.682e-24) and the 2,886,750-to-1 ratio
  are byte-identical. Only the print changed after the log was written
  (the strip now shows 16 digits, and each sampled term prints its error
  as roughly 1/N), so the log was regenerated; the old one is kept as
  `media/pirace/measure-superseded-print.log`.
- Voice round trip re-run against the shipped `voice.wav`: transcript
  matches `narration.txt` after normalisation. Duration 38.77 s.
- `final.mp4` re-probed: 1080x1920, 60 fps, h264 High, AAC, 40.000 s.
  Mean -15.9 dB, peak -0.0 dB, matching the recorded mix.
- Six full-resolution frames re-extracted from the final (0.5, 8, 16, 27,
  33, 38 s) and inspected. The error chart was checked at full zoom: the
  axis runs to 1e-16, so both Ramanujan dots (7.6e-08 and 6.4e-16) sit
  inside the plot box, the second one below the 1e-13 gridline as it
  should.

### Published

- Video id: `7H-27Updk5g` <https://youtu.be/7H-27Updk5g>
- Uploaded private: 2026-09-04 10:01 local (just after the midnight
  Pacific quota reset), `scripts/yt-upload.py pirace`.
- QA gate against `projects/pirace/metadata.json` after processing
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
- Made public: 2026-09-04 10:02:52 +03:00 (07:02:52Z). Re-read after the flip confirms
  privacyStatus public with the synthetic-media disclosure preserved.
