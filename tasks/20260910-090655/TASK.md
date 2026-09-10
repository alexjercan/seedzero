# Produce short: Kapitza pendulum, can a pendulum stand upside down

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day12

## Goal

Backlog idea "Kapitza pendulum: the same inverted pendulum with the same
nudge, pivot still versus pivot shaking; measure the fall time of the
still one and the maximum tilt of the shaken one over ten minutes (expect
it never falls)." Day twelve slate, second slot. Chosen because the
channel's measured winners are two-panel same-input physics comparisons
(double pendulum, tautochrone, Dzhanibekov) and this one has a visible
cause that can be switched off on screen. Question in the first two
seconds: "Can a pendulum stand upside down?" One setup number (shakes per
second), one payoff number (how long the shaken one stands against the
still one's fall time). Every number below is printed by the sim before
the script is written.

## Claim

Can a pendulum stand upside down? The same rigid pendulum twice, balanced
on end, the same nudge at the same moment. With its pivot still it tips
over in under half a second, like a pencil on its tip. With its pivot
shaking up and down forty times a second it wobbles but stands, for the
whole video and for a ten minute run. Stop the shaking and it falls in
under a second. The shaking was holding it up.

## Evidence

### Measurements

`sims/kapitza/kapitza.py` with `projects/kapitza/manifest.json` (theta
from the upright, theta'' = (g + y_p'') / l sin theta - damping theta',
RK4 at 2,400 steps per second, deterministic, no seed; log in
`media/kapitza/measure.log`, final run after the timing changes):

- pendulum 10 cm, pivot stroke 1.0 cm each way at 40 Hz (peak pivot
  acceleration 64 g), air drag 0.2 per second on both, nudge 0.5 rad/s
  at 2.5 s on both
- stability: A omega 2.51 m/s against the threshold sqrt(2 g l) 1.40 m/s
  (1.79 times); averaged-motion basin edge 112 deg from upright;
  predicted slow wobble 0.426 s per cycle
- pivot still: tilt passes 90 deg 0.427 s after the nudge (at 2.927 s),
  hangs straight down first at 3.017 s; 182.8 deg from upright at 38 s
- pivot shaking: largest tilt after the nudge and before the kick
  2.35 deg (at 2.60 s); tilt 1.12 deg at 10 s; measured slow wobble
  0.423 s per cycle against 0.426 predicted
- kick 6 rad/s at 15 s on the shaking pendulum only (12 times the nudge):
  swings out to 28.5 deg (at 15.12 s), back under 5 deg at 15.21 s,
  6.51 deg tilt left at 29 s, never fell before the shaking stops
- shaking stops at 29 s (ramped down over 0.3 s): tilt passes 90 deg
  0.429 s later (at 29.429 s), hangs straight down first at 29.519 s
- ten minute run with the shaking never stopped (no kick): largest tilt
  2.35 deg at 2.60 s, largest tilt after the first minute 0.0075 deg,
  never fell
- checks: no drag for two minutes, largest tilt 2.38 deg, never fell,
  wobble 0.423 s; stroke 0.3 cm (A omega 0.75 m/s, below the threshold)
  falls 0.474 s after the nudge; the same run without the kick has
  0.141 deg tilt at 29 s and falls 0.945 s after the shaking stops
- payoff: pivot still fell in 0.43 s; pivot shaking still up until the
  shaking stops at 29 s, then fell in 0.43 s (the residual wobble from
  the kick happened to lean the right way; without the kick 0.95 s)

Narration numbers: under half a second (0.43 s), forty times a second,
under a second (0.43 s). Design changes after the first measurement:
nudge moved from 1.0 s to 2.5 s so the fall is on screen when narrated,
a visible hard kick at 15 s as the mechanism demonstration, shaking
switched off at 29 s to match the words "Now stop the shaking".

### Production

- `sims/kapitza/kapitza.py` renders two panels of the same 10 cm
  pendulum, pivot still above and pivot shaking below (the shaking pivot
  is motion-blurred over 12 sub-samples), each with a header label and a
  readout ("balanced", "up for X s", "fell in X s"), a push arrow at the
  nudge (2.5 s, both) and at the kick (15.0 s, shaking only), shaking
  switched off at 29.0 s with a 0.3 s ramp; the question "Can a pendulum
  stand upside down?" is drawn for the first 2.4 s; payoff from 24.5 s
  ("pivot still: fell in 0.43 s / pivot shaking: still up at N s"),
  which becomes "shaking off at 29 s: fell in 0.43 s" once the bottom
  pendulum has fallen
- narration `projects/kapitza/narration.txt`, 112 words; round trip
  passed at 32.972 s (log `media/kapitza/voice.log`); "Kick it harder"
  is spoken at the 15.0 s kick and "Now stop the shaking" at the 29.0 s
  switch-off; music seed 35 at gain 0.18
- compose: 2,280 frames at 60 fps, final.mp4 38.000 s, 1080x1920, h264,
  aac, faststart; mean volume -15.8 dB, peak 0.0 dB
- text widths measured before rendering: overlay 761 px, title 511 and
  630 px, header label 729 px, readouts 334 and 343 px, payoff 521 and
  726 px (the first payoff line 2 draft was 1,061 px and was shortened)
- inspection: contact sheet plus full-resolution frames at 1.0, 2.8,
  6.0, 15.4, 24.8, 29.5, 33.0 and 37.9 s from final.mp4; fixed the header label
  colliding with the readout (readout moved under the label), the nudge
  word overlapping the readout (shorter arrow, word under the arrow) and
  the over-wide payoff line; the finals show the question and both
  pendulums upright at 1.0 s, the top one fallen at 3 s while the bottom
  one stands, the 28.5 deg kick recovery, the payoff on screen while it
  is spoken, and the bottom pendulum fallen after the shaking stops

### Published

- clock before upload: 10:00:11 EEST 2026-09-10 = 00:00:11 PDT, the
  fresh Pacific quota day
- first upload attempt at 10:00:28 EEST was rejected by the API before
  the media was sent: invalidTitle, because the 106-character title
  "Can a pendulum stand upside down? Pivot still: falls in 0.43 s. Pivot
  shaking 40 times a second: stays up." exceeds YouTube's 100-character
  limit; title shortened to "Can a pendulum stand upside down? Pivot
  still: falls in 0.43 s. Shaking 40 times a second: stays up." (100
  characters) in `projects/kapitza/metadata.json`
