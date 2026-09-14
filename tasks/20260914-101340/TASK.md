# Produce short: Orbit passing lane, fire forward and fall behind

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day16

## Goal

Backlog idea (trend research 2026-09-13, task 20260913-212839, ranked
first): "Orbit passing lane: two ships side by side in the same 400 km
circular orbit; one fires a 10 m/s burst forward; measure the gap after
one lap and the height difference at the far side; expect the burst
ship about 170 km behind after one 92-minute lap and 35 km higher at
the far side." Day sixteen, first slot. Chosen because the channel's
top shorts are continuous-motion physics with a plain question hook
(Fourier 1,044 views, brachistochrone 949, tautochrone 946, Dzhanibekov
941, gyroscope 924, elevator 920) and this is a two-ship same-orbit
comparison with one setup number (the 10 m/s burst) and one payoff
number (how far behind after one lap). Peg: JUICE Earth flyby
2026-09-30. Question in the first two seconds: "Fire your engine
forward. Do you pull ahead?"

## Claim

Two ships side by side in the same circular orbit. One fires a short
burst forward. It does not pull ahead: it climbs into a higher, slower
lap and ends the lap far behind the ship that did nothing. Every number
below is printed by the sim before the script is written.

## Evidence

### Measurements

(recorded after the measure-only run, before scripting)

`sims/orbitlane/orbitlane.py` with `projects/orbitlane/manifest.json`
(two ships integrated in the inertial plane around a point-mass Earth
with RK4 at 0.5 s steps; the gold ship's position measured in the
white ship's frame as arc distance along the track and difference in
distance from the centre; deterministic, no seed; log in
`media/orbitlane/measure.log`):

- orbit: circular, 400 km above an Earth of radius 6,371 km (mu
  3.986e14 m^3/s^2); speed 7,672.6 m/s; lap 2 pi sqrt(r^3 / mu) =
  5,544.9 s = 92:25; the gold ship gains 10 m/s along its motion at
  the burst (36 km/h, 0.130% of its speed)
- white ship: back at the burst point after 5,544.86 s = 92:25 (closed
  form 5,544.86 s)
- forward burst: the gold ship is ahead by at most 4.21 km at 638 s =
  10:38 after the burst, then falls back level at 1,126 s = 18:46; at
  the far side (2,772 s) it is +35.41 km in height and -82.74 km along
  the track; highest point +35.42 km at 2,784 s = 46:24; its own lap
  takes 5,566.6 s = 92:47 (+21.8 s against the white ship); after one
  white lap it is -167.22 km along the track, +0.01 km in height,
  167.21 km away in a straight line; orbit +0.00 to +35.42 km against
  the white ship's height; energy drift 1.1e-14
- check, backward burst: at most 4.22 km behind at 10:38, level at
  18:46, -35.18 km at the far side and +83.61 km along the track,
  lowest -35.18 km, own lap 5,523.3 s = 92:03 (-21.6 s); after one
  white lap +165.48 km along the track, -0.01 km in height
- check, half the step (0.25 s): white lap 5,544.86 s; after one white
  lap the gold ship is -167.216 km along the track and +0.005 km in
  height (unchanged)
- check, Clohessy-Wiltshire closed forms: -3 T dv = -166.35 km along
  the track after one lap; highest point 4 dv / n = 35.30 km; largest
  lead 4.21 km at 638 s; the new lap 3 T dv / v = +21.7 s longer
- on screen: the burst at 6.4 s of video, one white lap in 22 s (252x),
  far side at 17.4 s, level again at 10.9 s, lap complete at 28.4 s

Narration numbers: ten meters per second (setup), one hundred sixty
seven kilometers behind (payoff).

### Production

- `sims/orbitlane/orbitlane.py` renders a lap dial (Earth radius 112 px
  with the orbit ring at the true ratio, a marker at the burst point,
  a progress arc, white and gold dots) with a stopwatch under it
  reading the simulated time since the burst and the lap fraction, and
  a local view below with the white ship fixed at (930, 1230) as an
  outline rocket, the gold ship drawn at true scale (5.0 px/km, 100 km
  bar) in the white ship's frame with a trail, a "same height" dotted
  line, an exhaust flash for 0.5 s at the burst, and two readouts
  (along the track: ahead/behind; height: higher/lower/level); the
  two-line question for the first 2.4 s and the three-line payoff from
  28.6 s; the state freezes at the lap end; the last 0.6 s crossfade
  to frame one
- text widths measured before rendering: overlay 855 px, title lines
  567 and 603, labels 580 and 382, readouts 415 and 412, watch 204,
  watch label 440, scale 133, payoff lines 511, 597 and 696
