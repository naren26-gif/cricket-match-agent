import json

from config.settings import OUTPUT_DIR
from src.parser import filter_international_matches
from src.scraper import ESPNCricketScraper


SAMPLE_ESPN_HTML = """
<html>
  <body>
    <div class="card-match" data-match-id="match-1001">
      <div class="date-time">25 Sep, 2026, 3:00 PM</div>
      <div class="teams">India vs Pakistan</div>
      <span class="format">ODI</span>
      <div class="venue">Lahore Stadium</div>
      <div class="status">Upcoming</div>
    </div>
    <div class="card-match" data-match-id="match-1002">
      <div class="date-time">27 Sep, 2026, 9:00 AM</div>
      <div class="teams">England vs Australia</div>
      <span class="format">Test</span>
      <div class="venue">Lord's</div>
      <div class="status">Upcoming</div>
    </div>
    <div class="card-match" data-match-id="match-1003">
      <div class="date-time">30 Sep, 2026, 5:00 PM</div>
      <div class="teams">County Team A vs County Team B</div>
      <span class="format">County</span>
      <div class="venue">County Ground</div>
      <div class="status">Upcoming</div>
    </div>
  </body>
</html>
"""


def test_scrape_and_parse_espn_schedule_and_write_output():
    scraper = ESPNCricketScraper()

    live_html = scraper.fetch_page()
    html_to_parse = live_html if live_html else SAMPLE_ESPN_HTML
    source = "live_espn" if live_html else "fallback_fixture"

    matches = scraper.parse_matches(html_to_parse)
    assert matches, "No matches were parsed from ESPN-style HTML."

    filtered_matches = filter_international_matches(matches)
    output_file = OUTPUT_DIR / "espn_matches_output.json"

    payload = {
        "source": source,
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
            }
            for match in filtered_matches
        ],
    }

    output_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    assert output_file.exists()
    assert output_file.stat().st_size > 0
    assert len(payload["matches"]) >= 1
