# Produce short: Lorenz forecast horizon, know the start 1,000x better

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day13

## Goal

Backlog idea "Lorenz forecast horizon: nudge the Lorenz system by 1e-3,
1e-6 and 1e-9; measure the time to disagree by one unit; expect about
7.6, 15.3 and 22.9, so every thousandfold gain in precision buys the
same 7.6." Day thirteen, second slot, produced on the foreground
guidance that the day must reach three published shorts. Chosen from
the slate evidence at 10:15: the channel's top shorts are continuous
motion physics and "nudge it and watch them disagree" chaos (double
pendulum 1,160 views, A-star flood 978, tautochrone 943, Dzhanibekov
937, resonance 872, stadium billiards 776), while grid automata (glider
gun 131, percolation 107), counters (under 111), agent lanes (traffic
21, ants 163) and maths drawings (pi race 211, Benford 94, golden angle
2) sit far below. Langton's ant and the Fourier square from the proposed
slate are therefore held back for this idea and the Kelvin wake. One
plain question inside two seconds: "Know the start 1,000x better. How
much longer can you predict?" One setup number (a thousand times), one
payoff number (the same 7.6 seconds each time). Every number below is
printed by the sim before the script is written.

## Claim

Start the same chaotic model three times, each start a thousand times
closer to the true one than the last. How much longer can you predict?
Each thousandfold gain in precision buys the same extra time, about
seven point six seconds, not a thousand times more. The three copies
split from the true path at about 7.6, 15.3 and 22.9 seconds.

## Evidence

### Measurements

(recorded after the measure-only run, before scripting)

`sims/lorenz/lorenz.py` with `projects/lorenz/manifest.json` (Lorenz
system sigma 10, rho 28, beta 8/3, RK4 at 2,400 steps per time unit,
one time unit played as one second, deterministic, no seed; log in
`media/lorenz/measure.log`):

- ensemble: 200 starts spaced 0.37 s along the attractor after a 30 s
  transient from (1, 1, 1), each with three copies whose x is moved by
  1e-3, 1e-6 and 1e-9; a copy "splits" when its distance from its
  reference first reaches 1.0; the 1e-3 copy splits at 6.769 s on
  average (sd 1.909, min 0.766, max 14.117), the 1e-6 copy at 14.354 s
  (sd 1.929, 8.887 to 21.788), the 1e-9 copy at 22.153 s (sd 1.828,
  17.813 to 28.730)
- ensemble gaps: 7.585 s (sd 1.963) and 7.799 s (sd 1.810); mean gap
  7.692 s, so a thousandfold in precision buys 7.7 s on average;
  implied growth rate 0.8981 per unit time (Lorenz's largest Lyapunov
  exponent is about 0.9056); both gaps within 1 s of the mean in 75 of
  200 starts
- start for the video: the sim picks the candidate whose three split
  times are closest to the ensemble averages (sum of squares), a
  printed rule rather than a hand pick: candidate 125 (transient 76.25
  s), (13.611006, 16.317673, 30.798821)
- video runs from that start: 1 thousandth off splits at 6.7205 s
  (distance 0.01 at 1.449 s, 0.1 at 3.046 s, 10 at 6.971 s, largest
  50.37 in 40 s); 1 millionth off splits at 14.2193 s (0.01 at 6.965,
  0.1 at 11.201, 10 at 14.467; largest 49.16); 1 billionth off splits
  at 21.8184 s (0.01 at 14.475, 0.1 at 18.118, 10 at 24.127; largest
  44.55)
- gaps in the video: 7.4988 s and 7.5991 s (mean 7.5490); implied
  growth rate 0.9151 per unit time
- check, the same start at 4,800 steps per unit: splits 6.7205, 14.2193,
  21.8181 s (unchanged to 0.0003 s)
- check, the same nudges along y instead of x: 5.2811, 12.8252, 21.1132
  s (gaps 7.54 and 8.29); along z: 6.7849, 14.2823, 22.5766 s (gaps 7.50
  and 8.29); the direction moves single split times by up to 1.4 s, the
  law stays
- payoff: each thousandfold bought 7.5 s, then 7.6 s; narrated as "the
  same seven and a half seconds each time"; the ensemble average 7.7 s
  and its spread go to the description

Narration numbers: a thousand times better (setup), six point seven,
fourteen point two, twenty one point eight (the on-screen stopwatches),
seven and a half seconds each time (payoff).

### Production

