# Channel setup and agent access

Owner steps to create the Seed Zero channel and give the agent autonomous
upload and analytics access. The agent never touches the main channel.

## 1. Create the channel as a Brand Account

1. Sign in to YouTube with your normal Google account.
2. Settings -> "Add or manage your channel(s)" -> "Create a channel".
3. Name it **Seed Zero** (fallback names in `README.md`).
4. Set the handle: `@SeedZeroLab`.

A Brand Account channel is a separate identity under your Google account.
OAuth below is scoped to this identity only, so the agent's token cannot see
or modify the main channel. This is the isolation guarantee.

In the new channel's settings, set: audience "not made for kids"
(channel-level), category Education, language English.

## 2. Create the Google Cloud OAuth client

1. In <https://console.cloud.google.com> create a new project, for example
   `seed-zero-agent`. Do not reuse a project tied to the main channel.
2. Enable APIs: **YouTube Data API v3** and **YouTube Analytics API**.
3. Configure the OAuth consent screen: External. Add your own email as the
   only test user.
4. Set publishing status to **In production**, not Testing. In Testing,
   refresh tokens expire after seven days and the agent stops working
   weekly. In production the app shows an "unverified" warning during
   consent; for a single-user personal tool that is acceptable, continue via
   "Advanced".
5. Create credentials -> OAuth client ID -> Desktop app. Download the JSON
   as `secrets/client_secret.json` in this repo. `secrets/` is gitignored.

## 3. One-time authorization

When `secrets/client_secret.json` exists, ask the agent to run the auth
flow. It will produce a URL for you to open. Critical step: when Google
shows the account chooser, **pick the Seed Zero brand channel identity, not
your main account identity**. The refresh token is then stored in
`secrets/token.json` and only ever acts as Seed Zero.

Scopes the agent will request:

- `youtube.upload` — upload videos.
- `youtube` — set thumbnails, playlists, and video metadata.
- `yt-analytics.readonly` — read retention and traffic data to steer
  content.

## 4. Known constraints

- **Quota**: 10,000 units per day by default. One upload costs 1,600 units,
  so about six uploads per day maximum. Fine for three shorts per week.
- **Unverified-app private lock**: YouTube can keep videos uploaded through
  an unverified API project locked private until the project passes a
  Google audit. If that happens, the fallback below covers publishing while
  the audit runs. Request the audit from the Cloud console when prompted.
- Verify current policy details when executing this guide; Google changes
  these flows often.

## 5. Fallback while access is pending

The agent can produce complete upload packets without any credentials:

- `media/<name>/final.mp4` — the finished short.
- `projects/<name>/metadata.json` — title, description, tags, category,
  visibility, and the disclosure flag.

You drag the file into YouTube Studio and paste the metadata. Ten minutes a
week, and production is not blocked on OAuth.

## 6. What the agent does once access exists

- Uploads on the agreed cadence, private first, public after QA.
- Sets title, description, tags, and thumbnail from the tracked metadata.
- Reads analytics weekly: swipe-away rate, average percentage viewed,
  replays. Records findings in task evidence and adjusts the slate.
- Never operates on any channel other than Seed Zero.
