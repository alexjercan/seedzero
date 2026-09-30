# Produce short: Balloon or dice in a car, which way does the balloon lean

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day32

## Goal

Backlog idea (trend research 2026-09-30, task 20260930-100404, pillar 2
chaos and physics, everyday mechanics; read the full entry under
"Added by trend research 2026-09-30" in docs/niche.md):
"Balloon or dice in a car: a helium balloon (30 cm, 6.4 g against 17.3
g of air) and a hanging dice, each on a 50 cm string, in a car pulling
0.3 g; measure which way each leans and how far; expect both to settle
at atan(a / g), the dice backward and the balloon forward; buoyancy as
the displaced air's weight in the tilted effective gravity, added mass
half the air, no drag; the swing size depends on the damping chosen,
so narrate the direction and the settled angle; repeat the launch;
deterministic, no seed."

Orchestrator notes (2026-09-30, before this brief). Use a = 2.7778
m/s^2, "zero to one hundred kilometers an hour in ten seconds" (100 /
3.6 / 10), not 0.3 g, so the setup number is a phrase everyone knows;
then atan(a / g) = 15.82 degrees (g = 9.80665). The model, in the car's
frame: effective gravity g_eff = (-a, -g) (backward and down). Dice: a
point mass on a string L = 0.50 m from the ceiling, theta positive
backward, theta'' = (a cos theta - g sin theta) / L - c theta'.
Balloon: a 30 cm sphere on a string L = 0.50 m tied to the floor or
the console; displaced air m_air = 1.204 kg/m^3 times the sphere's
volume = 17.02 g, balloon plus helium m_b = 6.4 g, added mass m_add =
m_air / 2; the cabin air is at rest in the car's frame, so its pressure
gradient is along g_eff and the buoyancy is -m_air g_eff (up and
forward); phi positive forward, (m_b + m_add) L phi'' = (m_air - m_b)
(a cos phi - g sin phi) - (m_b + m_add) L c phi'. Both settle at tan =
a / g: the dice 15.82 degrees back, the balloon 15.82 degrees forward,
the same angle, opposite ways, whatever the masses. Checks, not facts
(orchestrator RK4 in /tmp/day32/check.py and check.log): lift over
inertia (m_air - m_b) / (m_b + m_add) = 0.712; small-swing periods
1.419 s (dice) and 1.681 s (balloon); with damping c = 2 per second and
a 0.5 s throttle ramp both are within 0.4 degrees of 15.82 by 4 s and
within 0.1 by 6 s (print the angles at the payoff time and the peaks;
with c = 1 the peaks are near 24 degrees); the car reaches 60 km/h at
6 s (50 m). Integrate both by RK4 at 1e-4 s or finer, check the
equilibrium against atan(a / g) and a half-step rerun, and print for
the description: 0.3 g gives 16.70 degrees, 0.5 g 26.57, 1.0 g 45.00;
the undamped peak after a sudden start is 2 atan(a / g) = 31.6 degrees;
the damping is a chosen number, say so and state c. State every
derived number above as a check the sim must print, not as a fact.

Drawing: side view inside the car (a simple cabin outline, the car
moving right, road marks or scenery sliding left at the car's speed so
the acceleration is visible, a speed readout "0 to 100 km/h in 10 s"
and the live km/h); the dice hanging from the ceiling near the mirror,
the balloon on its string from the floor or the console, both strings
drawn, an angle arc and a live degree readout for each, a dashed
vertical through each anchor; when settled, a dashed line at the
equilibrium tilt and labels "dice: 15.8 degrees back" and "balloon:
15.8 degrees forward"; the throttle window 6 to 8 s then a fade and
reset as tablecloth does; three or four runs in about 40 s; the last
frame equals the first; both objects at rest and vertical on frame 0
(or the run that crosses the seam identical at both ends).

Day thirty-two, third slot. Chosen because "which way does the
balloon go" is a famous debate most people answer wrong (backward), the
payoff is exact and parameter free (the same angle as the dice,
opposite way), and both objects move visibly in one frame. Question in
the first two seconds: "The car speeds up. Which way does the balloon
lean?" (or the producer's wording with the question by word nine; keep
the question identical in the title, the hook and the payoff). Setup
number: zero to one hundred in ten seconds (say "kilometers an hour"
once). Payoff number: forward, fifteen point eight degrees, the same
angle as the dice swinging back. The masses, the periods, the peaks
and the 0.3 g / 0.5 g / 1 g angles go to the card and the description.
Whisper risks: "Floor it" is risky, prefer "The car speeds up"; "dice"
(pre-test; "die" is worse), "helium" (pre-test; "the balloon" alone is
fine in the narration), "lean" and "leans"; avoid "do you" before a
verb; avoid "pull" as a noun; pre-test hooks with scripts/voiceover.sh
and keep the one whose question lands earliest under two seconds.
Make the last frame equal the first. Measure every fixed text line
with PIL before rendering and keep every line under 950 px, and the
title under 100 characters with no < or >. Music seed 100. Templates:
sims/pendulum or sims/bigswing (RK4 pendulum with an angle readout),
sims/tablecloth (two objects on one clock, slow motion not needed
here, reset fade), sims/braking or sims/swerve (a car body and road
marks). Sim name balloon: sims/balloon/balloon.py, projects/balloon/,
media/balloon/.

