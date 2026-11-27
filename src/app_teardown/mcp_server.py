"""Local stdio MCP Server exposing Idea-to-Build App Teardown & Product Research tools."""

from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from mcp.server.mcpserver import MCPServer as _MCPServer
except ImportError:
    from mcp.server.fastmcp import FastMCP as _MCPServer  # type: ignore[no-redef]

from .asset_kit_finder import find_free_asset_kits
from .config import (
    DEFAULT_MAX_DOMAIN_IMAGES,
    DEFAULT_MAX_FRAMES,
    DEFAULT_MAX_VIDEO_SEC,
    DEFAULT_RESEARCH_DIR,
)
from .domain_researcher import harvest_domain_reference_images
from .idea_planner import build_domain_image_queries, decompose_idea, research_domain_knowledge
from .models import TeardownRun
from .pipeline import analyze_single_video, purge_campaign_media, rebuild_teardown_reports, run_teardown
from .report_generator import write_domain_and_kits_reports
from .store_discovery import discover_app_store, discover_google_play
from .utils import safe_join, slugify
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
    official_only: bool = False,
) -> dict[str, Any]:
    """Discover the top popular competitor apps/games on Google Play and/or Apple App Store without downloading media yet. Set official_only=True to query strictly Apple's official iTunes Search API."""
    selected = (
        ["apple_app_store"]
        if official_only
        else (
            ["google_play", "apple_app_store"]
            if stores in ("both", "all")
            else [s.strip() for s in stores.split(",") if s.strip()]
        )
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
    core_subject: str = "",
    famous_brands: list[str] | None = None,
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
    download_domain_images: bool = True,
    max_domain_images: int = DEFAULT_MAX_DOMAIN_IMAGES,
    official_only: bool = False,
) -> dict[str, Any]:
    """Run full Idea-to-Build teardown: mechanic-based top-5 competitor discovery, YouTube gameplay/walkthrough clips, hybrid keyframes, color palettes, real-world domain & famous brand visual reference research, free UI/model/SFX kits, reports, and dashboard.html. Set official_only=True for strict official/open-licensed API compliance mode."""
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
        core_subject=core_subject,
        famous_brands=famous_brands,
        download_domain_images=download_domain_images,
        max_domain_images=max_domain_images,
        official_only=official_only,
    )
    return {
        "run_id": run.run_id,
        "output_dir": run.output_dir,
        "official_only": run.official_only,
        "competitor_count": len(run.competitors),
        "domain_evidence_count": len(run.domain_evidence),
        "domain_reference_images_count": len(run.domain_references),
        "domain_reference_sheet": str(Path(run.output_dir) / run.domain_reference_sheet_path) if run.domain_reference_sheet_path else "",
        "domain_palette_card": str(Path(run.output_dir) / run.domain_palette_card_path) if run.domain_palette_card_path else "",
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
        "prototype_plan": str(Path(run.output_dir) / "PROTOTIP_VE_TAM_SURUM_PLANI.md"),
        "dashboard_html": str(Path(run.output_dir) / "dashboard.html"),
    }


@mcp.tool()
def research_domain_subject(
    topics: list[str] | None = None,
    idea: str = "",
    subject: str = "",
    famous_brands: list[str] | None = None,
    download_images: bool = True,
    output_subfolder: str = "",
    max_images: int = DEFAULT_MAX_DOMAIN_IMAGES,
    country: str = "us",
    lang: str = "en",
    official_only: bool = False,
) -> dict[str, Any]:
    """Research real-world subject matter (what it is, how it is made, layers/anatomy, famous real-world brands) and download visual reference photos, moodboard contact sheet, and real-world HEX palette under teardowns/<output_subfolder>. Set official_only=True for strictly Wikipedia + Wikimedia Commons + Openverse CC APIs."""
    brief = decompose_idea(
        idea=idea or subject or (" ".join(topics or [])),
        explicit_domain_topics=topics,
        explicit_subject=subject,
        explicit_famous_brands=famous_brands,
    )
    resolved_topics = list(topics) if topics else brief.domain_topics
    resolved_subject = (subject or brief.core_subject).strip()
    resolved_brands = list(famous_brands) if famous_brands else brief.famous_brands

    items = research_domain_knowledge(
        resolved_topics,
        lang=lang,
        country=country,
        core_subject=resolved_subject,
        famous_brands=resolved_brands,
        official_only=official_only,
    )

    refs = []
    sheet_rel = ""
    pal = []
    pal_card_rel = ""
    out_dir: Path | None = None

    if download_images or output_subfolder:
        folder_name = output_subfolder.strip() or f"domain_{slugify(resolved_subject or 'subject', 32)}"
        out_dir = safe_join(DEFAULT_RESEARCH_DIR, folder_name)
        out_dir.mkdir(parents=True, exist_ok=True)
        if download_images:
            img_queries = brief.image_queries or build_domain_image_queries(resolved_subject, famous_brands=resolved_brands)
            refs, sheet_rel, pal, pal_card_rel = harvest_domain_reference_images(
                image_queries=img_queries,
                run_dir=out_dir,
                subject_title=resolved_subject,
                max_images=max_images,
                lang=lang,
                country=country,
                official_only=official_only,
            )
        stub_run = TeardownRun(
            run_id=out_dir.name,
            campaign_name=resolved_subject or out_dir.name,
            query=resolved_subject,
            product_mode=brief.product_mode,
            stores=[],
            country=country,
            lang=lang,
            limit_per_store=0,
            max_video_sec=0,
            max_frames=0,
            created_at=datetime.now(tz=timezone.utc).isoformat(),
            output_dir=str(out_dir),
            idea_brief=brief,
            domain_evidence=items,
            domain_references=refs,
            domain_reference_sheet_path=sheet_rel,
            domain_palette=pal,
            domain_palette_card_path=pal_card_rel,
        )
        write_domain_and_kits_reports(stub_run, out_dir)

    return {
        "core_subject": resolved_subject,
        "famous_brands": resolved_brands,
        "output_dir": str(out_dir) if out_dir else "",
        "domain_report": str(out_dir / "DOMAIN_ARASTIRMASI.md") if out_dir else "",
        "reference_sheet": str(out_dir / sheet_rel) if (out_dir and sheet_rel) else "",
        "palette_card": str(out_dir / pal_card_rel) if (out_dir and pal_card_rel) else "",
        "evidence_count": len(items),
        "reference_images_count": len(refs),
        "domain_evidence": [i.__dict__ for i in items],
        "domain_references": [r.__dict__ for r in refs],
        "domain_palette": [asdict(s) for s in pal],
    }


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


@mcp.tool()
def purge_campaign_media_tool(
    campaign_folder_name: str,
    keep_palettes: bool = True,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Delete downloaded third-party media (videos, keyframes, store screenshots, icons, brand photos) inside teardowns/<campaign_folder_name> while keeping authored Markdown reports and JSON indices."""
    target = safe_join(DEFAULT_RESEARCH_DIR, campaign_folder_name)
    return purge_campaign_media(target, keep_palettes=keep_palettes, dry_run=dry_run)


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
