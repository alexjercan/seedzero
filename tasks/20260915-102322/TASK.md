# Produce short: Gravity assist, pass behind or in front of the planet

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day17

## Goal

Backlog idea (trend research 2026-09-13, task 20260913-212839): "Gravity
assist: the same probe at 5 km/s relative to an Earth-mass planet on a
30 km/s orbit, passing behind the planet versus in front of it at the
same distance; measure the speed relative to the Sun before and after;
expect about plus 5 km/s behind and minus 5 in front, mirror images,
with the planet's own speed unchanged to nine digits (peg: JUICE Earth
flyby 2026-09-30; its 2024 flyby gave minus 4.8 km/s)." Day seventeen,
third slot. Chosen for the live peg (JUICE flies past Earth on
2026-09-30), the two-ship same-input comparison of continuous motion,
and one plain question with one setup number (the planet's 30 km/s)
and one payoff number (the speed gained). Question in the first two
seconds: "Can a planet throw a ship faster, for free?"

## Claim

Two identical ships coast toward the same moving planet with the same
speed and the same closest approach. The one that passes behind the
planet leaves faster relative to the Sun; the one that passes in front
leaves slower. Every number below is printed by the sim before the
script is written.

## Evidence

(measurements, production, publication: recorded below as they happen)

### Measurements

`nix develop -c python3 sims/gravityassist/gravityassist.py --measure-only`
at 2026-09-15 10:46 EEST, 16.9 s, output in `media/gravityassist/measure.log`.

- setup: an Earth-mass planet (mu 3.986e14 m^3/s^2, radius 6,371 km) on a
  circular orbit of radius 149,597,871 km around the Sun (mu 1.32712e20),
  moving at 29,784.7 m/s; two ships start 1,000,000 km from the planet on
  its sunward side, moving straight away from the Sun at 5,000 m/s relative
  to the planet, aimed to pass 12,742 km from the planet's centre (6,371 km
  above the surface), one behind it and one in front; Sun-frame RK4 with
  steps of 0.5 to 20 s scaled to the distance from the planet; each ship's
  starting offset is found by shooting (secant) until its closest approach
  matches; deterministic, no seed
- behind (gold): starting offset -23,767.6 km along the planet's motion;
  closest approach 12,742.0 km at -2.080 h (before the run's nominal zero,
  because the pull speeds the ships up on the way in), 9,311 m/s relative
  to the planet there; relative to the planet 5,000.0 m/s in, 4,990.4 out,
  path turned by 68.67 degrees; relative to the Sun 30,201.5 m/s in,
  34,349.0 m/s out, +4,147.6 m/s (+4.15 km/s); reduced to the planet's
  distance from the Sun 30,003.2 in, 34,427.7 out, +4,424.5 m/s; 107.0 h in
  23,819 steps; the planet's own speed 29,784.6918 m/s at both ends
- front (white): starting offset +23,798.8 km; closest approach 12,742.0 km
  at -2.080 h, 9,311 m/s relative there; relative to the planet 5,000.0 in,
  4,989.3 out, turned 68.69 degrees; relative to the Sun 30,201.5 m/s in,
  25,053.3 m/s out, -5,148.1 m/s (-5.15 km/s); reduced 30,003.2 in,
  25,127.9 out, -4,875.3 m/s
