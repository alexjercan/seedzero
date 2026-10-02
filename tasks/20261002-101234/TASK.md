# Produce short: Balance a broom, a 1.2 m broom beside a 15 cm pencil let go 1 degree off vertical

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day34

## Goal

Backlog idea (trend research 2026-09-25, task 20260925-101408, pillar 2
chaos and physics, inverted pendulum; read the full entry under "Added
by trend research 2026-09-25" in docs/niche.md): "Balance a broom: a 1.2
m stick beside a 15 cm pencil balanced on a fingertip, both let go 1
degree off vertical; measure the time to fall flat; expect 1.50 s
against 0.53 s (45 degrees at 1.29 against 0.46 s), exactly sqrt(8) =
2.83 times longer for the broom because the fall time scales with
sqrt(L) (theta'' = 3 g sin theta / 2L); RK4; the answer is half known,
so rank it mid; repeat the release; deterministic, no seed."

Orchestrator notes (2026-10-02, before this brief). The model: a uniform
thin stick of length L stands on a fingertip with its foot held in place
(a hinge: the foot neither slips nor lifts; say "the foot stays on the
finger"), let go from rest theta0 = 1 degree off vertical, theta
measured from vertical; about the foot I = m L^2 / 3 and the torque is
m g (L / 2) sin theta, so theta'' = (3 g / (2 L)) sin theta; the mass
cancels. Energy: theta'^2 = (3 g / L)(cos theta0 - cos theta). In the
scaled time tau = t sqrt(3 g / (2 L)) the equation is theta'' = sin
theta for every length, so every time in the fall scales exactly with
sqrt(L): the pencil's fall is the broom's fall played sqrt(8) = 2.8284
times faster, and the ratio is the same at every angle. Top panel: the
broom, L = 1.2 m. Bottom panel: the pencil, L = 0.15 m, eight times
shorter. g = 9.80665.

Checks, not facts (orchestrator RK4 at 10 us, /tmp/day34/closed.log):
broom 45 degrees at 1.2889 s, flat (90 degrees, the floor) at 1.4985 s,
angular speed at the floor 4.951 rad/s (energy form sqrt(3 g cos theta0
/ L) = 4.951), tip speed 5.94 m/s; pencil 45 degrees at 0.4557 s, flat
at 0.5298 s, 14.004 rad/s, tip 2.10 m/s; ratio of the flat times 2.8284
= sqrt(8) (and of the 45-degree times); small-angle growth rate sqrt(3 g
/ (2 L)) = 3.501 per second for the broom (e-fold 0.286 s, the lean
doubles every 0.198 s) against 9.903 per second for the pencil (e-fold
0.101 s). For the description: the broom from 0.5 degrees flat at
1.6964 s, from 2 degrees 1.3005 s, from 5 degrees 1.0390 s; a 30 cm
ruler 0.7492 s (exactly half the broom), a 1 m stick 1.3679 s, a 10 cm
stub 0.4326 s, a 4.8 m pole 2.9969 s (exactly twice the broom). Integrate
by RK4 at 10,000 steps per second with the floor (theta = 90 degrees)
and the 45-degree crossing located by bisection inside the step; check
against the energy form at every printed angle and the time ratio
against sqrt(8) to 1e-5; half-step rerun; print the foot's push on the
stick (vertical and horizontal, in weights) through the fall as
sims/icerod does for its hinge, so the description can say the foot is
held (the sideways push grows late in the fall). State every number
above as a check the sim must print, not as a fact.

Drawing: side view, two bands (y 330-880 and 880-1430). Each band at its
own scale so both sticks are about 400 px long on screen (broom 333 px
per metre, pencil 2667 px per metre): label the pencil band "15 cm
pencil, drawn 8x" and say "each stick drawn to fit" in the legend and
the overlay, so the frame shows the same fall at two speeds, which is
the physics (the same equation in scaled time). A fingertip (a simple
rounded finger) under the foot near the band's left third; the stick
falls to the right; a faint ghost of the vertical start; keep both as
plain uniform sticks (the model is uniform) and name them in the labels.
Per band: label "1.2 m broom" / "15 cm pencil, drawn 8x" (40 px), "1 degree
off vertical" (28 px), a live angle "N.N degrees" and a clock that
freezes gold when the stick hits the floor; a gold event row "flat at
1.498 s" / "flat at 0.530 s". A muted 45-degree tick and its time are
optional (the description has them). Shown at 1/3 speed: the pencil is
flat 1.59 s after the release, the broom 4.50 s after; cycle 8 s with
the release 0.4 s in, the fallen sticks held until the reset crossfade
at the end, 5 cycles in 40 s, the last frame equal to the first.
Nothing in the overlay rows 96-130 or under the captions from y 1440.

Day thirty-four, second slot. Chosen because "which is easier to
balance" is a question anyone has tried with a finger, the answer
surprises half the viewers (the broom), both panels show the same
motion at visibly different speeds, and the payoff is an exact ratio
with a closed form. Question in the first two seconds: "Which is easier
to balance, a pencil or a broom?" (keep the question identical in the
title, the hook and the payoff). Setup number: the broom is eight times
as long (one degree off vertical is the shared condition). Payoff: the
broom takes one and a half seconds to fall, the pencil half a second;
two point eight times longer, exactly the square root of eight. The
45-degree times, the other lengths and leans and the foot's push go to
the card and the description. Whisper risks: "broom" and "pencil"
(pre-test), "fingertip" and "balance" (pre-test), "tips over" / "topples"
(pre-test; "falls" is safe), "flat" (passed 2026-09-28), "the square root
of eight" and "root eight" (pre-test both; keep the one that passes),
"one degree" (pre-test), "let go" (safe); avoid "do you"; "Which is
easier" as the opening (pre-test the onset). Pre-test hooks with
scripts/voiceover.sh and keep the one whose question lands earliest
under two seconds. Measure every fixed text line with PIL before
rendering and keep every line under 950 px, and the title under 100
characters with no < or >. Music seed 105. Templates: sims/icerod (a
hinged stick falling: RK4 with bisection at the floor, the energy and
quadrature checks, the hinge force), sims/hingedstick, sims/deskchain
(bands, cycle, reset fade, layout asserts). Sim name broom:
sims/broom/broom.py, projects/broom/, media/broom/.

## Claim (expected; the sim's numbers replace these)

A 1.2 m broom and a 15 cm pencil, each let go from rest 1 degree off
vertical with the foot held: the broom is flat at 1.4985 s, the pencil
at 0.5298 s, exactly sqrt(8) = 2.828 times longer because the fall time
scales with sqrt(L). Narrated: a broom and a pencil, the broom eight
times as long, both one degree off vertical (setup); the broom takes one
and a half seconds to fall, the pencil half a second, two point eight
times longer, exactly the square root of eight (payoff). Card: the
question; broom flat at 1.498 s, pencil at 0.530 s; ratio 2.828 =
sqrt(8), the time grows with the square root of the length; 45 degrees
at 1.289 / 0.456 s; a 30 cm ruler 0.749 s, half the broom; a 4.8 m pole
3.00 s. Description: the model statement, the equation and the scaled
time, the energy check, the other leans and lengths, the foot's push,
the RK4 checks.

## Claim

A 1.2 m broom and a 15 cm pencil, each let go from rest 1 degree off
vertical with the foot held on the finger: the broom lies flat at 1.4985
s (45 degrees at 1.2889 s), the pencil at 0.5298 s (45 degrees at 0.4557
s); the ratio of the flat times is 2.82843 = sqrt(8) within 2.1e-14
(the same at 45 degrees) because every time in the fall scales with
sqrt(L): theta'' = (3 g / (2 L)) sin theta is theta'' = sin theta in the
scaled time tau = t sqrt(3 g / (2 L)). RK4 at 10,000 steps/s agrees with
the quadrature of the energy form within 9.2e-14 s and the half-step
rerun moves the flat times by under 3.4e-15 s. At the floor the broom
turns at 4.9510 rad/s (tip 5.94 m/s), the pencil at 14.0037 rad/s (tip
2.10 m/s). Narrated: a pencil and a broom on a fingertip, one degree off
vertical, the broom eight times as long (setup); the broom takes one and
a half seconds to fall, the pencil half a second; eight times the
length, root eight times the time: two point eight times longer,
exactly the square root of eight (payoff). Card: the question; broom
flat at 1.498 s, pencil at 0.530 s; 2.828 times longer, exactly root 8;
8x the length, root 8 = 2.83x the time; 45 degrees at 1.289 and 0.456
s; 30 cm ruler 0.749 s, 4.8 m pole 3.00 s. Description: the model
statement, the equation and the scaled time, the energy and quadrature
checks, the growth rates, the foot's push, the other leans and lengths,
the RK4 checks.

## Evidence

### Measurements

media/broom/measure.log (`nix develop -c python3 sims/broom/broom.py
--measure-only`, 2026-10-02 10:29:04 EEST, final manifest):

```
Fri Oct  2 10:29:04 AM EEST 2026
setup: a uniform thin stick stands on a fingertip with its foot held in place (a hinge: the foot neither slips nor lifts), let go from rest 1 degree off vertical (theta from vertical); about the foot I = m L^2 / 3 and the torque is m g (L / 2) sin theta, so theta'' = (3 g / (2 L)) sin theta and the mass cancels; top panel the broom, L = 1.2 m (120 cm); bottom panel the pencil, L = 0.15 m (15 cm), 8 times shorter (the broom is 8 times as long); g = 9.80665 m/s^2; the stick lies flat at theta = 90 degrees (the floor); both integrated by RK4 at 10000 steps per second (dt = 1e-04 s) with the floor and the 45-degree crossing located by bisection inside the step; shown at 1/3 speed on a 8 s cycle (480 frames) with the release 0.8 s into the cycle, 5 cycles in 40 s; each stick drawn to fit, 350 px long on screen (broom 292 px per metre, pencil 2333 px per metre, drawn 8x); deterministic, no seed
broom (1.2 m): RK4: the stick lies flat at 1.4985 s (quadrature of the energy form 1.4985 s, diff -9.2e-14 s) and passes 45 degrees at 1.2889 s (quadrature 1.2889 s, diff -1.3e-13 s); theta'^2 stays within 2.6e-13 rad^2/s^2 of the energy form (3 g / L)(cos theta0 - cos theta) and the energy drifts by 1.1e-14 of the energy released over 14985 steps; at the floor theta' = 4.9510 rad/s (energy form sqrt(3 g cos theta0 / L) = 4.9510) and the tip comes down at L theta' = 5.941 m/s = 5.94 m/s; at 45 degrees theta' = 2.6790 rad/s (energy form 2.6790); small-angle growth rate sqrt(3 g / (2 L)) = 3.5012 per second (e-fold 0.2856 s; the growing mode doubles every ln 2 / rate = 0.1980 s; from rest the lean follows cosh, first doubling at acosh(2) / rate = 0.3761 s): RK4 lean at 2 degrees at 0.3762 s, 4 degrees at 0.5894 s (0.2132 s later), 10 degrees at 0.8551 s
  broom: the foot's push on the stick (weights): vertical 0.9998 and horizontal +0.0131 (forward, toward the fall) at the release; the forward push peaks at +0.229 at 26.7 degrees and reverses at 48.2 degrees (closed form cos theta = 2/3: 48.2 degrees); the vertical push falls to 0.0001 at 70.5 degrees (closed form (3 cos theta - 1)^2 / 4, zero at cos theta = 1/3: 70.5 degrees) and is 0.2500 at the floor; the sideways pull back toward the foot grows late in the fall to 1.4998 weights at the floor (closed form (3/2) cos theta0 = 1.4998); the sideways push exceeds the vertical push from 54.1 degrees on, so a foot on a plain floor would slip: it must be held
pencil (0.15 m): RK4: the stick lies flat at 0.5298 s (quadrature of the energy form 0.5298 s, diff -2.9e-14 s) and passes 45 degrees at 0.4557 s (quadrature 0.4557 s, diff -4.2e-14 s); theta'^2 stays within 2.2e-12 rad^2/s^2 of the energy form (3 g / L)(cos theta0 - cos theta) and the energy drifts by 1.1e-14 of the energy released over 5298 steps; at the floor theta' = 14.0037 rad/s (energy form sqrt(3 g cos theta0 / L) = 14.0037) and the tip comes down at L theta' = 2.101 m/s = 2.10 m/s; at 45 degrees theta' = 7.5773 rad/s (energy form 7.5773); small-angle growth rate sqrt(3 g / (2 L)) = 9.9029 per second (e-fold 0.1010 s; the growing mode doubles every ln 2 / rate = 0.0700 s; from rest the lean follows cosh, first doubling at acosh(2) / rate = 0.1330 s): RK4 lean at 2 degrees at 0.1330 s, 4 degrees at 0.2084 s (0.0754 s later), 10 degrees at 0.3023 s
  pencil: the foot's push on the stick (weights): vertical 0.9998 and horizontal +0.0131 (forward, toward the fall) at the release; the forward push peaks at +0.229 at 26.7 degrees and reverses at 48.2 degrees (closed form cos theta = 2/3: 48.2 degrees); the vertical push falls to 0.0001 at 70.5 degrees (closed form (3 cos theta - 1)^2 / 4, zero at cos theta = 1/3: 70.5 degrees) and is 0.2500 at the floor; the sideways pull back toward the foot grows late in the fall to 1.4998 weights at the floor (closed form (3/2) cos theta0 = 1.4998); the sideways push exceeds the vertical push from 54.1 degrees on, so a foot on a plain floor would slip: it must be held
the two panels: the broom is flat at 1.4985 s = 1.50 s (one and a half seconds) against 0.5298 s = 0.53 s (half a second) for the pencil, 0.9687 s apart; the ratio of the flat times is 2.82843 = 2.8 times longer (two point eight times; 2.83x) = exactly sqrt(8) = 2.82843 (diff -2.1e-14); the ratio of the 45-degree times is 2.82843 (diff -2.2e-14); the ratio of the lean doublings is the same: in the scaled time tau = t sqrt(3 g / (2 L)) the equation is theta'' = sin theta for every length, so every time in the fall scales with sqrt(L): the pencil's fall is the broom's fall played 2.8284 times faster; the broom is 8 times as long, so its fall takes sqrt(8) = 2.828 times longer at every angle
for the description (same model): the broom from 0.5 degrees: 45 degrees at 1.4869 s, flat at 1.6964 s (quadrature 1.6964 s); the broom from 2 degrees: 45 degrees at 1.0909 s, flat at 1.3005 s (quadrature 1.3005 s); the broom from 5 degrees: 45 degrees at 0.8287 s, flat at 1.0390 s (quadrature 1.0390 s); a 0.3 m stick (30 cm) from 1 degree: 45 degrees at 0.6445 s, flat at 0.7492 s (sqrt(0.3 / 1.2) = 0.5000 times the broom's 1.4985 s = 0.7492 s), 9.902 rad/s and tip 2.97 m/s at the floor; a 1 m stick (100 cm) from 1 degree: 45 degrees at 1.1766 s, flat at 1.3679 s (sqrt(1 / 1.2) = 0.9129 times the broom's 1.4985 s = 1.3679 s), 5.424 rad/s and tip 5.42 m/s at the floor; a 0.1 m stick (10 cm) from 1 degree: 45 degrees at 0.3721 s, flat at 0.4326 s (sqrt(0.1 / 1.2) = 0.2887 times the broom's 1.4985 s = 0.4326 s), 17.151 rad/s and tip 1.72 m/s at the floor; a 4.8 m stick (480 cm) from 1 degree: 45 degrees at 2.5778 s, flat at 2.9969 s (sqrt(4.8 / 1.2) = 2.0000 times the broom's 1.4985 s = 2.9969 s), 2.476 rad/s and tip 11.88 m/s at the floor
check at half the time step (20000 steps per second): broom flat at 1.4984521 s (-8.9e-16), 45 degrees at 1.2889162 s (+6.7e-16), 4.951049 rad/s at the floor (-4.7e-14); pencil flat at 0.5297828 s (-3.4e-15), 45 degrees at 0.4557007 s (-3.0e-15), 14.003683 rad/s at the floor (+4.3e-14); ratio 2.828427
schedule (video time, 1/3 speed): cycles of 8 s start at 0.00, 8.00, 16.00, 24.00, 32.00 s (the first on the first frame); the release 0.8 s into each cycle at 0.80, 8.80, 16.80, 24.80, 32.80 s; the pencil passes 45 degrees 1.37 s after the release at 2.17, 10.17, 18.17, 26.17, 34.17 s and lies flat 1.59 s after the release at 2.39, 10.39, 18.39, 26.39, 34.39 s; the broom passes 10 degrees 2.57 s after the release at 3.37, 11.37, 19.37, 27.37, 35.37 s, 45 degrees 3.87 s after at 4.67, 12.67, 20.67, 28.67, 36.67 s and lies flat 4.50 s after the release at 5.30, 13.30, 21.30, 29.30, 37.30 s; both lie flat with their readouts until the reset fade, which crossfades back to the standing stick over 0.6 s ending 0.2 s before the cycle's end (out over 7.20 to 7.50 s, in over 7.50 to 7.80 s after the cycle start, at 7.20, 15.20, 23.20, 31.20, 39.20 s), then both stand held from 7.80 s to the next release at 8.80 s; on the first frame the cycle is 0.00 s in (0.267 s real before the release): the broom at 1.0 degrees, the pencil at 1.0 degrees, held at rest; title until 3 s; payoff card from 22.9 s; the title fades back in over the last 0.5 s and the last frame repeats the first (the scene is periodic: 40 s holds exactly 5 cycles)
text widths: overlay@34 838 px, title line 1@56 851 px, title line 2@56 645 px, legend@40 754 px, clock@28 390 px, clock rest@28 194 px, label broom@40 285 px, sublabel broom@28 321 px, fixed broom@28 433 px, event broom@40 314 px, tick broom@24 294 px, tip broom@28 188 px, label pencil@40 522 px, sublabel pencil@28 321 px, fixed pencil@28 433 px, event pencil@40 314 px, tick pencil@24 294 px, tip pencil@28 188 px, angle@40 295 px, band clock@28 115 px, payoff line 1@40 856 px, payoff line 2@40 876 px, payoff line 3@40 767 px, payoff line 4@40 857 px, payoff line 5@40 766 px, payoff line 6@40 853 px
row check: the left column ends at x 562 px and the right column starts at x 745 px; both end 136 px under the band top and the standing stick (at x 360 px) tops out at 154 px under the band top with its cap, 18 px under the rows; the hinge is at (360, 512) and the tip's arc has radius 350 px (plus the 8 px cap), so the flat stick reaches x 718 px; the right column's corner is 538 px from the hinge, the event row's corner 416 px and the 45-degree label's corner 370 px (its text to x 923 px); the fingertip spans x 336 to 384 px from 520 px under the band top to the band bottom; each band is 550 px tall (y 330 to 880 and 880 to 1430); the caption band starts at y 1440; the title rows end at y 280 and the overlay band ends at y 130
Fri Oct  2 10:29:05 AM EEST 2026
```

Brief checks (every number is a line the sim printed):

- Broom 45 degrees at 1.2889 s, flat at 1.4985 s: passed (RK4 1.2889 /
  1.4985 s; quadrature of the energy form within 1.3e-13 / 9.2e-14 s).
- Broom angular speed at the floor 4.951 rad/s, energy form sqrt(3 g
  cos theta0 / L) = 4.951, tip 5.94 m/s: passed (4.9510 rad/s both
  ways, tip 5.941 m/s = 5.94 m/s).
- Pencil 45 degrees at 0.4557 s, flat at 0.5298 s, 14.004 rad/s, tip
  2.10 m/s: passed (0.4557 / 0.5298 s, 14.0037 rad/s both ways, tip
  2.101 m/s = 2.10 m/s).
- Ratio of the flat times 2.8284 = sqrt(8), and of the 45-degree times:
  passed (2.82843 both, diff -2.1e-14 and -2.2e-14 against sqrt(8);
  the brief asked for 1e-5).
- Growth rate sqrt(3 g / (2 L)) = 3.501 per second for the broom, e-fold
  0.286 s, "the lean doubles every 0.198 s", 9.903 per second for the
  pencil, e-fold 0.101 s: passed (3.5012 / 0.2856 / 0.1980 s; 9.9029 /
  0.1010 s). 0.198 s is the doubling of the growing mode (ln 2 / rate);
  from rest the lean follows cosh and first doubles at acosh(2) / rate
  = 0.3761 s (RK4 2 degrees at 0.3762 s, 4 degrees at 0.5894 s). Both
  printed; the description says both.
- Broom from 0.5 degrees flat at 1.6964 s, from 2 degrees 1.3005 s, from
  5 degrees 1.0390 s: passed (each with its quadrature equal).
- 30 cm ruler 0.7492 s (exactly half the broom): passed (0.7492 s,
  sqrt(0.3 / 1.2) = 0.5000 times 1.4985 s). 1 m stick 1.3679 s: passed.
  10 cm stub 0.4326 s: passed. 4.8 m pole 2.9969 s (exactly twice):
  passed (2.0000 times 1.4985 s).
- RK4 at 10,000 steps per second with the floor and the 45-degree
  crossing by bisection inside the step: done (14,985 and 5,298 steps).
- Energy form checked at every printed angle: passed (theta'^2 within
  2.6e-13 and 2.2e-12 rad^2/s^2 over the whole run; 45-degree speeds
  2.6790 and 7.5773 rad/s equal to the energy form; energy drift 1.1e-14
  of the energy released).
- Half-step rerun: passed (20,000 steps/s moves the flat times by
  -8.9e-16 and -3.4e-15 s, the 45-degree times by under 7e-16 s, the
  floor speeds by under 5e-14 rad/s; the ratio stays 2.828427).
- The foot's push through the fall as sims/icerod prints it: passed
  (vertical 0.9998, horizontal +0.0131 at the release; forward peak
  +0.229 at 26.7 degrees; reversal at 48.2 degrees = closed form cos
  theta = 2/3; vertical zero at 70.5 degrees = closed form cos theta =
  1/3, 0.2500 at the floor; pull back 1.4998 weights at the floor =
  (3/2) cos theta0; sideways exceeds vertical from 54.1 degrees: the
  foot must be held). The same curve for both sticks, as the scaled
  equation says.
- Shown at 1/3 speed: pencil flat 1.59 s after the release, broom 4.50 s
  after: passed (schedule line).

### Production

- Sim: sims/broom/broom.py, modelled on sims/icerod/icerod.py (RK4 with
  bisection at the floor, the energy and quadrature checks, the hinge
  force) and sims/deskchain/deskchain.py (bands, cycle, reset fade,
  layout asserts): RK4 at 10,000 steps/s with bisection on the crossing
  step at 45 and 90 degrees, quadrature of the energy form with the
  substitution theta = theta0 + s^2 (400,000 panels), energy check at
  every step, half-step rerun, closed forms for the foot's push; the
  drawing reads the same RK4 table (np.interp); 2x supersampled bands;
  loop, periodicity and loop-step checks; ffmpeg rawvideo pipe with a
  ProcessPoolExecutor (12 workers); --measure-only and --frames.
- Manifest projects/broom/manifest.json: seed 0, fps 60, g 9.80665, lean
  1.0 degree, broom 1.2 m / pencil 0.15 m with their labels,
  description-only leans 0.5 / 2 / 5 degrees and lengths 0.3 / 1.0 / 0.1
  / 4.8 m, 10,000 steps/s, sim_end 4 s, slow 3.0, cycle 8 s,
  first_cycle_at 0.0, release_at 0.8 s, reset_fade 0.6 s, reset_hold 0.2
  s, land_flash 0.35 s, scene 40 s, stick 350 px, foot at x 360 and 520
  px under the band top, title "Which is easier to balance,|a pencil or
  a broom?" until 3 s, payoff_t 22.9 s, payoff_hold 0.6 s, six payoff
  lines formatted from the measured values, loop_fade 0.5, music seed
  105, gain 0.18, voice offset 0.6, caption_y 0.75, overlay "each stick
  drawn to fit | 1/3 speed | no seed".
- Layout: overlay y 96-130 (compose); title two rows at y 190 / 252
  until 3 s; legend "each stick drawn to fit, 1/3 speed" at y 236 and
  the clock ("held, at rest" / "N.NNN s after the release") at y 290
  after the title; bands y 330-880 (broom, teal) and 880-1430 (pencil,
  coral); per band: label "1.2 m broom" / "15 cm pencil, drawn 8x" (40
  px), "1 degree off vertical" (28 px) and "the foot stays on the
  finger" (28 px) in the left column; the right column (from x 745)
  "N.N degrees" (40 px, gold when flat), the band clock "N.NNN s" (28
  px, frozen gold at the floor) and "tip N.NN m/s" (28 px); the gold
  event row "flat at 1.498 s" / "flat at 0.530 s" at x 880 and 330 px
  under the band top when the stick lands; a muted 45-degree tick on the
  arc with "45 degrees at 1.289 s" / "45 degrees at 0.456 s" (24 px); a
  side view with the hinge at (360, 512 under the band top), a rounded
  finger with a nail under the foot, the stick falling to the right along
  a faint arc of radius 350 px to a dashed floor guide at x 718, a
  dashed ghost of the vertical start with a ring at its tip, a landing
  flash of 0.35 s; the six-line gold card from y 1572 at a 48 px pitch;
  nothing in rows 96-130 or 1440-1530 (asserted in the row check and
  measured on the footage). Every stick 350 px long on screen (broom
  292 px/m, pencil 2333 px/m, drawn 8x).
- Hook pre-tests (media/broom/hooks/pretest.log, 10:22-10:24): hook1
  ("Which is easier to balance, a pencil or a broom? Both stand on a
  fingertip, one degree off vertical, and the broom is eight times as
  long.") ok 7.77 s, speech from 0.075 s of voice = 0.675 s of video,
  the question done at 2.78 s of voice: chosen; hook2 failed ("on a
  fingertip" heard as "and a fingertip"); hook3 ("... One degree off
  vertical. Let go. The broom is eight times as long.") ok 6.84 s.
  words.txt: "The broom." at a sentence start heard as "brune"; "The
  pencil", "A fingertip", "Balance", "It tips over", "It topples", "It
  falls flat", "The square root of eight", "Root eight", "One degree",
  "One and a half seconds", "Half a second", "Two point eight times
  longer", "Eight times as long", "Let go", "The foot stays on the
  finger", "Played slower", "The same fall, only slower" all passed.
  words2 (the whole payoff block as narrated, "So, which is easier to
  balance ... The broom, by far. ... exactly the square root of eight.")
  ok 14.88 s. words3 ("By far, the broom. The broom wins, by far. It is
  the broom." and the setup sentences) ok 17.47 s.
- Narration: projects/broom/narration.txt, 104 words; the question is
  the first sentence (10 words, on screen in the title from frame 0,
  spoken 0.675-3.36 s) and is repeated word for word ("So, which is
  easier to balance, a pencil or a broom?") before the payoff; one setup
  number (one degree off vertical; the broom eight times as long) and
  one payoff number (one and a half seconds against half a second; two
  point eight times longer, exactly the square root of eight); the
  mechanism sentences name only what the frame shows (the pencil falls
  at once, the broom leans slowly then falls, the same fall only played
  slower); American spelling; no digits; no "do you".
- Voice (media/broom/voice.log): pass 1 (104 words, 10:25:08) failed,
  whisper dropped the "a" of "one and a half"; pass 2 (10:26:11, the
  same text) ok 33.506 s. voice.wav ends at 34.11 s of video; 21 pauses
  matched by captions.py.
- timing.log (voice offset 0.6 s; whisper's own spelling):

```
  0.60 -   3.36  which is easier to balance, a pencil or a broom.
  3.36 -   5.06  both stand on a fingertip,
  5.06 -   6.64  1 degree off vertical
  6.64 -   8.34  The broom eight times as long.
  8.34 -   9.18  Let's go!
  9.18 -  10.96  The pencil falls at once.
 10.96 -  13.48  The broom leans slowly then falls.
 13.48 -  14.79  It is the same fall.
 14.79 -  16.02  only played slower
 16.02 -  21.69  The longer the stick, the slower it falls.
 So, which is easier to balance: a pencil or a broom?
 21.69 -  23.13  The broom by far.
 23.13 -  25.58  It takes one and a half seconds to fall.
 25.58 -  27.41  The pencil in half a second.
 27.41 -  28.72  8 times the length,
 28.72 -  30.50  root eight times the time,
 30.50 -  34.11  2.8 times longer, exactly the square root of 8.
voice 33.51 s, ends at 34.11 s of video
```

- Schedule and sync (caption chunk times from captions.filter): releases
  at 0.80, 8.80, 16.80, 24.80, 32.80 s. "Which is easier to balance, a
  pencil or a broom?" 0.60-3.50 while the cycle-1 pencil falls (flat at
  2.39 with "flat at 0.530 s" lit); "Both stand on a fingertip, one
  degree off vertical, the broom eight times as long." 3.50-8.49 while
  the broom falls (flat at 5.30), both lie flat and the crossfade
  (7.20-7.80) brings the standing sticks back; "Let go." 8.49-9.30 over
  the second release at 8.80; "The pencil falls at once." 9.30-11.09
  with the pencil flat at 10.39; "The broom leans, slowly, then falls."
  11.09-13.59 with the broom at 10 degrees at 11.37, 45 degrees at 12.67
  and flat at 13.30; "It is the same fall, only played slower. The
  longer the stick, the slower it falls." 13.59-18.40 with both flat
  and their gold rows lit, the crossfade at 15.20 and the third release
  at 16.80; "So, which is easier to balance, a pencil or a broom?"
  18.40-21.82 as the cycle-3 pencil lies flat (18.39) and the broom
  falls (flat at 21.30); "The broom, by far." 21.82-23.35 with both gold
  "flat at" rows lit; the card rises from 22.9 s and is full at 23.5 s
  as "It takes one and a half seconds to fall." 23.35-25.71 is spoken
  (the crossfade at 23.20-23.80 under it, the fourth release at 24.80);
  "The pencil, in half a second." 25.71-27.53 as the cycle-4 pencil
  falls (flat at 26.39); "Eight times the length, root eight times the
  time: two point eight times longer, exactly the square root of eight."
  27.53-34.11 with the card up while the broom falls (flat at 29.30) and
  the fifth cycle starts (release 32.80, pencil flat 34.39); the title
  fades back in over 39.5-40.0 s.
- Smoke frames viewed before the render (--frames, footage only):
  smoke-{0.0, 1.0, 2.5, 9.3, 10.2, 12.8, 13.5, 24.2, 39.7}.png: title
  and both sticks standing on their fingertips at 1.0 degrees with the
  ghost, the arc and the 45-degree ticks; the pencil leaning with its
  live angle, clock and tip speed; the pencil flat with the landing
  flash and "flat at 0.530 s"; the legend and clock after the title; the
  broom past 45 degrees; the broom flat with both gold rows; the dip
  crossfade back to the standing sticks; the six-line card inside the
  frame; the loop fade. All text inside the frame; the stick tops 18 px
  under the text rows (stick_px 350 and foot_dy 520 after the first
  layout assert failed at 360 / 510).
- Render (media/broom/render.log, 10:29:05-10:29:31): loop check 0 px,
  periodicity check 0 px, loop step 0 px (the last frames sit in the
  held phase after the reset_hold), footage 40.00 s at 60 fps, 2400
  frames. A first render with the fade ending on the cycle boundary gave
  a loop step of 6104 px; reset_hold 0.2 s fixed it.
- Compose (media/broom/compose.log, 10:29:40-10:30:12): music seed 105,
  40.00 s; captions 21 pauses detected, 21 matched (max chunk start
  shift 0.749 s against word-count timing); contact sheet 8x5 at 1 fps;
  final.mp4 40.000000 s; preview.mp4 40.066667 s.
- Text widths (PIL ImageFont.getlength, DejaVuSans-Bold, asserted < 950
  px): overlay@34 838, title@56 851 / 645, legend@40 754, clock@28 390
  (rest 194), labels@40 285 / 522, sublabels@28 321, fixed@28 433,
  events@40 314, ticks@24 294, tips@28 188, angle@40 295, band clock@28
  115, payoff lines@40 856 / 876 / 767 / 857 / 766 / 853 px.

### Local QA

- Frames extracted from media/broom/final.mp4 (never edited) with
  ffmpeg -ss T and viewed at full resolution:
  - 0.00: overlay "each stick drawn to fit | 1/3 speed | no seed", the
    title "Which is easier to balance, / a pencil or a broom?", both
    sticks standing on their fingertips at "1.0 degrees", "0.000 s",
    "tip 0.00 m/s", the ghost rings, the arcs with "45 degrees at 1.289
    s" / "45 degrees at 0.456 s", "1 degree off vertical" and "the foot
    stays on the finger" in both bands; no caption, no card.
  - 1.00: the pencil at 1.2 degrees and 0.067 s after the release, the
    broom still at 1.0 degrees; caption "Which is easier to".
  - 2.40: the pencil flat at "90.0 degrees" / "0.530 s" in gold with the
    landing flash and "flat at 0.530 s"; the broom at 3.3 degrees, 0.533
    s; caption "balance, a pencil or".
  - 11.00 (mid-run, cycle 2): legend and clock "0.733 s after the
    release", the broom at 6.6 degrees with "tip 0.47 m/s", the pencil
    flat with its gold row; caption "once.".
  - 23.60 (payoff + 0.7): the cycle-3 crossfade with the clock "held, at
    rest", the readouts and the flat sticks dimmed, the card full in
    gold; caption "It takes one and a".
  - 25.60: cycle 4 at 0.267 s after the release, the broom at 1.5
    degrees, the pencil at 7.0 degrees, the card full; caption "fall.".
  - 33.00: cycle 5 at 0.067 s, the card full; caption "square root of".
  - 39.983 (frame 2399): the title back, both sticks standing, the same
    picture as 0.00; no caption, no card.
  Nothing clipped at the frame edges, no text in the caption band, the
  six card lines sit between y 1572 and about 1850.
- sheet.png (8x5 at 1 fps): five identical cycles: the standing sticks,
  the pencil flat within two tiles with its gold row, the broom leaning
  and flat with both rows lit, the crossfade back; captions under; the
  card from the tile at 23 s.
- Question timing: on screen from frame 0 in the title; spoken from
  0.675 s of video (speech onset 0.075 s in voice.wav plus the 0.6 s
  offset) to 3.36 s (10 words); repeated at 18.40-21.82 s; answered "The
  broom, by far." at 21.82-23.35 s.
- Captions: 34 chunks of at most 20 characters, 0.600-34.106 s; the
  concatenated caption text equals narration.txt word for word (104
  words, compared by script).
- Payoff number on screen when spoken: "broom flat at 1.498 s, pencil
  at 0.530 s" is full on the card from 23.5 s while "It takes one and a
  half seconds to fall. The pencil, in half a second." is spoken
  23.35-27.53 s (the gold "flat at 1.498 s" and "flat at 0.530 s" rows
  are lit in the bands from 21.30 until the crossfade at 23.20); "2.828
  times longer: exactly root 8" and "8x the length, root 8 = 2.83x the
  time" on the card while "Eight times the length, root eight times the
  time: two point eight times longer, exactly the square root of eight."
  is spoken 27.53-34.11 s.
- Footage signalstats: overlay band (rows 96-130) and caption band (rows
  1440-1530) YMAX 28 in all 2400 footage frames; both bands hold only
  the background.
- Loop: render.log loop check 0 px, periodicity check 0 px and loop step
  0 px on the footage. Final loop noise (codec only): frame 2399 vs 0:
  25,178 px over 8 levels, 553 over 32, max 75, mean 0.51; 2398 vs 2399:
  23,435 / 2 / max 37 / mean 0.18; 0 vs 1: 706 / 109 / max 61 / mean
  0.03; the caption band of frames 0 and 2399 within 2 levels of the
  background.
- ffprobe final.mp4: h264 1080x1920 yuv420p 60/1, 2400 frames, duration
  40.000000 s, aac 22050 Hz mono, moov before mdat (faststart),
  4,073,176 bytes.
- md5sum media/broom/final.mp4: a738b903ee7bb4068a34a9fa62241b53.
- Narrated numbers against measure.log: "one degree off vertical" (let
  go from rest 1 degree off vertical), "the broom eight times as long"
  (the broom is 8 times as long), "one and a half seconds" (flat at
  1.4985 s = 1.50 s (one and a half seconds)), "half a second" (0.5298 s
  = 0.53 s (half a second)), "eight times the length, root eight times
  the time" (8 times as long, so its fall takes sqrt(8) = 2.828 times
  longer), "two point eight times longer" (2.8 times longer (two point
  eight times)), "exactly the square root of eight" (= exactly sqrt(8) =
  2.82843, diff -2.1e-14). All on printed lines.
- Metadata number check by script (commas stripped): 141 numbers in the
  description (73 distinct), none missing from measure.log; the title's
  1.50, 0.53, 2.83 and 8 all present.

### Metadata

- Title (99 characters, ASCII, no < or >): Which is easier to balance, a pencil or a broom? Broom flat at 1.50 s, pencil 0.53 s, 2.83x: root 8
- Description: 4,388 characters, ASCII, no arrows; one setup paragraph
  (the model, every constant, RK4 and its checks, 1/3 speed, 5 drops in
  40 s, no seed), "Measured:" bullets (both panels with the quadrature
  and energy forms, the ratio and the scaled time, the growth rates and
  doublings, the foot's push, the other leans, the other lengths, the
  RK4 checks), a "Why:" paragraph, the rerun line, the AI line.
- Tags (11): which is easier to balance, balance a broom, balancing a pencil, inverted pendulum, falling stick, hinged rod, square root of length, physics, physics visualization, simulation, shorts.
- categoryId "27", privacyStatus "private", containsSyntheticMedia true,
  selfDeclaredMadeForKids false.

### Deviations from the brief

- Sticks 350 px long on screen (brief: about 400 px; broom 292 px/m and
  pencil 2333 px/m, still drawn 8x): the label, sublabel and fixed rows
  need the top 136 px of each 550 px band, and a 400 px stick standing
  at 1 degree would reach into them; at 350 px the standing tip is 18 px
  under the rows and the flat stick reaches x 718, clear of the right
  column at x 745.
- The release is 0.8 s into the cycle with first_cycle_at 0.0 (brief:
  0.4 s in): frame 0 shows both sticks held at rest 0.267 s real before
  the first release, and the releases at 0.80, 8.80, 16.80, 24.80, 32.80
  s put "Let go." (8.49-9.30) on the second release.
- reset_hold 0.2 s added after the 0.6 s reset fade (fade 7.20-7.80 into
  each cycle, then both stand held to the next release): the first
  render with the fade ending on the cycle boundary gave a loop step of
  6104 px; with the hold the loop step is 0 px.
- The reset is a dip-to-background crossfade (the sims/icerod pattern:
  the fallen picture fades out over the first half, the standing picture
  fades in over the second).
- The overlay reads "each stick drawn to fit | 1/3 speed | no seed"
  without "1 degree" (too wide at 34 px); "1 degree off vertical" is the
  sublabel in both bands.
- The question has 10 words and takes 2.7 s to speak: it starts at 0.675
  s and ends at 3.36 s of video; it is on screen in the title from frame
  0 and the first spoken word lands inside the first second.
- The brief's "the lean doubles every 0.198 s" is the growing mode's
  doubling (ln 2 / rate); from rest the first doubling is at acosh(2) /
  rate = 0.3761 s (RK4: 2 degrees at 0.3762 s). Both printed; the
  description states both.
- The card says "root 8" ("2.828 times longer: exactly root 8", "8x the
  length, root 8 = 2.83x the time") and shows the 4.8 m pole as 3.00 s
  (2.9969 s); the description has the full values.
- No clamp or holder is drawn for the held phase: the fingertip holds
  the foot and the clock says "held, at rest" before each release.
- Hook1 (question first, as in the brief) chosen over hook3 (question
  then "Let go."): both passed, hook1's speech starts earlier (0.075 s
  of voice) and its second sentence is the narrated setup.
- Voice pass 1 failed on a dropped "a" in "one and a half"; the same
  text passed on pass 2 (Piper's audio differs run to run).

## Niche note

  [produced 2026-10-02 as "Which is easier to balance, a pencil or a
  broom? Broom flat at 1.50 s, pencil 0.53 s, 2.83x: root 8"; measured
  a uniform stick hinged at its foot on a fingertip, let go from rest 1
  degree off vertical with g 9.80665, theta'' = (3 g / (2 L)) sin theta,
  RK4 at 10,000 steps/s with bisection at 45 and 90 degrees: the 1.2 m
  broom lies flat at 1.4985 s (45 degrees at 1.2889 s, 4.9510 rad/s and
  tip 5.94 m/s at the floor, growth rate 3.5012/s, e-fold 0.2856 s), the
  15 cm pencil at 0.5298 s (45 degrees at 0.4557 s, 14.0037 rad/s, tip
  2.10 m/s, rate 9.9029/s); the ratio 2.82843 = sqrt(8) within 2.1e-14
  at the floor and at 45 degrees because every time scales with sqrt(L);
  quadrature of the energy form within 9.2e-14 s, half step within
  3.4e-15 s; the foot's push reverses at 48.2 degrees and the sideways
  push exceeds the vertical from 54.1 degrees, so the foot must be held;
  the broom from 0.5 / 2 / 5 degrees 1.6964 / 1.3005 / 1.0390 s; a 30 cm
  ruler 0.7492 s (half the broom), 1 m 1.3679 s, 10 cm 0.4326 s, a 4.8 m
  pole 2.9969 s (twice); shown at 1/3 speed on an 8 s cycle, 5 drops in
  40 s; task 20261002-101234]

## Upload

- orchestrator review (2026-10-02T10:52:39+03:00): task evidence, sheet.png and full frames at
  0.00, 2.40, 11.00, 25.60 and 39.98 s inspected; ffprobe h264 1080x1920 60 fps
  2400 frames 40.000 s; md5 a738b903ee7bb4068a34a9fa62241b53; title 99 chars, no angle brackets; description 4388 chars, no angle brackets, 11 tags; captions match narration word for word, compose pause alignment 21 of 21; measure.log matches the closed forms (broom 45 degrees at 1.2889 s, flat at 1.4985 s, 4.951 rad/s at the floor; pencil 0.4557 s and 0.5298 s, 14.004 rad/s; flat-time ratio 2.8284 = sqrt(8)); question on screen from frame 0 and
  repeated word for word before the payoff; nothing clipped at the 1080 px
  frame; last frame equals the first; approved for upload
- upload attempt 2 of 5 for the quota day that began 2026-10-02T10:00
  EEST, recorded at 2026-10-02T10:53:46+03:00 before starting scripts/yt-upload.py; one
  attempt (twostrings, yD8XL-OnEz4, published) was on record since the
  boundary
- uploaded private as vpn_dIASulU at 2026-10-02T10:53:55+03:00
  (https://youtu.be/vpn_dIASulU); channels.list 1 unit + videos.insert
  1,600 units; media/broom/upload.log
- scripts/yt-qa.py broom vpn_dIASulU --wait --publish in the
  foreground (started 2026-10-02T10:54:02+03:00): gate 15 of 15 on the first
  processed read (processed, succeeded, hd, 1080x1920, title, description
  and tags match, category 27, not made for kids, PT41S for the 40.000 s
  file, private before publish); published at 2026-10-02T10:54:21+03:00;
  re-read privacyStatus=public selfDeclaredMadeForKids=False
  embeddable=True; yt-qa quota 53 units; media/broom/publish.log
- attempt 2 of 5 complete: 1,654 units; slot 2 of 3 resolved as
  published (recorded 2026-10-02T10:54:46+03:00)

### Quota
- attempt 2 of the hard cap of 5 for the quota day that began
  2026-10-02T10:00 EEST; cost 1,654 units (the channels.list verification
  inside yt-upload.py, the 1,600-unit insert, and the gate run's reads,
  update and re-read as printed by yt-qa.py, 53); day total after two
  attempts 3,308 of 10,000 used, 6,692 remaining
