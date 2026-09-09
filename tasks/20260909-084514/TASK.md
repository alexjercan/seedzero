# Produce short: Dzhanibekov flip, which one flips

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day11

## Goal

Backlog idea "Dzhanibekov flip: a box in zero g spun about the
intermediate axis versus the long axis with the same tiny wobble; measure
the first flip time, the flip period and the count of flips in forty
seconds, with the long axis never flipping; check energy and angular
momentum conservation." Day eleven slate, second slot. Chosen because the
research run found the flip circulating as a short with high demand, and
because it is a two-panel same-input physics comparison, the format the
channel's numbers reward. Question in the first two seconds: "Which one
flips?" One setup number (the spin rate), one payoff number (the flip
count or period). Euler's equations with RK4, a projected box renderer.

## Claim

Which one flips? Same brick, same spin of one turn per second, same tiny
wobble. Spun about its long axis the brick is steady: not one flip, not
even a wobble you can see. Spun about its middle axis any wobble doubles
and doubles until the brick turns right over, then flips back: a flip
every six point eight seconds, six by the end of the video.

## Evidence

### Measurements

`sims/dzhanibekov/dzhanibekov.py` with `projects/dzhanibekov/manifest.json`
(Euler's rigid-body equations with a quaternion, RK4 at 1,200 steps per
second, deterministic, no seed; log in `media/dzhanibekov/measure.log`):

- brick 1 x 2 x 3, unit mass: moments of inertia x 1.0833, y 0.8333,
  z 0.4167 (long axis z smallest, middle axis y, thin axis x largest);
  spin 6.2832 rad/s, wobble 0.001 rad/s on the other two axes
- linearised growth rate about the middle axis 3.0183 per second; first
  flip predicted near 2.90 s
- long axis: 0 flips in 40 s; largest tilt of the spin axis from the
  angular momentum 0.0320 deg; energy drift 4.1e-14, |L| drift 2.1e-14
- middle axis: 6 flips at 3.041, 9.851, 16.661, 23.472, 30.282, 37.092 s;
  period mean 6.810 s (min 6.810, max 6.810); one flip from 10 to 170 deg
  takes 1.615 s; tilt 0.0127 deg at frame 0, 0.2423 at 1 s, 4.952 at 2 s,
  22.13 at 2.5 s; energy drift 2.5e-13
- checks: thin axis 0 flips, largest tilt 0.0107 deg; wobble 1e-6 first
  flip 5.329 s, 4 flips, period 11.330 s; wobble 0.01 first flip 2.278 s,
  8 flips, period 5.285 s

### Production

- `sims/dzhanibekov/dzhanibekov.py` renders two bricks in a tilted
  camera with back-face culling, one face pair teal and one gold so a flip
  is visible, a red rod along the spin axis with a ball at its plus end,
  a "flips: N" counter (gold once it is above zero), the axis tilt, and a
  0 to 40 s timeline with a gold tick per flip; the question "Which one
  flips?" is drawn for the first 3 s; payoff at 23.0 s in two lines
  ("middle axis: a flip every 6.8 s / long axis: never")
- narration `projects/dzhanibekov/narration.txt`, 102 words; the round
  trip passed at 34.040 s after rewording "The wobble grows" (came back
  "wob ble") as "Its tilt grows" and dropping "The gold side now faces
  you", which would have been false after the second flip; captions:
  "Bottom brick: a flip" at 23.29 s, "every six point eight seconds"
  to 26.30 s, "Top brick: never." at 28.63 s, last caption ends 34.64 s;
  music seed 32 at gain 0.18
- compose: 2,400 frames at 60 fps, final.mp4 40.000 s, 1080x1920, h264,
  aac, moov before mdat; mean volume -16.1 dB, peak -0.1 dB
- inspection: contact sheet plus full-resolution frames at 1.0, 3.6, 24.0
  and 33.5 s from final.mp4; fixed a wrong Euler derivative, the gold
  face showing at rest, identical silhouettes for the two bricks, dark
  shading, a one-line payoff too wide for the frame (now two lines), an
  overlay 1,287 px wide (shortened to 913 px) and flip ticks crossing the
  timeline labels; the finals show the question with both bricks at
  1.0 s, the first flip under way at 3.6 s, and the payoff on screen at
  24.0 s while it is spoken

### Published

- clock before upload: 10:00:19 EEST 2026-09-09 = 00:00:19 PDT, the
  fresh Pacific quota day
- uploaded private to the Seed Zero channel (UCWXsZTvrh_OHkzt6v1xkTsw)
  via `scripts/yt-upload.py`: video nNsIK9nWsUY, publishedAt 10:00:28 EEST
  (log in `media/dzhanibekov/upload.log`)
- QA gate (scratchpad yt-qa.py, videos.list): 15 of 15 on the first read
  at 10:01 EEST: Seed Zero channel, uploadStatus processed,
  processingStatus succeeded, no rejection, HD, embeddable, 1080x1920,
  title, description, tags, categoryId 27, madeForKids false,
  selfDeclaredMadeForKids false, duration PT41S (40.000 s rounds up),
  private
- published (videos.update privacyStatus public, containsSyntheticMedia
  true) at 10:01:35 EEST; re-read 15 s later: public, madeForKids false,
  selfDeclaredMadeForKids false, embeddable true (log in
  `media/dzhanibekov/publish.log`)
- public URL: https://youtu.be/nNsIK9nWsUY

### Quota

- this short: 1,600 (insert) + 1 (channel check) + 1 (gate read) + 52
  (publish and re-read) = 1,654 units; the day 11 slate together about
  4,962 of 10,000, leaving room for one re-upload and analytics reads
