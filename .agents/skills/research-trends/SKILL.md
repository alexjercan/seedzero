---
name: research-trends
description: Search the web for trends in the simulation-science shorts niche and turn them into measurable idea candidates for the backlog.
---

# Research trends

Find what is trending in and around the niche, then convert it into ideas
that fit the measured-claim format. Research feeds ideas only. Every
narrated claim still comes from a simulation measured in this repo, and no
external media enters a short.

1. **Ground.** Read `docs/niche.md`: pillars, claim style, backlog. Note
   the gaps: pillars with few ideas, formats not yet tried, queued ideas
   that need a stronger angle.
2. **Search.** Use WebSearch, and WebFetch for pages that look
   load-bearing. Useful angles:
   - Trending short-form science and math content: which subjects, hooks,
     and formats win right now.
   - Active channels near the niche (Primer, 3Blue1Brown, physics-sim and
     math-animation accounts): recent subjects and what performed.
   - Fresh pegs: discoveries, anniversaries, dates (pi day), viral debates
     that a simulation can settle with a number.
   - Audience phrasing: the questions people ask about the pillar topics,
     from search suggestions, forums, and comments.
   Keep to roughly five to ten focused queries per run.
3. **Filter.** Keep an idea only if all of these hold:
   - It fits a pillar in `docs/niche.md`, or makes a case for a new one.
   - A deterministic in-repo simulation can render it at 1080x1920.
   - It yields one measurable, surprising number.
   - It needs no external media, licensed assets, or unverifiable claims.
4. **Record.** Append survivors to the backlog in `docs/niche.md` in the
   existing one-line format: the idea, then the measurable surprise to
   expect. If research shows a queued idea is saturated or weak, add a
   short note beside it instead of deleting it.
5. **Evidence.** Record in a Tatr task: the queries, the source URLs, what
   each source showed, and why each idea was accepted or rejected. Append
   a `web/data/log.jsonl` entry. Refresh `web/data/slate.json` if the
   queue changed.

Do not copy scripts, visuals, or branding from other channels. Trends pick
the subject; the measured-claim format is the channel's own.
