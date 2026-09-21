# Produce short: Torricelli jets, three holes in a one metre tank

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day23

## Goal

Backlog idea (trend research 2026-09-20, task 20260920-100347, pillar 2
chaos and physics):
"Torricelli jets: a tank of water 1 m deep on the floor with holes 25,
50 and 75 cm below the surface, the jets drawn as particle streams;
measure where each jet lands; expect the middle hole to reach exactly
1.000 m and the top and bottom holes to tie at 0.866 m (range
2 sqrt(h (H - h)); speeds sqrt(2 g h) = 2.21, 3.13, 3.84 m/s), and a
second beat where the level drops and the top half of the water leaves
in 29.3 percent of the emptying time; deterministic, no seed."
Day twenty-three, second slot. Chosen because continuous water motion
with one plain question is a proven format on the channel (tsunami 929
views, water wheel 923, ripple tank 432) and the answer is a genuine
surprise: the lowest hole, with the most pressure, does not shoot the
farthest. One claim only: the landing distances of the three jets at a
constant level (the tank is kept full). The emptying beat goes to the
description or is dropped; do not narrate a second claim.
Question in the first two seconds: "Three holes in a full tank. Which
jet lands farthest?" (or the producer's better wording, kept identical
in the title, the hook and the payoff).

## Claim

From a tank one meter deep, the jet from the middle hole lands one
meter out and the jets from the top and bottom holes tie short of it.
Every number in the narration is printed by the sim before the script is
written.

## Evidence

### Measurements

(recorded after the measure-only run, before scripting)

`sims/torricelli/torricelli.py --measure-only` with
`projects/torricelli/manifest.json` (a tank of water H = 1 m deep
standing on the floor and kept full, so the level is constant; three
holes in its right wall h = 0.25, 0.50 and 0.75 m below the surface;
each hole emits a horizontal jet at the Torricelli speed sqrt(2 g h),
drawn as a stream of particles, one every 0.0125 s of simulated time
(80 per second), each particle in closed-form free fall to the floor;
g = 9.80665 m/s^2; no air drag; the landing distance is measured by
stepping one particle at 3,600 steps per second (dt = 2.78e-4 s) with
the exact constant-acceleration update and locating the floor crossing
by interpolation inside the crossing step; played at 1/4 speed;
deterministic, no seed; run at 10:16 EEST, log in
`media/torricelli/measure.log`):

- closed forms: exit speed v = sqrt(2 g h); fall time t = sqrt(2 (H -
  h) / g); range R = v t = 2 sqrt(h (H - h)); R is largest where h (H -
  h) is largest, at h = H / 2 = 0.5 m, where R = H = 1 m exactly; h and
  H - h give the same range, so the pairs tie
- top hole, 0.25 m below the surface (a quarter of the depth), 0.75 m
  above the floor: exit speed 2.2143 m/s; fall time 0.3911 s; the
  stepped particle reaches the floor at 0.3911 s (1,408 steps, -4.5e-9
  s) 0.8660 m from the wall (closed form 0.8660 m, -1.0e-8 m), moving
  3.835 m/s down and 2.214 m/s along at the landing (60.0 degrees below
  horizontal); particles 2.77 cm apart along the jet, 32 in flight
- middle hole, 0.50 m down (half the depth), 0.50 m above the floor:
  exit speed 3.1316 m/s; fall time 0.3193 s; the stepped particle lands
  at 0.3193 s (1,150 steps, -2.9e-8 s) 1.0000 m from the wall (closed
  form 1.0000 m, -9.2e-8 m), moving 3.132 m/s down and 3.132 m/s along
  (45.0 degrees); particles 3.91 cm apart, 26 in flight
- bottom hole, 0.75 m down (three quarters of the depth), 0.25 m above
  the floor: exit speed 3.8354 m/s; fall time 0.2258 s; the stepped
  particle lands at 0.2258 s (813 steps, -1.8e-8 s) 0.8660 m from the
  wall (closed form 0.8660 m, -6.9e-8 m), moving 2.214 m/s down and
  3.835 m/s along (30.0 degrees); particles 4.79 cm apart, 19 in flight
- result: the middle jet lands farthest, 1.0000 m from the wall; the
  top jet lands at 0.8660 m and the bottom jet at 0.8660 m, a tie to
  5.9e-8 m; the middle jet beats them by 0.1340 m = 13.4 cm; the bottom
  jet leaves 1.732 times faster than the top jet but flies 1.732 times
  shorter (sqrt(3) both ways)
