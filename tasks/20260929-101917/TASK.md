# Produce short: Draw shot, the same low hit on a near ball beside a far ball

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day31

## Goal

Backlog idea (trend research 2026-09-29, task 20260929-100144, pillar 2
chaos and physics, pool; read the full entry under "Added by trend
research 2026-09-29" in docs/niche.md):
"Draw shot: two identical low hits (2.0 m/s, tip half a radius below
centre, 2.5 m/s of backspin, cloth mu 0.2), the object ball 30 cm
away beside 1.2 m away; measure where the cue ball goes after the
head-on hit; expect the backspin to run out at 76.5 cm (d* = (v0^2 -
(v0 - 0.4 R w0)^2) / (2 mu g), at 1.000 m/s), the 30 cm cue ball to
come back at 0.486 m/s (2/7 of the 1.70 m/s of spin left) and the 1.2
m cue ball to follow at 0.204 m/s (2/7 of the 0.714 m/s rolling
speed, reached after 89 cm); the 76.5 cm depends on mu and the tip
offset, so state both; builds on sims/cueball; repeat the shot;
deterministic, no seed."

Orchestrator notes (2026-09-29, before this brief). The model: pool
balls of radius 28.6 mm, equal masses, cloth sliding friction mu 0.2, g
9.80665, no rolling resistance, no cushion. The cue strikes the cue
ball level, half a radius below centre, so the ball leaves at v0 = 2.0
m/s with backspin R w0 = (5/2)(h / R) v0 = 2.5 m/s (print the impulse
relation). While it slides, v falls at mu g and the backspin R w falls
at (5/2) mu g; the slip v + R w falls at (7/2) mu g until rolling.
Head-on hit on an equal ball at rest: instantaneous, elastic, no
ball-ball friction; the cue ball keeps its spin and gives all its
speed to the object ball, which leaves sliding with no spin and rolls
at 5/7 of its speed. After the hit the cue ball (v = 0) keeps its spin
and the cloth turns it into motion: with backspin R w it ends rolling
back at (2/7) R w; with topspin (already rolling) it follows at (2/7) v.
Checks, not facts (orchestrator closed forms in /tmp/day31/check.py):
backspin gone at 0.5099 s after 76.48 cm at 1.0000 m/s; rolling at
0.6555 s after 88.97 cm at 0.7143 m/s; panel A, object ball 30 cm
ahead (centre to contact distance; say which in the log): hit at 0.1630
s at 1.6802 m/s with R w = +1.7006 m/s of backspin left, the cue ball
comes back at 0.4859 m/s after 6.02 cm of slip, the object ball rolls
at 1.2002 m/s; panel B, object ball 120 cm ahead: hit at 1.0900 s at
0.7143 m/s rolling (topspin 0.7143), the cue ball follows at 0.2041 m/s
after 1.06 cm of slip, the object ball rolls at 0.5102 m/s. The
threshold 76.48 cm: any object ball closer than that draws the cue ball
back, any farther and it follows. Print the threshold at mu 0.15 and
0.25 and at a tip offset of 0.3 R for the description (it depends on
both; state both on the card). Use exact piecewise integration between
the events (as sims/cueball did) and check against a stepped
integration.

State every derived number above as a check the sim must print, not as
a fact.

Drawing: two panels stacked, the same table cloth, the same scale and
the same clock, side view or top-down (the producer's choice; side view
with a stripe shows the spin best, as sims/cueball did); a cue stick
tip striking low at the start; panel A the object ball at 30 cm, panel
B at 1.2 m; a gold dashed line at 76.5 cm on both panels labelled
"backspin gone here"; the spin shown by a stripe or a dot on the cue
ball and a small curved arrow; after the hit the cue ball visibly
comes back in A and follows in B, with a readout "comes back 0.49 m/s"
/ "follows 0.20 m/s"; the object ball leaves the frame or is stopped
by the panel edge (no cushion physics; fade it). Slow motion so the
1.1 s to the far hit plays over several seconds (say the factor on
screen). Repeat the shot (fade and reset as tablecloth and cutshot do);
several shots in about 40 s; the last frame equals the first.

