# Produce short: Newton's cradle, lift two balls, how many fly out

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day20

## Goal

Backlog idea (trend research 2026-09-16, task 20260916-100924):
"Newton's cradle: five steel balls with Hertz contacts; two balls lifted
10 cm and released beside the same cradle with one ball lifted; measure
how many balls leave the far side and how high they rise; expect two
balls to 10 cm against one ball to 10 cm and never one ball at double
speed (that would rise 40 cm and needs twice the energy); check
momentum and energy to 1e-9; deterministic, no seed."
Day twenty, first slot. Chosen because it is continuous motion, a
two-panel same-input comparison (the same cradle, one ball lifted
against two), a viral classroom question, with one plain question, one
setup number (two balls lifted 10 cm) and one payoff number (two balls
rise to the measured height, never one ball to 40 cm) that momentum and
energy conservation check.
Question in the first two seconds: "Lift two balls. How many fly out?"

## Claim

Lift two balls of a five-ball cradle and let go: two balls leave the far
side and rise to the same height, never one ball at double speed. Every
number below is printed by the sim before the script is written.

## Evidence

### Measurements

(recorded after the measure-only run, before scripting)

`sims/cradle/cradle.py --measure-only` with `projects/cradle/manifest.json`
(five steel balls of radius 1.5 cm, density 7850 kg/m^3, 111.0 g each, on
30 cm strings from pivots 30.3 mm apart, so the balls hang 0.3 mm apart at
rest; exact pendulums with a Hertz contact F = k delta^1.5 between
neighbours, k = 2.5e8 N/m^1.5, softened from real steel (E = 200 GPa,
nu = 0.3, k = 1.27e10) by a factor 51 so that a click lasts 0.41 ms with
197 microns of squash instead of 86 microseconds and 41 microns, and the
step resolves it; g = 9.80665 m/s^2; top cradle: ball 1 lifted so its
centre is 10 cm above rest (48.19 degrees); bottom cradle: balls 1 and 2
lifted together to the same height; both let go at 0.8 s of the video;
RK4 at a base step of 5e-6 s (83 steps per click) cut into 8 sub-steps
while any pair touches, with a geometric ramp of tiny steps at every
contact onset and offset; 39.3 s simulated for the 40 s scene;
deterministic, no seed; log in `media/cradle/measure.log`, run at 10:47
EEST):

- closed forms: speed at the bottom sqrt(2 g h) = 1.4005 m/s; one ball at
  double speed would rise 4 h = 40 cm, above the pivots (the strings are
  30 cm), and carry twice the energy of two balls at 1.40 m/s with the
  same momentum; swing period 1.0990 s at small angles and 1.1496 s at
  48.2 degrees, so a click every 0.5748 s; 108.83 mJ lifted per ball
- one lifted, first click: contact begins at 1.0876 s of the video
  (0.2876 s after release), the incoming ball at 1.4004 m/s against
  1.4005; four contacts (1-2, 2-3, 3-4, 4-5) of 0.41 ms each, the click
  over in 1.67 ms; outgoing speeds balls 1..5: -0.0000, -0.0000, -0.0000,
  -0.0000, 1.4005 m/s; far-side peaks 0.000, 0.000, 0.000, 0.000, 10.000
  cm (closed form v^2 / 2 g: 10.000); balls out (peak over 1 cm): 1
  (ball 5); the second click at 1.6645 s sends ball 1 back out the near
  side to 9.999 cm and the far balls rise at most 0.000 cm after it
- two lifted, first click: contact begins at 1.0876 s, the incoming ball
  at 1.4004 m/s; six contacts (2-3, 1-2, 3-4, 2-3, 4-5, 3-4) of 0.41 ms
  each, the click over in 1.67 ms; outgoing speeds -0.0000, -0.0000,
  -0.0000, 1.4004, 1.4005 m/s; far-side peaks 0.000, 0.000, 0.000, 9.999,
  10.000 cm (closed form 9.999, 10.000); balls out: 2 (balls 4, 5); the
  second click at 1.6645 s sends balls 1 and 2 back out the near side to
  9.999 cm each and the far balls rise at most 0.001 cm after it