- check depths (closed form, not drawn): 0.1 m -> 0.6000 m, 0.4 m ->
  0.9798 m, 0.6 m -> 0.9798 m, 0.9 m -> 0.6000 m; a hole at the
  surface or at the floor gives 0 m
- draining note (closed form, not drawn, not narrated): if the tank
  were left to drain through one hole in its bottom the level would
  fall as H (1 - t / T)^2, so the top half of the water leaves in 29.3
  percent of the emptying time T and the bottom half takes the other
  70.7 percent
- schedule printed by the sim (1/4 speed; one particle every 3 frames
  from each open hole, 800 emissions in the 40 s scene, so the streams
  are periodic and frame 2,400 equals frame 0; all three jets flow from
  the first frame; first draft: holes close at 14.6 s, last particle
  out 14.550 s, bottom stream lands out by 15.45 s, middle by 15.83 s,
  top by 16.11 s; bottom re-opens 17.5 s and its first particle lands
  18.40 s; top re-opens 20.5 s, lands 22.06 s; middle re-opens 24.0 s,
  lands 25.28 s; the landing mark and label appear at each first
  landing; title until 2.4 s; card from 27 s; loop crossfade over the
  last 0.5 s; the events are re-timed from the voice timing below)
- text widths (DejaVuSans-Bold): overlay 913 px at 34; title lines 811
  and 794 px at 56; tank label 348 px at 28; depth labels 203 px at 28;
  speed labels 154 px at 32; ruler labels 18, 82 and 82 px at 26;
  landing labels 139 and 256 px at 36; payoff lines 560, 338 and 665
  px at 40; nothing over 950 px (the first draft's overlay "tank kept
  full | no air drag | 1/4 speed | no seed" measured 913 px and was
  kept)

Narration numbers: one meter deep (setup, H = 1 m, with the holes a
quarter, half and three quarters of the way down) and the payoff: the
middle jet at one meter out (the 1.0000 m measured, shown as 1.00 m on
the mark and the card) with the top and bottom jets tied at eighty
seven centimeters (the 0.8660 m measured, shown as 0.87 m). The exit
speeds, the fall times, the closed forms, the check depths and the
draining note go to the description. No number contradicted the claim.

### Production

- layout (`sims/torricelli/torricelli.py`): overlay at y 96, title at
  y 190/252 (two lines at 56 px), the tank on the left (water x 40 to
  242, glass walls 8 px, rim 16 px) with its surface at y 460 and the
  floor at y 1160 (700 px per metre), the label "1 m of water, kept
  full" above the rim at y 420, the three holes in the right wall at y
  635/810/985 with a plug drawn when closed, the jets starting at the
  wall's outer face x 250 with a depth label ("0.25 m down", 28 px) and
  a speed label ("2.21 m/s", 32 px, in the jet colour, shown only while
  the hole is open) stacked above each jet; particles of radius 6.5 px
  (teal top, gold middle, coral bottom) with a light core; a floor slab
  44 px deep with the ruler ticks and labels 0, 0.5 m and 1.0 m engraved
  in it; at each first landing a flash ring, a tick on the floor (two
  side by side at the tie point) and a distance label on its own row
  under the slab with a leader from the slab (middle "1.00 m" in gold
  at y 1256; top and bottom "0.87 m" then "0.87 m, a tie" in white at
  y 1304); captions at caption_y 0.75, card from y 1592; geometry drawn
  at 2x and reduced
- streams: one particle every 0.0125 s of simulated time = every 3
  frames at 1/4 speed, 800 emissions in the 40 s scene, so the pattern
  is periodic and frame 2,400 equals frame 0; emission instants are
  global multiples of 3 frames and a hole simply emits at those it is
  open for (negative frames count as open, the tail of the previous
  loop), so the first frame already shows all three jets in flight and
  the last frame runs straight into the first; the crossfade over the
  last 0.5 s fades only the card, the marks and the labels out and the
  title in, the streams run through untouched
