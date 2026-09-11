# Produce short: Gyroscope top, spin it faster and it circles slower

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day13

## Goal

Backlog idea "Gyroscope top: two identical tops with the same tilt, one
spinning three times faster; measure the precession periods (expect a
3:1 ratio against the exact mgr / (I omega)) and the fall time of a top
spun below the critical rate." Day thirteen, first slot. Chosen from the
morning briefing evidence (web/data refreshed 08:01: the day-12 physics
pieces stand at 526, 216 and 121 views, day-11 tautochrone and
Dzhanibekov at 943 and 937, while the grid and counter formats sit at 2
to 316) over the other two proposed ideas: Langton's ant is a grid
cellular automaton (the format of the weakest retainers) and the Fourier
square is a maths drawing (pi race 211, Benford 94). The top is a
two-panel same-input physics comparison with continuous motion, the
channel's measured winner, and its surprise is checkable with one number
in and one number out. Question in the first two seconds: "Spin a top
three times faster. Does it circle faster?" One setup number (three
times the spin), one payoff number (the lap time of the faster top
against the slower one). Every number below is printed by the sim
before the script is written.

## Claim

Spin a top three times faster. Does it circle faster? The same top twice
at the same lean. One spins three times faster than the other. The
faster top circles slower, and about three times slower: its lap takes
about three times as long. The extra spin slows the circle.

## Evidence

### Measurements

`sims/gyrotop/gyrotop.py` with `projects/gyrotop/manifest.json` (heavy
symmetric top, Lagrange's equations in theta, phi, psi with p_phi and
p_psi conserved, RK4 at 2,400 steps per second, g 9.81, mass cancels,
deterministic, no seed; log in `media/gyrotop/measure.log`):

- top: solid disc radius 2.0 cm, thickness 0.6 cm, centre 1.2 cm above
  the tip; per unit mass I1 2.470e-4, I3 2.000e-4 m^2, g r 0.11772; lean
  30 deg from the vertical, both tops started in steady precession
- thresholds: standing straight up is stable above 8.58 turns a second;
  released from rest at 30 deg the top swings past horizontal below 6.52
  turns a second
- slow top, 30 turns a second (1,800 rpm), I3 w3 3.76x the threshold:
  steady precession 3.1800 rad/s, period 1.9758 s (fast-top
  approximation m g r / (I3 w3): 2.0122 s); measured 20 laps in 40 s,
  first lap at 1.9758 s, every lap 1.9758 s; lean stays at 30.0000 deg;
  energy drift 1e-16; 1,200 turns in 40 s
- fast top, 90 turns a second (5,400 rpm), 11.27x the threshold: steady
  precession 1.0429 rad/s, period 6.0245 s (approximation 6.0365 s);
  measured 6 laps in 40 s, first lap at 6.0245 s, every lap 6.0245 s;
  lean stays at 30.0000 deg; energy drift 0; 3,600 turns in 40 s
- ratio of lap times fast over slow: 3.0491 (the fast-top approximation
  gives exactly 3; the exact steady root adds the I1 cos(theta) W^2
  term)
- check, step halving to 4,800 steps per second: first laps 1.9758 and
  6.0245 s, unchanged
- check, full rigid-body run (Euler's equations in the body frame with
  the gravity torque about the tip, unit quaternion, 14,400 steps per
  second): first laps 1.9758 and 6.0245 s, lean 30.000 deg throughout,
  vertical angular momentum drift 1.6e-11 and 1.3e-9
- check, released from rest at the same lean (no starting precession):
  slow top 10 laps in 20 s, average lap 1.9756 s, lean wobbles between
  30.00 and 31.24 deg; fast top 3 laps in 20 s, average lap 6.0238 s,
  wobble 30.00 to 30.13 deg; the steady start changes nothing narrated
- check, too little spin from rest at the same lean: 5 turns a second
  passes horizontal at 0.097 s (lean reaches 112.8 deg), 6 turns a
  second at 0.108 s (97.9 deg), 7 turns a second stays up (lean wobbles
  between 30.0 and 82.7 deg over 6 s)
- payoff: 2.0 s a lap became 6.0 s a lap; three times the spin, about
  three times slower (3.05)

Narration numbers: three times faster (setup), two point zero seconds a
circle became six point zero (payoff), three times slower (3.05 rounded).

### Production

