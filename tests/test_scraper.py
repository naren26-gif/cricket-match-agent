"""
Unit tests for the scraper and parser
"""

import pytest
from datetime import datetime, timedelta

from src.models import Match
from src.parser import MatchFilter


class TestMatchModel:
    """Test the Match data class"""

    def test_match_creation(self):
        """Test creating a Match object"""
        match = Match(
            match_id="1",
            date="2024-09-25",
            time="15:30",
            home_team="India",
            away_team="Pakistan",
            format="ODI",
            venue="Lahore",
            status="Upcoming",
            competition="Pakistan tour of India 2024"
        )

        assert match.home_team == "India"
        assert match.format == "ODI"
        assert str(match) == "India vs Pakistan (ODI) - 2024-09-25 15:30"


class TestMatchFilter:
    """Test the match filtering logic"""

    def test_is_international_format(self):
        """Test format validation"""
        filter_obj = MatchFilter()

        assert filter_obj.is_international_format("ODI") == True
        assert filter_obj.is_international_format("Test") == True
        assert filter_obj.is_international_format("T20") == True
        assert filter_obj.is_international_format("County") == False

    def test_is_international_scope(self):
        """Test international/major-league scope validation"""
        filter_obj = MatchFilter()

        bilateral_odi = Match(
            "1", "2026-09-25", "15:30", "India", "Pakistan",
            "ODI", "Lahore", "Upcoming", "Pakistan tour of India 2024"
        )
        assert filter_obj.is_international_scope(bilateral_odi) == True

        major_league_t20 = Match(
            "2", "2026-09-25", "15:30", "Mumbai Indians", "Chennai Super Kings",
            "T20", "Wankhede Stadium", "Upcoming", "Indian Premier League 2026"
        )
        assert filter_obj.is_international_scope(major_league_t20) == True

        domestic_league_t20 = Match(
            "3", "2026-09-25", "15:30", "West Delhi Lions", "New Delhi Tigers",
            "T20", "Arun Jaitley Stadium", "Upcoming", "Delhi Premier League 2026"
        )
        assert filter_obj.is_international_scope(domestic_league_t20) == False

        womens_odi = Match(
            "4", "2026-09-25", "15:30", "India Women", "Pakistan Women",
            "ODI", "Lahore", "Upcoming", "Pakistan Women tour of India 2024"
        )
        assert filter_obj.is_international_scope(womens_odi) == False

        domestic_first_class = Match(
            "5", "2026-09-25", "15:30", "Mumbai", "Delhi",
            "TEST", "Wankhede Stadium", "Upcoming", "Ranji Trophy 2026"
        )
        assert filter_obj.is_international_scope(domestic_first_class) == False

    def test_is_top15_nation_match(self):
        """Test top-15 ICC-ranked nation validation for bilateral matches"""
        filter_obj = MatchFilter()

        top15_vs_top15 = Match(
            "1", "2026-09-25", "15:30", "India", "Pakistan",
            "ODI", "Lahore", "Upcoming", "Pakistan tour of India 2024"
        )
        assert filter_obj.is_top15_nation_match(top15_vs_top15) == True

        top15_vs_non_top15 = Match(
            "2", "2026-09-25", "15:30", "India", "Nepal",
            "ODI", "Lahore", "Upcoming", "Nepal tour of India 2024"
        )
        assert filter_obj.is_top15_nation_match(top15_vs_non_top15) == False

        # Franchise leagues are exempt from the nation-ranking check - their
        # "teams" are city/franchise sides, not nations.
        major_league_t20 = Match(
            "3", "2026-09-25", "15:30", "Mumbai Indians", "Chennai Super Kings",
            "T20", "Wankhede Stadium", "Upcoming", "Indian Premier League 2026"
        )
        assert filter_obj.is_top15_nation_match(major_league_t20) == True

        # Alias spellings (e.g. "USA" for "United States") should still match
        usa_alias = Match(
            "4", "2026-09-25", "15:30", "India", "USA",
            "ODI", "Lahore", "Upcoming", "USA tour of India 2024"
        )
        assert filter_obj.is_top15_nation_match(usa_alias) == True

    def test_filter_matches(self):
        """Test filtering a list of matches"""
        today = datetime.now().date()
        upcoming_date = (today + timedelta(days=2)).strftime("%Y-%m-%d")
        league_date = (today + timedelta(days=3)).strftime("%Y-%m-%d")

        test_matches = [
            Match(
                "1", upcoming_date, "15:30", "India", "Pakistan",
                "ODI", "Lahore", "Upcoming", "Pakistan tour of India 2026"
            ),
            Match(
                "2", league_date, "09:00", "West Delhi Lions", "New Delhi Tigers",
                "T20", "Arun Jaitley Stadium", "Upcoming", "Delhi Premier League 2026"
            ),
        ]

        filter_obj = MatchFilter()
        filtered = filter_obj.filter_matches(test_matches)

        # Should only keep the international ODI, not the domestic T20 league
        assert len(filtered) == 1
        assert filtered[0].format == "ODI"


# Run tests with: pytest tests/test_scraper.py
