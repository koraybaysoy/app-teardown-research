# Contributing to App & Game Teardown Research Toolkit

Contributions, bug reports, new teardown rubrics, and language translations are welcome!

## Development Setup
1. Fork and clone the repository.
2. Run `./setup.ps1` (Windows) or `bash ./setup.sh` (macOS/Linux).
3. Run tests before opening a pull request:
   ```bash
   pytest -v
   ```

## Security & Quality Guardrails
All pull requests must preserve these core invariants:
- **Path Safety:** Use `safe_join()` for all filesystem outputs under `teardowns/`.
- **SSRF Defense:** Validate every external download URL with `validate_asset_url()` and web citation URLs with `validate_public_web_url()`.
- **Subprocess Safety:** Always invoke `ffmpeg` and `ffprobe` via argument lists with `shell=False`.
- **Safe Dashboard:** Keep strict CSP and build DOM elements strictly with `document.createElement` and `textContent` (no `innerHTML`).
- **Skill Parity:** Keep `skills/`, `.agents/skills/`, and `.claude/skills/` synchronized whenever editing any `SKILL.md` or rubric file.
