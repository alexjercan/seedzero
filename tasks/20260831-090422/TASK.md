# Produce short: Sorting race, quicksort vs bubble

- STATUS: CLOSED
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

### Production

- Voice round-trip: two iterations. "Quicksort" transcribed as "quick
  sort" (narration now says "Quick sort"); "Ninety thousand. One
  hundred thousand." folded across the sentence break into 190,000 by
  normalize.py (added "Then" between them). Final ok at 37.0 s.
- Contact sheet: quicksort triangle done and green at 1 s while bubble
  grinds; "Then one hundred" caption lands with the counter at
  100,115; "eighty comparisons." lands at 130,607 just before the
  cross; payoff appears at the cross. Loop closes. Mix: mean -15.7 dB.

### Upload and publish

- Uploaded private after the Pacific quota reset (1,600 units):
  video `wZt9K5LYZB4`, <https://youtu.be/wZt9K5LYZB4>.
- QA: processing succeeded, PT41S, all metadata fields verified.
- Published public at 2026-08-31 ~10:04 +03:00 under the self-QA
  policy. Third of the day's three slots: daily cadence cap reached,
  no more uploads today.

