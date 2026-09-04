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

**Data source changed: ESPNCricinfo scraping abandoned, replaced with the
CricketData.org (CricAPI) JSON API.** ESPNCricinfo sits behind Akamai's
WAF/Bot Manager — plain HTTP requests get a `403 Access Denied` outright,
and even a full realistic browser header set only gets redirected to a
dead legacy domain (stale 2007-era archive content), not real fixtures.
Headless-browser (Playwright) bypass was considered but not pursued —
this sandbox lacks the sudo access needed to install Chromium's system
libraries, and it would still be uncertain against Bot Manager. Pivoted
to CricketData.org instead: a documented, free-tier (100 req/day) JSON
API, confirmed working end-to-end (including a real Docker run).

Phase 1 (repo/folder structure) and Phase 2 (scraper + parser + data
model) are done:
- `src/models.py` — `Match` data model. Added a `competition` field
  (series/tournament name, e.g. "Pakistan tour of England 2026" or
  "Indian Premier League 2026") — needed to tell international matches
  and major leagues apart from domestic cricket, since CricAPI's format
  field alone (test/odi/t20) doesn't carry that distinction.
- `src/scraper.py` — `CricApiScraper` (was `ESPNCricketScraper`). Calls
  `/v1/currentMatches` + paginates `/v1/matches` (bounded by
  `MAX_PAGES_TO_FETCH`, default 8 pages), maps records to `Match` objects.
  Note: CricAPI returns HTTP 200 even on failures (bad key, quota
  exhausted) with the real outcome in the JSON body's `status` field —
  `_get()` checks that explicitly rather than trusting the HTTP status.
- `src/parser.py` — `MatchFilter` / `filter_international_matches`.
  Replaced the old venue-keyword check with `is_international_scope()`:
  Test/ODI matches pass once they clear `EXCLUDE_KEYWORDS` (women's,
  youth, domestic first-class/List A, warm-ups); T20 matches additionally
  need to match `ALLOWED_LEAGUES` (IPL/BBL/CPL/PSL/etc.) or contain
  "tour of" (bilateral international) — otherwise they're treated as a
  domestic T20 league and excluded.
- `config/settings.py` — `CRICAPI_KEY` loaded via `python-dotenv` from a
  local `.env` (gitignored; already present, key already provisioned).
  Docker/CI must inject it as a real env var instead (e.g.
  `docker run --env-file .env ...`) since `.env` isn't copied into the
  image (`.dockerignore` excludes it).
- `.vscode/settings.json` — added `python.envFile` +
  `python.terminal.activateEnvironment` so the integrated terminal/
  debugger auto-load `.env`.
- `src/logger_setup.py`, `src/utils.py` — done (`utils.py` still empty)
- `main.py` — orchestrates fetch → filter → save to `output/matches.json`
- `tests/` — `test_scraper.py` (updated for the new `Match`/filter shape),
  `test_cricapi_scrape_output.py` (was `test_espn_scrape_output.py`,
  rewritten against sample CricAPI-shaped records instead of ESPN HTML)
- `requirements.txt` — dropped `beautifulsoup4` (no HTML parsing anymore)
- `src/Dockerfile` + root `.dockerignore` — containerization done, rebuilt
  and verified with the new scraper (note: Dockerfile lives in `src/`, not
  the repo root — build context needs `-f src/Dockerfile .` from the root,
  since it `COPY . .`)

Not started yet:
- `src/image_generator.py` — **empty file**, Phase 3 not begun (landscape
  1200×628 + square 1080×1080 templates)
- GitHub Actions weekly cron workflow (`.github/workflows/weekly-scrape.yml`)
  — will need `CRICAPI_KEY` added as a repo secret
- Manual/automated social upload workflow

Next logical action: build `src/image_generator.py` (Phase 3) now that
`output/matches.json` is populated with real data end-to-end.

## Standing instructions from the user
_Append new durable instructions here, most recent first, as they're given
in conversation. Each entry: what to do/avoid, and why if stated._

- (2026-09-04) Keep this CLAUDE.md file current and treat it as the record
  of project instructions — update it whenever new standing guidance is
  given, rather than only relying on chat memory.