- narration `projects/orbitlane/narration.txt`, 109 words; round trip
  passed first time on all three drafts (30.33, 33.67 and 34.25 s;
  log `media/orbitlane/voice.log`); the first draft was too short for
  the lap and the second put "halfway around" after the lap end, so
  the mechanism sentences were reordered; hooks considered: "Speed up
  in orbit. Do you pull ahead?" (kept), "Fire your engine forward. Do
  you pull ahead?" (ambiguous about the engine's direction), "Hit the
  gas in orbit." (no question)
- spoken timing checked with `scripts/voice-timing.py` (voice split at
  pauses, each piece transcribed, plus the 0.6 s offset): the question
  0.6 to 2.6; "fires its engine and gains ten meters per second" 5.0
  to 8.5 with the burst at 6.4; "At first it edges ahead" 8.5 to 10.1
  with the lead peaking at 8.9 and level at 10.9; "Halfway around, the
  gold ship is far above and already behind" 15.5 to 19.9 with the far
  side at 17.4; "One lap after speeding up" 27.4 to 29.0 with the lap
  complete at 28.4; "the gold ship is one hundred sixty seven
  kilometers behind" 29.0 to about 32 with the payoff on screen from
  28.6; voice ends at 34.85; music seed 48 at gain 0.18
- compose: `media/orbitlane/final.mp4` 40.000 s, 1080x1920, 60 fps,
  h264 with faststart, aac, 2.7 MB; audio mean -16.4 dB, peak 0.0 dB
  after the limiter (log `media/orbitlane/compose.log`)
- inspection (contact sheet 8x5 at 1 fps plus full-resolution frames
  of the composed final at 0.02, 2.0, 6.5, 9.0, 12.0, 17.4, 24.0,
  28.6, 30.5, 34.0 and 39.95 s): title on frame one under the overlay
  with the gold ship inside the white outline and the dial turning;
  exhaust flash at 6.5 s; "4.2 km ahead, 4.7 km higher" at 9.0 s under
  "ten meters per"; "82.7 km behind, 35.4 km higher" at 17.4 s under
  "gold ship is far"; "167.2 km behind, level" with lap 1.00 at 28.6;
  the payoff is on screen at 30.5 s while "one hundred sixty seven"
  is spoken; captions sit between the scale bar and the payoff; the
  loop crossfade closes on the title
- `projects/orbitlane/metadata.json`: title 89 characters, category
  27, private, altered-content disclosure true, not made for kids

### Published

- quota check before the insert: clock 2026-09-14T10:35:18+03:00 EEST; zero upload
  attempts recorded since the 10:00 EEST boundary (the previous
  three inserts were at 21:59 to 22:00 on 2026-09-13, the previous
  quota day); this is insert attempt 1 of the hard cap of 5
- attempt 1 recorded at 2026-09-14T10:35:18+03:00, video name orbitlane, before running
  `scripts/yt-upload.py orbitlane`
- upload: `scripts/yt-upload.py orbitlane` ran 10:35:18 to 10:35:24 EEST,
  token verified to see only the Seed Zero channel, video id
  Mx9chV20aDc, private (`media/orbitlane/upload.log`)
- gate read at 2026-09-14T10:36:39+03:00: 15 of 15 pass (processed,
  succeeded, hd, embeddable, 1080x1920 source, title, description, tags
  as a set, category 27, not made for kids, PT41S, private);
  containsSyntheticMedia reads absent as usual (`media/orbitlane/qa.log`)
- publish read at 2026-09-14T10:39:24+03:00: 15 of 15 pass again;
  privacy set to public at 10:39:26 EEST; re-read after 15 s:
  privacyStatus public, madeForKids false, embeddable true
  (`media/orbitlane/publish.log`)
- public at https://youtu.be/Mx9chV20aDc

### Quota

- upload attempt 1 of 5 for the quota day that began 2026-09-14
  10:00 EEST
- units: 1 channel check + 1,600 insert + 1 gate read + 1 publish
  read + 50 update + 1 re-read = 1,654 units; day total after this
  video 1,654 of 10,000

### Repository

- committed on master as 28c9eb1 "Publish the day sixteen slate"
  (sims, projects, tasks, docs/niche.md, web/data,
  scripts/voice-timing.py; media and secrets untracked) and pushed to
  origin git@github.com:alexjercan/seedzero.git at 10:44 EEST on
  2026-09-14; the push advanced origin/master from 7ca7339 to 28c9eb1;
  verified with `git rev-parse HEAD origin/master` (both
  28c9eb15aaf08bc3cad3efd4d63a1acdcc86f022) and `git status -sb`
  (master...origin/master, no divergence); this note is committed
  separately as "Record the day sixteen push"
