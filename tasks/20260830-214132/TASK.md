# Normalize web status data files

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: backlog

## Scope

Replace the executable `web/data.js` object with machine-readable data files.
Include times in log dates and paginate videos, ideas, and logs on the status
page.

## Decisions

- Store channel metadata and totals in `web/data/status.json`.
- Store videos and ideas as JSON arrays in separate files.
- Store the append-only work log in `web/data/log.jsonl`.
- Use ISO 8601 timestamps with explicit UTC offsets for log entries.
- Paginate each list in the browser at five items per page. Show newest log
  entries first.
- Use commit author times as the best available timestamps for migrated log
  entries. Entries created in one commit share that commit time.

## Evidence

- Migrated all 2 videos, 5 ideas, and 11 existing log entries without changing
  their content. Added the cleanup as log entry 12.
- `nix develop --command python ...` parsed all three JSON files and all 12
  JSONL records. It also verified that every log timestamp has a timezone.
- `node --check web/app.js` passed.
- A local `python -m http.server` returned all page, script, JSON, and JSONL
  resources over HTTP.
- `git diff --check` passed.
