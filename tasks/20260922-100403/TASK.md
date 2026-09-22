# Produce short: Lifeguard path, the straight line beside the least-time path

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day24

## Goal

Backlog idea (trend research 2026-09-20, task 20260920-100347, pillar 4
algorithms in motion, with the optics link):
"Lifeguard path: a lifeguard 20 m up the beach, a swimmer 40 m along and
20 m out, running 5 m/s and swimming 1.25 m/s; the straight line beside
the least-time path; measure the arrival times; expect 28.3 s against
24.5 s (enter the water 35.5 m along, not 20; Snell's law, sin a / v
equal on both sides; run-then-swim 24.9 s); the race repeats so the
short loops; deterministic, no seed."
Day twenty-four, third slot. Chosen because path races on the same start
and end are a proven format (brachistochrone 948 views, A-star maze 978)
and the race plays in real time inside a 40 s short: both rescuers leave
at once and the bent path arrives first. Question in the first two
seconds: "Straight to the swimmer, or run farther first?" (or the
producer's better wording, kept identical in the title, the hook and the
payoff).

## Claim

A lifeguard twenty meters up the beach who runs at five meters a second
and swims at one and a quarter reaches a swimmer forty meters along and
twenty meters out in twenty-eight point three seconds on the straight
line, and in twenty-four point five seconds by running farther along the
sand and entering the water near the swimmer: the bent path wins by
nearly four seconds. Every number in the narration is printed by the sim
before the script is written.

## Evidence

### Measurements

(recorded after the measure-only run, before scripting)

`sims/lifeguard/lifeguard.py --measure-only` with
`projects/lifeguard/manifest.json` (a straight waterline, sand on one
side and water on the other; the lifeguard chair d = 20 m up the beach
from the waterline, the swimmer a = 40 m along the shore and b = 20 m
out in the water; running speed 5 m/s on sand, swimming speed 1.25 m/s
in water, 4 x slower, both constant, no acceleration; two rescuers
leave the chair at the same instant, one on the straight line and one
on the least-time path; both are points advanced by exact arc length
per frame at 60 fps and checked against the closed forms; played in
real time, one run per video; drawn at 21 px per metre (840 px along
the shore, 840 px across, inside a 1,000 by 930 px field with 5.7 m of
margin each side and 2.1 m above and below; 25 px per metre would have
put the chair 40 px from the frame edge); deterministic, no seed; run
at 10:16:54 EEST, log in `media/lifeguard/measure.log`):

- straight line (chair to swimmer, crosses the waterline at x = a d /
  (d + b) = 20.0000 m along): 28.2843 m of sand in 5.6569 s plus
  28.2843 m of water in 22.6274 s = 28.2843 s over 56.5685 m; 45.00 deg
  from the shore normal on both legs; sin(alpha)/vr = 0.14142 against
  sin(beta)/vs = 0.56569, not equal, so not the least-time path
- least-time path (golden-section search of T(x) = sqrt(20^2 + x^2)/5
  + sqrt(20^2 + (40 - x)^2)/1.25 on [0, 40] m, 51 iterations, bracket
  1e-9 m): enter the water at x* = 35.5355 m along (4.4645 m short of
  the swimmer); 40.7771 m of sand in 8.1554 s plus 20.4922 m of water
  in 16.3938 s = 24.5492 s over 61.2693 m (4.7008 m longer than the
  straight line); dT/dx at x* = 4.5e-9 s/m; Snell check sin(alpha)/vr =
  0.17429 = sin(beta)/vs = 0.17429 (difference 4.5e-9); alpha = 60.63
  deg, beta = 12.58 deg; sin(alpha)/sin(beta) = 4.0000 = vr/vs
- gap: the bent path wins by 3.7351 s (13.21 percent of the straight
  time); the bent rescuer runs 2.4986 s longer and swims 6.2336 s less
  than the straight one
- run-then-swim (x = 40 m, run level with the swimmer then swim straight
  out): 44.7214 m of sand in 8.9443 s plus 20.0000 m of water in
  16.0000 s = 24.9443 s, 0.3951 s slower than the least-time path
- table T(x): x = 0 m 39.777 s; 10 m 33.317 s; 20 m 28.284 s; 30 m
  25.100 s; 35.5 m 24.549 s; 40 m 24.944 s
