# Produce short: Lorenz water wheel, turn the tap up

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day20

## Goal

Backlog idea (trend research 2026-09-16, task 20260916-100924):
"Lorenz water wheel: a wheel of leaking buckets under a steady tap
beside the same wheel under a faster tap; measure the direction
reversals in five minutes and the longest run one way; expect the slow
tap to turn steadily and the fast tap to reverse irregularly (the
Malkus wheel is the Lorenz system); the count is the payoff, so keep
the wheel and the water on screen; RK4; deterministic, no seed."
Day twenty, third slot. Chosen because it is continuous motion, a
two-panel same-input comparison (the same wheel under two tap rates),
from the chaos pillar that performs on this channel, with one plain
question, one setup number (how much faster the tap runs) and one
payoff number (the count of reversals) the simulation measures.
Question in the first two seconds: "Turn the tap up. Does the wheel
spin faster?"

## Claim

A wheel of leaking buckets under a steady tap turns one way for ever;
under a faster tap the same wheel keeps changing direction at
irregular times. Every number below is printed by the sim before the
script is written.

## Evidence

### Measurements

(recorded after the measure-only run, before scripting)

`sims/waterwheel/waterwheel.py` with `projects/waterwheel/manifest.json`
(a vertical wheel of radius 30 cm with 12 buckets on its rim, g =
9.80665 m/s^2; every bucket leaks at 0.1 per second, so it loses 9.5
percent of its water each second; the tap pours into the buckets
nearest the top through a Gaussian lobe of width 0.4 rad, normalised
over the buckets so the total inflow is exact; bearing drag 0.77 N m s
per rad; dry wheel inertia 1.3 kg m^2 plus R^2 times the water on it;
slow tap 20 g/s, fast tap 3 times that = 60 g/s; both wheels start at
rest with empty buckets and bucket 0 at 0.05 rad clockwise of the top;
RK4 at dt = 1 ms; the video shows the 240 s window in 40 s, 6x;
deterministic, no seed; log in `media/waterwheel/measure.log`). The
parameters came from a scan (`media/waterwheel/scan.log`, 216 sets of
K, r, sigma, lobe width and tap ratio, then 72 rounded drag and inertia
values) for a run whose slow wheel never reverses and whose fast wheel
reverses 6 to 12 times in the window with its last reversal early
enough for the payoff sentence; the count below is that run's
measurement, and the sensitivity line records that a different start
gives a different count later on:

- Lorenz form of the wheel (first Fourier modes, b = 1): slow tap r =
  g R Q c1 / (nu K^2) = 7.05, sigma = nu / (K I) = 5.84, Hopf value
  sigma (sigma + 4) / (sigma - 2) = 14.97, so steady rotation is
  stable; closed-form steady speed K sqrt(r - 1) = 0.2460 rad/s; fast
  tap r = 21.16, sigma = 5.69, Hopf value 14.94, so the fast wheel's
  steady rotation is unstable
- reversal rule (printed): a reversal is counted when omega crosses
  zero and then reaches 0.05 rad/s in the new direction; its time is
  the zero crossing; a wobble about zero that does not reach 0.05 rad/s
  the other way does not count; the first direction is set when
  |omega| first reaches 0.05 rad/s
- slow wheel (20 g/s): starts turning clockwise at 34.0 s; 0 reversals
  in 240 s and 0 in 480 s; steady speed 0.2469 rad/s = 2.36 turns a
  minute clockwise (mean over the last 30 s of the window), turn period
  25.44 s, within 5 percent of it from 208.1 s, between 0.2275 and
  0.2608 rad/s over the last 60 s (a shrinking wobble about the steady
  value, never near zero); peak 0.5231 rad/s at 42.9 s (the start-up
  swing); 7.46 net turns in the window; 0.2509 rad/s at the end
- fast wheel (60 g/s): starts turning clockwise at 17.4 s; 6 reversals
  in the 240 s window, at 25.3, 95.2, 123.2, 137.1, 153.5 and 168.0 s
  of wheel time = 4.2, 15.9, 20.5, 22.8, 25.6 and 28.0 s of video; runs
  one way 8.0 (from the start), 69.9, 28.0, 13.9, 16.4 and 14.5 s,
  longest 69.9 s, shortest 8.0 s, and the last run from 168.0 s to the
  end of the window, 72.0 s and still going; 7.74 turns clockwise and
  5.69 counterclockwise (net +2.05); peak 1.2052 rad/s = 11.51 turns a
  minute at 22.8 s; 0.7139 rad/s at the end of the window
- fast wheel, next window (240 to 480 s): 7 more reversals at 258.3,
  287.8, 355.9, 421.5, 435.5, 450.1 and 463.8 s; 13 in 480 s; longest
  run in the second window 90.3 s
