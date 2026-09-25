# Produce short: Bucket over the head, 36 rpm beside 21 rpm on the same arm

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day27

## Goal

Backlog idea (trend research 2026-09-25, task 20260925-101408, pillar 2
chaos and physics, rotation; read the full entry under "Added by trend
research 2026-09-25" in docs/niche.md):
"Bucket over the head: a bucket of water on a 1 m arm turned at a
steady 36 rpm beside 24 rpm, the water as parcels that fly free the
moment the bucket stops pushing them; measure the slowest turn that
keeps the water in and where it spills; expect 29.9 rpm (one turn
every 2.006 s, omega = sqrt(g / r)), the 36 rpm water pressing on the
bucket with 0.45 g at the top and the 24 rpm water leaving 49.9
degrees before the top at 2.51 m/s and landing 0.69 m past the pivot
line 0.90 s later; say the arm is driven at constant rpm; the fast
panel is periodic so the short loops; deterministic, no seed."

Orchestrator notes (2026-09-25, before this brief): the model is
kinematic plus free flight. The arm turns at a steady rate omega (a
motor, or "your arm keeps a steady rate"; state it); the water sits at
radius r = 1.00 m from the pivot (the water surface; the bucket's open
top faces the pivot); at angle phi from the top the bucket floor
pushes each parcel with N = m (omega^2 r - g cos phi), and a parcel
leaves the moment N would go negative, with the bucket's velocity
omega r along the tangent, then flies free under g (no air) until it
hits the floor or the person at the pivot. 36 rpm: omega = 3.770
rad/s, omega^2 r = 14.21 m/s^2 above g, N at the top is 0.449 m g,
the water never leaves. 24 rpm: omega = 2.513 rad/s, omega^2 r =
6.317, cos phi = 0.644, the water leaves 49.9 degrees before the top
on the way up, at 2.513 m/s, falls inside the circle (the arm keeps
pulling the bucket round faster than gravity pulls the water) and
lands on the far side; the threshold is omega = sqrt(g / r) = 3.132
rad/s = 29.9 rpm, one turn every 2.006 s. Print all of these from the
parcel integration against the closed forms (the leave angle, the
leave speed, the threshold rpm and period, the 0.45 g at the top,
where and when the parcels land, the flight time), with the pivot
height above the floor stated (say 1.5 m, so the bottom of the circle
clears the floor by 0.5 m). Give the parcels a spread of radii inside
the bucket (0.90 to 1.00 m, the bucket depth) so they leave over a
small range of angles and print that range; the headline number is
for the water surface at r = 1.00 m. Both panels are periodic: 36 rpm
makes 24 turns in 40 s and 24 rpm 16 turns, so the scene loops if the
slow bucket is refilled each turn; the cleanest device is a pool at
the bottom of the swing that the bucket dips into (both panels), or a
plain refill at the bottom stated in the legend; the producer chooses
and says so on screen or in the description. Draw the person at the
pivot (a head and shoulders) so the spilled water landing on or past
them reads at a glance. Two panels stacked, "36 turns a minute" above
and "24 turns a minute" below, the same arm and bucket; the producer
may pick other round rates as long as one is above 29.9 rpm and one
below, both periods divide the scene length, and the sim prints them.

Day twenty-seven, third slot. Chosen because it is a question everyone
has asked, two panels on the same arm that end differently (stays in
against pours out), continuous periodic rotation with an exact
threshold, the loop-the-loop and hoop-bead family (965, 925) and the
merry-go-round just published. Question in the first two seconds:
"Swing a bucket over your head. How slow before it spills?" (or the
producer's better wording, kept identical in the title, the hook and
the payoff). Setup number: a one meter arm (the two rates sit on the
panel labels); payoff number: thirty turns a minute (one turn every
two seconds). The 50 degrees, the 0.45 g and the landing spot go to
the description and the readouts.

Print the schedule in video time, the loop check and the on-screen
text widths. Make the last frame equal the first. Music seed 85.

## Claim

A bucket of water on a one meter arm turned at a steady 36 turns a
minute keeps its water through every turn (0.45 g still presses it
into the bucket at the top); the same bucket at 24 turns a minute
pours out 50 degrees before the top, every turn; the slowest turn that
holds the water is 30 a minute, one turn every 2.0 s. Every number in
the narration is printed by the sim before the script is written (the
producer may change the round values; the sim sets the claim).

## Evidence

### Measurements

(recorded after the measure-only run, before scripting)

`sims/bucket/bucket.py --measure-only` with `projects/bucket/manifest.json`
(a bucket of water on an arm of 1.00 m from the pivot at your shoulder
to the water surface, the bucket's open top facing the pivot and the
water filling it from 1.00 to 1.10 m as 25 parcels on a 5 by 5 grid,
radii 1.00 to 1.10 m and -0.075 to 0.075 m across the bucket; the arm
turns clockwise on screen at a steady rate, 36 rpm above (omega 3.7699
rad/s, 1.6667 s per turn) and 21 rpm below (omega 2.1991 rad/s, 2.8571 s
per turn); the pivot 1.5 m above the floor, so the bucket floor at 1.115
m clears the floor by 0.385 m at the bottom of the swing; you at the
pivot seen from the side, head radius 0.11 m centred 0.21 m above the
pivot, body 0.28 m deep; g 9.81 m/s^2; a parcel at radius rho on the arm
is pushed by the bucket floor with N = m (omega^2 rho - g cos phi) at phi
from the top, the same for every parcel across the bucket's width, and
leaves when N would go negative, then flies free under g with no air,
stepped at 10,000 steps per second (dt 1e-4 s) against the closed forms;
the slow bucket refilled at the bottom of each turn; real time, 24 fast
turns and 14 slow turns in 40 s; drawn at 200 px per metre; deterministic,
no seed; run at 10:45:40 EEST, log in `media/bucket/measure.log`):

- threshold: the surface water (r = 1 m) stays in when omega^2 r >= g,
  omega = sqrt(g / r) = 3.1321 rad/s = 29.91 rpm, one turn every 2.0061
  s (29.9 rpm and 2.0 s to a tenth, 30 rpm to the nearest whole turn);
  the deeper water at r = 1.1 m holds down to 28.52 rpm, so the surface
  sets the limit; whole-rpm sweep by stepping the arm through a turn: 26
  rpm leaves 40.9 degrees before the top (-0.244 g at the top), 27 rpm
  35.4 degrees (-0.185 g), 28 rpm 28.8 degrees (-0.124 g), 29 rpm 19.9
  degrees (-0.060 g), 30 rpm holds (+0.006 g at the top), 31 rpm holds
  (+0.074 g), 32 rpm holds (+0.145 g); the slowest whole rate that holds
  is 30 rpm (2.000 s per turn, +0.0061 g at the top) and 29 rpm spills
- fast panel (36 rpm): omega^2 r = 14.212 m/s^2 at the surface against g
  = 9.81; the push on the surface water is 0.449 g at the top (0.45 g),
  2.449 g at the bottom and 1.449 g at the sides; the smallest push on
  any parcel through the turn is 0.449 g (the surface, at the top), so
  no parcel leaves; stepping every parcel through a full turn finds no
  leave
- slow panel (21 rpm): omega^2 r = 4.836 m/s^2 at the surface, below g,
  so the push on the surface water reaches zero on the way up at cos phi
  = 0.4930, phi = 60.46 degrees before the top (stepped 60.46, diff
  1.5e-8 degrees; 60 degrees to the nearest degree, 29.5 degrees above
  the horizontal); at the top the bucket would have to pull with 0.507
  g; the surface parcel on the arm leaves at (-0.870, 0.493) m from the
  pivot at omega r = 2.199 m/s (vx 1.084, vy 1.913), rises to an apex
  0.680 m above the pivot (0.360 m above the top of your head) at
  -0.659 m from the pivot line, and comes down on your body at (-0.140,
  -0.443) m, 1.06 m above the floor, after 0.673 s of flight (closed
  form -0.140 m after 0.673 s, diffs 1.2e-13 m and 2.9e-15 s); closest
  approach 0.196 m to your head; closest approach to the bucket, which
  keeps turning, 0.300 m at 0.27 s once it has separated by 0.3 m (it
  never meets the bucket again)
- all 25 parcels: they leave between 60.5 and 57.2 degrees before the
  top (the surface first, the floor water at r = 1.1 m last, 0.026 s
  later), at 2.199 to 2.425 m/s; stepped leave angles within 1.8e-7
  degrees of the closed form; apexes 0.631 to 0.852 m above the pivot;
  flights 0.544 to 0.815 s; 23 come down on your body, 2 on your head, 0
  on the floor (the body hits from 1.77 to 0.29 m above the floor, x
  from -0.140 to -0.066 m); closest approach to the turning bucket 0.300
  m; Verlet hits within 2.4e-13 m and 4.4e-14 s of the closed form
- for the description (the surface water on the same arm, other rates):
  15 rpm leaves 75.4 degrees before the top at 1.571 m/s, apex 0.37 m
  above the pivot, hits the floor 0.663 m short of the pivot line after
  0.772 s; 20 rpm leaves 63.4 degrees at 2.094 m/s, apex 0.63 m, hits
  your body 0.27 m above the floor after 0.806 s; 21 rpm leaves 60.5
  degrees at 2.199 m/s, apex 0.68 m, hits your body 1.06 m above the
  floor after 0.673 s; 24 rpm leaves 49.9 degrees at 2.513 m/s, apex
  0.83 m, hits the floor 0.668 m past the pivot line after 0.886 s; 26
  rpm leaves 40.9 degrees at 2.723 m/s, apex 0.92 m, floor 1.164 m past
  after 0.884 s; 28 rpm leaves 28.8 degrees at 2.932 m/s, apex 0.98 m,
  floor 1.715 m past after 0.855 s; 29 rpm leaves 19.9 degrees at 3.037
  m/s, apex 0.99 m, floor 1.997 m past after 0.819 s; 30 rpm holds,
  0.006 g at the top; 36 rpm holds, 0.449 g at the top
- schedule printed by the sim (first manifest, fast_top_at 0 s and
  slow_leave_at -0.4 s, to be set from the voice timing): the fast
  bucket is at the top at 0 s and every 1.6667 s after; the slow bucket
  refills at the bottom 0.949 s before each leave; the surface water
  leaves at -0.4 + 2.85714 k s, i.e. at 2.46, 5.31, 8.17, 11.03, 13.89,
  16.74, 19.60, 22.46, 25.31, 28.17, 31.03, 33.89, 36.74, 39.60 s, the
  floor water 0.026 s after; the water lands 0.673 to 0.815 s after each
  leave and the splash fades until the refill 1.908 s after the leave;
  on the first frame the slow water is 0.4 s into its flight and the
  fast bucket is at the top; title until 2.4 s, then the legend and the
  fixed readouts; payoff card from 30 s; the title fades back in over
  the last 0.5 s and the last frame repeats the first (the scene is
  periodic: 40 s holds exactly 24 fast turns and 14 slow turns)
- text widths (DejaVuSans-Bold): overlay 841 px at 34 (a first draft,
  "arm 1 m | 36 rpm above, 21 rpm below | no seed", measured 930 px and
  was shortened before any render); title lines 736 and 800 px at 56;
  legend 823 px at 40, tag line 709 px at 28; panel labels 403 px, push
  readout 265 px, "spills" 117 px at 40; fixed lines 290, 271, 463 and
  433 px, "you" tag 57 px at 28; payoff lines 524, 572, 777 and 756 px
  at 40; nothing over 950 px; the sim asserts every line under 950 px

Rate choice: the brief's 24 rpm was run first (10:40:30 EEST, the same
sim before the landing print handled parcels that never cross the pivot
line): the surface water leaves 49.92 degrees before the top at 2.513
m/s, crosses the pivot line 0.457 m above the pivot and lands on the
floor 0.668 m past it after 0.886 s, but its closest approach to the
drawn head is 0.006 m and the trailing parcels (0.075 m behind the arm)
come down on the head, so at 24 rpm the water grazes the head and lands
just past you, a mixed outcome that no plain sentence describes. A sweep
of 20 to 26 rpm with the same flight code (25 and 26 rpm clear the head
by 0.16 m or more and land 0.9 to 1.6 m past you; 20 to 22 rpm come
down on you) picked 21 rpm: every one of the 25 parcels comes down on
you, 21 rpm makes exactly 14 turns in 40 s, and 36 rpm stays as briefed.
The claim's "24 turns a minute pours out 50 degrees before the top"
therefore becomes "21 turns a minute lets go 60 degrees before the top
and all of it comes down on you"; the 36 rpm, the 0.45 g at the top and
the 30 a minute threshold stand as written.

