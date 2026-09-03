# Produce short: Five-state busy beaver

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day5

## Goal

Backlog idea "Busy beaver: run the five-state busy beaver champion
machine to its halt as a scrolling tape; count every step, exactly
47,176,870 from five states (peg: ninety years of Turing's 1936 paper,
window through December 2026)." Day five slate, algorithms-in-motion
pillar (A-star 971, sorting race 483). The step count is exact and
seed-free, so the reproducibility bar is the strongest possible.

## Claim

The five-state, two-symbol busy beaver champion, run from a blank tape,
halts after exactly forty seven million, one hundred seventy six
thousand, eight hundred seventy steps with four thousand ninety eight
ones on the tape. The tape first spans one hundred cells at step two
thousand six hundred seventy, one thousand cells at step two hundred
eighty four thousand, ten thousand cells at step twenty five million.
The fifth state reads a zero and halts.

## Evidence

### Measurements

`sims/busybeaver/busybeaver.py` with `projects/busybeaver/manifest.json`
(machine 1RB1LC_1RC1RB_1RD0LE_1LA1LD_1RZ0LA, blank tape, head at cell 0,
halting transition counted as a step, exact integer simulation):

- halts after 47,176,870 steps; 4,098 ones on the tape
- cells visited 12,289, from -12,243 to +45 relative to the start
- halting transition: state E reads 0, writes 1, moves right, halts
- tape first spans 10 cells at step 24, 100 cells at step 2,670,
  1,000 cells at step 284,475, 10,000 cells at step 25,615,315
- snapshots: step 100 spans 17 cells with 17 ones; step 2,000 spans 90
  cells, 65 ones; step 1,000,000 spans 2,001 cells, 1,355 ones; step
  12,000,000 spans 6,591 cells, 5,817 ones
- final tape: 8,193 runs, longest run of ones 2
- reference: the same step count and ones count are the published BB(5)
  values (Marxen and Buntrock 1990; proved by bbchallenge 2024). The
  description cites them; the narration uses only the run above.

No seed and no floating point: the result is exact by construction.

### Production

- The playback clock is logarithmic (step keys in the manifest, log
  interpolation with rounding clamped to the halt): step 1 at 1 s,
  100 at 7 s, 50,000 at 15 s, one million at 18 s, the halt at 27 s. An
  earlier truncating interpolation could stop one step short of the
  halt; the report steps are also snapshot targets now.
- Voice round-trip: 116 words, 38.12 s, after five rephrases:
  "rewrites" was transcribed as "rew rites", "state E" as "he", and
  "twenty five million" needed the digit-folding fix in
  `scripts/normalize.py` ("25 million"). Scene 42 to 40 s.
- Timing: each span milestone is on screen before it is spoken (100
  cells at 11.4 s, 1,000 at 16.7 s, 10,000 at 24.8 s of video; spoken
  at 18-26 s), the counter turns red at the halt at 27 s before "forty
  seven million" at about 28 s, and "ones on tape 4,098" is on screen
  from the halt.
- Full-resolution frames at 0.5, 8, 27.5 and 35 s inspected. The
  header under the seed overlay collided with it; the state table and
  tape strip moved down 30 and 20 px and the short was re-rendered and
  re-checked. Captions sit between the diagram label and the step
  counter; the payoff card "5 states. 47,176,870 steps. then it halts."
  fades in at 27.5 s.
- Mix: mean -16.2 dB, peak 0.0 dB. Final 40.00 s, 1080x1920, 60 fps,
  music seed 14.

### Upload and publish

- Uploaded private at 10:20 +03:00 on the fresh Pacific quota day (1,600
  units): video `-Jkxs7kNpCg`, <https://youtu.be/-Jkxs7kNpCg>.
- QA of the processed upload: processing succeeded, upload status
  processed, PT41S, hd, channel id UCWXsZTvrh_OHkzt6v1xkTsw, and title,
  description, all nine tags, category 27 and made-for-kids false
  verified against `projects/busybeaver/metadata.json`.
- Published public at 2026-09-03 10:22:09 +03:00 under the self-QA
  policy, then re-read to confirm. Third of the day's three slots.
