# Produce short: Bus wait, on tempo versus at random

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day8

## Goal

Pillar idea from docs/niche.md, "the inspection paradox with buses",
not yet in the backlog. Day eight slate, second slot, probability
pillar in the channel's leading two-panel comparison format (double
pendulum 1,160 views, resonance 865, billiards 774, pendulum wave 723):
the same stop, the same ten thousand passengers, the same number of
buses, and one difference, the buses run on tempo or at random moments.
Measure the average wait on each road, the gap around each passenger,
the share waiting longer than a headway and the longest wait, and check
against the exact values for the uniform model, before scripting.

## Claim

Same stop, same ten thousand passengers, same number of buses over one
week. On tempo, one bus every ten minutes, the average wait is five
minutes. At random, the same one thousand eight buses at random moments
with the same average gap of ten minutes, the average wait is ten
minutes, double. A random moment usually lands in a long gap: the gap
around the average passenger is nearly twenty minutes, not ten. At
random three thousand seven hundred seventy six passengers waited over
ten minutes; on tempo none. The longest random wait is sixty six
minutes.

## Evidence

### Measurements

`sims/buses/buses.py --measure-only` with `projects/buses/manifest.json`
(seed 0, one week of 10,080 minutes, headway 10 minutes so 1,008 buses
per road, 10,000 passengers at uniformly random moments of the week,
the same moments on both roads; the tempo road's buses at minutes 10,
20, ..., 10,080; the random road's 1,008 bus times drawn uniformly over
the week from the same seeded stream and sorted; the week repeats, so a
passenger after the last bus waits for the first bus of the next week;
numpy RandomState; log in `media/buses/measure.log`):

- both roads: bus-to-bus gap mean 10.000 min; random road gaps median
  6.93, shortest 0.010, longest 67.21 min
- on tempo: passenger wait mean 4.965 min, median 4.95, longest 10.00;
  0 waited over 10 min; 1,002 waited under 1 min; gap around the
  passenger mean 10.000 min
- at random: passenger wait mean 10.018 min, median 6.99, longest
  66.35; 3,776 = 37.8% waited over 10 min, 1,369 = 13.7% over 20 min;
  923 waited under 1 min; gap around the passenger mean 19.899 min
- ratio of mean waits 2.02
- exact values for the uniform model (n points on a circle of length
  L): tempo wait L / 2n = 5.000, gap 10.000; random wait L / (n + 1)
  = 9.990, gap around the passenger 2L / (n + 1) = 19.980, share
  waiting over 10 min (1 - 10 / L)^n = 36.8%. The seed 0 share of
  37.8% is two standard deviations above the exact value (one standard
  deviation is 0.48 points); the means sit within 0.04 min of exact
- running averages as the week plays: tempo 4.79 (first 120 min), 4.78
  (600), 4.97 (3,000), 4.88 (day 1), 4.98 (2 days); random 12.16 (first
  120 min), 8.34 (600), 9.25 (3,000), 8.94 (day 1), 9.35 (2 days). The
  narration quotes only the whole-week values, which are on screen
  from the moment the week ends

### Production

- `sims/buses/buses.py` renders two roads (on tempo above, at random
  below) with buses driving to the stop, a queue of waiting passengers,
  live counts and running average wait, a clock that accelerates through
  the week (90 min by 9 s, 600 by 13 s, 3,000 by 16 s, the week by 18 s,
  so the whole-week averages are on screen before "five minutes" at
  18.05 s), then a slow replay while the histogram of waits, the gap
  around a passenger (27 s), the over-10-minute marker (31 s) and the
  longest-wait triangle (36.5 s) come in; payoff at 30 s
- narration `projects/buses/narration.txt`, 112 words; voice round trip
  passed, 38.31 s; music seed 22 at gain 0.18
- `scripts/compose.sh buses`: final.mp4 40.000 s, 1080x1920, 60 fps,
  h264 + aac, faststart, 3.5 MB, mean -16.2 dB, peak -0.0 dB
- inspected: contact sheet and full-resolution frames at 1.0, 8.5, 14.5,
  17.5, 18.6, 24.0, 31.6, 38.0 s. Fixed before the final render: the
  clock overlapped the panel label (moved to the label line, right
  aligned), the "gap around a passenger" readout overlapped the
  histogram title (title removed, unit moved to the axis label), PIL
  refused a bar under one pixel (bar guard). Fixed after the first
  composite: the histogram only appeared at 20 s and left the lower
  third of each panel empty for half the short, so it now accumulates
  live as passengers board and the axes are on screen from the start.
  Final composite clean: captions sit between the panels, bunched buses
  and a 42-person queue show on the random road at 14.5 s, the
  histogram and markers match the measured 0 and 3,776 over ten minutes
  and the 66 min longest wait

### Published

- Video id: `KpidSRY8hpM` <https://youtu.be/KpidSRY8hpM>
- Uploaded private: 2026-09-06 10:00:16 local (07:00:16Z; Pacific quota day
  2026-09-06, clock verified 10:00:11 EEST = 00:00:11 PDT),
  `scripts/yt-upload.py buses`.
- QA gate against `projects/buses/metadata.json` after processing
  succeeded: channel `UCWXsZTvrh_OHkzt6v1xkTsw`, uploadStatus processed,
  processingStatus succeeded, no rejection or failure reason, definition
  hd, embeddable, source stream 1080x1920, title, description, tags (as
  a set), categoryId 27, madeForKids false, selfDeclaredMadeForKids
  false, duration PT40S or PT41S, private before the flip. 15 of 15
  checks pass on 2 gate reads; the first gate read at 10:00:38 found the bus upload still processing (uploadStatus uploaded, processingStatus processing) and the second read 20 s later found it processed. Log in `media/buses/publish.log`.
- processingHints empty (faststart MP4).
- Made public: 2026-09-06 10:01:32 +03:00 (07:01:32Z) by videos.update on
  status (privacyStatus public, selfDeclaredMadeForKids false,
  containsSyntheticMedia true, embeddable true). The re-read 15 s later
  returned privacyStatus public, madeForKids false,
  selfDeclaredMadeForKids false, embeddable true.

### Quota for 2026-09-06

Spent 4,963 of the 10,000 daily units on the whole day-eight slate:
4,800 for three `videos.insert`, 3 for the channel-identity check inside
each upload, 150 for three `videos.update`, 7 for gate reads (one per
short before publishing, one extra while the bus upload processed, one
per short inside the publish run) and 3 for the confirming re-reads.
That leaves room for a full re-upload plus analytics, as the cadence
rule requires. No slot slipped.
