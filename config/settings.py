"""
Cricket Agent Configuration
Central place for all constants, URLs, and settings
"""

import os
from pathlib import Path

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


# ============================================================================
# WEBSITE & API CONFIGURATION
# ============================================================================

# ESPNCricinfo URLs
ESPN_BASE_URL = "https://www.espncricinfo.com"
ESPN_SCHEDULE_URL = f"{ESPN_BASE_URL}/schedule"

# Headers to mimic a real browser
# Prevents being blocked as a "bot"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Referer": ESPN_BASE_URL,
    "Connection": "keep-alive",
}


# ============================================================================
# SCRAPER SETTINGS
# ============================================================================

# Request timing
REQUEST_TIMEOUT = 10  # seconds - how long to wait for response
REQUEST_RETRY_ATTEMPTS = 3  # how many times to retry on failure
REQUEST_DELAY = 2  # seconds between requests (be respectful to the server)

# Playwright settings (for JS-rendered pages)
PLAYWRIGHT_HEADLESS = True  # Don't show browser window
PLAYWRIGHT_TIMEOUT = 15000  # milliseconds

# Match formats to include
ALLOWED_FORMATS = ["TEST", "ODI", "T20I", "T20L"]  # T20L = T20 League

# Exclude these keywords in venue names (for filtering out club/county cricket)
EXCLUDE_KEYWORDS = ["County", "Domestic", "Provincial", "Club", "Domestic First-Class"]


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