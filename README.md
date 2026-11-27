<div align="center">

# App & Game Teardown Research Toolkit

**Local mobile app and game competitor analysis for AI coding agents. Plan your tech stack, dissect top App Store and Google Play rivals frame by frame from YouTube gameplay, research real-world subjects with famous brand reference photos and layer anatomy, collect free CC0 UI/UX, 3D, and SFX kits, and ship a build-ready design blueprint.**

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

<br>

<p>
  <img src="assets/dashboard-preview.png" alt="App Teardown Research local HTML dashboard preview showing competitor matrix, real-world subject study, gameplay keyframe timeline, and free CC0 kits" width="100%">
</p>
<p><sub>Self-contained local dashboard (<code>dashboard.html</code>, zero CDNs, strict CSP, Light and Dark Zinc themes) generated automatically after each research run.</sub></p>

</div>

---

## Why This Exists

Most mobile game and mobile app teams start coding before they really know their market. Checking five rival titles properly takes days. You install each app, record onboarding or gameplay, pause YouTube videos to inspect HUD spacing, sample HEX color codes, log every interstitial ad or paywall, and dig through blogs for retention numbers.

This Python toolkit runs that whole product teardown on your own machine with zero API fees. Start with a rough idea, such as a hypercasual gate-runner cooking game or a daily habit tracker. First, it compares tech stack options (Godot, Unity, Phaser, Flutter, React Native, or Native) so you pick an engine before writing code. Then it pulls the top 5 popular competitors from Google Play and the Apple App Store, downloads bounded YouTube gameplay or UI walkthrough clips, runs FFmpeg frame extraction, renders HEX color palette cards, archives web evidence, finds free game assets and UI kits, and hands multimodal AI agents (Antigravity, Claude Code, Codex, Cursor, GitHub Copilot) everything they need to write a concrete design blueprint.

## What It Does

- **Step 0: Idea Intake, Tech Advisor, and Mechanic vs. Real-World Subject Split (`plan-idea`):**
  - Reads your raw app or game concept and ranks 3 fitting tech stacks with clear trade-offs (Godot 4, Unity 6, Phaser for games; Flutter, React Native, Native for apps). You pick the stack first.
  - Separates competitor mechanic search from real-world subject research. If you pitch a hypercasual gate-runner about stacking burgers, it benchmarks top hypercasual runner games on both stores instead of recipe apps. At the same time, it identifies the real-world subject (`hamburger`), iconic real-world brands (`McDonald's Big Mac`, `Burger King Whopper`, `Shake Shack`, `Five Guys`, `In-N-Out`), and structured research queries covering what it is, how it is made, its layers/anatomy, and its real-world equivalent.
- **Real-World Subject & Famous Brand Visual Reference Engine (`research-domain`):**
  - Pulls encyclopedic subject definitions, step-by-step preparation stages, layer/component breakdowns, and famous brand profiles via the official Wikipedia API and DuckDuckGo into `DOMAIN_ARASTIRMASI.md`.
  - Automatically searches and downloads real-world anatomy, preparation, and famous brand reference photos (zero API keys via Bing Images, Wikimedia Commons, and Openverse, with per-hop SSRF DNS validation and Pillow verification) into `assets/domain_references/`.
  - Composes a category-labeled visual moodboard contact sheet (`domain_reference_sheet.png`) and extracts a real-world subject HEX palette card (`domain_palette_card.png`) so AI agents can study silhouettes, layer order, and natural colors directly before designing original stylized assets.
- **Free UI/UX, 3D/2D Model, SFX, Font, and SDK Kit Finder (`find-kits`):**
  - Curates and web-searches free (`CC0 1.0`, `MIT`, `SIL OFL`, royalty-free) production packs matched to your theme and chosen engine.
  - Covers UI kits (Kenney UI, Figma Community, Game-Icons, Lucide), 3D/2D models (Kenney Food Kit, KayKit, Quaternius, Poly Pizza), sound effects (Kenney Audio, Freesound CC0, Mixkit), Google Fonts, and free plugins (Godot AdMob, PhantomCamera, Godot Shaders, RevenueCat) in `FREE_ASSET_VE_KIT_REHBERI.md`.
- **Top-5 App Store and Google Play Discovery (No API Keys):**
  - Ranks popular leaders across Google Play and Apple App Store by search relevance, install volume, rating count, and store rating.
  - Saves store metadata, IAP price ladders, ad flags, icons, screenshots, and 30+ user reviews to surface ad fatigue, paywall complaints, and what players praise most.
