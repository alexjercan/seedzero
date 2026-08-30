# Design channel branding

- STATUS: OPEN
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
