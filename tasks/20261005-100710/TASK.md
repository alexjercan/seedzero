# Produce short: spinning glass, 4 cm or 6 cm of water, which comes first, a dry bottom or a spill

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day37

## Goal

Backlog idea (trend research 2026-10-04, task 20261004-101250, pillar 2
chaos and physics, everyday mechanics; read the full entry under "Added
by trend research 2026-10-04" in docs/niche.md): "Spinning glass, 4 cm or
6 cm: a 7 cm glass 10 cm tall with 4 cm of water beside the same glass
with 6 cm, both spun up slowly on a turntable; measure which happens
first, the bottom showing or the water spilling; expect the 4 cm glass
to show a dry spot at 341.8 rpm (the rim then at 8.0 cm) and spill at
427.2 rpm, and the 6 cm glass to spill at the same 341.8 rpm (centre then
at 2.0 cm) and show its bottom only at 418.6 rpm; the two events swap
sides at half full, where both come at once at 382.1 rpm (the paraboloid
depth w^2 R^2 / (4 g) equals the fill; dry radius and rim height closed
form, volume check to 1e-6 L); the water takes about 8 s to catch up
with the glass at 342 rpm (Ekman spin-up), so ramp over 30 s or more and
narrate the rpm, not the time; a fluid, but rigid rotation closed form,
no grid; rank it low; deterministic, no seed."

Orchestrator notes (2026-10-05, before this brief; closed forms in
/tmp/day37/closed.py with the log in /tmp/day37/closed.log, g = 9.807).
The model: a straight-sided glass, inner radius R = 3.5 cm, height H =
10 cm, on a turntable; the water turns with the glass as one body (rigid
rotation, the quasi-steady state after spin-up; say so, and say that
real water lags a glass that is spun up quickly, which is why the ramp
is slow); its surface is the paraboloid z(r) = z0 + w^2 r^2 / (2 g),
with the depth from rim to centre d = w^2 R^2 / (2 g) and, while the
bottom is covered and nothing has spilled, the mean level equal to the
fill h: centre z0 = h - w^2 R^2 / (4 g), rim z(R) = h + w^2 R^2 / (4 g).
Top band: 4 cm of water (153.9 mL). Bottom band: 6 cm (230.9 mL). Both
glasses are spun up on the same ramp: 0 rpm until 3.0 s of video, then
linearly to 450 rpm at 33.0 s (15 rpm per second), held at 450 until the
end; narrate the rpm, not the time. Events on the ramp: the 4 cm glass
bares its bottom (centre reaches 0) at w = sqrt(4 g h) / R = 35.790 rad/s
= 341.8 rpm with its rim at 8.0 cm, well inside the glass; from then its
water is a ring and the dry disc grows (surface z = (w^2 / (2 g)) (r^2 -
r0^2) with r0 set by the volume pi w^2 (R^2 - r0^2)^2 / (4 g) = V); it
spills only at 427.2 rpm (rim at 10 cm, dry radius then 1.57 cm). The 6
cm glass spills first, at the same 341.8 rpm (rim reaches 10 cm, centre
then at 2.0 cm), and from then its rim stays at 10 cm while the water
leaves (z0 = H - w^2 R^2 / (2 g), volume shrinks); its bottom bares at w
= sqrt(2 g H) / R = 40.014 rad/s = 382.1 rpm, when 192.4 mL of its 230.9
mL remain (the paraboloid then holds exactly half the glass), NOT at the
research entry's 418.6 rpm (that figure ignored the spilled water; print
both and say which is right in the evidence and in the niche note). Half
full (5 cm) is the swap: both events at once at 382.1 rpm. Compute every
state by closed form each frame (no integration needed) and check: the
volume under the surface by numerical quadrature to 1e-6 L against the
fill before any spill; the dry-ring volume formula against the same
quadrature; the spill volume history for the 6 cm glass (monotone, 38.5
mL lost by 382.1 rpm); the event rpms against the closed forms; the
schedule in video time (341.8 rpm at 25.79 s, 382.1 at 28.47 s, 427.2 at
31.48 s with the ramp above; print the exact figures).

Checks, not facts (the sim must print and compare; state them as checks):
4 cm: bottom dry at 341.8 rpm (35.790 rad/s), rim then 8.0 cm; spill at
427.2 rpm with dry radius 1.57 cm; 6 cm: spill at 341.8 rpm, centre then
2.0 cm; bottom dry at 382.1 rpm (40.014 rad/s) with 192.4 of 230.9 mL
left (38.5 mL spilled); 5 cm: both at 382.1 rpm; the no-spill figure
418.6 rpm for a 6 cm fill printed as the wrong guess; volumes 153.9 and
230.9 mL; quadrature within 1e-6 L; rim and centre heights at 100, 200,
300, 400 and 450 rpm for both glasses (table); for the description: a
wider 9 cm glass (R 4.5 cm) with 4 cm: bottom dry at 265.8 rpm; a 2 cm
fill: dry at 241.7 rpm and spill at 604.1 rpm (print exact); print the
text widths and the layout clearances.

