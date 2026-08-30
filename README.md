# Agent YouTube

> Create your own niche and try to beat my stats!

A YouTube Shorts studio run end to end by an AI agent. The agent picks the
subjects, writes the simulations, renders the footage, speaks the narration,
composes the music, draws the art, and prepares each upload. Every narrated
claim is measured by the same simulation that rendered the footage.

## Niche

**Simulation-driven science shorts.** Each short runs one real, deterministic
simulation and makes one surprising claim about it: probability paradoxes,
chaos, emergence, and algorithms in motion. The claim is never written from
memory. The simulation measures it, the task records the number, and the
narration quotes the measurement. The seed appears on screen, so every video
is reproducible by anyone.

Why this niche fits this agent:

- The footage is code. The agent writes correct, deterministic render code.
- The claims are computable. Accuracy is enforced by assertion, not by vibes.
- The visuals are native to the format: motion, loops, and a payoff frame.
- No camera, no gameplay license, no stock footage, no copyright exposure.

See `docs/niche.md` for pillars, audience notes, and the idea backlog.

## Channel identity

- **Name: Seed Zero**
- Handle: `@SeedZeroLab` (`@SeedZero` was taken at creation time).
- Tagline: "Real simulations. Measured claims. Seed on screen."
- About text: "Every video on this channel is a real, deterministic
  simulation. Every claim you hear was measured from that exact run. The seed
  is on screen, so you can reproduce it. Written, rendered, voiced, and scored
  by an AI agent."
- Avatar and banner: generated in-repo (tracked as a branding task).

## Initial channel settings

| Setting | Value |
| --- | --- |
| Channel type | Brand Account under the owner's Google account |
| Category | Education |
| Default language | English |
| Audience | Not made for kids (channel-level) |
| Altered content disclosure | Yes; the channel is openly AI-made |
| Default visibility | Private on upload; public after final QA pass |
| Comments | On, hold potentially inappropriate for review |
| License | Standard YouTube license |
| Country | Owner's choice |

## Format and cadence

- Vertical 1080x1920, 60 fps, VP9 or H.264 source, 30 to 45 seconds.
- Voice: local speech API, `piper-1`, `en_US-lessac-medium`.
- Music and sound: procedural, generated in-repo, no licensed audio.
- Cadence: 3 shorts per week to start. Adjust from retention data.
- Shorts only. Other platforms (TikTok, IG Reels) reuse the same vertical
  file if the owner grants access later. Long form is out of scope.

## Layout

- `docs/` — vision, niche, and channel setup guides.
- `sims/` — deterministic simulation and render code, one folder per short.
- `projects/` — per-video production data: script, manifest, metadata.
- `media/` — rendered output, ignored by git.
- `scripts/` — production helpers (voice-over, music, composition).
- `tasks/` — Tatr-tracked work.
- `web/` — static status page: stats, videos, ideas, and a work log. Open
  `web/index.html` in a browser; the agent keeps `web/data.js` current.
- `secrets/` — OAuth credentials for uploads, ignored by git.

## Quickstart

```sh
scripts/voiceover.sh projects/<name>/narration.txt media/<name>/voice.wav
```

## Channel access

The agent needs upload and analytics access to work autonomously. The owner
setup steps are in `docs/channel-setup.md`.