- check, closed form with the planet's velocity fixed and no Sun:
  eccentricity 1.7992, turn 2 asin(1/e) = 67.53 degrees, +4,256.8 m/s
  behind and -4,964.8 m/s in front (the full run differs by 0.1 to 0.2
  km/s because the planet's velocity turns 4.4 degrees along its orbit
  over the 107 h and the ships move through the Sun's field)
- check, half the step (behind): closest approach 12,742.0 km, +4,147.6
  m/s (full step +4,147.6)
- check, recoil: the gold ship's velocity changes by 5,635.2 m/s in the
  planet's frame; momentum conservation gives the planet (5.972e24 kg) a
  recoil of 1,000 kg x 5,635.2 m/s / 5.972e24 kg = 9.4e-19 m/s, about a
  billionth of a billionth of a metre per second; the integration treats
  the ship as massless
- narration numbers: the planet's 30 km/s (29,784.7 m/s), gold +4.1 km/s
  (+4,147.6 m/s), white -5.1 km/s (-5,148.1 m/s), the planet pays about
  a billionth of a billionth of a metre per second (9.4e-19 m/s)

### Production

- sim `sims/gravityassist/gravityassist.py`, manifest
  `projects/gravityassist/manifest.json`: 1080x1920, 60 fps, 40.000 s,
  planet-centred view (positions relative to the planet, speeds relative
  to the Sun), time lapse through monotone cubic knots (video s -> hours
  from the closest pass): 0 -> -53.6, 9 -> -1.4, 13 -> 0, 17 -> +1.4,
  22 -> +16.7, 26 -> +53.6, then held at the 1,000,000 km exit; zoom
  min(12 px per 1,000 km, 0.85 x view / farthest ship); title 0 to 2.4 s;
  payoff card at 26.4 s; loop fade 0.6 s
- text widths measured with PIL before rendering, all under 950 px:
  overlay 785, title lines 601 and 700, panel labels 383 and 417, clock
  595, payoff lines 938, 680, 406, 702
- smoke frames at 0.02, 1.5, 4, 9, 11.5, 13, 14.5, 17, 22, 27, 39.95 s
  inspected at full resolution (`media/gravityassist/row-a.png`, `row-b.png`,
  `row-c.png`): ships enter from the left at 1,000,000 km, the view zooms
  in to the flyby, the two paths bend around the planet and cross just
  after the closest pass (the runs are independent; noted in the
  description), gold leaves up along the planet's motion and white down
  against it, readouts 30.2 -> 34.3 km/s and 30.2 -> 25.1 km/s, payoff
  card matches (+4.1, -5.1, 9 x 10^-19 m/s), the last frame fades to the
  first
- narration `projects/gravityassist/narration.txt`, 112 words; first
  round trip failed on "pull" (heard "pole") and "came" (heard "can"),
  reworded to "gravity" and "arrived"; then trimmed by three words; the
  final round trip passed: `ok: transcript matches narration (37.395737s)`
  (`media/gravityassist/voice.log`)
- phrase timing (`scripts/voice-timing.py`, offset 0.6 s): the question
  0.60 to 2.41 s; setup to 11.24 s; "the planet's gravity bends both
  paths" inside 11.24 to 15.63 s, around the closest pass at 13.00 s;
  gold's exit 15.63 to 20.06 s; white's exit 20.06 to about 24 s; the
  question again to 26.30 s; "Yes." 26.30 to 27.01 s under the payoff card
  at 26.4 s; "4.1 ... faster than it arrived" to 32.63 s; "5.1 slower" to
  34.27 s; the recoil line to 38.00 s; loop fade from 39.4 s
- render: `sims/gravityassist/gravityassist.py` wrote
  `media/gravityassist/footage.mp4` (2,400 frames, `render.log`); compose:
  `scripts/compose.sh gravityassist` wrote `final.mp4` (40.000 s, h264
  1080x1920 at 60 fps plus aac; mean -16.6 dB, peak -0.0 dB), `preview.mp4`
  and `sheet.png` (`compose.log`)
- local QA: full-resolution frames of `final.mp4` at 0.02, 1.5, 4, 9, 13,
  14.5, 17, 22, 27, 33, 36, 39.95 s inspected (`media/gravityassist/row-a.png`,
  `row-b.png`, `row-c.png`): overlay at the top, title for 2.4 s, panel
  labels and live readouts, the flyby with the zoom in and out, the clock
  above the caption band and the captions inside it, the payoff card under
  the captions from 26.4 s with the measured numbers, the last frame fading
  to the first; pass
- metadata `projects/gravityassist/metadata.json`: title 91 characters,
  description with the measured list, the checks and the note about the
  superimposed runs, 10 tags, category 27, private, containsSyntheticMedia
  true, not made for kids

### Published

- quota check before the insert: clock 2026-09-15T10:51:34+03:00 EEST; two
  upload attempts recorded since the 10:00 EEST boundary (bulletdrop at
  10:34:02 and machcone at 10:38:12, both published); this is insert
  attempt 3 of the hard cap of 5
- attempt 3 recorded at 2026-09-15T10:51:50+03:00, video name gravityassist,
  before running `scripts/yt-upload.py gravityassist`
- upload: `scripts/yt-upload.py gravityassist` ran 10:51:50 to about 10:52:00
  EEST, token verified to see only the Seed Zero channel, video id
  UzQ_3x5POKo, private (`media/gravityassist/upload.log`)
- gate: `scripts/yt-qa.py gravityassist UzQ_3x5POKo` at 2026-09-15T10:53:52+03:00,
  15 of 15 pass (processed, succeeded, hd, 1080x1920, title, description,
  tags, category 27, not for kids, PT41S for the 40.000 s file, private);
  containsSyntheticMedia reads absent as on every earlier upload
  (`media/gravityassist/qa.log`)
- publish: `scripts/yt-qa.py gravityassist UzQ_3x5POKo --publish` re-ran the
  gate (15 of 15) and set the video public at 2026-09-15T10:54:04+03:00;
  the re-read after 15 s shows privacyStatus public, madeForKids false,
  embeddable true; public at https://youtu.be/UzQ_3x5POKo

### Quota

- attempt 3 of the hard cap of 5 for the quota day that began
  2026-09-15T10:00 EEST; cost 1 + 1,600 + 1 + 1 + 50 + 1 = 1,654 units;
  day total after three attempts 4,962 units

### Repository

- committed as 086ecfe "Publish the day seventeen slate" (sims, projects,
  tasks, docs/niche.md, web/data; no media, previews or secrets) and pushed
  to origin/master at 2026-09-15 10:55 EEST
