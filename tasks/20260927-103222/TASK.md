# Produce short: Cut shot, a sliding cue ball beside a rolling one on the same half-ball hit

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day29

## Goal

Backlog idea (trend research 2026-09-27, task 20260927-102520, pillar 2
chaos and physics, collisions; read the full entry under "Added by trend
research 2026-09-27" in docs/niche.md):
"Cut shot: two cue balls at 2.0 m/s into a still ball half-ball (a 30
degree cut), one sliding with no spin beside one rolling; measure the
angle between the two paths once both balls roll; expect exactly 90.0
degrees for the sliding cue ball (the tangent line, 5/7 of 1.0 m/s
after 12.5 cm of slip) against 63.7 degrees for the rolling one, whose
kept spin bends it from 60 to 33.7 degrees off its line at 1.116 m/s
after 26 cm (v_final = (5/7) v_after + (2/7) v0 along the original
line; the 30 degree rule, about 27 degrees for 1/4 and 3/4 ball hits),
the object ball at 5/7 of 1.732 m/s in both; repeat the shot;
deterministic, no seed."

Orchestrator notes (2026-09-27, before this brief). Build from
`sims/cueball/cueball.py` and `projects/cueball/` (day 27, the head-on
follow shot, https://youtu.be/pcnwZnIKhh0, 957 views in two days): the
same balls (radius 28.6 mm), the same cloth (sliding friction mu 0.2,
g 9.80665), the same stun launch for the no-spin ball (a cue ball whose
backspin the cloth wears off exactly at the hit) and the same rolling
launch for the other, the same 2.0 m/s at impact, the same stripe that
shows the spin. The one change: the object ball sits half a ball to one
side, so the cue ball's centre is aimed at the object ball's edge (impact
parameter one radius, sin(cut) = 1/2, a 30 degree cut). The impact is
instantaneous, elastic and frictionless between the balls: the object
ball takes the component along the line of centres, v0 cos 30 = 1.732
m/s, 30 degrees off the cue line to one side; the cue ball keeps the
perpendicular component, v0 sin 30 = 1.000 m/s along the tangent line,
60 degrees off its line to the other side, and keeps whatever spin it
had. Panel A, no spin: after the hit the slip velocity at the contact
point is the ball's own velocity, so cloth friction only slows it along
the tangent line; it settles rolling at 5/7 of 1.000 = 0.714 m/s after
t = 2 v / (7 mu g) = 0.1456 s and 12.5 cm; its path and the object
ball's path meet at exactly 90.00 degrees. Panel B, rolling: the spin
is unchanged by the hit and is the spin of rolling at 2.0 m/s along
the original line, so the slip velocity at the contact point is u =
v_after - v0_vec = (-1.5, 0.866) m/s, magnitude 1.732 m/s, and for a
uniform sphere the slip keeps a fixed direction while it shrinks at
(7/2) mu g, so friction mu g acts along one fixed direction and the
cue ball's path is a parabola; it settles rolling at t = 2 |u| / (7 mu
g) = 0.2522 s with v_final = (5/7) v_after + (2/7) v0_vec = (0.929,
0.619) m/s, 1.116 m/s at 33.67 degrees off its original line, after
about 26 cm of curve; the angle between the two balls' final paths is
30 + 33.67 = 63.67 degrees. The object ball, both panels: leaves
sliding with no spin at 1.732 m/s, settles rolling at 5/7 = 1.237 m/s
after 0.2523 s and 37.5 cm, direction unchanged. Integrate the sliding
phases exactly or by RK4 and check them against these closed forms, as
cueball does; the research's throwaway slip loop hung on a 1e-6 stop
threshold smaller than one step of slip, so stop on the closed-form
settling time or on one step's worth of slip.

State every derived number above as a check the sim must print, not as
a fact: 90.00 and 63.67 degrees, 0.714 and 1.116 m/s, 33.67 degrees off
the line, 12.5 and 26 cm of slip, 0.1456 and 0.2522 s, the object ball's
1.732 then 1.237 m/s and 37.5 cm; the impact's momentum and energy
balance; and for the description the 1/4 and 3/4 ball hits (cuts of
14.48 and 48.59 degrees) whose rolling cue ball ends 27.6 and 27.3
degrees off its line (the "30 degree rule" of pool), and the same shot
at 1.0 and 3.0 m/s (the angles do not change, only the slip distances).