- **YouTube Gameplay and Walkthrough Harvester (`yt-dlp`):**
  - Searches YouTube for clean no-commentary mobile gameplay (Game Mode) or app UI/onboarding walkthroughs (App Mode), scores each video, and downloads a bounded clip. By default, it grabs the first 4 minutes to capture launch, FTUE, core loop, and early monetization.
- **Hybrid Frame Extraction and HEX Color Palette Engine (`FFmpeg` + `Pillow`):**
  - Pairs `ffmpeg` scene-change detection with uniform timeline sampling (24 keyframes per app by default) so menu, gameplay, ad, and paywall transitions do not get missed.
  - Builds timestamped, phase-labeled 3x4 storyboards (`gameplay_01_storyboard_*.png`), individual full-res frames, and a visual `color_palette_card.png` with HEX codes, RGB ratios, luminance, and warm/cool splits.
- **Game Mode and App Mode Teardown Rubrics:**
  - **Game Mode:** UI/UX and HUD layout, core gameplay loop, controls and game feel, color palette contrast, standout hooks, ad cadence (interstitial, rewarded, banner), IAP economy, and D1/D7/D30 retention.
  - **App Mode:** Onboarding and time-to-value, navigation and thumb-zone layout, visual design system, UX delights, paywall timing and pricing anchoring, habit loops, and churn triggers.
- **Zero-API-Key Web Evidence and Evidence Ledger (`evidence.json`):**
  - Collects revenue estimates, monetization write-ups, and UX/game teardowns into `web_research.md` and `evidence/web_sources.json`.
  - Tags every artifact with a stable Evidence ID (`EV-STORE-01`, `EV-VID-01`, `EV-FRAME-01-04`, `EV-PALETTE-01`, `EV-WEB-02`, `EV-DOM-01`, `EV-REF-01`, `EV-KIT-01`) so reports cite real local files or URLs instead of guesswork.
- **Reports, Design Blueprint, Prototype Gate, and Local Dashboard (`dashboard.html`):**
  - Writes per-app `teardown_report.md`, `web_research.md`, `store_metadata.md`, `evidence.json`, plus campaign-wide `GENEL_TEARDOWN_RAPORU.md`, `DOMAIN_ARASTIRMASI.md`, `FREE_ASSET_VE_KIT_REHBERI.md`, `TASARIM_BLUEPRINT.md`, `PROTOTIP_VE_TAM_SURUM_PLANI.md`, `apps_index.csv`, and a self-contained local `dashboard.html` (strict CSP, zero CDNs, zero `innerHTML`).
- **Prototype -> Feedback -> Full-Version Build Workflow:**
  - After all research and reports finish, the agent asks whether to build a quick working prototype demonstrating the core screens and loop.
  - Once the prototype runs, it presents a clear Prototype vs. Full Release roadmap (what works now, what will be added next, and what the finished product will look like) and asks for your feedback, tweaks, or extra ideas.
  - Only when you confirm everything is ready does the agent build the complete full-version app or game from start to finish.

## Install as Plugin or Agent Skills

### 1. Universal Agent Skills (`skills.sh` / `npx skills`)
Works with Antigravity, Claude Code, Codex, Cursor, GitHub Copilot, Windsurf, and other Agent Skills clients:

```bash
# Install both skills (app-teardown + teardown-frameworks)
npx skills add https://github.com/koraybaysoy/app-teardown-research

# Or install one skill
npx skills add https://github.com/koraybaysoy/app-teardown-research --skill app-teardown
npx skills add https://github.com/koraybaysoy/app-teardown-research --skill teardown-frameworks
```

### 2. Claude Code Plugin (Marketplace Install)
```text
/plugin install app-teardown --marketplace koraybaysoy/app-teardown-research
```

### 3. Claude Code Global MCP Server (Use From Any Repo)
Run `setup.ps1` or `setup.sh` once, then register the local MCP server globally:

```bash
claude mcp add --scope user app-teardown \
  -e PYTHONPATH="/absolute/path/to/app-teardown-research/src" \
  -- "/absolute/path/to/app-teardown-research/.venv/bin/python" -m app_teardown.mcp_server
```

