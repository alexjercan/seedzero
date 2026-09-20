# Produce short: Pi collisions, 100 to 1 beside 10,000 to 1

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day22

## Goal

Backlog idea (trend research 2026-09-20, task 20260920-100347, pillar 2
chaos and physics / pillar 4 algorithms in motion):
"Pi collisions: a small block at rest between a wall and a big block
pushed at 1 m/s, mass ratio 100 beside 10,000; count every click of
block on block and block on wall until they part for good; expect
exactly 31 and 314 (3 at equal mass, 3,141 at a million; the count is
the largest N with N atan(sqrt(m/M)) below pi), the small block peaking
at 10 and 100 m/s; event-driven, no time step; the run repeats so the
short loops; deterministic, no seed."
Day twenty-two, first slot. Chosen because the channel's best shorts are
continuous tabletop motion in two panels on the same input with a
closed-form check (rolling race 1,010 views, coupled pendulums 1,078,
hoop bead 982, cradle 956, water wheel 934, monkey and hunter 962), and
the click count is the most famous counterintuitive integer in the
niche. Question in the first two seconds: "Push a heavy block into a
light one. How many clicks before they part?"

## Claim

With the big block one hundred times heavier the blocks and the wall
click exactly thirty one times before the pair drift apart for good;
at ten thousand times heavier, three hundred fourteen: the digits of pi
appear in a count of collisions. Every number in the narration is
printed by the sim before the script is written.

## Evidence

### Measurements

(recorded after the measure-only run, before scripting; the wall gap and
block gap were then retuned twice from the voice timing, and the final
numbers below are from the last run; the counts, peak speeds, final
speeds, energy and momentum checks were identical in all three runs,
since the geometry only scales the times)

`sims/piblocks/piblocks.py --measure-only` with
`projects/piblocks/manifest.json` (a 1 kg block at rest 0.28 m from a wall
on a frictionless floor; a heavy block 0.55 m to its right pushed toward
it at 1 m/s; every collision elastic; two panels on the same push and the
same start, the heavy block 100 kg on top and 10,000 kg below; the light
block is 0.25 m wide, which only shifts the contact point: the motion
depends on the wall gap and the block gap alone; event driven: there is
no time step, the sim solves each next contact time exactly and the
motion between clicks is uniform, so the click count is exact and every
click is counted even where dozens fall inside one frame; deterministic,
no seed; first run 10:30 EEST at wall gap 0.3 m and block gap 0.4 m,
rerun 10:35 at 0.31 and 0.4, final run 10:38 at 0.28 and 0.55; log in
`media/piblocks/measure.log`, under 1 s):

- closed form, the largest N with N atan(sqrt(m / M)) strictly below pi,
  against the sim's count: mass ratio 1 to 1: 3 (4 atan(1) = pi exactly,
  not below it), sim 3; 100 to 1: 31 (31 atan = 3.089728, 32 atan =
  3.189397), sim 31; 10,000 to 1: 314 (314 atan = 3.139895, 315 atan =
  3.149895), sim 314; 1,000,000 to 1: 3,141 (3,141 atan = 3.140999,
  3,142 atan = 3.141999), sim 3,141; pi = 3.141593
- top panel, 100 kg into 1 kg: 31 clicks in all, 16 block on block and
  15 on the wall; first click at 0.5500 s; the heavy block stops (its
  speed passes zero) at click 15 at 0.8279 s with its face 27.79 cm from
  the wall at the closest (the light block has 2.8 cm of room); the
  light block peaks at 9.997 m/s after click 15; fastest click interval
  2.7949 ms between clicks 15 and 16; click 30 (wall) at 1.0134 s, then
  the light block's lone last trip at 1.510 m/s takes 0.3560 s to click
  31 (block on block) at 1.3694 s with the heavy block's face 0.787 m
  from the wall; after it the light block moves right at 0.4779 m/s and
  the heavy block at 0.9989 m/s, so they never meet again; energy
  50.000000 J at the end against 50.000000 J at the start (largest
  relative drift 8.53e-16); momentum given to the wall 200.3636 kg m/s
  (start -100.0, end +100.3636); largest relative momentum drift across
  a block-on-block click 3.34e-16
