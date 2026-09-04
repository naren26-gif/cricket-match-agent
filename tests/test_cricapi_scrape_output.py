import json

from config.settings import OUTPUT_DIR
from src.parser import filter_international_matches
from src.scraper import CricApiScraper


# Representative records in CricketData.org's (CricAPI) real response shape,
# confirmed against the live /v1/matches endpoint.
SAMPLE_CRICAPI_RECORDS = [
    {
        "id": "match-1001",
        "name": "India vs Pakistan, 3rd ODI, Pakistan tour of India 2026",
        "matchType": "odi",
        "status": "Match starts at 15:30 GMT",
        "venue": "Lahore Stadium",
        "date": "2026-09-25",
        "dateTimeGMT": "2026-09-25T15:30:00",
        "teams": ["India", "Pakistan"],
        "matchStarted": False,
        "matchEnded": False,
    },
    {
        "id": "match-1002",
        "name": "England vs Australia, 2nd Test, Australia tour of England 2026",
        "matchType": "test",
        "status": "Match starts at 09:00 GMT",
        "venue": "Lord's",
        "date": "2026-09-27",
        "dateTimeGMT": "2026-09-27T09:00:00",
        "teams": ["England", "Australia"],
        "matchStarted": False,
        "matchEnded": False,
    },
    {
        "id": "match-1003",
        "name": "Mumbai vs Delhi, Final, Ranji Trophy 2026",
        "matchType": "test",
        "status": "Match starts at 05:00 GMT",
        "venue": "Wankhede Stadium",
        "date": "2026-09-30",
        "dateTimeGMT": "2026-09-30T05:00:00",
        "teams": ["Mumbai", "Delhi"],
        "matchStarted": False,
        "matchEnded": False,
    },
]


def test_map_and_filter_cricapi_records_and_write_output():
    scraper = CricApiScraper()

    matches = [scraper._record_to_match(record) for record in SAMPLE_CRICAPI_RECORDS]
    matches = [m for m in matches if m is not None]
    assert matches, "No matches were mapped from sample CricAPI records."

    filtered_matches = filter_international_matches(matches)
    output_file = OUTPUT_DIR / "cricapi_matches_output.json"

    payload = {
        "source": "sample_fixture",
        "total_matches_parsed": len(matches),
        "total_matches_after_filter": len(filtered_matches),
        "matches": [
            {
                "match_id": match.match_id,
                "date": match.date,
                "time": match.time,
                "home_team": match.home_team,
                "away_team": match.away_team,
                "format": match.format,
                "venue": match.venue,
                "status": match.status,
                "competition": match.competition,
            }
            for match in filtered_matches
        ],
    }

    output_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    assert output_file.exists()
    assert output_file.stat().st_size > 0

    # The Ranji Trophy (domestic first-class) match should be filtered out;
    # the bilateral ODI and Test should survive.
    assert len(payload["matches"]) == 2
    competitions = {m["competition"] for m in payload["matches"]}
    assert "Ranji Trophy 2026" not in competitions
