# Produce short: Mach cone, where is the jet when you hear it

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day17

## Goal

Backlog idea (trend research 2026-09-13, task 20260913-212839): "Mach
cone: a sound source emitting a ring every 0.1 s at Mach 0.5, 1 and 2;
measure the half angle of the ring envelope; expect no cone at 0.5, a
flat wall at 1 and exactly 30.0 deg at 2; exact circles, loops; the
cheap replacement for the Kelvin wake." Day seventeen, second slot.
Chosen because it is continuous motion in three same-input panels, exact
geometry with no time-step question, and a plain question a listener
on the ground answers: where is the jet when you first hear it? One
setup number (twice the speed of sound) and one payoff number (how far
past the listener the jet is when its sound arrives). Question in the
first two seconds: "Where is the jet when you hear it?"

## Claim

A jet flying at twice the speed of sound outruns its own sound. A
person one hundred metres to the side hears nothing until the cone of
piled-up sound rings sweeps over them, and by then the jet is already
well past. Every number below is printed by the sim before the script
is written.

## Evidence

### Measurements

(recorded after the measure-only run, before scripting)

`sims/machcone/machcone.py` with `projects/machcone/manifest.json`
(three jets at Mach 0.5, 1 and 2, speed of sound 343 m/s, each sending
out a ring of sound every 0.1 s from 0.5 s before the video; every ring
an exact circle growing at 343 m/s about its emission point; a listener
100 m to the side of each path; the jets start 250, 500 and 1,000 m
before the listener so all three pass it at 1.4577 s; exact geometry,
no time step, no seed; log in `media/machcone/measure.log`):

- Mach 0.5 (171.5 m/s): the first sound reaches the listener at 0.5213
  s, 0.9364 s before the jet passes abeam, when the jet is 160.6 m
  before the listener; the first drawn ring (sent at -0.5 s) arrives
  at the same moment
- Mach 1 (343 m/s): the first sound reaches the listener at 1.4793 s,
  0.0216 s after abeam, when the jet is 7.4 m past; same for the first
  drawn ring
- Mach 2 (686 m/s): the first sound reaches the listener at 1.7102 s,
  0.2525 s after abeam, when the jet is 173.2 m past; the first drawn
  ring (sent at 1.4 s) arrives at 1.7136 s with the jet 175.5 m past
- cone at Mach 2: half angle fitted to the upper hull of the union of
  the drawn rings behind the jet at 2.5 s: 30.00 degrees (a plain
  least-squares fit of the scalloped envelope gave 30.53 before the
  hull fit was written); exact asin(c / v) = 30.000 degrees; a
  listener 100 m to the side is first reached when the jet is 100 /
  tan(30 deg) = 173.2 m past
- check, listener 1,000 m to the side at Mach 2: the jet is 1,732 m
  past when the first sound arrives (closed form 1,732 m)
- wall at Mach 1: the front edges of all 32 rings are within 0.000000
  m of the jet's nose
- lead at Mach 0.5: at the end of the run the oldest ring's front is
  543.1 m ahead of the jet; every ring leads it by (343 - 171.5) m per
  second of age
- the 160.6 m and 7.4 m figures depend on the pre-roll and start
  distances; the 173.2 m figure does not (stated in the description)

Narration numbers: one hundred meters to the side (setup), one hundred
seventy three meters past (payoff). The 30 degrees is drawn on the
cone and goes to the description.

### Production

