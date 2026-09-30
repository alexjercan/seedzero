# Produce short: Box or ball on a moving belt, which one rides along

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day32

## Goal

Backlog idea (trend research 2026-09-30, task 20260930-100404, pillar 2
chaos and physics, rolling; read the full entry under "Added by trend
research 2026-09-30" in docs/niche.md):
"Ball or box on a moving belt: a box (mu 0.4) and a solid ball placed
at rest at the start of a 2 m belt running at 1.0 m/s; measure the
speed each settles at and when each leaves the belt; expect the box to
reach belt speed in 0.255 s after sliding 12.7 cm and leave at 2.13 s,
and the ball to stop slipping after 0.073 s and 1.0 cm at exactly 2/7
of the belt speed (0.2857 m/s, V k / (1 + k)), rolling backward on the
belt at 5/7 V for ever and leaving at 7.04 s; ring 1/2, cylinder 1/3,
hollow ball 2/5; any mu > 0 works; no rolling resistance, say so; the
belt is periodic so the short loops; deterministic, no seed."

Orchestrator notes (2026-09-30, before this brief). The model: a
conveyor belt (a checkout belt or a moving walkway) 2.00 m long runs at
V = 1.0 m/s to the right. At t = 0 a box and a solid ball (k = 2/5,
radius r, choose 3 to 4 cm, with a stripe so the spin shows) are set
down at rest at the belt's start, mu = 0.4 for both against the belt.
Box: kinetic friction mu g accelerates it until it matches the belt,
then it rides. Ball: the same friction accelerates the centre at mu g
and spins it up (backspin sense: the bottom point moves forward
relative to the centre); the slip ends when the bottom point moves at
the belt's speed, v (1 + 1/k) = V, and from then on the ball rolls with
no friction at all, forward over the ground at v and backward relative
to the belt at V - v. Checks, not facts (orchestrator closed forms in
/tmp/day32/check.py and check.log): box at belt speed after V / (mu g)
= 0.2549 s and 12.75 cm of slip, leaves the 2 m belt at 2.127 s; ball
slips for V k / (mu g (1 + k)) = 0.0728 s over 1.04 cm, then rolls at
V k / (1 + k) = 2/7 V = 0.2857 m/s over the ground, 0.7143 m/s backward
relative to the belt, and leaves at 7.04 s; angular momentum about the
belt surface line is conserved through the slip (print it: m v (1 + k)
= k m V); a stepped Coulomb slip at 1e-6 s against the closed forms and
a half-step rerun. For the description print: ring 1/2 (off at 4.06
s), cylinder 1/3 (6.04 s), hollow ball 2/5 (5.05 s); any mu above zero
gives the same 2/7 (mu changes only the 0.07 s and 1 cm); the same
physics in a car pulling 0.3 g rolls a footwell ball back at 5/7 of
the car's acceleration (2.10 m/s^2, 1 m in 0.98 s, needs mu 0.086)
while a box with mu 0.4 stays put; no rolling resistance and no air,
a real ball creeps up to belt speed eventually. State every derived
number above as a check the sim must print, not as a fact.

Drawing: side view, two panels stacked on one clock (box on top, ball
below), the same belt drawn the same way at the same scale with a
moving texture (stripes or rollers moving at V, so the belt's motion is
visible even when the ball barely moves), the same start and exit
lines; a stripe on the ball; per-panel readouts: ground speed and, for
the ball, "on the belt: -0.71 m/s"; a short slow-motion or an inset is
NOT required (the 0.07 s slip is a detail); real time is fine, a run
is 7.04 s for the ball, so five runs fit about 40 s with a short fade
and reset between them (or a cycle length that divides the scene); the
box leaves at 2.1 s and the exit label "off at 2.1 s, at belt speed"
stays until the reset; the ball's label "2/7 of the belt speed, 0.29
m/s" when the slip ends and "off at 7.0 s" at the exit; the last frame
equals the first.

Day thirty-two, second slot. Chosen because the intuition is split
(the forum thread the research read answered "belt speed"), the payoff
is an exact fraction, the panels end differently (the box gone, the
ball still crawling), and it is everyday (checkout belt, treadmill).
Question in the first two seconds: "A box and a ball on a moving belt.
Which one rides along?" (or the producer's wording with the question by
word nine; keep the question identical in the title, the hook and the
payoff). Setup number: the belt runs at one meter per second (say the
unit once). Payoff number: the box rides at the belt's speed; the ball
crawls at two sevenths of it. The 0.25 s, 12.7 cm, 2.1 s and 7.0 s go
to the card and the description. Whisper risks: pre-test "belt",
"sevenths" (if "two sevenths" fails, say "less than a third of it" and
keep 2/7 on the card and in the title), "rides"; avoid "do you" before
a verb; pre-test hooks with scripts/voiceover.sh and keep the one whose
question lands earliest under two seconds. Make the last frame equal
the first. Measure every fixed text line with PIL before rendering and
keep every line under 950 px, and the title under 100 characters with
no < or >. Music seed 99. Templates: sims/cueball (stepped Coulomb
slip, closed forms), sims/rollrace and sims/uphill (rolling bodies with
stripes, two panels on one clock, cycle and loop checks),
sims/tablecloth (reset fade). Sim name belt: sims/belt/belt.py,
projects/belt/, media/belt/.
## Claim

