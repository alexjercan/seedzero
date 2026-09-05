# Produce short: Epidemic threshold, one contact more

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day7

## Goal

Backlog idea "Epidemic threshold: same virus, contact rate just below
versus just above the threshold; measure final infected counts." Day
seven slate, first slot, emergence pillar. Chosen because the channel's
leading format is a two-panel comparison where a tiny difference in one
parameter blows up (double pendulum 1,161 views, resonance 844 in its
first day, billiards 773, pendulum wave 721), and this idea has exactly
that shape: same town, same first case, same coin flips, one contact
more or less per sick person. Measure the realised reproduction number
and the final case count in each panel before scripting.

## Claim

Same town of forty thousand people, same virus, same ten first cases,
same seed. With eleven contacts a day each case infected zero point nine
three others on average over the first hundred cases, and the outbreak
died on day fifty at two hundred twenty five cases. With thirteen
contacts a day each case infected one point one nine others; the
outbreak passed ten thousand cases by day two hundred and burned out on
day two hundred fifty five at eleven thousand three hundred ninety seven
cases, more than a quarter of the town. Two more contacts a day, fifty
times the cases.

## Evidence

### Measurements

`sims/epidemic/epidemic.py --measure-only` with
`projects/epidemic/manifest.json` (seed 0, town 200 by 200 = 40,000
people, 10 first cases at seeded houses, contacts drawn each day from
the 11 by 11 block around the house (reach 5), transmission probability
0.05 per contact, 2 sick days, SIR on a grid, numpy RandomState; the
below panel uses 11 contacts a day, the above panel 13; log in
`media/epidemic/measure.log`):

- both panels start from the same ten houses (checked: True)
- 11 contacts a day (nominal R0 1.10): realised R over the first 50
  cases 0.96, first 100 cases 0.93, first 200 cases 1.00, over all 225
  cases 0.956; peak 26 sick on day 37; outbreak ended on day 50 with
  225 cases = 0.6% of the town; day 10: 59, day 20: 91, day 30: 129,
  day 40: 209 cases
- 13 contacts a day (nominal R0 1.30): realised R over the first 50
  cases 1.14, first 100 cases 1.19, first 200 cases 1.09; peak 184 sick
  on day 99; outbreak ended on day 255 with 11,397 cases = 28.5% of the
  town; day 10: 116, day 20: 351, day 30: 689, day 40: 1,094, day 60:
  2,112, day 80: 3,413, day 100: 5,044, day 120: 6,385, day 150: 8,665,
  day 200: 10,752 cases
- ratio of final counts 50.7 to 1
- how typical seed 0 is, 300 seeds per panel: 11 contacts took off
  (more than 1,000 cases) in 6.0% of runs, cases min 15, median 267,
  max 1,506, seed 0 at the 45th percentile; 13 contacts took off in
  97.3%, cases min 16, median 12,004, max 14,554, seed 0 at the 35th
  percentile

Design path, recorded because it changed the claim's shape:

- The first scan (`--scan`, `media/epidemic/scan.log`, 100 by 100 town,
  first cases in the town centre, reach 3, 300 seeds per contact
  count) put the tipping point at 13 to 14 contacts with a fuzzy edge
  (13: 6.7% take off, 14: 68.7%, 15: 97.0%). Ten first cases spread
  over seeded houses with reach 5 sharpened it to 11 versus 13.
- At 100 by 100 (`media/epidemic/measure-100x100.log`) seed 0 gave 725
  versus 3,379 cases, only 4.7 to 1, with the below run at the 96th
  percentile of its own distribution. The 200 by 200 town gives 50.7
  to 1 with both runs near the middle of their distributions, so the
  narrated contrast is typical, not a lucky seed.

### Production

- Timeline: the towns start on day 0 at 0.5 s and run at 9 days per
  second, so the top town's end on day 50 lands at 6.1 s (spoken "Day
  fifty: over" at 6.3 to 7.5 s), day 200 at 22.7 s, and the bottom
  town's end on day 255 at 28.8 s inside "It burns out on day two
  hundred fifty five" (28.2 to 30.5 s). Payoff "11 contacts: 225 cases.
  13 contacts: 11,397" fades in at 30.0 s.
- Voice round trip: 117 words, 38.87 s, fourth wording. The first
  draft ran 44.15 s for a 40 s scene and was trimmed. "Bottom:" was
  transcribed "putum" and became "thirteen in the bottom" and "The
  bottom town". "Day two hundred: ten thousand" folded to 210,000 in
  the normaliser because only punctuation separated the two numbers;
  it became "By day two hundred, more than ten thousand cases".
- Layout fixes from the full-resolution frames: the overlay "seed 0 |
  40,000 people | same 10 first cases | deterministic" ran off both
  edges at 34 px and lost "deterministic"; the 3 px houses with a 1 px
  grout left 2 px dots that vanished on a dark town, so cells under
  5 px are now solid and the susceptible, sick, fresh and recovered
  colours were brightened.
- Inspected after the final render: the contact sheet (8 by 5 at 1 fps)
  and frames at 0.5, 7, 12, 20, 29 and 33 s. The top town flickers and
  stops at 225 cases from 6 s on, the bottom town sweeps the square,
  captions sit between the panels, the payoff is on screen at 30 s.
- Mix: mean -15.6 dB, peak -0.0 dB. Final 40.000 s, 1080x1920, 60 fps,
  h264 plus AAC, music seed 18, faststart MP4.

### Published

- Video id: `jD5cymWeNgM` <https://youtu.be/jD5cymWeNgM>
- Uploaded private: 2026-09-05 10:00:43 local, 43 s after the midnight
  Pacific quota reset (clock verified: 10:00:32 local = 00:00:32 PDT,
  Pacific date 2026-09-05), `scripts/yt-upload.py epidemic`.
- QA gate against `projects/epidemic/metadata.json` after processing
  succeeded: channel `UCWXsZTvrh_OHkzt6v1xkTsw`, uploadStatus processed,
  processingStatus succeeded, no rejection or failure reason, definition
  hd, embeddable, source stream 1080x1920, title, description, tags (as
  a set; YouTube returns them alphabetised), categoryId 27, madeForKids
  false, selfDeclaredMadeForKids false, duration PT41S (YouTube rounds
  40.000 s up), private before the flip. 15 of 15 checks pass. Log in
  `media/epidemic/publish.log`.
- processingHints came back empty: the faststart MP4 cleared the
  nonStreamableMov hint that every day-six upload carried.
- Made public: 2026-09-05 10:01:41 +03:00 (07:01:40Z publishedAt).
  Re-read confirms privacyStatus public.
