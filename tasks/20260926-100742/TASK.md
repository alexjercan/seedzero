# Produce short: Falling folded chain, the chain tip beside a ball over the same 1 m drop

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day28

## Goal

Backlog idea (trend research 2026-09-25, task 20260925-101408, pillar 2
chaos and physics, falling; read the full entry under "Added by trend
research 2026-09-25" in docs/niche.md):
"Falling folded chain: a 1 m chain folded in half with one end held,
the free end let go beside a ball dropped from the same height;
measure the time each takes to fall 1 m; expect the chain tip at 0.383
s against the ball's 0.452 s (84.7 percent, a 69 ms lead), the ball
still 28 cm up when the tip arrives, the tip at 3.8 m/s halfway down
against the ball's 3.1 (v^2 = g x (2L - x) / (L - x), Calkin and
March; RK4 to 0.9 L matches to four decimals); the tip speed runs away
in the last centimetres, so cap the drawing at the fold and say the
real chain whips; repeat the drop; deterministic, no seed."

Orchestrator notes (2026-09-26, before this brief). The model: a
uniform chain of length L = 1.00 m, one end held fixed at the top, the
chain folded so that the free end starts level with the held end and
the fold hangs L / 2 below them. At t = 0 the free end is released.
With the free end fallen a distance x the fixed side is a straight
hanging length (L + x) / 2 and the free side a straight length (L - x)
/ 2 rising from the fold to the free end, so the fold sits (L + x) / 2
below the top and moves at half the tip speed. Energy-conserving model
(Calkin and March 1989, the model that experiments confirm): the free
end's speed obeys v^2 = g x (2L - x) / (L - x); differentiating gives
the tip acceleration a = g (1 + x (2L - x) / (2 (L - x)^2)), which is
g at release and grows without bound as x nears L. Integrate x(t) by
RK4 at 10,000 steps a second or finer to 0.9 L and check it against
the closed form to four decimals; take the tail (0.9 L to L) from the
quadrature t = integral dx / v, which converges because v grows like
1 / sqrt(L - x). The ball is a point mass dropped from rest at the same
height as the free end, no air, y = g t^2 / 2 (draw it with a radius,
say 3 cm, but measure its centre). g = 9.81 m/s^2.

State every derived number below as a check the sim must print, not as
a fact: chain tip 1.00 m in 0.3824 s, ball in 0.4515 s (sqrt(2 L / g)),
the chain at 84.7 percent of the ball's time, a 69 ms lead; the ball
has fallen 0.717 m and is still 0.283 m up when the tip lands; the tip
at 3.84 m/s at x = 0.5 m against the ball's 3.13 m/s at the same
depth; time to 0.9 L 0.3755 s, to 0.99 L 0.3820 s, to L 0.3824 s (so
the cap changes the fall time by less than a millisecond); the tip
acceleration at x = 0.5 m is g (1 + 0.5 x 1.5 / (2 x 0.25)) = 2.5 g.
Print the times at which the drawing cap applies (see below) and the
tip speed there.

Drawing: the chain as a chain of links (about 40 links of 2.5 cm, or a
thick line with link marks) along the two straight sides and a small
half-circle at the fold; the ball beside it at the same scale, both
released from the same start line, both measured to the same finish
line 1.00 m below; a scale bar. Cap the drawing: once the free side is
shorter than one link (x > L minus one link), draw the chain fully hung
with the tip at x = L and print the time at which the cap applies; say
in the description that the model's tip speed runs away in the last
centimetres and a real chain whips and loses energy there, and that
the fall time to 0.99 L (0.3820 s) is within a millisecond of the time
to L. Slow motion: the fall takes under half a second, so show it at
1/8 speed (3.6 s for the ball) or a rate that reads well; freeze or
mark the ball's position at the moment the tip lands ("28 cm up") and
let the ball land 69 ms (0.55 s at 1/8 speed) later; then reset and
repeat the drop so the scene is periodic and the last frame equals the
first; print the schedule in video time and the loop check.

Day twenty-eight, first slot. Chosen because it is a which-lands-first
race on one drop (the rolling race 950 and the hinged stick 734 are the
family), two things released at the same instant that arrive apart, a
closed form the sim checks, and no seed. Question in the first two
seconds: "Drop a folded chain beside a ball. Which lands first?" (or
the producer's better wording; the words before the question count,
keep them under nine; keep the question identical in the title, the
hook and the payoff). Setup number: one meter (both fall one meter).
Payoff number: twenty eight centimeters (the chain tip lands with the
ball still twenty eight centimeters up); or the two times if the
producer's timing check prefers them, written so the voice reads them
well. The 0.38 s against 0.45 s, the 85 percent, the 69 ms and the 3.8
against 3.1 m/s go to the card and the description. Make the last
frame equal the first. Measure every fixed text line with PIL before
rendering and keep every line under 950 px. Music seed 86.