A box and a solid ball are set down at rest on a 2 m belt running at
1 m/s, both with grip 0.4. The box reaches the belt speed after 0.2549 s
and 12.75 cm of slip and leaves the belt at 2.1275 s, at belt speed. The
ball stops slipping after 0.0728 s and 1.04 cm at 0.2857 m/s = 2/7 of
the belt speed, rolls backward on the belt at 0.7143 m/s and leaves at
7.0364 s, 3.31 times as long on the belt. Narrated: "The box rides along,
at the belt's speed. The ball crawls at less than a third of it. Its spin
took most of the push." (0.2857 < 1/3; r omega = 0.7143 m/s against
v = 0.2857 m/s). Title and card carry the exact 2/7.

## Evidence

### Measurements

Command: `nix develop --command python3 sims/belt/belt.py --measure-only`
with date lines, written to media/belt/measure.log (copied whole):

```
Wed Sep 30 10:59:06 AM EEST 2026
setup: the same belt in both panels, 2 m from the start line to the exit line, running at V = 1 m/s to the right (stripes every 0.1 m move with it); at the release a box of side 8 cm (top panel, no spin) and a solid ball of radius 4 cm (bottom panel, I = 0.4 m r^2, a stripe on it) are set down at rest at the start line, both with sliding friction coefficient 0.4 against the belt; while the bottom of an object lags the belt the belt drags it forward with mu m g = 3.9227 m/s^2 on the centre (and mu g / (k r) = 245.17 rad/s^2 on the ball's spin); once the bottom point matches the belt nothing slips and no friction acts; each object leaves when its centre crosses the exit line, then falls off the end of the belt (g = 9.80665 m/s^2) and drops out of its panel; no rolling resistance and no air (a real ball would creep up to the belt speed); the slip stepped as a Coulomb slip at dt = 1e-06 s, checked against the closed forms and a half-step rerun; shown in real time on a 8 s cycle (480 frames) with the release 0.2 s into the cycle, 5 cycles in 40 s; drawn at 480 px per metre; deterministic, no seed
box: stepped slip: at belt speed after 0.2549 s (closed form V / (mu g) = 0.2549 s, diff -1.1e-12 s) and 12.75 cm of slip (closed form V^2 / (2 mu g) = 12.75 cm, diff -9.9e-11 cm), 254930 steps; speed then 1.000000 m/s = the belt's (1.0000 V), 0 m/s on the belt, so the belt has nothing left to drag and the box rides; its centre crosses the exit line 2 m on at 2.1275 s (closed form t + (L - d) / V = 2.1275 s, diff -8.4e-14 s), at belt speed
ball: stepped slip: the slip ends after 0.0728 s (closed form V k / (mu g (1 + k)) = 0.0728 s, diff +7.4e-14 s) and 1.04 cm (closed form 1.04 cm, diff -3.4e-14 cm), 72837 steps; speed over the ground then 0.2857 m/s = 0.2857 of the belt speed (closed form V k / (1 + k) = 2/7 V = 0.2857 m/s, diff -3.2e-13 m/s); spin 17.86 rad/s (2.84 turns a second, bottom point moving forward), r omega = 0.7143 m/s, so the bottom point moves at v + r omega = 1.000000 m/s = the belt's and the slip is closed; on the belt the centre moves at v - V = -0.7143 m/s (0.7143 V backward, 5/7 = 0.7143): it rolls backward on the belt; angular momentum about the belt surface line per unit mass k r^2 omega - r v stays within 4.5e-13 of zero (in m r V) through the slip (the friction acts along that line), and m v (1 + k) = 0.4000 m = k m V = 0.4000 m; from then on no friction acts, v and the spin hold, and its centre crosses the exit line at 7.0364 s (closed form t + (L - d) / v = 7.0364 s, diff +7.9e-12 s), still at 0.2857 m/s
the two panels: the box leaves at 2.1275 s at 1.0000 m/s (belt speed); the ball leaves at 7.0364 s at 0.2857 m/s (0.2857 of the belt speed, 2/7 = 0.2857), 3.31 times as long on the belt; on the belt the box sits still (0 m/s) and the ball rolls backward at 0.7143 m/s; both feel the same drag mu m g, but the ball's drag also spins it, and the spin matches the belt after 0.0728 s, when the centre has only 0.2857 V
for the description (same belt, same grip unless said): ring (k = 1.0000): settles at 0.5000 m/s = 0.5000 V (closed form k / (1 + k) = 0.5000) after 0.1275 s and 3.19 cm, off at 4.064 s; solid cylinder (k = 0.5000): settles at 0.3333 m/s = 0.3333 V (closed form k / (1 + k) = 0.3333) after 0.0850 s and 1.42 cm, off at 6.042 s; hollow ball (k = 0.6667): settles at 0.4000 m/s = 0.4000 V (closed form k / (1 + k) = 0.4000) after 0.1020 s and 2.04 cm, off at 5.051 s; the solid ball with grip 0.1: settles at 0.2857 V after 0.2913 s and 4.16 cm, off at 7.146 s; the solid ball with grip 1: settles at 0.2857 V after 0.0291 s and 0.42 cm, off at 7.015 s; the same physics in a car pulling 0.3 g (a = 2.9420 m/s^2): a footwell ball rolls back at a / (1 + k) = 5/7 a = 2.1014 m/s^2, 1 m in 0.9756 s, rolling without slipping if the grip is at least a k / (g (1 + k)) = 0.0857; a box with grip 0.4 stays put since 0.3 g is under 0.4 g
check at half the time step (5e-07 s): box slip 0.2549291 s (-4.3e-13), 12.7464527 cm (+2.4e-10), speed 1.0000000 m/s (+0.0e+00), off at 2.1274645 s (-2.8e-12); ball slip 0.0728369 s (+6.7e-14), 1.0405267 cm (+8.4e-13), speed 0.2857143 m/s (+5.2e-13), off at 7.0364184 s (-1.3e-11)
schedule (video time, real time): cycles of 8 s start at -0.20, 7.80, 15.80, 23.80, 31.80, 39.80 s (the first 0.20 s before the first frame); the objects are set down at rest 0.2 s into each cycle at 0.00, 8.00, 16.00, 24.00, 32.00 s; the box is at belt speed at 0.25, 8.25, 16.25, 24.25, 32.25 s and crosses the exit line at 2.13, 10.13, 18.13, 26.13, 34.13 s (off the frame 0.19 s later, having dropped 17.7 cm); the ball's slip ends at 0.07, 8.07, 16.07, 24.07, 32.07 s and it crosses the exit line at 7.04, 15.04, 23.04, 31.04, 39.04 s (out of its band 0.30 s later at x 1051 px); the reset crossfade runs over the last 0.4 s of each cycle (the readouts out from 7.40, 15.40, 23.40, 31.40, 39.40 s, the resting objects in from 7.60, 15.60, 23.60, 31.60, 39.60 s); on the first frame the cycle is 0.20 s in (0.00 s after the release: the box at 0.0 cm and 0.00 m/s, the ball at 0.0 cm and 0.00 m/s, slip); title until 3 s; payoff card from 23.8 s; the title fades back in over the last 0.5 s and the last frame repeats the first (the scene is periodic: 40 s holds exactly 5 cycles); belt texture: 8 px per frame, period 48 px, 400 periods in 40 s (a whole number, so the stripes match across the seam)
text widths: overlay@34 771 px, title line 1@56 588 px, title line 2@56 617 px, legend@40 650 px, clock@28 370 px, clock held@28 326 px, label box@40 82 px, sublabel box@28 362 px, fixed box@28 323 px, readout box@40 517 px, readout off box@40 251 px, on belt box@28 329 px, spin box@28 115 px, event box ride@40 573 px, event box off@40 597 px, label ball@40 83 px, sublabel ball@28 362 px, fixed ball@28 323 px, readout ball@40 517 px, readout off ball@40 251 px, on belt ball@28 329 px, spin ball@28 246 px, event ball ride@40 691 px, event ball off@40 829 px, start@24 65 px, exit@24 119 px, belt arrow@24 135 px, payoff line 1@40 867 px, payoff line 2@40 840 px, payoff line 3@40 810 px, payoff line 4@40 899 px, payoff line 5@40 858 px, payoff line 6@40 827 px
row check: the left column ends at x 402 px, the right column starts at x 523 px; both end 136 px under the band top; the event row spans 278 to 322 px under the band top (widest 829 px, centred), the objects' tops sit 342 px under the band top on the belt at 380; the marks under the belt at 440 px; each band is 550 px tall (y 330 to 880 and 880 to 1430); the caption band starts at y 1440; the title rows end at y 280 and the overlay band ends at y 130
Wed Sep 30 10:59:07 AM EEST 2026
```

