# Produce short: Loop the loop, released from the top's height beside 2.5 R

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day22

## Goal

Backlog idea (trend research 2026-09-20, task 20260920-100347, pillar 2
chaos and physics):
"Loop the loop: a puck on a frictionless track with a 1 m loop released
from the height of the loop's top (2R) beside one released from 2.5R;
measure where each leaves the track; expect the 2R puck to peel off
41.8 degrees above the centre (1.67 R up, 48 degrees short of the top)
and the 2.5R puck to pass the top at 3.13 m/s with zero track force
(sin theta = 2(h/R - 1)/3; a rolling ball needs 2.7R and peels off at
36.0 degrees from 2R); the passing puck circles again and again so the
short loops; deterministic, no seed."
Day twenty-two, second slot. Chosen because the channel's best shorts
are continuous tabletop motion in two panels on the same input with a
closed-form check (rolling race 1,010 views, coupled pendulums 1,078,
hoop bead 982, cradle 956, monkey and hunter 962), and everyone guesses
that starting level with the top of the loop is enough. Question in
the first two seconds: "Start level with the top of the loop. Does the
puck make it round?"

## Claim

Released from the height of the top of a one metre loop, a frictionless
puck does not make it round: it leaves the track forty eight degrees
short of the top and falls; released from two and a half times the
radius it passes the top and keeps circling. Every number in the
narration is printed by the sim before the script is written.

## Evidence

### Measurements

(recorded after the measure-only run, before scripting)

`sims/looptrack/looptrack.py --measure-only` with
`projects/looptrack/manifest.json` (a frictionless point puck on one
track: a straight ramp at 45 degrees from (-2.997, 2.50) m into a dip arc
of radius 1.2 m (tangent point (-0.849, 0.352) m), then a vertical loop of
radius R = 1 m with its bottom at (0, 0) and its top at (0, 2), then a
flat exit of 2.2 m; g = 9.80665 m/s^2; ramp 3.039 m, dip 0.942 m, loop
6.283 m; two panels, the same track, released from rest at h = 2 R (top
panel, level with the top of the loop) and h = 2.5 R (bottom panel); RK4
on (s, v) along the arc length at 3,600 steps per second (dt = 2.78e-4
s), track force N = m (v^2 kappa + g n_y) with v from energy so N is
exact in s, departure where N < -1e-7 m g located by bisection on s, then
a closed-form projectile to the loop wall; played at 1/3 speed;
deterministic, no seed; first run at 10:31 EEST, re-run at 10:37 after
the schedule change, log in `media/looptrack/measure.log`):

- closed forms: the puck leaves where sin theta = 2 (h/R - 1) / 3, theta
  above the loop centre: h = 2 R gives 41.81 degrees above the centre =
  48.19 degrees short of the top at a height of 1.6667 R; 2.25 R gives
  56.44 degrees; 2.49 R gives 83.38; the threshold is 2.5 R (sin theta =
  1, N = 0 exactly at the top); speed at the top from 2.5 R sqrt(g R) =
  3.1316 m/s; bottom speeds sqrt(2 g h) 6.2631 m/s from 2 R and 7.0024
  m/s from 2.5 R; track force at the bottom of the loop (2 h/R + 1) m g:
  5 weights from 2 R, 6 weights from 2.5 R; a rolling solid ball (k =
  0.4, v^2 = 2 g (h - y) / 1.4) needs 2.7 R and from 2 R leaves at sin
  theta = 10 (h/R - 1) / 17, 36.03 degrees
- top panel, level with the top (h = 2 R = 2.0 m, ramp point (-2.497, 2)
  m, s = 0.7071 m): reaches the loop bottom at 0.9754 s at 6.2631 m/s
  (closed form 6.2631), track force there 5.0000 weights; LEAVES the
  track at 1.4686 s (0.4932 s after entering the loop) at 131.810 degrees
  round from the bottom = 41.810 degrees above the centre = 48.190
  degrees short of the top (closed form 41.810 and 48.190); height 1.6667
  m = 1.6667 R at x = 0.7454 m; speed 2.5569 m/s (RK4 speed 2.5569),
  velocity (-1.7046, 1.9058) m/s, 48.2 degrees above horizontal heading
  left; track force at departure 1.8e-15 weights, the last sample before
  it 0.001473; flight: peak 1.8519 m at x = 0.4141 m after 0.1943 s,
  meets the loop wall after 0.7774 s of flight at (-0.5797, 0.1852) m,
  324.57 degrees round from the bottom (35.43 degrees up the left side),
  at 2.2459 s after release, speed 5.9661 m/s (1.9256 along the track,
  5.6468 into it); the run ends at the landing (the impact is not
  modelled); energy drift before departure 3.1e-9