- smoke pass 1 (`--frames` at 0, 1.5, 15, 18.6, 22.3, 25.5, 28 and
  39.8 s, 10:16 EEST, before any render): three defects: the middle
  jet's leader line from the floor to the "1.00 m" label ran through
  the "1.0 m" ruler label; the streams read sparse at radius 5.5 px;
  the scene sat high with dead space above the caption band; fixes: the
  floor became a 44 px slab with the ruler labels inside it so the
  leaders start below the slab and cross no label, particle radius
  6.5 px, the whole scene moved 40 px down (surface 420 to 460, floor
  1120 to 1160, label rows to 1256 and 1304); smoke pass 2 (10:17
  EEST, same times) clean: the title clear of the overlay and the tank
  label, the plugged holes with the stream tails still landing at 15 s,
  the tie label and the "1.00 m" label on separate rows with nothing
  crossing, the crossfade at 39.8 s
- narration (written after the measure-only run, 10:18 EEST): three
  hooks tried, "A tank one meter deep, kept full of water. Three holes
  in a full tank. Which jet lands farthest?" (kept: a noun-phrase start,
  the setup number, then the title question in the title's words),
  "Three holes in a full tank. Which jet lands farthest?" (dropped: an
  audio-initial "Three" risks the clipped-onset mishearing seen with
  "Spin" and "Start", and it carries no setup number) and "Which of
  three jets from a full tank lands farthest?" (dropped: "Which" at the
  onset is the same risk as "Where", and the payoff could not repeat it
  in the same words); `projects/torricelli/narration.txt`, 110 words;
  the setup is "one meter deep" with the holes "a quarter, half, and
  three quarters down", the payoffs "The middle jet, at one meter out"
  and "Eighty seven centimeters, for both"; "A tank one meter deep,
  kept full of water" chosen over "A tank of water, one meter deep" so
  captions.py keeps "one meter" in one chunk ("A tank one meter" /
  "deep, kept full of" / "water."); the last sentence reordered to
  "Eighty seven centimeters, for both." so "Eighty seven" is a chunk on
  its own, and "The middle jet, at" / "one meter out." checked with
  chunks() before recording
- voice: `scripts/voiceover.sh projects/torricelli/narration.txt` passed
  on the first run at 10:18:59 EEST with no misheard word (the
  transcript wrote "1 meter", "87 centimeters" and "three quarters" back
  and the normaliser folded them): 110 words, 32.72 s, ends at 33.32 s
  of the 40 s video, 3.4 words/s; log in `media/torricelli/voice.log`
- timing (`scripts/voice-timing.py`, +0.6 s offset, log in
  `media/torricelli/timing.log`): "A tank one meter deep, kept full of
  water. Three holes in a full tank. Which jet lands farthest?" 0.60 to
  6.26 s over the title (to 2.4 s) and the three flowing jets; "The
  holes sit a quarter, half, and three quarters down. Deeper water
  pushes harder." 6.26 to 10.75 s; "so the lower hole makes the faster
  jet, but a low jet has little height to fall, so little time to fly."
  10.75 to 16.38 s with the holes closing at 14.0 s and the streams
  landing out by 15.51 s; "The bottom jet leaves fastest and hits the
  floor at once. The top jet has the most height." 16.38 to 21.21 s
  with the bottom hole re-opening at 17.0 s and its first particle
  landing at 17.90 s (about when "hits the floor" is spoken), then the
  top hole re-opening at 19.8 s; "But it is slowest." 21.21 to 22.35 s
  with the top jet landing at the tie point at 21.36 s; "The middle jet
  balances speed and time. So which jet lands farthest? The middle
  jet." 22.35 to 27.48 s with the middle hole re-opening at 22.5 s,
  landing at 23.78 s, and the card fading in from 25.4 s (lit by 26.0
  s); "At one meter out." 27.48 to 28.79 s; "The top and bottom jets
  tie, short of it." 28.79 to 31.14 s; "Eighty seven centimeters for
  both." 31.14 to 33.32 s with the card on; all three jets flow to the
  end with no narration from 33.3 s
- schedule decisions: close_at 14.0 s (streams drained by 15.51 s,
  before the bottom re-opens at 17.0 s); open_at bottom 17.0 s, top
  19.8 s, middle 22.5 s (each a multiple of the 3-frame emission
  period, so the first particle leaves at the re-opening instant); the
  order bottom, top, middle follows the narration (fastest but low,
  highest but slow, the balance); payoff_t 25.4 s so the card is fully
  lit at 26.0 s, after the middle jet's landing (23.78 s) and before
  "The middle jet. At one meter out." (26.0 to 28.79 s); the title
  holds until 2.4 s; loop_fade 0.5 s
