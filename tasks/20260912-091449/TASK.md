# Produce short: Plane boarding, what is the fastest way to board a plane

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day14

## Goal

Backlog idea "Plane boarding: the same 150 passengers, seats and bag
times; back-to-front versus random versus Steffen; measure boarding
time; expect Steffen about twice as fast as back-to-front and
back-to-front the slowest of the three." Day fourteen, first slot.
Chosen from the seven unproduced ideas because it is a three-lane
same-input race with continuous visible motion (passengers walking an
aisle and sitting), the channel's measured winner format (brachistochrone
949 views, tautochrone 945, Dzhanibekov 939), and its surprise is one
number in and one number out. Question in the first two seconds: "What
is the fastest way to board a plane?" One setup number (150 passengers),
one payoff number (the boarding time of the fastest order against the
slowest). Every number below is printed by the sim before the script is
written.

## Claim

What is the fastest way to board a plane? The same one hundred fifty
passengers, the same seats, the same bag times, three boarding orders.
Back to front is the slowest. Boarding window seats first, back to
front, every other row, takes about half the time.

## Evidence

### Measurements

(recorded after the measure-only run, before scripting)

`sims/boarding/boarding.py` with `projects/boarding/manifest.json`
(time-stepped single-aisle model, 0.1 s steps with integer step timers,
seed 0; log in `media/boarding/measure.log`):

- plane: 25 rows of six (A and F window, B and E middle, C and D
  aisle), 150 passengers, every seat taken; bag times drawn once per
  passenger on a tenth-second grid, uniform 5 to 20 s (mean 12.55 s,
  total 1,882 s); walking 0.8 s per row; 6 s for every seated neighbour
  climbed over; a passenger enters the door cell when it is free
- back to front (five zones of five rows, rear zone first, seeded order
  inside a zone): last passenger seated at 1,151.9 s = 19.20 min; 145 of
  150 passengers stood blocked in the aisle at some point; on average
  1.63 passengers stowing bags at the same time, at most 6; at most 24
  standing blocked at once
- random (one seeded shuffle): 790.4 s = 13.17 min; 134 of 150 blocked
  at some point; 2.38 stowing at once on average, at most 6; at most 16
  blocked at once
- window seats first (Steffen: window, then middle, then aisle seats;
  rows 25, 23, 21 ... one side, the same rows the other side, then the
  even rows): 318.4 s = 5.31 min; 70 of 150 blocked at some point; 5.91
  stowing at once on average, at most 13; at most 13 blocked at once
- ratios: back to front over window seats first 3.62x; random over
  window seats first 2.48x; back to front over random 1.46x
- check, half the time step (0.05 s): 1,151.9, 790.4 and 318.4 s,
  unchanged
- check, 20 seeds (0 to 19) of bag draws and shuffles: mean boarding
  time back to front 19.19 min (17.17 to 21.32), random 13.76 min (12.23
  to 15.36), window seats first 5.30 min (5.06 to 5.48); mean ratio
  3.62x; back to front slowest in 20 of 20 seeds, window seats first
  fastest in 20 of 20
- on screen at 50x from sim time 20 s: window seats first finishes at
  6.0 s of video, random at 15.4 s, back to front at 22.6 s
- payoff: window seats first 5:18 (318.4 s), back to front 19:12 (1,151.9 s), 3.6x

Narration numbers: one hundred fifty passengers (setup), five minutes
and eighteen seconds against nineteen minutes and twelve seconds
(payoff), three point six times slower.

### Production

- `sims/boarding/boarding.py` renders three fuselages of the same plane
  (25 rows of six, door cell at the front, seats filled in the lane
  colour when taken), aisle dots per passenger (ring: stowing a bag,
  white: blocked behind someone, colour: walking), a label line per
  lane with the order name, a "boarded" tag once the last passenger
  sits, and a clock in m:ss that freezes at the measured finish; legend
  "stowing a bag / waiting behind them"; the question "What is the
  fastest way to board a plane?" for the first 2.4 s, then the subtitle
  "same seats, same bags, three orders"; payoff "window seats first:
  5:18 / back to front: 19:12" from 27.0 s; 50x from sim time 20 s, 0.6
  s crossfade back to the title
