# Unify web videos and ideas

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: backlog

## Scope

Merge the separate video and idea data and UI sections. Reduce page height.

## Decisions

- Use `web/data/slate.json` for both produced videos and future ideas.
- A produced slate entry contains its video URL, date, views, and publication
  status. Future entries need only a title and status.
- Coalesce the two produced idea records with their corresponding video
  records instead of showing duplicates.
- Keep pagination on the unified slate and the work log.

## Evidence

- The unified slate contains 2 produced videos and 3 future idea records.
- Reduced main padding and section spacing, and removed one heading, list, and
  pagination control from the page.
- YouTube Data API refresh at `2026-08-30T21:47:43+03:00` first verified that
  the OAuth token sees exactly one channel: Seed Zero
  (`UCWXsZTvrh_OHkzt6v1xkTsw`).
- API measurements: 1 subscriber and 2 public videos. The pendulum video had 8
  views and the Galton video had 6 views. The channel-level `viewCount` still
  reported 0, so the page uses the measured per-video sum of 14.
- JSON consistency checks, `node --check web/app.js`, and `git diff --check`
  passed.
