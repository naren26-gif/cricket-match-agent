# 🏏 Cricket Match Weekly Agent

Automates weekly collection of upcoming **international cricket matches**
(Test, ODI, T20I, and major T20 leagues like the IPL/BBL/CPL) and will
generate shareable images for X/Twitter and Instagram. Designed to run on
a weekly schedule via GitHub Actions.

## How it works

```
Scheduled trigger (GitHub Actions cron, Tuesdays 10:00 UTC)
        ↓
Fetch matches from the CricketData.org (CricAPI) JSON API
        ↓
Filter for international-scope matches only
        ↓
Save results to output/matches.json
        ↓
Generate shareable images (landscape 1200×628 / square 1080×1080) — in progress
        ↓
Manual upload to X & Instagram (MVP; API integration later)
```

**Scope:** international matches only — Test, ODI, T20I, and major T20
leagues (IPL, BBL, CPL, PSL, BPL, LPL, SA20, ILT20, MLC, The Hundred).
County/club, other domestic leagues, youth, and women's cricket are
excluded by default.

## Project status

- ✅ Repo structure, data model, and CricAPI-based scraper/filter
- ✅ Weekly GitHub Actions automation + CI (tests on every push/PR)
- 🚧 Image generation (`src/image_generator.py`) — not started
- ⏳ Automated social upload — planned, manual for now

> Note: the original plan scraped ESPNCricinfo directly, but its
> Akamai WAF blocks plain HTTP requests and serves stale content even
> with browser-like headers. The project now uses the CricketData.org
> (CricAPI) JSON API instead — see [CLAUDE.md](CLAUDE.md) for the full
> history.

## Project structure

```
cricket-match-agent/
├── main.py                 # Orchestrates: fetch → filter → save
├── src/
│   ├── scraper.py          # CricApiScraper — fetches from CricAPI
│   ├── parser.py           # Filters matches to international scope
│   ├── models.py           # Match data model
│   ├── image_generator.py  # Image creation (not yet implemented)
│   ├── logger_setup.py     # Logging config
│   └── Dockerfile          # Container build (build context = repo root)
├── config/
│   └── settings.py         # URLs, constants, filter rules, secrets loading
├── tests/                  # pytest suite
├── output/                 # Generated matches.json / images (gitignored)
├── logs/                   # Runtime logs (gitignored)
└── .github/workflows/
    ├── weekly-scrape.yml   # Weekly cron + manual trigger
    └── ci.yml              # Tests + lint on every push/PR to main
```

## Getting started

### Prerequisites
- Python 3.10+
- A free [CricketData.org](https://cricketdata.org/) API key (100
  requests/day on the free tier)

### Setup

```bash
# 1. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate      # on Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Add your API key
echo "CRICAPI_KEY=your_key_here" > .env
```

### Run it

```bash
python main.py
```

This fetches current/upcoming matches, filters them to international
scope, and writes the result to `output/matches.json`.

### Run with Docker

The `Dockerfile` lives in `src/`, but the build context must be the repo
root (it copies the whole project in):

```bash
docker build -t cricket-match-agent -f src/Dockerfile .
docker run --env-file .env cricket-match-agent
```

### Run the tests

```bash
pytest
```

## Automation

Two GitHub Actions workflows run in this repo:

- **`weekly-scrape.yml`** — runs every Tuesday at 10:00 UTC (plus manual
  `workflow_dispatch`), fetches matches using the `CRICAPI_KEY` repo
  secret, and uploads `output/matches.json` as a build artifact.
- **`ci.yml`** — runs `pytest` (required) and `flake8` (informational
  only) on every push/PR to `main`.

## Tech stack

- **Fetching:** `requests` against the CricketData.org JSON API
- **Parsing:** `python-dateutil`
- **Images:** `Pillow`
- **Testing:** `pytest`
- **Automation:** GitHub Actions

## Documentation

Project context for contributors (and for Claude Code) is split across
path-scoped files, auto-loaded by directory:

- [CLAUDE.md](CLAUDE.md) — project index, current status, standing
  instructions
- [ARCHITECTURE.md](ARCHITECTURE.md) — pipeline, repo structure, build
  phases, live automation details
- [OWNERS.md](OWNERS.md) — who's building this
- `src/CLAUDE.md`, `config/CLAUDE.md`, `tests/CLAUDE.md` — tech stack,
  data model, secrets handling, testing conventions

## License

No license has been chosen yet for this project.