## Claim

A one meter chain folded in half with one end held, its free end let
go beside a ball dropped from the same line at the same instant: the
chain tip reaches the finish line one meter down in 0.383 s, the ball
in 0.452 s (the chain in 84.7 percent of the ball's time, a 69 ms
lead), and when the tip lands the ball is still 28 cm up. Halfway down
the tip already moves 3.84 m/s against the ball's 3.13 m/s. Every
number in the narration is printed by the sim before the script is
written (the sim sets the claim).

## Evidence

### Measurements

(recorded after the measure-only run, before scripting)

`sims/chain/chain.py --measure-only` with `projects/chain/manifest.json`
(a uniform chain of 1.00 m, 40 links of 2.5 cm, folded in half from a
peg, one end held at the top, the free end level with it and the fold
0.5 m below; a ball of radius 3 cm, a point mass measured at its centre,
beside it at the same start line; both let go at the same instant and
measured to the same finish line 1.00 m below; no air; g 9.81 m/s^2;
the tip follows v^2 = g x (2L - x) / (L - x) (Calkin and March, energy
conserving), a = g (1 + x (2L - x) / (2 (L - x)^2)), integrated by RK4
at 10,000 steps per second to 0.9 L and checked against the quadrature
t = integral dx / v with the endpoint singularities removed (x = s^2
below 0.9 L, u = sqrt(L - x) above it; Simpson, 200,000 intervals per
piece); the ball y = g t^2 / 2; shown at 1/8 speed; drawn at 740 px per
metre; deterministic, no seed; run at 10:19:06 EEST, log in
`media/chain/measure.log`):

- fall times: the chain tip reaches 1.00 m in 0.3825 s (0.382537 s;
  the brief's 0.3824 is the same number rounded down, 0.1 ms apart)
  and the ball in 0.4515 s (sqrt(2 L / g) = 0.45152); the chain takes
  84.7 percent of the ball's time, a 69.0 ms lead; when the tip lands
  the ball has fallen 0.718 m and is 0.282 m up (28 cm to the nearest
  centimetre, 28.2 cm); the trapezoid table used for drawing gives
  0.382537 s, within 3e-12 s of Simpson
- RK4 check: 3,758 steps of 1e-4 s from rest to 0.9 L; the speed stays
  within 1.0e-9 m/s of the closed form along the way; the tip passes
  0.5 L at 0.30268 s at 3.83601 m/s (quadrature 0.30268 s, closed form
  3.83601 m/s; diffs 4.9e-9 s and 1.1e-7 m/s) and 0.9 L at 0.37579 s at
  9.85493 m/s (quadrature 0.37579 s, closed form 9.85490; diffs 2.0e-8 s
  and 2.8e-5 m/s): RK4 matches the closed form to four decimals; the
  ball stepped at the same dt lands at 0.45152 s (diff 2.0e-9 s) at
  4.429 m/s
- speeds at the same depth: 0.25 m tip 2.39 m/s (0.2206 s) against the
  ball 2.21 m/s (0.2258 s); 0.50 m tip 3.84 m/s (0.3027 s) against 3.13
  m/s (0.3193 s); 0.75 m tip 6.07 (0.3556 s) against 3.84 (0.3910 s);
  0.90 m tip 9.85 (0.3758 s) against 4.20 (0.4284 s); 0.95 m tip 13.99
  (0.3802 s) against 4.32 (0.4401 s); 0.99 m tip 31.32 (0.3823 s)
  against 4.41 (0.4493 s); the tip acceleration at 0.5 L is 24.525
  m/s^2 = 2.50 g (g at release, unbounded as x nears L); halfway: the
  tip passes 0.5 L at 0.3027 s when the ball has fallen 0.449 m, so the
  tip is 0.051 m (5 cm) ahead and moving 3.84 m/s against the ball's
  2.97 m/s at that instant
- tail and cap: time to 0.9 L 0.3758 s, to 0.99 L 0.3823 s, to L 0.3825
  s (the last centimetre takes 0.21 ms); the drawing cap (the free side
  shorter than one link, x > 0.975 m) applies from 0.3817 s, 0.84 ms of
  real time (6.7 ms of video, 0.40 frames) before the tip lands, where
  the model's tip speed is 19.8 m/s (4.5 times the ball's speed at that
  depth); the cap changes the drawn fall time by under a millisecond
