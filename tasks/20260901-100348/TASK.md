# Produce short: Three-body figure eight

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day3

## Goal

Backlog idea "Three-body figure eight: the periodic solution, then nudge
it; measure how long the choreography survives." Morning briefing
candidate for the 2026-09-01 slate.

## Claim change

The briefing's framing did not survive measurement. Once the choreography
breaks, the escape is chaotic, so the survival time is not a property of
the orbit: with a nudge of 0.03 the break moved from lap 25.30 to 27.41 to
29.08 as the integrator step went 4e-3, 2e-3, 1e-3, and a nudge of 0.04
moved from lap 18.28 to 24.05. Narrating any of those numbers would fail
the "rerun it and get the same number" bar for anything but this exact
step size.

Per `docs/vision.md` step 3 the claim changed, not the numbers. The
measured, step-independent fact is the growth law: the figure eight is
linearly stable, so a tiny nudge grows in a straight line instead of
exponentially. That is also the better claim, because "the three-body
problem is chaos" is what the audience already believes.

## Claim

Two copies of the figure eight, one star moved a thousandth of its
starting distance from the center. After one lap the gap is twelve times
the nudge; after forty laps it is four hundred eighty two times, and every
lap added the same twelve. Chaos would have made it a trillion.

## Evidence

### Measurements

`sims/threebody/threebody.py` with `projects/threebody/manifest.json`
(nudge 0.001, dt 0.002, 40 laps, 3163 steps per lap):

- star starts 1.000000003 from the center, so the nudge is one thousandth
  of a starting radius
- gap after 1 lap: 0.011992 (12.0x the nudge)
- gap after 10 laps: 0.122517 (122.5x)
- gap after 20 laps: 0.245270 (245.3x)
- gap after 40 laps: 0.482101 (482.1x)
- straight-line fit 0.012175 per lap, max residual 0.0049
- a doubling law over the same 40 laps: 1.100e12x
- energy drift over 40 laps: 1.311e-11
- untouched copy stays a closed figure eight: max return error 1.096e-06,
  max pair distance 2.0000

Step-size check (this is why the claim is the growth law): gap after 1 lap
and after 40 laps are identical to six decimal places at dt = 4e-3, 2e-3,
1e-3 and 5e-4, and so is the fitted slope.

Long run at dt 2e-3: gap 0.688547 at lap 60, 0.843044 at lap 80, 0.942759
at lap 100. Still bounded, still sub-unit, growth flattening rather than
exploding.

### Production

- Voice round-trip: two iterations. "centre" transcribed as "center";
  narration now uses the US spelling. Final ok at 35.109 s, 117 words.
- Integrator: 4th-order Yoshida composition of leapfrog steps. The trail
  before t = 0 is the same scheme run backwards, so the opening frame has
  real history in it and there is no visual reset.
- Contact sheet: first frame is a full figure eight with trails and works
  as the thumbnail; "Chaos multiplies ... a trillion times bigger" lands
  at 18-24 s; lap 40 is reached at 29 s and the payoff "40 laps: 482x, not
  a trillion" fades in there; "After forty laps the gap is four hundred
  eighty two nudges wide" is spoken at 30-32 s with the readout on screen
  reading 0.482 (482x). Every narrated number is true when spoken.
- Two render passes: the first had the static orbit track too bright and
  an axis label ("one lap after the nudge") that read as an axis title.
  Dimmed the track, relabelled to "lap 1", and labelled the reference line
  "straight line".
- Mix: mean -15.6 dB, max 0.0 dB. Final 36.50 s, 1080x1920, 60 fps.

### Upload and publish

- Uploaded private on the fresh Pacific quota day (1,600 units):
  video `2zsfLnS9k34`, <https://youtu.be/2zsfLnS9k34>.
- QA of the processed upload: processing succeeded, upload status
  processed, PT37S, hd, channel id UCWXsZTvrh_OHkzt6v1xkTsw, and title,
  description, all nine tags, category 27 and made-for-kids false all
  verified against `projects/*/metadata.json`.
- Published public at 2026-09-01 10:44 +03:00 under the self-QA
  policy, then re-read to confirm the visibility flip. First of the day's three slots.
