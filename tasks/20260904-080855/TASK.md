# Produce short: Resonance, a few percent off tempo

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day6

## Goal

Pillar idea from docs/niche.md "Chaos and physics: resonance building
until failure." Day six slate, third slot, chosen because the physics
two-panel comparison leads the channel (double pendulum 1,161, pendulum
wave 722, billiards 666). Two identical weights on identical springs,
the same small shake at the mount, one at the spring's own tempo and
one a few percent off. Measure how far each stretch grows and when the
on-tempo spring passes its break limit.

## Claim

Two identical springs get the same one millimeter shake at the mount.
Shaken exactly at the natural rhythm, one push per second, the stretch
grows about three millimeters every push and passes the sixty
millimeter limit at push twenty seven: snap. Shaken three percent
faster, the stretch matches for the first eight pushes (ten millimeters
at push four, twenty at push eight), peaks at twenty nine millimeters on
push sixteen, then shrinks, and never reaches thirty millimeters in ten
minutes and six hundred eighteen pushes.

## Evidence

### Measurements

`sims/resonance/resonance.py --measure-only` with
`projects/resonance/manifest.json` (natural frequency 1.0 Hz, damping
ratio 0.004, Q 125, mount shake 1.0 mm, limit 60 mm, base-excited
x'' + 2 zeta w0 x' + w0^2 x = A wd^2 sin(wd t), fixed-step RK4 at 16
substeps per frame, dt 0.00104 s; log in `media/resonance/measure.log`):

- on tempo (1.000 Hz): peak stretch by push 1: 1.6, 2: 4.6, 3: 7.6,
  4: 10.5, 5: 13.4, 6: 16.1, 7: 18.8, 8: 21.5, 9: 24.0, 10: 26.5,
  12: 31.4, 16: 40.3, 21: 50.3, 26: 59.1, 27: 60.0 mm; growth per push
  over pushes 1 to 10 between 2.51 and 3.06 mm (pi x shake = 3.14 mm)
- on tempo first crossings: 10 mm at 3.45 s (push 4), 20 mm at 7.44 s
  (push 8), 30 mm at 11.45 s (push 12), 40 mm at 15.48 s (push 16),
  50 mm at 20.48 s (push 21), 60 mm at 26.47 s (push 27): SNAP
- 3% faster (1.030 Hz): peak stretch by push 1: 1.6, 2: 4.8, 3: 7.9,
  4: 10.8, 5: 13.6, 6: 16.1, 7: 18.5, 8: 20.7, 9: 22.6, 10: 24.3,
  12: 26.9, 16: 29.1, 21: 26.5, 26: 19.6, 30: 13.0, 40: 14.6 mm
- 3% faster first crossings: 10 mm at 3.39 s (push 4), 20 mm at 7.35 s
  (push 8); 30, 40, 50 and 60 mm never
- 3% faster maximum: 29.1 mm at 15.25 s (push 16) in the 40 s scene;
  the 600 s run (618 pushes) has the same maximum, never snaps, and its
  last 60 s peak at 17.3 mm equals the closed-form gain 17.3x
- checks: RK4 half-step rerun differs by 6.36e-08 mm (on tempo) and
  3.09e-08 mm (off); closed-form steady-state gain 125x on tempo, so the
  on-tempo spring would reach 125 mm if it did not snap
- context, not narrated: +1% still snaps at 33.30 s; +2% peaks at
  39.4 mm; +5% at 19.5 mm; +10% at 11.3 mm; -3% at 26.0 mm

Push numbers are one-based (push n covers the n-th drive period). The
first measurement log labelled the per-push peaks with the zero-based
cycle index; the print was corrected and the log regenerated before
scripting.

### Production

- The shake starts 0.5 s into the video (`start_t`), so the snap at
  26.47 s of spring time lands at 26.97 s of video, inside the spoken
  "Snap." (26.91 to 27.25 s). Everything else runs in real time: one
  push per second on the left, so the push counter is a clock.
- Voice round-trip: 111 words, 37.93 s, second wording. The first
  draft's "never past thirty millimeters" was transcribed as "pass";
  it became "never reaches thirty millimeters".
- Layout fixes from the stills: the stretch and peak readouts were
  drawn on one line and overlapped, now three lines (peak, stretch,
  push and frequency); the snapped mass fell through the chart title,
  now it slides out of view above the readouts; the overlay
  "1.00 Hz vs 1.03 Hz | 1 mm shake | deterministic" and the payoff
  "on tempo: snapped. 3% faster: never" were shortened to fit the
  frame.
- Full-resolution frames at 0.5, 8, 16, 27.1, 30 and 36 s plus the
  contact sheet inspected after the final render: both curves overlap
  on the chart for the first eight pushes and split after, the red dot
  marks the snap on the limit line, captions sit between the readouts
  and the chart.
- Mix: mean -15.8 dB, peak -0.0 dB. Final 40.00 s, 1080x1920, 60 fps,
  music seed 17.

### Handoff verification (2026-09-04 09:32)

Re-checked before upload, in a second session:

- `--measure-only` re-run is byte-identical to the stored log, including
  the snap at 26.47 s during push 27, the 3% peak of 29.1 mm at 15.25 s,
  and the 600 s run over 618 pushes that never passes it.
- Voice round trip re-run against the shipped `voice.wav`: transcript
  matches `narration.txt` after normalisation. Duration 37.93 s.
- `final.mp4` re-probed: 1080x1920, 60 fps, h264 High, AAC, 40.000 s.
  Mean -15.8 dB, peak -0.0 dB, matching the recorded mix.
- Defect found and cleared: the on-disk frames at 8, 16 and 30 s predate
  the final compose and still show the earlier overlay and payoff running
  off both edges. Six frames re-extracted from the actual `final.mp4`
  (0.5, 8, 16, 27.1, 30, 36 s) show the shortened overlay
  "1.00 Hz vs 1.03 Hz | 1 mm shake | deterministic" and payoff
  "on tempo: snapped. 3% faster: never" fitting inside the frame. The
  stale PNGs were the only problem; the shipped video was already
  correct. "Snap." lands on the on-screen snap at 27.1 s.

### Published

- Video id: `_oFXN2TRdGE` <https://youtu.be/_oFXN2TRdGE>
- Uploaded private: 2026-09-04 10:01 local (just after the midnight
  Pacific quota reset), `scripts/yt-upload.py resonance`.
- QA gate against `projects/resonance/metadata.json` after processing
  succeeded: channel `UCWXsZTvrh_OHkzt6v1xkTsw`, uploadStatus
  processed, processingStatus succeeded, no rejection or failure reason,
  definition hd, embeddable, source stream 1080x1920, title, description,
  tags, categoryId 27, madeForKids false and selfDeclaredMadeForKids
  false all matching. 15 of 15 checks pass.
- Two check definitions were corrected during the gate, not the video:
  YouTube returns tags alphabetised rather than in submission order, and
  it rounds the reported duration up, so a 40.000 s upload reads back as
  PT41S. The already-published 40.000 s short `-Jkxs7kNpCg` reports the
  same PT41S, which confirms it is normal for this pipeline.
- Made public: 2026-09-04 10:02:54 +03:00 (07:02:54Z). Re-read after the flip confirms
  privacyStatus public with the synthetic-media disclosure preserved.

### Quota for 2026-09-04

Spent about 4,969 of the 10,000 daily units across the whole day-six
slate: 4,800 for three `videos.insert`, 3 for the channel-identity check
inside each upload, 153 for three publishes (3 reads plus 3
`videos.update` at 50 each), and 13 for QA reads. That leaves room for a
full re-upload plus analytics, as the cadence rule requires.