### 4. Cursor and Antigravity Plugins
- **Antigravity:** Ships with root `plugin.json`, `mcp_config.json`, `.agents/skills/`, and `.agents/rules/`.
- **Cursor:** Ships with `.cursor-plugin/plugin.json`, `.cursor-plugin/marketplace.json`, `.cursor/rules/app-teardown.mdc`, and `.mcp.json`.

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
- **FFmpeg** in your system `PATH` (needed for YouTube clip trimming, scene-change detection, and keyframe extraction):
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
# 0. Plan an idea first: get ranked tech stack options + separated mechanic query and domain topics
./.venv/bin/python -m app_teardown.cli plan-idea "hypercasual cooking gate runner game building burgers" --mode game

# 1. Preview top 5 popular competitors across both stores
./.venv/bin/python -m app_teardown.cli discover "hypercasual runner stack gate" --stores both --country us --lang en --limit 5

# 2. Full Idea-to-Build teardown (top 5 per store, YouTube gameplay clips, 24 hybrid frames, HEX palettes, real-world subject + famous brand reference photos, free UI/3D/SFX kits, reports, dashboard)
./.venv/bin/python -m app_teardown.cli teardown \
  --idea "hypercasual cooking gate runner game building burgers" \
  --query "hypercasual runner stack gate game" \
  --tech godot \
  --theme "burger cooking food" \
  --subject "hamburger" \
  --famous-brands "McDonald's Big Mac" "Burger King Whopper" "Shake Shack ShackBurger" "Five Guys Cheeseburger" \
  --stores both \
  --mode game \
  --limit 5 \
  --country us \
  --lang en \
  --max-video-sec 240 \
  --max-frames 24 \
  --max-domain-images 12 \
  --name "hypercasual-burger-gate-godot"

# 3. Standalone real-world subject + famous brand photo research and free asset kit finder
./.venv/bin/python -m app_teardown.cli research-domain --idea "hypercasual burger making game" --out-dir "teardowns/burger-domain-ref" --max-images 12
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

# 8. Compliance mode (official & open-licensed APIs only: Apple iTunes API, Wikipedia, Wikimedia Commons, Openverse, curated CC0/MIT kits)
./.venv/bin/python -m app_teardown.cli teardown \
  --idea "hypercasual cooking gate runner game building burgers" \
  --tech godot \
  --official-only \
  --name "burger-official-apis"

# 9. Purge downloaded third-party media after completing reports (keeps all authored Markdown reports and JSON indices)
./.venv/bin/python -m app_teardown.cli purge-media "teardowns/<campaign_folder>" --dry-run
./.venv/bin/python -m app_teardown.cli purge-media "teardowns/<campaign_folder>"

# 10. List saved teardown campaigns
./.venv/bin/python -m app_teardown.cli list
```

*(On Windows, replace `./.venv/bin/python` with `.\.venv\Scripts\python.exe`.)*

## Using With AI Agents (Prompt Example)

```text
Read .agents/skills/app-teardown/SKILL.md and .agents/skills/teardown-frameworks/SKILL.md.
I want to build a hypercasual cooking gate-runner game where players stack burgers through gates.
First suggest 3 tech stack options (Godot, Unity, Phaser) and let me choose.
After I pick the engine, research the top 5 hypercasual runner competitors on Google Play and Apple App Store, download their YouTube gameplay, extract keyframes and HEX color palettes, research real hamburger layer rules, find free CC0 UI/UX, 3D model, and SFX kits, and write a full TASARIM_BLUEPRINT.md.
```

## Connecting as an MCP Server

`.mcp.json` and `mcp_config.json` sit at the repository root. Exposed MCP tools:
- `plan_idea_and_tech`
- `discover_top_apps`
- `run_product_teardown`
- `research_domain_subject`
- `find_free_asset_kits_tool`
- `extract_gameplay_frames`
- `collect_web_evidence`
- `list_teardown_campaigns`
- `rebuild_campaign_teardown`
- `purge_campaign_media_tool`

## Output Structure

All downloaded media stays local under `teardowns/` (git-ignored):

```text
teardowns/
└── 2026-11-27_1230_hypercasual-burger-gate-godot/
    ├── dashboard.html                 # Interactive filmstrip, palette wall, domain panel, free kits catalog
    ├── GENEL_TEARDOWN_RAPORU.md       # Cross-competitor comparison matrix and market synthesis
    ├── DOMAIN_ARASTIRMASI.md          # Real-world subject-matter rules (e.g. burger layer order, cooking stages)
    ├── FREE_ASSET_VE_KIT_REHBERI.md   # Verified free CC0/MIT UI/UX, 3D/2D model, SFX/audio, font, and SDK kits
    ├── TASARIM_BLUEPRINT.md           # Build-ready engine-specific architecture, UI/UX, color, monetization, and sprint plan
    ├── PROTOTIP_VE_TAM_SURUM_PLANI.md # Quick prototype scope, prototype-to-full delta table, and user feedback gate
    ├── apps_index.csv                 # Spreadsheet-ready competitor summary
    ├── apps_index.json                # Complete structured run payload
    ├── evidence/
    │   ├── domain_sources.json
    │   ├── domain_references.json
    │   └── free_kits.json
    ├── assets/
    │   └── domain_references/         # Downloaded real-world & famous brand photos + moodboard + palette card
    │       ├── domain_reference_sheet.png
    │       ├── domain_palette_card.png
    │       └── ref_01_*.jpg
    └── apps/
        └── gp_example-game_com-example/
            ├── teardown_report.md     # Evidence-cited UI/UX, gameplay, monetization, and retention teardown
            ├── web_research.md        # Archived web sources and agent web verification notes
            ├── store_metadata.md      # Archived store listing, IAP ladder, and user reviews
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

