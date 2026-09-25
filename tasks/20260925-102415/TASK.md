# Produce short: Pulled spool, a low pull beside a steep pull on the same string

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day27

## Goal

Backlog idea (trend research 2026-09-25, task 20260925-101408, pillar 2
chaos and physics, rolling; read the full entry under "Added by trend
research 2026-09-25" in docs/niche.md):
"Pulled spool: a spool with a 3 cm wheel and a 1.5 cm axle on a table,
the string off the bottom of the axle pulled with 0.2 N at 30 degrees
beside 80 degrees above the table; measure which way it rolls and how
far in one second; expect toward the hand below 60.0 degrees (cos =
axle over wheel) and away above it, 22.9 cm toward at 30 degrees
against 20.4 cm away at 80 (a = F (R cos theta - r) / ((k + 1) m R)
about the contact point, I = 0.6 m R^2, no slip needs mu 0.15 or
more); repeat the pull so the short loops; deterministic, no seed."

Orchestrator notes (2026-09-25, before this brief): the research
numbers hold with a spool mass of 100 g (F = 0.2 N is 0.204 m g):
a = F (R cos theta - r) / ((k + 1) m R) with R = 0.03 m, r = 0.015 m
and k = 0.6 gives 0.4575 m/s^2 toward the hand at 30 degrees (22.9 cm
in 1.00 s) and 0.408 m/s^2 away at 80 degrees (20.4 cm). Two checks
the sim must print: the lift check F sin theta < m g (0.197 N against
0.981 N at 80 degrees; a lighter spool with the same pull leaves the
table) and the no-slip check mu >= f / N with f = F cos theta - m a
and N = m g - F sin theta (0.145 at 30 degrees, 0.05 at 80); set mu =
0.3 and assert both. Torque about the contact point P: with the string
tangent to the bottom of the axle and pulled at theta above the table,
the line of action passes at distance R cos theta - r from P, so the
spool rolls toward the hand when cos theta > r / R (theta below 60.00
degrees) and away when cos theta < r / R; at exactly 60 degrees the
string line passes through P and the spool does not roll. The one
visible causal story: extend the string as a dashed line down to the
table; where that line meets the table relative to the contact point
decides the direction (ahead of P, toward the hand: rolls toward;
behind P: rolls away; through P: no roll). Draw that line and mark P
in both panels. The producer may pick other round values (the angles,
the pull, the mass, k for a spool with heavy flanges) as long as the
sim prints them and both checks pass; keep the switch at a round 60
degrees (r / R = 1/2).

Day twenty-seven, first slot. Chosen because it is a prediction demo
with a majority wrong answer (most people say a low pull drags the
spool away), two panels on the same spool and the same pull that end
in opposite directions, continuous tabletop rolling motion with an
exact closed form, the format of the channel's best shorts (rolling
race 950, turntable 973, braking 1,010, pi blocks 991). Question in the
first two seconds: "Pull the string. Which way does the spool roll?"
(or the producer's better wording, kept identical in the title, the
hook and the payoff). Setup number: the axle is half the wheel (the
two pull angles sit on the panel labels); payoff number: 60 degrees,
the switch angle. The distances go to the description and the
on-screen readouts.

