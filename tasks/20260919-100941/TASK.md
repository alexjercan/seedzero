# Produce short: Parking lot probing, roll forward versus random retry

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day21

## Goal

Backlog idea (trend research 2026-09-09, task 20260909-083310, pillar
idea for hash collisions):
"Parking-lot probing: 1,000 spaces, 950 cars with the same preferred
spots; roll forward to the next free spot versus a fresh random spot on
each retry; measure the spots passed by the last fifty cars and the
longest run of taken spots; expect about fifty against ten at ninety
percent full and two hundred against twenty at ninety five."
Day twenty-one, third slot. Chosen because the everyday-queue pieces
with a plain question are among the channel's best (elevator paradox
918 views, plane boarding 771) and it is a two-panel same-input
comparison (the same cars, the same preferred spots, two rules) with
one setup number (950 cars into 1,000 spaces) and one payoff number per
rule that the linear-probing closed form checks.
Question in the first two seconds: "950 cars, 1,000 spaces. How many
spots does the last car drive past?"

## Claim

When every car rolls forward from its preferred spot, the taken spots
clump into long runs and the last cars drive past hundreds of spots;
when a blocked car tries a fresh random spot instead, the last cars pass
about twenty. Every number in the narration is printed by the sim
before the script is written.

## Evidence

### Measurements

(recorded after the measure-only run, before scripting)

`sims/parking/parking.py --measure-only` with `projects/parking/manifest.json`
(one row of 1,000 spaces drawn as 50 columns by 20 rows, space 999 wrapping
to space 0; 950 cars arrive one at a time; car i wants one preferred spot
drawn uniformly from numpy default_rng, SeedSequence(0) spawned into a
preferred-spot stream and a retry stream, and the same preferred spots
feed both lots; top lot, roll forward: a blocked car drives forward one
space at a time to the next free spot (linear probing); bottom lot, fresh
random spot: a blocked car draws a new random spot from the retry stream
and tries there until it finds a free one (random probing; a retry may hit
the same taken spot twice); spots passed = taken spots driven past or
tried before parking = probes minus one; seed 0; log in
`media/parking/measure.log`, run at 10:26 EEST, 1 s):

- closed forms: linear probing expects (1 + 1/(1 - a)^2) / 2 probes at
  load a: 50.5 at 0.90 and 200.5 at 0.95 (49.5 and 199.5 spots passed);
  random probing expects 1 / (1 - a) tries: 10.0 at 0.90 and 20.0 at 0.95
  (9.0 and 19.0 spots passed); car 950 arrives at load 0.949: 191.7 and
  18.6 spots passed expected; averaged over cars 901 to 950 (loads 0.900
  to 0.949): 98.0 and 12.8 spots passed
- blocks of fifty cars, spots passed (roll forward avg / closed form /
  max; fresh random spot avg / closed form / max): cars 1-50 0.0/0.0/0,
  0.0/0.0/0; 51-100 0.0/0.1/1, 0.0/0.1/1; 101-150 0.1/0.2/1, 0.1/0.1/1;
  151-200 0.2/0.2/3, 0.2/0.2/2; 201-250 0.4/0.3/3, 0.4/0.3/3; 251-300
  0.5/0.5/3, 0.4/0.4/2; 301-350 0.7/0.6/6, 0.6/0.5/4; 351-400 0.9/0.8/5,
  0.6/0.6/4; 401-450 1.4/1.0/7, 1.0/0.7/8; 451-500 1.2/1.3/9, 0.9/0.9/6;
  501-550 1.4/1.7/8, 1.3/1.1/11; 551-600 2.6/2.3/21, 1.3/1.4/8; 601-650
  4.4/3.1/30, 1.8/1.7/8; 651-700 5.4/4.2/30, 2.4/2.1/11; 701-750
  7.1/6.1/27, 2.4/2.6/8; 751-800 6.8/9.5/57, 3.8/3.5/18; 801-850
  19.9/16.1/114, 4.3/4.7/23; 851-900 37.1/32.6/201, 7.4/7.1/29; 901-950
  80.9/98.0/360, 12.4/12.8/122
- cars 901 to 950 (the lot 90 to 95 percent full): roll forward avg 80.9
  spots passed (closed form 98.0), max 360 (car 943), median 41; fresh
  random spot avg 12.4 (closed form 12.8), max 122 (car 950), median 6;
  ratio of the averages 6.5; rounded for the card and the narration: 81
  and 12 spots per car; the running average over the last 50 parked cars
  at 900 cars: 37.1 and 7.4