Day thirty-one, third slot. Chosen because pool shorts are the channel's
strongest recent genre (cue ball follow 957, cut shot 952), "does the
cue ball come back?" has a visible yes and no on the same hit, the
threshold is a closed form, and no seed. Question in the first two
seconds: "Hit it low. Does the cue ball come back?" (or the producer's
better wording; keep the words before the question under nine; keep
the question identical in the title, the hook and the payoff; whisper
dropped "do" before "you", so pre-test "Does the cue ball come back"
early). Setup number: two meters a second (or the 30 cm and 1.2 m
distances on screen only). Payoff number: only if the other ball is
closer than seventy six centimeters; the backspin runs out there. Near:
it comes back; far: it follows. The 0.49 and 0.20 m/s, the 1.70 m/s of
spin left and the mu and tip-offset dependence go to the card and the
description. Whisper risks: "cue" may come back "queue" (the normaliser
may not fold it; pre-test and reword to "white ball" if it fails);
"backspin" may split as "back spin"; write "seventy six centimeters";
pre-test the hooks with scripts/voiceover.sh and keep the one whose
question lands earliest under two seconds. Make the last frame equal
the first. Measure every fixed text line with PIL before rendering and
keep every line under 950 px, and the title under 100 characters with
no < or >. Music seed 97. Templates: sims/cueball (the sliding and
rolling cue ball, piecewise exact integration, stripe, head-on hit),
sims/cutshot (the latest pool short, cycles and reset fade), sims/
tablecloth (two panels on one clock). Sim name drawshot:
sims/drawshot/drawshot.py, projects/drawshot/, media/drawshot/.

## Claim

The same low hit (a level cue half a radius below the centre, the ball
leaving at 2 m/s with 2.5000 m/s of backspin, mu 0.2) makes the cue
ball come back only if the other ball is closer than 76.48 cm: that is
where the cloth has rubbed the backspin away (0.5099 s after the
strike, the ball at 1.0000 m/s). With the other ball 30 cm away the cue
ball hits it at 1.6802 m/s with 1.7006 m/s of backspin left, stops and
rolls back at 0.4859 m/s (2/7 of the spin left). With the other ball
1.2 m away the backspin ran out first, the ball rolls in at 0.7143 m/s
and follows at 0.2041 m/s (2/7 of 0.7143). At 76.48 cm it stops dead.
The line moves with the cloth (mu 0.15: 101.97 cm, mu 0.25: 61.18 cm),
the tip (0.3 R low: 52.01 cm, 0.4 R low: 65.26 cm) and the speed (1.5
m/s: 43.02 cm, 3 m/s: 172.08 cm). Narrated: two meters a second
(setup); only if the other ball sits closer than seventy six
centimeters, where the backspin runs out (payoff). Card: the question,
the answer, 76.5 cm, 30 cm back 0.49 m/s with 1.70 m/s spin left, 1.2 m
follows 0.20 m/s, mu 0.15 / 0.25: 102 / 61 cm, tip 0.3 R: 52 cm.
Description: the sweep, the cloth, tip and speed dependence, the
stepped check.

## Evidence

### Measurements

`nix develop -c python3 sims/drawshot/drawshot.py --measure-only` at
11:08:50 EEST (the final manifest), media/drawshot/measure.log, copied
whole:

```
Tue Sep 29 11:08:50 AM EEST 2026
setup: the same low hit on two cue balls, drawn from the side one above the other; a level cue strikes each ball 0.5 radius below its centre and it leaves at v0 = 2 m/s; ball radius 28.6 mm (a 57.2 mm ball), equal masses, a solid sphere I = 2/5 m R^2, cloth sliding friction mu = 0.2 on any slipping contact, g = 9.80665 m/s^2, no rolling resistance, no cushion; the other ball waits dead ahead, 30 cm of the cue ball's travel to the hit on top (centre to contact: the cue ball's centre moves 30 cm before the balls touch, centres 35.72 cm apart) and 120 cm below (centres 125.72 cm apart); the hit is head on, instantaneous, elastic and frictionless between the balls (the cue ball hands over its speed and keeps its spin); every ball integrated as exact constant-acceleration pieces between the events (a slip closing, the hit), checked against the closed forms and a stepped integration; shown at 1/5 speed on a 10 s cycle (600 frames) with the strike 1.6 s into the cycle, 4 shots in 40 s; drawn at 680 px per metre (ball radius 19.4 px); deterministic, no seed
launch: the impulse J at h = 0.5 R below the centre gives m v0 = J and (2/5) m R^2 omega0 = J h, so R omega0 = (5/2)(h / R) v0 = 2.5000 m/s of backspin (omega0 = 87.413 rad/s against the roll); the slip v - R omega starts at 4.5000 m/s; the cloth slows the ball at mu g = 1.96133 m/s^2, the backspin R omega at (5/2) mu g = 4.90332 m/s^2 and the slip at (7/2) mu g = 6.86465 m/s^2
backspin gone: the cue ball's backspin is gone at 0.5099 s after 76.48 cm at 1.0000 m/s (closed forms h v0 / (mu g) = 0.5099 s, d* = v0^2 h (2 - h) / (2 mu g) = 76.48 cm = (v0^2 - (v0 - 0.4 R omega0)^2) / (2 mu g) = 76.48 cm, v0 (1 - h) = 1.0000 m/s; diffs 0.0e+00, 0.0e+00, 0.0e+00); from there the spin turns forward and the ball rolls at 0.7143 m/s at 0.6555 s after 88.97 cm (closed forms (5 v0 - 2 R omega0) / 7 = 0.7143 m/s, (v0 + R omega0) / (7/2 mu g) = 0.6555 s, 88.97 cm; diffs 1.1e-16, 0.0e+00, 0.0e+00)
near (the other ball 30 cm ahead, closer than d*): the cue ball hits it at 0.1630 s at 1.6802 m/s with R omega = -1.7006 m/s, 1.7006 m/s of backspin left (closed forms 0.1630 s, 1.6802 m/s, -1.7006 m/s; diffs 0.0e+00, 0.0e+00, 2.2e-16); right after the hit the cue ball has 0 m/s and keeps its backspin; the cloth drags it back and it rolls back at -0.4859 m/s (0.4859 m/s back) 0.2477 s after the hit and 6.02 cm of slip (closed forms (2/7) R omega = -0.4859 m/s, |R omega| / (7/2 mu g) = 0.2477 s, 6.02 cm; diffs 1.1e-16, 5.6e-17, 2.8e-17); that is 0.28571 of the spin left (2/7 = 0.28571); the other ball leaves at 1.6802 m/s with no spin and rolls at 1.2002 m/s (5/7 of 1.6802 = 1.2002); momentum 1.6802 = 1.6802 and translational energy 1.4116 = 1.4116 per unit mass across the hit
far (the other ball 120 cm ahead, farther than d*): the cue ball rolls into it at 1.0900 s at 0.7143 m/s with R omega = +0.7143 m/s (forward spin, rolling; closed forms 1.0900 s, 0.7143 m/s; diffs 2.2e-16, 1.1e-16); right after the hit the cue ball has 0 m/s and keeps its forward spin; the cloth drags it forward and it follows at +0.2041 m/s 0.1041 s after the hit and 1.06 cm of slip (closed forms (2/7) v = +0.2041 m/s, v / (7/2 mu g) = 0.1041 s, 1.06 cm; diffs 2.8e-17, 5.6e-17, 8.5e-17); the other ball leaves at 0.7143 m/s and rolls at 0.5102 m/s (5/7 = 0.5102); momentum 0.7143 = 0.7143, energy 0.2551 = 0.2551 per unit mass
answer: the same strike, only the other ball's distance differs: at 30 cm the cue ball comes back at 0.4859 m/s, at 120 cm it follows at 0.2041 m/s; the line between is d* = 76.48 cm: any other ball closer than that is hit while backspin is left and the cue ball comes back, any farther and the spin has turned forward and the cue ball follows (at d* itself it stops dead)
sweep (the same strike, the other ball at other distances; the cue ball's final speed, + forward): 10.00 cm: hit at 0.0513 s at 1.8994 m/s, R omega -2.2485, comes back at -0.6424 m/s; 30.00 cm: hit at 0.1630 s at 1.6802 m/s, R omega -1.7006, comes back at -0.4859 m/s; 50.00 cm: hit at 0.2917 s at 1.4278 m/s, R omega -1.0696, comes back at -0.3056 m/s; 70.00 cm: hit at 0.4487 s at 1.1199 m/s, R omega -0.2997, comes back at -0.0856 m/s; 76.48 cm: hit at 0.5099 s at 1.0000 m/s, R omega -0.0000, stops dead at +0.0000 m/s; 80.00 cm: hit at 0.5464 s at 0.9284 m/s, R omega +0.1791, follows at +0.0512 m/s; 90.00 cm: hit at 0.6700 s at 0.7143 m/s, R omega +0.7143, follows at +0.2041 m/s; 120.00 cm: hit at 1.0900 s at 0.7143 m/s, R omega +0.7143, follows at +0.2041 m/s; 150.00 cm: hit at 1.5100 s at 0.7143 m/s, R omega +0.7143, follows at +0.2041 m/s
for the description (the threshold d* moves with the cloth, the tip and the speed; here mu 0.2, tip 0.5 R, 2 m/s: 76.48 cm): mu 0.15: 101.97 cm (closed form 101.97); mu 0.25: 61.18 cm (closed form 61.18); tip 0.3 R low (R omega0 = 1.50 m/s): 52.01 cm (closed form 52.01); tip 0.4 R low (R omega0 = 2.00 m/s): 65.26 cm (closed form 65.26); 1.5 m/s: 43.02 cm (closed form 43.02); 3 m/s: 172.08 cm (closed form 172.08); d* grows as 1 / mu and as v0^2 and with the tip's depth h (2 - h)
stepped check (semi-implicit Euler, the slip snapped to rolling on its closing step; differences from the exact pieces in brackets): dt 1e-05 s: near: hit at 0.163040 s (+7.1e-06), 1.680225 m/s (-1.4e-05), R omega -1.700562 (+3.5e-05), the cue ball ends at -0.485875 m/s (+9.9e-06), far: hit at 1.090040 s (+1.9e-05), 0.714286 m/s (-4.7e-12), R omega +0.714286 (-4.7e-12), the cue ball ends at +0.204082 m/s (-1.4e-12), backspin gone at 0.509860 s (+1.9e-06) after 76.4784 cm (-3.1e-04 cm); dt 1e-06 s: near: hit at 0.163033 s (+9.6e-08), 1.680238 m/s (-1.9e-07), R omega -1.700596 (+4.7e-07), the cue ball ends at -0.485885 m/s (+1.3e-07), far: hit at 1.090023 s (+1.7e-06), 0.714286 m/s (+1.9e-11), R omega +0.714286 (+1.9e-11), the cue ball ends at +0.204082 m/s (+4.8e-12), backspin gone at 0.509859 s (+8.9e-07) after 76.4788 cm (+3.9e-05 cm)
schedule (video time, 1/5 speed): cycles of 10 s start at 0.00, 10.00, 20.00, 30.00, 40.00 s; the strike 1.6 s into each cycle at 1.60, 11.60, 21.60, 31.60 s; near: the hit 0.82 s after the strike at 2.42, 12.42, 22.42, 32.42 s, the cue ball rolls back from 3.65, 13.65, 23.65, 33.65 s, is back over its start at 6.12, 16.12, 26.12, 36.12 s and leaves the panel on the left at 8.69, 18.69, 28.69, 38.69 s (1.4172 s real); far: the backspin is gone at the gold line 2.55 s after the strike at 4.15, 14.15, 24.15, 34.15 s, the ball rolls from 4.88, 14.88, 24.88, 34.88 s, the hit at 7.05, 17.05, 27.05, 37.05 s, the cue ball follows at its final speed from 7.57, 17.57, 27.57, 37.57 s and has crept 8.9 cm past the hit point when the reset starts; the other balls leave the panel on the right 4.90 s (near) and 6.71 s (far) after the strike; the stick (drawn only) waits 4 cm behind the ball, strokes in at 1.5 m/s from 0.13 s before the strike, follows through 3 cm and fades after it; the reset crossfades over the last 0.5 s of each cycle (out 9.50 to 9.75 s, in 9.75 to 10.00 s after the cycle start); the first frame is 0.00 s into a cycle (-0.3200 s real from the strike); title until 3.4 s; payoff card from 28.2 s; the title fades back in over the last 0.5 s and the last frame repeats the first (the scene holds exactly 4 cycles)
text widths: overlay@34 876 px, title line 1@56 305 px, title line 2@56 547 px, title line 3@56 368 px, legend@40 812 px, clock@28 364 px, clock before@28 265 px, label near@40 116 px, sub near@28 348 px, bracket near@28 94 px, label far@40 64 px, sub far@28 342 px, bracket far@28 89 px, state at rest@28 105 px, state backspin@28 140 px, state no spin@28 115 px, state topspin@28 119 px, state rolling@28 102 px, state rolling back@28 186 px, readout before@40 383 px, readout near@40 470 px, readout far@40 367 px, line label@28 310 px, line mark@28 125 px, payoff line 1@40 893 px, payoff line 2@40 780 px, payoff line 3@40 836 px, payoff line 4@40 899 px, payoff line 5@40 524 px, payoff line 6@40 879 px, payoff line 7@40 818 px
row check: the label and state end at x 364 px, the sub line at x 388 px, the readout starts at x 570 px
body labels near: the bracket label spans x 205 to 299 px, the d* mark 680 to 805 px (right of the gold line), gap 381 px
body labels far: the bracket label spans x 514 to 602 px, the d* mark 680 to 805 px (right of the gold line), gap 78 px
frame check: the start at x 150 px, the gold line at x 670 px, the far other ball at x 1005 px (right edge 1024 px of 1080); the stick's tip at the strike at x 133 px
Tue Sep 29 11:08:52 AM EEST 2026
```