Model: a rigid spool (two flanges of radius R joined by an axle of
radius r, I = k m R^2 about the centre, k = 0.6, mass m) on a level
table; the string leaves the bottom of the axle tangentially toward
the hand and is held at a fixed angle theta above the table with a
constant pull F (the hand moves with the spool so the angle stays
fixed; say so); rolling without slipping, so I_P alpha = torque about
P with I_P = (k + 1) m R^2 and a = alpha R; integrated with RK4 and
compared with the closed form; each pull lasts 1.0 s (or the
producer's duration), then the spool is reset for the next pull. Side
view, the two panels stacked: pull at 30 degrees above, pull at 80
degrees below, both spools starting at the same x with the hand to
the right (or the producer's layout). Print: the accelerations and the
distances at 1.00 s in both panels against the closed form, the
direction of each, the switch angle acos(r / R), where the string line
meets the table relative to P in both panels, the lift and no-slip
checks and the required mu, the schedule in video time, the loop check
and the on-screen text widths. Make the last frame equal the first.
Music seed 83.

## Claim

A spool whose axle is half as wide as its wheel, pulled by a string off
the bottom of the axle, rolls toward the hand when the string is
pulled at 30 degrees above the table (22.9 cm in the first second) and
away from the hand when pulled at 80 degrees (20.4 cm); the switch is
at 60 degrees, where the string line passes through the point touching
the table. Every number in the narration is printed by the sim before
the script is written (the producer may change the round values; the
sim sets the claim).

## Evidence

### Measurements

(recorded after the measure-only run, before scripting)

`sims/spool/spool.py --measure-only` with `projects/spool/manifest.json`
(a 200 g spool with a wheel of radius R = 3 cm and an axle of radius
r = 1.5 cm, r / R = 0.5, I = 0.6 m R^2 about the centre, on a level
table with mu = 0.3 and g = 9.81 m/s^2; the string wound on the axle
leaves its bottom tangentially toward the hand on the right, is held
at a fixed angle above the table and pulled with a constant 0.2 N
(0.102 m g); the hand moves with the spool so the angle and the pull
stay fixed; rolling without slipping about the contact point P, I_P =
(k + 1) m R^2 = 2.880e-4 kg m^2, RK4 at 10,000 steps per second with
the torque taken from the string geometry at every step; two panels,
the string at 30 degrees above and 80 degrees below; each pull 1.0 s,
one pull every 3 s, 14 pulls in 42 s; drawn at 28 px per cm, wheel
radius 84 px; deterministic, no seed; run at 10:38:30 EEST and again
at 10:43 EEST after the card's fourth line was shortened, log in
`media/spool/measure.log`):

- pull at 30 degrees: torque about P = F (R cos theta - r) = 2.1962e-3
  N m clockwise, lever arm R cos theta - r = +1.098 cm; acceleration
  +0.2288 m/s^2 (closed form +0.2288 m/s^2, diff 5.6e-17); after 1.00
  s the spool has rolled 11.44 cm toward the hand (closed form a t^2 /
  2 = 11.44 cm, diff 6.5e-15 m; half-step check 11.438294 cm, diff
  5.4e-15 m) at 0.2288 m/s; the wheel turns 218.5 degrees (3.813 rad)
  and the axle winds in 5.72 cm of string; the string line meets the
  table 2.20 cm behind P, on the far side from the hand; lift check F
  sin theta = 0.100 N against m g = 1.962 N (ok); no-slip check:
  friction f = m a - F cos theta = -0.1275 N against N = m g - F sin
  theta = 1.8620 N, needs mu >= 0.068 (ok with mu = 0.3)
- pull at 80 degrees: torque -1.9581e-3 N m counterclockwise, lever
  arm -0.979 cm; acceleration -0.2040 m/s^2 (closed form -0.2040
  m/s^2, diff 2.8e-17); after 1.00 s the spool has rolled 10.20 cm
  away from the hand (closed form 10.20 cm, diff 4.2e-15 m; half-step
  check 10.198494 cm, diff 1.6e-15 m) at 0.2040 m/s; the wheel turns
  194.8 degrees the other way (3.399 rad) and the axle pays out 5.10
  cm of string; the string line meets the table 0.99 cm ahead of P,
  between P and the hand; lift check F sin theta = 0.197 N against m g
  = 1.962 N (ok); no-slip check: f = -0.0755 N against N = 1.7650 N,
  needs mu >= 0.043 (ok with mu = 0.3)
- switch: the spool rolls toward the hand when cos theta > r / R =
  0.5 and away when cos theta < r / R; acos(r / R) = 60.00 degrees;
  at 60.00 degrees the torque about P is -8.7e-19 N m, the
  acceleration -9.0e-17 m/s^2 and the string line meets the table
  0.0000 cm from P (through the touch point, tangent to the axle); 30
  degrees is 30.00 degrees below the switch, 80 degrees 20.00 degrees
  above it
- the orchestrator's note had the table rule the other way round
  ("ahead of P, toward the hand: rolls toward"); the sim's geometry
  gives the line meeting the table behind P (on the far side from
  the hand) at 30 degrees, where the spool rolls toward the hand, and
  ahead of P (between P and the hand) at 80 degrees, where it rolls
  away: at a low angle the line of action passes above P and the pull
  turns the spool clockwise about P (torque F (R cos theta - r) > 0);
  the visual story and the narration follow the sim (behind: toward;
  in front: away; through P: the switch)
- the research and the orchestrator's numbers (0.4575 and 0.408
  m/s^2, 22.9 and 20.4 cm, mu 0.145) were for a 100 g spool; the mass
  was doubled to 200 g with the same 0.2 N so a 1.00 s pull fits the
  1080 px frame at 28 px per cm with both spools starting on one line
  (11.44 cm toward and 10.20 cm away, accelerations 0.2288 and 0.2040
  m/s^2, the friction needed 0.068 and 0.043); the directions, the
  60.00 degree switch and both checks are unchanged
- for the description (the same spool and pull at other angles, the
  distance after 1.00 s, + ahead of P): 0 degrees +0.3125 m/s^2,
  15.62 cm toward the hand, the line parallel to the table, mu >=
  0.070; 15 degrees +0.2912, 14.56 cm toward, line -5.40 cm, mu 0.071;
  30 degrees as above (line -2.20 cm); 45 degrees +0.1294, 6.47 cm
  toward, line -0.88 cm, mu 0.063; 60 degrees 0, no roll, line 0.00
  cm, mu 0.056; 75 degrees -0.1507, 7.54 cm away, line +0.75 cm, mu
  0.046; 80 degrees as above (line +0.99 cm); 90 degrees -0.3125,
  15.62 cm away, line +1.50 cm, mu 0.035
- schedule printed by the sim (first manifest, first_pull_at -0.5 s,
  to be set from the voice timing): pulls every 3 s at -0.50, 2.50,
  ..., 41.50 s, each ending 1 s later (0.50, 3.50, ..., 39.50 s), the
  end state held 1.2 s, fade out 0.3 s, fade in at the start 0.3 s,
  then the wait for the next pull; title until 2.4 s; card from 30 s;
  the title fades back in over the last 0.5 s and the last frame
  repeats the first (42 s holds exactly 14 pulls)
- text widths (DejaVuSans-Bold): overlay 878 px at 34; title lines
  422 and 863 px at 50 (the second line, "which way does the spool
  roll?", measured 967 px at 56 before any render, so the title is
  set at 50 px); counter 448 px, panel labels 410 px, readouts 351
  and 308 px at 40; legend 822 px, hand tag 79 px, switch tag 176 px
  at 28; payoff lines 691, 804, 883 and 914 px at 40 (a first draft of
  line 4, "at 60 degrees the line meets the touch point", measured
  1,012 px and was shortened before any render); nothing over 950 px;
  the sim asserts every line under 950 px

Narration numbers: half (setup; the axle radius is half the wheel
radius, r / R = 0.5, on the overlay as "wheel 3 cm | axle 1.5 cm" and
in the legend); sixty degrees (payoff; the measured switch acos(r /
R) = 60.00 degrees). The two pull angles stay on the panel labels;
the distances (11.44 cm toward, 10.20 cm away), the accelerations,
the lever arms, the meeting points and the checks go to the readouts,
the card and the description. The claim's distances change from 22.9
and 20.4 cm (a 100 g spool) to 11.44 and 10.20 cm (200 g); the
directions and the 60 degree switch hold as claimed.

### Production

- layout changed after the first smoke frames (28 px per cm with both
  spools on one start line left the spools small): 40 px per cm, wheel
  radius 120 px, the 30 degree spool starting at x = 240 px and the 80
  degree spool at x = 700 px, tables at y = 780 and 1300, string drawn
  4.5 cm long; `--measure-only` rerun with the final manifest at
  10:49:49 EEST (`media/spool/measure.log`, 7 lines): every physics
  number, the switch, the angle scan and the text widths are the same
  as recorded above
- narration `projects/spool/narration.txt`: 110 words, American
  spelling, numbers as words ("half", "sixty degrees"); the question
  "Which way does the spool roll?" after three words, the payoff in
  the same words; every number from the measure-only print
- hook pretests through `scripts/voiceover.sh` into
  `media/spool/hooks/` (10:39:53 to 10:40:23 EEST, log in
  `media/spool/hooks/pretest.log`): hook1 6.28 s, hook2 6.03 s, hook3
  6.73 s and the payoff 5.32 s passed first pass; the setup piece came
  back "onto" for "on to", changed to "drawn down to the table"; the
  mechanism piece came back "deep" for a sentence-initial "Steep,",
  changed to "The steep line lands in front"; hook1 kept (question
  onset 1.67 s of video at +0.6 s, silencedetect -35 dB 0.08 s)
- full take `nix develop -c scripts/voiceover.sh
  projects/spool/narration.txt media/spool/voice.wav`
  (`media/spool/voice.log`): pass 1 matched at 35.19 s but the text
  was 114 words, so "Same spool, same tug." was removed; pass 2 "ok:
  transcript matches narration (33.088435s)" at 10:42:21 EEST, 110
  words, voice.wav md5 bb0f5f5ea621eedc679acae7a7d8707b
- `scripts/voice-timing.py media/spool/voice.wav 0.6`
  (`media/spool/timing.log`, 10:42:28 EEST): "Pull the string, which
  way does the spool roll?" 0.60 to 3.39 s (pause 1.44 to 1.66, the
  question spoken from 1.66 s); "The axle is half as wide as the
  wheel" 3.39 to 5.64; "Top" 7.31; "Bottom" 9.01; "the low one rolls
  toward the hand, the steep one rolls away" to 13.98; "Why?" 13.98
  to 14.57 (heard as a CJK glyph in the per-piece pass only); the
  gold dashes and the touch point 14.57 to 20.37; "the spool rolls
  toward the hand" 20.37 to 22.15; "the spool rolls away" 23.88 to
  25.40; "The switch is at sixty degrees" 25.40 to 27.19; "So, which
  way does the spool roll? Toward the hand below sixty degrees, away
  above it." 28.88 to 33.69; voice 33.09 s, ends at 33.69 s of video
