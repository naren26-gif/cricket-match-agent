"""
Unit tests for the image generator (Phase 3)
"""

import json
import re
from datetime import datetime, timedelta, timezone

from PIL import Image, ImageDraw, ImageFont

from src.image_generator import (
    LANDSCAPE_SIZE,
    SQUARE_SIZE,
    _format_date,
    _normalize_format,
    _truncate,
    generate_images,
    load_matches,
    select_featured_matches,
)


def _in_days(n):
    return (datetime.now(timezone.utc).date() + timedelta(days=n)).strftime("%Y-%m-%d")


def make_match(**overrides):
    base = {
        "match_id": "1",
        "date": _in_days(4),
        "time": "14:00",
        "home_team": "India",
        "away_team": "Australia",
        "format": "ODI",
        "venue": "Melbourne Cricket Ground",
        "status": "Upcoming",
    }
    base.update(overrides)
    return base


class TestSelectFeaturedMatches:
    def test_filters_out_unconfirmed_placeholder_matches(self):
        matches = [
            make_match(match_id="1", date=_in_days(1)),
            make_match(match_id="2", date=_in_days(2), home_team="Tbc", away_team="Tbc"),
        ]

        result = select_featured_matches(matches)

        assert [m["match_id"] for m in result] == ["1"]

    def test_sorts_chronologically_by_date_then_time(self):
        matches = [
            make_match(match_id="a", date=_in_days(2), time="10:00"),
            make_match(match_id="b", date=_in_days(1), time="23:00"),
            make_match(match_id="c", date=_in_days(1), time="05:00"),
        ]

        result = select_featured_matches(matches)

        assert [m["match_id"] for m in result] == ["c", "b", "a"]

    def test_excludes_matches_outside_the_days_ahead_window(self):
        matches = [
            make_match(match_id="past", date=_in_days(-1)),
            make_match(match_id="today", date=_in_days(0)),
            make_match(match_id="in_range", date=_in_days(7)),
            make_match(match_id="too_far", date=_in_days(8)),
        ]

        result = select_featured_matches(matches, days_ahead=7)

        assert [m["match_id"] for m in result] == ["today", "in_range"]

    def test_caps_at_max_count(self):
        matches = [make_match(match_id=str(i), date=_in_days(i)) for i in range(1, 11)]

        result = select_featured_matches(matches, days_ahead=30, max_count=7)

        assert len(result) == 7

    def test_uses_placeholders_when_no_confirmed_matches_in_window(self):
        matches = [
            make_match(match_id="1", date=_in_days(1), home_team="Tbc", away_team="Tbc"),
            make_match(match_id="2", date=_in_days(2), home_team="Tbc", away_team="Tbc"),
        ]

        result = select_featured_matches(matches)

        # No confirmed matches in the window at all, so placeholders are
        # used rather than returning an empty image.
        assert [m["match_id"] for m in result] == ["1", "2"]

    def test_empty_input_returns_empty(self):
        assert select_featured_matches([]) == []


class TestFormatHelpers:
    def test_normalize_format_variants(self):
        assert _normalize_format("t20") == "T20"
        assert _normalize_format("T20I") == "T20"
        assert _normalize_format("Test") == "TEST"
        assert _normalize_format("odi") == "ODI"
        assert _normalize_format(None) == "T20"
        assert _normalize_format("") == "T20"

    def test_format_date_valid(self):
        assert _format_date("2026-09-09") == "Wed, 09 Sep"

    def test_format_date_invalid_falls_back_to_raw_value(self):
        assert _format_date("not-a-date") == "not-a-date"
        assert _format_date(None) == ""


class TestTruncate:
    def _draw(self):
        return ImageDraw.Draw(Image.new("RGB", (10, 10)))

    def test_short_text_is_unchanged(self):
        draw = self._draw()
        font = ImageFont.load_default(size=20)

        assert _truncate(draw, "Hi", font, 1000) == "Hi"

    def test_long_text_is_truncated_with_ellipsis_and_fits_width(self):
        draw = self._draw()
        font = ImageFont.load_default(size=20)
        long_text = "A very long venue name that will not fit in the row"

        result = _truncate(draw, long_text, font, 50)

        assert result.endswith("…")
        assert draw.textlength(result, font=font) <= 50


class TestLoadMatches:
    def test_loads_matches_from_json_file(self, tmp_path):
        matches_file = tmp_path / "matches.json"
        matches_file.write_text(json.dumps([make_match()]))

        result = load_matches(matches_file)

        assert result == [make_match()]


class TestGenerateImages:
    def test_returns_none_when_no_matches_to_feature(self):
        assert generate_images(matches=[]) is None

    def test_creates_correctly_sized_landscape_and_square_png_files(self, tmp_path):
        matches = [
            make_match(match_id=str(i), date=_in_days(i), format="TEST" if i == 1 else "T20")
            for i in range(1, 6)
        ]

        result = generate_images(matches=matches, output_dir=tmp_path)

        assert result is not None
        landscape_path, square_path = result
        assert landscape_path.exists()
        assert square_path.exists()

        with Image.open(landscape_path) as img:
            assert img.size == LANDSCAPE_SIZE
        with Image.open(square_path) as img:
            assert img.size == SQUARE_SIZE

    def test_filenames_follow_naming_convention(self, tmp_path):
        matches = [make_match(match_id=str(i), date=_in_days(i)) for i in range(1, 6)]

        landscape_path, square_path = generate_images(matches=matches, output_dir=tmp_path)

        assert re.fullmatch(r"cricket_matches_week_\d{2}_landscape\.png", landscape_path.name)
        assert re.fullmatch(r"cricket_matches_week_\d{2}_square\.png", square_path.name)
