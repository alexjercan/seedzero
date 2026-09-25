# Produce short: Cue ball follow, a sliding cue ball beside a rolling one on the same hit

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day27

## Goal

Backlog idea (trend research 2026-09-25, task 20260925-101408, pillar 2
chaos and physics, collisions; read the full entry under "Added by
trend research 2026-09-25" in docs/niche.md):
"Cue ball follow: two cue balls at 2.0 m/s into a still ball head-on,
one sliding with no spin and one rolling; measure the cue ball's speed
after the hit; expect the sliding ball to stop dead and the rolling
ball to creep forward to exactly 2/7 of its speed (0.571 m/s) once the
cloth friction turns its kept spin back into rolling, the struck ball
settling at 5/7 (1.429 m/s) in both panels (mu 0.2 sets only the
settling distances, 8.3 and 50 cm; the fractions are exact); a stripe
on the ball shows the spin; repeat the shot; deterministic, no seed."

Orchestrator notes (2026-09-25, before this brief): the model is the
standard one. Equal-mass balls, head-on, elastic, no friction between
the balls: the hit swaps the balls' forward speeds and leaves each
ball's spin as it was. Top panel (no spin): the cue ball arrives at
2.0 m/s with no spin, hands its 2.0 m/s to the object ball and stops
dead, and stays put (no spin, nothing to move it). Bottom panel
(rolling): the cue ball arrives rolling at 2.0 m/s (spin v / R), hands
over its 2.0 m/s and is left at rest but still spinning forward; the
cloth friction (mu = 0.2, sliding friction on a solid sphere, I = 2/5
m R^2) pushes it forward while it slides, the slip v - R omega closes
at (7/2) mu g, and it rolls again at v = 2 v0 / 7 = 0.5714 m/s after
v0 / (3.5 mu g) = 0.291 s and 8.3 cm (0.5 mu g t^2). The object ball
in both panels leaves at 2.0 m/s sliding with no spin and settles to
5 v0 / 7 = 1.4286 m/s after the same 0.291 s and 50.0 cm (v0 t - 0.5
mu g t^2). Print all of these from the integration of both balls
(RK4 or exact piecewise) against the closed forms (2/7, 5/7, the times
and the distances), and print the state at the instant of the hit in
both panels (2.0000 m/s, spin 0 against spin v / R). The run-up:
friction acts on any sliding contact, so a spinless ball on real cloth
begins to roll during its run-up; either launch the no-spin ball with
the backspin that friction wears off exactly at the hit (print the
launch state and check the state at the hit) or draw the run-up as
given and say in the description that the ball arrives spinless (a
stun hit); the producer chooses and states the model. Ball radius
28.6 mm (a 57.2 mm ball). The cue ball's kept spin is the one visible
causal story, so show the spin: a side view with a stripe or a dot on
each ball that turns with it, so the top cue ball stops with its
stripe frozen and the bottom cue ball stops moving while its stripe
keeps turning, then creeps forward. The producer may pick other round
values as long as the sim prints them; keep 2/7 and 5/7 exact by
keeping mu the same in both panels.

Day twenty-seven, second slot. Chosen because it is an everyday pool
debate (stop, stun or follow) settled by an exact fraction, two panels
on the same hit that end differently (a dead stop against a creep
forward), continuous tabletop motion in the ball genre and the
collision family (cradle 958, pi blocks 991, rolling race 950).
Question in the first two seconds: "Hit the ball dead on. Does the cue
ball stop?" (or the producer's better wording, kept identical in the
title, the hook and the payoff). Setup number: two meters a second;
payoff number: two sevenths of its speed (0.57 m/s). The 5/7, the
times and the distances go to the description and the readouts.

Model: as above; a side view (or the producer's view that shows the
spin), the two panels stacked, "no spin" above and "rolling" below,
the cloth as a line, the object ball 30 cm ahead of the cue ball at the
start, the shot repeated every few seconds with a reset so the short
loops (the object ball rolls out of the frame; fade and reset). Print
the schedule in video time, the loop check and the on-screen text
widths. Make the last frame equal the first. Music seed 84.

## Claim

Two cue balls hit a still ball dead on at two meters a second. The one
that arrives with no spin stops dead. The one that arrives rolling
stops, then its kept spin drags it forward again to exactly two
sevenths of its speed, 0.571 m/s; the struck ball rolls off at five
sevenths in both cases. Every number in the narration is printed by
the sim before the script is written (the producer may change the
round values; the sim sets the claim).