- stepper checks (2,400 frames at 60 fps, exact arc length per frame
  from release_at 0.8 s, the crossing frame split at the exact crossing
  time): straight enters the water at 5.656854249 s (closed form the
  same, diff 4.0e-14) and arrives at 28.284271247 s (diff 6.4e-14), max
  |s - closed form| 6.7e-13 m; bent enters at 8.155414879 s (diff
  3.6e-14) and arrives at 24.549208963 s (diff 1.8e-13), max 7.5e-13 m
- schedule printed by the sim (real time, one run, release at 0.8 s):
  the straight rescuer enters the water at 6.46 s, the bent one at 8.96
  s, the bent one arrives at 25.35 s, the straight one at 29.08 s, hold
  to 39.50 s, loop fade 39.50 to 40.00 s; title until 2.4 s; card from
  25 s in the first manifest, to be set from the voice timing
- text widths (DejaVuSans-Bold): overlay 875 px at 34 (the first draft
  "same start, same swimmer | run 5 m/s, swim 1.25 m/s | real time | no
  seed" was 1,429 px and the "same swimmer" / "same start" variants
  1,118 to 1,167 px, all shortened before any render); title lines 786
  and 616 px at 56; column labels 221 and 176 px at 32; clock "t 28.3
  s" 271 px and the frozen "28.3 s" 218 px at 64 ("arrived 24.5 s" at
  64 would be 500 px, the full column width, so "arrived" is a 32 px
  tag of 130 px beside the frozen clock); sub-readouts 387 px at 28;
  entry labels 78 and 108 px, "swimmer" 143, "water" 91, "sand" 76 at
  28, "chair" 73 at 26, scale "10 m" 67 at 24; payoff lines 557, 440,
  522 and 443 px at 40; nothing over 950 px

Narration numbers: the lifeguard runs four times faster than she swims
(setup; 5 / 1.25 = 4); twenty four point five seconds on the bent path
against twenty eight point three on the straight line (payoff; the
measured 24.5492 and 28.2843, shown as 24.5 and 28.3 on the clocks and
the card). The entry points, the sand and water splits, the 3.7 s gap,
the run-then-swim 24.9 s, the table, the Snell angles and the stepper
checks go to the description. No number contradicted the claim.

### Production

- layout (`sims/lifeguard/lifeguard.py`): overlay at y 96, title at y
  190/252, one top-down field from y 350 to 1280 (x 40 to 1040) at 21
  px per metre with the waterline at y 815, water (dark blue) above and
  sand (warm dark) below, a foam line and a fainter wet-sand line, faint
  ripple dashes on five rows, distance ticks every 10 m on the
  waterline, a 10 m scale bar and "water" label top left, "sand" bottom
  right; the chair at (0, -20) m (x 120, y 1235) as a white square with
  "chair" under it; the swimmer at (40, 20) m (x 960, y 395) as a coral
  dot in a 24 px coral ring with "swimmer" to its left; both full
  routes chair -> entry -> swimmer as thin dashed lines in the path
  colour (teal for the straight line, gold for the bent path) at alpha
  0.6, the covered part drawn solid 4 px as each rescuer advances;
  entry ticks and labels "20 m" and "35.5 m" on the waterline; the
  rescuers as 10 px dots with a ring (the straight rescuer's ring 21
  px, the bent's 16 px, so both show when they coincide) and a 0.6 s
  expanding ring flash at each arrival; a two-column readout row from y
  1296 (columns at x 80 and 580): the label at 32 px in the path
  colour, the live clock "t 12.3 s" at 64 px, and "sand 5.7 s / water
  22.6 s" at 28 px (the water part appears at the entry); at arrival
  the clock freezes at "24.5 s" (gold for the winner, plain for the
  straight line) with a 32 px "arrived" tag beside it; captions at
  caption_y 0.75; the four-line card from y 1592; geometry drawn at 2x
  and reduced; the straight line is the left column because its entry
  (20 m) is left of the bent entry (35.5 m) on the field
- whisper pre-test (10:18:24 EEST, before scripting, no numbers;
  `media/lifeguard/hooks/`): three hook variants and one mechanism
  sentence group round-tripped through `scripts/voiceover.sh`: "A
  swimmer in trouble. Straight to the swimmer, or run farther first?"
  (3.63 s, passed), "Straight to the swimmer, or run farther first? A
  lifeguard on the sand, a swimmer out in the water." (5.19 s, passed,
  the sentence-initial "Straight" not clipped) and "A swimmer needs
  help. Straight to the swimmer, or run farther first?" (3.59 s,
  passed), plus "The straight line hits the water early and crawls the
  long way at swimming speed. The bent path keeps sprinting on the
  sand, then swims a shorter stretch. Less water means less crawling.
  The longer run costs less than the water it saves." (12.49 s,
  passed); "straight" (the 2026-09-13 "stray" risk) passed in all four
