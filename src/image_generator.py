"""
Image generator for the Cricket Match Weekly Agent.
Renders landscape (X/Twitter) and square (Instagram) shareable images
summarizing the week's key international matches. See src/CLAUDE.md for
the image spec this implements.
"""

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from config.settings import MATCHES_JSON_FILE, OUTPUT_DIR
from src.logger_setup import setup_logger

logger = setup_logger(__name__)

LANDSCAPE_SIZE = (1200, 628)
SQUARE_SIZE = (1080, 1080)

# The image features every match in the next FEATURED_WINDOW_DAYS days
# (today inclusive), capped at MAX_FEATURED_MATCHES so a busy week's rows
# don't shrink to illegible slivers on the fixed-size image.
FEATURED_WINDOW_DAYS = 7
MAX_FEATURED_MATCHES = 15

COLOR_BG = "#0F1729"
COLOR_CARD = "#1B2740"
COLOR_TEXT = "#F4F6FB"
COLOR_SUBTEXT = "#8891A5"
COLOR_ACCENT = "#F2C94C"
COLOR_BADGE_TEXT = "#0B1220"

FORMAT_COLORS = {
    "TEST": "#3B82F6",  # Blue
    "ODI": "#22C55E",   # Green
    "T20": "#EF4444",   # Red
}

PLACEHOLDER_TEAM_NAMES = {"tbc", "tba"}


def load_matches(path=None):
    """Load match dicts from the JSON file main.py writes (matches.json)."""
    path = Path(path or MATCHES_JSON_FILE)
    with open(path) as f:
        return json.load(f)


def select_featured_matches(matches, days_ahead=FEATURED_WINDOW_DAYS, max_count=MAX_FEATURED_MATCHES):
    """
    Feature every match scheduled in the next `days_ahead` days (today
    inclusive), sorted chronologically, capped at max_count for legibility
    on the fixed-size image. Franchise leagues often list playoff/qualifier
    slots as "Tbc vs Tbc" before teams are decided - those are excluded
    unless there are no confirmed matches in the window, in which case
    they're used instead so the image isn't empty.
    """
    def is_confirmed(m):
        return (
            (m.get("home_team") or "").strip().lower() not in PLACEHOLDER_TEAM_NAMES
            and (m.get("away_team") or "").strip().lower() not in PLACEHOLDER_TEAM_NAMES
        )

    def sort_key(m):
        return (m.get("date") or "", m.get("time") or "")

    today = datetime.now(timezone.utc).date()
    cutoff = today + timedelta(days=days_ahead)

    def in_window(m):
        try:
            match_date = datetime.strptime(m.get("date") or "", "%Y-%m-%d").date()
        except ValueError:
            return False
        return today <= match_date <= cutoff

    upcoming = [m for m in matches if in_window(m)]

    confirmed = sorted((m for m in upcoming if is_confirmed(m)), key=sort_key)
    if confirmed:
        return confirmed[:max_count]

    placeholders = sorted((m for m in upcoming if not is_confirmed(m)), key=sort_key)
    return placeholders[:max_count]


def _normalize_format(fmt):
    f = (fmt or "").strip().upper()
    if f.startswith("T20"):
        return "T20"
    if f in ("TEST", "ODI"):
        return f
    return f or "T20"