- bottom panel, 10,000 kg into 1 kg: 314 clicks in all, 157 block on
  block and 157 on the wall; first click at 0.5500 s; the heavy block
  stops at click 157 at 0.8300 s with its face 25.28 cm from the wall at
  the closest (0.3 cm of room); the light block peaks at 99.996 m/s
  after click 157; fastest click interval 0.0280 ms between clicks 157
  and 158; click 313 (block on block) at 1.0694 s, then the light block's
  lone last trip at 0.170 m/s takes 1.4103 s to click 314 (wall) at
  2.4797 s with the heavy block's face 1.900 m from the wall; after it
  the light block moves right at 0.1697 m/s and the heavy block at 1.0000
  m/s; energy 5000.000000 J against 5000.000000 J (largest relative drift
  1.27e-15); momentum given to the wall 20000.1553 kg m/s (start
  -10000.0, end +10000.1553); largest relative momentum drift across a
  block-on-block click 3.85e-16
- shape of the event (why the schedule is what it is): almost every click
  falls in one burst around the moment the heavy block stops (top: clicks
  2 to 30 between 0.69 and 1.01 s; bottom: clicks 2 to 313 between 0.69
  and 1.07 s), and the last click is a lone straggler: the light block
  leaves the second-to-last click with a small speed and makes one slow
  trip (0.36 s on top, 1.41 s below) before the final tap; the ratio of
  that trip to the burst is fixed by the mass ratio, not by the geometry
  (every time after the first click scales with the wall gap)
- video schedule at 1/10 speed (playback 0.1; a frame is 1.667 ms of real
  time): first click at 5.50 s in both panels; the heavy block stops at
  8.28 s (top, click 15) and 8.30 s (bottom, click 157); top: click 30 at
  10.13 s and the last click 31 at 13.69 s, the heavy block's right face
  leaves the frame (x 1080) at 22.08 s, at most 1 click per frame;
  bottom: click 313 at 10.69 s and the last click 314 at 24.80 s, the
  heavy block leaves the frame at 22.05 s, at most 54 clicks in one frame
  at the turnaround (the counter counts them all; the frame cannot show
  each one); top click times in video s: 5.50b 6.91w 7.39b 7.64w 7.79b
  7.89w 7.97b 8.03w 8.08b 8.12w 8.16b 8.19w 8.22b 8.25w 8.28b 8.31w 8.33b
  8.36w 8.39b 8.43w 8.46b 8.50w 8.55b 8.60w 8.67b 8.76w 8.88b 9.06w 9.39b
  10.13w 13.69b; bottom every 25th and the last five: #1 5.50b #26 8.19w
  #51 8.25b #76 8.27w #101 8.28b #126 8.29w #151 8.30b #176 8.31w #201
  8.31b #226 8.32w #251 8.34b #276 8.37w #301 8.51b #310 8.97w #311 9.18b
  #312 9.59w #313 10.69b #314 24.80w
- earlier geometries (same counts and speeds, other times): wall gap 0.3
  m and block gap 0.4 m put the first click at 4.00 s, the stop at 7.0 s,
  the top's last tap at 12.78 s and the bottom's at 24.67 s; 0.31 and 0.4
  gave 4.00, 7.1, 13.07 and 25.36 s
- track 2.042 m across 980 px at 480 px/m; the start needs 1.58 m; the
  heavy block is drawn 240 x 200 px in both panels (a fixed size with a
  mass label, not the cube-root size ratio, which would not fit)

Decisions: the brief's 1 m block gap and larger wall gap (about 3.6 s
and 7.4 s real) were cut so that at one fixed slow motion factor the
burst is watchable, the top's last tap lands in frame, and the bottom's
lone last wall tap lands before the payoff sentence; the geometry does
not change the counts, the peak speeds or the final speeds, only the
times. Both panels run at the same 1/10 speed so the comparison stays
fair on screen. The brief expected the top to finish at 12 to 15 s and
the bottom at 28 to 30 s; the measured shape of the event (one burst,
then a lone straggler) made 13.7 s and 24.8 s the honest fit for a
narration that ends at 34.5 s.

Narration numbers: one hundred times heavier and ten thousand (setup, one
per panel), thirty one and three hundred fourteen (payoff, the exact
counts on the card and the counters), the digits of pi (the reveal). The
equal-mass 3, the million 3,141, the closed form, the peak speeds, the
fastest intervals, the energy and momentum checks, the lone last trips
and the room at the turnaround go to the description.

### Production

