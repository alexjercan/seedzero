# AGENTS.md

Global `~/AGENTS.md` applies.

## Project

- Autonomous YouTube Shorts studio for the Seed Zero channel.
- Simulation and render code lives under `sims/<name>/`. Production data
  lives under `projects/<name>/`. Rendered media lives under `media/<name>/`
  and stays out of git. Upload credentials live under `secrets/` and stay out
  of git.

## Hard rules

- Never touch the owner's main channel or its credentials. This project only
  operates the Seed Zero channel.
- Every narrated claim must come from a number the simulation measured in
  this repo. Record the measurement in the task evidence before scripting.
- Voice-over must pass the round-trip check in `scripts/voiceover.sh`. The
  transcription must match the approved narration text.
- All footage, music, and art are generated in-repo. No external media, no
  licensed assets, no stock.
- Publishing: upload private, then publish after the agent's own QA pass
  (owner authorized 2026-08-30). Never publish work that fails the quality
  gate; slip the slot instead.

## Cadence

- Quality over quantity (owner confirmed 2026-08-30). A strong short that
  slips beats a weak short that ships.
- Up to 3 uploads per day. Hard cap 5, never 6: an upload costs 1600 of
  10,000 daily quota units, and the day must keep room for one QA-failure
  re-upload plus analytics reads.
- Ramp condition: after about two weeks or twenty published shorts, if
  retention data shows which formats work and the backlog holds fifteen or
  more validated ideas, raise to 4-5 per day and spend the extra slots on
  the proven formats.
- Run the research-trends skill about weekly to keep the backlog fed.

## Workflow

- Work on `master` unless the user requests isolation.
- Use Tatr for tracked work. Give each task one scheduling tag: `backlog` at
  priority 0 or the current production tag.
- Keep decisions, measurements, and evidence with the task.
- Use Nix for Python, FFmpeg, and media commands (`nix develop`).
- Renders are deterministic: fixed seeds, versioned manifests, no wall-clock
  or randomness outside the seeded generator. LLMs may draft scripts and
  code but never run inside final composition.
- Inspect rendered output before calling work done. Do not commit media,
  previews, exports, or secrets.
- Keep `web/data/` current: append timestamped JSONL log entries for meaningful
  work, and refresh status and slate data when they change.

## Project references

- Read `docs/vision.md` before changing the production flow.
- Read `docs/niche.md` before choosing or scripting a subject.
- Read `docs/channel-setup.md` before any upload or channel-settings work.
