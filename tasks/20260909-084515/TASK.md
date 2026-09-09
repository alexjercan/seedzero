# Produce short: Ant double bridge, do ants find the shortest path

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day11

## Goal

Backlog idea "Ant double bridge (pillar idea, ant trails): same colony
and seed; short and long bridge open from the start versus the short
bridge opening later; measure the share of trips on the short bridge at
ten minutes; expect about nine in ten against a minority: the colony that
found the long path first keeps it." Day eleven slate, third slot, the
emergence pillar's ant trails, and the audience's own recurring question
"do ants find the shortest path". Two panels, the same colony and the
same random draws; the scent on each bridge is the one visible cause.
Question in the first two seconds: "Do ants find the shortest path?"
One setup number (the long bridge is twice as long), one payoff number
per panel (the share of trips on the short bridge at ten minutes).

## Claim

Do ants find the shortest path? One colony, the same random choices, two
bridges to the food, the long one twice as long. Every ant leaves scent
and ants follow the stronger scent. With both bridges open, ants on the
short bridge come back sooner, so its scent builds faster, so more ants
pick it: at minute ten ninety eight percent of trips take the short
bridge. With only the long bridge open at first, its scent builds alone;
when the short bridge opens nobody switches, and at minute ten zero
percent take it. Yes, if they find it first.

## Evidence

### Measurements

`sims/antbridge/antbridge.py` with `projects/antbridge/manifest.json`
(60 ants, seed 0 with one numpy RandomState stream per ant, short bridge
20 s to cross, long bridge 2.0x, Deneubourg choice rule (k + scent)^n
with k 20 and n 2, scent half life 600 s, 2 s pause at each end, one ant
released every 0.5 s, 12 s of pre-roll before the clock starts; log in
`media/antbridge/render.log`):

- open panel (both bridges from the start), share of trips on the short
  bridge by minute: 64.2, 78.0, 84.1, 87.5, 92.9, 95.5, 96.8, 97.0, 98.8,
  98.0 percent; minute 10: 150 short, 3 long crossings; scent 995 short,
  85 long; all ten minutes 1,332 short against 138 long (90.6%); first
  minute at 80 percent or more: minute 3
- late panel (long bridge only, short bridge opens at 480 s): 0 short
  crossings in every minute, 60 to 96 long crossings a minute; minute 10:
  0 short, 96 long; scent 0 short, 607 long; all ten minutes 0 short
  against 830 long (0.0%)
- payoff, minute 10: open panel 98.0%, late panel 0.0%
- checks at seeds 1, 2, 3: open panel minute 10 share 97.4, 96.7, 98.7
  percent; late panel 0.0 percent each time

### Production

- `sims/antbridge/antbridge.py` renders two panels (nest left, food
  right, the short bridge a straight line and the long bridge an arc of
  twice the length) with bridges that thicken and warm from grey to
  orange with scent, white outbound and gold returning ants, a colony
  clock, a readout "short bridge: N% of trips this minute", the late
  panel's short bridge dashed and marked "closed" until it opens at
  8:00 (22.86 s of video, ten colony minutes in 28.6 s at 21x); the
  question "Do ants find the shortest path?" is drawn for the first 3 s;
  payoff at 28.6 s in two lines ("minute 10, top: 98% take the short
  bridge / bottom: 0%")
- narration `projects/antbridge/narration.txt`, 110 words; the round
  trip passed at 36.629 s; the share was corrected from "ninety nine" to
  the measured "ninety eight" after the compression changed to 21x, and
  "The short bridge opens at minute two" became "Then the short bridge
  opens" with the opening moved to minute 8 so it happens as the words
  are spoken; captions: "Top: both bridges" at 11.92 s, "Bottom: only
  the" at 19.25 s, "Then the short" at 22.91 s, "Minute ten." at
  28.57 s (clock 10:00), "Top: ninety eight" at 29.24 s, "Bottom: zero."
  at 32.57 s, last caption ends 37.23 s; music seed 33 at gain 0.18
- compose: 2,400 frames at 60 fps, final.mp4 40.000 s, 1080x1920, h264,
  aac, moov before mdat; mean volume -16.1 dB, peak 0.0 dB
- inspection: contact sheet plus full-resolution frames at 1.0, 14.0,
  22.5, 23.5, 29.5 and 36.0 s from final.mp4; fixed an IndexError in the
  per-minute counts, totals that ran past minute 10, an empty first
  frame (pre-roll added), a payoff line that overflowed the frame
  (shortened and split in two), and the short bridge opening 17 s before
  the narration mentioned it; the finals show the question with ants
  already crossing at 1.0 s, the dashed closed bridge at 22.5 s and the
  open bridge with "Then the short" at 23.5 s, and the payoff with the
  98% readout at 29.5 s

### Published

- clock before upload: 10:00:19 EEST 2026-09-09 = 00:00:19 PDT, the
  fresh Pacific quota day
- uploaded private to the Seed Zero channel (UCWXsZTvrh_OHkzt6v1xkTsw)
  via `scripts/yt-upload.py`: video NywakrCTt94, publishedAt 10:00:33 EEST
  (log in `media/antbridge/upload.log`)
- QA gate (scratchpad yt-qa.py, videos.list): 15 of 15 on the first read
  at 10:01 EEST: Seed Zero channel, uploadStatus processed,
  processingStatus succeeded, no rejection, HD, embeddable, 1080x1920,
  title, description, tags, categoryId 27, madeForKids false,
  selfDeclaredMadeForKids false, duration PT41S (40.000 s rounds up),
  private
- published (videos.update privacyStatus public, containsSyntheticMedia
  true) at 10:01:53 EEST; re-read 15 s later: public, madeForKids false,
  selfDeclaredMadeForKids false, embeddable true (log in
  `media/antbridge/publish.log`)
- public URL: https://youtu.be/NywakrCTt94

### Quota

- this short: 1,600 (insert) + 1 (channel check) + 1 (gate read) + 52
  (publish and re-read) = 1,654 units; the day 11 slate together about
  4,962 of 10,000, leaving room for one re-upload and analytics reads
