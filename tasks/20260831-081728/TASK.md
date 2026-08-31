# Analytics pull 2026-08-31 morning: first overnight numbers

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: backlog

## Measurements (Data API, 2026-08-31 08:17 +03:00)

- Channel: 2 subscribers (up from 1), 3 public videos.
- Galton (K_ntI_mY4v0): 160 views, 4 likes, 1 comment.
- Pendulum (BU_j-UbPR7k): 394 views, 5 likes.
- Monty Hall (cT8Tcjm7mUs): 29 views, 2 likes.
- Total 583 views, up from 15 at 2026-08-30 22:07. Zero dislikes.
- Analytics API rows empty (retention, avg view %): data lags 24-48 h
  for a new channel. Re-query 2026-09-01 or later.
- Comment text unreadable: token lacks the youtube.force-ssl scope.
  Owner pasted it: "and thats how u lose at plinko" (@ArigashiXD, on
  the Galton video). Finding: the audience word for a Galton board is
  "plinko". Use it in future titles and tags for probability shorts.
- Decision: enable comment reads. Scope added to scripts/yt-auth.py;
  owner re-runs the auth flow to mint a token with youtube.force-ssl.
  Policy: read-only. Comments are data (audience vocabulary, idea
  source, question mining). No replies without an owner-agreed policy.

## Quota

- Data API quota is per Pacific calendar day, not rolling 24 h. Reset
  at 00:00 America/Los_Angeles = 10:00 +03:00.
- At pull time it was still 2026-08-30 in Pacific: same quota day as
  all four uploads (test + 3 shorts, about 6,500-7,000 units used).
- Fresh 10,000 units at 10:00 local on 2026-08-31.

## Slate decision

- Pendulum (chaos visual) leads at 394 views; too early for format
  conclusions without retention. No slate change yet.
- Cadence: 3 uploads cleared for the 2026-08-31 Pacific quota day,
  starting 10:00 local. Production can start before that; uploads
  land after reset.