- schedule printed by the sim (first manifest, release_at 0.6, drop
  period 8 s, hold 2.4 s, fades 0.5 s, to be set from the voice timing):
  releases at 0.60, 8.60, 16.60, 24.60, 32.60 s; the tip lands 3.060 s
  after each release, the ball 3.612 s after (0.552 s later); the ball's
  position at the tip's landing is marked "28 cm up" from the tip's
  landing until the fade; on the first frame both sit at the start line
  0.60 s before the first release; the scene is periodic (40 s holds
  exactly 5 drops)
- text widths (DejaVuSans-Bold): overlay 874 px at 34 (the first draft
  "1 m chain folded in half beside a ball | 1/8 speed | no seed"
  measured 1117 px and was shortened before any render); title lines
  619, 423 and 565 px at 56 (the one-line "Drop a folded chain beside a
  ball." measured 1062 px, so the title is three lines); legend 657 px
  at 40, tag 709 px at 28; labels 121 and 83 px, clock 164 px at 40;
  readouts 316, 312, 305 and 320 px, gap tag 144 px, scale 58 px, fixed
  lines 649 and 687 px at 28; payoff lines 755, 620, 790 and 738 px at
  40; nothing over 950 px; the sim asserts every line under 950 px

Narration numbers: one meter (setup; both fall one meter, on the overlay
"1 m drop", the legend and the scale bar); twenty eight centimeters
(payoff; the ball is 0.282 m up when the tip lands, 28 cm to the nearest
centimetre). The 0.38 s against 0.45 s, the 69 ms, the 85 percent and
the 3.84 against 3.13 m/s go to the fixed lines, the card and the
description.
### Production

- layout (`sims/chain/chain.py`): overlay "chain and ball, 1 m drop |
  1/8 speed | no seed" at y 96 (drawn by compose from the manifest);
  title "Drop a folded chain / beside a ball. / Which lands first?" at y
  200/262/324 (56 px, three lines because the one-line form measured
  1062 px) for the first 3 s, then the legend "both fall 1 m, let go
  together" at y 236 (40 px) and the tag "1/8 speed, no air, ball
  measured at its center" at y 290 (28 px, muted); labels "chain" and
  "ball" at y 405 over the columns and the live clock right-aligned at
  x 1020; the start line at y 460 from x 200 to 940 with the peg at x
  420, the finish line 740 px below at y 1200, the 1 m scale bar at x
  150; the chain as 40 alternating ellipse links (flat 1.6 cm, edge 0.7
  cm, 2.1 cm long, outline 3 px at 2x) down the held side at x 405 and
  up the free side at x 435 (strand gap 4 cm) with a half-circle at the
  fold, a gold dot on the tip; the ball (radius 3 cm, teal) at x 720;
  once the tip lands a gold tick on the finish line, a dashed gold
  ghost ring at the ball's height at that instant with a gold bar and
  "28 cm up" beside it, the ball itself going on to its own landing
  with a teal tick; readouts at y 1250, the tip's left-aligned at x 200
  ("tip 0.36 m, 3.0 m/s", then "tip lands at 0.383 s" in gold) and the
  ball's right-aligned at x 940 ("ball 0.34 m, 2.6 m/s", then "ball
  lands at 0.452 s" in teal), so the two never meet; the fixed lines
  "halfway down: tip 3.84 m/s, ball 3.13 m/s" / "chain tip 0.383 s,
  ball 0.452 s: a 69 ms lead" at y 1300/1336 (28 px, shown with the
  legend from 3 s); geometry band y 380 to 1420 drawn at 2x and
  reduced, coordinates rounded to 1e-4 px; captions at caption_y 0.75
  (y 1440 to 1520); the four-line card from y 1592 (40 px, 56 px
  pitch); each pair fades out over 0.4 s after its hold and the start
  state fades in over 0.4 s; the HUD fades out and the title back in
  over the last 0.5 s, the last frame equal to the first