Earlier runs: 10:35:36 (media/drawshot/measure-1035.log) stopped on
the width assert (the first card draft had lines of 972 to 1137 px).
The later runs up to 11:03:00 changed only the scale, the start, the
cycle and strike time, the reset fade and the card, so only the
display parts of the setup line, the schedule, the widths and the
frame check changed. Every physics number was identical in every
run.

The brief's checks against the log: R w0 2.5 m/s (2.5000); backspin
gone at 0.5099 s after 76.48 cm at 1.0000 m/s (0.5099, 76.48, 1.0000);
rolling at 0.6555 s after 88.97 cm at 0.7143 m/s (0.6555, 88.97,
0.7143); near hit at 0.1630 s at 1.6802 m/s with 1.7006 m/s of backspin
left (0.1630, 1.6802, -1.7006 with omega counted forward), comes back
at 0.4859 m/s after 6.02 cm (0.4859, 6.02), the other ball rolls at
1.2002 m/s (1.2002); far hit at 1.0900 s at 0.7143 m/s rolling (1.0900,
0.7143, +0.7143), follows at 0.2041 m/s after 1.06 cm (0.2041, 1.06),
the other ball rolls at 0.5102 m/s (0.5102). The distances are the
cue ball's centre travel to contact (centres 35.72 and 125.72 cm
apart); the log says so. No claim changed.

