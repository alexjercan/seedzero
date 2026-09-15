# Produce short: Dropped versus fired bullet, which lands first

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day17

## Goal

Backlog idea (trend research 2026-09-13, task 20260913-212839): "Dropped
versus fired bullet: same 1.5 m height, one dropped and one fired level
at 360 m/s, in a vacuum and in air with quadratic drag; measure the
landing times; expect 0.553 s for both in a vacuum and the fired one a
few hundredths later in air because drag on the fast bullet also pushes
up; the vacuum tie is the headline, the air gap depends on the drag
choice." Day seventeen, first slot. Chosen because it is a viral debate
a simulation settles with one number (the research run found
"misconception then disproof" formats share most), a two-panel
same-input comparison of continuous motion, with one setup number (the
height) and one payoff number (the landing time). Question in the first
two seconds: "Drop one bullet, fire one level. Which lands first?"

## Claim

Two bullets start at the same height at the same moment. One is dropped,
one is fired level. With no air they hit the ground at the same instant.
Every number below is printed by the sim before the script is written.

## Evidence

### Measurements

(recorded after the measure-only run, before scripting)

`sims/bulletdrop/bulletdrop.py` with `projects/bulletdrop/manifest.json`
(two bullets integrated with RK4 at 1e-5 s steps in two dimensions,
gravity 9.80665 m/s^2, no air, flat ground; landing time interpolated
inside the last step; deterministic, no seed; log in
`media/bulletdrop/measure.log`):

- setup: both bullets start 1.5 m up at the same instant; one dropped
  from rest, one fired level at 360 m/s (1,296 km/h, 1.05 times the
  speed of sound)
- dropped: hits the ground at 0.55310 s at 5.424 m/s (closed form
  sqrt(2h/g) = 0.55310 s)
- fired: hits the ground at 0.55310 s, 199.11 m from the start, at
  360.04 m/s; lands +0.000 ms after the dropped one (0.0 microseconds
  apart)
- heights: over the whole fall the two heights differ by at most 0.000
  micrometres
- check, half the step (5e-6 s): 0.55310 s for both, gap +0.000 ms
- check, in air (1.225 kg/m^3, drag coefficient 0.3, 9 mm bullet of 8
  g, quadratic drag along the velocity, k 1.461e-3 per metre): dropped
  0.5533 s, fired 0.5775 s (+24.2 ms later, 181.5 m from the start,
  arriving at 276 m/s); the drag on the fast bullet has an upward part
  because the drag force points against the velocity, which tilts down
- check, ground curving away like the Earth (radius 6,371 km): the
  fired bullet lands at 0.55367 s, +0.57 ms later, the ground having
  dropped 3.1 mm under it

Narration numbers: one and a half meters (setup), zero point five five
three seconds (payoff). The 199 m and the air gap go to the card and
the description.

### Production

- `projects/bulletdrop/narration.txt`: 107 words;
  `scripts/voiceover.sh` round trip passed on the first wording ("ok:
  transcript matches narration (33.390295s)",
  `media/bulletdrop/voice.log`); voice ends at 33.99 s of video
- timing (`scripts/voice-timing.py`, +0.6 s offset): "Which lands
  first? Neither." spoken about 27.1 to 28.8 s, "Both hit at 0.553
  seconds" from 28.8 s; the slow-motion factor was set to 1/49 so both
  bullets land at 27.10 s of video and the payoff card comes at 28.6 s
- text widths measured with PIL before rendering: overlay 856 px, title
  lines 512, 451 and 565 px, panel labels 189 and 478 px, readout 200
  px, clock 263 px, payoff lines 584, 542 and 756 px; all under 950 px
- layout fixes before the final render: the ruler labels clipped at
  the left frame edge and crossed the panel divider (rulers moved to
  150 px inside each panel centre), the ground stripes were too dark to
  read as motion (brightened), and the clock's speed label sat in the
  caption band at y 1442 (floor moved to y 1300, clock to 1352)
- footage: `sims/bulletdrop/bulletdrop.py` rendered 40.00 s at 60 fps,
  1080x1920 (`media/bulletdrop/render.log`); the fired panel's camera
  follows the bullet with metre stripes and 10 m posts streaming past;
  the bullets are drawn about 4x life size (stated in the description)
- compose: `scripts/compose.sh bulletdrop` (music seed 51, gain 0.18,
  captions at 0.75); final.mp4 40.000 s, h264 1080x1920 + aac; mean
  volume -17.0 dB, peak -0.0 dB (`media/bulletdrop/compose.log`)
- inspected full-resolution frames at 0.02, 1.5, 4.0, 12.0, 20.0, 27.0,
  27.3, 29.0, 33.0 and 39.95 s (`media/bulletdrop/frame-*.png`, rows in
  `row-a.png` and `row-b.png`) and the contact sheet `sheet.png`:
  question on screen for the first 2.4 s with motion already under
  way, the two height readouts identical on every frame, both bullets
  on the floor with the clock at 0.553 s from 27.1 s, caption "Which
  lands first?" over the landed frame, payoff card from 28.6 s, clock
  clear of the caption band, crossfade back to frame 0 at the end;
  approved
- `projects/bulletdrop/metadata.json`: title 94 characters, category
  27, private, altered-content disclosure true, not made for kids;
  description carries the air and curvature checks


### Published

- quota check before the insert: clock 2026-09-15T10:34:02+03:00 EEST; zero upload
  attempts recorded since the 10:00 EEST boundary; this is insert
  attempt 1 of the hard cap of 5
- attempt 1 recorded at 2026-09-15T10:34:02+03:00, video name bulletdrop, before running
  `scripts/yt-upload.py bulletdrop`
- upload: `scripts/yt-upload.py bulletdrop` ran 10:34:02 to about 10:34:10
  EEST, token verified to see only the Seed Zero channel, video id
  lEWXfXBpJVc, private (`media/bulletdrop/upload.log`)
- gate: `scripts/yt-qa.py bulletdrop lEWXfXBpJVc` at 2026-09-15T10:36:53+03:00,
  15 of 15 pass (processed, succeeded, hd, 1080x1920, title, description,
  tags, category 27, not for kids, PT41S for the 40.000 s file, private);
  containsSyntheticMedia reads absent as on every earlier upload
  (`media/bulletdrop/qa.log`)
- publish: `scripts/yt-qa.py bulletdrop lEWXfXBpJVc --publish` re-ran the gate
  (15 of 15) and set the video public at 2026-09-15T10:38:34+03:00; the
  re-read after 15 s shows privacyStatus public, madeForKids false,
  embeddable true; public at https://youtu.be/lEWXfXBpJVc

### Quota

- attempt 1 of the hard cap of 5 for the quota day that began
  2026-09-15T10:00 EEST; cost 1 (channel check) + 1,600 (insert) + 1 (gate)
  + 1 (gate re-read) + 50 (publish update) + 1 (re-read) = 1,654 units

### Repository

- committed as 086ecfe "Publish the day seventeen slate" (sims, projects,
  tasks, docs/niche.md, web/data; no media, previews or secrets) and pushed
  to origin/master at 2026-09-15 10:55 EEST
