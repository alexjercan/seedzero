# Produce short: Monty Hall race

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: pilot

## Goal

Ten thousand Monty Hall games from one seed, every game scored both ways;
produce the short where the switch and stay bars race and switching wins
about two thirds.

## Claim

Ten thousand games at seed zero: staying won three thousand three hundred
and eight, switching won six thousand six hundred and ninety two. Switching
more than doubled the wins.

## Evidence

### Measurements

- `sims/montyhall/montyhall.py` at manifest seed 0, 10000 games:
  stay wins 3308 (33.08%), switch wins 6692 (66.92%), switch vs stay
  2.02 to 1. Theory: 2/3 = 6666.7.
- Host honesty check printed by the sim: the opened door is never the
  pick and never the prize, so the mechanism matches the narration.
- Every game is scored under both strategies, so exactly one strategy
  wins each game; the two bars always sum to the resolved game count.

### Hooks considered

1. "Ten thousand rounds of the same game, all at once." [kept]
2. "Ten thousand people played the same game show. The switchers won
   twice as often."
3. "This puzzle made mathematicians angry. Ten thousand games settle it."

Kept 1: it matches the opening visual (the finished race) and defers the
payoff numbers to the measured beat.

### Production

- `sims/montyhall/montyhall.py` renders the race as two horizontal bars
  with riding counts, a 2/3 dashed target line, and a doors panel that
  replays the first games one by one (pick outline, forced goat reveal,
  switch arrow, prize reveal with winner label). Footage 40.5 s,
  1080x1920, 60 fps; ends on the intro frame so the loop closes.
- Voice round-trip failed twice, then passed at 37.9 s: "and" inside
  spelled numbers broke number folding in `scripts/normalize.py`, and
  sentence-initial "Switching" transcribed as "twitching". Dropped the
  "and"s and rephrased to "The switch".
- First contact sheet (vertical bars) showed the caption band striking
  the stay count and the payoff line crowding the switch count; moved to
  horizontal bars with fixed label rows clear of the caption band at
  y 1344-1420, then widened row spacing to unclip the switch label.
- Final inspection: hook lands at 0 s (finished race + ratio), captions
  match narration, measured counts land at 18.5 s as they are spoken,
  loop closes. Mix: mean -15.7 dB, limiter at 0.9.

### Upload and publish

- Uploaded private with new `scripts/yt-upload.py` (1,600 quota units):
  video `cT8Tcjm7mUs`, <https://youtu.be/cT8Tcjm7mUs>.
- QA on the processed video: processing succeeded, duration PT41S,
  title, description, tags, category, privacy verified against
  `projects/montyhall/metadata.json` (API alphabetizes tags;
  containsSyntheticMedia is write-only in videos.list, accepted at
  insert).
- Published public at 2026-08-30T22:07:34+03:00 under the self-QA
  policy (owner authorized 2026-08-30).