## Evidence

### Measurements

(recorded after the measure-only run, before scripting)

`sims/cueball/cueball.py --measure-only` with
`projects/cueball/manifest.json` (two cue balls hit a ball at rest dead
on at v0 = 2 m/s, drawn from the side one above the other; ball radius
28.6 mm (a 57.2 mm ball), equal masses, a solid sphere I = 2/5 m R^2,
cloth sliding friction mu = 0.2 on any slipping contact, g = 9.80665,
no rolling resistance, no friction between the balls, an elastic
head-on hit that swaps the balls' forward speeds and keeps each ball's
spin; the top cue ball arrives sliding with no spin, a stun shot struck
with the backspin that the cloth wears off exactly at the hit (the
model chosen over drawing an unphysical spinless run-up: the sim
prints the launch state and checks the state at the hit), the bottom
cue ball arrives rolling; the struck ball rests 30 cm ahead of the
rolling cue ball, centre to centre, at x = 0.38 m of the 0.90 m
panel; each panel integrated as exact constant-acceleration pieces
between the events, slip closure and the hit, no time step; shown at
1/8 speed, one shot every 8 s, 5 shots in 40 s in this first manifest,
the schedule to be set from the voice timing; drawn at 1200 px per
metre, ball radius 34.3 px; deterministic, no seed; run at 10:39:07
EEST, log in `media/cueball/measure.log`):

- launch (t = 0 of each shot, real time): the rolling cue ball leaves
  x = 0.0800 m at 2.0000 m/s rolling (spin 69.930 rad/s) and reaches
  the ball after 0.1214 s (0.2428 m); the no-spin cue ball leaves x =
  0.0655 m, 31.45 cm behind the ball, at 2.2381 m/s with 20.813 rad/s
  of backspin (R omega = -0.5953 m/s), so that the cloth (mu g =
  1.9613 m/s^2 on the speed, 5 mu g / 2 R = 171.44 rad/s^2 on the
  spin) wears the backspin off exactly at the hit
- hit: at 0.1214 s of real time in both panels (target 0.1214 s, diffs
  5.6e-17 and 0) the cue balls touch the ball at x = 0.3228 m; the top
  cue ball arrives at 2.0000 m/s with spin 0.0000 rad/s (diffs 2.2e-16
  and 1.1e-14), the bottom cue ball at 2.0000 m/s with spin 69.930
  rad/s (v0 / R = 69.930, diff 0); right after the hit the top cue
  ball has 0.0000 m/s and spin 0.0000, the bottom cue ball 0.0000 m/s
  and spin 69.930, the struck ball 2.0000 m/s with spin 0 in both
  panels; momentum 2.0000 = 2.0000 and translational energy 2.0000 =
  2.0000 per unit mass across the hit
- follow: the bottom cue ball, at rest but spinning, is dragged
  forward by the cloth and rolls again at 0.5714 m/s after 0.2913 s
  and 0.0832 m of creep (closed forms 2 v0 / 7 = 0.5714 m/s, v0 / (7/2
  mu g) = 0.2913 s, 1/2 mu g t^2 = 0.0832 m; diffs 1.1e-16, 0,
  1.4e-17); that is 0.28571 of its arrival speed (2/7 = 0.28571, diff
  5.6e-17); its spin falls from 69.930 to 19.980 rad/s (v / R =
  19.980); after that it rolls on at 0.5714 m/s to the end of the shot
- struck ball: leaves sliding at 2.0000 m/s with no spin and rolls at
  1.4286 m/s in both panels after 0.2913 s and 0.4995 m (closed forms
  5 v0 / 7 = 1.4286 m/s, 0.2913 s, v0 t - 1/2 mu g t^2 = 0.4995 m;
  diffs 2.2e-16, 0, 5.6e-17); that is 0.71429 of the arrival speed
  (5/7 = 0.71429); it settles at x = 0.8795 m, inside the panel, and
  leaves the panel (x > 0.9286 m) 0.3258 s after the hit (2.61 s of
  video at 1/8)
