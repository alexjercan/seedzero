# Produce short: Double slit ripple tank, one slit versus two

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day21

## Goal

Backlog idea (trend research 2026-09-16, task 20260916-100924):
"Double slit ripple tank: a 2 cm wave through one slit beside two slits
10 cm apart; measure the bright band angles on a screen 60 cm away;
expect bands at 11.5, 23.6 and 36.9 degrees (d sin theta = n lambda)
with dark bands between them and no bands from the single slit; 2D
finite-difference wave solver, steady state so the short loops;
deterministic, no seed (peg: Schrodinger centenary 2026, Nobel physics
2026-10-06)."
Day twenty-one, second slot. Chosen because it is continuous motion, a
two-panel same-input comparison (the same wave through one slit against
two), a classic with a plain question, one setup number (two slits ten
centimeters apart) and one payoff number that a closed form checks.
Question in the first two seconds: "Open a second slit. Does more wave
get through everywhere?"

## Claim

The same two centimeter ripples through one slit spread into one smooth
fan; through two slits ten centimeters apart they split into bright
bands with dark water between them, the first dark band a few degrees
off centre, exactly where d sin theta = lambda / 2 says. Every number in
the narration is printed by the sim before the script is written.

## Evidence

### Measurements

(recorded after the measure-only run, before scripting)

`sims/slits/slits.py --measure-only` with `projects/slits/manifest.json`
(a ripple tank 80 x 58 cm seen from above; the 2D wave equation
u_tt + 2 sigma u_t = c^2 (u_xx + u_yy) at c = 0.2 m/s and 10 Hz, so the
wavelength is 2.0 cm; grid 1 mm, 800 x 580 cells, 20 per wavelength;
fourth-order Laplacian, second order with mirrored values in the five
rows around the wall; leapfrog at dt = 1.6667 ms, Courant 0.3333, 60
steps per period, 2 steps per video frame; a quadratic sponge 4 cm wide
on all four edges at rate 80/s; a soft plane-wave source on the row at
y = 4 cm ramped over two periods from 0.3 s of the video, source
amplitude 0.0671 so the incident wave has amplitude about 1; a hard
Neumann wall 1 mm thick at y = 14 cm with an absorbing beach 3 cm deep on
its face at rate 100/s except in the slit columns; top panel one slit
1 cm wide at the centre, bottom panel two slits 1 cm wide 10 cm apart;
a screen line 40 cm past the wall spanning +-36 cm, +-42.0 degrees;
time-lapse at 5x slow motion, 8 s of wave in the 40 s scene;
deterministic, no seed; log in `media/slits/measure.log`, run at 10:35
EEST, 69 s):

- closed forms: bright where d sin theta = n lambda: 11.54, 23.58, 36.87
  degrees (8.16, 17.46, 30.00 cm along the 40 cm screen); dark where
  d sin theta = (n + 1/2) lambda: 5.74, 17.46, 30.00, 44.43 degrees (4.02,
  12.58, 23.09, 39.21 cm); on a screen spanning +-42.0 degrees that is 7
  bright bands (the centre plus 3 each side) and 6 dark bands between
  them; one slit 1 cm wide needs sin theta = lambda / a = 2 for a dark
  direction, over one, so no dark band anywhere: one smooth fan; the wave
  crosses the 10 cm from the source to the wall in 2.5 s of video and the
  40 cm from the wall to the screen centre in 10.0 s more
- incident wave: amplitude 0.9911 (one slit) / 0.9944 (two slits)
  measured 5 to 10 cm up the tank over the last period; envelope minimum
  0.9715 / 0.9671, standing-wave ratio 1.020 / 1.028, so the beach sends
  back 1.0% / 1.4% of the amplitude (the incoming ripples travel, they
  do not stand); the wave reaches the wall at 2.05 s of the video, the
  screen centre at 13.38 / 13.23 s and the screen end 35 cm off axis at
  16.70 / 15.90 s