- bottom panel, half a radius higher (h = 2.5 R = 2.5 m, ramp point
  (-2.997, 2.5) m, s = 0): reaches the loop bottom at 1.0742 s at 7.0024
  m/s (closed form 7.0024), track force there 6.0000 weights; passes the
  top at 1.7189 s (0.6447 s after entering the loop) at 3.1316 m/s
  (closed form sqrt(g R) = 3.1316); track force at the top 0.000000
  weights (closed form 2 (h/R - 2) - 1 = 0), smallest sampled value in
  the loop 3.023e-9 weights at 1.7189 s, 180.003 degrees round; MAKES IT
  ROUND: leaves the loop at 2.3636 s at 7.0024 m/s and reaches the end of
  the exit at 2.6778 s; energy drift 1.0e-8
- checks (not drawn): 2.25 R leaves at 56.44 degrees above the centre
  (33.56 short, closed form 56.44), height 1.8333 R, at 1.5460 s, lands
  after 0.6445 s at 280.7 degrees round; 2.49 R leaves at 83.38 degrees
  (6.62 short, closed form 83.38), height 1.9933 R, at 1.6832 s, lands
  after 0.1468 s at 199.9 degrees round; 2.51 R makes it round with
  0.0200 weights of track force at the top, top at 1.7174 s at 3.1627
  m/s; rolling solid ball from 2 R leaves at 36.03 degrees above the
  centre (53.97 short, closed form 36.03) at 1.6934 s at 2.4018 m/s;
  rolling solid ball from 2.7 R makes it round with 0.000000 weights at
  the top, top speed 3.1316 m/s at 2.0109 s
- schedule printed by the sim (4 runs of 10 s at 1/3 speed, release at
  0 s into each run, crossfade reset over the last 0.5 s): in each run
  the top puck enters the loop at +2.93 s, leaves the track at +4.41 s
  and lands at +6.74 s; the bottom puck enters at +3.22 s, passes the
  top at +5.16 s, leaves the loop at +7.09 s and is off the end at +8.03
  s; runs start at 0, 10, 20 and 30 s, so the departures fall at 4.41,
  14.41, 24.41 and 34.41 s and the top crossings at 5.16, 15.16, 25.16
  and 35.16 s; resets 9.5-10, 19.5-20, 29.5-30 and 39.5-40 s (the last
  one is also the loop fade); title until 2.4 s; card from 22 s
- text widths (DejaVuSans-Bold): overlay 856 px at 34; title lines 736,
  664 and 643 px at 56; panel labels 398 and 443 px at 40; sublabel 441,
  level label 278 and readout label 314 px at 28; readout 334 px at 48;
  marks 229, 311 and 314 px at 32; payoff lines 669, 799 and 883 px at
  40; nothing over 950 px (the first draft's payoff lines were 967 and
  983 px and were shortened before any render)

Narration numbers: level with the top (setup, the 2 R release, with the
bottom puck named as half a radius higher), forty eight degrees short of
the top (payoff, the 48.190 measured, shown as 48 on the card and the
mark) and two and a half times the radius (payoff, the 2.5 R release,
shown as 2.5 x the radius on the card). The speeds, the heights, the
track forces, the flight, the closed forms and the checks go to the
description. No number contradicted the claim.

### Production

