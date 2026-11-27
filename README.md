<div align="center">

# App & Game Teardown Research Toolkit

**Idea-to-Build mobile app and game pre-production & competitor teardown studio: interactive tech stack advisor (Godot, Unity, Flutter, React Native), mechanic-based top-5 App Store & Google Play discovery, YouTube gameplay/walkthrough frame-by-frame dissection, HEX color palette cards, real-world domain research, free UI/UX + 3D/2D model + SFX kits, and build-ready product design blueprints.**

<p>
  <strong>English</strong> ·
  <a href="docs/i18n/README.tr.md">Türkçe</a> ·
  <a href="docs/i18n/README.zh-CN.md">简体中文</a> ·
  <a href="docs/i18n/README.es.md">Español</a> ·
  <a href="docs/i18n/README.pt-BR.md">Português</a> ·
  <a href="docs/i18n/README.ja.md">日本語</a> ·
  <a href="docs/i18n/README.de.md">Deutsch</a> ·
  <a href="docs/i18n/README.ko.md">한국어</a>
</p>

<p>
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white" alt="Python 3.11+">
  <img src="https://img.shields.io/badge/License-MIT-22C55E" alt="MIT License">
  <img src="https://img.shields.io/badge/MCP-Ready-8B5CF6" alt="MCP Ready">
  <img src="https://img.shields.io/badge/Agents-Claude%20%7C%20Codex%20%7C%20Antigravity%20%7C%20Cursor%20%7C%20Copilot-0EA5E9" alt="Multi-Agent Compatible">
</p>

</div>

---

## Why This Exists

Before writing the first line of code for a new mobile game or app, teams spend days installing top competitors, recording gameplay or onboarding flows, pausing YouTube walkthroughs to inspect HUD layouts, screenshotting paywalls, sampling HEX colors, and hunting for monetization and retention articles.

This toolkit automates the entire pre-design teardown locally with zero API fees. Point it at a genre or app category (for example, `"hypercasual runner"` or `"habit tracker"`), and it finds the top 5 most popular apps on **Google Play** and **Apple App Store**, downloads bounded YouTube gameplay or walkthrough clips, extracts hybrid scene-change + interval keyframes, builds timestamped storyboards and HEX color palette swatch cards, archives web evidence, and lets multimodal AI agents (Antigravity, Claude Code, Codex, Cursor, Copilot) inspect every frame to deliver evidence-cited teardown reports and a build-ready product blueprint.

## What It Does

- **Step 0 — Idea Intake, Tech Stack Advisor & Mechanic-vs-Domain Split (`plan-idea`):**
  - Takes your raw app or game idea (for example, *"hypercasual cooking game where you pass through gates to assemble burgers"*), proposes 3 ranked technology options (**Godot 4**, **Unity 6**, **Phaser/Web** or **Flutter**, **React Native**, **Native**) with trade-offs so you choose your engine/framework first.
  - Automatically separates **Competitor Mechanic Benchmarking** (researching top *hypercasual gate/stack runners* rather than recipe apps) from **Real-World Domain Research** (researching *classic hamburger layer order, cooking stages, topping combinations* into `DOMAIN_ARASTIRMASI.md`).
- **Free UI/UX, 3D/2D Model, SFX/Audio, Font & Engine SDK Kit Finder (`find-kits`):**
  - Curates and web-discovers verified free (`CC0 1.0`, `MIT`, `SIL OFL`, Royalty-Free) UI kits (Kenney UI, Figma Community, Game-Icons, Lucide), 3D/2D model packs (Kenney Food Kit, KayKit, Quaternius, Poly Pizza), SFX packs (Kenney Audio, Freesound CC0, Mixkit), Google Fonts, and tech-specific plugins (e.g. Godot AdMob, PhantomCamera, Godot Shaders, RevenueCat) into `FREE_ASSET_VE_KIT_REHBERI.md`.