- sensitivity: the fast wheel restarted with the start angle moved by
  1e-6 rad is 0.001 rad away in wheel angle from 157.2 s and 0.1 rad
  from 252.6 s (past the window); it has the same 6 reversal times in
  the window; the gap grows about 0.0456 per second, e-folding every
  21.9 s
- check at half the step (dt = 0.5 ms): slow steady speed 0.2469 rad/s
  (+0.000000); the fast wheel's 6 reversal times agree to 0.000 s
- buckets: fullest bucket in the window 258.6 g (drawn full at 260 g);
  water on the wheel at the end of the window 200.0 g (slow) and 600.0
  g (fast), equal to Q / K
- on-screen text widths (PIL getlength): overlay 915, title lines 508
  and 879, labels 191 and 176, sublabels 346 and 345, "reversals" 146,
  counter 67, speed line 312, status 192, "6x speed" 142, clock 90,
  payoff lines 843 and 586 px; all under 950 px
- video mapping: the reversals show at 4.2, 15.9, 20.5, 22.8, 25.6 and
  28.0 s of video; the counter reads 6 from 28.01 s; peak on-screen
  spin 1.15 turns per second

Narration numbers: three times the water (setup), six (payoff, the
reversal count in the window). The 4 minutes, the 6x factor, the
speeds, the run lengths, the second window, the Lorenz form, the
sensitivity and the half-step check go to the description and the
screen.

### Production

- narration: three hooks tried, "Turn the tap up. Does the wheel spin
  faster?" (the title), "More water, more spin? Turn the tap up and
  count." and "Why does a faster tap make this wheel turn back?"; the
  first was kept because the payoff answers it in the same words ("No.
  The slow tap turns one way the whole time. The fast tap reversed six
  times."); the third gives the answer away and the second has no
  matching payoff; the audio opens with a noun phrase ("A wheel of
  leaking buckets under a tap.") so the sentence-initial "Turn" is not
  clipped; `projects/waterwheel/narration.txt`, 116 words; the setup
  number is three times the water, the payoff six; "chaos", "Lorenz"
  and the minutes stay off the narration
- voice: `scripts/voiceover.sh projects/waterwheel/narration.txt`
  failed the round trip once on wording, never on a number: "The heavy
  side drops" was heard as "sigh drops" (now "The heavy side goes
  down"); the second run passed (116 words, 35.32 s, ends at 35.92 s
  of the 40 s video, 3.3 words/s); timing (`scripts/voice-timing.py`,
  +0.6 s offset): the question "Does the wheel spin faster?" inside
  0.6 to 5.5 s with the title card to 2.4 s, "Same wheel. Same
  buckets. Two taps." 5.5 to 8.4 s, "The fast tap pours three times
  the water ... the wheel turns" 8.4 to 16.85 s with both wheels
  turning (fast from 2.9 s, slow from 5.7 s, first reversal at 4.2 s),
  "The slow wheel picks a direction and keeps it, the fast wheel gets
  too much water and swings too far" 16.85 to 22.63 s over reversals 2
  and 3 (15.9, 20.5 s), "The full buckets ride up the other side, and
  their weight drags the wheel back. Watch the counter. There is no
  pattern. So does the wheel spin faster" 22.63 to 30.69 s over
  reversals 4, 5 and 6 (22.8, 25.6, 28.0 s; the counter reads 6 from
  28.01 s), "No." 30.69 to 31.31 s as the payoff card fades in from
  30.6 s, "The slow tap turns one way the whole time. The fast tap
  reversed six times." 31.31 to 35.92 s with the card up and the
  counter at 6; log in `media/waterwheel/voice.log`
- footage: `sims/waterwheel/waterwheel.py` (no arguments) wrote
  `media/waterwheel/footage.mp4`, 40.00 s at 60 fps, 2,400 frames, at
  10:50 EEST with payoff_t 30.6 s in the manifest (moved from 30.0 s
  after the voice timing so the card fades in on "No."; the manifest
  change touches only the drawing; the same run re-printed every
  measurement above, log in `media/waterwheel/render.log`); text
  widths at most 915 px (the overlay) so nothing clips at 1080 px;
  smoke frames at 0, 1.5, 3, 6, 12, 20, 28, 34 and 39.7 s inspected
  first, then the layout changed and frames at 0, 1.5, 3, 12, 28.3
  and 39.7 s inspected again: the three-line title sat on the tap
  pipe (now two lines, "Does the wheel spin faster?" 879 px), the fast
  wheel's buckets saturated the drawing at 120 g (now drawn full at
  260 g against the 258.6 g fullest bucket), the slow wheel's settle
  metric was changed from a 1 percent to a 5 percent band plus the
  range over the last 60 s, and the stream got a falling texture so
  the first seconds are not static; each panel shows the tap and
  stream (width by tap rate), the wheel with spokes and hanging
  buckets with water levels and drips, a direction arrow at the hub
  that fades through zero speed, "reversals" counter with a 0.5 s
  white flash at each measured reversal, live turns a minute, "6x
  speed", a wheel-time clock, the status words "one way" (slow, from
  6.7 s) and "turns back" (fast, 1.6 s after each reversal), and a
  thin trace of speed against time under the buckets; the payoff card
  reads "no. slow tap: one way the whole time | fast tap: reversed 6
  times" with the 6 taken from the measured list