- all 950 cars: roll forward avg 9.00 spots passed, total 8,551, 503 cars
  parked at their preferred spot, first car past 100 spots: car 839;
  fresh random spot avg 2.17, total 2,063, 493 cars at their preferred
  spot, max over all cars 122 (car 950)
- longest run of consecutive taken spots: at 900 cars roll forward 265,
  fresh random spot 39; at 950 cars roll forward 515, fresh random spot
  72; roll forward first run over 100 after car 824, over 200 after car
  846
- last car (car 950, preferred spot 609, load 0.949): roll forward drove
  past 2 spots, from spot 609 to spot 611; fresh random spot tried 122
  taken spots and parked at spot 682 (a 0.95^122 = 0.2 percent draw at
  that load); the fifty cars before it: roll forward 30, 133, 16, 9, 51,
  2, 117, 0, 21, 184, 210, 111, 0, 0, 0, 24, 28, 19, 108, 38, 1, 154, 84,
  3, 54, 319, 284, 77, 5, 246, 4, 4, 337, 3, 10, 77, 0, 231, 123, 37, 56,
  108, 360, 10, 0, 44, 72, 50, 190, 2; fresh random spot 2, 12, 0, 39,
  14, 1, 24, 0, 0, 3, 5, 26, 17, 1, 1, 8, 3, 1, 2, 13, 2, 1, 1, 4, 6, 34,
  20, 5, 5, 0, 10, 13, 30, 6, 6, 14, 0, 11, 28, 12, 5, 9, 28, 3, 9, 20,
  17, 21, 4, 122
- check, seeds 1 to 5 (roll forward / fresh random spot): seed 1: cars
  901-950 avg 57.7 / 13.9, max 329 / 81, last car 203 / 5, longest run at
  900 cars 209 / 51 and at 950 cars 495 / 102; seed 2: avg 31.9 / 10.3,
  max 144 / 55, last car 40 / 27, longest run 147 / 37 and 177 / 55; seed
  3: avg 49.0 / 16.1, max 196 / 57, last car 37 / 20, longest run 145 /
  52 and 298 / 88; seed 4: avg 56.3 / 7.9, max 361 / 72, last car 14 / 3,
  longest run 202 / 48 and 392 / 134; seed 5: avg 42.1 / 12.7, max 266 /
  109, last car 48 / 6, longest run 206 / 44 and 437 / 91
- check, 100,000-space lot, 96,000 cars, seed 0: cars at load 0.895 to
  0.905 (1,000 cars): roll forward avg 48.3 (closed form 49.6, at 0.90
  exactly 49.5), fresh random spot avg 9.23 (closed form 9.01, at 0.90
  exactly 9.0); cars at load 0.945 to 0.955 (1,000 cars): roll forward
  avg 222.1 (closed form 201.5, at 0.95 exactly 199.5), fresh random spot
  avg 19.35 (closed form 19.07, at 0.95 exactly 19.0); cars 90,001 to
  95,000 (load 0.90 to 0.95) avg 99.2 / 13.07 (closed forms 99.5 /
  12.86); longest run at 90 percent 984 / 94 and at 95 percent 2,579 /
  148

Decisions: the brief offered the last car's own count or the average over
the last fifty cars as the payoff. At seed 0 the last car is an unlucky
draw in the wrong direction (roll forward past 2 spots, fresh random spot
122 tries, a 1-in-500 event at that load), so it is not a clean single
number; the average over cars 901 to 950 is (80.9 against 12.4, closed
forms 98.0 and 12.8, a 6.5 ratio; seeds 1 to 5 give 31.9-57.7 against
7.9-16.1, all in the same direction). Payoff = the block average, shown
rounded (81 and 12 spots per car) on the card and as the live "last 50
cars: avg N spots" readout, which equals the block average once car 950
has parked. The question therefore asks about "the last cars", not "the
last car". The single-car readout "this car passed N spots" stays on
screen (it is what the frame shows); the unlucky last car goes to the
description.

Narration numbers: nine hundred fifty cars into one thousand spaces
(setup), eighty one spots per car and twelve spots per car (payoff, the
80.9 and 12.4 block averages rounded, matching the card and the readouts).
The closed forms, the block table, the longest runs, the last car, the
other seeds and the big lot go to the description.

### Production

