# Produce short: Fourier square from circles, does the bump go away

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day13

## Goal

Backlog idea "Fourier square from circles: spinning circles draw a square
wave; measure the peak overshoot at 5, 50 and 500 circles; expect the
peak eighteen percent above the flat top every time (Gibbs), with the
drawing as a seamless loop." Day thirteen, third slot, produced on the
foreground guidance that the day must reach three published shorts.
The Kelvin wake was tried first as the stronger physics-motion idea and
failed its feasibility measurement (scratchpad prototype, steady linear
deep-water wake of a 1 m Gaussian pressure patch computed spectrally):
the wake angle measured from the field is not the same at every speed,
amplitude peaks along rays at 18.8, 10.3 and 8.8 deg for 4, 8 and 12
m/s (the Rabaud-Moisy narrowing of the visible wake at high Froude
number) and outer-crest fits of 19.7, 19.1 and 13.2 deg, so the
narrated claim would depend on a boat-size definition; recorded in
docs/niche.md, slot not committed. The Fourier square is the strongest
remaining measurable idea: the overshoot is exact, deterministic, and
the epicycle drawing is continuous motion that loops exactly. Langton's
ant (grid automaton, the weakest retaining format) stays in the
backlog. One plain question inside two seconds: "Add more circles. Does
the bump go away?" One setup number (5 circles, then 50), one payoff
number (the bump stays 18 percent). Every number below is printed by
the sim before the script is written.

## Claim

Spinning circles chained together draw a square wave. Add more circles
and the drawing hugs the square more closely, but the pen still
overshoots the top by about eighteen percent of the height: five
circles, fifty, five hundred, the bump gets thinner and never shorter.

## Evidence

### Measurements

(recorded after the measure-only run, before scripting)

`sims/fourier/fourier.py` with `projects/fourier/manifest.json` (partial
sums of the square wave of height 1 evaluated term by term, golden
section search for the highest point, Simpson quadrature for Si(pi),
deterministic, no seed; log in `media/fourier/measure.log`):

- limit for infinitely many circles: (2/pi) Si(pi) = 1.178980, 17.90%
  above the flat top (the Wilbraham-Gibbs constant)
- 5 circles (harmonics 1 to 9): highest point 1.182328, 18.23% above the
  flat top, 400.0 ms after the jump at 8 s per period; the bump is back
  at the top level 621.2 ms after the jump; RMS gap to the square 0.2010
- 50 circles (harmonics 1 to 99): highest point 1.179013, 17.90% above,
  40.0 ms after the jump, back at the top level at 62.3 ms; RMS gap
  0.0637
- 500 circles: 1.178980, 17.90%, 4.0 ms, back at 6.2 ms; RMS gap 0.0201
- 5,000 circles: 1.178980, 17.90%, 0.4 ms, back at 0.6 ms; RMS gap
  0.0064
- from 5 to 50 circles the bump got 10.0x thinner and its height went
  from 18.23% to 17.90%; the RMS gap shrinks like one over the square
  root of the circle count while the peak never drops below 17.90%
- payoff: 18% too high at 5, 50 and 500 circles (18.23, 17.90, 17.90
  rounded); the bump gets thinner, never shorter

Narration numbers: five circles, then fifty (setup), eighteen percent
(payoff), with five hundred and five thousand as the same eighteen.

### Production

- `sims/fourier/fourier.py` renders two panels of the same square wave:
  the epicycle chain on the left (circle k has radius (4/pi)/(2k+1)
  times the 100 px wave height and turns 2k+1 times per 8 s period),
  the pen, a connector to the trace start, and the exact partial sum
  scrolling right at 300 px per period over the faint target square; a
  dashed grey line at the flat top and a dashed coloured line at the
  measured peak; label "5 circles" / "50 circles" and the readout "peak
  18% too high" per panel; a ring flash at the pen at each measured
  peak after a rising jump; the question "Add more circles. Does the
  bump go away?" for the first 2.4 s; "500 circles: peak 18% too high"
  and "5,000 circles: peak 18% too high" appear at 21.1 and 22.9 s as
  they are spoken; payoff "does the bump go away? no / 5, 50 or 500
  circles: 18% too high" from 27.0 s; five exact periods in 40 s, so
  the drawing loops exactly and the 0.6 s crossfade only carries the
  text