- uploaded private to the Seed Zero channel (UCWXsZTvrh_OHkzt6v1xkTsw)
  via `scripts/yt-upload.py`: video rkux49qUSzg, publishedAt 10:01:00 EEST
  (both attempts logged in `media/kapitza/upload.log`)
- QA gate (scratchpad yt-qa.py, videos.list): 10 of 15 at 10:01:16 EEST
  while YouTube was still processing (uploadStatus uploaded, sd, no
  source size, duration P0D); 15 of 15 at 10:03:03 EEST: Seed Zero
  channel, uploadStatus processed, processingStatus succeeded, no
  rejection, HD, embeddable, 1080x1920, title, description, tags,
  categoryId 27, madeForKids false, selfDeclaredMadeForKids false,
  duration PT39S (38.000 s rounds up), private
- published (videos.update privacyStatus public, containsSyntheticMedia
  true) at 10:03:05 EEST; re-read 15 s later: public, madeForKids false,
  selfDeclaredMadeForKids false, embeddable true (log in
  `media/kapitza/publish.log`)
- public URL: https://youtu.be/rkux49qUSzg

### Quota

- this short: 1,600 (insert) + 1 (channel check) + 2 (gate reads) + 52
  (publish and re-read) = 1,655 units, plus the rejected first insert
  (1,600 + 1 if YouTube charges a request that fails validation, which
  the quota page does not state); the day 12 slate together 4,967 units
  by the successful requests alone, at most 6,568 of 10,000 if the
  rejected insert counted, which still leaves room for analytics reads;
  four insert attempts today against the hard cap of five
