# Produce short: Hinged stick and ball, 30 degrees beside 60 degrees

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day22

## Goal

Backlog idea (trend research 2026-09-20, task 20260920-100347, pillar 2
chaos and physics):
"Hinged stick (Galileo's paradox): a 1 m rod hinged at one end with a
ball resting on its tip, propped at 30 degrees beside the same rod at
60 degrees, both released at once; measure when the rod lies flat and
when the ball lands; expect the 30 degree rod flat at 0.281 s with the
ball still 11 cm up (the tip starts at 1.125 g and the ball drops into
a cup 0.866 L along the rod) and the 60 degree rod flat at 0.481 s
after the ball has landed at 0.420 s (tip at 0.375 g); the tip beats
the ball below 35.26 degrees (cos^2 theta = 2/3); deterministic, no
seed."
Day twenty-two, third slot. Chosen because the channel's best shorts
are continuous tabletop motion in two panels on the same input with a
closed-form check (rolling race 1,010 views, coupled pendulums 1,078,
hoop bead 982, cradle 956, monkey and hunter 962), and a falling stick
that outruns a free-falling ball is a plain race question with a
threshold the two panels straddle. Question in the first two seconds:
"Let go of a stick with a ball on its tip. Which one hits the table
first?"

## Claim

A one metre stick hinged at one end and propped at thirty degrees falls
flat faster than a ball dropped from its tip: the stick is down at
about zero point two eight seconds with the ball still eleven
centimetres in the air; propped at sixty degrees the ball lands first.
Every number in the narration is printed by the sim before the script
is written.

## Evidence

### Measurements

(recorded after the measure-only run, before scripting)

`sims/hingedstick/hingedstick.py --measure-only` with
`projects/hingedstick/manifest.json` (a uniform stick of length 1 m
hinged at its left end on a table, propped at 30 degrees (top panel) and
60 degrees (bottom); a free ball held at rest level with the tip, its
centre 1 m from the hinge, just past the tip's reach: the tip sweeps
outward on an arc of radius L as the stick falls, so a ball "a hair to
the right of the tip" would be struck, and the ball sits at x = L where
the tip lands beside it; both let go at t = 0; g = 9.80665 m/s^2; the
stick obeys theta'' = -(3 g / 2 L) cos theta and stops flat, the ball
falls freely and stops on the table; RK4 at 6,000 steps per second, dt =
1.67e-4 s, for 0.8 s; the ball is a point for every number and is drawn
larger than life; deterministic, no seed; log in
`media/hingedstick/measure.log`, run at 10:30 EEST, 1 s):

- tip's initial vertical acceleration (3/2) g cos^2 theta0 equals g at
  35.26 degrees (cos^2 theta0 = 2/3): below it the tip starts down
  faster than a free ball, above it slower
- top panel, 30 degrees: tip height 0.5000 m; the tip starts down at
  1.125 g; the stick lies flat at 0.2811 s (energy integral 0.2811 s,
  -8.0e-9 s); the ball lands at 0.3193 s (sqrt(2 h / g) = 0.3193 s,
  -8.6e-10 s); the stick lands first, 0.0382 s before the ball; when the
  stick is flat the ball is 11.25 cm up; tip speed on landing 3.835 m/s
  (closed form sqrt(3 g L sin theta0) = 3.835 m/s)
- bottom panel, 60 degrees: tip height 0.8660 m; the tip starts down at
  0.375 g; the stick lies flat at 0.4811 s (energy integral 0.4811 s,
  -4.0e-9 s); the ball lands at 0.4203 s (closed form 0.4203 s, -8.1e-9
  s); the ball lands first, 0.0609 s before the stick; when the ball
  lands the stick is at 16.06 degrees with its tip 27.66 cm up; tip
  speed on landing 5.048 m/s (closed form 5.048 m/s)
