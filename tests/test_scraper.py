"""
Unit tests for the scraper and parser
"""

import pytest
from datetime import datetime, timedelta

from src.models import Match
from src.scraper import fetch_matches
from src.parser import MatchFilter, filter_international_matches


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
            status="Upcoming"
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
        assert filter_obj.is_international_format("T20I") == True
        assert filter_obj.is_international_format("County") == False
    
    def test_is_international_venue(self):
        """Test venue validation"""
        filter_obj = MatchFilter()
        
        assert filter_obj.is_international_venue("Lahore Stadium") == True
        assert filter_obj.is_international_venue("County Ground") == False
    
    def test_filter_matches(self):
        """Test filtering a list of matches"""
        today = datetime.now().date()
        upcoming_date = (today + timedelta(days=2)).strftime("%Y-%m-%d")
        county_date = (today + timedelta(days=3)).strftime("%Y-%m-%d")

        test_matches = [
            Match("1", upcoming_date, "15:30", "India", "Pakistan", "ODI", "Lahore", "Upcoming"),
            Match("2", county_date, "09:00", "County Team A", "County Team B", "County", "County Ground", "Upcoming"),
        ]

        filter_obj = MatchFilter()
        filtered = filter_obj.filter_matches(test_matches)

        # Should only keep the ODI match
        assert len(filtered) == 1
        assert filtered[0].format == "ODI"


# Run tests with: pytest tests/test_scraper.py