## Security and Privacy Notes

- **SSRF & `robots.txt` Protection:** Media and store requests enforce HTTPS and allowlisted store, CDN, and YouTube hosts. Public web citation URLs and real-world reference photo downloads reject direct IPs, localhost, private/non-global DNS resolutions, SVG/HTML payloads, and unsafe redirect hops, and respect third-party `robots.txt` rules.
- **Privacy by Default (KVKK / GDPR):** User review author names from Google Play and Apple App Store are automatically anonymized (`reviewer_01`, `reviewer_02`, ...) rather than stored as personal usernames.
- **Path Safety:** Output folders and filenames are ASCII-slugified and checked via `safe_join()` against directory traversal.
- **Subprocess Safety:** `ffmpeg` and `ffprobe` always run with `shell=False` and explicit argument arrays.
- **Safe Local Dashboard:** `dashboard.html` enforces a strict Content Security Policy and creates all DOM nodes via `document.createElement` and `textContent` (zero `innerHTML`).
- **Prompt Injection Defense:** Agent rules treat all scraped store text, reviews, YouTube titles, and web snippets strictly as untrusted data.

## Legal, Terms of Service, and Responsible Use

This toolkit is designed strictly for **local, private market research and pre-production product study**. You are responsible for complying with the Terms of Service, copyright laws, trademark laws, and privacy regulations applicable in your jurisdiction:

- **Use `--official-only` for Strict Platform Compliance:** By default, local runs may query unofficial endpoints (YouTube clips via `yt-dlp`, Google Play web scraping, Apple Storefront HTML, Bing Images, DuckDuckGo HTML). Pass `--official-only` to run only official and open-licensed APIs (Apple iTunes Search/Lookup/RSS API, Wikipedia API, Wikimedia Commons API, Openverse API, and curated `CC0`/`MIT`/`SIL OFL` kits) and feed your own local screen recordings into `extract-video`.
- **Do Not Redistribute Third-Party Media:** Downloaded videos, keyframes, competitor store screenshots, icons, and real-world/brand reference photos remain copyrighted by their respective owners. Keep `teardowns/` strictly local (git-ignored), never commit or publish downloaded third-party media, and run `app-teardown purge-media <campaign_dir>` once your own written reports are done.
- **Do Not Clone Competitors or Copy Brand Trademarks:** Study abstract design patterns, UX flows, monetization timing, and real-world layer/process logic. Always ship 100% original code, original stylized art, and original branding. Never use third-party brand logos, packaging, or trademarked product names inside your app or store listing.
- **Verify Third-Party Asset Licenses Before Shipping:** Curated `CC0 1.0`, `MIT`, `Apache 2.0`, `BSD`, and `SIL OFL` kits are commercially safe, while `CC BY` requires in-app attribution. Always inspect live web search asset hits to ensure they are not `CC BY-NC` (Non-Commercial) or `CC BY-SA` before commercial release.
- **No Commercial Scraping SaaS:** Do not wrap the default scraping modes into a hosted multi-tenant SaaS or paid data resale service.

## License

[MIT](LICENSE)
