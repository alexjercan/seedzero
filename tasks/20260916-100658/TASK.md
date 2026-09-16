# Produce short: Rainbow angle, why every rainbow is the same size

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day18

## Goal

Backlog idea (trend research 2026-09-13, task 20260913-212839): "Rainbow
angle: 10,000 parallel rays into a water drop, one internal bounce, red
and violet; measure the exit angle where the rays pile up; expect 42.4
deg for red and 40.6 for violet and no rays past the pile, a dark band,
then the two-bounce pile near 51 deg; exact Snell geometry, no seed."
Day eighteen, first slot. Chosen because it is continuous motion (rays
sweeping through one drop), exact geometry with no time step, and a
plain question with one setup number (ten thousand rays) and one payoff
number (the angle where the rays pile up). Question in the first two
seconds: "Why is every rainbow the same size?"

## Claim

Parallel rays of one colour enter a round drop at every height, bend in,
bounce once off the back, and bend out. Their exit directions pile up at
one angle and none leaves past it. That angle is the rainbow. Every
number below is printed by the sim before the script is written.

## Evidence

### Measurements

(recorded after the measure-only run, before scripting)

`sims/rainbow/rainbow.py` with `projects/rainbow/manifest.json` (10,000
parallel rays of each colour enter one round drop at evenly spaced
heights b = (k + 1/2) / 10,000 drop radii from the centre to the top
edge, bend in by vector Snell, bounce once off the back, bend out; exit
angle measured from the antisolar direction; red n = 1.331, violet n =
1.343; exact geometry, no time step, no seed; log in
`media/rainbow/measure.log`):

- red: the exit angles pile up at 42.37 degrees (closed form 4 asin(sin
  i0 / n) - 2 i0 with cos^2 i0 = (n^2 - 1) / 3 gives 42.370, incidence
  59.53 degrees), reached by ray 8,619 at height 0.8619 of the radius;
  1,196 of 10,000 rays leave within one degree of it and 375 within a
  tenth of a degree; 0 rays leave past 42.370 degrees; the centre ray
  leaves at 0.00 degrees and the edge ray at 15.95; the tallest
  0.5-degree bin (42.0 to 42.5) holds 724 rays
- red, two bounces: the pile is at 50.37 degrees (closed form 50.365);
  0 rays of either kind leave between 42.37 and 50.37 degrees (the dark
  band)
- violet: the pile is at 40.65 degrees (closed form 40.646, incidence
  58.83 degrees), reached by ray 8,557 at height 0.8557 of the radius;
  1,237 of 10,000 rays within one degree, 388 within a tenth; 0 rays
  past 40.646; centre ray 0.00 degrees, edge ray 13.63; tallest bin
  (40.0 to 40.5) holds 523 rays
- violet, two bounces: 53.48 degrees (closed form 53.478); 0 rays
  between 40.65 and 53.48
- the two piles are 1.72 degrees apart; the vector trace agrees with
  the angle formula 4 r - 2 i on the peak ray to 1e-9 degrees (asserted)

Narration numbers: ten thousand rays (setup), forty two degrees
(payoff). The violet pile at forty degrees closes the story as the
inner edge of the band; the counts within one degree, the two-bounce
piles and the dark band go to the description.

### Production

