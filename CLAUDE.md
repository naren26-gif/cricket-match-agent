# Cricket Match Weekly Agent — Project Context for Claude Code

> This file lives at the root of the `cricket-match-agent` repo. Claude Code
> reads it automatically on every session in this folder, so it always has
> this context without being re-explained.
>
> **Standing rule for Claude Code:** treat this file as the single source of
> truth for this project. Read it at the start of every session. Whenever
> the user gives an instruction meant to apply beyond the current message
> (a preference, a scope rule, a "always/never do X"), add it to
> "Standing instructions from the user" below instead of letting it live
> only in chat history. Keep "Current status" up to date as work lands.

## Who's building this
The user is new to Linux/Unix environments and Claude Code / CLI tooling.
**Always explain setup steps and commands in plain language, 2-3 lines of
reasoning per step, before running them** — treat this like onboarding a
new joiner, not a peer engineer. Don't assume familiarity with git, venvs,
shells, or cron syntax; explain briefly what each does the first time it's used.

## Objective
Automate weekly collection of international cricket matches from
ESPNCricinfo and generate shareable images (landscape for X/Twitter,
square for Instagram). Runs weekly, recommended Tuesday 10:00 AM UTC.

**Scope:** International matches only — Test, ODI, T20I, and major T20
leagues (IPL, BBL, CPL, etc.). Exclude county/club cricket, domestic
leagues (unless specified), youth cricket, and women's cricket (unless
explicitly requested).

## Architecture (pipeline)
```
Scheduled Trigger (GitHub Actions cron)
        ↓
Web Scraper (ESPNCricinfo schedule pages)
        ↓
Data Parser & Filter (international matches only)
        ↓
Image Generator (PIL/Pillow)
        ↓
Store image in repo /output/
        ↓
Manual upload to X & Instagram (MVP) → API integration later
```

## Repo structure to scaffold (Phase 1)
```
cricket-match-agent/
├── src/
│   ├── scraper.py          # ESPNCricinfo web scraper
│   ├── parser.py           # data parsing & filtering
│   ├── image_generator.py  # image creation
│   └── utils.py            # helper functions
├── output/                 # weekly generated images
├── config/
│   └── settings.py         # URLs, constants, config
├── tests/                  # unit tests
├── requirements.txt
├── README.md
├── .gitignore              # venv/, __pycache__/, .env, output/
└── .github/
    └── workflows/
        └── weekly-scrape.yml
```

## Tech stack
- Python 3.10+
- Scraping: `requests`, `beautifulsoup4`, `selenium` or `playwright`, `lxml`
- Parsing: `python-dateutil`, optional `pandas`
- Images: `Pillow` (primary), `reportlab` (alt)
- Scheduling: GitHub Actions cron (primary), `schedule`/`APScheduler` as local fallback
- Future: `tweepy` (X API), `python-dotenv` for secrets
- Testing/quality: `pytest`, `pytest-mock`, `black`, `flake8`, `pylint`

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
```

## Image spec
- Landscape 1200×628px (X), Square 1080×1080px (Instagram) — generate both.
- Show 5-7 key matches: date, teams, format badge (color-coded: Test=Blue,
  ODI=Green, T20=Red), venue, time (UTC).
- Filename convention: `cricket_matches_week_XX_landscape.png` / `_square.png`.

## Key operational notes
- Check `robots.txt` at espncricinfo.com before scraping; throttle requests
  2-3 seconds apart; rotate user-agents.
- Store all times in UTC; let viewers interpret locally.
- Manual upload to social media is the MVP — no auto-posting API yet.
- GitHub Actions free tier (2,000 min/month) is more than sufficient for a
  weekly job.

## Build order (phases)
1. Repo + venv + folder structure + git (this session's starting point)
2. Scraper + parser + data model
3. Image generator (landscape + square templates)
4. GitHub Actions automation (weekly cron)
5. Manual social upload workflow (API integration later, optional)
6. Tests (unit + integration, target >80% coverage)
7. Deploy + monitor

## Current status
_Last updated: 2026-09-04._

Phase 1 (repo/folder structure) and most of Phase 2 (scraper + parser +
data model) are done:
- `src/models.py` — `Match` data model
- `src/scraper.py` — `ESPNCricketScraper` (requests + BeautifulSoup, retry
  with exponential backoff). **CSS selectors in `parse_matches` /
  `_parse_datetime` are placeholders** — they were written before
  inspecting the real ESPNCricinfo HTML and need to be verified/updated
  against the live page before this can scrape real data.
- `src/parser.py` — `MatchFilter` / `filter_international_matches`
  (dedupe, format/venue/date-range filtering, sort)
- `src/logger_setup.py`, `src/utils.py`, `config/settings.py` — done
- `main.py` — orchestrates scrape → filter → save to `output/matches.json`
- `tests/` — `test_scraper.py`, `test_espn_scrape_output.py` exist
- `src/Dockerfile` + root `.dockerignore` — containerization done (note:
  Dockerfile lives in `src/`, not the repo root — build context needs
  `-f src/Dockerfile .` from the root, since it `COPY . .`)

Not started yet:
- `src/image_generator.py` — **empty file**, Phase 3 not begun (landscape
  1200×628 + square 1080×1080 templates)
- GitHub Actions weekly cron workflow (`.github/workflows/weekly-scrape.yml`)
- Manual/automated social upload workflow
- No `.env` / secrets handling yet (not needed until social API integration)

Next logical action: verify real ESPNCricinfo HTML structure and fix the
placeholder selectors in `src/scraper.py`, since nothing downstream can be
validated against real data until that's correct.

## Standing instructions from the user
_Append new durable instructions here, most recent first, as they're given
in conversation. Each entry: what to do/avoid, and why if stated._

- (2026-09-04) Keep this CLAUDE.md file current and treat it as the record
  of project instructions — update it whenever new standing guidance is
  given, rather than only relying on chat memory.
