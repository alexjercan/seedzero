# Establish Seed Zero channel access

- STATUS: OPEN
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