- compose: `scripts/compose.sh waterwheel` wrote
  `media/waterwheel/final.mp4` (h264 1080x1920 60 fps, aac, 40.000 s;
  music seed 61 at gain 0.18, a seed no other project uses; captions
  at caption_y 0.75); loudness mean -16.4 dB, peak -0.0 dB; preview
  and 8x5 contact sheet written (`media/waterwheel/compose.log`)
- local QA: frames at 0.02, 2.3, 4.3, 8.5, 16.0, 22.9, 28.1, 30.7,
  34.5 and 39.95 s extracted from final.mp4; the contact sheet and all
  ten frames inspected: overlay at y 96 and the two title lines at 190
  and 252 with clear space between them, both wheels at rest with the
  streams on and the counters at 0 at 0.02 s (the thumbnail), the
  title fading under the caption "buckets under a tap." at 2.3 s, the
  fast wheel's first reversal at 4.3 s ("turns back", counter 1, arrow
  flipped, slow wheel still at 0.0 turns a minute), "one way" on the
  slow wheel at 8.5 s with the fast wheel at 6.0 turns a minute
  counterclockwise, reversal 2 at 16.0 s (counter 2, 0.7 turns a
  minute through zero), reversal 4 at 22.9 s (counter 4, 0.2 turns a
  minute, arrow faded) under "The full buckets", the counter flashing
  6 with "turns back" at 28.1 s under "There is no pattern.", the
  payoff card fading in at 30.7 s under "spin faster?" with the
  counter already at 6, the card fully on at 34.5 s under "The fast
  tap" with the slow wheel at 2.2 turns a minute and reversals 0, and
  the last frame crossfading to the title frame; the caption band (y
  1440 to 1520) has nothing behind it, the trace strips end at 1411;
  no clipped text, captions match the narration; approved
- metadata: `projects/waterwheel/metadata.json`, title 100 characters
  (the maximum), description with the setup, the reversal rule, the
  slow wheel's steady speed, the six reversal times and run lengths,
  the second window, the Lorenz form, the sensitivity and half-step
  checks, a "Why" paragraph naming the wheel as the Lorenz system, the
  rerun sentence and the closing line; 10 tags; category 27; private;
  containsSyntheticMedia true
- not done by this producer: upload, publish, web/data, commit (the
  orchestrator reviews and uploads)

### Published

- quota check before the insert: clock 2026-09-18T10:53:23+03:00 EEST; one upload
  attempt (monkeyhunter, 10:26:34, published) recorded since the 10:00
  EEST boundary (log entries and media/*/upload.log both checked); this
  is insert attempt 2 of the hard cap of 5
- orchestrator review before the upload: task evidence, the contact
  sheet and the frames at 0.02, 16.0 and 30.7 s inspected; title clear
  of the overlay, no clipped text, the reversal counter reads 6 with the
  payoff card while the count is spoken, the last frame crossfading to
  the first; the description carries the fast wheel's peak speed (11.5
  turns a minute) and its net turns so the "No" answer is honest; noted
  that both wheels rest for the first 2.9 to 5.7 s with only the stream
  and the filling buckets moving; approved
- attempt 2 recorded at 2026-09-18T10:53:23+03:00, video name waterwheel, before running
  `scripts/yt-upload.py waterwheel`

- upload: `scripts/yt-upload.py waterwheel` ran 10:53:23 to 10:53:30 EEST,
  token verified to see only the Seed Zero channel, video id
  5v7Z2S9ybgA, private (`media/waterwheel/upload.log`)
- gate: `scripts/yt-qa.py waterwheel 5v7Z2S9ybgA --wait --publish` in
  the foreground from 10:58:30 EEST, after a five-minute wait so the
  tags could read back (the first upload of the day showed them absent
  for about six minutes); processing had succeeded, 15 of 15 pass
  (processed, succeeded, hd, 1080x1920, title, description, tags,
  category 27, not for kids, PT41S for the 40.000 s file, private);
  containsSyntheticMedia reads absent as on every earlier upload
  (`media/waterwheel/publish.log`)
- publish: the same run set the video public at 2026-09-18T10:58:32+03:00;
  the re-read after 15 s shows privacyStatus public, madeForKids false,
  embeddable true; public at https://youtu.be/5v7Z2S9ybgA

### Quota

- attempt 2 of the hard cap of 5 for the quota day that began
  2026-09-18T10:00 EEST; cost 1 + 1,600 + 52 = 1,653 units; day total
  after two attempts 3,312 units