- two slits, screen at 40 cm, intensity u^2 averaged over the last 10
  periods at 40 s: 7 bright bands at 0.00, +-8.17, +-17.50, +-29.85 cm
  (0.00, +-11.55, +-23.63, +-36.73 degrees); 6 dark bands at +-4.05,
  +-12.67, +-23.21 cm (+-5.79, +-17.57, +-30.12 degrees); dark over
  bright 0.0155, 0.0137, 0.0103 (largest 0.0155, so the dark bands hold
  under 2% of the intensity of their neighbours); band heights as a
  fraction of the centre 1.000, 0.952, 0.815, 0.611; against the closed
  forms the bright bands are within 0.14 degrees (11.55 vs 11.54, 23.63
  vs 23.58, 36.73 vs 36.87; the outer band is pulled inward by the
  falling single-slit envelope) and the dark bands within 0.12 degrees
  (5.79 vs 5.74, 17.57 vs 17.46, 30.12 vs 30.00); the first dark band
  5.79 degrees off centre, 4.05 cm along the screen; the profile is
  symmetric to the printed precision
- one slit, same average: 1 bright band with a flat top within 1% of the
  peak from -3.5 to +3.5 cm (-5.1 to +5.1 degrees); 0 dark bands; the
  profile falls from the peak to the screen ends with local rises of at
  most 0.139% of the peak per mm; the largest pruned ripple 0.55% of the
  peak (the band threshold is 4%); intensity as a fraction of the peak
  at 0, 10, 20, 30, 35 cm: 0.994, 0.922, 0.760, 0.593, 0.528, the same
  on both sides
- totals along the screen: two slits let through 1.990 times the summed
  intensity of one slit, and the centre of the screen is 3.804 times as
  bright (two waves in step: amplitude twice, intensity four times);
  transmitted amplitude at the screen centre 0.0885 (two slits) and
  0.0454 (one slit) against the incident 0.9944
- live counts from the 4-period running average (the strip on screen):
  one slit 0, 0 until 13.67 s then 1 bright, 0 dark to the end; two
  slits 3, 2 at 13.48 s, 5, 4 at 14.40 s, 7, 6 from 16.18 s to the end
- steadiness: at 30 s and at 35 s the 10-period average gives the same
  7 bright and 6 dark bands with angles within 0.01 degrees of the 40 s
  values; a 20-period window gives the same angles to 0.00 degrees and
  the same largest dark over bright 0.0155
- check at half the grid step (0.5 mm, dt 0.8333 ms, 1600 x 1160 cells,
  run to 26 s of the video): 7 bright at 0.00, +-8.16, +-17.47, +-29.83
  cm (+-11.54, +-23.59, +-36.71 degrees) and 6 dark at +-4.05, +-12.66,
  +-23.19 cm (+-5.78, +-17.56, +-30.10 degrees): within 0.04 (bright)
  and 0.02 (dark) degrees of the full-step run; dark over bright largest
  0.0171
- check on a screen 20 cm from the wall (a wider view, +-61 degrees): 9
  bright bands (0.00, +-11.83, +-23.99, +-37.11, +-52.63 degrees) and 8
  dark (+-5.93, +-17.94, +-30.58, +-44.85); the bands of orders 1 to 3
  sit at 0.507 to 0.513 of their 40 cm positions (a straight line from
  the wall centre gives 0.500); one slit: 1 bright band, 0 dark, ripple
  0.13% of the peak
- check on a screen 30 cm from the wall (+-50 degrees): 9 bright (0.00,
  +-11.64, +-23.66, +-36.82, +-49.73 degrees) and 8 dark (+-5.83,
  +-17.67, +-30.24, +-44.60); orders 1 to 3 at 0.751 to 0.756 of their
  40 cm positions (closed form 0.750); one slit: 1 bright band, 0 dark,
  ripple 0.00%

