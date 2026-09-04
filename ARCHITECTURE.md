# Architecture

## Objective (recap)
Automate weekly collection of international cricket matches and generate
shareable images (landscape for X/Twitter, square for Instagram). Runs
weekly, recommended Tuesday 10:00 AM UTC. See root `CLAUDE.md` for full
scope rules (international matches only, formats included/excluded).

## Pipeline
```
Scheduled Trigger (GitHub Actions cron)
        ↓
Web Scraper (now CricAPI JSON, was ESPNCricinfo scraping — see root
        CLAUDE.md "Current status" for why)
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
│   ├── scraper.py          # CricAPI scraper (was ESPNCricinfo scraper)
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
        ├── weekly-scrape.yml
        └── ci.yml
```

## Build order (phases)
1. Repo + venv + folder structure + git
2. Scraper + parser + data model
3. Image generator (landscape + square templates)
4. GitHub Actions automation (weekly cron)
5. Manual social upload workflow (API integration later, optional)
6. Tests (unit + integration, target >80% coverage)
7. Deploy + monitor

See root `CLAUDE.md` → "Current status" for which phases are actually done.

## Automation (live)
Two GitHub Actions workflows are committed under `.github/workflows/`
(added in `78f39a6`):

- **`weekly-scrape.yml`** — runs on the Tuesday 10:00 UTC cron
  (`0 10 * * 2`) plus manual `workflow_dispatch`. Installs deps, injects
  `CRICAPI_KEY` from the repo secret, runs `python main.py`, and uploads
  `output/matches.json` as a build artifact.
- **`ci.yml`** — runs on every push/PR to `main`. Installs deps, runs
  `pytest`, then `flake8` (lint step is `continue-on-error: true` —
  informational only for now, not a required gate).

GitHub Actions free tier (2,000 min/month) is more than sufficient for a
weekly job plus per-push CI.
