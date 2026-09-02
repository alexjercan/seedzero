# Produce short: Traffic jam from nothing

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day4


## Goal

Backlog idea "Traffic jam from nothing: a ring road, one braking car;
measure the backward wave speed of the phantom jam. Research 2026-08-30:
use the Sugiyama twenty two car ring with no obstacle at all." Day four
slate, chosen for the physics-and-motion pillar that leads the channel
numbers (pendulum 1141, pendulum wave 699 views).

## Claim

Twenty two identical cars on a two hundred thirty metre ring, no obstacle,
spacing within three metres of even. The first car stops dead at fifty two
seconds. In the fifty seconds after the jam settles, its back edge moves
eighty five metres against the traffic: six point zero kilometres per hour
backward, while the cars average six point one forward.

## Evidence

### Model choice

The first pass used the optimal velocity model (Bando 1995). At every
setting that jammed inside two minutes it let cars overlap (minimum
headway 1.8-3.5 m against a 4 m car) and drove speeds negative, so it was
dropped for the intelligent driver model (Treiber 2000), which brakes as
the gap closes and never touched: minimum headway 5.22 m over the whole
run. A stopped car is held at zero speed until its gap opens (the standard
treatment; 67,097 such holds at dt 0.01, all inside the jam).

Parameter sweep (time headway T, acceleration a, spacing jitter): jams
need a < 0.8 m/s2 at this density; a = 0.3, T = 1.2 s, jitter 3 m gives
one dominant jam, a first stop at 52.4 s, and a clean track. Jitter 4 m
put two cars in contact at the start (headway 3.63 m) and was rejected.

### Measurements

`sims/traffic/traffic.py` with `projects/traffic/manifest.json`
(seed 0, 22 cars, ring 230 m, car 4 m, IDM: desired 50 km/h, T 1.2 s,
a 0.3 m/s2, b 2.0 m/s2, s0 2.0 m; jitter <= 3 m; RK4 at dt 0.01 s;
164 s of simulation played at 4x):

- mean headway 10.45 m, gap 6.45 m, equilibrium speed 13.3 km/h
- first car below 2 km/h at t = 52.4 s
- back of the main jam tracked from 62.4 s (10 s after the first stop) to
  112.4 s: moved -84.7 m, straight-line slope -1.673 m/s = -6.02 km/h,
  max residual 6.09 m, 3-6 stopped cars in it (mean 4.9)
- all cars in that window: average 6.1 km/h, max 21.2 km/h
- same tracker over the rest of the run (112.4-164 s): -5.37 km/h,
  max residual 2.81 m
- stop-front check (each stop paired with the most recent stop of the car
  ahead, 62 pairs): median 5.44 km/h backward, mean 6.32
- stop events 69, 3-4 per car; minimum headway 5.22 m; no contact
- after the first stop the cars average 6.0 km/h; the jam went 0.81 laps
  backward while the cars went 0.81 laps forward

Step check: first stop 52.4 s and the 50 s window slope -6.02 km/h are
identical at dt 0.02, 0.01 and 0.005 (pair median 5.50/5.49/5.47).

Measurement notes: a first wave-speed estimate tracked the slowest car
and jumped between jams (residuals 45-220 m), and a cross-correlation of
the stopped pattern was biased toward zero shift by cars sitting still.
Both were replaced by the back-of-jam tracker above, which is the slope of
the red band on the space-time chart. The narrated speed is that tracker
over the 50 s window that is complete on screen before it is spoken.

### Production

- Voice round-trip: 122 words, 39.29 s. One rephrase: "after it
  settled" transcribed as "it's", replaced by "after the jam formed".
- Timing: the sim plays at 4x, so the 50 s tracking window (62.4 s to
  112.4 s on the clock) is complete on screen at 28.1 s of video, and the
  payoff "the jam rolls backward at 6.0 km/h" fades in from 28.5 s, before
  "Six point zero" is spoken at about 31 s. The space-time band at the
  bottom shows the red jam stripes sloping against the traffic.
- Fixes before the final render: the payoff text overflowed the frame
  width and was shortened; the clock readout is labelled "clock" with
  "playing at 4x" so the 126 s value is not read as video time; the car
  colour scale tops out at 20 km/h so the jam reads red against green.
- Contact sheet and full-resolution frames at 14.5 s (first stop, clock
  58 s, "in, the first car") and 31.5 s (clock 126 s, slowest car 0.0
  km/h, payoff visible) inspected: captions clear of the chart labels,
  no clipping, every narrated number on screen when spoken.
- Mix: mean -15.7 dB, peak 0.0 dB. Final 41.00 s, 1080x1920, 60 fps,
  music seed 9.

### Upload and publish

- Uploaded private at 10:01 +03:00 on the fresh Pacific quota day (1,600
  units): video `jCLHCYeRziY`, <https://youtu.be/jCLHCYeRziY>.
- QA of the processed upload: processing succeeded, upload status
  processed, PT42S, hd, channel id UCWXsZTvrh_OHkzt6v1xkTsw, and title,
  description, all nine tags (YouTube returns them sorted), category 27
  and made-for-kids false verified against `projects/traffic/metadata.json`.
- Published public at 2026-09-02 10:07:47 +03:00 under the self-QA
  policy, then re-read to confirm. First of the day's three slots.