- narration (written after the measure-only run): three hooks tried,
  "Nine hundred fifty cars into one thousand spaces. How far do the last
  cars go?" (kept: it names the setup and asks the title question in the
  title's words), "One thousand spaces, nine hundred fifty cars. How far
  do the last cars go?" and "A lot with one thousand spaces takes nine
  hundred fifty cars. How far does a late car drive?" (dropped: the
  single-car reading is the one the seed-0 last car contradicts, and a
  "drive" title line is 970-1008 px at 56 px, over the 950 px limit);
  `projects/parking/narration.txt`, 108 words; the setup number is nine
  hundred fifty cars into one thousand spaces, the payoff about eighty
  one spots per car (roll forward) and about twelve spots per car (fresh
  random spot), "about" because the card and the readouts show the 80.9
  and 12.4 block averages rounded; the closed forms, the longest runs,
  the last car, the other seeds and the big lot stay in the description
- voice: `scripts/voiceover.sh projects/parking/narration.txt` passed on
  every run with no misheard word; run 1 at 10:28:03 EEST, 110 words,
  35.19 s (ends at 35.79 s, at the 36 s bound); "full" and a leading "So"
  cut, run 2 at 10:28:25, 108 words, 34.52 s; the payoff sentences then
  reworded because captions.py (20 characters a chunk) split the number
  as "Roll forward: eighty" / "one spots per car." ("about" added, "long"
  cut, "drive past" to "pass"); run 3 at 10:32:53, 108 words, 34.81 s,
  ends at 35.41 s of the 40 s video, 3.1 words/s; chunks now "Roll
  forward: about" / "eighty one spots per" / "car." and "Fresh random
  spot:" / "about twelve spots" / "per car."; log in
  `media/parking/voice.log`
- timing (`scripts/voice-timing.py`, +0.6 s offset): "950 cars into 1000
  spaces, how far do the last cars go?" 0.60 to 5.22 s over the title (to
  2.4 s) with the first car at 0.4 s; "Each car wants one random spot"
  5.22 to 7.24 s; "On top, a blocked car rolls forward to the next free
  spot" 7.24 to about 11 s (cars 600 to 750, trails of 4 to 7 spots);
  "Below, it tries a fresh random spot" about 11 to 13.5 s; "On top,
  taken spots clump into runs" about 13.5 to 16.13 s with 830 to 880 cars
  parked and the first run over 200 forming after car 846 (about 14.5 s);
  "A car that lands in a run drives to its end, the runs grow and late
  cars pass more and more spots" 16.13 to 22.61 s across the end of the
  fast phase (16.99 s) and the first slow cars; "Below, the taken spots
  stay evenly dotted" 22.61 to 24.82 s; "so most fresh tries find a gap
  fast" 24.82 to about 27.2 s; "So how far do the last cars go?" about
  27.2 to 29.6 s, the last car parked at 26.92 s and the card fading in
  from 27.4 s (payoff_t set from this timing, after the event);
  "Roll forward, about 81 spots per car" about 29.6 to 32 s (the number
  from 30.19 s) and "Fresh random spot, about 12 spots per car" about 32
  to 35.41 s (the number from 33.57 s), both over the card
- footage: `sims/parking/parking.py` (no arguments) wrote
  `media/parking/footage.mp4`, 40.00 s at 60 fps, 2,400 frames, in 48 s
  with eight forked workers, at 10:34 EEST; the same run re-printed every
  measurement above (`media/parking/render.log`); schedule printed by the
  sim: car 1 at 0.4 s, cars 1 to 900 park by 16.99 s (slots 8.0 to 39.3
  ms, 54 cars per second on average), cars 901 to 950 take 64 to 641 ms
  each (4 to 38 frames, in proportion to 40 plus the longer of their two
  paths), the longest drive (car 943, 360 spots) from 25.11 s at 13.4
  spots per frame, car 950 from 26.74 s parking at 26.92 s, trails fade
  over 0.3 s, card at 27.4 s, title until 2.4 s; text widths at most 896
  px (the overlay; title 743 and 887 px, labels 266 and 416, sublabels
  615 and 524, readouts 521 at 36 px and 557, 404, 311 at 28 px, payoff
  lines 662 and 813 px), so nothing clips at 1080 px; smoke frames at 0,
  1, 2, 8, 15, 18, 20, 24, 27, 28.2, 28.4, 30 and 39.8 s (`--frames`,
  10:26 EEST) inspected for the layout: the title clear of the overlay
  band, the two 50 x 20 grids at a 20 px pitch (x 40 to 1040, y 430 to
  830 and 990 to 1390), the trails as pale streaks, the card below the
  caption band