### Production

- Sim: sims/drawshot/drawshot.py with projects/drawshot/manifest.json
  (seed 0, fps 60, ball_radius_m 0.0286, mu 0.2, g 9.80665,
  strike_speed_m_s 2.0, tip_offset_R 0.5, near_object_m 0.3,
  far_object_m 1.2, stepped_dts 1e-5 and 1e-6, sweep 0.1 to 1.5 m,
  description mu 0.15 / 0.25, tips 0.3 / 0.4 R, speeds 1.5 / 3.0 m/s,
  slow 5, cycle_s 10, strike_at 1.6, first_cycle_at 0, reset_fade 0.5,
  scene_duration 40, px_per_m 680, start_x_px 150, stick_speed_m_s 1.5,
  stick_ready_m 0.04, stick_follow_m 0.03, title_until 3.4, payoff_t
  28.2, payoff_hold 0.6, loop_fade 0.5, music_seed 97, music_gain 0.18,
  voice_offset 0.6, caption_y 0.75). Built from sims/cueball (exact
  constant-acceleration pieces between the events, the head-on hit, the
  stripe) and sims/icerod (frame-integer phase). The stepped check is a
  semi-implicit Euler run at dt 1e-5 and 1e-6 s with the slip snapped
  to rolling on its closing step. Frames are drawn from the frame
  number modulo the 600-frame cycle; the new shot is fully in one frame
  before the cycle ends, and the last frame is the live frame 0.
- Layout (1080x1920): overlay at y 96 (34 px teal, drawn by compose);
  title three rows at y 180, 242, 304 (56 px) until 3.4 s, then the
  legend "the same low hit on both, 1/5 speed" at y 236 (40 px) and the
  clock "N.NNN s after the strike" at y 290 (28 px); near panel label
  row at y 430 ("close", 40 px, and the state, 28 px, coloured by the
  spin sign), "other ball 30 cm away" at y 474, the readout right to x
  1040 ("cue ball / comes back / follows N.NN m/s", 40 px, gold once
  settled), cloth line at y 740; far panel the same 500 px lower
  (cloth at y 1240); the geometry layer y 560 to 1340 drawn at 2x and
  reduced; the start at x 150, 680 px per metre (ball radius 19.4 px);
  the gold dashed line at x 670 with "backspin gone here" above it and
  "76.5 cm" right of it in the table body; the distance bracket "30 cm"
  / "1.2 m" in the body; the stick drawn level with its axis half a
  radius below the centre (chalk tip, white ferrule, wood), waiting 4
  cm behind the ball, stroking in and fading after the follow-through;
  the cue ball white with a coral stripe band and a dark dot, the other
  ball gold; a curved spin arrow over the cue ball (coral for backspin,
  teal for forward spin, length set by |R omega|); a gold trail under
  the cue ball after the hit; a flash ring at the contact for 0.35 s;
  captions at y 1440 (64 px); the seven-line gold card from y 1572 at a
  48 px pitch (last row centred at 1860).
- Hook pre-tests (media/drawshot/hooks/pretest.log, 10:25:15 to
  10:25:33 EEST), each through scripts/voiceover.sh, all passed on the
  first pass; question onset = the silence_end after the first phrase
  (n=-35dB d=0.08) plus 0.6 s: hook1 "Hit it low. Does the cue ball
  come back?" 1.70 s; hook2 "Hit low. ..." 1.71 s; hook3 "A low hit.
  ..." 1.61 s; hook4 "Draw shot. ..." 1.52 s; hook5 "Hit it low. Does
  the white ball come back?" 1.49 s. "cue" came back as "cue" in every
  hook. Kept hook1 (see Deviations). payoff1 and body1 also passed.
