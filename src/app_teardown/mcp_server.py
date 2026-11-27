"""Local stdio MCP Server exposing Idea-to-Build App Teardown & Product Research tools."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

try:
    from mcp.server.mcpserver import MCPServer as _MCPServer
except ImportError:
    from mcp.server.fastmcp import FastMCP as _MCPServer  # type: ignore[no-redef]

from .asset_kit_finder import find_free_asset_kits
from .config import DEFAULT_MAX_FRAMES, DEFAULT_MAX_VIDEO_SEC, DEFAULT_RESEARCH_DIR
from .idea_planner import decompose_idea, research_domain_knowledge
from .pipeline import analyze_single_video, rebuild_teardown_reports, run_teardown
from .store_discovery import discover_app_store, discover_google_play
from .utils import safe_join
from .web_researcher import collect_competitor_web_evidence

mcp = _MCPServer("app-teardown-research")


@mcp.tool()
def plan_idea_and_tech(
    idea: str,
    product_mode: str = "auto",
    preferred_tech: str = "",
) -> dict[str, Any]:
    """Step 0: Analyze a user's app/game idea, propose 3 ranked technology stack options (e.g. Godot/Unity/Phaser or Flutter/RN/Native) to ask the user, and split the research into mechanic competitor query vs real-world domain topics."""
    brief = decompose_idea(idea=idea, product_mode=product_mode, selected_tech=preferred_tech)
    return asdict(brief)


@mcp.tool()
def discover_top_apps(
    query: str,
    stores: str = "both",
    country: str = "us",
    lang: str = "en",
    limit: int = 5,
) -> dict[str, Any]:
    """Discover the top popular competitor apps/games on Google Play and/or Apple App Store without downloading media yet."""
    selected = (
        ["google_play", "apple_app_store"]
        if stores in ("both", "all")
        else [s.strip() for s in stores.split(",") if s.strip()]
    )
    res: dict[str, Any] = {}
    if "google_play" in selected:
        res["google_play"] = discover_google_play(query, lang=lang, country=country, limit=limit)
    if "apple_app_store" in selected:
        res["apple_app_store"] = discover_app_store(query, country=country, lang=lang, limit=limit)
    return res


@mcp.tool()
def run_product_teardown(
    query: str = "",
    idea: str = "",
    selected_tech: str = "",
    theme_label: str = "",
    domain_topics: list[str] | None = None,
    targets: list[str] | None = None,
    stores: str = "both",
    product_mode: str = "auto",
    limit_per_store: int = 5,
    country: str = "us",
    lang: str = "en",
    campaign_name: str = "",
    max_video_sec: int = DEFAULT_MAX_VIDEO_SEC,
    max_frames: int = DEFAULT_MAX_FRAMES,
    download_videos: bool = True,
    run_web_research: bool = True,
) -> dict[str, Any]:
    """Run full Idea-to-Build teardown: mechanic-based top-5 competitor discovery, YouTube gameplay/walkthrough clips, hybrid keyframes, color palettes, domain subject research, free UI/model/SFX kits, reports, and dashboard.html."""
    selected = (
        ["google_play", "apple_app_store"]
        if stores in ("both", "all")
        else [s.strip() for s in stores.split(",") if s.strip()]
    )
    run = run_teardown(
        query=query,
        targets=targets or [],
        stores=selected,
        product_mode=product_mode,
        limit_per_store=limit_per_store,
        country=country,
        lang=lang,
        campaign_name=campaign_name,
        max_video_sec=max_video_sec,
        max_frames=max_frames,
        download_videos=download_videos,
        run_web_research=run_web_research,
        idea=idea,
        selected_tech=selected_tech,
        domain_topics=domain_topics,
        theme_label=theme_label,
    )
    return {
        "run_id": run.run_id,
        "output_dir": run.output_dir,
        "competitor_count": len(run.competitors),
        "domain_evidence_count": len(run.domain_evidence),
        "free_asset_kits_count": len(run.free_asset_kits),
        "cross_analysis": run.cross_analysis,
        "competitors": [
            {
                "store": c.store,
                "app_id": c.app_id,
                "folder_name": c.folder_name,
                "title": c.title,
                "product_mode": c.product_mode,
                "monetization_model": c.signals.monetization_model,
                "evidence_score": c.signals.evidence_score,
                "frame_count": sum(len(v.frames) for v in c.youtube_videos),
                "storyboards": [p for v in c.youtube_videos for p in v.storyboard_paths],
                "palette_card": c.palette_card_path,
                "web_evidence_count": len(c.web_evidence),
                "report_path": str(Path(run.output_dir) / "apps" / c.folder_name / "teardown_report.md"),
                "evidence_json": str(Path(run.output_dir) / "apps" / c.folder_name / "evidence.json"),
            }
            for c in run.competitors
        ],
        "general_report": str(Path(run.output_dir) / "GENEL_TEARDOWN_RAPORU.md"),
        "domain_report": str(Path(run.output_dir) / "DOMAIN_ARASTIRMASI.md"),
        "free_kits_report": str(Path(run.output_dir) / "FREE_ASSET_VE_KIT_REHBERI.md"),
        "design_blueprint": str(Path(run.output_dir) / "TASARIM_BLUEPRINT.md"),
        "dashboard_html": str(Path(run.output_dir) / "dashboard.html"),
    }