## Claim

Inside a car that pulls away from rest at 100 km/h per 10 s (a = 2.7778
m/s^2, 0.2833 g, after a 0.5 s throttle ramp), a dice on a 50 cm string
from the ceiling and a helium balloon (30 cm across, 6.4 g with its gas
against 17.02 g of displaced air, added mass half the air, no drag) tied
to the floor with its centre 50 cm above the anchor both settle where
tan(angle) = a / g: atan(a / g) = 15.82 degrees, the dice back and the
balloon forward, the same angle, opposite ways, whatever the masses.
With the chosen damping c = 2 per second the dice peaks at 22.04 degrees
(0.987 s after the throttle) and the balloon at 21.58 (1.128 s); both are
within 0.3 degrees of 15.82 by 4 s (16.09 and 15.60) and within 0.05 by
6 s (15.77 and 15.83); at 9.5 s 15.8162 and 15.8159. Small-swing periods
at rest 1.419 s (dice) and 1.681 s (balloon). Undamped sudden start: both
peak at 31.63 degrees = 2 atan(a / g). Other pulls: 0.3 g 16.70 degrees,
0.5 g 26.57, 1 g 45.00. Narrated: zero to one hundred kilometers an hour
in ten seconds (setup); forward, fifteen point eight degrees, the same
angle as the dice, the opposite way (payoff). Card: the question;
forward 15.8 degrees, dice 15.8 back; tan(angle) = a / g, whatever the
masses; balloon 6.4 g, the air it displaces 17.0 g; 0.3 g 16.7, 0.5 g
26.6, 1 g 45; chosen damping 2/s, peaks 22.0 and 21.6. Description: the
periods, the c = 1 peaks, the car's speed and distance, the checks.

## Evidence

### Measurements

`nix develop --command python3 sims/balloon/balloon.py --measure-only`
at 10:56:04 EEST (the final manifest), media/balloon/measure.log, copied
whole:

```
Wed Sep 30 10:56:04 AM EEST 2026
setup: side view inside a car that pulls away from rest at a = 100 km/h in 10 s = 2.7778 m/s^2 (0.2833 g) after a linear throttle ramp of 0.5 s; a dice (a point mass, drawn 8 cm across) hangs from the ceiling on a 50 cm string; a helium balloon of radius 15 cm (30 cm across, volume 14.14 litres) is tied to the floor with its centre 50 cm above the anchor; balloon plus gas 6.4 g, displaced air 1.204 kg/m^3 x volume = 17.02 g, added mass 0.5 of the air = 8.51 g, no drag; in the car's frame g_eff = (-a, -g), 10.1925 m/s^2 tilted 15.82 degrees back from the vertical; dice: theta'' = (a cos theta - g sin theta) / L - c theta' (theta positive backward); balloon: (m_b + m_add) L phi'' = (m_air - m_b)(a cos phi - g sin phi) - (m_b + m_add) L c phi' (phi positive forward); damping c = 2 per second, a chosen number; g = 9.80665 m/s^2; RK4 on (theta, theta', phi, phi', x, v) at 10000 steps per second (dt = 1e-04 s) for 9.5 s; 10 s cycle (600 frames) with the throttle 1 s into the cycle, 4 cycles in 40 s, no slow motion; drawn at 400 px per metre; deterministic, no seed
lift over inertia: (m_air - m_b) / (m_b + m_add) = (17.02 - 6.4) / (6.4 + 8.51) = 0.712; the balloon's net lift is 104.2 mN, 2.66 times its weight in displaced air
equilibrium: both settle where tan(angle) = a / g = 0.28325: atan(a / g) = 15.82 degrees (15.8150), the dice 15.82 degrees back and the balloon 15.82 degrees forward; the angle does not depend on the masses, the string length or the damping
small-swing periods: at rest 2 pi sqrt(L / g) = 1.419 s (dice) and 2 pi sqrt(L / (k g)) = 1.681 s (balloon, k = 0.712); about the tilted equilibrium (g_eff 10.1925) 1.392 s and 1.649 s undamped, 1.427 s and 1.709 s with c = 2 per second (2 pi / sqrt(w0^2 - c^2 / 4))
dice: RK4 with c = 2: swings back to a first peak of 22.04 degrees at 0.987 s after the throttle, back to 12.77 at 1.701 s, 17.31 at 2.415 s, 15.08 at 3.129 s (first peak to second peak 1.428 s); 16.09 degrees at 4 s (+0.28 from atan(a / g)), 15.77 at 6 s (-0.04), 15.8162 at 9.5 s (+0.0012); last more than 0.2 degrees from 15.82 at 4.08 s; at the payoff time (25.2 s of video, 4.20 s after the throttle) 15.87 degrees back; never crosses the vertical the other way: min 0.00 degrees
balloon: RK4 with c = 2: swings forward to a first peak of 21.58 degrees at 1.128 s after the throttle, back to 13.37 at 1.983 s, 16.86 at 2.838 s, 15.37 at 3.692 s (first peak to second peak 1.709 s); 15.60 degrees at 4 s (-0.22 from atan(a / g)), 15.83 at 6 s (+0.02), 15.8159 at 9.5 s (+0.0009); last more than 0.2 degrees from 15.82 at 4.02 s; at the payoff time (25.2 s of video, 4.20 s after the throttle) 15.82 degrees forward; never crosses the vertical the other way: min 0.00 degrees
car: RK4: 57.50 km/h (15.9722 m/s) and 45.95 m at 6 s (closed form with the 0.5 s ramp 57.50 km/h, 45.95 m; diffs 2.3e-11 m/s, 3.0e-11 m; with no ramp 60.00 km/h and 50.00 m); it passes 60 km/h at 6.25 s and would reach 100 km/h at 10.25 s (10 s of steady pull plus half the ramp); 92.5 km/h and 118.9 m at 9.5 s, the end of the run
undamped sudden start (c = 0, no ramp): the dice peaks at 31.63 degrees at 0.699 s and the balloon at 31.63 degrees at 0.828 s (closed form 2 atan(a / g) = 31.63; diffs -3.3e-07, -2.2e-08 degrees); with the 0.5 s ramp and no damping the peaks are 28.52 (dice, at 0.948 s) and 29.37 (balloon, at 1.077 s) degrees, and neither ever settles
for the description (damping c = 1 per second, same ramp): the dice peaks at 24.76 degrees at 0.963 s and the balloon at 24.75 at 1.095 s; 16.97 and 15.48 degrees at 4 s, 15.18 and 16.51 at 6 s; last more than 0.2 degrees from 15.82 at 8.13 s (dice) and 8.67 s (balloon)
for the description (other pulls, same strings, same damping): 0.3 g (2.942 m/s^2): atan = 16.70 degrees, RK4 at 8 s 16.70 (dice, back) and 16.71 (balloon, forward), peaks 23.3 and 22.8; 0.5 g (4.903 m/s^2): atan = 26.57 degrees, RK4 at 8 s 26.57 (dice, back) and 26.57 (balloon, forward), peaks 37.1 and 36.4; 1 g (9.807 m/s^2): atan = 45.00 degrees, RK4 at 8 s 45.01 (dice, back) and 45.00 (balloon, forward), peaks 63.4 and 62.6
check at half the time step (20000 steps per second): dice peak 22.037243 degrees (+4.4e-08) at 0.987414 s (-7.0e-10), 15.773026 at 6 s (-9.5e-15); balloon peak 21.575152 degrees (+9.3e-08) at 1.128344 s (-2.2e-09), 15.831430 at 6 s (+5.1e-14); car at 6 s 45.949074 m (+2.7e-11)
schedule (video time, real speed): cycles of 10 s start at 0.00, 10.00, 20.00, 30.00, 40.00 s; the throttle 1 s into each cycle at 1.00, 11.00, 21.00, 31.00 s; the dice peaks at 1.99, 11.99, 21.99, 31.99 s and the balloon at 2.13, 12.13, 22.13, 32.13 s; the settled labels light at 5.08, 15.08, 25.08, 35.08 s (dice) and 5.02, 15.02, 25.02, 35.02 s (balloon); the run fades out over 9.40 to 9.70 s of each cycle and the resting cabin fades in over 9.70 to 10.00 s, the car at 81.5 km/h and 92.3 m when the fade starts; on the first frame the cycle is 0 s in: both at rest, hanging straight, the car still; title until 3 s; payoff card from 25.2 s; the title fades back in over the last 0.5 s and the last frame repeats the first (the scene is periodic: 40 s holds exactly 4 cycles)
text widths: overlay@34 886 px, title line 1@56 507 px, title line 2@56 512 px, title line 3@56 786 px, legend@40 781 px, clock@28 376 px, clock rest@28 411 px, label balloon@40 167 px, live balloon@28 340 px, live rest@28 471 px, settled balloon@28 457 px, label dice@40 93 px, live dice@28 340 px, settled dice@28 408 px, speed@48 251 px, distance@28 337 px, payoff line 1@40 758 px, payoff line 2@40 841 px, payoff line 3@40 906 px, payoff line 4@40 898 px, payoff line 5@40 894 px, payoff line 6@40 936 px
layout: the left column ends at x 517 px and the right column starts at 612 px; the rows end 134 px under the band top, the speed row spans 186 to 270 px and the roof is at 330 px; the balloon's top at its widest swing (21.58 degrees) is 534 px under the band top, 204 px under the roof; the dice's lowest point (22.04 degrees) is 538 px, 242 px above the floor; the balloon's front at its widest is x 534 px and the dice's back x 702 px, 169 px apart; the road ends 1070 px under the band top, 30 px above the band's bottom; the third title row ends at y 330 px against the band top at 330
Wed Sep 30 10:56:11 AM EEST 2026
```

