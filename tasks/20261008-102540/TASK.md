# Produce short: five books past the table edge, equal steps beside shrinking steps, does the stack hold

- STATUS: OPEN
- PRIORITY: 0
- TAGS: day40

## Goal

Backlog idea (trend research 2026-10-08, task 20261008-100401, pillar 2
chaos and physics, everyday statics; read the full "Books past the
table edge" bullet at the end of docs/niche.md): five books stacked one
at a time at a table edge, each pushed out the same step beside steps
that shrink from the top; the equal stack falls at book four, the
shrinking stack holds its top book wholly past the table.

Orchestrator notes (2026-10-08; closed forms in /tmp/day40/closed.py
with the log /tmp/day40/closed.log; research scripts
/tmp/day40/research/books5.py, books.py, books_tip.py with their logs;
g = 9.807 m/s^2). Read /tmp/day40/producer-conventions.md first. The
model: five identical uniform books, L = 20 cm long and 3 cm thick,
placed one at a time from the bottom up; the bottom book's front end
sits d1 past the table edge and each next book sits d_i past the front
end of the one below. Statics, exact in fractions: a sub-stack (the top
j books) holds on the book under it, or the whole stack holds on the
table, when its combined centre of mass is at or behind that support's
front end (the margin = support end minus the sub-stack's centre, in
cm; the stack falls at the first negative margin). Top band, the "equal"
case: d = 4.44 cm for every book (chosen so that both stacks reach the
same 22.2 cm). Bottom band, the "shrinking" case: steps 1.9, 2.4, 3.2,
4.9, 9.8 cm from the bottom up (each just under L/10, L/8, L/6, L/4,
L/2, the harmonic steps). Print every sub-stack margin after each book
goes on, both stacks' top ends, the exact limit for 4 and 5 books, the
equal-step rule, the variants for the description, and the fall of the
equal stack drawn as one rigid piece about the table edge (RK4, say it
is a drawing model: the four books as one body with its centre of mass
1.10 cm past the edge and 6.0 cm up, pivoting while the edge grip holds
(grip 0.3 chosen for the drawing) then sliding off and out of the band).

Checks, not facts (the sim must print and compare; state them as
checks; exact fractions where they are exact): equal 4.44 cm: after
book 1 the worst margin is +5.56 cm at the table, after book 2 +3.34,
after book 3 +1.12, after book 4 -1.10 (TIPS: the centre of mass of the
four is 1.10 cm past the edge), so the stack falls when book 4 goes on
and book 5 is never placed (after 5 it would be -3.32); the rule: equal
steps d topple a stack of n books once d > L / (n + 1), so 4.44 cm
holds 3 books (limit 5.00) and not 4 (limit 4.00); shrinking 1.9 / 2.4
/ 3.2 / 4.9 / 9.8: after book 1 +8.10 at the table, after 2 +6.90, after
3 +5.433, after 4 +3.475, after 5 +0.200 at book 3 (the worst), every
margin positive, the top book's front end 22.20 cm out and its back end
2.20 cm past the table edge (wholly past the table); the exact limit is
half the harmonic sum: 137/120 of a book = 22.833 cm for five, 25/24 =
20.833 cm for four (only 0.8 cm clear, so five books); the equal stack's
drawing fall: 0.335 s to 51.5 deg (7.56 rad/s) at grip 0.3 before it
slides (0.348 s to 57.6 deg at grip 0.5). Print the schedule in video
time, the text widths and the layout clearances.

Drawing: two-band layout (sims/deskchain style, read it whole; bands y
330 to 880 and 880 to 1430; sims/fingers draws balance-point readouts,
sims/tray a tip about an edge), SIDE view at 2,000 px per metre: the
table top 470 px under the band top with its edge at x 470 and a leg,
books 400 by 60 px slabs with a 2 px darker spine line, stacked from the
table top upward (five books = 300 px, the top at 170 px under the band
top: clear of the readout rows at 40 / 84 / 120 px; assert), each book
sliding in from the left along the top of the stack to its place (0.6 s
of video per book) so the step is visible; a dashed vertical line at
the table edge from the table top to the band top; under the stack a
small gold triangle marker at the combined centre of mass of the books
placed so far, with the live margin readout; the top book's overhang
marked when it lands. Label rows (40 px, coloured): "equal steps, 4.44
cm" (coral) and "shrinking steps, 9.8 to 1.9 cm" (teal). Readouts (28
px): left column "book N of 5" and "balance N.NN cm behind the edge"
(live; "N.NN cm past the edge" in gold when negative); right column
"top book NN.N cm out". Gold event rows: top "equal: falls at book 4"
(lit as the stack starts to tip and held), bottom "shrinking: holds,
2.2 cm past the table" (lit when book 5 lands and held). Timeline, no
slow motion needed: cycle 10 s (600 frames): books land at 1, 2, 3, 4
and 5 s of the cycle (each slides in over the 0.6 s before it lands);
the equal stack tips from 4.0 s (draw the drawing-model pivot at 1/2
speed, 0.67 s of video to 51.5 deg, then slide off and fall out of the
band by 6 s); the shrinking stack's book 5 lands at 5.0 s and the stack
holds; hold both to 9.5 s, crossfade reset over the last 0.5 s; 4 cycles
in 40 s, exactly periodic, the last frame equal to the first (the first
frame shows book 1 already sliding in on both bands: motion in frame
one). Legend row after the title: "same five books, same table edge".
Overlay: "five 20 cm books | no seed" (measure it).

