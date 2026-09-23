# Produce short: Spring pendulum swap, tuned beside detuned on the same bounce

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day25

## Goal

Backlog idea (trend research 2026-09-20, task 20260920-100347, pillar 2
chaos and physics, oscillators):
"Spring pendulum swap: a bob on a spring stretched to 1 m, bouncing 10
cm straight up and down with a 0.1 degree tilt, the spring tuned to two
bounces per swing (k/m = 4 g/l) beside the same bob on a spring tuned to
1.5; measure the largest sideways swing in a minute; expect the tuned
bob to start swinging on its own, past 5 degrees at 18.6 s and 11.4
degrees at 23.8 s while its bounce shrinks to 3 cm, and the detuned bob
to stay under 0.3 degrees; RK4; the swing size depends on the tilt and
bounce chosen, so the sim sets the claim; deterministic, no seed."
Research feasibility numbers (task 20260920-100347): stretched length 1
m (swing period 2.006 s), k/m = 4 g/l = 39.23 s^-2 (bounce period 1.003
s), 10 cm bounce, 0.1 degree tilt, RK4 at 1 ms: the swing passes 1
degree at 11.59 s, 5 degrees at 18.63 s and peaks at 11.37 degrees at
23.82 s while the bounce falls to 3.09 cm; half step gives the same;
tuned to 1.5 or 1.8 bounces per swing the swing never passes 0.25
degrees in 60 s.
Day twenty-five, first slot. Chosen because it is a two-panel oscillator
on the same input (same bob, same 10 cm bounce, same tilt, only the
spring differs) with continuous motion and a plain question, the format
of the channel's best shorts (coupled pendulum swap 1,046 views, hoop
bead 925, big swing 973, turntable 973), and because the bounce turning
into a swing by itself is a visible surprise. Question in the first two
seconds: "Bounce it straight up and down. Does it start to swing?" (or
the producer's better wording, kept identical in the title, the hook and
the payoff).

## Claim