- footage: `sims/torricelli/torricelli.py` (no arguments) wrote
  `media/torricelli/footage.mp4`, 40.00 s at 60 fps, 2,400 frames, h264
  crf 16 yuv420p, in 26 s with eight forked workers, 10:19:53 to
  10:20:19 EEST; the same run re-printed every measurement above
  (`media/torricelli/render.log`); loop check printed by the sim: frame
  2,400 (the wrap-around) differs from frame 0 in 0 px; the last frame
  (2,399) differs from the first in 20,236 px, which is the one step of
  particle motion between them (77 particles moving 6 to 10 px)
- compose: `scripts/compose.sh torricelli` wrote
  `media/torricelli/final.mp4` at 10:20:44 EEST (h264 1080x1920 60
  fps, aac 22050 Hz mono, 40.000 s; music seed 72 at gain 0.18;
  captions at caption_y 0.75, 39 drawtext filters); loudness mean
  -16.4 dB, peak 0.0 dB; preview (40.07 s) and 8x5 contact sheet
  written (`media/torricelli/compose.log`)

### Local QA

- smoke pass 1 (10:16 EEST, `--frames` before any render): three layout
  defects found and fixed (the leader through the "1.0 m" ruler label,
  the sparse streams, the high scene; see Production); smoke pass 2
  (10:17 EEST) clean before the footage render
- final pass (10:21 to 10:22 EEST): frames at 0.02, 1.5, 5.0, 11.0,
  14.5, 15.8, 17.9, 18.5, 21.4, 22.0, 23.8, 24.5, 26.2, 27.9, 29.5,
  31.8, 35.0 and 39.95 s extracted from final.mp4
  (`media/torricelli/frame-*.png`) and inspected with the 8x5 contact
  sheet (`media/torricelli/sheet.png`): 0.02 s shows the overlay "tank
  kept full | no air drag | 1/4 speed | no seed" at y 96, the title
  "Three holes in a full tank. / Which jet lands farthest?" at y 190
  to 280 clear of it and of the tank label, and all three jets in
  flight with their depth and speed labels (the thumbnail); 1.5 s shows
  the same under "A tank one meter"; 14.5 s shows the three plugged
  holes with the stream tails still in the air under "little height
  to"; 15.8 s shows the still tank with the plugs and an empty floor
  under "fall, so little time"; 17.9 s shows the bottom jet's first
  particle at the floor under "leaves fastest and"; 21.4 s shows the
  top jet landing on the bottom jet's mark with the teal flash ring,
  the two ticks and the white "0.87 m, a tie" label under "The top jet
  has the"; 23.8 s shows the middle jet's first particle at the 1.0 m
  ruler mark with the gold ring and the "1.00 m" label under "The
  middle jet"; 26.2 s shows the card fully lit ("which jet lands
  farthest? / middle: 1.00 m / top and bottom: 0.87 m, a tie") under
  "So which jet lands"; 27.9 s shows "The middle jet, at" with the card
  and the "1.00 m" label on screen while the voice says "At one meter
  out"; 31.8 s shows "it." with the card's "0.87 m" line on screen
  while the voice says "Eighty seven centimeters" (the caption "Eighty
  seven" runs 31.83 to 32.43 s, the proportional caption timing lags
  the voice by under a second at the end); 35.0 s shows all three jets
  flowing under the card with no caption; 39.95 s shows the crossfade
  almost complete, the title in and the card and labels faint;
  captions match the narration word for word and sit in the y 1440 to
  1520 band with the label rows ending at y 1322 and the card from
  1592; no text clips at the frame edges (the widest on-screen text is
  the overlay at 913 px; the "1.00 m" label ends at x 1019, the tie
  label at 991); the payoff numbers are on screen when spoken (card
  from 25.4 s, "one meter out" at 27.5 s, "eighty seven" at about 31.2
  s); the loop closes: the sim's wrap-around check is 0 px, and in
  final.mp4 frame 2,399 differs from frame 0 in 22,526 px of which
  21,601 are the particle step in the jet region (y 440 to 1180, max
  channel difference 255) and 925 are encoder noise around the
  identical title and overlay text (max channel difference 73, one
  pixel over 64, none over 128); ffprobe: h264 1080x1920 60 fps, 2,400
  frames, aac 22050 Hz mono, 40.000 s, 2,289,012 bytes, moov before
  mdat; md5 539688b340692a54d1db82ee409f8a97; approved

### Metadata