Day forty, second slot. Chosen because "can the top book sit entirely
past the table" is a desk trick anyone can try tonight, the two stacks
end in a fall against a hold, the numbers are exact fractions (137/120
of a book, d > L / (n + 1)), and a stack built one book at a time
repeats cleanly. Question in the first two seconds: "Can a stack of
books hold the top one completely past the table?" (pre-test; it is the
first sentence). Keep the question identical in the title, the hook and
the payoff. Setup number: "five books" (one setup number only; the step
sizes go to the labels, card and description). Payoff: "Yes: shrink the
steps and the top book sits two point two centimeters past the table.
Equal steps fall at book four." (at most two numbers in the payoff beat).
The mechanism sentence must follow the picture: each book only has to
balance the books above it, so the top steps can be big and the bottom
ones must be small; equal steps push the whole pile's balance point past
the edge. Whisper risks: "centimeters" (once per take), "two point two",
"book four" (may come back "before": pre-test "falls at book four" and
"falls when the fourth book goes on"), "stack", "steps", "overhang"
(avoid); avoid "do you", avoid "too". Pre-test hooks with
scripts/voiceover.sh and keep the one whose question lands earliest
under two seconds. Measure every fixed text line with PIL before
rendering and keep every line under 950 px, and the title under 100
characters with no < or >. Music seed 122. Templates: sims/deskchain
(two-band layout, asserts, the clock, the crossfade; read it whole),
sims/fingers (balance readouts), sims/tray (tip about an edge). Sim
name bookstack: sims/bookstack/bookstack.py, projects/bookstack/,
media/bookstack/.

## Claim (expected; the sim's numbers replace these)

Five 20 cm books go on one at a time at a table edge. Pushed out 4.44
cm each, the pile's balance point is 1.12 cm inside the edge after
three books and 1.10 cm past it when the fourth goes on, so it falls at
book four. With steps that shrink from the top (9.8, 4.9, 3.2, 2.4, 1.9
cm) every book balances the ones above it, the worst margin is 0.2 cm,
and the top book's back end sits 2.2 cm past the table. The limit for
five books is 137/120 of a book, 22.8 cm. Narrated: five books (setup);
two point two centimeters past the table against falls at book four
(payoff). Card: the question; the answer (shrinking: holds, 2.2 cm past;
equal 4.44 cm: falls at book 4); the limit 22.8 cm; the rule d > L / (n
+ 1). Description: the model statement, the margins, both stacks, the
limits for 4 and 5 books, the drawing model, the checks.

## Claim