@mcp.tool()
def research_domain_subject(
    topics: list[str],
    country: str = "us",
    lang: str = "en",
) -> list[dict[str, Any]]:
    """Research real-world domain/subject-matter knowledge behind the product (e.g. hamburger layer order, cooking stages, habit psychology)."""
    items = research_domain_knowledge(topics, lang=lang, country=country)
    return [i.__dict__ for i in items]


@mcp.tool()
def find_free_asset_kits_tool(
    product_mode: str = "game",
    selected_tech: str = "godot",
    theme_label: str = "",
    run_live_web_search: bool = True,
) -> list[dict[str, Any]]:
    """Find verified free (CC0/MIT/SIL OFL/Royalty-Free) UI/UX kits, 3D/2D model packs, SFX/audio kits, fonts, and tech-specific SDK plugins."""
    kits = find_free_asset_kits(
        product_mode=product_mode,
        selected_tech=selected_tech,
        theme_label=theme_label,
        run_live_web_search=run_live_web_search,
    )
    return [k.__dict__ for k in kits]


@mcp.tool()
def extract_gameplay_frames(
    source: str,
    output_subfolder: str,
    title: str = "",
    max_video_sec: int = DEFAULT_MAX_VIDEO_SEC,
    max_frames: int = DEFAULT_MAX_FRAMES,
) -> dict[str, Any]:
    """Download a bounded YouTube gameplay/walkthrough clip (or inspect a local video) and extract hybrid keyframes, storyboards, and a HEX color palette card under teardowns/<output_subfolder>."""
    out_dir = safe_join(DEFAULT_RESEARCH_DIR, output_subfolder)
    rec = analyze_single_video(
        source=source,
        out_dir=out_dir,
        max_video_sec=max_video_sec,
        max_frames=max_frames,
        title=title,
    )
    return {
        "output_dir": str(out_dir),
        "title": rec.title,
        "downloaded": rec.downloaded,
        "clip_duration_sec": rec.clip_duration_sec,
        "frame_count": len(rec.frames),
        "storyboards": rec.storyboard_paths,
        "palette_card": rec.palette_card_path,
        "dominant_colors": [s.hex for s in rec.dominant_colors],
        "error": rec.error,
    }


@mcp.tool()
def collect_web_evidence(
    app_name: str,
    product_mode: str = "game",
    developer: str = "",
    country: str = "us",
    lang: str = "en",
) -> list[dict[str, Any]]:
    """Collect zero-API-key web evidence snippets and verified URLs covering revenue, monetization, ads, retention, and UX teardowns."""
    items = collect_competitor_web_evidence(
        app_title=app_name,
        product_mode=product_mode,
        developer=developer,
        lang=lang,
        country=country,
    )
    return [i.__dict__ for i in items]


@mcp.tool()
def list_teardown_campaigns() -> list[dict[str, Any]]:
    """List all saved teardown campaigns under the teardowns directory."""
    if not DEFAULT_RESEARCH_DIR.exists():
        return []
    out: list[dict[str, Any]] = []
    for d in sorted(DEFAULT_RESEARCH_DIR.iterdir(), reverse=True):
        cfg = d / "run_config.json"
        if d.is_dir() and cfg.exists():
            data = json.loads(cfg.read_text(encoding="utf-8"))
            data["path"] = str(d)
            out.append(data)
    return out


@mcp.tool()
def rebuild_campaign_teardown(campaign_folder_name: str) -> dict[str, Any]:
    """Rebuild all Markdown reports and dashboard.html for an existing teardown campaign folder."""
    target = safe_join(DEFAULT_RESEARCH_DIR, campaign_folder_name)
    run = rebuild_teardown_reports(target)
    return {
        "run_id": run.run_id,
        "output_dir": run.output_dir,
        "competitor_count": len(run.competitors),
    }


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