- stop: the top cue ball stays at x = 0.3228 m from the hit to the end
  of the shot (0.8786 s, 7.03 s of video): max |x - x_hit| = 0, max
  |v| = 0, max |spin| = 1.1e-14 rad/s (no slip, so the cloth has
  nothing to act on)
- for the description (same shot, other cloths): mu 0.1: the cue ball
  rolls again at 0.5714 m/s after 0.5827 s and 16.6 cm, the struck
  ball at 1.4286 m/s after 99.9 cm; mu 0.2: 0.2913 s, 8.3 cm and 49.9
  cm; mu 0.3: 0.1942 s, 5.5 cm and 33.3 cm (the fractions do not move
  with mu); same cloth, other speeds: 1 m/s: 0.2857 and 0.7143 m/s
  after 0.1457 s, creep 2.1 cm; 3 m/s: 0.8571 and 2.1429 m/s after
  0.4370 s, creep 18.7 cm
- schedule printed by the sim (first manifest, shot_period 8 s,
  first_shot_at -0.25 s, to be set from the voice timing): launches
  at 7.75, 15.75, 23.75, 31.75, 39.75 s (the first shot launched 0.25
  s before the first frame, its cue balls 6.2 cm into the run-up); the
  hit 0.97 s after each launch at 0.72, 8.72, 16.72, 24.72, 32.72 s;
  the bottom cue ball rolls again 2.33 s after the hit at 3.05, 11.05,
  19.05, 27.05, 35.05 s; the struck ball settles at the same instants
  and leaves the panel 2.61 s after the hit; each shot crossfades to
  the next launch over the last 0.8 s of its period (out over 7.20 to
  7.60 s, in over 7.60 to 8.00 s after the launch, the incoming cue
  balls running in from the left); title until 2.4 s; the title fades
  back in over the last 0.5 s and the last frame repeats the first