- smoke frames (`--frames`, pass 1 at 10:20:39 EEST, at 0, 1.5, 6.46,
  8.96, 25.35, 29.08, 33 and 39.8 s): three defects: both dots stacked
  at the chair hid the teal rescuer on the first frame (the thumbnail)
  and at the swimmer after both arrivals; the coral swimmer marker (a
  15 px ring) vanished under the arriving dot; the dashed routes at
  alpha 0.5 read faint on the water; fixes: the straight rescuer's ring
  21 px against the bent's 16 px, the swimmer ring 24 px with the label
  moved 8 px left, dashes at alpha 0.6; smoke pass 2 at 10:21:54 EEST
  (0, 25.35 and 33 s) clean: the teal ring shows outside the gold at
  the chair, the gold dot sits inside the coral ring at the bent
  arrival, the coral, teal and gold rings nest at the swimmer in the
  hold; nothing clips, nothing enters the caption band
- narration (written after the measure-only run, 10:19 EEST): the first
  hook kept ("A swimmer in trouble." is a noun phrase, so no clipped
  verb onset, and it puts the question at 1.76 s); the question-first
  variant dropped because the setup after the question delays the
  story and leaves "Straight" at the clipped-onset position; "A swimmer
  needs help" dropped as weaker than "in trouble";
  `projects/lifeguard/narration.txt`, 108 words; the rescuers named by
  their paths ("the straight line", "the bent path"), matching the
  column labels, instead of by colour; the setup number as "four times
  faster" ("Each runs four times" is exactly 20 characters, one chunk);
  "twenty four point five seconds" cannot fit one 20-character chunk
  (22 characters for the number alone), so the sentences are built for
  the readable split, "Only twenty four | point five seconds." and
  "takes twenty eight | point three seconds.", checked with chunks()
  before recording; "still", "pull", "got" and "spread" avoided; no
  possessives or apostrophes; "together" instead of "at once"; the
  narration order (bent then straight) follows the arrival order on
  screen
- voice: `scripts/voiceover.sh projects/lifeguard/narration.txt` pass 1
  at 10:20:12 EEST passed, "ok: transcript matches narration": 108
  words, 34.02 s, ends at 34.62 s of the 40 s video, 3.17 words/s; log
  in `media/lifeguard/voice.log`