Drawing: two panels stacked as in cueball, a top-down cloth with a metre
tick, the cue ball with its stripe, the object ball half a ball to one
side, the same shot repeated; draw the tangent line (90 degrees from the
object ball's path) as a faint dashed guide in both panels so the eye
sees the rolling ball bend away from it; a live angle readout between
the two balls' headings once both roll, or a drawn angle arc at the end
of each shot; slow motion as cueball (1/8 speed); the shot period must
divide the scene length so the loop closes.

Day twenty-nine, first slot. Chosen because it is the sibling of the
cue ball follow short (957 views in two days), an everyday pool debate
("the balls split at a right angle") that is only true for a stun shot,
an exact angle a closed form checks, two panels on the same hit that
end on different lines, and no seed. Question in the first two seconds:
"Cut the ball. Do the two balls split at a right angle?" (or the
producer's better wording, e.g. "Hit the ball half on. Do they split at
ninety degrees?"; keep the words before the question under nine, avoid
"cue" as a first word since whisper clips onsets, pre-test the hooks;
keep the question identical in the title, the hook and the payoff).
Setup number: half a ball (the cut) or two meters a second (the speed):
pick one for the narration and put the other in the overlay. Payoff
number: ninety degrees with no spin against sixty four degrees rolling.
The 5/7 fractions, the slip distances and the 30 degree rule go to the
card and the description. Make the last frame equal the first. Measure
every fixed text line with PIL before rendering and keep every line
under 950 px, and the title under 100 characters with no < or >. Music
seed 89. Title length, tags and description as in projects/cueball.

## Claim

Two cue balls hit a ball at rest half on (the cue ball's centre aimed at
the object ball's edge, a 30 degree cut) at 2.0 m/s on a cloth with
sliding friction 0.2, one arriving sliding with no spin, the other
rolling: with no spin the two balls' final paths meet at exactly 90.00
degrees (the cue ball only slows along the tangent line, to 5/7 of 1.000
m/s after 12.5 cm); rolling, the kept spin bends the cue ball back to
33.67 degrees off its old line (1.116 m/s after 26.2 cm of curve) and
the paths meet at 63.67 degrees. Every number in the narration is
printed by the sim before the script is written; the sim sets the claim.

## Evidence

### Measurements

(recorded after the measure-only run, before scripting)

`sims/cutshot/cutshot.py --measure-only` with
`projects/cutshot/manifest.json` (ball radius 28.6 mm, equal masses, a
solid sphere I = 2/5 m R^2, cloth sliding friction mu 0.2 on any
slipping contact, g 9.80665 m/s^2, no rolling resistance, no friction
between the balls, an instantaneous elastic hit that hands the object
ball the velocity component along the line of centres and keeps each
ball's spin; the object ball half a ball to one side of the cue line,
impact parameter b = R = 28.6 mm, sin(cut) = 0.5000, cut 30 degrees, its
centre 4.95 cm ahead of the hit point and 2.86 cm to the side; the top
cue ball a stun shot, the bottom one rolling, both at 2.0 m/s at the
hit; the slip u = v - w keeps a fixed direction and shrinks at 7/2 mu g,
so every sliding phase is an exact constant-acceleration piece, -mu g
u_hat on the velocity and 5/2 mu g u_hat on the spin's surface speed;
the events, a slip closing or the hit, are roots of closed forms and
the slip is stopped on its closed-form settling time, not on a
threshold; shown at 1/8 speed, one shot every 7 s, 6 shots in 42 s,
drawn at 1000 px per metre on a 1.00 by 0.47 m cloth; deterministic,
no seed; first run at 10:45:25 EEST crashed on numpy 2's np.cross with
2-vectors (replaced by a 2D cross helper), second run 10:45:34 stopped
on the width assert (overlay 969 px, shortened), the numbers below
recorded from the 10:45:53 run before scripting; re-run at 10:47:29 and
10:51:34 EEST with the final title, hit point 0.545 m and 52.5 cm
run-up set from the voice timing, the physics unchanged, only the
launch positions, the panel geometry and the schedule differ; log in
`media/cutshot/measure.log`):

- launch (real time, t = 0 of each shot): the rolling cue ball leaves x
  = 0.0200 m at 2.0000 m/s rolling (spin 69.930 rad/s) and reaches the
  hit point after 0.2625 s (52.50 cm); the no-spin cue ball leaves x =
  -0.0476 m, 59.26 cm behind the hit point, at 2.5148 m/s with 45.004
  rad/s of backspin (surface speed 1.2871 m/s), so the cloth (mu g =
  1.9613 m/s^2 on the speed, 5/2 mu g = 4.9033 m/s^2 on the spin, 7/2 mu
  g = 6.8647 m/s^2 on the slip) wears the backspin off exactly at the
  hit (first run: run-up 40 cm, 0.2000 s, 2.3923 m/s, 34.289 rad/s)
- hit: at 0.2625 s (top) and 0.2625 s (bottom) of real time (target
  0.2625 s, diffs 5.6e-17 and 0.0e+00) the cue balls' centres reach x =
  0.5450 m with the centres 57.200 mm apart (2 R = 57.200) on a line of
  centres 30.00 degrees off the cue line; top cue ball 2.0000 m/s, spin
  surface speed 0.0e+00 m/s; bottom cue ball 2.0000 m/s, spin 69.930
  rad/s along its line (v0 / R = 69.930); right after: the object ball
  1.7321 m/s at 30.00 degrees off the cue line with no spin, both panels
  (closed form v0 cos 30 = 1.7321 m/s); the cue balls 1.0000 and 1.0000
  m/s at 60.00 degrees off the cue line to the other side, along the
  tangent line (closed form v0 sin 30 = 1.0000 m/s at 60 degrees), the
  top one with no spin and the bottom one with its rolling spin unchanged
  (69.930 rad/s along the old line); the two paths leave the hit 90.00
  degrees apart in both panels; momentum before and after the hit
  (2.0000, 0.0000) = (2.0000, 0.0000), translational energy 2.0000 =
  2.0000 per unit mass
- no spin: after the hit the slip at the contact is the ball's own
  velocity, so the cloth only slows it along the tangent line; it
  settles rolling at 0.7143 m/s, 60.00 degrees off its old line
  (unchanged), after 0.1457 s and 12.49 cm of slip (closed forms 5/7 of
  1.0000 = 0.7143 m/s, 2 v / (7 mu g) = 0.1457 s, v t - 1/2 mu g t^2 =
  12.49 cm; diffs 7.8e-16, 1.1e-16, 2.6e-16); the deviation from the
  tangent line along the way is at most 8.7e-14 mm; its path and the
  object ball's path meet at 90.00 degrees (a right angle)
- rolling: right after the hit the slip at the contact is v_after -
  v0_vec = (-1.5000, -0.8660) m/s, 1.7321 m/s at 150.00 degrees, and it
  keeps that direction while it shrinks at 7/2 mu g, so the cloth's push
  mu g points one fixed way and the path is a parabola; the cue ball
  settles rolling at (0.9286, -0.6186) = 1.1157 m/s, 33.67 degrees off
  its old line, after 0.2523 s and 26.23 cm of curve (25.99 cm as the
  crow flies) (closed forms v_final = 5/7 v_after + 2/7 v0_vec =
  (0.9286, -0.6186) = 1.1157 m/s at 33.67 degrees, 2 |u| / (7 mu g) =
  0.2523 s; diffs 2.2e-16, 0.0e+00, 5.6e-17); its spin turns from 69.930
  rad/s along the old line to 39.012 rad/s along the new one; the kept
  spin bends it from 60.00 to 33.67 degrees off its line, 26.33 degrees
  back from the tangent line; its path and the object ball's path meet
  at 63.67 degrees (30 + 33.67), not a right angle
- object ball, both panels: leaves sliding at 1.7321 m/s with no spin,
  30 degrees off the cue line, and rolls at 1.2372 m/s after 0.2523 s
  and 37.46 cm, direction unchanged (closed forms 5/7 of 1.7321 = 1.2372
  m/s, 0.2523 s, 37.46 cm; diffs 0.0e+00, 0.0e+00, 5.6e-17); in the
  rolling panel the object ball and the cue ball settle at the same
  instant (both slips start at 1.7321 m/s); the balls leave the cloth
  2.64 s (object) and 3.18 s (top cue) and 3.01 s (bottom cue) of video
  after the hit and the trails stay
- answer: the two balls' final paths meet at 90.00 degrees with no spin
  and 63.67 degrees rolling; the cue ball settles at 0.7143 m/s after
  12.5 cm of slip with no spin and at 1.1157 m/s after 26.2 cm of curve
  rolling
- for the description (same speed, other cuts; the 30 degree rule):
  three-quarter ball (14.48 degree cut, sin 0.25): the rolling cue ball
  leaves at 75.52 degrees and settles 27.63 degrees off its line at
  0.7457 m/s after 16.6 cm, the paths 42.10 degrees apart; half ball
  (30.00, sin 0.50): 60.00 to 33.67 degrees, 1.1157 m/s, 26.2 cm, paths
  63.67 apart; quarter ball (48.59, sin 0.75): 41.41 to 27.27 degrees,
  1.5469 m/s, 29.2 cm, paths 75.86 apart; with no spin every cut splits
  at 90.00
- for the description (same cut, other speeds): 1 m/s: no spin 90.00
  degrees after 3.1 cm of slip, rolling 63.67 degrees (33.67 off its
  line) after 6.6 cm of curve, the object ball 0.6186 m/s after 9.4 cm;
  2 m/s: 12.5 and 26.2 cm, the object ball 1.2372 m/s after 37.5 cm; 3
  m/s: 28.1 and 59.0 cm, the object ball 1.8558 m/s after 84.3 cm; the
  angles do not change with the speed
- schedule printed by the sim (final manifest; the first run had the hit
  point at 0.42 m, a 40 cm run-up and first_shot_at -0.6, hits at 1.0 +
  7 k s, replaced after the voice timing): launches every 7 s at 6.70,
  13.70, 20.70, 27.70, 34.70, 41.70 s (the first shot launched at -0.3
  s, its cue balls 7.5 cm into the run-up on the first frame); the hit
  2.10 s after each launch, at 1.80, 8.80, 15.80, 22.80, 29.80, 36.80 s;
  the no-spin cue ball rolls again 1.17 s after the hit (2.97, 9.97,
  16.97, 23.97, 30.97, 37.97 s); the rolling cue ball and both object
  balls roll again 2.02 s after the hit (3.82, 10.82, 17.82, 24.82,
  31.82, 38.82 s); the balls leave the cloth 2.64 to 3.18 s after the
  hit and the trails and readouts stay; the shot crossfades to the next
  launch over the last 0.8 s of each 7 s (out 6.20 to 6.60, in 6.60 to
  7.00 s after the launch); title until 3.4 s; payoff card from 27.0 s;
  the title fades back in over the last 0.5 s and the last frame
  repeats the first (6 shots in 42 s, exactly periodic)
- text widths (DejaVuSans-Bold): overlay 915 px at 34 (the first draft
  "two cue balls 2 m/s, half-ball hit | mu 0.2 | no seed" measured 969
  px and tripped the assert before any render); title lines 390, 508
  and 680 px at 56 (the question "do the two balls split at a right
  angle?" would be about 1300 px on one 56 px line, so the title is
  three lines: "Cut the ball:" / "do the two balls" / "split at a right
  angle?"); counter 241 px at 40; legend 777 px at 28; panel labels 165
  and 146 px at 40; state words 105, 102 and 126 px at 28; speed readout
  383 px and split readout 232 px at 40; cue tag 123, scale label 94 and
  tangent tag 192 px at 28; payoff lines 273, 863, 596, 886 and 892 px
  at 40; nothing over 950 px; the sim asserts every line under 950 px
  and that the row label plus state (ending at x 416) clears the readout
  (starting at x 597)

Narration numbers: two meters a second (setup; hit_speed_m_s 2.0, both
cue balls at 2.0000 m/s at the hit), ninety degrees (payoff; the no-spin
panel's final paths 90.00 degrees apart) and sixty four degrees (payoff;
the rolling panel's 63.67 degrees, said to the nearest degree, 63.7 on
the card and the readout). The half-ball cut goes to the overlay ("half
ball") and the narration's "half on"; the 5/7 fractions, the 12.5 and
26.2 cm, the 33.67 degrees, the 0.1457 and 0.2523 s, the object ball's
1.732 then 1.237 m/s and 37.5 cm and the 30 degree rule go to the card
and the description. The numbers match the brief; no change to the
claim.

### Production

- layout (`sims/cutshot/cutshot.py`, built from sims/cueball/cueball.py:
  the same balls, cloth, stun and rolling launches, crossfade loop,
  text-width machinery and forked render workers, the physics
  generalised to 2D vectors for the half-ball hit): overlay "two cue
  balls 2 m/s | half ball | mu 0.2 | no seed" at y 96 (drawn by compose
  from the manifest), title "Cut the ball: / do the two balls / split at
  a right angle?" at y 172/234/296 (56 px, three lines) for the first
  3.4 s, then the counter "shot N of 6" at y 236 (40 px) and the legend
  "no spin at the hit above, rolling below; 1/8 speed" at y 290 (28 px);
  two top-down cloths (dark green, x 40 to 1040, 1000 by 470 px, 1000 px
  per metre, drawn at 2x and reduced) at y 404 to 874 and 944 to 1414,
  each with its row above it at y 380 / 920: the label "no spin" /
  "rolling" (40 px), the state word (sliding, slipping, rolling; 28 px
  muted) and, right-aligned at x 980, the readout "cue ball N m/s"
  before the hit and "split N°" (the live angle between the two balls'
  velocities) after it, gold once both balls roll; on each cloth the cue
  line across the middle (faint solid), the tangent line through the hit
  point at 60 degrees (teal dashed, tagged "tangent line" at its upper
  left end), a cross at the hit point, a 10 cm scale bar bottom left,
  the cue ball as a shaded sphere seen from above with a coral stripe
  band through its spin axis and a dark dot (the orientation integrated
  by Rodrigues steps from the spin, 8 substeps a frame, so the stripe
  rolls, stops with the stun ball and tilts as the rolling ball's spin
  turns), the object ball gold with a dot, a "cue ball" tag over the cue
  ball from the moment its centre is on the cloth until the hit, and
  from the hit the trails of both balls (white
  and gold) which stay after the balls leave the cloth; captions at
  caption_y 0.75 (y 1440 to 1520); the five-line card from y 1592 (40
  px, 56 px pitch); the HUD fades out over the first 0.25 s of the last
  0.5 s and the title fades in over the last 0.25 s, the last frame
  equal to the first; every shot is the same table of pieces indexed by
  frame offset, so the periodicity is exact
- whisper pre-tests (10:45:53 to 10:46:06 EEST, `media/cutshot/hooks/`,
  log `hooks/pretest.log`), question onset from silencedetect (-35 dB,
  0.08 s) plus the 0.6 s offset: hook1 "Hit a ball half on. Do the two
  balls split at a right angle?" passed, question at 1.80 s (silence
  1.08 to 1.20 s); hook2 "Cut the ball. Do the two balls split at a right
  angle?" passed, question at 1.37 s (silence 0.63 to 0.77 s); hook3 "Hit
  a ball half on. Do they split at a right angle?" failed ("Hit" came
  back "it", the onset clip); hook2 kept: the earliest question, the
  brief's own first wording, and a hard first consonant after the "Hit"
  clip on hook3
- narration (`projects/cutshot/narration.txt`): 104 words, 17
  sentences; "two meters a second", "ninety degrees" and "sixty four
  degrees" the only measured numbers, all in words ("two cue balls",
  "half on" and "one way" are not measurements); the question inside the
  first three words and identical in the title, the hook and the payoff;
  the last line "Rolling, no. Sixty four degrees." split into two
  sentences after the first compose so the caption chunker keeps "Sixty
  four degrees." on one caption (as "Rolling, no: sixty four degrees."
  it cut "sixty" from "four degrees."); no "still", "pull", "spread", "straight", "a hundred", "metres",
  "brakes", "drifts", "games", "coins", "let's", "onto", "for ever" or
  sentence-initial "Where", "Spin" or "Slower"