- layout fixes from smoke frames: overlay 1,040 px and subtitle 1,043
  px overflowed the frame (shortened to 810 and 836 px); a seated count
  collided with the next panel label and the clock (removed); the
  "boarded" tag collided with the next clock (moved into the label
  line); the last seat column was clipped by the rounded hull (seat
  span to 990 px, hull radius 44); the clock said 5:18 while the payoff
  said 5.3 min (payoff and narration now use minutes and seconds); the
  subtitle repeated the overlay's "same 150 passengers" (replaced)
- narration `projects/boarding/narration.txt`, 104 words; round trip
  passed at 35.585 s (log `media/boarding/voice.log`) after rewording:
  "three orders" (heard "free orders") became "boarded three ways",
  "Nobody is in anybody's way" (heard "s") became "Nobody gets in
  anybody's way"; a 119-word first draft was trimmed; hooks considered:
  "What is the fastest way to board a plane?" (kept), "Why does
  boarding take so long?" (no single measured answer), "Back to front
  or random?" (the answer is a third order)
- caption schedule (chunks with the 0.6 s offset, voice 35.585 s):
  question 0.60 to 3.68; "Top: back to front, the usual call." 7.79 to
  10.18 while window seats first has already finished at 6.0 s; "One
  person stops to stow a bag, and the whole line waits." 12.58 to
  16.68; "Bottom: window seats first, every other row." 17.71 to 20.10;
  "Bags go up all along the plane at once." 21.81 to 24.89 with back to
  front finishing at 22.6 s; the question again 24.89 to 27.97 with the
  payoff on screen from 27.0; "five minutes and eighteen seconds" 30.03
  to 31.74; "nineteen minutes and twelve seconds" 32.76 to 34.47;
  "Three point six times slower." 34.47 to 36.18; music seed 44 at gain
  0.18
- text widths measured before rendering: overlay 810 px, title lines
  746 and 553, labels 322, 190 and 455, clock 178, subtitle 836,
  boarded tag 140, legend 672, payoff lines 543 and 450
- compose: `media/boarding/final.mp4` 40.000 s, 1080x1920, 60 fps,
  h264 with faststart, aac, 3.8 MB; audio mean -16.5 dB, peak -0.0 dB
  after the limiter (log `media/boarding/compose.log`)
- inspection (contact sheet 8x5 at 1 fps plus full-resolution frames
  at 0.5, 2.8, 13.0, 23.0, 28.5 and 39.95 s, and 2.8 and 28.5 s again
  after the subtitle change): title on frame one; three lanes labelled
  in their colours with the clocks running together; rings and white
  dots show the stowing and the blocked line in the back-to-front lane;
  the bottom lane shows "boarded 5:18" from 6.0 s, the middle "boarded
  13:10" from 15.4 s, the top "boarded 19:12" from 22.6 s; the caption
  band at 0.75 sits under the legend and never touches a fuselage; the
  payoff is on screen while the question is answered; loop crossfade
  closes on the title (first versus last frame mean pixel difference
  1.08 of 255)

### Published

- the Pacific quota day rolled over at 10:00:08 EEST = 00:00:08 PDT
  (clock verified against TZ=America/Los_Angeles) before the insert
- uploaded private with `scripts/yt-upload.py boarding` at 10:00:12 to
  10:00:16 EEST (publishedAt 2026-09-12T07:00:14Z), video L8qbh5LHRso,
  https://youtu.be/L8qbh5LHRso (log `media/boarding/upload.log`)
- gate read 1 at 10:00:29: 10 of 15 while processing (uploadStatus
  uploaded, processingStatus processing, definition sd, tags empty,
  duration P0D); read 2 at 10:01:40: 15 of 15 (processed, succeeded,
  hd, 1080x1920, PT41S, Seed Zero channel, title, description and tags
  match, category 27, not for kids, private) (log
  `media/boarding/qa.log`)
- published with `--publish` at 10:01:55 EEST after a fresh 15 of 15
  read; re-read privacyStatus public, embeddable, madeForKids false,
  selfDeclaredMadeForKids false (log `media/boarding/publish.log`)

### Quota

- this short: 1,600 insert + 1 channel check + 2 gate reads + 52
  publish run (1 read, 50 update, 1 re-read) = 1,655 units; day total
  1,655 of 10,000; one insert attempt today against the hard cap of
  five
