# Produce short: Rolling race, which shape rolls down first

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day19

## Goal

Backlog idea (trend research 2026-09-16, task 20260916-100924):
"Rolling race: a solid ball, a solid cylinder, a hollow ball and a hoop
of the same size and mass released together on the same 2 m ramp at
20 degrees; measure the arrival times; expect 1.292, 1.337, 1.410 and
1.544 s (t = sqrt(2L(1+k)/(g sin theta)) with k = 2/5, 1/2, 2/3, 1;
the hoop 19.5 percent behind the ball) and the same order at any mass
or size; the race repeats so the short loops; deterministic, no seed."
Day nineteen, first slot. Chosen because it is continuous motion, a
same-input comparison (four shapes, same mass, same size, same ramp),
repeats so the short loops, with one plain question, one setup number
(the ramp) and one payoff number (the gap at the finish) that a closed
form checks.
Question in the first two seconds: "Which one rolls down first?"

## Claim

Four objects of the same mass and the same size roll down the same
ramp. The solid ball wins and the hoop comes last, whatever the mass
or the size. Every number below is printed by the sim before the
script is written.

## Evidence

### Measurements

(recorded after the measure-only run, before scripting)

`sims/rollrace/rollrace.py --measure-only` with
`projects/rollrace/manifest.json` (a ramp 2 m long at 20 degrees,
g = 9.80665, g sin theta = 3.3541 m/s^2, friction coefficient 0.5; four
bodies of mass 1 kg and radius 20 cm released from rest at the top and
rolling without slipping, each with I = k m r^2 and a = m g sin theta /
(m + I / r^2): solid ball k = 2/5, solid cylinder k = 1/2, hollow ball
k = 2/3, hoop k = 1; RK4 on [s, v] at 1000 steps per second, the
arrival interpolated inside the crossing step; deterministic, no seed;
log in `media/rollrace/measure.log`):

- solid ball: accelerates at 2.3958 m/s^2, arrives at 1.2921 s (closed
  form sqrt(2 L (1 + k) / (g sin theta)) = 1.2921 s), 3.0957 m/s at the
  bottom, needs mu >= 0.1040 to roll without slipping
- solid cylinder: 2.2360 m/s^2, arrives at 1.3375 s (closed form
  1.3375 s), 2.9907 m/s, needs mu >= 0.1213
- hollow ball: 2.0124 m/s^2, arrives at 1.4098 s (closed form 1.4098 s),
  2.8372 m/s, needs mu >= 0.1456
- hoop: 1.6770 m/s^2, arrives at 1.5444 s (closed form 1.5444 s),
  2.5900 m/s, needs mu >= 0.1820
- finishing order: solid ball 1.2921 s, solid cylinder 1.3375 s, hollow
  ball 1.4098 s, hoop 1.5444 s
- gap: the hoop arrives 0.2523 s after the solid ball, 19.5% behind
  (closed-form ratio sqrt(2 / 1.4) = 1.1952); at the finish the solid
  ball moves at 3.096 m/s and the hoop at 2.590 m/s; when the ball
  finishes the hoop is still 0.600 m from the line
- check: with 10x the mass (10 kg) and 2x the radius (40 cm) the
  arrival times are identical, 1.2921, 1.3375, 1.4098 and 1.5444 s;
  the mass and the radius cancel
- friction: rolling without slipping needs mu >= k / (1 + k) tan
  theta, at most 0.1820 (the hoop), so the ramp's friction 0.5 keeps
  all four rolling
- check: at half the time step the arrivals are the same 1.2921,
  1.3375, 1.4098 and 1.5444 s
- for the description only: a frictionless block sliding the same ramp
  (no spin, k = 0) arrives at 1.0921 s (closed form 1.0921 s) at
  3.663 m/s
- video: played at 1/4 speed; the solid ball finishes 5.17 s into each
  race and the hoop 6.18 s in; all four clocks frozen from 6.18 s to
  7.50 s of each 8 s race, reset over the last 0.5 s; 5 races in
  40 s, so the video loops on the race

Narration numbers: the two meter ramp (setup), the solid ball at one
point two nine seconds (payoff) with the hoop at one point five four
seconds as the contrast. The 20 degrees stays on screen only. The
accelerations, speeds, friction, the 19.5 percent, the 10x mass and
2x radius check and the sliding block go to the description.

### Production

