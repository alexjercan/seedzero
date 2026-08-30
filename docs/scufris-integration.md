# Scufris integration

How the Seed Zero studio plugs into scufris (`~/personal/scufris2`), the
owner's assistant. Everything below cites real scufris mechanisms.

## What scufris is

Scufris is a Pi-based assistant: a background service owns the conversation, a
Linux desktop companion owns voice, windows, and widgets, and a jobs helper
delegates work to Pi or Claude harnesses in owned tmux sessions
(`scufris2/docs/src/dev/architecture.md`). Projects integrate by placing a
`.scufris.toml` menu at their Git root; scufris discovers roots under
`SCUFRIS_PROJECT_ROOTS`, which includes `~/personal`.

## Integration architecture

```text
agent-youtube                          scufris2
  web/status.json  <-- agent writes --> seedzero backend reads (widget data)
  .scufris.toml    <-- menu ----------> jobs helper spawns claude jobs (triggers)
  systemd user timer -> claude -p /produce-short (scheduled slots)
```

Three pieces: a status file the widget reads, an agent menu scufris spawns
jobs from, and host timers for scheduled slots. Scufris has no scheduler of
its own (none in `scufris2/docs/src/` or `scufris2/nix/`), so slots live in
systemd user timers on this machine.

## The widget

Widget model (`scufris2/docs/src/dev/widgets.md`): a widget is a local view at
`surfaces/desktop/widgets/NAME/{widget.toml,widget.ts}`, opened by a widget
call in the agent's `scufris_final_response`, fed JSON readings by a
deterministic backend under `surfaces/desktop/backends/NAME/`. Contract:
`surfaces/desktop/widgets/widget.d.ts` (mount/update/destroy).

Data flow:

1. This repo gains `web/status.json`, a machine-readable sibling of
   `web/data.js`: channel stats, per-video views, idea queue, recent log
   entries, and a `run` block (slot, phase, PID, started, outcome). The same
   update step that keeps `data.js` current writes both.
2. A new `scripts/yt-stats.py` pulls the YouTube Analytics API with
   `secrets/token.json` (scope `yt-analytics.readonly`, see
   `docs/channel-setup.md`) and refreshes stats in both files. It runs on the
   "pull analytics" trigger and at the start of each scheduled slot.
3. A new shipped scufris widget `seedzero` plus backend
   `surfaces/desktop/backends/seedzero/backend.py` reads `status.json`. Model
   it on the `today` backend: stat the file on a beat, re-read on mtime
   change, one JSON reading per line, `trouble` beside the data. Path via a
   `SCUFRIS_SEEDZERO_STATUS` variable, following the `SCUFRIS_TODAY_COMMAND`
   pattern in `docs/src/reference/environment.md`.

Refresh: the desktop polls the backend at the manifest `cadence` (default
1000 ms); the backend only re-reads on file change, so an idle panel costs one
stat per beat. The owner says "show me seed zero" and Pi opens the exhibit.

Quick first step, no scufris rebuild: an external view-only widget
(`widget.toml` + compiled `widget.js`) on `SCUFRIS_WIDGET_PATH`. External
widgets cannot load new backends, so Pi passes a snapshot of `status.json` in
the call arguments and the panel does not live-refresh. Good for week one;
the shipped widget is the real target.

## Triggers

Exact mechanism: the project agent menu (`scufris2/docs/src/dev/jobs.md`,
example: `~/personal/nova-showcase/.scufris.toml`). Add `.scufris.toml` at
this repo root. Supported harnesses are `pi` and `claude`; Claude jobs run the
normal interactive adapter, so this repo's skills
(`.claude/skills/produce-short`, `upload`, `tatr`, `voiceover`) work.

```toml
[conventions]
keywords = { tracking = "tatr", workspace = "master", base = "master", publishing = "explicit" }

[agents.produce]
description = "Produce the next Seed Zero short end to end."
keywords = { harness = "claude" }

[agents.analytics]
description = "Pull YouTube analytics and refresh web/data.js and web/status.json."
keywords = { harness = "claude" }

[agents.publish]
description = "Publish a pending private video after QA."
keywords = { harness = "claude" }
```

The owner tells Scufris "have seedzero produce the next short". Scufris calls
`scufris_job_spawn` with this entry; the job runs in an owned tmux session in
the project workspace; `working`/`blocked`/`done`/`failed` events wake the
conversation (`docs/src/dev/messaging.md`); the owner steers a live job with
`scufris_job_send`. Job history stays inspectable via
`scufris2/scripts/scufris-jobs` and `$XDG_STATE_HOME/scufris/jobs/`.

## Scheduled production

Mechanism: 2-3 systemd user timers (e.g. 09:00, 14:00, 19:00) run a new
`scripts/produce-slot.sh` in this repo. The script takes a lock file, records
its PID in `status.json` (so it can be stopped by recorded PID), refreshes
analytics, then runs `claude -p "/produce-short"` headless. YouTube quota
allows about six uploads per day (`docs/channel-setup.md`), so 3/day fits.

Quality gate: a slot ships nothing weak. After the measure step, if no claim
in the queue is supported by a strong measured number, the run records
`outcome: slipped` with the reason in `status.json` and the log, and exits
clean. The slot slips; the next timer tries again with a fresh or fixed idea.
Never pad the slot with filler and never bend a number to fit a claim.

Failure handling: the script traps errors and writes
`outcome: failed, reason: ...` to `status.json`; the widget shows the last
outcome and the systemd journal keeps the transcript. One attempt per slot, no
retry storms. Two consecutive failures stop the timers until the owner clears
the state. Uploads stay private on upload per `README.md`; publishing runs
through the `publish` trigger.

Intervention: timer runs are not scufris jobs (the jobs helper pins an owner
Pi session, which a timer does not have). The owner sees the run in the
widget, and can ask Scufris to stop it by the recorded PID or to spawn a
`produce`/`publish` job that takes over interactively.

## What needs building

agent-youtube side:

- `web/status.json` writer alongside the existing `web/data.js` habit.
- `scripts/yt-stats.py` (Analytics API pull using `secrets/token.json`).
- `.scufris.toml` with the `produce`, `analytics`, `publish` agents.
- `scripts/produce-slot.sh` plus systemd user timer/service units.

scufris2 side:

- Shipped widget `surfaces/desktop/widgets/seedzero/` and backend
  `surfaces/desktop/backends/seedzero/`, plus the `SCUFRIS_SEEDZERO_STATUS`
  plumbing. Optional interim: the external view-only widget on
  `SCUFRIS_WIDGET_PATH`.

## Open questions for the owner

1. Widget path: build the shipped widget and backend in scufris2 now, or
   start with the external view-only snapshot widget and upgrade later?
2. Publishing authority: at 2-3 slots per day, does the agent flip private to
   public after its own QA pass, or does every video wait for you? Current
   rules say public only after final QA and publishing stays explicit.
3. Are timer runs outside scufris jobs acceptable, or should we build a small
   surface client that injects a "produce" message through `surface.sock` so
   scheduled runs become steerable scufris jobs?
4. Claude job defaults are `opus` xhigh in scufris; pin a cheaper
   model/thinking in the `.scufris.toml` keywords for routine analytics runs?
5. Cadence ramp: README says 3 shorts per week to start; when does retention
   data justify moving to daily slots?