- decisions in the schedule: the brief's 20 s fast phase became 16.6 s
  so the last car parks (26.92 s) before the payoff sentence (about 27.2
  s) with the 108-word narration ending at 35.41 s; the last car gets no
  special slow hold because its own drive (2 against 122 spots) is the
  unlucky draw, so the slow phase shares 10 s across cars 901 to 950 in
  proportion to their longer path, which gives the 360-spot drive of car
  943 the most screen time (0.64 s)
- compose: `scripts/compose.sh parking` wrote `media/parking/final.mp4`
  at 10:34 EEST (h264 1080x1920 60 fps, aac 22050 Hz mono, 40.000 s;
  music seed 42 at gain 0.18; captions at caption_y 0.75, 34 drawtext
  filters); loudness mean -16.6 dB, peak -0.0 dB; preview and 8x5
  contact sheet written (`media/parking/compose.log`); an earlier
  compose at 10:30 EEST (before the wording and plural fixes) measured
  -16.5 dB and was replaced

### Local QA

- first pass (10:30 EEST, the earlier render): frames at 0.02, 1.5, 10,
  15.5, 20, 24.5, 28.3, 30.7, 33.6, 35 and 39.95 s and the contact sheet
  inspected; two defects found: the readout printed "this car passed 1
  spots", and the captions split the payoff number as "Roll forward:
  eighty" / "one spots per car."; the sim's plural was fixed, the payoff
  sentences reworded, the voice re-recorded and re-timed, the schedule
  moved (t_last_park 27.6 to 27.0 s, payoff_t 28.0 to 27.4 s), and the
  footage and final re-rendered
- second pass (10:34 EEST): frames at 0.02, 1.5, 10, 15.5, 20, 24.5,
  27.6, 30.7, 34, 35 and 39.95 s extracted from final.mp4
  (`media/parking/frame-*.png`) and inspected with the contact sheet:
  0.02 s shows the overlay at y 96, the title "950 cars, 1,000 spaces. /
  How far do the last cars go?" at y 190/252 clear of it, both lots empty
  with every readout at 0 (the thumbnail); 1.5 s shows 134 cars parked
  under "Nine hundred fifty" with the title still up; 10 s shows 684
  cars, "the next free spot." and "this car passed 1 spot"; 15.5 s shows
  861 cars under "clump into runs." with "longest full run 207" in gold
  and the runs visible as filled row segments; 20 s shows 919 cars, "The
  runs grow, and", a pale 46-spot trail across the top rows and "longest
  full run 384"; 24.5 s shows 938 cars under "spots stay evenly" with a
  108-spot drive on top and the bottom lot evenly dotted; 27.6 s shows
  all 950 parked, "gap fast." and the card fading in; 30.7 s shows "Roll
  forward: about" over the fully lit card "roll forward: 81 spots per car
  / fresh random spot: 12 spots per car" with the readouts "last 50 cars:
  avg 81 spots" and "avg 12 spots", "longest full run 515" and "72", and
  the last car's own "this car passed 2 spots" and "122 spots"; 34 s
  shows "about twelve spots" over the card; 35 s "per car."; 39.95 s the
  crossfade to the title frame; captions match the narration word for
  word and sit in the y 1440 to 1520 band with the grids ending at 1390
  and the card from 1592; no text clips at the frame edges; the payoff
  numbers are on screen when spoken (30.19 and 33.57 s); approved

### Metadata

- `projects/parking/metadata.json`: title "950 cars, 1,000 spaces. How
  far do the last cars go? Roll forward 81 spots per car, random retry
  12." (100 characters); description with the setup, the seed and the
  two streams, a Measured list (the block average and closed forms, the
  block table from car 551, the longest runs, the totals, the unlucky
  last car and why the payoff is the block average, seeds 1 to 5, the
  100,000-space lot), a Why paragraph (runs grow at their ends and
  merge, a longer run catches more preferred spots; a fresh random spot
  has no memory, so the tries are geometric with mean 1 / (1 - a)), the
  rerun line and the AI-made line; 10 tags (parking lot, hash table,
  hash collisions, linear probing, probability, algorithms, simulation,
  computer science, math visualization, shorts); category 27; private;
  containsSyntheticMedia true; selfDeclaredMadeForKids false
- not uploaded; task left open for the orchestrator's review and upload

