# Produce short: Tsunami shoaling, a one meter wave meets the shore

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day21

## Goal

Backlog idea (trend research 2026-09-16, task 20260916-100924):
"Tsunami shoaling: a 1 m wave in 4,000 m of water runs onto a slope that
ends at 10 m depth, beside the same wave in a flat 4,000 m tank; measure
the speed and the crest height; expect 198 m/s slowing to 9.9 m/s
(sqrt(g h)) and the crest growing to 4.5 m (Green's law, (4000/10)^(1/4))
with the wavelength 20 times shorter; 1D shallow water solver, no
breaking; deterministic, no seed (peg: World Tsunami Awareness Day
2026-11-05)."
Day twenty-one, first slot. Chosen because it is continuous motion with
one visible causal story (the seabed rises, the wave slows, the wave
grows), one plain question, one setup number (a one meter wave) and one
payoff number (the crest height at the shore) that a closed form checks.
Question in the first two seconds: "A one meter wave at sea. How tall at
the shore?"

## Claim

A one meter wave in four thousand meters of water grows to four point
four meters by the time the water is ten meters deep (measured 4.385 m;
Green's law says 4.47, and the two percent short is real: a single hump
leaves a long low wave behind on the slope), and slows from about two
hundred meters a second to ten. Every number in the narration is printed
by the sim before the script is written.

## Evidence

### Measurements

(recorded after the measure-only run, before scripting; the video times
were re-recorded from the render run after the timeline moved to the
voice, see Production; the physics numbers are the same in both runs)

`sims/tsunami/tsunami.py --measure-only` with
`projects/tsunami/manifest.json` (1D linear shallow water, eta_t + (h u)_x
= 0, u_t + g eta_x = 0, g = 9.80665, on an Arakawa C grid, dx = 100 m,
dt = 0.25 s, Courant 0.495 in the deepest cell, staggered leapfrog, closed
walls at x = 0 and 3,800 km; sea floor flat at 4,000 m to x = 2,700 km,
then h = 4000 ((x_apex - x) / 1000 km)^2 with x_apex = 3,700 km, a 950 km
slope down to 10 m at x = 3,650 km (sea-floor slope 0.0080 at the top,
0.00040 at the foot), then a flat 10 m shelf; on this profile sqrt(h) is
linear in x so the local wavelength shrinks by the same 0.10 m per metre
travelled everywhere on the slope; the wave is a Gaussian hump of height
exactly 1 m and 100 km wide at half height (sigma 42.47 km) centred at
x = 1,850 km at t = 0, launched right-going, u = eta sqrt(g / h); 28,800 s
(8 h) of sea time shown in 40 s at time x720, 12 s per frame, 48 steps per
frame; control: the same hump in a flat 4,000 m tank 8,000 km long for the
same time; linear, no breaking; deterministic, no seed; measure-only log
in `media/tsunami/measure.log` (10:32 EEST, with the hump starting at
1,500 km and the shelf ending at 3,780 km), the final geometry's full
printout in `media/tsunami/render.log` (10:36 EEST)):

- closed forms: sqrt(g h) = 198.06 m/s at 4,000 m and 9.903 m/s at 10 m;
  Green's law (4000 / 10)^(1/4) = 4.4721, so 1 m would become 4.472 m at
  10 m; the width at half height scales with sqrt(h), 20.0 times shorter
  at 10 m (5.0 km); the crest reaches the slope after 4,292 s (5.96 s of
  the video), crosses it in 15,126 s (21.01 s; closed form L_apex /
  c_deep times ln 20) and reaches the shelf at 19,417 s (26.97 s); the
  crest passes 1,000 m at 10.82 s of the video, 100 m at 18.89 s, 30 m at
  23.12 s, 10 m at 26.97 s
- main run, deep flat section (x = 2,275 km, 2.98 s of the video): crest
  1.0000 m, speed 198.06 m/s against sqrt(g h) 198.06, width 100.00 km
- crest at the check depths (measured against Green's law, speed against
  sqrt(g h), width against 100 km sqrt(h / 4000)): 1,000 m (10.82 s):
  1.4262 m against 1.4142, 99.05 m/s against 99.03, 50.35 km against
  50.00; 100 m (18.89 s): 2.5168 m against 2.5149, 31.32 against 31.32,
  15.83 km against 15.81; 30 m (23.11 s): 3.3872 m against 3.3981, 17.16
  against 17.15, 8.65 km against 8.66; 10 m, the foot of the slope
  (19,415 s, 26.96 s): 4.3851 m against 4.4721, 9.90 against 9.90, 5.02 km
  against 5.00
- on the shelf, 20 km past the foot (x = 3,670 km, 21,435 s, 29.77 s of
  the video): crest 4.3849 m against Green 4.4721 (ratio 0.9805), speed
  9.900 m/s against 9.903, width 4.931 km against 5.000, a factor 20.28
  shorter than at the start; at the end of the scene (28,788 s) the crest
  is 4.3842 m at x = 3,743 km, 92.8 km onto the shelf, at 9.900 m/s;
  largest crest over the run 4.3851 m at 26.98 s
- energy (the discrete 0.5 g eta^2 + 0.5 h u_{n-1/2} u_{n+1/2} that the
  staggered leapfrog conserves exactly): 7.381384e5 J/m at the start and
  at the end, relative drift +6.3e-16, largest excursion 2.8e-15; volume
  0.1064 km^2 conserved to 6.8e-16
- reflection: the slope sends a long low wave back into the deep water;
  its left-going part (eta - u sqrt(h / g)) / 2, exact in the flat
  section, is 0.0135 m when the crest enters the slope and 0.0265 m
  (2.65 % of 1 m) when the crest reaches the foot (largest over the run
  0.0266 m at 25.60 s); it reaches the wall at x = 0 no earlier than
  17,924 s (24.9 s of the video), where it doubles to 0.0531 m, and its
  bounce cannot be back at the slope before 31,557 s, after the 28,800 s
  run; on the slope itself the largest |eta| more than three half-height
  widths behind the crest is 0.0410 m (4.10 % of 1 m) when the crest
  reaches the foot and 0.160 m at most over the run (28.50 s), which is
  the trough drawn down right behind the hump: -0.046 m at the foot,
  -0.1665 m on the shelf (Green's law grows the trough too); the hump
  (within three half-height widths of the crest) holds 0.1064 km^2 of
  water at the start, 0.0231 km^2 (21.7 %) at the foot and 0.0213 km^2
  (20.0 %) on the shelf, the rest is the wave sent back and the trough
- why 4.385 and not 4.472: Green's law is the leading (WKB) order for a
  wave short against the slope; on this profile the equation in travel
  time is a Klein-Gordon equation with cutoff period 4 pi L_apex / c_deep
  = 17.6 h, so the hump's longest-period part is sent back (the 2.65 %
  plateau) and its long-period part lags into a trailing trough; the
  crest arrives 2 % short. Checked with the first geometry: a 50 km hump
  loses 1.0 % (4.4261 m), rounding the slope's top over 200 km changes
  nothing (4.3801 m), so the kink is not the cause
  (`media/tsunami/diag2.py`, scratch, not tracked); a 25 km hump at this
  grid gives 4.3102 m (1.25 km wide on the shelf, 12 cells,
  under-resolved), so the 100 km hump at 50 cells per width on the shelf
  is the resolved choice
- check at half the grid step with half the time step (dx = 50 m, dt =
  0.125 s): 1.4262 / 2.5168 / 3.3871 / 4.3847 m at the check depths and
  4.3847 m on the shelf against 1.4262 / 2.5168 / 3.3872 / 4.3851 and
  4.3849 at the full step; speeds 99.05, 31.32, 17.16, 9.91, 9.902 m/s;
  energy drift +3.5e-15
- check at half the time step alone (dt = 0.125 s): 4.3851 m at the foot,
  4.3849 m on the shelf, every check-depth number equal to four decimals;
  energy drift -3.5e-15
- control (flat 4,000 m tank, same hump, same time): crest 1.0000 m, speed
  198.06 m/s, width 100.00 km at 21,444 s (when the slope run is 20 km
  onto the shelf, x = 6,097 km) and at the end (x = 7,552 km); crest
  between 1.0000 and 1.0000 m over the run; energy drift -1.6e-16

Decisions: the claim's "about four and a half meters" became four point
four meters (measured 4.385 m; readouts and card show 4.4 m). The first
domain (deep section 1,200 km, hump at 200 km) let the wave sent back
bounce off the wall at x = 0 and return to the slope during the run, off
screen but untidy; the deep section was lengthened to 2,700 km so the
bounce cannot return before the run ends. The control tank was
lengthened from 6,000 to 8,000 km after a run showed the control hump
hitting its far wall (crest 1.9995 m there). Green's law is stated as the
closed form with the 2 % shortfall explained in the description; the
speeds are not narrated as numbers (readouts and the card show 198 and
9.9 m/s).

Narration numbers: one meter (setup, the 1.0000 m hump), ten meters deep
(the shelf depth, the place of the payoff), four point four meters
(payoff, the 4.3849 m crest on the shelf). The 4.47 closed form, the
speeds, the 20.28 width ratio, the reflection, the trough, the energy and
the checks go to the description.

### Production

- narration (written after the measure-only run): three hooks tried,
  "A one meter wave at sea. How tall at the shore?" (kept, it is the
  title's words and names the setup number), "This wave is one meter tall
  at sea. How tall will it be at the shore?" and "One meter at sea. How
  tall at the shore?"; `projects/tsunami/narration.txt`, 108 words; the
  setup number is one meter, the payoff four point four meters (at the
  shore, where the water is ten meters deep); the speeds are not
  narrated as numbers (the readouts and the card show 198 and 9.9 m/s)
- voice: `scripts/voiceover.sh projects/tsunami/narration.txt` failed on
  the first run at 109 words: whisper wrote "sea floor" as "seafloor"
  (twice) and "the wave is four" as "the waves four"; "sea floor" became
  "ocean floor" (the on-screen minimap label too) and "the wave is four
  point four meters tall" became "it is four point four meters tall";
  the second run passed at 10:41 EEST (108 words, 30.38 s, ends at
  30.98 s of the 40 s video, 3.55 words/s); log in
  `media/tsunami/voice.log`; timing (`scripts/voice-timing.py`, +0.6 s
  offset, `media/tsunami/timing.log`): "A one meter wave at sea, how
  tall at the shore?" 0.60 to 3.16 s over the title (to 2.4 s); "Out in
  the deep ocean, this wave is one meter tall and fast" 3.16 to 6.85 s
  with the readouts at 4,000 m, 198 m/s, 1.0 m; "Now the ocean floor
  rises" 6.85 to 8.79 s; "The water gets shallower, and the wave slows
  down" 8.79 to about 11.5 s; "The back of the wave is in deeper water,
  so it moves faster, and it catches up with the front" about 11.5 to
  16.5 s; "The wave gets narrower and taller" to 18.63 s; "The shallower
  the water, the slower the wave, and the taller it grows" 18.63 to
  22.40 s; "Near the shore, the ocean floor comes up fast" 22.40 to
  25.21 s; "And so does the wave. At the shore, where the water is ten
  meters deep, it is four point four meters tall" 25.21 to 30.98 s
- timeline moved to the voice: with the hump starting 1,200 km before
  the slope the floor began rising at 8.42 s (after "the ocean floor
  rises", 6.85 to 8.79 s) and the crest reached 10 m at 29.42 s, inside
  the last words of the payoff sentence; x_start_km went from 1,500 to
  1,850 (the deep run 850 km, 4,292 s) so the floor rises from 5.96 s and
  the crest reaches the foot at 26.97 s, while "where the water is ten
  meters deep" is spoken (about 27 to 29 s) and before "four point four
  meters tall" (about 29.3 to 31 s); payoff_t set to 27.0 s (the card
  fades in as the crest reaches 10 m, during the payoff sentence); the
  shelf margin (x_end_km 3,800) and the control tank (8,000 km) were
  lengthened to match; the physics numbers do not change (same profile,
  same hump), only the video times: 1,000 m at 10.82 s, 100 m at
  18.89 s, 30 m at 23.11 s, 10 m at 26.97 s (from `media/tsunami/render.log`)
- footage: `sims/tsunami/tsunami.py` (no arguments) wrote
  `media/tsunami/footage.mp4`, 40.00 s at 60 fps, 2,400 frames, at
  10:37 EEST (measure 40 s, frames 70 s on 12 forked workers); the same
  run re-printed every measurement above (`media/tsunami/render.log`);
  text widths at most 855 px (the overlay), title lines 805 and 697 px,
  readouts at most 308 px, payoff lines 588 and 713 px (the first card
  text, "at the shore, 10 m deep: 4.4 m tall, 9.9 m/s", measured 979 px
  and was cut to "at the shore: 4.4 m tall, 9.9 m/s"), so nothing clips
  at 1080 px; the window is 270 km wide at the start (the hump 400 px
  wide at half height, 40 px tall) and 60 km at the end (88 px wide,
  175 px tall), the 20 km scale bar 80 px at the start and 358 px at the
  end, the ocean floor under the crest at y 1360 at the start and y 860
  at the end; smoke frames at 0, 1.5, 8.4, 13.3, 21.3, 26, 29.5, 32.5, 36
  and 39.7 s (`--frames`, 10:32 EEST, first geometry) inspected: the
  title over the deep wave with the floor a thin strip, the floor
  ramping up through the frame, the thin shelf under the tall spike, the
  card; fixes after them: the minimap window box shortened so it clears
  the "10 m" label on the shelf, the scrolling floor ticks brightened
- compose: `scripts/compose.sh tsunami` wrote `media/tsunami/final.mp4`
  at 10:38 EEST (h264 1080x1920 60 fps, aac 22050 Hz mono, 40.000 s;
  music seed 41 at gain 0.18; voice offset 0.6 s; captions at caption_y
  0.75); loudness mean -16.9 dB, peak -0.0 dB; preview and 8x5 contact
  sheet written (`media/tsunami/compose.log`)

### Local QA

- frames at 0.02, 1.5, 7.5, 13, 20, 27.3, 30, 35 and 39.95 s extracted
  from final.mp4 (`media/tsunami/frame-*.png`) and inspected with the
  contact sheet (10:40 EEST): the overlay at y 96 clear of the title; the
  question readable on the first frame over the deep wave, with the
  readouts 4,000 m, 198 m/s, 1.0 m and the minimap marker at the start of
  the run; "A one meter wave at" in the clear band at 1.5 s under the
  panel, the title still up; "Now the ocean floor" at 7.5 s with the
  floor already a visible ramp (2,576 m, 159 m/s, 1.1 m); "is in deeper
  water," at 13 s (537 m, 72.6 m/s, 1.7 m); "water, the slower" at 20 s
  (73 m, 26.7 m/s, 2.7 m) with the hump visibly narrower and taller and
  the scale bar longer; "At the shore, where" at 27.3 s with the card
  fading in, the readouts 10 m, 9.9 m/s, 4.4 m and the thin shelf under
  the spike; "four point four" at 30 s over the full card, the payoff
  number on screen as it is spoken and equal on the readout and the
  card; the card alone on the tall wave at 35 s; the last frame
  crossfading into the title frame at 39.95 s; the contact sheet shows
  the readouts falling and rising monotonically, the captions matching
  the narration chunks, no text at the frame edges, the caption band
  (y 1430..1530) clear of the panel (ends at y 1400) and the card (from
  y 1592); approved

### Metadata

- `projects/tsunami/metadata.json`: title 94 characters (the question,
  then 4.4 m tall by the time the water is 10 m deep; the producer's
  first title also carried "and 20 times slower", cut by the orchestrator
  so the title holds one setup and one payoff number); description with the
  setup, a "Measured:" list (every printed crest, speed and width against
  the closed forms, the travel times, the control, the wave sent back and
  the trough, the energy and volume conservation, the half-step checks),
  a "Why:" paragraph with Green's law and the 2 % shortfall, the rerun
  line and the AI-made line; 10 tags; category 27; private;
  containsSyntheticMedia true; selfDeclaredMadeForKids false

### Release

- orchestrator review (10:49 EEST): the task evidence, the 8x5
  contact sheet and the full-resolution frames at 0.02, 13, 30 and 39.95 s inspected: the question over the deep wave on the first frame with the minimap, the readouts and the 20 km bar; the floor ramping up and the hump growing at 13 s (537 m, 72.6 m/s, 1.7 m) under a caption that matches the narration; the tall narrow hump on the shelf at 30 s with the readouts 10 m, 9.9 m/s, 4.4 m, the card and the caption "four point four"; the crossfade to the title frame at 39.95 s; the contact sheet shows the readouts moving monotonically and every caption chunk in the clear band. One change by the orchestrator: the title's third number ("and 20 times slower") was cut so the title carries one setup number and one payoff number as docs/vision.md requires; it now reads "A one meter wave at sea. How tall at the shore? 4.4 m tall by the time the water is 10 m deep." (91 characters); the 20x figure stays in the description; approved for release
- quota check: clock 2026-09-19T10:49:11+03:00; zero upload attempts recorded
  since the 2026-09-19 10:00 EEST boundary (no 2026-09-19 upload entries
  in web/data/log.jsonl, no media/*/upload.log files exist)
- upload: BLOCKED. secrets/token.json and secrets/client_secret.json do
  not exist: the owner ran `git clean -fdx` in the repo at 2026-09-18
  21:07:58 EEST (fish history), which removed the untracked secrets/,
  media/ and .direnv/ directories; no copy of either file exists under
  the home directory, and re-authorization needs the client secret plus
  an interactive owner login (docs/channel-setup.md, section 3). No
  videos.insert call was made; this is not a quota attempt.
- slot resolution: slipped for the 2026-09-19 quota day with the reason
  above; the manual upload packet is ready (docs/channel-setup.md,
  section 5): `media/tsunami/final.mp4` (h264 1080x1920 60 fps, aac,
  40.000 s) and `projects/tsunami/metadata.json` (title, description,
  tags, category 27, private, altered-content disclosure). Once
  secrets/ is restored, `scripts/yt-upload.py tsunami` and then
  `scripts/yt-qa.py tsunami VIDEO_ID --wait --publish` release it, each
  recorded as a quota attempt on that day. The task stays OPEN until the
  upload and publication evidence are recorded.

### Published

- credentials restored: the owner refreshed secrets/client_secret.json
  and secrets/token.json at 2026-09-19 11:00 EEST; a channels.list read
  at 11:02 EEST verified the token sees only the Seed Zero channel
  (60 videos, uploads playlist 60, newest cradle qE-8l1rEPRY of
  2026-09-18); the media/ tree had been rebuilt by the producing run
  at 10:27 to 10:44 EEST (deterministic renders)
- pre-upload check (11:02 EEST): final.mp4 h264 1080x1920 60 fps, aac
  22050 Hz mono, 40.000 s, moov before mdat; md5
  6a0f420aaf65b8c6fcfdb74b47c1d875; title 94 characters (the Release
  note above says 91; 94 is the count of the file as uploaded); the 8x5
  contact sheet re-inspected by the releasing session: question over the
  deep wave, floor rising, hump narrowing and growing, card with
  4.4 m tall, 9.9 m/s, crossfade to the title; approved
- quota check before the insert: clock 2026-09-19T11:04:05+03:00; zero upload attempts
  recorded since the 2026-09-19 10:00 EEST boundary (log entries and
  media/*/upload.log both checked); this is insert attempt 1 of the
  hard cap of 5
- attempt 1 recorded at 2026-09-19T11:04:05+03:00, video name tsunami, before running
  `scripts/yt-upload.py tsunami`

- upload: `scripts/yt-upload.py tsunami` ran 11:04:05 to 11:04:10 EEST,
  token verified to see only the Seed Zero channel, video id
  DlmRoaSp85g, private (`media/tsunami/upload.log`)

- gate: `scripts/yt-qa.py tsunami DlmRoaSp85g --wait --publish` ran in
  the foreground at 11:05:12 EEST after one pre-gate read showed
  processing succeeded and 10 tags present (one minute after the
  insert, no tag lag this time): 15 of 15 pass (processed, succeeded,
  hd, 1080x1920, title, description, tags as a set, category 27, not
  for kids, PT41S for the 40.000 s file, private); containsSyntheticMedia
  reads absent as on every earlier upload (`media/tsunami/publish.log`)
- publish: the same run set the video public at 2026-09-19T11:05:14+03:00;
  the re-read after 15 s shows privacyStatus public, madeForKids false,
  embeddable true; public at https://youtu.be/DlmRoaSp85g

### Quota

- attempt 1 of the hard cap of 5 for the quota day that began
  2026-09-19T10:00 EEST; cost 1 + 1,600 + 1 + 1 + 50 + 1 = 1,654 units
  (the channels.list verification inside yt-upload.py, the insert, the
  pre-gate read, the gate read, the update, the re-read); the
  releasing session's 11:02 token check (channels.list and
  playlistItems.list) cost 2 more units, charged to the day, not to
  this attempt

- slot resolution: published for the 2026-09-19 quota day; this
  supersedes the slipped resolution recorded under Release above

### Repository

- committed as 079736e "Produce the day twenty-one slate as manual upload
  packets" (sims, projects, tasks, docs/niche.md, web/data; no media,
  previews or secrets) and pushed to origin/master at 10:50 EEST
- committed as 1762ebc "Publish the day twenty-one slate" (tasks,
  docs/niche.md, web/data; no media, previews or secrets) and pushed
  to origin/master at 2026-09-19 11:08 EEST