- `sims/lorenz/lorenz.py` renders one big x-z view of the attractor (26
  px per unit, a faint 60 s backdrop path for the butterfly shape) with
  the reference run as a white dot and trail and the three copies as
  concentric rings (gold 1e-3, teal 1e-6, coral 1e-9) with their own
  trails, so the stack visibly holds together and peels apart ring by
  ring; a 6.9 s pre-roll of the reference path leads exactly into the
  start so the copies are in motion at frame 0 and a "start" marker
  shows where they begin; three rows with a stopwatch each that counts
  model time and freezes in colour at the split; the question "Know the
  start 1,000x better. How much longer can you predict?" for the first
  2.4 s and the payoff "how much longer? 7.5 s, each time / 6.7 s, then
  14.2 s, then 21.8 s" in the same place from 29.9 s; the last 0.6 s
  crossfade to frame 0 so the video loops
- narration `projects/lorenz/narration.txt`, 114 words; round trip
  passed at 35.364 s (log `media/lorenz/voice.log`) after rewording:
  "Three copies" at a sentence start (heard "free") became "All three
  copies", "seven and a half" (written back as 7.5) became "seven point
  five", "a millionth" (heard "million th") became "one part in a
  thousand, one in a million, and one in a billion", "bought" (heard
  "what") became "gave"; two connecting lines were added so each
  stopwatch freezes while its number is spoken; hooks considered: "Know
  the start 1,000x better. How much longer can you predict?" (kept),
  "Three copies of one storm. Which one splits first?" (spoils the
  order, no number), "Can a perfect start beat chaos?" (no plain
  answer on screen)
- caption schedule (chunks with the 0.6 s offset, voice 35.36 s):
  "splits away at six / point seven seconds" 12.70 to 14.87 s against
  the gold split at 13.6 s of video; "fourteen point two" 20.14 to 21.07
  against the teal split at 21.1; "twenty one point / eight" 27.59 to
  28.83 against the coral split at 28.7; payoff on screen from 29.9 s
  while "Each thousand times better gave the same seven point five
  seconds" runs 28.83 to 32.24; voice ends 35.96 s; music seed 41 at
  gain 0.18
- compose: 2,400 frames at 60 fps, final.mp4 40.000 s, 1080x1920, h264,
  aac, faststart; mean volume -16.7 dB, peak -0.0 dB
- text widths measured before rendering: overlay 602 px, title lines
  799 and 936 px, rows 668 to 712 px, payoff lines under 700 px after
  shortening a 992 px first draft
- inspection: smoke frames at ten times (layout, ring stacking, the
  stopwatch freeze, the payoff), then the contact sheet plus
  full-resolution frames from final.mp4 at 0.5, 2.8, 7.2, 13.7, 21.2,
  28.8, 30.5, 36.0 and 39.95 s; the finals show the question with the
  rings already moving at 0.5 s, the "start" marker as the stopwatches
  begin, the gold ring alone off the white path with "6.7 s" frozen
  under the caption "splits away at six" at 13.7 s, teal at 21.2, coral
  at 28.8, the payoff over the attractor at 30.5 s, and the captions
  sitting under the rows without overlap; loop crossfade over the last
  0.6 s

### Published

- quota day: the Pacific day 2026-09-11 (reset verified at 10:00:22 EEST
  before the first upload of the day); this is the day's second insert
- uploaded private to the Seed Zero channel (UCWXsZTvrh_OHkzt6v1xkTsw)
  via `scripts/yt-upload.py` between 10:39:52 and 10:39:57 EEST: video
  td7bbyUL77s, publishedAt 2026-09-11T07:39:53Z = 10:39:53 EEST (log in
  `media/lorenz/upload.log`)
- QA gate (`scripts/yt-qa.py`, videos.list): 15 of 15 on the first read
  at 10:40:37 EEST: Seed Zero channel, uploadStatus processed,
  processingStatus succeeded, no rejection, HD, embeddable, 1080x1920,
  title, description, the ten tags as a set, categoryId 27,
  madeForKids false, selfDeclaredMadeForKids false, duration PT41S
  (40.000 s rounds up), private
- published (videos.update privacyStatus public, containsSyntheticMedia
  true, embeddable true) at 10:41:13 EEST after a second clean 15 of 15
  read in the same run; re-read 15 s later: public, madeForKids false,
  selfDeclaredMadeForKids false, embeddable true (log in
  `media/lorenz/publish.log`)
- public URL: https://youtu.be/td7bbyUL77s

### Quota

- this short: 1,600 (insert) + 1 (channel check) + 2 (gate reads) + 50
  (publish) + 1 (re-read) = 1,654 units; the day so far 1,655 + 1,654 =
  3,309 of 10,000 with two insert attempts against the hard cap of
  five, leaving room for the third short plus one re-upload and
  analytics reads