- classic cup-on-the-tip variant (not drawn): at 30 degrees the ball
  starts 0.866 m from the hinge, the stick falls away from under it and
  lies flat at 0.2811 s, and the ball lands on the flat stick at 0.3193
  s, 0.866 m along it; at 60 degrees the ball starts 0.500 m from the
  hinge, leaves the tip at once (the tip starts at 0.375 g) and meets
  the moving stick at 0.3192 s with the stick at 36.23 degrees, then
  rides it down (the loaded stick is not simulated); in the cup version
  the stick never loses, which is why the short races a free ball beside
  the tip
- check at 45 degrees (not drawn): stick flat at 0.3701 s (energy
  integral 0.3701 s), ball lands at 0.3797 s (closed form 0.3797 s); the
  stick lands first, by 0.0097 s; tip starts at 0.750 g
- crossover angle (stick flat and ball landing at the same time,
  bisection on the closed forms between 30 and 60 degrees): 47.907
  degrees, both at 0.3890 s; RK4 at that angle: stick flat 0.3890 s,
  ball 0.3890 s; below it the stick wins, above it the ball
- check at half the time step (12,000 steps per second): 30 degrees
  stick flat 0.281136 s (+4.9e-9), ball 0.319330 s (+4.4e-10), ball
  11.245 cm up at the flat; 60 degrees stick flat 0.481148 s (+2.3e-9),
  ball 0.420262 s (+7.1e-9), tip 27.660 cm up at the ball's landing
- a first measure run (10:30 EEST) read the stick's angle at the ball's
  landing from the nearest RK4 sample (27.63 cm against the half-step's
  27.665); the sim now interpolates inside the step (27.66 cm) and was
  re-run at 10:30 EEST before scripting

Decisions: the backlog line's ball on the tip is not used (the cup
variant above: the stick falls away from under the ball below 35.26
degrees and the ball drops onto the stick above it, so the stick lands
first or together at every angle); the free ball level with the tip
keeps the race honest and flips the answer between the panels. The
brief's "a hair to the right of the tip" became "just past the tip's
reach" (ball centre at x = L from the hinge) because the tip sweeps
outward on its arc as the stick falls and would strike a ball placed
inside its reach (0.134 L inside at 30 degrees); on screen the ball
hangs on the dashed release level 13 cm right of the 30 degree tip and
50 cm right of the 60 degree tip, and the flat stick's tip lands just
short of it. Payoff wording: the 60 degree panel uses the parallel "tip
still 28 cm up" (27.66 cm rounded, what the ghost stick on screen shows
at the ball's landing) rather than the 0.0609 s gap, so both panels
answer with the same kind of number; the two landing times stay on the
readouts and the card.

Narration numbers: thirty degrees and sixty degrees (setup, the panel
labels), zero point two eight seconds and eleven centimeters (the 30
degree payoff: 0.2811 s and 11.25 cm, shown as 0.28 s and 11 cm on the
card and 0.281 s / 11 cm on the readouts), twenty eight centimeters (the
60 degree payoff: 27.66 cm rounded, 28 cm on the card and the ghost
label). The accelerations in g, the 35.26 degree threshold, the tip
speeds, the 45 degree case, the crossover angle, the cup variant and
the checks go to the description.

### Production

- narration (written after the measure-only run, 10:31 EEST): three
  hooks tried, "A stick and a ball, let go together. Which hits the
  table first?" (kept: it asks the title's question in the title's
  words and the payoff answers it in the same words; the opener is a
  short fragment before the question so the first spoken word is not a
  verb that whisper clips, after "Spin" came back "Thin" on day
  nineteen), "Let go of a stick and a ball together. Which hits the
  table first?" (dropped from the narration, kept as the on-screen
  title: the clipped-onset risk on the first word of the audio) and
  "Can a falling stick beat a falling ball to the table?" (dropped: a
  yes/no question that does not name the two angles, and the payoff
  could not answer it in the same words); `projects/hingedstick/narration.txt`,
  110 words; setup numbers thirty degrees and sixty degrees, payoff zero
  point two eight seconds with the ball still eleven centimeters up, and
  the ball with the tip still twenty eight centimeters up; "in slow
  motion" instead of "one tenth speed" because whisper may write "1/10",
  which the normaliser cannot match; the payoff sentences were split
  into short sentences so captions.py (20 characters a chunk) keeps
  "zero point two eight", "eleven centimeters" and "twenty eight" whole
  (checked with chunks() before the voice run: "the stick, flat at" /
  "zero point two eight" / "seconds." / "The ball is still" / "eleven
  centimeters" / "up." and "The tip is still" / "twenty eight" /
  "centimeters up.")