Drawing: two-band layout (sims/deskchain style), side view cross-section,
the 4 cm glass on top (the "bottom shows first" case) and the 6 cm glass
below; same scale, same ramp, same rpm readout. Scale 36 px per cm: the
glass 252 px wide (inner) and 360 px tall with 8 px walls, standing on a
turntable platter (a flat slab with a short spindle below; a small
top-view dial beside the glass showing a spinning mark whose angle
advances with the integrated rpm, so the speed reads; blur the mark to a
ring above about two turns per video second as sims/yoyo did for the
spin); the water drawn as the filled region between the glass floor (or
the dry disc) and the paraboloid surface, computed at 2x and reduced;
when the bottom bares, draw the dry disc in the floor colour and the
water as two side lobes meeting the walls; when the water spills, draw
thin teal streaks down the outside of the walls and a small puddle on the
platter, and drop the volume readout; a dashed gold line at the rim
height and a dashed line at the fill height (the still level). Label rows
(40 px, coloured): "4 cm of water" (teal) and "6 cm of water" (coral).
Readouts (28 px): left column "NNN turns a minute" (shared ramp) and
"center N.N cm" ; right column "rim N.N cm" and "water NNN mL". Gold
event rows: top "4 cm: bottom shows at 342 rpm, rim 8 cm, no spill" (lit
at the event and held; a second row "spills at 427 rpm" may light
later), bottom "6 cm: spills at 342 rpm, center 2 cm" (lit and held; a
second row "bottom shows at 382 rpm, 38 mL gone" lights later). Single
run: ramp as above, hold at 450 rpm, and fade back to the first frame
over the last loop_fade seconds; the last frame equal to the first. The
legend row after the title: "same glass, same spin-up, 15 rpm a second";
the shared readout is the rpm. Overlay: "7 cm glass, 10 cm tall | 4 cm
vs 6 cm of water | no seed" (measure it; shorten if over 950 px).

Day thirty-seven, second slot. Chosen because "which happens first"
with two panels that end differently is the winning format (ice cube
against ball 973, cue ball 957, bucket over your head 940, which is a
spinning-water sibling), the panels end visibly differently (a dry disc
in one glass, water running down the other), the threshold is exact and
plain (half full is the swap, both at 342 turns a minute), and the
research run kept it as a rigid-rotation closed form. Question in the
first two seconds: "A glass of water on a turntable. Does the bottom
show before it spills?" or "Spin up a glass of water. Which comes first,
a dry bottom or a spill?" (never start the narration with "Spin": the
onset clips; pre-test the variants and keep the question identical in
the title, the hook and the payoff). Setup number: four centimeters of
water against six (two panels, so "four centimeters" and "six
centimeters" may both be spoken; "a ten centimeter glass" goes to the
overlay). Payoff: with four centimeters the bottom shows first, at three
hundred forty two turns a minute; with six it spills first, at the same
three hundred forty two; the rule: under half full the bottom shows
first, over half full it spills first (speak at most two numbers in the
payoff beat; "three hundred forty two turns a minute" and "half full"
are the preferred pair; "eight centimeters" and "two centimeters" go to
the card). The mechanism sentence must follow the picture: the spin
throws the water outward and up the wall, and the surface dips in the
middle as much as it climbs at the rim; four centimeters of dip empties
the centre of the shallow glass, while the deep glass is already at the
rim ("paraboloid" and "centrifugal" stay out of the narration). Whisper
risks: "rpm" (say "turns a minute"), "spills" and "spill" (pre-test),
"spin up" and "spun" (pre-test), "turntable" (pre-test), "half full"
(pre-test), "three hundred forty two" (pre-test), "dry" (pre-test),
"centimeters" (passed before), avoid "do you", avoid "fly", avoid "pull"
as a noun. Pre-test hooks with scripts/voiceover.sh and keep the one
whose question lands earliest under two seconds. Measure every fixed
text line with PIL before rendering and keep every line under 950 px,
and the title under 100 characters with no < or >. Music seed 113.
Templates: sims/deskchain (two-band layout, asserts, the clock, the
fade; read it whole), sims/bucket (water drawn in a container, a spin
readout), sims/coinrecord (a turntable at a stated rpm), sims/torricelli
(water levels and jets drawn at 2x). Sim name spinglass:
sims/spinglass/spinglass.py, projects/spinglass/, media/spinglass/.

## Claim (expected; the sim's numbers replace these)

