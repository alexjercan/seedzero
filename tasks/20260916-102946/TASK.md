# Produce short: Turntable ball, where does a ball go on a spinning record

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day18

## Goal

Backlog idea (trend research 2026-09-16, task 20260916-100924):
"Turntable ball: a solid ball set rolling across a record turning at
33 1/3 rpm beside a hollow ball given the same push; measure the path
and the loop time; expect both to run in closed circles instead of
flying off, the solid ball once every 3.5 table turns (6.30 s, exactly
2/7 of the table rate) and the hollow ball every 2.5 turns (4.50 s,
2/5), while a frictionless puck slides straight off; exactly periodic
so the short loops; deterministic, no seed." Day eighteen, third slot.
Chosen because it is continuous motion, a two-panel same-input
comparison (a sliding puck and a rolling ball given the same push on
the same record), exactly periodic so the short loops, with one plain
question, one setup number (the record's speed) and one payoff number
(the ball's loop time in table turns) that a closed form checks.
Question in the first two seconds: "Where does the ball go?"

## Claim

A ball rolling on a spinning record does not fly off. It runs in a
closed circle and comes back to where it started, once every three and
a half turns of the record, whatever push it was given. A puck that
slides instead of rolling leaves the record. Every number below is
printed by the sim before the script is written.

## Evidence

### Measurements

(recorded after the measure-only run, before scripting)

`sims/turntable/turntable.py` with `projects/turntable/manifest.json`
(a record of radius 15 cm turning at 33 1/3 rpm, 1.800 s per turn,
Omega = 3.4907 rad/s; a solid ball of radius 2 cm with I = 0.4 m r^2
pushed from the centre at 5 cm/s and rolling without slipping: its
centre, velocity and spin vector integrated with RK4 at 100 steps per
frame (dt = 1.67e-4 s) under the rolling constraint, the friction force
being whatever keeps the contact point moving with the record and the
same force torquing the ball; a puck with no grip given the same push;
37.8 s = 21.00 turns of the record; deterministic, no seed; log in
`media/turntable/measure.log`):

- ball: back at the start after 6.3000 s = 3.5000 turns of the record
  (closest approach 0.00 um); its velocity turns a full circle in
  6.3000 s = 3.5000 turns; closed form (1 + k) / k = 3.5000 turns =
  6.3000 s; the path is a circle of radius 5.013 cm (closed form v / (c
  Omega) with c = k / (1 + k) = 2/7: 5.013 cm) reaching 10.03 cm from
  the record's centre, 3.0 cm inside the edge; no-slip residual under
  9.8e-15 m/s; 6.000 loops in the 37.8 s video
- puck: with no grip it slides straight at 5 cm/s and its centre passes
  the edge at 3.00 s (1.67 turns of the record)
- hollow ball (I = 2/3 m r^2, measured, not drawn): back after 4.5000 s
  = 2.5000 turns (closed form 2.5000); circle radius 3.581 cm
- checks: pushed at 3 cm/s toward 130 degrees the ball is back after
  6.3000 s = 3.5000 turns on a circle of radius 3.008 cm (the loop time
  does not depend on the push, only the circle's size does); at half
  the time step the return is at 6.3000 s

Narration numbers: one point eight seconds a turn (setup), back at the
centre every three and a half turns, said as "two loops for every
seven turns" if the round trip needs it (payoff). The circle radius,
the hollow ball and the other push go to the description.

### Production

- footage: `sims/turntable/turntable.py` (no arguments) wrote
  `media/turntable/footage.mp4`, 37.80 s at 60 fps, 2,268 frames (six
  loops of 6.30 s, 21.00 turns of the record, so the video loops on the
  ball's own period); the same run re-printed every measurement above
  (log in `media/turntable/render.log`); text widths at most 722 px
  (the counter row) so nothing clips at 1080 px; smoke frames at 0,
  1.5, 2.8, 3.4, 6.3, 12, 20, 29.5 and 37.7 s inspected first; the
  puck's path line is clipped 1.2 cm past the edge of the record
  instead of running to the frame edge
- voice: `scripts/voiceover.sh projects/turntable/narration.txt` failed
  the round trip three times on wording, never on a number: whisper
  doubled "Where" at the sentence break before "Where does the ball
  go?" (now "So where does the ball go?"), heard "across a spinning
  record" as "across the spinning record" (now "the spinning record"),
  and wrote "three and a half" as "3.5" (now "three point five turns",
  which also matches the card's "3.50 turns"); the fourth run passed
  (109 words, 31.85 s, ends at 32.45 s of the 37.8 s video, 3.4
  words/s); "The puck slides straight and drops off the edge" is
  spoken from about 12 s, after the puck has left at 3.0 s, and the
  tag under the record keeps its exit time on screen; the payoff card
  comes at 29.0 s as "In a circle, back to the center every three
  point five turns" is spoken (28.33 to 32.45 s); log in
  `media/turntable/voice.log`
- compose: `scripts/compose.sh turntable` wrote
  `media/turntable/final.mp4` (h264 1080x1920 60 fps, aac, 37.800 s;
  music seed 55 at gain 0.18; captions at caption_y 0.75); loudness
  mean -16.2 dB, peak -0.0 dB; preview and 8x5 contact sheet written
- local QA: frames at 0.02, 1.5, 3.0, 4.5, 6.3, 12, 20, 27, 29.5, 33
  and 37.75 s extracted from final.mp4 and inspected: title on screen
  to 2.4 s, the puck at the edge at 3.0 s with its tag "puck, no grip:
  off the record at 3.0 s" under the record, the ball's coral trail
  closing into a circle through the centre, the counter "record turns
  3.50 ball loops 1" as the ball is back at the centre at 6.3 s and
  "18.33 / 5" at 33 s, the payoff card "every 3.50 turns of the
  record" under the captions from 29 s, the last frame crossfades to
  the title (the counter row fades under the title for 0.6 s); no
  clipped text, captions match the narration
- metadata: `projects/turntable/metadata.json`, title 100 characters,
  description with the closed form (1 + k) / k, the circle radius, the
  other push, the hollow ball, the puck and the checks; 10 tags;
  category 27; private; containsSyntheticMedia true

### Published

- quota check before the insert: clock 2026-09-16T10:42:58+03:00 EEST; two upload attempts
  (rainbow, 10:25:57, published; tunnel, 10:42:33, uploaded private
  and waiting for its gate) recorded since the 10:00 EEST boundary;
  this is insert attempt 3 of the hard cap of 5
- attempt 3 recorded at 2026-09-16T10:42:58+03:00, video name turntable, before running
  `scripts/yt-upload.py turntable`
- upload: `scripts/yt-upload.py turntable` ran 10:42:58 to 10:43:04 EEST,
  token verified to see only the Seed Zero channel, video id
  2TPdAAac0Jc, private (`media/turntable/upload.log`)
- note: the session that ran the upload stopped before reading the gate;
  a new session took over at 10:53 EEST, re-read the task evidence, the
  contact sheet and the quota records (attempts 1 to 3 on record) and
  continued the release flow
- gate: `scripts/yt-qa.py turntable 2TPdAAac0Jc` at 2026-09-16T10:53:26+03:00,
  15 of 15 pass (processed, succeeded, hd, 1080x1920, title, description,
  tags, category 27, not for kids, PT38S for the 37.800 s file, private);
  containsSyntheticMedia reads absent as on every earlier upload
  (`media/turntable/qa.log`)
- publish: `scripts/yt-qa.py turntable 2TPdAAac0Jc --publish` at 10:54:19 EEST
  re-ran the gate (15 of 15) and set the video public at
  2026-09-16T10:54:21+03:00; the re-read after 15 s (10:54:37) shows
  privacyStatus public, madeForKids false, embeddable true; public at
  https://youtu.be/2TPdAAac0Jc

### Quota

- attempt 3 of the hard cap of 5 for the quota day that began
  2026-09-16T10:00 EEST; cost 1 + 1,600 + 1 + 52 = 1,654 units;
  day total after three attempts 4,962 units
