"""Command-line interface for Idea-to-Build App Teardown & Product Research Toolkit."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

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
from .pipeline import analyze_single_video, rebuild_teardown_reports, run_teardown
from .report_generator import write_domain_and_kits_reports
from .store_discovery import discover_app_store, discover_google_play
from .web_researcher import collect_competitor_web_evidence


def _parse_stores(raw: str) -> list[str]:
    if raw in ("both", "all"):
        return ["google_play", "apple_app_store"]
    return [s.strip() for s in raw.split(",") if s.strip()]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="app-teardown",
        description="Idea-to-Build mobile app & game competitor teardown: tech stack advisor, dual-store discovery, YouTube gameplay frame extraction, domain research, free UI/model/SFX kits, and design blueprints.",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable debug logging")
    sub = parser.add_subparsers(dest="command", required=True)

    # 1. plan-idea
    p_idea = sub.add_parser("plan-idea", help="Decompose an app/game idea into mechanic benchmark query, domain topics, and ranked tech stack options.")
    p_idea.add_argument("idea", help="Free-text description of the app or game idea")
    p_idea.add_argument("--mode", choices=["auto", "game", "app"], default="auto")
    p_idea.add_argument("--tech", default="", help="Optional preferred tech stack (godot, unity, phaser, flutter, react-native, native)")
    p_idea.add_argument("--json", action="store_true", help="Print structured JSON output")

    # 2. discover
    p_disc = sub.add_parser("discover", help="Preview top popular apps on Google Play and/or Apple App Store.")
    p_disc.add_argument("query", help="Mechanic, genre, or niche query (e.g. 'hypercasual runner stack gate')")
    p_disc.add_argument("--stores", default="both", help="google_play, apple_app_store, or both")
    p_disc.add_argument("--country", default="us")
    p_disc.add_argument("--lang", default="en")
    p_disc.add_argument("--limit", type=int, default=5)
    p_disc.add_argument("--json", action="store_true")

    # 3. teardown
    p_td = sub.add_parser("teardown", help="Run full Idea-to-Build competitor teardown: store discovery, YouTube frames, palettes, real-world domain & famous brand photo research, free kits, reports & dashboard.")
    p_td.add_argument("--idea", default="", help="User's app/game idea (auto-splits mechanic query vs real-world subject & brand research)")
    p_td.add_argument("--tech", default="", help="Chosen tech stack (godot, unity, phaser, flutter, react-native, native)")
    p_td.add_argument("--theme", default="", help="Theme label for domain & free asset kit search (e.g. 'burger cooking food')")
    p_td.add_argument("--subject", default="", help="Concrete real-world subject to research (e.g. 'hamburger', 'espresso coffee', 'luxury perfume')")
    p_td.add_argument("--famous-brands", nargs="*", default=[], help="Famous real-world brands/products to research and download visual references for (e.g. \"McDonald's Big Mac\" \"Burger King Whopper\")")
    p_td.add_argument("--domain-topics", nargs="*", default=[], help="Custom real-world subject-matter research queries (e.g. 'hamburger layers order')")
    p_td.add_argument("--no-domain-images", action="store_true", help="Skip downloading real-world & famous brand reference photos")
    p_td.add_argument("--max-domain-images", type=int, default=DEFAULT_MAX_DOMAIN_IMAGES, help="Max real-world & famous brand reference photos to download (default: 12)")
    p_td.add_argument("--query", default="", help="Competitor mechanic/category query for store search")
    p_td.add_argument("--targets", nargs="*", default=[], help="Specific store URLs or app IDs")
    p_td.add_argument("--stores", default="both", help="google_play, apple_app_store, or both")
    p_td.add_argument("--mode", choices=["auto", "game", "app"], default="auto")
    p_td.add_argument("--limit", type=int, default=5, help="Top popular apps per store (default: 5)")
    p_td.add_argument("--country", default="us")
    p_td.add_argument("--lang", default="en")
    p_td.add_argument("--name", default="", help="Campaign folder label")
    p_td.add_argument("--max-video-sec", type=int, default=DEFAULT_MAX_VIDEO_SEC)
    p_td.add_argument("--max-frames", type=int, default=DEFAULT_MAX_FRAMES)
    p_td.add_argument("--no-videos", action="store_true")
    p_td.add_argument("--no-web", action="store_true")
    p_td.add_argument("--reviews", type=int, default=30)
    p_td.add_argument("--out-dir", default="")

    # 4. research-domain
    p_dom = sub.add_parser("research-domain", help="Research real-world subject matter (what it is, how it's made, layers/anatomy, famous brands) and optionally download visual reference photos.")
    p_dom.add_argument("topics", nargs="*", help="One or more domain research queries (optional when --idea or --subject is given)")
    p_dom.add_argument("--idea", default="", help="Free-text product idea to auto-derive real-world subject, famous brands, and image queries")
    p_dom.add_argument("--subject", default="", help="Concrete real-world subject (e.g. 'hamburger', 'pizza', 'perfume')")
    p_dom.add_argument("--brands", nargs="*", default=[], help="Famous real-world brands/icons to research and photograph")
    p_dom.add_argument("--out-dir", default="", help="Output folder to save DOMAIN_ARASTIRMASI.md, downloaded reference photos, moodboard sheet, and palette card")
    p_dom.add_argument("--max-images", type=int, default=DEFAULT_MAX_DOMAIN_IMAGES, help="Max visual reference photos to download when --out-dir is set")
    p_dom.add_argument("--no-images", action="store_true", help="Skip downloading reference photos")
    p_dom.add_argument("--country", default="us")
    p_dom.add_argument("--lang", default="en")
    p_dom.add_argument("--out", default="", help="Optional JSON output file path")

    # 5. find-kits
    p_kits = sub.add_parser("find-kits", help="Find free UI/UX kits, 3D/2D model packs, SFX/audio kits, fonts, and tech SDK plugins.")
    p_kits.add_argument("--mode", choices=["game", "app"], default="game")
    p_kits.add_argument("--tech", default="godot", help="Chosen tech stack (godot, unity, phaser, flutter, react-native, native)")
    p_kits.add_argument("--theme", default="", help="Theme keywords (e.g. 'burger cooking food')")
    p_kits.add_argument("--no-web", action="store_true", help="Return curated verified kits only without live search")
    p_kits.add_argument("--out", default="", help="Optional JSON output file path")

    # 6. extract-video
    p_vid = sub.add_parser("extract-video", help="Extract hybrid scene+interval frames, storyboards, and color palette from a YouTube URL or local MP4.")
    p_vid.add_argument("source", help="YouTube URL or local video path")
    p_vid.add_argument("--out", required=True)
    p_vid.add_argument("--title", default="")
    p_vid.add_argument("--max-video-sec", type=int, default=DEFAULT_MAX_VIDEO_SEC)
    p_vid.add_argument("--max-frames", type=int, default=DEFAULT_MAX_FRAMES)

    # 7. web-research
    p_web = sub.add_parser("web-research", help="Collect zero-API-key web evidence for an app's monetization, revenue, retention, and UX.")
    p_web.add_argument("app_name")
    p_web.add_argument("--mode", choices=["game", "app"], default="game")
    p_web.add_argument("--developer", default="")
    p_web.add_argument("--country", default="us")
    p_web.add_argument("--lang", default="en")
    p_web.add_argument("--out", default="")

    # 8. rebuild
    p_reb = sub.add_parser("rebuild", help="Rebuild Markdown reports and dashboard.html for an existing teardown campaign.")
    p_reb.add_argument("campaign_dir")

    # 9. list
    sub.add_parser("list", help="List saved teardown campaigns under ./teardowns.")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    if args.command == "plan-idea":
        brief = decompose_idea(idea=args.idea, product_mode=args.mode, selected_tech=args.tech)
        if args.json:
            print(json.dumps(asdict(brief), ensure_ascii=False, indent=2))
        else:
            print(f"\nIdea: {brief.raw_idea}")
            print(f"Detected Mode: {brief.product_mode}")
            print(f"Competitor Benchmark Query (Mechanic Axis): {brief.mechanic_query}")
            print(f"Theme / Asset Axis: {brief.theme_label}")
            print(f"Core Real-World Subject: {brief.core_subject}")
            if brief.famous_brands:
                print(f"Famous Real-World Brands to Study: {', '.join(brief.famous_brands)}")
            print("Domain Subject-Matter Topics:")
            for t in brief.domain_topics:
                print(f"  - {t}")
            if brief.image_queries:
                print("Planned Visual Reference Photo Searches:")
                for iq in brief.image_queries:
                    print(f"  - [{iq.get('category', 'ref')}] {iq.get('label', '')}: {iq.get('query', '')}")
            print("\nRecommended Technology Options:")
            for idx, opt in enumerate(brief.tech_options, start=1):
                rec = " [RECOMMENDED]" if opt.recommended else ""
                print(f"  {idx}. {opt.name} ({opt.id}){rec} | Complexity: {opt.complexity} | {opt.license_cost}")
                print(f"     Best for: {opt.best_for}")
        return 0

    if args.command == "discover":
        stores = _parse_stores(args.stores)
        out: dict[str, list] = {}
        if "google_play" in stores:
            out["google_play"] = discover_google_play(args.query, lang=args.lang, country=args.country, limit=args.limit)
        if "apple_app_store" in stores:
            out["apple_app_store"] = discover_app_store(args.query, country=args.country, lang=args.lang, limit=args.limit)
        if args.json:
            print(json.dumps(out, ensure_ascii=False, indent=2))
        else:
            for st, items in out.items():
                print(f"\n=== {st.upper()} ({len(items)}) ===")
                for idx, it in enumerate(items, start=1):
                    metric = it.get("installs") or f"{it.get('ratings_count', 0):,} ratings"
                    print(f"{idx}. {it['title']} [{it['app_id']}] | {it['rating']}★ | {metric} | Pop: {it['popularity_score']}")
        return 0

    if args.command == "teardown":
        run = run_teardown(
            query=args.query,
            targets=args.targets,
            stores=_parse_stores(args.stores),
            product_mode=args.mode,
            limit_per_store=args.limit,
            country=args.country,
            lang=args.lang,
            campaign_name=args.name,
            max_video_sec=args.max_video_sec,
            max_frames=args.max_frames,
            download_videos=not args.no_videos,
            run_web_research=not args.no_web,
            review_count=args.reviews,
            output_base_dir=Path(args.out_dir) if args.out_dir else None,
            idea=args.idea,
            selected_tech=args.tech,
            domain_topics=args.domain_topics,
            theme_label=args.theme,
            core_subject=args.subject,
            famous_brands=args.famous_brands,
            download_domain_images=not args.no_domain_images,
            max_domain_images=args.max_domain_images,
        )
        print(json.dumps({
            "run_id": run.run_id,
            "output_dir": run.output_dir,
            "competitor_count": len(run.competitors),
            "domain_evidence_count": len(run.domain_evidence),
            "domain_reference_images_count": len(run.domain_references),
            "domain_reference_sheet": str(Path(run.output_dir) / run.domain_reference_sheet_path) if run.domain_reference_sheet_path else "",
            "domain_palette_card": str(Path(run.output_dir) / run.domain_palette_card_path) if run.domain_palette_card_path else "",
            "free_asset_kits_count": len(run.free_asset_kits),
            "general_report": str(Path(run.output_dir) / "GENEL_TEARDOWN_RAPORU.md"),
            "domain_report": str(Path(run.output_dir) / "DOMAIN_ARASTIRMASI.md"),
            "free_kits_report": str(Path(run.output_dir) / "FREE_ASSET_VE_KIT_REHBERI.md"),
            "design_blueprint": str(Path(run.output_dir) / "TASARIM_BLUEPRINT.md"),
            "prototype_plan": str(Path(run.output_dir) / "PROTOTIP_VE_TAM_SURUM_PLANI.md"),
            "dashboard_html": str(Path(run.output_dir) / "dashboard.html"),
            "cross_analysis": run.cross_analysis,
        }, ensure_ascii=False, indent=2))
        return 0

    if args.command == "research-domain":
        brief = None
        if args.idea or args.subject or args.brands:
            brief = decompose_idea(
                idea=args.idea or args.subject,
                explicit_domain_topics=args.topics or None,
                explicit_subject=args.subject,
                explicit_famous_brands=args.brands or None,
            )
        topics = list(args.topics) if args.topics else (brief.domain_topics if brief else [])
        core_subject = (args.subject or (brief.core_subject if brief else "")).strip()
        famous_brands = list(args.brands) if args.brands else (brief.famous_brands if brief else [])
        if not topics and not core_subject:
            parser.error("Provide positional topics, --idea, or --subject for research-domain.")

        items = research_domain_knowledge(
            topics,
            lang=args.lang,
            country=args.country,
            core_subject=core_subject,
            famous_brands=famous_brands,
        )

        refs = []
        sheet_rel = ""
        pal = []
        pal_card_rel = ""
        if args.out_dir:
            out_dir_path = Path(args.out_dir).resolve()
            out_dir_path.mkdir(parents=True, exist_ok=True)
            if not args.no_images:
                img_queries = (
                    brief.image_queries
                    if brief and brief.image_queries
                    else build_domain_image_queries(core_subject or (topics[0] if topics else ""), famous_brands=famous_brands)
                )
                refs, sheet_rel, pal, pal_card_rel = harvest_domain_reference_images(
                    image_queries=img_queries,
                    run_dir=out_dir_path,
                    subject_title=core_subject or (topics[0] if topics else "Domain"),
                    max_images=args.max_images,
                    lang=args.lang,
                    country=args.country,
                )
            stub_run = TeardownRun(
                run_id=out_dir_path.name,
                campaign_name=core_subject or out_dir_path.name,
                query=core_subject or (topics[0] if topics else ""),
                product_mode=brief.product_mode if brief else "game",
                stores=[],
                country=args.country,
                lang=args.lang,
                limit_per_store=0,
                max_video_sec=0,
                max_frames=0,
                created_at=datetime.now(tz=timezone.utc).isoformat(),
                output_dir=str(out_dir_path),
                idea_brief=brief,
                domain_evidence=items,
                domain_references=refs,
                domain_reference_sheet_path=sheet_rel,
                domain_palette=pal,
                domain_palette_card_path=pal_card_rel,
            )
            write_domain_and_kits_reports(stub_run, out_dir_path)

        payload = {
            "core_subject": core_subject,
            "famous_brands": famous_brands,
            "evidence_count": len(items),
            "reference_images_count": len(refs),
            "reference_sheet": str(Path(args.out_dir).resolve() / sheet_rel) if (args.out_dir and sheet_rel) else "",
            "palette_card": str(Path(args.out_dir).resolve() / pal_card_rel) if (args.out_dir and pal_card_rel) else "",
            "domain_report": str(Path(args.out_dir).resolve() / "DOMAIN_ARASTIRMASI.md") if args.out_dir else "",
            "domain_evidence": [i.__dict__ for i in items],
            "domain_references": [r.__dict__ for r in refs],
            "domain_palette": [asdict(s) for s in pal],
        }
        if args.out:
            p = Path(args.out)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    if args.command == "find-kits":
        kits = find_free_asset_kits(
            product_mode=args.mode,
            selected_tech=args.tech,
            theme_label=args.theme,
            run_live_web_search=not args.no_web,
        )
        payload = [k.__dict__ for k in kits]
        if args.out:
            p = Path(args.out)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    if args.command == "extract-video":
        rec = analyze_single_video(
            source=args.source,
            out_dir=Path(args.out),
            max_video_sec=args.max_video_sec,
            max_frames=args.max_frames,
            title=args.title,
        )
        print(json.dumps({
            "title": rec.title,
            "downloaded": rec.downloaded,
            "local_path": rec.local_path,
            "clip_duration_sec": rec.clip_duration_sec,
            "frame_count": len(rec.frames),
            "storyboards": rec.storyboard_paths,
            "palette_card": rec.palette_card_path,
            "dominant_colors": [s.hex for s in rec.dominant_colors],
            "error": rec.error,
        }, ensure_ascii=False, indent=2))
        return 0

    if args.command == "web-research":
        items = collect_competitor_web_evidence(
            app_title=args.app_name,
            product_mode=args.mode,
            developer=args.developer,
            lang=args.lang,
            country=args.country,
        )
        payload = [i.__dict__ for i in items]
        if args.out:
            out_p = Path(args.out)
            out_p.parent.mkdir(parents=True, exist_ok=True)
            out_p.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    if args.command == "rebuild":
        run = rebuild_teardown_reports(Path(args.campaign_dir))
        print(json.dumps({
            "run_id": run.run_id,
            "output_dir": run.output_dir,
            "competitor_count": len(run.competitors),
        }, ensure_ascii=False, indent=2))
        return 0

    if args.command == "list":
        if not DEFAULT_RESEARCH_DIR.exists():
            print("[]")
            return 0
        items = []
        for d in sorted(DEFAULT_RESEARCH_DIR.iterdir(), reverse=True):
            cfg = d / "run_config.json"
            if d.is_dir() and cfg.exists():
                entry = json.loads(cfg.read_text(encoding="utf-8"))
                entry["path"] = str(d)
                items.append(entry)
        print(json.dumps(items, ensure_ascii=False, indent=2))
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