- **Popular Top-5 Dual-Store Discovery (No API Keys):**
  - Searches Google Play and Apple App Store and ranks leaders by blended relevance, install volume, rating count, and store score.
  - Captures store metadata, IAP price ladders, ad-support flags, icons, store screenshots, and up to 30+ user reviews to mine ad fatigue, paywall friction, and core praise drivers.
- **YouTube Gameplay & App Walkthrough Harvester (`yt-dlp`):**
  - Automatically searches YouTube for clean no-commentary mobile gameplay (Game Mode) or app UI/onboarding walkthroughs (App Mode), scores candidates, and downloads a bounded clip (default: first 4 minutes covering launch, FTUE, core loop, and early monetization).
- **Hybrid Frame-by-Frame Dissection & Visual Color Palette Engine (`FFmpeg` + `Pillow`):**
  - Combines `ffmpeg` scene-change detection (capturing menu -> gameplay -> ad -> paywall transitions) with uniform timeline sampling (default: 24 keyframes per app).
  - Generates timestamped, phase-labeled 3x4 storyboards (`gameplay_01_storyboard_*.png`), individual full-res frames, and a rendered **`color_palette_card.png`** with exact HEX codes, RGB ratios, luminance, and warm/cool temperature breakdown.
- **Dual-Mode Product Teardown Rubrics (Game Mode + General App Mode):**
  - **Game Mode:** UI/UX & HUD layout, core gameplay loop, controls & game feel ("juice"), visual/color direction, standout hooks, ad cadence (interstitial/rewarded/banner), IAP economy, D1/D7/D30 retention & live-ops.
  - **App Mode:** Onboarding & Minimum Path to Value, information architecture & thumb-zone navigation, design system & HEX palette, UX delights, paywall timing & pricing anchoring, habit loops & churn prevention.
- **Zero-API-Key Web Evidence Archiving + Evidence Ledger (`evidence.json`):**
  - Collects web research snippets and verified URLs covering revenue estimates, monetization breakdowns, and UX/game design teardowns into `web_research.md` and `evidence/web_sources.json`.
  - Assigns unique Evidence IDs (`EV-STORE-01`, `EV-VID-01`, `EV-FRAME-01-04`, `EV-PALETTE-01`, `EV-WEB-02`, `EV-REV-05`) so every claim in your report traces back to a local artifact or URL.
- **Reports, Design Blueprint & Local Visual Studio (`dashboard.html`):**
  - Outputs per-competitor `teardown_report.md`, `web_research.md`, `store_metadata.md`, `evidence.json`, plus campaign-level `GENEL_TEARDOWN_RAPORU.md`, `TASARIM_BLUEPRINT.md`, `apps_index.csv`, and an interactive local `dashboard.html` (strict CSP, zero CDNs, zero `innerHTML`).

## Install as Plugin or Agent Skills

### 1. Universal Agent Skills (`skills.sh` / `npx skills`)
Works with **Antigravity, Claude Code, Codex, Cursor, GitHub Copilot, Windsurf**, and other Agent Skills clients:

```bash
# Install both skills (app-teardown + teardown-frameworks)
npx skills add https://github.com/koraybaysoy/app-teardown-research

# Or install individually
npx skills add https://github.com/koraybaysoy/app-teardown-research --skill app-teardown
npx skills add https://github.com/koraybaysoy/app-teardown-research --skill teardown-frameworks
```

### 2. Claude Code Plugin (One-Step Marketplace Install)
```text
/plugin install app-teardown --marketplace koraybaysoy/app-teardown-research
```

### 3. Claude Code Global MCP (Use From Any Project Folder)
After running `setup.ps1` or `setup.sh` once, register the local MCP server globally:

```bash
claude mcp add --scope user app-teardown \
  -e PYTHONPATH="/absolute/path/to/app-teardown-research/src" \
  -- "/absolute/path/to/app-teardown-research/.venv/bin/python" -m app_teardown.mcp_server
```

### 4. Cursor & Antigravity Plugins
- **Antigravity:** Includes root `plugin.json`, `mcp_config.json`, `.agents/skills/`, and `.agents/rules/`.
- **Cursor:** Includes `.cursor-plugin/plugin.json`, `.cursor-plugin/marketplace.json`, `.cursor/rules/app-teardown.mdc`, and `.mcp.json`.

