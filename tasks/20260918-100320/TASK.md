# Produce short: Monkey and hunter, aim straight at a dropping target

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day20

## Goal

Backlog idea (trend research 2026-09-16, task 20260916-100924):
"Monkey and hunter: a dart fired straight at a target hanging 10 m up
and 20 m away, the target let go at the shot, at 30 m/s beside 60 m/s;
measure the miss distance; expect 0.000 m for both (both fall 2.72 m by
the hit at 0.745 s and 0.68 m at 0.373 s), a shot aimed 1 degree high
misses by 44 cm, and any speed under 15.7 m/s lets the target reach the
ground first; deterministic, no seed."
Day twenty, second slot. Chosen because it is continuous motion, a
two-panel same-input comparison (the same aim at two dart speeds), a
classic demo with a plain question, one setup number (the distance to
the target) and one payoff number (how far both had fallen at the hit)
that a closed form checks.
Question in the first two seconds: "Aim straight at it. It drops as you
fire. Do you hit?"

## Claim

A dart aimed straight at a hanging target that drops the instant the
dart leaves hits it at any speed, because both fall the same distance
in the same time. Every number below is printed by the sim before the
script is written.

## Evidence

### Measurements

(recorded after the measure-only run, before scripting)

`sims/monkeyhunter/monkeyhunter.py` with
`projects/monkeyhunter/manifest.json` (a launcher at the origin, a
target hanging 10 m up and 20 m away, the dart aimed straight at the
target's start and fired at 30 m/s (top panel) and 60 m/s (bottom); the
target is let go from rest at t = 0, the instant the dart leaves; g =
9.80665 m/s^2, no air; dart and target are points for every number and
are drawn larger than life; RK4 on both bodies at 6000 steps per second,
dt = 1.67e-4 s, to 1.6 s; every number cross-checked against the closed
form; deterministic, no seed; log in `media/monkeyhunter/measure.log`):

- aim angle atan(10 / 20) = 26.565 degrees (cos 0.89443, sin 0.44721);
  the target's start is 22.361 m from the muzzle along the aim line; a
  target let go from 10 m reaches the ground at sqrt(2 H / g) = 1.4281 s
- dart at 30 m/s: crosses the target's x at 0.7454 s (closed form
  D / (v cos theta) = 0.7454 s); at that moment the dart is 2.7241 m
  below its aim line and the target 2.7241 m below its start (closed
  form g t^2 / 2 = 2.7241 m; the two drops differ by +0.000
  micrometres); dart height 7.2759 m, target height 7.2759 m, gap
  -0.000000 m; miss at closest approach 0.000000 m at 0.7454 s; dart
  speed at the hit 27.52 m/s; over the whole flight the dart's drop
  below its aim line and the target's drop differ by at most 0.000
  micrometres; on screen at 1/5 speed the flight lasts 3.73 s
- dart at 60 m/s: crosses the target's x at 0.3727 s (closed form
  0.3727 s); the dart 0.6810 m below its aim line and the target
  0.6810 m below its start (closed form 0.6810 m; drops differ by
  +0.000 micrometres); both at height 9.3190 m, gap -0.000000 m; miss
  at closest approach 0.000000 m at 0.3727 s; dart speed at the hit
  58.46 m/s; drops differ by at most 0.000 micrometres over the flight;
  on screen the flight lasts 1.86 s
- slowest dart that still hits before the target reaches the ground:
  closed form D / (cos theta sqrt(2 H / g)) = 15.658 m/s; bracketing
  search between 10 and 20 m/s to 0.0001 m/s gives 15.658 m/s; at 15
  m/s the dart reaches the ground at 1.3681 s, 1.65 m short of the
  target's x, while the target is still 0.82 m up; the target reaches
  the ground at 1.4281 s; closest approach while both are in the air
  1.843 m
- aimed 1 degree high at 30 m/s: when the dart crosses the target's x
  at 0.7520 s it passes 0.4402 m above the target (closed form
  D (tan(theta + 1 degree) - tan theta) = 0.4402 m); miss at closest
  approach 0.3902 m at 0.7452 s (closed form sqrt(D^2 + H^2) sin(1
  degree) = 0.3902 m); the same aim at 60 m/s misses by 0.3902 m: the
  miss does not depend on the speed
- aimed 1 degree low at 30 m/s: crosses the target's x at 0.7390 s,
  0.4326 m below the target (closed form 0.4326 m); miss at closest
  approach 0.3902 m at 0.7452 s (closed form 0.3902 m); at 60 m/s
  0.3902 m
- if the target did not drop: the 30 m/s dart crosses the target's x
  2.724 m below it (closest approach 2.658 m at 0.7666 s); the 60 m/s
  dart 0.681 m below (closest approach 0.625 m)
