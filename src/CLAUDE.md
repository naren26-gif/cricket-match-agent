# src/ — code conventions

This file is auto-loaded by Claude Code whenever it works on files under
`src/`. See the root `CLAUDE.md` for project-wide objective/status, and
`ARCHITECTURE.md` for the overall pipeline.

## Tech stack
- Python 3.10+
- Scraping: `requests` (CricAPI JSON — no HTML parsing anymore, see root
  `CLAUDE.md` "Current status" for the ESPNCricinfo → CricAPI switch)
- Parsing: `python-dateutil`, optional `pandas`
- Images: `Pillow` (primary), `reportlab` (alt)
- Scheduling: GitHub Actions cron (primary), `schedule`/`APScheduler` as
  local fallback
- Future: `tweepy` (X API), `python-dotenv` for secrets

## Data model
```python
Match:
  match_id: str        # unique identifier
  date: str            # ISO format
  time: str            # UTC
  home_team: str
  away_team: str
  format: str          # TEST / ODI / T20I
  venue: str
  status: str          # upcoming / scheduled / live
  competition: str     # series/tournament name, e.g. "Pakistan tour of
                        # England 2026" or "Indian Premier League 2026" —
                        # needed to tell international matches and major
                        # leagues apart from domestic cricket, since
                        # CricAPI's format field alone (test/odi/t20)
                        # doesn't carry that distinction
```

## Image spec
- Landscape 1200×628px (X), Square 1080×1080px (Instagram) — generate both.
- Show every match in the next 7 days (see `FEATURED_WINDOW_DAYS` in
  `image_generator.py`), capped at 15 matches for legibility on the
  fixed-size image: date, teams, format badge (color-coded: Test=Blue,
  ODI=Green, T20=Red), venue, time (UTC).
- Filename convention: `cricket_matches_week_XX_landscape.png` / `_square.png`.

## Key operational notes
- Check `robots.txt` at the data source before scraping; throttle requests
  2-3 seconds apart; rotate user-agents.
- Store all times in UTC; let viewers interpret locally.
- Manual upload to social media is the MVP — no auto-posting API yet.
- CricAPI returns HTTP 200 even on failures (bad key, quota exhausted) with
  the real outcome in the JSON body's `status` field — `_get()` in
  `scraper.py` checks that explicitly rather than trusting the HTTP status.
- Bilateral/international matches (Test/ODI/T20I nation vs nation) must be
  between two of the current top 15 ICC-ranked nations
  (`TOP_15_ODI_NATIONS` in `config/settings.py`) to pass `parser.py`'s
  filter — see `is_top15_nation_match()`. Franchise T20 leagues (IPL/BBL/
  etc, via `ALLOWED_LEAGUES`) are exempt, since their teams are city/
  franchise sides, not nations. The nations list is a manually maintained
  snapshot (dated in a comment in `settings.py`) of the ICC Men's ODI Team
  Rankings, not a live lookup — update it periodically as rankings shift.