Earlier measure runs, not kept (the physics numbers were identical in
every run): the first run (10:51) failed the width assert on the overlay
"0 to 100 km/h in 10 s | 50 cm strings | 2/s damping | no seed" (1157
px; now 886 px without the damping, which moved to the legend) and on
card line 6 (1095 px; now "chosen damping 2/s: peaks 22.0 and 21.6", 936
px); card line 2 went from 948 px to "forward 15.8 degrees, dice 15.8
back" (841 px). The second smoke run (10:52) crashed in the road-mark
drawing when a dash lay entirely off the left edge (an inverted
rectangle); fixed by skipping empty rectangles. The third run (10:54,
title changed to the kept hook, payoff_t 26.0) produced the smoke frames;
payoff_t then moved to 25.2 after the voice timing.

The brief's checks against the log: atan(a / g) = 15.82 degrees (log
15.82, 15.8150); lift over inertia 0.712 (0.712); small-swing periods
1.419 and 1.681 s (1.419, 1.681); within 0.4 degrees by 4 s (dice +0.28,
balloon -0.22) and within 0.1 by 6 s (-0.04, +0.02); c = 1 peaks near 24
(24.76 and 24.75); undamped sudden-start peak 2 atan(a / g) = 31.6
(31.63, RK4 diffs -3.3e-07 and -2.2e-08); 0.3 g 16.70, 0.5 g 26.57, 1.0
g 45.00 (16.70 / 26.57 / 45.00 closed form; RK4 at 8 s 16.70 / 16.71,
26.57 / 26.57, 45.01 / 45.00); RK4 at 1e-4 s or finer (1e-4, half step
2e-4 moves the peaks by 4.4e-08 and 9.3e-08 degrees); car at 6 s "60
km/h (50 m)": holds only with no ramp (60.00 km/h, 50.00 m); with the
brief's own 0.5 s ramp the sim gives 57.50 km/h and 45.95 m at 6 s and
60 km/h at 6.25 s (the sim wins; the description states both). No other
check failed.

### Production

- Sim: sims/balloon/balloon.py with projects/balloon/manifest.json (seed
  0, fps 60, g 9.80665, zero_to_km_h 100, zero_to_s 10, throttle_ramp_s
  0.5, string_m 0.5, balloon_radius_m 0.15, balloon_mass_g 6.4,
  air_density_kg_m3 1.204, added_mass_fraction 0.5, damping_per_s 2,
  description_damping_per_s 1, description_accels_g 0.3 / 0.5 / 1.0,
  settle_deg 0.2, steps_per_second 10000, sim_end_s 9.5, cycle_s 10,
  go_at 1.0, first_cycle_at 0.0, reset_fade 0.6, scene_duration 40,
  px_per_m 400, dice_side_m 0.08, dash_m 0.4, dash_period_m 1.2,
  title_until 3.0, payoff_t 25.2, payoff_hold 0.6, loop_fade 0.5,
  music_seed 100, music_gain 0.18, voice_offset 0.6, caption_y 0.75).
  One RK4 state (theta, theta', phi, phi', x, v) with a time-dependent
  throttle a(t) = a min(1, t / 0.5 s); extremes from the sign changes of
  the angular velocity refined linearly; the settle time is the last
  sample more than 0.2 degrees from atan(a / g); checked against
  atan(a / g), 2 atan(a / g), the closed-form car motion and a half-step
  rerun. Frames are drawn from the frame integer modulo the 600-frame
  cycle, so the scene is exactly periodic; the last frame is the live
  frame 0.
