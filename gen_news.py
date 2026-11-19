#!/usr/bin/env python3
"""
gen_news.py – Generates entry.png for news-image-20261119.
A deterministic 1024x1024 "world front page" poster rendering world news
for Thursday 19 November 2026. No random module, no datetime.now() in rendering.
Fonts only from /usr/share/fonts/truetype/dejavu/.
"""

import sys
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

WIDTH = 1024
HEIGHT = 1024
MARGIN = 40

# Masthead configuration
MASTHEAD_HEIGHT = 72

# Color palette – flat, editorial colors
COLOR_BG = (240, 240, 245)
COLOR_MASTHEAD_BG = (30, 30, 55)
COLOR_MASTHEAD_FG = (255, 255, 255)
COLOR_PANEL_BG = (255, 255, 255)
COLOR_PANEL_BORDER = (180, 180, 200)
COLOR_HEADLINE = (30, 30, 60)
COLOR_TEXT = (50, 50, 55)
COLOR_ACCENT = (220, 50, 55)

# Font loading – only DejaVu Sans / Serif from the system font dir
FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")
FONT_BOLD = ImageFont.truetype(str(FONT_DIR / "DejaVuSans-Bold.ttf"), 20)
FONT_BOLD_LARGE = ImageFont.truetype(str(FONT_DIR / "DejaVuSans-Bold.ttf"), 32)
FONT_MEDIUM = ImageFont.truetype(str(FONT_DIR / "DejaVuSans-Bold.ttf"), 16)
FONT_SMALL = ImageFont.truetype(str(FONT_DIR / "DejaVuSans.ttf"), 12)
FONT_SERIF = ImageFont.truetype(str(FONT_DIR / "DejaVuSerif-Bold.ttf"), 28)
FONT_SERITALIC = ImageFont.truetype(str(FONT_DIR / "DejaVuSerif.ttf"), 14)

# Verify fonts loaded
assert FONT_BOLD is not None
assert FONT_BOLD_LARGE is not None
assert FONT_MEDIUM is not None
assert FONT_SMALL is not None
assert FONT_SERIF is not None
assert FONT_SERITALIC is not None

# News panel data: 6 stories for 3x2 grid
# Descriptions rewritten as complete short sentences; "600,000" uses comma
PANELS = [
    {
        "headline": "Trump Meets Xi and Putin at APEC",
        "text": "Historic first trilateral summit in Shenzhen, China.",
    },
    {
        "headline": "ICJ Judgment: Myanmar Rohingya",
        "text": "Landmark ruling in Gambia v Myanmar.",
    },
    {
        "headline": "Odesa Struck by Russian Strikes",
        "text": "Russian missiles kill civilians; Zelensky slams the attack.",
    },
    {
        "headline": "Gulf Intercepts Iranian Drones",
        "text": "Gulf states shoot down Iranian drone fire.",
    },
    {
        "headline": "Nvidia Halts H200 to China",
        "text": "600,000 GPUs stalled amid export controls.",
    },
    {
        "headline": "GTA 6 Launches After 13-Year Wait",
        "text": "Rockstar's blockbuster finally goes on sale.",
    },
]

NUM_PANELS = len(PANELS)  # 6

# Grid layout: 3 columns, 2 rows
NUM_COLS = 3
NUM_ROWS = 2
GAP = 20

# ---------------------------------------------------------------------------
# Helper: wrap text to a maximum width in pixels given a font
# ---------------------------------------------------------------------------

def wrap_text(draw: ImageDraw, text: str, font, max_width: int) -> list[str]:
    """Split *text* into lines such that each line fits within *max_width*."""
    words = text.split()
    lines: list[str] = []
    current: list[str] = []
    for word in words:
        test = " ".join(current + [word])
        _, _, w, _ = draw.textbbox((0, 0), test, font=font)
        if w <= max_width:
            current.append(word)
        else:
            if current:
                lines.append(" ".join(current))
            current = [word]
    if current:
        lines.append(" ".join(current))
    return lines


# ---------------------------------------------------------------------------
# Main composition
# ---------------------------------------------------------------------------

