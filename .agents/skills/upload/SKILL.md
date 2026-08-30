---
name: upload
description: Publish a finished short to the Seed Zero channel, or produce a manual upload packet while access is pending.
---

# Upload

Operates only on the Seed Zero channel. Never on any other channel.

## With credentials (`secrets/token.json` exists)

Use the YouTube Data API via the Python environment in the dev shell:

- Upload `media/<name>/final.mp4` with `videos.insert`, category Education,
  visibility private, self-declared altered content, metadata from
  `projects/<name>/metadata.json`.
- After the agent's own QA pass of the processed video, flip visibility to
  public (owner authorized self-QA publishing on 2026-08-30).
- One upload costs 1,600 quota units of the 10,000 daily budget.
- Record the video ID and publish time in the task evidence.

## Without credentials

Produce the manual packet instead and tell the owner:

- `media/<name>/final.mp4`
- `projects/<name>/metadata.json`

The owner drags the file into YouTube Studio and pastes the metadata. Setup
steps for full access are in `docs/channel-setup.md`.