- `sims/gyrotop/gyrotop.py` renders two panels of the same top on a table
  seen from 22 deg above: a solid disc with a stem and a handle knob, the
  dotted ring the knob sweeps at the nominal lean with a white lap-start
  mark, a header label ("spins 30 times a second"), a rolling "turns"
  counter (the spin times the clock), a "laps" counter that steps at each
  measured lap and the lap time readout after the first lap; the question
  "Spin a top 3x faster. Does it circle faster?" is drawn for the first
  2.4 s; a gravity arrow at the disc centre from 15.4 s and a sideways
  arrow along the knob's motion from 17.4 s, both off at 25.0 s; payoff
  from 26.0 s ("does it circle faster? no, slower / 2.0 s a lap became
  6.0 s a lap") held to the end; the last 0.6 s crossfade to frame 0 so
  the video loops (lap times 1.9758 and 6.0245 s share no common
  multiple near 40 s)
- narration `projects/gyrotop/narration.txt`, 104 words; round trip
  passed at 34.319 s (log `media/gyrotop/voice.log`) after rewording:
  the opening "Spin" (heard "then", then "pin") became "Take a top and
  spin it", "turns that pull sideways" (heard "pole") became "turns that
  fall sideways", sentence-final "six point zero." (the zero was dropped)
  became "six point zero seconds a circle", and "has not finished its
  first circle" (spoken at 13 s, false after the fast top's first lap at
  6.0 s) became "is clearly slower"; hooks considered: "Spin a top three
  times faster. Does it circle faster?" (kept), "Which top circles
  faster, the fast spinner or the slow one?" (two things to hold),
  "Faster spin, faster circles? This top says no." (spoils the answer)
- caption schedule (chunks with the 0.6 s offset): "Gravity pulls the
  leaning top down" 15.45 to 17.43 s, "The spin turns that fall
  sideways" 17.43 to 19.74, "slows down" ends 25.02, "Does it circle
  faster? No, slower." 25.02 to 27.00, "became six point zero" 28.98 to
  29.97, voice ends 34.92 s; music seed 37 at gain 0.18
- compose: 2,400 frames at 60 fps, final.mp4 40.000 s, 1080x1920, h264,
  aac, faststart; mean volume -16.1 dB, peak -0.0 dB
- text widths measured before rendering: overlay 595 px, title lines
  637 and 652 px, labels 542 px, turns readout 331 px, lap readouts 279
  px, laps 211 and 250 px, payoff lines 709 and 669 px
- inspection: smoke frames at 0.5, 1.0, 3.0, 9.5, 12.0, 20.0, 26.0 and
  39.9 s (the "gravity" label sat on the disc rim without contrast, so
  it got a dark stroke), then the contact sheet plus full-resolution
  frames from final.mp4 at 0.5, 2.8, 6.5, 12.0, 16.2, 18.6, 26.6, 30.5
  and 39.95 s; the finals show the question and the overlay with both
  tops in motion at 0.5 s, "laps: 1, 2.0 s a lap" on the slow top by
  2.8 s, the fast top's first lap and "6.0 s a lap" at 6.5 s, the
  gravity and sideways arrows with their captions, the payoff on screen
  while "No, slower" is spoken at 26.6 s, and the title back over the
  tops at 39.95 s

### Published

- clock before upload: 10:00:22 EEST 2026-09-11 = 00:00:22 PDT, the
  fresh Pacific quota day (the monitor fired at 10:00:13); yesterday's
  Pacific day had already spent four insert attempts, so the upload
  waited for the reset to keep room for a re-upload
- uploaded private to the Seed Zero channel (UCWXsZTvrh_OHkzt6v1xkTsw)
  via `scripts/yt-upload.py` between 10:00:26 and 10:00:39 EEST: video
  AcMvMjpwBLc, publishedAt 2026-09-11T07:00:35Z = 10:00:35 EEST (log in
  `media/gyrotop/upload.log`)
- QA gate (`scripts/yt-qa.py`, videos.list): 9 of 15 at 10:00:43 EEST
  while YouTube was still processing (uploadStatus uploaded, sd, no
  source size, empty tags, duration P0D); 15 of 15 at 10:01:37 EEST:
  Seed Zero channel, uploadStatus processed, processingStatus succeeded,
  no rejection, HD, embeddable, 1080x1920, title, description, the nine
  tags as a set, categoryId 27, madeForKids false,
  selfDeclaredMadeForKids false, duration PT41S (40.000 s rounds up),
  private
- published (videos.update privacyStatus public, containsSyntheticMedia
  true, embeddable true) at 10:01:47 EEST after a third clean 15 of 15
  read in the same run; re-read 15 s later: public, madeForKids false,
  selfDeclaredMadeForKids false, embeddable true (log in
  `media/gyrotop/publish.log`)
- public URL: https://youtu.be/AcMvMjpwBLc

### Quota

- this short: 1,600 (insert) + 1 (channel check) + 3 (gate reads) + 50
  (publish) + 1 (re-read) = 1,655 units of 10,000 on the Pacific day
  2026-09-11; one insert attempt today against the hard cap of five,
  which leaves room for two more uploads plus a re-upload and analytics
  reads
- the day 13 slate was one short: the briefing evidence supported one
  production-ready physics-motion idea, and the Fourier square and
  Langton's ant were held back as weaker formats rather than shipped