- schedule set from the timing (final manifest): pull_period 3.0,
  pull_duration 1.0, first_pull_at -0.4 (frame 0 is 0.4 s into pull
  1, 1.8 cm rolled, so the thumbnail shows motion in progress), hold
  1.6, reset_fade 0.1 (dips at 2.2 to 2.4 s + 3 k, none over the
  question, "toward the hand", "rolls away" or "sixty degrees");
  pulls at 2.6 + 3 k s end at 0.6, 3.6, ..., 39.6 s; title_until 2.4;
  payoff_t 25.6 with payoff_hold 0.6, so the card and the 60 degree
  reference lines are lit from 26.2 s, before "sixty degrees" (26.77
  to 27.67) and during "below sixty degrees" (31.88 to 32.79); pull
  12 (32.6 to 33.6 s) runs under "away above it" (32.79 to 33.69);
  loop_fade 0.5; the first_pull_at candidates were scored against the
  pause table, and values later than -0.4 were rejected because frame
  0 showed no motion
- smoke frames (`--frames`, `media/spool/smoke-*.png`, four passes
  10:41 to 10:48 EEST): pass 1 spools too small (fixed by the layout
  above, spokes brightened); pass 2 readouts "toward 0.0 cm" and a
  stub bar at the start state (readouts now hidden under 0.05 cm) and
  the "hand" tag over the pull arrow at 80 degrees (tag moved 62 px
  beyond the hand along the string); pass 3 a dark notch in the table
  line during the 0.2 s reset (the fading group was painted at alpha
  0 in the background colour; the moving group is now drawn on an
  RGBA overlay composited at the group alpha) and the counter reading
  "pull 15 of 14" at 41.6 s (modulo fixed); pass 4 clean at 0.0, 1.7,
  19.0, 23.25, 31.0, 41.6 and 41.98 s
