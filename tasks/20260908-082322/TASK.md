# Produce short: Coupon collector, the last stickers cost the most

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day10

## Goal

Backlog idea "Coupon collector: how many packs to complete a fifty-sticker
album; measure the expected long tail." Day ten slate, first slot,
probability pillar staged as physical motion, the format the channel
numbers reward (the 2026-09-08 briefing: continuous motion with one thing
visibly diverging holds people, double pendulum 86% average view, Boids
135%; grid-of-counters shorts sit at 26 to 28%). Packs open one at a
time; a new sticker flies into its album slot, a duplicate bounces off
and drops onto a growing pile. The album fill and the pile are the two
things diverging. Measure the packs to complete, the packs spent on the
first forty, the last ten and the last one, the duplicate count, and the
spread over many seeds before scripting. The last frame returns to the
empty album so the short loops.

## Claim

Fifty stickers, one random sticker per pack, seed zero. The first forty
stickers took sixty four packs. The last ten took one hundred thirty six,
more than twice the first forty. Two hundred packs for fifty stickers, one
hundred fifty of them doubles. Ten thousand albums took two hundred
twenty five packs on average; in nine of ten the last ten cost more than
the first forty; more than one in ten needed over three hundred.

## Evidence

### Measurements

`sims/stickers/stickers.py --measure-only` with
`projects/stickers/manifest.json` (seed 0, 50 stickers, one uniform draw
per pack from numpy RandomState; log in `media/stickers/measure.log`):

- album complete after 200 packs; 150 duplicates
- first 40 stickers: 64 packs (exact expectation 50 x (H(50) - H(10)) =
  78.51)
- last 10 stickers: 136 packs (exact expectation 50 x H(10) = 146.45)
- last 1 sticker: 8 packs (exact expectation 50.00; seed 0 got lucky on
  the final sticker, so the narration quotes the ten-thousand-album mean
  of 50.0 for that line, not the seed-0 draw)
- exact expected packs for all 50: 50 x H(50) = 224.96
- sticker 10 found at pack 11, 20 at 25, 30 at 41, 40 at 64, 45 at 126,
  48 at 178, 49 at 192, 50 at 200
- duplicates when 40 were found: 24; at the end: 150
- check over seeds 0..9,999: mean packs 224.7 (exact 224.96), median
  214, sd 62.2, min 96, max 681; mean first 40: 78.5, mean last 10:
  146.2, mean last 1: 50.0
- check: the last 10 cost more than the first 40 in 90.2% of albums
- check: albums needing more than 150 packs 93.1%, more than 200 59.8%,
  more than 300 10.8% (1,076 of 10,000), more than 400 1.6%, more than
  500 0.2%
- check: seed 0 sits at percentile 39 of the 10,000 albums, an ordinary
  draw on the lucky side

### Production

- `sims/stickers/stickers.py` renders a five by ten album of numbered
  slots, a pack origin above it, cards that fly to their slot in 0.25 s
  (new: the slot lights white then settles to its colour; duplicate: the
  card bounces on to a twelve-column brick pile in 0.35 s), a HUD with
  packs opened and stickers found, a duplicates counter over the pile,
  milestone tags under the album (40 found after 64 packs; 50 after 200);
  pack schedule linear from pack 0 at 0.0 s to pack 10 at 2.0 s, pack 64
  at 6.5 s and pack 200 at 15.5 s, so 64 is on screen before "Forty found
  after sixty four packs" at 8.0 s and 200 before "Complete after two
  hundred packs" at 15.8 s; payoff at 21.0 s; from 25.0 s the same 200
  packs replay over 13.5 s while the narration gives the ten-thousand-album
  numbers; at 39.3 s the album and pile wipe to empty so the last frame
  matches the first (loop)
- narration `projects/stickers/narration.txt`, 108 words; voice round trip
  passed at 34.92 s after three rewordings: "Seed zero." as its own
  sentence came back "se ed" twice (moved into the first sentence as
  "Fifty stickers to collect, seed zero."), "averaged" came back
  "average" (now "took ... packs on average"); music seed 27 at gain 0.18
- compose: footage 2,400 frames at 60 fps, final.mp4 40.000 s, 1080x1920,
  h264 crf 16, moov before mdat, 7.2 MB; mean volume -15.8 dB, peak
  -0.0 dB (limiter)
- inspection: contact sheet (40 frames at 1 fps) and full-resolution
  frames at 0.0, 9.0, 16.5, 22.0 and 39.7 s from final.mp4; early smoke
  frames showed the payoff line overflowing the frame (shortened to
  "first 40: 64 packs. last 10: 136 packs"), both milestone tags
  overlapping at completion (now one tag line) and the duplicates label
  crowding the captions (slots shortened, pile lowered, captions at 0.61);
  the finals show the tag "40 found after 64 packs" clear above the
  caption at 9 s, 200 packs and 50 of 50 on screen at 16.5 s while
  "Complete after two hundred packs" is spoken, the payoff under the pile
  at 22 s, and the wiped empty album at 39.7 s matching frame 0

### Published

- clock before upload: 10:00:19 EEST 2026-09-08 = 00:00:19 PDT, the
  fresh Pacific quota day
- uploaded private to the Seed Zero channel (UCWXsZTvrh_OHkzt6v1xkTsw)
  via `scripts/yt-upload.py`: video P_igHVYavLI, publishedAt 10:00:23 EEST
  (log in `media/stickers/upload.log`)
- QA gate (scratchpad yt-qa.py, videos.list): 15 of 15 on the first read
  at 10:01 EEST: Seed Zero channel, uploadStatus processed,
  processingStatus succeeded, no rejection, HD, embeddable, 1080x1920,
  title, description, tags, categoryId 27, madeForKids false,
  selfDeclaredMadeForKids false, duration PT40S, private
- published (videos.update privacyStatus public, containsSyntheticMedia
  true) at 10:01:21 EEST; re-read 15 s later: public, madeForKids false,
  selfDeclaredMadeForKids false, embeddable true
- public URL: https://youtu.be/P_igHVYavLI

### Quota

- this short: 1,600 (insert) + 1 (channel check) + 1 (gate read) + 52
  (publish and re-read) = 1,654 units; the day 10 slate together about
  4,962 of 10,000, leaving room for one re-upload and analytics reads