- narration (written after the 10:30 measure-only run): three hooks
  tried, "Push a heavy block into a light one. How many clicks before
  they part?" (kept: it is the title question and the payoff answers it
  in the same words; the sentence-initial "Push" was a known onset risk
  and passed on every run), "Two blocks and a wall. How many clicks
  before they part?" (dropped: it does not say which block moves, so the
  setup line would have to) and "Why does this block click three hundred
  fourteen times?" (dropped: it gives the payoff away and asks for a
  mechanism the frame cannot show); `projects/piblocks/narration.txt`,
  111 words; the setup numbers are one hundred times heavier and ten
  thousand, the payoff thirty one and three hundred fourteen, then the
  digits of pi; `captions.py` chunks (20 characters) keep "On top, one
  hundred" / "times heavier.", "Below, ten thousand.", "at thirty one.",
  "One hundred to one:" / "thirty one." and "Ten thousand to one:"
  intact; "three hundred fourteen." is 23 characters and cannot fit one
  chunk, so it splits as "three hundred" / "fourteen." (the cleanest
  split available; see the note for the orchestrator)
- voice: run 1 at 10:32:18 EEST, a 101-word draft, passed the round trip
  at 29.14 s (3.47 words/s, ending at 29.74 s of video), but
  `voice-timing.py` put the payoff sentence at 19.0 to 25.0 s, before the
  bottom's last tap, and "long gone" at 17.4 to 19.0 s while the heavy
  block was still in frame; reworded to 111 words (a burst line "The
  clicks come faster and faster, then slower", "long gone" to "drives
  away", "all alone" added); run 2 at 10:34:03 failed on one word,
  "Below, the heavy block" heard as "A heavy block" (the lost "the"
  after a pause, as the memory note warns), so the sentence became "The
  heavy block below drives away"; run 3 at 10:34:45 passed, 111 words,
  33.92 s, ends at 34.52 s of the 40 s video (3.27 words/s); log in
  `media/piblocks/voice.log`
- timing (`scripts/voice-timing.py`, +0.6 s offset, run 3): "Push a
  heavy block into a light one" 0.60 to 2.66 s and "How many clicks
  before they part? On top," to 5.05 s over the title (to 2.4 s) with the
  first click at 5.50 s; "one hundred times heavier, below ten thousand.
  The clicks come faster and faster" 5.05 to 9.81 s over the burst (the
  stop at 8.28 and 8.30 s); "then slower, and every click counts, on the
  block and on the wall" 9.81 to 13.39 s over the sparse clicks (top
  click 30 at 10.13 s, bottom 313 at 10.69 s); "On top. One last tap, and
  they part at thirty one" 13.39 to about 16.5 s with the top's tap at
  13.69 s; "The light block slowed the heavy one, stopped it, and sent it
  back" to 19.94 s while the heavy blocks move right; "The heavy block
  below drives away" 19.94 to 22.01 s as both heavy blocks leave the
  frame (22.05 and 22.08 s); "and the light block, all alone, crawls
  back to the wall for one last tap" 22.01 to about 26.6 s with the
  bottom's wall tap at 24.80 s and the card from 25.2 s; "So how many
  clicks before they part?" about 26.6 to 28.71 s over the lit card;
  "One hundred to one, thirty one, ten thousand to one" 28.71 to 31.91
  s; "three hundred fourteen. The digits of pi" 31.91 to 34.52 s; the
  wall gap and block gap (0.28 and 0.55 m) and payoff_t (25.2 s) were
  set from this timing
- footage: `sims/piblocks/piblocks.py` (no arguments) wrote
  `media/piblocks/footage.mp4`, 40.00 s at 60 fps, 2,400 frames, h264
  crf 16 yuv420p, in 27 s with eight forked workers; first at 10:35 EEST
  (wall gap 0.31 m, block gap 0.4 m), then at 10:38 with the final
  geometry after the first QA pass; the same run re-printed every
  measurement above (`media/piblocks/render.log`); text widths at most
  896 px (the overlay; title lines 607, 503, 524 and 551 px, panel
  labels 406 and 477, sublabels 634 and 683, mass labels 137 and 201 at
  36 px and 63 at 26 px, the speed tag 173, the counter 184 at 88 px,
  "clicks" 113, the status 284, payoff lines 777, 686 and 331 px), so
  nothing clips at 1080 px; smoke frames at 0, 1.5, 4.5, 6.5, 7, 7.5, 9,
  12.8, 15, 24.7, 26 and 39.8 s (`--frames`, 10:31 EEST, first geometry)
  inspected for the layout: the four-line title at y 190 to 376 clear of
  the overlay band and of the top panel's header at y 454, the two
  panels with the wall at x 40 to 60, the floors at y 880 and 1390, the
  88 px counters, the click flashes on the wall face and the heavy
  block's face, the light block's ghost trail at the turnaround, the
  card below the caption band