- `projects/machcone/narration.txt`: 122 words; `scripts/voiceover.sh`
  round trip passed on the first wording ("ok: transcript matches
  narration (35.874830s)", `media/machcone/voice.log`); voice ends at
  36.47 s of video
- timing (`scripts/voice-timing.py`, +0.6 s offset): "so the listener
  hears it coming" 13.3 to 16.4 s, "hears it as it passes" 19.1 to
  21.3 s, "and the listener hears nothing until that edge arrives" 27.2
  to 31.5 s, "Where is the jet when you hear it? at twice the speed of
  sound" from about 29.5 s, "already 173 meters past you" 33.3 to 36.5
  s; the slow motion was set to 1/16 so the Mach 2 listener hears the
  boom at 27.36 s of video (Mach 0.5 at 8.34 s, Mach 1 at 23.67 s, the
  jets abeam at 23.32 s) and the payoff card comes at 31.0 s
- text widths measured with PIL before rendering: a first overlay was
  999 px and the third payoff line 1,129 px; the overlay was cut to
  "same sound | same listener | no seed" (713 px) and the payoff split
  into four lines (771, 826, 584 and 531 px); title lines 505 and 565
  px, panel labels 427, 347 and 455 px, listener tag 370 px, clock 263
  px; all under 950 px
- layout fix before the final render: the clock's speed label (y 250)
  ran into the first panel's label, so the three panels were moved to
  start at y 290 (370 px each, ending at 1,402, clear of the caption
  band at 1,440)
- footage: `sims/machcone/machcone.py` rendered 40.00 s at 60 fps,
  1080x1920 (`media/machcone/render.log`); the camera follows each jet;
  the Mach 2 panel draws the exact cone lines and the 30 degree arc
- compose: `scripts/compose.sh machcone` (music seed 52, gain 0.18,
  captions at 0.75); final.mp4 40.000 s, h264 1080x1920 + aac; mean
  volume -15.9 dB, peak -0.0 dB (`media/machcone/compose.log`)
- inspected full-resolution frames at 0.02, 1.5, 5.0, 8.5, 15.0, 23.5,
  27.5, 29.0, 31.5, 36.0 and 39.95 s (`media/machcone/frame-*.png`,
  rows in `row-a.png` and `row-b.png`) and the contact sheet: question
  on screen for the first 2.4 s with rings already streaming, the three
  listeners turn gold on their own panels at 8.3, 23.7 and 27.4 s with
  the "hears it: jet ... m away / past" tags, the cone lines run along
  the ring envelope, payoff card from 31.0 s in four lines above the
  frame bottom, crossfade back to frame 0 at the end; approved
- `projects/machcone/metadata.json`: title 87 characters, category 27,
  private, altered-content disclosure true, not made for kids;
  description carries the three arrival times, the cone fit and the 1
  km listener check


### Published

- quota check before the insert: clock 2026-09-15T10:38:12+03:00 EEST; one upload
  attempt recorded since the 10:00 EEST boundary (bulletdrop at
  10:34:02, private, awaiting its gate read); this is insert attempt 2
  of the hard cap of 5
- attempt 2 recorded at 2026-09-15T10:38:12+03:00, video name machcone, before running
  `scripts/yt-upload.py machcone`
- upload: `scripts/yt-upload.py machcone` ran 10:38:12 to about 10:38:20
  EEST, token verified to see only the Seed Zero channel, video id
  OtTBM61o6p4, private (`media/machcone/upload.log`)
- gate: `scripts/yt-qa.py machcone OtTBM61o6p4` at 2026-09-15T10:40:29+03:00,
  15 of 15 pass (processed, succeeded, hd, 1080x1920, title, description,
  tags, category 27, not for kids, PT41S for the 40.000 s file, private);
  containsSyntheticMedia reads absent as on every earlier upload
  (`media/machcone/qa.log`)
- publish: `scripts/yt-qa.py machcone OtTBM61o6p4 --publish` re-ran the gate
  (15 of 15) and set the video public at 2026-09-15T10:44:58+03:00; the
  re-read after 15 s shows privacyStatus public, madeForKids false,
  embeddable true; public at https://youtu.be/OtTBM61o6p4

### Quota

- attempt 2 of the hard cap of 5 for the quota day that began
  2026-09-15T10:00 EEST; cost 1 + 1,600 + 1 + 1 + 50 + 1 = 1,654 units;
  day total after two attempts 3,308 units