A 7 cm glass, 10 cm tall, spun up slowly on a turntable with the water
turning as one body: with 4 cm of water the bottom shows first, at 342
turns a minute, with the rim then at 8 cm and nothing spilled (it spills
only at 427); with 6 cm of water it spills first, at the same 342 turns
a minute, with the centre still 2 cm deep (its bottom shows at 382, after
38 mL has gone); the swap is at half full, where both happen at once at
382 turns a minute. Narrated: four centimeters against six (setup); with
four the bottom shows first, with six it spills first, both at three
hundred forty two turns a minute; under half full the bottom shows
first, over half full it spills first (payoff). Card: the question; the
answer with 342 rpm both ways; 4 cm: rim 8 cm, spills at 427; 6 cm:
centre 2 cm, bottom at 382 after 38 mL spilled; half full: both at 382;
the dip equals the climb. Description: the model statement, the
paraboloid, the two runs, the fill and glass variants, the spin-up
caveat, the checks.

## Claim

A 7 cm glass, 10 cm tall, spun up slowly on a turntable with the water
turning as one body: with 4 cm of water the bottom shows first, at 341.8
turns a minute (35.790 rad/s), with the rim then at 8.0 cm and nothing
spilled; it spills only at 427.2 rpm (dry radius then 1.57 cm). With 6 cm
of water it spills first, at the same 341.8 rpm, with the centre still
2.0 cm deep; its bottom shows at 382.1 rpm (40.014 rad/s), after 38.5 mL
of its 230.9 mL has gone and 192.4 mL (exactly half the glass) remains.
Half full is the swap: both at once at 382.1 rpm. Under half full the
bottom shows first, over half full it spills first. Narrated: "four
centimeters of water on top, six below" (setup); "the shallow glass: the
dry bottom, at three hundred forty two turns a minute; the deep glass:
the spill, at the same speed; under half full, the bottom shows first;
over half full, it spills first" (payoff). The research entry's 418.6
rpm for the 6 cm bottom is wrong: it ignores the spilled water.

## Evidence

### Measurements

`nix develop -c python3 sims/spinglass/spinglass.py projects/spinglass/manifest.json --measure-only`,
logged to media/spinglass/measure.log (exit 0, 10:20:56 to 10:20:57):