- timing (`scripts/voice-timing.py`, +0.6 s offset, log in
  `media/lifeguard/timing.log`): "A swimmer in trouble." 0.60 to 1.76
  s; "straight to the swimmer," 1.76 to 2.97 (the question starts at
  1.76 s, inside the title's 2.4 s); "or run farther first. Two
  lifeguards leave the chair together." 2.97 to 6.39; "One takes the
  straight line. The other runs farther along the sand. Each runs four
  times faster than she swims. The straight line hits the water early."
  6.39 to 14.73 with the straight entry at 6.46 s and the bent entry at
  8.96 s; "and crawls the long way at swimming speed." 14.73 to 17.18;
  "The bent path keeps sprinting on the sand." 17.18 to 19.39; "then
  swims a shorter stretch. The longer run costs less than the water it
  saves." 19.39 to 23.73; "The bent path arrives first." 23.73 to 25.64
  with the bent arrival at 25.35 s on "first"; "Only 24.5 seconds."
  25.64 to 27.79 with the gold clock frozen from 25.35 s and the card
  fully lit from 25.6 s; "The straight line takes 28.3 seconds. So,
  straight to the swimmer," 27.79 to 31.92 with the straight arrival at
  29.08 s on "twenty eight point three"; "Or run farther first." 31.92
  to 33.28; "Run farther first." 33.28 to 34.62 (the sentence-initial
  "Run" transcribed correctly); the hold (34.6 to 39.5 s) and the loop
  fade play under the card with no narration
- schedule decisions: release_at 0.8 s (both rescuers at the chair
  under the title on the first frame; 0.8 rather than 0.5 so the bent
  arrival, 25.35 s, lands on "first" of "arrives first" (23.73 to
  25.64) and the straight arrival, 29.08 s, on "twenty eight point
  three"); payoff_t 25.0 s from the timing, so the card is fully lit at
  25.6 s, before the first payoff number at 25.64 s and 0.25 s after
  the bent arrival; the card names the straight time 3.5 s before the
  straight rescuer arrives, which the brief allows ("may light when the
  bent path arrives")
- footage: `sims/lifeguard/lifeguard.py` (no arguments) wrote
  `media/lifeguard/footage.mp4`, 40.00 s at 60 fps, 2,400 frames, h264
  crf 16 yuv420p, in 30 s with eight forked workers, 10:22:28 to
  10:22:58 EEST; the same run re-printed every measurement above
  (`media/lifeguard/render.log`); loop check on the raw frames: the
  last frame differs from the first in 0 px
- compose: `scripts/compose.sh lifeguard` wrote
  `media/lifeguard/final.mp4` at 10:23:08 EEST (h264 1080x1920 60 fps,
  2,400 frames, aac 22050 Hz mono, 40.000 s, 2,567,330 bytes; music
  seed 76 at gain 0.18; captions at caption_y 0.75, 39 drawtext
  filters, the overlay plus 38 caption chunks); loudness mean -15.9 dB,
  peak -0.0 dB; preview (40.07 s) and 8x5 contact sheet written
  (`media/lifeguard/compose.log`)

### Local QA

- smoke pass 1 (10:20:39 EEST, `--frames` before any render): three
  layout defects found and fixed (the stacked dots, the hidden swimmer
  marker, the faint dashes; see Production); smoke pass 2 (10:21:54
  EEST) clean before the footage render
- final pass (10:24 EEST): frames at 0.02, 1.5, 6.46, 8.96, 25.35, 26.5,
  29.08, 30.5, 33.5 and 39.95 s extracted from final.mp4
  (`media/lifeguard/frame-*.png`) and inspected with the 8x5 contact
  sheet (`media/lifeguard/sheet.png`): 0.02 s shows the overlay "run 5
  m/s, swim 1.25 m/s | real time | no seed" at y 96, the title
  "Straight to the swimmer, / or run farther first?" at y 190 and 252
  clear of it and of the field, both rescuers at the chair (the teal
  ring outside the gold), the dashed routes, the entry labels, the
  swimmer, the clocks "t 0.0 s" (the thumbnail); 1.5 s shows both dots
  3.5 m from the chair with their solid segments under "A swimmer in";
  6.46 s shows the straight rescuer on the 20 m tick with "sand 5.7 s /
  water 0.0 s" under "One takes the"; 8.96 s shows the bent rescuer on
  the 35.5 m tick with "sand 8.2 s / water 0.0 s" while the straight
  one is 3 m out at "water 2.5 s", under "farther along the"; 25.35 s
  shows the bent arrival, the gold dot inside the coral swimmer ring,
  the gold clock "24.5 s arrived", the straight clock "t 24.6 s" with
  the teal dot 4.5 m short, the card fading in, under "The bent path";
  26.5 s shows "Only twenty four" with the card lit and the gold clock
  frozen; 29.08 s shows the straight rescuer one frame before arrival
  at "t 28.3 s" with the teal ring nested inside the coral ring, under
  "takes twenty eight"; 30.5 s shows "28.3 s arrived" in plain text
  beside the gold "24.5 s arrived", the three rings nested, under
  "point three seconds."; 33.5 s shows the hold under "farther first?";
  39.95 s shows the crossfade to the title frame with the card, the
  "arrived" tags and the solid routes fading out; captions match the
  narration word for word (the contact sheet reads every chunk in
  order) and sit in the y 1440 to 1520 band with the lowest readout
  text ending at y 1432 and the card from 1592; the widest text (the
  overlay, 875 px) is centred with 102 px margins and nothing clips at
  the frame edges; the payoff numbers are on screen when spoken (the
  gold 24.5 s clock from 25.35 s and the card from 25.6 s against "Only
  24.5 seconds" at 25.64 s; "28.3 s" on the card from 25.6 s and the
  frozen clock from 29.08 s against "takes 28.3 seconds" from 27.79 s);
  the loop closes: the raw last frame differs from the raw first frame
  in 0 px (render.log), and on the encoded final frame 2399 differs
  from frame 0 in 4,804 px by more than 24 levels (0.23 percent, at
  text edges, max channel difference 81, mean 0.49, encoder noise: the
  footage's own encoded first and last frames differ in 1,147 px);
  ffprobe: h264 1080x1920, 60/1 fps, 2,400 frames (also by decode), aac
  22050 Hz mono, 40.000000 s, atoms ftyp, moov, free, mdat (moov before
  mdat), md5 dd9f66304e1f5f4bf3cbf68cb1dcec97; approved locally

### Metadata

- `projects/lifeguard/metadata.json`: title "Straight to the swimmer,
  or run farther first? Run farther first: 24.5 s. Straight line: 28.3
  s" (95 characters); description with the setup (the chair 20 m up the
  beach, the swimmer 40 m along and 20 m out, 5 m/s on sand and 1.25
  m/s in water, the straight line entering at 20 m, the least-time path
  from the golden-section minimum of T(x), the per-frame stepper, real
  time, no seed), a Measured list (both paths' entry points, sand and
  water splits and totals, the 3.74 s gap, run-then-swim 24.94 s, the
  T(x) table, the Snell angles 60.63 and 12.58 deg with sin/v = 0.1743
  on both sides, the stepper agreement), a Why paragraph in plain words
  (a metre of water costs four times a metre of sand; the bent path
  trades 2.5 s more running for 6.2 s less swimming until the extra
  sand costs as much as the water it saves; that balance is Snell's
  law, and light bends at a surface for the same reason, the path of
  least time), the rerun line and the AI-made line; 10 tags (lifeguard
  problem, Snell's law, Fermat's principle, least time path,
  refraction, optimization, physics, physics visualization, simulation,
  shorts); category 27; private; containsSyntheticMedia true;
  selfDeclaredMadeForKids false; the same keys in the same order as
  projects/tetherball/metadata.json
- not uploaded; task left open for the orchestrator's review and upload

### Release

- orchestrator review (10:32 EEST): the task evidence, the 8x5 contact
  sheet and the full-resolution frames at 0.02, 25.35, 30.5 and 39.95 s
  inspected: the question "Straight to the swimmer, / or run farther
  first?" over the beach with both rescuers at the chair, the two dashed
  routes, the entry marks "20 m" and "35.5 m" and the swimmer top right
  on the first frame; 25.35 s shows the bent rescuer inside the swimmer
  ring with "24.5 s arrived" in gold while the straight one is at t 24.6
  s in the water, the card fading in under "The bent path"; 30.5 s
  shows both arrived, "28.3 s arrived" and "24.5 s arrived", under
  "point three seconds." with the card "straight to the swimmer, / or
  run farther first? / run farther first: 24.5 s / straight line: 28.3
  s"; 39.95 s shows the crossfade to the title frame; the card naming
  the straight line's 28.3 s from 25.0 s, four seconds before that
  rescuer arrives, accepted as in the tetherball short (its card named
  both speeds before the second half-string moment); every caption in
  the clear band, no clipping; final.mp4 h264 1080x1920 60 fps, 2,400
  frames, aac 22050 Hz mono, 40.000 s, moov before mdat, md5
  dd9f66304e1f5f4bf3cbf68cb1dcec97; title 95 characters; approved for
  release
- quota check: clock 2026-09-22T10:35:16+03:00; two upload attempts (bounceslope, 10:32:36,
  published as hlBy6yci8_U at 10:33:10; braking, 10:33:53, published as
  faJeNRiCo5Y at 10:34:38) recorded since the 2026-09-22 10:00 EEST
  boundary (log entries and media/*/upload.log both checked); this is
  insert attempt 3 of the hard cap of 5
- attempt 3 recorded at 2026-09-22T10:35:16+03:00, video name lifeguard, before running
  `scripts/yt-upload.py lifeguard`

### Published

- upload: `scripts/yt-upload.py lifeguard` ran 10:35:16 to 10:35:21 EEST,
  token verified to see only the Seed Zero channel, video id
  Vd3AJDhZgiM, private (`media/lifeguard/upload.log`)
- gate: `scripts/yt-qa.py lifeguard Vd3AJDhZgiM --wait --publish` ran in
  the foreground from 10:35:27 EEST: processing succeeded and the 10 tags
  read back on the first poll, 15 of 15 pass (processed, succeeded, hd,
  1080x1920, title, description, tags as a set, category 27, not for
  kids, PT41S for the 40.000 s file, private); containsSyntheticMedia
  reads absent as on every earlier upload (`media/lifeguard/publish.log`)
- publish: the same run set the video public at 2026-09-22T10:36:00+03:00;
  the re-read after 15 s shows privacyStatus public, madeForKids false,
  embeddable true; public at https://youtu.be/Vd3AJDhZgiM
- slot resolution: published for the 2026-09-22 quota day

### Quota

- attempt 3 of the hard cap of 5 for the quota day that began
  2026-09-22T10:00 EEST; cost 1 + 1,600 + 54 = 1,655 units (the
  channels.list verification inside yt-upload.py, the insert, the gate
  run's reads, update and re-read as printed by yt-qa.py); day total
  after three attempts 4,964 units
