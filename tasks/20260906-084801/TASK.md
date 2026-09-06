# Produce short: Gambler's ruin, fair coin versus forty nine percent

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day8

## Goal

Backlog idea "Gambler's ruin: a fair coin, one player has ten times the
bankroll; measure how often the small stack survives." Day eight
slate, third slot, probability pillar in the channel's leading
two-panel "same everything, one tiny difference" format (double
pendulum 1,160 views, resonance 865, billiards 774): the same ten chips
against a hundred, the same random draws in both panels, and the coin
moved from fifty to forty nine percent. Measure how many of ten
thousand players break the house in each panel, how long the games
last, and the exact ruin probabilities as a check, before scripting.

## Claim

Ten chips against one hundred, one chip a flip, until someone has
nothing. Ten thousand players at seed zero, the same random draws in
both panels; one flip in a hundred lands differently. With the fair
coin eight hundred sixty six broke the house and nine thousand one
hundred thirty four went bust, nine of every ten. With the forty nine
percent coin sixty four broke the house, thirteen times fewer. Fair
games lasted nine hundred fifty flips on average, tilted games four
hundred sixty two. Three thousand two hundred eighty one fair-coin
players were finished within one hundred flips.

## Evidence

### Measurements

`sims/ruin/ruin.py --measure-only` with `projects/ruin/manifest.json`
(seed 0, 10,000 games per panel, player 10 chips, house 100, one chip a
flip; uniform draws from one numpy RandomState stream in chunks of
1,000 flips shared by both panels, the player wins flip j of game i
when draw u(i, j) < p; p = 0.5 in the fair panel, 0.49 in the tilted
panel; log in `media/ruin/measure.log`):

- 1.00% of draws land differently between the panels (those in
  [0.49, 0.50))
- fair: player broke the house in 866 games = 8.66% (exact a / N = 10
  / 110 = 9.09%, one standard deviation 0.29 points, so 1.5 below);
  bust in 9,134 = 91.34%; game length mean 950.4 flips (exact a (N - a)
  = 1,000), median 212, shortest 10, longest 19,994; over within 10
  flips: 7, within 100: 3,281, within 1,000: 7,625, within 10,000:
  9,952; winning games mean 3,713 flips, median 3,208, shortest 714
- tilted: broke the house in 64 = 0.64% (exact 0.61%, one standard
  deviation 0.08); bust in 9,936 = 99.36%; game length mean 461.7
  (exact 466.4), median 148, shortest 10, longest 14,488; over within
  100 flips: 3,964, within 1,000: 8,850; winning games mean 2,935
  flips, shortest 1,060
- ratio 13.5 to 1 ("thirteen times fewer")
- coupling: on the same draws the tilted player never holds more chips
  than the fair player, so every tilted win is a fair win: 64 games won
  in both panels, 802 won fair and lost tilted, 0 the other way
- exact win probability for other tilts from 10 against 100: 50%:
  9.09%, 49.5%: 2.76%, 49%: 0.61%, 48%: 0.02%, 45%: 0.00%
- independent check, `sims/ruin/ruin.py --check 100000 1` (100,000
  games per panel at seed 1, log in `media/ruin/check.log`): fair
  9,154 = 9.15% broke the house (exact 9.09%, one standard deviation
  0.09), mean 1,003.5 flips; tilted 607 = 0.61% (exact 0.61%), mean
  467.1 flips. The code reproduces the theory; the seed 0 fair count is
  a low draw and the narration states it as measured, with the exact
  value in the description

### Production

- `sims/ruin/ruin.py` renders two panels (fair coin above, 49% below)
  of 400 sampled game paths drawn incrementally on a log-flip axis
  from 1 to 50,000 flips, a shared flip clock that runs log-uniformly
  from 0.5 s to 23 s (flip 100 at about 12 s, 20,000 at about 21 s, so
  the tallies are final before "eight hundred sixty six" at 21.35 s),
  live "broke the house", "bust" and "still playing" tallies, the
  "over by flip 100" milestone label and, once every game is over, the
  average game length; payoff at 30 s
- narration `projects/ruin/narration.txt`, 110 words; voice round trip
  passed after rewording ("a hundred" reads as 100, "games" as "gains",
  "with the" as "with a", "in" as "and", and "one hundred. One chip"
  folds into 101 in the normaliser), 38.68 s; music seed 23 at gain 0.18
- `scripts/compose.sh ruin`: final.mp4 40.000 s, 1080x1920, 60 fps,
  h264 + aac, faststart, 3.4 MB, mean -15.9 dB, peak -0.0 dB
- inspected: contact sheet and full-resolution frames at 1.0, 10.0,
  12.0, 17.0, 22.5, 31.0, 38.5 s. Fixed before the final render: the
  "house broke" axis label was clipped off the left edge (replaced by
  "110" plus an inside label), the flip clock touched the panel label
  (moved to the label line), the milestone label collided with the
  inside label (moved down), and int16 overflow in the sampled paths
  (cast to float64). Fixed after the first composite: the "flips (log
  scale)" axis label collided with the "bust" readout, so the unit now
  rides on the last tick as "10,000 flips". Final composite clean:
  captions sit between the panels, tallies 866 / 9,134 and 64 / 9,936
  and the average game lengths 950 and 462 match the measurement

### Published

- Video id: `P2tQerZucVI` <https://youtu.be/P2tQerZucVI>
- Uploaded private: 2026-09-06 10:00:20 local (07:00:20Z; Pacific quota day
  2026-09-06, clock verified 10:00:11 EEST = 00:00:11 PDT),
  `scripts/yt-upload.py ruin`.
- QA gate against `projects/ruin/metadata.json` after processing
  succeeded: channel `UCWXsZTvrh_OHkzt6v1xkTsw`, uploadStatus processed,
  processingStatus succeeded, no rejection or failure reason, definition
  hd, embeddable, source stream 1080x1920, title, description, tags (as
  a set), categoryId 27, madeForKids false, selfDeclaredMadeForKids
  false, duration PT40S or PT41S, private before the flip. 15 of 15
  checks pass on 1 gate read. Log in `media/ruin/publish.log`.
- processingHints empty (faststart MP4).
- Made public: 2026-09-06 10:01:50 +03:00 (07:01:50Z) by videos.update on
  status (privacyStatus public, selfDeclaredMadeForKids false,
  containsSyntheticMedia true, embeddable true). The re-read 15 s later
  returned privacyStatus public, madeForKids false,
  selfDeclaredMadeForKids false, embeddable true.

### Quota for 2026-09-06

Spent 4,963 of the 10,000 daily units on the whole day-eight slate:
4,800 for three `videos.insert`, 3 for the channel-identity check inside
each upload, 150 for three `videos.update`, 7 for gate reads (one per
short before publishing, one extra while the bus upload processed, one
per short inside the publish run) and 3 for the confirming re-reads.
That leaves room for a full re-upload plus analytics, as the cadence
rule requires. No slot slipped.
