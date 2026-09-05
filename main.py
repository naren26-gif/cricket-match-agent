"""
Cricket Match Weekly Agent - Main Entry Point
Orchestrates: Scrape → Parse → Store
"""

import json
from datetime import datetime

from src.scraper import fetch_matches
from src.parser import filter_international_matches
from src.image_generator import generate_images
from config.settings import MATCHES_JSON_FILE
from src.logger_setup import setup_logger

logger = setup_logger(__name__)


def main():
    """
    Main workflow:
    1. Fetch matches from CricketData.org
    2. Filter for international matches only
    3. Save to JSON file
    4. Generate shareable images (landscape + square)
    """
    
    logger.info("🏏 Cricket Match Agent Starting...")
    
    # Step 1: Fetch matches from CricketData.org
    logger.info("Step 1: Fetching matches from CricketData.org...")
    raw_matches = fetch_matches()
    
    if not raw_matches:
        logger.error("No matches fetched. Aborting.")
        return False
    
    logger.info(f"Step 1 Complete: Found {len(raw_matches)} total matches")
    
    # Step 2: Filter for international matches only
    logger.info("Step 2: Filtering for international matches...")
    filtered_matches = filter_international_matches(raw_matches)
    
    if not filtered_matches:
        logger.warning("No international matches found after filtering.")
    
    logger.info(f"Step 2 Complete: {len(filtered_matches)} international matches")
    
    # Step 3: Save to JSON file
    logger.info("Step 3: Saving matches to JSON...")
    success = save_matches_to_json(filtered_matches)
    
    if not success:
        logger.error("Failed to save matches")
        return False

    logger.info(f"Step 3 Complete: Saved to {MATCHES_JSON_FILE}")

    # Step 4: Generate shareable images (landscape + square) from the
    # matches.json file Step 3 just wrote
    logger.info("Step 4: Generating shareable images...")
    images = generate_images()

    if images:
        landscape_path, square_path = images
        logger.info(f"Step 4 Complete: Generated {landscape_path.name} and {square_path.name}")
    else:
        logger.warning("Step 4: No images generated (no matches to feature)")

    logger.info("🏏 Cricket Match Agent Completed Successfully!")
    return True


def save_matches_to_json(matches):
    """
    Save match list to JSON file
    
    Args:
        matches: List of Match objects
    
    Returns:
        True if successful
    """
    try:
        # Convert Match objects to dictionaries
        matches_data = [
            {
                "match_id": m.match_id,
                "date": m.date,
                "time": m.time,
                "home_team": m.home_team,
                "away_team": m.away_team,
                "format": m.format,
                "venue": m.venue,
                "status": m.status,
            }
            for m in matches
        ]
        
        # Write to JSON file
        with open(MATCHES_JSON_FILE, "w") as f:
            json.dump(matches_data, f, indent=2)
        
        logger.info(f"Saved {len(matches_data)} matches to {MATCHES_JSON_FILE}")
        return True
    
    except Exception as e:
        logger.error(f"Error saving to JSON: {e}")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)