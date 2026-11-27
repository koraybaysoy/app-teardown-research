# CLAUDE.md

Claude Code project instructions. Follow `AGENTS.md` as the primary reference for CLI commands, evidence rules, and security boundaries.

## Claude Code Workflow
1. Project skills are installed under `.claude/skills/` (`app-teardown` and `teardown-frameworks`). Read both before running a teardown or drafting a blueprint.
2. Always run **Step 0 (`plan-idea` / `plan_idea_and_tech`)** first when the user describes an app or game idea: propose 2-3 technology options (e.g. Godot 4, Unity 6, Phaser or Flutter, React Native, Native), ask the user to confirm their tech choice, and separate **Mechanic Competitor Benchmarking** from **Real-World Domain Research**.
3. Run Python commands using `.venv/Scripts/python.exe` (Windows) or `.venv/bin/python` (macOS/Linux).
4. After running `teardown`, visually inspect each competitor's `assets/gameplay_frames/*_storyboard_*.png`, critical keyframes (`*_frame_*.jpg`), `assets/color_palette_card.png`, and `assets/store_screenshots_sheet.png` before filling `teardown_report.md`.
5. Enrich `web_research.md`, `DOMAIN_ARASTIRMASI.md`, and `FREE_ASSET_VE_KIT_REHBERI.md` via WebSearch whenever deeper revenue data, domain rules (e.g. burger layer assembly), or theme-matched CC0/MIT UI/model/SFX kits are needed.
6. Deliver a build-ready `TASARIM_BLUEPRINT.md` tailored specifically to the user's chosen technology stack.
