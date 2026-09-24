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
| Default visibility | Private on upload; the agent publishes after its own QA pass (owner authorized 2026-08-30) |
| Comments | On, hold potentially inappropriate for review |
| License | Standard YouTube license |
| Country | Owner's choice |

## Format and cadence

- Vertical 1080x1920, 60 fps, VP9 or H.264 source, 30 to 45 seconds.
- Voice: standalone Piper API, `piper-1`, `en_US-lessac-medium`, with direct whisper.cpp verification.
- Music and sound: procedural, generated in-repo, no licensed audio.
- Cadence: target 3 shorts per quota day, released after the 10:00 local quota
  reset. Quality gates may reduce the day's count.
- Shorts only. Other platforms (TikTok, IG Reels) reuse the same vertical
  file if the owner grants access later. Long form is out of scope.

## Layout

- `docs/` — vision, niche, and channel setup guides.
- `sims/` — deterministic simulation and render code, one folder per short.
- `projects/` — per-video production data: script, manifest, metadata.
- `media/` — rendered output, ignored by git.
- `scripts/` — production helpers (voice-over, music, composition).
- `systemd/` - user service and timer for the daily production run.
- `tasks/` — Tatr-tracked work.
- `web/` - static status page: stats, the video and idea slate, and a work log.
  Data lives in JSON and JSONL under `web/data/`. Run `python -m http.server -d web` to
  preview it locally. Pushes to `master` deploy it to GitHub Pages through
  `.github/workflows/pages.yml`.
- `secrets/` — OAuth credentials for uploads, ignored by git.

## Quickstart

```sh
scripts/voiceover.sh projects/<name>/narration.txt media/<name>/voice.wav
```

The script uses Piper at `http://localhost:10303/v1/audio/speech` and
whisper.cpp at `http://localhost:10301/inference`. Set `TTS_API` or `STT_API`
to override either full endpoint.

## Daily production run

`scripts/seedzero-produce` runs Claude in this repository with Fable at xhigh
effort and invokes `/daily-production`. It streams progress, requires the
final `PRODUCTION_STATUS: COMPLETE` line, and writes each report under
`${XDG_STATE_HOME:-~/.local/state}/automation/seedzero-produce/`.

```sh
scripts/seedzero-produce
scripts/seedzero-produce --open
scripts/seedzero-produce --detach
scripts/seedzero-produce --open-last
scripts/seedzero-produce --logs
```

`--open` runs production, then opens that run's report. `--detach` starts the
run in a transient user service. `--open-last` opens the newest saved
`result.html` without starting a run. `--logs` follows the scheduled
`seedzero-produce.service` with `journalctl --user -fu`. Use only one mode at a
time.

Install the command and enable the 10:00 local systemd timer:

```sh
./install.sh
```

Run the launcher tests with:

```sh
python3 -m unittest scripts/test_seedzero_produce.py
```

## Channel access

The agent needs upload and analytics access to work autonomously. The owner
setup steps are in `docs/channel-setup.md`.