Narration numbers: one meter (setup; the arm, on the overlay "arm 1 m"
and in the narration; the two rates stay on the panel labels); thirty a
minute (payoff; the sweep's slowest whole rate that holds, 30 rpm with
+0.006 g at the top while 29 rpm spills; the closed-form limit 29.91 rpm
and one turn every 2.006 s go to the card as "limit 29.9 rpm" and "one
every 2.0 s"). The 60 degrees, the 0.45 g, the apex, the landing on
your body, the flight time and the other rates go to the readouts and
the description.

### Production

- layout (`sims/bucket/bucket.py`): overlay "arm 1 m | 36 rpm above, 21
  below | no seed" at y 96 (drawn by compose from the manifest), title
  "Bucket over your head: / how slow before it spills?" at y 190/252
  (56 px) for the first 3 s, then the legend "same arm, same bucket,
  two speeds" at y 236 (40 px) and the tag "side view, refilled at the
  bottom of each turn" at y 290 (28 px, muted); two panels stacked at
  200 px per metre, each with its label "36 turns a minute" / "21 turns
  a minute" top left at x 60 and the live readout top right at x 1020
  ("push x.xx g" while the water is in the bucket, "spills" in coral
  once it has left), the fast panel with its pivot at (600, 564) and
  its floor line at y 864, the slow panel with its pivot at (600, 1118)
  and its floor at y 1418; in each panel a dashed ring at the water's
  mid radius, you as a grey rounded torso, neck and head with a "you"
  tag (head 0.11 m centred 0.21 m above the pivot), the arm as a line
  from the pivot, the bucket as a trapezoid with its open top toward
  the pivot, the water as a teal block while it is in the bucket and as
  25 teal parcels with 0.1 s trails once it has left, then teal
  splashes on you that fade until the refill; a gold arc with tick
  marks from the leave angle to the top of the slow ring; the fixed
  lines "push at top 0.45 g" / "holds, every turn" at y 786/820 in the
  fast panel and "lets go 60 deg before the top" (gold) / "all of it
  comes down on you" at y 1340/1374 in the slow panel (28 px, shown
  with the legend from 3 s); geometry band y 320 to 1436 drawn at 2x
  and reduced; captions at caption_y 0.75 (y 1440 to 1520); the
  four-line card from y 1592 (40 px, 56 px pitch); the HUD (legend,
  tag, fixed lines, arc, card) fades out over the first 0.25 s of the
  last 0.5 s and the title fades in over the last 0.25 s, the last
  frame equal to the first
