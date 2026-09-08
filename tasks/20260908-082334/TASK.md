# Produce short: Benford's law, doubling versus counting

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day10

## Goal

Backlog idea "Benford's law: leading digits of powers of two; count the
ones versus the nines." Day ten slate, third slot, algorithms pillar.
The 2026-09-08 briefing warned this one is naturally a static bar chart
and asked for it only as powers marching past with the histogram
building live, so the short is two panels taking the same steps: the top
panel counts up one at a time, the bottom panel doubles; at every step
the leading digit of the current number drops as a ball into one of nine
bins. Counting fills the bins evenly, doubling piles them on 1, so the
panels visibly diverge. No randomness anywhere: exact integers, no seed.
Measure the leading-digit counts after 1,000 and 10,000 steps, the
counts for 1 and 9, their ratio and Benford's exact shares before
scripting.

## Claim

Count to one thousand: one hundred twelve numbers start with one, one
hundred eleven start with nine. Double one thousand times instead: three
hundred one start with one, only forty five start with nine, six point
seven to one. Two to the nine hundred ninety nine has three hundred one
digits. Ten thousand steps: three thousand ten against four hundred fifty
eight; thirty percent of the doubled numbers start with one.

## Evidence

### Measurements

`sims/benford/benford.py --measure-only` with
`projects/benford/manifest.json` (exact Python integers 1..10,000 and
2^0..2^9,999, leading digit from the decimal string; log in
`media/benford/measure.log`):

- counting after 1,000 steps: 1: 112, 2 to 9: 111 each; leading 1 11.2%,
  leading 9 11.10%, ratio 1.01 to 1
- doubling after 1,000 steps: 1: 301, 2: 176, 3: 125, 4: 97, 5: 79, 6:
  69, 7: 56, 8: 52, 9: 45; leading 1 30.1%, leading 9 4.50%, ratio 6.69
  to 1
- Benford exact log10(1 + 1/d): 30.1%, 17.6%, 12.5%, 9.7%, 7.9%, 6.7%,
  5.8%, 5.1%, 4.6%; at 1,000 steps 1 leads 301.0 times and 9 leads 45.8,
  ratio 6.58 to 1
- 2^999 has 301 digits; 2^9,999 has 3,010 digits
- counting after 10,000 steps: 1: 1,112, 2 to 9: 1,111 each
- doubling after 10,000 steps: 1: 3,010, 2: 1,761, 3: 1,249, 4: 970, 5:
  791, 6: 670, 7: 579, 8: 512, 9: 458; leading 1 30.1%, leading 9 4.58%,
  ratio 6.57 to 1
- running counts (doubling 1 / 9; counting 1 / 9): 3/0 and 2/1 after 10
  steps, 30/5 and 12/11 after 100, 151/23 and 111/11 after 500, 301/45
  and 112/111 after 1,000, 1,505/226 and 1,111/111 after 5,000,
  3,010/458 and 1,112/1,111 after 10,000

### Production

- `sims/benford/benford.py` renders two panels on one shared bar scale:
  a header, the current number with its leading digit in the panel colour
  (the doubling panel shows the first fourteen digits and the digit
  count), nine bins with bars, a white ball carrying the leading digit
  that drops from the number into its bin at every step, readouts "starts
  with 1" and "starts with 9"; step schedule log-interpolated from step 1
  before 0.0 s to 4 at 2.4 s, 8 at 4.6 s, 120 at 8.0 s and 1,000 at 11.0
  s (the narration reads the 1,000-step numbers from 11.2 s), a hold to
  23.5 s during which the bars named by the narration pulse white and
  keep their count label (count 1 at 12.9 s, count 9 at 15.7 s, double 1
  at 17.7 s, double 9 at 19.8 s), then the same run continues to 10,000
  steps by 28.3 s while the scale zooms out (the narration reads the
  10,000-step numbers from 27.7 s); payoff line at 18.6 s, replaced by the
  10,000-step line at 29.0 s; from 31.6 s, once the
  10,000-step sentence has been read, the first 1,000 steps replay over
  7.9 s for motion, tagged "(replay)"
- narration `projects/benford/narration.txt`, 102 words; voice round trip
  passed at 35.29 s after rewording "Doubling: three hundred one" (came
  back "dou bling") as "Double instead:", "doublings" as "the doubled
  numbers" and "onto" (came back "on to") as "up on"; music seed 29 at
  gain 0.18
- compose: footage 2,400 frames at 60 fps, final.mp4 40.000 s, 1080x1920,
  h264 crf 16, moov before mdat, 6.5 MB; mean volume -16.4 dB, peak
  0.0 dB (limiter)
- inspection: contact sheet and full-resolution frames at 0.0, 13.5,
  20.0, 30.5, 31.0, 33.5 and 34.0 s from final.mp4; the first cut held
  static bars for 12 s twice, against the channel evidence, so the bars
  named by the narration now pulse with their count and the first 1,000
  steps replay at the end; the first replay cut started at 30.0 s while
  "three thousand ten against four hundred fifty eight" was still being
  read over empty bins, so the replay moved to 31.6 s, after the
  sentence; the finals show the 1,000-step bars with 112 and 45 labelled
  when spoken, the 10,000-step bars and readouts 1,112 / 1,111 and
  3,010 / 458 on screen through the sentence at 31 s, and the replay
  balls carrying their digits into the bins at 33.5 s

### Published

- clock before upload: 10:00:19 EEST 2026-09-08 = 00:00:19 PDT, the
  fresh Pacific quota day
- uploaded private to the Seed Zero channel (UCWXsZTvrh_OHkzt6v1xkTsw)
  via `scripts/yt-upload.py`: video HkqX1e1EK_M, publishedAt 10:00:36 EEST
  (log in `media/benford/upload.log`)
- QA gate (scratchpad yt-qa.py, videos.list): 15 of 15 on the first read
  at 10:01 EEST: Seed Zero channel, uploadStatus processed,
  processingStatus succeeded, no rejection, HD, embeddable, 1080x1920,
  title, description, tags, categoryId 27, madeForKids false,
  selfDeclaredMadeForKids false, duration PT40S, private
- published (videos.update privacyStatus public, containsSyntheticMedia
  true) at 10:01:58 EEST; re-read 15 s later: public, madeForKids false,
  selfDeclaredMadeForKids false, embeddable true
- public URL: https://youtu.be/HkqX1e1EK_M

### Quota

- this short: 1,600 (insert) + 1 (channel check) + 1 (gate read) + 52
  (publish and re-read) = 1,654 units; the day 10 slate together about
  4,962 of 10,000, leaving room for one re-upload and analytics reads
