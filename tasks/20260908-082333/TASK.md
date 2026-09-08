# Produce short: Streak test, which coin is fair

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day10

## Goal

Backlog idea "Streak test: ten thousand seeded runs of one hundred coin
flips; measure how many contain a streak of six or more (expect nearly
all; corrects the gambler's fallacy 'due for tails' intuition)." Day ten
slate, second slot, probability pillar as a two-panel same-draws
comparison with continuous motion (the format the channel numbers
reward). Two coins flip from the same seeded draws: the top coin is
fair, the bottom coin gets the same intended flip but is never allowed
past three in a row. Coins land in rows that glide upward; a coin inside
a streak of six or more lights up gold, so the panels visibly diverge.
The hook is a quiz: which coin is the fair one. Measure the share of runs
holding streaks of five to ten or more, the longest streak, the exact
transfer-matrix probabilities and independent seeds before scripting.

## Claim

One of these coins is fair, the other never runs past three in a row.
Same random draws, seed zero, ten thousand runs of one hundred flips.
The top coin is the fair one: eight thousand one hundred two of ten
thousand runs held six or more in a row, five thousand four hundred forty
three held seven or more, eight hundred seventy nine held ten or more;
the longest streak was twenty one. The bottom coin never streaked once,
and it is the fake.

## Evidence

### Measurements

`sims/streaks/streaks.py --measure-only` with
`projects/streaks/manifest.json` (seed 0, 10,000 runs of 100 flips, numpy
RandomState uniform draws; fair coin heads when the draw is under 0.5;
the safe coin takes the same intended flip unless it would be a fourth in
a row, then switches; log in `media/streaks/measure.log`):

- fair coin, runs with a streak of 4 or more: 9,999 of 10,000 (exact
  100.0%); 5 or more: 9,714 = 97.1% (exact 97.2%); 6 or more: 8,102 =
  81.0% (exact 80.7%); 7 or more: 5,443 = 54.4% (exact 54.2%); 8 or
  more: 3,204 = 32.0% (exact 31.5%); 10 or more: 879 = 8.8% (exact 8.7%)
- fair coin longest streak: 21, in run 6,269; mean longest per run 6.99;
  heads 49.92%
- fair coin longest-streak histogram: 3: 1, 4: 285, 5: 1,612, 6: 2,659,
  7: 2,239, 8: 1,500, 9: 825, 10: 448, 11: 216, 12: 119, 13: 44, 14: 26,
  15: 15, 16: 5, 17: 3, 18: 2, 21: 1
- safe coin: 0 of 10,000 runs hold 4 or more; longest 3 in every run;
  heads 49.97%; it agreed with the fair coin on 930,039 of 1,000,000
  flips (69,961 forced switches)
- exact probabilities from a transfer matrix over the current run length
  (`exact_no_run`): printed beside each measured share above
- check: fair coin at seed 1: 8,029 of 10,000 runs hold 6 or more;
  longest 21
- check: 100 runs per seed over seeds 0..99: mean 80.0 of 100 hold 6 or
  more (min 70, max 89) against exact 80.7%

### Production

- `sims/streaks/streaks.py` renders two panels of coin rows (25 coins a
  row, four rows a run, fifteen rows visible) that glide upward as flips
  land, the newest three coins tumbling in; heads blue, tails slate, a
  coin inside a streak that reaches six turns gold the moment the sixth
  lands; thin lines separate runs; headers carry the label, the longest
  streak so far and "runs with 6+ in a row: X of Y"; labels read coin A
  and coin B until the reveal at 12.4 s, then "fair coin" and "same
  draws, never past 3"; flip schedule log-interpolated from 25 flips
  before 0.0 s (the first row is on screen in frame 0) to 100 at 4.0 s,
  300 at 10.5 s, 2,000 at 12.5 s and all 1,000,000 at 15.0 s, so 8,102
  of 10,000 is on screen before it is spoken at 15.3 s; payoff at 18.0 s;
  from 20.0 s runs 1 to 4 replay over 19.5 s with the totals held
- narration `projects/streaks/narration.txt`, 111 words; voice round trip
  passed at 32.06 s after rewording "Real coins streak" (came back
  "coin") as "A real coin streaks" and dropping "in run six thousand two
  hundred sixty nine" (came back "runs"); music seed 28 at gain 0.18
- compose: footage 2,400 frames at 60 fps, final.mp4 40.000 s, 1080x1920,
  h264 crf 16, moov before mdat, 15.5 MB; mean volume -16.1 dB, peak
  0.0 dB (limiter)
- inspection: contact sheet and full-resolution frames at 0.0, 11.0,
  14.0, 18.5 and 30.0 s from final.mp4; smoke frames found nearly every
  coin gold because the highlight ignored whether a streak reached six
  (fixed with a per-flip final streak length), the big tally colliding
  with the longest-streak label (header restructured), coins tumbling up
  into the header at high flip rates (only the newest three tumble) and a
  payoff line too wide for the frame (shortened); the finals show a full
  first row in frame 0 with the newest coins tumbling in, gold only on
  runs of six or more in the top panel and never in the bottom one, the
  reveal labels and "8,102 of 10,000" on screen before they are spoken,
  the payoff at 18.5 s, and the replay building rows at 30 s

### Published

- clock before upload: 10:00:19 EEST 2026-09-08 = 00:00:19 PDT, the
  fresh Pacific quota day
- uploaded private to the Seed Zero channel (UCWXsZTvrh_OHkzt6v1xkTsw)
  via `scripts/yt-upload.py`: video w50iLhHg-8o, publishedAt 10:00:29 EEST
  (log in `media/streaks/upload.log`)
- QA gate (scratchpad yt-qa.py, videos.list): 15 of 15 on the first read
  at 10:01 EEST: Seed Zero channel, uploadStatus processed,
  processingStatus succeeded, no rejection, HD, embeddable, 1080x1920,
  title, description, tags, categoryId 27, madeForKids false,
  selfDeclaredMadeForKids false, duration PT40S, private
- published (videos.update privacyStatus public, containsSyntheticMedia
  true) at 10:01:40 EEST; re-read 15 s later: public, madeForKids false,
  selfDeclaredMadeForKids false, embeddable true
- public URL: https://youtu.be/w50iLhHg-8o

### Quota

- this short: 1,600 (insert) + 1 (channel check) + 1 (gate read) + 52
  (publish and re-read) = 1,654 units; the day 10 slate together about
  4,962 of 10,000, leaving room for one re-upload and analytics reads
