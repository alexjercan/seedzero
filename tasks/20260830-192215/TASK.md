# Establish Seed Zero channel access

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: backlog

## Goal

Get autonomous upload and analytics access to the Seed Zero channel, scoped
so the agent can never touch the owner's main channel.

## Direction

- The owner follows `docs/channel-setup.md`: Brand Account channel, Google
  Cloud project, OAuth desktop client, production publishing status.
- Blocked on the owner until `secrets/client_secret.json` exists.
- When it exists: write `scripts/yt-auth.py` for the one-time authorization,
  have the owner pick the Seed Zero identity, store `secrets/token.json`.
- Verify scope isolation before first use: call `channels.list(mine=true)`
  and confirm the only returned channel is Seed Zero.
- Until then, use the manual upload packet fallback from the upload skill.

## Acceptance

- `secrets/token.json` exists and refreshes without user action.
- `channels.list(mine=true)` returns exactly the Seed Zero channel.
- A private test upload succeeds and is deleted afterward.
- Quota use per upload is recorded.

## Evidence

### Setup

The owner created the Seed Zero Brand Account channel (handle
`@SeedZeroLab`; `@SeedZero` was taken) and the `seed-zero-agent` Google
Cloud project with YouTube Data API v3 and YouTube Analytics API enabled.
Publishing the OAuth app to production required a homepage and privacy
policy URL; the policy now lives at
<https://alexjercan.github.io/seed-zero-privacy.html> (deployed 2026-08-30
from the owner's site repo). OAuth client is a Desktop app;
`secrets/client_secret.json` and `secrets/token.json` are in place and
ignored by git. `scripts/yt-auth.py` performs the one-time flow and the
isolation check.

### Verification (2026-08-30)

- Token scopes: `youtube`, `youtube.upload`, `yt-analytics.readonly`; a
  refresh succeeded without user action.
- `channels.list(mine=true)` returned exactly one channel: Seed Zero,
  `UCWXsZTvrh_OHkzt6v1xkTsw`, 0 subscribers, 0 videos. The token cannot
  see the owner's main channel.
- Private test upload succeeded (video `MSNufNtDRIs`, status private,
  uploadStatus uploaded) and was deleted; a follow-up lookup returned no
  items.
- Quota per upload cycle: 1,600 units for `videos.insert`, 50 for
  `videos.delete`, 1 per list call, out of 10,000 per day.
