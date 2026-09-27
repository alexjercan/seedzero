# Produce short: Coin rotation, a coin around a coin beside the same coin along a flat strip

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day29

## Goal

Backlog idea (trend research 2026-09-27, task 20260927-102520, pillar 2
chaos and physics, rolling; read the full entry under "Added by trend
research 2026-09-27" in docs/niche.md):
"Coin rotation: a coin rolled without slipping around an identical coin
beside the same coin rolled along a flat strip as long as the other
rim; measure the turns of a marked point per lap; expect exactly 2
around the coin (R / r + 1; upright again halfway) against exactly 1
along the strip, 4 around a coin of three times the radius (the 1982
SAT keyed 3); one lap is exactly periodic so the short loops;
deterministic, no seed."

Orchestrator notes (2026-09-27, before this brief). The model: a coin
of radius r rolls without slipping around a fixed coin of the same
radius R = r. Its centre moves on a circle of radius R + r; when the
contact point has advanced an arc s along the fixed rim, the centre
has turned theta = s / R about the fixed coin and the rolling coin's
own orientation in the lab frame (a marked arrow on its face) has
turned phi = s / r + s / R = theta (1 + R / r). One lap, s = 2 pi R,
gives phi = 2 pi (R / r + 1) = 4 pi for R = r: exactly 2 turns of the
arrow. The arrow points up again (phi = 2 pi) at s = 2 pi R r / (R +
r) = pi R for R = r: halfway around, on the far side. The same coin
rolled along a flat strip of length 2 pi R (the fixed rim unrolled)
turns phi = s / r = 2 pi: exactly 1 turn. Around a coin of radius 3 r
the count is 4 (the 1982 SAT keyed 3, and every answer offered was
wrong); along a strip as long as that rim, 3. The extra turn is the
centre's own lap around the fixed coin. No slip means the arc rolled on
the moving coin equals the arc covered on the fixed rim (or the strip)
at every instant; print that check. Kinematics only, no seed; pick a
rolling speed so that one lap takes a whole number of frames and the
strip panel finishes at the same instant (the same contact speed on
both), then the scene is exactly periodic and the last frame equals the
first.

State every derived number above as a check the sim must print, not as
a fact: the arrow's lab angle over the lap (4 pi around, 2 pi along),
the count of returns to upright per lap (2 against 1), the point where
the arrow is first upright again (halfway, 180 degrees around), the
no-slip arc check, the centre's path length 2 pi (R + r) = 2 times the
coin's own circumference, and for the description 4 against 3 around a
coin of three times the radius and 3 against 2 around twice the radius.

Drawing: two panels stacked or side by side, the same coin in both with
a bold arrow (or a large single mark) on its face so a full turn is
unmistakable; top, the fixed coin with the rolling coin going around
it; bottom, a flat strip exactly as long as the fixed coin's rim, drawn
as that rim unrolled (the same colour, maybe the rim's tick marks), with
the coin rolling along it; a live "turns" counter on each panel that
counts up continuously (e.g. 1.37) and a marker each time the arrow
points up again; the two panels run at the same contact speed so the
strip coin finishes its strip as the other finishes its lap; several
laps in 40 s; the loop closes on a lap boundary.

Day twenty-nine, second slot. Chosen because the coin rotation paradox
is a famous puzzle almost everyone answers wrong (one turn), it is
continuous visible rolling motion like the turntable ball (974 views),
two panels on the same coin that end on different counts, an exact
integer a closed form checks, and no seed. Question in the first two
seconds: "Roll a coin around a coin. How many times does it turn?" (or
the producer's better wording; keep the words before the question under
nine; keep the question identical in the title, the hook and the
payoff). Whisper heard "coins" as "coin" on 2026-09-08 and "run" as
"runs": write "a coin" and "another coin" in the singular, avoid
"coins", and pre-test the hooks. Setup number: the two coins are the
same size (say it in words; "the same size" is the setup). Payoff
number: two turns, not one; on the flat strip, one turn. The 4 against
3 and the halfway upright point go to the card and the description.
Make the last frame equal the first. Measure every fixed text line with
PIL before rendering and keep every line under 950 px, and the title
under 100 characters with no < or >. Music seed 90.

## Claim

A coin that rolls without slipping around a fixed coin of the same size
turns exactly 2 times per lap (the arrow's lab angle grows 4 pi) and is
upright again halfway around, at 180 degrees on the far side. The same
coin rolled along a flat strip exactly as long as that rim turns 1 time
(2 pi). Its centre travels 2 pi (R + r), 2 times the coin's own
circumference, around the coin and 1 time along the strip; the extra
turn is the lap of the line of centres. Narrated: same coin, same size
(setup); one turn halfway around; two turns per lap; once along the
strip; the centre travels twice as far so the coin turns twice; two
turns, not one; along the strip, one turn. Card: 2 turns around, 1 turn
along the strip, upright again halfway around, 4 turns around a coin 3
times as big. Description: 3 against 2 for twice the radius, 4 against
3 for three times (the 1982 SAT keyed 3).

## Evidence

### Measurements

`nix develop -c python3 sims/coinroll/coinroll.py projects/coinroll/manifest.json --measure-only`
at 10:50:31 EEST, media/coinroll/measure.log, copied whole:

```
setup: a coin of radius r rolls without slipping around a fixed coin of radius R = 1 r (the same size), and the same coin rolls along a flat strip of length 2 pi R = 6.2832 r, the fixed rim unrolled; the contact point advances at v = 0.9817 r/s on both panels, so a lap of the rim and the strip both take 6.4 s (384 frames), then both hold 3.6 s at the end; 4 laps of 10 s in 40 s; sampled at 100 steps per frame (dt = 1.67e-04 s); drawn at 100 px per r; kinematics only, deterministic, no seed
around: over one lap (s = 2 pi R = 6.2832 r) the arrow's lab angle grows to 12.5664 rad = 4.0000 pi = 2.0000 turns (closed form 2 pi (R / r + 1) = 4.0000 pi); the arrow is upright again 2 times per lap: first at s = 3.1416 r = 0.5000 of the rim, theta = 180.00 degrees, 3.200 s into the roll (halfway, on the far side; closed form s = 2 pi R r / (R + r) = 3.1416 r), then at s = 6.2832 r, theta = 360.00 degrees, 6.400 s (back at the start); relative to the line of centres the coin turns s / r = 1.0000 turn per lap and the line of centres itself turns 1.0000 turn: 2.0000 in all
along: the same coin rolls the strip (s = 2 pi R = 6.2832 r) at the same contact speed in 6.4 s; the arrow's lab angle grows to 6.2832 rad = 2.0000 pi = 1.0000 turn (closed form s / r = 2 pi); upright again 1 time per strip, at s = 6.2832 r, the end of the strip, 6.400 s
no slip: the arc of the rolling coin's rim that has touched, r (phi - theta), matches the arc covered on the fixed rim, R theta, within 4.0e-12 r at every sample around, and r phi matches s within 2.0e-12 r along; the material point of the rolling coin at the contact moves at most 2.7e-08 v around and 4.5e-09 v along (central differences over 3.3e-04 s): it rests on the rim, it rolls, it does not slide; at the end of a lap the whole rim of the rolling coin, 2 pi r = 6.2832 r, has touched, 1.0000 times its own rim, so the painted arcs close together
centre: the rolling coin's centre travels 12.5664 r per lap around the coin (closed form 2 pi (R + r) = 12.5664 r), 2.0000 times the coin's own circumference 2 pi r = 6.2832 r, at 1.9635 r/s; along the strip it travels 6.2832 r, 1.0000 times, at 0.9817 r/s; the extra turn around the coin is the lap of the line of centres
for the description: around a coin of 2 times the radius the arrow turns 3.0000 turns per lap (upright again 3 times, first at theta = 120.00 degrees) against 2.0000 along a strip as long as that rim (upright 2 times); R / r + 1 = 3; around a coin of 3 times the radius the arrow turns 4.0000 turns per lap (upright again 4 times, first at theta = 90.00 degrees) against 3.0000 along a strip as long as that rim (upright 3 times); R / r + 1 = 4 (the 1982 SAT keyed 3 for the coin of 3 times the radius)
schedule (video time): 4 laps of 10 s (600 frames), each rolling 6.4 s (384 frames) and holding 3.6 s at the end; lap boundaries (the strip coin jumps back to the start, the counters reset, the painted rims clear) at 5.0, 15.0, 25.0, 35.0 s; the arrow is upright again halfway around at 8.2, 18.2, 28.2, 38.2 s; back at the start with the counters at 2.00 and 1.00 (the strip coin at the end of the strip) at 1.4, 11.4, 21.4, 31.4 s, holding until the next boundary; on the first frame the coin is 5.00 s into a roll, 78.1 % of the way around (theta = 281 degrees), the counters read 1.56 and 0.78 turns; title until 3 s, then the legend and the tag, the counters from 5 s; payoff card from 29.2 s; the title fades back in over the last 0.5 s and the last frame repeats the first (the scene is periodic: 40 s holds exactly 4 laps)
text widths: overlay@34 880 px, title line 1@56 611 px, title line 2@56 524 px, title line 3@56 401 px, legend@40 756 px, tag@28 888 px, label around@40 632 px, label along@40 813 px, counter word@28 84 px, counter around@40 99 px, counter along@40 232 px, payoff line 1@40 431 px, payoff line 2@40 670 px, payoff line 3@40 849 px, payoff line 4@40 669 px, payoff line 5@40 814 px
```

The first measure run (10:44, before the narration) used an 8.0 s roll
per 10 s lap: v = 0.7854 r/s, centre 1.5708 r/s, no-slip residuals
6.3e-12 r around and 3.2e-12 r along, contact-point speed 1.7e-08 v and
2.9e-09 v. Every turn count, angle, length and ratio above was identical
in that run; only the speed-dependent numbers changed when the roll was
shortened to 6.4 s (plus a 3.6 s hold) so the lap ends land on the
narrated words. The narration uses none of the speed-dependent numbers.
Its first version failed the width assert (payoff line 4 at 1339 px);
the card was split into five lines and re-measured.

### Production

- Sim: sims/coinroll/coinroll.py with projects/coinroll/manifest.json
  (seed 0, fps 60, coin_radius_px 100, fixed_radius_ratio 1.0, lap_s
  10.0, roll_s 6.4, laps 4, lap_at 5.0, counters_from 5.0, substeps 100,
  rim_ticks 12, scene_duration 40.0, title_until 3.0, payoff_t 29.2,
  payoff_hold 0.6, loop_fade 0.5, music_seed 90, music_gain 0.18,
  voice_offset 0.6, caption_y 0.75). Kinematics only: s = v t, theta =
  s / R, phi = s / r + s / R, uprights by interpolation at 2 pi k. The
  phase of a frame comes from the frame integer modulo the lap frames,
  so the scene is exactly periodic; the last frame is the live frame 0.
- Layout (1080x1920): overlay at y 96 (34 px teal, drawn by compose);
  title three rows at y 172, 234, 296 (56 px) until 3 s, then the legend
  "same coin, same size, no slipping" at y 236 (40 px) and the tag "the
  arrow counts the turns; red is the rim already rolled" at y 290 (28
  px); panel labels at y 360 and 1086 (40 px); geometry layer y 330 to
  1420 drawn at 2x and downsampled; fixed coin centre (540, 700) at 100
  px per r, the rolling coin's centre on the circle of radius 200 px;
  strip at y 1331 from x 226 to 854 (2 pi R = 628 px) with 13 ticks and
  a gold start notch; "turns 1.00" counter for the strip at y 1392; the
  around counter ("turns" at 28 px, the number at 40 px) sits on the
  fixed coin's face; captions at y 1440 (64 px); payoff card five gold
  40 px rows from y 1592, step 56. The coin is a gold disc with a coral
  arc for the rim already rolled and a dark arrow from -0.5 r to 0.82 r;
  a faint gold ghost ring with an up arrow marks where the arrow is next
  upright; the teal trail is the centre's path.
- Hook pre-tests (media/coinroll/hooks/pretest.log, 10:45:18 to
  10:46:21 EEST), each through scripts/voiceover.sh, all seven passed on
  the first pass; question onset = first silence_end (n=-35dB d=0.08)
  plus 0.6 s: hook1 "Roll a coin around a coin." 2.30 s; hook2 "Roll a
  coin around another coin." 2.85 s; hook3 "A coin rolls around a coin."
  2.58 s; hook4 "Roll a coin around a coin, how many times" 2.41 s;
  hook5 "A coin around a coin." 2.28 s; hook6 "Coin around a coin." 1.98
  s; hook7 "A coin around a coin, how many times" 2.20 s. Kept hook6.
- Narration: projects/coinroll/narration.txt, 105 words, the question
  at words 5 to 10, identical in the title, the hook and the payoff;
  numbers as words; American "center"; no whisper-risk words.
- Voice (media/coinroll/voice.log): pass 1 at 10:46:45 (103 words,
  payoff "How many times does it turn? Two turns, not one.") failed,
  whisper dropped "turn" (diff token 93). Pass 2 at 10:47:37 ("Around
  the coin, two turns, not one.", 106 words) passed at 33.785 s, but
  the 20-character caption chunks would have split "Around the coin,
  two" from "turns, not one.", so the line was reworded. Pass 3 at
  10:49:32 ("It makes two turns, not one.", 105 words): "ok: transcript
  matches narration (34.365533s) -> media/coinroll/voice.wav". The
  voice ends at 34.97 s of video.
- Timing (scripts/voice-timing.py media/coinroll/voice.wav 0.6, in
  media/coinroll/timing.log): 0.60 to 4.42 "Coin around a coin. How
  many times does it turn? Same coin"; 4.42 to 5.51 "same size."; 5.51
  to 7.67 "Watch the arrow. Halfway around,"; 7.67 to 10.61 "the arrow
  points up again. That is one turn already."; 10.61 to 11.58 "Back at
  the start,"; 11.58 to 13.51 "it points up again. Two turns."; 13.51
  to 16.04 "Now the same coin rolls along a flat strip,"; 16.04 to
  20.37 "exactly as long as the rim it went around. Same speed, same
  distance."; 20.37 to 21.49 "It turns once,"; 21.49 to 22.48 "and that
  is all."; 22.48 to 23.61 "Around the coin,"; 23.61 to 25.71 "the
  center travels twice as far,"; 25.71 to 29.11 "so the coin turns
  twice. So, coin around a coin."; 29.11 to 30.80 "How many times does
  it turn?"; 30.80 to 34.97 "It makes two turns, not one. Along the
  flat strip, one turn." Question onset on the full take: first
  silence_end 1.425 s in the wav plus 0.6 = 2.03 s (media/coinroll/
  silences.log).
- Schedule: laps of 10 s with a 6.4 s roll and a 3.6 s hold, lap_at 5.0
  so the coin is back at the start with the counters at 2.00 and 1.00
  at 1.4, 11.4, 21.4, 31.4 s and holds until 5.0, 15.0, 25.0, 35.0 s;
  halfway uprights at 8.2, 18.2, 28.2, 38.2 s. "the arrow points up
  again" (7.67 to 10.61) covers the 8.2 s upright; "Back at the start,
  it points up again. Two turns." (10.61 to 13.51) covers the lap end
  at 11.4 s with the counter at 2.00; "It turns once," (20.37 to 21.49)
  covers the strip end at 21.4 s with the strip counter at 1.00; the
  card (payoff_t 29.2, lit at 29.8) lights inside the spoken question
  (29.11 to 30.80) while the 28.2 s upright is on screen; "It makes two
  turns, not one." (30.80 to 33.0) covers the lap end at 31.4 s; the
  strip counter reads 1.00 for "Along the flat strip, one turn." (33.0
  to 34.97). Counters are hidden until 5.0 s so the opening hold (1.4
  to 5.0 s) does not show 2.00 and 1.00 before the question is answered.
- Smoke frames (--frames, 10:50:33): 15 PNGs at 0.0, 2.0, 3.5, 5.0,
  8.2, 11.4, 13.0, 15.0, 21.4, 23.0, 29.85, 31.4, 33.5, 39.6, 39.98 s,
  each viewed and the caption band (y 1440 to 1530) and overlay band
  (y 96 to 130) scanned. First pass: the title's third row ended 6 px
  above the top panel label at y 350; the label moved to y 360. All
  other rows clear: title rows do not touch the labels, the card rows
  sit below the captions, the strip counter sits above the caption band.
- Footage: render 10:50:51 to 10:51:16 (media/coinroll/render.log):
  loop check 0 px, periodicity check 0 px, loop step 15,854 px;
  media/coinroll/footage.mp4 3,580,216 B, 2400 frames.
- Compose: scripts/compose.sh 10:51:16 to 10:51:28 (compose.log): music
  seed 90, 40.00 s; captions 35 chunks; final.mp4 40.000000 s; preview
  40.066667 s; sheet 8x5 at 1 fps.
- Text widths (PIL, from measure.log, all under 950 px): overlay 880,
  title 611 / 524 / 401, legend 756, tag 888, label around 632, label
  along 813, counter word 84, counter around 99 (fits the 160 px limit
  on the coin face), counter along 232, payoff 431 / 670 / 849 / 669 /
  814.

### Local QA

- Frames extracted from media/coinroll/final.mp4 (never edited) and
  viewed with the Read tool:
  - frame-0.02.png: overlay, three title rows ("Coin around a coin." /
    "How many times" / "does it turn?"), both panel labels, the coin 78
    % around with the arrow down-left and the coral rim arc, the strip
    coin partly along with its coral arc, ghost ring below the fixed
    coin; no counters, no caption, no card. Clean.
  - frame-2.0.png: title still up, caption "How many times does" at y
    1440; the coin back at the start with the arrow up (the lap ended
    at 1.4 s), the strip coin at the end of the strip with the arrow
    up; counters hidden.
  - frame-8.2.png: legend and tag in place of the title; the coin
    halfway around, at the bottom, arrow up, the fixed coin's face
    reads "turns 1.00"; the strip coin mid-strip, arrow down, "turns
    0.50"; caption "again." Upright halfway lands on the word.
  - frame-11.4.png: the coin back at the start, arrow up, "turns 2.00";
    the strip coin at the end, "turns 1.00"; caption "Back at the
    start,".
  - frame-21.4.png: same geometry, "turns 2.00" and "turns 1.00";
    caption "It turns once, and".
  - frame-29.85.png: the card lit (five gold rows, "2 turns around, 1
    turn along the strip" the third), the coin mid-roll at "turns
    1.52", the strip coin at "turns 0.76"; caption "How many times
    does". The card is on screen inside the spoken question.
  - frame-31.4.png: the coin at the start, "turns 2.00", the strip
    coin at the end, "turns 1.00"; caption "It makes two turns,"; card
    lit. The payoff number is on screen twice when it is spoken.
  - frame-33.5.png: same, caption "Along the flat"; strip counter 1.00
    for "one turn".
  - frame-39.98.png: title back, counters gone, the coin 78 % around
    and the strip coin partly along, the same picture as frame-0.02.
  - sheet.png (40 thumbnails at 1 fps): the title for the first 3 s,
    then the legend and tag; four laps with the counters resetting at
    5, 15, 25, 35 s; captions readable in every thumbnail from 1 to 34
    s; the card from 30 s; no clipped text, nothing at the frame edge.
- Question: on screen from frame 0 in the title (three rows, 611 / 524
  / 401 px), spoken from 2.03 s ("How many times does" caption 1.909 to
  3.218, "it turn?" 3.218 to 3.873). The brief asked for the question
  inside two seconds; 2.03 s is 0.03 s over (day 28 accepted 1.90 s).
- Captions: media/coinroll/captions.filter, 35 chunks, 105 words,
  matches projects/coinroll/narration.txt word for word (script check
  True), longest chunk 20 characters; "Two turns." 12.710 to 13.364,
  "It makes two turns," 31.038 to 32.347, "not one." 32.347 to 33.002,
  "strip, one turn." 33.984 to 34.966.
- Bands: signalstats over all 2,400 footage frames: the caption band
  (rows 1420 to 1530) and the overlay band (rows 96 to 130) have YMAX
  28 in every frame (background only; text is at 213 and above), so
  the sim draws nothing under the captions or the overlay. An earlier
  RGB scan (max deviation 2 levels, 0 frames over 8) had a short pipe
  read and counted 2378 and 2331 frames; the signalstats scan counts
  all 2,400.
- Loop: footage last frame equals the first (0 px). In final.mp4 frame
  2399 against frame 0: 36,883 px over 8 levels, 1,153 over 32, max 96,
  mean 0.41 (h264 quantisation, the same order as day 28); loop step
  17,563 px, so the seam is no larger than one frame of motion.
- ffprobe: h264 1080x1920 yuv420p 60/1, 2400 frames; aac 22050 Hz mono;
  40.000000 s; 3,829,571 bytes; moov before mdat.
- md5sum media/coinroll/final.mp4: 79531a7164ea0cac01ae7fe8b0153b17
- Narrated numbers against measure.log: "same size" (R = 1 r); "one
  turn" halfway (upright at theta = 180.00 degrees, 0.5000 of the rim);
  "Two turns" (2.0000 turns, 4.0000 pi); "turns once" (1.0000 turn,
  2.0000 pi); "twice as far" (centre 12.5664 r = 2.0000 times 6.2832
  r); "two turns, not one" and "one turn" (2.0000 against 1.0000). Card
  "4 turns around a coin 3 times as big" (4.0000 turns, R / r + 1 = 4).
- Metadata check: the description had been drafted with the 10:44
  run's speed-dependent numbers (v 0.7854 r/s, centre 1.5708 r/s,
  residuals 6.3e-12 / 3.2e-12 r, 1.7e-08 / 2.9e-09 v); corrected to the
  10:50:31 measure.log (0.9817 r/s, 1.9635 r/s, 4.0e-12 / 2.0e-12 r,
  2.7e-08 / 4.5e-09 v) and every number in the description checked
  against the log.

### Metadata

projects/coinroll/metadata.json: title "Coin around a coin: how many
times does it turn? 2 turns around, 1 turn along a flat strip" (90
characters); description 3,146 characters with the model, the
"Measured:" list, the "Why:" paragraph (1982 SAT, keyed 3, answer 4,
question voided), the rerun line and the AI-made line; 11 tags;
categoryId 27; privacyStatus private; containsSyntheticMedia true;
selfDeclaredMadeForKids false; no angle brackets.

### Deviations from the brief

- Hook "Coin around a coin." instead of "Roll a coin around a coin.":
  the pre-tests put the question at 1.98 s against 2.30 s. The title,
  hook and payoff all carry the same question.
- Question onset 2.03 s on the full take (1.98 s in the pre-test).
- Each 10 s lap is a 6.4 s roll and a 3.6 s hold, not continuous
  rolling: the hold keeps the counters at 2.00 and 1.00 on screen for
  the narrated words, and at each boundary (5, 15, 25, 35 s) the strip
  coin jumps back to the start and the painted rims clear.
- The loop seam is at 78 % of a roll, not at a lap boundary: 40 s holds
  exactly 4 laps so the last frame equals the first anyway, and the seam
  is continuous motion instead of the strip coin's jump.
- Counters are hidden until 5.0 s so the opening hold does not answer
  the question before the narration does.
- The card has five lines (line 4 of the four-line draft was 1339 px).

## Niche note

[produced 2026-09-27 as "Coin around a coin: how many times does it
turn? 2 turns around, 1 turn along a flat strip"; measured 2.0000 turns
per lap around a coin of the same size (4.0000 pi, upright again halfway
at theta = 180.00 degrees) against 1.0000 along a strip as long as the
rim, centre path 2 pi (R + r) = 2.0000 times the circumference, no-slip
arc match within 4.0e-12 r; 3 against 2 for twice the radius and 4
against 3 for three times (the 1982 SAT keyed 3); task 20260927-103223]

## Upload

- orchestrator review (2026-09-27T11:12:08+03:00): task evidence, sheet.png and frames at 0.02,
  8.2, 31.4 and 39.98 s inspected; numbers match measure.log and the closed
  form R / r + 1; approved for upload
- upload attempt 2 of 5 for the quota day that began 2026-09-27T10:00
  EEST, recorded at 2026-09-27T11:12:08+03:00 before starting scripts/yt-upload.py; one attempt
  (cutshot, published as aEgJbsPwqeo) was on record since the boundary
- uploaded private as myMUuK-p_L8 at 11:12:11 EEST (media/coinroll/upload.log);
  scripts/yt-qa.py --wait --publish: gate 15 of 15 (PT41S for the 40.000 s
  file), set public at 11:12:54 EEST and re-read public
  (media/coinroll/publish.log); https://youtu.be/myMUuK-p_L8
- attempt 2 of 5 complete at 2026-09-27T11:13:26+03:00: 1,655 units (1 channels read, 1,600
  insert, 54 gate, update and re-read)
- slot resolution: published for the 2026-09-27 quota day at 11:12:54 EEST,
  https://youtu.be/myMUuK-p_L8

### Quota
- attempt 2 of the hard cap of 5 for the quota day that began
  2026-09-27T10:00 EEST; cost 1 + 1,600 + 54 = 1,655 units (the
  channels.list verification inside yt-upload.py, the insert, the gate
  run's single read, update and re-read as printed by yt-qa.py); day total
  after three attempts 1,655 + 1,655 + 1,653 = 4,963 units plus 5 for the
  10:02 stats refresh and 5 for the 11:17 refresh, target of three met

### Repository
- committed as 042e398 "Publish the day twenty-nine slate" (sims,
  projects, tasks, docs/niche.md, web/data; no media, previews or
  secrets) and pushed to origin/master at 2026-09-27 11:18 EEST on top of
  21b9197
