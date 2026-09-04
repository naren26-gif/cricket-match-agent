# config/ — settings & secrets

This file is auto-loaded by Claude Code whenever it works on files under
`config/`.

## Secrets handling
- `CRICAPI_KEY` is loaded via `python-dotenv` from a local `.env`
  (gitignored, not committed) — read in `config/settings.py`.
- `.dockerignore` excludes `.env`, so it is never copied into the Docker
  image. Docker/CI must inject `CRICAPI_KEY` as a real environment
  variable instead (e.g. `docker run --env-file .env ...` locally, or the
  `secrets.CRICAPI_KEY` repo secret in `weekly-scrape.yml` for CI — see
  `ARCHITECTURE.md` → "Automation (live)").
- The VS Code workspace (`.vscode/settings.json`) sets `python.envFile` +
  `python.terminal.activateEnvironment` so the integrated terminal/debugger
  auto-load `.env` too.