- layout: panels at y 430 and 940, each 470 px (header 40 px label and
  28 px "1/10 speed" tag, 28 px sublabel, 88 px counter with a 36 px
  "clicks" unit, 32 px status word "pushing" / "parted for good", the
  wall from panel top + 240 to the floor at + 450, the light block 120 x
  120 px in gold with a "1 kg" label, the heavy block 240 x 200 px in
  the panel colour with its mass label); captions at caption_y 0.75 (y
  1440 to about 1520); payoff card at y 1592, 1648 and 1704
- compose: `scripts/compose.sh piblocks` wrote `media/piblocks/final.mp4`
  first at 10:36 EEST and again at 10:38:59 EEST with the final footage
  (h264 1080x1920 60 fps, aac 22050 Hz mono, 40.000 s; music seed 62 at
  gain 0.18; captions at caption_y 0.75, 35 drawtext filters); loudness
  mean -17.6 dB, peak -0.0 dB; preview and 8x5 contact sheet written
  (`media/piblocks/compose.log`)

### Local QA

- first pass (10:37 EEST, the 10:36 render at wall gap 0.31 m and block
  gap 0.4 m): frames at 0.02, 1.5, 4.5, 7.1, 9, 13.2, 15.8, 20.5, 25.4,
  26.5, 30.2, 32.5 and 39.95 s and the contact sheet inspected; layout,
  captions, card, counters and loop all clean; one sync defect: the
  burst peaked at 7.1 s while "The clicks come faster and faster" was
  spoken at 7.9 to 9.8 s, and the top's last tap (13.07 s) came before
  "One last tap" (14.1 to 15.0 s); the block gap was raised from 0.4 to
  0.55 m (first click 1.5 s later) and the wall gap trimmed from 0.31 to
  0.28 m so the bottom's tap stays ahead of the card and the payoff
  sentence; measured again, re-rendered and re-composed
- second pass (10:39 EEST): frames at 0.02, 1.5, 5.6, 8.3, 10.1, 13.7,
  14.6, 20.5, 24.8, 26.5, 30.2, 32.5 and 39.95 s extracted from
  final.mp4 (`media/piblocks/frame-*.png`) and inspected with the
  contact sheet (`media/piblocks/sheet.png`): 0.02 s shows the overlay
  at y 96, the title "Push a heavy block / into a light one. / How many
  clicks / before they part?" at y 190 to 376 clear of it, both panels
  at the start with the counters at 0 and "pushing" (the thumbnail); 1.5
  s shows "Push a heavy block" in the band with the title still up and
  both heavy blocks sliding left; 5.6 s shows "On top, one hundred" with
  the first flash on both heavy faces and both counters at 1; 8.3 s
  shows "The clicks come" with the light blocks pinned against the wall,
  both flashes lit and the counters at 15 and 157 (the stop); 10.1 s
  shows "then slower, and" with 29 and 312; 13.7 s shows "On top, one
  last" with the top counter at 31 in teal, "parted for good" and the
  flash on the heavy block's face as the light block taps it, the
  bottom at 313; 14.6 s the same words with the blocks moving apart;
  20.5 s shows "sent it back." with both heavy blocks near the right
  edge; 24.8 s shows "back to the wall for" with the bottom counter at
  314 in coral, "parted for good" and the wall flash, the heavy blocks
  as slivers at the frame edge; 26.5 s shows "one last tap." over the
  fully lit card "how many clicks before they part? / 100 to 1: 31.
  10,000 to 1: 314. / the digits of pi"; 30.2 s "One hundred to one:"
  and 32.5 s "three hundred" over the card; 39.95 s the crossfade to the
  title frame; captions match the narration word for word and sit in
  the y 1440 to 1520 band with the floors at 880 and 1390 and the card
  from 1592; no text clips at the frame edges; the payoff numbers are on
  screen when spoken (the counters from 13.69 and 24.80 s, the card from
  25.2 s, "thirty one" at about 30 s and "three hundred fourteen" at
  about 32 s); the counters end at exactly 31 and 314; approved