- voice: `scripts/voiceover.sh projects/hingedstick/narration.txt
  media/hingedstick/voice.wav` passed on the first run at 10:32 EEST
  with no misheard word ("still" twice, "Which" after a full stop and
  "hangs" all came back right): 110 words, 34.12 s, ends at 34.72 s of
  the 40 s video, 3.2 words/s; log in `media/hingedstick/voice.log`
- timing (`scripts/voice-timing.py`, +0.6 s offset): "A stick and a
  ball, let go together" 0.60 to 2.73 s over the title (to 2.4 s) with
  the first drop released at 0.60 s; "which hits the table first, the
  stick is hinged at one end" 2.73 to 5.91 s across the first landings
  (30 degree stick 3.41 s, ball 3.79 s, 60 degree ball 4.80 s, stick
  5.41 s); "and the ball hangs level with its tip" 5.91 to 7.89 s over
  the reset (6.67 s) and the second release (7.27 s); "Both drop at
  once, in slow motion. On top, the stick starts at thirty degrees"
  7.89 to 12.86 s; "Its tip starts down faster than the ball, and the
  stick lands first. Below, the stick starts at sixty degrees" 12.86 to
  18.95 s over the third drop (release 13.93 s, 30 degree stick flat
  16.74 s and flagged first, 60 degree ball down 18.14 s); "Its tip
  starts down slower" 18.95 to 20.80 s with the fourth release at 20.60
  s; "And the ball wins. So, which hits the table first?" 20.80 to
  23.87 s with the 30 degree stick flat at 23.41 s; "At thirty degrees,
  the stick" 23.87 to 25.79 s over that flagged stick and the card
  (payoff_t 23.6 s, set from this timing: after the 23.41 s landing and
  before the payoff sentence); "flat at zero point two eight seconds"
  25.79 to 28.18 s over the card's "0.28 s" across the reset at 26.67
  s; "The ball is still eleven centimeters up" 28.18 to 30.33 s over the
  card's "ball still 11 cm up" with the fifth drop's stick landing at
  30.08 s and its ghost label "still 11 cm up"; "at sixty degrees, the
  ball" 30.33 to 32.32 s over the fifth drop's ball landing at 31.47 s,
  flagged first; "The tip is still twenty eight centimeters up" 32.32 to
  34.72 s over the ghost stick "tip still 28 cm up" (to the reset at
  33.33 s) and the card
- footage: `sims/hingedstick/hingedstick.py` (no arguments) wrote
  `media/hingedstick/footage.mp4`, 40.00 s at 60 fps, 2,400 frames, in
  30 s with eight forked workers, at 10:33 EEST; the same run re-printed
  every measurement above (`media/hingedstick/render.log`); schedule
  printed by the sim: 1/10 speed, 6 drops of 6.667 s, both let go 0.6 s
  into each cycle; 30 degrees: stick flat 3.41 s and ball down 3.79 s
  into the cycle; 60 degrees: ball down 4.80 s and stick flat 5.41 s;
  everything down by 5.41 s and held to the reset; releases at 0.60,
  7.27, 13.93, 20.60, 27.27, 33.93 s; the 30 degree stick lands at 3.41,
  10.08, 16.74, 23.41, 30.08, 36.74 s and the 60 degree ball at 4.80,
  11.47, 18.14, 24.80, 31.47, 38.14 s; title until 2.4 s; card at 23.6
  s; crossfade over the last 0.6 s; text widths at most 856 px (the
  overlay; title lines 507, 619 and 819 px, labels 433, sublabel 702 at
  28 px, clock 197 at 48 px, readouts 253 to 357 at 36 px, ghost labels
  243 and 304 at 32 px, payoff lines 578, 703, 602, 679 and 580 px at 40
  px), so nothing clips at 1080 px; smoke frames at 0, 1.5, 3.5, 3.7,
  4.0, 4.9, 5.5, 26 and 39.8 s (`--frames`, 10:31 EEST) inspected for
  the layout: the three title lines at y 190 to 314 clear of the panel
  labels at 372, both sticks with the ball on the dashed release level,
  the tip's arc, the clock and the readouts on the right, the ghost ball
  with its bracket and "still 11 cm up", the ghost stick with "tip still
  28 cm up", the "first" flags, the five-line card from y 1592; one
  layout fix after the smoke frames: the ball gap widened from 6 to 12
  px and the ghost-stick bracket moved 4 px right so the flat stick's
  tip cap and the bracket no longer touch
