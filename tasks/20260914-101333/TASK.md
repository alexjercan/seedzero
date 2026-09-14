# Produce short: Metronome sync, two metronomes tick together

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day16

## Goal

Backlog idea (trend research 2026-09-13, task 20260913-212839): "Metronome
sync: two metronomes started a quarter beat apart on a board that rolls
on two cans versus the same two on a fixed table; measure the time to
lock in step; expect the board pair to lock within about a minute and
the table pair to keep their gap for the whole run (Pantaleone 2002
model: escapement pendulums coupled through the moving base)." Day
sixteen, third slot. Chosen because it is a viral subject (TikTok
"metronome sync" pages in the research run), a two-panel same-input
comparison of continuous visible motion, with one setup number (the
starting gap between the ticks) and one payoff number (the time to
lock). Question in the first two seconds: "Why do these two end up
ticking together?"

## Claim

Two identical metronomes start out of step. On a fixed table they stay
out of step for the whole run. On a light board that can roll they
pull each other into step within the run. Every number below is printed
by the sim before the script is written.

## Evidence

### Measurements

(recorded after the measure-only run, before scripting)

`sims/metronome/metronome.py` with `projects/metronome/manifest.json`
(two escapement-driven pendulums on a base of mass M sliding in one
dimension, equations from the Lagrangian, the 3 by 3 acceleration
system solved at every RK4 stage at 1,000 steps per second; both
metronomes started on the escapement's limit cycle; deterministic, no
seed; log in `media/metronome/measure.log`):

- metronomes: 120 beats per minute (a full swing every 1.00 s, a beat
  every 0.50 s), pendulum length 24.8 cm, bob 30 g, swing 30 degrees
  held by an escapement of strength 0.3; board 1,600 g on two cans
  with drag 0.2 kg/s, or fixed to the table; metronome two starts 0.25
  beat (125 ms) behind metronome one
- board: gap between the ticks in beats: 0.248 at 0 s, 0.195 at 5 s,
  0.135 at 10 s, 0.098 at 15 s, 0.064 at 20 s, 0.041 at 25 s, 0.029
  at 30 s, 0.012 at 40 s, 0.002 at 60 s (125, 98, 68, 49, 32, 20, 15,
  6 and 1 ms)
- table: 0.250 beat at every sample from 0 to 60 s; largest change
  over the run 0.00000 beat: never in step
- board pair: in step (gap under 0.05 beat = 25 ms, and staying
  there) from the tick at 22.83 s; gap at the end 0.0024 beat = 1.2
  ms; the board moves at most 14.0 mm from its start; ticks near the
  lock: metronome one at 21.761, 22.832, 23.904 s, metronome two at
  21.788, 22.857, 23.926 s
- check, half the step: in step from 22.83 s
- check, board 800 g: in step from 10.95 s; 3,200 g: from 47.69 s;
  6,400 g: not in step by 60 s (gap 0.096 beat)
- check, start 0.5 beat apart: in step from 42.22 s; 0.9 beat apart:
  not in step by 60 s (gap 0.165 beat)
- model choices recorded: a first run started metronome two on the
  small-angle circle with the board at rest, so the board drifted
  100 mm from the initial momentum and the table gap wobbled within
  each swing (phase measured from the state); the start was moved onto
  the limit cycle with zero net momentum and the gap is now measured
  from the tick times; a scan of escapement 0.05, 0.15 and 0.3 with
  boards of 0.6, 1.2 and 2.4 kg showed that the weak escapement
  (0.05) locks in an overshooting way (the gap swings through zero
  and back) while 0.3 locks monotonically with the lock time growing
  with board mass (0.6 kg 8.8 s, 1.2 kg 17.4 s, 2.4 kg 34.7 s), so
  0.3 and 1.6 kg were chosen for a lock near 23 s

Narration numbers: an eighth of a second apart (setup), in step after
twenty three seconds (payoff).

