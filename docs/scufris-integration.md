# Agent integration

Seed Zero owns its production policy and workflow. External launchers select
the agent; the repository tells that agent how to run the studio.

## Entry points

The direct launcher is `~/personal/flow/seedzero-produce`. The Scufris
`produce` agent remains an equivalent entry point. Both start Claude with
Fable at xhigh effort and invoke `/daily-production`.

## Skill ownership

- `daily-production` owns the three-short quota day.
- `research-trends` replenishes the backlog when it lacks strong ideas.
- `produce-short` takes one measured claim through local QA.
- `voiceover` generates and verifies narration.
- `upload` records quota use, uploads privately, verifies processing, and
  publishes videos that pass QA.

`AGENTS.md` holds the standing channel, quality, cadence, quota, and publishing
rules. `docs/vision.md` defines the video format. `docs/niche.md` defines the
subject space and backlog.

## Daily execution

Production and local QA may begin before the quota reset. Upload calls wait for
10:00 local, when the YouTube quota day resets. A run started later proceeds
immediately. The workflow targets three public shorts, counts every upload
attempt, and stops at five attempts. Tasks and `web/data/log.jsonl` hold the
evidence used by later runs.