- smoke frames (`--frames`, three passes): pass 1 at 10:45:56 EEST (0,
  1.0, 2.0, 3.02, 5.0, 6.6, 10.02, 30.5, 34.0, 41.98 s on the first
  schedule) found the "cue ball" tag following the ball off the cloth
  into the caption band at 5.0 s (y 1471) and the "tangent line" tag at
  the line's lower end under the exiting cue ball at 3.02 s; fixed by
  showing the tag only before the hit, moving the tangent tag to the
  line's upper left end and making the cue line solid so "the dashed
  line" named one line; pass 2 at 10:47:34 (0, 1.0, 2.0, 3.02, 5.0, 6.6,
  30.5, 41.98 s) clean except the readout "split 0.0°" on the top panel
  at the exact hit frame (the two panels' hit times differ by 1e-16 s
  and state_at picked the pre-hit piece); fixed by keying the hit flag
  on each panel's own hit time and giving state_at a 1e-9 s boundary
  tolerance; pass 3 at 10:51:37 on the final schedule (0, 1.8, 8.8,
  15.8, 17.1, 22.8, 23.8, 27.6, 31.95, 33.5, 41.98 s) clean: both panels
  "split 90.0°" at the hit frames, the top ball settled gold at 17.1 s
  with the bottom one curving at 72.3°, the card lit at 27.6 s under the
  run-up of shot 5, both readouts gold (90.0°, 63.7°) at 31.95 s with the
  object balls in the top right corners, the trails and gold readouts
  holding at 33.5 s after the balls left, 41.98 s equal to 0 s; nothing
  in the caption band on any frame; pass 4 at 10:59:58 (6.7, 6.9, 27.6
  s) after the first composed QA frame at 27.6 s showed the "cue ball"
  tag at the cloth's left edge with the stun ball still off the cloth
  (the tag is now drawn only while the ball's centre is on the cloth):
  no tag over the off-cloth ball at 6.7 and 27.6 s, both tags at 6.9 s
- voice (`scripts/voiceover.sh cutshot`, log `media/cutshot/voice.log`):
  pass 1 at 10:47:54 EEST failed, "stripe" came back "strike" ("Watch
  the stripe." replaced by "Watch the spin."); pass 2 at 10:48:12 failed,
  "dashed" came back "dash ed" and the payoff's "So, do the two balls"
  came back "to" ("the dashed line" replaced by "the green line", the
  payoff opened with the bare question "Do the two balls split at a
  right angle?", which mirrors the hook); pass 3 at 10:48:58 passed,
  "ok: transcript matches narration (33.413515s)", 33.41 s (kept as
  `media/cutshot/voice-pass3.wav`); pass 4 at 10:59:54 with the payoff
  split into "Rolling, no. Sixty four degrees." passed, "ok: transcript
  matches narration (33.343855s)"; voice.wav 33.34 s, ends at 33.94 s
  of video with the 0.6 s offset; Piper re-voices the whole take, so
  every sentence moved by up to 0.3 s against pass 3
- timing (`scripts/voice-timing.py media/cutshot/voice.wav`, log
  `media/cutshot/timing.log`, pass 4, video time): "Cut the ball." 0.60
  to 1.45, "Do the two balls split at a right angle? ... Both hit the
  ball half on." 1.45 to 10.70 (whisper lumped the first eight
  sentences), "The ball goes one way." 10.70 to 12.19, "The cue balls
  the other." 12.19 to 13.59, "with no spin." 13.59 to 14.72, "The top
  one follows the green line," 14.72 to 16.82, "A right angle exactly."
  16.82 to 18.56, "The bottom one keeps its spin. ... Same hit." 18.56
  to 24.92, "Same bend, every time, do the two balls split at a right
  angle, with no spin." 24.92 to 29.68, "Yes." 29.68 to 30.46, "ninety
  degrees rolling no sixty four degrees" 30.46 to 33.94; the sentence
  boundaries from silencedetect on the take (-35 dB, 0.08 s, video
  time): "Cut the ball." ends 1.32, pause to 1.58, so "Do" sounds at
  1.58 s; "angle?" ends 3.58; "Two cue balls." 3.75 to 4.65; "Two meters
  a second." 4.77 to 5.87; "No spin on top." 6.08 to 7.11; "Rolling
  below." 7.30 to 7.97; "Watch the spin." 8.13 to 9.08; "Both hit the
  ball half on." 9.24 to 10.58; "The ball goes one way," 10.83 to
  12.00; "the cue balls the other." 12.37 to 13.46; "With no spin,"
  13.73 to 14.55; "the top one follows the green line:" 14.90 to 16.68;
  "a right angle, exactly." 16.97 to 18.42; "The bottom one keeps its
  spin." 18.69 to 20.15; "The cloth grabs that spin and bends the ball
  back toward its old line." 20.34 to 24.09; "Same hit," 24.23 to 24.75;
  "same bend," 25.08 to 25.80; "every time." 26.00 to 26.57; "Do the two
  balls split at a right angle?" 26.71 to 28.56; "With no spin," 28.74
  to 29.52; "yes:" 29.84 to 30.32; "ninety degrees." 30.60 to 31.56;
  "Rolling, no. Sixty four degrees." 31.75 to 33.78 (no pause over 0.08
  s between "no." and "Sixty"); the voice ends at 33.94 s
- schedule (manifest): the hit point moved from the brief-era 0.42 m to
  0.545 m with a 52.5 cm run-up (2.10 s of video) and first_shot_at -0.3
  s so the hits land at 1.8 + 7 k s (set on the pass-3 timing, checked
  again on pass 4): the first hit at 1.80 s inside the spoken question
  (1.58 to 3.58 s), the second at 8.80 s under "Watch the spin." (8.13
  to 9.08) and just before "Both hit the ball half on." (9.24 to 10.58),
  the third at 15.80 s so the no-spin ball slides along the tangent line
  15.80 to 16.97 s under "the top one follows the green line:" (14.90 to
  16.68) and stops on the line at 16.97 s as "a right angle, exactly."
  starts (16.97 to 18.42), the fourth at 22.80 s so the rolling ball's
  curve 22.80 to 24.82 s runs under "bends the ball back toward its old
  line. Same hit," (about 22.5 to 24.75), the fifth at 29.80 s so the
  top readout reads "split 90.0°" from 29.80 s and its ball stops at
  30.97 s under "ninety degrees." (30.60 to 31.56), and the bottom
  readout turns gold at "split 63.7°" at 31.82 s, before "Sixty four
  degrees." (about 32.3 to 33.78; both readouts gold from 31.82 s once
  the object balls stop too), the trails and readouts holding until the
  fade at 34.30 s; title_until 3.4 (the spoken question ends 3.58 s, the
  caption "angle?" runs to about 4.5 s by proportional timing); payoff_t
  27.0 with a 0.6 s fade, so the card is fully lit at 27.6 s, inside the
  spoken question (26.71 to 28.56) and before the numbers
- footage (`sims/cutshot/cutshot.py` with the manifest, 8 forked
  workers piping raw frames to libx264 crf 16): first render started
  10:51:48 EEST (PID 340175 in `media/cutshot/render.pid`), 2520 frames
  in about 3 minutes, `media/cutshot/footage.mp4` 42.00 s at 60 fps;
  re-rendered at 11:00:35 (PID 349978) with the cue-tag rule, same
  checks: "loop check: last frame differs from the first in 0 px (max
  channel difference 0)", "periodicity check: the scene drawn live at 42
  s differs from 0 s in 0 px", "loop step: the frame before the last
  differs from the last in 6111 px (the incoming cue balls are still
  fading in on that frame)"; log `media/cutshot/render.log`