## Supported AI Coding Agents

| Tool | Config / Discovery Path | Status |
| :--- | :--- | :--- |
| **Antigravity** | `plugin.json` + `AGENTS.md` + `.agents/skills/` + `.agents/rules/` | Native |
| **OpenAI Codex CLI** | `AGENTS.md` + `.agents/skills/` | Native |
| **Claude Code** | `.claude-plugin/` + `CLAUDE.md` + `.claude/skills/` + `.mcp.json` | Native |
| **Cursor** | `.cursor-plugin/` + `.cursor/rules/app-teardown.mdc` + `.mcp.json` | Native |
| **GitHub Copilot** | `AGENTS.md` + `.github/copilot-instructions.md` | Native |
| **Claude Desktop / Any MCP Client** | `python -m app_teardown.mcp_server` (stdio MCP) | Native |

## Prerequisites

- **Python 3.11+**
- **FFmpeg** in your system `PATH` (required for YouTube clip trimming, scene-change detection, and keyframe extraction):
  - Windows: `winget install Gyan.FFmpeg`
  - macOS: `brew install ffmpeg`
  - Ubuntu/Debian: `sudo apt install ffmpeg`

## Quick Setup

### Windows (PowerShell)
```powershell
git clone https://github.com/koraybaysoy/app-teardown-research.git
cd app-teardown-research
.\setup.ps1
```

### macOS / Linux
```bash
git clone https://github.com/koraybaysoy/app-teardown-research.git
cd app-teardown-research
bash ./setup.sh
```

## CLI Usage

```bash
# 0. Plan an idea first: get ranked tech stack options + separated mechanic query & domain topics
./.venv/bin/python -m app_teardown.cli plan-idea "hypercasual cooking gate runner game building burgers" --mode game

# 1. Preview top 5 popular competitors across both stores
./.venv/bin/python -m app_teardown.cli discover "hypercasual runner stack gate" --stores both --country us --lang en --limit 5

# 2. Full Idea-to-Build teardown (top 5 per store, YouTube gameplay clips, 24 hybrid frames, HEX palettes, domain research, free UI/3D/SFX kits, reports, dashboard)
./.venv/bin/python -m app_teardown.cli teardown \
  --idea "hypercasual cooking gate runner game building burgers" \
  --query "hypercasual runner stack gate game" \
  --tech godot \
  --theme "burger cooking food" \
  --stores both \
  --mode game \
  --limit 5 \
  --country us \
  --lang en \
  --max-video-sec 240 \
  --max-frames 24 \
  --name "hypercasual-burger-gate-godot"

# 3. Standalone real-world domain research & free asset kit finder
./.venv/bin/python -m app_teardown.cli research-domain "classic hamburger layers assembly order" "fast food burger ingredients"
./.venv/bin/python -m app_teardown.cli find-kits --mode game --tech godot --theme "burger cooking food"

# 4. Teardown a non-game mobile app niche (auto or --mode app)
./.venv/bin/python -m app_teardown.cli teardown \
  --idea "gamified daily habit tracker" \
  --tech flutter \
  --query "habit tracker" \
  --stores both \
  --mode app \
  --limit 5 \
  --name "habit-tracker-flutter"

# 5. Extract scene-change + interval frames and color palette from any YouTube URL or local MP4
./.venv/bin/python -m app_teardown.cli extract-video "https://www.youtube.com/watch?v=..." --out "teardowns/manual_clip" --max-video-sec 240 --max-frames 24

# 6. Collect web evidence for a single app
./.venv/bin/python -m app_teardown.cli web-research "Subway Surfers" --mode game --country us --lang en

# 7. Rebuild reports and dashboard.html without re-downloading media
./.venv/bin/python -m app_teardown.cli rebuild "teardowns/<campaign_folder>"

# 8. List saved teardown campaigns
./.venv/bin/python -m app_teardown.cli list
```