- layout fixes from smoke frames: at each jump the chain lunges
  sideways by about (2A/pi)(ln 2N + 0.58), so the 50-circle chain left
  the frame on the left; the wave height went from 130 to 100 px, the
  chain centre from x 200 to 400 and the trace start from 660 to 740 so
  both lunges stay inside the frame and short of the trace
- narration `projects/fourier/narration.txt`, 92 words; round trip
  passed at 32.020 s (log `media/fourier/voice.log`) after rewording:
  "chases" (heard "cheeses") became "follows", "Five thousand:
  eighteen." (written back as 5018) became "Five thousand circles:
  eighteen again."; hooks considered: "Add more circles. Does the bump
  go away?" (kept), "Can spinning circles draw a square?" (no
  measurable answer), "Why does this wave overshoot?" (asks for the
  mechanism before the picture shows it)
- caption schedule (chunks with the 0.6 s offset, voice 32.02 s): "by
  eighteen percent" 8.61 to 9.65 s with the first 5-circle peak flash
  at 8.4 s; "Fifty circles. Ten times more." 9.65 to 11.39; "But watch
  the pen at each jump" 15.91 to 18.35 against the rising jump at 16.0
  s; "Five hundred circles: eighteen percent" 21.13 to 22.88 as the 500
  line appears at 21.1; "Five thousand circles: eighteen again" 22.88
  to 24.62 as the 5,000 line appears at 22.9; "Does the bump go away?
  No." 27.05 to 29.14 with the payoff on screen from 27.0; voice ends
  32.62 s; music seed 43 at gain 0.18
- text widths measured before rendering: overlay 652 px, title lines
  550 and 790 px, labels 262 and 301 px, readouts 504 px, extra lines
  693 and 736 px, payoff lines 630 and 758 px after shortening a 978 px
  first draft
- compose: `media/fourier/final.mp4` 40.000 s, 1080x1920, 60 fps, h264
  crf 18 with faststart, aac 192k, 8.9 MB; audio mean -16.9 dB, peak
  -0.0 dB after the limiter (log `media/fourier/compose.log`)
- inspection (contact sheet 8x5 at 1 fps plus full-resolution frames at
  0.5, 2.8, 8.4, 12.0, 16.4, 21.5, 23.5, 28.0, 33.0 and 39.95 s): title
  question on screen from frame one to 2.4 s; both panels labelled with
  "N circles" and "peak 18% too high" in their colours; the caption band
  at 0.49 sits between the panels and never touches a chain or trace;
  the 5-circle trace shows visible ripples and the 50-circle trace a
  thin spike at each jump, both reaching the measured peak guide; the
  500 and 5,000 readouts appear at 21.1 and 22.9 s under the lower
  panel; the payoff "does the bump go away? no" is on screen from 27.0
  s while the caption "Does the bump go away?" is spoken; the horizontal
  lunge of both chains stays inside the frame; loop crossfade closes on
  the title (first versus last frame mean pixel difference 0.45 of 255)

### Published

- uploaded private with `scripts/yt-upload.py fourier` at 10:46:18 to
  10:46:23 EEST (publishedAt 2026-09-11T07:46:19Z), video iIWkxb6zYqE,
  https://youtu.be/iIWkxb6zYqE (log `media/fourier/upload.log`)
- gate read 1 at 10:46:37: 11 of 15 while processing (uploadStatus
  uploaded, processingStatus processing, definition sd, duration P0D);
  read 2 at 10:47:39: 15 of 15 (processed, succeeded, hd, 1080x1920,
  PT41S, Seed Zero channel, title, description and tags match, category
  27, not for kids, private) (log `media/fourier/qa.log`)
- published with `--publish` at 10:47:53 EEST after a fresh 15 of 15
  read; re-read privacyStatus public, embeddable, madeForKids false,
  selfDeclaredMadeForKids false (log `media/fourier/publish.log`)

### Quota

- this short: 1,600 insert + 1 + 1 gate reads + 52 publish run (1 read,
  50 update, 1 re-read) = 1,654 units; day total 4,963 of 10,000 after
  the gyroscope top (1,655) and Lorenz (1,654); three insert attempts
  today against the hard cap of five, so one QA-failure re-upload plus
  analytics reads still fit