- text widths (DejaVuSans-Bold): overlay 912 px at 34; title lines 648
  and 731 px at 56; counter 241 px, panel labels 165 and 146 px, speed
  readout 383 px at 40; legend 777 px, state words 102 to 136 px, cue
  ball tag 123 px at 28; payoff lines 458, 522, 596, 899 and 929 px at
  40 (a first draft of line 5, "0.57 m/s from 2.00 m/s after 8.3 cm
  of creep", measured 1,007 px and was reworded before any render);
  nothing over 950 px; the sim asserts every line under 950 px and
  that the label plus state word (ending at x 426 at most) clears the
  speed readout (from x 597)

Narration numbers: two meters a second (setup; the arrival speed of
both cue balls, on the overlay and the readouts); two sevenths of its
speed (payoff; the measured 0.5714 m/s = 0.28571 of 2.0000 m/s, shown
as "2/7 of its speed" and "0.57 m/s" on the card and "cue ball 0.57
m/s" on the readout). The 5/7 (1.4286 m/s), the 0.2913 s, the 8.3 cm
creep and the 49.9 cm, the launch backspin, the spins and the other
cloths and speeds go to the description (0.29 s and 8.3 cm also on the
card). No number contradicted the claim; the claim text is left as
written (the sim confirms 2/7 = 0.5714 m/s and 5/7 = 1.4286 m/s, 8.3
cm and 49.9 cm at mu 0.2).

### Production

- layout (`sims/cueball/cueball.py`): overlay "two cue balls 2 m/s |
  head on | mu 0.2 | no seed" at y 96 (34 px, teal); the title "Hit a
  ball dead on: / does the cue ball stop?" at y 190 and 252 (56 px) for
  the first 2.4 s, then the counter "shot k of 5" at y 236 (40 px) and
  the legend "no spin at the hit above, rolling below; 1/8 speed" at y
  290 (28 px, muted); two side views stacked at 1200 px per metre (ball
  radius 34.3 px): "no spin" with its readout row at y 380 (the label at
  40 px, the state word "sliding" or "at rest" at 28 px muted beside it,
  ending at x 426 at most, the readout "cue ball 2.00 m/s" at 40 px
  right-aligned at x 980, gold once the cue ball has reached its final
  state) over the cloth line at y 700, and "rolling" with its row at y
  920 (state word "rolling" or "spinning") over the cloth at y 1240; the
  cloth as a teal line over a dark strip with ticks every 0.1 m (the
  strip ends at row 1284); the cue ball a white disc with a coral stripe
  (a great circle seen edge on) and a dark dot that turn with the ball's
  spin, the struck ball a gold disc with a dot; a "cue ball" tag (28 px)
  22 px above each cue ball, its x clamped to 76 px so it stays whole
  while the ball runs in from the left edge; from the hit a white tick
  on the cloth at the hit point and, in the bottom view, a gold creep
  line from the hit point to the cue ball's contact point; each shot
  crossfades to the next over the last 0.8 s of its 8.4 s period (out
  over 7.6 to 8.0 s, in over 8.0 to 8.4 s after the launch, the incoming
  cue balls running in from the left, the struck ball back on its spot);
  geometry band y 400 to 1420 drawn at 2x and reduced, text at 1x;
  captions at caption_y 0.75; the five-line card from y 1592 (40 px,
  gold); loop fade over the last 0.5 s (counter, legend and card out
  over the first 0.25 s, the title in over the last 0.25 s); the last
  frame repeats the first
- whisper pre-tests (10:42:39 to 10:43:30 EEST, before the full take;
  `media/cueball/hooks/`, log `hooks/pretest.log`, onsets in
  `hooks/onsets.log`): five hook variants passed the round trip on their
  first pass: hook1 "Hit the ball dead on. Does the cue ball stop? Two
  cue balls. Two meters a second." (4.74 s), hook2 with a comma after
  "dead on" (5.15 s), hook3 "Hit a ball dead on, does the cue ball stop?
  ..." (4.82 s), hook4 "Dead on, does the cue ball stop? ..." (4.67 s),
  hook5 "A pool shot, dead on. Does the cue ball stop? ..." (5.58 s);
  the setup group (18.19 s) passed; the payoff group "So, does the cue
  ball stop? With no spin, yes, it stops dead. Rolling, no. The cue ball
  rolls on at two sevenths of its speed." failed ("cue" heard as "cube"
  twice and "at" as "a"); reworded to "It rolls on again at two sevenths
  of its speed." (payoff2, 8.38 s, passed; payoff3 "It keeps on rolling
  at ..." 8.64 s and payoff4 "It rolls on again, with ..." 8.73 s also
  passed), payoff2 kept and the "cue ball" mentions in the body cut to
  the ones the story needs; the question onset measured on the hook wavs
  (silencedetect at -35 dB, 0.08 s, plus the 0.6 s offset): after "Hit
  the ball dead on." at 1.85 s (hook1), after "Hit the ball dead on," at
  2.06 s (hook2), after "Hit a ball dead on," at 1.93 s (hook3), after
  "Dead on," at 1.52 s (hook4), after "A pool shot, dead on." at 2.46 s
  (hook5); "Hit a ball dead on." kept as its own 19-character sentence
  (four words before the question, the shot named), and the title and
  the card carry the same words with a colon ("Hit a ball dead on: /
  does the cue ball stop?")
- smoke frames (`--frames`, 10:49 to 10:51 EEST): pass 1 (at 0, 1.7,
  8.97, 10.0, 15.8, 17.4, 25.8, 29.6, 31.0, 41.6, 41.98 s) crashed at
  41.6 s, the frame exactly half way through the crossfade (`draw_panel`
  tested `tau > P - F / 2` and drew no incoming shot, so its tag state
  was None); fixed with `>=`, the frames written before the crash
  deleted; pass 2 found two defects: the "cue ball" tags were drawn 400
  px too high (the geometry layer's y offset was missing) and sat over
  the title and the top cloth, and the title read "Hit the ball dead on"
  while the recorded question is "Hit a ball dead on"; fixed by adding
  the layer offset and by changing the manifest title and the card's
  first line; pass 3 at 10:50:09 EEST (the same 11 instants) clean: the
  title over the run-up on the first frame, the hit at 8.97 s with both
  cue balls stopped and the struck ball leaving, the creep line and "cue
  ball 0.57 m/s" in gold at 10.0 and 31.0 s, the card lit at 29.6 s, the
  HUD dimming at 41.6 s, the last frame equal to the first; the tag's x
  was then clamped to 76 px so it cannot leave the frame while the
  incoming ball runs in, and pass 4 at 10:51:19 EEST (at 7.9 and 41.45
  s, the run-in frames) showed the tag whole at the left edge
- narration (written after the measure-only run, 10:40 EEST;
  `projects/cueball/narration.txt`, 100 words, American spelling): "Hit
  a ball dead on. Does the cue ball stop?" then the setup ("Two cue
  balls. Two meters a second." as its own 20-character chunk with the
  number and the unit together, "No spin on top. Rolling below. Watch
  the stripe."), the hit ("Both hit. Both cue balls stop, and the ball
  takes all of the speed."), the two outcomes ("With no spin, the top
  one stays put. The bottom one keeps its spin. The cloth grabs that
  spin and drags the ball forward again."), "Same hit, same creep, every
  time.", "Now the bottom ball." for the fourth hit, and the payoff "So,
  does the cue ball stop? With no spin, yes, it stops dead. Rolling, no.
  It rolls on again at two sevenths of its speed." (chunks "It rolls on
  again at | two sevenths of its | speed."); chunks() checked before
  recording; "still", "pull", "got", "spread", "straight" alone,
  "brakes", "drifts", "dives", "a hundred", a sentence-initial "Where"
  or "Spin" and "and a half" avoided ("stays put" instead of "stays
  still"); the setup number is the arrival speed, the payoff number the
  fraction; the 5/7, the times and the distances stay on the card and in
  the description
- voice: `scripts/voiceover.sh projects/cueball/narration.txt` take 1 at
  10:48:28 EEST passed the round trip ("ok: transcript matches
  narration", 31.58 s; `media/cueball/voice-take1.log`,
  `timing-take1.log`, `pauses-take1.log`) but its order was wrong for
  the picture: "The ball takes all of the speed and both cue balls
  stop." put "both cue balls stop" 2.4 s after the hit, while the bottom
  ball was already creeping; reordered to "Both cue balls stop, and the
  ball takes all of the speed." and re-recorded; take 2 at 10:48:31 EEST
  passed: 100 words, 31.66 s, ends at 32.26 s of the 42 s video, 3.16
  words/s; log in `media/cueball/voice.log`
- timing (`scripts/voice-timing.py`, +0.6 s offset,
  `media/cueball/timing.log`, with the fine pause table from
  silencedetect at -35 dB, 0.08 s in `pauses.log`): "Hit a ball dead
  on." 0.60 to 1.55, then the pause to 1.69, so the question "Does the
  cue ball stop?" starts at 1.69 s and ends at 2.91; "Two cue balls."
  3.07 to 3.89; "Two meters a second." 4.00 to 5.04; "No spin on top."
  5.18 to 6.20; "Rolling below." 6.41 to 7.28; "Watch the stripe." 7.48
  to 8.33; "Both hit." 8.59 to 9.09 with the second hit at 8.97 s; "Both
  cue balls stop," 9.34 to 10.47; "and the ball takes all of the speed."
  10.74 to 12.27; "With no spin," 12.40 to 13.14; "the top one stays
  put." 13.49 to 14.69; "The bottom one keeps its spin." 14.92 to 16.50;
  "The cloth grabs that spin and drags the ball forward again." 16.71 to
  20.02 with the third hit at 17.37 s and the creep to 19.70 s; "Same
  hit," 20.18 to 20.75; "same creep," 21.05 to 21.70; "every time."
  21.94 to 22.51; "Now the bottom ball." 22.75 to 23.70; "So," 23.82 to
  24.16; "does the cue ball stop?" 24.31 to 25.57; "With no spin," 25.73
  to 26.53 with the fourth hit at 25.77 s; "yes," 26.83 to 27.24; "it
  stops dead." 27.35 to 28.19; "Rolling, no." 28.46 to 29.23 with the
  bottom ball rolling again at 28.10 s; "It rolls on again at" 29.48 to
  30.63; "two sevenths of its speed." 30.71 to 32.08; the per-piece
  transcript merged some pieces across the coarse 0.22 s splits ("with
  no spin," into the previous piece, "So." as its own piece; pause
  splits, not mishearings; the full-file round trip matched)
- schedule decisions: shot_period 8.4 s, first_shot_at -0.4 s and
  scene_duration 42 s (5 shots, an integer length in the 40 to 42 s
  range) from the take-2 timing: the first hit at 0.57 s under the title
  during "Hit a ball dead on." (the cue balls are 10 cm into the run-up
  on the first frame, motion in progress for the thumbnail; the top ball
  stops and the bottom ball creeps while the question is asked); the
  hits at 8.97 s inside "Both hit." (8.59 to 9.09), 17.37 s inside "The
  cloth grabs that spin" with the creep to 19.70 s under "drags the ball
  forward again", 25.77 s inside "With no spin," (25.73 to 26.53) so the
  top ball's dead stop sits under "yes, it stops dead", and 34.17 s
  after the voice; the bottom ball rolls again at 28.10 s, just before
  "Rolling, no." (28.46 to 29.23), so the readout "cue ball 0.57 m/s"
  turns gold before the answer; payoff_t 28.9 s with a 0.6 s fade, so
  the card is fully lit at 29.5 s, after "Rolling, no." and before "two
  sevenths of its speed" (30.71 to 32.08); the creep line and the 0.57
  m/s readout hold to the crossfade at 32.4 s, so the payoff number is
  on screen for the whole payoff sentence; the struck ball leaves each
  view 2.61 s after the hit and is back on its spot with the next launch
- footage: `sims/cueball/cueball.py` (no arguments) wrote
  `media/cueball/footage.mp4`, 42.00 s at 60 fps, 2,520 frames, h264 crf
  16 yuv420p, in 39 s with eight forked workers, 10:52:09 to 10:52:48
  EEST; the same run re-printed every measurement above
  (`media/cueball/render.log`); loop check on the raw frames: the last
  frame differs from the first in 0 px (max channel difference 0);
  periodicity check: the scene drawn live at 42 s differs from 0 s in 0
  px; the frame before the last differs from the last in 8,656 px (the
  incoming cue balls are still fading in on that frame)
- compose: `scripts/compose.sh cueball` (10:52:55 to 10:53:36 EEST)
  wrote `media/cueball/final.mp4` (h264 1080x1920 60 fps, 2,520 frames,
  aac 22050 Hz mono, 42.000 s, 3,031,432 bytes; music seed 84 at gain
  0.18; captions at caption_y 0.75, 31 drawtext filters, the overlay
  plus 30 caption chunks); loudness mean -16.3 dB, peak -0.0 dB; preview
  (42.07 s) and the 8x6 contact sheet written
  (`media/cueball/compose.log`)

### Local QA

- smoke passes 1 to 4 (10:49 to 10:51 EEST, `--frames` before any
  render): three defects found and fixed (the crash on the crossfade's
  middle frame, the "cue ball" tags 400 px too high, the title wording)
  and the tag clamp added; pass 3 (10:50:09 EEST) clean, pass 4
  (10:51:19 EEST) confirmed the clamp on the run-in frames
- final pass (10:54 to 10:58 EEST): frames at 0.02, 1.7, 9.0, 12.0,
  17.5, 25.9, 29.6, 31.0, 41.6 and 41.98 s extracted from final.mp4
  (`media/cueball/frame-*.png`) and inspected with the 8x6 contact sheet
  (`media/cueball/sheet.png`): 0.02 s shows the overlay "two cue balls 2
  m/s | head on | mu 0.2 | no seed" at y 96, the title "Hit a ball dead
  on: / does the cue ball stop?" at y 190 and 252 clear of it, both
  views with the cue balls 10 cm into the run-up ("cue ball 2.13 m/s"
  sliding above, "cue ball 2.00 m/s" rolling below), the stripes turned
  differently, the struck ball 30 cm ahead, no caption yet (the
  thumbnail); 1.7 s shows the caption "Hit a ball dead on." under the
  title with the first hit done: the top cue ball at rest on the hit
  tick with "cue ball 0.00 m/s" in gold, the bottom one "spinning" at
  0.28 m/s with the gold creep line, the struck balls leaving; 9.0 s
  shows "shot 2 of 5" and the legend in place of the title, the second
  hit with both cue balls touching the struck balls, the bottom readout
  0.01 m/s, under "Both hit."; 12.0 s shows the bottom cue ball
  "rolling" at 0.57 m/s in gold at the end of its creep line, the top
  one at rest, the struck balls gone, under "all of the speed."; 17.5 s
  shows the third hit just done (bottom "spinning" 0.03 m/s) under "its
  spin."; 25.9 s shows the fourth hit just done under "ball stop?"; 29.6
  s shows the card "hit a ball dead on: / does the cue ball stop? / no
  spin: yes, it stops dead / rolling: no, it rolls on at 2/7 of its
  speed / 0.57 m/s after 0.29 s and 8.3 cm of creep" fully lit with "cue
  ball 0.57 m/s" in gold and the creep line, under "It rolls on again
  at"; 31.0 s the same with the ball further on, under "two sevenths of
  its speed"; 41.6 s shows the loop fade starting (counter, legend and
  card dimming, the incoming cue balls at the left edge with their tags
  whole, "cue ball 2.24 m/s" sliding and 2.00 m/s rolling); 41.98 s
  shows the title frame (the last frame equals the first); captions
  match the narration word for word (the contact sheet reads every chunk
  in order) and sit in rows 1440 to 1501; the footage has nothing in
  rows 1420 to 1530 on any of ten instants checked (0, 1.7, 8.97, 12.0,
  17.4, 25.8, 29.6, 31.0, 41.6, 41.98 s), the lowest geometry row is
  1284 (the bottom cloth's tick strip) and the card's glyphs occupy rows
  1576 to 1837; the text and ball columns span 103 to 977 on normal
  frames, 78 to 1002 with the card (its widest line 929 px) and 18 to
  1002 at 41.6 s (the clamped tag at the left edge, 123 px wide, centred
  at x 76), nothing clips; the payoff number is on screen when spoken
  (the readout "cue ball 0.57 m/s" gold from 28.10 s, the card from 29.5
  s, "two sevenths of its speed" spoken 30.71 to 32.08, caption "two
  sevenths of its" 30.68 to 31.94); the question starts at 1.69 s with
  the title on screen from frame 0 (the question caption runs from 2.18
  s: the chunks are timed by their share of the take's characters, so
  this one lags the voice by half a second, and the title carries the
  words); the loop closes: the raw last frame differs from the raw first
  frame in 0 px (render.log), and on the encoded final frame 2519
  differs from frame 0 in 2,242 px by more than 24 levels (0.11 percent,
  max channel difference 88, mean 0.28, encoder noise); ffprobe: h264
  1080x1920, 60/1 fps, 2,520 frames (also by decode), aac 22050 Hz mono,
  42.000000 s, 3,031,432 bytes, atoms ftyp, moov, free, mdat (moov
  before mdat), md5 f0f92de6979b8a05f482fa53ed1f4531; loudness mean
  -16.3 dB, peak -0.0 dB; approved locally
- measure.log refreshed at 10:58:30 EEST with the final manifest
  (shot_period 8.4, first_shot_at -0.4, scene_duration 42, the "Hit a
  ball" title, the reworded payoff line 5); the 10:39:07 run kept as
  `media/cueball/measure-1039.log`; every physical number identical,
  only the schedule line, the stop window (0.9286 s, 7.43 s of video),
  the title line 1 width (582 px) and the payoff line 1 width (410 px)
  changed

### Metadata

- `projects/cueball/metadata.json`: title "Hit a ball dead on at 2 m/s:
  does the cue ball stop? No spin: dead stop. Rolling: 2/7 of its speed"
  (98 characters); description (3,146 characters, no < or >) with the
  setup (two cue balls at 2 m/s into a ball at rest, the stun shot's
  20.8 rad/s of backspin launched at 2.24 m/s 31.4 cm behind the ball,
  the rolling ball's 69.9 rad/s, equal masses, I = 2/5 m R^2, radius
  28.6 mm, the elastic head-on hit that swaps speeds and keeps spins, mu
  0.2, exact piecewise integration checked against the closed forms, 1/8
  speed, 5 shots in 42 s, no seed), a Measured list (the 2.0000 m/s
  arrivals with spins 0 and 69.930 rad/s, the swap with momentum and
  energy 2.0000 = 2.0000, the top ball's drift 0, the 0.5714 m/s after
  0.2913 s and 8.3 cm as exactly 2/7 with the spin falling to 19.980
  rad/s, the struck ball's 1.4286 m/s = 5/7 after 49.9 cm, the mu 0.1
  and 0.3 and the 1 and 3 m/s variants), a Why paragraph in plain words
  (the hit only trades speed; no spin, nothing left, a dead stop; the
  rolling ball keeps its spin, the cloth rubs on it and pushes the ball
  forward until it rolls; the push acts at the contact point so the
  turning about that point is kept, 2/5 against 7/5, hence 2/7 whatever
  the cloth; stop, stun and follow named), the rerun line and the
  AI-made line; 10 tags (cue ball, stop shot, follow shot, pool physics,
  billiards, does the cue ball stop, physics, physics visualization,
  simulation, shorts); category 27; private; containsSyntheticMedia
  true; selfDeclaredMadeForKids false; the same keys in the same order
  as projects/merrygoround/metadata.json
- not uploaded; task left open for the orchestrator's review and upload

### Release
- orchestrator review (11:12 EEST): the task evidence, the 8x6 contact
  sheet and the full-resolution frames at 0.02, 12.0 and 29.6 s
  inspected: the question "Hit a ball dead on: / does the cue ball
  stop?" over both views from frame 0 with the cue balls already in
  their run-up ("cue ball 2.13 m/s" sliding above, "cue ball 2.00 m/s"
  rolling below, the red stripes turned differently, the orange struck
  ball 30 cm ahead; the thumbnail); 12.0 s shows shot 2 with the top cue
  ball at rest on the hit tick ("cue ball 0.00 m/s") and the bottom one
  "rolling" at "cue ball 0.57 m/s" in gold at the end of its creep line,
  the struck balls gone off the right edge; 29.6 s shows the card "hit a
  ball dead on: / does the cue ball stop? / no spin: yes, it stops dead
  / rolling: no, it rolls on at 2/7 of its speed / 0.57 m/s after 0.29 s
  and 8.3 cm of creep" lit under the caption "It rolls on again at"; the
  narrated numbers (two meters a second, two sevenths of its speed)
  match the 2.0000 m/s arrival and 0.5714 = 2/7 in
  media/cueball/measure.log; the stun run-up (launched at 2.24 m/s with
  20.8 rad/s of backspin, spin 0 at the hit) is stated in the
  description and the legend names the 1/8 speed; captions sit in the y
  1440 to 1501 band clear of the geometry; final.mp4 h264 1080x1920 60
  fps, 2,520 frames, aac 22050 Hz mono, 42.000 s (scene_duration 42, so
  the gate accepts PT42S or PT43S), moov before mdat, md5
  f0f92de6979b8a05f482fa53ed1f4531; title 98 characters; the
  description carries no < or >; approved for release
- quota check: clock 2026-09-25T11:11:51+03:00; one upload attempt (spool, 11:10:07,
  published as 5xhaVWmicBI at 11:11:07) recorded since the 2026-09-25
  10:00 EEST boundary (log entries and media/*/upload.log both checked);
  this is insert attempt 2 of the hard cap of 5
- attempt 2 recorded at 2026-09-25T11:11:51+03:00, video name cueball, before running
  `scripts/yt-upload.py cueball`

### Published
- upload: `scripts/yt-upload.py cueball` (attempt 2) ran 11:11:51 to
  11:11:57 EEST, token verified to see only the Seed Zero channel, video
  id pcnwZnIKhh0, private (`media/cueball/upload.log`)
- gate: `scripts/yt-qa.py cueball pcnwZnIKhh0 --wait --publish` ran in
  the foreground from 11:12:03 EEST: processing succeeded and the 10 tags
  read back within the first minute of polling, 15 of 15 pass
  (processed, succeeded, hd, 1080x1920, title, description, tags as a
  set, category 27, not for kids, PT43S for the 42.000 s file, private);
  containsSyntheticMedia reads absent as on every earlier upload
  (`media/cueball/publish.log`)
- publish: the same run set the video public at 2026-09-25T11:12:52+03:00;
  the re-read after 15 s shows privacyStatus public, madeForKids false,
  embeddable true; public at https://youtu.be/pcnwZnIKhh0
- slot resolution: published for the 2026-09-25 quota day

### Quota
- attempt 2 of the hard cap of 5 for the quota day that began
  2026-09-25T10:00 EEST; cost 1 + 1,600 + 55 = 1,656 units (the
  channels.list verification inside yt-upload.py, the insert, the gate
  run's reads, update and re-read as printed by yt-qa.py); day total after
  two attempts 3,312 units plus 5 for the 10:18 stats refresh

### Repository
- committed as 2f677a4 "Publish the day twenty-seven slate" (sims,
  projects, tasks, docs/niche.md, web/data; no media, previews or
  secrets) and pushed to origin/master at 2026-09-25 11:17 EEST