- Narration: projects/drawshot/narration.txt, 113 words, the question
  at words 4 to 9, identical in the title, the hook and the payoff
  ("So does the cue ball come back? It comes back only if ..."); the
  numbers as words ("two meters a second", "seventy six
  centimeters"); American "meters", "centimeters".
- Voice (media/drawshot/voice-take1..5.log): take 1 at 10:39:32 passed
  (34.876 s) but its timing put the mechanism words about 1.3 s after
  the gold line crossing, so the schedule moved to 1/5 speed on 10 s
  cycles and the narration was re-timed. Take 2 at 10:40:52 failed:
  whisper heard "gold" as "goal" ("At the gold line" became "At the
  line"). Take 3 at 10:42:01 failed: whisper heard the sentence-initial
  "Only" as "especially" ("Only if" became "It comes back only if").
  Take 4 at 10:42:45 passed (34.551 s), but its captions split the
  payoff number ("closer than seventy" / "six centimeters."). Take 5 at
  10:51:06 ("sits closer than", "So does" without the comma) passed:
  "ok: transcript matches narration (33.796644s) ->
  media/drawshot/voice-take5.wav", copied to media/drawshot/voice.wav.
  The voice ends at 34.40 s of video.
- Timing (take 5; scripts/voice-timing.py media/drawshot/voice.wav 0.6
  in media/drawshot/timing.log, and the pauses in
  media/drawshot/silences.log plus 0.6 s): "Hit it low." 0.60 to 1.29;
  "Does the cue ball come back?" 1.46 to 2.78; "The same low hit," 3.05
  to 3.98; "two meters a second." 4.17 to 5.22; "One comes back." 5.38
  to 6.26; "One follows." 6.50 to 7.26; "On top, the other ball is
  close." 7.54 to 9.38; "Below, it is far." 9.80 to 11.07; "Watch the
  backspin arrow." 11.34 to 12.63; "The cloth rubs it away." 12.86 to
  14.09; "At the line, it is gone," 14.28 to 15.75; "and the ball
  rolls forward." 15.91 to 17.21; "Far: the backspin ran out," 17.35
  to 19.14; "so the cue ball follows the other ball." 19.33 to 21.27;
  "Close: the hit stops the cue ball," 21.47 to 23.65; "but the
  backspin is still there, and it drags the ball back." 23.82 to 26.64;
  "So does the cue ball come back?" 26.73 to 28.15; "It comes back only
  if the other ball sits closer than seventy six centimeters." 28.40 to
  32.43; "That is where the backspin runs out." 32.63 to 34.25.
- Schedule against the voice (measure.log schedule line): strikes at
  1.60, 11.60, 21.60, 31.60 s. "Hit it low." ends before the first
  strike; the near hit (2.42) falls in the question; the near cue ball
  is back over its start at 6.12 inside "One comes back." and the far
  hit at 7.05 inside "One follows."; the strike at 11.60 inside "Watch
  the backspin arrow."; the far ball crosses the gold line at 14.15 and
  "At the line" starts at 14.28; it rolls from 14.88 ("and the ball
  rolls forward"); the far hit at 17.05 and the follow from 17.57 under
  "Far: the backspin ran out"; the reset starts at 19.50, so "so the
  cue ball follows" (19.33) starts with the ball still following in
  gold; the strike at 21.60 under "Close:", the near hit at 22.42
  under "the hit stops the cue ball", the ball rolling back from 23.65
  and over its start at 26.12 under "it drags the ball back"; the card
  at 28.2 (lit at 28.8) right after the spoken question; the far ball
  crosses the gold line at 34.15 under "backspin runs out" (32.63 to
  34.25).
- Smoke frames (--frames) viewed before the renders: the stick was only
  about 40 px long at the ready pose at px_per_m 720 / start x 115, so
  the start moved to x 150 at 680 px per metre and the stick waits 4 cm
  behind the ball (about 100 px of stick in frame 0). The eight-line
  card at a 44 px pitch ran to y 1880; it is seven lines at 48 px.
- Footage: render 11:08:52 to 11:09:16 (media/drawshot/render.log):
  loop check 0 px, periodicity check 0 px, loop step 0 px;
  media/drawshot/footage.mp4 2400 frames.
- Compose: scripts/compose.sh drawshot 11:09:16 to 11:09:28
  (media/drawshot/compose.log): music seed 97, 40.00 s; captions 35
  chunks; final.mp4 40.000000 s; preview.mp4 40.066667 s; sheet 8x5 at
  1 fps.
- Text widths (PIL, from measure.log, all under 950 px): overlay 876;
  title 305 / 547 / 368; legend 812; clock 364 / 265; labels 116 / 64;
  sub lines 348 / 342; brackets 94 / 89; states 102 to 186; readouts
  383 / 470 / 367; line label 310; line mark 125; card 893 / 780 / 836
  / 899 / 524 / 879 / 818. Row check: the label and state end at x 364,
  the readout starts at x 570. Body labels: the bracket label and the
  76.5 cm mark are 381 px (near) and 78 px (far) apart. Frame check: the
  far other ball's right edge at x 1024 of 1080.

### Local QA

- Frames extracted from media/drawshot/final.mp4 (never edited) by
  frame number and viewed with the Read tool:
  - frame-0.png (0.000 s): overlay, the three title rows, both cue
    balls at rest with the stick 4 cm behind and its axis below the
    centre, the gold line with "backspin gone here" and "76.5 cm", the
    brackets "30 cm" and "1.2 m", readouts "cue ball 0.00 m/s"; no
    caption, no card.
  - frame-88.png (1.467 s): question onset; title up, caption "Hit it
    low." (changes to "Does the cue ball" at 1.50), stick starting its
    stroke.
  - frame-147.png (2.450 s): the near hit with the flash ring, coral
    backspin arrow on the near cue ball, "comes back 0.01 m/s"; the
    far ball sliding at 1.67 m/s with backspin; caption "Does the cue
    ball".
  - frame-367.png (6.117 s): near cue ball back over its start,
    "rolling back", "comes back 0.49 m/s" in gold; far ball rolling
    at 0.71 m/s; caption "One comes back.".
  - frame-425.png (7.083 s): the far hit, teal arrow, "follows 0.01
    m/s"; caption "One follows.".
  - frame-857.png (14.283 s): the far ball just past the gold line,
    "topspin"; caption "At the line, it is".
  - frame-1164.png (19.400 s): the far cue ball following, "follows
    0.20 m/s" in gold, near "comes back 0.49 m/s" in gold; caption
    "ball follows the".
  - frame-1347.png (22.450 s): the near hit, the cue ball stopped with
    the backspin arrow; caption "the cue ball, but".
  - frame-1560.png (26.000 s): near ball rolling back past its start;
    caption "drags the ball back.".
  - frame-1740.png (29.000 s): card lit (seven gold rows), both
    readouts gold; caption "It comes back only".
  - frame-1900.png (31.667 s): caption "seventy six" with "76.5 cm" on
    the card, on the gold line mark and in the card's answer rows. The
    payoff number is on screen when spoken.
  - frame-2049.png (34.150 s): the far ball on the gold line; caption
    "backspin runs out.".
  - frame-2398.png and frame-2399.png: the title back, both balls at
    rest with the stick ready, the same picture as frame-0.
  - sheet.png (40 thumbnails at 1 fps): the title for the first 3 s,
    then the legend and clock; four shots with the resets at 9.5, 19.5,
    29.5 s; captions readable from 1 to 34 s; the card from 28 s; no
    clipped text, nothing at the frame edge.
- Question: on screen from frame 0 in the title (305 / 547 / 368 px),
  spoken from 1.46 s (first silence_end 0.858 s in the wav plus 0.6).
- Captions: media/drawshot/captions.filter, 35 chunks, 113 words,
  matches projects/drawshot/narration.txt word for word (script check
  True), longest chunk 20 characters; "sits closer than" 30.51 to
  31.41, "seventy six" 31.41 to 32.00, "centimeters." 32.00 to 32.30.
- Bands: over all 2,400 footage frames the maximum deviation from the
  background is 0 in rows 90 to 135 (overlay band) and 0 in rows 1400
  to 1544 (caption band), so the sim draws nothing under the captions
  or the overlay. The last card row reaches y 1880; rows 1880 to 1919
  carry its descenders only.
- Loop: footage last frame equals the first (0 px) and the frame before
  the last equals the last (0 px). In final.mp4 frame 2399 against
  frame 0: 34,398 px over 8 levels, 1,711 over 32, max 86, mean 0.43
  (h264 quantisation, the same order as day 30); frame 2398 against
  2399: 31,287 px over 8, 14 over 32, max 38, mean 0.24.
- ffprobe: h264 1080x1920 yuv420p 60/1, 2400 frames; aac 22050 Hz
  mono; 40.000000 s; 3,338,017 bytes; moov before mdat.
- Loudness (ebur128): I -15.9 LUFS, LRA 6.9 LU, true peak 0.0 dBFS
  (the voice wav itself peaks at 0.1 dBFS; icerod's final 0.1 dBFS).
- md5sum media/drawshot/final.mp4: 1472a478367d3295674b3fe0afbbdd5f
- Narrated numbers against measure.log: "two meters a second" (setup
  line: v0 = 2 m/s; launch line: R omega0 = 2.5000 m/s); "closer than
  seventy six centimeters. That is where the backspin runs out."
  (backspin gone line: 76.48 cm; answer line: d* = 76.48 cm); "the hit
  stops the cue ball" (near and far lines: right after the hit the cue
  ball has 0 m/s); "One comes back. One follows." (near -0.4859, far
  +0.2041 m/s). Card: 76.5 cm (76.48), 0.49 (0.4859), 1.70 (1.7006),
  0.20 (0.2041), 102 / 61 cm (101.97 / 61.18), 52 cm (52.01).
- Metadata check: every number in the description read against
  media/drawshot/measure.log after the final run (2.5000, 87.413, 30 cm,
  1.2 m, 28.6 mm, 0.2, 9.80665, 1/5, 10 s, 4 shots, 0.5099, 76.48,
  1.0000, 0.7143, 0.6555, 88.97, 0.1630, 1.6802, 1.7006, 0.4859,
  0.2477, 6.02, 1.2002, 1.0900, 0.2041, 0.1041, 1.06, 0.5102, the sweep
  -0.6424 / -0.4859 / -0.3056 / -0.0856 / 0.0000 / +0.0512 / +0.2041,
  101.97 / 61.18, 52.01 / 65.26, 43.02 / 172.08, stepped dt 1e-06 at
  most 1.7e-06 s, 4.7e-07 m/s, 3.9e-05 cm).

### Metadata

projects/drawshot/metadata.json: title "Hit it low at 2 m/s: does the
cue ball come back? Only if the other ball is closer than 76.5 cm" (95
characters, no angle brackets); description 3,498 characters with the
model, the "Measured:" list, the "Why:" paragraph, the rerun line and
the AI-made line, no angle brackets; 12 tags; categoryId 27;
privacyStatus private; containsSyntheticMedia true;
selfDeclaredMadeForKids false.

### Deviations from the brief

- Hook: kept hook1 "Hit it low. Does the cue ball come back?" (pre-test
  1.70 s, 1.46 s in the final take), not the earliest pre-test. hook5
  (1.49 s) says "white ball", which the brief keeps for the case that
  "cue" fails (it did not); hook4 (1.52 s) opens with the jargon "Draw
  shot."; hook3 (1.61 s) "A low hit." is weaker than the imperative.
  All are under two seconds.
- Narration wording forced by whisper: "At the line" instead of "At
  the gold line" ("gold" heard as "goal"); "It comes back only if"
  instead of "Only if" ("Only" heard as "especially"). "sits closer
  than" instead of "is closer than" so the captions keep "seventy six"
  in one chunk. The title and the card keep "closer than".
- The narration says "seventy six centimeters"; the title, card and
  line mark say 76.5 cm (76.48 measured).
- The spoken phrase "so the cue ball follows the other ball" (19.33 to
  21.27) runs into the reset: the ball follows in gold until 19.50,
  fades out by 19.75, and the next shot fades in at rest. The narration names what the
  viewer just saw; the far readout keeps "follows 0.20 m/s" on screen
  until the fade.
- The card has seven lines (the question, the answer, 76.5 cm, the 30
  cm and 1.2 m results, mu 0.15 / 0.25 and tip 0.3 R), last row at y
  1860, the same depth as day 30. The 0.4 R tip and the speeds are only
  in the description.
- The stick is drawn only (no cue physics); its stroke is kinematic
  and it fades after a 3 cm follow-through.
- The other balls leave the frame on the right (near 4.90 s, far 6.71
  s after the strike, in video time); no cushion, no fade needed.

## Niche note

[produced 2026-09-29 as "Hit it low at 2 m/s: does the cue ball come
back? Only if the other ball is closer than 76.5 cm"; measured a level
hit half a radius low at 2 m/s (2.5000 m/s backspin, mu 0.2): the
backspin is gone after 76.48 cm at 0.5099 s (1.0000 m/s); the other
ball 30 cm away: hit at 1.6802 m/s with 1.7006 m/s spin left, the cue
ball comes back at 0.4859 m/s (2/7); 1.2 m away: rolls in at 0.7143
m/s and follows at 0.2041 m/s (2/7); at 76.48 cm it stops dead; the
line at mu 0.15 / 0.25 is 101.97 / 61.18 cm, at a 0.3 / 0.4 R tip
52.01 / 65.26 cm, at 1.5 / 3 m/s 43.02 / 172.08 cm; exact pieces within
1.7e-06 s of a stepped integration at dt 1e-06; task 20260929-101917]

## Upload

- orchestrator review (2026-09-29T11:19:52+03:00): task evidence, sheet.png and frames 1164
  (19.40 s) and 1900 (31.67 s) inspected; numbers match measure.log and
  the closed forms in /tmp/day31/check.py (d* = 76.48 cm, (2/7) R w =
  0.4859 m/s back, (2/7) v = 0.2041 m/s forward); approved for upload
- upload attempt 3 of 5 for the quota day that began 2026-09-29T10:00
  EEST, recorded at 2026-09-29T11:19:52+03:00 before starting scripts/yt-upload.py; two
  attempts (swerve MFVd3MiPsUI and uphill rLaOH8SOh4U, both published)
  were on record since the boundary
- uploaded private as G1HkDcfYGNM at 2026-09-29T11:19:58+03:00
  (https://youtu.be/G1HkDcfYGNM); channels.list 1 unit + videos.insert
  1,600 units; media/drawshot/upload.log
- scripts/yt-qa.py drawshot G1HkDcfYGNM --wait --publish in the
  foreground: gate 15 of 15 on the first read (processed, succeeded, hd,
  1080x1920, title, description and tags match, category 27, not made
  for kids, PT41S for the 40.000 s file, private before publish);
  published at 2026-09-29T11:20:23+03:00; re-read privacyStatus=public;
  yt-qa quota 53 units; media/drawshot/publish.log
- attempt 3 of 5 complete: 1,654 units; slot 3 of 3 resolved as
  published

### Quota
- attempt 3 of the hard cap of 5 for the quota day that began
  2026-09-29T10:00 EEST; cost 1,654 units (the channels.list verification
  inside yt-upload.py, the 1,600-unit insert, and the gate run's reads,
  update and re-read as printed by yt-qa.py); day total after three
  attempts 1,655 + 1,655 + 1,654 = 4,964 units plus 5 for the 10:01
  stats refresh and 5 for the 11:21 refresh, 4,974 of 10,000 used,
  5,026 remaining; target of three met
