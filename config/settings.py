"""
Cricket Agent Configuration
Central place for all constants, URLs, and settings
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# ============================================================================
# PROJECT PATHS
# ============================================================================

# Root directory of the project
PROJECT_ROOT = Path(__file__).parent.parent
SRC_DIR = PROJECT_ROOT / "src"
OUTPUT_DIR = PROJECT_ROOT / "output"
LOG_DIR = PROJECT_ROOT / "logs"

# Ensure directories exist
OUTPUT_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)

# Load secrets (e.g. CRICAPI_KEY) from a local .env file, if present.
# In Docker/CI, the key is instead injected as a real environment variable
# (e.g. `docker run -e CRICAPI_KEY=...`), so a missing .env file is fine.
load_dotenv(PROJECT_ROOT / ".env")


# ============================================================================
# WEBSITE & API CONFIGURATION
# ============================================================================

# CricketData.org (formerly CricAPI) - JSON API for cricket fixtures.
# ESPNCricinfo was dropped as a source: it sits behind Akamai's WAF/Bot
# Manager, which blocks plain HTTP requests outright (403) and serves stale
# archived content even when a full browser header set gets past the WAF.
CRICAPI_BASE_URL = "https://api.cricapi.com/v1"
CRICAPI_KEY = os.getenv("CRICAPI_KEY")
CRICAPI_MATCHES_URL = f"{CRICAPI_BASE_URL}/matches"
CRICAPI_CURRENT_MATCHES_URL = f"{CRICAPI_BASE_URL}/currentMatches"

# The /matches endpoint returns 25 matches per page, ordered by recent
# activity (not strictly chronological), mixing recently completed and
# upcoming fixtures across ALL series. We page through a bounded number of
# pages and keep only what falls in our date window - this bounds API hits
# (free tier: 100/day) while still catching near-term matches.
MAX_PAGES_TO_FETCH = 8


# ============================================================================
# SCRAPER SETTINGS
# ============================================================================

# Request timing
REQUEST_TIMEOUT = 10  # seconds - how long to wait for response
REQUEST_RETRY_ATTEMPTS = 3  # how many times to retry on failure
REQUEST_DELAY = 2  # seconds between requests (be respectful to the API)

# Match formats to include (matches CricAPI's lowercase `matchType` values:
# "test", "odi", "t20" - compared case-insensitively)
ALLOWED_FORMATS = ["TEST", "ODI", "T20"]

# Major T20 leagues to include (checked against the match's competition/
# series name). Any T20 match NOT in this list and NOT a bilateral
# international ("<Country> tour of <Country>") is treated as a domestic
# league and excluded, per project scope.
ALLOWED_LEAGUES = [
    "Indian Premier League",
    "Big Bash League",
    "Caribbean Premier League",
    "Pakistan Super League",
    "Bangladesh Premier League",
    "Lanka Premier League",
    "SA20",
    "ILT20",
    "Major League Cricket",
    "The Hundred",
]

# Keywords that, if found in the competition/series name or team names,
# exclude a match regardless of format (women's, youth, domestic
# first-class/List A tournaments, warm-up/practice games, "A" tours).
EXCLUDE_KEYWORDS = [
    "Women", "County", "Domestic", "Provincial", "Club",
    "Ranji", "Vijay Hazare", "Syed Mushtaq Ali", "Duleep", "Irani",
    "Buchi Babu", "U19", "Under-19", "Warm-up", "Practice Match",
    "Emerging", "Development", " A tour", "'A' team",
]

# Top 15 nations per the ICC Men's ODI Team Rankings, snapshotted 2026-09-05
# (source: https://en.wikipedia.org/wiki/ICC_Men%27s_ODI_Team_Rankings).
# Applied only to bilateral/international matches (Test/ODI/T20I nation vs
# nation) - NOT to major T20 franchise leagues (IPL/BBL/etc, see
# ALLOWED_LEAGUES above), whose "teams" are city/franchise sides rather than
# nations, so a ranking filter doesn't apply to them.
#
# ICC rankings shift after most series, so this list is a manually
# maintained snapshot, not a live lookup - update it periodically (e.g. from
# the Wikipedia page above, or https://www.icc-cricket.com/rankings/mens/team-rankings/odi).
TOP_15_ODI_NATIONS = [
    "India", "New Zealand", "Australia", "South Africa", "Pakistan",
    "Sri Lanka", "England", "Afghanistan", "Bangladesh", "West Indies",
    "Zimbabwe", "Ireland", "Scotland", "Netherlands", "United States",
]

# Alternate spellings CricAPI (or other sources) may use for a nation in
# TOP_15_ODI_NATIONS, mapped to the canonical name above (compared
# case-insensitively).
NATION_ALIASES = {
    "usa": "united states",
    "united states of america": "united states",
}


# ============================================================================
# DATA STORAGE
# ============================================================================

# Output formats and locations
MATCHES_JSON_FILE = OUTPUT_DIR / "matches.json"
MATCHES_CSV_FILE = OUTPUT_DIR / "matches.csv"

# How many days ahead to fetch
DAYS_AHEAD = 30  # Fetch matches for the next 30 days

# Keep matches from the past (for historical data)
INCLUDE_COMPLETED = False  # Set to True if you want past matches


# ============================================================================
# LOGGING
# ============================================================================

LOG_FILE = LOG_DIR / "scraper.log"
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL

LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


# ============================================================================
# ERROR HANDLING
# ============================================================================

# If scraper fails after retries, use cached data?
USE_CACHED_DATA = True  # Falls back to last successful scrape

# How long to wait before giving up (seconds)
TOTAL_TIMEOUT = 30

# Abort if fewer than N matches found (safety check)
MIN_MATCHES_EXPECTED = 5


# ============================================================================
# ENVIRONMENT VARIABLES (Optional for secrets)
# ============================================================================

# Load from .env file if it exists (for API keys, credentials)
# DO NOT commit .env to Git!
ENVIRONMENT = os.getenv("ENV", "development")  # development or production
DEBUG = ENVIRONMENT == "development"