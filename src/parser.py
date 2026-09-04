"""
Data parser and filter for cricket matches
Cleans, validates, and filters match data
"""

from typing import List
from datetime import datetime

from config.settings import ALLOWED_FORMATS, ALLOWED_LEAGUES, EXCLUDE_KEYWORDS, DAYS_AHEAD
from src.models import Match
from src.logger_setup import setup_logger

logger = setup_logger(__name__)


class MatchFilter:
    """
    Filters and validates cricket match data
    Ensures only international matches are included
    """
    
    def __init__(self):
        """Initialize the filter with settings"""
        self.allowed_formats = ALLOWED_FORMATS
        self.allowed_leagues = ALLOWED_LEAGUES
        self.exclude_keywords = EXCLUDE_KEYWORDS
        self.days_ahead = DAYS_AHEAD

        logger.info("MatchFilter initialized")
    
    def is_international_format(self, format_str: str) -> bool:
        """
        Check if the format is international (not county/domestic)
        
        Args:
            format_str: Match format (e.g., "ODI", "Test", "T20I")
        
        Returns:
            True if international, False otherwise
        """
        # Normalize format string
        format_normalized = format_str.upper().strip()
        
        # Check if it's in our allowed list
        for allowed in self.allowed_formats:
            if allowed in format_normalized:
                return True
        
        return False
    
    def is_international_scope(self, match: Match) -> bool:
        """
        Check if a match is in scope: international (Test/ODI/T20I) or a
        major T20 league, and not women's/youth/domestic cricket.

        Args:
            match: Match object (uses competition, home_team, away_team)

        Returns:
            True if in scope, False otherwise
        """
        haystack = f"{match.competition} {match.home_team} {match.away_team}".lower()

        # Reject women's, youth, domestic first-class/List A, warm-ups, etc.
        for keyword in self.exclude_keywords:
            if keyword.lower() in haystack:
                logger.debug(f"Excluding '{match.competition}' (contains '{keyword}')")
                return False

        # Test/ODI matches that survive the exclude list are international
        if match.format.upper() in ("TEST", "ODI"):
            return True

        # T20 matches must be either a recognized major league, or a
        # bilateral international tour, to be considered in scope
        competition_lower = match.competition.lower()
        is_major_league = any(
            league.lower() in competition_lower for league in self.allowed_leagues
        )
        is_bilateral_tour = "tour of" in competition_lower

        if not (is_major_league or is_bilateral_tour):
            logger.debug(f"Excluding domestic T20 league '{match.competition}'")
            return False

        return True
    
    def is_within_date_range(self, date_str: str) -> bool:
        """
        Check if match date is within the next N days
        
        Args:
            date_str: Date in format YYYY-MM-DD
        
        Returns:
            True if match is within date range
        """
        try:
            match_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            today = datetime.now().date()
            days_diff = (match_date - today).days
            
            # Include if within date range
            if 0 <= days_diff <= self.days_ahead:
                return True
            
            return False
        
        except ValueError:
            logger.warning(f"Invalid date format: {date_str}")
            return False
    
    def is_valid_match(self, match: Match) -> bool:
        """
        Validate if a match meets all criteria
        
        Args:
            match: Match object to validate
        
        Returns:
            True if match is valid and should be included
        """
        # Check format
        if not self.is_international_format(match.format):
            logger.debug(f"Rejecting match (format): {match}")
            return False

        # Check international/major-league scope
        if not self.is_international_scope(match):
            logger.debug(f"Rejecting match (scope): {match}")
            return False
        
        # Check date range
        if not self.is_within_date_range(match.date):
            logger.debug(f"Rejecting match (date range): {match}")
            return False
        
        # Check for missing data
        if match.home_team == "Unknown" or match.away_team == "Unknown":
            logger.warning(f"Rejecting match (missing teams): {match}")
            return False
        
        return True
    
    def filter_matches(self, matches: List[Match]) -> List[Match]:
        """
        Filter a list of matches based on criteria
        
        Args:
            matches: List of Match objects
        
        Returns:
            Filtered list of Match objects (only international)
        """
        logger.info(f"Filtering {len(matches)} matches...")
        
        valid_matches = [m for m in matches if self.is_valid_match(m)]
        
        logger.info(f"After filtering: {len(valid_matches)} matches")
        logger.info(f"Excluded: {len(matches) - len(valid_matches)} matches")
        
        return valid_matches
    
    def remove_duplicates(self, matches: List[Match]) -> List[Match]:
        """
        Remove duplicate matches (same match_id)
        
        Args:
            matches: List of Match objects
        
        Returns:
            List without duplicates
        """
        seen = set()
        unique_matches = []
        
        for match in matches:
            if match.match_id not in seen:
                unique_matches.append(match)
                seen.add(match.match_id)
        
        if len(unique_matches) < len(matches):
            logger.info(f"Removed {len(matches) - len(unique_matches)} duplicate matches")
        
        return unique_matches
    
    def sort_by_date(self, matches: List[Match]) -> List[Match]:
        """
        Sort matches chronologically (earliest first)
        
        Args:
            matches: List of Match objects
        
        Returns:
            Sorted list
        """
        try:
            return sorted(matches, key=lambda m: (m.date, m.time))
        except Exception as e:
            logger.warning(f"Error sorting matches: {e}")
            return matches


# ============================================================================
# PUBLIC API
# ============================================================================

def filter_international_matches(matches: List[Match]) -> List[Match]:
    """
    Filter and validate matches (main entry point)
    
    Args:
        matches: Raw list of Match objects from scraper
    
    Returns:
        Cleaned, filtered, sorted list of international matches
    """
    logger.info("Starting match filtering pipeline")
    
    filter_obj = MatchFilter()
    
    # Step 1: Remove duplicates
    matches = filter_obj.remove_duplicates(matches)
    
    # Step 2: Filter for international matches only
    matches = filter_obj.filter_matches(matches)
    
    # Step 3: Sort by date
    matches = filter_obj.sort_by_date(matches)
    
    logger.info(f"Filtering complete. Final count: {len(matches)} matches")
    
    return matches


if __name__ == "__main__":
    # Test the filter
    print("Testing MatchFilter...")
    
    # Create sample matches
    test_matches = [
        Match(
            match_id="1", date="2024-09-25", time="15:30",
            home_team="India", away_team="Pakistan",
            format="ODI", venue="Lahore", status="Upcoming",
            competition="Pakistan tour of India 2024"
        ),
        Match(
            match_id="2", date="2024-09-26", time="09:00",
            home_team="England", away_team="West Indies",
            format="Test", venue="Old Trafford", status="Upcoming",
            competition="West Indies tour of England 2024"
        ),
    ]
    
    filtered = filter_international_matches(test_matches)
    print(f"Filtered matches: {len(filtered)}")
    for match in filtered:
        print(f"  {match}")