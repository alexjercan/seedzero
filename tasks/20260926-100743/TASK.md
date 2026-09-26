# Produce short: Tarzan release, let go at the bottom beside 31 degrees past it on the same 6 m rope

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day28

## Goal

Backlog idea (trend research 2026-09-25, task 20260925-101408, pillar 2
chaos and physics, swing and flight; read the full entry under "Added
by trend research 2026-09-25" in docs/niche.md):
"Tarzan release: a rider on a 6 m rope let go from 60 degrees, the
water 3 m below the low point, one rider letting go at the bottom
beside one letting go 31 degrees past it; measure the landing
distance; expect 6.00 m against 10.26 m (the scan's best release is
30.9 degrees past the bottom; 45 degrees gives 9.14 m and hanging on
to the far top only 5.20 m); v^2 = 2 g L (cos theta - cos 60) then a
parabola; RK4 pendulum plus closed-form flight; the swing repeats so
the short loops; deterministic, no seed."

Orchestrator notes (2026-09-26, before this brief). The model: a rider
as a point mass on a massless rope of L = 6.00 m from a fixed pivot;
the water surface is 3.00 m below the low point of the swing; the
rider starts from rest with the rope 60 degrees from the vertical on
the left and swings down. Integrate the pendulum by RK4 (theta'' =
-(g / L) sin theta) at 10,000 steps a second and check it against the
energy closed form v^2 = 2 g L (cos theta - cos 60 degrees). At the
release angle theta past the bottom (on the rising side) the rider
leaves along the tangent, at theta above the horizontal, with that v,
from the point (L sin theta, 3 + L (1 - cos theta)) measured from the
spot on the water directly below the low point; then a parabola with
no air until the water. The landing distance is the horizontal
position at the water, measured from that spot. Draw the release, the
flight and the splash; then the rider resets to 60 degrees and the
swing repeats. g = 9.81 m/s^2.

State every derived number below as a check the sim must print, not as
a fact: release at the bottom 7.67 m/s horizontal, 0.782 s of flight,
6.00 m; release 31 degrees past the bottom 6.48 m/s at 31 degrees
above the horizontal from 3.857 m above the water, 1.290 s of flight,
10.26 m; the scan over release angles peaks at 30.9 degrees with 10.26
m (30 and 31 degrees both give 10.26 to two decimals, so the whole
degree is fine on screen); 20 degrees 9.60 m, 35 degrees 10.16 m, 45
degrees 9.14 m, and hanging on to the far top (60 degrees, speed zero,
a straight drop from 6.00 m above the water, 5.20 m out) 5.20 m. Print
the time from the start at 60 degrees to the bottom and to 31 degrees
(the RK4 swing), and the whole-degree scan from 0 to 60.

Drawing: two panels stacked, the same swing in both: pivot, rope,
rider, the water line 3 m below the low point, the far bank; the upper
panel lets go at the bottom, the lower panel 31 degrees past it; the
flight path traced and the splash marked with its distance from the
spot under the low point; the horizontal reach is 5.2 m back (the 60
degree start) plus 10.3 m forward, so about 16 m wide, which fits at
60 px per metre; each panel about 9 m tall (pivot 6 m above the low
point plus 3 m to the water). Real time or half speed, as reads
better; the swing plus flight plus a short splash hold gives a cycle
of a few seconds; make the cycle divide the scene length so the last
frame equals the first, and print the schedule in video time and the
loop check.

Day twenty-eight, second slot. Chosen because it is a when-do-you-let-go
debate with a big measured gap (the lifeguard 680 and the braking 1,010
are the family), two panels on the same swing that end apart, a closed
form the sim checks, and no seed. Question in the first two seconds:
"Swing on a rope. When do you let go to fly farthest?" (or the
producer's better wording; keep the words before the question under
nine; keep the question identical in the title, the hook and the
payoff). Setup number: a six meter rope (the 60 degree start and the 3
m drop go on the overlay and in the description). Payoff: "thirty one
degrees past the bottom: ten meters; at the bottom: six" is two
numbers; the producer may keep both distances if the card carries
them, or narrate the reach ("four meters farther") and put the
distances on the card. The 45 degree, 20 degree, 35 degree and far-top
results go to the description. Make the last frame equal the first.
Measure every fixed text line with PIL before rendering and keep every
line under 950 px. Music seed 87.

## Claim

A rider on a six meter rope, starting from rest at 60 degrees with the
water 3 m below the low point, who lets go at the bottom of the swing
lands 6.00 m out (7.67 m/s, level, 0.78 s of flight); the same rider
letting go 31 degrees past the bottom lands 10.26 m out (6.48 m/s
pointed 31 degrees up from 3.86 m above the water, 1.29 s of flight),
4.26 m farther; the scan over every release angle peaks at 30.9
degrees with the same 10.26 m. Every number in the narration is
printed by the sim before the script is written (the sim sets the
claim).

## Evidence

### Measurements

(recorded after the measure-only run, before scripting)

`sims/tarzan/tarzan.py --measure-only` with `projects/tarzan/manifest.json`
(a rider as a point mass on a massless rope of 6.00 m from a fixed
pivot; the water surface 3.00 m below the low point of the swing, so
the pivot is 9 m above the water; the rider starts from rest with the
rope 60 degrees from the vertical on the left and swings down; theta''
= -(g / L) sin theta by RK4 at 10,000 steps per second (dt 1e-4 s)
against the energy closed form v^2 = 2 g L (cos theta - cos 60); at the
release angle theta past the bottom the rider leaves along the tangent,
at theta above the horizontal, from (L sin theta, 3 + L (1 - cos
theta)) measured from the spot on the water under the low point, then a
parabola with no air (velocity Verlet at the same dt against the closed
form) until the water; the landing distance is the horizontal position
at the water from that spot; g 9.81 m/s^2; the upper rider lets go at
the bottom, the lower rider 31 degrees past it; drawn at 48 px per
metre at half speed, the 4 s cycle of swing, flight, splash and reset
taking 8 s of video, 5 cycles in 40 s; deterministic, no seed; run at
10:21:14 EEST, log in `media/tarzan/measure.log`):

- swing (RK4 from rest at 60 degrees): the rider reaches the bottom
  after 1.3184 s at 7.6720 m/s (closed form 7.6720 m/s, diff 1.5e-8
  m/s) and 31 degrees past the bottom after 1.7650 s at 6.4843 m/s
  (closed form 6.4843, diff 1.3e-8 m/s), 0.4467 s after the bottom; the
  rope reaches the far top (60 degrees) after 2.6367 s at 0.0002 m/s;
  the full period is 5.2734 s (4 sqrt(L / g) K(sin 30 degrees) = 5.2734
  s, diff 8e-15 s; a small-angle pendulum would take 4.9138 s); the
  energy per unit mass drifts by at most 1e-12 J/kg over 7.4 s
- upper panel (lets go at the bottom): 7.6720 m/s (7.67) level (vx
  7.672, vy 0) from (0.000, 3.000) m, 3.000 m above the water; no rise;
  hits the water after 0.7821 s (0.782 s) at 6.0000 m (6.00 m) from the
  spot under the low point (Verlet 6.0000 m after 0.7821 s, diffs
  1.2e-8 m and 1.5e-9 s)
- lower panel (lets go 31 degrees past the bottom): 6.4843 m/s (6.48)
  at 31 degrees above the horizontal (vx 5.558, vy 3.340) from (3.090,
  3.857) m, 3.857 m above the water and 3.090 m past the spot; apex
  4.425 m above the water at 4.982 m; hits the water after 1.2903 s
  (1.290 s) at 10.2618 m (10.26 m) (Verlet 10.2618 m after 1.2903 s,
  diffs 2.0e-9 m and 3.5e-10 s)
- the two against each other: the lower rider lets go 1.188 m/s slower
  (84.5 % of the bottom speed) but 0.857 m higher and pointed 31 degrees
  up, stays in the air 0.508 s longer (1.65 x) and lands 4.262 m farther
  (10.26 against 6.00 m, 71.0 % farther)
- scan of the release angle (whole degrees 0 to 60): 0: 6.00, 5: 7.04,
  10: 8.03, 15: 8.90, 20: 9.60, 25: 10.06, 28: 10.21, 29: 10.24, 30:
  10.26, 31: 10.26, 32: 10.25, 33: 10.24, 35: 10.16, 40: 9.78, 45: 9.14,
  50: 8.27, 55: 7.17, 59: 5.98, 60: 5.20 m (the full list in the log);
  the whole-degree best is 31 degrees at 10.2618 m (30 degrees gives
  10.2571 m, the same 10.26 to two decimals); the fine scan (0.01
  degree steps) peaks at 30.90 degrees with 10.2619 m (10.26 m);
  hanging on to the far top (60 degrees, speed 0) drops the rider
  straight down from 6.000 m above the water, 5.196 m out, 1.106 s to
  the water, 5.20 m
- for the description (release angle: speed, height, flight, landing):
  0 deg 7.67 m/s, 3.00 m, 0.782 s, 6.00 m; 10 deg 7.55, 3.09, 0.939,
  8.03; 20 deg 7.19, 3.36, 1.116, 9.60; 25 deg 6.92, 3.56, 1.201,
  10.06; 30 deg 6.56, 3.80, 1.277, 10.26; 31 deg 6.48, 3.86, 1.290,
  10.26; 35 deg 6.13, 4.09, 1.339, 10.16; 40 deg 5.60, 4.40, 1.383,
  9.78; 45 deg 4.94, 4.76, 1.403, 9.14; 50 deg 4.10, 5.14, 1.393, 8.27;
  55 deg 2.94, 5.56, 1.338, 7.17; 60 deg 0.00, 6.00, 1.106, 5.20
- schedule printed by the sim (first manifest, cycle_start_at -3.7 s,
  to be set from the voice timing): cycles of 8 s start at -3.7, 4.30,
  12.30, 20.30, 28.30, 36.30 s with the rider at rest at 60 degrees; in
  each cycle the upper rider lets go 2.637 s after the start and
  splashes at 4.201 s, the lower rider lets go at 3.530 s and splashes
  at 6.111 s, the empty rope reaches the far top at 5.273 s, the splash
  and the distance hold until the reset fade over the last 0.4 s; on
  the first frame the upper rider is 1.06 s into its flight and the
  lower rider 0.17 s into its flight; title until 3 s; card from 29.2
  s; the scene is periodic, 40 s holds exactly 5 cycles
- text widths (DejaVuSans-Bold): overlay 857 px at 34 (a first draft
  "rope 6 m from 60 deg | water 3 m down | no seed" measured 946 px and
  was shortened before any render); title lines 658, 613 and 469 px at
  56; legend 806 px at 40, tag 443 px at 28; labels 480 and 700 px at
  40; fixed lines 231, 376, 249 and 355, 376, 249 px at 28; distance
  labels 108 and 128 px at 28; readouts 154, 182 and 171 px at 40; card
  lines 780, 745, 496 and 610 px at 40; nothing over 950 px; the sim
  asserts every line under 950 px

Narration numbers: six meter (setup; the rope, on the overlay "6 m
rope" and in the narration; the 60 degree start and the 3 m drop stay
on the overlay and in the description); thirty one degrees past the
bottom, ten meters and six (payoff; 10.2618 m and 6.0000 m from the
closed form and the Verlet flight, both on the card to two decimals;
the brief allows both distances when the card carries them). The
speeds, the flight times, the 0.857 m, the apex, the scan and the far
top go to the readouts and the description.

### Production

- layout (`sims/tarzan/tarzan.py`): overlay "6 m rope, 60 deg | water 3
  m down | no seed" at y 96 (drawn by compose from the manifest), title
  "You swing on a rope. / When should you let go / to fly farthest?" at
  y 196/254/312 (56 px) for the first 3.2 s, then the legend "same
  swing, two moments to let go" at y 246 (40 px) and the tag "side view,
  half speed, no air" at y 298 (28 px, muted); two panels stacked at 48
  px per metre, each with its label top left at x 60 ("lets go at the
  bottom" / "lets go 31 deg past the bottom", 40 px) and a live readout
  top right at x 1020 (the rope angle "-55 deg" while on the rope, the
  distance flown "3.44 m" in flight, the landing distance in gold after
  the splash); the upper panel with its pivot at (372, 394) and the
  water line at y 826, the lower panel with its pivot at (372, 944) and
  the water at 1376, a 40 px tinted water band under each line (to 866
  and 1416) that carries a gold measure line from the spot under the
  low point to the splash with the label "6.00 m" / "10.26 m"; in each
  panel the rider as a teal disc (0.3 m) on a grey rope from the white
  pivot, a dashed arc of the rider's path from -60 to +60 degrees, a
  short ledge under the start, a gold tick at the bottom (upper) and a
  gold arc from the bottom to 31 degrees with ticks (lower), the empty
  rope swinging on and fading after the release, the release point as
  a small ring, the flight traced as a teal line, a teal splash ring
  and crown at the landing; the fixed lines "7.67 m/s, level / 3.00 m
  above the water / 0.78 s in the air" and "6.48 m/s, up at 31 deg /
  3.86 m above the water / 1.29 s in the air" (28 px, the first line
  gold) at the bottom left of each panel at y water-96/-64/-32; the
  geometry band y 350 to 1420 drawn at 2x and reduced; captions at
  caption_y 0.75 (y 1440 to 1520); the four-line card from y 1592 (40
  px, 56 px pitch); the HUD (legend, tag, fixed lines, gold marks,
  card) fades out over the first 0.25 s of the last 0.5 s and the title
  fades in over the last 0.25 s, the last frame equal to the first; the
  first smoke pass showed the pivot's beam bar as an underscore under
  the panel label, so the beam was dropped and the pivot is a dot
- whisper pre-tests (10:22:35 to 10:23:35 EEST, `media/tarzan/hooks/`,
  log `hooks/pretest.log`): the brief's question "When do you let go to
  fly farthest?" lost "do" in five of five passes (hook1 "You swing on
  a rope. When do you ...", hook2 "Swing on a rope. When do you ...",
  hook3 and v2 "You are on a rope swing. When do you ..." twice, v3 "So,
  when do you ..." after "rope swing"), hook1 also heard "swim" for
  "swing"; "farthest" came back "far thest" three times after a "rope
  swing" opening (v1, v3, v5); v4 "You swing on a rope. When should you
  let go to fly farthest? A six meter rope, with water below." passed
  twice (5.09 and 5.39 s) and the matching payoff p1 "So, when should
  you let go to fly farthest? Thirty one degrees past the bottom. Ten
  meters, not six." passed twice (5.93 and 6.42 s); the mechanism group
  "Same swing, two riders, two moments to let go. ... so you get more
  time in the air." passed (19.09 s) and the first payoff group with
  "when do you" passed once (5.68 s); question onsets from silencedetect
  on the v4 wavs (-35 dB, 0.08 s, plus the 0.6 s offset): the pause
  after "rope." ends at 1.79 and 1.73 s of video; v4 kept, so the
  question is "When should you let go to fly farthest?" (a change from
  the brief's suggested "When do you let go"; the title, the hook, the
  card and the payoff all carry the new words), five words before it
- narration (`projects/tarzan/narration.txt`): 111 words, 11 sentences,
  "six meter" (setup), "thirty one degrees", "ten meters" and "six"
  (payoff) the only numbers, all in words; no "still", "pull",
  "spread", "straight", "a hundred", "metres", "brakes", "drifts",
  "games", "let's" or sentence-initial "Where", "Spin", "Swing" (the
  whisper mishearing list); "lets go" appears only on screen
- smoke frames (`--frames`, two passes 10:24:20 and 10:28:24 EEST, log
  `media/tarzan/smoke.log`): pass 1 at 0, 1.5, 2.9, 5.0, 7.0, 7.9, 8.6,
  10.5, 12.1, 29.85, 39.6, 39.98 s with the first schedule
  (cycle_start_at -3.7) found the pivot beam under the label (fixed as
  above) and nothing else; pass 2 at 0, 1.9, 3.1, 9.94, 11.5, 18.83,
  20.5, 21.6, 28.3, 30.0, 31.0, 39.6, 39.98 s with the final schedule:
  title over both panels at 0 s with the riders just off the ledge at
  -55 deg, both riders at 0 deg at 9.94 s (the upper at its release),
  the upper in flight and the lower just released at 31 deg at 18.83 s,
  both splashes with the measure lines and the card at 30.0 s, clean
- voice (`scripts/voiceover.sh tarzan`, log `media/tarzan/voice.log`):
  pass 1 at 10:25:02 EEST failed the round trip ("leave" heard "lead"
  in "but you leave going up"), reworded to "but you are going up";
  passes 2 and 3 at 10:25:30 and 10:25:34 failed on the sentence-initial
  "Slower" (heard "flower", then "so are"; the clipped-onset family),
  reworded to "You are slower now, but you are going up, from higher,
  so you get more time in the air."; pass 4 at 10:25:38 failed on "fly"
  heard "5" in the payoff question (the same words passed in five
  earlier passes, a coin flip, no change); pass 5 at 10:26:01 EEST
  passed, "ok: transcript matches narration (30.778050s)"; voice.wav
  30.78 s, ends at 31.38 s of video with the 0.6 s offset (111 words in
  30.78 s, 3.6 words per second; the pass-1 loop stopped after one pass
  because the grep pipeline masked the exit status, fixed for the
  later passes)
- timing (`scripts/voice-timing.py media/tarzan/voice.wav`, log
  `media/tarzan/timing.log`, plus silencedetect at -35 dB, 0.10 s for
  the finer pauses; video time): "You swing on a rope." 0.60 to 1.64,
  "When should you let go to fly farthest?" 1.82 to 3.55 (the pause
  after "rope." spans 1.64 to 1.82 s, so "When" sounds at 1.82 s), "A
  six meter rope," 3.74 to 4.57, "with water below." 4.79 to 5.57,
  "Same swing, two riders, two moments to let go." 5.78 to 8.49, "On
  the upper swing," 8.68 to 9.62, "you let go at the bottom." 9.80 to
  11.06, "That is your fastest point," 11.24 to 12.43, "but you fly out
  level," 12.75 to 13.84, "and the water is close." 14.13 to 15.24, "On
  the lower swing," 15.44 to 16.31, "you hang on a little longer," 16.64
  to 17.82, "and let go thirty one degrees past the bottom." 18.05 to
  20.49, "You are slower now," 20.62 to 21.50, "but you are going up,"
  21.80 to 22.54, "from higher," 22.90 to 23.43, "so you get more time
  in the air." 23.76 to 25.65, "So, when should you let go to fly
  farthest?" 25.81 to 27.63, "Thirty one degrees past the bottom." 27.87
  to 29.64, "Ten meters," 29.81 to 30.45, "not six." 30.63 to 31.25; the
  voice-timing pieces heard "A 6-meter rope" and "10 meters, not 6"
  (digits, harmless: the gate is the full-file round trip)
- schedule (manifest): speed 0.5 (half speed), cycle_s 8 (the 4 s real
  cycle of swing, flight, splash and reset), cycle_start_at -0.7 so the
  cycles start at -0.7, 7.3, 15.3, 23.3, 31.3, 39.3 s; the upper rider
  lets go 2.637 s after each start and splashes at 4.201 s, the lower
  lets go at 3.530 s and splashes at 6.111 s, the reset fade runs over
  the last 0.4 s: upper releases at 1.94, 9.94, 17.94, 25.94, 33.94 s,
  upper splashes at 3.50, 11.50, 19.50, 27.50, 35.50 s, lower releases
  at 2.83, 10.83, 18.83, 26.83, 34.83 s, lower splashes at 5.41, 13.41,
  21.41, 29.41, 37.41 s, resets at 6.90, 14.90, 22.90, 30.90, 38.90 s;
  the 9.94 s upper release sits under "you let go at the bottom." (9.80
  to 11.06; caption "you let go at the" 9.75 to 11.14), the 18.83 s
  lower release under "and let go thirty one degrees past the bottom."
  (18.05 to 20.49; caption "longer, and let go" 18.07 to 19.18), the
  29.41 s lower splash lights "10.26 m" before "Ten meters," (29.81 to
  30.45) and both distances hold to the fade at 30.90 s while "not six."
  sounds (30.63 to 31.25); on the first frame both riders are 0.7 s into
  the swing, just off the ledge; the first hook cycle plays the whole
  story under the title (releases at 1.94 and 2.83 s, splashes at 3.50
  and 5.41 s); title_until 3.2 (the question caption "go to fly
  farthest?" runs to 4.21 s); payoff_t 27.6 with a 0.6 s fade, so the
  card is fully lit at 28.2 s inside "Thirty one degrees past the
  bottom." (27.87 to 29.64) and before "Ten meters,"
- footage (`nix develop -c python3 sims/tarzan/tarzan.py`, log
  `media/tarzan/render.log`): one render 10:29:28 to 10:30:08 EEST: loop
  check 0 px (max channel difference 0), periodicity check 0 px, loop
  step 2,492 px (the rider moves 3.07 px per frame at the bottom); 2,400
  frames, eight forked workers, h264 crf 16 yuv420p 60 fps, footage.mp4
  2,759,060 bytes, 40.00 s; `--measure-only` re-run into
  `media/tarzan/measure.log` at 10:30:09 EEST with the final manifest
  and sim (the schedule print now starts at the cycle that contains 0 s
  and clips the event lists to the scene)
- compose (`scripts/compose.sh tarzan`, log `media/tarzan/compose.log`):
  one run 10:30:09 to 10:30:24 EEST: music seed 87 at 40.00 s (gain
  0.18), 31 caption chunks (longest 20 characters, "Ten meters, not
  six." one chunk of exactly 20), final.mp4 3,169,028 bytes 40.000000 s,
  preview.mp4 540x960 30 fps 929,765 bytes 40.066667 s, sheet.png 8x5
  at 1 fps 482,682 bytes
- text widths (measure.log, PIL at the drawn sizes): overlay 857 px,
  title lines 658, 746 and 469 px, legend 806 px, tag 443 px, labels
  480 and 700 px, fixed lines 231, 376, 249 and 355, 376, 249 px,
  distance labels 108 and 128 px, readouts 154, 182 and 171 px, card
  lines 875, 745, 496 and 610 px, all under 950 px; the first overlay
  draft "rope 6 m from 60 deg | water 3 m down | no seed" measured 946
  px and was shortened

### Local QA

- frames (`media/tarzan/frame-<t>.png` from final.mp4 at 0.02, 1.9, 2.0,
  9.94, 11.5, 18.83, 20.5, 21.6, 28.3, 30.0, 31.0 and 39.98 s, plus
  `sheet.png`) inspected: 0.02 s: overlay and the three-line question
  from frame 0 over both panels, both riders just off the ledge on the
  rope at "-55 deg", the water bands empty; 1.9 and 2.0 s: caption "When
  should you let" in the band under the panels, the title still up, the
  upper rider just released at the bottom on the hook cycle ("0.24 m")
  and the lower rider at "2 deg"; 9.94 s: caption "you let go at the",
  the legend and tag in place of the title, both riders at the bottom
  of the dashed arc, the upper one just off the rope ("0.05 m") at the
  gold tick, the lower one at "0 deg" with the gold arc ahead of it, the
  fixed lines in both panels; 11.5 s: caption "That is your fastest",
  the upper rider at the water 6 m out ("6.00 m" in gold) at the end of
  its traced path with the empty rope fading on the right, the lower
  rider in flight ("4.95 m"); 18.83 s: caption "longer, and let go", the
  upper rider in flight ("3.44 m"), the lower rider just released at the
  end of the gold arc ("3.10 m") with the release ring; 20.5 s: caption
  "past the bottom.", the upper splash with the "6.00 m" measure line,
  the lower rider past its apex ("7.73 m") on the traced arc; 21.6 s:
  caption "You are slower now,", both splashes with the measure lines
  "6.00 m" and "10.26 m" and the gold readouts; 28.3 s: caption "let go
  to fly", the card "when should you let go to fly farthest? / 31 deg
  past the bottom: 10.26 m / at the bottom: 6.00 m / the scan peaks at
  30.9 deg" lit under it, the lower rider in flight ("7.18 m"); 30.0 s:
  caption "past the bottom.", both measure lines and the card; 31.0 s:
  caption "Ten meters, not six.", both measure lines (the reset fade
  just begun) and the card; 39.98 s: the title back and the HUD gone,
  matches 0.02 s; the contact sheet shows the captions in narration
  order, the story playing once under the title in the first 6 s, and
  the card from 28 s to 39 s
- question inside two seconds: the title carries the question from
  frame 0; the narration reaches "When should you let go to fly
  farthest?" after five words, the word "When" sounds at 1.82 s (pause
  1.64 to 1.82 s in video time); the caption "When should you let"
  shows 1.99 to 3.10 s and "go to fly farthest?" 3.10 to 4.21 s
- captions: the 31 chunks read back from `media/tarzan/captions.filter`
  match the 111 narration words exactly, in order; longest chunk 20
  characters; "Ten meters, not six." (20) is one chunk 30.27 to 31.38 s,
  "Thirty one degrees" 28.61 to 29.44 s and "past the bottom." 29.44 to
  30.27 s
- payoff on screen when spoken: the card fades in 27.6 to 28.2 s and
  holds to the loop fade; "31 deg past the bottom: 10.26 m" and "at the
  bottom: 6.00 m" are fully lit at 28.2 s while "Thirty one degrees past
  the bottom." sounds 27.87 to 29.64 and "Ten meters, not six." 29.81 to
  31.25 (frames 28.3, 30.0 and 31.0 inspected); the lower panel's
  "10.26 m" measure line and gold readout are lit from the 29.41 s
  splash and the upper panel's "6.00 m" from 27.50 s, both until the
  reset fade at 30.90 s; the card's "the scan peaks at 30.9 deg" matches
  the fine scan
- clipping and bands: every one of the 2,400 footage frames scanned
  (numpy, more than 24 levels from the background): content columns 60
  to 1020 of 0 to 1079 and rows 172 to 1783; the caption exclusion band
  rows 1420 to 1530 never deviates more than 5 levels from the
  background (0 frames over 8 levels); the lowest geometry row is 1415
  (the lower water band); the card starts at 1572
- loop: the raw last frame equals the first (0 px, max channel
  difference 0) and the live scene at 40 s equals 0 s (0 px); in the
  encoded footage.mp4 the last frame differs from the first in 660 px
  over 24 levels (max 59) and in final.mp4 frame 2399 against frame 0
  differs in 26,707 px by more than 8 levels (max channel difference
  74, mean 0.37 levels, 923 px over 32 levels), the same order as the
  bucket final (20,985 px, max 67, mean 0.31), i.e. h264 quantisation
  on the second-generation encode, not content
- ffprobe final.mp4: h264 1080x1920 yuv420p 60/1 fps, 2,400 frames,
  40.000000 s, 3,169,028 bytes, aac 22050 Hz mono, moov before mdat;
  md5 21f861b49ded75f614e9d7cf3a9a8166
- narrated numbers against measure.log: "A six meter rope" is rope_m
  6.0 (overlay "6 m rope"); "thirty one degrees past the bottom" is
  lower_release_deg 31 (the whole-degree best of the scan, 10.2618 m;
  the fine scan peaks at 30.90 degrees with 10.2619 m, on the card);
  "Ten meters" is the 31 degree landing 10.2618 m (10.26 m on the card
  and the measure line); "six" is the bottom landing 6.0000 m (6.00 m on
  the card and the measure line); "fastest point" is 7.672 m/s at the
  bottom against 6.484 m/s at 31 degrees; "fly out level" is vy 0 at
  the bottom; "going up, from higher" is 31 degrees above the
  horizontal from 3.857 m against 3.000 m; "more time in the air" is
  1.290 s against 0.782 s; the fixed lines carry 7.67 m/s, 3.00 m, 0.78
  s and 6.48 m/s, 31 deg, 3.86 m, 1.29 s from the same log
- no defect left

### Metadata

- `projects/tarzan/metadata.json`: title "Rope swing: when should you
  let go to fly farthest? 31 deg past the bottom, 10.26 m against 6 m"
  (95 characters); description (3,162 characters) with the setup (a
  rider on a 6 m rope from a fixed pivot, from rest at 60 degrees, the
  water 3 m below the low point, the upper rider letting go at the
  bottom and the lower 31 degrees past it, a point mass on a massless
  rope, RK4 at 10,000 steps a second against v^2 = 2 g L (cos theta -
  cos 60), the tangent release and the parabola with no air, the
  landing measured from the spot under the low point, half speed, 5
  cycles in 40 s, no seed), a Measured list (the bottom release 7.67
  m/s level from 3.00 m, 0.782 s, 6.00 m; the 31 degree release 6.48
  m/s at 31 degrees up, 84.5 % of the bottom speed, from 3.86 m, apex
  4.43 m, 1.290 s, 1.65 times longer, 10.26 m, 4.26 m and 71 % farther;
  the scan 0 to 55 degrees with the 30.9 degree peak and the 5.20 m far
  top; the swing times 1.318, 1.765, 2.637 s and the 5.273 s period
  against the elliptic form and the 4.914 s small-angle period; the
  2e-8 m/s, 1e-12 J/kg, 2e-8 m and 2e-9 s checks), a Why paragraph in
  plain words (how far you fly is how fast you leave times how long you
  stay up; the bottom is fastest but level and lowest, 0.78 s; a little
  past the bottom trades 15.5 % of the speed for an upward launch from
  higher, 1.29 s, 10.26 against 6.00 m; too far past and the rope has
  taken the speed back, 45 degrees 9.14 m, the far top 5.20 m; the best
  is 31 degrees, well under 45, because you start above the water and
  the rope takes speed back on the way up), the rerun line and the
  AI-made line; 10 tags (rope swing, tarzan swing, when to let go,
  projectile motion, pendulum, rope swing physics, physics, physics
  visualization, simulation, shorts); category 27; private;
  containsSyntheticMedia true; selfDeclaredMadeForKids false; the same
  keys in the same order as projects/bucket/metadata.json; no "<" or
  ">"
- not uploaded; task left open for the orchestrator's review and upload

### Niche note

[produced 2026-09-26 as projects/tarzan, day 28 second slot: 6.00 m
letting go at the bottom (7.67 m/s level from 3.00 m, 0.782 s) against
10.26 m letting go 31 degrees past it (6.48 m/s at 31 degrees up from
3.86 m, 1.290 s), 4.26 m farther, the fine scan peaking at 30.9 degrees
with 10.26 m, 45 degrees 9.14 m and the far top 5.20 m, all as the
entry expected (RK4 within 2e-8 m/s of the closed form); the question
became "When should you let go to fly farthest?" because whisper
dropped "do" from "When do you let go" in five of five passes; half
speed, 8 s cycles, five in 40 s, the last frame equal to the first; no
seed; task 20260926-100743]

### Release
- orchestrator review (10:46 EEST): the task evidence, the 8x5 contact
  sheet and the full-resolution frames at 0.02, 21.6, 30.0 and 39.98 s
  inspected: the question "You swing on a rope. / When should you let
  go / to fly farthest?" over both panels from frame 0 with both riders
  on the rope just off the ledge at "-55 deg" (the thumbnail); 21.6 s
  shows both splashes with the traced flight paths and the gold measure
  lines "6.00 m" and "10.26 m", the release ring at the bottom of the
  upper arc and at the end of the gold 31 degree arc in the lower
  panel, the fixed lines "7.67 m/s, level / 3.00 m above the water /
  0.78 s in the air" and "6.48 m/s, up at 31 deg / 3.86 m above the
  water / 1.29 s in the air", under the caption "You are slower now,";
  30.0 s shows the card "when should you let go to fly farthest? / 31
  deg past the bottom: 10.26 m / at the bottom: 6.00 m / the scan peaks
  at 30.9 deg" lit under the caption "past the bottom." with both
  measure lines up; 39.98 s matches 0.02 s; the contact sheet shows the
  captions in narration order, the story playing once under the title
  in the first 6 s and the card from 28 s; the narrated numbers (a six
  meter rope, thirty one degrees past the bottom, ten meters, six)
  match rope_m 6.0, the whole-degree scan best 31 degrees at 10.2618 m
  and the bottom landing 6.0000 m in media/tarzan/measure.log, and the
  orchestrator's own closed forms before the brief (6.00 m, 10.26 m at
  31 degrees, scan best 30.9 degrees) agree; the producer's changes
  (the question "When should you let go" because whisper dropped "do"
  in five of five passes, applied to the title, hook, card and payoff
  alike; 48 px per metre; half speed on 8 s cycles) are recorded in the
  task and keep the claim; captions sit in the y 1440 to 1520 band,
  scanned clean on all 2,400 footage frames; final.mp4 h264 1080x1920
  60 fps, 2,400 frames, aac 22050 Hz mono, 40.000 s (scene_duration 40,
  so the gate accepts PT40S or PT41S), moov before mdat, md5
  21f861b49ded75f614e9d7cf3a9a8166; title 95 characters; the
  description carries no < or >; approved for release
- quota check: clock 2026-09-26T10:49:13+03:00; one upload attempt (chain, 10:47:12,
  published as hDic9PCXFKs at 10:48:06) recorded since the 2026-09-26
  10:00 EEST boundary (log entries and media/*/upload.log both checked);
  this is insert attempt 2 of the hard cap of 5
- attempt 2 recorded at 2026-09-26T10:49:13+03:00, video name tarzan, before running
  `scripts/yt-upload.py tarzan`

### Published
- upload: `scripts/yt-upload.py tarzan` (attempt 2) ran 10:49:13 to
  10:49:20 EEST, token verified to see only the Seed Zero channel, video
  id f-ZLd4-azw0, private (`media/tarzan/upload.log`)
- gate: `scripts/yt-qa.py tarzan f-ZLd4-azw0 --wait --publish` ran in
  the foreground from 10:49:27 EEST: processing succeeded and the 10
  tags read back within the first minute of polling, 15 of 15 pass
  (processed, succeeded, hd, 1080x1920, title, description, tags as a
  set, category 27, not for kids, PT41S for the 40.000 s file, private);
  containsSyntheticMedia reads absent as on every earlier upload
  (`media/tarzan/publish.log`)
- publish: the same run set the video public at 2026-09-26T10:49:59+03:00;
  the re-read after 15 s shows privacyStatus public, madeForKids false,
  embeddable true; public at https://youtu.be/f-ZLd4-azw0
- slot resolution: published for the 2026-09-26 quota day

### Quota
- attempt 2 of the hard cap of 5 for the quota day that began
  2026-09-26T10:00 EEST; cost 1 + 1,600 + 54 = 1,655 units (the
  channels.list verification inside yt-upload.py, the insert, the gate
  run's reads, update and re-read as printed by yt-qa.py); day total
  after two attempts 3,310 units plus 5 for the 10:03 stats refresh

### Repository
- committed as 36e0764 "Publish the day twenty-eight slate" (sims,
  projects, tasks, docs/niche.md, web/data; no media, previews or
  secrets) and pushed to origin/master at 2026-09-26 10:55 EEST
