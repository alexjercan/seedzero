# Produce short: marble on rails, the same marble down the same 20 degree slope on two rails beside a flat board, which gets down first

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day38

## Goal

Backlog idea (trend research 2026-10-05, task 20261005-100712, pillar 2
chaos and physics, everyday mechanics; read the full "Marble on rails
(Galileo's groove)" bullet under "Added by trend research 2026-10-05" in
docs/niche.md): the same marble down the same slope, on a flat board
beside two rails; the rails lose.

Orchestrator notes (2026-10-06; closed forms in /tmp/day38/closed.py with
the log /tmp/day38/closed.log; g = 9.807 m/s^2). Read
/tmp/day38/producer-conventions.md first. The model: a solid marble of
radius R = 1 cm (2 cm across; I = k m R^2, k = 2/5; the mass cancels, say
so) rolls without slipping from rest 1.00 m (measured along the slope)
down a slope at 20 degrees; no air drag, no rolling resistance (say so:
chosen). Top band, the slow "no" case: RAILS, two thin rails whose contact
lines are 1.6 R = 1.6 cm apart, so the marble touches each rail at
contact radius r = sqrt(R^2 - (0.8 R)^2) = 0.6 R = 6.0 mm and its centre
sits 0.4 R = 4.0 mm lower than on a board; rolling without slipping on
the rails means v = omega r, so a = g sin a / (1 + k R^2 / r^2) = g sin a
/ (1 + 0.4 / 0.36) = 1.5888 m/s^2; 1 m in 1.1220 s at 1.7826 m/s, spin
297.1 rad/s = 47.3 turns per second at the bottom, 26.5 turns over the
metre, spin share of the energy k R^2 / r^2 / (1 + k R^2 / r^2) = 0.5263,
grip needed 0.1149. Bottom band, the fast "yes" case: FLAT BOARD, contact
radius R: a = g sin a / (1 + k) = 2.3959 m/s^2; 1 m in 0.9137 s at 2.1890
m/s, spin 218.9 rad/s = 34.8 turns per second, 15.9 turns over the metre,
spin share 0.2857, grip needed 0.1040. Ratios: acceleration 1.5079 (closed
(1 + k / 0.36) / (1 + k)), time 1.2280 (its square root), margin 0.2083
s; when the flat marble reaches the bottom the rail marble is 0.6632 m
down, 33.7 cm short. Both marbles stop on a stop pad at the foot (no
bounce, the stop itself not modelled, say so). Integrate both bands with
RK4 at dt = 1e-4 s (position along the slope and spin angle), bisection
for the arrival at the foot, a half-step rerun agreeing within 1e-9 s, as
a check against the closed forms; print the energy balance per kilogram
(potential drop g L sin a = 3.3542 J/kg; flat: translation 2.3959 + spin
0.9583; rails: translation 1.5888 + spin 1.7654), the no-slip condition
(the grip needed), the table at 0.2 s steps (positions and speeds of
both) and the description variants.

Checks, not facts (the sim must print and compare; state them as checks):
flat 0.9137 s, 2.1890 m/s, a 2.3959; rails 1.1220 s,
1.7826 m/s, a 1.5888; ratios 1.5079 and 1.2280; rail marble at 0.6632 m
when the flat one lands (33.7 cm short); table: 0.2 s flat 0.0479 m rails
0.0318 m; 0.4 s 0.1917 against 0.1271 m; 0.6 s 0.4313 against 0.2860 m;
0.8 s 0.7667 against 0.5084 m; spin 218.9 against 297.1 rad/s at the
bottom (34.8 against 47.3 turns per second; 15.9 against 26.5 turns over
the metre); spin share 0.2857 against 0.5263; grip needed 0.1040 against
0.1149; for the description: rails 1.2 R apart (contact 0.8 R) 0.9843 s,
1.8 R apart (contact 0.436 R) 1.3607 s; 10 degree slope 1.2823 against
1.5746 s and 30 degrees 0.7557 against 0.9279 s (the ratio 1.2280 the
same); the times do not depend on the marble's radius (print a 5 mm and a
20 mm marble with rails 1.6 radii apart: unchanged); a sliding ice cube
0.7722 s; Galileo's groove 8.5 punti wide for a ball of radius 10 punti:
contact 0.9052 R, acceleration 5.93 percent less (TPT 2024 says 5.75).
Print the schedule in video time, the text widths and the layout
clearances.