- whisper pre-tests (10:22:13 to 10:22:25 EEST, `media/chain/hooks/`,
  log `hooks/pretest.log`): every passage passed on its first pass:
  hook1 "Chain beside a ball. Which lands first? The chain is folded in
  half, one end held." (5.28 s), hook2 "A chain beside a ball. Which
  lands first? ..." (5.45 s), hook3 "Chain or ball, which lands first?
  ..." (4.79 s), hook4 "A folded chain, a ball. Which lands first? ..."
  (5.47 s), the mechanism group "Both fall one meter ... and the lead
  keeps growing." (17.12 s, with "tugs on it" and "ahead of the ball",
  both later changed, see voice) and the payoff group "Now watch the
  finish line. So, which lands first? The chain. ... Every drop, the
  same." (9.68 s; the number came back as "28"); question onsets from
  silencedetect on the hook wavs (-35 dB, 0.08 s, plus the 0.6 s
  offset; `media/chain/onsets.log`): hook1 1.90 s, hook2 2.07 s, hook3
  1.54 s, hook4 2.11 s; hook1 kept (four words before the question,
  "beside a ball" the same words as the title); hook3 is quicker but
  its "Chain or ball," breaks the title's wording; the brief's spoken
  "Drop a folded chain beside a ball." (seven words) would have put the
  question near 2.7 s, so the on-screen title keeps the brief's words
  and the voice opens with "Chain beside a ball."
- narration (`projects/chain/narration.txt`): 102 words, 14 sentences,
  "one meter" (setup) and "Twenty eight centimeters" (payoff) the two
  claim numbers, both in words; "shown eight times slower" names the
  playback rate (the overlay's 1/8 speed), not a measurement; no
  "still", "pull", "spread", "straight", "a hundred", "metres",
  "brakes", "drifts", "games", "let's", bare "Where", "Spin" or "Swing"
  first, no decimals (the whisper mishearing list); "So, which lands
  first?" of the pre-test became "Which lands first?" so the payoff
  question is one caption chunk identical to the hook
- smoke frames (`--frames`, six passes 10:24 to 10:35 EEST, log
  `media/chain/smoke.log`): pass 1 (10:24:31; 0, 1.5, 1.99, 2.9, 4.2,
  4.4, 6.5, 7.2, 7.6, 12.0, 19.42, 28.1, 29.0, 30.5, 39.6, 39.98 s)
  found the two readouts colliding under the finish line once the tip
  had landed ("tip lands at 0.383 s" ran into "ball 0.89 m, ...") and
  the links too thin to read at 1080 px; fixed by anchoring the tip
  readout left at x 200 and the ball readout right at x 940 and by
  thickening the links; pass 2 (10:25:38) clean; pass 3 (10:26:36, with
  the schedule set from the voice timing, at 18.66, 27.35, 28.0, 30.0 s
  among others) clean, then the first footage render; pass 4 (10:33:32,
  after the release list replaced the fixed period: 7.9, 10.5, 12.0,
  13.5, 15.6, 16.1, 18.66, 27.35, 30.0, 39.98 s) showed the second
  drop's fade-in ending at its release instant (start hold 0.00 s);
  fixed with start_hold_min 0.3; pass 5 (10:33:55) and pass 6 (10:35:07,
  the final sim and manifest) clean: the fold moving at 10.5 and 12.0
  s, the tip landed at 13.5 s, the landed pair fading at 15.4 s, the
  start state at 16.1 s, halfway at 18.66 s, the card lit at 27.35 s,
  the "28 cm up" mark at 30.0 s, the title back at 39.98 s
- voice (`scripts/voiceover.sh chain`, log `media/chain/voice.log`):
  pass 1 at 10:23:07 EEST failed the round trip (whisper wrote "t ugs"
  for "tugs"); pass 2 at 10:24:25 with the same text failed the same
  way and heard "a" for "the" in "ahead of the ball"; pass 3 at
  10:24:54 with "the fold tugs on it as well" changed to "the fold drags
  it down as well" and "already ahead of the ball" to "already ahead"
  passed, "ok: transcript matches narration (32.055147s)"; voice.wav
  32.06 s, ends at 32.66 s of video with the 0.6 s offset
- timing (`scripts/voice-timing.py media/chain/voice.wav`, log
  `media/chain/timing.log`, video time): "chain beside a ball." 0.60 to
  1.77, the question "which lands first" from 1.77 (the pause after
  "ball" spans 1.61 to 1.93 s in video time, silencedetect 1.011 to
  1.332 s in the wav, so the word "Which" sounds at 1.93 s), "the chain
  is folded in half" to 4.64, "one end held, both fall one meter." 4.64
  to 6.95, "Let go at the same instant." 6.95 to 8.65, "shown eight
  times slower" 8.65 to 10.09 (heard "Shonei", harmless: the gate is
  the full-file round trip), "Watch the fold as it moves down." 10.09
  to 12.45, "The falling side gets shorter ... Halfway down," 12.45 to
  19.67, "The tip is already ahead." 19.67 to 21.26, "And the lead keeps
  growing. Now watch the finish line." 21.26 to 24.31, "which lands
  first, the chain." 24.31 to 26.49, "When its tip lands" 26.49 to 27.83
  (heard "lens" in this pass only), "The ball is not down yet. 28
  centimeters to go." 27.83 to 31.00, "Every drop." 31.00 to 31.91,
  "The same." 31.91 to 32.66
