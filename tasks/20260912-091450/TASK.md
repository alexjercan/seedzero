# Produce short: Elevator paradox, which way is the first elevator going

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day14

## Goal

Backlog idea "Elevator paradox: ten floors, you wait on floor two;
measure over ten thousand waits how often the first elevator to arrive
is going down; expect about eighty nine percent." Day fourteen, second
slot. Chosen because it is one continuous motion (one elevator cycling a
ten-floor shaft) with one watcher and one seeded random input (the
moments the watcher presses the button), and the answer is a single
counted number that a viewer can check by rerunning at the shown seed.
Question in the first two seconds: "You wait on floor two. Which way is
the first elevator going?" One setup number (ten floors, floor two), one
payoff number (the share of arrivals going down). Every number below is
printed by the sim before the script is written.

## Claim

You wait on floor two of a ten-floor building with one elevator that
runs top to bottom and back without stopping. Press the button at ten
thousand random moments. The first elevator to reach you is going down
about nine times in ten, because the elevator is almost always above
you.

## Evidence

### Measurements

(recorded after the measure-only run, before scripting)

`sims/elevator/elevator.py` with `projects/elevator/manifest.json` (one
elevator at a constant 2 s per floor, never stopping, position a
triangle wave; the first arrival after each press found in closed form;
log in `media/elevator/measure.log`):

- 10 floors, 18 s up, 18 s down, cycle 36 s; 10,000 button presses at
  seed 0 spread evenly over 6 full cycles (216 s) starting at sim time
  40.0 s
- floor 2 (you): first elevator going down 8,900 times, going up 1,100
  (89.00% down; exact share of the cycle spent above floor 2: 8/9 =
  88.89%); mean wait 14.3 s, 15.8 s when it came down, 2.0 s when it
  came up
- floor 9 (a friend, not narrated): going down 1,138, going up 8,862
  (11.38% down; exact 1/9 = 11.11%)
- floor 5 (middle, not narrated): going down 5,562, going up 4,438
  (55.62%; exact 5/9 = 55.56%)
- check, 1,000,000 presses at seed 1 on floor 2: 88.850% down
- on screen at 10x from sim time 20 s: presses from 2.00 to 23.60 s of
  video, last press answered at 26.60 s; the elevator is at floor 9.00
  going down in the first frame
- payoff: going down 8,900 of 10,000, going up 1,100

Narration numbers: floor two of ten (setup), eight thousand nine
hundred out of ten thousand (payoff); the mechanism share eight seconds
out of nine is the exact 8/9 the sim prints.

### Production

- `sims/elevator/elevator.py` renders a ten-floor building with a shaft
  and the car (a rectangle with a direction triangle), a stick figure
  "you" on floor 2 with a gold button, and on the right a trace "where
  the elevator has been" over the last 72 s of sim time, teal above
  floor 2 and gold below; each press is a tick on the floor-2 line,
  white until the elevator arrives, then teal (down) or gold (up); a
  tally "going down N / going up N" with a proportion bar; the
  three-line question for the first 2.6 s, then the subtitle "10
  floors, one elevator, never stops"; payoff "going down: 8,900 of
  10,000 presses / going up: 1,100" from 28.0 s; 10x from sim time 20
  s, 0.6 s crossfade back to the title
- layout fixes from smoke frames and the first composed frames: tally
  labels at font 56 collided (font 44); the "you" label sat under the
  floor line (moved above the head); payoff line 1 was 954 px
  (shortened to 834); the title's first line touched the overlay at y
  96 (title lines moved from 150/212/274 to 168/228/288, footage
  re-rendered and re-composed)
- narration `projects/elevator/narration.txt`, 119 words; round trip
  passed first time at 33.518 s (log `media/elevator/voice.log`); a
  95-word first draft (27.5 s) said "Down." before the last press was
  answered at 26.6 s, so the mechanism paragraph was lengthened until
  "Down." lands at 29.05 s; hooks considered: "You wait on floor 2.
  Which way is the first elevator going?" (kept), "Why is the elevator
  always going the wrong way?" (assumes the answer), "Is the elevator
  against you?" (no measured answer)
- caption schedule (chunks with the 0.6 s offset, voice 33.518 s):
  question 0.60 to 5.39; "Press the button at ten thousand random
  moments" 7.92 to 10.74 with the presses on screen from 2.00 to 23.60
  s; "The line on the right shows where the elevator has been" 11.87 to
  14.96; "eight seconds out of nine" 16.09 to 17.50; "Which way is the
  first elevator going?" 27.08 to 29.05 after the last press is
  answered at 26.60 s; "Down." 29.05 to 29.33 with the payoff on screen
  from 28.0; "Eight thousand nine hundred times out of ten thousand"
  29.33 to 31.86; "Your friend on floor nine sees the opposite." 31.86
  to 34.12; music seed 45 at gain 0.18
- text widths measured before rendering: overlay 826 px, subtitle 800,
  title lines 612, 683 and 492, tally labels 443 and 372, payoff lines
  834 and 354
- compose: `media/elevator/final.mp4` 40.000 s, 1080x1920, 60 fps,
  h264 with faststart, aac, 5.7 MB; audio mean -16.7 dB, peak -0.0 dB
  after the limiter (log `media/elevator/compose.log`)
- inspection (contact sheet 8x5 at 1 fps plus full-resolution frames
  at 0.5, 2.8, 10.0, 20.0, 26.6, 29.5 and 39.95 s, then 0.5 and 39.95
  again after the title move): the car starts at floor 9 going down;
  the trace shows the long triangle above floor 2 and the short gold
  dips below it; press ticks turn teal or gold as they are answered;
  the tally reads 8,900 / 1,100 from 26.6 s; the caption band at 0.75
  sits under the tally bar; the payoff is on screen while "Down." is
  spoken; the title clears the overlay; loop crossfade closes on the
  title (first versus last frame mean pixel difference 0.43 of 255)

### Published

- uploaded private with `scripts/yt-upload.py elevator` at 10:00:21 to
  10:00:25 EEST (publishedAt 2026-09-12T07:00:22Z), video Bdksy-fBzow,
  https://youtu.be/Bdksy-fBzow (log `media/elevator/upload.log`)
- gate read 1 at 10:01:41: 15 of 15 (processed, succeeded, hd,
  1080x1920, PT41S, Seed Zero channel, title, description and tags
  match, category 27, not for kids, private) (log
  `media/elevator/qa.log`)
- published with `--publish` at 10:02:13 EEST after a fresh 15 of 15
  read; re-read privacyStatus public, embeddable, madeForKids false,
  selfDeclaredMadeForKids false (log `media/elevator/publish.log`)

### Quota

- this short: 1,600 insert + 1 channel check + 1 gate read + 52 publish
  run (1 read, 50 update, 1 re-read) = 1,654 units; day total 3,309 of
  10,000 after the boarding short (1,655); two insert attempts today
  against the hard cap of five