```
Mon Oct  5 10:20:56 AM EEST 2026
warning: Git tree '/home/alex/personal/seedzero' is dirty
setup: the same glass in both panels, seen from the side as a cross-section: a straight-sided glass of inner radius R = 3.5 cm (7 cm across) and height H = 10 cm on a turntable platter; top panel 4 cm of water (153.9 mL), bottom panel 6 cm (230.9 mL); both spun up on the same ramp: 0 rpm until 3 s of video, then 15 rpm per second to 450 rpm at 33 s (47.124 rad/s), held to the end at 40 s; the water turns with the glass as one body (rigid rotation, the quasi-steady state after spin-up; real water lags a glass that is spun up quickly, which is why the ramp is slow); its surface is the paraboloid z = z0 + w^2 r^2 / (2 g) with the depth rim to centre d = w^2 R^2 / (2 g); while the bottom is covered and nothing has spilled the mean level is the fill: centre z0 = h - w^2 R^2 / (4 g), rim h + w^2 R^2 / (4 g); past the dry point the water is a ring r0 to R with z = (w^2 / (2 g)) (r^2 - r0^2) and volume pi w^2 (R^2 - r0^2)^2 / (4 g); past the spill point the rim stays at H and the volume shrinks to the capacity pi R^2 (H - d / 2) while d <= H, then pi g H^2 / w^2; the ramp is monotone, so the water at w is min(fill, capacity(w)) and every state is a closed form of w alone, nothing integrated; g = 9.807 m/s^2; drawn at 36 px per cm (the glass 252 px wide inside and 360 px tall); deterministic, no seed
4 cm of water (top panel, 153.9 mL): the bottom shows first: the centre reaches 0 at w = 35.790 rad/s = 341.8 rpm = 342 rpm (closed form sqrt(4 g h) / R = 35.790 rad/s = 341.8 rpm, diff +7.1e-15), the rim then at 8.0 cm = 8 cm (2 h; the dip of 4.0 cm equals the climb of 4.0 cm), water 153.9 mL, nothing spilled; from then the water is a ring and the dry disc grows; the rim reaches H only at w = 44.737 rad/s = 427.2 rpm = 427 rpm (closed form (H / R) sqrt(g / h) = 44.737 rad/s = 427.2 rpm, diff +1.5e-10) with the dry radius 1.57 cm = 1.6 cm of 3.5 (dry disc 3.1 cm across), the water still 153.9 mL; at 450 rpm 138.7 mL remain, 15.2 mL spilled, dry radius 1.85 cm
6 cm of water (bottom panel, 230.9 mL): it spills first: the rim reaches H at w = 35.790 rad/s = 341.8 rpm = 342 rpm (closed form sqrt(4 g (H - h)) / R = 35.790 rad/s = 341.8 rpm, diff +1.2e-10), the centre then at 2.0 cm = 2 cm (2 h - H; the climb of 4.0 cm equals the dip of 4.0 cm), water 230.9 mL; from then the rim stays at H and the water leaves; the bottom shows at w = 40.014 rad/s = 382.1 rpm = 382 rpm (closed form sqrt(2 g H) / R = 40.014 rad/s = 382.1 rpm, diff +0.0e+00), when 192.4 mL of 230.9 mL remain (exactly half the glass, pi R^2 H / 2 = 192.4 mL) and 38.5 mL = 38 mL have spilled; at 450 rpm 138.7 mL remain, 92.2 mL spilled, dry radius 1.85 cm
wrong guess: sqrt(4 g h) / R with h = 6 cm gives 43.833 rad/s = 418.6 rpm for the bottom to show, the figure in the research entry; it ignores the spilled water (it would put the rim at 12.0 cm, above the 10 cm glass); with the spill the 6 cm glass has only 160.4 mL left at 418.6 rpm and its bottom has been dry since 382.1 rpm, so 382.1 rpm is right and 418.6 rpm is wrong
half full (5 cm, 192.4 mL): the swap; the bottom shows at 40.014 rad/s = 382.1 rpm and the rim reaches H at 40.014 rad/s = 382.1 rpm, both at once (closed forms 40.014 and 40.014 rad/s, diffs +0.0e+00 and +1.0e-10; the paraboloid depth w^2 R^2 / (2 g) = H = 10 cm exactly); under half full the bottom shows first, over half full it spills first
spill history (the water at each speed, 4501 samples at 0.1 rpm from 0 to 450 rpm, monotone non-increasing in both glasses): 300 rpm: 6 cm 230.9 mL (0.0 gone), 4 cm 153.9 mL (0.0 gone); 341.8 rpm: 6 cm 230.9 mL (0.0 gone), 4 cm 153.9 mL (0.0 gone); 350 rpm: 6 cm 223.4 mL (7.5 gone), 4 cm 153.9 mL (0.0 gone); 360 rpm: 6 cm 214.0 mL (16.9 gone), 4 cm 153.9 mL (0.0 gone); 370 rpm: 6 cm 204.4 mL (26.5 gone), 4 cm 153.9 mL (0.0 gone); 382.1 rpm: 6 cm 192.4 mL (38.5 gone), 4 cm 153.9 mL (0.0 gone); 400 rpm: 6 cm 175.6 mL (55.3 gone), 4 cm 153.9 mL (0.0 gone); 418.6 rpm: 6 cm 160.3 mL (70.6 gone), 4 cm 153.9 mL (0.0 gone); 427.2 rpm: 6 cm 153.9 mL (77.0 gone), 4 cm 153.9 mL (0.0 gone); 450 rpm: 6 cm 138.7 mL (92.2 gone), 4 cm 138.7 mL (15.2 gone); the 6 cm glass has lost 38.5 mL by 382.1 rpm; above 427.2 rpm both glasses hold the same water, pi g H^2 / w^2, 138.7 mL each at 450 rpm
quadrature: Simpson's rule with 2000 intervals on 2 pi r z(r) over the wet radii against the closed-form volume (the fill before any spill, the ring formula past the dry point, the capacity past the spill point): worst 2.71e-14 mL = 2.71e-17 L, within 1e-6 L; shallow 0 rpm 153.938040 mL vs 153.938040 (+2.7e-14); deep 0 rpm 230.907060 mL vs 230.907060 (+0.0e+00); shallow 100 rpm 153.938040 mL vs 153.938040 (+2.7e-14); deep 100 rpm 230.907060 mL vs 230.907060 (+0.0e+00); shallow 200 rpm 153.938040 mL vs 153.938040 (+0.0e+00); deep 200 rpm 230.907060 mL vs 230.907060 (+0.0e+00); shallow 300 rpm 153.938040 mL vs 153.938040 (+0.0e+00); deep 300 rpm 230.907060 mL vs 230.907060 (+0.0e+00); shallow 341.8 rpm 153.938040 mL vs 153.938040 (+2.7e-14); deep 341.8 rpm 230.878246 mL vs 230.878246 (+0.0e+00); shallow 382.1 rpm 153.938040 mL vs 153.938040 (+0.0e+00); deep 382.1 rpm 192.430867 mL vs 192.430867 (+0.0e+00); shallow 400 rpm 153.938040 mL vs 153.938040 (+0.0e+00); deep 400 rpm 175.593659 mL vs 175.593659 (-2.7e-14); shallow 427.2 rpm 153.938040 mL vs 153.938040 (+0.0e+00); deep 427.2 rpm 153.945261 mL vs 153.945261 (+2.7e-14); shallow 450 rpm 138.740669 mL vs 138.740669 (+0.0e+00); deep 450 rpm 138.740669 mL vs 138.740669 (+0.0e+00)
table (rim and centre heights): 100 rpm (10.472 rad/s, depth 0.7 cm): 4 cm: centre 3.7 cm, rim 4.3 cm, water 153.9 mL; 6 cm: centre 5.7 cm, rim 6.3 cm, water 230.9 mL | 200 rpm (20.944 rad/s, depth 2.7 cm): 4 cm: centre 2.6 cm, rim 5.4 cm, water 153.9 mL; 6 cm: centre 4.6 cm, rim 7.4 cm, water 230.9 mL | 300 rpm (31.416 rad/s, depth 6.2 cm): 4 cm: centre 0.9 cm, rim 7.1 cm, water 153.9 mL; 6 cm: centre 2.9 cm, rim 9.1 cm, water 230.9 mL | 400 rpm (41.888 rad/s, depth 11.0 cm): 4 cm: centre 0.0 cm, rim 9.4 cm, dry radius 1.34 cm, water 153.9 mL; 6 cm: centre 0.0 cm, rim 10.0 cm, dry radius 1.04 cm, water 175.6 mL | 450 rpm (47.124 rad/s, depth 13.9 cm): 4 cm: centre 0.0 cm, rim 10.0 cm, dry radius 1.85 cm, water 138.7 mL; 6 cm: centre 0.0 cm, rim 10.0 cm, dry radius 1.85 cm, water 138.7 mL
for the description: a wider glass, R = 4.5 cm (9 cm across), with 4 cm: bottom dry at 27.837 rad/s = 265.8 rpm (rim then 8.0 cm), spills at 332.3 rpm; the 3.5 cm glass with 2 cm (77.0 mL): dry at 25.307 rad/s = 241.7 rpm (rim then 4.0 cm), spills at 63.268 rad/s = 604.2 rpm; the dry speed scales as sqrt(h) / R and the spill speed of an under-half fill as 1 / (R sqrt(h)); spin-up note (not drawn): water spun up suddenly takes about h / sqrt(nu w) to catch up with the glass (Ekman spin-up, nu = 1e-06 m^2/s): 6.7 s for 4 cm and 10.0 s for 6 cm at 341.8 rpm, so the ramp of 30 s at 15 rpm per second is slow against it and the rigid-rotation surface is the quasi-steady state
brief checks (19 of 21 agree at the brief's precision, 21 of 21 within one unit of its last digit): 4 cm bottom dry (rpm): brief 341.8, sim 341.77 (ok); 4 cm bottom dry (rad/s): brief 35.79, sim 35.7899 (ok); 4 cm rim then (cm): brief 8, sim 8.00 (ok); 4 cm spill (rpm): brief 427.2, sim 427.21 (ok); 4 cm dry radius at the spill (cm): brief 1.57, sim 1.565 (ok); 6 cm spill (rpm): brief 341.8, sim 341.77 (ok); 6 cm centre then (cm): brief 2, sim 2.00 (ok); 6 cm bottom dry (rpm): brief 382.1, sim 382.11 (ok); 6 cm bottom dry (rad/s): brief 40.014, sim 40.0143 (ok); 6 cm left then (mL): brief 192.4, sim 192.42 (ok); 6 cm spilled then (mL): brief 38.5, sim 38.48 (ok); 5 cm both (rpm): brief 382.1, sim 382.11 (ok); 6 cm no-spill wrong guess (rpm): brief 418.6, sim 418.58 (ok); 4 cm volume (mL): brief 153.9, sim 153.94 (ok); 6 cm volume (mL): brief 230.9, sim 230.91 (ok); 9 cm glass, 4 cm: dry (rpm): brief 265.8, sim 265.82 (ok); 2 cm fill: dry (rpm): brief 241.7, sim 241.67 (ok); 2 cm fill: spill (rpm): brief 604.1, sim 604.17 (ok within one unit of the brief's last digit); 341.8 rpm at (s): brief 25.79, sim 25.785 (ok within one unit of the brief's last digit); 382.1 rpm at (s): brief 28.47, sim 28.474 (ok); 427.2 rpm at (s): brief 31.48, sim 31.481 (ok)
schedule (video time, real time): both glasses at rest until 3 s, then 15 rpm per second; 100 rpm at 9.67 s and 140 rpm at 12.33 s (the dial's mark blurs to a ring between them, 1.67 to 2.33 turns per second of video); the 4 cm glass bares its bottom and the 6 cm glass reaches its rim at 341.8 rpm at 25.78 s (both first event rows light); the 6 cm glass bares its bottom at 382.1 rpm at 28.47 s (its second row lights); the 4 cm glass reaches its rim at 427.2 rpm at 31.48 s (its second row lights); the ramp reaches 450 rpm at 33 s and holds (the streaks stop, the puddles stay); the platter turns 165.00 turns in all (112.50 on the ramp); on the first frame both glasses are at rest with their still levels; title until 3 s; payoff card from 23.6 s; single run: over the last 0.5 s the scene crossfades back to the first frame (the readouts and the card out over its first half, the title in over its second) and the last frame repeats the first
text widths (the on-screen strings verbatim): overlay@34 942 px '7 cm glass, 10 cm tall | 4 vs 6 cm water | no seed', title line 1@56 817 px 'A glass of water, spun up.', title line 2@56 585 px 'Which comes first,', title line 3@56 621 px 'dry bottom or spill?', legend@40 933 px 'same glass, same ramp, 15 rpm a second', clock rest@28 105 px 'at rest', clock ramp@28 507 px 'spinning up, 255 turns a minute', clock held@28 422 px 'held at 450 turns a minute', label shallow@40 310 px '4 cm of water', event shallow row 1@40 865 px 'bottom shows at 342 rpm, rim at 8 cm', event shallow row 2@40 379 px 'spills at 427 rpm', label deep@40 310 px '6 cm of water', event deep row 1@40 674 px 'spills at 342 rpm, center 2 cm', event deep row 2@40 871 px 'bottom shows at 382 rpm, 38 mL gone', rpm row@28 301 px '450 turns a minute', centre row@28 217 px 'center 2.9 cm', centre dry row@28 164 px 'center dry', rim row@28 167 px 'rim 9.1 cm', water row@28 216 px 'water 231 mL', dial tag@24 116 px 'top view', rim tag@24 134 px 'rim 10 cm', fill tag shallow@24 123 px 'still 4 cm', fill tag deep@24 123 px 'still 6 cm', payoff line 1@40 868 px 'which comes first, dry bottom or spill?', payoff line 2@40 942 px '4 cm: bottom shows at 342 rpm, rim 8 cm', payoff line 3@40 811 px '6 cm: spills at 342 rpm, center 2 cm', payoff line 4@40 934 px 'then 4 cm spills at 427, 6 cm dries at 382', payoff line 5@40 765 px 'half full: both at once, at 382 rpm', payoff line 6@40 784 px 'the dip equals the climb at the rim'
row check: the left column ends at x 350 px and the right column starts at x 824 px; the rows end 134 px under the band top; the glass spans x 406 to 674 px (inner 414 to 666) from its rim at 62 px under the band top to its floor at 422, the floor plate to 430, the platter (x 330 to 750) to 446 and the spindle to 456; the puddles reach x 266 and 814 at most on the platter top; the rim and fill tags sit right of the glass to x 818; the dial is centred at x 930, 300 px under the band top with radius 58 (y 242 to 388 with its tag, x 872 to 988); the event rows are centred 482 and 526 px under the band top (from 460 to 548) and span x 105 to 975 px (widest 871 px); the surface never rises above the rim (asserted in every state); each band is 550 px tall (y 330 to 880 and 880 to 1430); the caption band starts at y 1440; the title rows end at y 330 and the overlay band ends at y 130
exit 0
Mon Oct  5 10:20:57 AM EEST 2026
```

