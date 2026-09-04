# tests/ — testing conventions

This file is auto-loaded by Claude Code whenever it works on files under
`tests/`.

## Framework & target
- `pytest` (see root `pytest.ini`), with `pytest-mock` for mocking.
- Target >80% coverage (Build order phase 6 in `ARCHITECTURE.md`).
- `flake8`/`black`/`pylint` for style — currently wired into `ci.yml` as
  lint-only (`continue-on-error`, informational, not a required gate; see
  `ARCHITECTURE.md` → "Automation (live)").

## Current test files
- `test_scraper.py` — covers `CricApiScraper`, updated for the
  `Match`/filter shape (was ESPNCricinfo-oriented before the data-source
  switch documented in root `CLAUDE.md`).
- `test_cricapi_scrape_output.py` — (renamed from
  `test_espn_scrape_output.py`) rewritten against sample CricAPI-shaped
  JSON records instead of ESPN HTML fixtures.

## CI
Every push/PR to `main` runs this whole suite via `.github/workflows/ci.yml`
(`pip install -r requirements.txt` then `pytest`) — see `ARCHITECTURE.md`.
