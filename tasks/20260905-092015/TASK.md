# Produce short: Random walk home, line versus plane

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day7

## Goal

Backlog idea "Random walk versus drunk walk home: measure
return-to-origin times in one and two dimensions." Day seven slate,
second slot, probability pillar in the channel's two-panel comparison
format: the same coin, the same seed, the same number of steps, one
extra dimension. Measure how many of ten thousand walkers have been
back home by a fixed step count on the line and on the plane, and how
long the walkers that do return take.

## Claim

Ten thousand walkers on a line and ten thousand on a plane, same coin,
same seed, one unit a step. On the line half have been home after two
steps, ninety two percent after one hundred steps, ninety seven percent
after one thousand. On the plane a quarter after two steps, fifty eight
percent after one hundred, sixty eight percent after one thousand.
After two thousand steps two hundred seven walkers are still out on the
line and three thousand thirteen on the plane, fifteen times as many.

## Evidence

### Measurements

`sims/randomwalk/randomwalk.py --measure-only` with
`projects/randomwalk/manifest.json` (seed 0, 10,000 walkers per world,
2,000 steps, one unit per step in a uniformly random axis direction,
numpy RandomState; a walker counts as home once it has stood on the
origin at least once; log in `media/randomwalk/measure.log`):

- line: home at least once by step 2: 5,053 (50.53%), step 10: 7,530
  (75.30%), step 100: 9,178 (91.78%), step 1,000: 9,716 (97.16%), step
  2,000: 9,793 (97.93%); still out at step 2,000: 207 = 2.07%
- line exact probability of no return by step n (central binomial over
  4^k): 0.5000, 0.2461, 0.0796, 0.0252, 0.0178 at steps 2, 10, 100,
  1,000, 2,000
- line first-return step among the 9,793 that got home: median 2, mean
  37.3, latest 1,998; percentiles 50/75/90/99: 2, 10, 48, 852
- plane: home by step 2: 2,480 (24.80%), step 10: 4,182 (41.82%), step
  100: 5,822 (58.22%), step 1,000: 6,771 (67.71%), step 2,000: 6,987
  (69.87%); still out at step 2,000: 3,013 = 30.13%
- plane first-return step among the 6,987 that got home: median 6,
  mean 102.1, latest 1,994; percentiles 50/75/90/99: 6, 40, 274, 1,542
- still out at step 2,000: plane 3,013 against line 207 = 14.6 times
  as many ("fifteen times" in the narration)
- context, not narrated: three dimensions at the same seed, home by
  step 2,000: 3,335 (33.35%), 6,665 still out
- check, not narrated: 100,000 line walkers at seed 1 leave 1,805
  still out at step 2,000 = 1.80% against the exact 1.78%

The seed 0 line count (2.07% still out) sits 2.2 standard deviations
above the exact 1.78%. The seed 1 check with ten times the walkers
lands on the exact value, so the code is right and seed 0 is simply a
slightly high draw. The narration states the seed 0 counts as measured
and the description gives the exact figures.

### Production

- Timeline: piecewise-linear step clock (`step_keys`): step 2 at 3.0 s,
  step 10 at 6.0 s, step 100 at 13.5 s, step 1,000 at 21.0 s, step 2,000
  at 27.5 s, then hold; each spoken count is on screen when it is said
  (half home on the line at 3.0 s, 92% at 13.5 s, 97% at 21 s, 207 and
  3,013 still out from 27.5 s). Payoff "line: 98% home. plane: 70% home"
  fades in at 29.0 s.
- Voice round trip: 115 words, 36.17 s, fourth wording. The first
  draft ran 43.27 s and was trimmed. "Teal" was transcribed "deal" and
  became "turns green" (the home colour is drawn teal-green). "step one
  hundred, ninety two percent" folded to 192 in the normaliser and
  became "After one hundred steps, ninety two percent".
- The seed 0 line count is 2.2 standard deviations above the exact
  value, so an independent 100,000-walker check at seed 1 was added to
  the measurement (1.80% against 1.78%) before the narration was
  approved. The title first said "never got home", which is wrong for a
  finite walk; it now says "still out".
- Layout fix from the full-resolution frames: the overlay "seed 0 |
  10,000 walkers each | 2,000 steps | deterministic" ran off both edges;
  it is now "seed 0 | 10,000 walkers each | deterministic".
- Inspected after the final compose: the contact sheet and frames at 1,
  12 and 30 s (plus 5, 20, 26 and 36 s from the previous compose, which
  differed only in the overlay). The line histogram turns teal from the
  centre out, the plane cloud grows with a teal core, captions sit
  between the line readout and the plane label.
- Mix: mean -16.0 dB, peak -0.0 dB. Final 40.000 s, 1080x1920, 60 fps,
  h264 plus AAC, music seed 19, faststart MP4.

### Published

- Video id: `D0H64ZV2lB4` <https://youtu.be/D0H64ZV2lB4>
- Uploaded private: 2026-09-05 10:00:48 local (Pacific quota day
  2026-09-05, clock verified), `scripts/yt-upload.py randomwalk`.
- QA gate against `projects/randomwalk/metadata.json` after processing
  succeeded: channel `UCWXsZTvrh_OHkzt6v1xkTsw`, uploadStatus processed,
  processingStatus succeeded, no rejection or failure reason, definition
  hd, embeddable, source stream 1080x1920, title, description, tags (as
  a set; YouTube returns them alphabetised), categoryId 27, madeForKids
  false, selfDeclaredMadeForKids false, duration PT41S (YouTube rounds
  40.000 s up), private before the flip. 15 of 15 checks pass. Log in
  `media/randomwalk/publish.log`.
- processingHints empty (faststart MP4).
- Made public: 2026-09-05 10:01:55 +03:00 (07:01:55Z publishedAt).
  Re-read confirms privacyStatus public.