Brief checks, each against the sim's print:

- 4 cm bottom dry: brief 341.8 rpm (35.790 rad/s), sim 341.77 rpm
  (35.7899 rad/s): ok. Rim then 8.0 cm: ok. Nothing spilled: ok.
- 4 cm spill: brief 427.2 rpm, dry radius 1.57 cm; sim 427.21 rpm,
  1.565 cm: ok.
- 6 cm spill: brief 341.8 rpm, centre 2.0 cm; sim 341.77 rpm, 2.00 cm: ok.
- 6 cm bottom dry: brief 382.1 rpm (40.014 rad/s) with 192.4 of 230.9
  mL left (38.5 mL spilled); sim 382.11 rpm (40.0143 rad/s), 192.42 mL
  left, 38.48 mL spilled: ok. The sim prints the no-spill guess
  sqrt(4 g h) / R = 43.833 rad/s = 418.6 rpm as the wrong figure: it
  would put the rim at 12.0 cm in a 10 cm glass; with the spill the
  glass holds 160.4 mL at 418.6 rpm and its bottom has been dry since
  382.1 rpm. 382.1 rpm is right, 418.6 rpm is wrong.
- 5 cm: both events at 382.1 rpm (closed forms 40.014 and 40.014 rad/s,
  diffs 0 and 1.0e-10): ok.