- check at half the time step (12000 steps per second): the 30 m/s dart
  crosses at 0.7454 s, both fallen 2.7241 m, miss 0.000000 m (+9.78e-13
  m and +9.76e-13 m against the full step)

Narration numbers: twenty meters (setup, the distance to the target),
two point seven two meters (payoff, the 2.7241 m both had fallen by the
30 m/s hit, shown as 2.72 on the card and the readouts). The speeds, the
hit times, the 0.68 m fall of the 60 m/s shot, the 15.658 m/s
threshold, the 1 degree misses, the no-drop pass-under and the checks
go to the description; the speeds are on screen as panel labels only.

### Production

- narration: three hooks tried, "A target hangs twenty meters away.
  Aim straight at it. It drops as you fire. Do you hit?" (the title
  question after a noun-phrase opener, kept), "Aim a dart straight at a
  target twenty meters away. It falls the moment you fire. Hit or
  miss?" and "A target drops the instant you fire. Where should you
  aim?"; the first was kept because the payoff answers it in the same
  words ("So, do you hit? Yes, you hit"); `projects/monkeyhunter/
  narration.txt`, 101 words; the setup number is twenty meters, the
  payoff two point seven two meters; the speeds stay on screen only
- voice: `scripts/voiceover.sh projects/monkeyhunter/narration.txt`
  attempt 1 passed at 109 words (34.11 s, ending 34.71 s of video;
  `media/monkeyhunter/voice-attempt1.log`) but its timing put "two
  point seven two meters" at 32.2 to 34.7 s, after the 30 m/s freeze
  window closes at 33.33 s; the narration was trimmed by 8 words
  ("Watch the brackets.", "in the air", "the instant the dart leaves"
  to "as the dart leaves"); attempt 2 failed the round trip on wording,
  not a number: "leaves" at the end of a sentence was heard as "leads"
  (`media/monkeyhunter/voice-attempt2.log`), reworded to "The target is
  released at the shot."; attempt 3 passed (101 words, 32.00 s, ends
  at 32.60 s of video, 3.2 words/s); timing (`scripts/voice-timing.py`,
  +0.6 s offset): "It drops as you fire" 3.66 to 5.12 s over the first
  flight (fired at 0.5 s, the 60 m/s hit at 2.86 s, the 30 m/s hit at
  4.23 s), "The dart falls below its aim line, the target falls below
  its hook" 11.25 to 15.23 s over the second flight (fired 7.17 s, hits
  9.53 and 10.89 s, freeze to 13.33 s), "Both fall the same amount,
  every moment" 15.23 to 17.58 s over the third flight (fired 13.83 s),
  "the fast dart arrives sooner and falls less" inside 17.58 to 22.81 s
  around the 60 m/s hit at 16.19 and 22.86 s, "The slow dart takes
  longer and falls more" 22.81 to 25.18 s with the 30 m/s hit at
  24.23 s, "So do you hit?" by 27.73 s as the fifth shot flies (fired
  27.17 s), "Yes, you hit" 27.73 to 29.09 s with the 60 m/s hit flash
  at 29.03 s and the payoff card from 29.0 s, "By the hit, both had
  fallen 2.72 meters" 29.09 to 32.60 s with the 30 m/s hit at 30.89 s
  and its freeze ("fallen 2.72 m" on both brackets, "miss: 0.000 m")
  to 33.33 s; log in `media/monkeyhunter/voice.log`
- footage: `sims/monkeyhunter/monkeyhunter.py` (no arguments) wrote
  `media/monkeyhunter/footage.mp4`, 40.00 s at 60 fps, 2,400 frames,
  10:22 to 10:24 EEST, with the same run re-printing every measurement
  above (`media/monkeyhunter/render.log`); on screen the shots run at
  1/5 speed: six cycles of 6.667 s (400 frames each), both darts fired
  0.5 s into each cycle, the 60 m/s dart hits 2.36 s into the cycle and
  freezes with a flash, the 30 m/s dart hits at 4.23 s and freezes to
  the reset; each panel draws the dashed aim line, a "[" bracket from
  the aim line down to the dart and a "]" bracket from the hook down to
  the target, both labelled "fallen x m" and equal at every moment,
  "hit" and "miss: 0.000 m" at the hit, a clock and "1/5 speed"; text
  widths at most 894 px (payoff line 1; the overlay 869, the target's
  bracket label ends at about 1025 px) so nothing clips at 1080 px;
  the manifest's payoff_t moved from 30.0 to 29.0 s after the voice
  timing so the card lands on "Yes, you hit"; smoke frames at 0, 1, 2,
  3.5, 5, 12, 22, 30 and 39.7 s were inspected before the layout fixes
  (scene narrowed to 35 px/m so the target's label stays inside the
  frame, the dart's label held back until it has fallen 0.12 m so it
  clears the launcher, the dart drawn inside the barrel at rest,
  payoff line 2 shortened from 968 to 735 px) and 0, 1, 2, 5 and 12 s
  after them