- schedule (manifest, printed in `media/chain/measure.log`): a release
  list instead of the brief's fixed period, releases at 0.24, 9.90,
  16.24, 24.24, 32.24 s; the tip lands 3.060 s after each release (3.30,
  12.96, 19.30, 27.30, 35.30 s) and the ball 3.612 s after (3.85, 13.51,
  19.85, 27.85, 35.85 s), 0.552 s later; hold_after_ball 3.2 s clipped
  per drop to its gap (3.20, 1.63, 3.20, 3.20, 3.20 s) with reset_fade
  0.4 s and start_hold_min 0.3 s (start holds 2.05, 0.30, 0.39, 0.39,
  0.39 s); the first frame is the start state 0.24 s before the first
  release, which is also the state 8.00 s after the last release, so
  the scene is periodic; drop 2 at 9.90 s keeps the fold moving under
  "Watch the fold." (caption 10.03 to 10.97) and "As it moves down,"
  (10.97 to 12.23) and lands its tip at 12.96 s inside "the falling
  side" (12.23 to 13.17); the rest of that sentence ("gets shorter and
  lighter, and the fold drags it down as well", 13.17 to 16.94) plays
  over the landed pair and its fade, because the fall is 3.06 s of
  video at the brief's 1/8 speed and the sentence runs 6 s; drop 3 at
  16.24 s passes halfway at 18.66 s under "faster than the" (18.51 to
  19.46) and "Halfway down, the" (19.77 to 20.71) with the tip still in
  the air until 19.30 s; drop 4 at 24.24 s lands its tip at 27.30 s
  inside "When its tip lands," (26.68 to 27.94), the ball lands at
  27.85 s, and the "28 cm up" mark stays until the fade at 31.05 s,
  through "Twenty eight" (29.83 to 30.45) and most of "centimeters to
  go." (30.45 to 31.40); title_until 3.0 (the caption "Which lands
  first?" runs 1.86 to 2.80 s); payoff_t 26.6 with a 0.6 s fade, so the
  card is fully lit at 27.2 s, before "Twenty eight"
- footage (`nix develop -c python3 sims/chain/chain.py`, log
  `media/chain/render.log`): the first render ran after the 10:26 smoke
  pass with release_at 0.24 and drop_period 8 (its render and compose
  logs were overwritten by the final run); its QA frame at 12.0 s
  showed the caption "As it moves down," over an already landed chain
  (that schedule released drop 2 at 8.24 s, tip down at 11.30 s), so the
  manifest's fixed period was replaced by the release list above and
  the sim re-rendered 10:35:09 to 10:35:39 EEST: loop check 0 px,
  periodicity check 0 px, loop step 0 px (the first and last frames are
  both the held start state); 2,400 frames, eight forked workers, h264
  crf 16 yuv420p 60 fps, footage.mp4 2,116,842 bytes, 40.00 s;
  `--measure-only` re-run into `media/chain/measure.log` at 10:35:07
  EEST with the final manifest and sim (same numbers as the 10:19 run)
- compose (`scripts/compose.sh chain`, log `media/chain/compose.log`):
  final run 10:35:39 to 10:35:53 EEST: music seed 86 at 40.00 s (gain
  0.18), 34 caption chunks (longest 20 characters, "Twenty eight" one
  chunk), final.mp4 2,708,809 bytes 40.000000 s, preview.mp4 540x960 30
  fps 878,006 bytes 40.066667 s, sheet.png 8x5 at 1 fps 419,428 bytes
- text widths (measure.log, PIL at the drawn sizes): as listed under
  Measurements, overlay 874, title 619/423/565, legend 657, tag 709,
  fixed lines 649 and 687, card lines 755/620/790/738 px, all under 950
  px and asserted by the sim

### Local QA