Brief checks against the log (closed forms in /tmp/day32/check.log):

- box at belt speed after V / (mu g) = 0.2549 s: 0.2549 s, diff
  -1.1e-12 s. Holds.
- box slip 12.75 cm: 12.75 cm, diff -9.9e-11 cm. Holds.
- box off the 2 m belt at 2.127 s: 2.1275 s, diff -8.4e-14 s. Holds.
- ball slip V k / (mu g (1 + k)) = 0.0728 s over 1.04 cm: 0.0728 s,
  1.04 cm. Holds.
- ball at V k / (1 + k) = 2/7 V = 0.2857 m/s: 0.2857 m/s, diff -3.2e-13
  m/s. Holds.
- ball 0.7143 m/s backward on the belt: -0.7143 m/s (5/7 V). Holds.
- ball off at 7.04 s: 7.0364 s, diff +7.9e-12 s. Holds.
- angular momentum about the belt surface line conserved through the
  slip: k r^2 omega - r v within 4.5e-13 of zero; m v (1 + k) = 0.4000 m
  = k m V. Holds.
- stepped Coulomb slip at 1e-6 s against the closed forms: all diffs
  under 1e-10. Half-step rerun at 5e-7 s: all diffs under 1e-9. Holds.
- ring 1/2 off at 4.06 s: 0.5000 V, off 4.064 s. Holds.
- cylinder 1/3 off at 6.04 s: 0.3333 V, off 6.042 s. Holds.
- hollow ball 2/5 off at 5.05 s: 0.4000 V, off 5.051 s. Holds.
- any mu above zero gives the same 2/7: grip 0.1 gives 0.2857 V after
  0.2913 s and 4.16 cm; grip 1 gives 0.2857 V after 0.0291 s and
  0.42 cm. Holds.
