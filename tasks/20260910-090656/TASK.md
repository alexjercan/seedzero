# Produce short: Magnetic pendulum, same drop same magnet

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day12

## Goal

Backlog idea "Magnetic pendulum: two bobs released a tenth of a millimetre
apart over three magnets; measure the time they separate by a bob width
and the final magnet of each; plus a grid of releases counting the share
whose neighbour ends at a different magnet." Day twelve slate, third slot.
Chosen because the channel's best retainer is the double pendulum (two
runs a hair apart, 86% average view) and this is the same format with a
visible finish: each bob stops over a magnet. Question in the first two
seconds: "Same drop, same magnet?" One setup number (a tenth of a
millimetre), one payoff number (the time the two bobs part). Every number
below is printed by the sim before the script is written.

## Claim

Two identical pendulums released from rest a tenth of a millimetre apart
above three magnets split within about a second and end over different
magnets. The gap is a thousand times the release gap after about three
seconds.

## Evidence

Deterministic model (no seed): string 1 m, drag 0.3 per second, three
magnets 6 cm from the centre at 90, 210 and 330 deg, bob 3 cm above the
magnet plane, magnet strength 0.006 m^3/s^2 (pull straight above a magnet
0.68 g), bob 10 mm across, RK4 at 1200 steps per second for the pair.
Release point chosen by rule, not by hand: the nearest 1 mm grid point to
the reference (0, 8 cm) whose 0.1 mm neighbour ends at a different magnet,
confirmed by the fine run (candidate 1 accepted). Log:
media/magpendulum/measure.log.

### Measurements

- Basin map, 200 x 200 release points 1 mm apart over a 20 cm square,
  50 s each: red 13772, blue 13114, purple 13114 end points; 41.7% of
  points end at a different magnet from their neighbour 1 mm to the right;
  26.9% differ from a neighbour 0.1 mm to the right.
- Release (-0.05, 7.95) cm and 0.1 mm to the right of it, both from rest.
- Gap passes 1 mm at 0.67 s, 10 mm (one bob width, the split) at 1.071 s,
  100 mm (a thousand times the release gap) at 3.29 s. Gap in the first
  second: 0.100, 0.091, 0.211, 0.684, 2.621, 6.726 mm at 0.0, 0.2, 0.4,
  0.6, 0.8, 1.0 s (the gap dips to 0.04 mm while both bobs converge on
  the red magnet, then grows). Gap at 1, 2, 3, 5 s: 6.7, 17.4, 19.0,
  114.2 mm; largest 12.5 cm at 3.4 s.
- White bob ends over the purple magnet, settled (within 5 mm, under
  5 mm/s) at 7.85 s. Gold bob ends over the red magnet, settled at 7.96 s.
- Check at 2400 steps per second: split 1.071 s, purple and red (same).
- Check released 1 mm apart: split 0.658 s, purple and blue. Released
  10 mm apart: split 0.216 s, purple and blue.
- Video: two drops of 22 s at half speed, released 5 s into each drop;
  on screen the split comes 2.1 s after release and both bobs are settled
  15.9 s after release.

Narration numbers: setup one tenth of a millimeter (US spelling so the
whisper round trip matches); payoff a thousand
times wider in three seconds, different magnets (purple and red).

### Production

- `sims/magpendulum/magpendulum.py` renders the table from above (three
  named magnets, the release cross, both bobs with fading trails and a
  settled ring), a header label with the physics clock, and a log-scale
  gap strip below the captions (0.1 mm to 10 cm with a "one ball width"
  tick and "split at 1.1 s" once the gap passes it); two drops of 22 s at
  half speed, released 5 s into each drop, with the bobs gliding back to
  the release cross in a 0.8 s reset; the question "Two drops, a hair
  apart. Same magnet?" is drawn for the first 2.4 s and again in the last
  reset, the header hidden while the title shows, so the last frame equals
  the first (mean pixel difference 0.010); payoff from 20.9 s ("same
  magnet? no: purple and red / released a tenth of a millimeter apart")
  held to the final reset
- narration `projects/magpendulum/narration.txt`, 118 words; round trip
  passed at 38.417 s (log `media/magpendulum/voice.log`) after rewording
  whisper mishearings ("millimetre" as "millimeter", "balls" as "bowls",
  "paths" as "pads"); captions: "Then they split" 7.44 to 8.41 s (split on
  screen at 7.14 s), "thousand times wider" ends 14.27 s (100 mm on
  screen at 11.6 s), "settles over the purple magnet" at 20.9 s with the
  payoff, "Together at first" 25.99 to 26.97 s (second release 27.0 s),
  the mechanism sentence 26.97 to 31.85 s spans the second split at
  29.14 s; music seed 36 at gain 0.18
- compose: 2,640 frames at 60 fps, final.mp4 44.000 s, 1080x1920, h264,
  aac, faststart; mean volume -15.4 dB, peak 0.0 dB
- text widths measured before rendering: overlay 858 px, title 755 and
  467 px, payoff 762 and 852 px (a 1,052 px draft was shortened), header
  label 632 px
- inspection: two contact sheets plus full-resolution frames at 1.0,
  2.3, 7.5, 8.0, 21.0, 27.2, 27.3, 43.6, 43.9 and 43.98 s; fixed the
  title overlapping the compose overlay (title moved to y 168..226, table
  to y 260..1200, captions to 0.655), the header ghosting through the
  loop crossfade (header hidden while the title shows), dark trail
  scribbles over the magnets at reset (trails under the magnets, skipped
  at the end of the reset), magnet names hidden by the bobs, the header
  colliding with the clock, and a gap readout of "0.0 mm" at 0.2 s (now
  two decimals under 1 mm: 0.04 mm); the finals show the question and
  both bobs on the release cross at 1.0 s, the split and the gold
  "split at 1.1 s" mark at 7.5 s, the settled rings and the payoff at
  21.0 s, the second drop starting under the held payoff, and the bobs
  back on the cross under the title at 43.98 s

### Published

- clock before upload: 10:00:11 EEST 2026-09-10 = 00:00:11 PDT, the
  fresh Pacific quota day
- uploaded private to the Seed Zero channel (UCWXsZTvrh_OHkzt6v1xkTsw)
  via `scripts/yt-upload.py`: video Y-rfFZyeAc0, publishedAt 10:00:32 EEST
  (log in `media/magpendulum/upload.log`)
- QA gate (scratchpad yt-qa.py, videos.list): 15 of 15 on the first read
  at 10:01:06 EEST: Seed Zero channel, uploadStatus processed,
  processingStatus succeeded, no rejection, HD, embeddable, 1080x1920,
  title, description, tags, categoryId 27, madeForKids false,
  selfDeclaredMadeForKids false, duration PT45S (44.000 s rounds up),
  private
- published (videos.update privacyStatus public, containsSyntheticMedia
  true) at 10:01:40 EEST after a second clean gate read; re-read 15 s
  later: public, madeForKids false, selfDeclaredMadeForKids false,
  embeddable true (log in `media/magpendulum/publish.log`)
- public URL: https://youtu.be/Y-rfFZyeAc0

### Quota

- this short: 1,600 (insert) + 1 (channel check) + 1 (gate read) + 52
  (publish and re-read) = 1,654 units; the day 12 slate together 4,967
  units by the successful requests (plus 2 for the page refresh), at most
  6,568 of 10,000 if the rejected Kapitza insert counted; four insert
  attempts today against the hard cap of five