- conservation across the first click: momentum 0.155420 -> 0.155412
  kg m/s (one lifted) and 0.310840 -> 0.310824 (two lifted); energy
  108.831025 -> 108.831025 mJ (-9.8e-10) and 217.662050 -> 217.662049 mJ
  (-1.3e-9); over all 68 / 72 major clicks the energy changes by at most
  5.7e-9 / 8.7e-9 across a click and drifts 1.3e-8 / 1.1e-8 over the
  whole run; the momentum changes by at most 7.0e-4 / 1.1e-3 across a
  click because the strings of the balls that sit a gap short of their
  rest points pull sideways while the click lasts (1.7 ms), not a loss
- rhythm: 68 major clicks (one lifted) and 72 (two lifted, plus 7 minor
  contacts under 0.3 of the first squash) in 39.3 s, the first three
  0.5769 s apart; ball 1 peaks on the near side every 1.1529 / 1.1523 s
  (closed form 1.1496); ball 5's far-side peak ranges 9.96 cm (12.9 s)
  to 10.00 cm (24.4 s) with one lifted and 9.94 cm (12.9 s) to 10.44 cm
  (35.9 s) with two, a slow beat of the balls that stay (small-angle
  period 1.099 s) against the click cadence; the balls that stay sway at
  most 1.47 degrees (0.010 cm of rise) / 3.01 degrees (0.042 cm), kicked
  a gap's width at every click
- loop: ball 1's last near-side peak 9.97 cm at 39.998 s (one lifted)
  and 10.22 cm at 39.977 s (two lifted); at 40 s the lifted balls sit
  0 / 10 px sideways and 0 / 11 px vertically from their first-frame
  spots; the 0.6 s loop fade covers the rest (release_t moved from 0.7
  to 0.8 s after a first run left them 36 / 75 px off)
- check at half the step (2.5e-6 s): every far-side peak and outgoing
  speed repeats to four decimals (9.9998 cm; 9.9995 and 9.9998 cm;
  1.40046; 1.40043 and 1.40045 m/s)
- check at ten times the stiffness (k = 2.5e9, a 0.16 ms click, dt / 4):
  the two balls rise 9.9997 and 9.9999 cm, balls out 2
- check with no gap at all (balls touching exactly, not drawn): the whole
  chain squeezes as one for 1.1 ms and the push disperses; one lifted
  gives far-side peaks 0.161 and 9.777 cm for balls 4 and 5 (one ball
  out); two lifted gives 0.460, 6.406 and 12.990 cm for balls 3, 4 and 5
  (two balls out, not to equal heights); energy and momentum still
  conserved (217.6621 -> 217.6621 mJ, 0.31084 -> 0.31083 kg m/s); the
  prototypes without a gap also slid into a symmetric sloshing mode
  within 5 s; this is why the drawn run has the 0.3 mm gap: a real
  cradle's 86 microsecond click is far shorter than the time to cross
  any hair of a gap, so its clicks come one at a time

Decisions: a first prototype with a 1 mm gap and k = 2.5e7 gave 8 degrees
of rest-ball sway and far peaks beating 9.47 to 10.52 cm; 0.3 mm and
k = 2.5e8 cut the sway to 1.5 / 3.0 degrees and the beat to 9.96-10.00 /
9.94-10.44 cm. Plain RK4 without sub-steps drifted 2.5e-6 in energy
(the delta^1.5 kink at zero overlap); the contact sub-steps and the
onset/offset ramps bring it to 1e-8.