Decisions: the brief's two 1080 x 700 px panels at 8 px/cm do not fit
the layout rules (the caption band at y 1430..1530 must be clear, the
payoff card below 1560, the title above the panels), which leave about
526 px of tank per panel; keeping the screen at 60 cm and the tank 130
cm wide would give 6.4 px/cm, a 13 px wavelength. The band angles depend
only on lambda / d, so the wavelength (2 cm), the slit separation (10
cm), the slit width (1 cm) and the 1 mm grid stay as briefed, the screen
moves to 40 cm past the wall and the tank is 80 x 58 cm with the screen
spanning +-42 degrees (7 bright and 6 dark bands land cleanly inside;
the 44.4 degree dark band and the 53 degree bright band stay out of
view, so the counts do not depend on the sponge edge); that gives 9
px/cm, an 18 px wavelength, and the wave reaches the screen at 13.2 s at
the briefed 1/5 real speed (at 60 cm it would take 18 s). The check
screens are at 20 and 30 cm instead of 30 cm. The source is soft
(additive) rather than forced, so the wave the wall sends back passes
through it into the sponge, and the wall face is an absorbing beach
except in the slit columns; with a bare hard wall the incoming ripples
stood in front of it (a pure standing wave, the crests pulsing in place)
and the narration line "the ripples roll up to the wall" would not have
matched the frame. The first run used the plain 5-point stencil; its
half-grid check moved the angles by up to 0.17 degrees (numerical
dispersion biased the full-step angles outward by 0.1 to 0.2 degrees),
so the Laplacian went to fourth order away from the wall and the check
now agrees to 0.04 degrees.

Narration numbers: ten centimeters apart (setup, the two slits), seven
bright bands (payoff, the count on the screen strip; the card and the
readouts show the same 7 and the 6 dark bands). The angles, the 1.5%
dark over bright, the 1.99 times summed intensity, the 3.8 times
centre, the half-step, longer-window, steadiness and check-screen
results go to the description.

### Production

- narration (written after the measure-only run): three hooks tried,
  "One slit makes a fan. What do two slits make?" (kept: it is the
  title's words, the top panel shows the fan while the question is
  asked, and the payoff answers it in the same words), "Open a second
  slit. Does more wave get through?" (the honest answer is "twice as
  much in total, but in bands", two claims) and "Open a second slit. Do
  the ripples add up?" (abstract for the first two seconds);
  `projects/slits/narration.txt`, 108 words; the setup number is ten
  centimeters apart, the payoff seven bright bands; "dark water between
  them" carries no number in the narration (the card says "dark
  between", the readout shows the 6)
- voice: `scripts/voiceover.sh projects/slits/narration.txt` passed on
  the first run at 10:37 EEST (108 words, 32.76 s, ends at 33.36 s of
  the 40 s video, 3.3 words/s); no word was misheard in the round trip
  (`media/slits/voice.log`); timing (`scripts/voice-timing.py` plus a
  0.10 s pause scan, +0.6 s offset): "One slit makes a fan. What do two
  slits make?" 0.60 to 3.54 s over the title (to 2.4 s) with the first
  crests already rolling at 1.5 s; "The same ripples roll up to a wall"
  3.54 to 5.67 s as the wave reaches the wall (2.05 s) and keeps
  arriving; "On top, the wall has one slit. Below, it has two slits, ten
  centimeters apart" 5.67 to 10.74 s while the fans grow past the wall;
  "Past the wall, the top ripples spread into one smooth fan. Below, two
  fans overlap" 10.74 to about 15.7 s as the fans reach the screen (13.2
  s) and the strips light up; "Where a crest meets a crest, the water
  swings high. Where a crest meets a trough, the water stays flat" about
  15.7 to 21.7 s over the settled lanes (counts final at 16.18 s); "The
  gold strip at the top adds up the motion over time and counts the
  bright bands" 21.7 to 25.8 s; "So what do two slits make?" 25.8 to
  27.6 s; "One slit makes one smooth fan" 27.6 to 29.7 s with the payoff
  card fading in from 27.6 s (payoff_t set from the timing); "Two slits
  make seven bright bands, with dark water between them" 29.7 to 33.36 s
  over the card, "seven" spoken at about 30.3 s
