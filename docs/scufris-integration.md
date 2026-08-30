# Scufris integration

How the Seed Zero studio plugs into scufris (`~/personal/scufris2`), the
owner's assistant. Everything below cites real scufris mechanisms.

## Decisions (2026-08-30)

- Triggers: adopted. `.scufris.toml` is committed at the repo root with
  `produce`, `analytics`, and `publish` agents; the owner triggers runs by
  asking scufris. Publishing is self-QA (owner authorized): upload private,
  agent QA, then public.
- Scheduled slots: rejected. No systemd timers; the sections below on
  timers are kept as reference only. The owner asks scufris instead.
- Widget: on hold (owner wants no refresh pressure on quotas). Stats
  questions go through the `analytics` agent on demand; Data API reads
  cost ~1 unit each of 10,000/day, and the Analytics API has a separate
  quota pool, so on-demand answering is effectively free.
- A proactive morning briefing is under design; see the follow-up research.

## What scufris is

Scufris is a Pi-based assistant: a background service owns the conversation, a
Linux desktop companion owns voice, windows, and widgets, and a jobs helper
delegates work to Pi or Claude harnesses in owned tmux sessions
(`scufris2/docs/src/dev/architecture.md`). Projects integrate by placing a
`.scufris.toml` menu at their Git root; scufris discovers roots under
`SCUFRIS_PROJECT_ROOTS`, which includes `~/personal`.

## Integration architecture

```text
seedzero                               scufris2
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

seedzero side:

- `web/status.json` writer alongside the existing `web/data.js` habit.
- `scripts/yt-stats.py` (Analytics API pull using `secrets/token.json`).
- `.scufris.toml` with the `produce`, `analytics`, `publish` agents.
- `scripts/produce-slot.sh` plus systemd user timer/service units.

scufris2 side:

- Shipped widget `surfaces/desktop/widgets/seedzero/` and backend
  `surfaces/desktop/backends/seedzero/`, plus the `SCUFRIS_SEEDZERO_STATUS`
  plumbing. Optional interim: the external view-only widget on
  `SCUFRIS_WIDGET_PATH`.

## Morning briefing (designed 2026-08-30, not built)

Findings from scufris2, read-only:

- Scufris has no scheduler, cron, or login hook that reaches Pi. The one
  proactive primitive is the worker-event wake: an extension calls
  `pi.sendMessage(..., { deliverAs: "followUp", triggerTurn: true })`
  (`agent/extensions/scufris/workflow/orchestration.ts:239-254`) and Pi
  runs an unprompted turn. Quick Review completion uses the same path.
- Pi extensions are TypeScript modules under the `pi.extensions` key of
  `scufris2/package.json`: default-export `(pi: ExtensionAPI)`, lifecycle
  via `pi.on("session_start", ...)`, tools via `pi.registerTool`. An
  in-tree `setTimeout` precedent exists (`service/client.ts:150`).
- `surface.sock` accepts synthetic surfaces (protocol v5 hello/message),
  but an injected message is never spoken by the desktop and fabricates a
  user message.

Options, ranked by machinery added:

- **A. Greeted briefing** (skill only): owner says "morning"; a scufris2
  skill tells Pi to read `web/status.json`, optionally run a small
  analytics pull, compare uploads against the cadence target, report, and
  offer to spawn produce/publish jobs. Spoken, zero new mechanisms, but
  needs the one-word prompt.
- **B. Briefing extension** (recommended): a small foreground extension
  `agent/extensions/scufris/briefing.ts` arms one `setTimeout` at
  `session_start` for the configured time (catch-up on late login), checks
  a last-briefing-date state file, then fires the job-event wake with a
  briefing instruction. Unprompted, no polling, lands on all surfaces.
- **C. Synthetic-surface injector**: external process injects a message
  through `surface.sock`; still needs its own scheduler, is never spoken,
  and fakes a user message. Not recommended.

Positions on the open points: trigger is fixed time plus catch-up on
session start, deduped by a state file; the cadence target lives in
`web/status.json` (for example `targets.shorts_per_day`); a live stats
pull inside the briefing is allowed, since reads cost about one quota
unit. Building B later means: `briefing.ts` plus a time setting in
scufris2, and `scripts/yt-stats.py` plus `web/status.json` here.

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