Narration numbers: ten centimeters (setup, both cradles), one ball out
and two balls out (the balls-out counts), to ten centimeters (payoff,
the 10.000 and 9.999 / 10.000 cm first-click peaks, shown as integer cm
on the readouts and the card), twice the energy (the closed form). The
40 cm of one ball at double speed, the speeds, the click lengths, the
conservation figures, the rhythm, the sway, the no-gap, half-step and
stiffness checks go to the description.

### Production

- narration (written after the measure-only run): three hooks tried,
  "Five steel balls. Lift two balls. How many fly out?" (kept, it names
  the setup and asks the title question in the title's words), "Lift two
  balls of this cradle. How many fly out?" and "Two balls go in. How
  many come out?"; `projects/cradle/narration.txt`, 110 words; the setup
  number is ten centimeters, the payoff one flies out / two fly out, to
  ten centimeters; the 40 cm of one ball at double speed stays in the
  description
- voice: `scripts/voiceover.sh projects/cradle/narration.txt` passed on
  the first run at 118 words but ran 37.23 s, over the 36 s guideline;
  "Same cradle twice." was cut and the second run passed at 10:45 EEST
  (110 words, 34.73 s, ends at 35.33 s of the 40 s video, 3.2 words/s);
  no number or word was misheard in the round trip (the timing pass
  alone wrote "phi" for "fly" at 33.1 s; the gate transcript matched);
  timing (`scripts/voice-timing.py`, +0.6 s offset): "Five steel balls,
  lift two balls. How many fly out?" 0.60 to 4.25 s over the title (to
  2.4 s) and the first click at 1.09 s; "On top, one ball was lifted ten
  centimeters. Below, two balls were lifted the same" 5.08 to 10.10 s;
  "one ball swings in and one ball flies out the far side, below two
  swing in and two fly out" 10.10 to 15.73 s while both cradles click
  every 0.577 s; "Each click hands the push to the next ball, and the
  balls in the middle barely move" 15.73 to about 20 s; "why not one
  ball at double speed, it would carry the same push but twice the
  energy, and that energy is not there" about 20 to 26.86 s; "So how
  many fly out?" 26.86 to 28.36 s with the payoff card fading in from
  28.4 s (payoff_t set from the timing, after the event); "Lift one
  ball, one flies out to ten centimeters" 28.36 to 31.92 s and "Lift two
  balls, two fly out, to ten centimeters" 31.92 to 35.33 s over the
  card; log in `media/cradle/voice.log`
- footage: `sims/cradle/cradle.py` (no arguments) wrote
  `media/cradle/footage.mp4`, 40.00 s at 60 fps, 2,400 frames, at
  10:54 EEST; the same run re-printed every measurement above
  (`media/cradle/render.log`); text widths at most 848 px (the overlay),
  payoff lines 752 and 714 px, so nothing clips at 1080 px; smoke frames
  at 0, 0.5, 1.1, 1.4, 1.6, 3, 6, 12, 22, 30, 36 and 39.7 s (`--frames`,
  10:47 EEST) inspected: the held balls under the title, the click
  flash at 1.1 s, the far balls on the 10 cm line with "1 to 10 cm" and
  "2 to 10 cm" at 1.4 s, the readouts resetting at each click and
  climbing live, the payoff card, the crossfade; an earlier smoke set
  had ball 5 at its peak nearly touching the "10 cm" label (the cradle
  centre moved from x 540 to 500) and the peak readout at one decimal
  ("to 10.3 cm" late in the run against the narrated ten; now integer
  cm, matching the card)
- compose: `scripts/compose.sh cradle` wrote `media/cradle/final.mp4`
  at 10:54 EEST (h264 1080x1920 60 fps, aac 22050 Hz mono, 40.000 s;
  music seed 63 at gain 0.18; captions at caption_y 0.75); loudness
  mean -16.1 dB, peak -0.0 dB; preview and 8x5 contact sheet written
  (`media/cradle/compose.log`)