- footage: `sims/rollrace/rollrace.py` (no arguments) wrote
  `media/rollrace/footage.mp4`, 40.00 s at 60 fps, 2,400 frames (five
  8 s races at 1/4 speed, so the video loops on the race); the same
  run re-printed every measurement above (log in
  `media/rollrace/render.log`); text widths at most 872 px (the
  overlay) so nothing clips at 1080 px; loop check: the last frame
  differs from the first in 0 px; smoke frames at 0, 1.5, 3, 6, 8, 12,
  20, 29.5, 31.3, 31.8, 39.6 and 39.9 s inspected first
- voice: `scripts/voiceover.sh projects/rollrace/narration.txt` passed
  the round trip on the first try (110 words, 33.56 s, ends at 34.16 s
  of the 40 s video, 3.3 words/s); timing (`scripts/voice-timing.py`,
  +0.6 s offset): the four shapes are named 6.31 to 12.10 s over race 1
  (the ball finishes at 5.17 s, the hoop at 6.18 s of each race, clocks
  frozen with the ranks to 7.10 s), "The solid ball leads at once"
  inside 8.59 to 12.10 s as race 2 starts at 8 s, "and the hoop drops
  behind" 12.10 to 13.68 s as the ball finishes race 2 at 13.17 s,
  "So which one rolls down first?" 26.01 to 28.03 s during race 4,
  "The solid ball at 1.29 seconds" 28.03 to 30.91 s with the payoff
  card from 28.0 s and the ball's finish at 29.17 s, "The hoop comes
  last, at 1.54 seconds" 30.91 to 34.16 s with the hoop's finish at
  30.18 s; log in `media/rollrace/voice.log`
- compose: `scripts/compose.sh rollrace` wrote `media/rollrace/final.mp4`
  (h264 1080x1920 60 fps, aac, 40.000 s; music seed 56 at gain 0.18;
  captions at caption_y 0.75); loudness mean -16.7 dB, peak -0.0 dB;
  preview and 8x5 contact sheet written (`media/rollrace/compose.log`)
- local QA: frames at 0.02, 1.5, 5.2, 6.3, 8.5, 12, 20, 26.5, 29.2,
  30.5, 33 and 39.75 s were extracted from final.mp4 by the producing
  session at 10:18 EEST; that session stopped before reviewing them;
  the resumed session inspected the contact sheet and the frames at
  0.02, 6.3, 29.2, 30.5 and 39.75 s at 15:35 EEST: question on screen
  to 2.4 s with the four shapes at the line and the clocks at 0.01 s,
  four lanes with the running clocks above, the finish times with
  ranks (1.29 s 1st, 1.34 s 2nd, 1.41 s 3rd, 1.54 s 4th) frozen after
  each race, the ball at the line with "1.29 s 1st" while the others
  still roll at 29.2 s, the payoff card "the solid ball: 1.29 s / the
  hoop last: 1.54 s" under the captions from 28 s, the last frame
  crossfading to the title; no clipped text, captions match the
  narration; approved
- metadata: `projects/rollrace/metadata.json` (written in the resumed
  session), title 100 characters, description with the four arrival
  times against the closed form, the accelerations and speeds, the
  19.5 percent gap, the 10x mass and 2x radius check, the half-step
  check, the friction bound and the sliding block; 10 tags; category
  27; private; containsSyntheticMedia true

### Published

- quota check before the insert: clock 2026-09-17T15:40:39+03:00 EEST; zero upload
  attempts recorded since the 10:00 EEST boundary (log entries and
  media/*/upload.log both checked); this is insert attempt 1 of the
  hard cap of 5
- attempt 1 recorded at 2026-09-17T15:40:39+03:00, video name rollrace, before running
  `scripts/yt-upload.py rollrace`
- upload: `scripts/yt-upload.py rollrace` ran 15:40:39 to 15:40:45 EEST,
  token verified to see only the Seed Zero channel, video id
  Ahe_3vRDMXA, private (`media/rollrace/upload.log`)
- gate: `scripts/yt-qa.py rollrace Ahe_3vRDMXA --wait --publish` in the
  foreground from 15:40:54 EEST; processing had already succeeded at the
  first poll; 15 of 15 pass (processed, succeeded, hd, 1080x1920, title,
  description, tags, category 27, not for kids, PT41S for the 40.000 s
  file, private); containsSyntheticMedia reads absent as on every
  earlier upload (`media/rollrace/publish.log`)
- publish: the same run set the video public at 2026-09-17T15:41:17+03:00;
  the re-read after 15 s shows privacyStatus public, madeForKids false,
  embeddable true; public at https://youtu.be/Ahe_3vRDMXA

### Quota

- attempt 1 of the hard cap of 5 for the quota day that began
  2026-09-17T10:00 EEST; cost 1 + 1,600 + 2 + 50 + 1 = 1,654 units;
  day total after one attempt 1,654 units