- footage `sims/spool/spool.py` (h264 crf 16 yuv420p 60 fps, 2,520
  frames, 8 workers, 10:48:52 to 10:49:31 EEST, log in
  `media/spool/render.log`):
  loop check 0 px (the last frame equals the first), periodicity
  check 0 px (the live scene at 42 s equals 0 s), loop step 32,180 px
  between the last two frames; `media/spool/footage.mp4` 4,384,262
  bytes, md5 ba87cd79ad24be5e5903d3b37adfd1b4
- `nix develop -c scripts/compose.sh spool` (10:49:31 to 10:49:47
  EEST, `media/spool/compose.log`): music seed 83, 42.00 s, gain
  0.18; 37 drawtext captions in `media/spool/captions.filter` (20-char
  chunks, "Pull the string." 0.60 to 1.50, "Which way does the" 1.50
  to 2.71, "spool roll?" 2.71 to 3.31, "sixty degrees, right" 26.77
  to 27.67, "below sixty degrees," 31.88 to 32.79, "away above it."
  32.79 to 33.69; every number and unit in one chunk); final.mp4
  42.000000 s, preview.mp4 42.066667 s, sheet.png 8x6 at 1 fps

### Local QA

- frames extracted from `media/spool/final.mp4` and inspected
  (`media/spool/frame-*.png`): 0.02 s (frame 1: overlay "wheel 3 cm |
  axle 1.5 cm | 0.2 N pull | no seed", the two-line title "Pull the
  string: which way does the spool roll?", both spools mid-pull with
  "toward 2.1 cm" and "away 1.9 cm", nothing else, works as a
  thumbnail), 1.7 s (caption "Which way does the", the question
  spoken from 1.66 s, pull 1 held at 11.4 and 10.2 cm), 12.0 s, 19.0
  s ("the white touch", pull 7 held, gold dashes landing behind P in
  the top panel and in front in the bottom panel), 26.3 s (inside a
  reset dip: tables only, caption "The switch is at", card lit), 27.0
  s ("sixty degrees, right", card "below 60 degrees: toward the hand
  | above 60 degrees: away from the hand | 60 degrees: the line hits
  the touch point", the 60 degree dotted reference from P with the
  "60 degrees" tag in both panels, pull 10 at 0.40 s), 31.0 s
  ("Toward the hand", pull 11 held, card and references), 32.9 s
  ("away above it.", pull 12 at 0.30 s), 41.6 s (counter "pull 14 of
  14", title fading in), frame 2519 (title frame, equals the first);
  contact sheet `media/spool/sheet.png` shows every caption chunk in
  order and no stray frame
- question inside two seconds: title on screen from frame 0, "Pull
  the string." caption from 0.60 s, "Which way does the" from 1.50 s,
  spoken at 1.66 s; the payoff repeats the same words at 28.88 s and
  the card carries them from 26.2 s
- captions match `projects/spool/narration.txt` word for word (37
  chunks, joined text equal to the narration); "sixty degrees" is on
  the card and on both panel tags when spoken at 26.77 and 31.88 s
- no clipping: every fixed line measured under 950 px (widest the
  card's fourth line at 914 px); content spans x = 60 to 1020; the
  caption band rows 1420 to 1530 hold only the caption glyphs (rows
  1440 to 1502 with the descenders); the card's top glyphs start at
  y = 1564; the tables and tags end by y = 1372; the title sits at y
  = 190 and 248 under the overlay at y = 96 to 130
- loop: the raw render differs 0 px between the last and first frame;
  in the encoded final.mp4 frame 2519 differs from frame 0 in 3,485
  px over a channel difference of 24 (0.168 percent, max 85, mean
  0.38, encoder noise on the text edges); the `-ss 41.98` seek lands
  on frame 2519 (same numbers); frame 1 (0.02 s) differs from frame 0
  in 34,458 px because the pull is in progress
- ffprobe: h264 1080x1920 yuv420p 60/1, nb_frames 2,520 (2,520
  decoded), duration 42.000000 s, 4,586,753 bytes; aac 22050 Hz mono;
  atoms ftyp, moov, free, mdat (moov before mdat); md5
  301f3e627a240c22d97bb9e4f2827920; loudness mean -16.6 dB, peak
  -0.0 dB
- open defects: none; approved locally
- `media/spool/measure.log` refreshed at 10:49:49 EEST with the final
  manifest and matches the numbers in the description

### Metadata

- `projects/spool/metadata.json`: title "Which way does the spool
  roll? Axle half the wheel: toward the hand below 60 degrees, away
  above" (96 chars); description 2,849 chars with the setup, the
  "Measured" list (accelerations, distances, lever arms, meeting
  points, the switch, the lift and no-slip checks, the angle scan),
  the "Why" paragraph, the rerun line and the AI-made line, no angle
  brackets; 10 tags; categoryId "27"; privacyStatus "private";
  containsSyntheticMedia true; selfDeclaredMadeForKids false; keys in
  the same order as `projects/merrygoround/metadata.json`
- `docs/niche.md`: the Pulled spool bullet carries "[produced
  2026-09-25: ...]" with the measured numbers, the reversed table
  rule and this task id
- not uploaded; task left open for the orchestrator's review and upload

### Release
- orchestrator review (11:12 EEST): the task evidence, the 8x6 contact
  sheet and the full-resolution frames at 0.02, 19.0 and 27.0 s
  inspected: the question "Pull the string: / which way does the spool
  roll?" over both spools from frame 0 with the first pull already in
  progress ("toward 2.1 cm", "away 1.9 cm"), the string leaving the
  bottom of the axle toward the hand in both panels with the gold
  dashed string line drawn down to the table and the white touch point
  marked (the thumbnail); 19.0 s shows pull 7 held at "toward 11.4 cm"
  and "away 10.2 cm" with the gold line landing behind the touch point
  above and in front of it below, the green and red distance bars on
  the table; 27.0 s shows the 60 degree dotted reference from the touch
  point with its tag in both panels and the card "which way does the
  spool roll? / below 60 degrees: toward the hand / above 60 degrees:
  away from the hand / 60 degrees: the line hits the touch point" lit
  under the caption "sixty degrees, right"; the narrated numbers (half
  as wide, sixty degrees) match r / R = 0.5 and acos(r / R) = 60.00
  degrees in media/spool/measure.log; the producer's reversal of the
  brief's table rule is correct (torque about P is x_Q F sin theta for
  a string line meeting the table at x_Q, so a line landing behind P
  rolls the spool toward the hand) and the 200 g mass and 0.2 N pull
  pass the lift and no-slip checks; captions sit in the y 1440 to 1502
  band clear of the geometry; final.mp4 h264 1080x1920 60 fps, 2,520
  frames, aac 22050 Hz mono, 42.000 s (scene_duration 42, so the gate
  accepts PT42S or PT43S), moov before mdat, md5
  301f3e627a240c22d97bb9e4f2827920; title 96 characters; the
  description carries no < or >; approved for release
