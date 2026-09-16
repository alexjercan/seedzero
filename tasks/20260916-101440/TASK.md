# Produce short: Quantum tunnelling, can a ball go through a wall

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day18

## Goal

Backlog idea (trend research 2026-09-13, task 20260913-212839): "Quantum
tunnelling: a wave packet with 80 percent of the energy needed to top a
wall beside a classical ball with the same energy; measure the share of
the packet that comes out on the far side; expect a few percent (set the
wall so it lands near 3 percent) against 0 for the ball, and halving the
wall width to multiply the share by about ten; split-step Fourier, no
seed (peg: Schrodinger equation centenary 2026, Nobel physics
2026-10-06)." Day eighteen, second slot. Chosen because it is a
two-panel same-input comparison of continuous motion (a ball and a wave
sent at the same wall with the same energy), a plain question, one setup
number (eighty percent of the energy) and one payoff number (the share
that comes out on the far side). Question in the first two seconds:
"Can a ball go through a wall?"

## Claim

A ball with eighty percent of the energy needed to top a wall bounces
back every time. A quantum wave packet with the same energy sends a
measured few percent of itself through the wall to the far side. Every
number below is printed by the sim before the script is written.

## Evidence

### Measurements

(recorded after the measure-only run, before scripting)

`sims/tunnel/tunnel.py` with `projects/tunnel/manifest.json` (natural
units hbar = m = 1; a Gaussian wave packet with k0 = 1, width sigma =
20, starting at x = -80, kinetic energy k0^2 / 2 = 0.5 against a
rectangular wall of height V0 = 0.625, so the energy is 80% of the wall,
width a = 4.44 (kappa = 0.5, kappa a = 2.220); split-step Fourier with
Strang splitting on a cell-centred grid of 32,768 points over 808.28
whose cells tile the wall exactly (180 cells, dx = 0.02467), dt =
0.01042, 2,400 frames of 8 steps to t = 200; the classical ball has the
same energy, speed 1, radius 8 (drawn larger after the smoke frames; the
radius only sets where its edge meets the wall) and bounces off the near
face;
deterministic, no seed; log in `media/tunnel/measure.log`):

- closed form for a single-energy plane wave at E = 0.8 V0, T = 1 / (1
  + V0^2 sinh^2(kappa a) / (4 E (V0 - E))): 3.000% through this wall,
  25.92% through half the wall, 0.0356% through twice the wall
- the packet's mean energy is 0.50033 = 80.05% of the wall; the share
  of its momentum components with enough energy to top the wall
  classically is 1.75e-6
- at t = 200 the packet is 96.823% reflected, 1.94e-4% inside the wall
  and 3.177% past the wall; norm 1.0000000000; the transmitted share
  passes half its final value at 16.22 s of video and 99% of it at
  25.50 s; the ball's edge hits the wall at t = 69.78 (13.96 s of
  video; 14.46 s in the first run with radius 5.5) and never passes
- checks: 3.161% past the wall at half the time step, 3.176% on twice
  the grid (65,536 points); 26.02% through half the wall (8.2x), and
  0.0734% through twice the wall (43x less)
- convergence ladder before the grid was chosen (same dt): 3.468% on
  8,192 points (dx 0.0987), 3.181% on 16,384, 3.177% on 32,768, 3.176%
  on 65,536; a first 8,192-point run with the wall edges not aligned to
  cells gave 3.359% against 3.222% on twice the grid, which is why the
  grid is cell-centred with the wall an exact number of cells
- the packet's share (3.18%) sits above the single-energy 3.000%
  because the packet carries a spread of energies and the transmission
  grows faster than linearly with energy

Narration numbers: eighty percent of the energy (setup), three point
two percent (payoff, the digit the checks agree on). The plane-wave
closed form, the half-wall and double-wall runs go to the description.

### Production

- footage: `sims/tunnel/tunnel.py` (no arguments) wrote
  `media/tunnel/footage.mp4`, 40.00 s at 60 fps, 2,400 frames; the
  same run re-printed every measurement above (log in
  `media/tunnel/render.log`); text widths at most 867 px (payoff line
  3) so nothing clips at 1080 px; smoke frames at 0, 1.5, 8, 14.4,
  16.2, 19, 25.5, 31 and 39.9 s inspected first (density spikes
  overshot the wave panel and the transmitted 3% bump was invisible,
  so the wave panel draws the amplitude |psi| scaled to 190 px and the
  readout counts probability)