- Volumes 153.9 and 230.9 mL: sim 153.94 and 230.91: ok.
- Quadrature: Simpson, 2000 intervals, worst 2.71e-14 mL against the
  closed-form volume at 18 (glass, rpm) states including the ring and
  the spilled states: within 1e-6 L: ok.
- Spill history: 4501 samples at 0.1 rpm, monotone non-increasing in
  both glasses; the 6 cm glass has lost 38.5 mL by 382.1 rpm: ok.
- Event rpms by bisection on the state against the closed forms: diffs
  at most 1.5e-10 rad/s: ok.
- Heights table at 100, 200, 300, 400, 450 rpm for both glasses:
  printed (see the log).
- Description variants: 9 cm glass (R 4.5 cm) with 4 cm dry at 265.8 rpm
  (brief 265.8): ok; 2 cm fill dry at 241.7 rpm (brief 241.7): ok;
  spill at 604.17 rpm (brief 604.1): within one unit of the brief's
  last digit, the exact figure is 604.2 (63.268 rad/s).
- Schedule: 341.8 rpm at 25.785 s (brief 25.79; within one unit of the
  last digit, the exact figure is 25.78 s), 382.1 at 28.474 s (brief
  28.47): ok, 427.2 at 31.481 s (brief 31.48): ok.
