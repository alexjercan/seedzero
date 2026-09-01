# Produce short: Coin flip for a million

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day3

## Goal

Backlog idea "Coin flip for a million: ten thousand players choose fifty
thousand sure versus a coin flip for a million; expected value says flip,
yet measure how many flippers walk away with nothing (peg: viral poll,
publish by mid September 2026)." Morning briefing candidate for the
2026-09-01 slate.

## Claim change

Measured, the one-shot version has no surprise in it: 5,064 of 10,000
flippers keep the million and 4,936 walk away with nothing. "About half
of them lost a coin flip" is what every viewer predicts before pressing
play, so it fails the "one surprising claim" bar in `docs/vision.md` even
though the number is real.

Per `docs/vision.md` step 3 the claim changed rather than the numbers.
Round one is still exactly the viral poll; the winners are then offered the
same bet again, round after round. That keeps the hook, keeps the fair
coin, and has a payoff nobody predicts.

## Claim

Ten thousand players, fifty thousand guaranteed or a fair coin flip for a
million, taken again every round. The pot grows ten point zero times a
round, exactly what expected value promises. At round thirteen the pot is
zero and none of the ten thousand players is still holding anything.

## Evidence

### Measurements

`sims/coinflip/coinflip.py` with `projects/coinflip/manifest.json`
(seed 0, 10,000 players, keep 50,000 or flip for 1,000,000, so 20x the
stake on heads and expected value 10x every round):

- safe total if nobody ever flips: 500,000,000
- round  1: 5,064 still holding, pot 5.06 billion
- round  2: 2,602, pot 52 billion
- round  3: 1,287, pot 515 billion
- round  4: 635, pot 5.08 trillion
- round  5: 330, pot 52.8 trillion
- round  6: 170, pot 544 trillion
- round  7: 91, pot 5.82 quadrillion
- round  8: 51, pot 65.3 quadrillion
- round  9: 28, pot 717 quadrillion
- round 10: 8, pot 4.1 quintillion
- round 11: 3, pot 30.7 quintillion
- round 12: 2, pot 410 quintillion
- round 13: 0, pot 0
- pot growth per round before the last: min 5.71x, max 13.33x, mean 10.02x,
  which is the expected value multiplier to two decimal places
- expected value after 13 rounds: 10 trillion times the stake

Seed sensitivity: the bust round is 13 at seeds 0 and 1, 14 at seed 2 and
12 at seed 3. The narrated number is seed 0, which is on screen and in the
description, so a rerun reproduces it.

### Production

- Voice round-trip: passed first time at 40.031 s, 125 words.
- Round one holds from 3.5 s to 8.5 s so that "Five thousand sixty four are
  still holding" is spoken against the 5,064 readout; rounds two to
  thirteen then run on a steady 2.0 s cadence to 30.5 s.
- Two render passes. The first left nine and a half seconds of a fully
  static empty grid at the end. Added a survivors-per-round bar chart in
  that dead space, which also makes the halving visible; the round
  thirteen bar is drawn as nothing rather than a stub.
- Contact sheet: opening frame is a solid block of 10,000 gold squares and
  works as the thumbnail; "Five thousand sixty four are still holding" at
  6-8 s with "still holding: 5,064 of 10,000" on screen; "Round thirteen"
  at 32 s with the grid empty, "pot: 0" and the payoff "13 rounds: 0 of
  10,000 left"; "Zero of ten thousand still have anything" at 37-39 s.
  Every narrated number is true when spoken.
- Mix: mean -15.2 dB. Final 41.50 s, 1080x1920, 60 fps.

### Upload and publish

- Uploaded private on the fresh Pacific quota day (1,600 units):
  video `AbSkSS1F2Mw`, <https://youtu.be/AbSkSS1F2Mw>.
- QA of the processed upload: processing succeeded, upload status
  processed, PT42S, hd, channel id UCWXsZTvrh_OHkzt6v1xkTsw, and title,
  description, all nine tags, category 27 and made-for-kids false all
  verified against `projects/*/metadata.json`.
- Published public at 2026-09-01 10:44 +03:00 under the self-QA
  policy, then re-read to confirm the visibility flip. Third of the
  day's three slots: the daily cadence cap is reached, no more uploads today. Quota spent 4,953 of 10,000 units
  (three uploads at 1,600, plus the QA reads and the three visibility
  updates), so the day keeps room for a re-upload.
