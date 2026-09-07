# Produce short: Birthday paradox, your birthday versus any two

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: day9

## Goal

Backlog idea "Birthday paradox: a grid of fifty rooms of twenty three
people fills; count how many rooms hold a shared birthday (expect about
half); ten thousand rooms gives a sharper count." Day nine slate, second
slot, probability pillar dressed in the channel's leading two-panel
"same everything, one difference" format: the same ten thousand rooms,
the same twenty three people, the same birthdays in both panels, and one
question changed. Top: rooms where someone shares your birthday. Bottom:
rooms where any two people share one. People walk into the room one at a
time. Measure both counts after every person, the exact probabilities as
a check, and how many people it takes for a coin flip on your own
birthday, before scripting.

## Claim

Same ten thousand rooms, twenty three people in each, same birthdays,
only the question changes. Rooms where someone shares your birthday:
five hundred sixty nine, under six percent. Rooms where any two people
share a birthday: four thousand nine hundred twenty two, nearly half.
You get twenty two comparisons; any two people make two hundred fifty
three pairs. A coin flip on your own birthday takes two hundred fifty
three people: then four thousand nine hundred eighty six rooms.

## Evidence

### Measurements

`sims/birthday/birthday.py --measure-only` with
`projects/birthday/manifest.json` (seed 0, 10,000 rooms, birthdays
uniform over a 365-day year, one draw of 10,000 x 253 birthdays; person
one is you; the claim reads the first 23 people of every room in both
panels and the top room then keeps filling to 253; numpy RandomState;
log in `media/birthday/measure.log`):

- at 23 people: someone shares yours in 569 rooms = 5.69% (exact
  1 - (364/365)^22 = 5.86%, one standard deviation 0.23 points); any two
  share in 4,922 rooms = 49.22% (exact 50.73%, one standard deviation
  0.50 points); ratio 8.65x
- per person: shares yours 32, 50, 78, 109, 136, 165, 183, 207, 225,
  257, 280, 306, 340, 360, 390, 416, 440, 464, 493, 518, 548, 569 rooms
  at 2..23 people; any two 32, 74, 164, 268, 386, 543, 721, 918, 1,105,
  1,341, 1,587, 1,825, 2,101, 2,391, 2,692, 3,004, 3,295, 3,607, 3,947,
  4,278, 4,608, 4,922, every value within about two standard
  deviations of exact
- comparisons: you against 22 others; any two among 23 makes 253 pairs
- first 100 rooms on screen at 23 people: shares yours 4, any two 53
- the top room keeps filling: 760 rooms at 30 people, 1,250 at 50,
  2,383 at 100, 3,380 at 150, 4,231 at 200, 4,986 at 253 (49.86%, exact
  49.91%); the smallest crowd with an exact chance over 50% that someone
  shares yours is 254 people, against 23 for any two
- featured room 1: nobody shares yours among 23; two pairs share a
  birthday, Mar 29 (persons 14 and 20) and Mar 30 (persons 16 and 22);
  the first pair match arrives with person 20
- check: 100,000 rooms of 23 at seed 1: shares yours 6.00%, any two
  50.65% (exact 5.86% and 50.73%)

### Production

- `sims/birthday/birthday.py` renders two panels on the same room: a
  31 x 12 calendar of 30 px day cells (a ring could not separate the
  featured room's Mar 29 and Mar 30 pairs), people walking in from a door
  one at a time (person j enters at 0.8 + 0.55 j s, all 23 in by 13.3 s),
  a gold "you" dot with an outlined label, lit cells for the panel's
  matches, a 10 x 10 grid of the first 100 rooms lit when the panel's rule
  holds, and the count over all 10,000 rooms after every arrival. The top
  room keeps filling from 27.5 to 35.5 s to 253 people, the "a coin flip
  on yours: 253 people" status appears at 31 s as it is spoken, the
  "23 people: 253 pairs" status at 28 s; payoff at 24 s reads "23 people:
  shares yours 569, any two 4,922"
- narration `projects/birthday/narration.txt`, 100 words; voice round
  trip passed at 37.80 s after a 111-word draft ran 40.05 s; music seed
  25 at gain 0.18
- `scripts/compose.sh birthday`: final.mp4 40.000 s, 1080x1920, 60 fps,
  h264 + aac, faststart, 2.8 MB, mean -15.3 dB, peak -0.0 dB
- inspected: smoke frames at 1, 6, 12, 13.5, 20, 25, 26, 29.5, 29.6 and
  31 s, both contact sheets and full-resolution frames from final.mp4 at
  15.5, 26.0, 33.0, 34.5 and 37.5 s. Fixed before the final render: the
  panel label collided with the people counter (counter moved under the
  label, calendar and texts shifted down), the "you" label was hidden by
  later arrivals (drawn last with an outline), the rush to 253 people
  ran 7 s ahead of its narration (moved from 24.0..29.3 s to
  27.5..35.5 s so 4,986 lands as "Then: four thousand nine hundred eighty
  six" is spoken). Final composite clean: captions sit between the
  panels, 569 and 4,922 are on screen from 13.3 s, well before they are
  spoken at 19 and 22 s

### Published

- Video id: `fMkt_YLUjUA` <https://youtu.be/fMkt_YLUjUA>
- Uploaded private: 2026-09-07 10:01:07 local (07:01:07Z; Pacific quota day
  2026-09-07, clock verified 10:00:19 EEST = 00:00:19 PDT),
  `scripts/yt-upload.py birthday`.
- QA gate against `projects/birthday/metadata.json` after processing
  succeeded: channel `UCWXsZTvrh_OHkzt6v1xkTsw`, uploadStatus processed,
  processingStatus succeeded, no rejection or failure reason, definition
  hd, embeddable, source stream 1080x1920, title, description, tags (as
  a set), categoryId 27, madeForKids false, selfDeclaredMadeForKids
  false, duration PT41S, private before the flip. 15 of 15 checks pass
  on the publish read at 10:02:44; the first read at 10:01:30 found the
  upload still processing (13 of 15). Log in `media/birthday/publish.log`.
- processingHints empty (faststart MP4).
- Made public: 2026-09-07 10:02:46 +03:00 (07:02:46Z) by videos.update on
  status (privacyStatus public, selfDeclaredMadeForKids false,
  containsSyntheticMedia true, embeddable true). The re-read 15 s later
  returned privacyStatus public, madeForKids false,
  selfDeclaredMadeForKids false, embeddable true.

### Quota for 2026-09-07

Shared with the other two day-nine shorts: 4,963 of 10,000 units for the
slate (see task 20260907-084959 for the breakdown). No slot slipped.