- Text widths and layout clearances: printed; every line under 950 px
  (widest the overlay and payoff line 2 at 942 px); the row check
  asserts the column, glass, platter, dial and event-row clearances.
- Brief checks: 19 of 21 agree at the brief's precision, 21 of 21
  within one unit of the brief's last digit.

### Production

- sims/spinglass/spinglass.py (closed forms of w for every state, no
  integration; bisection and Simpson quadrature as checks; two-band
  deskchain layout; 2x water layers; dial with a ring blur between 100
  and 140 rpm; streaks and puddles when spilling; single run with a
  0.5 s crossfade back to frame 0). projects/spinglass/manifest.json
  (seed 0, fps 60, g 9.807, R 0.035 m, H 0.10 m, fills 0.04 and 0.06 m,
  ramp 3.0 s start, 15 rpm/s, 450 rpm, music seed 113).
- Smoke frames viewed before the render: media/spinglass/smoke-*.png
  at 0.0, 1.5, 2.0, 2.9, 3.5, 10.0, 20.0, 25.7, 26.2, 28.5, 29.5, 31.6,
  33.5, 39.5, 39.8 and 39.983 s (rest, title, ramp start, ring blur,
  paraboloids, the dry disc lobes, streaks and puddles, the card, the
  fade blend, the last frame).
- Render: media/spinglass/render.log (10:20:57 to 10:21:24, exit 0).
  Loop check 0 px; fade check 246339 px at 39.500 s, 132752 px at
  39.750 s, 0 px at 39.967 s (max channel diff 14); loop step 0 px;
  footage 40.00 s at 60 fps.
- Hook pre-tests (media/spinglass/hooks/pretest.log): hook1 "Which comes
  first, dry bottom or spill? A glass of water, spun up slowly." ok
  (5.00 s); hook2, hook3 (turntable), hook4 ("a dry bottom or a spill")
  and hook5 all ok. hook1 kept: the question is the first words, so it
  lands at 0.60 s of video. Risk words: "spills", "spill", "spin",
  "turntable", "half full", "three hundred forty two", "dry",
  "centimeters" all transcribed; sentence-initial "Spun up slowly." was
  heard as "pun", so "spun up" stays mid-sentence. Three full-narration
  variants (narr1-3, 109-112 words) passed in pre-test.
- Narration: projects/spinglass/narration.txt, 110 words. Voice
  (media/spinglass/voice.log): pass 1 and 2 failed on "centimeters"
  heard as "cm" three times; pass 3 (narr2 wording) failed with four
  "cm"; pass 4 with one "centimeters" instance passed: "ok: transcript
  matches narration (32.507937s)". voice.wav md5
  09a0b8276106d59786af2d46ad204b66. Piper is not deterministic here:
  the same text gave different durations between passes.
- Timing (media/spinglass/timing.log, voice_offset 0.6): question 0.60
  to 8.00 s, mechanism 8.00 to 16.51, question again 16.51 to 21.30,
  "the shallow glass, the dry bottom, at 342 turns a minute" 21.30 to
  26.54, "the spill at the same speed, under half full" 26.54 to 29.42,
  "the bottom shows first" 29.42 to 30.94, "over half full, it spills
  first" 30.94 to 33.11. Voice 32.51 s, ends at 33.11 s of 40.00.
  Eight silences over 0.2 s (media/spinglass/silences.log), the longest
  0.47 s at 15.68 s.
- Compose (media/spinglass/compose.log, 10:21:24 to 10:21:39, exit 0):
  music seed 113, 40.00 s; captions 20 pauses detected, 20 matched,
  max chunk start shift 1.573 s; sheet 8x5 at 1 fps; final.mp4
  40.000000 s; preview.mp4 40.066667 s.

### Local QA

- ffprobe: h264 1080x1920 at 60/1, aac 22050 Hz, duration 40.000000 s,
  moov before mdat (faststart). md5sum final.mp4
  ff1aa38b0ce150b104de8c9099cd49e1.
- Captions: 32 drawtext chunks, 110 of 110 words equal the narration in
  order; "Which comes first," on screen 0.600 to 1.767 s, "dry bottom or
  spill?" 1.767 to 3.014 s; "three hundred forty" 23.597 to 24.335 s,
  "two turns a minute." 24.335 to 25.530 s; "spills first." 32.345 to
  33.108 s.
- Band signalstats over footage.mp4: caption band YMAX 28, overlay band
  YMAX 28 (dark under the text).
