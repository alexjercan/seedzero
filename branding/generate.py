#!/usr/bin/env python3
"""Seed Zero channel branding generator.

Deterministic: fixed constants only, no RNG, no wall clock. SEED = 0.
Run from the repo root:

    nix develop -c python3 branding/generate.py

Outputs (all under branding/):
    avatar.png      800x800  Galton-board mark (pegs over a bell mound)
    avatar-32.png   32x32    legibility check downscale
    banner.png      2048x1152 wordmark + tagline inside the 1235x338 safe area
    banner-safe.png 1235x338 crop of the banner safe area
"""

import math
import os

from PIL import Image, ImageDraw, ImageFont

SEED = 0  # recorded for provenance; no randomness is used

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_PATH = os.environ["SEED_ZERO_FONT"]

# Palette (matches web/index.html)
BG = (11, 14, 18)        # #0b0e12
ACCENT = (92, 200, 165)  # #5cc8a5
TEXT = (216, 222, 230)   # #d8dee6
MUTED = (138, 148, 163)  # #8a94a3
FAINT = (16, 20, 26)     # large faint mound outside the safe area
FAINT2 = (24, 30, 38)    # faint peg dots outside the safe area

TAGLINE = "Real simulations. Measured claims. Seed on screen."

# Galton mark geometry in design units (origin = top peg center).
MARK_ROW_STEP = 85       # vertical distance between peg rows
MARK_COL_STEP = 85       # horizontal distance between pegs in a row
MARK_PEG_R = 36          # peg dot radius
MARK_ROWS = 3            # rows of 1, 2, 3 pegs
MARK_BASE_Y = 415        # mound baseline below top peg center
MARK_MOUND_H = 155       # mound peak height above baseline
MARK_MOUND_HALF_W = 235  # mound half width
MARK_TOP = -MARK_PEG_R
MARK_BOTTOM = MARK_BASE_Y
MARK_H = MARK_BOTTOM - MARK_TOP          # 451
MARK_W = 2 * MARK_MOUND_HALF_W           # 470


def dot(draw, cx, cy, r, color):
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=color)


def mound_polygon(cx, base_y, half_w, height, steps=256):
    """Filled Gaussian mound with a flat baseline."""
    sigma = half_w * 0.36
    pts = []
    for i in range(steps + 1):
        x = cx - half_w + 2.0 * half_w * i / steps
        t = (x - cx) / sigma
        pts.append((x, base_y - height * math.exp(-0.5 * t * t)))
    pts.append((cx + half_w, base_y))
    pts.append((cx - half_w, base_y))
    return pts


def draw_mark(draw, cx, top_y, scale, peg_color, mound_color):
    """Galton mark: triangle of pegs above a bell mound.

    cx = horizontal center, top_y = y of the top peg center.
    """
    s = scale
    for row in range(MARK_ROWS):
        y = top_y + row * MARK_ROW_STEP * s
        n = row + 1
        for k in range(n):
            x = cx + (k - (n - 1) / 2.0) * MARK_COL_STEP * s
            dot(draw, x, y, MARK_PEG_R * s, peg_color)
    draw.polygon(
        mound_polygon(cx, top_y + MARK_BASE_Y * s,
                      MARK_MOUND_HALF_W * s, MARK_MOUND_H * s),
        fill=mound_color,
    )


def make_avatar():
    size, ss = 800, 4
    S = size * ss
    img = Image.new("RGB", (S, S), BG)
    draw = ImageDraw.Draw(img)
    # Center the mark extents in the canvas; stays inside the inscribed circle.
    top_y = ((size - MARK_H) / 2.0 - MARK_TOP) * ss
    draw_mark(draw, S / 2.0, top_y, float(ss), ACCENT, ACCENT)
    avatar = img.resize((size, size), Image.LANCZOS)
    avatar.save(os.path.join(OUT_DIR, "avatar.png"))
    avatar.resize((32, 32), Image.LANCZOS).save(
        os.path.join(OUT_DIR, "avatar-32.png"))


def make_banner():
    w, h, ss = 2048, 1152, 2
    safe_w, safe_h = 1235, 338
    safe_l, safe_t = (w - safe_w) // 2, (h - safe_h) // 2  # 406, 407
    cy = safe_t + safe_h / 2.0                             # 576

    img = Image.new("RGB", (w * ss, h * ss), BG)
    draw = ImageDraw.Draw(img)

    # Faint large-scale motif outside the safe area: a wide mound whose peak
    # sits just under the safe-area bottom edge, and a big peg triangle above.
    draw.polygon(mound_polygon(w / 2.0 * ss, 1170 * ss, 1500 * ss, 430 * ss),
                 fill=FAINT)
    for row in range(3):
        y = (110 + row * 95) * ss
        n = row + 1
        for k in range(n):
            x = (w / 2.0 + (k - (n - 1) / 2.0) * 95) * ss
            dot(draw, x, y, 26 * ss, FAINT2)

    # Safe-area lockup: mini Galton mark + wordmark + tagline, group centered.
    word_font = ImageFont.truetype(FONT_PATH, 120 * ss)
    tag_font = ImageFont.truetype(FONT_PATH, 32 * ss)
    word_bb = word_font.getbbox("Seed Zero")
    tag_bb = tag_font.getbbox(TAGLINE)
    word_w, word_ink_h = word_bb[2] - word_bb[0], word_bb[3] - word_bb[1]
    tag_w, tag_ink_h = tag_bb[2] - tag_bb[0], tag_bb[3] - tag_bb[1]

    mark_scale = 0.42 * ss
    mark_w = MARK_W * mark_scale
    gap = 48 * ss
    line_gap = 34 * ss
    text_w = max(word_w, tag_w)
    group_w = mark_w + gap + text_w
    group_l = (w * ss - group_w) / 2.0

    mark_cx = group_l + mark_w / 2.0
    mark_top_y = cy * ss - MARK_H * mark_scale / 2.0 - MARK_TOP * mark_scale
    draw_mark(draw, mark_cx, mark_top_y, mark_scale, ACCENT, ACCENT)

    text_l = group_l + mark_w + gap
    block_h = word_ink_h + line_gap + tag_ink_h
    block_top = cy * ss - block_h / 2.0
    word_y = block_top - word_bb[1]
    draw.text((text_l, word_y), "Seed", font=word_font, fill=TEXT)
    draw.text((text_l + word_font.getlength("Seed "), word_y), "Zero",
              font=word_font, fill=ACCENT)
    tag_y = block_top + word_ink_h + line_gap - tag_bb[1]
    draw.text((text_l, tag_y), TAGLINE, font=tag_font, fill=MUTED)

    banner = img.resize((w, h), Image.LANCZOS)
    banner.save(os.path.join(OUT_DIR, "banner.png"))
    banner.crop((safe_l, safe_t, safe_l + safe_w, safe_t + safe_h)).save(
        os.path.join(OUT_DIR, "banner-safe.png"))


def main():
    make_avatar()
    make_banner()
    print("seed:", SEED)
    for name in ("avatar.png", "avatar-32.png", "banner.png", "banner-safe.png"):
        with Image.open(os.path.join(OUT_DIR, name)) as im:
            print(f"{name}: {im.width}x{im.height}")


if __name__ == "__main__":
    main()