- frames (`media/chain/frame-<t>.png` from final.mp4 at 0.02, 2.0,
  12.0, 15.4, 18.66, 27.35, 30.0 and 39.98 s, plus `sheet.png`)
  inspected: 0.02 s: overlay and the three-line title from frame 0, the
  folded chain hanging from the peg with its gold tip at the start line
  beside the ball, clock 0.000 s, readouts "tip 0.00 m, 0.0 m/s" and
  "ball 0.00 m, 0.0 m/s", the caption band empty; 2.0 s: caption "Which
  lands first?" in the band, the title still up, the free side halfway
  down its fold (tip 0.25 m, 2.4 m/s) and the ball level with it (0.24
  m, 2.2 m/s), clock 0.220 s; 12.0 s: caption "As it moves down," with
  the legend, tag and fixed lines in place of the title, the fold
  moving (tip 0.36 m, 3.0 m/s; ball 0.34 m, 2.6 m/s; clock 0.262 s);
  15.4 s: caption "fold drags it down", the landed pair fading (dimmed
  clock 0.452 s, "tip lands at 0.383 s", "ball lands at 0.452 s", the
  ghost ring and "28 cm up" bar); 18.66 s: caption "faster than the",
  the tip exactly halfway ("tip 0.50 m, 3.9 m/s") with the ball 5 cm
  behind ("ball 0.45 m, 3.0 m/s"), clock 0.303 s; 27.35 s: caption
  "When its tip lands,", the chain fully hung with the gold tick on the
  finish line and "tip lands at 0.383 s", the ball still in the air
  inside its dashed ghost ring ("ball 0.74 m, 3.8 m/s"), the "28 cm up"
  bar beside it, the card "drop a folded chain beside a ball: / which
  lands first? the chain / tip 0.38 s, ball 0.45 s, a 69 ms lead / ball
  28 cm up when the tip lands" lit under the caption; 30.0 s: caption
  "Twenty eight", both landed ("ball lands at 0.452 s"), the ghost ring
  and "28 cm up" bar still up, the card lit; 39.98 s: the title back
  and the HUD gone, matches 0.02 s; the contact sheet shows the
  captions in narration order, a moving pair in the second and third
  thumbnails of each 8 s cycle, the "28 cm up" mark on every landed
  thumbnail and the card from 27 s to 39 s
- question inside two seconds: the title carries the question from
  frame 0; the narration reaches "Which lands first?" after four words,
  the word "Which" sounds at 1.93 s (silence 1.011 to 1.332 s in the
  wav plus the 0.6 s offset; timing.log chunk boundary 1.77 s); the
  caption "Chain beside a ball." shows 0.60 to 1.86 s and "Which lands
  first?" 1.86 to 2.80 s
- captions: the 34 chunks read back from `media/chain/captions.filter`
  match the 102 narration words exactly, in order
  (`media/chain/captions-check.log`); longest chunk 20 characters;
  "Twenty eight" (12) is one chunk 29.83 to 30.45 s and "Which lands
  first?" is one chunk both times (1.86 to 2.80 and 25.11 to 26.06 s)
- payoff on screen when spoken: the tip of drop 4 lands at 27.30 s
  inside "When its tip lands," (26.68 to 27.94) and the "28 cm up" bar
  and ghost ring appear at that instant and hold until the fade at
  31.05 s, so they are up while "Twenty eight" (29.83 to 30.45) and
  "centimeters to go." (30.45 to 31.40) sound (frame 30.0 inspected);
  the card fades in 26.6 to 27.2 s and holds to the loop fade, its "28
  cm up when the tip lands" lit through the payoff; the card's 0.38 s,
  0.45 s and 69 ms match measure.log
- clipping and bands: every one of the 2,400 footage frames scanned
  (numpy, `media/chain/bandscan.log`): content columns 124 to 1017 of 0
  to 1079 and rows 176 to 1781; the caption exclusion band rows 1420 to
  1530 never deviates more than 2 levels from the background (0 px over
  8 levels); the lowest content row above the band is 1351 (the second
  fixed line); the card starts at 1592
- loop: the raw last frame equals the first (0 px) and the live scene
  at 40 s equals 0 s (0 px); in the encoded final.mp4
  (`media/chain/loopcheck.log`) frame 2399 against frame 0 differs in
  20,761 px by more than 8 levels (max channel difference 95, mean 0.29
  levels, 916 px over 32 levels on the title and link edges), the same
  order as the published bucket final (20,985 px, max 67, mean 0.31),
  i.e. h264 quantisation on the second-generation encode, not content;
  the loop step from frame 2398 to 2399 is 26,236 px over 8 levels (max
  38, the title fading back in)