### Production

- `projects/metronome/narration.txt`: 111 words; two mishearings in
  the first drafts ("started" heard as "start at", "they are in step"
  heard as "they're") were reworded to "an eighth of a second apart"
  and "they fall into step"; `scripts/voiceover.sh` round trip passed
  ("ok: transcript matches narration (30.824490s)",
  `media/metronome/voice.log`); voice ends at 31.42 s of video
- timing (`scripts/voice-timing.py`, +0.6 s offset): "Why do they
  tick together? The board" spoken about 23.5 to 26.4 s while the
  board pair locks at 23.83 s of video (22.83 s of the run after the
  1.0 s release); "they fall into step after 23 seconds" from 26.41
  s, payoff card from 27.0 s
- text widths measured with PIL before rendering: overlay 866 px,
  title lines 568 and 780 px, panel labels 747 and 274 px, longest
  readout 461 px, clock 218 px, payoff lines 857, 866 and 700 px; all
  under 950 px
- footage: `sims/metronome/metronome.py` rendered 40.00 s at 60 fps,
  1080x1920 (`media/metronome/render.log`); the board's motion is
  drawn at true scale (about 1 cm at 1,100 px per metre)
- compose: `scripts/compose.sh metronome` (music seed 50, gain 0.18,
  captions at 0.75); final.mp4 40.000 s, h264 1080x1920 + aac; mean
  volume -16.9 dB, peak -0.0 dB (`media/metronome/compose.log`)
- inspected full-resolution frames at 0.02, 2.0, 5.0, 12.0, 20.0,
  23.8, 27.0, 29.0, 32.0 and 39.95 s (`media/metronome/frame-*.png`,
  rows in `row-a.png` and `row-b.png`): question on screen for the
  first 2.4 s, board readout counts down 104, 68, 35, 27 ms and reads
  "ticks in step" from 23.83 s, table readout stays at 125 ms, clock
  matches the run, captions clear of both panels, payoff card from
  27.0 s, crossfade back to frame 0 at the end; approved
- `projects/metronome/metadata.json`: title 99 characters (a first
  draft was 107 and was cut), category 27, private, altered-content
  disclosure true, not made for kids; description carries the
  per-5-second gaps and the mass and start-gap checks

### Published

- quota check before the insert: clock 2026-09-14T10:41:42+03:00 EEST; two upload
  attempts recorded since the 10:00 EEST boundary (orbitlane at
  10:35:18, published 10:39:26; swing at 10:40:30, private, awaiting
  its gate read); this is insert attempt 3 of the hard cap of 5
- attempt 3 recorded at 2026-09-14T10:41:42+03:00, video name metronome, before running
  `scripts/yt-upload.py metronome`
- upload: `scripts/yt-upload.py metronome` ran 10:41:42 to 10:41:48
  EEST, token verified to see only the Seed Zero channel, video id
  owcns7Z0fVk, private (`media/metronome/upload.log`)
- gate read at 2026-09-14T10:42:54+03:00: 15 of 15 pass (processed,
  succeeded, hd, embeddable, 1080x1920 source, title, description, tags
  as a set, category 27, not made for kids, PT41S, private);
  containsSyntheticMedia reads absent as usual
  (`media/metronome/qa.log`)
- publish read at 2026-09-14T10:43:16+03:00: 15 of 15 pass again;
  privacy set to public at 10:43:19 EEST; re-read after 15 s:
  privacyStatus public, madeForKids false, embeddable true
  (`media/metronome/publish.log`)
- public at https://youtu.be/owcns7Z0fVk

### Quota

- upload attempt 3 of 5 for the quota day that began 2026-09-14
  10:00 EEST
- units: 1 channel check + 1,600 insert + 1 gate read + 1 publish
  read + 50 update + 1 re-read = 1,654 units; day total after this
  video 4,962 of 10,000 (plus the stats read at close)
