# Produce short: Langton's ant, two rules build a highway

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day14

## Goal

Backlog idea "Langton's ant: two rules, one ant; measure the step at
which the highway starts, its period and its drift; expect step 9,977,
period 104, two cells per period; exact, no seed." Day fourteen, third
slot. Chosen over the secretary problem, Collatz and parking-lot probing
because the drawing format is no longer the weakest: the Fourier square
(a maths drawing) topped day 13 at 1,044 views against 553 and 362 for
the two physics pieces, and Langton's ant is the canonical order-from-
chaos drawing with an exact, seedless step count. Question in the first
two seconds: "Can two rules make a plan?" One setup number (two rules),
one payoff number (the step where the highway starts). Every number
below is printed by the sim before the script is written.

## Claim

One ant on a blank grid follows two rules: on a white cell turn right,
flip the cell, step; on a black cell turn left, flip the cell, step.
For about ten thousand steps it scribbles a mess. Then, at a step the
sim measures near 9,977, it starts building a straight highway, 104
steps per block, two cells further every block, and never stops.

## Evidence

### Measurements

(recorded after the measure-only run, before scripting)

`sims/langton/langton.py` with `projects/langton/manifest.json` (exact
integer automaton on a set of painted cells, no seed, 1,000,000 steps;
log in `media/langton/measure.log`):

- period of the settled motion, smallest repeating shift scanned from
  step 500,000: 104 steps, moving (-2, +2) cells per period
- the highway starts at step 9,977: from that step every 104-step block
  repeats the same 104 turns (58 right, 46 left) and lands 2 cells
  further along the diagonal; verified for 9,519 periods out to step
  999,953; the turn sequence is identical in every period
- before the highway the ant painted 715 cells and wandered over a box
  49 by 45 cells (x -19 to 29, y -22 to 22); at step 9,977 it is at
  (-15, -10) facing left
- first profile [[0,12],[3,12],[8,450],[40,450]]: 15,591 steps in 40 s,
  highway at 27.53 s, 53 periods (106 cells) by the end, visited box 155
  by 127 cells (retuned below so the counter reads 9,977 as the number
  is spoken and the cells stay large)

Narration numbers: two rules (setup), step nine thousand nine hundred
seventy seven and one hundred four steps (payoff), thousands of steps of
mess, checked out to a million steps.

### Production

- `sims/langton/langton.py` renders the painted cells as teal squares
  (9 px) inside a wire box sized to every cell the ant visits in the
  40 s, the ant as a gold dot with a heading line, the two rules top
  left after the title, a "step N" counter top right, a gold "highway
  from step 9,977" line under the rules once the counter passes 9,977,
  and the payoff "what does it build? a highway / 104 steps a block,
  checked to a million" from 23.2 s; the view is turned a quarter turn
  anticlockwise so the road runs right and down on screen (a rotation
  keeps right turns right turns); 0.6 s crossfade back to the title
- speed profile retuned after the first measure-only run: the first
  profile [[0,12],[3,12],[8,450],[40,450]] put the highway at 27.53 s
  with 15,591 steps and 6 px cells; the final profile holds 12 steps a
  second for 8.5 s while the rules are read, ramps to 805 a second
  through the mess so the counter reads 9,977 at 22.00 s as the number
  is spoken, then slows to 110 a second on the road: 12,653 steps in
  40 s, 25 highway periods (50 cells), visited box 99 by 71 cells, 9 px
  cells (log `media/langton/measure.log`)
- layout fixes from smoke frames: the counter collided with the second
  title line (moved under the title and rules at y 340, grid box from y
  400); the highway line under the grid would have sat inside the
  caption band (moved under the rules top left); "forever" in the
  payoff was not a measured claim (now "checked to a million");
  highway text 1,424 px and payoff lines 976 and 978 px (then 1,067)
  shortened to 477, 673 and 876 px
- narration `projects/langton/narration.txt`, 102 words; round trip
  passed at 35.143 s (log `media/langton/voice.log`) after rewording:
  "at step" (heard "add step") became "on step", "One ant, two rules."
  (heard "One and two rules") became "One ant follows two rules.";
  hooks considered: "One ant, two rules. What does it build?" (kept),
  "Can two rules build a road?" (gives the answer away), "Why does the
  ant stop wandering?" (no proven mechanism to narrate)
- caption schedule (chunks with the 0.6 s offset, voice 35.143 s):
  "One ant follows two rules. What does it build?" 0.60 to 3.67; the
  rules 3.67 to 8.45 while the ant moves 12 steps a second; "For
  thousands of steps it makes a mess" 11.86 to 14.25 as the speed ramps
  to 805 a second; "Then, on step nine thousand nine hundred seventy
  seven, something clicks." 19.37 to 23.12 with the counter passing
  9,977 at 22.00 s; "What does it build? A highway." 23.12 to 25.17
  with the payoff on screen from 23.2; "checked out to a million
  steps" 29.94 to 31.99; "A mess for ten thousand steps, then a road."
  32.67 to 35.74; music seed 46 at gain 0.18
- text widths measured before rendering: overlay 677 px, title lines
  606 and 612, rules 575 and 565, counter 374, highway line 477,
  payoff lines 673 and 876
- compose: `media/langton/final.mp4` 40.000 s, 1080x1920, 60 fps, h264
  with faststart, aac, 2.7 MB; audio mean -16.6 dB, peak -0.0 dB after
  the limiter (log `media/langton/compose.log`)
- inspection (smoke frames at 0.5, 5.0, 12.0, 22.0, 23.5, 30.0 and 39.0
  s, contact sheet 8x5 at 1 fps, full-resolution frames of the final at
  0.5, 2.8, 9.0, 16.0, 22.0, 23.5, 31.0 and 39.95 s): title on frame
  one with the counter clear of it; single steps visible while the
  rules are read; the mess grows top left through 16 s; the counter
  reads 9,978 at 22.0 s under the caption "hundred seventy"; the gold
  highway line and the payoff appear at 22.0 and 23.2 s; the road runs
  right and down and stays inside the box to the last frame; the
  caption band at 0.75 sits under the box; loop crossfade closes on the
  title (first versus last frame mean pixel difference 0.14 of 255)

### Published

- uploaded private with `scripts/yt-upload.py langton` at 10:00:25 to
  10:00:29 EEST (publishedAt 2026-09-12T07:00:26Z), video No7zkBgVoc0,
  https://youtu.be/No7zkBgVoc0 (log `media/langton/upload.log`)
- gate read 1 at 10:01:42: 15 of 15 (processed, succeeded, hd,
  1080x1920, PT41S, Seed Zero channel, title, description and tags
  match, category 27, not for kids, private) (log
  `media/langton/qa.log`)
- published with `--publish` at 10:02:32 EEST after a fresh 15 of 15
  read; re-read privacyStatus public, embeddable, madeForKids false,
  selfDeclaredMadeForKids false (log `media/langton/publish.log`)

### Quota

- this short: 1,600 insert + 1 channel check + 1 gate read + 52 publish
  run (1 read, 50 update, 1 re-read) = 1,654 units; day total 4,963 of
  10,000 after the boarding (1,655) and elevator (1,654) shorts; three
  insert attempts today against the hard cap of five, so one QA-failure
  re-upload plus analytics reads still fit