- ffprobe final.mp4 (`media/chain/probe.log`): h264 1080x1920 yuv420p
  60/1 fps, 2,400 frames, 40.000000 s, 2,708,809 bytes, aac 22050 Hz
  mono, moov (offset 40) before mdat (offset 44,700); md5
  bdc31ec187393f92453dfb3410416f35
- narrated numbers against measure.log: "one meter" is chain_m 1.0 and
  the 1.00 m drop (overlay "1 m drop", legend "both fall 1 m", the
  scale bar); "eight times slower" is slow_factor 8; "Twenty eight
  centimeters to go" is the ball 0.282 m up when the tip lands (28.2
  cm); "The chain" lands first by 69.0 ms (0.3825 against 0.4515 s);
  "Halfway down, the tip is already ahead" is the tip at 0.5 L at
  0.3027 s with the ball 0.051 m behind; the fixed lines' 3.84 and 3.13
  m/s are the speeds at 0.50 m, "0.383 s" and "0.452 s" the fall times
  rounded to the millisecond, the card's "0.38 s, ball 0.45 s, a 69 ms
  lead" the same rounded to two decimals
- changes from the brief, recorded: the spoken hook is "Chain beside a
  ball. Which lands first?" (the brief's "Drop a folded chain beside a
  ball." stays on the title and the card) to keep the question inside
  two seconds; the tip time prints 0.3825 s (0.382537), the brief's
  0.3824 being the same number rounded down; a release list with
  per-drop clipped holds replaces the fixed 8 s period so the drops sit
  under the words that describe them; "tugs on it" became "drags it
  down" and "ahead of the ball" became "ahead" for the round trip; the
  second half of the mechanism sentence plays over the landed pair
  (accepted: the fall is 3.06 s of video at the brief's 1/8 speed)
- no defect left

### Metadata

- `projects/chain/metadata.json`: title "Drop a folded chain beside a
  ball, 1 m: which lands first? The chain, the ball still 28 cm up" (93
  characters); description (3,629 characters) with the setup (a 1.00 m
  chain of 40 links folded in half from a peg, one end held, the fold
  0.5 m below, a 3 cm ball measured at its centre beside it, both let
  go at the same instant to a finish line 1.00 m below, no air, g 9.81,
  the Calkin and March model with the held side (L + x) / 2 and the
  free side (L - x) / 2, v^2 = g x (2L - x) / (L - x), a = g (1 + x (2L
  - x) / (2 (L - x)^2)), the quadrature and the RK4 check, y = g t^2 /
  2, 1/8 speed, five drops in 40 s, no seed), a Measured list (0.3825
  against 0.4515 s, 84.7 percent, 69 ms; 0.718 m fallen, 0.282 m up;
  the speeds at 0.25, 0.50, 0.75, 0.90 and 0.99 m; 2.50 g halfway; the
  ball 5 cm behind at the tip's halfway; the 0.9 L, 0.99 L and L times
  with the 0.21 ms last centimetre; the RK4 agreement within 1e-9 m/s
  and 2e-8 s; the drawing cap from 0.3817 s at 19.8 m/s with the note
  that the model's tip speed runs away in the last centimetres, a real
  chain whips and loses energy there, and the time to 0.99 L is within
  a millisecond of the time to L), a Why paragraph in plain words (only
  the free side moves, links come to rest on the held side so the
  moving side gets shorter and lighter while its energy stays, g at
  release, 2.5 g halfway, the fold's tension rho v^2 / 4, the ball has
  only gravity, the lead depends only on the length), the rerun line
  and the AI-made line; 10 tags (falling chain, folded chain, chain
  drop, which lands first, faster than free fall, free fall, physics,
  physics visualization, simulation, shorts); category 27; private;
  containsSyntheticMedia true; selfDeclaredMadeForKids false; the same
  keys in the same order as projects/bucket/metadata.json; no "<" or
  ">"
- not uploaded; task left open for the orchestrator's review and upload

### Niche note

Text for the chain entry in docs/niche.md (not applied by the
producer; the orchestrator appends it after review):

[produced 2026-09-26 with the spoken hook "Chain beside a ball. Which
lands first?" (the title keeps "Drop a folded chain beside a ball."):
the chain tip reaches 1.00 m in 0.3825 s against the ball's 0.4515 s
(84.7 percent, a 69 ms lead), the ball 0.282 m up (28 cm) when the tip
lands; halfway down the tip moves 3.84 m/s against the ball's 3.13
with the ball 5 cm behind, the tip acceleration there 2.50 g; RK4 at
10,000 steps a second to 0.9 L within 1e-9 m/s and 2e-8 s of the closed
form; the drawing capped from 0.3817 s (the free side shorter than one
link, tip speed 19.8 m/s), the time to 0.99 L within a millisecond of
the time to L; five drops in 40 s at 1/8 speed on a release list so
the drops sit under the words; task 20260926-100742]

