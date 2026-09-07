# Produce short: Buffon's needle, pi from falling sticks

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day9

## Goal

Backlog idea "Buffon's needle: estimate pi by dropping ten thousand
needles; show the estimate converge on screen." Day nine slate, first
slot, probability pillar dressed as physical motion, the format the
channel numbers reward (double pendulum 1,160 views, resonance 872,
billiards 776, pendulum wave 723 against 29 to 111 for chart-shaped
probability shorts). Sticks fall and tumble onto a floor of boards one
stick wide; the ones that cross a line light up; two times the stick
count over the crossing count is read out live. Measure the crossing
count, the estimate, its error, the running estimate and the spread of
the estimate over many seeds before scripting.

## Claim

Drop ten thousand sticks on a floor of boards one stick wide, each at a
random spot and angle. Six thousand three hundred fifty cross a line.
Two times ten thousand over that is three point one four nine six,
against pi three point one four one six: off by a quarter of a percent.
A million sticks gave three point one four zero zero. Ten thousand
sticks give two digits, a million give three.

## Evidence

### Measurements

`sims/needles/needles.py --measure-only` with `projects/needles/manifest.json`
(seed 0, 10,000 sticks of 120 px on boards 120 px wide, centre uniform
over the floor, angle uniform over a half turn, a stick crosses when half
its horizontal shadow reaches the nearest board line; numpy RandomState;
log in `media/needles/measure.log`):

- 6,350 of 10,000 sticks cross a line = 63.50% (exact 2/pi = 63.66%,
  one standard deviation 0.48 points)
- estimate 2 x 10,000 / 6,350 = 3.14961; pi = 3.14159; error +0.00801
  = 0.255%
- mean shadow |cos angle| 0.6364 (exact 2/pi = 0.6366)
- running estimate: 2.0000 after 5 sticks, 2.2222 after 10, 2.3529
  after 20, 2.6316 after 50, 2.7397 after 100, 3.0075 after 200, 3.2468
  after 500, 3.1397 after 1,000, 3.1373 after 2,000, 3.1338 after
  5,000, 3.1496 after 10,000; within 0.1 of pi from stick 551 on,
  within 0.01 from stick 9,855 on, reads 3.14 from stick 9,941 on
- check: 1,000,000 sticks at seed 1: 636,943 crossing, estimate
  3.14000, error -0.00159
- check: 10,000 sticks over seeds 0..999: mean estimate 3.1434, sd
  0.0239; within 0.1 of pi 100.0% of seeds, within 0.01 32.9%, reading
  3.14 16.5%; lowest 3.0703, highest 3.2180. Seed 0 is an ordinary
  draw, a third of a standard deviation above the mean

### Production

- `sims/needles/needles.py` renders a floor of boards 120 px wide; sticks
  fall from above with a tumble, land white-to-gold when they cross a
  line and white-to-green when they miss; the landing schedule is
  log-interpolated (20 sticks by 4.5 s, 100 by 8 s, 500 by 12 s, 2,000
  by 16.5 s, all 10,000 by 20.5 s, so 10,000 and 6,350 are on screen
  before "Ten thousand sticks" at 20.6 s); the live readout shows two
  times the sticks over the crossings from stick 10; from 29 s the same
  10,000 sticks replay over 10.5 s for motion while the readout is
  labelled "final estimate from all 10,000 sticks" and holds 3.1496;
  payoff at 30 s. Falling sticks are masked to the floor area so they
  never cross the HUD or the readout
- narration `projects/needles/narration.txt`, 117 words; voice round
  trip passed at 36.99 s after rewording "pi" as "the number pi" (whisper
  heard "pie" four times), "got" as "gave" and "buy" as "give"; music seed
  24 at gain 0.18
- `scripts/compose.sh needles`: final.mp4 40.000 s, 1080x1920, 60 fps,
  h264 + aac, faststart (moov before mdat), 176 MB (the dense stick
  texture defeats the codec at crf 16), mean -15.8 dB, peak -0.2 dB
- inspected: smoke frames at 1, 4, 12, 19, 21, 31, 33 and 39.5 s, both
  contact sheets and full-resolution frames from final.mp4 at 13.9,
  20.4, 30.5 and 36.0 s. Fixed before the final render: falling sticks
  drawn over the HUD text (masked), the replay readout wobbling
  (3.1903, 3.0953) while the narration says "off by a quarter of a
  percent" (readout frozen at the full-run value and relabelled). Final
  composite clean: captions sit in the readout gap at caption_y 0.70,
  10,000 and 6,350 are on screen when spoken, the replay label reads
  "(replay)"

### Published

- Video id: `rY2w4GjBfoc` <https://youtu.be/rY2w4GjBfoc>
- Uploaded private: 2026-09-07 10:00:33 local (07:00:33Z; Pacific quota day
  2026-09-07, clock verified 10:00:19 EEST = 00:00:19 PDT),
  `scripts/yt-upload.py needles`, 176 MB resumable upload done 10:01:04.
- QA gate against `projects/needles/metadata.json` after processing
  succeeded: channel `UCWXsZTvrh_OHkzt6v1xkTsw`, uploadStatus processed,
  processingStatus succeeded, no rejection or failure reason, definition
  hd, embeddable, source stream 1080x1920, title, description, tags (as
  a set), categoryId 27, madeForKids false, selfDeclaredMadeForKids
  false, duration PT41S, private before the flip. 15 of 15 checks pass
  on the publish read at 10:02:26; the first read at 10:01:27 found the
  upload still processing (13 of 15) and one poll at 10:02:12 found it
  processed. Log in `media/needles/publish.log`.
- processingHints empty (faststart MP4).
- Made public: 2026-09-07 10:02:28 +03:00 (07:02:28Z) by videos.update on
  status (privacyStatus public, selfDeclaredMadeForKids false,
  containsSyntheticMedia true, embeddable true). The re-read 15 s later
  returned privacyStatus public, madeForKids false,
  selfDeclaredMadeForKids false, embeddable true.

### Quota for 2026-09-07

Spent 4,963 of the 10,000 daily units on the whole day-nine slate:
4,800 for three `videos.insert`, 3 for the channel-identity check inside
each upload, 150 for three `videos.update`, 7 for gate reads (one per
short while processing, one shared poll, one per short inside the
publish run) and 3 for the confirming re-reads. That leaves room for a
full re-upload plus analytics, as the cadence rule requires. No slot
slipped.
