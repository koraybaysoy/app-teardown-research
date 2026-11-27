"""End-to-end orchestration pipeline for Idea-to-Build App Teardown & Product Research."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from PIL import Image

from .analyzer import analyze_competitor, compute_cross_analysis, detect_product_mode
from .asset_kit_finder import find_free_asset_kits
from .config import (
    DEFAULT_MAX_DOMAIN_IMAGES,
    DEFAULT_MAX_FRAMES,
    DEFAULT_MAX_VIDEO_SEC,
    DEFAULT_RESEARCH_DIR,
)
from .dashboard import write_dashboard
from .domain_researcher import harvest_domain_reference_images
from .frame_extractor import (
    extract_frames_and_palette,
    extract_palette_swatches,
    render_palette_card,
)
from .idea_planner import decompose_idea, research_domain_knowledge
from .models import (
    AssetKitItem,
    ColorSwatch,
    CompetitorRecord,
    DomainEvidenceItem,
    DomainReferenceImage,
    IAPItem,
    IdeaBrief,
    ImageAsset,
    KeyframeRecord,
    ProductSignals,
    ReviewSample,
    TechStackOption,
    TeardownRun,
    WebEvidenceItem,
    YouTubeVideoRecord,
)
from .report_generator import write_campaign_reports, write_competitor_artifacts
from .store_discovery import (
    discover_app_store,
    discover_google_play,
    download_store_visuals,
    fetch_app_store_competitor,
    fetch_google_play_competitor,
)
from .utils import format_bytes, parse_store_target, safe_join, slugify
from .web_researcher import collect_competitor_web_evidence
from .youtube_harvester import download_youtube_clip, search_youtube_gameplay

logger = logging.getLogger(__name__)


def _build_combined_palette(record: CompetitorRecord, app_dir: Path) -> None:
    """Build an overall app color palette card combining gameplay frames, screenshots, and icon."""
    sample_paths: list[Path] = []
    for vid in record.youtube_videos:
        for kf in vid.frames[:10]:
            p = app_dir / kf.local_path
            if p.exists():
                sample_paths.append(p)
    for shot in record.screenshots[:4]:
        if shot.downloaded and shot.local_path:
            p = app_dir / shot.local_path
            if p.exists():
                sample_paths.append(p)
    if record.icon_asset and record.icon_asset.downloaded and record.icon_asset.local_path:
        p = app_dir / record.icon_asset.local_path
        if p.exists():
            sample_paths.append(p)

    imgs: list[Image.Image] = []
    try:
        for p in sample_paths[:16]:
            try:
                with Image.open(p) as im:
                    imgs.append(im.convert("RGB").copy())
            except Exception:  # noqa: BLE001
                continue
        if imgs:
            swatches = extract_palette_swatches(imgs, top_k=8)
            record.combined_palette = swatches
            card_path = safe_join(app_dir, "assets", "color_palette_card.png")
            if render_palette_card(swatches, record.title, card_path):
                record.palette_card_path = card_path.relative_to(app_dir).as_posix()
    finally:
        for im in imgs:
            im.close()


def _hydrate_competitor_from_dict(data: dict[str, Any]) -> CompetitorRecord:
    """Reconstruct a CompetitorRecord dataclass tree from saved metadata.json."""
    icon_raw = data.get("icon_asset")
    icon_asset = ImageAsset(**icon_raw) if isinstance(icon_raw, dict) else None
    screenshots = [ImageAsset(**s) for s in (data.get("screenshots") or []) if isinstance(s, dict)]
    iap_items = [IAPItem(**i) for i in (data.get("iap_items") or []) if isinstance(i, dict)]
    reviews = [ReviewSample(**r) for r in (data.get("reviews") or []) if isinstance(r, dict)]
    web_ev = [WebEvidenceItem(**w) for w in (data.get("web_evidence") or []) if isinstance(w, dict)]
    comb_pal = [
        ColorSwatch(
            hex=c["hex"],
            rgb=tuple(c.get("rgb") or (0, 0, 0)),
            ratio_pct=float(c.get("ratio_pct") or 0.0),
            luminance=float(c.get("luminance") or 0.0),
            temperature=str(c.get("temperature") or "neutral"),
        )
        for c in (data.get("combined_palette") or [])
        if isinstance(c, dict) and c.get("hex")
    ]
    yt_videos: list[YouTubeVideoRecord] = []
    for v in data.get("youtube_videos") or []:
        if not isinstance(v, dict):
            continue
        frames = [KeyframeRecord(**f) for f in (v.get("frames") or []) if isinstance(f, dict)]
        v_colors = [
            ColorSwatch(
                hex=c["hex"],
                rgb=tuple(c.get("rgb") or (0, 0, 0)),
                ratio_pct=float(c.get("ratio_pct") or 0.0),
                luminance=float(c.get("luminance") or 0.0),
                temperature=str(c.get("temperature") or "neutral"),
            )
            for c in (v.get("dominant_colors") or [])
            if isinstance(c, dict) and c.get("hex")
        ]
        v_clean = {k: val for k, val in v.items() if k not in ("frames", "dominant_colors")}
        yt_videos.append(YouTubeVideoRecord(**v_clean, frames=frames, dominant_colors=v_colors))

    sig_raw = data.get("signals")
    signals = ProductSignals(**sig_raw) if isinstance(sig_raw, dict) else ProductSignals()

    excluded = {
        "icon_asset", "screenshots", "iap_items", "reviews", "web_evidence",
        "combined_palette", "youtube_videos", "signals",
    }
    base = {k: v for k, v in data.items() if k not in excluded}
    return CompetitorRecord(
        **base,
        icon_asset=icon_asset,
        screenshots=screenshots,
        iap_items=iap_items,
        reviews=reviews,
        web_evidence=web_ev,
        combined_palette=comb_pal,
        youtube_videos=yt_videos,
        signals=signals,
    )


def run_teardown(
    query: str = "",
    targets: list[str] | None = None,
    stores: list[str] | None = None,
    product_mode: str = "auto",
    limit_per_store: int = 5,
    country: str = "us",
    lang: str = "en",
    campaign_name: str = "",
    max_video_sec: int = DEFAULT_MAX_VIDEO_SEC,
    max_frames: int = DEFAULT_MAX_FRAMES,
    download_videos: bool = True,
    run_web_research: bool = True,
    review_count: int = 30,
    output_base_dir: Path | None = None,
    idea: str = "",
    selected_tech: str = "",
    domain_topics: list[str] | None = None,
    theme_label: str = "",
    core_subject: str = "",
    famous_brands: list[str] | None = None,
    download_domain_images: bool = True,
    max_domain_images: int = DEFAULT_MAX_DOMAIN_IMAGES,
    official_only: bool = False,
) -> TeardownRun:
    """Execute full Idea-to-Build teardown: idea decomposition, store discovery, optional YouTube frames, real-world subject & brand photo research, free kits, reports & dashboard."""
    selected_stores = stores or ["google_play", "apple_app_store"]
    if official_only:
        if "google_play" in selected_stores:
            logger.info("Official-only compliance mode: restricting store discovery to official Apple iTunes API (skipping unofficial Google Play scraping).")
        selected_stores = ["apple_app_store"]
    target_list = [t.strip() for t in (targets or []) if t and t.strip()]

    # 0. Idea decomposition (separates mechanic benchmark query from real-world domain + brand photo research)
    idea_brief: IdeaBrief | None = None
    if (
        idea.strip()
        or selected_tech.strip()
        or domain_topics
        or theme_label.strip()
        or core_subject.strip()
        or famous_brands
        or query.strip()
    ):
        idea_brief = decompose_idea(
            idea=idea or core_subject or query,
            product_mode=product_mode,
            selected_tech=selected_tech,
            explicit_mechanic_query=query,
            explicit_domain_topics=domain_topics,
            explicit_theme=theme_label,
            explicit_subject=core_subject,
            explicit_famous_brands=famous_brands,
        )
        if not query.strip() and not target_list:
            query = idea_brief.mechanic_query

    if not query.strip() and not target_list:
        raise ValueError("Provide --idea, a search --query, or at least one --targets URL/ID.")

    stamp = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d_%H%M")
    camp_slug = slugify(campaign_name or (idea_brief.theme_label if idea_brief else "") or query or "teardown-run", max_len=40)
    run_id = f"{stamp}_{camp_slug}"
    base_dir = output_base_dir or DEFAULT_RESEARCH_DIR
    base_dir.mkdir(parents=True, exist_ok=True)
    run_dir = safe_join(base_dir, run_id)
    apps_dir = safe_join(run_dir, "apps")
    apps_dir.mkdir(parents=True, exist_ok=True)

    # 1. Resolve target (store, app_id, country_override) pairs
    resolved_targets: list[tuple[str, str, str]] = []
    seen_keys: set[tuple[str, str]] = set()

    def _add_target(st: str, aid: str, ctry: str) -> None:
        key = (st, aid)
        if key not in seen_keys:
            seen_keys.add(key)
            resolved_targets.append((st, aid, ctry))

    for raw in target_list:
        kind, ident, c_override = parse_store_target(raw)
        if kind in ("google_play", "apple_app_store"):
            _add_target(kind, ident, c_override or country)
        else:
            if not query:
                query = ident

    if query.strip() and not target_list:
        if "google_play" in selected_stores:
            try:
                for cand in discover_google_play(query, lang=lang, country=country, limit=limit_per_store):
                    _add_target("google_play", cand["app_id"], country)
            except Exception as exc:  # noqa: BLE001
                logger.warning("Google Play discovery failed: %s", exc)
        if "apple_app_store" in selected_stores:
            try:
                for cand in discover_app_store(query, country=country, lang=lang, limit=limit_per_store):
                    _add_target("apple_app_store", cand["app_id"], country)
            except Exception as exc:  # noqa: BLE001
                logger.warning("Apple App Store discovery failed: %s", exc)

    # 2. Harvest each competitor
    effective_download_videos = download_videos and not official_only
    effective_comp_web = run_web_research and not official_only
    competitors: list[CompetitorRecord] = []
    for st, aid, ctry in resolved_targets:
        if official_only and st == "google_play":
            logger.info("Official-only compliance mode: skipping Google Play target %s", aid)
            continue
        try:
            if st == "google_play":
                record = fetch_google_play_competitor(aid, lang=lang, country=ctry, review_count=review_count)
            else:
                record = fetch_app_store_competitor(
                    aid,
                    country=ctry,
                    lang=lang,
                    review_count=review_count,
                    official_only=official_only,
                )
        except Exception as exc:  # noqa: BLE001
            logger.warning("Failed fetching %s:%s -> %s", st, aid, exc)
            continue

        record.product_mode = detect_product_mode(
            query=query,
            category=record.category,
            secondary_categories=record.secondary_categories,
            description=record.description,
            explicit_mode=product_mode,
        )

        app_dir = safe_join(apps_dir, record.folder_name)
        app_dir.mkdir(parents=True, exist_ok=True)
        download_store_visuals(record, app_dir)

        if effective_download_videos:
            try:
                yt_candidates = search_youtube_gameplay(
                    record.title,
                    product_mode=record.product_mode,
                    developer=record.developer,
                    max_candidates=6,
                )
                if not yt_candidates and record.store_video_urls:
                    for sv in record.store_video_urls:
                        if "youtube.com" in sv or "youtu.be" in sv:
                            yt_candidates.append(YouTubeVideoRecord(
                                title=f"{record.title} Official Trailer",
                                url=sv,
                                search_query="store_listing_video",
                                selection_score=10.0,
                            ))
                if yt_candidates:
                    best = yt_candidates[0]
                    videos_dir = safe_join(app_dir, "assets", "gameplay_video")
                    frames_dir = safe_join(app_dir, "assets", "gameplay_frames")
                    best = download_youtube_clip(
                        best,
                        videos_dir=videos_dir,
                        app_dir=app_dir,
                        stem="gameplay_01",
                        max_video_sec=max_video_sec,
                    )
                    if best.downloaded and best.local_path:
                        best = extract_frames_and_palette(
                            best,
                            video_path=app_dir / best.local_path,
                            frames_dir=frames_dir,
                            app_dir=app_dir,
                            stem="gameplay_01",
                            max_frames=max_frames,
                        )
                    record.youtube_videos.append(best)
                    safe_join(app_dir, "youtube_candidates.json").write_text(
                        json.dumps([c.__dict__ for c in yt_candidates[:5]], ensure_ascii=False, indent=2, default=str),
                        encoding="utf-8",
                    )
            except Exception as exc:  # noqa: BLE001
                logger.warning("YouTube harvesting failed for %s: %s", record.title, exc)

        _build_combined_palette(record, app_dir)

        if effective_comp_web:
            try:
                record.web_evidence = collect_competitor_web_evidence(
                    record.title,
                    product_mode=record.product_mode,
                    developer=record.developer,
                    lang=lang,
                    country=ctry,
                )
                ev_dir = safe_join(app_dir, "evidence")
                ev_dir.mkdir(parents=True, exist_ok=True)
                safe_join(ev_dir, "web_sources.json").write_text(
                    json.dumps([w.__dict__ for w in record.web_evidence], ensure_ascii=False, indent=2),
                    encoding="utf-8",
                )
            except Exception as exc:  # noqa: BLE001
                logger.warning("Web evidence collection failed for %s: %s", record.title, exc)

        analyze_competitor(record, explicit_mode=product_mode, query=query)
        write_competitor_artifacts(record, app_dir)
        competitors.append(record)

    # 3. Domain Subject-Matter Research & Free Asset Kits Discovery
    cross = compute_cross_analysis(competitors)
    resolved_mode = (
        idea_brief.product_mode
        if idea_brief
        else (cross.get("dominant_mode") or detect_product_mode(query=query, explicit_mode=product_mode))
    )
    resolved_theme = (idea_brief.theme_label if idea_brief else theme_label) or query
    resolved_tech = (idea_brief.selected_tech if idea_brief else selected_tech) or (
        "godot" if resolved_mode == "game" else "flutter"
    )

    domain_ev: list[DomainEvidenceItem] = []
    if run_web_research and idea_brief and (idea_brief.domain_topics or idea_brief.core_subject):
        try:
            domain_ev = research_domain_knowledge(
                idea_brief.domain_topics,
                lang=lang,
                country=country,
                core_subject=idea_brief.core_subject,
                famous_brands=idea_brief.famous_brands,
                official_only=official_only,
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("Domain knowledge research failed: %s", exc)

    domain_refs: list[DomainReferenceImage] = []
    domain_ref_sheet = ""
    domain_pal: list[ColorSwatch] = []
    domain_pal_card = ""
    if download_domain_images and idea_brief and idea_brief.image_queries:
        try:
            domain_refs, domain_ref_sheet, domain_pal, domain_pal_card = harvest_domain_reference_images(
                image_queries=idea_brief.image_queries,
                run_dir=run_dir,
                subject_title=idea_brief.core_subject or resolved_theme,
                max_images=max_domain_images,
                lang=lang,
                country=country,
                official_only=official_only,
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("Domain visual reference harvesting failed: %s", exc)

    free_kits: list[AssetKitItem] = find_free_asset_kits(
        product_mode=resolved_mode,
        selected_tech=resolved_tech,
        theme_label=resolved_theme,
        run_live_web_search=run_web_research and not official_only,
        lang=lang,
        country=country,
    )

    run = TeardownRun(
        run_id=run_id,
        campaign_name=campaign_name or query or run_id,
        query=query,
        product_mode=resolved_mode,
        stores=selected_stores,
        country=country.lower(),
        lang=lang.lower(),
        limit_per_store=limit_per_store,
        max_video_sec=max_video_sec,
        max_frames=max_frames,
        created_at=datetime.now(tz=timezone.utc).isoformat(),
        output_dir=str(run_dir),
        official_only=official_only,
        idea_brief=idea_brief,
        domain_evidence=domain_ev,
        domain_references=domain_refs,
        domain_reference_sheet_path=domain_ref_sheet,
        domain_palette=domain_pal,
        domain_palette_card_path=domain_pal_card,
        free_asset_kits=free_kits,
        competitors=competitors,
        cross_analysis=cross,
    )

    write_campaign_reports(run, run_dir)
    write_dashboard(run, run_dir)
    return run


def analyze_single_video(
    source: str,
    out_dir: Path,
    max_video_sec: int = DEFAULT_MAX_VIDEO_SEC,
    max_frames: int = DEFAULT_MAX_FRAMES,
    title: str = "",
) -> YouTubeVideoRecord:
    """Download (if YouTube URL) or inspect a local video and extract hybrid keyframes + palette."""
    out_dir = out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    frames_dir = safe_join(out_dir, "frames")

    src_path = Path(source)
    if src_path.exists() and src_path.is_file():
        vid = YouTubeVideoRecord(
            title=title or src_path.stem,
            url="",
            downloaded=True,
            local_path=src_path.name,
            file_size_bytes=src_path.stat().st_size,
        )
        return extract_frames_and_palette(
            vid,
            video_path=src_path,
            frames_dir=frames_dir,
            app_dir=out_dir,
            stem=slugify(title or src_path.stem, 28),
            max_frames=max_frames,
        )

    videos_dir = safe_join(out_dir, "video")
    vid = YouTubeVideoRecord(title=title, url=source, search_query="direct_url")
    vid = download_youtube_clip(vid, videos_dir=videos_dir, app_dir=out_dir, stem="clip_01", max_video_sec=max_video_sec)
    if vid.downloaded and vid.local_path:
        vid = extract_frames_and_palette(
            vid,
            video_path=out_dir / vid.local_path,
            frames_dir=frames_dir,
            app_dir=out_dir,
            stem="clip_01",
            max_frames=max_frames,
        )
    return vid


def rebuild_teardown_reports(campaign_dir: Path) -> TeardownRun:
    """Rebuild all per-app reports, domain/kit reports, campaign reports, and dashboard.html from saved files."""
    campaign_dir = campaign_dir.resolve()
    cfg_path = safe_join(campaign_dir, "run_config.json")
    cfg = json.loads(cfg_path.read_text(encoding="utf-8")) if cfg_path.exists() else {}

    apps_root = safe_join(campaign_dir, "apps")
    competitors: list[CompetitorRecord] = []
    if apps_root.exists():
        for app_dir in sorted(apps_root.iterdir()):
            if not app_dir.is_dir():
                continue
            meta_file = app_dir / "metadata.json"
            if not meta_file.exists():
                continue
            raw = json.loads(meta_file.read_text(encoding="utf-8"))
            rec = _hydrate_competitor_from_dict(raw)
            analyze_competitor(rec, explicit_mode=cfg.get("product_mode", "auto"), query=cfg.get("query", ""))
            write_competitor_artifacts(rec, app_dir)
            competitors.append(rec)

    # Hydrate saved domain evidence, visual reference photos, and free kits if present
    domain_ev: list[DomainEvidenceItem] = []
    dom_file = campaign_dir / "evidence" / "domain_sources.json"
    if dom_file.exists():
        for d in json.loads(dom_file.read_text(encoding="utf-8")):
            if isinstance(d, dict):
                domain_ev.append(DomainEvidenceItem(**d))

    domain_refs: list[DomainReferenceImage] = []
    domain_ref_sheet = str(cfg.get("domain_reference_sheet_path") or "")
    domain_pal_card = str(cfg.get("domain_palette_card_path") or "")
    domain_pal: list[ColorSwatch] = []
    refs_file = campaign_dir / "evidence" / "domain_references.json"
    if refs_file.exists():
        raw_refs = json.loads(refs_file.read_text(encoding="utf-8"))
        if isinstance(raw_refs, dict):
            ref_list = raw_refs.get("references") or []
            domain_ref_sheet = str(raw_refs.get("reference_sheet_path") or domain_ref_sheet)
            domain_pal_card = str(raw_refs.get("palette_card_path") or domain_pal_card)
            domain_pal = [
                ColorSwatch(
                    hex=c["hex"],
                    rgb=tuple(c.get("rgb") or (0, 0, 0)),
                    ratio_pct=float(c.get("ratio_pct") or 0.0),
                    luminance=float(c.get("luminance") or 0.0),
                    temperature=str(c.get("temperature") or "neutral"),
                )
                for c in (raw_refs.get("domain_palette") or [])
                if isinstance(c, dict) and c.get("hex")
            ]
        elif isinstance(raw_refs, list):
            ref_list = raw_refs
        else:
            ref_list = []
        for r in ref_list:
            if isinstance(r, dict):
                domain_refs.append(DomainReferenceImage(**r))

    free_kits: list[AssetKitItem] = []
    kits_file = campaign_dir / "evidence" / "free_kits.json"
    if kits_file.exists():
        free_kits = [AssetKitItem(**k) for k in json.loads(kits_file.read_text(encoding="utf-8"))]

    idea_brief: IdeaBrief | None = None
    if cfg.get("idea") or cfg.get("selected_tech") or cfg.get("domain_topics") or cfg.get("core_subject"):
        idea_brief = decompose_idea(
            idea=cfg.get("idea") or cfg.get("core_subject") or cfg.get("query") or "",
            product_mode=cfg.get("product_mode") or "auto",
            selected_tech=cfg.get("selected_tech") or "",
            explicit_mechanic_query=cfg.get("query") or "",
            explicit_domain_topics=cfg.get("domain_topics") or [],
            explicit_theme=cfg.get("theme_label") or "",
            explicit_subject=cfg.get("core_subject") or "",
            explicit_famous_brands=cfg.get("famous_brands") or [],
        )
        # Ensure tech_options hydrated cleanly as TechStackOption instances
        idea_brief.tech_options = [
            t if isinstance(t, TechStackOption) else TechStackOption(**t) for t in idea_brief.tech_options
        ]

    run = TeardownRun(
        run_id=cfg.get("run_id") or campaign_dir.name,
        campaign_name=cfg.get("campaign_name") or campaign_dir.name,
        query=cfg.get("query") or "",
        product_mode=cfg.get("product_mode") or "auto",
        stores=cfg.get("stores") or ["google_play", "apple_app_store"],
        country=cfg.get("country") or "us",
        lang=cfg.get("lang") or "en",
        limit_per_store=int(cfg.get("limit_per_store") or 5),
        max_video_sec=int(cfg.get("max_video_sec") or DEFAULT_MAX_VIDEO_SEC),
        max_frames=int(cfg.get("max_frames") or DEFAULT_MAX_FRAMES),
        created_at=cfg.get("created_at") or datetime.now(tz=timezone.utc).isoformat(),
        output_dir=str(campaign_dir),
        official_only=bool(cfg.get("official_only", False)),
        idea_brief=idea_brief,
        domain_evidence=domain_ev,
        domain_references=domain_refs,
        domain_reference_sheet_path=domain_ref_sheet,
        domain_palette=domain_pal,
        domain_palette_card_path=domain_pal_card,
        free_asset_kits=free_kits,
        competitors=competitors,
        cross_analysis=compute_cross_analysis(competitors),
    )
    write_campaign_reports(run, campaign_dir)
    write_dashboard(run, campaign_dir)
    return run


def purge_campaign_media(
    campaign_dir: Path,
    keep_palettes: bool = True,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Delete downloaded third-party media (videos, keyframes, screenshots, icons, brand reference photos) while preserving authored Markdown reports and JSON indices."""
    root = campaign_dir.resolve()
    if not root.exists() or not root.is_dir():
        raise ValueError(f"Campaign directory does not exist: {root}")
    root_prefix = str(root) + "\\" if "\\" in str(root) else str(root) + "/"

    palette_names = {"color_palette_card.png", "domain_palette_card.png"}
    media_exts = {".mp4", ".mkv", ".webm", ".mov", ".jpg", ".jpeg", ".png", ".webp", ".gif"}

    candidate_dirs: list[Path] = []
    dom_refs_dir = root / "assets" / "domain_references"
    if dom_refs_dir.exists() and dom_refs_dir.is_dir():
        candidate_dirs.append(dom_refs_dir)

    apps_dir = root / "apps"
    if apps_dir.exists() and apps_dir.is_dir():
        for app_dir in sorted(apps_dir.iterdir()):
            if not app_dir.is_dir():
                continue
            app_assets = app_dir / "assets"
            if app_assets.exists() and app_assets.is_dir():
                candidate_dirs.append(app_assets)

    targets: list[Path] = []
    for base in candidate_dirs:
        for fp in sorted(base.rglob("*")):
            if not fp.is_file():
                continue
            resolved_fp = fp.resolve()
            if not str(resolved_fp).startswith(root_prefix):
                continue
            if resolved_fp.suffix.lower() not in media_exts:
                continue
            if keep_palettes and resolved_fp.name in palette_names:
                continue
            targets.append(resolved_fp)

    deleted_rel: list[str] = []
    freed_bytes = 0
    for fp in targets:
        try:
            fsize = fp.stat().st_size
        except OSError:
            fsize = 0
        rel = fp.relative_to(root).as_posix()
        deleted_rel.append(rel)
        freed_bytes += fsize
        if not dry_run:
            try:
                fp.unlink(missing_ok=True)
            except OSError as exc:
                logger.warning("Could not delete %s: %s", fp, exc)

    if not dry_run:
        # Remove empty media subdirectories (bottom-up), never deleting campaign root or reports
        for base in candidate_dirs:
            for sub in sorted(base.rglob("*"), reverse=True):
                if sub.is_dir():
                    try:
                        sub.rmdir()
                    except OSError:
                        pass
            try:
                base.rmdir()
            except OSError:
                pass
        cfg_path = root / "run_config.json"
        if cfg_path.exists():
            try:
                cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
                cfg["media_purged_at"] = datetime.now(tz=timezone.utc).isoformat()
                cfg["media_purged_files_count"] = len(deleted_rel)
                cfg_path.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
            except Exception as exc:  # noqa: BLE001
                logger.debug("Could not stamp run_config.json after purge: %s", exc)

    preserved_reports = [
        p.name for p in sorted(root.glob("*.md"))
    ]
    return {
        "campaign_dir": str(root),
        "dry_run": dry_run,
        "keep_palettes": keep_palettes,
        "deleted_count": len(deleted_rel),
        "freed_bytes": freed_bytes,
        "freed_human": format_bytes(freed_bytes),
        "deleted_files": deleted_rel,
        "preserved_reports": preserved_reports,
    }