### Release
- orchestrator review (10:46 EEST): the task evidence, the 8x5 contact
  sheet and the full-resolution frames at 0.02, 27.35, 30.0 and 39.98 s
  inspected: the question "Drop a folded chain / beside a ball. / Which
  lands first?" over the folded chain and the ball at the start line
  from frame 0 with the clock at 0.000 s (the thumbnail); 27.35 s shows
  the chain fully hung with the gold tick on the finish line and "tip
  lands at 0.383 s", the ball still in the air inside its dashed ghost
  ring with the "28 cm up" bar, the fixed lines "halfway down: tip 3.84
  m/s, ball 3.13 m/s" and "chain tip 0.383 s, ball 0.452 s: a 69 ms
  lead", and the card "drop a folded chain beside a ball: / which lands
  first? the chain / tip 0.38 s, ball 0.45 s, a 69 ms lead / ball 28 cm
  up when the tip lands" lit under the caption "When its tip lands,";
  30.0 s shows both landed with the ghost ring and the "28 cm up" bar
  under the caption "Twenty eight"; 39.98 s matches 0.02 s; the contact
  sheet shows the captions in narration order and the card from 27 s;
  the narrated numbers (one meter, twenty eight centimeters) match
  chain_m 1.0 and the ball 0.282 m up at the tip's landing in
  media/chain/measure.log, and the orchestrator's own quadrature before
  the brief (0.3824 s, 0.4515 s, 0.283 m up) agrees; the producer's
  changes (the spoken hook "Chain beside a ball." for a 1.93 s question
  onset with the brief's words kept on the title and the card, the
  release list in place of a fixed period, 0.3825 s for the tip) are
  recorded in the task and keep the claim; captions sit in the y 1440
  to 1520 band, the band scanned clean on all 2,400 footage frames;
  final.mp4 h264 1080x1920 60 fps, 2,400 frames, aac 22050 Hz mono,
  40.000 s (scene_duration 40, so the gate accepts PT40S or PT41S), moov
  before mdat, md5 bdc31ec187393f92453dfb3410416f35; title 93
  characters; the description carries no < or >; approved for release
- quota check: clock 2026-09-26T10:47:12+03:00; zero upload attempts recorded since the
  2026-09-26 10:00 EEST boundary (no upload entries in web/data/log.jsonl
  today, the newest media/*/upload.log is bucket at 2026-09-25 11:13);
  this is insert attempt 1 of the hard cap of 5
- attempt 1 recorded at 2026-09-26T10:47:12+03:00, video name chain, before running
  `scripts/yt-upload.py chain`

### Published
- upload: `scripts/yt-upload.py chain` (attempt 1) ran 10:47:12 to
  10:47:18 EEST, token verified to see only the Seed Zero channel, video
  id hDic9PCXFKs, private (`media/chain/upload.log`)
- gate: `scripts/yt-qa.py chain hDic9PCXFKs --wait --publish` ran in the
  foreground from 10:47:33 EEST: processing succeeded and the 10 tags
  read back within the first minute of polling, 15 of 15 pass
  (processed, succeeded, hd, 1080x1920, title, description, tags as a
  set, category 27, not for kids, PT41S for the 40.000 s file, private);
  containsSyntheticMedia reads absent as on every earlier upload
  (`media/chain/publish.log`)
- publish: the same run set the video public at 2026-09-26T10:48:06+03:00;
  the re-read after 15 s shows privacyStatus public, madeForKids false,
  embeddable true; public at https://youtu.be/hDic9PCXFKs
- slot resolution: published for the 2026-09-26 quota day

### Quota
- attempt 1 of the hard cap of 5 for the quota day that began
  2026-09-26T10:00 EEST; cost 1 + 1,600 + 54 = 1,655 units (the
  channels.list verification inside yt-upload.py, the insert, the gate
  run's reads, update and re-read as printed by yt-qa.py); day total
  after one attempt 1,655 units plus 5 for the 10:03 stats refresh

### Repository
- committed as 36e0764 "Publish the day twenty-eight slate" (sims,
  projects, tasks, docs/niche.md, web/data; no media, previews or
  secrets) and pushed to origin/master at 2026-09-26 10:55 EEST
