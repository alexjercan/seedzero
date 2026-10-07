# Research trends: run 13 for the day 39 slate and the backlog

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: backlog

## Goal

Thirteenth research-trends run, 2026-10-07 from about 10:05 EEST, for
all three slots of day 39 and the backlog. The backlog in `docs/niche.md`
holds seventeen unproduced ideas and the day 38 close judged them weak
for a first pick: space time-lapses and counters (Kelvin wake, Collatz,
secretary problem, rogue wave, Saturn retrograde, Halley, L2 drift),
low-ranked ideas (corner reflector, basketball arc, Moon clock, sliding
ladder, falling chimney, two springs stacked or side by side, stick or
string, train wheel backward), a tie payoff (bathtub drain) and a heavy
build (dam break). Find 6 to 9 new candidates that fit the winning
format: continuous tabletop or everyday motion, two panels on the same
input that end visibly differently on a phone screen, one plain question
in the first two seconds, one setup number, one payoff number, a
closed-form check, a loop or a repeat, and a build of about 25 minutes
with RK4, event-driven steps or closed forms (no PDE, no fluid grid, no
ray tracing, no fitted aerodynamics, no rider or posture models, no
chosen material strengths). Avoid siblings of produced shorts (read the
[produced ...] notes in docs/niche.md: drops beside a ball, Atwood,
yo-yo, chain off a desk, capstan, coin on a record, river crossing,
kerb hop, carried pendulum, balloon in a car, belt, broom, bat, strings,
spool, cue ball, tablecloth, brake or swerve, ice cube against ball,
bucket, swing, spring drop, hoop bead, gyro top, Kapitza, resonance,
metronomes, block on a wedge, spinning glass, cart on a ramp, push or
pull a crate, marble on rails, fingers under a ruler). Re-judge the two
strongest backlog ideas (train wheel backward, sliding ladder) against
the new candidates. Measure every survivor with a throwaway script in
/tmp/day39/research/ (g = 9.807) and check the model (contact forces
positive, no-slip friction available with the minimum mu stated, energy
kept where it should be, panels visibly different at 1080x1920). Rank
the survivors and name the best three for today's three slots with
their numbers, question, setup and payoff numbers and a drawing sketch
each in the style of the day 38 briefs (/tmp/day38/brief-rails.md). No
production in this run.

Rules for this run: follow the research-trends skill (five to ten
focused queries, WebSearch and WebFetch). Append the survivors to
docs/niche.md at the very end of the file under a new paragraph "Added by
trend research 2026-10-07 (evidence in task 20261007-100305; selection
favoured ...)" in the existing one-line bullet format; re-read the file
right before editing and append only. Record the evidence in this task
file (queries, URLs, what each showed, why each idea was accepted or
rejected, the measurement logs) under "## Evidence". Do not edit
web/data/ (the orchestrator appends the journal entry from your report),
do not run git, do not produce anything, do not spawn subagents, never
use sleep in Bash. Finish by reporting: the ranked survivors with their
numbers, the recommended three slot ideas each with a full brief
paragraph, the docs/niche.md lines you added, and a one-paragraph
journal line for web/data/log.jsonl.

## Evidence

Research ran 2026-10-07 about 10:05 to 10:50 EEST. Throwaway scripts
and logs in /tmp/day39/research/ (one per candidate, g 9.807, python3
via nix develop). No production, no git, no web/data change in this
run.

### Queries (10 WebSearch, 5 WebFetch)

1. "physics demo tilt a tray with a marble and a dice which moves first
   friction rolling explanation". Showed the Mungan TPT paper "A race
   between rolling and sliding up and down an incline", UCSC and UCSB
   demo pages and the UMD D1-61 rolling-versus-sliding demo: the
   rolling-versus-sliding race is a standard demo; the tilting-tray
   "which goes first" framing was not found as a short, so it is open.
   https://www.usna.edu/Users/physics/mungan/_files/documents/Publications/TPT52.pdf
   https://lecdem.physics.umd.edu/d/d1/d1-61.html
