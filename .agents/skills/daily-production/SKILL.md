---
name: daily-production
description: Produce, QA, upload, and publish today's Seed Zero slate.
---

# Run today's studio

Own the daily batch from selection through publication. Follow `AGENTS.md` and
read `docs/vision.md`, `docs/niche.md`, `web/data/status.json`,
`web/data/slate.json`, and entries since the latest quota boundary in
`web/data/log.jsonl` first.

1. **Quota.** The quota day begins at 10:00 local. Count every upload attempt
   recorded since the latest boundary. The target is three successful uploads;
   the hard cap is five attempts. Stop when the records are unclear or another
   upload could cross the cap.
2. **Slate.** Count shorts already published in this quota day and select only
   enough ideas to reach three. Prefer strong backlog ideas supported by recent
   channel results. Use `/research-trends` when fewer than three strong ideas
   are available.
3. **Produce.** Run `/produce-short` separately for each selected idea. Keep one
   Tatr task per short. Finish measurement, render, voice, composition, local
   QA, metadata, and evidence before any upload.
4. **Gate.** When local QA finishes before 10:00, wait until 10:00. After the
   boundary, recheck the attempt count before each upload.
5. **Release.** Run `/upload` for each approved short. Upload private, wait for
   YouTube processing, inspect the processed result, and publish immediately
   when it passes. Record the attempt before starting the next upload.
6. **Close.** Close each video's task after its publication evidence is stored.
   Refresh `web/data/status.json`, `web/data/slate.json`, and the journal. Report
   published videos, slipped slots, quota attempts, and remaining quota.

A weak claim, failed QA, or exhausted budget slips that slot. The daily target
never lowers the quality gate.