Drawing: two-band layout (sims/deskchain style; sims/uphill draws a 20
degree slope with a rolling ball whose stripe shows the spin, sims/
cartramp draws a slope with a stop pad, sims/rollrace rolls bodies down a
ramp with RK4; read deskchain whole and the drawing parts of uphill),
side view, the rails on top (the "no" case) and the flat board below;
same scale, same clock. The slope descends left to right, 1.00 m long
(about 650 px per metre: 611 px of run, 222 px of rise; its top near x
80 and the band's content well under the label rows), a stop pad at the
foot. The marble is drawn larger than life (say so in measure.log: a
drawn radius of about 22 px against the model's 1 cm = 6.5 px) with a
stripe or two spots so the spin shows; the physics uses R = 1 cm. In the
rails band draw the rail as a thin double line and the marble sunk by
the drawn 0.4 of its radius; add a small end-view inset in each band (a
circle on a flat line in the flat band; a circle resting on two rail
dots with the contact radius 0.6 R marked in gold in the rails band) so
the mechanism is visible. A dashed gold mark on the slope where the rail
marble is (0.6632 m) at the instant the flat marble reaches the foot,
with "34 cm short" (24 px). Label rows (40 px, coloured): "on two rails"
(coral) and "on a flat board" (teal). Readouts (28 px): left column
"N.NN m down the slope" and the clock; right column "speed N.NN m/s" and
"spin NN.N turns/s". Gold event rows: top "rails: down in 1.122 s" (lit
at the arrival and held), bottom "flat board: down in 0.914 s" (lit and
held). Shown at 1/4 speed; cycle 8 s (480 frames): release at 0.5 s of
the cycle, the flat marble arrives at 0.5 + 4 * 0.9137 = 4.155 s, the
rail marble at 0.5 + 4 * 1.1220 = 4.988 s, hold, reset by a crossfade
over the last 0.6 s of the cycle; 5 cycles in 40 s, exactly periodic,
the last frame equal to the first. The legend row after the title: "same
marble, same slope, 1/4 speed"; the shared clock in real seconds since
the release. Overlay: "2 cm marble, 20 deg slope, 1 m | no seed"
(measure it; shorten if over 950 px).

Day thirty-eight, second slot. Chosen because "which gets down first"
on the same slope reads as a tie to most viewers and is not, the two
panels end visibly differently (one marble at the foot while the other
is a third of the way up), the factor is exact (sqrt((1 + k / 0.36) /
(1 + k)) = 1.2280) and the repeat is a natural loop; it is also Galileo's
own groove, which the description can mention (not the narration).
Question in the first two seconds: "Same marble, same slope. Flat board
or two rails: which one gets down first?" (pre-test; a question-first
form "Which marble gets down first, on a flat board or on two rails?"
lands at 0.6 s). Keep the question identical in the title, the hook and
the payoff. Setup number: "twenty degrees" (or "one meter"; one setup
number only). Payoff: the flat board, in zero point nine one seconds;
the rails, one point one two seconds (the two panel results; at most
two numbers in the payoff beat; "thirty four centimeters short" may
replace the second time if it reads better: pre-test both). The
mechanism sentence must follow the picture: on rails the marble touches
at a smaller radius, so it must spin faster for every centimeter it
rolls, and the spin takes more than half of the energy (the inset and
the spin readout show this). Whisper risks: "rails" and "rail" (pre-
test), "marble" (pre-test), sentence-initial "Spin" (clipped; never
start a sentence with it), "flat board" (pre-test; "Slow hoop" came
back "flow" once), "slope" (pre-test), "Galileo" (keep it out of the
narration), avoid "do you", avoid "too", "zero point nine one" (pre-
test; "point nine one" is the fallback). Pre-test hooks with
scripts/voiceover.sh and keep the one whose question lands earliest
under two seconds. Measure every fixed text line with PIL before
rendering and keep every line under 950 px, and the title under 100
characters with no < or >. Music seed 116. Templates: sims/deskchain
(two-band layout, asserts, the clock, the crossfade; read it whole),
sims/uphill (20 degree slope, a rolling ball with a stripe),
sims/cartramp (slope with a stop pad, gold mark on the slope),
sims/rollrace (rolling bodies, RK4, arrival events). Sim name rails:
sims/rails/rails.py, projects/rails/, media/rails/.

## Claim (expected; the sim's numbers replace these)

The same 2 cm solid marble rolls 1 m from rest down the same 20 degree
slope. On a flat board it reaches the bottom in 0.914 s (2.396 m/s^2).
On two rails 1.6 radii apart it touches at 0.6 of its radius, must spin
1.67 times faster for the same speed, and reaches the bottom in 1.122 s
(1.589 m/s^2), 1.228 times longer; when the flat marble lands the rail
marble is 34 cm short. Spin takes 52.6 percent of the energy on the
rails against 28.6 percent on the board. Narrated: twenty degrees
(setup); zero point nine one against one point one two seconds (payoff).
Card: the question; the answer with 0.914 against 1.122 s; 34 cm short
when the flat one lands; spin 28.6 against 52.6 percent of the energy;
rails 1.2 R apart 0.984 s, 1.8 R 1.361 s; any marble size, any slope:
1.228 times longer. Description: the model statement, the equations,
the two runs, the spacing and slope variants, the energy split,
Galileo's groove, the checks.

## Claim

The same 2 cm solid marble (radius 1 cm, k = 2/5, the mass cancels) rolls
without slipping from rest 1 m down the same 20 degree slope; no air drag,
no rolling resistance (chosen). On a flat board it reaches the foot in
0.9137 s at 2.1890 m/s (a = g sin a / 1.4 = 2.3959 m/s^2). On two rails
1.6 radii apart it touches at 0.6 of its radius (6.0 mm, its centre 4.0
mm lower), must spin 1.667 times faster for the same speed, and reaches
the foot in 1.1220 s at 1.7826 m/s (a = g sin a / (1 + 0.4 / 0.36) =
1.5888 m/s^2), 1.2280 times longer (sqrt of the acceleration ratio
1.5079); when the flat marble lands the rail marble is 0.6632 m down,
33.7 cm short. Spin takes 52.6 percent of the energy on the rails against
28.6 percent on the board (3.3542 J/kg: 2.3959 + 0.9583 flat, 1.5888 +
1.7654 rails); grip needed 0.1040 and 0.1149. Narrated: twenty degrees
(setup, with "shown four times slower"); the flat board in zero point
nine one seconds, the rails one point one two (payoff). Card: the
question; the flat board 0.914 s, the rails 1.122 s; 34 cm short when the
board one lands; spin takes 28.6 against 52.6 percent; rails 1.2 R apart
0.984 s, 1.8 R 1.361 s; any size, any slope: 1.228 times longer.

## Evidence

### Measurements

Sim: sims/rails/rails.py with projects/rails/manifest.json (RK4 at dt =
1e-4 s on position, spin angle and speed, bisection for the arrival at
the foot, half-step rerun, closed forms; deterministic, no seed, no wall
clock). Log: media/rails/measure.log (exit 0; the full final log
follows).

Brief checks (the sim prints "checks against the brief (44 checks, 0
failed)"): flat 0.9137 s (sim 0.913661), 2.1890 m/s (2.188996), a
2.3959 (2.39585); rails 1.1220 s (1.121958), 1.7826 m/s (1.782598), a
1.5888 (1.58883); ratios 1.5079 (1.50794) and 1.2280 (1.22798); rail
marble 0.6632 m (0.663158) when the flat one lands, 33.7 cm short
(33.6842); table 0.2 s 0.0479 / 0.0318 (0.047917 / 0.0317766), 0.4 s
0.1917 / 0.1271 (0.191668 / 0.127106), 0.6 s 0.4313 / 0.2860 (0.431253 /
0.285989), 0.8 s 0.7667 / 0.5084 (0.766672 / 0.508425); spin 218.9 /
297.1 rad/s (218.9 / 297.1), 34.8 / 47.3 turns per second (34.8389 /
47.2849), 15.9 / 26.5 turns over the metre (15.9155 / 26.5258); spin
share 0.2857 / 0.5263 (0.285714 / 0.526316); grip 0.1040 / 0.1149
(0.103991 / 0.114938); rails 1.2 R apart 0.9843 s (0.984346), 1.8 R
1.3607 s (1.36072); 10 degrees 1.2823 / 1.5746 s (1.28226 / 1.57459), 30
degrees 0.7557 / 0.9279 s (0.755659 / 0.927935), ratio 1.2280 the same;
5 mm and 20 mm marbles on rails 1.6 radii apart: times unchanged
(asserted within 1e-9 s); ice cube 0.7722 s (0.772184); Galileo contact
0.9052 R (0.905193), 5.93 percent less (5.92517; TPT 2024 says 5.75);
energy 3.3542 = 2.3959 + 0.9583 = 1.5888 + 1.7654 J/kg. Also printed: the
RK4 arrivals agree with the closed forms within 4e-14 s and the half-step
rerun within 8e-14 s; the no-slip condition; the schedule; the text widths
(every line under 950 px, max 915 px for payoff line 2); the layout
clearances. All checks passed; no check failed.

Final measure.log:

```
Tue Oct  6 10:26:39 AM EEST 2026
warning: Git tree '/home/alex/personal/seedzero' is dirty
setup: side view, two panels on one clock, the same slope drawn the same way at the same scale: a solid marble of radius R = 1 cm (2 cm across; I = k m R^2 with k = 0.4; the mass cancels) rolls without slipping from rest 1 m (measured along the slope) down a slope at 20 degrees; no air drag and no rolling resistance (chosen); g = 9.807 m/s^2; top panel two thin rails whose contact lines are 1.6 R = 1.6 cm apart, bottom panel a flat board; both marbles stop on a stop pad at the foot (no bounce; the stop itself is not modelled); both panels integrated by classical RK4 at 10000 steps per second (dt = 1e-04 s) on the position along the slope, the spin angle and the speed, the arrival at the foot located by bisection inside the step, checked against the closed forms and a half-step rerun; shown at 1/4 speed on a 8 s cycle (480 frames) with the release 0.5 s into the cycle, 5 cycles in 40 s; drawn at 650 px per metre along the slope (611 px of run, 222 px of rise); the marble is drawn larger than life, a drawn radius of 22 px against the model's 1 cm = 6.5 px, and the drawn marble rolls without slipping at its drawn size (its stripe turns 1.667 times faster on the rails, as the model's spin does); the readouts are the model's; deterministic, no seed
rails (top panel): contact lines 1.6 R apart, so the marble touches at the contact radius r = sqrt(R^2 - (0.8 R)^2) = 0.6000 R = 6.0 mm and its centre sits 4.00 mm lower than on a board; rolling without slipping means v = omega r, so a = g sin a / (1 + k R^2 / r^2) = g sin a / (1 + 1.1111) = 1.5888 m/s^2; RK4 from rest: 1 m in 1.121958 s = 1.1220 s at 1.782598 m/s = 1.7826 m/s (closed form sqrt(2 L / a) = 1.121958 s, a t = 1.782598 m/s; diffs +3.8e-14 s, -3.4e-13 m/s), 11220 steps; the position stays within 6.9e-14 m of a t^2 / 2 over the run; half-step rerun (dt = 5e-05 s): 1.121958036 s (-3.3e-14 s) at 1.782597865 m/s (+7.1e-13 m/s); spin at the bottom omega = v / r = 297.1 rad/s = 47.3 turns per second (RK4 spin angle 166.6667 rad = 26.53 turns over the metre; closed L / (2 pi r) = 26.53), the spin share of the energy k R^2 / r^2 / (1 + k R^2 / r^2) = 0.5263, grip needed (friction over the contact normal forces, k (R / r) a / (g cos a)) 0.1149
flat board (bottom panel): contact lines 0 R apart, so the marble touches at the contact radius r = sqrt(R^2 - (0 R)^2) = 1.0000 R = 10.0 mm and its centre sits 0.00 mm lower than on a board; rolling without slipping means v = omega r, so a = g sin a / (1 + k R^2 / r^2) = g sin a / (1 + 0.4000) = 2.3959 m/s^2; RK4 from rest: 1 m in 0.913661 s = 0.9137 s at 2.188996 m/s = 2.1890 m/s (closed form sqrt(2 L / a) = 0.913661 s, a t = 2.188996 m/s; diffs +1.4e-14 s, -4.1e-14 m/s), 9137 steps; the position stays within 3.0e-14 m of a t^2 / 2 over the run; half-step rerun (dt = 5e-05 s): 0.913660997 s (-7.7e-14 s) at 2.188995708 m/s (+5.7e-13 m/s); spin at the bottom omega = v / r = 218.9 rad/s = 34.8 turns per second (RK4 spin angle 100.0000 rad = 15.92 turns over the metre; closed L / (2 pi r) = 15.92), the spin share of the energy k R^2 / r^2 / (1 + k R^2 / r^2) = 0.2857, grip needed (friction over the contact normal forces, k (R / r) a / (g cos a)) 0.1040
flat against rails: a ratio 1.5079, time ratio 1.2280 (closed (1 + k / 0.36) / (1 + k) = 1.5079, sqrt 1.2280); margin 0.2083 s; speed at the bottom 2.1890 against 1.7826 m/s; the rail marble must spin 1.6667 times faster for the same speed
rail marble when the flat marble reaches the bottom (t 0.9137 s): 0.6632 m down at 1.4516 m/s, 33.7 cm short = 34 cm short (closed a_r t_f^2 / 2 = 0.6632 m)
flat marble when the rail marble is halfway: t 0.7933 s, flat at 0.7540 m
  t 0.2000 s: flat 0.0479 m (v 0.4792), rails 0.0318 m (v 0.3178)
  t 0.4000 s: flat 0.1917 m (v 0.9583), rails 0.1271 m (v 0.6355)
  t 0.6000 s: flat 0.4313 m (v 1.4375), rails 0.2860 m (v 0.9533)
  t 0.8000 s: flat 0.7667 m (v 1.9167), rails 0.5084 m (v 1.2711)
  t 0.9137 s: flat 1.0000 m (v 2.1890), rails 0.6632 m (v 1.4516)
  t 1.0000 s: flat 1.0000 m (v 2.1890), rails 0.7944 m (v 1.5888)
  t 1.1220 s: flat 1.0000 m (v 2.1890), rails 1.0000 m (v 1.7826)
energy per kg at the bottom: potential drop g L sin a = 3.3542 J/kg; flat: translation 2.3959 + spin 0.9583 = 3.3542; rails: translation 1.5888 + spin 1.7654 = 3.3542; spin share 28.6 percent flat against 52.6 percent on the rails; the RK4 speeds give 3.3542 and 3.3542 J/kg
no-slip condition: the friction needed is k (R / r) m a and the contact normal forces add to m g cos a (R / r), so the grip needed is 0.1040 on the board and 0.1149 on the rails (a chosen grip of 0.3 or more holds both)
for the description: rails 1.2 R apart (contact radius 0.800 R = 8.0 mm, centre sunk 2.00 mm): a 2.0641 m/s^2, 1 m in 0.9843 s (closed 0.9843 s) at 2.0318 m/s, spin 40.4 turns/s (19.9 turns over the metre), grip needed 0.1120, spin share 0.3846; rails 1.8 R apart (contact radius 0.436 R = 4.4 mm, centre sunk 5.64 mm): a 1.0802 m/s^2, 1 m in 1.3607 s (closed 1.3607 s) at 1.4698 m/s, spin 53.7 turns/s (36.5 turns over the metre), grip needed 0.1076, spin share 0.6780; 10 degree slope: flat 1.2823 s, rails 1.5746 s (ratio 1.2280, the same); 30 degree slope: flat 0.7557 s, rails 0.9279 s (ratio 1.2280, the same); marble radius 5 mm, rails 1.6 R apart (8 mm): times unchanged (0.9137 and 1.1220 s; the ratio depends only on the gap in radii; spin 69.7 against 94.6 turns/s); marble radius 20 mm, rails 1.6 R apart (32 mm): times unchanged (0.9137 and 1.1220 s; the ratio depends only on the gap in radii; spin 17.4 against 23.6 turns/s); a sliding ice cube (no spin, no friction) for reference: a = g sin a = 3.3542 m/s^2, 1 m in 0.7722 s (closed 0.7722 s); Galileo's groove 8.5 punti wide for a ball of radius 10 punti: contact radius 0.9052 R, acceleration x 0.9407 (5.93 percent less than on a flat board; TPT 2024 says 5.75), time x 1.0310
checks against the brief (44 checks, 0 failed): flat time (s): brief 0.9137, sim 0.913661, diff -3.9e-05: ok; flat speed (m/s): brief 2.189, sim 2.189, diff -4.3e-06: ok; flat a (m/s^2): brief 2.3959, sim 2.39585, diff -4.9e-05: ok; rails time (s): brief 1.122, sim 1.12196, diff -4.2e-05: ok; rails speed (m/s): brief 1.7826, sim 1.7826, diff -2.1e-06: ok; rails a (m/s^2): brief 1.5888, sim 1.58883, diff +2.8e-05: ok; a ratio: brief 1.5079, sim 1.50794, diff +3.7e-05: ok; time ratio: brief 1.228, sim 1.22798, diff -1.9e-05: ok; rail marble at the flat landing (m): brief 0.6632, sim 0.663158, diff -4.2e-05: ok; short (cm): brief 33.7, sim 33.6842, diff -1.6e-02: ok; flat spin (rad/s): brief 218.9, sim 218.9, diff -4.3e-04: ok; rails spin (rad/s): brief 297.1, sim 297.1, diff -3.6e-04: ok; flat turns/s: brief 34.8, sim 34.8389, diff +3.9e-02: ok; rails turns/s: brief 47.3, sim 47.2849, diff -1.5e-02: ok; flat turns over the metre: brief 15.9, sim 15.9155, diff +1.5e-02: ok; rails turns over the metre: brief 26.5, sim 26.5258, diff +2.6e-02: ok; flat spin share: brief 0.2857, sim 0.285714, diff +1.4e-05: ok; rails spin share: brief 0.5263, sim 0.526316, diff +1.6e-05: ok; flat grip needed: brief 0.104, sim 0.103991, diff -8.5e-06: ok; rails grip needed: brief 0.1149, sim 0.114938, diff +3.8e-05: ok; contact radius (R): brief 0.6, sim 0.6, diff -1.1e-16: ok; centre sunk (mm): brief 4, sim 4, diff +1.8e-15: ok; potential drop (J/kg): brief 3.3542, sim 3.35419, diff -8.5e-06: ok; flat translation (J/kg): brief 2.3959, sim 2.39585, diff -4.9e-05: ok; flat spin energy (J/kg): brief 0.9583, sim 0.95834, diff +4.0e-05: ok; rails translation (J/kg): brief 1.5888, sim 1.58883, diff +2.8e-05: ok; rails spin energy (J/kg): brief 1.7654, sim 1.76536, diff -3.6e-05: ok; ice cube (s): brief 0.7722, sim 0.772184, diff -1.6e-05: ok; Galileo contact (R): brief 0.9052, sim 0.905193, diff -6.7e-06: ok; Galileo percent less: brief 5.93, sim 5.92517, diff -4.8e-03: ok; table 0.2 s flat (m): brief 0.0479, sim 0.047917, diff +1.7e-05: ok; table 0.2 s rails (m): brief 0.0318, sim 0.0317766, diff -2.3e-05: ok; table 0.4 s flat (m): brief 0.1917, sim 0.191668, diff -3.2e-05: ok; table 0.4 s rails (m): brief 0.1271, sim 0.127106, diff +6.2e-06: ok; table 0.6 s flat (m): brief 0.4313, sim 0.431253, diff -4.7e-05: ok; table 0.6 s rails (m): brief 0.286, sim 0.285989, diff -1.1e-05: ok; table 0.8 s flat (m): brief 0.7667, sim 0.766672, diff -2.8e-05: ok; table 0.8 s rails (m): brief 0.5084, sim 0.508425, diff +2.5e-05: ok; rails 1.2 R apart (s): brief 0.9843, sim 0.984346, diff +4.6e-05: ok; rails 1.8 R apart (s): brief 1.3607, sim 1.36072, diff +2.5e-05: ok; 10 deg flat (s): brief 1.2823, sim 1.28226, diff -4.1e-05: ok; 10 deg rails (s): brief 1.5746, sim 1.57459, diff -1.1e-05: ok; 30 deg flat (s): brief 0.7557, sim 0.755659, diff -4.1e-05: ok; 30 deg rails (s): brief 0.9279, sim 0.927935, diff +3.5e-05: ok
schedule (video time, 1/4 speed): cycles of 8 s start at -1.00, 7.00, 15.00, 23.00, 31.00, 39.00 s (the first 1.00 s before the first frame); both marbles are let go 0.5 s into each cycle at 7.50, 15.50, 23.50, 31.50, 39.50 s (the stop pins fade over 0.3 s); the flat marble reaches the foot 3.65 s after the release at 3.15, 11.15, 19.15, 27.15, 35.15 s (4.155 s into the cycle; its event row lights and the gold '34 cm short' mark fades in over 0.3 s in the rails band); the rail marble reaches the foot 4.49 s after the release at 3.99, 11.99, 19.99, 27.99, 35.99 s (4.988 s into the cycle; its event row lights), 0.83 s of video after the flat one; the reset crossfade runs over the last 0.6 s of each cycle (from 6.40, 14.40, 22.40, 30.40, 38.40 s; the readouts out over its first half and in over its second); on the first frame the cycle is 1.00 s in (0.125 s real after the release: the rail marble rolling at 1.2 cm, the flat marble rolling at 1.9 cm); title until 3 s; payoff card from 33.6 s; the title fades back in over the last 0.5 s and the last frame repeats the first (the scene is periodic: 40 s holds exactly 5 cycles)
text widths (the on-screen strings verbatim): overlay@34 789 px '2 cm marble, 20 deg slope, 1 m | no seed', title line 1@56 773 px 'Two rails or a flat board:', title line 2@56 848 px 'which one gets down first?', legend@40 824 px 'same marble, same slope, 1/4 speed', clock@28 390 px '1.122 s after the release', clock held@28 194 px 'held, at rest', label rails@40 265 px 'on two rails', down rails@28 359 px '1.00 m down the slope', contact rails@28 388 px 'touches at 0.6 R = 6 mm', speed rails@28 239 px 'speed 1.78 m/s', spin rails@28 266 px 'spin 47.3 turns/s', event rails@40 484 px 'rails: down in 1.122 s', inset r rails@24 118 px 'r = 0.6 R', label flat@40 332 px 'on a flat board', down flat@28 359 px '1.00 m down the slope', contact flat@28 348 px 'touches at R = 10 mm', speed flat@28 239 px 'speed 2.19 m/s', spin flat@28 266 px 'spin 34.8 turns/s', event flat@40 607 px 'flat board: down in 0.914 s', inset r flat@24 67 px 'r = R', inset label@24 121 px 'end view', mark@24 161 px '34 cm short', payoff line 1@40 606 px 'which one gets down first?', payoff line 2@40 915 px 'the flat board: 0.914 s; the rails: 1.122 s', payoff line 3@40 869 px '34 cm short when the board one lands', payoff line 4@40 826 px 'spin takes 28.6 against 52.6 percent', payoff line 5@40 897 px 'rails 1.2 R apart: 0.984 s; 1.8 R: 1.361 s', payoff line 6@40 884 px 'any size, any slope: 1.228 times longer'
row check: the left column ends at x 428 px, the right column starts at x 774 px; both end 136 px under the band top; the event rows span 152 to 192 px under the band top, right-aligned at x 1040 from x 433 (widest 607 px); the slope's start contact at x 80.0, 240.0 px under the band top, the foot (s = 1 m) at x 690.8, 462.3 px, the plank's lower end corner at x 746.2, 497.4 px, the stop pad's far corners at x 740.6, 433.6 and 725.6, 475.0 px; the marble's highest pixel at the start 202.2 (rails) and 198.7 (flat) px under the band top, its downhill extreme at the foot x 717.7 and 719.0 px; the stop pin's top at 227.0 px; the gold mark's dashed line rises to 321.7 px and its label is centred at x 630, 310 px (161 px wide); the end-view inset spans 212.0 to 346.0 px under the band top and x 796 to 1036 px; each band is 550 px tall (y 330 to 880 and 880 to 1430); the caption band starts at y 1440; the title rows end at y 280 and the overlay band ends at y 130
Tue Oct  6 10:26:39 AM EEST 2026
```

### Production

- Manifest: projects/rails/manifest.json (fps 60, 40 s, 1/4 speed, cycle
  8 s, release 0.5 s into the cycle, first_cycle_at -1.0, reset
  crossfade 0.6 s, pin fade 0.3 s, mark fade 0.3 s, 650 px/m along the
  slope with the start contact at x 80 and 240 px under the band top,
  marble drawn 22 px, title until 3 s, payoff_t 33.6 s, hold 0.6 s,
  loop fade 0.5 s, music seed 116, music gain 0.18, voice offset 0.6,
  caption_y 0.75, overlay "2 cm marble, 20 deg slope, 1 m | no seed").
- Layout: two bands (rails y 330-880, flat board 880-1430), label rows
  at 40 px under the band top, readouts at 84 and 120 (left "N.NN m down
  the slope" and "touches at 0.6 R = 6 mm" / "touches at R = 10 mm";
  right "speed N.NN m/s" and "spin NN.N turns/s", gold and held at the
  foot), gold event rows at 172 right-aligned ("rails: down in 1.122 s",
  "flat board: down in 0.914 s"); the slope from x 80 to the foot at x
  690.8 (611 px of run, 222 px of rise) with a stop pad; the rails band
  has a thin base, a far rail behind the marble and the near rail drawn
  over it so the marble sits sunk by 0.4 of its drawn radius; the end-
  view inset (centre x 860) shows the marble on a line or on two rail
  dots with the spin axis dashed and the contact radius in gold ("r =
  R", "r = 0.6 R"); a dashed gold mark from 0.6632 m to the foot with
  "34 cm short" after the flat landing; the drawn marble rolls without
  slipping at its drawn size (printed in measure.log); the readouts are
  the model's.
- Schedule (video time): releases 7.50, 15.50, 23.50, 31.50, 39.50 s;
  flat landings 3.15, 11.15, 19.15, 27.15, 35.15 s; rail landings 3.99,
  11.99, 19.99, 27.99, 35.99 s; crossfades from 6.40, 14.40, 22.40,
  30.40, 38.40 s. Frame 0: 0.125 s after a release, the marbles rolling
  at 1.2 cm (rails) and 1.9 cm (flat).
- Smoke frames viewed: media/rails/smoke-{0.0,1.5,2.0,3.4,8.0,10.6,11.2,
  12.0,34.0,35.5,38.7}.png (first pass) and smoke-{0.0,3.4,11.2}.png
  after the drawing fixes: frame 0 title over both marbles near the top;
  3.4 s the flat marble at the pad with its event row and the gold "34
  cm short" mark, the rail marble at 0.76 m; 10.6 s both rolling at
  0.48 / 0.72 m; 11.2 s the flat marble landed, the rail one at 0.68 m
  with the mark fading in; 12.0 s both landed with both event rows;
  35.5 s the card up. Fixes after the first pass: payoff line 3
  shortened (1129 px), the "34 cm short" label moved up (it touched the
  dashed tick), the inset moved left (its label reached x 1056), the
  rails drawn as a thin double line over a thin base with a far rail
  behind the marble.
- Render: media/rails/render.log, footage.mp4 (2400 frames, about 30 s;
  rendered twice, the second time after the title change); loop check 0
  px (max channel difference 0); periodicity check 0 px; loop step 1911
  px between the last two frames.
- Hook pre-tests (media/rails/hooks/pretest.log): hook1 "Flat board or
  two rails: which one gets down first? Same marble, same slope, twenty
  degrees." FAILED ("board or" heard as "border"); hook2 "Same marble,
  same slope. Flat board or two rails: which one gets down first?" ok,
  the question from 2.8 s of voice (3.4 s of video); hook3 "Which one
  gets down first, a marble on a flat board or on two rails?" FAILED
  ("on" as "and", "board or" as "border"); hook4 "Flat board or two
  rails: which marble gets down first? Same marble, same slope." ok at
  0.6 s; hook5 "Two rails or a flat board: which one gets down first?
  Same marble, same slope." ok twice, the question at 0.60 s of video;
  hook6 "A flat board, or two rails: ..." ok twice; hook7 "On two rails
  or on a flat board: ..." ok twice. Chosen: hook5 (question first, no
  "board or", lands at 0.60 s). Word test (words.txt, 33 s) passed on
  the first take: "rails", "rail marble", "marble", "flat board",
  "slope", "twenty degrees", "zero point nine one seconds", "one point
  one two", "smaller radius", "for every centimeter it rolls", "half of
  the energy", "gets ahead", "a third of the way up", "Every run the
  same", "four times slower", "Thirty four centimeters short", "Watch
  the spin", "On top, the marble rides on two rails", "Below, it rolls
  on a flat board".
- Narration: projects/rails/narration.txt, 121 words; the question is
  the first sentence (spoken 0.60-3.85 s of video) and is repeated word
  for word before the payoff ("So, two rails or a flat board: which one
  gets down first?"); the payoff answers in the same words ("The flat
  board, in zero point nine one seconds. The rails take one point one
  two."). One setup number (twenty degrees, plus the 1/4 speed note),
  two payoff numbers (the two panel times).
- Voice: pass 1 ok on the first take (media/rails/voice.log: "ok:
  transcript matches narration (36.490159s)"); no mishearing. Timing
  (media/rails/timing.log, offset 0.6): question 0.60-3.85 (whisper
  splits it at the colon); "same marble, same slope, 20 degrees" to
  6.47; "Shown four times slower" 6.47-8.05; "On top. The marble rides
  on two rails" 8.05-10.65 (release at 7.50); "Below, it rolls on a flat
  board. Watch the spin." 10.65-13.97 (flat landing 11.15, rails 11.99);
  mechanism 13.97-22.48 (release 15.50, landings 19.15 and 19.99); "The
  board marble gets ahead" 22.48-24.24 (release 23.50); "and is down
  while the other one is still a third of the way up" 24.24-27.17 (flat
  landing 27.15); "every run the same. So, two rails or a flat board,"
  27.17-30.48 (rails landing 27.99); "which one gets down first, the
  flat board," 30.48-33.08 (release 31.50); "In 0.91 seconds, the rails
  take 1.12." 33.08-37.09 (card from 33.6, flat landing 35.15, rails
  landing 35.99). Voice 36.49 s, ends at 37.09 s of video. 13 silences
  at -35 dB / 0.22 s (media/rails/silences.log).
- Compose: media/rails/compose.log: music seed 116, 40.00 s; captions 20
  pauses detected, 20 matched, max chunk start shift 1.734 s against
  word-count timing (no fallback); final.mp4 40.000000 s.
- Text widths (measure.log): overlay 789, title rows 773 and 848, legend
  824, labels 265 / 332, readouts at most 390, event rows 484 / 607,
  mark 161, inset labels at most 121, payoff lines 606 / 915 / 869 / 826
  / 897 / 884 px; all under 950 px, asserted.

### Local QA

- media/rails/final.mp4: md5 62a641920f2bf373aa68ada01da8e733, 4205360
  bytes; ffprobe h264 1080x1920 60/1, aac 22050 Hz mono, duration
  40.000000; atoms ftyp@0 moov@32 free@44852 mdat@44860 (faststart).
- Caption text against the narration: 35 drawtext chunks (the first is
  the overlay); the joined caption text equals narration.txt word for
  word (checked by script after undoing the drawtext escapes). The first
  caption "Two rails or a flat" is enabled from 0.600 s, "board: which
  one" 1.796-2.950, "gets down first?" 2.950-3.850.
- signalstats YMAX on footage.mp4: caption band rows 1440-1530 = 28
  (background), overlay band rows 96-130 = 28: nothing drawn under the
  captions or the overlay.
- Full-resolution frames viewed (media/rails/qa-T.png): 0.00 overlay,
  two-row title "Two rails or a flat board: / which one gets down
  first?", both marbles just released near the top (0.01 / 0.02 m), the
  insets, no caption; 1.00 caption "Two rails or a flat", marbles at 0.11
  / 0.17 m; 2.10 "board: which one", marbles at 0.34 / 0.51 m, the flat
  one visibly ahead; 18.40 legend and clock 0.725 s, rails 0.42 m, flat
  0.63 m, caption "for every centimeter"; 27.10 clock 0.900 s, rails
  0.64 m, flat 0.97 m about to touch the pad, caption "of the way up.";
  34.00 the card rising (dim gold), caption "zero point nine one",
  marbles at 0.31 / 0.47 m; 35.40 the flat marble at the pad with "flat
  board: down in 0.914 s", the gold "34 cm short" mark in the rails band
  with the rail marble at 0.76 m, caption "The rails take one", card
  up; 36.20 both at the pad, both event rows, caption "point one two.",
  card; 39.983 identical to frame 0 (title back, no caption, no card).
  media/rails/sheet.png viewed: 40 cells, the captions in order, the
  card from 33.6 s, no clipping, the loop closes.
- Question timing: on screen from frame 0 (title) and spoken from 0.60
  s (first caption enable 0.600 s).
- Narrated numbers: "twenty degrees" (manifest slope_deg 20, log "20
  degrees"), "four times slower" (1/4 speed), "zero point nine one
  seconds" (log 0.913661 s = 0.9137 s), "one point one two" (log
  1.121958 s = 1.1220 s). Description and title numbers checked by
  script against measure.log (75 distinct numbers, none missing).

### Metadata

projects/rails/metadata.json written by a Python script with asserts
(title 91 chars, description 3040 chars, 11 tags, ASCII, no < or >;
every number in the title and description present in measure.log);
ls -l confirmed the file (3615 bytes). Title: "Two rails or a flat
board: which one gets down first? The flat board, 0.91 s against 1.12
s". privacyStatus private, categoryId 27, containsSyntheticMedia true,
selfDeclaredMadeForKids false.

### Deviations from the brief

- Question wording: "Two rails or a flat board: which one gets down
  first?" instead of "Flat board or two rails: which one gets down
  first?": whisper heard "board or" as "border" on two of four takes,
  while the rails-first form passed twice (and the order matches the
  bands, rails on top). Identical in the title, the hook and the payoff.
- The narration is 121 words (36.49 s), above the 104-110 target; the
  pace puts every beat under its event (the payoff times under the
  landings at 35.15 and 35.99 s) and the voice ends at 37.09 s.
- Readouts: the shared clock sits at y 290 (deskchain style) and the
  left column's second readout is the fixed contact line ("touches at
  0.6 R = 6 mm") instead of a second clock.
- Event rows at 172 px under the band top, right-aligned (cartramp
  style) rather than under the slope, so the gold mark and the inset
  stay clear.
- Card line 3 "34 cm short when the board one lands" (the longer form
  measured 1129 px); line 6 "any size, any slope: 1.228 times longer".
- The drawn marble (22 px) rolls without slipping at its drawn size, so
  its stripe turns 4.4 and 7.4 times over the metre instead of the
  model's 15.9 and 26.5 (which would alias at 60 fps); the spin readout
  carries the model's numbers; stated in measure.log.
- The rails band has a thin base under the rails (6 px) instead of the
  flat band's 14 px board, so the two cases read differently at a
  glance.

## Niche note

Appended to the "Marble on rails (Galileo's groove)" bullet in
docs/niche.md: [produced 2026-10-06 as "Two rails or a flat board: which
one gets down first? The flat board, 0.91 s against 1.12 s"; measured
flat board 1 m in 0.9137 s at 2.1890 m/s (a 2.3959 m/s^2), two rails 1.6
R apart (contact 0.6 R) 1.1220 s at 1.7826 m/s (a 1.5888 m/s^2), ratio
1.2280 = sqrt 1.5079, margin 0.2083 s, the rail marble 0.6632 m down
(33.7 cm short) when the flat one lands, spin 34.8 against 47.3 turns/s,
spin share 0.2857 against 0.5263, grip 0.1040 and 0.1149, rails 1.2 R
0.9843 s and 1.8 R 1.3607 s, 10 deg 1.2823 / 1.5746 s, 30 deg 0.7557 /
0.9279 s, ice cube 0.7722 s, Galileo contact 0.9052 R (5.93 percent
less); RK4 dt 1e-4 s against the closed forms, 44 checks, 0 failed; task
20261006-101403]

## Upload

- Attempt 2 of 5 (quota day 2026-10-06T10:00 EEST) recorded at 2026-10-06T10:45:47+03:00 before scripts/yt-upload.py rails; one earlier attempt (pushpull, succeeded).
- Uploaded private as fbCfcgjoWWI at 2026-10-06T10:45:50Z (videos.insert 1,600 units). yt-qa.py --wait --publish: gate 15 of 15 on the first processed read, published at 2026-10-06T10:46:48+03:00, re-read public, 55 units. https://youtu.be/fbCfcgjoWWI
