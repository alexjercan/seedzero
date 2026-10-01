# Produce short: Rope round a post, one turn beside two turns with 2 kg against 20 kg

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day33

## Goal

Backlog idea (trend research 2026-09-30, task 20260930-100404, pillar 2
chaos and physics, everyday mechanics; read the full entry under "Added
by trend research 2026-09-30" in docs/niche.md): "Rope round a post: a
20 kg load on a rope wrapped one turn beside two turns round a post with
mu 0.3, a hand holding 20 N (2 kg); measure whether the load holds;
expect one turn to hold at most 6.59 times the pull (131.7 N, e^(mu
theta)), so the 20 kg slips and falls 1 m in 0.79 s at 3.22 m/s^2, and
two turns to hold 43.4 times (867 N, 88 kg); 1.21 turns is the limit for
20 kg, three turns hold 286 times; the factor depends on mu (0.2: 12.3,
0.4: 152 at two turns), so state the rope; closed form; repeat;
deterministic, no seed."

Orchestrator notes (2026-10-01, before this brief). Replace the hand by a
hanging 2 kg weight, so the whole scene is two weights on one rope over
a post and nothing needs a hand model: a massless, unstretchable rope
wrapped theta = 2 pi (one full turn, top band) or 4 pi (two full turns,
bottom band) round a fixed round post of radius 6 cm (the radius does not
enter the capstan factor, say so); friction between rope and post mu =
0.3, the same at rest and sliding (a chosen number for a rope on a wooden
post, say so); on one side hangs M = 20 kg, on the other m = 2 kg; g =
9.80665. Capstan (Euler-Eytelwein): the rope holds while the big tension
is at most e^(mu theta) times the small one. e^(0.3 x 2 pi) = 6.5862 for
one turn, e^(0.3 x 4 pi) = 43.376 for two, 285.68 for three. The 2 kg
side pulls with m g = 19.613 N, so one turn holds at most 129.18 N =
13.17 kg: the 20 kg (196.13 N) is too much and the rope slips. Two turns
hold up to 850.8 N = 86.75 kg: the 20 kg holds with 4.34 times to spare.
The turns needed for exactly 20 kg: ln(M / m) / (2 pi mu) = ln(10) /
1.885 = 1.2216 turns (439.8 degrees). Sliding with one turn: both weights
move with the rope, T_big = e^(mu theta) T_small, the small side m (g +
a) = T_small, the big side M g - T_big = M a, so a = g (M - m e^(mu
theta)) / (M + m e^(mu theta)) = 9.80665 x (20 - 13.172) / (20 + 13.172)
= 2.0185 m/s^2: the 20 kg falls 1 m (and the 2 kg rises 1 m) in sqrt(2 /
a) = 0.9954 s, arriving at 2.009 m/s; the rope slides round the post at
that speed. Checks, not facts (orchestrator closed forms, /tmp/day33):
factors 6.5862 / 43.376 / 285.68; holds up to 13.17 kg with one turn,
86.75 kg with two, 571.3 kg with three; the limit for 20 kg 1.2216
turns; one turn slips at a = 2.0185 m/s^2, 1 m in 0.9954 s at 2.009 m/s
(integrate by RK4 at 10,000 steps a second and check against the closed
form within 1e-6 s and a half-step rerun); two turns: static, net
capacity 850.8 - 196.1 = 654.7 N to spare, nothing moves; mu 0.2 gives
3.51 (one turn) and 12.35 (two), mu 0.4 gives 12.35 and 152.4; with a 20
N hand instead of the 2 kg weight one turn would fall at 3.22 m/s^2 (for
the description only). Also print a load scan for two turns: 86 kg
holds, 87 kg slips. State every derived number above as a check the sim
must print, not as a fact.

Drawing: side view of a horizontal round post drawn as a cylinder (a
rounded bar, say 120 px across, centred in the band's upper part), the
rope wrapped round it as one or two countable bands (a helix seen from
the side: draw the front half of each turn over the post and hide the
back half; two turns side by side with a small pitch so they read as
two), the rope then hanging straight down on the left to a 20 kg block
and on the right to a 2 kg block (blocks labelled "20 kg" and "2 kg",
drawn to a plausible size, the big one bigger); a floor 1 m below the
big block's start (at 350 px per metre, or whatever fits the 550 px band
with the post and the blocks inside it: measure and assert); dash marks
along the hanging rope that move with the rope when it slips, so the
sliding is visible even in slow motion; a gold readout of the capacity
"holds up to 13.2 kg" (top) and "holds up to 86.8 kg" (bottom) in the
left column, the live "20 kg: falling, N.NN m/s" or "20 kg: holding" in
the right column; a gold event row "slips: 20 kg on the floor at 1.00 s"
(top, lit at the landing) and "holds" (bottom, lit two seconds after the
release). A support under the big block holds it until the release (a
short held phase), then slides away. Shown at 1/4 speed (0.995 s becomes
3.98 s); cycle 8 s with the release 0.6 s in, the block on the floor at
4.58 s, then a hold and a reset crossfade, 5 cycles in 40 s, the last
frame equal to the first. The two-turn band never moves: that is the
result; keep its readouts alive so it does not look frozen. Nothing
drawn under the captions.

Day thirty-three, second slot. Chosen because "can a small weight hold a
big one" is a tactile everyday question (tying up a boat, a belay), the
answer is a famous exponential most people have never seen as a number,
the panels end visibly differently (one load drops, one hangs), and the
payoff is a closed form. Question in the first two seconds: "Can two
kilos hold twenty, round a post?" or "Can two kilos hold twenty kilos?"
(the producer's wording with the question by word nine; keep the question
identical in the title, the hook and the payoff). Setup number: two
kilos against twenty, one turn beside two turns. Payoff number: one turn
slips, two turns hold, and two turns would hold eighty six kilos. The
factors 6.6 and 43, the 1.22 turns, the three-turn figure and the other
grips go to the card and the description. Whisper risks: "kilos" and
"kilograms" (pre-test both), "post", "turn" was dropped once on
2026-09-27 (pre-test "one turn", "two turns"), "round the post" versus
"around the post" (pre-test), "rope", "slips"; avoid "pull" as a noun
(say "the two kilo weight pulls"); avoid "do you"; "eighty six" as words.
Pre-test hooks with scripts/voiceover.sh and keep the one whose question
lands earliest under two seconds. Measure every fixed text line with PIL
before rendering and keep every line under 950 px, and the title under
100 characters with no < or >. Music seed 102. Templates: sims/belt (two
bands, reset fade, layout asserts), sims/springdrop or sims/tablecloth
(slow motion with a release inside the cycle, a block on a floor),
sims/spool (a drawn rope or string). Sim name capstan:
sims/capstan/capstan.py, projects/capstan/, media/capstan/.

## Claim (expected; the sim's numbers replace these)

A 2 kg weight on a rope round a post with grip 0.3 holds a 20 kg weight
on the other end with two turns of rope (capacity 850.8 N = 86.75 kg,
e^(mu theta) = 43.38) and not with one turn (capacity 129.2 N = 13.17 kg,
factor 6.586): with one turn the 20 kg falls 1 m in 0.9954 s at 2.0185
m/s^2 while the 2 kg rises. Exactly 20 kg needs 1.22 turns; each turn
multiplies the holding power by 6.59. Narrated: two kilos against twenty,
one turn beside two (setup); one turn slips, two turns hold, and two
turns would hold eighty six kilos (payoff). Card: the question; one turn
holds 13 kg, two turns 87 kg; each turn times 6.6, e^(0.3 x angle); 20
kg needs 1.22 turns; three turns 571 kg; grip 0.2: times 12 for two
turns, grip 0.4: times 152. Description: the sliding acceleration and
fall time, the RK4 check, the model statement.

## Claim

A 2 kg weight on a rope round a post with grip 0.3 holds a 20 kg weight
on the other end with two turns of rope (e^(0.3 x 4 pi) = 43.3762,
capacity 850.75 N = 86.752 kg, 654.62 N spare) and not with one turn
(e^(0.3 x 2 pi) = 6.5861, capacity 129.17 N = 13.172 kg, 66.96 N
short): with one turn the 20 kg falls 1 m in 0.99540 s at 2.0185 m/s^2,
arriving at 2.0092 m/s, while the 2 kg rises 1 m. Exactly 20 kg needs
1.2216 turns; each turn multiplies the holding power by 6.5861. Load
scan with two turns: 86 kg holds, 87 kg slips. Narrated: two kilos
against twenty, one turn beside two (setup); not with one turn, with
two turns yes, two turns would hold eighty six kilos (payoff). Card: the
question; one turn 13.2 kg, two turns 86.8 kg; each turn times 6.6;
20 kg needs 1.22 turns; three turns 571 kg; grip 0.4 times 152.

## Evidence

### Measurements

Command: `nix develop -c python3 sims/capstan/capstan.py --measure-only`
with date lines, written to media/capstan/measure.log (copied whole):

```
Thu Oct  1 10:31:16 AM EEST 2026
warning: Git tree '/home/alex/personal/seedzero' is dirty
setup: a massless, unstretchable rope round a fixed horizontal round post of radius 6 cm (drawn at 40 px = 14.3 cm, larger than scale: the radius does not enter the capstan factor e^(mu theta), the same factors hold with any radius), 1 full turn in the top panel (theta = 2 pi) and 2 full turns in the bottom panel (theta = 4 pi); friction coefficient mu = 0.3 between rope and post, the same at rest and sliding (a chosen number for a rope on a wooden post); on the left hangs M = 20 kg (196.13 N), on the right m = 2 kg (19.613 N), g = 9.80665 m/s^2; the rope holds while T_big <= e^(mu theta) T_small; the floor is 1 m under the big weight; a latch carries the big weight until the release, then slides away; the fall integrated by RK4 at 10000 steps per second (dt = 1e-04 s) and checked against the closed forms and a half-step rerun; shown at 1/4 speed on a 8 s cycle (480 frames) with the release 0.6 s into the cycle, 5 cycles in 40 s; drawn at 280 px per metre; deterministic, no seed
one turn: e^(0.3 x 2 pi) = 6.5861, so the 2 kg side (19.613 N) holds at most 129.17 N = 13.172 kg; the 20 kg (196.13 N) is 1.518 times that (66.96 N short): the rope slips
two turns: e^(0.3 x 4 pi) = 43.3762, so the 2 kg side holds at most 850.75 N = 86.752 kg; the 20 kg is 0.2305 of that (4.338 times to spare, 654.62 N spare): the rope holds, nothing moves; the other way round the 2 kg side would need 19.613 N > 43.3762 x 196.13 N to pull the 20 kg up, so it holds that way as well
one turn, sliding: both weights move with the rope; T_small = m (g + a) = 23.650 N, T_big = 6.5861 T_small = 155.76 N, M g - T_big = 40.370 N = M a; a = g (M - m K) / (M + m K) = 2.0185 m/s^2 (0.2058 g); RK4 at 10000 steps/s: the 20 kg reaches the floor 1 m down after 0.99540 s (closed form sqrt(2 L / a) = 0.99540 s, diff -9.6e-11 s) at 2.0092 m/s (closed form a t = 2.0092 m/s, diff -1.9e-10 m/s), 9955 steps; half-step rerun (dt = 5e-05 s): 0.9954019 s (+4.9e-11 s), 2.0092386 m/s (+9.8e-11 m/s); the rope slides round the post at the same speed and the 2 kg rises 1 m in the same 0.995 s; the run ends at the landing
the limit: exactly 20 kg needs ln(M / m) / (2 pi mu) = 1.2216 turns (439.8 degrees); each full turn multiplies the holding power by e^(2 pi mu) = 6.5861; three turns: factor 285.68, holds up to 5603.1 N = 571.4 kg
load scan with the 2 kg side: one turn: 12 kg holds, 13 kg holds, 14 kg slips (a = 0.2988 m/s^2), 15 kg slips (a = 0.6363 m/s^2) (limit 13.17 kg); two turns: 84 kg holds, 85 kg holds, 86 kg holds, 87 kg slips (a = 0.0140 m/s^2), 88 kg slips (a = 0.0700 m/s^2), 89 kg slips (a = 0.1254 m/s^2) (limit 86.75 kg)
for the description: the factor depends on the grip: grip 0.2: 3.514 with one turn, 12.345 with two turns; grip 0.4: 12.345 with one turn, 152.406 with two turns; a hand holding a steady 20 N instead of the 2 kg weight: one turn holds up to 131.7 N = 13.43 kg, the 20 kg falls at (M g - K x 20 N) / M = 3.2206 m/s^2, 1 m in 0.7880 s
schedule (video time, 1/4 speed): cycles of 8 s start at -2.80, 5.20, 13.20, 21.20, 29.20, 37.20 s; the release 0.6 s into each cycle at 5.80, 13.80, 21.80, 29.80, 37.80 s (the latch slides away over the next 0.3 s); with one turn the 20 kg reaches the floor 3.98 s of video after the release at 1.78, 9.78, 17.78, 25.78, 33.78 s and the top event text lights there; with two turns nothing moves and the bottom event text lights 2 s of video (0.50 s real) after the release at 7.80, 15.80, 23.80, 31.80, 39.80 s; each cycle crossfades to the latched setup over its last 0.4 s (from 4.80, 12.80, 20.80, 28.80, 36.80 s); on the first frame the cycle is 2.80 s in (0.550 s real after the release): the top 20 kg is falling at 30.5 cm down, the bottom 20 kg is holding; title until 3 s; payoff card from 28.8 s; the title fades back in over the last 0.5 s and the last frame repeats the first (the scene is periodic: 40 s holds exactly 5 cycles)
text widths: overlay@34 849 px, title line 1@56 422 px, title line 2@56 576 px, legend@40 747 px, clock@28 370 px, clock held@28 268 px, label one@40 193 px, capacity one@28 305 px, factor one@28 225 px, state held@40 98 px, state falling@40 143 px, state down@40 122 px, state holding@40 169 px, event one@40 473 px, label two@40 217 px, capacity two@28 305 px, factor two@28 244 px, event two@40 486 px, speed@28 239 px, fallen@28 207 px, holding for@28 279 px, big label@24 75 px, small label@20 48 px, dimension@24 50 px, payoff line 1@40 721 px, payoff line 2@40 845 px, payoff line 3@40 653 px, payoff line 4@40 800 px, payoff line 5@40 697 px, payoff line 6@40 880 px
row check: the left column ends at x 345 px and the right column starts at x 761 px, the post spans x 430 to 650 px and y 70 to 150 px under the band top; the event text (widest 486 px, centred) spans x 297 to 783 px between the label (ends at 257) and the state (starts at 871); the rows end 136 px under the band top; the 20 kg block hangs at x 432 to 528 from y 172 to 244 and lands with its bottom on the floor at 524 (1 m = 280 px); the 2 kg block hangs at x 571 to 629 from y 452 to 498 (26 px above the floor) and rises to 172, 22 px under the post; the latch tip retracts from x 520 to 416 (16 px clear of the block); the floor hatch ends 541 px under the band top; each band is 550 px tall (y 330 to 880 and 880 to 1430); the caption band starts at y 1440; the title rows end at y 280 and the overlay band ends at y 130
Thu Oct  1 10:31:16 AM EEST 2026
```

Brief checks against the log (orchestrator closed forms in the brief):

- factors 6.5862 / 43.376 / 285.68: 6.5861 / 43.3762 / 285.68 (the
  brief's 6.5862 is e^(0.3 x 2 pi) rounded up; the log's 6.5861 is the
  4-decimal truncation of 6.58614). Holds.
- one turn holds up to 13.17 kg with 2 kg: 129.17 N = 13.172 kg. Holds.
- two turns 86.75 kg: 850.75 N = 86.752 kg. Holds.
- three turns 571.3 kg: 5603.1 N = 571.4 kg (571.36). Holds.
- limit for 20 kg 1.2216 turns: 1.2216 turns (439.8 degrees). Holds.
- one turn slips at a = 2.0185 m/s^2: 2.0185 m/s^2 (0.2058 g); tensions
  T_small 23.650 N, T_big 155.76 N, M g - T_big = 40.370 N = M a. Holds.
- 1 m in 0.9954 s at 2.009 m/s: RK4 at 10,000 steps/s 0.99540 s and
  2.0092 m/s, within -9.6e-11 s and -1.9e-10 m/s of the closed forms
  (the brief asks for 1e-6 s); half-step rerun +4.9e-11 s, +9.8e-11
  m/s. Holds.
- two turns static, 850.8 - 196.1 = 654.7 N spare: holds, 654.62 N
  spare (4.338 times to spare), nothing moves; also holds the other way
  round. Holds.
- mu 0.2 gives 3.51 and 12.35; mu 0.4 gives 12.35 and 152.4: 3.514 /
  12.345 and 12.345 / 152.406. Holds.
- 20 N hand instead of the 2 kg: one turn falls at 3.22 m/s^2: 3.2206
  m/s^2, 1 m in 0.7880 s (holds up to 131.7 N = 13.43 kg). Holds.
- load scan for two turns, 86 kg holds, 87 kg slips: 84, 85, 86 kg
  hold, 87 kg slips (a = 0.0140 m/s^2), 88 and 89 slip. Holds. One turn:
  13 kg holds, 14 kg slips.
- the post radius does not enter the factor: stated in the setup line
  (6 cm, drawn at 40 px = 14.3 cm).
- backlog numbers (131.7 N, 0.79 s, 3.22 m/s^2, 867 N, 88 kg, 1.21
  turns) belong to the 20 N hand variant; the brief replaced the hand by
  a hanging 2 kg (19.613 N), which gives 129.17 N, 850.75 N, 86.75 kg
  and 1.2216 turns. The hand variant is printed for the description.

No discrepancy.

### Production

- Sim: sims/capstan/capstan.py. Capstan factors and capacities in closed
  form, the one-turn slide with both weights moving (a = g (M - m K) /
  (M + m K)), the 1 m fall by RK4 at 10,000 steps/s with the landing
  located inside the step, closed-form and half-step checks, load scans,
  other grips and the hand variant, layout asserts (every text line
  under 950 px, columns clear of the post, the centred event text clear
  of both side texts, the 20 kg lands on the floor inside the band, the
  2 kg rises to 22 px under the post, the latch retracts clear of the
  block, block labels fit), loop and periodicity checks. Deterministic,
  no seed.
- Manifest: projects/capstan/manifest.json. M 20 kg, m 2 kg, mu 0.3,
  post radius 6 cm (drawn 40 px), turns 1 and 2, fall 1 m, g 9.80665,
  10,000 steps/s, 1/4 speed, cycle 8 s with the release 0.6 s in, first
  cycle at -2.8 s, reset fade 0.4 s, latch slide 0.3 s, the bottom event
  2 s after the release, 5 cycles in 40 s, 280 px/m, title until 3 s,
  payoff card from 28.8 s (hold 0.6 s), loop fade 0.5 s, music seed 102,
  gain 0.18, voice offset 0.6 s, caption_y 0.75, overlay "2 kg vs 20 kg
  | grip 0.3 | 1/4 speed | no seed".
- Layout: two bands y 330-880 (one turn, coral) and 880-1430 (two
  turns, teal); in each band the label row 40 px under the band top
  holds the label (left), the gold event text (centred, "on the floor at
  1.00 s" / "holds, nothing moves") and the live state (right: held,
  falling, down, holding); rows 84 and 120 hold "holds up to 13.2 kg" /
  "2 kg times 6.6" (left) and the speed and the fall or the holding time
  (right); the post (horizontal rounded bar, radius 40 px) centred 110
  px under the band top, one or two front half-turns drawn over it as
  countable crossings (the back halves hidden), the strands hanging from
  its bottom edge at x 480 (20 kg, 96x72 block) and 600 (2 kg, 58x46
  block), dash marks every 28 px of rope that move with the rope (down
  the 20 kg strand, over the post, up the 2 kg strand), a latch from a
  wall at x 300 under the 20 kg block that retracts over 0.3 s, the
  floor 524 px under the band top (1 m = 280 px) with a "1 m" dimension
  line; legend "same rope, same post, 1/4 speed" at y 236 and the clock
  at y 290 in real seconds after the release; six-line card from y 1572.
- Hook pre-tests (media/capstan/hooks/pretest.log, 6 probes): hook1 "Can
  two kilos hold twenty kilos? A rope goes round a post." ok 3.77 s, the
  question spoken 0.60-2.58 s of video (pause at 1.98 s of voice),
  chosen; hook2 "Can two kilograms hold twenty kilograms? A rope goes
  around a post." ok 4.10 s (both "kilograms" and "around" pass); hook3
  "Can two kilos hold twenty, round a post?" fails ("round a post" comes
  back "round to post"); hook4 "Can two kilos hold twenty kilos on a
  rope round a post?" ok 3.37 s; hook5 "... A rope goes around a post."
  ok 3.96 s; words.txt (round the post, slides round the post, rubs,
  one turn, two turns, Not with one turn, eighty six kilos, ride up,
  let the big one go) ok 23.37 s.
- Narration: projects/capstan/narration.txt, 108 words, the question
  first (word one) and repeated word for word before the payoff;
  American spelling; numbers as words; setup number two kilos against
  twenty (one turn beside two), payoff number eighty six kilos.
- Voice: scripts/voiceover.sh, Piper 10303, whisper.cpp 10301. Pass 1
  (10:27:57) ok 34.16 s on the first-order text (107 words). Pass 2
  (10:30:13) ok 34.40 s after reordering for the schedule (the fall in
  one sentence after "let the big one go", the marks on the rope moved
  to the two-turn sentence). No mishearing in either pass. Voice ends at
  35.00 s of video.
- Timing (media/capstan/timing.log, pass 2; fine pauses at d=0.12 in
  media/capstan/pauses-fine.log, video time): question 0.60-2.85; "A
  rope goes round a post. Twenty kilos hang on one side, two kilos on the
  other." 2.85-7.80; "The top rope goes round the post once." 7.80-10.14;
  "The bottom rope goes round twice." 10.14-12.27; "Now let the big one
  go." 12.27-13.84; "With one turn," 14.10-14.86; "the rope slides round
  the post," 15.09-16.54; "the twenty kilos fall," 16.82-18.00; "and the
  two kilos ride up." 18.40-19.67; "With two turns, nothing moves, not
  even the marks on the rope." 19.84-23.06; "Every turn multiplies the
  grip, because the post rubs on more rope." 23.20-26.76; "So, can two
  kilos hold twenty kilos?" 26.90-29.17; "Not with one turn." 29.38-
  30.53; "With two turns, yes." 30.82-31.75; "Two turns would hold
  eighty six kilos." 31.95-34.79.
- Schedule and sync: first_cycle_at -2.8 s puts the releases at 5.80,
  13.80, 21.80, 29.80 and 37.80 s and the landings at 1.78, 9.78, 17.78,
  25.78 and 33.78 s: the latch retracts as "go" ends (13.84), the fall
  runs under "the rope slides round the post, the twenty kilos fall"
  (15.09-18.00) and the 2 kg is at the top for "ride up"; the release at
  29.80 falls inside "Not with one turn." (29.38-30.53) and the landing
  at 33.78 inside "hold eighty six kilos" (32.55-34.79); the bottom
  "holds, nothing moves" is lit from 2 s after each release (23.80 under
  the two-turn sentence, 31.80 under "With two turns, yes"); the card
  rises at 28.8 s (lit by 29.4) as "Not with one turn." starts. Frame 0
  is 0.55 s real after a release (the 20 kg 30.5 cm down, falling).
- Smoke frames (media/capstan/smoke-*.png, from the first schedule with
  first_cycle_at 0, the geometry unchanged): 0.0 (title, both latched),
  1.5, 2.0 (latch retracted, dashes moving), 3.4 (HUD, "holds, nothing
  moves" lit), 4.7 ("on the floor at 1.00 s", the 2 kg under the post),
  7.7, 7.9 (reset crossfade), 8.1, 26.0 (six-line card), 39.6, 39.98;
  viewed 0.0, 2.0, 3.4, 4.7, 7.9, 26.0 with the Read tool before the
  full render.
- Render: `nix develop -c python3 sims/capstan/capstan.py` ->
  media/capstan/render.log (10:31:16-10:31:42): loop check 0 px (max
  channel difference 0), periodicity check 0 px, loop step 4,177 px,
  footage 40.00 s at 60 fps (2,400 frames).
- Compose: scripts/compose.sh capstan -> media/capstan/compose.log
  (10:31:42-10:31:54): music seed 102 40.00 s; "captions: 19 pauses
  detected, 19 matched, max chunk start shift 1.096 s against word-count
  timing"; contact sheet 8x5 at 1 fps; final.mp4 40.000000 s. 32
  caption chunks, 108 words, word-for-word match with the narration,
  longest chunk 20 chars.
- Text widths (measure.log, PIL at the drawn size): overlay 849 px,
  title rows 422 and 576 px, legend 747, clock 370, labels 193 and 217,
  capacity 305, factor 225 and 244, states 98 to 169, events 473 and
  486, speed 239, fallen 207, holding for 279, block labels 75 (24 px)
  and 48 (20 px), dimension 50, card lines 721 / 845 / 653 / 800 / 697
  / 880 px; all under 950 px, asserted.

### Local QA

- Footage signalstats: overlay band (rows 96-130) YMAX 28 in all 2,400
  footage frames; caption band (rows 1440-1530) YMAX 28 in all 2,400
  frames; both bands hold only the background.
- Final loop noise (codec only): frame 2399 vs 0: 23,919 px over 8
  levels, 420 over 32, max 75, mean 0.46; 2398 vs 2399: 21,248 / 4,019 /
  max 236; 0 vs 1: 4,190 / 2,487 / max 233. The seam is quieter than an
  ordinary frame step.
- Frames extracted from media/capstan/final.mp4 (never edited) and read:
  0.00 (overlay, two-row title, top 20 kg falling at 1.11 m/s and 0.31 m
  with the latch retracted and the 2 kg part way up, bottom holding
  with "holds, nothing moves" lit, no caption, no card), 1.00 (caption
  "Can two kilos hold", top falling 1.61 m/s, 0.65 m), 2.10 (caption
  "twenty kilos?", top "on the floor at 1.00 s" and "down", the 2 kg
  under the post), 15.50 (legend and clock "0.42 s after the release",
  caption "rope slides round", top falling 0.86 m/s and 0.18 m, dashes
  on both strands, bottom "holding for 0.42 s"), 29.20 (caption "hold
  twenty kilos?", both latched, "held on the latch", card fading in),
  30.60 (caption "Not with one turn.", top just released, 0.40 m/s and
  0.04 m, card lit), 33.90 (caption "eighty six kilos.", top on the
  floor, "on the floor at 1.00 s", card lit), 39.98 (title back, equals
  frame 0). Nothing clipped, nothing in the caption band, the events
  lit under their words.
- Contact sheet media/capstan/sheet.png: 40 thumbnails, clean; the card
  from 29 s, the title at 0-2 s and 39 s.
- Question timing: on screen from frame 0 (title) and spoken 0.60-2.85 s
  (hook1 pre-test 0.60-2.58 s). Payoff number "eighty six kilos" spoken
  33.83-35.00 s with the card (86.8 kg) lit since 29.4 s and the top
  block landing at 33.78 s.
- Captions: 32 chunks, 108 words, word-for-word match with
  narration.txt (checked by script from captions.filter).
- ffprobe: h264 1080x1920 yuv420p 60/1, 2,400 frames; aac 22050 Hz mono;
  duration 40.000000 s; 3,161,267 bytes; moov at byte 36, mdat at
  44,784 (faststart).
- md5sum media/capstan/final.mp4: 1be13adf57167a7e4867e9977eb08883.
- Narrated numbers against measure.log: "two kilos" and "twenty kilos"
  (m = 2 kg, M = 20 kg in the setup line), "once" / "twice" (1 full turn
  and 2 full turns), "eighty six kilos" (load scan: 86 kg holds, 87 kg
  slips; capacity 86.752 kg). Every narrated number is on a printed line.
- Description check: 122 numbers in the description, every one
  present in measure.log (commas stripped, by script).
- Title 82 chars, no < or >, ASCII. Every fixed text line measured
  with PIL under 950 px (widest: card line 6 at 880 px).

### Metadata

projects/capstan/metadata.json:

- title: "Can two kilos hold twenty kilos? One turn round a post slips; two turns hold 86 kg" (82 chars).
- description: 3659 chars ASCII. The model and every constant (20 kg
  = 196.13 N, 2 kg = 19.613 N, g 9.80665, mu 0.3, post radius 6 cm,
  angles 2 pi and 4 pi, floor 1 m, RK4 at 10000 steps/s, 1/4 speed, 8 s
  cycle, 5 cycles in 40 s), a "Measured:" list (factors 6.5861 and
  43.3762, capacities 129.17 N = 13.172 kg and 850.75 N = 86.752 kg,
  1.518 times and 66.96 N short, 0.2305 and 4.338 times to spare with
  654.62 N spare, tensions 23.650 / 155.76 / 40.370 N, a 2.0185 m/s^2,
  0.99540 s, 2.0092 m/s, 1.2216 turns, 439.8 degrees, 285.68, 5603.1 N
  = 571.4 kg, the load scans, grips 0.2 and 0.4, the 20 N hand, the
  check diffs), a "Why:" paragraph, the rerun line, the AI-made line.
- tags (11): can two kilos hold twenty kilos, rope round a post, capstan
  equation, rope friction, belay friction, exponential grip,
  Euler-Eytelwein, physics, physics visualization, simulation, shorts.
- categoryId 27, privacyStatus private, containsSyntheticMedia true,
  selfDeclaredMadeForKids false.

### Deviations from the brief

- Scene schedule: first_cycle_at -2.8 s (releases at 13.8 and 29.8 s)
  so the release plays under "let the big one go" and "Not with one
  turn." and the fourth landing under "eighty six kilos". Frame 0 is
  therefore mid-fall (0.55 s real after a release), not the latched
  setup; the last frame equals it.
- Narration reordered after voice pass 1 (which also passed): the fall
  in one sentence right after "let the big one go", "not even the marks
  on the rope" in the two-turn sentence, so the 4 s fall sits under its
  words. Second sentence "A rope goes round a post." (hook1); hook3's
  "round a post" inside the question failed the pre-test.
- Event texts "on the floor at 1.00 s" and "holds, nothing moves"
  (brief: "slips: 20 kg on the floor at 1.00 s" and "holds"): the event
  row is centred on the label row between the panel label and the live
  state, since the post and the 1 m fall fill the band; the right-hand
  state reads held / falling / down / holding without the "20 kg:"
  prefix (the block is labelled).
- Scale 280 px/m (brief: 350 or whatever fits): the 1 m fall, the post,
  the 20 kg block and the 2 kg block hanging 1 m below the post all fit
  the 550 px band. The post is drawn at 40 px radius (14.3 cm at scale,
  the real 6 cm would be 17 px); the log and the description say the
  radius does not enter the factor.
- The 2 kg block rises exactly 1 m and stops 22 px under the post at the
  landing; the run ends at the landing (what the 2 kg does afterwards is
  not modelled, stated in the log and description).
- Card line 6 carries only grip 0.4 (152 times); grip 0.2 (12.345) is in
  the description. Title says "two turns hold 86 kg" from the integer
  load scan (86 holds, 87 slips); the card says 86.8 kg.
- The latch is a bar from a wall at the left retracting over 0.3 s
  (brief: a support that slides away).
- The hook pre-test "kilos" against "kilograms": both passed; "kilos"
  kept (the question lands by word six either way).
- Voice ends at 35.00 s; the last 5 s carry the card, the fifth cycle
  and the loop fade with music only.

## Niche note

[produced 2026-10-01 as "Can two kilos hold twenty kilos? One turn round a post slips; two turns hold 86 kg"; measured with a hanging 2 kg instead of
the hand: e^(0.3 x 2 pi) = 6.5861, so one turn holds at most 129.17 N =
13.172 kg and the 20 kg slips at 2.0185 m/s^2, 1 m in 0.99540 s at
2.0092 m/s; e^(0.3 x 4 pi) = 43.3762, so two turns hold up to 850.75 N
= 86.752 kg (654.62 N spare) and nothing moves; load scan 86 kg holds,
87 kg slips; exactly 20 kg needs 1.2216 turns; three turns 571.4 kg;
grip 0.2 gives 12.345 and grip 0.4 gives 152.406 with two turns; a
steady 20 N hand would let the 20 kg fall at 3.2206 m/s^2, 1 m in
0.7880 s; RK4 at 10,000 steps a second within 1e-10 s of the closed
form, half step within 5e-11 s; task 20261001-101158]

## Upload

- orchestrator review (2026-10-01T10:48:52+03:00): task evidence, sheet.png and full frames at
  0.00, 15.50, 30.60 and 39.98 s inspected; ffprobe h264 1080x1920 60 fps
  2400 frames 40.000 s; md5 1be13adf57167a7e4867e9977eb08883; title 82
  chars, no angle brackets; description 3659 chars, no angle brackets, 11
  tags; captions match narration word for word (32 chunks); measure.log
  matches the closed forms (e^(0.3 x 2 pi) = 6.5861, e^(0.3 x 4 pi) =
  43.376, one turn holds 13.17 kg, two turns 86.75 kg, exactly 20 kg needs
  1.2216 turns, the 20 kg falls 1 m in 0.9954 s at a = 2.0185 m/s^2);
  frame 0 is mid-fall by design (cycle starts 0.55 s before frame 0);
  approved for upload, waits for attempt 1 (deskchain) to resolve
- upload attempt 2 of 5 for the quota day that began 2026-10-01T10:00
  EEST, recorded at 2026-10-01T10:55:23+03:00 before starting scripts/yt-upload.py; one
  attempt (deskchain 12ESwWxQ9Ws, published) was on record since the
  boundary
- uploaded private as aByGt6B3gh0 at 2026-10-01T10:55:29+03:00
  (https://youtu.be/aByGt6B3gh0); channels.list 1 unit + videos.insert
  1,600 units; media/capstan/upload.log
- scripts/yt-qa.py capstan aByGt6B3gh0 --wait --publish in the foreground
  (started 2026-10-01T10:55:37+03:00): gate 14 of 15, tags read back as []
  on the first processed read (the known read lag of about six minutes
  after an insert; not re-sent); publish refused; 3 units; rerun after
  the lag
- scripts/yt-qa.py capstan aByGt6B3gh0 --wait --publish rerun in the
  foreground (started 2026-10-01T11:01:46+03:00): gate 15 of 15 (processed,
  succeeded, hd, 1080x1920, title, description and tags match, category
  27, not made for kids, PT41S for the 40.000 s file, private before
  publish); published at 2026-10-01T11:01:48+03:00; re-read
  privacyStatus=public selfDeclaredMadeForKids=False embeddable=True;
  yt-qa quota 52 units; media/capstan/publish.log
- attempt 2 of 5 complete: 1,656 units; slot 2 of 3 resolved as
  published (recorded 2026-10-01T11:02:15+03:00)

### Quota
- attempt 2 of the hard cap of 5 for the quota day that began
  2026-10-01T10:00 EEST; cost 1,656 units (the channels.list verification
  inside yt-upload.py, the 1,600-unit insert, the first gate run's 3
  reads, and the rerun's reads, update and re-read as printed by
  yt-qa.py, 52); day total after two attempts 1,656 + 1,656 = 3,312 of
  10,000 used, 6,688 remaining
