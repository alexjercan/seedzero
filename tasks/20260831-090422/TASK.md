# Produce short: Sorting race, quicksort vs bubble

- STATUS: OPEN
- PRIORITY: 0
- TAGS: day2

## Goal

Quicksort versus bubble sort on the same seeded shuffle of 512 bars,
with honest comparison counters replayed at one shared rate. Backlog
idea validated by trend research 2026-08-30 ("fastest sorting
algorithm" recurring search; expected ratio above 20 to 1).

## Claim

Same five hundred twelve shuffled bars, same rules. Quicksort finishes
in four thousand four hundred sixty one comparisons, one point zero
seconds at the race rate. Bubble sort needs one hundred thirty
thousand six hundred eighty comparisons and crosses at thirty point
zero seconds: twenty nine times the work for the same result.

## Evidence

### Measurements

`sims/sortrace/sortrace.py` at manifest seed 0, 512 bars, race 30.0 s:

- quicksort: 4,461 comparisons, 2,637 swaps
- bubble sort: 130,680 comparisons, 65,075 swaps
- ratio: 29.3 to 1
- shared race rate: 4,356 comparisons/s (bubble crosses at 30.0 s)
- quicksort finishes at 1.02 s of race time
- both replays sort-verified (asserted ascending) before rendering
- narration callouts "ninety thousand" and "one hundred thousand" land
  at video 24.0 s and 25.5 s, when the shared-rate counter reads about
  93,600 and 100,200: both true when spoken.

