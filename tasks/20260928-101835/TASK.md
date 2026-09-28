# Produce short: Rod on ice, a stick let go on ice beside the same stick hinged at its foot

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day30

## Goal

Backlog idea (trend research 2026-09-27, task 20260927-102520, pillar 2
chaos and physics, rigid bodies; read the full entry under "Added by
trend research 2026-09-27" in docs/niche.md):
"Rod on ice: a 1 m rod let go 10 degrees off vertical on ice beside the
same rod with its foot pinned; measure the time to lie flat and where
the tip lands; expect the ice rod flat at 0.517 s with its tip 0.50 m
from its start line (the centre falls straight down) against 0.768 s
and 1.00 m pinned, 1.49 times faster, both at 5.38 rad/s at the floor;
theta'^2 = 12 g (sin 80 - sin theta) / (L (1 + 3 cos^2 theta)) against
3 g (sin 80 - sin theta) / L; mild, so rank it low; repeat;
deterministic, no seed."

Orchestrator notes (2026-09-28, before this brief). The model: a
uniform thin rod of length L = 1.0 m stands on a floor with its foot at
x = 0, leaning 10 degrees off vertical toward the right (theta = 80
degrees from the floor), and is let go from rest. Panel A, ice: the
floor is frictionless, so no horizontal force acts and the centre of
mass falls straight down along x = (L / 2) cos 80 = 0.0868 m while the
foot slides back; with the foot on the floor, y_c = (L / 2) sin theta,
and the energy form (I_c = m L^2 / 12) gives theta'^2 = 12 g (sin 80 -
sin theta) / (L (1 + 3 cos^2 theta)); the equation of motion is (1 + 3
cos^2 theta) theta'' = 3 sin theta cos theta theta'^2 - (6 g / L) cos
theta. Panel B, hinged: the foot is pinned in a hinge, theta'' = -(3 g
/ (2 L)) cos theta, theta'^2 = 3 g (sin 80 - sin theta) / L. RK4 both
at 10,000 steps a second or finer and check against the energy forms.
Orchestrator integration (checks, not facts, g = 9.81): ice flat at
0.517 s, hinged at 0.768 s (1.487 times longer), both at 5.38 rad/s at
the floor (the same, since the same energy ends in the same rotation:
on ice the centre's vertical speed is zero at the floor). Where the tip
lands: on ice the tip's horizontal travel is (L / 2)(1 - cos 80) =
0.413 m (it lands 0.587 m from the foot's start) and the foot slides
back by the same 0.413 m; hinged, the tip travels L (1 - cos 80) =
0.826 m (it lands 1.000 m from the foot). The ratio is exactly 2.000
at any release angle, because the centre on ice does not move sideways:
the payoff. Contact checks the sim must print: on ice the floor's push
on the foot N = m (g + y_c'') stays positive, at least 0.169 weights
(at 27.4 degrees), so the foot never leaves the floor; on the hinge the
vertical hinge force drops to 0.008 weights at 19.2 degrees and the
horizontal hinge force reaches 93 times the vertical near the floor, so
no friction could hold this foot: say "hinged" or "pinned in a hinge",
never "on a rough floor". For the description print the same run at 1
and 5 degrees off vertical (ice 0.811 and 0.603 s, hinged 1.368 and
0.948 s; the travel ratio still 2.000) and the sqrt(L) scaling (a 1.2 m
rod at 10 degrees: ice 0.566 s).

State every derived number above as a check the sim must print, not as
a fact.

Drawing: two panels stacked, the same scale and floor line, the same
clock; panel A an ice floor (pale, a few highlights), panel B a floor
with a small hinge bracket at the foot; the stick as a thick bar with
a marked middle and a coloured tip; a faint vertical guide through the
centre of mass on panel A so the viewer sees it drop straight down; a
start mark on the floor at the foot and a landing mark where the tip
comes down; a live horizontal readout of the tip's travel in cm on
each panel; the stick held flat after landing with the readouts; slow
motion so the 0.5 s fall plays over 2 to 3 s (say the factor on
screen); repeat the drop so the short loops (fade and reset as
tablecloth does, or a cycle length that divides the scene); several
cycles in about 40 s; the last frame equals the first.

Day thirty, third slot. Chosen because "where does the tip land?" has a
visible different answer on the two panels from the same release, the
exact half is a closed form, sims/hingedstick already has the hinged
half of the physics, and no seed. Question in the first two seconds:
"A stick falls on ice. Where does the tip land?" (or the producer's
better wording; keep the words before the question under nine; keep
the question identical in the title, the hook and the payoff). Setup
number: one meter stick (or ten degrees off vertical; pick one for the
narration, the other goes to the overlay). Payoff number: forty one
centimeters along on ice, eighty three on the hinge, exactly half; the
middle falls straight down and the foot slides back. The 0.52 against
0.77 s, the 5.4 rad/s and the 0.169 weights go to the card and the
description; "which lands first" is a second question, so keep it off
the hook and the payoff. Whisper risks: "ice" may come back as "eyes",
"tip" as "tip" (fine) or "tape", "hinged" as "hinge"; pre-test the
hooks with scripts/voiceover.sh and keep the one whose question lands
earliest under two seconds; avoid short function words at pace ("do",
"it" at a sentence start). Make the last frame equal the first. Measure
every fixed text line with PIL before rendering and keep every line
under 950 px, and the title under 100 characters with no < or >. Music
seed 94. Templates: sims/hingedstick (the hinged rod, RK4, energy
check, a falling stick drawn), sims/tablecloth (two panels on one
clock, slow motion, cycles, reset fade), sims/springdrop (two panels
with readouts). Sim name icerod: sims/icerod/icerod.py,
projects/icerod/, media/icerod/.

## Claim

A uniform 1 m stick let go from rest 10 degrees off vertical on a
frictionless floor (ice) lands with its tip 41.32 cm along from where
the tip started, (L / 2)(1 - cos 80), because no horizontal force acts:
the centre stays at x = 8.68 cm and drops 49.24 cm straight down while
the foot slides back the same 41.32 cm. The same stick with its foot
pinned in a hinge lands with its tip 82.64 cm along, L (1 - cos 80). The
ratio is 2.0000, exactly 2 at any lean. The ice stick is flat at 0.5166
s against 0.7680 s hinged (1.487 times longer), both at 5.3836 rad/s at
the floor; the floor's push on the ice foot never drops below 0.169
weights (at 27.4 degrees); the hinge's vertical force drops to 0.0075
weights at 19.2 degrees and the horizontal to vertical ratio reaches 93.4
at 18.8 degrees, so that foot must be pinned. Narrated: one meter stick
(setup); forty one centimeters on ice, eighty three pinned in a hinge,
exactly half as far (payoff). Card: 41 cm along on ice, 83 cm in a
hinge; half; flat at 0.517 s on ice, 0.768 s hinged; both at 5.38 rad/s;
ice foot pushed up at least 0.17 weight. Description: 1 and 5 degrees
off vertical, a 1.2 m stick, the hinge forces.

## Evidence

### Measurements

`nix develop -c python3 sims/icerod/icerod.py --measure-only` at
11:08:36 EEST (the final manifest), media/icerod/measure.log, copied
whole:

```
Mon Sep 28 11:08:36 AM EEST 2026
setup: a uniform stick of length 1 m stands with its foot at x = 0, leaning 10 degrees off vertical toward the right (theta0 = 80 degrees from the floor), and is let go from rest; top panel the floor is ice (frictionless, the foot free to slide), bottom panel the same stick with its foot pinned in a hinge; g = 9.81 m/s^2; both integrated by RK4 at 12000 steps per second (dt = 8.33e-05 s) with the landing located by bisection inside the step; shown at 1/5 speed on a 8 s cycle (480 frames) with the release 0.6 s into the cycle, 5 cycles in 40 s; drawn at 420 px per metre; deterministic, no seed
ice: RK4: the stick lies flat at 0.5166 s (quadrature of the energy form 0.5166 s, diff -8.8e-11 s); theta'^2 stays within 7.5e-14 rad^2/s^2 of the energy form and the energy drifts by 2.4e-15 of the energy released over 6199 steps; at the floor theta' = 5.3836 rad/s (closed form sqrt(3 g sin theta0 / L) = 5.3836), the tip comes down at L theta' = 5.384 m/s and the centre at (L / 2) theta' = 2.692 m/s; the tip's horizontal travel is (L / 2)(1 - cos theta0) = 41.32 cm, so it lands 58.68 cm from the foot's start, and the foot slides back the same 41.32 cm; the centre stays at x = (L / 2) cos theta0 = 8.68 cm (no horizontal force) and drops (L / 2) sin theta0 = 49.24 cm straight down; the foot slides fastest at 1.299 m/s at 50.5 degrees and its speed (L / 2) sin theta theta' is 0.000 m/s at the floor: it stops as the tip lands; the floor's push on the foot N = m (g + y_c'') is 0.917 weights at the release, at least 0.169 weights (at 27.4 degrees) and 0.250 weights at the floor, never zero, so the foot never leaves the floor
hinged: RK4: the stick lies flat at 0.7680 s (quadrature of the energy form 0.7680 s, diff -1.7e-10 s); theta'^2 stays within 2.2e-13 rad^2/s^2 of the energy form and the energy drifts by 7.7e-15 of the energy released over 9216 steps; at the floor theta' = 5.3836 rad/s (closed form sqrt(3 g sin theta0 / L) = 5.3836), the tip comes down at L theta' = 5.384 m/s and the centre at (L / 2) theta' = 2.692 m/s; the tip's horizontal travel is L (1 - cos theta0) = 82.64 cm, so it lands L = 100.00 cm from the foot; the hinge force (weights): vertical 0.977 at the release, at least 0.0075 (at 19.2 degrees) and 0.250 at the floor; horizontal (toward the foot, pulling the stick back) 0.698 at that angle and 1.477 at the floor; the horizontal to vertical ratio reaches 93.4 at 18.8 degrees (a rough floor would need a friction coefficient of 93.4), so no friction could hold this foot: it must be pinned
the two panels: the tip travels 41.32 cm on ice against 82.64 cm hinged, a ratio of 2.0000 (exactly 2 at any lean: on ice the centre does not move sideways, so the tip's travel is half the stick's foreshortening L (1 - cos theta0) instead of all of it); the ice stick is flat at 0.5166 s against 0.7680 s hinged, 1.487 times longer, 0.2514 s apart; both reach the floor at 5.3836 and 5.3836 rad/s (the same energy ends in the same rotation: at theta = 0 both kinetic energies are m L^2 theta'^2 / 6)
for the description (same release, other leans and a longer stick): 1 degree off vertical: ice flat at 0.811 s (quadrature 0.811), hinged 1.368 s (quadrature 1.368), 1.686 times longer; tip travel 49.13 cm against 98.25 cm, ratio 2.0000; both at 5.425 and 5.425 rad/s at the floor; 5 degree off vertical: ice flat at 0.603 s (quadrature 0.603), hinged 0.948 s (quadrature 0.948), 1.572 times longer; tip travel 45.64 cm against 91.28 cm, ratio 2.0000; both at 5.415 and 5.415 rad/s at the floor; a 1.2 m stick at 10 degrees: ice flat at 0.566 s, hinged 0.841 s (sqrt(1.2 / 1) = 1.0954 times the 1 m times, 0.566 and 0.841 s); tip travel 49.58 cm against 99.16 cm, ratio 2.0000
check at half the time step (24000 steps per second): ice flat at 0.516572 s (-1.6e-15), 5.383576 rad/s at the floor (+6.2e-15); hinged flat at 0.767978 s (+8.3e-15), 5.383576 rad/s at the floor (-1.5e-14)
schedule (video time, 1/5 speed): cycles of 8 s start at -0.40, 7.60, 15.60, 23.60, 31.60, 39.60 s (the first 0.40 s before the first frame); the release 0.6 s into each cycle at 0.20, 8.20, 16.20, 24.20, 32.20 s; the ice stick lies flat 2.58 s after the release at 2.78, 10.78, 18.78, 26.78, 34.78 s and the hinged stick 3.84 s after the release at 4.04, 12.04, 20.04, 28.04, 36.04 s; both lie flat with their readouts until the reset fade, which crossfades back to the standing stick over the last 0.8 s of each cycle (out over 7.20 to 7.60 s, in over 7.60 to 8.00 s after the cycle start, at 6.80, 14.80, 22.80, 30.80, 38.80 s); on the first frame the cycle is 0.40 s in (-0.040 s real after the release): the ice stick is at 80.0 degrees with its tip 0.0 cm along, the hinged stick at 80.0 degrees with its tip 0.0 cm along; title until 3 s; payoff card from 25.4 s; the title fades back in over the last 0.5 s and the last frame repeats the first (the scene is periodic: 40 s holds exactly 5 cycles)
text widths: overlay@34 842 px, title line 1@56 386 px, title line 2@56 793 px, legend@40 748 px, clock@28 390 px, clock rest@28 406 px, label ice@40 134 px, sublabel ice@28 361 px, fixed ice@28 284 px, readout ice@40 350 px, readout2 ice@28 252 px, label hinged@40 393 px, sublabel hinged@28 339 px, fixed hinged@28 284 px, readout hinged@40 350 px, readout2 hinged@28 312 px, mark start@28 76 px, payoff line 1@40 271 px, payoff line 2@40 559 px, payoff line 3@40 824 px, payoff line 4@40 830 px, payoff line 5@40 825 px, payoff line 6@40 671 px, payoff line 7@40 885 px
row check: the left column ends at x 433 px and the standing stick starts at x 470 px; the readout row starts at x 690 px and the second row at x 728 px
clearance: the hinged tip passes 24 px from the readout row, 14 px from the second row at the closest; the ice tip never goes right of x 716 px
Mon Sep 28 11:08:37 AM EEST 2026
```

Earlier measure runs, all with the same physics and the same numbers
(only the layout, the card and the schedule lines changed): the first
run at 11:02 failed the width assert (payoff line 7 "the ice foot stays
down: at least 0.17 weight" was 1008 px; reworded to "ice foot pushed up
at least 0.17 weight", 885 px). The second run at 11:04 failed the row
check (the left column ended at x 485 px against the standing stick at
x 420 px; px_per_m 450, foot_x_px 420): the scale went to 420 px/m, the
foot to x 470 and the ice sublabel from "no grip: the foot slides back"
(445 px) to "no grip: the foot slides" (361 px). The third run at 11:05
passed with first_cycle_at -1.6 and payoff_t 26.0; the final run has
first_cycle_at -0.4 and payoff_t 25.4 (the schedule set from the voice
timing). The RK4 numbers, the quadrature, the forces and the text
widths of the unchanged lines were identical in every run.

The brief's checks against the log: ice flat 0.517 s (log 0.5166 s),
hinged 0.768 s (0.7680 s), 1.487 times longer (1.487), both 5.38 rad/s
at the floor (5.3836 and 5.3836); ice tip travel 0.413 m (41.32 cm),
lands 0.587 m from the foot's start (58.68 cm), foot back 0.413 m
(41.32 cm); hinged tip travel 0.826 m (82.64 cm), lands 1.000 m (100.00
cm); ratio 2.000 (2.0000); N at least 0.169 weights at 27.4 degrees
(0.169 at 27.4); hinge vertical minimum 0.008 weights at 19.2 degrees
(0.0075 at 19.2); horizontal to vertical 93 near the floor (93.4 at 18.8
degrees, not at the floor, where it is 1.477 / 0.250 = 5.9); 1 and 5
degrees: ice 0.811 and 0.603 s, hinged 1.368 and 0.948 s (0.811, 0.603,
1.368, 0.948), ratio 2.000 (2.0000); 1.2 m at 10 degrees ice 0.566 s
(0.566). One stated reason in the brief does not hold: the centre's
vertical speed at the floor is not zero on ice, it is (L / 2) theta' =
2.692 m/s on both panels; the angular speeds agree because at theta = 0
both kinetic energies are m L^2 theta'^2 / 6 (the log says so).

### Production

- Sim: sims/icerod/icerod.py with projects/icerod/manifest.json (seed 0,
  fps 60, g 9.81, stick_length_m 1.0, lean_deg 10, description leans 1
  and 5, description length 1.2, steps_per_second 12000, sim_end_s 2.0,
  slow 5, cycle_s 8.0, release_at 0.6, first_cycle_at -0.4, reset_fade
  0.8, land_flash 0.35, scene_duration 40.0, px_per_m 420, foot_x_px
  470, title_until 3.0, payoff_t 25.4, payoff_hold 0.6, loop_fade 0.5,
  music_seed 94, music_gain 0.18, voice_offset 0.6, caption_y 0.75).
  RK4 on (theta, theta') with the ice equation (1 + 3 cos^2 theta)
  theta'' = 3 sin theta cos theta theta'^2 - (6 g / L) cos theta and the
  hinged theta'' = -(3 g / 2 L) cos theta; the landing by 60 bisections
  inside the crossing step; checked against the energy forms, the
  quadrature of the time to lie flat (theta = theta0 - s^2, 400,000
  midpoints) and a half-step rerun; the contact forces from the RK4
  states (N = m (g + y_c'') on ice; H_x = m x_c'', H_y = m (g + y_c'')
  on the hinge). Frames are drawn from the frame integer modulo the
  480-frame cycle, so the scene is exactly periodic; the last frame is
  the live frame 0.
- Layout (1080x1920): overlay at y 96 (34 px teal, drawn by compose);
  title two rows at y 190, 252 (56 px) until 3 s, then the legend "same
  stick, same lean, 1/5 speed" at y 236 (40 px) and the shared clock at
  y 290 (28 px); geometry layer y 330 to 1430 drawn at 2x and
  downsampled; ice band from y 330 with its floor at y 810, hinge band
  from y 880 with its floor at y 1360, slabs 32 px thick from x 60 to
  1020, the foot's start at x 470 (gold notch, "start" label 50 px under
  the surface), 420 px per metre; left column at x 40: label (40 px,
  panel colour), sublabel (28 px), fixed line "lies flat at 0.517 s" /
  "0.768 s" (28 px gold, hud only); right column to x 1040: live "tip
  NN cm along" (40 px, gold once landed) and "foot NN cm back" / "foot
  held by the pin" (28 px); the stick a 16 px bar (teal on ice, coral
  on the hinge) with a white-ringed middle and a gold tip cap; a dashed
  ghost of the start pose; on ice a faint teal dashed guide through the
  centre of mass; travel bars in the slab (gold for the tip, teal for
  the ice foot); a landing notch and a flash ring at the tip's landing;
  captions at y 1440 (64 px); the seven-line gold card from y 1572 at a
  48 px pitch (last row centred at 1860).
- Hook pre-tests (media/icerod/hooks/pretest.log, 10:27:58 to 10:28:07
  EEST), each through scripts/voiceover.sh, all five passed on the first
  pass; question onset = first silence_end (n=-35dB d=0.08) plus 0.6 s:
  hook1 "A stick falls on ice. Where does the tip land?" 2.19 s; hook2
  "Drop a stick on ice." 1.95 s; hook3 "A stick falls on ice. Where
  does its tip land?" 2.06 s; hook4 "Stick on ice. Where does the tip
  land?" 1.69 s; hook5 "A stick tips over on ice." 2.36 s. Kept hook4.
- Narration: projects/icerod/narration.txt, 106 words, the question at
  words 4 to 8, identical in the title, the hook and the payoff; numbers
  as words ("one meter", "Forty one centimeters", "Eighty three",
  "exactly half"); "pinned in a hinge", never "rough floor"; American
  "meter", "centimeters".
- Voice (media/icerod/voice.log): pass 1 at 11:02:36 (112 words, payoff
  "Forty one centimeters along. Pinned in a hinge, eighty three.")
  failed, whisper heard "along" as "long" (diff token 85). Pass 2 at
  11:03:16 ("Forty one centimeters, on ice. Eighty three, pinned in a
  hinge. Exactly half as far, ...", 108 words) passed at 33.541 s, but
  the timing put the mechanism words 2 to 4 s after each stick had
  landed on the 8 s cycle, so the narration was re-timed (setup
  shortened to "On top, ice. Watch the middle.", "Once more, side by
  side." added before the numbers). Pass 3 at 11:07:34 (106 words): "ok:
  transcript matches narration (34.864762s) -> media/icerod/voice.wav".
  The voice ends at 35.46 s of video.
- Timing (scripts/voice-timing.py media/icerod/voice.wav 0.6, in
  media/icerod/timing.log): 0.60 to 2.95 "Stick on ice, where does the
  tip land?"; 2.95 to 4.26 "A one meter stick"; 4.26 to 5.95 "leaning a
  little, let go."; 5.95 to 7.17 "On top, ice."; 7.17 to 9.53 "Watch the
  middle, it drops straight down."; 9.53 to 11.09 "and the foot slides
  back."; 11.09 to 11.87 "No grip."; 11.87 to 14.23 "So nothing pushes
  the stick sideways."; 14.23 to 16.93 "Below, the same stick, the same
  lean,"; 16.93 to 20.58 "but the foot is pinned in a hinge, the stick
  swings around the pin,"; 20.58 to 23.43 "and the tip swings wide, so
  stick on ice."; 23.43 to 26.75 "Where does the tip land? Once more,
  side by side."; 26.75 to 28.80 "41 cm, on ice."; 28.80 to 30.79 "83.
  Pinned in a hinge."; 30.79 to 32.35 "Exactly half as far"; 32.35 to
  35.46 "because the middle drops straight down and the foot slides
  back." Question onset on the full take: first silence_end 0.940 s in
  the wav plus 0.6 = 1.54 s (media/icerod/silences.log).
- Schedule: cycles of 8 s start at -0.4, 7.6, 15.6, 23.6, 31.6 s;
  releases at 0.2, 8.2, 16.2, 24.2, 32.2 s; the ice stick is flat 2.58
  s after each release (2.78, 10.78, 18.78, 26.78, 34.78 s) and the
  hinged stick 3.84 s after (4.04, 12.04, 20.04, 28.04, 36.04 s); both
  hold flat until the reset fade at 6.8, 14.8, 22.8, 30.8, 38.8 s.
  "it drops straight down" (7.17 to 9.53) and "the foot slides back"
  (9.53 to 11.09) sit inside the ice fall 8.2 to 10.78; "pinned in a
  hinge, the stick swings around the pin" (16.93 to 20.58) inside the
  hinge swing 16.2 to 20.04; the ice stick lands at 26.78 as "Forty
  one" starts (caption 26.91 to 27.57) and the hinged stick at 28.04
  before "Eighty three" (28.56 to 29.54), both flat with the gold
  readouts 41 and 83 until 30.8; "Exactly half as far" (30.53 to 31.85)
  is spoken over the reset fade with the card on screen; the last
  release at 32.2 puts the fall under "because the middle drops
  straight down and the foot slides back" (32.35 to 35.46). The card
  (payoff_t 25.4, lit at 26.0) lights inside "Once more, side by side."
  right after the spoken question (23.62 to 25.27).
- Smoke frames (--frames, 11:09): 11 PNGs at 0.0, 1.5, 8.8, 10.2, 18.5,
  26.9, 29.0, 31.0, 33.5, 39.6, 39.98 s; 0.0, 8.8, 18.5 and 29.0 viewed
  before the render: title rows clear of the overlay and the labels,
  the left column clear of the standing stick, the readouts clear of
  the hinged tip's path (clearance 24 and 14 px printed), the card
  rows under the caption band, nothing at the frame edge. One blemish
  found and fixed: the ice foot readout read "foot -0 cm back" at rest
  (negative zero); the slide is clamped at 0 before formatting.
- Footage: render 11:09:12 to 11:09:39 (media/icerod/render.log): loop
  check 0 px, periodicity check 0 px, loop step 0 px (the seam is inside
  the 0.6 s rest before the release, so the two frames at the seam are
  the same standing picture); media/icerod/footage.mp4 2400 frames.
- Compose: scripts/compose.sh 11:09:53 to 11:10:21 (compose.log): music
  seed 94, 40.00 s; captions 36 chunks; final.mp4 40.000000 s; preview
  40.066667 s; sheet 8x5 at 1 fps.
- Text widths (PIL, from measure.log, all under 950 px): overlay 842,
  title 386 / 793, legend 748, clock 390 / 406, label ice 134, sublabel
  ice 361, fixed ice 284, readout ice 350, readout2 ice 252, label
  hinged 393, sublabel hinged 339, fixed hinged 284, readout hinged 350,
  readout2 hinged 312, start 76, payoff 271 / 559 / 824 / 830 / 825 /
  671 / 885.

### Local QA

- Frames extracted from media/icerod/final.mp4 (never edited) and viewed
  with the Read tool:
  - frame-0.02.png: overlay, two title rows ("Stick on ice." / "Where
    does the tip land?"), both sticks standing at 80 degrees with the
    gold tip caps and the ringed middles, "tip 0 cm along", "foot 0 cm
    back", "foot held by the pin", start notches, the ice guide; no
    caption, no card. Clean.
  - frame-1.6.png: title still up, caption "Where does the tip" at y
    1440; both sticks falling (ice tip 19 cm along, foot 19 cm back;
    hinged tip 11 cm), ghost start poses, travel bars in the slabs.
  - frame-9.0.png: legend and clock "0.160 s after the release" in
    place of the title, fixed lines "lies flat at 0.517 s" / "0.768 s";
    ice stick just released (tip 6 cm along, foot 6 cm back); caption
    "It drops straight".
  - frame-18.5.png: ice stick low (39 cm), hinged stick at 32 cm
    swinging; caption "hinge.".
  - frame-26.9.png: the ice stick flat with the flash ring at the tip,
    "tip 41 cm along" and "foot 41 cm back" in gold, the landing notch;
    the hinged stick still swinging at 47 cm; the card lit (seven gold
    rows); caption "side.". "Forty one" starts 0.01 s later.
  - frame-29.0.png: both flat, "tip 41 cm along" and "tip 83 cm along"
    in gold, both landing notches; caption "Eighty three, pinned"; card
    lit. The payoff numbers are on screen when spoken.
  - frame-31.0.png: both flat, the readouts and the sticks dimming in
    the reset fade; caption "Exactly half as far,"; the card carries
    "41 cm along on ice, 83 cm in a hinge" and "half: ...".
  - frame-39.98.png: title back, hud gone, both sticks standing at 80
    degrees with the readouts at 0, the same picture as frame-0.02.
  - sheet.png (40 thumbnails at 1 fps): the title for the first 3 s,
    then the legend and clock; five drops with the resets at 7, 15,
    23, 31, 39 s; captions readable in every thumbnail from 1 to 35 s;
    the card from 26 s; no clipped text, nothing at the frame edge.
- Question: on screen from frame 0 in the title (386 / 793 px), spoken
  from 1.54 s ("Stick on ice." caption 0.600 to 1.587, "Where does the
  tip" 1.587 to 2.902, "land?" 2.902 to 3.231).
- Captions: media/icerod/captions.filter, 36 chunks, 106 words, matches
  projects/icerod/narration.txt word for word (script check True),
  longest chunk 20 characters; "Forty one" 26.913 to 27.571,
  "centimeters, on ice." 27.571 to 28.558, "Eighty three, pinned"
  28.558 to 29.544, "in a hinge." 29.544 to 30.531, "Exactly half as
  far," 30.531 to 31.847.
- Bands: signalstats over all 2,400 footage frames: the caption band
  (rows 1440 to 1530) and the overlay band (rows 96 to 130) have YMAX
  28 in every frame (background only), so the sim draws nothing under
  the captions or the overlay.
- Loop: footage last frame equals the first (0 px). In final.mp4 frame
  2399 against frame 0: 21,831 px over 8 levels, 388 over 32, max 85,
  mean 0.48 (h264 quantisation, the same order as days 28 and 29);
  frame 2398 against 2399 18,902 px over 8 (codec noise on identical
  source frames), so the seam is invisible.
- ffprobe: h264 1080x1920 yuv420p 60/1, 2400 frames; aac 22050 Hz mono;
  40.000000 s; 3,696,663 bytes; moov before mdat (faststart).
- md5sum media/icerod/final.mp4: 75386b47c9d8f419780a6aefb58d0bf9
- Narrated numbers against measure.log: "one meter stick" (L = 1 m);
  "Forty one centimeters, on ice" (41.32 cm); "Eighty three, pinned in
  a hinge" (82.64 cm); "Exactly half as far" (ratio 2.0000); "the
  middle drops straight down" (the centre stays at x = 8.68 cm, drops
  49.24 cm); "the foot slides back" (41.32 cm). Card: 41 / 83 cm, 0.517
  / 0.768 s, 5.38 rad/s (5.3836), 0.17 weight (0.169).
- Metadata check: every number in the description read against
  media/icerod/measure.log after the final run (travel 41.32 / 58.68 /
  82.64 / 100.00 cm, centre 8.68 / 49.24 cm, times 0.5166 / 0.7680 s
  with the quadrature diffs -8.8e-11 / -1.7e-10, 1.487, 0.2514 s,
  5.3836 rad/s, 5.384 and 2.692 m/s, N 0.917 / 0.169 at 27.4 / 0.250,
  foot 1.299 m/s at 50.5 degrees, hinge 0.977 / 0.0075 at 19.2 / 0.250,
  0.698 / 1.477, 93.4 at 18.8, leans 0.811 / 1.368 (1.686), 0.603 /
  0.948 (1.572), 49.13 / 98.25, 45.64 / 91.28, 1.2 m 0.566 / 0.841,
  1.0954, 49.58 / 99.16, checks 7.5e-14 / 2.2e-13, 2.4e-15 / 7.7e-15,
  6199 / 9216 steps, half step 1.6e-15 / 8.3e-15).

### Metadata

projects/icerod/metadata.json: title "Stick on ice: where does the tip
land? 41 cm on ice, 83 cm pinned in a hinge, exactly half" (90
characters, no angle brackets); description 3,744 characters with the
model, the "Measured:" list, the "Why:" paragraph, the rerun line and
the AI-made line; 11 tags; categoryId 27; privacyStatus private;
containsSyntheticMedia true; selfDeclaredMadeForKids false.

### Deviations from the brief

- Hook "Stick on ice. Where does the tip land?" instead of "A stick
  falls on ice. Where does the tip land?": the pre-tests put the
  question at 1.69 s against 2.19 s (2.19 is over two seconds). The
  title, hook and payoff all carry the same question.
- The horizontal to vertical hinge force ratio peaks at 93.4 at 18.8
  degrees, near the vertical force's minimum, not "near the floor"; at
  the floor it is 1.477 / 0.250 = 5.9. The card and the description
  state the peak and its angle.
- The brief's reason for the equal angular speeds ("on ice the centre's
  vertical speed is zero at the floor") is wrong: the centre comes down
  at 2.692 m/s on both panels. The description gives the right reason
  (equal kinetic energies m L^2 theta'^2 / 6 at theta = 0).
- The narration's payoff says "Forty one centimeters, on ice. Eighty
  three, pinned in a hinge." instead of "forty one centimeters along":
  whisper heard "along" as "long" after "centimeters".
- The last panel event under the payoff: "Exactly half as far" (30.53
  to 31.85) is spoken while the readouts fade in the reset (30.8 to
  31.6); the card keeps 41 and 83 on screen, and the next fall runs
  under "because the middle drops straight down and the foot slides
  back".
- The loop seam sits in the 0.6 s rest before a release, so frame 0
  (the thumbnail) shows the two sticks standing with the title, not
  motion in progress; the fall starts at 0.2 s.
- The card has seven lines at a 48 px pitch (line 7 of the first draft
  was 1008 px and was reworded).
- The overlay carries "10 degrees off vertical | 1/5 speed | no seed";
  the narration's setup number is "one meter", and the 1/5 factor is
  also in the legend.

## Niche note

[produced 2026-09-28 as "Stick on ice: where does the tip land? 41 cm
on ice, 83 cm pinned in a hinge, exactly half"; measured the tip 41.32
cm along on ice ((L / 2)(1 - cos 80), the foot back 41.32 cm, the
centre fixed at 8.68 cm) against 82.64 cm pinned in a hinge, ratio
2.0000 at any lean; flat at 0.5166 s on ice against 0.7680 s hinged
(1.487 times), both 5.3836 rad/s at the floor; ice foot push at least
0.169 weights at 27.4 degrees; hinge vertical force down to 0.0075
weights at 19.2 degrees, horizontal to vertical up to 93.4; 1 and 5
degrees off vertical 0.811 / 1.368 s and 0.603 / 0.948 s; RK4 at 12,000
steps a second within 1e-10 s of the quadrature; task 20260928-101835]

## Upload

- orchestrator review (2026-09-28T11:29:18+03:00): task evidence, sheet.png and the frames in
  /tmp/day30/review/icerod inspected; readouts match measure.log and the
  RK4 check in /tmp/day30/check_icerod2.py; approved for upload
- upload attempt 3 of 5 for the quota day that began 2026-09-28T10:00
  EEST, recorded at 2026-09-28T11:29:18+03:00 before starting scripts/yt-upload.py; two
  attempts were on record since the boundary (crash published, pegswing
  private with its gate pending)
- uploaded private as ixDyblhn3ag at 2026-09-28T11:29:25+03:00
  (https://youtu.be/ixDyblhn3ag); channels.list 1 unit + videos.insert
  1,600 units; media/icerod/upload.log
- scripts/yt-qa.py icerod ixDyblhn3ag --wait --publish in the foreground:
  gate 15 of 15 on the first poll (processed, succeeded, hd, 1080x1920,
  title, description and tags match, category 27, not made for kids,
  PT41S, private before publish); published at 2026-09-28T11:30:01+03:00;
  re-read privacyStatus=public; yt-qa quota 54 units;
  media/icerod/publish.log
- attempt 3 of 5 complete at 2026-09-28T11:31:05+03:00: 1,655 units; slot 3 of 3 resolved as
  published

### Quota
- attempt 3 of the hard cap of 5 for the quota day that began
  2026-09-28T10:00 EEST; cost 1 + 1,600 + 54 = 1,655 units (the
  channels.list verification inside yt-upload.py, the insert, the gate run's
  single read, update and re-read as printed by yt-qa.py); day total after
  three attempts 1,655 + 1,656 + 1,655 = 4,966 units plus 5 for the 10:05
  stats refresh and 5 for the 11:35 refresh, target of three met