- `projects/rainbow/narration.txt`: 115 words; `scripts/voiceover.sh`
  round trip passed on the first wording ("ok: transcript matches
  narration (34.005624s)", `media/rainbow/voice.log`); voice ends at
  34.61 s of video
- timing (`scripts/voice-timing.py`, +0.6 s offset): "Rays near the
  middle come straight back, higher up, they leave wider and wider,
  until the angle stops at 42 degrees and turns back" 12.85 to 19.87 s
  against the red sweep reaching its pile at 18.96 s (red rays sweep 0
  to 22 s); "Light piles up where it stops, and not one ray gets past
  it" 19.87 to 23.58 s with the "1,196 of 10,000 rays within 1 degree"
  readout from 22 s; "Violet light bends a little more" 23.58 to 25.58 s
  against the violet sweep 23.5 to 28.5 s (its pile at 27.8 s, moved
  earlier from 24 to 31 s after a first timing read put the words
  before the pile); "so its pile sits at 40 degrees, just inside the
  red. Why is every rainbow the same size?" 25.58 to 31.05 s; "because
  light leaving a drop piles up at 42 degrees" 31.05 to 34.61 s with
  the payoff card from 31.0 s
- text widths measured with PIL before rendering: overlay 825 px,
  title lines 681 and 467, readout 866, chart label 282, sun label 148,
  payoff lines 826, 634, 655 and 899; the end-of-sweep readout "red:
  1,196 of 10,000 rays within 1 degree of 42.4 degrees" is 976 px,
  inside the frame with 52 px margins, accepted after inspection at
  22.5 s; a first readout with the colour name (1,007 px) was cut
- layout fixes from smoke frames: the first tone map saturated the ray
  haze into solid blocks, so the density scale was raised and the rays
  fade out between y 990 and 1110 above the histogram; the drop moved
  up to (680, 640) radius 270; the chart label and peak labels share
  the row at y 1146 so nothing collides
- footage: `sims/rainbow/rainbow.py` rendered 40.00 s at 60 fps,
  1080x1920 (`media/rainbow/render.log`); rays are splatted
  additively so the pile at 42.4 degrees shows as a bright edge
- compose: `scripts/compose.sh rainbow` (music seed 53, gain 0.18,
  captions at 0.75); final.mp4 40.000 s, h264 1080x1920 + aac; mean
  volume -17.4 dB, peak -0.2 dB (`media/rainbow/compose.log`)
- inspected full-resolution frames of the composed final at 0.02, 1.5,
  5.0, 12.0, 19.0, 22.5, 26.0, 28.5, 31.5, 34.0 and 39.95 s
  (`media/rainbow/frame-*.png`, rows in `row-a.png` and `row-b.png`)
  and the contact sheet: question on screen for the first 2.4 s with
  the first ray already moving, the readout follows the sweep, the
  42.4 degree label appears at 19 s as the words land, violet's 40.6
  label at 28 s, the payoff card from 31 s in four lines under the
  captions, crossfade back to frame 0 at the end; approved
- `projects/rainbow/metadata.json`: title 100 characters, category 27,
  private, altered-content disclosure true, not made for kids; the
  description carries the closed form, the counts within one degree,
  the two-bounce piles and the dark band

### Published

- quota check before the insert: clock 2026-09-16T10:25:57+03:00 EEST; zero upload attempts
  recorded since the 10:00 EEST boundary; this is insert attempt 1 of
  the hard cap of 5
- attempt 1 recorded at 2026-09-16T10:25:57+03:00, video name rainbow, before running
  `scripts/yt-upload.py rainbow`
- upload: `scripts/yt-upload.py rainbow` ran 10:25:57 to 10:26:04 EEST,
  token verified to see only the Seed Zero channel, video id
  ZC1euLz5dXA, private (`media/rainbow/upload.log`)
- gate: `scripts/yt-qa.py rainbow ZC1euLz5dXA` at 2026-09-16T10:30:50+03:00,
  15 of 15 pass (processed, succeeded, hd, 1080x1920, title, description,
  tags, category 27, not for kids, PT41S for the 40.000 s file, private);
  containsSyntheticMedia reads absent as on every earlier upload
  (`media/rainbow/qa.log`)
- publish: `scripts/yt-qa.py rainbow ZC1euLz5dXA --publish` re-ran the gate
  (15 of 15) and set the video public at 2026-09-16T10:33:37+03:00; the
  re-read after 15 s shows privacyStatus public, madeForKids false,
  embeddable true; public at https://youtu.be/ZC1euLz5dXA

### Quota

- attempt 1 of the hard cap of 5 for the quota day that began
  2026-09-16T10:00 EEST; cost 1 + 1,600 + 1 + 1 + 50 + 1 = 1,654 units;
  day total after one attempt 1,654 units