- whisper pre-tests (10:47:58 to 10:48:18 EEST, `media/bucket/hooks/`,
  log `hooks/pretest.log`): every passage passed on its first pass:
  hook1 "Bucket over your head, how slow before it spills? A one meter
  arm, turned at a steady rate." (5.27 s), hook2 "A bucket over your
  head. How slow before it spills? ..." (5.89 s), hook3 "Swing a bucket
  over your head. How slow before it spills? ..." (5.68 s), the
  mechanism group "Watch the fast bucket. ... Every turn." (15.49 s;
  "flies free" and "comes down on you" survived) and the payoff group
  "Same arm, same bucket, two speeds. ... Thirty a minute. Any slower,
  and it pours out on you." (10.66 s; the number came back as "30");
  question onsets from silencedetect on the hook wavs (-35 dB, 0.08 s,
  plus the 0.6 s offset): hook1 1.84 s, hook2 2.12 s, hook3 2.13 s;
  hook1 kept (comma, four words before the question); the title and
  the card carry the same words with a colon, the narration a comma
- narration (`projects/bucket/narration.txt`): 104 words, 15
  sentences, "one meter" and "thirty a minute" the only numbers, both
  in words; no "still", "pull", "spread", "straight", "a hundred" or
  sentence-initial "Where" (the whisper mishearing list)