- car at 0.3 g: footwell ball back at 5/7 a = 2.1014 m/s^2 (brief 2.10),
  1 m in 0.9756 s (0.98), needs grip 0.0857 (0.086); box with grip 0.4
  stays put (0.3 g under 0.4 g). Holds.
- backlog numbers 0.255 s, 12.7 cm, 2.13 s, 0.073 s, 1.0 cm, 7.04 s hold
  at their rounding.

No discrepancy.

### Production

- Sim: sims/belt/belt.py. Stepped Coulomb slip (Euler on v and omega at
  dt = 1e-6 s, trapezoid on x, linear interpolation for the slip
  closure), closed forms, half-step rerun, layout asserts (every text
  line under 950 px, columns do not meet, the ball leaves at the right
  edge, texture period a whole number of frames), loop and periodicity
  checks. Deterministic, no seed.
- Manifest: projects/belt/manifest.json. V 1.0 m/s, L 2.0 m, mu 0.4, box
  side 8 cm, ball radius 4 cm, k 0.4, g 9.80665, step 1e-6 s, cycle 8 s
  with the release 0.2 s in, first cycle at -0.2 s, reset fade 0.4 s,
  5 cycles in 40 s, 480 px/m, start_x 50 px, belt lead 0.05 m, texture
  period 0.1 m, title until 3 s, payoff card from 23.8 s (hold 0.6 s),
  loop fade 0.5 s, music seed 99, gain 0.18, voice offset 0.6 s,
  caption_y 0.75, overlay "belt 1 m/s | grip 0.4 | real time | no seed".
