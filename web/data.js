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
    { date: "2026-08-30", title: "10,000 balls fell. 3 reached the edges.", url: "https://youtu.be/K_ntI_mY4v0", views: 0, note: "private, awaiting owner QA" },
  ],
  ideas: [
    { title: "Galton board: center beats edge 924 to 1", status: "produced" },
    { title: "Double pendulum: divergence from a thousandth of a degree", status: "queued" },
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
  ],
};
