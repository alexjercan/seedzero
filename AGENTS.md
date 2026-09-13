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

## Daily production

- Target 3 public shorts per quota day. Count successful uploads since the
  latest 10:00 local quota reset and produce only the remainder.
- Three uploads cost 4,800 of the 10,000 daily units. Count every attempt,
  including failed and replacement uploads. Hard cap 5 attempts, never 6.
- Production and local QA may run before 10:00. Hold upload calls until the
  quota resets. Runs started after 10:00 may upload as soon as QA passes.
- Upload private, inspect the processed video, then publish immediately after
  it passes. The owner has authorized this release flow.
- Quality beats count. Slip a slot when its claim or render is weak.
- Use the research-trends skill when the backlog lacks enough strong ideas.

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