- Layout (1080x1920): overlay "0 to 100 km/h in 10 s | 50 cm strings |
  no seed" at y 96 (34 px teal, drawn by compose); title three rows at y
  186, 244, 302 (56 px) until 3 s, then the legend "0 to 100 km/h in 10
  s, damping 2/s" at y 236 (40 px) and the clock "N.NN s after the
  throttle" / "at rest before the throttle" at y 290 (28 px); geometry
  band y 330 to 1430 drawn at 2x and downsampled: header columns
  (balloon left at x 60 in coral, dice right to x 1020 in teal) with the
  label at y 370 (40 px), the live readout "NN.N degrees forward / back"
  or "0.0 degrees, hanging straight" at y 414 (28 px, gold once
  settled), the settled line "settles 15.8 degrees forward / back" at y
  450 (28 px gold, 25 percent until the object settles, then lit over
  0.3 s); the speed row "NN km/h" at y 540 (48 px) and "NN m since the
  start" at y 586 (28 px); the cabin cutaway with the roof at y 660, the
  floor at 1110, the dashboard and windshield at the front (right), the
  mirror on a stalk by the windshield, the wheels on the road at y
  1250, the road surface y 1250 to 1400 with lane dashes (0.4 m every
  1.2 m) sliding left at the car's speed, each smeared over one frame's
  travel so they never strobe; the dice anchor at x 800 on the roof and
  the balloon anchor at x 400 on the floor, a muted dashed plumb line
  through each, a 70 px angle arc in the object's colour from the plumb
  line to the string, and once settled a gold dashed line at the
  equilibrium tilt through each anchor; captions at y 1440 (64 px); the
  six-line gold card from y 1572 at a 48 px pitch.
- Hook pre-tests (media/balloon/hooks/pretest.log, 10:52:59 to 10:53:17
  EEST), each through scripts/voiceover.sh with the setup sentence, all
  seven passed on the first pass; question onset = the silence_end
  before the question plus 0.6 s, or the voice start plus 0.6 s when the
  question comes first: hook1 "The car speeds up. Which way does the
  balloon lean?" 1.93 s; hook2 "Which way does the balloon lean when the
  car speeds up?" 0.80 s (0.197 s leading silence); hook3 "The car
  speeds up. Which way does the balloon swing?" no pause detected after
  "speeds up."; hook4 "The car pulls away. Which way does the balloon
  lean?" 1.94 s; hook5 "Which way does the balloon lean? The car speeds
  up." 0.80 s; hook6 "A balloon in a car. The car speeds up. Which way
  does the balloon lean?" 4.89 s; words "A dice hangs from the mirror. A
  helium balloon floats on a string, tied to the floor. The dice leans
  back. The balloon leans forward. So, once more, from rest." passed
  (dice, helium, leans, "So, once more" all clean). Kept hook2: the
  question comes first inside one natural sentence that also carries the
  setup, and lands 1.1 s earlier than the brief's two-sentence wording.
- Narration: projects/balloon/narration.txt, 113 words, the question at
  words 1 to 11, identical in the title, the hook and the payoff ("So,
  once more, from rest. Which way does the balloon lean when the car
  speeds up? Forward, from the first push."); numbers as words ("Zero to
  one hundred kilometers an hour, in ten seconds", "Fifteen point eight
  degrees forward"); American "kilometers"; "the balloon" alone in the
  narration (helium only in the description).
- Voice (media/balloon/voice.log): pass 1 at 10:54:41 (113 words): "ok:
  transcript matches narration (35.758730s) ->
  media/balloon/voice.wav". One pass, no mishearing. The voice ends at
  36.36 s of video.
- Timing (scripts/voice-timing.py media/balloon/voice.wav 0.6 in
  media/balloon/timing.log; the piece transcripts are whisper's own and
  heard "dice" as "day" in one piece and "from rest" as "from a rest";
  the full round trip passed): the first piece 0.60 to 8.64 s ("Which
  way does the balloon lean when the car speeds up? Zero to 100
  kilometers an hour in 10 seconds. A dice hangs from the mirror."; the
  voice has no leading silence, media/balloon/silences.log, so the
  question starts at 0.60 s and its first pause is at 2.86 to 3.07 s of
  voice, 3.46 to 3.67 s of video); "A balloon floats on a string," 8.64
  to 10.40; "tied to the floor." 10.40 to 11.51; "The dice swings back,
  as you expect." 11.51 to 13.84; "The balloon swings forward." 13.84 to
  15.52; "Both swing, then settle. So, once more, from rest." 15.52 to
  19.08; "Which way does the balloon lean when the car speeds up?
  Forward," 19.08 to 22.64; "from the first push," 22.64 to 23.79; "It
  swings and settles." 23.79 to 25.43; "Fifteen point eight degrees
  forward, the same angle as the dice." 25.43 to 29.22; "The opposite
  way." 29.22 to 30.36; "The balloon is lighter than the air around it."
  30.36 to 32.61; "The heavy air piles up at the back," 32.61 to 34.60;
  "and pushes the balloon forward." 34.60 to 36.36.
- Schedule: cycles of 10 s start at 0, 10, 20, 30 s; the throttle at
  1.00, 11.00, 21.00, 31.00 s; the dice peaks at 1.99, 11.99, 21.99,
  31.99 s and the balloon at 2.13, 12.13, 22.13, 32.13 s; the settled
  labels light at 5.02 / 5.08 s (plus 10 k); the run fades out over 9.40
  to 9.70 s of each cycle (the car at 81.5 km/h) and the resting cabin
  fades in over 9.70 to 10.00 s. Sync: the first run plays under the
  question and the setup; "The dice swings back, as you expect" (11.51
  to 13.84) plays as the dice swings back to its 11.99 s peak, "The
  balloon swings forward" (13.84 to 15.52) as the balloon rocks about
  15.8 forward, "Both swing, then settle" (15.52) as both labels light
  (15.02, 15.08); the third run starts at 21.00 under the repeated
  question, "Forward" (about 22.4 s) lands on the balloon's 22.13 s
  peak, "It swings and settles" (23.79 to 25.43) as it settles, and
  "Fifteen point eight" (from 25.43) comes with both labels lit (25.02,
  25.08) and the card rising (payoff_t 25.2, lit at 25.8); the fourth
  run plays under "The balloon is lighter than the air around it. The
  heavy air piles up at the back, and pushes the balloon forward" (30.36
  to 36.36) as the balloon swings forward again (peak 32.13) and settles
  (35.02).