- smoke frames (`--frames`, three passes 10:50 to 10:52 EEST at 0, 1.5,
  1.99, 2.9, 12.0, 21.5, 24.3, 25.2, 29.85, 31.0, 39.6, 39.98 s): pass
  1 found the slow panel's floor line at rows 1428 to 1431, inside the
  1420 to 1530 caption exclusion band; fixed by lifting both pivots 12
  px (564/1118, geometry band from 320); pass 2 put the lowest
  geometry row at 1419 with no other defect; pass 3, after the
  schedule print was rewritten to describe the frame-0 state (the slow
  bucket empty, 1.71 s after its leave, splashes fading until the
  refill at 0.19 s), clean: title over both panels at 0 s, the caption
  band empty, the parcels in flight at 24.3 s, the splashes on you at
  25.2 s, the card lit at 29.85 s, the title back at 39.98 s
- voice (`scripts/voiceover.sh bucket`, log `media/bucket/voice.log`):
  pass 1 at 10:48:35 EEST failed the round trip (whisper wrote "sp
  ills" for the last "spills"); pass 2 at 10:49:35 EEST with the same
  text passed, "ok: transcript matches narration (32.066757s)";
  voice.wav 32.07 s, ends at 32.67 s of video with the 0.6 s offset
- timing (`scripts/voice-timing.py media/bucket/voice.wav`, log
  `media/bucket/timing.log`, video time): "Bucket over your head."
  0.60 to 1.81, the question "how slow before it spills" from 1.81
  (the pause after "head" spans 1.64 to 1.99 s, so the word "how"
  sounds at 1.99 s), the setup to 6.44, "Same bucket." 6.44 to 7.41
  (heard "Sane", harmless: the gate is the full-file round trip), "Two
  speeds, the top one is fast." 7.41 to 9.71, "The bottom one is
  slow." 9.71 to 11.16, "Watch the fast bucket ... at the top of every
  turn," 11.16 to 15.44, "The bucket pushes on the water." 15.44 to
  17.14, "so the water rides along and holds." 17.14 to 19.27, "Now
  the slow bucket, on the way up." 19.27 to 21.36, "The push runs out
  before the top." 21.36 to 23.51, "The water flies free and comes
  down on you." 23.51 to 26.26, "every turn so how slow before it
  spills 30 a minute" 26.26 to 30.21, "Any slower and it pours out on
  you." 30.21 to 32.67
- schedule (manifest): fast_top_at 0 (the fast bucket at the top on
  frame 0, then every 1.6667 s), slow_leave_at 1.142857 so the slow
  water leaves at 1.14, 4.00, 6.86, 9.71, 12.57, 15.43, 18.29, 21.14,
  24.00, 26.86, 29.71, 32.57, 35.43, 38.29 s: the 24.00 s leave sits
  under "The water flies free and comes down on you." (23.51 to 26.26;
  captions "The water flies" 24.03 to 24.96, "free, and comes down"
  24.96 to 26.19), its parcels hit you from 24.54 to 24.82 s, before
  "on you" (26.19 to 26.81); the 29.71 s leave has the water in the air
  during "Thirty a minute." (caption 29.27 to 30.20) and on you from
  30.25 to 30.53 s under "Any slower, and it pours out on you." (30.20
  to 32.67); title_until 3.0 (the question caption "before it spills?"
  runs to 3.38 s); payoff_t 29.2 with a 0.6 s fade, so the card is
  fully lit at 29.8 s inside the "Thirty a minute." caption
- footage (`nix develop -c python3 sims/bucket/bucket.py`, log
  `media/bucket/render.log`): the first render 10:52:51 to 10:53:37
  EEST passed the loop check (0 px) but the periodicity check drew the
  scene live at 40 s 395 px different from 0 s (max channel difference
  106), all of it in rows 339 to 467, columns 577 to 622, the fast arm
  and bucket at the top: theta = 150.796 rad and 0 rad give the same
  positions to 1e-11 px and PIL rounds the two edges differently;
  fixed by rounding the drawn coordinates to 1e-4 px in the layout
  helper and re-rendered 10:55:19 to 10:55:51 EEST: loop check 0 px,
  periodicity check 0 px, loop step 6434 px (the fast arm turns 3.60
  degrees per frame, the slow arm 2.10); 2,400 frames, eight forked
  workers, h264 crf 16 yuv420p 60 fps, footage.mp4 5,406,130 bytes,
  40.00 s; `--measure-only` re-run into `media/bucket/measure.log` at
  10:56 EEST with the final manifest and sim
- compose (`scripts/compose.sh bucket`, log `media/bucket/compose.log`):
  first run 10:54:17 to 10:54:42 EEST on the first footage, second run
  10:55:51 to 10:56:07 EEST on the re-render: music seed 85 at 40.00 s
  (gain 0.18), 33 caption chunks (longest 20 characters, "Thirty a
  minute." one chunk), final.mp4 5,312,607 bytes 40.000000 s,
  preview.mp4 540x960 30 fps 1,235,776 bytes 40.066667 s, sheet.png
  8x5 at 1 fps 539,073 bytes
- text widths (measure.log, PIL at the drawn sizes): overlay 841 px,
  title lines 736 and 800 px, legend 823 px, tag 709 px, labels 403 px,
  fixed lines 290, 271, 463 and 433 px, push readout 265 px, "spills"
  117 px, card lines 524, 572, 777 and 756 px, all under 950 px; the
  first overlay draft "arm 1 m | 36 rpm above, 21 rpm below | no seed"
  measured 930 px and was shortened

### Local QA

- frames (`media/bucket/frame-<t>.png` from final.mp4 at 0.02, 2.0,
  24.3, 25.2, 29.85 and 39.98 s, plus `sheet.png`) inspected: 0.02 s:
  overlay and title from frame 0 over both panels, the fast bucket just
  past the top with "push 0.46 g", the slow bucket empty low on the
  right with "spills" and the last splashes fading on you; 2.0 s:
  caption "head, how slow" in the band under the panels, the title
  still up, the fast bucket on the right ("push 1.14 g"), the slow
  bucket empty on the way up with fresh splashes down your body; 24.3
  s: caption "The water flies", the 25 parcels with trails just free of
  the slow bucket at the upper left inside the gold arc, the fixed
  lines and the legend and tag in place of the title; 25.2 s: caption
  "free, and comes down", the parcels landed as splashes down your
  head and body, the empty bucket at the right; 29.85 s: caption
  "Thirty a minute.", the card "bucket over your head: / how slow
  before it spills? / 30 turns a minute, one every 2.0 s / limit 29.9
  rpm: 29 spills, 30 holds" lit under it, the slow water just leaving
  at the upper left, the fast bucket near the top ("push 0.60 g");
  39.98 s: the title back and the HUD gone, matches 0.02 s; the contact
  sheet shows the captions in narration order and the card from 30 s
  to 39 s
- question inside two seconds: the title carries the question from
  frame 0; the narration reaches "how slow before it spills" after four
  words, the word "how" sounds at 1.99 s (pause 1.64 to 1.99 s in video
  time; timing.log chunk boundary 1.81 s); the caption "head, how slow"
  shows 1.52 to 2.45 s and "before it spills?" 2.45 to 3.38 s
- captions: the 33 chunks read back from `media/bucket/captions.filter`
  match the 104 narration words exactly, in order; longest chunk 20
  characters; "Thirty a minute." (16) is one chunk 29.27 to 30.20 s
- payoff on screen when spoken: the card fades in 29.2 to 29.8 s and
  holds to the loop fade; "30 turns a minute" is fully lit at 29.8 s
  while "Thirty a minute." sounds 29.27 to 30.20 s (frame 29.85
  inspected); the card's "limit 29.9 rpm: 29 spills, 30 holds" matches
  the measured 29.91 rpm and the whole-rpm sweep
- clipping and bands: every one of the 2,400 footage frames scanned
  (numpy, more than 24 levels from the background): content columns 61
  to 1019 of 0 to 1079 and rows 166 to 1781; the caption exclusion band
  rows 1420 to 1530 never deviates more than 5 levels from the
  background (0 frames over 8 levels); the lowest geometry row is 1419
  (the slow floor line); the card starts at 1592
- loop: the raw last frame equals the first (0 px, max channel
  difference 0) and the live scene at 40 s equals 0 s (0 px); in the
  encoded final.mp4 frame 2399 against frame 0 differs in 20,985 px by
  more than 8 levels (max channel difference 67, mean 0.31 levels, 825
  px over 32 levels on the title and arm edges), the same order as the
  published merry-go-round final (18,572 px, max 80, mean 0.28), i.e.
  h264 quantisation on the second-generation encode, not content; the
  loop step from frame 2398 to 2399 is 32,667 px
- ffprobe final.mp4: h264 1080x1920 yuv420p 60/1 fps, 2,400 frames,
  40.000000 s, 5,312,607 bytes, aac 22050 Hz mono, moov before mdat;
  md5 1487b8c3a59ecfd7e1d089060897eeeb
- narrated numbers against measure.log: "one meter arm" is arm_m 1.0
  (overlay "arm 1 m"); "Thirty a minute" is the sweep's slowest whole
  rate that holds (30 rpm, +0.006 g at the top; 29 rpm spills; closed
  form 29.91 rpm); "36 turns a minute" and "21 turns a minute" on the
  labels are the manifest rates; "push at top 0.45 g" is 0.449 g;
  "lets go 60 deg before the top" is 60.46 degrees; "all of it comes
  down on you" is 25 of 25 parcels on the body or head, none on the
  floor
- no defect left

### Metadata

- `projects/bucket/metadata.json`: title "Bucket over your head: how
  slow before it spills? 30 turns a minute on a 1 m arm" (80
  characters); description (3,797 characters) with the setup (1 m arm
  from the shoulder pivot to the water surface, the bucket's open top
  toward the pivot, the water from 1.00 to 1.10 m, 36 and 21 turns a
  minute, side view with you at the pivot 1.5 m above the floor, 25
  parcels, N = m (omega^2 rho - g cos phi), leave when N would go
  negative, free flight without air, refill at the bottom, 24 fast and
  14 slow turns in 40 s, no seed), a Measured list (the sqrt(g / r)
  limit 29.9 rpm and 2.006 s with the 29 rpm / 30 rpm sweep, the 36
  rpm pushes 0.45, 1.45 and 2.45 g, the 21 rpm leave at 60.5 degrees
  and 2.20 m/s with the 0.68 m apex and the hit 0.67 s later 1.06 m
  above the floor, the 25 parcels' 60.5 to 57.2 degrees and 2.20 to
  2.43 m/s with 23 body and 2 head hits, the 2e-7 degree and 3e-13 m
  checks, the 15 to 30 rpm variants), a Why paragraph in plain words
  (the water stays in only while the bucket pushes; gravity supplies g
  of the omega^2 r push at the top and the floor the rest; below the
  limit gravity is already more than the circle needs before the top,
  the push runs out and the water keeps going while the bucket turns
  on; the limit scales with the square root of the arm), the rerun
  line and the AI-made line; 10 tags (bucket of water, swing a bucket
  over your head, centripetal force, circular motion, how slow before
  it spills, vertical circle, physics, physics visualization,
  simulation, shorts); category 27; private; containsSyntheticMedia
  true; selfDeclaredMadeForKids false; the same keys in the same order
  as projects/merrygoround/metadata.json; no "<" or ">"
- not uploaded; task left open for the orchestrator's review and upload

### Release
- orchestrator review (11:12 EEST): the task evidence, the 8x5 contact
  sheet and the full-resolution frames at 0.02, 25.2 and 29.85 s
  inspected: the question "Bucket over your head: / how slow before it
  spills?" over both panels from frame 0 with the fast bucket just past
  the top ("push 0.46 g") and the slow bucket empty on the right with
  "spills" and the last splashes fading down the person (the
  thumbnail); 25.2 s shows the 25 parcels landed as splashes down the
  head and body in the slow panel with the readouts "lets go 60 deg
  before the top / all of it comes down on you" and the fast panel's
  "push at top 0.45 g / holds, every turn"; 29.85 s shows the card
  "bucket over your head: / how slow before it spills? / 30 turns a
  minute, one every 2.0 s / limit 29.9 rpm: 29 spills, 30 holds" lit
  under the caption "Thirty a minute." with the slow water just leaving
  at the upper left inside the gold arc; the narrated numbers (a one
  meter arm, thirty a minute) match arm_m 1.0 and the whole-rpm sweep
  (30 holds at +0.006 g, 29 spills, closed form 29.91 rpm) in
  media/bucket/measure.log; the producer's change of the slow rate
  from the briefed 24 rpm to 21 rpm is recorded in the task and
  docs/niche.md and keeps the claim (below the limit, spills on the way
  up) while putting the water on the person instead of past them, and
  the task title now reads 21 rpm; the constant-rate arm and the
  refill at the bottom are stated on the legend and in the
  description; captions sit in the y 1440 to 1520 band, the caption
  exclusion band scanned clean on all 2,400 footage frames; final.mp4
  h264 1080x1920 60 fps, 2,400 frames, aac 22050 Hz mono, 40.000 s
  (scene_duration 40, so the gate accepts PT40S or PT41S), moov before
  mdat, md5 1487b8c3a59ecfd7e1d089060897eeeb; title 80 characters; the
  description carries no < or >; approved for release
- quota check: clock 2026-09-25T11:13:35+03:00; two upload attempts (spool, 11:10:07,
  published as 5xhaVWmicBI at 11:11:07; cueball, 11:11:51, published as
  pcnwZnIKhh0 at 11:12:52) recorded since the 2026-09-25 10:00 EEST
  boundary (log entries and media/*/upload.log both checked); this is
  insert attempt 3 of the hard cap of 5
- attempt 3 recorded at 2026-09-25T11:13:35+03:00, video name bucket, before running
  `scripts/yt-upload.py bucket`

### Published
- upload: `scripts/yt-upload.py bucket` (attempt 3) ran 11:13:35 to
  11:13:41 EEST, token verified to see only the Seed Zero channel, video
  id xPS0hhN56p4, private (`media/bucket/upload.log`)
- gate: `scripts/yt-qa.py bucket xPS0hhN56p4 --wait --publish` ran in
  the foreground from 11:13:48 EEST: processing succeeded and the 10 tags
  read back within the first poll, 15 of 15 pass (processed, succeeded,
  hd, 1080x1920, title, description, tags as a set, category 27, not for
  kids, PT41S for the 40.000 s file, private); containsSyntheticMedia
  reads absent as on every earlier upload (`media/bucket/publish.log`)
- publish: the same run set the video public at 2026-09-25T11:14:05+03:00;
  the re-read after 15 s shows privacyStatus public, madeForKids false,
  embeddable true; public at https://youtu.be/xPS0hhN56p4
- slot resolution: published for the 2026-09-25 quota day

### Quota
- attempt 3 of the hard cap of 5 for the quota day that began
  2026-09-25T10:00 EEST; cost 1 + 1,600 + 53 = 1,654 units (the
  channels.list verification inside yt-upload.py, the insert, the gate
  run's reads, update and re-read as printed by yt-qa.py); day total after
  three attempts 4,966 units plus 5 for the 10:18 stats refresh, target
  of three met

### Repository
- committed as 2f677a4 "Publish the day twenty-seven slate" (sims,
  projects, tasks, docs/niche.md, web/data; no media, previews or
  secrets) and pushed to origin/master at 2026-09-25 11:17 EEST