- footage: `sims/slits/slits.py` (no arguments) wrote
  `media/slits/footage.mp4`, 40.00 s at 60 fps, 2,400 frames, at 10:43
  EEST (2 min: the measure pool, then both tanks stepped frame by frame
  in the render loop, 1.8 ms per step); the same run re-printed every
  measurement above and its live counts matched the measure run on all
  2,399 frames (`media/slits/render.log`); text widths at most 892 px
  (payoff line 2), overlay 798, title lines 666 and 774, label "two
  slits, 10 cm apart" 442 at 36 px, readouts 489 at 28 px, angle label
  160, payoff line 1 549, so nothing clips at 1080 px and the label and
  the readouts leave a 69 px gap; smoke frames at 0, 1.5, 3, 8, 14, 17,
  24, 28, 33 and 39.7 s (`--frames`, 10:39 EEST) inspected before the
  render: flat water under the title, the first crests at 1.5 s, the
  wave at the wall at 3 s, the fans and the strips building, 7 humps
  and the "dark at 5.8°" label from 16.2 s, the crossfade; the smoke set
  showed the readouts (32 px, 570 px wide) running into the two-slit
  label and payoff line 2 at 1036 px ("dark water between"), so the
  readouts went to 28 px and the card line to "dark between" (892 px)
- compose: `scripts/compose.sh slits` wrote `media/slits/final.mp4` at
  10:44 EEST (h264 1080x1920 60 fps, aac 22050 Hz mono, 40.000 s; music
  seed 71 at gain 0.18; voice offset 0.6 s; captions at caption_y 0.75);
  loudness mean -16.9 dB, peak -0.0 dB; preview and 8x5 contact sheet
  written (`media/slits/compose.log`)

### Local QA

- frames at 0.02, 1.5, 8, 14, 20, 28.2, 30.5, 33, 35 and 39.95 s
  extracted from final.mp4 (`media/slits/frame-*.png`) and all of them
  plus the contact sheet inspected at full resolution
- 0.02 s: the overlay at the top, the title "One slit makes a fan. What
  do two slits make?" clear of it, both tanks flat with the wall and its
  one or two gaps, labels, "bright bands: 0 dark bands: 0"; works as the
  thumbnail
- 1.5 s: the first crests rolling in at the bottom of both tanks under
  the title (motion started within a second), caption "One slit makes
  a" in the clear band below the tanks
- 8 s: a semicircular fan from the one slit above, two overlapping fans
  with visible lanes below, the incoming stripes bold under the wall;
  caption "one slit."
- 14 s: the fans reach the screen, the gold strips light up (one hump
  above, three humps below), readouts 1/0 and 3/2, caption "Below, two
  fans"; the narration follows what is on screen
- 20 s: strips settled, "bright bands: 7 dark bands: 6" and "bright
  bands: 1 dark bands: 0", "dark at 5.8°" under the first dark hump,
  bright lanes and flat lanes in the water; caption "a trough, the
  water"