- layout: overlay at y 96 (captions.py), title at 190/252/314 (56 px),
  panels from y 336 to 1436 (tables at y 836 and 1386, 400 px per metre,
  hinge at x 100, ball centre at x 533), captions at caption_y 0.75 (y
  1440 to about 1520), card at y 1592 to 1816
- compose: `scripts/compose.sh hingedstick` wrote
  `media/hingedstick/final.mp4` at 10:34 EEST (h264 1080x1920 60 fps,
  aac 22050 Hz mono, 40.000 s; music seed 73 at gain 0.18; captions at
  caption_y 0.75, 38 drawtext filters); loudness mean -17.1 dB, peak
  -0.0 dB; preview and 8x5 contact sheet written
  (`media/hingedstick/compose.log`)

### Local QA

- one pass (10:35 EEST): frames at 0.02, 1.5, 3.5, 4.9, 10.3, 16.9,
  20.7, 24.2, 27.0, 29.0, 31.9, 33.0 and 39.95 s extracted from
  final.mp4 (`media/hingedstick/frame-*.png`) and inspected with the
  contact sheet: 0.02 s shows the overlay at y 96, the title "Let go of
  a stick / and a ball together. / Which hits the table first?" clear
  of the panel labels, both sticks propped with the balls on the release
  level and every readout at 0 (the thumbnail); 1.5 s shows the title
  still up, both drops 0.090 s in, "tip 45 cm up / ball 46 cm up" and
  "tip 85 cm up / ball 83 cm up" under "A stick and a ball,"; 3.5 s
  shows the 30 degree stick flat with the landing ring, "first", the
  ghost ball with "still 11 cm up", "stick flat 0.281 s" and "ball 9 cm
  up", while the 60 degree stick is still 65 cm up, under "Which hits
  the table"; 4.9 s shows the 60 degree ball landed with its ring and
  "first", the ghost stick with "tip still 28 cm up", "ball lands 0.420
  s" and "tip 24 cm up", the top panel stopped at 0.319 s, under "The
  stick is hinged"; 10.3 s and 16.9 s show the second and third drops
  with the top stick flat first under "Both drop at once," and "ball,
  and the stick"; 20.7 s shows the fourth release 0.010 s in under "Its
  tip starts down"; 24.2 s shows the card fading in with the top stick
  flagged first under "table first?"; 27.0 s shows the reset (0.000 s)
  with the card's "0.28 s" under "zero point two eight"; 29.0 s the
  fifth drop mid-fall under "The ball is still"; 31.9 s the 60 degree
  ball flagged first with the ghost stick under "the ball."; 33.0 s both
  down under "The tip is still"; 39.95 s the crossfade to the title
  frame; captions match the narration word for word and sit in the y
  1440 to 1520 band with the tables ending at y 1396 and the card from
  1592; no text clips at the frame edges; the payoff numbers are on
  screen when spoken (the card from 23.6 s, the ghost labels at 30.08
  and 31.47 s); the winner is flagged in each panel; the loop closes;
  approved with no re-render

### Metadata

