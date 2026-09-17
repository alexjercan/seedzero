# Produce short: Bead on a spinning hoop, where does the bead settle

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day19

## Goal

Backlog idea (trend research 2026-09-16, task 20260916-100924):
"Bead on a spinning hoop: a bead on a 20 cm hoop spun at 60 rpm beside
the same hoop at 100 rpm; measure where the bead settles; expect the
slow bead to fall back to the bottom and the fast bead to climb and
hold at 63.6 degrees (cos theta = g / (omega^2 R), threshold 66.9 rpm;
134 rpm gives 75.5 degrees); light damping; deterministic, no seed."
Day nineteen, third slot. Chosen because it is continuous motion, a
two-panel same-input comparison (the same hoop and bead at two spin
rates), with one plain question, one setup number (the spin rate) and
one payoff number (the angle the bead holds) that a closed form checks.
Question in the first two seconds: "Spin the hoop. Where does the bead
settle?"

## Claim

A bead on a spinning hoop stays at the bottom until the hoop spins
fast enough, then climbs to a fixed angle and holds it. Every number
below is printed by the sim before the script is written.

## Evidence

### Measurements

(recorded after the measure-only run, before scripting)

`sims/hoopbead/hoopbead.py` with `projects/hoopbead/manifest.json` (a
bead on a vertical hoop of radius 20 cm spinning about its vertical
diameter, g = 9.80665 m/s^2, damping c = 0.8 per second, chosen after a
first run at 0.6 per second left both beads 13 to 14 s to come back
within 0.5 degrees of their rest angles after the nudge and the fast
bead reading 63.32 degrees at 40 s, still wobbling; two hoops, both at
rest with the bead 2 degrees off the bottom, spin rate ramped linearly
from 1 s over 6 s to 60 rpm (slow) and 100 rpm (fast); nudge: 25
degrees added to theta instantly at 22 s, away from the bottom on the
bead's own side, theta' unchanged, on both beads; RK4 at 600 steps per
second, dt = 1.67e-3 s, for 40 s; deterministic, no seed; log in
`media/hoopbead/measure.log`):

- tipping rate sqrt(g / R) = 7.0024 rad/s = 66.87 rpm; the fast hoop
  crosses it at 5.012 s of the ramp; the slow hoop's 60 rpm is 0.897 of
  it (g / (omega^2 R) = 1.2420 > 1, no rest angle above the bottom)
- closed form arccos(g / (omega^2 R)): 63.44 degrees at 100 rpm (omega =
  10.4720 rad/s); 75.58 degrees at 134 rpm
- fast bead (100 rpm): lifts off (theta past 5 degrees) at 6.353 s with
  the hoop at 89.2 rpm, 1.341 s after the tipping rate; first reaches
  its rest angle 63.44 degrees at 6.807 s; overshoots to 86.45 degrees
  at 6.957 s; stays within 0.5 degrees of its final angle from 16.527 s;
  holds 63.42 degrees at 40 s (-0.017 against the closed form); 63.45
  degrees just before the nudge; it lifted off on the left half of the
  hoop, the side its residual swing was on when the hoop passed the
  tipping rate (the equation is symmetric in theta; the sim tracks the
  signed angle and every measurement is the angle away from the bottom)
- slow bead (60 rpm): -0.032 degrees at the end of the ramp (7 s);
  largest excursion after the ramp and before the nudge 0.147 degrees at
  7.53 s; largest angle over the whole ramp 2.000 degrees (the start);
  within 0.5 degrees of the bottom from 3.272 s; holds 0.011 degrees at
  40 s
- nudge on the slow bead: from 0.00 to 25.00 degrees at 22 s; swings
  back through the bottom to 17.59 degrees on the other side at 22.93 s;
  within 5 degrees of the bottom from 26.06 s, within 0.5 degrees from
  31.313 s (9.31 s after the nudge)
- nudge on the fast bead: from 63.45 to 88.45 degrees at 22 s; swings
  back through its rest angle to 35.65 degrees at 22.36 s; within 5
  degrees of its final angle from 26.19 s, within 0.5 degrees from
  31.902 s (9.90 s after the nudge)
- small swings about the slow bead's rest angle (the bottom): closed
  form sqrt(g / R - omega^2) = 3.091 rad/s = 0.492 Hz (period 2.033 s,
  damped 2.050 s); measured period after the nudge 2.043 s; amplitude
  halves every 1.73 s
- small swings about the fast bead's rest angle: closed form omega sin
  theta_eq = 9.367 rad/s = 1.491 Hz (period 0.671 s); measured period
  after the nudge 0.671 s
- check at 134 rpm (not drawn): holds 75.58 degrees at 40 s against the
  closed form 75.58; lifts off at 4.885 s
- check at half the time step (1200 steps per second): the fast bead
  lifts off at 6.353 s, settles from 16.526 s and holds 63.42 degrees at
  40 s (+0.0000 against the full step)

Narration numbers: one hundred turns a minute (setup), sixty three
point four degrees (payoff, the 63.42 the fast bead holds at 40 s,
shown as 63.4 on the card and the readout). The tipping rate, the
slow hoop's 60 rpm, the lift-off time, the overshoot, the swing rates,
the 134 rpm angle and the checks go to the description.

### Production

- narration (written in the resumed session at 15:40 EEST): three hooks
  tried, "Spin the hoop. Where does the bead settle?" (the title),
  "Spin the hoop faster. Where does the bead sit?" and "Why does this
  bead climb the hoop?"; the first was kept because the payoff answers
  it in the same words; `projects/hoopbead/narration.txt`, 117 words;
  the setup number is one hundred turns a minute, the payoff sixty
  three point four degrees; the slow hoop's 60 stays on screen only