- Smoke frames (--frames): 12 PNGs at 0.0, 1.5, 2.0, 3.5, 5.5, 9.55,
  9.85, 12.0, 22.0, 25.5, 27.0, 39.98 s (media/balloon/smoke-*.png, from
  the run with payoff_t 26.0), used to check the cabin, the arcs, the
  settled lines, the fade and the card before the render.
- Footage: render 10:56:11 to 10:56:51 (media/balloon/render.log): loop
  check 0 px, periodicity check 0 px, loop step 0 px (the frame before
  the last is the resting cabin at 99.7 percent, under the 24-level
  threshold); media/balloon/footage.mp4 2400 frames.
- Compose: scripts/compose.sh 10:56:57 to 10:57:08 (compose.log): music
  seed 100, 40.00 s; "captions: 21 pauses detected, 21 matched, max
  chunk start shift 1.106 s against word-count timing" (every pause
  matched, no fallback); final.mp4 40.000000 s; preview 40.066667 s;
  sheet 8x5 at 1 fps.
- Text widths (PIL, from measure.log, all under 950 px): overlay 886,
  title 507 / 512 / 786, legend 781, clock 376 / 411, label balloon 167,
  live balloon 340, live rest 471, settled balloon 457, label dice 93,
  live dice 340, settled dice 408, speed 251, distance 337, payoff 758 /
  841 / 906 / 898 / 894 / 936. Layout (asserted in measure): the header
  columns end at x 517 and start at 612 px; the balloon's top at its
  widest swing is 204 px under the roof, the dice's lowest point 242 px
  above the floor, the two objects 169 px apart at their widest; the road
  ends 30 px above the band's bottom; the third title row ends at y 330,
  the band top (the band's first text is at y 356).

### Local QA

- Frames extracted from media/balloon/final.mp4 (never edited) and
  viewed with the Read tool at full resolution:
  - frame-0.00.png: overlay, three title rows ("Which way does" / "the
    balloon lean" / "when the car speeds up?"), both objects hanging
    straight with "0.0 degrees, hanging straight", "0 km/h", "0 m since
    the start", the cabin, crisp lane dashes, no caption, no card.
    Clean, works as the thumbnail.
  - frame-1.00.png: caption "Which way does the" at y 1440; the title
    up; the car still (the throttle comes at 1.00 s).
  - frame-2.10.png: both near their peaks ("21.5 degrees forward",
    "21.3 degrees back"), the arcs and plumb lines, "9 km/h", caption
    "balloon lean when".
  - frame-22.10.png: legend and clock "1.10 s after the throttle", the
    settled lines dim, both near their peaks on the third run, caption
    "the car speeds up?".
  - frame-25.60.png: caption "Fifteen point eight"; both live readouts
    gold ("16.0 degrees forward", "15.6 degrees back"), both "settles
    15.8 degrees" lines lit, the gold dashed equilibrium lines through
    both anchors, "43 km/h", the card fading in.
  - frame-27.00.png: the six card rows lit and inside the frame ("which
    way does the balloon lean?" / "forward 15.8 degrees, dice 15.8 back"
    / "tan(angle) = a / g, whatever the masses" / "balloon 6.4 g, the
    air it displaces 17.0 g" / "0.3 g: 16.7 degrees, 0.5 g: 26.6, 1 g:
    45" / "chosen damping 2/s: peaks 22.0 and 21.6"); caption "degrees
    forward."; both readouts "15.8 degrees".
  - frame-39.98.png: title back, hud gone, the same picture as
    frame-0.00.
  - frame-12.00.png and frame-35.00.png extracted for the record (mid
    second and fourth runs), not needed after the sheet.
  - sheet.png (40 thumbnails at 1 fps): the title for the first 3 s,
    then the legend and clock; four runs with the fade at 9, 19, 29, 39
    s; captions readable in every thumbnail from 1 to 36 s; the card
    from 26 s; no clipped text, nothing at the frame edge.
- Question: on screen from frame 0 in the title (507 / 512 / 786 px),
  spoken from 0.60 s (no leading silence in the voice); "Which way does
  the" caption 0.600 to 1.640, "balloon lean when" 1.640 to 2.421, "the
  car speeds up?" 2.421 to 3.666.
- Captions: media/balloon/captions.filter, 38 chunks, 113 words, matches
  projects/balloon/narration.txt word for word (script check True),
  longest chunk 20 characters; "Forward, from the" 22.237 to 23.208,
  "first push." 23.208 to 23.922, "It swings, and" 23.922 to 25.021,
  "settles." 25.021 to 25.542, "Fifteen point eight" 25.542 to 26.712,
  "degrees forward." 26.712 to 27.655, "The same angle as" 27.655 to
  28.616, "the dice, the" 28.616 to 29.638, "opposite way." 29.638 to
  30.470; the last chunk "forward." 36.043 to 36.359.
- Bands: signalstats over all 2,400 footage frames: the caption band
  (rows 1440 to 1530) and the overlay band (rows 96 to 130) have YMAX
  28 in every frame (background only), so the sim draws nothing under
  the captions or the overlay.
- Loop: footage last frame equals the first (0 px). In final.mp4 frame
  2399 against frame 0: 47,242 px over 8 levels, 1,261 over 32, max 77,
  mean 0.71 (h264 quantisation: the footage frames are identical); frame
  2398 against 2399: 46,169 over 8, 0 over 32, max 30 (the resting cabin
  at 99.7 percent against 100); frame 0 against 1 for reference: 602
  over 8, 258 over 32, max 60.
- ffprobe: h264 1080x1920 yuv420p 60/1, 2400 frames; aac 22050 Hz mono;
  40.000000 s; 3,754,663 bytes; moov at byte 36 before mdat at 44,176
  (faststart).
- md5sum media/balloon/final.mp4: 979904394bb7ab723d326950766ced4b
- Narrated numbers against measure.log: "Zero to one hundred kilometers
  an hour, in ten seconds" (setup line, a = 100 km/h in 10 s); "The dice
  swings back" (dice line, first peak 22.04 degrees back); "The balloon
  swings forward" (balloon line, 21.58 forward); "Both swing, then
  settle" (settle at 4.08 and 4.02 s); "Forward" (balloon line);
  "Fifteen point eight degrees forward" (equilibrium line, atan(a / g) =
  15.82; at the payoff time 15.82 forward); "The same angle as the dice,
  the opposite way" (equilibrium line, the dice 15.82 back); "The
  balloon is lighter than the air around it" (setup line, 6.4 g against
  17.02 g). Card: 15.8 (15.82), 6.4 g, 17.0 g (17.02), 16.7 / 26.6 / 45
  (16.70 / 26.57 / 45.00), 2/s, 22.0 and 21.6 (22.04, 21.58).
- Metadata check: every number in the description read against
  media/balloon/measure.log by script after the final run (90 numeric
  tokens, 66 distinct, commas stripped, 0 missing).

### Metadata

projects/balloon/metadata.json: title "Which way does the balloon lean
when the car speeds up? Forward, 15.8 degrees, the dice 15.8 back" (97
characters, no angle brackets); description 3,548 characters, ASCII,
with the model (the tilted effective gravity, the buoyancy along it,
the added mass, the chosen damping c = 2), the "Measured:" list, the
"Why:" paragraph (the air thrown back piles up at the back, the pressure
difference is the buoyancy and pushes the balloon forward; the damping
is a chosen number), the rerun line and the AI-made line; 11 tags
(balloon in a car, which way does the balloon lean, helium balloon,
buoyancy, pendulum, acceleration, car physics, physics, physics
visualization, simulation, shorts); categoryId 27; privacyStatus
private; containsSyntheticMedia true; selfDeclaredMadeForKids false.

### Deviations from the brief

- Hook "Which way does the balloon lean when the car speeds up?"
  instead of "The car speeds up. Which way does the balloon lean?": the
  pre-test put the brief's wording at 1.93 s (under two seconds but
  with 70 ms to spare), the kept single sentence at 0.80 s in the
  pre-test and at 0.60 s in the final voice. The title, the hook and
  the payoff carry the same eleven words, and the answer follows them
  ("Forward, from the first push.").