- `projects/torricelli/metadata.json`: title "Three holes in a full
  tank. Which jet lands farthest? The middle: 1.00 m. Top and bottom:
  0.87 m." (97 characters; the first draft with "The middle one" was
  101 and was shortened); description with the setup (the 1 m tank kept
  full, the three holes, the Torricelli exit speed, particle streams in
  closed-form free fall, the stepped-particle landing measurement at
  3,600 steps per second checked against 2 sqrt(h (H - h)), no seed,
  one quarter speed), a Measured list (the three holes' exit speeds,
  fall times and landing distances with the closed forms, the 13.4 cm
  margin and the 6e-8 m tie, the sqrt(3) speed and time ratio, the
  closed forms with the peak at H / 2 and the tying pairs at 0.1/0.9
  and 0.4/0.6 m, the draining note marked not drawn), a Why paragraph
  in plain words (speed grows with the square root of the depth, flight
  time with the square root of the height, the product peaks in the
  middle and is the same for pairs that swap depth for height), the
  rerun line and the AI-made line; 10 tags (Torricelli, Torricelli's
  law, water jet, fluid dynamics, projectile motion, tank with holes,
  physics, physics visualization, simulation, shorts); category 27;
  private; containsSyntheticMedia true; selfDeclaredMadeForKids false
- not uploaded; task left open for the orchestrator's review and upload

### Release

- orchestrator review (10:36 EEST): the task evidence, the 8x5 contact
  sheet and the full-resolution frames at 0.02, 15.8, 21.4, 23.8, 27.9
  and 39.95 s inspected: the question over the three flowing jets with
  the exit speeds at the holes on the first frame; 15.8 s shows the
  holes plugged and the empty floor under "fall, so little time"; 21.4 s
  shows the top jet landing on the bottom jet's mark with "0.87 m, a
  tie" under "The top jet has the"; 23.8 s shows the middle jet landing
  on the 1.0 m ruler mark with "1.00 m" in gold under "The middle jet";
  27.9 s shows the card "which jet lands farthest? / middle: 1.00 m /
  top and bottom: 0.87 m, a tie" under "The middle jet, at"; 39.95 s
  shows the crossfade to the title frame with the marks and the card
  fading out; every caption in the clear band, no clipping; final.mp4
  h264 1080x1920 60 fps, 2,400 frames, aac 22050 Hz mono, 40.000 s, moov
  before mdat, md5 539688b340692a54d1db82ee409f8a97; title 97
  characters; approved for release
- quota check: clock 2026-09-21T10:38:33+03:00; one upload attempt (bigswing, 10:37:09,
  published as AO0xsAawEUw at 10:37:49) recorded since the 2026-09-21
  10:00 EEST boundary (log entry and media/bigswing/upload.log both
  checked); this is insert attempt 2 of the hard cap of 5
- attempt 2 recorded at 2026-09-21T10:38:33+03:00, video name torricelli, before running
  `scripts/yt-upload.py torricelli`

### Published

- upload: `scripts/yt-upload.py torricelli` ran 10:38:33 to 10:38:38 EEST,
  token verified to see only the Seed Zero channel, video id
  oNbFaWeSD44, private (`media/torricelli/upload.log`)
- gate: `scripts/yt-qa.py torricelli oNbFaWeSD44 --wait --publish` ran in
  the foreground from 10:38:47 EEST: processing succeeded and the 10
  tags read back on the first poll, 15 of 15 pass (processed, succeeded,
  hd, 1080x1920, title, description, tags as a set, category 27, not for
  kids, PT41S for the 40.000 s file, private); containsSyntheticMedia
  reads absent as on every earlier upload (`media/torricelli/publish.log`)
- publish: the same run set the video public at 2026-09-21T10:39:19+03:00;
  the re-read after 15 s shows privacyStatus public, madeForKids false,
  embeddable true; public at https://youtu.be/oNbFaWeSD44
- slot resolution: published for the 2026-09-21 quota day

### Quota

- attempt 2 of the hard cap of 5 for the quota day that began
  2026-09-21T10:00 EEST; cost 1 + 1,600 + 54 = 1,655 units (the
  channels.list verification inside yt-upload.py, the insert, the gate
  run's reads, update and re-read as printed by yt-qa.py); day total
  after two attempts 3,309 units

### Repository

- committed as 84cdda2 "Publish the day twenty-three slate" (sims,
  projects, tasks, docs/niche.md, web/data; no media, previews or
  secrets) and pushed to origin/master at 2026-09-21 10:42 EEST
