# Produce short: Chain over the desk edge, 18 cm hanging beside 22 cm on the same desk

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day33

## Goal

Backlog idea (trend research 2026-09-30, task 20260930-100404, pillar 2
chaos and physics, everyday mechanics; read the full entry under "Added
by trend research 2026-09-30" in docs/niche.md): "Necklace over the desk
edge: a 1 m chain on a desk with mu 0.25, 18 cm hanging beside 22 cm;
measure whether it slides off and when; expect the threshold at exactly
20 percent hanging (mu / (1 + mu)), the 18 cm chain to hold for ever and
the 22 cm chain to run away as a cosh (the excess over the threshold
e-folds every 0.286 s, rate sqrt((1 + mu) g / L)) and be all off the
desk at 1.252 s with the last link at 2.80 m/s (21 cm: 1.450 s, 25 cm:
0.990 s, 30 cm: 0.791 s); frictionless, 1 cm hanging leaves at 1.69 s;
mu 0.4 needs 28.6 percent, mu 0.1 9.1; RK4 within 1e-4 s of the closed
form; repeat the drop; deterministic, no seed."

Orchestrator notes (2026-10-01, before this brief). The model: a uniform
chain of length L = 1.00 m (mass per length lambda, it cancels) lies
straight on a level desk and hangs straight down over a smooth rounded
edge (no friction and no momentum loss at the corner: say "a smooth
rounded edge"); x is the hanging length; friction on the desk part mu =
0.25, the same at rest and sliding (a chosen number for a metal chain on
a wooden desk, say so); g = 9.80665. At rest the chain holds while the
hanging weight g x is at most the grip mu g (L - x), so the threshold is
x* = mu L / (1 + mu) = 0.2000 m: exactly one fifth of the chain. With 18
cm over the edge the grip needed is 0.18 / 0.82 = 0.2195 of the weight
on the desk, under 0.25: it holds for ever. With 22 cm the need is 0.22
/ 0.78 = 0.2821, over 0.25: it slides. Sliding: lambda L x'' = lambda g
x - mu lambda g (L - x), so x'' = (g / L)((1 + mu) x - mu L) = k^2 (x -
x*) with k = sqrt((1 + mu) g / L) = 3.5012 per second (e-fold 0.2856 s);
from rest x(t) = x* + (x0 - x*) cosh(k t). The chain is all off the desk
when x = L: for x0 = 0.22 m at t = acosh((L - x*) / (x0 - x*)) / k =
acosh(40) / k = 1.2518 s, the last link moving at k (x0 - x*) sinh(k t) =
2.80 m/s; after that the whole chain falls freely (draw it falling out
of the band). Checks, not facts (orchestrator closed forms, /tmp/day33):
x* = 20.00 cm; 18 cm holds (need 0.2195 against 0.25), 22 cm slides
(need 0.2821); off the desk at 1.2518 s at 2.80 m/s; the 2 cm excess
doubles to 4 cm at 0.376 s (cosh k t = 2), 20 cm at 1.05 s; 21 cm off
at 1.450 s, 25 cm at 0.990 s, 30 cm at 0.791 s, 50 cm at 0.471 s;
frictionless with 1 cm hanging: off at 1.692 s; mu 0.4 needs 28.57
percent, mu 0.1 needs 9.09 percent, mu 0.25 at 2 m of chain still needs
one fifth (the fraction does not depend on L or on the chain's weight);
integrate the slide by RK4 at 10,000 steps a second from rest at x0 and
check it against the cosh form within 1e-4 s and 1e-6 m, plus a
half-step rerun; also print the static check for 18 cm (net force
negative, so RK4 is not needed: the chain never moves) and the time the
hanging part passes 30, 50, 75 and 100 cm. State every derived number
above as a check the sim must print, not as a fact.

Drawing: side view; the same desk in both bands, a slab whose top is
about 90 px under the band top and whose right edge sits near x 700 px
(the band is 550 px tall, so use 400 px per metre: the 1 m chain lies
328 px along the desk when 18 cm hang and reaches 400 px below the desk
top when it is all over the edge, inside the band); the chain as a line
of round links or beads at a fixed pitch (say 2 cm) that slide right
along the desk and down over the edge, so the viewer sees the chain
move link by link; a muted tick on the hanging part at 20 cm labelled
"one fifth"; the top band the 18 cm chain ("18 cm over the edge"), the
bottom band the 22 cm chain ("22 cm over the edge"); left column: the
label and "grip needed 0.22 of the weight on the desk, has 0.25" (or a
shorter wording that fits); right column: live "hanging NN cm" and
"speed N.NN m/s"; a gold event row "holds, for ever" (top, lit two
seconds after the release) and "slides off at 1.25 s" (bottom, lit as
the last link leaves). A finger or clamp holds each chain until the
release (a short held phase at the start of each cycle), then lets go.
Shown at 1/3 speed (1.25 s becomes 3.76 s); cycle 8 s with the release
0.6 s in and a reset crossfade at the end, 5 cycles in 40 s, the last
frame equal to the first; the fall after the edge continues out of the
band before the fade (assert it). Nothing drawn under the captions.

Day thirty-three, first slot. Chosen because "will it slide off" is a
tabletop debate anyone can picture, the panels end visibly differently
(one chain never moves, the other runs away and drops), and the payoff
is an exact fraction with a closed-form check. Question in the first two
seconds: "Will the chain slide off the desk?" (keep the question
identical in the title, the hook and the payoff). Setup number: one
meter of chain, with eighteen centimeters over the edge beside twenty
two. Payoff number: the line is twenty centimeters, exactly one fifth
(the 22 cm chain is gone in one and a quarter seconds). The e-fold time,
the 21 / 25 / 30 cm times, the frictionless case and the other grips go
to the card and the description. Whisper risks: "one fifth" and "a
fifth" (pre-test both), "chain" (passed on 2026-09-26), "desk", "edge",
"slides" and "slide off" (pre-test), "hang" / "hangs" / "hanging"; avoid
"do you"; avoid "pull" as a noun; "eighteen" and "twenty two" as words.
Pre-test hooks with scripts/voiceover.sh and keep the one whose question
lands earliest under two seconds. Measure every fixed text line with PIL
before rendering and keep every line under 950 px, and the title under
100 characters with no < or >. Music seed 101. Templates: sims/belt
(two bands, Coulomb slip, reset fade, layout asserts), sims/chain (a
drawn chain of links), sims/tablecloth (slow motion with a release
inside the cycle). Sim name deskchain: sims/deskchain/deskchain.py,
projects/deskchain/, media/deskchain/.

## Claim (expected; the sim's numbers replace these)

A 1 m chain on a desk with grip 0.25 holds for ever with 18 cm over the
edge (grip needed 0.2195 of the weight on the desk) and slides off with
22 cm over the edge: the hanging length runs away as 20 cm + 2 cm
cosh(3.5012 t), the last link leaves the desk at 1.2518 s at 2.80 m/s.
The line is exactly one fifth of the chain, mu / (1 + mu) = 20.00 cm,
whatever the chain's length or weight. Narrated: one meter of chain,
eighteen centimeters over the edge beside twenty two (setup); the line
is twenty centimeters, exactly one fifth; the twenty two is gone in one
and a quarter seconds (payoff). Card: the question; 18 cm holds, 22 cm
gone in 1.25 s; the line 20 cm = one fifth, mu / (1 + mu); 21 cm 1.45
s, 25 cm 0.99 s, 30 cm 0.79 s; grip 0.4 needs 28.6 %, 0.1 needs 9.1 %;
no friction: 1 cm hanging is off in 1.69 s. Description: the cosh law
and the e-fold, the RK4 checks, the model statement.

## Claim

A 1 m chain on a desk with grip 0.25 holds for ever with 18 cm over the
edge (grip needed 0.2195 of the weight on the desk, net -0.0250 lambda g)
and slides off with 22 cm over the edge (grip needed 0.2821): the hanging
length runs away as 20 cm + 2 cm cosh(3.5012 t) and the last link leaves
the desk at 1.2515 s at 2.80 m/s (RK4 at 10,000 steps/s within 1.6e-15 s
of the closed form, half step within 2.2e-15 s). The line is exactly one
fifth of the chain, mu / (1 + mu) = 20.00 cm = 20.00 percent, whatever the
chain's length or weight (2 m of chain: 40.0 cm, the same fifth).
Narrated: one meter of chain, eighteen centimeters over the edge on top,
twenty two below (setup); at eighteen no, at twenty two yes; the line is
twenty centimeters, exactly one fifth of the chain, whatever it weighs;
just over it the whole chain is gone in one and a quarter seconds
(payoff). Card: the question; 18 cm holds, 22 cm is gone in 1.25 s; the
line is 20 cm, exactly one fifth; 21 cm 1.45 s, 25 cm 0.99 s, 30 cm 0.79
s; grip 0.4 needs 28.6 %, 0.1 needs 9.1 %; no grip: 1 cm hanging is off
in 1.69 s. Description: the model statement, the cosh law and the e-fold,
the crossings, the description-only variants, the RK4 checks.

## Evidence

### Measurements

media/deskchain/measure.log (`nix develop -c python3
sims/deskchain/deskchain.py --measure-only`, 2026-10-01 10:29:48 EEST,
final manifest):

```
Thu Oct  1 10:29:48 AM EEST 2026
setup: the same desk in both panels: a uniform chain of 1 m (40 links of 2.5 cm; its mass per length cancels) lies straight on a level desk and hangs straight down over a smooth rounded edge (no friction and no momentum loss at the corner); friction on the desk part mu = 0.25, the same at rest and sliding (a chosen number for a metal chain on a wooden desk); g = 9.80665 m/s^2; a clamp holds each chain until the release; top panel 18 cm over the edge, bottom panel 22 cm; the slide integrated by RK4 at 10000 steps per second (dt = 1e-04 s) with the edge crossing located by bisection inside the step, checked against the closed form x = x* + (x0 - x*) cosh(k t) and a half-step rerun; after the edge the whole chain falls freely; shown at 1/3 speed on a 8 s cycle (480 frames) with the release 0.4 s into the cycle, 5 cycles in 40 s; drawn at 380 px per metre; deterministic, no seed
threshold: at rest the chain holds while the hanging weight lambda g x is at most the grip mu lambda g (L - x), so the line is x* = mu L / (1 + mu) = 0.2000 m = 20.00 cm = 20.00 percent of the chain, exactly one fifth at mu = 0.25 (1/5 = 0.2000); the fraction does not depend on L or on the chain's weight; sliding, x'' = k^2 (x - x*) with k = sqrt((1 + mu) g / L) = 3.5012 per second, so the excess over the line grows as cosh(k t): it e-folds every 1/k = 0.2856 s and doubles at acosh(2) / k = 0.3761 s
18 cm over the edge (top panel): the hanging weight is 0.1800 lambda g, the grip available mu (L - x0) = 0.2050 lambda g, net -0.0250 lambda g: negative, so the chain never moves and RK4 is not needed; the grip needed is x0 / (L - x0) = 0.2195 of the weight on the desk, under 0.25; 18 cm is 2.0 cm under the line: it holds for ever
22 cm over the edge (bottom panel): the hanging weight is 0.2200 lambda g against a grip of 0.1950 lambda g, net +0.0250 lambda g: positive, so it slides; the grip needed is 0.2821 of the weight on the desk, over 0.25; 22 cm is 2.0 cm over the line; RK4 from rest: the chain is all off the desk at 1.2515 s (closed form acosh((L - x*) / (x0 - x*)) / k = 1.2515 s, diff +1.6e-15 s) with the last link moving at 2.8001 m/s = 2.80 m/s (closed form k (x0 - x*) sinh(k t) = 2.8001 m/s, diff -6.7e-15 m/s), 12516 steps; the hanging length stays within 4.8e-15 m of the cosh form over the run; half-step rerun (dt = 5e-05 s): off at 1.2515384 s (+2.2e-15 s) at 2.8000744 m/s (+1.5e-14 m/s); after the edge the whole chain falls freely from 2.80 m/s
crossings (RK4 table, 22 cm chain): the excess doubled to 4 cm at 0.3761 s at 0.121 m/s (closed form 0.3761 s, diff -5.0e-09 s); the hanging part at 30 cm at 0.6548 s at 0.343 m/s (closed form 0.6548 s, diff -4.3e-09 s); the excess at 20 cm (hanging 40 cm) at 0.8549 s at 0.697 m/s (closed form 0.8549 s, diff -2.4e-09 s); the hanging part at 50 cm at 0.9711 s at 1.048 m/s (closed form 0.9711 s, diff -3.1e-09 s); the excess at 20 times its start (hanging 60 cm) at 1.0534 s at 1.399 m/s (closed form 1.0534 s, diff -3.6e-09 s); the hanging part at 75 cm at 1.1445 s at 1.924 m/s (closed form 1.1445 s, diff -3.7e-09 s); the hanging part at 100 cm at 1.2515 s at 2.800 m/s (closed form 1.2515 s, diff +1.6e-15 s)
for the description: 21 cm over the edge (grip needed 0.2658): all off at 1.4495 s at 2.80 m/s (closed form 1.4495 s, diff -7.3e-15 s); 25 cm over the edge (grip needed 0.3333): all off at 0.9896 s at 2.80 m/s (closed form 0.9896 s, diff +1.3e-15 s); 30 cm over the edge (grip needed 0.4286): all off at 0.7908 s at 2.78 m/s (closed form 0.7908 s, diff -2.6e-15 s); 50 cm over the edge (grip needed 1.0000): all off at 0.4675 s at 2.60 m/s (closed form 0.4675 s, diff +1.1e-15 s); no friction (mu 0) with 1 cm over the edge: the line is at 0 cm and k = sqrt(g / L) = 3.1316 per second; all off at 1.6919 s at 3.13 m/s (closed form acosh(L / x0) / k = 1.6919 s, diff -4.4e-16 s); grip 0.4 needs 28.57 percent over the edge (28.57 cm of 1 m); grip 0.1 needs 9.09 percent over the edge (9.09 cm of 1 m); grip 0.25 with 2 m of chain needs 40.0 cm = 20.00 percent, the same fifth; the chain's weight cancels, so a heavy chain and a light one share the line
schedule (video time, 1/3 speed): cycles of 8 s start at -0.40, 7.60, 15.60, 23.60, 31.60, 39.60 s (the first 0.40 s before the first frame); the clamps let go 0.4 s into each cycle at 0.00, 8.00, 16.00, 24.00, 32.00 s; the 22 cm chain's hanging part passes 30 cm at 1.96, 9.96, 17.96, 25.96, 33.96 s; 50 cm at 2.91, 10.91, 18.91, 26.91, 34.91 s; 75 cm at 3.43, 11.43, 19.43, 27.43, 35.43 s; it is all off the desk 3.75 s after the release at 3.75, 11.75, 19.75, 27.75, 35.75 s (the event row lights) and its tail is out of the band 0.79 s later at 4.54, 12.54, 20.54, 28.54, 36.54 s (4.94 s into the cycle, before the fade at 7.40 s); the 18 cm chain never moves and its event row lights 2 s after the release at 2.00, 10.00, 18.00, 26.00, 34.00 s; the clamp lifts over 0.3 s; the reset crossfade runs over the last 0.6 s of each cycle (from 7.00, 15.00, 23.00, 31.00, 39.00 s; the readouts out over its first half and in over its second); on the first frame the cycle is 0.40 s in (0.000 s real after the release: the 18 cm chain hold at 18.0 cm, the 22 cm chain slide at 22.0 cm); title until 3 s; payoff card from 22.9 s; the title fades back in over the last 0.5 s and the last frame repeats the first (the scene is periodic: 40 s holds exactly 5 cycles)
text widths: overlay@34 804 px, title line 1@56 433 px, title line 2@56 578 px, legend@40 772 px, clock@28 390 px, clock held@28 194 px, label hold@40 463 px, sublabel hold@28 424 px, fixed hold@28 307 px, event hold@40 330 px, label slide@40 463 px, sublabel slide@28 424 px, fixed slide@28 285 px, event slide@40 415 px, hanging@40 360 px, off@40 269 px, speed@28 239 px, last link@28 313 px, on the desk@28 309 px, tick@24 214 px, payoff line 1@40 729 px, payoff line 2@40 819 px, payoff line 3@40 769 px, payoff line 4@40 914 px, payoff line 5@40 879 px, payoff line 6@40 827 px
row check: the left column ends at x 503 px, the right column starts at x 680 px; both end 136 px under the band top; the desk top is 150 px under the band top (slab to 178, legs at x 70 and 580 to 526); the clamp spans x 616 to 660 px between the columns and rises to 46 px under the band top when lifted; the event row spans 308 to 352 px under the band top and x 132 to 548 px (widest 415 px, centred on 340) between the legs; the chain hangs at x 684 px from 146 px under the band top and its tip reaches 530 px with the chain all over the edge; the one fifth tick at 222 px under the band top, its label to x 936 px; each band is 550 px tall (y 330 to 880 and 880 to 1430); the caption band starts at y 1440; the title rows end at y 280 and the overlay band ends at y 130
Thu Oct  1 10:29:48 AM EEST 2026
```

Brief checks (every number is a line the sim printed):

- x* = mu L / (1 + mu) = 20.00 cm = 20.00 percent, exactly one fifth:
  passed (0.2000 m, 1/5 = 0.2000; the fraction does not depend on L or
  on the weight).
- 18 cm holds, grip needed 0.2195 against 0.25: passed (net -0.0250
  lambda g; the static check is printed, RK4 not needed).
- 22 cm slides, grip needed 0.2821: passed (net +0.0250 lambda g).
- All off the desk at 1.2518 s at 2.80 m/s: the sim gives 1.2515 s
  (RK4 and the closed form acosh(40) / 3.5012 agree within 1.6e-15 s;
  the brief's 1.2518 is a rounding of the same expression) with the last
  link at 2.8001 m/s = 2.80 m/s: passed.
- k = sqrt((1 + mu) g / L) = 3.5012 per second, e-fold 0.2856 s: passed.
- The 2 cm excess doubles to 4 cm at 0.376 s: passed (0.3761 s).
- "20 cm at 1.05 s": the sim gives the excess at 20 times its start
  (hanging 60 cm) at 1.0534 s, which is the brief's 1.05 s; the excess
  at 20 cm (hanging 40 cm) is at 0.8549 s. Both printed.
- 21 cm 1.450 s, 25 cm 0.990 s, 30 cm 0.791 s: passed (1.4495, 0.9896,
  0.7908 s).
- 50 cm 0.471 s: the sim gives 0.4675 s (acosh((1 - 0.2) / (0.5 - 0.2))
  / 3.5012 = 0.4675 s, RK4 and closed form within 1.1e-15 s); the
  brief's 0.471 s is 3.5 ms off. The description uses 0.4675 s.
- Frictionless with 1 cm hanging, off at 1.692 s: passed (1.6919 s at
  3.13 m/s, k = 3.1316 per second).
- mu 0.4 needs 28.57 percent, mu 0.1 needs 9.09 percent: passed.
- mu 0.25 with 2 m of chain still one fifth: passed (40.0 cm = 20.00
  percent).
- RK4 at 10,000 steps per second within 1e-4 s and 1e-6 m of the cosh
  form: passed (1.6e-15 s, 4.8e-15 m over the run, 12,516 steps);
  half-step rerun at 5e-05 s: passed (+2.2e-15 s, +1.5e-14 m/s).
- The static check for 18 cm printed: passed.
- The hanging part passing 30, 50, 75 and 100 cm printed: passed
  (0.6548, 0.9711, 1.1445, 1.2515 s at 0.343, 1.048, 1.924, 2.800 m/s,
  each within 5e-09 s of the closed form).
- The fall after the edge continues out of the band before the fade:
  asserted (the tail leaves the band 0.79 s after the last link leaves
  the desk, 4.94 s into the 8 s cycle; the fade starts at 7.40 s).

### Production

- Sim: sims/deskchain/deskchain.py, modelled on sims/belt/belt.py: RK4
  at 10,000 steps/s with bisection on the crossing step, closed-form and
  half-step checks, the static check, crossings read from the RK4 table;
  the drawing reads the same table (np.interp) and free fall after the
  edge; 2x supersampled bands; loop, periodicity and loop-step checks;
  ffmpeg rawvideo pipe with a ProcessPoolExecutor; --measure-only and
  --frames.
- Manifest projects/deskchain/manifest.json: seed 0, fps 60, g 9.80665,
  chain 1.0 m, mu 0.25, hangs 0.18 / 0.22 m, link 2.5 cm (40 beads),
  10,000 steps/s, slow 3.0, cycle 8 s, first_cycle_at -0.4 s, release_at
  0.4 s, reset_fade 0.6 s, hold event 2 s after the release, clamp lift
  0.3 s, scene 40 s, 380 px/m, desk edge at x 680, desk top 150 px under
  the band top, title "Will the chain|slide off the desk?" until 3 s,
  payoff_t 22.9 s, payoff_hold 0.6 s, six payoff lines formatted from the
  measured values, loop_fade 0.5, music seed 101, gain 0.18, voice offset
  0.6, caption_y 0.75, overlay "1 m chain | grip 0.25 | 1/3 speed | no
  seed"; description-only hangs 21 / 25 / 30 / 50 cm, grips 0.4 / 0.1,
  2 m chain, frictionless 1 cm.
- Layout: overlay y 96-130 (compose); title two rows at y 190 / 252
  until 3 s; legend "same desk, same chain, 1/3 speed" at y 236 and the
  clock ("held, at rest" / "N.NNN s after the release") at y 290 after
  the title; bands y 330-880 (18 cm, teal) and 880-1430 (22 cm, coral);
  per band: label "18 cm over the edge" (40 px), "grip needed 0.22, has
  0.25" (28 px) and "2 cm under / over the line" (28 px gold, from the
  release); right column "hanging NN cm" (40 px), "speed N.NN m/s", "on
  the desk NN cm"; after the edge "off the desk" and "last link at 2.80
  m/s"; the desk slab from 150 px under the band top with its right edge
  at x 680 and legs at x 70 and 580; the chain as 40 alternating beads
  at 2.5 cm (9.5 px) pitch sliding right along the desk and down over
  the edge, a gold tip and a coloured start marker; the muted tick "20
  cm, one fifth" on the hanging part; a clamp between the columns that
  lifts 50 px over 0.3 s at the release; the gold event row under the
  desk between the legs (x 132-548): "holds, for ever" 2 s after the
  release, "slides off at 1.25 s" as the last link leaves; the six-line
  gold card from y 1572 at a 48 px pitch; nothing in rows 96-130 or
  1440-1530 (asserted in the row check and measured on the footage).
- Hook pre-tests (media/deskchain/hooks/pretest.log, 10:23): hook1 ok
  6.23 s (question first, speech from 0.076 s); hook2 ok 7.35 s; hook3
  ("A chain on a desk. Will the chain slide off the desk?") ok 3.15 s,
  question from 1.19 s voice = 1.79 s video; hook4 ok 6.87 s, speech
  from 0.065 s voice = 0.67 s video, question ends 1.74 s voice = 2.34 s
  video: chosen; hook5 failed ("meter" heard as "niter" once). words.txt:
  "slides off the desk", "slides off the edge", "one fifth", "a fifth",
  "exactly one fifth of the chain", "hangs over the edge", "hang over the
  edge", "twenty two centimeters", "let go", "the grip wins", "pulls the
  chain over", "link by link", "one and a quarter seconds", "whatever the
  chain weighs", "nothing moves" all passed; "for ever" heard as
  "forever": not spoken (the event row keeps the brief's "holds, for
  ever").
- Narration: projects/deskchain/narration.txt, 104 words; the question is
  the first sentence (spoken 0.67-2.30 s) and is repeated word for word
  ("So, will the chain slide off the desk?") before the payoff; one setup
  number (one meter of chain; eighteen centimeters and twenty two) and
  one payoff number (twenty centimeters, exactly one fifth; one and a
  quarter seconds); American spelling; no digits.
- Voice (media/deskchain/voice.log): pass 1 (107 words, 10:25:24)
  failed, "Not at eighteen." heard as "9 at eighteen"; pass 2 (10:25:43)
  reworded to "At eighteen, no.", ok 35.25 s; pass 3 (104 words,
  10:28:47, restructured for the schedule: dropped "Same desk, same
  grip.", moved "gone in one and a quarter seconds" to the last sentence)
  ok 33.62 s. voice.wav ends at 34.22 s of video; 14 pauses at d 0.22.
- timing.log (voice offset 0.6 s; whisper's own spelling):

```
  0.60 -   7.46  Will the chain slide off the desk?
 1 meter of chain, 18 centimeters hang over the edge on top,
 22 below.
  7.46 -   8.26  Let go!
  8.26 -  10.96  Below, each link that goes over polls harder.
 10.96 -  13.77  It runs away, link by link, and drops.
 13.77 -  14.59  On top.
 14.59 -  17.33  The part on the desk grips back. The grip wins!
 17.33 -  20.62  Nothing moves. So, will the chain slide off the desk?
 20.62 -  21.81  At 18, no.
 21.81 -  23.48  At 22, yes.
 23.48 -  25.19  The line is 20 centimeters.
 25.19 -  27.29  exactly one-fifth of the chain,
 27.29 -  29.34  whatever it weighs under the line
 29.34 -  30.65  The chain stays put.
 30.65 -  31.57  Just over it,
 31.57 -  34.22  The whole chain is gone in one and a quarter seconds.
voice 33.62 s, ends at 34.22 s of video
```

- Schedule and sync: releases at 0, 8, 16, 24, 32 s. "Let go." 7.60-8.39
  over the release at 8.0; "Below, each link that goes over pulls
  harder. It runs away, link by link, and drops." 8.39-13.90 while the
  22 cm chain runs away (30 cm at 9.96, 50 cm at 10.91, all off at 11.75
  with the event row lit, tail out at 12.54); "On top, the part on the
  desk grips back. The grip wins. Nothing moves." 13.90-18.01 with the
  top chain still and "holds, for ever" lit since 10.00; "So, will the
  chain slide off the desk?" 18.01-20.74 as the cycle-3 chain goes off
  at 19.75; "At eighteen, no. At twenty two, yes." 20.74-23.61 with both
  event rows lit (the crossfade starts at 23.0); the card rises from
  22.9 s and is full at 23.5 s as "The line is twenty centimeters,
  exactly one fifth of the chain, whatever it weighs." 23.61-28.52 is
  spoken; "Under the line, the chain stays put. Just over it, the whole
  chain is gone in one and a quarter seconds." 28.52-34.22 while the
  cycle-5 chain slides (released at 32.0, 30 cm at 33.96, all off at
  35.75 with "slides off at 1.25 s" lit); the title fades back in over
  39.5-40.0 s.
- Smoke frames viewed before the render: smoke-{0.0, 2.0, 3.2, 4.4, 5.0,
  7.9, 8.6, 10.6, 26.6, 39.6}.png on the first schedule (release 0.6 s
  in) and smoke-{0.0, 8.1, 23.3}.png on the final schedule: title and
  clamped chains at 0; clamps lifted and the 22 cm chain creeping; HUD
  legend and clock; "holds, for ever" under the top desk; "off the desk /
  last link at 2.80 m/s / slides off at 1.25 s" with the chain falling
  out of the band; the crossfade back to the clamped setup; the six-line
  card inside the frame; the loop fade. All text inside the frame.
- Render (media/deskchain/render.log, 10:29:49-10:30:15): loop check 0
  px, periodicity check 0 px, loop step 0 px (threshold 24 levels; the
  last two frames sit in the held phase), footage 40.00 s at 60 fps,
  2400 frames.
- Compose (media/deskchain/compose.log, 10:30:26-10:30:39): music seed
  101, 40.00 s; captions 23 pauses detected, 23 matched (max chunk start
  shift 1.091 s against word-count timing); contact sheet 8x5 at 1 fps;
  final.mp4 40.000000 s; preview.mp4 40.066667 s.
- Text widths (PIL ImageFont.getlength, DejaVuSans-Bold, asserted < 950
  px): overlay@34 804, title@56 433 / 578, legend@40 772, clock@28 390
  (held 194), labels@40 463, sublabels@28 424, fixed@28 307 / 285,
  event@40 330 / 415, hanging@40 360, off@40 269, speed@28 239, last
  link@28 313, on the desk@28 309, tick@24 214, payoff lines@40 729 /
  819 / 769 / 914 / 879 / 827 px.

### Local QA

- Frames extracted from media/deskchain/final.mp4 (never edited) with
  ffmpeg -ss T and viewed at full resolution:
  - 0.00: overlay, the title "Will the chain / slide off the desk?",
    both chains clamped at the edge with 18 cm and 22 cm hanging,
    "hanging 18 cm / speed 0.00 m/s / on the desk 82 cm" and "hanging 22
    cm / 0.00 m/s / 78 cm", the "20 cm, one fifth" tick, no caption, no
    card.
  - 1.00: clamps lifted; the 22 cm chain at 24 cm and 0.10 m/s, the 18
    cm chain still at 18 cm; caption "Will the chain slide".
  - 2.10: "holds, for ever" lit in gold under the top desk (2.0 s) and
    "hanging 18 cm" gold; the 22 cm chain at 32 cm, 0.40 m/s, its tip
    past the tick; caption "off the desk?".
  - 11.00 (mid-run, cycle 2): legend and clock "1.000 s after the
    release", "2 cm under the line" / "2 cm over the line", the 22 cm
    chain at 53 cm and 1.16 m/s with 47 cm on the desk; caption
    "harder.".
  - 19.60: clock 1.200 s, the 22 cm chain at 87 cm and 2.34 m/s with 13
    cm on the desk, the tail still inside the band; caption "slide off
    the desk?".
  - 23.30 (payoff + 0.4): the cycle-3 crossfade (clock 2.433 s, clamps
    back on both chains, readouts faded out) with the card rising at two
    thirds; caption "At twenty two, yes.".
  - 24.70 (payoff + 1.8): cycle 4 at 0.233 s after the release, the 22
    cm chain at 23 cm and 0.06 m/s, the card full in gold; caption "The
    line is twenty".
  - 33.50: cycle 5 at 0.500 s, 26 cm at 0.20 m/s, the card full; caption
    "in one and a quarter".
  - 39.98 (frame 2399): the title back, both chains clamped, the same
    picture as 0.00; no caption, no card.
  Nothing clipped at the frame edges, no text in the caption band, the
  six card lines sit between y 1572 and about 1850.
- sheet.png (8x5 at 1 fps): five identical cycles: the clamped setup,
  the 22 cm chain running away and falling out of the band with "off
  the desk / last link at 2.80 m/s / slides off at 1.25 s", the top chain
  still with "holds, for ever", the crossfade back; captions under; the
  card from the tile at 23 s.
- Question timing: on screen from frame 0 in the title; spoken from
  0.665 s of video (speech onset 0.065 s in voice.wav plus the 0.6 s
  offset) to 2.30 s; repeated at 18.01-20.74 s; answered "At eighteen,
  no. At twenty two, yes." at 20.74-23.61 s.
- Captions: 32 chunks of at most 20 characters, 0.60-34.22 s; the
  concatenated caption text equals narration.txt word for word (104
  words, compared by script).
- Payoff number on screen when spoken: "the line is 20 cm, exactly one
  fifth" is full on the card from 23.5 s while "The line is twenty
  centimeters, exactly one fifth" is spoken 23.61-26.84 s; "gone in one
  and a quarter seconds" 31.92-34.22 s with "22 cm is gone in 1.25 s" on
  the card.
- Footage signalstats: overlay band (rows 96-130) and caption band (rows
  1440-1530) YMAX 28 in all 2400 footage frames; both bands hold only
  the background.
- Loop: render.log loop check 0 px and periodicity check 0 px on the
  footage. Final loop noise (codec only): frame 2399 vs 0: 22,282 px
  over 8 levels, 262 over 32, max 77 at a title letter edge, mean 0.48;
  2398 vs 2399: 14,594 / 17 / max 50; 0 vs 1: 1,693 / 892 / max 108
  (the clamps start to lift).
- ffprobe final.mp4: h264 1080x1920 yuv420p 60/1, 2400 frames, duration
  40.000000 s, aac 22050 Hz mono, moov before mdat (faststart),
  3,616,912 bytes.
- md5sum media/deskchain/final.mp4: e18b9fb86f792cf45019f155c754a1e0.
- Narrated numbers against measure.log: "one meter of chain" (a uniform
  chain of 1 m), "eighteen centimeters" (18 cm over the edge, top
  panel), "twenty two" (22 cm over the edge, bottom panel), "twenty
  centimeters, exactly one fifth" (x* = 0.2000 m = 20.00 cm = 20.00
  percent, exactly one fifth), "one and a quarter seconds" (all off the
  desk at 1.2515 s). All on printed lines.
- Metadata number check by script (commas stripped): 93 numbers in the
  description (60 distinct), none missing from measure.log; the title's
  18, 22, 1.25 and 20 all present.

### Metadata

- Title (99 characters, ASCII, no < or >): Will the chain slide off the desk? 18 cm holds, 22 cm is gone in 1.25 s. The line: 20 cm, one fifth
- Description: 3,291 characters, ASCII, no arrows; one setup paragraph
  (the model, every constant, RK4 and its checks, 1/3 speed, 5 runs in
  40 s, no seed), "Measured:" bullets (the line, both panels, k and the
  crossings, the description-only hangs and grips, the frictionless
  case, the 2 m chain, the RK4 checks), a "Why:" paragraph, the rerun
  line, the AI line.
- Tags (11): will the chain slide off the desk, chain over the desk edge, chain on a table, sliding chain, friction, static friction, one fifth, physics, physics visualization, simulation, shorts.
- categoryId "27", privacyStatus "private", containsSyntheticMedia true,
  selfDeclaredMadeForKids false.

### Deviations from the brief

- Desk top 150 px under the band top at 380 px/m (brief: about 90 px at
  400 px/m): the label, sublabel and fixed rows need 136 px, so the slab
  sits under them; at 380 px/m the chain's tip reaches 530 px under the
  band top when it is all over the edge, inside the 550 px band (400
  px/m would reach 550 px plus the bead).
- The gold event row sits under the desk between the legs (x 132-548),
  not at the band centre, so it never meets the hanging chain.
- The release is 0.4 s into the cycle with first_cycle_at -0.4 s (brief:
  0.6 s in, cycle from 0): the clamps let go at 0, 8, 16, 24, 32 s so
  "Let go." lands on a release; frame 0 is the release instant with the
  clamps still down.
- "At eighteen, no." instead of "Not at eighteen." (whisper heard "9 at
  eighteen").
- "for ever" is not spoken (whisper joins it to "forever"); the event row
  keeps the brief's "holds, for ever".
- The brief's "20 cm at 1.05 s" matches the excess at 20 times its start
  (hanging 60 cm, 1.0534 s); the excess at 20 cm (hanging 40 cm) is at
  0.8549 s. Both printed; the description uses the printed values.
- 50 cm over the edge: the sim gives 0.4675 s, the brief 0.471 s; the
  description uses 0.4675 s.
- The brief's 1.2518 s: the sim's RK4 and closed form give 1.2515 s; the
  title and card say 1.25 s.
- Narration restructured after pass 2 (104 words: dropped "Same desk,
  same grip.", moved "gone in one and a quarter seconds" to the last
  sentence) so each narrated event plays under its words.

## Niche note

  [produced 2026-10-01 as "Will the chain slide off the desk? 18 cm
  holds, 22 cm is gone in 1.25 s. The line: 20 cm, one fifth"; measured
  a 1 m chain (40 links of 2.5 cm) on the same desk with mu 0.25 and g
  9.80665 over a smooth rounded edge, 18 cm hanging on top and 22 cm
  below, RK4 at 10,000 steps/s with bisection at the edge: the line x* =
  mu L / (1 + mu) = 20.00 cm = 20.00 percent, exactly one fifth whatever
  the chain weighs or how long it is (2 m needs 40.0 cm, the same
  fifth); 18 cm holds for ever (grip needed 0.2195, net -0.0250 lambda
  g), 22 cm slides (needed 0.2821): all off at 1.2515 s with the last
  link at 2.80 m/s (closed form within 1.6e-15 s, half step within
  2.2e-15 s), k 3.5012/s, e-fold 0.2856 s, the excess doubles at 0.3761
  s, 30/50/75 cm at 0.6548/0.9711/1.1445 s; 21 cm 1.4495 s, 25 cm 0.9896
  s, 30 cm 0.7908 s, 50 cm 0.4675 s (the brief said 0.471); no friction
  with 1 cm hanging 1.6919 s; mu 0.4 needs 28.57 percent, mu 0.1 9.09;
  shown at 1/3 speed on an 8 s cycle, 5 drops in 40 s; task
  20261001-101157]

## Upload

- orchestrator review (2026-10-01T10:48:52+03:00): task evidence, sheet.png and full frames at
  0.00, 11.00, 24.70 and 39.98 s inspected; ffprobe h264 1080x1920 60 fps
  2400 frames 40.000 s; md5 e18b9fb86f792cf45019f155c754a1e0; title 99
  chars, no angle brackets; description 3291 chars, no angle brackets, 11
  tags; captions match narration word for word (32 chunks); measure.log
  matches the closed forms (x* = mu L / (1 + mu) = 20.00 cm, k = 3.5012
  per second, the 22 cm chain all off at 1.2515 s with closed form
  acosh((L - x*) / (x0 - x*)) / k, 21 cm 1.4495 s, 25 cm 0.9896 s, 30 cm
  0.7908 s); approved for upload
- upload attempt 1 of 5 for the quota day that began 2026-10-01T10:00
  EEST, recorded at 2026-10-01T10:48:52+03:00 before starting scripts/yt-upload.py; zero
  attempts were on record since the boundary (journal and media/*/upload.log
  checked)
- uploaded private as 12ESwWxQ9Ws at 2026-10-01T10:48:56+03:00
  (https://youtu.be/12ESwWxQ9Ws); channels.list 1 unit + videos.insert
  1,600 units; media/deskchain/upload.log
- scripts/yt-qa.py deskchain 12ESwWxQ9Ws --wait --publish in the
  foreground (started 2026-10-01T10:49:04+03:00): gate 14 of 15, tags
  read back as [] on the first processed read (the known read lag of
  about six minutes after an insert; not re-sent); publish refused; 3
  units; rerun after the lag
- scripts/yt-qa.py deskchain 12ESwWxQ9Ws --wait --publish rerun in the
  foreground (started 2026-10-01T10:54:52+03:00): gate 15 of 15 (processed,
  succeeded, hd, 1080x1920, title, description and tags match, category
  27, not made for kids, PT41S for the 40.000 s file, private before
  publish); published at 2026-10-01T10:54:54+03:00; re-read
  privacyStatus=public selfDeclaredMadeForKids=False embeddable=True;
  yt-qa quota 52 units; media/deskchain/publish.log
- attempt 1 of 5 complete: 1,656 units; slot 1 of 3 resolved as
  published (recorded 2026-10-01T10:55:23+03:00)

### Quota
- attempt 1 of the hard cap of 5 for the quota day that began
  2026-10-01T10:00 EEST; cost 1,656 units (the channels.list verification
  inside yt-upload.py, the 1,600-unit insert, the first gate run's 3
  reads, and the rerun's reads, update and re-read as printed by
  yt-qa.py, 52); day total after one attempt 1,656 of 10,000 used,
  8,344 remaining