2. "jump from a boat to the dock physics problem boat moves back fall
   in the water momentum". Showed Vedantu, Brainly (four threads),
   schoolphysics.co.uk and a Physics Forums thread: a textbook staple
   asked many ways ("why is it not a good idea to jump from a rowboat
   to a dock"), always answered with momentum and never with a landing
   distance.
   https://www.schoolphysics.co.uk/age16-19/Mechanics/Dynamics/text/Momentum_conservation/index.html
   https://www.physicsforums.com/threads/person-jumping-out-of-a-moving-boat-problem.27158/
3. "banked curve icy road car slides flat curve versus banked turn same
   speed physics explanation". Showed EIU, Illinois dynref, BC Campus
   and Batesville pages and a Brainly ice-storm question: the design
   speed tan(theta) = v^2 / (r g), the ice-storm "slides up or down"
   case is a known question.
   https://www.ux1.eiu.edu/~addavis/1350/06CirMtn/BankedCurve.html
   https://dynref.engr.illinois.edu/avb.html
4. "stick-slip block pulled by spring hops jerky motion static kinetic
   friction demonstration formula". Showed the TU Delft ShowingPhysics
   demo, Rabinowicz's 1956 Scientific American "Stick and Slip",
   Harvard "Friction Blocks" and the MathWorks friction model: the
   hopping tray demo is standard; no hop formula given anywhere.
   https://interactivetextbooks.tudelft.nl/showthephysics/demos/demo14/demo14.html
   https://sciencedemonstrations.fas.harvard.edu/presentations/friction-blocks
5. "ball rolling off a sphere leaves surface cos theta 10/17 versus
   sliding 2/3 demonstration". Showed the arXiv "Finger Paint and
   Physics" exercise-ball demo (10/17 rolling, 2/3 sliding) and a
   Quora marble-on-a-bowling-ball thread: the numbers are known.
   https://arxiv.org/pdf/1811.11832
6. "viral physics shorts October 2026 everyday experiment debate
   "which one" explained". Showed the fluxnote list, Physics World on
   viral experiments and three generic "experiments that look fake"
   shorts: nothing specific; everyday "I had no idea" framing confirmed.
   https://fluxnote.io/guides/science-youtube-shorts-ideas
7. "lift yourself bosun's chair pulley half your weight physics
   demonstration". Showed Physics Forums (three threads), Berkeley and
   Tom Tits demo pages and Wikipedia: mechanical advantage exactly 2,
   half the weight, twice the rope.
   https://berkeleyphysicsdemos.net/node/136
8. "walk or run in the rain which gets you less wet physics model
   answer". Showed The Conversation, BBC Science Focus, weather.com,
   an arXiv MATLAB simulation and the UW CSE rain page: the box model,
   running wins by about 10 to 30 percent depending on the shape.
   https://theconversation.com/walk-or-run-in-the-rain-a-physics-based-approached-to-staying-dry-or-at-least-getting-less-wet-240849
9. "Steve Mould OR Veritasium OR "Physics Girl" new video 2026
   everyday mechanics puzzle". Showed channel pages and an upload
   schedule (Veritasium 2026: spider silk, eclipse from space): no
   mechanics puzzle peg this week.
   https://seriesreminder.com/series/veritasium
10. "tilting board friction angle block starts to slide tan(mu) while
    ball rolls immediately demonstration "angle of repose" marble".
    Showed Vedantu angle-of-repose pages, everydaybudd's incline
    calculator and MCAT prep: tan(theta) = mu for the block, (2/7)
    tan(alpha) for a rolling ball; the contrast is textbook but not a
    short.
    https://www.vedantu.com/question-answer/define-angle-of-friction-and-angle-of-repose-class-11-physics-cbse-600109271821181eb2312b10

### Sources (fetched pages)

- arXiv 1811.11832 (finger paint on an exercise ball): the extraction
  was garbled (it reported cos 0.75 and 0.50); the search abstract
  gives 10/17 (54 degrees) rolling and 2/3 (48 degrees) sliding, both
  checked in-repo (53.97 and 48.20 from a 1 degree start).
- TU Delft stick-slip demo: cloth on a tube and a sprung tray; no
  numbers and no formula; "the tray will jump ahead, stand still, jump
  ahead".
- Physics Forums boat thread: 50 kg person, 400 kg boat, relative
  speed 4.5 m/s; momentum plus relative velocity; nobody asks whether
  the jumper reaches the dock.
- The Conversation rain article: water = rho d (S_h a / v + S_v); the
  front share is fixed, only the top share shrinks with speed; no
  numbers.
- Veritasium schedule page: no mechanics peg.

### Measured candidates (python3, /tmp/day39/research/*.py and *.log)

1. Tilting tray, marble or dice (tray.py, .log). 40 cm tray, 3 deg/s
   about the low edge, dice grip 0.4, ball k 2/5. Ball off at 1.8726 s
   and 5.618 deg (closed form without frame terms 1.8707 s, 5.612 deg;
   half step within 1.8e-12 s), 0.64 m/s, N 0.988 W, grip needed
   0.028. Dice slides from 21.80 deg (7.267 s), off at 8.910 s and
   26.73 deg, 0.73 m/s, min N 0.90 W. Margin 7.04 s and 21.1 deg. Grip
   0.2 / 0.3 / 0.5 / 0.6: 16.3 / 21.7 / 31.4 / 35.8 deg. Rates 1 / 2 /
   5 deg/s: 2.7 / 4.3 / 7.9 against 24.2 / 25.6 / 28.8 deg. Ice cube
   5.0, cylinder 5.7, hollow ball 6.0, ring 6.3 deg. Drawing: tray 600
   px, raised end 59 px up at the ball's exit, 270 px at the dice's.
2. Jump from a boat (boat.py, .log). 70 kg jumper, 50 kg boat, 3.5
   m/s at 45 deg relative to the boat, 1 m gap. Tied: 2.4749 m/s,
   0.5047 s, apex 0.312 m, lands 1.2491 m (on the dock). Free: jumper
   1.0312 m/s, boat -1.4437 m/s, lands 0.5205 m (0.48 m short), boat
   back 0.7286 m; ratio 2.4000 = (M + m) / M; momentum 0. RK4
   projectile check to 1e-6 m. Same-energy model 0.8063 m. Clears 1 m
   from a 281 kg boat or at 6.72 m/s. Boats 30 / 100 / 200 / 400 kg:
   0.37 / 0.73 / 0.93 / 1.06 m. KE 428.8 J tied, 303.7 J free.
   Drawing at 400 px/m: gap 400, tied landing 500, free 208, recoil
   291 px.
3. Banked curve on ice (bank.py, .log). 50 km/h, R 50 m, grip 0.1,
   bank 20 deg, lane half width 3.5 m. Needed 0.3934 g. Flat: slides,
   radius 196.70 m, over the outer edge after 22.051 m and 1.5876 s
   (RK4 1.5876 s, speed kept 50.00 km/h); flat limit 25.21 km/h.
   Banked: grip needed 0.0257 outward, N 1.0742 W, holds; design 48.09
   km/h; window 40.23 to 55.32 km/h; 30 and 40 km/h slide down the
   bank, 60 and 70 out. Grips 0.3 / 0.5 / 0.8: flat limits 43.7 / 56.4
   / 71.3 km/h, banked windows 19.1 to 68.8 / 0 to 81.9 / 0 to 102.2.
   Bank needed at 50 km/h with grip 0.1: 15.76 deg; no grip 21.47.
4. Tall glass or short glass (glass.py, .log, glass_edge.log). Grip
   0.5, 3 deg/s. Slide line 26.565 deg (8.855 s), a sliding glass at
   the edge 10.479 s, 31.44 deg. Tall 7 x 18 cm tips at 21.250 deg
   (7.084 s), on its side at 7.810 s (0.727 s later, tray at 23.4
   deg); edge grip under 0.5 until psi 52 deg (0.657 s), edge force
   zero at 7.777 s. Short 8 x 8 cm slides first (tip would need 45
   deg). Grip 0.3 slides both; 0.4 and 0.6 keep the split.
5. Rope or bungee (bungee.py, .log). 2 kg, grips 0.5 / 0.3, 50 N/m,
   5 cm/s. Rope creeps at 5 cm/s. Bungee: first stretch 19.61 cm in
   3.9228 s; slip w 5 rad/s, A 7.85 cm, slip 0.6790 s, hop 0.1909 m
   (2A 0.1569 plus 0.0340), cycle 3.8173 s, stuck 3.14 s; stepped
   dt 1e-5 gives 5 hops at 3.9228, 7.7401, 11.5573, 15.3746, 19.1919
   s, each 0.1909 m; peak 0.4455 m/s; energy 0.9233 + 0.1998 = 1.1231
   J per hop (quadrature 0.1998). 20 / 100 / 200 N/m: 44.4 / 10.3 /
   5.7 cm. Hand 2 / 10 / 20 cm/s: 17.0 / 23.0 / 32.0 cm.
6. Bosun's chair (bosun.py, .log). 70 + 10 kg, W 784.56 N, pull 450
   N. Friend: nothing moves. Self: 2 P 900 N, 1.4430 m/s^2, 2.886 m in
   2 s, 5.772 m of rope; threshold 392.28 N (40.0 kg). Energy 2,597.4
   J = 2,264.2 + 333.2 J. Pull 400 N: 0.193 m/s^2; 800 N lifts both.
7. Ice cube or ball off a dome (dome.py, .log). R 20 cm, r 1 cm, from
   1 deg. Ice cube leaves 48.198 deg at 1.1434 m/s (0.6545 s), lands
   29.23 cm out. Ball ideal 53.975 deg (10/17), 1.1006 m/s, lands
   28.50 cm; with grip 0.3 / 0.5 / 1.0 / 2.0 it slips from 35.4 / 41.8
   / 47.6 / 50.7 deg and leaves at 52.13 / 52.76 / 53.33 / 53.64 deg.
   On a 350 px dome the leave points are 22 by 27 px apart and the
   landing points 13 px apart.
8. Walk or run in the rain (rain.py, .log). Box 0.10 m^2 top, 0.68
   front, 100 m, rain 8 m/s: walk 1.5 m/s 121,333 drops against run 4
   m/s 88,000, 27.5 percent less; the front 68,000 is fixed; the limit
   is 44 percent less.
9. Train wheel backward and sliding ladder: re-judged on the numbers
   already in docs/niche.md (6.67 km/h backward, 13 mm loop; ladder
   top leaves at 2/3 height, second panel weak); no new script.

### Ranking

Filter: continuous tabletop or everyday motion, two panels on the same
input that end visibly differently on a phone, one plain question, one
setup number, one payoff number, a closed-form check, a loop or repeat,
about 25 minutes with RK4, events or closed forms, no PDE, no fluid
grid, no fitted aerodynamics, no rider or posture models, no chosen
material strengths, no siblings of produced shorts.

1. Tilting tray, marble or dice (accepted, slot 1). Marble off at 5.6
   deg, dice off at 26.7 deg, 21 deg and 7 s apart; exact closed forms
   for both (w t - sin w t and tan theta = mu); the panels end with one
   object gone while the other sits; the mechanism (friction holds a
   block, only turns a ball) follows the picture; tilt-and-reset loop.
   Not a sibling: the ice cube or ball uphill asked "which climbs
   higher", this asks "which goes first when you tilt".
2. Jump from a boat (accepted, slot 2). Tied lands 1.25 m, free 0.52 m
   and falls in; exact (M + m) / M = 2.4; an everyday debate asked many
   ways online and never answered with a distance; point-mass jumper,
   like the cart recoil; the model choice (relative takeoff speed) is
   stated and the alternative lands short too.
3. Banked curve on ice (accepted, slot 3). Flat car over the lane edge
   in 1.59 s, banked car holds with grip 0.0257 needed; exact closed
   forms and a 40 to 55 km/h window; a road subject like brake or
   swerve (734 views); the bank needs a cross-section inset.
4. Tall glass or short glass (accepted, rank 4). Tips at 21.3 deg
   against slides at 26.6 deg, exact thresholds; the tip fall needs the
   edge model (holds to 52 deg, lifts 0.03 s before the side lands);
   same prop as idea 1, so a week apart.
5. Rope or bungee (accepted, rank 5). Hops of 19.1 cm every 3.82 s
   against a smooth creep; exact hop formula; the stick-slip mechanism
   already carried the fingers-under-a-ruler short.
6. Bosun's chair (accepted, rank 6). Nothing moves against 2.89 m in
   2 s, threshold half the weight; the pull is a chosen number and it
   is a pulley cousin of the Atwood drop.
7. Train wheel backward (backlog, stays low): one number, 13 mm loop.
8. Sliding ladder (backlog, stays low): the second panel is weak.
9. Ice cube or ball off a dome (rejected): the panels look alike (22
   px between the leave points, 13 px between the landings) and the
   ball slips before it leaves, so the 10/17 is never reached.
10. Walk or run in the rain (rejected): a rate-only counter with a
    27.5 percent answer and no motion that ends differently.

Queued backlog ideas: nothing in this run showed a queued idea weak or
saturated beyond the notes already on them; no notes added.

### Files changed

- docs/niche.md: appended "Added by trend research 2026-10-07 (evidence
  in task 20261007-100305; ...)" with six bullets: Tilting tray marble
  or dice, Jump from a boat, Banked curve on ice, Tall glass or short
  glass, Rope or bungee, Bosun's chair. No other bullet changed.
- tasks/20261007-100305/TASK.md (this file).
- No web/data change, no production, no upload, no commit in this run.