- quota check: clock 2026-09-25T11:10:07+03:00; zero upload attempts recorded since the
  2026-09-25 10:00 EEST boundary (no upload entries in web/data/log.jsonl
  today, newest media/*/upload.log is merrygoround at 2026-09-24 10:53);
  this is insert attempt 1 of the hard cap of 5
- attempt 1 recorded at 2026-09-25T11:10:07+03:00, video name spool, before running
  `scripts/yt-upload.py spool`

### Published
- upload: `scripts/yt-upload.py spool` (attempt 1) ran 11:10:07 to
  11:10:13 EEST, token verified to see only the Seed Zero channel, video
  id 5xhaVWmicBI, private (`media/spool/upload.log`)
- gate: `scripts/yt-qa.py spool 5xhaVWmicBI --wait --publish` ran in the
  foreground from 11:10:19 EEST: processing succeeded and the 10 tags
  read back within the first minute of polling, 15 of 15 pass
  (processed, succeeded, hd, 1080x1920, title, description, tags as a
  set, category 27, not for kids, PT43S for the 42.000 s file, private);
  containsSyntheticMedia reads absent as on every earlier upload
  (`media/spool/publish.log`)
- publish: the same run set the video public at 2026-09-25T11:11:07+03:00;
  the re-read after 15 s shows privacyStatus public, madeForKids false,
  embeddable true; public at https://youtu.be/5xhaVWmicBI
- slot resolution: published for the 2026-09-25 quota day

### Quota
- attempt 1 of the hard cap of 5 for the quota day that began
  2026-09-25T10:00 EEST; cost 1 + 1,600 + 55 = 1,656 units (the
  channels.list verification inside yt-upload.py, the insert, the gate
  run's reads, update and re-read as printed by yt-qa.py); day total after
  one attempt 1,656 units plus 5 for the 10:18 stats refresh