- voice: `scripts/voiceover.sh projects/tunnel/narration.txt` passed
  the round trip on the first try (110 words, 31.22 s, ends at 31.82 s
  of the 40 s video, 3.5 words/s); "Same speed, same start." was added
  so "It hits" (12.71 to 14.45 s) lands on the bounce at 13.96 s, and
  the payoff card comes at 29.0 s as "Not the ball, but three point
  two percent" is spoken (24.70 to 31.82 s); log in
  `media/tunnel/voice.log`
- compose: `scripts/compose.sh tunnel` wrote `media/tunnel/final.mp4`
  (h264 1080x1920 60 fps, aac, 40.000 s; music seed 54 at gain 0.18;
  captions at caption_y 0.75); loudness mean -16.9 dB, peak -0.0 dB;
  preview and 8x5 contact sheet written
- local QA: frames at 0.02, 1.5, 6, 12, 14.5, 16, 20, 25.5, 29.5, 33
  and 39.95 s extracted from final.mp4 and inspected: title on
  screen to 2.4 s, the wave reaches the wall and the readout climbs
  (0.5% at 12 s, 1.1% at 14.5 s, 2.6% at 20 s, 3.1% at 25.5 s, 3.2%
  from 29.5 s), the ball is ringed as it hits at 14.5 s and is on its
  way back at 16 s, interference fringes during the reflection, the
  payoff card "the wave: 3.2% comes out the far side" under the
  captions from 29 s, the last frame crossfades to the title; no
  clipped text, captions match the narration
- metadata: `projects/tunnel/metadata.json`, title 100 characters,
  description with the plane-wave closed form, the half-wall and
  double-wall runs, the checks, the amplitude-versus-probability note
  and the Schrodinger centenary; 10 tags; category 27; private;
  containsSyntheticMedia true

### Published

- quota check before the insert: clock 2026-09-16T10:42:33+03:00 EEST; one upload attempt
  (rainbow, 10:25:57, published) recorded since the 10:00 EEST
  boundary; this is insert attempt 2 of the hard cap of 5
- attempt 2 recorded at 2026-09-16T10:42:33+03:00, video name tunnel, before running
  `scripts/yt-upload.py tunnel`
- upload: `scripts/yt-upload.py tunnel` ran 10:42:33 to 10:42:38 EEST,
  token verified to see only the Seed Zero channel, video id
  4hGRhL65ZTo, private (`media/tunnel/upload.log`)
- note: the session that ran the upload stopped before reading the gate;
  a new session took over at 10:53 EEST, re-read the task evidence, the
  contact sheet and the quota records (attempts 1 to 3 on record) and
  continued the release flow
- gate: `scripts/yt-qa.py tunnel 4hGRhL65ZTo` at 2026-09-16T10:53:23+03:00,
  15 of 15 pass (processed, succeeded, hd, 1080x1920, title, description,
  tags, category 27, not for kids, PT40S for the 40.000 s file, private);
  containsSyntheticMedia reads absent as on every earlier upload
  (`media/tunnel/qa.log`)
- publish: `scripts/yt-qa.py tunnel 4hGRhL65ZTo --publish` at 10:54:01 EEST
  re-ran the gate (15 of 15) and set the video public at
  2026-09-16T10:54:04+03:00; the re-read after 15 s (10:54:19) shows
  privacyStatus public, madeForKids false, embeddable true; public at
  https://youtu.be/4hGRhL65ZTo

### Quota

- attempt 2 of the hard cap of 5 for the quota day that began
  2026-09-16T10:00 EEST; cost 1 + 1,600 + 1 + 52 = 1,654 units;
  day total after two attempts 3,308 units

### Repository

- committed as ddff1b0 "Publish the day eighteen slate" (sims, projects,
  tasks, docs/niche.md, web/data; no media, previews or secrets) and pushed
  to origin/master at 2026-09-16 10:59 EEST
