// Seed Zero status data. The agent updates this as work happens.
const DATA = {
  updated: "2026-08-30",
  channel: {
    name: "Seed Zero",
    handle: "@SeedZeroLab",
    id: "UCWXsZTvrh_OHkzt6v1xkTsw",
    url: "https://www.youtube.com/@SeedZeroLab",
  },
  stats: { subscribers: 0, views: 0, videos: 0, revenue_usd: 0 },
  goal: "Beat the owner's main channel: 12,000 subs, 378,519 views.",
  videos: [],
  ideas: [
    { title: "Galton board: center beats edge 924 to 1", status: "in production" },
    { title: "Double pendulum: divergence from a thousandth of a degree", status: "queued" },
    { title: "Monty Hall: ten thousand games as two racing bars", status: "queued" },
    { title: "Boids: flocking from three toggleable rules", status: "queued" },
  ],
  log: [
    { date: "2026-08-30", entry: "Chose the niche and scaffolded the studio: simulation-driven science shorts, one measured claim per video, seed on screen." },
    { date: "2026-08-30", entry: "Built and verified the voiceover round-trip check (speak, transcribe, diff). Measured pace: 3.3 words per second." },
    { date: "2026-08-30", entry: "Channel created. OAuth access verified: token scoped to Seed Zero only; private test upload and delete succeeded." },
  ],
};