- compose (`scripts/compose.sh cutshot`, log `media/cutshot/compose.log`):
  first pass at 10:56:53 EEST (voice pass 3, footage 1; its QA found the
  edge tag and the split caption, see Local QA), final pass at 11:02:30
  EEST: music seed 89 at 42.00 s, overlay from the manifest, 33 caption
  chunks, `media/cutshot/final.mp4` 42.000000 s, `preview.mp4` 42.07 s,
  `sheet.png` 8 by 6 at 1 fps
- text widths: see Measurements; the render asserted every line under
  950 px on both renders; the composed frames show the widest lines
  (payoff line 5, 892 px; the overlay, 915 px) inside the frame with
  margins on both sides

### Local QA

- frames (`media/cutshot/frame-<t>.png` from final.mp4 at 0.02, 2.0,
  8.8, 17.1, 23.8, 27.6, 31.0, 33.0 and 41.98 s, plus `sheet.png`)
  inspected after the final compose: 0.02 s: overlay and the three-line
  title from frame 0, both panels with "cue ball" tags over the cue
  balls 7.5 cm into the run-up, readouts "cue ball 2.43 m/s" (stun ball
  still shedding backspin) and "cue ball 2.00 m/s", the dashed tangent
  line with its tag, the hit cross, the 10 cm bars, no caption (the
  thumbnail); 2.0 s: caption "Do the two balls", the title still up, 0.2
  s after the first hit with both object balls off along the gold line
  and both cue balls on the tangent line, readouts "split 90.0°" (top,
  sliding) and "split 87.2°" (bottom, slipping, already bending); 8.8 s:
  caption "Watch the spin.", "shot 2 of 6" and the legend in place of
  the title, the exact hit frame of shot 2 with the balls touching on
  the line of centres and both readouts "split 90.0°"; 17.1 s: caption
  "top one follows the", shot 3, the top cue ball settled and rolling
  on the tangent line at "split 90.0°" with its white trail straight
  along the dashed line, the bottom cue ball slipping off the line at
  "split 72.3°" with a visibly curved trail, both object balls near the
  top right; 23.8 s: caption "ball back toward its", shot 4, the top
  ball sliding on the line at 90.0°, the bottom ball at "split 76.2°"
  with the curve starting; 27.6 s: caption "Do the two balls", the card
  fully lit ("cut the ball: / do the two balls split at a right angle?
  / no spin: yes, exactly 90.0° / rolling: no, 63.7°: its kept spin
  bends it / to 33.7° off its line after 26 cm of curve"), the counter
  still "shot 4 of 6" while shot 5's balls fade in at the left edge
  with no floating tag (the stun ball is off the cloth, the rolling ball
  half in); 31.0 s: caption "With no spin, yes:", shot 5 with the top
  ball just settled at "split 90.0°" and the bottom ball slipping at
  "split 73.6°", the card lit; 33.0 s: caption "Sixty four degrees.",
  all four balls off the cloth, the trails holding (straight white on
  the tangent line above, the bent white curve below, gold object-ball
  lines to the top right corners), both readouts gold "split 90.0°" and
  "split 63.7°", the card lit; 41.98 s: the title back, the HUD and card
  gone, the balls 7.5 cm in, matches 0.02 s; the contact sheet shows
  the captions in narration order, six identical shots at 7 s spacing,
  the card from 27 s to 41 s and the title back on the last thumbnail;
  nothing in the caption band (y 1440 to 1530) or the overlay band (y
  96 to 130) on any frame, the title rows clear of the panel labels
- the first compose (10:57 EEST, voice pass 3) was inspected at the same
  times: it showed the "cue ball" tag at the cloth's left edge with the
  stun ball still off the cloth during each fade-in (27.6 s), and the
  captions cut the payoff number in two ("Rolling, no: sixty" then
  "four degrees."); both fixed and re-rendered, re-voiced and
  re-composed, see Production
- question inside two seconds: the title carries the question from
  frame 0; the narration reaches "Do the two balls split at a right
  angle?" after three words; the word "Do" sounds at 1.58 s of video
  (pause 1.32 to 1.58 s in video time on the full take; hook2 pre-test
  1.37 s; the first hit at 1.80 s lands inside the question); the
  caption "Cut the ball." shows 0.60 to 1.56 s, "Do the two balls" 1.56
  to 2.84 s, "split at a right" 2.84 to 4.13 s and "angle?" 4.13 to
  4.45 s
- captions: the 33 chunks read back from `media/cutshot/captions.filter`
  (drawtext 2 to 34; drawtext 1 is the overlay) join to the 104 words of
  `projects/cutshot/narration.txt` word for word; the longest chunk is
  "Two meters a second." at 20 characters; "ninety degrees." 31.70 to
  32.34 s, "Rolling, no." 32.34 to 32.98 s, "Sixty four degrees." 32.98
  to 33.94 s (proportional timing runs about 1 s behind the voice at the
  end: "ninety degrees." is spoken 30.60 to 31.56 s)
- payoff number on screen when spoken: the card with "no spin: yes,
  exactly 90.0°" and "rolling: no, 63.7°" is lit from 27.6 s, before the
  payoff question ends (28.56 s); the top readout reads "split 90.0°"
  from the fifth hit at 29.80 s through "ninety degrees." (30.60 to
  31.56 s); the bottom readout turns gold "split 63.7°" at 31.82 s,
  before "Sixty four degrees." (about 32.3 to 33.78 s); both readouts
  and the card stay until the fade at 34.30 s
- last frame equals first: the sim's own check on the raw frames, 0 px
  different (max channel difference 0) and the live 42 s scene equal to
  0 s in 0 px; in `final.mp4` frame 2519 against frame 0 differs by
  0.368 per channel on average (20,805 px over 8, max 91 on text edges),
  against 0.224 between frames 0 and 1 of the same file, so h264 noise
  only; the frames at 0.02 and 41.98 s look identical
- stream: h264 1080x1920 at 60 fps, 2520 frames, 42.000000 s; aac 22050
  Hz mono; 3,305,535 bytes; md5 e4a3cfe8dc2aa1b8dec96bb2767acca9; the first compose's final
  (md5 f9663f35473e1a4c42e97c188ad000f0) is superseded

### Metadata

- `projects/cutshot/metadata.json`: title "Cut the ball: do the two
  balls split at a right angle? No spin: 90 degrees. Rolling: 63.7
  degrees" (97 characters); description (4,873 characters) with the
  setup (two 57.2 mm cue balls at 2.0 m/s on mu 0.2 cloth hitting a ball
  at rest half on, the 30 degree cut, one with no spin and one rolling,
  the exact piecewise integration, 1/8 speed, six shots in 42 s, no
  seed), a Measured list (the hit at 0.2625 s with the centres 57.200 mm
  apart, the 1.7321 and 1.0000 m/s after the hit, the 90.00 degrees
  with no spin and the 0.7143 m/s after 0.1457 s and 12.49 cm, the
  rolling ball's 1.1157 m/s at 33.67 degrees after 0.2523 s and 26.23
  cm and the 63.67 degrees, the object ball's 1.2372 m/s after 37.46
  cm, the 30 degree rule table for three-quarter, half and quarter ball
  and the 1, 2 and 3 m/s table), a Why paragraph (the hit hands over the
  line-of-centres component and leaves the spin; the cloth's push on a
  slipping ball points along the fixed slip direction), the rerun note
  ("Rerun sims/cutshot/cutshot.py with projects/cutshot/manifest.json
  and you get these numbers exactly.") and the last line "Made end to
  end by an AI agent: simulation, footage, voice, music, and edit."; no
  "<" or ">"; 11 tags (cut shot, cue ball, stun shot, tangent line, pool
  physics, billiards, do the two balls split at a right angle, physics,
  physics visualization, simulation, shorts); categoryId "27";
  privacyStatus "private"; containsSyntheticMedia true;
  selfDeclaredMadeForKids false

Deviations from the brief: the hook is "Cut the ball." (the brief's
first wording; hook1 "Hit a ball half on." also passed the round trip
with the question at 1.80 s, but whisper clipped "Hit" to "it" on hook3,
so the hard "C" was kept and the question sounds at 1.58 s on the full
take). The spoken setup number is "two meters a second" and the half-ball
cut is carried by "half on" in the narration and "half ball" in the
overlay. The payoff says "sixty four degrees" for the measured 63.67
(the card and the readout show 63.7°). The title is three lines because
the question is about 1300 px at 56 px on one line. The run-up is 52.5
cm with the hit point at 0.545 m and first_shot_at -0.3 s so the hits
land at 1.8 + 7 k s on the narration beats (the brief's geometry was a
40 cm run-up with the hit at 0.42 m). "Watch the stripe." became "Watch
the spin." and "the dashed line" became "the green line" for whisper;
the dashed teal line on screen is tagged "tangent line" and the cue line
is solid and faint so "the green line" names one line. The payoff's last
sentence is "Rolling, no. Sixty four degrees." so the caption keeps the
number whole. The "cue ball" tag is drawn only while the ball's centre
is on the cloth. Every measured number matched the brief, so the claim
did not change.

## Niche note

[produced 2026-09-27 as "Cut the ball: do the two balls split at a right
angle?", two cue balls at 2.0 m/s hitting a ball at rest half on (a 30
degree cut, sin 0.5) on mu 0.2 cloth, the top one with no spin at the
hit and the bottom one rolling, shown 8x slow, 6 shots in 42 s: with no
spin the two paths meet at exactly 90.00 degrees, the cue ball slowing
along the tangent line to 0.7143 m/s (5/7) after 0.1457 s and 12.49 cm;
rolling, the kept spin bends the cue ball 26.33 degrees back from the
tangent line to 33.67 degrees off its old line at 1.1157 m/s after
0.2523 s and 26.23 cm of curve, the paths meeting at 63.67 degrees; the
object ball leaves at 1.7321 m/s and rolls at 1.2372 m/s after 37.46 cm;
three-quarter, half and quarter ball cuts give 42.10, 63.67 and 75.86
degrees rolling and 90.00 at every cut with no spin; the angles do not
change with speed; the title is three lines because the question is
about 1300 px at 56 px; task 20260927-103222]

## Upload

- orchestrator review (2026-09-27T11:10:44+03:00): task evidence, sheet.png and frames at 0.02,
  17.1, 33.0 and 41.98 s inspected; numbers match measure.log and the
  orchestrator's closed forms; approved for upload
- upload attempt 1 of 5 for the quota day that began 2026-09-27T10:00
  EEST, recorded at 2026-09-27T11:10:44+03:00 before starting scripts/yt-upload.py; zero
  attempts were on record since the boundary
- uploaded private as aEgJbsPwqeo at 11:10:48 EEST (media/cutshot/upload.log);
  scripts/yt-qa.py --wait --publish: gate 15 of 15 (PT43S for the 42.000 s
  file), set public at 11:11:32 EEST and re-read public
  (media/cutshot/publish.log); https://youtu.be/aEgJbsPwqeo
- attempt 1 of 5 complete at 2026-09-27T11:12:08+03:00: 1,655 units (1 channels read, 1,600
  insert, 54 gate, update and re-read)
- slot resolution: published for the 2026-09-27 quota day at 11:11:32 EEST,
  https://youtu.be/aEgJbsPwqeo

### Quota
- attempt 1 of the hard cap of 5 for the quota day that began
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