- 28.2 s: the payoff card fully in ("one slit: one smooth fan" / "two
  slits: 7 bright bands, dark between") at y 1592 and 1648, caption
  "make?" above it in the band
- 30.5 s: caption "Two slits make seven" with the card's "7 bright
  bands" and the readout "bright bands: 7" on screen: the payoff number
  is on screen when spoken
- 33 s: caption "dark water between" over the card; 35 s: no caption,
  the card and the steady pattern
- 39.95 s: the crossfade nearly complete, the title back, the strips
  and fans faded to flat water, readouts back to 0: the last frame fades
  to the first
- contact sheet: the captions match the narration word for word in
  order, the card is on from 28 s to the end, no text touches the frame
  edges (payoff line 2 spans x 95 to 985, the readouts end at 1040), the
  caption band y 1430..1530 holds only captions; approved

### Metadata

- `projects/slits/metadata.json`: title 98 characters ("One slit makes a
  fan. What do two slits 10 cm apart make? 7 bright bands, with dark
  water between."), description with the setup, the measured angles
  against the closed forms, the dark over bright, the single-slit
  profile, the 1.99 times summed intensity and 3.8 times centre, the
  incident wave and beach reflection, the arrival and settle times, the
  half-step, longer-window, steadiness and check-screen results, a Why
  paragraph, the rerun line and the AI line; 10 tags; category 27;
  private; containsSyntheticMedia true; selfDeclaredMadeForKids false
- not uploaded; the task stays open for the upload and publication
  evidence

### Release

- orchestrator review (10:49 EEST): the task evidence, the 8x5
  contact sheet and the full-resolution frames at 0.02, 14, 30.5 and 39.95 s inspected: the question over the two flat tanks with the wall gaps on the first frame; the fans reaching the screen with the strips lighting (1/0 and 3/2) under "Below, two fans" at 14 s; the seven gold humps, "dark at 5.8\u00b0", the readouts 7/6 and 1/0, the card and the caption "Two slits make seven" at 30.5 s; the crossfade at 39.95 s; the contact sheet shows the counts climbing 3, 5, 7 and holding, every caption in the clear band; approved for release
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
  section 5): `media/slits/final.mp4` (h264 1080x1920 60 fps, aac,
  40.000 s) and `projects/slits/metadata.json` (title, description,
  tags, category 27, private, altered-content disclosure). Once
  secrets/ is restored, `scripts/yt-upload.py slits` and then
  `scripts/yt-qa.py slits VIDEO_ID --wait --publish` release it, each
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
  d04e5f2a38bb1a841b572bf56b15ed9e; title 98 characters; the 8x5
  contact sheet re-inspected by the releasing session: question over
  the two dark tanks, ripples reaching the wall, one fan above and two
  fans below, the gold strip building to 1 bright / 0 dark and 7 bright
  / 6 dark, the card, the crossfade to the title; approved
- quota check before the insert: clock 2026-09-19T11:04:26+03:00; one upload attempt
  (tsunami, 11:04:05, uploaded private as DlmRoaSp85g, gate pending)
  recorded since the 2026-09-19 10:00 EEST boundary (log entries and
  media/*/upload.log both checked); this is insert attempt 2 of the
  hard cap of 5
- attempt 2 recorded at 2026-09-19T11:04:26+03:00, video name slits, before running
  `scripts/yt-upload.py slits`

- upload: `scripts/yt-upload.py slits` ran 11:04:26 to 11:04:32 EEST,
  token verified to see only the Seed Zero channel, video id
  e78W6KshdFg, private (`media/slits/upload.log`)

- gate: `scripts/yt-qa.py slits e78W6KshdFg --wait --publish` ran in
  the foreground at 11:05:53 EEST after one pre-gate read showed
  processing succeeded and 10 tags present: 15 of 15 pass (processed,
  succeeded, hd, 1080x1920, title, description, tags as a set, category
  27, not for kids, PT41S for the 40.000 s file, private);
  containsSyntheticMedia reads absent as on every earlier upload
  (`media/slits/publish.log`)
- publish: the same run set the video public at 2026-09-19T11:05:55+03:00;
  the re-read after 15 s shows privacyStatus public, madeForKids false,
  embeddable true; public at https://youtu.be/e78W6KshdFg
- slot resolution: published for the 2026-09-19 quota day; this
  supersedes the slipped resolution recorded under Release above

### Quota

- attempt 2 of the hard cap of 5 for the quota day that began
  2026-09-19T10:00 EEST; cost 1 + 1,600 + 1 + 1 + 50 + 1 = 1,654 units
  (the channels.list verification inside yt-upload.py, the insert, the
  pre-gate read, the gate read, the update, the re-read); day total
  after two attempts 3,308 units

### Repository

- committed as 079736e "Produce the day twenty-one slate as manual upload
  packets" (sims, projects, tasks, docs/niche.md, web/data; no media,
  previews or secrets) and pushed to origin/master at 10:50 EEST
- committed as 1762ebc "Publish the day twenty-one slate" (tasks,
  docs/niche.md, web/data; no media, previews or secrets) and pushed
  to origin/master at 2026-09-19 11:08 EEST