Five identical 20 cm books, 3 cm thick, go on one at a time at a table
edge (statics, exact in fractions). Pushed out 4.44 cm each, the worst
margin is +5.56, +3.34 and +1.12 cm after books 1 to 3 (all at the
table), and when the fourth goes on the four books' centre of mass is
1.10 cm past the edge (margin -11/10 cm), so the stack falls at book
four and book 5 is never placed (it would be -3.32). Equal steps d
topple n books once d > L / (n + 1): 4.44 cm holds 3 books (limit 5.00)
and not 4 (limit 4.00). With steps that shrink from the top (1.9, 2.4,
3.2, 4.9, 9.8 cm from the bottom up) every margin is positive: +8.10,
+6.90, +5.433, +3.475 at the table and +0.200 cm at book 3 after book 5;
the whole stack's centre is 0.34 cm behind the edge, the top book's
front end 22.20 cm out and its back end 2.20 cm past the table edge.
The limit is half the harmonic sum: 137/120 of a book = 22.833 cm for
five, 25/24 = 20.833 cm for four (0.833 cm clear). The drawn fall (a
drawing model, grip 0.3, the corner pushing normal to the bottom
book's face) pivots 0.251 s to 23.8 deg, slides off the corner until
0.342 s at 51.5 deg and leaves the band 0.509 s after the tip starts.
Narrated: five books (setup); "Yes: shrink the steps and the top book
sits two point two centimeters past the table. Equal steps fall at book
four." (payoff).

## Evidence

### Measurements

`nix develop -c python3 sims/bookstack/bookstack.py --measure-only`
(final run after the phase change, exit 0, saved as
media/bookstack/measure.log; the first run at 10:36 differed only in the
schedule line and the dates):

```
Thu Oct  8 11:06:43 AM EEST 2026
setup: side view, two bands on one clock, the same table drawn the same way at the same scale: 5 identical uniform books, L = 20 cm long and t = 3 cm thick (the weight cancels), placed one at a time from the bottom up at a table edge; the bottom book's front end sits d1 past the table edge and each next book sits d_i past the front end of the one below; a sub-stack (the top j books) holds on the book under it, or the whole stack holds on the table, while its combined centre of mass is at or behind that support's front end; margin = support end minus the sub-stack's centre (cm, exact fractions), the stack falls at the first negative margin; top band equal steps 4.44, 4.44, 4.44, 4.44, 4.44 cm, bottom band shrinking steps 1.9, 2.4, 3.2, 4.9, 9.8 cm from the bottom up; g = 9.807 m/s^2; drawn at 2000 px per metre; deterministic, no seed
equal steps (111/25, 111/25, 111/25, 111/25, 111/25 cm):
  after book 1: margins on the table +139/25 = +5.560; worst +5.560 cm at the table, holds; the whole stack's centre 5.560 cm behind the edge; top end 4.44 cm out
  after book 2: margins on the table +167/50 = +3.340; on book 1 +139/25 = +5.560; worst +3.340 cm at the table, holds; the whole stack's centre 3.340 cm behind the edge; top end 8.88 cm out
  after book 3: margins on the table +28/25 = +1.120; on book 1 +167/50 = +3.340; on book 2 +139/25 = +5.560; worst +1.120 cm at the table, holds; the whole stack's centre 1.120 cm behind the edge; top end 13.32 cm out
  after book 4: margins on the table -11/10 = -1.100; on book 1 +28/25 = +1.120; on book 2 +167/50 = +3.340; on book 3 +139/25 = +5.560; worst -1.100 cm at the table, FALLS; the whole stack's centre -1.100 cm past the edge (1.10 cm past); top end 17.76 cm out
  after book 5: margins on the table -83/25 = -3.320; on book 1 -11/10 = -1.100; on book 2 +28/25 = +1.120; on book 3 +167/50 = +3.340; on book 4 +139/25 = +5.560; worst -3.320 cm at the table, FALLS; the whole stack's centre -3.320 cm past the edge (3.32 cm past); top end 22.20 cm out
  equal: falls at book 4
shrinking steps (19/10, 12/5, 16/5, 49/10, 49/5 cm):
  after book 1: margins on the table +81/10 = +8.100; worst +8.100 cm at the table, holds; the whole stack's centre 8.100 cm behind the edge; top end 1.90 cm out
  after book 2: margins on the table +69/10 = +6.900; on book 1 +38/5 = +7.600; worst +6.900 cm at the table, holds; the whole stack's centre 6.900 cm behind the edge; top end 4.30 cm out
  after book 3: margins on the table +163/30 = +5.433; on book 1 +6 = +6.000; on book 2 +34/5 = +6.800; worst +5.433 cm at the table, holds; the whole stack's centre 5.433 cm behind the edge; top end 7.50 cm out
  after book 4: margins on the table +139/40 = +3.475; on book 1 +23/6 = +3.833; on book 2 +87/20 = +4.350; on book 3 +51/10 = +5.100; worst +3.475 cm at the table, holds; the whole stack's centre 3.475 cm behind the edge; top end 12.40 cm out
  after book 5: margins on the table +17/50 = +0.340; on book 1 +3/10 = +0.300; on book 2 +4/15 = +0.267; on book 3 +1/5 = +0.200; on book 4 +1/5 = +0.200; worst +0.200 cm at book 3, holds; the whole stack's centre 0.340 cm behind the edge; top end 22.20 cm out
  shrinking: every margin positive, holds; the top book's front end 22.20 cm out, its back end 2.20 cm past the table edge (wholly past the table)
limit (the harmonic stack, every margin zero): n books reach (L / 2) H_n: 1: 1/2 of a book = 10.000 cm; 2: 3/4 of a book = 15.000 cm; 3: 11/12 of a book = 18.333 cm; 4: 25/24 of a book = 20.833 cm; 5: 137/120 of a book = 22.833 cm; 6: 49/40 of a book = 24.500 cm; 7: 363/280 of a book = 25.929 cm; 8: 761/560 of a book = 27.179 cm
five books: steps L/10, L/8, L/6, L/4, L/2 = 2.000, 2.500, 3.333, 5.000, 10.000 cm reach 137/120 of a book = 22.833 cm, the top book's back end 2.833 cm past the edge; four books reach 25/24 = 20.833 cm, only 0.833 cm clear
equal steps d: the whole stack's centre sits L/2 - d (n + 1) / 2 behind the edge, so n books fall once d > L / (n + 1): n = 1: 10 = 10.00 cm; n = 2: 20/3 = 6.67 cm; n = 3: 5 = 5.00 cm; n = 4: 4 = 4.00 cm; n = 5: 10/3 = 3.33 cm
equal 111/25 cm: holds 3 books (limit 5.00 cm) and not 4 (limit 4.00 cm)
for the description: the shrinking steps upside down (9.8 cm at the bottom): worst margins after each book +0.200, -2.250, -4.133, -5.675, -6.980 cm; falls at book 2; the exact harmonic steps L/10 .. L/2: worst margins after each book +8.000, +6.750, +5.222, +3.208, +0.000 cm; holds, top end 22.833 cm out, back end +2.833 cm; equal 4.00 cm steps: worst margins after each book +6.000, +4.000, +2.000, +0.000, -2.000 cm; falls at book 5; equal 3.33 cm steps: worst margins after each book +6.670, +5.005, +3.340, +1.675, +0.010 cm; holds, top end 16.650 cm out, back end -3.350 cm
the fall (drawing model): the 4 books as one rigid body, centre of mass 1.10 cm past the edge and 6.0 cm up, I about the centre 279.90 m cm^2 per book mass (books (L^2 + t^2) / 12 plus parallel axes), 428.74 about the corner; RK4 at dt = 1e-05 s, events by bisection inside the step
  grip 0.3, the brief's table-frame split (horizontal over vertical corner force): pivots 0.335 s to 51.5 deg (7.56 rad/s), vertical push 0.563 W; the face frame (normal to the bottom book's face, drawn): pivots 0.251 s to 23.8 deg (4.18 rad/s), push 0.772 W, grip needed 0.300
  grip 0.5, the brief's table-frame split (horizontal over vertical corner force): pivots 0.348 s to 57.6 deg (8.25 rad/s), vertical push 0.543 W; the face frame (normal to the bottom book's face, drawn): pivots 0.279 s to 31.5 deg (5.16 rad/s), push 0.648 W, grip needed 0.500
  half-step rerun (face, grip 0.3): 0.250648 s against 0.250648 s (+6.7e-14 s), 23.8381 deg
  drawn (grip 0.3): pivots 0.251 s to 23.8 deg, then slides 0.92 cm along the bottom face over the corner (kinetic grip 0.3) until 0.342 s at 51.5 deg (the corner's push reached zero), then flies free at (0.33, -0.61) m/s turning 5.99 rad/s; half-step rerun leaves at 0.34152 s (-4.4e-13 s); the slide speed never reverses (min 0.0e+00 m/s)
  drawn fall checks: no book corner inside the table and the table corner inside no book over the fall (worst 0.00 mm); the highest corner reaches 202 px under the band top (the readout rows end at 136); every book is under the band bottom 0.509 s after the tip starts
checks against the brief (33 checks, 22 exact in fractions, 0 failed): equal after book 1 worst margin (cm): brief 139/25, sim 139/25 exactly: ok; equal after book 2 worst margin (cm): brief 167/50, sim 167/50 exactly: ok; equal after book 3 worst margin (cm): brief 28/25, sim 28/25 exactly: ok; equal after book 4 worst margin (cm): brief -11/10, sim -11/10 exactly: ok; equal after book 5 worst margin (cm): brief -83/25, sim -83/25 exactly: ok; equal four books' centre past the edge (cm): brief 11/10, sim 11/10 exactly: ok; equal falls at book: brief 4, sim 4 exactly: ok; rule limit n = 3 (cm): brief 5, sim 5 exactly: ok; rule limit n = 4 (cm): brief 4, sim 4 exactly: ok; equal holds books: brief 3, sim 3 exactly: ok; shrinking after book 1 worst margin (cm): brief 81/10, sim 81/10 exactly: ok; shrinking after book 2 worst margin (cm): brief 69/10, sim 69/10 exactly: ok; shrinking after book 4 worst margin (cm): brief 139/40, sim 139/40 exactly: ok; shrinking after book 5 worst margin (cm): brief 1/5, sim 1/5 exactly: ok; shrinking worst after book 5 at book: brief 3, sim 3 exactly: ok; shrinking falls never (0 = never): brief 0, sim 0 exactly: ok; shrinking every margin positive (1 = yes): brief 1, sim 1 exactly: ok; shrinking top front end (cm): brief 111/5, sim 111/5 exactly: ok; shrinking top back end past the edge (cm): brief 11/5, sim 11/5 exactly: ok; equal top front end after 5 (cm): brief 111/5, sim 111/5 exactly: ok; limit five books (of a book): brief 137/120, sim 137/120 exactly: ok; limit four books (of a book): brief 25/24, sim 25/24 exactly: ok; shrinking after book 3 worst margin (cm): brief 5.433, sim 5.43333, diff +3.3e-04: ok; limit five books (cm): brief 22.833, sim 22.8333, diff +3.3e-04: ok; limit four books (cm): brief 20.833, sim 20.8333, diff +3.3e-04: ok; four-book clearance (cm): brief 0.8, sim 0.833333, diff +3.3e-02: ok; fall body centre past the edge (cm): brief 1.1, sim 1.1, diff +2.2e-16: ok; fall body centre up (cm): brief 6, sim 6, diff +0.0e+00: ok; table-frame pivot time, grip 0.3 (s): brief 0.335, sim 0.334548, diff -4.5e-04: ok; table-frame pivot angle, grip 0.3 (deg): brief 51.5, sim 51.4503, diff -5.0e-02: ok; table-frame spin, grip 0.3 (rad/s): brief 7.56, sim 7.55736, diff -2.6e-03: ok; table-frame pivot time, grip 0.5 (s): brief 0.348, sim 0.348175, diff +1.8e-04: ok; table-frame pivot angle, grip 0.5 (deg): brief 57.6, sim 57.6173, diff +1.7e-02: ok
schedule (video time): cycles of 10 s start at -4.80, 5.20, 15.20, 25.20, 35.20 s (the first 4.80 s before the first frame); each book slides in over the 0.6 s before it lands; books land 1, 2, 3, 4, 5 s into each cycle: book 1 at 6.20, 16.20, 26.20, 36.20 s; book 2 at 7.20, 17.20, 27.20, 37.20 s; book 3 at 8.20, 18.20, 28.20, 38.20 s; book 4 at 9.20, 19.20, 29.20, 39.20 s; book 5 at 0.20, 10.20, 20.20, 30.20 s; the equal stack never gets book 5; it starts to tip as book 4 lands at 9.20, 19.20, 29.20, 39.20 s (its event row lights), the fall drawn at 1/2 speed: it pivots 0.50 s of video to 23.8 deg, slides off by 9.88, 19.88, 29.88, 39.88 s and has left the band at 0.22, 10.22, 20.22, 30.22 s (5.02 s into the cycle, by 6 s); the shrinking stack's book 5 lands and its event row lights at 0.20, 10.20, 20.20, 30.20 s; both held to 9.5 s, the reset crossfade over the last 0.5 s of each cycle (from 4.70, 14.70, 24.70, 34.70 s); on the first frame the cycle is 4.80 s in (book 5 67 percent through its slide, the equal stack 0.80 s of video into its fall); title until 3 s; payoff card from 30.3 s; the title fades back in over the last 0.5 s and the last frame repeats the first (40 s holds exactly 4 cycles)
text widths (the on-screen strings verbatim): overlay@34 509 px 'five 20 cm books | no seed', title line 1@56 653 px 'Can a stack of books', title line 2@56 522 px 'hold the top one', title line 3@56 843 px 'completely past the table?', legend@40 768 px 'same five books, same table edge', clock@28 633 px 'one book a second, the fall at 1/2 speed', label equal@40 469 px 'equal steps, 4.44 cm', event equal@28 334 px 'equal: falls at book 4', label shrinking@40 673 px 'shrinking steps, 9.8 to 1.9 cm', event shrinking@28 612 px 'shrinking: holds, 2.2 cm past the table', book count@28 177 px 'book 5 of 5', balance behind@28 525 px 'balance 8.10 cm behind the edge', balance past@28 486 px 'balance 1.10 cm past the edge', top book@28 336 px 'top book 22.2 cm out', payoff line 1@40 848 px 'can a stack of books hold the top one', payoff line 2@40 602 px 'completely past the table?', payoff line 3@40 874 px 'shrinking: holds, 2.2 cm past the table', payoff line 4@40 668 px 'equal 4.44 cm: falls at book 4', payoff line 5@40 874 px 'five-book limit 22.8 cm (137/120 book)', payoff line 6@40 794 px 'equal steps fall once d > L / (n + 1)'
row check: the label rows run 40 px under the band top; row 84 ends at x 217 px on the left and starts at x 704 px on the right; row 120 ends at x 565 px; the rows end 136 px under the band top; the five-book stack's top is 170 px under the band top, its overhang line at 158 px, the dashed edge line from the table top to 146 px; the books span x 108 to 914 px; the table top 470 px under the band top with its edge at x 470, slab to 490, a leg at x 60 to 78; the centre-of-mass triangle from 472 to 489 px; the event rows centred 520 px under the band top from x 100 to 434 (equal) and 712 (shrinking); the falling books are drawn only past the edge under the table top; each band is 550 px tall (y 330 to 880 and 880 to 1430); the caption band starts at y 1440; the title rows end at y 330
exit 0
Thu Oct  8 11:06:46 AM EEST 2026
```

Checks in the brief, each printed and compared by the sim (33 checks,
22 exact in fractions, 0 failed, assert on the count):

- equal 4.44 cm, worst margin after book 1 +5.56, 2 +3.34, 3 +1.12, 4
  -1.10, 5 -3.32 cm, all at the table: sim 139/25, 167/50, 28/25,
  -11/10, -83/25 exactly. ok.
- the four books' centre of mass 1.10 cm past the edge: sim 11/10
  exactly; falls at book 4: sim 4. ok.
- the rule d > L / (n + 1): limits 5 (n = 3) and 4 (n = 4) exactly; 4.44
  cm holds 3 books and not 4. ok.
- shrinking worst margin after book 1 +8.10, 2 +6.90, 4 +3.475, 5 +0.200
  cm: sim 81/10, 69/10, 139/40, 1/5 exactly; after book 3 +5.433: sim
  163/30 = 5.43333. ok.
- the worst after book 5 is at book 3: sim book 3 (book 4 ties at 1/5;
  the first minimum is book 3). ok.
- every shrinking margin positive, never falls: sim yes. ok.
- top front end 22.20 cm (both stacks after five) and back end 2.20 cm
  past the table edge: sim 111/5 and 11/5 exactly. ok.
- limits 137/120 of a book = 22.833 cm for five, 25/24 = 20.833 cm for
  four, about 0.8 cm clear: sim 137/120, 25/24 exactly, 22.8333,
  20.8333, 0.833 cm. ok.
- the fall body: centre of mass 1.10 cm past the edge and 6.0 cm up: sim
  1.1 and 6. ok.
- the brief's fall numbers, table-frame criterion: 0.335 s to 51.5 deg
  (7.56 rad/s) at grip 0.3, 0.348 s to 57.6 deg at grip 0.5: sim
  0.334548 s, 51.4503 deg, 7.55736 rad/s; 0.348175 s, 57.6173 deg. ok
  as a reproduction of the research model; the drawn model uses the
  face-frame criterion, see Deviations.
- half-step reruns: face pivot 0.250648 s, diff +6.7e-14 s; free-flight
  start 0.34152 s, diff -4.4e-13 s; the slide never reverses. ok.
- the drawn fall never cuts the table (worst 0.00 mm), its highest
  corner reaches 202 px under the band top (rows end at 136), and every
  book is under the band bottom 0.509 s after the tip starts, 5.02 s
  into the cycle at 1/2 speed (by 6 s). ok, asserted.
- five books reach 170 px under the band top, the overhang line 158,
  the readout rows end 136: asserted. ok.
- every fixed text line under 950 px: widest payoff line 3 and 5 at 874
  px; asserted. ok.
- schedule: books land 1, 2, 3, 4, 5 s into each 10 s cycle, the
  cycles start at -4.80, 5.20, 15.20, 25.20, 35.20 s (first_cycle_at
  -4.8, see Deviations); the equal stack tips at 9.20, 19.20, 29.20,
  39.20 s and has left the band at 0.22, 10.22, 20.22, 30.22 s; the
  shrinking book 5 lands at 0.20, 10.20, 20.20, 30.20 s; crossfade over
  the last 0.5 s (from 4.70, 14.70, 24.70, 34.70 s); 4 cycles in 40 s;
  the first frame is 4.80 s into the cycle (book 5 67 percent through
  its slide, the equal stack 0.80 s of video into its fall; the sim now
  asserts motion on the first frame). ok.

### Production

- sims/bookstack/bookstack.py (new): two-band side view after
  sims/deskchain (bands y 330 to 880 and 880 to 1430, label rows at 40,
  readouts at 84 and 120, the crossfade, the loop and periodicity
  checks, the ffmpeg rawvideo render), the tip about an edge after
  sims/tray (RK4 with bisection for events, the dashed line helper).
  Statics in Fractions with every sub-stack margin printed; the fall as
  a three-phase drawing model (pivot, slide over the corner with kinetic
  grip, free flight) by RK4 at 1e5 steps per second with half-step
  reruns; 33 brief checks with assert; text-width and layout asserts
  (stack top, overhang line, row columns, event rows against the leg
  and the edge, the falling books against the table and the rows, the
  card against the caption band). Deterministic, no seed used.
- projects/bookstack/manifest.json: L 20 cm, t 3 cm, five books, steps
  equal 4.44 x 5 and shrinking 1.9 / 2.4 / 3.2 / 4.9 / 9.8 cm (as
  decimal strings, read as exact fractions), g 9.807, grip 0.3 (0.5 for
  the variant), steps_per_second 100000, slow 2, cycle 10 s,
  first_cycle_at -4.8 (was -0.6, changed for the payoff timing, see
  Deviations), lands 1 to 5 s, slide 0.6 s, reset fade 0.5 s, 2000 px
  per metre, table top 470, edge x 470, title_until 3.0, payoff_t 30.3
  (set from timing.log), music_seed 122, voice_offset 0.6, overlay
  "five 20 cm books | no seed".
- sims/bookstack/bookstack.py, one change after the voice: the
  schedule line now names what moves on the first frame for any phase
  (the sliding book and the equal stack's fall) and asserts that
  something moves; no drawing code changed.
- Smoke frames viewed before the full render (media/bookstack/smoke-*.png
  at 0.0, 1.5, 3.6, 3.9, 4.2, 4.6, 6.0, 9.15, 33.5 s): book 1 sliding in
  on both bands on the first frame under the three-row title; at 3.6 s
  the equal stack starting to tip with the gold triangle 1.10 cm past
  the edge, "balance 1.10 cm past the edge" in gold and "equal: falls at
  book 4" lit; at 3.9 and 4.2 s the four books rotating and sliding off
  the corner and dropping out of the band; at 4.6 s the shrinking stack
  complete, the gold bracket over the 2.2 cm gap, the overhang line to
  22.2 cm and "shrinking: holds, 2.2 cm past the table" lit; 9.15 s mid
  crossfade; 33.5 s the card. One fix from the smoke pass: the overhang
  line of the last landed book was drawn through the next sliding book;
  it is now hidden while a book slides. Smoke frames at the new phase
  (smoke-0.0.png and smoke-30.9.png): frame 0 shows the equal stack
  falling past the edge and the shrinking book 5 two thirds through its
  slide under the title; 30.9 s shows the full shrinking stack with the
  gold 2.2 cm bracket, both event rows lit and the card nearly full.
- Full render (re-rendered 11:07 at first_cycle_at -4.8 and payoff_t
  30.3; the card is in the footage): media/bookstack/render.log: loop
  check 0 px (max channel difference 0), periodicity 0 px, loop step
  27009 px (the first frame is now mid-motion: falling books and a
  sliding book); footage.mp4 h264 1080x1920 60/1, 2400 frames,
  40.000000 s.
- First TTS attempt (10:32 to 11:01): the local Piper TTS on port 10303
  answered every request with HTTP 503
  {"error":{"code":"backend_unavailable"}}; the orchestrator restarted
  it at 11:03 and the work resumed at 11:04.
- Hook pre-tests (media/bookstack/hooks/pretest.log, one take each at
  11:04): hook1 "Can a stack of books hold the top one completely past
  the table? Five books, the same table edge." ok (5.34 s); hook2 "...
  Five books, one table." ok (5.02 s); hook3 "... Try it with five
  books." ok (4.78 s); hook4 "... Same five books, same edge." ok (5.14
  s). The question is the first sentence of every hook; speech starts
  0.03 s into the voice (0.63 s of video) in hook1, hook3 and hook4 and
  0.06 s in hook2 (10 ms RMS over 5 percent of peak); hook2's question
  ends at 3.92 s of video (voice-timing.py). Chosen: the hook1 form
  without "the" ("Five books, same table edge.", it echoes the legend
  row), already in narration.txt; the question matches the title and
  the payoff word for word. Word pre-test (hooks/words.txt: two point
  two centimeters, falls at book four, the fourth book goes on, steps,
  balance point, pile, shrink) ok on the first take (25.74 s).
- Narration projects/bookstack/narration.txt, 115 words; the question
  "Can a stack of books hold the top one completely past the table?" is
  the first sentence and is repeated word for word before the payoff.
  Pass 1 failed on "the bottom ones small" (whisper heard "ones" as
  "1"); it became "the bottom steps small" (still 115 words).
- Voice round trip media/bookstack/voice.log: pass 1 error ("ones" ->
  "1"), pass 2 ok (33.599 s) on the reworded text; 2 passes, the
  accepted take matched.
- Timing media/bookstack/timing.log (offset 0.6 s): the question and
  "Five books. Same table edge." 0.60 to 6.15 s; "On top, every step is
  the same. Below, the steps shrink from the top down." 6.15 to 10.83
  s (books 1 to 5 land at 6.20 to 10.20 s on both bands); "The gold
  mark ... balance the books above it," 10.83 to 15.23 s; "so the top
  steps ... until the fourth book takes it past the edge. So," 15.23 to
  23.56 s (the equal stack tips as book 4 lands at 19.20 s); the
  repeated question 23.56 to 27.08 s; "Yes." 27.08 to 27.82 s; "Shrink
  the steps and the top book sits two point two centimeters past the
  table." 27.82 to 32.13 s; "Equal steps fall at book four." 32.13 to
  34.20 s; the voice ends at 34.20 s of video. Word timestamps of the
  payoff piece (whisper, voice 26.9 to 31.6 s cut): "two point two"
  29.82 to 30.36 s, "centimeters" 30.36 to 31.00 s of video. The
  shrinking book 5 lands at 30.20 s and the card rises from payoff_t
  30.3 s to full at 30.9 s, while "two point two centimeters" is
  spoken; the equal stack tipped at 29.20 s and left the band at 30.22
  s, and its row stays lit through "Equal steps fall at book four";
  the reset crossfade starts at 34.70 s, after the voice ends.
- Compose media/bookstack/compose.log: music seed 122, 40.00 s;
  captions 14 pauses detected, 13 matched, max chunk start shift 0.728
  s against word-count timing; final.mp4 40.000000 s; preview.mp4
  (40.066667 s) and sheet.png written.

### Local QA

- ffprobe final.mp4: h264 1080x1920 at 60/1, aac 22050 Hz mono,
  duration 40.000000 s; atoms ftyp, moov at 32, free, mdat (faststart);
  2876102 bytes; md5 d9c601a403ce3bb4015e90059da282a1.
- Caption and overlay bands: signalstats YMAX of footage.mp4 rows 1440
  to 1530 is 28 and rows 96 to 130 is 28 over all 2400 frames
  (background only).
- Captions: 36 drawtext entries in media/bookstack/captions.filter (the
  first is the overlay "five 20 cm books | no seed"), 35 caption
  chunks; joined, after undoing the drawtext escapes and the
  typographic apostrophe in "pile's", they equal the narration word for
  word (115 words); no two chunks overlap in time; the widest chunk
  "two centimeters past" is 781 px at 64 px with the border (PIL). First
  captions "Can a stack of books" 0.600 to 1.905 s, "hold the top one"
  1.905 to 2.949 s; last "book four." 33.439 to 34.199 s.
- Full-resolution frames viewed (media/bookstack/qa-*.png): 0.00 s
  overlay, three-row title, the equal stack 0.8 s into its fall past the
  edge with "balance 1.10 cm past the edge" in gold and "equal: falls at
  book 4" lit, the shrinking book 5 sliding in, no caption; 1.00 s the
  shrinking stack complete with the gold 2.2 cm bracket and "shrinking:
  holds, 2.2 cm past the table" lit, the equal band empty, caption "Can
  a stack of books"; 2.10 s the same scene, caption "hold the top one";
  9.60 s the equal stack's tip, four books rotated about the corner
  with the gold triangle 1.10 cm past the edge, the shrinking stack at 4
  books, legend and clock rows, caption "shrink from the top"; 10.25 s
  book 5 landed on the shrinking stack, "top book 22.2 cm out", the
  overhang line and the 2.2 cm bracket, both event rows lit, the equal
  band empty; 20.00 s mid video, the equal books falling past the edge
  (second cycle), caption "pile's balance point"; 30.70 s the card
  rising in gold under caption "two centimeters past", the shrinking
  stack complete with its event row lit and the equal row lit; 39.983 s
  identical to frame 0 (title back, no caption, no card). Nothing
  clipped at the frame edge; the event row at y 1400 ends above the
  caption band; the card lines sit under the captions.
- sheet.png (8x5 at 1 fps): 40 cells, the captions in order, books
  building one a second in each cycle, the equal fall at 9, 19 and 29 s,
  the card from 30 s, the reset after 34.7 s under the card, the loop
  closes on the first frame.

### Metadata

- projects/bookstack/metadata.json written by a script with asserts
  (re-checked at 11:10 against the new measure.log after the narration
  and phase change; title and description unchanged, all asserts pass):
  title 99 characters (under 100), description
  3562 characters (under 5,000), ASCII, no angle
  brackets in title or description (the rule is written "d is more than
  L / (n + 1)" in the description), 12 tags; every
  number in the title and description (57 distinct, commas stripped)
  appears in media/bookstack/measure.log.
- Title: Can a stack of books hold the top one completely past the table? Yes, 2.2 cm. Equal falls at book 4
- privacyStatus private, categoryId 27, containsSyntheticMedia true,
  selfDeclaredMadeForKids false.

### Deviations from the brief

- The drawn fall uses the face-frame contact: the table's corner
  touches the bottom book's flat face, so its push is normal to that
  face and the grip needed is the force along the face over the force
  normal to it. The research run (books_tip.py) split the corner force
  into horizontal and vertical table-frame parts, which gives the
  brief's 0.335 s to 51.5 deg (7.56 rad/s) at grip 0.3; the sim
  reproduces those numbers as checks, but in the face frame the corner
  slips earlier, at 0.251 s and 23.8 deg (4.18 rad/s; grip 0.5: 0.279 s,
  31.5 deg). The drawing then slides the body over the corner with
  kinetic grip 0.3 until the corner's push reaches zero at 0.342 s and
  51.5 deg, and lets it fly free. The fall is a drawing model and is not
  narrated; the description gives the face-frame numbers.
- The dashed edge line runs from the table top to 146 px under the band
  top, not to the band top: the label row and the balance readout cross
  x 470.
- The gold event rows sit under the table slab (28 px, 520 px under the
  band top, from x 100), the only free row: the label fills row 40 and
  the readouts rows 84 and 120.
- The clock row reads "one book a second, the fall at 1/2 speed" (the
  scene has no physical clock; the books go on at a fixed pace).
- The gold triangle marks the centre of mass of the books that have
  landed (the book sliding in is held); in the equal band it stays at
  1.10 cm past the edge after the books fall, with the gold readout.
  The shrinking readout shows the whole stack's balance (0.34 cm behind
  the edge after book 5); its worst margin, 0.200 cm at book 3, is in
  the description.
- Payoff card line 5 reads "five-book limit 22.8 cm (137/120 book)" to
  fit 950 px.
- Title "... Yes, 2.2 cm. Equal falls at book 4" (99 characters): the
  question alone is 64 characters.
- The cycle phase moved from first_cycle_at -0.6 to -4.8. With -0.6 the
  shrinking book 5 lands at 4.40, 14.40, 24.40 and 34.40 s, but the
  voice says "two point two centimeters" at 29.82 to 31.00 s and ends at
  34.20 s, so in that cycle book 5 would land after the payoff and the
  2.2 cm gap would not be on screen while it is spoken (the third
  cycle's stack resets at 28.90 to 29.40 s). With -4.8 book 5 lands at
  30.20 s, the card rises from 30.3 s, and the reset waits until 34.70
  s. Cost: the first frame is not book 1 sliding in on both bands but
  the equal stack 0.8 s into its fall and the shrinking book 5 sliding
  in (still motion on frame one, asserted), and the hold with "2.2 cm
  past the table" is on screen from 0.20 to 4.70 s while the question
  is asked.
- Narration: "the bottom ones small" became "the bottom steps small"
  (whisper heard "ones" as "1" in pass 1).

## Niche note

[produced 2026-10-08 as "Can a stack of books hold the top one completely past the table? Yes, 2.2 cm. Equal falls at book 4"; measured equal 4.44 cm margins +5.56 /
+3.34 / +1.12 then -1.10 cm at book 4 (centre 1.10 cm past the edge,
falls), rule d > L / (n + 1) (4.44 holds 3, limit 4.00 for 4),
shrinking 1.9 / 2.4 / 3.2 / 4.9 / 9.8 worst +8.10 / +6.90 / +5.433 /
+3.475 / +0.200 cm (book 3), top 22.20 cm out with its back end 2.20 cm
past the table, limits 137/120 = 22.833 cm (five) and 25/24 = 20.833 cm
(four), drawn fall face frame 0.251 s to 23.8 deg then off the corner
at 0.342 s, 51.5 deg; task 20261008-102540]

## Upload

- Attempt 3 of 5 (quota day 2026-10-08T10:00 EEST) recorded at 2026-10-08T11:42:07+03:00 before scripts/yt-upload.py bookstack; attempts 1 and 2 belong to toast (401 pre-check, then 410 with a stuck stub).
- Attempt 3 failed at 2026-10-08T11:43:02+03:00: insert answered HTTP 401 Invalid Credentials after the pre-check passed; the uploads playlist held no new video. No video created.
- Attempt 4 of 5 recorded at 2026-10-08T13:27:31+03:00 before scripts/yt-upload.py bookstack (one multipart insert, no hidden resend; last probe 5 of 10 rejected).
- Attempt 4 failed at 2026-10-08T13:28:36+03:00: multipart insert answered HTTP 401; no video created.
- Slipped 2026-10-08T13:57:50+03:00: attempt 5 not spent; the final probe at 13:57 read 7 of 10 rejected (rule: fire at 14:00 only at 6 or fewer). final.mp4 (md5 d9c601a403ce3bb4015e90059da282a1) passed every local gate and is ready to upload on the next quota day. Gate: upload (YouTube token service rejecting valid tokens).
