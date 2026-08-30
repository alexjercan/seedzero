# Design channel branding

- STATUS: CLOSED
- PRIORITY: 0
- TAGS: backlog

## Goal

Generate the Seed Zero avatar, banner, and description in-repo so the
channel looks intentional from day one.

## Direction

- Avatar: 800x800, readable at 32 pixels. A minimal mark built from the
  niche itself, for example a Galton-board triangle of dots collapsing into
  a bell curve, or a "0" seed glyph. Generate with Python or Inkscape SVG,
  render to PNG, keep the source tracked under `branding/`.
- Banner: 2048x1152 with the safe area (1235x338 centered) carrying the
  tagline "Real simulations. Measured claims. Seed on screen."
- Dark background, one accent color, no gradients that die on compression.
- Deterministic generation, seed recorded, like all other footage.

## Acceptance

- `branding/` holds generated avatar and banner sources plus PNGs sized to
  spec, and the render commands are reproducible.
- Avatar legibility checked at 32x32 by rendering the downscale.
- Owner uploads them or the agent sets them via the API once access exists.

## Evidence

### Generated (2026-08-30)

A parallel agent built `branding/generate.py`, a single deterministic
script (fixed constants, no RNG or clock; reruns are hash-identical):

- `branding/avatar.png` 800x800: a 1-2-3 triangle of accent-green peg dots
  settling into a filled Gaussian mound on `#0b0e12`, inside the inscribed
  circle for YouTube's circular crop.
- `branding/avatar-32.png`: LANCZOS downscale check; dots and mound stay
  distinct at 32 px (peg spacing was widened and the mound fattened after
  the first review pass found the dots fusing).
- `branding/banner.png` 2048x1152 with the wordmark, tagline, and mark
  centered in the 1235x338 safe area; `branding/banner-safe.png` is the
  crop check.

Regenerate with `nix develop -c python3 branding/generate.py`. The parent
session reviewed all four images at full and small size.

### Applied

- Banner uploaded via `channelBanners.insert` and set through
  `channels.update`; channel description and keywords set at the same
  time. Verified live on the channel.
- The avatar cannot be set through the YouTube Data API. Owner action:
  YouTube Studio -> Customization -> Branding -> Picture -> upload
  `branding/avatar.png`.