- Scene: two panels on one clock, the same belt drawn the same way with
  stripes every 0.1 m moving at 16 layer px per frame (period 96 layer
  px, 400 whole periods in 40 s so the stripes match across the seam).
  Per-panel readouts: ground speed, on the belt +/-, spin (ball), event
  row ("at belt speed after 0.25 s", "2/7 of the belt speed, 0.29 m/s",
  "off at 2.13 s, at belt speed", "off at 7.04 s, 2/7 of the belt
  speed"). Objects fall off the belt end under g after the exit line and
  leave the panel. Reset crossfade over the last 0.4 s of each cycle.
- Narration: projects/belt/narration.txt, 108 words, question by word
  three, unit said once. Voice: scripts/voiceover.sh, Piper 10303,
  whisper.cpp 10301 round trip. Pass 1 (10:56) ok 29.81 s. Pass 2
  (11:04) ok 30.39 s, after removing two commas ("on the belt and
  crawls", "crawls at less than") that Piper did not pause at, which had
  led the payoff captions by 0.9-1.3 s. No mishearing in either pass.
  Voice ends at 30.99 s of video.
- Hook pre-test (media/belt/hooks/pretest.log, 11 probes): hook1 "Which
  one rides along, the box or the ball?" ok 4.79 s; hook2 "Which rides
  along, box or ball?" fails ("along, box" -> "a long box"); hook3 "A box
  and a ball on a moving belt. Which one rides along?" ok but question
  lands after 2 s; hook4 ok, same; hook5 "rides the belt" fails ("rise");
  hook6 and hook8 fail ("a long"); hook7 "Which rides along, the box or
  the ball?" ok 4.56 s, chosen (question spoken 0.68-1.5 s of video,
  ends by word nine); frac1 "two sevenths" fails ("two seventh"); frac2
  "less than a third of it" ok; mech1 (mechanism block) ok 18.52 s.
- Timing: scripts/voice-timing.py -> media/belt/timing.log; whisper word
  times +0.6 s -> media/belt/words.log; silencedetect pauses ->
  media/belt/silences.log (17 pauses, 16 interior). Schedule from the
  word times: releases at 0, 8, 16, 24, 32 s; "drags it up to speed.
  Then the box rides" 8.07-10.34 over the box dragged 8.0-8.25 and
  riding to 10.13; "keeps up with the belt" 16.46-17.47 as the fresh
  ball's 2/7 label lights at 16.07; "The box rides along, at the belt's
  speed" 24.59-26.47 over the box riding 24.25-26.13 and its exit label
  from 26.13; "The ball crawls at less than a third of it" 26.98-28.66
  over the ball rolling 24.07-31.04 with its 2/7 label lit; card from
  23.8 s (lit 24.4 s).
- Render: `nix develop --command python3 sims/belt/belt.py` ->
  media/belt/render.log (11:00:27-11:01:14): loop check 0 px,
  periodicity check 0 px, loop step 13,416 px, footage 40.00 s at 60 fps
  (2400 frames).
- Compose: scripts/compose.sh belt -> media/belt/compose.log
  (11:04:20-11:04:33): music seed 99 40.00 s; "captions: 16 pauses
  detected, 16 matched, max chunk start shift 0.800 s against
  word-count timing"; contact sheet 8x5 at 1 fps; final.mp4 40.000000 s.
  The two unmatched punctuation boundaries are the "along," commas in
  the two questions, where Piper does not pause. 30 caption chunks,
  108 words, word-for-word match with the narration, longest chunk
  21 chars.

### Local QA

- Footage signalstats: overlay band (rows 96-130) and caption band
  (rows 1440-1530) YMAX 28 in all 2400 footage frames; both bands hold
  only the background.
- Final loop noise (codec only): frame 2399 vs 0: 29,495 px over
  8 levels, 786 over 32, max 73, mean 0.41; 2398 vs 2399: 36,109 /
  13,134 / max 62; 0 vs 1: 21,140 / 15,949 / max 251. The seam is
  quieter than an ordinary frame step.
- Frames extracted from media/belt/final.mp4 (never edited) and read:
  0.00 (overlay, two-row title, both objects at rest on the start line,
  readouts 0.00 m/s, belt stripes, no caption, no card), 1.00 (caption
  "Which rides along,", box already at belt speed), 2.40 (box falling
  off the belt end, exit label lit), 8.30 (second cycle, box riding,
  ball rolling with its 2/7 label), 14.40 (ball near the exit, box gone),
  16.20 (clock 0.20 s after the release, box 0.78 m/s slipping, ball 2/7
  label lit, caption "Once the bottom of"), 24.30 (card fading in,
  caption "the ball?", box riding), 25.60 (box 1.00 m/s in gold with
  "at belt speed after 0.25 s", ball 2/7 label, caption "The box rides
  along,", card lit), 27.30 ("off at 2.13 s, at belt speed", ball
  rolling, caption "The ball crawls at", card), 29.00 (caption "less
  than a third", card), 33.50 (fifth cycle, no caption, card holds),
  39.98 (title back, equals frame 0). Nothing clipped, no text over
  the caption band, labels lit at the spoken moments.
- Smoke frames from the footage before compose: 0.0, 2.2 (box flying
  off the end), 7.2 (ball dropping past the exit roller), 7.7 (resting
  objects fading in), 8.1, 15.7, 24.3, 26.5, 39.6 (loop fade), 39.98.
- Contact sheet media/belt/sheet.png: 40 thumbnails, clean.
- Caption alignment against whisper word times: "The box rides along,"
  caption 24.595 vs "box" spoken 24.64; "The ball crawls at" 27.011 vs
  "ball" 27.06; "Its spin took most" 29.182 vs "spin" 29.36; first
  caption 0.600 vs "Which" 0.68.
- ffprobe: h264 1080x1920 yuv420p 60/1, 2400 frames; aac 22050 Hz mono;
  duration 40.000000 s; 4,424,136 bytes; moov before mdat.
- md5sum media/belt/final.mp4: 7e205eb148ee05932e28a72576a2ef27.
- Description check: 58 numbers in the description, every one present
  in measure.log.
- Title 92 chars, no < or >. Every fixed text line measured with PIL
  under 950 px (widest: event ball off 829 px, payoff line 4 899 px).

### Metadata

projects/belt/metadata.json:

- title: "Which rides along, the box or the ball? The box, at belt
  speed; the ball crawls at 2/7 of it" (92 chars).
- description: 3411 chars ASCII. The model, a "Measured:" list (box
  0.2549 s, 12.75 cm, 1.0000 m/s, off 2.1275 s; ball 0.0728 s, 1.04 cm,
  0.2857 m/s, 17.86 rad/s, 2.84 turns/s, bottom point 1.000000 m/s,
  0.7143 m/s backward, off 7.0364 s, 3.31 times as long; angular
  momentum 4.5e-13, m v (1 + k) = 0.4000; ring 0.5000 V 0.1275 s 3.19 cm
  off 4.064 s; cylinder 0.3333 V 0.0850 s 1.42 cm off 6.042 s; hollow
  ball 0.4000 V 0.1020 s 2.04 cm off 5.051 s; grip 0.1 and grip 1 both
  0.2857 V; car 0.3 g 2.9420 m/s^2, ball back at 2.1014 m/s^2, 1 m in
  0.9756 s, grip 0.0857; check diffs), a "Why:" paragraph, the half-step
  rerun line, no rolling resistance and no air stated, AI-made line.
- tags (11): box or ball, which rides along, conveyor belt, rolling
  ball, sliding friction, moment of inertia, angular momentum, physics,
  physics visualization, simulation, shorts.
- categoryId 27, privacyStatus private, containsSyntheticMedia true,
  selfDeclaredMadeForKids false.

### Deviations from the brief

- Question wording "Which rides along, the box or the ball?" (hook7)
  instead of "A box and a ball on a moving belt. Which one rides along?"
  The brief's wording lands the question at about 2.5 s; hook7 lands it
  by 1.5 s. "along, box" is mis-heard as "a long box", so the articles
  stay. The same wording is in the title, the hook and the payoff.
- Payoff says "less than a third of it": "two sevenths" failed the
  pre-test ("two seventh"). 2/7 is on the card, in the title, in the
  ball's event label and in the description, as the brief allows.
- Objects fall off the belt end under g after the exit line and leave
  the panel (the box off the right edge, the ball out of the band
  bottom). The landing is not modelled or drawn.
- Box side 8 cm, ball radius 4 cm (brief: 3 to 4 cm). Belt starts at
  x 50 px with a 5 cm lead before the start line so the ball clears the
  right edge before the band bottom.
- The ball's exit label reads "off at 7.04 s, 2/7 of the belt speed"
  (brief: "off at 7.0 s"); the 5/7 backward speed shows as the "on the
  belt -0.71 m/s" readout, not in the narration.
- Real time, no slow motion or inset (allowed by the brief). The 0.07 s
  slip is only visible as the stripe spin-up and the 2/7 label.
- Frame 0 is the release instant: objects at rest on the start line,
  belt already moving. The last frame equals the first.
- Voice ends at 30.99 s; the last 9 s carry the card, the fifth cycle
  and the loop fade with music only.
- Two commas removed from the narration after pass 1 for caption
  alignment (see Production). Card drops the "any grip gives 2/7" line
  (kept in the description); ring 1/2, cylinder 1/3, hollow ball 2/5 are
  the sixth card line.
- Voice pass 1 (29.81 s) was replaced by pass 2 (30.39 s); the pass-1
  compose had captions leading the words by 0.9-1.3 s from "So," on
  because the DP skipped "belt," and "crawls." instead of the two
  unpaused commas.

## Niche note

[produced 2026-09-30 as "Which rides along, the box or the ball? The
box, at belt speed; the ball crawls at 2/7 of it"; measured the box at
belt speed after 0.2549 s and 12.75 cm, off the 2 m belt at 2.1275 s;
the solid ball's slip ending after 0.0728 s and 1.04 cm at 0.2857 m/s
(2/7 V), 0.7143 m/s backward on the belt, off at 7.0364 s, 3.31 times as
long on the belt; ring 1/2 (off 4.064 s), cylinder 1/3 (6.042 s), hollow
ball 2/5 (5.051 s); grips 0.1 and 1 give the same 2/7; a car at 0.3 g
rolls a footwell ball back at 2.1014 m/s^2, 1 m in 0.9756 s, needing
grip 0.0857; stepped Coulomb slip at 1e-6 s within 1e-11 of the closed
forms, half step within 1e-9; narrated "less than a third of it" because
whisper hears "two seventh"; task 20260930-104026]

## Upload

- orchestrator review (2026-09-30T11:19:48+03:00): task evidence, sheet.png and full frames at
  0.00, 25.60, 29.00 and 39.98 s inspected; ffprobe h264 1080x1920 60 fps
  2400 frames 40.000 s; md5 7e205eb148ee05932e28a72576a2ef27; title 92
  chars, no angle brackets; captions match narration word for word;
  measure.log numbers match the closed forms in /tmp/day32/check.py (box
  reaches belt speed after 0.2549 s and 12.75 cm, off the belt at 2.127 s;
  ball settles at Vk/(1+k) = 0.2857 m/s after 0.0728 s and 1.04 cm, off
  the belt at 7.036 s; angular momentum about the belt line 0.4000 kept);
  approved for upload
- upload attempt 2 of 5 for the quota day that began 2026-09-30T10:00
  EEST, recorded at 2026-09-30T11:19:48+03:00 before starting scripts/yt-upload.py; one
  attempt (wallbounce, published as vC17_o8y_y4) was on record since the
  boundary
- uploaded private as mYyXLCyecNA at 2026-09-30T11:19:54+03:00
  (https://youtu.be/mYyXLCyecNA); channels.list 1 unit + videos.insert
  1,600 units; media/belt/upload.log
- scripts/yt-qa.py belt mYyXLCyecNA --wait --publish in the foreground
  (started 2026-09-30T11:20:01+03:00): gate 15 of 15 on the second read
  (processed, succeeded, hd, 1080x1920, title, description and tags
  match, category 27, not made for kids, PT41S for the 40.000 s file,
  private before publish); published at 2026-09-30T11:20:18+03:00;
  re-read privacyStatus=public selfDeclaredMadeForKids=False
  embeddable=True; yt-qa quota 53 units; media/belt/publish.log
- attempt 2 of 5 complete: 1,654 units; slot 2 of 3 resolved as
  published (recorded 2026-09-30T11:20:47+03:00)

### Quota
- attempt 2 of the hard cap of 5 for the quota day that began
  2026-09-30T10:00 EEST; cost 1,654 units (the channels.list verification
  inside yt-upload.py, the 1,600-unit insert, and the gate run's 2 reads,
  update and re-read as printed by yt-qa.py); day total after two
  attempts 1,664 + 1,654 = 3,318 units plus 5 for the 10:02 stats
  refresh, 3,323 of 10,000 used, 6,677 remaining

## Push
- committed as 5710175 "Publish the day thirty-two slate" and pushed to
  origin/master at 2026-09-30T11:25:56+03:00 (ec85030..5710175; the push also carried
  the unpushed day 31 commit 3b58b88); media/ and secrets/ not committed
