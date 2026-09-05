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
- `test_image_generator.py` — covers Phase 3 (`src/image_generator.py`):
  featured-match selection (placeholder filtering/padding, chronological
  sort, min/max cap), the format/date/truncation render helpers, and
  `generate_images()` end-to-end (writes to `tmp_path`, not the real
  `output/` dir — asserts PNG dimensions and the
  `cricket_matches_week_XX_*.png` filename convention).

## CI
Every push/PR to `main` runs this whole suite via `.github/workflows/ci.yml`
(`pip install -r requirements.txt` then `pytest`) — see `ARCHITECTURE.md`.
