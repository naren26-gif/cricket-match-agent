"""
Cricket match data client for CricketData.org (CricAPI)
Fetches international cricket match schedules via JSON API
"""

import time
from typing import List, Optional
from datetime import datetime

import requests

from config.settings import (
    CRICAPI_KEY,
    CRICAPI_MATCHES_URL,
    CRICAPI_CURRENT_MATCHES_URL,
    MAX_PAGES_TO_FETCH,
    REQUEST_TIMEOUT,
    REQUEST_RETRY_ATTEMPTS,
    REQUEST_DELAY,
)
from src.models import Match
from src.logger_setup import setup_logger

logger = setup_logger(__name__)


class CricApiScraper:
    """
    Client for the CricketData.org (CricAPI) JSON API
    Handles pagination, retries, and mapping API records to Match objects
    """

    def __init__(self):
        self.api_key = CRICAPI_KEY
        self.timeout = REQUEST_TIMEOUT
        self.retry_attempts = REQUEST_RETRY_ATTEMPTS
        self.delay = REQUEST_DELAY

        logger.info("CricApiScraper initialized")

    def _get(self, url: str, params: dict) -> Optional[dict]:
        """
        Make a single GET request with retries, and validate the API's own
        success/failure status (CricAPI returns HTTP 200 even on failures,
        e.g. an invalid key or an exhausted daily quota, with the real
        outcome in the JSON body's "status" field).

        Returns:
            The parsed JSON body on success, or None if the request or the
            API call itself failed.
        """
        for attempt in range(1, self.retry_attempts + 1):
            try:
                response = requests.get(url, params=params, timeout=self.timeout)
                response.raise_for_status()
                data = response.json()

                if data.get("status") == "failure":
                    logger.error(f"API error: {data.get('reason', 'unknown reason')}")
                    return None

                return data

            except requests.exceptions.Timeout:
                logger.warning(f"Timeout on attempt {attempt}. Retrying...")
                time.sleep(2 ** attempt)

            except requests.exceptions.ConnectionError as e:
                logger.warning(f"Connection error: {e}. Retrying...")
                time.sleep(2 ** attempt)

            except requests.exceptions.HTTPError as e:
                logger.error(f"HTTP error: {e}")
                return None

            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                return None

        logger.error("All retry attempts exhausted")
        return None

    def _record_to_match(self, record: dict) -> Optional[Match]:
        """
        Map a single CricAPI match record to a Match object

        Returns:
            Match object, or None if the record is missing required fields
        """
        teams = record.get("teams") or []
        if len(teams) < 2:
            return None

        match_type = (record.get("matchType") or "").upper()
        date_time_gmt = record.get("dateTimeGMT")
        if not date_time_gmt:
            return None

        try:
            dt = datetime.strptime(date_time_gmt, "%Y-%m-%dT%H:%M:%S")
        except ValueError:
            logger.warning(f"Could not parse dateTimeGMT '{date_time_gmt}'")
            return None

        if record.get("matchEnded"):
            status = "Completed"
        elif record.get("matchStarted"):
            status = "Live"
        else:
            status = "Upcoming"

        # The API's "name" field is formatted like:
        # "England vs Pakistan, 3rd Test, Pakistan tour of England 2026"
        # The competition is everything after the last comma.
        name_parts = (record.get("name") or "").split(",")
        competition = name_parts[-1].strip() if name_parts else ""

        return Match(
            match_id=str(record.get("id", "")),
            date=dt.strftime("%Y-%m-%d"),
            time=dt.strftime("%H:%M"),
            home_team=teams[0],
            away_team=teams[1],
            format=match_type,
            venue=record.get("venue", "TBA"),
            status=status,
            competition=competition,
        )

    def fetch_all_matches(self) -> List[Match]:
        """
        Main entry point: fetch matches from the API and map them to
        Match objects. Combines the "currently happening" feed with a
        bounded number of pages from the general matches feed.

        Returns:
            List of Match objects (unfiltered - see parser.py for
            international/date-range filtering)
        """
        logger.info("=" * 60)
        logger.info("FETCHING STARTED")
        logger.info("=" * 60)

        if not self.api_key:
            logger.error(
                "CRICAPI_KEY is not set. Add it to a local .env file "
                "(CRICAPI_KEY=...) or pass it as an environment variable."
            )
            return []

        matches: List[Match] = []

        current = self._get(
            CRICAPI_CURRENT_MATCHES_URL, {"apikey": self.api_key, "offset": 0}
        )
        if current:
            for record in current.get("data", []):
                match = self._record_to_match(record)
                if match:
                    matches.append(match)
            time.sleep(self.delay)

        for page in range(MAX_PAGES_TO_FETCH):
            offset = page * 25
            data = self._get(
                CRICAPI_MATCHES_URL, {"apikey": self.api_key, "offset": offset}
            )
            if not data:
                break

            for record in data.get("data", []):
                match = self._record_to_match(record)
                if match:
                    matches.append(match)

            if offset + 25 >= data.get("info", {}).get("totalRows", 0):
                break

            time.sleep(self.delay)

        logger.info("=" * 60)
        logger.info(f"FETCHING COMPLETE: Found {len(matches)} matches")
        logger.info("=" * 60)

        return matches


# ============================================================================
# PUBLIC API (functions other modules call)
# ============================================================================

def fetch_matches() -> List[Match]:
    """
    Fetch all cricket matches from CricketData.org (unfiltered)

    Returns:
        List of Match objects

    Example:
        matches = fetch_matches()
        for match in matches:
            print(match.home_team, "vs", match.away_team)
    """
    scraper = CricApiScraper()
    return scraper.fetch_all_matches()


if __name__ == "__main__":
    # Test the scraper directly
    print("Testing CricApiScraper...")
    matches = fetch_matches()

    print(f"\nFound {len(matches)} matches:")
    for match in matches[:5]:  # Print first 5
        print(f"  {match}")