- The balloon's 50 cm is from the floor anchor to the balloon's centre
  (the point-mass length in the brief's equation); the drawn string is
  35 cm plus the 15 cm radius. The setup line and the description say
  so.
- The car at 6 s: the brief's "60 km/h at 6 s (50 m)" ignores its own
  0.5 s throttle ramp; with the ramp the sim gives 57.50 km/h and 45.95
  m at 6 s and 60 km/h at 6.25 s, 100 km/h at 10.25 s. The description
  gives both; the phrase "0 to 100 km/h in 10 s" names the steady pull.
- The throttle stays on to the reset fade (8.4 s after the throttle,
  81.5 km/h) rather than a 6 to 8 s window that ends with the throttle
  off, so the objects never swing back to vertical inside a run; each
  run ends in the fade to the resting cabin.
- The live readouts and the settled labels sit in two header columns
  above the cabin (balloon left, dice right, matching their places in
  the car) rather than beside the objects, so no text crosses the
  cabin drawing; the angle arcs and the gold equilibrium dashes are at
  the anchors.
- Scenery: only the lane dashes slide (smeared over one frame's travel
  so they do not strobe at 80 km/h); the speed and distance readouts
  carry the acceleration. No posts or trees.
- The dice is a point mass in the model, drawn 8 cm across; the seats
  are left out of the cutaway so the balloon's string from the floor is
  visible.
- The card's second line reads "forward 15.8 degrees, dice 15.8 back"
  (841 px) because "the same angle as the dice, opposite way" did not
  fit under 950 px with the number.
- The payoff card lands at 25.2 s (lit at 25.8) so it is rising while
  "Fifteen point eight" is spoken (25.43 s by whisper, caption 25.542);
  the settled labels are already lit at 25.02 and 25.08 s.
- Caption alignment leads the speech by up to 1.1 s against word-count
  timing (the compose line); the aligned chunks put "Fifteen point
  eight" at 25.542, 0.1 s after whisper's piece start.

## Niche note

[produced 2026-09-30 as "Which way does the balloon lean when the car
speeds up? Forward, 15.8 degrees, the dice 15.8 back"; measured both a
hanging dice and a floor-tied helium balloon (6.4 g against 17.02 g of
displaced air, added mass half the air, no drag) on 50 cm strings
settling at atan(a / g) = 15.82 degrees in a car pulling 100 km/h per
10 s (2.7778 m/s^2), the dice back and the balloon forward; with the
chosen damping 2/s peaks 22.04 and 21.58 degrees, within 0.3 by 4 s and
0.05 by 6 s; periods 1.419 and 1.681 s; undamped sudden start 31.63 = 2
atan(a / g); 0.3 g 16.70, 0.5 g 26.57, 1 g 45.00; RK4 at 10,000 steps a
second, half step within 1e-7 degrees; task 20260930-104027]

## Upload

- orchestrator review (2026-09-30T11:20:59+03:00): task evidence, sheet.png and full frames at
  0.00, 2.10, 25.60 and 39.98 s inspected; ffprobe h264 1080x1920 60 fps
  2400 frames 40.000 s; md5 979904394bb7ab723d326950766ced4b; title 97
  chars, no angle brackets; captions match narration word for word;
  measure.log numbers match the closed forms in /tmp/day32/check.py
  (a = 2.7778 m/s^2 for 0 to 100 km/h in 10 s, atan(a/g) = 15.82 deg
  for both the balloon and the dice, with 2/s damping 15.77 and 15.83
  deg at 6 s); approved for upload
- upload attempt 3 of 5 for the quota day that began 2026-09-30T10:00
  EEST, recorded at 2026-09-30T11:20:59+03:00 before starting scripts/yt-upload.py; two
  attempts (wallbounce vC17_o8y_y4 and belt mYyXLCyecNA, both published)
  were on record since the boundary
- uploaded private as 910Al8RGRNU at 2026-09-30T11:21:04+03:00
  (https://youtu.be/910Al8RGRNU); channels.list 1 unit + videos.insert
  1,600 units; media/balloon/upload.log
- scripts/yt-qa.py balloon 910Al8RGRNU --wait --publish in the foreground
  (started 2026-09-30T11:21:12+03:00): gate 15 of 15 on the fourth read
  (processed, succeeded, hd, 1080x1920, title, description and tags
  match, category 27, not made for kids, PT41S for the 40.000 s file,
  private before publish); published at 2026-09-30T11:21:59+03:00;
  re-read privacyStatus=public selfDeclaredMadeForKids=False
  embeddable=True; yt-qa quota 55 units; media/balloon/publish.log
- attempt 3 of 5 complete: 1,656 units; slot 3 of 3 resolved as
  published (recorded 2026-09-30T11:22:36+03:00)

### Quota
- attempt 3 of the hard cap of 5 for the quota day that began
  2026-09-30T10:00 EEST; cost 1,656 units (the channels.list verification
  inside yt-upload.py, the 1,600-unit insert, and the gate run's 4 reads,
  update and re-read as printed by yt-qa.py); day total after three
  attempts 1,664 + 1,654 + 1,656 = 4,974 units plus 5 for the 10:02
  stats refresh, 4,979 of 10,000 used, 5,021 remaining before the
  closing stats refresh; target of three met

## Push
- committed as 5710175 "Publish the day thirty-two slate" and pushed to
  origin/master at 2026-09-30T11:25:56+03:00 (ec85030..5710175; the push also carried
  the unpushed day 31 commit 3b58b88); media/ and secrets/ not committed
