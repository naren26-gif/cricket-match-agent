"""
Data models for cricket matches
Defines the structure of match data
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Match:
    """
    Represents a single cricket match
    
    Attributes:
        match_id: Unique identifier (string or int from ESPNCricinfo)
        date: Match date (ISO format: 2024-09-25)
        time: Match time in UTC (ISO format: 15:30:00)
        home_team: Team playing at home (string)
        away_team: Visiting team (string)
        format: Match format (TEST, ODI, T20I, T20L)
        venue: Stadium name (string)
        status: Match status (Upcoming, Live, Completed)
    """
    
    match_id: str
    date: str  # Format: YYYY-MM-DD
    time: str  # Format: HH:MM (UTC)
    home_team: str
    away_team: str
    format: str  # TEST, ODI, T20I, T20L, or league names
    venue: str
    status: str  # Upcoming, Live, Completed
    
    def __repr__(self):
        """Human-readable representation"""
        return f"{self.home_team} vs {self.away_team} ({self.format}) - {self.date} {self.time}"


# Example usage (you'll create these in scraper):
# match = Match(
#     match_id="1234567",
#     date="2024-09-25",
#     time="15:30",
#     home_team="India",
#     away_team="Pakistan",
#     format="ODI",
#     venue="Lahore Stadium",
#     status="Upcoming"
# )