- layout (`sims/looptrack/looptrack.py`): overlay at y 96, title at y
  190/252/314, two panels of 543 px from y 350 with the loop bottom 18 px
  above each panel's lower edge, loop radius 200 px (R = 1 m at 200 px
  per metre; 240 px would not fit a 2.5 m start in a 543 px panel),
  loop centre at x 660, ramp top at x 60, flat exit to the frame edge;
  a dashed level line at the height of the top of the loop from the ramp
  to the top with the label "level with the top" in the top panel; a
  tick across the ramp at each release point; panel labels top-right
  ("level with the top" / "half a radius higher" at 40 px, "released
  from rest 2.0 m up" / "2.5 m up" at 28 px); a live "push from the
  track" readout bottom-left in weights (gold when under 0.05); at the
  departure a gold radius to the departure point, a muted radius to the
  top, a gold arc outside the loop across the gap and the mark "48 deg
  short"; in flight a dotted trail; at the top crossing a gold ring at
  the top and "push 0 at the top", then "all the way round" once the
  puck leaves the loop; captions at caption_y 0.75, card from y 1592;
  geometry drawn at 2x and reduced
- smoke frames (`--frames`, 10:33 EEST, at 0, 1.5, 4.8, 5.5, 6.5, 7.2,
  7.8, 29.5 and 39.8 s): three defects: the "over the top, push 0" mark
  was left-aligned at x 830 and ran to x 1197, off the frame; "48 deg
  short" ended 21 px from the edge; the bottom puck's start sat 15 px
  under the top panel's exit line; fixes: loop centre 700 to 660 px,
  marks right-aligned at x 1040, "push 0 at the top" (311 px); the run
  period changed from 5 x 8 s to 4 x 10 s so the marks hold on screen
  before each reset; smoke pass 2 at 10:38 EEST (0, 1.5, 4.6, 5.2, 7.2,
  9.7, 22.5, 25.5, 27.5, 29.7, 34.5, 39.8 s) clean, except that the
  readout popped at the run boundary because the reset only faded the
  live number; the reset was then rewritten as a whole-frame pixel
  crossfade between the live state and the start state
- narration (written after the measure-only run, 10:34 EEST): three
  hooks tried, "A puck on a loop track. Start level with the top of the
  loop. Does the puck make it round?" (kept: it names the setup and asks
  the title question in the title's words), "Start level with the top
  of the loop. Does the puck make it round?" (dropped: an audio-initial
  "Start" risks the clipped-onset mishearing seen with "Spin") and "Is
  starting level with the top of the loop enough to make it round?"
  (dropped: it does not name the puck and the payoff could not repeat
  it in the same words); `projects/looptrack/narration.txt`, 107 words;
  the setup is "level with the top" and "half a radius higher", the
  payoffs "forty eight degrees short of the top, the puck comes off" and
  "from two and a half times the radius, yes, all the way round";
  "comes off" chosen over "lets go" because the normaliser splits a
  transcribed "let's"; the payoff sentence reordered so captions.py
  keeps "Forty eight degrees" in one 20-character chunk ("Forty eight
  degrees" / "short of the top," / "the puck comes off." and "From two
  and a half" / "times the radius," / "yes."), checked with chunks()
  before recording
- voice: `scripts/voiceover.sh projects/looptrack/narration.txt` passed
  on the first run at 10:35:34 EEST with no misheard word (the
  round-trip transcript wrote "two and a half" back as words): 107
  words, 29.48 s, ends at 30.08 s of the 40 s video, 3.6 words/s; log
  in `media/looptrack/voice.log`
- timing (`scripts/voice-timing.py`, +0.6 s offset): "A puck on a loop
  track. Start level with the top of the loop. Does the puck make it
  round? Same track." 0.60 to 5.99 s over the title (to 2.4 s) and run
  1 (entry 2.93 s, departure 4.41 s); "No friction. One puck starts
  level with the top, the other half a radius higher." 5.99 to 10.49 s
  over run 1's flight, landing (6.74 s) and round trip (7.09 s); "The
  track can only push on the puck. Near the top, the puck needs speed to
  keep that push." 10.49 to 15.65 s over run 2's descent and departure
  (14.41 s, the readout dropping to 0.0); "The top puck slows too much,
  the push drops to zero, and it comes off." 15.65 to about 20.1 s over
  run 2's flight and landing (16.74 s); "So does the puck make it
  round? Level with the top, no." about 20.1 to 23.5 s over run 3's
  descent (release 20.0 s, entry 22.93 s); "Forty eight degrees short
  of the top, the puck comes off." about 23.5 to 26.11 s with the card
  on from 22.0 s, the departure at 24.41 s and the flight to 26.74 s;
  "From two and a half times the radius, yes." 26.11 to 28.94 s after
  the top crossing at 25.16 s, with the loop exit at 27.09 s and the
  "all the way round" mark from then; "All the way round." 28.94 to
  30.08 s with the mark on until the reset at 29.5 s; run 4 (30 to 40
  s) plays both outcomes under the card with no narration
- schedule decisions: 4 runs of 10 s released at the run start (motion
  from the first frame; the first frame is the pucks at rest on their
  marks under the title); release_at 0.0 and run_period 10 chosen from
  the timing so that run 3's departure (24.41 s) falls inside "the puck
  comes off" (24.95 to 26.11 s) and its round trip (27.09 s) inside
  "From two and a half times the radius, yes"; payoff_t 22.0 s, after
  run 2's departure (14.41 s) and landing and before the first payoff
  number (23.5 s); the two answers are 6.5 s apart in the voice while
  the two events are 2.7 s apart on screen, so the mechanism sentence
  runs about 2 s behind run 2's departure and the card carries the
  numbers
- footage: `sims/looptrack/looptrack.py` (no arguments) wrote
  `media/looptrack/footage.mp4`, 40.00 s at 60 fps, 2,400 frames, h264
  crf 16 yuv420p, in 53 s with eight forked workers, 10:38:39 to
  10:39:31 EEST; the same run re-printed every measurement above
  (`media/looptrack/render.log`); loop check: the last frame differs
  from the first in 0 px
- compose: `scripts/compose.sh looptrack` wrote
  `media/looptrack/final.mp4` at 10:39:56 EEST (h264 1080x1920 60 fps,
  aac 22050 Hz mono, 40.000 s; music seed 62 at gain 0.18; captions at
  caption_y 0.75, 33 drawtext filters); loudness mean -17.5 dB, peak 0.0
  dB; preview (40.07 s) and 8x5 contact sheet written
  (`media/looptrack/compose.log`)

### Local QA

- smoke pass 1 (10:33 EEST, `--frames` before any render): three layout
  defects found and fixed (the clipped "over the top, push 0" mark, the
  "48 deg short" mark 21 px from the edge, the bottom puck's start under
  the top panel's exit line; see Production); smoke pass 2 (10:38 EEST)
  clean, the readout pop at the run boundary fixed by the whole-frame
  crossfade before the footage render
- final pass (10:40 EEST): frames at 0.02, 1.5, 4.5, 7.0, 12.5, 14.8,
  18.0, 22.5, 24.0, 25.5, 27.5, 29.3, 35.5 and 39.95 s extracted from
  final.mp4 (`media/looptrack/frame-*.png`) and inspected with the 8x5
  contact sheet (`media/looptrack/sheet.png`): 0.02 s shows the overlay
  at y 96, the title "Start level with the top / of the loop. Does the /
  puck make it round?" at y 190 to 314 clear of it and of the geometry,
  both pucks at rest on their start ticks with the top puck on the
  dashed "level with the top" line and both readouts at 0.7 x weight
  (the thumbnail); 1.5 s shows both pucks sliding under "A puck on a
  loop"; 4.5 s shows run 1's departure under "Does the puck make": the
  gold radius, the gap arc, "48 deg short" and the readout 0.0 x weight
  in gold, the bottom puck climbing at 0.8 x weight; 7.0 s shows the
  landed puck with its dotted flight across the loop, the bottom puck
  at the loop bottom at 5.9 x weight with the gold ring and "push 0 at
  the top", under "friction."; 12.5 s shows run 2's descent under "push
  on the puck."; 14.8 s shows run 2's departure with the readout at 0.0
  under "puck needs speed to"; 18.0 s shows "too much, the push" with
  the top puck landed and the bottom puck leaving at the frame edge;
  22.5 s shows the card fading in under "Level with the top," with run
  3 descending; 24.0 s shows "Forty eight degrees" with the card fully
  lit ("level with the top: no, 48 deg short / 2.5 x the radius: yes,
  all the way round") and the top puck climbing at 1.1 x weight; 25.5 s
  shows "the puck comes off." over the flight, the marks and 0.0 x
  weight; 27.5 s shows "From two and a half" with the bottom puck on
  the exit under "all the way round"; 29.3 s shows "All the way round."
  with the mark still on; 35.5 s shows run 4 under the card with the
  bottom puck just past the top ("push 0 at the top", 0.2 x weight) and
  the top puck in flight; 39.95 s shows the crossfade to the title
  frame with the card fading out; captions match the narration word for
  word and sit in the y 1440 to 1520 band with the exit track ending at
  y 1418 and the card from 1592; no text clips at the frame edges; the
  payoff numbers are on screen when spoken (card from 22.0 s, "forty
  eight" at about 23.5 s, "two and a half" at 26.11 s); the departure
  angle is marked by the radius, the arc and "48 deg short"; the loop
  closes (0 px difference); approved

### Metadata

- `projects/looptrack/metadata.json`: title "Start level with the top of
  the loop. Does the puck make it round? No: it lets go 48 degrees
  short." (99 characters); description with the setup (the track, the
  two release heights, the exact track force from energy, RK4 at 3,600
  steps per second, no seed, one third speed), a Measured list (the
  closed form and the 2.5 R threshold, the level-with-the-top run with
  its departure, flight and landing, the 2.5 R run with its zero track
  force at the top, the 2.25 R, 2.49 R, 2.51 R and rolling-ball checks,
  the energy drift), a Why paragraph (the track pushes toward the centre
  but cannot hold on; the track's share of the centre-pointing force
  hits zero where 2 g (h - y) / R = -g cos(angle); the top needs sqrt(g
  R), which costs half a radius of extra height), the rerun line and
  the AI-made line; 10 tags (loop the loop, roller coaster loop,
  vertical loop, normal force, centripetal force, energy conservation,
  physics, physics visualization, simulation, shorts); category 27;
  private; containsSyntheticMedia true; selfDeclaredMadeForKids false
- not uploaded; task left open for the orchestrator's review and upload

### Release

- orchestrator review (10:47 EEST): the task evidence, the 8x5
  contact sheet and the full-resolution frames at 0.02, 14.8, 25.5, 27.5
  and 39.95 s inspected: the question over the two tracks with the top
  puck on the dashed "level with the top" line on the first frame; run
  2's departure at 14.8 s with the gold radius, the gap arc, "48 deg
  short" and the readout 0.0 x weight; the card "does the puck make it
  round? / level with the top: no, 48 deg short / 2.5 x the radius:
  yes, all the way round" under "the puck comes off." at 25.5 s with
  the flight dotted across the loop; "From two and a half" at 27.5 s
  with the bottom puck on the exit under "all the way round"; the
  crossfade at 39.95 s; every caption in the clear band, no clipping;
  final.mp4 h264 1080x1920 60 fps, 2,400 frames, aac 22050 Hz mono,
  40.000 s, moov before mdat, md5 ee5f90ff93b43c60bf442057a1f6d527;
  title 99 characters; approved for release
- quota check: clock 2026-09-20T10:47:10+03:00; one upload attempt (piblocks, 10:46:28,
  uploaded private as OsyugHAfCH4, gate running) recorded since the
  2026-09-20 10:00 EEST boundary (log entry and media/piblocks/upload.log
  both checked); this is insert attempt 2 of the hard cap of 5
- attempt 2 recorded at 2026-09-20T10:47:10+03:00, video name looptrack, before running
  `scripts/yt-upload.py looptrack`

### Published

- upload: `scripts/yt-upload.py looptrack` ran 10:47:10 to 10:47:16 EEST,
  token verified to see only the Seed Zero channel, video id
  Mm_gJO6VKsc, private (`media/looptrack/upload.log`)
- gate: `scripts/yt-qa.py looptrack Mm_gJO6VKsc --wait --publish` ran in
  the foreground from 10:47:27 EEST: processing succeeded and the 10
  tags read back, 15 of 15 pass (processed, succeeded, hd, 1080x1920,
  title, description, tags as a set, category 27, not for kids, PT41S
  for the 40.000 s file, private); containsSyntheticMedia reads absent
  as on every earlier upload (`media/looptrack/publish.log`)
- publish: the same run set the video public at 2026-09-20T10:47:47+03:00;
  the re-read after 15 s shows privacyStatus public, madeForKids false,
  embeddable true; public at https://youtu.be/Mm_gJO6VKsc
- slot resolution: published for the 2026-09-20 quota day

### Quota

- attempt 2 of the hard cap of 5 for the quota day that began
  2026-09-20T10:00 EEST; cost 1 + 1,600 + 53 = 1,654 units (the
  channels.list verification inside yt-upload.py, the insert, the gate
  run's reads, update and re-read as printed by yt-qa.py); day total
  after two attempts 3,307 units

### Repository
