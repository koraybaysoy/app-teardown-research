# CLAUDE.md

Claude Code project instructions. Follow `AGENTS.md` as the primary reference for CLI commands, evidence rules, and security boundaries.

## Claude Code Workflow
1. Project skills are installed under `.claude/skills/` (`app-teardown` and `teardown-frameworks`). Read both before running a teardown or drafting a blueprint.
2. Always run **Step 0 (`plan-idea` / `plan_idea_and_tech`)** first when the user describes an app or game idea: propose 2-3 technology options (e.g. Godot 4, Unity 6, Phaser or Flutter, React Native, Native), ask the user to confirm their tech choice, and separate **Mechanic Competitor Benchmarking** from **Real-World Subject & Famous Brand Visual Research**.
3. Run Python commands using `.venv/Scripts/python.exe` (Windows) or `.venv/bin/python` (macOS/Linux).
4. After running `teardown`, visually inspect each competitor's `assets/gameplay_frames/*_storyboard_*.png`, critical keyframes (`*_frame_*.jpg`), `assets/color_palette_card.png`, `assets/store_screenshots_sheet.png`, AND `assets/domain_references/domain_reference_sheet.png` + `domain_palette_card.png` before filling `teardown_report.md` and `DOMAIN_ARASTIRMASI.md`.
5. Enrich `web_research.md`, `DOMAIN_ARASTIRMASI.md` (what it is, how it is made, layers/anatomy, real-world equivalent, famous brands), and `FREE_ASSET_VE_KIT_REHBERI.md` via WebSearch whenever deeper revenue data, domain rules, or theme-matched CC0/MIT UI/model/SFX kits are needed.
6. Deliver a build-ready `TASARIM_BLUEPRINT.md` and `PROTOTIP_VE_TAM_SURUM_PLANI.md` tailored specifically to the user's chosen technology stack.
7. After all research and reports finish, ask the user whether to create a quick working prototype showing how the app/game will look and work. After presenting the prototype, lay out what will be added for the full release, collect user feedback and new ideas, and only build the complete full-version app/game end-to-end once the user confirms everything is ready.
8. For strict platform/ToS compliance, use `--official-only` (official Apple iTunes API, Wikipedia, Wikimedia Commons, Openverse, curated CC0/MIT kits). Review authors are anonymized (`reviewer_XX`), third-party image downloads honor `robots.txt`, and `purge-media` removes third-party media while preserving authored Markdown reports.