- compose: `scripts/compose.sh monkeyhunter` wrote
  `media/monkeyhunter/final.mp4` (h264 1080x1920 60 fps, aac,
  40.000 s; music seed 63 at gain 0.18; captions at caption_y 0.75);
  loudness mean -16.6 dB, peak -0.0 dB; preview and 8x5 contact sheet
  written (`media/monkeyhunter/compose.log`)
- local QA: frames at 0.02, 1.5, 2.3, 2.9, 4.3, 12, 22, 29.1, 31, 32 and
  39.95 s extracted from final.mp4 and inspected with the contact
  sheet: the overlay at y 96 with the title from y 190 not touching it
  and both darts loaded in their launchers under the title at 0.02 s;
  both darts in flight with the equal "fallen 0.20 m" brackets under
  "A target hangs" at 1.5 s; the title fading at 2.3 s with the 60 m/s
  dart at 0.360 s, one step from its hit; the 60 m/s hit ("hit",
  "miss: 0.000 m", "fallen 0.68 m" on both brackets) with the 30 m/s
  dart still flying at 2.9 s; the 30 m/s hit flash with "fallen 2.72
  m" on both brackets at 4.3 s; both freezes under "The dart falls
  below" at 12 s; the fourth shot in flight at 22 s; the fifth shot's
  60 m/s hit flash with the payoff card fading in under "Yes, you hit:
  by the" at 29.1 s; the 30 m/s hit flash with the card under "hit,
  both had fallen" at 31 s; "two point seven two" with both freezes,
  "miss: 0.000 m" twice and the card "at 30 m/s both had fallen 2.72
  m" at 32 s; the last frame crossfading into the title frame at
  39.95 s; no clipped text, the caption band empty behind the captions,
  captions match the narration; the flash ring crosses the dart's
  label for 0.35 s at each hit, transient and legible; approved
- metadata: `projects/monkeyhunter/metadata.json`, title 98
  characters, description with the aim angle, both hit times and
  falls, the closest-approach misses, the 15.658 m/s threshold and the
  15 m/s short shot, the 1 degree high and low misses, the no-drop
  pass-under and the half-step check, the 1/5 speed note; 10 tags;
  category 27; private; containsSyntheticMedia true

### Published

- quota check before the insert: clock 2026-09-18T10:26:34+03:00 EEST; zero upload
  attempts recorded since the 10:00 EEST boundary (log entries and
  media/*/upload.log both checked); this is insert attempt 1 of the
  hard cap of 5
- orchestrator review before the upload: task evidence, the contact
  sheet and the frames at 0.02, 2.9, 31.0 and 39.95 s inspected; title
  clear of the overlay, no clipped text, the payoff card and both
  "fallen 2.72 m" brackets on screen while the number is spoken, the
  last frame crossfading to the first; approved
- attempt 1 recorded at 2026-09-18T10:26:34+03:00, video name monkeyhunter, before running
  `scripts/yt-upload.py monkeyhunter`

- upload: `scripts/yt-upload.py monkeyhunter` ran 10:26:34 to 10:26:42 EEST,
  token verified to see only the Seed Zero channel, video id
  Fb-2BqjEcz4, private (`media/monkeyhunter/upload.log`)
- gate: `scripts/yt-qa.py monkeyhunter Fb-2BqjEcz4 --wait --publish` in
  the foreground from 10:26:49 EEST; processing succeeded on the first
  poll, but snippet.tags read back absent, so the gate was 14 of 15 and
  publish was refused at 10:26:49, 10:27:28 and 10:29:21 (a raw
  videos.list at 10:30 confirmed the tags key missing, not empty); the
  tags appeared by 10:32:52, 15 of 15 pass (processed, succeeded, hd,
  1080x1920, title, description, tags, category 27, not for kids, PT41S
  for the 40.000 s file, private); containsSyntheticMedia reads absent
  as on every earlier upload (`media/monkeyhunter/publish.log`)
- publish: the same run set the video public at 2026-09-18T10:32:55+03:00;
  the re-read after 15 s shows privacyStatus public, madeForKids false,
  embeddable true; public at https://youtu.be/Fb-2BqjEcz4

### Quota

- attempt 1 of the hard cap of 5 for the quota day that began
  2026-09-18T10:00 EEST; cost 1 + 1,600 + 3 + 1 + 1 + 1 + 52 = 1,659
  units; day total after one attempt 1,659 units
