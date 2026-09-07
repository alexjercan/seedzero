# Produce short: Balls into bins, random versus two choices

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day9

## Goal

Backlog idea "Random versus balanced: ten thousand items signed plus or
minus by coin flip versus a greedy balancing rule; measure the random
drift near one hundred against the balanced drift near three." Day nine
slate, third slot, algorithms pillar. The scalar version is trivial (a
greedy sign rule never drifts past one), so the short uses the classic
balls-into-bins form of the same idea: the same ten thousand balls fall
into one hundred bins in two panels; on the left each ball takes a
random bin, on the right each ball peeks at two bins and takes the
emptier one (the power of two choices). Galton-style motion plus the
channel's two-panel comparison. Measure the tallest and shortest stack
and the spread under each rule, the exact same first pick in both panels,
how often the peek changed the pick, and the spread over many seeds and
at ten times the balls, before scripting.

## Claim

Same ten thousand balls, same one hundred bins, same first pick for
every ball. Top: each ball drops into its random bin. Bottom: each ball
also looks at one more bin and drops into the emptier one. At ten
thousand balls the random stacks run from seventy eight to one hundred
thirty four, gap fifty six; two choices run from ninety eight to one
hundred two, gap four, fourteen times flatter. The second look changed
the pick only three thousand four hundred ninety times. At one hundred
thousand balls the random gap grows to one hundred thirty five; two
choices: five.

## Evidence

### Measurements

`sims/bins/bins.py --measure-only` with `projects/bins/manifest.json`
(seed 0, 100,000 balls, 100 bins, every ball draws two bins, the random
panel takes the first draw, the two-choices panel takes the emptier of
the two with ties to the first; the claim reads at 10,000 balls and the
same run continues to 100,000; numpy RandomState; log in
`media/bins/measure.log`):

- random at 10,000 balls: tallest 134, shortest 78, gap 56, average
  100.0, standard deviation 10.41 (theory sqrt(10,000/100) = 10.0); 17
  bins over 110% of average, 16 under 90%
- two choices at 10,000 balls: tallest 102, shortest 98, gap 4,
  standard deviation 0.80; no bin outside 90..110% of average
- gap ratio at 10,000: 14.0x; the second look changed the pick 3,490
  times in the first 10,000 balls = 34.9%, 34,080 times in all 100,000;
  the two bins were tied 31,172 times in 100,000
- random at 100,000 balls: tallest 1,069, shortest 934, gap 135,
  standard deviation 31.28 (theory 31.6); two choices: tallest 1,002,
  shortest 997, gap 5, standard deviation 0.96; ratio 27.0x
- gap as the balls land (random / two): 3 / 3 at 100, 18 / 5 at
  1,000, 24 / 4 at 2,000, 31 / 8 at 5,000, 56 / 4 at 10,000, 79 / 6 at
  20,000, 115 / 4 at 50,000, 135 / 5 at 100,000
- theory: two choices keep the tallest within about log2(ln 100) = 2.2
  of the average whatever the count
- check: a separate 10,000-ball run at seed 0 makes the same picks and
  choices (prefix property holds): True
- check over seeds 0..999 at 10,000 balls: random gap mean 50.0 (min
  36, max 73), tallest mean 126.0 (115..147); two choices gap mean 5.0
  (min 2, max 10), tallest mean 101.9 (101..104). Seed 0's random gap
  of 56 is an ordinary draw; its two-choices gap of 4 is typical

### Production

- `sims/bins/bins.py` renders two panels of 100 bins on a shared
  vertical scale: balls rain from the top of each panel (log-interpolated
  schedule, 30 balls by 3.5 s, 1,000 by 9.5 s, 10,000 by 14 s, so 134, 78
  and 56 are on screen before "Ten thousand balls in" at 17 s), the
  two-choices panel outlines both candidate bins for the first 60 balls,
  red and grey triangles mark the tallest and shortest stack with a
  colour-matched readout row, a dashed average line, the "second look
  changed the pick 3,490 times" note at 26.5 s, then the same run keeps
  raining from 27 to 33 s to 100,000 balls while the scale zooms out;
  payoff at 33.5 s
- narration `projects/bins/narration.txt`, 104 words; voice round trip
  passed at 36.59 s after rewording "spread" as "gap" (whisper heard
  "pred"), "peek" as "second look" ("peak") and "still five" as "only
  five" ("sil"); the on-screen readout and payoff say "gap" to match;
  music seed 26 at gain 0.18
- `scripts/compose.sh bins`: final.mp4 40.000 s, 1080x1920, 60 fps,
  h264 + aac, faststart, 13.1 MB, mean -15.7 dB, peak -0.0 dB
- inspected: smoke frames at 1, 3, 8, 14.5, 23, 26, 27, 28, 30, 33.5 s,
  three contact sheets and full-resolution frames from final.mp4 at
  17.5, 26.0, 29.5 and 35.0 s. Fixed before the final render: panel
  labels 855 and 970 px wide collided with the ball counters (shortened),
  marker labels overlapped each other and the average label (labels
  moved into the readout row), the 100,000-ball rain started before
  "fourteen times flatter" was spoken (hold extended to 27 s), the
  average label sat under a marker during the rain (outlined). Final
  composite clean: 135 and 5 are on screen from 33 s, before they are
  spoken at 34.5 and 36.5 s

### Published

- Video id: `b5UMZJhc9UY` <https://youtu.be/b5UMZJhc9UY>
- Uploaded private: 2026-09-07 10:01:10 local (07:01:10Z; Pacific quota day
  2026-09-07, clock verified 10:00:19 EEST = 00:00:19 PDT),
  `scripts/yt-upload.py bins`.
- QA gate against `projects/bins/metadata.json` after processing
  succeeded: channel `UCWXsZTvrh_OHkzt6v1xkTsw`, uploadStatus processed,
  processingStatus succeeded, no rejection or failure reason, definition
  hd, embeddable, source stream 1080x1920, title, description, tags (as
  a set), categoryId 27, madeForKids false, selfDeclaredMadeForKids
  false, duration PT41S, private before the flip. 15 of 15 checks pass
  on the publish read at 10:03:02; the first read at 10:01:31, 21 s after
  the upload, found it still processing with definition sd and duration
  P0D (11 of 15), all of which resolved once processing succeeded. Log in
  `media/bins/publish.log`.
- processingHints empty (faststart MP4).
- Made public: 2026-09-07 10:03:04 +03:00 (07:03:04Z) by videos.update on
  status (privacyStatus public, selfDeclaredMadeForKids false,
  containsSyntheticMedia true, embeddable true). The re-read 15 s later
  returned privacyStatus public, madeForKids false,
  selfDeclaredMadeForKids false, embeddable true.

### Quota for 2026-09-07

Shared with the other two day-nine shorts: 4,963 of 10,000 units for the
slate (see task 20260907-084959 for the breakdown). No slot slipped.