### Release

- orchestrator review (10:49 EEST): the task evidence, the 8x5
  contact sheet and the full-resolution frames at 0.02, 20, 30.7 and 39.95 s inspected: the question over the two empty grids on the first frame; the runs as filled row segments with a pale trail and "longest full run 384" under "The runs grow, and" at 20 s; the card "roll forward: 81 spots per car / fresh random spot: 12 spots per car" with the readouts "last 50 cars: avg 81 spots" and "avg 12 spots" and the caption "Roll forward: about" at 30.7 s; the crossfade at 39.95 s; the contact sheet shows the top lot clumping and the bottom lot evenly dotted, every caption in the clear band; approved for release
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
  section 5): `media/parking/final.mp4` (h264 1080x1920 60 fps, aac,
  40.000 s) and `projects/parking/metadata.json` (title, description,
  tags, category 27, private, altered-content disclosure). Once
  secrets/ is restored, `scripts/yt-upload.py parking` and then
  `scripts/yt-qa.py parking VIDEO_ID --wait --publish` release it, each
  recorded as a quota attempt on that day. The task stays OPEN until the
  upload and publication evidence are recorded.

### Published

- credentials restored: the owner refreshed secrets/client_secret.json
  and secrets/token.json at 2026-09-19 11:00 EEST; a channels.list read
  at 11:02 EEST verified the token sees only the Seed Zero channel
  (60 videos, newest cradle qE-8l1rEPRY of 2026-09-18); the media/ tree
  had been rebuilt by the producing run at 10:27 to 10:44 EEST
- pre-upload check (11:02 EEST): final.mp4 h264 1080x1920 60 fps, aac
  22050 Hz mono, 40.000 s, moov before mdat; md5
  39b5df3e4c199cbaec0ae24afa03fea3; title 100 characters (the limit);
  the 8x5 contact sheet re-inspected by the releasing session: question
  over the two near-empty lots, both lots filling, the top lot clumping
  into runs from about 80 percent full while the bottom stays dotted,
  the readouts climbing to 81 and 12 spots, the card, the crossfade to
  the title; approved
- quota check before the insert: clock 2026-09-19T11:04:44+03:00; two upload attempts
  (tsunami, 11:04:05, private DlmRoaSp85g; slits, 11:04:26, private
  e78W6KshdFg; both gates pending) recorded since the 2026-09-19 10:00
  EEST boundary (log entries and media/*/upload.log both checked); this
  is insert attempt 3 of the hard cap of 5
- attempt 3 recorded at 2026-09-19T11:04:44+03:00, video name parking, before running
  `scripts/yt-upload.py parking`

- upload: `scripts/yt-upload.py parking` ran 11:04:44 to 11:04:50 EEST,
  token verified to see only the Seed Zero channel, video id
  bt2G-PQK13k, private (`media/parking/upload.log`)

- gate: `scripts/yt-qa.py parking bt2G-PQK13k --wait --publish` ran in
  the foreground at 11:06:12 EEST after one pre-gate read showed
  processing succeeded and 10 tags present: 15 of 15 pass (processed,
  succeeded, hd, 1080x1920, title, description, tags as a set, category
  27, not for kids, PT41S for the 40.000 s file, private);
  containsSyntheticMedia reads absent as on every earlier upload
  (`media/parking/publish.log`)
- publish: the same run set the video public at 2026-09-19T11:06:15+03:00;
  the re-read after 15 s shows privacyStatus public, madeForKids false,
  embeddable true; public at https://youtu.be/bt2G-PQK13k
- slot resolution: published for the 2026-09-19 quota day; this
  supersedes the slipped resolution recorded under Release above

### Quota

- attempt 3 of the hard cap of 5 for the quota day that began
  2026-09-19T10:00 EEST; cost 1 + 1,600 + 1 + 1 + 50 + 1 = 1,654 units
  (the channels.list verification inside yt-upload.py, the insert, the
  pre-gate read, the gate read, the update, the re-read); day total
  after three attempts 4,962 units

### Repository

- committed as 079736e "Produce the day twenty-one slate as manual upload
  packets" (sims, projects, tasks, docs/niche.md, web/data; no media,
  previews or secrets) and pushed to origin/master at 10:50 EEST
- committed as 1762ebc "Publish the day twenty-one slate" (tasks,
  docs/niche.md, web/data; no media, previews or secrets) and pushed
  to origin/master at 2026-09-19 11:08 EEST
