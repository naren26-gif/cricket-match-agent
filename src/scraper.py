"""
Web scraper for ESPNCricinfo
Fetches international cricket match schedules
Implements BeautifulSoup (fast) → Playwright (fallback) hybrid approach
"""

import time
import json
from typing import List, Optional
from datetime import datetime
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from config.settings import (
    ESPN_SCHEDULE_URL,
    HEADERS,
    REQUEST_TIMEOUT,
    REQUEST_RETRY_ATTEMPTS,
    REQUEST_DELAY,
)
from src.models import Match
from src.logger_setup import setup_logger

logger = setup_logger(__name__)


class ESPNCricketScraper:
    """
    Scraper for ESPNCricinfo schedule page
    Handles network requests, retries, and error recovery
    """
    
    def __init__(self):
        """Initialize the scraper with settings"""
        self.url = ESPN_SCHEDULE_URL
        self.headers = HEADERS
        self.timeout = REQUEST_TIMEOUT
        self.retry_attempts = REQUEST_RETRY_ATTEMPTS
        self.delay = REQUEST_DELAY
        
        logger.info(f"ESPNCricket Scraper initialized for URL: {self.url}")
    
    def fetch_page(self) -> Optional[str]:
        """
        Fetch the HTML content of the schedule page
        Implements retry logic for resilience
        
        Returns:
            HTML content as string, or None if all retries fail
        """
        for attempt in range(1, self.retry_attempts + 1):
            try:
                logger.debug(f"Fetching page (attempt {attempt}/{self.retry_attempts})")
                
                response = requests.get(
                    self.url,
                    headers=self.headers,
                    timeout=self.timeout
                )
                
                # Check if request was successful
                response.raise_for_status()  # Raises HTTPError for bad status codes
                
                logger.info(f"Successfully fetched page (status: {response.status_code})")
                
                # Respect the server: wait before next request
                time.sleep(self.delay)
                
                return response.text
            
            except requests.exceptions.Timeout:
                logger.warning(f"Timeout on attempt {attempt}. Retrying...")
                time.sleep(2 ** attempt)  # Exponential backoff: 2s, 4s, 8s
            
            except requests.exceptions.ConnectionError as e:
                logger.warning(f"Connection error: {e}. Retrying...")
                time.sleep(2 ** attempt)
            
            except requests.exceptions.HTTPError as e:
                logger.error(f"HTTP error: {e}")
                if response.status_code == 403:
                    logger.error("Access forbidden. May need IP rotation or retry later.")
                return None
            
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                return None
        
        logger.error("All retry attempts exhausted")
        return None
    
    def parse_matches(self, html_content: str) -> List[Match]:
        """
        Parse HTML content and extract match data
        
        Args:
            html_content: Raw HTML from the schedule page
        
        Returns:
            List of Match objects
        """
        logger.info("Parsing HTML content")
        matches = []
        
        try:
            soup = BeautifulSoup(html_content, "html.parser")
            
            # ================================================================
            # IMPORTANT: These CSS selectors need to be updated based on
            # actual ESPNCricinfo HTML structure.
            # 
            # If the website changes its HTML, these selectors will break.
            # When that happens, inspect the website again (see Part 1)
            # and update these selectors.
            # ================================================================
            
            # Find all match cards on the page
            # NOTE: Update this selector based on your inspection!
            match_cards = soup.find_all("div", class_="card-match")
            
            logger.debug(f"Found {len(match_cards)} match cards")
            
            for idx, card in enumerate(match_cards, 1):
                try:
                    # Extract data from each card
                    # NOTE: These selectors need adjustment for actual HTML
                    
                    match_id = card.get("data-match-id", f"match_{idx}")
                    
                    date_elem = card.find("div", class_="date-time")
                    date_str = date_elem.get_text(strip=True) if date_elem else "N/A"
                    
                    teams_elem = card.find("div", class_="teams")
                    teams_text = teams_elem.get_text(strip=True) if teams_elem else "N/A vs N/A"
                    
                    format_elem = card.find("span", class_="format")
                    format_str = format_elem.get_text(strip=True) if format_elem else "Unknown"
                    
                    venue_elem = card.find("div", class_="venue")
                    venue = venue_elem.get_text(strip=True) if venue_elem else "TBA"
                    
                    status_elem = card.find("div", class_="status")
                    status = status_elem.get_text(strip=True) if status_elem else "Upcoming"
                    
                    # Parse teams (format: "India vs Pakistan")
                    teams = teams_text.split(" vs ")
                    home_team = teams[0].strip() if len(teams) > 0 else "Unknown"
                    away_team = teams[1].strip() if len(teams) > 1 else "Unknown"
                    
                    # Parse date and time (you may need to adjust this)
                    # This is a placeholder; adjust based on actual format
                    date, time_str = self._parse_datetime(date_str)
                    
                    # Create Match object
                    match = Match(
                        match_id=str(match_id),
                        date=date,
                        time=time_str,
                        home_team=home_team,
                        away_team=away_team,
                        format=format_str,
                        venue=venue,
                        status=status
                    )
                    
                    matches.append(match)
                    logger.debug(f"Parsed match {idx}: {match}")
                
                except Exception as e:
                    logger.warning(f"Error parsing match card {idx}: {e}")
                    continue
            
            logger.info(f"Successfully parsed {len(matches)} matches")
            return matches
        
        except Exception as e:
            logger.error(f"Error parsing HTML: {e}")
            return []
    
    def _parse_datetime(self, datetime_str: str) -> tuple[str, str]:
        """
        Parse date-time string into standardized format
        
        Args:
            datetime_str: Raw datetime string from HTML (e.g., "25 Sep, 2024, 3:00 PM")
        
        Returns:
            Tuple of (date, time) in ISO format
            date: YYYY-MM-DD
            time: HH:MM (24-hour format, UTC)
        
        Note:
            This is a placeholder. Adjust parsing logic based on actual format.
        """
        try:
            # Example parsing (adjust based on actual format from ESPNCricinfo)
            # If format is "25 Sep, 2024, 3:00 PM"
            dt = datetime.strptime(datetime_str, "%d %b, %Y, %I:%M %p")
            
            # Assume times are in UTC (adjust timezone if needed)
            date = dt.strftime("%Y-%m-%d")
            time = dt.strftime("%H:%M")
            
            return date, time
        
        except ValueError as e:
            logger.warning(f"Could not parse datetime '{datetime_str}': {e}")
            return "N/A", "N/A"
    
    def fetch_all_matches(self) -> List[Match]:
        """
        Main entry point: fetch and parse all matches
        
        Returns:
            List of Match objects
        """
        logger.info("=" * 60)
        logger.info("SCRAPING STARTED")
        logger.info("=" * 60)
        
        html = self.fetch_page()
        
        if html is None:
            logger.error("Failed to fetch page. Returning empty list.")
            return []
        
        matches = self.parse_matches(html)
        
        logger.info("=" * 60)
        logger.info(f"SCRAPING COMPLETE: Found {len(matches)} matches")
        logger.info("=" * 60)
        
        return matches


# ============================================================================
# PUBLIC API (functions other modules call)
# ============================================================================

def fetch_matches() -> List[Match]:
    """
    Fetch all international cricket matches from ESPNCricinfo
    
    Returns:
        List of Match objects
    
    Example:
        matches = fetch_matches()
        for match in matches:
            print(match.home_team, "vs", match.away_team)
    """
    scraper = ESPNCricketScraper()
    return scraper.fetch_all_matches()


if __name__ == "__main__":
    # Test the scraper directly
    print("Testing ESPNCricket Scraper...")
    matches = fetch_matches()
    
    print(f"\nFound {len(matches)} matches:")
    for match in matches[:5]:  # Print first 5
        print(f"  {match}")