### Metadata

- `projects/piblocks/metadata.json`: title "Push a heavy block into a
  light one. How many clicks? 100 to 1: 31. 10,000 to 1: 314. Digits of
  pi." (99 characters; "The digits of pi." made it 103); description
  with the setup (0.28 m wall gap, 0.55 m block gap, 1 m/s, elastic, two
  panels, 1/10 speed, event driven, no seed), a Measured list (the exact
  counts and their split, the closed form with the equal-mass 3 and the
  million 3,141, the peak speeds, the room at the turnaround, the
  fastest intervals and the 54 clicks in one frame, the lone last trips,
  the final speeds, the energy and momentum checks), a Why paragraph
  (each click takes a slice of the heavy block's momentum, the wall tap
  turns the light block around, equal steps of atan(sqrt(m / M)) around
  a circle of fixed energy until a half turn is used up, so the count is
  pi over that angle rounded down and spells the digits of pi at ratios
  of 100 to the n), the rerun line and the AI-made line; 10 tags (pi,
  colliding blocks, elastic collision, digits of pi, momentum, physics,
  physics visualization, simulation, math visualization, shorts);
  category 27; private; containsSyntheticMedia true;
  selfDeclaredMadeForKids false
- not uploaded; task left open for the orchestrator's review and upload

### Release

- orchestrator review (10:46 EEST): the task evidence, the 8x5
  contact sheet and the full-resolution frames at 0.02, 14.6, 30.2, 32.5
  and 39.95 s inspected: the question over the two starting panels on the
  first frame; the top counter at 31 in teal with "parted for good" and
  the bottom at 313 at 14.6 s; the card "how many clicks before they
  part? / 100 to 1: 31. 10,000 to 1: 314. / the digits of pi" under
  "One hundred to one:" at 30.2 s and "three hundred" at 32.5 s (the
  23-character number cannot fit one 20-character chunk; the card
  carries 314); the crossfade at 39.95 s; every caption in the clear
  band, no clipping; final.mp4 h264 1080x1920 60 fps, 2,400 frames,
  aac 22050 Hz mono, 40.000 s, moov before mdat, md5
  7eb224caec70502c53c17a133b462a1c; title 99 characters; approved for
  release
- quota check: clock 2026-09-20T10:46:28+03:00; zero upload attempts recorded since the
  2026-09-20 10:00 EEST boundary (no 2026-09-20 upload entries in
  web/data/log.jsonl; the newest media/*/upload.log is parking at
  2026-09-19 11:04); this is insert attempt 1 of the hard cap of 5
- attempt 1 recorded at 2026-09-20T10:46:28+03:00, video name piblocks, before running
  `scripts/yt-upload.py piblocks`

### Published

- upload: `scripts/yt-upload.py piblocks` ran 10:46:28 to 10:46:34 EEST,
  token verified to see only the Seed Zero channel, video id
  OsyugHAfCH4, private (`media/piblocks/upload.log`)
- gate: `scripts/yt-qa.py piblocks OsyugHAfCH4 --wait --publish` ran in
  the foreground from 10:46:53 EEST: processing succeeded and the 10
  tags read back on the first poll, 15 of 15 pass (processed, succeeded,
  hd, 1080x1920, title, description, tags as a set, category 27, not for
  kids, PT41S for the 40.000 s file, private); containsSyntheticMedia
  reads absent as on every earlier upload (`media/piblocks/publish.log`)
- publish: the same run set the video public at 2026-09-20T10:46:55+03:00;
  the re-read after 15 s shows privacyStatus public, madeForKids false,
  embeddable true; public at https://youtu.be/OsyugHAfCH4
- slot resolution: published for the 2026-09-20 quota day

### Quota

- attempt 1 of the hard cap of 5 for the quota day that began
  2026-09-20T10:00 EEST; cost 1 + 1,600 + 1 + 50 + 1 = 1,653 units (the
  channels.list verification inside yt-upload.py, the insert, the gate
  read, the update, the re-read); day total after one attempt 1,653
  units

### Repository

- committed as e13d192 "Publish the day twenty-two slate" (sims,
  projects, tasks, docs/niche.md, web/data; no media, previews or
  secrets) and pushed to origin/master at 2026-09-20 10:50 EEST
