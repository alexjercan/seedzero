# Produce short: Tautochrone bowl, do they arrive together

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day11

## Goal

Backlog idea "Tautochrone bowl: five balls released from five heights in
a circular bowl versus a cycloid bowl; measure the arrival-time spread and
each ball's period; expect 0.000 s and equal periods on the cycloid
against a spread that grows every swing in the circle; the cycloid panel
is exactly periodic, so the last frame equals the first." Day eleven
slate, first slot. Chosen because the channel's measured winners are
physics motion pieces staged as two panels with the same input (double
pendulum 1,171 views at 86% average view, resonance 874, billiards 807),
and the framing rules in docs/vision.md ask for one plain question in
the first two seconds: "Do they arrive together?" One setup number (five
balls), one payoff number (the spread in the round bowl against zero in
the curved one). The cycloid panel is exactly periodic, so the short is
built as a seamless loop.

## Claim

Do five balls dropped from five heights arrive at the bottom together?
Same drop, no friction, same equation. In the round bowl the top ball has
farther to go and falls behind; the gap grows every crossing, and by
crossing thirty the balls arrive three point two seconds apart. In the
curved bowl (a cycloid) the top ball starts where the wall is nearly
vertical, so it moves faster and the extra speed exactly pays for the
extra distance: zero seconds apart at every one of the forty crossings.
At forty seconds every ball is back on its mark, so the video loops.

## Evidence

### Measurements

`sims/tautochrone/tautochrone.py` with `projects/tautochrone/manifest.json`
(bead on a wire, s'' = -g dy/ds, RK4 at 600 steps per second, g 9.81,
deterministic, no seed; log in `media/tautochrone/measure.log`):

- cycloid parameter a 0.24849 m so the period is exactly 2.000 s (20
  periods in 40 s); round bowl radius = depth = 0.49698 m; round bowl
  0.994 m wide, curved bowl 1.561 m wide, both 0.497 m deep; release
  heights 0.0994, 0.1988, 0.2982, 0.3976, 0.4970 m
- round bowl periods 1.45171, 1.49419, 1.54304, 1.60033, 1.66925 s from
  release angles 36.9, 53.1, 66.4, 78.5, 90.0 deg; each equals the exact
  elliptic-integral period to five decimals; first bottoms 0.3629 to
  0.4173 s (first arrival spread 0.0544 s); 55, 54, 52, 50, 48 crossings
  in 40 s; energy drift under 5e-11
- round bowl spread of the k-th crossing: 1: 0.054 s, 2: 0.163, 3: 0.272,
  5: 0.489, 10: 1.033, 12: 1.251, 20: 2.121, 30: 3.209, 40: 4.297 s;
  largest 5.167 s at crossing 48
- curved bowl: every ball's period 2.00000 s (exact 2.00000); first bottom
  0.5000 s for all five; 40 crossings; spread 0.000 s at every crossing;
  energy drift 6.9e-12
- loop check: at the last frame (39.9833 s) the cycloid balls are within
  1.362 mm of their marks with speed under 163.425 mm/s; at 40 s they are
  at rest on their marks
- payoff at crossing 30: round 3.209 s apart, curved 0.000 s apart

### Production

- `sims/tautochrone/tautochrone.py` renders two panels: the round bowl
  above, the cycloid below, five coloured balls with hollow release marks,
  a bottom marker, a flash ring at each bottom crossing, a per-ball
  crossing timeline for the last four seconds, and a readout "crossing N:
  X s apart" per panel; the question "Do they arrive together?" is drawn
  in the top panel for the first 3 s and again from 38.8 s while the
  round-bowl balls are lifted back to their marks over 1.2 s, so the last
  frame equals the first; payoff at 24.6 s ("crossing 30: round bowl
  3.2 s apart / curved bowl 0.000 s apart") held until 38.4 s
- narration `projects/tautochrone/narration.txt`, 105 words; the round
  trip passed at 36.571 s after rewording whisper mishearings ("bowls" as
  "balls", "high ball" as "highball", "steeper" as "steep er", and a
  110-word draft that ran 39.56 s); captions: "The round one: no." at
  24.18 s, "By crossing thirty" at 25.55 s, "The curved one: yes." at
  28.97 s, last caption ends 37.17 s; music seed 31 at gain 0.18
- compose: 2,400 frames at 60 fps, final.mp4 40.000 s, 1080x1920, h264,
  aac, moov before mdat; mean volume -16.1 dB, peak 0.0 dB
- inspection: contact sheet plus full-resolution frames at 1.0, 26.5 and
  39.95 s from final.mp4; fixed the title colliding with the crossing
  readout, the curved-bowl label colliding with the readout, coincident
  cycloid ticks hiding each other (one row per ball), a faded readout
  punching a hole in the returning title, an overlay line 1,078 px wide
  at the frame edge (shortened to 799 px) and a payoff "3.21 s" that did
  not match the narrated "three point two" (now 3.2 s); the finals show
  the question and both bowls in motion at 1.0 s, the payoff on screen
  while it is spoken, and every ball back on its mark under the title at
  39.95 s

### Published

- clock before upload: 10:00:19 EEST 2026-09-09 = 00:00:19 PDT, the
  fresh Pacific quota day
- uploaded private to the Seed Zero channel (UCWXsZTvrh_OHkzt6v1xkTsw)
  via `scripts/yt-upload.py`: video i0HN7HQdfZ0, publishedAt 10:00:22 EEST
  (log in `media/tautochrone/upload.log`)
- QA gate (scratchpad yt-qa.py, videos.list): 15 of 15 on the first read
  at 10:01 EEST: Seed Zero channel, uploadStatus processed,
  processingStatus succeeded, no rejection, HD, embeddable, 1080x1920,
  title, description, tags, categoryId 27, madeForKids false,
  selfDeclaredMadeForKids false, duration PT41S (40.000 s rounds up),
  private
- published (videos.update privacyStatus public, containsSyntheticMedia
  true) at 10:01:16 EEST; re-read 15 s later: public, madeForKids false,
  selfDeclaredMadeForKids false, embeddable true (log in
  `media/tautochrone/publish.log`)
- public URL: https://youtu.be/i0HN7HQdfZ0

### Quota

- this short: 1,600 (insert) + 1 (channel check) + 1 (gate read) + 52
  (publish and re-read) = 1,654 units; the day 11 slate together about
  4,962 of 10,000, leaving room for one re-upload and analytics reads
