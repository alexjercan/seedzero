# Produce short: Swing pumping, higher with nobody pushing

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day16

## Goal

Backlog idea (trend research 2026-09-13, task 20260913-212839, ranked
fifth): "Swing pumping: a swing started at 5 degrees with no push; the
rider stands at the bottom and squats at the top, 10 percent length
change, versus the reversed rhythm; measure the angle after each swing;
expect the right rhythm to pass 60 degrees in about ten swings and the
reversed rhythm to shrink toward zero; a swing at rest never starts."
Day sixteen, second slot. Chosen because it is a two-panel same-start
comparison of continuous visible motion in the Kapitza family (827
views), with one setup number (5 degrees, nobody pushing) and one
payoff number (the angle after the counted swings). Question in the
first two seconds: "Nobody is pushing. How does a swing go higher?"

## Claim

Two identical swings start at five degrees with nobody pushing. On one
the rider stands up at the bottom and squats at the top; on the other
the rider does the opposite. The first climbs past sixty degrees; the
second dies away. Every number below is printed by the sim before the
script is written.

## Evidence

### Measurements

(recorded after the measure-only run, before scripting)

`sims/swing/swing.py` with `projects/swing/manifest.json` (a
variable-length pendulum, theta'' = -(g / L) sin theta - 2 (L' / L)
theta', with an event-driven rider whose centre of mass moves toward
its target length with a 40 ms time constant; RK4 at 2,000 steps per
second; deterministic, no seed; log in `media/swing/measure.log`):

- swing: rope 2.5 m, the rider's centre of mass 2.25 m from the pivot
  standing and 2.5 m squatting (10% length change), reaction lag 40 ms;
  both released from rest at 5 degrees with nobody pushing; small-swing
  period 3.17 s
- peak angle after each swing, stand at the bottom and squat at the
  top: 6.8, 9.3, 12.7, 17.3, 23.6, 32.3, 44.5, 62.2, 89.4 degrees
- peak angle after each swing, the other way round: 3.67, 2.70, 1.98,
  1.46, 1.07, 0.79, 0.58, 0.43, 0.31, 0.23 degrees
- the pumped swing first passes 60 degrees on swing 8 (62.15 degrees
  at 25.27 s); on that swing the other rhythm peaks at 0.43 degrees
  (at 24.48 s); the pumped swing passes 90 degrees on swing 9;
  halfway to the target (30 degrees) on swing 6
- growth per swing 1.36x at small angles; impulsive closed form
  (L / L')^3 = 1.372x in energy per half swing; the other rhythm
  shrinks by 0.736x per swing
- check, a swing at rest with the same rider: largest angle in 20 s
  0.000000 degrees (nothing to pump)
- check, half the step: swing 8 at 25.27 s, peaks 6.82, 9.29, 12.66
- check, half the reaction lag (20 ms): swing 8; peaks 6.84, 9.34,
  12.78 (a quicker rider pumps slightly harder)
- check, a 5% length change: passes 60 degrees on swing 17 at 54.3 s
- first model tried: a rider whose length followed the swing's phase
  smoothly (L = L_long - dL sin^2 phi); it pumped only 5% per swing
  (5.27, 5.55, 5.86 ... degrees), far below the stand-and-squat rhythm,
  so the rider was made event-driven; with a 50 ms lag swing 8 peaked
  at 60.03 degrees, too close to the target, so the lag was set to
  40 ms (62.15 degrees) before scripting

Narration numbers: five degrees (setup), sixty degrees after eight
swings (payoff); the other rhythm's half a degree is the comparison.

### Production

- `sims/swing/swing.py` renders two swings stacked (pivots at y 430
  and 1000, 150 px/m, rope 375 px): a beam, the rope to a seat drawn at
  the long length, the rider as a disc at the live length (it rises
  above the seat when standing), a faint arc of the current peak angle,
  per-panel labels ("stand at the bottom, squat at the top" in gold,
  "the other way round" in teal) and readouts "swing N" and "peak N.N
  deg" updated at each turning point on the start side; real time from
  the release at 1.6 s; the pumped swing freezes at its 60-degree peak
  (26.87 s of video) and the three-line payoff appears at 27.0 s; the
  last 0.6 s crossfade to frame one
- text widths measured before rendering: overlay 746 px (the first
  overlay measured 1,007 px and was shortened), title lines 606, 567
  and 335, labels 847 and 460, readout 620, payoff lines 654, 863 and
  798
- narration `projects/swing/narration.txt`, 109 words; round trip
  passed first time on both drafts (28.78 and 32.28 s; log
  `media/swing/voice.log`); the first draft put the payoff words
  before the swing reached 60 degrees, so "Nobody touches them again."
  and "Every pass adds a little more." were added; hooks considered:
  "Nobody is pushing. How does a swing go higher?" (kept), "How does a
  swing go higher with nobody pushing?" (question lands later), "Can a
  swing pump itself?" (jargon)
- spoken timing checked with `scripts/voice-timing.py`: the question
  0.6 to about 3.5; "both let go from five degrees" to 5.9 with the
  release at 1.6; the two rhythms named 5.9 to 13.4; the mechanism
  13.4 to 22.8; "Eight swings later, it passes sixty degrees" about
  28.2 to 31.0 with the peak reached at 26.87 and the payoff on screen
  from 27.0; "under half a degree" 31.6 to 32.8; voice ends at 32.88;
  music seed 49 at gain 0.18
- compose: `media/swing/final.mp4` 40.000 s, 1080x1920, 60 fps, h264
  with faststart, aac; audio mean -16.2 dB, peak 0.0 dB after the
  limiter (log `media/swing/compose.log`)
- inspection (contact sheet 8x5 at 1 fps plus full-resolution frames
  of the composed final at 0.02, 2.0, 5.0, 12.0, 20.0, 26.0, 27.0,
  29.0, 32.0 and 39.95 s): title on frame one under the overlay with
  both swings at 5 degrees; "swing 1 peak 6.8 deg" against "swing 1
  peak 3.7 deg" at 5.0 s; "swing 5 peak 23.6" against "swing 6 peak
  0.8" at 20.0; the frozen top swing at its 62.1-degree peak with the
  arc from 27.0 s; the payoff is on screen at 29.0 s under "Eight
  swings later," and at 32.0 under "under half a degree."; the loop
  crossfade closes on the title
- `projects/swing/metadata.json`: title 95 characters (a first
  draft was 109 and was cut to the payoff's own words), category 27,
  private, altered-content disclosure true, not made for kids

### Published

- quota check before the insert: clock 2026-09-14T10:40:30+03:00 EEST; one upload
  attempt recorded since the 10:00 EEST boundary (orbitlane at
  10:35:18, published 10:39:26); this is insert attempt 2 of the hard
  cap of 5
- attempt 2 recorded at 2026-09-14T10:40:30+03:00, video name swing, before running
  `scripts/yt-upload.py swing`
- upload: `scripts/yt-upload.py swing` ran 10:40:30 to 10:40:35 EEST,
  token verified to see only the Seed Zero channel, video id
  4MtpXdc6NkA, private (`media/swing/upload.log`)
- gate read at 2026-09-14T10:41:36+03:00: 15 of 15 pass (processed,
  succeeded, hd, embeddable, 1080x1920 source, title, description, tags
  as a set, category 27, not made for kids, PT41S, private);
  containsSyntheticMedia reads absent as usual (`media/swing/qa.log`)
- publish read at 2026-09-14T10:41:56+03:00: 15 of 15 pass again;
  privacy set to public at 10:41:59 EEST; re-read after 15 s:
  privacyStatus public, madeForKids false, embeddable true
  (`media/swing/publish.log`)
- public at https://youtu.be/4MtpXdc6NkA

### Quota

- upload attempt 2 of 5 for the quota day that began 2026-09-14
  10:00 EEST
- units: 1 channel check + 1,600 insert + 1 gate read + 1 publish
  read + 50 update + 1 re-read = 1,654 units; day total after this
  video 3,308 of 10,000

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