A bob on a spring stretched to one meter, set bouncing ten centimeters
up and down with a tenth of a degree of tilt, starts swinging on its own
when the spring is tuned to two bounces per swing: past five degrees at
eighteen point six seconds and about eleven degrees at twenty-four
seconds, while its bounce almost stops (the bob's vertical travel is
down to about two centimeters either way at the swing peak and under
one centimeter a second later; changed from "shrinks to three
centimeters" after the measure-only run, see Measurements); the same bob on
a spring tuned to one and a half bounces per swing never passes a
quarter of a degree. Every number in the narration is printed by the sim
before the script is written.

## Evidence

### Measurements

(recorded after the measure-only run, before scripting)

`sims/springswap/springswap.py --measure-only` with
`projects/springswap/manifest.json` (a point bob on a light spring from
a fixed pivot, stretched equilibrium length l = 1 m; the bob pulled 10
cm below the equilibrium with a 0.1 degree tilt from vertical and
released at rest; two panels share every input and only the spring
differs: left k/m = 4 g/l = 39.2266 s^-2, natural length 0.7500 m, two
bounces per swing; right k/m = 2.25 g/l = 22.0650 s^-2, natural length
0.5556 m, 1.5 bounces per swing; full two-degree-of-freedom polar
equations r'' = r theta'^2 + g cos theta - (k/m)(r - l0), theta'' =
-(2 r' theta' + g sin theta) / r, no small-angle approximation, no
damping; RK4 at 1,200 steps/s (0.83 ms, 20 steps per frame) with the
half-step check at 2,400; measured over 60 s, scene 40 s at 60 fps,
2,400 frames, real time; drawn at 700 px per metre; deterministic, no
seed; first run 10:22:29 EEST, re-run 10:25:17 after the readout-window
and text-width fixes below, log in `media/springswap/measure.log`):

- periods: swing 2.0064 s by the closed form 2 pi sqrt(l/g); from the
  zero crossings of theta the tuned panel gives 1.9594 s over the first
  10 s (9 intervals, the tiny swing is being pulled into step by the
  drive) and 2.0055 s between 10 and 20 s (10 intervals), the detuned
  panel 2.0164 s and 2.0287 s; bounce 1.0032 s tuned and 1.3376 s
  detuned from the zero crossings of r' (18 and 13 intervals in 10 s),
  the same as the closed forms 2 pi sqrt(m/k); ratios 2.0000 and 1.5000
  bounces per swing by the closed forms
- tuned (2 bounces a swing): the swing angle first passes 1 degree at
  11.59 s and 5 degrees at 18.63 s; peak swing within 40 s 11.37
  degrees at 23.82 s, which is also the peak within 60 s (largest angle
  over 60 s 11.373 degrees); the same numbers as the research
  feasibility run (11.59, 18.63, 11.37 at 23.82)
- tuned, bounce at the swing peak: half the range over one bounce
  period centred on 23.82 s is 1.26 cm radial (r - l) and 1.30 cm
  vertical (r cos theta); the research figure of 3.09 cm is the largest
  stretch |r - l| in the swing period around the peak (the r extremum
  at 23.05 s, +3.09 cm); the successive r extrema run +7.71 (20.06 s),
  -6.93, +6.56, -5.51, +5.02, -3.68, +3.09 (23.05 s), -1.54, +0.97
  (23.98 s), +0.09 (24.32 s), +1.03 (24.67 s), -1.61, +3.15, -3.74,
  +5.07 cm, so the bounce nearly vanishes for a second around the peak
  (scratch check `/tmp/springswap/check.py`); the on-screen bounce
  readout (half the vertical range over the last bounce period) reads
  8.89 cm at 18.63 s, 6.09 at 22 s, 4.39 at 23 s, 2.33 at 23.82 s, 1.30
  at 24.5 s, 0.85 cm at its minimum at 24.83 s, 1.31 at 25 s, 3.26 at
  26 s, 4.98 at 27 s, 6.30 at 28 s, 8.29 at 30 s, 9.83 at 35 s and 9.98
  cm at 39.5 s; the swing readout (largest |theta| over the last swing
  period) reads 5.05 deg at 18.63 s, 11.37 from 23.82 to 25.5 s, 10.76
  at 27 s, 7.48 at 30 s, 2.77 at 35 s, 0.95 at 39.5 s and 0.84 deg at
  the scene end 39.98 s with the bounce back to 9.98 cm: the swap runs
  backwards and the scene ends almost where it began
- detuned (1.5 bounces a swing): the swing never passes 1 degree in 60
  s (so never 5); peak within 40 s 0.14 degrees at 2.01 s and within 60
  s 0.141 degrees at 59.52 s (largest angle over 60 s 0.141 degrees,
  under the quarter degree of the claim); bounce 10.00 cm radial and
  vertical throughout; readouts swing 0.14 deg and bounce 10.00 cm at
  the scene end
- half-step check at 2,400 steps/s: tuned 5 degrees at 18.6281 s (diff
  2.2e-7 s), peak 11.3727 degrees at 23.8226 s against 11.3727 at
  23.8226 (diffs 2.0e-10 degrees, 1.9e-8 s); detuned never 5 degrees,
  peak 0.1415 degrees at 59.5159 s on both step sizes (diffs 1.1e-12
  degrees, 4.9e-9 s)
- energy drift over 60 s: tuned max |E - E0| 3.41e-12 J/kg (1.74e-9
  percent of the 0.1961 J/kg bounce energy, E0 -8.384669 J/kg); detuned
  4.09e-13 J/kg (3.71e-10 percent of 0.1103 J/kg)
- geometry: the lowest bob edge is y = 1,200 px in both panels (the
  readout row starts at 1,290); the tuned bob's largest sideways reach
  139 px of the 270 px panel half-width, the detuned 2 px; r ranges
  0.9000 to 1.1000 m in both panels over the scene
- schedule printed by the sim (real time, one run from release at 0 s):
  tuned swing past 1 degree at 11.59 s, 5 degrees at 18.63 s, peak
  23.82 s; loop fade 39.50 to 40.00 s; title until 2.4 s; card from
  24 s in the first manifest, set to 23.2 s from the voice timing
- text widths (DejaVuSans-Bold): overlay 858 px at 34 (the first draft
  "same bob, same 10 cm bounce | real time | no seed" was 985 px and
  was shortened to "same bob, same bounce | real time | no seed" before
  any render); title lines 745 and 714 px at 56; panel labels 374 and
  413 px at 36; readouts "swing 11.4 deg" 343 px at 40 and "bounce 10.0
  cm" 320 px at 36; clock 109 px at 32; payoff lines 530, 506, 749 and
  771 px at 40 (the first draft of line 4, "1.5 bounces a swing: no,
  0.14 deg at most", was 957 px and lost "at most"); nothing over 950
  px

Narration numbers: ten centimeters up, ten down (setup; the 10 cm
release amplitude, readout "bounce 10.0 cm"); two bounces a swing and
one point five (the panel tunings, on the labels); a tenth of a degree
off straight (the 0.1 degree tilt); for ten seconds, nothing (the swing
is under 1 degree until 11.59 s); it leans eleven point four degrees
(payoff, the measured 11.37 degree peak at 23.82 s, shown as 11.4 on the
readout and the card); the bounce fades until it almost stops (the
readout falls to 0.85 cm at 24.83 s, no number narrated); the right bob
a quarter degree at most (payoff, the measured 0.141 degree maximum in
60 s, shown as 0.14 on the card). The crossing times, the periods, the
3.09 cm stretch, the readout minimum, the half-step and energy checks
go to the description. One number contradicted the claim: the bounce at
the swing peak is not "three centimeters" by any per-period measure (it
is 1.3 cm centred on the peak, 2.3 cm on the trailing readout, and the
readout bottoms at 0.85 cm a second later; 3.09 cm is the last big
stretch before the peak), so the Claim now says the bounce almost stops
and the narration says "until it almost stops".

### Production

- layout (`sims/springswap/springswap.py`): overlay at y 96, title at y
  190/252 for 2.4 s, a muted 32 px clock at y 250 after the title (hidden
  again in the loop fade), panel labels "2 bounces a swing" (gold) and
  "1.5 bounces a swing" (teal) at y 345 over panels centred at x 270 and
  810; a 300 px top bar with a pivot dot at y 400; the spring as a
  zigzag of 14 coils (16 px amplitude, 22 px straight leads) from the
  pivot to the bob's edge, so it visibly stretches and shortens; a faint
  straight-down reference line of 700 px (1 m) from the pivot and, once
  the swing readout passes 0.3 degrees, a faint arc at 700 px spanning
  the latest swing either side of it; the bob a 30 px disc in the panel
  colour with a dark centre; readouts per panel at y 1310 ("swing 11.4
  deg", 40 px, panel colour) and 1362 ("bounce 2.3 cm", 36 px, muted);
  captions at caption_y 0.75; the four-line card from y 1592; geometry
  drawn at 2x on a layer from y 300 to 1280 and reduced; the bob's
  lowest edge 1,200 px clears the readout row
- whisper pre-test (10:25:17 to 10:25:23 EEST, before scripting;
  `media/springswap/hooks/`): three hook variants and one mechanism
  group round-tripped through `scripts/voiceover.sh`, all passed on the
  first pass: "A bob on a spring. Bounce it up and down. Does it start
  to swing?" (3.94 s), "Bounce it up and down. Does it start to swing?
  Same bob, same bounce, two springs." (5.35 s, the sentence-initial
  "Bounce" not clipped), "One bob, one spring. Bounce it up and down.
  Does it start to swing?" (4.11 s), and the mechanism group "The left
  spring is tuned to two bounces a swing, the right one to one point
  five. The release is a tenth of a degree off straight. For ten
  seconds, nothing. Then the left bob begins to swing. Each bounce lands
  in step with the swing and pushes it. The bounce fades into the swing,
  until it almost stops. It leans eleven point four degrees. The right
  bob never joins in. A quarter degree at most. Only when the spring is
  tuned." (24.40 s, 76 words, 3.11 words/s); "straight", "one point
  five", "a tenth of a degree", "a quarter degree" and "eleven point
  four" all came back right
- narration (written after the measure-only run, 10:25 EEST): the first
  hook kept (a noun phrase opens, so no clipped verb onset, and the
  question starts at 1.85 s); the question-first variant dropped because
  the setup after the question delays the story; "One bob, one spring"
  dropped as flatter; `projects/springswap/narration.txt`, 109 words;
  the panels named by their tunings ("the left is tuned to two bounces a
  swing, the right to one point five"), matching the labels; "one point
  five" rather than "one and a half" because normalize.py folds "one and
  a half" differently from a transcribed "1.5"; the setup number as "Ten
  centimeters up, ten down" (19 characters, one chunk); "eleven point
  four degrees" cannot fit one 20-character chunk, so the sentence is
  built for the readable split "It leans eleven | point four degrees.",
  and "a quarter degree" is kept whole with "A quarter degree at |
  most."; "the right to one | point five." splits at "point" like the
  lifeguard short; checked with chunks() before recording (37 chunks);
  "still", "got", "pull", "spread", "started", "they are" and "a hundred"
  avoided; no possessives or apostrophes; the narration order (left
  panel grows, bounce fades, peak, right panel never moves) follows the
  screen; the bounce is narrated as "until it almost stops" with no
  number, because the measured value depends on the window (see
  Measurements)
- voice: `scripts/voiceover.sh projects/springswap/narration.txt` pass
  1 at 10:25:57 EEST passed, "ok: transcript matches narration": 109
  words, 32.69 s, ends at 33.29 s of the 40 s video, 3.33 words/s; log
  in `media/springswap/voice.log`
- timing (`scripts/voice-timing.py`, +0.6 s offset, log in
  `media/springswap/timing.log`; the piece-level transcript heard "A
  barb on a spring" for the first 1.2 s piece, while the full-take round
  trip passed): "A bob on a spring." 0.60 to 1.85 s; "Bounce it up and
  down. Does it start to swing? Ten centimeters up." 1.85 to 5.68 (the
  question starts at 1.85 s, inside the title's 2.4 s); "ten down, on
  two springs, the left is tuned to two bounces a swing," 5.68 to 9.84;
  "the right to one point five. The release is a tenth of a degree off
  straight. For ten seconds," 9.84 to 14.88; "nothing." 14.88 to 15.50;
  "Then the left bob starts to swing." 15.50 to 17.43 with the swing
  readout at 2.4 to 3.1 degrees and the lean visible; "Each bounce lands
  in step and pushes the swing, the bounce fades, until it almost stops."
  17.43 to 22.69 with the 5 degree crossing at 18.63 s and the bounce
  readout falling from 8.9 to 4.6 cm; "It leans eleven point four
  degrees. The right bob never joins in. A quarter degree at most. So,
  bounce it up and down." 22.69 to 30.13 as one piece (no pause found),
  about 3.1 words/s, so "eleven point four" lands about 23.3 to 24.3 s
  against the peak at 23.82 s, "The right bob" about 24.6 to 26.6 s and
  "A quarter degree" about 26.6 to 28.2 s; "Does it start to swing?"
  30.13 to 31.44; "Only when the spring is tuned." 31.44 to 33.29; the
  hold (33.3 to 39.5 s, the swing handing its energy back to the bounce)
  and the loop fade play under the card with no narration
- schedule decisions: no release delay (the bob is at the bottom of its
  bounce on the first frame, under the title, with the readouts "swing
  0.1 deg" and "bounce 10.0 cm"); payoff_t 23.2 s from the timing, so
  the card fades in 23.2 to 23.8 s while "It leans eleven" is spoken and
  is fully lit at the swing peak (23.82 s), before "point four degrees"
  and 1.4 s before "The right bob never joins in"; the swing readout
  shows 11.4 from about 23.6 s
- smoke frames (`--frames`, pass 1 at 10:25:59 EEST, at 0, 1.5, 12,
  18.63, 23.82, 24.83, 27, 33 and 39.8 s): one defect: in the loop fade
  the live frame's clock "39.8 s" at y 250 ghosted through the title's
  second row (y 252) as the first frame blended in; fix: the clock is
  hidden from 39.5 s (scene end minus loop_fade); everything else clean:
  the title clear of the overlay band and the labels, the springs
  visibly stretching, the gold bob out on its arc at 23.82 s with
  "swing 11.4 deg / bounce 2.3 cm", the near-rigid swing at 24.83 s with
  "bounce 0.9 cm", the teal bob straight with "swing 0.1 deg / bounce
  10.0 cm" throughout, the card in the y 1592 to 1760 band; the earlier
  readout-window fix (the first measure run read "bounce 0.00 cm" on
  frame 0 because the trailing window was empty; the window now looks
  ahead to one period inside the first period, so frame 0 reads the
  release amplitude) was made before the smoke pass
- footage: `sims/springswap/springswap.py` (no arguments) wrote
  `media/springswap/footage.mp4`, 40.00 s at 60 fps, 2,400 frames, h264
  crf 16 yuv420p, in 32 s with eight forked workers, 10:27:15 to
  10:27:47 EEST; the same run re-printed every measurement above
  (`media/springswap/render.log`); loop check on the raw frames: the
  last frame differs from the first in 0 px (max channel difference 0)
- compose: `scripts/compose.sh springswap` wrote
  `media/springswap/final.mp4` at 10:28:47 EEST (h264 1080x1920 60 fps,
  2,400 frames, aac 22050 Hz mono, 40.000 s, 6,346,885 bytes; music
  seed 77 at gain 0.18; captions at caption_y 0.75, 38 drawtext filters,
  the overlay plus 37 caption chunks); loudness mean -16.2 dB, peak -0.0
  dB; preview (40.07 s) and 8x5 contact sheet written
  (`media/springswap/compose.log`)

### Local QA

- smoke pass 1 (10:25:59 EEST, `--frames` before any render): one
  layout defect found and fixed (the clock ghosting through the title in
  the loop fade; see Production); the fix is a one-line condition, so
  the footage render was the second look at the fade and it is clean in
  the final frame at 39.95 s
- final pass (10:29 EEST): frames at 0.02, 1.5, 5.0, 12.0, 15.5, 18.63,
  23.82, 24.83, 27.0, 30.5, 36.0 and 39.95 s extracted from final.mp4
  (`media/springswap/frame-*.png`) and inspected with the 8x5 contact
  sheet (`media/springswap/sheet.png`): 0.02 s shows the overlay "same
  bob, same bounce | real time | no seed" at y 96, the title "Bounce it
  up and down. / Does it start to swing?" at y 190 and 252 clear of it
  and of the labels, both bobs at the bottom of their bounce on straight
  springs, "swing 0.1 deg / bounce 10.0 cm" under each (the thumbnail);
  1.5 s shows both bobs mid-bounce under "A bob on a spring."; 15.5 s
  shows the gold bob leaning 2.4 degrees with its faint arc under "For
  ten seconds,"; 18.63 s shows "swing 5.1 deg / bounce 8.9 cm" with the
  spring slanted under "Each bounce lands in"; 23.82 s shows the gold
  bob at the right end of its arc, "swing 11.4 deg / bounce 2.3 cm", the
  card fading in, under "It leans eleven"; 24.83 s shows the gold bob at
  the left end with "bounce 0.9 cm", the card lit, under "point four
  degrees."; 27.0 s shows "swing 10.8 deg / bounce 5.0 cm" against the
  teal "swing 0.1 deg / bounce 10.0 cm" under "A quarter degree at";
  30.5 s shows the swap running backwards, "swing 7.1 deg / bounce 8.6
  cm", under "Does it start to"; 39.95 s shows the crossfade to the
  title frame with the card fading out, no clock, faint ghosts of the
  bobs at their two bounce phases; captions match the narration word for
  word (the contact sheet reads every chunk in order) and sit in the y
  1440 to 1520 band with the lowest readout text ending at y 1380 and
  the card from 1592; the widest text (the overlay, 858 px) is centred
  with 111 px margins and nothing clips at the frame edges; the payoff
  numbers are on screen when spoken (the gold readout "swing 11.4 deg"
  from about 23.6 s and the card from 23.8 s against "eleven point four
  degrees" at about 23.3 to 24.3 s; the teal readout "swing 0.1 deg"
  throughout and the card's "no, 0.14 deg" against "A quarter degree at
  most" at about 26.6 to 28.2 s); the loop closes: the raw last frame
  differs from the raw first frame in 0 px (render.log), the encoded
  footage's frames 2399 and 0 differ in 544 px by more than 24 levels
  (0.03 percent, max 54), and on the encoded final frame 2399 differs
  from frame 0 in 2,878 px (0.14 percent, at text edges, max channel
  difference 75, mean 0.43, encoder noise); ffprobe: h264 1080x1920,
  60/1 fps, 2,400 frames (also by decode), aac 22050 Hz mono, 40.000000
  s, atoms ftyp, moov, ... (moov before mdat), md5
  8195e70f050184e35e7d7533a2142e44; approved locally

### Metadata

- `projects/springswap/metadata.json`: title "Bounce it up and down.
  Does it start to swing? 2 bounces a swing: yes, 11.4 deg. 1.5: no,
  0.14 deg" (98 characters); description with the setup (the spring
  stretched to 1 m by the bob's weight, the 10 cm pull-down with a 0.1
  degree tilt, released at rest, the two tunings with k/m = 39.23 and
  22.07 s^-2 and natural lengths 0.75 and 0.556 m, the full polar
  equations, RK4 at 1200 steps/s with the half-step check, real time,
  no seed), a Measured list (the periods, the 1 and 5 degree crossings
  at 11.59 and 18.63 s, the 11.37 degree peak at 23.82 s, the bounce at
  the peak with the 3.09 cm last stretch, the readout minimum 0.85 cm at
  24.83 s, the state at 39.98 s, the detuned 0.141 degree maximum, the
  half-step and energy checks), a Why paragraph in plain words (a
  swinging bob tugs its spring twice per swing; at two bounces a swing
  every bounce lands in step with the tug and pushes the swing; the
  energy comes out of the bounce, which is why it fades to almost
  nothing at the peak and then the exchange runs backwards; at 1.5
  bounces a swing the pushes fall out of step and cancel), the rerun
  line and the AI-made line; 10 tags (spring pendulum, autoparametric
  resonance, parametric resonance, elastic pendulum, coupled
  oscillators, energy transfer, physics, physics visualization,
  simulation, shorts); category 27; private; containsSyntheticMedia
  true; selfDeclaredMadeForKids false; the same keys in the same order
  as projects/lifeguard/metadata.json
- not uploaded; task left open for the orchestrator's review and upload

### Release

- orchestrator review (10:37 EEST): the task evidence, the 8x5 contact
  sheet and the full-resolution frames at 0.02, 23.82, 27.0 and 39.95 s
  inspected: the question "Bounce it up and down. / Does it start to
  swing?" over both springs with the labels "2 bounces a swing" and "1.5
  bounces a swing" and both readouts at "swing 0.1 deg / bounce 10.0 cm"
  on the first frame; 23.82 s shows the left bob leaning on its swing arc
  at "swing 11.4 deg / bounce 2.3 cm" while the right bob holds "swing
  0.1 deg / bounce 10.0 cm", the card fading in under "It leans eleven";
  27.0 s shows the swing at 10.8 deg with the card lit under "A quarter
  degree at"; 39.95 s shows the crossfade to the title frame; the voice
  timing puts "Bounce it up and down." at 1.85 s, inside the two-second
  window, with the title question on screen from frame 0; every caption
  in the clear band, no clipping; the producer's bounce clause change
  ("almost stops", no number narrated, 3.09 cm in the description)
  accepted; final.mp4 h264 1080x1920 60 fps, 2,400 frames, aac 22050 Hz
  mono, 40.000 s, moov before mdat, md5
  8195e70f050184e35e7d7533a2142e44; title 98 characters; approved for
  release
- quota check: clock 2026-09-23T10:38:32+03:00; zero upload attempts recorded since the
  2026-09-23 10:00 EEST boundary (log entries and media/*/upload.log both
  checked; the newest upload.log is lifeguard at 2026-09-22 10:35); this
  is insert attempt 1 of the hard cap of 5
- attempt 1 recorded at 2026-09-23T10:38:32+03:00, video name springswap, before running
  `scripts/yt-upload.py springswap`

### Published

- upload: `scripts/yt-upload.py springswap` ran 10:38:12 to 10:38:39 EEST,
  token verified to see only the Seed Zero channel, video id
  utBc09NZWUk, private (`media/springswap/upload.log`)
- gate: `scripts/yt-qa.py springswap utBc09NZWUk --wait --publish` ran in
  the foreground from 10:38:46 EEST: processing succeeded and the 10 tags
  read back on the first poll, 15 of 15 pass (processed, succeeded, hd,
  1080x1920, title, description, tags as a set, category 27, not for
  kids, PT41S for the 40.000 s file, private); containsSyntheticMedia
  reads absent as on every earlier upload (`media/springswap/publish.log`)
- publish: the same run set the video public at 2026-09-23T10:39:20+03:00;
  the re-read after 15 s shows privacyStatus public, madeForKids false,
  embeddable true; public at https://youtu.be/utBc09NZWUk
- slot resolution: published for the 2026-09-23 quota day

### Quota

- attempt 1 of the hard cap of 5 for the quota day that began
  2026-09-23T10:00 EEST; cost 1 + 1,600 + 54 = 1,655 units (the
  channels.list verification inside yt-upload.py, the insert, the gate
  run's reads, update and re-read as printed by yt-qa.py); day total
  after one attempt 1,655 units

### Repository

- committed as 93c0496 "Publish the day twenty-five slate" (sims,
  projects, tasks, docs/niche.md, web/data; no media, previews or
  secrets) and pushed to origin/master at 2026-09-23 10:44 EEST