def compose() -> Image.Image:
    """Create and return the 1024x1024 image."""
    img = Image.new("RGB", (WIDTH, HEIGHT), COLOR_BG)
    draw = ImageDraw.Draw(img)

    # ── Masthead bar ──────────────────────────────────────────────────────
    masthead_y0 = MARGIN
    masthead_y1 = MARGIN + MASTHEAD_HEIGHT
    draw.rectangle(
        [MARGIN, masthead_y0, WIDTH - MARGIN, masthead_y1],
        fill=COLOR_MASTHEAD_BG,
    )

    # Masthead text: "THE WORLD" large, "THURSDAY 19 NOVEMBER 2026" smaller below
    headline_font = FONT_BOLD_LARGE
    sub_font = FONT_SERITALIC

    main_text = "THE WORLD"
    sub_text = "THURSDAY 19 NOVEMBER 2026"

    _, _, mw, mh = draw.textbbox((0, 0), main_text, font=headline_font)
    mx = MARGIN + (WIDTH - 2 * MARGIN - mw) // 2
    my = masthead_y0 + (MASTHEAD_HEIGHT - mh) // 2
    draw.text((mx, my), main_text, fill=COLOR_MASTHEAD_FG, font=headline_font)

    _, _, sw, sh = draw.textbbox((0, 0), sub_text, font=sub_font)
    # Add bottom padding so sub_text does not touch the band's bottom edge
    sy = masthead_y1 - sh - 4
    sx = MARGIN + (WIDTH - 2 * MARGIN - sw) // 2
    draw.text((sx, sy), sub_text, fill=COLOR_MASTHEAD_FG, font=sub_font)

    # ── Panel layout ──────────────────────────────────────────────────────
    panel_area_y0 = masthead_y1  # start right below the masthead

    usable_w = WIDTH - 2 * MARGIN
    usable_h = HEIGHT - MARGIN - panel_area_y0

    panel_w = (usable_w - (NUM_COLS - 1) * GAP) // NUM_COLS
    panel_h = (usable_h - (NUM_ROWS - 1) * GAP) // NUM_ROWS

    grid_start_x = MARGIN
    grid_start_y = panel_area_y0

    desc_font = FONT_MEDIUM
    headline_font = FONT_BOLD

    accent_h = 2  # height of accent bar per panel

    for idx, panel in enumerate(PANELS):
        row = idx // NUM_COLS
        col = idx % NUM_COLS

        px = grid_start_x + col * (panel_w + GAP)
        py = grid_start_y + row * (panel_h + GAP)

        # Panel inner area (with padding)
        pad = 12
        inner_x0 = px + pad
        inner_y0 = py + pad
        inner_x1 = px + panel_w - pad
        inner_y1 = py + panel_h - pad
        available_w = panel_w - 2 * pad

        # Panel background – white with a faint border
        draw.rectangle(
            [px, py, px + panel_w, py + panel_h],
            fill=COLOR_PANEL_BG,
            outline=COLOR_PANEL_BORDER,
            width=1,
        )

        # ── Draw headline and description ─────────────────────────────
        headline = panel["headline"]
        text = panel["text"]

        # Wrap both headline and description
        headline_lines = wrap_text(draw, headline, headline_font, available_w)
        desc_lines_raw = wrap_text(draw, text, desc_font, available_w)
        # Take up to 2 description lines
        desc_lines = desc_lines_raw[:2]

        # Compute total headline height
        total_hh = 0
        for ln in headline_lines:
            _, _, _, h = draw.textbbox((0, 0), ln, font=headline_font)
            total_hh += h
        total_hh += 4 * max(0, len(headline_lines) - 1)  # 4px line gaps

        # Compute total description height
        total_dh = 0
        for ln in desc_lines:
            _, _, _, h = draw.textbbox((0, 0), ln, font=desc_font)
            total_dh += h
        total_dh += 6 * max(0, len(desc_lines) - 1)  # 6px gap between two lines

        # Total text block height (headline + gap + description)
        total_block_h = total_hh + 8 + total_dh  # 8px gap between headline and description

        # ── Draw accent bar: 2px tall at bottom of inner area ───────────
        accent_y0 = inner_y1 - accent_h
        draw.rectangle(
            [inner_x0, accent_y0, inner_x1, inner_y1],
            fill=COLOR_ACCENT,
        )

        # Center the text block vertically within the inner area above the accent bar
        text_area_h = inner_y1 - accent_h - inner_y0  # space above accent bar
        start_y = inner_y0 + (text_area_h - total_block_h) // 2
        if start_y < inner_y0:
            start_y = inner_y0
        if start_y + total_block_h > inner_y1 - accent_h:
            start_y = inner_y1 - accent_h - total_block_h

        # Draw headline
        current_y = start_y
        for i, ln in enumerate(headline_lines):
            _, _, lw, lh = draw.textbbox((0, 0), ln, font=headline_font)
            lx = inner_x0 + (available_w - lw) // 2
            draw.text((lx, current_y), ln, fill=COLOR_HEADLINE, font=headline_font)
            current_y += lh
            if i < len(headline_lines) - 1:
                current_y += 4  # 4px gap between headline lines

        # Draw description below headline
        desc_y = current_y + 8  # 8px gap between headline and description
        for i, ln in enumerate(desc_lines):
            _, _, lw, lh = draw.textbbox((0, 0), ln, font=desc_font)
            lx = inner_x0 + (available_w - lw) // 2
            draw.text((lx, desc_y), ln, fill=COLOR_TEXT, font=desc_font)
            desc_y += lh
            if i < len(desc_lines) - 1:
                desc_y += 6  # 6px gap between description lines

    return img


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    """Generate entry.png and write it to the Makefun output directory."""
    img = compose()
    # Save deterministically; no randomness, no timestamps in the image data.
    out_path = Path("entry.png")
    img.save(out_path, format="PNG", optimize=True)
    size = os.path.getsize(out_path)
    print(
        f"Wrote {out_path} ({img.width}x{img.height}, {size} bytes)"
    )

    # Also copy to the Makefun output dir if env var set
    target_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    target_path = Path(target_dir) / "entry.png"
    target_dir_path = Path(target_dir)
    target_dir_path.mkdir(parents=True, exist_ok=True)
    # Copy the same PNG bytes across
    import shutil
    shutil.copy2(str(out_path), str(target_path))
    print(f"Copied to {target_path}")


if __name__ == "__main__":
    main()