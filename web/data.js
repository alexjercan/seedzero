// Seed Zero status data. The agent updates this as work happens.
const DATA = {
  updated: "2026-08-30",
  channel: {
    name: "Seed Zero",
    handle: "@SeedZeroLab",
    id: "UCWXsZTvrh_OHkzt6v1xkTsw",
    url: "https://www.youtube.com/@SeedZeroLab",
  },
  stats: { subscribers: 0, views: 0, videos: 1, revenue_usd: 0 },
  goal: "Beat the owner's main channel: 12,000 subs, 378,519 views.",
  videos: [
    { date: "2026-08-30", title: "10,000 balls fell. 3 reached the edges.", url: "https://youtu.be/K_ntI_mY4v0", views: 0 },
    { date: "2026-08-30", title: "0.001 degrees apart. Watch them disagree.", url: "https://youtu.be/BU_j-UbPR7k", views: 0, note: "private, awaiting owner QA" },
  ],
  ideas: [
    { title: "Galton board: center beats edge 924 to 1", status: "produced" },
    { title: "Double pendulum: divergence from a thousandth of a degree", status: "produced" },
    { title: "Fourteen more measured-claim ideas", status: "backlog in docs/niche.md" },
    { title: "Monty Hall: ten thousand games as two racing bars", status: "queued" },
    { title: "Boids: flocking from three toggleable rules", status: "queued" },
  ],
  log: [
    { date: "2026-08-30", entry: "Chose the niche and scaffolded the studio: simulation-driven science shorts, one measured claim per video, seed on screen." },
    { date: "2026-08-30", entry: "Built and verified the voiceover round-trip check (speak, transcribe, diff). Measured pace: 3.3 words per second." },
    { date: "2026-08-30", entry: "Channel created. OAuth access verified: token scoped to Seed Zero only; private test upload and delete succeeded." },
    { date: "2026-08-30", entry: "Built the composition pipeline: seeded music, character-budget captions, seed overlay, preview, contact sheet. Deterministic reruns verified." },
    { date: "2026-08-30", entry: "Branding done: deterministic avatar and banner. Banner, description, and keywords set via API; avatar needs a manual Studio upload." },
    { date: "2026-08-30", entry: "First short produced and uploaded private: Galton board, seed 0. Measured 2181 center vs 3 at both edges; theory says 924 paths to 1. Video K_ntI_mY4v0." },
    { date: "2026-08-30", entry: "Owner approved the pilot. First video is PUBLIC. Seed Zero is live." },
    { date: "2026-08-30", entry: "Double pendulum short produced: 110 deg release, 0.001 deg delta, split at 9.8 s, gap wider than the pendulum at 14.9 s. Private as BU_j-UbPR7k." },
    { date: "2026-08-30", entry: "Scufris integration designed: widget from web/status.json, triggers via .scufris.toml claude jobs, 2-3 daily slots via systemd timers. See docs/scufris-integration.md." },
    { date: "2026-08-30", entry: "Day one wrap: two videos public, self-QA publishing authorized, repo renamed to seedzero, scufris triggers committed, morning-briefing extension designed and tasked in scufris2 (20260830-212048). Next: Monty Hall." },
    { date: "2026-08-30", entry: "Added GitHub Pages CI/CD for the status page. Pushes to master now deploy the web folder." },
  ],
};