- Full-resolution frames viewed (media/spinglass/qa-*.png): 0.00 s
  (overlay, three title rows, both glasses at rest at their still
  levels with the dashed still and rim lines, dials with a mark, no
  caption); 1.00 s (caption "Which comes first,"); 2.10 s ("dry bottom
  or spill?"); 15.00 s (legend, "spinning up, 180 turns a minute", both
  paraboloids, 4 cm centre 2.9 rim 5.1, 6 cm centre 4.9 rim 7.1,
  ring-blurred dials, caption "A dip as deep as the"); 24.00 s (315 rpm,
  4 cm centre 0.6 cm, 6 cm rim 9.4 cm, the card fading in, caption
  "three hundred forty"); 25.40 s (336 rpm, card fully up, "two turns a
  minute."); 26.00 s (345 rpm: 4 cm "center dry" with the dry disc and
  the row "bottom shows at 342 rpm, rim at 8 cm"; 6 cm rim 10.0,
  water 228 mL in gold, streaks and puddles, row "spills at 342 rpm,
  center 2 cm"; caption "The deep glass: the"); 31.60 s (429 rpm: 4 cm
  "spills at 427 rpm" lit with puddles, water 153 mL; 6 cm "bottom shows
  at 382 rpm, 38 mL gone"; caption "Over half full, it"); 39.983 s
  (equal to frame 0). sheet.png shows the run in order: title, ramp,
  event rows lighting, the card from about 24 s, the fade at the end.
  No clipped text, no caption over the readouts, the surface never
  above the rim.

### Metadata

projects/spinglass/metadata.json written by a Python script with
asserts (title 94 chars, at most 100; description 4542 chars, under
5000; no angle brackets; ASCII; 12 tags), then `ls -l` confirmed 5127
bytes. Title: "Which comes first, dry bottom or spill? 4 cm of water:
dry at 342 rpm. 6 cm: spills at 342 rpm". Every number in the
description (74 distinct) and the title appears in measure.log
(checked by script with commas stripped). Category 27, private,
synthetic media declared, not made for kids.

### Deviations from the brief

- Question wording: "Which comes first, dry bottom or spill?" The
  brief's "a dry bottom or a spill" measured 950 px at 40 px on the
  card, so the articles went; the same words in the title, the hook,
  the card and the payoff.
- Overlay "7 cm glass, 10 cm tall | 4 vs 6 cm water | no seed" (942 px);
  the brief's text measured 1059 px.
- Legend "same glass, same ramp, 15 rpm a second" (933 px); "same
  spin-up" measured 984 px.
- Event rows shortened to fit: "bottom shows at 342 rpm, rim at 8 cm"
  (no "4 cm:" prefix, "no spill" dropped), "spills at 427 rpm", "spills
  at 342 rpm, center 2 cm", "bottom shows at 382 rpm, 38 mL gone".
- The dial sits at x 930 (right of the tags) rather than right beside
  the glass; the tags "rim 10 cm" and "still N cm" sit between.
- The volume readout is kept and counts down in gold while spilling
  rather than dropped; the centre readout reads "center dry" once the
  bottom bares.
- Narration 110 words with one "centimeters" (the setup line); the
  payoff names "the shallow glass" and "the deep glass" instead of
  "with four centimeters" and "with six", because whisper heard
  "centimeters" as "cm" after a number in three of four passes.
- The payoff card rises at 23.6 s while the spoken 342 lands at 23.6 to
  25.5 s; the on-screen event is at 25.78 s, about 2 s after the number
  is spoken.
- Two brief figures differ by rounding: the 2 cm spill is 604.2 rpm
  (brief 604.1) and the 341.8 rpm time is 25.78 s (brief 25.79).

## Niche note

[produced 2026-10-05 as "Which comes first, dry bottom or spill? 4 cm
of water: dry at 342 rpm. 6 cm: spills at 342 rpm"; measured 4 cm: dry
bottom at 341.8 rpm (rim 8.0 cm), spill at 427.2 rpm; 6 cm: spill at
341.8 rpm (centre 2.0 cm), bottom dry at 382.1 rpm after 38.5 mL has
spilled (192.4 mL left, half the glass), not at 418.6 rpm, which is the
no-spill guess sqrt(4 g h) / R and would put the rim at 12 cm; half
full both at 382.1 rpm; quadrature worst 2.7e-14 mL; task
20261005-100710]

## Upload

- Attempt 2 of 5 (quota day 2026-10-05T10:00 EEST) recorded at 2026-10-05T11:03:33+03:00 before scripts/yt-upload.py spinglass; one earlier attempt (wedge, succeeded).
- Uploaded private as TxWDK_XlnHg at 2026-10-05T11:03:36+03:00 (videos.insert 1,600 units). yt-qa.py --wait --publish run twice: 11:03:44 tags [] on the first processed read (tag read lag, 14 of 15, refused, 2 units); 11:09:38 after a 330 s wait 15 of 15, published at 2026-10-05T11:09:41+03:00, re-read public, 52 units. https://youtu.be/TxWDK_XlnHg