- `projects/hingedstick/metadata.json`: title "Let go of a stick and a
  ball. Which hits the table first? At 30 degrees the stick, ball 11 cm
  up." (97 characters); description with the setup, a Measured list
  (the accelerations in g and the 35.26 degree threshold, both panels'
  landing times against the closed forms, the heights at the winner's
  landing, the tip speeds, the 45 degree case, the crossover angle, the
  cup variant, the half-step check), a Why paragraph (the stick turns as
  one piece, the middle falls slower than g because the hinge carries
  part of the weight, the tip is twice as far out so it moves twice as
  fast as the middle, 1.5 g cos^2 near flat; propped steep the twist is
  small at the start), the rerun line and the AI-made line; 10 tags
  (hinged stick, falling stick, faster than gravity, Galileo, free fall,
  rotation, physics demo, physics, simulation, shorts); category 27;
  private; containsSyntheticMedia true; selfDeclaredMadeForKids false
- not uploaded; task left open for the orchestrator's review and upload

### Release

- orchestrator review (10:48 EEST): the task evidence, the 8x5
  contact sheet and the full-resolution frames at 0.02, 24.2, 29.0, 33.0
  and 39.95 s inspected: the question over the two propped sticks with
  the balls on the dashed release level on the first frame; the 30
  degree stick flat and flagged "first" with the ghost ball "still 11 cm
  up", "stick flat 0.281 s / ball lands 0.319 s", while the 60 degree
  stick is mid-fall at 24.2 s; the card "which hits the table first? /
  30 degrees: the stick, at 0.28 s / with the ball still 11 cm up / 60
  degrees: the ball, at 0.42 s / with the tip still 28 cm up" under "The
  ball is still" at 29.0 s; the 60 degree ball flagged "first" with the
  ghost stick "tip still 28 cm up" at 33.0 s; the crossfade at 39.95 s;
  every caption in the clear band, no clipping; final.mp4 h264
  1080x1920 60 fps, 2,400 frames, aac 22050 Hz mono, 40.000 s, moov
  before mdat, md5 84be77922b2b414692191bd27d5543e6; title 97
  characters; approved for release
- quota check: clock 2026-09-20T10:48:02+03:00; two upload attempts (piblocks, 10:46:28,
  published as OsyugHAfCH4 at 10:46:55; looptrack, 10:47:10, uploaded
  private as Mm_gJO6VKsc, gate running) recorded since the 2026-09-20
  10:00 EEST boundary (log entries and media/*/upload.log both checked);
  this is insert attempt 3 of the hard cap of 5
- attempt 3 recorded at 2026-09-20T10:48:02+03:00, video name hingedstick, before running
  `scripts/yt-upload.py hingedstick`

### Published

- upload: `scripts/yt-upload.py hingedstick` ran 10:48:02 to 10:48:07
  EEST, token verified to see only the Seed Zero channel, video id
  XLqgiglIcqo, private (`media/hingedstick/upload.log`)
- gate: `scripts/yt-qa.py hingedstick XLqgiglIcqo --wait --publish` ran
  in the foreground from 10:48:22 EEST: processing succeeded and the 10
  tags read back, 15 of 15 pass (processed, succeeded, hd, 1080x1920,
  title, description, tags as a set, category 27, not for kids, PT41S
  for the 40.000 s file, private); containsSyntheticMedia reads absent
  as on every earlier upload (`media/hingedstick/publish.log`)
- publish: the same run set the video public at 2026-09-20T10:48:58+03:00;
  the re-read after 15 s shows privacyStatus public, madeForKids false,
  embeddable true; public at https://youtu.be/XLqgiglIcqo
- slot resolution: published for the 2026-09-20 quota day

### Quota

- attempt 3 of the hard cap of 5 for the quota day that began
  2026-09-20T10:00 EEST; cost 1 + 1,600 + 54 = 1,655 units (the
  channels.list verification inside yt-upload.py, the insert, the gate
  run's reads, update and re-read as printed by yt-qa.py); day total
  after three attempts 4,962 units, target of three met

### Repository

- committed as e13d192 "Publish the day twenty-two slate" (sims,
  projects, tasks, docs/niche.md, web/data; no media, previews or
  secrets) and pushed to origin/master at 2026-09-20 10:50 EEST