def _format_date(date_str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").strftime("%a, %d %b")
    except (ValueError, TypeError):
        return date_str or ""


def _text_size(draw, text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def _draw_centered_text(draw, center, text, font, fill):
    w, h = _text_size(draw, text, font)
    draw.text((center[0] - w / 2, center[1] - h / 2), text, font=font, fill=fill)


def _draw_right_aligned_text(draw, top_right, text, font, fill):
    w, _ = _text_size(draw, text, font)
    draw.text((top_right[0] - w, top_right[1]), text, font=font, fill=fill)


def _truncate(draw, text, font, max_width):
    if max_width <= 0 or draw.textlength(text, font=font) <= max_width:
        return text
    ellipsis = "…"
    while text and draw.textlength(text + ellipsis, font=font) > max_width:
        text = text[:-1]
    return (text + ellipsis) if text else ellipsis


def _render(size, matches, week_start, week_end):
    width, height = size
    img = Image.new("RGB", size, COLOR_BG)
    draw = ImageDraw.Draw(img)

    margin = int(width * 0.045)
    header_h = int(height * 0.16)
    footer_h = int(height * 0.04)

    # Pillow's load_default(size=...) embeds its own scalable font data, so
    # this renders identically on a bare CI runner or Docker image with no
    # system fonts installed - no truetype() path to keep in sync.
    title_font = ImageFont.load_default(size=int(height * 0.052))
    subtitle_font = ImageFont.load_default(size=int(height * 0.026))

    draw.text((margin, int(header_h * 0.16)), "THIS WEEK IN CRICKET", font=title_font, fill=COLOR_TEXT)
    draw.text(
        (margin, int(header_h * 0.62)),
        f"{week_start} - {week_end} (UTC)",
        font=subtitle_font,
        fill=COLOR_SUBTEXT,
    )
    draw.rectangle([margin, header_h - 6, margin + int(width * 0.07), header_h - 2], fill=COLOR_ACCENT)

    rows_top = header_h + int(height * 0.02)
    rows_bottom = height - footer_h
    row_gap = int(height * 0.015)
    row_h = (rows_bottom - rows_top - row_gap * (len(matches) - 1)) // len(matches)

    team_font = ImageFont.load_default(size=int(row_h * 0.32))
    meta_font = ImageFont.load_default(size=int(row_h * 0.22))
    badge_font = ImageFont.load_default(size=int(row_h * 0.19))

    for i, match in enumerate(matches):
        y0 = rows_top + i * (row_h + row_gap)
        y1 = y0 + row_h
        draw.rounded_rectangle([margin, y0, width - margin, y1], radius=int(row_h * 0.14), fill=COLOR_CARD)

        pad = int(row_h * 0.12)
        fmt = _normalize_format(match.get("format"))
        badge_color = FORMAT_COLORS.get(fmt, COLOR_SUBTEXT)
        badge_h = int(row_h * 0.5)
        badge_w = int(badge_h * 1.5)
        bx0 = margin + pad
        by0 = y0 + (row_h - badge_h) // 2
        draw.rounded_rectangle(
            [bx0, by0, bx0 + badge_w, by0 + badge_h], radius=int(badge_h * 0.25), fill=badge_color
        )
        _draw_centered_text(draw, (bx0 + badge_w / 2, by0 + badge_h / 2), fmt, badge_font, COLOR_BADGE_TEXT)

        text_x = bx0 + badge_w + pad
        right_edge = width - margin - pad

        date_str = _format_date(match.get("date"))
        time_str = f"{match['time']} UTC" if match.get("time") else ""
        right_block_w = max(_text_size(draw, date_str, meta_font)[0], _text_size(draw, time_str, meta_font)[0])
        team_max_w = right_edge - right_block_w - pad - text_x

        teams = f"{match.get('home_team') or 'TBC'} vs {match.get('away_team') or 'TBC'}"
        draw.text(
            (text_x, y0 + row_h * 0.16),
            _truncate(draw, teams, team_font, team_max_w),
            font=team_font,
            fill=COLOR_TEXT,
        )
        draw.text(
            (text_x, y0 + row_h * 0.58),
            _truncate(draw, match.get("venue") or "", meta_font, team_max_w),
            font=meta_font,
            fill=COLOR_SUBTEXT,
        )

        _draw_right_aligned_text(draw, (right_edge, y0 + row_h * 0.16), date_str, meta_font, COLOR_TEXT)
        _draw_right_aligned_text(draw, (right_edge, y0 + row_h * 0.58), time_str, meta_font, COLOR_SUBTEXT)

    return img


def generate_images(matches=None, output_dir=None):
    """
    Render both the landscape and square images for this week's featured
    matches and save them to output_dir.

    Returns:
        (landscape_path, square_path) tuple, or None if there were no
        matches to feature.
    """
    if matches is None:
        matches = load_matches()

    featured = select_featured_matches(matches)
    if not featured:
        logger.error("No matches available to render - skipping image generation")
        return None

    output_dir = Path(output_dir or OUTPUT_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)

    dates = [m["date"] for m in featured if m.get("date")]
    week_start = _format_date(min(dates)) if dates else ""
    week_end = _format_date(max(dates)) if dates else ""
    week_num = datetime.now(timezone.utc).isocalendar()[1]

    landscape_path = output_dir / f"cricket_matches_week_{week_num:02d}_landscape.png"
    square_path = output_dir / f"cricket_matches_week_{week_num:02d}_square.png"

    _render(LANDSCAPE_SIZE, featured, week_start, week_end).save(landscape_path)
    _render(SQUARE_SIZE, featured, week_start, week_end).save(square_path)

    logger.info(f"Saved landscape image to {landscape_path}")
    logger.info(f"Saved square image to {square_path}")

    return landscape_path, square_path


if __name__ == "__main__":
    result = generate_images()
    exit(0 if result else 1)