- local QA: frames at 0.02, 1.09, 1.4, 2.4, 7, 12, 20, 28.5, 33, 35 and
  39.95 s extracted from final.mp4 (`media/cradle/frame-*.png`); the
  contact sheet and the frames at 0.02, 1.4, 7, 20, 28.5, 33, 35 and
  39.95 s inspected: overlay and title over the held cradles with both
  counts at 0; "1 to 10 cm" and "2 to 10 cm" with the far balls on the
  10 cm line at 1.4 s under "Five steel balls."; the readouts resetting
  at each click and climbing (to 5 cm and to 6 cm with the click flash
  at 7 s) back to 10 cm; "in the middle barely" with the rest balls
  still in a row at 20 s; the card fading in under "So how many fly
  out?" at 28.5 s with the lifted balls at their near peaks; "Lift two
  balls: two" and "fly out, to ten" over the card; the last frame
  crossfading to the title; captions match the narration, no clipped
  text, the caption band clear of the balls; approved
- metadata: `projects/cradle/metadata.json`, title 84 characters,
  description with the speeds, the click lengths, the peaks, the 40 cm
  closed form, conservation, rhythm, the sway, the softened stiffness,
  the half-step, stiffness and no-gap checks; 10 tags; category 27;
  private; containsSyntheticMedia true

### Published

- quota check before the insert: clock 2026-09-18T10:57:16+03:00 EEST; two upload
  attempts (monkeyhunter, 10:26:34, published; waterwheel, 10:53:23,
  private, gate pending) recorded since the 10:00 EEST boundary (log
  entries and media/*/upload.log both checked); this is insert attempt
  3 of the hard cap of 5
- orchestrator review before the upload: task evidence, the contact
  sheet and the frames at 0.02, 1.4 and 33 s inspected; title clear of
  the overlay, no clipped text, the "balls out" counters and the "to 10
  cm" readouts agree with the narration, the payoff card on screen while
  the payoff sentence is spoken, the balls already in flight at 1.4 s,
  the last frame crossfading to the first; the description states the
  softened stiffness, the 0.3 mm gap and the gapless dispersion check;
  approved
- attempt 3 recorded at 2026-09-18T10:57:16+03:00, video name cradle, before running
  `scripts/yt-upload.py cradle`

- upload: `scripts/yt-upload.py cradle` ran 10:57:16 to 10:57:26 EEST,
  token verified to see only the Seed Zero channel, video id
  qE-8l1rEPRY, private (`media/cradle/upload.log`; YouTube publishedAt
  10:57:23 EEST)
- gate: the producing session stopped after the upload; a read-only
  `scripts/yt-qa.py cradle qE-8l1rEPRY` at 11:22:43 EEST passed 15 of 15
  (processed, succeeded, hd, 1080x1920, title, description, tags,
  category 27, not for kids, PT41S for the 40.000 s file, private) and
  published nothing; the resumed run rechecked the task evidence, the
  contact sheet, the three attempt entries in web/data/log.jsonl and the
  three media/*/upload.log files written since the boundary, then ran
  `scripts/yt-qa.py cradle qE-8l1rEPRY --wait --publish` in the
  foreground from 11:37:53 EEST: processing already succeeded on the
  first poll, 15 of 15 pass again; containsSyntheticMedia reads absent
  as on every earlier upload (`media/cradle/publish.log`)
- publish: the same run set the video public at 2026-09-18T11:37:56+03:00;
  the re-read after 15 s shows privacyStatus public, madeForKids false,
  embeddable true; public at https://youtu.be/qE-8l1rEPRY

### Quota

- attempt 3 of the hard cap of 5 for the quota day that began
  2026-09-18T10:00 EEST; cost 1 + 1,600 + 1 + 52 = 1,654 units (the 1 is
  the read-only gate at 11:22); day total after three attempts 4,966
  units

### Repository

- committed as 2de3568 "Publish the day twenty slate" (sims, projects,
  tasks, docs/niche.md, scripts/yt-stats.py, web/data; no media, previews
  or secrets) and pushed to origin/master at 2026-09-18 11:44 EEST