*(On Windows, replace `./.venv/bin/python` with `.\.venv\Scripts\python.exe`.)*

## Using With AI Agents (Prompt Example)

```text
Read .agents/skills/app-teardown/SKILL.md and .agents/skills/teardown-frameworks/SKILL.md.
I want to design a new hypercasual mobile game.
Run a full teardown for the top 5 competitors across Google Play and Apple App Store (US/en).
Visually inspect every extracted storyboard, critical gameplay keyframes, color_palette_card.png, and store_screenshots_sheet.png.
Enrich web_research.md using web search for revenue, ad cadence, and retention benchmarks.
Fill every competitor's teardown_report.md with exact Evidence IDs, synthesize GENEL_TEARDOWN_RAPORU.md, and produce an actionable TASARIM_BLUEPRINT.md for my upcoming game.
```

## Connecting as an MCP Server

`.mcp.json` and `mcp_config.json` are included at the repository root. Exposed MCP tools:
- `plan_idea_and_tech`
- `discover_top_apps`
- `run_product_teardown`
- `research_domain_subject`
- `find_free_asset_kits_tool`
- `extract_gameplay_frames`
- `collect_web_evidence`
- `list_teardown_campaigns`
- `rebuild_campaign_teardown`

## Output Structure

All downloaded media stays local under `teardowns/` (git-ignored):

```text
teardowns/
└── 2026-11-27_1230_hypercasual-burger-gate-godot/
    ├── dashboard.html                 # Interactive filmstrip, palette wall, domain panel, free kits catalog
    ├── GENEL_TEARDOWN_RAPORU.md       # Cross-competitor comparison matrix & market synthesis
    ├── DOMAIN_ARASTIRMASI.md          # Real-world subject-matter rules (e.g. burger layer order, cooking stages)
    ├── FREE_ASSET_VE_KIT_REHBERI.md   # Verified free CC0/MIT UI/UX, 3D/2D model, SFX/audio, font & SDK kits
    ├── TASARIM_BLUEPRINT.md           # Build-ready engine-specific architecture, UI/UX, color, monetization & sprint plan
    ├── apps_index.csv                 # Spreadsheet-ready competitor summary
    ├── apps_index.json                # Complete structured run payload
    ├── evidence/
    │   ├── domain_sources.json
    │   └── free_kits.json
    └── apps/
        └── gp_example-game_com-example/
            ├── teardown_report.md     # Evidence-cited deep UI/UX, gameplay, monetization & retention teardown
            ├── web_research.md        # Archived web sources + agent web verification notes
            ├── store_metadata.md      # Archived store listing, IAP ladder & user reviews
            ├── evidence.json          # Complete Evidence ID ledger (EV-STORE, EV-VID, EV-FRAME, EV-WEB)
            ├── metadata.json          # Normalized competitor JSON
            ├── evidence/
            │   └── web_sources.json
            └── assets/
                ├── icon/
                ├── store_screenshots/
                ├── store_screenshots_sheet.png
                ├── color_palette_card.png
                ├── gameplay_video/    # Bounded YouTube gameplay/walkthrough clip
                └── gameplay_frames/   # Individual keyframes + 3x4 timestamped storyboards
```

## Security & Privacy Notes

- **SSRF Protection:** Media/API requests enforce HTTPS and allowlisted store/CDN/YouTube hosts; public web citation URLs reject direct IPs, localhost, and private/internal hosts.
- **Path Safety:** All output folders and filenames are ASCII-slugified and checked via `safe_join()` against directory traversal.
- **Subprocess Safety:** `ffmpeg` and `ffprobe` are always called with `shell=False` and explicit argument arrays.
- **Safe Local Dashboard:** `dashboard.html` enforces a strict Content Security Policy and builds all DOM nodes via `document.createElement` and `textContent` (zero `innerHTML`).
- **Prompt Injection Defense:** Agent rules treat all scraped store copy, reviews, YouTube titles, and web snippets strictly as untrusted data.

## License

[MIT](LICENSE)
