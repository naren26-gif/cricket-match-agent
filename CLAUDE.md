# Cricket Match Weekly Agent — Project Context for Claude Code

> This file lives at the root of the `cricket-match-agent` repo. Claude Code
> reads it automatically on every session in this folder, so it always has
> this context without being re-explained.
>
> **Standing rule for Claude Code:** treat this file (plus the files it
> imports and the nested `CLAUDE.md` files below) as the single source of
> truth for this project. Read it at the start of every session. Whenever
> the user gives an instruction meant to apply beyond the current message
> (a preference, a scope rule, an "always/never do X"), add it to
> "Standing instructions from the user" below instead of letting it live
> only in chat history. Keep "Current status" up to date as work lands.

@OWNERS.md

@ARCHITECTURE.md

## Where things live
This project splits guidance across path-scoped files instead of one long
document:

- **`OWNERS.md`** (imported above) — who's building this, communication
  style.
- **`ARCHITECTURE.md`** (imported above) — pipeline, repo structure, build
  order phases, live GitHub Actions workflows.
- **`src/CLAUDE.md`** — tech stack, data model, image spec, scraper
  operational notes. Auto-loaded whenever Claude Code works on files
  under `src/`.
- **`config/CLAUDE.md`** — settings/secrets handling. Auto-loaded under
  `config/`.
- **`tests/CLAUDE.md`** — testing conventions. Auto-loaded under `tests/`.

This file itself stays a short index: Objective, Current status, and
Standing instructions (below), which change often and apply project-wide.

## Objective
Automate weekly collection of international cricket matches from
ESPNCricinfo and generate shareable images (landscape for X/Twitter,
square for Instagram). Runs weekly, recommended Tuesday 10:00 AM UTC.

**Scope:** International matches only — Test, ODI, T20I, and major T20
leagues (IPL, BBL, CPL, etc.). Exclude county/club cricket, domestic
leagues (unless specified), youth cricket, and women's cricket (unless
explicitly requested).

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

Phase 1 (repo/folder structure), Phase 2 (scraper + parser + data model),
and Phase 4 (GitHub Actions automation) are done:
- `src/models.py` — `Match` data model (full shape in `src/CLAUDE.md`).
- `src/scraper.py` — `CricApiScraper` (was `ESPNCricketScraper`). Calls
  `/v1/currentMatches` + paginates `/v1/matches` (bounded by
  `MAX_PAGES_TO_FETCH`, default 8 pages), maps records to `Match` objects.
- `src/parser.py` — `MatchFilter` / `filter_international_matches`.
  Replaced the old venue-keyword check with `is_international_scope()`:
  Test/ODI matches pass once they clear `EXCLUDE_KEYWORDS` (women's,
  youth, domestic first-class/List A, warm-ups); T20 matches additionally
  need to match `ALLOWED_LEAGUES` (IPL/BBL/CPL/PSL/etc.) or contain
  "tour of" (bilateral international) — otherwise they're treated as a
  domestic T20 league and excluded.
- `config/settings.py` — see `config/CLAUDE.md` for secrets handling.
- `.vscode/settings.json` — added `python.envFile` +
  `python.terminal.activateEnvironment` so the integrated terminal/
  debugger auto-load `.env`.
- `src/logger_setup.py`, `src/utils.py` — done (`utils.py` still empty)
- `main.py` — orchestrates fetch → filter → save to `output/matches.json`
- `tests/` — see `tests/CLAUDE.md` for current test files and conventions
- `requirements.txt` — dropped `beautifulsoup4` (no HTML parsing anymore)
- `src/Dockerfile` + root `.dockerignore` — containerization done, rebuilt
  and verified with the new scraper (note: Dockerfile lives in `src/`, not
  the repo root — build context needs `-f src/Dockerfile .` from the root,
  since it `COPY . .`)
- `.github/workflows/weekly-scrape.yml` + `.github/workflows/ci.yml` —
  both committed (`78f39a6`). `CRICAPI_KEY` is already added as a repo
  secret for the weekly workflow. Full details in `ARCHITECTURE.md` →
  "Automation (live)".

Not started yet:
- `src/image_generator.py` — **empty file**, Phase 3 not begun (landscape
  1200×628 + square 1080×1080 templates, spec in `src/CLAUDE.md`)
- Manual/automated social upload workflow (Phase 5)

Next logical action: build `src/image_generator.py` (Phase 3) now that
`output/matches.json` is populated with real data end-to-end.

## Standing instructions from the user
_Append new durable instructions here, most recent first, as they're given
in conversation. Each entry: what to do/avoid, and why if stated._

- (2026-09-04) Reorganized this file into path-scoped files: `OWNERS.md`
  and `ARCHITECTURE.md` are imported above (always loaded with this file);
  `src/`, `config/`, and `tests/` each got their own `CLAUDE.md` that
  Claude Code auto-loads when working in that directory. Keep new
  directory-specific guidance in the matching nested file rather than
  growing this root file back out.
- (2026-09-04) Keep this CLAUDE.md file current and treat it as the record
  of project instructions — update it whenever new standing guidance is
  given, rather than only relying on chat memory.