- voice: `scripts/voiceover.sh projects/hoopbead/narration.txt` failed
  the round trip twice on wording, never on a number: "part way" was
  heard as "partway" (now "partway") and "Slow hoop," at the start of a
  phrase was heard as "flow" twice (now "On the slow hoop,"); then the
  first word "Spin" at the start of the audio was heard as "Thin" (the
  opener is now "A bead on a spinning hoop. Where does the bead
  settle?", the question unchanged); the third run passed (117 words,
  35.02 s, ends at 35.62 s of the 40 s video, 3.3 words/s); timing
  (`scripts/voice-timing.py`, +0.6 s offset): "The fast bead lifts off,
  swings wide, and settles partway up" 9.17 to about 12.4 s after the
  lift-off at 6.35 s while the bead still swings (settled from 16.5 s),
  "Now nudge both beads" 21.15 to about 22.5 s over the nudge at 22.0 s,
  "So where does the bead settle? On the slow hoop, at the bottom"
  inside 26.19 to 31.75 s with the payoff card from 30.0 s, "On the
  fast hoop, sixty three point four degrees up" 31.75 to 34.64 s once
  the bead is within 0.5 degrees (31.90 s) and the "holds" label is on,
  "and it holds" 34.64 to 35.62 s; log in `media/hoopbead/voice.log`
- footage: `sims/hoopbead/hoopbead.py` (no arguments) wrote
  `media/hoopbead/footage.mp4`, 40.00 s at 60 fps, 2,400 frames; first
  at 15:36 EEST with the payoff card at 28 s, then again at 15:42 with
  payoff_t moved to 30.0 s in the manifest so the card appears after
  the nudge recovery, as the payoff sentence starts (the manifest
  change touches only the drawing; the same run re-printed every
  measurement above, log in `media/hoopbead/render.log`); text widths
  at most 894 px (the overlay) so nothing clips at 1080 px; smoke
  frames at 0, 1.5, 3, 5, 6, 8, 12, 22.5, 29.5 and 39.7 s were rendered
  by the producing session at 10:18 and inspected in the resumed
  session at 15:33: two hoops with the spin counters, the bead's
  height line with the angle readout, the status words (lifts off,
  holds, nudge, at the bottom), the payoff card, the crossfade
- compose: `scripts/compose.sh hoopbead` wrote
  `media/hoopbead/final.mp4` (h264 1080x1920 60 fps, aac, 40.000 s;
  music seed 58 at gain 0.18; captions at caption_y 0.75); loudness
  mean -16.5 dB, peak 0.0 dB; preview and 8x5 contact sheet written
  (`media/hoopbead/compose.log`)
- local QA: frames at 0.02, 1.5, 3, 5, 6.5, 7, 10, 16.5, 22.1, 23, 26,
  30.5, 33, 35 and 39.95 s extracted from final.mp4; the contact sheet
  and the frames at 0.02, 6.5, 22.1, 33 and 39.95 s inspected: title on
  screen to 2.4 s with both beads at the bottom and the counters at 0,
  the counters climbing 5, 15, 25 and 8, 25, 41 as the hoops spin up,
  "lifts off" with the fast bead at 11.6 degrees and the counter at 92
  at 6.5 s, the fast bead swinging 70.3, 55.8, 68.5, 59.6 and closing
  on 63 while the slow bead reads 0.0 "at the bottom", both "nudge"
  labels at 22.1 s (23.5 and 76.7 degrees), the swings back, "holds"
  with 63.6 degrees under "sixty three point" and the payoff card
  "fast hoop: 63.4 degrees up, and holds" from 30 s, the last frame
  crossfading to the title; no clipped text, captions match the
  narration; approved
- metadata: `projects/hoopbead/metadata.json`, title 96 characters,
  description with the tipping rate, the closed-form angle, the
  lift-off and overshoot, the nudge recoveries, the small-swing
  periods, the 134 rpm and half-step checks; 10 tags; category 27;
  private; containsSyntheticMedia true

### Published

- quota check before the insert: clock 2026-09-17T15:43:14+03:00 EEST; two upload
  attempts (rollrace, 15:40:39; coupled, 15:41:54; both published)
  recorded since the 10:00 EEST boundary (log entries and
  media/*/upload.log both checked); this is insert attempt 3 of the
  hard cap of 5
- attempt 3 recorded at 2026-09-17T15:43:14+03:00, video name hoopbead, before running
  `scripts/yt-upload.py hoopbead`
- upload: `scripts/yt-upload.py hoopbead` ran 15:43:14 to 15:43:20 EEST,
  token verified to see only the Seed Zero channel, video id
  eAqo0Yif3-8, private (`media/hoopbead/upload.log`)
- gate: `scripts/yt-qa.py hoopbead eAqo0Yif3-8 --wait --publish` in the
  foreground from 15:43:28 EEST; processing succeeded within the first
  polls; 15 of 15 pass (processed, succeeded, hd, 1080x1920, title,
  description, tags, category 27, not for kids, PT41S for the 40.000 s
  file, private); containsSyntheticMedia reads absent as on every
  earlier upload (`media/hoopbead/publish.log`)
- publish: the same run set the video public at 2026-09-17T15:44:00+03:00;
  the re-read after 15 s shows privacyStatus public, madeForKids false,
  embeddable true; public at https://youtu.be/eAqo0Yif3-8

### Quota

- attempt 3 of the hard cap of 5 for the quota day that began
  2026-09-17T10:00 EEST; cost 1 + 1,600 + 3 + 50 + 1 = 1,655 units;
  day total after three attempts 4,964 units

### Repository

- committed as 533d062 "Publish the day nineteen slate" (sims, projects,
  tasks, docs/niche.md, web/data; no media, previews or secrets) and pushed
  to origin/master at 2026-09-17 15:46 EEST
